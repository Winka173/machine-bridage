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

Every map has its own outline inside the 160 m square (`boundary.py`): the edge is carved in
per map (valleys, bays, a canyon rim, trimmed corners) and never into the camps, objectives,
roads, buildings, map units or any campaign route. Decoration left outside is dropped; the
game fills the outside with terrain, blocks it to ground units and shows it on the minimap.

Once the outline is carved, every battlefield is dressed inside it with the map kit (`warzone`):
burnt-out wrecks and shell craters in no man's land, foxholes, a trench line, barricades and a
road checkpoint at every objective, a field camp on each camp's flanks, and per theme telegraph
poles, pylons, ruins, dead trees and anti-tank ditches. Cover comes in equal numbers on either
half, trees give way to it, and campaign spawns and routes stay clear.

Every placement is checked against the footprints in balance.json, the roads, the camps and
the objectives, and the result is flood-filled on the simulation's 2 m navigation grid (with
its 1.5 m obstacle clearance, filled exactly like NavGrid.AddBlocker) to prove that both camps
can reach every objective, and in Siege that the player can reach the HQ.

Last come the bases (`hardpoints.py`): each camp's HQ behind its rally, its 11 tower hardpoints
(2 large, 3 medium, 6 small) and 3 utility hardpoints (both camps in Conquest, mirrored; the
attacker's camp in Siege, the same as in Conquest; none in Survival), and an outpost of a medium
and a small hardpoint at every Conquest objective. The clutter in their way (trees, craters,
wrecks, loose rocks, the old field camp) is cleared off, and where a camp or an outpost still has
no room its buildings in the way are pulled down (never terrain); nothing else on the battlefield
changes. No hardpoint stands in a lane, a gate or a narrow pass, and with every one filled all
the routes are still open.

    python Tools/maps/build_maps.py [map ids...]   (no ids: all of them)
"""
import json
import math
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import boundary as outline_tools  # noqa: E402
import hardpoints  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data'
# The layouts are designed on a 160 m grid (HALF_DESIGN) and spread over the 300 m battlefield
# (scale_layout): positions grow by S, buildings, props and capture radii keep their size.
# (The battlefields were 200 m across, S 1.25, until round 5 made them half as big again.)
HALF_DESIGN = 80.0
S = 1.875
HALF = HALF_DESIGN * S
# Against the old 200 m battlefield: positions written for it grow by GROW; fixed numbers of
# things scattered over the open ground grow with the area, and a quarter more (DENSE).
GROW = S / 1.25
AREA = GROW * GROW
DENSE = AREA * 1.25


def more(n):
    """A count written for the 200 m battlefield, for this one (denser too)."""
    return int(round(n * DENSE))
SURFACE_TILES = {'lava_pool', 'river_water', 'river_ford'}
CELL = 2.0
CLEARANCE = 1.5


def load_props():
    text = (DATA / 'balance.json').read_text(encoding='utf-8')
    text = re.sub(r'^\s*//.*$', '', text, flags=re.M)
    balance = json.loads(text)
    props = {p['id']: p for p in balance['props']}
    # A prop's "scale" resizes its model and footprint together (see Catalog.cs).
    for p in props.values():
        scale = p.get('scale', 1.0)
        p['width'] *= scale
        p['depth'] *= scale
    return props


PROPS = load_props()


def load_static_footprints():
    """Fixed defences' anchored ground (SimWorld.StaticFootprint): 0.8 times the longer hull side."""
    text = (DATA / 'balance.json').read_text(encoding='utf-8')
    balance = json.loads(re.sub(r'^\s*//.*$', '', text, flags=re.M))
    out = {}
    for v in balance['vehicles']:
        if not v.get('static', False):
            continue
        scale = v.get('scale', 1.0)
        length = v['length'] * scale if 'length' in v else v['radius'] * 2.7
        width = v['width'] * scale if 'width' in v else v['radius'] * 1.6
        out[v['id']] = max(length, width) * 0.8
    return out


STATIC_FOOTPRINT = load_static_footprints()
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
        self.boundary = None  # the battlefield's outline, once carved (see boundary.py)
        self.half = HALF_DESIGN  # half the square's side: the design grid, until scale_layout

    # ------------------------------------------------------------------ geometry
    @staticmethod
    def size(def_id, rot):
        p = PROPS[def_id]
        w, d = p['width'], p['depth']
        if rot % 90:
            return ((w + d) * R2,) * 2  # diagonal (bridges): the bounding square, as in Prop.cs
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
        if x0 < -self.half + 2 or z0 < -self.half + 2 or x1 > self.half - 2 or z1 > self.half - 2:
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
        h = self.half
        if x0 < -h + 1 or z0 < -h + 1 or x1 > h - 1 or z1 > h - 1 or not self.fits(x0, z0, x1, z1, pad):
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

    def grid_lo(self):
        """The nav grid's low corner (x and z): the square's, unless the layout is being worked on
        in shifted coordinates (the fortress, see fortify_corner)."""
        return getattr(self, 'grid_origin', None) if getattr(self, 'grid_origin', None) is not None else -self.half

    def grid_n(self):
        """Cells along a side of the nav grid."""
        return int(getattr(self, 'grid_side', None) or self.half * 2) // int(CELL)

    def reachable(self, targets=None):
        """Flood fill on the nav grid from the first camp; returns the unreachable targets
        (by default the other camps and every objective)."""
        n = self.grid_n()
        blocked = self.blocked_grid()

        def cell(x, z):
            return int((x - self.grid_lo()) / CELL), int((z - self.grid_lo()) / CELL)

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
        blocked = self.blocked_grid(units=False)
        gx, gz = int((x - self.grid_lo()) / CELL), int((z - self.grid_lo()) / CELL)
        return not blocked[gz][gx]

    def blocked_grid(self, units=True):
        """The simulation's 2 m navigation grid, exactly as NavGrid.AddBlocker fills it: every cell
        that a blocking footprint, grown by the obstacle clearance, touches at all. Fixed defences
        placed as map units block their ground too (SimWorld anchors every one as it spawns: a
        square of 0.8 times its longer side)."""
        n = self.grid_n()
        blocked = [[False] * n for _ in range(n)]
        rects = [r for prop, r in zip(self.props, self.rects) if PROPS[prop['def']].get('blocks', False)]
        if units:
            for u in self.units:
                side = STATIC_FOOTPRINT.get(u['def'])
                if side:
                    rects.append((u['x'] - side / 2, u['z'] - side / 2, u['x'] + side / 2, u['z'] + side / 2))
        for x0, z0, x1, z1 in rects:
            a0 = int(math.floor((x0 - CLEARANCE - self.grid_lo()) / CELL))
            a1 = int(math.floor((x1 + CLEARANCE - 1e-4 - self.grid_lo()) / CELL))
            b0 = int(math.floor((z0 - CLEARANCE - self.grid_lo()) / CELL))
            b1 = int(math.floor((z1 + CLEARANCE - 1e-4 - self.grid_lo()) / CELL))
            for gx in range(max(0, a0), min(n, a1 + 1)):
                for gz in range(max(0, b0), min(n, b1 + 1)):
                    blocked[gz][gx] = True
        if self.boundary:
            # Outside the outline is terrain, blocked like SimWorld does: by the cell centre.
            for gz in range(n):
                for gx in range(n):
                    cx, cz = gx * CELL + self.grid_lo() + CELL / 2, gz * CELL + self.grid_lo() + CELL / 2
                    if not outline_tools.inside(self.boundary, cx, cz):
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


# Natural blockers: they are terrain already, so the outline may carve through them.
NATURAL = {'mesa', 'cliff_a', 'cliff_b', 'boulders', 'snow_rock', 'basalt_rock_a', 'basalt_rock_b', 'basalt_rock_c',
           'obsidian_spire', 'volcanic_cliff', 'lava_pool', 'river_water', 'river_ford', 'hedge', 'stone_wall', 'fence'}


def campaign_keep(map_id):
    """Everything the campaign places on a map: boss and convoy spawns and routes, mission units."""
    text = (DATA / 'campaign.json').read_text(encoding='utf-8')
    missions = json.loads(re.sub(r'^\s*//.*$', '', text, flags=re.M))['missions']
    circles, lines = [], []
    for m in missions:
        if m['map'] != map_id:
            continue
        for key in ('boss', 'convoy'):
            if key in m:
                spot = m[key]
                circles.append((spot['x'], spot['z'], outline_tools.KEEP_UNIT))
                route = spot.get('route', [])
                pts = [(spot['x'], spot['z'])] + [(route[i], route[i + 1]) for i in range(0, len(route) - 1, 2)]
                if len(pts) > 1:
                    lines.append((pts, outline_tools.KEEP_ROUTE))
        for u in m.get('units', []):
            circles.append((u['x'], u['z'], outline_tools.KEEP_UNIT))
    return circles, lines


def keep_of(layouts, map_id):
    """What the outline must not cut: the core (camps, objectives, campaign routes and units, the
    fortress) never; the extras (roads, buildings) except in a map's forced bites."""
    circles, lines = campaign_keep(map_id)
    core_rects, extra_rects, roads = [], [], []
    for L in layouts:
        for t in L.teams:
            circles.append((t[0], t[1], outline_tools.KEEP_CAMP))
        for x, z, r in L.points:
            circles.append((x, z, r + outline_tools.KEEP_POINT))
        for road in L.roads:
            pts = road['points']
            roads.append(([(pts[i], pts[i + 1]) for i in range(0, len(pts) - 1, 2)], road['width'] / 2 + outline_tools.KEEP_ROAD))
        for prop, (x0, z0, x1, z1) in zip(L.props, L.rects):
            if PROPS[prop['def']].get('blocks', False) and prop['def'] not in NATURAL:
                g = outline_tools.KEEP_PROP
                siege_part = prop['def'] in ('command_hq', 'base_wall', 'fuel_depot', 'ammo_dump', 'vehicle_hangar')
                (core_rects if siege_part else extra_rects).append((x0 - g, z0 - g, x1 + g, z1 + g))
        for x0, z0, x1, z1 in L.reserved:
            core_rects.append((x0 - 2, z0 - 2, x1 + 2, z1 + 2))
        for u in L.units:
            circles.append((u['x'], u['z'], outline_tools.KEEP_UNIT))
    for u in CONQUEST_UNITS + SURVIVAL_UNITS:
        circles.append((u['x'], u['z'], outline_tools.KEEP_UNIT))
    return {'core': {'circles': circles, 'rects': core_rects, 'lines': lines},
            'extra': {'rects': extra_rects, 'lines': roads}}


def apply_outline(L, poly):
    """Takes what the outline left outside off the battlefield and records the outline. What lay
    wholly outside stays as decor: drawn, never simulated, so the ground beyond the boundary is
    the same country as inside (houses, woods, rocks) instead of an empty strip; what straddled
    the line is dropped (half a house on the edge would read as playable)."""
    kept_props, kept_rects, decor, dropped = [], [], [], 0
    for prop, rect in zip(L.props, L.rects):
        x0, z0, x1, z1 = rect
        corners = ((x0, z0), (x1, z0), (x0, z1), (x1, z1), ((x0 + x1) / 2, (z0 + z1) / 2))
        inside = [outline_tools.inside(poly, x, z) for x, z in corners]
        if all(inside):
            kept_props.append(prop)
            kept_rects.append(rect)
            continue
        dropped += 1
        if not any(inside) and prop['def'] not in SURFACE_TILES:
            decor.append(prop)
    L.props, L.rects = kept_props, kept_rects
    L.decor = decor
    L.boundary = poly
    return dropped


def dump(path, comment, meta, layout):
    out = [f'// {comment}', '// Generated by Tools/maps/build_maps.py: edit the script, not this file.', '{']
    fields = []
    for key, value in meta.items():
        if key == 'bases':
            # A camp per block, a hardpoint per line.
            camps = []
            for base in value:
                head = json.dumps({k: v for k, v in base.items() if k != 'slots'})[:-1]
                slots = ',\n'.join('      ' + json.dumps(s) for s in base['slots'])
                camps.append(f'    {head}, "slots": [\n{slots}\n    ]}}')
            fields.append('  "bases": [\n' + ',\n'.join(camps) + '\n  ]')
            continue
        fields.append(f'  "{key}": {json.dumps(value)}')
    if layout.boundary:
        flat = [v for x, z in layout.boundary for v in (x, z)]
        fields.append(f'  "boundary": {json.dumps(flat)}')
    fields.append('  "roads": [\n' + ',\n'.join('    ' + json.dumps(r) for r in layout.roads) + '\n  ]')
    fields.append('  "props": [\n' + ',\n'.join('    ' + json.dumps(p) for p in layout.props) + '\n  ]')
    if getattr(layout, 'decor', None):
        fields.append('  "decor": [\n' + ',\n'.join('    ' + json.dumps(p) for p in layout.decor) + '\n  ]')
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
    n = int(HALF_DESIGN * 2 / step)
    for gx in range(n):
        x = -HALF_DESIGN + step * (gx + 0.5)
        for gz in range(n):
            z = -HALF_DESIGN + step * (gz + 0.5)
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
    # A low road bridge carries each track across its ford, square to the river (diagonal).
    L.force('bridge_road', 0.0, 0.0, 45)
    for sign in (1, -1):
        L.force('bridge_road', *diag(sign * river_s(52), sign * 52), 45)

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
# (The fortress is laid out by fortify(), further down.)
# A gate is 10 m of clear opening centred on an odd coordinate, the centre of a 2 m navigation
# cell: with the 1.5 m obstacle clearance on each wall end that leaves three whole walkable cells
# (6 m) across it, room for a parked hull and a tank passing it. A 7 m gate kept two cells, or
# one when centred on a cell edge, and a single hull stopped in it closed the fortress.
GATE = 10.0                           # clear opening in a wall

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


def wall_line(L, axis, line, start, end, gate=None, corner_seam=0.5, slit=None):
    """Base wall segments end to end along a wall centreline; `gate` is the centre of a GATE-wide
    opening. Without a gate the segments run from `start`; a wall whose length is not a whole
    number of segments leaves its odd metres as a slit at `slit` (behind the HQ, where no one
    sees it and no hull fits through it). With a gate the segments run outwards from the gate
    and the metres left over become small seams at the corners."""
    pieces = []
    if gate is None and slit is not None:
        u = start
        while u + 8 <= slit + 1e-6:
            pieces.append(u + 4)
            u += 8
        u = end
        while u - 8 >= slit - 1e-6:
            pieces.append(u - 4)
            u -= 8
    elif gate is None:
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


MODELS = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Models'


def model_or(kind, fallback):
    """A new fortress model once its art exists, else the nearest existing piece."""
    return kind if (MODELS / f'{kind}.glb').exists() else fallback


# The siege fortress on the 200 m battlefield, in three rings round the command HQ (see
# SiegeMode): the outer line (stage 1: its relay stations), an L of walls closing the north-east
# off against the map's edge (stage 2: the shield generators inside), and the walled keep with
# the HQ (stage 3). Ring distances are the larger of the x and z offsets from the HQ.
# The HQ stands in the keep's back corner, a metre or two off the walls (too close for a hull to
# get behind it), so the keep is an open yard in front of it rather than a ring of alleys round
# it: defenders coming out of the keep and attackers going in have room to pass each other.
HQ = (75.0, 75.0)
KEEP = (41.4, 41.4, 84.0, 84.0)     # keep wall centrelines x0, z0, x1, z1 (the gated walls run from 42 to 84)
KEEP_GATE = 63.0                    # the keep's gates, in its west and south walls
RING_GATE = 53.0                    # the wall ring's gates, in its west and south walls
RING_WALL = 14.0                    # the wall ring runs along x = 14 and z = 14
OUTER_LINE = -12.0                  # the outer line runs along x = -12 and z = -12
SIEGE_RINGS = [60.0, 35.0]          # beyond 60 m of the HQ: stage 1; beyond 35 m: stage 2; else stage 3
SIEGE_RALLY = (58.0, 58.0)          # the defenders' camp in Siege: the keep's yard (their conquest camp is under the HQ)


def fortress_defences():
    """(vehicle, x, z) of every fixed defence, facing the player's corner; mirrored pairs across the diagonal."""
    heavy = model_or('heavy_turret', 'gun_turret')
    flak = 'aa_turret.flak'  # the flak tower is the AA tower's rank-7 branch now
    battery = model_or('missile_battery', 'aa_turret')
    pairs = [
        # Stage 1, the outer line: bunkers on the line, towers, guns and AA behind it.
        ('mg_bunker', OUTER_LINE, 36.0), ('mg_bunker', OUTER_LINE, 78.0),
        ('guard_tower', 0.0, 24.0), ('guard_tower', 0.0, 88.0),
        ('gun_turret', 2.0, 44.0), ('aa_turret', 6.0, 74.0),
        # Stage 2, inside the wall ring, clear of the lane from each ring gate to the keep gate.
        ('gun_turret', 20.0, 40.0), ('rocket_turret', 20.0, 70.0), ('aa_turret', 32.0, 44.0),
        ('artillery_emplacement', 26.0, 88.0), (battery, 34.0, 34.0), (flak, 36.0, 88.0),
        # Stage 3, the keep: in its corners and against its walls, clear of the yard and the
        # gates' mouths (the flak tower alone, in the corner west of the HQ).
        (heavy, 46.5, 46.5), ('mg_bunker', 54.0, 79.0), ('aa_turret', 60.0, 79.0), (flak, 46.5, 77.5, 'alone'),
    ]
    out, seen = [], set()
    for kind, x, z, *alone in pairs:
        for px, pz in ((x, z),) if alone else ((x, z), (z, x)):
            if (px, pz) in seen:
                continue
            seen.add((px, pz))
            out.append((kind, px, pz))
    return out


# The fortress's own buildings (barracks, stores, offices, workshops): worth a bounty to the
# attacker when knocked down (see SiegeMode), and cover for the defenders inside.
FORTRESS_BUILDINGS = ['warehouse', 'office_block', 'container_stack', 'garage', 'container_stack', 'container', 'radar_dome',
                      'container', 'garage', 'container', 'office_block', 'garage', 'container_stack']

# Lanes kept open for the attack: from each ring gate to the keep gate, 28 m wide round it.
FORTRESS_LANES = [(13, 44, 43, 72), (44, 13, 72, 43)]

# Two buildings (or a building and a wall) either touch, closing the gap for good, or leave at
# least this much between them: 6 m of room for hull centres once both sides are grown by the
# obstacle clearance (two walkable cells at least, three where they line up), enough for two
# hulls to pass. A gap in between makes an alley one hull wide that jams the first time a
# vehicle stops in it.
ALLEY_SEALED = 2.5
ALLEY_OPEN = 9.0

# Fortress buildings stand this far from whatever they are pushed up against.
BUILDING_HUG = 0.5


def solid_rects(L):
    """What vehicles cannot drive through: blocking props and the ground fixed defences anchor."""
    rects = [r for p, r in zip(L.props, L.rects) if PROPS[p['def']].get('blocks', False)]
    for u in L.units:
        side = STATIC_FOOTPRINT.get(u['def'])
        if side:
            rects.append((u['x'] - side / 2, u['z'] - side / 2, u['x'] + side / 2, u['z'] + side / 2))
    return rects


def alley_with(L, x0, z0, x1, z1):
    """The first solid footprint that a rectangle would stand an alley's width from: too far to
    close the gap, too near to leave room to pass. None if none."""
    for rect in solid_rects(L):
        a0, b0, a1, b1 = rect
        dx = max(a0 - x1, x0 - a1, 0.0)
        dz = max(b0 - z1, z0 - b1, 0.0)
        if ALLEY_SEALED < math.hypot(dx, dz) < ALLEY_OPEN:
            return rect
    return None


def hugging(rng, anchor, w, d):
    """A centre for a w x d footprint flush against a random side of `anchor` (BUILDING_HUG off it)."""
    a0, b0, a1, b1 = anchor
    side = rng.randrange(4)
    if side < 2:
        x = a0 - BUILDING_HUG - w / 2 if side == 0 else a1 + BUILDING_HUG + w / 2
        lo, hi = sorted((b0 - d / 2 + 1, b1 + d / 2 - 1))
        return x, rng.uniform(lo, hi)
    z = b0 - BUILDING_HUG - d / 2 if side == 2 else b1 + BUILDING_HUG + d / 2
    lo, hi = sorted((a0 - w / 2 + 1, a1 + w / 2 - 1))
    return rng.uniform(lo, hi), z


def fortress_buildings(L, name, count=14, reach=None):
    """Buildings in the wall ring (the keep's yard stays open), in mirrored pairs across the
    diagonal, clear of the approach lanes. Each stands flush against something solid (a wall, a
    store, a defence) and at least an alley's width from everything else: a fortress of blocks and
    open lanes, not of one-hull alleys. Returns them, newest last (dropped first if they block a
    route)."""
    rng = random.Random(sum(ord(c) for c in name) * 7919)
    placed = []

    def in_lane(x, z, w, d):
        return any(x - w / 2 - 1 < r[2] and x + w / 2 + 1 > r[0] and z - d / 2 - 1 < r[3] and z + d / 2 + 1 > r[1]
                   for r in FORTRESS_LANES)

    def in_ring(r):
        cx, cz = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        return cx >= RING_WALL - 1 and cz >= RING_WALL - 1 and not (KEEP[0] < cx < KEEP[2] and KEEP[1] < cz < KEEP[3])

    tries = 0
    while len(placed) < count and tries < 9000:
        tries += 1
        kind = rng.choice(FORTRESS_BUILDINGS)
        rot = rng.choice((0, 90))
        anchors = [r for r in solid_rects(L) if in_ring(r)]
        if not anchors:
            break
        w, d = Layout.size(kind, rot)
        x, z = hugging(rng, rng.choice(anchors), w, d)
        x, z = round(x, 2), round(z, 2)
        if x < RING_WALL + 1 or z < RING_WALL + 1 or (40 < x < 88 and 40 < z < 88):
            continue
        for px, pz, prot in ((x, z, rot), (z, x, 90 - rot)):
            w, d = Layout.size(kind, prot)
            if in_lane(px, pz, w, d) or len(placed) >= count:
                continue
            if alley_with(L, px - w / 2, pz - d / 2, px + w / 2, pz + d / 2) is not None:
                continue
            if L.put(kind, px, pz, prot, pad=BUILDING_HUG - 0.1):
                # Never at the price of a route: a building that cuts one off goes again at once.
                if reach is not None and L.reachable(reach()):
                    L.remove(lambda a0, b0, a1, b1, hx=px, hz=pz: a0 <= hx <= a1 and b0 <= hz <= b1)
                    continue
                placed.append((kind, px, pz))
    L.failed = [f for f in L.failed if f[0] not in FORTRESS_BUILDINGS]
    return placed


UNIT_SPOT = {'guard_tower': 4.0, 'gun_turret': 5.5, 'aa_turret': 5.0, 'rocket_turret': 5.0, 'mg_bunker': 4.5,
             'artillery_emplacement': 7.0, 'heavy_turret': 8.5, 'flak_tower': 8.5, 'aa_turret.flak': 8.5, 'missile_battery': 9.5}


def siege_targets(L):
    """What the attack must be able to reach: the enemy camp, the HQ, every relay and generator."""
    generator = model_or('shield_generator', 'fuel_depot')
    hq = next(p for p in L.props if p['def'] == 'command_hq')
    w, d = PROPS['command_hq']['width'] / 2, PROPS['command_hq']['depth'] / 2
    targets = [('camp', *L.teams[1]), ('hq', hq['x'] - w, hq['z'] - d, hq['x'] + w, hq['z'] + d)]
    for p in L.props:
        if p['def'] in ('radar_station', generator):
            pw, pd = PROPS[p['def']]['width'] / 2, PROPS[p['def']]['depth'] / 2
            targets.append((p['def'], p['x'] - pw, p['z'] - pd, p['x'] + pw, p['z'] + pd))
    return targets


def fortify(L, name, buildings=True):
    """Turns a conquest layout (on the 200 m battlefield) into its siege variant: the fortress
    in three rings round the command HQ (see the notes above HQ)."""
    L.failed = []
    L.teams = [L.teams[0], SIEGE_RALLY]
    x0, z0, x1, z1 = KEEP
    ring = RING_WALL
    edge = L.half + 4.0  # past the outline: the pieces outside it are dropped, the rest seals against it
    # Clear everything inside the wall ring, and cut the roads there.
    L.remove(lambda a0, b0, a1, b1: a1 > ring - 4 and b1 > ring - 4)
    clip_roads(L, ring - 5, ring - 5, L.half, L.half)
    L.points = []
    ring_gate, keep_gate = RING_GATE, KEEP_GATE
    # Approach lanes, 14 m wide, from beyond the outer line to each ring gate.
    for g in (ring_gate,):
        L.remove(lambda a0, b0, a1, b1: a1 > OUTER_LINE - 30 and a0 < ring + 2 and b1 > g - 7 and b0 < g + 7)
        L.remove(lambda a0, b0, a1, b1: b1 > OUTER_LINE - 30 and b0 < ring + 2 and a1 > g - 7 and a0 < g + 7)

    # Defences first, clearing whatever stood on their spots.
    for kind, x, z in fortress_defences():
        r = UNIT_SPOT[kind] / 2
        L.remove(lambda a0, b0, a1, b1: a0 < x + r + 1.5 and a1 > x - r - 1.5 and b0 < z + r + 1.5 and b1 > z - r - 1.5)
        L.reserved.append((x - r, z - r, x + r, z + r))
        L.units.append({'def': kind, 'team': 1, 'x': x, 'z': z, 'heading': 225})

    # The wall ring: an L along x = 14 and z = 14 out to the map's edge, a gate in each.
    wall_line(L, 'z', ring, ring + 0.6, edge, gate=ring_gate)          # west wall, running north
    wall_line(L, 'x', ring, ring - 0.6, edge, gate=ring_gate)          # south wall, running east
    # The keep: the south and west walls run from 42 to 84 with a gate in the middle of each (two
    # segments either side of it), a floodlight mast on the corner between them; the north and
    # east walls, behind the HQ, close the ring and keep their odd metres as a slit hidden behind
    # it (the north wall takes the far corner).
    lo = x0 + 0.6
    wall_line(L, 'x', z0, lo, lo + 42.0, gate=keep_gate, corner_seam=0.0)     # south
    wall_line(L, 'z', x0, lo, lo + 42.0, gate=keep_gate, corner_seam=0.0)     # west
    wall_line(L, 'x', z1, lo, x1 + 0.6, slit=HQ[0])                            # north
    wall_line(L, 'z', x1, lo, z1 - 0.6, slit=HQ[1])                            # east
    L.force('floodlight_mast', x0, z0, 0)

    # Stage objectives: the relay stations behind the outer line, the shield generators inside
    # the ring, the command HQ in the keep.
    generator = model_or('shield_generator', 'fuel_depot')
    L.put('command_hq', *HQ, 0, pad=0.3)
    for x, z in ((-2.0, 60.0), (60.0, -2.0)):
        L.remove(lambda a0, b0, a1, b1: a0 < x + 7 and a1 > x - 7 and b0 < z + 7 and b1 > z - 7)
        L.put('radar_station', x, z, 0, pad=0.5)
    for x, z in ((26.0, 78.0), (78.0, 26.0), (24.0, 24.0)):
        L.put(generator, x, z, 0, pad=0.5)
    # The ring's stores and hangars (they chain when they go), off the lanes to the keep gates.
    L.put('fuel_depot', 35.0, 78.0, 90)
    L.put('fuel_depot', 78.0, 35.0, 0)
    L.put('ammo_dump', 19.0, 80.0, 90)
    L.put('ammo_dump', 80.0, 19.0, 0)
    L.put('vehicle_hangar', 58.0, 90.0, 0)
    L.put('vehicle_hangar', 90.0, 58.0, 90)
    L.put('helipad', 90.0, 76.0, 0, pad=0.2)
    # (Not when carving the outline: the buildings must not move the battlefield's edge for every version.)
    houses = fortress_buildings(L, name, reach=lambda: siege_targets(L)) if buildings else []
    # Floodlights beside the ring gates, and sandbag walls inside them that funnel no narrower
    # than the gate itself.
    for x, z in ((ring + 2, ring_gate - 9.5), (ring + 2, ring_gate + 9.5), (ring_gate - 9.5, ring + 2), (ring_gate + 9.5, ring + 2)):
        L.put('floodlight_mast', x, z, 0, pad=0.2)
    for x, z, rot in ((ring + 6, ring_gate - 7.5, 0), (ring + 6, ring_gate + 7.5, 0), (ring_gate - 7.5, ring + 6, 90),
                      (ring_gate + 7.5, ring + 6, 90)):
        L.put('sandbag_wall', x, z, rot, pad=0.2)

    # Razor wire 8 m out from the ring walls, open at the gate approaches.
    for u in (22.0, 30.0, 38.0, 62.0, 86.0):
        for x, z, rot in ((ring - 8, u, 90), (u, ring - 8, 0)):
            w, d = Layout.size('razor_wire', rot)
            L.remove(lambda a0, b0, a1, b1: a0 < x + w / 2 + 0.5 and a1 > x - w / 2 - 0.5 and b0 < z + d / 2 + 0.5 and b1 > z - d / 2 - 0.5)
            L.put('razor_wire', x, z, rot, pad=0.0)

    # The outer line: sandbag strongpoints round each bunker, tank traps between, open lanes.
    def outer(kind, u, off, rot_along):
        for x, z, rot in ((OUTER_LINE - off, u, 90 if rot_along else 0), (u, OUTER_LINE - off, 0 if rot_along else 90)):
            w, d = Layout.size(kind, rot)
            L.remove(lambda a0, b0, a1, b1: a0 < x + w / 2 + 1.5 and a1 > x - w / 2 - 1.5 and
                     b0 < z + d / 2 + 1.5 and b1 > z - d / 2 - 1.5)
            L.put(kind, x, z, rot, pad=0.2)
    for u in (36.0, 78.0):
        outer('sandbags', u - 5.5, 0, True)
        outer('sandbags', u + 5.5, 0, True)
        outer('sandbags', u, 4.2, True)
    for u, off in ((18.0, 0), (21.5, 1.8), (25.0, 0), (62.0, 0), (65.5, 1.8), (69.0, 0), (88.0, 0)):
        outer('tank_trap', u, off, True)

    # Roads: through each ring gate and keep gate into the keep's yard.
    L.road(7, OUTER_LINE - 30, ring_gate, x0 - 6, ring_gate, x0 - 6, keep_gate, x0 + 12, keep_gate)
    L.road(7, ring_gate, OUTER_LINE - 30, ring_gate, z0 - 6, keep_gate, z0 - 6, keep_gate, z0 + 12)

    for def_id, x, z in L.failed:
        print(f'warning: {name} siege: could not place {def_id} near ({x}, {z})')
    L.failed = []
    for unit in L.units:
        if not L.walkable(unit['x'], unit['z']):
            raise SystemExit(f"{name} siege: {unit['def']} at ({unit['x']}, {unit['z']}) stands on a blocked cell")
    targets = siege_targets(L)
    missing = L.reachable(targets)
    # A building that closes a route goes again (newest first), until every objective can be reached.
    while missing and houses:
        kind, hx, hz = houses.pop()
        L.remove(lambda a0, b0, a1, b1: a0 <= hx <= a1 and b0 <= hz <= b1)
        missing = L.reachable(targets)
    if missing:
        raise SystemExit(f'{name} siege: unreachable from the player camp: {missing}')
    if buildings:
        print(f'{name} siege: {len(houses)} fortress buildings')
    return L


# ---------------------------------------------------------------------------- battlefield dressing
# Which parts of the map kit each theme gets: telegraph poles along the roads, a line of pylons
# across open country, shattered dead trees, ruined houses round the centre, anti-tank ditches.
WAR = {
    'temperate': dict(poles=True, pylons=True, dead=True, ruins=True, ditch=True),
    'desert': dict(poles=True, pylons=True, dead=True, ruins=False, ditch=False),
    'snow': dict(poles=True, pylons=True, dead=True, ruins=False, ditch=True),
    'harbor': dict(poles=False, pylons=True, dead=False, ruins=True, ditch=False),
    'volcanic': dict(poles=False, pylons=False, dead=True, ruins=False, ditch=False),
    'jungle': dict(poles=True, pylons=False, dead=False, ruins=False, ditch=False),
    'urban': dict(poles=False, pylons=False, dead=False, ruins=True, ditch=False),
}
GREENERY = {'tree', 'palm', 'cactus', 'charred_tree', 'jungle_tree_a', 'jungle_tree_b', 'jungle_tree_c', 'bamboo_clump',
            'fern_bush', 'dead_tree'}
WRECKS = ('wreck_tank', 'wreck_tank', 'wreck_tank', 'wreck_truck', 'wreck_truck', 'wreck_car', 'wreck_car', 'artillery_wreck')
FIELD_CAMP = ('command_tent', 'camo_net', 'supply_pile', 'fuel_bladder', 'radio_mast', 'supply_pile', 'camo_net')
QUARTERS = (0, 90, 180, 270)


def segment_distance(x, z, ax, az, bx, bz):
    dx, dz = bx - ax, bz - az
    length = dx * dx + dz * dz
    t = 0.0 if length == 0 else max(0.0, min(1.0, ((x - ax) * dx + (z - az) * dz) / length))
    return math.hypot(x - ax - dx * t, z - az - dz * t)


def warzone(L, map_id, theme, poly):
    """Dresses a finished layout as a fought-over battlefield with the map kit: burnt-out wrecks,
    each with the crater of the shell that killed it, in no man's land; shell craters, foxholes, a
    trench line, barricades, a wreck and a road checkpoint round every objective; a field camp
    (command tent, camouflage nets, supply piles, a fuel bladder, a radio mast) on each camp's
    flanks; telegraph poles along the roads, pylons across open country, ruins round the centre
    and shattered trees, per theme (WAR).

    Anything that is cover (wrecks, ruins, tents, barricades, pylons: they block movement, most
    block fire too) comes in equal numbers on either half of the map and stays clear of every
    campaign spawn and route. Trees and scrub give way to it. Everything
    goes through the usual checks (camps, plazas, objectives, roads, other footprints) and inside
    the battlefield's outline `poly`."""
    style = WAR[theme]
    rng = random.Random(sum(map(ord, map_id)) * 7 + 3)
    circles, lines = campaign_keep(map_id)

    def clear(kind, x, z, rot):
        if not PROPS[kind].get('blocks', False):
            return True
        # Spawns and routes keep 6 m and 5 m of open ground round them (units path round the rest).
        reach = max(L.size(kind, rot)) / 2 + 1.0
        for cx, cz, _ in circles:
            if math.hypot(x - cx, z - cz) < 6.0 + reach:
                return False
        for pts, _ in lines:
            for (ax, az), (bx, bz) in zip(pts, pts[1:]):
                if segment_distance(x, z, ax, az, bx, bz) < 5.0 + reach:
                    return False
        return True

    def within(kind, x, z, rot, margin=1.5):
        w, d = L.size(kind, rot)
        w, d = w / 2 + margin, d / 2 + margin
        return all(outline_tools.inside(poly, x + sx * w, z + sz * d) for sx in (-1, 0, 1) for sz in (-1, 0, 1))

    # Trees and scrub give way: a wreck or a camp stands in a clearing, so only the solid props
    # (buildings, rock, walls, other dressing) are in the way; the greenery under a new piece goes.
    solid = [None]

    def ok(kind, x, z, rot, pad, road_gap):
        x, z = round(x * 2) / 2, round(z * 2) / 2
        if not (within(kind, x, z, rot) and clear(kind, x, z, rot)):
            return False
        if solid[0] is None:
            solid[0] = [(p, r) for p, r in zip(L.props, L.rects) if p['def'] not in GREENERY]
        props, rects = L.props, L.rects
        L.props, L.rects = [p for p, _ in solid[0]], [r for _, r in solid[0]]
        try:
            return L.free(kind, x, z, rot, pad, road_gap)
        finally:
            L.props, L.rects = props, rects

    def add(kind, x, z, rot):
        x, z = round(x * 2) / 2, round(z * 2) / 2
        w, d = L.size(kind, rot)
        box = (x - w / 2 - 0.5, z - d / 2 - 0.5, x + w / 2 + 0.5, z + d / 2 + 0.5)
        keep = [(p, r) for p, r in zip(L.props, L.rects)
                if not (p['def'] in GREENERY and r[0] < box[2] and r[2] > box[0] and r[1] < box[3] and r[3] > box[1])]
        L.props, L.rects = [p for p, _ in keep], [r for _, r in keep]
        L.force(kind, x, z, rot)
        solid[0] = None

    def one(kind, x, z, rot=0, pad=1.0, road_gap=1.0):
        if not ok(kind, x, z, rot, pad, road_gap):
            return False
        add(kind, x, z, rot)
        return True

    def ring(place, kind, cx, cz, r0, r1, rot=None, pad=1.0, road_gap=1.0, tries=40):
        for _ in range(tries):
            a = rng.random() * math.tau
            r = rng.uniform(r0, r1)
            if place(kind, cx + math.cos(a) * r, cz + math.sin(a) * r, rng.choice(QUARTERS) if rot is None else rot,
                     pad=pad, road_gap=road_gap):
                return True
        return False

    def run(kind, cx, cz, rot, tiles, length):
        """Tiles laid end to end (trenches, ditches) along x (rot 90) or z (rot 0), all or none."""
        ux, uz = (1, 0) if rot % 180 == 90 else (0, 1)
        spots = [(cx + ux * length * (i - (tiles - 1) / 2), cz + uz * length * (i - (tiles - 1) / 2)) for i in range(tiles)]
        if not all(ok(kind, x, z, rot, 0.5, 1.0) for x, z in spots):
            return False
        for x, z in spots:
            add(kind, x, z, rot)
        return True

    def half(x, z):
        """0 for the south-west (team 0) half of the map, 1 for the north-east half."""
        return 0 if x + z < 0 else 1

    # A field camp on the flanks of each camp.
    for tx, tz in L.teams:
        base = math.atan2(-tz, -tx)
        for i, kind in enumerate(FIELD_CAMP):
            side = 1 if i % 2 == 0 else -1
            for _ in range(80):
                a = base + side * math.radians(rng.uniform(50, 135))
                r = rng.uniform(25, 44)
                if one(kind, tx + math.cos(a) * r, tz + math.sin(a) * r, rng.choice((0, 90)), pad=1.2):
                    break

    # Every objective: craters, foxholes, a trench line, barricades, a wreck and a road checkpoint.
    for px, pz, r in L.points:
        for _ in range(3):
            ring(one, 'crater_large', px, pz, r * 0.2, r + 12, rot=0, pad=0.5, road_gap=0.5)
        for _ in range(2):
            ring(one, 'foxhole', px, pz, r + 1, r + 8, rot=0, pad=0.5)
        # A trench line along one side of the objective: two tiles if they fit, else one.
        sides = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        rng.shuffle(sides)
        spots = [(sx, sz, d, shift) for d in (r + 3.5, r + 6, r + 9) for sx, sz in sides for shift in (0, -6, 6)]
        length = PROPS['trench_straight']['depth']
        for tiles in (2, 1):
            if any(run('trench_straight', px + sx * d + sz * shift, pz + sz * d + sx * shift, 90 if sz else 0, tiles, length)
                   for sx, sz, d, shift in spots):
                break
        ring(one, 'trench_corner', px, pz, r + 4, r + 12, pad=0.8)
        for _ in range(2):
            ring(one, 'barricade', px, pz, r + 3, r + 12, pad=1.5, tries=60)
        ring(one, rng.choice(('wreck_car', 'wreck_truck')), px, pz, r + 3, r + 16, pad=1.5, tries=60)
        checkpoint(L, px, pz, r, one)

    # No man's land: burnt-out wrecks, as many on either half, each beside the crater of the shell
    # that killed it. In the city the open ground is the avenues, so the wrecks lie in the streets.
    placed = [0, 0]
    on_road = None if theme == 'urban' else 1.5
    wrecks = more(7)
    for _ in range(1500 * 3):
        if min(placed) >= wrecks:
            break
        x, z = rng.uniform(-HALF + 16, HALF - 16), rng.uniform(-HALF + 16, HALF - 16)
        if placed[half(x, z)] >= wrecks or min(math.hypot(x - t[0], z - t[1]) for t in L.teams) < 34:
            continue
        if one(rng.choice(WRECKS), x, z, rng.choice(QUARTERS), pad=1.8, road_gap=on_road):
            placed[half(x, z)] += 1
            a = rng.random() * math.tau
            one('crater_large', x + math.cos(a) * 6.5, z + math.sin(a) * 6.5, 0, pad=0.3, road_gap=None if on_road is None else 0.5)
    for _ in range(more(8)):
        for _ in range(40):
            x, z = rng.uniform(-HALF + 15, HALF - 15), rng.uniform(-HALF + 15, HALF - 15)
            if min(math.hypot(x - t[0], z - t[1]) for t in L.teams) > 30 and one('crater_large', x, z, 0, pad=0.5,
                                                                                  road_gap=None if on_road is None else 0.5):
                break

    if style['ruins']:
        for kind in ('ruin_house', 'ruin_tower', 'ruin_house', 'ruin_tower'):
            ring(one, kind, 0, 0, 22 * GROW, 42 * GROW, pad=1.5, tries=80)
        # Half the old ruins become the new, more broken ones (never larger, so nothing overlaps).
        for prop in L.props:
            if prop['def'] == 'ruin':
                roll = rng.random()
                prop['def'] = 'ruin_house' if roll < 0.5 else 'ruin_tower' if roll < 0.75 else 'ruin'

    if style['pylons']:
        # A pylon line out on each flank, each tower as near its slot as it fits.
        for t0 in (44 * GROW, -44 * GROW):
            for s0 in range(int(-52 * GROW), int(52 * GROW) + 1, 26):
                for ds, dt in ((0, 0), (0, -5), (0, 5), (-5, 0), (5, 0), (-5, -5), (5, 5), (0, -10), (0, 10), (-8, 8), (8, -8)):
                    if one('power_pylon', *diag(s0 + ds, t0 + dt), 0, pad=1.5, road_gap=2.0):
                        break

    if style['poles']:
        count = 0
        for road in L.roads:
            if road['width'] > 9 or count >= more(36):
                continue
            pts, half = road['points'], road['width'] / 2
            carry = 4.0
            for i in range(0, len(pts) - 2, 2):
                ax, az, bx, bz = pts[i:i + 4]
                length = math.hypot(bx - ax, bz - az)
                if length < 1:
                    continue
                ux, uz = (bx - ax) / length, (bz - az) / length
                at = carry
                while at < length and count < more(36):
                    x, z = ax + ux * at - uz * (half + 2.4), az + uz * at + ux * (half + 2.4)
                    if one('telegraph_pole', x, z, 0, pad=0.3, road_gap=1.2):
                        count += 1
                    at += 15.0
                carry = at - length

    if style['dead']:
        for _ in range(more(16)):
            for _ in range(30):
                x, z = rng.uniform(-HALF + 14, HALF - 14), rng.uniform(-HALF + 14, HALF - 14)
                if min(math.hypot(x - t[0], z - t[1]) for t in L.teams) > 28 and one('dead_tree', x, z, 0, pad=0.5):
                    break

    if style['ditch']:
        for _ in range(60):
            s, t = rng.uniform(-34 * GROW, -12 * GROW), rng.uniform(-30 * GROW, 30 * GROW)
            x, z = diag(s, t)
            rot = rng.choice((0, 90))
            if run('tank_ditch', x, z, rot, 2, PROPS['tank_ditch']['depth']) and run('tank_ditch', -x, -z, rot, 2, PROPS['tank_ditch']['depth']):
                break
    return L


def checkpoint(L, px, pz, r, place):
    """A road checkpoint beside a straight stretch of road 6 to 14 m out from an objective."""
    for road in L.roads:
        pts, half = road['points'], road['width'] / 2
        for i in range(0, len(pts) - 2, 2):
            ax, az, bx, bz = pts[i:i + 4]
            along_x = abs(bz - az) < 0.2 * abs(bx - ax)
            along_z = abs(bx - ax) < 0.2 * abs(bz - az)
            length = math.hypot(bx - ax, bz - az)
            if not (along_x or along_z) or length < 4:
                continue
            for k in range(int(length / 2) + 1):
                t = k * 2 / length
                x, z = ax + (bx - ax) * t, az + (bz - az) * t
                if not r + 6 < math.hypot(x - px, z - pz) < r + 14:
                    continue
                w, d = Layout.size('checkpoint', 0)
                for side in (1, -1):
                    off = half + 1.0 + d / 2
                    if along_x and place('checkpoint', x, z + side * off, 0 if side > 0 else 180, pad=0.8, road_gap=0.4):
                        return True
                    if along_z and place('checkpoint', x + side * off, z, 90 if side > 0 else 270, pad=0.8, road_gap=0.4):
                        return True
    return False


def scale_layout(L):
    """Spreads a layout built on the 160 m design grid over the 200 m battlefield: every position
    (props, roads, camps, objectives, plazas) moves out by S; buildings, props, road widths and
    capture radii keep their size, so streets, yards and fields open up. The 4 m surface tiles
    (lava, river, ford) are laid again on the battlefield's own 4 m grid, from where the scaled
    design put them, so rivers and lava stay unbroken."""
    s = S
    L.teams = [(x * s, z * s) for x, z in L.teams]
    L.points = [(x * s, z * s, r) for x, z, r in L.points]
    L.clear = tuple((a * s, b * s, c * s, d * s) for a, b, c, d in L.clear)
    L.roads = [{'width': r['width'], 'points': [v * s for v in r['points']]} for r in L.roads]
    L._samples = None
    design_tiles = {}
    props, rects = [], []
    for prop in L.props:
        if prop['def'] in SURFACE_TILES:
            design_tiles[(math.floor((prop['x'] + HALF_DESIGN) / 4.0), math.floor((prop['z'] + HALF_DESIGN) / 4.0))] = prop['def']
            continue
        x, z = round(prop['x'] * s * 20) / 20, round(prop['z'] * s * 20) / 20
        rot = prop.get('rot', 0)
        w, d = Layout.size(prop['def'], rot)
        entry = dict(prop, x=x, z=z)
        props.append(entry)
        rects.append((x - w / 2, z - d / 2, x + w / 2, z + d / 2))
    L.props, L.rects = props, rects
    L.reserved = [(a * s, b * s, c * s, d * s) for a, b, c, d in L.reserved]
    L.units = [dict(u, x=u['x'] * s, z=u['z'] * s) for u in L.units]
    L.half = HALF
    if design_tiles:
        n = int(HALF * 2 / 4.0)
        for gx in range(n):
            for gz in range(n):
                x, z = -HALF + 4.0 * (gx + 0.5), -HALF + 4.0 * (gz + 0.5)
                kind = design_tiles.get((math.floor((x / s + HALF_DESIGN) / 4.0), math.floor((z / s + HALF_DESIGN) / 4.0)))
                if kind:
                    L.force(kind, x, z)
    return L


# What fills a theme's open ground: trees in clumps, rocks, and the buildings of its hamlets.
DENSIFY = {
    'temperate': dict(trees=('tree',), rocks=('boulders',), houses=('cottage', 'house_small', 'barn', 'garage'), yard='fence'),
    'desert': dict(trees=('palm', 'cactus', 'cactus'), rocks=('boulders',), houses=('adobe_house', 'adobe_house', 'garage'), yard='wall'),
    'snow': dict(trees=('tree',), rocks=('snow_rock',), houses=('log_cabin', 'log_cabin', 'barn'), yard='fence'),
    'harbor': dict(trees=('tree',), rocks=(), houses=('warehouse', 'garage', 'container_stack'), yard='jersey_barrier'),
    'volcanic': dict(trees=('charred_tree',), rocks=('basalt_rock_a', 'basalt_rock_c'), houses=('ruin', 'ruin_house'), yard=None),
    'jungle': dict(trees=('jungle_tree_a', 'jungle_tree_b', 'jungle_tree_c', 'bamboo_clump', 'fern_bush'), rocks=('boulders',),
                   houses=('stilt_hut',), yard=None),
    'urban': dict(trees=('tree',), rocks=(), houses=('shop', 'office_block'), yard='jersey_barrier'),
}


def densify(L, map_id, theme, poly):
    """Fills the ground the bigger battlefield opened up: clumps of the theme's trees in the
    open, a few rock outcrops away from the roads, and hamlets (two or three of the theme's
    buildings with a yard and a vehicle) beside the roads, as many on either half. Everything is
    inside the outline, clear of camps, objectives, plazas and campaign routes."""
    style = DENSIFY[theme]
    rng = random.Random(sum(map(ord, map_id)) * 13 + 5)
    circles, lines = campaign_keep(map_id)

    def clear(x, z, reach):
        for cx, cz, _ in circles:
            if math.hypot(x - cx, z - cz) < 6.0 + reach:
                return False
        for pts, _ in lines:
            for (ax, az), (bx, bz) in zip(pts, pts[1:]):
                if segment_distance(x, z, ax, az, bx, bz) < 5.0 + reach:
                    return False
        return True

    def inside(kind, x, z, rot=0, margin=1.5):
        w, d = L.size(kind, rot)
        w, d = w / 2 + margin, d / 2 + margin
        return all(outline_tools.inside(poly, x + sx * w, z + sz * d) for sx in (-1, 0, 1) for sz in (-1, 0, 1))

    def put(kind, x, z, rot=0, pad=1.0, road_gap=1.0):
        x, z = round(x * 2) / 2, round(z * 2) / 2
        blocks = PROPS[kind].get('blocks', False)
        if not inside(kind, x, z, rot) or (blocks and not clear(x, z, max(L.size(kind, rot)) / 2 + 1)):
            return False
        return L.add(kind, x, z, rot, pad=pad, road_gap=road_gap)

    def far_from_points(x, z, extra):
        return all(math.hypot(x - px, z - pz) > r + extra for px, pz, r in L.points)

    def far_from_camps(x, z, d):
        return all(math.hypot(x - t[0], z - t[1]) > d for t in L.teams)

    # Tree clumps in the open.
    for _ in range(more(18)):
        for _ in range(40):
            cx, cz = rng.uniform(-HALF + 8, HALF - 8), rng.uniform(-HALF + 8, HALF - 8)
            if far_from_camps(cx, cz, 32) and far_from_points(cx, cz, 6) and outline_tools.inside(poly, cx, cz):
                break
        else:
            continue
        for _ in range(rng.randint(6, 12)):
            a, r = rng.random() * math.tau, 7 * math.sqrt(rng.random())
            put(rng.choice(style['trees']), cx + math.cos(a) * r, cz + math.sin(a) * r, 0, pad=0.3, road_gap=1.0)

    # Rock outcrops, off the roads and the objectives.
    for _ in range(more(6) if style['rocks'] else 0):
        for _ in range(40):
            cx, cz = rng.uniform(-HALF + 10, HALF - 10), rng.uniform(-HALF + 10, HALF - 10)
            if far_from_camps(cx, cz, 34) and far_from_points(cx, cz, 12) and outline_tools.inside(poly, cx, cz):
                break
        else:
            continue
        for _ in range(rng.randint(2, 4)):
            a, r = rng.random() * math.tau, 4 * math.sqrt(rng.random())
            put(rng.choice(style['rocks']), cx + math.cos(a) * r, cz + math.sin(a) * r, 0, pad=2.0, road_gap=3.0)

    # Hamlets beside the roads: equal numbers on either half.
    made = [0, 0]
    samples = L.road_samples()
    hamlets = more(3)
    for _ in range(400 * 3):
        if min(made) >= hamlets or not samples:
            break
        px, pz, half_width = samples[rng.randrange(len(samples))]
        side = 0 if px + pz < 0 else 1
        if made[side] >= hamlets or not far_from_camps(px, pz, 34) or not far_from_points(px, pz, 14):
            continue
        # Set back from the road, on whichever side has room.
        placed = 0
        for k in range(rng.randint(2, 3)):
            kind = rng.choice(style['houses'])
            a = rng.random() * math.tau
            off = half_width + 6 + k * 3 + rng.uniform(0, 4)
            x, z = px + math.cos(a) * off, pz + math.sin(a) * off
            if put(kind, x, z, rng.choice((0, 90, 180, 270)), pad=1.5, road_gap=1.5):
                placed += 1
                if style['yard'] and rng.random() < 0.6:
                    put(style['yard'], x + rng.uniform(-6, 6), z + rng.uniform(-6, 6), rng.choice((0, 90)), pad=0.4, road_gap=1.0)
                if rng.random() < 0.4:
                    put(rng.choice(('car', 'truck')), x + rng.uniform(-7, 7), z + rng.uniform(-7, 7), rng.choice((0, 90)),
                        pad=0.8, road_gap=0.6)
        if placed:
            made[side] += 1
    return L


def grown(units):
    """Start units written round the camps of the 200 m battlefield, moved out with their camp
    (the same place beside it, clear of its bastions)."""
    shift = 58 * S - 58 * 1.25
    return [dict(u, x=round(u['x'] + (shift if u['x'] > 0 else -shift), 2), z=round(u['z'] + (shift if u['z'] > 0 else -shift), 2))
            for u in units]


# The fortress is laid out for the corner of the 200 m battlefield (HQ, walls and gates in its
# own coordinates, above); on the bigger one it keeps its size and moves out to the corner.
FORT_SHIFT = HALF - 100.0


def translate(L, dx, dz):
    """Moves every position of a layout (props, roads, camps, objectives, open areas, units)."""
    L.teams = [(x + dx, z + dz) for x, z in L.teams]
    L.points = [(x + dx, z + dz, r) for x, z, r in L.points]
    L.clear = tuple((a + dx, b + dz, c + dx, d + dz) for a, b, c, d in L.clear)
    L.roads = [{'width': r['width'], 'points': [v + (dx if i % 2 == 0 else dz) for i, v in enumerate(r['points'])]} for r in L.roads]
    L._samples = None
    L.props = [dict(p, x=round((p['x'] + dx) * 20) / 20, z=round((p['z'] + dz) * 20) / 20) for p in L.props]
    L.rects = [(a + dx, b + dz, c + dx, d + dz) for a, b, c, d in L.rects]
    L.reserved = [(a + dx, b + dz, c + dx, d + dz) for a, b, c, d in L.reserved]
    L.units = [dict(u, x=u['x'] + dx, z=u['z'] + dz) for u in L.units]
    L.failed = [(d, x + dx, z + dz) for d, x, z in L.failed]
    return L


def fortify_corner(L, map_id, buildings=True):
    """Builds the fortress in its own coordinates, in the enemy's corner of the bigger battlefield:
    the layout is moved so that corner lies where the fortress plan expects it, fortified, and
    moved back. While it is built the square's edge is where the plan has it (its old 100 m
    half), which in these coordinates is the real edge of the bigger battlefield."""
    half = L.half
    L.half = half - FORT_SHIFT
    L.grid_origin, L.grid_side = -half - FORT_SHIFT, half * 2
    translate(L, -FORT_SHIFT, -FORT_SHIFT)
    fortify(L, map_id, buildings=buildings)
    translate(L, FORT_SHIFT, FORT_SHIFT)
    L.half = half
    L.grid_origin, L.grid_side = None, None
    return L


def finish(L):
    for def_id, x, z in L.failed:
        print(f'warning: could not place {def_id} near ({x}, {z})')
    missing = L.reachable()
    if missing:
        raise SystemExit(f'Unreachable from the first camp: {missing}')
    return L


TEAMS = [{'team': 0, 'x': -58 * S, 'z': -58 * S}, {'team': 1, 'x': 58 * S, 'z': 58 * S}]
SIZE = int(round(HALF * 2))
CONQUEST_UNITS = [
    {'def': 'scout_jeep', 'team': 0, 'x': -62.5, 'z': -72.5, 'heading': 45},
    {'def': 'scout_jeep', 'team': 0, 'x': -72.5, 'z': -62.5, 'heading': 45},
    {'def': 'ifv', 'team': 0, 'x': -66.25, 'z': -66.25, 'heading': 45},
    {'def': 'light_tank', 'team': 0, 'x': -75.0, 'z': -75.0, 'heading': 45},
    {'def': 'scout_jeep', 'team': 1, 'x': 62.5, 'z': 72.5, 'heading': 225},
    {'def': 'scout_jeep', 'team': 1, 'x': 72.5, 'z': 62.5, 'heading': 225},
    {'def': 'ifv', 'team': 1, 'x': 66.25, 'z': 66.25, 'heading': 225},
    {'def': 'light_tank', 'team': 1, 'x': 75.0, 'z': 75.0, 'heading': 225},
]
SURVIVAL_UNITS = [
    {'def': 'light_tank', 'team': 0, 'x': -62.5, 'z': -72.5, 'heading': 45},
    {'def': 'light_tank', 'team': 0, 'x': -72.5, 'z': -62.5, 'heading': 45},
    {'def': 'main_battle_tank', 'team': 0, 'x': -66.25, 'z': -66.25, 'heading': 45},
    {'def': 'scout_jeep', 'team': 0, 'x': -76.25, 'z': -57.5, 'heading': 45},
    {'def': 'scout_jeep', 'team': 0, 'x': -57.5, 'z': -76.25, 'heading': 45},
    {'def': 'artillery', 'team': 0, 'x': -78.75, 'z': -78.75, 'heading': 45},
    {'def': 'light_tank', 'team': 1, 'x': 62.5, 'z': 72.5, 'heading': 225},
    {'def': 'light_tank', 'team': 1, 'x': 72.5, 'z': 62.5, 'heading': 225},
    {'def': 'main_battle_tank', 'team': 1, 'x': 66.25, 'z': 66.25, 'heading': 225},
    {'def': 'scout_jeep', 'team': 1, 'x': 57.5, 'z': 76.25, 'heading': 225},
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


def plan_bases(map_id, layout, siege):
    """The bases (see hardpoints.py): both camps and the outposts on the Conquest battlefield (which
    Survival shares; it has no bases of its own), the attacker's camp in Siege. Takes the props in
    their way off both layouts. Returns (Conquest bases, {point index: outpost slots}, Siege bases)."""
    hardpoints.configure(STATIC_FOOTPRINT['headquarters'] / 0.8)
    campaign = campaign_keep(map_id)

    def footprints(L):
        """Every prop's ground as the game sees it: worked out again from its entry, since a prop
        renamed after it was placed (the old ruins turned into the new, bigger ones) still has its
        old rectangle in the layout."""
        out = []
        for prop in L.props:
            w, d = Layout.size(prop['def'], prop.get('rot', 0))
            out.append((prop['x'] - w / 2, prop['z'] - d / 2, prop['x'] + w / 2, prop['z'] + d / 2))
        return out

    def grid_of(L, rects):
        def fill(kept):
            props, old = L.props, L.rects
            L.props, L.rects = [props[i] for i in kept], [rects[i] for i in kept]
            try:
                return L.blocked_grid()
            finally:
                L.props, L.rects = props, old
        return fill

    def plan(name, L, camps, units, outposts=True, **options):
        blocks = [PROPS[p['def']].get('blocks', False) for p in L.props]
        rects = footprints(L)
        result = hardpoints.plan_bases(name, L.props, rects, blocks, grid_of(L, rects), L.grid_lo(), L.roads, L.boundary,
                                       L.points if outposts else [], L.teams, camps, units, campaign, outposts, **options)
        gone = set(result[2])
        L.props = [p for i, p in enumerate(L.props) if i not in gone]
        L.rects = [r for i, r in enumerate(L.rects) if i not in gone]
        return result

    rally, other = layout.teams
    bases, outposts, gone, report = plan(map_id, layout, [(0, rally, other), (1, other, rally)],
                                         [(u['x'], u['z']) for u in grown(CONQUEST_UNITS)])
    siege_bases, _, siege_gone, siege_report = plan(
        f'{map_id} siege', siege, [(0, siege.teams[0], siege.teams[1])],
        [(u['x'], u['z']) for u in grown(CONQUEST_UNITS) if u['team'] == 0],
        outposts=False, reuse=(bases[0], hardpoints.camp_parts(report, bases[0])), demolish=report['demolished'])

    def needed(counts):
        return ', '.join(f'{n} {k}' for k, n in counts.items()) or '-'

    camp = report.get('camp', {})
    sizes = '/'.join(str(sum(1 for s in bases[0]['slots'] if s['kind'] == 'tower' and s['size'] == n))
                     for n in ('large', 'medium', 'small'))
    utilities = sum(1 for s in bases[0]['slots'] if s['kind'] == 'utility')
    parts = '; '.join(f'{k}: {needed(v)}' for k, v in camp.items() if k != 'hq')
    print(f'{map_id}: camps of {sizes} large/medium/small towers and {utilities} utilities, HQ {camp.get("hq")} '
          f'({parts}); outposts {[len(outposts.get(i, [])) for i in range(len(layout.points))]} '
          f'({needed(report.get("outposts", {}))}); {len(gone)} props cleared'
          + (', camp buildings pulled down' if report['demolished'] else '')
          + (f', buildings pulled down at points {report["crowded"]}' if report['crowded'] else ''))
    print(f'{map_id} siege: attacker camp {"as in Conquest" if siege_report["reused"] else "planned afresh"}, '
          f'{len(siege_gone)} props cleared')
    return bases, outposts, siege_bases


def main(only=()):
    for map_id, build, theme, names, conquest, survival in MAPS:
        if only and map_id not in only:
            continue
        layout = scale_layout(build())
        # One outline per battlefield, shared by all its versions: carved round everything the
        # Conquest, Survival and Siege versions and the campaign need; then the battlefield is
        # dressed and filled inside it (the siege version the same, before its fortress).
        poly, _ = outline_tools.carve(map_id, keep_of([layout, fortify_corner(scale_layout(build()), map_id, buildings=False)], map_id), seed=len(map_id) * 31 + 7)
        densify(warzone(layout, map_id, theme, poly), map_id, theme, poly)
        siege = fortify_corner(densify(warzone(scale_layout(build()), map_id, theme, poly), map_id, theme, poly), map_id)
        dropped = apply_outline(layout, poly)
        apply_outline(siege, poly)
        missing = layout.reachable()
        if missing:
            raise SystemExit(f'{map_id}: unreachable inside the outline: {missing}')
        hq = next(p for p in siege.props if p['def'] == 'command_hq')
        w, d = PROPS['command_hq']['width'] / 2, PROPS['command_hq']['depth'] / 2
        missing = siege.reachable([('camp', *siege.teams[1]), ('hq', hq['x'] - w, hq['z'] - d, hq['x'] + w, hq['z'] + d)])
        if missing:
            raise SystemExit(f'{map_id} siege: unreachable inside the outline: {missing}')
        bases, outposts, siege_bases = plan_bases(map_id, layout, siege)
        print(f'{map_id}: outline of {len(poly)} points, {dropped} props left outside dropped')
        counts = {}
        for p in layout.props:
            counts[p['def']] = counts.get(p['def'], 0) + 1
        print(f'{map_id}: {len(layout.props)} props:', dict(sorted(counts.items())))
        points = [{'id': pid, 'name': name, 'x': x, 'z': z, 'radius': r, 'outpost': outposts.get(i, [])}
                  for i, (pid, name, (x, z, r)) in enumerate(zip(('west', 'town', 'east'), names, layout.points))]
        dump(DATA / 'maps' / f'{map_id}_conquest.json', conquest,
             {'id': f'{map_id}_conquest', 'theme': theme, 'size': SIZE, 'teams': TEAMS, 'points': points,
              'units': grown(CONQUEST_UNITS), 'bases': bases}, layout)
        dump(DATA / 'maps' / f'{map_id}_sandbox.json', survival,
             {'id': f'{map_id}_sandbox', 'theme': theme, 'size': SIZE, 'teams': TEAMS, 'units': grown(SURVIVAL_UNITS)}, layout)
        # Siege: the same battlefield (built afresh, so it is identical) with the enemy fortress.
        name = conquest.split(' for ')[0]
        dump(DATA / 'maps' / f'{map_id}_siege.json',
             f'{name} for Siege: the enemy fortress holds the north-east quadrant; destroy its command HQ.',
             {'id': f'{map_id}_siege', 'theme': theme, 'size': SIZE,
              'teams': [TEAMS[0], {'team': 1, 'x': siege.teams[1][0], 'z': siege.teams[1][1]}], 'points': [], 'siegeRings': SIEGE_RINGS,
              'units': [u for u in grown(CONQUEST_UNITS) if u['team'] == 0] + siege.units, 'bases': siege_bases}, siege)
        print(f'{map_id}_siege: {len(siege.props)} props, {len(siege.units)} defences')


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
