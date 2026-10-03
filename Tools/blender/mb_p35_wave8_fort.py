"""Prompt 35 wave 8 (lane A): the base pieces rebuilt from scratch, each from its own spec
(Tools/blender/specs/<id>.json), on the kit35 library. DECISIONS "Prompt 35 wave 8 (lane A)".

- dragons_teeth: Westwall "Hoeckerhindernis" segment: two staggered rows of cast truncated pyramids (the back row
  taller) on a half-buried footing slab, each tooth with its casting lift line, chipped arrises and a stencilled
  number; one tooth broken to its rebar with the spall at its foot; a Czech hedgehog wedged in the front gap; moss,
  grass and stones at the bases, marker stakes with Team bands at the two ends. The rows repeat every 5 m along X
  (teeth 1.667 m apart, the rows half a pitch apart), so segments laid end to end continue the pattern.
- dragons_teeth_a (hedgehog branch): the same footing carrying three big Czech hedgehogs welded from rolled-steel
  angles with gusset plates and bolts, two small ones between them, the set chained together and to anchor stakes,
  rust bleeding onto the concrete.

Metres, +Z up, -Y front, +X left (the old models' extents and orientation).
"""
import math
import random

from mathutils import Matrix, Vector

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau


# ============================================================================= shared pieces of the segment
def _footing(a, rng, seed, plinths=()):
    """The half-buried foundation: a cast spine strip along the line, a square plinth under each tooth or
    hedgehog (`plinths` = [(x, y, size)]) standing out of it front and back, the dug earth bed round them with a
    ragged edge (straight at the two ends, so segments meet), the shuttering joints, loose stones and grass."""
    k.extrude(a.part('Footing', 'Plaster'), [(-2.5, -.3), (2.5, -.3), (2.5, .34), (-2.5, .34)], .14,
              loc=(0, 0, 0), axis='Z', chamfer=.03, corner=.02)
    for x, y, b in plinths:
        k.block(a.part('Footing', 'Plaster'), (b, b, .16), loc=(x, y, -.05), chamfer=.03)
    # The earth bed: a low mound with a ragged outline (two jagged long edges, straight ends).
    n = 22
    front = [(-2.5 + 5 * i / n, -(.78 + (.2 if i % 2 else 0) + rng.uniform(-.1, .12))) for i in range(n + 1)]
    back = [(2.5 - 5 * i / n, .8 + (.22 if i % 2 else 0) + rng.uniform(-.1, .12)) for i in range(n + 1)]
    k.extrude(a.part('Footing_dirt', 'Dirt'), front + back, .1, loc=(0, 0, -.02), axis='Z', chamfer=.04,
              taper=(1, .9))
    joints = a.part('Footing_joints', 'Undercarriage')
    for x in (-1.667, 0.0, 1.667):
        joints.box((.02, .62, .012), loc=(x + .833, .02, .071), bevel=0)
    stones = a.part('Stones', 'Rock', flat=True)
    for i in range(16):
        sz = rng.uniform(.05, .12)
        x = rng.uniform(-2.4, 2.4)
        y = (1 if i % 2 else -1) * rng.uniform(.85, 1.12)
        stones.ico((sz, sz * .8, sz * .55), loc=(x, y, .02), sub=0, jitter=.35, seed=seed + i * 1.3)
    grass = a.part('Tufts', 'Grass', flat=True)
    for i in range(18):
        x = -2.4 + i * .28 + rng.uniform(-.08, .08)
        y = (1 if i % 2 else -1) * rng.uniform(.9, 1.12)
        _tuft(grass, (x, y, .03), rng.uniform(.14, .24), rng)
    return grass


def _tuft(part, loc, h, rng, blades=5):
    """A grass tuft: thin leaning blades (open triangles, two-sided) round a point."""
    x, y, z = loc
    verts, faces = [], []
    for b in range(blades):
        u = b * TAU / blades + rng.uniform(-.3, .3)
        lean = rng.uniform(.15, .45)
        w = .025
        cx, cy = math.cos(u), math.sin(u)
        base = len(verts)
        tip = (x + cx * h * lean, y + cy * h * lean, z + h * rng.uniform(.8, 1.1))
        tri = [(x - cy * w, y + cx * w, z), (x + cy * w, y - cx * w, z), tip]
        verts += tri + [(px + cx * .006, py + cy * .006, pz) for px, py, pz in tri]   # the back 6 mm behind
        faces += [(base, base + 1, base + 2), (base + 5, base + 4, base + 3)]
    part.mesh(verts, faces)


# ============================================================================= dragons_teeth
ROWS = ((-.42, (-2.083, -.417, 1.25), .86, .84), (.55, (-1.25, .417, 2.083), .94, 1.08))


def _tooth(a, teeth, lift, x, y, b, h, top, yaw, lean):
    """One cast tooth: a truncated pyramid with chamfered arrises on a short square plinth (the pour's first
    lift), the lift line where the second pour met it, and a capping slab."""
    rot = (lean[0], lean[1], yaw)
    k.block(teeth, (b + .08, b + .08, .14), loc=(x, y, .07), rot=rot, chamfer=.03)
    k.block(teeth, (b, b, h - .14), loc=(x, y, .14 + (h - .14) / 2), rot=rot, chamfer=.05, taper=(top, top),
            ends=(False, True))
    # The lift line: a thin band one third up, proud of the faces (mortar squeeze from the second pour).
    zl = .14 + (h - .14) * .38
    kk = 1 + (top - 1) * .38
    k.extrude(lift, [(-b * kk / 2 - .012, -b * kk / 2 - .012), (b * kk / 2 + .012, -b * kk / 2 - .012),
                     (b * kk / 2 + .012, b * kk / 2 + .012), (-b * kk / 2 - .012, b * kk / 2 + .012)], .035,
              loc=(x, y, zl), rot=rot, axis='Z')


def dragons_teeth(a):
    """See the module docstring. No runtime nodes (a static obstacle)."""
    rng = random.Random(3508)
    _footing(a, rng, 1.0, [(x, y, b + .26) for y, xs, b, _h in ROWS for x in xs])
    teeth = a.part('Teeth', 'Plaster')
    lift = a.part('Lift_lines', 'Plaster')
    chips = a.part('Rubble', 'Concrete', flat=True)
    for y, xs, b, h in ROWS:
        for x in xs:
            broken = (x, y) == (-1.25, .55)
            hh = .6 if broken else h + rng.uniform(-.05, .06)
            tp = (.62 if broken else .36) + rng.uniform(-.03, .03)
            px, py = x + rng.uniform(-.04, .04), y + rng.uniform(-.04, .04)
            yaw = rng.uniform(-.12, .12)
            _tooth(a, teeth, lift, px, py, b, hh, tp, yaw, (rng.uniform(-.02, .02), rng.uniform(-.02, .02)))
            if broken:
                # The snapped top: a jagged cap, rebar bent out of it, the spall lying at its foot.
                chips.ico((.3, .28, .1), loc=(px, py, hh + .02), sub=1, jitter=.4, seed=7.0)
                bar = a.part('Rebar', 'Rust')
                for dx, dy, rx, ry in ((-.12, .1, .35, .2), (.12, -.08, -.4, .1), (.05, .14, .15, -.45),
                                       (-.1, -.12, -.2, -.3)):
                    bar.cyl(.012, .34, loc=(px + dx, py + dy, hh + .14), rot=(rx, ry, 0), seg=4, bevel=0)
                for j, (dx, dy, s) in enumerate(((.62, -.25, .16), (.7, .2, .11), (-.58, -.38, .13), (.4, .56, .1),
                                                 (-.66, .3, .09), (.15, -.62, .08))):
                    chips.ico((s, s * .8, s * .55), loc=(px + dx, py + dy, .08), sub=0, jitter=.3, seed=j + 2.0)
            else:
                # Chipped arrises: two or three small spalls lying at the base, a broken corner piece.
                for j in range(2):
                    u = rng.uniform(0, TAU)
                    chips.ico((.07, .05, .04), loc=(px + math.cos(u) * (b * .62), py + math.sin(u) * (b * .62), .08),
                              sub=0, jitter=.3, seed=rng.uniform(0, 50))
    # Stencilled serial numbers on the front faces of the front row (white paint, faded).
    paint = a.part('Stencils', 'PlasterWhite')
    for x in (-2.083, -.417, 1.25):
        for j in range(3):
            paint.box((.05, .01, .09), loc=(x - .07 + j * .07, -.42 - .3, .42), rot=(-.24, 0, 0), bevel=0)
    # Moss on the shaded faces and at the foot of each tooth.
    moss = a.part('Moss', 'FoliageDark', flat=True)
    for j, (x, y, z) in enumerate(((-2.083, -.42, .3), (.417, .55, .45), (2.083, .55, .25), (1.25, -.42, .2),
                                   (-.417, -.42, .15), (-1.25, .55, .12))):
        moss.ico((.2, .12, .1), loc=(x + .26, y - .2, z), sub=1, jitter=.3, seed=j * 3.1)
    for j, (x, y) in enumerate(((-1.7, .0), (1.0, .1), (2.2, -.9), (-2.3, .95), (-.2, .95), (1.7, .95))):
        moss.ico((.22, .16, .03), loc=(x, y, .07), sub=1, jitter=.35, seed=j * 1.7)
    grass = a.part('Tufts', 'Grass', flat=True)
    for j in range(12):
        y, xs, b, _h = ROWS[j % 2]
        x = xs[j % 3] + rng.uniform(-.4, .4)
        _tuft(grass, (x, y + (b / 2 + .07) * (1 if j % 3 else -1), .07), rng.uniform(.12, .2), rng)
    _hedgehog(a, (.417, -.74, .07), .3, 1.3, 'Hedgehogs', 'Rust', 'Hedgehog_plates', bolts=False)
    # Marker stakes at the two ends (Team band, a white reflector).
    for x, y, yaw in ((2.38, 1.0, .3), (-2.38, -1.0, -.4)):
        rot = (.03, -.02, yaw)
        a.part('Stakes', 'Wood').box((.06, .06, 1.2), loc=(x, y, .6), rot=rot, bevel=0)
        k.block(a.part('Stake_bands', 'Team'), (.13, .13, .26), loc=(x, y, .94), rot=rot, chamfer=.03)
        k.block(a.part('Stake_bands', 'Team'), (.13, .13, .06), loc=(x, y, 1.2), rot=rot, chamfer=.02)
        a.part('Stake_reflectors', 'PlasterWhite').box((.075, .075, .06), loc=(x, y, .84), rot=rot, bevel=0)
    K.dust(a, (0, 0, -.6), radius=1.0, k=.1)
    k.clean(a)


def _hedgehog(a, loc, yaw, length, part, mat, plate, flange=.1, t=.022, bolts=True, plate_mat='Steel'):
    """A Czech hedgehog: three rolled angles crossed at right angles through one centre, standing on three ends
    (the cube diagonal vertical); the gusset plates at the crossing and, with bolts, the bolt heads through them.
    `yaw` turns it."""
    turn = Vector((1, 1, 1)).normalized().rotation_difference(Vector((0, 0, 1))).to_matrix()
    spin = Matrix.Rotation(yaw, 3, 'Z')
    c = Vector(loc) + Vector((0, 0, length / 2 / math.sqrt(3)))
    sh = a.part(part, mat)
    feet = []
    for axis in (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))):
        d = spin @ turn @ axis
        side = d.cross(Vector((0, 0, 1)))
        side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
        up = d.cross(side).normalized()
        rot = Matrix((side, up, d)).transposed().to_euler('XYZ')
        # The rolled angle: an L section (its heel on the axis) with the cut ends' edges chamfered (worn).
        prof = [(0, 0), (flange, 0), (flange, t), (t, t), (t, flange), (0, flange)]
        k.extrude(sh, [(x - t / 2, y - t / 2) for x, y in prof], length, loc=tuple(c), rot=rot, axis='Z',
                  chamfer=t * .8, ends=(True, True))
        for e in (-1, 1):
            end = c + d * e * length / 2
            if end.z < c.z:
                feet.append(end)
    pl = a.part(plate, plate_mat)
    pl.box((flange * 1.7, flange * 1.7, flange * 1.7), loc=tuple(c), rot=(.62, .62, yaw), bevel=0)
    if bolts:
        bt = a.part('Kit_bolts', 'Steel')
        for i in range(3):
            u = yaw + i * TAU / 3
            bt.cyl(.022, .05, loc=(c.x + math.cos(u) * .1, c.y + math.sin(u) * .1, c.z + .12), seg=6, bevel=0)
    return c, feet


# ============================================================================= dragons_teeth_a
def dragons_teeth_a(a):
    """See the module docstring. No runtime nodes (a static obstacle)."""
    rng = random.Random(3509)
    _footing(a, rng, 4.0, [(-1.67, -.08, .9), (0, 0, .9), (1.67, .08, .9), (-.83, .7, .55), (.83, -.7, .55)])
    centres = []
    for i, x in enumerate((-1.67, 0.0, 1.67)):
        c, _feet = _hedgehog(a, (x, .08 * (i - 1), .07), .35 + i * .9, 2.25, 'Hedgehogs', 'Rust', 'Hedgehog_plates',
                             flange=.16, t=.03)
        centres.append(c)
    for i, x in enumerate((-.83, .83)):
        _hedgehog(a, (x, .7 * (1 - 2 * i), .07), 1.2 + i, 1.2, 'Hedgehogs', 'Rust', 'Hedgehog_plates', flange=.11,
                  t=.024)
    # Base shoes: a welded steel shoe under each big hedgehog's feet, bolted to the slab.
    shoes = a.part('Shoes', 'Steel')
    bolts = a.part('Kit_bolts', 'Steel')
    for i, x in enumerate((-1.67, 0.0, 1.67)):
        yaw = .35 + i * .9
        for j in range(3):
            u = yaw + R90 + j * TAU / 3
            r = 2.25 / 2 * math.sqrt(2 / 3)
            fx, fy = x + math.cos(u) * r, .08 * (i - 1) + math.sin(u) * r
            if abs(fx) > 2.4 or abs(fy) > 1.05:
                continue
            shoes.box((.28, .28, .03), loc=(fx, fy, .085), rot=(0, 0, u), bevel=0)
            for q in range(2):
                v = u + q * math.pi + .78
                bolts.cyl(.018, .04, loc=(fx + math.cos(v) * .1, fy + math.sin(v) * .1, .1), seg=6, bevel=0)
    # The anchor chain: links looped from hedgehog to hedgehog, low, and down to an anchor stake at each end.
    links = a.part('Chain', 'Steel')
    pts = [(-2.35, .7, .12)] + [(c.x, c.y, .32) for c in centres] + [(2.35, -.7, .12)]
    for p0, p1 in zip(pts, pts[1:]):
        p0, p1 = Vector(p0), Vector(p1)
        n = max(4, int((p1 - p0).length / .11))
        for j in range(n):
            f = (j + .5) / n
            p = p0.lerp(p1, f) - Vector((0, 0, .18 * math.sin(math.pi * f)))
            d = (p1 - p0).normalized()
            yaw = math.atan2(d.y, d.x)
            links.box((.1, .022, .045 if j % 2 else .02), loc=tuple(p), rot=(R90 * (j % 2), 0, yaw), bevel=0)
    for x, y in ((-2.35, .7), (2.35, -.7)):
        a.part('Anchor_stakes', 'Rust').cyl(.035, .5, loc=(x, y, .1), rot=(.2, 0, 0), seg=6, bevel=0)
        k.block(a.part('Anchor_stakes', 'Steel'), (.16, .16, .08), loc=(x, y, .3), chamfer=.025)
    # Rust streaks bled onto the slab under each hedgehog, weld spatter at the shoes.
    stain = a.part('Rust_stains', 'Dirt')
    for i, x in enumerate((-1.67, 0.0, 1.67)):
        stain.box((.5, .35, .006), loc=(x + .1, .08 * (i - 1) - .1, .073), rot=(0, 0, .4 * i), bevel=0)
    grass = a.part('Tufts', 'Grass', flat=True)
    for j in range(10):
        _tuft(grass, (-2.2 + j * .48 + rng.uniform(-.1, .1), rng.uniform(-.7, .7), .07), rng.uniform(.12, .18), rng)
    moss = a.part('Moss', 'FoliageDark', flat=True)
    for j, (x, y) in enumerate(((-2.1, -.6), (-.9, .2), (.6, -.5), (2.2, .6), (1.2, .8))):
        moss.ico((.2, .15, .03), loc=(x, y, .07), sub=1, jitter=.35, seed=j * 2.3)
    for x, y, yaw in ((2.38, 1.0, .3), (-2.38, -1.0, -.4)):
        rot = (.03, -.02, yaw)
        a.part('Stakes', 'Wood').box((.06, .06, 1.2), loc=(x, y, .6), rot=rot, bevel=0)
        k.block(a.part('Stake_bands', 'Team'), (.13, .13, .26), loc=(x, y, .94), rot=rot, chamfer=.03)
        k.block(a.part('Stake_bands', 'Team'), (.13, .13, .06), loc=(x, y, 1.2), rot=rot, chamfer=.02)
        a.part('Stake_reflectors', 'PlasterWhite').box((.075, .075, .06), loc=(x, y, .84), rot=rot, bevel=0)
    K.dust(a, (0, 0, -.6), radius=1.0, k=.1)
    k.clean(a)


BUILDERS = {
    'dragons_teeth': (dragons_teeth, dict(ao_distance=.5, grime_height=.4, ao_strength=.6)),
    'dragons_teeth_a': (dragons_teeth_a, dict(ao_distance=.5, grime_height=.4, ao_strength=.45)),
}
