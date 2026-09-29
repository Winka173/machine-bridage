"""The siege fortress (Siege and Defend), built into a finished battlefield: it holds the enemy's
corner and 40-50 % of the play area (SHARE, measured inside the outline), in three rings round the
command HQ, and its set pieces.

  * The outer line (ring 1): a line across the battlefield, square to the diagonal between the
    camps, where the ground behind it is SHARE of the play area. Strongpoints along it (tower
    hardpoints behind sandbags), belts of tank traps and wire in front with gaps to drive through,
    and the three relay stations (stage 1) behind it. Everything the battlefield had behind the
    line stays: it is the fortress's outer works.
  * The walls (ring 2): an L of wall along x = RING and z = RING out to the outline, each arm with
    a main gate (steel doors that block until blown in) on the road to the keep and a sally port
    (an open gateway) far out on its flank, the long way round. Inside: the shield generators
    (stage 2), the super-gun, the line in (a rail line or a runway coming in over the edge), the
    fortress's stores and barracks (bounties), and the walls' tower hardpoints.
  * The keep (ring 3): walls round the command HQ in its back corner, a closed gate in its south
    wall and an open one in its west wall; the keep's large towers and utility hardpoints. The
    shield dome covers it while a generator stands.

Tower hardpoints are sized (small, medium, large, utility) and belong to a ring; the defender's
base loadout fills them in the game (BaseSystem.EstablishFortress). They stand on open ground off
the roads, the gate mouths and the line in, apart from each other and from anything solid.

Every piece is checked on the simulation's navigation grid: from the attacker's camp the HQ, the
relays, the generators, the super-gun, the line's stop and the defenders' rally can be reached with
every gate shut (through the sally ports) and with every hardpoint filled; with the sally ports
shut too the walls hold (the gates matter); and knocking a wall down never closes anything.

    fortify(L, map_id, theme, poly) -> (fortress block for the map file, siege rings)

It works on any battlefield of the current size whose enemy camp is in the north-east corner, so
new maps get their fortress from the same call (build_maps.main).
"""
import math
import random

import boundary as outline_tools
import hardpoints

CELL = 2.0
CLEARANCE = 1.5
SEGMENT = 8.0                  # a base_wall piece
GATE = 10.0                    # a gateway's clear opening
# The open gateways (the walls' two sally ports and the keep's west gate) are double: two gateway
# frames side by side, 18 m, seven walkable cells across (prompt 12). A 10 m one left three cells,
# one way at a time, and in Defend and Endless the defender's whole army and every wave came
# through them; the stuck report's worst spots were in their mouths.
SALLY = 18.0
YARD_WALLS, YARD_KEEP = 14.0, 14.0   # how deep the yard behind an open gateway stays clear: the walls', the keep's
KEEP_OPEN = (100.0, 118.0)     # the keep's open west gate: from, to (the wall pieces either side come out even)

HQ = (125.0, 125.0)            # the command HQ, in the keep's back corner (where the outline was carved round it)
RALLY = (108.0, 108.0)         # the defenders' camp: the keep's yard
KEEP = (83.4, 83.4, 134.0)     # the keep's west and south wall lines, and its north and east ones
KEEP_GATE = 113.0              # its gates' centre, in the west and south walls
RING = 40.0                    # the walls along x = RING and z = RING
RING_START = RING + 0.6        # the first wall piece starts here (a floodlight mast stands in the corner)
# The main gate three pieces out from the corner, centred on an odd metre (the middle of a 2 m
# navigation cell): its 10 m opening then leaves three whole walkable cells once blown in (the odd
# 1.4 m before it is a seam behind the gateway's pillar).
MAIN_GATE = 71.0
SHARE = 0.45                   # the fortress's share of the play area
SHARE_RANGE = (0.40, 0.50)
ROAD = 7.0

# The line in: which maps bring their reinforcements by train and which onto a runway (a new map
# takes its theme's default). It comes in over the north edge into the outer works west of the
# walls, its stop by the west sally port: the attackers see every train and aircraft come in.
ARRIVAL = {
    'ashfield': 'runway', 'dunebreak': 'runway', 'frostpeak': 'rail', 'ironport': 'rail', 'redrock': 'runway',
    'whiteout': 'rail', 'greenvale': 'runway', 'rustyard': 'rail', 'emberridge': 'runway', 'junglepass': 'rail',
    'skyhold': 'runway', 'metrocity': 'rail',
}
ARRIVAL_BY_THEME = {'harbor': 'rail', 'urban': 'rail', 'snow': 'rail', 'jungle': 'rail'}
RUNWAY_WIDTH = 16.0
RUNWAY_LENGTH = (60.0, 96.0)   # the runway's length inside the outline: at least, at most
RAIL_X = RING - 16.0           # the rail line comes down along this x
RAIL_END = 96.0                # to its buffer stop

SUPER_GUN = (95.0, 52.0)
GENERATORS = [(52.0, 112.0), (112.0, 52.0), (57.0, 57.0)]

# Tower hardpoints by ring: (size, kind, count, preferred spots); each goes to the nearest free
# spot of a preferred one, in order, until the ring has its count.
KEEP_SLOTS = [
    ('large', 'tower', 3, [(91.0, 91.0), (91.5, 127.5), (127.5, 91.5), (100.0, 100.0)]),
    ('medium', 'tower', 2, [(103.0, 128.5), (128.5, 103.0), (100.0, 118.0), (118.0, 100.0)]),
    ('medium', 'utility', 3, [(92.0, 101.0), (101.0, 92.0), (110.0, 128.0), (128.0, 110.0), (98.0, 110.0)]),
]
WALL_SLOTS = [
    ('large', 'tower', 2, [(54.0, 128.0), (128.0, 54.0), (46.0, 46.0), (60.0, 90.0), (90.0, 60.0)]),
    ('medium', 'tower', 5, [(46.0, 46.0), (54.0, 86.0), (86.0, 54.0), (60.0, 100.0), (100.0, 60.0), (78.0, 124.0),
                            (124.0, 78.0), (140.0, 64.0), (64.0, 140.0)]),
    ('small', 'tower', 5, [(52.0, 60.0), (60.0, 50.0), (78.0, 96.0), (96.0, 78.0), (46.0, 140.0), (140.0, 46.0),
                           (62.0, 80.0), (80.0, 62.0), (100.0, 140.0), (140.0, 100.0)]),
]
OUTER_SMALL = 8
OUTER_MEDIUM = 3

# What may make way for the fortress's pieces outside the walls: the battlefield's clutter.
CLUTTER = hardpoints.CAMP_CLUTTER
# Blocked ground each hardpoint size plans for (0.8 times the largest structure it takes).
BLOCK = {size: across * 0.8 for size, across in hardpoints.SIZES.items()}
SUPER_GUN_BLOCK = 8.0 * 1.8 * 0.8

BUILDINGS = ['warehouse', 'office_block', 'container_stack', 'garage', 'container_stack', 'container', 'radar_dome',
             'container', 'garage', 'container', 'office_block', 'garage', 'container_stack', 'ammo_dump', 'fuel_depot']


def share(poly, c):
    """The share of the play area (inside the outline) with x + z >= c."""
    total = hit = 0
    for x in range(-149, 150, 2):
        for z in range(-149, 150, 2):
            if outline_tools.inside(poly, x, z):
                total += 1
                if x + z >= c:
                    hit += 1
    return hit / max(1, total)


def outer_line(poly, target=SHARE):
    """The outer line x + z = c that leaves `target` of the play area behind it."""
    lo, hi = -80.0, 80.0
    for _ in range(24):
        mid = (lo + hi) / 2
        if share(poly, mid) > target:
            lo = mid
        else:
            hi = mid
    return round((lo + hi) / 2, 1)


def area_polygon(c, half):
    """The fortress's ground: the square's part behind the outer line, counter-clockwise."""
    return [(c - half, half), (half, c - half), (half, half)][::-1]


def rect_inside(poly, rect, margin=0.0):
    x0, z0, x1, z1 = rect
    xs, zs = (x0 - margin, (x0 + x1) / 2, x1 + margin), (z0 - margin, (z0 + z1) / 2, z1 + margin)
    return all(outline_tools.inside(poly, x, z) for x in xs for z in zs)


def rects_gap(a, b):
    dx = max(b[0] - a[2], a[0] - b[2], 0.0)
    dz = max(b[1] - a[3], a[1] - b[3], 0.0)
    return math.hypot(dx, dz)


def square(x, z, side):
    h = side / 2
    return (x - h, z - h, x + h, z + h)


class Fortress:
    """The pieces placed so far on one siege layout, and the checks."""

    def __init__(self, L, name, theme, poly, rally):
        self.L = L
        self.name = name
        self.theme = theme
        self.poly = poly
        self.rally = rally                  # the attacker's drop zone
        self.rng = random.Random(sum(map(ord, name)) * 131 + 7)
        self.keepout = []                   # rectangles nothing solid may stand in (lanes, gate mouths, the line in)
        self.slots = []                     # (size, kind, x, z, ring)
        self.blocks = []                    # (x, z, side) blocked ground of every hardpoint and the super-gun
        self.gates, self.sally = [], []     # rectangles of the closed gates, and of the sally ports
        self.walls = []                     # index into L.props of every wall piece
        self.relays, self.generators = [], []
        self.gun = None
        self.arrival = None

    # ---------------------------------------------------------------- geometry
    def solid(self):
        """Rectangles that block the way: blocking props and the hardpoints' ground."""
        out = [r for p, r in zip(self.L.props, self.L.rects) if hardpoints_blocks(p)]
        out += [square(x, z, side) for x, z, side in self.blocks]
        return out

    def free(self, rect, gap=2.0, soft=0.5, road=2.0, edge=6.0, keepout=True):
        """A rectangle clear of props (gap to blocking ones, soft to the rest), reserved ground,
        hardpoints, roads, the keep-out lanes and the outline's edge."""
        L = self.L
        if not rect_inside(self.poly, rect, edge):
            return False
        for p, (a0, b0, a1, b1) in zip(L.props, L.rects):
            g = gap if hardpoints_blocks(p) else soft
            if rect[0] - g < a1 and rect[2] + g > a0 and rect[1] - g < b1 and rect[3] + g > b0:
                return False
        for r in L.reserved:
            if rects_gap(rect, r) < gap:
                return False
        for x, z, side in self.blocks:
            if rects_gap(rect, square(x, z, side)) < max(gap, 4.0):
                return False
        if keepout and any(rects_gap(rect, k) < 0.5 for k in self.keepout):
            return False
        if road is not None and L.near_road(*rect, road):
            return False
        return True

    def clear_clutter(self, rect, reach=2.0):
        """Takes the battlefield's clutter (trees, craters, wrecks, loose rocks...) off a rectangle."""
        x0, z0, x1, z1 = rect
        keep = [(p, r) for p, r in zip(self.L.props, self.L.rects)
                if not (p['def'] in CLUTTER and r[0] < x1 + reach and r[2] > x0 - reach and r[1] < z1 + reach and r[3] > z0 - reach)]
        self.L.props = [p for p, _ in keep]
        self.L.rects = [r for _, r in keep]

    def spot(self, x, z, side, reach=14.0, clear=False, **rules):
        """The free spot for a square `side` across nearest (x, z), searched outwards; None if none."""
        for ring in range(0, int(reach / 2) + 1):
            steps = 1 if ring == 0 else ring * 8
            for k in range(steps):
                a = k * math.tau / steps + ring * 0.37
                px = round((x + math.cos(a) * ring * 2.0) * 2) / 2
                pz = round((z + math.sin(a) * ring * 2.0) * 2) / 2
                rect = square(px, pz, side)
                if clear and rect_inside(self.poly, rect, rules.get('edge', 6.0)):
                    saved = (self.L.props, self.L.rects)
                    self.clear_clutter(rect, 3.0)
                    if self.free(rect, **rules):
                        return px, pz
                    self.L.props, self.L.rects = saved
                    continue
                if self.free(rect, **rules):
                    return px, pz
        return None

    # ---------------------------------------------------------------- walls and gates
    def wall_run(self, axis, line, start, end, out=False):
        """Wall pieces end to end along a wall's centreline from `start` towards `end`; with `out`
        it goes on until a piece reaches past the outline (it runs into the terrain there)."""
        L = self.L
        u = start
        direction = 1 if end >= start else -1
        while True:
            a, b = u, u + direction * SEGMENT
            if not out and (b - end) * direction > 1e-6:
                break
            c = (a + b) / 2
            x, z = (c, line) if axis == 'x' else (line, c)
            if out and not outline_tools.inside(self.poly, *((a, line) if axis == 'x' else (line, a))):
                break
            L.force('base_wall', x, z, 0 if axis == 'x' else 90)
            self.walls.append(len(L.props) - 1)
            u = b
            if out and not outline_tools.inside(self.poly, *((b, line) if axis == 'x' else (line, b))):
                break
            if abs(u) > 400:
                break
        return u

    def gateway(self, axis, line, centre, closed, width=GATE):
        """A gateway frame in a GATE-wide opening; with `closed` its steel doors too. A wider
        opening (an open double gateway, SALLY) gets two frames side by side."""
        L = self.L
        x, z = (centre, line) if axis == 'x' else (line, centre)
        rot = 0 if axis == 'x' else 90
        frames = [0.0] if width <= GATE else [-width / 4, width / 4]
        for f in frames:
            L.force('base_gate', x + (f if axis == 'x' else 0.0), z + (f if axis == 'z' else 0.0), rot)
        h = width / 2
        rect = (x - h, z - 1, x + h, z + 1) if axis == 'x' else (x - 1, z - h, x + 1, z + h)
        if closed:
            L.force('fortress_gate', x, z, rot)
            self.gates.append(rect)
        else:
            self.sally.append(rect)
        # Nothing stands in the gate's mouth on either side; behind an open gateway the yard stays
        # clear deeper in (towards the keep), so the traffic through it has room to spread out
        # (prompt 12: a column queued in a lane between hardpoints and stores behind the sally port).
        m = 9.0
        inner = m if closed else (YARD_KEEP if line > RING + 1 else YARD_WALLS)
        self.keepout.append((x - h - 1, z - m, x + h + 1, z + inner) if axis == 'x' else (x - m, z - h - 1, x + inner, z + h + 1))

    def ring_wall(self, axis):
        """One arm of the wall ring: corner, three pieces, the main gate, pieces to the sally port
        far out, the sally port, and pieces on into the terrain."""
        line = RING
        u = self.wall_run(axis, line, RING_START, MAIN_GATE - GATE / 2)
        self.gateway(axis, line, MAIN_GATE, closed=True)
        # The sally port as far out as leaves a piece of wall between it and the outline.
        edge = MAIN_GATE
        while outline_tools.inside(self.poly, *((edge, line) if axis == 'x' else (line, edge))) and edge < 200:
            edge += 1.0
        pieces = max(2, int((edge - SEGMENT - SALLY - 3.0 - (MAIN_GATE + GATE / 2)) // SEGMENT))
        sally = MAIN_GATE + GATE / 2 + pieces * SEGMENT + SALLY / 2
        self.wall_run(axis, line, MAIN_GATE + GATE / 2, sally - SALLY / 2)
        self.gateway(axis, line, sally, closed=False, width=SALLY)
        self.wall_run(axis, line, sally + SALLY / 2, 1000.0, out=True)
        return sally

    def keep_walls(self):
        x0, z0, x1 = KEEP
        lo = x0 + 0.6
        # South wall: the closed gate; west wall: the open one (the keep's sally port, double).
        self.wall_run('x', z0, lo, KEEP_GATE - GATE / 2)
        self.gateway('x', z0, KEEP_GATE, closed=True)
        self.wall_run('x', z0, KEEP_GATE + GATE / 2, x1)
        a, b = KEEP_OPEN
        self.wall_run('z', z0, lo, a)
        self.gateway('z', z0, (a + b) / 2, closed=False, width=b - a)
        self.wall_run('z', z0, b, x1)
        # North and east walls behind the HQ, their odd metres a slit hidden behind it.
        for axis in ('x', 'z'):
            u = lo
            while u + SEGMENT <= HQ[0] + 1e-6:
                self.place_wall(axis, x1, u + SEGMENT / 2)
                u += SEGMENT
            u = x1 + 0.6
            while u - SEGMENT >= HQ[0] - 1e-6:
                self.place_wall(axis, x1, u - SEGMENT / 2)
                u -= SEGMENT
        self.L.force('floodlight_mast', x0, z0, 0)
        self.L.force('floodlight_mast', RING, RING, 0)

    def place_wall(self, axis, line, c):
        x, z = (c, line) if axis == 'x' else (line, c)
        self.L.force('base_wall', x, z, 0 if axis == 'x' else 90)
        self.walls.append(len(self.L.props) - 1)

    # ---------------------------------------------------------------- the grid checks
    def grid(self, gates=True, sally=False, walls=True, extra=()):
        """The navigation grid with the hardpoints filled; `gates`/`sally` shut those gateways,
        `walls` False knocks every wall piece down."""
        L = self.L
        props, rects = L.props, L.rects
        drop = set() if walls else set(self.walls)
        units = L.units
        try:
            L.props = [p for i, p in enumerate(props) if i not in drop and (gates or p['def'] != 'fortress_gate')]
            L.rects = [r for i, (p, r) in enumerate(zip(props, rects)) if i not in drop and (gates or p['def'] != 'fortress_gate')]
            if sally:
                for r in self.sally:
                    L.props = L.props + [{'def': 'fortress_gate', 'x': 0, 'z': 0}]
                    L.rects = L.rects + [r]
            L.units = units + [{'def': '_block', 'x': x, 'z': z, 'side': side} for x, z, side in self.blocks]
            return blocked_with_blocks(L, extra)
        finally:
            L.props, L.rects, L.units = props, rects, units

    def targets(self):
        L = self.L
        hq = next(p for p in L.props if p['def'] == 'command_hq')
        w, d = 8.0, 7.0
        out = [('rally', *RALLY), ('hq', hq['x'] - w, hq['z'] - d, hq['x'] + w, hq['z'] + d)]
        for kind in ('radar_station', 'shield_generator'):
            for p in L.props:
                if p['def'] == kind:
                    out.append((kind, p['x'] - 4, p['z'] - 4, p['x'] + 4, p['z'] + 4))
        if self.gun:
            h = SUPER_GUN_BLOCK / 2
            out.append(('super_gun', self.gun[0] - h, self.gun[1] - h, self.gun[0] + h, self.gun[1] + h))
        if self.arrival:
            out.append(('arrival', *self.arrival['stop']))
        return out

    def missing(self, blocked):
        return reach_targets(self.L, blocked, self.rally, self.targets())


def hardpoints_blocks(prop):
    from build_maps import PROPS
    return PROPS[prop['def']].get('blocks', False)


def blocked_with_blocks(L, extra=()):
    """Layout.blocked_grid with the fortress's hardpoints (pseudo units '_block' with their side) filled in."""
    real = [u for u in L.units if u['def'] != '_block']
    fake = [u for u in L.units if u['def'] == '_block']
    units = L.units
    L.units = real
    try:
        blocked = L.blocked_grid()
    finally:
        L.units = units
    n = len(blocked)
    lo = L.grid_lo()
    for u in fake:
        fill(blocked, lo, n, square(u['x'], u['z'], u['side']))
    for rect in extra:
        fill(blocked, lo, n, rect)
    return blocked


def fill(blocked, lo, n, rect):
    x0, z0, x1, z1 = rect
    nx, nz = len(blocked[0]), len(blocked)
    a0 = int(math.floor((x0 - CLEARANCE - lo) / CELL))
    a1 = int(math.floor((x1 + CLEARANCE - 1e-4 - lo) / CELL))
    b0 = int(math.floor((z0 - CLEARANCE - lo) / CELL))
    b1 = int(math.floor((z1 + CLEARANCE - 1e-4 - lo) / CELL))
    for gx in range(max(0, a0), min(nx, a1 + 1)):
        for gz in range(max(0, b0), min(nz, b1 + 1)):
            blocked[gz][gx] = True


def flood(blocked, lo, start):
    nx, nz = len(blocked[0]), len(blocked)
    sx, sz = int((start[0] - lo) / CELL), int((start[1] - lo) / CELL)
    seen = {(sx, sz)}
    todo = [(sx, sz)]
    while todo:
        gx, gz = todo.pop()
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            c = (gx + dx, gz + dz)
            if 0 <= c[0] < nx and 0 <= c[1] < nz and c not in seen and not blocked[c[1]][c[0]]:
                seen.add(c)
                todo.append(c)
    return seen


def reach_targets(L, blocked, start, targets):
    lo = L.grid_lo()
    seen = flood(blocked, lo, start)

    def cell(x, z):
        return int((x - lo) / CELL), int((z - lo) / CELL)

    missing = []
    for t in targets:
        if len(t) == 5:
            a0, b0 = cell(t[1] - 3.0, t[2] - 3.0)
            a1, b1 = cell(t[3] + 3.0, t[4] + 3.0)
            if not any((gx, gz) in seen for gx in range(a0, a1 + 1) for gz in range(b0, b1 + 1)):
                missing.append(t[0])
        elif cell(t[1], t[2]) not in seen:
            missing.append(t[0])
    return missing


# -------------------------------------------------------------------------------- the build
def fortify(L, name, theme, poly):
    """Builds the fortress into a finished siege layout (outline applied). Returns the map file's
    fortress block and siege rings."""
    from build_maps import clip_roads
    half = L.half
    attacker = L.teams[0]
    F = Fortress(L, name, theme, poly, attacker)
    L.failed = []
    L.teams = [attacker, RALLY]
    L.points = []
    c = outer_line(poly)
    got = share(poly, c)
    if not SHARE_RANGE[0] <= got <= SHARE_RANGE[1]:
        raise SystemExit(f'{name} siege: the fortress holds {got:.0%} of the battlefield')

    # The walls' ground: everything inside the ring goes, the roads through it too.
    L.remove(lambda a0, b0, a1, b1: a1 > RING - 4 and b1 > RING - 4)
    clip_roads(L, RING - 5, RING - 5, half + 10, half + 10)

    # Walls and gates.
    sally_x = F.ring_wall('x')
    sally_z = F.ring_wall('z')
    F.keep_walls()
    L.put('command_hq', *HQ, 0, pad=0.3)
    # Every gateway's mouth clear of whatever the battlefield had there (a rock on the road before a
    # main gate on Whiteout, a pylon and a container on Hydro Dam): the approach is the gate's (prompt 12).
    keep = [(p, r) for p, r in zip(L.props, L.rects)
            if p['def'] in OBJECTIVES or not any(r[0] < k[2] and r[2] > k[0] and r[1] < k[3] and r[3] > k[1] for k in F.keepout)]
    L.props, L.rects = [p for p, _ in keep], [r for _, r in keep]

    # Roads: from the outer line through each main gate to the keep's gates.
    kx, ky = KEEP[0], KEEP[1]
    L.road(ROAD, c - 150.0 + 40.0, MAIN_GATE, KEEP_GATE, MAIN_GATE, KEEP_GATE, ky + 12.0)
    L.road(ROAD, MAIN_GATE, c - 150.0 + 40.0, MAIN_GATE, KEEP_GATE, kx + 12.0, KEEP_GATE)
    L._samples = None
    # The roads to the main gates stay open from the outer line in (containers and a pylon closed
    # Hydro Dam's west one to the big hulls; prompt 12): nothing solid on them but the objectives.
    lanes = [(c - 150.0 + 40.0, MAIN_GATE - ROAD / 2 - 2.0, RING, MAIN_GATE + ROAD / 2 + 2.0),
             (MAIN_GATE - ROAD / 2 - 2.0, c - 150.0 + 40.0, MAIN_GATE + ROAD / 2 + 2.0, RING)]
    keep = [(p, r) for p, r in zip(L.props, L.rects)
            if p['def'] in OBJECTIVES or not any(r[0] < k[2] and r[2] > k[0] and r[1] < k[3] and r[3] > k[1] for k in lanes)]
    L.props, L.rects = [p for p, _ in keep], [r for _, r in keep]

    # The line in (a runway or a rail line) in the outer works by the west sally port.
    kind = ARRIVAL.get(name) or ARRIVAL_BY_THEME.get(theme, 'runway')
    for choice in (kind, 'rail' if kind == 'runway' else 'runway'):
        props, rects, keepout = list(L.props), list(L.rects), list(F.keepout)
        F.arrival = line_in(F, choice, c, half, sally_z)
        # Its stop must be reachable from the attacker's camp (the line is theirs to take).
        if F.arrival and not reach_targets(L, F.grid(gates=True), attacker, [('arrival', *F.arrival['stop'])]):
            break
        if F.arrival:
            print(f'warning: {name} siege: the {choice} line in cannot be reached; trying the other')
        L.props, L.rects, F.keepout = props, rects, keepout
        F.arrival = None

    # The super-gun and the shield generators.
    at = F.spot(*SUPER_GUN, SUPER_GUN_BLOCK + 3.0, reach=12.0, gap=3.0, road=2.0)
    if at:
        F.gun = at
        F.blocks.append((at[0], at[1], SUPER_GUN_BLOCK))
    else:
        L.failed.append(('super_gun', *SUPER_GUN))
    for x, z in GENERATORS:
        at = F.spot(x, z, 7.0, reach=12.0, gap=3.0, road=1.0)
        if at and L.put('shield_generator', *at, 0, pad=0.5):
            F.generators.append(at)
        else:
            L.failed.append(('shield_generator', x, z))

    # The keep's and the walls' hardpoints.
    for size, kind_, n, prefs in KEEP_SLOTS:
        place_many(F, size, kind_, 3, n, prefs, reach=8.0, gap=2.0, edge=3.0, road=1.0)
    for size, kind_, n, prefs in WALL_SLOTS:
        place_many(F, size, kind_, 2, n, prefs, reach=14.0, gap=3.0, road=2.0)

    # The outer line: relays, strongpoints and obstacle belts.
    outer_works(F, c, half)

    # The fortress's stores (they go up in a chain when hit) and its barracks in the ring's yard.
    stores(F)
    buildings(F)

    # Searchlight masts along the walls.
    for u in (60.0, 96.0, 124.0):
        for x, z in ((RING + 3.0, u), (u, RING + 3.0)):
            at = F.spot(x, z, 1.2, reach=6.0, gap=1.5, road=0.5)
            if at:
                L.put('floodlight_mast', *at, 0, pad=0.2)

    # The checks.
    bare = F.blocks
    F.blocks = []
    missing = F.missing(F.grid(gates=True))
    F.blocks = bare
    if missing:
        raise SystemExit(f'{name} siege: with the gates shut and no hardpoints, unreachable from the attacker camp: {missing}')
    missing = F.missing(F.grid(gates=True))
    # A hardpoint that cuts a route off goes again: the one whose going opens it (the latest first).
    while missing and F.slots:
        culprit = None
        for k in range(len(F.slots) - 1, -1, -1):
            size, kind_, x, z, ring = F.slots[k]
            kept = F.blocks
            F.blocks = [b for b in kept if (b[0], b[1]) != (x, z)]
            still = F.missing(F.grid(gates=True))
            F.blocks = kept
            if len(still) < len(missing):
                culprit = k
                break
        if culprit is None:
            culprit = len(F.slots) - 1
        size, kind_, x, z, ring = F.slots.pop(culprit)
        F.blocks = [b for b in F.blocks if (b[0], b[1]) != (x, z)]
        print(f'warning: {name} siege: {size} {kind_} hardpoint at ({x}, {z}) dropped: it cut off {missing}')
        missing = F.missing(F.grid(gates=True))
    if missing:
        raise SystemExit(f'{name} siege: with the gates shut, unreachable from the attacker camp: {missing}')
    missing = F.missing(F.grid(gates=False, walls=False))
    if missing:
        raise SystemExit(f'{name} siege: with the walls down, unreachable: {missing}')
    # Room for the biggest hull (prompt 12 C.2): the same places, over routes three cells wide.
    open_wide(F, c)
    sealed = F.grid(gates=True, sally=True)
    held = reach_targets(L, sealed, attacker, [('hq', HQ[0] - 8, HQ[1] - 7, HQ[0] + 8, HQ[1] + 7)])
    if not held:
        print(f'warning: {name} siege: the walls do not hold with every gateway shut (the gates do not matter)')

    for def_id, x, z in L.failed:
        print(f'warning: {name} siege: could not place {def_id} near ({x}, {z})')
    L.failed = []
    rings = [round(HQ[0] - RING, 2), round(HQ[0] - KEEP[0], 2)]
    block = {
        'hq': list(HQ),
        'area': [round(v, 2) for p in area_polygon(c, half) for v in p],
        'outerLine': c,
        'slots': [slot_entry(F, *s) for s in F.slots],
    }
    if F.gun:
        block['superGun'] = {'x': F.gun[0], 'z': F.gun[1], 'heading': hardpoints.heading_to(*F.gun, *attacker)}
    if F.arrival:
        block['arrival'] = F.arrival
    print(f'{name} siege: fortress holds {got:.1%} (outer line x + z = {c}), {len(F.slots)} hardpoints '
          f'({count(F, 1)}/{count(F, 2)}/{count(F, 3)} by ring), {len(F.relays)} relays, {len(F.generators)} generators, '
          f'{"super-gun, " if F.gun else ""}{F.arrival["kind"] if F.arrival else "no line in"}, sally ports at {sally_x:.0f}/{sally_z:.0f}')
    return block, rings


# ---------------------------------------------------------------------------------- the biggest hull
# What may go to open a way for the biggest hull, in the order it goes on a tie: the battlefield's
# clutter in the fortress's ground (trees, craters, wrecks) and a searchlight mast, then the outer
# line's obstacle belts, a store or a building of the yard, then a tower hardpoint of the walls or the
# keep. Walls, gates, objectives, terrain and the super-gun always stay.
WIDE_CLUTTER = {'floodlight_mast': 0, 'sandbags': 1, 'sandbag_wall': 1, 'tank_trap': 1, 'razor_wire': 1,
                'container': 1, 'container_stack': 1, 'garage': 1, 'warehouse': 1, 'office_block': 1,
                'radar_dome': 1, 'fuel_depot': 1, 'ammo_dump': 1, 'vehicle_hangar': 1}
WIDE_REACH = 6.0
FIRE_REACH = 15.0
# Never taken out: the stages' objectives (a relay is a radar station, also in the battlefield's buildings).
OBJECTIVES = {'radar_station', 'shield_generator', 'command_hq', 'base_wall', 'base_gate', 'fortress_gate'}


def open_wide(F, c, in_fort=None):
    """With every gate shut and every hardpoint filled, every place the attack needs (the defenders'
    drop zone, the relays, the generators, the HQ, the super-gun, the line's stop and both mouths of
    every gateway) must be reached from the attacker's camp over cells with open ground all round
    (a route three cells wide: room for the keep's guardian, and for two hulls to pass). Where one is
    not, the piece of the fortress's clutter whose going opens the most goes, one at a time, until
    every place is reached or nothing more helps (a warning: check_access.py will then fail the map).
    Before this, the walls' yard was open to a car everywhere but to the big hulls only through gaps
    of one or two cells, and the stuck report's jams were there."""
    from build_maps import PROPS, STATIC_FOOTPRINT, BUILDINGS as FIELD_BUILDINGS
    L = F.L
    lo = L.grid_lo()
    n = L.grid_n()
    nz = L.grid_nz()
    counts = [0] * (n * nz)
    # (In the fortress's ground: behind the diagonal outer line, or a long battlefield's own test.)
    if in_fort is None:
        def in_fort(x, z):
            return x + z > c - 4.0

    def cells(rect):
        x0, z0, x1, z1 = rect
        a0 = max(0, int(math.floor((x0 - CLEARANCE - lo) / CELL)))
        a1 = min(n - 1, int(math.floor((x1 + CLEARANCE - 1e-4 - lo) / CELL)))
        b0 = max(0, int(math.floor((z0 - CLEARANCE - lo) / CELL)))
        b1 = min(nz - 1, int(math.floor((z1 + CLEARANCE - 1e-4 - lo) / CELL)))
        return [gz * n + gx for gz in range(b0, b1 + 1) for gx in range(a0, a1 + 1)]

    pieces = []   # (kind order, what, cells, remove)
    outer = c
    for i, (prop, rect) in enumerate(zip(L.props, L.rects)):
        if not PROPS[prop['def']].get('blocks', False):
            continue
        cells_ = cells(rect)
        for k in cells_:
            counts[k] += 1
        cx, cz = (rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2
        # (Only in the fortress's ground: the battlefield outside stays as the other versions have it.)
        order = WIDE_CLUTTER.get(prop['def'], 0 if prop['def'] in CLUTTER else 1 if prop['def'] in FIELD_BUILDINGS else None)
        if prop['def'] in OBJECTIVES:
            order = None
        if order is not None and in_fort(cx, cz):
            pieces.append((order, ('prop', id(prop)), prop['def'], cells_, (prop, rect)))
    for u in L.units:
        side = STATIC_FOOTPRINT.get(u['def'])
        if side:
            cells_ = cells(square(u['x'], u['z'], side))
            for k in cells_:
                counts[k] += 1
            # The classic fortress's defences are map units: one on a causeway may go, last of all.
            if u.get('team') == 1 and in_fort(u['x'], u['z']):
                pieces.append((3, ('unit', id(u)), u['def'], cells_, u))
    for x, z, side in F.blocks:
        cells_ = cells(square(x, z, side))
        for k in cells_:
            counts[k] += 1
        slot = next((sl for sl in F.slots if (sl[2], sl[3]) == (x, z)), None)
        if slot:
            pieces.append((2, ('slot', (x, z)), f'{slot[0]} {slot[1]} hardpoint', cells_, (slot, (x, z, side))))
    if L.boundary:
        for gz in range(nz):
            for gx in range(n):
                if not outline_tools.inside(L.boundary, gx * CELL + lo + CELL / 2, gz * CELL + lo + CELL / 2):
                    counts[gz * n + gx] += 1

    def wide(gx, gz):
        if gx < 1 or gz < 1 or gx >= n - 1 or gz >= nz - 1:
            return False
        for dz in (-n, 0, n):
            base = gz * n + gx + dz
            if counts[base - 1] or counts[base] or counts[base + 1]:
                return False
        return True

    def cell_of(x, z):
        return int((x - lo) / CELL), int((z - lo) / CELL)

    targets = []
    for t in F.targets():
        if len(t) == 5:
            # (An objective is shot, not driven onto: a firing position 15 m off will do, as check_access.py has it.)
            r = WIDE_REACH if t[0] in ('camp', 'rally') else FIRE_REACH
            targets.append((t[0], t[1] - r, t[2] - r, t[3] + r, t[4] + r))
        else:
            targets.append((t[0], t[1] - WIDE_REACH, t[2] - WIDE_REACH, t[1] + WIDE_REACH, t[2] + WIDE_REACH))
    for prop in L.props:
        if prop['def'] == 'base_gate':
            ax, az = (0.0, 6.0) if prop.get('rot', 0) % 180 == 0 else (6.0, 0.0)
            for sgn in (1, -1):
                x, z = prop['x'] + sgn * ax, prop['z'] + sgn * az
                targets.append(('gateway mouth', x - WIDE_REACH, z - WIDE_REACH, x + WIDE_REACH, z + WIDE_REACH))
    boxes = []
    for name, x0, z0, x1, z1 in targets:
        a0, b0 = cell_of(x0, z0)
        a1, b1 = cell_of(x1, z1)
        boxes.append((name, a0, b0, a1, b1))

    sx, sz = cell_of(*F.rally)

    def missing():
        start = None
        best = float('inf')
        for gz in range(sz - 6, sz + 7):
            for gx in range(sx - 6, sx + 7):
                if 0 <= gx < n and 0 <= gz < nz and wide(gx, gz):
                    d = (gx - sx) ** 2 + (gz - sz) ** 2
                    if d < best:
                        best, start = d, (gx, gz)
        if start is None:
            return [b[0] for b in boxes], bytearray(n * nz)
        seen = bytearray(n * nz)
        todo = [start[1] * n + start[0]]
        seen[todo[0]] = 1
        while todo:
            k = todo.pop()
            gx, gz = k % n, k // n
            for nx, nz_ in ((gx + 1, gz), (gx - 1, gz), (gx, gz + 1), (gx, gz - 1)):
                j = nz_ * n + nx
                if 0 <= nx < n and 0 <= nz_ < nz and not seen[j] and wide(nx, nz_):
                    seen[j] = 1
                    todo.append(j)
        out = []
        for name, a0, b0, a1, b1 in boxes:
            if not any(seen[gz * n + gx] for gz in range(max(0, b0), min(nz - 1, b1) + 1) for gx in range(max(0, a0), min(n - 1, a1) + 1)):
                out.append(name)
        return out, seen

    def touches(cells_, seen):
        """A piece whose ground lies within two cells of the reached ground (only such a piece can extend it)."""
        for k in cells_:
            gx, gz = k % n, k // n
            for dz in range(-2, 3):
                for dx in range(-2, 3):
                    x, z = gx + dx, gz + dz
                    if 0 <= x < n and 0 <= z < nz and seen[z * n + x]:
                        return True
        return False

    now, seen = missing()
    removed = []
    digging, dug = 0, []
    # One piece at a time: the one that leaves the fewest places out of reach, else (a way out that
    # takes two pieces) the one that opens the most new wide ground; at most 14 pieces a fortress.
    while now and len(removed) < 14:
        best = None
        area = sum(seen)
        for piece in pieces:
            order, key, what, cells_, _ = piece
            if not touches(cells_, seen):
                continue
            for k in cells_:
                counts[k] -= 1
            out, reached = missing()
            left, grown = len(out), sum(reached) - area
            for k in cells_:
                counts[k] += 1
            score = (left, -grown, order, len(cells_))
            if (left < len(now) or (grown >= 12 and digging < 6)) and (best is None or score < best[0]):
                best = (score, piece)
        if best is None:
            print(f'warning: {F.name} siege: the biggest hull cannot reach {sorted(set(now))} and no clutter in the way can go')
            break
        order, key, what, cells_, keep = best[1]
        for k in cells_:
            counts[k] -= 1
        pieces.remove(best[1])
        if key[0] == 'prop':
            i = next(j for j, prop in enumerate(L.props) if id(prop) == key[1])
            del L.props[i]
            del L.rects[i]
        elif key[0] == 'unit':
            L.units = [u for u in L.units if id(u) != key[1]]
        else:
            F.slots = [sl for sl in F.slots if (sl[2], sl[3]) != key[1]]
            F.blocks = [b for b in F.blocks if (b[0], b[1]) != key[1]]
        removed.append(what)
        before = len(now)
        now, seen = missing()
        if len(now) < before:
            digging, dug = 0, []
        else:
            # Digging towards a place that takes two pieces: kept only if it gets there.
            digging += 1
            dug.append(best[1])
    # Pieces taken out while digging towards a place never reached go back where they were.
    for order, key, what, cells_, keep in dug:
        for k in cells_:
            counts[k] += 1
        if key[0] == 'prop':
            L.props.append(keep[0])
            L.rects.append(keep[1])
        elif key[0] == 'unit':
            L.units.append(keep)
        else:
            F.slots.append(keep[0])
            F.blocks.append(keep[1])
        removed.remove(what)
    # A hardpoint whose centre is not open ground (without its own tower) would have its tower moved
    # off it by the game: it goes (the game checks this too, MapConnectivityTests).
    for slot in list(F.slots):
        size_, kind_, x, z, ring = slot
        own = [b for b in F.blocks if (b[0], b[1]) == (x, z)]
        mine = set(k for b in own for k in cells(square(b[0], b[1], b[2])))
        gx, gz = cell_of(x, z)
        k = gz * n + gx
        if counts[k] - (1 if k in mine else 0) > 0:
            F.slots.remove(slot)
            F.blocks = [b for b in F.blocks if (b[0], b[1]) != (x, z)]
            print(f'warning: {F.name} siege: {size_} {kind_} hardpoint at ({x}, {z}) dropped: its centre is not open ground')
    if removed:
        print(f'{F.name} siege: for the biggest hull, took out {", ".join(removed)}')


def line_in(F, kind, c, half, sally):
    """The line in, in the outer works west of the walls: a runway along the north edge whose
    aircraft stops short of the west sally port, or a rail line coming down from the north edge
    to a buffer stop by it. Its ground is cleared of the battlefield's clutter and buildings and
    kept open. None when the map has no room for it."""
    L = F.L
    if kind == 'runway':
        best = None
        for z in range(int(half - 12), 90, -2):
            # The longest run west from the walls inside the outline (the width clear of the edge).
            x = RING - 12.0
            while x > -half and x + z >= c + 12 and rect_inside(F.poly, (x - 2, z - RUNWAY_WIDTH / 2, x, z + RUNWAY_WIDTH / 2), 3.0):
                x -= 2.0
            run = RING - 12.0 - x
            if run >= RUNWAY_LENGTH[0] and (best is None or min(run, RUNWAY_LENGTH[1]) > best[1] + 3.0):
                best = (float(z), min(run, RUNWAY_LENGTH[1]))
        if best is None:
            return None
        z, run = best
        east = RING - 12.0
        west = east - run
        rect = (west, z - RUNWAY_WIDTH / 2, east, z + RUNWAY_WIDTH / 2)
        clear_ground(F, rect)
        F.keepout.append((rect[0] - 2, rect[1] - 2, rect[2] + 2, rect[3] + 2))
        stop = (east - 10.0, z)
        # It lands from beyond the west edge of the battlefield and rolls east to its stop.
        return {'kind': 'runway', 'path': [-half - 60.0, z, west, z, east, z], 'stop': [stop[0], stop[1]], 'heading': 90,
                'width': RUNWAY_WIDTH}
    # Rail: from beyond the north edge straight down to a buffer stop, the platform on its east side.
    x = RAIL_X
    top = RAIL_END
    while outline_tools.inside(F.poly, x, top + 2.0) and top < half + 20:
        top += 2.0
    if top - RAIL_END < 30.0:
        return None
    rect = (x - 3.0, RAIL_END - 2.0, x + 9.0, top + 2.0)
    clear_ground(F, rect)
    F.keepout.append((rect[0] - 2, rect[1] - 2, rect[2] + 2, rect[3] + 2))
    stop = (x + 6.0, RAIL_END + 12.0)
    return {'kind': 'rail', 'path': [x, half + 60.0, x, RAIL_END], 'stop': [stop[0], stop[1]], 'heading': 90}


def clear_ground(F, rect):
    """Takes everything but terrain off a rectangle (the line in's ground)."""
    x0, z0, x1, z1 = rect
    keep = [(p, r) for p, r in zip(F.L.props, F.L.rects)
            if p['def'] in hardpoints.TERRAIN or not (r[0] < x1 + 1 and r[2] > x0 - 1 and r[1] < z1 + 1 and r[3] > z0 - 1)]
    F.L.props = [p for p, _ in keep]
    F.L.rects = [r for _, r in keep]


def place_many(F, size, kind, ring, count, prefs, **rules):
    placed = 0
    for x, z in prefs:
        if placed >= count:
            break
        if place_slot(F, size, kind, x, z, ring, quiet=True, **rules):
            placed += 1
    if placed < count:
        F.L.failed.append((f'{count - placed} {size} {kind} hardpoints of ring {ring}', *prefs[0]))
    return placed


def count(F, ring):
    return sum(1 for s in F.slots if s[4] == ring)


def slot_entry(F, size, kind, x, z, ring):
    entry = {'x': x, 'z': z, 'size': size}
    if kind == 'utility':
        entry['kind'] = 'utility'
    entry['facing'] = hardpoints.heading_to(x, z, *F.rally)
    entry['ring'] = ring
    return entry


def place_slot(F, size, kind, x, z, ring, reach=12.0, clear=False, quiet=False, **rules):
    side = BLOCK[size]
    at = F.spot(x, z, side, reach=reach, clear=clear, **rules)
    if at is None:
        if not quiet:
            F.L.failed.append((f'{size} {kind} hardpoint', x, z))
        return None
    F.slots.append((size, kind, at[0], at[1], ring))
    F.blocks.append((at[0], at[1], side))
    return at


def outer_works(F, c, half):
    """The outer line x + z = c: relay stations behind it, strongpoints (tower hardpoints behind
    sandbags) along it, belts of tank traps and wire in front with gaps between them."""
    L = F.L
    mx = my = c / 2
    u = (math.sqrt(0.5), -math.sqrt(0.5))       # along the line
    n = (math.sqrt(0.5), math.sqrt(0.5))        # into the fortress

    def at(t, off):
        return mx + u[0] * t + n[0] * off, my + u[1] * t + n[1] * off

    def deep(size, kind, t, depths, reach):
        for off in depths:
            x, z = at(t, off)
            if outline_tools.inside(F.poly, x, z) and place_slot(F, size, kind, x, z, 1, reach=reach, clear=True, quiet=True,
                                                                 gap=2.5, road=2.0):
                return True
        return False

    # Relays: in the middle and on either flank, well behind the line.
    for base in (-50.0, 0.0, 50.0):
        placed = False
        for t, off in ((tt, oo) for tt in (base, base * 0.8, base * 1.2, base * 0.6) for oo in (22.0, 30.0, 16.0, 40.0, 50.0)):
            x, z = at(t, off)
            spot = F.spot(x, z, 9.2, reach=18.0, clear=True, gap=3.0, road=1.0) if outline_tools.inside(F.poly, x, z) else None
            if spot and L.put('radar_station', *spot, 0, pad=0.5):
                F.relays.append(spot)
                placed = True
                break
        if not placed:
            L.failed.append(('radar_station', *at(base, 26.0)))
    # Strongpoints: a small tower hardpoint every 26 m along the line (a medium one at every third),
    # as close behind it as there is room, sandbags in front.
    small = medium = 0
    for k, t in enumerate(range(-156, 157, 26)):
        if not outline_tools.inside(F.poly, *at(t, 10.0)):
            continue
        if medium < OUTER_MEDIUM and k % 3 == 1 and deep('medium', 'tower', float(t), (15.0, 22.0, 30.0), 10.0):
            medium += 1
        if small < OUTER_SMALL and deep('small', 'tower', t + 7.0, (9.0, 14.0, 20.0, 27.0), 9.0):
            small += 1
        for dt in (-4.0, 4.0):
            x, z = at(t + dt, 3.0)
            rect = square(x, z, 4.0)
            F.clear_clutter(rect, 1.0)
            if F.free(rect, gap=1.0, soft=0.3, road=1.0, edge=4.0):
                L.put('sandbags', x, z, 0 if (k + (dt > 0)) % 2 else 90, pad=0.2)
    # More where the line still has room.
    t = -143.0
    while (small < OUTER_SMALL or medium < OUTER_MEDIUM) and t < 150:
        if medium < OUTER_MEDIUM and deep('medium', 'tower', t, (18.0, 26.0, 34.0), 10.0):
            medium += 1
        elif small < OUTER_SMALL and deep('small', 'tower', t, (12.0, 18.0, 26.0, 34.0), 9.0):
            small += 1
        t += 17.0
    if small < OUTER_SMALL or medium < OUTER_MEDIUM:
        L.failed.append((f'outer line: {OUTER_SMALL - small} small and {OUTER_MEDIUM - medium} medium hardpoints', mx, my))
    # Obstacle belts in front of the line: short runs with gaps a column can drive through.
    for t in range(-160, 161, 16):
        if (t // 16) % 3 == 0:
            continue
        x, z = at(float(t), -8.0)
        kind = 'tank_trap' if (t // 16) % 2 else 'razor_wire'
        w, d = (1.6, 1.6) if kind == 'tank_trap' else (8.0, 1.0)
        rot = 0 if kind == 'tank_trap' else (0 if t % 32 else 90)
        rect = square(x, z, max(w, d))
        F.clear_clutter(rect, 0.5)
        if F.free(rect, gap=2.0, soft=0.3, road=1.5, edge=4.0):
            if kind == 'tank_trap':
                for dx, dz in ((0, 0), (2.6, -2.6), (-2.6, 2.6)):
                    L.put('tank_trap', x + dx, z + dz, 0, pad=0.3)
            else:
                L.put('razor_wire', x, z, rot, pad=0.3)
    # Field positions behind the strongpoints: camo nets, stores, tents.
    for t in range(-120, 121, 60):
        x, z = at(float(t) + 15.0, 20.0)
        for kind in ('camo_net', 'supply_pile', 'command_tent'):
            spot = F.spot(x, z, 6.0, reach=8.0, gap=2.0, road=1.0)
            if spot:
                L.put(kind, *spot, 0, pad=0.5)
                x, z = spot[0] + 7.0, spot[1] - 7.0


STORES = [
    ('fuel_depot', 2, [(62.0, 96.0), (96.0, 62.0), (130.0, 76.0), (76.0, 130.0), (140.0, 50.0), (50.0, 140.0)]),
    ('ammo_dump', 2, [(48.0, 96.0), (96.0, 48.0), (140.0, 62.0), (62.0, 140.0), (120.0, 46.0), (46.0, 120.0)]),
    ('vehicle_hangar', 2, [(104.0, 142.0), (142.0, 104.0), (80.0, 142.0), (142.0, 80.0), (60.0, 80.0), (80.0, 60.0)]),
]


def stores(F):
    """Fuel depots, ammunition dumps and vehicle hangars in the walls' yard, off the lanes: the
    fortress's stores, each a bounty for the attacker and a blast when it goes."""
    L = F.L
    before = set(F.missing(F.grid(gates=True)))
    for kind, count, prefs in STORES:
        placed = 0
        for x, z in prefs:
            if placed >= count:
                break
            w, d = L.size(kind, 0)
            at = F.spot(x, z, max(w, d), reach=10.0, gap=3.0, road=1.5)
            if at and L.put(kind, *at, 0, pad=0.5):
                if set(F.missing(F.grid(gates=True))) - before:
                    L.remove(lambda a0, b0, a1, b1, hx=at[0], hz=at[1]: a0 <= hx <= a1 and b0 <= hz <= b1)
                    continue
                placed += 1
        if placed < count:
            L.failed.append((f'{count - placed} {kind}', *prefs[0]))


def buildings(F, count=12):
    """Stores and barracks in the ring's yard (bounties for the attacker, cover for the
    defenders), flush against something solid or well clear of it, off the lanes."""
    from build_maps import Layout, alley_with, hugging
    L = F.L
    rng = F.rng
    x0 = KEEP[0]
    placed = 0
    tries = 0
    before = set(F.missing(F.grid(gates=True)))
    while placed < count and tries < 4000:
        tries += 1
        kind = rng.choice(BUILDINGS)
        rot = rng.choice((0, 90))
        w, d = Layout.size(kind, rot)
        anchors = [r for r in F.solid() if (r[0] + r[2]) / 2 >= RING - 1 and (r[1] + r[3]) / 2 >= RING - 1
                   and not (x0 < (r[0] + r[2]) / 2 < KEEP[2] and x0 < (r[1] + r[3]) / 2 < KEEP[2])]
        if not anchors:
            break
        x, z = hugging(rng, rng.choice(anchors), w, d)
        x, z = round(x * 2) / 2, round(z * 2) / 2
        rect = (x - w / 2, z - d / 2, x + w / 2, z + d / 2)
        if x < RING + 2 or z < RING + 2 or (x0 - 2 < x and x0 - 2 < z):
            continue
        if not F.free(rect, gap=0.4, soft=0.3, road=1.0, edge=3.0):
            continue
        if alley_with(L, *rect) is not None:
            continue
        if L.put(kind, x, z, rot, pad=0.3):
            if set(F.missing(F.grid(gates=True))) - before:
                L.remove(lambda a0, b0, a1, b1, hx=x, hz=z: a0 <= hx <= a1 and b0 <= hz <= b1)
                continue
            placed += 1
    return placed
