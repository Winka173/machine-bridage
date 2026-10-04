"""MB_FINAL F3 (the owner's final bundle, VIEC_CHO_AGENT_FINAL section 6, "VFX/feel"): a static check that every weapon's
look grows in step with what it does. Reads balance.json only (no Unity, no run).

    python Tools/balance/f3_tier_feel.py            # writes Docs/checks/f3_tier_feel.md, exit 1 on an inversion

The T0-T5 tier (the firing look: flash, tongues, the hull's squat and recoil; the landing overlay) comes from the weapon's
family (`weaponFamilyTable`: calibre for guns, warhead for missiles, rockets and bombs; `TierFx.Looks` overrides a few in
the view). The blast's size is its `impactTier` (Small..Ultimate), its rings the real core and edge. The checks:

1. Tier by calibre / warhead: within guns (shell, bullet) a bigger calibre never has a lower tier; within missiles, rockets
   and bombs a heavier warhead (warheadKg, else size) never has a lower tier, except across kinds the table keeps apart.
2. In step with the hit: a weapon of a higher tier that both deals less damage a round (under 0.8 x) and reaches less (core
   under the other's) is listed (a stronger, wider hit drawn smaller). Re-run after a balance pass changes damage or splash.
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
    boss_ids, _, _ = F.users(data)
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
                         core=num(w.get("splash")), impact=w.get("impactTier"), boss=wid in boss_ids,
                         air=w.get("targets") == "Air"))
    by_calibre, in_step, bands = [], [], []
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
                in_step.append((a, b))
    for r in rows:
        if r["impact"] in BANDS and abs(BANDS[r["impact"]] - max(1, r["tier"])) > 1:
            bands.append(r)
    out = ["# MB_FINAL F3: weapon look against its hit (static, `python Tools/balance/f3_tier_feel.py`)", "",
           f"{len(rows)} weapons with a tier; {len(by_calibre)} tier/calibre inversions, {len(in_step)} hits drawn smaller than a "
           f"weaker one, {len(bands)} blast sizes two or more bands from the tier.", ""]
    out += ["## 1. Tier by calibre / warhead", "", "| weapon (tier, mm or kg) | lower-tier weapon it outweighs |", "|---|---|"]
    key = {"calibre": "calibre", "warhead": "charge"}
    out += [f"| {a['id']} (T{a['tier']}, {a[key[k]]:g}) | {b['id']} (T{b['tier']}, {b[key[k]]:g}) |" for a, b, k in by_calibre[:60]]
    out += ["", "## 2. In step with the hit", "", "| higher tier (dmg, core) | lower tier that hits harder and wider |", "|---|---|"]
    out += [f"| {a['id']} (T{a['tier']}, {a['damage']:g}, {a['core']:g} m) | {b['id']} (T{b['tier']}, {b['damage']:g}, {b['core']:g} m) |"
            for a, b in in_step[:60]]
    out += ["", "## 3. Blast size against tier", "", "| weapon | tier | impactTier |", "|---|---|---|"]
    out += [f"| {r['id']} | T{r['tier']} | {r['impact']} |" for r in bands[:80]]
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
    print(out[2])
    return 1 if by_calibre else 0


if __name__ == "__main__":
    sys.exit(main())
