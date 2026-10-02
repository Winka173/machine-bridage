"""Prompt 30 L8: the static map audit (sheet "Đo bản đồ"). Read-only: it never changes a map.

    python Tools/audit/map_audit.py              # every map file
    python Tools/audit/map_audit.py ashfield     # the files of one battlefield

Writes Docs/checks/map_audit.md and Docs/checks/map_audit.csv. The ground is the Sim's 2 m navigation grid as
build_maps.py builds it (blocking props grown by 1.5 m, fixed defences, outside the outline blocked); paths are
8-way shortest paths on it; sightlines are rays over a fire-blocking grid (props that block fire), 16 fixed
directions from a fixed sample of cells, at one eye height (the ground is flat). Everything is deterministic.

What a static measure cannot show (the sheet's own list): win rates, real traffic jams, flow, real artillery value,
how the AI picks lanes, how long fights last, performance. Symmetric files (_conquest, _sandbox) are compared side
against side; asymmetric ones (_siege, _long) are reported by role, never as 1:1.
"""
from __future__ import annotations

import csv
import glob
import heapq
import json
import math
import os
import re
import statistics
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MAPS = os.path.join(ROOT, "Assets", "MachineBrigade", "Resources", "Data", "maps")
OUT_MD = os.path.join(ROOT, "Docs", "checks", "map_audit.md")
OUT_CSV = os.path.join(ROOT, "Docs", "checks", "map_audit.csv")
CELL, CLEARANCE = 2.0, 1.5
REF_WIDTH = 3.07           # main_battle_tank's width (m): the reference vehicle
TANK_RANGE = 32.0          # gun_120mm's range (m)
ART_RANGE = 120.0          # a long gun's reach for the indirect-fire envelope (counter-battery range)
SQRT2 = math.sqrt(2)
# Prompt 33 L3: an ordinary vehicle's speed on each terrain tag (ROAD +20 %, ROUGH -15 %, FOREST -25 %, SHALLOW_WATER
# -50 %), the cost of a cell = 1 / speed; "--no-terrain" measures as before (plain distance).
TERRAIN = "--no-terrain" not in sys.argv
TERRAIN_COST = {"ROAD": 1 / 1.2, "ROUGH": 1 / 0.85, "FOREST": 1 / 0.75, "SHALLOW_WATER": 1 / 0.5}
DIRS = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, SQRT2), (1, -1, SQRT2), (-1, 1, SQRT2), (-1, -1, SQRT2)]


def strip(text):
    return re.sub(r"^\s*//.*$", "", text, flags=re.M)


def balance():
    sys.path.insert(0, os.path.join(ROOT, "Tools", "ai"))
    import export_applied_xlsx as E  # noqa: E402
    return E.balance()


class Grid:
    def __init__(self, data, props, vehicles):
        b = data.get("bounds")
        half = data["size"] / 2
        self.x0, self.z0, self.x1, self.z1 = (b if b else (-half, -half, half, half))
        self.nx, self.nz = int((self.x1 - self.x0) / CELL), int((self.z1 - self.z0) / CELL)
        self.walk = [[True] * self.nx for _ in range(self.nz)]
        self.fire = [[False] * self.nx for _ in range(self.nz)]   # blocks a shot
        # Prompt 33 L3: the terrain tags' static cost (the time to cross a cell at an ordinary vehicle's speed there, as
        # TerrainRules.PathCost in the Sim): paths become travel times in metres at normal speed.
        self.cost = [[1.0] * self.nx for _ in range(self.nz)]
        if TERRAIN and data.get("terrain"):
            for zone in data["terrain"].get("zones", []):
                c = TERRAIN_COST.get(zone["tag"], 1.0)
                r = zone["rects"]
                for i in range(0, len(r), 4):
                    for gz in range(max(0, int(round((r[i + 1] - self.z0) / CELL))), min(self.nz, int(round((r[i + 3] - self.z0) / CELL)))):
                        for gx in range(max(0, int(round((r[i] - self.x0) / CELL))), min(self.nx, int(round((r[i + 2] - self.x0) / CELL)))):
                            self.cost[gz][gx] = c
        for p in data["props"]:
            d = props.get(p["def"])
            if not d or not d.get("blocks", False):
                continue
            w, dep = d["width"], d["depth"]
            if p.get("rot", 0) % 180 == 90:
                w, dep = dep, w
            elif p.get("rot", 0) % 90:
                w = dep = max(w, dep)
            fire = d.get("blocksFire", True)
            self.block(p["x"] - w / 2, p["z"] - dep / 2, p["x"] + w / 2, p["z"] + dep / 2, fire)
        for u in data.get("units", []):
            v = vehicles.get(u["def"])
            if v and v.get("static"):
                side = 0.8 * max(v.get("length", 4), v.get("width", 4))
                self.block(u["x"] - side / 2, u["z"] - side / 2, u["x"] + side / 2, u["z"] + side / 2, True)
        flat = data.get("boundary") or []
        poly = list(zip(flat[0::2], flat[1::2]))
        if poly:
            for gz in range(self.nz):
                cz = self.z0 + (gz + 0.5) * CELL
                xs = []
                for i in range(len(poly)):
                    (ax, az), (bx, bz) = poly[i], poly[(i + 1) % len(poly)]
                    if (az > cz) != (bz > cz):
                        xs.append(ax + (cz - az) * (bx - ax) / (bz - az))
                xs.sort()
                inside = [False] * self.nx
                for a, c in zip(xs[0::2], xs[1::2]):
                    for gx in range(max(0, int((a - self.x0) / CELL)), min(self.nx, int((c - self.x0) / CELL) + 1)):
                        cx = self.x0 + (gx + 0.5) * CELL
                        if a <= cx <= c:
                            inside[gx] = True
                for gx in range(self.nx):
                    if not inside[gx]:
                        self.walk[gz][gx] = False

    def block(self, x0, z0, x1, z1, fire):
        a0 = int(math.floor((x0 - CLEARANCE - self.x0) / CELL))
        a1 = int(math.floor((x1 + CLEARANCE - 1e-4 - self.x0) / CELL))
        b0 = int(math.floor((z0 - CLEARANCE - self.z0) / CELL))
        b1 = int(math.floor((z1 + CLEARANCE - 1e-4 - self.z0) / CELL))
        for gz in range(max(0, b0), min(self.nz, b1 + 1)):
            for gx in range(max(0, a0), min(self.nx, a1 + 1)):
                self.walk[gz][gx] = False
        if fire:
            for gz in range(max(0, int((z0 - self.z0) / CELL)), min(self.nz, int((z1 - self.z0) / CELL) + 1)):
                for gx in range(max(0, int((x0 - self.x0) / CELL)), min(self.nx, int((x1 - self.x0) / CELL) + 1)):
                    self.fire[gz][gx] = True

    def cell(self, x, z):
        return min(self.nx - 1, max(0, int((x - self.x0) / CELL))), min(self.nz - 1, max(0, int((z - self.z0) / CELL)))

    def open_near(self, x, z, reach=12):
        gx, gz = self.cell(x, z)
        best = None
        for r in range(reach):
            for dz in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if max(abs(dx), abs(dz)) != r:
                        continue
                    a, b = gx + dx, gz + dz
                    if 0 <= a < self.nx and 0 <= b < self.nz and self.walk[b][a]:
                        d = dx * dx + dz * dz
                        if best is None or d < best[0]:
                            best = (d, a, b)
            if best:
                return best[1], best[2]
        return None

    def dijkstra(self, start, penalty=None):
        dist = {start: 0.0}
        parent = {start: None}
        heap = [(0.0, start)]
        while heap:
            d, (x, z) = heapq.heappop(heap)
            if d > dist[(x, z)]:
                continue
            for dx, dz, c in DIRS:
                a, b = x + dx, z + dz
                if not (0 <= a < self.nx and 0 <= b < self.nz) or not self.walk[b][a]:
                    continue
                if dx and dz and not (self.walk[z][a] and self.walk[b][x]):
                    continue
                nd = d + c * CELL * self.cost[b][a] + (penalty.get((a, b), 0.0) if penalty else 0.0)
                if nd < dist.get((a, b), 1e18):
                    dist[(a, b)] = nd
                    parent[(a, b)] = (x, z)
                    heapq.heappush(heap, (nd, (a, b)))
        return dist, parent

    def regions(self):
        seen = [[False] * self.nx for _ in range(self.nz)]
        sizes = []
        for z in range(self.nz):
            for x in range(self.nx):
                if not self.walk[z][x] or seen[z][x]:
                    continue
                stack, n = [(x, z)], 0
                seen[z][x] = True
                while stack:
                    a, b = stack.pop()
                    n += 1
                    for dx, dz, _ in DIRS[:4]:
                        c, d = a + dx, b + dz
                        if 0 <= c < self.nx and 0 <= d < self.nz and self.walk[d][c] and not seen[d][c]:
                            seen[d][c] = True
                            stack.append((c, d))
                sizes.append(n)
        sizes.sort(reverse=True)
        return sizes

    def clearance(self):
        """Distance (cells) from each walkable cell to the nearest blocked one (4-way BFS)."""
        INF = 10 ** 6
        dist = [[INF] * self.nx for _ in range(self.nz)]
        q = []
        for z in range(self.nz):
            for x in range(self.nx):
                if not self.walk[z][x]:
                    dist[z][x] = 0
                    q.append((x, z))
        i = 0
        while i < len(q):
            x, z = q[i]
            i += 1
            for dx, dz, _ in DIRS[:4]:
                a, b = x + dx, z + dz
                if 0 <= a < self.nx and 0 <= b < self.nz and dist[b][a] > dist[z][x] + 1:
                    dist[b][a] = dist[z][x] + 1
                    q.append((a, b))
        return dist

    def ray(self, x, z, ux, uz, cap=150.0):
        t = CELL
        while t < cap:
            a, b = int((x + ux * t - self.x0) / CELL), int((z + uz * t - self.z0) / CELL)
            if not (0 <= a < self.nx and 0 <= b < self.nz) or self.fire[b][a] or not self.walk[b][a] and self.fire[b][a]:
                return t
            t += CELL
        return cap


def local_width(clear, x, z, nx, nz):
    """The corridor's width (m) round a path cell: the widest clearance within 6 m (a shortest path hugs walls),
    as cells across, plus the blockers' grown margin on both sides."""
    c = 0
    for dz in range(-3, 4):
        for dx in range(-3, 4):
            a, b = x + dx, z + dz
            if 0 <= a < nx and 0 <= b < nz:
                c = max(c, clear[b][a])
    return max(0, 2 * c - 1) * CELL + 2 * CLEARANCE


def path(parent, end):
    out = []
    while end is not None:
        out.append(end)
        end = parent.get(end)
    return out[::-1]


def pct(values, p):
    if not values:
        return 0.0
    s = sorted(values)
    return s[min(len(s) - 1, int(p * len(s)))]


def audit(path_file, props, vehicles):
    with open(path_file, encoding="utf-8") as f:
        data = json.loads(strip(f.read()))
    name = os.path.basename(path_file)[:-5]
    symmetric = name.endswith(("_conquest", "_sandbox"))
    g = Grid(data, props, vehicles)
    row = {"map": name, "kind": "symmetric" if symmetric else "asymmetric"}
    flags = []
    sizes = g.regions()
    row["disconnectedNavRegions"] = sum(1 for s in sizes[1:] if s >= 25)
    rallies = [g.open_near(t["x"], t["z"]) for t in data["teams"]]
    targets = [(p["id"], p["x"], p["z"]) for p in data.get("points", [])]
    fort = data.get("fortress")
    if fort and fort.get("hq"):
        targets.append(("hq", fort["hq"][0], fort["hq"][1]))
    maps = [g.dijkstra(r) if r else ({}, {}) for r in rallies]
    unreachable = []
    per_team = [[], []]
    for tid, x, z in targets:
        c = g.open_near(x, z)
        for team, (dist, _) in enumerate(maps[:2]):
            if c is None or c not in dist:
                unreachable.append(f"{tid}<-{team}")
            else:
                per_team[team].append(dist[c])
    row["objectiveReachability"] = "ok" if not unreachable else "; ".join(unreachable)
    if row["disconnectedNavRegions"] or unreachable:
        flags.append("RED connectivity")
    row["pathToObjective0"] = round(statistics.median(per_team[0]), 1) if per_team[0] else ""
    row["pathToObjective1"] = round(statistics.median(per_team[1]), 1) if per_team[1] else ""
    if symmetric and per_team[0] and per_team[1]:
        m0, m1 = statistics.median(per_team[0]), statistics.median(per_team[1])
        delta = abs(m0 - m1) / max(1.0, (m0 + m1) / 2)
        row["medianPathDelta"] = f"{delta:.1%}"
        if delta > 0.15:
            flags.append("RED path delta")
        elif delta > 0.10:
            flags.append("YELLOW path delta")
    else:
        row["medianPathDelta"] = "by role"
    between = maps[0][0].get(rallies[1]) if len(rallies) > 1 and rallies[1] else None
    row["firstContactDistance"] = round(between / 2, 1) if between else ""
    cells = [g.open_near(x, z) for _, x, z in targets]
    o2o = []
    for i in range(len(cells)):
        for j in range(i + 1, len(cells)):
            if cells[i] and cells[j]:
                d, _ = g.dijkstra(cells[i])
                if cells[j] in d:
                    o2o.append(d[cells[j]])
    row["objectiveToObjectiveDistance"] = round(min(o2o), 1) if o2o else ""
    # Lanes: shortest path camp to camp, penalise its corridor, search again; three more times.
    lanes = []
    clear = g.clearance()
    if between:
        penalty = {}
        for _ in range(4):
            dist, parent = g.dijkstra(rallies[0], penalty)
            if rallies[1] not in dist:
                break
            p = path(parent, rallies[1])
            near = set()
            for (x, z) in p:
                for dx in range(-2, 3):
                    for dz in range(-2, 3):
                        near.add((x + dx, z + dz))
            new = True
            for other in lanes:
                shared = sum(1 for c in p if c in other["near"])
                if shared > 0.5 * len(p):
                    new = False
            room = pct([local_width(clear, x, z, g.nx, g.nz) for x, z in p], 0.1)
            if new and room >= 2 * REF_WIDTH:
                lanes.append({"cells": p, "near": near, "room": room})
            for c in near:
                penalty[c] = penalty.get(c, 0.0) + 25.0
    row["independentLaneCount"] = len(lanes)
    if symmetric and len(lanes) < 2:
        flags.append("RED one lane")
    # Chokes along the lanes: runs of cells narrower than 2.5 reference widths.
    choke_cells = []
    for lane in lanes:
        for (x, z) in lane["cells"]:
            if local_width(clear, x, z, g.nx, g.nz) < 2.5 * REF_WIDTH:
                choke_cells.append((x, z))
    mandatory = 0
    if lanes:
        groups = {}
        for (x, z) in choke_cells:
            groups.setdefault((x // 5, z // 5), set()).add((x, z))
        for key, cs in groups.items():
            crossing = sum(1 for lane in lanes if any(c in lane["near"] for c in cs))
            if crossing > 0.6 * len(lanes):
                mandatory += 1
        row["mandatoryChokeCount"] = mandatory
        row["optionalChokeCount"] = max(0, len(groups) - mandatory)
        row["corridorWidthP10"] = round(pct([local_width(clear, x, z, g.nx, g.nz) for lane in lanes for x, z in lane["cells"]], 0.1), 1)
    else:
        row["mandatoryChokeCount"] = row["optionalChokeCount"] = row["corridorWidthP10"] = ""
    # Sightlines: every 6th cell, 16 directions.
    rays, exposure = [], []
    dirs16 = [(math.cos(k * math.pi / 8), math.sin(k * math.pi / 8)) for k in range(16)]
    for z in range(0, g.nz, 6):
        for x in range(0, g.nx, 6):
            if not g.walk[z][x]:
                continue
            cx, cz = g.x0 + (x + 0.5) * CELL, g.z0 + (z + 0.5) * CELL
            rays += [g.ray(cx, cz, ux, uz) for ux, uz in dirs16]
    for _, x, z in targets:
        exposure += [g.ray(x, z, ux, uz) for ux, uz in dirs16]
    row["sightlineP95"] = round(pct(rays, 0.95), 1)
    row["objectiveExposureP95"] = round(pct(exposure, 0.95), 1) if exposure else ""
    row["longRangeExposureArea"] = f"{sum(1 for r in rays if r > 2 * TANK_RANGE) / max(1, len(rays)):.0%}"
    if row["sightlineP95"] > TANK_RANGE:
        flags.append("YELLOW sightline")
    # Fire: an objective within a tank gun's reach of a camp, and the share of the map under a long gun from a camp.
    row["directFireCoverage"] = "exposed" if any(math.hypot(x - t["x"], z - t["z"]) < TANK_RANGE + 40 for _, x, z in targets for t in data["teams"]) else "-"
    walk_cells = [(x, z) for z in range(g.nz) for x in range(g.nx) if g.walk[z][x]]
    covered = []
    for t in data["teams"]:
        n = sum(1 for x, z in walk_cells if math.hypot(g.x0 + (x + 0.5) * CELL - t["x"], g.z0 + (z + 0.5) * CELL - t["z"]) < ART_RANGE)
        covered.append(f"{n / max(1, len(walk_cells)):.0%}")
    row["indirectFireGeometricEnvelope"] = "/".join(covered)
    # Drop zones.
    areas, exits, threats = [], [], []
    statics = [(u, vehicles.get(u["def"], {})) for u in data.get("units", [])]
    for team, t in enumerate(data["teams"][:2]):
        area = sum(1 for x, z in walk_cells if math.hypot(g.x0 + (x + 0.5) * CELL - t["x"], g.z0 + (z + 0.5) * CELL - t["z"]) < 20) * CELL * CELL
        areas.append(round(area))
        ring = []
        for k in range(72):
            a = k * 2 * math.pi / 72
            gx, gz = g.cell(t["x"] + 30 * math.cos(a), t["z"] + 30 * math.sin(a))
            ring.append(g.walk[gz][gx])
        runs = sum(1 for k in range(72) if ring[k] and not ring[k - 1])
        exits.append(runs if not all(ring) else "open")
        near = [math.hypot(u["x"] - t["x"], u["z"] - t["z"]) for u, v in statics if u.get("team") not in (team, None) and v.get("static")]
        threats.append(round(min(near), 1) if near else "")
        if near and min(near) < 40:
            flags.append(f"RED drop zone {team} in tower range")
    row["usableDropArea"] = "/".join(map(str, areas))
    row["exitCount"] = "/".join(map(str, exits))
    if symmetric and any(e != "open" and e < 2 for e in exits):
        flags.append("YELLOW exits")
    row["staticThreatDistance"] = "/".join(map(str, threats))
    # Long battlefields: the defence's layers and the defender's way back.
    rings = data.get("siegeRings")
    row["defensiveLayerSpacing"] = round(abs(rings[0] - rings[1]), 1) if rings and len(rings) > 1 else ""
    if fort and fort.get("hq") and len(rallies) > 1 and rallies[1]:
        hq = g.open_near(*fort["hq"])
        d, _ = g.dijkstra(rallies[1])
        row["fallbackRouteLength"] = round(d.get(hq, 0.0), 1) if hq else ""
        row["reinforcementTravelProxy"] = f"{d.get(hq, 0.0) / 6.5:.0f} s" if hq else ""
    else:
        row["fallbackRouteLength"] = row["reinforcementTravelProxy"] = ""
    # Neutral sites: their value to each side by path distance.
    sites = data.get("neutrals", [])
    if sites and len(maps) > 1:
        value = [0.0, 0.0]
        for s in sites:
            c = g.open_near(s["x"], s["z"])
            for team in range(2):
                d = maps[team][0].get(c)
                if d is not None:
                    value[team] += 1.0 / (1.0 + d / 100.0)
        delta = abs(value[0] - value[1]) / max(1e-6, (value[0] + value[1]) / 2)
        row["neutralValueDelta"] = f"{delta:.0%}"
        if symmetric and delta > 0.20:
            flags.append("RED neutral delta")
        elif symmetric and delta > 0.10:
            flags.append("YELLOW neutral delta")
    else:
        row["neutralValueDelta"] = "-"
    row["flags"] = "; ".join(flags) if flags else "GREEN"
    return row


COLUMNS = ["map", "kind", "flags", "disconnectedNavRegions", "objectiveReachability", "pathToObjective0", "pathToObjective1",
           "medianPathDelta", "firstContactDistance", "objectiveToObjectiveDistance", "independentLaneCount",
           "mandatoryChokeCount", "optionalChokeCount", "corridorWidthP10", "sightlineP95", "objectiveExposureP95",
           "longRangeExposureArea", "directFireCoverage", "indirectFireGeometricEnvelope", "usableDropArea", "exitCount",
           "staticThreatDistance", "defensiveLayerSpacing", "fallbackRouteLength", "reinforcementTravelProxy",
           "neutralValueDelta"]


def main(only=()):
    b = balance()
    props = {p["id"]: p for p in b["props"]}
    vehicles = {v["id"]: v for v in b["vehicles"]}
    files = sorted(glob.glob(os.path.join(MAPS, "*.json")))
    if only:
        files = [f for f in files if any(os.path.basename(f).startswith(o) for o in only)]
    rows = []
    for f in files:
        rows.append(audit(f, props, vehicles))
        print(rows[-1]["map"], rows[-1]["flags"], flush=True)
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in COLUMNS})
    red = [r for r in rows if "RED" in r["flags"]]
    yellow = [r for r in rows if "RED" not in r["flags"] and "YELLOW" in r["flags"]]
    out = ["# Map audit (prompt 30 L8, static, read-only)", "",
           "Generated by `Tools/audit/map_audit.py` from the map files; the full table is `map_audit.csv`. Nothing was "
           "changed and nothing was simulated.", "",
           "**Limits of a static measure:** it does not show win rates, real traffic jams or flow, the real value of "
           "artillery (spotting, minimum ranges, the AI), how the AI picks lanes, how long fights last, or performance. "
           "Paths are on the 2 m navigation grid, sightlines on a flat ground with one eye height. Symmetric versions "
           "(Conquest, Sandbox) are compared side against side; Siege and the long battlefields are reported by role.", "",
           f"{len(rows)} files: {len(red)} RED, {len(yellow)} YELLOW, {len(rows) - len(red) - len(yellow)} GREEN.", "",
           "Thresholds: medianPathDelta ≤ 10 % GREEN, 10-15 % YELLOW, > 15 % RED (symmetric); fewer than 2 lanes RED "
           f"(symmetric); a drop zone within 40 m of an enemy fixed defence RED; sightline P95 above the tank gun's "
           f"{TANK_RANGE:.0f} m YELLOW (information); neutralValueDelta > 10 % YELLOW, > 20 % RED (symmetric).", "",
           "| Map | Kind | Flags | Lanes | Path delta | Chokes (mand./opt.) | Sightline P95 | Exits | Neutral Δ |",
           "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['map']} | {r['kind']} | {r['flags']} | {r['independentLaneCount']} | {r['medianPathDelta']} | "
                   f"{r['mandatoryChokeCount']}/{r['optionalChokeCount']} | {r['sightlineP95']} | {r['exitCount']} | {r['neutralValueDelta']} |")
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out) + "\n")
    print(f"{len(rows)} maps: {len(red)} RED, {len(yellow)} YELLOW")


if __name__ == "__main__":
    main([a for a in sys.argv[1:] if not a.startswith("--")])
