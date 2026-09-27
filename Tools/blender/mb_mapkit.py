"""Machine Brigade battlefield dressing kit built with frontier_kit: the clutter of a fought-over
battlefield that the map generator scatters along roads, round objectives and camps and across open
ground, plus a few landmark pieces. All seen from the high three-quarter game camera, so each one is
built to read at a glance:
  * wrecks: wreck_tank, wreck_truck, wreck_car, artillery_wreck (Charred and Rust, with bare-metal
    ash patches; no Team paint);
  * earthworks: trench_straight, trench_corner, foxhole, crater_large, tank_ditch;
  * camp and road clutter: command_tent, camo_net, supply_pile, fuel_bladder, checkpoint, barricade;
  * lines and masts: power_pylon, telegraph_pole, radio_mast;
  * landmarks: bridge_road, ruin_house, ruin_tower, and a shell-shattered dead_tree.

Conventions follow mb_vehicles / mb_props: metres, +Z up, Blender -Y is the front, origins on the
ground at the footprint centre (Blender X = width, Y = depth). Every piece is a static prop: no
pivots, no Team paint. Materials are the neutral kit set (Dirt, Sandbag, Concrete, Steel, Wood,
LogWood, Canvas, Charred, Rust, Rubber...), so each piece sits on any map theme; nothing carries baked
snow or sand, and no grass. Camouflage nets are modelled with real holes (cells left out of the mesh),
because alpha cut-outs are not available. Touching parts overlap or stand at least 1 cm apart, never
face to face (coplanar faces z-fight). Earthworks (trenches, foxhole, crater, anti-tank ditch) are
built above the ground: their "depth" is the height of their banks over a floor at ground level, and
their outer slopes sink 5 cm below z = 0 so they never float on uneven ground. The bridge's piers and
abutments reach 1 m below ground to meet a river bed.

Tiling: trench_straight ends flush at y = +-4 m on a centreline at x = 0; trench_corner's arms end
flush on the footprint edge with the same cross-section (centreline enters at (-1.3, -2.5) heading +Y
and leaves at (+2.5, +1.3) heading +X); tank_ditch ends flush at y = +-5 m.
"""
import math
import random

import bmesh
from mathutils import Euler, Matrix, Vector, noise

from mb_siege import bag_arc, bag_run, coil, crate, generator, hazard_sign, lattice, shells
from mb_terrain import _split
from mb_vehicles import ACROSS, FORWARD, R90, _face_frame, _frame, _hull2d, _jerrycans

TAU = math.tau
UP = Vector((0, 0, 1))


# ----------------------------------------------------------------------------- shared helpers
def _along(d):
    """Euler rotation that turns local +Z onto direction d (cylinders and cones along d)."""
    return UP.rotation_difference(Vector(d).normalized()).to_euler('XYZ')


def _basis(o, x, z):
    """Frame at o whose local X runs along x and whose local Z is z made square to it."""
    x = Vector(x).normalized()
    y = Vector(z).cross(x).normalized()
    z = x.cross(y)
    return Matrix(((x.x, y.x, z.x, o[0]), (x.y, y.y, z.y, o[1]), (x.z, y.z, z.z, o[2]), (0, 0, 0, 1)))


def _box_on(part, m, size, off=(0, 0, 0), bevel=0.0, seg=1, taper=(1, 1)):
    """Box in frame m: size along m's axes, off its centre in m's local coordinates."""
    part.box(size, loc=m @ Vector(off), rot=m.to_euler('XYZ'), bevel=bevel, seg=seg, taper=taper)


def _blotch(part, m, r, seed, sides=10, depth=.03, squash=1.0):
    """Irregular flat patch (rust, ash, soot, a burnt hole) on the surface whose frame is m (local Z out
    of the surface): a lobed outline, so no two read alike. It sinks half its depth, so its face stands
    depth / 2 proud."""
    rng = random.Random(seed)
    ph, lobes = rng.uniform(0, TAU), rng.choice((2, 3))
    pts = []
    for k in range(sides):
        t = (k + rng.uniform(-.25, .25)) * TAU / sides
        rr = r * (.7 + .22 * math.sin(lobes * t + ph) + rng.uniform(-.14, .14))
        pts.append((rr * math.cos(t), rr * squash * math.sin(t)))
    part.prism(pts, depth, loc=m.to_translation(), rot=m.to_euler('XYZ'), axis='Z', bevel=0)


def _top(x, y, z, yaw=0.0):
    """Frame on an upward-facing surface."""
    return _frame((x, y, z), (0, 0, yaw))


def _side(x, y, z, s):
    """Frame on a vertical face whose outward normal is +-X (s = 1 / -1)."""
    return _basis((x, y, z), (0, s, 0), (s, 0, 0))


def _front(x, y, z, s=-1):
    """Frame on a vertical face whose outward normal is +-Y (s = -1: the front)."""
    return _basis((x, y, z), (-s, 0, 0), (0, s, 0))


def _transform(a, keys, m):
    """Apply matrix m to the parts with these keys (a turret knocked askew, a gun on its side)."""
    for key in keys:
        bm = a.shapes[key].bm
        bmesh.ops.transform(bm, matrix=m, verts=list(bm.verts))
        bm.normal_update()


def _rest(a, keys, contacts, sink=.02):
    """Tilt the parts with these keys so the three contact points (build coordinates) lie on the ground,
    then lower them until those points sit `sink` below it."""
    p0, p1, p2 = (Vector(p) for p in contacts)
    n = (p1 - p0).cross(p2 - p0).normalized()
    if n.z < 0:
        n = -n
    rot = n.rotation_difference(UP).to_matrix().to_4x4()
    m = Matrix.Translation((0, 0, -(rot @ p0).z - sink)) @ rot
    _transform(a, keys, m)
    return m


def _bounds(a):
    pts = [v.co for sh in a.shapes.values() for v in sh.bm.verts]
    return (Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)]))


def _centre(a):
    """Shift everything so the footprint's bounding box is centred on the origin."""
    lo, hi = _bounds(a)
    _transform(a, list(a.shapes), Matrix.Translation((-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, 0)))


def _samples(path, step, start=0.0):
    """Points every `step` metres along a 2D polyline, with the unit tangent there."""
    pts = [Vector(p) for p in path]
    out, d = [], start
    for p, q in zip(pts, pts[1:]):
        n = (q - p).length
        t = (q - p) / n
        while d <= n + 1e-6:
            out.append((p + t * d, t))
            d += step
        d -= n
    return out


def _strip(part, rings_spec, w, th):
    """Thin lofted strip: rings_spec is [(centre, across, normal, width scale)...]; each cross-section is a
    w x th rectangle spanned by `across` and `normal` (split barrel petals, bent sheet metal)."""
    rings = []
    for c, u, n, k in rings_spec:
        c, u, n = Vector(c), Vector(u).normalized() * w * k / 2, Vector(n).normalized() * th / 2
        rings.append([tuple(c - u - n), tuple(c + u - n), tuple(c + u + n), tuple(c - u + n)])
    part.loft(rings)


def _chunks(parts, rng, cx, cy, r, h, n, z0=0.0, size=(.25, .6), seed=0.0):
    """Rubble heap: n faceted chunks inside radius r about (cx, cy), piling up to height h in the middle.
    parts is a list of parts to deal the chunks into."""
    for i in range(n):
        d = r * math.sqrt(rng.random())
        t = rng.uniform(0, TAU)
        x, y = cx + d * math.cos(t), cy + d * math.sin(t)
        z = h * (1 - (d / r) ** 2)
        s = rng.uniform(*size) * (.6 + .4 * (z / h if h else 1))
        parts[i % len(parts)].ico((s, s * rng.uniform(.7, 1.1), s * rng.uniform(.45, .7)),
                                  loc=(x, y, z0 + z * .75 + s * .2), rot=(0, 0, rng.uniform(0, TAU)), sub=1,
                                  jitter=.3, seed=seed + i * 1.37)


def _densify(path, step, clear=0.0):
    """Polyline with extra points so no span is longer than step. No extra point falls within `clear` of an
    interior corner (a bank wider than its span would fold over itself on the inside of the bend)."""
    pts = [Vector(p) for p in path]
    out = [pts[0]]
    for i, (p, q) in enumerate(zip(pts, pts[1:])):
        L = (q - p).length
        a0 = clear if i > 0 else 0.0
        a1 = L - (clear if i < len(pts) - 2 else 0.0)
        n = max(1, math.ceil((a1 - a0) / step - 1e-6))
        extra = [a0 + (a1 - a0) * k / n for k in range(n + 1)]
        out += [p.lerp(q, d / L) for d in extra if 1e-6 < d < L - 1e-6]
        out.append(q)
    return [(p.x, p.y) for p in out]


def _bank(part, path, profile, seed, amp=.03, fade=1.0, closed=False, lift=.1):
    """Earth bank swept along a 2D path with mitred corners: profile [(u, z)...] is its closed cross-section,
    u the offset to the right of travel (outwards on a counter-clockwise loop). Points higher than `lift`
    get noise up to amp, faded out within `fade` metres of an open path's ends, so pieces that end flush
    match their neighbours."""
    pts = [Vector(p) for p in path]
    n = len(pts)
    cum = [0.0]
    for p, q in zip(pts, pts[1:]):
        cum.append(cum[-1] + (q - p).length)
    off = Vector((seed * 3.1, seed * 1.7, seed * .7))
    rings = []
    for i, p in enumerate(pts):
        if closed:
            e1, e2 = (p - pts[i - 1]).normalized(), (pts[(i + 1) % n] - p).normalized()
        else:
            e1 = (p - pts[i - 1]).normalized() if i else (pts[1] - p).normalized()
            e2 = (pts[i + 1] - p).normalized() if i < n - 1 else e1
        n1, n2 = Vector((e1.y, -e1.x)), Vector((e2.y, -e2.x))
        nm = (n1 + n2).normalized() / max(.5, (1 + n1.dot(n2)) / 2) ** .5
        f = 1.0 if closed else max(0.0, min(1.0, cum[i] / fade, (cum[-1] - cum[i]) / fade))
        ring = []
        for u, z in profile:
            x, y = p.x + nm.x * u, p.y + nm.y * u
            if z > lift:
                z += amp * f * noise.noise(Vector((x * .8, y * .8, 0)) + off)
            ring.append(part.bm.verts.new((x, y, z)))
        rings.append(ring)
    if closed:
        part._faces(rings + [rings[0]], False, False)
    else:
        part._faces(rings)


def _revet(a, p0, p1, n, zs=((.05, .18), (.2, .33), (.35, .47)), piece=2.0, post=1.4, stagger=0.0):
    """Plank revetment on a vertical earth face running from p0 to p1 (2D, on the face) that faces n (into
    the trench): rows of 4 cm boards half sunk into the face, joints staggered row to row, and log posts
    in front of them between the ends (so segments laid end to end never double a post)."""
    p0, p1, n = Vector(p0), Vector(p1), Vector(n).normalized()
    L = (p1 - p0).length
    t = (p1 - p0) / L
    yaw = math.atan2(t.y, t.x)
    boards = a.part('Revetment', 'Wood')
    for r, (za, zb) in enumerate(zs):
        cuts, x = [0.0], piece * ((.45 if r % 2 else .9) + stagger) % piece + .3
        while x < L - .3:
            cuts.append(x)
            x += piece
        cuts.append(L)
        for ua, ub in zip(cuts, cuts[1:]):
            c = p0 + t * ((ua + ub) / 2)
            boards.box((ub - ua - .03, .04, zb - za), loc=(c.x, c.y, (za + zb) / 2), rot=(0, 0, yaw), bevel=0)
    posts = a.part('Revetment_posts', 'LogWood')
    k = max(1, round(L / post))
    for i in range(k):
        c = p0 + t * (L * (i + .5) / k) + n * .06
        posts.box((.1, .08, zs[-1][1] + .1), loc=(c.x, c.y, (zs[-1][1] + .1) / 2 - .04), rot=(0, 0, yaw), bevel=0)


def _duckboards(a, p0, p1, section=2.0, z=.03):
    """Duckboard walk on a trench floor from p0 to p1: sections of two log runners under board slats."""
    p0, p1 = Vector(p0), Vector(p1)
    L = (p1 - p0).length
    t = (p1 - p0) / L
    side = Vector((-t.y, t.x))
    yaw = math.atan2(t.y, t.x)
    runners, slats = a.part('Duckboard_runners', 'LogWood'), a.part('Duckboards', 'Wood')
    count = max(1, round(L / section))
    step = L / count
    for i in range(count):
        a0, a1 = i * step + .03, (i + 1) * step - .03
        for s in (-1, 1):
            c = p0 + t * ((a0 + a1) / 2) + side * s * .2
            runners.box((a1 - a0, .07, .05), loc=(c.x, c.y, z + .025), rot=(0, 0, yaw), bevel=0)
        m = max(2, round((a1 - a0) / .42))
        for j in range(m):
            c = p0 + t * (a0 + (j + .5) * (a1 - a0) / m)
            slats.box((.11, .56, .03), loc=(c.x, c.y, z + .062), rot=(0, 0, yaw), bevel=0)


# Trench cross-section to the right of the centreline: revetted inner face at .45 m, crest .52 m.
TRENCH_BANK = [(.45, -.05), (1.2, -.05), (.85, .48), (.62, .52), (.45, .46)]
TRENCH_FLOOR = [(-.44, -.05), (.44, -.05), (.44, .03), (-.44, .03)]


def _trench(a, path, seed, arms, rng):
    """Trench along a centreline path: two earth banks, a floor, plank revetment and duckboards per straight
    arm (arms: [(p0, p1, left face (a0, a1), right face (b0, b1))...]) and a sandbag lip on both crests."""
    earth = a.part('Banks', 'Dirt')
    dense = _densify(path, .5)
    _bank(earth, _densify(path, .5, clear=1.25), TRENCH_BANK, seed)
    _bank(earth, dense, [(-u, z) for u, z in TRENCH_BANK], seed + 5)
    _bank(a.part('Floor', 'Dirt'), dense, TRENCH_FLOOR, seed, lift=1.0)
    bags = a.part('Sandbags', 'Sandbag')
    for (p0, p1, left, right, crest_l, crest_r, duck) in arms:
        t = (Vector(p1) - Vector(p0)).normalized()
        n_left, n_right = Vector((t.y, -t.x)), Vector((-t.y, t.x))       # the faces look into the trench
        _revet(a, *left, n_left, stagger=rng.uniform(0, .5))
        _revet(a, *right, n_right, stagger=rng.uniform(0, .5))
        _duckboards(a, *duck)
        for k, (q0, q1) in enumerate((crest_l, crest_r)):
            bag_run(bags, rng, q0, q1, .52 + .085, size=(.7, .36, .24), half=k == 1)


# ----------------------------------------------------------------------------- trench_straight
def trench_straight(a):
    """Dug trench segment (2.4 x 8.0 m, 0.75 m): two earth banks with a plank revetment on log posts
    facing the trench, a sandbag lip along both crests, a duckboard walk on the floor, an ammunition box
    and a spade. Runs along Y; both ends are cut flush at y = +-4 m on the centreline x = 0 with the same
    cross-section as trench_corner's arms, so pieces line up. Blocks neither movement nor fire."""
    rng = random.Random(61)
    _trench(a, [(0, -4.0), (0, 4.0)], 1.0,
            [((0, -4.0), (0, 4.0), ((-.45, -4.0), (-.45, 4.0)), ((.45, -4.0), (.45, 4.0)),
              ((-.73, -4.0), (-.73, 4.0)), ((.73, -4.0), (.73, 4.0)), ((0, -4.0), (0, 4.0)))], rng)
    crate(a, (-.25, 1.6, .1), size=(.6, .32, .26), yaw=R90 + .08)
    a.part('Spade', 'Steel').box((.2, .03, .26), loc=(1.0, -1.3, .3), rot=(.25, 0, .3), bevel=0)
    a.part('Spade_handle', 'LogWood').limb((.99, -1.34, .42), (.92, -1.55, .92), .04, .04, bevel=0)
    bags = a.part('Loose_bags', 'Sandbag')
    bag_run(bags, rng, (-.2, -2.3), (.35, -2.1), .18, size=(.6, .34, .22))


# ----------------------------------------------------------------------------- trench_corner
def trench_corner(a):
    """90-degree trench corner (5.0 x 5.0 m, 0.75 m), same banks, revetment, duckboards and sandbag lip as
    trench_straight. Its centreline enters from the -Y edge at x = -1.3 heading +Y, turns at (-1.3, 1.3)
    and leaves through the +X edge at y = +1.3; both arms end flush on the footprint edge with the straight
    segment's cross-section. The inside of the bend is open ground. Blocks neither movement nor fire."""
    rng = random.Random(62)
    c = -1.3
    e = 2.5
    _trench(a, [(c, -e), (c, -c), (e, -c)], 2.0, [
        # arm 1 along +Y: left face x = c - .45 (outer), right face x = c + .45 (inner corner)
        ((c, -e), (c, -c), ((c - .45, -e), (c - .45, -c + .43)), ((c + .45, -e), (c + .45, -c - .415)),
         ((c - .73, -e), (c - .73, -c + .73)), ((c + .73, -e), (c + .73, -c - .73)), ((c, -e), (c, -c + .3))),
        # arm 2 along +X: left face y = -c + .45 (outer), right face y = -c - .45 (inner)
        ((c, -c), (e, -c), ((c - .47, -c + .45), (e, -c + .45)), ((c + .47, -c - .45), (e, -c - .45)),
         ((c - .73, -c + .73), (e, -c + .73)), ((c + .73, -c - .73), (e, -c - .73)), ((c + .31, -c), (e, -c))),
    ], rng)
    crate(a, (c + .2, -c + .2, .1), size=(.6, .32, .26), yaw=.7)
    bags = a.part('Loose_bags', 'Sandbag')
    bag_run(bags, rng, (c - .25, -1.6), (c + .2, -1.2), .18, size=(.6, .34, .22))


# ----------------------------------------------------------------------------- foxhole
def foxhole(a):
    """Round sandbagged foxhole (3.0 x 3.0 m, 0.8 m): an earth ring bank round a pit with two courses of
    sandbags on the crest, open at the back (+Y) where plank steps lead in; a light machine gun on its
    bipod rests on the front bags, with an ammunition box, a helmet and a spade in the pit. Blocks neither
    movement nor fire."""
    rng = random.Random(63)
    ring = [(math.cos(k * TAU / 24), math.sin(k * TAU / 24)) for k in range(24)]
    _bank(a.part('Bank', 'Dirt'), ring, [(-.28, -.05), (.5, -.05), (.1, .36), (-.15, .4), (-.28, .3)], 3.0,
          amp=.04, closed=True)
    a.part('Floor', 'Dirt').cyl(.76, .08, loc=(0, 0, -.01), seg=16, bevel=0)
    bags = a.part('Sandbags', 'Sandbag')
    g = .42
    for k in range(2):
        bag_arc(bags, rng, .92 - k * .05, R90 + g + .08 * k, R90 + TAU - g - .08 * k, .47 + k * .21,
                size=(.62, .34, .23), half=k == 1)
    planks = a.part('Steps', 'Wood')
    for k, (y, z) in enumerate(((.95, .36), (1.25, .2))):
        planks.box((.7, .26, .05), loc=(0, y, z), rot=(-.25, 0, rng.uniform(-.06, .06)), bevel=0)
    # Light machine gun on its bipod, on the front bags, pointing -Y.
    gun = a.part('LMG', 'Armor')
    zg = .47 + .21 + .12 + .1
    gun.box((.09, .5, .12), loc=(.05, -.72, zg), bevel=0)
    gun.box((.07, .3, .11), loc=(.05, -.33, zg - .03), rot=(.15, 0, 0), bevel=0)               # stock
    gun.box((.05, .08, .2), loc=(.05, -.62, zg - .12), bevel=0)                                # magazine
    a.part('LMG_barrel', 'Steel').cyl(.018, .55, loc=(.05, -1.2, zg + .02), rot=FORWARD, seg=6, bevel=0)
    for s in (-1, 1):
        a.part('LMG_bipod', 'Steel').limb((.05, -1.25, zg), (.05 + s * .15, -1.33, zg - .2), .02, .02, bevel=0)
    crate(a, (.35, .3, .03), size=(.5, .26, .22), yaw=.5)
    a.part('Helmet', 'Crate').sphere(.15, loc=(-.4, -.1, .03), seg=10, rings=6, cut=0.0)
    a.part('Helmet_rim', 'Crate').cyl(.17, .02, loc=(-.4, -.1, .035), seg=10, bevel=0)
    a.part('Spade', 'Steel').box((.2, .26, .025), loc=(-.2, .45, .05), rot=(0, 0, .6), bevel=0)
    a.part('Spade_handle', 'LogWood').box((.04, .7, .035), loc=(-.46, .8, .06), rot=(0, 0, .6), bevel=0)


# ----------------------------------------------------------------------------- crater_large
def crater_large(a):
    """Blast crater (7.0 x 7.0 m): a raised, ragged earth lip ring (crest 0.66 m) round a scorched pit whose
    floor is at ground level (0.6 m below the crest); charred ejecta rays streak the outer slope, clods lie
    round it with a twisted fragment and splinters. Faceted, flat shaded. Blocks neither movement nor
    fire."""
    rng = random.Random(81)
    seg = 30
    prof = [(.55, .035), (1.1, .07), (1.6, .17), (1.95, .34), (2.25, .55), (2.5, .66), (2.75, .56), (3.0, .36),
            (3.25, .14), (3.5, -.05)]
    off = Vector((4.1, 2.3, 0))
    verts = [(0.0, 0.0, .03)]
    for i, (r, z) in enumerate(prof):
        for k in range(seg):
            t = (k + (.5 if i % 2 else 0)) * TAU / seg
            c, s = math.cos(t), math.sin(t)
            rr = r if r >= 3.4 else r * (1 + .07 * noise.noise(Vector((c * 1.4, s * 1.4, 3.0)) + off))
            x, y = rr * c, rr * s
            zz = z if r >= 3.4 or r < .5 else z + .07 * noise.noise(Vector((x * 1.2, y * 1.2, 7.0)) + off)
            verts.append((x, y, zz))
    # Materials per quad, so the scorch edge and the ejecta rays follow the rings and spokes instead of
    # zig-zagging triangle by triangle: the pit is scorched out to ring 3 (and ragged into ring 4), and a
    # few rays of charred spoil cross the outer slope.
    faces = [(0, 1 + k, 1 + (k + 1) % seg) for k in range(seg)]
    mats = ['Charred'] * seg
    rays = [rng.randrange(seg) for _ in range(5)]
    for i in range(len(prof) - 1):
        a0, b0 = 1 + i * seg, 1 + (i + 1) * seg
        for k in range(seg):
            k1 = (k + 1) % seg
            if i % 2 == 0:
                quad = [(a0 + k, b0 + k, a0 + k1), (a0 + k1, b0 + k, b0 + k1)]
            else:
                quad = [(a0 + k, b0 + k, b0 + k1), (a0 + k, b0 + k1, a0 + k1)]
            t = (k + .5) * TAU / seg
            scorch = i < 3 or (i == 3 and noise.noise(Vector((math.cos(t) * 2, math.sin(t) * 2, 5.0))) > -.1)
            ray = i >= 6 and any(min((k - q) % seg, (q - k) % seg) <= (1 if i >= 8 else 0) and (k + q) % 3
                                 for q in rays)
            faces += quad
            mats += ['Charred' if scorch or ray else 'Dirt'] * 2
    lookup = {}
    for f, m in zip(faces, mats):
        c = sum((Vector(verts[j]) for j in f), Vector()) / 3
        lookup[round(c.x, 4), round(c.y, 4)] = m
    _split(a, verts, faces, lambda c, n: lookup[round(c.x, 4), round(c.y, 4)], 'Crater')
    clods = a.part('Clods', 'Dirt', flat=True)
    for k in range(12):
        t = rng.uniform(0, TAU)
        r = rng.uniform(2.6, 3.35)
        s = rng.uniform(.12, .26)
        z = max(0.0, .66 - abs(r - 2.5) * .9)
        clods.ico((s, s * .9, s * .6), loc=(r * math.cos(t), r * math.sin(t), z + s * .25), sub=1, jitter=.3,
                  seed=k * 1.9)
    frag = a.part('Fragment', 'Rust')
    frag.limb((1.2, -.6, .06), (1.75, -.35, .22), .16, .03, bevel=0)
    frag.limb((1.75, -.35, .22), (1.95, .05, .12), .12, .03, bevel=0, taper=(.4, 1))
    frag.limb((-2.9, 1.1, .3), (-2.5, 1.5, .45), .1, .025, bevel=0)
    splinters = a.part('Splinters', 'Wood')
    for k in range(3):
        t = rng.uniform(0, TAU)
        r = rng.uniform(2.9, 3.3)
        splinters.box((.07, rng.uniform(.5, .8), .04), loc=(r * math.cos(t), r * math.sin(t), .2),
                      rot=(rng.uniform(-.3, .3), rng.uniform(-.2, .2), t + rng.uniform(-.8, .8)), bevel=0)


# ----------------------------------------------------------------------------- tank_ditch
def tank_ditch(a):
    """Anti-tank ditch segment (4.0 x 10.0 m, 1.4 m): a V-shaped cut whose bottom lies at ground level
    between a low lip on the +X (enemy) side and the steep face of a high spoil bank on the -X side; a line
    of timber pickets with two strands of barbed wire runs along the lip and clods lie on the spoil. Runs
    along Y; ends are cut flush at y = +-5 m with the same profile, so segments line up. Faceted, flat
    shaded. Blocks neither movement nor fire."""
    rng = random.Random(82)
    prof = [(-2.0, -.05), (-1.55, .45), (-1.1, 1.18), (-.8, 1.36), (-.45, 1.28), (.05, .5), (.3, .04), (.52, .04),
            (1.2, .3), (1.6, .46), (2.0, -.05)]
    rows = 21
    off = Vector((1.7, 5.3, 0))
    verts, faces = [], []
    for j in range(rows):
        y = -5.0 + 10.0 * j / (rows - 1)
        fade = min(1.0, (5.0 - abs(y)) / 1.2)
        for x, z in prof:
            if z > .1:
                x += .12 * fade * noise.noise(Vector((x * .7, y * .5, 2.0)) + off)
                z += .1 * fade * noise.noise(Vector((x * .9, y * .9, 6.0)) + off) * min(1.0, z)
            verts.append((x, y, z))
    n = len(prof)
    for j in range(rows - 1):
        for i in range(n - 1):
            p = j * n + i
            faces.append((p, p + 1, p + n + 1, p + n))
    _split(a, verts, faces, lambda c, nrm: 'Charred' if .12 < c.x < .75 else 'Dirt', 'Ditch')      # mud at the bottom
    caps = a.part('Ditch_ends', 'Dirt', flat=True)
    for j, sgn in ((0, -1), (rows - 1, 1)):
        ring = [verts[j * n + i] for i in range(n)]
        caps.mesh(ring, [list(range(n))] if sgn > 0 else [list(range(n))[::-1]])
    clods = a.part('Clods', 'Dirt', flat=True)
    for k in range(8):
        y = rng.uniform(-4.2, 4.2)
        x = rng.uniform(-1.6, -.6)
        s = rng.uniform(.14, .28)
        clods.ico((s, s * .9, s * .6), loc=(x, y, 1.0 + (.3 if -1.1 < x < -.5 else 0)), sub=1, jitter=.3, seed=k * 2.3)
    pickets = a.part('Pickets', 'LogWood')
    for k in range(5):
        y = -4.0 + k * 2.0
        pickets.box((.08, .08, 1.15), loc=(1.62, y, .6), rot=(0, .12, 0), bevel=0)
    wire = a.part('Barbed_wire', 'Steel')
    for z in (.7, 1.05):
        wire.tube([(1.62 + .12 * (z - .6), -5.0, z), (1.62 + .12 * (z - .6), 5.0, z)], .012, seg=3, caps=False)


# ----------------------------------------------------------------------------- camp helpers
def _net(a, rng, x0, x1, y0, y1, height, cells=(16, 12), keep=None, holes=.15, garnish=30, seed=0.0,
         name='Camo_net', mat='Crate', tufts=('FoliageDark', 'Sandbag', 'FoliageDark', 'Dirt')):
    """Camouflage net draped over height(x, y), after mb_siege.camo_net: a sheet of jittered cells with a
    ragged outline (cells failing keep are dropped) and torn holes (a share `holes` of the inner cells is
    left out: alpha cut-outs are not available), dressed with garnish tufts 2-3 cm proud of it. Olive drab
    base with dark green and sand garnish, so it suits every theme. Keep its slopes under ~50 degrees:
    the sheet is single-sided and seen from above."""
    nx, ny = cells
    verts, faces, index = [], [], {}
    off = Vector((seed * 3.7, seed * 1.3, seed * 2.1))

    def z_at(x, y):
        return height(x, y) + .05 * noise.noise(Vector((x * .8, y * .8, 0)) + off)
    for j in range(ny + 1):
        for i in range(nx + 1):
            x = x0 + (x1 - x0) * i / nx
            y = y0 + (y1 - y0) * j / ny
            if 0 < i < nx and 0 < j < ny:
                x += (x1 - x0) / nx * .18 * noise.noise(Vector((x, y, 5.0)) + off)
                y += (y1 - y0) / ny * .18 * noise.noise(Vector((x, y, 9.0)) + off)
            index[i, j] = len(verts)
            verts.append((x, y, z_at(x, y)))
    kept = []
    for j in range(ny):
        for i in range(nx):
            cx = x0 + (x1 - x0) * (i + .5) / nx
            cy = y0 + (y1 - y0) * (j + .5) / ny
            if keep and not keep(cx, cy):
                continue
            if 0 < i < nx - 1 and 0 < j < ny - 1 and rng.random() < holes:
                continue
            faces.append((index[i, j], index[i + 1, j], index[i + 1, j + 1], index[i, j + 1]))
            kept.append((i, j))
    used = sorted({k for f in faces for k in f})
    remap = {k: n for n, k in enumerate(used)}
    a.part(name, mat).mesh([verts[k] for k in used], [tuple(remap[k] for k in f) for f in faces])
    for g in range(garnish if kept else 0):
        i, j = kept[rng.randrange(len(kept))]
        cx = x0 + (x1 - x0) * (i + rng.uniform(.2, .8)) / nx
        cy = y0 + (y1 - y0) * (j + rng.uniform(.2, .8)) / ny
        s = rng.uniform(.22, .4)
        yaw = rng.uniform(0, TAU)
        base = []
        for k in range(4):
            u = yaw + k * R90
            px, py = cx + s * math.cos(u), cy + s * .75 * math.sin(u)
            base.append((px, py, z_at(px, py) + .03))
        top = (cx, cy, z_at(cx, cy) + rng.uniform(.1, .15))
        a.part(f'{name}_garnish', tufts[g % len(tufts)]).mesh(base + [top],
                                                              [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)])


def _drum(a, loc, mat='Crate', lying=None):
    """200-litre drum standing on loc, or lying on its side along yaw `lying`: body, two rolling hoops and
    (standing) a bung on the lid."""
    x, y, z = loc
    body, hoops = a.part('Drums', mat), a.part('Drum_hoops', mat)
    if lying is None:
        body.cyl(.29, .88, loc=(x, y, z + .44), seg=10, bevel=0)
        for h in (.3, .58):
            hoops.cyl(.302, .03, loc=(x, y, z + h), seg=10, bevel=0)
        a.part('Drum_bungs', 'Steel').cyl(.04, .03, loc=(x + .15, y + .05, z + .885), seg=6, bevel=0)
    else:
        d = Vector((math.cos(lying), math.sin(lying), 0))
        rot = (0, R90, lying)
        body.cyl(.29, .88, loc=(x, y, z + .29), rot=rot, seg=10, bevel=0)
        for h in (-.14, .14):
            hoops.cyl(.302, .03, loc=Vector((x, y, z + .29)) + d * h, rot=rot, seg=10, bevel=0)


def _pallet(a, x, y, yaw=0.0, w=1.2, d=1.0):
    """Wooden pallet on the ground (top at 0.14 m); returns its frame."""
    m = _frame((x, y, 0), (0, 0, yaw))
    a.part('Pallets', 'Wood').box((w, d, .06), loc=m @ Vector((0, 0, .11)), rot=(0, 0, yaw), bevel=0)
    for k in (-1, 0, 1):
        a.part('Pallet_skids', 'LogWood').box((w - .04, .12, .1), loc=m @ Vector((0, k * (d / 2 - .08), .04)),
                                              rot=(0, 0, yaw), bevel=0)
    return m


def _tarp_stack(a, m, size):
    """A crate stack under a lashed tarpaulin standing on frame m: a soft box, skirts flaring at the
    bottom and two ropes over the top."""
    w, d, h = size
    yaw = m.to_euler('XYZ').z
    tarp = a.part('Tarp', 'Canvas')
    tarp.box((w + .08, d + .08, h), loc=m @ Vector((0, 0, h / 2)), rot=(0, 0, yaw), bevel=.07, seg=2, taper=(.95, .95))
    for s in (-1, 1):
        tarp.box((w + .02, .03, .32), loc=m @ Vector((0, s * (d / 2 + .08), .15)), rot=(s * .22, 0, yaw), bevel=0)
    rope = a.part('Ropes', 'Rubber')
    for u in (-w / 4, w / 4):
        pts = [(u, -d / 2 - .1, .02), (u, -d / 2 - .04, h * .9), (u, -d / 2 + .1, h + .005), (u, d / 2 - .1, h + .005),
               (u, d / 2 + .04, h * .9), (u, d / 2 + .1, .02)]
        rope.tube([tuple(m @ Vector(p)) for p in pts], .016, seg=4)


def _stripes(a, p0, p1, n, r_w=.05, r_r=.065, first='BarrelRed'):
    """Barrier pole from p0 to p1 in n alternating red and white bands (the red ones 3 cm fatter, so the
    overlapping band ends never share a face)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0) / n
    rot = _along(d)
    for k in range(n):
        red = (k % 2 == 0) == (first == 'BarrelRed')
        c = p0 + d * (k + .5)
        a.part('Barrier_red' if red else 'Barrier_white', 'BarrelRed' if red else 'PlasterWhite').cyl(
            r_r if red else r_w, d.length + (.02 if red else 0), loc=c, rot=rot, seg=8, bevel=0)


# ----------------------------------------------------------------------------- command_tent
def command_tent(a):
    """Command post tent (6.0 x 5.0 m, 5.8 m to the mast tip): a ridge tent in canvas with olive straps, its
    front curtain rolled up under a flat awning on poles, a door at the +X end and a window and stove pipe
    at the -X end, and a torn camouflage net over the roof. Under the awning: a table of radio sets with
    dials, lamps, handsets and a whip antenna, a map board on an easel and two folding chairs; outside: a
    telescopic antenna mast on guys, a generator and jerrycans, guy ropes and pegs. Blocks movement and
    fire (the tent)."""
    rng = random.Random(91)
    canvas = a.part('Tent', 'Canvas')
    y0, y1, eave, ridge, yr = -.5, 2.1, 1.3, 2.4, .8
    canvas.prism([(y0, -.02), (y1, -.02), (y1 - .12, eave), (yr, ridge), (y0 + .12, eave)], 4.0, axis='X', bevel=.04,
                 seg=1)

    def roof(y):
        return eave + (ridge - eave) * (1 - min(1.0, abs(y - yr) / (yr - y0 - .12)))
    straps = a.part('Straps', 'Crate')
    nf = Vector((0, -(ridge - eave), yr - y0 - .12)).normalized()
    nb = Vector((0, ridge - eave, yr - y0 - .12)).normalized()
    nw = Vector((0, 1.32, .12)).normalized()
    for x in (-1.33, 0.0, 1.33):
        straps.limb(tuple(Vector((x, y0 + .12, eave)) + nf * .012), tuple(Vector((x, yr, ridge)) + nf * .012), .12,
                    .025, bevel=0)
        straps.limb(tuple(Vector((x, y1 - .12, eave)) + nb * .012), tuple(Vector((x, yr, ridge)) + nb * .012), .12,
                    .025, bevel=0)
        straps.limb(tuple(Vector((x, y1, -.02)) + nw * .012), tuple(Vector((x, y1 - .12, eave)) + nw * .012), .12, .025,
                    bevel=0)
    straps.box((4.06, .2, .06), loc=(0, yr, ridge - .01), bevel=0)
    dark = a.part('Openings', 'Undercarriage')
    tilt = math.atan2(.12, 1.32)
    dark.box((3.5, .03, 1.1), loc=(0, y0 + .12 * .67 / 1.32 - .004, .65), rot=(-tilt, 0, 0), bevel=0)   # curtain up
    canvas.cyl(.1, 3.6, loc=(0, y0 + .03, eave - .06), rot=ACROSS, seg=8, bevel=0)
    dark.box((.03, .9, 1.6), loc=(2.005, yr, .8), bevel=0)                                    # +X door
    for s in (-1, 1):
        canvas.box((.04, .35, 1.65), loc=(2.06, yr + s * .6, .8), rot=(0, 0, s * .5), bevel=0)
    dark.box((.03, .6, .42), loc=(-2.005, yr, 1.55), bevel=0)                                 # -X window
    canvas.cyl(.06, .7, loc=(-2.04, yr, 1.8), rot=FORWARD, seg=6, bevel=0)
    steel = a.part('Steel', 'Steel')
    steel.cyl(.07, 1.3, loc=(-1.4, 1.5, roof(1.5) + .5), seg=8, bevel=0)                         # stove pipe
    steel.cyl(.13, .06, loc=(-1.4, 1.5, roof(1.5) + 1.17), seg=8, bevel=0)
    # Awning on two poles, with a valance and guy ropes.
    rings = []
    for k in range(5):
        t = k / 4
        y = .1 + (-1.95 - .1) * t
        z = (roof(.1) + .02) * (1 - t) + 1.8 * t - .07 * math.sin(math.pi * t)
        rings.append([(-1.95, y, z - .015), (1.95, y, z - .015), (1.95, y, z + .015), (-1.95, y, z + .015)])
    canvas.loft(rings)
    canvas.box((3.9, .02, .2), loc=(0, -1.965, 1.7), bevel=0)
    wood = a.part('Poles', 'Wood')
    rope = a.part('Guy_ropes', 'Rubber')
    pegs = []
    for s in (-1, 1):
        wood.cyl(.04, 1.8, loc=(s * 1.85, -1.9, .9), seg=6, bevel=0)
        rope.tube([(s * 1.85, -1.9, 1.75), (s * 2.3, -2.42, .02)], .012, seg=3)
        pegs.append((s * 2.3, -2.42))
        rope.tube([(s * 2.0, yr, ridge - .05), (s * 2.9, yr, .02)], .012, seg=3)
        pegs.append((s * 2.9, yr))
        rope.tube([(s * 1.3, y1 - .1, eave), (s * 1.3, 2.45, .02)], .012, seg=3)
        pegs.append((s * 1.3, 2.45))
    for x, y in pegs:
        steel.box((.04, .04, .16), loc=(x, y, .05), rot=(.2, 0, 0), bevel=0)

    # Torn net over the roof.
    def drape(x, y):
        zr = roof(y) if y0 + .12 <= y <= y1 - .12 else eave - (y - (y1 - .12)) * 1.1
        return zr + .1 - max(0.0, abs(x) - 1.95) * 1.3
    _net(a, rng, -2.3, 2.3, .25, 2.5, drape, cells=(12, 7), holes=.14, garnish=26, seed=5.0,
         keep=lambda x, y: abs(x) < 2.25 - .2 * (1 + noise.noise(Vector((x, y, 3.0)))) and
         y < 2.45 - .15 * (1 + noise.noise(Vector((x * 1.5, 0, 4.0)))))
    # Radio table, map board, chairs.
    zt = .74
    a.part('Table', 'Wood').box((1.8, .75, .05), loc=(-.2, -1.05, zt), bevel=0)
    for sx in (-.85, .85):
        for sy in (-.32, .32):
            steel.box((.04, .04, zt - .02), loc=(-.2 + sx, -1.05 + sy, (zt - .02) / 2), bevel=0)
    for i, (x, w, h) in enumerate(((-.8, .42, .3), (-.28, .45, .26), (.3, .5, .34))):
        a.part('Radios', 'Crate').box((w, .32, h), loc=(x, -.95, zt + .025 + h / 2), bevel=.015, seg=1)
        a.part('Radio_panels', 'Armor').box((w - .06, .02, h - .08), loc=(x, -1.115, zt + .025 + h / 2), bevel=0)
        for k in range(2 + i % 2):
            a.part('Dials', 'Glass').box((.06, .02, .05), loc=(x - w / 2 + .1 + k * .1, -1.13, zt + .025 + h * .62),
                                         bevel=0)
        a.part('Radio_lamps', 'Lamp').box((.03, .02, .03), loc=(x + w / 2 - .08, -1.13, zt + .025 + h * .35), bevel=0)
    a.part('Handsets', 'Rubber').box((.2, .07, .06), loc=(-.45, -1.28, zt + .055), rot=(0, 0, .3), bevel=0)
    steel.cyl(.01, 1.4, loc=(.45, -.9, zt + .025 + .34 + .7), seg=4, bevel=0)                    # whip antenna
    rope.tube([(.3, -.8, zt + .1), (.5, -.62, .02), (1.6, -1.2, .02), (2.2, -1.6, .02)], .018, seg=4)
    board = _frame((-1.55, -1.3, 0), (0, 0, .35))
    for sx in (-.3, .3):
        wood.limb(tuple(board @ Vector((sx, 0, 0))), tuple(board @ Vector((sx * .6, .12, 1.55))), .04, .04, bevel=0)
    wood.limb(tuple(board @ Vector((0, .5, 0))), tuple(board @ Vector((0, .14, 1.45))), .04, .04, bevel=0)
    bm = board @ _frame((0, .06, 1.15), (-.14, 0, 0))
    _box_on(a.part('Map_board', 'Medical'), bm, (.9, .03, .62))
    for off, mat in (((-.2, .08), 'BarrelRed'), ((.15, -.1), 'ContainerBlue'), ((.25, .15), 'BarrelRed')):
        _box_on(a.part('Map_marks', mat), bm, (.08, .02, .08), off=(off[0], -.024, off[1]))
    for x, yaw in ((-.75, .15), (.35, -.2)):
        cm = _frame((x, -1.65, 0), (0, 0, yaw))
        _box_on(canvas, cm, (.44, .4, .04), off=(0, 0, .45))
        _box_on(canvas, cm, (.44, .04, .3), off=(0, .2, .75))
        for sx in (-.2, .2):
            steel.limb(tuple(cm @ Vector((sx, -.18, 0))), tuple(cm @ Vector((sx, .2, .9))), .025, .025, bevel=0)
            steel.limb(tuple(cm @ Vector((sx, .18, 0))), tuple(cm @ Vector((sx, -.18, .45))), .025, .025, bevel=0)
    # Telescopic antenna mast on guys.
    mx, my = 2.25, -1.65
    for k, (r, h, z) in enumerate(((.05, 2.0, 0.0), (.038, 2.0, 1.9), (.028, 1.8, 3.8))):
        steel.cyl(r, h, loc=(mx, my, z + h / 2), seg=6, bevel=0)
    steel.limb((mx - .55, my, 5.55), (mx + .55, my, 5.55), .03, .03, bevel=0)
    steel.limb((mx, my - .55, 5.35), (mx, my + .55, 5.35), .025, .025, bevel=0)
    for k in range(3):
        t = k * TAU / 3 + .4
        px, py = mx + .68 * math.cos(t), my + .68 * math.sin(t)
        rope.tube([(mx, my, 4.2), (px, py, .02)], .008, seg=3)
        steel.box((.04, .04, .14), loc=(px, py, .05), bevel=0)
    generator(a, (-2.3, -1.85, 0), yaw=.1, size=(1.1, .6, .75), body='Crate', door='Armor')
    rope.tube([(-1.7, -1.8, .3), (-1.5, -1.5, .02), (-1.3, -.7, .02), (-1.1, -.52, .1)], .018, seg=4)
    _jerrycans(a, (-2.55, -.95, 0), 2, axis='x')


# ----------------------------------------------------------------------------- camo_net
def camo_net(a):
    """Camouflage net on poles over a supply cache (8.0 x 6.0 m, 2.8 m): a khaki net with dark green and
    sand garnish sags between six poles with spreaders (four corner poles on guy ropes, two taller centre
    poles), its edges hanging lower; it is torn, with holes and a ragged outline (modelled, not alpha).
    Under it: pallets of crates, a stack of long boxes, a tarp-covered stack, drums and jerrycans. Blocks
    neither movement nor fire (it can be driven through)."""
    rng = random.Random(92)
    poles = [(-3.4, -2.4, 2.0), (3.4, -2.4, 2.0), (-3.4, 2.4, 2.0), (3.4, 2.4, 2.0), (0.0, -1.1, 2.75),
             (0.0, 1.1, 2.75)]
    wood = a.part('Poles', 'Wood')
    rope = a.part('Guy_ropes', 'Rubber')
    for k, (x, y, h) in enumerate(poles):
        wood.cyl(.05, h, loc=(x, y, h / 2 - .02), seg=6, bevel=0)
        a.part('Spreaders', 'LogWood').box((.5, .05, .05), loc=(x, y, h - .08), rot=(0, 0, k * .7), bevel=0)
        if k < 4:
            sx, sy = (1 if x > 0 else -1), (1 if y > 0 else -1)
            rope.tube([(x, y, h - .15), (x + sx * .45, y + sy * .45, .02)], .012, seg=3)
            a.part('Pegs', 'Steel').box((.04, .04, .15), loc=(x + sx * .45, y + sy * .45, .05), bevel=0)

    def drape(x, y):
        z = max(h - .42 * math.hypot(x - px, y - py) for px, py, h in poles)
        return max(z, 1.25) - max(0.0, abs(x) - 3.4) * 1.1 - max(0.0, abs(y) - 2.4) * 1.1
    _net(a, rng, -3.95, 3.95, -2.95, 2.95, drape, cells=(16, 12), holes=.22, garnish=40, seed=3.0,
         keep=lambda x, y: (abs(x) / 3.95) ** 4 + (abs(y) / 2.95) ** 4 < .9 + .12 * noise.noise(Vector((x, y, 2.0))))
    z = .14
    m = _pallet(a, -1.8, -.7, .06)
    for j in (-.26, .26):
        crate(a, tuple(m @ Vector((0, j, z))), size=(1.1, .48, .36), yaw=.06)
    for i in (-.27, .27):
        crate(a, tuple(m @ Vector((i, 0, z + .36))), size=(.98, .48, .34), yaw=.06 + R90, band=i < 0)
    m = _pallet(a, 1.7, .9, -.08, w=1.3, d=.9)
    for layer in range(3):
        for k in range(3):
            crate(a, tuple(m @ Vector((.05 * (layer % 2), (k - 1) * .31 + .02 * (layer % 2), z + layer * .26))),
                  size=(1.25, .28, .26),
                  yaw=-.08,
                  band=(k + layer) % 3 == 1)
    _tarp_stack(a, _frame((-.9, 1.3, 0), (0, 0, -.1)), (1.2, .9, 1.0))
    for x, y, mat in ((1.2, -1.3, 'Crate'), (1.82, -1.15, 'Crate'), (1.55, -1.85, 'BarrelRed'), (2.45, -1.5, 'Crate')):
        _drum(a, (x, y, 0), mat)
    _drum(a, (.4, -.6, 0), 'Fuel', lying=.4)
    _jerrycans(a, (-.2, .5, 0), 3, axis='x')
    crate(a, (.45, 1.6, 0), size=(1.3, .8, .62), yaw=.05)


# ----------------------------------------------------------------------------- supply_pile
def supply_pile(a):
    """Supply dump (4.0 x 3.0 m, 1.3 m): a pallet stack under a lashed tarpaulin, a pallet of ammunition
    crates two layers high with one more crate thrown on top, fuel drums standing and one lying, a row of
    jerrycans and an open box of shells. Blocks movement and fire (low: tanks can fire over it)."""
    z = .14
    m = _pallet(a, -1.3, .65, .05, w=1.3, d=1.1)
    _tarp_stack(a, m @ _frame((0, 0, z), (0, 0, 0)), (1.25, 1.05, .95))
    m = _pallet(a, .3, .75, -.06)
    for j in (-.26, .26):
        crate(a, tuple(m @ Vector((0, j, z))), size=(1.1, .48, .36), yaw=-.06)
    for i in (-.27, .27):
        crate(a, tuple(m @ Vector((i, 0, z + .36))), size=(.98, .48, .34), yaw=-.06 + R90, band=i > 0)
    crate(a, tuple(m @ Vector((.05, .02, z + .7))), size=(.7, .38, .3), yaw=.35)
    for x, y, mat in ((1.65, .95, 'Crate'), (1.65, .3, 'BarrelRed'), (1.1, -.2, 'Crate')):
        _drum(a, (x, y, 0), mat)
    _drum(a, (.35, -.95, 0), 'Crate', lying=.25)
    _jerrycans(a, (-1.4, -.85, 0), 4, axis='x')
    box = _frame((1.35, -.95, 0), (0, 0, -.3))
    a.part('Shell_box', 'Wood').shell([(-.42, -.22), (.42, -.22), (.42, .22), (-.42, .22)], .28, .03,
                                      loc=box.to_translation(), rot=(0, 0, -.3), floor=.03)
    shells(a, tuple(box @ Vector((0, 0, .03))), 4, 2, r=.07, h=.5, pitch=.19, yaw=-.3)
    a.part('Shell_box_lid', 'Wood').box((.86, .46, .03), loc=box @ Vector((0, -.5, .05)), rot=(.06, 0, -.3), bevel=0)


# ----------------------------------------------------------------------------- fuel_bladder
def fuel_bladder(a):
    """Collapsible fuel bladder (5.0 x 3.0 m, 0.8 m): a rubberised olive pillow in a spill liner with a low
    wall, carry handles along its sides, fill and vent fittings on top and a coupling with a red valve at
    the +X end; a hose runs to a pump skid (engine, pump, filters, manifold with valves, control box with a
    lamp, exhaust), and a dispensing hose with a nozzle lies coiled on the ground. Hazard sign and fire
    extinguisher. Blocks movement, not fire."""
    cx, L, W, H = -.45, 3.9, 1.15, .72
    rings = []
    for u in (-1.0, -.93, -.72, -.38, 0.0, .38, .72, .93, 1.0):
        s = (1 - abs(u) ** 6) ** .5 if abs(u) < 1 else .0
        w = W * (.82 + .18 * s)
        h = max(.07, H * s ** .6)
        prof = [(w, -.03), (w, h * .35), (w * .95, h * .72), (w * .78, h * .95), (w * .4, h), (-w * .4, h),
                (-w * .78, h * .95), (-w * .95, h * .72), (-w, h * .35), (-w, -.03)]
        rings.append([(cx + u * L / 2, y, z) for y, z in prof])
    a.part('Bladder', 'Crate').loft(rings)
    liner = a.part('Liner', 'Canvas')
    lx0, lx1, ly = -2.5, 1.6, 1.45
    liner.box((lx1 - lx0 - .1, 2 * ly - .1, .03), loc=((lx0 + lx1) / 2, 0, .0), bevel=0)
    liner.shell([(lx0, -ly), (lx1, -ly), (lx1, ly), (lx0, ly)], .2, .08, bevel=.02, seg=1)
    rub = a.part('Fittings', 'Rubber')
    for s in (-1, 1):
        for x in (-1.7, -.9, .0, .8):
            rub.tube([(cx + x + .45 - .12, s * (W + .02), .2), (cx + x + .45 - .1, s * (W + .1), .26),
                      (cx + x + .45 + .1, s * (W + .1), .26), (cx + x + .45 + .12, s * (W + .02), .2)], .02, seg=4)
    steel = a.part('Steel', 'Steel')
    for x, y in ((-1.4, .3), (.2, -.35)):
        steel.cyl(.12, .14, loc=(x, y, H - .01), seg=8, bevel=0)
        steel.cyl(.07, .1, loc=(x, y, H + .1), seg=6, bevel=0)
    xe = cx + L / 2
    steel.cyl(.1, .3, loc=(xe + .08, 0, .22), rot=ACROSS, seg=8, bevel=0)                         # coupling
    a.part('Valves', 'BarrelRed').torus(.12, .02, loc=(xe + .2, 0, .42), seg=10, ring=3)
    steel.cyl(.02, .2, loc=(xe + .2, 0, .32), seg=4, bevel=0)
    a.part('Hoses', 'Rubber').tube([(xe + .22, 0, .22), (1.84, -.05, .12), (1.88, -.2, .16), (1.95, -.2, .3)], .06,
                                   seg=6)
    # Pump skid.
    px = 2.1
    a.part('Skid', 'Undercarriage').box((.75, 1.2, .12), loc=(px, 0, .06), bevel=.02, seg=1)
    a.part('Engine', 'Crate').box((.55, .5, .45), loc=(px, .3, .345), bevel=.03, seg=1)
    a.part('Engine_grille', 'Undercarriage').grille(.35, .3, loc=(px, .56, .36), rot=(0, 0, math.pi), slats=3,
                                                   depth=.04, thickness=.03)
    steel.cyl(.17, .22, loc=(px, -.2, .3), rot=FORWARD, seg=10, bevel=.02, bseg=1)                 # pump volute
    for k in range(2):
        steel.cyl(.07, .35, loc=(px + .2, -.42 + k * .17, .3), seg=8, bevel=0)                      # filters
    a.part('Manifold', 'Pipe').tube([(px - .2, -.45, .25), (px - .2, -.2, .25), (px - .05, -.2, .25)], .045, seg=6)
    a.part('Valves', 'BarrelRed').torus(.07, .015, loc=(px - .2, -.36, .33), seg=8, ring=3)
    a.part('Control_box', 'Armor').box((.25, .12, .34), loc=(px - .22, .42, .42), bevel=.02, seg=1)
    a.part('Control_lamp', 'Lamp').box((.05, .02, .05), loc=(px - .22, .35, .5), bevel=0)
    steel.cyl(.03, .4, loc=(px + .15, .45, .75), seg=5, bevel=0)                                   # exhaust
    a.part('Hoses', 'Rubber').tube([(px - .1, -.55, .2), (1.95, -.8, .05), (2.3, -1.0, .05), (2.28, -1.36, .05),
                                    (1.85, -1.32, .05), (1.78, -1.05, .05)], .045, seg=5)
    steel.cyl(.035, .3, loc=(1.9, -.98, .06), rot=(0, R90, .5), seg=6, bevel=0)                  # nozzle
    hazard_sign(a, (2.3, .95, 0), size=.45, height=1.0)
    a.part('Extinguisher', 'BarrelRed').cyl(.09, .5, loc=(1.9, 1.25, .26), seg=8, bevel=.02, bseg=1)
    a.part('Extinguisher_stand', 'Armor').box((.28, .06, .55), loc=(1.9, 1.35, .275), bevel=0)


# ----------------------------------------------------------------------------- checkpoint
def checkpoint(a):
    """Road checkpoint (6.0 x 4.0 m, 2.4 m): the road runs along Y through it. A sandbag guard booth (three
    courses on the +X side, door at the back) with log corner posts, a corrugated roof held down by
    sandbags and a floodlight; a red and white barrier arm across the road from a post with a
    counterweight to a forked rest; staggered concrete blocks forming a chicane; a red stop board on two
    posts, a burning-drum stove and a field telephone. Blocks movement and fire (the booth)."""
    rng = random.Random(95)
    bx, by, hw = 2.1, .6, .82
    bags = a.part('Sandbags', 'Sandbag')
    size = (.62, .34, .24)
    courses = 5
    for k in range(courses):
        z = .12 - .01 + k * .215
        half = k % 2 == 1
        bag_run(bags, rng, (bx - hw, by - hw), (bx + hw, by - hw), z, size, half=half)
        bag_run(bags, rng, (bx + hw, by - hw + .17), (bx + hw, by + hw), z, size, half=not half)
        bag_run(bags, rng, (bx - hw, by + hw), (bx - hw, by - hw + .17), z, size, half=not half)
        bag_run(bags, rng, (bx + hw - .17, by + hw), (bx + .15, by + hw), z, size, half=half)
    wood = a.part('Posts', 'LogWood')
    for sx in (-1, 1):
        for sy in (-1, 1):
            wood.box((.1, .1, 2.15), loc=(bx + sx * (hw - .02), by + sy * (hw - .02), 1.07), bevel=0)
    a.part('Roof', 'Corrugated').box((2.0, 2.0, .05), loc=(bx, by, 2.17), rot=(.06, 0, 0), bevel=0)
    for x, y in ((-.55, -.5), (.5, .55), (-.4, .6)):
        bag_run(a.part('Roof_bags', 'Sandbag'), rng, (bx + x - .3, by + y), (bx + x + .3, by + y), 2.17 + .12 - y * .06,
                size)
    a.part('Floodlight', 'Armor').box((.3, .2, .22), loc=(bx - hw + .05, by - hw - .05, 2.0), rot=(.4, 0, .5), bevel=0)
    a.part('Floodlight_lens', 'Lamp').box((.24, .03, .16), loc=(bx - hw + .005, by - hw - .135, 1.97),
                                          rot=(.4, 0, .5), bevel=0)
    a.part('Telephone', 'Crate').box((.26, .18, .16), loc=(bx + .2, by - hw, .11 + (courses - 1) * .215 + .19), bevel=0)
    # Barrier arm across the road (lowered) with a counterweight and a forked rest.
    post = a.part('Barrier_post', 'Concrete')
    post.box((.35, .35, 1.0), loc=(1.1, -.55, .5), bevel=.03, seg=1)
    a.part('Hinge', 'Steel').cyl(.09, .5, loc=(1.1, -.55, 1.05), rot=FORWARD, seg=8, bevel=0)
    _stripes(a, (1.1, -.75, 1.05), (-2.55, -.75, 1.05), 8)
    a.part('Counterweight', 'Concrete').box((.45, .3, .3), loc=(1.55, -.75, 1.05), bevel=.02, seg=1)
    a.part('Barrier_steel', 'Steel').cyl(.04, .5, loc=(1.33, -.75, 1.05), rot=ACROSS, seg=6, bevel=0)
    rest = a.part('Rest', 'Steel')
    rest.box((.08, .08, .95), loc=(-2.4, -.75, .47), bevel=0)
    for s in (-1, 1):
        rest.box((.04, .04, .22), loc=(-2.4, -.75 + s * .1, 1.03), bevel=0)
    rest.box((.1, .28, .04), loc=(-2.4, -.75, .94), bevel=0)
    # Concrete chicane.
    conc = a.part('Blocks', 'Concrete')
    for x, y, yaw in ((-1.95, -1.65, .04), (.15, -1.7, -.06), (-1.0, 1.55, .08)):
        conc.box((1.3, .6, .8), loc=(x, y, .4), rot=(0, 0, yaw), bevel=.05, seg=1, taper=(.8, .92))
        m = _frame((x, y, .8), (0, 0, yaw))
        for s in (-.35, .35):
            a.part('Lifting_eyes', 'Rust').tube([tuple(m @ Vector((s - .08, 0, -.02))),
                                                 tuple(m @ Vector((s - .06, 0, .1))),
                                                 tuple(m @ Vector((s + .06, 0, .1))),
                                                 tuple(m @ Vector((s + .08, 0, -.02)))],
                                                .02, seg=4)
    # Stop board, drum stove.
    for sx in (-.4, .4):
        a.part('Sign_posts', 'Steel').box((.06, .06, 1.7), loc=(-2.55 + sx, -1.85 + .04, .85), bevel=0)
    a.part('Sign', 'BarrelRed').box((1.1, .05, .6), loc=(-2.55, -1.86, 1.45), bevel=.01, seg=1)
    a.part('Sign_band', 'PlasterWhite').box((.85, .03, .16), loc=(-2.55, -1.895, 1.45), bevel=0)
    _drum(a, (2.55, -1.4, 0), 'Rust')
    a.part('Embers', 'LavaGlow').cyl(.26, .03, loc=(2.55, -1.4, .87), seg=10, bevel=0)
    a.part('Stove_grill', 'Charred').cyl(.27, .04, loc=(2.55, -1.4, .9), seg=10, bevel=0)


# ----------------------------------------------------------------------------- barricade
def barricade(a):
    """Street barricade (6.0 x 1.8 m, 1.4 m) along X, facing -Y: a stack of car tyres and two tyres leaning
    on it, a burnt car door propped against planks nailed across, a double row of sandbags with a third
    course and a coil of barbed wire along the top, a drum on its side, a bent steel bed frame and brick
    rubble at the foot. Blocks movement and fire."""
    rng = random.Random(96)
    tyres = a.part('Tyres', 'Rubber')
    for k in range(3):
        tyres.torus(.3, .12, loc=(-2.35 + k * .02, .1 - k * .03, .12 + k * .235), rot=(0, 0, k), seg=10, ring=4)
    tyres.torus(.3, .12, loc=(-1.85, -.38, .38), rot=(1.2, .1, .3), seg=10, ring=4)
    tyres.torus(.3, .12, loc=(-2.8, -.35, .36), rot=(1.1, -.2, -.4), seg=10, ring=4)
    # Planks nailed across between the tyres and the sandbags.
    planks = a.part('Planks', 'Wood')
    for p0, p1 in (((-2.0, .25, .05), (-.4, .2, 1.05)), ((-2.0, .3, 1.0), (-.35, .28, .1)),
                      ((-1.9, .38, .55), (-.3, .36, .62)), ((-1.2, .5, .05), (-1.0, .5, 1.25))):
        planks.limb(p0, p1, .2, .04, bevel=0)
    a.part('Planks_dark', 'LogWood').limb((-.6, .45, .05), (-.25, .1, 1.1), .14, .05, bevel=0)
    # Burnt car door propped against the planks.
    m = _frame((-1.15, -.05, 0), (-.32, 0, .08))
    door = a.part('Door', 'Charred')
    _box_on(door, m, (1.05, .06, .52), off=(0, 0, .28))
    _box_on(door, m, (1.0, .08, .06), off=(-.02, 0, .95))
    _box_on(door, m, (.06, .045, .41), off=(.5, 0, .75))
    door.limb(tuple(m @ Vector((-.5, 0, .52))), tuple(m @ Vector((-.28, 0, .96))), .06, .04, bevel=0)
    _box_on(a.part('Door_rust', 'Rust'), m, (.5, .03, .28), off=(.15, -.035, .3))
    _box_on(a.part('Door_handle', 'Steel'), m, (.14, .04, .03), off=(.35, -.05, .45))
    # Sandbags.
    bags = a.part('Sandbags', 'Sandbag')
    size = (.68, .36, .24)
    for k, (ys, z) in enumerate((((-.2, .2), .11), ((-.2, .2), .325), ((0.0,), .54))):
        for y in ys:
            bag_run(bags, rng, (-.2, y), (2.95, y), z, size, half=(k % 2 == 1) ^ (y > 0))
    coil(a.part('Barbed_wire', 'Steel'), .1, 2.8, 0, .9, .26, pitch=.3, pts=6, wire=.012)
    _drum(a, (1.3, -.62, 0), 'Rust', lying=.15)
    frame = a.part('Bed_frame', 'Steel')
    fm = _frame((.3, .62, 0), (-.25, 0, -.05))
    for s in (-1, 1):
        frame.limb(tuple(fm @ Vector((s * .45, 0, 0))), tuple(fm @ Vector((s * .45, 0, 1.25))), .04, .04, bevel=0)
    for zz in (.25, .6, .95, 1.22):
        frame.limb(tuple(fm @ Vector((-.47, 0, zz))), tuple(fm @ Vector((.47, 0, zz + (.05 if zz > 1 else 0)))), .03,
                   .03, bevel=0)
    _chunks([a.part('Bricks', 'Brick', flat=True), a.part('Rubble', 'Concrete', flat=True)], rng, 2.3, -.5, .35, .2,
            6, size=(.1, .2), seed=3.0)


# ----------------------------------------------------------------------------- power_pylon
def _arm(part, s, zb, zt, body_b, body_t, tip, lace=2):
    """Pylon cross-arm on side s: two bottom chords from the body corners at zb and two top chords from the
    body corners at zt, all meeting at the tip x = s * tip, with laced side and bottom faces."""
    t = Vector((s * tip, 0, zb + .05))
    b = [Vector((s * body_b, y, zb)) for y in (-body_b, body_b)]
    u = [Vector((s * body_t, y, zt)) for y in (-body_t, body_t)]
    for p in b:
        part.limb(tuple(p), tuple(t), .08, .08, bevel=0)
    for p in u:
        part.limb(tuple(p), tuple(t), .065, .065, bevel=0)
    for k in range(1, lace + 1):
        f0, f1 = (k - 1) / (lace + .6), k / (lace + .6)
        for i in (0, 1):
            part.limb(tuple(b[i].lerp(t, f0)), tuple(u[i].lerp(t, f1)), .04, .04, bevel=0)
        part.limb(tuple(b[0].lerp(t, f1)), tuple(b[1].lerp(t, (f0 + f1) / 2)), .035, .035, bevel=0)


def _insulator_string(a, top, discs=4, pitch=.2, r=.13):
    """Suspension insulator string hanging from `top`: a steel link, porcelain discs and a line clamp.
    Returns the clamp point where the conductor leaves."""
    x, y, z = top
    steel = a.part('Fittings', 'Steel')
    steel.box((.06, .06, .18), loc=(x, y, z - .08), bevel=0)
    length = discs * pitch + .1
    steel.cyl(.025, length, loc=(x, y, z - .15 - length / 2), seg=4, bevel=0)
    for k in range(discs):
        a.part('Insulators', 'Medical').cyl(r, .05, loc=(x, y, z - .25 - k * pitch), seg=8, bevel=0)
    zc = z - .2 - length
    steel.box((.1, .22, .08), loc=(x, y, zc), bevel=0)
    return Vector((x, y, zc))


def _stubs(a, p, length=1.9, sag=.25, name='Wires'):
    """Conductor stubs leaving point p both ways along Y, sagging towards the next pylon."""
    part = a.part(name, 'Undercarriage')
    for s in (-1, 1):
        part.tube([tuple(p), (p.x, p.y + s * length * .5, p.z - sag * .75), (p.x, p.y + s * length, p.z - sag)], .022,
                  seg=3)


def power_pylon(a):
    """Steel lattice transmission pylon (4.0 x 4.0 m base, 14 m): four legs on concrete footings taper to a
    waist at 9 m and a straight top section; two tiers of laced cross-arms (4.4 m and 3.4 m) carry
    porcelain insulator strings, an earth-wire peak tops it, and every conductor leaves as a sagging stub
    both ways along Y towards the next pylon. Members are square flat struts (the lattice helper staggers
    their sections so none share a face plane). An anti-climb band and a danger plate at the foot. Blocks
    movement and fire at its base (the legs); wires and arms block nothing."""
    steel = a.part('Lattice', 'MetalSheet')
    for sx in (-1, 1):
        for sy in (-1, 1):
            a.part('Footings', 'Concrete').box((.62, .62, .5), loc=(sx * 1.75, sy * 1.75, .2), bevel=.03, seg=1,
                                               taper=(.85, .85))
    lattice(steel, 0, 0, .42, 9.0, 1.75, .52, 6, leg=.16, brace=.05)
    lattice(steel, 0, 0, 9.0, 13.0, .52, .38, 3, leg=.14, brace=.045)
    for sx in (-1, 1):
        for sy in (-1, 1):
            steel.limb((sx * .38, sy * .38, 12.98), (sx * .06, sy * .06, 13.9), .08, .08, bevel=0)
    steel.box((.2, .2, .12), loc=(0, 0, 13.9), bevel=0)

    def half(z0, z1, zz):
        return z0[1] + (z1[1] - z0[1]) * (zz - z0[0]) / (z1[0] - z0[0])
    for s in (-1, 1):
        _arm(steel, s, 9.0, 10.0, .52, half((9.0, .52), (13.0, .38), 10.0), 2.2)
        _arm(steel, s, 11.6, 12.5, half((9.0, .52), (13.0, .38), 11.6), half((9.0, .52), (13.0, .38), 12.5), 1.7)
        for tip, z in ((2.14, 9.0), (1.64, 11.6)):
            _stubs(a, _insulator_string(a, (s * tip, 0, z)))
    _stubs(a, Vector((0, 0, 13.95)), sag=.15, name='Earth_wire')
    guard = a.part('Anti_climb', 'Steel')
    zg, hw = 3.1, 1.75 + (.52 - 1.75) * (3.1 - .42) / (9.0 - .42)
    for sx in (-1, 1):
        for sy in (-1, 1):
            for k in range(3):
                guard.limb((sx * hw, sy * hw, zg), (sx * (hw + .3), sy * (hw + .3 - k * .15), zg + .25), .025, .025,
                           bevel=0)
    plate = _basis((0, -hw - .05, 2.3), (1, 0, 0), (0, -1, 0))
    _box_on(a.part('Danger_plate', 'Hazard'), plate, (.4, .5, .03), off=(0, 0, .0))
    _box_on(a.part('Danger_mark', 'Charred'), plate, (.08, .26, .02), off=(0, .03, .02))
    _box_on(a.part('Danger_mark', 'Charred'), plate, (.2, .05, .02), off=(0, -.14, .02))


# ----------------------------------------------------------------------------- telegraph_pole
def telegraph_pole(a):
    """Wooden telegraph pole (0.6 x 0.6 m at the ground, 7.3 m): a tapered log pole in an earth collar with a
    capped top, two cross-arms on steel braces carrying porcelain insulators whose wire stubs sag away
    along Y, step bolts and a number plate, and a leaning stay wire with a stay insulator and a yellow guard
    to a concrete anchor 1.7 m off along -X. Blocks neither movement nor fire."""
    lean = (.015, -.02, 0)
    wood = a.part('Pole', 'LogWood')
    wood.cyl(.14, 7.25, loc=(0, 0, 3.6), r2=.11, rot=lean, seg=8, bevel=0)
    m = _frame((0, 0, 0), lean)
    a.part('Collar', 'Dirt', flat=True).ico((.3, .3, .12), loc=(0, 0, .02), sub=1, jitter=.25, seed=2.0)
    _box_on(a.part('Cap', 'Steel'), m, (.26, .26, .05), off=(0, 0, 7.24))
    arms = a.part('Cross_arms', 'Wood')
    braces = a.part('Braces', 'Steel')
    insul = a.part('Insulators', 'Medical')
    for z, half, n in ((6.75, .8, 4), (6.25, .55, 2)):
        _box_on(arms, m, (2 * half, .1, .1), off=(0, -.14, z))
        for s in (-1, 1):
            braces.limb(tuple(m @ Vector((s * half * .6, -.14, z - .05))), tuple(m @ Vector((0, -.12, z - .55))), .04,
                        .012,
                        bevel=0)
        xs = [-half + .08 + (2 * half - .16) * k / (n - 1) for k in range(n)]
        for x in xs:
            p = m @ Vector((x, -.14, z + .05))
            a.part('Pins', 'Steel').cyl(.015, .12, loc=(p.x, p.y, p.z + .05), seg=4, bevel=0)
            insul.lathe([(.05, 0), (.06, .035), (.045, .08), (.02, .11)], loc=(p.x, p.y, p.z + .07), seg=6)
            _stubs(a, Vector((p.x, p.y, p.z + .15)), length=1.1, sag=.12)
    steps = a.part('Step_bolts', 'Steel')
    for k in range(8):
        z = 2.4 + k * .45
        ang = (k % 2) * math.pi
        p = m @ Vector((math.cos(ang) * .12, math.sin(ang) * .12 + .02, z))
        steps.cyl(.012, .22, loc=tuple(p), rot=ACROSS, seg=4, bevel=0)
    _box_on(a.part('Number_plate', 'Hazard'), m @ _basis((0, -.135, 2.0), (1, 0, 0), (0, -1, 0)), (.14, .2, .02))
    # Leaning stay wire to an anchor along -X.
    top, anchor = Vector(m @ Vector((-.1, 0, 5.5))), Vector((-1.7, 0, .06))
    stay = a.part('Stay', 'Steel')
    stay.tube([tuple(top), tuple(anchor)], .012, seg=3)
    d = anchor - top
    insul.cyl(.04, .16, loc=top + d * .3, rot=_along(d), seg=6, bevel=0)
    a.part('Stay_guard', 'Hazard').cyl(.03, 1.6, loc=anchor - d.normalized() * .82, rot=_along(d), seg=6, bevel=0)
    a.part('Anchor', 'Concrete').box((.3, .3, .12), loc=(-1.72, 0, .04), rot=(0, 0, .2), bevel=.02, seg=1)


# ----------------------------------------------------------------------------- radio_mast
def radio_mast(a):
    """Guyed lattice radio mast (3.0 x 3.0 m, 16.3 m): a triangular lattice painted in red and white aviation
    bands on a concrete pad, held by guy wires at two levels to three anchor blocks on the footprint edge.
    Red obstruction lights (the emissive LavaGlow of the kit's traffic and warning lights) burn at the top
    and at 8 and 12 m; panel antennas and a dish near the top, a lightning rod, a feeder cable down one leg
    and an equipment cabinet with a lamp at the foot. Blocks neither movement nor fire (a thin mast)."""
    a.part('Pad', 'Concrete').box((1.1, 1.1, .3), loc=(0, 0, .13), bevel=.03, seg=1)
    r, z0, z1, panels = .3, .28, 15.6, 12
    corners = [(r * math.cos(t), r * math.sin(t)) for t in (R90, R90 + TAU / 3, R90 + 2 * TAU / 3)]
    for i in range(panels):
        za, zb = z0 + (z1 - z0) * i / panels, z0 + (z1 - z0) * (i + 1) / panels
        red = (i // 2) % 2 == 0
        p = a.part('Mast_red' if red else 'Mast_white', 'BarrelRed' if red else 'PlasterWhite')
        leg = .07 if i % 2 == 0 else .09                     # alternate, so overlapping leg ends never share faces
        for q in range(3):
            p.limb((*corners[q], za - .05), (*corners[q], zb + .05), leg, leg, bevel=0)
        for q in range(3):
            q2 = (q + 1) % 3
            c0, c1 = (corners[q], corners[q2]) if i % 2 == 0 else (corners[q2], corners[q])
            p.limb((*c0, za + .04), (*c1, zb - .04), .03, .03, bevel=0)
            p.limb((*corners[q], zb + .012 * (q - 1)), (*corners[q2], zb + .012 * (q - 1)), .05, .05, bevel=0)
    steel = a.part('Steel', 'Steel')
    steel.box((.7, .7, .06), loc=(0, 0, z0 + .02), bevel=0)
    steel.cyl(.02, 1.0, loc=(0, 0, z1 + .5), seg=4, bevel=0)                                  # lightning rod
    glow = a.part('Obstruction_lights', 'LavaGlow')
    for x, y, z in ((0, 0, z1 + .12), (corners[1][0], corners[1][1], 8.35), (corners[2][0], corners[2][1], 8.35),
                    (corners[0][0], corners[0][1], 12.0)):
        steel.cyl(.08, .08, loc=(x, y, z - .07), seg=6, bevel=0)
        glow.sphere(.075, loc=(x, y, z + .02), seg=8, rings=5)
    for q, z in ((1, 13.8), (2, 13.8)):
        cx, cy = corners[q]
        t = math.atan2(cy, cx)
        a.part('Panel_antennas', 'Armor').box((.28, .1, 1.1), loc=(cx * 1.6, cy * 1.6, z), rot=(0, 0, t + R90),
                                              bevel=.02,
                                              seg=1)
        steel.limb((cx, cy, z - .3), (cx * 1.6, cy * 1.6, z - .3), .04, .04, bevel=0)
    dish = a.part('Dish', 'Medical')
    dish.lathe([(0.02, 0), (.3, .05), (.46, .16), (.48, .2), (.02, .06)], loc=(0, -.62, 11.0), rot=(R90 + .15, 0, 0),
               seg=12)
    steel.limb((0, -.25, 11.0), (0, -.55, 11.0), .05, .05, bevel=0)
    fx, fy = corners[2][0] + .06, corners[2][1]
    a.part('Feeder', 'Rubber').tube([(fx, fy, .5), (fx, fy, 13.6)], .03, seg=4)
    a.part('Cabinet', 'Armor').box((.6, .4, 1.0), loc=(.15, -.9, .5), bevel=.02, seg=1)
    a.part('Cabinet_lamp', 'Lamp').box((.05, .02, .05), loc=(.35, -1.11, .85), bevel=0)
    a.part('Feeder', 'Rubber').tube([(.25, -.69, .7), (.32, -.45, .4), (fx, fy, .5)], .03, seg=4)
    guys = a.part('Guys', 'Steel')
    for q in range(3):
        cx, cy = corners[q]
        t = math.atan2(cy, cx)
        ax, ay = 1.5 * math.cos(t), 1.5 * math.sin(t)
        a.part('Anchors', 'Concrete').box((.34, .34, .3), loc=(ax, ay, .1), rot=(0, 0, t), bevel=.03, seg=1)
        for z in (7.0, 14.2):
            guys.tube([(cx, cy, z), (ax, ay, .25)], .012, seg=3)
        steel.cyl(.03, .25, loc=(ax * .96, ay * .96, .4), rot=_along((cx - ax, cy - ay, 7.0)), seg=6, bevel=0)


# ----------------------------------------------------------------------------- bridge_road
def bridge_road(a):
    """Concrete road bridge span (8.0 x 20.0 m) along Y for a river: a flat, drivable deck whose road surface
    is at 1.2 m (asphalt with lane markings and expansion joints, raised sidewalks with kerbs), solid
    parapet walls under steel handrails, two lamp posts, edge beams with drain spouts, four longitudinal
    girders on two piers (pier caps on round columns) and end abutments. The piers and abutments run down
    to 1 m below ground so they meet a river bed. Battle damage: a broken, bent stretch of the +X railing
    with exposed rebar, a scorch and debris on the road. Blocks nothing (it is driven over)."""
    rng = random.Random(111)
    conc = a.part('Concrete', 'Concrete')
    L = 10.0
    conc.box((7.8, 2 * L, .35), loc=(0, 0, .905), bevel=.02, seg=1)                          # slab .73 - 1.08
    a.part('Road', 'Asphalt').box((5.8, 2 * L, .12), loc=(0, 0, 1.14), bevel=0)              # road top 1.2
    for s in (-1, 1):
        a.part('Sidewalks', 'Concrete').box((1.0, 2 * L, .27), loc=(s * 3.4, 0, 1.215), bevel=.02, seg=1)
        conc.box((.12, 2 * L, .8), loc=(s * 3.96, 0, 1.0), bevel=.02, seg=1)                  # edge beam
        for y in (-7.5, -2.5, 2.5, 7.5):
            a.part('Drains', 'Steel').cyl(.05, .25, loc=(s * 4.05, y, .8), rot=ACROSS, seg=6, bevel=0)
    paint = a.part('Markings', 'PlasterWhite')
    for s in (-1, 1):
        paint.box((.1, 2 * L - .4, .03), loc=(s * 2.7, 0, 1.2), bevel=0)
    for k in range(7):
        paint.box((.12, 1.4, .03), loc=(0, -9.0 + k * 3.0, 1.2), bevel=0)
    for y in (-L + .35, -3.4, 3.4, L - .35):
        a.part('Joints', 'Steel').box((5.76, .12, .05), loc=(0, y, 1.2), bevel=0)
    # Parapet walls and handrails, broken on the +X side between y = 1.6 and 4.8.
    wall = a.part('Parapets', 'Concrete')
    rail = a.part('Handrails', 'Steel')
    gap = (1.6, 4.8)
    for s in (-1, 1):
        runs = [(-L, L)] if s < 0 else [(-L, gap[0]), (gap[1], L)]
        for y0, y1 in runs:
            wall.box((.22, y1 - y0 - .02, .45), loc=(s * 3.79, (y0 + y1) / 2, 1.555), bevel=.02, seg=1)
            n = max(1, round((y1 - y0) / 1.6))
            for k in range(n + 1):
                y = y0 + .1 + (y1 - y0 - .2) * k / n
                rail.box((.06, .06, .5), loc=(s * 3.79, y, 2.0), bevel=0)
            for z in (2.2, 1.95):
                rail.tube([(s * 3.79, y0 + .1, z), (s * 3.79, y1 - .1, z)], .035 if z > 2 else .025, seg=6)
    # The broken stretch: stubs of wall, a bent rail and rebar, debris.
    rust = a.part('Rebar', 'Rust')
    for y, h in ((gap[0] + .25, .3), (gap[1] - .3, .22)):
        wall.box((.22, .5, h), loc=(3.79, y, 1.33 + h / 2), rot=(0, 0, .05), bevel=0, taper=(.9, .7))
    for k in range(4):
        y = gap[0] + .5 + k * .7
        rust.limb((3.72 + .04 * k, y, 1.34),
                  (3.95 + .1 * rng.random(), y + rng.uniform(-.2, .2), 1.6 + .3 * rng.random()),
                  .025, .025, bevel=0)
    rail.tube([(3.79, gap[0] - .1, 2.2), (3.95, gap[0] + .8, 2.1), (4.0, gap[0] + 1.4, 1.75)], .035, seg=6)
    rail.tube([(3.79, gap[1] + .1, 2.2), (3.9, gap[1] - .6, 2.25)], .035, seg=6)
    _chunks([a.part('Debris', 'Concrete', flat=True)], rng, 2.1, 3.3, .9, .2, 7, z0=1.2, size=(.1, .22), seed=4.0)
    _blotch(a.part('Scorch', 'Charred'), _top(1.4, 3.4, 1.2), 1.1, 112, sides=12)
    # A shell hit through the asphalt on the other lane: bare deck concrete, rebar, potholes, debris.
    _blotch(a.part('Deck_scar', 'Concrete'), _top(-1.5, -5.6, 1.2), .75, 113, sides=11)
    _blotch(a.part('Scorch', 'Charred'), _top(-1.45, -5.55, 1.215), .4, 114, sides=9)
    for k in range(3):
        rust.limb((-1.9 + k * .35, -5.9, 1.2), (-1.8 + k * .3, -5.3 + .1 * k, 1.26 + .05 * k), .02, .02, bevel=0)
    for x, y, r, seed in ((-.9, -7.2, .22, 115), (-1.9, -3.9, .18, 116), (1.8, -1.2, .2, 117)):
        _blotch(a.part('Potholes', 'Charred'), _top(x, y, 1.2), r, seed, sides=7)
    _chunks([a.part('Debris', 'Concrete', flat=True), a.part('Asphalt_chunks', 'Asphalt', flat=True)], rng, -1.3, -5.0,
            1.3, .15, 8, z0=1.2, size=(.08, .2), seed=6.0)
    # Lamp posts.
    for s, y in ((-1, -5.0), (1, 6.5)):
        rail.cyl(.07, 5.0, loc=(s * 3.79, y, 1.78 + 2.5), seg=8, bevel=0)
        rail.limb((s * 3.79, y, 6.6), (s * 2.9, y, 6.85), .06, .06, bevel=0)
        a.part('Lamp_heads', 'Armor').box((.5, .22, .14), loc=(s * 2.75, y, 6.85), bevel=.02, seg=1)
        a.part('Lamps', 'Lamp').box((.4, .16, .03), loc=(s * 2.75, y, 6.77), bevel=0)
    # Girders, piers and abutments.
    for x in (-2.9, -1.0, 1.0, 2.9):
        conc.box((.42, 2 * L - 1.2, .45), loc=(x, 0, .52), bevel=.02, seg=1)
    for y in (-3.4, 3.4):
        conc.box((7.2, .9, .5), loc=(0, y, .06), bevel=.03, seg=1)
        for x in (-2.3, 2.3):
            conc.cyl(.42, 1.0, loc=(x, y, -.45), seg=12, bevel=0)
    for s in (-1, 1):
        conc.box((7.8, .8, 1.73), loc=(0, s * (L - .4), -.135), bevel=.02, seg=1)


# ----------------------------------------------------------------------------- ruins
def _ruin_walls(a, rng, walls, base, th, core='Brick', skin='Plaster', soot_h=1.6, skin_drop=.5, amp=.28, inner=None):
    """Broken walls after mb_town.ruin. walls = [(face, offset, length, controls, openings)...]: '-y' / '+y'
    walls run along X (u = x), '-x' / '+x' along Y (u = y), centred on `offset`; controls [(u, height)...]
    shape the broken top (plus sharp piecewise noise of `amp`), openings [(u0, u1, sill, lintel)...] are cut
    through (spans the break has eaten are dropped, so a lintel with a gap becomes a notch). Each wall is a
    core `th` thick with an outer skin that stops lower (the facing fallen away) and soot inside, over an
    optional interior plaster skin (`inner`) 1 cm further back that shows above the soot."""
    core_p = a.part('Walls', core, flat=True)
    skin_p = a.part('Wall_facing', skin, flat=True)
    soot_p = a.part('Soot', 'Charred', flat=True)
    inner_p = a.part('Wall_plaster', inner, flat=True) if inner else None

    def profile(controls, u):
        for (ua, ha), (ub, hb) in zip(controls, controls[1:]):
            if ua <= u <= ub:
                return ha + (hb - ha) * (u - ua) / (ub - ua)
        return controls[0][1] if u < controls[0][0] else controls[-1][1]

    def wobble(L, amp_):
        n = max(4, int(L / .32))
        vals = [rng.uniform(-amp_, amp_) for _ in range(n + 1)]

        def f(u):
            t = min(float(n), max(0.0, (u + L / 2) / L * n))
            i = min(n - 1, int(t))
            return vals[i] + (vals[i + 1] - vals[i]) * (t - i)
        return f

    def pieces(L, height, openings, grow=0.0):
        n = max(4, int(L / .32))
        us = [-L / 2 + L * i / n for i in range(n + 1)]

        def top(u):
            return max(.15, height(u))
        ops = [(u0 - grow, u1 + grow, zb - grow, zt + grow) for u0, u1, zb, zt in openings]
        cuts = sorted({-L / 2, L / 2} | {max(-L / 2, min(L / 2, c)) for o in ops for c in o[:2]})
        out = []
        for ua, ub in zip(cuts, cuts[1:]):
            if ub - ua < .02:
                continue
            mid = (ua + ub) / 2
            spans, z = [], 0.0
            for zb, zt in sorted((zb, zt) for u0, u1, zb, zt in ops if u0 <= mid <= u1):
                if zb > z + .05:
                    spans.append((z, zb))
                z = max(z, zt)
            spans.append((z, math.inf))
            tops = [(ua, top(ua))] + [(u, top(u)) for u in us if ua < u < ub] + [(ub, top(ub))]
            for za, zb in spans:
                if max(h for _, h in tops) < za + .12 or (za > 0 and min(h for _, h in tops) < za + .1):
                    continue
                edge = [(u, min(zb, max(za + .03, h))) for u, h in tops]
                out.append([(ua, za), (ub, za)] + edge[::-1])
        return out

    def extrude(part, face, offset, polys, depth, dz=0.0):
        for poly in polys:
            if face in ('-y', '+y'):
                part.prism(poly, depth, loc=(0, offset, base + dz), axis='Y', bevel=0)
            else:
                part.prism(poly, depth, loc=(offset, 0, base + dz), axis='X', bevel=0)
    tops = {}
    for face, off, L, controls, openings in walls:
        nz, drop = wobble(L, amp), wobble(L, .25)

        def jag(u, c=controls, nz=nz):
            return profile(c, u) + nz(u)
        extrude(core_p, face, off, pieces(L, jag, openings), th)
        sgn = 1 if face in ('+y', '+x') else -1
        extrude(skin_p, face, off + sgn * (th / 2 + .005),
                pieces(L - .04, lambda u, j=jag, dr=drop: j(u) - skin_drop - dr(u), openings, grow=.12), .05)
        extrude(soot_p, face, off - sgn * (th / 2 + .005),
                pieces(L - .04, lambda u, j=jag: min(j(u) - .15, soot_h + .5 * math.sin(u * 2.3)), openings, grow=.05),
                .05)
        if inner_p:
            extrude(inner_p, face, off - sgn * (th / 2 - .005),
                    pieces(L - .06, lambda u, j=jag, dr=drop: j(u) - .35 - .6 * dr(u), openings, grow=.08), .05,
                    dz=.012)
        tops[face] = lambda u, c=controls: profile(c, u)
    return tops


def ruin_house(a):
    """Shelled two-storey house (8.0 x 8.0 m, 6.6 m): only the back and left walls still stand, their tops
    torn jagged (the left gable corner reaches 6.6 m) with empty window holes, broken floor joists, a
    hanging radiator and soot inside; the front and right walls are knee-high stubs. The roof has fallen
    in: a ridge beam and charred rafters lean from the back wall into a big heap of brick, plaster and
    concrete rubble in the middle, one tiled section of roof still lies on them; roof tiles, planks, a
    bathtub and a door frame in the debris, on a scorched floor slab. Reads as a ruin from any side.
    Blocks movement and fire."""
    rng = random.Random(121)
    base, th, h = .22, .32, 3.8
    a.part('Plinth', 'Concrete').box((7.8, 7.8, base), loc=(0, 0, base / 2), bevel=.04, seg=1)
    _blotch(a.part('Scorch', 'Charred'), _top(.3, .2, base), 3.0, 122, sides=12, squash=.9)
    _ruin_walls(a, rng, [
        ('+y', h - th / 2, 2 * h,
         [(-3.8, 6.4), (-2.9, 5.6), (-1.6, 4.9), (-.2, 3.3), (1.0, 2.6), (2.2, 1.5), (3.8, .9)],
         [(-2.6, -1.6, 1.0, 2.3), (.4, 1.4, 1.0, 2.3), (-2.6, -1.6, 3.7, 4.9), (.4, 1.4, 3.7, 4.9), (-.9, .0, 0, 2.2)]),
        ('-x', -h + th / 2, 2 * (h - th), [(-3.5, 1.1), (-2.2, 2.3), (-.8, 3.3), (.9, 4.6), (2.4, 5.4), (3.5, 6.2)],
         [(-2.4, -1.4, 1.0, 2.3), (.4, 1.4, 1.0, 2.3), (.4, 1.4, 3.7, 4.9)]),
        ('-y', -h + th / 2, 2 * h, [(-3.8, 1.3), (-2.6, .75), (-1.2, .35), (.8, .55), (2.4, .25), (3.8, .6)],
         [(-.5, .5, 0, 2.2)]),
        ('+x', h - th / 2, 2 * (h - th), [(-3.5, .5), (-1.2, .9), (1.0, .35), (3.5, 1.1)], []),
    ], base, th, soot_h=2.1, inner='PlasterWhite')
    core = a.part('Walls', 'Brick', flat=True)
    core.box((.7, .5, 5.2), loc=(-3.3, 1.8, base + 2.6), bevel=0)                               # chimney breast
    char = a.part('Beams', 'Charred')
    wood = a.part('Planks', 'Wood')
    for y in (-.2, .7, 1.6, 2.5):                                                                # joist stubs
        char.box((.7 if y > 1 else .45, .16, .22), loc=(-3.4 + (.35 if y > 1 else .22), y, base + 3.3), rot=(0, .15, 0),
                 bevel=0)
    a.part('Radiator', 'Steel').box((.8, .1, .5), loc=(-1.0, h - th - .08, base + 4.1), rot=(0, .25, 0), bevel=0)
    # Collapsed roof: ridge beam and rafters leaning into the heap, a tiled section on them.
    char.limb((-3.3, 3.4, base + 6.0), (1.5, -1.3, base + 1.3), .26, .26, bevel=0)
    for x0, x1, top in ((-3.1, -2.2, 5.7), (-2.3, -1.3, 5.0), (-1.4, -.2, 4.4), (-.5, .8, 3.3), (.5, 1.9, 2.5)):
        (char if x0 < -1 else wood).limb((x0, 3.45, base + top), (x1, -.6 + rng.uniform(-.4, .4), base + .9), .14, .18,
                                         bevel=0)
    roof = _basis((-1.9, .9, base + 2.35), (1, .25, .1), (.15, -.5, .85))
    tiles = [(-1.0, -.85), (.9, -.95), (1.05, -.1), (.75, .2), (.95, .8), (.2, .95), (-.1, .7), (-.45, .95),
             (-1.05, .8), (-.9, .1), (-1.1, -.3)]
    a.part('Roof_tiles', 'RoofSlate').prism(tiles, .09, loc=roof.to_translation(), rot=roof.to_euler('XYZ'), axis='Z',
                                            bevel=0)
    for v in (-.6, -.1, .4):
        _box_on(wood, roof, (1.9, .06, .05), off=(0, v, -.07))
    # Rubble heap, tiles, planks, a bathtub and a door frame.
    _chunks([core, a.part('Plaster_chunks', 'Plaster', flat=True), a.part('Chunks', 'Concrete', flat=True)], rng,
            .6, -.4, 2.7, 1.6, 26, z0=base, size=(.28, .7), seed=5.0)
    heap = a.part('Heap', 'Brick', flat=True)
    heap.ico((2.3, 2.0, 1.0), loc=(.6, -.4, base - .2), sub=2, jitter=.3, seed=6.0)
    for v in heap.bm.verts:                                                                     # flat, buried base
        v.co.z = max(v.co.z, base - .04)
    _chunks([core], rng, -1.8, 2.3, 1.1, .6, 8, z0=base, size=(.2, .45), seed=9.0)
    tile = a.part('Tiles', 'RoofSlate')
    for k in range(10):
        tile.box((rng.uniform(.5, .9), rng.uniform(.35, .55), .07),
                 loc=(rng.uniform(-3.0, 3.0), rng.uniform(-3.2, 1.0), base + rng.uniform(.25, 1.0)),
                 rot=(rng.uniform(-.5, .5), rng.uniform(-.5, .5), rng.uniform(0, TAU)), bevel=0)
    for k in range(5):
        wood.box((.16, rng.uniform(1.4, 2.4), .06),
                 loc=(rng.uniform(-2.6, 2.6), rng.uniform(-2.8, 1.8), base + rng.uniform(.3, .9)),
                 rot=(rng.uniform(-.35, .35), rng.uniform(-.3, .3), rng.uniform(0, TAU)), bevel=0)
    tub = _frame((2.4, 1.7, base + .15), (.25, -.12, .5))
    a.part('Bathtub', 'Medical').shell([(-.75, -.34), (.75, -.34), (.75, .34), (-.75, .34)], .5, .05,
                                       loc=tub.to_translation(), rot=tub.to_euler('XYZ'), floor=.05, bevel=.02)
    df = a.part('Door_frame', 'Wood')
    for x in (-.93, .03):
        df.box((.1, .12, 2.2), loc=(x, h - th / 2, base + 1.1), bevel=0)
    df.box((1.06, .12, .1), loc=(-.45, h - th / 2, base + 2.25), rot=(0, .06, 0), bevel=0)


def ruin_tower(a):
    """Shelled church tower (5.0 x 5.0 m, 10 m): a square stone tower on a plinth, torn open by a great
    V-shaped breach in its front (-Y) face; the back-right corner still stands 10 m with its belfry
    openings (louvres in the side one), the other walls are broken lower, stone facing fallen from the
    brick core near the breaks and soot inside. Stepped corner buttresses, two string courses where the
    wall survives, a shattered clock face on the +X side, charred bell-frame beams jutting from the top,
    the fallen bell lying in the rubble at the foot of the breach and rubble inside and out. Blocks
    movement and fire."""
    rng = random.Random(131)
    base, half, th = .4, 2.1, .55
    a.part('Plinth', 'Concrete').box((4.9, 4.9, base), loc=(0, 0, base / 2), bevel=.05, seg=1)
    front = [(-2.1, 6.4), (-1.3, 5.0), (-.4, 2.8), (.5, 2.4), (1.3, 5.4), (2.1, 8.2)]
    walls = [
        ('-y', -half + th / 2, 2 * half, front, [(-.55, .55, 0, 2.6), (-.35, .35, 4.3, 5.7)]),
        ('+y', half - th / 2, 2 * half, [(-2.1, 7.2), (-.8, 8.2), (.8, 9.3), (2.1, 9.6)],
         [(-.45, .45, 7.2, 8.6), (-.35, .35, 4.3, 5.5)]),
        ('-x', -half + th / 2, 2 * (half - th), [(-1.55, 6.2), (0, 5.6), (1.55, 7.0)], [(-.35, .35, 4.3, 5.5)]),
        ('+x', half - th / 2, 2 * (half - th), [(-1.55, 8.0), (0, 8.9), (1.55, 9.5)], [(-.45, .45, 7.2, 8.6)]),
    ]
    tops = _ruin_walls(a, rng, walls, base, th, core='Brick', skin='Concrete', soot_h=4.5, skin_drop=.7, amp=.35)
    stone = a.part('Stonework', 'Concrete')
    for sx in (-1, 1):
        for sy in (-1, 1):
            hgt = 3.0 if sy < 0 else 4.2
            stone.box((.8, .8, 2.4), loc=(sx * half, sy * half, base + 1.2), bevel=.03, seg=1)
            stone.box((.66, .66, hgt - 2.4), loc=(sx * half, sy * half, base + (2.4 + hgt) / 2), bevel=.03, seg=1,
                      taper=(.85, .85))
    # String courses where the wall still stands.
    for face, off, L, controls, openings in walls:
        for zb in (3.6, 6.8):
            us = [-L / 2 + L * k / 24 for k in range(25)]
            run = []
            for u in us + [None]:
                ok = u is not None and tops[face](u) - .6 > zb and not (-.6 < u < .6 and face == '-y')
                if ok:
                    run.append(u)
                    continue
                if len(run) > 2:
                    u0, u1 = run[0], run[-1]
                    if face in ('-y', '+y'):
                        u0, u1 = max(u0, -half - .09), min(u1, half + .09)
                        yy = (half + .045) * (1 if face == '+y' else -1)
                        stone.box((u1 - u0, .09, .18), loc=((u0 + u1) / 2, yy, base + zb), bevel=0)
                    else:
                        u0, u1 = max(u0, -half), min(u1, half)
                        xx = (half + .045) * (1 if face == '+x' else -1)
                        stone.box((.09, u1 - u0, .18), loc=(xx, (u0 + u1) / 2, base + zb + .02), bevel=0)
                run = []
    # Belfry louvres in the +X opening, clock face below it.
    a.part('Louvres', 'Wood').grille(.8, 1.3, loc=(half - .1, 0, base + 7.9), rot=(0, 0, R90), slats=5, depth=.06,
                                     thickness=.05)
    clock = [(.6 * math.cos(t), .6 * math.sin(t)) for t in (k * TAU / 14 for k in range(14))]
    clock[3] = (clock[3][0] * .35, clock[3][1] * .35)
    clock[4] = (clock[4][0] * .5, clock[4][1] * .45)
    zc = base + 6.0
    a.part('Clock_ring', 'Charred').cyl(.66, .03, loc=(half + .03, 0, zc), rot=(0, R90, 0), seg=14, bevel=0)
    a.part('Clock', 'Medical').prism(clock, .04, loc=(half + .045, 0, zc), axis='X', bevel=0)
    hands = a.part('Clock_hands', 'Charred')
    hands.box((.02, .05, .4), loc=(half + .075, .05, zc + .15), rot=(.35, 0, 0), bevel=0)
    hands.box((.02, .3, .05), loc=(half + .075, -.12, zc - .03), rot=(.2, 0, 0), bevel=0)
    # Shell and bullet pocks on the faces the camera sees.
    pocks = a.part('Pocks', 'Charred')
    for k in range(14):
        u = rng.uniform(-1.6, 1.6)
        z = base + rng.uniform(1.2, 5.5)
        r = rng.uniform(.1, .22)
        if k % 2 and abs(u) > .75 and z + r < base + tops['-y'](u) - 1.1:
            _blotch(pocks, _front(u, -half - .035, z), r, 150 + k, sides=7)
        elif k % 2 == 0 and abs(z - zc) > .9 and z + r < base + tops['+x'](u) - 1.1:
            _blotch(pocks, _side(half + .035, u, z, 1), r, 160 + k, sides=7)
    # Charred bell-frame beams jutting from the top, a floor of soot, rubble, the bell.
    beams = a.part('Beams', 'Charred')
    beams.limb((-1.3, 1.4, base + 7.3), (1.6, .6, base + 8.9), .24, .24, bevel=0)
    beams.limb((1.4, -1.2, base + 6.4), (1.2, 1.5, base + 8.6), .22, .22, bevel=0)
    beams.limb((-1.2, -.8, base + 2.5), (.8, 1.3, base + 5.6), .2, .2, bevel=0)
    a.part('Floor', 'Charred').box((3.02, 3.02, .06), loc=(0, 0, base + .02), bevel=0)
    _chunks([a.part('Walls', 'Brick', flat=True), stone], rng, 0, 0, 1.4, 1.1, 10, z0=base, size=(.25, .5), seed=2.0)
    _chunks([a.part('Walls', 'Brick', flat=True), a.part('Rubble', 'Concrete', flat=True)], rng, .15, -2.35, .6, .7, 14,
            size=(.18, .42), seed=7.0)
    _chunks([a.part('Rubble', 'Concrete', flat=True)], rng, 2.35, .9, .5, .3, 5, size=(.15, .3), seed=8.0)
    bell = _frame((-.25, -2.3, .5), (1.25, .25, .6))
    a.part('Bell', 'Rust').lathe([(.03, 0), (.46, 0), (.48, .08), (.4, .24), (.31, .52), (.29, .74), (.2, .86),
                                  (.02, .9)],
                                 loc=bell.to_translation(), rot=bell.to_euler('XYZ'), seg=12)


# ----------------------------------------------------------------------------- dead_tree
def dead_tree(a):
    """Shell-shattered tree (2.0 x 2.0 m, 4.3 m): a leaning trunk snapped at 3 m into pale splinters around a
    charred break, bark blasted off one side, root flares, broken branch stubs with raw ends, one torn
    branch hanging down and the fallen crown section lying at its foot with a splintered end. Blocks
    neither movement nor fire."""
    rng = random.Random(141)
    bark = a.part('Bark', 'Bark')
    raw = a.part('Splinters', 'Adobe')
    char = a.part('Charred', 'Charred')
    lean = Vector((.06, -.04, 1)).normalized()
    rot = _along(lean)
    top = lean * 2.95
    bark.cyl(.27, 3.0, loc=lean * 1.5, r2=.2, rot=rot, seg=8, bevel=0)
    char.cyl(.19, .06, loc=top - lean * .02, rot=rot, seg=8, bevel=0)
    for k in range(9):
        t = k * TAU / 9 + rng.uniform(-.2, .2)
        rim = top + Vector((math.cos(t) * .16, math.sin(t) * .16, 0))
        hgt = rng.uniform(.35, 1.1) if k % 3 else rng.uniform(.2, .45)
        tip = rim + lean * hgt + Vector((math.cos(t), math.sin(t), 0)) * hgt * rng.uniform(.1, .35)
        (raw if k % 3 else bark).limb(tuple(rim - lean * .1), tuple(tip), .1, .06, bevel=0, taper=(.15, .2))
    for k in range(4):
        t = k * TAU / 4 + .5
        bark.limb((0, 0, .5), (math.cos(t) * .75, math.sin(t) * .75, .02), .22, .16, bevel=0, taper=(.4, .5))
    for z, t, length in ((1.9, .6, .6), (2.4, 2.5, .45), (2.6, 4.2, .7), (1.5, 3.6, .35)):
        p = lean * z
        d = Vector((math.cos(t), math.sin(t), .6)).normalized()
        bark.limb(tuple(p), tuple(p + d * length), .12, .12, bevel=0, taper=(.5, .5))
        raw.limb(tuple(p + d * (length - .04)), tuple(p + d * (length + .1)), .06, .05, bevel=0, taper=(.3, .3))
    p = lean * 2.2
    bark.limb(tuple(p), (.75, .45, .55), .11, .1, bevel=0, taper=(.6, .6))                       # torn branch hanging
    bark.limb((.75, .45, .55), (.85, .6, .05), .06, .06, bevel=0, taper=(.5, .5))
    bark.limb((.62, .36, .9), (.9, .15, .6), .05, .05, bevel=0, taper=(.4, .4))
    for k, (zb, t) in enumerate(((1.0, 3.5), (1.7, 3.9))):                                       # bark blasted off
        m = _basis(lean * zb + Vector((math.cos(t), math.sin(t), 0)) * .235, (-math.sin(t), math.cos(t), 0),
                   (math.cos(t), math.sin(t), 0))
        _blotch(raw if k == 0 else char, m, .16, 142 + k, depth=.04, squash=2.2)
    # The fallen crown section with its splintered end.
    d = Vector((math.cos(1.15), math.sin(1.15), 0))
    c = Vector((-.45, -.55, .17))
    bark.cyl(.17, 1.4, loc=c, rot=(0, R90, 1.15), r2=.12, seg=7, bevel=0)
    end = c - d * .7
    for k in range(4):
        t = k * TAU / 4
        off = Vector((-d.y, d.x, 0)) * math.cos(t) * .1 + Vector((0, 0, math.sin(t) * .1))
        raw.limb(tuple(end + off + d * .05), tuple(end + off * 1.3 - d * rng.uniform(.25, .45)), .07, .05, bevel=0,
                 taper=(.2, .2))
    bark.limb(tuple(c + d * .3), tuple(c + d * .3 + Vector((.1, -.3, .45))), .06, .06, bevel=0, taper=(.4, .4))


# ----------------------------------------------------------------------------- wreck_tank
def wreck_tank(a):
    """Burnt-out main battle tank hulk (3.4 x 7.0 m, 2.3 m). The MBT's hull, blackened and blotched with
    rust: the turret is knocked 20 degrees round, tipped and shoved off its ring with the gun snapped at
    2 m and drooping; the right track has come off and lies flat under the bare road wheels, its broken
    end trailing out ahead; left skirts torn away or hanging, glacis armour blocks missing, hatches blown
    open, a road wheel and a skirt plate lying on the ground. Blocks movement and fire."""
    rng = random.Random(71)
    char = a.part('Hull', 'Charred')
    rust = a.part('Rust', 'Rust')
    soot = a.part('Soot', 'Undercarriage')
    L, hw, bw, top, rb = 5.7, 1.22, .58, .95, .26
    char.prism([(-2.9, .44), (-2.9, .8), (-2.05, 1.26), (2.4, 1.26), (2.85, 1.02), (2.85, .44)], 1.96, axis='X',
               bevel=.05, seg=1)
    ash = a.part('Ash', 'Armor')
    char.cyl(.98, .1, loc=(0, .15, 1.29), seg=12, bevel=0)                            # turret ring
    soot.cyl(.86, .03, loc=(0, .15, 1.34), seg=10, bevel=0)                           # open ring
    # Left (far) track, burnt in place, under a fender; the right fender is torn and bent up.
    rl, first = .3, L / 2 - .5
    outline = _hull2d([(cy + r * math.cos(k * TAU / 12), cz + r * math.sin(k * TAU / 12))
                       for cy, cz, r in ((-(L / 2 - rb), top - rb, rb), (L / 2 - rb, top - rb, rb),
                                         (-first, rl - .01, rl), (first, rl - .01, rl)) for k in range(12)])
    a.part('Track', 'Undercarriage').prism(outline, bw, loc=(-hw, 0, 0), axis='X', bevel=0)
    char.box((bw + .14, L * .92, .06), loc=(-hw, -.03, top + .05), bevel=0)
    char.box((bw + .14, 2.65, .06), loc=(hw, -1.3, top + .05), bevel=0)
    char.box((bw + .1, 1.1, .06), loc=(hw + .03, .05 + .5, top + .05 + .22), rot=(.45, .12, .04), bevel=0)
    char.box((bw + .14, .5, .06), loc=(hw, -2.83, top - .06), rot=(-.5, 0, 0), bevel=0)   # bent fender tip
    # Left skirts: three plates left, one hanging from a bolt, one blown off (on the ground at the front).
    step = (5.05 + .035) / 5
    for i in range(5):
        yc = -2.75 + step * (i + .5) - .0175
        if i == 2:
            continue
        if i == 4:
            m = _frame((-1.6, yc + .47, 1.25), (.5, 0, 0))
            _box_on(char, m, (.1, .96, .56), off=(0, -.47, -.27))
        else:
            char.box((.1, .96, .56), loc=(-1.6, yc, .98), bevel=0)
            rust.box((.03, .5, .3), loc=(-1.655, yc + rng.uniform(-.15, .15), .9), rot=(rng.uniform(-.3, .3), 0, 0),
                     bevel=0)
    ys = [-L / 2 + .5 + i * (L - 1.0) / 6 for i in range(7)]
    wheels = a.part('Wheels', 'Charred')
    for i in (2, 3):                                                                    # left, behind the gap
        wheels.cyl(.28, .09, loc=(-1.53, ys[i], .44), rot=ACROSS, seg=8, bevel=0)
        rust.cyl(.08, .04, loc=(-1.59, ys[i], .44), rot=ACROSS, seg=4, bevel=0)
    # Right side: bare road-wheel rims standing on the thrown track; wheel 4 lies on the ground behind.
    for i, y in enumerate(ys):
        if i == 4:
            continue
        wheels.cyl(.26, .09, loc=(1.53, y, .32), rot=ACROSS, seg=8, bevel=0)
        rust.cyl(.08, .04, loc=(1.59, y, .32), rot=ACROSS, seg=4, bevel=0)
    wheels.cyl(.22, .08, loc=(1.5, 2.59, .69), rot=ACROSS, seg=10, bevel=0)              # sprocket
    for k in range(5):
        ang = k * TAU / 5 + .3
        rust.box((.05, .07, .08), loc=(1.5, 2.59 + math.cos(ang) * .24, .69 + math.sin(ang) * .24),
                 rot=(ang + R90, 0, 0), bevel=0)
    wheels.cyl(.23, .08, loc=(1.5, -2.59, .69), rot=ACROSS, seg=10, bevel=0)             # idler
    rust.cyl(.08, .04, loc=(1.56, -2.59, .69), rot=ACROSS, seg=4, bevel=0)
    soot.box((.1, 5.2, .32), loc=(1.02, 0, .62), bevel=0)                               # sooty lower hull
    links = a.part('Track_links', 'Rust')
    path = [(hw, 2.62), (hw, -2.55), (hw + .05, -3.0), (hw + .17, -3.33), (hw + .36, -3.58)]
    for k, (p, t) in enumerate(_samples(path, .3, .1)):
        yaw = math.atan2(t.y, t.x) - R90
        tail = p.y < -2.6
        links.box((bw, .26, .06), loc=(p.x, p.y, .02 + (.015 * math.sin(k * 1.7) if tail else 0)),
                  rot=(rng.uniform(-.05, .05) if tail else 0, 0, yaw + (rng.uniform(-.08, .08) if tail else 0)),
                  bevel=0)
        if k % 4 == 0 and not tail:
            soot.box((.07, .1, .09), loc=(p.x - .1, p.y, .08), bevel=0)                 # guide horns
    # Glacis: three armour blocks left of five, bolt plates where the others were.
    g0, g1 = Vector((0, -2.9, .8)), Vector((0, -2.05, 1.26))
    gn = Vector((0, -(g1.z - g0.z), g1.y - g0.y)).normalized()
    gm = g0.lerp(g1, .5)
    for x, mat, twist in ((-1.1, char, 0.0), (0.0, rust, 0.0), (.55, char, .35)):
        m = _basis(gm + Vector((x, 0, 0)), (math.cos(twist), 0, math.sin(twist) * .3), gn)
        _box_on(mat, m, (.5, .42, .12), off=(0, -.03 if twist else 0, .05))
    for x in (-.55, 1.1):
        for dx in (-.15, .15):
            _box_on(soot, _basis(gm + Vector((x + dx, 0, 0)), (1, 0, 0), gn), (.06, .06, .05), off=(0, 0, .01))
    _blotch(rust, _basis(g0.lerp(g1, .35) + Vector((-.45, 0, 0)), (1, 0, 0), gn), .42, 1, squash=.6)

    # Driver's hatch blown open, periscopes, headlights, tow hooks.
    soot.cyl(.26, .04, loc=(0, -1.72, 1.265), seg=12, bevel=0)
    char.cyl(.26, .06, loc=(0, -1.42, 1.5), rot=(R90 - .35, 0, 0), seg=12, bevel=.015, bseg=1)
    for dx in (-.18, 0, .18):
        soot.box((.13, .08, .08), loc=(dx, -2.08, 1.28), bevel=0)
    for s in (-1, 1):
        char.box((.24, .12, .17), loc=(s * .72, -2.94, .72), bevel=0)
        soot.box((.15, .03, .1), loc=(s * .72, -3.005, .72), bevel=0)
        rust.box((.16, .18, .12), loc=(s * .3, -2.96, .62), bevel=0)
        soot.box((.44, .06, .3), loc=(s * .4, 2.86, .84), bevel=0)
    # Engine deck: grille, one crushed bin (the other gone), burnt-out fender bin, tow cables.
    soot.grille(1.3, .8, loc=(0, 1.72, 1.28), rot=(-R90, 0, 0), slats=4, depth=.1, thickness=.05)
    for dy in (-.43, .43):
        rust.box((1.42, .06, .05), loc=(0, 1.72 + dy, 1.27), bevel=0)
    char.box((.62, .22, .14), loc=(.62, 2.37, 1.3), rot=(.25, .12, .06), bevel=.02, seg=1)
    soot.box((.5, .12, .04), loc=(-.62, 2.37, 1.265), bevel=0)
    char.shell([(-.23, -.55), (.23, -.55), (.23, .55), (-.23, .55)], .26, .03, loc=(-1.29, 1.2, 1.02), floor=.02)
    rust.tube([(-1.25, -2.4, 1.06), (-1.25, -.6, 1.06), (-1.2, .5, 1.06), (-1.1, .8, 1.06)], .022, seg=4)
    rust.tube([(1.25, -1.9, 1.06), (1.34, -2.45, .95), (1.62, -2.8, .5), (1.72, -3.05, .04)], .022, seg=4)
    for x, y, r, seed, part in ((.45, -.95, .42, 2, rust), (-.5, 1.1, .36, 3, ash), (-1.22, -1.5, .3, 4, rust),
                                (1.22, -1.4, .28, 5, rust)):
        _blotch(part, _top(x, y, 1.26 if abs(x) < 1 else top + .08), r, seed, squash=.7 if abs(x) > 1 else 1.0)
    _blotch(soot, _top(.2, 1.72, 1.26), .55, 6, squash=.7)
    _blotch(soot, _top(0, -1.72, 1.26), .42, 7)

    # Turret: built round its own origin, then knocked askew onto the ring.
    before = set(a.shapes)
    tb = a.part('Hulk_turret', 'Charred')
    tr = a.part('Hulk_turret_rust', 'Rust')
    ts = a.part('Hulk_turret_soot', 'Undercarriage')
    outline = [(-.95, 1.05), (.95, 1.05), (1.12, .25), (.95, -.72), (.42, -1.18), (-.42, -1.18), (-.95, -.72),
               (-1.12, .25)]
    tb.prism(outline, .66, loc=(0, 0, .33), axis='Z', bevel=.05, taper=.9)
    tb.box((1.6, .7, .5), loc=(0, 1.35, .32), bevel=.04, seg=1, taper=(.95, .9))
    tb.box((.62, .34, .5), loc=(0, -1.22, .33), bevel=.04, seg=1)
    for b0, b1, keep in (((.42, -1.18), (.95, -.72), (.3,)), ((-.95, -.72), (-.42, -1.18), (.3, .7))):
        for u in keep:
            m = _face_frame(b0, b1, .66, .9, u=u, v=.45)
            _box_on(tr if u < .5 else tb, m, (.24, .22, .09), off=(0, 0, .035))
    tb.cyl(.3, .22, loc=(.42, .25, .77), seg=10, bevel=0)                              # cupola
    tb.cyl(.26, .05, loc=(.42, .6, 1.08), rot=(R90 - .3, 0, 0), seg=10, bevel=0)       # lid thrown open
    ts.cyl(.22, .04, loc=(.42, .25, .88), seg=10, bevel=0)
    ts.cyl(.25, .03, loc=(-.42, .35, .665), seg=10, bevel=0)                           # loader's hatch gone
    tb.box((.34, .3, .26), loc=(-.55, -.5, .76), bevel=0)                              # sight box
    ts.box((.24, .04, .14), loc=(-.55, -.66, .78), bevel=0)
    for s in (-1, 1):
        for i in range(3 if s < 0 else 1):
            tb.cyl(.05, .16, loc=(s * (.78 + i * .09), -.7, .56), rot=(.6, 0, s * .4), seg=4, bevel=0)
    tr.tube([(-.7, 1.72, .44), (-.72, 2.06, .5), (-.1, 2.12, .36), (.5, 2.02, .2)], .02, seg=4)
    tr.tube([(.7, 1.72, .44), (.74, 1.95, .62)], .02, seg=4)
    tr.cyl(.015, .5, loc=(-.72, .95, .9), rot=(.5, .3, 0), seg=4, bevel=0)             # antenna stub
    ta = a.part('Hulk_turret_ash', 'Armor')
    for x, y, r, seed, part in ((.35, -.45, .36, 11, tr), (.6, .75, .26, 12, ta), (.15, 1.32, .3, 13, tr)):
        _blotch(part, _top(x, y, .66 if abs(y) < 1 else .57), r, seed)
    _blotch(ts, _top(-.42, .35, .655), .45, 14)
    d = Vector((0, -math.cos(.1), -math.sin(.1)))
    base = Vector((0, -1.3, .33))
    a.part('Gun_tube', 'Charred').cyl(.11, 2.0, loc=base + d * 1.0, rot=_along(d), seg=10, bevel=0)
    tr.cyl(.16, .45, loc=base + d * .75, rot=_along(d), seg=10, bevel=0)                 # thermal sleeve
    end = base + d * 2.0
    side = Vector((1, 0, 0))
    upv = d.cross(side).normalized()
    for k in range(4):
        phi = k * TAU / 4 + .3
        radial = side * math.cos(phi) + upv * math.sin(phi)
        tip = end + d * rng.uniform(.1, .24) + radial * .05
        tr.limb(tuple(end + radial * .08 - d * .02), tuple(tip), .06, .025, bevel=0, taper=(.25, .25))
    turret = set(a.shapes) - before
    _transform(a, turret, Matrix.Translation((-.1, .12, 1.34)) @ Euler((.05, -.07, -.35), 'XYZ').to_matrix().to_4x4())

    # On the ground: road wheel, skirt plate, loose links, an armour block.
    wheels.cyl(.26, .09, loc=(.95, 3.28, .035), seg=8, bevel=0)
    rust.cyl(.08, .06, loc=(.95, 3.28, .07), seg=4, bevel=0)
    char.box((.96, .56, .08), loc=(-.95, -3.35, .03), rot=(.05, .03, .3), bevel=0)
    for x, y, yaw in ((-.2, 3.2, .6), (.2, 3.45, 1.9), (-1.5, 2.95, .2)):
        links.box((bw, .17, .06), loc=(x, y, .02), rot=(0, .04, yaw), bevel=0)
    char.box((.5, .42, .12), loc=(-.3, -3.45, .05), rot=(.08, -.06, .9), bevel=0)
    _centre(a)


# ----------------------------------------------------------------------------- wreck_truck
def wreck_truck(a):
    """Burnt-out 6x6 cargo truck (2.6 x 7.5 m, 2.3 m). Tyres burnt away, so it sits low on bare rims with
    the tyres' bead wires lying round two of them; the cab is crushed (pillars buckled, the roof folded
    down in a crease, windscreen and a door gone), the bonnet popped. The cargo bed keeps its canopy bows
    (one gone, one bent) over burnt planks with a scrap of canvas, charred crates and a drum; the side
    boards are burnt through and the tailgate hangs open. Blocks movement and fire."""
    char = a.part('Body', 'Charred')
    rust = a.part('Rust', 'Rust')
    soot = a.part('Soot', 'Undercarriage')
    zc = .36
    for s in (-1, 1):
        char.box((.16, 7.0, .24), loc=(s * .46, -.05, .62), bevel=0)
    for y in (-3.1, -1.2, .6, 2.2, 3.3):
        char.box((.78, .12, .14), loc=(0, y, .6), bevel=0)
    for y in (-2.45, 1.4, 2.75):
        char.cyl(.07, 1.9, loc=(0, y, zc), rot=ACROSS, seg=6, bevel=0)
        for s in (-1, 1):
            rust.cyl(.36, .26, loc=(s * 1.0, y, zc), rot=ACROSS, seg=10, bevel=0)
            soot.cyl(.17, .3, loc=(s * 1.0, y, zc), rot=ACROSS, seg=8, bevel=0)
    for x, y in ((.98, -2.45), (-.98, 1.4)):                                            # tyre bead wires
        rust.torus(.42, .014, loc=(x, y + .06, .03), rot=(.05, .1, 0), seg=12, ring=3)
    # Bonnet (popped open), radiator, fenders, bumper.
    char.box((1.5, 1.45, .75), loc=(0, -2.83, 1.12), bevel=.04, seg=1, taper=(.94, .96))
    char.box((1.4, .7, .04), loc=(.05, -2.55, 1.53), rot=(-.06, .07, .04), bevel=0)      # bonnet lid, buckled up
    char.box((1.36, .66, .04), loc=(.08, -3.18, 1.66), rot=(-.4, .1, .06), bevel=0)
    _blotch(rust, _frame((.2, -2.5, 1.555), (-.06, .07, .04)), .4, 20, squash=.7)
    soot.grille(1.1, .55, loc=(0, -3.57, 1.1), slats=4, depth=.05, thickness=.04)
    for s in (-1, 1):
        char.box((.55, 1.5, .05), loc=(s * 1.0, -2.55, 1.0), rot=(-.08, 0, s * .03), bevel=0)
        char.box((.55, .05, .34), loc=(s * 1.0, -3.27, .88), bevel=0)
        soot.cyl(.1, .1, loc=(s * .98, -3.31, 1.1), rot=FORWARD, seg=8, bevel=0)
        rust.box((.12, .2, .12), loc=(s * .6, -3.8, .78), bevel=0)                      # tow hooks
    rust.box((2.3, .2, .24), loc=(0, -3.68, .78), rot=(0, .05, 0), bevel=.02, seg=1)
    # Cab: lower body, buckled pillars, folded roof, gaping windows, burnt seats and wheel.
    char.box((2.2, 1.2, .82), loc=(0, -1.45, 1.19), bevel=.03, seg=1)
    for s in (-1, 1):
        char.limb((s * 1.04, -2.0, 1.58), (s * 1.13, -1.88, 1.78), .08, .08, bevel=0)
        char.limb((s * 1.13, -1.88, 1.78), (s * 1.02, -1.92, 1.96), .08, .08, bevel=0)
        char.limb((s * 1.04, -.92, 1.58), (s * 1.07, -.97, 2.0), .08, .08, bevel=0)
        soot.box((.02, .03, .7), loc=(s * 1.105, -1.96, 1.2), bevel=0)                  # door shut lines
    soot.box((.03, .9, .66), loc=(1.11, -1.4, 1.22), bevel=0)                           # door gone
    char.box((2.18, .62, .06), loc=(.05, -1.72, 1.97), rot=(.26, .12, .03), bevel=0)
    char.box((2.18, .62, .06), loc=(.02, -1.15, 2.0), rot=(-.18, .1, .02), bevel=0)
    char.box((2.1, .06, .36), loc=(0, -.9, 1.78), bevel=0)
    soot.box((1.1, .03, .2), loc=(0, -.93, 1.8), bevel=0)
    soot.box((1.9, .9, .06), loc=(0, -1.45, 1.61), bevel=0)                             # burnt interior
    soot.box((1.8, .4, .35), loc=(0, -1.15, 1.78), bevel=0)
    rust.torus(.18, .02, loc=(-.5, -1.78, 1.86), rot=(1.1, 0, 0), seg=10, ring=3)
    rust.tube([(1.05, -.8, .8), (1.05, -.8, 2.05), (1.12, -.95, 2.2)], .05, seg=6)       # exhaust stack
    rust.cyl(.25, 1.0, loc=(-.95, -.5, .62), rot=FORWARD, seg=10, bevel=.02, bseg=1)       # fuel tank
    char.box((.4, .6, .4), loc=(.9, -.4, .7), bevel=.02, seg=1)                          # tool box
    # Cargo bed: planks (some burnt through), rails, side boards with gaps, bows, cargo.
    y0, y1 = -.72, 3.6
    for i in range(7):
        if i == 4:
            continue
        x = -1.05 + i * .35
        ya, yb = (y0 + .05, 1.5) if i == 1 else (y0 + .05, y1 - .02)
        a.part('Planks', 'Wood' if i in (2, 5) else 'Charred').box((.31, yb - ya, .08), loc=(x, (ya + yb) / 2, .8),
                                                                  bevel=0)
    b0 = y0 + .03                                                                       # behind the bulkhead face
    for s in (-1, 1):
        rust.box((.08, y1 - b0, .14), loc=(s * 1.2, (b0 + y1) / 2, .81), bevel=0)
        for ya, yb in ((b0, .9), (1.3, 2.6)) if s > 0 else ((b0, 1.7), (2.2, y1)):
            char.box((.06, yb - ya, .46), loc=(s * 1.2, (ya + yb) / 2, 1.11), bevel=0)
        for y in (-.6, .6, 1.9, 3.5):
            rust.box((.12, .08, .6), loc=(s * 1.21, y, 1.14), bevel=0)
    char.box((2.4, .08, .9), loc=(0, -.68, 1.29), bevel=0)
    char.box((2.3, .06, .5), loc=(0, 3.68, .56), rot=(.15, 0, 0), bevel=0)               # tailgate hanging open
    bows = a.part('Bows', 'Rust')
    for y, lean in ((-.45, 0.0), (.75, 0.0), (3.15, .35)):
        m = _frame((0, y, .84), (lean * .4, 0, 0))
        pts = [(-1.18, 0, 0), (-1.18, 0, 1.06), (-1.0, 0, 1.36), (1.0, 0, 1.36 - lean), (1.18, 0, 1.06 - lean),
               (1.18, 0, 0)]
        bows.tube([tuple(m @ Vector(p)) for p in pts], .03, seg=4)
    for s in (-1, 1):
        bows.tube([(s * 1.18, 1.95, .84), (s * 1.18, 1.95, 1.3 if s < 0 else 1.6)], .03, seg=4)
    bows.tube([(-.5, -.45, 2.2), (-.5, .75, 2.2), (-.45, 1.2, 2.05)], .025, seg=4)
    a.part('Canvas_scrap', 'Canvas').box((.04, .85, .72), loc=(-1.25, .15, 1.72), rot=(.05, .22, 0), bevel=0)
    char.box((.04, .85, .12), loc=(-1.29, .15, 1.33), rot=(.05, .22, 0), bevel=0)
    for x, y, yaw in ((-.5, 2.2, .1), (.35, 2.9, -.25)):
        char.box((.9, .6, .5), loc=(x, y, 1.09), rot=(0, 0, yaw), bevel=.03, seg=1)
        rust.box((.2, .63, .52), loc=(x, y, 1.09), rot=(0, 0, yaw), bevel=0)
    rust.cyl(.29, .88, loc=(.4, 1.3, 1.13), rot=(0, R90, .3), seg=10, bevel=.02, bseg=1)
    _blotch(rust, _top(-.3, 1.0, .85), .3, 23)
    _blotch(rust, _side(-1.1, -1.5, 1.05, -1), .3, 24, squash=.7)
    for s in (-1, 1):
        _blotch(rust, _side(s * 1.23, .2, 1.12, s), .25, 27 + s, squash=.8)
    _centre(a)


# ----------------------------------------------------------------------------- wreck_car
def wreck_car(a):
    """Burnt-out saloon on its roof (2.0 x 4.4 m, 1.3 m): the roof and pillars are crushed flat under the
    body, which rests a little askew; the underside is on top for the camera: floor pan, tunnel and prop
    shaft, exhaust and silencer, fuel tank, suspension arms and axle, bare rims (one with a charred
    tyre). Charred shell with rust, dark window slots and wheel arches. Blocks movement and fire."""
    char = a.part('Body', 'Charred')
    rust = a.part('Rust', 'Rust')
    soot = a.part('Soot', 'Undercarriage')
    H = 1.3
    up = [(-2.15, .40), (2.1, .40), (2.12, .72), (2.0, .96), (.9, 1.0), (-1.15, 1.0), (-2.02, .9), (-2.17, .62)]
    char.prism([(y, H - z) for y, z in up], 1.74, axis='X', bevel=.06, seg=1)
    char.box((1.5, 2.0, .34), loc=(0, .05, .15), bevel=.03, seg=1, taper=(1.08, 1.05))     # crushed roof
    for s in (-1, 1):
        soot.box((.04, 1.75, .15), loc=(s * .785, .05, .17), rot=(0, s * .17, 0), bevel=0)
        soot.box((1.3, .04, .15), loc=(0, .05 + s * 1.03, .17), rot=(-s * .15, 0, 0), bevel=0)
        for y in (-1.32, 1.35):
            soot.prism([(y - .37, .9), (y - .33, .75), (y - .2, .66), (y, .63), (y + .2, .66), (y + .33, .75),
                        (y + .37, .9)], .03, loc=(s * .865, 0, 0), axis='X', bevel=0)
        for y in (-.9, .4):
            soot.box((.03, .025, .36), loc=(s * .875, y, .6), bevel=0)
        soot.box((.25, .05, .1), loc=(s * .56, -2.175, .66), bevel=0)                  # empty headlight sockets
        soot.box((.24, .05, .14), loc=(s * .62, 2.115, .47), bevel=0)
    # Underside, now on top: a rusty floor pan.
    a.part('Floor_pan', 'Rust').box((1.6, 3.9, .04), loc=(0, .0, .9), bevel=0)
    char.cyl(.16, 2.3, loc=(0, .25, .9), rot=FORWARD, seg=8, bevel=0)
    rust.cyl(.04, 1.5, loc=(0, .75, 1.07), rot=FORWARD, seg=6, bevel=0)
    rust.tube([(.35, -1.7, .93), (.36, -.5, .97), (.42, 1.1, .97), (.42, 2.15, .94)], .035, seg=5)
    rust.box((.28, .62, .17), loc=(.42, 1.55, .97), bevel=.02, seg=1)
    rust.box((.7, .5, .18), loc=(-.42, .95, .96), bevel=.03, seg=1)
    soot.box((.55, .7, .22), loc=(0, -1.45, .98), bevel=.03, seg=1)
    for s in (-1, 1):
        char.limb((s * .2, -1.55, .96), (s * .68, -1.34, 1.0), .08, .06, bevel=0)
        char.limb((s * .2, -1.1, .96), (s * .68, -1.3, 1.0), .08, .06, bevel=0)
    rust.cyl(.05, 1.46, loc=(0, 1.35, 1.0), rot=ACROSS, seg=6, bevel=0)
    rust.sphere(.14, loc=(0, 1.35, 1.0), seg=8, rings=5)
    for x, y in ((-.81, -1.32), (.81, 1.35)):
        rust.cyl(.2, .16, loc=(x, y, H - .31), rot=ACROSS, seg=10, bevel=0)
        soot.cyl(.08, .2, loc=(x, y, H - .31), rot=ACROSS, seg=6, bevel=0)
    for x, y in ((.81, -1.32), (-.81, 1.35)):                                           # charred tyres
        a.part('Tyres', 'Rubber').cyl(.3, .19, loc=(x, y, H - .31), rot=ACROSS, seg=12, bevel=.04, bseg=1)
        rust.cyl(.14, .23, loc=(x, y, H - .31), rot=ACROSS, seg=8, bevel=0)
    char.box((1.76, .16, .2), loc=(0, -2.22, .84), bevel=.03, seg=1)
    char.box((1.7, .16, .18), loc=(-.1, 2.2, .7), rot=(.1, .3, .05), bevel=.03, seg=1)    # rear bumper hanging
    for x, y, r, seed in ((.25, -.5, .4, 31), (-.35, 1.0, .32, 32)):
        _blotch(soot, _top(x, y, .92), r, seed, squash=.8)
    for s in (-1, 1):
        _blotch(rust, _side(s * .87, -.2, .55, s), .3, 35 + s, squash=.5)
    everything = list(a.shapes)
    _transform(a, everything, Matrix.Rotation(.07, 4, 'Y') @ Matrix.Rotation(.02, 4, 'X'))
    lo, _ = _bounds(a)
    _transform(a, everything, Matrix.Translation((0, 0, -lo.z - .02)))
    # Loose on the ground: a hub cap and a strip of trim.
    rust.cyl(.16, .03, loc=(.75, -2.0, .01), rot=(.05, 0, 0), seg=8, bevel=0)
    char.box((.05, 1.1, .05), loc=(-.95, .8, .02), rot=(0, 0, .2), bevel=0)
    _centre(a)


# ----------------------------------------------------------------------------- artillery_wreck
def artillery_wreck(a):
    """Destroyed 152 mm towed howitzer (3.0 x 6.0 m, 1.9 m), the artillery_emplacement's gun after a hit:
    the tube is split at the muzzle into four peeled petals and the muzzle brake lies in front; the right
    wheel is off (lying flat beside it), so the carriage rests on the axle stub, tipped over onto the left
    rim and one spade. The right trail is snapped (its end on the ground), the right half of the shield
    blown off, the left half holed; spent cases and a smashed crate. Blocks movement and fire."""
    before = set(a.shapes)
    char = a.part('Gun_carriage', 'Charred')
    rust = a.part('Gun_rust', 'Rust')
    soot = a.part('Gun_soot', 'Undercarriage')
    z9 = .09
    for s in (-1, 1):
        a0, a1 = Vector((s * .3, .45, .5 + z9)), Vector((s * 1.02, 1.78, .2 + z9))
        if s < 0:
            char.limb(tuple(a0), tuple(a1), .22, .26, bevel=.03)
            char.limb(tuple(a1 + Vector((0, 0, .02))), (s * 1.1, 1.98, .06 + z9), .28, .28, bevel=.02)
            char.box((.56, .08, .5), loc=(s * 1.14, 2.06, .24 + z9), rot=(-.3, 0, -s * .5), bevel=.02, seg=1)
        else:
            mid = a0.lerp(a1, .45)
            char.limb(tuple(a0), tuple(mid), .22, .26, bevel=.03)
            rust.limb(tuple(mid - (a1 - a0) * .02), tuple(mid + (a1 - a0) * .06 + Vector((0, 0, .05))), .16, .18,
                      bevel=0, taper=(.4, .6))
    char.box((1.9, .5, .3), loc=(0, .15, .62 + z9), bevel=.03, seg=1)
    rust.cyl(.08, 2.4, loc=(0, .15, .56 + z9), rot=ACROSS, seg=8, bevel=0)                # axle, right stub bare
    rust.cyl(.36, .3, loc=(-1.18, .15, .56 + z9), rot=ACROSS, seg=12, bevel=.02, bseg=1)  # left rim, tyre burnt
    soot.cyl(.14, .36, loc=(-1.18, .15, .56 + z9), rot=ACROSS, seg=8, bevel=0)
    char.cyl(.36, .12, loc=(0, .1, .77 + z9), seg=14, bevel=.02, bseg=1)
    zt = 1.2 + z9
    for s in (-1, 1):
        char.box((.1, .95, .62), loc=(s * .36, .28, .98 + z9), bevel=.03, seg=1, taper=(1, .55), shift=(0, -.12))
        rust.cyl(.11, .14, loc=(s * .44, .15, zt), rot=ACROSS, seg=10, bevel=0)
    char.limb((-.52, .7, .78 + z9), (-.52, .3, zt + .3), .11, .11, bevel=.01)
    char.limb((.52, .7, .78 + z9), (.52, .55, .98 + z9), .11, .11, bevel=.01)             # snapped equilibrator
    # Left half of the shield (holed and bent back), apron.
    char.box((.95, .07, .82), loc=(-.66, -.56, 1.3 + z9), rot=(-.22, 0, .08), bevel=.02, seg=1, taper=(.94, 1))
    char.box((.5, .07, .66), loc=(-1.28, -.36, 1.24 + z9), rot=(-.3, 0, -.85), bevel=.02, seg=1)
    char.box((1.9, .06, .3), loc=(0, -.5, .56 + z9), rot=(.12, 0, .05), bevel=.015, seg=1)
    fm = _basis((-.66, -.56, 1.3 + z9), (math.cos(.08), math.sin(.08), 0), (0, -math.cos(.22), math.sin(.22)))
    for off, r, seed in (((-.2, .15), .1, 41), ((.22, -.1), .07, 42), ((.05, .3), .06, 43)):
        _blotch(soot, fm @ _frame((off[0], off[1], .04), (0, 0, 0)), r, seed, sides=6, depth=.04)
    rust.box((.24, .12, .18), loc=(-.62, -.66, 1.78 + z9), rot=(0, .3, 0), bevel=.02, seg=1)
    # Cradle, recuperators, open breech and the split tube.
    p = math.radians(8)
    f, u = Vector((0, -math.cos(p), math.sin(p))), Vector((0, math.sin(p), math.cos(p)))
    o = Vector((0, .15, zt))

    def at(dist, up=0.0):
        return o + f * dist + u * up
    char.box((.4, 1.7, .34), loc=at(.2), rot=(-p, 0, 0), bevel=.04, seg=1)
    char.cyl(.085, 1.6, loc=at(.35, .25), rot=(R90 - p, 0, 0), seg=10, bevel=.01, bseg=1)
    rust.cyl(.085, .7, loc=at(-.1, -.23), rot=(R90 - p, 0, 0), seg=10, bevel=0)           # broken recuperator
    rust.cyl(.07, .3, loc=at(.35, -.23), rot=(R90 - p + .3, 0, .2), seg=8, bevel=0)
    char.box((.38, .5, .38), loc=at(-.8), rot=(-p, 0, 0), bevel=.03, seg=1)
    soot.box((.24, .06, .24), loc=at(-1.06), rot=(-p, 0, 0), bevel=0)
    tube = a.part('Gun_tube', 'Charred')
    t0, t1 = 1.05, 3.25
    tube.cyl(.1, t1 - t0, loc=at((t0 + t1) / 2), rot=(R90 - p, 0, 0), seg=12, bevel=0)
    tube.cyl(.14, .3, loc=at(1.3), rot=(R90 - p, 0, 0), seg=12, bevel=0)                 # sleeve collar
    rust.box((.025, .5, .03), loc=at(t1 - .32, .1), rot=(-p, 0, 0), bevel=0)            # crack
    side = Vector((1, 0, 0))
    for k, length in enumerate((.8, .6, .75, .5)):
        phi = k * TAU / 4 + .45
        radial = side * math.cos(phi) + u * math.sin(phi)
        across = side * -math.sin(phi) + u * math.cos(phi)
        spec = []
        for i in range(5):
            t = i / 4
            dist = t1 - .03 + length * t - .12 * t ** 3
            rho = .085 + .4 * length * t * t
            normal = radial - f * (.9 * t)
            spec.append((at(dist) + radial * rho, across, normal, 1.0 - .75 * t))
        _strip(rust, spec, .15, .025)
    gun = set(a.shapes) - before
    _rest(a, gun, [(-1.18, .15, .56 + z9 - .36), (1.2, .15, .56 + z9 - .08), (-1.22, 2.1, z9 + .01)])
    # On the ground: right wheel, shield half, trail end, muzzle brake, spent cases, smashed crate.
    char.cyl(.55, .3, loc=(1.0, -1.25, .13), rot=(.06, -.04, 0), seg=14, bevel=.06, bseg=1)
    rust.cyl(.34, .33, loc=(1.0, -1.25, .135), rot=(.06, -.04, 0), seg=12, bevel=0)
    char.box((.95, .82, .07), loc=(.85, .55, .06), rot=(.1, -.08, .4), bevel=.02, seg=1, taper=(.94, 1))
    char.limb((.95, 1.35, .14), (1.2, 2.1, .12), .22, .26, bevel=.03)
    char.box((.56, .5, .08), loc=(1.25, 2.3, .06), rot=(.1, 0, .3), bevel=.02, seg=1)
    char.cyl(.14, .5, loc=(-.75, -3.3, .15), rot=(0, R90, .5), seg=10, bevel=0)
    for dx in (-.14, .14):
        char.box((.15, .34, .3), loc=(-.75 + dx * math.cos(.5), -3.3 + dx * math.sin(.5), .16), rot=(0, 0, .5),
                 bevel=.015, seg=1)
    for x, y, yaw in ((.3, -2.7, .3), (.75, -2.25, 1.2), (-.9, 1.1, 2.0)):
        a.part('Cases', 'Gilded').cyl(.075, .44, loc=(x, y, .075), rot=(0, R90, yaw), seg=6, bevel=0)
    char.shell([(-.5, -.23), (.5, -.23), (.5, .23), (-.5, .23)], .3, .03, loc=(-.95, -1.6, 0), rot=(0, 0, .6),
               floor=.03)
    shells(a, (-.95, -1.6, .03), 2, 1, r=.07, h=.6, pitch=.2, yaw=.6)
    _centre(a)


# name: (builder, Asset options)
BUILDERS = {
    'wreck_tank': (wreck_tank, dict(ao_distance=.8, grime_height=.5)),
    'wreck_truck': (wreck_truck, dict(ao_distance=.8, grime_height=.5)),
    'wreck_car': (wreck_car, dict(ao_distance=.6, grime_height=.4)),
    'artillery_wreck': (artillery_wreck, dict(ao_distance=.7, grime_height=.4)),
    'trench_straight': (trench_straight, dict(ao_distance=.6, grime_height=.3)),
    'trench_corner': (trench_corner, dict(ao_distance=.6, grime_height=.3)),
    'foxhole': (foxhole, dict(ao_distance=.6, grime_height=.3)),
    'crater_large': (crater_large, dict(ao_distance=1.2, grime_height=.3)),
    'tank_ditch': (tank_ditch, dict(ao_distance=1.2, grime_height=.4)),
    'command_tent': (command_tent, dict(ao_distance=.9, grime_height=.4)),
    'camo_net': (camo_net, dict(ao_distance=.8, grime_height=.4)),
    'supply_pile': (supply_pile, dict(ao_distance=.6, grime_height=.3)),
    'fuel_bladder': (fuel_bladder, dict(ao_distance=.7, grime_height=.3)),
    'checkpoint': (checkpoint, dict(ao_distance=.7, grime_height=.4)),
    'barricade': (barricade, dict(ao_distance=.6, grime_height=.3)),
    'power_pylon': (power_pylon, dict(ao_distance=.8, ao_strength=.7, grime_height=.6)),
    'telegraph_pole': (telegraph_pole, dict(ao_distance=.4, grime_height=.4)),
    'radio_mast': (radio_mast, dict(ao_distance=.5, ao_strength=.7, grime_height=.4)),
    'bridge_road': (bridge_road, dict(ao_distance=1.2, grime_height=.6)),
    'ruin_house': (ruin_house, dict(ao_distance=1.2, grime_height=.6)),
    'ruin_tower': (ruin_tower, dict(ao_distance=1.2, grime_height=.8)),
    'dead_tree': (dead_tree, dict(ao_distance=.8, grime_height=.5)),
}
