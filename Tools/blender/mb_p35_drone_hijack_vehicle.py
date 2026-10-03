"""Prompt 35 wave 6 (lane B): the drone hijack vehicle rebuilt from scratch (spec: Tools/blender/specs/drone_hijack_vehicle.json).

A Krasukha / Repellent-class electronic-attack truck on a BAZ-6910-type 8x8 (the def's modelSize 9.01 x 2.76 x
3.83 m): the low armoured cab with its raked three-pane windscreen and short bonnet step, two doors, the cab-roof
mast with the small spinning sensor dish (`Radar`); eight wheels in a 1-1-2 axle spread (the second axle set back)
with independent wishbones and axle beams; the long sloped-ended equipment body with roof air-conditioning units,
side doors, louvres and the stowage boxes under it; the directional hijack array on its turning mast at the rear
(`Turret` > `Muzzle_main`): a tilted flat phased panel of cells in a frame, four yagi elements and a feed horn,
the elevation arms; the generator pod, cable trays, the spare wheel, jerrycans, mud flaps, steps, mirrors, lamps
and Team bands.

Its own cab and body (not dazzler_vehicle's or gps_jammer_vehicle's). Runtime nodes kept: `Turret`, `Muzzle_main`,
`Radar`, `Point_exhaust`, `Point_fire`; old part names `Cab`, `Shelter`, `Array_panel`, `Array_cells`, `Radar_*`,
`Turret_mast`, `Roof_boxes`, `Vents`; new for the gate: `Axles`, `Glass`, `Stowage`. The def is unarmed (no
weapon role). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
WR, WW, TRACK = .52, .38, .98
AXLES = (-3.45, -1.85, 1.75, 3.05)
FRONT, REAR = -4.55, 4.5
HALF = 1.3
FRAME_Z = 1.1
CAB_Y1 = -2.55
CAB_ROOF = 2.5
BODY_Y0, BODY_Y1, BODY_Z1 = -2.4, 4.4, 3.0


def _running_gear(a):
    frame = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        K.chamfer_box(frame, (.14, 8.7, .3), loc=(s * .48, 0, FRAME_Z - .12), c=.02)
    susp = a.part('Suspension', 'Steel')
    for i, y in enumerate(AXLES):
        for s in (-1, 1):
            P.tread_wheel(a, (s * TRACK, y, WR), WR, WW, s, seg=12, rim_seg=6, nuts=0, depth=.05, dish=.8)
            K.dust(a, (s * TRACK, y, .1), radius=1.0, k=.28)
            susp.tube([(s * .48, y - .22, WR - .05), (s * (TRACK - .22), y, WR), (s * .48, y + .22, WR - .05)], .035,
                      seg=5)
        K.axle(a.part('Axles', 'Undercarriage'), y, WR, .55, r=.1, diff=i in (0, 3))
    a.pivot('Point_fire', (0, .5, 1.9))


def _cab(a):
    cab = a.part('Cab', 'Team')
    rings = []
    # The armoured cab: a short sloped nose step, the raked windscreen line, the roof, slab sides leaning in.
    for y, zt, h in ((FRONT, FRAME_Z + .55, HALF - .12), (FRONT + .3, FRAME_Z + .75, HALF - .05),
                     (FRONT + .95, CAB_ROOF, HALF - .1), (CAB_Y1, CAB_ROOF, HALF - .1)):
        rings.append([(-HALF, y, FRAME_Z), (HALF, y, FRAME_Z), (HALF, y, FRAME_Z + .7), (h, y, zt),
                      (-h, y, zt), (-HALF, y, FRAME_Z + .7)])
    k.sharp_loft(cab, rings, chamfer=.04)
    # Three windscreen panes on the raked face, small door windows, doors, steps, mirrors.
    yb, zb, yt, zt = FRONT + .32, FRAME_Z + .82, FRONT + .9, CAB_ROOF - .08
    for x0, x1 in ((-1.12, -.4), (-.36, .36), (.4, 1.12)):
        K.windscreen(a, [(x1, yb, zb), (x0, yb, zb), (x0, yt, zt), (x1, yt, zt)], frame_mat='Undercarriage', wipers=1,
                     bar=.05)
    glass = a.part('Windows', 'Glass')
    fit = a.part('Cab_fit', 'Steel')
    dark = a.part('Door_panels', 'Undercarriage')
    for s in (-1, 1):
        x = s * (HALF - .07)
        glass.box((.012, .55, .35), loc=(x, -3.25, 2.15), rot=(0, s * .1, 0), bevel=0)
        dark.box((.012, .02, 1.1), loc=(s * (HALF + .004), -2.85, 1.7), bevel=0)
        K.handle(fit, (s * (HALF + .004), -3.0, 1.75), (s * (HALF + .004), -2.9, 1.75), (s, 0, 0), h=.025, r=.01)
        P.step(a, (s * (HALF - .05), -3.2, FRAME_Z - .2), w=.2, d=.45)
        K.mirror(fit, (s * (HALF - .1), FRONT + .7, 2.15), s, arm=.12, size=(.04, .12, .26))
        K.lamp(a, (s * .95, FRONT + .02, FRAME_Z + .4), (0, -1, 0), r=.08, mat='Armor', guard=True)
    K.chamfer_box(a.part('Bumper', 'Armor'), (HALF * 2 - .1, .25, .3), loc=(0, FRONT - .02, FRAME_Z - .05), c=.03)
    gr = a.part('Grille', 'Undercarriage')
    for i in range(8):
        gr.box((.05, .02, .28), loc=((i - 3.5) * .16, FRONT + .02, FRAME_Z + .35), bevel=0)
    # The sensor mast on the cab roof with the small spinning dish (`Radar`).
    rm = a.part('Sensor_stub', 'Steel')
    rm.cyl(.05, .1, loc=(-.55, -3.2, CAB_ROOF + .02), seg=8, bevel=0)
    r = a.pivot('Radar', (-.55, -3.2, 2.55))
    K.dish(a.part('Radar_dish', 'Armor', r), a.part('Radar_feed', 'Steel', r), (0, 0, .3), r=.32, normal=(0, -1, .3),
           seg=12)
    a.part('Radar_mast', 'Steel', r).cyl(.035, .3, loc=(0, 0, .15), seg=6, bevel=0)
    K.beacon(a, (.75, -3.0, CAB_ROOF))


def _body(a):
    sh = a.part('Shelter', 'Team')
    # The equipment body: sloped front and rear ends, flat roof.
    prof = [(BODY_Y0, FRAME_Z + .2), (BODY_Y1, FRAME_Z + .2), (BODY_Y1, BODY_Z1 - .35), (BODY_Y1 - .35, BODY_Z1),
            (BODY_Y0 + .35, BODY_Z1), (BODY_Y0, BODY_Z1 - .35)]
    k.extrude(sh, prof, HALF * 2, axis='X', chamfer=.04, corner=.03)
    dark = a.part('Door_panels', 'Undercarriage')
    fit = a.part('Steel', 'Steel')
    for s in (-1, 1):
        x = s * (HALF + .004)
        dark.box((.012, .85, 1.5), loc=(x, -1.2, 2.1), bevel=0)
        K.handle(fit, (x, -.85, 2.0), (x, -.85, 2.2), (s, 0, 0), h=.03, r=.012)
        K.grille(a, (x + s * .005, .9, 2.55), .7, .3, facing=(s, 0, 0), slats=4, frame_mat='Armor')
        a.part('Team_band', 'Team').box((.012, 6.2, .1), loc=(s * (HALF + .006), 1.0, 1.55), bevel=0)
        # Stowage boxes under the body between the axle groups.
        for y in (-.6, .4):
            k.block(a.part('Stowage', 'Armor'), (.3, .85, .4), loc=(s * (HALF - .15), y, FRAME_Z - .25), chamfer=.02)
    # Roof air-conditioning units and the roof boxes.
    vents = a.part('Vents', 'Armor')
    for y in (-1.6, -.6):
        k.block(vents, (1.0, .7, .3), loc=(.45, y, BODY_Z1), chamfer=.04)
        K.grille(a, (.45, y, BODY_Z1 + .31), .7, .45, facing=(0, 0, 1), slats=4, frame_mat='Armor')
    k.block(a.part('Roof_boxes', 'Armor'), (.6, 1.4, .25), loc=(-.6, -1.0, BODY_Z1), chamfer=.03)
    a.part('Kit_cables', 'Rubber').tube([(-.6, -.3, BODY_Z1 + .1), (-.4, .6, BODY_Z1 + .05), (0, 1.2, BODY_Z1 + .1)],
                                        .035, seg=5)
    a.part('Racks', 'Steel').tube([(-1.1, -2.0, BODY_Z1 + .02), (-1.1, -2.0, BODY_Z1 + .1), (-1.1, .3, BODY_Z1 + .1),
                                   (-1.1, .3, BODY_Z1 + .02)], .02, seg=4)
    K.ladder(a.part('Ladders', 'Steel'), (.7, BODY_Y1 + .05, FRAME_Z + .1), (.7, BODY_Y1 - .25, BODY_Z1 - .05),
             width=.4, step=.3)


def _array(a):
    """The hijack array on its turning mast (`Turret` > `Muzzle_main`): phased panel, yagis, feed horn."""
    k.lathe(a.part('Mast_ring', 'Steel'), [(.45, 0), (.45, .1), (.38, .14), (0, .14)], loc=(0, 1.6, BODY_Z1),
            seg=14, worn=(1,))
    t = a.pivot('Turret', (0, 1.6, 2.65 + .5))
    mast = a.part('Turret_mast', 'Armor', t)
    mast.cyl(.12, .45, loc=(0, 0, -.2), seg=10, bevel=0)
    k.block(a.part('Turret_armor', 'Armor', t), (.7, .5, .3), loc=(0, .05, -.05), chamfer=.04)
    for s in (-1, 1):
        mast.limb((s * .32, .05, 0), (s * .55, -.35, .2), .07, .07, bevel=0)
    # The panel tilted 20 degrees up, facing forward, its grid of cells and frame.
    tilt = (R90 + .35, 0, 0)
    k.block(a.part('Array_panel', 'Team', t), (1.9, .9, .12), loc=(0, -.42, .2), rot=tilt, chamfer=.03)
    cells = a.part('Array_cells', 'Undercarriage', t)
    m = K.frame((0, -.49, .22), tilt)
    from mathutils import Vector
    for i in range(6):
        for j in range(3):
            p = m @ Vector(((i - 2.5) * .29, (j - 1) * .26, 0))
            cells.box((.24, .2, .02), loc=tuple(p), rot=tilt, bevel=0)
    # Four yagi elements along the panel's top edge, the feed horn under it.
    yagi = a.part('Turret_steel', 'Steel', t)
    for x in (-.75, -.25, .25, .75):
        yagi.tube([(x, -.5, .68), (x, -1.15, .78)], .015, seg=4)
        for d in range(4):
            yy = -.6 - d * .15
            yagi.tube([(x - .12 + d * .015, yy, .7 + d * .015), (x + .12 - d * .015, yy, .7 + d * .015)], .008, seg=3)
    k.lathe(a.part('Feed_horn', 'Armor', t), [(.06, 0), (.08, .05), (.16, .3), (0, .3)], loc=(0, -.85, -.12),
            rot=K.FORWARD, seg=8, caps=(True, False))
    a.pivot('Muzzle_main', (0, -1.0, .2), t)


def _rear(a):
    gen = a.part('Generator', 'Armor')
    k.block(gen, (.9, .5, .7), loc=(-.65, REAR - .35, FRAME_Z - .05), chamfer=.04)
    K.grille(a, (-.65, REAR - .09, FRAME_Z + .3), .7, .35, facing=(0, 1, 0), slats=4, frame_mat='Armor')
    K.exhaust(a, (.9, REAR - .2, FRAME_Z - .35), r=.05, length=.25, direction=(0, 1, 0), muffler=False, cap=False)
    a.pivot('Point_exhaust', (.9, 4.5, 1.0))
    K.soot(a, (.9, REAR + .05, FRAME_Z - .35), radius=.45, k=.5)
    P.tread_wheel(a, (-1.0, 2.4, FRAME_Z + .1), .44, .28, 1, seg=10, rim_seg=6, tyre='Spare_wheel', rim='Spare_rim',
                  hub=False)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (.55, REAR - .3, FRAME_Z - .05), rot=(0, 0, 0))
    for s in (-1, 1):
        a.part('Tail_lamps', 'LavaGlow').box((.14, .01, .08), loc=(s * 1.1, REAR + .01, FRAME_Z - .12), bevel=0)
        P.mudflap(a, (s * TRACK, AXLES[3] + .65, .78), w=.42, h=.35)
        P.mudflap(a, (s * TRACK, AXLES[1] + .65, .78), w=.42, h=.35)
    K.whip_antenna(a.part('Antennas', 'Steel'), (1.1, 3.9, BODY_Z1), h=.7, r=.02, lean=.08)


def drone_hijack_vehicle(a):
    """The drone hijack vehicle: see the module docstring."""
    _running_gear(a)
    _cab(a)
    _body(a)
    _array(a)
    _rear(a)
    k.clean(a)


BUILDERS = {
    'drone_hijack_vehicle': (drone_hijack_vehicle, dict(ao_distance=.6, grime_height=.6)),
}
