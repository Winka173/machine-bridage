"""Machine Brigade volcanic, jungle, airbase and city map props built with frontier_kit.

Volcanic ridge: columnar basalt clusters with glowing cracks, an obsidian spire, a lava vent, a
charred tree and a dark cliff. Jungle: three buttress-rooted canopy trees with hanging vines, a
bamboo clump, a fern, an overgrown stepped temple and a stilt hut under palm thatch. Airbase: an
arched hangar with its doors half open, a control tower, a parked fighter, a fuel truck, a radome
building, a blast wall and a runway edge light. City: two high-rises, a glass skyscraper with a
helipad, an open parking garage, a billboard, a city bus and a traffic light.

Same conventions as mb_props, mb_town and mb_themes: metres, +Z up, Blender X = width, Y = depth
(the footprints are given as X x Y), the front faces -Y and origins sit on the ground at the
footprint centre. Vehicle props (parked_jet, fuel_truck, bus) are modelled nose to -Y like the
army's vehicles and then turned so the nose points to +X, as mb_town's car and truck are. Parts that
touch overlap or stand at least 1 cm apart, so no two visible faces are coplanar (they z-fight).

New kit materials: LavaGlow (emissive molten rock; also the red of traffic and aviation lights),
SignalGreen (emissive traffic-light green) and Obsidian (glossy black volcanic glass).

Moving parts: the control tower's surface radar spins on its `Radar` pivot (about local Z). The
parked jet, fuel truck and bus are static props (no rig names); the jet is painted Team, and the
fuel truck's cab and the bus body are CarRed, so the map can repaint them like the town truck.
Night windows follow the town houses: every window pane is Glass or, at random, Lamp. Tall
buildings carry detailed roofs (plant rooms, tanks, air conditioners, aerials, dishes) because the
game camera looks down on them. Trees stay near 1,000 triangles and rocks under 1,000.
"""
import math
import random

import bmesh
from mathutils import Matrix, Vector, noise
from mathutils.bvhtree import BVHTree

from frontier_kit import chamfered
from mb_air import (LEFT, RIGHT, Planform, _aam, _aam_parts, _dome, _duct, _intake, _nozzle, _patch, _sec,
                    _skin_panel, _skin_z, _surface, _upright, _wing)
from mb_terrain import _outline, _split
from mb_themes import ladder, loft_along, pot, rim, ring_rail, roof_tank
from mb_town import (NORMAL, TANGENT, _arches, _turn, _wheels, ac_unit, door, fbox, letters, pane, roof_shell, slide,
                     window)
from mb_vehicles import _dish, _frame

R90 = math.pi / 2
TAU = math.tau
ALONG_X = (0, R90, 0)  # cylinder axis along X
ALONG_Y = (R90, 0, 0)  # cylinder axis along Y


# ----------------------------------------------------------------------------- shared helpers
def hexagon(r, turn=0.0):
    return [(r * math.cos(turn + k * math.pi / 3), r * math.sin(turn + k * math.pi / 3)) for k in range(6)]


def column(part, x, y, r, z0, h, turn=0.0, slope=0.0, aim=0.0):
    """Hexagonal basalt column from z0 up to h whose top is cut at `slope` (rise per metre) rising
    towards the direction `aim`."""
    c, s = math.cos(aim), math.sin(aim)
    ring = hexagon(r, turn)
    part.loft([[(x + u, y + v, z0) for u, v in ring], [(x + u, y + v, h + slope * (u * c + v * s)) for u, v in ring]])


def fallen_column(part, x, y, r, length, yaw, roll=0.0):
    """Broken basalt column lying on the ground along `yaw`."""
    m = Matrix.Translation((x, y, r * .8)) @ Matrix.Rotation(yaw, 4, 'Z') @ Matrix.Rotation(R90, 4, 'Y')
    rings = [[tuple(m @ Vector((u, v, z))) for u, v in hexagon(r, roll)] for z in (-length / 2, length / 2)]
    part.loft(rings)


def ring_solid(rings, cap=True):
    """Faces for stacked closed rings (each wound counter-clockwise seen from above): quads between
    the rings, and the last ring capped. Returns verts, faces for mb_terrain._split."""
    n = len(rings[0])
    verts = [p for ring in rings for p in ring]
    faces = []
    for k in range(len(rings) - 1):
        for i in range(n):
            j = (i + 1) % n
            a0, a1, b0, b1 = k * n + i, k * n + j, (k + 1) * n + i, (k + 1) * n + j
            faces += [(a0, a1, b1), (a0, b1, b0)]
    if cap:
        last = (len(rings) - 1) * n
        faces.append(tuple(last + i for i in range(n)))
    return verts, faces


def wobble(seed, amp, k=1.6):
    """Smooth closed noise around a ring: f(theta, level) in [-amp, amp]."""
    off = Vector((seed * 3.7, seed * 1.3, seed * 2.9))
    return lambda th, lv=0.0: amp * noise.noise(Vector((math.cos(th) * k, math.sin(th) * k, lv * .7)) + off)


def recentre(a, w=None, d=None):
    """Shift every part so the footprint's bounding box is centred on the origin (pivot-less props);
    with w and d, also scale it in X and Y to exactly that footprint."""
    pts = [v.co for s in a.shapes.values() for v in s.bm.verts]
    x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
    y0, y1 = min(p.y for p in pts), max(p.y for p in pts)
    kx = w / (x1 - x0) if w else 1.0
    ky = d / (y1 - y0) if d else 1.0
    for s in a.shapes.values():
        for v in s.bm.verts:
            v.co.x = (v.co.x - (x0 + x1) / 2) * kx
            v.co.y = (v.co.y - (y0 + y1) / 2) * ky


def crack(part, pts, r=.045):
    """Glowing crack: a thin tube half sunk into the surface it follows."""
    part.tube(pts, r, seg=4)


# ----------------------------------------------------------------------------- volcanic
def basalt_cluster(a, seed, w, d, hmax, r, fissure=(), cracks=2, rubble=4, ox=0.0, oy=0.0, hmin=.45, gap=.05,
                   back=.25):
    """Honeycomb of hexagonal basalt columns inside a wobbly w x d ellipse centred at (ox, oy):
    tallest at the back, stepping down to the front, tops cut at random slopes, colours mixed
    Asphalt / Charred / RoofSlate. `fissure` is a polyline across the cluster where the columns
    break off into low stubs over a glowing lava seam; `cracks` tall front columns get a glowing
    crack down a visible face. Columns stand `gap` apart, so their faces never touch."""
    rng = random.Random(seed)
    parts = {m: a.part('Basalt', m, flat=True) for m in ('Asphalt', 'Charred', 'RoofSlate')}
    glow = a.part('Lava', 'LavaGlow')
    s = math.sqrt(3) * r + gap
    rx, ry = w / 2 - r * .85, d / 2 - r * .85
    edge = _outline(rng, ((2, 3, .09), (4, 6, .05)))

    def seam_dist(x, y):
        best = 9.0
        for (x0, y0), (x1, y1) in zip(fissure, fissure[1:]):
            dx, dy = x1 - x0, y1 - y0
            t = max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / (dx * dx + dy * dy)))
            best = min(best, math.hypot(x - x0 - t * dx, y - y0 - t * dy))
        return best

    cells = []
    n = int(max(w, d) / s) + 2
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x, y = i * s * math.cos(math.pi / 6), i * s * .5 + j * s
            u, v = x / rx, y / ry
            rho = math.hypot(u, v) / edge(math.atan2(v, u))
            if rho <= 1.0:
                cells.append((x, y, rho))
    tall = []
    for x, y, rho in cells:
        h = hmax * (1 - .72 * rho ** 1.5) * (1 - back + back * (y / ry + 1) / 2) * rng.uniform(.78, 1.06)
        if rng.random() < .12:
            h *= rng.uniform(.4, .7)  # broken column
        h = max(hmin * rng.uniform(.8, 1.2), h)
        stub = fissure and seam_dist(x, y) < s * .75
        if stub:
            h = rng.uniform(.14, .32)
        rr = r * rng.uniform(.93, 1.0)
        mat = rng.choices(('Asphalt', 'Charred', 'RoofSlate'), (.5, .28, .22))[0]
        slope = rng.uniform(.05, .32) if h > .5 else rng.uniform(0, .1)
        column(parts[mat], ox + x, oy + y, rr, -.05, h, turn=rng.uniform(-.04, .04), slope=slope,
               aim=rng.uniform(.6, 2.6))
        if not stub:
            tall.append((h, x, y, rr))
    if fissure:
        pts = [(ox + x, oy + y, .03) for x, y in fissure]
        glow.tube(pts, .15, seg=5)
        for (x0, y0), (x1, y1) in zip(fissure, fissure[1:]):  # embers between the stubs
            for t in (.3, .7):
                glow.ico((.16, .13, .07), loc=(ox + x0 + (x1 - x0) * t + rng.uniform(-.15, .15),
                                               oy + y0 + (y1 - y0) * t + rng.uniform(-.15, .15), .05),
                         sub=1, jitter=.2, seed=seed + t)
    # Glowing cracks down the visible faces (the camera looks from the front right) of tall columns
    # on the front half.
    front = sorted((c for c in tall if c[0] > min(1.1, hmax * .45) and c[2] < 0), key=lambda c: c[2] - c[1] * .3)
    for h, x, y, rr in front[:cracks]:
        phi = rng.choice((-R90, -math.pi / 6))
        ap = rr * math.cos(math.pi / 6)
        c, sn = math.cos(phi), math.sin(phi)
        tx, ty = -sn, c
        pts = []
        for k, z in enumerate((h * .82, h * .62, h * .42, h * .22, .06)):
            u = (.09 if k % 2 else -.07) * rr / .42
            pts.append((ox + x + c * (ap - .01) + tx * u, oy + y + sn * (ap - .01) + ty * u, z))
        crack(glow, pts, .05)
        glow.ico((.2, .16, .06), loc=(ox + x + c * (ap + .12), oy + y + sn * (ap + .12), .02), sub=1, jitter=.2,
                 seed=seed + h)
    # Fallen column pieces and chips at the foot, on the front side.
    for k in range(rubble):
        th = rng.uniform(-2.8, -.2)
        e = edge(th)
        x, y = ox + math.cos(th) * (rx + r) * e * 1.02, oy + math.sin(th) * (ry + r) * e * 1.02
        if k % 2 == 0:
            fallen_column(parts[rng.choice(('Asphalt', 'Charred'))], x, y, r * .7, rng.uniform(.6, 1.1),
                          rng.uniform(0, math.pi), rng.uniform(0, 1))
        else:
            parts['Asphalt'].ico((r * .7, r * .6, r * .4), loc=(x, y, r * .2), sub=1, jitter=.3, seed=seed + k)


def basalt_rock_a(a):
    """Columnar basalt cluster (5 x 4 m, 2.6 m) split by a glowing lava seam."""
    basalt_cluster(a, 31, 5.0, 3.8, 2.6, .42, fissure=[(-1.6, -1.1), (-.6, -.2), (.2, .1), (1.5, .9)], cracks=2,
                   rubble=4)
    recentre(a)


def basalt_rock_b(a):
    """Large columnar basalt outcrop (7 x 5 m, 3.6 m) with a lava seam and glowing cracks."""
    basalt_cluster(a, 47, 6.5, 4.6, 3.6, .5, fissure=[(-2.9, .5), (-1.6, -.2), (-.4, -.9), (.6, -1.4), (1.3, -2.1)],
                   cracks=3, rubble=5)
    recentre(a)


def basalt_rock_c(a):
    """Small basalt column stack (3 x 3 m, 1.9 m) with one glowing crack."""
    basalt_cluster(a, 53, 2.8, 2.9, 1.9, .36, cracks=1, rubble=2, hmin=.35)
    recentre(a, 3.0, 3.0)


def shard(part, base, tip, r0, sides, rng, stations=4, twist=.4, taper=1.15):
    """Faceted glassy shard: irregular polygon sections tapering from base to a point at tip."""
    base, tip = Vector(base), Vector(tip)
    rings = []
    turn = rng.uniform(0, TAU)
    radii = [rng.uniform(.8, 1.2) for _ in range(sides)]
    for k in range(stations):
        t = k / stations
        c = base.lerp(tip, t)
        r = r0 * (1 - t) ** taper * rng.uniform(.9, 1.1)
        ring = []
        for i in range(sides):
            ang = turn + t * twist + i * TAU / sides + rng.uniform(-.12, .12)
            ring.append((c.x + math.cos(ang) * r * radii[i], c.y + math.sin(ang) * r * radii[i], c.z))
        rings.append(ring)
    rings.append([tuple(tip)])
    part.loft(rings)


def obsidian_spire(a):
    """Obsidian spire (3 x 3 m, 7 m): a faceted black-glass blade with three lesser shards leaning
    out of a heap of dark rock, glowing seams at its foot."""
    rng = random.Random(61)
    glass = a.part('Obsidian', 'Obsidian', flat=True)
    shard(glass, (0, 0, -.1), (.2, .15, 7.0), 1.12, 6, rng, stations=5, twist=.5, taper=.85)
    for base, tip, r0 in (((.7, -.4, -.1), (1.3, -.95, 3.5), .58), ((-.65, -.3, -.1), (-1.2, -.8, 2.8), .5),
                          ((-.25, .65, -.1), (-.65, 1.2, 4.3), .6), ((.55, .5, -.1), (.95, .95, 2.1), .4)):
        shard(glass, base, tip, r0, 5, rng, stations=3, taper=.9)
    rock = a.part('Rock', 'Asphalt', flat=True)
    dark = a.part('Rock_dark', 'Charred', flat=True)
    for k, (x, y, rx, ry, rz) in enumerate(((.95, .15, .6, .5, .42), (-.9, .45, .55, .5, .38),
                                            (.1, -1.05, .5, .42, .32), (-1.05, -.95, .4, .36, .28),
                                            (1.1, -1.05, .34, .3, .22), (.2, 1.1, .45, .36, .3))):
        (rock if k % 2 else dark).ico((rx, ry, rz), loc=(x, y, rz * .45), sub=1, jitter=.3, seed=k * 1.9 + 3)
    glow = a.part('Lava', 'LavaGlow')
    crack(glow, [(-.55, -.62, .03), (-.1, -.78, .05), (.35, -.62, .03), (.72, -.82, .04)], .07)
    crack(glow, [(.72, -.82, .04), (1.12, -.62, .03), (1.35, -.35, .03)], .055)
    glow.ico((.18, .15, .06), loc=(-.55, -.62, .02), sub=1, jitter=.2, seed=4)


def lava_vent(a):
    """Lava vent (3 x 3 m, 1.1 m): a fumarole cone of ragged dark scoria with sulphur crusts on its
    rim, a bubbling lava pool in the crater and three glowing runnels down its slopes."""
    rng = random.Random(71)
    seg = 18
    wob = wobble(7.1, .11)
    prof = [(1.5, -.06), (1.36, .16), (1.1, .44), (.86, .74), (.7, .94), (.6, 1.02), (.52, .95), (.45, .78),
            (.4, .6)]

    def at(th, k):
        r, z = prof[k]
        rr = r * (1 + wob(th, k)) * (1 + .06 * math.sin(3 * th + 1.3))
        zz = z + (.05 * noise.noise(Vector((math.cos(th) * 2, math.sin(th) * 2, k))) if 0 < k < len(prof) - 1 else 0)
        return rr * math.cos(th), rr * math.sin(th), zz
    rings = [[at(i * TAU / seg, k) for i in range(seg)] for k in range(len(prof))]
    verts, faces = ring_solid(rings)

    def pick(c, n):
        rad = Vector((c.x, c.y, 0))
        inner = rad.length > 1e-6 and n.dot(rad.normalized()) < -.05
        if inner:
            return 'Charred'
        if c.z > .82 and noise.noise(c * 2.3 + Vector((1.7, 0, 0))) > .05:
            return 'Hazard'
        return 'Charred' if noise.noise(c * 1.4) > .25 else 'Asphalt'
    _split(a, verts, faces, pick, 'Cone', rewind=False)
    glow = a.part('Lava', 'LavaGlow')
    glow.sphere((.46, .46, .1), loc=(0, 0, .62), seg=12, rings=6, cut=0.0)
    glow.torus(.4, .045, loc=(0, 0, .66), seg=14, ring=4)
    # Runnels spilling over low points of the rim and down the front and right slopes.
    for th0, drift in ((-1.5, .12), (-.35, -.1), (-2.5, .08)):
        pts = []
        for k in range(5, -1, -1):
            th = th0 + drift * (5 - k) + .04 * math.sin(k * 2.1)
            x, y, z = at(th, k)
            out = Vector((x, y, 0)).normalized()
            pts.append((x + out.x * .025, y + out.y * .025, z + .035))
        crack(glow, pts, .075)
        x, y, _ = at(th0 + drift * 5, 0)
        glow.ico((.3, .24, .05), loc=(x * 1.04, y * 1.04, .0), sub=1, jitter=.2, seed=th0)
    # Sulphur crusts and loose scoria blocks.
    sulphur = a.part('Sulphur', 'Hazard', flat=True)
    for th in (.6, 2.1, 3.9):
        x, y, z = at(th, 5)
        sulphur.ico((.16, .13, .06), loc=(x * .98, y * .98, z + .02), sub=1, jitter=.25, seed=th)
    blocks = a.part('Scoria', 'Asphalt', flat=True)
    for th, rr in ((.9, .24), (2.8, .2), (4.4, .26), (5.5, .17)):
        x, y, _ = at(th, 0)
        blocks.ico((rr, rr * .85, rr * .6), loc=(x * .98, y * .98, rr * .25), sub=1, jitter=.3, seed=th * 2)


def charred_tree(a):
    """Burnt dead tree (1.2 x 1.2 m base, 4.9 m): a charred trunk snapped into splinters, three
    stubby limbs, root flares and embers still glowing in its cracks and at its foot."""
    rng = random.Random(81)
    wood = a.part('Trunk', 'Charred')
    spine = [(0, 0, -.05), (.04, .02, 1.3), (.12, .05, 2.6), (.2, .02, 3.7)]
    sections = []
    for i, r in enumerate((.3, .24, .2, .16)):
        sections.append([(r * math.cos(k * TAU / 7 + i * .4) * rng.uniform(.88, 1.1),
                          r * math.sin(k * TAU / 7 + i * .4) * rng.uniform(.88, 1.1)) for k in range(7)])
    loft_along(wood, spine, (1, 0, 0), sections)
    top = Vector(spine[-1])
    for k, (dx, dy, h, s) in enumerate(((.06, .05, 1.15, .1), (-.08, .04, .7, .09), (.02, -.08, .9, .08),
                                        (.08, -.03, .5, .07))):
        wood.limb(top + Vector((dx, dy, -.2)), top + Vector((dx * 2.2, dy * 2.2, h)), s, s * .9, bevel=0,
                  taper=(.2, .2))
    for p0, p1, s in (((.05, .02, 2.0), (1.1, .35, 2.9), .12), ((.1, .03, 2.8), (-.85, .4, 3.6), .1),
                      ((.02, 0, 1.4), (-.3, -.95, 2.2), .1), ((1.1, .35, 2.9), (1.35, .15, 3.3), .06)):
        wood.limb(p0, p1, s, s * .9, bevel=0, taper=(.45, .45))
    for t in (.3, 1.9, 3.4, 5.0):
        wood.limb((0, 0, .5), (math.cos(t) * .56, math.sin(t) * .56, .04), .17, .14, bevel=0, taper=(.35, .45))
    glow = a.part('Embers', 'LavaGlow')
    crack(glow, [(.2, -.2, .25), (.23, -.18, .6), (.19, -.21, .95), (.21, -.17, 1.3)], .035)
    crack(glow, [(.12, -.19, 2.0), (.16, -.14, 2.35), (.12, -.17, 2.6)], .03)
    glow.cyl(.13, .12, loc=(.18, -.2, .1), seg=6, bevel=0)
    ash = a.part('Ash', 'Asphalt', flat=True)
    for k, (x, y) in enumerate(((-.35, .3), (.35, .35), (-.3, -.35))):
        ash.ico((.22, .18, .07), loc=(x, y, .01), sub=1, jitter=.3, seed=k + 9)
    glow.ico((.12, .1, .04), loc=(.42, -.3, .02), sub=1, jitter=.3, seed=2)


def volcanic_cliff(a):
    """Dark volcanic cliff (14 x 6 m, 7 m): stacked lava-flow strata with ash on the ledges, glowing
    seams along the lower ledge and cracks down the front, a lava spill at its foot, a group of
    basalt columns at its right end and scree."""
    rng = random.Random(91)
    H, seg = 7.0, 30
    edge = _outline(rng, ((2, 3, .12), (4, 6, .06)))
    jit = [rng.uniform(-.05, .05) for _ in range(seg)]
    levels = [(-.02, 1.04), (.18, 1.0), (.4, .95), (.4, .87), (.62, .84), (.64, .79), (.64, .75), (.88, .72),
              (1.0, .68), (1.03, .52), (1.05, .3)]
    rings = []
    for k, (f, sc) in enumerate(levels):
        ring = []
        for i in range(seg):
            th = i * TAU / seg + (k % 2) * .05
            r = sc * edge(th) * (1 + jit[i] + rng.uniform(-.03, .03))
            z = H * f + (rng.uniform(-.12, .12) if 0 < k < len(levels) - 1 else 0)
            ring.append((r * math.cos(th), r * math.sin(th), z))
        rings.append(ring)
    base = rings[0]
    minx, maxx = min(p[0] for p in base), max(p[0] for p in base)
    miny, maxy = min(p[1] for p in base), max(p[1] for p in base)
    kx, ky = 13.4 / (maxx - minx), 5.6 / (maxy - miny)
    ox, oy = (minx + maxx) / 2, (miny + maxy) / 2

    def tf(p):
        return ((p[0] - ox) * kx, (p[1] - oy) * ky, p[2])
    rings = [[tf(p) for p in ring] for ring in rings]
    verts = [p for ring in rings for p in ring] + [(-ox * kx, -oy * ky, H * 1.07)]
    centre = len(verts) - 1
    faces = []
    for k in range(len(rings) - 1):
        for i in range(seg):
            j = (i + 1) % seg
            a0, a1 = k * seg + i, k * seg + j
            b0, b1 = a0 + seg, a1 + seg
            faces += [(a0, a1, b1), (a0, b1, b0)] if (i + k) % 2 else [(a0, a1, b0), (a1, b1, b0)]
    last = (len(rings) - 1) * seg
    faces += [(last + i, last + (i + 1) % seg, centre) for i in range(seg)]

    def pick(c, n):
        if n.z > .8:
            return 'Charred'
        return 'RoofSlate' if noise.noise(c * .45 + Vector((3.1, 0, 0))) > .28 else 'Asphalt'
    _split(a, verts, faces, pick, 'Cliff', rewind=False)
    glow = a.part('Lava', 'LavaGlow')

    def visible(i):
        th = i * TAU / seg
        return -2.7 < th - TAU < .35 or -2.7 < th < .35

    # Seams in the inner corner of the lower ledge on the visible side, broken into runs.
    idx = [i for i in range(seg) if visible(i)]
    runs, run = [], []
    for i in sorted(idx, key=lambda i: (i * TAU / seg + math.pi) % TAU):
        run.append(i)
        if len(run) >= rng.randint(3, 5):
            runs.append(run)
            run = []
    for run in runs[::2] + runs[1::4]:
        pts = []
        for i in run:
            p2, p3 = Vector(rings[2][i]), Vector(rings[3][i])
            q = p3.lerp(p2, .22)
            pts.append((q.x, q.y, max(p2.z, p3.z) + .02))
        if len(pts) >= 2:
            crack(glow, pts, .085)
    # Cracks down the front wall from the lower ledge to the foot.
    for i in (idx[len(idx) // 3], idx[2 * len(idx) // 3]):
        pts = []
        for k in (2, 1, 0):
            p = Vector(rings[k][i])
            out = Vector((p.x, p.y, 0)).normalized()
            wig = .12 if k == 1 else 0
            pts.append((p.x + out.x * .01 + out.y * wig, p.y + out.y * .01 - out.x * wig, max(p.z, .05)))
        crack(glow, pts, .06)
        p = Vector(rings[0][i])
        glow.ico((.55, .4, .06), loc=(p.x * 1.03, p.y * 1.03, .01), sub=1, jitter=.2, seed=i)
    # A glowing fissure across the top, and loose blocks on it.
    tree = BVHTree.FromPolygons([Vector(v) for v in verts], faces, epsilon=0.0)

    def surface(x, y):
        hit = tree.ray_cast(Vector((x, y, H * 2)), Vector((0, 0, -1)), H * 3)[0]
        return hit.z if hit is not None else H
    top_pts = [(-3.6, .9), (-2.4, .35), (-1.5, .6), (-.4, -.1), (.7, .25), (1.6, -.35), (2.9, -.05)]
    crack(glow, [(x, y, surface(x, y) + .02) for x, y in top_pts], .1)
    for x, y in ((-1.5, .6), (1.6, -.35)):
        glow.ico((.3, .22, .05), loc=(x, y, surface(x, y) + .01), sub=1, jitter=.2, seed=x)
    blocks = a.part('Top_blocks', 'Asphalt', flat=True)
    for k, (x, y, rr) in enumerate(((-2.6, -.9, .55), (.4, 1.1, .45), (2.2, .8, .6), (-4.2, -.1, .4), (3.6, -.9, .35))):
        blocks.ico((rr * 1.2, rr, rr * .6), loc=(x, y, surface(x, y) + rr * .15), sub=1, jitter=.3, seed=k * 2.1)
    # Basalt columns against the right end, and scree.
    basalt_cluster(a, 97, 2.6, 2.3, 4.4, .36, cracks=1, rubble=2, ox=5.15, oy=-.95, back=.4, hmin=1.2)
    scree = a.part('Scree', 'Asphalt', flat=True)
    for k in range(6):
        th = rng.uniform(-2.9, .3)
        p = Vector(rings[0][int((th % TAU) / TAU * seg) % seg])
        size = rng.uniform(.35, .7)
        scree.ico((size * 1.2, size, size * .7), loc=(p.x * 1.02, p.y * 1.02, size * .2), sub=1, jitter=.3,
                  seed=k * 1.7 + 5)


# ----------------------------------------------------------------------------- jungle
def buttress(part, phi, r_in, reach, height, thick=.16):
    """Plank buttress root: a thin concave fin running from the trunk (height up it) out to `reach`
    on the ground along the direction phi."""
    span = reach - r_in
    prof = [(r_in, -.06), (reach, -.06), (reach - span * .12, .14), (r_in + span * .42, height * .28),
            (r_in + span * .12, height * .75), (r_in, height)]
    part.prism(prof, thick, axis='X', rot=(0, 0, phi - R90), bevel=0)


def poly(r, n, turn=0.0, rng=None, var=0.0):
    """Regular n-gon outline (optionally with jittered radii)."""
    out = []
    for k in range(n):
        f = 1 + (rng.uniform(-var, var) if rng else 0.0)
        out.append((r * f * math.cos(turn + k * TAU / n), r * f * math.sin(turn + k * TAU / n)))
    return out


def limb(part, p0, p1, r0, r1, rise=.3, sides=5, turn=0.0):
    """Branch from p0 to p1 bowed upwards by `rise` of its length, tapering r0 -> r1."""
    p0, p1 = Vector(p0), Vector(p1)
    mid = (p0 + p1) / 2 + Vector((0, 0, (p1 - p0).length * rise * .5))
    d = (p1 - p0).normalized()
    side = Vector((-d.y, d.x, 0)) if abs(d.z) < .95 else Vector((1, 0, 0))
    loft_along(part, [p0, mid, p1], side, [poly(r0, sides, turn), poly((r0 + r1) / 2, sides, turn + .3),
                                           poly(r1, sides, turn + .6)])


def vine(part, top, length, rng, sway=.35, r=.035):
    """Liana hanging from `top`, swinging a little as it falls."""
    x, y, z = top
    ang = rng.uniform(0, TAU)
    pts = [(x, y, z + .1)]
    for k in (1, 2, 3):
        t = k / 3
        pts.append((x + math.cos(ang) * sway * math.sin(t * 2.2), y + math.sin(ang) * sway * math.sin(t * 2.2),
                    z - length * t))
    part.tube(pts, r, seg=3)


def jungle_tree(a, seed, trunk_h, r0, lean, limbs, crown, buttresses, reach, vines, extra=()):
    """Rainforest tree: a tapering trunk on plank buttress roots, limbs spreading into a broad
    canopy of flattened leaf masses, lianas and aerial roots hanging from the limbs.
    limbs: [(height fraction, yaw, length, rise)]; crown: [(x, y, z, rx, rz, sub)] extra canopy
    masses over the trunk top (each limb end gets one too); extra: [(x, y, z)] points to hang long
    aerial roots from (they end 60 cm above the ground)."""
    rng = random.Random(seed)
    bark = a.part('Trunk', 'Bark')
    lx, ly = lean
    spine = [(0, 0, -.1), (lx * .1, ly * .1, trunk_h * .3), (lx * .45, ly * .45, trunk_h * .66), (lx, ly, trunk_h)]
    radii = (r0, r0 * .8, r0 * .66, r0 * .52)
    loft_along(bark, spine, (1, 0, 0), [poly(r, 7, i * .35, rng, .08) for i, r in enumerate(radii)])
    for k in range(buttresses):
        phi = k * TAU / buttresses + rng.uniform(-.25, .25)
        buttress(bark, phi, r0 * .45, reach * rng.uniform(.85, 1.0), trunk_h * rng.uniform(.2, .28), thick=r0 * .3)
    leaves = [a.part('Leaves', m, flat=True) for m in ('Foliage', 'FoliageDark', 'Foliage', 'FoliageLight')]
    hang = []

    def trunk_at(f):
        return Vector((lx * f ** 1.5, ly * f ** 1.5, trunk_h * f))
    for i, (f, yaw, length, rise) in enumerate(limbs):
        p0 = trunk_at(f)
        d = Vector((math.cos(yaw), math.sin(yaw), 0))
        p1 = p0 + d * length + Vector((0, 0, length * rise))
        rb = r0 * .42 * (.7 + .3 * length / 3.5)
        limb(bark, p0, p1, rb, rb * .45, rise=.25)
        rx = 1.5 + length * .2
        leaves[i % 4].ico((rx, rx * .92, rx * .5), loc=p1 + Vector((0, 0, .45)), sub=2, jitter=.22,
                          seed=seed + i * 1.7)
        hang += [p0.lerp(p1, .55), p0.lerp(p1, .85)]
    top = trunk_at(1.0)
    for i, (x, y, z, rx, rz, sub) in enumerate(crown):
        leaves[(i + 1) % 4].ico((rx, rx * .9, rz), loc=top + Vector((x, y, z)), sub=sub, jitter=.26,
                                seed=seed + 10 + i * 2.3)
    for p in hang[1::3]:  # epiphytes perched on the limbs
        a.part('Epiphytes', 'FoliageLight', flat=True).ico((.28, .26, .2), loc=p + Vector((0, 0, .18)), sub=1,
                                                           jitter=.3, seed=p.x)
    vp = a.part('Vines', 'FoliageDark')
    for p in hang[:vines]:
        vine(vp, (p.x, p.y, p.z - .1), rng.uniform(2.0, min(4.5, p.z - .8)), rng)
    for x, y, z in extra:  # long aerial roots, ending just above the ground
        vine(vp, (x, y, z), z - .6, rng, sway=.2, r=.05)


def jungle_tree_a(a):
    """Kapok (about 12.5 m): a tall straight trunk on five big plank buttresses (2 x 2 m), near-level
    limbs under a broad flat-topped canopy about 10 m across, lianas hanging below."""
    jungle_tree(a, 101, 9.6, .5, (.2, .1),
                limbs=[(.84, .3, 2.8, .1), (.88, 1.6, 2.6, .12), (.82, 2.9, 2.9, .08), (.9, 4.2, 2.5, .12),
                       (.86, 5.3, 2.7, .1)],
                crown=[(0, 0, 1.1, 2.3, 1.1, 2), (1.2, -1.3, .7, 1.5, .8, 1), (-1.3, 1.1, .8, 1.5, .8, 1)],
                buttresses=5, reach=1.12, vines=7)


def jungle_tree_b(a):
    """Strangler fig (about 11 m): a thick trunk wrapped in aerial roots on six low buttresses
    (2 x 2 m), a round, dense canopy about 9 m across and long roots hanging to the ground."""
    jungle_tree(a, 113, 6.8, .58, (-.15, .1),
                limbs=[(.7, .6, 2.6, .35), (.78, 2.2, 2.8, .3), (.74, 3.7, 2.5, .35), (.82, 5.2, 2.7, .3)],
                crown=[(0, 0, 1.6, 2.4, 1.5, 2), (.9, .8, 2.6, 1.6, 1.0, 1), (-.8, -.9, 2.4, 1.5, 1.0, 1),
                       (1.4, -1.2, .9, 1.4, .9, 1)],
                buttresses=6, reach=.95, vines=6,
                extra=[(1.5, .9, 5.9), (-1.2, 1.6, 6.1), (.2, -1.9, 5.6), (-1.9, -.5, 5.8)])
    roots = a.part('Aerial_roots', 'Bark')
    rng = random.Random(7)
    for k in range(5):
        t = k * TAU / 5 + .4
        pts = [(math.cos(t + dz * .6) * .62, math.sin(t + dz * .6) * .62, z) for dz, z in ((0, 5.6), (.5, 3.8),
                                                                                      (1.0, 1.8))]
        pts.append((math.cos(t + 1.3) * .92, math.sin(t + 1.3) * .92, -.05))
        roots.tube(pts, .08 * rng.uniform(.8, 1.1), seg=4)


def jungle_tree_c(a):
    """Leaning rainforest giant (about 12 m): a buttressed trunk (2 x 2 m) leaning into heavy limbs,
    an open, lopsided canopy about 9 m across and a curtain of lianas."""
    jungle_tree(a, 127, 8.4, .46, (.75, -.35),
                limbs=[(.62, .4, 3.4, .45), (.72, 3.4, 2.8, .4), (.9, 1.9, 2.4, .3), (.95, 5.4, 2.2, .3),
                       (.8, -1.2, 2.6, .35)],
                crown=[(.3, -.2, 1.5, 2.0, 1.1, 2), (1.6, .6, .9, 1.4, .8, 1)],
                buttresses=4, reach=1.1, vines=10)


def bamboo_clump(a):
    """Bamboo clump (2.5 x 2.5 m base, about 7.5 m): eleven jointed culms arching out of a leafy
    base, with sprays of narrow leaves along their upper halves."""
    rng = random.Random(131)
    culm_parts = [a.part('Culms', 'FoliageLight'), a.part('Culms', 'Foliage')]
    leaf_parts = [a.part('Leaves', 'Foliage'), a.part('Leaves', 'FoliageLight'), a.part('Leaves', 'FoliageDark')]
    stations = 5
    for k in range(11):
        t = k * 2.4 + rng.uniform(-.3, .3)
        rr = .3 + .6 * math.sqrt(rng.random())
        bx, by = math.cos(t) * rr, math.sin(t) * rr
        H = rng.uniform(5.5, 7.4)
        out = Vector((math.cos(t), math.sin(t), 0)) * rng.uniform(.8, 1.9)
        r = rng.uniform(.055, .075)
        spine = [Vector((bx, by, -.05)) + out * (i / (stations - 1)) ** 2.2 + Vector((0, 0, H * i / (stations - 1)))
                 for i in range(stations)]
        secs = [poly(r * (1.18 if i % 2 else 1.0) * (1 - .3 * i / stations), 5, .3 * i) for i in range(stations)]
        loft_along(culm_parts[k % 2], spine, (-math.sin(t), math.cos(t), 0), secs)
        for j, f in enumerate((.55, .72, .9)):
            i = f * (stations - 1)
            i0 = min(int(i), stations - 2)
            base = spine[i0].lerp(spine[i0 + 1], i - i0)
            for b in range(2):
                yaw = t + (b - .5) * 1.4 + rng.uniform(-.3, .3)
                d = Vector((math.cos(yaw), math.sin(yaw), 0))
                L = rng.uniform(.8, 1.1)
                pts = [base, base + d * L * .45 + Vector((0, 0, .12)), base + d * L + Vector((0, 0, -.25))]
                loft_along(leaf_parts[(k + j + b) % 3], pts, (-d.y, d.x, 0),
                           [[(-.02, 0), (0, .02), (.02, 0)], [(-.13, 0), (0, .04), (.13, 0)], []])
    for k in range(4):
        t = k * TAU / 4 + .5
        a.part('Base_leaves', 'FoliageDark', flat=True).ico((.6, .55, .4), loc=(math.cos(t) * .8, math.sin(t) * .8,
                                                                               .2), sub=1, jitter=.3, seed=k * 1.3)
    a.part('Litter', 'Dirt', flat=True).ico((1.2, 1.15, .12), loc=(0, 0, -.02), sub=1, jitter=.2, seed=3)


def fern_bush(a):
    """Fern clump (1.5 x 1.5 m, 0.8 m): nine arching, drooping fronds from a low crown."""
    rng = random.Random(141)
    parts = [a.part('Fronds', m) for m in ('Foliage', 'FoliageLight', 'FoliageDark')]
    for k in range(9):
        yaw = k * TAU / 9 + rng.uniform(-.2, .2)
        d = Vector((math.cos(yaw), math.sin(yaw), 0))
        L = rng.uniform(.72, .8)
        up = rng.uniform(.5, .75)
        spine = [Vector((0, 0, .12)) + d * L * f + Vector((0, 0, h)) for f, h in
                 ((0, 0), (.25, up * .7), (.55, up * .85), (.82, up * .5), (1.0, .1))]
        secs = [[(-q, 0), (0, .025), (q, 0)] for q in (.02, .13, .15, .09)] + [[]]
        loft_along(parts[k % 3], spine, (-d.y, d.x, 0), secs)
    a.part('Crown', 'Bark', flat=True).ico((.16, .16, .14), loc=(0, 0, .1), sub=1, jitter=.2, seed=2)


def mossy(part, rng, x, y, z, r):
    """Irregular flat moss patch standing 5 cm proud of the surface at height z (plus a random
    1.5 cm step, so overlapping patches never share a top face)."""
    z += .015 * rng.randint(0, 3)
    part.prism([(r * math.cos(k * TAU / 6) * rng.uniform(.6, 1.1), r * math.sin(k * TAU / 6) * rng.uniform(.6, 1.1))
                for k in range(6)], .1, loc=(x, y, z), axis='Z', bevel=0)


def temple_ruin(a):
    """Overgrown stepped temple (12 x 12 m, about 10.5 m): four battered stone tiers with cornices
    and carved panels, a steep central stair between balustrades up to a shrine with a dark doorway,
    a corbelled roof and a broken roof comb. Moss on the terraces, bushes, lianas, a strangler fig
    rooted over the back-right corner, guardian statues and a collapsed front-left corner."""
    rng = random.Random(151)
    stone = a.part('Stone', 'Canvas')  # weathered, lichen-grey stone
    trim = a.part('Trim', 'Concrete')
    carve = a.part('Carving', 'RoofSlate')
    dark = a.part('Openings', 'Charred')
    moss = a.part('Moss', 'Grass')
    rubble = a.part('Rubble', 'Canvas', flat=True)
    rise = .3
    # (half size, bottom, top, collapse): tier tops fall at mid-step heights, so no stair tread lies
    # on one; `collapse` cuts a broken notch out of the front-left corner.
    tiers = [(5.8, 0.0, 4.5 * rise, 2.0), (4.7, 4.5 * rise - .02, 9.5 * rise, 1.7),
             (3.65, 9.5 * rise - .02, 13.5 * rise, .9), (2.65, 13.5 * rise - .02, 17.5 * rise, 0)]

    def outline(hs, c):
        if not c:
            return [(-hs, -hs), (hs, -hs), (hs, hs), (-hs, hs)]
        return [(hs, -hs), (hs, hs), (-hs, hs), (-hs, -hs + c), (-hs + c * .22, -hs + c * .7),
                (-hs + c * .5, -hs + c * .62), (-hs + c * .62, -hs + c * .3), (-hs + c, -hs)]
    for i, (hs, z0, z1, c) in enumerate(tiers):
        h = z1 - z0
        k = (hs - .14) / hs
        stone.prism(outline(hs, c), h, loc=(0, 0, z0 + h / 2), axis='Z', taper=k, bevel=.04, seg=1)
        # Cornice band just under the terrace (the terrace itself stays bare stone) and a plinth band.
        trim.prism(outline(hs * k + .12, c * k), .24, loc=(0, 0, z1 - .18), axis='Z', bevel=.03, seg=1)
        stone.prism(outline(hs + .06, c), .28, loc=(0, 0, z0 + .14), axis='Z', bevel=.03, seg=1)
        if c:  # fallen blocks heaped in the notch
            for j in range(4):
                f = .22 + .14 * j
                rubble.box((rng.uniform(.5, .8), rng.uniform(.4, .6), rng.uniform(.3, .4)),
                           loc=(-hs + c * f + rng.uniform(-.1, .1), -hs + c * (.5 - f * .6), z0 + .15 + .2 * (j % 2)),
                           rot=(rng.uniform(-.4, .4), rng.uniform(-.4, .4), rng.uniform(0, 3)), bevel=0)
        # Carved panels (a raised frame round a glyph block) on every face except the stair's middle.
        n = 3 if hs > 4 else 2
        for face, (nx, ny) in NORMAL.items():
            tx, ty = TANGENT[face]
            for j in range(n):
                u = (j - (n - 1) / 2) * (2 * hs / n)
                if face == '-y' and abs(u) < 2.0:
                    continue
                along = nx * 0 + (tx * u + ty * u)  # world x on the -y face, world y on the -x face
                if c and face in ('-y', '-x') and along < -hs + c + .9:
                    continue
                p = (nx * (hs - .07) + tx * u, ny * (hs - .07) + ty * u, z0 + h * .52)
                fbox(trim, face, p, (min(1.5, 2 * hs / n - .5), .2, h * .5), out=.0)
                fbox(carve, face, p, (min(.9, 2 * hs / n - 1.0), .2, h * .3), out=.05)
    # Central stair up the front (-Y) between sloping balustrades.
    steps = 18
    y_foot, y_top = -5.95, -2.65
    run = (y_top - y_foot) / steps
    prof = [(y_foot, 0.0)]
    for k in range(steps):
        y = y_foot + k * run
        prof += [(y, (k + 1) * rise), (y + run, (k + 1) * rise)]
    prof += [(y_top + .6, steps * rise), (y_top + .6, 0.0)]
    stone.prism(prof, 2.6, axis='X', bevel=0)
    zl = steps * rise
    for sx in (-1, 1):
        trim.prism([(y_foot - .05, 0), (y_foot - .05, .75), (y_top - .1, zl + .55), (y_top + .5, zl + .55),
                    (y_top + .5, 0)], .5, loc=(sx * 1.55, 0, 0), axis='X', bevel=.03, seg=1)
    # Shrine: walls with a dark doorway, a corbelled roof and a broken roof comb.
    zs = zl - .02
    sw, sh = 1.55, 2.3
    stone.box((2 * sw, 2 * sw, sh), loc=(0, .3, zs + sh / 2), bevel=.05, seg=1)
    y0s = .3 - sw
    fbox(dark, '-y', (0, y0s, zs + .95), (1.05, .1, 1.85), out=.02)
    for s in (-1, 1):
        fbox(trim, '-y', (s * .72, y0s, zs + .98), (.3, .24, 1.95), out=.05, bevel=.02)
    fbox(trim, '-y', (0, y0s, zs + 2.02), (1.9, .28, .32), out=.06, bevel=.02)
    for face in ('-x', '+x'):
        fbox(dark, face, (-sw if face == '-x' else sw, .3, zs + 1.3), (.5, .1, .7), out=.02)
    zr = zs + sh
    for i, (hs2, hh) in enumerate(((1.82, .3), (1.45, .5), (1.12, .45), (.8, .4))):
        (trim if i == 0 else stone).box((2 * hs2, 2 * hs2, hh + .02), loc=(0, .3, zr + hh / 2 - .01), bevel=.04, seg=1)
        zr += hh
    comb = [(-.75, 0), (.75, 0), (.75, .9), (.4, 1.35), (-.1, 1.05), (-.45, 1.5), (-.75, 1.3)]
    stone.prism(comb, .34, loc=(0, .5, zr - .02), axis='Y', bevel=.02, seg=1)
    for x in (-.4, .35):
        dark.box((.26, .38, .34), loc=(x, .5, zr + .45), bevel=0)
    # Guardian statues on pedestals flanking the stair foot.
    for sx in (-1, 1):
        x = sx * 2.35
        stone.box((.8, .8, .7), loc=(x, -5.45, .35), bevel=.04, seg=1)
        trim.box((.56, .7, .55), loc=(x, -5.45, .97), bevel=.08, seg=1, taper=(.8, .85))
        trim.box((.42, .4, .38), loc=(x, -5.62, 1.4), bevel=.07, seg=1)
        carve.box((.12, .3, .3), loc=(x + sx * .24, -5.4, 1.35), bevel=.03, seg=1)
        mossy(moss, rng, x, -5.42, 1.62, .18)
    # Collapsed front-left corner: tumbled blocks and a rubble heap on the ground.
    chunks = a.part('Rubble', 'Concrete', flat=True)
    for k in range(9):  # on the lowest terrace
        x, y = -4.95 + rng.uniform(-.5, .6), -4.95 + rng.uniform(-.6, .5)
        chunks.box((rng.uniform(.5, .9), rng.uniform(.4, .7), rng.uniform(.3, .45)),
                   loc=(x, y, tiers[0][2] + rng.uniform(.1, .5)),
                   rot=(rng.uniform(-.4, .4), rng.uniform(-.4, .4), rng.uniform(0, 3)), bevel=0)
    for k in range(4):
        chunks.ico((.55, .45, .35), loc=(-5.3 + k * .45, -5.95, .25 + .12 * (k % 2)), sub=1, jitter=.3, seed=k * 1.9)
    for x, y, turn in ((5.2, -6.1, .4), (3.9, -6.15, -.3), (-6.12, 2.6, 1.5), (-5.9, -4.2, .6)):
        chunks.box((.8, .5, .45), loc=(x, y, .2), rot=(0, .05, turn), bevel=0)
    # Moss on the terraces and bushes in their corners.
    for i, (hs, z0, z1, c) in enumerate(tiers[:-1]):
        inner = tiers[i + 1][0]
        for k in range(6):
            t = rng.uniform(0, TAU)
            m = (hs + inner) / 2 - .1
            x, y = max(-m, min(m, math.cos(t) * m * 1.3)), max(-m, min(m, math.sin(t) * m * 1.3))
            if y < -inner and abs(x) < 2.1:
                x = 2.6 * (1 if x >= 0 else -1)
            if x < -hs + c + .3 and y < -hs + c + .3:
                continue  # the collapsed corner
            mossy(moss, rng, x, y, z1 + .04, (hs - inner) * .55)
    bush = [a.part('Bushes', 'FoliageDark', flat=True), a.part('Bushes', 'Foliage', flat=True)]
    for k, (x, y, z, r) in enumerate(((-5.2, 4.9, tiers[0][2], .7), (5.2, -5.0, tiers[0][2], .6),
                                      (-4.1, -4.1, tiers[1][2], .55), (4.15, 1.6, tiers[1][2], .5),
                                      (-3.1, 2.6, tiers[2][2], .45), (5.3, 1.8, tiers[0][2], .6),
                                      (-5.25, -1.8, tiers[0][2], .55))):
        bush[k % 2].ico((r, r * .9, r * .7), loc=(x, y, z + r * .35), sub=2, jitter=.25, seed=k * 2.2 + 1)
    # Strangler fig rooted over the back-right corner, its roots draped down the tiers.
    fig = a.part('Fig', 'Bark')
    base = Vector((4.2, 4.2, tiers[1][2]))
    lean = Vector((-.5, -.4, 4.2))
    loft_along(fig, [base + Vector((0, 0, -.2)), base + lean * .45, base + lean], (1, 0, 0),
               [poly(.4, 6), poly(.3, 6, .3), poly(.24, 6, .6)])
    z0t = tiers[0][2] + .06
    for t in (-.5, .2, .8, 1.4, 2.0):
        d = Vector((math.cos(t), math.sin(t), 0))
        pts = [base + d * .12 + Vector((0, 0, .8 - .06 * t)), base + d * .55 + Vector((0, 0, .08)), base + d * .9,
               base + d * 1.45, base + d * 1.85]
        for q, z in zip(pts[2:], (z0t + .12, z0t + .1, -.05)):
            q.z = z
        fig.tube([tuple(p) for p in pts], .1, seg=4)
    ftop = base + lean
    leaves = [a.part('Fig_leaves', 'Foliage', flat=True), a.part('Fig_leaves', 'FoliageDark', flat=True)]
    for k, (x, y, z, r) in enumerate(((0, 0, .6, 2.3), (-1.4, .6, .1, 1.5), (.9, -1.3, -.1, 1.5))):
        limb(fig, ftop, ftop + Vector((x * .7, y * .7, z)), .18, .09)
        leaves[k % 2].ico((r, r * .9, r * .55), loc=ftop + Vector((x, y, z + .5)), sub=2, jitter=.28, seed=k * 3.1)
    # Lianas hanging over the tier edges.
    vp = a.part('Vines', 'FoliageDark')
    for x, y, i in ((-2.2, -4.72, 1), (1.4, -3.68, 2), (4.72, -1.0, 1), (4.72, 2.2, 1), (-4.72, .8, 1),
                    (-3.68, -1.9, 2), (3.68, .5, 2), (-2.1, -2.7, 3), (2.4, -4.72, 1), (3.1, -3.68, 2),
                    (5.84, -3.4, 0), (2.69, -1.6, 3), (5.84, .6, 0)):
        z = tiers[i][2] + .08
        vine(vp, (x * 1.01, y * 1.01, z), z * rng.uniform(.4, .75), rng, sway=.1, r=.045)


def thatch_course(part, rng, length, width, loc, rot, thick=.12, teeth=14, depth=.24):
    """Course of palm thatch lying in its local XY plane (X along the ridge, Y up the slope) with a
    ragged lower edge, `thick` along local Z (the roof normal)."""
    pts = []
    for i in range(teeth + 1):
        x = -length / 2 + length * (i + (rng.uniform(-.3, .3) if 0 < i < teeth else 0)) / teeth
        pts.append((x, -width / 2 - (depth * rng.uniform(.4, 1.3) if i % 2 else depth * rng.uniform(0, .25))))
    pts += [(length / 2, width / 2), (-length / 2, width / 2)]
    part.prism(pts, thick, loc=loc, rot=rot, axis='Z', bevel=0)


def stilt_hut(a):
    """Stilt hut (7 x 6 m, about 7 m): a woven-bamboo room and a railed veranda on a plank deck
    2.1 m up on twelve log stilts, under a steep layered palm-thatch roof. A ladder up to the
    veranda, propped shutters (some windows lit), a lantern at the door, pots, a hammock, a
    woodpile and a dugout canoe under the floor."""
    rng = random.Random(161)
    logw = a.part('Stilts', 'LogWood')
    wood = a.part('Wood', 'Wood')
    fl = 2.1
    xs, ys = (-2.8, -.93, .93, 2.8), (-2.15, .1, 2.15)
    for x in xs:
        for y in ys:
            logw.cyl(.12, fl - .08, loc=(x, y, (fl - .08) / 2 - .06), seg=6, bevel=0)
            a.part('Footings', 'Concrete', flat=True).ico((.26, .23, .1), loc=(x, y, 0), sub=1, jitter=.2, seed=x + y)
    for y in (ys[0], ys[-1]):  # X braces along the front and back rows
        for x0, x1 in ((xs[0], xs[1]), (xs[2], xs[3])):
            wood.limb((x0, y + .1, .35), (x1, y + .1, fl - .4), .08, .06, bevel=0)
            wood.limb((x1, y + .14, .35), (x0, y + .14, fl - .4), .08, .06, bevel=0)
    for x in (xs[0], xs[-1]):
        wood.limb((x + .1, ys[0], .35), (x + .1, ys[1], fl - .4), .06, .08, bevel=0)
    for y in ys:
        wood.box((6.0, .16, .2), loc=(0, y, fl - .22), bevel=.02, seg=1)
    for x in xs:
        wood.box((.14, 4.7, .16), loc=(x, 0, fl - .16), bevel=0)
    wood.box((6.1, 4.8, .1), loc=(0, 0, fl - .05), bevel=.02, seg=1)
    a.part('Deck_edge', 'LogWood').box((6.14, .14, .14), loc=(0, -2.38, fl - .09), bevel=0)
    # Room: woven walls between corner posts, with battens.
    wx, wy0, wy1, wh = 2.5, -.75, 2.25, 2.1
    top = fl + wh
    a.part('Walls', 'Canvas').box((2 * wx, wy1 - wy0, wh + .02), loc=(0, (wy0 + wy1) / 2, fl + wh / 2 - .01), bevel=.02,
                                  seg=1)
    for x in (-wx, wx):
        for y in (wy0, wy1):
            logw.cyl(.1, wh + .25, loc=(x, y, fl + (wh + .25) / 2), seg=6, bevel=0)
    bat = a.part('Battens', 'LogWood')
    for z in (fl + .12, top - .1):
        for face, p, L in (('+y', (0, wy1), 2 * wx), ('-x', (-wx, (wy0 + wy1) / 2), wy1 - wy0),
                           ('+x', (wx, (wy0 + wy1) / 2), wy1 - wy0)):
            fbox(bat, face, (p[0], p[1], z), (L - .2, .08, .07), out=.03)
        for x0b, x1b in ((-wx + .1, -1.5), (-.3, wx - .1)):  # the front battens stop at the door posts
            fbox(bat, '-y', ((x0b + x1b) / 2, wy0, z), (x1b - x0b, .08, .07), out=.03)
    # Door with a half-drawn curtain, windows with shutters propped open on sticks.
    dark = a.part('Openings', 'Charred')
    fbox(dark, '-y', (-.9, wy0, fl + .95), (.95, .08, 1.85), out=.01)
    fbox(a.part('Curtain', 'WoodRed'), '-y', (-1.15, wy0, fl + 1.0), (.43, .03, 1.72), out=.05)
    for s in (-1, 1):
        fbox(wood, '-y', (-.9 + s * .52, wy0, fl + .95), (.1, .1, 1.95), out=.04)
    fbox(wood, '-y', (-.9, wy0, fl + 1.93), (1.2, .14, .12), out=.05)

    def shutter_window(face, p, w=.85, h=.7):
        fbox(pane(a, rng, .5) if rng.random() < .6 else dark, face, p, (w, .06, h), out=.01)
        nx, ny = NORMAL[face]
        for s in (-1, 1):
            fbox(wood, face, slide(face, p, s * (w / 2 + .05)), (.08, .08, h + .1), out=.04)
        fbox(wood, face, slide(face, p, 0, -h / 2 - .05), (w + .2, .12, .08), out=.05)
        # Shutter hinged along the head, propped out at 50 degrees.
        ang = math.radians(50)
        hx, hy, hz = p[0] + nx * .06, p[1] + ny * .06, p[2] + h / 2 + .04
        L = h + .05
        cx, cy, cz = hx + nx * math.sin(ang) * L / 2, hy + ny * math.sin(ang) * L / 2, hz - math.cos(ang) * L / 2
        size = (w + .06, .05, L) if nx == 0 else (.05, w + .06, L)
        wood.box(size, loc=(cx, cy, cz), rot=(ang * ny, -ang * nx, 0), bevel=0)
        end = (hx + nx * math.sin(ang) * L, hy + ny * math.sin(ang) * L, hz - math.cos(ang) * L)
        wood.limb((hx + nx * .02, hy + ny * .02, p[2] - h / 2), (end[0] - nx * .04, end[1] - ny * .04, end[2] + .04),
                  .03, .03, bevel=0)
    shutter_window('-y', (1.2, wy0, fl + 1.3))
    shutter_window('+x', (wx, .8, fl + 1.3))
    shutter_window('-x', (-wx, .9, fl + 1.3))
    shutter_window('+y', (-.8, wy1, fl + 1.3))
    # Roof: thick thatch on a ridge along X, layered in three courses per slope, a rolled ridge cap.
    ze, zr, hy = 3.85, 6.7, 3.0

    def under(y):
        return ze + (zr - ze) * (1 - abs(y) / hy)
    thatch = a.part('Thatch', 'Sandbag')
    outer = roof_shell(thatch, [(-hy, ze), (0, zr)], 6.9, 'x', t=.3, bevel=.05)
    # Three courses per slope with ragged lower edges; each overlaps the top of the one below.
    (ey, ez), (_, rz) = outer[0], outer[1]
    alpha = math.atan2(rz - ez, -ey)
    slope = math.hypot(rz - ez, ey)
    for side, turn in ((-1, 0.0), (1, math.pi)):
        up = Vector((0, -side * math.cos(alpha), math.sin(alpha)))
        nrm = Vector((0, side * math.sin(alpha), math.cos(alpha)))
        eave = Vector((0, side * -ey, ez))
        for i, (f0, f1) in enumerate(((0.0, .4), (.34, .72), (.66, 1.0))):
            lift = -.03 + .06 * i
            c = eave + up * ((f0 + f1) / 2 * slope) + nrm * (lift + .06)
            thatch_course(a.part('Thatch_courses', 'Sandbag' if i != 1 else 'Canvas'), rng, 7.02 - .04 * i,
                          (f1 - f0) * slope, tuple(c), (alpha, 0, turn))
    a.part('Ridge', 'Canvas').cyl(.24, 7.0, loc=(0, 0, outer[1][1] + .02), rot=ALONG_X, seg=8, bevel=.03, bseg=1)
    for x in (-3.0, -1.0, 1.0, 3.0):  # ridge bindings
        a.part('Ridge_ties', 'LogWood').cyl(.26, .12, loc=(x, 0, outer[1][1] + .02), rot=ALONG_X, seg=8, bevel=0)
    gable = a.part('Gables', 'Canvas')
    for x in (-wx, wx):
        gable.prism([(wy0, top - .02), (wy1, top - .02), (wy1, under(wy1) - .02), (0, zr - .02),
                     (wy0, under(wy0) - .02)], .1, loc=(x, 0, 0), axis='X', bevel=0)
    # Veranda: posts up to the eave, railings with a gap for the ladder.
    yf = -2.3
    for x in xs:
        logw.cyl(.09, under(yf) - fl + .05, loc=(x, yf, (under(yf) + fl) / 2), seg=6, bevel=0)
    rail = a.part('Railing', 'LogWood')
    lx = 1.87
    for z in (fl + .45, fl + .92):
        for x0, x1 in ((-2.8, lx - .45), (lx + .45, 2.8)):
            rail.box((x1 - x0, .07, .07), loc=((x0 + x1) / 2, yf - .1, z), bevel=0)
        for x in (-2.95, 2.95):
            rail.box((.07, wy0 - yf, .07), loc=(x, (yf + wy0) / 2, z), bevel=0)
    for x in (-1.9, 0.0, .5):
        rail.box((.06, .09, .9), loc=(x, yf - .1, fl + .45), bevel=0)
    # Ladder up to the gap in the railing.
    lad = a.part('Ladder', 'LogWood')
    y_foot, y_head = -2.98, -2.42
    for s in (-1, 1):
        lad.limb((lx + s * .27, y_foot, -.02), (lx + s * .27, y_head, fl + .7), .07, .07, bevel=0)
    for i in range(7):
        z = .3 + i * .3
        lad.box((.54, .05, .05), loc=(lx, y_foot + (y_head - y_foot) * z / (fl + .72), z), bevel=0)
    # Lantern by the door, pots, a basket, a bench and a fishing net on the railing.
    zl = under(-1.4) - .05
    a.part('Lantern_cord', 'Armor').box((.02, .02, zl - (fl + 1.95)), loc=(-.1, -1.4, (zl + fl + 1.95) / 2), bevel=0)
    a.part('Lantern', 'Lamp').box((.18, .18, .24), loc=(-.1, -1.4, fl + 1.84), bevel=.03, seg=1)
    a.part('Lantern_cap', 'Armor').cyl(.14, .07, loc=(-.1, -1.4, fl + 1.98), r2=.04, seg=6, bevel=0)
    jars = a.part('Pots', 'Brick')
    pot(jars, 2.45, -1.2, fl, s=.9)
    pot(jars, 2.55, -.8, fl, s=.7)
    pot(jars, -2.2, -1.9, fl, s=.8)
    a.part('Basket', 'Canvas').cyl(.26, .32, loc=(-2.5, -1.3, fl + .16), r2=.3, seg=8, bevel=.02, bseg=1)
    wood.box((1.3, .4, .08), loc=(.2, -1.05, fl + .45), bevel=.02, seg=1)
    for sx in (-1, 1):
        wood.box((.08, .32, .4), loc=(.2 + sx * .5, -1.05, fl + .2), bevel=0)
    a.part('Net', 'Canvas').box((1.4, .04, .6), loc=(-1.1, yf - .14, fl + .62), rot=(.08, 0, 0), bevel=0)
    # Under the floor: a hammock between two stilts, a woodpile, a dugout canoe and a water jar.
    ham = a.part('Hammock', 'WoodRed')
    pts = [(-2.72, 1.45), (-2.2, 1.02), (-1.85, .92), (-1.5, 1.02), (-1.0, 1.45)]
    ham.loft([[(x, .5, z + .06), (x, .1, z - .02), (x, -.3, z + .06), (x, .1, z + .02)] for x, z in pts])
    pile = a.part('Woodpile', 'Wood')
    for row, count in enumerate((4, 3, 2)):
        for j in range(count):
            pile.cyl(.1, .9, loc=(1.5 + (j + row * .5) * .21, 1.4, .1 + row * .18), rot=ALONG_Y, seg=5, bevel=0)
    hull = [(-1.6, 0), (-1.2, -.2), (-.5, -.33), (.5, -.33), (1.2, -.2), (1.6, 0), (1.2, .2), (.5, .33), (-.5, .33),
            (-1.2, .2)]
    a.part('Canoe', 'Wood').prism(hull, .34, loc=(0, -1.0, .15), axis='Z', bevel=.03, seg=1)
    a.part('Canoe_inside', 'Charred').prism([(x * .82, y * .7) for x, y in hull], .1, loc=(0, -1.0, .285), axis='Z',
                                            bevel=0)
    pot(jars, -1.6, 1.3, 0.0, s=1.1)
    vp = a.part('Vines', 'FoliageDark')
    vine(vp, (2.9, 2.2, fl - .1), fl - .1, rng, sway=.12, r=.04)


# ----------------------------------------------------------------------------- airbase
SEGMENTS = {'0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc', '5': 'afgcd', '6': 'afgedc', '7': 'abc',
            '8': 'abcdefg', '9': 'abcdfg'}


def numeral(part, text, face, p, h=1.0, t=.14, out=.03):
    """Seven-segment numerals centred on wall point p (hangar numbers, stencils). Uprights stand
    1.2 cm further out than the bars, so no two segment faces are coplanar."""
    w = h * .55
    pitch = w + h * .35
    for k, ch in enumerate(text):
        c = slide(face, p, (k - (len(text) - 1) / 2) * pitch)
        bar = w + t - .02
        spots = {'a': (0, h / 2, bar, t, 0), 'g': (0, 0, bar, t, 0), 'd': (0, -h / 2, bar, t, 0),
                 'f': (-w / 2, h / 4, t, h / 2, .012), 'b': (w / 2, h / 4, t, h / 2, .012),
                 'e': (-w / 2, -h / 4, t, h / 2, .012), 'c': (w / 2, -h / 4, t, h / 2, .012)}
        for s in SEGMENTS[ch]:
            u, v, su, sv, o = spots[s]
            fbox(part, face, slide(face, c, u, v), (su, .04, sv), out=out + o)


def octagon(r, z, turn=math.pi / 8):
    return [(r * math.cos(turn + k * TAU / 8), r * math.sin(turn + k * TAU / 8), z) for k in range(8)]


def quad(part, a0, a1, b1, b0):
    """Single-sided quad a0 a1 b1 b0, facing the side from which it winds counter-clockwise."""
    part.mesh([a0, a1, b1, b0], [(0, 1, 2, 3)])


def hangar(a):
    """Arched aircraft hangar (22 x 16 m, 10.5 m): a corrugated barrel-vault roof with standing
    seams, skylights and ridge vents on low concrete walls; the front gable's 12 m door has four
    sliding leaves on floor rails, half open, showing the lit, hollow interior with a tug and carts
    on the painted floor. A number board over the door, floodlights, side windows and door, an
    office annex on the right and a gas bottle rack on the left."""
    rng = random.Random(171)
    hw, Hw, apex = 9.3, 3.0, 10.3
    R = (hw * hw + (apex - Hw) ** 2) / (2 * (apex - Hw))
    zc = apex - R
    y0, y1 = -7.3, 7.6
    cy, L = (y0 + y1) / 2, y1 - y0

    def arch(x, lift=0.0):
        return zc + math.sqrt(max(0.0, R * R - x * x)) + lift
    a.part('Slab', 'Concrete').box((21.6, 15.9, .08), loc=(.2, -.05, -.01), bevel=.02, seg=1)
    # Barrel-vault roof over low walls.
    th0 = math.acos((hw + .06) / R)
    prof = [(-R * math.cos(th0 + (R90 - th0) * i / 8), zc + R * math.sin(th0 + (R90 - th0) * i / 8)) for i in range(9)]
    outer = roof_shell(a.part('Roof', 'Corrugated'), prof, L + .6, 'y', t=.22, centre=(0, cy), bevel=.03)
    wall = a.part('Walls', 'Concrete')
    for sx in (-1, 1):
        x0, x1 = sx * (hw - .3), sx * hw
        wall.prism([(x0, 0), (x1, 0), (x1, arch(hw) + .06), (x0, arch(hw - .3) + .06)], L - .04, loc=(0, cy, 0),
                   axis='Y', bevel=.02, seg=1)
    sheet = a.part('Gables', 'MetalSheet')
    gw = hw - .05  # gables stop 5 cm inside the side walls' outer faces
    top = [(x, arch(x, .1)) for x in (gw * math.cos(math.pi * i / 16) for i in range(17))]
    sheet.prism([(-gw, 0), (gw, 0)] + top, .3, loc=(0, y1 - .15, 0), axis='Y', bevel=.02, seg=1)
    dw, dh = 6.0, 6.6
    fy = y0 + .15
    for sx in (-1, 1):
        xs = [sx * (dw + (gw - dw) * i / 6) for i in range(7)]
        sheet.prism([(sx * gw, 0), (sx * dw, 0)] + [(x, arch(x, .1)) for x in xs], .3, loc=(0, fy, 0), axis='Y',
                    bevel=.02, seg=1)
    sheet.prism([(-dw, dh), (dw, dh)] + [(x, arch(x, .1)) for x in (dw * (1 - 2 * i / 10) for i in range(11))], .3,
                loc=(0, fy, 0), axis='Y', bevel=.02, seg=1)
    # Door opening trim, header beam and floor rails.
    haz = a.part('Door_edges', 'Hazard')
    for sx in (-1, 1):
        fbox(haz, '-y', (sx * (dw + .16), y0, dh / 2), (.32, .08, dh), out=.03)
    steel = a.part('Steel', 'Steel')
    track = a.part('Door_track', 'Armor')
    track.box((2 * hw - .4, .9, .36), loc=(0, y0 - .42, dh + .2), bevel=.03, seg=1)
    for yy in (y0 - .3, y0 - .62):
        steel.box((2 * hw - .6, .12, .05), loc=(0, yy, .03), bevel=0)
    # Four leaves, half open: each inner leaf has slid over its outer one on the front track.
    for sx in (-1, 1):
        for x_in, x_out, yy in ((dw + .25, 3.1, y0 - .3), (5.95, 2.8, y0 - .62)):
            xa, xb = sx * x_in, sx * x_out
            xm, lw = (xa + xb) / 2, abs(xa - xb)
            a.part('Door_leaves', 'MetalSheet').box((lw, .14, dh - .04), loc=(xm, yy, dh / 2 + .02), bevel=.02, seg=1)
            ribs = a.part('Door_ribs', 'Armor')
            for z in (.9, 2.3, 3.7, 5.1, 6.1):
                ribs.box((lw - .1, .05, .08), loc=(xm, yy - .085, z), bevel=0)
            for k in range(2):
                fbox(pane(a, rng, .1), '-y', (xm - lw / 4 + k * lw / 2, yy - .07, 4.4), (lw * .36, .04, .6), out=.02)
            fbox(haz, '-y', (xb - sx * .08, yy - .07, dh / 2), (.14, .04, dh - .3), out=.02)
    # Number board and floodlights over the door.
    board = a.part('Board', 'Armor')
    fbox(board, '-y', (0, y0, 7.75), (3.2, .08, 1.3), out=.04)
    numeral(a.part('Numbers', 'PlasterWhite'), '07', '-y', (0, y0 - .08, 7.75), h=.9, t=.14, out=.02)
    for sx in (-1, 1):
        steel.limb((sx * 4.2, y0 - .02, 7.9), (sx * 4.2, y0 - .7, 8.2), .07, .07, bevel=0)
        a.part('Floodlights', 'Armor').box((.5, .3, .3), loc=(sx * 4.2, y0 - .8, 8.25), rot=(-.5, 0, 0), bevel=.03,
                                           seg=1)
        a.part('Flood_lens', 'Lamp').box((.42, .04, .22), loc=(sx * 4.2, y0 - .92, 8.18), rot=(-.5, 0, 0), bevel=0)
    # Interior: painted floor, a tug, carts and drums in the light of the ceiling lamps.
    paint = a.part('Floor_paint', 'Hazard')
    paint.box((.2, 8.0, .03), loc=(0, y0 + 3.8, .04), bevel=0)
    paint.box((5.0, .2, .03), loc=(0, y0 + 1.2, .06), bevel=0)
    tug = a.part('Tug', 'Hazard')
    tug.box((1.3, 2.3, .7), loc=(1.9, y0 + 3.4, .7), bevel=.08, seg=1)
    tug.box((1.1, .8, .5), loc=(1.9, y0 + 3.9, 1.25), bevel=.06, seg=1)
    for dx in (-.62, .62):
        for dy in (-.7, .7):
            a.part('Tug_wheels', 'Rubber').cyl(.32, .25, loc=(1.9 + dx, y0 + 3.4 + dy, .32), rot=ALONG_X, seg=10,
                                               bevel=0)
    a.part('Carts', 'BarrelRed').box((.9, .6, .9), loc=(-2.1, y0 + 2.4, .5), bevel=.04, seg=1)
    a.part('Carts', 'BarrelRed').box((.7, .5, 1.3), loc=(-3.0, y0 + 2.9, .7), bevel=.04, seg=1)
    for x, y in ((-1.2, y0 + 4.6), (-.6, y0 + 4.9)):
        a.part('Drums', 'Fuel').cyl(.3, .9, loc=(x, y, .48), seg=10, bevel=.02, bseg=1)
    lamp = a.part('Ceiling_lamps', 'Lamp')
    for yy in (y0 + 3.0, y0 + 7.5, y0 + 12.0):
        for x in (-3.5, 3.5):
            lamp.box((1.2, .3, .1), loc=(x, yy, arch(x) - .35), bevel=0)
            steel.box((.03, .03, .3), loc=(x, yy, arch(x) - .15), bevel=0)
    # Roof: standing seams, skylights on both flanks, ridge ventilators.
    seams = a.part('Roof_seams', 'Steel')
    for k in range(8):
        yy = y0 - .15 + k * (L + .3) / 7
        seams.tube([(u * 1.004, yy, z + .03) for u, z in outer], .05, seg=3)
    glass = a.part('Skylights', 'Glass')
    for side in (-1, 1):
        (u0, z0), (u1, z1) = outer[3 if side < 0 else 13], outer[4 if side < 0 else 12]
        ang = math.atan2(z1 - z0, u1 - u0)
        seg_len = math.hypot(u1 - u0, z1 - z0)
        nu, nz = -math.sin(ang), math.cos(ang)
        if nz < 0:
            nu, nz = -nu, -nz
        step = (L + .3) / 7
        for k in range(3):
            yy = y0 - .15 + (2 * k + 1.5) * step
            glass.box((seg_len * .85, 1.7, .06), loc=((u0 + u1) / 2 + nu * .05, yy, (z0 + z1) / 2 + nz * .05),
                      rot=(0, -ang, 0), bevel=0)
    vent = a.part('Vents', 'MetalSheet')
    for yy in (y0 + 2.0, cy, y1 - 2.0):
        vent.cyl(.32, .6, loc=(0, yy, apex + .22 + .25), seg=10, bevel=0)
        vent.cyl(.46, .16, loc=(0, yy, apex + .22 + .62), r2=.2, seg=10, bevel=0)
    # Side walls: windows, a personnel door with a lamp, downpipes.
    for y in (-4.5, -1.5, 1.5, 4.5):
        window(a, rng, '-x', (-hw, y, 1.9), w=1.8, h=.9, frame='Steel', mullion=1, lit=.3, sill=None)
    for y in (1.5, 4.5):
        window(a, rng, '+x', (hw, y, 1.9), w=1.8, h=.9, frame='Steel', mullion=1, lit=.3, sill=None)
    door(a, '-x', (-hw, -6.3, .03), w=1.0, h=2.1, mat='Steel', frame='Armor', step=None, lamp=True)
    for sx in (-1, 1):
        for y in (-3.0, 3.0):
            steel.cyl(.07, 2.7, loc=(sx * (hw + .1), y, 1.35), seg=6, bevel=0)
    # Office annex on the right front.
    ax0, ax1, ay0, ay1, ah = hw - .05, 11.0, -6.9, -1.0, 3.3
    axc, ayc = (ax0 + ax1) / 2, (ay0 + ay1) / 2
    a.part('Annex', 'PlasterWhite').box((ax1 - ax0, ay1 - ay0, ah), loc=(axc, ayc, ah / 2), bevel=.04, seg=1)
    a.part('Annex_roof', 'MetalSheet').box((ax1 - ax0 + .3, ay1 - ay0 + .4, .14), loc=(axc + .1, ayc, ah + .06),
                                           bevel=.03, seg=1)
    window(a, rng, '-y', (axc, ay0, 1.8), w=1.1, h=1.0, frame='Steel', mullion=1, lit=.6)
    for y in (-5.5, -3.9):
        window(a, rng, '+x', (ax1, y, 1.8), w=1.1, h=1.0, frame='Steel', mullion=1, lit=.5)
    door(a, '+x', (ax1, -2.1, .03), w=.95, h=2.1, mat='Steel', frame='Armor', step=None, lamp=True)
    ac_unit(a, '+y', (axc, ay1, 2.4))
    a.part('Roof_AC', 'MetalSheet').box((1.0, 1.2, .6), loc=(axc, -4.8, ah + .43), bevel=.04, seg=1)
    a.part('AC_fan', 'Rubber').cyl(.3, .04, loc=(axc, -4.6, ah + .74), seg=10, bevel=0)
    fbox(a.part('Sign', 'ContainerBlue'), '-y', (axc, ay0, 2.85), (1.5, .06, .4), out=.03)
    # Gas bottle rack on the left.
    a.part('Rack_pad', 'Concrete').box((1.0, 2.4, .12), loc=(-10.1, 2.6, .06), bevel=.02, seg=1)
    for k in range(5):
        a.part('Bottles', 'Hazard' if k % 2 else 'Steel').cyl(.14, 1.5, loc=(-10.1 + (k % 2) * .3 - .15, 1.7 + k * .45,
                                                                           .87), seg=8, bevel=.03, bseg=1)
    cage = a.part('Rack', 'Armor')
    for y in (1.4, 3.8):
        cage.box((.06, .06, 1.7), loc=(-10.5, y, .95), bevel=0)
        cage.box((.06, .06, 1.7), loc=(-9.7, y, .95), bevel=0)
    for z in (.7, 1.6):
        cage.box((.06, 2.5, .06), loc=(-10.52, 2.6, z), bevel=0)


def control_tower(a):
    """Airfield control tower (6 x 6 m, 14.8 m to the antenna tips): a two-storey operations block,
    a concrete shaft with a lit stair-window strip, and on a railed octagonal floor a flared glass
    cab (two panes lit) under an overhanging roof carrying a surface radar that spins on its
    `Radar` pivot, a beacon, whip antennas with red obstruction lights and an anemometer."""
    rng = random.Random(181)
    conc = a.part('Walls', 'Concrete')
    bw, bh = 2.9, 3.6
    conc.box((2 * bw, 2 * bw, bh), loc=(0, 0, bh / 2), bevel=.04, seg=1)
    conc.shell([(-bw - .02, -bw - .02), (bw + .02, -bw - .02), (bw + .02, bw + .02), (-bw - .02, bw + .02)], .5, .22,
               loc=(0, 0, bh - .02))
    a.part('Roof_deck', 'Asphalt').box((2 * bw - .3, 2 * bw - .3, .1), loc=(0, 0, bh + .02), bevel=0)
    a.part('Band', 'PlasterWhite').box((2 * bw + .06, 2 * bw + .06, .3), loc=(0, 0, .9), bevel=.02, seg=1)
    door(a, '-y', (-1.5, -bw, .0), w=1.1, h=2.1, mat='Glass', frame='Steel', step=None, lamp=True)
    conc.box((2.0, .55, .16), loc=(-1.5, -bw - .24, 2.45), bevel=.03, seg=1)
    for x in (.4, 1.9):
        window(a, rng, '-y', (x, -bw, 2.0), w=1.0, h=1.1, frame='Steel', mullion=1, lit=.4)
    for face, p in (('+x', (bw, -1.2)), ('+x', (bw, 1.2)), ('-x', (-bw, -1.2)), ('-x', (-bw, 1.2)), ('+y', (-1.2, bw)),
                    ('+y', (1.2, bw))):
        window(a, rng, face, (p[0], p[1], 2.0), w=1.0, h=1.1, frame='Steel', mullion=1, lit=.4)
    a.part('Sign', 'ContainerBlue').box((1.9, .06, .38), loc=(-1.5, -bw - .53, 2.75), bevel=0)
    letters(a, rng, '-y', (-1.5, -bw - .56, 2.75), 1.6, h=.26, mat='PlasterWhite', out=.0)
    ac_unit(a, '+x', (bw, 0, 3.0))
    for x, y in ((1.7, 1.6), (-1.8, 1.7)):
        a.part('Roof_AC', 'MetalSheet').box((1.0, .8, .6), loc=(x, y, bh + .37), bevel=.04, seg=1)
        a.part('AC_fan', 'Rubber').cyl(.26, .04, loc=(x, y, bh + .68), seg=10, bevel=0)
    # Shaft with a strip of stair windows and groove bands.
    sw, s0, s1 = 1.4, bh - .02, 10.62
    conc.box((2 * sw, 2 * sw, s1 - s0), loc=(0, 0, (s0 + s1) / 2), bevel=.04, seg=1)
    for z in (5.3, 6.9, 8.5):
        a.part('Grooves', 'Armor').box((2 * sw + .04, 2 * sw + .04, .08), loc=(0, 0, z), bevel=0)
    for z in (4.5, 6.1, 7.7, 9.3):
        fbox(a.part('Frames', 'Steel'), '-y', (0, -sw, z), (.8, .1, 1.05), out=.03)
        fbox(pane(a, rng, .5), '-y', (0, -sw, z), (.62, .06, .85), out=.065)
    for face, p in (('+x', (sw, 0)), ('-x', (-sw, 0))):
        fbox(a.part('Frames', 'Steel'), face, (p[0], p[1], 9.3), (.8, .1, .7), out=.03)
        fbox(pane(a, rng, .5), face, (p[0], p[1], 9.3), (.62, .06, .52), out=.065)
    # Cab floor with a railing, flared glass cab, mullions and a sill band.
    fz = 10.93
    conc.cyl(2.95, .35, loc=(0, 0, fz - .175), seg=8, rot=(0, 0, math.pi / 8), bevel=.03, bseg=1)
    rail = a.part('Railing', 'Hazard')
    ring = octagon(2.84, fz)
    for x, y, z in ring:
        rail.box((.06, .06, 1.05), loc=(x, y, z + .5), bevel=0)
    for h in (.52, 1.02):
        rail.tube([(x, y, z + h) for x, y, z in ring + ring[:1]], .03, seg=4, caps=False)
    glass = a.part('Cab_glass', 'Glass')
    lo, hi = octagon(2.3, fz - .03), octagon(2.72, 12.85)
    glass.loft([lo, hi])
    a.part('Sill', 'Concrete').cyl(2.42, .4, loc=(0, 0, fz + .17), seg=8, rot=(0, 0, math.pi / 8), bevel=.02, bseg=1)
    mull = a.part('Mullions', 'Armor')
    for (x0, y0, _), (x1, y1, _) in zip(octagon(2.39, 0), octagon(2.74, 0)):
        mull.limb((x0, y0, fz + .3), (x1, y1, 12.86), .1, .1, bevel=0)
    lit = a.part('Cab_lit', 'Lamp')
    for k in (5, 6):  # the front-right panes glow
        b0, b1 = Vector(octagon(2.3 + .02, 0)[k]), Vector(octagon(2.3 + .02, 0)[(k + 1) % 8])
        t0, t1 = Vector(octagon(2.72 + .02, 0)[k]), Vector(octagon(2.72 + .02, 0)[(k + 1) % 8])
        zb, zt = fz + .45, 12.72
        fb, ft = (zb - (fz - .03)) / (12.85 - fz + .03), (zt - (fz - .03)) / (12.85 - fz + .03)
        pb0, pb1 = b0.lerp(t0, fb), b1.lerp(t1, fb)
        pt0, pt1 = b0.lerp(t0, ft), b1.lerp(t1, ft)
        q = [pb0.lerp(pb1, .1), pb0.lerp(pb1, .9), pt0.lerp(pt1, .9), pt0.lerp(pt1, .1)]
        quad(lit, *[(p.x, p.y, z) for p, z in zip(q, (zb, zb, zt, zt))])
    # Roof: overhanging slab, radar on its pivot, beacon, antennas, anemometer.
    rz = 12.84
    a.part('Cab_roof', 'Armor').cyl(3.02, .36, loc=(0, 0, rz + .18), seg=8, rot=(0, 0, math.pi / 8), bevel=.04, bseg=1)
    a.part('Roof_edge', 'PlasterWhite').cyl(3.06, .14, loc=(0, 0, rz + .12), seg=8, rot=(0, 0, math.pi / 8), bevel=0)
    top = rz + .36
    steel = a.part('Steel', 'Steel')
    steel.cyl(.18, .52, loc=(0, 0, top + .24), seg=8, bevel=0)
    r = a.pivot('Radar', (0, 0, top + .5))
    a.part('Radar_mount', 'Armor', r).box((.32, .32, .26), loc=(0, 0, .13), bevel=.03, seg=1)
    a.part('Radar_array', 'Armor', r).box((2.5, .22, .34), loc=(0, 0, .45), bevel=.03, seg=1)
    a.part('Radar_face', 'Medical', r).box((2.36, .05, .26), loc=(0, -.12, .45), bevel=0)
    a.part('Beacon', 'Lamp').sphere(.14, loc=(1.9, 1.1, top + .5), seg=8, rings=5)
    steel.cyl(.04, .35, loc=(1.9, 1.1, top + .17), seg=6, bevel=0)
    red = a.part('Obstruction_lights', 'LavaGlow')
    for x, y, h in ((-2.0, .7, 1.25), (-1.3, -1.8, 1.0)):
        steel.cyl(.025, h, loc=(x, y, top + h / 2), seg=5, bevel=0)
        red.sphere(.06, loc=(x, y, top + h + .04), seg=6, rings=4)
    steel.cyl(.03, 1.0, loc=(1.6, -1.6, top + .5), seg=6, bevel=0)
    for k, ang in enumerate((0, R90)):
        steel.box((.6, .025, .025), loc=(1.6, -1.6, top + .9 + .03 * k), rot=(0, 0, ang), bevel=0)
    for k in range(4):
        t = k * R90
        a.part('Anemometer', 'Armor').sphere(.06, loc=(1.6 + .3 * math.cos(t), -1.6 + .3 * math.sin(t), top + 1.0),
                                             seg=6, rings=4)
    a.part('Roof_AC', 'MetalSheet').box((.9, .7, .5), loc=(-1.1, 1.3, top + .24), bevel=.04, seg=1)


def parked_jet(a):
    """Parked single-engine fighter (10 x 9 m, 3.6 m; nose to +X): Team-painted fuselage, cropped
    delta wings with flaps and ailerons, stabilisers and a fin with a rudder, the canopy raised on
    its rear hinge over the open cockpit and ejection seat, a red intake cover and remove-before-
    flight streamers, the gear on yellow chocks, a boarding ladder hooked on the left sill and
    missiles on the wingtip rails. The engine is cold: no exhaust glow."""
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    moving = a.part('Control_surfaces', 'Armor')
    panels = a.part('Panels', 'Team')
    red = a.part('Covers', 'BarrelRed')
    hull = [_sec(-4.25, .33, 1.24, 1.8, n=12), _sec(-3.5, .44, 1.14, 1.95, n=12), _sec(-2.5, .54, 1.07, 2.08, n=12),
            _sec(-1.3, .68, 1.02, 2.06, n=12), _sec(.1, .76, 1.0, 1.98, n=12), _sec(1.6, .72, 1.0, 1.94, n=12),
            _sec(2.9, .6, 1.02, 1.9, n=12), _sec(3.9, .48, 1.02, 1.92, n=12)]
    body.loft(hull, bevel=0)
    armor.loft([[(0, -5.2, 1.52)], _sec(-5.0, .12, 1.42, 1.62, n=12), _sec(-4.65, .24, 1.32, 1.72, n=12),
                _sec(-4.2, .32, 1.25, 1.79, n=12)])
    steel.cyl(.022, .45, loc=(0, -5.33, 1.52), rot=ALONG_Y, seg=6, bevel=0)
    red.box((.05, .012, .32), loc=(.05, -5.45, 1.35), bevel=0)
    _patch(armor, hull, -4.2, -3.5, 5, 7)                                                  # anti-glare panel
    _patch(panels, hull, 1.7, 2.8, 4, 5, out=.018, inn=.012, bevel=.005)                     # engine bay doors
    _patch(panels, hull, 1.7, 2.8, 7, 8, out=.018, inn=.012, bevel=.005)
    # Open cockpit: a dark tub, coaming, ejection seat with its yellow and black handle.
    _patch(dark, hull, -3.35, -1.45, 5, 7, out=.012, inn=.02)
    top_z = _skin_z(hull, -1.8, 0)
    armor.box((.42, .36, .6), loc=(0, -1.8, top_z + .2), bevel=0)
    armor.box((.3, .2, .2), loc=(0, -1.72, top_z + .56), bevel=0)
    a.part('Seat_handle', 'Hazard').box((.2, .05, .06), loc=(0, -1.93, top_z + .62), bevel=0)
    armor.box((.6, .3, .16), loc=(0, -3.15, _skin_z(hull, -3.15, 0) + .04), bevel=0)
    a.part('HUD', 'Glass').box((.26, .03, .2), loc=(0, -3.08, _skin_z(hull, -3.15, 0) + .2), rot=(-.3, 0, 0), bevel=0)
    # Canopy raised about its rear hinge, with its frame.
    st = [(y, w, _skin_z(hull, y, w) - .03, crown) for y, w, crown in
          ((-3.45, .16, 2.12), (-3.1, .36, 2.36), (-2.5, .44, 2.5), (-1.9, .42, 2.46), (-1.4, .3, 2.3))]
    hinge = Vector((0, -1.35, st[-1][2] + .06))
    turn = Matrix.Rotation(-.55, 3, 'X')

    def raised(p):
        return tuple(hinge + turn @ (Vector(p) - hinge))
    rings = [[raised(p) for p in _dome(y, w, z0, z1, 9)] for y, w, z0, z1 in st]
    a.part('Canopy', 'Glass').loft(rings, bevel=.02, seg=1)
    frames = a.part('Canopy_frames', 'Armor')
    frames.tube([r_[0] for r_ in rings], .03, seg=4)
    frames.tube([r_[-1] for r_ in rings], .03, seg=4)
    frames.tube(rings[-1], .035, seg=4)
    steel.limb((.3, -1.5, st[-1][2]), raised((.3, -1.75, st[-1][2] + .05)), .04, .04, bevel=0)   # canopy strut
    spine = [_dome(y, w, _skin_z(hull, y, w) - .04, z1) for y, w, z1 in ((-1.45, .3, 2.25), (-.2, .32, 2.16),
                                                                         (1.3, .26, 2.04))]
    body.loft(spine + [[(0, 2.7, 1.96)]], bevel=0)
    steel.box((.02, .2, .15), loc=(0, .4, 2.24), rot=(-.35, 0, 0), bevel=0, taper=(1, .5))
    # Chin intake with its red cover and streamer.
    lips = a.part('Intake_lips', 'Team')
    trunk = [_duct(0, -1.3, .9, .38, .25), _duct(0, .2, 1.08, .3, .18)]
    _intake(a, body, lips, dark, (0, -2.05, .86), .4, .26, .3, trunk)
    m = _frame((0, -2.05, .86), (R90 + .3, 0, 0))
    red.box((.72, .44, .12), loc=tuple(m @ Vector((0, 0, .24))), rot=(R90 + .3, 0, 0), bevel=0)
    red.box((.07, .012, .45), loc=(.22, -2.43, .5), bevel=0)
    # Wings with flaps and ailerons, stabilisers, a fin with its rudder.
    wing = Planform(.5, 4.3, -1.55, 1.7, 3.75, .95, .2, .06, 1.34, 1.3)
    for frame in (RIGHT, LEFT):
        _wing(body, moving, wing, frame, cs=[(1.05, 4.3, .74)], bevel=0)
        _skin_panel(panels, wing, frame, 1.3, 2.4, .22, .56)
    stab = Planform(.35, 2.15, 3.15, 4.05, 1.3, .55, .09, .04, 1.45, 1.4)
    for frame in (RIGHT, LEFT):
        _surface(body, stab, frame, bevel=0)
    fin = Planform(0, 1.8, 2.35, 3.75, 1.85, .72, .11, .05)
    _wing(body, moving, fin, _upright(0.0, 1.78, 0.0), cs=[(0.0, 1.8, .68)], lower=1.0, bevel=0)
    _nozzle(a, 0, 3.85, 1.47, .42, .75, seg=10, glow=False)
    # Landing gear on chocks.
    tyres = a.part('Tyres', 'Rubber')
    chock = a.part('Chocks', 'Hazard')
    rope = a.part('Chock_ropes', 'Canvas')
    gear = [(0, -3.05, .25, .16), (-1.05, .75, .34, .22), (1.05, .75, .34, .22)]
    for x, y, r, w in gear:
        tyres.cyl(r, w, loc=(x, y, r), rot=ALONG_X, seg=10, bevel=0)
        steel.cyl(r * .5, w + .02, loc=(x, y, r), rot=ALONG_X, seg=8, bevel=0)
        cw = w + .14
        for s in (-1, 1):
            y_in = y + s * r * .5
            chock.prism([(y_in, 0), (y_in + s * .34, 0), (y_in + s * .34, .15), (y_in + s * .1, .2)], cw,
                        loc=(x, 0, 0), axis='X', bevel=0)
        side = 1 if x >= 0 else -1
        rope.tube([(x + side * (cw / 2 - .03), y - r * .5 - .25, .1), (x + side * (cw / 2 + .04), y, .06),
                   (x + side * (cw / 2 - .03), y + r * .5 + .25, .1)], .02, seg=4)
    steel.cyl(.055, .95, loc=(0, -2.92, .25 + .5), seg=8, bevel=0)                          # nose strut
    for s in (-1, 1):
        steel.box((.03, .3, .25), loc=(s * .11, -3.0, .38), bevel=0)                          # fork
        body.box((.03, .9, .4), loc=(s * .21, -2.75, .92), bevel=0)                         # nose gear doors
        x = s * 1.05
        steel.limb((x, .75, .34), (s * .82, .55, 1.3), .1, .1, bevel=0)                      # main struts
        steel.limb((s * .95, .6, .7), (s * .6, 1.3, 1.08), .05, .05, bevel=0)                  # drag braces
        body.box((.03, 1.0, .5), loc=(s * .72, .8, .82), bevel=0)                            # main gear doors
    # Boarding ladder hooked on the left sill.
    lad = a.part('Ladder', 'Hazard')
    sill = _skin_z(hull, -2.6, .45)
    for dy in (-.22, .22):
        lad.limb((-1.42, -2.6 + dy, .0), (-.7, -2.6 + dy, sill + .1), .06, .06, bevel=0)
        lad.limb((-.7, -2.6 + dy, sill + .1), (-.44, -2.6 + dy, sill + .14), .04, .04, bevel=0)
    for k in range(6):
        f = (k + .7) / 7
        steel.box((.05, .44, .04), loc=(-1.42 + .72 * f, -2.6, (sill + .1) * f), bevel=0)
    # Wingtip rails with missiles, their seekers under red covers; nav lights (off).
    aams = _aam_parts(a)
    for s in (-1, 1):
        x = s * 4.33
        armor.box((.07, 1.4, .08), loc=(x, 1.9, 1.28), bevel=0)
        _aam(aams, (s * 4.41, 1.2, 1.2), length=2.0, r=.065, canards=False)
        red.box((.16, .2, .16), loc=(s * 4.41, .26, 1.2), bevel=0)
        red.box((.05, .012, .32), loc=(s * 4.41, .2, 1.0), bevel=0)
        a.part('Nav_lights', 'BarrelRed' if s < 0 else 'RoofGreen').box((.06, .14, .06), loc=(s * 4.3, 1.75, 1.36),
                                                                       bevel=0)
    _turn(a, R90)


def fuel_truck(a):
    """Airfield fuel truck (7 x 2.6 m, 3.1 m; nose to +X): a snub cab (CarRed, like the town
    truck's) with a roof beacon, an oval tank banded in steel with a red stripe, hazard diamonds and
    block lettering, a railed walkway with manholes on top, a rear pump cabinet with a hose reel and
    ladder, side lockers, extinguishers and three axles."""
    rng = random.Random(191)
    paint = a.part('Cab', 'CarRed')
    under = a.part('Chassis', 'Undercarriage')
    under.box((1.0, 6.5, .28), loc=(0, .05, .74), bevel=.02, seg=1)
    paint.prism([(-3.48, .82), (-1.7, .82), (-1.7, 2.9), (-3.15, 2.9), (-3.44, 2.3), (-3.5, 1.6)], 2.34, axis='X',
                bevel=.08, seg=2)
    glass = a.part('Glass', 'Glass')
    p0, p1 = (-3.43, 2.35), (-3.17, 2.85)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    n = (-math.sin(ang), math.cos(ang))
    glass.limb((0, p0[0] + n[0] * .03, p0[1] + n[1] * .03), (0, p1[0] + n[0] * .03, p1[1] + n[1] * .03), 2.05, .04,
               bevel=0)
    for face, x in (('-x', -1.17), ('+x', 1.17)):
        fbox(glass, face, (x, -2.55, 2.35), (1.0, .04, .7), out=.01)
    dark = a.part('Rubber_trim', 'Rubber')
    armor = a.part('Trim', 'Armor')
    armor.box((2.44, .24, .34), loc=(0, -3.58, .86), bevel=.04, seg=1)
    fbox(armor, '-y', (0, -3.5, 1.35), (1.3, .05, .5), out=.02)
    for z in (1.2, 1.35, 1.5):
        fbox(dark, '-y', (0, -3.5, z), (1.2, .04, .05), out=.05)
    for sx in (-1, 1):
        a.part('Headlights', 'Lamp').box((.3, .05, .2), loc=(sx * .88, -3.52, 1.3), bevel=.02, seg=1)
        a.part('Marker_lights', 'Alloy').box((.1, .05, .08), loc=(sx * 1.08, -3.52, 1.3), bevel=0)
        armor.limb((sx * 1.14, -3.1, 2.3), (sx * 1.36, -3.2, 2.3), .04, .04, bevel=0)
        armor.box((.06, .16, .38), loc=(sx * 1.37, -3.25, 2.15), bevel=.01, seg=1)
        armor.box((.16, .5, .08), loc=(sx * 1.2, -2.55, .95), bevel=0)
        for y in (-3.1, -2.0):
            dark.box((.02, .03, 1.45), loc=(sx * 1.175, y, 2.05), bevel=0)
        a.part('Handles', 'Steel').box((.03, .14, .05), loc=(sx * 1.185, -2.15, 1.9), bevel=0)
    for t0 in (-.55, .35):
        q0 = [c0 + (c1 - c0) * .1 + nc * .055 for c0, c1, nc in zip(p0, p1, n)]
        q1 = [c0 + (c1 - c0) * .55 + nc * .055 for c0, c1, nc in zip(p0, p1, n)]
        dark.limb((t0, q0[0], q0[1]), (t0 + .3, q1[0], q1[1]), .03, .02, bevel=0)
    paint.box((2.1, .3, .05), loc=(0, -3.3, 2.97), bevel=.01, seg=1)
    a.part('Beacon', 'Alloy').cyl(.1, .16, loc=(.5, -2.5, 3.0), seg=8, bevel=.02, bseg=1)
    a.part('Plate', 'PlasterWhite').box((.46, .03, .12), loc=(0, -3.71, .86), bevel=0)
    # Oval tank with steel bands, a red stripe, hazard diamonds and lettering.
    zb, zt, w = 1.02, 2.72, 1.18

    def sec(y, k):
        return _sec(y, w * k, zb + (zt - zb) * (1 - k) / 2, zt - (zt - zb) * (1 - k) / 2, n=14, pt=2.3, pb=2.3)
    tank = [sec(-1.62, .72), sec(-1.52, .93), sec(-1.38, 1.0), sec(3.0, 1.0), sec(3.14, .93), sec(3.24, .72)]
    a.part('Tank', 'Fuel').loft(tank, bevel=0)
    bands = a.part('Tank_bands', 'Steel')
    for y in (-1.1, .8, 2.7):
        bands.loft([sec(y - .07, 1.0 + .018), sec(y + .07, 1.0 + .018)])
    stripe = a.part('Tank_stripe', 'BarrelRed')
    for y_a, y_b in ((-1.0, .72), (.88, 2.62)):
        _patch(stripe, tank, y_a, y_b, 5, 6, out=.012, inn=.02)
        _patch(stripe, tank, y_a, y_b, 8, 9, out=.012, inn=.02)
    zm = (zb + zt) / 2
    for face, x in (('-x', -w), ('+x', w)):
        letters(a, rng, face, (x, 1.75 if x > 0 else -.25, zm + .12), 1.5, h=.28, mat='Charred', out=.0)
        for size, mat, o in ((.3, 'PlasterWhite', .012), (.22, 'BarrelRed', .025)):
            a.part('Placards', mat).box((.02, size, size), loc=(x + (o if x > 0 else -o), -.55 if x > 0 else 2.55,
                                                                zm + .02), rot=(math.pi / 4, 0, 0), bevel=0)
    for size, mat, o in ((.36, 'PlasterWhite', .012), (.28, 'BarrelRed', .025)):
        a.part('Placards', mat).box((size, .02, size), loc=(0, 3.25 + o, zm + .1), rot=(0, math.pi / 4, 0), bevel=0)
    # Walkway, railings and manholes on top.
    walk = a.part('Walkway', 'Armor')
    walk.box((.7, 4.0, .06), loc=(0, .8, zt + .01), bevel=0)
    rail = a.part('Railing', 'Hazard')
    for sx in (-1, 1):
        for y in (-1.0, .8, 2.6):
            rail.box((.04, .04, .7), loc=(sx * .5, y, zt + .22), bevel=0)
        rail.box((.07, 3.68, .05), loc=(sx * .5, .8, zt + .56), bevel=0)
    for y in (-.2, 1.8):
        a.part('Manholes', 'Steel').cyl(.3, .14, loc=(0, y, zt + .05), seg=10, bevel=0)
        a.part('Manholes', 'Steel').cyl(.07, .12, loc=(.2, y + .2, zt + .15), seg=6, bevel=0)
    # Rear pump cabinet with a roller shutter and hose reel, rear ladder and lights.
    cab = a.part('Pump_cabinet', 'Armor')
    cab.box((2.24, .7, 1.1), loc=(0, 3.1, 1.3), bevel=.03, seg=1)
    for k in range(5):
        fbox(a.part('Shutter', 'Steel'), '+y', (-.45, 3.45, .95 + k * .18), (1.1, .03, .06), out=.02)
    a.part('Hose_reel', 'Rubber').cyl(.3, .8, loc=(.6, 3.5, 1.15), rot=ALONG_X, seg=10, bevel=.02, bseg=1)
    for dx in (-.43, .43):
        a.part('Hose_reel_ends', 'Steel').cyl(.36, .05, loc=(.6 + dx, 3.5, 1.15), rot=ALONG_X, seg=10, bevel=0)
    armor.box((2.3, .14, .16), loc=(0, 3.48, .62), bevel=.02, seg=1)
    lad = a.part('Ladder', 'Steel')
    for dx in (-.9, -.5):
        lad.box((.04, .04, 2.0), loc=(dx, 3.5, 1.75), bevel=0)
    for k in range(6):
        lad.box((.4, .06, .03), loc=(-.7, 3.5, .95 + k * .32), bevel=0)
    for sx in (-1, 1):
        a.part('Taillights', 'BarrelRed').box((.25, .05, .15), loc=(sx * .95, 3.56, .8), bevel=.01, seg=1)
    a.part('Plate', 'PlasterWhite').box((.46, .03, .12), loc=(0, 3.57, .62), bevel=0)
    # Side lockers, extinguishers, underrun guards, mud flaps.
    for sx in (-1, 1):
        a.part('Lockers', 'Armor').box((.65, 1.4, .55), loc=(sx * .87, .15, .75), bevel=.03, seg=1)
        fbox(a.part('Locker_handles', 'Steel'), '+x' if sx > 0 else '-x', (sx * 1.195, .15, .9), (.3, .03, .04),
             out=.015)
        a.part('Extinguishers', 'BarrelRed').cyl(.09, .5, loc=(sx * 1.05, -1.3, .95), seg=6, bevel=0)
        a.part('Underrun', 'Steel').box((.04, 2.95, .06), loc=(sx * 1.23, -.475, .62), bevel=0)
        a.part('Mud_flaps', 'Rubber').box((.6, .03, .45), loc=(sx * .9, 3.2, .55), bevel=0)
    _wheels(a, [(sx * .98, -2.55) for sx in (-1, 1)], .48, .3, hub=.45)
    _wheels(a, [(sx * .94, y) for sx in (-1, 1) for y in (1.55, 2.6)], .48, .4, hub=.45)
    _arches(a, 1.17, (-2.55,), .82, .56)
    _turn(a, R90)


def geodesic(part, r, loc, cut, sub=3):
    """Geodesic dome: an icosphere of radius r at loc kept above local height cut * r, its lowest
    ring flattened onto the cut so it seats on a round base."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < cut - 1e-4], context='VERTS')
    ring = math.sqrt(1 - cut * cut)
    for v in bm.verts:
        if v.is_boundary:
            xy = Vector((v.co.x, v.co.y))
            if xy.length > 1e-6:
                xy = xy.normalized() * ring
            v.co = (xy.x, xy.y, cut)
    bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary])
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.verts.index_update()
    verts = [tuple(Vector(loc) + v.co * r) for v in bm.verts]
    faces = [[v.index for v in f.verts] for f in bm.faces]
    bm.free()
    part.mesh(verts, faces)


def radar_dome(a):
    """Radome building (8 x 8 m, 7.9 m): a white geodesic radome on a round plinth with a railed
    walkway, on a flat-roofed equipment building with a door, louvres, wall air conditioners, a
    caged ladder, a cable tray to a generator, an aerial and a red obstruction light."""
    rng = random.Random(201)
    a.part('Pad', 'Concrete').box((7.9, 7.9, .2), loc=(0, 0, .1), bevel=.04, seg=1)
    bw, bh, z0 = 3.3, 3.2, .18
    top = z0 + bh
    walls = a.part('Walls', 'MetalSheet')
    walls.box((2 * bw, 2 * bw, bh + .02), loc=(0, 0, z0 + (bh + .02) / 2), bevel=.05, seg=1)
    a.part('Parapet', 'Concrete').shell([(-bw - .04, -bw - .04), (bw + .04, -bw - .04), (bw + .04, bw + .04),
                                         (-bw - .04, bw + .04)], .45, .2, loc=(0, 0, top - .02), bevel=.02)
    a.part('Roof_deck', 'Asphalt').box((2 * bw - .3, 2 * bw - .3, .1), loc=(0, 0, top + .03), bevel=0)
    for face, p, us in (('-y', (0, -bw), (-2.75, -.3, 2.4)), ('+x', (bw, 0), (-2.4, .3, 2.6)),
                        ('-x', (-bw, 0), (-2.2, -1.1, 2.2)), ('+y', (0, bw), (-2.2, -1.1, 0, 1.1, 2.2))):
        for u in us:
            fbox(a.part('Wall_ribs', 'Steel'), face, slide(face, (p[0], p[1], z0 + bh / 2), u), (.08, .05, bh - .2),
                 out=.02)
    door(a, '-y', (-1.6, -bw, z0), w=1.1, h=2.2, mat='Steel', frame='Armor', step=None, lamp=True)
    a.part('Canopy', 'Armor').box((1.8, .9, .12), loc=(-1.6, -bw - .42, z0 + 2.55), bevel=.03, seg=1)
    vent = a.part('Louvres', 'Steel')
    for face, p in (('-y', (1.3, -bw)), ('+x', (bw, -1.2))):
        fbox(a.part('Louvre_frames', 'Armor'), face, (p[0], p[1], z0 + 2.2), (1.3, .06, .8), out=.04)
        nx, ny = NORMAL[face]
        vent.grille(1.1, .6, loc=(p[0] + nx * .1, p[1] + ny * .1, z0 + 2.2), rot=(0, 0, math.atan2(ny, nx) + R90),
                    slats=4)
    ac_unit(a, '+x', (bw, 1.4, z0 + 1.0))
    ac_unit(a, '-x', (-bw, -.8, z0 + 1.0))
    fbox(a.part('Sign', 'Hazard'), '-y', (1.3, -bw, z0 + 1.2), (1.0, .05, .5), out=.03)
    # Radome on its plinth, walkway railing, beacon.
    a.part('Plinth', 'Concrete').cyl(2.95, .82, loc=(0, 0, top + .41), seg=20, bevel=.03, bseg=1)
    a.part('Plinth_band', 'Armor').cyl(2.97, .16, loc=(0, 0, top + .72), seg=20, bevel=0)
    rc, rr = top + .8 + .55, 2.9
    geodesic(a.part('Radome', 'Medical', flat=True), rr, (0, 0, rc), -.55 / rr)
    ring_rail(a.part('Railing', 'Hazard'), 0, 0, top + .06, 3.15, h=1.0, posts=12, pts=24)
    a.part('Obstruction_light', 'LavaGlow').sphere(.1, loc=(0, 0, rc + rr + .06), seg=8, rings=5)
    # Caged ladder up the right wall, aerial, cable tray and a generator.
    lx, ly = bw + .12, 1.9
    steel = a.part('Steel', 'Steel')
    ladder(steel, (lx, ly, z0), top + 1.0, R90, width=.44, step=.35, rung=.07)
    for z in (1.8, 2.5, 3.2, 3.9):
        steel.tube([(lx - .01, ly - .25, z), (lx + .3, ly - .25, z), (lx + .38, ly, z), (lx + .3, ly + .25, z),
                    (lx - .01, ly + .25, z)], .02, seg=4)
    steel.cyl(.04, 3.0, loc=(-2.6, 2.6, top + 1.5), seg=6, bevel=0)
    for z, hw_ in ((top + 2.3, .5), (top + 2.7, .35)):
        steel.box((2 * hw_, .03, .03), loc=(-2.6, 2.6, z), bevel=0)
    gen = a.part('Generator', 'Armor')
    gen.box((1.7, .5, 1.0), loc=(1.6, -3.6, .7), bevel=.05, seg=1)
    a.part('Cable_tray', 'Steel').box((.3, .1, .9), loc=(1.6, -3.33, 1.6), bevel=0)
    a.part('Generator_stripe', 'Hazard').box((1.72, .04, .12), loc=(1.6, -3.86, .6), bevel=0)


def revetment(a):
    """Blast wall (12 x 2 m, 3.6 m): six numbered concrete T-wall panels on their feet with lifting
    eyes, an earth berm banked against the back and grass on it."""
    rng = random.Random(211)
    conc = a.part('Panels', 'Concrete')
    for i in range(6):
        x = -5.0 + i * 2.0
        conc.box((1.96, .3, 3.6), loc=(x, -.8, 1.8), bevel=.05, seg=1, taper=(1, .7))
        conc.box((1.9, .22, .2), loc=(x, -1.02, .09), bevel=.03, seg=1)
        for dx in (-.5, .5):
            a.part('Lifting_eyes', 'Steel').tube([(x + dx - .1, -.8, 3.55), (x + dx - .1, -.8, 3.66),
                                                  (x + dx, -.8, 3.72), (x + dx + .1, -.8, 3.66),
                                                  (x + dx + .1, -.8, 3.55)], .025, seg=4)
        numeral(a.part('Stencils', 'PlasterWhite'), str(i + 1), '-y', (x, -.95, 2.6), h=.5, t=.08, out=.01)
        fbox(a.part('Stencil_bands', 'Hazard'), '-y', (x, -.95, .55), (1.4, .03, .12), out=.012)
    # Earth berm against the back: a faceted height field running into the wall.
    nx, ny = 24, 5
    ys = [-.7, -.3, .15, .6, 1.02]
    zs = [3.05, 2.75, 1.9, .8, -.06]
    verts, faces = [], []
    for j in range(ny):
        for i in range(nx + 1):
            x = -6.0 + 12.0 * i / nx
            end = min(1.0, (6.0 - abs(x)) / .9)
            z = zs[j] * (.3 + .7 * end) if j < ny - 1 else -.06
            z += (.12 * noise.noise(Vector((x * .8, ys[j] * 2, 1.3))) if 0 < j < ny - 1 else 0)
            verts.append((x, ys[j] + (.05 * noise.noise(Vector((x, j, 4.0))) if 0 < j < ny - 1 else 0), max(-.06, z)))
    for j in range(ny - 1):
        for i in range(nx):
            a0, a1 = j * (nx + 1) + i, j * (nx + 1) + i + 1
            b0, b1 = a0 + nx + 1, a1 + nx + 1
            faces += [(a0, b0, b1), (a0, b1, a1)]
    # End caps close the berm against the wall at both ends.
    for i in (0, nx):
        col = [j * (nx + 1) + i for j in range(ny)]
        base = len(verts)
        verts += [(verts[c][0], verts[c][1], -.06) for c in col]
        for j in range(ny - 1):
            q = (col[j], col[j + 1], base + j + 1, base + j)
            faces.append(q[::-1] if i == nx else q)
    _split(a, verts, faces, lambda c, n: 'Grass' if n.z > .75 and noise.noise(c * .9) > -.1 else 'Dirt', 'Berm')
    tufts = a.part('Tufts', 'Grass', flat=True)
    for k, x in enumerate((-4.6, -2.1, .4, 2.9, 5.0)):
        tufts.ico((.35, .25, .18), loc=(x, .35, 1.55 + .2 * math.sin(k)), sub=1, jitter=.3, seed=k * 1.7)


def runway_light(a):
    """Elevated runway edge light (0.5 x 0.5 m, 0.5 m): a base can bolted to a concrete pad, a
    yellow frangible coupling, a stem and a housing under a glowing Lamp lens."""
    a.part('Pad', 'Concrete').box((.48, .48, .06), loc=(0, 0, .02), bevel=.01, seg=1)
    steel = a.part('Steel', 'Steel')
    steel.cyl(.17, .08, loc=(0, 0, .085), seg=10, bevel=0)
    steel.bolts([(.13 * math.cos(k * TAU / 4 + .4), .13 * math.sin(k * TAU / 4 + .4), .13) for k in range(4)], r=.016,
                h=.02, seg=4, bevel=0)
    a.part('Coupling', 'Hazard').cyl(.045, .09, loc=(0, 0, .17), seg=8, bevel=0)
    steel.cyl(.03, .16, loc=(0, 0, .28), seg=6, bevel=0)
    a.part('Housing', 'Armor').cyl(.075, .08, loc=(0, 0, .39), seg=10, bevel=0)
    a.part('Lens', 'Lamp').lathe([(.068, .425), (.07, .47), (.05, .5), (0, .51)], seg=10)


# ----------------------------------------------------------------------------- city
def faces_of(x0, x1, y0, y1):
    """(face, wall centre (x, y), length) of a rectangular block's four facades."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return (('-y', (cx, y0), x1 - x0), ('+y', (cx, y1), x1 - x0), ('-x', (x0, cy), y1 - y0), ('+x', (x1, cy), y1 - y0))


def window_band(a, rng, face, p, length, z, h, bays, lit, frame='Armor'):
    """Ribbon window: a dark band 1 cm proud of the wall with `bays` panes 2.5 cm proud of it, each
    Glass or, at random, lit Lamp."""
    fbox(a.part('Window_bands', frame), face, (p[0], p[1], z), (length, .04, h), out=.01)
    pw = length / bays
    for i in range(bays):
        q = slide(face, (p[0], p[1], z), -length / 2 + (i + .5) * pw)
        fbox(pane(a, rng, lit), face, q, (pw - .14, .04, h - .16), out=.035)


def roof_ac(a, x, y, z, w=1.4, d=1.0, h=.8):
    """Rooftop air conditioner with a dark fan on top."""
    a.part('Roof_AC', 'MetalSheet').box((w, d, h), loc=(x, y, z + h / 2 - .02), bevel=.04, seg=1)
    a.part('AC_fan', 'Rubber').cyl(min(w, d) * .32, .04, loc=(x + w * .18, y, z + h), seg=10, bevel=0)
    a.part('AC_grille', 'Steel').box((w * .3, d + .04, h * .5), loc=(x - w * .25, y, z + h * .45), bevel=0)


def mast(a, x, y, z, h, arms=2, light=True):
    """Steel aerial mast with cross arms and a red obstruction light on top."""
    steel = a.part('Aerials', 'Steel')
    steel.cyl(.05, h, loc=(x, y, z + h / 2), seg=6, bevel=0)
    for k in range(arms):
        steel.box((.9 - .25 * k, .03, .03), loc=(x, y, z + h * (.62 + .18 * k)), rot=(0, 0, .6 * k), bevel=0)
    if light:
        a.part('Obstruction_lights', 'LavaGlow').sphere(.07, loc=(x, y, z + h + .05), seg=6, rings=4)


def dish_on_post(a, x, y, z, r=.55, tilt=.5):
    """Satellite dish on a short post, facing -Y and tilted up."""
    a.part('Aerials', 'Steel').cyl(.05, .7, loc=(x, y, z + .35), seg=6, bevel=0)
    _dish(a.part('Dishes', 'Medical'), (x, y - .05, z + .75), r, r, depth=r * .3, seg=10, tilt=tilt)


def stair_house(a, rng, x, y, z, w, d, h, mat='Concrete'):
    """Roof stair and lift house with a steel door and lamp on its -Y face and a vent on its roof."""
    a.part('Stair_house', mat).box((w, d, h), loc=(x, y, z + h / 2 - .02), bevel=.04, seg=1)
    a.part('Stair_house_cap', 'Concrete').box((w + .2, d + .2, .14), loc=(x, y, z + h + .03), bevel=.02, seg=1)
    door(a, '-y', (x - w * .2, y - d / 2, z), w=.9, h=2.0, mat='Steel', frame='Armor', step=None, lamp=True)
    a.part('Vents', 'Steel').cyl(.2, .5, loc=(x + w * .25, y + d * .2, z + h + .3), seg=8, bevel=0)
    return z + h + .1


def lobby(a, rng, x0, x1, y0, y1, g, cols, entrance_x=0.0, sign='Hazard'):
    """Ground-floor lobby: a glass box set 60 cm back behind perimeter columns, a fascia band,
    an entrance canopy with a lit soffit on the -Y side, glazed doors and a shop sign."""
    inset = .6
    a.part('Lobby_glass', 'Glass').box((x1 - x0 - 2 * inset, y1 - y0 - 2 * inset, g - .12),
                                       loc=((x0 + x1) / 2, (y0 + y1) / 2, .06 + (g - .12) / 2), bevel=0)
    conc = a.part('Columns', 'Concrete')
    for face, (px, py), L in faces_of(x0, x1, y0, y1):
        n = cols
        for i in range(n + 1) if face in ('-y', '+y') else range(1, n):
            q = slide(face, (px, py, g / 2), -L / 2 + .3 + i * (L - .6) / n)
            nx, ny = NORMAL[face]
            conc.box((.6, .6, g - .15), loc=(q[0] - nx * .3, q[1] - ny * .3, (g - .15) / 2), bevel=.03, seg=1)
        mull = a.part('Lobby_mullions', 'Steel')
        for i in range(n):
            q = slide(face, (px, py, g / 2), -L / 2 + .3 + (i + .5) * (L - .6) / n)
            nx, ny = NORMAL[face]
            fbox(mull, face, (q[0] - nx * inset, q[1] - ny * inset, q[2]), (.08, .06, g - .2), out=.02)
        if face != '-y':
            for i in range(n):
                if rng.random() < .45:
                    q = slide(face, (px, py, 1.9), -L / 2 + .3 + (i + .25) * (L - .6) / n)
                    fbox(a.part('Lobby_lit', 'Lamp'), face, (q[0] - nx * inset, q[1] - ny * inset, 1.9),
                         ((L - .6) / n * .38, .04, 2.2), out=.035)
    a.part('Fascia', 'Concrete').box((x1 - x0 + .1, y1 - y0 + .1, .7), loc=((x0 + x1) / 2, (y0 + y1) / 2, g - .33),
                                     bevel=.03, seg=1)
    ex = entrance_x
    a.part('Canopy', 'Steel').box((4.2, 1.2, .24), loc=(ex, y0 - .5, g - 1.0), bevel=.03, seg=1)
    a.part('Canopy_soffit', 'Lamp').box((3.8, .8, .03), loc=(ex, y0 - .55, g - 1.13), bevel=0)
    for sx in (-1, 1):
        a.part('Canopy_posts', 'Steel').cyl(.07, g - 1.1, loc=(ex + sx * 1.9, y0 - .95, (g - 1.1) / 2), seg=8, bevel=0)
    fbox(a.part('Doors', 'Armor'), '-y', (ex, y0 + inset, 1.2), (2.4, .1, 2.4), out=.03)
    fbox(a.part('Door_glass', 'Lamp'), '-y', (ex, y0 + inset, 1.2), (2.1, .04, 2.1), out=.07)
    sx0 = x0 + 2.6
    fbox(a.part('Shop_sign', sign), '-y', (sx0, y0, g - .33), (3.2, .08, .5), out=.06)
    letters(a, rng, '-y', (sx0, y0, g - .33), 2.8, h=.3, mat='Charred', out=.11)


def highrise_a(a):
    """Concrete and glass high-rise (12 x 12 m; roof parapet 24.8 m, 28.6 m to the aerial): a
    glazed lobby behind columns under an entrance canopy, six floors of ribbon windows (some lit)
    between white spandrels, corner piers and pilasters, and a busy roof: a stair and lift house
    with an aerial and a dish, two water tanks on stands, four air conditioners, ducts and vents."""
    rng = random.Random(221)
    hw = 5.7
    g, storey, floors = 4.4, 3.2, 6
    top = g + floors * storey
    x0, x1, y0, y1 = -hw, hw, -hw, hw
    lobby(a, rng, x0, x1, y0, y1, g, 4, entrance_x=1.35)
    a.part('Walls', 'Concrete').box((2 * hw, 2 * hw, top - g + .12), loc=(0, 0, (g + top) / 2 - .04), bevel=.04, seg=1)
    white = a.part('Spandrels', 'PlasterWhite')
    for f in range(floors):
        zf = g + f * storey
        white.box((2 * hw + .16, 2 * hw + .16, .95), loc=(0, 0, zf + .47), bevel=.02, seg=1)
        for face, p, L in faces_of(x0, x1, y0, y1):
            window_band(a, rng, face, p, L - 1.2, zf + .95 + (storey - .95) / 2, storey - 1.1, 5, .3)
    conc = a.part('Piers', 'Concrete')
    for sx in (-1, 1):
        for sy in (-1, 1):
            conc.box((.9, .9, top - g + .3), loc=(sx * (hw - .3), sy * (hw - .3), (g + top + .3) / 2 - .1), bevel=.03,
                     seg=1)
    for face, p, L in faces_of(x0, x1, y0, y1):
        for u in (-(L - 1.2) * .3, (L - 1.2) * .3):
            fbox(conc, face, slide(face, (p[0], p[1], (g + top) / 2), u), (.26, .36, top - g), out=.1)
    conc.box((2 * hw + .44, 2 * hw + .44, .5), loc=(0, 0, top + .15), bevel=.04, seg=1)
    rect = [(-hw - .2, -hw - .2), (hw + .2, -hw - .2), (hw + .2, hw + .2), (-hw - .2, hw + .2)]
    conc.shell(rect, .85, .28, loc=(0, 0, top + .38), bevel=.02)
    a.part('Coping', 'Steel').shell([(x * 1.004, y * 1.004) for x, y in rect], .06, .34, loc=(0, 0, top + 1.22),
                                    bevel=0)
    deck = top + .42
    a.part('Roof_deck', 'Asphalt').box((2 * hw - .2, 2 * hw - .2, .1), loc=(0, 0, deck - .05), bevel=0)
    # Roof.
    zs = stair_house(a, rng, -2.6, 2.0, deck, 3.4, 4.0, 2.7)
    mast(a, -3.6, 3.2, zs, 2.3)
    dish_on_post(a, -1.6, 1.0, zs, r=.5)
    for x in (1.7, 3.9):
        roof_tank(a, x, 3.4, deck, r=.8, h=1.5, mat='Fuel', leg=1.0)
    for x, y in ((-3.6, -3.4), (-1.5, -3.4), (1.6, -2.6), (3.8, -2.6)):
        roof_ac(a, x, y, deck)
    duct = a.part('Ducts', 'Steel')
    duct.box((5.6, .45, .45), loc=(-.1, -1.95, deck + .3), bevel=.02, seg=1)
    duct.box((.45, 2.4, .45), loc=(2.7, -.6, deck + .32), bevel=.02, seg=1)
    for x, y in ((0, 1.2), (4.6, .4), (-4.6, -1.6)):
        a.part('Vents', 'Steel').cyl(.13, .7, loc=(x, y, deck + .35), seg=8, bevel=0)
        a.part('Vents', 'Steel').cyl(.2, .08, loc=(x, y, deck + .72), seg=8, bevel=0)
    dish_on_post(a, 4.3, -.4, deck, r=.6)


def highrise_b(a):
    """Slab high-rise (14 x 10 m; roof parapet 30.1 m, 35.1 m to the mast): a glazed lobby, glass
    long faces behind full-height concrete fins and floor bands with lit bays, solid end walls with
    window slots and stacked glass balconies on the right, and on the roof a louvred plant room with
    a telecom mast, two cooling towers, water tanks, air conditioners and a lit sign frame."""
    rng = random.Random(231)
    hx, hy = 6.4, 4.5
    g, storey, floors = 4.5, 3.1, 8
    top = g + floors * storey
    x0, x1, y0, y1 = -hx, hx, -hy, hy
    lobby(a, rng, x0, x1, y0, y1, g, 5, entrance_x=2.44, sign='ContainerBlue')
    a.part('Walls', 'Concrete').box((2 * hx, 2 * hy, top - g + .12), loc=(0, 0, (g + top) / 2 - .04), bevel=.04, seg=1)
    conc = a.part('Fins', 'Concrete')
    nbay = 9
    span = 2 * hx - .8
    for face, y in (('-y', y0), ('+y', y1)):
        fbox(a.part('Curtain_glass', 'Glass'), face, (0, y, (g + top) / 2), (span, .04, top - g - .1), out=.01)
        for f in range(floors):
            zf = g + f * storey
            fbox(conc, face, (0, y, zf + .1), (span + .2, .3, .24), out=.15)
            for i in range(nbay):
                if rng.random() < .3:
                    q = slide(face, (0, y, zf + 1.65), -span / 2 + (i + .5) * span / nbay)
                    fbox(a.part('Lit_bays', 'Lamp'), face, q, (span / nbay - .5, .04, 2.3), out=.04)
        for i in range(nbay + 1):
            q = slide(face, (0, y, (g + top) / 2), -span / 2 + i * span / nbay)
            fbox(conc, face, q, (.24, .54, top - g + .2), out=.25)
    for face, x in (('-x', x0), ('+x', x1)):
        for f in range(floors):
            zf = g + f * storey
            for u in (-2.4, 2.4):
                q = slide(face, (x, 0, zf + 1.7), u)
                fbox(a.part('Frames', 'Armor'), face, q, (1.3, .08, 1.6), out=.03)
                fbox(pane(a, rng, .3), face, q, (1.1, .05, 1.4), out=.06)
            if face == '+x':
                sl = a.part('Balconies', 'Concrete')
                sl.box((.95, 2.8, .18), loc=(x + .46, 0, zf + .09), bevel=.02, seg=1)
                rail = a.part('Balcony_glass', 'Glass')
                rail.box((.05, 2.8, .9), loc=(x + .9, 0, zf + .63), bevel=0)
                for sy in (-1, 1):
                    rail.box((.86, .05, .88), loc=(x + .47, sy * 1.36, zf + .62), bevel=0)
                fbox(pane(a, rng, .4), '+x', (x, 0, zf + 1.4), (1.6, .05, 2.2), out=.03)
    conc.box((2 * hx + .44, 2 * hy + .44, .6), loc=(0, 0, top + .2), bevel=.04, seg=1)
    rect = [(-hx - .2, -hy - .2), (hx + .2, -hy - .2), (hx + .2, hy + .2), (-hx - .2, hy + .2)]
    conc.shell(rect, .8, .28, loc=(0, 0, top + .48), bevel=.02)
    deck = top + .52
    a.part('Roof_deck', 'Asphalt').box((2 * hx - .2, 2 * hy - .2, .1), loc=(0, 0, deck - .05), bevel=0)
    # Roof: plant room with louvres and a telecom mast, cooling towers, tanks, air conditioners.
    px, py, pw, pd, ph = -3.3, 1.6, 5.0, 4.0, 3.0
    a.part('Plant_room', 'MetalSheet').box((pw, pd, ph), loc=(px, py, deck + ph / 2 - .02), bevel=.04, seg=1)
    a.part('Plant_roof', 'Concrete').box((pw + .2, pd + .2, .14), loc=(px, py, deck + ph + .03), bevel=.02, seg=1)
    for face, p in (('-y', (px + .5, py - pd / 2)), ('+x', (px + pw / 2, py))):
        fbox(a.part('Louvre_frames', 'Armor'), face, (p[0], p[1], deck + 1.6), (2.4, .06, 1.6), out=.03)
        nx, ny = NORMAL[face]
        a.part('Louvres', 'Steel').grille(2.2, 1.4, loc=(p[0] + nx * .1, p[1] + ny * .1, deck + 1.6),
                                          rot=(0, 0, math.atan2(ny, nx) + R90), slats=6)
    door(a, '-y', (px - 1.6, py - pd / 2, deck), w=.9, h=2.0, mat='Steel', frame='Armor', step=None, lamp=True)
    zm = deck + ph + .1
    lat = a.part('Mast', 'Steel')
    b0, b1 = .55, .25
    for sx in (-1, 1):
        for sy in (-1, 1):
            lat.limb((px + sx * b0, py + sy * b0, zm), (px + sx * b1, py + sy * b1, zm + 4.2), .07, .07, bevel=0)
    for z, s in ((zm + 1.4, .45), (zm + 2.8, .35)):
        for sy in (-1, 1):
            lat.box((2 * s, .04, .04), loc=(px, py + sy * s, z), bevel=0)
            lat.box((.04, 2 * s, .04), loc=(px + sy * s, py, z + .03), bevel=0)
    for k, t in enumerate((-R90, R90 * .3, 2.2)):
        c, s = math.cos(t), math.sin(t)
        a.part('Panel_antennas', 'Medical').box((.3, .12, 1.0), loc=(px + c * .42, py + s * .42, zm + 3.4),
                                                rot=(0, 0, t + R90), bevel=.02, seg=1)
    a.part('Obstruction_lights', 'LavaGlow').sphere(.08, loc=(px, py, zm + 4.3), seg=6, rings=4)
    for x in (1.2, 3.8):
        a.part('Cooling_towers', 'MetalSheet').cyl(1.0, 1.7, loc=(x, 2.4, deck + .83), seg=12, bevel=.03, bseg=1)
        a.part('Fan_shrouds', 'Steel').cyl(.8, .4, loc=(x, 2.4, deck + 1.85), r2=.72, seg=12, bevel=0)
        a.part('AC_fan', 'Rubber').cyl(.66, .04, loc=(x, 2.4, deck + 1.99), seg=12, bevel=0)
    roof_tank(a, 5.4, 3.3, deck, r=.6, h=1.3, mat='Fuel', leg=.8)
    for x, y in ((.6, -1.2), (2.4, -1.2), (4.2, -1.2)):
        roof_ac(a, x, y, deck, w=1.2, d=.9, h=.7)
    a.part('Ducts', 'Steel').box((4.6, .4, .4), loc=(2.4, -.2, deck + .25), bevel=.02, seg=1)
    # Lit sign frame at the front edge: a lit panel with coloured blocks.
    steel = a.part('Sign_frame', 'Steel')
    sy0 = y0 + .9
    for x in (-5.4, -2.9):
        steel.box((.12, .12, 2.6), loc=(x, sy0 + .12, deck + 1.3), bevel=0)
        steel.limb((x, sy0 + .12, deck + 2.3), (x, sy0 + 1.4, deck), .08, .08, bevel=0)
    a.part('Sign', 'Lamp').box((3.8, .1, 1.3), loc=(-4.15, sy0, deck + 1.9), bevel=.02, seg=1)
    letters(a, rng, '-y', (-4.15, sy0 - .05, deck + 1.9), 3.5, h=.8, mat='ContainerBlue', out=.02)


def skyscraper(a):
    """Glass skyscraper (14 x 14 m; helipad deck 39.5 m, 43 m to the spire): a stone podium with a
    glazed entrance hall, a chamfered glass tower with a mullion grid, floor transoms, a louvred
    plant band and lit windows, a setback crown with a glass-railed terrace (water tanks, air
    conditioners, a window-cleaning crane and a spire) and a rooftop helipad with its circle and H,
    edge lights, a safety net frame and a windsock."""
    rng = random.Random(241)
    ph = 8.0
    stone = a.part('Podium', 'Concrete')
    stone.box((13.8, 13.8, ph), loc=(0, 0, ph / 2), bevel=.05, seg=1)
    stone.box((14.0, 14.0, .5), loc=(0, 0, ph - .15), bevel=.03, seg=1)
    hall = a.part('Hall_glass', 'Glass')
    fbox(hall, '-y', (0, -6.9, 3.6), (8.4, .06, 6.6), out=.02)
    mull = a.part('Hall_mullions', 'Steel')
    for i in range(7):
        fbox(mull, '-y', (-4.2 + i * 1.4, -6.9, 3.6), (.1, .06, 6.7), out=.06)
    for z in (2.4, 4.8):
        fbox(mull, '-y', (0, -6.9, z), (8.4, .06, .1), out=.075)
    for i in range(6):
        if rng.random() < .55:
            fbox(a.part('Hall_lit', 'Lamp'), '-y', (-3.5 + i * 1.4, -6.9, 5.9), (1.2, .04, 1.9), out=.045)
    a.part('Canopy', 'Steel').box((6.0, 2.0, .24), loc=(0, -7.9 + .9, 4.6), bevel=.03, seg=1)
    a.part('Canopy_soffit', 'Lamp').box((5.6, 1.5, .03), loc=(0, -7.0, 4.46), bevel=0)
    a.part('Revolving_door', 'Glass').cyl(.95, 2.4, loc=(0, -7.0, 1.2), seg=12, bevel=0)
    a.part('Revolving_top', 'Steel').cyl(1.0, .2, loc=(0, -7.0, 2.5), seg=12, bevel=0)
    for face, p in (('-x', (-6.9, 0)), ('+x', (6.9, 0)), ('+y', (0, 6.9))):
        for u in (-4.0, -1.35, 1.35, 4.0):
            for z in (2.2, 5.6):
                q = slide(face, (p[0], p[1], z), u)
                fbox(a.part('Frames', 'Armor'), face, q, (1.8, .08, 2.2), out=.03)
                fbox(pane(a, rng, .35), face, q, (1.6, .05, 2.0), out=.06)
    for sx in (-1, 1):  # planters by the entrance
        a.part('Planters', 'Concrete').box((1.4, .9, .6), loc=(sx * 5.4, -7.0 + .35, .3), bevel=.04, seg=1)
        a.part('Planter_shrubs', 'FoliageDark', flat=True).ico((.65, .45, .45), loc=(sx * 5.4, -6.65, .75), sub=1,
                                                               jitter=.25, seed=sx + 4)
    # Tower: chamfered glass shaft with mullions, transoms, a plant band and lit windows.
    tz0, tz1, tw, tc = ph - .1, 35.8, 12.0, 1.2
    a.part('Tower_glass', 'Glass').prism(chamfered(tw, tw, tc), tz1 - tz0, loc=(0, 0, (tz0 + tz1) / 2), axis='Z',
                                         bevel=0)
    steel = a.part('Mullions', 'Steel')
    h = tz1 - tz0
    flat = tw - 2 * tc
    for face, (nx, ny) in NORMAL.items():
        for k in range(7):
            u = -flat / 2 + k * flat / 6
            tx, ty = TANGENT[face]
            fbox(steel, face, (nx * tw / 2 + tx * u, ny * tw / 2 + ty * u, (tz0 + tz1) / 2), (.1, .12, h), out=.04)
    for sx in (-1, 1):
        for sy in (-1, 1):
            m = tw / 2 - tc / 2
            steel.box((.12, .12, h), loc=(sx * (m + .03), sy * (m + .03), (tz0 + tz1) / 2), rot=(0, 0, math.pi / 4),
                      bevel=0)
    floors = 9
    fh = h / floors
    for f in range(1, floors):
        z = tz0 + f * fh
        if f == 5:
            a.part('Plant_band', 'Armor').prism(chamfered(tw + .14, tw + .14, tc + .03), 1.3, loc=(0, 0, z + .3),
                                                axis='Z', bevel=0)
            continue
        steel.prism(chamfered(tw + .1, tw + .1, tc + .02), .14, loc=(0, 0, z), axis='Z', bevel=0)
    for f in range(floors):
        if f == 5:
            continue
        zc = tz0 + (f + .5) * fh
        for face, (nx, ny) in NORMAL.items():
            tx, ty = TANGENT[face]
            for k in range(6):
                if rng.random() < .22:
                    u = -flat / 2 + (k + .5) * flat / 6
                    fbox(a.part('Tower_lit', 'Lamp'), face, (nx * tw / 2 + tx * u, ny * tw / 2 + ty * u, zc),
                         (flat / 6 - .3, .04, fh - .5), out=.02)
    # Terrace on the tower top, the setback crown and its glass balustrade.
    a.part('Terrace', 'Asphalt').prism(chamfered(tw - .1, tw - .1, tc - .04), .16, loc=(0, 0, tz1 + .02), axis='Z',
                                       bevel=0)
    a.part('Terrace_edge', 'Steel').prism(chamfered(tw + .12, tw + .12, tc + .03), .2, loc=(0, 0, tz1 - .02), axis='Z',
                                          bevel=0)
    a.part('Balustrade', 'Glass').shell(chamfered(tw - .05, tw - .05, tc - .02), 1.1, .06, loc=(0, 0, tz1 + .08),
                                        bevel=0)
    cw, cc, cz1 = 8.6, .9, 39.0
    a.part('Crown', 'MetalSheet').prism(chamfered(cw, cw, cc), cz1 - tz1, loc=(0, 0, (tz1 + cz1) / 2), axis='Z',
                                        bevel=.03, seg=1)
    for face, (nx, ny) in NORMAL.items():
        tx, ty = TANGENT[face]
        fbox(a.part('Crown_louvres', 'Armor'), face, (nx * cw / 2, ny * cw / 2, 38.45), (cw - 2 * cc - .4, .06, .7),
             out=.03)
        for k in range(3):
            fbox(a.part('Crown_slats', 'Steel'), face, (nx * cw / 2, ny * cw / 2, 38.23 + k * .22),
                 (cw - 2 * cc - .5, .04, .06), out=.07)
    door(a, '-y', (-2.2, -cw / 2, tz1 + .1), w=.9, h=2.0, mat='Steel', frame='Armor', step=None, lamp=True)
    tz = tz1 + .1
    for x, y in ((-4.5, 4.5), (4.6, 4.4)):
        roof_tank(a, x * .98, y * .98, tz, r=.5, h=1.1, mat='Fuel', leg=.6)
    for x, y in ((-4.9, -2.0), (-4.9, .4), (2.2, -5.0), (-.4, -5.0)):
        roof_ac(a, x, y, tz, w=1.0, d=.9, h=.7)
    # Window-cleaning crane on a rail along the right side of the terrace.
    bmu = a.part('BMU', 'Hazard')
    a.part('BMU_rail', 'Steel').box((.14, 7.0, .1), loc=(5.2, .6, tz + .05), bevel=0)
    bmu.box((.9, 1.2, .9), loc=(5.2, 2.6, tz + .55), bevel=.05, seg=1)
    bmu.limb((5.2, 2.6, tz + 1.0), (5.2, 2.6, tz + 2.3), .25, .25, bevel=0)
    bmu.limb((5.0, 2.6, tz + 2.2), (6.55, 2.6, tz + 2.3), .2, .2, bevel=0)
    a.part('BMU_cradle', 'Steel').box((.3, 1.4, .3), loc=(6.5, 2.6, tz + 1.4), bevel=0)
    # Spire at the back-left corner of the terrace.
    a.part('Spire', 'Steel').cyl(.16, 7.0, loc=(-4.6, 2.0, tz + 3.5), r2=.05, seg=8, bevel=0)
    red = a.part('Obstruction_lights', 'LavaGlow')
    for z in (tz + 3.6, tz + 7.05):
        red.sphere(.09, loc=(-4.6, 2.0, z), seg=6, rings=4)
    # Helipad on struts over the crown.
    hz = cz1 + .45
    pad = 5.1
    for sx in (-1, 1):
        for sy in (-1, 1):
            steel.limb((sx * 3.6, sy * 3.6, cz1 - .02), (sx * 4.6, sy * 4.6, hz - .2), .16, .16, bevel=0)
    a.part('Helipad', 'Asphalt').box((2 * pad, 2 * pad, .26), loc=(0, 0, hz - .13), bevel=.03, seg=1)
    a.part('Helipad_circle', 'Hazard').cyl(3.75, .035, loc=(0, 0, hz), seg=24, bevel=0)
    white = a.part('Helipad_H', 'PlasterWhite')
    for sx in (-1, 1):
        white.box((.5, 3.0, .04), loc=(sx * .85, 0, hz + .035), bevel=0)
    white.box((1.3, .5, .04), loc=(0, 0, hz + .06), bevel=0)
    lamp = a.part('Pad_lights', 'Lamp')
    for k in range(12):
        t = k * TAU / 12
        c, s = math.cos(t), math.sin(t)
        m = pad - .2
        k2 = m / max(abs(c), abs(s))
        lamp.box((.16, .16, .1), loc=(c * k2, s * k2, hz + .04), bevel=.02, seg=1)
    net = a.part('Safety_net', 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            net.limb((sx * pad, sy * pad, hz - .1), (sx * (pad + .9), sy * (pad + .9), hz + .15), .05, .05, bevel=0)
    ring = [(-pad - .9, -pad - .9, hz + .15), (pad + .9, -pad - .9, hz + .15), (pad + .9, pad + .9, hz + .15),
            (-pad - .9, pad + .9, hz + .15), (-pad - .9, -pad - .9, hz + .15)]
    net.tube(ring, .04, seg=4, caps=False)
    q = pad + .85
    a.part('Net_mesh', 'Undercarriage').shell([(-q, -q), (q, -q), (q, q), (-q, q)], .06, .8, loc=(0, 0, hz + .02),
                                              bevel=0)
    net.cyl(.04, 1.8, loc=(pad - .4, pad - .4, hz + .9), seg=6, bevel=0)
    a.part('Windsock', 'BarrelRed').cyl(.2, .9, loc=(pad - .4 - .45, pad - .4, hz + 1.65), r2=.1, rot=(0, -R90, 0),
                                        seg=8, bevel=0)
    a.part('Windsock_bands', 'PlasterWhite').cyl(.17, .2, loc=(pad - .4 - .6, pad - .4, hz + 1.65), rot=(0, -R90, 0),
                                                 seg=8, bevel=0)
    stair = a.part('Pad_stair', 'Steel')
    for dx in (-.35, .35):
        stair.limb((2.6 + dx, -cw / 2 - .9, tz + .05), (2.6 + dx, -pad + .4, hz - .2), .08, .08, bevel=0)


def parked_car(a, x, y, z, yaw, mat):
    """Low-detail parked car (4.2 x 1.8 m) for garage decks: a painted body and roof, glass cabin
    and a dark base."""
    c, s = math.cos(yaw), math.sin(yaw)

    def at(u, v, h):
        return (x + c * u - s * v, y + s * u + c * v, z + h)
    rot = (0, 0, yaw)
    a.part('Car_bases', 'Rubber').box((1.66, 3.9, .34), loc=at(0, 0, .18), rot=rot, bevel=0)
    a.part('Car_bodies', mat).box((1.78, 4.2, .52), loc=at(0, 0, .6), rot=rot, bevel=.08, seg=1)
    a.part('Car_glass', 'Glass').box((1.56, 2.1, .5), loc=at(0, .25, 1.1), rot=rot, bevel=0, taper=(.9, .72))
    a.part('Car_roofs', mat).box((1.36, 1.4, .06), loc=at(0, .3, 1.36), rot=rot, bevel=0)


def parking_garage(a):
    """Open parking garage (16 x 12 m, 10.2 m; 12.3 m to the stair tower): three open decks and a
    roof deck on a column grid, perimeter upstands with level numbers, a ramp rising through a gap
    in the roof, parked cars on every level, bay lines and lamp posts on the roof, a glazed stair
    tower with a lit P sign, a lift room and a barrier at the entrance."""
    rng = random.Random(251)
    conc = a.part('Structure', 'Concrete')
    hx, hy = 7.8, 5.8
    levels = (3.15, 6.15, 9.15)
    xs = (-7.3, -3.65, 0.0, 3.65, 7.3)
    ys = (-5.3, 0.0, 5.3)
    for x in xs:
        for y in ys:
            conc.box((.5, .5, levels[-1] - .05), loc=(x, y, (levels[-1] - .05) / 2), bevel=.02, seg=1)
    a.part('Ground_slab', 'Asphalt').box((2 * hx, 2 * hy, .08), loc=(0, 0, -.01), bevel=0)
    ramp_x0, ramp_x1, ramp_y0, ramp_y1 = .4, 7.55, 2.7, 5.45
    ry0 = ramp_y0 + .02  # the ramp's side faces stand clear of the roof pieces'
    for k, zt in enumerate(levels):
        if k < 2:
            conc.box((2 * hx, 2 * hy, .3), loc=(0, 0, zt - .15), bevel=.03, seg=1)
        else:
            conc.box((2 * hx, ramp_y0 + hy, .3), loc=(0, (ramp_y0 - hy) / 2, zt - .15), bevel=.03, seg=1)
            conc.box((ramp_x0 + hx, hy - ramp_y0, .3), loc=((ramp_x0 - hx) / 2, (ramp_y0 + hy) / 2, zt - .15),
                     bevel=.03, seg=1)
            conc.box((hx - ramp_x1 + .02, hy - ramp_y0, .3), loc=((ramp_x1 + hx) / 2, (ramp_y0 + hy) / 2, zt - .15),
                     bevel=0)
        # Upstands on the deck edge, an opening at the ramp on the roof, a painted band.
        rim(a.part('Upstands', 'Concrete'), -hx - .02, hx + .02, -hy - .02, hy + .02, zt - .32, 1.3, .2, bevel=.02)
        for face, p, L in faces_of(-hx, hx, -hy, hy):
            if face in ('-y', '+x'):
                fbox(a.part('Upstand_band', 'PlasterWhite'), face, (p[0], p[1], zt + .75), (L - .4, .04, .16), out=.03)
        fbox(a.part('Level_boards', 'ContainerBlue'), '-y', (-6.2, -hy, zt + .45), (.8, .06, .7), out=.04)
        numeral(a.part('Level_numbers', 'PlasterWhite'), str(k + 1), '-y', (-6.2, -hy - .07, zt + .45), h=.45, t=.08,
                out=.02)
    # Ramp from deck 2 up through the gap in the roof.
    run = ramp_x1 - ramp_x0
    rise = levels[2] - levels[1]
    ang = math.atan2(rise, run)
    L = math.hypot(run, rise)
    conc.box((L, ramp_y1 - ry0, .3), loc=((ramp_x0 + ramp_x1) / 2, (ry0 + ramp_y1) / 2,
                                               (levels[1] + levels[2]) / 2 - .15 / math.cos(ang)),
             rot=(0, -ang, 0), bevel=0)
    a.part('Ramp_paint', 'Hazard').box((L, .14, .04), loc=((ramp_x0 + ramp_x1) / 2, ramp_y0 + .2,
                                                           (levels[1] + levels[2]) / 2 + .01), rot=(0, -ang, 0),
                                       bevel=0)
    # Bay lines on the roof deck and parked cars.
    zr = levels[2]
    # Cars park in the bays between the column lines (x) clear of the column rows (y).
    bays = (-5.47, -1.83, 1.83, 5.47)
    lines = a.part('Bay_lines', 'PlasterWhite')
    for x in bays:
        for dx in (-1.2, 1.2):
            lines.box((.1, 4.2, .03), loc=(x + dx, -2.9, zr + .005), bevel=0)
    for dx in (-1.2, 1.2):
        lines.box((.1, 4.2, .03), loc=(-1.83 + dx, 2.65, zr + .005), bevel=0)
    paints = ('CarRed', 'ContainerBlue', 'PlasterWhite', 'Hazard', 'Armor', 'RoofGreen', 'Steel', 'ContainerRed')
    spots = [(x, -2.9, zr, 0) for x in (bays[0], bays[1], bays[3])]
    spots += [(x, -2.9, levels[1], 0) for x in bays] + [(bays[1], 2.65, levels[1], math.pi)]
    spots += [(x, -2.9, levels[0], 0) for x in (bays[0], bays[2], bays[3])] + [(x, 2.65, levels[0], math.pi)
                                                                               for x in (bays[1], bays[2])]
    spots += [(x, -2.9, .03, 0) for x in (bays[0], bays[1])] + [(x, 2.65, .03, math.pi) for x in (bays[2], bays[3])]
    for i, (x, y, z, yaw) in enumerate(spots):
        parked_car(a, x + rng.uniform(-.1, .1), y + rng.uniform(-.15, .15), z, yaw + rng.uniform(-.04, .04),
                   paints[(i * 3) % len(paints)])
    for x, y in ((-5.0, -.4), (2.5, -.4), (-1.3, 4.9)):
        pole = a.part('Lamp_posts', 'Armor')
        pole.cyl(.07, 3.8, loc=(x, y, zr + 1.9), seg=6, bevel=0)
        pole.box((.1, .9, .1), loc=(x, y - .4, zr + 3.8), bevel=0)
        a.part('Lamp_heads', 'Lamp').box((.3, .5, .06), loc=(x, y - .75, zr + 3.73), bevel=0)
    # Stair tower with a glazed strip and the lit P sign; lift room beside it on the roof.
    sx0, sx1, sy0, sy1, sh = -hx - .06, -hx + 3.0, hy - 3.2, hy + .06, zr + 3.1
    scx, scy = (sx0 + sx1) / 2, (sy0 + sy1) / 2
    a.part('Stair_tower', 'Concrete').box((sx1 - sx0, sy1 - sy0, sh), loc=(scx, scy, sh / 2 - .01), bevel=.04, seg=1)
    a.part('Stair_cap', 'Armor').box((sx1 - sx0 + .2, sy1 - sy0 + .2, .16), loc=(scx, scy, sh + .06), bevel=.02, seg=1)
    for z in (1.6, 4.6, 7.6, 10.6):
        fbox(pane(a, rng, .6), '-y', (-hx + 1.5, sy0, z), (1.6, .06, 2.2), out=.02)
    fbox(a.part('P_sign', 'ContainerBlue'), '+x', (sx1, sy0 + 1.6, sh - 1.4), (2.2, .08, 2.2), out=.04)
    pl = a.part('P_letter', 'Lamp')
    q = (sx1 + .09, sy0 + 1.6, sh - 1.4)
    fbox(pl, '+x', slide('+x', q, -.35), (.3, .04, 1.6), out=.0)
    fbox(pl, '+x', slide('+x', q, .05, .5), (.6, .04, .28), out=.012)
    fbox(pl, '+x', slide('+x', q, .05, .05), (.6, .04, .26), out=.012)
    fbox(pl, '+x', slide('+x', q, .35, .28), (.26, .04, .6), out=.0)
    a.part('Lift_room', 'Concrete').box((2.4, 2.2, 2.4), loc=(-hx + 4.4, hy - 1.4, zr + 1.18), bevel=.04, seg=1)
    roof_ac(a, -hx + 4.4, hy - 1.4, zr + 2.38, w=1.0, d=.8, h=.5)
    # Entrance barrier and pay booth at the front right.
    a.part('Booth', 'PlasterWhite').box((1.2, 1.2, 2.3), loc=(5.4, -hy + .9, 1.15), bevel=.04, seg=1)
    fbox(pane(a, rng, .8), '-y', (5.4, -hy + .3, 1.5), (.9, .05, .8), out=.01)
    arm = a.part('Barrier_arm', 'PlasterWhite')
    arm.box((3.2, .1, .1), loc=(3.2, -hy + .55, 1.0), bevel=0)
    for k in range(4):
        a.part('Barrier_stripes', 'BarrelRed').box((.35, .12, .12), loc=(2.0 + k * .8, -hy + .55, 1.0), bevel=0)
    a.part('Barrier_post', 'Hazard').box((.3, .3, 1.1), loc=(4.75, -hy + .55, .55), bevel=.02, seg=1)
    fbox(a.part('Height_bar', 'Hazard'), '-y', (3.2, -hy, 2.55), (3.4, .1, .2), out=.06)
    for x in (1.7, 4.7):
        a.part('Height_bar_hangers', 'Steel').box((.04, .04, .3), loc=(x, -hy - .06, 2.78), bevel=0)


def billboard(a):
    """Roadside billboard (8 x 1.5 m, 8.3 m): two steel posts on footings carry a trussed 8 x 3.2 m
    panel with a generic advert of colour blocks (a sun disc, a sweep, a red product shape and
    lettering; no real brand), a railed catwalk and four lamps lighting the face."""
    rng = random.Random(261)
    steel = a.part('Steel', 'Steel')
    frame = a.part('Frame', 'Armor')
    for x in (-2.4, 2.4):
        a.part('Footings', 'Concrete').box((.6, .6, .4), loc=(x, .35, .16), bevel=.04, seg=1)
        frame.box((.34, .34, 7.9), loc=(x, .35, 4.05), bevel=.02, seg=1)
    z0, z1 = 5.0, 8.2
    frame.box((8.0, .2, z1 - z0), loc=(0, 0, (z0 + z1) / 2), bevel=.03, seg=1)
    for z in (5.3, 7.9):
        steel.box((7.6, .16, .16), loc=(0, .15, z), bevel=0)
    for x in (-3.4, -1.0, 1.0, 3.4):
        steel.limb((x, .2, 5.3), (x + (.9 if x < 0 else -.9), .2, 7.9), .1, .1, bevel=0)
    # Advert: a blue field, a sun disc, a white sweep, a red product shape, lettering.
    ad = -.1
    a.part('Ad_field', 'ContainerBlue').box((7.7, .04, 2.9), loc=(0, ad - .01, (z0 + z1) / 2), bevel=0)
    a.part('Ad_sun', 'Hazard').cyl(1.05, .03, loc=(-2.4, ad - .04, 7.0), rot=ALONG_Y, seg=16, bevel=0)
    a.part('Ad_sweep', 'PlasterWhite').box((5.4, .03, .38), loc=(.6, ad - .06, 6.3), rot=(0, -.18, 0), bevel=0)
    a.part('Ad_product', 'CarRed').box((1.1, .04, 2.1), loc=(2.6, ad - .085, 6.65), bevel=.12, seg=2)
    a.part('Ad_product_cap', 'PlasterWhite').box((.6, .04, .35), loc=(2.6, ad - .11, 7.8), bevel=.05, seg=1)
    letters(a, rng, '-y', (-1.2, ad - .04, 5.4), 4.0, h=.4, mat='PlasterWhite', out=.03)
    a.part('Ad_badge', 'BarrelRed').box((.5, .04, .5), loc=(-3.4, ad - .09, 5.45), rot=(0, math.pi / 4, 0), bevel=0)
    # Catwalk with a railing and four lamps on goosenecks.
    frame.box((8.0, .64, .07), loc=(0, -.46, 4.85), bevel=0)
    for x in (-3.0, 0, 3.0):
        steel.limb((x, -.05, 5.04), (x, -.72, 4.8), .06, .06, bevel=0)
    for x in (-3.95, -2.0, 0.0, 2.0, 3.95):
        steel.box((.05, .05, 1.0), loc=(x, -.73, 5.38), bevel=0)
    steel.box((7.86, .07, .05), loc=(0, -.73, 5.88), bevel=0)
    steel.box((7.86, .07, .04), loc=(0, -.73, 5.4), bevel=0)
    for x in (-3.0, -1.0, 1.0, 3.0):
        steel.tube([(x, -.67, 4.9), (x, -.8, 5.3), (x, -.85, 5.6), (x, -.78, 5.76)], .03, seg=4)
        a.part('Lamp_heads', 'Armor').box((.36, .22, .14), loc=(x, -.74, 5.84), rot=(.6, 0, 0), bevel=.02, seg=1)
        a.part('Lamp_lenses', 'Lamp').box((.3, .03, .1), loc=(x, -.74 + .125 * .825, 5.84 + .125 * .565),
                                          rot=(.6, 0, 0), bevel=0)
    ladder(steel, (2.4, .1, .4), 4.85, 0.0, width=.4, step=.35, rung=.07)


def bus(a):
    """City bus (11 x 2.6 m, 3.3 m; nose to +X, doors on the kerb side, -Y): a CarRed body (the map
    can repaint it like the town cars) with a white livery band, a window band with pillars, two
    glazed doors, an amber destination sign, a roof air-conditioning pod and hatches, open wheel
    arches in the skirts, mirrors, wipers, lights and bumpers."""
    paint = a.part('Body', 'CarRed')
    W = 2.5
    hx = W / 2
    paint.prism([(-5.47, 1.08), (5.45, 1.08), (5.47, 2.95), (5.35, 3.08), (-5.25, 3.08), (-5.46, 2.85), (-5.5, 1.5)],
                W, axis='X', bevel=.1, seg=2)
    a.part('Underbody', 'Undercarriage').box((2.12, 10.6, .7), loc=(0, 0, .75), bevel=0)
    skirt = [(-5.45, -3.85), (-2.55, 1.85), (3.15, 5.43)]
    for sx in (-1, 1):
        for ya, yb in skirt:
            paint.box((.16, yb - ya, .7), loc=(sx * (hx - .08), (ya + yb) / 2, .75), bevel=.03, seg=1)
    for y in (-5.36, 5.34):
        paint.box((W - .1, .2, .66), loc=(0, y, .73), bevel=.03, seg=1)
    armor = a.part('Trim', 'Armor')
    for y in (-5.48, 5.46):
        armor.box((W + .04, .22, .34), loc=(0, y, .55), bevel=.04, seg=1)
    # Glazing: windscreen, window band, rear window, doors, and the destination sign.
    glass = a.part('Glass', 'Glass')
    fbox(glass, '-y', (0, -5.49, 1.98), (2.2, .04, 1.15), out=.01)
    fbox(glass, '+y', (0, 5.47, 2.35), (1.9, .04, .9), out=.01)
    dark = a.part('Pillars', 'Armor')
    for face, x in (('-x', -hx), ('+x', hx)):
        fbox(glass, face, (x, .25, 2.05), (9.6, .04, 1.15), out=.01)
        for k in range(9):
            y = -4.35 + k * 1.2
            if face == '-x' and any(d0 - .1 < y < d1 + .1 for d0, d1 in ((-5.15, -3.95), (.2, 1.5))):
                continue
            fbox(dark, face, (x, y, 2.05), (.12, .05, 1.2), out=.03)
        fbox(a.part('Livery', 'PlasterWhite'), face, (x, 0, 1.3), (10.8, .03, .22), out=.015)
    for y0, y1 in ((-5.15, -3.95), (.2, 1.5)):
        yc = (y0 + y1) / 2
        fbox(armor, '-x', (-hx, yc, 1.75), (y1 - y0 + .1, .05, 2.2), out=.035)
        for dy in (-.3, .3):
            fbox(glass, '-x', (-hx, yc + dy, 1.8), (.5, .04, 1.95), out=.065)
    fbox(a.part('Destination', 'Alloy'), '-y', (0, -5.46, 2.7), (1.7, .04, .2), out=.02)
    fbox(a.part('Route', 'Alloy'), '+x', (hx, -4.5, 2.95), (.5, .04, .18), out=.02)
    # Lights, mirrors, wipers, plates, rear grille.
    for sx in (-1, 1):
        a.part('Headlights', 'Lamp').box((.34, .05, .16), loc=(sx * .85, -5.5, 1.25), bevel=.02, seg=1)
        a.part('Indicators', 'Alloy').box((.12, .05, .1), loc=(sx * 1.12, -5.51, 1.25), bevel=0)
        a.part('Taillights', 'BarrelRed').box((.16, .05, .5), loc=(sx * 1.1, 5.5, 1.5), bevel=.02, seg=1)
        armor.limb((sx * 1.2, -5.2, 2.75), (sx * 1.34, -5.45, 2.75), .05, .05, bevel=0)
        armor.box((.08, .16, .42), loc=(sx * 1.36, -5.5, 2.55), bevel=.02, seg=1)
    rub = a.part('Wipers', 'Rubber')
    for x in (-.5, .5):
        rub.limb((x, -5.525, 1.5), (x + .35, -5.525, 2.3), .04, .02, bevel=0)
    a.part('Plates', 'PlasterWhite').box((.5, .03, .13), loc=(0, -5.6, .56), bevel=0)
    a.part('Plates', 'PlasterWhite').box((.5, .03, .13), loc=(0, 5.58, .56), bevel=0)
    for k in range(4):
        fbox(armor, '+y', (0, 5.46, 1.25 + k * .12), (1.6, .03, .05), out=.02)
    # Roof: air-conditioning pod with grilles, escape hatches.
    a.part('Roof_pod', 'PlasterWhite').box((1.9, 2.6, .32), loc=(0, 1.6, 3.2), bevel=.08, seg=1)
    for dy in (-.7, .7):
        a.part('Pod_grilles', 'Armor').box((1.4, .5, .04), loc=(0, 1.6 + dy, 3.37), bevel=0)
    for y in (-3.0, -1.1, 4.0):
        a.part('Hatches', 'Armor').box((.7, .7, .06), loc=(0, y, 3.1), bevel=.02, seg=1)
    _wheels(a, [(sx * 1.0, y) for sx in (-1, 1) for y in (-3.2, 2.5)], .5, .34, hub=.45)
    _turn(a, R90)


def traffic_light(a):
    """Traffic light (0.6 x 0.6 m, 4.7 m): a pole on a footing with two signal heads, one facing
    -Y showing red (LavaGlow) and one facing +X showing green (SignalGreen), the others dark
    lenses under visors, a push-button box and a street name plate."""
    a.part('Footing', 'Concrete').box((.5, .5, .16), loc=(0, 0, .06), bevel=.02, seg=1)
    pole = a.part('Pole', 'Armor')
    pole.cyl(.075, 4.4, loc=(0, 0, 2.3), r2=.06, seg=8, bevel=0)
    pole.cyl(.1, .3, loc=(0, 0, .28), seg=8, bevel=0)
    pole.cyl(.08, .08, loc=(0, 0, 4.545), seg=8, bevel=0)
    lit = {'-y': 0, '+x': 2}
    lens_off = ('BarrelRed', 'Rust', 'RoofGreen')
    lens_on = ('LavaGlow', 'Alloy', 'SignalGreen')
    for face, (cx, cy) in (('-y', (-.09, -.15)), ('+x', (.15, .09))):
        nx, ny = NORMAL[face]
        box = (.28, .18, .88) if nx == 0 else (.18, .28, .88)
        zc = 3.5
        pole.box(box, loc=(cx, cy, zc), bevel=.02, seg=1)
        back = (.38, .03, 1.0) if nx == 0 else (.03, .38, 1.02)
        a.part('Backplates', 'Charred').box(back, loc=(cx - nx * .1, cy - ny * .1, zc), bevel=0)
        pole.box((.14, .1, .08) if nx else (.1, .14, .08), loc=(cx - nx * .06, cy - ny * .06, zc + .5), bevel=0)
        for k in range(3):
            z = zc + .27 - k * .27
            mat = lens_on[k] if lit[face] == k else lens_off[k]
            rot = ALONG_Y if nx == 0 else ALONG_X
            fx, fy = cx + nx * .1, cy + ny * .1
            a.part('Lenses', mat).cyl(.085, .03, loc=(fx, fy, z), rot=rot, seg=10, bevel=0)
            vis = (.22, .05, .03) if nx == 0 else (.05, .22, .03)
            a.part('Visors', 'Armor').box(vis, loc=(fx + nx * .035, fy + ny * .035, z + .1), rot=(ny * -.3, nx * .3, 0),
                                          bevel=0)
    a.part('Button_box', 'Hazard').box((.12, .1, .2), loc=(-.1, -.03, 1.2), bevel=.02, seg=1)
    a.part('Street_plate', 'ContainerBlue').box((.03, .45, .16), loc=(-.1, .1, 2.7), bevel=0)
    a.part('Street_plate_text', 'PlasterWhite').box((.02, .36, .07), loc=(-.12, .1, 2.7), bevel=0)
    pole.box((.06, .06, .06), loc=(-.08, .1, 2.7), bevel=0)


# name: (builder, Asset options)
BUILDERS = {
    'basalt_rock_a': (basalt_rock_a, dict(ao_distance=1.0, grime_height=.3)),
    'basalt_rock_b': (basalt_rock_b, dict(ao_distance=1.2, grime_height=.3)),
    'basalt_rock_c': (basalt_rock_c, dict(ao_distance=.8, grime_height=.3)),
    'obsidian_spire': (obsidian_spire, dict(ao_distance=1.2, grime_height=.4)),
    'lava_vent': (lava_vent, dict(ao_distance=.8, grime_height=.3)),
    'charred_tree': (charred_tree, dict(ao_distance=.8, grime_height=.5)),
    'volcanic_cliff': (volcanic_cliff, dict(ao_distance=2.0, grime_height=1.0)),
    'jungle_tree_a': (jungle_tree_a, dict(ao_distance=1.6, grime_height=.6)),
    'jungle_tree_b': (jungle_tree_b, dict(ao_distance=1.6, grime_height=.6)),
    'jungle_tree_c': (jungle_tree_c, dict(ao_distance=1.6, grime_height=.6)),
    'bamboo_clump': (bamboo_clump, dict(ao_distance=.8, grime_height=.4)),
    'fern_bush': (fern_bush, dict(ao_distance=.5, grime_height=.2)),
    'temple_ruin': (temple_ruin, dict(ao_distance=1.8, grime_height=1.0)),
    'stilt_hut': (stilt_hut, dict(ao_distance=1.2, grime_height=.6)),
    'hangar': (hangar, dict(ao_distance=2.2, grime_height=1.0)),
    'control_tower': (control_tower, dict(ao_distance=1.4, grime_height=.8)),
    'parked_jet': (parked_jet, dict(ao_distance=.9, grime_height=.5)),
    'fuel_truck': (fuel_truck, dict(ao_distance=.6, grime_height=.5)),
    'radar_dome': (radar_dome, dict(ao_distance=1.4, grime_height=.8)),
    'revetment': (revetment, dict(ao_distance=1.0, grime_height=.5)),
    'runway_light': (runway_light, dict(ao_distance=.15, grime_height=.1)),
    'highrise_a': (highrise_a, dict(ao_distance=2.0, grime_height=1.0)),
    'highrise_b': (highrise_b, dict(ao_distance=2.0, grime_height=1.0)),
    'skyscraper': (skyscraper, dict(ao_distance=2.2, grime_height=1.0)),
    'parking_garage': (parking_garage, dict(ao_distance=1.8, grime_height=.8)),
    'billboard': (billboard, dict(ao_distance=.8, grime_height=.5)),
    'bus': (bus, dict(ao_distance=.6, grime_height=.5)),
    'traffic_light': (traffic_light, dict(ao_distance=.3, grime_height=.3)),
}
