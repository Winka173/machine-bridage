"""Prompt 35 wave 10 (lane B): heavy_turret_a, the coastal long-range branch of the heavy turret (heavy_turret.coastal,
gun_155_twin_coastlr; unit_refs A-222 Bereg, AK-130 on shore, M284 long range), rebuilt from scratch (spec:
Tools/blender/specs/heavy_turret_a.json) as an upgrade of its wave 2 base: it stands on the same Hegemon barbette
(owner decision 4: a base and its branches share one emplacement; `mb_p35_wave2_heavy.barbette`, the shared
sub-assembly lane A wrote for heavy_turret and heavy_turret_b) and turns a longer-ranged gun house of its own.

The gun house (this script): the base's faceted twin-155 house stretched for the long barrels: a raised rear bustle
for the bigger charges, the two gun ports with cast mantlets and canvas blast covers, the two long 155 mm barrels
(L/52 class, 6.2 m) with thermal sleeves, bore evacuators and double-baffle brakes, the coaxial MG; on the roof the
coastal fire control the branch adds: a rangefinder bar with armoured ears, the surface-search radar on a lattice
post with its spinning array (`Radar`), an optical director, the commander's cupola, hatches, vents, the pintle MG on
its riser and post (the roof-gun rule), antennas, the Team band and hazard marks.

Runtime nodes (kept): `Turret` (0, 0.2, 2.92), `Main_cannon`, `Muzzle_brake`, `Muzzle_main` (with its per-barrel
`Muzzle_b1_main` / `_b2_main`, written here as heavy_turret_b does), `Muzzle_coax`, `Mount_mg` / `Muzzle_mg`; new:
`Radar` (the spinning search array: the def is coastal). Built from frontier_kit / mb_kit27 primitives, mb_kit35, the
wave 2 helpers and the base's shared barbette; no other model's builder. Metres, +Z up, -Y front, +X left. Under
6,000 triangles.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_wave2_heavy as H

R90 = math.pi / 2
TAU = math.tau
TY, TZ = H.TY, H.TZ
BL = 6.0                  # barrel length (the base's is 3.56)


def gun_house(a):
    t = a.pivot('Turret', (0, TY, TZ))
    h = 1.7
    top = .05 + h
    k.extrude(a.part('Turret_body', 'Armor', t), [(-1.3, -2.25), (1.3, -2.25), (2.3, -1.2), (2.3, 2.4), (1.9, 3.0),
                                                  (-1.9, 3.0), (-2.3, 2.4), (-2.3, -1.2)], h,
              loc=(0, 0, .05 + h / 2), axis='Z', chamfer=.05, corner=.05, taper=(.82, .86), caps=(False, True))
    # The raised rear bustle for the bigger charges.
    k.extrude(a.part('Turret_bustle', 'Armor', t), [(-1.5, 1.4), (1.5, 1.4), (1.6, 3.0), (1.3, 3.55), (-1.3, 3.55),
                                                    (-1.6, 3.0)], .55, loc=(0, 0, top + .2), axis='Z', chamfer=.04,
              corner=.04, taper=(.9, .9), caps=(False, True))
    tb = a.part('Turret_band', 'Team', t)
    for s in (-1, 1):
        tb.box((.03, 3.0, .32), loc=(s * 2.17, .6, .95), rot=(0, -s * .09, 0), bevel=0)
    a.part('Hazard_marks', 'Hazard', t).box((2.4, .03, .12), loc=(0, 3.5, top + .45), bevel=0)
    seams = a.part('Panel_seams', 'Charred', t)
    for s in (-1, 1):
        for y in (.0, 1.4):
            seams.box((.02, .04, 1.45), loc=(s * (2.3 - .82 * .09 - .06), y, .82), rot=(0, -s * .1, 0), bevel=0)
    K.weld(a.part('Kit_welds', 'Charred', t), [(-1.6, -.9, top + .005), (1.6, -.9, top + .005)])
    # Gun ports with cast mantlets and canvas blast covers; the long barrels.
    for s in (-1, 1):
        k.block(a.part('Mantlet', 'Armor', t), (.62, .58, .74), loc=(s * .78, -2.35, .37), chamfer=.05)
        k.lathe(a.part('Blast_covers', 'Canvas', t), [(.26, 0), (.22, .25), (.17, .4)], loc=(s * .78, -2.62, .72),
                rot=K.FORWARD, seg=8, caps=(False, False))
        k.lathe(a.part('Main_cannon', 'Steel', t), [(.17, .3), (.15, .4), (.15, 1.5), (.19, 1.6), (.19, 2.4),
                                                    (.15, 2.5), (.13, 3.6), (.12, BL), (0, BL)],
                loc=(s * .78, -2.6, .72), rot=K.FORWARD, seg=8, worn=(3, 4))
        for f in (.9, 3.0):
            a.part('Thermal_sleeves', 'Undercarriage', t).cyl(.16 if f < 3 else .14, .05,
                                                              loc=(s * .78, -2.6 - f, .72), rot=K.FORWARD, seg=8,
                                                              bevel=0)
        k.lathe(a.part('Muzzle_brake', 'Undercarriage', t), [(.11, BL - .02), (.2, BL), (.2, BL + .32), (.09, BL + .32),
                                                             (0, BL + .3)], loc=(s * .78, -2.6, .72), rot=K.FORWARD,
                seg=8, worn=(1,))
        for f in (.09, .21):
            a.part('Brake_ports', 'Charred', t).box((.42, .05, .06), loc=(s * .78, -2.6 - BL - f, .72), bevel=0)
    a.pivot('Muzzle_main', (0, -2.6 - BL - .32, .72), t)
    a.pivot('Muzzle_b1_main', (-.78, 0, 0), 'Muzzle_main')
    a.pivot('Muzzle_b2_main', (.78, 0, 0), 'Muzzle_main')
    a.part('Coax', 'Steel', t).cyl(.035, .2, loc=(0, -2.2, .72), rot=(R90, 0, 0), seg=6, bevel=0)
    a.pivot('Muzzle_coax', (0, -2.29, .72), t)
    # Fire control: the rangefinder bar with its ears, the search radar on its post, the optical director.
    k.block(a.part('Sight', 'Armor', t), (3.4, .45, .36), loc=(0, .9, top), chamfer=.05)
    for s in (-1, 1):
        k.lathe(a.part('Sight', 'Armor', t), [(.2, -.22), (.2, .22)], loc=(s * 1.85, .9, top + .18), rot=(0, R90, 0),
                seg=8)
        a.part('Glass', 'Glass', t).box((.03, .2, .14), loc=(s * 2.06, .85, top + .19), bevel=0)
    post = a.part('Radar_post', 'Steel', t)
    for dx, dy in ((-.2, -.2), (.2, -.2), (0, .22)):
        post.tube([(dx, 2.4 + dy, top + .75), (dx * .3, 2.4 + dy * .3, top + 1.2)], .03, seg=4)
    r = a.pivot('Radar', (0, 2.4, top + 1.25), t)
    k.block(a.part('Radar_turntable', 'Armor', r), (.35, .35, .18), loc=(0, 0, .05), chamfer=.02)
    k.extrude(a.part('Radar_array', 'PlasterWhite', r), [(-1.1, -.06), (1.1, -.06), (.95, .06), (-.95, .06)], .4,
              loc=(0, 0, .35), axis='Z', chamfer=.01)
    a.part('Radar_feed', 'Steel', r).box((1.6, .05, .05), loc=(0, -.12, .35), bevel=0)
    k.block(a.part('Director', 'Armor', t), (.5, .6, .45), loc=(-1.2, -.3, top + .22), chamfer=.04)
    a.part('Glass', 'Glass', t).box((.3, .03, .14), loc=(-1.2, -.61, top + .3), bevel=0)
    # Cupola, hatch, vents, the raised pintle MG, antennas, lamps, the ladder.
    k.lathe(a.part('Cupola', 'Armor', t), [(.42, 0), (.42, .18), (.37, .24), (0, .24)], loc=(1.15, -.6, top), seg=10,
            worn=(2,))
    k.block(a.part('Hatches', 'Armor', t), (.7, .7, .06), loc=(.1, -1.3, top), chamfer=0)
    K.handle(a.part('Kit_handles', 'Steel', t), (-.1, -1.3, top + .06), (.3, -1.3, top + .06), (0, 0, 1), h=.06)
    for x in (-1.3, 1.3):
        k.lathe(a.part('Vents', 'Steel', t), [(.15, 0), (.15, .1), (.1, .14), (0, .14)], loc=(x, 2.85, top + .7),
                seg=8)
    K.pintle_mg(a, t, (1.0, .5, top + .3), scale=1.2, post=.35, riser=.15)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (-1.5, 3.1, top + .7), h=.9, r=.025)
    for s in (-1, 1):
        a.part('Lamps', 'Lamp', t).box((.16, .04, .1), loc=(s * 1.25, -1.98, top - .4), bevel=0)
    K.ladder(a.part('Ladders', 'Steel', t), (.9, 3.62, .1), (.9, 3.55, top + .75), width=.45, step=.3, r=.018)
    rail = a.part('Railings', 'Steel', t)
    for path in ([(1.85, -.9, top), (1.85, 1.3, top)], [(-1.85, -.9, top), (-1.85, 1.3, top)]):
        K.railing(rail, path, h=.8, post=.6, r=.018)
    # Stowage bins on the bustle flanks, a spare-charge rack, the radar post's hazard collar, red brake bands.
    for s in (-1, 1):
        K.crate(a.part('Bins', 'Crate', t), a.part('Kit_straps', 'Steel', t), (.35, 1.1, .4),
                (s * 1.85, 2.3, top - .2), bands=1)
        a.part('Brake_bands', 'BarrelRed', t).cyl(.205, .06, loc=(s * .78, -2.6 - BL - .16, .72), rot=K.FORWARD,
                                                  seg=8, bevel=0)
    for i in range(4):
        a.part('Charge_cans', 'Fuel', t).cyl(.12, .55, loc=(-.6 + i * .3, 3.75, top - .1), rot=(0, 0, 0), seg=8,
                                             bevel=0)
    a.part('Radar_collar', 'Hazard', t).cyl(.32, .12, loc=(0, 2.4, top + .81), seg=8, bevel=0)
    return t


def heavy_turret_a(a):
    H.barbette(a)
    gun_house(a)
    k.clean(a)


BUILDERS = {'heavy_turret_a': (heavy_turret_a, dict(ao_distance=.9, grime_height=.6, ao_strength=.65))}
