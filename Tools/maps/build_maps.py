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

Round 4M added eight more, laid out on the battlefield itself (world_layout) rather than on the
design grid, so causeways, bridges and walls are drawn to the metre:
  * Landing Beach (temperate): the player's camp on a beach along the south shore (sea, surf,
    hedgehogs, wire, dunes, a broken sea wall), a band of rock bluffs broken by four exits, the
    enemy on the plateau above with a coastal village round its church square and hedged fields.
  * Hydro Dam (temperate): the reservoir in the north held by a dam whose crest is one crossing,
    the river south through a gorge past the power station and the switchyard, a road bridge at
    the centre and a ford by a hamlet: the only three ways across.
  * Capital (urban): the government quarter on a river island (the palace and the domed
    parliament on the palace square, ministries along the Mall), one bridge to each bank, dense
    blocks between avenues, boulevards to the royal gardens and the central station.
  * Silver Bug Launch Site (desert): a fenced launch complex: the rocket and its gantries on the
    pad at the centre, rail lines in from the assembly building and the propellant farm, radar
    dishes, blockhouses, a perimeter road inside the razor-wire fence.
  * Salt Flats (desert): open flats with long sight lines and a few rock clusters as stepping
    stones; a salt works, a survey beacon and brine pumps.
  * Border Bridge (temperate): a broad river with the Great Bridge at its narrows (the choke
    point), a ford and an old bridge far out on the flanks, border posts, a village and a depot.
  * Swamp (jungle): hummocks in impassable water joined by 12 m causeways, main bridges and
    8 m footbridges (the narrow passes), a sunken temple and two stilt villages.
  * Coral Isles (desert): islands with sand beaches in a lagoon, joined by causeways, bridges
    and footbridges, a lighthouse on the centre island, fishing villages.

Prompt 16 added Lighthouse Bay (temperate, a rocky coast on the sea); prompt 20 M two more, laid
out the same way:
  * Open-Pit Mine (desert): a terraced pit at the centre, three broken rings of rock stepping
    down to its floor with ramps through each, haul roads down the benches and out to a crusher
    plant and an ore loadout on the rim (factories, silos, tanks, gantries, conveyors), spoil
    heaps on the flanks, truck depots by the camps. Its 14 m haul road through the pit is the
    fixed route of a slow, very large boss (FIXED_ROUTES, written as the map's "routes"): the
    ground 7 m either side of it stays open all the way, checked on the finished battlefield.
  * Orbital Gateway (snow): a spaceport with a launch pad on either flank (the rocket between
    its gantries, flame trenches, propellant tanks, blockhouses, sandbag walls), radar posts on
    both camps' approaches, and a 60 x 60 m drop-pod field at the centre kept clear of anything
    solid (floodlights and runway lights round its edge).

Lava pools, river water and fords are 4 m surface tiles (lava and deep water block, fords do
not); the map view merges them into smooth surfaces.

Every map also gets a Siege version (fortress.py `fortify`, built into the finished siege
battlefield): the enemy fortress holds 45 % of the play area in the north-east, in three rings (an
outer line across the map with relays and strongpoints, walls with closed gates and open sally
ports, the keep round the command HQ), its towers on sized hardpoints by ring, a super-gun and a rail
line or runway, all written into the map file's "fortress" block. The outline is carved round the
first, smaller fortress plan (`fortify` here, kept only for that), so the other versions and the
campaign are unchanged.

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
import functools
import json
import math
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import boundary as outline_tools  # noqa: E402
import fortress  # noqa: E402
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
    # The keep's flak tower became the AA tower's flak branch (a def that inherits, so it has no
    # size of its own here); the fortress keeps the ground planned for the old 8 m Flakturm, so
    # its layout (and every siege battlefield) stays as it was.
    out.setdefault('aa_turret.flak', 8 * 0.8)
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
        self.camp_clear = 22.0   # nothing stands this near a camp (plus half its size)
        self.world = False       # laid out on the battlefield itself, not the design grid (see world_layout)

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
        if x0 < -self.half + 2 or z0 < -self.half + 2 or x1 > self.half - 2 or z1 > self.top() - 2:
            return False
        blocks = PROPS[def_id].get('blocks', False)
        for team in self.teams:
            if math.hypot(x - team[0], z - team[1]) < self.camp_clear + max(w, d) / 2:
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
        if x0 < -h + 1 or z0 < -h + 1 or x1 > h - 1 or z1 > self.top() - 1 or not self.fits(x0, z0, x1, z1, pad):
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
        """Cells along a side of the nav grid (along x on a long battlefield)."""
        return int(getattr(self, 'grid_side', None) or self.half * 2) // int(CELL)

    def top(self):
        """The battlefield's north edge: the square's, or a long battlefield's (prompt 17, longmap.py)."""
        north = getattr(self, 'north', None)
        return north if north is not None else self.half

    def grid_nz(self):
        """Cells along z of the nav grid: a long battlefield runs on north of the square."""
        if getattr(self, 'north', None) is None:
            return self.grid_n()
        return int(round(self.north - self.grid_lo())) // int(CELL)

    def reachable(self, targets=None):
        """Flood fill on the nav grid from the first camp; returns the unreachable targets
        (by default the other camps and every objective)."""
        n, nz = self.grid_n(), self.grid_nz()
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
                if 0 <= c[0] < n and 0 <= c[1] < nz and c not in seen and not blocked[c[1]][c[0]]:
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
        n, nz = self.grid_n(), self.grid_nz()
        blocked = [[False] * n for _ in range(nz)]
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
                for gz in range(max(0, b0), min(nz, b1 + 1)):
                    blocked[gz][gx] = True
        if self.boundary:
            # Outside the outline is terrain, blocked like SimWorld does: by the cell centre.
            for gz in range(nz):
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
    # A fixed route (prompt 20 M) is kept like a campaign route, as wide as the ground it keeps open.
    for pts in FIXED_ROUTES.get(map_id, {}).values():
        lines.append((pts, ROUTE_HALF + 3.0))
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
    the line is dropped (half a house on the edge would read as playable). On a battlefield laid
    out on the ground itself (world_layout) terrain that straddles the line stays: a rock wall or
    a stretch of water runs on into the edge, with no gap beside it to drive round."""
    kept_props, kept_rects, decor, dropped = [], [], [], 0
    for prop, rect in zip(L.props, L.rects):
        x0, z0, x1, z1 = rect
        corners = ((x0, z0), (x1, z0), (x0, z1), (x1, z1), ((x0 + x1) / 2, (z0 + z1) / 2))
        inside = [outline_tools.inside(poly, x, z) for x, z in corners]
        if all(inside) or (L.world and any(inside) and prop['def'] in NATURAL and PROPS[prop['def']].get('blocks', False)):
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
        if key == 'fortress':
            # The fortress's plan: a hardpoint per line.
            head = json.dumps({k: v for k, v in value.items() if k != 'slots'})[:-1]
            slots = ',\n'.join('    ' + json.dumps(s) for s in value['slots'])
            fields.append(f'  "fortress": {head}, "slots": [\n{slots}\n  ]}}')
            continue
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


# ------------------------------------------------------------------------ battlefields of round 4M
# The eight battlefields added in round 4M are laid out on the battlefield itself (300 m, world
# coordinates) rather than on the 160 m design grid: their causeways, bridges, sea walls and city
# blocks are drawn to the metre. Camps, objectives and roads are where the builder puts them, and
# nothing stands within 41 m of a camp (the design grid's 22 m, spread by S).
CAMP_0 = (-58.0 * S, -58.0 * S)
CAMP_1 = (58.0 * S, 58.0 * S)


def world_layout(seed, points, clear=()):
    """A layout made on the battlefield itself (see the note above): scale_layout leaves it alone."""
    L = Layout(seed, [CAMP_0, CAMP_1], points, clear)
    L.half = HALF
    L.camp_clear = 22.0 * S
    L.world = True
    return L


def mirror(x, z):
    return -x, -z


def world_tiles(L, kind_at, road_gap=1.0, camp_gap=24.0, ignore_points=False):
    """Surface tiles (river water, fords, lava) on the battlefield's 4 m grid: `kind_at(x, z)` names
    the tile for each cell centre, or None. Unlike `tiles` they may come up to the camps (the sea
    beside a beach camp), but not within `camp_gap` of a rally; deep tiles keep `road_gap` off
    the roads (a road over water is a causeway or a bridge) and, unless `ignore_points`, out of
    the objectives; no tile goes into an open square or onto a prop already placed. Returns
    tiles placed."""
    placed = 0
    n = int(HALF * 2 / 4.0)
    for gx in range(n):
        x = -HALF + 4.0 * (gx + 0.5)
        for gz in range(n):
            z = -HALF + 4.0 * (gz + 0.5)
            kind = kind_at(x, z)
            if kind is None:
                continue
            x0, z0, x1, z1 = x - 2.0, z - 2.0, x + 2.0, z + 2.0
            if any(math.hypot(x - tx, z - tz) < camp_gap for tx, tz in L.teams):
                continue
            if any(x1 > c0 and x0 < c1 and z1 > d0 and z0 < d1 for c0, d0, c1, d1 in L.clear):
                continue
            deep = PROPS[kind].get('blocks', False)
            if deep and not ignore_points and any(
                    math.hypot(min(max(px, x0), x1) - px, min(max(pz, z0), z1) - pz) < r - 1 for px, pz, r in L.points):
                continue
            if deep and road_gap is not None and L.near_road(x0, z0, x1, z1, road_gap):
                continue
            if not L.fits(x0, z0, x1, z1, 0.0):
                continue
            L.force(kind, x, z)
            placed += 1
    return placed


def poly_band(pts, half):
    """The outline of a band `half` metres either side of a polyline (for water channels, dunes)."""
    left, right = [], []
    for i, (x, z) in enumerate(pts):
        (ax, az), (bx, bz) = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
        length = math.hypot(bx - ax, bz - az)
        nx, nz = -(bz - az) / length, (bx - ax) / length
        left.append((x + nx * half, z + nz * half))
        right.append((x - nx * half, z - nz * half))
    return left + right[::-1]


def polyline_distance(x, z, pts):
    """Distance from a point to a polyline of (x, z) vertices."""
    return min(segment_distance(x, z, ax, az, bx, bz) for (ax, az), (bx, bz) in zip(pts, pts[1:]))


def both_halves(fn, *spots):
    """Calls fn(x, z, *rest) for every spot (x, z, *rest) and for its mirror image through the centre."""
    for spot in spots:
        x, z, *rest = spot
        fn(x, z, *rest)
        fn(-x, -z, *rest)


def lines_of(L, kind, x0, z0, x1, z1, gap, rot=None, pad=0.2, road_gap=0.5, ignore_points=False, gates=()):
    """Copies of a prop along a straight line, `gap` metres apart end to end, broken where `gates`
    ((u0, u1) distances along the line) keeps a way through. Returns pieces placed."""
    length = math.hypot(x1 - x0, z1 - z0)
    ux, uz = (x1 - x0) / length, (z1 - z0) / length
    if rot is None:
        rot = 0 if abs(ux) >= abs(uz) else 90
    w, d = Layout.size(kind, rot)
    along = w if abs(ux) >= abs(uz) else d
    placed = 0
    u = along / 2
    while u <= length - along / 2 + 1e-6:
        if any(a - along / 2 < u < b + along / 2 for a, b in gates):
            u += 0.5
            continue
        if L.add(kind, x0 + ux * u, z0 + uz * u, rot, pad=pad, road_gap=road_gap, ignore_points=ignore_points):
            placed += 1
        u += along + gap
    return placed


def rock_wall(L, x0, x1, line, rows=2, kinds=('cliff_a', 'cliff_b'), seam=0.6, depth=10.3, jitter=1.2, scree=0.35,
              axis='x'):
    """A solid band of rock from x0 to x1 along the curve z = line(x) (its near edge): `rows` rows
    of rock pieces set edge to edge (the obstacle clearance seals the seams), the rows staggered
    by half a piece, with a little jitter so the face is broken; scree tumbled along the near
    foot. With axis 'z' the same along x = line(z) from z = x0 to x1. A piece that does not fit
    (a road, a camp) leaves its place empty. Returns pieces placed."""
    placed = 0
    for r in range(rows):
        u = x0 + (r % 2) * 5.0
        while True:
            kind = L.rng.choice(kinds)
            w, d = Layout.size(kind, 0)
            along, across = (w, d) if axis == 'x' else (d, w)
            if u + along > x1 + 1e-6:
                # The end of the row: the shortest piece that still fits.
                for kind in sorted(kinds, key=lambda k: Layout.size(k, 0)[0 if axis == 'x' else 1]):
                    w, d = Layout.size(kind, 0)
                    along, across = (w, d) if axis == 'x' else (d, w)
                    if u + along <= x1 + 1e-6:
                        break
                else:
                    break
            c = u + along / 2
            # Only the near face is broken (the jitter moves it out, never into the row behind).
            v = line(c) + r * depth + across / 2 - (L.rng.uniform(0.0, jitter) if r == 0 else 0.0)
            x, z = (c, v) if axis == 'x' else (v, c)
            if L.add(kind, x, z, L.rng.choice((0, 180)), pad=0.1, road_gap=1.0):
                placed += 1
                u += along + seam
            else:
                u += 1.0
    if scree:
        u = x0 + 2.0
        while u < x1 - 2.0:
            if L.rng.random() < scree:
                v = line(u) - L.rng.uniform(1.5, 3.0)
                x, z = (u, v) if axis == 'x' else (v, u)
                if L.add('boulders', x, z, L.rng.choice((0, 90)), pad=0.1, road_gap=1.0):
                    placed += 1
            u += 4.5
    return placed


def landing_shore(x):
    """Landing Beach's waterline: the sea lies south of it."""
    return -127.0 + 4.0 * math.sin(x / 29.0 + 0.5) + 2.0 * math.sin(x / 11.0)


def landing_bluff(x):
    """The foot of Landing Beach's bluffs: climbing gently to the east, and set back in the west
    where the beach widens round the landing camp."""
    return -60.0 + 0.08 * x + 4.0 * math.sin(x / 37.0) + 20.0 * math.exp(-((x + 112.0) / 34.0) ** 2)


def landingbeach(seed=167):
    """Landing Beach (temperate): the player lands on a long beach along the south shore, with
    the sea behind the camp, surf at the waterline, rows of hedgehogs and wire on the sand, dunes
    and a broken sea wall at the top of the beach. A band of rock bluffs closes the beach off;
    four exits (draws) lead up through it onto the plateau, where the enemy holds the bluff tops, a
    coastal village round its church square and the hedged fields behind it. The objectives: the
    beach strongpoint (east), the head of the main draw (centre) and the village square (west)."""
    beach, village = (58.0, -92.0), (-52.0, 84.0)
    vx, vz = village
    points = [(*village, 13.0), (0.0, 0.0, 16.0), (*beach, 13.0)]
    square = (vx - 17.0, vz - 17.0, vx + 17.0, vz + 17.0)
    L = world_layout(seed, points, clear=((-8, -8, 8, 8), square))
    shore, bluff = landing_shore, landing_bluff
    exits = ((-124.0, -100.0), (-60.0, -40.0), (-14.0, 14.0), (50.0, 72.0))

    # Roads: the beach road along the top of the sand; the main road up the central draw to the
    # centre and on to the enemy's camp; tracks up the other exits; the village's two streets
    # and the lanes across the plateau.
    def along(x):
        return x, round(bluff(x) - 22.0, 1)
    L.road(6, *CAMP_0, *along(-112), *along(-80), *along(-50), *along(-20), *along(0), *along(30), *along(61), *along(90),
           *along(120), *along(148))
    L.road(5, *along(61), *beach)
    L.road(7, *along(0), 0, -40, 2, -20, 0, 0, 8, 36, 30, 62, 64, 80, *CAMP_1)
    L.road(5, *along(-112), -112, -40, -108, -10, -100, 30, -104, 60, -112, 84)
    L.road(5, *along(-50), -50, -44, -44, -24, -30, -8, 0, 0)
    L.road(5, *along(61), 62, -34, 70, -20, 84, 10, 100, 60, *CAMP_1)
    L.road(6, -112, 84, -20, 84, 8, 36)
    L.road(5, vx, 42, vx, 132)
    L.road(5, -20, 84, 30, 112, 70, 126)
    L.road(5, 84, 10, 40, 20, 8, 36)

    # The sea and the surf: deep water off the beach, two tiles of shallows at the waterline, the
    # landing camp on a spit of sand.
    def sea(x, z):
        line = shore(x)
        if z < line - 7.0:
            return 'river_water'
        if z < line:
            return 'river_ford'
        return None
    world_tiles(L, sea, road_gap=None, camp_gap=26.0)

    # The bluffs: a band of rock 18 m deep from the west edge to the east edge, broken only at
    # the four exits.
    edges = [-156.0] + [v for pair in exits for v in pair] + [156.0]
    for x0, x1 in zip(edges[0::2], edges[1::2]):
        rock_wall(L, x0 + 1.0, x1 - 1.0, lambda x: bluff(x) + 1.0)

    # The beach: hedgehogs in two staggered rows above the surf, wire behind them, dunes, the sea
    # wall at the top of the sand (broken every 34 m and at every exit), knocked-out vehicles in
    # the shallows.
    for row, off in ((0, 8.0), (1, 15.0)):
        x = -140.0 + row * 13.0
        while x < 146.0:
            z = shore(x) + off
            for k in range(3):
                L.add('tank_trap', x + k * 3.4, z + (1.2 if k % 2 else -1.2), 0, pad=0.3, road_gap=1.0)
            x += 28.0
    x = -134.0
    while x < 140.0:
        L.add('razor_wire', x, shore(x) + 22.0, 0, pad=0.3, road_gap=1.0)
        x += 23.0
    for x0 in range(-136, 140, 34):
        z = bluff(x0 + 12) - 10.0
        if any(a - 8 < x0 + 12 < b + 8 for a, b in exits):
            continue
        lines_of(L, 'wall', x0, z, x0 + 25, z, 0.6, pad=0.2, road_gap=1.0)
    for x in range(-130, 146, 12):
        z = shore(x) + 27.0 + L.rng.uniform(0.0, max(0.0, bluff(x) - shore(x) - 56.0))
        for k in range(L.rng.randint(1, 3)):
            L.add('dirt_mound', x + L.rng.uniform(-4, 4), z + k * 3.5, L.rng.choice((0, 90)), pad=0.3, road_gap=1.0)
    for kind, x, off, rot in (('wreck_truck', -70.0, 3.0, 90), ('wreck_tank', -20.0, 5.0, 0), ('wreck_truck', 26.0, 4.0, 0),
                              ('wreck_tank', 96.0, 6.0, 90), ('wreck_car', 128.0, 5.0, 0), ('wreck_tank', -44.0, 13.0, 0)):
        L.add(kind, x, shore(x) + off, rot, pad=0.8, road_gap=None)

    # The beach strongpoint (east objective): a concrete casemate either side, a command post
    # behind, sandbags round the middle.
    bx, bz = beach
    for dx, dz, kind, rot in ((-19.0, 10.0, 'garage', 0), (20.0, 12.0, 'garage', 0), (0.0, 23.0, 'ruin_tower', 0),
                              (-8.0, -6.0, 'sandbags', 0), (8.0, 6.0, 'sandbags', 0), (6.0, -8.0, 'sandbags', 90)):
        L.add(kind, bx + dx, bz + dz, rot, pad=0.6, road_gap=0.6, ignore_points=True)
    L.scatter('ammo_crate', bx, bz, 3, 10, 4, pad=0.3)

    # The bluff tops: bunkers, trenches and sandbag nests looking down on the beach, a watchtower
    # at the head of each exit, and the head of the main draw ringed by barriers.
    for x in (-86.0, -26.0, 30.0, 100.0, 132.0):
        top = bluff(x) + 37.0
        L.near('garage', x, top, 4, 0, pad=0.8)
        L.add('sandbags', x + 9.0, top - 1.0, 0, pad=0.4, road_gap=0.5)
        L.add('trench_straight', x - 9.0, top + 1.0, 90, pad=0.4, road_gap=0.5)
    for a, b in exits:
        L.near('watchtower', b + 9.0, bluff(b) + 30.0, 4, pad=0.6)
    for dx, dz, kind, rot in ((-12.0, 8.0, 'sandbags', 90), (12.0, -6.0, 'sandbags', 90), (-6.0, -12.0, 'jersey_barrier', 0),
                              (7.0, 12.0, 'jersey_barrier', 0)):
        L.add(kind, dx, dz, rot, pad=0.4, road_gap=0.3, ignore_points=True)
    L.near('radar_station', 26.0, 6.0, 5, 0, pad=0.8)
    L.near('ruin_tower', -24.0, 14.0, 4, 0, pad=0.8)

    # The coastal village on the plateau: the church on the square (the west objective), houses
    # facing its two streets either side of the square, a farm on the lanes beyond.
    L.add('church', vx + 30.0, vz + 22.0, 90, pad=0.6, must=True)
    houses = ['cottage', 'house_small', 'townhouse', 'house_large', 'cottage', 'shop', 'house_small', 'townhouse']
    for axis, line, spans in (('x', vz, ((vx - 19.0, -110.0), (vx + 19.0, -24.0))), ('z', vx, ((vz + 19.0, 130.0), (vz - 19.0, 44.0)))):
        for start, end in spans:
            for side in (1, -1):
                kinds = houses[:]
                L.rng.shuffle(kinds)
                L.frontage(axis, line, side, start, end, kinds, setback=1.6, road_half=3.0, alley_every=(2, 3), cars=0.3)
    for x, z, facing in ((-118.0, 118.0, 90), (-4.0, 124.0, 0), (44.0, 50.0, 90), (122.0, -10.0, 270)):
        L.farmstead(x, z, facing)

    # The bocage: hedgerows round the fields on the plateau, gates where the lanes cross.
    for x0, z0, x1, z1 in ((-140.0, 16.0, -76.0, 16.0), (-76.0, 16.0, -76.0, 56.0), (-36.0, 20.0, -36.0, 58.0),
                           (20.0, 10.0, 76.0, 10.0), (100.0, 20.0, 100.0, 44.0), (26.0, 90.0, 26.0, 140.0),
                           (40.0, -8.0, 120.0, -8.0), (-140.0, -6.0, -80.0, -6.0), (120.0, 30.0, 146.0, 30.0),
                           (60.0, 100.0, 60.0, 140.0), (-30.0, 104.0, 10.0, 104.0), (-20.0, 40.0, 30.0, 40.0)):
        hedgerow(L, x0, z0, x1, z1, kind='hedge', gates=(14.0, 34.0), gate=10.0, trees=0.35)
    for cx, cz, r, d in ((-134.0, 136.0, 12.0, 0.14), (134.0, -30.0, 9.0, 0.12), (-10.0, 142.0, 8.0, 0.1),
                         (80.0, 40.0, 8.0, 0.1), (-84.0, 30.0, 8.0, 0.1), (134.0, 60.0, 9.0, 0.1)):
        L.forest(cx, cz, r, d)
    return finish(L)


DAM_Z = 96.0          # the dam's crest road runs along z = 96 ...
DAM_X = 50.0          # ... from x = -50 to 50
DAM_HALF = 6.0        # the crest is 12 m of dry concrete


def dam_river_x(z):
    """Hydro Dam's river below the dam: its centre line, running north to south."""
    return 6.0 * math.sin(z / 31.0) - 0.04 * z


def dam_river_half(z):
    """The river's half width: a narrow gorge below the dam, wider down the valley."""
    return 9.0 if z > 40.0 else 9.0 + min(3.0, (40.0 - z) / 12.0)


def dam_lake_south(x):
    """The reservoir's south shore west of the dam (it floods everything north of this)."""
    return 104.0 + 5.0 * math.sin(x / 17.0) + 0.06 * max(0.0, -x - 60.0)


def dam_lake_east(z):
    """The reservoir's east shore, north of the dam's east end."""
    return 56.0 + 4.0 * math.sin(z / 9.0)


def hydrodam(seed=173):
    """Hydro Dam (temperate): a river valley dammed at its head. The reservoir fills the
    north-west, held by the dam whose crest road is one crossing; below it the river runs south
    through a rocky gorge past the power station (west bank, the west objective) and the
    switchyard (east bank), under the road bridge at the centre (the centre objective) and over a
    broad ford by a hamlet (east bank, the east objective) out of the valley. The river splits the
    battlefield: the dam, the bridge and the ford are the only ways across."""
    station, ford = (-40.0, 64.0), (36.0, -98.0)
    points = [(*station, 12.0), (0.0, 0.0, 16.0), (*ford, 12.0)]
    L = world_layout(seed, points)
    rx, rh = dam_river_x, dam_river_half
    bridge = (-22.0, -8.5, 22.0, 8.5)
    ford_z = (-116.0, -84.0)

    # Roads: the valley road from camp to camp over the bridge; the dam road along the west
    # bank and over the crest to the enemy's camp; the ford road; a road down each bank.
    L.road(7, *CAMP_0, -80, -60, -52, -12, -30, 0, 30, 0, 52, 12, 80, 60, *CAMP_1)
    L.road(6, *CAMP_0, -126, -60, -112, 20, -84, 60, -60, 84, -50, DAM_Z, DAM_X, DAM_Z, 70, 98, *CAMP_1)
    L.road(6, *CAMP_0, -60, -104, -20, -100, 20, -100, *ford, 70, -80, 112, -20, 126, 60, *CAMP_1)
    L.road(5, *station, -60, 84)
    L.road(5, -52, -12, -60, 30, *station)
    L.road(5, 52, 12, 66, 44, 68, 80, 70, 98)

    # The water: the reservoir north of the dam and its shores, the river down the gorge and the
    # valley, shallows at the ford, and under the bridge (drawn as water beneath the deck).
    def water(x, z):
        if abs(x) <= DAM_X + 2.0 and abs(z - DAM_Z) < DAM_HALF:
            return None                                   # the crest
        if z > DAM_Z + DAM_HALF - 0.1 and (x < -DAM_X and z > dam_lake_south(x) or -DAM_X <= x < dam_lake_east(z)):
            return 'river_water'
        if z < DAM_Z - DAM_HALF and abs(x - rx(z)) < rh(z):
            if ford_z[0] < z < ford_z[1]:
                return 'river_ford'
            if bridge[0] < x < bridge[2] and bridge[1] < z < bridge[3]:
                return 'river_ford'
            return 'river_water'
        return None
    world_tiles(L, water, road_gap=None, camp_gap=40.0, ignore_points=True)
    # The bridge deck over the river, two lanes side by side.
    for x in (-10.0, 10.0):
        for z in (-4.2, 4.2):
            L.force('bridge_road', x, z, 90)

    # The dam: its concrete faces either side of the crest, lamps along the crest, the intake
    # towers on the lake side and the spillway blocks below.
    for zf in (DAM_Z - DAM_HALF - 0.6, DAM_Z + DAM_HALF + 0.6):
        x = -DAM_X
        while x + 8.0 <= DAM_X + 1e-6:
            L.force('base_wall', x + 4.0, zf, 0)
            x += 8.0
    for x in range(-44, 45, 11):
        L.add('lamp_post', float(x), DAM_Z + 4.6, 0, pad=0.1, road_gap=None, ignore_points=True)
    for x in (-24.0, 24.0):
        L.force('water_tower', x, DAM_Z + DAM_HALF + 5.0)

    # West bank, the power station at the foot of the dam: the turbine hall against the gorge,
    # transformer yard, offices, the penstock pipes down from the dam and its fuel store.
    sx, sz = station
    L.add('factory', -21.0, 81.0, 0, pad=0.5, road_gap=0.8, must=True)
    L.near('warehouse', -66.0, 48.0, 4, 90, pad=0.8)
    L.near('office_block', -76.0, 90.0, 4, 0, pad=0.8)
    for z in (72.0, 64.0):
        L.add('pipeline', -16.0, z, 90, pad=0.3, road_gap=0.5, ignore_points=True)
    for dx, dz in ((-6.0, -8.0), (6.0, -9.0)):
        L.add('fuel_tank', sx + dx, sz + dz, 0, pad=0.6, ignore_points=True)
    L.add('sandbags', sx + 8.0, sz + 2.0, 90, pad=0.4, ignore_points=True)
    L.scatter('barrel', sx, sz, 3, 10, 5, pad=0.3)
    L.scatter('truck', sx, sz, 5, 11, 1, pad=0.8)

    # East bank, the switchyard: pylons in rows inside a fence, transformers between them, the
    # power line marching off east.
    for i in range(3):
        for j in range(3):
            L.add('power_pylon', 28.0 + i * 9.0, 62.0 + j * 9.0, 0, pad=0.3, road_gap=0.8)
    for x, z in ((32.5, 66.5), (41.5, 75.5)):
        L.add('container', x, z, 90, pad=0.3, road_gap=0.8)
    for x0, z0, x1, z1 in ((22.0, 56.0, 58.0, 56.0), (22.0, 88.0, 58.0, 88.0), (22.0, 56.0, 22.0, 88.0)):
        hedgerow(L, x0, z0, x1, z1, kind='fence', gates=(18.0,), gate=8.0)
    for k, (x, z) in enumerate(((74.0, 70.0), (100.0, 60.0), (126.0, 50.0))):
        L.add('power_pylon', x, z, 0, pad=1.0, road_gap=1.5)

    # The gorge: broken rock along both banks below the dam, the valley opening further down.
    for z, side in ((50.0, -1), (40.0, 1), (30.0, -1)):
        formation(L, rx(z) + side * (rh(z) + 7.0), z, 'cliff_b', 3, 2)
    for z in (84.0, 70.0, 56.0):
        outcrop(L, rx(z) + rh(z) + 5.0, z, 3, 2, pad=0.4)
    for z, side in ((30.0, 1), (16.0, -1), (-30.0, 1), (-46.0, -1), (-64.0, 1), (-140.0, -1), (-136.0, 1)):
        outcrop(L, rx(z) + side * (rh(z) + 8.0), z, 5, 3, pad=0.5)

    # The ford: a hamlet on the east bank (the east objective) with a mill, cottages and a jetty,
    # a farm on the west bank.
    fx, fz = ford
    for dx, dz, kind, rot in ((24.0, -18.0, 'barn', 90), (30.0, 10.0, 'cottage', 90), (-2.0, 26.0, 'cottage', 0),
                              (8.0, -28.0, 'house_small', 0)):
        L.near(kind, fx + dx, fz + dz, 4, rot, pad=0.8)
    L.scatter('ammo_crate', fx, fz, 3, 9, 3, pad=0.3)
    L.add('sandbags', fx - 9.0, fz + 3.0, 90, pad=0.4, ignore_points=True)
    L.farmstead(-58.0, -128.0, 0)

    # The bridge's approaches: barriers and a checkpoint hut either end.
    for sign in (1, -1):
        L.add('jersey_barrier', sign * 26.0, sign * 12.0, 90, pad=0.4, road_gap=0.3, ignore_points=True)
        L.add('sandbags', sign * 30.0, sign * -11.0, 0, pad=0.4, road_gap=0.3, ignore_points=True)
        L.near('garage', sign * 40.0, sign * -20.0, 4, 0, pad=0.8)

    # Woods on the valley sides and round the lake, fields and hedges on the valley floor.
    for cx, cz, r, d in ((-130.0, 84.0, 14.0, 0.18), (-96.0, 20.0, 12.0, 0.16), (-140.0, -10.0, 9.0, 0.14),
                         (130.0, -84.0, 14.0, 0.18), (96.0, -20.0, 12.0, 0.16), (140.0, 10.0, 9.0, 0.14),
                         (86.0, 140.0, 10.0, 0.16), (-60.0, 40.0, 8.0, 0.12), (60.0, -40.0, 8.0, 0.12),
                         (-40.0, -60.0, 8.0, 0.12), (40.0, 30.0, 7.0, 0.1), (-86.0, -130.0, 8.0, 0.12),
                         (86.0, -130.0, 8.0, 0.12), (-30.0, 130.0, 8.0, 0.1)):
        L.forest(cx, cz, r, d)
    for x0, z0, x1, z1 in ((-100.0, -76.0, -40.0, -76.0), (-36.0, -76.0, -36.0, -30.0), (100.0, 76.0, 40.0, 76.0),
                           (36.0, 30.0, 36.0, 50.0), (-100.0, -20.0, -100.0, 10.0), (100.0, 20.0, 100.0, -10.0)):
        hedgerow(L, x0, z0, x1, z1, kind='hedge', gates=(14.0,), gate=10.0, trees=0.3)
    return finish(L)


def city_block(L, x0, z0, x1, z1, kinds, gap=1.0, pad=0.3, road_gap=0.8):
    """Fills a city block with buildings in rows, a metre apart (the obstacle clearance closes the
    seams, so the block is one solid mass with its streets round it), each the biggest of `kinds`
    that still fits the room left. Returns buildings placed."""
    placed = 0
    z = z0
    while z < z1 - 5.0:
        x, depth = x0, 0.0
        while x < x1 - 5.0:
            options = [(k, r) for k in kinds for r in (0, 90)]
            L.rng.shuffle(options)
            smallest = min(Layout.size(k, 0)[0] for k in kinds) + gap

            def fill(o):
                # Pieces that leave either no room at the end of the row or room for another first.
                left = x1 - x - Layout.size(*o)[0]
                return 0 if left < 3.0 or left >= smallest else 1
            options.sort(key=fill)
            for kind, rot in options:
                w, d = Layout.size(kind, rot)
                if x + w > x1 + 1e-6 or z + d > z1 + 1e-6 or (depth and d > depth + 3.0):
                    continue
                if L.add(kind, x + w / 2, z + d / 2, rot, pad=pad, road_gap=road_gap):
                    placed += 1
                    x += w + gap
                    depth = max(depth, d)
                    break
            else:
                x += 2.0
        z += (depth or 4.0) + gap
    return placed


def capital(seed=179):
    """Capital (urban): the government quarter stands on an island between two arms of the river,
    joined to each bank by one bridge: the west bridge over the north arm and the east bridge over
    the south arm, so every way across goes over the island. On the island the Mall, a boulevard
    lined with trees, runs through the palace square (the centre objective) between the palace
    (north) and the domed parliament (south), with ministries along it. On the banks, dense blocks
    of offices, flats, shops and towers between avenues; a boulevard from each bridge to the
    royal gardens on the north bank (the west objective) or the central station's square on the
    south bank (the east objective), a park, and a plaza by each camp. The streets, the river and
    the blocks mirror through the centre."""
    gardens, station = (-84.0, 100.0), (84.0, -100.0)
    points = [(*gardens, 13.0), (0.0, 0.0, 16.0), (*station, 13.0)]
    square = (-28.0, -12.0, 28.0, 12.0)
    plazas = ((62.0, -122.0, 106.0, -80.0), (-106.0, 80.0, -62.0, 122.0))
    L = world_layout(seed, points, clear=(square,) + plazas)
    arm = (36.0, 52.0)                       # the arms of the river: z = 36..52 and -52..-36
    bridges = [(-84.0, 1), (84.0, -1)]       # (x, which arm: 1 north, -1 south)

    def at(sign, x, z):
        return sign * x, sign * z

    def box(sign, x0, z0, x1, z1):
        (a, b), (c, d) = at(sign, x0, z0), at(sign, x1, z1)
        return min(a, c), min(b, d), max(a, c), max(b, d)

    # Streets, the same on either half: the Mall on the island and its cross streets; on each
    # bank the embankment, the avenue, the cross streets and the boulevard from its bridge.
    L.road(24, -146, 0, -30, 0)                                                         # the Mall, either
    L.road(24, 30, 0, 146, 0)                                                           # side of the square
    for x in (-120, -36, 36, 120):
        for z in (1, -1):
            L.road(10, x, 12 * z, x, 34 * z)
    for sign in (1, -1):
        L.road(20, *at(sign, 84, -12), *at(sign, 84, -60))                               # bridge street and bridge
        L.road(10, *at(sign, -146, -60), *at(sign, 146, -60))                            # embankment
        L.road(16, *at(sign, -58, -104), *at(sign, 60, -104))                            # avenue, either side
        L.road(16, *at(sign, 108, -104), *at(sign, 146, -104))                           # of the square
        L.road(12, *at(sign, 60, -104), *at(sign, 60, -118), *at(sign, 108, -118), *at(sign, 108, -104))
        L.road(24, *at(sign, 84, -60), *at(sign, 84, -78))                               # the boulevard
        for x in (0, 40, 124):
            L.road(12, *at(sign, x, -60), *at(sign, x, -146))                            # cross streets
        L.road(12, *at(sign, -40, -60), *at(sign, -40, -104))
    L.road(10, *CAMP_0, -96, -60)
    L.road(10, *CAMP_0, -58, -104)
    L.road(10, *CAMP_1, 96, 60)
    L.road(10, *CAMP_1, 58, 104)

    # The river: two arms from the west edge to the east edge, water under each bridge's deck.
    def water(x, z):
        if not arm[0] <= abs(z) <= arm[1]:
            return None
        for bx, which in bridges:
            if abs(x - bx) < 13.0 and z * which > 0:
                return 'river_ford'
        return 'river_water'
    world_tiles(L, water, road_gap=None, camp_gap=30.0)
    for bx, which in bridges:
        for dx in (-8.35, 0.0, 8.35):
            L.force('bridge_road', bx + dx, which * 44.0, 0)

    # The palace (north of the square) and the domed parliament (south), wing to wing.
    L.add('apartment', 0.0, 27.0, 0, pad=0.3, road_gap=0.5, must=True)
    for x in (-14.2, 14.2):
        L.add('office_block', x, 27.0, 0, pad=0.3, road_gap=0.5, must=True)
    L.add('radar_dome', 0.0, -25.0, 0, pad=0.3, road_gap=0.5, must=True)
    for x in (-10.2, 10.2):
        L.add('office_block', x, -27.0, 0, pad=0.3, road_gap=0.5, must=True)
    for x in (-24.0, 24.0):
        L.add('apartment', x, -23.0, 90, pad=0.3, road_gap=0.5)
    # The ministries along the Mall, and its avenue trees.
    kinds_ministry = ('office_block', 'apartment', 'townhouse', 'shop')
    for sign in (1, -1):
        for x0, z0, x1, z1 in ((42.5, 13.5, 113.5, 34.0), (126.5, 13.5, 147.0, 34.0), (42.5, -34.0, 72.5, -13.5),
                               (95.5, -34.0, 113.5, -13.5), (126.5, -34.0, 147.0, -13.5)):
            city_block(L, *box(sign, x0, z0, x1, z1), kinds_ministry)
    for x in range(-136, 137, 12):
        if abs(x) > 30:
            for z in (10.0, -10.0):
                L.add('tree', float(x), z, 0, pad=0.2, road_gap=None)

    # The banks: blocks of flats, offices, shops and towers between the streets (round the
    # gardens the blocks give way to the park), a park by the embankment, the camp plaza.
    kinds_bank = ('apartment', 'office_block', 'highrise_a', 'highrise_b', 'shop', 'townhouse', 'skyscraper')
    for sign in (1, -1):
        blocks = [(7.0, -94.5, 33.0, -66.5), (47.0, -94.5, 70.5, -66.5), (97.5, -94.5, 117.0, -66.5),
                  (131.0, -94.5, 147.0, -66.5), (-44.5, -147.0, -7.0, -113.5), (7.0, -147.0, 33.0, -113.5),
                  (47.0, -147.0, 52.5, -113.5), (115.5, -147.0, 117.0, -113.5), (131.0, -147.0, 147.0, -113.5)]
        for b in blocks:
            city_block(L, *box(sign, *b), kinds_bank)
        for u in range(-46, -8, 5):
            for v in (-70.0, -92.0):
                L.add('tree', *at(sign, float(u), v), 0, pad=0.2, road_gap=0.5)
        for v in range(-88, -71, 5):
            for u in (-46.0, -10.0):
                L.add('tree', *at(sign, u, float(v)), 0, pad=0.2, road_gap=0.5)
        for u, v, rot in ((-28.0, -76.0, 0), (-28.0, -86.0, 0), (-36.0, -81.0, 90), (-20.0, -81.0, 90)):
            L.add('hedge', *at(sign, u, v), rot, pad=0.2, road_gap=0.5)
        # Boulevard trees and street furniture, buses and parked cars.
        for v in range(-66, -92, -8):
            for u in (74.5, 93.5):
                L.add('tree', *at(sign, u, float(v)), 0, pad=0.2, road_gap=None)
        for u in range(-50, 147, 16):
            for v in (-54.0, -66.0, -95.0, -113.0):
                L.add('lamp_post', *at(sign, float(u), v), 0, pad=0.2, road_gap=0.1)
        for u, v, rot in ((20.0, -100.0, 0), (104.0, -100.0, 0), (60.0, -57.0, 0), (-3.5, -130.0, 90), (127.5, -84.0, 90)):
            L.add('bus', *at(sign, u, v), rot, pad=0.4, road_gap=None)
        for u, v, rot in ((-30.0, -108.0, 0), (30.0, -108.0, 0), (130.0, -108.0, 0), (43.5, -80.0, 90), (3.5, -76.0, 90),
                          (120.5, -128.0, 90), (60.0, -63.0, 0), (-20.0, -63.0, 0)):
            L.add('car', *at(sign, u, v), rot, pad=0.4, road_gap=None)
        for u, v in ((0.0, -60.0), (40.0, -60.0), (124.0, -60.0), (0.0, -104.0), (40.0, -104.0), (124.0, -104.0)):
            for du, dv in ((-9.0, -9.0), (9.0, 9.0)):
                L.add('traffic_light', *at(sign, u + du, v + dv), 0, pad=0.2, road_gap=0.1)
        for u, v in ((-124.0, -80.0), (-80.0, -130.0), (-134.0, -134.0)):
            L.forest(*at(sign, u, v), 6, 0.1)

    # The west objective, the royal gardens: hedged parterres and tree walks round a lawn, the
    # chapel and the orangery behind.
    gx, gz = gardens
    for dx in (-24.0, -12.0, 12.0, 24.0):
        for dz in (-20.0, 20.0):
            L.add('hedge', gx + dx, gz + dz, 0, pad=0.2, road_gap=0.5)
    for dz in (-12.0, 0.0, 12.0):
        for dx in (-30.0, 30.0):
            L.add('hedge', gx + dx, gz + dz, 90, pad=0.2, road_gap=0.5)
    for u in range(-36, 37, 6):
        for v in (-28.0, 28.0):
            L.add('tree', gx + u, gz + v, 0, pad=0.2, road_gap=0.5)
    L.near('church', gx, gz + 40.0, 3, 90, pad=0.8)
    L.forest(gx - 44.0, gz + 2.0, 8, 0.12)
    # The east objective, the central station: the train hall behind the square, offices either
    # side, buses and taxis on the square.
    sx, sz = station
    L.near('warehouse', sx, sz - 38.0, 3, 0, pad=0.8)
    for x in (sx - 18.0, sx + 18.0):
        L.near('office_block', x, sz - 38.0, 2, 0, pad=0.8)
    for x in (sx - 16.0, sx + 16.0):
        L.add('bus', x, sz + 2.0, 90, pad=0.4, road_gap=None, ignore_points=True)
    for dx, dz in ((-6.0, 8.0), (6.0, 8.0), (-8.0, -6.0), (8.0, -6.0)):
        L.add('car', sx + dx, sz + dz, 0, pad=0.4, road_gap=None, ignore_points=True)

    # The palace square: planters, lamps and barricades thrown up across the Mall.
    for dx, dz, kind, rot in ((-20.0, 8.0, 'jersey_barrier', 90), (20.0, -8.0, 'jersey_barrier', 90), (-8.0, 0.0, 'sandbags', 90),
                              (8.0, 0.0, 'sandbags', 90), (-14.0, -9.0, 'tree', 0), (14.0, 9.0, 'tree', 0)):
        L.force(kind, dx, dz, rot)
    return finish(L)


LAUNCH_FENCE = 104.0      # the perimeter fence runs along x and z = +-104


def launchsite(seed=181):
    """Silver Bug launch site (desert): a secret launch complex behind a perimeter fence of razor
    wire, gated where the roads come in. At the centre the launch pad (the centre objective): the
    rocket standing between two umbilical gantries, flame pits either side, blockhouses round it.
    Two rail lines come in to the pad, mirrored: from the assembly building in the north-west (the
    west objective), where the rocket's stages wait on their transporter, and from the propellant
    farm in the south-east (the east objective) with its tank train. Radar dishes and a tracking
    station stand between the pad and each camp; a perimeter road runs inside the fence."""
    vab, farm = (-50.0, 80.0), (50.0, -80.0)
    points = [(*vab, 13.0), (0.0, 0.0, 16.0), (*farm, 13.0)]
    L = world_layout(seed, points, clear=((-6, -6, 6, 6),))
    f = LAUNCH_FENCE

    def at(sign, x, z):
        return sign * x, sign * z

    # Roads: from each camp through its gate to the pad, the perimeter road inside the fence,
    # service roads to the assembly building and the farm; the two rail lines.
    for sign in (1, -1):
        L.road(8, *at(sign, -58 * S, -58 * S), *at(sign, -88, -88), *at(sign, -40, -40), *at(sign, -14, -14))
        L.road(6, *at(sign, -96, -96), *at(sign, 96, -96))
        L.road(6, *at(sign, -96, -96), *at(sign, -96, 96))
        L.road(6, *at(sign, -40, -40), *at(sign, 20, -60), *at(sign, *farm))
        L.road(6, *at(sign, -40, -40), *at(sign, -70, 10), *at(sign, -96, 40))
        L.road(6, *at(sign, 96, -40), *at(sign, 124, -30), *at(sign, 146, -26))           # side gates
        L.road(6, *at(sign, 40, -96), *at(sign, 30, -124), *at(sign, 26, -146))
        L.road(3, *at(sign, -80, 150), *at(sign, -80, 30), *at(sign, -16, 30))                       # the rail line

    # The launch pad: the rocket (a tall stack) on the north edge of the apron with the fixed
    # service gantry behind it, the mobile service tower drawn back to the south edge, flame pits
    # either side of the rocket, propellant tanks, blockhouses and sandbag walls round the apron.
    L.add('refinery_tower', 0.0, 12.0, 0, pad=0.3, road_gap=None, ignore_points=True, must=True)
    L.add('gantry_crane', 0.0, 21.0, 0, pad=0.3, road_gap=None, ignore_points=True, must=True)
    L.add('gantry_crane', 0.0, -22.0, 0, pad=0.3, road_gap=None, ignore_points=True, must=True)
    L.add('tank_ditch', 0.0, 3.5, 90, pad=0.3, road_gap=None, ignore_points=True)
    for sign in (1, -1):
        L.add('crater_large', sign * 30.0, sign * 30.0, 0, pad=0.3, road_gap=None)
        for x, z in ((-40.0, 28.0), (36.0, 40.0)):
            L.add('fuel_tank', *at(sign, x, z), 0, pad=0.6, road_gap=0.5)
        for x, z, rot in ((-46.0, 12.0, 0), (42.0, -14.0, 90)):
            L.near('garage', *at(sign, x, z), 6, rot, pad=0.8)
        L.add('sandbag_wall', *at(sign, -26.0, 40.0), 0, pad=0.4, road_gap=0.5)

    # The rail lines: the rocket's stages on their transporter by the pad, wagons in the sidings.
    for sign in (1, -1):
        transporter = ['rail_tanker', 'rail_tanker', 'rail_boxcar']
        if sign > 0:
            train(L, 30.0, -60.0, -20.0, transporter, gap=(0.6, 0.8))
            train(L, None, 112.0, 148.0, ['rail_boxcar', 'rail_boxcar', 'rail_tanker'], gap=(0.8, 1.4), rot=90, x=-80.0)
        else:
            train(L, -30.0, 20.0, 60.0, ['rail_tanker', 'rail_tanker', 'rail_tanker'], gap=(0.6, 0.8))
            train(L, None, -148.0, -112.0, ['rail_tanker', 'rail_tanker', 'rail_boxcar'], gap=(0.8, 1.4), rot=90, x=80.0)

    # West, the assembly building: the tall hall the rail line runs into, offices and a crane.
    vx, vz = vab
    L.add('hangar', -80.0, 84.0, 90, pad=0.8, road_gap=None, must=True)
    L.near('office_block', vx + 10.0, vz - 24.0, 6, 0, pad=0.8)
    L.near('warehouse', vx + 30.0, vz + 4.0, 6, 0, pad=0.8)
    L.add('gantry_crane', -80.0, 56.0, 90, pad=0.5, road_gap=None)
    L.scatter('ammo_crate', vx, vz, 3, 10, 4, pad=0.3)
    # East, the propellant farm: storage tanks, fuel tanks and pipes.
    fx, fz = farm
    for x, z in ((61.5, -58.0), (72.5, -58.0), (72.5, -47.0)):
        L.add('storage_tank', x, z, 0, pad=0.8, road_gap=0.8)
    for dx, dz in ((20.0, 6.0), (-20.0, 8.0)):
        L.add('fuel_tank', fx + dx, fz + dz, 0, pad=0.6, road_gap=0.5)
    L.add('pipeline', fx + 12.0, fz - 8.0, 0, pad=0.3, road_gap=0.5, ignore_points=True)
    L.add('pipeline', fx - 12.0, fz - 8.0, 0, pad=0.3, road_gap=0.5, ignore_points=True)
    L.scatter('barrel', fx, fz, 3, 10, 6, pad=0.3)

    # Radar dishes and a tracking station between the pad and each camp, mirrored.
    for sign in (1, -1):
        for x, z in ((-66.0, -26.0), (-82.0, -6.0), (-54.0, -54.0)):
            L.near('radar_station', *at(sign, x, z), 8, 0, pad=0.8)
        L.near('radar_dome', *at(sign, -8.0, -58.0), 8, 0, pad=0.8)
        L.near('office_block', *at(sign, 30.0, -76.0), 6, 0, pad=0.8)
        L.near('ammo_dump', *at(sign, -20.0, -62.0), 4, 0, pad=0.8)
        L.near('watchtower', *at(sign, -f + 16.0, 60.0), 4, pad=0.6)
        L.near('watchtower', *at(sign, 60.0, -f + 16.0), 4, pad=0.6)

    # The perimeter fence: razor wire along x and z = +-104, gated wherever a road crosses it and
    # at the camps' corners.
    for sign in (1, -1):
        for axis in ('x', 'z'):
            u = -f
            while u + 8.0 <= f + 1e-6:
                x, z = (u + 4.0, -f) if axis == 'x' else (-f, u + 4.0)
                L.add('razor_wire', *at(sign, x, z), 0 if axis == 'x' else 90, pad=0.1, road_gap=2.0)
                u += 9.0

    # The desert round the complex: rock formations, scrub, a few palms by the offices.
    for sign in (1, -1):
        for kind, x, z in (('mesa', -128.0, 40.0), ('cliff_b', -40.0, -128.0), ('mesa', 20.0, 128.0), ('cliff_b', -128.0, -20.0)):
            formation(L, *at(sign, x, z), kind, 8, 3)
        for x, z in ((-86.0, -30.0), (-30.0, -86.0), (-70.0, 80.0), (10.0, -80.0), (-84.0, 10.0)):
            outcrop(L, *at(sign, x, z), 5, 3, pad=0.6)
        for x, z, r in ((-120.0, 90.0, 8.0), (80.0, -130.0, 7.0), (-10.0, 120.0, 6.0)):
            L.forest(*at(sign, x, z), r, 0.1, kind='cactus')
    return finish(L)


def saltflat(seed=163):
    """Salt Flats (desert): open salt flats with long sight lines for the guns and missiles, broken
    only by a few rock clusters set as stepping stones along the approaches, so short-range
    vehicles can close in from cover to cover. A salt works and a brine pumping station hold the
    side objectives (the same ground, mirrored), a survey beacon the centre."""
    west, east = (-56.0, 88.0), (56.0, -88.0)
    points = [(*west, 13.0), (0.0, 0.0, 16.0), (*east, 13.0)]
    L = world_layout(seed, points, clear=((-6, -6, 6, 6),))

    # Tracks across the flat: camp to camp over the beacon, the cross track from the works to the
    # pumps, and each camp's track out to its nearer objective.
    L.road(6, *CAMP_0, -60, -60, 60, 60, *CAMP_1)
    L.road(5, *west, -30, 42, 30, -42, *east)
    L.road(5, -96, -86, -40, -94, *east)
    L.road(5, 96, 86, 40, 94, *west)

    # The survey beacon at the centre: a mast, the survey huts, a weather radar either side, and
    # sandbags dug in round them.
    L.add('radio_mast', 3.5, 9.0, 0, pad=0.5, road_gap=0.5, ignore_points=True)
    for x, z, kind, rot in ((-24.0, 17.0, 'radar_station', 0), (-9.0, 6.0, 'container', 90), (6.0, -12.0, 'container', 0),
                            (12.0, 4.0, 'sandbags', 90), (-4.0, 13.0, 'sandbags', 0)):
        for sx, sz in ((x, z), (-x, -z)):
            L.add(kind, sx, sz, rot, pad=0.5, road_gap=0.4, ignore_points=True)

    # The works and the pumps: the same ground mirrored, the sheds and tanks beyond the objective
    # (away from the centre) and behind it, the flanks left open for the outposts. Salt heaps and
    # the evaporation pans' low walls at the works; pump jacks and a pipeline at the pumps.
    for sign, works in ((1, True), (-1, False)):
        px, pz = west if works else east

        def at(dx, dz):
            return px + sign * dx, pz + sign * dz
        L.near('warehouse' if works else 'factory', *at(-6.0, 30.0), 3, 0, pad=0.8)
        L.near('garage', *at(22.0, 22.0), 3, 0, pad=0.8)
        L.near('storage_tank', *at(-30.0, 8.0), 3, 0, pad=0.8)
        for dx, dz in ((-6.0, 6.0), (7.0, -4.0)):
            if works:
                L.add('dirt_mound', *at(dx, dz), 0, pad=0.4, road_gap=0.4, ignore_points=True)
            else:
                L.add('oil_pump', *at(dx, dz), 0, pad=0.8, road_gap=0.6, ignore_points=True)
        if works:
            for dz in (44.0, 50.0):
                lines_of(L, 'stone_wall', *at(-24.0, dz), *at(8.0, dz), 1.5, pad=0.2)
        else:
            lines_of(L, 'pipeline', *at(-26.0, 46.0), *at(8.0, 46.0), 2.0, pad=0.3)
        L.scatter('barrel', px, pz, 3, 10, 5, pad=0.3)
        L.scatter('ammo_crate', px, pz, 3, 10, 3, pad=0.3)

    # The rock clusters: stepping stones 40-60 m apart along every approach (the straight run
    # between the camps stays open), a mesa or a cliff with scree at its foot, or a boulder heap.
    # The same on either half, mirrored through the centre.
    stones = (
        # camp to the beacon, either side of the track
        ('mesa', -110.0, -58.0), ('cliff_b', -58.0, -110.0), ('boulders', -58.0, -26.0), ('boulders', -26.0, -58.0),
        # out along the west flank to the far objective
        ('cliff_b', -118.0, 6.0), ('mesa', -104.0, 70.0),
        # to the near objective
        ('cliff_a', 4.0, -120.0),
        # the middle of the flanks, between the objectives and the beacon
        ('mesa', -62.0, 34.0), ('boulders', -24.0, 60.0),
    )
    for kind, x, z in stones:
        for sx, sz in ((x, z), (-x, -z)):
            if kind == 'boulders':
                outcrop(L, sx, sz, 5, 4, pad=0.6)
            else:
                formation(L, sx, sz, kind, 8, 3)
    return finish(L)


def border_bank(x):
    """Border Bridge's river: its north bank (the south bank is the mirror image, -border_bank(-x)).
    The river is 50 m across, narrowing to 24 m at the Great Bridge (a bridge is built at the
    narrows)."""
    return 24.0 + 3.0 * math.sin(x / 25.0) - 12.0 * math.exp(-(x / 30.0) ** 2)


def borderbridge(seed=191):
    """Border Bridge (temperate): a broad river on the border runs across the battlefield from
    west to east. The Great Bridge carries the highway over it at the centre (the centre
    objective), a border post at either end; the only other ways across are long detours at the
    far flanks: a ford in the west and a narrow old bridge in the east. A border village holds the
    north bank (the west objective), the customs depot the south bank (the east objective)."""
    village, depot = (-60.0, 84.0), (60.0, -84.0)
    points = [(*village, 13.0), (0.0, 0.0, 14.0), (*depot, 13.0)]
    L = world_layout(seed, points)
    great = (-22.0, 22.0)                     # the Great Bridge's span of the river (x)
    small = (116.0, 128.0)                    # the old bridge's (the east flank)
    ford = (-138.0, -112.0)                   # the ford's (the west flank)

    # Roads: the highway over the Great Bridge from camp to camp, the embankment road along each
    # bank, the detour roads out to the ford and the old bridge, and lanes to the objectives.
    L.road(10, *CAMP_0, -70, -70, -8, -40, 0, -30, 0, 30, 8, 40, 70, 70, *CAMP_1)
    for sign in (1, -1):
        L.road(6, -146 * sign, -38 * sign, 146 * sign, -38 * sign)
    L.road(6, -125, -38, -125, 38)                                                     # the ford track
    L.road(5, 122, -38, 122, 38)                                                       # the old bridge
    L.road(6, *CAMP_0, -118, -60, -125, -38)
    L.road(6, *CAMP_1, 118, 60, 122, 38)
    L.road(6, *CAMP_0, -40, -110, 20, -96, *depot, 100, -60, 122, -38)
    L.road(6, *CAMP_1, 40, 110, -20, 96, *village, -100, 60, -125, 38)
    L.road(5, *village, -40, 50, -8, 40)
    L.road(5, *depot, 40, -50, 8, -40)

    # The river: deep water from edge to edge, fords at the ford, water drawn under both
    # bridges' decks.
    def water(x, z):
        if not -border_bank(-x) < z < border_bank(x):
            return None
        if ford[0] < x < ford[1] or great[0] < x < great[1] or small[0] < x < small[1]:
            return 'river_ford'
        return 'river_water'
    world_tiles(L, water, road_gap=None, camp_gap=40.0, ignore_points=True)
    for x in (-16.7, -8.35, 0.0, 8.35, 16.7):
        for z in (-10.0, 10.0):
            L.force('bridge_road', x, z, 0)
    for z in (-20.0, 0.0, 20.0):
        L.force('bridge_road', 122.0, z, 0)

    # Keep the decks and the ford clear of the battlefield dressing that follows.
    L.clear = ((great[0], -20.0, great[1], 20.0), (small[0], -26.0, small[1], 26.0), (ford[0], -26.0, ford[1], 26.0))

    # The border posts at either end of the Great Bridge: customs houses, barrier booths, a
    # watchtower and the flag masts, mirrored.
    for sign in (1, -1):
        def at(x, z, s=sign):
            return s * x, s * z
        L.add('checkpoint', *at(-14.0, -46.0), 0, pad=0.4, road_gap=0.3)
        L.add('checkpoint', *at(14.0, -50.0), 180, pad=0.4, road_gap=0.3)
        L.near('office_block', *at(-34.0, -58.0), 5, 0, pad=0.8)
        L.near('garage', *at(30.0, -60.0), 5, 0, pad=0.8)
        L.near('watchtower', *at(-26.0, -46.0), 4, pad=0.6)
        for x in (-6.0, 6.0):
            L.add('floodlight_mast', *at(x, -33.0), 0, pad=0.3, road_gap=0.2)
        for x in range(-60, 61, 12):
            if abs(x) > 24:
                L.add('fence', *at(float(x), -31.0), 0, pad=0.2, road_gap=0.5)
        L.add('jersey_barrier', *at(-16.0, -64.0), 90, pad=0.4, road_gap=0.3)
        L.add('jersey_barrier', *at(16.0, -66.0), 90, pad=0.4, road_gap=0.3)
        # The old bridge's and the ford's posts: a sandbagged hut each.
        L.near('garage', *at(136.0, -50.0), 4, 0, pad=0.8)
        L.add('sandbags', *at(112.0, -46.0), 0, pad=0.4, road_gap=0.5)
        L.near('garage', *at(-104.0, -52.0), 4, 0, pad=0.8)

    # The border village (north bank): houses round its green, a church, a farm.
    vx, vz = village
    L.add('church', vx + 2.0, vz + 30.0, 90, pad=0.6)
    for dx, dz, kind, rot in ((-26.0, 12.0, 'cottage', 90), (-24.0, -12.0, 'house_small', 90), (26.0, 14.0, 'townhouse', 270),
                              (24.0, -14.0, 'cottage', 270), (-4.0, -26.0, 'house_small', 0), (-30.0, 34.0, 'barn', 0),
                              (32.0, 36.0, 'house_large', 0)):
        L.near(kind, vx + dx, vz + dz, 4, rot, pad=0.8)
    L.farmstead(-114.0, 118.0, 90)
    # The customs depot (south bank): warehouses, a truck park and containers, trucks at the gate.
    dx0, dz0 = depot
    for dx, dz, kind, rot in ((0.0, -30.0, 'warehouse', 0), (-28.0, -14.0, 'warehouse', 90), (28.0, 14.0, 'office_block', 0),
                              (26.0, -16.0, 'container_stack', 90), (30.0, -6.0, 'container_stack', 90), (-26.0, 16.0, 'garage', 0)):
        L.near(kind, dx0 + dx, dz0 + dz, 4, rot, pad=0.8)
    L.scatter('truck', dx0, dz0, 5, 11, 3, pad=0.8)
    L.scatter('ammo_crate', dx0, dz0, 3, 10, 4, pad=0.3)
    L.farmstead(114.0, -118.0, 270)

    # The banks: hedged fields, woods on the flanks, a line of poplars along each embankment.
    for sign in (1, -1):
        for x0, z0, x1, z1 in ((-100.0, -70.0, -40.0, -70.0), (40.0, -60.0, 100.0, -60.0), (-90.0, -130.0, -90.0, -84.0),
                               (80.0, -140.0, 80.0, -100.0), (-40.0, -140.0, -40.0, -100.0)):
            hedgerow(L, sign * x0, sign * z0, sign * x1, sign * z1, kind='hedge', gates=(14.0,), gate=10.0, trees=0.3)
        for x, z, r, d in ((-136.0, -86.0, 10.0, 0.16), (-70.0, -130.0, 9.0, 0.14), (100.0, -130.0, 8.0, 0.12),
                           (136.0, -70.0, 9.0, 0.14), (-20.0, -120.0, 7.0, 0.1)):
            L.forest(sign * x, sign * z, r, d)
        for x in range(-140, 141, 9):
            L.add('tree', float(x), sign * -45.0, 0, pad=0.2, road_gap=1.0)
    return finish(L)


class Archipelago:
    """Dry ground in water, for the swamp and the islands: hummocks or islands (discs with a
    wobbly shore), the camps' own ground (squares round the rallies), causeways (bands along
    polylines) and bridges (bands of shallows under a deck across a channel, from one end to the
    other); everything else is deep water. Given for one half of the battlefield and mirrored
    through the centre. `beach` rings every island with that many metres of shallows (walkable
    sand at the water's edge)."""

    def __init__(self, discs, causeways, bridges, camp_half=50.0, beach=0.0, seed=1):
        self.discs = discs + [(-x, -z, r) for x, z, r in discs if (x, z) != (0.0, 0.0)]
        self.causeways = causeways + [([(-x, -z) for x, z in pts], half) for pts, half in causeways]
        self.bridges = bridges + [((-a[0], -a[1]), (-b[0], -b[1]), half) for a, b, half in bridges]
        self.camp_half = camp_half
        self.beach = beach
        self.seed = seed

    def shore(self, x, z, cx, cz, r):
        """How far inside the disc's wobbly shore a point is (negative outside)."""
        a = math.atan2(z - cz, x - cx)
        k = cx * 0.13 + cz * 0.07 + self.seed
        wobble = 1.0 + 0.1 * math.sin(3 * a + k) + 0.06 * math.sin(5 * a - 2 * k)
        return r * wobble - math.hypot(x - cx, z - cz)

    def island_depth(self, x, z):
        """Metres inside the islands and camps' ground (the largest over them), negative outside."""
        best = -1e9
        for cx, cz in (CAMP_0, CAMP_1):
            best = max(best, self.camp_half - max(abs(x - cx), abs(z - cz)))
        for cx, cz, r in self.discs:
            best = max(best, self.shore(x, z, cx, cz, r))
        return best

    def depth(self, x, z):
        """Metres inside the dry ground (the largest over every shape), negative in the water."""
        best = self.island_depth(x, z)
        for pts, half in self.causeways:
            best = max(best, half - polyline_distance(x, z, pts))
        return best

    def in_bridge(self, x, z):
        for (ax, az), (bx, bz), half in self.bridges:
            length = math.hypot(bx - ax, bz - az)
            ux, uz = (bx - ax) / length, (bz - az) / length
            u = (x - ax) * ux + (z - az) * uz
            if -1.0 <= u <= length + 1.0 and abs((x - ax) * uz - (z - az) * ux) < half:
                return True
        return False

    def tile(self, x, z):
        """The surface tile for the 4 m cell centred on (x, z), or None for dry ground."""
        if self.in_bridge(x, z):
            return 'river_ford'
        if self.depth(x, z) >= 0.0:
            return None
        # Beaches ring the islands, not the causeways (they keep their width).
        return 'river_ford' if self.island_depth(x, z) > -self.beach else 'river_water'

    def lay(self, L):
        """Lays the water, and a deck along every bridge (lanes side by side, end to end)."""
        world_tiles(L, self.tile, road_gap=None, camp_gap=40.0, ignore_points=True)
        for (ax, az), (bx, bz), half in self.bridges:
            length = math.hypot(bx - ax, bz - az)
            ux, uz = (bx - ax) / length, (bz - az) / length
            rot = round(math.degrees(math.atan2(ux, uz))) % 180
            lanes = max(1, int(round(half * 2 / 8.35)))
            pieces = max(1, int(math.ceil((length + 2.0) / 20.0)))
            cx, cz = (ax + bx) / 2, (az + bz) / 2
            for i in range(lanes):
                for k in range(pieces):
                    u = (k - (pieces - 1) / 2) * 20.0
                    v = (i - (lanes - 1) / 2) * 8.35
                    L.force('bridge_road', round(cx + ux * u + uz * v, 2), round(cz + uz * u - ux * v, 2), rot)

    def dry(self, x, z, margin=0.0):
        return self.depth(x, z) >= margin and not self.in_bridge(x, z)


def swamp_layout():
    """Swamp's hummocks, causeways and bridges (one half; the other is its mirror image). The
    causeways and bridges run square to the 4 m water grid and on it, so their width is exact:
    20 m of dry ground (five 4 m tiles, eight walkable 2 m cells with the obstacle clearance off
    either bank) for a causeway or a main bridge, 8 m (two cells: a narrow pass) for a wooden
    footbridge. (They were 12 m, four cells, until prompt 12: a siege army of heavy hulls going both
    ways jammed on the main bridges to the centre.)"""
    discs = [(0.0, 0.0, 34.0), (62.0, -86.0, 28.0), (-66.0, -22.0, 16.0), (-22.0, -66.0, 16.0), (-108.0, 30.0, 14.0)]
    causeways = [
        ([(-68.0, -48.0), (-68.0, -32.0)], 8.0),                  # camp - west hummock
        ([(-48.0, -68.0), (-32.0, -68.0)], 8.0),                  # camp - south hummock
        ([(-8.0, -64.0), (10.0, -64.0)], 8.0),                    # south hummock - footbridge ...
        ([(26.0, -64.0), (46.0, -64.0)], 8.0),                    # ... - near objective
        ([(-48.0, -104.0), (-10.0, -104.0)], 8.0),                # camp - footbridge ...
        ([(10.0, -104.0), (42.0, -104.0)], 8.0),                  # ... - near objective
        ([(-108.0, -48.0), (-108.0, 0.0)], 8.0),                  # the west detour: camp - footbridge ...
        ([(-108.0, 40.0), (-108.0, 76.0), (-86.0, 76.0)], 8.0),   # ... the hummock beyond - far objective
        ([(-84.0, -20.0), (-104.0, -20.0)], 8.0),                 # west hummock - the detour
        ([(-20.0, -84.0), (-20.0, -104.0)], 8.0),                 # south hummock - the camp's causeway
    ]
    # Bridges across the channels: (one end, the other, half width), a deck on shallows. The main
    # bridges (20 m) to the centre, footbridges (8 m, half 4: narrow passes) where a
    # causeway crosses a channel.
    bridges = [
        ((-50.0, -20.0), (-26.0, -20.0), 10.0),                  # west hummock - centre
        ((-20.0, -50.0), (-20.0, -26.0), 10.0),                  # south hummock - centre
        ((8.0, -66.0), (28.0, -66.0), 4.0),                      # footbridge to the near objective
        ((-12.0, -102.0), (12.0, -102.0), 4.0),                  # footbridge on the camp's causeway
        ((-106.0, -2.0), (-106.0, 18.0), 4.0),                   # footbridge on the west detour
    ]
    return Archipelago(discs, causeways, bridges, camp_half=62.0)


SWAMP = swamp_layout()


def swamp(seed=193):
    """Swamp (jungle): hummocks of dry ground in brown swamp water, joined by raised causeways and
    short wooden bridges over the channels; the water is impassable, so every route is a chain of
    narrow ways. The biggest hummock holds the centre objective (a sunken temple); the side
    objectives are fishing villages on stilts on their own hummocks, reached from the camps by a
    causeway and a bridge each, and from the far camp by a long detour."""
    A = SWAMP
    west, east = (-62.0, 86.0), (62.0, -86.0)
    points = [(*west, 13.0), (0.0, 0.0, 16.0), (*east, 13.0)]
    L = world_layout(seed, points)

    # Roads: muddy tracks along the causeways and over the bridges.
    for pts, half in A.causeways:
        L.road(5, *[v for p in pts for v in p])
    for a, b, half in A.bridges:
        L.road(5, *a, *b)
    A.lay(L)

    # The sunken temple on the central hummock, its fallen gatehouse, broken walls. (16 m out, not 12:
    # 3 m apart on the diagonal, they left the hummock's crossing one cell wide; prompt 12.)
    L.add('temple_ruin', *diag(0, 16), 0, pad=0.5, road_gap=None, ignore_points=True, must=True)
    L.add('ruin', *diag(0, -16), 0, pad=0.5, road_gap=None, ignore_points=True, must=True)
    for sign in (1, -1):
        # (The pieces at (3, 11) and the stone wall at (10, 10) closed the hummock's crossing to a cell
        # or two between the temple and the ruin: the heavy hulls could not pass each other; prompt 12.)
        for x, z, kind, rot in ((-10, 10, 'wall', 0),):
            L.add(kind, sign * x, sign * z, rot, pad=0.4, road_gap=0.3, ignore_points=True)
        L.near('ruin', *diag(sign * -4, sign * 26), 4, 0, pad=0.6)
    # The stilt villages on the side objectives' hummocks, and huts on the others.
    for sign in (1, -1):
        px, pz = (east if sign > 0 else west)
        for dx, dz, rot in ((-14.0, 10.0, 0), (14.0, -10.0, 90), (-4.0, 20.0, 90), (6.0, -20.0, 0), (-20.0, -4.0, 0)):
            L.near('stilt_hut', px + sign * dx, pz + sign * dz, 4, rot, pad=0.8)
        L.near('watchtower', px + sign * 12.0, pz + sign * 12.0, 4, pad=0.6)
        L.scatter('barrel', px, pz, 4, 11, 5, pad=0.3)
        L.scatter('ammo_crate', px, pz, 4, 11, 3, pad=0.3)
        for x, z in ((-66.0, -22.0), (-22.0, -66.0), (-108.0, 30.0)):
            L.near('stilt_hut', sign * (x - 4.0), sign * (z + 4.0), 4, 0, pad=0.8)

    # The swamp forest: jungle trees and bamboo over the dry ground, reeds (ferns) at the edges.
    def species(x, z):
        return 'bamboo_clump' if A.depth(x, z) < 5.0 and L.rng.random() < 0.6 else L.rng.choice(
            ('jungle_tree_a', 'jungle_tree_b', 'jungle_tree_c', 'jungle_tree_a'))
    clearings = [(0, 0, 22), (*west, 18), (*east, 18)]
    mixed_woods(L, [(-150, -150), (150, -150), (150, 150), (-150, 150)], 0.012, species, clearings, edge=0)
    mixed_woods(L, [(-150, -150), (150, -150), (150, 150), (-150, 150)], 0.006, ('fern_bush',), clearings, edge=0, clumps=0.3)
    return finish(L)


def coral_layout():
    """Coral Isles' islands, causeways and bridges (one half; the other is its mirror image), laid
    square to the 4 m water grid like the swamp's (12 m causeways and main bridges, 8 m footbridges)."""
    discs = [(0.0, 0.0, 30.0), (62.0, -86.0, 26.0), (-70.0, -20.0, 14.0), (-20.0, -70.0, 14.0), (-112.0, 22.0, 12.0)]
    causeways = [
        ([(-56.0, -20.0), (-26.0, -20.0)], 6.0),                  # west islet - centre
        ([(-48.0, -68.0), (-34.0, -68.0)], 6.0),                  # camp - south islet
        ([(-8.0, -72.0), (8.0, -72.0)], 6.0),                     # south islet - bridge ...
        ([(24.0, -72.0), (44.0, -72.0)], 6.0),                    # ... - near island
        ([(-48.0, -108.0), (46.0, -108.0)], 6.0),                 # the long causeway: camp - near island
        ([(-112.0, -48.0), (-112.0, 8.0)], 6.0),                  # the west detour: camp - islet ...
        ([(-112.0, 50.0), (-112.0, 76.0), (-90.0, 76.0)], 6.0),   # ... - far island
        ([(-84.0, -20.0), (-104.0, -20.0)], 6.0),                 # west islet - the detour
        ([(-20.0, -84.0), (-20.0, -108.0)], 6.0),                 # south islet - the long causeway
    ]
    bridges = [
        ((-68.0, -48.0), (-68.0, -32.0), 6.0),                   # camp - west islet
        ((-20.0, -58.0), (-20.0, -28.0), 6.0),                   # south islet - centre
        ((6.0, -70.0), (26.0, -70.0), 4.0),                      # footbridge to the near island
        ((-110.0, 32.0), (-110.0, 52.0), 4.0),                   # footbridge on the west detour
    ]
    return Archipelago(discs, causeways, bridges, camp_half=60.0, beach=6.0, seed=5)


CORAL = coral_layout()


def coralisles(seed=197):
    """Coral Isles (desert): a chain of coral islands in a turquoise lagoon, joined by fixed stone
    causeways and bridges (no boats): the camps on the two big islands, the centre island with its
    lighthouse on the headland (the centre objective), a fishing village on the west and east
    islands (the side objectives), islets between. Sand beaches ring every island; palms, coral
    rock and huts on them."""
    A = CORAL
    west, east = (-62.0, 86.0), (62.0, -86.0)
    points = [(*west, 13.0), (0.0, 0.0, 15.0), (*east, 13.0)]
    L = world_layout(seed, points)
    for pts, half in A.causeways:
        L.road(5, *[v for p in pts for v in p])
    for a, b, half in A.bridges:
        L.road(5, *a, *b)
    A.lay(L)

    # The lighthouse on the centre island's north headland: the white tower, its lamp mast, the
    # keeper's cottage and a walled yard; an old coral-stone fort on the south headland.
    L.add('silo', -10.0, 20.0, 0, pad=0.4, road_gap=None, ignore_points=True, must=True)
    L.add('floodlight_mast', -6.5, 20.0, 0, pad=0.1, road_gap=None, ignore_points=True)
    L.near('cottage', -2.0, 27.0, 3, 0, pad=0.6)
    for x, z, rot in ((-19.0, 24.0, 90), (-14.0, 29.5, 0)):
        L.add('stone_wall', x, z, rot, pad=0.2, road_gap=0.5, ignore_points=True)
    L.near('ruin', 10.0, -21.0, 3, 0, pad=0.6)
    for x, z, rot in ((18.0, -24.0, 90), (4.0, -28.0, 0)):
        L.add('stone_wall', x, z, rot, pad=0.2, road_gap=0.5, ignore_points=True)
    for sign in (1, -1):
        L.add('sandbags', sign * 8.0, sign * -4.0, 90, pad=0.4, road_gap=0.3, ignore_points=True)
        # The fishing villages: huts round the landing, nets (camouflage nets), a watchtower.
        px, pz = (east if sign > 0 else west)
        for dx, dz, kind, rot in ((-14.0, 10.0, 'adobe_house', 0), (14.0, -10.0, 'adobe_house', 90), (-4.0, 20.0, 'stilt_hut', 90),
                                  (6.0, -20.0, 'stilt_hut', 0)):
            L.near(kind, px + sign * dx, pz + sign * dz, 4, rot, pad=0.8)
        L.near('camo_net', px - sign * 10.0, pz - sign * 6.0, 4, 0, pad=0.4)
        L.near('watchtower', px + sign * 14.0, pz + sign * 14.0, 4, pad=0.6)
        L.scatter('barrel', px, pz, 4, 11, 5, pad=0.3)
        L.scatter('ammo_crate', px, pz, 4, 11, 3, pad=0.3)

    # Palms and coral rock over the islands, thickest inland of the beaches.
    def species(x, z):
        return 'palm'
    clearings = [(0, 0, 20), (*west, 18), (*east, 18)]
    mixed_woods(L, [(-150, -150), (150, -150), (150, 150), (-150, 150)], 0.012, species, clearings, edge=0, road_gap=1.5)
    for sign in (1, -1):
        for x, z in ((-70.0, -20.0), (-20.0, -70.0), (-112.0, 22.0), (-128.0, -80.0), (-80.0, -128.0), (40.0, -100.0)):
            outcrop(L, sign * x, sign * z, 5, 2, pad=0.6)
    return finish(L)


MAPS_4M = [
    # id, builder, theme, point names (west, town, east), conquest comment, survival comment
    ('landingbeach', landingbeach, 'temperate', ('village', 'draw', 'beach'),
     'Landing Beach for Conquest: a beach under rock bluffs, four exits up to a coastal village on the plateau.',
     'Landing Beach for Survival: the same beach, holding out against waves from the north-east.'),
    ('hydrodam', hydrodam, 'temperate', ('power_station', 'bridge', 'ford'),
     'Hydro Dam for Conquest: a dammed river valley, crossed only on the dam crest, at the road bridge and over a ford.',
     'Hydro Dam for Survival: the same valley, holding out against waves from the north-east.'),
    ('capital', capital, 'urban', ('gardens', 'palace_square', 'station'),
     'Capital for Conquest: the government quarter on a river island, one bridge to each bank, dense blocks and boulevards.',
     'Capital for Survival: the same city, holding out against waves from the north-east.'),
    ('launchsite', launchsite, 'desert', ('assembly_building', 'launch_pad', 'propellant_farm'),
     'Silver Bug Launch Site for Conquest: a fenced launch complex, the pad at the centre, rail lines in from assembly and fuel.',
     'Silver Bug Launch Site for Survival: the same complex, holding out against waves from the north-east.'),
    ('saltflat', saltflat, 'desert', ('salt_works', 'survey_beacon', 'brine_pumps'),
     'Salt Flats for Conquest: open salt flats with long sight lines, a few rock clusters as stepping stones.',
     'Salt Flats for Survival: the same flats, holding out against waves from the north-east.'),
    ('borderbridge', borderbridge, 'temperate', ('border_village', 'great_bridge', 'customs_depot'),
     'Border Bridge for Conquest: a broad river crossed by the Great Bridge at the centre, a ford and an old bridge far out on the flanks.',
     'Border Bridge for Survival: the same river, holding out against waves from the north-east.'),
    ('swamp', swamp, 'jungle', ('west_village', 'sunken_temple', 'east_village'),
     'Swamp for Conquest: hummocks of dry ground joined by causeways and wooden bridges over impassable water.',
     'Swamp for Survival: the same swamp, holding out against waves from the north-east.'),
    ('coralisles', coralisles, 'desert', ('west_isle', 'lighthouse', 'east_isle'),
     'Coral Isles for Conquest: coral islands in a lagoon joined by causeways and bridges, a lighthouse on the centre island.',
     'Coral Isles for Survival: the same islands, holding out against waves from the north-east.'),
]

# The open flats keep their long sight lines: no tree clumps or hamlets, a few boulder heaps, a
# third of the wrecks and no pylon line.
WAR_4M = {
    'coralisles': dict(pylons=False, poles=False, dead_trees=6, where=lambda x, z: CORAL.depth(x, z) >= 12.0),
    # On the water maps nothing solid is dropped on a causeway, a bridge or a narrow shore.
    'swamp': dict(pylons=False, where=lambda x, z: SWAMP.depth(x, z) >= 12.0),
    'launchsite': dict(pylons=False),
    'landingbeach': dict(pylons=False, ditch=False),
    'saltflat': dict(pylons=False, wrecks=6, craters=10, dead_trees=8),
}
DENSIFY_4M = {
    # The islands grow palms and coral rock; fishing huts, not adobe towns.
    'coralisles': dict(trees=('palm',), houses=('stilt_hut', 'adobe_house'), yard=None, clumps=12, outcrops=4, hamlets=2,
                       where=lambda x, z: CORAL.depth(x, z) >= 12.0),
    # The swamp's hummocks are wooded by hand: a few more clumps, huts instead of hamlets.
    'swamp': dict(clumps=10, outcrops=4, hamlets=2, where=lambda x, z: SWAMP.depth(x, z) >= 12.0),
    # The launch complex is secret ground: no hamlets, only scrub and a few rocks.
    'launchsite': dict(clumps=10, outcrops=6, hamlets=0),
    # The capital is built block by block: no hamlets, a few tree clumps in the plazas.
    'capital': dict(clumps=6, hamlets=0),
    # The beach stays sand: trees and rock only on the plateau above the bluffs; the village is
    # built by hand, so no hamlets.
    'landingbeach': dict(clumps=24, outcrops=0, hamlets=0, where=lambda x, z: z > landing_bluff(x) + 16.0),
    'saltflat': dict(clumps=0, outcrops=4, hamlets=0),
}


# ------------------------------------------------------------------------ end of round 4M


# ------------------------------------------------------------------------ prompt 16: Lighthouse Bay
# The sea fills the south-east of the battlefield, beyond a coast running diagonally between the two
# camps (SW and NE), so both sides meet it alike: the map is symmetric by the reflection through the
# north-west to south-east diagonal, (x, z) -> (-z, -x), which swaps the camps. Everything here is
# laid out in the coast's own frame: u along the coast (south-west to north-east), w out to sea
# (towards the south-east corner), both in metres from the centre.
LB_R = math.sqrt(0.5)
LB_BASE = 34.0                 # the waterline along the cliffs by the camps
LB_COVE, LB_COVE_U, LB_COVE_W = 14.0, 62.0, 34.0     # the two coves: how far the beach is set back, where, how wide
LB_HEAD, LB_HEAD_W = 22.0, 22.0                        # the lighthouse headland on the axis: how far out, how wide
LB_SAND = (38.0, 96.0)         # |u| of the coves' sand beaches (the cliffs elsewhere)
LB_PIER_U, LB_PIER_HEAD = 48.0, 52.0                    # the piers: |u|, and w of their heads
LB_JETTY_HEAD = 55.0           # the headland's tip beside the lighthouse (the third place guns reach the near lane from)
# The sea lanes the ships run on (id, w, half the stretch they patrol): the near lane in reach of
# guns on the pier heads, the far lane only of artillery, aircraft and the coastal batteries.
LB_LANES = (('near', 92.0, 88.0), ('mid', 106.0, 82.0), ('far', 120.0, 76.0))
LB_LANDINGS = (72.0, 86.0)     # |u| of the beach points landing craft run up on
LB_BATTERY = (104.0, 16.0)     # the coastal batteries (|u|, w), on the cliff tops
LB_POINTS = (('west', 0.0, -104.0, 13.0), ('town', 0.0, -20.0, 15.0), ('east', 0.0, 38.0, 12.0))


def lb_uw(x, z):
    return (x + z) * LB_R, (x - z) * LB_R


def lb_xz(u, w):
    return round((u + w) * LB_R, 2), round((u - w) * LB_R, 2)


def lb_shore(u):
    """The waterline's w at u: the cliffs, set back into the two coves, out round the headland."""
    return (LB_BASE - LB_COVE * math.exp(-((abs(u) - LB_COVE_U) / LB_COVE_W) ** 2)
            + LB_HEAD * math.exp(-(u / LB_HEAD_W) ** 2))


def lb_sandy(u):
    return LB_SAND[0] <= abs(u) <= LB_SAND[1]


def lb_rot(rot):
    """A prop's rotation mirrored with its position (the footprint's axes swap)."""
    return (270 - rot) % 360


def lb_both(L, kind, u, w, rot=0, **kw):
    """A prop at (u, w) and its mirror image at (-u, w); returns how many went in."""
    x, z = lb_xz(u, w)
    placed = int(L.add(kind, x, z, rot, **kw))
    if abs(u) > 0.01:
        x, z = lb_xz(-u, w)
        placed += int(L.add(kind, x, z, lb_rot(rot), **kw))
    return placed


def lb_road(L, width, *uw):
    """A road through points given as (u, w) pairs, drawn on both halves (one road on the axis)."""
    pts = [lb_xz(uw[i], uw[i + 1]) for i in range(0, len(uw), 2)]
    L.road(width, *[v for p in pts for v in p])
    if any(abs(uw[i]) > 0.01 for i in range(0, len(uw), 2)):
        pts = [lb_xz(-uw[i], uw[i + 1]) for i in range(0, len(uw), 2)]
        L.road(width, *[v for p in pts for v in p])


def lb_sea_block():
    """The sea as the game needs it (map data "sea"): the coast's frame, its waterline, the lanes the
    ships run on, where landing craft beach, the pier heads, the coastal batteries, the lighthouse."""
    shore = [v for u in range(-212, 213, 4) for v in (float(u), round(lb_shore(u), 2))]   # u, w pairs
    lanes = [{'id': i, 'w': w, 'patrol': p, 'end': round(212.1 - w - 4.0, 1)} for i, w, p in LB_LANES]
    landings = []
    for s in (-1, 1):
        for u in LB_LANDINGS:
            uu = s * u
            beach = lb_shore(uu)
            landings.append({'x': lb_xz(uu, beach + 1.5)[0], 'z': lb_xz(uu, beach + 1.5)[1],
                             'inland': list(lb_xz(uu, beach - 9.0))})
    # x, z pairs; the last is the headland's tip.
    piers = [v for p in [lb_xz(s * LB_PIER_U, LB_PIER_HEAD) for s in (-1, 1)] + [lb_xz(0.0, LB_JETTY_HEAD)] for v in p]
    bu, bw = LB_BATTERY
    batteries = [{'id': 'battery_' + tag, 'x': lb_xz(s * bu, bw)[0], 'z': lb_xz(s * bu, bw)[1], 'heading': 135}
                 for tag, s in (('w', -1), ('e', 1))]
    return {'along': [round(LB_R, 5), round(LB_R, 5)], 'shore': shore, 'lanes': lanes, 'landings': landings, 'piers': piers,
            'batteries': batteries, 'lighthouse': 'east', 'lamp': list(lb_xz(0.0, 48.0)), 'airEntry': list(lb_xz(0.0, 205.0))}


def lb_open_sea(poly):
    """The outline on the sea side follows the square's edge: the sea runs on out of the battlefield
    (the ships sail in and out there), so no carved coast is left standing in the water."""
    out = []
    for x, z in poly:
        u, w = lb_uw(x, z)
        if w > lb_shore(u) + 10.0:
            if HALF - abs(x) < HALF - abs(z):
                x = math.copysign(HALF, x)
            else:
                z = math.copysign(HALF, z)
        out.append((x, z))
    return out


def lb_sea_tile(x, z):
    """The sea's tile at a 4 m cell's centre: deep water, surf on the cove beaches, or None (land)."""
    u, w = lb_uw(x, z)
    line = lb_shore(u)
    if w <= line:
        return None
    if lb_sandy(u) and w <= line + 6.0:
        return 'river_ford'
    return 'river_water'


def lb_refill_sea(L):
    """The classic fortress clears its ground and its approach lanes, sea and all: the sea comes back
    wherever nothing of the fortress stands (its walls run on into the water as harbour moles). A road
    of its that starts out at sea (the south gate's approach) starts at the waterline instead."""
    for road in L.roads:
        pts = road['points']
        while len(pts) >= 4 and lb_sea_tile(pts[0], pts[1]):
            ax, az, bx, bz = pts[0], pts[1], pts[2], pts[3]
            length = math.hypot(bx - ax, bz - az)
            if length <= 1.0:
                del pts[0:2]
                continue
            pts[0], pts[1] = ax + (bx - ax) / length, az + (bz - az) / length
    L.roads = [r for r in L.roads if len(r['points']) >= 4]
    L._samples = None
    # Wall and gate pieces the plan ran out onto the water go (the sea closes the line there).
    def at_sea(prop):
        if prop['def'] not in ('base_wall', 'base_gate', 'fortress_wall', 'fortress_gate'):
            return False
        if lb_sea_tile(prop['x'], prop['z']):
            return True
        if prop['def'] in ('base_gate', 'fortress_gate'):
            # A gate that opens onto the surf is no gate: the wall ends at the shore instead.
            dx, dz = (0.0, 6.0) if prop.get('rot', 0) % 180 == 0 else (6.0, 0.0)
            return bool(lb_sea_tile(prop['x'] + dx, prop['z'] + dz) or lb_sea_tile(prop['x'] - dx, prop['z'] - dz))
        return False
    keep = [(prop, rect) for prop, rect in zip(L.props, L.rects) if not at_sea(prop)]
    L.props, L.rects = [p for p, _ in keep], [r for _, r in keep]
    world_tiles(L, lb_sea_tile, road_gap=1.0, camp_gap=26.0, ignore_points=True)
    return L


def lb_near_both(L, kind, u, w, radius=6.0, rot=0, pad=0.8, road_gap=0.5, ignore_points=False, must=False):
    """A prop as near (u, w) as it fits, and its mirror image, both or neither (the halves stay equal)."""
    rng = L.rng
    for attempt in range(160):
        r = radius * math.sqrt(attempt / 160)
        a = rng.random() * math.tau
        uu, ww = u + math.cos(a) * r, w + math.sin(a) * r
        x, z = lb_xz(uu, ww)
        x, z = round(x * 2) / 2, round(z * 2) / 2
        mx, mz = -z, -x
        if not L.free(kind, x, z, rot, pad, road_gap, ignore_points):
            continue
        if abs(uu) < 0.5:
            L.add(kind, x, z, rot, pad=pad, road_gap=road_gap, ignore_points=ignore_points)
            return 1
        if not L.free(kind, mx, mz, lb_rot(rot), pad, road_gap, ignore_points):
            continue
        # Each must also leave room for the other (they could overlap on the axis).
        L.add(kind, x, z, rot, pad=pad, road_gap=road_gap, ignore_points=ignore_points)
        if L.add(kind, mx, mz, lb_rot(rot), pad=pad, road_gap=road_gap, ignore_points=ignore_points):
            return 2
        L.props.pop()
        L.rects.pop()
    if must:
        L.failed.append((kind, *lb_xz(u, w)))
    return 0


def lighthousebay(seed=199, siege=False):
    """Lighthouse Bay (temperate, prompt 16): the sea fills the south-east beyond a rocky coast. Two coves
    with long sand beaches (where landing craft run up) and a fishing pier each; between them the
    headland with the lighthouse and its jetty (the east objective: whoever holds it watches the sea);
    high cliffs by the camps with an abandoned coastal battery on each; a fishing village round the
    market at the centre; the old fort on the pine hill in the north-west (the west objective). Three
    sea lanes run along the coast at 70, 84 and 98 m off the cove beaches: guns on the pier heads and
    the jetty reach the near lane, artillery, aircraft and the batteries the far one. For the Siege
    version (`siege`) the north-east camp's coast is left bare: the classic fortress stands there."""
    points = [(*lb_xz(u, w), r) for _, u, w, r in LB_POINTS]
    tx, tz = lb_xz(0.0, -20.0)
    square = (tx - 12.0, tz - 12.0, tx + 12.0, tz + 12.0)
    L = world_layout(seed, points, clear=((-6, -6, 6, 6), square))

    # Roads: the coast road behind the beaches, the inland road through the village, a road up to
    # the old fort, one down the headland to the lighthouse and on onto its jetty, tracks to the
    # beaches, the batteries and the piers (the piers and the jetty are roads over the water: the
    # sea keeps off them, their decks are drawn on top). lb_road draws each off-axis road on both halves.
    lb_road(L, 6, -150.0, 2.0, -122.0, 8.0, -88.0, 4.0, -60.0, 0.0, -34.0, 10.0, 0.0, 18.0)
    lb_road(L, 6, -152.0, -8.0, -110.0, -40.0, -52.0, -34.0, -16.0, -22.0)
    lb_road(L, 5, 0.0, -36.0, 0.0, -70.0, 0.0, -92.0)
    lb_road(L, 5, 0.0, -6.0, 0.0, 18.0, 0.0, 32.0)
    lb_road(L, 7, -LB_PIER_U, lb_shore(LB_PIER_U) - 6.0, -LB_PIER_U, LB_PIER_HEAD)
    lb_road(L, 4, -72.0, 0.0, -74.0, 12.0)
    lb_road(L, 4, -104.0, 6.0, -104.0, 12.0)
    lb_road(L, 4, -30.0, -60.0, -60.0, -80.0, -96.0, -84.0)

    # The sea: deep water off the cliffs and the headland, two tiles of surf on the cove beaches.
    world_tiles(L, lb_sea_tile, road_gap=1.0, camp_gap=26.0, ignore_points=True)

    # The piers' and the jetty's decks, wooden on piles, over their roads.
    for sgn in (-1, 1):
        w = lb_shore(LB_PIER_U) - 2.0
        while w <= LB_PIER_HEAD + 0.1:
            x, z = lb_xz(sgn * LB_PIER_U, w)
            L.force('pier', x, z, 45)
            w += 5.6

    # The lighthouse on the headland (the east objective), its keeper's cottage, sandbag nests and a
    # pillbox either side at the neck.
    lx, lz = lb_xz(0.0, 48.0)
    L.add('lighthouse', lx, lz, 0, pad=0.4, road_gap=None, ignore_points=True, must=True)
    lb_near_both(L, 'cottage', 14.0, 24.0, 5.0, 0, pad=0.5, road_gap=0.4, ignore_points=True)
    lb_near_both(L, 'sandbags', 9.0, 38.0, 3.0, 45, pad=0.3, road_gap=0.3, ignore_points=True)
    lb_near_both(L, 'garage', 24.0, 2.0, 5.0, 0, pad=0.6, road_gap=0.5)

    # The cliffs: rock along the waterline by the camps and round the headland's flanks. Scree inland.
    def cliff_line(u0, u1, step=7.5, back=5.5):
        u = u0
        while u <= u1:
            w = lb_shore(u) - back
            kind = L.rng.choice(('cliff_b', 'cliff_a', 'boulders'))
            if siege and u > 60.0:
                x, z = lb_xz(-u, w)
                L.add(kind, x, z, lb_rot(0), pad=0.1, road_gap=1.0, ignore_points=True)
            else:
                lb_both(L, kind, u, w, L.rng.choice((0, 90)), pad=0.1, road_gap=1.0, ignore_points=True)
            u += step
    cliff_line(98.0, 150.0)
    cliff_line(21.0, 34.0, step=6.5, back=3.5)
    for u in range(100, 146, 9):
        if L.rng.random() < 0.6 and not siege:
            lb_both(L, 'boulders', float(u), lb_shore(u) - 14.0 - L.rng.uniform(0.0, 3.0), 0, pad=0.3, road_gap=1.0)

    # The coves: sand beaches with fishing boats drawn up and net racks, a hamlet behind each, wrecks
    # of an old landing in the surf, the coastal battery's emplacement on the cliff top beyond.
    for u in (58.0, 66.0, 80.0, 90.0):
        lb_near_both(L, 'fishing_boat', u, lb_shore(u) - 8.0, 3.0, L.rng.choice((0, 90)), pad=0.6, road_gap=0.6)
    for u in (62.0, 76.0, 84.0):
        lb_near_both(L, 'fence', u, lb_shore(u) - 14.0, 3.0, 0, pad=0.3, road_gap=0.6)
    for u, w, kind, rot in ((56.0, -14.0, 'cottage', 0), (70.0, -18.0, 'house_small', 90), (84.0, -12.0, 'cottage', 90),
                            (66.0, -26.0, 'barn', 0), (96.0, -18.0, 'shop', 0), (46.0, -16.0, 'stilt_hut', 0)):
        lb_near_both(L, kind, u, w, 7.0, rot, pad=0.8, road_gap=0.5)
    for kind, u, off, rot in (('wreck_tank', 70.0, 3.0, 45), ('wreck_truck', 88.0, 4.0, 0)):
        lb_both(L, kind, u, lb_shore(u) + off, rot, pad=0.8, road_gap=None)
    bu, bw = LB_BATTERY
    for du, dw, kind, rot in ((-7.0, -3.0, 'sandbags', 45), (7.0, -3.0, 'sandbags', 45), (-9.0, 4.0, 'ammo_crate', 0),
                              (9.0, 4.0, 'ammo_crate', 0)):
        lb_near_both(L, kind, bu + du, bw + dw, 2.5, rot, pad=0.3, road_gap=0.3)

    # The fishing village round the market square at the centre (the town objective).
    for du, dw, kind, rot in ((-28.0, -6.0, 'townhouse', 0), (-26.0, -30.0, 'house_small', 0), (-22.0, 14.0, 'cottage', 90),
                              (-40.0, -18.0, 'shop', 0), (-14.0, -42.0, 'house_small', 90), (-44.0, 4.0, 'cottage', 0)):
        lb_near_both(L, kind, du, -20.0 + dw, 6.0, rot, pad=0.6, road_gap=0.4)
    for du, dw in ((-14.0, 6.0), (-16.0, -12.0), (-6.0, -18.0)):
        lb_near_both(L, 'market_stall', du, -20.0 + dw, 4.0, 0, pad=0.5, road_gap=0.3, ignore_points=True)

    # The old fort on the pine hill (the west objective): casemates round a ruined tower, sandbag
    # nests and a trench; the pines all round it.
    for du, dw, kind, rot in ((-16.0, -8.0, 'garage', 0), (-12.0, 12.0, 'garage', 90), (-8.0, 4.0, 'sandbags', 45),
                              (-6.0, -18.0, 'ruin_tower', 0), (-10.0, 20.0, 'trench_straight', 45)):
        lb_near_both(L, kind, du, -104.0 + dw, 4.0, rot, pad=0.5, road_gap=0.4, ignore_points=True)
    lb_near_both(L, 'watchtower', 24.0, -96.0, 5.0, 0, pad=0.6)

    # Pine woods inland, thickest in the north-west round the fort; tree lines along the fields.
    for u, w, r, d in ((-40.0, -120.0, 16.0, 0.12), (-70.0, -100.0, 14.0, 0.11), (-30.0, -150.0, 12.0, 0.12),
                       (-110.0, -80.0, 12.0, 0.1), (-60.0, -140.0, 10.0, 0.1), (-130.0, -44.0, 8.0, 0.1)):
        for sgn in (-1, 1):
            x, z = lb_xz(sgn * u, w)
            L.forest(x, z, r, d)
    for u0, w0, u1, w1 in ((-120.0, -18.0, -84.0, -18.0), (-84.0, -18.0, -84.0, -56.0), (-50.0, -50.0, -24.0, -50.0)):
        for sgn in (-1, 1):
            ax, az = lb_xz(sgn * u0, w0)
            bx, bz = lb_xz(sgn * u1, w1)
            L.tree_line(ax, az, bx, bz, spacing=4.5)
    return finish(L)


MAPS_P16 = [
    ('lighthousebay', lighthousebay, 'temperate', ('old_fort', 'fishing_village', 'lighthouse'),
     'Lighthouse Bay for Conquest: a rocky coast on the sea, two coves with beaches and piers, the lighthouse on the headland between them.',
     'Lighthouse Bay for Survival: the same coast, holding out against waves from the north-east.'),
]
WAR_P16 = {
    # Nothing solid is dropped on the beaches, the headland or the cliff edge (the sea's side).
    'lighthousebay': dict(pylons=False, ditch=False, where=lambda x, z: lb_uw(x, z)[1] < lb_shore(lb_uw(x, z)[0]) - 18.0),
}
DENSIFY_P16 = {
    'lighthousebay': dict(clumps=16, outcrops=4, hamlets=1, where=lambda x, z: lb_uw(x, z)[1] < lb_shore(lb_uw(x, z)[0]) - 22.0),
}


# ------------------------------------------------------------------------ prompt 20 M: Open-Pit Mine, Orbital Gateway
# A fixed route (map data "routes": {name: [x0, z0, x1, z1, ...]}) is the road a very slow, very large
# boss drives every time (the open-pit mine's bucket-wheel excavator, "kronos"). It is laid as a
# ROUTE_ROAD haul road, and the ground ROUTE_HALF either side of it stays open all along: the nav
# cells under it (sampled every ROUTE_STEP metres along, every half metre across) are kept free of
# anything solid by the builder (clear_route), the map kit and the fill (warzone, densify), and main
# checks them on the finished Conquest and Survival battlefield (check_route). The camps' hardpoints
# may stand on it: the boss crushes towers and walls.
ROUTE_HALF = 7.0
ROUTE_STEP = 2.0
ROUTE_ROAD = 14.0
FIXED_ROUTES = {}     # map id -> {route name: [(x, z), ...]}


def route_meta(map_id):
    """A map's fixed routes (prompt 20 M), for every version of it: flat x, z pairs in metres."""
    routes = FIXED_ROUTES.get(map_id)
    if not routes:
        return {}
    return {'routes': {name: [round(v, 2) for p in pts for v in p] for name, pts in routes.items()}}


@functools.lru_cache(maxsize=None)
def route_cells(map_id):
    """The nav cells (the square's 2 m grid) a map's fixed routes keep open: every cell under a
    point up to ROUTE_HALF either side of the route, sampled every ROUTE_STEP metres along it."""
    cells = set()
    for pts in FIXED_ROUTES.get(map_id, {}).values():
        for (ax, az), (bx, bz) in zip(pts, pts[1:]):
            length = math.hypot(bx - ax, bz - az)
            ux, uz = (bx - ax) / length, (bz - az) / length
            steps = max(1, int(math.ceil(length / ROUTE_STEP)))
            for k in range(steps + 1):
                x, z = ax + ux * length * k / steps, az + uz * length * k / steps
                for j in range(-int(ROUTE_HALF * 2), int(ROUTE_HALF * 2) + 1):
                    off = j * 0.5
                    cells.add((int(math.floor((x - uz * off + HALF) / CELL)), int(math.floor((z + ux * off + HALF) / CELL))))
    return frozenset(cells)


def on_route(map_id, x0, z0, x1, z1):
    """Whether a blocking footprint, grown by the obstacle clearance as NavGrid fills it, would close
    a cell of one of the map's fixed routes."""
    cells = route_cells(map_id)
    if not cells:
        return False
    a0 = int(math.floor((x0 - CLEARANCE + HALF) / CELL))
    a1 = int(math.floor((x1 + CLEARANCE - 1e-4 + HALF) / CELL))
    b0 = int(math.floor((z0 - CLEARANCE + HALF) / CELL))
    b1 = int(math.floor((z1 + CLEARANCE - 1e-4 + HALF) / CELL))
    return any((gx, gz) in cells for gx in range(a0, a1 + 1) for gz in range(b0, b1 + 1))


def clear_route(L, map_id):
    """Takes every blocking prop off a map's fixed routes (the ramps through the pit's rock rings
    open to the route's full width). Returns how many went."""
    keep = [(p, r) for p, r in zip(L.props, L.rects) if not (PROPS[p['def']].get('blocks', False) and on_route(map_id, *r))]
    removed = len(L.props) - len(keep)
    L.props, L.rects = [p for p, _ in keep], [r for _, r in keep]
    return removed


def check_route(L, map_id, what):
    """Stops the build unless every cell of the map's fixed routes is open ground (props, the
    outline) on a finished battlefield."""
    if not FIXED_ROUTES.get(map_id):
        return
    blocked = L.blocked_grid(units=False)
    n, nz = L.grid_n(), L.grid_nz()
    cells = route_cells(map_id)
    shut = sorted(c for c in cells if not (0 <= c[0] < n and 0 <= c[1] < nz) or blocked[c[1]][c[0]])
    if shut:
        spots = [(gx * CELL - HALF + 1, gz * CELL - HALF + 1) for gx, gz in shut[:4]]
        raise SystemExit(f'{what}: a fixed route is closed within {ROUTE_HALF:g} m of it at {len(shut)} cells, e.g. {spots}')
    for name, pts in FIXED_ROUTES[map_id].items():
        length = sum(math.hypot(bx - ax, bz - az) for (ax, az), (bx, bz) in zip(pts, pts[1:]))
        print(f'{what}: route {name} ({len(pts)} points, {length:.0f} m) open {ROUTE_HALF:g} m either side '
              f'({len(cells)} cells checked every {ROUTE_STEP:g} m)')


def polar(r, degrees):
    """World x, z of a point `r` metres from the centre at `degrees` anticlockwise from east."""
    a = math.radians(degrees)
    return r * math.cos(a), r * math.sin(a)


PIT_RINGS = (25.0, 48.0, 88.0)     # the pit's rock rings (radius of each): the floor's edge, the middle bench's, the rim
PIT_BENCH = 68.0                   # the haul road's radius round the upper bench
# The ramps through each ring besides the roads' (degrees, and each has its image at +180; the
# opening in metres): the main cut down the camps' axis from the upper bench to the floor, and a
# narrower ramp through the middle bench and the rim further round.
PIT_RAMPS = {PIT_RINGS[0]: ((45.0, 24.0),), PIT_RINGS[1]: ((45.0, 24.0), (100.0, 14.0)), PIT_RINGS[2]: ((70.0, 14.0),)}
# The excavator's road, from the north-east camp's road end down round the upper bench, straight
# over the pit floor and up the far side (the same road mirrored) to the south-west camp's road end,
# then on to just outside the player's HQ (12 m behind the rally).
_KRONOS_NE = [(96.0, 96.0), polar(104.0, 30.0), polar(PIT_BENCH, 5.0), polar(PIT_BENCH, -15.0), polar(PIT_BENCH, -35.0)]
KRONOS = [(round(x, 2), round(z, 2)) for x, z in
          _KRONOS_NE + [(0.0, 0.0)] + [mirror(*p) for p in reversed(_KRONOS_NE)] + [(-104.0, -104.0)]]
FIXED_ROUTES['openpit'] = {'kronos': KRONOS}


def mirrored(L, kind, x, z, rot=0, radius=0.0, pad=1.0, road_gap=0.8, ignore_points=False, must=False):
    """A prop and its image through the centre, both or neither, so either camp's half is the same
    ground: at (x, z), or with `radius` at the nearest spot within it (a 1 m lattice, nearest first)
    where both fit. Returns whether they went in."""
    spots = [(0, 0)]
    if radius:
        n = int(radius)
        spots += sorted(((dx, dz) for dx in range(-n, n + 1) for dz in range(-n, n + 1) if 0 < math.hypot(dx, dz) <= radius),
                        key=lambda d: (math.hypot(*d), d))
    for dx, dz in spots:
        ax, az = round((x + dx) * 2) / 2, round((z + dz) * 2) / 2
        if not (L.free(kind, ax, az, rot, pad, road_gap, ignore_points) and L.free(kind, -ax, -az, rot, pad, road_gap, ignore_points)):
            continue
        L.add(kind, ax, az, rot, pad=pad, road_gap=road_gap, ignore_points=ignore_points)
        if L.add(kind, -ax, -az, rot, pad=pad, road_gap=road_gap, ignore_points=ignore_points):
            return True
        L.props.pop()   # the two copies overlap each other (only by the centre): try the next spot
        L.rects.pop()
    if must:
        L.failed.append((kind, x, z))
    return False


def mirror_new(L, since, pad=0.1, road_gap=1.0):
    """Gives every prop placed since index `since` its image through the centre; one whose image does
    not fit goes too, so the two halves stay the same ground. Returns pairs kept."""
    new = list(zip(L.props[since:], L.rects[since:]))
    L.props, L.rects = L.props[:since], L.rects[:since]
    kept = 0
    for prop, _ in new:
        rot = prop.get('rot', 0)
        if L.free(prop['def'], -prop['x'], -prop['z'], rot, pad, road_gap):
            L.force(prop['def'], prop['x'], prop['z'], rot)
            L.force(prop['def'], -prop['x'], -prop['z'], rot)
            kept += 1
    return kept


def pit_ring(L, radius, ramps):
    """One of the pit's benches: a broken ring of cliff round the centre, opened for `ramps`
    ((degrees, opening in metres), each with its image through the centre), with scree tumbled down
    its inner foot. Each arc is laid on one half and mirrored onto the other; a road through it opens
    its own gap."""
    gaps = sorted([(a % 360.0, math.degrees(w / 2 / radius)) for a, w in ramps] +
                  [((a + 180.0) % 360.0, math.degrees(w / 2 / radius)) for a, w in ramps])
    arcs = [(gaps[i][0] + gaps[i][1], gaps[(i + 1) % len(gaps)][0] - gaps[(i + 1) % len(gaps)][1] + (360.0 if i == len(gaps) - 1 else 0.0))
            for i in range(len(gaps))]
    for a0, a1 in arcs[:len(arcs) // 2]:
        steps = max(2, int(math.ceil((a1 - a0) / 5.0)))
        since = len(L.props)
        rock_chain(L, [polar(radius, a0 + (a1 - a0) * k / steps) for k in range(steps + 1)], kinds=('cliff_a', 'cliff_b'),
                   gap=0.5, jitter=1.0, pad=0.3, road_gap=1.0)
        mirror_new(L, since)
    for k in range(0, 180, 9):
        if L.rng.random() < 0.4:
            mirrored(L, 'boulders', *polar(radius - 8.0 - L.rng.uniform(0.0, 1.5), float(k)), L.rng.choice((0, 90)), pad=0.3,
                     road_gap=1.0)


def openpit(seed=211):
    """Open-Pit Mine (desert, prompt 20 M): the terraced pit at the centre, three broken rings of rock
    stepping down to its floor (the town objective), with ramps through each ring. The excavator's
    14 m haul road winds down round the upper bench from the north-east, crosses the floor and climbs
    out the same way to the south-west (the fixed route "kronos"); a haul road runs from each bench
    turn out to the crusher plant on the north-west rim (the west objective) or the ore loadout on
    the south-east one (the east objective): factories, silos, storage tanks, a gantry over the
    conveyors, ore heaps. Spoil roads lead off the rim to the spoil heaps on the flanks, where the
    flank roads run from each camp to the far plant; the service roads pass the truck depots (garages
    and parked haul trucks) to the near one. The same ground on either half, mirrored."""
    west, east = (-80.0, 80.0), (80.0, -80.0)
    points = [(*west, 13.0), (0.0, 0.0, 16.0), (*east, 13.0)]
    L = world_layout(seed, points, clear=((-6, -6, 6, 6),))

    def at(sign, x, z):
        return sign * x, sign * z

    # Roads: the excavator's haul road first (everything else keeps off it), each camp's road onto it,
    # then per half (drawn for the north-east camp and the east plant, mirrored): the plant's haul
    # road off the bench, the spoil road, the flank road and the service road.
    L.road(ROUTE_ROAD, *[v for p in KRONOS[:-1] for v in p])
    bench_turn = polar(PIT_BENCH, -35.0)
    rim_turn = polar(104.0, 30.0)
    for sign in (1, -1):
        L.road(8, *at(sign, *CAMP_1), *at(sign, 96.0, 96.0))
        L.road(12, *at(sign, *bench_turn), *at(sign, 70.0, -58.0), *at(sign, *east))
        L.road(10, *at(sign, *rim_turn), *at(sign, 108.0, 38.0), *at(sign, 124.0, 24.0))
        L.road(8, *at(sign, 112.0, 72.0), *at(sign, 124.0, 24.0), *at(sign, 122.0, -24.0), *at(sign, 110.0, -50.0),
               *at(sign, *east))
        L.road(8, *at(sign, 72.0, 112.0), *at(sign, 20.0, 108.0), *at(sign, -40.0, 104.0), *at(sign, *west))

    # The pit: the rim, the middle bench and the floor's edge, each a broken ring of cliff.
    for radius in PIT_RINGS:
        pit_ring(L, radius, PIT_RAMPS[radius])

    # On the benches: ore heaps and parked haul trucks, away from the haul road.
    for r, a in ((PIT_BENCH, 45.0), (PIT_BENCH, 60.0), (PIT_BENCH, 78.0), (PIT_BENCH, -62.0), (36.5, 10.0), (36.5, 78.0),
                 (36.5, -85.0)):
        mirrored(L, 'dirt_mound', *polar(r, a), 0 if abs(math.cos(math.radians(a))) < 0.7 else 90, radius=3.0, pad=0.5,
                 road_gap=1.0)
    for r, a, rot in ((PIT_BENCH, 52.0, 90), (PIT_BENCH, 86.0, 0), (PIT_BENCH, -70.0, 0), (12.0, 70.0, 90)):
        mirrored(L, 'truck', *polar(r, a), rot, radius=3.0, pad=0.6, road_gap=0.8, ignore_points=True)

    # The plants on the rim: the crusher house (a factory) beyond the objective, the gantry over the
    # conveyors, the silos, storage tanks and the ore stockpile; the same buildings at either plant.
    px, pz = east
    mirrored(L, 'factory', 102.0, -102.0, 0, radius=5.0, pad=0.8, must=True)
    mirrored(L, 'gantry_crane', 80.0, -106.0, 0, radius=4.0, pad=0.8, must=True)
    for x, z in ((58.0, -112.0), (64.0, -112.0), (58.0, -118.0), (64.0, -118.0)):
        mirrored(L, 'silo', x, z, 0, pad=0.4, road_gap=0.8)
    for x, z in ((110.0, -84.0), (110.0, -72.0)):
        mirrored(L, 'storage_tank', x, z, 0, radius=4.0, pad=0.8)
    for x0, z0, x1, z1 in ((70.0, -116.0, 100.0, -116.0), (120.0, -100.0, 120.0, -66.0)):
        since = len(L.props)
        lines_of(L, 'pipeline', x0, z0, x1, z1, 2.0, pad=0.3)
        mirror_new(L, since, pad=0.3, road_gap=0.5)
    for dx, dz in ((16.0, 12.0), (20.0, 4.0), (8.0, -16.0), (26.0, -26.0), (-4.0, -20.0)):
        mirrored(L, 'dirt_mound', px + dx, pz + dz, 90 if dx > 10 else 0, radius=2.0, pad=0.4, road_gap=0.6, ignore_points=True)
    mirrored(L, 'sandbags', px - 12.0, pz + 6.0, 90, radius=3.0, pad=0.4, road_gap=0.5, ignore_points=True)
    for sign in (1, -1):
        L.scatter('barrel', *at(sign, px, pz), 3, 10, 5, pad=0.3)

    # The spoil heaps on the flanks, between the rim and the flank road; a few boulders among them.
    for x, z in ((100.0, -30.0), (108.0, -22.0), (100.0, -12.0), (110.0, -6.0), (102.0, 4.0), (112.0, -38.0), (98.0, 16.0)):
        mirrored(L, 'dirt_mound', x, z, L.rng.choice((0, 90)), radius=2.0, pad=0.5, road_gap=1.0)
    for x, z in ((104.0, -46.0), (96.0, 26.0)):
        mirrored(L, 'boulders', x, z, 0, radius=3.0, pad=0.6, road_gap=1.0)

    # The truck depots by the service roads: garages, parked haul trucks and a fuel tank.
    for x in (10.0, 22.0, 34.0):
        mirrored(L, 'garage', x, 120.0, 0, radius=2.0, pad=0.6, road_gap=0.8)
    for x in (46.0, 50.0, 54.0):
        mirrored(L, 'truck', x, 121.0, 90, radius=2.0, pad=0.4, road_gap=0.8)
    mirrored(L, 'fuel_tank', -2.0, 120.0, 0, radius=2.0, pad=0.6, road_gap=0.8)

    # The desert round the mine: a few rock formations and cactus scrub.
    for sign in (1, -1):
        for kind, x, z in (('mesa', 128.0, -128.0), ('cliff_b', 60.0, 132.0), ('cliff_b', 134.0, 50.0)):
            formation(L, *at(sign, x, z), kind, 8, 3)
        for x, z in ((-20.0, 128.0), (130.0, -8.0)):
            L.forest(*at(sign, x, z), 7.0, 0.1, kind='cactus')

    # The excavator's road is open to its full width: the ramps through the rings with it.
    clear_route(L, 'openpit')
    return finish(L)


ORBIT_FIELD = 30.0    # the drop-pod field: 60 x 60 m at the centre, clear of everything solid


def orbitalgate(seed=223):
    """Orbital Gateway (snow, prompt 20 M): a spaceport on a snowy plateau. At the centre the drop-pod
    field (the town objective), 60 x 60 m of open ground with floodlight masts and runway lights round
    its edge and an apron road round it; a launch pad on either flank (the west and east objectives,
    mirrored): the rocket (a tall stack) between two gantries, flame trenches, propellant tanks,
    blockhouses and sandbag walls round the apron. A radar post astride each camp's road to the field:
    a radar dome, radar stations, radio masts and the tracking office. Flank roads run from each camp
    to the far pad, the outer roads to the near one; pine woods and snow rock between."""
    points = [(-80.0, 80.0, 13.0), (0.0, 0.0, 16.0), (80.0, -80.0, 13.0)]
    f = ORBIT_FIELD
    L = world_layout(seed, points, clear=((-f, -f, f, f),))

    def at(sign, x, z):
        return sign * x, sign * z

    # Roads: the apron road round the field, then per half (drawn for the north-east camp and the
    # south-east pad, mirrored): the camp's road to the field, the pad's road off the apron, the flank
    # road down the east edge to the pad and the outer road along the north edge to the far one.
    e = f + 8.0
    L.road(6, -e, -e, e, -e, e, e, -e, e, -e, -e)
    for sign in (1, -1):
        L.road(8, *at(sign, *CAMP_1), *at(sign, 70.0, 70.0), *at(sign, e, e))
        L.road(8, *at(sign, e, -e), *at(sign, 62.0, -62.0), *at(sign, 80.0, -80.0))
        L.road(8, *at(sign, 112.0, 72.0), *at(sign, 126.0, 10.0), *at(sign, 118.0, -44.0), *at(sign, 80.0, -80.0))
        L.road(8, *at(sign, 72.0, 112.0), *at(sign, 10.0, 126.0), *at(sign, -44.0, 118.0), *at(sign, -80.0, 80.0))

    # The field's edge: runway lights all round, floodlight masts off the corners' roads.
    edge = f + 1.5
    for u in range(-27, 28, 6):
        for x, z in ((u, -edge), (u, edge), (-edge, u), (edge, u)):
            L.add('runway_light', float(x), float(z), 0, pad=0.2, road_gap=0.3, ignore_points=True)
    for u in (-15.0, 15.0):
        for x, z in ((u, -f - 3.0), (u, f + 3.0), (-f - 3.0, u), (f + 3.0, u)):
            L.add('floodlight_mast', x, z, 0, pad=0.3, road_gap=0.5, ignore_points=True, must=True)

    # The launch pads: the rocket on its stand beyond the objective, a gantry either side, a flame
    # trench before and behind it, the propellant tanks, blockhouses and sandbag walls round the apron.
    mirrored(L, 'refinery_tower', 100.0, -100.0, 0, pad=0.3, road_gap=None, ignore_points=True, must=True)
    for x in (91.0, 109.0):
        mirrored(L, 'gantry_crane', x, -100.0, 90, pad=0.3, road_gap=None, ignore_points=True, must=True)
    for z in (-91.5, -108.5):
        mirrored(L, 'tank_ditch', 100.0, z, 0, pad=0.2, road_gap=None, ignore_points=True)
    for x, z in ((124.0, -94.0), (124.0, -106.0)):
        mirrored(L, 'storage_tank', x, z, 0, radius=4.0, pad=0.8)
    for x in (98.0, 104.0, 110.0):
        mirrored(L, 'fuel_tank', x, -122.0, 0, radius=2.0, pad=0.6, road_gap=0.5)
    mirrored(L, 'garage', 70.0, -106.0, 0, radius=4.0, pad=0.8)
    mirrored(L, 'garage', 106.0, -70.0, 90, radius=4.0, pad=0.8)
    for x, z, rot in ((64.0, -96.0, 0), (96.0, -64.0, 90), (86.0, -118.0, 0), (118.0, -84.0, 90)):
        mirrored(L, 'sandbag_wall', x, z, rot, radius=2.0, pad=0.4, road_gap=0.5, ignore_points=True)
    for x, z in ((114.0, -114.0), (86.0, -86.0)):
        mirrored(L, 'floodlight_mast', x, z, 0, radius=2.0, pad=0.3, road_gap=0.5, ignore_points=True)
    for sign in (1, -1):
        L.scatter('barrel', *at(sign, 80.0, -80.0), 4, 11, 5, pad=0.3)

    # The radar posts astride each camp's road to the field (diagonal frame: s along the road).
    for kind, s, t in (('radar_dome', 84.0, 20.0), ('radar_station', 72.0, -20.0), ('radar_station', 96.0, -19.0),
                       ('office_block', 102.0, 24.0), ('log_cabin', 64.0, 26.0)):
        mirrored(L, kind, *diag(s, t), 0, radius=5.0, pad=0.8, must=True)
    for s, t in ((80.0, -31.0), (92.0, 31.0), (66.0, -12.0)):
        mirrored(L, 'radio_mast', *diag(s, t), 0, radius=2.0, pad=0.4, road_gap=0.8)
    mirrored(L, 'sandbags', *diag(60.0, 12.0), 0, radius=2.0, pad=0.4, road_gap=0.5)

    # Pine woods and snow rock between the lanes.
    for sign in (1, -1):
        for x, z, r in ((100.0, 20.0, 13.0), (20.0, 100.0, 13.0), (64.0, -12.0, 8.0), (-12.0, 64.0, 8.0), (136.0, -30.0, 8.0),
                        (-30.0, 136.0, 8.0)):
            L.forest(*at(sign, x, z), r, 0.12)
        for x, z in ((52.0, 100.0), (100.0, 50.0), (140.0, 60.0)):
            outcrop(L, *at(sign, x, z), 5, 3, kinds=('snow_rock',), pad=0.6)
    return finish(L)


MAPS_P20 = [
    ('openpit', openpit, 'desert', ('crusher_plant', 'pit_floor', 'ore_loadout'),
     'Open-Pit Mine for Conquest: a terraced pit of broken rock rings, haul roads down to its floor, a crusher plant and an ore loadout on the rim.',
     'Open-Pit Mine for Survival: the same mine, holding out against waves from the north-east.'),
    ('orbitalgate', orbitalgate, 'snow', ('west_pad', 'landing_field', 'east_pad'),
     'Orbital Gateway for Conquest: a snowbound spaceport, a launch pad on either flank, radar posts on the approaches, a drop-pod field at the centre.',
     'Orbital Gateway for Survival: the same spaceport, holding out against waves from the north-east.'),
]
WAR_P20 = {
    # No pylon line across the pit's benches.
    'openpit': dict(pylons=False),
    'orbitalgate': dict(pylons=False),
}
DENSIFY_P20 = {
    # Scrub and rock round the mine, nothing on the benches; no hamlets (the depots are the mine's buildings).
    'openpit': dict(clumps=8, outcrops=6, hamlets=0, where=lambda x, z: math.hypot(x, z) > PIT_RINGS[2] + 8.0),
    # Woods and crew cabins, never on the field.
    'orbitalgate': dict(hamlets=2, where=lambda x, z: max(abs(x), abs(z)) > ORBIT_FIELD + 12.0),
}


# ------------------------------------------------------------------------ prompt 22 E: two new battlefields
# Foundry and Veyra Old Quarter (DECISIONS 22E): both on the battlefield itself (world_layout), point-symmetric
# through the centre like every square map, their names only in the game's tables (NameText, Strings).
P22_LANES = (-112.0, -48.0, -16.0, 16.0, 48.0, 112.0)   # the Foundry's lanes, each way
P22_LANE = 10.0                                        # a lane's width: 8.6 m of drivable floor between the buildings
FOUNDRY_HALL = (-40.0, -32.0, 40.0, 32.0)              # the casting hall's walls (centrelines)
FOUNDRY_SHOP = (-105.5, 54.5, -54.5, 105.5)              # the press shop's walls; the rolling mill is its image


def p22_walls(L, x0, z0, x1, z1, doors=(), kind='wall', skip_roads=True):
    """Walls round a rectangle (centrelines x0..x1, z0..z1), segment by segment. A segment is left out where
    a lane runs through the wall (skip_roads: the lanes are the hall's doorways) or where it overlaps a door:
    ('n'|'s'|'w'|'e', centre along the wall, opening in metres). Returns segments placed."""
    w = PROPS[kind]['width']
    placed = 0
    for side, line, a, b, axis in (('s', z0, x0, x1, 'x'), ('n', z1, x0, x1, 'x'), ('w', x0, z0, z1, 'z'), ('e', x1, z0, z1, 'z')):
        n = int((b - a + 1e-6) // w)
        u = a + (b - a - n * w) / 2      # the odd metres split between the two corners (sealed by the clearance)
        for _ in range(n):
            c = u + w / 2
            u += w
            if any(s == side and abs(c - m) < (o + w) / 2 for s, m, o in doors):
                continue
            x, z, rot = (c, line, 0) if axis == 'x' else (line, c, 90)
            ww, dd = Layout.size(kind, rot)
            rect = (x - ww / 2, z - dd / 2, x + ww / 2, z + dd / 2)
            if skip_roads and L.near_road(*rect, 1.0):
                continue
            L.force(kind, x, z, rot)
            placed += 1
    return placed


def p22_minus(rect, holes, margin=1.5, least=8.0):
    """What is left of a rectangle once `holes` (grown by `margin`) are cut out: rectangles at least `least` m
    each way (a block partly inside a hall is built only outside it)."""
    pieces = [rect]
    for hx0, hz0, hx1, hz1 in holes:
        hx0, hz0, hx1, hz1 = hx0 - margin, hz0 - margin, hx1 + margin, hz1 + margin
        out = []
        for x0, z0, x1, z1 in pieces:
            if hx1 <= x0 or hx0 >= x1 or hz1 <= z0 or hz0 >= z1:
                out.append((x0, z0, x1, z1))
                continue
            out += [(x0, z0, hx0, z1), (hx1, z0, x1, z1), (max(x0, hx0), z0, min(x1, hx1), hz0), (max(x0, hx0), hz1, min(x1, hx1), z1)]
        pieces = [p for p in out if p[2] - p[0] >= least and p[3] - p[1] >= least]
    return pieces


def p22_blocks(lanes, half=HALF - 4.0, lane=P22_LANE):
    """The blocks between a lane grid's lanes (and the edge), inside the lanes' edges."""
    edges = [-half] + [v for c in lanes for v in (c - lane / 2, c + lane / 2)] + [half]
    spans = [(edges[i], edges[i + 1]) for i in range(0, len(edges), 2)]
    return [(x0, z0, x1, z1) for x0, x1 in spans for z0, z1 in spans]


def foundry(seed=233, siege=False):
    """Foundry (urban, prompt 22 E.1): Hegemon's old tank works, a walled complex of workshops and sheds
    under one roofline, cut by 10 m factory lanes into solid blocks: every way across is a narrow passage
    between walls. The casting hall at the centre (the town objective): its walls opened only where the
    lanes run in, two furnaces, the ladles, a conveyor and a gantry over the casting floor. The press shop
    in the north-west block (the west objective) and the rolling mill in the south-east one (the east
    objective, its image): walled yards with one doorway a side, a gantry crane, presses and coil stacks.
    Each camp has an open loading yard round it (the works' goods yard); the blocks are factories,
    warehouses, sheds, container stacks, tanks and silos, pipe runs over the yards. The same ground on
    either half, mirrored. The Siege version (siege=True) leaves the fortress's ground open: no hall walls,
    nothing built in the blocks beyond the first lanes in the north-east (the fortress builds its own)."""
    west, east = (-80.0, 80.0), (80.0, -80.0)
    points = [(*west, 13.0), (0.0, 0.0, 16.0), (*east, 13.0)]
    L = world_layout(seed, points, clear=((-15.0, -15.0, 15.0, 15.0),))
    p22_lanes(L, P22_LANES)

    # The casting hall's walls, open where the four lanes run in; the press shop's and the rolling
    # mill's, one doorway a side (not on a lane: the lanes pass round the yards).
    if not siege:
        p22_walls(L, *FOUNDRY_HALL)
    # The doorways sit off the middle of each wall (the yard's machines stand clear of them).
    shop_doors = (('n', -66.0, 12.0), ('s', -94.0, 12.0), ('w', 94.0, 12.0), ('e', 66.0, 12.0))
    image = {'n': 's', 's': 'n', 'w': 'e', 'e': 'w'}
    mill_doors = tuple((image[s], -m, o) for s, m, o in shop_doors)
    x0, z0, x1, z1 = FOUNDRY_SHOP
    p22_walls(L, x0, z0, x1, z1, shop_doors, skip_roads=False)
    p22_walls(L, -x1, -z1, -x0, -z0, mill_doors, skip_roads=False)
    mill = (-x1, -z1, -x0, -z0)

    # Inside the casting hall: the two furnaces (tall stacks) and their ladles, a conveyor run (a pipe
    # line) and the gantry over the far floor; the objective's ring stays clear.
    # (The lanes cross the hall: the machines stand in the floor between them.)
    for x, z in ((-30.0, 0.0), (-30.0, 26.5)):
        mirrored(L, 'refinery_tower', x, z, 0, pad=0.4, road_gap=0.5, ignore_points=True, must=True)
    for x, z in ((-36.0, 6.0), (-36.0, -6.0), (-24.0, 26.5)):
        mirrored(L, 'silo', x, z, 0, pad=0.4, road_gap=0.5, ignore_points=True)
    for x, z in ((-5.0, 27.0), (5.0, 27.0)):
        mirrored(L, 'container_stack', x, z, 0, pad=0.4, road_gap=0.5, ignore_points=True)
    for sign in (1, -1):
        L.scatter('ammo_crate', sign * -30.0, sign * 12.0, 1, 4, 3, pad=0.2)

    # The press shop (and its image, the rolling mill): the gantry crane across the yard, the presses
    # (storage tanks) and coil stacks along the walls, crates by the doors; the objective's ring clear.
    px, pz = west
    mirrored(L, 'gantry_crane', px - 6.0, pz + 18.0, 0, pad=0.4, road_gap=0.5, ignore_points=True, must=True)
    for dx, dz in ((-18.0, -10.0), (18.0, 10.0)):
        mirrored(L, 'storage_tank', px + dx, pz + dz, 0, pad=0.4, road_gap=0.5, ignore_points=True, must=True)
    for sign in (1, -1):
        L.scatter('ammo_crate', sign * (px + 16.0), sign * (pz - 16.0), 1, 5, 4, pad=0.2)
        L.scatter('barrel', sign * (px - 16.0), sign * (pz - 18.0), 1, 4, 3, pad=0.2)

    # The blocks: factories and warehouses in solid rows, sheds and stacks where a big one does not fit,
    # tanks and silos in the tank farm blocks by the loading yards. Nothing in the halls.
    works = ('factory', 'warehouse', 'garage', 'container_stack')
    farms = ('storage_tank', 'silo', 'container_stack', 'garage')
    for b in p22_blocks(P22_LANES):
        cx, cz = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        if cx < 0 or (cx == 0 and cz < 0):
            continue     # the south-west half is the image of this one
        kinds = farms if abs(cx) > 100 or abs(cz) > 100 else works
        p22_fill(L, b, (FOUNDRY_HALL, FOUNDRY_SHOP, mill), kinds, siege)

    # Pipe runs along the loading yards' edges and wrecked trucks in the lanes by the camps.
    for x, z, rot in ((96.0, 74.0, 0), (74.0, 96.0, 90), (122.0, 70.0, 90)):
        mirrored(L, 'truck', x, z, rot, radius=3.0, pad=0.5, road_gap=None)
    for x, z in ((70.0, 120.0), (120.0, 40.0)):
        since = len(L.props)
        lines_of(L, 'pipeline', x, z, x + 16.0, z, 0.5, pad=0.2, road_gap=0.8)
        mirror_new(L, since, pad=0.2, road_gap=0.8)
    return finish(L)


VEYRA_STREETS = (-108.0, -60.0, -18.0, 18.0, 60.0, 108.0)   # the old quarter's streets, each way (with their jogs)
VEYRA_SQUARES = ((-94.0, 66.0, -66.0, 94.0), (-22.0, -18.0, 22.0, 18.0), (66.0, -94.0, 94.0, -66.0))
VEYRA_PIAZZAS = ((34.0, 30.0, 46.0, 44.0), (-46.0, -44.0, -34.0, -30.0), (26.0, -122.0, 40.0, -110.0), (-40.0, 110.0, -26.0, 122.0))


def p22_lanes(L, lanes, width=P22_LANE):
    """A grid of straight lanes across the battlefield; the outer ones stop short of the camps' yards (the
    camp's HQ stands behind its rally, where they would cross)."""
    edge = HALF - 4.0
    for c in lanes:
        a, b = (-edge, 90.0) if c > 100 else (-90.0, edge) if c < -100 else (-edge, edge)
        L.road(width, c, a, c, b)
        L.road(width, a, c, b, c)


def p22_fill(L, block, holes, kinds, siege, margin=1.5):
    """Builds a block of the north-east half (what the halls or squares leave of it) and its image; in a
    Siege version a block in the fortress's ground (beyond the first lanes in the north-east) stays open and
    only its image is built."""
    fortress = siege and block[0] >= 20.0 and block[1] >= 20.0
    for piece in p22_minus(block, holes, margin=margin):
        if fortress:
            x0, z0, x1, z1 = piece
            image = (-x1, -z1, -x0, -z0)
            if not any(image[0] < h[2] and image[2] > h[0] and image[1] < h[3] and image[3] > h[1] for h in holes):
                city_block(L, *image, kinds, gap=1.0, pad=0.3, road_gap=0.8)
            continue
        since = len(L.props)
        city_block(L, *piece, kinds, gap=1.0, pad=0.3, road_gap=0.8)
        mirror_new(L, since, pad=0.3, road_gap=0.8)


def veyra_street(c, vertical, jog=3.0, step=36.0):
    """One old-town street: straight on the grid line `c` with a jog of `jog` m every `step` m (the old
    plots it bends round), laid for c >= 0 and mirrored through the centre for c < 0. Flat x, z points."""
    edge = HALF - 4.0
    sign = 1.0 if c >= 0 else -1.0
    base = abs(c)
    # The outer streets stop short of the camps' yards (see p22_lanes).
    end = 86.0 if base > 100 else edge
    pts = []
    t = -edge
    k = 0
    while t < end:
        off = (jog if (k % 2) else -jog) * (1.0 if base > 30 else 0.0)
        pts.append((base + off, t) if vertical else (t, base + off))
        t = min(end, t + step)
        k += 1
    pts.append((base, end) if vertical else (end, base))
    if sign < 0:
        pts = [(-x, -z) for x, z in pts]
    return [v for p in pts for v in p]


def veyra_old_quarter(seed=241, siege=False):
    """Veyra Old Quarter (urban, prompt 22 E.2): the capital's old town, narrow streets between tall old
    houses that bend round the old plots, opening on squares. The cathedral square at the centre (the town
    objective): the cathedral on its north side, the old town hall facing it, market stalls and lamps. The
    market square in the north-west (the west objective) and the clock square in the south-east (the east
    objective, its image): stalls, trees, a well of cobbles. Four small piazzas along the way; a ring of
    old wall pieces and gatehouses on the edge; barricades and burnt cars where the streets meet. The same
    ground on either half, mirrored. The Siege version (siege=True) leaves the fortress's ground open (see
    p22_fill)."""
    west, east = (-80.0, 80.0), (80.0, -80.0)
    points = [(*west, 13.0), (0.0, 0.0, 16.0), (*east, 13.0)]
    L = world_layout(seed, points, clear=VEYRA_SQUARES + VEYRA_PIAZZAS)
    for c in VEYRA_STREETS:
        L.road(P22_LANE, *veyra_street(c, True))
        L.road(P22_LANE, *veyra_street(c, False))
    # Each camp's way into the town: a wider street from the camp's plaza.
    for sign in (1, -1):
        L.road(12, sign * CAMP_1[0], sign * CAMP_1[1], sign * 108.0, sign * 60.0)
        L.road(12, sign * CAMP_1[0], sign * CAMP_1[1], sign * 60.0, sign * 108.0)

    # The cathedral on the square's north side; the old town hall (offices round a tower) faces it.
    L.add('church', 0.0, 30.0, 90, pad=0.3, road_gap=0.5, must=True)
    L.add('office_block', 0.0, -30.0, 0, pad=0.3, road_gap=0.5, must=True)
    # Market stalls, lamps and planted trees round every square, clear of the objective rings.
    for x0, z0, x1, z1 in VEYRA_SQUARES:
        for u in (0.18, 0.5, 0.82):
            for x, z in ((x0 + (x1 - x0) * u, z0 + 1.2), (x0 + (x1 - x0) * u, z1 - 1.2)):
                L.force('lamp_post', x, z)
    for sx, sz in ((-80.0, 80.0), (80.0, -80.0)):
        for dx, dz, rot in ((-11.0, -8.0, 0), (11.0, -8.0, 0), (-11.0, 8.0, 0), (11.0, 8.0, 0)):
            L.force('market_stall', sx + dx, sz + dz, rot)
    for x0, z0, x1, z1 in VEYRA_PIAZZAS:
        cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
        L.force('tree', cx - 3.0, cz)
        L.force('tree', cx + 3.0, cz)

    # The houses: tall townhouses, stone houses of offices, shops on the ground floor, cottages and sheds where
    # the plot is tight; a block is built only where the streets and squares leave room.
    kinds = ('townhouse', 'cottage', 'office_block', 'shop', 'garage')
    for b in p22_blocks(VEYRA_STREETS):
        cx, cz = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        if cx < 0 or (cx == 0 and cz < 0):
            continue
        p22_fill(L, b, VEYRA_SQUARES + VEYRA_PIAZZAS, kinds, siege, margin=1.0)

    # The old town wall's broken pieces on the edge, and a gatehouse (a ruined tower) by each camp road.
    for sign in (1, -1):
        for x in (-120.0, -80.0, -40.0, 0.0, 40.0):
            L.add('stone_wall', sign * x, sign * -141.0, 0, pad=0.3, road_gap=0.8)
            L.add('stone_wall', sign * 141.0, sign * -x, 90, pad=0.3, road_gap=0.8)
        L.add('ruin_tower', sign * 120.0, sign * 72.0, 0, pad=0.4, road_gap=0.8)
    # Cars parked along the side streets (nothing solid in a street: they are the only ways through).
    for x, z, rot in ((104.0, 30.0, 90), (30.0, 104.0, 0), (56.0, -30.0, 90), (-30.0, 56.0, 0), (18.0, 84.0, 90)):
        mirrored(L, 'car', x, z, rot, radius=2.0, pad=0.3, road_gap=None)
    return finish(L)


MAPS_P22 = [
    ('foundry', foundry, 'urban', ('press_shop', 'casting_hall', 'rolling_mill'),
     'Foundry for Conquest: an old Hegemon tank works, walled halls and solid blocks of sheds cut by narrow factory lanes.',
     'Foundry for Survival: the same works, holding out against waves from the north-east.'),
    ('veyra_old_quarter', veyra_old_quarter, 'urban', ('market_square', 'cathedral_square', 'clock_square'),
     "Veyra Old Quarter for Conquest: the capital's old town, narrow bending streets between tall houses, three squares.",
     'Veyra Old Quarter for Survival: the same old town, holding out against waves from the north-east.'),
]
WAR_P22 = {
    # Indoor works and a packed old town: no pylons, poles or trench lines through the blocks.
    'foundry': dict(pylons=False, poles=False, ditch=False),
    'veyra_old_quarter': dict(pylons=False, poles=False, ditch=False),
}
DENSIFY_P22 = {
    # Every block is built by hand: no hamlets or tree clumps (the fill only reaches the outer edge).
    'foundry': dict(clumps=0, outcrops=0, hamlets=0, where=lambda x, z: max(abs(x), abs(z)) > HALF - 12.0),
    'veyra_old_quarter': dict(clumps=2, outcrops=0, hamlets=0, where=lambda x, z: max(abs(x), abs(z)) > HALF - 12.0),
}


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
        # Room for the biggest hull (prompt 12 C.2), as the big fortress has it (fortress.open_wide):
        # routes three cells wide to every objective and gateway mouth, the clutter in the way taken
        # out. (Only on the real build: the outline is carved round the plan without buildings.)
        fortress.open_wide(ClassicFortress(L, name), 2 * OUTER_LINE)
        print(f'{name} siege: {len(houses)} fortress buildings')
    return L


class ClassicFortress:
    """What fortress.open_wide needs of the classic corner fortress: its layout, name, the attacker's
    camp, its objectives, and no hardpoints (its defences are map units)."""

    def __init__(self, L, name):
        self.L, self.name, self.rally = L, name, L.teams[0]
        self.blocks, self.slots = [], []

    def targets(self):
        return siege_targets(self.L)


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
# Per battlefield, changes to its theme's kit (keys of WAR, plus counts: 'wrecks' a half,
# 'craters', 'dead_trees', and 'where': a test (x, z) of the ground where cover that blocks may
# stand), for the maps whose ground the plain kit would spoil (the open salt flats, the causeways
# of the water maps).
MAP_WAR = {}


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
    style = dict(WAR[theme], **MAP_WAR.get(map_id, {}))
    rng = random.Random(sum(map(ord, map_id)) * 7 + 3)
    circles, lines = campaign_keep(map_id)

    def clear(kind, x, z, rot):
        if not PROPS[kind].get('blocks', False):
            return True
        # A fixed route (prompt 20 M) keeps its whole width open.
        w, d = L.size(kind, rot)
        if on_route(map_id, x - w / 2, z - d / 2, x + w / 2, z + d / 2):
            return False
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

    where = style.get('where')

    def ok(kind, x, z, rot, pad, road_gap):
        x, z = round(x * 2) / 2, round(z * 2) / 2
        if not (within(kind, x, z, rot) and clear(kind, x, z, rot)):
            return False
        if where is not None and PROPS[kind].get('blocks', False) and not where(x, z):
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
    wrecks = style.get('wrecks', more(7))
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
    for _ in range(style.get('craters', more(8))):
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
        for _ in range(style.get('dead_trees', more(16))):
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
    design put them, so rivers and lava stay unbroken. A layout made on the battlefield itself
    (world_layout) is already there and comes back as it is."""
    if L.world:
        return L
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


# Per battlefield, changes to its theme's fill (keys of DENSIFY, plus counts: 'clumps' of trees,
# rock 'outcrops', 'hamlets' a half, and 'where': a test (x, z) of the ground it may fill).
MAP_DENSIFY = {}


def densify(L, map_id, theme, poly):
    """Fills the ground the bigger battlefield opened up: clumps of the theme's trees in the
    open, a few rock outcrops away from the roads, and hamlets (two or three of the theme's
    buildings with a yard and a vehicle) beside the roads, as many on either half. Everything is
    inside the outline, clear of camps, objectives, plazas and campaign routes."""
    style = dict(DENSIFY[theme], **MAP_DENSIFY.get(map_id, {}))
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

    where = style.get('where')

    def put(kind, x, z, rot=0, pad=1.0, road_gap=1.0):
        x, z = round(x * 2) / 2, round(z * 2) / 2
        blocks = PROPS[kind].get('blocks', False)
        if not inside(kind, x, z, rot) or (blocks and not clear(x, z, max(L.size(kind, rot)) / 2 + 1)):
            return False
        w, d = L.size(kind, rot)
        if blocks and on_route(map_id, x - w / 2, z - d / 2, x + w / 2, z + d / 2):
            return False
        if where is not None and not where(x, z):
            return False
        return L.add(kind, x, z, rot, pad=pad, road_gap=road_gap)

    def far_from_points(x, z, extra):
        return all(math.hypot(x - px, z - pz) > r + extra for px, pz, r in L.points)

    def far_from_camps(x, z, d):
        return all(math.hypot(x - t[0], z - t[1]) > d for t in L.teams)

    # Tree clumps in the open.
    for _ in range(style.get('clumps', more(18))):
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
    for _ in range(style.get('outcrops', more(6)) if style['rocks'] else 0):
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
    hamlets = style.get('hamlets', more(3))
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


# The battlefields of round 4M (see world_layout), and what they change in the kit and the fill.
MAPS += MAPS_4M
MAP_WAR.update(WAR_4M)
MAP_DENSIFY.update(DENSIFY_4M)
# Prompt 16: Lighthouse Bay.
MAPS += MAPS_P16
MAP_WAR.update(WAR_P16)
MAP_DENSIFY.update(DENSIFY_P16)
# Prompt 20 M: Open-Pit Mine and Orbital Gateway.
MAPS += MAPS_P20
MAP_WAR.update(WAR_P20)
MAP_DENSIFY.update(DENSIFY_P20)
# Prompt 22 E: Foundry and Veyra Old Quarter.
MAPS += MAPS_P22
MAP_WAR.update(WAR_P22)
MAP_DENSIFY.update(DENSIFY_P22)

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


# Causeway battlefields: the large fortress's walls would cut every causeway, so their Siege
# version keeps the classic walled square in the north-east corner (fortify_corner).
# Lighthouse Bay (prompt 16): the sea fills the south-east, where the big fortress would stand in the water.
CLASSIC_SIEGE = {'swamp', 'coralisles'}
# Battlefields whose builder lays a Siege version of its own (siege=True): Lighthouse Bay (its coast), the two
# dense maps of prompt 22 E (the fortress's ground left open).
SIEGE_OWN = {'lighthousebay', 'foundry', 'veyra_old_quarter'}


def sea_meta(map_id):
    """A map's sea (prompt 16), for every version of it: the lanes, beaches, piers and batteries."""
    return {'sea': lb_sea_block()} if map_id == 'lighthousebay' else {}


def main(only=()):
    for map_id, build, theme, names, conquest, survival in MAPS:
        if only and map_id not in only:
            continue
        layout = scale_layout(build())
        # One outline per battlefield, shared by all its versions: carved round everything the
        # Conquest, Survival and Siege versions and the campaign need; then the battlefield is
        # dressed and filled inside it (the siege version the same, before its fortress).
        poly, _ = outline_tools.carve(map_id, keep_of([layout, fortify_corner(scale_layout(build()), map_id, buildings=False)], map_id), seed=len(map_id) * 31 + 7)
        # A map on the sea keeps the square's edge on the sea's side (the ships sail in and out there).
        if map_id == 'lighthousebay':
            poly = lb_open_sea(poly)
        densify(warzone(layout, map_id, theme, poly), map_id, theme, poly)
        # (The outline is carved round the first fortress plan above, so the Conquest and Survival
        # versions and the campaign stay as they were; the fortress itself is built into the
        # finished siege battlefield, inside that outline: see fortress.py.)
        classic = map_id in CLASSIC_SIEGE
        # Lighthouse Bay's Siege version leaves the fortress's corner of the coast bare.
        siege_build = functools.partial(build, siege=True) if map_id in SIEGE_OWN else build
        siege = densify(warzone(scale_layout(siege_build()), map_id, theme, poly), map_id, theme, poly)
        # The classic fortress is built before the outline is applied, as it always was.
        if classic:
            siege = fortify_corner(siege, map_id)
            if map_id == 'lighthousebay':
                lb_refill_sea(siege)
        dropped = apply_outline(layout, poly)
        apply_outline(siege, poly)
        missing = layout.reachable()
        if missing:
            raise SystemExit(f'{map_id}: unreachable inside the outline: {missing}')
        if classic:
            hq = next(p for p in siege.props if p['def'] == 'command_hq')
            w, d = PROPS['command_hq']['width'] / 2, PROPS['command_hq']['depth'] / 2
            missing = siege.reachable([('camp', *siege.teams[1]), ('hq', hq['x'] - w, hq['z'] - d, hq['x'] + w, hq['z'] + d)])
            if missing:
                raise SystemExit(f'{map_id} siege: unreachable inside the outline: {missing}')
            fortress_block, siege_rings = None, SIEGE_RINGS
        else:
            fortress_block, siege_rings = fortress.fortify(siege, map_id, theme, poly)
            if map_id == 'lighthousebay':
                # The fortress's ground on the coast: the sea comes back round it, and a hardpoint the
                # plan put out on the water is dropped.
                lb_refill_sea(siege)
                fortress_block['slots'] = [sl for sl in fortress_block['slots'] if not lb_sea_tile(sl['x'], sl['z'])]
        bases, outposts, siege_bases = plan_bases(map_id, layout, siege)
        # A fixed route (prompt 20 M) is open all along on the Conquest battlefield (Survival's too: the same layout).
        check_route(layout, map_id, map_id)
        print(f'{map_id}: outline of {len(poly)} points, {dropped} props left outside dropped')
        counts = {}
        for p in layout.props:
            counts[p['def']] = counts.get(p['def'], 0) + 1
        print(f'{map_id}: {len(layout.props)} props:', dict(sorted(counts.items())))
        points = [{'id': pid, 'name': name, 'x': x, 'z': z, 'radius': r, 'outpost': outposts.get(i, [])}
                  for i, (pid, name, (x, z, r)) in enumerate(zip(('west', 'town', 'east'), names, layout.points))]
        dump(DATA / 'maps' / f'{map_id}_conquest.json', conquest,
             {'id': f'{map_id}_conquest', 'theme': theme, 'size': SIZE, 'teams': TEAMS, 'points': points,
              'units': grown(CONQUEST_UNITS), 'bases': bases, **sea_meta(map_id), **route_meta(map_id)}, layout)
        dump(DATA / 'maps' / f'{map_id}_sandbox.json', survival,
             {'id': f'{map_id}_sandbox', 'theme': theme, 'size': SIZE, 'teams': TEAMS, 'units': grown(SURVIVAL_UNITS), **sea_meta(map_id), **route_meta(map_id)}, layout)
        # Siege: the same battlefield (built afresh, so it is identical) with the enemy fortress.
        name = conquest.split(' for ')[0]
        if classic:
            dump(DATA / 'maps' / f'{map_id}_siege.json',
                 f'{name} for Siege: the enemy fortress holds the north-east quadrant; destroy its command HQ.',
                 {'id': f'{map_id}_siege', 'theme': theme, 'size': SIZE,
                  'teams': [TEAMS[0], {'team': 1, 'x': siege.teams[1][0], 'z': siege.teams[1][1]}], 'points': [], 'siegeRings': siege_rings,
                  'units': [u for u in grown(CONQUEST_UNITS) if u['team'] == 0] + siege.units, 'bases': siege_bases, **sea_meta(map_id),
                  **route_meta(map_id)}, siege)
            print(f'{map_id}_siege: {len(siege.props)} props, {len(siege.units)} defences (classic fortress)')
            continue
        dump(DATA / 'maps' / f'{map_id}_siege.json',
             f'{name} for Siege: the enemy fortress holds the north-east of the battlefield (its outer line, walls and keep); '
             f'destroy its command HQ.',
             {'id': f'{map_id}_siege', 'theme': theme, 'size': SIZE,
              'teams': [TEAMS[0], {'team': 1, 'x': siege.teams[1][0], 'z': siege.teams[1][1]}], 'points': [], 'siegeRings': siege_rings,
              'units': [u for u in grown(CONQUEST_UNITS) if u['team'] == 0], 'bases': siege_bases, 'fortress': fortress_block,
              **sea_meta(map_id), **route_meta(map_id)}, siege)
        print(f'{map_id}_siege: {len(siege.props)} props, {len(fortress_block["slots"])} fortress hardpoints')


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
