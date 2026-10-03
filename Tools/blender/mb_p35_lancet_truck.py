"""Prompt 35 wave 1 (lane B): the Lancet truck rebuilt from scratch (spec: Tools/blender/specs/lancet_truck.json).

A KamAZ Typhoon-K 6x6 MRAP (0.82 x real: the def's modelSize 7.41 x 2.02 x 2.7 m) carrying the Lancet loitering
munition launcher: the angular armoured cab-forward cab with its big flat armoured windscreens, the V-hull under it
and the heavy bumper; behind it the armoured equipment body with sloped lower sides, side doors and stowage bins;
on its deck the launcher turntable with the long catapult rail rising forward (the sheet's long diagonal rail from
above), a Lancet with its two cruciform X wing sets and the pusher propeller sitting on the rail's carriage, and a
rack of six launch canisters for the reloads; six big wheels (a front axle, a rear tandem); the M2 on a raised roof
ring over the cab.

Its own body: nothing taken from the FPV carrier (also a Typhoon-K, with a honeycomb drone box).
Runtime nodes kept: `Turret` (the launcher's yaw pivot), `Muzzle_main` (the rail's top end), `Mount_mg` /
`Muzzle_mg`, `Point_exhaust`, `Point_fire`; `Box_face` (the canister rack's face, a launch face).
Metres, +Z up, -Y front, +X left.
"""
import math

import bmesh
from mathutils import Matrix, Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
WR, WW, TRACK = .53, .38, .8
AXLES = (-2.7, 1.0, 2.42)
FRONT, REAR = -3.7, 3.7
HALF = 1.0
CAB_Y0, CAB_Y1, CAB_Z0, ROOF = -3.62, -1.92, 1.1, 2.28
BODY_Y0, BODY_Y1, DECK = -1.86, 3.62, 1.82
RAIL = 0.22                   # the rail's rise (radians)


def _running_gear(a):
    frame = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        K.chamfer_box(frame, (.12, 7.1, .28), loc=(s * .42, 0, .92), c=.02)
    for y in AXLES:
        for s in (-1, 1):
            P.tread_wheel(a, (s * TRACK, y, WR), WR, WW, s, seg=12, rim_seg=8, depth=.045)
            K.dust(a, (s * TRACK, y, .15), radius=1.0, k=.28)
        K.axle(a.part('Axles', 'Undercarriage'), y, WR, TRACK - .1, r=.08, diff=y < 0)
    susp = a.part('Suspension', 'Steel')
    for s in (-1, 1):
        # Independent suspension: the wishbones and the coil-over struts at every wheel.
        for y in AXLES:
            susp.tube([(s * .45, y - .15, WR + .05), (s * (TRACK - .2), y, WR + .02), (s * .45, y + .15, WR + .05)],
                      .03, seg=5)
            k.lathe(susp, [(.07, 0), (.07, .3), (.05, .32), (.05, .45)], loc=(s * (TRACK - .3), y, WR + .1),
                    rot=(0, -s * .3, 0), seg=6)
    a.pivot('Point_fire', (0, 1.0, 2.0))


def _cab(a):
    team = a.part('Cab', 'Team')
    dark = a.part('Cab_dark', 'Undercarriage')
    # Horizontal sections: a sharply cut front (the armoured windscreen raked back), the lower front wrapping in
    # to the V-hull, the roof a little narrower (side armour leaning in).
    rings = []
    for z, yf, c, h in ((CAB_Z0 - .25, CAB_Y0 + .25, .3, HALF - .35), (CAB_Z0 + .1, CAB_Y0, .2, HALF),
                        (CAB_Z0 + .55, CAB_Y0 + .02, .22, HALF), (ROOF - .1, CAB_Y0 + .42, .3, HALF - .1),
                        (ROOF, CAB_Y0 + .52, .32, HALF - .14)):
        rings.append([(-h, CAB_Y1, z), (-h, yf + c, z), (-h + c, yf, z), (h - c, yf, z), (h, yf + c, z),
                      (h, CAB_Y1, z)])
    k.sharp_loft(team, rings, chamfer=.04)
    # The heavy bumper with its tow eyes, the grille slot, lamps in armoured housings.
    bump = a.part('Bumper', 'Armor')
    K.chamfer_box(bump, (HALF * 2 + .02, .26, .32), loc=(0, FRONT + .13, .95), c=.04)
    for s in (-1, 1):
        bump.box((.1, .08, .12), loc=(s * .55, FRONT - .02, .86), bevel=0)
        K.lamp(a, (s * .78, CAB_Y0 - .005, CAB_Z0 + .35), (0, -1, 0), r=.075, mat='Armor', guard=True)
    K.grille(a, (0, CAB_Y0 - .005, CAB_Z0 + .32), .9, .22, facing=(0, -1, 0), slats=4, frame_mat='Armor')
    # The two big flat armoured windscreens on the raked face, the side windows, the door and its hinges.
    z0, z1 = CAB_Z0 + .62, ROOF - .16

    def fy(z):
        return CAB_Y0 + .02 + .4 * (z - CAB_Z0 - .55) / (ROOF - .1 - CAB_Z0 - .55) - .008
    for s in (-1, 1):
        x0, x1 = s * .06, s * (HALF - .3)
        c = [(x0, fy(z0), z0), (x1, fy(z0), z0), (x1, fy(z1), z1), (x0, fy(z1), z1)]
        if s < 0:
            c = [c[1], c[0], c[3], c[2]]
        K.windscreen(a, c, frame_mat='Undercarriage', wipers=1, bar=.06)
    glass = a.part('Glass', 'Glass')
    fit = a.part('Cab_fit', 'Steel')
    for s in (-1, 1):
        x = s * (HALF + .003)
        glass.box((.012, .55, .4), loc=(s * (HALF - .055), -2.75, ROOF - .45), rot=(0, s * .1, 0), bevel=0)
        for y in (-3.12, -2.35):
            dark.box((.012, .02, ROOF - CAB_Z0 - .3), loc=(x, y, (ROOF + CAB_Z0) / 2 - .1), bevel=0)
        K.hinge(fit, (x + s * .01, -3.1, CAB_Z0 + .25), (x + s * .01, -3.1, CAB_Z0 + .45), r=.022, knuckles=2)
        K.handle(fit, (x, -2.45, CAB_Z0 + .6), (x, -2.55, CAB_Z0 + .6), (s, 0, 0), h=.025, r=.01)
        P.step(a, (s * (HALF - .1), -2.75, .7), w=.4)
        P.step(a, (s * (HALF - .1), -2.75, .95), w=.4)
        K.mirror(fit, (s * (HALF - .05), CAB_Y0 + .5, ROOF - .3), s, arm=.05, size=(.035, .1, .28))
        a.part('Team_band', 'Team').box((.012, 1.0, .09), loc=(s * (HALF + .006), -2.75, CAB_Z0 + .14), bevel=0)
        # Front fender boxes over the front wheels.
        K.chamfer_box(a.part('Fenders', 'Armor'), (.42, 1.2, .1), loc=(s * TRACK, AXLES[0], WR + .62), c=.025)
    P.raised_gun(a, (.3, -2.5, ROOF), pivot='Mount_mg', barrel='MG_barrel', brake='MG_flash', muzzle='Muzzle_mg',
                 riser=.1, ring_r=.36, post=.14, length=1.0, shield_k=.75, tag='_mg')
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.75, -2.1, ROOF - .05), h=.5, r=.02)


def _body(a):
    """The armoured equipment body: V-hull lower sides, upright upper sides, the deck, doors, bins, exhaust."""
    body = a.part('Body', 'Armor')
    yl = BODY_Y1 - BODY_Y0
    yc = (BODY_Y0 + BODY_Y1) / 2
    k.extrude(body, [(-HALF + .3, .82), (HALF - .3, .82), (HALF, 1.18), (HALF, DECK), (-HALF, DECK), (-HALF, 1.18)],
              yl, loc=(0, yc, 0), axis='Y', chamfer=.04, corner=.03)
    fit = a.part('Kit_latches', 'Steel')
    dark = a.part('Body_dark', 'Undercarriage')
    for s in (-1, 1):
        x = s * (HALF + .004)
        # Side doors (equipment lockers) with their seams, hinges and handles; a team band.
        for y0, y1 in ((-1.6, -.5), (-.3, .6), (1.7, 3.3)):
            for y in (y0, y1):
                dark.box((.01, .015, DECK - 1.25), loc=(x, y, (DECK + 1.2) / 2), bevel=0)
            dark.box((.01, y1 - y0, .015), loc=(x, (y0 + y1) / 2, 1.22), bevel=0)
            fit.box((.02, .05, .1), loc=(x + s * .01, y1 - .1, 1.5), bevel=0)
        a.part('Team_band', 'Team').box((.012, yl - .3, .09), loc=(s * (HALF + .008), yc, DECK - .12), bevel=0)
        # Rear fender boxes over the tandem, mud flaps.
        K.chamfer_box(a.part('Fenders', 'Armor'), (.42, 2.0, .1), loc=(s * TRACK, (AXLES[1] + AXLES[2]) / 2,
                                                                        WR + .6), c=.025)
        P.mudflap(a, (s * TRACK, AXLES[2] + .62, WR + .55), w=.42, h=.45)
    # A rear door with its window, the ladder under it, tail lamps.
    K.hatch_rect(a, (-.3, BODY_Y1 + .005, 1.4), size=(.6, .65), normal=(0, 1, 0))
    K.ladder(a.part('Ladders', 'Steel'), (-.3, REAR + .02, .5), (-.3, REAR + .02, 1.05), width=.4, step=.22)
    for s in (-1, 1):
        a.part('Tail_lamps', 'Undercarriage').box((.18, .05, .1), loc=(s * .78, BODY_Y1 + .02, 1.05), bevel=0)
        a.part('Tail_lenses', 'LavaGlow').box((.14, .01, .07), loc=(s * .78, BODY_Y1 + .05, 1.05), bevel=0)
    K.exhaust(a, (.92, BODY_Y0 + .15, 1.5), r=.05, length=.75, direction=(0, 0, 1), muffler=False, cap=True)
    a.pivot('Point_exhaust', (.92, BODY_Y0 + .15, 2.3))
    # Deck furniture: a railing round the deck's edge, a stowage bin, the generator box.
    K.railing(a.part('Railings', 'Steel'), [(-HALF + .05, BODY_Y0 + .1, DECK), (-HALF + .05, BODY_Y1 - .1, DECK)],
              h=.3, post=1.1, r=.018)
    K.chamfer_box(a.part('Stowage', 'Crate'), (.7, .5, .3), loc=(.55, BODY_Y0 + .4, DECK + .15), c=.03)
    K.crate(a.part('Stowage', 'Crate'), a.part('Kit_straps', 'Steel'), (.5, .4, .3), (-.5, BODY_Y0 + .38, DECK),
            bands=1)


def _launcher(a):
    """The launcher: turntable, the catapult rail rising forward, the Lancet on its carriage, the canister rack."""
    yt = 1.15
    k.ring(a.part('Turntable', 'Steel'), [(.55, 0), (.65, 0), (.65, .1), (.55, .1)], loc=(0, yt, DECK), seg=16)
    t = a.pivot('Turret', (0, yt, DECK + .1))
    base = a.part('Rack_base', 'Armor', t)
    K.chamfer_box(base, (1.1, 1.4, .3), loc=(0, .3, .15), c=.04)
    # The rail: a long box beam from behind the turntable rising forward, its trestle legs and the elevation ram.
    L = 3.5
    p0 = Vector((0, 1.8, -.02))                   # rear end (turret space)
    d = Vector((0, -math.cos(RAIL), math.sin(RAIL)))
    p1 = p0 + d * L
    rail = a.part('Rail', 'Steel', t)
    rot = (-RAIL, 0, 0)
    mid = (p0 + p1) / 2
    k.block(rail, (.24, L, .16), loc=tuple(mid), rot=rot, chamfer=.025)
    for f in (.15, .5, .85):                       # the guide tracks on the beam's top
        q = p0 + d * (L * f)
        rail.box((.24, .1, .03), loc=tuple(q + Vector((0, 0, .075))), rot=rot, bevel=0)
    legs = a.part('Rams', 'Steel', t)
    legs.tube([(-.3, .9, .3), tuple(p0 + d * 1.6 + Vector((-.09, 0, -.05))), ], .035, seg=6)
    legs.tube([(.3, .9, .3), tuple(p0 + d * 1.6 + Vector((.09, 0, -.05)))], .035, seg=6)
    # The Lancet on the carriage near the rail's top: a slim body, the two X wing sets, the pusher propeller.
    c = p0 + d * (L * .45) + Vector((0, 0, .2))
    m = Matrix.Translation(c) @ Matrix.Rotation(-RAIL, 4, 'X')
    lan = a.part('Lancet', 'MetalSheet', t)
    k.lathe(lan, [(0, -.66), (.05, -.62), (.075, -.5), (.075, .5), (.05, .66), (0, .72)], loc=tuple(c),
            rot=(R90 - RAIL, 0, 0), seg=8, worn=(2,))
    a.part('Lancet_seeker', 'Glass', t).cyl(.045, .03, loc=tuple(m @ Vector((0, -.72, 0))), rot=(R90 - RAIL, 0, 0),
                                            seg=8, bevel=0)
    wings = a.part('Munition_wings', 'Team', t)
    for yy, span, chord in ((-.35, .42, .22), (.35, .5, .26)):
        for i in range(4):
            u = i * R90 + math.pi / 4
            off = Vector((math.cos(u) * span / 2, yy, math.sin(u) * span / 2))
            wm = m @ Matrix.Translation(off) @ Matrix.Rotation(u, 4, 'Y')
            wings.box((span, chord, .012), loc=tuple(wm.to_translation()), rot=tuple(wm.to_euler('XYZ')), bevel=0)
    prop = a.part('Lancet_prop', 'Undercarriage', t)
    for i in range(2):
        pm = m @ Matrix.Translation((0, .7, 0)) @ Matrix.Rotation(i * R90 + .3, 4, 'Y')
        prop.box((.34, .015, .04), loc=tuple(pm.to_translation()), rot=tuple(pm.to_euler('XYZ')), bevel=0)
    a.part('Carriage', 'Undercarriage', t).box((.26, .3, .1), loc=tuple(c - Vector((0, 0, .14))), rot=rot, bevel=0)
    a.pivot('Muzzle_main', tuple(p1 + Vector((0, -.05, .15))), t)
    # The canister rack beside the rail: six launch tubes for the reloads, its face (a launch face) and doors.
    shell = a.part('Box_shell', 'Armor', t)
    face = a.part('Box_face', 'Undercarriage', t)
    for s in (-1, 1):
        x = s * .55
        K.chamfer_box(shell, (.38, 1.5, .52), loc=(x, .9, .56), c=.03)
        face.box((.34, .02, .48), loc=(x, .14, .56), bevel=0)
        for j in range(3):
            a.part('Cells', 'Undercarriage', t).cyl(.075, .03, loc=(x + (j - 1) * .11, .13, .64), rot=K.FORWARD,
                                                    seg=6, bevel=0)
            a.part('Cells', 'Undercarriage', t).cyl(.075, .03, loc=(x + (j - 1) * .11, .13, .46), rot=K.FORWARD,
                                                    seg=6, bevel=0)
        a.part('Rack_fit', 'Steel', t).box((.4, .04, .04), loc=(x, 1.2, .84), bevel=0)


def lancet_truck(a):
    """The Lancet truck: see the module docstring."""
    _running_gear(a)
    _cab(a)
    _body(a)
    _launcher(a)
    k.clean(a)


BUILDERS = {
    'lancet_truck': (lancet_truck, dict(ao_distance=.55, grime_height=.7)),
}
