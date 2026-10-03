"""Prompt 35 wave 7 (lane C): the elite tank destroyer rebuilt from scratch (spec: Tools/blender/specs/elite_tank_destroyer.json).

A 2S25M Sprut-SDM1 hull and turret (unit_refs' 2S25 Sprut-SD, upgraded) carrying the def's long 105 mm
(gun_105_apfsds; prompt 35 wave 9: the visible gun matches the data; the def's modelSize 9.08 x 3.01 x 2.34 m, the
gun's overhang inside the length): the long low air-droppable hull of the BMD-4M family with the boat
bow and its folded trim vane, seven small road wheels a side on swing arms, the front idler and the rear sprocket
with four return rollers, black skirt edges with front flaps, the water-jet outlets on the rear plate, the engine
grilles; the flat angular turret with bolted add-on armour boxes on its cheeks, the long 105 mm on its mantlet
(sleeve bands, fume extractor, a plain muzzle collar), the commander's panoramic sight and the gunner's sight, the
remote 12.7 mm standing on its post (the def's free `hmg_roof`, MODEL_STANDARD "Roof guns"), smoke dischargers, the
bustle basket with its stowage and aerials. Elite marks (DECISIONS 25B2): the team-coloured body, black armour
(EliteBlack), gilded bands and red-glowing sights.

Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Mount_mg`, `Muzzle_mg`, `Hatches`,
`Point_exhaust`, `Point_fire`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
BLACK = 'EliteBlack'
BODY = 'Team'
TX, TW = 1.18, .48
WR = .28
WHEELS = (-2.3, -1.55, -.8, -.05, .7, 1.45, 2.2)
TOP = 1.12
NOSE, TAIL = -3.05, 3.15
TUR = (0, .2, TOP)


def _hull(a):
    hull = a.part('Hull', BODY)

    def sec(w_low, z_low, w_sp, z_sp, w_top, z_top):
        return [(0, z_low), (w_low, z_low), (w_low, z_sp - .14), (w_sp, z_sp), (w_top, z_top), (0, z_top)]
    # The boat bow, the glacis, the sponsons with the sides leaning in, the rear plate.
    C.section_loft(hull, [
        (NOSE, sec(.55, .62, .7, .66, .6, .7)),
        (NOSE + .45, sec(.82, .38, 1.36, .66, 1.18, .86)),
        (-2.0, sec(.86, .34, 1.45, .72, 1.25, TOP)),
        (2.85, sec(.86, .34, 1.45, .72, 1.25, TOP)),
        (TAIL, sec(.84, .42, 1.4, .72, 1.2, TOP - .06)),
    ])
    for s in (-1, 1):
        a.part('Skirt_edge', BLACK).box((.05, 5.2, .09), loc=(s * 1.44, -.0, .66), bevel=0)
        sk = a.part('Skirts', 'Rubber')
        for j in range(2):
            sk.box((.02, .55, .25), loc=(s * 1.45, -2.45 + j * .58, .5), rot=(.12, 0, 0), bevel=0)
        a.part('Team_band', 'Gilded').box((.01, 3.0, .07), loc=(s * 1.36, .5, 1.0), rot=(0, s * .25, 0), bevel=0)
    # The folded trim vane on the glacis with its ribs, the driver's hatch and periscopes, lamps, tow hooks.
    vane = a.part('Trim_vane', BLACK)
    K.plate(vane, (2.2, .55, .035), loc=(0, -2.6, .8), rot=(-.6, 0, 0), chamfer=.01)
    rib = a.part('Trim_vane_ribs', BLACK)
    for x in (-.8, -.27, .27, .8):
        rib.box((.04, .5, .04), loc=(x, -2.58, .83), rot=(-.6, 0, 0), bevel=0)
    C.hatch(a, (0, -1.7, TOP), r=.26)
    for x in (-.28, 0, .28):
        K.periscope(a, (x, -2.0, TOP + .01), facing=(0, -1, 0), size=(.12, .07, .06), mat=BLACK)
    for s in (-1, 1):
        K.lamp(a, (s * 1.05, -2.3, 1.02), (0, -1, .15), r=.065, guard=True, mat=BLACK)
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .5, NOSE - .02, .62), facing=(0, -1, 0), size=.07)
    # The engine deck and the water jets.
    K.grille(a, (0, 2.3, TOP + .02), 1.5, .9, facing=(0, 0, 1), slats=7, frame_mat=BLACK)
    for s in (-1, 1):
        K.grille(a, (s * .95, 1.45, TOP + .02), .45, .6, facing=(0, 0, 1), slats=3, frame_mat=BLACK)
        k.lathe(a.part('Waterjets', BLACK), [(.18, 0), (.22, .04), (.22, .18), (.16, .22)], loc=(s * .55, TAIL, .66),
                rot=K.BACKWARD, seg=12, worn=(2,))
        a.part('Waterjets_dark', 'Undercarriage').cyl(.15, .02, loc=(s * .55, TAIL + .21, .66), rot=K.BACKWARD,
                                                      seg=12, bevel=0)
        a.part('Tail_lamps', 'EliteGlow').box((.08, .02, .05), loc=(s * 1.12, TAIL + .01, 1.0), bevel=0)
    a.pivot('Point_exhaust', (1.2, 2.1, TOP))
    a.pivot('Point_fire', (0, 1.6, TOP + .3))
    for s in (-1, 1):
        C.stowage_box(a, (.38, .85, .22), (s * 1.18, 1.95, TOP - .03), mat=BLACK, latches=2)
    C.cable_reel(a, (-1.18, -1.2, TOP + .12), r=.15, w=.3, axis='Y')
    C.jerry_rack(a, (1.18, -1.15, TOP - .03), count=2, axis='Y')


def _running_gear(a):
    for s in (-1, 1):
        C.running_gear(a, s, TX, TW, WHEELS, WR, sprocket=(2.82, .5, .26), idler=(-2.78, .52, .25),
                       rollers=[(-1.9, .72), (-.45, .74), (1.05, .74), (2.4, .72)], pitch=.23, disc_mat=BLACK,
                       wheel_w=.17, seg=9, teeth=13, idler_spokes=5)
        arms = a.part('Suspension', 'Undercarriage')
        for y in WHEELS:
            C.wheel_arm(arms, s, TX - .18, y, WR, length=.34, back=1, r=.04)


def _turret(a):
    t = a.pivot('Turret', TUR)
    K.turret_ring(a.part('Turret_ring', BLACK), TUR, .9, h=.05)
    body = a.part('Turret_body', BODY, t)
    bot = [(-.45, -1.1), (.45, -1.1), (1.05, -.6), (1.08, .9), (.85, 1.35), (-.85, 1.35), (-1.08, .9), (-1.05, -.6)]
    top = [(-.3, -.8), (.3, -.8), (.85, -.45), (.88, .82), (.7, 1.2), (-.7, 1.2), (-.88, .82), (-.85, -.45)]
    C.slab_loft(body, bot, top, 0, .55)
    K.plate(a.part('Turret_roof', BLACK, t), (1.3, 1.2, .03), loc=(0, .35, .565))
    # Bolted add-on armour boxes on both cheeks, the gold band round the bustle.
    arm = a.part('Turret_armour', BLACK, t)
    for s in (-1, 1):
        for j in range(2):
            K.plate(arm, (.1, .42, .36), loc=(s * (1.0 + j * .05), -.68 + j * .44, .27), rot=(0, 0, s * (.6 - j * .4)),
                    chamfer=.012)
    a.part('Team_band', 'Gilded', t).box((1.72, .02, .07), loc=(0, 1.33, .28), bevel=0)
    # The mantlet and the very long gun.
    man = a.part('Mantlet', BLACK, t)
    k.extrude(man, [(-.17, -.2), (.13, -.22), (.18, .2), (-.13, .22)], .56, loc=(0, -1.1, .3), axis='X',
              chamfer=.03, corner=.02)
    # The def's gun_105_apfsds: a long 105 mm (L7 / 2A70-class barrel length, the slimmer tube, the fume extractor
    # well forward), drawn to match the data (lead's wave 9 call; it was the 2S25's 125 mm).
    C.gun_tube(a, 'Main_cannon', t, (0, -1.22, .3), 4.2, .066, seg=12, sleeve=3, extractor=(.45, 1.8),
               brake='plain', brake_name='Muzzle_brake')
    a.part('Main_cannon_gilt', 'Gilded', t).cyl(.08, .08, loc=(0, -1.22 - 4.2 * .8, .3), rot=K.FORWARD, seg=12,
                                                bevel=0)
    a.pivot('Muzzle_main', (0, -5.48, .3), t)
    # Sights: the commander's panoramic sight (right rear), the gunner's sight box (left front).
    cs = a.part('Sight', BLACK, t)
    k.lathe(cs, [(.13, 0), (.13, .2), (.16, .22), (.16, .36), (0, .38)], loc=(-.4, .2, .55), seg=10, worn=(3,))
    a.part('Sight_glow', 'EliteGlow', t).box((.15, .01, .07), loc=(-.4, .04, .84), bevel=0)
    K.chamfer_box(cs, (.3, .34, .24), loc=(.5, -.5, .67), c=.03)
    a.part('Glass', 'Glass', t).box((.22, .01, .1), loc=(.5, -.675, .7), bevel=0)
    a.part('Sight_glow', 'EliteGlow', t).box((.14, .01, .06), loc=(.5, -.68, .7), bevel=0)
    C.hatch(a, (.45, .6, .58), r=.24, parent=t, mat=BLACK)
    # The remote 12.7 mm on its post behind the commander's sight.
    C.roof_gun(a, (-.4, .75, .565), parent=t, pivot='Mount_mg', barrel='MG', brake='MG_flash', muzzle='Muzzle_mg',
               post=.22, length=1.0, scale=.85, shield=False, mat=BLACK, tag='_rws')
    # Smoke dischargers, the bustle basket with its stowage, aerials.
    for s in (-1, 1):
        K.smoke_dischargers(a, .92, -.3, .4, s, count=3, parent=t)
    bk = a.part('Racks', 'Steel', t)
    sq = [(-.015, -.015), (.015, -.015), (.015, .015), (-.015, .015)]
    for z in (.18, .45):
        k.sweep(bk, sq, [(.78, 1.3, z), (.78, 1.7, z), (-.78, 1.7, z), (-.78, 1.3, z)])
    a.part('Stowage', 'Canvas', t).box((1.3, .34, .24), loc=(0, 1.5, .31), bevel=.04)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (.75, 1.05, .55), h=.45)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (-.75, 1.1, .55), h=.4)


def elite_tank_destroyer(a, detail=False):
    """The elite tank destroyer: see the module docstring."""
    _hull(a)
    _running_gear(a)
    _turret(a)
    K.dust(a, (0, 0, .3), radius=3.4, k=.12)
    k.clean(a)


BUILDERS = {
    'elite_tank_destroyer': (elite_tank_destroyer, dict(ao_distance=.45, grime_height=.5)),
}
