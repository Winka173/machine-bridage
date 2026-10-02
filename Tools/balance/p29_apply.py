"""Prompt 29 S01: applies the round-2 balance manifest (Docs/balance/manifest_v2.json) to balance.json.

    python Tools/balance/p29_apply.py --dry                       # checks every bundle, writes nothing but the log
    python Tools/balance/p29_apply.py --bundles "B0-*"            # applies the matching bundles that pass
    python Tools/balance/p29_apply.py --bundles "B1-*,E1" --dry

Rules (the sheet "Quy tắc"): only FIX and APPLY rows change data (R1); a row whose text says "Xem lại" waits for the owner;
before applying, each row is ALREADY_APPLIED (current == new), OK (current == expected_before within tolerance) or
CONFLICT (R2); one CONFLICT drops its whole bundle; a bundle applies whole and only after its depends_on (R3); numbers come
only from entity_id / field_path / expected_before / new_value (R4); field paths map through the C01 table
(Docs/balance_field_map.md, the MAPPERS below), an unmapped path is CONFLICT (R5); one ROUND_HALF_UP (R6); weapons are
never edited by a unit-scope row (R8: checked after every bundle). Each run appends its outcome per bundle to
Docs/balance/apply_log_p29.md: OK / ALREADY_APPLIED / CONFLICT / BLOCKED / SKIPPED(status).

Code bundles (S01-S09, B3-AI, the code part of B2/G1) count as done when listed in DONE_CODE (each pass adds its own),
checks (C06, C11, C12) when listed in DONE_CHECKS: a bundle depending on anything else is BLOCKED.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import sys
from decimal import ROUND_HALF_UP, Decimal

sys.path.insert(0, os.path.dirname(__file__))
from jsonc_edit import Doc, Entry, fmt, loads  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MANIFEST = os.path.join(ROOT, "Docs", "balance", "manifest_v2.json")
BALANCE = os.path.join(ROOT, "Assets", "MachineBrigade", "Resources", "Data", "balance.json")
LOG = os.path.join(ROOT, "Docs", "balance", "apply_log_p29.md")
# Bundles applied by earlier runs (written by real runs): depends_on reads it, and an applied bundle is not checked
# again (a later bundle may have moved its values on, B1 after B0).
STATE = os.path.join(ROOT, "Docs", "balance", "apply_state_p29.json")

# Code bundles whose code is in the repository (each pass adds the ones it wrote).
DONE_CODE: set[str] = {"S01", "S02", "S03", "S04", "S05", "S06", "S07", "S08", "S09", "B2-APS-trophy", "B3-AI"}
# Field paths that are code, not data (C01): their bundle counts as applied when it is in DONE_CODE.
CODE_PATHS = ("aircraft.", "equipment.", "boss.")
# Checks done with a result that lets their bundles go (Docs/checks/*.md).
DONE_CHECKS: set[str] = {"C06", "C12"}

# Mode names of E1 -> SimWorld.ModeTag values, and the bank each mode's code gives the side the manifest means.
MODE_TAGS = {
    "Chiếm cứ điểm / Tử chiến / Vua đồi": ["Conquest", "Deathmatch", "KingOfTheHill"],
    "Công phá": ["Assault"],
    "Công thành": ["Siege"],
    "Phòng thủ / Vô tận": ["Defend", "Endless"],
    "Sinh tồn": ["Survival"],
    "Săn trùm": ["BossRush"],
}
CODE_BANK = {"Siege": 40, "BossRush": 45}  # ModeSessions: the siege attacker and the boss rush player; else TeamEconomy's 30
DEFAULT_BANK = 30
VAULT_BONUS = 15  # Commanders.cs: okoye's BankBonus
DELIVERY = 3.5  # EconomySystem.DeliverySeconds
FLARE_KINDS = ("Flares",)
SELF_APS_RADIUS = 20  # the sheet "APS": a new SELF_APS (titan_tank) at 20 m like next_gen_tank; the manifest has no radius row


def round_half_up(x, step=1):
    """R6: the one rounding (12.5 -> 13, 19.5 -> 20; step 10 for health: 2485 -> 2490). Never Python's round()."""
    q = Decimal(str(step))
    return int((Decimal(str(x)) / q).quantize(Decimal(1), rounding=ROUND_HALF_UP) * q)


class Unmapped(Exception):
    pass


# ----------------------------------------------------------------------------------------------------------------
# The C01 mappers: read(state) -> current value in the manifest's units; write(state, value).


class State:
    def __init__(self, doc: Doc):
        self.doc = doc
        self.data = doc.data()
        self.vehicles = {v["id"]: v for v in self.data["vehicles"]}
        self.skills = {s["id"]: s for s in self.data.get("skills", [])}

    def refresh(self):
        self.data = self.doc.data()
        self.vehicles = {v["id"]: v for v in self.data["vehicles"]}

    def vehicle(self, uid):
        if uid not in self.vehicles:
            raise Unmapped(f"no vehicle '{uid}'")
        return self.vehicles[uid]

    def toughness(self, uid):
        v = self.vehicle(uid)
        return self.data["toughness"]["bosses" if v.get("boss") else "vehicles"]

    def edit(self, uid, fn):
        self.doc.edit("vehicles", uid, fn)
        self.refresh()

    def flare_skill(self, uid):
        for s in self.vehicle(uid).get("skills", []) or []:
            if s in self.skills and self.skills[s].get("kind") in FLARE_KINDS:
                return s
        return None


def m_hp(st, uid, value=None, write=False):
    t = st.toughness(uid)
    if write:
        st.edit(uid, lambda e: e.set("hp", round_half_up(value / t)))
        return None
    return st.vehicle(uid)["hp"] * t


def hp_equal(st, uid, a, b, tol):
    """Health compares in data units: one ROUND_HALF_UP of each over the toughness."""
    t = st.toughness(uid)
    return a is not None and b is not None and round_half_up(a / t) == round_half_up(b / t)


def simple(key, default=None):
    def m(st, uid, value=None, write=False):
        if write:
            st.edit(uid, lambda e: e.set(key, value))
            return None
        return st.vehicle(uid).get(key, default)
    return m


def m_flare_recharge(st, uid, value=None, write=False):
    v = st.vehicle(uid)
    if write:
        def fn(e: Entry):
            if value is None:
                # No flares (D6: the stealth bomber has none on the real aircraft): the flare skill goes from this vehicle.
                skill = st.flare_skill(uid)
                if skill:
                    e.set("skills", [s for s in v["skills"] if s != skill])
                e.remove("flareRecharge")
            else:
                e.set("flareRecharge", value)
        st.edit(uid, fn)
        return None
    if "flareRecharge" in v:
        return v["flareRecharge"]
    skill = st.flare_skill(uid)
    return st.skills[skill]["cooldown"] if skill else None


def aps(key, default):
    def m(st, uid, value=None, write=False):
        v = st.vehicle(uid)
        if write:
            if "aps" not in v:
                st.edit(uid, lambda e: e.set("aps", {"radius": SELF_APS_RADIUS, key: value}))
            else:
                st.edit(uid, lambda e: e.set_sub("aps", key, value))
            return None
        return v.get("aps", {}).get(key, default)
    return m


APS_NAMES = {"NONE": "None", "BUILT_IN": "BuiltIn", "RETROFIT_ELIGIBLE": "RetrofitEligible"}


def m_aps_capability(st, uid, value=None, write=False):
    """The manifest's NONE / BUILT_IN / RETROFIT_ELIGIBLE are the C# enum names None / BuiltIn / RetrofitEligible in the data;
    absent reads as "—" (the manifest's word for "never set"; the code reads it as None)."""
    if write:
        st.edit(uid, lambda e: e.set("apsCapability", APS_NAMES.get(value, value)))
        return None
    back = {v: k for k, v in APS_NAMES.items()}
    have = st.vehicle(uid).get("apsCapability")
    return back.get(have, have) if have is not None else "—"


UNIT_FIELDS = {
    "hp": m_hp,
    "cost": simple("cp"),
    "speed": simple("speed"),
    "outgoingDamageMult": simple("outgoingDamageMult", 1),
    "dropDelaySec": simple("dropDelay", DELIVERY),
    "flare.maxCharges": simple("flareCharges", 0),
    "flare.rechargeSec": m_flare_recharge,
    "apsCapability": m_aps_capability,
    "interception.rechargeSec": aps("recharge", None),
    "interception.maxCharges": aps("charges", 0),
    "interception.shellChance": aps("shells", 0),
    "interception.blocks.artilleryRocket": aps("rockets", False),
}


def bank_map(st):
    return st.data.get("economy", {}).get("bankByMode", {})


def m_bank(st, entity, value=None, write=False):
    if entity == "Chỉ huy Vault":
        # Derived: the ordinary bank plus the commander's bonus; checked, never written.
        if write:
            return None
        return m_bank(st, "Chiếm cứ điểm / Tử chiến / Vua đồi") + VAULT_BONUS
    tags = MODE_TAGS.get(entity)
    if tags is None:
        raise Unmapped(f"no mode tag for '{entity}'")
    banks = bank_map(st)
    if write:
        sec = st.doc._section("economy")
        e = Entry(st.doc.text[sec[0]:sec[1] + 1])
        mapping = dict(banks)
        for tag in tags:
            before = CODE_BANK.get(tag, DEFAULT_BANK)
            mapping[tag] = [before, value]
        e.set_raw("bankByMode", "{ " + ", ".join(f'"{k}": {fmt(v)}' for k, v in mapping.items()) + " }", after="supply")
        st.doc.text = st.doc.text[:sec[0]] + e.text + st.doc.text[sec[1] + 1:]
        st.refresh()
        return None
    values = {banks[t][1] if t in banks else CODE_BANK.get(t, DEFAULT_BANK) for t in tags}
    if len(values) != 1:
        raise Unmapped(f"modes of '{entity}' disagree: {values}")
    return values.pop()


def mapper(row):
    path = str(row.get("field_path") or "")
    if path.startswith("units."):
        _, uid, rest = path.split(".", 2)
        if rest in UNIT_FIELDS:
            return uid, UNIT_FIELDS[rest]
    if path == "modes.<mode>.cpStockCap":
        return row["entity_id"], m_bank
    raise Unmapped(f"no mapping for {path}")


# ----------------------------------------------------------------------------------------------------------------


def equal(st, row, a, b):
    if str(row.get("field_path", "")).endswith(".apsCapability"):
        # The manifest writes "never set" both as "—" and as NONE.
        a, b = ("NONE" if x in ("—", None) else x for x in (a, b))
    if a is None or b is None or isinstance(a, (str, bool)) or isinstance(b, (str, bool)):
        return a == b
    tol = float(row.get("tolerance") or 0)
    if str(row.get("field_path", "")).endswith(".hp"):
        return hp_equal(st, row["field_path"].split(".")[1], a, b, tol)
    return abs(float(a) - float(b)) <= tol + 1e-9


def expected(row):
    v = row.get("expected_before")
    return None if v in ("—",) and row.get("value_type") != "enum" else v


def deps(bundle_row):
    d = bundle_row.get("depends_on") or ""
    return [x.strip() for x in str(d).split(",") if x.strip()]


def review(row):
    """A row marked "Xem lại" in a status column waits for the owner. The prose columns (reason, derivation) are not
    read (R4): the B0 rows quote round 1's "Xem lại" to explain the fix."""
    return any("Xem lại" in str(row.get(k) or "") for k in ("status", "validation", "owner_decision_id", "new_value"))


def run(patterns, dry):
    with open(MANIFEST, encoding="utf-8") as f:
        man = json.load(f)
    rows_by = {}
    for r in man["rows"]:
        rows_by.setdefault(r["bundle_id"], []).append(r)
    bundles = man["bundles"]
    doc = Doc(BALANCE)
    st = State(doc)
    weapons_before = json.dumps(st.data["weapons"], sort_keys=True)
    outcome: dict[str, str] = {}
    applied = set(json.load(open(STATE, encoding="utf-8"))) if os.path.exists(STATE) else set()
    lines = [f"\n## Run {'dry' if dry else 'apply'}: {', '.join(patterns)} (manifest {man['sha256'][:12]})\n",
             "| bundle | outcome | detail |", "|---|---|---|"]

    def done(b):
        return b in DONE_CODE or b in DONE_CHECKS or b in applied or outcome.get(b) in ("OK", "ALREADY_APPLIED", "APPLIED")

    for b in bundles:
        bid = b["bundle_id"]
        rows = rows_by.get(bid, [])
        status = (b.get("Trạng thái") or "").strip()
        if not any(fnmatch.fnmatch(bid, p.strip()) for p in patterns):
            # Earlier passes' bundles: their state is what the data says now (for depends_on).
            if bid in DONE_CODE:
                outcome[bid] = "APPLIED"
            continue
        if bid in applied:
            outcome[bid] = "APPLIED"
            lines.append(f"| {bid} | APPLIED | in an earlier run |")
            continue
        if status not in ("FIX", "APPLY"):
            outcome[bid] = f"SKIPPED({status or 'empty'})"
            lines.append(f"| {bid} | {outcome[bid]} | |")
            continue
        if any(review(r) for r in rows):
            outcome[bid] = "SKIPPED(Xem lại)"
            lines.append(f"| {bid} | {outcome[bid]} | a row waits for the owner |")
            continue
        missing = [d for d in deps(b) if not done(d)]
        if missing:
            outcome[bid] = "BLOCKED"
            lines.append(f"| {bid} | BLOCKED | waits for {', '.join(missing)} |")
            continue
        code_rows = [r for r in rows if str(r.get("field_path")).startswith(CODE_PATHS)]
        if code_rows and bid not in DONE_CODE:
            outcome[bid] = "BLOCKED"
            lines.append(f"| {bid} | BLOCKED | code not written yet ({code_rows[0]['field_path']}) |")
            continue
        data_rows = [r for r in rows if str(r.get("field_path")) != "—" and r not in code_rows]
        if code_rows and not data_rows:
            outcome[bid] = "OK"
            lines.append(f"| {bid} | OK | code bundle ({len(code_rows)} code rows) |")
            continue
        if not data_rows:
            outcome[bid] = "APPLIED" if bid in DONE_CODE else "BLOCKED"
            lines.append(f"| {bid} | {outcome[bid]} | code bundle{'' if bid in DONE_CODE else ': code not written yet'} |")
            continue
        verdicts, conflict = [], None
        for r in data_rows:
            try:
                uid, m = mapper(r)
                cur = m(st, uid)
            except Unmapped as ex:
                conflict = f"{r['field_path']}: {ex}"
                break
            new, exp = r.get("new_value"), expected(r)
            if equal(st, r, cur, new):
                verdicts.append("ALREADY_APPLIED")
            elif equal(st, r, cur, exp):
                verdicts.append("OK")
            else:
                conflict = f"{r['field_path']}: current {cur}, expected {exp}, new {new}"
                break
        if conflict:
            outcome[bid] = "CONFLICT"
            lines.append(f"| {bid} | CONFLICT | {conflict} |")
            continue
        if all(v == "ALREADY_APPLIED" for v in verdicts):
            outcome[bid] = "ALREADY_APPLIED"
            lines.append(f"| {bid} | ALREADY_APPLIED | |")
            continue
        note = " (with ALREADY_APPLIED rows)" if "ALREADY_APPLIED" in verdicts else ""
        # Applied in memory in a dry run too (a later bundle's expected_before is an earlier one's new value).
        if True:
            for r, v in zip(data_rows, verdicts):
                if v == "OK":
                    uid, m = mapper(r)
                    m(st, uid, r.get("new_value"), write=True)
            # R8: a unit-scope bundle never changes a weapon.
            if json.dumps(st.data["weapons"], sort_keys=True) != weapons_before:
                raise SystemExit(f"{bid}: a weapon changed (R8)")
        outcome[bid] = "OK"
        lines.append(f"| {bid} | OK{' (dry)' if dry else ''} | {len(data_rows)} rows{note} |")

    if not dry:
        if doc.text != open(BALANCE, encoding="utf-8", newline="").read():
            with open(BALANCE, "w", encoding="utf-8", newline="") as f:
                f.write(doc.text)
        applied |= {b for b, v in outcome.items() if v in ("OK", "ALREADY_APPLIED")}
        with open(STATE, "w", encoding="utf-8", newline="\n") as f:
            json.dump(sorted(applied), f, indent=1)
            f.write("\n")
    with open(LOG, "a", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    counts = {}
    for k, v in outcome.items():
        if any(fnmatch.fnmatch(k, p.strip()) for p in patterns):
            counts[v.split("(")[0]] = counts.get(v.split("(")[0], 0) + 1
    print(counts)
    return outcome


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundles", default="*")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    if not os.path.exists(LOG):
        with open(LOG, "w", encoding="utf-8", newline="\n") as f:
            f.write("# Prompt 29 apply log (Tools/balance/p29_apply.py)\n")
    run(args.bundles.split(","), args.dry)


if __name__ == "__main__":
    main()
