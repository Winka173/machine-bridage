"""Prompt 33 L1 / L6: the map zones and the biome dressing per map (DECISIONS "Prompt 33 L1 / L6").

Writes Assets/MachineBrigade/Resources/Data/map_dressing.json, read by the view only (Game/Views/MapDressing.cs,
Surroundings): the edge band width, the fixed scenery seed, the biome and its dressing per map family, and the camera
frame the outer ring is sized from. The map JSON files are not touched (the simulation never reads this file).

    python Tools/maps/map_dressing.py            # write the file
    python Tools/maps/map_dressing.py --check    # validate the committed file (exit 1 on a problem)

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


def build():
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
    return {'version': 2, 'camera': cam, 'biomes': BIOMES, 'maps': maps, 'edges': EDGE_DRESSING}


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
    data = build()
    OUT.write_text(json.dumps(data, indent=1) + '\n', encoding='utf-8')
    print(f'wrote {OUT.relative_to(ROOT)}: {len(data["maps"])} maps')
    problems = check(data)
    for p in problems:
        print('PROBLEM', p)
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
