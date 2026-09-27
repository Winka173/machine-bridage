"""Generate every battlefield (Conquest, Survival and Siege versions) into Resources/Data/maps.

The layouts are designed, not random. Random numbers (fixed seed) only vary building types,
gaps and tree placement, so the output is stable.
  * Ashfield (temperate): a paved square with a ring road, streets of houses facing the
    street, fuel depots at the side objectives, farmsteads, rock cover, forests in the corners.
  * Dunebreak (desert): a refinery of towers, pipes and storage tanks at the centre, an oasis
    market town and a pumpjack oil field at the sides, mesas and rock formations with scree,
    boulder fields and cactus scrub.
  * Frostpeak (snow): a log-cabin village in a clearing carved out of thick snowy pine forest,
    a radar station on the western heights, a lumber camp, snow rock in the woods.
  * Ironport (harbour): quays with gantry cranes and a container yard of tidy bays on the north
    shore, a factory district at the centre and a rail yard of coupled tank wagons and boxcars.
  * Redrock Canyon (desert): two long walls of mesa and cliff split the floor into three
    canyon lanes; an oasis market is the hub, with a slot through each wall to a side objective
    (a pumpjack wellhead and a caravan stop).
  * Whiteout Pass (snow): a pass through thick pine forest with rock shoulders; a watchtower
    line crosses it, and all three objectives sit on that line, as far from either camp: a
    signal post, the frozen lake (open ice) and a sawmill with its lumber settlement.
  * Greenvale Farms (temperate): hedgerowed fields, orchards and copses round a crossroads
    village with a church and an inn on the green; a farmstead on either flank.
  * Rust Yard (harbour): a ruined industrial district cut in two by a marshalling yard of
    wagons on four sidings; burnt-out works, rubble and wrecks, a foundry and a scrapyard.
  * Ember Ridge (volcanic): a lava rift across basalt fields, crossed only at an abandoned
    geothermal plant (turbine halls, storage and fuel tanks, live wellheads) and two causeways;
    lava pools, obsidian spires, fumaroles and burnt forest.
  * Jungle Pass (jungle): a brown river winds through dense rainforest; a temple ruin stands in
    the wide central ford, stilt villages hold the two others, overgrown ridges shape the pass.
  * Skyhold Airbase (temperate): a runway between two hangar aprons whose parked jets and fuel
    trucks stand close on purpose (one fireball sets off the line), a control tower and radar
    dome at midfield, jets in revetments, fuel farms by the camps.
  * Metro City (urban): a grid of 16 m avenues between high-rise blocks, skyscrapers round the
    central plaza, a park and a parking lot as the side objectives, buses and traffic lights.

Lava pools, river water and fords are 4 m surface tiles (lava and deep water block, fords do
not); the map view merges them into smooth surfaces.

Every map also gets a Siege version (`fortify`): the enemy fortress fills the north-east
quadrant (a walled 56 m square with two gates, the command HQ, depots, dumps, hangars and an
outer line of bunkers and obstacles), with its fixed defences as team-1 map units.

Every placement is checked against the footprints in balance.json, the roads, the camps and
the objectives, and the result is flood-filled on the simulation's 2 m navigation grid (with
its 1.5 m obstacle clearance, filled exactly like NavGrid.AddBlocker) to prove that both camps
can reach every objective, and in Siege that the player can reach the HQ.

    python Tools/maps/build_maps.py [map ids...]   (no ids: all of them)
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
        self.reserved = []  # rectangles kept free for map units (siege defences)
        self.units = []     # extra map units (siege defences)

    # ------------------------------------------------------------------ geometry
    @staticmethod
    def size(def_id, rot):
        p = PROPS[def_id]
        w, d = p['width'], p['depth']
        return (d, w) if rot % 180 == 90 else (w, d)

    def road(self, width, *points):
        self.roads.append({'width': width, 'points': [float(v) for v in points]})
        self._samples = None

    def road_samples(self):
        """Points every 0.75 m along every road, with the road's half width (cached)."""
        if getattr(self, '_samples', None) is None:
            self._samples = []
            for road in self.roads:
                pts = road['points']
                half = road['width'] / 2
                for i in range(0, len(pts) - 2, 2):
                    ax, az, bx, bz = pts[i], pts[i + 1], pts[i + 2], pts[i + 3]
                    length = math.hypot(bx - ax, bz - az)
                    steps = max(1, int(length / 0.75))
                    for k in range(steps + 1):
                        t = k / steps
                        self._samples.append((ax + (bx - ax) * t, az + (bz - az) * t, half))
        return self._samples

    def near_road(self, x0, z0, x1, z1, gap):
        """True when a rectangle comes closer than `gap` to any road edge."""
        for px, pz, half in self.road_samples():
            dx = max(x0 - px, 0, px - x1)
            if dx - half >= gap:
                continue
            dz = max(z0 - pz, 0, pz - z1)
            if math.hypot(dx, dz) - half < gap:
                return True
        return False

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
        if not self.fits(x0, z0, x1, z1, pad):
            return False
        if road_gap is not None and self.near_road(x0, z0, x1, z1, road_gap):
            return False
        return True

    def fits(self, x0, z0, x1, z1, pad):
        """True when a rectangle (grown by `pad`) overlaps no placed prop and no reserved unit spot."""
        for (a0, b0, a1, b1) in self.rects:
            if x0 - pad < a1 and x1 + pad > a0 and z0 - pad < b1 and z1 + pad > b0:
                return False
        for (a0, b0, a1, b1) in self.reserved:
            if x0 - pad < a1 and x1 + pad > a0 and z0 - pad < b1 and z1 + pad > b0:
                return False
        return True

    def put(self, def_id, x, z, rot=0, pad=0.3):
        """Hand placement that ignores camps, objectives, plazas and roads (the siege fortress):
        only the map edge, other props and reserved unit spots are respected."""
        w, d = self.size(def_id, rot)
        x0, z0, x1, z1 = x - w / 2, z - d / 2, x + w / 2, z + d / 2
        if x0 < -HALF + 1 or z0 < -HALF + 1 or x1 > HALF - 1 or z1 > HALF - 1 or not self.fits(x0, z0, x1, z1, pad):
            self.failed.append((def_id, x, z))
            return False
        self.force(def_id, x, z, rot)
        return True

    def force(self, def_id, x, z, rot=0):
        """Places a prop with no checks at all (wall segments that meet end to end, gates in their gaps)."""
        x, z = round(x * 20) / 20, round(z * 20) / 20
        w, d = self.size(def_id, rot)
        self.rects.append((x - w / 2, z - d / 2, x + w / 2, z + d / 2))
        entry = {'def': def_id, 'x': x, 'z': z}
        if rot:
            entry['rot'] = rot
        self.props.append(entry)

    def remove(self, hit):
        """Drops every prop whose footprint `hit(x0, z0, x1, z1)` selects; returns how many."""
        keep = [(p, r) for p, r in zip(self.props, self.rects) if not hit(*r)]
        removed = len(self.props) - len(keep)
        self.props = [p for p, _ in keep]
        self.rects = [r for _, r in keep]
        return removed

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

    def reachable(self, targets=None):
        """Flood fill on the nav grid from the first camp; returns the unreachable targets
        (by default the other camps and every objective)."""
        n = int(HALF * 2 / CELL)
        blocked = self.blocked_grid()

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
        if targets is None:
            targets = [('camp', t[0], t[1]) for t in self.teams[1:]] + [('point', p[0], p[1]) for p in self.points]
        missing = []
        for t in targets:
            # A target given as a rectangle (name, x0, z0, x1, z1) counts when any cell beside it is reached.
            if len(t) == 5:
                a0, b0 = cell(t[1] - 3.0, t[2] - 3.0)
                a1, b1 = cell(t[3] + 3.0, t[4] + 3.0)
                if not any((gx, gz) in seen for gx in range(a0, a1 + 1) for gz in range(b0, b1 + 1)):
                    missing.append(t)
            elif cell(t[1], t[2]) not in seen:
                missing.append(t)
        return missing

    def walkable(self, x, z):
        """Whether the nav cell under a point is open (units spawned elsewhere get moved)."""
        blocked = self.blocked_grid()
        gx, gz = int((x + HALF) / CELL), int((z + HALF) / CELL)
        return not blocked[gz][gx]

    def blocked_grid(self):
        """The simulation's 2 m navigation grid, exactly as NavGrid.AddBlocker fills it: every cell
        that a blocking footprint, grown by the obstacle clearance, touches at all."""
        n = int(HALF * 2 / CELL)
        blocked = [[False] * n for _ in range(n)]
        for prop, (x0, z0, x1, z1) in zip(self.props, self.rects):
            if not PROPS[prop['def']].get('blocks', False):
                continue
            a0 = int(math.floor((x0 - CLEARANCE + HALF) / CELL))
            a1 = int(math.floor((x1 + CLEARANCE - 1e-4 + HALF) / CELL))
            b0 = int(math.floor((z0 - CLEARANCE + HALF) / CELL))
            b1 = int(math.floor((z1 + CLEARANCE - 1e-4 + HALF) / CELL))
            for gx in range(max(0, a0), min(n, a1 + 1)):
                for gz in range(max(0, b0), min(n, b1 + 1)):
                    blocked[gz][gx] = True
        return blocked


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


R2 = math.sqrt(0.5)


def diag(s, t):
    """Diagonal map coordinates to world x, z: `s` runs along the camp-to-camp axis (south-west
    to north-east, the camps sit at s = -82 and +82), `t` across it (positive to the north-west).
    The point (s, t) mirrors to (-s, -t), like (x, z) to (-x, -z)."""
    return (s - t) * R2, (s + t) * R2


def undiag(x, z):
    """World x, z to diagonal (s, t): the inverse of `diag`."""
    return (x + z) * R2, (z - x) * R2


def tiles(L, kind_at, step=4.0, road_gap=1.0):
    """Surface tiles (lava, river water, fords) on the 4 m grid: `kind_at(x, z)` names the tile
    for each cell centre, or None. Tiles touch edge to edge, so a river reads as one surface;
    deep tiles keep off roads (a road over lava or water is a causeway or ford) and, being
    blocking, off the objectives. Returns tiles placed."""
    placed = 0
    n = int(HALF * 2 / step)
    for gx in range(n):
        x = -HALF + step * (gx + 0.5)
        for gz in range(n):
            z = -HALF + step * (gz + 0.5)
            kind = kind_at(x, z)
            if kind is None:
                continue
            gap = road_gap if PROPS[kind].get('blocks', False) else None
            if L.add(kind, x, z, 0, pad=0.0, road_gap=gap):
                placed += 1
    return placed


def mixed_woods(L, poly, density, kinds, avoid=(), edge=4.0, clumps=0.6, road_gap=1.0):
    """`woods` with a mix of tree models (jungle species, bamboo by the water)."""
    xs = [x for x, _ in poly]
    zs = [z for _, z in poly]
    area = 0.0
    for (ax, az), (bx, bz) in zip(poly, poly[1:] + poly[:1]):
        area += ax * bz - bx * az
    target = int(abs(area) / 2 * density)
    placed = 0
    for _ in range(target * 12):
        if placed >= target:
            break
        x, z = L.rng.uniform(min(xs), max(xs)), L.rng.uniform(min(zs), max(zs))
        if not inside(poly, x, z) or any(math.hypot(x - ax, z - az) < r for ax, az, r in avoid):
            continue
        gap = min(abs((bx - ax) * (az - z) - (ax - x) * (bz - az)) / max(1e-6, math.hypot(bx - ax, bz - az))
                  for (ax, az), (bx, bz) in zip(poly, poly[1:] + poly[:1]))
        if gap < edge and L.rng.random() > gap / edge:
            continue
        noise = math.sin(x * 0.11 + 1.7) * math.cos(z * 0.13 - 0.6) + 0.6 * math.sin((x - z) * 0.07 + 2.1)
        if L.rng.random() > 1 - clumps * (0.5 - 0.5 * max(-1.0, min(1.0, noise))):
            continue
        kind = kinds(x, z) if callable(kinds) else L.rng.choice(kinds)
        if L.add(kind, x, z, 0, pad=0.25, road_gap=road_gap):
            placed += 1
    return placed


def rock_chain(L, pts, kinds=('mesa', 'cliff_a', 'cliff_b'), gap=0.5, jitter=1.2, pad=0.3, road_gap=1.0):
    """An unbroken wall of rock along a polyline of world (x, z) points. Each piece is set just
    clear of the last (the 1.5 m nav clearance seals the seams), and no piece sticks out past
    either end, so the wall opens exactly where the polyline stops. Returns pieces placed."""
    segs = []
    total = 0.0
    for (ax, az), (bx, bz) in zip(pts, pts[1:]):
        length = math.hypot(bx - ax, bz - az)
        segs.append((total, length, ax, az, (bx - ax) / length, (bz - az) / length))
        total += length

    def at(p):
        for start, length, ax, az, ux, uz in segs:
            if p <= start + length or (start, length) == segs[-1][:2]:
                q = p - start
                return ax + ux * q, az + uz * q, ux, uz
        raise ValueError

    prev = None
    p = 0.0
    placed = 0
    chain = []
    while p < total:
        # The next piece goes where it first clears the last one; if nothing fits there
        # (a road, a camp, an objective), the wall breaks and starts again further on.
        best = None
        options = list(kinds)
        L.rng.shuffle(options)
        for kind in options + ['boulders']:
            rot = L.rng.choice((0, 90))
            w, d = Layout.size(kind, rot)
            hw, hd = w / 2, d / 2
            j = L.rng.uniform(-jitter, jitter)
            q = p
            while q < total:
                x, z, ux, uz = at(q)
                reach = hw * abs(ux) + hd * abs(uz)
                if q - reach < -0.01:
                    q += 0.5
                    continue
                if q + reach > total + 0.01:
                    break
                x, z = round((x - uz * j) * 2) / 2, round((z + ux * j) * 2) / 2
                if prev and abs(x - prev[0]) < hw + prev[2] + gap and abs(z - prev[1]) < hd + prev[3] + gap:
                    q += 0.5
                    continue
                if L.add(kind, x, z, rot, pad=pad, road_gap=road_gap):
                    best = (q, x, z, hw, hd)
                break
            if best:
                break
        if best:
            chain.append(prev)
            p = best[0]
            prev = best[1:]
            placed += 1
        else:
            p += 2.0
            chain.append(prev)
            prev = None
    chain.append(prev)
    # A slanting wall of boxes touches only at the corners: tuck scree into the notches so it
    # reads as one ridge rather than a row of blocks.
    for a, b in zip(chain, chain[1:]):
        if not a or not b:
            continue
        if abs(b[0] - a[0]) < 2 or abs(b[1] - a[1]) < 2:
            continue
        sx, sz = (1 if b[0] > a[0] else -1), (1 if b[1] > a[1] else -1)
        for kind in ('cliff_b', 'boulders', 'boulders'):
            w, d = PROPS[kind]['width'] / 2, PROPS[kind]['depth'] / 2
            g = pad + 0.2
            # Beside a (across its z face) and against b's x face, then the mirror notch.
            for nx, nz in ((b[0] - sx * (b[2] + g + w), a[1] + sz * (a[3] + g + d)),
                           (a[0] + sx * (a[2] + g + w), b[1] - sz * (b[3] + g + d))):
                if L.add(kind, nx, nz, 0, pad=pad, road_gap=road_gap):
                    placed += 1
    return placed


def ridge(L, spine, half, kinds=('mesa', 'cliff_a', 'cliff_b')):
    """A canyon wall: an unbroken chain of rock down the spine polyline, then the band `half`
    metres either side of it packed solid round the chain. It opens only past the spine's ends."""
    rock_chain(L, spine, kinds)
    # The band stops short of the spine's ends by the packing slack, so nothing overhangs a gap.
    spine = [list(v) for v in spine]
    for end, nxt in ((0, 1), (-1, -2)):
        (x, z), (nx, nz) = spine[end], spine[nxt]
        length = math.hypot(nx - x, nz - z)
        spine[end] = [x + (nx - x) / length * 3.0, z + (nz - z) / length * 3.0]
    left, right = [], []
    for i, (x, z) in enumerate(spine):
        (ax, az), (bx, bz) = spine[max(0, i - 1)], spine[min(len(spine) - 1, i + 1)]
        length = math.hypot(bx - ax, bz - az)
        nx, nz = -(bz - az) / length, (bx - ax) / length
        left.append((x + nx * half, z + nz * half))
        right.append((x - nx * half, z - nz * half))
    massif(L, left + right[::-1], kinds, scree=False)


def inside(poly, x, z):
    """Point in polygon (world x, z vertices), by ray casting."""
    hit = False
    for (ax, az), (bx, bz) in zip(poly, poly[1:] + poly[:1]):
        if (az > z) != (bz > z) and x < ax + (z - az) * (bx - ax) / (bz - az):
            hit = not hit
    return hit


def massif(L, poly, kinds=('mesa', 'cliff_a', 'cliff_b'), slack=3.0, pad=0.3, road_gap=1.0, axis=(R2, R2), scree=True):
    """Packs a polygon of world (x, z) vertices solid with rock: the big pieces first, swept
    along `axis` so each settles against the last, then boulders in the cracks. A piece may
    overhang the outline by `slack` metres, which gives slanting edges their broken, stepped
    look. Returns pieces placed."""
    xs = [x for x, _ in poly]
    zs = [z for _, z in poly]
    placed = 0
    for kind, step in [(k, 2) for k in kinds] + ([('boulders', 1)] if scree else []):
        cands = [(x, z) for x in range(int(min(xs)) - 2, int(max(xs)) + 3, step)
                 for z in range(int(min(zs)) - 2, int(max(zs)) + 3, step)]
        cands.sort(key=lambda c: c[0] * axis[0] + c[1] * axis[1] + L.rng.uniform(-1.5, 1.5))
        for x, z in cands:
            rot = L.rng.choice((0, 90))
            w, d = Layout.size(kind, rot)
            hw, hd = max(0.5, w / 2 - slack), max(0.5, d / 2 - slack)
            if not all(inside(poly, x + sx * hw, z + sz * hd) for sx in (-1, 1) for sz in (-1, 1)):
                continue
            if L.add(kind, x, z, rot, pad=pad if kind != 'boulders' else 0.1, road_gap=road_gap):
                placed += 1
    return placed


def formation(L, x, z, kind, radius=8, scree=3, scree_kind='boulders'):
    """A rock formation: one big piece as close to a point as it fits, with boulders tumbled
    round its foot so it never stands alone like a dropped box."""
    if not L.near(kind, x, z, radius, L.rng.choice((0, 90))):
        return False
    p = L.props[-1]
    w, d = Layout.size(kind, p.get('rot', 0))
    placed = 0
    for _ in range(scree * 15):
        if placed >= scree:
            break
        a = L.rng.random() * math.tau
        ca, sa = math.cos(a), math.sin(a)
        # Just outside the footprint along this direction.
        reach = min(w / 2 / max(abs(ca), 1e-6), d / 2 / max(abs(sa), 1e-6)) + L.rng.uniform(2.6, 4.5)
        if L.add(scree_kind, p['x'] + ca * reach, p['z'] + sa * reach, L.rng.choice((0, 90)), pad=0.3, road_gap=1.0):
            placed += 1
    return True


def outcrop(L, cx, cz, r, count, kinds=('boulders',), pad=0.6, road_gap=1.0):
    """A cluster of rock: `count` pieces within `r` of a point (boulder fields, snow rock)."""
    placed = 0
    for _ in range(count * 12):
        if placed >= count:
            break
        a = L.rng.random() * math.tau
        rr = r * math.sqrt(L.rng.random())
        if L.add(L.rng.choice(kinds), cx + math.cos(a) * rr, cz + math.sin(a) * rr, L.rng.choice((0, 90)), pad=pad,
                 road_gap=road_gap):
            placed += 1
    return placed


def woods(L, poly, density, avoid=(), kind='tree', edge=4.0, clumps=0.6):
    """Trees over a polygon of world (x, z) vertices, `density` per square metre on average,
    thinning over the last `edge` metres of the outline. Slow noise gathers them into thickets
    and glades (`clumps` 0 is even). `avoid` lists (x, z, r) clearings kept open."""
    xs = [x for x, _ in poly]
    zs = [z for _, z in poly]
    area = 0.0
    for (ax, az), (bx, bz) in zip(poly, poly[1:] + poly[:1]):
        area += ax * bz - bx * az
    target = int(abs(area) / 2 * density)
    placed = 0
    for _ in range(target * 12):
        if placed >= target:
            break
        x, z = L.rng.uniform(min(xs), max(xs)), L.rng.uniform(min(zs), max(zs))
        if not inside(poly, x, z) or any(math.hypot(x - ax, z - az) < r for ax, az, r in avoid):
            continue
        # Distance to the outline, for a ragged forest edge.
        gap = min(abs((bx - ax) * (az - z) - (ax - x) * (bz - az)) / max(1e-6, math.hypot(bx - ax, bz - az))
                  for (ax, az), (bx, bz) in zip(poly, poly[1:] + poly[:1]))
        if gap < edge and L.rng.random() > gap / edge:
            continue
        noise = math.sin(x * 0.11 + 1.7) * math.cos(z * 0.13 - 0.6) + 0.6 * math.sin((x - z) * 0.07 + 2.1)
        if L.rng.random() > 1 - clumps * (0.5 - 0.5 * max(-1.0, min(1.0, noise))):
            continue
        if L.add(kind, x, z, 0, pad=0.25, road_gap=1.0):
            placed += 1
    return placed


def hedgerow(L, x0, z0, x1, z1, kind='hedge', gates=(), gate=9.0, trees=0.0, side=1):
    """Hedges, walls or fences end to end along an axis-aligned line, broken by field gates.
    `gates` are distances from the start where a `gate`-metre gap is left; `trees` is the chance
    of a hedgerow tree beside each piece (on `side`)."""
    along_x = abs(x1 - x0) >= abs(z1 - z0)
    rot = 0 if along_x else 90
    piece = Layout.size(kind, rot)[0 if along_x else 1]
    length = abs(x1 - x0) if along_x else abs(z1 - z0)
    direction = 1 if (x1 - x0 if along_x else z1 - z0) >= 0 else -1
    u = piece / 2
    placed = 0
    while u <= length - piece / 2 + 1e-6:
        if any(g - gate / 2 - piece / 2 < u < g + gate / 2 + piece / 2 for g in gates):
            u += 0.5
            continue
        x = x0 + direction * u if along_x else x0
        z = z0 if along_x else z0 + direction * u
        if L.add(kind, x, z, rot, pad=0.1, road_gap=0.5):
            placed += 1
            if trees and L.rng.random() < trees:
                off = side * 1.9
                L.add('tree', x + (0 if along_x else off), z + (off if along_x else 0), 0, pad=0.1, road_gap=0.5)
        u += piece + 0.5
    return placed


def orchard(L, x0, z0, x1, z1, spacing=5.0, kind='tree'):
    """Fruit trees in straight rows."""
    z = z0
    while z <= z1 + 1e-6:
        x = x0
        while x <= x1 + 1e-6:
            L.add(kind, x + L.rng.uniform(-0.4, 0.4), z + L.rng.uniform(-0.4, 0.4), 0, pad=0.2, road_gap=1.0)
            x += spacing
        z += spacing


def train(L, z, x0, x1, kinds, gaps=(), gap=(0.8, 1.5), rot=0, x=None):
    """Wagons coupled along a siding (axis-aligned track along x at `z`, or along z at `x`),
    with breaks where `gaps` lists (from, to) spans kept open for crossings."""
    placed = 0
    u = min(x0, x1)
    end = max(x0, x1)
    k = 0
    while u < end:
        kind = kinds[k % len(kinds)] if isinstance(kinds, (list, tuple)) else kinds
        length = Layout.size(kind, rot)[0 if x is None else 1]
        if u + length > end:
            break
        centre = u + length / 2
        if any(a - length / 2 < centre < b + length / 2 for a, b in gaps):
            u += 1.0
            continue
        if (L.add(kind, centre, z, rot, pad=0.2, road_gap=None, ignore_points=True) if x is None
                else L.add(kind, x, centre, rot, pad=0.2, road_gap=None, ignore_points=True)):
            placed += 1
            k += 1
            u += length + L.rng.uniform(*gap)
        else:
            u += 1.0
    return placed


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
    L.scatter('fuel_tank', 30, -46, 9, 12, 2, pad=0.8)
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
                       ('sandbags', -32, -40, 0), ('sandbags', -40, -32, 90)))
    for x, z in ((-70, 30), (20, 70)):
        formation(L, x, z, 'mesa', 10, 4)
        formation(L, -x, -z, 'mesa', 10, 4)
    # Rock formations in the open desert, each with scree at its foot: the cover between the
    # town, the plant and the oil field, and along the camp roads.
    for kind, x, z in (('cliff_b', -44, 22), ('cliff_b', 22, 36)):
        formation(L, x, z, kind, 12, 3)
        formation(L, -x, -z, kind, 12, 3)
    # Boulder fields: a scatter of rock with a dirt bank or two.
    for x, z in ((-30, 22), (-14, 38), (36, 30), (12, -38), (-36, -30), (-58, 12), (-8, 76), (50, 8)):
        outcrop(L, x, z, 6, 4, pad=0.5)
        outcrop(L, -x, -z, 6, 4, pad=0.5)
    for x, z in ((26, 44), (-4, 66)):
        L.near('dirt_mound', x, z, 12, L.rng.choice([0, 90]))
        L.near('dirt_mound', -x, -z, 12, L.rng.choice([0, 90]))
    # Cactus scrub in patches, thickest round the rock.
    for cx, cz, r in ((-60, 40, 10), (-20, 66, 8), (-66, -6, 8), (44, 40, 9), (-40, 20, 7), (18, 40, 6),
                      (-44, 30, 6), (-50, -16, 6), (-28, -38, 6), (-8, 44, 5), (-64, 18, 6), (30, 60, 6),
                      (54, -8, 6), (-34, 10, 5), (40, 24, 5)):
        L.forest(cx, cz, r, 0.12, kind='cactus')
        L.forest(-cx, -cz, r, 0.12, kind='cactus')

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

    # Snow rock outcrops in the woods and along the valley sides.
    for x, z, n in ((-60, 70, 4), (-70, 52, 3), (-46, 6, 3), (-52, -12, 3), (26, 70, 3), (-4, 74, 2),
                    (-74, 20, 3), (-38, -70, 3), (-20, -40, 2)):
        outcrop(L, x, z, 5, n, ('snow_rock',), pad=0.4)
        outcrop(L, -x, -z, 5, n, ('snow_rock',), pad=0.4)

    # Thick snowy pine forest over everything that is not village, road or objective, so the
    # village sits in a clearing carved out of the woods; thickest in the far corners.
    clearings = [(0, 0, 25), (-30, 46, 17), (30, -46, 17), (-30, 62, 9)]
    woods(L, [(-80, -80), (80, -80), (80, 80), (-80, 80)], 0.019, clearings, edge=0)
    for sign in (1, -1):
        woods(L, [(sign * -80, sign * 40), (sign * -40, sign * 80), (sign * -80, sign * 80)], 0.03, clearings, edge=0)
        woods(L, [(sign * 40, sign * -80), (sign * 80, sign * -40), (sign * 80, sign * -80)], 0.03, clearings, edge=0)

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

    # Container yard beside the docks objective: bays of stacks two rows wide, three deep,
    # single boxes at the seaward end, with straddle lanes between the bays.
    for bx, rows in ((-75, (28, 34.5, 41)), (-62, (28, 34.5, 41)), (-49, (28, 34.5, 41))):
        for dx in (0, 3.0):
            for i, z in enumerate(rows):
                kind = 'container' if i == len(rows) - 1 else 'container_stack'
                L.add(kind, bx + dx, z, 90, pad=0.2)
    # Loose boxes on the quay itself, squared up to the berths.
    for x, z, rot in ((-37, 44, 0), (-37, 47, 0), (-22, 52, 0)):
        L.add('container', x, z, rot, pad=0.2, ignore_points=True)
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

    # Rail yard on the eastern objective: rakes of tank wagons and boxcars coupled along both
    # tracks, broken in the middle of the objective (the ground to fight over) and, on the
    # northern track, at a crossing further east.
    for z, gaps in ((-39, ((23, 37), (60.5, 65.5))), (-53, ((23, 37),))):
        kinds = ['rail_tanker' if L.rng.random() < 0.45 else 'rail_boxcar' for _ in range(8)]
        train(L, z, 5.5, 78, kinds, gaps=gaps, gap=(0.5, 0.8))
    L.add('warehouse', 50, -68, 0, pad=0.8)
    L.add('warehouse', 20, -70, 0, pad=0.8)
    L.add('water_tower', 64, -66, 0, pad=0.8)
    L.scatter('fuel_tank', 30, -46, 7, 10, 2, pad=0.8)
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


def redrock(seed=71):
    teams = [(-58.0, -58.0), (58.0, 58.0)]
    points = [(-30.0, 46.0, 12.0), (0.0, 0.0, 16.0), (30.0, -46.0, 12.0)]
    L = Layout(seed, teams, points, clear=((-5, -5, 5, 5),))

    def both(s, t):
        """A diagonal position and its mirror through the centre."""
        return (diag(s, t), diag(-s, -t))

    # Sandy tracks along the three canyon floors; the middle one ends at the oasis.
    L.road(5, *diag(-82, 0), *diag(-54, 5), *diag(-30, -4), *diag(-15, 0))
    L.road(5, *diag(82, 0), *diag(54, -5), *diag(30, 4), *diag(15, 0))
    track = [(-78, 14), (-60, 40), (-40, 46), (-18, 49), (0, 52), (11, 54), (30, 49), (50, 41), (64, 30), (76, 14)]
    for sign in (1, -1):
        L.road(4.5, *[v for s, t in track for v in diag(sign * s, sign * t)])

    # Two long canyon walls split the floor into three lanes. Each is broken only by a narrow
    # slot from the oasis bowl out to its lane's objective, so the oasis is the hub that links
    # them; beside the slot the wall bulges back to make room for the oasis courts.
    walls = (((-64, 25), (-34, 28), (-18, 35), (-2, 36)),
             ((8, 30), (34, 29), (64, 25)))
    for sign in (1, -1):
        for part in walls:
            ridge(L, [diag(sign * s, sign * t) for s, t in part], 9)
    # The canyon rim closes the far corners.
    for sign in (1, -1):
        massif(L, [diag(sign * s, sign * t) for s, t in ((-42, 76), (42, 76), (0, 118))], kinds=('mesa', 'mesa', 'cliff_a'),
               scree=False)

    # The oasis: stalls round the spring under two rings of palms, and on each side of the
    # bowl an adobe court in the lee of the canyon wall.
    for s, t, rot in ((-10, 3, 0), (10, -3, 0), (-3, -10, 90), (3, 10, 90)):
        L.add('market_stall', *diag(s, t), rot, pad=0.3, road_gap=0.3)
    ring_of(L, 'palm', 0, 0, 7.0, 9, 0.3)
    ring_of(L, 'palm', 0, 0, 13.0, 14, 0.1)
    for s, t, kind in ((-12, 20, 'adobe_large'), (-2, 21, 'adobe_house'), (-23, 17, 'adobe_house')):
        for sign in (1, -1):
            x, z = diag(sign * s, sign * t)
            L.near(kind, x, z, 7, 0 if sign > 0 else 180, pad=0.8)
    for sign in (1, -1):
        for s, t, rot in ((-7, 15, 0), (-18, 12, 90)):
            L.add('wall', *diag(sign * s, sign * t), rot, pad=0.4)
        L.forest(*diag(sign * 16, sign * 13), 6, 0.12, kind='palm')
        L.forest(*diag(sign * 24, sign * -9), 5, 0.1, kind='palm')
        L.scatter('barrel', *diag(sign * -8, sign * 13), 1, 4, 4, pad=0.3)
        L.scatter('ammo_crate', *diag(sign * 8, sign * 11), 1, 4, 2, pad=0.3)

    # West, the wellhead: pumpjacks round the objective, a storage tank up the canyon.
    ax, az = points[0][:2]
    for s, t in ((-10, 7), (6, 11), (9, -9)):
        x, z = diag(s, t)
        L.near('oil_pump', ax + x, az + z, 4, L.rng.choice((0, 90)), pad=1.0)
    L.near('storage_tank', *diag(32, 60), 5, 0, pad=0.8)
    L.scatter('fuel_tank', ax, az, 7, 10, 1, pad=0.8)
    L.scatter('barrel', ax, az, 3, 10, 8, pad=0.3)
    L.scatter('truck', ax, az, 5, 10, 1, pad=0.8)
    L.add('sandbags', ax + 8, az - 8, 90, pad=0.4, ignore_points=True)
    # East, the caravan stop: adobe walls and a watchtower over the south-east canyon.
    cx, cz = points[2][:2]
    for s, t, kind in ((-10, -9, 'adobe_large'), (8, -12, 'adobe_house')):
        x, z = diag(s, t)
        L.near(kind, cx + x, cz + z, 4, 0, pad=0.8)
    L.near('watchtower', cx + diag(-3, 13)[0], cz + diag(-3, 13)[1], 4, pad=0.6)
    for s, t, rot in ((0, -13, 0), (13, -4, 90)):
        x, z = diag(s, t)
        L.add('wall', cx + x, cz + z, rot, pad=0.4)
    L.add('sandbags', cx - 6, cz + 8, 90, pad=0.4, ignore_points=True)
    L.add('sandbags', cx + 8, cz + 2, 0, pad=0.4, ignore_points=True)
    for dx, dz in ((-3, 3), (4, -4)):
        L.add('market_stall', cx + dx, cz + dz, 0, pad=0.4, road_gap=0.3)
    L.scatter('barrel', cx, cz, 3, 10, 6, pad=0.3)
    L.scatter('ammo_crate', cx, cz, 3, 10, 3, pad=0.3)
    L.forest(*diag(-26, -64), 5, 0.12, kind='palm')
    L.near('water_tower', *diag(-24, -58), 5, pad=0.6)
    # Two more pumpjacks drilled in the south-east canyon.
    for s, t in ((36, -50), (48, -40)):
        L.near('oil_pump', *diag(s, t), 5, L.rng.choice((0, 90)), pad=1.0)

    # Rockfall at the foot of the walls, and boulder fields as cover out on the canyon floors.
    for s, t in ((-50, 19), (-26, 45), (20, 40), (-40, -19), (54, 19), (-12, 19)):
        for (x, z) in both(s, t):
            outcrop(L, x, z, 3, 2, pad=0.3)
    for s, t in ((-20, 58), (40, 56), (-52, 44), (-40, 8), (40, -8), (-22, -10)):
        for (x, z) in both(s, t):
            outcrop(L, x, z, 5, 3)
    # Cactus scrub everywhere the ground is open.
    for s, t, r in ((-46, 38, 7), (-14, 62, 6), (24, 56, 7), (56, 40, 6), (-64, 8, 6), (-40, 10, 6), (-22, -12, 5),
                    (40, 10, 6), (60, -12, 6), (2, 44, 5), (-2, 64, 5), (-28, 54, 4), (36, 60, 5), (-58, 46, 4),
                    (-30, 0, 6), (-52, -8, 5), (18, 18, 4)):
        for (x, z) in both(s, t):
            L.forest(x, z, r, 0.12, kind='cactus')
    approach_cover(L, (('boulders', -30, -48, 0), ('boulders', -48, -30, 0), ('dirt_mound', -24, -62, 0),
                       ('sandbags', -40, -40, 0), ('tank_trap', -36, -44, 0), ('tank_trap', -44, -36, 0)))
    for s, t in ((6, 62),):
        for (x, z) in both(s, t):
            L.near('dirt_mound', x, z, 8, L.rng.choice((0, 90)))

    return finish(L)


def whiteout(seed=83):
    teams = [(-58.0, -58.0), (58.0, 58.0)]
    # The watchtower line runs across the pass: all three objectives sit on it, the same
    # distance from both camps.
    points = [(-38.0, 38.0, 12.0), (0.0, 0.0, 16.0), (38.0, -38.0, 12.0)]
    L = Layout(seed, teams, points, clear=((-11, -11, 11, 11),))
    a, c = diag(0, 54), diag(0, -54)

    def quad(s, t):
        """A diagonal position mirrored across both diagonals: the pass and the tower line."""
        return [diag(s, t), diag(-s, t), diag(s, -t), diag(-s, -t)]

    # The pass road from camp to camp, a track round the frozen lake, the patrol track along
    # the tower line and logging roads up through the forest to the post and the sawmill.
    L.road(6, *diag(-82, 0), *diag(-60, 4), *diag(-40, 0), *diag(-25, 0))
    L.road(6, *diag(82, 0), *diag(60, -4), *diag(40, 0), *diag(25, 0))
    shore = [(25 * math.cos(k * math.tau / 8), 25 * math.sin(k * math.tau / 8)) for k in range(9)]
    L.road(5, *[v for p in shore for v in p])
    for sign in (1, -1):
        L.road(4.5, *diag(0, sign * 25), *diag(0, sign * 54))
        for side in (1, -1):
            track = [(56, 3), (46, 22), (30, 44), (14, 54), (0, 54)]
            L.road(4.5, *[v for s, t in track for v in diag(side * s, sign * t)])

    # The narrows: rock shoulders pinch the pass either side of the lake basin.
    for x, z in quad(40, 16):
        L.near('cliff_b', x, z, 3, L.rng.choice((0, 90)), pad=0.5)
        outcrop(L, x, z, 8, 4, ('snow_rock',), pad=0.4)
    # Broken rock along both sides of the pass: a gorge with gaps out into the forest.
    for s in (22, 31, 50, 60, 68):
        for x, z in quad(s, 15 + (s % 3)):
            outcrop(L, x, z, 4, 2, ('snow_rock',), pad=0.3)

    # The frozen lake: open ice for the centre objective, a rocky shore round it.
    for x, z in quad(12.5, 12):
        L.near('snow_rock', x, z, 3, L.rng.choice((0, 90)), pad=0.5)
    for x, z in quad(27, 22):
        outcrop(L, x, z, 4, 2, ('snow_rock',), pad=0.4)

    # The watchtower line: towers, sandbag nests and dragon's teeth along a cut through the
    # forest, from the signal post across the lake to the sawmill.
    # The patrol track runs through a gate at each tower.
    for sign in (1, -1):
        for t in (33, 86):
            L.near('watchtower', *diag(sign * 8, sign * t), 2, pad=0.6)
            L.near('sandbags', *diag(sign * -7, sign * t), 2, 0, pad=0.4)
            for side in (1, -1):
                for k in range(3):
                    L.add('tank_trap', *diag(side * (13 + 3.5 * k), sign * (t + (1.5 if k % 2 else -1.5))), 0, pad=0.4)

    # West, the signal post: a radar behind the objective, towers and a barracks round it.
    L.add('radar_station', *diag(0, 71), 0, pad=0.8, must=True)
    for side in (1, -1):
        L.near('watchtower', *diag(side * 13, 65), 3, pad=0.6)
        L.near('log_cabin', *diag(side * 15, 43), 5, 0, pad=0.8)
        L.add('sandbags', *diag(side * 8, 44), 90 if side > 0 else 0, pad=0.4, ignore_points=True)
    L.near('garage', *diag(-22, 64), 5, 0, pad=0.8)
    L.near('fuel_tank', *diag(22, 64), 5, pad=0.8)
    L.scatter('ammo_crate', a[0], a[1], 3, 9, 4, pad=0.3)
    L.scatter('barrel', a[0], a[1], 3, 9, 6, pad=0.3)
    L.scatter('truck', a[0], a[1], 5, 9, 1, pad=0.8)

    # East, the sawmill: the mill shed, timber barns, cabins, logging trucks in a fenced yard,
    # and a lumber settlement strung along the roads either side.
    L.add('warehouse', *diag(0, -76), 0, pad=0.8, must=True)
    for side in (1, -1):
        L.near('barn', *diag(side * 17, -65), 4, 0, pad=0.8)
        L.near('log_cabin', *diag(side * 15, -43), 5, 0, pad=0.8)
        for s, t in ((40, -40), (24, -34), (30, -58), (44, -52), (18, -80)):
            L.near('log_cabin', *diag(side * s, t), 7, 0 if side > 0 else 180, pad=0.8)
    # The log yard between the objective and the mill, fenced on two sides.
    hedgerow(L, c[0] - 10, c[1] - 14.5, c[0] + 6, c[1] - 14.5, kind='fence', gates=(8,), gate=5)
    hedgerow(L, c[0] - 10.5, c[1] - 14, c[0] - 10.5, c[1] - 2, kind='fence', gates=(6,), gate=5)
    L.scatter('truck', c[0], c[1], 4, 9, 3, pad=0.8)
    L.scatter('barrel', c[0], c[1], 3, 9, 6, pad=0.3)
    L.near('fuel_tank', *diag(12, -66), 8, pad=0.8)

    # Snow rock outcrops in the forest and at the pass edges near the camps.
    for s, t, n in ((30, 58, 4), (54, 32, 4), (22, 82, 3), (46, 50, 3), (66, 14, 3), (16, 30, 2), (34, 28, 3)):
        for x, z in quad(s, t):
            outcrop(L, x, z, 5, n, ('snow_rock',), pad=0.4)
    approach_cover(L, (('snow_rock', -30, -48, 0), ('snow_rock', -48, -30, 0), ('tank_trap', -38, -42, 0),
                       ('tank_trap', -42, -38, 0), ('sandbags', -34, -40, 0), ('sandbags', -40, -34, 90)))

    # Thick snowy pine forest over everything else, cut by the roads and the tower line.
    clearings = [(0, 0, 27), (a[0], a[1], 17), (c[0], c[1], 19), (*diag(0, 71), 9), (*diag(0, -76), 12)]
    for ss in (1, -1):
        for st in (1, -1):
            poly = [diag(ss * s, st * t) for s, t in ((8, 13), (80, 13), (80, 31), (8, 103))]
            woods(L, poly, 0.036, clearings)
    # The pass floor itself keeps a few lone pines.
    woods(L, [diag(-80, -12), diag(80, -12), diag(80, 12), diag(-80, 12)], 0.004, clearings)

    return finish(L)


def greenvale(seed=97):
    teams = [(-58.0, -58.0), (58.0, 58.0)]
    points = [(-32.0, 46.0, 12.0), (0.0, 0.0, 16.0), (32.0, -46.0, 12.0)]
    L = Layout(seed, teams, points, clear=((-10, -10, 10, 10),))

    # Two country lanes cross at the village green; lanes from each camp join them, and farm
    # tracks run out to the two farmsteads.
    L.road(6, -78, 0, 78, 0)
    L.road(6, 0, -78, 0, 78)
    for sign in (1, -1):
        L.road(5, sign * -58, sign * -58, sign * -42, sign * -42, sign * -42, 0)
        L.road(5, sign * -42, sign * -42, 0, sign * -42)
        L.road(4.5, 0, sign * 46, sign * -78, sign * 46)
        L.road(4.5, sign * -32, 0, sign * -32, sign * 46)

    # The village: a church and an inn facing the green, cottages and shops with gardens
    # along the four lanes, and a churchyard wall.
    L.add('church', 21, 23, 90, pad=0.5, must=True)
    L.add('house_large', -21, -22, 0, pad=0.5, must=True)
    for x, z, rot in ((14, 33.5, 0), (28, 33.5, 0), (32.5, 26, 90), (32.5, 16, 90)):
        L.add('stone_wall', x, z, rot, pad=0.3)
        L.add('stone_wall', -x, -z, rot, pad=0.3)
    L.forest(26, 38, 4, 0.1)
    L.forest(-26, -36, 4, 0.1)
    kinds = ['cottage', 'house_small', 'shop', 'cottage', 'townhouse', 'garage', 'house_small', 'cottage']
    for axis in ('x', 'z'):
        for side in (1, -1):
            for direction in (1, -1):
                row_kinds = kinds[:]
                L.rng.shuffle(row_kinds)
                L.frontage(axis, 0, side, 16 * direction, 41 * direction, row_kinds, setback=2.0, road_half=3.0,
                           alley_every=(2, 3), yards=True, cars=0.35)
    for x, z in ((12, 12), (-12, 12), (12, -12), (-12, -12)):
        L.add('tree', x, z, 0, pad=0.3, road_gap=1.0)

    # West farm: the yard is the objective, the barn and silos to the north, the farmhouse
    # to the west, a walled paddock and an orchard beyond.
    ax, az = points[0][:2]
    for sign in (1, -1):
        x, z = sign * ax, sign * az
        L.near('barn', x, z + sign * 17, 3, 0, pad=0.8)
        L.near('silo', x + sign * 14, z + sign * 15, 3, pad=0.6)
        L.near('silo', x + sign * 19.5, z + sign * 15, 3, pad=0.6)
        L.near('house_large', x - sign * 19, z + sign * 8, 4, 90 if sign > 0 else 270, pad=0.8)
        L.near('cottage', x - sign * 18, z - sign * 10, 4, 90 if sign > 0 else 270, pad=0.8)
        L.near('garage', x + sign * 16, z - sign * 9, 4, 0, pad=0.8)
        L.near('water_tower', x + sign * 26, z + sign * 24, 4, pad=0.6)
        L.scatter('truck', x, z, 4, 9, 2, pad=0.8)
        L.scatter('barrel', x, z, 3, 10, 5, pad=0.3)
        L.scatter('ammo_crate', x, z, 3, 10, 3, pad=0.3)
        L.add('sandbags', x + sign * 8, z - sign * 8, 90, pad=0.4, ignore_points=True)
        # The yard wall on the side facing the village, with a gate on the track.
        hedgerow(L, x + sign * 7, z - sign * 14, x + sign * 22, z - sign * 14, kind='stone_wall', gates=(7,), gate=8)
        hedgerow(L, x - sign * 26, z + sign * 22, x - sign * 8, z + sign * 22, kind='fence', gates=(9,), gate=6)

    # Fields: hedges with oaks line the lanes outside the village and divide the fields; stone
    # walls on a few boundaries. Pieces never cross a lane or track, which leaves the gates.
    lines = (
        # the country lanes, both sides
        (-78, 4.5, -44, 4.5, 'hedge'), (-78, -4.5, -46, -4.5, 'hedge'),
        (-4.5, 44, -4.5, 78, 'hedge'), (4.5, 46, 4.5, 78, 'hedge'),
        # the farm tracks, both sides, broken round the farmyard
        (-78, 50, -48, 50, 'hedge'), (-78, 42, -50, 42, 'hedge'), (-16, 50, -6, 50, 'hedge'), (-14, 42, -6, 42, 'hedge'),
        (-36, 6, -36, 30, 'hedge'), (-28, 20, -28, 30, 'hedge'),
        # the camp lanes, both sides
        (-46, -36, -46, -8, 'hedge'), (-38, -34, -38, -8, 'hedge'), (-36, -46, -8, -46, 'hedge'), (-34, -38, -8, -38, 'hedge'),
        # field boundaries
        (-78, 24, -40, 24, 'hedge'), (-58, 54, -58, 78, 'hedge'), (-28, 62, -8, 62, 'stone_wall'),
        (-78, -24, -50, -24, 'stone_wall'), (-24, -78, -24, -50, 'stone_wall'), (-78, -40, -66, -40, 'hedge'),
        (-40, -78, -40, -66, 'hedge'),
    )
    for x0, z0, x1, z1, kind in lines:
        for sign in (1, -1):
            hedgerow(L, sign * x0, sign * z0, sign * x1, sign * z1, kind=kind, gates=(14,) if kind == 'stone_wall' else (),
                     gate=10, trees=0.3 if kind == 'hedge' else 0.0, side=1 if (z0 == z1) == (x0 < 0) else -1)

    # Orchards, copses and a wood in each empty corner.
    for x0, z0, x1, z1 in ((-72, 8, -52, 20), (-24, 66, -8, 76), (-72, -36, -56, -28)):
        orchard(L, x0, z0, x1, z1, spacing=5.0)
        orchard(L, -x1, -z1, -x0, -z0, spacing=5.0)
    for cx, cz, r, d in ((-64, 66, 13, 0.2), (-72, 36, 6, 0.14), (-12, 34, 5, 0.1), (-54, 32, 5, 0.12),
                         (-40, -64, 7, 0.14), (-66, -40, 6, 0.14), (-16, -68, 6, 0.14), (-68, -16, 6, 0.12)):
        L.forest(cx, cz, r, d)
        L.forest(-cx, -cz, r, d)

    # Cover on the open approaches: haystack-sized dirt mounds, a few boulders by the lanes,
    # a broken-down tractor or two.
    approach_cover(L, (('boulders', -30, -48, 0), ('boulders', -48, -30, 0), ('dirt_mound', -24, -62, 0),
                       ('dirt_mound', -62, -24, 90), ('sandbags', -36, -40, 0), ('sandbags', -40, -36, 90)))
    for x, z, rot in ((-40, 30, 0), (-32, 74, 90), (-60, 36, 90)):
        L.near('truck', x, z, 5, rot, pad=0.8)
        L.near('truck', -x, -z, 5, rot, pad=0.8)
    for x, z in ((-40, 14), (-20, 26), (-56, -14), (-14, -54), (-48, 74)):
        L.near('dirt_mound', x, z, 5, L.rng.choice((0, 90)))
        L.near('dirt_mound', -x, -z, 5, L.rng.choice((0, 90)))

    return finish(L)


def rustyard(seed=101):
    teams = [(-58.0, -58.0), (58.0, 58.0)]
    points = [(-34.0, 46.0, 12.0), (0.0, 0.0, 16.0), (34.0, -46.0, 12.0)]
    L = Layout(seed, teams, points, clear=((-9, -9, 9, 9),))

    # A marshalling yard of four sidings cuts the district in two; service roads run along
    # both sides of it, level crossings cross it, and broken streets lead off into the works.
    for z in (-18, -6, 6, 18):
        L.road(3, -78, z, 78, z)
    for sign in (1, -1):
        L.road(6, -78, sign * 32, 78, sign * 32)                            # service road along the yard
        L.road(5, sign * -58, sign * -58, sign * -44, sign * -44, sign * -44, sign * -32)
        L.road(6, sign * 8, sign * 32, sign * 8, sign * 78)                 # street into the works
        L.road(6, sign * 8, sign * 56, sign * -78, sign * 56)
        for x in (-40, 40):
            L.road(6, sign * x, sign * 32, sign * x, sign * 24)             # level crossings
    L.road(6, -40, -24, -40, 24)
    L.road(6, 40, -24, 40, 24)

    # Rolling stock left on the sidings: long rakes broken at the level crossings and at one
    # staggered gap each, shorter strings on the inner tracks that leave the middle of the
    # yard open, and a derailed boxcar either side of it.
    rakes = {18: ((-44, -36), (-8, 1), (36, 44)), 6: ((-44, -36), (-16, 16), (36, 44))}
    for z, gaps in rakes.items():
        for sign in (1, -1):
            spans = [(a, b) if sign > 0 else (-b, -a) for a, b in gaps]
            kinds = [L.rng.choice(('rail_boxcar', 'rail_boxcar', 'rail_tanker')) for _ in range(14)]
            train(L, sign * z, -77, 77, kinds, gaps=spans, gap=(0.5, 1.0))
    for x, z in ((-12.5, 10.5), (12.5, -10.5)):
        L.add('rail_boxcar', x, z, 90, pad=0.4, road_gap=None, ignore_points=True, must=True)
    for x, z, rot in ((-9, 0, 90), (9, 0, 90), (0, 11, 0), (0, -11, 0)):
        L.add('jersey_barrier', x, z, rot, pad=0.4, road_gap=None, ignore_points=True)
    L.scatter('barrel', 0, 0, 4, 12, 8, pad=0.3)
    L.scatter('dirt_mound', 0, 0, 9, 14, 3, pad=0.4)

    # The two halves of the district mirror each other through the centre, so both camps get
    # the same ground; only what the buildings are changes. South-east of the yard the
    # scrapyard objective sits among container stacks, north-west the foundry among ruins.
    for sign in (1, -1):
        def at(x, z):
            return sign * x, sign * z
        south = sign > 0
        # Works beside the camp.
        L.near('factory', *at(-24, -47), 3, 0, pad=1.0)
        L.near('ruin', *at(-20, -67), 3, 0, pad=0.8)
        L.near('silo', *at(-36, -42), 3, pad=0.6)
        L.near('water_tower', *at(-60, -27), 3, pad=0.6)
        # The far works round the other objective, and the ruins either side of it.
        L.near('warehouse', *at(16, -68), 3, 0, pad=0.8)
        L.near('factory' if south else 'warehouse', *at(48, -68), 3, 0, pad=0.8)
        L.near('office_block', *at(70, -67), 3, 0, pad=0.8)
        L.near('ruin', *at(6, -44), 3, 0, pad=0.8)
        L.near('ruin', *at(66, -44), 3, 0, pad=0.8)
        # The objective's own ring (offsets towards the yard first): stacks of containers round
        # the scrapyard, gutted halls and broken walls round the foundry.
        ox, oz = at(34, -46)
        if south:
            ring = (('container_stack', -15, 7, 90), ('container_stack', -15, -5, 90), ('container', 15, 6, 90),
                    ('container_stack', 15, -6, 90), ('container_stack', -6, -15, 0), ('container', 6, -15, 0))
        else:
            ring = (('ruin', -17, 2, 0), ('ruin', 17, 3, 0), ('wall', -6, -14, 0), ('jersey_barrier', 6, -14, 0),
                    ('wall', -14, 9, 90), ('wall', 14, 8, 90))
        for kind, dx, dz, rot in ring:
            L.near(kind, ox + sign * dx, oz - dz if not south else oz + dz, 4, rot, pad=0.5)
        for dx, dz in ((-5, 5), (5, -3), (-2, -5)):
            L.near('dirt_mound', ox + dx, oz + dz, 3, L.rng.choice((0, 90)), pad=0.4)
        L.scatter('car', ox, oz, 3, 10, 3, pad=0.5)
        L.scatter('barrel', ox, oz, 3, 10, 5, pad=0.3)
        L.scatter('ammo_crate', ox, oz, 3, 10, 2, pad=0.3)
        # Rubble and roadblocks in the streets, burnt-out wrecks left on the roads.
        for x, z in ((-10, -40), (-2, -62), (30, -62), (60, -52)):
            L.near(L.rng.choice(('dirt_mound', 'dirt_mound', 'boulders')), *at(x, z), 6, L.rng.choice((0, 90)), pad=0.6)
        for x, z, rot in ((-34, -38, 0), (-14, -52, 90), (26, -38, 90), (0, -52, 0), (46, -60, 0)):
            L.near('jersey_barrier', *at(x, z), 5, rot, pad=0.4)
        for x, z, rot in ((-30, -32, 0), (-8, -70, 90), (22, -56, 0), (58, -32, 0), (60, -56, 0), (-44, -38, 90), (12, -32, 0)):
            L.add(L.rng.choice(('car', 'car', 'truck')), *at(x + L.rng.uniform(-2, 2), z), rot, pad=0.5, road_gap=None)
        for x in (-56, -26, 24, 54):
            L.near('container_stack', *at(x, -26), 3, 0, pad=0.5)
        # Shells of burnt-out sheds: two walls standing at a corner round a heap of rubble.
        for x, z in ((1, -70), (57, -44)):
            cx, cz = at(x, z)
            if L.near('wall', cx, cz - 3.5, 6, 0, pad=0.3):
                wx, wz = L.props[-1]['x'], L.props[-1]['z'] + 3.5
                L.near('wall', wx - 3.5, wz + 1, 2, 90, pad=0.3)
                L.near(L.rng.choice(('dirt_mound', 'boulders')), wx + 2, wz + 1, 3, 0, pad=0.3)
    approach_cover(L, (('jersey_barrier', -30, -48, 0), ('dirt_mound', -24, -62, 0), ('tank_trap', -36, -50, 0),
                       ('boulders', -34, -64, 0)))

    # The old quay on the north shore, and weeds and scrub trees taking over the empty lots.
    row(L, 'dock_bollards', -76, 77, 76, 77, 9, 0, pad=0.3, road_gap=None)
    for cx, cz, r, d in ((-70, -70, 7, 0.1), (70, 70, 7, 0.1), (-70, 70, 8, 0.1), (70, -70, 8, 0.1),
                         (-40, -72, 5, 0.1), (40, 72, 5, 0.1), (-74, 10, 5, 0.08), (74, -10, 5, 0.08)):
        L.forest(cx, cz, r, d)

    return finish(L)


def emberridge(seed=113):
    teams = [(-58.0, -58.0), (58.0, 58.0)]
    # A lava rift runs corner to corner across the camp axis. The plant spans its middle and the
    # side objectives sit on the two causeways, so every crossing is worth holding.
    rift_s = lambda t: 5.0 * math.sin(t / 10.0)   # the rift wanders; odd, so it mirrors
    w, e = diag(rift_s(50), 50), diag(rift_s(-50), -50)
    points = [(round(w[0]), round(w[1]), 12.0), (0.0, 0.0, 16.0), (round(e[0]), round(e[1]), 12.0)]
    L = Layout(seed, teams, points, clear=((-5, -5, 5, 5),))

    def half_width(t):
        """Even in t (mirrors); the rift swells into a lava lake in the two far corners."""
        a = abs(t)
        return 9.0 + 2.0 * math.cos(t / 7.0) + max(0.0, a - 90.0) * 0.95

    # Roads: the pass road from camp to camp over the plant, and a loop through the causeways:
    # from each side's pass road out to one causeway, straight across the rift, and back to the
    # other side's pass road. Lava never covers a road, so the roads are the crossings.
    L.road(7, *diag(-82, 0), *diag(-56, -4), *diag(-30, 0), *diag(30, 0), *diag(56, 4), *diag(82, 0))
    for sign in (1, -1):
        L.road(5, *[v for s, t in ((-46, -2), (-44, 24), (-24, 50), (24, 50)) for v in diag(sign * s, sign * t)])
        L.road(5, *[v for s, t in ((-24, -50), (-40, -30), (-46, -6)) for v in diag(sign * s, sign * t)])

    # The abandoned geothermal plant: two turbine halls, storage tanks, wellheads (live vents)
    # piped into a manifold of fuel tanks inside the objective. One hit and the plant goes up in
    # a chain of fireballs.
    for sign in (1, -1):
        L.add('factory', sign * -30, sign * -9, 90, pad=1.0, must=True)
        L.add('storage_tank', sign * -30, sign * 6, 0, pad=0.8, must=True)
        L.add('storage_tank', sign * -9, sign * -27, 0, pad=0.8, must=True)
        for x, z in ((-9, 4), (-4, 9)):
            L.add('fuel_tank', sign * x, sign * z, 0, pad=0.6, ignore_points=True, must=True)
        for x, z, rot in ((-13.5, -1, 90), (-1, -13.5, 0), (-16, 7, 0), (7, -16, 90)):
            L.add('pipeline', sign * x, sign * z, rot, pad=0.4, road_gap=None, ignore_points=True)
        for x, z in ((-10, 12), (12, -10)):
            L.add('lava_vent', sign * x, sign * z, 0, pad=0.4, road_gap=0.5, ignore_points=True)
        L.near('garage', sign * -40, sign * -44, 8, 0, pad=0.8)
        L.near('ruin', sign * -18, sign * -44, 8, 0, pad=0.8)
        L.near('watchtower', sign * -4, sign * -20, 4, pad=0.6)
        L.near('ruin', sign * -44, sign * -8, 6, 0, pad=0.6)
        L.scatter('barrel', sign * -14, sign * -14, 2, 6, 6, pad=0.3)
        L.scatter('ammo_crate', sign * -12, sign * 12, 2, 5, 3, pad=0.3)
        L.add('jersey_barrier', sign * -13, sign * -3, 90, pad=0.4, ignore_points=True)
        L.add('sandbags', sign * -3, sign * -13, 0, pad=0.4, ignore_points=True)

    # The rift itself, from the plant out to the lava lakes in the far corners, and lava pools
    # welling up in the basalt fields of each half.
    pools = [(-65.0, -17.0, 8.5), (12.7, -69.3, 8.5), (-60.8, 32.5, 7.5)]
    pools += [(-x, -z, r) for x, z, r in pools]

    def lava(x, z):
        s, t = undiag(x, z)
        for px, pz, r in pools:
            wobble = 1.0 + 0.18 * math.sin(3 * math.atan2(z - pz, x - px) + px)
            if math.hypot(x - px, z - pz) < r * wobble:
                return 'lava_pool'
        if abs(t) < 21:
            return None
        return 'lava_pool' if abs(s - rift_s(t)) < half_width(t) else None
    tiles(L, lava, road_gap=1.5)

    # Broken basalt banks: cliffs and spires along the rift, clear of the causeways.
    for sign in (1, -1):
        for t, side in ((30, 1), (36, -1), (66, 1), (72, -1), (84, 1)):
            s = rift_s(t) + side * (half_width(t) + 8)
            x, z = diag(sign * s, sign * t)
            formation(L, x, z, 'volcanic_cliff', 5, 2, scree_kind='basalt_rock_c')
        for t, side in ((42, 1), (58, -1), (78, -1), (62, 1)):
            s = rift_s(t) + side * (half_width(t) + 4)
            outcrop(L, *diag(sign * s, sign * t), 4, 3, ('obsidian_spire',), pad=0.4)

    # Basalt fields in each half: rock cover, spires and fumaroles; a burnt forest along the
    # flanks and in the corners behind the camps.
    for sign in (1, -1):
        for s, t, n in ((-40, 14, 4), (-44, -22, 4), (-26, 26, 3), (-24, -30, 3), (-60, 30, 4), (-62, -30, 4),
                        (-30, 60, 3), (-34, -60, 3), (-12, 30, 2), (-12, -32, 2)):
            outcrop(L, *diag(sign * s, sign * t), 6, n, ('basalt_rock_a', 'basalt_rock_b', 'basalt_rock_c'), pad=0.5)
        for s, t in ((-50, 42), (-52, -44), (-20, 52), (-22, -54)):
            outcrop(L, *diag(sign * s, sign * t), 4, 3, ('obsidian_spire',), pad=0.4)
        for s, t in ((-36, 12), (-46, 30), (-48, -30), (-22, 20), (-24, -18), (-66, 12), (-64, -14)):
            L.near('lava_vent', *diag(sign * s, sign * t), 5, pad=0.6)
        for s, t, r, d in ((-60, 50, 12, 0.14), (-62, -52, 12, 0.14), (-84, 30, 10, 0.12), (-84, -30, 10, 0.12),
                           (-40, 70, 8, 0.1), (-42, -72, 8, 0.1), (-34, 12, 5, 0.08), (-36, -14, 5, 0.08)):
            L.forest(*diag(sign * s, sign * t), r, d, kind='charred_tree')
    approach_cover(L, (('basalt_rock_c', -30, -48, 0), ('basalt_rock_c', -48, -30, 0), ('dirt_mound', -24, -62, 0),
                       ('dirt_mound', -62, -24, 90), ('tank_trap', -36, -44, 0), ('tank_trap', -44, -36, 0),
                       ('sandbags', -32, -40, 0), ('sandbags', -40, -32, 90)))

    return finish(L)


def junglepass(seed=127):
    teams = [(-58.0, -58.0), (58.0, 58.0)]
    # A brown river winds corner to corner through the rainforest. The temple ruin stands in a
    # wide ford at the centre; stilt villages hold the two other fords.
    river_s = lambda t: 8.0 * math.sin(t / 14.0)
    w, e = diag(river_s(52), 52), diag(river_s(-52), -52)
    points = [(round(w[0]), round(w[1]), 12.0), (0.0, 0.0, 16.0), (round(e[0]), round(e[1]), 12.0)]
    L = Layout(seed, teams, points, clear=())
    fords = [(0.0, 0.0, 19.0), (points[0][0], points[0][1], 14.0), (points[2][0], points[2][1], 14.0)]

    def half_width(t):
        return 7.6 + 1.6 * math.cos(t / 9.0)

    # Muddy tracks: camp to camp through the pass and the temple ford, and out to both villages.
    L.road(6, *diag(-82, 0), *diag(-58, 4), *diag(-38, 0), *diag(-18, -3), *diag(18, 3), *diag(38, 0),
           *diag(58, -4), *diag(82, 0))
    for sign in (1, -1):
        L.road(4.5, *[v for s, t in ((-38, 0), (-34, 24), (-18, 44), (river_s(52), 52), (18, 60))
                      for v in diag(sign * s, sign * t)])
        L.road(4.5, *[v for s, t in ((-38, 0), (-30, -26), (-16, -44), (river_s(-52), -52), (16, -60))
                      for v in diag(sign * s, sign * t)])

    # The temple in the shallows at the centre, on the river's axis so it is as far from both
    # camps; its fallen gatehouse faces it across the ford, with broken walls and stones round.
    L.add('temple_ruin', *diag(0, 12), 0, pad=0.5, road_gap=None, ignore_points=True, must=True)
    L.add('ruin', *diag(0, -12), 0, pad=0.5, road_gap=None, ignore_points=True, must=True)
    for sign in (1, -1):
        for x, z, kind, rot in ((-10, 10, 'wall', 0), (10, 10, 'stone_wall', 90), (-11, -3, 'stone_wall', 90),
                                (3, 11, 'wall', 0)):
            L.add(kind, sign * x, sign * z, rot, pad=0.4, road_gap=0.3, ignore_points=True)
        L.near('ruin', *diag(sign * -4, sign * 26), 4, 0, pad=0.6)
        L.near('boulders', *diag(sign * 12, sign * 14), 4, 0, pad=0.4)

    # The river: deep water between the fords (and wherever a track crosses it).
    def river(x, z):
        s, t = undiag(x, z)
        if abs(s - river_s(t)) >= half_width(t):
            return None
        if any(math.hypot(x - fx, z - fz) < r for fx, fz, r in fords):
            return 'river_ford'
        if L.near_road(x - 2, z - 2, x + 2, z + 2, 1.0):
            return 'river_ford'
        return 'river_water'
    tiles(L, river, road_gap=None)

    # Stilt villages on the banks of the side fords: huts round a landing, bamboo by the water.
    for sign in (1, -1):
        px, pz = sign * points[0][0], sign * points[0][1]
        ps, pt = undiag(px, pz)
        for ds, dt, rot in ((-16, 6, 0), (-15, -6, 90), (-24, 0, 0), (15, 7, 90), (16, -6, 0), (24, 2, 90),
                            (-20, 14, 90), (20, -13, 0)):
            x, z = diag(ps + sign * ds, pt + sign * dt)
            L.near('stilt_hut', x, z, 4, rot, pad=0.8)
        L.scatter('barrel', px, pz, 5, 12, 5, pad=0.3)
        L.scatter('ammo_crate', px, pz, 5, 12, 3, pad=0.3)
        L.near('watchtower', *diag(ps - sign * 12, pt + sign * 16), 4, pad=0.6)
        L.near('fuel_tank', *diag(ps - sign * 20, pt - sign * 12), 4, pad=0.6)
        L.add('sandbags', px - sign * 9, pz - sign * 9, 90, pad=0.4, ignore_points=True)
        L.forest(*diag(ps - sign * 6, pt + sign * 18), 5, 0.12, kind='bamboo_clump')
        L.forest(*diag(ps + sign * 7, pt - sign * 18), 5, 0.12, kind='bamboo_clump')

    # The pass: a rock ridge across each half, overgrown, broken where the tracks go through.
    for sign in (1, -1):
        for part in (((-44, 16), (-46, 34), (-40, 52), (-34, 64)), ((-44, -16), (-46, -34), (-40, -52), (-34, -66))):
            rock_chain(L, [diag(sign * s, sign * t) for s, t in part], kinds=('cliff_a', 'cliff_b'))
        for s, t in ((-54, 24), (-56, -28), (-30, 70), (-24, -74), (-60, 60), (-62, -62)):
            outcrop(L, *diag(sign * s, sign * t), 5, 3, ('boulders',), pad=0.4)
    approach_cover(L, (('boulders', -30, -48, 0), ('boulders', -48, -30, 0), ('dirt_mound', -24, -62, 0),
                       ('dirt_mound', -62, -24, 90), ('sandbags', -36, -40, 0), ('sandbags', -40, -36, 90)))

    # Rainforest over everything else: tall trees in thickets, bamboo along the river, ferns
    # in the undergrowth.
    def species(x, z):
        s, t = undiag(x, z)
        if abs(s - river_s(t)) < half_width(t) + 7 and L.rng.random() < 0.5:
            return 'bamboo_clump'
        return L.rng.choice(('jungle_tree_a', 'jungle_tree_a', 'jungle_tree_b', 'jungle_tree_c'))
    clearings = [(0, 0, 21), (points[0][0], points[0][1], 17), (points[2][0], points[2][1], 17)]
    mixed_woods(L, [(-80, -80), (80, -80), (80, 80), (-80, 80)], 0.024, species, clearings, edge=0)
    mixed_woods(L, [(-80, -80), (80, -80), (80, 80), (-80, 80)], 0.009, ('fern_bush',), clearings, edge=0, clumps=0.3)

    return finish(L)


def skyhold(seed=139):
    teams = [(-58.0, -58.0), (58.0, 58.0)]
    # The runway crosses the base west to east; the objectives are the runway midfield and the
    # two hangar aprons, which face each other across it.
    points = [(-40.0, 34.0, 12.0), (0.0, 0.0, 16.0), (40.0, -34.0, 12.0)]
    L = Layout(seed, teams, points, clear=((-6, -6, 6, 6),))

    L.road(22, -77, 0, 77, 0)                                           # runway
    for sign in (1, -1):
        L.road(12, sign * -72, sign * 24, sign * 2, sign * 24)          # parallel taxiway
        for x in (-64, -30):
            L.road(12, sign * x, sign * 11, sign * x, sign * 24)        # links to the runway
        L.road(14, sign * -74, sign * 36, sign * 2, sign * 36)          # hangar apron
        L.road(6, sign * -58, sign * -58, sign * -40, sign * -40, sign * -40, sign * -11)  # camp road to the runway
        L.road(5, sign * -40, sign * -40, sign * -10, sign * -40)       # service road to the fuel farm

    # Tower and radar dome face each other across midfield.
    L.add('control_tower', -13, 15.5, 0, pad=0.3, road_gap=None, must=True)
    L.add('radar_dome', 13.5, -16.5, 0, pad=0.3, road_gap=None, must=True)

    # Runway lights along both edges, threshold bars at both ends.
    for x in range(-72, 73, 8):
        for z in (-12, 12):
            L.add('runway_light', x, z, 0, pad=0.1, road_gap=None, ignore_points=True)
    for z in range(-9, 10, 3):
        for x in (-76, 76):
            L.add('runway_light', x, z, 0, pad=0.1, road_gap=None, ignore_points=True)

    for sign in (1, -1):
        def at(x, z):
            return sign * x, sign * z
        # Hangars behind the apron; the middle one opens onto the objective.
        for x in (-64, -40, -16):
            L.add('hangar', *at(x, 53.5), 0 if sign > 0 else 180, pad=0.8, road_gap=0.5, must=True)
        # Parked jets nose to tail on the apron either side of the objective, fuel trucks
        # alongside: close on purpose, so one fireball sets off the whole line.
        for x in (-72.5, -61.5):
            L.add('parked_jet', *at(x, 36), 0, pad=0.4, road_gap=None, must=True)
        for x in (-21.5, -10.5, 0.5):
            L.add('parked_jet', *at(x, 36), 0, pad=0.4, road_gap=None, must=True)
        for x in (-67, -16, -5):
            L.add('fuel_truck', *at(x, 43.5), 0, pad=0.3, road_gap=None, must=True)
        # Two more jets in U-shaped revetments behind the hangars.
        for x in (-64, -40):
            L.add('parked_jet', *at(x, 68), 0, pad=0.3, road_gap=None, must=True)
            L.add('revetment', *at(x, 75.8), 0, pad=0.1, road_gap=None)
            for side in (-1, 1):
                L.add('revetment', *at(x + side * 7, 68.5), 90, pad=0.1, road_gap=None)
        # Fuel farm behind each camp's end of the base: a storage tank, fuel tanks and tankers.
        L.add('storage_tank', *at(-18, -50), 0, pad=0.8, must=True)
        for x, z in ((-26, -46), (-26, -52), (-10, -52), (-10, -58)):
            L.add('fuel_tank', *at(x, z), 0, pad=0.6)
        L.add('fuel_truck', *at(-14, -39.5), 0, pad=0.3, road_gap=None)
        L.add('fuel_truck', *at(-22, -39.5), 0, pad=0.3, road_gap=None)
        # Barracks, workshops and watch posts beside the camp road.
        L.near('warehouse', *at(-60, -24), 4, 90, pad=0.8)
        L.near('office_block', *at(-30, -24), 4, 0, pad=0.8)
        L.near('garage', *at(-18, -26), 4, 0, pad=0.8)
        L.near('watchtower', *at(-6, -28), 4, pad=0.6)
        L.near('watchtower', *at(-20, 68), 4, pad=0.6)
        L.near('truck', *at(-50, -20), 4, 90, pad=0.6)
        # Cover at midfield: blast barriers and a sandbag nest by the runway edge.
        L.add('jersey_barrier', *at(-9, 6), 0, pad=0.4, road_gap=None, ignore_points=True)
        L.add('jersey_barrier', *at(5, 8), 0, pad=0.4, road_gap=None, ignore_points=True)
        L.add('sandbags', *at(-3, -7), 0, pad=0.4, road_gap=None, ignore_points=True)
        L.scatter('barrel', *at(-40, 34), 6, 12, 6, pad=0.3)
        L.scatter('ammo_crate', *at(-40, 34), 6, 12, 4, pad=0.3)
        L.add('sandbags', *at(-44, 27), 0, pad=0.4, road_gap=None, ignore_points=True)
        L.add('jersey_barrier', *at(-36, 27), 0, pad=0.4, road_gap=None, ignore_points=True)
        for x in range(-70, 1, 14):
            L.add('lamp_post', *at(x, 44.5), 0, pad=0.2, road_gap=0.2)
        # The perimeter fence along the far edge.
        hedgerow(L, *at(-76, 77.2), *at(-2, 77.2), kind='fence', gates=(40,), gate=8)
    approach_cover(L, (('boulders', -30, -60, 0), ('dirt_mound', -62, -30, 90), ('tank_trap', -36, -50, 0),
                       ('tank_trap', -50, -36, 0), ('sandbags', -30, -52, 0), ('sandbags', -52, -30, 90)))
    for cx, cz, r, d in ((-70, -70, 8, 0.14), (-72, -44, 6, 0.12), (-44, -72, 6, 0.12), (-4, -70, 7, 0.12),
                         (-74, -14, 5, 0.1), (-30, -70, 5, 0.1), (-54, -34, 5, 0.12), (-24, -64, 5, 0.12),
                         (-68, -32, 5, 0.12)):
        L.forest(cx, cz, r, d)
        L.forest(-cx, -cz, r, d)

    return finish(L)


def metrocity(seed=151):
    teams = [(-58.0, -58.0), (58.0, 58.0)]
    # A grid of 16 m avenues (x and z = +-18, +-54) cuts the city into 20 m blocks. The plaza at
    # the centre is ringed by skyscrapers; the park and a parking lot are the side objectives.
    points = [(-36.0, 36.0, 12.0), (0.0, 0.0, 16.0), (36.0, -36.0, 12.0)]
    L = Layout(seed, teams, points, clear=((-5, -5, 5, 5),))
    avenues = (-54, -18, 18, 54)
    for a in avenues:
        L.road(16, a, -78, a, 78)
        L.road(16, -78, a, 78, a)

    def extent(c):
        """A block's span along one axis: inner blocks sit between avenues, edge blocks run to the map edge."""
        return (-78, -62) if c == -72 else (62, 78) if c == 72 else (c - 10, c + 10)

    # The towers: skyscrapers round the plaza, high-rises and apartment blocks beyond, the parking
    # garage behind the parking lot. The blocks next to the camps stay open lots.
    towers = {(-36, 0): ('skyscraper', 0), (36, 0): ('skyscraper', 0), (0, -36): ('skyscraper', 0),
              (0, 36): ('skyscraper', 0), (36, 36): ('highrise_a', 0), (-36, -36): ('highrise_a', 0),
              (-72, 0): ('highrise_b', 90), (72, 0): ('highrise_b', 90), (0, -72): ('highrise_b', 0),
              (0, 72): ('highrise_b', 0), (-72, 36): ('apartment', 90), (72, -36): ('apartment', 90),
              (-72, 72): ('highrise_a', 0), (72, -72): ('highrise_a', 0), (36, -72): ('parking_garage', 0),
              (-36, 72): ('highrise_b', 0), (36, 72): ('office_block', 0), (-36, -72): ('office_block', 0),
              (72, 36): ('shop', 90), (-72, -36): ('shop', 90)}
    for (cx, cz), (kind, rot) in towers.items():
        (x0, x1), (z0, z1) = extent(cx), extent(cz)
        x, z = (x0 + x1) / 2, (z0 + z1) / 2
        if not L.add(kind, x, z, rot, pad=0.6, road_gap=0.8):
            L.near(kind, x, z, 3, rot, pad=0.6)
    # Billboards in the forecourts facing the avenues (where a tower leaves room), and street
    # trees in the block corners.
    for (cx, cz), (kind, rot) in towers.items():
        (x0, x1), (z0, z1) = extent(cx), extent(cz)
        for bx, bz, brot in (((x0 + x1) / 2 + 4.6, z0 + 2.5, 0), ((x0 + x1) / 2 - 4.6, z1 - 2.5, 0),
                             (x0 + 2.5, (z0 + z1) / 2 - 4.6, 90), (x1 - 2.5, (z0 + z1) / 2 + 4.6, 90)):
            L.add('billboard', bx, bz, brot, pad=0.3, road_gap=0.6)
        for tx, tz in ((x0 + 1.6, z0 + 1.6), (x1 - 1.6, z1 - 1.6)):
            L.add('tree', tx, tz, 0, pad=0.2, road_gap=0.3)

    # The park (west objective): tree-lined walks and hedges round a lawn.
    (x0, x1), (z0, z1) = extent(-36), extent(36)
    for u in range(0, 21, 4):
        for x, z in ((x0 + 1.5, z0 + u), (x1 - 1.5, z0 + u), (x0 + u, z0 + 1.5), (x0 + u, z1 - 1.5)):
            L.add('tree', x, z, 0, pad=0.2, road_gap=0.3)
    for x, z, rot in ((-36, 31, 0), (-36, 41, 0), (-41, 36, 90), (-31, 36, 90)):
        L.add('hedge', x, z, rot, pad=0.2, road_gap=0.3)
    L.forest(-36, 36, 4, 0.1)
    # The parking lot (east objective): four rows of cars, lamps at the corners.
    for z in (-43.4, -38.6, -33.4, -28.6):
        for i in range(6):
            L.add('car', 28.5 + i * 2.9, z, 90 if z in (-43.4, -33.4) else 270, pad=0.2, road_gap=0.3)
    for x, z in ((27.5, -27.5), (44.5, -44.5)):
        L.add('lamp_post', x, z, 0, pad=0.2, road_gap=0.1)

    # The plaza: barriers and sandbags for cover, trees in planters.
    for sign in (1, -1):
        L.add('jersey_barrier', sign * -7, sign * 3, 90, pad=0.4, road_gap=0.2, ignore_points=True)
        L.add('jersey_barrier', sign * 3, sign * 7, 0, pad=0.4, road_gap=0.2, ignore_points=True)
        L.add('sandbags', sign * 7, sign * -3, 90, pad=0.4, road_gap=0.2, ignore_points=True)
        for x, z in ((-7.5, -7.5), (7.5, -7.5)):
            L.add('tree', sign * x, sign * z, 0, pad=0.3, road_gap=0.3)

    # The streets: traffic lights on every corner, lamp posts along the kerbs, buses at the stops
    # and cars parked along the avenues. Parked buses keep 12 m of every avenue clear.
    for ax in avenues:
        for az in avenues:
            for sx in (-1, 1):
                for sz in (-1, 1):
                    L.add('traffic_light', ax + sx * 9, az + sz * 9, 0, pad=0.2, road_gap=0.1)
    for a in avenues:
        for u in range(-72, 73, 12):
            if any(abs(u - b) < 11 for b in avenues):
                continue
            for side in (-1, 1):
                L.add('lamp_post', a + side * 8.8, u, 0, pad=0.2, road_gap=0.1)
                L.add('lamp_post', u, a + side * 8.8, 0, pad=0.2, road_gap=0.1)
    for sign in (1, -1):
        for x, z, rot in ((-36, -24.4, 0), (-36, 11.6, 0), (24.4, -36, 90), (-11.6, 36, 90), (-72, -11.6, 0),
                          (11.6, -72, 90), (-60.4, 36, 90), (36, 48.4, 0)):
            L.add('bus', sign * x, sign * z, rot, pad=0.4, road_gap=None)
        for x, z, rot in ((-30, -12.8, 0), (-42, 12.8, 0), (12.8, -30, 90), (-12.8, 42, 90), (-66, 23.2, 0),
                          (-48.2, -30, 90), (23.2, 66, 90), (48.8, 30, 90), (-6, -48.8, 0), (-24, 60.8, 0)):
            L.add('car', sign * x, sign * z, rot, pad=0.4, road_gap=None)
    # Roadblocks and a sandbag nest where each camp's avenues meet.
    for sign in (1, -1):
        L.add('jersey_barrier', sign * -40, sign * -50, 0, pad=0.4, road_gap=None)
        L.add('jersey_barrier', sign * -50, sign * -40, 90, pad=0.4, road_gap=None)
        L.add('sandbags', sign * -44, sign * -44, 0, pad=0.4, road_gap=None)
    return finish(L)


# ---------------------------------------------------------------------------------- siege
# The enemy fortress fills the north-east quadrant round (42, 42): a 56 m ring of wall with a
# gate in the west and south walls (the sides facing the player), guard towers in the corners,
# the command HQ in the middle, depots, dumps and hangars round it, and an outer line of
# bunkers, tank traps and sandbags 22 m in front of the walls.
FORT = (14.0, 14.0, 70.0, 70.0)      # wall centrelines: x0, z0, x1, z1
GATE = 7.0                            # clear opening in a wall
OUTER = -8.0                          # the outer line runs along x = -8 and z = -8
SIEGE_DEFENCES = [
    # (vehicle, x, z): static team-1 defences, facing the player's corner (heading 225).
    ('guard_tower', 19.0, 19.0), ('guard_tower', 65.0, 19.0), ('guard_tower', 19.0, 65.0), ('guard_tower', 65.0, 65.0),
    ('gun_turret', 21.0, 33.0), ('gun_turret', 21.0, 51.0), ('gun_turret', 33.0, 21.0), ('gun_turret', 51.0, 21.0),
    ('aa_turret', 28.0, 28.0), ('aa_turret', 54.0, 36.0), ('aa_turret', 36.0, 54.0),
    ('rocket_turret', 52.0, 27.0), ('rocket_turret', 27.0, 52.0),
    ('artillery_emplacement', 46.0, 55.5), ('artillery_emplacement', 55.5, 46.0),
    ('mg_bunker', OUTER, 30.0), ('mg_bunker', OUTER, 54.0), ('mg_bunker', 30.0, OUTER), ('mg_bunker', 54.0, OUTER),
]
# Room kept free round each defence: its hull (length x width in balance.json) plus a little.
UNIT_SPOT = {'guard_tower': 4.0, 'gun_turret': 5.5, 'aa_turret': 5.0, 'rocket_turret': 5.0, 'mg_bunker': 4.5,
             'artillery_emplacement': 7.0}


def clip_roads(L, x0, z0, x1, z1):
    """Cuts every road where it passes through a rectangle (the fortress), keeping the pieces outside."""
    out = []
    for road in L.roads:
        pts = road['points']
        pieces, current = [], []
        for i in range(0, len(pts) - 2, 2):
            ax, az, bx, bz = pts[i], pts[i + 1], pts[i + 2], pts[i + 3]
            steps = max(1, int(math.hypot(bx - ax, bz - az) / 1.0))
            for k in range(steps + (1 if i == len(pts) - 4 else 0)):
                t = k / steps
                x, z = ax + (bx - ax) * t, az + (bz - az) * t
                if x0 <= x <= x1 and z0 <= z <= z1:
                    if len(current) >= 2:
                        pieces.append(current)
                    current = []
                else:
                    current.append((round(x, 2), round(z, 2)))
        if len(current) >= 2:
            pieces.append(current)
        for piece in pieces:
            # Keep the corners only: drop points on a straight run.
            simple = [piece[0]]
            for a, b, c in zip(piece, piece[1:], piece[2:]):
                if abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])) > 1e-3:
                    simple.append(b)
            simple.append(piece[-1])
            if math.hypot(simple[-1][0] - simple[0][0], simple[-1][1] - simple[0][1]) >= 4:
                out.append({'width': road['width'], 'points': [v for p in simple for v in p]})
    L.roads = out
    L._samples = None


def wall_line(L, axis, line, start, end, gate=None, corner_seam=0.5):
    """Base wall segments end to end along a wall centreline; `gate` is the centre of a GATE-wide
    opening. Without a gate the wall is exactly seven segments; with one, six, and the metre
    left over becomes two small seams at the corners (under the guard towers)."""
    pieces = []
    if gate is None:
        u = start
        while u + 8 <= end + 1e-6:
            pieces.append(u + 4)
            u += 8
    else:
        g0, g1 = gate - GATE / 2, gate + GATE / 2
        u = g0
        while u - 8 >= start + corner_seam - 1e-6:
            pieces.append(u - 4)
            u -= 8
        u = g1
        while u + 8 <= end - corner_seam + 1e-6:
            pieces.append(u + 4)
            u += 8
    for c in pieces:
        if axis == 'x':
            L.force('base_wall', c, line, 0)
        else:
            L.force('base_wall', line, c, 90)
    if gate is not None:
        if axis == 'x':
            L.force('base_gate', gate, line, 0)
        else:
            L.force('base_gate', line, gate, 90)


def fortify(L, name):
    """Turns a conquest layout into its siege variant (see the notes above FORT)."""
    x0, z0, x1, z1 = FORT
    L.failed = []
    # Clear the quadrant, the razor wire belt in front of the walls included, and cut the roads.
    L.remove(lambda a0, b0, a1, b1: a1 > 1.0 and b1 > 1.0)
    clip_roads(L, x0 - 1, z0 - 1, HALF, HALF)
    L.points = []
    # Clear a 12 m approach lane out from each gate, through the outer line and 26 m beyond it
    # (rock, lava or buildings there would seal the fortress off).
    west_gate, south_gate = (z0 + z1) / 2 + 0.6, (x0 + x1) / 2 - 0.6
    L.remove(lambda a0, b0, a1, b1: a1 > OUTER - 26 and a0 < x0 and b1 > west_gate - 6 and b0 < west_gate + 6)
    L.remove(lambda a0, b0, a1, b1: b1 > OUTER - 26 and b0 < z0 and a1 > south_gate - 6 and a0 < south_gate + 6)

    # Reserve the defence positions first, clearing whatever stood on the outer-line bunkers.
    for kind, x, z in SIEGE_DEFENCES:
        r = UNIT_SPOT[kind] / 2
        L.remove(lambda a0, b0, a1, b1: a0 < x + r + 1.5 and a1 > x - r - 1.5 and b0 < z + r + 1.5 and b1 > z - r - 1.5)
        L.reserved.append((x - r, z - r, x + r, z + r))
        L.units.append({'def': kind, 'team': 1, 'x': x, 'z': z, 'heading': 225})

    # The ring: each wall runs past one corner (a pinwheel), so the corners close without overlap.
    # The gates sit mid-wall, so six segments fit either side of each with half a metre to spare.
    wall_line(L, 'x', z0, x0 - 0.6, x1 - 0.6, gate=(x0 + x1) / 2 - 0.6)  # south wall
    wall_line(L, 'z', x1, z0 - 0.6, z1 - 0.6)                            # east wall
    wall_line(L, 'x', z1, x0 + 0.6, x1 + 0.6)                            # north wall
    wall_line(L, 'z', x0, z0 + 0.6, z1 + 0.6, gate=(z0 + z1) / 2 + 0.6)  # west wall

    # Inside: the HQ in the middle, hangars along the north and east walls with an ammo dump and
    # a fuel depot beside each (they chain), a helipad on the rally, floodlights, and sandbag
    # walls lining the two gate lanes (the lanes themselves stay open).
    L.put('command_hq', 42, 42, 0, pad=0.5)
    L.put('vehicle_hangar', 28.5, 62.5, 0)
    L.put('ammo_dump', 38.5, 64, 90)
    L.put('fuel_depot', 46.5, 65, 0)
    L.put('vehicle_hangar', 62.5, 28.5, 90)
    L.put('ammo_dump', 64, 38.5, 0)
    L.put('fuel_depot', 65, 46.5, 90)
    L.put('helipad', 57, 57, 0, pad=0.2)
    for x, z in ((17, 37.5), (17, 47.7), (36.3, 17), (46.5, 17), (56, 67.5), (67.5, 57)):
        L.put('floodlight_mast', x, z, 0, pad=0.2)
    for x, z, rot in ((28, 36.5, 0), (28, 47.5, 0), (36.5, 28, 90), (47.5, 28, 90)):
        L.put('sandbag_wall', x, z, rot, pad=0.2)

    # Razor wire 10 m out from the west and south walls, open at the gate approaches, the corner
    # and the far ends.
    for u in (12, 20, 28, 56, 64):
        L.put('razor_wire', 4, u, 90, pad=0.0)
        L.put('razor_wire', u, 4, 0, pad=0.0)

    # The outer line: strongpoints of sandbags round each bunker, rows of tank traps between,
    # gaps for vehicles and for the gate roads.
    def outer(kind, u, off, rot_along):
        """A piece on both outer lines: `u` along the line, `off` in front (+) or behind (-) it."""
        for x, z, rot in ((OUTER - off, u, 90 if rot_along else 0), (u, OUTER - off, 0 if rot_along else 90)):
            w, d = Layout.size(kind, rot)
            L.remove(lambda a0, b0, a1, b1: a0 < x + w / 2 + 1.5 and a1 > x - w / 2 - 1.5 and
                     b0 < z + d / 2 + 1.5 and b1 > z - d / 2 - 1.5)
            L.put(kind, x, z, rot, pad=0.2)
    for u in (30, 54):
        outer('sandbags', u - 5.5, 0, True)
        outer('sandbags', u + 5.5, 0, True)
        outer('sandbags', u, 4.2, True)
    for u, off in ((13, 0), (16.5, 1.8), (20, 0), (64, 0), (67.5, 1.8), (71, 0)):
        outer('tank_trap', u, off, True)
    for u in (6.5, 76):
        outer('sandbags', u, 0, True)
    L.remove(lambda a0, b0, a1, b1: a0 < OUTER + 2.5 and a1 > OUTER - 2.5 and b0 < OUTER + 2.5 and b1 > OUTER - 2.5)
    L.put('tank_trap', OUTER, OUTER, 0, pad=0.2)

    # Roads through the gates to the HQ, and from the HQ to the helipad.
    L.road(7, -30, west_gate, 34, west_gate)
    L.road(7, south_gate, -30, south_gate, 35)
    L.road(6, 50, 50, 56, 56)

    for def_id, x, z in L.failed:
        print(f'warning: {name} siege: could not place {def_id} near ({x}, {z})')
    L.failed = []
    for unit in L.units:
        if not L.walkable(unit['x'], unit['z']):
            raise SystemExit(f"{name} siege: {unit['def']} at ({unit['x']}, {unit['z']}) stands on a blocked cell")
    hq = next(p for p in L.props if p['def'] == 'command_hq')
    w, d = PROPS['command_hq']['width'] / 2, PROPS['command_hq']['depth'] / 2
    missing = L.reachable([('camp', *L.teams[1]), ('hq', hq['x'] - w, hq['z'] - d, hq['x'] + w, hq['z'] + d)])
    if missing:
        raise SystemExit(f'{name} siege: unreachable from the player camp: {missing}')
    return L


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
    ('redrock', redrock, 'desert', ('wellhead', 'oasis', 'caravan_stop'),
     'Redrock Canyon for Conquest: three canyon lanes between red rock walls, an oasis market at the centre.',
     'Redrock Canyon for Survival: the same canyons, holding out against waves from the north-east.'),
    ('whiteout', whiteout, 'snow', ('signal_post', 'frozen_lake', 'sawmill'),
     'Whiteout Pass for Conquest: a watchtower line across a forest pass, the frozen lake at its centre.',
     'Whiteout Pass for Survival: the same pass, holding out against waves from the north-east.'),
    ('greenvale', greenvale, 'temperate', ('west_farm', 'crossroads', 'east_farm'),
     'Greenvale Farms for Conquest: hedgerowed farmland round a crossroads village, a farmstead on either flank.',
     'Greenvale Farms for Survival: the same farmland, holding out against waves from the north-east.'),
    ('rustyard', rustyard, 'harbor', ('foundry', 'marshalling_yard', 'scrapyard'),
     'Rust Yard for Conquest: a ruined industrial district split by a marshalling yard, a foundry and a scrapyard.',
     'Rust Yard for Survival: the same ruins, holding out against waves from the north-east.'),
    ('emberridge', emberridge, 'volcanic', ('west_causeway', 'geothermal_plant', 'east_causeway'),
     'Ember Ridge for Conquest: a lava rift across basalt fields, crossed at an abandoned geothermal plant and two causeways.',
     'Ember Ridge for Survival: the same lava fields, holding out against waves from the north-east.'),
    ('junglepass', junglepass, 'jungle', ('west_village', 'temple', 'east_village'),
     'Jungle Pass for Conquest: a river through dense rainforest, a temple ruin in the central ford, stilt villages on the others.',
     'Jungle Pass for Survival: the same rainforest, holding out against waves from the north-east.'),
    ('skyhold', skyhold, 'temperate', ('west_apron', 'runway', 'east_apron'),
     'Skyhold Airbase for Conquest: a runway between two hangar aprons of parked jets and fuel trucks that chain-explode.',
     'Skyhold Airbase for Survival: the same airbase, holding out against waves from the north-east.'),
    ('metrocity', metrocity, 'urban', ('park', 'plaza', 'parking_lot'),
     'Metro City for Conquest: a grid of 16 m avenues between high-rises, skyscrapers round the central plaza.',
     'Metro City for Survival: the same city, holding out against waves from the north-east.'),
]


def main(only=()):
    for map_id, build, theme, names, conquest, survival in MAPS:
        if only and map_id not in only:
            continue
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
        # Siege: the same battlefield (built afresh, so it is identical) with the enemy fortress.
        siege = fortify(build(), map_id)
        name = conquest.split(' for ')[0]
        dump(DATA / 'maps' / f'{map_id}_siege.json',
             f'{name} for Siege: the enemy fortress holds the north-east quadrant; destroy its command HQ.',
             {'id': f'{map_id}_siege', 'theme': theme, 'size': 160, 'teams': TEAMS, 'points': [],
              'units': [u for u in CONQUEST_UNITS if u['team'] == 0] + siege.units}, siege)
        print(f'{map_id}_siege: {len(siege.props)} props, {len(siege.units)} defences')


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
