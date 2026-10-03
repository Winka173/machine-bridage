"""Prompt 35 wave 1 (lane B): the counter-battery radar rebuilt from scratch (spec:
Tools/blender/specs/counter_battery_radar.json).

An AN/TPQ-53 on its FMTV 6x6 (the def's modelSize 6.65 x 2.3 x 2.89 m, about 0.9 x real): the FMTV's flat-fronted
tilt cab with the wide grille, two-pane windscreen and rounded roof edge; on the bed the generator set with its fan
grilles and exhaust, the electronics cabinets and the cable reels; at the rear the antenna turntable and the large
flat phased-array panel standing tilted back on its yoke (the sheet's "flat rectangular radar panel, about a third
of the length"), its face divided into tiles, the IFF strip along its top, the cooling ducts on its back; levelling
jacks at the rear corners; six wheels (single front axle, rear tandem); the M2 on a raised ring over the cab.

Runtime nodes kept: `Radar` (the array's pivot: the runtime turns it, ModelLibrary's spinner pattern), `Mount_mg` /
`Muzzle_mg` (the main weapon: mainSlot mg, mainAim Free), `Point_exhaust`, `Point_fire`.
Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
WR, WW, TRACK = .49, .36, .84
AXLES = (-2.25, .95, 2.3)
FRONT, REAR = -3.32, 3.32
HALF = 1.1
CAB_Y0, CAB_Y1, CAB_Z0, ROOF = -3.2, -1.62, 1.0, 2.32
FLOOR = 1.22
TILT = .38                      # the array's lean back from upright (radians)


def _chassis(a):
    frame = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        K.chamfer_box(frame, (.11, 6.3, .26), loc=(s * .44, 0, .9), c=.02)
    for y in (-2.8, -.4, 1.7, 3.0):
        frame.box((.8, .08, .14), loc=(0, y, .9), bevel=0)
    for y in AXLES:
        for s in (-1, 1):
            P.tread_wheel(a, (s * TRACK, y, WR), WR, WW, s, seg=12, rim_seg=8)
            K.dust(a, (s * TRACK, y, .15), radius=.95, k=.27)
        K.axle(a.part('Axles', 'Undercarriage'), y, WR, TRACK - .1, r=.075, diff=False)
    susp = a.part('Suspension', 'Steel')
    for s in (-1, 1):
        P.leaf_pack(susp, s * .44, AXLES[0], WR + .18, 1.05, leaves=3, w=.08)
        P.leaf_pack(susp, s * .44, (AXLES[1] + AXLES[2]) / 2, WR + .16, 1.6, leaves=4, w=.09)
    fen = a.part('Fenders', 'Undercarriage')
    for s in (-1, 1):
        k.sweep(fen, [(-.2, -.012), (.2, -.012), (.2, .012), (-.2, .012)],
                [(s * TRACK, AXLES[1] - .66, WR + .3), (s * TRACK, AXLES[1] - .5, WR + .58),
                 (s * TRACK, AXLES[2] + .5, WR + .58), (s * TRACK, AXLES[2] + .66, WR + .3)])
        P.mudflap(a, (s * TRACK, AXLES[2] + .68, WR + .46), w=.4, h=.42)
    P.fuel_tank(a, (.86, -.55, .92), 1.0, .23, straps=1)
    P.toolbox(a, (-.86, -.6, .92), (.3, .7, .44))
    a.pivot('Point_fire', (0, -.5, 1.9))


def _cab(a):
    team = a.part('Cab', 'Team')
    dark = a.part('Cab_dark', 'Undercarriage')
    # Side profile: upright grille face, the windscreen a little raked, a rounded roof edge, the flat back.
    prof = [(CAB_Y1, CAB_Z0), (CAB_Y0, CAB_Z0), (CAB_Y0, CAB_Z0 + .62), (CAB_Y0 + .1, ROOF - .2),
            (CAB_Y0 + .2, ROOF - .05), (CAB_Y0 + .36, ROOF), (CAB_Y1 + .1, ROOF), (CAB_Y1, ROOF - .08)]
    k.extrude(team, prof, HALF * 2, axis='X', chamfer=.06, corner=.05)
    # The front: the big grille with its brush guard, the lamps in the fender corners, the bumper.
    K.grille(a, (0, CAB_Y0 - .01, CAB_Z0 + .32), 1.3, .44, facing=(0, -1, 0), slats=6, frame_mat='Undercarriage')
    guard = a.part('Brush_guard', 'Steel')
    guard.tube([(-.75, CAB_Y0 - .08, CAB_Z0 - .05), (-.75, CAB_Y0 - .1, CAB_Z0 + .58), (.75, CAB_Y0 - .1, CAB_Z0 + .58),
                (.75, CAB_Y0 - .08, CAB_Z0 - .05)], .025, seg=5)
    for x in (-.25, .25):
        guard.tube([(x, CAB_Y0 - .09, CAB_Z0 - .05), (x, CAB_Y0 - .1, CAB_Z0 + .58)], .02, seg=4)
    bump = a.part('Bumper', 'Steel')
    K.chamfer_box(bump, (HALF * 2, .2, .26), loc=(0, FRONT + .1, .88), c=.03)
    for s in (-1, 1):
        K.lamp(a, (s * .88, CAB_Y0 - .01, CAB_Z0 + .3), (0, -1, 0), r=.075, mat='Undercarriage', guard=False)
        bump.box((.1, .06, .1), loc=(s * .55, FRONT - .02, .8), bevel=0)
    # Windscreen: two panes, the centre post, wipers.
    z0, z1 = CAB_Z0 + .68, ROOF - .24

    def fy(z):
        return CAB_Y0 + .1 * (z - CAB_Z0 - .62) / (ROOF - .2 - CAB_Z0 - .62) - .006
    for s in (-1, 1):
        x0, x1 = s * .05, s * (HALF - .12)
        c = [(x0, fy(z0), z0), (x1, fy(z0), z0), (x1, fy(z1), z1), (x0, fy(z1), z1)]
        if s < 0:
            c = [c[1], c[0], c[3], c[2]]
        K.windscreen(a, c, frame_mat='Undercarriage', wipers=1, bar=.035)
    glass = a.part('Glass', 'Glass')
    fit = a.part('Cab_fit', 'Steel')
    for s in (-1, 1):
        x = s * (HALF + .004)
        for y in (CAB_Y0 + .25, CAB_Y1 - .2):
            dark.box((.01, .015, ROOF - CAB_Z0 - .2), loc=(x, y, (ROOF + CAB_Z0) / 2 - .05), bevel=0)
        glass.box((.012, .7, .46), loc=(s * (HALF + .002), (CAB_Y0 + CAB_Y1) / 2 + .05, ROOF - .42), bevel=0)
        K.handle(fit, (x, CAB_Y1 - .4, CAB_Z0 + .55), (x, CAB_Y1 - .3, CAB_Z0 + .55), (s, 0, 0), h=.02, r=.01)
        P.step(a, (s * (HALF - .12), (CAB_Y0 + CAB_Y1) / 2, .66), w=.4)
        fit.tube([(x, CAB_Y0 + .2, ROOF - .3), (x + s * .04, CAB_Y0 + .18, ROOF - .3),
                  (x + s * .04, CAB_Y0 + .18, CAB_Z0 + .7)], .013, seg=4)
        a.part('Mirrors', 'Undercarriage').box((.035, .12, .3), loc=(x + s * .055, CAB_Y0 + .18, ROOF - .55),
                                               bevel=0)
        a.part('Team_band', 'Team').box((.012, 1.2, .09), loc=(s * (HALF + .008), (CAB_Y0 + CAB_Y1) / 2,
                                                               CAB_Z0 + .2), bevel=0)
    glass.box((1.3, .012, .34), loc=(0, CAB_Y1 - .005, ROOF - .4), bevel=0)
    P.raised_gun(a, (.4, CAB_Y1 - .55, ROOF), pivot='Mount_mg', barrel='MG_barrel', brake='MG_flash',
                 muzzle='Muzzle_mg', riser=.1, ring_r=.38, post=.15, length=1.0, shield_k=.75, tag='_mg')
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.9, CAB_Y1 - .15, ROOF - .05), h=.6, r=.02)


def _bed(a):
    bed = a.part('Bed', 'Armor')
    K.chamfer_box(bed, (HALF * 2, 4.8, .16), loc=(0, .9, FLOOR - .08), c=.02)
    for s in (-1, 1):
        bed.box((.05, 4.8, .14), loc=(s * (HALF - .02), .9, FLOOR + .07), bevel=0)
        a.part('Team_band', 'Team').box((.012, 4.4, .08), loc=(s * (HALF + .012), .9, FLOOR + .02), bevel=0)
    # The generator set behind the cab: housing, fan grilles each side, the exhaust, its control panel.
    gen = a.part('Generator', 'Armor')
    K.chamfer_box(gen, (1.9, 1.2, .9), loc=(0, -.9, FLOOR + .45), c=.05)
    for s in (-1, 1):
        K.grille(a, (s * .955, -.9, FLOOR + .5), .8, .5, facing=(s, 0, 0), slats=4, frame_mat='Armor')
    for x in (-.45, .45):
        k.ring(a.part('Fan_grilles', 'Undercarriage'), [(.2, 0), (.24, 0), (.24, .03), (.2, .03)],
               loc=(x, -.9, FLOOR + .9), seg=10)
        a.part('Fan_grilles', 'Undercarriage').cyl(.2, .01, loc=(x, -.9, FLOOR + .91), seg=10, bevel=0)
    K.panel(a, a.part('Generator_panel', 'Armor'), (.5, .35), (0, -.29, FLOOR + .5), (0, 1, 0), rivet=0)
    K.exhaust(a, (.7, -1.4, FLOOR + .9), r=.045, length=.45, direction=(0, 0, 1), muffler=False, cap=True)
    a.pivot('Point_exhaust', (.7, -1.4, FLOOR + 1.42))
    # Electronics cabinets, the cable reels, a ladder up the left side.
    cab = a.part('Cabinets', 'Armor')
    K.chamfer_box(cab, (.55, .7, .75), loc=(.72, .25, FLOOR + .375), c=.03)
    K.chamfer_box(cab, (.55, .55, .55), loc=(-.72, .2, FLOOR + .275), c=.03)
    fit = a.part('Kit_latches', 'Steel')
    for x, h in ((.72, .75), (-.72, .55)):
        fit.box((.4, .012, .03), loc=(x, -.11 if h > .6 else -.08, FLOOR + h * .6), bevel=0)
        fit.box((.04, .015, .1), loc=(x + .18, -.11 if h > .6 else -.08, FLOOR + h * .45), bevel=0)
    reel = a.part('Cable_reels', 'Undercarriage')
    for x in (0,):
        k.lathe(reel, [(.08, -.12), (.26, -.12), (.26, -.1), (.18, -.1), (.18, .1), (.26, .1), (.26, .12),
                       (.08, .12)], loc=(x, .35, FLOOR + .3), rot=(0, R90, 0), seg=8)
    reel.box((.4, .06, .32), loc=(0, .35, FLOOR + .16), bevel=0)
    # Rear: levelling jacks, tail lamps, the tow pintle.
    for s in (-1, 1):
        K.outrigger(a.part('Jacks', 'Armor'), a.part('Kit_hooks', 'Steel'), (s * .5, REAR - .25, 1.0), s,
                    reach=.4, drop=.55, w=.15)
        a.part('Tail_lamps', 'Undercarriage').box((.2, .05, .1), loc=(s * .78, REAR - .05, .95), bevel=0)
        a.part('Tail_lenses', 'LavaGlow').box((.16, .01, .07), loc=(s * .78, REAR - .02, .95), bevel=0)


def _radar(a):
    """The antenna on its turntable: the `Radar` pivot carries the yoke and the tilted phased-array panel."""
    k.ring(a.part('Turntable', 'Steel'), [(.5, 0), (.62, 0), (.62, .12), (.5, .12)], loc=(0, 2.05, FLOOR), seg=16)
    r = a.pivot('Radar', (0, 2.05, FLOOR + .12))
    yoke = a.part('Radar_yoke', 'Armor', r)
    k.lathe(yoke, [(.5, 0), (.5, .08), (.36, .14), (.3, .32)], seg=14, worn=(1,))
    for s in (-1, 1):
        K.chamfer_box(yoke, (.14, .4, .7), loc=(s * .55, .05, .55), c=.03)
    yoke.box((1.24, .3, .16), loc=(0, .05, .32), bevel=0)
    # The array: 2.2 x 1.65 m panel, 0.22 thick, leaning back TILT between the yoke arms.
    W, H, T = 2.2, 1.65, .22
    c, sn = math.cos(TILT), math.sin(TILT)
    ctr = (0, .12 + sn * .3, .8)
    rot = (-TILT, 0, 0)
    m = K.frame(ctr, rot)

    def at(x, y, z):
        return K._at(m, (x, y, z))
    pan = a.part('Radar_panel', 'Armor', r)
    K.chamfer_box(pan, (W, T, H), loc=ctr, rot=rot, c=.04)
    face = a.part('Radar_face', 'Undercarriage', r)
    face.box((W - .12, .02, H - .2), loc=at(0, -T / 2 - .005, -.04), rot=rot, bevel=0)
    seams = a.part('Radar_seams', 'Steel', r)
    for i in range(1, 6):
        x = -W / 2 + .06 + i * (W - .12) / 6
        seams.box((.02, .025, H - .2), loc=at(x, -T / 2 - .012, -.04), rot=rot, bevel=0)
    for j in range(1, 4):
        z = -H / 2 + .06 + j * (H - .2) / 4
        seams.box((W - .12, .025, .02), loc=at(0, -T / 2 - .012, z), rot=rot, bevel=0)
    iff = a.part('Radar_iff', 'Team', r)
    K.chamfer_box(iff, (W - .2, .14, .14), loc=at(0, -.02, H / 2 + .08), rot=rot, c=.02)
    # Back: the cooling ducts and the electronics boxes, the elevation struts down to the yoke.
    back = a.part('Radar_back', 'Steel', r)
    for x in (-.65, 0, .65):
        back.box((.28, .1, H - .3), loc=at(x, T / 2 + .05, 0), rot=rot, bevel=0)
    for s in (-1, 1):
        back.tube([at(s * .55, T / 2, -H * .2), (s * .55, .35, .4)], .035, seg=6)
    a.part('Radar_lamp', 'Alloy', r).box((.08, .08, .06), loc=at(-W / 2 + .1, -.02, H / 2 + .18), rot=rot, bevel=0)


def counter_battery_radar(a):
    """The counter-battery radar: see the module docstring."""
    _chassis(a)
    _cab(a)
    _bed(a)
    _radar(a)
    k.clean(a)


BUILDERS = {
    'counter_battery_radar': (counter_battery_radar, dict(ao_distance=.55, grime_height=.7)),
}
