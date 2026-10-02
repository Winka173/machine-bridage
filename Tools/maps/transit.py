"""Prompt 33 L4-L5: the routes of the big ships and the trains on the generated map files.

    python Tools/maps/transit.py            # every battlefield
    python Tools/maps/transit.py --check    # only check, write nothing (exit 1 on a problem)
    python Tools/maps/transit.py ironport   # one battlefield

Works on the generated map files (run it again after Tools/maps/build_maps.py, like neutrals.py): it writes one
field per route system, each on its own line before "boundary", and replaces what an earlier run wrote:

- "seaRoutes" (L4, a map with a "sea"): the SeaRouteGraph of the big ships, built from the sea lanes by the same rule as
  `SeaRouteGraph.FromSea` (Sim/Navigation/SeaRouteGraph.cs): a track node every NODE_STEP m along each lane (u in the
  coast's frame) from -end to +end, an exit node EXIT_REACH m beyond each end (outside the play area: the ships' routes
  run on out of it), holding nodes (the passing bays) on two holding lines (HOLD_SHORE m inshore of the nearest lane and
  HOLD_SEA m out beyond the farthest) where they are on the water and inside the map, linked to the nearest lane's
  track node; cross links between lanes at the same u. Every segment is two-way (passing bays, no one-way rule).
- "rails" (L5): the RailSplines (see RAILS below).

Checks (also with --check): every track and holding node inside the map is on the water; every two-way lane has a
passing bay within BAY_REACH m of each of its nodes; the exits lie beyond the map's edge.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MAPS = os.path.join(ROOT, "Assets", "MachineBrigade", "Resources", "Data", "maps")
BATTLEFIELDS = ["ashfield", "borderbridge", "capital", "coralisles", "dunebreak", "emberridge", "foundry", "frostpeak",
                "greenvale", "hydrodam", "ironport", "junglepass", "landingbeach", "launchsite", "lighthousebay",
                "metrocity", "openpit", "orbitalgate", "redrock", "rustyard", "saltflat", "skyhold", "swamp",
                "veyra_old_quarter", "whiteout"]
VARIANTS = ["conquest", "sandbox", "siege"]

# ------------------------------------------------------------------ L4: the sea route graph (keep in step with C#)
NODE_STEP = 40.0
EXIT_REACH = 40.0
HOLD_SHORE = 16.0
HOLD_SEA = 18.0
HOLD_MARGIN = 12.0      # a holding node keeps this far inside the map's square
HOLD_WATER = 8.0        # and this far out from the waterline
CORRIDOR = 20.0
BAY_REACH = 60.0


def strip(text: str) -> str:
    return re.sub(r"^\s*//.*$", "", text, flags=re.M)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.loads(strip(f.read()))


class Sea:
    """The coast's frame of map data "sea" (as SeaDef): u along, w out."""

    def __init__(self, s):
        a = s.get("along", [math.sqrt(0.5), math.sqrt(0.5)])
        n = math.hypot(a[0], a[1])
        self.along = (a[0] / n, a[1] / n)
        self.out = (self.along[1], -self.along[0])
        flat = s.get("shore", [])
        self.su = flat[0::2]
        self.sw = flat[1::2]
        self.lanes = sorted(s.get("lanes", []), key=lambda l: l["w"])

    def at(self, u, w):
        return (self.along[0] * u + self.out[0] * w, self.along[1] * u + self.out[1] * w)

    def shore(self, u):
        if not self.su:
            return 0.0
        if u <= self.su[0]:
            return self.sw[0]
        last = len(self.su) - 1
        if u >= self.su[last]:
            return self.sw[last]
        step = (self.su[last] - self.su[0]) / last
        i = max(0, min(last - 1, int((u - self.su[0]) / step)))
        t = (u - self.su[i]) / max(1e-3, self.su[i + 1] - self.su[i])
        return self.sw[i] + (self.sw[i + 1] - self.sw[i]) * t

    def is_sea(self, u, w, margin=0.0):
        return w > self.shore(u) + margin


def sea_graph(sea: Sea, half: float):
    """The graph as SeaRouteGraph.FromSea builds it: nodes [{id, x, z, kind, lane}], segments [{a, b}]."""
    nodes, segments, frames = [], [], {}

    def node(nid, u, w, kind, lane):
        x, z = sea.at(u, w)
        nodes.append({"id": nid, "x": round(x, 2), "z": round(z, 2), "kind": kind, "lane": lane})
        frames[nid] = (u, w)
        return nid

    def inside(u, w, margin):
        x, z = sea.at(u, w)
        return abs(x) <= half - margin and abs(z) <= half - margin

    tracks = {}
    for lane in sea.lanes:
        end = lane.get("end", 100.0)
        us = [-(end + EXIT_REACH)]
        k0, k1 = math.ceil(-end / NODE_STEP), math.floor(end / NODE_STEP)
        us += [k * NODE_STEP for k in range(k0, k1 + 1)]
        us.append(end + EXIT_REACH)
        ids = []
        for i, u in enumerate(us):
            kind = "exit" if i in (0, len(us) - 1) else "track"
            ids.append(node(f"{lane['id']}_{i}", u, lane["w"], kind, lane["id"]))
        for a, b in zip(ids, ids[1:]):
            segments.append({"a": a, "b": b})
        tracks[lane["id"]] = ids
    if not sea.lanes:
        return {"corridor": CORRIDOR, "nodes": nodes, "segments": segments}
    # Cross links between neighbouring lanes at the same u (track nodes only, not the exits).
    for la, lb in zip(sea.lanes, sea.lanes[1:]):
        by_u = {round(frames[n][0], 2): n for n in tracks[lb["id"]][1:-1]}
        for n in tracks[la["id"]][1:-1]:
            other = by_u.get(round(frames[n][0], 2))
            if other:
                segments.append({"a": n, "b": other})
    # The holding lines: inshore of the nearest lane, out beyond the farthest.
    lines = [(sea.lanes[0]["w"] - HOLD_SHORE, sea.lanes[0]), (sea.lanes[-1]["w"] + HOLD_SEA, sea.lanes[-1])]
    for side, (w, lane) in zip(("shore", "sea"), lines):
        for n in tracks[lane["id"]]:
            u, _ = frames[n]
            if n == tracks[lane["id"]][0] or n == tracks[lane["id"]][-1]:
                continue
            if not inside(u, w, HOLD_MARGIN) or not sea.is_sea(u, w, HOLD_WATER):
                continue
            h = node(f"hold_{side}_{n}", u, w, "holding", lane["id"])
            segments.append({"a": n, "b": h})
    return {"corridor": CORRIDOR, "nodes": nodes, "segments": segments}


def check_sea(name, graph, sea: Sea, half):
    problems = []
    by_id = {n["id"]: n for n in graph["nodes"]}

    def uw(n):
        x, z = n["x"], n["z"]
        return (x * sea.along[0] + z * sea.along[1], x * sea.out[0] + z * sea.out[1])

    for n in graph["nodes"]:
        x, z = n["x"], n["z"]
        u, w = uw(n)
        on_map = abs(x) <= half and abs(z) <= half
        if n["kind"] == "exit":
            if on_map:
                problems.append(f"{name}: exit {n['id']} ({x}, {z}) is inside the map")
            continue
        if on_map and not sea.is_sea(u, w, 4.0):
            problems.append(f"{name}: node {n['id']} ({x}, {z}) is not on the water")
    holds = [uw(n) for n in graph["nodes"] if n["kind"] == "holding"]
    for n in graph["nodes"]:
        if n["kind"] != "track":
            continue
        u, _ = uw(n)
        if not any(abs(u - hu) <= BAY_REACH for hu, _ in holds):
            problems.append(f"{name}: lane node {n['id']} has no passing bay within {BAY_REACH:.0f} m along the coast")
    for s in graph["segments"]:
        if s["a"] not in by_id or s["b"] not in by_id:
            problems.append(f"{name}: segment {s['a']}-{s['b']} names a missing node")
    return problems


# ------------------------------------------------------------------ L5: the rails (keep in step with RailSpline / RailSystem)
# Each line: an id, its points inside the map (in order from the end that runs out of the map), and which of its ends run
# out through the edge band to a tunnel portal ("first", "both"; the other end is a buffer stop inside). The lines of
# build_maps.py's FIXED_ROUTES (the boss trains' routes, kept clear by the builder), Capital's Nemesis line (c7m10's stage),
# Rust Yard's siding run on west as far as its ground is clear, Foundry's line found on its layout (foundry_line), and on
# every Siege version with a rail line in its fortress the line in ("siege", the arrival path, already from beyond the map).
BAND_HALF = 3.5          # RailSpline.BandHalf
PORTAL_REACH = 40.0      # the portal stands this far beyond the map's square
CORNER_RADIUS = 8.0      # a corner is rounded to this radius (a waypoint stays within 3.3 m of the line)
CROSSING_MERGE = 12.0
HULL = 4.0               # a crossing's length: the band across the road, plus a hull
TRAIN_CLEAR = 2.3        # nothing solid within this of the line (the widest train's half width, 1.8 m, + 0.5 m)
LINES = {
    # From the west portal along the quay to a buffer stop at Juggernaut's spot (a command tent stands on the line's east end).
    "ironport": [("quay", [(-138.75, 106.8), (128.0, 106.8)], "first")],
    "metrocity": [("avenue", [(128.0, 101.25), (75.0, 101.25), (0.0, 101.25), (-67.5, 101.25), (-101.25, 101.25), (-101.25, 33.75)], "first")],
    # On the avenue, 4 m south of its middle (a wreck stands on the middle); c7m10's waypoints stay within 5 m of it.
    "capital": [("nemesis", [(140.0, -4.0), (36.0, -4.0)], "first")],
    "rustyard": [("siding", [(140.0, 11.25), (132.0, 11.25)], "first")],
}
# Rust Yard's siding runs on west from Gungnir's spot while its band is clear, at most this far.
SIDING_WEST = 60.0
# Foundry has no line of its own: one is laid on its layout (the longest clear straight run in from the north-east edge).
FOUNDRY = "foundry"
FOUNDRY_MIN = 60.0
FOUNDRY_MAX = 120.0


class Ground:
    """The ground at load as the Sim's grid has it before a mode spawns anything: blocking props and the outline."""

    def __init__(self, m, props):
        import check_access as ca
        self.ca = ca
        self.g = ca.Grid(m["size"], m.get("bounds"))
        self.prop_blocked = set()
        self.solid = []
        for p in m["props"]:
            w, d, blocks = props[p["def"]]
            if not blocks:
                continue
            if p.get("rot", 0) % 180 == 90:
                w, d = d, w
            self.block(p["x"], p["z"], w + 2 * ca.CLEARANCE, d + 2 * ca.CLEARANCE, self.prop_blocked)
            w0, d0, _ = props[p["def"]]
            self.solid.append((p["x"], p["z"], w0 / 2, d0 / 2, p.get("rot", 0)))
        self.poly = None
        if m.get("boundary"):
            flat = m["boundary"]
            self.poly = list(zip(flat[0::2], flat[1::2]))
        self.half = m["size"] / 2
        self._inside = {}

    def block(self, x, z, w, d, into):
        a0, b0 = self.g.cell(x - w / 2, z - d / 2)
        a1, b1 = self.g.cell(x + w / 2 - 1e-4, z + d / 2 - 1e-4)
        for gz in range(max(0, b0), min(self.g.nz - 1, b1) + 1):
            for gx in range(max(0, a0), min(self.g.nx - 1, a1) + 1):
                into.add((gx, gz))

    def inside(self, x, z):
        if abs(x) > self.half or abs(z) > self.half:
            return False
        return self.poly is None or self.ca.outline_tools.inside(self.poly, x, z)

    def open(self, gx, gz):
        if not (0 <= gx < self.g.nx and 0 <= gz < self.g.nz) or (gx, gz) in self.prop_blocked:
            return False
        key = (gx, gz)
        if key not in self._inside:
            self._inside[key] = self.inside(*self.g.centre(gx, gz))
        return self._inside[key]

    def band_clear(self, x, z, tx, tz):
        """No blocking prop's footprint (as placed, turned by its rot) within TRAIN_CLEAR of the line at (x, z)."""
        for px, pz, hw, hd, rot in self.solid:
            if abs(px - x) > hw + hd + TRAIN_CLEAR or abs(pz - z) > hw + hd + TRAIN_CLEAR:
                continue
            a = math.radians(rot)
            # Into the prop's own frame (its rot turns it clockwise seen from above, the game's heading).
            dx, dz = x - px, z - pz
            lx = dx * math.cos(a) - dz * math.sin(a)
            lz = dx * math.sin(a) + dz * math.cos(a)
            ox = max(0.0, abs(lx) - hw)
            oz = max(0.0, abs(lz) - hd)
            if math.hypot(ox, oz) < TRAIN_CLEAR:
                return False
        return True


def polyline(points):
    out = [points[0]]
    for a, b in zip(points, points[1:]):
        if math.hypot(b[0] - a[0], b[1] - a[1]) > 1e-6:
            out.append(b)
    return out


def rounded(points, radius=CORNER_RADIUS):
    """The corners rounded (an arc of the radius, sampled every 15 degrees or less)."""
    if len(points) < 3:
        return [(round(x, 2), round(z, 2)) for x, z in points]
    out = [points[0]]
    for i in range(1, len(points) - 1):
        a, b, c = points[i - 1], points[i], points[i + 1]
        d1 = (b[0] - a[0], b[1] - a[1])
        d2 = (c[0] - b[0], c[1] - b[1])
        l1, l2 = math.hypot(*d1), math.hypot(*d2)
        u1, u2 = (d1[0] / l1, d1[1] / l1), (d2[0] / l2, d2[1] / l2)
        turn = math.atan2(u1[0] * u2[1] - u1[1] * u2[0], u1[0] * u2[0] + u1[1] * u2[1])
        if abs(turn) < 1e-3:
            out.append(b)
            continue
        cut = min(radius * math.tan(abs(turn) / 2), l1 / 2, l2 / 2)
        r = cut / math.tan(abs(turn) / 2)
        p0 = (b[0] - u1[0] * cut, b[1] - u1[1] * cut)
        side = 1 if turn > 0 else -1
        centre = (p0[0] - u1[1] * r * side, p0[1] + u1[0] * r * side)
        a0 = math.atan2(p0[1] - centre[1], p0[0] - centre[0])
        steps = max(2, int(math.ceil(abs(math.degrees(turn)) / 15)))
        for k in range(steps + 1):
            ang = a0 + turn * k / steps
            out.append((centre[0] + r * math.cos(ang), centre[1] + r * math.sin(ang)))
    out.append(points[-1])
    return polyline([(round(x, 2), round(z, 2)) for x, z in out])


def extend(a, b, half):
    """From b, on along a->b until PORTAL_REACH beyond the map's square."""
    dx, dz = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dz)
    dx, dz = dx / n, dz / n
    ts = []
    if abs(dx) > 1e-6:
        ts.append(((half if dx > 0 else -half) - b[0]) / dx)
    if abs(dz) > 1e-6:
        ts.append(((half if dz > 0 else -half) - b[1]) / dz)
    t = min(x for x in ts if x >= 0) + PORTAL_REACH
    return (round(b[0] + dx * t, 2), round(b[1] + dz * t, 2))


def measured(points):
    at = [0.0]
    for a, b in zip(points, points[1:]):
        at.append(at[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    return at


def point_at(points, at, s):
    for i in range(len(points) - 1):
        if at[i + 1] >= s or i == len(points) - 2:
            span = max(1e-6, at[i + 1] - at[i])
            t = min(1.0, max(0.0, (s - at[i]) / span))
            a, b = points[i], points[i + 1]
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), ((b[0] - a[0]) / span, (b[1] - a[1]) / span)
    return points[-1], (0.0, 1.0)


def play_stretch(ground, points, at, gates):
    """The stretch inside the play area: from where the line first comes inside (if it comes in) to where it last is."""
    total = at[-1]
    s_in = [k * 0.5 for k in range(int(total * 2) + 1) if ground.inside(*point_at(points, at, k * 0.5)[0])]
    if not s_in:
        return None
    first, last = s_in[0], s_in[-1]
    return (first if gates in ("first", "both") else 0.0, last if gates == "both" else total)


def blocked_on(ground, points, at, lo, hi):
    """The places along [lo, hi] where a blocking prop stands on the band (every metre)."""
    bad = []
    s = lo
    while s <= hi + 1e-6:
        (x, z), (tx, tz) = point_at(points, at, s)
        if not ground.band_clear(x, z, tx, tz):
            bad.append(round(s, 1))
        s += 1.0
    return bad


def seg_cross(a, b, c, d):
    """The intersection of segments a-b and c-d: (t along a-b, point, sine of the angle) or None (parallel or apart)."""
    r = (b[0] - a[0], b[1] - a[1])
    q = (d[0] - c[0], d[1] - c[1])
    den = r[0] * q[1] - r[1] * q[0]
    if abs(den) < 1e-9:
        return None
    w = (c[0] - a[0], c[1] - a[1])
    t = (w[0] * q[1] - w[1] * q[0]) / den
    u = (w[0] * r[1] - w[1] * r[0]) / den
    if not (0.0 <= t <= 1.0 and 0.0 <= u <= 1.0):
        return None
    return t, (a[0] + r[0] * t, a[1] + r[1] * t), abs(den) / (math.hypot(*r) * math.hypot(*q))


def crossings(m, points, at, lo, hi):
    """Where the map's roads cross the play stretch: id, s, x, z, the box its barriers close, its length."""
    found = []
    for road in m.get("roads", []):
        flat = road["points"]
        rp = list(zip(flat[0::2], flat[1::2]))
        width = road.get("width", 5.0)
        for c, d in zip(rp, rp[1:]):
            for i, (a, b) in enumerate(zip(points, points[1:])):
                hit = seg_cross(a, b, c, d)
                if not hit:
                    continue
                t, p, sine = hit
                s = at[i] + (at[i + 1] - at[i]) * t
                if s < lo or s > hi or sine < 0.2:
                    continue
                along = width / sine + 2.0
                across = 2 * BAND_HALF
                tx, tz = (b[0] - a[0]), (b[1] - a[1])
                if abs(tx) >= abs(tz):
                    w, dd = along, across
                else:
                    w, dd = across, along
                found.append({"s": round(s, 2), "x": round(p[0], 2), "z": round(p[1], 2), "width": round(w, 2), "depth": round(dd, 2),
                              "length": round(2 * BAND_HALF / sine + HULL, 2)})
    found.sort(key=lambda c: c["s"])
    merged = []
    for c in found:
        if merged and c["s"] - merged[-1]["s"] < CROSSING_MERGE:
            prev = merged[-1]
            x0 = min(prev["x"] - prev["width"] / 2, c["x"] - c["width"] / 2)
            x1 = max(prev["x"] + prev["width"] / 2, c["x"] + c["width"] / 2)
            z0 = min(prev["z"] - prev["depth"] / 2, c["z"] - c["depth"] / 2)
            z1 = max(prev["z"] + prev["depth"] / 2, c["z"] + c["depth"] / 2)
            prev.update({"x": round((x0 + x1) / 2, 2), "z": round((z0 + z1) / 2, 2), "width": round(x1 - x0, 2), "depth": round(z1 - z0, 2),
                         "length": max(prev["length"], c["length"])})
            continue
        merged.append(c)
    out = []
    for i, c in enumerate(merged):
        out.append({"id": f"x{i + 1}", "s": c["s"], "x": c["x"], "z": c["z"], "width": c["width"], "depth": c["depth"], "length": c["length"]})
    return out


def closing_ok(ground, m, box):
    """Like NavStates.Validate: closing the crossing's box keeps the anchors joined and seals at most 6 open cells."""
    from collections import deque
    g = ground.g
    shut = set()
    ground.block(box["x"], box["z"], box["width"], box["depth"], shut)

    def label(extra):
        seen = {}
        n = 0
        for gz in range(g.nz):
            for gx in range(g.nx):
                if (gx, gz) in seen or (gx, gz) in extra or not ground.open(gx, gz):
                    continue
                n += 1
                seen[(gx, gz)] = n
                q = deque([(gx, gz)])
                while q:
                    x, z = q.popleft()
                    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        k = (x + dx, z + dz)
                        if k in seen or k in extra or not ground.open(*k):
                            continue
                        seen[k] = n
                        q.append(k)
        return seen

    before = label(set())
    after = label(shut)
    anchors = [(t["x"], t["z"]) for t in m["teams"]] + [(p["x"], p["z"]) for p in m.get("points", [])]
    cells = [g.cell(x, z) for x, z in anchors]
    home_before = [before.get(c) for c in cells]
    home_after = [after.get(c) for c in cells]
    for i in range(len(cells)):
        for j in range(i + 1, len(cells)):
            if home_before[i] and home_before[i] == home_before[j] and home_after[i] != home_after[j]:
                return False, f"cuts anchor {anchors[i]} from {anchors[j]}"
    main_after = home_after[0]
    main_before = home_before[0]
    sealed = sum(1 for k, r in before.items() if r == main_before and k not in shut and after.get(k) != main_after)
    if sealed > 6:
        return False, f"seals {sealed} cells"
    return True, ""


def rail(ground, m, rid, kind, inner, gates, problems, name, required=True):
    """A RailSpline's data from its points inside the map: the portal end(s) added, corners rounded, measured, checked."""
    pts = list(inner)
    if gates in ("first", "both"):
        pts = [extend(pts[1], pts[0], ground.half)] + pts
    if gates == "both":
        pts = pts + [extend(pts[-2], pts[-1], ground.half)]
    pts = rounded(polyline(pts))
    at = measured(pts)
    stretch = play_stretch(ground, pts, at, gates)
    if stretch is None:
        problems.append(f"{name}: rail {rid} never comes inside the play area")
        return None
    lo, hi = stretch
    bad = blocked_on(ground, pts, at, lo, hi)
    if bad:
        if required:
            problems.append(f"{name}: rail {rid}: blocking props on its band at s = {bad[:6]}")
        return None
    xs = crossings(m, pts, at, lo, hi)
    for c in xs:
        ok, why = closing_ok(ground, m, c)
        if not ok:
            # Its barriers would cut the ground (a camp's drop zone on it): it warns, but never closes its ground.
            c["closes"] = False
            print(f"{name}: rail {rid} crossing {c['id']}: closing it {why}: it only warns")
    return {"id": rid, "kind": kind, "points": [v for p in pts for v in p], "playFrom": round(lo, 2), "playTo": round(hi, 2), "crossings": xs}


def siding(ground):
    """Rust Yard's siding: from Gungnir's spot west while the band stays clear (at most SIDING_WEST m)."""
    x0, z = 132.0, 11.25
    x = x0
    while x0 - x < SIDING_WEST and ground.band_clear(x - 1.0, z, 1.0, 0.0):
        x -= 1.0
    return [(140.0, z), (round(x, 2), z)]


def foundry_line(ground):
    """The longest clear straight run in from the north or east edge of Foundry (in the enemy's half), FOUNDRY_MIN..MAX m."""
    best = None
    for c in range(-120, 121, 2):
        for axis in ("north", "east"):
            if axis == "north":
                start, step = (float(c), ground.half), (0.0, -1.0)
            else:
                start, step = (ground.half, float(c)), (-1.0, 0.0)
            length, entered = 0, None
            for k in range(int(ground.half * 2)):
                x, z = start[0] + step[0] * k, start[1] + step[1] * k
                if entered is None:
                    if ground.inside(x, z) and ground.band_clear(x, z, step[0], step[1]):
                        entered = k
                    continue
                if not ground.inside(x, z) or not ground.band_clear(x, z, step[0], step[1]) or k - entered >= FOUNDRY_MAX:
                    break
                length = k - entered
            if entered is None or length < FOUNDRY_MIN:
                continue
            mx, mz = start[0] + step[0] * (entered + length / 2), start[1] + step[1] * (entered + length / 2)
            if mx + mz <= 0:
                continue
            key = (length, -abs(c - 24), axis)
            if best is None or key > best[0]:
                first = (start[0] + step[0] * entered, start[1] + step[1] * entered)
                end = (start[0] + step[0] * (entered + length), start[1] + step[1] * (entered + length))
                best = (key, [(round(first[0], 2), round(first[1], 2)), (round(end[0], 2), round(end[1], 2))])
    return best[1] if best else None


def rails_for(bf, variant, m, props, problems, name):
    ground = Ground(m, props)
    out = []
    for rid, inner, gates in LINES.get(bf, []):
        if bf == "rustyard":
            inner = siding(ground)
        r = rail(ground, m, rid, "line", inner, gates, problems, name, required=variant != "siege")
        if r:
            out.append(r)
        elif variant == "siege":
            print(f"{name}: rail {rid} left out (its band is not clear in the Siege version)")
    # Foundry's own line, but not beside the Siege version's fortress line (they would run side by side).
    if bf == FOUNDRY and not ((m.get("fortress") or {}).get("arrival") or {}).get("kind") == "rail":
        inner = foundry_line(ground)
        if inner:
            r = rail(ground, m, "works", "line", inner, "first", problems, name, required=False)
            if r:
                out.append(r)
        else:
            problems.append(f"{name}: no clear straight run for Foundry's line")
    arrival = (m.get("fortress") or {}).get("arrival")
    if arrival and arrival.get("kind") == "rail":
        flat = arrival["path"]
        pts = rounded(polyline(list(zip(flat[0::2], flat[1::2]))))
        at = measured(pts)
        stretch = play_stretch(ground, pts, at, "first")
        if stretch is None:
            problems.append(f"{name}: the fortress line never comes inside the play area")
        else:
            lo, hi = stretch
            bad = blocked_on(ground, pts, at, lo, hi)
            # The line's last metres may run into the terrain past the train's stop (its front stands 12.5 m short of the end).
            stop = at[-1] - 12.5
            if bad and min(bad) > stop + 1.0:
                print(f"{name}: the fortress line stops at s = {min(bad) - 1.0:.1f} (terrain on its last metres)")
                hi = min(bad) - 1.0
                bad = []
            if bad:
                problems.append(f"{name}: the fortress line: blocking props on its band at s = {bad[:6]}")
            xs = crossings(m, pts, at, lo, hi)
            for c in xs:
                ok, why = closing_ok(ground, m, c)
                if not ok:
                    c["closes"] = False
                    print(f"{name}: siege_line crossing {c['id']}: closing it {why}: it only warns")
            out.append({"id": "siege_line", "kind": "siege", "points": [v for p in pts for v in p], "playFrom": round(lo, 2),
                        "playTo": round(hi, 2), "crossings": xs})
    return out


# ------------------------------------------------------------------ writing


def rewrite(path, fields):
    """Puts each field on its own line before "boundary" (or before "props"), replacing an earlier run's."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    keys = [f'  "{k}":' for k in fields]
    lines = [l for l in lines if not any(l.startswith(k) for k in keys)]
    out = []
    for l in lines:
        if out and l == "" and out[-1] == "":
            continue
        out.append(l)
    lines = out
    at = next((i for i, l in enumerate(lines) if l.startswith('  "boundary":')), None)
    if at is None:
        at = lines.index('  "props": [')
    new = []
    for k, v in fields.items():
        if v is None:
            continue
        new += [f'  "{k}": {json.dumps(v, separators=(", ", ": "))},', ""]
    lines[at:at] = new
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def main(argv):
    check_only = "--check" in argv
    only = [a for a in argv if not a.startswith("--")]
    problems = []
    written = 0
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import check_access
    props, _, _ = check_access.balance()
    for bf in BATTLEFIELDS:
        if only and bf not in only:
            continue
        for variant in VARIANTS:
            path = os.path.join(MAPS, f"{bf}_{variant}.json")
            if not os.path.exists(path):
                continue
            m = load(path)
            name = f"{bf}_{variant}"
            half = m["size"] / 2
            fields = {}
            if "sea" in m:
                sea = Sea(m["sea"])
                graph = sea_graph(sea, half)
                problems += check_sea(name, graph, sea, half)
                fields["seaRoutes"] = graph
                holds = sum(1 for n in graph["nodes"] if n["kind"] == "holding")
                print(f"{name}: sea routes, {len(graph['nodes'])} nodes ({holds} holding), {len(graph['segments'])} segments")
            rails = rails_for(bf, variant, m, props, problems, name)
            if rails:
                fields["rails"] = rails
                for r in rails:
                    print(f"{name}: rail {r['id']} ({r['kind']}), play {r['playFrom']}-{r['playTo']} m, {len(r['crossings'])} crossings")
            if not fields:
                continue
            if not check_only:
                rewrite(path, fields)
                written += 1
    for p in problems:
        print("PROBLEM", p)
    print(f"{written} map files written, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
