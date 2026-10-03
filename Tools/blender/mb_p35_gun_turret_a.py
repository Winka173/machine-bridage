"""Prompt 35 wave 7 (lane C): the long-gun turret branch rebuilt from scratch (spec: Tools/blender/specs/gun_turret_a.json).

gun_turret.long (gun_sniper_120, the def's turret_gun_120_long: Rh-120 L/55) as an upgrade of lane A's rebuilt
gun_turret (wave 2): the base's casemate is shared (owner decision 4; `mb_p35_wave2_guns.casemate`, the same family),
and on its race a Leopard-2A6-class turret: the base's faceted welded turret outline with the wedge add-on armour over
its front, Team side plates, the mantlet with the longer L/55 gun (thermal sleeve, fume extractor, the muzzle
reference sensor), the coaxial MG, the commander's panoramic sight raised on its mast, the long telescopic sniper
sight on the roof (the old branch's mark), the gunner's sight, the cupola and the loader's hatch, smoke dischargers,
the bustle basket with its tarp and two whips.

Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Coax`, `Muzzle_coax`. Metres, +Z up,
-Y front, +X left. Under 6,000 triangles (owner decision 6).
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_wave2_guns as base

R90 = math.pi / 2
TZ = base.TZ


def gun_turret_a(a):
    """gun_turret_a: the casemate with the 2A6-class turret and the L/55 (see the module docstring)."""
    base.casemate(a)
    t = a.pivot('Turret', (0, 0, TZ))
    h = .78
    top = .08 + h
    k.extrude(a.part('Turret_body', 'Armor', t), [(-.75, -2.0), (.75, -2.0), (1.65, -1.2), (1.65, 1.6), (1.35, 2.4),
                                                  (-1.35, 2.4), (-1.65, 1.6), (-1.65, -1.2)], h,
              loc=(0, 0, .08 + h / 2), axis='Z', chamfer=.04, corner=.04, taper=(.86, .86), caps=(False, True))
    # The wedge armour: two arrowhead modules over the front cheeks, their bolt rows; Team side plates.
    wd = a.part('Turret_wedges', 'Armor', t)
    for s in (-1, 1):
        k.extrude(wd, [(.0, 0), (.75, 0), (.1, .62)], .09, loc=(s * .9, -2.05, .55), rot=(R90, 0, s * .55),
                  axis='Z', chamfer=.012)
        k.extrude(wd, [(-.05, .0), (.05, .0), (.05, .7), (-.05, .7)], 1.0, loc=(s * 1.25, -1.75, .15),
                  rot=(0, 0, s * -.9), axis='Y', chamfer=.01)
    bolts = a.part('Kit_bolts', 'Steel', t)
    for s in (-1, 1):
        for j in range(3):
            bolts.cyl(.025, .03, loc=(s * (.95 + j * .2), -2.1 - j * .12, .7), rot=(R90, 0, 0), seg=5, bevel=0)
    sp = a.part('Turret_skirts', 'Team', t)
    for s in (-1, 1):
        k.extrude(sp, [(-.8, .1), (1.5, .1), (1.4, .66), (-.8, .62)], .05, loc=(s * 1.66, 0, 0), axis='X',
                  chamfer=.012)
    K.weld(a.part('Kit_welds', 'Charred', t), [(-1.3, 1.0, top + .005), (1.3, 1.0, top + .005)])
    # The mantlet, the long L/55 with its muzzle reference sensor, the coax.
    k.block(a.part('Mantlet', 'Armor', t), (.95, .5, .55), loc=(0, -2.1, .38), chamfer=.05)
    L = 4.9
    K.gun_barrel(a, 'Main_cannon', t, 0, -2.25, .66, L, .105, seg=10, extractor=(.36, 1.6, .45), brake='collar')
    k.block(a.part('Muzzle_sensor', 'Steel', t), (.1, .25, .12), loc=(0, -2.25 - L + .25, .8), chamfer=.01)
    a.part('Muzzle_sensor', 'Steel', t).box((.03, .03, .1), loc=(0, -2.25 - L + .25, .72), bevel=0)
    a.pivot('Muzzle_main', (0, -2.25 - L - .12, .66), t)
    a.part('Coax', 'Steel', t).cyl(.03, 1.05, loc=(.42, -2.36, .47), rot=(R90, 0, 0), seg=6, bevel=0)
    a.pivot('Muzzle_coax', (.42, -2.88, .47), t)
    # Sights: the gunner's block, the panoramic sight raised on its mast, the long sniper telescope.
    sg = a.part('Sight', 'Armor', t)
    k.block(sg, (.4, .55, .38), loc=(-.95, -1.25, top), chamfer=.04)
    a.part('Glass', 'Glass', t).box((.3, .03, .16), loc=(-.95, -1.53, top + .22), bevel=0)
    k.lathe(sg, [(.1, 0), (.1, .35), (.16, .38), (.16, .62), (0, .66)], loc=(.85, -.4, top), seg=10, worn=(3,))
    a.part('Glass', 'Glass', t).box((.2, .02, .12), loc=(.85, -.565, top + .5), bevel=0)
    sc = a.part('Sniper_scope', 'Steel', t)
    k.lathe(sc, [(.09, 0), (.09, .1), (.065, .14), (.065, 1.3), (.085, 1.36), (.085, 1.5), (0, 1.5)],
            loc=(-.35, -.3, top + .28), rot=K.FORWARD, seg=10, worn=(1, 5))
    for y in (-.5, -1.2):
        sc.box((.06, .08, .28), loc=(-.35, y, top + .14), bevel=0)
    a.part('Glass', 'Glass', t).cyl(.07, .01, loc=(-.35, -1.81, top + .28), rot=K.FORWARD, seg=10, bevel=0)
    # Hatches, smoke dischargers, the bustle basket with the tarp, two whips.
    K.hatch_round(a, (.75, .4, top), r=.36, parent=t, periscopes=3, seg=12)
    K.hatch_rect(a, (-.75, .6, top), (.6, .75), parent=t)
    for s in (-1, 1):
        K.smoke_dischargers(a, 1.35, -.9, .65, s, count=4, parent=t)
    bk = a.part('Racks', 'Steel', t)
    y0, y1 = 2.42, 2.95
    for z in (.3, .75):
        bk.tube([(-1.3, y0, z), (-1.3, y1, z), (1.3, y1, z), (1.3, y0, z)], .02, seg=4, caps=False)
    for x in (-1.3, 0, 1.3):
        bk.tube([(x, y1, .3), (x, y1, .75)], .018, seg=4)
    bk.box((2.6, .5, .03), loc=(0, (y0 + y1) / 2, .3), bevel=0)
    K.net_roll(a.part('Tarp', 'Canvas', t), a.part('Kit_straps', 'Steel', t), (0, 2.68, .48), length=1.8, r=.16)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (1.1, 2.2, top), h=1.75, r=.022)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (-1.1, 2.2, top), h=1.6, r=.022)
    k.clean(a)


BUILDERS = {
    'gun_turret_a': (gun_turret_a, dict(ao_distance=.7, grime_height=.45, ao_strength=.65)),
}
