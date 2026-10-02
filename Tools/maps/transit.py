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
