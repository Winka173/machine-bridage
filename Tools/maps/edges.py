"""Prompt 33 L2: the map's edge types, its corners, the lines that run on out of it and the entry gates.

    python Tools/maps/edges.py            # every map file (_conquest, _sandbox, _siege, _long)
    python Tools/maps/edges.py --check    # only check, write nothing (exit 1 on a problem)
    python Tools/maps/edges.py ironport   # one battlefield's files

Works on the generated map files (run it after Tools/maps/build_maps.py, neutrals.py and transit.py). It writes two
fields, each on its own line before "boundary" (replacing an earlier run's), and trims "decor":

- "edges" {"band", "outer", "segments", "corners", "links"}:
  - segments: every side of the map's rectangle ("N" z max, "E" x max, "S", "W") cut into runs of one edgeType
    (LAND / SEA / RIVER / CLIFF / URBAN) with an optional edgeModifier (HARBOR / INDUSTRIAL / URBAN) and, on SEA, the
    shore that meets the land (BEACH / CLIFF / QUAY). "from"/"to" are along the side (x on N and S, z on E and W).
  - corners: where two edge types meet (along a side, or at the rectangle's corner): the prebuilt corner piece the view
    puts there ("piece", e.g. corner_land_sea, mouth_river_sea); never random ground.
  - links: where a road, a rail, a river, the coast, a sea lane or an air corridor meets the rectangle's edge, and the
    way it runs on out ("dirX", "dirZ" outward) for "outer" metres through the edge band and the outer band.
- "entryGates": the ingress contract's gates. Each has its gameplayEntryPosition ("x", "z", open ground in the play area
  joined to the battlefield), the way in ("inX", "inZ"), its side, its kind (road / edge / rail / sea) and the view-only
  approach: "visualIngressLength" (metres from the outer band's far edge to the gate) along "path" (x, z pairs from out
  there to the gate). The real vehicle exists only from the gate's tick; the stand-in on the path is the view's.
- decor (scenery beyond the outline): buildings, trees and other land scenery on the water of a SEA side are removed
  (the sea runs to the horizon: no houses, woods or ground there). Harbour scenery (bollards, cranes, piers) stays.

Classification (per 10 m bin of each side, the strip within STRIP m of the edge): water tiles (river_water) -> SEA on a
map with sea (SEA_MAPS), RIVER elsewhere; a cliff prop (cliff_a/_b, volcanic_cliff, mesa) -> CLIFF; an urban map ->
URBAN; else LAND. OVERRIDES puts the sea where the map's water lies beyond its square (Ironport's and Rust Yard's quays).
Runs shorter than MIN_RUN m join their neighbour (a river keeps its own).
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_access as ca  # noqa: E402
import transit  # noqa: E402

MAPS = transit.MAPS
VARIANTS = ["conquest", "sandbox", "siege", "long"]
BAND = 16.0          # the edge band's width (prompt 33 L1: 12-20 m; lane A tunes it per map in its dressing)
OUTER = 120.0        # how far the lines run on beyond the rectangle (the widest view: 101 m half width at 2.4:1, + 15 %)
STRIP = 14.0         # how deep a side's strip is for the classification
BIN = 10.0
MIN_RUN = 20.0
GATE_STEP = 30.0     # an edge gate every this many metres along a side one can drive in from
GATE_MERGE = 15.0    # an edge gate this near a road's gate is left out
EDGE_MARGIN = 7.0    # as SpawnPoints.EdgeMargin: a gate stands at least this far in from the rectangle's edge
GATE_DEPTH = 40.0    # and at most this far

SEA_MAPS = {"landingbeach", "lighthousebay", "coralisles", "ironport", "rustyard"}
URBAN_MAPS = {"capital", "foundry", "metrocity", "veyra_old_quarter"}
INDUSTRIAL_MAPS = {"foundry", "rustyard", "ironport", "launchsite", "orbitalgate", "openpit", "dunebreak"}
CLIFF_PROPS = {"cliff_a", "cliff_b", "volcanic_cliff", "mesa"}
HARBOUR_DECOR = {"dock_bollards", "gantry_crane", "pier", "fishing_boat", "container", "container_stack"}
# The sea beyond the square where the map has no water tiles of its own: the quays' far side (square files only).
OVERRIDES = {
    ("ironport", "square"): {"N": ("SEA", "HARBOR", "QUAY")},
    ("rustyard", "square"): {"N": ("SEA", "INDUSTRIAL", "QUAY")},
}
# The shore kind of a SEA side where it is not a beach (Lighthouse Bay's headland under the lighthouse).
SHORES = {"lighthousebay": {"E": "CLIFF"}, "landingbeach": {}, "coralisles": {}}
SIDES = ["N", "E", "S", "W"]
# Island maps: beyond the outline is the sea (Coral Keys' islands stand in it), but where land scenery stands.
ISLAND_MAPS = {"coralisles"}


def rect_of(m):
    if m.get("bounds"):
        return tuple(m["bounds"])
    h = m["size"] / 2
    return (-h, -h, h, h)


def side_frame(side, r):
    """(start point, along unit, outward unit, length) of a side, along running with x (N, S) or z (E, W)."""
    x0, z0, x1, z1 = r
    if side == "N":
        return (x0, z1), (1, 0), (0, 1), x1 - x0
    if side == "S":
        return (x0, z0), (1, 0), (0, -1), x1 - x0
    if side == "E":
        return (x1, z0), (0, 1), (1, 0), z1 - z0
    return (x0, z0), (0, 1), (-1, 0), z1 - z0


def classify(bf, square, m, r):
    water = [(p["x"], p["z"]) for p in m["props"] + m.get("decor", []) if p["def"] == "river_water"]
    cliffs = [(p["x"], p["z"]) for p in m["props"] + m.get("decor", []) if p["def"] in CLIFF_PROPS]
    over = OVERRIDES.get((bf, "square" if square else "long"), {})
    flat = m.get("boundary") or []
    poly = list(zip(flat[0::2], flat[1::2]))
    land_decor = [(p["x"], p["z"]) for p in m.get("decor", []) if p["def"] not in HARBOUR_DECOR and p["def"] != "river_water"]
    segments = []
    for side in SIDES:
        (sx, sz), (ax, az), (ox, oz), length = side_frame(side, r)
        if side in over:
            t, mod, shore = over[side]
            seg = {"side": side, "from": round(sx * ax + sz * az, 2), "to": round(sx * ax + sz * az + length, 2), "type": t}
            if mod:
                seg["modifier"] = mod
            if shore:
                seg["shore"] = shore
            segments.append(seg)
            continue
        bins = []
        n = int(round(length / BIN))
        for k in range(n):
            u0, u1 = k * BIN, (k + 1) * BIN

            def near(pts, depth, pad):
                for px, pz in pts:
                    u = (px - sx) * ax + (pz - sz) * az
                    d = -((px - sx) * ox + (pz - sz) * oz)      # metres in from the edge
                    if u0 - pad <= u <= u1 + pad and -4 <= d <= depth:
                        return True
                return False

            def off_outline():
                for d in (2.0, 7.0, 12.0):
                    for f in (0.25, 0.5, 0.75):
                        x = sx + ax * (u0 + (u1 - u0) * f) - ox * d
                        z = sz + az * (u0 + (u1 - u0) * f) - oz * d
                        if not poly or ca.outline_tools.inside(poly, x, z):
                            return False
                return not near(land_decor, STRIP, 0.0)

            if near(water, STRIP, 0.0) or (bf in ISLAND_MAPS and off_outline()):
                t = "SEA" if bf in SEA_MAPS else "RIVER"
            elif near(cliffs, STRIP + 10, 4.0):
                t = "CLIFF"
            elif bf in URBAN_MAPS:
                t = "URBAN"
            else:
                t = "LAND"
            bins.append(t)
        runs = []
        for k, t in enumerate(bins):
            if runs and runs[-1][0] == t:
                runs[-1][2] = k + 1
            else:
                runs.append([t, k, k + 1])
        # Short runs join their longer neighbour (a river crossing keeps its own run).
        changed = True
        while changed and len(runs) > 1:
            changed = False
            for i, (t, a, b) in enumerate(runs):
                if t == "RIVER" or (b - a) * BIN >= MIN_RUN:
                    continue
                left = runs[i - 1] if i > 0 else None
                right = runs[i + 1] if i + 1 < len(runs) else None
                into = left if right is None or (left is not None and left[2] - left[1] >= right[2] - right[1]) else right
                if into is left:
                    left[2] = b
                else:
                    right[1] = a
                runs.pop(i)
                merged = []
                for run in runs:
                    if merged and merged[-1][0] == run[0]:
                        merged[-1][2] = run[2]
                    else:
                        merged.append(run)
                runs = merged
                changed = True
                break
        base = sx * ax + sz * az
        for t, a, b in runs:
            seg = {"side": side, "from": round(base + a * BIN, 2), "to": round(base + min(length, b * BIN), 2), "type": t}
            mod = modifier(bf, t)
            if mod:
                seg["modifier"] = mod
            if t == "SEA":
                seg["shore"] = SHORES.get(bf, {}).get(side, "BEACH")
            segments.append(seg)
    return segments


def modifier(bf, t):
    if t == "SEA":
        return "HARBOR" if bf == "ironport" else "INDUSTRIAL" if bf == "rustyard" else None
    if bf in INDUSTRIAL_MAPS:
        return "INDUSTRIAL"
    if t == "LAND" and bf in URBAN_MAPS:
        return "URBAN"
    return None


def point_on(side, u, r):
    (sx, sz), (ax, az), _, _ = side_frame(side, r)
    base = sx * ax + sz * az
    return sx + ax * (u - base), sz + az * (u - base)


PIECE = {
    frozenset(["LAND", "SEA"]): "corner_land_sea", frozenset(["RIVER", "SEA"]): "mouth_river_sea",
    frozenset(["CLIFF", "SEA"]): "corner_cliff_sea", frozenset(["URBAN", "SEA"]): "corner_quay_sea",
    frozenset(["LAND", "RIVER"]): "bank_land_river", frozenset(["CLIFF", "RIVER"]): "gorge_cliff_river",
    frozenset(["URBAN", "RIVER"]): "embankment_urban_river", frozenset(["LAND", "CLIFF"]): "corner_land_cliff",
    frozenset(["LAND", "URBAN"]): "corner_land_urban", frozenset(["CLIFF", "URBAN"]): "corner_cliff_urban",
}


def corners(segments, r):
    """Where two edge types meet along a side, and the rectangle's four corners (outer corner pieces)."""
    out = []
    by_side = {s: [g for g in segments if g["side"] == s] for s in SIDES}
    for side, segs in by_side.items():
        for a, b in zip(segs, segs[1:]):
            if a["type"] != b["type"]:
                x, z = point_on(side, a["to"], r)
                out.append({"x": round(x, 2), "z": round(z, 2), "between": [a["type"], b["type"]],
                            "piece": PIECE[frozenset([a["type"], b["type"]])]})
    x0, z0, x1, z1 = r
    for (x, z), (s1, end1), (s2, end2) in [((x0, z1), ("N", 0), ("W", -1)), ((x1, z1), ("N", -1), ("E", -1)),
                                           ((x1, z0), ("S", -1), ("E", 0)), ((x0, z0), ("S", 0), ("W", 0))]:
        t1, t2 = by_side[s1][end1]["type"], by_side[s2][end2]["type"]
        piece = f"outer_{t1.lower()}" if t1 == t2 else PIECE[frozenset([t1, t2])].replace("corner_", "outer_", 1)
        out.append({"x": x, "z": z, "between": [t1, t2], "piece": piece, "outer": True})
    return out


def seg_at(segments, side, u):
    for g in segments:
        if g["side"] == side and g["from"] - 1e-6 <= u <= g["to"] + 1e-6:
            return g
    return None


def edge_hit(x, z, dx, dz, r):
    """Where the ray from (x, z) along (dx, dz) leaves the rectangle: (side, u, x, z, t)."""
    x0, z0, x1, z1 = r
    best = None
    for side, t in (("E", (x1 - x) / dx if dx > 1e-9 else None), ("W", (x0 - x) / dx if dx < -1e-9 else None),
                    ("N", (z1 - z) / dz if dz > 1e-9 else None), ("S", (z0 - z) / dz if dz < -1e-9 else None)):
        if t is not None and t >= -1e-6 and (best is None or t < best[1]):
            best = (side, t)
    if best is None:
        return None
    side, t = best
    hx, hz = x + dx * t, z + dz * t
    u = hx if side in ("N", "S") else hz
    return side, u, hx, hz, t


def links(m, r, segments):
    """The lines that meet the edge: roads, rails, rivers, the coast, sea lanes, air corridors."""
    out = []
    x0, z0, x1, z1 = r
    reach = 14.0

    def near_edge(x, z):
        return min(x - x0, x1 - x, z - z0, z1 - z) <= reach

    for road in m.get("roads", []):
        pts = list(zip(road["points"][0::2], road["points"][1::2]))
        for end, prev in ((pts[0], pts[1]), (pts[-1], pts[-2])):
            if not near_edge(*end):
                continue
            dx, dz = end[0] - prev[0], end[1] - prev[1]
            L = math.hypot(dx, dz)
            if L < 1e-6:
                continue
            hit = edge_hit(end[0], end[1], dx / L, dz / L, r)
            if hit is None or hit[4] > reach * 2:
                continue
            side, u, hx, hz, _ = hit
            out.append({"kind": "road", "side": side, "x": round(hx, 2), "z": round(hz, 2), "dirX": round(dx / L, 4),
                        "dirZ": round(dz / L, 4), "width": road.get("width", 6), "from": [round(end[0], 2), round(end[1], 2)]})
    for rail in m.get("rails", []):
        pts = list(zip(rail["points"][0::2], rail["points"][1::2]))
        for a, b in zip(pts, pts[1:]):
            inside_a = x0 <= a[0] <= x1 and z0 <= a[1] <= z1
            inside_b = x0 <= b[0] <= x1 and z0 <= b[1] <= z1
            if inside_a == inside_b:
                continue
            p, q = (b, a) if inside_b else (a, b)          # p inside, q outside
            dx, dz = q[0] - p[0], q[1] - p[1]
            L = math.hypot(dx, dz)
            side, u, hx, hz, _ = edge_hit(p[0], p[1], dx / L, dz / L, r)
            out.append({"kind": "rail", "id": rail["id"], "side": side, "x": round(hx, 2), "z": round(hz, 2),
                        "dirX": round(dx / L, 4), "dirZ": round(dz / L, 4)})
    # Rivers and the coast: the water runs of the sides, and where a sea side meets another type.
    for g in segments:
        side = g["side"]
        (_, _), _, (ox, oz), _ = side_frame(side, r)
        if g["type"] == "RIVER":
            mid = (g["from"] + g["to"]) / 2
            x, z = point_on(side, mid, r)
            out.append({"kind": "river", "side": side, "x": round(x, 2), "z": round(z, 2), "dirX": ox, "dirZ": oz,
                        "width": round(g["to"] - g["from"], 2)})
    for c in corners(segments, r):
        if "SEA" in c["between"] and len(set(c["between"])) == 2:
            out.append({"kind": "coast", "x": c["x"], "z": c["z"], "between": c["between"]})
    sea = m.get("sea")
    if sea:
        for n in (m.get("seaRoutes") or {}).get("nodes", []):
            if n.get("kind") == "exit":
                x, z = n["x"], n["z"]
                cx, cz = min(max(x, x0), x1), min(max(z, z0), z1)
                dx, dz = x - cx, z - cz
                L = math.hypot(dx, dz) or 1.0
                out.append({"kind": "seaLane", "lane": n.get("lane"), "x": round(cx, 2), "z": round(cz, 2),
                            "dirX": round(dx / L, 4), "dirZ": round(dz / L, 4)})
        if sea.get("airEntry"):
            ax_, az_ = sea["airEntry"]
            out.append({"kind": "air", "x": ax_, "z": az_, "dirX": round(math.copysign(0.7071, ax_), 4),
                        "dirZ": round(math.copysign(0.7071, az_), 4), "note": "sea.airEntry"})
    # Air corridors: aircraft come in over any side (EconomySystem's EdgeBehind); one corridor mark per side's middle.
    for side in SIDES:
        (sx, sz), (ax, az), (ox, oz), length = side_frame(side, r)
        out.append({"kind": "air", "side": side, "x": round(sx + ax * length / 2, 2), "z": round(sz + az * length / 2, 2),
                    "dirX": ox, "dirZ": oz})
    return out


class Ground:
    """The bare grid (blocking props, static start units, the outline) and its main region (team 0's)."""

    def __init__(self, m, tables):
        props, footprint, _ = tables
        self.g = ca.build_grid(m, props, footprint, fill=False)
        sx, sz = self.g.cell(m["teams"][0]["x"], m["teams"][0]["z"])
        start = self.nearest_open(sx, sz)
        self.main = set()
        if start:
            q = deque([start])
            self.main.add(start)
            while q:
                x, z = q.popleft()
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    k = (x + dx, z + dz)
                    if k not in self.main and self.g.open(*k):
                        self.main.add(k)
                        q.append(k)

    def nearest_open(self, gx, gz):
        for rr in range(12):
            for dz in range(-rr, rr + 1):
                for dx in range(-rr, rr + 1):
                    if max(abs(dx), abs(dz)) == rr and self.g.open(gx + dx, gz + dz):
                        return gx + dx, gz + dz
        return None

    def ok(self, x, z):
        """Open ground of the main region with a little room round it (a column comes in here)."""
        gx, gz = self.g.cell(x, z)
        return all((gx + dx, gz + dz) in self.main for dx in (-1, 0, 1) for dz in (-1, 0, 1))


def gate(kind, side, x, z, inx, inz, r, gid):
    """A gate at (x, z), the way in (inx, inz): its approach runs straight back out OUTER m past the rectangle."""
    hit = edge_hit(x, z, -inx, -inz, r)
    to_edge = hit[4] if hit else 0.0
    ex, ez = x - inx * to_edge, z - inz * to_edge
    fx, fz = ex - inx * OUTER, ez - inz * OUTER
    return {"id": gid, "kind": kind, "side": side, "x": round(x, 2), "z": round(z, 2), "inX": round(inx, 4), "inZ": round(inz, 4),
            "visualIngressLength": round(to_edge + OUTER, 2),
            "path": [round(fx, 2), round(fz, 2), round(ex, 2), round(ez, 2), round(x, 2), round(z, 2)]}


def entry_gates(m, r, segments, ground, link_list):
    gates = []
    n = 0
    drivable = {"LAND", "URBAN", "CLIFF", "RIVER"}
    # Roads: the first open spot along the road in from the edge.
    for l in link_list:
        if l["kind"] != "road":
            continue
        inx, inz = -l["dirX"], -l["dirZ"]
        for d in range(int(EDGE_MARGIN), int(GATE_DEPTH) + 1, 1):
            x, z = l["x"] + inx * d, l["z"] + inz * d
            if ground.ok(x, z):
                gates.append(gate("road", l["side"], x, z, inx, inz, r, f"road{n}"))
                n += 1
                break
    # Rails: the line's own entry gate (the RailSpline's playFrom point, where it crosses the outline).
    for rail in m.get("rails", []):
        pts = list(zip(rail["points"][0::2], rail["points"][1::2]))
        s = rail.get("playFrom", 0.0)
        acc = 0.0
        for a, b in zip(pts, pts[1:]):
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            if acc + L >= s and L > 1e-6:
                t = (s - acc) / L
                x, z = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                inx, inz = (b[0] - a[0]) / L, (b[1] - a[1]) / L
                side = edge_hit(x, z, -inx, -inz, r)
                g = gate("rail", side[0] if side else "", x, z, inx, inz, r, f"rail_{rail['id']}")
                g["rail"] = rail["id"]
                g["playFrom"] = s
                gates.append(g)
                break
            acc += L
    # Edges one can drive in from: every GATE_STEP m, the first open spot EDGE_MARGIN-GATE_DEPTH m in.
    for side in SIDES:
        (sx, sz), (ax, az), (ox, oz), length = side_frame(side, r)
        base = sx * ax + sz * az
        k = GATE_STEP / 2
        while k < length:
            u = base + k
            g = seg_at(segments, side, u)
            k += GATE_STEP
            if g is None:
                continue
            ex, ez = point_on(side, u, r)
            kind = "sea" if g["type"] == "SEA" else "edge"
            if g["type"] not in drivable and kind != "sea":
                continue
            depth = 60 if kind == "sea" else GATE_DEPTH
            for d in range(int(EDGE_MARGIN), int(depth) + 1):
                x, z = ex - ox * d, ez - oz * d
                if ground.ok(x, z):
                    if kind == "edge" and any(math.hypot(x - q["x"], z - q["z"]) < GATE_MERGE for q in gates):
                        break
                    gates.append(gate(kind, side, x, z, -ox, -oz, r, f"{kind}{n}"))
                    n += 1
                    break
    # A sea's own landing beaches (Lighthouse Bay): the landing craft's way in from the water.
    sea = m.get("sea")
    if sea:
        for i, l in enumerate(sea.get("landings", [])):
            ix, iz = l["inland"]
            dx, dz = ix - l["x"], iz - l["z"]
            L = math.hypot(dx, dz) or 1.0
            if ground.ok(ix, iz):
                g = gate("sea", "", ix, iz, dx / L, dz / L, r, f"landing{i}")
                g["path"] = [round(l["x"] - dx / L * OUTER, 2), round(l["z"] - dz / L * OUTER, 2), l["x"], l["z"], ix, iz]
                g["visualIngressLength"] = round(OUTER + L, 2)
                gates.append(g)
    return gates


def trim_decor(m, r, segments):
    """Land scenery on the water of a SEA side goes (the sea runs on to the horizon)."""
    water = {(round(p["x"] / 4), round(p["z"] / 4)) for p in m["props"] + m.get("decor", []) if p["def"] == "river_water"}
    x0, z0, x1, z1 = r
    keep, dropped = [], []
    for p in m.get("decor", []):
        x, z = p["x"], p["z"]
        drop = False
        if p["def"] not in HARBOUR_DECOR and p["def"] != "river_water":
            on_water = any((round(x / 4) + dx, round(z / 4) + dz) in water for dx in (-1, 0, 1) for dz in (-1, 0, 1))
            for side, d, u in (("N", z1 - z, x), ("S", z - z0, x), ("E", x1 - x, z), ("W", x - x0, z)):
                g = seg_at(segments, side, u)
                # On a sea side: anything on the water, and any land scenery in the strip by the edge (the sea's).
                if g and g["type"] == "SEA" and (on_water and d <= 30 or d <= STRIP):
                    drop = True
        (dropped if drop else keep).append(p)
    return keep, dropped


def rewrite_decor(path, keep):
    """Rewrites the "decor" array in place (one item a line, as build_maps.py writes it)."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    try:
        start = lines.index('  "decor": [')
    except ValueError:
        return
    end = start + 1
    while not lines[end].startswith("  ]"):
        end += 1
    items = ["    " + json.dumps(p, separators=(", ", ": ")) + ("," if i + 1 < len(keep) else "") for i, p in enumerate(keep)]
    lines[start + 1:end] = items
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def check(name, m, r, segments, gates):
    problems = []
    for side in SIDES:
        segs = [g for g in segments if g["side"] == side]
        (sx, sz), (ax, az), _, length = side_frame(side, r)
        base = sx * ax + sz * az
        if not segs or abs(segs[0]["from"] - base) > 0.01 or abs(segs[-1]["to"] - (base + length)) > 0.01:
            problems.append(f"{name}: side {side} not covered")
        for a, b in zip(segs, segs[1:]):
            if abs(a["to"] - b["from"]) > 0.01:
                problems.append(f"{name}: side {side} gap at {a['to']}")
    bf = name.rsplit("_", 1)[0]
    if bf in SEA_MAPS and not name.endswith("_long") and not any(g["type"] == "SEA" for g in segments):
        problems.append(f"{name}: a sea map without a SEA side")
    if not any(g["kind"] in ("road", "edge") for g in gates):
        problems.append(f"{name}: no land entry gate")
    return problems


def main(argv):
    check_only = "--check" in argv
    only = [a for a in argv if not a.startswith("--")]
    tables = ca.balance()
    problems, written = [], 0
    summary = {}
    for bf in transit.BATTLEFIELDS:
        if only and bf not in only:
            continue
        for variant in VARIANTS:
            path = os.path.join(MAPS, f"{bf}_{variant}.json")
            if not os.path.exists(path):
                continue
            name = f"{bf}_{variant}"
            m = transit.load(path)
            r = rect_of(m)
            segs = classify(bf, variant != "long", m, r)
            link_list = links(m, r, segs)
            ground = Ground(m, tables)
            gates = entry_gates(m, r, segs, ground, link_list)
            keep, dropped = trim_decor(m, r, segs)
            problems += check(name, m, r, segs, gates)
            edges = {"band": BAND, "outer": OUTER, "segments": segs, "corners": corners(segs, r), "links": link_list}
            types = sorted({g["type"] for g in segs})
            summary[name] = types
            runs = ", ".join(g["side"] + " " + g["type"] + ("+" + g["modifier"] if "modifier" in g else "") for g in segs)
            print(f"{name}: {runs}; {len(gates)} gates; {len(link_list)} links; {len(dropped)} decor off the sea")
            if not check_only:
                transit.rewrite(path, {"edges": edges, "entryGates": gates})
                if dropped:
                    rewrite_decor(path, keep)
                written += 1
    for p in problems:
        print("PROBLEM", p)
    sea = sorted({n.rsplit("_", 1)[0] for n, t in summary.items() if "SEA" in t})
    print(f"maps with a SEA side: {', '.join(sea)}")
    print(f"{written} map files written, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
