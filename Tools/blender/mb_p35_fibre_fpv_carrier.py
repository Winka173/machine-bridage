"""Prompt 35 wave 6 (lane B): the fibre-optic FPV carrier rebuilt from scratch (spec: Tools/blender/specs/fibre_fpv_carrier.json).

An armoured 4x4 pickup (Land Cruiser 79 / Kozak-class conversion; the def's modelSize 4.6 x 1.9 x 2.0 m) carrying
fibre-optic FPV drones: the bonnet with its louvred grille and bull bar, the armoured four-door cab with small
thick windows, roof hatch and mirrors, four wheels with chunky tyres on beam axles with leaf springs; in the bed
the launch rack on its turntable (`Turret` > `Muzzle_main`): a tilted frame holding four quadcopters with their
charges and cameras, the two big fibre spools on their frame beside it, the cable guides; the mini-swarm launch box
on the cab roof (`Mount_rocket` > `Muzzle_rocket`: the def's free secondary), the operator's antenna mast, jerrycans,
a spare wheel, a net, lamps, steps and Team bands.

Its own body: nothing is taken from another wheeled model. Runtime nodes kept: `Turret`, `Muzzle_main`,
`Point_exhaust`, `Point_fire` (the wrapper adds `Part_wheel` / `Part_wheelb`); old part names `Hull`, `Bed`, `Rack`,
`Drones`, `Spools`, `Spool_frame`; new: `Mount_rocket`, `Muzzle_rocket`, `Axles`, `Stowage`. Metres, +Z up, -Y front,
+X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
WR, WW, TRACK = .4, .3, .78
AXLES = (-1.45, 1.35)
FRONT, REAR = -2.3, 2.3
HALF = .9
CAB_Y0, CAB_Y1, ROOF = -.85, .45, 1.82
BED_Z = 1.0


def _running_gear(a):
    a.part('Chassis', 'Undercarriage').box((1.0, 4.2, .2), loc=(0, 0, .62), bevel=0)
    susp = a.part('Suspension', 'Steel')
    for y in AXLES:
        for s in (-1, 1):
            P.tread_wheel(a, (s * TRACK, y, WR), WR, WW, s, seg=14, rim_seg=8, nuts=5, depth=.05)
            K.dust(a, (s * TRACK, y, .1), radius=.8, k=.3)
            K.leaf_spring(susp, s * .48, y, WR + .12, .9, leaves=4, w=.07)
        K.axle(a.part('Axles', 'Undercarriage'), y, WR, .62, r=.07, diff=True)
    a.pivot('Point_fire', (0, 0, 1.6))


def _body(a):
    hull = a.part('Hull', 'Team')
    # The bonnet: from the grille back to the windscreen, a gentle slope, cut corners.
    rings = []
    for y, zt, h in ((FRONT + .05, .98, HALF - .12), (FRONT + .28, 1.2, HALF - .04), (CAB_Y0, 1.28, HALF)):
        rings.append([(-h, y, .65), (h, y, .65), (h, y, zt - .08), (h - .08, y, zt), (-h + .08, y, zt), (-h, y, zt - .08)])
    k.sharp_loft(hull, rings, chamfer=.03)
    # The armoured cab: slab sides leaning in, a steep windscreen, a flat roof.
    cab = a.part('Cab', 'Team')
    rings = []
    for z, yf, h in ((.65, CAB_Y0, HALF), (1.28, CAB_Y0, HALF), (ROOF - .05, CAB_Y0 + .32, HALF - .2),
                     (ROOF, CAB_Y0 + .36, HALF - .23)):
        rings.append([(-h, yf, z), (h, yf, z), (h, CAB_Y1, z), (-h, CAB_Y1, z)])
    k.sharp_loft(cab, rings, chamfer=.03)
    # Windscreen panes, small thick side windows, door seams and handles, mirrors, steps.
    def fy(z):
        return CAB_Y0 + .32 * (z - 1.28) / (ROOF - .05 - 1.28) - .006
    z0, z1 = 1.33, ROOF - .1
    for s in (-1, 1):
        x0, x1 = s * .04, s * (HALF - .2)
        c = [(x0, fy(z0), z0), (x1, fy(z0), z0), (x1, fy(z1), z1), (x0, fy(z1), z1)]
        if s < 0:
            c = [c[1], c[0], c[3], c[2]]
        K.windscreen(a, c, frame_mat='Undercarriage', wipers=1, bar=.045)
    glass = a.part('Glass', 'Glass')
    fit = a.part('Steel', 'Steel')
    dark = a.part('Door_seams', 'Undercarriage')
    for s in (-1, 1):
        for y in (-.45, .1):
            glass.box((.012, .3, .2), loc=(s * (HALF - .095), y, 1.55), rot=(0, s * .35, 0), bevel=0)
            dark.box((.012, .015, .65), loc=(s * (HALF + .003), y + .2, 1.0), bevel=0)
            K.handle(fit, (s * (HALF + .003), y + .1, 1.2), (s * (HALF + .003), y + .17, 1.2), (s, 0, 0), h=.02,
                     r=.008)
        K.mirror(fit, (s * (HALF - .05), CAB_Y0 + .15, 1.45), s, arm=.1, size=(.03, .1, .16))
        P.step(a, (s * (HALF - .02), -.2, .5), w=.15, d=.8)
        a.part('Team_band', 'Team').box((.012, 1.2, .08), loc=(s * (HALF + .006), -.2, .85), bevel=0)
    K.hatch_round(a, (.25, -.15, ROOF), r=.25, periscopes=0, seg=10)
    # The grille, bull bar, lamps, tow hooks, the wheel arches.
    gr = a.part('Grille', 'Undercarriage')
    for i in range(6):
        gr.box((1.1, .02, .035), loc=(0, FRONT + .04, .8 + i * .055), bevel=0)
    bb = a.part('Bull_bar', 'Steel')
    bb.tube([(-.75, FRONT - .05, .55), (-.75, FRONT - .12, 1.0), (.75, FRONT - .12, 1.0), (.75, FRONT - .05, .55)], .035,
            seg=6)
    bb.tube([(-.75, FRONT - .1, .78), (.75, FRONT - .1, .78)], .03, seg=6)
    for s in (-1, 1):
        K.lamp(a, (s * .62, FRONT + .03, 1.02), (0, -1, 0), r=.07, mat='Undercarriage', guard=False)
        K.tow_hook(a.part('Kit_hooks', 'Steel'), (s * .4, FRONT - .02, .55), facing=(0, -1, 0), size=.06)
    fen = a.part('Fenders', 'Undercarriage')
    for s in (-1, 1):
        for y in AXLES:
            k.sweep(fen, [(-.06, -.02), (.06, -.02), (.06, .02), (-.06, .02)],
                    [(s * (HALF - .02), y + .5 * math.cos(u), WR + .45 * math.sin(u))
                     for u in [math.radians(d) for d in range(10, 180, 34)]])
    # The bed: tub, sides and tailgate, tail lamps, the exhaust under it.
    bed = a.part('Bed', 'Armor')
    k.block(bed, (HALF * 2, REAR - CAB_Y1 - .05, .1), loc=(0, (CAB_Y1 + REAR) / 2 + .02, BED_Z - .1), chamfer=.02)
    for s in (-1, 1):
        bed.box((.05, REAR - CAB_Y1 - .05, .38), loc=(s * (HALF - .025), (CAB_Y1 + REAR) / 2 + .02, BED_Z + .19),
                bevel=0)
        a.part('Tail_lamps', 'LavaGlow').box((.08, .01, .12), loc=(s * .78, REAR + .01, BED_Z + .1), bevel=0)
    bed.box((HALF * 2 - .1, .05, .38), loc=(0, REAR - .02, BED_Z + .19), bevel=0)
    K.exhaust(a, (.7, REAR - .1, .55), r=.03, length=.18, direction=(0, 1, 0), muffler=False, cap=False)
    a.pivot('Point_exhaust', (.7, 2.3, .7))
    K.soot(a, (.7, REAR + .05, .55), radius=.4, k=.45)


def _rack(a):
    """The FPV launch rack on its turntable in the bed (`Turret`): four quadcopters on a tilted frame."""
    k.lathe(a.part('Turntable', 'Steel'), [(.42, 0), (.42, .05), (.36, .08), (0, .08)], loc=(0, 1.2, BED_Z - .05),
            seg=14)
    t = a.pivot('Turret', (0, 1.2, .95))
    rack = a.part('Rack', 'Armor', t)
    tilt = (.45, 0, 0)
    k.block(rack, (1.2, .9, .05), loc=(0, -.05, .4), rot=tilt, chamfer=.015)
    for s in (-1, 1):
        rack.limb((s * .5, .15, 0), (s * .5, .25, .55), .05, .05, bevel=0)
        rack.limb((s * .5, -.3, 0), (s * .5, -.35, .25), .05, .05, bevel=0)
    from mathutils import Vector
    m = K.frame((0, -.05, .43), tilt)
    dr = a.part('Drones', 'Team', t)
    arms = a.part('Drone_arms', 'Undercarriage', t)
    rot = a.part('Drone_rotors', 'Rubber', t)
    chg = a.part('Drone_charges', 'Fuel', t)
    for i, (dx, dy) in enumerate(((-.28, -.2), (.28, -.2), (-.28, .22), (.28, .22))):
        c = m @ Vector((dx, dy, .05))
        k.block(dr, (.12, .2, .07), loc=tuple(c), rot=tilt, chamfer=.015)
        for ax, ay in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            p = m @ Vector((dx + ax * .11, dy + ay * .11, .07))
            arms.tube([tuple(c), tuple(p)], .012, seg=4)
            rot.cyl(.07, .01, loc=tuple(p + Vector((0, 0, .02))), rot=tilt, seg=8, bevel=0)
        chg.cyl(.035, .2, loc=tuple(m @ Vector((dx, dy - .12, .02))), rot=(tilt[0] + R90, 0, 0), seg=6, bevel=0)
        a.part('Drone_cams', 'Glass', t).box((.04, .02, .03), loc=tuple(m @ Vector((dx, dy - .11, .08))), rot=tilt,
                                              bevel=0)
    a.pivot('Muzzle_main', (0, -.4, .6), t)


def _spools(a):
    """The two fibre spools on their frame beside the rack, the cable guides to the rack."""
    fr = a.part('Spool_frame', 'Steel')
    for x in (-.55, .55):
        fr.box((.05, .05, .5), loc=(x, 2.0, BED_Z + .25), bevel=0)
    fr.tube([(-.6, 2.0, BED_Z + .5), (.6, 2.0, BED_Z + .5)], .025, seg=6)
    for x in (-.28, .28):
        k.lathe(a.part('Spools', 'Hazard'), [(.22, -.13), (.22, -.11), (.12, -.1), (.12, .1), (.22, .11), (.22, .13)],
                loc=(x, 2.0, BED_Z + .5), rot=(0, R90, 0), seg=14, worn=(0, 5))
        a.part('Spool_fibre', 'Medical').cyl(.17, .2, loc=(x, 2.0, BED_Z + .5), rot=(0, R90, 0), seg=14, bevel=0)
    a.part('Kit_cables', 'Medical').tube([(-.28, 1.85, BED_Z + .55), (-.15, 1.55, BED_Z + .65), (0, 1.35, BED_Z + .6)],
                                         .008, seg=3)


def _roof(a):
    """The mini-swarm launch box on the cab roof (`Mount_rocket`), the operator's antenna mast, stowage."""
    m = a.pivot('Mount_rocket', (-.35, .1, ROOF + .02))
    k.block(a.part('Launcher_box', 'Armor', m), (.5, .6, .22), loc=(0, 0, .02), chamfer=.02)
    tubes = a.part('Tubes', 'Undercarriage', m)
    for i in range(3):
        for j in range(2):
            tubes.cyl(.06, .02, loc=(-.15 + i * .15, -.305, .08 + j * .1), rot=K.FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_rocket', (0, -.33, .13), m)
    K.whip_antenna(a.part('Antennas', 'Steel'), (.6, .35, ROOF), h=.2, r=.02)
    k.block(a.part('Antennas', 'Steel'), (.08, .08, .1), loc=(.6, .35, ROOF), chamfer=0)
    a.part('Antennas', 'Steel').cyl(.1, .06, loc=(.6, .35, ROOF + .22), seg=10, bevel=0)
    # Stowage: jerrycans and a spare wheel behind the cab, a rolled net on the bed side.
    for x in (-.65, -.45):
        K.jerrycan(a.part('Jerrycans', 'Fuel'), (x, CAB_Y1 + .15, BED_Z), rot=(0, 0, 0), scale=.85)
    P.tread_wheel(a, (.55, CAB_Y1 + .2, BED_Z + .32), .32, .22, 1, seg=12, rim_seg=6, tyre='Spare_wheel',
                  rim='Spare_rim', hub=False)
    K.net_roll(a.part('Stowage', 'Canvas'), a.part('Kit_straps', 'Undercarriage'), (-HALF + .1, 1.4, BED_Z + .42),
               length=1.1, r=.08, axis='Y')


def fibre_fpv_carrier(a):
    """The fibre-optic FPV carrier: see the module docstring."""
    _running_gear(a)
    _body(a)
    _rack(a)
    _spools(a)
    _roof(a)
    k.clean(a)


BUILDERS = {
    'fibre_fpv_carrier': (fibre_fpv_carrier, dict(ao_distance=.5, grime_height=.55)),
}
