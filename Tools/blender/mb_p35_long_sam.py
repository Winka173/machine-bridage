"""Prompt 35 wave 9 (lane C): the long-range SAM launcher rebuilt from scratch (spec: Tools/blender/specs/long_sam.json).

The S-300PMU's 5P85S on the MAZ-543 8x8 (unit_refs: 5P85, 48N6, MAZ-543; the def's modelSize 11.02 x 2.46 x
2.59 m): the MAZ's two separate two-man cabs either side of the engine bay with the radiator grille between them,
their flat windscreens and side windows, the front bumper, lamps and mirrors; the long chassis on four axles in two
pairs on big lugged tyres with their mud wings; the launch control cabin behind the cabs with its door and steps;
the four 48N6 canisters (TPK) lying in a 2 x 2 pack on the erector frame (`Turret`), their ribbed bands and end
caps, the hinge and the erecting rams at the rear, the rear outrigger jacks folded up; the generator's exhaust,
toolboxes, jerrycans and the spare wheel.

Runtime nodes kept: `Turret`, `Muzzle_main`, `Muzzle_missile` (at the canisters' rear ends, where they fire from
when erected), `Point_exhaust`, `Point_fire` (the wrapper adds `Part_wheel` / `Part_wheelb`). Metres, +Z up,
-Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WR = .6
AXLES = (-3.6, -2.25, 1.35, 2.7)
TX = .86
FRAME_Z = 1.05
NOSE, TAIL = -5.5, 5.5


def _cabs(a):
    """The MAZ-543's two cabs either side of the engine bay, the radiator grille, bumper, lamps."""
    for s in (-1, 1):
        cab = a.part('Cab', 'Team')
        x0 = s * .74
        C.slab_loft(cab, [(x0 - .42, NOSE + .1), (x0 + .42, NOSE + .1), (x0 + .42, NOSE + 1.6), (x0 - .42, NOSE + 1.6)],
                    [(x0 - .3, NOSE + .55), (x0 + .3, NOSE + .55), (x0 + .3, NOSE + 1.5), (x0 - .3, NOSE + 1.5)],
                    FRAME_Z - .15, 2.32)
        K.windscreen(a, [(x0 - .34, NOSE + .2, 1.62), (x0 + .34, NOSE + .2, 1.62), (x0 + .27, NOSE + .5, 2.22),
                         (x0 - .27, NOSE + .5, 2.22)], frame_mat='Team', wipers=1)
        gl = a.part('Glass', 'Glass')
        gl.box((.01, .7, .4), loc=(x0 + s * .375, NOSE + 1.0, 1.95), rot=(0, s * .1, 0), bevel=0)
        a.part('Doors', 'Team').box((.012, .7, .7), loc=(x0 + s * .425, NOSE + 1.0, 1.3), bevel=0)
        K.handle(a.part('Kit_steel', 'Steel'), (x0 + s * .435, NOSE + 1.15, 1.5), (x0 + s * .435, NOSE + 1.25, 1.5),
                 (s, 0, 0), h=.025, r=.01)
        K.mirror(a.part('Kit_steel', 'Steel'), (x0 + s * .4, NOSE + .3, 1.9), s, arm=.06, size=(.04, .02, .16))
        K.lamp(a, (x0 + s * .2, NOSE + .08, 1.15), (0, -1, 0), r=.08, guard=True)
        a.part('Roof_hatches', 'Armor').box((.4, .4, .03), loc=(x0, NOSE + .95, 2.33), bevel=0)
    # The engine bay between the cabs: radiator grille in front, the bonnet louvres.
    eng = a.part('Hull', 'Team')
    k.block(eng, (.66, 1.5, .85), loc=(0, NOSE + .85, FRAME_Z + .3), chamfer=.04)
    K.grille(a, (0, NOSE + .1, FRAME_Z + .65), .55, .55, facing=(0, -1, 0), slats=6, frame_mat='Steel')
    K.grille(a, (0, NOSE + 1.0, FRAME_Z + 1.16), .5, .8, facing=(0, 0, 1), slats=5, frame_mat='Team')
    bp = a.part('Bumper', 'Steel')
    K.chamfer_box(bp, (2.4, .14, .22), loc=(0, NOSE + .02, FRAME_Z - .2), c=.03)
    for s in (-1, 1):
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .5, NOSE - .06, FRAME_Z - .25), facing=(0, -1, 0), size=.08)


def _chassis(a):
    fr = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        fr.box((.16, 10.4, .3), loc=(s * .45, .1, FRAME_Z - .15), bevel=0)
    ax = a.part('Axles', 'Undercarriage')
    for y in AXLES:
        K.axle(ax, y, WR, TX - .1, r=.07)
        for s in (-1, 1):
            K.tread_wheel(a, (s * TX, y, WR), WR, .42, s, seg=12)
    wing = a.part('Mud_wings', 'Team')
    for y0, y1 in ((AXLES[0], AXLES[1]), (AXLES[2], AXLES[3])):
        for s in (-1, 1):
            K.plate(wing, (.5, y1 - y0 + 1.4, .04), loc=(s * (TX + .03), (y0 + y1) / 2, WR * 2 + .12), chamfer=.01)
            K.plate(wing, (.04, .3, .35), loc=(s * (TX + .26), y1 + .7, WR * 2 - .05), chamfer=.008)
    a.part('Kit_steel', 'Steel').box((2.3, .06, .25), loc=(0, TAIL - .05, FRAME_Z - .1), bevel=0)
    for s in (-1, 1):
        a.part('Tail_lamps', 'Lamp').box((.1, .02, .08), loc=(s * 1.0, TAIL - .02, FRAME_Z + .02), bevel=0)
    K.exhaust(a, (-.95, -2.9, FRAME_Z + .2), r=.07, length=.9, direction=(0, 0, 1))
    a.pivot('Point_exhaust', (-.95, -2.9, FRAME_Z + 1.15))
    a.pivot('Point_fire', (0, 0, FRAME_Z + .8))


def _cabin(a):
    """The launch control cabin behind the cabs, the stowage along the frame."""
    cb = a.part('Cabin', 'Team')
    C.slab_loft(cb, C.octagon(2.3, 1.5, .08, y0=-2.95), C.octagon(1.5, 1.2, .14, y0=-2.95), FRAME_Z + .55, 2.25,
                mid=(C.octagon(2.3, 1.5, .08, y0=-2.95), FRAME_Z + .9))
    k.block(cb, (2.3, 1.5, .55), loc=(0, -2.95, FRAME_Z + .275), chamfer=0)
    a.part('Glass', 'Glass').box((.01, .4, .25), loc=(1.04, -3.2, 2.0), rot=(0, -.6, 0), bevel=0)
    K.door(a, (-1.16, -2.95, FRAME_Z + .1), size=(.6, 1.0), normal=(-1, 0, 0), mat='Team')
    st = a.part('Steps', 'Steel')
    for i in range(2):
        st.box((.12, .5, .03), loc=(-1.25, -2.95, .55 + i * .28), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (.9, -3.5, 2.25), h=.45, r=.015)
    k.block(a.part('Cabin_ac', 'Armor'), (.6, .5, .25), loc=(0, -2.9, 2.37), chamfer=.03)
    # Toolboxes, jerrycans and the spare wheel along the frame.
    for s in (-1, 1):
        C.stowage_box(a, (.35, 1.0, .35), (s * 1.0, -.4, FRAME_Z - .55), mat='Team', latches=2)
    C.jerry_rack(a, (-1.08, .55, FRAME_Z - .55), count=2, axis='Y')
    K.tread_wheel(a, (1.0, .45, FRAME_Z - .2), .45, .3, 1, seg=10, tyre='Spare_wheel', rim='Spare_wheel_rim')


def _launcher(a):
    """The 2 x 2 pack of 48N6 canisters on the erector (`Turret`), hinge, rams, jacks."""
    hz = FRAME_Z + .2
    t = a.pivot('Turret', (0, 1.6, hz))
    fr = a.part('Launcher_frame', 'Team', t)
    for s in (-1, 1):
        fr.box((.12, 7.0, .18), loc=(s * .6, .2, .05), bevel=0)
    for y in (-2.8, -.9, 1.0, 2.9):
        fr.box((1.3, .12, .12), loc=(0, y, .05), bevel=0)
    tubes = a.part('Launcher_tubes', 'Canvas', t)
    bands = a.part('Launcher_bands', 'Team', t)
    ends = a.part('Launcher_ends', 'Steel', t)
    covers = a.part('Launcher_covers', 'Undercarriage', t)
    R, L = .3, 6.9
    for cx in (-.32, .32):
        for cz in (.42, 1.02):
            k.lathe(tubes, [(R, -L / 2), (R, L / 2)], loc=(cx, .3, cz), rot=K.FORWARD, seg=12, caps=(False, False))
            for f in (-.4, -.12, .16, .43):
                bands.cyl(R + .025, .07, loc=(cx, .3 + f * L, cz), rot=K.FORWARD, seg=10, bevel=0)
            k.lathe(ends, [(R + .03, 0), (R + .03, .1), (R * .5, .16), (0, .17)], loc=(cx, .3 - L / 2, cz),
                    rot=K.FORWARD, seg=10)
            k.lathe(covers, [(R + .03, 0), (R + .03, .12), (0, .14)], loc=(cx, .3 + L / 2, cz), rot=K.BACKWARD,
                    seg=12)
    st = a.part('Launcher_straps', 'Steel', t)
    for y in (-2.0, 1.2):
        st.box((1.32, .05, .05), loc=(0, .3 + y, 1.34), bevel=0)
    a.pivot('Muzzle_main', (.32, .3 + L / 2 + .18, 1.02), t)
    a.pivot('Muzzle_missile', (-.32, .3 + L / 2 + .18, 1.02), t)
    # The hinge at the rear, the erecting rams (folded) and the rear jacks.
    a.part('Launcher_hinge', 'Steel').cyl(.09, 1.6, loc=(0, TAIL - .55, hz), rot=(0, R90, 0), seg=8, bevel=0)
    rams = a.part('Launcher_rams', 'Steel')
    for s in (-1, 1):
        rams.limb((s * .5, TAIL - 1.0, FRAME_Z - .05), (s * .5, 0, hz + .02), .07, .08, bevel=0)
    jk = a.part('Outriggers', 'Steel')
    pads = a.part('Outrigger_pads', 'Steel')
    for s in (-1, 1):
        K.outrigger(jk, pads, (s * .5, TAIL - .4, FRAME_Z - .05), s, reach=.58, drop=.35, w=.14)


def long_sam(a, detail=False):
    """The 5P85S on the MAZ-543: see the module docstring."""
    _cabs(a)
    _chassis(a)
    _cabin(a)
    _launcher(a)
    K.dust(a, (0, 0, .3), radius=5.0, k=.14)
    k.clean(a)


BUILDERS = {
    'long_sam': (long_sam, dict(ao_distance=.45, grime_height=.5)),
}
