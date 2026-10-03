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
- headquarters: the fortified camp HQ on its 14 x 12 m plinth (the footprint kept exactly: the prompt 32 HQ types
  use this model): a two-storey battered cast block with buttresses, pour lines, slit windows under visors and
  the Team fascia; the hardened entrance portal with the hazard-framed blast door, the sandbag chicane, HESCO and
  jersey barriers, the flag; the corner bastion tower with the first twin 30 mm in its sandbag ring; on the roof
  the gun drum and the twin heavy gun turret (blast bags, long barrels with brakes, the coax, the cupola), and a
  second twin 30 mm nest (the data's second hq_flak gets its own Mount_mg.001); the signals wing with the
  helipad on its roof; the yard with the lattice radar tower (Radar), the generator set, drums and HESCO.

Metres, +Z up, -Y front, +X left (the old models' extents and orientation).
"""
import math
import random

from mathutils import Matrix, Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w5parts as W

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


# ============================================================================= headquarters
HQ_X0, HQ_X1, HQ_Y0, HQ_Y1, HQ_ROOF = -6.0, 1.2, -3.0, 5.0, 5.4      # the main block (the old file's)
HQ_GUN = (-2.3, -.9)                                                    # the turret drum (old Turret pivot)
HQ_Z0 = .22                                                             # the plinth top
HQ_GT = (2.3, 4.75, 6.2)                       # prompt 35: the fortress gun tower (centre, deck height), rear right


def headquarters(a):
    """See the module docstring (headquarters). The footprint is the old file's exactly: the 14 x 12 m plinth;
    the HQ types (prompt 32: fortress ground / air, garrison, shield) use this model as it is. Runtime: Turret,
    Main_cannon / Main_cannon_2, Muzzle_brake / _2, Muzzle_main / .001 (mb_p34_barrels adds Muzzle_b1 / b2_main),
    Muzzle_coax, Radar (the yard tower's dish), Mount_mg / Muzzle_mg (the bastion tower's twin 30 mm) and
    Mount_mg.001 / Muzzle_mg.001 (the second twin 30 mm, on the main roof's front left corner), Mount_gun /
    Muzzle_gun (prompt 35: the fortress types' `gun` slot, the 120 mm L/55 on the gun tower at the rear right)."""
    K.suffixed(a)
    rng = random.Random(3510)
    k.extrude(a.part('Plinth', 'Concrete'), [(-7.0, -6.0), (7.0, -6.0), (7.0, 6.0), (-7.0, 6.0)], .26,
              loc=(0, 0, .09), axis='Z', chamfer=.04, corner=.8)
    joints = a.part('Plinth_joints', 'Undercarriage')
    for x in (-3.5, 0, 3.5):
        joints.box((.03, 11.8, .012), loc=(x, 0, .225), bevel=0)
    for y in (-3.0, 3.0):
        joints.box((13.8, .03, .012), loc=(0, y, .225), bevel=0)
    _hq_block(a)
    _hq_front(a, rng)
    _hq_tower(a, rng)
    _hq_roof(a)
    _hq_wing(a)
    _hq_yard(a)
    _hq_turret(a)
    _hq_gun_tower(a)
    k.clean(a)


def _hq_slit(a, x, y, z, w, facing, lit=True, shutter=False):
    """An armoured slit window in a wall facing `facing` ('-y', '+y', '-x', '+x'): the dark or lit pane, the frame,
    the visor hood above, a Team shutter half drawn when `shutter`."""
    ax = facing[1]
    s = 1 if facing[0] == '+' else -1
    if ax == 'y':
        size, off = (w, .04, .32), (0, s * .03, 0)
        hood, hoff = (w + .2, .3, .06), (0, s * .15, .2)
    else:
        size, off = (.04, w, .32), (s * .03, 0, 0)
        hood, hoff = (.3, w + .2, .06), (s * .15, 0, .2)
    a.part('Lit_windows' if lit else 'Windows', 'Lamp' if lit else 'Glass').box(
        size, loc=(x + off[0], y + off[1], z), bevel=0)
    fs = (size[0] + .12, size[1] + .02, size[2] + .12) if ax == 'y' else (size[0] + .02, size[1] + .12, size[2] + .12)
    a.part('Window_frames', 'Armor').box(fs, loc=(x + off[0] * .6, y + off[1] * .6, z), bevel=0)
    a.part('Window_visors', 'Armor').box(hood, loc=(x + hoff[0], y + hoff[1], z + hoff[2]), rot=(0, 0, 0), bevel=0)
    if shutter:
        sh = (size[0] * .55, .03, size[2] + .04) if ax == 'y' else (.03, size[1] * .55, size[2] + .04)
        sx = (-w * .22, s * .07, 0) if ax == 'y' else (s * .07, -w * .22, 0)
        a.part('Shutters', 'Team').box(sh, loc=(x + sx[0], y + sx[1], z), bevel=0)


def _hq_block(a):
    """The two-storey command block: battered cast walls (the second pour stepped in), corner buttresses, the pour
    lines, the Team fascia and floor bands, the slit windows with visors, the parapet and coping, the rear door."""
    x0, x1, y0, y1, roof = HQ_X0, HQ_X1, HQ_Y0, HQ_Y1, HQ_ROOF
    xc, yc = (x0 + x1) / 2, (y0 + y1) / 2
    blk = a.part('Block', 'Concrete')
    k.block(blk, (x1 - x0, y1 - y0, 2.6), loc=(xc, yc, HQ_Z0 + 1.3), chamfer=.06, taper=(.985, .985))
    k.block(blk, (x1 - x0 - .12, y1 - y0 - .12, roof - HQ_Z0 - 2.6), loc=(xc, yc, (HQ_Z0 + 2.6 + roof) / 2), chamfer=.06,
            taper=(.985, .985))
    for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        k.block(a.part('Buttresses', 'Concrete'), (.7, .7, roof - HQ_Z0 - .6), loc=(cx, cy, (roof - .6 + HQ_Z0) / 2), chamfer=.05,
                taper=(.75, .75))
    lines = a.part('Pour_lines', 'Undercarriage')
    for z in (1.4, 2.82, 4.1):
        for (px, py, lx, ly) in ((xc, y0 - .005, x1 - x0 - .8, .02), (xc, y1 + .005, x1 - x0 - .8, .02),
                                 (x0 - .005, yc, .02, y1 - y0 - .8)):
            lines.box((lx, ly, .025), loc=(px, py, z), bevel=0)
    team = a.part('Fascia', 'Team')
    team.shell([(x0 - .04, y0 - .04), (x1 + .04, y0 - .04), (x1 + .04, y1 + .04), (x0 - .04, y1 + .04)], .45, .08,
               loc=(0, 0, roof - .55))
    team.shell([(x0 - .03, y0 - .03), (x1 + .03, y0 - .03), (x1 + .03, y1 + .03), (x0 - .03, y1 + .03)], .2, .06,
               loc=(0, 0, 2.72))
    par = a.part('Parapet', 'Concrete')
    for (px, py, lx, ly) in ((xc, y0 + .15, x1 - x0, .3), (xc, y1 - .15, x1 - x0, .3), (x0 + .15, yc, .3, y1 - y0),
                             (x1 - .15, yc, .3, y1 - y0)):
        k.block(par, (lx, ly, .62), loc=(px, py, roof + .31), chamfer=.03)
    cop = a.part('Coping', 'Team')
    for (px, py, lx, ly) in ((xc, y0 + .15, x1 - x0 + .04, .36), (xc, y1 - .15, x1 - x0 + .04, .36),
                             (x0 + .15, yc, .36, y1 - y0), (x1 - .15, yc, .36, y1 - y0)):
        cop.box((lx, ly, .07), loc=(px, py, roof + .655), bevel=0)
    a.part('Roof_deck', 'Asphalt').box((x1 - x0 - .6, y1 - y0 - .6, .05), loc=(xc, yc, roof + .005), bevel=0)
    for i, x in enumerate((-5.1, -4.0, -.8, .3)):
        _hq_slit(a, x, y0, 1.7, .8, '-y', lit=i % 2 == 0, shutter=i == 1)
    for i, x in enumerate((-5.1, -3.9, -.9, .3)):
        _hq_slit(a, x, y0 + .06, 4.1, .8, '-y', lit=i != 2, shutter=i in (0, 3))
    for i, y in enumerate((-1.8, .2, 2.2)):
        _hq_slit(a, x0, y, 1.7, .9, '-x', lit=i == 1, shutter=i == 2)
        _hq_slit(a, x0 + .06, y, 4.1, .9, '-x', lit=i != 1)
    for i, x in enumerate((-3.4, -1.9, -.4)):
        _hq_slit(a, x, y1 - .06, 4.1, .8, '+y', lit=i == 1, shutter=i == 0)
    for i, y in enumerate((-2.0, -.4, 1.2, 2.9)):
        _hq_slit(a, x1 - .06, y, 4.3, .8, '+x', lit=i % 2 == 1)
    K.door(a, (-.2, y1 + .01, HQ_Z0), size=(1.3, 2.1), normal=(0, 1, 0), mat='Armor', frame_mat='Steel')
    a.part('Steps', 'Concrete').box((1.8, .5, .12), loc=(-.2, y1 + .25, HQ_Z0 + .05), bevel=0)
    K.lamp(a, (-.2, y1 + .05, 2.75), (0, 1, 0), r=.08, guard=True)


def _hq_front(a, rng):
    """The front: the hardened entrance portal with its canopy slab, the hazard-framed blast door, the sign band
    and caged lamps; the sandbag chicane, HESCO runs and jersey barriers; the Team flag at the front left; the
    corner floodlights."""
    px, y0 = HQ_GUN[0], HQ_Y0
    portal = a.part('Portal', 'Concrete')
    k.block(portal, (3.2, 1.4, 3.0), loc=(px, y0 - .68, HQ_Z0 + 1.5), chamfer=.08, taper=(.97, .97))
    k.block(portal, (3.6, 1.8, .3), loc=(px, y0 - .78, HQ_Z0 + 3.1), chamfer=.05)
    fy = y0 - 1.38
    K.door(a, (px, fy - .01, HQ_Z0), size=(1.7, 2.2), normal=(0, -1, 0), mat='Armor', frame_mat='Steel')
    a.part('Blast_door', 'Armor').box((1.7, .06, 2.2), loc=(px, fy + .03, HQ_Z0 + 1.1), bevel=0)
    for i in range(6):
        a.part('Door_hazard', 'SafetyStripe' if i % 2 else 'Charred').box((.14, .04, .3), loc=(px - 1.0, fy - .02,
                                                                                               .5 + i * .32), bevel=0)
        a.part('Door_hazard', 'SafetyStripe' if i % 2 == 0 else 'Charred').box((.14, .04, .3), loc=(px + 1.0, fy - .02,
                                                                                                    .5 + i * .32),
                                                                               bevel=0)
    a.part('Sign', 'Team').box((2.4, .05, .3), loc=(px, fy - .03, 2.95), bevel=0)
    for s in (-1, 1):
        K.lamp(a, (px + s * 1.35, fy - .02, 2.25), (0, -1, 0), r=.08, guard=True)
    K.sandbag_run(a, [(px - 1.5, -5.25, HQ_Z0), (px + 1.0, -5.25, HQ_Z0)], courses=3, bag=(.6, .32, .2),
                  part='Sandbags', seed=3)
    K.sandbag_run(a, [(px + 1.0, -5.25, HQ_Z0), (px + 1.0, -4.6, HQ_Z0)], courses=3, bag=(.6, .32, .2),
                  part='Sandbags', seed=4)
    K.hesco(a, (-5.4, -5.1, HQ_Z0), cells=2)
    K.hesco(a, (.25, -5.1, HQ_Z0), cells=2)
    for x in (1.9, 3.7, 5.5):
        k.extrude(a.part('Barriers', 'Concrete'), [(-.3, 0), (.3, 0), (.12, .25), (.1, .8), (-.1, .8), (-.12, .25)],
                  1.7, loc=(x, -5.4, HQ_Z0), axis='X', chamfer=.03)
        a.part('Barrier_bands', 'SafetyStripe').box((1.6, .02, .12), loc=(x, -5.53, HQ_Z0 + .5), rot=(.22, 0, 0),
                                                    bevel=0)
    # The flag at the front left, flying forward, its obstruction light.
    a.part('Flag_pole', 'Steel').cyl(.05, 8.0, loc=(-6.6, -4.9, HQ_Z0 + 4.0), seg=8, bevel=0)
    flag = a.part('Flag', 'Team')
    verts, faces = [], []
    for i in range(6):
        f = i / 5
        y = -4.95 - f * 1.75
        dz = .08 * math.sin(f * 4.2)
        dx = .06 * math.sin(f * 3.1 + .5)
        verts += [(-6.6 + dx, y, HQ_Z0 + 7.85 + dz), (-6.6 + dx, y, HQ_Z0 + 6.75 + dz)]
    for i in range(5):
        q = i * 2
        faces += [(q, q + 1, q + 3, q + 2)]
    flag.mesh(verts, faces)
    flag.mesh([(x + .01, y, z) for x, y, z in verts], [tuple(reversed(f)) for f in faces])
    a.part('Obstruction_lights', 'LavaGlow').sphere(.08, loc=(-6.6, -4.9, HQ_Z0 + 8.1), seg=6, rings=4)
    for x, yaw in ((HQ_X0 + .4, -.5), (HQ_X1 - .4, .5)):
        a.part('Flood_brackets', 'Steel').box((.1, .5, .1), loc=(x, HQ_Y0 - .22, 4.95), bevel=0)
        k.block(a.part('Floodlights_housing', 'Armor'), (.5, .26, .36), loc=(x, HQ_Y0 - .55, 4.8),
                rot=(.5, 0, yaw), chamfer=.03)
        a.part('Floodlights_lens', 'Lamp').box((.42, .02, .28), loc=(x, HQ_Y0 - .69, 4.92), rot=(.5, 0, yaw),
                                               bevel=0)


def _hq_flak(a, index, loc, muzzle):
    """A twin 30 mm flak mount (2A38 class) on its yaw pivot Mount_mg[.NNN]: the carriage with its seat and sight,
    the shield, the two barrels with their jackets and flash hiders, the ammunition boxes; Muzzle_mg[.NNN] between
    the barrels at `muzzle` (pivot frame)."""
    tag = '' if index == 0 else f'__{index:03d}'
    m = a.pivot(K.name('Mount_mg', index), loc)
    k.lathe(a.part(f'Flak_carriage{tag}', 'Armor', m), [(.55, 0), (.55, .08), (.42, .14), (.38, .3)], seg=12)
    K.chamfer_box(a.part(f'Flak_carriage{tag}', 'Armor', m), (.7, .9, .35), loc=(0, .1, .45), c=.04)
    k.block(a.part(f'Flak_shield{tag}', 'Team', m), (1.1, .06, .55), loc=(0, -.45, .4), rot=(-.2, 0, 0), chamfer=.015)
    mx, my, mz = muzzle
    for dx in (-.2, .2):
        bl = a.part(f'Flak_barrel{tag}', 'Steel', m)
        k.lathe(bl, [(.05, 0), (.05, .3), (.035, .33), (.035, abs(my) - .25), (.05, abs(my) - .22),
                     (.05, abs(my) - .02), (0, abs(my))], loc=(mx + dx, 0, mz), rot=K.FORWARD, seg=8)
        K.chamfer_box(a.part(f'Flak_ammo{tag}', 'Crate', m), (.18, .45, .3), loc=(mx + dx * 2.4, .25, mz - .05),
                      c=.02)
    K.chamfer_box(a.part(f'Flak_sight{tag}', 'Armor', m), (.16, .2, .18), loc=(-.4, -.1, .75), c=.02)
    a.part(f'Flak_sight_glass{tag}', 'Glass', m).box((.1, .01, .08), loc=(-.4, -.205, .77), bevel=0)
    a.part(f'Flak_steel{tag}', 'Steel', m).box((.3, .3, .05), loc=(.35, .35, .5), bevel=0)    # the layer's seat
    a.pivot(K.name('Muzzle_mg', index), muzzle, m)
    return m


def _hq_tower(a, rng):
    """The corner bastion tower at the rear left: a battered concrete prism with the Team band and loopholes, the
    asphalt deck, the sandbag ring on the three sides away from the main gun, the first twin 30 mm, the ladder."""
    fx, fy, tz, tw = -5.35, 4.25, 6.3, 2.6
    k.extrude(a.part('Block', 'Concrete'), [(-tw / 2, -tw / 2), (tw / 2, -tw / 2), (tw / 2, tw / 2),
                                            (-tw / 2, tw / 2)], tz - HQ_Z0, loc=(fx, fy, (tz + HQ_Z0) / 2),
              axis='Z', chamfer=.08, corner=.5, taper=(.93, .93))
    a.part('Fascia', 'Team').shell([(fx - tw / 2 + .02, fy - tw / 2 + .02), (fx + tw / 2 - .02, fy - tw / 2 + .02),
                                    (fx + tw / 2 - .02, fy + tw / 2 - .02), (fx - tw / 2 + .02, fy + tw / 2 - .02)],
                                   .35, .08, loc=(0, 0, tz - .6))
    for y in (3.7, 4.6):
        _hq_slit(a, fx - tw / 2 + .08, y, 2.4, .5, '-x', lit=y > 4)
    _hq_slit(a, fx, fy + tw / 2 - .08, 2.4, .6, '+y', lit=False)
    a.part('Tower_deck', 'Asphalt').box((tw - .3, tw - .3, .05), loc=(fx, fy, tz + .005), bevel=0)
    away = math.atan2(fy - HQ_GUN[1], fx - HQ_GUN[0])
    pts = [(fx + 1.15 * math.cos(away + u), fy + 1.15 * math.sin(away + u), tz) for u in
           [-1.9 + i * .38 for i in range(11)]]
    K.sandbag_run(a, pts, courses=2, bag=(.55, .32, .2), part='Blast_bags', mat='Sandbag', seed=5)
    _hq_flak(a, 0, (fx, fy, tz + .03), (.2, -2.25, .76))
    K.ladder(a.part('Ladder', 'Steel'), (fx + tw / 2 + .12, 4.9, HQ_ROOF), (fx + tw / 2 + .12, 4.9, tz + .5),
             width=.44, step=.3)


def _hq_roof(a):
    """The main roof: the gun drum with its hazard band and race, the second twin 30 mm in a sandbagged nest on the
    front left corner (under the gun's barrels), the roof hatch, vents, air conditioners, two whip masts with their
    beacons, the cable tray."""
    roof = HQ_ROOF
    gx, gy = HQ_GUN
    a.part('Drum', 'Concrete').cyl(2.15, .78, loc=(gx, gy, roof + .39), seg=28, bevel=.04, bseg=1)
    for i in range(28):
        u = (i + .5) * TAU / 28
        a.part('Drum_band', 'SafetyStripe' if i % 2 else 'Charred').box(
            (.46, .06, .16), loc=(gx + 2.16 * math.cos(u), gy + 2.16 * math.sin(u), roof + .6), rot=(0, 0, u + R90),
            bevel=0)
    a.part('Race', 'Steel').cyl(1.95, .08, loc=(gx, gy, roof + .81), seg=28, bevel=.02, bseg=1)
    # The second flak nest (Mount_mg.001): sandbags round three sides, the mount on its low pedestal.
    nx, ny = -5.05, -2.15
    K.sandbag_run(a, [(nx - .9, ny + .9, roof), (nx - .9, ny - .7, roof), (nx + .9, ny - .7, roof)], courses=2,
                  bag=(.55, .32, .18), part='Sandbags', seed=6)
    _hq_flak(a, 1, (nx, ny, roof + .05), (0, -1.9, .62))
    k.block(a.part('Hatches', 'Armor'), (.9, .9, .14), loc=(-.4, 3.8, roof + .07), chamfer=.03)
    a.part('Hatch_fittings', 'Steel').box((.9, .06, .06), loc=(-.4, 3.33, roof + .12), bevel=0)
    for x, y in ((-.2, 2.4), (-4.6, 1.0), (.4, -2.3)):
        a.part('Vents', 'Steel').cyl(.16, .5, loc=(x, y, roof + .25), seg=8, bevel=0)
        a.part('Vent_caps', 'Armor').cyl(.26, .07, loc=(x, y, roof + .5), r2=.16, seg=8, bevel=0)
    for x in (-2.4, -1.2):
        k.block(a.part('Aircon', 'Fuel'), (.8, .9, .5), loc=(x, 4.1, roof + .25), chamfer=.03)
        a.part('Aircon_fans', 'Rubber').cyl(.28, .03, loc=(x, 4.1, roof + .51), seg=12, bevel=0)
    # The masts stand on the rear parapet, clear of the three gun sweeps (prompt 35: the right one moved off the
    # gun tower's arc).
    for x, y, h in ((-2.0, 4.75, 3.2), (-2.9, 4.75, 2.4)):
        a.part('Antenna', 'Steel').cyl(.05, h, loc=(x, y, roof + .7 + h / 2), seg=6, bevel=0)
        a.part('Antenna', 'Steel').cyl(.12, .1, loc=(x, y, roof + .7), seg=8, bevel=0)
        for f in (.45, .8):
            a.part('Antenna', 'Steel').box((.5, .03, .03), loc=(x, y, roof + .7 + h * f), bevel=0)
        K.beacon(a, (x, y, roof + .7 + h), r=.06)
    a.part('Cable_tray', 'Steel').box((.3, 2.4, .08), loc=(.85, 3.4, roof + .1), bevel=0)
    a.part('Cables', 'Rubber').tube([(.85, 2.2, roof + .14), (.4, 1.6, roof + .14), (-.6, 1.4, roof + .3)], .04,
                                    seg=5)


def _hq_wing(a):
    """The signals wing on the right: the single-storey cast block with its band and slits, the side door, the
    ladder; the helipad on its roof (asphalt, Team border, white ring and H, edge lights, the windsock)."""
    wx0, wx1, wy0, wy1, wz = HQ_X1, 6.8, -4.6, 1.5, 3.4
    k.block(a.part('Wing', 'Concrete'), (wx1 - wx0, wy1 - wy0, wz - HQ_Z0), loc=((wx0 + wx1) / 2, (wy0 + wy1) / 2,
                                                                              (wz + HQ_Z0) / 2), chamfer=.06,
            taper=(.99, .99))
    a.part('Fascia', 'Team').shell([(wx0 + .06, wy0 - .04), (wx1 + .04, wy0 - .04), (wx1 + .04, wy1 + .04),
                                    (wx0 + .06, wy1 + .04)], .35, .08, loc=(0, 0, wz - .4))
    for (px, py, lx, ly) in (((wx0 + wx1) / 2, wy0 + .1, wx1 - wx0, .2), ((wx0 + wx1) / 2, wy1 - .1, wx1 - wx0, .2),
                             (wx1 - .1, (wy0 + wy1) / 2, .2, wy1 - wy0)):
        k.block(a.part('Parapet', 'Concrete'), (lx, ly, .3), loc=(px, py, wz + .15), chamfer=.02)
    for i, x in enumerate((2.2, 3.4, 4.6, 5.8)):
        _hq_slit(a, x, wy0, 1.6, .7, '-y', lit=i != 2, shutter=i == 3)
    for i, y in enumerate((-3.4, -1.9, -.4)):
        _hq_slit(a, wx1, y, 1.6, .7, '+x', lit=i == 1)
    K.door(a, (wx1 + .01, .7, HQ_Z0), size=(1.0, 2.1), normal=(1, 0, 0), mat='Armor', frame_mat='Steel')
    a.part('Side_door', 'Armor').box((.04, 1.2, .1), loc=(wx1 + .02, .7, HQ_Z0 + 2.25), bevel=0)
    K.lamp(a, (wx1 + .04, .7, 2.6), (1, 0, 0), r=.07, guard=True)
    a.part('Wall_lamp_base', 'Armor').box((.06, .2, .2), loc=(wx1 + .03, .7, 2.6), bevel=0)
    K.ladder(a.part('Ladder', 'Steel'), (5.9, wy1 + .3, HQ_Z0), (5.9, wy1 + .3, wz + .6), width=.44, step=.34)
    hx, hy, hs, hz = (wx0 + wx1) / 2 + .05, (wy0 + wy1) / 2, 5.0, wz + .02
    a.part('Pad', 'Asphalt').box((hs, hs, .05), loc=(hx, hy, hz), bevel=0)
    e, bw = hs / 2 - .2, .28
    team = a.part('Pad_border', 'Team')
    for s in (-1, 1):
        team.box((2 * e + bw, bw, .03), loc=(hx, hy + s * e, hz + .03), bevel=0)
        team.box((bw, 2 * e - bw, .03), loc=(hx + s * e, hy, hz + .03), bevel=0)
    paint = a.part('Pad_markings', 'PlasterWhite')
    k.ring(paint, [(1.75, 0), (1.95, 0), (1.95, .03), (1.75, .03)], loc=(hx, hy, hz + .012), seg=24)
    for s in (-1, 1):
        paint.box((.36, 1.9, .035), loc=(hx + s * .62, hy, hz + .042), bevel=0)
    paint.box((1.0, .34, .025), loc=(hx, hy, hz + .037), bevel=0)
    d = e + .02
    for lx, ly in [(hx + i * d, hy + j * d) for i in (-1, 0, 1) for j in (-1, 0, 1) if i or j]:
        a.part('Edge_light_bases', 'Armor').cyl(.09, .04, loc=(lx, ly, hz + .04), seg=6, bevel=0)
        a.part('Edge_lights', 'Lamp').cyl(.05, .05, loc=(lx, ly, hz + .08), seg=6, bevel=0)
    a.part('Windsock_pole', 'Steel').cyl(.04, 2.2, loc=(wx1 - .25, wy0 + .25, wz + 1.1), seg=6, bevel=0)
    a.part('Windsock', 'SafetyStripe').cyl(.16, .7, loc=(wx1 - .25, wy0 - .12, wz + 2.1), rot=(R90 - .3, 0, 0),
                                           r2=.09, seg=8, bevel=0)


def _hq_yard(a):
    """The yard behind the wing: the lattice radar tower on its footing with the platform and rail, the dish on its
    turntable (Radar spins), the generator set, the fuel drums, the cable run, HESCO along the right edge."""
    rx, ry = 4.4, 3.95
    k.block(a.part('Tower_footing', 'Concrete'), (1.8, 1.8, .3), loc=(rx, ry, HQ_Z0 + .1), chamfer=.04)
    tw = a.part('Radar_tower', 'Steel')
    b0, b1, z0, z1 = .75, .45, HQ_Z0 + .25, 6.2
    for sx in (-1, 1):
        for sy in (-1, 1):
            tw.tube([(rx + sx * b0, ry + sy * b0, z0), (rx + sx * b1, ry + sy * b1, z1)], .07, seg=4)
    for i in range(3):
        za, zb = z0 + (z1 - z0) * i / 3, z0 + (z1 - z0) * (i + 1) / 3
        wa, wb = b0 + (b1 - b0) * i / 3, b0 + (b1 - b0) * (i + 1) / 3
        for (ax_, ay_), (bx_, by_) in (((-1, -1), (1, -1)), ((1, -1), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, -1))):
            tw.tube([(rx + ax_ * wa, ry + ay_ * wa, za), (rx + bx_ * wb, ry + by_ * wb, zb)], .025, seg=4)
            tw.tube([(rx + ax_ * wb, ry + ay_ * wb, zb), (rx + bx_ * wb, ry + by_ * wb, zb)], .025, seg=4)
    k.block(a.part('Tower_platform', 'Armor'), (1.5, 1.5, .1), loc=(rx, ry, 6.25), chamfer=.02)
    K.railing(a.part('Tower_rail', 'Steel'), [(rx - .72, ry - .72, 6.3), (rx + .72, ry - .72, 6.3),
                                             (rx + .72, ry + .72, 6.3), (rx - .72, ry + .72, 6.3),
                                             (rx - .72, ry - .72, 6.3)], h=.4, post=1.45, r=.02)
    a.part('Dish_pedestal', 'Steel').cyl(.25, .35, loc=(rx, ry, 6.47), seg=10, bevel=0)
    r = a.pivot('Radar', (rx, ry, 6.64))
    a.part('Radar_turntable', 'Armor', r).cyl(.34, .1, loc=(0, 0, .05), seg=12, bevel=0)
    K.chamfer_box(a.part('Radar_frame', 'Steel', r), (.26, .26, .45), loc=(0, .08, .32), c=.02)
    K.dish(a.part('Radar_dish', 'Medical', r), a.part('Radar_horn', 'Armor', r), (0, .2, .75), r=.95,
           normal=(0, -.9, .45), seg=14)
    for sx in (-1, 1):
        a.part('Radar_frame', 'Steel', r).tube([(sx * .7, -.05, .55), (0, -.75, 1.15)], .03, seg=4)
    K.beacon(a, (rx + .6, ry + .6, 6.3), r=.07)
    # The generator set on its skid: the housing with louvres and doors, the exhaust, the panel, the stripe.
    # Prompt 35: the set moved forward between the wing and the gun tower, the drums behind the radar footing.
    gx, gy = 2.55, 2.62
    a.part('Generator_skid', 'Steel').box((1.2, 2.1, .12), loc=(gx, gy, HQ_Z0 + .06), bevel=0)
    K.chamfer_box(a.part('Generator', 'Fuel'), (1.0, 1.9, 1.1), loc=(gx, gy, HQ_Z0 + .67), c=.05)
    a.part('Generator_roof', 'Armor').box((1.06, 1.96, .06), loc=(gx, gy, HQ_Z0 + 1.25), bevel=0)
    for s in (-1, 1):
        K.grille(a, (gx + s * .51, gy - .4, HQ_Z0 + .8), .7, .45, facing=(s, 0, 0), slats=5, frame_mat='Armor')
        a.part('Generator_doors', 'Armor').box((.02, .6, .8), loc=(gx + s * .51, gy + .5, HQ_Z0 + .65), bevel=0)
    a.part('Generator_stripe', 'Hazard').box((1.02, 1.92, .08), loc=(gx, gy, HQ_Z0 + .25), bevel=0)
    a.part('Generator_panel', 'Armor').box((.4, .04, .5), loc=(gx, gy + .97, HQ_Z0 + .8), bevel=0)
    k.lathe(a.part('Generator_exhaust', 'Steel'), [(.07, 0), (.07, .5), (.09, .52), (.09, .6)],
            loc=(gx + .3, gy - .55, HQ_Z0 + 1.25), seg=8)
    K.soot(a, (gx + .3, gy - .55, HQ_Z0 + 1.85), radius=.35, k=.4)
    for x, y in ((3.95, 5.5), (4.55, 5.62), (5.15, 5.5)):
        K.fuel_drum(a.part('Drums', 'BarrelRed'), a.part('Drum_band', 'Steel'), (x, y, HQ_Z0), r=.28, h=.86)
    a.part('Cables', 'Rubber').tube([(2.05, 3.2, .5), (1.75, 3.25, .3), (1.45, 3.25, .3), (1.27, 3.25, .9)], .05,
                                    seg=5)
    for y in (2.55, 3.61, 4.67):
        K.hesco(a, (6.3, y, HQ_Z0), yaw=R90)


def _hq_turret(a):
    """The twin heavy gun turret on the drum (Turret): a faceted house with canvas blast bags round the two ports,
    the face plates, the long barrels with their sleeves, fume extractors and muzzle brakes (Main_cannon /
    Muzzle_brake left, Main_cannon_2 / Muzzle_brake_2 right), the ball-mounted coax between them, the sight hoods,
    the cupola with periscopes, hatches, the rear hoist door, stowage bins, antennas."""
    gx, gy = HQ_GUN
    t = a.pivot('Turret', (gx, gy, HQ_ROOF + .86))
    a.part('Turret_ring', 'Armor', t).cyl(1.85, .16, loc=(0, 0, .06), seg=24, bevel=0)
    W.poly_turret(a.part('Turret_body', 'Team', t), [
        (.12, [(-1.2, -1.75), (1.2, -1.75), (1.75, -1.0), (1.8, 1.3), (1.4, 1.9), (-1.4, 1.9), (-1.8, 1.3),
               (-1.75, -1.0)]),
        (.75, [(-1.15, -1.55), (1.15, -1.55), (1.7, -.9), (1.75, 1.3), (1.38, 1.88), (-1.38, 1.88), (-1.75, 1.3),
               (-1.7, -.9)]),
        (1.22, [(-.95, -1.05), (.95, -1.05), (1.5, -.62), (1.55, 1.2), (1.24, 1.75), (-1.24, 1.75), (-1.55, 1.2),
                (-1.5, -.62)])], chamfer=.05)
    zg = .62
    for x, nm, br in ((-.6, 'Main_cannon', 'Muzzle_brake'), (.6, 'Main_cannon_2', 'Muzzle_brake_2')):
        k.lathe(a.part('Blast_bags', 'Canvas', t), [(.36, 0), (.42, .08), (.38, .2), (.26, .3)],
                loc=(x, -1.62, zg), rot=K.FORWARD, seg=10)
        K.gun_barrel(a, nm, t, x, -1.85, zg, 3.21, .13, seg=12, extractor=(.42, 1.5, .55), brake_name=br,
                     brake='baffle')
    a.pivot('Muzzle_main', (.6, -5.36, zg), t)
    a.pivot('Muzzle_main__001', (-.6, -5.36, zg), t)
    k.block(a.part('Turret_armor', 'Armor', t), (.5, .12, .5), loc=(0, -1.6, zg + .1), rot=(-.58, 0, 0), chamfer=.02)
    k.lathe(a.part('Coax_mount', 'Armor', t), [(0, -.12), (.14, -.1), (.16, 0), (.14, .1), (0, .12)],
            loc=(0, -1.68, zg), seg=10)
    k.lathe(a.part('Coax', 'Steel', t), [(.025, 0), (.025, .36), (0, .37)], loc=(0, -1.7, zg), rot=K.FORWARD, seg=6)
    a.pivot('Muzzle_coax', (0, -2.06, zg), t)
    # Roof: sight hoods, the cupola with periscopes, a hatch, lifting eyes; the rear hoist door, bins.
    for x in (-1.0, 1.0):
        K.chamfer_box(a.part('Periscope_hoods', 'Armor', t), (.36, .3, .22), loc=(x, -.8, 1.3), c=.03)
        a.part('Sight_glass', 'Glass', t).box((.26, .01, .12), loc=(x, -.955, 1.32), bevel=0)
    k.ring(a.part('Cupola_top', 'Armor', t), [(.34, 0), (.4, 0), (.4, .2), (.34, .2)], loc=(.55, .6, 1.22), seg=12)
    for i in range(6):
        u = i * TAU / 6
        a.part('Periscope', 'Glass', t).box((.09, .015, .06), loc=(.55 + math.cos(u) * .41, .6 + math.sin(u) * .41,
                                                                    1.33), rot=(0, 0, u + R90), bevel=0)
    K.hatch_round(a, (-.6, .7, 1.22), r=.32, parent=t, periscopes=0, seg=10)
    a.part('Hatch_fittings', 'Steel', t).box((.5, .05, .05), loc=(-.6, .3, 1.26), bevel=0)
    k.block(a.part('Turret_steel', 'Steel', t), (1.1, .1, .8), loc=(0, 1.86, .6), chamfer=.02)
    for s in (-1, 1):
        K.crate(a.part('Stowage', 'Armor', t), a.part('Latches', 'Steel', t), (.18, 1.2, .5), (s * 1.82, .3, .12),
                bands=1)
        K.whip_antenna(a.part('Antenna', 'Steel', t), (s * 1.1, 1.5, 1.22), h=.9, lean=.15)
    a.part('Team_band', 'Team', t).box((1.6, .8, .012), loc=(0, .2, 1.225), bevel=0)


def _hq_gun_tower(a):
    """Prompt 35 (owner answer 2026-10-03): the fortress HQ types' `gun` slot gets its gun on the model. The HQ types
    swap the def, not the model, so one gun serves both: turret_gun_120_long (Rh-120 L/55, one barrel), the fortress
    ground type's (the default fortress branch). A second bastion tower at the rear right of the main block, in the
    first's style (battered cast prism, Team band, loopholes, a ladder up its back), carries the low casemate turret
    on its race: the faceted gun house on its yaw pivot Mount_gun, the mantlet, the long barrel with its sleeve, fume
    extractor and baffle brake, Muzzle_gun at the brake's face; sight hood, hatch, rear bin, whip.
    Placement: outside the main turret's barrel sweep (5.4 m), the gun's barrel above the radar platform's rail and
    the main roof's parapet, so the three guns and the radar turn all the way round clear of each other."""
    fx, fy, tz = HQ_GT
    tw = 2.0
    k.extrude(a.part('Block', 'Concrete'), [(-tw / 2, -tw / 2), (tw / 2, -tw / 2), (tw / 2, tw / 2),
                                            (-tw / 2, tw / 2)], tz - HQ_Z0, loc=(fx, fy, (tz + HQ_Z0) / 2),
              axis='Z', chamfer=.08, corner=.4, taper=(.93, .93))
    a.part('Fascia', 'Team').shell([(fx - tw / 2 + .03, fy - tw / 2 + .03), (fx + tw / 2 - .03, fy - tw / 2 + .03),
                                    (fx + tw / 2 - .03, fy + tw / 2 - .03), (fx - tw / 2 + .03, fy + tw / 2 - .03)],
                                   .35, .08, loc=(0, 0, tz - .62))
    lines = a.part('Pour_lines', 'Undercarriage')
    for z in (1.6, 3.2, 4.6):
        lines.box((tw - .5, .02, .025), loc=(fx, fy + tw / 2 - .02 - .035 * z / tz, z), bevel=0)
        lines.box((.02, tw - .5, .025), loc=(fx + tw / 2 - .02 - .035 * z / tz, fy, z), bevel=0)
    _hq_slit(a, fx, fy + tw / 2 - .06, 2.2, .5, '+y', lit=True)
    _hq_slit(a, fx, fy + tw / 2 - .1, 4.4, .5, '+y', lit=False, shutter=True)
    _hq_slit(a, fx + tw / 2 - .06, fy + .2, 2.2, .5, '+x', lit=False)
    _hq_slit(a, fx - .2, fy - tw / 2 + .1, 4.4, .5, '-y', lit=True)
    _hq_slit(a, fx + tw / 2 - .1, fy - .3, 5.1, .4, '+x', lit=True)
    top = tw * .93
    a.part('Tower_deck', 'Asphalt').box((top - .1, top - .1, .04), loc=(fx, fy, tz + .005), bevel=0)
    a.part('Coping', 'Team').shell([(fx - top / 2, fy - top / 2), (fx + top / 2, fy - top / 2),
                                    (fx + top / 2, fy + top / 2), (fx - top / 2, fy + top / 2)], .07, .06,
                                   loc=(0, 0, tz - .02))
    a.part('Race', 'Steel').cyl(.82, .1, loc=(fx, fy, tz + .05), seg=24, bevel=.015, bseg=1)
    for i in range(16):
        u = (i + .5) * TAU / 16
        a.part('Drum_band', 'SafetyStripe' if i % 2 else 'Charred').box(
            (.3, .03, .06), loc=(fx + .83 * math.cos(u), fy + .83 * math.sin(u), tz + .05), rot=(0, 0, u + R90),
            bevel=0)
    K.ladder(a.part('Ladder', 'Steel'), (fx - .35, fy + tw / 2 + .12, HQ_Z0), (fx - .35, fy + tw / 2 + .05, tz + .1),
             width=.44, step=.32)
    K.lamp(a, (fx + .45, fy + tw / 2 - .02, 2.9), (0, 1, 0), r=.07, guard=True)
    # The gun house on its yaw pivot: low and faceted, the front plate raked back, the sides and the rear bustle.
    m = a.pivot('Mount_gun', (fx, fy, tz + .1))
    a.part('Gun_ring', 'Armor', m).cyl(.8, .08, loc=(0, 0, .04), seg=20, bevel=0)
    W.poly_turret(a.part('Gun_house', 'Team', m), [
        (.08, [(-.6, -.86), (.6, -.86), (.8, -.45), (.8, .74), (.58, .92), (-.58, .92), (-.8, .74), (-.8, -.45)]),
        (.62, [(-.56, -.8), (.56, -.8), (.77, -.42), (.77, .74), (.56, .9), (-.56, .9), (-.77, .74), (-.77, -.42)]),
        (1.08, [(-.42, -.42), (.42, -.42), (.6, -.24), (.62, .7), (.46, .84), (-.46, .84), (-.62, .7),
                (-.6, -.24)])], chamfer=.04)
    zg = .8
    k.block(a.part('Gun_mantlet', 'Armor', m), (.62, .22, .5), loc=(0, -.86, zg), chamfer=.04, taper=(.85, .85))
    K.gun_barrel(a, 'Gun_barrel', m, 0, -.97, zg, 2.7, .1, seg=12, extractor=(.42, 1.5, .42), brake_name='Gun_brake',
                 brake='baffle')
    a.pivot('Muzzle_gun', (0, -.97 - 2.7 - .26, zg), m)
    for s in (-1, 1):
        k.block(a.part('Gun_armor', 'Armor', m), (.22, .08, .4), loc=(s * .45, -.78, .5), rot=(-.5, 0, 0),
                chamfer=.015)
    K.chamfer_box(a.part('Periscope_hoods', 'Armor', m), (.3, .26, .2), loc=(-.38, -.25, 1.17), c=.03)
    a.part('Sight_glass', 'Glass', m).box((.22, .01, .1), loc=(-.38, -.385, 1.19), bevel=0)
    K.hatch_round(a, (.25, .3, 1.08), r=.26, parent=m, periscopes=0, seg=10)
    K.crate(a.part('Stowage', 'Armor', m), a.part('Latches', 'Steel', m), (1.0, .18, .4), (0, .99, .45), bands=1)
    K.whip_antenna(a.part('Antenna', 'Steel', m), (-.45, .6, 1.08), h=.8, lean=.15)
    a.part('Team_band', 'Team', m).box((.9, .5, .012), loc=(0, .3, 1.085), bevel=0)


BUILDERS = {
    'dragons_teeth': (dragons_teeth, dict(ao_distance=.5, grime_height=.4, ao_strength=.6)),
    'dragons_teeth_a': (dragons_teeth_a, dict(ao_distance=.5, grime_height=.4, ao_strength=.45)),
    'headquarters': (headquarters, dict(ao_distance=1.2, grime_height=.8, ao_strength=.7)),
}
