"""Long battlefields for Siege, Defend, Endless and the weekly fortress (prompt 17 A-B).

A long battlefield is 300 m across and 480 m along the attack: the map's own 300 m battlefield
(its Conquest version: the ground, the dressing, the attacker's camp and the three objectives,
all where they always were, so campaign coordinates still hold) and 180 m more to the north,
where the defender's layered base stands behind a buffer zone. The long axis runs from the
attacker's camp in the south-west to the base; the flanks are no wider than the square's.

  * The square's own outline is kept south of SEAM; north of it the long battlefield has a new
    outline of its own (the theme's strip and noise), blended into the old flanks over BLEND
    metres. The dressing the square had outside its old outline there (its decor: trees, rocks,
    houses beyond the edge) comes back as real props where the new outline takes it in: the
    ground that was scenery before is played on now.
  * The layered base (B.1): the buffer zone (firing positions on the attacker's side, dragon's
    teeth, anti-tank ditches and wire, with gaps a column can drive through), the forward works
    (the three relays and forward strongpoints), the outer wall across the whole width with a
    closed main gate and two open sally ports, the yard (shield generators, the super-gun,
    stores, barracks, the line in), the inner wall (the keep: a closed gate in its south wall,
    open gateways in its side walls), then the command HQ and the defenders' drop zone in the
    keep. Each layer has its own hardpoints, labelled by place (outer gate, outer wall, yard,
    inner wall, beside the HQ, utility; the forward ones "forward"), listed most important
    first per size so a lower HQ level opens the best ones (balance.json base.longLevels).
  * SiegeMode reads the rings from the map's "rings" polygons (ring 2 inside the outer wall,
    ring 3 inside the keep); "siegeRings" are the axial distances from the HQ for older readers.

Every piece is checked on the simulation's navigation grid as fortress.py does: with the gates shut
(through the sally ports) and every hardpoint filled the HQ, the relays, the generators, the
super-gun, the line's stop and the defenders' drop zone can be reached from the attacker's camp;
with the walls down too; and, for the biggest hull, over routes three cells wide (open_wide).

    python Tools/maps/longmap.py [map ids...]   (no ids: every map with a siege version)

Writes Resources/Data/maps/<id>_long.json and runs check_access.py on each file. A new map (such as
Lighthouse Bay) gets its long version from the same call once it is in build_maps.MAPS.
"""
import copy
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import boundary as outline_tools  # noqa: E402
import build_maps as B  # noqa: E402
import fortress as F_  # noqa: E402
import hardpoints  # noqa: E402

# ------------------------------------------------------------------------------------ geometry
WEST, SOUTH, EAST, NORTH = -150.0, -150.0, 150.0, 330.0
WIDTH, LENGTH = EAST - WEST, NORTH - SOUTH          # 300 x 480
SEAM = 118.0            # south of this the square keeps its own outline
BLEND = 30.0            # north of the seam the flanks' edge goes over to the strip's over this far
EDGE_MAX = (12.0, 11.0)  # the strip's edge cuts in at most this far: flanks, north (the HQ stands near it)
EDGE_MIN = 3.0

# The layered base, in the long battlefield's coordinates.
BUFFER = (150.0, 190.0)     # the buffer zone (z): firing positions, dragon's teeth, ditches, wire
TEETH_Z = 168.0             # the dragon's teeth belt (two staggered rows)
DITCH_Z = 178.0             # the anti-tank ditches
WIRE_Z = 185.0              # the wire
FIRING_Z = 140.0            # the firing positions (the attacker's high ground), on the buffer's near side
OUTER = 218.0               # the outer wall along z = OUTER, across the whole width
MAIN_GATE = -1.0            # its closed main gate (an odd metre: three whole cells once blown in)
SALLY = (-103.0, 101.0)     # its open sally ports (double, F_.SALLY wide)
KEEP_Z = 266.0              # the inner wall: the keep's south wall
KEEP_X = (-46.6, 44.6)      # the keep's west and east walls (their pieces come out even from the gate)
KEEP_GATE = -1.0            # the keep's closed gate
KEEP_SIDE = (282.6, 300.6)  # the open gateways in the keep's side walls: from, to (along z)
HQ = (0.0, 305.0)
RALLY = (0.0, 284.0)        # the defenders' drop zone: the keep's yard, in front of the HQ
ROAD = 7.0
GATE, SALLY_W = F_.GATE, F_.SALLY
SIEGE_RINGS = [round(HQ[1] - OUTER, 2), round(HQ[1] - KEEP_Z, 2)]
# Where the attack's reinforcements land once a ring has fallen (B.2): in front of the buffer after
# the forward works, in front of the outer wall once the yard is taken... (stage 2 and stage 3).
FORWARD_DROPS = [(0.0, 128.0), (-1.0, 196.0)]

# The base's hardpoints (B.1, B.4): size, kind, place, ring, preferred spots. Per size the list is
# in the order of importance (the i-th small slot opens at the level the table gives i + 1 small
# slots): the gates first, then the inner wall, the outer wall, the yard, the HQ.
BASE_SLOTS = [
    ('small', 'tower', 'outer_gate', 2, [(-16.0, 226.0), (14.0, 226.0)]),
    ('small', 'tower', 'inner_wall', 3, [(-16.0, 274.0), (14.0, 274.0)]),
    ('small', 'tower', 'outer_wall', 2, [(-60.0, 225.0), (58.0, 225.0)]),
    ('small', 'tower', 'yard', 2, [(-128.0, 256.0), (126.0, 256.0)]),
    ('medium', 'tower', 'outer_gate', 2, [(-30.0, 230.0)]),
    ('medium', 'tower', 'inner_wall', 3, [(28.0, 278.0)]),
    ('medium', 'tower', 'outer_wall', 2, [(-82.0, 227.0), (80.0, 227.0)]),
    ('medium', 'tower', 'yard', 2, [(62.0, 250.0)]),
    ('large', 'tower', 'yard', 2, [(-88.0, 250.0), (88.0, 250.0)]),
    ('large', 'tower', 'hq_side', 3, [(-24.0, 298.0)]),
    ('medium', 'utility', 'hq_side', 3, [(22.0, 298.0), (-26.0, 314.0), (24.0, 314.0), (-32.0, 284.0)]),
]
# The forward works' strongpoints (ring 1), towers repeated from the loadout (no HQ level).
FORWARD_SLOTS = [
    ('medium', [(-68.0, 204.0), (66.0, 204.0)]),
    ('small', [(-128.0, 200.0), (-94.0, 198.0), (-34.0, 204.0), (32.0, 204.0), (92.0, 198.0), (126.0, 200.0)]),
]
RELAYS = [(-52.0, 197.0), (12.0, 199.0), (56.0, 197.0)]
GENERATORS = [(-86.0, 286.0), (84.0, 284.0), (38.0, 244.0)]
SUPER_GUN = (-52.0, 244.0)
FIRING = [(-112.0, FIRING_Z), (-46.0, FIRING_Z - 4.0), (44.0, FIRING_Z - 4.0), (110.0, FIRING_Z)]
STORES = [
    ('fuel_depot', 2, [(-120.0, 238.0), (120.0, 238.0), (-100.0, 312.0), (104.0, 272.0)]),
    ('ammo_dump', 2, [(-72.0, 312.0), (126.0, 282.0), (-128.0, 288.0), (70.0, 272.0)]),
    ('vehicle_hangar', 2, [(-110.0, 272.0), (112.0, 316.0), (-70.0, 238.0), (100.0, 238.0)]),
]
BUILDINGS = F_.BUILDINGS
RUNWAY_Z = 308.0            # a runway along the east yard's north side, landing from beyond the east edge
RAIL_X = -130.0             # a rail line down the west yard from beyond the north edge
RAIL_END = 274.0


def in_strip_fort(x, z):
    """The fortress's ground on a long battlefield: the buffer zone and everything behind it."""
    return z > BUFFER[0] - 4.0


# ------------------------------------------------------------------------------------ the outline
RES = 1.0
NX, NZ = int(WIDTH / RES), int(LENGTH / RES)


def _centre(gx, gz):
    return WEST + (gx + 0.5) * RES, SOUTH + (gz + 0.5) * RES


def _row_intervals(poly, z):
    """The x spans of a row inside a polygon (even-odd, as boundary.inside counts)."""
    xs = []
    n = len(poly)
    for i in range(n):
        (ax, az), (bx, bz) = poly[i], poly[i - 1]
        if (az > z) != (bz > z):
            xs.append(ax + (z - az) * (bx - ax) / (bz - az + 1e-12))
    xs.sort()
    return [(xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2)]


def long_outline(map_id, old_poly):
    """The long battlefield's outline, counter-clockwise: the square's own south of SEAM, the strip's
    north of it (its edge cut in by the map's base depth and noise, capped), blended over BLEND."""
    base, noise, scale, _ = outline_tools.SHAPES.get(map_id, (4.0, 6.0, 20.0, []))
    base, noise, scale = base * outline_tools.DEPTH, noise * outline_tools.DEPTH, scale * outline_tools.SCALE
    seed = len(map_id) * 31 + 7
    # How far in the square's outline stands on each flank at the seam.
    spans = _row_intervals(old_poly, SEAM)
    west_seam = (spans[0][0] - WEST) if spans else base
    east_seam = (EAST - spans[-1][1]) if spans else base

    def depth(u, v, cap):
        n = outline_tools.fbm(u / scale + 50.0, v / scale + 50.0, seed) * 2.0
        return max(EDGE_MIN, min(cap, base + (n - 1.0) * noise))

    carved = [[True] * NX for _ in range(NZ)]
    for gz in range(NZ):
        z = SOUTH + (gz + 0.5) * RES
        if z < SEAM:
            for a, b in _row_intervals(old_poly, z):
                for gx in range(max(0, int(math.ceil((a - WEST) / RES - 0.5))), min(NX, int(math.floor((b - WEST) / RES - 0.5)) + 1)):
                    carved[gz][gx] = False
            continue
        t = min(1.0, (z - SEAM) / BLEND)
        t = t * t * (3 - 2 * t)
        dw = west_seam + (depth(WEST, z, EDGE_MAX[0]) - west_seam) * t
        de = east_seam + (depth(EAST, z, EDGE_MAX[0]) - east_seam) * t
        for gx in range(NX):
            x = WEST + (gx + 0.5) * RES
            dn = depth(x, NORTH, EDGE_MAX[1])
            carved[gz][gx] = not (x - WEST > dw and EAST - x > de and NORTH - z > dn)
    # Round off spikes (as boundary.carve_mask), then one connected battlefield with no pockets.
    for _ in range(2):
        nxt = [row[:] for row in carved]
        for gz in range(NZ):
            for gx in range(NX):
                count = 0
                for dz in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        x, z = gx + dx, gz + dz
                        count += 1 if (x < 0 or z < 0 or x >= NX or z >= NZ or carved[z][x]) else 0
                nxt[gz][gx] = count >= 5
        carved = nxt
    carved = _one_region(carved)
    return _trace(carved)


def _one_region(carved):
    seen = [[False] * NX for _ in range(NZ)]
    best = []
    for sz in range(NZ):
        for sx in range(NX):
            if carved[sz][sx] or seen[sz][sx]:
                continue
            region, todo = [], [(sx, sz)]
            seen[sz][sx] = True
            while todo:
                gx, gz = todo.pop()
                region.append((gx, gz))
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    x, z = gx + dx, gz + dz
                    if 0 <= x < NX and 0 <= z < NZ and not seen[z][x] and not carved[z][x]:
                        seen[z][x] = True
                        todo.append((x, z))
            if len(region) > len(best):
                best = region
    open_cells = [[False] * NX for _ in range(NZ)]
    for gx, gz in best:
        open_cells[gz][gx] = True
    outside = [[False] * NX for _ in range(NZ)]
    todo = [(gx, gz) for gx in range(NX) for gz in (0, NZ - 1)] + [(gx, gz) for gz in range(NZ) for gx in (0, NX - 1)]
    todo = [(gx, gz) for gx, gz in todo if not open_cells[gz][gx]]
    for gx, gz in todo:
        outside[gz][gx] = True
    while todo:
        gx, gz = todo.pop()
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            x, z = gx + dx, gz + dz
            if 0 <= x < NX and 0 <= z < NZ and not outside[z][x] and not open_cells[z][x]:
                outside[z][x] = True
                todo.append((x, z))
    return [[outside[gz][gx] for gx in range(NX)] for gz in range(NZ)]


def _trace(carved):
    """boundary.outline on the long grid: the open region's edge, counter-clockwise, simplified and rounded."""
    def is_open(gx, gz):
        return 0 <= gx < NX and 0 <= gz < NZ and not carved[gz][gx]

    edges = {}

    def add(a, b):
        edges.setdefault(a, []).append(b)

    for gz in range(NZ):
        for gx in range(NX):
            if not is_open(gx, gz):
                continue
            if not is_open(gx, gz - 1):
                add((gx, gz), (gx + 1, gz))
            if not is_open(gx + 1, gz):
                add((gx + 1, gz), (gx + 1, gz + 1))
            if not is_open(gx, gz + 1):
                add((gx + 1, gz + 1), (gx, gz + 1))
            if not is_open(gx - 1, gz):
                add((gx, gz + 1), (gx, gz))
    start = min(edges)
    loop, prev, p = [start], start, edges[start].pop(0)
    guard = 0
    while p != start and guard < 800000:
        loop.append(p)
        options = edges[p]
        if len(options) > 1:
            dx, dz = p[0] - prev[0], p[1] - prev[1]
            options.sort(key=lambda e: -((dx * (e[1] - p[1])) - (dz * (e[0] - p[0]))))
        prev, p = p, options.pop(0)
        guard += 1
    pts = [(x * RES + WEST, z * RES + SOUTH) for x, z in loop]
    pts = outline_tools._simplify(pts + [pts[0]], 0.9)[:-1]
    pts = outline_tools._chaikin(outline_tools._subdivide(pts, 3.0), 2)
    pts = outline_tools._simplify(pts + [pts[0]], 0.25)[:-1]
    return [(round(x, 2), round(z, 2)) for x, z in pts]


def corners(rect):
    x0, z0, x1, z1 = rect
    return ((x0, z0), (x1, z0), (x0, z1), (x1, z1), ((x0 + x1) / 2, (z0 + z1) / 2))


def reoutline(L, poly, old_poly):
    """The long outline on the layout: what the square kept south of the seam stays (the traced outline
    is within a metre of the old one there); north of it a prop stays wholly inside or goes to the
    decor; the square's decor that now lies wholly inside comes back as a prop (the scenery beyond the
    old edge is played on now) where it has room."""
    kept, kept_rects, decor = [], [], []
    for prop, rect in zip(L.props, L.rects):
        if rect[3] < SEAM - 6.0:
            kept.append(prop)
            kept_rects.append(rect)
            continue
        inside = [outline_tools.inside(poly, x, z) for x, z in corners(rect)]
        if all(inside):
            kept.append(prop)
            kept_rects.append(rect)
        elif not any(inside) and prop['def'] not in B.SURFACE_TILES:
            decor.append(prop)
    L.props, L.rects = kept, kept_rects
    back = 0
    for prop in getattr(L, 'decor', []) or []:
        w, d = B.Layout.size(prop['def'], prop.get('rot', 0))
        rect = (prop['x'] - w / 2, prop['z'] - d / 2, prop['x'] + w / 2, prop['z'] + d / 2)
        inside = [outline_tools.inside(poly, x, z) for x, z in corners(rect)]
        if all(inside):
            if rect[1] > SEAM - 40.0 and L.fits(*rect, 0.3):
                L.props.append(prop)
                L.rects.append(rect)
                back += 1
        elif not any(inside):
            decor.append(prop)
    L.decor = decor
    L.boundary = poly
    return back


def strip_decor(L, theme, poly, rng):
    """Scenery beyond the new edge in the strip (the square's decor covers its own edge): the theme's
    trees and rocks, a house here and there, so the country goes on past the outline."""
    kinds = B.DENSIFY.get(theme, B.DENSIFY['temperate'])
    trees = list(kinds['trees']) or ['tree']
    rocks = list(kinds['rocks'])
    houses = list(kinds['houses'])
    placed = 0
    z = SEAM - 2.0
    while z < NORTH:
        x = WEST + 2.0
        while x < EAST:
            px, pz = x + rng.uniform(-1.6, 1.6), z + rng.uniform(-1.6, 1.6)
            roll = rng.random()
            kind = rng.choice(houses) if houses and roll < 0.04 else rng.choice(rocks) if rocks and roll < 0.2 else rng.choice(trees)
            w, d = B.Layout.size(kind, 0)
            rect = (px - w / 2, pz - d / 2, px + w / 2, pz + d / 2)
            if rect[0] > WEST and rect[2] < EAST and rect[3] < NORTH and not any(outline_tools.inside(poly, cx, cz) for cx, cz in corners(rect)):
                if not any(r[0] < rect[2] + 0.5 and r[2] > rect[0] - 0.5 and r[1] < rect[3] + 0.5 and r[3] > rect[1] - 0.5
                           for r in _decor_rects(L)):
                    L.decor.append({'def': kind, 'x': round(px * 2) / 2, 'z': round(pz * 2) / 2})
                    L._decor_rects.append(rect)
                    placed += 1
            x += 6.5
        z += 6.5
    return placed


def _decor_rects(L):
    if getattr(L, '_decor_rects', None) is None:
        L._decor_rects = []
        for prop in L.decor:
            w, d = B.Layout.size(prop['def'], prop.get('rot', 0))
            L._decor_rects.append((prop['x'] - w / 2, prop['z'] - d / 2, prop['x'] + w / 2, prop['z'] + d / 2))
    return L._decor_rects


# ------------------------------------------------------------------------------------ the fortress
class LongFortress(F_.Fortress):
    """fortress.Fortress on the long battlefield: the same checks, the layered base's own drop zone."""

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
            h = F_.SUPER_GUN_BLOCK / 2
            out.append(('super_gun', self.gun[0] - h, self.gun[1] - h, self.gun[0] + h, self.gun[1] + h))
        if self.arrival:
            out.append(('arrival', *self.arrival['stop']))
        return out

    def gate_at(self, axis, line, centre, closed, width=GATE, inward=1):
        """A gateway (fortress.Fortress.gateway) whose inside is `inward` (+1: +z or +x, -1: -z or -x)."""
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
        m = 9.0
        inner = m if closed else F_.YARD_WALLS
        lo, hi = (-m, inner) if inward > 0 else (-inner, m)
        self.keepout.append((x - h - 1, z + lo, x + h + 1, z + hi) if axis == 'x' else (x + lo, z - h - 1, x + hi, z + h + 1))

    def outer_wall(self):
        z = OUTER
        g0, g1 = MAIN_GATE - GATE / 2, MAIN_GATE + GATE / 2
        self.wall_run('x', z, g1, SALLY[1] - SALLY_W / 2)
        self.gate_at('x', z, SALLY[1], False, SALLY_W)
        self.wall_run('x', z, SALLY[1] + SALLY_W / 2, 1000.0, out=True)
        self.wall_run('x', z, g0, SALLY[0] + SALLY_W / 2)
        self.gate_at('x', z, SALLY[0], False, SALLY_W)
        self.wall_run('x', z, SALLY[0] - SALLY_W / 2, -1000.0, out=True)
        self.gate_at('x', z, MAIN_GATE, True)

    def keep_walls(self):
        z0 = KEEP_Z
        xw, xe = KEEP_X
        self.wall_run('x', z0, xw + 0.6, KEEP_GATE - GATE / 2)
        self.gate_at('x', z0, KEEP_GATE, True)
        self.wall_run('x', z0, KEEP_GATE + GATE / 2, xe - 0.6)
        a, b = KEEP_SIDE
        for x, inward in ((xw, 1), (xe, -1)):
            self.wall_run('z', x, z0 + 0.6, a)
            self.gate_at('z', x, (a + b) / 2, False, b - a, inward)
            self.wall_run('z', x, b, 1000.0, out=True)
        self.L.force('floodlight_mast', xw, z0, 0)
        self.L.force('floodlight_mast', xe, z0, 0)


def slot_at(F, size, kind, place, ring, prefs, **rules):
    """The first preferred spot with room for a hardpoint (fortress.place_slot), recorded with its place."""
    for x, z in prefs:
        at = F_.place_slot(F, size, kind, x, z, ring, quiet=True, **rules)
        if at:
            F.places[(at[0], at[1])] = place
            return at
    F.L.failed.append((f'{size} {kind} hardpoint ({place})', *prefs[0]))
    return None


def facing(x, z):
    """A hardpoint faces the way in: south, a little towards the middle."""
    return hardpoints.heading_to(x, z, x * 0.6, BUFFER[0] - 80.0)


def slot_entry(F, size, kind, x, z, ring):
    entry = {'x': x, 'z': z, 'size': size}
    if kind == 'utility':
        entry['kind'] = 'utility'
    entry['facing'] = facing(x, z)
    entry['ring'] = ring
    entry['place'] = F.places.get((x, z), 'forward' if ring == 1 else 'yard')
    return entry


def line_in(F, kind):
    """The line in: a rail line down the west yard from beyond the north edge, or a runway along the
    east yard landing from beyond the east edge. None when there is no room."""
    L = F.L
    if kind == 'runway':
        z = RUNWAY_Z
        east = KEEP_X[1] + 14.0
        x = east
        while x < EAST and F_.rect_inside(F.poly, (x, z - F_.RUNWAY_WIDTH / 2, x + 2, z + F_.RUNWAY_WIDTH / 2), 3.0):
            x += 2.0
        run = x - east
        if run < F_.RUNWAY_LENGTH[0]:
            return None
        run = min(run, F_.RUNWAY_LENGTH[1])
        west, far = east, east + run
        rect = (west, z - F_.RUNWAY_WIDTH / 2, far, z + F_.RUNWAY_WIDTH / 2)
        F_.clear_ground(F, rect)
        F.keepout.append((rect[0] - 2, rect[1] - 2, rect[2] + 2, rect[3] + 2))
        stop = (west + 10.0, z)
        return {'kind': 'runway', 'path': [EAST + 60.0, z, far, z, west, z], 'stop': [stop[0], stop[1]], 'heading': 270,
                'width': F_.RUNWAY_WIDTH}
    x = RAIL_X
    top = RAIL_END
    while outline_tools.inside(F.poly, x, top + 2.0) and top < NORTH + 20:
        top += 2.0
    if top - RAIL_END < 30.0:
        return None
    rect = (x - 3.0, RAIL_END - 2.0, x + 9.0, top + 2.0)
    F_.clear_ground(F, rect)
    F.keepout.append((rect[0] - 2, rect[1] - 2, rect[2] + 2, rect[3] + 2))
    stop = (x + 6.0, RAIL_END + 12.0)
    return {'kind': 'rail', 'path': [x, NORTH + 60.0, x, RAIL_END], 'stop': [stop[0], stop[1]], 'heading': 180}


def buffer_zone(F):
    """B.3: the buffer zone in front of the base: firing positions (earth-banked gun pits on the
    attacker's side, the high ground its guns fire from), a belt of dragon's teeth, anti-tank
    ditches and wire, each with gaps: before the main gate, the sally ports and between them."""
    L = F.L
    gaps = [(MAIN_GATE - 9.0, MAIN_GATE + 9.0), (SALLY[0] - 11.0, SALLY[0] + 11.0), (SALLY[1] - 11.0, SALLY[1] + 11.0),
            (-58.0, -46.0), (46.0, 58.0)]

    def open_at(x):
        return any(a <= x <= b for a, b in gaps)

    # Dragon's teeth: two staggered rows.
    x = WEST + 4.0
    while x < EAST - 4.0:
        if not open_at(x):
            for dz, dx in ((0.0, 0.0), (3.2, 1.6)):
                px, pz = x + dx, TEETH_Z + dz
                rect = F_.square(px, pz, 1.6)
                if F_.rect_inside(F.poly, rect, 4.0) and not open_at(px):
                    F.clear_clutter(rect, 0.4)
                    if F.free(rect, gap=0.6, soft=0.2, road=None, edge=4.0, keepout=False):
                        L.put('tank_trap', px, pz, 0, pad=0.2)
        x += 3.2
    # Anti-tank ditches (dug ground; the painter darkens it) and wire.
    x = WEST + 10.0
    k = 0
    while x < EAST - 10.0:
        if not open_at(x) and not open_at(x - 5.0) and not open_at(x + 5.0):
            rect = (x - 5.0, DITCH_Z - 2.0, x + 5.0, DITCH_Z + 2.0)
            if F_.rect_inside(F.poly, rect, 3.0):
                F.clear_clutter(rect, 0.3)
                if F.free(rect, gap=0.3, soft=0.3, road=None, edge=3.0, keepout=False):
                    L.put('tank_ditch', x, DITCH_Z, 90, pad=0.1)
            if k % 3 != 2:
                wire = (x - 4.0, WIRE_Z - 0.5, x + 4.0, WIRE_Z + 0.5)
                if F_.rect_inside(F.poly, wire, 4.0):
                    F.clear_clutter(wire, 0.3)
                    if F.free(wire, gap=1.0, soft=0.3, road=None, edge=4.0, keepout=False):
                        L.put('razor_wire', x, WIRE_Z, 0, pad=0.2)
        x += 12.0
        k += 1
    # Firing positions: a horseshoe of earth banks open to the south, sandbags on its lip.
    firing = []
    for fx, fz in FIRING:
        spot = F.spot(fx, fz, 13.0, reach=10.0, gap=1.0, soft=0.3, road=1.0)
        if not spot:
            L.failed.append(('firing position', fx, fz))
            continue
        x, z = spot
        for kind, dx, dz, rot in (('dirt_mound', 0.0, 4.5, 0), ('dirt_mound', -5.0, 1.0, 90), ('dirt_mound', 5.0, 1.0, 90),
                                  ('sandbags', -2.6, 6.8, 0), ('sandbags', 2.6, 6.8, 0)):
            L.put(kind, x + dx, z + dz, rot, pad=0.1)
        firing.append([x, z])
    # Shell holes across the buffer.
    rng = F.rng
    for _ in range(40):
        x, z = rng.uniform(WEST + 12.0, EAST - 12.0), rng.uniform(BUFFER[0], BUFFER[1] + 6.0)
        kind = rng.choice(('crater_large', 'crater_large', 'foxhole'))
        w, d = B.Layout.size(kind, 0)
        rect = (x - w / 2, z - d / 2, x + w / 2, z + d / 2)
        if F.free(rect, gap=0.5, soft=0.5, road=0.5, edge=4.0):
            L.put(kind, x, z, 0, pad=0.3)
    return firing


def forward_works(F):
    """The forward works behind the buffer: the three relays (stage 1) and the strongpoints (ring 1)."""
    L = F.L
    for x, z in RELAYS:
        spot = F.spot(x, z, 9.2, reach=16.0, clear=True, gap=3.0, road=1.0)
        if spot and L.put('radar_station', *spot, 0, pad=0.5):
            F.relays.append(spot)
        else:
            L.failed.append(('radar_station', x, z))
    for size, prefs in FORWARD_SLOTS:
        for x, z in prefs:
            at = F_.place_slot(F, size, 'tower', x, z, 1, reach=10.0, clear=True, quiet=True, gap=2.5, road=2.0)
            if at:
                F.places[at] = 'forward'
                for dx in (-3.5, 3.5):
                    rect = F_.square(at[0] + dx, at[1] - 6.0, 4.0)
                    F.clear_clutter(rect, 0.5)
                    if F.free(rect, gap=1.0, soft=0.3, road=1.0, edge=4.0):
                        L.put('sandbags', at[0] + dx, at[1] - 6.0, 0, pad=0.2)
            else:
                L.failed.append((f'forward {size} hardpoint', x, z))


def stores(F):
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


def barracks(F, count=12):
    """The yard's stores and barracks, flush against something solid or well clear of it, off the lanes."""
    L = F.L
    rng = F.rng
    placed = tries = 0
    before = set(F.missing(F.grid(gates=True)))
    xw, xe = KEEP_X
    while placed < count and tries < 3000:
        tries += 1
        kind = rng.choice(BUILDINGS)
        rot = rng.choice((0, 90))
        w, d = B.Layout.size(kind, rot)
        anchors = [r for r in F.solid() if (r[1] + r[3]) / 2 > OUTER + 1 and not (xw < (r[0] + r[2]) / 2 < xe and (r[1] + r[3]) / 2 > KEEP_Z)]
        if not anchors:
            break
        x, z = B.hugging(rng, rng.choice(anchors), w, d)
        x, z = round(x * 2) / 2, round(z * 2) / 2
        rect = (x - w / 2, z - d / 2, x + w / 2, z + d / 2)
        if rect[1] < OUTER + 3 or (xw - 3 < x < xe + 3 and z > KEEP_Z - 3):
            continue
        if not F.free(rect, gap=0.4, soft=0.3, road=1.0, edge=3.0):
            continue
        if B.alley_with(L, *rect) is not None:
            continue
        if L.put(kind, x, z, rot, pad=0.3):
            if set(F.missing(F.grid(gates=True))) - before:
                L.remove(lambda a0, b0, a1, b1, hx=x, hz=z: a0 <= hx <= a1 and b0 <= hz <= b1)
                continue
            placed += 1
    return placed


def main_road(L):
    """The road in: from the battlefield's road nearest the seam, north through the main gate and the
    keep's gate to the HQ. Everything on it goes (terrain too: the long battlefield opens a way)."""
    best, best_d = None, float('inf')
    for x, z, _ in L.road_samples():
        if z > SEAM or z < 40.0:
            continue
        d = math.hypot(x - MAIN_GATE, z - SEAM)
        if d < best_d:
            best, best_d = (round(x, 2), round(z, 2)), d
    start = best or (MAIN_GATE, 60.0)
    turn = (MAIN_GATE, max(start[1] + 12.0, 132.0))
    L.road(ROAD, start[0], start[1], turn[0], turn[1], MAIN_GATE, HQ[1] - 10.0)
    half = ROAD / 2 + 2.0
    lanes = [(min(start[0], turn[0]) - half, min(start[1], turn[1]) - half, max(start[0], turn[0]) + half, turn[1] + half),
             (MAIN_GATE - half, turn[1] - half, MAIN_GATE + half, KEEP_Z)]

    def on_segment(r):
        cx, cz = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        d = B.segment_distance(cx, cz, start[0], start[1], turn[0], turn[1])
        return d < half + max(r[2] - r[0], r[3] - r[1]) / 2

    keep = [(p, r) for p, r in zip(L.props, L.rects)
            if p['def'] in F_.OBJECTIVES or not ((on_segment(r)) or any(r[0] < k[2] and r[2] > k[0] and r[1] < k[3] and r[3] > k[1] for k in lanes[1:]))]
    L.props, L.rects = [p for p, _ in keep], [r for _, r in keep]
    return lanes


def fortify_long(L, name, theme, poly):
    """The layered base on the long battlefield (outline applied). Returns the fortress block."""
    attacker = L.teams[0]
    F = LongFortress(L, name, theme, poly, attacker)
    F.places = {}
    L.failed = []
    L.teams = [attacker, RALLY]
    # A radar station of the battlefield's own would count as a relay: it becomes a radar dome.
    for p in L.props:
        if p['def'] == 'radar_station':
            p['def'] = 'radar_dome'
    L.rects = [(p['x'] - w / 2, p['z'] - d / 2, p['x'] + w / 2, p['z'] + d / 2)
               for p in L.props for w, d in [B.Layout.size(p['def'], p.get('rot', 0))]]
    # The walls' ground: everything behind the outer wall goes, and the roads through it.
    L.remove(lambda a0, b0, a1, b1: b1 > OUTER - 4)
    B.clip_roads(L, WEST - 10, OUTER - 5, EAST + 10, NORTH + 10)
    lanes = main_road(L)
    F.outer_wall()
    F.keep_walls()
    L.put('command_hq', *HQ, 0, pad=0.3)
    keep = [(p, r) for p, r in zip(L.props, L.rects)
            if p['def'] in F_.OBJECTIVES or not any(r[0] < k[2] and r[2] > k[0] and r[1] < k[3] and r[3] > k[1] for k in F.keepout)]
    L.props, L.rects = [p for p, _ in keep], [r for _, r in keep]
    F.keepout.append(lanes[1])

    # The line in, in the yard.
    kind = F_.ARRIVAL.get(name) or F_.ARRIVAL_BY_THEME.get(theme, 'runway')
    for choice in (kind, 'rail' if kind == 'runway' else 'runway'):
        props, rects, keepout = list(L.props), list(L.rects), list(F.keepout)
        F.arrival = line_in(F, choice)
        if F.arrival and not F_.reach_targets(L, F.grid(gates=True), attacker, [('arrival', *F.arrival['stop'])]):
            break
        if F.arrival:
            print(f'warning: {name} long: the {choice} line in cannot be reached; trying the other')
        L.props, L.rects, F.keepout = props, rects, keepout
        F.arrival = None

    # The super-gun and the shield generators in the yard.
    at = F.spot(*SUPER_GUN, F_.SUPER_GUN_BLOCK + 3.0, reach=12.0, gap=3.0, road=2.0)
    if at:
        F.gun = at
        F.blocks.append((at[0], at[1], F_.SUPER_GUN_BLOCK))
    else:
        L.failed.append(('super_gun', *SUPER_GUN))
    for x, z in GENERATORS:
        at = F.spot(x, z, 7.0, reach=12.0, gap=3.0, road=1.0)
        if at and L.put('shield_generator', *at, 0, pad=0.5):
            F.generators.append(at)
        else:
            L.failed.append(('shield_generator', x, z))

    # The base's hardpoints by layer, then the forward works and the buffer zone.
    for size, kind_, place, ring, prefs in BASE_SLOTS:
        for x, z in prefs:
            slot_at(F, size, kind_, place, ring, [(x, z)], reach=10.0, gap=2.0, edge=3.0, road=1.0)
    forward_works(F)
    firing = buffer_zone(F)
    stores(F)
    barracks(F)
    for u in (-124.0, -76.0, 30.0, 72.0, 124.0):
        at = F.spot(u, OUTER + 3.0, 1.2, reach=6.0, gap=1.5, road=0.5)
        if at:
            L.put('floodlight_mast', *at, 0, pad=0.2)
    for x, z in ((KEEP_X[0] + 3.0, KEEP_Z + 14.0), (KEEP_X[1] - 3.0, KEEP_Z + 14.0), (-60.0, 300.0), (60.0, 300.0)):
        at = F.spot(x, z, 1.2, reach=6.0, gap=1.5, road=0.5)
        if at:
            L.put('floodlight_mast', *at, 0, pad=0.2)

    # The checks (fortress.fortify's).
    bare = F.blocks
    F.blocks = []
    missing = F.missing(F.grid(gates=True))
    F.blocks = bare
    if missing:
        raise SystemExit(f'{name} long: with the gates shut and no hardpoints, unreachable from the attacker camp: {missing}')
    missing = F.missing(F.grid(gates=True))
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
        print(f'warning: {name} long: {size} {kind_} hardpoint at ({x}, {z}) dropped: it cut off {missing}')
        missing = F.missing(F.grid(gates=True))
    if missing:
        raise SystemExit(f'{name} long: with the gates shut, unreachable from the attacker camp: {missing}')
    missing = F.missing(F.grid(gates=False, walls=False))
    if missing:
        raise SystemExit(f'{name} long: with the walls down, unreachable: {missing}')
    F_.open_wide(F, None, in_fort=in_strip_fort)
    sealed = F.grid(gates=True, sally=True)
    if not F_.reach_targets(L, sealed, attacker, [('hq', HQ[0] - 8, HQ[1] - 7, HQ[0] + 8, HQ[1] + 7)]):
        print(f'warning: {name} long: the walls do not hold with every gateway shut (the gates do not matter)')
    for def_id, x, z in L.failed:
        print(f'warning: {name} long: could not place {def_id} near ({x}, {z})')
    L.failed = []

    # The slots in the order the game opens them: per size the base's by importance (the order they were
    # placed in), then the forward ones.
    base, forward = [], []
    for s in F.slots:
        size, kind_, x, z, ring = s
        place = F.places.get((x, z), 'forward' if ring == 1 else 'yard')
        (forward if place == 'forward' else base).append(s)
    ring2 = [WEST - 10.0, OUTER - 1.0, EAST + 10.0, OUTER - 1.0, EAST + 10.0, NORTH + 10.0, WEST - 10.0, NORTH + 10.0]
    ring3 = [KEEP_X[0] - 1.0, KEEP_Z - 1.0, KEEP_X[1] + 1.0, KEEP_Z - 1.0, KEEP_X[1] + 1.0, NORTH + 10.0, KEEP_X[0] - 1.0, NORTH + 10.0]
    area = [WEST, BUFFER[0] - 4.0, EAST, BUFFER[0] - 4.0, EAST, NORTH, WEST, NORTH]
    block = {
        'hq': list(HQ),
        'layout': 'layered',
        'area': area,
        'rings': [ring2, ring3],
        'outerWall': OUTER,
        'innerWall': KEEP_Z,
        'forward': [list(p) for p in FORWARD_DROPS],
        'firing': firing,
        'slots': [slot_entry(F, *s) for s in base] + [slot_entry(F, *s) for s in forward],
    }
    if F.gun:
        block['superGun'] = {'x': F.gun[0], 'z': F.gun[1], 'heading': 180}
    if F.arrival:
        block['arrival'] = F.arrival
    counts = {}
    for e in block['slots']:
        key = e['place'] if e.get('kind') != 'utility' else 'utility'
        counts[key] = counts.get(key, 0) + 1
    sizes = {s: sum(1 for e in block['slots'] if e['place'] != 'forward' and e.get('kind') != 'utility' and e['size'] == s)
             for s in ('small', 'medium', 'large')}
    print(f'{name} long: {len(block["slots"])} hardpoints (base {sizes["small"]}/{sizes["medium"]}/{sizes["large"]} small/medium/large, '
          f'{counts.get("utility", 0)} utility, {counts.get("forward", 0)} forward; {counts}), {len(F.relays)} relays, '
          f'{len(F.generators)} generators, {"super-gun, " if F.gun else ""}{F.arrival["kind"] if F.arrival else "no line in"}, '
          f'{len(firing)} firing positions')
    return block


# ------------------------------------------------------------------------------------ the build
def build_one(map_id, build, theme, names, conquest, survival):
    # The Conquest battlefield, exactly as build_maps.main makes it (its camps planned).
    layout = B.scale_layout(build())
    poly, _ = outline_tools.carve(map_id, B.keep_of([layout, B.fortify_corner(B.scale_layout(build()), map_id, buildings=False)], map_id),
                                  seed=len(map_id) * 31 + 7)
    B.densify(B.warzone(layout, map_id, theme, poly), map_id, theme, poly)
    B.apply_outline(layout, poly)
    shadow = copy.deepcopy(layout)
    bases, outposts, _ = B.plan_bases(map_id, layout, shadow)
    points = [{'id': pid, 'name': name, 'x': x, 'z': z, 'radius': r, 'outpost': outposts.get(i, [])}
              for i, (pid, name, (x, z, r)) in enumerate(zip(('west', 'town', 'east'), names, layout.points))]

    # The long battlefield: the square's ground and a strip to the north.
    L = layout
    L.north = NORTH
    new_poly = long_outline(map_id, poly)
    back = reoutline(L, new_poly, poly)
    L._decor_rects = None
    rng = random.Random(len(map_id) * 977 + 17)
    added = strip_decor(L, theme, new_poly, rng)
    block = fortify_long(L, map_id, theme, new_poly)
    missing = L.reachable([('hq', HQ[0] - 8, HQ[1] - 7, HQ[0] + 8, HQ[1] + 7)] + [('point', p['x'], p['z']) for p in points])
    if missing:
        raise SystemExit(f'{map_id} long: unreachable: {missing}')
    name = conquest.split(' for ')[0]
    meta = {
        'id': f'{map_id}_long', 'theme': theme, 'size': int(LENGTH), 'bounds': [WEST, SOUTH, EAST, NORTH],
        'teams': [B.TEAMS[0], {'team': 1, 'x': RALLY[0], 'z': RALLY[1]}], 'points': points, 'siegeRings': SIEGE_RINGS,
        'units': [u for u in B.grown(B.CONQUEST_UNITS) if u['team'] == 0], 'bases': [bases[0]], 'fortress': block,
    }
    B.dump(B.DATA / 'maps' / f'{map_id}_long.json',
           f'{name}, long (prompt 17): 300 x 480 m, the attack from the south-west camp to the layered base in the north '
           f'(buffer zone, outer wall, yard, inner wall, HQ); for Siege, Defend, Endless and the weekly fortress.', meta, L)
    print(f'{map_id}_long: outline of {len(new_poly)} points, {back} props back from the decor, {added} strip decor, '
          f'{len(L.props)} props, {len(L.decor)} decor')


def main(only=()):
    import check_access
    done = []
    for entry in B.MAPS:
        map_id = entry[0]
        if only and map_id not in only:
            continue
        build_one(*entry)
        done.append(map_id)
    tables = check_access.balance()
    failed = 0
    for map_id in done:
        problems = check_access.check(B.DATA / 'maps' / f'{map_id}_long.json', tables)
        print(f'{map_id}_long: {"ok" if not problems else "; ".join(problems)}')
        failed += bool(problems)
    return failed


if __name__ == '__main__':
    sys.exit(1 if main(sys.argv[1:]) else 0)
