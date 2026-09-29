"""Access for the biggest hull (prompt 12 C.2): on a map file as the game loads it, every drop zone,
outpost, gate and objective must be connected to the attacker's (team 0's) drop zone by a route at
least three navigation cells wide (every cell of it with open ground all round: the width of a
gate, room for the biggest hull, not just a gap a car squeezes through), with every gate shut and
every hardpoint filled by the biggest tower its size takes. Blocking only grows with a bigger tower,
so that is the worst of every hardpoint configuration. Each hardpoint's centre must also be open
ground (else the game moves its tower off it). The grid is the simulation's: 2 m cells, footprints
grown by the 1.5 m obstacle clearance, fixed defences a square of 0.8 times their longer side,
everything outside the outline blocked. The same check runs in the game's tests on the sim's own
grid (MapConnectivityTests).

    python Tools/maps/check_access.py [map ids...]   (no ids: every map's _conquest and _siege file)

build_maps.py runs it on every map it writes and stops on a failure.
"""
import json
import math
import re
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import boundary as outline_tools  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data'
CELL = 2.0
CLEARANCE = 1.5
REACH = 6.0          # how near a place (beyond its footprint) the wide route has to come
FIRE_REACH = 15.0    # an objective is shot, not driven onto: a firing position this near will do
SIZES = ('small', 'medium', 'large')


def load(path):
    return json.loads(re.sub(r'^\s*//.*$', '', Path(path).read_text(encoding='utf-8'), flags=re.M))


def balance():
    b = load(DATA / 'balance.json')
    props = {}
    for p in b['props']:
        scale = p.get('scale', 1.0)
        props[p['id']] = (p['width'] * scale, p['depth'] * scale, p.get('blocks', False))
    footprint, towers = {}, {s: [] for s in SIZES + ('utility',)}
    for v in b['vehicles']:
        if not v.get('static', False):
            continue
        scale = v.get('scale', 1.0)
        length = v['length'] * scale if 'length' in v else v['radius'] * 2.7
        width = v['width'] * scale if 'width' in v else v['radius'] * 1.6
        footprint[v['id']] = max(length, width) * 0.8
        fort = v.get('fort')
        if not fort or 'size' not in fort or v.get('passable') or '.' in v['id'] or v['id'] in ('point_tower', 'flak_tower', 'spawn_bastion'):
            continue
        kind = 'utility' if fort.get('kind', 'Tower').lower() == 'utility' else fort['size'].lower()
        towers[kind].append(footprint[v['id']])
    # A slot takes its own size or smaller: the biggest tower it can hold.
    biggest = {'utility': max(towers['utility'])}
    for i, s in enumerate(SIZES):
        biggest[s] = max(f for t in SIZES[:i + 1] for f in towers[t])
    return props, footprint, biggest


class Grid:
    def __init__(self, size):
        self.n = int(math.ceil(size / CELL))
        self.half = self.n * CELL / 2
        self.blocked = [[False] * self.n for _ in range(self.n)]

    def cell(self, x, z):
        return int(math.floor((x + self.half) / CELL)), int(math.floor((z + self.half) / CELL))

    def centre(self, gx, gz):
        return (gx + 0.5) * CELL - self.half, (gz + 0.5) * CELL - self.half

    def block(self, x, z, w, d):
        """Like NavGrid.AddBlocker: every cell the footprint grown by the clearance touches."""
        hw, hd = w / 2 + CLEARANCE, d / 2 + CLEARANCE
        a0, b0 = self.cell(x - hw, z - hd)
        a1, b1 = self.cell(x + hw - 1e-4, z + hd - 1e-4)
        for gz in range(max(0, b0), min(self.n - 1, b1) + 1):
            for gx in range(max(0, a0), min(self.n - 1, a1) + 1):
                self.blocked[gz][gx] = True

    def open(self, gx, gz):
        return 0 <= gx < self.n and 0 <= gz < self.n and not self.blocked[gz][gx]

    def wide(self, gx, gz):
        return all(self.open(gx + dx, gz + dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1))


def build_grid(m, props, footprint, fill=True, biggest=None):
    g = Grid(m['size'])
    for p in m['props']:
        w, d, blocks = props[p['def']]
        if not blocks:
            continue
        if p.get('rot', 0) % 180 == 90:
            w, d = d, w
        g.block(p['x'], p['z'], w, d)
    for u in m.get('units', []):
        side = footprint.get(u['def'])
        if side:
            g.block(u['x'], u['z'], side, side)
    if fill:
        for base in m.get('bases', []):
            side = footprint.get('headquarters', 11.2)
            g.block(base['hq']['x'], base['hq']['z'], side, side)
        for slot in slots_of(m):
            side = biggest['utility' if slot.get('kind') == 'utility' else size_class(slot.get('size', 'large'))]
            g.block(slot['x'], slot['z'], side, side)
        f = m.get('fortress') or {}
        if f.get('superGun'):
            side = footprint.get('super_gun', 6.4)
            g.block(f['superGun']['x'], f['superGun']['z'], side, side)
    if m.get('boundary'):
        flat = m['boundary']
        poly = list(zip(flat[0::2], flat[1::2]))
        for gz in range(g.n):
            for gx in range(g.n):
                if not outline_tools.inside(poly, *g.centre(gx, gz)):
                    g.blocked[gz][gx] = True
    return g


def size_class(size):
    """A slot's size class (older data gives metres across, as HardpointDef.ClassOf reads them)."""
    if isinstance(size, str):
        return size.lower()
    return 'small' if size <= 5.5 else 'medium' if size <= 7.5 else 'large'


def slots_of(m):
    out = []
    for base in m.get('bases', []):
        out.extend(base['slots'])
    out.extend((m.get('fortress') or {}).get('slots', []))
    for p in m.get('points', []):
        out.extend(p.get('outpost', []))
    return out


def flood_wide(g, x, z):
    sx, sz = g.cell(x, z)
    best, best_d = None, float('inf')
    for gz in range(sz - 6, sz + 7):
        for gx in range(sx - 6, sx + 7):
            if g.wide(gx, gz):
                cx, cz = g.centre(gx, gz)
                d = (cx - x) ** 2 + (cz - z) ** 2
                if d < best_d:
                    best, best_d = (gx, gz), d
    seen = set()
    if best is None:
        return seen
    seen.add(best)
    todo = deque([best])
    while todo:
        gx, gz = todo.popleft()
        for nx, nz in ((gx + 1, gz), (gx - 1, gz), (gx, gz + 1), (gx, gz - 1)):
            if (nx, nz) not in seen and g.wide(nx, nz):
                seen.add((nx, nz))
                todo.append((nx, nz))
    return seen


def reached(g, seen, x, z, hx=0.0, hz=0.0):
    a0, b0 = g.cell(x - hx - REACH, z - hz - REACH)
    a1, b1 = g.cell(x + hx + REACH, z + hz + REACH)
    return any((gx, gz) in seen for gx in range(a0, a1 + 1) for gz in range(b0, b1 + 1))


def check(path, tables=None):
    """The problems with one map file (empty when it passes)."""
    props, footprint, biggest = tables or balance()
    m = load(path)
    problems = []
    bare = build_grid(m, props, footprint, fill=False)
    for s in slots_of(m):
        if not bare.open(*bare.cell(s['x'], s['z'])):
            problems.append(f"hardpoint ({s['x']}, {s['z']}) is not on open ground")
    g = build_grid(m, props, footprint, fill=True, biggest=biggest)
    teams = {t['team']: (t['x'], t['z']) for t in m['teams']}
    seen = flood_wide(g, *teams[0])
    need = []
    for team, at in teams.items():
        if team != 0:
            need.append((f'team {team} drop zone', *at, 0.0, 0.0))
    for p in m.get('points', []):
        need.append((f"point {p['id']}", p['x'], p['z'], 0.0, 0.0))
    for p in m['props']:
        w, d, _ = props[p['def']]
        if p.get('rot', 0) % 180 == 90:
            w, d = d, w
        if p['def'] in ('radar_station', 'shield_generator', 'command_hq'):
            need.append((p['def'], p['x'], p['z'], w / 2 + FIRE_REACH - REACH, d / 2 + FIRE_REACH - REACH))
        if p['def'] == 'base_gate':
            across = (0.0, 6.0) if p.get('rot', 0) % 180 == 0 else (6.0, 0.0)
            need.append(('gateway mouth', p['x'] + across[0], p['z'] + across[1], 0.0, 0.0))
            need.append(('gateway mouth', p['x'] - across[0], p['z'] - across[1], 0.0, 0.0))
    f = m.get('fortress') or {}
    if f.get('superGun'):
        need.append(('super-gun', f['superGun']['x'], f['superGun']['z'], 4.0 + FIRE_REACH - REACH, 4.0 + FIRE_REACH - REACH))
    if f.get('arrival'):
        need.append(("the line's stop", *f['arrival']['stop'], 0.0, 0.0))
    for what, x, z, hx, hz in need:
        if not reached(g, seen, x, z, hx, hz):
            problems.append(f'{what} ({x:.1f}, {z:.1f}) out of reach of the biggest hull')
    return problems


def main(ids):
    tables = balance()
    files = []
    for f in sorted((DATA / 'maps').glob('*.json')):
        map_id, _, variant = f.stem.rpartition('_')
        if variant in ('conquest', 'siege') and (not ids or map_id in ids):
            files.append(f)
    failed = 0
    for f in files:
        problems = check(f, tables)
        print(f'{f.stem}: {"ok" if not problems else "; ".join(problems)}')
        failed += bool(problems)
    print(f'{len(files) - failed}/{len(files)} maps pass')
    return failed


if __name__ == '__main__':
    sys.exit(1 if main(sys.argv[1:]) else 0)
