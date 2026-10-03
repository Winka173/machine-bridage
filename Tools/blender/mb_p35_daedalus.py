"""Prompt 35 wave 10 (lane B): Daedalus, Aurel's assault ship, rebuilt from scratch (spec:
Tools/blender/specs/daedalus.json).

unit_sheet: based on the Acclamator class (Attack of the Clones), Aurel's assault ship: it waits in orbit, then
switches between high and low passes. Drawn at the old file's size (37.1 x 20.4 x 12.8 m; no modelSize): the
arrowhead hull in plan, its hard chine with the upper hull sloping up from the nose and the lower hull (Keel) falling
to the belly, the central dorsal trench with its spine, the stepped superstructure aft with the bridge tower, its
window band and the two sensor dishes (the APS emitters on its roof: `Mount_APS`), the four turbolaser turrets on
the upper hull, the two point-defence lasers forward (`Pd_laser_l` / `_r`, breakable), the two forward ball guns
under the chine (`Mount_gun` / `.001`, twin barrels, a muzzle each), the three drop-pod bays in the
belly (`Pod_bay_1` .. `_3`: ring, glowing pod, frame), the four landing legs folded under the belly (its running
gear), the main thruster block aft (`Thruster_main`: housing, six nozzles, glow), Aurel's stripes, flank plates,
belly plates, hull lights, window rows and deck fittings. Boss rule: the breakable parts are riveted plates one shade
off on their own nodes.

Runtime nodes kept at their old places: `Mount_gun` / `.001` with `Muzzle_gun` / `.001`, `Pd_laser_l` / `_r`,
`Thruster_main`, `Pod_bay_1` .. `_3`, `Point_fire`, `Point_exhaust`; new: `Mount_APS` (the def's APS). Built only from
frontier_kit / mb_kit27 primitives, mb_kit35 and lane B's helpers; no other model's builder. Metres, +Z up, -Y front,
+X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
Y0, Y1 = -18.5, 15.6     # nose / stern


def half_w(y):
    return .6 + (10.0 - .6) * (y - Y0) / (Y1 - Y0)


def top_z(y):
    return min(2.7, .3 + (y - Y0) * .16)


def bot_z(y):
    return max(-2.6, -.3 - (y - Y0) * .16)


def _hull(a):
    up = a.part('Upper_hull', 'Plaster')
    low = a.part('Keel', 'Armor')
    ys = (Y0, -15.0, -10.0, -4.0, 2.0, 8.0, 13.0, Y1)
    urings, lrings = [], []
    for y in ys:
        w = half_w(y)
        t, b = top_z(y), bot_z(y)
        urings.append([(-w, y, 0), (w, y, 0), (w * .82, y, t * .7), (w * .3, y, t), (-w * .3, y, t), (-w * .82, y, t * .7)])
        lrings.append([(-w * .75, y, b), (w * .75, y, b), (w, y, 0), (-w, y, 0)])
    k.sharp_loft(up, urings, chamfer=.08)
    k.sharp_loft(low, lrings, chamfer=.08)
    # The hard chine band (Aurel's stripe) and flank plates.
    chine = a.part('Aurel_stripes', 'Team')
    for s in (-1, 1):
        chine.tube([(s * half_w(y) * 1.003, y, .02) for y in (Y0 + .3, -10.0, 2.0, Y1)], .14, seg=4, caps=False)
        for i, y in enumerate((-12.0, -7.0, -2.0, 3.0, 8.0, 12.5)):
            w = half_w(y)
            L = 2.6 + .3 * (i % 3)
            K.armour_plate(a, a.part('Flank_plates', 'Armor'), (L, .9, .1),
                           (s * (w * .9), y, top_z(y) * .35), rot=(0, -s * .9, -s * math.atan(9.4 / 34.1)), rivet=.6)
    # The dorsal trench with its spine and lights, deck lines, window rows on the upper slopes.
    k.block(a.part('Trench', 'Undercarriage'), (1.6, 20.0, .3), loc=(0, -2.0, top_z(-2.0) - .1), chamfer=.02)
    a.part('Spine', 'Armor').box((.6, 20.0, .4), loc=(0, -2.0, top_z(-2.0) + .05), bevel=.03)
    lights = a.part('Spine_lights', 'Lamp')
    for y in range(-11, 8, 2):
        lights.box((.15, .15, .06), loc=(0, y, top_z(-2.0) + .27), bevel=0)
    lines = a.part('Deck_lines', 'Undercarriage')
    for y in range(-14, 14, 3):
        w = half_w(y)
        for s in (-1, 1):
            lines.box((w * .5, .06, .02), loc=(s * w * .55, y, top_z(y) * .88), rot=(0, -s * .38, 0), bevel=0)
    win = a.part('Windows', 'Lamp')
    for s in (-1, 1):
        for y in (-6.0, -3.0, 0.0, 3.0, 6.0, 9.0):
            w = half_w(y)
            win.box((.9, .25, .05), loc=(s * w * .55, y, top_z(y) * .86), rot=(0, -s * .38, 0), bevel=0)
    # Belly plates, deck fittings (clutter) on the upper hull's flat.
    for i, y in enumerate((-9.0, -4.0, 10.0)):
        K.armour_plate(a, a.part('Belly_plates', 'Armor'), (3.0 + .4 * i, 2.2, .1), (0, y, bot_z(y) - .04),
                       rivet=.7)
    for s in (-1, 1):
        P.clutter(a, 'Greebles', 'Armor', s * 1.2 if s > 0 else -4.5, 4.5 if s > 0 else -1.2, 4.0, 12.0,
                  top_z(8.0) - .05, 16, seed=7 + s, size=(.3, 1.2), height=(.15, .6))
    P.clutter(a, 'Greebles_light', 'PlasterWhite', -3.5, 3.5, 12.0, 14.8, top_z(13.0) - .05, 12, seed=9,
              size=(.3, 1.0), height=(.2, .7))
    a.pivot('Point_fire', (0, 3.0, 3.6))


def _superstructure(a):
    """The stepped superstructure aft and the bridge tower with its dishes and the APS emitters."""
    st = a.part('Hull', 'Plaster')
    for (w, d, h, y, z) in ((9.0, 8.0, 1.2, 9.0, 2.6), (6.0, 6.0, 1.2, 9.5, 3.8), (3.2, 4.0, 1.4, 10.0, 5.0)):
        k.block(st, (w, d, h), loc=(0, y, z + h / 2), chamfer=.12, taper=(.85, .85))
    a.part('Step_windows', 'Lamp').box((5.2, .05, .25), loc=(0, 6.45, 4.4), bevel=0)
    a.part('Step_windows', 'Lamp').box((8.0, .05, .25), loc=(0, 5.05, 3.2), bevel=0)
    # The bridge tower.
    k.extrude(a.part('Hull_tower', 'Plaster'), [(-1.0, -1.4), (1.0, -1.4), (1.3, .2), (1.0, 1.4), (-1.0, 1.4),
                                                (-1.3, .2)], 1.6, loc=(0, 10.5, 7.2), axis='Z', chamfer=.06,
              taper=(.85, .9), caps=(False, True))
    k.block(a.part('Hull_bridge', 'Armor'), (4.0, 1.6, .8), loc=(0, 10.0, 8.2), chamfer=.08, taper=(.85, .8))
    a.part('Bridge_windows', 'Lamp').box((3.4, .05, .22), loc=(0, 9.22, 8.6), rot=(.2, 0, 0), bevel=0)
    for s in (-1, 1):
        a.part('Dish_posts', 'Steel').cyl(.12, 1.0, loc=(s * 1.6, 10.6, 8.9), seg=8, bevel=0)
        K.dish(a.part('Tower_dishes', 'PlasterWhite'), a.part('Dish_feed', 'Steel'), (s * 1.6, 10.6, 9.5), r=.75,
               normal=(s * .6, -.3, 1), seg=14)
    m = a.pivot('Mount_APS', (0, 10.4, 8.65))
    k.lathe(a.part('Aps_emitter', 'Armor', m), [(.35, 0), (.35, .15), (.2, .3), (0, .32)], seg=10)
    a.part('Aps_glow', 'Energy', m).sphere(.14, loc=(0, -.1, .32), seg=8, rings=4)
    a.part('Aurel_stripes', 'Team').box((4.02, 1.62, .15), loc=(0, 10.0, 7.95), bevel=0)


def _weapons(a):
    # Four turbolaser turrets on the upper hull slopes (decor: the def's lasers fire from the gun mounts).
    for (x, y) in ((4.6, 1.0), (-4.6, 1.0), (6.2, 6.0), (-6.2, 6.0)):
        z = top_z(y) * .78 + .15
        k.lathe(a.part('Turbolasers', 'Armor'), [(.8, 0), (.8, .25), (.6, .5), (0, .55)], loc=(x, y, z), seg=10)
        for dx in (-.18, .18):
            a.part('Turbolaser_barrels', 'Steel').cyl(.07, 1.6, loc=(x + dx, y - 1.0, z + .35), rot=(R90, 0, 0),
                                                      seg=6, bevel=0)
    # The point-defence lasers forward (breakable: Pd_laser_l / _r).
    for name, x, tag in (('Pd_laser_l', 3.2, ''), ('Pd_laser_r', -3.2, '_r')):
        p = a.pivot(name, (x, -5.0, 3.2))
        k.lathe(a.part('Pd_base' + tag, 'Armor', p), [(.7, -1.4), (.7, -.2), (.55, 0), (0, 0)], seg=10)
        a.part('Pd_dome' + tag, 'Armor', p).sphere(.45, loc=(0, 0, .1), seg=10, rings=5)
        a.part('Pd_emitter' + tag, 'Steel', p).cyl(.09, .7, loc=(0, -.5, .35), rot=(R90 - .3, 0, 0), seg=6, bevel=0)
        a.part('Pd_glow' + tag, 'Energy', p).sphere(.1, loc=(0, -.85, .45), seg=6, rings=4)
        K.tone(a, name, k=.86)
    # The forward ball guns under the chine (one barrel each; the L3 wrapper makes them twins).
    for i, x in enumerate((2.4, -2.4)):
        m = a.pivot(K.name('Mount_gun', i), (x, -6.0, -1.4))
        tag = '' if i == 0 else '_001'
        a.part('Gun_ball' + tag, 'Armor', m).sphere(.75, seg=12, rings=8)
        for dx in (-.19, .19):
            k.lathe(a.part('Gun_barrel' + tag, 'Steel', m), [(.1, 0), (.09, .3), (.08, 1.9), (.11, 2.0), (.11, 2.2),
                                                             (0, 2.2)], loc=(dx, -.6, -.2), rot=(R90 + .12, 0, 0),
                    seg=8)
        mz = K.name('Muzzle_gun', i)
        a.pivot(mz, (0, -2.7, -.45), K.name('Mount_gun', i))
        a.pivot(f'Muzzle_b1_gun{tag}', (-.19 if x > 0 else .19, 0, 0), mz)
        a.pivot(f'Muzzle_b2_gun{tag}', (.19 if x > 0 else -.19, 0, 0), mz)
        K.tone(a, K.name('Mount_gun', i), k=.88)


def _belly(a):
    """Drop-pod bays, folded landing legs, the main thruster block."""
    for i, (x, y) in enumerate(((4.0, 2.0), (0.0, 5.0), (-4.0, 2.0)), start=1):
        p = a.pivot(f'Pod_bay_{i}', (x, y, -2.0))
        k.lathe(a.part(f'Bay_ring_{i}', 'Armor', p), [(1.25, -.4), (1.25, .1), (.95, .1), (.95, -.4)], seg=14)
        k.lathe(a.part(f'Bay_pod_{i}', 'Team', p), [(0, -.9), (.5, -.75), (.8, -.3), (.8, .3), (0, .35)], seg=12)
        a.part(f'Bay_glow_{i}', 'Energy', p).torus(.88, .05, loc=(0, 0, -.42), seg=14, ring=3)
        for j in range(4):
            u = j * R90 + .4
            a.part(f'Bay_frame_{i}', 'Steel', p).box((.15, .5, .5), loc=(math.cos(u) * 1.1, math.sin(u) * 1.1, -.4),
                                                     rot=(0, 0, u), bevel=0)
        K.tone(a, f'Pod_bay_{i}', k=.88)
    legs = a.part('Legs', 'Steel')
    pads = a.part('Leg_pads', 'Armor')
    for (x, y) in ((5.0, -2.0), (-5.0, -2.0), (6.5, 9.0), (-6.5, 9.0)):
        z = bot_z(y) * .8
        legs.limb((x, y, z), (x * 1.05, y + 2.0, z - .8), .3, .35, bevel=.03)
        legs.limb((x * 1.05, y + 2.0, z - .8), (x * 1.08, y + 1.0, z - 1.1), .22, .22, bevel=.02)
        k.block(pads, (1.0, 1.4, .2), loc=(x * 1.08, y + 1.0, z - 1.2), chamfer=.04)
    t = a.pivot('Thruster_main', (0, 15.5, .6))
    k.block(a.part('Engine_housing', 'Armor', t), (12.0, 2.0, 3.2), loc=(0, .3, 0), chamfer=.15, taper=(.92, .9))
    for i in range(6):
        x = -5.0 + i * 2.0
        k.lathe(a.part('Engine_nozzles', 'Steel', t), [(.75, 0), (.85, .6), (.8, .7), (.6, .7)],
                loc=(x, 1.3, (i % 2) * .5 - .25), rot=K.BACKWARD, seg=12, caps=(False, True))
        a.part('Engine_glow', 'Energy', t).cyl(.6, .05, loc=(x, 1.9, (i % 2) * .5 - .25), rot=(R90, 0, 0), seg=12,
                                               bevel=0)
    K.tone(a, 'Thruster_main', k=.86)
    a.pivot('Point_exhaust', (0, 19.0, .6))
    K.soot(a, (0, 17.0, .6), radius=4.0, k=.3)


def _skin(a):
    """The serrated chine (side sponsons), the hull plating patchwork in three tones, more deck fittings, the sensor
    blister on the right flank: the read of the big wedge from the battle camera."""
    ang = math.atan(9.4 / 34.1)
    for s in (-1, 1):
        for i, y in enumerate((-13.0, -9.0, -5.0, -1.0, 3.0, 7.0, 11.0)):
            w = half_w(y)
            L, d, h = 1.6 + .3 * (i % 3), .7 + .1 * (i % 2), .8 + .15 * (i % 3)
            k.block(a.part('Step_recesses', 'Armor'), (d, L, h), loc=(s * (w + d * .3), y, 0), rot=(0, 0, -s * ang),
                    chamfer=.08)
            a.part('Step_windows', 'Lamp').box((.05, L * .7, .15), loc=(s * (w + d * .8 + .01), y, .15),
                                               rot=(0, 0, -s * ang), bevel=0)
    tones = ('PlasterWhite', 'Concrete', 'Armor')
    for i, y in enumerate(range(-15, 13, 2)):
        w = half_w(y)
        for j, f in enumerate((.3, .55, .78)):
            if f * w < 1.1:
                continue
            for s in (-1, 1):
                mat = tones[(i + j + (s > 0)) % 3]
                zz = top_z(y) * (1.0 - (f - .3) / .52 * .3) + .04
                a.part(f'Hull_plates_{mat.lower()}', mat).box((.9 + .1 * (i % 4), 1.3 + .1 * (j + i % 3), .04),
                                                               loc=(s * f * w, y, zz), rot=(0, -s * .38, 0), bevel=0)
    P.clutter(a, 'Deck_fittings', 'Steel', -1.6, 1.6, -15.0, -9.0, top_z(-9.0) - .3, 14, seed=21, size=(.2, .6),
              height=(.2, .5))
    x, y = -half_w(4.0) - .4, 4.0
    k.lathe(a.part('Sensor_blister', 'Armor'), [(0, -1.8), (.9, -1.4), (1.1, 0), (.9, 1.4), (0, 1.8)],
            loc=(x, y, .3), rot=K.FORWARD, seg=10)
    a.part('Antennas', 'Steel').cyl(.06, 3.0, loc=(x, y + .5, 1.8), seg=5, bevel=0)
    a.part('Antennas', 'Steel').cyl(.05, 2.2, loc=(3.0, 12.5, 7.9), seg=5, bevel=0)
    for j, (x, y) in enumerate(((2.2, -8.0), (-2.6, -4.0), (3.4, 4.5), (-3.8, 6.0), (1.8, 2.5), (-1.5, -11.0))):
        h = 1.2 + .4 * (j % 4)
        a.part('Antennas', 'Steel').cyl(.05, h, loc=(x, y, top_z(y) + h / 2), seg=5, bevel=0)
        a.part('Antenna_tips', 'BarrelRed').box((.12, .12, .12), loc=(x, y, top_z(y) + h), bevel=0)
    for s in (-1, 1):
        x, y, z = s * 3.6, 7.0, 3.8
        k.block(a.part('Comm_towers', 'Plaster'), (.9, .9, 1.6), loc=(x, y, z + .8), chamfer=.06, taper=(.8, .8))
        K.dish(a.part('Tower_dishes', 'PlasterWhite'), a.part('Dish_feed', 'Steel'), (x, y, z + 1.9), r=.55,
               normal=(s * .7, -.6, .6), seg=12)
        k.extrude(a.part('Stern_vanes', 'Armor'), [(0, 0), (1.6, 0), (1.9, 2.4), (1.2, 2.4)], .2,
                  loc=(s * 6.5, 15.2, 1.4), rot=(0, -s * .35, 0), axis='X', chamfer=.02)


def daedalus(a):
    K.suffixed(a)
    _hull(a)
    _skin(a)
    _superstructure(a)
    _weapons(a)
    _belly(a)
    k.clean(a)


BUILDERS = {'daedalus': (daedalus, dict(ao_distance=1.5, grime_height=.2, ground=False))}
