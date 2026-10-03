"""Prompt 35 wave 6 (lane B): the dazzler vehicle rebuilt from scratch (spec: Tools/blender/specs/dazzler_vehicle.json).

A Peresvet-class laser dazzler on an MZKT-type 8x8 chassis (the def's modelSize 9.01 x 2.76 x 3.83 m): the wide
flat-fronted cab-over cab with its two-pane windscreen, four doors, roof hatch and the remote 12.7 mm station on a
raised ring over the cab roof (`Turret`); eight wheels on four axles (two pairs) with walking-beam bogies and the
axle beams; the long equipment shelter with its doors, lockers, louvred vents, ladder and roof rails; the lens
housing on its lift frame at the shelter's front top: a box with six lenses in two rows (bezels, glass, a glowing
core each) behind the sun hood, hydraulic lift rams; the generator at the rear with its exhaust stack, the cable
reel, the spare wheel, jerrycans, mud flaps, steps, mirrors, lamps, the beacon and Team bands.

Its own cab and shelter (not drone_hijack_vehicle's or gps_jammer_vehicle's). Runtime nodes kept: `Turret`,
`Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Point_exhaust`, `Point_fire`; old part names `Cab`, `Shelter`,
`Lens_*`, `Lockers`, `Vents`, `Beacon`; new for the gate: `Axles`, `Spare_wheel`, `Stowage`. Metres, +Z up, -Y front,
+X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
WR, WW, TRACK = .5, .36, 1.0
AXLES = (-3.55, -2.3, 1.6, 2.85)
FRONT, REAR = -4.5, 4.5
HALF = 1.3
FRAME_Z = 1.05
CAB_Y1 = -2.75
CAB_ROOF = 2.42
SH_Y0, SH_Y1, SH_Z0, SH_Z1 = -2.55, 3.95, 1.35, 3.25


def _running_gear(a):
    frame = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        K.chamfer_box(frame, (.14, 8.6, .28), loc=(s * .5, 0, FRAME_Z - .1), c=.02)
    susp = a.part('Suspension', 'Steel')
    for i, y in enumerate(AXLES):
        for s in (-1, 1):
            P.tread_wheel(a, (s * TRACK, y, WR), WR, WW, s, seg=10, rim_seg=8, nuts=0, depth=.06)
            K.dust(a, (s * TRACK, y, .1), radius=1.0, k=.28)
        K.axle(a.part('Axles', 'Undercarriage'), y, WR, .62, r=.09, diff=i in (1, 2))
    # Walking beams between the axles of each pair, and their springs.
    for y0, y1 in ((AXLES[0], AXLES[1]), (AXLES[2], AXLES[3])):
        for s in (-1, 1):
            k.block(susp, (.1, y1 - y0 + .3, .16), loc=(s * .62, (y0 + y1) / 2, WR + .12), chamfer=.02)
    a.pivot('Point_fire', (0, .5, 1.9))


def _cab(a):
    cab = a.part('Cab', 'Team')
    rings = []
    # The cab-over: a flat front leaning back a little, straight sides, the roof's front edge rounded off.
    for y, zt, h in ((FRONT, CAB_ROOF - .35, HALF - .05), (FRONT + .12, CAB_ROOF - .05, HALF), (FRONT + .3, CAB_ROOF, HALF),
                     (CAB_Y1, CAB_ROOF, HALF)):
        rings.append([(-h, y, FRAME_Z + .05), (h, y, FRAME_Z + .05), (h, y, zt - .1), (h - .1, y, zt), (-h + .1, y, zt),
                      (-h, y, zt - .1)])
    k.sharp_loft(cab, rings, chamfer=.04)
    # The two-pane windscreen, side windows, four doors with handles and hinges, steps, mirrors.
    z0, z1 = 1.75, CAB_ROOF - .15
    for s in (-1, 1):
        x0, x1 = s * .05, s * (HALF - .12)
        c = [(x0, FRONT + .02, z0), (x1, FRONT + .02, z0), (x1, FRONT + .1, z1), (x0, FRONT + .1, z1)]
        if s < 0:
            c = [c[1], c[0], c[3], c[2]]
        K.windscreen(a, c, frame_mat='Undercarriage', wipers=1, bar=.05)
    glass = a.part('Windows', 'Glass')
    fit = a.part('Cab_fit', 'Steel')
    dark = a.part('Door_panels', 'Undercarriage')
    for s in (-1, 1):
        x = s * (HALF + .004)
        for y in (FRONT + .65, FRONT + 1.35):
            glass.box((.012, .5, .45), loc=(x, y, 2.0), bevel=0)
            dark.box((.012, .02, 1.0), loc=(x, y + .32, 1.6), bevel=0)
            K.handle(fit, (x, y + .2, 1.55), (x, y + .3, 1.55), (s, 0, 0), h=.025, r=.01)
        P.step(a, (s * (HALF - .05), FRONT + .7, FRAME_Z - .15), w=.2, d=.5)
        K.mirror(fit, (s * (HALF - .05), FRONT + .25, 2.05), s, arm=.12, size=(.04, .12, .28))
        K.lamp(a, (s * .95, FRONT - .01, 1.35), (0, -1, 0), r=.08, mat='Undercarriage', guard=False)
    # The grille, the bumper with its tow eyes, the front light bar.
    gr = a.part('Grille', 'Undercarriage')
    for i in range(6):
        gr.box((1.4, .02, .05), loc=(0, FRONT - .005, 1.25 + i * .07), bevel=0)
    K.chamfer_box(a.part('Bumper', 'Armor'), (HALF * 2, .22, .26), loc=(0, FRONT - .02, FRAME_Z - .05), c=.03)
    K.beacon(a, (-.95, FRONT + .35, CAB_ROOF))


def _shelter(a):
    sh = a.part('Shelter', 'Team')
    K.chamfer_box(sh, (HALF * 2, SH_Y1 - SH_Y0, SH_Z1 - SH_Z0), loc=(0, (SH_Y0 + SH_Y1) / 2, (SH_Z0 + SH_Z1) / 2), c=.05)
    k.block(a.part('Subframe', 'Undercarriage'), (HALF * 2 - .1, SH_Y1 - SH_Y0 + .2, .3),
            loc=(0, (SH_Y0 + SH_Y1) / 2, FRAME_Z + .02), chamfer=.02)
    dark = a.part('Door_panels', 'Undercarriage')
    fit = a.part('Steel', 'Steel')
    for s in (-1, 1):
        x = s * (HALF + .004)
        # A door, a row of lockers below the shelter, louvred vents, the corner castings.
        dark.box((.012, .9, 1.7), loc=(x, -1.4, 2.25), bevel=0)
        K.handle(fit, (x, -1.05, 2.1), (x, -1.05, 2.3), (s, 0, 0), h=.03, r=.012)
        K.grille(a, (x + s * .005, 1.0, 2.8), .8, .35, facing=(s, 0, 0), slats=4, frame_mat='Armor')
        lock = a.part('Lockers', 'Armor')
        for j, y in enumerate((-.4, .5, 1.4, 2.3)):
            lock.box((.12, .82, .45), loc=(s * (HALF - .05), y, FRAME_Z - .1), bevel=0)
            fit.box((.02, .1, .03), loc=(s * (HALF + .015), y, FRAME_Z + .02), bevel=0)
        for y in (SH_Y0 + .05, SH_Y1 - .05):
            fit.box((.06, .1, .1), loc=(s * (HALF - .02), y, SH_Z1 - .04), bevel=0)
        a.part('Team_band', 'Team').box((.012, 5.6, .1), loc=(s * (HALF + .006), .8, 1.6), bevel=0)
    vents = a.part('Vents', 'Armor')
    for y in (.6, 1.6, 2.6):
        vents.box((.6, .5, .18), loc=(-.45, y, SH_Z1 + .09), bevel=0)
        a.part('Vent_grilles', 'Undercarriage').box((.5, .4, .02), loc=(-.45, y, SH_Z1 + .19), bevel=0)
    a.part('Racks', 'Steel').tube([(.9, -.6, SH_Z1 + .02), (.9, -.6, SH_Z1 + .12), (.9, 3.5, SH_Z1 + .12),
                                   (.9, 3.5, SH_Z1 + .02)], .02, seg=4)
    K.ladder(a.part('Ladders', 'Steel'), (-.5, SH_Y1 + .05, FRAME_Z), (-.5, SH_Y1 + .05, SH_Z1), width=.4, step=.3)
    K.whip_antenna(a.part('Antennas', 'Steel'), (1.1, 3.6, SH_Z1), h=.5, r=.02, lean=.08)


def _lens(a):
    """The lens housing on its lift frame at the shelter's front top: six lenses, the sun hood, the lift rams."""
    y, z = SH_Y0 + .75, SH_Z1 + .08
    frame = a.part('Lift_frame', 'Steel')
    for s in (-1, 1):
        frame.limb((s * .8, y - .3, SH_Z1), (s * .8, y + .3, z + .2), .08, .08, bevel=0)
        frame.limb((s * .8, y + .3, SH_Z1), (s * .8, y - .3, z + .2), .08, .08, bevel=0)
        a.part('Lift_rams', 'Steel').cyl(.05, .4, loc=(s * .5, y + .35, SH_Z1 + .2), rot=(.5, 0, 0), seg=6, bevel=0)
    hz = z + .48
    k.block(a.part('Lens_housing', 'Armor'), (2.3, 1.2, .82), loc=(0, y, hz - .41), chamfer=.06)
    hood = a.part('Lens_hood', 'Team')
    hood.box((2.36, .5, .04), loc=(0, y - .78, hz + .02), rot=(-.12, 0, 0), bevel=0)
    for s in (-1, 1):
        hood.box((.04, .5, .82), loc=(s * 1.17, y - .78, hz - .38), bevel=0)
    for row in range(2):
        for col in range(3):
            c = ((col - 1) * .68, y - .61, hz - .2 - row * .38)
            k.lathe(a.part('Lens_bezels', 'Steel'), [(.17, 0), (.17, .05), (.12, .05)], loc=c, rot=K.FORWARD, seg=10,
                    caps=(False, False))
            a.part('Lens_glass', 'Energy').cyl(.125, .02, loc=(c[0], c[1] - .03, c[2]), rot=K.FORWARD, seg=10, bevel=0)
            a.part('Lens_cores', 'TeamGlow').cyl(.05, .02, loc=(c[0], c[1] - .045, c[2]), rot=K.FORWARD, seg=8,
                                                 bevel=0)
    a.part('Kit_cables', 'Rubber').tube([(.9, y + .6, hz - .7), (.95, y + .9, SH_Z1 + .05), (.95, y + 1.4, SH_Z1 + .02)],
                                        .035, seg=5)


def _rear(a):
    """The generator at the rear, its exhaust, the cable reel, the spare wheel, jerrycans, tail lamps, mud flaps."""
    gen = a.part('Generator', 'Armor')
    k.block(gen, (1.6, .45, 1.0), loc=(-.3, REAR - .3, FRAME_Z + .05), chamfer=.04)
    K.grille(a, (-.3, REAR - .07, FRAME_Z + .6), 1.2, .5, facing=(0, 1, 0), slats=6, frame_mat='Armor')
    K.exhaust(a, (.9, REAR - .35, FRAME_Z + .1), r=.06, length=.6, direction=(0, 0, 1), muffler=True, cap=True)
    a.pivot('Point_exhaust', (.9, 4.5, 1.0))
    K.soot(a, (.9, REAR - .35, FRAME_Z + .9), radius=.5, k=.5)
    reel = a.part('Cable_reel', 'Steel')
    k.lathe(reel, [(.3, -.25), (.3, -.22), (.18, -.2), (.18, .2), (.3, .22), (.3, .25)], loc=(-HALF + .35, REAR - .25,
                                                                                         FRAME_Z + .9),
            rot=(0, R90, 0), seg=12)
    a.part('Kit_cables', 'Rubber').cyl(.2, .38, loc=(-HALF + .35, REAR - .25, FRAME_Z + .9), rot=(0, R90, 0), seg=12,
                                       bevel=0)
    P.tread_wheel(a, (0, SH_Y1 + .05, FRAME_Z + .1), .46, .3, 1, seg=12, rim_seg=8, tyre='Spare_wheel',
                  rim='Spare_rim', hub=False)
    k.block(a.part('Stowage', 'Canvas'), (.6, .4, .3), loc=(.55, REAR - .7, FRAME_Z + .7), chamfer=.06)
    for s in (-1, 1):
        a.part('Tail_lamps', 'LavaGlow').box((.14, .01, .08), loc=(s * 1.1, REAR + .01, FRAME_Z - .1), bevel=0)
        P.mudflap(a, (s * TRACK, AXLES[3] + .6, .75), w=.4, h=.35)
        P.mudflap(a, (s * TRACK, AXLES[1] + .6, .75), w=.4, h=.35)


def _rws(a):
    P.raised_gun(a, (0, -3.5, CAB_ROOF), parent=None, pivot='Turret', barrel='Main_cannon', brake='Muzzle_brake',
                 muzzle='Muzzle_main', riser=.06, ring_r=.28, post=.12, length=.55, shield=False, ring=True,
                 mat='Armor', tag='')
    k.block(a.part('Rws_sensor', 'Armor'), (.2, .24, .18), loc=(-.38, -3.45, CAB_ROOF), chamfer=.02)


def dazzler_vehicle(a):
    """The dazzler vehicle: see the module docstring."""
    _running_gear(a)
    _cab(a)
    _shelter(a)
    _lens(a)
    _rear(a)
    _rws(a)
    k.clean(a)


BUILDERS = {
    'dazzler_vehicle': (dazzler_vehicle, dict(ao_distance=.6, grime_height=.6)),
}
