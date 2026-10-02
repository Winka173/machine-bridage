"""Prompt 34 L1: weapon families (weaponFamilyId / weaponVariantId) on every weapon, boss and player (DECISIONS "Prompt 34 L1").

Run from anywhere: `python Tools/balance/p34_families.py` (a dry run that prints what it would change), `--write` to save
balance.json and Docs/checks/player_weapon_family.md. A second run changes nothing.

  * A family is a calibre class for guns (the prompt's table: "152-155 mm", "120 mm HE", ...) and the real weapon for
    everything else (missiles, bombs, drones, lasers). The same real name always lands in the same family.
  * A variant (weaponVariantId) only where the round, its form or the fire mode really differs (flak on a gun whose family
    fires plain rounds, an AP dart on an HE calibre); each variant's reason is in the family table ("variants").
  * The table goes into balance.json as "weaponFamilyTable" (id, name, tier T0-T5, the boss numbers of prompt 34 L2 where
    the prompt lists them, the variants and their reasons). Catalog reads the id, the tier and the variants.
  * Player numbers are not changed. Weapons in the same family that differ (damage a round, speed, blast, damage type)
    are listed in Docs/checks/player_weapon_family.md.
  * Display fixes: Roc's bomb stick is a 400 kg bomb (family bomb, size 400, so no "203 mm" after its name); the
    Smerch pods are 300 mm (their size said 122). The lasers lose their "mm" in UnitLines.WeaponName (code).
"""
from __future__ import annotations

import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

from jsonc_edit import Doc, Entry, fmt, _match, _skip  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
PATH = os.path.join(ROOT, "Assets", "MachineBrigade", "Resources", "Data", "balance.json")
REPORT = os.path.join(ROOT, "Docs", "checks", "player_weapon_family.md")

# ------------------------------------------------------------------------------------------------ the family table

# (id, name, tier, boss numbers {damage, core, edge} or None, {variant: reason})
# The boss numbers are the prompt's table (boss scale, a round's damage; core and edge in metres; edge 0 = one layer).
TABLE = [
    ("cal_7_62", "7.62 mm machine gun", 0, None, {}),
    ("cal_12_7", "12.7 mm heavy machine gun", 0, {"damage": 15, "core": 0, "edge": 0}, {}),
    ("cal_14_5", "14.5 mm heavy machine gun", 0, None, {}),
    ("cal_20", "20 mm", 1, None, {}),
    ("cal_23", "23 mm", 1, {"damage": 7, "core": 0, "edge": 0}, {}),
    ("cal_25", "25 mm", 1, None, {"flak": "air-burst rounds against aircraft, the family's others are plain belted rounds"}),
    ("cal_30", "30 mm", 1, {"damage": 22, "core": 0, "edge": 0},
     {"flak": "the 2A38 / AK-630 air-burst (fragmentation, a 2.5 m burst) against aircraft; the family's round is a plain AP / HE belt"}),
    ("cal_35", "35 mm Oerlikon", 1, {"damage": 25, "core": 2.5, "edge": 0},
     {"ap": "AP rounds (no burst) loaded against ground targets instead of the air-burst"}),
    ("cal_40", "40 mm Bofors", 1, {"damage": 30, "core": 0, "edge": 0},
     {"flak": "proximity air-burst (3.5 m) against aircraft",
      "he": "the AC-130's 40 mm HE against the ground (a 3 m burst), not the plain round"}),
    ("gl_40", "40 mm grenade launcher", 1, None, {}),
    ("cal_57", "57 mm", 2, {"damage": 120, "core": 3, "edge": 6},
     {"ap": "AP rounds (kinetic, no burst) instead of HE", "flak": "air-burst against aircraft"}),
    ("rcl_73", "73 mm recoilless", 2, None, {}),
    ("cal_76", "76 mm", 2, None, {}),
    ("cal_100_105_he", "100-105 mm HE", 2, {"damage": 300, "core": 5, "edge": 10},
     {"flak": "the KS-19's time-fused flak against aircraft"}),
    ("cal_100_105_ap", "100-105 mm AP", 2, None, {"he": "a high-explosive second round of an AP gun"}),
    ("rcl_106", "106 mm recoilless", 2, None, {}),
    ("cal_120_he", "120 mm HE", 3, {"damage": 340, "core": 5, "edge": 10},
     {"mortar": "a lobbed mortar bomb (slow, high arc), not a gun's HE shell"}),
    ("cal_120_ap", "120 mm AP", 3, {"damage": 260, "core": 0, "edge": 0}, {}),
    ("cal_125_ap", "125 mm AP", 3, {"damage": 400, "core": 0, "edge": 0}, {}),
    ("cal_125_he", "125 mm HE", 3, None, {}),
    ("cal_127_130", "127-130 mm", 3, {"damage": 380, "core": 5, "edge": 10}, {}),
    ("cal_140", "140 mm", 3, None, {}),
    ("cal_152_155", "152-155 mm", 3, {"damage": 600, "core": 7, "edge": 14},
     {"ap": "an armour-piercing round fired direct (a tank gun's or a naval gun's AP), not the HE shell",
      "heat": "a shaped-charge (HEAT) round",
      "smart": "a sensor-fuzed or guided shell with submunitions",
      "guided": "a guided shell (one at a time)"}),
    ("cal_203", "203 mm", 4, {"damage": 900, "core": 8.5, "edge": 17}, {}),
    ("cal_240", "240 mm", 4, {"damage": 1100, "core": 10, "edge": 20}, {}),
    ("cal_406", "406 mm", 5, {"damage": 2400, "core": 14, "edge": 24}, {}),
    ("cal_800", "800 mm super-gun", 5, None, {}),
    ("rkt_70_80", "70-80 mm rockets", 2, None, {"guided": "a laser-guided rocket (APKWS)"}),
    ("rkt_107", "107 mm rockets", 2, None, {}),
    ("rkt_grad_122", "Grad 122 mm rockets", 3, {"damage": 200, "core": 4.5, "edge": 9},
     {"thermobaric": "a thermobaric warhead", "cluster": "a cluster warhead (bomblets)"}),
    ("rkt_140", "140 mm rockets", 3, None, {}),
    ("rkt_tos_220", "TOS-1A 220 mm thermobaric", 4, None, {}),
    ("rkt_gmlrs_227", "GMLRS 227 mm", 4, None, {"cluster": "the M30's cluster warhead"}),
    ("rkt_smerch_300", "Smerch 300 mm rockets", 4, {"damage": 450, "core": 8, "edge": 16}, {}),
    ("bomb_400", "400 kg bomb", 4, {"damage": 700, "core": 10, "edge": 20}, {}),
    ("atgm_kornet", "9M133 Kornet", 2, {"damage": 230, "core": 0, "edge": 0}, {}),
    ("gungnir_emrg", "EMRG electromagnetic railgun (Gungnir)", 5, None, {}),
]
FAMILIES = {t[0]: t for t in TABLE}

# Variants allowed on a real-name family (missiles, bombs ...): none so far.
OPEN_VARIANTS: dict[str, str] = {}

GUN_FAMILIES = {"mg", "autocannon", "tank_gun", "howitzer", "mortar", "naval_gun", "grenade", "recoilless", "special"}


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def real_base(w) -> str:
    """The real name without its mount in brackets ("Oerlikon 35 mm (twin)" -> "Oerlikon 35 mm")."""
    return re.sub(r"\s*\(.*?\)", "", w.get("real") or "").strip()


def tier_of_open(w) -> int:
    """T0-T5 for a weapon outside the calibre table (prompt 34 L5's table): by family and size."""
    fam, size = w.get("family"), float(w.get("size") or 0)
    if fam in ("melee",) or fam is None:
        return 0
    if fam in ("flame", "laser"):
        return 1
    if fam in ("drone",):
        return 3 if size >= 50 else 2
    if fam in ("atgm", "missile", "aa_missile"):
        return 4 if size >= 500 else 3 if size >= 250 else 2
    if fam in ("cruise", "cruise_missile", "ballistic"):
        return 4
    if fam == "bomb":
        return 4 if size >= 400 else 3 if size >= 250 else 2
    if fam == "railgun":
        return 3 if size >= 32 else 2
    if fam == "special":
        return 0
    return 2


def classify(w) -> tuple[str, str | None, int]:
    """(family id, variant id or None, tier) of a resolved weapon line."""
    fam = w.get("family")
    size = float(w.get("size") or 0)
    real = real_base(w)
    rl = (w.get("real") or "").lower()
    dt = w.get("damageType", "Kinetic")
    proj = w.get("projectile", "Shell")
    frag = dt == "Fragmentation"
    he = dt == "HighExplosive"
    variant = None
    if w["id"] == "p26_gungnir_emrg" or "emrg" in rl:
        return "gungnir_emrg", None, 5
    if fam == "special" and size >= 800:
        return "cal_800", None, 5
    if fam == "bomb" and 380 <= size <= 420:
        return "bomb_400", None, 4
    if fam == "atgm" and "kornet" in rl:
        return "atgm_kornet", None, 2
    if fam == "rocket":
        if "smerch" in rl or size == 300:
            return "rkt_smerch_300", None, 4
        if size in (70, 80):
            return "rkt_70_80", ("guided" if "apkws" in rl else None), 2
        if size == 107:
            return "rkt_107", None, 2
        if size == 122:
            v = "thermobaric" if ("thermobaric" in rl or w.get("thermobaric")) else "cluster" if (w.get("cluster") or "cluster" in (w.get("projectileModel") or "")) else None
            return "rkt_grad_122", v, 3
        if size == 140:
            return "rkt_140", None, 3
        if size == 220:
            return "rkt_tos_220", None, 4
        if size == 227:
            return "rkt_gmlrs_227", ("cluster" if (w.get("cluster") or "m30" in rl) else None), 4
    if fam in GUN_FAMILIES and fam != "special":
        if fam == "grenade":
            return "gl_40", None, 1
        if fam == "recoilless" or "recoilless" in rl:
            return ("rcl_106", None, 2) if size >= 100 else ("rcl_73", None, 2)
        if size <= 8:
            return "cal_7_62", None, 0
        if size <= 13:
            return "cal_12_7", None, 0
        if size <= 15:
            return "cal_14_5", None, 0
        if size <= 21:
            return "cal_20", None, 1
        if size <= 24:
            return "cal_23", None, 1
        if size <= 26:
            return "cal_25", ("flak" if frag else None), 1
        if size <= 31:
            return "cal_30", ("flak" if frag else None), 1
        if size <= 36:
            return "cal_35", (None if frag or w.get("splash", 0) > 0 else "ap"), 1
        if size <= 41:
            return "cal_40", ("flak" if frag else "he" if he and w.get("splash", 0) > 0 else None), 1
        if size <= 58:
            return "cal_57", ("flak" if frag else "ap" if dt == "Kinetic" else None), 2
        if size <= 77:
            return "cal_76", None, 2
        if size <= 106:
            ap = dt in ("Kinetic", "ShapedCharge")
            if ap:
                return "cal_100_105_ap", None, 2
            return "cal_100_105_he", ("flak" if frag else None), 2
        if size <= 121:
            if dt in ("Kinetic", "ShapedCharge"):
                return "cal_120_ap", None, 3
            return "cal_120_he", ("mortar" if fam == "mortar" else None), 3
        if size <= 126:
            return ("cal_125_ap", None, 3) if dt in ("Kinetic", "ShapedCharge") else ("cal_125_he", None, 3)
        if size <= 131:
            return "cal_127_130", None, 3
        if size <= 141:
            return "cal_140", None, 3
        if size <= 156:
            if "smart" in rl or "bonus" in rl:
                variant = "smart"
            elif "guided" in rl:
                variant = "guided"
            elif dt == "ShapedCharge":
                variant = "heat"
            elif dt == "Kinetic":
                variant = "ap"
            return "cal_152_155", variant, 3
        if size <= 210:
            return "cal_203", None, 4
        if size <= 250:
            return "cal_240", None, 4
        if size <= 410:
            return "cal_406", None, 5
    # Everything else: the real weapon is the family.
    base = slug(real) or slug(w["id"])
    prefix = {"aa_missile": "sam", "atgm": "atgm", "missile": "msl", "cruise": "cruise", "cruise_missile": "cruise",
              "ballistic": "bal", "bomb": "bomb", "drone": "drone", "flame": "flame", "laser": "laser", "railgun": "rail",
              "melee": "melee", "special": "special", "rocket": "rkt"}.get(fam or "", "wpn")
    if fam == "missile" and dt == "ShapedCharge":
        prefix = "atgm"
    if base.startswith(prefix + "_"):
        return base, None, tier_of_open(w)
    return f"{prefix}_{base}", None, tier_of_open(w)


# ------------------------------------------------------------------------------------------------ the data

class Weapons:
    """Every weapon line (the "weapons" array and secondRounds.rounds), resolved through "inherits" and the prompt 25
    "weaponFamily" blocks, as Catalog does (the family's fields on top)."""

    def __init__(self, data):
        self.raw = {w["id"]: w for w in data["weapons"]}
        self.rounds = {r["id"]: r for r in (data.get("secondRounds") or {}).get("rounds", [])}
        self.raw.update(self.rounds)
        fams = list(data.get("weaponFamilies", [])) + list((data.get("secondRounds") or {}).get("families", []))
        self.p25 = {f["id"]: f for f in fams}
        self._cache = {}

    def resolve(self, wid, family_merge=True):
        key = (wid, family_merge)
        if key in self._cache:
            return self._cache[key]
        w = dict(self.raw[wid])
        if "inherits" in w:
            base = dict(self.resolve(w["inherits"]))
            base.update(w)
            w = base
        if family_merge and w.get("weaponFamily") in self.p25:
            for k, v in self.p25[w["weaponFamily"]].items():
                if k not in ("id", "real"):
                    w[k] = v
        self._cache[key] = w
        return w


def assignment(ws: Weapons):
    """{weapon id: (family, variant, tier)} for every line."""
    return {wid: classify(ws.resolve(wid)) for wid in ws.raw}


def edits(ws: Weapons, assign):
    """{weapon id: {key: value}}: the family on each line whose inherited family differs ("" clears an inherited variant)."""
    out = {}
    for wid, raw in ws.raw.items():
        fam, var, _ = assign[wid]
        parent = raw.get("inherits")
        inh_f = inh_v = None
        if parent:
            # What the parent line ends up with after this script (its own edit or its inherited value).
            inh_f, inh_v = resolved_ids(ws, parent, assign)
        e = {}
        if fam != inh_f:
            e["weaponFamilyId"] = fam
        if var != inh_v:
            e["weaponVariantId"] = var if var else ""
        if e:
            out[wid] = e
    return out


def resolved_ids(ws, wid, assign):
    return assign[wid][0], assign[wid][1]


def users(data):
    """(boss weapon ids, player weapon ids): which weapons boss mounts (and boss laid systems) and other vehicles carry."""
    sys.path.insert(0, HERE)
    import p26_ab as A  # noqa: E402
    import steps_c as S  # noqa: E402
    built = A.expand(data)
    boss = set()
    for b in built.values():
        for wid in S.mounts_of(b):
            if wid:
                boss.add(wid)
        for key in ("salvo", "cruise", "bombard"):
            if isinstance(b.get(key), dict) and b[key].get("weapon"):
                boss.add(b[key]["weapon"])
    player = set()
    for v in data["vehicles"]:
        if v["id"] in built:
            continue
        for wid in [v.get("weapon")] + [m.get("weapon") for m in v.get("secondary") or []]:
            if wid:
                player.add(wid)
    return boss, player, built


# ------------------------------------------------------------------------------------------------ writing

def table_block():
    lines = ['  // Prompt 34 L1 (DECISIONS "Prompt 34 L1"): weapon families. A weapon names its family ("weaponFamilyId": a calibre',
             '  // class for guns, the real weapon for the rest; the same real name is always the same family) and, only where the round',
             '  // or the fire mode really differs, a variant ("weaponVariantId", listed here with its reason). "tier" is T0-T5 (prompt',
             '  // 34 L3 warnings, L5 effects); "boss" is the boss scale of prompt 34 L2 (a round\'s damage, core and edge in metres; edge',
             '  // 0: one layer), applied to boss weapons by Tools/balance/p34_boss_families.py. Written by Tools/balance/p34_families.py.',
             '  "weaponFamilyTable": [']
    rows = []
    for fid, name, tier, boss, variants in TABLE:
        d = {"id": fid, "name": name, "tier": tier}
        if boss:
            d["boss"] = boss
        if variants:
            d["variants"] = variants
        rows.append("    " + fmt(d))
    lines.append(",\n".join(rows))
    lines.append("  ],")
    return "\n".join(lines)


def open_families(assign):
    """The real-weapon families (not in the calibre table) with their tier, for the table block."""
    seen = {}
    for wid, (fam, var, tier) in assign.items():
        if fam not in FAMILIES:
            seen[fam] = max(tier, seen.get(fam, 0))
    return seen


def full_table(assign):
    extra = open_families(assign)
    for fam in sorted(extra):
        TABLE.append((fam, fam, extra[fam], None, {}))
        FAMILIES[fam] = TABLE[-1]


def set_on(doc: Doc, wid, fields, rounds_ids):
    if wid in rounds_ids:
        return set_in_rounds(doc, wid, fields)

    def fn(e: Entry):
        for k, v in fields.items():
            e.set(k, v, after=_after(e))
    return doc.edit("weapons", wid, fn)


def _after(e: Entry):
    for k in ("weaponVariantId", "weaponFamilyId", "inherits", "roundOf", "id"):
        if e.has(k):
            return k
    return "id"


def set_in_rounds(doc: Doc, wid, fields):
    t = doc.text
    m = re.search(r'\n  "secondRounds"\s*:\s*', t)
    s = _skip(t, m.end())
    e = _match(t, s)
    r = re.compile(r'\{\s*"id"\s*:\s*"' + re.escape(wid) + r'"')
    mm = r.search(t, s, e)
    if not mm:
        raise KeyError(wid)
    a = mm.start()
    b = _match(t, a) + 1
    ent = Entry(t[a:b])
    for k, v in fields.items():
        ent.set(k, v, after=_after(ent))
    if ent.text != t[a:b]:
        doc.text = t[:a] + ent.text + t[b:]
        return True
    return False


DATA_FIXES = {
    # Display fixes (prompt 34 L1): Roc's bomb stick is a 400 kg bomb (family bomb: no "203 mm" after its name); the
    # Smerch pods are 300 mm. Penetration is explicit on both parents (boss_howitzer 4, boss_rockets 2): unchanged.
    "p26_roc_roc_bombs": {"family": "bomb", "size": 400},
    "p26_jotunn_jo_rockets": {"size": 300},
}


def main():
    write = "--write" in sys.argv
    doc = Doc(PATH)
    data = doc.data()
    # Data fixes first, so the families are taken from the fixed lines.
    for wid, f in DATA_FIXES.items():
        def fn(e: Entry, f=f):
            for k, v in f.items():
                e.set(k, v, after="real" if e.has("real") else "id")
        if doc.edit("weapons", wid, fn):
            print(f"fix {wid}: {f}")
    data = doc.data()
    ws = Weapons(data)
    assign = assignment(ws)
    full_table(assign)
    # Same real name, same family (variants aside).
    by_real = collections.defaultdict(set)
    for wid, (fam, var, _) in assign.items():
        rb = real_base(ws.resolve(wid))
        if rb:
            by_real[rb].add(fam)
    clash = {r: f for r, f in by_real.items() if len(f) > 1}
    for r, f in sorted(clash.items()):
        print(f"WARN real name '{r}' in families {sorted(f)}")
    # The table block.
    block = table_block()
    if doc.has_section("weaponFamilyTable"):
        s, e = doc._section("weaponFamilyTable")
        # Replace from the comment above the key to the closing bracket and its comma.
        m = list(re.finditer(r'\n(  //[^\n]*\n)*  "weaponFamilyTable"', doc.text[:s]))[-1]
        end = e + 1
        if doc.text[end] == ",":
            end += 1
        doc.text = doc.text[:m.start() + 1] + block + doc.text[end:]
    else:
        m = re.search(r'\n(  //[^\n]*\n)*  "weapons"\s*:', doc.text)
        doc.text = doc.text[:m.start() + 1] + block + "\n\n" + doc.text[m.start() + 1:]
    ed = edits(ws, assign)
    n = 0
    for wid, f in ed.items():
        if set_on(doc, wid, f, ws.rounds):
            n += 1
    print(f"{n} weapon lines tagged ({len(assign)} weapons, {len(set(a[0] for a in assign.values()))} families)")
    boss, player, _ = users(data)
    report = player_report(ws, assign, player, boss)
    if write:
        doc.save()
        with open(REPORT, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(report)
        print("written")
    else:
        print("dry run (--write saves)")


def player_report(ws, assign, player, boss):
    groups = collections.defaultdict(list)
    for wid in sorted(player):
        if wid not in ws.raw:
            continue
        fam, var, tier = assign[wid]
        groups[(fam, var or "")].append(wid)
    out = ["# Player weapon families: the deviations (prompt 34 L1)", "",
           "Written by `Tools/balance/p34_families.py`. Prompt 34 does not change player weapons. This list shows where weapons",
           "of the same family and variant differ in damage per round, round speed, blast (core / edge) or damage type. The",
           "boss table (L2) is a different scale (boss damage), so it is shown for reference only. Fix later, after prompt 29",
           "and the replacement-round balance.", "",
           "A row is the family (and variant), the field that differs, then each value with the weapons that have it.", ""]
    count = 0
    for (fam, var), ids in sorted(groups.items()):
        if len(ids) < 2:
            continue
        rows = []
        for field, get in (("damage", lambda w: w.get("damage")), ("projectileSpeed", lambda w: w.get("projectileSpeed")),
                           ("splash", lambda w: w.get("splash", 0)), ("edge", lambda w: w.get("edge", 0)),
                           ("damageType", lambda w: w.get("damageType"))):
            vals = collections.defaultdict(list)
            for wid in ids:
                vals[json.dumps(get(ws.resolve(wid)))].append(wid)
            if len(vals) > 1:
                rows.append(f"  - {field}: " + "; ".join(f"{v} ({', '.join(sorted(i))})" for v, i in sorted(vals.items())))
        if rows:
            count += 1
            t = FAMILIES.get(fam)
            ref = f" (boss table: {t[3]['damage']} a round)" if t and t[3] else ""
            out.append(f"- **{fam}{' / ' + var if var else ''}**, T{assign[ids[0]][2]}{ref}: {len(ids)} weapons")
            out.extend(rows)
    out.insert(8, f"{count} families with deviations.")
    out.insert(9, "")
    shared = sorted(boss & player)
    out += ["", "## Weapons that bosses and player vehicles share", "",
            "Prompt 34 L2 changes boss weapons only. Where a boss carries a player's weapon and the boss table changes",
            "its numbers, L2 gives the boss its own copy. These weapons are shared:", "",
            ", ".join(f"`{w}`" for w in shared), ""]
    return "\n".join(out)


if __name__ == "__main__":
    main()
