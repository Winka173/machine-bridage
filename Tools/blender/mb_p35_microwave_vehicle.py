"""Prompt 35 wave 1 (lane B): the anti-drone microwave vehicle rebuilt from scratch (spec:
Tools/blender/specs/microwave_vehicle.json).

unit_refs has no entry: the model takes the closest fielded system, a Leonidas-class solid-state high-power
microwave emitter (a flat square array of horn cells on a pan-tilt pedestal) on a JLTV-class 4x4 utility vehicle
(the def's modelSize 5.8 x 2.1 x 2.9 m): the long armoured bonnet sloping to the grille slots, the two-door armoured
cab with thick small windows, the short utility bed carrying the emitter pedestal, the power module (generator,
battery bank and its cooling unit) and the cable reels; four big tyres on independent suspension; side steps.

Runtime nodes kept: `Turret` (the emitter's pan pivot), `Muzzle_main` (the array's face; the def has no weapon, the
pulse plays from there), `Point_exhaust`, `Point_fire`; mb_p34_parts adds the wreck wheels (`Part_wheel`,
`Part_wheelb`). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
WR, WW, TRACK = .46, .34, .8
AXLES = (-1.72, 1.55)
FRONT, REAR = -2.9, 2.9
HALF = 1.02
BED_Z = 1.28
CAB_Y0, CAB_Y1, ROOF = -1.02, .62, 2.12
TILT = .32                     # the array's look-up angle at rest


def _running_gear(a):
    frame = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        K.chamfer_box(frame, (.12, 5.4, .26), loc=(s * .42, 0, .86), c=.02)
    # The V-shaped belly plate between the axles.
    k.extrude(a.part('Belly', 'Armor'), [(-.6, .62), (.6, .62), (.8, .8), (-.8, .8)], 2.6, loc=(0, -.05, 0),
              axis='Y', chamfer=.02)
    susp = a.part('Suspension', 'Steel')
    for y in AXLES:
        for s in (-1, 1):
            P.tread_wheel(a, (s * TRACK, y, WR), WR, WW, s, seg=14, rim_seg=8, nuts=6, depth=.04)
            K.dust(a, (s * TRACK, y, .12), radius=.9, k=.28)
            # Double wishbones and the coil-over strut.
            susp.tube([(s * .4, y - .2, WR - .04), (s * (TRACK - .2), y, WR - .02), (s * .4, y + .2, WR - .04)], .03,
                      seg=5)
            susp.tube([(s * .4, y - .18, WR + .22), (s * (TRACK - .22), y, WR + .2), (s * .4, y + .18, WR + .22)],
                      .025, seg=5)
            k.lathe(susp, [(.075, 0), (.075, .28), (.05, .3), (.05, .42)], loc=(s * (TRACK - .32), y + .05, WR + .02),
                    rot=(0, -s * .35, 0), seg=6)
        K.axle(a.part('Axles', 'Undercarriage'), y, WR, .36, r=.1, diff=True)
    a.pivot('Point_fire', (0, -1.6, 1.4))


def _body(a):
    team = a.part('Cab', 'Team')
    # The bonnet: sections from the grille back to the windscreen, the front corners cut, the top domed.
    rings = []
    for y, h, zt, zb in ((FRONT + .08, HALF - .2, 1.12, .62), (FRONT + .35, HALF - .04, 1.25, .62),
                         (-1.6, HALF, 1.36, .62), (CAB_Y0 + .04, HALF, 1.42, .62)):
        rings.append([(-h, y, zb), (h, y, zb), (h, y, zt - .12), (h - .12, y, zt), (-h + .12, y, zt), (-h, y, zt - .12)])
    k.sharp_loft(team, rings, chamfer=.035)
    # Wheel arches: flared fenders front and rear.
    fen = a.part('Fenders', 'Undercarriage')
    for s in (-1, 1):
        for y in AXLES:
            k.sweep(fen, [(-.07, -.02), (.07, -.02), (.07, .02), (-.07, .02)],
                    [(s * (HALF - .02), y + .58 * math.cos(u), WR + .5 * math.sin(u))
                     for u in [math.radians(d) for d in range(5, 180, 25)]])
    # The cab: armoured, upright sides leaning in a little, raked windscreen, flat roof with the roof rails.
    cab = a.part('Cab_armor', 'Team')
    rings = []
    for z, yf, h in ((.62, CAB_Y0, HALF), (1.42, CAB_Y0, HALF), (ROOF - .06, CAB_Y0 + .42, HALF - .2),
                     (ROOF, CAB_Y0 + .5, HALF - .25)):
        rings.append([(-h, yf, z), (h, yf, z), (h, CAB_Y1, z), (-h, CAB_Y1, z)])
    k.sharp_loft(cab, rings, chamfer=.04)
    # The grille: vertical slots in the bonnet nose, the headlamp clusters, the bumper with its tow shackles.
    grille = a.part('Grille', 'Undercarriage')
    for i in range(7):
        x = (i - 3) * .17
        grille.box((.06, .02, .3), loc=(x, FRONT + .07, .9), bevel=0)
    bump = a.part('Bumper', 'Armor')
    K.chamfer_box(bump, (HALF * 2 - .1, .2, .22), loc=(0, FRONT + .1, .58), c=.03)
    for s in (-1, 1):
        K.lamp(a, (s * .62, FRONT + .2, 1.05), (0, -1, .25), r=.07, mat='Undercarriage', guard=False)
        K.tow_hook(a.part('Kit_hooks', 'Steel'), (s * .45, FRONT - .01, .5), facing=(0, -1, 0), size=.06)
    # Windscreen (two thick panes), small side windows, doors with hinges and handles, steps, mirrors.
    def fy(z):
        return CAB_Y0 + .42 * (z - 1.42) / (ROOF - .06 - 1.42) - .008
    z0, z1 = 1.48, ROOF - .12
    for s in (-1, 1):
        x0, x1 = s * .06, s * (HALF - .3)
        c = [(x0, fy(z0), z0), (x1, fy(z0), z0), (x1, fy(z1), z1), (x0, fy(z1), z1)]
        if s < 0:
            c = [c[1], c[0], c[3], c[2]]
        K.windscreen(a, c, frame_mat='Undercarriage', wipers=1, bar=.06)
    glass = a.part('Glass', 'Glass')
    fit = a.part('Cab_fit', 'Steel')
    dark = a.part('Cab_dark', 'Undercarriage')
    for s in (-1, 1):
        x = s * (HALF + .003)
        glass.box((.012, .5, .32), loc=(s * (HALF - .085), -.2, ROOF - .36), rot=(0, s * .3, 0), bevel=0)
        for y in (CAB_Y0 + .06, CAB_Y1 - .06):
            dark.box((.012, .02, 1.2), loc=(x, y, 1.25), bevel=0)
        K.hinge(fit, (x + s * .01, CAB_Y0 + .1, 1.0), (x + s * .01, CAB_Y0 + .1, 1.2), r=.02, knuckles=2)
        K.handle(fit, (x, CAB_Y1 - .25, 1.35), (x, CAB_Y1 - .15, 1.35), (s, 0, 0), h=.025, r=.01)
        P.step(a, (s * (HALF - .04), -.2, .58), w=.18, d=.5)
        K.mirror(fit, (s * (HALF - .1), CAB_Y0 + .25, ROOF - .4), s, arm=.05, size=(.035, .1, .24))
        a.part('Team_band', 'Team').box((.012, 2.5, .08), loc=(s * (HALF + .008), -1.2, .78), bevel=0)
        fit.tube([(s * (HALF - .32), CAB_Y0 + .55, ROOF + .02), (s * (HALF - .32), CAB_Y0 + .55, ROOF + .08),
                  (s * (HALF - .32), CAB_Y1 - .1, ROOF + .08), (s * (HALF - .32), CAB_Y1 - .1, ROOF + .02)], .018, seg=4)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.8, CAB_Y1 - .15, ROOF), h=.5, r=.02)
    # The utility bed: the tub with its drop tailgate, the rails, tail lamps.
    bed = a.part('Bed', 'Armor')
    K.chamfer_box(bed, (HALF * 2, REAR - CAB_Y1 - .05, .18), loc=(0, (CAB_Y1 + REAR) / 2 + .02, BED_Z - .09), c=.02)
    for s in (-1, 1):
        bed.box((.05, REAR - CAB_Y1 - .05, .36), loc=(s * (HALF - .025), (CAB_Y1 + REAR) / 2 + .02, BED_Z + .18),
                bevel=0)
        a.part('Tail_lamps', 'Undercarriage').box((.16, .05, .12), loc=(s * .8, REAR - .01, 1.15), bevel=0)
        a.part('Tail_lenses', 'LavaGlow').box((.12, .01, .08), loc=(s * .8, REAR + .02, 1.15), bevel=0)
    bed.box((HALF * 2 - .1, .05, .36), loc=(0, REAR - .02, BED_Z + .18), bevel=0)
    K.exhaust(a, (-.55, REAR - .2, .62), r=.035, length=.2, direction=(0, 1, 0), muffler=False, cap=False)
    a.pivot('Point_exhaust', (-.55, REAR + .02, .62))


def _power(a):
    """The power module on the bed: generator with vents, the battery bank, the cooling unit, cable reels."""
    gen = a.part('Generators', 'Armor')
    K.chamfer_box(gen, (1.8, .7, .62), loc=(0, CAB_Y1 + .42, BED_Z + .31), c=.04)
    for s in (-1, 1):
        K.grille(a, (s * .905, CAB_Y1 + .42, BED_Z + .32), .45, .36, facing=(s, 0, 0), slats=4, frame_mat='Armor')
    K.panel(a, a.part('Generators_ribs', 'Armor'), (.6, .3), (-.4, CAB_Y1 + .78, BED_Z + .32), (0, 1, 0), rivet=0)
    vents = a.part('Generator_vents', 'Undercarriage')
    for x in (-.45, .45):
        k.ring(vents, [(.17, 0), (.2, 0), (.2, .03), (.17, .03)], loc=(x, CAB_Y1 + .42, BED_Z + .62), seg=10)
        vents.cyl(.17, .01, loc=(x, CAB_Y1 + .42, BED_Z + .63), seg=10, bevel=0)
    # Cable reels and the power cable up to the emitter.
    reel = a.part('Cable_reels', 'Undercarriage')
    for s in (-1, 1):
        k.lathe(reel, [(.06, -.09), (.2, -.09), (.2, -.07), (.14, -.07), (.14, .07), (.2, .07), (.2, .09),
                       (.06, .09)], loc=(s * .75, 2.55, BED_Z + .22), rot=(0, R90, 0), seg=8)
    a.part('Kit_cables', 'Undercarriage').tube([(.5, CAB_Y1 + .78, BED_Z + .4), (.4, 1.4, BED_Z + .25),
                                                (.15, 1.75, BED_Z + .5)], .025, seg=5)
    P.fuel_tank(a, (.88, 0, .95), .9, .2, straps=1)
    P.toolbox(a, (-.88, .05, .92), (.25, .7, .4))


def _emitter(a):
    """The emitter: pedestal with its pan ring, the tilt yoke and the square array of horn cells, its back ribs."""
    yp = 1.95
    ped = a.part('Pedestal', 'Armor')
    k.lathe(ped, [(.42, 0), (.42, .08), (.3, .12), (.24, .4), (.3, .44)], loc=(0, yp, BED_Z), seg=12, worn=(1, 4))
    t = a.pivot('Turret', (0, yp, BED_Z + .46))
    yoke = a.part('Turret_armor', 'Armor', t)
    k.lathe(yoke, [(.34, 0), (.34, .06), (.26, .1), (.22, .18)], seg=12)
    for s in (-1, 1):
        K.chamfer_box(yoke, (.12, .36, .56), loc=(s * .66, 0, .4), c=.03)
    yoke.box((1.44, .26, .14), loc=(0, 0, .16), bevel=0)
    W, T = 1.24, .3
    c, sn = math.cos(TILT), math.sin(TILT)
    ctr = (0, -.04, .62)
    rot = (-TILT, 0, 0)           # face tilted up towards the front
    m = K.frame(ctr, rot)

    def at(x, y, z):
        return K._at(m, (x, y, z))
    em = a.part('Emitter', 'Armor', t)
    K.chamfer_box(em, (W, T, W), loc=ctr, rot=rot, c=.05)
    face = a.part('Emitter_face', 'Undercarriage', t)
    face.box((W - .12, .02, W - .12), loc=at(0, -T / 2 - .006, 0), rot=rot, bevel=0)
    cells = a.part('Horn_cells', 'Steel', t)
    n = 4
    p = (W - .16) / n
    for i in range(n):
        for j in range(n):
            x = -W / 2 + .08 + (i + .5) * p
            z = -W / 2 + .08 + (j + .5) * p
            cells.box((p * .78, .035, p * .78), loc=at(x, -T / 2 - .02, z), rot=rot, bevel=0)
    rim = a.part('Emitter_rim', 'Team', t)
    for s in (-1, 1):
        rim.box((W + .04, .06, .05), loc=at(0, -T / 2 + .02, s * (W / 2 + .01)), rot=rot, bevel=0)
        rim.box((.05, .06, W + .04), loc=at(s * (W / 2 + .01), -T / 2 + .02, 0), rot=rot, bevel=0)
    ribs = a.part('Emitter_ribs', 'Steel', t)
    for x in (-.4, 0, .4):
        ribs.box((.06, .14, W - .1), loc=at(x, T / 2 + .07, 0), rot=rot, bevel=0)
    for s in (-1, 1):
        a.part('Kit_bolts', 'Steel', t).cyl(.06, .08, loc=(s * .6, ctr[1], ctr[2]), rot=(0, R90, 0), seg=8, bevel=0)
    a.part('Visor', 'Glass', t).box((.16, .03, .1), loc=at(W / 2 - .12, -T / 2 - .01, W / 2 + .06), rot=rot,
                                    bevel=0)
    a.pivot('Muzzle_main', at(0, -T / 2 - .05, 0), t)


def microwave_vehicle(a):
    """The anti-drone microwave vehicle: see the module docstring."""
    _running_gear(a)
    _body(a)
    _power(a)
    _emitter(a)
    k.clean(a)


BUILDERS = {
    'microwave_vehicle': (microwave_vehicle, dict(ao_distance=.5, grime_height=.6)),
}
