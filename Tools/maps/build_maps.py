"""Generate every battlefield (Conquest and Survival versions) into Resources/Data/maps.

    python Tools/maps/build_maps.py

The layouts are designed, not random. Random numbers (fixed seed) only vary building types,
gaps and tree placement, so the output is stable.
  * Ashfield (temperate): a paved square with a ring road, streets of houses facing the
    street, fuel depots at the side objectives, farmsteads, rock cover, forests in the corners.
  * Dunebreak (desert): a refinery of towers, pipes and storage tanks at the centre, an oasis
    market town and a pumpjack oil field at the sides, mesas and cactus scrub.
  * Frostpeak (snow): a log-cabin village, a radar station on the western heights and a
    lumber camp, all inside thick snowy pine forest.
  * Ironport (harbour): quays with gantry cranes and container stacks on the north shore, a
    factory district at the centre and a rail yard of tank wagons and boxcars.

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
             'warehouse', 'garage', 'water_tower', 'ruin', 'fuel_tank', 'wall', 'adobe_house', 'adobe_large',
             'refinery_tower', 'storage_tank', 'oil_pump', 'log_cabin', 'radar_station', 'watchtower', 'factory',
             'office_block', 'gantry_crane', 'container', 'container_stack', 'rail_tanker', 'rail_boxcar'}


class Layout:
    def __init__(self, seed, teams, points, clear=((-13, -13, 13, 13),)):
        self.rng = random.Random(seed)
        self.teams = teams
        self.points = points
        self.clear = clear  # rectangles (x0, z0, x1, z1) kept open: squares, plazas
        self.props = []
        self.rects = []
        self.roads = []
        self.failed = []

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
        # Squares and plazas stay open.
        for (c0, d0, c1, d1) in self.clear:
            if x1 > c0 and x0 < c1 and z1 > d0 and z0 < d1:
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

    def add(self, def_id, x, z, rot=0, pad=1.0, road_gap=0.8, ignore_points=False, must=False):
        x, z = round(x * 2) / 2, round(z * 2) / 2
        if not self.free(def_id, x, z, rot, pad, road_gap, ignore_points):
            if must:
                self.failed.append((def_id, x, z))
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
    def forest(self, cx, cz, radius, density, kind='tree'):
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
            if self.add(kind, cx + math.cos(a) * r, cz + math.sin(a) * r, 0, pad=0.2, road_gap=1.0):
                count -= 1

    def tree_line(self, x0, z0, x1, z1, spacing=4.0, kind='tree'):
        length = math.hypot(x1 - x0, z1 - z0)
        for i in range(int(length / spacing) + 1):
            t = i / max(1, int(length / spacing))
            self.add(kind, x0 + (x1 - x0) * t + self.rng.uniform(-0.8, 0.8), z0 + (z1 - z0) * t + self.rng.uniform(-0.8, 0.8),
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
        self.scatter('truck', px, pz, 4, 9, 1, pad=0.8)
        self.scatter('barrel', px, pz, 2, 9, 12, pad=0.3)
        self.scatter('ammo_crate', px, pz, 3, 9, 5, pad=0.3)
        # Sandbag positions on the side facing the town.
        self.add('sandbags', px - ox * 10, pz - oz * 10, 90 if abs(ox) > abs(oz) else 0, pad=0.4, ignore_points=True)

    # ------------------------------------------------------------------ checks
    def near(self, def_id, cx, cz, radius, rot=0, pad=1.0):
        """One copy placed as close to a point as it fits (hand-placed features)."""
        for attempt in range(200):
            r = radius * math.sqrt(attempt / 200)
            a = self.rng.random() * math.tau
            if self.add(def_id, cx + math.cos(a) * r, cz + math.sin(a) * r, rot, pad=pad):
                return True
        self.failed.append((def_id, cx, cz))
        return False

    def scatter(self, def_id, cx, cz, r0, r1, count, pad):
        """`count` copies in a ring round a point, retrying until they fit (depot clutter)."""
        placed = 0
        for _ in range(count * 40):
            if placed >= count:
                break
            a = self.rng.random() * math.tau
            r = self.rng.uniform(r0, r1)
            rot = self.rng.choice([0, 90]) if def_id == 'truck' else 0
            if self.add(def_id, cx + math.cos(a) * r, cz + math.sin(a) * r, rot, pad=pad, road_gap=None, ignore_points=True):
                placed += 1
        if placed < count:
            self.failed.append((def_id, cx, cz))

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
    L.add('church', 14, 55, 180, pad=0.5, must=True)
    L.add('apartment', -12, -51.5, 0, pad=0.5, must=True)

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

    # Rock cover and earthworks along the approaches from the camps (clear of the camps themselves).
    cover = (('cliff_a', -34, -62, 0), ('boulders', -30, -48, 0), ('boulders', -48, -30, 0),
             ('dirt_mound', -24, -62, 0), ('dirt_mound', -62, -24, 90), ('tank_trap', -36, -44, 0), ('tank_trap', -44, -36, 0),
             ('sandbags', -32, -40, 0), ('sandbags', -40, -32, 90))
    for def_id, x, z, rot in cover:
        L.near(def_id, x, z, 12, rot)
        L.near(def_id, -x, -z, 12, rot)

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

    return finish(L)


def dump(path, comment, meta, layout):
    out = [f'// {comment}', '// Generated by Tools/maps/build_maps.py: edit the script, not this file.', '{']
    fields = []
    for key, value in meta.items():
        fields.append(f'  "{key}": {json.dumps(value)}')
    fields.append('  "roads": [\n' + ',\n'.join('    ' + json.dumps(r) for r in layout.roads) + '\n  ]')
    fields.append('  "props": [\n' + ',\n'.join('    ' + json.dumps(p) for p in layout.props) + '\n  ]')
    out.append(',\n\n'.join(fields))
    out.append('}')
    path.write_text('\n'.join(out) + '\n', encoding='utf-8')


def row(L, def_id, x0, z0, x1, z1, gap, rot=0, pad=0.4, road_gap=0.8, ignore_points=False):
    """Copies of a prop along a line, `gap` metres apart end to end (containers, wagons, pipes)."""
    w, d = Layout.size(def_id, rot)
    along = w if abs(x1 - x0) >= abs(z1 - z0) else d
    length = math.hypot(x1 - x0, z1 - z0)
    step = along + gap
    placed = 0
    u = along / 2
    while u <= length - along / 2 + 1e-6:
        t = u / length
        if L.add(def_id, x0 + (x1 - x0) * t, z0 + (z1 - z0) * t, rot, pad=pad, road_gap=road_gap, ignore_points=ignore_points):
            placed += 1
        u += step
    return placed


def ring_of(L, def_id, cx, cz, radius, count, start=0.0, pad=0.3):
    for i in range(count):
        a = start + i * math.tau / count
        L.add(def_id, cx + math.cos(a) * radius, cz + math.sin(a) * radius, 0, pad=pad, road_gap=0.5)


def approach_cover(L, pieces):
    """Cover on the approaches from both camps, mirrored through the centre."""
    for def_id, x, z, rot in pieces:
        L.near(def_id, x, z, 12, rot)
        L.near(def_id, -x, -z, 12, rot)


def dunebreak(seed=23):
    teams = [(-58.0, -58.0), (58.0, 58.0)]
    points = [(-30.0, 46.0, 12.0), (0.0, 0.0, 16.0), (30.0, -46.0, 12.0)]
    L = Layout(seed, teams, points, clear=((-8, -8, 8, 8),))

    # A perimeter road round the refinery, highways out to the desert, a street through the
    # oasis town and a track along the oil field.
    L.road(7, -24, -24, 24, -24, 24, 24, -24, 24, -24, -24)
    L.road(6, -24, 0, -78, 0)
    L.road(6, 24, 0, 78, 0)
    L.road(6, 0, 24, 0, 78)
    L.road(6, 0, -24, 0, -78)
    L.road(5, -58, -58, -24, -24)
    L.road(5, 58, 58, 24, 24)
    L.road(6, -3, 46, -74, 46)
    L.road(5, -3, 66, -74, 66)
    L.road(5, 3, -46, 74, -46)

    # The refinery: two cracking towers inside the objective, pipes to four storage tanks. Hit
    # one and the chain of fireballs can take the plant apart.
    L.add('refinery_tower', -12, 6, 0, pad=0.8, ignore_points=True, must=True)
    L.add('refinery_tower', 12, -6, 0, pad=0.8, ignore_points=True, must=True)
    L.add('pipeline', -12, -2, 90, pad=0.6, ignore_points=True)
    L.add('pipeline', 12, 2, 90, pad=0.6, ignore_points=True)
    L.add('pipeline', 4, 14, 0, pad=0.6, ignore_points=True)
    L.add('pipeline', -4, -14, 0, pad=0.6, ignore_points=True)
    for x, z in ((14, 14), (-14, -14)):
        L.add('storage_tank', x, z, 0, pad=0.8, ignore_points=True, must=True)
    for x, z in ((-37, -12), (37, 12)):
        L.add('storage_tank', x, z, 0, pad=0.8, must=True)
        L.scatter('fuel_tank', x, z, 8, 11, 2, pad=0.8)
    for x, z in ((-14, 14), (14, -14)):
        L.scatter('barrel', x, z, 1, 5, 6, pad=0.3)
        L.add('jersey_barrier', x, z - 4, 0, pad=0.4, ignore_points=True)
    L.add('watchtower', -20, 20, 0, pad=0.5, ignore_points=True)
    L.add('watchtower', 20, -20, 0, pad=0.5, ignore_points=True)

    # Oasis market town on the western objective: stalls and palms round the plaza, adobe
    # houses facing the street.
    for x in (-37, -30, -23):
        L.add('market_stall', x, 40.5, 0, pad=0.4)
        L.add('market_stall', x, 51.5, 180, pad=0.4)
    ring_of(L, 'palm', -30, 46, 13.5, 12, 0.2)
    ring_of(L, 'palm', -30, 46, 8.5, 6, 0.5)
    adobe = ['adobe_house', 'adobe_house', 'adobe_large', 'adobe_house', 'adobe_house', 'adobe_large']
    for side in (1, -1):
        for start, end in ((-5, -16), (-46, -72)):
            kinds = adobe[:]
            L.rng.shuffle(kinds)
            L.frontage('x', 46, side, start, end, kinds, setback=1.2, alley_every=(2, 3), yards=False, cars=0.25)
    kinds = adobe[:]
    L.rng.shuffle(kinds)
    L.frontage('x', 66, 1, -5, -72, kinds, setback=1.0, road_half=2.5, alley_every=(2, 3), yards=False, cars=0.2)
    # Roadside strips along the highways: workshops, houses and walls.
    strip = ['adobe_house', 'garage', 'adobe_house', 'adobe_large', 'wall', 'adobe_house', 'garage']
    for sign in (1, -1):
        for side in (1, -1):
            kinds = strip[:]
            L.rng.shuffle(kinds)
            L.frontage('x', 0, side, 30 * sign, 74 * sign, kinds, setback=1.8, alley_every=(1, 2), yards=False, cars=0.3)
    L.forest(-52, 64, 9, 0.12, kind='palm')
    L.forest(-8, 62, 6, 0.1, kind='palm')

    # Oil field on the eastern objective: pumpjacks, a pipeline with gaps, tanks and trucks.
    for x, z in ((21, -38), (39, -54)):
        L.add('oil_pump', x, z, 0, pad=1.0, ignore_points=True)
    for x, z in ((52, -36), (12, -58), (50, -62), (64, -52), (8, -34), (28, -66), (62, -30), (40, -30)):
        L.add('oil_pump', x, z, L.rng.choice([0, 90]), pad=1.2)
    row(L, 'pipeline', 6, -28.5, 70, -28.5, 7, 0, pad=0.4)
    L.add('storage_tank', 62, -66, 0, pad=0.8)
    L.scatter('fuel_tank', 30, -46, 5, 9, 2, pad=0.8)
    L.scatter('truck', 30, -46, 4, 9, 2, pad=0.8)
    L.scatter('barrel', 30, -46, 2, 9, 10, pad=0.3)
    L.scatter('ammo_crate', 30, -46, 3, 9, 4, pad=0.3)
    L.add('sandbags', 40, -40, 90, pad=0.4, ignore_points=True)
    L.add('sandbags', 20, -52, 90, pad=0.4, ignore_points=True)

    # Hamlets on the flanks.
    for x, z, facing in ((-66, -24, 90), (66, 24, 270)):
        L.near('adobe_large', x, z, 6, facing)
        L.near('adobe_house', x, z + 12, 8, facing)
        L.near('adobe_house', x, z - 12, 8, facing)
        L.near('market_stall', x + 9, z, 6, facing)

    # Mesas and rock on the approaches and in the empty corners; cactus scrub everywhere.
    approach_cover(L, (('boulders', -30, -48, 0), ('boulders', -48, -30, 0), ('dirt_mound', -24, -62, 0),
                       ('dirt_mound', -62, -24, 90), ('tank_trap', -36, -44, 0), ('tank_trap', -44, -36, 0),
                       ('sandbags', -32, -40, 0), ('sandbags', -40, -32, 90), ('cliff_a', -34, -64, 0)))
    for x, z in ((-70, 30), (70, -30), (20, 70), (-20, -70)):
        L.near('mesa', x, z, 10, L.rng.choice([0, 90]))
    # Rock outcrops in the open desert: the only cover between the town and the plant.
    for def_id, x, z in (('cliff_b', -44, 20), ('boulders', -30, 22), ('cliff_a', -50, -8), ('boulders', -14, 36),
                         ('cliff_b', 20, 36), ('boulders', 36, 30), ('cliff_a', 44, -60), ('boulders', 12, -36),
                         ('cliff_b', -20, -36), ('boulders', -36, -28), ('dirt_mound', -8, 32), ('dirt_mound', 8, -32)):
        L.near(def_id, x, z, 8, L.rng.choice([0, 90]))
        L.near(def_id, -x, -z, 8, L.rng.choice([0, 90]))
    for cx, cz, r in ((-60, 40, 10), (60, -40, 10), (-20, 66, 8), (20, -66, 8), (-66, -6, 8), (66, 6, 8),
                      (44, 40, 9), (-44, -40, 9), (-40, 20, 7), (40, -20, 7), (18, 40, 6), (-18, -40, 6)):
        L.forest(cx, cz, r, 0.05, kind='cactus')

    return finish(L)


def frostpeak(seed=37):
    teams = [(-58.0, -58.0), (58.0, 58.0)]
    points = [(-30.0, 46.0, 11.0), (0.0, 0.0, 16.0), (30.0, -46.0, 11.0)]
    L = Layout(seed, teams, points)

    L.road(7, -17, -17, 17, -17, 17, 17, -17, 17, -17, -17)     # village ring
    L.road(6, -17, 0, -78, 0)
    L.road(6, 17, 0, 78, 0)
    L.road(6, 0, 17, 0, 78)
    L.road(6, 0, -17, 0, -78)
    L.road(5, -58, -58, -17, -17)
    L.road(5, 58, 58, 17, 17)
    L.road(5, -3, 46, -19, 46)                                  # track up to the radar
    L.road(5, 3, -46, 19, -46)                                  # track to the lumber camp

    # The radar station crowns the western heights, watched by towers and ringed with rock.
    L.add('radar_station', -30, 62, 0, pad=1.0, must=True)
    L.add('watchtower', -43, 54, 0, pad=0.6)
    L.add('watchtower', -17, 37, 0, pad=0.6)
    for x, z, rot in ((-30, 37, 0), (-39, 44, 90), (-21, 50, 90)):
        L.add('sandbags', x, z, rot, pad=0.4, ignore_points=True)
    for def_id, x, z in (('cliff_a', -52, 64), ('cliff_b', -12, 66), ('snow_rock', -46, 34), ('snow_rock', -14, 58),
                         ('snow_rock', -50, 48), ('cliff_b', -56, 36), ('snow_rock', -26, 72), ('snow_rock', -40, 70)):
        L.near(def_id, x, z, 6)

    # The village: log cabins and cottages round the square, a church to the north.
    L.add('church', 14, 40, 180, pad=0.5, must=True)
    ring = ['log_cabin', 'cottage', 'log_cabin', 'house_small', 'log_cabin', 'townhouse']
    for axis in ('x', 'z'):
        for side in (1, -1):
            for direction in (1, -1):
                kinds = ring[:]
                L.rng.shuffle(kinds)
                L.frontage(axis, 17 * side, side, 4.5 * direction, 36 * direction, kinds, setback=1.5, alley_every=(2, 3),
                           yards=True, cars=0.3)
                L.frontage(axis, 17 * side, -side, 4.5 * direction, 12 * direction, kinds, setback=1.2, alley_every=(1, 1),
                           yards=False, cars=0.0)
    outer = ['log_cabin', 'barn', 'log_cabin', 'cottage', 'house_large', 'log_cabin']
    for axis, sign in (('x', 1), ('x', -1), ('z', 1), ('z', -1)):
        for side in (1, -1):
            kinds = outer[:]
            L.rng.shuffle(kinds)
            L.frontage(axis, 0, side, 22 * sign, 70 * sign, kinds, setback=2.0, alley_every=(1, 2), cars=0.2)

    # Lumber camp on the eastern objective: fuel, a warehouse, trucks and cabins.
    L.depot(30, -46, (0.6, -0.8))
    L.near('log_cabin', 16, -62, 6, 0)
    L.near('log_cabin', 46, -30, 6, 90)
    L.near('watchtower', 44, -58, 6)

    L.farmstead(-66, -24, 90)
    L.farmstead(66, 24, 270)

    approach_cover(L, (('snow_rock', -30, -48, 0), ('snow_rock', -48, -30, 0), ('dirt_mound', -24, -62, 0),
                       ('dirt_mound', -62, -24, 90), ('tank_trap', -36, -44, 0), ('tank_trap', -44, -36, 0),
                       ('sandbags', -32, -40, 0), ('sandbags', -40, -32, 90), ('cliff_a', -34, -64, 0)))

    # Thick snowy pine forest: the corners, the flanks and tree lines along every track.
    for cx, cz, r, d in ((-62, 62, 24, 0.3), (62, -62, 24, 0.3), (-70, 30, 11, 0.22), (70, -30, 11, 0.22),
                         (38, 66, 12, 0.22), (-38, -66, 12, 0.22), (-66, -2, 8, 0.18), (66, 2, 8, 0.18),
                         (40, 40, 9, 0.16), (-40, -40, 7, 0.12), (24, 60, 8, 0.2), (-24, -62, 7, 0.16),
                         (-48, 20, 8, 0.16), (48, -20, 8, 0.16)):
        L.forest(cx, cz, r, d)
    for x0, z0, x1, z1 in ((-54, -34, -30, -44), (54, 34, 30, 44), (-70, -6, -46, -6), (70, 6, 46, 6), (-6, 70, -6, 46),
                           (6, -70, 6, -46), (-34, -54, -44, -30), (34, 54, 44, 30), (-8, 22, -8, 34), (8, -22, 8, -34)):
        L.tree_line(x0, z0, x1, z1, spacing=3.5)

    return finish(L)


def ironport(seed=53):
    teams = [(-58.0, -58.0), (58.0, 58.0)]
    points = [(-30.0, 48.0, 12.0), (0.0, 0.0, 16.0), (30.0, -46.0, 12.0)]
    L = Layout(seed, teams, points, clear=((-10, -10, 10, 10),))

    L.road(7, -78, 57, 44, 57)                                  # quayside road
    L.road(7, -18, -18, 18, -18, 18, 18, -18, 18, -18, -18)     # ring round the factory square
    L.road(6, -18, 0, -78, 0)
    L.road(6, 18, 0, 78, 0)
    L.road(6, 0, 18, 0, 57)
    L.road(6, 0, -18, 0, -78)
    L.road(5, -58, -58, -18, -18)
    L.road(5, 58, 58, 18, 18)
    L.road(3, 5, -39, 78, -39)                                  # rail tracks
    L.road(3, 5, -53, 78, -53)

    # Quays on the north shore: bollards on the edge, gantry cranes over the berths.
    row(L, 'dock_bollards', -76, 77, 40, 77, 5, 0, pad=0.3, road_gap=None)
    for x in (-56, -30, -4):
        L.add('gantry_crane', x, 70, 0, pad=0.6, must=True)
    L.add('warehouse', 24, 68, 180, pad=0.8)

    # Container yard round the docks objective: stacks in rows with lanes between.
    for x in (-74, -66, -58, -50, -44):
        for z in (28, 38, 48):
            kind = 'container_stack' if L.rng.random() < 0.7 else 'container'
            L.add(kind, x, z, 90, pad=0.5)
    for x, z, rot in ((-36, 44, 0), (-24, 52, 0), (-30, 40, 90), (-22, 44, 90)):
        L.add('container', x, z, rot, pad=0.6, ignore_points=True)
    for x in (-14, -8):
        for z in (30, 40):
            L.add('container_stack', x, z, 90, pad=0.5)
    L.scatter('truck', -30, 48, 6, 11, 2, pad=0.8)

    # Factory district: two works either side of the square, offices round the ring.
    L.add('factory', -37, -12, 0, pad=1.0, must=True)
    L.add('factory', 37, 12, 180, pad=1.0, must=True)
    offices = ['office_block', 'warehouse', 'office_block', 'garage', 'shop', 'office_block']
    for axis in ('x', 'z'):
        for side in (1, -1):
            for direction in (1, -1):
                kinds = offices[:]
                L.rng.shuffle(kinds)
                L.frontage(axis, 18 * side, side, 4.5 * direction, 44 * direction, kinds, setback=1.5, alley_every=(1, 2),
                           yards=False, cars=0.45)
    for x, z in ((-9, 12), (9, -12), (12, 9), (-12, -9)):
        L.add('jersey_barrier', x, z, 0 if abs(z) > abs(x) else 90, pad=0.4, ignore_points=True)
    for i in range(-3, 4):
        for side in (1, -1):
            L.add('lamp_post', i * 11 + 5, side * 22.5, 0, pad=0.2, road_gap=0.2)
            L.add('lamp_post', side * 22.5, i * 11 - 5, 0, pad=0.2, road_gap=0.2)
    for x in range(-70, 44, 14):
        L.add('lamp_post', x, 61.5, 0, pad=0.2, road_gap=0.2)

    # Rail yard on the eastern objective: tank wagons and boxcars on two tracks, with gaps.
    for z in (-39, -53):
        x = 9.0
        while x < 76:
            kind = 'rail_tanker' if L.rng.random() < 0.45 else 'rail_boxcar'
            # Leave the middle of the objective open to fight over.
            if abs(x + 5.5 - 30) > 7:
                L.add(kind, x + 5.5, z, 0, pad=0.3, road_gap=None, ignore_points=True)
            x += 11 + L.rng.choice([3.5, 4, 5])
    L.add('warehouse', 50, -68, 0, pad=0.8)
    L.add('warehouse', 20, -70, 0, pad=0.8)
    L.add('water_tower', 64, -66, 0, pad=0.8)
    L.scatter('fuel_tank', 30, -46, 4, 8, 2, pad=0.8)
    L.scatter('barrel', 30, -46, 2, 10, 10, pad=0.3)
    L.scatter('ammo_crate', 30, -46, 3, 10, 4, pad=0.3)

    approach_cover(L, (('jersey_barrier', -30, -48, 0), ('jersey_barrier', -48, -30, 90), ('dirt_mound', -24, -62, 0),
                       ('dirt_mound', -62, -24, 90), ('tank_trap', -36, -44, 0), ('tank_trap', -44, -36, 0),
                       ('sandbags', -32, -40, 0), ('sandbags', -40, -32, 90), ('boulders', -34, -64, 0)))
    for x, z in ((-66, -24), (66, 24)):
        L.near('warehouse', x, z, 8, 90)
        L.near('container_stack', x + 10, z + 10, 6, 0)
        L.near('container_stack', x - 10, z - 10, 6, 0)

    # Scrubby parkland on the south and east edges.
    for cx, cz, r, d in ((-62, -2, 8, 0.14), (66, -8, 8, 0.14), (-40, -68, 9, 0.12), (68, 40, 7, 0.1),
                         (-6, -66, 7, 0.1), (46, -22, 6, 0.1)):
        L.forest(cx, cz, r, d)
    L.tree_line(-70, -10, -46, -10)
    L.tree_line(46, 8, 70, 8)

    return finish(L)


def finish(L):
    for def_id, x, z in L.failed:
        print(f'warning: could not place {def_id} near ({x}, {z})')
    missing = L.reachable()
    if missing:
        raise SystemExit(f'Unreachable from the first camp: {missing}')
    return L


TEAMS = [{'team': 0, 'x': -58, 'z': -58}, {'team': 1, 'x': 58, 'z': 58}]
CONQUEST_UNITS = [
    {'def': 'scout_jeep', 'team': 0, 'x': -50, 'z': -58, 'heading': 45},
    {'def': 'scout_jeep', 'team': 0, 'x': -58, 'z': -50, 'heading': 45},
    {'def': 'apc', 'team': 0, 'x': -53, 'z': -53, 'heading': 45},
    {'def': 'light_tank', 'team': 0, 'x': -60, 'z': -60, 'heading': 45},
    {'def': 'scout_jeep', 'team': 1, 'x': 50, 'z': 58, 'heading': 225},
    {'def': 'scout_jeep', 'team': 1, 'x': 58, 'z': 50, 'heading': 225},
    {'def': 'apc', 'team': 1, 'x': 53, 'z': 53, 'heading': 225},
    {'def': 'light_tank', 'team': 1, 'x': 60, 'z': 60, 'heading': 225},
]
SURVIVAL_UNITS = [
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
]

MAPS = [
    # id, builder, theme, point names (west, town, east), conquest comment, survival comment
    ('ashfield', ashfield, 'temperate', ('depot_west', 'town', 'depot_east'),
     'Ashfield for Conquest: a town square between two fuel depots, camps south-west and north-east.',
     'Ashfield for Survival: the same town, holding out against waves from the north-east.'),
    ('dunebreak', dunebreak, 'desert', ('oasis', 'refinery', 'oilfield'),
     'Dunebreak for Conquest: a refinery between an oasis town and an oil field, camps south-west and north-east.',
     'Dunebreak for Survival: the same desert, holding out against waves from the north-east.'),
    ('frostpeak', frostpeak, 'snow', ('radar', 'village', 'lumber_camp'),
     'Frostpeak for Conquest: a snowbound village between a radar station and a lumber camp.',
     'Frostpeak for Survival: the same valley, holding out against waves from the north-east.'),
    ('ironport', ironport, 'harbor', ('docks', 'factories', 'rail_yard'),
     'Ironport for Conquest: docks, a factory district and a rail yard on the northern shore.',
     'Ironport for Survival: the same port, holding out against waves from the north-east.'),
]


def main():
    for map_id, build, theme, names, conquest, survival in MAPS:
        layout = build()
        counts = {}
        for p in layout.props:
            counts[p['def']] = counts.get(p['def'], 0) + 1
        print(f'{map_id}: {len(layout.props)} props:', dict(sorted(counts.items())))
        points = [{'id': pid, 'name': name, 'x': x, 'z': z, 'radius': r}
                  for pid, name, (x, z, r) in zip(('west', 'town', 'east'), names, layout.points)]
        dump(DATA / 'maps' / f'{map_id}_conquest.json', conquest,
             {'id': f'{map_id}_conquest', 'theme': theme, 'size': 160, 'teams': TEAMS, 'points': points,
              'units': CONQUEST_UNITS}, layout)
        dump(DATA / 'maps' / f'{map_id}_sandbox.json', survival,
             {'id': f'{map_id}_sandbox', 'theme': theme, 'size': 160, 'teams': TEAMS, 'units': SURVIVAL_UNITS}, layout)


if __name__ == '__main__':
    main()
