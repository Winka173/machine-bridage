"""Prompt 30 L6: the neutral sites of the battlefields (sheet "Trung lập", the V1 rows).

    python Tools/maps/neutrals.py            # every battlefield's Conquest, Sandbox and Siege version
    python Tools/maps/neutrals.py ashfield   # one battlefield

Works on the generated map files (run it again after Tools/maps/build_maps.py): it adds a "neutrals" field (kind, x, z)
and the sites' buildings to "props" (marked "neutral": 1, so a second run replaces them). Each Conquest version (and its
Sandbox twin, the same layout) gets two kinds, each as a pair mirrored through the middle of the map, as its camps
are, so either side has its own of each at the same distance; the building (radar dome, garage, ammo dump; the
abandoned AA site has none until it is taken) stands 6 m behind the spot, on its side. The Siege version gets an AA
site and an ammo depot on the attacker's half (an asymmetric mode). Spots keep clear of props, hardpoints, units,
objectives and camps and stay inside the outline. Which kinds a mode switches on: balance.json "neutrals.modes".
Read-only besides those two fields; it prints what it could not place.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MAPS = os.path.join(ROOT, "Assets", "MachineBrigade", "Resources", "Data", "maps")
BALANCE = os.path.join(ROOT, "Assets", "MachineBrigade", "Resources", "Data", "balance.json")

R2 = math.sqrt(0.5)
PAIRS = [("radar", "ammo_depot"), ("workshop", "aa_site"), ("radar", "workshop"), ("ammo_depot", "aa_site")]
BUILDING = {"radar": "radar_dome", "workshop": "garage", "ammo_depot": "ammo_dump", "aa_site": None}
SITE_RADIUS = 9.0
# Candidate spots on a side's half, in a fixed order: nearest first to the preferred place (about 60 m from the middle
# along the camps' axis, 45 m off it), so the search is deterministic.
GRID = sorted(((a, c) for a in range(-96, -27, 3) for c in range(0, 100, 3)), key=lambda ac: (abs(ac[0] + 60) + abs(ac[1] - 45), ac))
BATTLEFIELDS = ["ashfield", "borderbridge", "capital", "coralisles", "dunebreak", "emberridge", "foundry", "frostpeak",
                "greenvale", "hydrodam", "ironport", "junglepass", "landingbeach", "launchsite", "lighthousebay",
                "metrocity", "openpit", "orbitalgate", "redrock", "rustyard", "saltflat", "skyhold", "swamp",
                "veyra_old_quarter", "whiteout"]


def strip(text: str) -> str:
    return re.sub(r"^\s*//.*$", "", text, flags=re.M)


def prop_sizes():
    sys.path.insert(0, os.path.join(ROOT, "Tools", "ai"))
    import export_applied_xlsx as E  # noqa: E402
    # Props that do not block (trees, grass, decals) do not keep a site away.
    return {p["id"]: (p["width"], p["depth"], p.get("blocks", False)) for p in E.balance()["props"]}


def inside(poly, x, z):
    hit = False
    for i in range(len(poly)):
        (x0, z0), (x1, z1) = poly[i], poly[(i + 1) % len(poly)]
        if (z0 > z) != (z1 > z) and x < x0 + (z - z0) * (x1 - x0) / (z1 - z0):
            hit = not hit
    return hit


class Field:
    """What a map's sites must keep clear of."""

    def __init__(self, data, sizes):
        self.half = data["size"] / 2
        flat = data.get("boundary") or []
        self.poly = list(zip(flat[0::2], flat[1::2]))
        self.rects = []
        for p in data["props"]:
            if p.get("neutral"):
                continue
            w, d, blocks = sizes.get(p["def"], (4.0, 4.0, True))
            if not blocks:
                continue
            if p.get("rot") in (90, 270):
                w, d = d, w
            self.rects.append((p["x"] - w / 2, p["z"] - d / 2, p["x"] + w / 2, p["z"] + d / 2))
        self.spots = [(u["x"], u["z"], 4.0) for u in data.get("units", [])]
        for base in data.get("bases", []):
            self.spots += [(s["x"], s["z"], 5.0) for s in base.get("slots", [])]
            hq = base.get("hq")
            if hq:
                self.spots.append((hq["x"], hq["z"], 9.0))
        fort = data.get("fortress")
        if fort:
            self.spots += [(s["x"], s["z"], 5.0) for s in fort.get("slots", [])]
        self.points = [(p["x"], p["z"], p["radius"]) for p in data.get("points", [])]
        self.teams = [(t["x"], t["z"]) for t in data["teams"]]
        self.sizes = sizes

    def open(self, x, z):
        if abs(x) > self.half - 14 or abs(z) > self.half - 14 or (self.poly and not inside(self.poly, x, z)):
            return False
        for (a0, b0, a1, b1) in self.rects:
            cx, cz = min(max(x, a0), a1), min(max(z, b0), b1)
            if math.hypot(cx - x, cz - z) < SITE_RADIUS:
                return False
        for (sx, sz, r) in self.spots:
            if math.hypot(sx - x, sz - z) < SITE_RADIUS + r:
                return False
        for (px, pz, r) in self.points:
            if math.hypot(px - x, pz - z) < r + 10:
                return False
        return all(math.hypot(tx - x, tz - z) >= 40 for tx, tz in self.teams)

    def fits(self, def_id, x, z):
        w, d, _ = self.sizes.get(def_id, (6.0, 6.0, True))
        x0, z0, x1, z1 = x - w / 2 - 0.5, z - d / 2 - 0.5, x + w / 2 + 0.5, z + d / 2 + 0.5
        if any(x0 < a1 and x1 > a0 and z0 < b1 and z1 > b0 for (a0, b0, a1, b1) in self.rects):
            return False
        return all(math.hypot(sx - x, sz - z) >= r + max(w, d) / 2 for sx, sz, r in self.spots)

    def take(self, def_id, x, z):
        w, d, _ = self.sizes.get(def_id, (6.0, 6.0, True))
        self.rects.append((x - w / 2, z - d / 2, x + w / 2, z + d / 2))


def spot(along, across):
    return R2 * along + R2 * across, R2 * along - R2 * across


def conquest_sites(field, index):
    sites, props, missing = [], [], []
    for k, kind in enumerate(PAIRS[index % len(PAIRS)]):
        sign = 1 if k == 0 else -1
        found = None
        for along, across in GRID:
            x, z = spot(along, sign * across)
            if not (field.open(x, z) and field.open(-x, -z)):
                continue
            b = BUILDING[kind]
            bx, bz = x - 6 * R2, z - 6 * R2
            if b and not (field.fits(b, bx, bz) and field.fits(b, -bx, -bz)):
                continue
            found = (x, z, bx, bz)
            break
        if not found:
            missing.append(kind)
            continue
        x, z, bx, bz = found
        for sx, sz, px, pz in ((x, z, bx, bz), (-x, -z, -bx, -bz)):
            sites.append({"kind": kind, "x": round(sx, 2), "z": round(sz, 2)})
            if BUILDING[kind]:
                field.take(BUILDING[kind], px, pz)
                props.append({"def": BUILDING[kind], "x": round(px, 2), "z": round(pz, 2), "neutral": 1})
            # The spot itself stays clear of the next kind's.
            field.spots.append((sx, sz, SITE_RADIUS))
    return sites, props, missing


def siege_sites(field):
    sites, props, missing = [], [], []
    for kind, sign in (("aa_site", 1), ("ammo_depot", -1)):
        found = None
        for along, across in GRID:
            x, z = spot(along + 15, sign * across)
            b = BUILDING[kind]
            bx, bz = x - 6 * R2, z - 6 * R2
            if field.open(x, z) and (not b or field.fits(b, bx, bz)):
                found = (x, z, bx, bz)
                break
        if not found:
            missing.append(kind)
            continue
        x, z, bx, bz = found
        sites.append({"kind": kind, "x": round(x, 2), "z": round(z, 2)})
        if BUILDING[kind]:
            field.take(BUILDING[kind], bx, bz)
            props.append({"def": BUILDING[kind], "x": round(bx, 2), "z": round(bz, 2), "neutral": 1})
        field.spots.append((x, z, SITE_RADIUS))
    return sites, props, missing


def rewrite(path, sites, props):
    """Puts "neutrals" before "roads" and the buildings at the end of "props" (earlier ones replaced)."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    lines = [l for l in lines if '"neutral": 1' not in l and not l.startswith('  "neutrals":')]
    # Drop the blank line a removed "neutrals" field left.
    out = []
    for l in lines:
        if out and l == "" and out[-1] == "":
            continue
        out.append(l)
    lines = out
    start = lines.index('  "props": [')
    end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("  ]"))
    if props:
        if not lines[end - 1].endswith(","):
            lines[end - 1] += ","
        new = ["    " + json.dumps(p) for p in props]
        new = [l + "," for l in new[:-1]] + [new[-1]]
        lines[end:end] = new
    roads = lines.index('  "roads": [')
    lines[roads:roads] = [f'  "neutrals": {json.dumps(sites)},', ""]
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def main(only=()):
    sizes = prop_sizes()
    report = []
    for i, name in enumerate(BATTLEFIELDS):
        if only and name not in only:
            continue
        cpath = os.path.join(MAPS, f"{name}_conquest.json")
        with open(cpath, encoding="utf-8") as f:
            data = json.loads(strip(f.read()))
        field = Field(data, sizes)
        sites, props, missing = conquest_sites(field, i)
        rewrite(cpath, sites, props)
        spath = os.path.join(MAPS, f"{name}_sandbox.json")
        if os.path.exists(spath):
            rewrite(spath, sites, props)
        report.append((name, "conquest+sandbox", sorted({s["kind"] for s in sites}), missing))
        gpath = os.path.join(MAPS, f"{name}_siege.json")
        if os.path.exists(gpath):
            with open(gpath, encoding="utf-8") as f:
                g = json.loads(strip(f.read()))
            gs, gp, gm = siege_sites(Field(g, sizes))
            rewrite(gpath, gs, gp)
            report.append((name, "siege", sorted({s["kind"] for s in gs}), gm))
    for name, variant, kinds, missing in report:
        print(f"{name} {variant}: {', '.join(kinds) or '-'}" + (f"  (not placed: {', '.join(missing)})" if missing else ""))


if __name__ == "__main__":
    main(sys.argv[1:])
