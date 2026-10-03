"""Prompt 35 wave 7 (lane C): the elite heavy tank rebuilt from scratch (spec: Tools/blender/specs/elite_heavy_tank.json).

An Object 195 / T-95 (unit_refs: 2A83 152 mm with HEAT rounds; the def's modelSize 9.64 x 3.46 x 2.53 m, the gun's
overhang inside the length): the very long low hull with the long glacis under a field of reactive armour bricks,
the crew capsule raised at the front with its row of periscopes and two hatches, seven large road wheels a side,
the front idler and the rear sprocket with three return rollers, rubber skirts with reactive armour boxes over the
front half; the low angular unmanned turret with its bustle, the huge 152 mm gun on its mantlet (thermal sleeve
bands, fume extractor, a muzzle collar), the 2A42 30 mm autocannon in its armoured housing on the right cheek (the
def's coaxial `autocannon_30`), the gunner's sight and the commander's panoramic sight, the remote 12.7 mm standing
on its post (the def's free `hmg_roof`, MODEL_STANDARD "Roof guns"), smoke dischargers, the engine deck with grilles
and exhausts, the unditching log, stowage. Elite marks (DECISIONS 25B2): the team-coloured body, black armour
(EliteBlack), gilded bands and red-glowing sights.

Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Coax`, `Muzzle_coax`, `Mount_mg`,
`Muzzle_mg`, `Hatches`, `Point_exhaust`, `Point_fire`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
BLACK = 'EliteBlack'
BODY = 'Team'
TX, TW = 1.38, .58
WR = .37
WHEELS = (-2.55, -1.72, -.89, -.06, .77, 1.6, 2.43)
TOP = 1.3
NOSE, TAIL = -3.55, 3.55
TUR = (0, .55, TOP)


def _hull(a):
    hull = a.part('Hull', BODY)
    prof = [(NOSE, .66), (NOSE + .25, .86), (-1.9, TOP), (3.3, TOP), (TAIL, 1.05), (TAIL - .05, .46), (-3.1, .44)]
    k.extrude(hull, prof, 2.6, axis='X', chamfer=.06, corner=.03)
    low = a.part('Hull_lower', BLACK)
    k.extrude(low, [(NOSE + .2, .64), (-3.05, .4), (3.2, .4), (3.25, .8)], (TX - TW / 2) * 2, axis='X', chamfer=.02)
    fen = a.part('Fenders', BODY)
    for s in (-1, 1):
        K.fender(fen, TX + .03, NOSE + .25, TAIL - .05, 1.0, .62, s, lip=.03)
    # The raised crew capsule at the front: sloped faces all round, a periscope row, two hatches.
    cap = a.part('Capsule', BODY)
    C.slab_loft(cap, [(-1.1, -1.95), (1.1, -1.95), (1.15, -.9), (-1.15, -.9)],
                [(-.95, -1.75), (.95, -1.75), (1.0, -1.0), (-1.0, -1.0)], TOP - .02, TOP + .2)
    for x in (-.75, -.45, -.15, .15, .45, .75):
        K.periscope(a, (x, -1.82, TOP + .17), facing=(0, -1, .2), size=(.13, .07, .06), mat=BLACK)
    for x in (-.5, .5):
        C.hatch(a, (x, -1.38, TOP + .2), r=.25, mat=BLACK)
    # Reactive armour over the long glacis (two fields either side of the centre line).
    g0, g1 = (NOSE + .25, .86), (-1.9, TOP)
    ang = math.atan2(g1[1] - g0[1], g1[0] - g0[0])
    d = (0, math.cos(ang), math.sin(ang))
    mid = (0, (g0[0] + g1[0]) / 2, (g0[1] + g1[1]) / 2 + .02)
    for s in (-1, 1):
        K.era_bricks(a, (s * .68, mid[1], mid[2]), (1, 0, 0), d, 3, 3, size=(.4, .4, .07), gap=.03, mat=BLACK,
                     bolts=False)
    for s in (-1, 1):
        K.lamp(a, (s * 1.1, -2.2, TOP - .05), (0, -1, .2), r=.07, guard=True, mat=BLACK)
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .75, NOSE - .02, .7), facing=(0, -1, 0), size=.08)
    # Skirts: rubber over the rear, reactive armour boxes over the front half.
    for s in (-1, 1):
        sk = a.part('Skirts', 'Rubber')
        sk.box((.03, 3.2, .45), loc=(s * (TX + .3), 1.6, .8), bevel=0)
        era = a.part('Skirt_era', BLACK)
        for j in range(5):
            K.plate(era, (.12, .6, .48), loc=(s * (TX + .33), -3.0 + j * .64, .8), chamfer=.015)
        a.part('Team_band', 'Gilded').box((.012, 3.0, .06), loc=(s * (TX + .315), 1.6, .95), bevel=0)
    # The engine deck: grilles, the exhaust louvres on the rear corners, the Team panel.
    for x in (-.6, .6):
        K.grille(a, (x, 2.55, TOP + .02), 1.0, 1.2, facing=(0, 0, 1), slats=7, frame_mat=BLACK)
    K.grille(a, (0, 1.55, TOP + .02), 1.6, .4, facing=(0, 0, 1), slats=5, frame_mat=BLACK)
    for s in (-1, 1):
        K.grille(a, (s * 1.25, 3.1, TOP - .1), .45, .6, facing=(s, .3, .5), slats=4, frame_mat=BLACK)
        a.part('Tail_lamps', 'EliteGlow').box((.1, .02, .06), loc=(s * 1.15, TAIL + .0, 1.2), bevel=0)
    a.pivot('Point_exhaust', (-1.25, 3.15, TOP))
    a.pivot('Point_fire', (0, 2.2, TOP + .3))
    # The unditching log across the rear plate on its brackets, a spare fuel drum pair, bins on the fenders.
    log = a.part('Log', 'Wood')
    log.cyl(.13, 2.4, loc=(0, TAIL + .12, 1.15), rot=(0, R90, 0), seg=8, bevel=0)
    for x in (-.8, .8):
        a.part('Kit_straps', 'Steel').cyl(.14, .05, loc=(x, TAIL + .12, 1.15), rot=(0, R90, 0), seg=8, bevel=0)
    for s in (-1, 1):
        k.lathe(a.part('Fuel_drums', BLACK), [(0, -.4), (.22, -.38), (.24, -.3), (.24, .3), (.22, .38), (0, .4)],
                loc=(s * .75, TAIL + .35, .6), rot=(0, R90, 0), seg=10, worn=(2, 3))
        C.stowage_box(a, (.4, .9, .24), (s * (TX + .05), 2.7, 1.0), mat=BLACK, latches=2)
    K.tow_cable(a.part('Tow_cable', 'Undercarriage'), [(-1.25, -.8, TOP + .02), (-1.25, 1.2, TOP + .02),
                                                       (-1.1, 1.6, TOP + .02)], r=.025)


def _running_gear(a):
    for s in (-1, 1):
        C.running_gear(a, s, TX, TW, WHEELS, WR, sprocket=(3.18, .58, .32), idler=(-3.22, .56, .31),
                       rollers=[(-1.3, .97), (.35, .98), (2.0, .97)], pitch=.25, disc_mat=BLACK,
                       wheel_w=.2, seg=9, teeth=12, idler_spokes=5, hide_top=(-3.0, 3.1, .86))
        arms = a.part('Suspension', 'Undercarriage')
        for y in WHEELS:
            C.wheel_arm(arms, s, TX - .2, y, WR, length=.38, back=1, r=.05)


def _turret(a):
    t = a.pivot('Turret', TUR)
    K.turret_ring(a.part('Turret_ring', BLACK), TUR, 1.05, h=.05)
    body = a.part('Turret_body', BODY, t)
    # A low wedge: the front plates slope back hard from the mantlet, the sides lean in, a long flat bustle.
    bot = [(-.5, -1.45), (.5, -1.45), (1.45, -.85), (1.5, 1.2), (1.3, 1.5), (-1.3, 1.5), (-1.5, 1.2), (-1.45, -.85)]
    top = [(-.4, -1.05), (.4, -1.05), (1.15, -.6), (1.22, 1.1), (1.05, 1.38), (-1.05, 1.38), (-1.22, 1.1),
           (-1.15, -.6)]
    C.slab_loft(body, bot, top, 0, .72)
    K.plate(a.part('Turret_roof', BLACK, t), (1.8, 1.7, .03), loc=(0, .3, .735))
    bus = a.part('Bustle', BLACK, t)
    K.chamfer_box(bus, (2.2, .6, .5), loc=(0, 1.75, .36), c=.05)
    for s in (-1, 1):
        a.part('Team_band', 'Gilded', t).box((.02, 1.8, .06), loc=(s * 1.47, .2, .28), rot=(0, s * .3, 0), bevel=0)
    a.part('Team_band', 'Gilded', t).box((2.0, .02, .06), loc=(0, 2.06, .3), bevel=0)
    # The mantlet and the huge 152 mm gun.
    K.chamfer_box(a.part('Mantlet', BLACK, t), (.86, .4, .52), loc=(0, -1.55, .36), c=.06)
    C.gun_tube(a, 'Main_cannon', t, (0, -1.72, .38), 4.3, .12, seg=12, sleeve=4, extractor=(.42, 1.6),
               brake='plain', brake_name='Muzzle_brake')
    a.part('Main_cannon_gilt', 'Gilded', t).cyl(.12, .1, loc=(0, -1.72 - 4.3 * .75, .38), rot=K.FORWARD, seg=12,
                                                bevel=0)
    a.pivot('Muzzle_main', (0, -6.08, .38), t)
    # The 30 mm autocannon in its armoured housing on the right cheek (the def's coax slot).
    ch = a.part('Coax_housing', BLACK, t)
    C.slab_loft(ch, [(-.2, -.6), (.2, -.6), (.2, .5), (-.2, .5)], [(-.16, -.5), (.16, -.5), (.16, .4), (-.16, .4)],
                0, .34, loc=(-1.25, -.55, .62))
    k.lathe(a.part('Coax', 'Steel', t), [(.05, 0), (.05, .3), (.035, .35), (.03, 1.5), (0, 1.5)],
            loc=(-1.25, -1.1, .82), rot=K.FORWARD, seg=8, worn=(1,))
    a.part('Coax_ribs', 'Steel', t).cyl(.045, .25, loc=(-1.25, -2.45, .82), rot=K.FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_coax', (-1.25, -2.62, .82), t)
    a.part('Feed_chute', 'Steel', t).tube([(-1.05, -.4, .8), (-.85, -.2, .76), (-.7, 0, .74)], .04, seg=5)
    # Sights: gunner's box (left front), commander's panoramic sight (right rear).
    gs = a.part('Sight', BLACK, t)
    K.chamfer_box(gs, (.4, .44, .32), loc=(.75, -.75, .88), c=.04)
    a.part('Glass', 'Glass', t).box((.3, .01, .14), loc=(.75, -.975, .94), bevel=0)
    a.part('Sight_glow', 'EliteGlow', t).box((.22, .01, .08), loc=(.75, -.98, .94), bevel=0)
    k.lathe(gs, [(.14, 0), (.14, .2), (.17, .22), (.17, .38), (0, .4)], loc=(-.45, .1, .73), seg=10, worn=(3,))
    a.part('Sight_glow', 'EliteGlow', t).box((.16, .01, .08), loc=(-.45, -.075, 1.03), bevel=0)
    # The remote 12.7 mm on its raised post behind the panoramic sight.
    C.roof_gun(a, (.4, .55, .735), parent=t, pivot='Mount_mg', barrel='MG', brake='MG_flash', muzzle='Muzzle_mg',
               post=.22, length=1.1, scale=.9, shield=False, mat=BLACK, tag='_rws')
    a.part('Sight_glow', 'EliteGlow', t).box((.1, .01, .06), loc=(.27, .4, 1.12), bevel=0)
    # Smoke dischargers on both front corners, aerials, the bustle rack with a tarp.
    for s in (-1, 1):
        K.smoke_dischargers(a, 1.12, -.65, .58, s, count=3, parent=t)
        K.whip_antenna(a.part('Antennas', 'Steel', t), (s * 1.0, 1.6, .61), h=.6 if s > 0 else .5, r=.02)
    K.net_roll(a.part('Tarp', 'Canvas', t), a.part('Kit_straps', 'Steel', t), (0, 1.75, .8), length=1.8, r=.13)
    C.hatch(a, (-.6, .85, .74), r=.22, parent=t, mat=BLACK)


def elite_heavy_tank(a, detail=False):
    """The elite heavy tank: see the module docstring."""
    _hull(a)
    _running_gear(a)
    _turret(a)
    K.dust(a, (0, 0, .3), radius=4.0, k=.12)
    k.clean(a)


BUILDERS = {
    'elite_heavy_tank': (elite_heavy_tank, dict(ao_distance=.5, grime_height=.55)),
}
