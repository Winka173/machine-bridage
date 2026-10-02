"""Prompt 33 L7: the twelve map validators (DECISIONS "Prompt 33 L2 view / L7").

Static Python checks over the map files (Resources/Data/maps), map_dressing.json, balance.json and the view's source:
nothing is simulated. Each check gives errors (a rule broken) and warnings (judged but allowed: a campaign file's intended
asymmetry, a known failure carried from before prompt 33).

    python Tools/maps/validate_p33.py               # all twelve, every map file (exit 1 on an error)
    python Tools/maps/validate_p33.py --quick       # without check 7 (check_access.py) and check 11 (chokepoints)
    python Tools/maps/validate_p33.py --only 1 5 9  # some checks
    python Tools/maps/validate_p33.py --json out.json

Run by Tools/maps/map_dressing.py after it writes map_dressing.json (the last map data step) and by the design document's
build (Tools/docs/prompt33.py, section 15g shows the table).

 1 edge_ring        SEA stretches: no land scenery, landmark or edge set on the sea; the sea dressing is sea kinds only;
                    the sea maps declare SEA.
 2 camera_cover     band + ring cover the widest camera frame + 15 % on every axis, at every supported aspect (and turned,
                    were the camera to rotate); the horizon ground and sea reach past it: no world gap.
 3 decoration_inert every decoration model is a GLB with no collider node, dress_* (or a prop's look for a landmark), never
                    a gameplay prop; the view's scenery code adds no collider and never touches the simulation.
 4 band_clear       no gameplay object (prop, wall, unit, slot, gate) in the edge band past the rectangle.
 5 continuity       every road end at the edge, rail, RIVER stretch, coast junction and sea route exit has its link out,
                    and the view draws every link kind (the links equal edges.py's recompute).
 6 entry_gates      every file has gates; each is on open ground in the play area, its approach runs from the outer band
                    to it; every edge / rail / sea delivery the campaign uses on a map has a data gate of its kind there
                    (else the Sim makes one where the point stands: a warning).
 7 access           check_access.py passes (the biggest hull's clearance), but for the failures known before prompt 33.
 8 terrain_zones    terrain tag zones: known tags, no empty zone, no overlap, inside the rectangle.
 9 rail_sea_graph   each RailSpline is one connected line with its play stretch, portal(s) beyond the edge and crossings in
                    play; each SeaRouteGraph is connected, exits beyond the edge, every segment between known nodes.
10 crossing_warning every level crossing warns at least max(4 s, length / 4.5 m/s + 0.5 s), and that is >= 4 s.
11 chokepoints      no single chokepoint (one 6 m cell: a one-hull gap) cuts off more than 45 % of the open ground, but
                    where the file says its asymmetry is intended (a warning there); a 10 m passage doing so is a warning.
12 replay_ingress   the ingress is data and fixed ticks: gate ids unique, numbers finite, the approach ends at the gate,
                    the row gap a whole number of ticks, no clock or unseeded random in the Sim's ingress, rail and sea
                    code (the replays themselves are Prompt33EdgeTests / RailTests / SeaRouteTests, run by the lead).
"""
from __future__ import annotations

import argparse
import json
import math
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_access as ca  # noqa: E402
import edge_view as ev  # noqa: E402
import edges as edges_tool  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data'
MAPS = DATA / 'maps'
MODELS = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Models'
DRESSING = DATA / 'map_dressing.json'
RESULTS = ROOT / 'Docs' / 'maps' / 'validate_p33.json'   # the last full run (the design document reads it)
SCRIPTS = ROOT / 'Assets' / 'MachineBrigade' / 'Scripts'
VIEW_FILES = ['Surroundings.cs', 'Surroundings.Zones.cs', 'Surroundings.Dressing.cs', 'Surroundings.Edges.cs',
              'Surroundings.Landmarks.cs']
SIM_INGRESS = ['Sim/Modes/MissionEvents.Ingress.cs', 'Sim/Navigation/EntryGate.cs', 'Sim/Navigation/SpawnPoints.cs',
               'Sim/Movement/RailSystem.cs', 'Sim/Navigation/RailSpline.cs', 'Sim/Navigation/SeaRouteGraph.cs',
               'Sim/Bosses/NavalSystem.Routes.cs']
SEA_MAPS = {'landingbeach', 'lighthousebay', 'coralisles', 'ironport', 'rustyard'}
TAGS = {'ROAD', 'ROUGH', 'FOREST', 'SHALLOW_WATER'}
LINK_KINDS = {'road', 'rail', 'river', 'coast', 'seaLane', 'air'}
SEA_DRESS_OK = ('dress_sea_', 'dress_coast_buoy', 'dress_coast_island_far', 'dress_edge_quay', 'dress_edge_crane_far',
                'dress_edge_containers')
SEA_LANDMARKS_OK = {'dress_landmark_harbour_light'}
# check_access.py's failures before prompt 33 (DECISIONS "Prompt 33 L5": 73/75, Mirewood and Veyra Old Quarter conquest).
KNOWN_ACCESS = {'swamp_conquest', 'veyra_old_quarter_conquest'}
TICK = 20
CHOKE_CELL = 3       # fine (2 m) cells per side of a chokepoint cell: 6 m
CHOKE_SHARE = 0.45
CHOKE_WIDE, CHOKE_WIDE_NEED = 5, 13   # the 10 m look (warnings only)


def variants():
    return sorted(f for f in MAPS.glob('*.json')
                  if f.stem.rsplit('_', 1)[-1] in ('conquest', 'sandbox', 'siege', 'long'))


def family(stem):
    return stem.rsplit('_', 1)[0]


class Result:
    def __init__(self, number, name):
        self.number, self.name = number, name
        self.errors, self.warnings, self.checked = [], [], 0

    def as_dict(self):
        return {'check': self.number, 'name': self.name, 'checked': self.checked, 'errors': self.errors,
                'warnings': self.warnings}


def glb_nodes(path):
    """The node names of a .glb (its JSON chunk)."""
    data = path.read_bytes()
    if len(data) < 20 or data[:4] != b'glTF':
        return None
    length, kind = struct.unpack('<II', data[12:20])
    doc = json.loads(data[20:20 + length].decode('utf-8'))
    return [n.get('name', '') for n in doc.get('nodes', [])]


# ---------------------------------------------------------------------------------------------------------- checks
def check_edge_ring(maps, dressing, r):
    sea = (dressing.get('edges') or {}).get('sea', {})
    sea_models = list(sea.get('waves', [])) + list(sea.get('ships', [])) + list(sea.get('islands', [])) + \
        [sea.get(k) for k in ('surf', 'stack', 'quay', 'crane', 'containers', 'laneBuoy') if sea.get(k)]
    for model in sea_models:
        if not model.startswith(SEA_DRESS_OK):
            r.errors.append(f'map_dressing edges.sea: {model} is not a sea or shore model')
    harbour = edges_tool.HARBOUR_DECOR
    for stem, m in maps.items():
        segs = ev.segments(m)
        if not segs:
            r.errors.append(f'{stem}: no edges data')
            continue
        r.checked += 1
        has_sea = any(s['type'] == 'SEA' for s in segs)
        if family(stem) in SEA_MAPS and not stem.endswith('_long') and not has_sea:
            r.errors.append(f'{stem}: a sea map without a SEA stretch')
        if not has_sea:
            continue
        for d in m.get('decor', []):
            if d['def'] in harbour:
                continue
            if ev.edge_sea(m, d['x'], d['z']) and not ev.near_coast(m, d['x'], d['z']):
                r.errors.append(f'{stem}: land scenery {d["def"]} at ({d["x"]}, {d["z"]}) stands on the sea beyond the edge')
        for lm in dressing.get('landmarks', []):
            if lm['map'] == stem and lm['model'] not in SEA_LANDMARKS_OK and ev.edge_sea(m, lm['x'], lm['z']):
                r.errors.append(f'{stem}: landmark {lm["id"]} stands on the sea')
        for s in segs:
            if s['type'] == 'SEA' and not s.get('shore'):
                r.errors.append(f'{stem}: SEA stretch {s["side"]} {s["from"]}..{s["to"]} has no shore kind')


def check_camera_cover(maps, dressing, r):
    cam = dressing.get('camera', {})
    pad = 1 + cam.get('pad', 0.15)
    tilt = math.radians(cam.get('tiltDegrees', 52))
    by_family = {e['id']: e for e in dressing.get('maps', [])}

    def reach(yaw_deg, zoom, aspect):
        yaw = math.radians(yaw_deg)
        hx, hz = zoom * aspect, zoom / math.sin(tilt)
        corners = [(sx * hx, sz * hz) for sx in (-1, 1) for sz in (-1, 1)]
        if cam.get('rotates'):
            d = math.hypot(hx, hz)
            return d, d
        rx = max(abs(x * math.cos(yaw) - z * math.sin(yaw)) for x, z in corners)
        rz = max(abs(x * math.sin(yaw) + z * math.cos(yaw)) for x, z in corners)
        return rx, rz

    for stem, m in maps.items():
        r.checked += 1
        entry = by_family.get(family(stem))
        if entry is None:
            r.errors.append(f'{stem}: no dressing entry')
            continue
        x0, z0, x1, z1 = ev.rect(m)
        long_map = (z1 - z0) > (x1 - x0) * 1.2
        zoom = cam['maxZoomLong'] if long_map else cam['maxZoomSquare']
        yaw = cam['yawLong'] if long_map else cam['yawSquare']
        need_x = need_z = 0.0
        for aspect in cam.get('aspects', [4 / 3, 16 / 9, 20 / 9]):
            rx, rz = reach(yaw, zoom, aspect)
            need_x, need_z = max(need_x, rx * pad), max(need_z, rz * pad)
        ring_x = cam['ringLongSide'] if long_map else cam['ringSquare']
        ring_z = cam['ringLongEnd'] if long_map else cam['ringSquare']
        band = entry['edgeBand']
        if band + ring_x + 1e-6 < need_x or band + ring_z + 1e-6 < need_z:
            r.errors.append(f'{stem}: band {band} + ring ({ring_x}, {ring_z}) under the frame + 15 % ({need_x:.1f}, '
                            f'{need_z:.1f})')
        # The decorated square (Surroundings.Extent) and the horizon ground (6 x it) out past every frame.
        half = max(x1 - x0, z1 - z0) / 2
        extent = max(half + 130, max((x1 - x0) / 2 + band + ring_x, (z1 - z0) / 2 + band + ring_z))
        if extent * 3 < half + band + max(need_x, need_z) * 2:
            r.errors.append(f'{stem}: the horizon ground ({extent * 3:.0f} m) ends inside the widest view')


def check_decoration_inert(dressing, gameplay, r):
    models = set()
    for b in dressing.get('biomes', []):
        for key in ('playSet', 'bandSet', 'ringSet', 'farSet', 'seaSet', 'horizonSet'):
            models.update(b.get(key, []))
        if b.get('farTree'):
            models.add(b['farTree'])
    e = dressing.get('edges') or {}
    models.update(c['model'] for c in e.get('corners', []))
    sea = e.get('sea', {})
    models.update(sea.get('waves', []) + sea.get('ships', []) + sea.get('islands', []))
    models.update(sea[k] for k in ('surf', 'stack', 'quay', 'crane', 'containers', 'laneBuoy') if sea.get(k))
    for s in e.get('sets', []):
        models.update(s['set'])
    if e.get('rail'):
        models.update([e['rail']['track'], e['rail']['portal']])
    looks = {lm['model'] for lm in dressing.get('landmarks', [])}
    for model in sorted(models | looks):
        r.checked += 1
        path = MODELS / f'{model}.glb'
        if not path.exists():
            r.errors.append(f'{model}.glb missing')
            continue
        nodes = glb_nodes(path) or []
        if any(re.search(r'collider|^col_|_col$', n, re.I) for n in nodes):
            r.errors.append(f'{model}: a collider node in the GLB')
        if model in models and not model.startswith('dress_'):
            r.errors.append(f'{model}: decoration that is not a dress_* model')
        if model in models and model in gameplay:
            r.errors.append(f'{model}: decoration that is a gameplay prop')
        if model in looks and not model.startswith('dress_') and model in gameplay:
            r.warnings.append(f'{model}: a prop GLB drawn as a landmark look (no prop, no collider)')
    for name in VIEW_FILES:
        src = (SCRIPTS / 'Game' / 'Views' / name).read_text(encoding='utf-8')
        code = re.sub(r'//.*', '', src)
        for bad, why in ((r'Collider', 'adds a collider'), (r'AddComponent<(?!MeshFilter|MeshRenderer)', 'adds a component'),
                         (r'\bNavGrid\b', 'touches the navigation grid'), (r'world\.(Add|Spawn|Remove|Step)\w*\(',
                                                                           'changes the simulation')):
            if re.search(bad, code):
                r.errors.append(f'{name}: {why}')


def check_band_clear(maps, gameplay_blocks, r):
    for stem, m in maps.items():
        r.checked += 1
        def out(x, z, what):
            if ev.beyond(m, x, z) > 0.5:
                r.errors.append(f'{stem}: {what} at ({x}, {z}) beyond the edge (in the band)')
        for p in m['props']:
            out(p['x'], p['z'], f'prop {p["def"]}')
        for u in m.get('units', []):
            out(u['x'], u['z'], f'unit {u["def"]}')
        for b in m.get('bases', []):
            out(b['hq']['x'], b['hq']['z'], 'base HQ')
        for s in ca.slots_of(m):
            out(s['x'], s['z'], 'base slot')
        for w in m.get('walls', []):
            pts = w.get('points', [])
            for x, z in zip(pts[0::2], pts[1::2]):
                out(x, z, f'wall {w.get("id", "")}')
        for g in m.get('entryGates', []):
            out(g['x'], g['z'], f'entry gate {g["id"]}')


def check_continuity(maps, r):
    for stem, m in maps.items():
        r.checked += 1
        e = m.get('edges') or {}
        rect = ev.rect(m)
        segs = e.get('segments', [])
        stored = e.get('links', [])
        kinds = {l['kind'] for l in stored}
        for k in kinds - LINK_KINDS:
            r.errors.append(f'{stem}: link kind {k} the view does not draw')
        want = edges_tool.links(m, rect, segs)

        def key(l):
            return (l['kind'], round(l['x']), round(l['z']))
        have = {key(l) for l in stored}
        for l in want:
            if key(l) not in have:
                r.errors.append(f'{stem}: {l["kind"]} at ({l["x"]}, {l["z"]}) meets the edge with no link out')
        for s in segs:
            if s['type'] == 'RIVER' and not any(l['kind'] == 'river' and l.get('side') == s['side'] for l in stored):
                r.errors.append(f'{stem}: RIVER stretch {s["side"]} {s["from"]}..{s["to"]} has no river running out')
        for c in e.get('corners', []):
            if 'SEA' in c['between'] and len(set(c['between'])) == 2 and \
                    not any(l['kind'] == 'coast' and abs(l['x'] - c['x']) < 1 and abs(l['z'] - c['z']) < 1 for l in stored):
                r.errors.append(f'{stem}: coast junction ({c["x"]}, {c["z"]}) has no coast link')
        for rail in m.get('rails', []):
            pts = list(zip(rail['points'][0::2], rail['points'][1::2]))
            ends_out = [p for p in (pts[0], pts[-1]) if ev.beyond(m, *p) > 0]
            if not ends_out:
                r.errors.append(f'{stem}: rail {rail["id"]} never leaves the map (no portal)')
            for p in ends_out:
                if ev.beyond(m, *p) < 30:
                    r.warnings.append(f'{stem}: rail {rail["id"]} ends {ev.beyond(m, *p):.0f} m past the edge (portal near)')
        for n in (m.get('seaRoutes') or {}).get('nodes', []):
            if n.get('kind') == 'exit' and ev.beyond(m, n['x'], n['z']) <= 0:
                r.errors.append(f'{stem}: sea route exit {n["id"]} inside the map')


def check_entry_gates(maps, campaign, r):
    tables = ca.balance()
    for stem, m in maps.items():
        r.checked += 1
        gates = m.get('entryGates', [])
        if not gates:
            r.errors.append(f'{stem}: no entry gates')
            continue
        g = ca.build_grid(m, tables[0], tables[1], fill=False)
        for gate in gates:
            if not g.open(*g.cell(gate['x'], gate['z'])):
                # A rail gate is the train's (a sim object on its line): a vehicle spawn the Sim moves onto a gate
                # skips one that is not on the battlefield's ground, so it is only noted.
                (r.warnings if gate.get('kind') == 'rail' else r.errors).append(
                    f'{stem}: gate {gate["id"]} not on open ground' + (' (a rail gate: trains only)' if gate.get('kind') == 'rail' else ''))
            path = gate.get('path', [])
            if len(path) < 4 or abs(path[-2] - gate['x']) > 0.5 or abs(path[-1] - gate['z']) > 0.5:
                r.errors.append(f'{stem}: gate {gate["id"]}: its approach does not end at the gate')
            elif ev.beyond(m, path[0], path[1]) < 0:
                r.errors.append(f'{stem}: gate {gate["id"]}: its approach does not start beyond the edge')
            if gate.get('visualIngressLength', 0) <= 0:
                r.errors.append(f'{stem}: gate {gate["id"]}: no visual ingress length')
    # The campaign's deliveries by map: an edge, rail or sea wave wants a data gate of its kind on that map.
    want = {'edge': {'road', 'edge'}, 'rail': {'rail'}, 'sea': {'sea'}}
    for mission in campaign:
        m = maps.get(mission['map'])
        if m is None:
            continue
        for kind in sorted(mission['kinds'] & set(want)):
            r.checked += 1
            if not any(g_['kind'] in want[kind] for g_ in m.get('entryGates', [])):
                r.warnings.append(f'{mission["id"]} on {mission["map"]}: {kind} delivery with no {kind} gate in the data '
                                  f'(the Sim makes one where the point stands)')


def check_access(r):
    tables = ca.balance()
    for f in sorted(MAPS.glob('*.json')):
        if f.stem.rsplit('_', 1)[-1] not in ('conquest', 'siege', 'long'):
            continue
        r.checked += 1
        problems = ca.check(f, tables)
        if problems:
            (r.warnings if f.stem in KNOWN_ACCESS else r.errors).append(
                f'{f.stem}: {"; ".join(problems)}' + (' (known before prompt 33)' if f.stem in KNOWN_ACCESS else ''))


def check_terrain(maps, r):
    for stem, m in maps.items():
        r.checked += 1
        t = m.get('terrain')
        if not t:
            r.errors.append(f'{stem}: no terrain tags')
            continue
        x0, z0, x1, z1 = ev.rect(m)
        rects = []
        for zone in t.get('zones', []):
            if zone['tag'] not in TAGS:
                r.errors.append(f'{stem}: unknown tag {zone["tag"]}')
            flat = zone.get('rects', [])
            if not flat:
                r.errors.append(f'{stem}: empty {zone["tag"]} zone')
            for i in range(0, len(flat), 4):
                a, b, c, d = flat[i:i + 4]
                if not (a < c and b < d):
                    r.errors.append(f'{stem}: {zone["tag"]} rect {flat[i:i + 4]} is empty')
                if a < x0 - .01 or b < z0 - .01 or c > x1 + .01 or d > z1 + .01:
                    r.errors.append(f'{stem}: {zone["tag"]} rect {flat[i:i + 4]} outside the map')
                rects.append((a, b, c, d, zone['tag']))
        rects.sort()
        for i, (a, b, c, d, tag) in enumerate(rects):
            for a2, b2, c2, d2, tag2 in rects[i + 1:]:
                if a2 >= c - 1e-6:
                    break
                if b < d2 - 1e-6 and b2 < d - 1e-6 and a < c2 - 1e-6:
                    r.errors.append(f'{stem}: {tag} {[a, b, c, d]} overlaps {tag2} {[a2, b2, c2, d2]}')


def check_rail_sea(maps, r):
    for stem, m in maps.items():
        for rail in m.get('rails', []):
            r.checked += 1
            pts = list(zip(rail['points'][0::2], rail['points'][1::2]))
            if len(pts) < 2:
                r.errors.append(f'{stem}: rail {rail["id"]} has under two points')
                continue
            length = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))
            if any(math.hypot(b[0] - a[0], b[1] - a[1]) < 1e-3 for a, b in zip(pts, pts[1:])):
                r.errors.append(f'{stem}: rail {rail["id"]} repeats a point')
            lo, hi = rail.get('playFrom', 0), rail.get('playTo', length)
            if not 0 <= lo < hi <= length + 0.5:
                r.errors.append(f'{stem}: rail {rail["id"]} play stretch {lo}..{hi} not within 0..{length:.1f}')
            if lo > 0.01 and ev.beyond(m, *pts[0]) <= 0:
                r.errors.append(f'{stem}: rail {rail["id"]} has an entry gate but starts inside the map')
            for c in rail.get('crossings', []):
                if not lo - 0.5 <= c['s'] <= hi + 0.5:
                    r.errors.append(f'{stem}: rail {rail["id"]} crossing {c["id"]} outside the play stretch')
        graph = m.get('seaRoutes')
        if not graph:
            continue
        r.checked += 1
        ids = {n['id'] for n in graph.get('nodes', [])}
        adj = {i: set() for i in ids}
        for s in graph.get('segments', []):
            if s['a'] not in ids or s['b'] not in ids:
                r.errors.append(f'{stem}: sea segment {s["a"]}-{s["b"]} names an unknown node')
                continue
            adj[s['a']].add(s['b'])
            adj[s['b']].add(s['a'])
        if ids:
            seen, todo = set(), [next(iter(sorted(ids)))]
            while todo:
                n = todo.pop()
                if n in seen:
                    continue
                seen.add(n)
                todo.extend(adj[n] - seen)
            if seen != ids:
                r.errors.append(f'{stem}: sea route graph in pieces ({len(ids) - len(seen)} nodes cut off)')
        if not any(n.get('kind') == 'exit' for n in graph.get('nodes', [])):
            r.errors.append(f'{stem}: sea route graph has no exit beyond the map')


def check_crossings(maps, r):
    for stem, m in maps.items():
        for rail in m.get('rails', []):
            for c in rail.get('crossings', []):
                r.checked += 1
                warning = max(4.0, c.get('length', 0) / 4.5 + 0.5)
                if warning < 4.0 or c.get('warning', warning) < warning - 1e-6:
                    r.errors.append(f'{stem}: crossing {rail["id"]}.{c["id"]} warns {c.get("warning", warning)} s < {warning:.2f} s')
                if c.get('closes') is False:
                    r.warnings.append(f'{stem}: crossing {rail["id"]}.{c["id"]} only warns (its closing would cut the ground)')


def chokepoint_share(m, tables, k=CHOKE_CELL, need=6):
    """The largest share of the open ground (cells of k x k fine 2 m cells, open with `need` of them open) one cell's
    removal cuts off from the biggest piece left."""
    g = ca.build_grid(m, tables[0], tables[1], fill=False)
    nx, nz = g.nx // k, g.nz // k
    open_ = [[sum(g.open(cx * k + i, cz * k + j) for i in range(k) for j in range(k)) >= need for cx in range(nx)]
             for cz in range(nz)]
    nodes = [(x, z) for z in range(nz) for x in range(nx) if open_[z][x]]
    if not nodes:
        return 0.0, None
    index = {n: i for i, n in enumerate(nodes)}
    adj = [[] for _ in nodes]
    for (x, z), i in index.items():
        for dx, dz in ((1, 0), (0, 1)):
            j = index.get((x + dx, z + dz))
            if j is not None:
                adj[i].append(j)
                adj[j].append(i)
    # The biggest connected piece, then articulation points in it (iterative Tarjan) with the sizes they cut off.
    comp = [-1] * len(nodes)
    sizes = []
    for s in range(len(nodes)):
        if comp[s] >= 0:
            continue
        stack, comp[s], n = [s], len(sizes), 0
        while stack:
            v = stack.pop()
            n += 1
            for w in adj[v]:
                if comp[w] < 0:
                    comp[w] = len(sizes)
                    stack.append(w)
        sizes.append(n)
    main = max(range(len(sizes)), key=lambda c: sizes[c])
    total = sizes[main]
    root = next(i for i in range(len(nodes)) if comp[i] == main)
    disc, low, size = [-1] * len(nodes), [0] * len(nodes), [1] * len(nodes)
    cut = {}
    t = 0
    disc[root] = low[root] = t
    stack = [(root, -1, iter(adj[root]))]
    while stack:
        v, parent, it = stack[-1]
        advanced = False
        for w in it:
            if w == parent:
                continue
            if disc[w] < 0:
                t += 1
                disc[w] = low[w] = t
                stack.append((w, v, iter(adj[w])))
                advanced = True
                break
            low[v] = min(low[v], disc[w])
        if advanced:
            continue
        stack.pop()
        if parent >= 0:
            low[parent] = min(low[parent], low[v])
            size[parent] += size[v]
            if low[v] >= disc[parent]:
                cut.setdefault(parent, []).append(size[v])
    best, where = 0.0, None
    for v, parts in cut.items():
        if v == root and len(parts) < 2:
            continue
        pieces = parts + [total - 1 - sum(parts)]
        locked = total - 1 - max(pieces)
        if locked / total > best:
            best, where = locked / total, nodes[v]
    if where is not None:
        where = g.centre(where[0] * k + 1, where[1] * k + 1)
    return best, where


def check_chokepoints(maps, r):
    tables = ca.balance()
    for stem, m in maps.items():
        r.checked += 1
        share, where = chokepoint_share(m, tables)
        if share > CHOKE_SHARE:
            msg = f'{stem}: one chokepoint near ({where[0]:.0f}, {where[1]:.0f}) cuts off {share * 100:.0f} % of the open ground'
            if (m.get('asymmetry') or {}).get('intended'):
                r.warnings.append(msg + ' (asymmetry intended)')
            else:
                r.errors.append(msg)
            continue
        # The same at 10 m cells (a passage up to about 10 m wide, two hulls): noted for a look, not a rule broken.
        share, where = chokepoint_share(m, tables, CHOKE_WIDE, CHOKE_WIDE_NEED)
        if share > CHOKE_SHARE:
            r.warnings.append(f'{stem}: a passage of 10 m or less near ({where[0]:.0f}, {where[1]:.0f}) holds '
                              f'{share * 100:.0f} % of the open ground')


def check_replay(maps, r):
    src = (SCRIPTS / 'Sim/Modes/MissionEvents.Ingress.cs').read_text(encoding='utf-8')
    gap = re.search(r'RowGap\s*=\s*([0-9.]+)', src)
    if not gap or abs(float(gap.group(1)) * TICK - round(float(gap.group(1)) * TICK)) > 1e-9:
        r.errors.append('MissionEvents.Ingress.cs: RowGap is not a whole number of ticks')
    for name in SIM_INGRESS:
        path = SCRIPTS / name
        if not path.exists():
            r.warnings.append(f'{name}: not found')
            continue
        code = re.sub(r'//.*', '', path.read_text(encoding='utf-8'))
        for bad, why in ((r'\bUnityEngine\b', 'uses UnityEngine'), (r'new\s+(System\.)?Random\s*\(', 'makes its own random'),
                         (r'\bDateTime\b|\bStopwatch\b|Environment\.TickCount', 'reads a clock'),
                         (r'\bGuid\b', 'makes a Guid')):
            if re.search(bad, code):
                r.errors.append(f'{name}: {why}')
    for stem, m in maps.items():
        r.checked += 1
        ids = [g['id'] for g in m.get('entryGates', [])]
        if len(ids) != len(set(ids)):
            r.errors.append(f'{stem}: entry gate ids repeat')
        for g in m.get('entryGates', []):
            values = [g['x'], g['z'], g.get('inX', 0), g.get('inZ', 0), g.get('visualIngressLength', 0)] + g.get('path', [])
            if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in values):
                r.errors.append(f'{stem}: gate {g["id"]} has a value that is not a finite number')


CHECKS = {
    1: 'edge_ring', 2: 'camera_cover', 3: 'decoration_inert', 4: 'band_clear', 5: 'continuity', 6: 'entry_gates',
    7: 'access', 8: 'terrain_zones', 9: 'rail_sea_graph', 10: 'crossing_warning', 11: 'chokepoints', 12: 'replay_ingress',
}


def campaign_missions():
    """Each mission's map file and the deliveries its events use (the library's, with the mission's overrides)."""
    text = (DATA / 'campaign.json').read_text(encoding='utf-8-sig')
    data = json.loads(re.sub(r'^\s*//.*$', '', text, flags=re.M))
    library = {e['id']: e for e in (data.get('eventLibrary') or {}).get('events', [])}
    out = []
    for mission in data.get('missions', []):
        if not mission.get('map'):
            continue
        kinds = set()
        for entry in mission.get('missionEvents', []):
            ref = entry if isinstance(entry, str) else entry.get('id')
            base = library.get(ref, {})
            params = dict(base.get('params') or {})
            if isinstance(entry, dict):
                params.update(entry.get('params') or {})
            if base.get('kind') not in ('EnemyWave', 'AllyWave'):
                continue
            d = params.get('delivery', 'edge')
            kinds.update(d if isinstance(d, list) else [d])
        out.append({'id': mission.get('id', '?'), 'map': f"{mission['map']}_{mission.get('variant') or 'conquest'}",
                    'kinds': kinds})
    return out


def run(only=None, quick=False, verbose=True):
    maps = {f.stem: ca.load(f) for f in variants()}
    dressing = json.loads(DRESSING.read_text(encoding='utf-8'))
    balance = ca.load(DATA / 'balance.json')
    gameplay = {p['id'] for p in balance.get('props', [])}
    gameplay_blocks = {p['id'] for p in balance.get('props', []) if p.get('blocks')}
    wanted = only or list(CHECKS)
    if quick:
        wanted = [n for n in wanted if n not in (7, 11)]
    results = []
    for n in wanted:
        r = Result(n, CHECKS[n])
        if n == 1:
            check_edge_ring(maps, dressing, r)
        elif n == 2:
            check_camera_cover(maps, dressing, r)
        elif n == 3:
            check_decoration_inert(dressing, gameplay, r)
        elif n == 4:
            check_band_clear(maps, gameplay_blocks, r)
        elif n == 5:
            check_continuity(maps, r)
        elif n == 6:
            check_entry_gates(maps, campaign_missions(), r)
        elif n == 7:
            check_access(r)
        elif n == 8:
            check_terrain(maps, r)
        elif n == 9:
            check_rail_sea(maps, r)
        elif n == 10:
            check_crossings(maps, r)
        elif n == 11:
            check_chokepoints(maps, r)
        elif n == 12:
            check_replay(maps, r)
        results.append(r)
        if verbose:
            print(f'{n:2d} {r.name:17s} checked {r.checked:4d}: {len(r.errors)} errors, {len(r.warnings)} warnings', flush=True)
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', nargs='*', type=int)
    ap.add_argument('--quick', action='store_true')
    ap.add_argument('--json')
    ap.add_argument('--list', action='store_true', help='print every error and warning')
    args = ap.parse_args()
    results = run(args.only, args.quick)
    for r in results:
        for e in (r.errors if not args.list else r.errors + r.warnings)[: None if args.list else 12]:
            print(f'   [{r.number}] {"ERROR" if e in r.errors else "warn"} {e}')
    out = args.json or (str(RESULTS) if not args.only and not args.quick else None)
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(json.dumps([r.as_dict() for r in results], indent=1) + chr(10), encoding='utf-8')
    errors = sum(len(r.errors) for r in results)
    print(f'{errors} errors, {sum(len(r.warnings) for r in results)} warnings')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
