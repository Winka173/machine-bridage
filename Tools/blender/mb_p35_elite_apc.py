"""Prompt 35 wave 7 (lane C): the elite infantry fighting vehicle rebuilt from scratch (spec: Tools/blender/specs/elite_apc.json).

A BMP-3 with the unmanned Epokha (Bumerang-BM) module (unit_refs: M2 Bradley / BMP-3 as the base chassis, the 2A42
30 mm; the ifv it is the elite of is the Bradley, so this one is the BMP-3 line; the def's modelSize 6.31 x 3.47 x
3.02 m): the low wide hull with the long flat glacis, the folded splash board and the trim vane, the two bow
machine-gun ports, six road wheels a side with the front idler, the rear sprocket and three return rollers, the
float boxes over the tracks, the rear doors with steps under the raised engine deck; the module on its ring with its
black armour cheeks, the 30 mm on its cradle with the double-baffle muzzle, the coaxial MG (the def's `mg_coax`),
two Kornet launchers either side on elevating arms (the def's `atgm`, aimed with the turret), the gunner's and the
commander's sights, smoke dischargers, aerials and stowage. Elite marks (DECISIONS 25B2): the team-coloured body,
black armour (EliteBlack), gilded bands and red-glowing sights.

Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Coax`, `Muzzle_coax`, `Launcher_arm`,
`Launcher_box`, `Tubes`, `Muzzle_missile`, `Hatches`, `Point_exhaust`, `Point_fire`. Metres, +Z up, -Y front,
+X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
BLACK = 'EliteBlack'
BODY = 'Team'
TX, TW = 1.25, .5
WR = .33
WHEELS = (-1.85, -1.08, -.31, .46, 1.23, 2.0)
TOP = 1.5
NOSE, TAIL = -2.85, 3.1
TUR = (0, .1, TOP)


def _hull(a):
    hull = a.part('Hull', BODY)
    # The BMP-3 profile: the lower nose, the long flat glacis, a flat roof rising to the engine deck at the rear,
    # the near-vertical rear plate with the doors.
    prof = [(NOSE, .62), (NOSE + .2, .82), (-1.0, TOP - .12), (1.4, TOP - .05), (1.6, TOP + .08), (TAIL - .05, TOP + .08),
            (TAIL, .5), (-2.4, .42)]
    k.extrude(hull, prof, 2.5, axis='X', chamfer=.05, corner=.025)
    low = a.part('Hull_lower', BLACK)
    k.extrude(low, [(NOSE + .15, .6), (-2.35, .4), (2.95, .4), (3.0, .9)], (TX - TW / 2) * 2, axis='X', chamfer=.02)
    # Float boxes over the tracks (the BMP-3's side "skirts"), the fenders, gold bands.
    for s in (-1, 1):
        K.fender(a.part('Fenders', BODY), TX + .02, NOSE + .25, TAIL - .05, 1.02, .56, s, lip=.03)
        sk = a.part('Skirts', BLACK)
        for j in range(4):
            K.plate(sk, (.16, 1.25, .34), loc=(s * (TX + .32), -1.9 + j * 1.3, .88), chamfer=.015)
        a.part('Team_band', 'Gilded').box((.012, 4.8, .06), loc=(s * (TX + .405), .05, .96), bevel=0)
    # The folded splash board and trim vane on the glacis, the bow MG ports, lamps, tow hooks.
    g0, g1 = (NOSE + .2, .82), (-1.0, TOP - .12)
    ang = math.atan2(g1[1] - g0[1], g1[0] - g0[0])
    gy, gz = (g0[0] + g1[0]) / 2, (g0[1] + g1[1]) / 2
    K.plate(a.part('Trim_vane', BLACK), (2.3, .7, .04), loc=(0, gy - .2, gz + .04), rot=(ang, 0, 0), chamfer=.01)
    rib = a.part('Trim_vane_ribs', BLACK)
    for x in (-.9, -.3, .3, .9):
        rib.box((.04, .66, .05), loc=(x, gy - .2, gz + .07), rot=(ang, 0, 0), bevel=0)
    for s in (-1, 1):
        x = s * .95
        k.lathe(a.part('MG_bow_ball', BLACK), [(.1, 0), (.12, .06), (.1, .12)], loc=(x, NOSE + .35, .9),
                rot=K.FORWARD, seg=8)
        a.part('MG_bow', 'Steel').cyl(.025, .45, loc=(x, NOSE + .1, .9), rot=K.FORWARD, seg=6, bevel=0)
        K.lamp(a, (s * 1.12, -1.6, TOP - .06), (0, -1, .15), r=.065, guard=True, mat=BLACK)
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .55, NOSE - .02, .62), facing=(0, -1, 0), size=.07)
    C.hatch(a, (0, -1.2, TOP - .1), r=.25)
    for x in (-.25, 0, .25):
        K.periscope(a, (x, -1.48, TOP - .1), facing=(0, -1, .2), size=(.12, .07, .06), mat=BLACK)
    # The rear: two doors with vision blocks and steps, the troop roof hatches over them, the engine deck grilles.
    for s in (-1, 1):
        dr = a.part('Doors', BLACK)
        K.plate(dr, (.62, .05, .85), loc=(s * .38, TAIL + .03, 1.0), chamfer=.012)
        a.part('Glass', 'Glass').box((.14, .01, .08), loc=(s * .38, TAIL + .06, 1.25), bevel=0)
        K.handle(a.part('Kit_steel', 'Steel'), (s * .2, TAIL + .07, .95), (s * .2, TAIL + .07, 1.1), (0, 1, 0), h=.04)
        K.hinge(a.part('Kit_steel', 'Steel'), (s * .7, TAIL + .05, .7), (s * .7, TAIL + .05, 1.3), r=.025, knuckles=2)
        k.block(a.part('Steps', 'Steel'), (.5, .22, .04), loc=(s * .38, TAIL + .15, .5), chamfer=0)
        C.hatch(a, (s * .55, 2.0, TOP + .08), r=.27, mat=BLACK)
        a.part('Tail_lamps', 'EliteGlow').box((.08, .02, .05), loc=(s * 1.15, TAIL + .0, 1.4), bevel=0)
    K.grille(a, (0, 2.7, TOP + .1), 1.6, .5, facing=(0, 0, 1), slats=6, frame_mat=BLACK)
    K.grille(a, (1.2, 1.2, TOP + .02), .4, .9, facing=(1, 0, .6), slats=5, frame_mat=BLACK)
    K.exhaust(a, (-1.25, 1.0, TOP - .05), r=.07, length=.3, direction=(-1, 0, .3), muffler=False, cap=False)
    a.pivot('Point_exhaust', (-1.45, 1.0, TOP))
    a.pivot('Point_fire', (0, 1.8, TOP + .3))
    # Stowage: bins on the rear fenders, a log, a jerrycan rack.
    for s in (-1, 1):
        C.stowage_box(a, (.38, .7, .26), (s * (TX + .08), 2.45, 1.1), mat=BLACK, latches=2)
    C.jerry_rack(a, (TX + .08, -2.2, 1.1), count=2, axis='Y')
    K.tow_cable(a.part('Tow_cable', 'Undercarriage'), [(-1.1, -.9, TOP - .08), (-1.1, 1.2, TOP - .04),
                                                       (-.95, 1.5, TOP + .1)], r=.025)


def _running_gear(a):
    for s in (-1, 1):
        C.running_gear(a, s, TX, TW, WHEELS, WR, sprocket=(2.7, .56, .29), idler=(-2.55, .58, .28),
                       rollers=[(-1.45, .95), (.07, .96), (1.6, .95)], pitch=.22, disc_mat=BLACK,
                       wheel_w=.18, seg=9, teeth=12, idler_spokes=5, hide_top=(-2.2, 2.6, .9))
        arms = a.part('Suspension', 'Undercarriage')
        for y in WHEELS:
            C.wheel_arm(arms, s, TX - .2, y, WR, length=.34, back=1, r=.045)


def _launcher(a, t, s):
    """Two Kornet tubes in a box on an elevating arm outside the module (s = 1 left, -1 right)."""
    x = s * 1.25
    arm = a.part('Launcher_arm', BLACK, t)
    arm.box((.36, .5, .12), loc=(s * 1.05, .1, .35), bevel=0)
    k.lathe(arm, [(.08, -.12), (.08, .12)], loc=(x, .1, .45), rot=(0, R90, 0), seg=8)
    K.chamfer_box(a.part('Launcher_box', BLACK, t), (.42, 1.45, .46), loc=(x + s * .1, -.15, .55), c=.03)
    tb = a.part('Tubes', 'Undercarriage', t)
    for dz in (.11, -.11):
        tb.cyl(.08, .02, loc=(x + s * .1, -.88, .55 + dz), rot=K.FORWARD, seg=8, bevel=0)
    a.part('Tube_caps', 'Hazard', t).box((.32, .02, .04), loc=(x + s * .1, -.885, .8), bevel=0)
    return (x + s * .1, -.9, .66)


def _turret(a):
    t = a.pivot('Turret', TUR)
    K.turret_ring(a.part('Turret_ring', BLACK), TUR, .95, h=.06)
    body = a.part('Turret_body', BODY, t)
    bot = [(-.5, -.95), (.5, -.95), (.95, -.5), (.98, .9), (.75, 1.2), (-.75, 1.2), (-.98, .9), (-.95, -.5)]
    top = [(-.4, -.6), (.4, -.6), (.75, -.3), (.78, .8), (.6, 1.05), (-.6, 1.05), (-.78, .8), (-.75, -.3)]
    C.slab_loft(body, bot, top, 0, .62)
    arm_ = a.part('Turret_armour', BLACK, t)
    for s in (-1, 1):
        K.plate(arm_, (.08, .8, .5), loc=(s * .92, -.45, .3), rot=(0, s * .15, s * .45), chamfer=.012)
    K.plate(a.part('Turret_roof', BLACK, t), (1.2, 1.2, .03), loc=(0, .3, .63))
    a.part('Team_band', 'Gilded', t).box((1.5, .02, .07), loc=(0, 1.2, .3), bevel=0)
    # The cradle, the 30 mm gun with its double baffle muzzle brake and the gilded ring, the coax.
    K.chamfer_box(a.part('Mantlet', BLACK, t), (.42, .35, .32), loc=(0, -1.0, .38), c=.04)
    end = C.gun_tube(a, 'Main_cannon', t, (0, -1.12, .42), 1.7, .04, seg=10, sleeve=0, brake='double',
                     brake_name='Muzzle_brake', taper=1.0)
    a.part('Main_cannon_gilt', 'Gilded', t).cyl(.055, .06, loc=(0, -1.6, .42), rot=K.FORWARD, seg=10, bevel=0)
    a.pivot('Muzzle_main', (0, end[1] - .2, .42), t)
    a.part('Coax', 'Steel', t).cyl(.022, .55, loc=(.3, -1.15, .3), rot=K.FORWARD, seg=6, bevel=0)
    a.pivot('Muzzle_coax', (.3, -1.43, .3), t)
    # The Kornet launchers either side; the missile muzzle at the left box.
    m = _launcher(a, t, 1)
    _launcher(a, t, -1)
    a.pivot('Muzzle_missile', m, t)
    # Sights: gunner's (left front), commander's panoramic (right rear), both with the elite glow.
    gs = a.part('Sight', BLACK, t)
    K.chamfer_box(gs, (.3, .36, .26), loc=(.45, -.35, .76), c=.03)
    a.part('Glass', 'Glass', t).box((.22, .01, .1), loc=(.45, -.535, .8), bevel=0)
    a.part('Sight_glow', 'EliteGlow', t).box((.14, .01, .06), loc=(.45, -.54, .8), bevel=0)
    k.lathe(gs, [(.12, 0), (.12, .18), (.15, .2), (.15, .34), (0, .36)], loc=(-.4, .3, .62), seg=10, worn=(3,))
    a.part('Sight_glow', 'EliteGlow', t).box((.14, .01, .07), loc=(-.4, .145, .89), bevel=0)
    for s in (-1, 1):
        K.smoke_dischargers(a, .8, .55, .5, s, count=3, parent=t)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (.6, .95, .62), h=.7)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (-.6, .95, .62), h=.55)
    K.crate(a.part('Stowage', BLACK, t), a.part('Kit_latches', 'Steel', t), (1.1, .25, .28), (0, 1.3, .15), bands=2)


def elite_apc(a, detail=False):
    """The elite infantry fighting vehicle: see the module docstring."""
    _hull(a)
    _running_gear(a)
    _turret(a)
    K.dust(a, (0, 0, .3), radius=3.2, k=.12)
    k.clean(a)


BUILDERS = {
    'elite_apc': (elite_apc, dict(ao_distance=.45, grime_height=.55)),
}
