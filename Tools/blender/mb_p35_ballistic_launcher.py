"""Prompt 35 wave 9 (lane C): the ballistic missile launcher rebuilt from scratch (spec:
Tools/blender/specs/ballistic_launcher.json).

The Iskander-M 9P78-1 on the MZKT-7930 8x8 (unit_refs: 9K720 Iskander, 9M723; the def's modelSize 10.7 x 2.53 x
4.18 m, its height the opened cover): the full-width four-seat cab with its raked split windscreen, side windows,
doors, the grille and bumper below, lamps and mirrors; the long chassis on four evenly spaced axles on big lugged
tyres with their wings; the launcher bay with its clamshell cover opened up on both sides (ribbed panels on their
hinges and rams), inside it the two 9M723 missiles side by side on the launch beam (`Turret`: their ogive noses,
the dark seeker windows, the four tail fins and the rocket nozzles) with the erector's rams at the rear; the
rear stabilising jacks, toolboxes, jerrycans, the spare wheel, the cab's roof rack and whips.

Runtime nodes kept: `Turret`, `Muzzle_main`, the old file's `Mount_mg` / `Muzzle_mg` (plain pivots on the cab
roof; the def has no secondary), `Point_exhaust`, `Point_fire`. Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Matrix

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WR = .6
AXLES = (-3.45, -1.75, 1.3, 3.0)
TX = .88
FZ = 1.05
NOSE, TAIL = -5.35, 5.35
BAY_Z = 1.25        # the bay's floor
BAY_TOP = 2.35      # the bay's sill (the cover's hinge line)


def _cab(a):
    cab = a.part('Cab', 'Team')
    C.section_loft(cab, [
        (NOSE, [(0, FZ - .25), (1.16, FZ - .25), (1.18, 1.6), (1.12, 1.66), (0, 1.66)]),
        (NOSE + .5, [(0, FZ - .25), (1.2, FZ - .25), (1.22, 1.62), (.9, 2.55), (0, 2.6)]),
        (NOSE + 2.3, [(0, FZ - .25), (1.2, FZ - .25), (1.22, 1.62), (.92, 2.6), (0, 2.62)]),
    ])
    for s in (-1, 1):
        K.windscreen(a, [(s * .05 if s < 0 else .05, NOSE + .05, 1.72), (s * 1.0, NOSE + .05, 1.72),
                         (s * .8, NOSE + .42, 2.5), (s * .05, NOSE + .42, 2.5)][::s], frame_mat='Team', wipers=1)
        gl = a.part('Glass', 'Glass')
        for y in (NOSE + .85, NOSE + 1.75):
            gl.box((.01, .6, .4), loc=(s * 1.09, y, 2.08), rot=(0, s * .34, 0), bevel=0)
        dr = a.part('Doors', 'Team')
        for y in (NOSE + .85, NOSE + 1.75):
            dr.box((.012, .8, .02), loc=(s * 1.225, y, 1.75), bevel=0)
            dr.box((.012, .02, .8), loc=(s * 1.225, y + .4, 1.35), bevel=0)
            K.handle(a.part('Kit_steel', 'Steel'), (s * 1.23, y + .2, 1.6), (s * 1.23, y + .3, 1.6), (s, 0, 0), h=.025,
                     r=.01)
        K.mirror(a.part('Kit_steel', 'Steel'), (s * 1.1, NOSE + .15, 2.0), s, arm=.08, size=(.05, .02, .18))
        K.lamp(a, (s * .85, NOSE - .01, 1.3), (0, -1, 0), r=.08, guard=True)
        st = a.part('Steps', 'Steel')
        for y in (NOSE + .85, NOSE + 1.75):
            st.box((.08, .45, .03), loc=(s * 1.2, y, .75), bevel=0)
    K.grille(a, (0, NOSE - .01, 1.3), 1.1, .4, facing=(0, -1, 0), slats=5, frame_mat='Steel')
    bp = a.part('Bumper', 'Steel')
    K.chamfer_box(bp, (2.4, .14, .22), loc=(0, NOSE - .02, FZ - .3), c=.03)
    for s in (-1, 1):
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .5, NOSE - .08, FZ - .35), facing=(0, -1, 0), size=.08)
    rk = a.part('Racks', 'Steel')
    sq = [(-.02, -.02), (.02, -.02), (.02, .02), (-.02, .02)]
    k.sweep(rk, sq, [(-.9, NOSE + .7, 2.62), (-.9, NOSE + 2.1, 2.62), (.9, NOSE + 2.1, 2.62), (.9, NOSE + .7, 2.62),
                     (-.9, NOSE + .7, 2.62)])
    a.part('Stowage', 'Canvas').box((1.4, .9, .25), loc=(0, NOSE + 1.4, 2.75), bevel=0)
    for s in (-1, 1):
        K.whip_antenna(a.part('Antennas', 'Steel'), (s * .85, NOSE + 2.15, 2.62), h=1.2, r=.015)
    m = a.pivot('Mount_mg', (.5, NOSE + 1.0, 2.62))
    a.pivot('Muzzle_mg', (0, -.5, .2), m)


def _chassis(a):
    fr = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        fr.box((.18, 10.2, .32), loc=(s * .45, .2, FZ - .16), bevel=0)
    ax = a.part('Axles', 'Undercarriage')
    for y in AXLES:
        K.axle(ax, y, WR, TX - .1, r=.07)
        for s in (-1, 1):
            K.tread_wheel(a, (s * TX, y, WR), WR, .44, s, seg=12)
    wing = a.part('Mud_wings', 'Team')
    for y in AXLES[1:]:
        for s in (-1, 1):
            K.plate(wing, (.5, 1.45, .04), loc=(s * (TX + .03), y, WR * 2 + .12), chamfer=.01)
    for s in (-1, 1):
        C.stowage_box(a, (.32, 1.2, .32), (s * 1.02, -.25, FZ - .55), mat='Team', latches=2)
    C.jerry_rack(a, (-1.1, 2.15, FZ - .55), count=2, axis='Y')
    K.tread_wheel(a, (1.02, 2.15, FZ - .2), .45, .3, 1, seg=10, tyre='Spare_wheel', rim='Spare_wheel_rim')
    K.exhaust(a, (1.1, NOSE + 2.4, FZ + .3), r=.07, length=.9, direction=(0, 0, 1))
    a.pivot('Point_exhaust', (1.1, NOSE + 2.4, FZ + 1.25))
    a.pivot('Point_fire', (0, .5, BAY_TOP))
    for s in (-1, 1):
        a.part('Tail_lamps', 'Lamp').box((.12, .02, .08), loc=(s * 1.0, TAIL - .02, FZ), bevel=0)
    jk = a.part('Outriggers', 'Steel')
    pads = a.part('Outrigger_pads', 'Steel')
    for s in (-1, 1):
        for y in (-2.55, TAIL - .4):
            K.outrigger(jk, pads, (s * .5, y, FZ - .05), s, reach=.6, drop=.35, w=.15)


def _bay(a):
    """The launcher bay: walls, floor, the clamshell cover opened up, the missiles on their beam (`Turret`)."""
    y0, y1 = NOSE + 2.4, TAIL - .25
    bay = a.part('Hull', 'Team')
    for s in (-1, 1):
        xa, xb = sorted((s * 1.0, s * 1.2))
        xc, xd = sorted((s * 1.0, s * 1.1))
        C.slab_loft(bay, [(xa, y0), (xb, y0), (xb, y1), (xa, y1)], [(xc, y0 + .05), (xd, y0 + .05), (xd, y1 - .05),
                                                                    (xc, y1 - .05)], BAY_Z - .2, BAY_TOP)
    k.block(bay, (2.4, .2, BAY_TOP - BAY_Z + .2), loc=(0, y1 - .1, BAY_Z - .2 + (BAY_TOP - BAY_Z + .2) / 2), chamfer=.02)
    k.block(bay, (2.4, .25, BAY_TOP - BAY_Z + .45), loc=(0, y0 + .12, BAY_Z - .2 + (BAY_TOP - BAY_Z + .45) / 2),
            chamfer=.02)
    a.part('Floor', 'Undercarriage').box((2.0, y1 - y0, .05), loc=(0, (y0 + y1) / 2, BAY_Z), bevel=0)
    # The cover: two ribbed halves swung open about the sills and hanging down along the bay's sides.
    cov = a.part('Cover', 'Team')
    ribs = a.part('Cover_ribs', 'Steel')
    pw = 1.0                           # each half's width (its height as it hangs)
    for s in (-1, 1):
        hx = s * 1.22
        cz = BAY_TOP - pw / 2 + .04
        K.plate(cov, (.04, y1 - y0 - .3, pw), loc=(hx + s * .02, (y0 + y1) / 2, cz), rot=(0, s * .06, 0),
                chamfer=.01)
        for j in range(7):
            yy = y0 + .4 + j * (y1 - y0 - .8) / 6
            ribs.box((.03, .06, pw * .95), loc=(hx + s * .055, yy, cz), rot=(0, s * .06, 0), bevel=0)
        a.part('Cover_hinges', 'Steel').cyl(.05, y1 - y0 - .4, loc=(hx, (y0 + y1) / 2, BAY_TOP + .02), rot=K.FORWARD,
                                            seg=6, bevel=0)
        a.part('Team_band', 'Team').box((.02, 3.0, .15), loc=(hx + s * .05, (y0 + y1) / 2, cz - .25),
                                        rot=(0, s * .06, 0), bevel=0)
        for yy in (y0 + 1.0, y1 - 1.0):
            a.part('Cover_rams', 'Steel').limb((s * 1.0, yy, BAY_TOP - .1), (s * 1.24, yy, BAY_TOP - .5), .03, .035,
                                               bevel=0)
    # The launch beam and the two 9M723 missiles side by side (`Turret`).
    t = a.pivot('Turret', (0, .9, BAY_Z + .05))
    beam = a.part('Launcher_beam', 'Armor', t)
    k.block(beam, (1.6, 6.6, .22), loc=(0, .2, 0), chamfer=.03)
    R, L = .36, 6.0
    lift = math.radians(22)           # the left missile on its erector, raised from its tail hinge
    for i, x in enumerate((-.42, .42)):
        hinge = (x, .2 + L / 2, .22 + R + .02)
        e = lift if i == 0 else 0.0
        rot = (R90 - e, 0, 0)
        d = (0, -math.cos(e), math.sin(e))
        k.lathe(a.part('Missiles', 'Fuel', t), [(R * .85, 0), (R, .15), (R, L * .72), (R * .85, L * .84),
                                                (R * .45, L * .96), (0, L)], loc=hinge, rot=rot, seg=12,
                worn=(2, 4))

        def at(f, up=0.0):
            return (x, hinge[1] + d[1] * f + math.sin(e) * up, hinge[2] + d[2] * f + math.cos(e) * up)
        a.part('Missile_seekers', 'Glass', t).cyl(R * .35, .02, loc=at(L * .9, R * .5), rot=(R90 - e - .5, 0, 0),
                                                  seg=8, bevel=0)
        a.part('Missile_bands', 'Hazard', t).cyl(R + .01, .08, loc=at(L * .55), rot=rot, seg=12, bevel=0)
        fins = a.part('Missile_fins', 'Steel', t)
        for j in range(4):
            u = j * R90 + math.pi / 4
            c = at(.35)
            fr = (Matrix.Rotation(-e, 3, 'X') @ Matrix.Rotation(u - R90, 3, 'Y')).to_euler('XYZ')
            fins.box((.02, .55, .28), loc=(c[0] + math.cos(u) * (R + .12), c[1] + math.sin(u) * (R + .12) * math.sin(e),
                                           c[2] + math.sin(u) * (R + .12) * math.cos(e)), rot=tuple(fr), bevel=0)
        k.lathe(a.part('Nozzles', 'Undercarriage', t), [(R * .55, 0), (R * .7, .12), (R * .5, .2)],
                loc=at(-.02), rot=(-R90 - e, 0, 0), seg=10)
        for f in (.25, .6):
            a.part('Launcher_cradles', 'Steel', t).box((.75, .1, .3), loc=(x, hinge[1] - L * f, .3), bevel=0)
        if i == 0:
            a.pivot('Muzzle_main', at(L + .02), t)
            ar = a.part('Erector_arm', 'Armor', t)
            ar.limb((x, hinge[1] - 1.0, .2), at(L * .45, -R - .05), .08, .08, bevel=0)
            k.block(ar, (.3, 4.2, .12), loc=at(L * .55, -R - .08), rot=(-e, 0, 0), chamfer=.02)
    rr = a.part('Launcher_rams', 'Steel', t)
    for s in (-1, 1):
        rr.limb((s * .75, 3.2, .05), (s * .75, 1.6, .25), .06, .07, bevel=0)


def ballistic_launcher(a, detail=False):
    """The Iskander-M 9P78-1: see the module docstring."""
    _cab(a)
    _chassis(a)
    _bay(a)
    K.dust(a, (0, 0, .3), radius=4.8, k=.14)
    k.clean(a)


BUILDERS = {
    'ballistic_launcher': (ballistic_launcher, dict(ao_distance=.45, grime_height=.5)),
}
