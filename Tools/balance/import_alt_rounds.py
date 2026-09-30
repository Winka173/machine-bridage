"""Prompt 25 G (DECISIONS 25G): second rounds ("đạn thay thế") from the balance sheet, re-runnable.

The sheet "Vũ khí đề xuất", column "Loại đạn thay thế gợi ý", suggests in words a second round for 69 weapons. This
script reads it (openpyxl, data_only) and writes one block of balance.json, "secondRounds": every round is a weapon of
its own ("roundOf": the gun it is loaded in, whose line it inherits) with its switch rule ("for": what it is loaded
for; "elite": only elites and rank-7 branches load it), and the families (A3) that group the same real round on
several guns. The only other lines it touches are those of an existing round a family takes in (the 2A83's HE-FRAG).

The words become data by these rules (DECISIONS 25G lists them with the reasons):
  * "Tự đổi: đạn xuyên (Động năng) với xe, đạn nổ trên không (Mảnh) với máy bay/drone" (the 20-40 mm autocannons):
    the gun keeps the round its own damage type is; the other is its second round. A kinetic gun gets the new
    air-burst (flak) round for aircraft and drones; a flak gun an armour-piercing round for everything on the ground;
    a high-explosive gun (the gunship's 40 mm) both, the armour-piercing one for armour only (its HE stays for the rest).
  * "đạn xuyên (Động năng) với xe giáp, đạn nổ mạnh (HE, xuyên N, nổ lan M m) với xe nhẹ và công trình" (tank guns):
    a high-explosive round for light vehicles and structures, with the sheet's penetration and blast, unless the same
    real gun already has an HE round in the data (the 2A83's HE-FRAG), whose numbers it then takes (A5: one round,
    one blast).
  * "Thêm đạn dẫn đường (Excalibur/Krasnopol: 1 phát, không tản mát) cho nhánh hạng 7 hoặc thẻ hỗ trợ" (big HE guns):
    a guided shell, one round a pull, no scatter, steered onto its target, for armour, elites and rank-7 branches only.
  * "Đạn xuyên API (xuyên N) cho bản tinh nhuệ" (12.7 mm machine guns): an armour-piercing incendiary round with the
    sheet's penetration, loaded for any target, elites and rank-7 branches only.
Where the words leave a number out, it comes from the gun's own numbers and prompt 13's calibre scale: a round's
damage is its calibre's (the gun's own), its speed and cadence the gun's; an air-burst round's penetration is
prompt 15 B.1's (1 below 30 mm, 2 from 30 mm) and its blast calibre / 12 m to the half metre (the 2A38's 30 mm at
2.5 m); an armour-piercing autocannon round pierces 2 (B.1); a high-explosive round bursts one impact size up.

Run from anywhere: python Tools/balance/import_alt_rounds.py [--check]  (--check: report only, write nothing).
"""
from __future__ import annotations

import argparse
import collections
import os
import re
import sys

import openpyxl

sys.path.insert(0, os.path.dirname(__file__))
import import_xlsx as X  # noqa: E402
import steps_a3 as F  # noqa: E402
from jsonc_edit import Doc  # noqa: E402

SHEET = "Vũ khí đề xuất"
COLUMN = "Loại đạn thay thế gợi ý"
BLOCK = "secondRounds"
NL = "\n"

# Weapons the sheet suggests a round for that get none, and why (the report and DECISIONS 25G repeat them).
SKIP = {
    "c_ram_gatling": "an intercept-only gun (DECISIONS 21F: it fires at incoming rounds only); a round for vehicles "
                     "would make it a ground gun",
    "gun_152": "has its high-explosive round already (gun_152_he, prompt 17 D.6): kept as it is",
    "gun_152_he": "is itself the heavy tank's second round (gun_152's high explosive)",
}

TIERS = ["Small", "Medium", "Large", "Huge", "Ultimate"]

# Round kinds: the id suffix, the words after the gun's real name, the form (icon), the round word the UI shows.
KINDS = {
    "flak": ("_flak", "air-burst", "Airburst"),
    "ap": ("_ap", "AP", "BeltedAutocannon"),
    "he": ("_he", "HE", "HeShell"),
    "guided": ("_guided", "guided", "HeShell"),
    "api": ("_api", "API", "BulletBig"),
}


def half(v: float) -> float:
    return round(v * 2.0) / 2.0


def real_parts(real: str) -> tuple[str, str]:
    """A real name split into the weapon and its mount in brackets ("2A42 30 mm", "(twin)")."""
    m = re.match(r"^(.*?)(\s*\([^)]*\))?\s*$", real)
    return m.group(1).strip(), (m.group(2) or "").strip()


def clauses(text: str) -> list[dict]:
    """The rounds a suggestion names: kind, targets, penetration, blast, gate, and its other words."""
    t = text.strip().rstrip(".")
    elite = "tinh nhuệ" in t or "nhánh hạng 7" in t
    if "dẫn đường" in t:
        return [{"kind": "guided", "for": ["armour"], "elite": elite, "single": "1 phát" in t, "noScatter": "không tản mát" in t,
                 "support": "thẻ hỗ trợ" in t}]
    if "API" in t:
        pen = re.search(r"xuyên (\d)", t)
        return [{"kind": "api", "for": ["any"], "elite": elite, "pen": int(pen.group(1)) if pen else None}]
    body = t.split(":", 1)[1] if t.startswith("Tự đổi") and ":" in t else t
    out = []
    for part in re.split(r",\s*(?=đạn)", body):
        part = part.strip()
        m = re.match(r"đạn (.+?)(?: \(([^)]*)\))? với (.+)$", part)
        if not m:
            raise ValueError(f"cannot read '{part}' in '{text}'")
        name, inside, whom = m.group(1), m.group(2) or "", m.group(3)
        if "nổ trên không" in name:
            kind = "flak"
        elif "nổ mạnh" in name:
            kind = "he"
        elif "xuyên" in name:
            kind = "ap"
        else:
            raise ValueError(f"no round kind in '{part}'")
        targets = []
        if "máy bay" in whom or "drone" in whom:
            targets.append("air")
        if "xe giáp" in whom:
            targets.append("armour")
        if "xe nhẹ" in whom:
            targets.append("light")
        if "cụm xe" in whom:
            targets.append("cluster")
        if "công trình" in whom:
            targets.append("structure")
        if not targets and re.search(r"\bxe\b", whom):
            targets.append("ground")
        pen = re.search(r"xuyên (\d)", inside)
        splash = re.search(r"nổ lan (\d+(?:[.,]\d+)?) m", inside)
        out.append({"kind": kind, "for": targets, "elite": elite, "pen": int(pen.group(1)) if pen else None,
                    "splash": X.num(splash.group(1)) if splash else None})
    return out


def own_kind(gun: dict) -> str | None:
    """The round a gun fires now, in the suggestion's words: kinetic and shaped charges pierce, fragmentation bursts."""
    t = gun.get("damageType")
    if t in ("Kinetic", "ShapedCharge"):
        return "ap"
    if t == "Fragmentation":
        return "flak"
    if t == "HighExplosive":
        return "he"
    return None


def pen_default(kind: str, size: float, gun: dict) -> int:
    """Prompt 15 B.1 (Armour.DefaultPenetration) for a round the words give no penetration."""
    if kind == "flak":
        return 2 if size >= 30 else 1
    if kind == "ap":
        return 3 if size >= 57 else 2
    return int(gun.get("pen", 1))


def tier_up(tier: str) -> str:
    i = TIERS.index(tier) if tier in TIERS else 0
    return TIERS[min(i + 1, TIERS.index("Huge"))] if i < TIERS.index("Huge") else tier


class Plan:
    def __init__(self, game: X.Game, rows):
        self.g = game
        self.rows = rows
        self.rounds: list[dict] = []
        self.skipped: list[tuple[str, str]] = []
        self.notes: list[str] = []
        self.existing_he = self._existing_he()

    def _existing_he(self) -> dict[str, str]:
        """Existing HE rounds by gun ("2A83 152 mm" -> gun_152_he): a gun's "he" target."""
        out = {}
        for wid, raw in self.g.raw_weapons.items():
            if "he" in raw:
                he = self.g.weapon(raw["he"])
                base, _ = real_parts(he.get("real", ""))
                out[re.sub(r"\s+HE(-FRAG)?$", "", base)] = raw["he"]
        return out

    def gun_base(self, gun: dict) -> str:
        base, _ = real_parts(gun.get("real", ""))
        return re.sub(r"\s+(HE(-FRAG)?|HEAT|APFSDS|AP)$", "", base)

    def build(self):
        head_ids = set()
        for wid, text in self.rows:
            head_ids.add(wid)
            if wid in SKIP:
                self.skipped.append((wid, SKIP[wid]))
                continue
            if wid not in self.g.raw_weapons:
                self.skipped.append((wid, "not in balance.json"))
                continue
            gun = self.g.weapon(wid)
            own = own_kind(gun)
            wanted = clauses(text)
            made = 0
            for c in wanted:
                if c["kind"] == own and c["kind"] in ("ap", "flak", "he") and len(wanted) > 1:
                    continue  # the gun's own round
                if c["kind"] == "ap" and own == "he" and c["for"] == ["ground"]:
                    c = dict(c, **{"for": ["armour"]})  # the HE gun keeps its own round for the rest
                self.rounds.append(self.round(wid, gun, c))
                made += 1
            if made == 0:
                self.skipped.append((wid, "the suggestion names only the round it fires"))

    def round(self, wid: str, gun: dict, c: dict) -> dict:
        kind = c["kind"]
        suffix, word, form = KINDS[kind]
        size = float(gun.get("size", 0) or 0)
        _, mount = real_parts(gun.get("real", wid))
        base = self.gun_base(gun)
        r = {"id": wid + suffix, "roundOf": wid, "inherits": wid, "round": kind, "for": c["for"]}
        if c.get("elite"):
            r["elite"] = True
        real = f"{F.ALIASES.get(base, base)} {word}"
        extra = {}
        if kind == "flak":
            extra = {"damageType": "Fragmentation", "pen": c.get("pen") or pen_default("flak", size, gun),
                     "splash": half(size / 12.0), "targets": "Air", "piercing": False}
        elif kind == "ap":
            extra = {"damageType": "Kinetic", "pen": c.get("pen") or pen_default("ap", size, gun), "splash": 0,
                     "targets": "Ground", "piercing": True}
        elif kind == "he":
            same = self.existing_he.get(self.gun_base(gun))
            if same:
                he = self.g.weapon(same)
                real = real_parts(he["real"])[0]
                extra = {"damageType": "HighExplosive", "pen": he.get("pen"), "splash": he.get("splash", 0),
                         "projectileSpeed": he.get("projectileSpeed"), "impactTier": he.get("impactTier"),
                         "roundWeight": he.get("roundWeight"), "joins": same}
            else:
                extra = {"damageType": "HighExplosive", "pen": c.get("pen") or 2,
                         "splash": c.get("splash") if c.get("splash") is not None else gun.get("splash", 0),
                         "impactTier": tier_up(gun.get("impactTier", "Medium"))}
            extra.update({"targets": "Ground", "piercing": False})
        elif kind == "guided":
            extra = {"damageType": gun.get("damageType"), "pen": gun.get("pen"), "spread": 0, "guided": True, "targets": "Ground"}
            if c.get("single"):
                extra["burst"] = 1
        elif kind == "api":
            extra = {"damageType": "Kinetic", "pen": c.get("pen") or 2, "piercing": True}
        r["real"] = real + (f" {mount}" if mount else "")
        # The same real round hits the same wherever it is fired (13's calibre scale): an existing round's damage.
        r["damage"] = self.g.weapon(extra["joins"])["damage"] if extra.get("joins") else gun["damage"]
        r["form"] = form
        r.update({k: v for k, v in extra.items() if v is not None})
        # Nothing of the gun's that is not this round's: its bonuses, its own second round, its family.
        if gun.get("bonuses"):
            r["bonuses"] = []
        r["weaponFamily"] = ""
        return r

    def families(self):
        """A3 for the new rounds: one family for each real round fired from two guns or more, or with an existing one."""
        def key(w):
            return F.real_key(w)
        resolved = {}
        for r in self.rounds:
            w = dict(self.g.weapon(r["inherits"]))
            for k in ("he", "air"):
                w.pop(k, None)
            w.update({k: v for k, v in r.items() if k != "joins"})
            resolved[r["id"]] = w
        groups = collections.defaultdict(list)
        for rid, w in resolved.items():
            groups[key(w)].append(rid)
        existing = collections.defaultdict(list)
        for wid in self.g.raw_weapons:
            k = key(self.g.weapon(wid))
            if k in groups:
                existing[k].append(wid)
        fams = []
        joined = []
        for k, members in sorted(groups.items(), key=lambda kv: kv[1][0]):
            olds = existing.get(k, [])
            if len(members) + len(olds) < 2:
                continue
            first = resolved[members[0]]
            fid = re.sub(r"[^a-z0-9]+", "_", k[0].lower()).strip("_")
            if any(f["id"] == fid for f in fams):
                fid += "_lobbed" if k[4] else "_direct"
            fam = {"id": fid, "real": k[0]}
            for field in ("projectileSpeed", "splash", "roundWeight", "projectileModel"):
                values = {repr(resolved[m].get(field)) for m in members}
                if len(values) > 1:
                    self.notes.append(f"{fid}: members differ in {field} ({', '.join(sorted(values))}); the first's kept")
                v = first.get(field)
                if v is None and field == "splash":
                    v = 0
                if v is not None:
                    fam[field] = v
            fams.append(fam)
            for m in members:
                for r in self.rounds:
                    if r["id"] == m:
                        r["weaponFamily"] = fid
            for old in olds:
                joined.append((old, fid))
        return fams, joined


def read_rows(wb) -> list[tuple[str, str]]:
    head, rows = X.sheet(wb, SHEET)
    ci = head.index(COLUMN)
    return [(r[0], str(r[ci]).strip()) for r in rows if r[0] and r[ci]]


ORDER = ["id", "roundOf", "inherits", "weaponFamily", "round", "for", "elite", "real", "damageType", "pen", "damage", "splash",
         "spread", "burst", "guided", "form", "piercing", "targets", "projectileSpeed", "impactTier", "bonuses"]


def line(r: dict) -> str:
    ordered = {k: r[k] for k in ORDER if k in r}
    ordered.update({k: v for k, v in r.items() if k not in ordered and k != "joins"})
    return X.fmt({k: F.number(v) for k, v in ordered.items()})


HEAD = (
    "  // Prompt 25 G (DECISIONS 25G): second rounds (\"đạn thay thế\"), written by Tools/balance/import_alt_rounds.py from the\n"
    "  // sheet's \"Loại đạn thay thế gợi ý\" (Vũ khí đề xuất): rerun it rather than editing by hand. A round is a weapon of its\n"
    "  // own: \"roundOf\" the gun it is loaded in (its line inherited, so its cadence, reach and speed are the gun's), \"round\"\n"
    "  // its kind (flak, ap, he, guided, api), \"for\" what the gun loads it for (air: aircraft and drones; ground: anything on\n"
    "  // the ground; armour: a vehicle of front armour 2 or more; light: 1 or less; structure: a fixed defence, a wall or a\n"
    "  // building; cluster: a vehicle with two more of its side in the blast; any), \"elite\": elites and rank-7 branches\n"
    "  // only. The gun keeps its own round for everything else. A switch takes the gun's reload (at least 0.5 s) and a\n"
    "  // loaded round stays in at least 2 s. \"families\" are prompt 25 A3's weapon families of the new rounds.\n"
)


def write(doc: Doc, fams, rounds) -> None:
    lines = ["{", '    "families": [']
    for i, f in enumerate(fams):
        lines.append("      " + X.fmt({k: F.number(v) for k, v in f.items()}) + ("," if i < len(fams) - 1 else ""))
    lines.append("    ],")
    lines.append('    "rounds": [')
    for i, r in enumerate(rounds):
        lines.append("      " + line(r) + ("," if i < len(rounds) - 1 else ""))
    lines.append("    ]")
    lines.append("  }")
    body = NL.join(lines)
    if doc.has_section(BLOCK):
        s0, e0 = doc._section(BLOCK)
        doc.text = doc.text[:s0] + body + doc.text[e0 + 1:]
    else:
        at = doc.text.index("\n  // Prompt 25 A3 (DECISIONS 25A): weapon families.")
        doc.text = doc.text[:at + 1] + HEAD + f'  "{BLOCK}": ' + body + ",\n\n" + doc.text[at + 1:]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="report only")
    args = ap.parse_args()
    wb = openpyxl.load_workbook(X.XLSX, data_only=True)
    rows = read_rows(wb)
    doc = Doc(X.BALANCE)
    game = X.Game(doc)
    plan = Plan(game, rows)
    plan.build()
    fams, joined = plan.families()
    taken = set(game.raw_weapons)
    for r in plan.rounds:
        if r["id"] in taken:
            raise SystemExit(f"{r['id']}: an existing weapon has this id")
    guns = sorted({r["roundOf"] for r in plan.rounds})
    print(f"{len(rows)} suggestions: {len(guns)} weapons get {len(plan.rounds)} second rounds; {len(plan.skipped)} skipped")
    for wid, why in plan.skipped:
        print(f"  skipped {wid}: {why}")
    by_kind = collections.Counter(r["round"] for r in plan.rounds)
    print("  rounds by kind: " + ", ".join(f"{k} {n}" for k, n in sorted(by_kind.items())))
    print(f"  {len(fams)} families; existing rounds joining one: " + (", ".join(f"{o} -> {f}" for o, f in joined) or "none"))
    for n in plan.notes:
        print("  note: " + n)
    if args.check:
        return 0
    write(doc, fams, plan.rounds)
    for old, fid in joined:
        doc.edit("weapons", old, lambda e, fid=fid: e.set("weaponFamily", fid), f"{old}: weaponFamily {fid}")
    print("balance.json " + ("written" if doc.save() else "unchanged"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
