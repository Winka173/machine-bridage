"""Prompt 35 wave 9 (lane C): the Kronos boss rebuilt from scratch (spec: Tools/blender/specs/kronos.json).

Kronos, a giant bucket-wheel excavator turned war machine (unit_refs: Bagger 288; the old file's 48.6 x 16.2 x
16.1 m kept): four crawler units under the corners of the substructure (`Part_track_fl/fr/rl/rr`, each with its
belt, track plates, rollers and drive tumbler), the octagonal substructure with its stair towers and the big
slewing ring; the machine house on the ring (stepped walls, window bands, walkways with railings and ladders, the
team band); the operator's cab on the house's front (`Part_cab`); the lattice cutter boom reaching forward with its
conveyor (`Part_boom`) to the bucket wheel (`Part_wheel`: the rim, the spokes and eighteen toothed buckets, the
chute); the A-frame pylon on the house with its cable stays to the boom and to the counterweight boom at the rear,
the counterweight box and the discharge conveyor beyond it; on the house roof the armament: the twin 30 mm turret
(`Turret`, the def's main), the two 57 mm turrets (`Mount_gun`, `Mount_gun.001`) and the second 30 mm
(`Mount_gun.002`), the rocket pod at the rear (`Mount_rocket`); floodlights, beacons, hazard bands.

Runtime nodes kept: the old file's boss parts at their positions, `Turret` / `Muzzle_main`, `Mount_gun` /
`Muzzle_gun`, `Mount_rocket` / `Muzzle_rocket`; added `Mount_gun.001` / `.002` with their muzzles (the def's five
mountWeapons need five muzzles). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TAU = math.tau
RING_Z = 4.5         # top of the slewing ring
ROOF = 9.6           # the machine house roof (the guns' deck)
STEEL = 'CraneYellow'


def _crawler(a, name, x, y):
    """One crawler unit under its Part_track pivot: belt, plates, rollers, tumbler, frame."""
    p = a.pivot(name, (x, y, 0))
    L, H, W = 6.6, 2.3, 3.0
    pts = []
    for cy, cz, r in ((-L / 2 + 1.0, 1.0, 1.0), (L / 2 - 1.1, 1.1, 1.1), (0, .55, .55)):
        for i in range(16):
            u = i * TAU / 16
            pts.append((cy + r * math.cos(u), cz + r * math.sin(u)))
    import mb_vehicles as mv
    outline = mv._hull2d(pts)
    k.extrude(a.part('Tracks', 'Undercarriage', p), outline, W, loc=(0, 0, 0), axis='X', chamfer=0)
    links = a.part('Track_links', 'Undercarriage', p)
    for (py, pz), (ty, tz) in mv._perimeter(outline, .55, 0.0):
        k.block(links, (W + .08, .22, .1), loc=(0, py + tz * .03, pz - ty * .03), rot=(math.atan2(tz, ty), 0, 0),
                chamfer=0)
    for s in (-1, 1):
        fr = a.part('Crawler_frames', STEEL, p)
        k.extrude(fr, [(-L / 2 + .9, .7), (L / 2 - .9, .7), (L / 2 - 1.6, 1.9), (-L / 2 + 1.6, 1.9)], .25,
                  loc=(s * (W / 2 + .14), 0, 0), axis='X', chamfer=.03)
        for yy in (-1.6, -.5, .6, 1.7):
            k.lathe(a.part('Rollers', 'Steel', p), [(.35, -.1), (.35, .1)], loc=(s * (W / 2 + .3), yy, .55),
                    rot=(0, R90, 0), seg=8)
        k.lathe(a.part('Sprockets', 'Steel', p), [(.8, -.12), (.8, .12)], loc=(s * (W / 2 + .3), L / 2 - 1.1, 1.1),
                rot=(0, R90, 0), seg=10)
        a.part('Hazard_marks', 'Hazard', p).box((.03, 2.0, .3), loc=(s * (W / 2 + .28), 0, 1.6), bevel=0)
    k.block(a.part('Crawler_frames', STEEL, p), (2.0, 2.0, 1.0), loc=(0, 0, 2.6), chamfer=.08)


def _substructure(a):
    for name, x, y in (('Part_track_fl', 6.5, -8), ('Part_track_fr', -6.5, -8), ('Part_track_rl', 6.5, 8),
                       ('Part_track_rr', -6.5, 8)):
        _crawler(a, name, x, y)
    sub = a.part('Chassis', STEEL)
    C.slab_loft(sub, C.octagon(13.0, 19.0, 3.0), C.octagon(11.0, 15.0, 3.2), 3.0, RING_Z - .6,
                mid=(C.octagon(13.0, 19.0, 3.0), 3.6))
    for x, y in ((6.5, -8), (-6.5, -8), (6.5, 8), (-6.5, 8)):
        sub.limb((x * .9, y * .9, 3.0), (x, y, 2.9), .6, .6, bevel=0)
    k.lathe(a.part('Slewing_ring', 'Steel'), [(5.6, RING_Z - .6), (5.8, RING_Z - .5), (5.8, RING_Z - .1),
                                              (5.4, RING_Z)], seg=24, worn=(2,))
    a.part('Team_band', 'Team').box((.05, 8.0, .5), loc=(6.55, 0, 3.3), bevel=0)
    a.part('Team_band', 'Team').box((.05, 8.0, .5), loc=(-6.55, 0, 3.3), bevel=0)
    # Stair towers on two corners of the substructure.
    for x, y in ((5.0, 9.0), (-5.0, -9.0)):
        st = a.part('Stairs', 'Steel')
        for i in range(7):
            st.box((.9, .3, .05), loc=(x, y - .5 + i * .18 * (1 if y > 0 else -1), .4 + i * .5), bevel=0)
        a.part('Railings', 'Steel').tube([(x + .45, y - .5, 1.2), (x + .45, y + (.6 if y > 0 else -.6), 4.0)], .04,
                                         seg=4)


def _house(a):
    """The machine house on the ring: stepped walls, window bands, walkways, railings, ladders."""
    h = a.part('Hull', STEEL)
    C.slab_loft(h, C.octagon(10.0, 16.5, 1.2, y0=2.0), C.octagon(9.0, 15.5, 1.4, y0=2.2), RING_Z, ROOF,
                mid=(C.octagon(10.0, 16.5, 1.2, y0=2.0), ROOF - 1.6))
    k.block(a.part('Hull_upper', STEEL), (4.0, 4.0, 1.8), loc=(0, 4.0, ROOF + .9), chamfer=.15)
    wb = a.part('Lit_windows', 'Glass')
    for s in (-1, 1):
        for j in range(6):
            wb.box((.04, 1.5, .5), loc=(s * 5.01, -4.0 + j * 2.4, ROOF - 2.4), bevel=0)
        a.part('Team_band', 'Team').box((.05, 14.0, .4), loc=(s * 5.02, 2.0, RING_Z + 1.4), bevel=0)
        # Walkways along the sides with railings and a ladder up to the roof.
        k.block(a.part('Walkways', 'Steel'), (1.0, 15.0, .1), loc=(s * 5.5, 2.0, RING_Z + 2.5), chamfer=0)
        rl = a.part('Railings', 'Steel')
        rl.tube([(s * 6.0, -5.4, RING_Z + 3.4), (s * 6.0, 9.4, RING_Z + 3.4)], .04, seg=4)
        for yy in range(-5, 10, 3):
            rl.limb((s * 6.0, yy, RING_Z + 2.55), (s * 6.0, yy, RING_Z + 3.4), .03, .03, bevel=0)
        K.ladder(a.part('Ladders', 'Steel'), (s * 5.1, 9.6, RING_Z + 2.55), (s * 4.6, 10.0, ROOF), width=.6, step=.4)
    K.grille(a, (0, 10.27, RING_Z + 2.0), 6.0, 1.6, facing=(0, 1, 0), slats=8, frame_mat=STEEL)
    for x, y in ((3.5, 9.5), (-3.5, -5.5), (3.5, -5.5)):
        K.floodlight(a, (x, y, ROOF), facing=(0, -1 if y < 0 else 1, -.4), pole=1.6)
    K.beacon(a, (0, -5.0, ROOF), r=.2)
    rr = a.part('Railings', 'Steel')
    pts = [(-4.3, -5.8), (4.3, -5.8), (4.3, 10.0), (-4.3, 10.0)]
    rr.tube([(x, y, ROOF + .9) for x, y in pts + pts[:1]], .04, seg=4)


def _cab(a):
    """The operator's cab on the house's front (boss part cab)."""
    p = a.pivot('Part_cab', (-3.0, -4.0, 9.6))
    cab = a.part('Cab', 'Team', p)
    C.slab_loft(cab, C.octagon(2.6, 2.4, .4), C.octagon(2.4, 2.0, .4, y0=.15), 0, 2.0)
    gl = a.part('Glass', 'Glass', p)
    gl.box((2.0, .04, 1.0), loc=(0, -1.12, 1.3), rot=(-.2, 0, 0), bevel=0)
    for s in (-1, 1):
        gl.box((.04, 1.4, .9), loc=(s * 1.25, 0, 1.3), bevel=0)
    k.block(a.part('Cab_roof', 'Steel', p), (2.8, 2.6, .15), loc=(0, .1, 2.08), chamfer=.03)
    K.whip_antenna(a.part('Antennas', 'Steel', p), (.9, .8, 2.15), h=1.5, r=.03)


def _lattice(part, p0, p1, w, h, bays, r=.07):
    """A box lattice girder from p0 to p1 (four chords, verticals and diagonals in each bay)."""
    x0, y0, z0 = p0
    x1, y1, z1 = p1
    corners = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]

    def at(f, cx, cz):
        return (x0 + (x1 - x0) * f + cx, y0 + (y1 - y0) * f, z0 + (z1 - z0) * f + cz)
    for cx, cz in corners:
        part.tube([at(0, cx, cz), at(1, cx, cz)], r * 1.5, seg=4)
    for b in range(bays):
        f0, f1 = b / bays, (b + 1) / bays
        for i, (cx, cz) in enumerate(corners):
            nx, nz = corners[(i + 1) % 4]
            part.tube([at(f0, cx, cz), at(f0, nx, nz)], r, seg=4)
            part.tube([at(f0, cx, cz), at(f1, nx, nz)], r, seg=4)


def _boom_and_wheel(a):
    """The cutter boom (boss part boom) and the bucket wheel (boss part bucket_wheel)."""
    pb = a.pivot('Part_boom', (0, -13.0, 10.0))
    g = a.part('Boom_girder', STEEL, pb)
    _lattice(g, (0, 7.0, -2.2), (0, -8.5, -.6), 2.8, 2.4, 9)
    bs = a.part('Boom_steel', 'Undercarriage', pb)
    bs.box((1.6, 15.5, .1), loc=(0, -.75, -.25), rot=(-.1, 0, 0), bevel=0)
    for f in (.2, .5, .8):
        a.part('Hazard_marks', 'Hazard', pb).box((2.9, .4, .05), loc=(0, 7.0 - 15.5 * f, -2.2 + 1.6 * f + 1.25),
                                                 bevel=0)
    pw = a.pivot('Part_wheel', (0, -22.0, 9.0))
    R = 6.4
    rim = a.part('Wheel_rim', STEEL, pw)
    for xx in (-1.0, 1.0):
        k.ring(rim, [(R - .5, -.12), (R, -.12), (R, .12), (R - .5, .12)], loc=(xx, 0, 0), rot=(0, R90, 0), seg=24)
    k.lathe(a.part('Wheel_hub', 'Steel', pw), [(1.0, -1.3), (1.2, -1.0), (1.2, 1.0), (1.0, 1.3)], rot=(0, R90, 0),
            seg=12)
    sp = a.part('Wheel_spokes', STEEL, pw)
    for i in range(9):
        u = i * TAU / 9
        for xx in (-1.0, 1.0):
            sp.limb((xx, math.cos(u) * 1.1, math.sin(u) * 1.1), (xx, math.cos(u) * (R - .4), math.sin(u) * (R - .4)),
                    .12, .12, bevel=0)
    bk = a.part('Buckets', 'Steel', pw)
    teeth = a.part('Bucket_teeth', 'Undercarriage', pw)
    for i in range(18):
        u = i * TAU / 18
        cy, cz = math.cos(u) * (R + .3), math.sin(u) * (R + .3)
        rot = (u + R90, 0, 0)
        k.block(bk, (2.4, 1.3, 1.0), loc=(0, cy, cz), rot=rot, chamfer=.08)
        for tx in (-.8, 0, .8):
            ty, tz = math.cos(u) * (R + .85), math.sin(u) * (R + .85)
            ty += -math.sin(u) * .5
            tz += math.cos(u) * .5
            teeth.box((.15, .3, .15), loc=(tx, ty, tz), rot=rot, bevel=0)
    a.part('Wheel_chute', STEEL, pw).box((2.2, 2.0, .2), loc=(0, 2.5, -1.0), rot=(.6, 0, 0), bevel=0)
    a.part('Team_band', 'Team', pw).cyl(1.25, .4, loc=(0, 0, 0), rot=(0, R90, 0), seg=12, bevel=0)


def _pylon(a):
    """The A-frame pylon with its cable stays, the counterweight boom and box, the discharge conveyor."""
    pyl = a.part('Pylon', STEEL)
    top = (0, 4.0, 16.0)
    for s in (-1, 1):
        pyl.limb((s * 1.8, 2.2, ROOF + 1.8), top, .3, .22, bevel=0)
        pyl.limb((s * 1.8, 5.8, ROOF + 1.8), top, .28, .2, bevel=0)
    pyl.box((1.2, 1.2, .6), loc=top, bevel=0)
    stays = a.part('Kit_cables', 'Undercarriage')
    stays.tube([top, (0, -19.0, 10.5)], .06, seg=4)
    stays.tube([top, (0, -9.0, 10.2)], .06, seg=4)
    stays.tube([top, (0, 17.5, 9.5)], .06, seg=4)
    K.beacon(a, (0, 4.0, 16.3), r=.18)
    cw = a.part('Counter_boom', STEEL)
    _lattice(cw, (0, 10.2, 7.0), (0, 17.5, 8.4), 2.6, 2.0, 4)
    k.block(a.part('Counterweight', 'Concrete'), (5.0, 3.0, 3.2), loc=(0, 17.8, 5.6), chamfer=.15)
    a.part('Hazard_marks', 'Hazard').box((5.05, .4, .6), loc=(0, 19.31, 6.6), bevel=0)
    dc = a.part('Conveyor', STEEL)
    _lattice(dc, (0, 18.5, 8.0), (0, 20.2, 6.6), 1.6, 1.0, 1)
    a.part('Conveyor_belt', 'Undercarriage').box((1.2, 2.0, .08), loc=(0, 19.3, 7.9), rot=(.7, 0, 0), bevel=0)


def _guns(a):
    """The roof armament: twin 30 mm (main), two 57 mm, the second 30 mm, the rocket pod."""
    def turret(pivot, loc, barrels, r, length, muzzle, tag, parent=None, house=1.0):
        t = a.pivot(pivot, loc, parent)
        g = a.part(f'Gun_house_{tag}', 'Team', t)
        C.slab_loft(g, C.octagon(1.8 * house, 2.0 * house, .4), C.octagon(1.3 * house, 1.5 * house, .35, y0=.1), 0,
                    .9 * house)
        a.part(f'Gun_ring_{tag}', 'Steel', t).cyl(1.0 * house, .15, loc=(0, 0, .05), seg=12, bevel=0)
        gp = a.part(f'Gun_barrels_{tag}', 'Steel', t)
        for j in range(barrels):
            dx = (j - (barrels - 1) / 2) * .35
            k.lathe(gp, [(r * 1.4, 0), (r * 1.4, .3), (r, .4), (r * .9, length), (0, length)],
                    loc=(dx, -1.0 * house + .05, .5 * house), rot=K.FORWARD, seg=8, worn=(1,))
        a.pivot(muzzle, (0, -1.0 * house + .05 - length - .05, .5 * house), t)
        K.periscope(a, (.5 * house, -.4, .9 * house), facing=(0, -1, 0), parent=t, size=(.2, .15, .12))
        return t
    # The main twin 30 mm on its old pivot (muzzle 4.2 m ahead, as the old file).
    turret('Turret', (4.0, 2.0, ROOF), 2, .07, 3.15, 'Muzzle_main', 'main')
    # Mount 1 / 2 (57 mm) and mount 4 (the second 30 mm, part gun_r's node Mount_gun.002).
    turret(K.name('Mount_gun', 0), (-4.0, 2.0, ROOF), 1, .1, 2.8, K.name('Muzzle_gun', 0), 'g0', house=1.05)
    turret(K.name('Mount_gun', 1), (3.0, 7.0, ROOF), 1, .1, 2.8, K.name('Muzzle_gun', 1), 'g1', house=1.05)
    turret(K.name('Mount_gun', 2), (-3.0, 7.0, ROOF), 2, .07, 2.4, K.name('Muzzle_gun', 2), 'g2', house=.9)
    # The rocket pod at the rear on its own pivot.
    m = a.pivot('Mount_rocket', (0, 9.0, ROOF))
    a.part('Rocket_mount', 'Steel', m).cyl(.5, .6, loc=(0, 0, .3), seg=10, bevel=0)
    pod = a.part('Pods', 'Team', m)
    k.block(pod, (2.0, 1.4, 1.1), loc=(0, .3, .95), rot=(.2, 0, 0), chamfer=.06)
    tubes = a.part('Pod_tubes', 'Undercarriage', m)
    for i in range(4):
        for j in range(3):
            tubes.cyl(.14, .03, loc=(-.6 + i * .4, -.42, .7 + j * .3), rot=(R90 - .2, 0, 0), seg=6, bevel=0)
    a.pivot('Muzzle_rocket', (0, -1.05, .9), m)


def kronos(a, detail=False):
    """The Kronos boss: see the module docstring."""
    K.suffixed(a)
    _substructure(a)
    _house(a)
    _cab(a)
    _boom_and_wheel(a)
    _pylon(a)
    _guns(a)
    K.dust(a, (0, 0, .5), radius=12.0, k=.14)
    k.clean(a)


BUILDERS = {
    'kronos': (kronos, dict(ao_distance=2.0, grime_height=2.5)),
}
