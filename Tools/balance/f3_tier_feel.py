"""MB_FINAL F3 (the owner's final bundle, VIEC_CHO_AGENT_FINAL section 6, "VFX/feel"): a static check that every weapon's
look grows in step with what it does. Reads balance.json only (no Unity, no run).

    python Tools/balance/f3_tier_feel.py            # writes Docs/checks/f3_tier_feel.md, exit 1 on any mismatch

The T0-T5 tier (the firing look: flash, tongues, the hull's squat and recoil; the landing overlay) comes from the weapon's
family (`weaponFamilyTable`: calibre for guns, warhead for missiles, rockets and bombs; `TierFx.Looks` overrides a few in
the view). The blast's size is its `impactTier` (Small..Ultimate), its rings the real core and edge. The checks:

1. Tier by calibre / warhead: within guns (shell, bullet) a bigger calibre never has a lower tier; within missiles, rockets
   and bombs a heavier warhead (warheadKg, else size) never has a lower tier, except across kinds the table keeps apart.
2. In step with the hit: a weapon of a higher tier that both deals less damage a round (under 0.8 x) and reaches less (core
   under the other's) and whose blast (impactTier) is bigger is listed (a stronger, wider hit drawn smaller); with a blast no
   bigger it is listed apart, kept by calibre (MB_FINAL: the tier is the bore's or the charge's). Boss templates and second
   rounds count on the side of whoever fires them. Re-run after a balance pass changes damage or splash.
3. Tier against blast size: the blast's band (Small 1 .. Ultimate 5) more than one band from the tier is listed (a look
   that does not match the overlay; a deliberate Large + T4 (Tomahawk, Kalibr from the ships) is one band apart and passes).
"""
from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

from jsonc_edit import loads  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
BALANCE = os.path.join(ROOT, "Assets", "MachineBrigade", "Resources", "Data", "balance.json")
TIERFX = os.path.join(ROOT, "Assets", "MachineBrigade", "Scripts", "Game", "Effects", "TierFx.cs")
REPORT = os.path.join(ROOT, "Docs", "checks", "f3_tier_feel.md")
BANDS = {"Small": 1, "Medium": 2, "Large": 3, "Huge": 4, "Ultimate": 5}
GUNS = {"Shell", "Bullet"}
CHARGES = {"Missile", "Rocket", "Bomb", "Drone"}


def num(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def view_looks():
    text = open(TIERFX, encoding="utf-8").read()
    return {m.group(1): int(m.group(2)) for m in re.finditer(r'\["([a-z0-9_]+)"\]\s*=\s*\((\d),', text)}


def main():
    data = loads(open(BALANCE, encoding="utf-8").read())
    table = {f["id"]: int(f.get("tier", -1)) for f in data.get("weaponFamilyTable", [])}
    # Every weapon as Catalog reads it (inherits, the prompt 25 family blocks), and which ones bosses fire (p34_families).
    import p34_families as F
    ws = F.Weapons(data)
    weapons = {wid: ws.resolve(wid) for wid in ws.raw}
    looks = view_looks()
    # Boss rounds are at boss scale (damage a round several times a vehicle's): compared only with each other.
    boss_ids, player_ids, _ = F.users(data)
    # MB_FINAL blast sizes: a boss template nobody fires itself (p26_typhon_ty100 under p26_typhon_direct_ty100) and a
    # second round (roundOf) are at the scale of whoever fires them: a parent fired only through boss children is a boss
    # round, a round takes its gun's side.
    children = {}
    for wid, raw in ws.raw.items():
        if raw.get("inherits"):
            children.setdefault(raw["inherits"], []).append(wid)

    def boss_scale(wid, seen=()):
        if wid in boss_ids:
            return True
        if wid in player_ids or wid in seen:
            return False
        parent = ws.raw[wid].get("roundOf")
        if parent in ws.raw:
            return boss_scale(parent, seen + (wid,))
        kids = [k for k in children.get(wid, []) if not ws.raw[k].get("roundOf")]
        return bool(kids) and all(boss_scale(k, seen + (wid,)) for k in kids)

    rows = []
    for wid, w in weapons.items():
        fam = w.get("weaponFamilyId")
        tier = looks.get(wid, table.get(fam, -1) if fam else -1)
        if tier < 0:
            continue
        kind = w.get("projectile") or ""
        calibre = num(w.get("caliberMm")) or num(w.get("size"))
        charge = num(w.get("warheadKg")) or num(w.get("size"))
        rows.append(dict(id=wid, fam=fam, tier=tier, kind=kind, calibre=calibre, charge=charge, damage=num(w.get("damage")),
                         core=num(w.get("splash")), impact=w.get("impactTier"), boss=boss_scale(wid),
                         air=w.get("targets") == "Air"))
    by_calibre, in_step, by_bore, bands = [], [], [], []
    # The calibre table's families only (a railgun's or coilgun's slug is drawn by its own family, not a bore).
    guns = [r for r in rows if r["kind"] in GUNS and r["calibre"] > 0 and str(r["fam"]).startswith(("cal_", "rcl_", "gl_"))]
    for a in guns:
        for b in guns:
            if a["calibre"] > b["calibre"] * 1.05 and a["tier"] < b["tier"] and a["fam"] != b["fam"]:
                by_calibre.append((a, b, "calibre"))
    charges = [r for r in rows if r["kind"] in CHARGES and r["charge"] > 0 and not str(r["fam"]).startswith(("cal_", "rcl_", "gl_"))]
    for a in charges:
        for b in charges:
            if a["kind"] == b["kind"] and a["air"] == b["air"] and a["charge"] > b["charge"] * 1.25 and a["tier"] < b["tier"] and a["fam"] != b["fam"]:
                by_calibre.append((a, b, "warhead"))
    for a in rows:
        for b in rows:
            if a["kind"] == b["kind"] and a["boss"] == b["boss"] and a["air"] == b["air"] and a["tier"] > b["tier"] and                     a["damage"] < 0.8 * b["damage"] and a["core"] < b["core"]:
                # MB_FINAL blast sizes: the tier is the calibre's or warhead's (the sheet keeps it, section 6), so a bigger
                # bore that hits softer keeps its firing look; it is out of step only if its blast (impactTier) is also
                # drawn bigger than the harder, wider hit's. The rest are listed apart, for the next balance pass.
                (in_step if BANDS.get(a["impact"], 0) > BANDS.get(b["impact"], 0) else by_bore).append((a, b))
    for r in rows:
        if r["impact"] in BANDS and abs(BANDS[r["impact"]] - max(1, r["tier"])) > 1:
            bands.append(r)
    out = ["# MB_FINAL F3: weapon look against its hit (static, `python Tools/balance/f3_tier_feel.py`)", "",
           f"{len(rows)} weapons with a tier; {len(by_calibre)} tier/calibre inversions, {len(in_step)} hits drawn smaller than a "
           f"weaker one ({len(by_bore)} more kept by calibre), {len(bands)} blast sizes two or more bands from the tier.", ""]
    out += ["## 1. Tier by calibre / warhead", "", "| weapon (tier, mm or kg) | lower-tier weapon it outweighs |", "|---|---|"]
    key = {"calibre": "calibre", "warhead": "charge"}
    out += [f"| {a['id']} (T{a['tier']}, {a[key[k]]:g}) | {b['id']} (T{b['tier']}, {b[key[k]]:g}) |" for a, b, k in by_calibre[:60]]
    out += ["", "## 2. In step with the hit", "", "| higher tier (dmg, core) | lower tier that hits harder and wider |", "|---|---|"]
    out += [f"| {a['id']} (T{a['tier']}, {a['damage']:g}, {a['core']:g} m) | {b['id']} (T{b['tier']}, {b['damage']:g}, {b['core']:g} m) |"
            for a, b in in_step[:60]]
    out += ["", f"Kept by calibre / warhead ({len(by_bore)}): a higher tier (its bore or charge) that hits softer than a lower one, "
            "its blast no bigger than the other's (the sheet's per-round damage; the tier stays the calibre's).", "",
            "| higher tier (dmg, core, blast) | lower tier that hits harder and wider (blast) |", "|---|---|"]
    out += [f"| {a['id']} (T{a['tier']}, {a['damage']:g}, {a['core']:g} m, {a['impact']}) | {b['id']} (T{b['tier']}, {b['damage']:g}, "
            f"{b['core']:g} m, {b['impact']}) |" for a, b in by_bore[:60]]
    out += ["", "## 3. Blast size against tier", "", "| weapon | tier | impactTier |", "|---|---|---|"]
    out += [f"| {r['id']} | T{r['tier']} | {r['impact']} |" for r in bands[:80]]
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
    print(out[2])
    return 1 if by_calibre or in_step or bands else 0


if __name__ == "__main__":
    sys.exit(main())
