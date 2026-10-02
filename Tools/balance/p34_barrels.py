"""Prompt 34 L4: barrels fired together (salvoMode SIMULTANEOUS) for the ships, the heavy turrets and the super tank
(DECISIONS "Prompt 34 L4").

    python Tools/balance/p34_barrels.py           # dry run
    python Tools/balance/p34_barrels.py --write   # save balance.json (a second run changes nothing)

A weapon with "barrels": N and "salvoMode": "SIMULTANEOUS" fires N rounds in the same tick each trigger pull, one from each
barrel (the view staggers the flashes 0.07 s a barrel); "burst" then counts volleys. A gun that fired its barrels as a
ripple (burst N, burstInterval apart) becomes burst 1 x N barrels. Its DPS is kept by a longer cooldown: the old salvo's
gaps, (N - 1) x burstInterval, are added to the cooldown, so its cycle stays the same. A second round of the gun inherits
the barrels; a round that goes one at a time (a guided shell) keeps one barrel.

The rule "a vehicle's DIFFERENT weapons never fire together" is unchanged: this is one weapon's barrels.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import p34_families as F  # noqa: E402
from jsonc_edit import Doc  # noqa: E402

# weapon -> (barrels, who carries it)
TARGETS = {
    "p26_leviathan_lev406": (3, "Leviathan, Kraken: the 406 mm triple turrets (laid: the salvo's three shells a turret)"),
    "p26_leviathan_sec_lev155": (3, "Leviathan, Kraken: the 155 mm/60 triple turrets"),
    "naval_130_twin": (2, "Scylla: the AK-130 twin"),
    "cruiser_203": (2, "the player's cruiser: the Mk 71 203 mm twin"),
    "gun_155_twin_fort": (2, "the heavy turret's 155 mm twin (the base line)"),
    "gun_155_twin_ap": (2, "the heavy turret (player)"),
    "gun_155_twin_coastlr": (2, "the heavy turret's coastal branch"),
    "bastion_gun": (2, "the headquarters and the spawn bastion (fortress): the 2A83 152 mm twin"),
    "gun_140_twin": (2, "the super tank (titan_tank): the NPzK 140 mm twin"),
}


def plan(data):
    ws = F.Weapons(data)
    edits, notes = {}, []
    for wid, (n, who) in TARGETS.items():
        w = ws.resolve(wid)
        burst, bi, cd = int(w.get("burst", 1)), float(w.get("burstInterval", 0.1)), float(w.get("cooldown", 1))
        if w.get("salvoMode") == "SIMULTANEOUS":
            continue  # already done (a rerun)
        if w.get("clip", 0):
            notes.append(f"{wid}: a magazine (clip): left as it is")
            continue
        f = {"barrels": n, "salvoMode": "SIMULTANEOUS"}
        if burst == n:
            f["burst"] = 1
            f["cooldown"] = round(cd + (n - 1) * bi, 4)
            notes.append(f"{wid}: burst {burst} x {bi} s + {cd} s -> {n} barrels together, cooldown {f['cooldown']} s (cycle kept) - {who}")
        elif burst == 1:
            notes.append(f"{wid}: {n} barrels together, one round each as before ({who})")
            if not w.get("laid"):
                # One round a pull was one barrel; N barrels a pull fire N rounds: the cycle grows N times to keep the DPS.
                f["cooldown"] = round(cd * n, 4)
        else:
            notes.append(f"{wid}: burst {burst} with {n} barrels: left as it is (check by hand)")
            continue
        edits[wid] = f
    # Second rounds of these guns that go one at a time keep one barrel.
    for rid, r in ws.rounds.items():
        gun = r.get("roundOf")
        if gun in TARGETS and (r.get("round") == "guided" or r.get("burst") == 1 or r.get("oneAtATime")):
            if ws.resolve(rid).get("barrels", 1) != 1 or rid not in [k for k in edits]:
                edits[rid] = {"barrels": 1, "salvoMode": "RIPPLE"}
                notes.append(f"{rid}: one at a time (a {r.get('round')} round): one barrel")
    return ws, edits, notes


# Prompt 34 L9 rule 4 (here for L4): every barrel of a simultaneous gun has its Muzzle_b<k> on the model. Model -> muzzles
# (as exported) of the guns that fire together, and the barrels each must have; Kraken's mounts are bare launch cells.
MUZZLES = {
    "leviathan": {"Muzzle_gun": 3, "Muzzle_gun.001": 3, "Muzzle_gun.002": 3, "Muzzle_gun.003": 3, "Muzzle_gun.004": 3},
    "sea_cruiser": {"Muzzle_gun": 2, "Muzzle_gun.001": 2},
    "heavy_turret": {"Muzzle_main": 2},
    "headquarters": {"Muzzle_main": 2},
    "titan_tank": {"Muzzle_main": 2},
    # Full fix L3 (DECISIONS "Sửa lỗi tổng hợp L3", Tools/blender/mb_fix_barrels.py): the bosses' twin guns.
    "behemoth": {"Muzzle_main": 2, "Muzzle_gun": 2, "Muzzle_gun.001": 2, "Muzzle_gun.002": 2},
    "cerberus": {"Muzzle_main": 2},
    "moloch": {"Muzzle_main": 2, "Muzzle_gun": 2, "Muzzle_gun.001": 2, "Muzzle_gun.002": 2},
    "typhon": {"Muzzle_gun": 2},
    "hydra_sub": {"Muzzle_gun": 2, "Muzzle_missile": 2},
    "daedalus": {"Muzzle_gun": 2, "Muzzle_gun.001": 2},
    "monster": {"Muzzle_gun": 2, "Muzzle_gun.001": 2},
    "fortress_bastion": {"Muzzle_gun": 2, "Muzzle_gun.001": 2},
}
KNOWN_MISSING = {"kraken": "its 406 mm and 155 mm mounts are launch cells and rocket boxes with no barrels: one muzzle each"}


def check_muzzles():
    import json
    import re
    import struct
    models = os.path.join(F.ROOT, "Assets", "MachineBrigade", "Resources", "Models")
    problems = []
    for model, want in MUZZLES.items():
        with open(os.path.join(models, model + ".glb"), "rb") as fh:
            b = fh.read()
        n = struct.unpack_from("<I", b, 12)[0]
        nodes = json.loads(b[20:20 + n])["nodes"]
        by_name = {nd.get("name"): nd for nd in nodes}
        for muzzle, barrels in want.items():
            nd = by_name.get(muzzle)
            if nd is None:
                problems.append(f"{model}: no {muzzle}")
                continue
            kids = [nodes[c].get("name", "") for c in nd.get("children", [])]
            got = [k for k in kids if re.match(r"^Muzzle_b\d+_", k)]
            if len(got) < barrels:
                problems.append(f"{model}.{muzzle}: {len(got)} barrel muzzles of {barrels}")
    return problems


def main():
    doc = Doc(F.PATH)
    data = doc.data()
    ws, edits, notes = plan(data)
    for n in notes:
        print(n)
    changed = 0
    for wid, f in edits.items():
        cur = ws.resolve(wid)
        f = {k: v for k, v in f.items() if cur.get(k) != v}
        if f and F.set_on(doc, wid, f, ws.rounds):
            changed += 1
    print(f"{changed} lines changed")
    problems = check_muzzles()
    for p in problems:
        print("MUZZLES:", p)
    for m, why in KNOWN_MISSING.items():
        print(f"note: {m}: {why}")
    print("muzzles: OK" if not problems else f"muzzles: {len(problems)} problems")
    if "--write" in sys.argv:
        doc.save()
        print("written")


if __name__ == "__main__":
    main()
