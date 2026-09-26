"""Generate the Ashfield maps (Conquest and Survival) into Resources/Data/maps.

    python Tools/maps/build_ashfield.py

The layout is designed, not random: a paved square at the centre with a ring road, four
streets leading out of town lined with houses that face the street, shops and apartments
around the square, fuel depots at the two side objectives, farmsteads, ruins, rock cover on
the approaches and dense forests in the two empty corners. Random numbers (fixed seed) only
vary building types, gaps and tree placement, so the output is stable.

Every placement is checked against the footprints in balance.json, the roads, the camps and
the objectives, and the result is flood-filled on the simulation's 2 m navigation grid (with
its 1.5 m obstacle clearance) to prove that both camps can reach every objective.
"""
import json
import math
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data'
HALF = 80.0
CELL = 2.0
CLEARANCE = 1.5


def load_props():
    text = (DATA / 'balance.json').read_text(encoding='utf-8')
    text = re.sub(r'^\s*//.*$', '', text, flags=re.M)
    balance = json.loads(text)
    return {p['id']: p for p in balance['props']}


PROPS = load_props()
BUILDINGS = {'house_small', 'house_large', 'cottage', 'townhouse', 'apartment', 'shop', 'church', 'barn', 'silo',
             'warehouse', 'garage', 'water_tower', 'ruin', 'fuel_tank', 'wall'}


class Layout:
    def __init__(self, seed, teams, points):
        self.rng = random.Random(seed)
        self.teams = teams
        self.points = points
        self.props = []
        self.rects = []
        self.roads = []

    # ------------------------------------------------------------------ geometry
    @staticmethod
    def size(def_id, rot):
        p = PROPS[def_id]
        w, d = p['width'], p['depth']
        return (d, w) if rot % 180 == 90 else (w, d)

    def road(self, width, *points):
        self.roads.append({'width': width, 'points': [float(v) for v in points]})

    def road_distance(self, x0, z0, x1, z1):
        """Smallest gap between a rectangle and any road edge (negative when overlapping)."""
        best = 1e9
        for road in self.roads:
            pts = road['points']
            half = road['width'] / 2
            for i in range(0, len(pts) - 2, 2):
                ax, az, bx, bz = pts[i], pts[i + 1], pts[i + 2], pts[i + 3]
                length = math.hypot(bx - ax, bz - az)
                steps = max(1, int(length / 0.75))
                for k in range(steps + 1):
                    t = k / steps
                    px, pz = ax + (bx - ax) * t, az + (bz - az) * t
                    dx = max(x0 - px, 0, px - x1)
                    dz = max(z0 - pz, 0, pz - z1)
                    best = min(best, math.hypot(dx, dz) - half)
        return best

    def free(self, def_id, x, z, rot, pad, road_gap, ignore_points=False):
        w, d = self.size(def_id, rot)
        x0, z0, x1, z1 = x - w / 2, z - d / 2, x + w / 2, z + d / 2
        if x0 < -HALF + 2 or z0 < -HALF + 2 or x1 > HALF - 2 or z1 > HALF - 2:
            return False
        blocks = PROPS[def_id].get('blocks', False)
        for team in self.teams:
            if math.hypot(x - team[0], z - team[1]) < 22 + max(w, d) / 2:
                return False
        # The square stays open.
        if x1 > -13 and x0 < 13 and z1 > -13 and z0 < 13:
            return False
        if not ignore_points and blocks:
            for (px, pz, radius) in self.points:
                cx, cz = min(max(px, x0), x1), min(max(pz, z0), z1)
                if math.hypot(cx - px, cz - pz) < radius - 1:
                    return False
        if road_gap is not None and self.road_distance(x0, z0, x1, z1) < road_gap:
            return False
        for (a0, b0, a1, b1) in self.rects:
            if x0 - pad < a1 and x1 + pad > a0 and z0 - pad < b1 and z1 + pad > b0:
                return False
        return True

    def add(self, def_id, x, z, rot=0, pad=1.0, road_gap=0.8, ignore_points=False):
        x, z = round(x * 2) / 2, round(z * 2) / 2
        if not self.free(def_id, x, z, rot, pad, road_gap, ignore_points):
            return False
        w, d = self.size(def_id, rot)
        self.rects.append((x - w / 2, z - d / 2, x + w / 2, z + d / 2))
        entry = {'def': def_id, 'x': x, 'z': z}
        if rot:
            entry['rot'] = rot
        self.props.append(entry)
        return True

    # ------------------------------------------------------------------ streets
    def frontage(self, axis, line, side, start, end, kinds, setback=1.8, road_half=3.5, alley_every=(2, 3),
                 yards=True, cars=0.35):
        """Buildings along a street: `axis` 'x' means the street runs along x at z = line.
        `side` +1 or -1 picks the side; buildings face the street. Returns placed count."""
        rot = {('x', 1): 180, ('x', -1): 0, ('z', 1): 270, ('z', -1): 90}[(axis, side)]
        direction = 1 if end > start else -1
        u = start
        run = 0
        placed = 0
        next_alley = self.rng.randint(*alley_every)
        k = 0
        while (u - end) * direction < 0:
            kind = kinds[k % len(kinds)]
            k += 1
            w, d = self.size(kind, rot)
            along, deep = (w, d) if axis == 'x' else (d, w)
            centre_u = u + direction * along / 2
            if (centre_u + direction * along / 2 - end) * direction > 0:
                break
            offset = line + side * (road_half + setback + deep / 2)
            x, z = (centre_u, offset) if axis == 'x' else (offset, centre_u)
            ok = self.add(kind, x, z, rot, pad=0.4)
            if ok:
                placed += 1
                run += 1
                if yards:
                    self.backyard(axis, side, x, z, along, deep)
                if cars and self.rng.random() < cars:
                    self.park(axis, line, side, centre_u, road_half)
            # Rows of two or three touch; then an alley wide enough for tanks.
            gap = 0.6
            if run >= next_alley or not ok:
                gap = 7.0 + self.rng.random() * 3
                run = 0
                next_alley = self.rng.randint(*alley_every)
            u += direction * (along + gap)
        return placed

    def backyard(self, axis, side, x, z, along, deep):
        kind = self.rng.choice(['fence', 'fence', 'hedge', 'stone_wall', None])
        if kind is None:
            return
        back = deep / 2 + 3.0
        if axis == 'x':
            self.add(kind, x, z + side * back, 0, pad=0.3, road_gap=0.5)
        else:
            self.add(kind, x + side * back, z, 90, pad=0.3, road_gap=0.5)

    def park(self, axis, line, side, u, road_half):
        kind = 'truck' if self.rng.random() < 0.2 else 'car'
        w, d = self.size(kind, 0)
        offset = line + side * (road_half + 0.2 + d / 2)
        if axis == 'x':
            self.add(kind, u + self.rng.uniform(-2, 2), offset, 0, pad=0.5, road_gap=None)
        else:
            self.add(kind, offset, u + self.rng.uniform(-2, 2), 90, pad=0.5, road_gap=None)

    # ------------------------------------------------------------------ clusters
    def forest(self, cx, cz, radius, density, dead=0.04):
        """Trees scattered in a noisy blob, thick in the middle and thinning at the edge."""
        count = int(math.pi * radius * radius * density)
        for _ in range(count * 6):
            if count <= 0:
                break
            a = self.rng.random() * math.tau
            r = radius * math.sqrt(self.rng.random())
            edge = r / radius
            wobble = 0.75 + 0.25 * math.sin(a * 3 + cx) * math.cos(a * 5 + cz)
            if edge > wobble or self.rng.random() < edge * 0.5:
                continue
            if self.add('tree', cx + math.cos(a) * r, cz + math.sin(a) * r, 0, pad=0.2, road_gap=1.0):
                count -= 1

    def tree_line(self, x0, z0, x1, z1, spacing=4.0):
        length = math.hypot(x1 - x0, z1 - z0)
        for i in range(int(length / spacing) + 1):
            t = i / max(1, int(length / spacing))
            self.add('tree', x0 + (x1 - x0) * t + self.rng.uniform(-0.8, 0.8), z0 + (z1 - z0) * t + self.rng.uniform(-0.8, 0.8),
                     0, pad=0.2, road_gap=1.0)

    def farmstead(self, x, z, facing):
        """Barn, silo, farmhouse and a walled yard; `facing` is the rotation of the house front."""
        self.add('barn', x, z, facing, pad=1.0)
        dx, dz = (1, 0) if facing in (0, 180) else (0, 1)
        self.add('silo', x + dx * 10, z + dz * 10, 0, pad=1.0)
        self.add('silo', x + dx * 15, z + dz * 15, 0, pad=1.0)
        self.add('cottage', x - dx * 13, z - dz * 13, facing, pad=1.0)
        self.add('truck', x + dz * 9, z + dx * 9, 90 if dx else 0, pad=0.8)
        for s in (-1, 1):
            self.add('stone_wall', x + dz * s * 16, z + dx * s * 16, 0 if dx else 90, pad=0.3)
            self.add('stone_wall', x + dz * s * 16 + dx * 7, z + dx * s * 16 + dz * 7, 0 if dx else 90, pad=0.3)

    def depot(self, px, pz, outward):
        """Fuel tanks inside the objective circle, a warehouse and water tower behind it."""
        ox, oz = outward
        # A row of tanks on the far side of the objective (the side away from the town).
        away = 1 if oz > 0 else -1
        for dx, dz in ((-6, 4.5), (0, 7.5), (6, 4.5)):
            self.add('fuel_tank', px + dx * away, pz + dz * away, 0, pad=0.8, ignore_points=True)
        rot = 180 if oz > 0 else 0
        self.add('warehouse', px + ox * 20, pz + oz * 20, rot, pad=1.0)
        self.add('water_tower', px + ox * 13 + oz * 12, pz + oz * 13 - ox * 12, 0, pad=1.0)
        self.add('garage', px - oz * 14 + ox * 6, pz + ox * 14 + oz * 6, 0, pad=1.0)
        self.add('truck', px - oz * 7, pz + ox * 7, 0, pad=0.8, ignore_points=True)
        for i in range(8):
            ang = self.rng.random() * math.tau
            r = self.rng.uniform(3, 9)
            self.add('barrel', px + math.cos(ang) * r, pz + math.sin(ang) * r, 0, pad=0.3, ignore_points=True)
        for i in range(3):
            self.add('ammo_crate', px - ox * 8 + i * 1.5 * oz, pz - oz * 8 - i * 1.5 * ox, 0, pad=0.2, ignore_points=True)
        # Sandbag positions on the side facing the town.
        self.add('sandbags', px - ox * 10, pz - oz * 10, 90 if abs(ox) > abs(oz) else 0, pad=0.4, ignore_points=True)

    # ------------------------------------------------------------------ checks
    def reachable(self):
        """Flood fill on the nav grid from the first camp; returns unreachable targets."""
        n = int(HALF * 2 / CELL)
        blocked = [[False] * n for _ in range(n)]
        for prop, (x0, z0, x1, z1) in zip(self.props, self.rects):
            if not PROPS[prop['def']].get('blocks', False):
                continue
            a0 = int(math.floor((x0 - CLEARANCE + HALF) / CELL))
            a1 = int(math.floor((x1 + CLEARANCE + HALF) / CELL))
            b0 = int(math.floor((z0 - CLEARANCE + HALF) / CELL))
            b1 = int(math.floor((z1 + CLEARANCE + HALF) / CELL))
            for gx in range(max(0, a0), min(n, a1 + 1)):
                for gz in range(max(0, b0), min(n, b1 + 1)):
                    # A cell is blocked when its centre falls inside the grown footprint.
                    cx = (gx + 0.5) * CELL - HALF
                    cz = (gz + 0.5) * CELL - HALF
                    if x0 - CLEARANCE <= cx <= x1 + CLEARANCE and z0 - CLEARANCE <= cz <= z1 + CLEARANCE:
                        blocked[gz][gx] = True

        def cell(x, z):
            return int((x + HALF) / CELL), int((z + HALF) / CELL)

        start = cell(*self.teams[0])
        seen = {start}
        todo = [start]
        while todo:
            gx, gz = todo.pop()
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                c = (gx + dx, gz + dz)
                if 0 <= c[0] < n and 0 <= c[1] < n and c not in seen and not blocked[c[1]][c[0]]:
                    seen.add(c)
                    todo.append(c)
        targets = [('camp', t[0], t[1]) for t in self.teams[1:]] + [('point', p[0], p[1]) for p in self.points]
        return [t for t in targets if cell(t[1], t[2]) not in seen]


def ashfield(seed=11):
    teams = [(-58.0, -58.0), (58.0, 58.0)]
    points = [(-30.0, 46.0, 11.0), (0.0, 0.0, 16.0), (30.0, -46.0, 11.0)]
    L = Layout(seed, teams, points)

    # Roads: a paved square with a ring road, an outer lane round the town, four streets out
    # into the country, and the camp roads joining the lane's corners.
    L.road(26, -6, 0, 6, 0)                                     # paved square
    L.road(7, -17, -17, 17, -17, 17, 17, -17, 17, -17, -17)     # ring road
    L.road(5, -42, -42, 42, -42, 42, 42, -42, 42, -42, -42)     # outer lane
    L.road(6, -17, 0, -78, 0)
    L.road(6, 17, 0, 78, 0)
    L.road(6, 0, 17, 0, 78)
    L.road(6, 0, -17, 0, -78)
    L.road(5, -58, -58, -42, -42)                               # camp roads
    L.road(5, 58, 58, 42, 42)

    # Depots first: their objectives shape everything around them.
    L.depot(-30, 46, (-0.6, 0.8))
    L.depot(30, -46, (0.6, -0.8))

    # The church stands just outside town on the north lane; a second landmark faces it south.
    L.add('church', 14, 55, 180, pad=0.5)
    L.add('apartment', -12, -49.5, 0, pad=0.5)

    # Around the square: shops, townhouses and apartments facing it across the ring road.
    ring = {
        ('x', 1): ['shop', 'townhouse', 'apartment', 'shop'],
        ('x', -1): ['apartment', 'shop', 'townhouse', 'shop'],
        ('z', 1): ['townhouse', 'shop', 'apartment', 'townhouse'],
        ('z', -1): ['shop', 'apartment', 'townhouse', 'shop'],
    }
    for (axis, side), kinds in ring.items():
        for direction in (1, -1):
            L.frontage(axis, 17 * side, side, 4.5 * direction, 40 * direction, kinds, setback=1.5, alley_every=(2, 3),
                       yards=False, cars=0.5)

    # Back rows facing the outer lane from inside town: small buildings, garages, sheds.
    small = ['cottage', 'garage', 'shop', 'cottage', 'garage']
    for axis in ('x', 'z'):
        for side in (1, -1):
            for direction in (1, -1):
                L.frontage(axis, 42 * side, -side, 5 * direction, 38 * direction, small, setback=1.2, road_half=2.5,
                           alley_every=(1, 2), yards=False, cars=0.25)

    # Streets out of town, between the ring and the lane.
    houses = ['house_small', 'cottage', 'townhouse', 'ruin', 'garage', 'cottage', 'house_small']
    for axis, sign in (('x', 1), ('x', -1), ('z', 1), ('z', -1)):
        for side in (1, -1):
            kinds = houses[:]
            L.rng.shuffle(kinds)
            L.frontage(axis, 0, side, 22 * sign, 38 * sign, kinds, setback=1.5, alley_every=(1, 2), yards=False, cars=0.3)

    # Beyond the lane: houses with gardens facing it, and along the country roads.
    outer = ['house_large', 'cottage', 'house_small', 'ruin', 'cottage', 'townhouse', 'garage', 'house_large', 'cottage']
    for axis in ('x', 'z'):
        for side in (1, -1):
            for direction in (1, -1):
                kinds = outer[:]
                L.rng.shuffle(kinds)
                L.frontage(axis, 42 * side, side, 5 * direction, 44 * direction, kinds, setback=2.5, road_half=2.5,
                           alley_every=(1, 2), cars=0.3)
    for axis, sign in (('x', 1), ('x', -1), ('z', 1), ('z', -1)):
        for side in (1, -1):
            kinds = outer[:]
            L.rng.shuffle(kinds)
            L.frontage(axis, 0, side, 48 * sign, 70 * sign, kinds, setback=3.0, alley_every=(1, 1), cars=0.2)

    # Farmsteads on the open flanks.
    L.farmstead(-66, -24, 90)
    L.farmstead(66, 24, 270)

    # Rock cover and earthworks along the approaches from the camps.
    cover = (('cliff_a', -50, -30, 90), ('cliff_b', 50, 30, 90), ('cliff_a', -30, -52, 0), ('cliff_b', 30, 52, 0),
             ('boulders', -46, -48, 0), ('boulders', 46, 48, 0), ('boulders', -70, -42, 0), ('boulders', 70, 42, 0),
             ('dirt_mound', -36, -58, 90), ('dirt_mound', 36, 58, 90), ('dirt_mound', -58, -36, 0), ('dirt_mound', 58, 36, 0),
             ('tank_trap', -46, -40, 0), ('tank_trap', -40, -46, 0), ('tank_trap', 46, 40, 0), ('tank_trap', 40, 46, 0),
             ('sandbags', -38, -47, 0), ('sandbags', -47, -38, 90), ('sandbags', 38, 47, 0), ('sandbags', 47, 38, 90))
    for def_id, x, z, rot in cover:
        L.add(def_id, x, z, rot, pad=1.0)

    # Forests fill the two empty corners; copses and tree lines break up the fields.
    L.forest(-62, 60, 22, 0.24)
    L.forest(62, -60, 22, 0.24)
    L.forest(-70, 36, 9, 0.14)
    L.forest(70, -36, 9, 0.14)
    L.forest(40, 66, 9, 0.12)
    L.forest(-40, -66, 9, 0.12)
    L.forest(-66, -20, 7, 0.12)
    L.forest(66, 20, 7, 0.12)
    for x0, z0, x1, z1 in ((-54, -34, -30, -44), (54, 34, 30, 44), (-70, -6, -46, -6), (70, 6, 46, 6), (-6, 70, -6, 46),
                           (6, -70, 6, -46), (-34, -54, -44, -30), (34, 54, 44, 30)):
        L.tree_line(x0, z0, x1, z1)

    missing = L.reachable()
    if missing:
        raise SystemExit(f'Unreachable from the first camp: {missing}')
    return L


def dump(path, comment, meta, layout):
    out = [f'// {comment}', '// Generated by Tools/maps/build_ashfield.py: edit the script, not this file.', '{']
    fields = []
    for key, value in meta.items():
        fields.append(f'  "{key}": {json.dumps(value)}')
    fields.append('  "roads": [\n' + ',\n'.join('    ' + json.dumps(r) for r in layout.roads) + '\n  ]')
    fields.append('  "props": [\n' + ',\n'.join('    ' + json.dumps(p) for p in layout.props) + '\n  ]')
    out.append(',\n\n'.join(fields))
    out.append('}')
    path.write_text('\n'.join(out) + '\n', encoding='utf-8')


def main():
    layout = ashfield()
    counts = {}
    for p in layout.props:
        counts[p['def']] = counts.get(p['def'], 0) + 1
    print(f'{len(layout.props)} props:', dict(sorted(counts.items())))

    teams = [{'team': 0, 'x': -58, 'z': -58}, {'team': 1, 'x': 58, 'z': 58}]
    dump(DATA / 'maps' / 'ashfield_conquest.json',
         'Ashfield for Conquest: a town square between two fuel depots, camps south-west and north-east.',
         {
             'id': 'ashfield_conquest', 'size': 160, 'teams': teams,
             'points': [
                 {'id': 'west', 'name': 'depot_west', 'x': -30, 'z': 46, 'radius': 11},
                 {'id': 'town', 'name': 'town', 'x': 0, 'z': 0, 'radius': 16},
                 {'id': 'east', 'name': 'depot_east', 'x': 30, 'z': -46, 'radius': 11},
             ],
             'units': [
                 {'def': 'scout_jeep', 'team': 0, 'x': -50, 'z': -58, 'heading': 45},
                 {'def': 'scout_jeep', 'team': 0, 'x': -58, 'z': -50, 'heading': 45},
                 {'def': 'apc', 'team': 0, 'x': -53, 'z': -53, 'heading': 45},
                 {'def': 'light_tank', 'team': 0, 'x': -60, 'z': -60, 'heading': 45},
                 {'def': 'scout_jeep', 'team': 1, 'x': 50, 'z': 58, 'heading': 225},
                 {'def': 'scout_jeep', 'team': 1, 'x': 58, 'z': 50, 'heading': 225},
                 {'def': 'apc', 'team': 1, 'x': 53, 'z': 53, 'heading': 225},
                 {'def': 'light_tank', 'team': 1, 'x': 60, 'z': 60, 'heading': 225},
             ],
         }, layout)
    dump(DATA / 'maps' / 'ashfield_sandbox.json',
         'Ashfield for Survival: the same town, holding out against waves from the north-east.',
         {
             'id': 'ashfield_sandbox', 'size': 160, 'teams': teams,
             'units': [
                 {'def': 'light_tank', 'team': 0, 'x': -50, 'z': -58, 'heading': 45},
                 {'def': 'light_tank', 'team': 0, 'x': -58, 'z': -50, 'heading': 45},
                 {'def': 'main_battle_tank', 'team': 0, 'x': -53, 'z': -53, 'heading': 45},
                 {'def': 'scout_jeep', 'team': 0, 'x': -61, 'z': -46, 'heading': 45},
                 {'def': 'scout_jeep', 'team': 0, 'x': -46, 'z': -61, 'heading': 45},
                 {'def': 'artillery', 'team': 0, 'x': -63, 'z': -63, 'heading': 45},
                 {'def': 'light_tank', 'team': 1, 'x': 50, 'z': 58, 'heading': 225},
                 {'def': 'light_tank', 'team': 1, 'x': 58, 'z': 50, 'heading': 225},
                 {'def': 'main_battle_tank', 'team': 1, 'x': 53, 'z': 53, 'heading': 225},
                 {'def': 'scout_jeep', 'team': 1, 'x': 46, 'z': 61, 'heading': 225},
             ],
         }, layout)


if __name__ == '__main__':
    main()
