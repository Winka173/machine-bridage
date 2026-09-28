"""Base hardpoints: where each side's HQ stands in its camp and where the towers and modules of
its base loadout go, and the outpost hardpoints beside the capture points (see BaseSites.cs).

A camp is the team's rally point (the drop zone) with the HQ 10-14 m behind it, away from the map
centre, and its tower hardpoints in three sizes: 2 large ones at the key positions close to the
HQ (flanking the drop zone, facing the enemy), 3 medium ones further out in between, and 6 small
ones on the outer ring and beside the lanes coming into the base; and 3 utility hardpoints near
the HQ, beside or behind it. Each size is written most important first (nearest the enemy): the
lower base levels use the first few of each. Each capture point gets an outpost: a medium
hardpoint on one flank and a small one on the other (square to the camp-to-camp axis, so neither
side's approach is favoured), 14-22 m from its centre.

A hardpoint of a size is planned for the largest structure that size takes (SIZES: 5, 6.5 and
9 m across), anchored as a blocker of 0.8 times that grown by the 1.5 m obstacle clearance, as
SimWorld.AnchorDefence does. Every one keeps clear of the drop zone, the roads (half their width
+ 6 m), every prop (3 m), the map's outline (8 m), the capture circles, the start units and the
campaign's spawns and routes, and of the other hardpoints. On the simulation's navigation grid
its blocked ground must be open and off every doorway cell (LaneMap's Narrow and NoPark flags,
worked out here exactly as the simulation does), may lean against at most one obstacle (so it
never closes the gap between two), must not make any new doorway cell (a gap of 1-3 cells to
something else), and must not cut any ground off. So no structure ever sits in a lane, a gate, a
narrow pass or the mouth of a camp exit. The finished plan is checked again on the grid with
every hardpoint filled.

Conquest camps are placed as mirror pairs through the centre (the camps are mirrored), so both
sides get the same base. Nothing here touches the layout or its random numbers: the battlefield
comes out as before, less only the props a base clears (see CAMP_CLUTTER).
"""
import math
from collections import namedtuple

CELL = 2.0
CLEARANCE = 1.5
NARROW_WIDTH = 6.0      # LaneMap.NarrowWidth
THROUGH_CELLS = 2       # LaneMap.ThroughCells
MAX_NOPARK_CELLS = 30   # LaneMap.MaxNoParkCells
NOPARK_MOUTH = 2        # LaneMap.NoParkMouth

SIZES = {'small': 5.0, 'medium': 6.5, 'large': 9.0}    # metres across the largest structure each slot size takes
CAMP_TOWERS = (('large', 2), ('medium', 3), ('small', 6))   # a camp's tower hardpoints, in the order they are placed
CAMP_UTILITIES = (('medium', 3),)                          # and its utility hardpoints
OUTPOST_SLOTS = ('medium', 'small')                        # an outpost's hardpoints
HQ_SIZE = 14 * 0.85             # the HQ's hull across; set from balance.json by configure()
HQ_BACK = (10.0, 14.0)          # the HQ stands this far behind the rally
RING_NEAR = 20.0                # camp hardpoints stand at least this far from the HQ
OUTPOST_RING = (14.0, 22.0)     # outpost hardpoints this far from the point's centre
OUTPOST_WIDE = (12.0, 32.0)     # ... or this far, for a point with no room in the first ring
DROP_ZONE = 16.0                # no hardpoint centre nearer a rally than this
DROP_CORE = 11.0                # nor any of its blocked ground
HQ_ROAD_GAP = 2.0               # the HQ keeps off the road itself (a camp road ends at the rally)
POINT_GAP = 3.0                 # camp footprint to a capture circle
UNIT_GAP = 3.0                  # blocked ground to a start unit or campaign spawn (Chebyshev)
ROUTE_GAP = 3.0                 # blocked ground to a campaign route
APART = 1                       # open cells at least between two structures' blocked ground (never touching)

# The margins, strictest first. Every hardpoint that fits under the first tier is placed under it.
# A camp hemmed in by the outline, its camp road and its drop zone has no room for twelve
# hardpoints 8 m apart within 45 m of its HQ, so the base spreads out first (the ring grows, with
# the margins kept), and only then do the margins close in; build_maps prints which tier each map
# needed. What never relaxes: the blocked ground open and off every doorway, no new doorway, no
# gap closed and no ground cut off, the drop zone, the spacing, the start units, the campaign's
# spawns and routes, and the capture circles.
#   ring: furthest from the HQ; road: footprint to a road's edge (on top of half its width);
#   prop: footprint to a blocking prop; soft: to any other prop; edge: footprint to the outline.
Tier = namedtuple('Tier', 'name ring road prop soft edge')
TIERS = (
    Tier('spec', 45.0, 6.0, 3.0, 3.0, 8.0),
    Tier('wide', 55.0, 6.0, 3.0, 3.0, 8.0),
    Tier('wider', 65.0, 6.0, 3.0, 3.0, 8.0),
    Tier('snug', 65.0, 4.0, 2.0, 1.0, 6.0),
    Tier('tight', 75.0, 2.5, 1.5, 0.5, 4.0),
    Tier('last', 85.0, 1.5, 1.0, 0.0, 3.0),
)
SPEC = TIERS[0]


def configure(hq_size):
    global HQ_SIZE
    HQ_SIZE = hq_size


def blocker_side(size):
    """The square a structure up to `size` across blocks: 0.8 of it, grown by the clearance."""
    return size * 0.8 + 2 * CLEARANCE


def heading_to(x, z, tx, tz):
    """Degrees, as the map files write headings (SimMath.HeadingOf: 0 is +z, 90 is +x)."""
    return round(math.degrees(math.atan2(tx - x, tz - z))) % 360


# The base's own ground. The battlefield's clutter (trees and bushes, craters, trenches, wrecks,
# loose rocks, obstacles, poles, the old field camp, parked cars) may be cleared for hardpoints
# within this far of a rally (or OUTPOST_CLEAR of a capture point): the plan is made as if it were
# gone, and then only the clutter within CLEAR_REACH of a structure's blocked ground is taken
# away. Buildings, rock walls, rivers and lava always stay: they shape the lanes.
CAMP_CLEAR = 95.0
OUTPOST_CLEAR = 32.0
CLEAR_REACH = 9.0        # blocking clutter this near a structure's blocked ground goes (no 1-3 cell gaps)
CLEAR_SOFT = 3.5         # other clutter only this near (the margin to props)
CAMP_CLUTTER = {
    'tree', 'palm', 'cactus', 'charred_tree', 'dead_tree', 'jungle_tree_a', 'jungle_tree_b', 'jungle_tree_c', 'fern_bush',
    'bamboo_clump', 'crater_large', 'foxhole', 'trench_corner', 'trench_straight', 'tank_ditch', 'dirt_mound', 'lava_vent',
    'camo_net', 'supply_pile', 'command_tent', 'fuel_bladder', 'radio_mast', 'ammo_crate', 'barrel', 'telegraph_pole',
    'lamp_post', 'power_pylon', 'wreck_tank', 'wreck_car', 'wreck_truck', 'artillery_wreck', 'tank_trap', 'sandbags',
    'jersey_barrier', 'barricade', 'razor_wire', 'boulders', 'snow_rock', 'basalt_rock_a', 'basalt_rock_b', 'basalt_rock_c',
    'hedge', 'fence', 'stone_wall', 'car', 'truck',
}


# Terrain never makes way, not even for a camp that is still short of hardpoints once its clutter
# is gone (then its buildings in the way are pulled down: the base is enlarged, see plan_bases).
TERRAIN = {'mesa', 'cliff_a', 'cliff_b', 'volcanic_cliff', 'obsidian_spire', 'lava_pool', 'river_water', 'river_ford',
           'bridge_road'}   # a bridge is the way across: never pulled down


def clearable(props, rects, rallies, points=(), demolish=False, crowded=()):
    """Indices of the props that may make way for hardpoints: the clutter round the camps and the
    points (see CAMP_CLUTTER); with `demolish` every camp building but terrain, and round the
    points of `crowded` (indices) every building but terrain."""
    out = []
    for i, (p, r) in enumerate(zip(props, rects)):
        in_camp = any(point_rect(x, z, *r) < CAMP_CLEAR for x, z in rallies)
        near = [k for k, (x, z, _) in enumerate(points) if point_rect(x, z, *r) < OUTPOST_CLEAR]
        if p['def'] in CAMP_CLUTTER:
            if in_camp or near:
                out.append(i)
        elif p['def'] not in TERRAIN and ((demolish and in_camp) or any(k in crowded for k in near)):
            out.append(i)
    return out


def in_the_way(rects, blocks, candidates, structures, reaches):
    """Of the `candidates` (indices into `rects`), those within reach of a structure's blocked
    ground (x, z, blocker side): each structure's own (reach, soft) of `reaches`, `soft` for
    clutter that does not block."""
    out = []
    for i in candidates:
        # To the millimetre: a layout moved and moved back (the siege fortress is built in shifted
        # coordinates) must clear exactly what the other versions clear.
        x0, z0, x1, z1 = (round(v, 3) for v in rects[i])
        for (x, z, side), (reach, soft) in zip(structures, reaches):
            h = side / 2 + (reach if blocks[i] else soft)
            if x0 < round(x + h, 3) and x1 > round(x - h, 3) and z0 < round(z + h, 3) and z1 > round(z - h, 3):
                out.append(i)
                break
    return out


# ------------------------------------------------------------------------------------ geometry
def point_rect(px, pz, x0, z0, x1, z1):
    return math.hypot(max(x0 - px, 0.0, px - x1), max(z0 - pz, 0.0, pz - z1))


def point_segment(px, pz, ax, az, bx, bz):
    vx, vz = bx - ax, bz - az
    length = vx * vx + vz * vz
    t = 0.0 if length < 1e-12 else max(0.0, min(1.0, ((px - ax) * vx + (pz - az) * vz) / length))
    return math.hypot(px - ax - vx * t, pz - az - vz * t)


def segment_hits_rect(ax, az, bx, bz, x0, z0, x1, z1):
    """Liang-Barsky: whether the segment a-b meets the rectangle."""
    t0, t1 = 0.0, 1.0
    dx, dz = bx - ax, bz - az
    for p, q in ((-dx, ax - x0), (dx, x1 - ax), (-dz, az - z0), (dz, z1 - az)):
        if abs(p) < 1e-12:
            if q < 0:
                return False
            continue
        r = q / p
        if p < 0:
            t0 = max(t0, r)
        else:
            t1 = min(t1, r)
        if t0 > t1:
            return False
    return True


def segment_rect(ax, az, bx, bz, x0, z0, x1, z1):
    """Distance from a segment to an axis-aligned rectangle (0 when they meet)."""
    if segment_hits_rect(ax, az, bx, bz, x0, z0, x1, z1):
        return 0.0
    return min(point_rect(ax, az, x0, z0, x1, z1), point_rect(bx, bz, x0, z0, x1, z1),
               *(point_segment(cx, cz, ax, az, bx, bz) for cx, cz in ((x0, z0), (x1, z0), (x0, z1), (x1, z1))))


def inside(poly, x, z):
    hit = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, zi = poly[i]
        xj, zj = poly[j]
        if (zi > z) != (zj > z) and x < (xj - xi) * (z - zi) / (zj - zi + 1e-12) + xi:
            hit = not hit
        j = i
    return hit


def square(x, z, side):
    h = side / 2
    return x - h, z - h, x + h, z + h


def mirror(x, z):
    return -x, -z


# ------------------------------------------------------------------------------------ the grid
def flood(blocked, start):
    """Cells reachable from `start` (4-way: the pathfinder's 8-way moves never cut corners)."""
    n = len(blocked)
    sx, sz = start
    if not (0 <= sx < n and 0 <= sz < n) or blocked[sz][sx]:
        return set()
    seen = {start}
    todo = [start]
    while todo:
        x, z = todo.pop()
        for c in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
            if 0 <= c[0] < n and 0 <= c[1] < n and c not in seen and not blocked[c[1]][c[0]]:
                seen.add(c)
                todo.append(c)
    return seen


def narrow_at(blocked, x, z):
    """LaneMap.FindDoorways for one walkable cell: whether it is in a doorway."""
    n = len(blocked)

    def run(dx, dz, cap):
        k = 0
        while k < cap:
            nx, nz = x + dx * (k + 1), z + dz * (k + 1)
            if not (0 <= nx < n and 0 <= nz < n) or blocked[nz][nx]:
                break
            k += 1
        return k

    for ax, az in ((1, 0), (0, 1), (1, 1), (1, -1)):
        step = (1.41421356 if ax and az else 1.0) * CELL
        cap = int(NARROW_WIDTH / step) + 1
        if (1 + run(ax, az, cap) + run(-ax, -az, cap)) * step > NARROW_WIDTH + 0.01:
            continue
        px, pz = -az, ax
        if run(px, pz, THROUGH_CELLS) < THROUGH_CELLS or run(-px, -pz, THROUGH_CELLS) < THROUGH_CELLS:
            continue
        return True
    return False


def lane_flags(blocked):
    """LaneMap.FindDoorways and MarkNoPark on a blocked grid: (narrow, nopark) per cell."""
    n = len(blocked)
    narrow = [[not blocked[z][x] and narrow_at(blocked, x, z) for x in range(n)] for z in range(n)]
    nopark = [[False] * n for _ in range(n)]
    seen = [[False] * n for _ in range(n)]
    for z in range(n):
        for x in range(n):
            if not narrow[z][x] or seen[z][x]:
                continue
            seen[z][x] = True
            group = [(x, z)]
            head = 0
            while head < len(group):
                cx, cz = group[head]
                head += 1
                for dz in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        nx, nz = cx + dx, cz + dz
                        if 0 <= nx < n and 0 <= nz < n and narrow[nz][nx] and not seen[nz][nx]:
                            seen[nz][nx] = True
                            group.append((nx, nz))
            if len(group) > MAX_NOPARK_CELLS:
                continue
            for cx, cz in group:
                for dz in range(-NOPARK_MOUTH, NOPARK_MOUTH + 1):
                    for dx in range(-NOPARK_MOUTH, NOPARK_MOUTH + 1):
                        nx, nz = cx + dx, cz + dz
                        if 0 <= nx < n and 0 <= nz < n and not blocked[nz][nx]:
                            nopark[nz][nx] = True
    return narrow, nopark


def components(blocked):
    """A label per blocked cell: which obstacle (8-connected) it belongs to; 0 for open cells."""
    n = len(blocked)
    label = [[0] * n for _ in range(n)]
    count = 0
    for z in range(n):
        for x in range(n):
            if not blocked[z][x] or label[z][x]:
                continue
            count += 1
            label[z][x] = count
            todo = [(x, z)]
            while todo:
                cx, cz = todo.pop()
                for dz in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        nx, nz = cx + dx, cz + dz
                        if 0 <= nx < n and 0 <= nz < n and blocked[nz][nx] and not label[nz][nx]:
                            label[nz][nx] = count
                            todo.append((nx, nz))
    return label


def cells_apart(a, b):
    """Open cells between two blocked cell ranges (Chebyshev; negative when they overlap)."""
    return max(b[0] - a[2] - 1, a[0] - b[2] - 1, b[1] - a[3] - 1, a[1] - b[3] - 1)


# ------------------------------------------------------------------------------------ the ground
class Ground:
    """What hardpoints must respect on one version of a battlefield: its navigation grid (as the
    simulation fills it, see Layout.blocked_grid), the doorways on it, the roads, props, outline,
    objectives and what the start and the campaign put down."""

    def __init__(self, blocked, lo, props, roads, boundary, points, rallies, units=(), campaign=((), ())):
        self.blocked = blocked
        self.n = len(blocked)
        self.lo = lo
        self.props = [tuple(r) for r, _ in props]          # (x0, z0, x1, z1) of every prop
        self.blocks = [bool(b) for _, b in props]          # whether it blocks movement
        self.roads = []                      # (ax, az, bx, bz, half width) per segment
        for road in roads:
            pts = road['points']
            for i in range(0, len(pts) - 2, 2):
                self.roads.append((pts[i], pts[i + 1], pts[i + 2], pts[i + 3], road['width'] / 2))
        self.boundary = list(boundary or [])
        self.edges = [(ax, az, bx, bz) for (ax, az), (bx, bz) in zip(self.boundary, self.boundary[1:] + self.boundary[:1])]
        self.points = list(points)           # (x, z, radius)
        self.rallies = list(rallies)
        self.units = list(units)             # (x, z) of the start units
        circles, lines = campaign
        self.spots = [(x, z) for x, z, _ in circles]
        self.routes = [(ax, az, bx, bz) for pts, _ in lines for (ax, az), (bx, bz) in zip(pts, pts[1:])]
        self.narrow, self.nopark = lane_flags(blocked)
        self.label = components(blocked)
        self.gap = self._distance_to_blocked()
        self._reach = {}
        self._buckets = {}
        for i, (x0, z0, x1, z1) in enumerate(self.props):
            for bx in range(int(math.floor(x0 / 16)), int(math.floor(x1 / 16)) + 1):
                for bz in range(int(math.floor(z0 / 16)), int(math.floor(z1 / 16)) + 1):
                    self._buckets.setdefault((bx, bz), []).append(i)

    def cell(self, x, z):
        return int(math.floor((x - self.lo) / CELL)), int(math.floor((z - self.lo) / CELL))

    def cells(self, x, z, side):
        """The cell range (a0, b0, a1, b1) a blocker `side` across centred on (x, z) fills (NavGrid.AddBlocker)."""
        h = side / 2
        return (int(math.floor((x - h - self.lo) / CELL)), int(math.floor((z - h - self.lo) / CELL)),
                int(math.floor((x + h - 1e-4 - self.lo) / CELL)), int(math.floor((z + h - 1e-4 - self.lo) / CELL)))

    def _distance_to_blocked(self):
        """Per cell, the Chebyshev distance (cells) to the nearest blocked cell (the grid's edge counts)."""
        n = self.n
        gap = [[n * 2] * n for _ in range(n)]
        todo = []
        for z in range(n):
            for x in range(n):
                if self.blocked[z][x]:
                    gap[z][x] = 0
                    todo.append((x, z))
                elif x in (0, n - 1) or z in (0, n - 1):
                    gap[z][x] = 1
                    todo.append((x, z))
        head = 0
        while head < len(todo):
            x, z = todo[head]
            head += 1
            d = gap[z][x] + 1
            for dz in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    nx, nz = x + dx, z + dz
                    if 0 <= nx < n and 0 <= nz < n and gap[nz][nx] > d:
                        gap[nz][nx] = d
                        todo.append((nx, nz))
        return gap

    def reach(self, x, z):
        key = self.cell(x, z)
        if key not in self._reach:
            self._reach[key] = flood(self.blocked, key)
        return self._reach[key]

    def openness(self, x, z, side):
        """Open cells between a blocker's ground and the nearest thing that blocks (-1: it overlaps one)."""
        a0, b0, a1, b1 = self.cells(x, z, side)
        if a0 < 0 or b0 < 0 or a1 >= self.n or b1 >= self.n:
            return -1
        return min(self.gap[gz][gx] for gz in range(b0, b1 + 1) for gx in range(a0, a1 + 1)) - 1

    # the fixed rules ---------------------------------------------------------------------
    def doorway_free(self, x, z, side):
        a0, b0, a1, b1 = self.cells(x, z, side)
        return not any(self.narrow[gz][gx] or self.nopark[gz][gx] for gz in range(b0, b1 + 1) for gx in range(a0, a1 + 1))

    def edge_clear(self, rect, gap):
        if not self.boundary:
            return True
        x0, z0, x1, z1 = rect
        if not inside(self.boundary, (x0 + x1) / 2, (z0 + z1) / 2):
            return False
        for ax, az, bx, bz in self.edges:
            if min(ax, bx) > x1 + gap or max(ax, bx) < x0 - gap or min(az, bz) > z1 + gap or max(az, bz) < z0 - gap:
                continue
            if segment_rect(ax, az, bx, bz, x0, z0, x1, z1) < gap:
                return False
        return True

    def road_gap(self, rect):
        """How far a rectangle stands from the nearest road's edge."""
        x0, z0, x1, z1 = rect
        return min((segment_rect(ax, az, bx, bz, x0, z0, x1, z1) - half for ax, az, bx, bz, half in self.roads), default=1e9)

    def road_cells_clear(self, rect, margin=0.25):
        """No navigation cell under the rectangle is a road cell (LaneMap stamps a cell as road when
        its centre lies within the road's half width), with `margin` to spare."""
        x0, z0, x1, z1 = rect
        a0, b0 = self.cell(x0, z0)
        a1, b1 = self.cell(x1 - 1e-3, z1 - 1e-3)
        for gz in range(b0, b1 + 1):
            for gx in range(a0, a1 + 1):
                cx, cz = self.lo + (gx + 0.5) * CELL, self.lo + (gz + 0.5) * CELL
                for ax, az, bx, bz, half in self.roads:
                    if point_segment(cx, cz, ax, az, bx, bz) <= half + margin:
                        return False
        return True

    def road_clear(self, rect, gap):
        x0, z0, x1, z1 = rect
        for ax, az, bx, bz, half in self.roads:
            g = half + gap
            if min(ax, bx) > x1 + g or max(ax, bx) < x0 - g or min(az, bz) > z1 + g or max(az, bz) < z0 - g:
                continue
            if segment_rect(ax, az, bx, bz, x0, z0, x1, z1) < g:
                return False
        return True

    def props_clear(self, rect, gap, soft):
        """No prop within `gap` of the rectangle (`soft` for props that do not block)."""
        far = max(gap, soft)
        x0, z0, x1, z1 = rect
        for bx in range(int(math.floor((x0 - far) / 16)), int(math.floor((x1 + far) / 16)) + 1):
            for bz in range(int(math.floor((z0 - far) / 16)), int(math.floor((z1 + far) / 16)) + 1):
                for i in self._buckets.get((bx, bz), ()):
                    a0, b0, a1, b1 = self.props[i]
                    g = gap if self.blocks[i] else soft
                    if x0 - g < a1 and x1 + g > a0 and z0 - g < b1 and z1 + g > b0:
                        return False
        return True

    def points_clear(self, rect, gap, skip=None):
        return all(i == skip or point_rect(px, pz, *rect) >= r + gap for i, (px, pz, r) in enumerate(self.points))

    @staticmethod
    def spots_clear(x, z, side, spots, gap):
        h = side / 2 + gap
        return all(max(abs(x - ux), abs(z - uz)) >= h for ux, uz in spots)

    def routes_clear(self, rect, gap):
        x0, z0, x1, z1 = rect
        for ax, az, bx, bz in self.routes:
            if min(ax, bx) > x1 + gap or max(ax, bx) < x0 - gap or min(az, bz) > z1 + gap or max(az, bz) < z0 - gap:
                continue
            if segment_rect(ax, az, bx, bz, x0, z0, x1, z1) < gap:
                return False
        return True

    def fits(self, x, z, size, rally, tier=SPEC, hq=False, point=None):
        """The rules on the bare ground for a structure `size` across centred on (x, z), built from
        `rally`'s camp, with the margins of `tier` (hq: the HQ itself, which stands in the drop
        zone; 'edge': the HQ on a camp hemmed in by its roads, right against a road's edge but on
        no road cell; point: an outpost at that point)."""
        side = blocker_side(size)
        if self.openness(x, z, side) < 0 or self.cell(x, z) not in self.reach(*rally):
            return False
        foot, block = square(x, z, size), square(x, z, side)
        if hq:
            # The rally itself stays open ground.
            if point_rect(rally[0], rally[1], *block) < 2.0:
                return False
        else:
            for rx, rz in self.rallies:
                if math.hypot(x - rx, z - rz) < DROP_ZONE or point_rect(rx, rz, *block) < DROP_CORE:
                    return False
        unit_gap = 1.5 if hq else UNIT_GAP
        road = self.road_cells_clear(foot) if hq == 'edge' else self.road_clear(foot, min(HQ_ROAD_GAP, tier.road) if hq else tier.road)
        return (self.doorway_free(x, z, side) and road
                and self.props_clear(foot, tier.prop, tier.soft) and self.edge_clear(foot, tier.edge)
                and self.points_clear(foot, POINT_GAP, skip=point)
                and self.spots_clear(x, z, side, self.units, unit_gap) and self.spots_clear(x, z, side, self.spots, unit_gap)
                and self.routes_clear(block, ROUTE_GAP))


# ------------------------------------------------------------------------------------ the plan
class Plan:
    """The structures chosen so far on one version of a map, anchored on a copy of its grid."""

    def __init__(self, ground, rallies):
        self.ground = ground
        self.rallies = rallies
        self.grid = [row[:] for row in ground.blocked]
        self.taken = []      # (x, z, size, side, cell range)
        self.rules = []      # (rally, rules) each was taken under

    def spaced(self, x, z, size, side):
        rng = self.ground.cells(x, z, side)
        return all(math.hypot(x - tx, z - tz) >= max(size, tsize) + 3.0 and cells_apart(rng, trng) >= APART
                   for tx, tz, tsize, tside, trng in self.taken)

    def allows(self, x, z, size):
        """The rules that depend on the grid: apart from the other structures, leaning on one
        obstacle at most, no new doorway cell and no ground cut off."""
        g = self.ground
        side = blocker_side(size)
        if not self.spaced(x, z, size, side):
            return False
        a0, b0, a1, b1 = rng = g.cells(x, z, side)
        n = g.n
        touched = {g.label[gz][gx] for gz in range(max(0, b0 - 1), min(n, b1 + 2)) for gx in range(max(0, a0 - 1), min(n, a1 + 2))
                   if g.label[gz][gx]}
        if len(touched) > 1:
            return False
        self._fill(rng, True)
        try:
            for gz in range(max(0, b0 - 5), min(n, b1 + 6)):
                for gx in range(max(0, a0 - 5), min(n, a1 + 6)):
                    if not self.grid[gz][gx] and not g.narrow[gz][gx] and narrow_at(self.grid, gx, gz):
                        return False
            if touched:
                # Leaning on an obstacle can close a pocket: nothing reachable may be cut off.
                for rally in self.rallies:
                    before = g.reach(*rally)
                    after = flood(self.grid, g.cell(*rally))
                    if any(c not in after and not self.grid[c[1]][c[0]] for c in before):
                        return False
            return True
        finally:
            self._fill(rng, False)
            for tx, tz, tsize, tside, trng in self.taken:
                self._fill(trng, True)

    def _fill(self, rng, value):
        a0, b0, a1, b1 = rng
        for gz in range(max(0, b0), min(self.ground.n, b1 + 1)):
            for gx in range(max(0, a0), min(self.ground.n, a1 + 1)):
                self.grid[gz][gx] = value or self.ground.blocked[gz][gx]

    def take(self, x, z, size):
        side = blocker_side(size)
        rng = self.ground.cells(x, z, side)
        self.taken.append((x, z, size, side, rng))
        self._fill(rng, True)

    def remove(self, x, z):
        """Takes the structure at (x, z) away again."""
        k = next(i for i, t in enumerate(self.taken) if (t[0], t[1]) == (x, z))
        del self.taken[k]
        del self.rules[k]
        self.grid = [row[:] for row in self.ground.blocked]
        for *_, trng in self.taken:
            self._fill(trng, True)

    def drop(self):
        x, z, size, side, rng = self.taken.pop()
        self.rules.pop()
        self._fill(rng, False)
        for tx, tz, tsize, tside, trng in self.taken:
            self._fill(trng, True)

    def try_take(self, spots, size, rallies, **rules):
        """Takes every (x, z) of `spots` (a hardpoint and its mirror images), each for its rally,
        or none of them."""
        done = 0
        for (x, z), rally in zip(spots, rallies):
            if not (self.ground.fits(x, z, size, rally, **rules) and self.allows(x, z, size)):
                break
            self.take(x, z, size)
            self.rules.append((rally, rules))
            done += 1
        else:
            return True
        for _ in range(done):
            self.drop()
        return False

    def structures(self):
        """(x, z, blocker side) of everything taken."""
        return [(x, z, side) for x, z, size, side, rng in self.taken]

    def replay(self, ground):
        """The same structures, taken again one by one under the same rules on other ground (the
        battlefield once the clutter in their way is gone). Returns (the plan, None), or (None, the
        index of the first structure that no longer fits)."""
        plan = Plan(ground, self.rallies)
        for k, ((x, z, size, side, rng), (rally, rules)) in enumerate(zip(self.taken, self.rules)):
            if not plan.try_take([(x, z)], size, [rally], **rules):
                return None, k
        return plan, None

    def verify(self, name):
        """Raises when the filled plan cuts ground off or makes a new doorway anywhere."""
        g = self.ground
        for rally in self.rallies:
            after = flood(self.grid, g.cell(*rally))
            lost = [c for c in g.reach(*rally) if c not in after and not self.grid[c[1]][c[0]]]
            if lost:
                raise SystemExit(f'{name}: the filled hardpoints cut off {len(lost)} cells, e.g. {lost[:3]}')
        n = g.n
        new = [(x, z) for z in range(n) for x in range(n)
               if not self.grid[z][x] and not g.narrow[z][x] and narrow_at(self.grid, x, z)]
        if new:
            raise SystemExit(f'{name}: the filled hardpoints make new doorway cells, e.g. {new[:3]}')


# ------------------------------------------------------------------------------------ camps
def frame(hx, hz, ex, ez):
    """Unit forward (towards the enemy) and left vectors from the HQ."""
    fx, fz = ex - hx, ez - hz
    d = math.hypot(fx, fz)
    return (fx / d, fz / d), (-fz / d, fx / d)


def hq_spots(rally):
    """HQ candidates, best first: straight behind the rally (away from the map centre) at 12 m,
    then turned off that line, nearer or further, within 10-14 m."""
    rx, rz = rally
    d = math.hypot(rx, rz)
    bx, bz = rx / d, rz / d
    out = []
    for back in [k * 0.5 for k in range(int(HQ_BACK[0] * 2), int(HQ_BACK[1] * 2) + 1)]:
        for turn in range(-45, 46, 5):
            a = math.radians(turn)
            ux, uz = bx * math.cos(a) - bz * math.sin(a), bx * math.sin(a) + bz * math.cos(a)
            x, z = round((rx + ux * back) * 2) / 2, round((rz + uz * back) * 2) / 2
            if not HQ_BACK[0] - 1e-6 <= math.hypot(x - rx, z - rz) <= HQ_BACK[1] + 1e-6:
                continue
            out.append((abs(turn) + 3.0 * abs(back - 12.0) + (0.01 if turn > 0 else 0.0), x, z))
    out.sort()
    return [(x, z) for _, x, z in out]


def ring_spots(ground, hx, hz, forward, role, size):
    """Hardpoint candidates (score, distance from the HQ, x, z) on a 1 m lattice round the HQ,
    best first for `role`: the large towers at the key positions close to the HQ (flanking the
    drop zone, facing the enemy), the medium ones further out in between, the small ones on the
    outer ring and beside the lanes coming into the base, the utilities near the HQ, beside or
    behind it."""
    (fx, fz), (lx, lz) = forward
    side = blocker_side(size)
    lo, hi = RING_NEAR, TIERS[-1].ring
    out = []
    for ix in range(int(math.floor(hx - hi)), int(math.ceil(hx + hi)) + 1):
        for iz in range(int(math.floor(hz - hi)), int(math.ceil(hz + hi)) + 1):
            x, z = float(ix), float(iz)
            dx, dz = x - hx, z - hz
            r = math.hypot(dx, dz)
            if not lo <= r <= hi or ground.openness(x, z, side) < 0:
                continue
            theta = abs(math.degrees(math.atan2(dx * lx + dz * lz, dx * fx + dz * fz)))
            if role == 'large':
                score = 0.5 * abs(theta - 50.0) + 3.0 * abs(r - 25.0)
            elif role == 'medium':
                score = 0.5 * theta + 2.5 * abs(r - 32.0)
            elif role == 'small':
                score = 0.35 * theta + 2.0 * abs(r - 40.0) - (12.0 if ground.road_gap(square(x, z, size)) < 11.0 else 0.0)
            else:
                score = 2.0 * abs(r - 24.0) + 0.3 * max(0.0, 100.0 - theta)
            out.append((round(score, 6), 1 if dx * lx + dz * lz > 0 else 0, ix, iz, r))
    out.sort()
    return [(score, r, float(ix), float(iz)) for score, _, ix, iz, r in out]


PACK = 3.0      # score per open cell more than a doorway's width between a hardpoint and its nearest neighbour


def packed(ground, taken, candidates, size):
    """The candidates re-ranked so that each next hardpoint stands as close to the ones already
    placed as the doorway rule allows (four open cells), filling the camp instead of scattering."""
    if not taken:
        return candidates
    side = blocker_side(size)
    ranked = []
    for k, (score, r, x, z) in enumerate(candidates):
        rng = ground.cells(x, z, side)
        gap = min(cells_apart(rng, trng) for *_, trng in taken)
        ranked.append((score + PACK * min(max(0, gap - 4), 8), k))
    ranked.sort()
    return [candidates[k] for _, k in ranked]


SIZE_ORDER = {'large': 0, 'medium': 1, 'small': 2}


def slot_entry(kind, name, x, z, ex, ez):
    return {'x': x, 'z': z, 'kind': kind, 'size': name, 'facing': heading_to(x, z, ex, ez)}


def base_entry(team, hq, slots, enemy):
    """A camp as the map file writes it: the towers large, medium, small, then the utilities; each
    size most important first (nearest the enemy), as the base levels take the first of each."""
    hx, hz = hq
    ex, ez = enemy
    ordered = sorted(slots, key=lambda s: (s[0] != 'tower', SIZE_ORDER[s[1]], round(math.hypot(s[2] - ex, s[3] - ez), 3), s[2], s[3]))
    return {'team': team, 'hq': {'x': hx, 'z': hz, 'heading': heading_to(hx, hz, ex, ez)},
            'slots': [slot_entry(kind, name, x, z, ex, ez) for kind, name, x, z in ordered]}


def camp_needs():
    """(kind, size name, count) of every hardpoint a camp gets, in the order they are placed."""
    return [('tower', name, count) for name, count in CAMP_TOWERS] + [('utility', name, count) for name, count in CAMP_UTILITIES]


def place_camps(plan, teams, rallies, enemies):
    """The camps of `teams` (one, or two mirrored through the centre) in `plan`. Returns their map
    entries and which margin tier each part needed ({'hq': name, 'tower large': {tier: n}, ...});
    None when the HQ found no spot."""
    ground = plan.ground
    mirrored = len(teams) == 2
    tiers = {}

    def images(x, z):
        return [(x, z), mirror(x, z)] if mirrored else [(x, z)]

    hq = None
    for tier, rule in [(tier, True) for tier in TIERS] + [(TIERS[-1], 'edge')]:
        hq = next(((x, z) for x, z in hq_spots(rallies[0]) if plan.try_take(images(x, z), HQ_SIZE, rallies, tier=tier, hq=rule)), None)
        if hq is not None:
            tiers['hq'] = tier.name if rule is True else 'against a road edge'
            break
    if hq is None:
        return None
    hqs = images(*hq)
    near = [[spot] for spot in hqs]      # each camp's own structures, for packing
    slots = [[] for _ in teams]          # (kind, size name, x, z)

    def have(k, kind, name):
        return sum(1 for s in slots[k] if s[0] == kind and s[1] == name)

    def fill(kind, name, count, camp):
        """Hardpoints of one kind and size for one camp (camp None: every camp at once, as mirror images)."""
        k = 0 if camp is None else camp
        cx, cz = hqs[k]
        size = SIZES[name]
        candidates = ring_spots(ground, cx, cz, frame(cx, cz, *enemies[k]), name if kind == 'tower' else 'utility', size)
        for tier in TIERS:
            while have(k, kind, name) < count:
                mine = [t for t in plan.taken if (t[0], t[1]) in near[k]]
                for score, r, x, z in packed(ground, mine, [c for c in candidates if c[1] <= tier.ring], size):
                    spots = images(x, z) if camp is None else [(x, z)]
                    if plan.try_take(spots, size, rallies if camp is None else [rallies[camp]], tier=tier):
                        for i, (sx, sz) in enumerate(spots):
                            j = i if camp is None else camp
                            slots[j].append((kind, name, sx, sz))
                            near[j].append((sx, sz))
                        key = f'{kind} {name}'
                        label = tier.name if camp is None else tier.name + '/own'
                        tiers.setdefault(key, {})
                        tiers[key][label] = tiers[key].get(label, 0) + 1
                        break
                else:
                    break

    for kind, name, count in camp_needs():
        fill(kind, name, count, None)
        if mirrored:
            # Ground that differs between the camps can leave the mirror images short: each camp
            # then takes the rest where it has room; if one still has fewer, the other gives up
            # its last ones, so both sides always get as many.
            for camp in range(len(teams)):
                fill(kind, name, count, camp)
            fewest = min(have(k, kind, name) for k in range(len(teams)))
            for camp_slots in slots:
                while sum(1 for s in camp_slots if s[0] == kind and s[1] == name) > fewest:
                    last = max(i for i, s in enumerate(camp_slots) if s[0] == kind and s[1] == name)
                    plan.remove(camp_slots[last][2], camp_slots[last][3])
                    del camp_slots[last]
    entries = [base_entry(team, spot, slots[i], enemies[i]) for i, (team, spot) in enumerate(zip(teams, hqs))]
    return entries, tiers


def reuse_camp(plan, parts, rally):
    """Takes a camp found on another version of the map, part by part in the order and under the
    rules it was placed there (`parts`: (x, z, size, rules, clearing reach)), if every part of it
    still fits here."""
    for i, (x, z, size, rules, reach) in enumerate(parts):
        if not plan.try_take([(x, z)], size, [rally], **rules):
            for _ in range(i):
                plan.drop()
            return False
    return True


def camp_parts(report, base):
    """The parts of one camp of a planned map (see plan_bases), for reuse_camp."""
    mine = {(base['hq']['x'], base['hq']['z'])} | {(s['x'], s['z']) for s in base['slots']}
    return [part for part in report['taken'] if (part[0], part[1]) in mine]


def complete(base):
    """Whether a camp has every hardpoint it needs."""
    return all(sum(1 for s in base['slots'] if s['kind'] == kind and s['size'] == name) >= count
               for kind, name, count in camp_needs())


# ------------------------------------------------------------------------------------ outposts
def outpost_spots(ground, px, pz, r, axis, size, ring=OUTPOST_RING):
    """Outpost candidates round a point, best first: on its flanks (square to the camp axis), just
    outside the circle, on open ground."""
    ax, az = axis
    side = blocker_side(size)
    want = min(max(OUTPOST_RING[0], r + size / 2 + 1.0), OUTPOST_RING[1])
    lo, hi = ring
    out = []
    for ix in range(int(math.floor(px - hi)), int(math.ceil(px + hi)) + 1):
        for iz in range(int(math.floor(pz - hi)), int(math.ceil(pz + hi)) + 1):
            x, z = float(ix), float(iz)
            dx, dz = x - px, z - pz
            d = math.hypot(dx, dz)
            if not lo <= d <= hi or ground.openness(x, z, side) < 0:
                continue
            along = abs(dx * ax + dz * az) / d          # 0 on the flanks, 1 facing a camp
            out.append((round(60.0 * along + 2.0 * abs(d - want), 6), ix, iz))
    out.sort()
    return [(float(ix), float(iz)) for _, ix, iz in out]


def place_outposts(plan, rallies, pairs):
    """Outpost hardpoints at every capture point: a medium one on one flank and a small one on the
    other. `pairs` lists (point index, its mirror image's index, or None): a point and its mirror
    get mirrored hardpoints, so neither side's outposts stand better. Returns {point index: [slot,
    ...]} and how many needed each margin tier."""
    ground = plan.ground
    (ax, az), (bx, bz) = rallies[0], rallies[1]
    d = math.hypot(bx - ax, bz - az)
    axis = ((bx - ax) / d, (bz - az) / d)
    tiers = {}

    def choose(i, j):
        """The outpost of point i (and its image at point j): [(size name, x, z)] each."""
        px, pz, r = ground.points[i]
        mine, theirs = [], []
        for name in OUTPOST_SLOTS:
            size = SIZES[name]
            passes = [(tier, outpost_spots(ground, px, pz, r, axis, size)) for tier in TIERS]
            passes.append((TIERS[-1], outpost_spots(ground, px, pz, r, axis, size, OUTPOST_WIDE)))
            done = False
            for n, (tier, candidates) in enumerate(passes):
                for x, z in candidates:
                    # The second one on the other flank.
                    if any((x - px) * (sx - px) + (z - pz) * (sz - pz) > 0 for _, sx, sz in mine):
                        continue
                    if not plan.try_take([(x, z)], size, [rallies[0]], tier=tier, point=i):
                        continue
                    if j is not None and j != i:
                        qx, qz, _ = ground.points[j]
                        m = (qx - (x - px), qz - (z - pz))
                        if not plan.try_take([m], size, [rallies[1]], tier=tier, point=j):
                            plan.drop()
                            continue
                        theirs.append((name, *m))
                    mine.append((name, x, z))
                    label = 'wide ring' if n == len(passes) - 1 else tier.name
                    tiers[label] = tiers.get(label, 0) + (2 if j is not None and j != i else 1)
                    done = True
                    break
                if done:
                    break
        return mine, theirs

    found = {}
    for i, j in pairs:
        mine, theirs = choose(i, j)
        if j is None or j == i or len(mine) == len(OUTPOST_SLOTS):
            found[i] = mine
            if j is not None and j != i:
                found[j] = theirs
            continue
        # No mirrored pair fits: each point gets its own.
        for _, x, z in mine + theirs:
            plan.remove(x, z)
        found[i] = choose(i, None)[0]
        found[j] = choose(j, None)[0]
    out = {}
    for i, spots in found.items():
        px, pz, _ = ground.points[i]
        out[i] = [{'x': x, 'z': z, 'kind': 'tower', 'size': name, 'facing': heading_to(px, pz, x, z)} for name, x, z in spots]
    return out, tiers


def mirror_pairs(points):
    """(index, index of its mirror image through the centre or None) for every point, each pair once."""
    pairs, done = [], set()
    for i, (x, z, _) in enumerate(points):
        if i in done:
            continue
        j = min(range(len(points)), key=lambda k: math.hypot(points[k][0] + x, points[k][1] + z))
        if math.hypot(points[j][0] + x, points[j][1] + z) > 8.0 or j in done:
            j = None
        pairs.append((i, j))
        done.add(i)
        if j is not None:
            done.add(j)
    return pairs


# ------------------------------------------------------------------------------------ a map
class NoRoom(Exception):
    """No spot for a camp's HQ until its buildings in the way are pulled down."""


def plan_bases(name, props, rects, blocks, grid_of, lo, roads, boundary, points, rallies, camps, units=(),
               campaign=((), ()), outposts=True, reuse=None, demolish=None, crowded=None):
    """Plans one version of a battlefield: the camps of `camps` ([(team, rally, enemy rally)]: one,
    or two mirrored through the centre), and the outposts at `points` when `outposts`.
    `grid_of(kept)` fills the navigation grid with only the props at those indices; `rallies`
    are every side's rally (the drop zones); `reuse` is (a camp planned on another version, its
    parts: see camp_parts), taken as it is when it still fits. A camp still short of hardpoints once its clutter may go is
    planned again with its buildings in the way pulled down too (`demolish`: True or False to
    decide it up front, as the other versions of the map did). Returns (bases, {point index:
    outpost slots}, the indices of the props to take away, what each needed: {'camp': {...},
    'outposts': {...}, 'reused': bool, 'demolished': bool, 'crowded': [point indices], 'taken':
    [(x, z, size, rules, clearing reach)] of every structure, in the order placed})."""
    def again(demolish, crowded):
        return plan_bases(name, props, rects, blocks, grid_of, lo, roads, boundary, points, rallies, camps, units,
                          campaign, outposts, reuse, demolish, crowded)

    if demolish is None:
        try:
            result = again(False, crowded)
        except NoRoom:
            return again(True, crowded)
        return result if all(complete(b) for b in result[0]) else again(True, crowded)
    if crowded is None:
        # A point without room for its whole outpost has its buildings in the way pulled down too.
        result = again(demolish, ())
        short = tuple(i for i in range(len(points)) if outposts and len(result[1].get(i, [])) < len(OUTPOST_SLOTS))
        return again(demolish, short) if short else result
    ids = clearable(props, rects, [rally for _, rally, _ in camps], points if outposts else (), demolish, crowded)

    def ground(skip):
        kept = [i for i in range(len(props)) if i not in skip]
        return Ground(grid_of(kept), lo, [(rects[i], blocks[i]) for i in kept], roads, boundary, points, rallies,
                      units, campaign)

    plan = Plan(ground(set(ids)), rallies)
    report = {'reused': False, 'demolished': demolish, 'crowded': list(crowded)}
    bases = None
    if reuse is not None and len(camps) == 1 and reuse_camp(plan, reuse[1], camps[0][1]):
        bases, report['reused'] = [reuse[0]], True
    if bases is None:
        placed = place_camps(plan, [t for t, _, _ in camps], [r for _, r, _ in camps], [e for _, _, e in camps])
        if placed is None:
            if not demolish:
                raise NoRoom(name)
            raise SystemExit(f'{name}: no spot for the HQ behind the rally')
        bases, report['camp'] = placed
    found = {}
    if outposts and points:
        found, report['outposts'] = place_outposts(plan, rallies, mirror_pairs(points))
    # Only the clutter in the way goes, and the plan is checked again on what is left: a structure
    # that no longer fits has the clutter cleared further round it (only it, so each camp's ground
    # comes out the same whatever the other structures needed).
    structures = plan.structures()
    reaches = [(CLEAR_REACH, CLEAR_SOFT)] * len(structures)
    if report['reused']:
        # As far round each part as on the other version, so the camp's ground comes out the same.
        reaches = [part[4] for part in reuse[1]] + reaches[len(reuse[1]):]
    while True:
        gone = in_the_way(rects, blocks, ids, structures, reaches)
        final, failed = plan.replay(ground(set(gone)))
        if final is not None:
            break
        reach, soft = reaches[failed]
        if reach >= CLEAR_REACH * 3:
            raise SystemExit(f'{name}: the hardpoint at {structures[failed][:2]} no longer fits once the clutter is back')
        reaches[failed] = (reach + 4, soft + 4) if reach < CLEAR_REACH + 8 else (CLEAR_REACH * 3, CLEAR_REACH * 3)
    final.verify(name)
    report['taken'] = [(x, z, size, rules, reach)
                       for (x, z, size, side, rng), (rally, rules), reach in zip(plan.taken, plan.rules, reaches)]
    return bases, found, gone, report
