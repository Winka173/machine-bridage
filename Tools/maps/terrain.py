"""Prompt 33 L3: terrain tags, landmarks and the asymmetry note on the generated map files.

    python Tools/maps/terrain.py            # every map file (_conquest, _sandbox, _siege, _long)
    python Tools/maps/terrain.py --check    # only check, write nothing (exit 1 on a problem)
    python Tools/maps/terrain.py ironport   # one battlefield's files

Run it after Tools/maps/edges.py. It writes, each on its own line before "boundary" (replacing an earlier run's):

- "terrain" {"cell": 2, "zones": [{"tag", "rects": [x0, z0, x1, z1, ...]}]}: the static terrain tags of the Sim's 2 m
  navigation cells inside the outline (NORMAL is the rest). A cell takes the first that holds, in this order:
  - SHALLOW_WATER: its centre on a ford tile (river_ford, the walkable water);
  - ROAD: its centre within half a road's width of the road's line (map "roads"), or on a road bridge (bridge_road);
  - FOREST: at least FOREST_TREES trees (tree, palm, jungle trees, bamboo, fern) within FOREST_REACH m of its centre;
  - ROUGH: within ROUGH_REACH m of rough ground (craters, boulders, rocks, mounds, crash debris, ruins) or, on an urban
    map, within URBAN_REACH m of a building's footprint (rubble at the city's feet; the cover is still the buildings').
  The zones are the tag's cells merged into rectangles (no two overlap, none empty; a tag's cluster of fewer than
  MIN_CELLS cells is dropped). On the versus files (_conquest, _sandbox) a cell keeps its tag only where its twin
  across the middle (the half-turn between the camps) has the same: the scenery is not placed symmetrically, the tags are.
- "landmarks": 2-3 per battlefield, each {"id", "kind", "x", "z", "name": {"en", "vi"}, "aliases"}: something seen from
  far off (a lighthouse, a water tower, a church, a crane ...), at the prop of LANDMARKS' kind nearest the hint, else at
  the hint (then "model" names what the view should stand there). "aliases" are the words the prompt 30 dialogue uses
  for it, so a line can be matched to the place.
- "asymmetry" on the role-asymmetric files (_siege, _long): {"intended": true, "reason"}. The campaign plays the shared
  files; no campaign map is asymmetric by itself in this pass (prompt 30's audit keeps the symmetric files symmetric).
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_access as ca  # noqa: E402
import transit  # noqa: E402

MAPS = transit.MAPS
VARIANTS = ["conquest", "sandbox", "siege", "long"]
SYMMETRIC = {"conquest", "sandbox"}   # the versus files (prompt 30's audit compares their sides 1:1)
CELL = 2.0
TAGS = ["ROAD", "ROUGH", "FOREST", "SHALLOW_WATER"]
TREES = {"tree", "palm", "jungle_tree_a", "jungle_tree_b", "jungle_tree_c", "bamboo_clump", "fern_bush"}
ROUGH_PROPS = {"crater_large", "boulders", "snow_rock", "basalt_rock_a", "basalt_rock_b", "basalt_rock_c", "dirt_mound",
               "crash_debris", "ruin", "ruin_house", "ruin_tower", "temple_ruin"}
URBAN_MAPS = {"capital", "foundry", "metrocity", "veyra_old_quarter"}
FOREST_TREES = 3
FOREST_REACH = 9.0
ROUGH_REACH = 4.0
URBAN_REACH = 5.0
URBAN_MIN_SIDE = 6.0     # a blocking prop at least this wide is a building
MIN_CELLS = 4

# Landmarks: (id, kind, prop def or None, hint (x, z) or point id, en, vi, aliases from the prompt 30 dialogue, model).
LANDMARKS = {
    "ashfield": [("wt_west", "water_tower", "water_tower", (-52, 119), "West depot water tower", "Tháp nước kho phía tây", ["the depot"], None),
                 ("wt_east", "water_tower", "water_tower", (52, -119), "East depot water tower", "Tháp nước kho phía đông", ["the depot"], None),
                 ("town_tower", "ruin_tower", "ruin_tower", (10, 58), "Old town tower", "Tháp cổ thị trấn", ["the square"], None)],
    "borderbridge": [("great_bridge", "bridge", None, "town", "The great bridge", "Cây cầu lớn", ["the bridge"], None),
                     ("village_church", "church", "church", (-58, 114), "Border village church", "Nhà thờ làng biên giới", [], None),
                     ("bridge_lights", "floodlight", "floodlight_mast", (6, -33), "Bridge floodlights", "Đèn pha đầu cầu", [], None)],
    "capital": [("palace", "palace", None, "town", "The palace", "Dinh thự", ["the palace", "the square"], "palace_dome"),
                ("station", "station", None, "east", "The station", "Nhà ga", ["the station"], "station_clock"),
                ("ministry_tower", "skyscraper", "skyscraper", (-15, 74), "Ministry tower", "Tòa tháp Bộ", [], None)],
    "coralisles": [("lighthouse", "lighthouse", None, "town", "The lighthouse", "Ngọn hải đăng", ["the lighthouse"], "lighthouse"),
                   ("west_watch", "watchtower", "watchtower", (-76, 72), "West isle watchtower", "Tháp canh đảo tây", [], None),
                   ("east_watch", "watchtower", "watchtower", (76, -72), "East isle watchtower", "Tháp canh đảo đông", [], None)],
    "dunebreak": [("refinery", "refinery", "refinery_tower", (-22, 11), "The refinery", "Nhà máy lọc dầu", ["the refinery"], None),
                  ("desert_mast", "radio_mast", "radio_mast", (138, 90), "Desert radio mast", "Cột vô tuyến sa mạc", [], None),
                  ("north_radar", "radar", "radar_dome", (8, 72), "North radar", "Ra-đa phía bắc", [], None)],
    "emberridge": [("geothermal", "plant", None, "town", "Geothermal plant", "Nhà máy địa nhiệt", [], "cooling_tower"),
                   ("spires", "spire", "obsidian_spire", (-41, 64), "Obsidian spires", "Cột đá vỏ chai", [], None),
                   ("ridge", "cliff", "volcanic_cliff", (74, -15), "The ridge", "Sườn núi lửa", ["the ridge"], None)],
    "foundry": [("stacks", "chimney", "refinery_tower", (-30, 0), "Casting hall stacks", "Ống khói xưởng đúc", ["the foundry"], None),
                ("north_works", "factory", "factory", (0, 80), "North works hall", "Xưởng phía bắc", [], None),
                ("south_works", "factory", "factory", (0, -80), "South works hall", "Xưởng phía nam", [], None)],
    "frostpeak": [("radar_station", "radar", "radar_station", (-56, 116), "The radar station", "Trạm ra-đa", ["the radar"], None),
                  ("village_church", "church", "church", (26, 75), "Village church", "Nhà thờ làng", ["the village"], None),
                  ("camp_water_tower", "water_tower", "water_tower", (52, -119), "Lumber camp water tower", "Tháp nước trại gỗ", [], None)],
    "greenvale": [("silos", "silo", "silo", (-34, 114), "West farm silos", "Si-lô trại phía tây", ["the silos"], None),
                  ("crossroads_church", "church", "church", (39, 43), "Crossroads church", "Nhà thờ ngã tư", ["the village"], None),
                  ("east_water_tower", "water_tower", "water_tower", (12, -131), "East farm water tower", "Tháp nước trại phía đông", ["the towers"], None)],
    "hydrodam": [("dam", "dam", None, (0, 102), "The dam", "Con đập", ["the dam"], "dam_wall"),
                 ("dam_towers", "water_tower", "water_tower", (-24, 107), "Dam towers", "Tháp đập", [], None),
                 ("power_station", "factory", "factory", (-21, 81), "Power station", "Trạm thủy điện", ["the station"], None)],
    "ironport": [("crane", "crane", "gantry_crane", (-8, 131), "Harbour crane", "Cần cẩu cảng", ["the harbour", "the quay"], None),
                 ("docks", "docks", None, "west", "The docks", "Bến tàu", ["the docks", "the dock"], None),
                 ("yard_water_tower", "water_tower", "water_tower", (60, -60), "Rail yard water tower", "Tháp nước ga hàng", ["the depot"], None)],
    "junglepass": [("temple", "temple", "temple_ruin", (-16, 16), "The temple", "Ngôi đền", ["the temple"], None),
                   ("temple_ford", "ford", "river_ford", (0, 0), "The temple ford", "Khúc cạn đền", ["the ford"], None),
                   ("village_church", "church", None, "west", "West village church", "Nhà thờ làng phía tây", ["the church", "the village"], "church")],
    "landingbeach": [("radar", "radar", "radar_station", (26, 6), "The radar", "Trạm ra-đa", ["the radar"], None),
                     ("village_church", "church", "church", (-22, 106), "Village church", "Nhà thờ làng", [], None),
                     ("bluffs", "cliff", "cliff_a", (-22, -58), "The bluffs", "Vách đá", ["the bluffs", "the beach"], None)],
    "launchsite": [("gantry", "gantry", "gantry_crane", (0, 21), "Launch pad gantry", "Giàn phóng", ["the pad"], None),
                   ("assembly_hangar", "hangar", "hangar", (-80, 84), "Assembly hangar", "Nhà chứa lắp ráp", ["the airfield"], None),
                   ("north_mesa", "mesa", "mesa", (20, 128), "North mesa", "Núi bàn phía bắc", [], None)],
    "lighthousebay": [("lighthouse", "lighthouse", "lighthouse", (34, -34), "The lighthouse", "Ngọn hải đăng", ["the lighthouse"], None),
                      ("old_fort", "fort", "watchtower", (-51, 85), "The old fort", "Pháo đài cũ", ["the fort"], None),
                      ("fishing_village", "village", None, "town", "The fishing village", "Làng chài", ["the village", "the pier"], None)],
    "metrocity": [("north_tower", "skyscraper", "skyscraper", (0, 68), "North tower", "Tòa tháp phía bắc", ["the towers"], None),
                  ("plaza", "plaza", None, "town", "The plaza", "Quảng trường", ["the plaza"], None),
                  ("billboard", "billboard", "billboard", (59, -121), "Parking billboard", "Biển quảng cáo bãi xe", ["the depot"], None)],
    "openpit": [("crusher_crane", "crane", "gantry_crane", (-80, 106), "Crusher crane", "Cần cẩu máy nghiền", ["the depot"], None),
                ("pit", "pit", None, "town", "The pit", "Đáy mỏ", ["the pit"], None),
                ("ore_loadout", "factory", "factory", (102, -102), "Ore loadout", "Trạm bốc quặng", [], None)],
    "orbitalgate": [("array", "radar", "radar_station", (65, 37), "The array", "Dàn ăng-ten", ["the array"], None),
                    ("west_gantry", "gantry", "gantry_crane", (-91, 100), "West pad gantry", "Giàn phóng phía tây", ["the gate"], None),
                    ("landing_field", "field", None, "town", "Landing field", "Bãi đáp", [], None)],
    "redrock": [("caravan_water_tower", "water_tower", "water_tower", (38, -112), "Caravan water tower", "Tháp nước trạm lữ hành", [], None),
                ("red_mesa", "mesa", "mesa", (-71, 22), "Red mesa", "Núi bàn đỏ", ["the ridge"], None),
                ("mine_church", "church", None, "town", "Mine town church", "Nhà thờ thị trấn mỏ", ["the church", "the mine"], "church")],
    "rustyard": [("yard_water_tower", "water_tower", "water_tower", (-112, -48), "Yard water tower", "Tháp nước bãi", [], None),
                 ("foundry", "factory", "factory", (-45, -88), "The foundry", "Xưởng đúc", ["the gate"], None),
                 ("quay_tower", "ruin_tower", "ruin_tower", (38, 126), "Quay ruin tower", "Tháp đổ bến cảng", ["the pier"], None)],
    "saltflat": [("survey_beacon", "beacon", None, "town", "Survey beacon", "Mốc trắc địa", [], "survey_beacon"),
                 ("survey_radar", "radar", "radar_station", (-24, 17), "Survey radar", "Ra-đa trắc địa", ["the pad"], None),
                 ("brine_pumps", "factory", "factory", (62, -118), "Brine pump house", "Trạm bơm nước muối", [], None)],
    "skyhold": [("control_tower", "control_tower", "control_tower", (-24, 29), "Control tower", "Đài kiểm soát", ["the runway"], None),
                ("dish", "radar", "radar_dome", (25, -31), "The dish", "Chảo ra-đa", ["the dish"], None),
                ("west_hangar", "hangar", "hangar", (-30, 100), "West hangar", "Nhà chứa máy bay phía tây", [], None)],
    "swamp": [("sunken_temple", "temple", "temple_ruin", (-12, 12), "Sunken temple", "Đền chìm", [], None),
              ("west_watch", "watchtower", "watchtower", (-74, 74), "West village watchtower", "Tháp canh làng tây", [], None),
              ("swamp_radar", "radar", "radar_dome", (13, 68), "Swamp radar", "Ra-đa đầm lầy", [], None)],
    "veyra_old_quarter": [("cathedral", "church", "church", (0, 30), "The cathedral", "Nhà thờ lớn", ["the square"], None),
                          ("clock_square", "clock", None, "east", "Clock square", "Quảng trường đồng hồ", [], "clock_tower"),
                          ("quarter_mast", "radio_mast", "radio_mast", (-142, -82), "Old quarter mast", "Cột vô tuyến khu phố cổ", ["the gate"], None)],
    "whiteout": [("signal_mast", "radio_mast", "radio_mast", (137, 91), "Signal mast", "Cột tín hiệu", ["the mast"], None),
                 ("frozen_lake", "lake", None, "town", "Frozen lake", "Hồ băng", [], None),
                 ("pass_watch", "watchtower", "watchtower", (-69, 103), "Pass watchtower", "Tháp canh đèo", ["the pass", "the towers"], None)],
}

ASYMMETRY = {
    "siege": "Siege: one side holds the fortress, the other attacks it (prompt 17); measured by role, never 1:1.",
    "long": "Long battlefield: the attacker's square and the defender's fortress strip (prompt 17); measured by role.",
}


class Raster:
    def __init__(self, m):
        if m.get("bounds"):
            self.x0, self.z0, x1, z1 = m["bounds"]
        else:
            n = int(math.ceil(m["size"] / CELL))
            self.x0 = self.z0 = -n * CELL / 2
            x1 = z1 = n * CELL / 2
        self.nx = int(math.ceil((x1 - self.x0) / CELL))
        self.nz = int(math.ceil((z1 - self.z0) / CELL))
        flat = m.get("boundary") or []
        self.poly = list(zip(flat[0::2], flat[1::2]))
        self.tag = [[None] * self.nx for _ in range(self.nz)]
        self.inside = [[True] * self.nx for _ in range(self.nz)]
        if self.poly:
            for gz in range(self.nz):
                for gx in range(self.nx):
                    self.inside[gz][gx] = ca.outline_tools.inside(self.poly, *self.centre(gx, gz))

    def centre(self, gx, gz):
        return self.x0 + (gx + 0.5) * CELL, self.z0 + (gz + 0.5) * CELL

    def cells_near(self, x, z, r):
        a0, a1 = int(math.floor((x - r - self.x0) / CELL)), int(math.floor((x + r - self.x0) / CELL))
        b0, b1 = int(math.floor((z - r - self.z0) / CELL)), int(math.floor((z + r - self.z0) / CELL))
        for gz in range(max(0, b0), min(self.nz - 1, b1) + 1):
            for gx in range(max(0, a0), min(self.nx - 1, a1) + 1):
                yield gx, gz

    def put(self, gx, gz, tag):
        if self.inside[gz][gx] and self.tag[gz][gx] is None:
            self.tag[gz][gx] = tag


def footprint(p, props):
    w, d, _ = props[p["def"]]
    if p.get("rot", 0) % 180 == 90:
        w, d = d, w
    return w, d


def tag_map(bf, m, props, symmetric=False):
    r = Raster(m)
    # 1. Fords.
    for p in m["props"]:
        if p["def"] != "river_ford":
            continue
        w, d = footprint(p, props)
        for gx, gz in r.cells_near(p["x"], p["z"], max(w, d)):
            cx, cz = r.centre(gx, gz)
            if abs(cx - p["x"]) <= w / 2 and abs(cz - p["z"]) <= d / 2:
                r.put(gx, gz, "SHALLOW_WATER")
    # 2. Roads and road bridges.
    for road in m.get("roads", []):
        half = road.get("width", 6) / 2
        pts = list(zip(road["points"][0::2], road["points"][1::2]))
        for (ax, az), (bx, bz) in zip(pts, pts[1:]):
            L2 = (bx - ax) ** 2 + (bz - az) ** 2
            x0, x1 = min(ax, bx) - half, max(ax, bx) + half
            z0, z1 = min(az, bz) - half, max(az, bz) + half
            for gz in range(max(0, int((z0 - r.z0) / CELL)), min(r.nz, int((z1 - r.z0) / CELL) + 1)):
                for gx in range(max(0, int((x0 - r.x0) / CELL)), min(r.nx, int((x1 - r.x0) / CELL) + 1)):
                    cx, cz = r.centre(gx, gz)
                    t = 0.0 if L2 < 1e-9 else max(0.0, min(1.0, ((cx - ax) * (bx - ax) + (cz - az) * (bz - az)) / L2))
                    if math.hypot(cx - (ax + (bx - ax) * t), cz - (az + (bz - az) * t)) <= half:
                        r.put(gx, gz, "ROAD")
    for p in m["props"]:
        if p["def"] == "bridge_road":
            w, d = footprint(p, props)
            for gx, gz in r.cells_near(p["x"], p["z"], max(w, d)):
                cx, cz = r.centre(gx, gz)
                if abs(cx - p["x"]) <= w / 2 and abs(cz - p["z"]) <= d / 2:
                    r.put(gx, gz, "ROAD")
    # 3. Forest: trees close together.
    count = {}
    for p in m["props"]:
        if p["def"] not in TREES:
            continue
        for gx, gz in r.cells_near(p["x"], p["z"], FOREST_REACH):
            cx, cz = r.centre(gx, gz)
            if math.hypot(cx - p["x"], cz - p["z"]) <= FOREST_REACH:
                count[(gx, gz)] = count.get((gx, gz), 0) + 1
    for (gx, gz), n in sorted(count.items()):
        if n >= FOREST_TREES:
            r.put(gx, gz, "FOREST")
    # 4. Rough ground; on an urban map the feet of its buildings.
    for p in m["props"]:
        w, d = footprint(p, props)
        blocks = props[p["def"]][2]
        if p["def"] in ROUGH_PROPS:
            reach = ROUGH_REACH
        elif bf in URBAN_MAPS and blocks and min(w, d) >= URBAN_MIN_SIDE:
            reach = URBAN_REACH
        else:
            continue
        for gx, gz in r.cells_near(p["x"], p["z"], max(w, d) / 2 + reach):
            cx, cz = r.centre(gx, gz)
            ox = max(0.0, abs(cx - p["x"]) - w / 2)
            oz = max(0.0, abs(cz - p["z"]) - d / 2)
            if math.hypot(ox, oz) <= reach:
                r.put(gx, gz, "ROUGH")
    drop_small(r)
    if symmetric:
        # A versus file stays fair: a cell keeps its tag only where its twin across the middle (the half-turn that takes
        # one camp to the other) has the same; the scenery the tags come from is not placed symmetrically.
        if symmetry(m) == "mirror":
            # The mirror across the line x = -z (Lighthouse Bay's coast): cell (gx, gz) <-> (n-1-gz, n-1-gx).
            twin = [[r.tag[r.nx - 1 - gx][r.nz - 1 - gz] if r.nx == r.nz else None for gx in range(r.nx)] for gz in range(r.nz)]
        else:
            twin = [[r.tag[r.nz - 1 - gz][r.nx - 1 - gx] for gx in range(r.nx)] for gz in range(r.nz)]
        for gz in range(r.nz):
            for gx in range(r.nx):
                if r.tag[gz][gx] != twin[gz][gx]:
                    r.tag[gz][gx] = None
        drop_small(r)
    return r


def symmetry(m):
    """Which way a versus file takes one camp to the other: "turn" (the half-turn about the middle) or "mirror" (across
    x = -z), whichever matches more of its props onto props of the same kind (Lighthouse Bay is a mirror)."""
    from collections import defaultdict
    at = defaultdict(set)
    for p in m["props"]:
        at[p["def"]].add((round(p["x"] / 2), round(p["z"] / 2)))

    def rate(f):
        hit = 0
        for p in m["props"]:
            x, z = f(p["x"], p["z"])
            gx, gz = round(x / 2), round(z / 2)
            if any((gx + dx, gz + dz) in at[p["def"]] for dx in (-1, 0, 1) for dz in (-1, 0, 1)):
                hit += 1
        return hit
    return "mirror" if rate(lambda x, z: (-z, -x)) > rate(lambda x, z: (-x, -z)) else "turn"


def drop_small(r):
    """A tag's 4-connected cluster under MIN_CELLS cells goes back to NORMAL."""
    seen = [[False] * r.nx for _ in range(r.nz)]
    for gz in range(r.nz):
        for gx in range(r.nx):
            t = r.tag[gz][gx]
            if t is None or seen[gz][gx]:
                continue
            stack, cluster = [(gx, gz)], []
            seen[gz][gx] = True
            while stack:
                x, z = stack.pop()
                cluster.append((x, z))
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    a, b = x + dx, z + dz
                    if 0 <= a < r.nx and 0 <= b < r.nz and not seen[b][a] and r.tag[b][a] == t:
                        seen[b][a] = True
                        stack.append((a, b))
            if len(cluster) < MIN_CELLS:
                for x, z in cluster:
                    r.tag[z][x] = None


def rects(r, tag):
    """The tag's cells as rectangles (rows' runs merged downwards while they line up)."""
    out = []
    used = [[False] * r.nx for _ in range(r.nz)]
    for gz in range(r.nz):
        gx = 0
        while gx < r.nx:
            if r.tag[gz][gx] != tag or used[gz][gx]:
                gx += 1
                continue
            end = gx
            while end + 1 < r.nx and r.tag[gz][end + 1] == tag and not used[gz][end + 1]:
                end += 1
            top = gz
            while top + 1 < r.nz and all(r.tag[top + 1][k] == tag and not used[top + 1][k] for k in range(gx, end + 1)):
                top += 1
            for z in range(gz, top + 1):
                for k in range(gx, end + 1):
                    used[z][k] = True
            out += [round(r.x0 + gx * CELL, 2), round(r.z0 + gz * CELL, 2), round(r.x0 + (end + 1) * CELL, 2), round(r.z0 + (top + 1) * CELL, 2)]
            gx = end + 1
    return out


def landmarks(bf, m):
    """A battlefield's landmarks; a hint naming a point takes the point's place in the battlefield's _conquest file."""
    out, problems = [], []
    pts = {p["id"]: (p["x"], p["z"]) for p in transit.load(os.path.join(MAPS, f"{bf}_conquest.json")).get("points", [])}
    pool = m["props"] + m.get("decor", [])
    for lid, kind, prop, hint, en, vi, aliases, model in LANDMARKS.get(bf, []):
        at = pts.get(hint) if isinstance(hint, str) else hint
        if at is None:
            problems.append(f"{bf}: landmark {lid}: no point {hint}")
            continue
        x, z = at
        found = None
        if prop:
            best = None
            for p in pool:
                if p["def"] == prop:
                    d = math.hypot(p["x"] - x, p["z"] - z)
                    if d <= 40 and (best is None or d < best[0]):
                        best = (d, p)
            if best:
                found = best[1]
        item = {"id": f"{bf}.{lid}", "kind": kind, "x": round(found["x"] if found else x, 2), "z": round(found["z"] if found else z, 2),
                "name": {"en": en, "vi": vi}}
        if found:
            item["prop"] = prop
        elif model or prop:
            item["model"] = model or prop
        if aliases:
            item["aliases"] = aliases
        out.append(item)
    if not 2 <= len(out) <= 3:
        problems.append(f"{bf}: {len(out)} landmarks")
    return out, problems


def main(argv):
    check_only = "--check" in argv
    only = [a for a in argv if not a.startswith("--")]
    props, _, _ = ca.balance()
    problems, written = [], 0
    total = {t: 0 for t in TAGS}
    cells_in = 0
    for bf in transit.BATTLEFIELDS:
        if only and bf not in only:
            continue
        for variant in VARIANTS:
            path = os.path.join(MAPS, f"{bf}_{variant}.json")
            if not os.path.exists(path):
                continue
            name = f"{bf}_{variant}"
            m = transit.load(path)
            r = tag_map(bf, m, props, symmetric=variant in SYMMETRIC)
            zones = []
            share = {}
            inside = sum(1 for row in r.inside for c in row if c)
            for t in TAGS:
                rs = rects(r, t)
                n = sum(1 for row in r.tag for c in row if c == t)
                share[t] = n / max(1, inside)
                total[t] += n
                if rs:
                    zones.append({"tag": t, "rects": rs})
            cells_in += inside
            marks, lp = landmarks(bf, m)
            problems += lp
            fields = {"terrain": {"cell": CELL, "zones": zones}, "landmarks": marks}
            fields["asymmetry"] = {"intended": True, "reason": ASYMMETRY[variant]} if variant in ASYMMETRY else None
            print(f"{name}: " + ", ".join(f"{t} {share[t]:.1%}" for t in TAGS) + f"; {sum(len(z['rects']) // 4 for z in zones)} rects; "
                  f"{len(marks)} landmarks")
            if not check_only:
                transit.rewrite(path, fields)
                written += 1
    for p in problems:
        print("PROBLEM", p)
    print("all files: " + ", ".join(f"{t} {total[t] / max(1, cells_in):.1%}" for t in TAGS) + " of the play area's cells")
    print(f"{written} map files written, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
