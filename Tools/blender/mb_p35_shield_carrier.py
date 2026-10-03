"""Prompt 35 wave 6 (lane B): the shield carrier rebuilt from scratch (spec: Tools/blender/specs/shield_carrier.json).

A Boxer 8x8 drive module carrying a field-emitter mission module (the def's modelSize 6.29 x 2.46 x 2.84 m; the hull
0.8 x the real Boxer): the tall faceted hull with its V belly, the steep two-step glacis, the driver's hatch and
periscopes front left, the engine on the front right (the grille louvres and the exhaust on the right side), eight
wheels on four axles (two pairs: the front pair close, a gap, the rear pair) with double wishbones and the axle
beams, the bolted add-on side armour, vision blocks; the mission module behind the cab line: the field emitter on
a turned drum with its cooling fins, three prongs carrying the reflector dish, the glowing Team ring and core
(TeamGlow), the power cabinet with cable runs; the remote 12.7 mm station on a raised ring on the front right
(`Turret`), smoke dischargers, stowage bins, jerrycans, the rear ramp door with steps, mud flaps, lamps, mirrors,
whips and Team bands.

Its own hull: nothing is taken from another wheeled model. Runtime nodes kept: `Turret`, `Main_cannon`,
`Muzzle_brake`, `Muzzle_main`, `Point_exhaust`, `Point_fire`; old part names `Emitter*`, `Chassis`, `Hull`, `Armor`;
new for the gate: `Axles`, `Glass`, `Stowage`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
WR, WW, TRACK = .45, .32, 1.0
AXLES = (-2.05, -1.05, .85, 1.85)
FRONT, REAR = -3.12, 3.1
HALF = 1.2
ROOF = 1.98


def _running_gear(a):
    frame = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        K.chamfer_box(frame, (.12, 5.6, .24), loc=(s * .45, 0, .62), c=.02)
    susp = a.part('Suspension', 'Steel')
    for y in AXLES:
        for s in (-1, 1):
            P.tread_wheel(a, (s * TRACK, y, WR), WR, WW, s, seg=12, rim_seg=8, nuts=0, depth=.05)
            K.dust(a, (s * TRACK, y, .1), radius=.9, k=.28)
            susp.tube([(s * .45, y - .2, WR - .06), (s * (TRACK - .2), y, WR - .02), (s * .45, y + .2, WR - .06)],
                      .03, seg=5)
        K.axle(a.part('Axles', 'Undercarriage'), y, WR, .55, r=.09, diff=y in (AXLES[1], AXLES[2]))
    a.pivot('Point_fire', (0, 1.8, 1.8))


def _hull(a):
    hull = a.part('Hull', 'Team')
    rings = []
    # Sections nose to tail: the V belly, vertical lower sides, the upper sides leaning in, a flat roof.
    for y, yb, zr in ((FRONT, FRONT + .5, 1.22), (FRONT + .35, FRONT + .5, 1.55), (FRONT + 1.05, FRONT + 1.0, ROOF),
                      (REAR - .08, REAR, ROOF), (REAR, REAR, ROOF - .1)):
        rings.append([(-.5, yb, .55), (.5, yb, .55), (HALF, yb, .9), (HALF, y, 1.45), (HALF - .2, y, zr),
                      (-HALF + .2, y, zr), (-HALF, y, 1.45), (-HALF, yb, .9)])
    k.sharp_loft(hull, rings, chamfer=.04)
    # The bolted add-on side armour panels (between the axle pairs), their bolts.
    arm = a.part('Armor', 'Armor')
    bolts = a.part('Kit_bolts', 'Steel')
    for s in (-1, 1):
        for y, L in ((-1.55, .55), (-.1, 1.55), (1.35, .45), (2.55, .7)):
            k.block(arm, (.05, L, .5), loc=(s * (HALF + .025), y, 1.15), chamfer=.015)
            for dy in (-L * .38, L * .38):
                bolts.box((.03, .04, .04), loc=(s * (HALF + .055), y + dy, 1.32), bevel=0)
        # Fenders over each wheel pair, mud flaps behind them.
        fen = a.part('Fenders', 'Undercarriage')
        for y0, y1 in ((AXLES[0] - .55, AXLES[1] + .55), (AXLES[2] - .55, AXLES[3] + .55)):
            k.block(fen, (.34, y1 - y0, .04), loc=(s * TRACK, (y0 + y1) / 2, 1.0), chamfer=0)
            P.mudflap(a, (s * TRACK, y1, .75), w=.36, h=.3)
    # The glacis: the driver's hatch and periscopes front left, the engine louvres front right, lamps, hooks.
    g0, g1 = (FRONT + .35, 1.55), (FRONT + 1.05, ROOF)
    ang = math.atan2(g1[1] - g0[1], g1[0] - g0[0])

    def on_glacis(f, x, up=.0):
        y = g0[0] + (g1[0] - g0[0]) * f
        z = g0[1] + (g1[1] - g0[1]) * f
        return (x, y - math.sin(ang) * up, z + math.cos(ang) * up)
    K.hatch_rect(a, (.55, FRONT + 1.45, ROOF), size=(.5, .55))
    for dx in (-.1, .2):
        K.periscope(a, on_glacis(.75, .45 + dx, .02), facing=(0, -1, 0), size=(.12, .09, .07))
    K.grille(a, on_glacis(.5, -.55, .02), .7, .5, facing=(0, -math.sin(ang), math.cos(ang)), slats=6,
             frame_mat='Armor')
    K.exhaust(a, (-HALF - .04, -1.6, 1.5), r=.05, length=.25, direction=(0, 0, 1), muffler=False, cap=True)
    a.pivot('Point_exhaust', (-.9, -1.6, 1.8))
    K.soot(a, (-HALF - .05, -1.6, 1.8), radius=.5, k=.45)
    for s in (-1, 1):
        K.lamp(a, (s * .9, FRONT + .1, 1.15), (0, -1, 0), r=.07, mat='Armor', guard=False)
        K.mirror(a.part('Cab_fit', 'Steel'), (s * (HALF - .2), FRONT + .55, 1.6), s, arm=.05, size=(.03, .1, .16))
        K.smoke_dischargers(a, HALF - .15, FRONT + 1.15, ROOF - .02, s, count=2)
    # Vision blocks on the sides, the rear ramp door with its steps and lamps.
    glass = a.part('Glass', 'Glass')
    for s in (-1, 1):
        for y in (-1.7, .1, 1.0):
            glass.box((.02, .22, .1), loc=(s * (HALF - .1), y, 1.7), rot=(0, s * .45, 0), bevel=0)
    K.plate(a.part('Hatches', 'Armor'), (1.1, .04, 1.05), loc=(0, REAR + .015, 1.15))
    K.hinge(a.part('Kit_hinges', 'Steel'), (-.4, REAR + .04, .64), (.4, REAR + .04, .64), r=.025, knuckles=3)
    K.handle(a.part('Kit_handles', 'Steel'), (.4, REAR + .04, 1.2), (.4, REAR + .04, 1.4), (0, 1, 0), h=.04)
    for s in (-1, 1):
        a.part('Tail_lamps', 'LavaGlow').box((.1, .01, .07), loc=(s * .95, REAR + .02, 1.6), bevel=0)
        P.step(a, (s * .4, REAR + .1, .58), w=.3, d=.18)
        a.part('Team_band', 'Team').box((.012, 4.2, .1), loc=(s * (HALF + .006), .25, 1.47), bevel=0)
    # Stowage: bins on the rear quarters, jerrycans, a net roll, a tow cable along the roof edge.
    st = a.part('Stowage', 'Canvas')
    P.toolbox(a, (-HALF - .08, 1.95, 1.55), (.16, 1.3, .45), mat='Armor')
    k.block(a.part('Crates', 'Crate'), (.5, .4, .3), loc=(.75, 2.8, ROOF), chamfer=.03)
    a.part('Kit_straps', 'Undercarriage').box((.52, .05, .31), loc=(.75, 2.8, ROOF + .15), bevel=0)
    K.net_roll(st, a.part('Kit_straps', 'Undercarriage'), (0, REAR - .3, ROOF + .02), length=1.6, r=.12, axis='X')
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.9, 2.85, ROOF), h=.55, r=.02, lean=.12)


def _emitter(a):
    """The field emitter on the mission module roof: a finned drum, three prongs, the dish, the glowing ring and core."""
    e = a.pivot('Emitter', (0, 1.25, ROOF - .14))
    k.lathe(a.part('Emitter_base', 'Armor', e), [(.62, 0), (.62, .1), (.55, .14), (.5, .32), (.42, .36), (0, .36)],
            seg=16, worn=(1, 3))
    fins = a.part('Emitter_fins', 'Steel', e)
    for i in range(8):
        u = i * TAU / 8
        fins.box((.16, .02, .2), loc=(math.cos(u) * .55, math.sin(u) * .55, .22), rot=(0, 0, u), bevel=0)
    pr = a.part('Emitter_prongs', 'Armor', e)
    for i in range(3):
        u = i * TAU / 3 + R90
        pr.limb((math.cos(u) * .32, math.sin(u) * .32, .34), (math.cos(u) * .5, math.sin(u) * .5, .68), .07, .06,
                bevel=0)
    k.lathe(a.part('Emitter_dish', 'Steel', e), [(.15, .5), (.45, .62), (.62, .74), (.6, .78), (.42, .68),
                                                 (.12, .58)], seg=16, worn=(2,))
    k.ring(a.part('Emitter_ring', 'TeamGlow', e), [(.5, .76), (.58, .76), (.58, .8), (.5, .8)], seg=16)
    a.part('Emitter_core', 'TeamGlow', e).sphere(.17, loc=(0, 0, .82), seg=10, rings=6)
    k.lathe(a.part('Emitter_glow', 'Steel', e), [(.06, .58), (.06, .7), (0, .72)], seg=8)
    # The power cabinet behind it and the cable runs.
    k.block(a.part('Power_cabinet', 'Armor'), (.8, .7, .45), loc=(-.4, 2.35, ROOF), chamfer=.04)
    K.grille(a, (-.4, 2.71, ROOF + .22), .6, .25, facing=(0, 1, 0), slats=4, frame_mat='Armor')
    cab = a.part('Kit_cables', 'Rubber')
    for x in (-.6, -.25):
        cab.tube([(x, 2.0, ROOF + .2), (x, 1.75, ROOF + .15), (x * .6, 1.55, ROOF + .25)], .03, seg=5)
    a.part('Team_band', 'Team').box((1.12, .02, .1), loc=(0, 1.995, ROOF + .3), bevel=0)


def _rws(a):
    """The remote 12.7 mm station on a raised ring over the commander's hatch, front right (`Turret`)."""
    P.raised_gun(a, (-.55, -1.5, ROOF - .3), parent=None, pivot='Turret', barrel='Main_cannon', brake='Muzzle_brake',
                 muzzle='Muzzle_main', riser=.04, ring_r=.28, post=.15, length=.9, shield=False, ring=True,
                 mat='Armor', tag='')
    k.block(a.part('Rws_sensor', 'Armor'), (.22, .26, .2), loc=(-.85, -1.45, ROOF + .02), chamfer=.02)
    a.part('Glass', 'Glass').box((.16, .012, .1), loc=(-.85, -1.585, ROOF + .14), bevel=0)


def shield_carrier(a):
    """The shield carrier: see the module docstring."""
    _running_gear(a)
    _hull(a)
    _emitter(a)
    _rws(a)
    k.clean(a)


BUILDERS = {
    'shield_carrier': (shield_carrier, dict(ao_distance=.5, grime_height=.6)),
}
