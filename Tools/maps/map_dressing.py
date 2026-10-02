"""Prompt 33 L1 / L6: the map zones and the biome dressing per map (DECISIONS "Prompt 33 L1 / L6").

Writes Assets/MachineBrigade/Resources/Data/map_dressing.json, read by the view only (Game/Views/MapDressing.cs,
Surroundings): the edge band width, the fixed scenery seed, the biome and its dressing per map family, and the camera
frame the outer ring is sized from. The map JSON files are not touched (the simulation never reads this file).

    python Tools/maps/map_dressing.py            # write the file
    python Tools/maps/map_dressing.py --check    # validate the committed file (exit 1 on a problem)
    (writing also runs Tools/maps/validate_p33.py --quick, the prompt 33 L7 validators; --no-validate skips them)

The four zones of a map (seen from the play area's edge, the map rectangle):
  1. play area   - the map itself (navigation, objectives, gameplay props);
  2. edge band   - `edgeBand` metres (12-20) past the edge: transition dressing and visual relief, no gameplay;
  3. outer ring  - `ring` metres past the band: decoration only, sized from the widest camera frame + 15 %;
  4. horizon     - beyond the ring: coarse range, far sea and islands, the horizon ground and the fog.
The ring is the furthest ground the camera can show past the edge when its focus sits on the edge (the focus is
clamped to the map rectangle): the orthographic frame at the furthest zoom, the fixed tilt and the widest supported
screen (4:3, 16:9, 20:9), turned by the map's yaw (the camera never rotates), projected on the ground, x 1.15.
"""
import argparse
import glob
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_access as ca  # noqa: E402
import edge_view as ev  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Assets/MachineBrigade/Resources/Data/map_dressing.json'
MAPS = ROOT / 'Assets/MachineBrigade/Resources/Data/maps'
MODELS = ROOT / 'Assets/MachineBrigade/Resources/Models'
CAMERA_CS = ROOT / 'Assets/MachineBrigade/Scripts/Game/CameraControl/RtsCamera.cs'
RUNNER_CS = ROOT / 'Assets/MachineBrigade/Scripts/Game/Match/MatchRunner.cs'
BALANCE = ROOT / 'Assets/MachineBrigade/Resources/Data/balance.json'

ASPECTS = (4 / 3, 16 / 9, 20 / 9)
PAD = 0.15
MODES = ('_conquest', '_long', '_sandbox', '_siege')


def camera_constants():
    cam = CAMERA_CS.read_text(encoding='utf-8')
    run = RUNNER_CS.read_text(encoding='utf-8')

    def const(src, name):
        m = re.search(r'\b' + name + r'\s*=\s*(-?[0-9.]+)f', src)
        if not m:
            raise SystemExit(f'cannot find {name}')
        return float(m.group(1))
    return {
        'tiltDegrees': const(cam, 'Pitch'),
        'maxZoomSquare': const(cam, 'DefaultMaxZoom'),
        'maxZoomLong': const(run, 'LongMaxZoom'),
        'yawSquare': const(cam, 'SquareYaw'),
        'yawLong': const(cam, 'LongYaw'),
        'rotates': False,
        'aspects': [round(a, 4) for a in ASPECTS],
        'pad': PAD,
    }


def reach(yaw, tilt, zoom, aspect, rotates=False):
    """World x and z half-extents of the ground the orthographic frame shows round its focus."""
    w = zoom * aspect                         # screen right, on the ground as it is
    d = zoom / math.sin(math.radians(tilt))   # screen up, stretched by the tilt onto the ground
    if rotates:
        r = math.hypot(w, d)
        return r, r
    y = math.radians(yaw)
    return abs(w * math.cos(y)) + abs(d * math.sin(y)), abs(w * math.sin(y)) + abs(d * math.cos(y))


def rings(cam):
    def widest(yaw, zoom):
        xs, zs = zip(*(reach(yaw, cam['tiltDegrees'], zoom, a, cam['rotates']) for a in cam['aspects']))
        return max(xs), max(zs)
    sx, sz = widest(cam['yawSquare'], cam['maxZoomSquare'])
    lx, lz = widest(cam['yawLong'], cam['maxZoomLong'])
    up = lambda v: float(math.ceil(v * (1 + cam['pad']) - 1e-6))  # noqa: E731
    return {'reachSquare': round(max(sx, sz), 2), 'reachLongSide': round(lx, 2), 'reachLongEnd': round(lz, 2),
            'ringSquare': up(max(sx, sz)), 'ringLongSide': up(lx), 'ringLongEnd': up(lz)}


def stable_seed(text):
    """FNV-1a (32 bit) of the family id, kept positive: the same in C# (MapDressing.StableSeed)."""
    h = 2166136261
    for ch in text.encode('utf-8'):
        h ^= ch
        h = (h * 16777619) & 0xFFFFFFFF
    return h & 0x7FFFFFFF


def T(prefix, items):
    """A weighted list: (name, weight) pairs expanded, each name prefixed with dress_<prefix>_."""
    out = []
    for name, weight in items:
        out += [name if name.startswith('dress_') else f'dress_{prefix}_{name}'] * weight
    return out


# Instances per hectare by zone (targets, DECISIONS "Prompt 33 L1 / L6"), the HLOD stand-in for the theme's trees,
# the visual relief (counts per map) and the default edge band.
BIOMES = [
    dict(id='temperate', edgeBand=16, play=8, band=120, ring=45, far=40,
         playSet=T('temperate', [('shrub', 2), ('wildflowers', 3), ('stump', 1)]),
         bandSet=T('temperate', [('shrub', 3), ('haybales', 1), ('stump', 2), ('wildflowers', 2)]),
         ringSet=T('temperate', [('shrub', 2), ('haybales', 2), ('stump', 1), ('wildflowers', 1)]),
         farSet=T('temperate', [('tree_far', 1)]), seaSet=[], horizonSet=[],
         farTree='dress_temperate_tree_far', hills=8, berms=6, ditches=3, dryBeds=1),
    dict(id='desert', edgeBand=20, play=5, band=70, ring=30, far=18,
         playSet=T('desert', [('scrub', 3), ('barrel_cacti', 1), ('bones', 1)]),
         bandSet=T('desert', [('scrub', 3), ('barrel_cacti', 2), ('bones', 1), ('hoodoo', 1)]),
         ringSet=T('desert', [('scrub', 2), ('hoodoo', 2), ('barrel_cacti', 1), ('bones', 1)]),
         farSet=T('desert', [('far', 1)]), seaSet=[], horizonSet=[],
         farTree='', hills=6, berms=4, ditches=0, dryBeds=3),
    dict(id='snow', edgeBand=18, play=6, band=100, ring=40, far=35,
         playSet=T('snow', [('drift', 2), ('ice_rock', 1)]),
         bandSet=T('snow', [('drift', 3), ('ice_rock', 2), ('log', 2)]),
         ringSet=T('snow', [('drift', 2), ('ice_rock', 1), ('log', 1)]),
         farSet=T('snow', [('pine_far', 1)]), seaSet=[], horizonSet=[],
         farTree='dress_snow_pine_far', hills=8, berms=4, ditches=0, dryBeds=1),
    dict(id='harbor', edgeBand=14, play=4, band=90, ring=35, far=12,
         playSet=T('temperate', [('wildflowers', 1)]),
         bandSet=T('harbor', [('pallets', 2), ('drums', 2), ('pipes', 1), ('bollards', 1)]),
         ringSet=T('harbor', [('pallets', 1), ('drums', 1), ('pipes', 2)]),
         farSet=T('harbor', [('shed_far', 1)]), seaSet=T('coast', [('buoy', 1)]), horizonSet=[],
         farTree='dress_temperate_tree_far', hills=3, berms=5, ditches=3, dryBeds=0),
    dict(id='jungle', edgeBand=14, play=10, band=150, ring=60, far=45,
         playSet=T('jungle', [('fern', 2), ('banana', 1)]),
         bandSet=T('jungle', [('palm_small', 2), ('banana', 2), ('fern', 3), ('vine_rock', 1)]),
         ringSet=T('jungle', [('palm_small', 2), ('banana', 1), ('fern', 2), ('vine_rock', 1)]),
         farSet=T('jungle', [('tree_far', 1)]), seaSet=[], horizonSet=[],
         farTree='dress_jungle_tree_far', hills=6, berms=3, ditches=2, dryBeds=2),
    dict(id='volcanic', edgeBand=16, play=5, band=70, ring=30, far=18,
         playSet=T('volcanic', [('ash_rocks', 1)]),
         bandSet=T('volcanic', [('ash_rocks', 2), ('cinder_cone', 1), ('snag', 2)]),
         ringSet=T('volcanic', [('ash_rocks', 1), ('cinder_cone', 2), ('snag', 1)]),
         farSet=T('volcanic', [('far', 1)]), seaSet=[], horizonSet=[],
         farTree='dress_volcanic_snag', hills=8, berms=3, ditches=0, dryBeds=2),
    dict(id='urban', edgeBand=12, play=3, band=80, ring=25, far=6,
         playSet=T('temperate', [('wildflowers', 1)]),
         bandSet=T('urban', [('rubble', 2), ('planter', 2), ('billboard', 1), ('kiosk', 1)]),
         ringSet=T('urban', [('rubble', 1), ('billboard', 1), ('kiosk', 1), ('planter', 1)]),
         farSet=T('urban', [('block_far', 1)]), seaSet=[], horizonSet=[],
         farTree='dress_temperate_tree_far', hills=0, berms=4, ditches=2, dryBeds=0),
    dict(id='coast', edgeBand=14, play=6, band=100, ring=35, far=20,
         playSet=T('coast', [('dune_grass', 2), ('driftwood', 1)]),
         bandSet=T('coast', [('dune_grass', 3), ('driftwood', 2), ('rowboat', 1)]),
         ringSet=T('coast', [('dune_grass', 2), ('driftwood', 1), ('rowboat', 1)]),
         farSet=T('temperate', [('tree_far', 1)]), seaSet=T('coast', [('buoy', 1)]),
         horizonSet=T('coast', [('island_far', 1)]),
         farTree='dress_temperate_tree_far', hills=5, berms=4, ditches=1, dryBeds=1),
]

# Per map family: biome, edge band (m), density factor and an optional far-tree override ('none': keep the theme's
# own trees in the far ring). The map JSON's theme keeps the palette; the biome picks the dressing.
MAP_TABLE = {
    'ashfield': ('temperate', 16, 1.0), 'borderbridge': ('temperate', 16, 1.0), 'greenvale': ('temperate', 16, 1.1),
    'hydrodam': ('temperate', 16, 1.0), 'skyhold': ('temperate', 18, 0.8),
    'capital': ('urban', 12, 1.0), 'metrocity': ('urban', 12, 1.0), 'veyra_old_quarter': ('urban', 12, 1.0),
    'foundry': ('harbor', 12, 1.0), 'ironport': ('harbor', 14, 1.0), 'rustyard': ('harbor', 14, 1.0),
    'coralisles': ('coast', 12, 1.0, 'none'), 'landingbeach': ('coast', 14, 1.0), 'lighthousebay': ('coast', 14, 1.0),
    'dunebreak': ('desert', 20, 1.0), 'launchsite': ('desert', 20, 0.8), 'openpit': ('desert', 18, 0.9),
    'redrock': ('desert', 18, 1.0), 'saltflat': ('desert', 20, 0.6),
    'emberridge': ('volcanic', 16, 1.0),
    'frostpeak': ('snow', 18, 1.0), 'orbitalgate': ('snow', 16, 0.9), 'whiteout': ('snow', 20, 0.8),
    'junglepass': ('jungle', 12, 1.0), 'swamp': ('jungle', 14, 1.1),
}


# Prompt 33 L2 (view side, DECISIONS "Prompt 33 L2 view / L7"): what stands beyond each edge type. The view
# (Surroundings.Edges.cs) reads the map's own "edges" data (Tools/maps/edges.py) and dresses by it:
# - corners: the prebuilt piece per corner name (dress_edge_<piece>, mb_p33_edges.py), "first" = the type on the
#   piece's own -X side (a junction) or on its +Z strip (an outer corner); the view mirrors it when the data's order
#   is the other way round; "radius" keeps the scatter and the relief off it.
# - sea: on a SEA stretch the water runs to the horizon (no land, houses or woods): whitecaps per hectare, surf lines
#   along a BEACH coast, stacks along a CLIFF coast, quay walls, cranes and containers along a QUAY coast, far ships
#   and hazy islands on the horizon, buoys along the sea lanes' way out.
# - sets: the edge modifiers' ring dressing (instances per hectare of the ring beyond that stretch).
# - rail: the track section laid along every RailSpline and the portal at its far end(s).
EDGE_DRESSING = {
    'corners': [
        dict(piece='outer_land', model='dress_edge_outer_land', first='LAND', radius=22.0),
        dict(piece='corner_land_cliff', model='dress_edge_corner_land_cliff', first='LAND', radius=24.0),
        dict(piece='outer_urban', model='dress_edge_outer_urban', first='URBAN', radius=18.0),
        dict(piece='bank_land_river', model='dress_edge_bank_land_river', first='LAND', radius=22.0),
        dict(piece='corner_land_sea', model='dress_edge_corner_land_sea', first='LAND', radius=26.0),
        dict(piece='outer_sea', model='dress_edge_outer_sea', first='SEA', radius=20.0),
        dict(piece='embankment_urban_river', model='dress_edge_embankment_urban_river', first='URBAN', radius=20.0),
        dict(piece='outer_land_sea', model='dress_edge_outer_land_sea', first='SEA', radius=22.0),
        dict(piece='outer_cliff', model='dress_edge_outer_cliff', first='CLIFF', radius=24.0),
        dict(piece='outer_river', model='dress_edge_outer_river', first='RIVER', radius=18.0),
    ],
    'sea': dict(waves=['dress_sea_whitecap'], waveDensity=6.0, surf='dress_sea_surf', stack='dress_sea_stack',
                quay='dress_edge_quay', crane='dress_edge_crane_far', containers='dress_edge_containers',
                ships=['dress_sea_ship_far', 'dress_sea_tanker_far'],
                islands=['dress_sea_island_haze', 'dress_coast_island_far'], shipsPerSide=2, islandsPerSide=2,
                laneBuoy='dress_coast_buoy', laneStep=40.0),
    'sets': [
        dict(key='INDUSTRIAL', ring=5.0, set=['dress_edge_chimney', 'dress_edge_tanks', 'dress_harbor_shed_far',
                                              'dress_harbor_shed_far', 'dress_harbor_pipes', 'dress_edge_containers']),
        dict(key='HARBOR', ring=6.0, set=['dress_edge_containers', 'dress_edge_containers', 'dress_harbor_shed_far',
                                          'dress_harbor_drums', 'dress_harbor_pallets']),
        dict(key='URBAN', ring=10.0, set=['dress_urban_block_far', 'dress_urban_kiosk', 'dress_urban_billboard']),
        dict(key='CLIFF', ring=14.0, set=['dress_edge_scree', 'dress_edge_scree', 'dress_desert_far']),
    ],
    'rail': dict(track='dress_edge_rail_track', portal='dress_edge_tunnel_portal', step=6.0),
}

PIECES = ('outer_land', 'corner_land_cliff', 'outer_urban', 'bank_land_river', 'corner_land_sea', 'outer_sea',
          'embankment_urban_river', 'outer_land_sea', 'outer_cliff', 'outer_river')


def edge_models(edges):
    """Every model id the edge dressing names."""
    out = [c['model'] for c in edges['corners']]
    sea = edges['sea']
    out += sea['waves'] + sea['ships'] + sea['islands'] + [sea[k] for k in ('surf', 'stack', 'quay', 'crane',
                                                                             'containers', 'laneBuoy')]
    for s in edges['sets']:
        out += s['set']
    out += [edges['rail']['track'], edges['rail']['portal']]
    return out

# Prompt 33 L3 (view): the landmarks data's "model" (a landmark no map prop is) -> the decoration model and its footprint
# (w along local X, d along local Z, metres). A model not listed here is a prop's own look (church, water_tower ...):
# its GLB is drawn as it is (no collider), at its balance.json footprint.
LANDMARK_MODELS = {
    'palace_dome': ('dress_landmark_palace_dome', 24.0, 20.0),
    'station_clock': ('dress_landmark_station_clock', 22.0, 12.0),
    'cooling_tower': ('dress_landmark_cooling_tower', 22.0, 26.0),
    'dam_wall': ('dress_landmark_dam_wall', 64.0, 7.0),
    'survey_beacon': ('dress_landmark_survey_beacon', 6.0, 6.0),  # thin (THIN_MODELS): may stand on drivable ground
    'clock_tower': ('dress_landmark_clock_tower', 7.0, 7.0),
}
# View-only landmarks no data entry has: Ironport's line c4m12.05 sees "the lighthouse" out on its SEA side, at the end of
# the quay line carried on west beyond the map (square files: their north side is the harbour's sea).
EXTRA_LANDMARKS = {
    'ironport': [dict(id='ironport.outer_lighthouse', model='dress_landmark_harbour_light', x=-205.0, z=166.0, yaw=0.0,
                      square=True)],
}
WATER_PROPS = {'river_water'}
# Open lattices and masts: a vehicle passing through one hardly shows, so drivable ground under them costs 1, not 10.
THIN_MODELS = {'survey_beacon', 'radio_mast'}
LANDMARK_REACH = 140.0  # metres from the data's place the search goes (nearer wins; drivable ground costs more)
LANDMARK_STEP = 3.0
LANDMARK_DISTANCE_COST = 0.35  # per metre from the data's place; a drivable cell costs 10
KEEP_POINT, KEEP_RALLY, KEEP_GATE, KEEP_ROAD, KEEP_RAIL = 4.0, 22.0, 6.0, 1.5, 4.5


class SpotSearch:
    """Where a landmark model can stand on one map file: off every prop's footprint (the water's excepted), the
    capture circles, the rallies, the bases' slots, the entry gates, the roads and the rails, and off the edge sea; as
    little of it on drivable ground as possible (decoration: units would drive through it), near the data's place."""

    def __init__(self, m, tables):
        self.m = m
        props, footprint, biggest = tables
        self.bare = ca.build_grid(m, props, footprint, fill=False)
        full = ca.build_grid(m, props, footprint, fill=True, biggest=biggest)
        g = self.bare
        self.slot = [[full.blocked[z][x] and not g.blocked[z][x] for x in range(g.nx)] for z in range(g.nz)]
        self.prop = [[False] * g.nx for _ in range(g.nz)]
        self.water = [[False] * g.nx for _ in range(g.nz)]
        for p in m['props']:
            w, d, blocks = props[p['def']]
            if p.get('rot', 0) % 180 == 90:
                w, d = d, w
            water = p['def'] in WATER_PROPS
            if not blocks and not water:
                continue
            a0, b0 = g.cell(p['x'] - w / 2 + .01, p['z'] - d / 2 + .01)
            a1, b1 = g.cell(p['x'] + w / 2 - .01, p['z'] + d / 2 - .01)
            for gz in range(max(0, b0), min(g.nz - 1, b1) + 1):
                for gx in range(max(0, a0), min(g.nx - 1, a1) + 1):
                    (self.water if water else self.prop)[gz][gx] = True
        self.keep = [[False] * g.nx for _ in range(g.nz)]
        circles = [(pt['x'], pt['z'], pt.get('radius', 12) + KEEP_POINT) for pt in m.get('points', [])]
        circles += [(t['x'], t['z'], KEEP_RALLY) for t in m.get('teams', [])]
        circles += [(e['x'], e['z'], KEEP_GATE) for e in m.get('entryGates', [])]
        segs = []
        for road in m.get('roads', []):
            pts = list(zip(road['points'][0::2], road['points'][1::2]))
            segs += [(a, b, road['width'] / 2 + KEEP_ROAD) for a, b in zip(pts, pts[1:])]
        for r in m.get('rails', []):
            pts = list(zip(r['points'][0::2], r['points'][1::2]))
            segs += [(a, b, KEEP_RAIL) for a, b in zip(pts, pts[1:])]
        for gz in range(g.nz):
            for gx in range(g.nx):
                x, z = g.centre(gx, gz)
                if any((x - cx) ** 2 + (z - cz) ** 2 < r * r for cx, cz, r in circles) or \
                        any(ev.seg_dist(x, z, a[0], a[1], b[0], b[1]) < h for a, b, h in segs):
                    self.keep[gz][gx] = True
        self.lines = ev.lines(m)
        self.corners = [(c['x'], c['z']) for c in (m.get('edges') or {}).get('corners', [])]
        self.taken = []  # footprints of the landmarks already stood on this file (x0, z0, x1, z1)

    @staticmethod
    def _table(grid):
        """Summed-area table of a boolean grid: (nz + 1) x (nx + 1)."""
        nz, nx = len(grid), len(grid[0])
        t = [[0] * (nx + 1) for _ in range(nz + 1)]
        for z in range(nz):
            row, acc = grid[z], 0
            for x in range(nx):
                acc += row[x]
                t[z + 1][x + 1] = t[z][x + 1] + acc
        return t

    @staticmethod
    def _sum(t, a0, b0, a1, b1):
        return t[b1 + 1][a1 + 1] - t[b0][a1 + 1] - t[b1 + 1][a0] + t[b0][a0]

    def tables(self):
        if getattr(self, '_bad', None) is None:
            g = self.bare
            self._bad = self._table([[self.keep[z][x] or self.prop[z][x] or self.slot[z][x] for x in range(g.nx)]
                                     for z in range(g.nz)])
            self._wet = self._table(self.water)
            self._walk = self._table([[not g.blocked[z][x] and not self.water[z][x] for x in range(g.nx)]
                                      for z in range(g.nz)])
        return self._bad, self._wet, self._walk

    def score(self, cx, cz, w, d, water_front, walk_cost=10.0):
        """(cost, drivable cells) of a footprint centred at (cx, cz), or None when it may not stand there."""
        out = ev.beyond(self.m, cx, cz)
        if out > 30:
            return None
        for x0, z0, x1, z1 in self.taken:
            if cx - w / 2 - 2 < x1 and cx + w / 2 + 2 > x0 and cz - d / 2 - 2 < z1 and cz + d / 2 + 2 > z0:
                return None
        g = self.bare
        bad, wet_t, walk_t = self.tables()
        a0, b0 = g.cell(cx - w / 2 + 1, cz - d / 2 + 1)
        a1, b1 = g.cell(cx + w / 2 - 1, cz + d / 2 - 1)
        cells = (a1 - a0 + 1) * (b1 - b0 + 1)
        ia0, ib0, ia1, ib1 = max(a0, 0), max(b0, 0), min(a1, g.nx - 1), min(b1, g.nz - 1)
        walk = wet = 0
        if ia0 <= ia1 and ib0 <= ib1:
            if self._sum(bad, ia0, ib0, ia1, ib1):
                return None
            walk = self._sum(walk_t, ia0, ib0, ia1, ib1)
            wet = self._sum(wet_t, ia0, ib0, ia1, ib1)
        if (ia0, ib0, ia1, ib1) != (a0, b0, a1, b1):
            # The part beyond the rectangle: off the edge sea, the rivers and lines running out, the corner pieces.
            for gz in range(b0, b1 + 1, 2):
                for gx in range(a0, a1 + 1, 2):
                    if 0 <= gx < g.nx and 0 <= gz < g.nz:
                        continue
                    x, z = g.centre(gx, gz)
                    if ev.edge_sea(self.m, x, z) or ev.river_distance(self.m, x, z) < 2:
                        return None
                    if any(ev.seg_dist(x, z, ln[0], ln[1], ln[2], ln[3]) < ln[4] + 2 for ln in self.lines):
                        return None
                    if any((x - qx) ** 2 + (z - qz) ** 2 < 26 * 26 for qx, qz in self.corners):
                        return None
        if water_front and wet < cells * 0.6:
            return None
        if not water_front and wet:
            return None  # only the dam stands in the water
        return walk * walk_cost + (25.0 if out > 0 else 0.0), walk

    def best(self, hx, hz, w, d, water_front=False, walk_cost=10.0):
        best = None
        r = int(LANDMARK_REACH / LANDMARK_STEP)
        for j in range(-r, r + 1):
            for i in range(-r, r + 1):
                dist = math.hypot(i, j) * LANDMARK_STEP
                if dist > LANDMARK_REACH:
                    continue
                cx, cz = hx + i * LANDMARK_STEP, hz + j * LANDMARK_STEP
                for yaw in ((0.0,) if water_front else (0.0, 90.0)):
                    fw, fd = (w, d) if yaw == 0.0 else (d, w)
                    sc = self.score(cx, cz, fw, fd, water_front, walk_cost)
                    if sc is None:
                        continue
                    cost = sc[0] + dist * LANDMARK_DISTANCE_COST
                    if best is None or cost < best[0]:
                        best = (cost, cx, cz, self.facing_water(cx, cz, fd) if water_front else yaw, sc[1])
        return best

    def facing_water(self, cx, cz, d):
        """A dam face falls towards local +Z: the yaw (0 or 180) that puts more water ahead of its parapet."""
        g = self.bare

        def wet(sign):
            n = 0
            for k in range(1, 6):
                gx, gz = g.cell(cx, cz + sign * (d / 2 + k * 2))
                n += 0 <= gx < g.nx and 0 <= gz < g.nz and self.water[gz][gx]
            return n
        return 0.0 if wet(1) >= wet(-1) else 180.0


def landmark_spots(report=None):
    """Every map file's landmark models where they can stand (map_dressing.json "landmarks")."""
    tables = ca.balance()
    props = tables[0]
    out = []
    for f in sorted(MAPS.glob('*.json')):
        m = ca.load(f)
        fam = f.stem
        for mode in MODES:
            if fam.endswith(mode):
                fam = fam[:-len(mode)]
        wanted = [lm for lm in m.get('landmarks', []) if lm.get('model')]
        extras = [e for e in EXTRA_LANDMARKS.get(fam, []) if not (e.get('square') and m.get('bounds'))]
        if not wanted and not extras:
            continue
        search = SpotSearch(m, tables) if wanted else None
        for lm in wanted:
            if lm['model'] in LANDMARK_MODELS:
                model, w, d = LANDMARK_MODELS[lm['model']]
            else:
                model = lm['model']
                w, d, _ = props.get(model, (8.0, 8.0, True))
            spot = search.best(lm['x'], lm['z'], w, d, water_front=lm['model'] == 'dam_wall',
                               walk_cost=1.0 if lm['model'] in THIN_MODELS else 10.0)
            if spot is None:
                if report is not None:
                    report.append(f'{f.stem}: {lm["id"]} ({model}) found no spot; not stood')
                continue
            _, x, z, yaw, walk = spot
            fw, fd = (w, d) if yaw in (0.0, 180.0) else (d, w)
            search.taken.append((x - fw / 2, z - fd / 2, x + fw / 2, z + fd / 2))
            out.append(dict(map=f.stem, id=lm['id'], model=model, x=round(x, 2), z=round(z, 2), yaw=yaw, scale=1.0,
                            radius=round(math.hypot(w, d) / 2, 1), onPlay=walk > 0))
            if report is not None:
                report.append(f'{f.stem}: {lm["id"]} ({model}) at ({x:.0f}, {z:.0f}) yaw {yaw:.0f}, '
                              f'{math.hypot(x - lm["x"], z - lm["z"]):.0f} m from the data, {walk} drivable cells')
        for e in extras:
            out.append(dict(map=f.stem, id=e['id'], model=e['model'], x=e['x'], z=e['z'], yaw=e['yaw'], scale=1.0,
                            radius=8.0, onPlay=False))
    return out

def families():
    out = set()
    for f in glob.glob(str(MAPS / '*.json')):
        name = Path(f).stem
        for m in MODES:
            if name.endswith(m):
                name = name[:-len(m)]
                break
        out.add(name)
    return sorted(out)


def build(report=None):
    cam = camera_constants()
    cam.update(rings(cam))
    biomes = {b['id']: b for b in BIOMES}
    maps = []
    for fam in families():
        row = MAP_TABLE.get(fam)
        if row is None:
            raise SystemExit(f'{fam}: no row in MAP_TABLE')
        biome, band, density = row[:3]
        b = biomes[biome]
        maps.append(dict(id=fam, biome=biome, edgeBand=float(band), density=density, seed=stable_seed(fam),
                         farTree=row[3] if len(row) > 3 else '',
                         hills=b['hills'], berms=b['berms'], ditches=b['ditches'], dryBeds=b['dryBeds']))
    return {'version': 2, 'camera': cam, 'biomes': BIOMES, 'maps': maps, 'edges': EDGE_DRESSING,
            'landmarks': landmark_spots(report)}


def check(data):
    problems = []
    cam = camera_constants()
    cam.update(rings(cam))
    for key, value in cam.items():
        if data['camera'].get(key) != value:
            problems.append(f'camera.{key}: file {data["camera"].get(key)} != code {value}')
    for k in ('Square', 'LongSide', 'LongEnd'):
        if data['camera']['ring' + k] < data['camera']['reach' + k] * (1 + PAD) - 1e-6:
            problems.append(f'ring{k} {data["camera"]["ring" + k]} does not cover reach x 1.15')
    gameplay = {p['id'] for p in json.loads(re.sub(r'^\s*//.*$', '', BALANCE.read_text(encoding='utf-8-sig'),
                                                   flags=re.M)).get('props', [])}
    ids = {b['id'] for b in data['biomes']}
    if ids != {'temperate', 'desert', 'snow', 'harbor', 'jungle', 'volcanic', 'urban', 'coast'}:
        problems.append(f'biomes {sorted(ids)}')
    for b in data['biomes']:
        for key in ('playSet', 'bandSet', 'ringSet', 'farSet', 'seaSet', 'horizonSet'):
            for m in b[key]:
                if not m.startswith('dress_'):
                    problems.append(f'{b["id"]}.{key}: {m} is not a decoration model (dress_*)')
                if m in gameplay:
                    problems.append(f'{b["id"]}.{key}: {m} is a gameplay prop')
                if not (MODELS / f'{m}.glb').exists():
                    problems.append(f'{b["id"]}.{key}: {m}.glb missing')
        if b['farTree'] and not (MODELS / f'{b["farTree"]}.glb').exists():
            problems.append(f'{b["id"]}: farTree {b["farTree"]}.glb missing')
        if not b['playSet'] or not b['bandSet'] or not b['ringSet'] or not b['farSet']:
            problems.append(f'{b["id"]}: an empty set')
    edges = data.get('edges')
    if not edges:
        problems.append('no edge dressing (prompt 33 L2 view)')
    else:
        pieces = {c['piece'] for c in edges['corners']}
        for piece in PIECES:
            if piece not in pieces:
                problems.append(f'edges.corners: no model for {piece}')
        for m in edge_models(edges):
            if not m.startswith('dress_'):
                problems.append(f'edges: {m} is not a decoration model (dress_*)')
            if m in gameplay:
                problems.append(f'edges: {m} is a gameplay prop')
            if not (MODELS / f'{m}.glb').exists():
                problems.append(f'edges: {m}.glb missing')
    for lm in data.get('landmarks', []):
        if not (MODELS / f'{lm["model"]}.glb').exists():
            problems.append(f'landmarks: {lm["map"]} {lm["id"]}: {lm["model"]}.glb missing')
        if not (MAPS / f'{lm["map"]}.json').exists():
            problems.append(f'landmarks: {lm["map"]} is not a map file')
    seen = {m['id'] for m in data['maps']}
    for fam in families():
        if fam not in seen:
            problems.append(f'{fam}: no dressing entry')
    seeds = [m['seed'] for m in data['maps']]
    if len(set(seeds)) != len(seeds):
        problems.append('two maps share a seed')
    for m in data['maps']:
        if m['biome'] not in ids:
            problems.append(f'{m["id"]}: unknown biome {m["biome"]}')
        if not 12 <= m['edgeBand'] <= 20:
            problems.append(f'{m["id"]}: edge band {m["edgeBand"]} outside 12-20 m')
        if m['seed'] != stable_seed(m['id']):
            problems.append(f'{m["id"]}: seed is not the stable seed')
        if not 0.3 <= m['density'] <= 2.0:
            problems.append(f'{m["id"]}: density {m["density"]}')
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--no-validate', action='store_true', help='skip the prompt 33 L7 validators after writing')
    args = ap.parse_args()
    if args.check:
        data = json.loads(OUT.read_text(encoding='utf-8'))
        problems = check(data)
        for p in problems:
            print('PROBLEM', p)
        c = data['camera']
        print(f'map_dressing.json: {len(data["maps"])} maps, {len(data["biomes"])} biomes; ring square {c["ringSquare"]} m '
              f'(reach {c["reachSquare"]}), long sides {c["ringLongSide"]} m (reach {c["reachLongSide"]}), long ends '
              f'{c["ringLongEnd"]} m (reach {c["reachLongEnd"]}); {len(problems)} problems')
        sys.exit(1 if problems else 0)
    report = []
    data = build(report)
    for line in report:
        print('LANDMARK', line)
    OUT.write_text(json.dumps(data, indent=1) + '\n', encoding='utf-8')
    print(f'wrote {OUT.relative_to(ROOT)}: {len(data["maps"])} maps')
    problems = check(data)
    for p in problems:
        print('PROBLEM', p)
    # Prompt 33 L7: the map validators after the last map data step (quick: check_access.py and the chokepoints are
    # run by `python Tools/maps/validate_p33.py`, which also writes the results the design document reads).
    if '--no-validate' not in sys.argv:
        import validate_p33
        found = validate_p33.run(quick=True)
        print(f'validate_p33 (quick): {sum(len(r.errors) for r in found)} errors, '
              f'{sum(len(r.warnings) for r in found)} warnings')
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
