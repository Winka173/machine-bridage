"""Prompt 34 L9: the six validators in one run (DECISIONS "Prompt 34 L8 / L9").

    python Tools/balance/p34_validate.py            # check (exit 1 on a problem)
    python Tools/balance/p34_validate.py --write    # also write the cruise warnings' rings onto their real area (a rerun changes nothing)

1. Families: within a family (variants aside) every boss weapon fires the same round (damage, speed, core, edge, type),
   in every boss; every variant used is listed with its reason (`p34_boss_families.validate` and the table).
2. Warnings: every T4+ boss round warns at least the escape formula (`p34_warnings.check`; Gungnir the named exception).
3. Rings: what the warning shows is the damage area. A weapon's rings are drawn from its own core and edge
   (`WeaponDef.WarnRadius`, tested in C#); here, the ships' laid salvos and cruise missiles, whose warning is a separate
   support entry: its `radius` must be the blast's edge and its `blast` the core (the Sim's cruise blast is
   `ExplosionDef.TwoLayer`: core `radius`, edge min(20, 2 x core)).
4. Muzzles: every vehicle with a gun that fires its barrels together (SIMULTANEOUS, barrels > 1) has a Muzzle_b<k> for
   each barrel on its model (`p34_barrels.MUZZLES`, checked in the GLBs), or is a listed exception.
5. Previews: every vehicle maps to one preview domain (ground / water / rail / air), the rail and sea bosses to theirs (a
   mirror of `PreviewSettings.Of`; `Prompt34PreviewTests` is the authority, it sees the whole catalog).
6. Wrecks: no gameplay collider: the wreck code adds no Collider, and no model is imported with colliders.
"""
from __future__ import annotations

import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import p34_families as F  # noqa: E402
import p34_boss_families as B  # noqa: E402
import p34_warnings as W  # noqa: E402
import p34_barrels as R  # noqa: E402
from jsonc_edit import Doc, Entry  # noqa: E402

MAX_EDGE = 20.0
SCRIPTS = os.path.join(F.ROOT, "Assets", "MachineBrigade", "Scripts")
MODELS = os.path.join(F.ROOT, "Assets", "MachineBrigade", "Resources", "Models")


# ---------------------------------------------------------------------------------------------------- 1. families

def families(data):
    problems = list(B.validate(data))
    ws = F.Weapons(data)
    assign = F.assignment(ws)
    table = {t["id"]: t for t in data.get("weaponFamilyTable", [])}
    for wid, (fam, var, _) in assign.items():
        if fam not in table:
            problems.append(f"{wid}: family {fam} is not in weaponFamilyTable")
            continue
        if var and not (table[fam].get("variants") or {}).get(var):
            problems.append(f"{wid}: variant {fam}/{var} has no reason in the table")
    return problems


# ---------------------------------------------------------------------------------------------------- 3. rings

def edge_of(core, edge=None):
    if edge:
        return float(edge)
    e = min(MAX_EDGE, 2.0 * core)
    return e if e > core else core


def ring_users(data):
    """(boss, block, core, edge, warning support) for every laid salvo and cruise missile with a warning entry."""
    built, _ = B.boss_users(data)
    out = []
    for bid, b in sorted(built.items()):
        s = b.get("salvo")
        if isinstance(s, dict) and s.get("warning"):
            core = float(s.get("radius", 7))
            out.append((bid, "salvo", core, edge_of(core, s.get("edge")), s["warning"]))
        c = b.get("cruise")
        if isinstance(c, dict) and c.get("warning"):
            core = float(c.get("radius", 16))
            out.append((bid, "cruise", core, edge_of(core), c["warning"]))
    return out


def rings(data):
    supports = {s["id"]: s for s in data.get("supports", [])}
    problems = []
    for bid, block, core, edge, sup in ring_users(data):
        s = supports.get(sup)
        if s is None:
            problems.append(f"{bid}.{block}: warning '{sup}' is no support")
            continue
        if abs(float(s.get("radius", 0)) - edge) > 0.01 or abs(float(s.get("blast", 0)) - core) > 0.01:
            problems.append(f"{bid}.{block}: the ring shows {s.get('radius')} / {s.get('blast')} m ({sup}), the blast is edge {edge:g} / core {core:g} m")
    return problems


def write_rings(doc: Doc):
    """Each warning support gets the area of the bosses that use it; a boss whose blast differs gets its own copy."""
    data = doc.data()
    supports = {s["id"]: s for s in data.get("supports", [])}
    by_sup = {}
    for bid, block, core, edge, sup in ring_users(data):
        by_sup.setdefault(sup, []).append((bid, block, core, edge))
    changed = 0
    for sup, users in by_sup.items():
        areas = sorted({(core, edge) for _, _, core, edge in users}, key=lambda a: -sum(1 for u in users if (u[2], u[3]) == a))
        main = areas[0]
        s = supports[sup]
        if abs(float(s.get("radius", 0)) - main[1]) > 0.01 or abs(float(s.get("blast", 0)) - main[0]) > 0.01:
            def fs(e: Entry, a=main):
                e.set("radius", a[1], after="kind")
                e.set("blast", a[0], after="radius")
            if doc.edit("supports", sup, fs):
                changed += 1
        for core, edge in areas[1:]:
            new_id = f"{sup}_{core:g}".replace(".", "_")
            if new_id not in supports:
                e = doc.entry("supports", sup)
                e.set("id", new_id)
                e.set("radius", edge, after="kind")
                e.set("blast", core, after="radius")
                doc.insert_after("supports", sup, e.text.strip())
                supports[new_id] = dict(s, id=new_id, radius=edge, blast=core)
                changed += 1
            for bid, block, c2, e2 in users:
                if (c2, e2) != (core, edge):
                    continue

                def fv(ent: Entry, block=block, new_id=new_id):
                    sub = ent.sub(block)
                    sub.set("warning", new_id, after="weapon")
                    ent.set_raw(block, sub.text)
                try:
                    if doc.edit("vehicles", bid, fv):
                        changed += 1
                except KeyError:
                    print(f"note: {bid}.{block} inherits its warning; give it '{new_id}' by hand")
    return changed


# ---------------------------------------------------------------------------------------------------- 4. muzzles

def mounts_weapons(v):
    ws = []
    if v.get("weapon"):
        ws.append(v["weapon"])
    for s in v.get("secondary", []) or []:
        if isinstance(s, dict) and s.get("weapon"):
            ws.append(s["weapon"])
    for w in (v.get("mountWeapons") or {}).values():
        if w:
            ws.append(w)
    return ws


def model_of(vehicles, v):
    """The model a vehicle draws: its own, else its parent's (a boss variant is its parent scaled), else a tower branch's base."""
    seen = set()
    while v is not None and v["id"] not in seen:
        seen.add(v["id"])
        if v.get("model"):
            return v["model"]
        parent = v.get("variantOf") or v.get("branchOf") or (v["id"].split(".")[0] if "." in v["id"] else None)
        if not parent or parent not in vehicles:
            return parent or v["id"]
        v = vehicles[parent]
    return v["id"] if v else ""


def muzzles(data):
    problems = list(R.check_muzzles())
    ws = F.Weapons(data)
    built, _ = B.boss_users(data)
    vehicles = {v["id"]: v for v in data["vehicles"]}
    vehicles.update(built)
    for vid, v in sorted(vehicles.items()):
        together = [w for w in mounts_weapons(v) if w in ws.raw and ws.resolve(w).get("salvoMode") == "SIMULTANEOUS"
                    and int(ws.resolve(w).get("barrels", 1)) > 1]
        if not together:
            continue
        model = model_of(vehicles, v)
        if model in R.MUZZLES or model in R.KNOWN_MISSING or vid in R.KNOWN_MISSING:
            continue
        if not os.path.exists(os.path.join(MODELS, model + ".glb")):
            problems.append(f"{vid}: fires {together[0]} barrels together, its model '{model}' is not built")
            continue
        problems.append(f"{vid}: fires {', '.join(sorted(set(together)))} barrels together; model '{model}' is not in p34_barrels.MUZZLES")
    return problems


# ---------------------------------------------------------------------------------------------------- 5. previews

AMPHIBIOUS = {"light_tank", "hover_gunboat", "landing_hovercraft"}
RAIL_UNITS = {"armored_train", "nuke_train", "rail_supergun"}
FRAMES = None


def domain(v, frames):
    """A mirror of PreviewSettings.Of, then its domain."""
    vid = v["id"]
    move = (frames.get(v.get("frame")) or {}).get("move", "")
    if v.get("flying"):
        return "air"
    if move.lower() == "rail" or v.get("route") == "rail" or vid in RAIL_UNITS or "train" in vid:
        return "rail"
    if v.get("naval") or move.lower() in ("ship", "submarine"):
        return "water"
    if v.get("frame") == "hovercraft" or vid in AMPHIBIOUS or "hover" in vid or "amphib" in vid or "boat" in vid:
        return "water"
    return "ground"


def previews(data):
    built, _ = B.boss_users(data)
    frames = {f["id"]: f for f in data.get("bossFrames", [])} if isinstance(data.get("bossFrames"), list) else dict(data.get("bossFrames") or {})
    vehicles = {v["id"]: v for v in data["vehicles"]}
    vehicles.update(built)
    want = {"armored_train": "rail", "nuke_train": "rail", "rail_supergun": "rail", "leviathan": "water", "kraken": "water",
            "typhon": "water", "caspian": "water", "scylla": "water", "nyx": "water", "landing_hovercraft": "water",
            "mega_gunship": "air", "drone_mothership": "air", "command_airship": "air", "sky_fortress": "air",
            "silver_bug": "air", "main_battle_tank": "ground", "behemoth": "ground", "kronos": "ground"}
    problems = []
    counts = {}
    for vid, v in vehicles.items():
        d = domain(v, frames)
        counts[d] = counts.get(d, 0) + 1
        if vid in want and want[vid] != d:
            problems.append(f"{vid}: preview domain {d}, should be {want[vid]}")
    for d in ("ground", "water", "rail", "air"):
        if not counts.get(d):
            problems.append(f"no unit has a {d} preview")
    return problems, counts


# ---------------------------------------------------------------------------------------------------- 6. wrecks

WRECK_CODE = ["Game/Effects/Wreck*.cs", "Game/Effects/ShipSinking*.cs", "Game/Effects/ChunkThrower*.cs", "Game/Effects/FireSpots*.cs",
              "Game/Effects/EffectsDirector*.cs", "Game/Views/VehicleView*.cs"]


def wrecks():
    problems = []
    for pattern in WRECK_CODE:
        for path in glob.glob(os.path.join(SCRIPTS, pattern)):
            with open(path, encoding="utf-8") as fh:
                for n, line in enumerate(fh, 1):
                    code = line.split("//")[0]
                    if re.search(r"AddComponent\s*<\s*\w*Collider\w*\s*>|typeof\(\s*\w*Collider\s*\)|CreatePrimitive\(", code):
                        problems.append(f"{os.path.relpath(path, SCRIPTS)}:{n}: adds a collider (CreatePrimitive adds one too)")
    for meta in glob.glob(os.path.join(MODELS, "*.glb.meta")) + glob.glob(os.path.join(MODELS, "*.fbx.meta")):
        with open(meta, encoding="utf-8") as fh:
            text = fh.read()
        if re.search(r"^\s*addColliders:\s*1", text, re.M):
            problems.append(f"{os.path.basename(meta)}: imported with colliders")
    return problems


# ---------------------------------------------------------------------------------------------------- main

def main():
    doc = Doc(F.PATH)
    if "--write" in sys.argv:
        n = write_rings(doc)
        doc.save()
        print(f"{n} entries written")
        doc = Doc(F.PATH)
    data = doc.data()
    total = 0
    warn_problems, warn_notes = W.check(data)
    preview_problems, counts = previews(data)
    for name, problems in (("1 families", families(data)), ("2 warnings", warn_problems), ("3 rings", rings(data)),
                           ("4 muzzles", muzzles(data)), ("5 previews", preview_problems), ("6 wrecks", wrecks())):
        for p in problems:
            print(f"PROBLEM [{name}]: {p}")
        print(f"{name}: " + ("OK" if not problems else f"{len(problems)} problems"))
        total += len(problems)
    for n in warn_notes:
        print("note [2 warnings]:", n)
    print("note [5 previews]: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) + " (balance.json units; the C# test sees the whole roster)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
