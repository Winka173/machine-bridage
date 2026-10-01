"""Prompt 26, pass 2 (C and D): the bosses' sizes, Ixion's and Gungnir's new designs, Leviathan's 406 mm (DECISIONS 26CD).

Run from this folder: `python p26_cd.py` (dry run) or `python p26_cd.py --write`; a second run changes nothing. No measurement
is made. Sizes are data only: a boss is drawn at its model's native length x its scale, and "size" (a main or standalone boss) or
"variant.size" (a mini made from a main) is what BossTemplates.Resize multiplies the scale, hit radius, parts and mounts by, so the
sizes below are solved here from each model's native length (glb_bounds) and written as those numbers. No Blender rebuild.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import glb_bounds as G  # noqa: E402
import p26_ab as P  # noqa: E402
from jsonc_edit import Doc, fmt  # noqa: E402

# Target drawn lengths in metres (the prompt's C.2 table; Fenrir, Locust and the like keep what they have).
MAIN = {"fortress_bastion": 40, "behemoth": 26, "mobile_fortress": 32, "drone_mothership": 55, "moloch": 40, "nuke_train": 70,
        "kronos": 60, "typhon": 70, "command_airship": 80, "daedalus": 60, "silver_bug": 90}
# A mini made from a main takes its parent's new scale times its own "variant.size"; a standalone one has its "size".
MINI = {"bastion_mk0": 24, "behemoth_mk0": 17, "behemoth_mk2": 18, "icarus_mk0": 36, "argus": 35,
        "behemoth_inferno": 17, "behemoth_tempest": 17, "supreme_command": 16, "caspian": 36, "rail_supergun": 45}
# Mini bosses the prompt says to keep as they are: the variants of a main that grows are held at their present length.
KEEP = ["fenrir", "locust", "stymphalos", "cerberus", "hydra"]
# Batch D mains (variants of a main): Monster is a ground boss (about 40 m), the others keep their ratio to the parent.
BATCH_D_MAIN = {"monster": 42}


def native(model):
    return G.bounds(model)[2]


def main():
    doc = Doc(P.PATH)
    data = doc.data()
    built = P.expand(data)
    raw = {v["id"]: v for v in data["vehicles"]}

    def model_of(i):
        return built[i].get("model") or (model_of(raw[i]["variantOf"]) if "variantOf" in raw[i] else i)

    def vsize(i):
        return (raw[i].get("variant") or {}).get("size", 0.7)

    def final(i, table):
        """The drawn scale of boss i under the sizes in `table` (id -> size)."""
        r = raw[i]
        if "variantOf" in r:
            return final(r["variantOf"], table) * table.get(i, vsize(i))
        return built[i].get("scale", 1.0) * table.get(i, r.get("size", 1.0))

    old = {}
    report = []
    for i in list(MAIN) + list(MINI) + KEEP + list(BATCH_D_MAIN) + ["garuda", "hyperion"]:
        old[i] = native(model_of(i)) * final(i, {})
    sizes = {}
    # 1. standalone entries (mains and standalone minis)
    for i, L in {**MAIN, **{k: v for k, v in MINI.items() if "variantOf" not in raw[k]}}.items():
        sizes[i] = round(L / (native(model_of(i)) * built[i].get("scale", 1.0)), 4)
    # 2. variants: the length wanted over the parent's new scale
    wanted = {**{k: v for k, v in MINI.items() if "variantOf" in raw[k]}, **BATCH_D_MAIN}
    for i in KEEP:
        wanted[i] = old[i]
    for i in ("garuda", "hyperion"):
        wanted[i] = old[i] * final(raw[i]["variantOf"], sizes) / final(raw[i]["variantOf"], {})
    for i, L in wanted.items():
        sizes[i] = round(L / (native(model_of(i)) * final(raw[i]["variantOf"], sizes)), 4)
    for i in sizes:
        report.append(f"{i:20s} {old[i]:6.1f} -> {native(model_of(i)) * final(i, sizes):6.1f} m   size {sizes[i]}")

    for i, s in sizes.items():
        if "variantOf" in raw[i]:
            doc.edit("vehicles", i, lambda e, s=s: e.set_sub("variant", "size", s))
        else:
            doc.edit("vehicles", i, lambda e, s=s: e.set("size", s))

    # ---- D.1 Ixion: the armoured BelAZ-75710 mine truck, on the railgun truck's model as a stand-in
    ixion_model = "railgun_truck"
    ixion_weapons = [
        ("p26_ixion_125", {"inherits": "gun_120mm", "weaponFamily": "", "real": "2A46 125 mm (turret, AP)", "size": 125, "damage": 780,
                           "cooldown": 2, "pen": 4, "splash": 0, "range": 38}),
        ("p26_ixion_mg", {"inherits": "boss_hmg", "weaponFamily": "", "damage": 15}),
    ]
    parts = [
        {"id": "wheel_l", "kind": "wheel", "hp": 0.07, "armour": 3, "wreck": "wreck_engine", "at": [-5.4, 8.5, 1.8], "radius": 2.8,
         "speed": 0.6, "turn": 0.5, "radio": "radio.part.wheel"},
        {"id": "wheel_r", "kind": "wheel", "hp": 0.07, "armour": 3, "wreck": "wreck_engine", "at": [5.4, 8.5, 1.8], "radius": 2.8,
         "speed": 0.6, "turn": 0.5, "radio": "radio.part.wheel"},
        {"id": "rear_l1", "kind": "reartyre", "hp": 0.035, "armour": 1, "wreck": "wreck_stump", "at": [-5.4, -3.0, 1.8], "radius": 2.6, "speed": 0.9, "turn": 0.9},
        {"id": "rear_r1", "kind": "reartyre", "hp": 0.035, "armour": 1, "wreck": "wreck_stump", "at": [5.4, -3.0, 1.8], "radius": 2.6, "speed": 0.9, "turn": 0.9},
        {"id": "rear_l2", "kind": "reartyre", "hp": 0.035, "armour": 1, "wreck": "wreck_stump", "at": [-5.4, -9.0, 1.8], "radius": 2.6, "speed": 0.9, "turn": 0.9},
        {"id": "rear_r2", "kind": "reartyre", "hp": 0.035, "armour": 1, "wreck": "wreck_stump", "at": [5.4, -9.0, 1.8], "radius": 2.6, "speed": 0.9, "turn": 0.9},
        {"id": "gun", "kind": "hulltower", "hp": 0.12, "armour": 3, "node": "Turret", "wreck": "wreck_turret", "at": [0, -1.5, 6.5], "radius": 3.2, "mounts": [0]},
        {"id": "cab", "kind": "cab", "hp": 0.08, "armour": 2, "wreck": "wreck_stump", "at": [-3.6, 9.5, 5.0], "radius": 3.0, "mounts": [1, 2]},
    ]

    def ixion(e):
        e.set("model", ixion_model)
        e.set("modelSize", [26, 12, 10])
        e.set("tint", [0.86, 0.66, 0.2])
        e.set("armour", [4, 3, 2, 2])
        e.set("weaponDamage", 1)
        e.set("speed", 7)
        e.set("turnRate", 6)
        e.set("turretTurnRate", 90)
        e.set("radius", 11)
        e.set("length", 26)
        e.set("width", 12)
        e.set("weapon", "p26_ixion_125")
        e.set("secondary", [{"weapon": "p26_ixion_mg", "slot": "mg", "aim": "Free"}, {"weapon": "p26_ixion_mg", "slot": "mg", "aim": "Free"}])
        e.set("mountWeapons", {"0": "p26_ixion_125", "1": "p26_ixion_mg", "2": "p26_ixion_mg"})
        e.set("bigAttack", "ixion_crush_charge")
        e.set("bigAttackScale", {"damage": 1, "cooldown": 1, "warn": 0})
        e.set("mines", {"interval": 8, "max": 6, "damage": 380, "radius": 4, "tier": "Large", "trigger": 2.2, "life": 20, "turnStrip": 15})
        e.set("parts", parts)

    doc.edit("vehicles", "ixion", ixion)
    report.append(f"ixion: {ixion_model} fitted to 26 m (native {native(ixion_model):.1f} m)")

    # ---- D.2 Gungnir: the rail electromagnetic supergun
    gungnir_weapon = ("p26_gungnir_emrg", {"inherits": "supergun_800", "weaponFamily": "", "real": "EMRG electromagnetic railgun (rail train, scaled up)",
                                           "size": 250, "projectileModel": "rail_slug", "projectileScale": 3.2, "damage": 2000, "cooldown": 25,
                                           "splash": 12, "edge": 20, "pen": 4, "range": 400, "minRange": 30, "projectileSpeed": 700})

    def gungnir(e):
        e.set("bombard", {"warn": 3, "scatter": 3, "blindScatter": 2.5, "first": 10, "weapon": "p26_gungnir_emrg", "warning": "supergun_shell",
                          "pierceMax": 5, "pierceDamage": 1000})
    doc.edit("vehicles", "rail_supergun", gungnir)

    # ---- the weapons
    for wid, fields in ixion_weapons + [gungnir_weapon]:
        line = "{ " + ", ".join(f'"{k}": {fmt(v)}' for k, v in {"id": wid, **fields}.items()) + " }"
        if wid in [w["id"] for w in doc.data()["weapons"]]:
            doc.edit("weapons", wid, lambda e, fields=fields: [e.set(k, v) for k, v in fields.items()])
        else:
            doc.insert_after("weapons", "p26_leviathan_lev406", line)
    nl = "\r\n" if "\r\n" in doc.text else "\n"
    # the charge, Ixion's secondary weapon (prompt 26 D.1): 2 s line warning, about every 10 s, a 1 s stun
    charge = ('{ "id": "ixion_crush_charge", "icon": "barrage", "warn": 2, "cooldown": 10, "first": 6, "aim": "group", "reach": 90, "target": "packed", '
              '"strikes": [{ "shape": "charge", "parts": ["wheel_l", "wheel_r"], "cut": 0, "length": 60, "width": 10, "duration": 4, "damage": 900, '
              '"type": "Kinetic", "pen": 4, "stun": 1 }] },')
    if '"id": "ixion_crush_charge"' not in doc.text:
        anchor = '    { "id": "bastion_420_shell"'
        assert anchor in doc.text
        doc.text = doc.text.replace(anchor, "    // Prompt 26 D.1: Ixion's crush charge is its secondary weapon (the mine truck's ram), not a super weapon: a 2 s warned line, about every 10 s." + nl
                                    + "    " + charge + nl + anchor, 1)
    # the HE round the 125 mm loads against a cluster (the AP shell is its own)
    he = ('      { "id": "p26_ixion_125_he", "roundOf": "p26_ixion_125", "inherits": "p26_ixion_125", "weaponFamily": "", "round": "he", "for": ["cluster"], '
          '"real": "2A46 125 mm HE-FRAG", "damageType": "HighExplosive", "pen": 3, "damage": 780, "splash": 5, "edge": 10, "form": "HeShell", '
          '"piercing": false, "targets": "Ground", "impactTier": "Huge" },')
    if '"id": "p26_ixion_125_he"' not in doc.text:
        anchor = '      { "id": "borer_cannon_he"'
        assert anchor in doc.text
        doc.text = doc.text.replace(anchor, he + nl + anchor, 1)

    # ---- D.4 Leviathan: 406 mm (Iowa's Mk 7), the calibre's name where it is written
    for old_s, new_s in [
        ('"real": "Type 94 460 mm/45 (triple)", "family": "howitzer", "size": 460', '"real": "Mk 7 406 mm/50 (Iowa, triple)", "family": "howitzer", "size": 406'),
        ('"real": "Type 94 460 mm/45 guided (triple)"', '"real": "Mk 7 406 mm/50 guided (Iowa, triple)"'),
        ('"real": "Type 94 406 mm/50 (triple)"', '"real": "Mk 7 406 mm/50 (Iowa, triple)"'),
        ("three triple 460 mm turrets now (the calibre scale's 460 mm, 950:", "three triple 406 mm turrets now (the calibre scale's 406 mm, 950:"),
        ("lays its three triple 460 mm turrets' salvos", "lays its three triple 406 mm turrets' salvos"),
        ("Kessler's Leviathan (Yamato lineage), the", "Kessler's Leviathan (an Iowa-class battleship, 1980s refit), the"),
    ]:
        doc.text = doc.text.replace(old_s, new_s)
    print("\n".join(report))
    if "--write" in sys.argv:
        print("file changed" if doc.save() else "file unchanged")
    else:
        print("dry run (--write saves)")


if __name__ == "__main__":
    main()
