"""Prompt 35 wave 10 (lane B): Gungnir, the rail supergun, rebuilt from scratch (spec:
Tools/blender/specs/rail_supergun.json).

unit_refs: the US Navy EMRG (an electromagnetic railgun, scaled up), the BZhRK Barguzin rail train, a modern diesel
locomotive (the separate rail_tractor model the def's tractor_l / _r parts attach); BossText: a super-heavy
electromagnetic gun on a railway, one shot every 25 s through several targets. Drawn at the old file's size
(63.9 x 8.8 x 16.5 m, the barrel raised; the def has no modelSize). The gun car: the track bed (sleepers, rails, the
ballast shoulders), four two-axle bogies under the long girder carriage (Deck) with its sloped armour skirts, the
deployed outrigger jacks on pads, walkways, ladders, railings and the deck fittings; the turntable and the armoured
gun house (`Part_main` > `Turret`) with its sloped cheeks, the trunnion block and the elevating rams; the 40 m
railgun barrel (`Main_cannon`, the main_gun part): a square rail housing in segments with clamping collars, the
glowing rail gap, coolant pipes, the support truss under it and the muzzle shroud (`Muzzle_brake`), the loading crane
on the turret's rear (`Part_crane`); the capacitor banks and cable runs on the rear deck, the fire-control cabin with
its radar (`Part_generator`, fire_control), the two 40 mm turrets forward (`Part_gun` / `.001` > `Mount_gun`) and the
two CIWS aft (`Part_mg` / `.001` > `Mount_mg`), the Team bands and hazard marks. Boss rule: the breakable parts are on
their own nodes, one shade off.

Runtime nodes kept at their old places: `Part_main`, `Turret`, `Part_crane`, `Muzzle_main` (0, -37.8, 15.74),
`Part_generator`, `Part_gun` / `.001` > `Mount_gun` / `.001` > `Muzzle_gun` / `.001`, `Part_mg` / `.001` >
`Mount_mg` / `.001` > `Muzzle_mg` / `.001`. Built only from frontier_kit / mb_kit27 primitives, mb_kit35 and lane
B's helpers; no other model's builder. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
DECK = 3.56
Y0, Y1 = -19.0, 17.0      # carriage front / rear
HW = 2.2                  # carriage half width
TRUN = (0, 1.5, 6.5)      # trunnion, world
TP = (0, 0, 3.7)          # Turret pivot, world
MUZ = (0, -37.8, 15.74)


def _track(a):
    k.extrude(a.part('Ballast', 'Rock'), [(-2.4, 0), (2.4, 0), (1.7, .18), (-1.7, .18)], 44.0, loc=(0, -1.0, 0),
              axis='Y', chamfer=0)
    rails = a.part('Rails', 'Steel')
    sl = a.part('Sleepers', 'Concrete')
    for s in (-1, 1):
        k.extrude(rails, [(-.04, 0), (.04, 0), (.015, .04), (.015, .13), (.04, .16), (-.04, .16), (-.015, .13),
                          (-.015, .04)], 44.0, loc=(s * .72, -1.0, .38), axis='Y')
    for i in range(62):
        y = -22.8 + i * .7
        sl.box((2.6, .24, .2), loc=(0, y, .28), bevel=0)
    clips = a.part('Kit_clips', 'Steel')
    for i in range(0, 62, 2):
        y = -22.8 + i * .7
        for s in (-1, 1):
            clips.box((.18, .1, .05), loc=(s * .72, y, .4), bevel=0)


def _carriage(a):
    for y in (-15.5, -11.0, 9.0, 13.5):
        K.bogie(a, (0, y, .38), gauge=1.44, wheel_r=.46, base=2.4)
    deck = a.part('Deck', 'Armor')
    k.extrude(deck, [(-HW, 0), (HW, 0), (HW, .9), (HW - .3, 1.3), (-HW + .3, 1.3), (-HW, .9)], Y1 - Y0,
              loc=(0, (Y0 + Y1) / 2, DECK - 1.3), axis='Y', chamfer=.05)
    skirt = a.part('Hull_skirts', 'Team')
    for s in (-1, 1):
        k.extrude(skirt, [(0, 0), (.25, 0), (.05, 1.0), (-.05, 1.0)], Y1 - Y0 - 2.0,
                  loc=(s * (HW + .02), (Y0 + Y1) / 2, DECK - 1.75), rot=(0, 0, 0 if s > 0 else math.pi), axis='Y',
                  chamfer=.02)
        a.part('Team_band', 'Team').box((.03, Y1 - Y0 - 4.0, .2), loc=(s * (HW + .06), (Y0 + Y1) / 2, DECK - .5),
                                        bevel=0)
        # Deployed outrigger jacks on pads.
        for y in (-17.5, -7.5, 5.0, 15.5):
            K.outrigger(a.part('Outriggers', 'Steel'), a.part('Jack_pads', 'Armor'), (s * (HW + .1), y, DECK - 1.0),
                        s, reach=1.4, drop=DECK - 1.0, w=.3)
        K.railing(a.part('Railings', 'Steel'), [(s * (HW - .1), Y0 + .5, DECK), (s * (HW - .1), -5.0, DECK)], h=.9,
                  post=1.5, r=.025)
        K.railing(a.part('Railings', 'Steel'), [(s * (HW - .1), 5.5, DECK), (s * (HW - .1), Y1 - .5, DECK)], h=.9,
                  post=1.5, r=.025)
        for y in (-18.6, 16.6):
            K.ladder(a.part('Ladders', 'Steel'), (s * 1.5, y, .5), (s * 1.5, y, DECK), width=.45, step=.3, r=.02)
    P.plane(a.part('Walkways', 'Undercarriage'), -1.9, 1.9, Y0 + .2, Y1 - .2, DECK + .005)
    lines = a.part('Deck_lines', 'Charred')
    for y in range(int(Y0) + 1, int(Y1), 2):
        lines.box((3.8, .05, .01), loc=(0, y, DECK + .01), bevel=0)
    for y in (Y0 - .1, Y1 + .1):
        k.block(a.part('Buffers', 'Steel'), (.3, .5, .3), loc=(.9, y, 1.4), chamfer=.03)
        k.block(a.part('Buffers', 'Steel'), (.3, .5, .3), loc=(-.9, y, 1.4), chamfer=.03)
        a.part('Hazard_marks', 'Hazard').box((3.8, .04, .3), loc=(0, y, 2.6), bevel=0)
    P.clutter(a, 'Deck_fittings', 'Steel', -1.8, 1.8, -8.5, -4.5, DECK, 16, seed=31, size=(.2, .6), height=(.15, .5))
    P.clutter(a, 'Deck_lockers', 'Armor', -1.8, 1.8, 5.0, 8.0, DECK, 10, seed=32, size=(.3, .8), height=(.3, .7))


def _gun(a):
    pm = a.pivot('Part_main', (0, 0, DECK))
    t = a.pivot('Turret', (0, 0, TP[2] - DECK), 'Part_main')
    k.lathe(a.part('Turntable', 'Steel', pm), [(3.0, -.05), (3.0, .1), (2.8, .14), (0, .14)], seg=20)
    # The armoured gun house: sloped cheeks, the trunnion block.
    k.extrude(a.part('Turret_walls', 'Armor', t), [(-2.4, -2.6), (2.4, -2.6), (2.8, -1.0), (2.8, 3.0), (2.2, 3.8),
                                                   (-2.2, 3.8), (-2.8, 3.0), (-2.8, -1.0)], 3.0, loc=(0, 0, 1.5),
              axis='Z', chamfer=.08, corner=.06, taper=(.78, .82), caps=(False, True))
    a.part('Team_band', 'Team', t).box((4.6, .04, .3), loc=(0, 3.62, 1.8), bevel=0)
    tl, tz = TRUN[1] - TP[1], TRUN[2] - TP[2]
    for s in (-1, 1):
        k.block(a.part('Turret_armor', 'Armor', t), (.7, 3.0, 2.4), loc=(s * 1.25, tl, tz - .4), chamfer=.08,
                taper=(.85, .9))
        a.part('Trunnions', 'Steel', t).cyl(.45, .5, loc=(s * 1.0, tl, tz), rot=(0, R90, 0), seg=12, bevel=0)
    # The barrel: from 6 m behind the trunnion to the old muzzle.
    dy, dz = MUZ[1] - TRUN[1], MUZ[2] - TRUN[2]
    e = math.atan2(dz, -dy)
    L = math.hypot(dy, dz)
    bore = P.Elev((0, tl, tz), e)
    for s in (-1, 1):
        a.part('Rams', 'Steel', t).tube([(s * .9, -1.5, .4), bore.at(6.0, dx=s * .9, up=-.6)], .2, seg=8)
    segs = [(-6.0, 0.0, 1.9, 2.1), (0.0, 8.0, 1.7, 1.9), (8.0, 18.0, 1.5, 1.7), (18.0, 28.0, 1.35, 1.5),
            (28.0, L - 2.4, 1.2, 1.35)]
    for t0, t1, w, h in segs:
        k.block(a.part('Main_cannon', 'Steel', t), (w, t1 - t0, h), loc=bore.at((t0 + t1) / 2), rot=bore.box_rot,
                chamfer=.08)
    # The cradle shroud round the barrel's root: a big sloped armoured box (Team) with its side vents.
    k.block(a.part('Turret_cradle', 'Team', t), (3.2, 13.0, 2.9), loc=bore.at(.5, up=-.2), rot=bore.box_rot,
            chamfer=.2, taper=(.8, .75))
    for s in (-1, 1):
        for j in range(4):
            a.part('Cradle_vents', 'Undercarriage', t).box((.05, 1.4, .5), loc=bore.at(-3.0 + j * 2.6, dx=s * 1.62,
                                                                                       up=-.1),
                                                           rot=bore.box_rot, bevel=0)
    glow = a.part('Main_cannon_glow', 'Energy', t)
    col = a.part('Main_cannon_collars', 'Armor', t)
    for i, tt in enumerate(range(1, int(L - 3), 3)):
        w = 1.9 - .7 * tt / L
        col.box((w + .25, .35 + .05 * (i % 3), w * 1.1 + .25), loc=bore.at(tt), rot=bore.box_rot, bevel=0)
    glow.box((.12, L - 9.0, .12), loc=bore.at((L + 3.0) / 2, up=.75), rot=bore.box_rot, bevel=0)
    for s in (-1, 1):
        a.part('Coolant_pipes', 'Undercarriage', t).tube([bore.at(t0, dx=s * .9, up=-.2) for t0 in (-4.0, 10.0, 24.0,
                                                                                                      L - 4.0)],
                                                         .1, seg=5)
    truss = a.part('Barrel_truss', 'Steel', t)
    for i in range(8):
        t0 = 2.0 + i * 3.6
        truss.tube([bore.at(t0, up=-.8), bore.at(t0 + 1.8, up=-1.6), bore.at(t0 + 3.6, up=-.8)], .06, seg=4,
                   caps=False)
    truss.tube([bore.at(2.0, up=-1.6), bore.at(30.0, up=-1.6)], .08, seg=4)
    k.block(a.part('Muzzle_brake', 'Undercarriage', t), (1.6, 2.4, 1.6), loc=bore.at(L - 1.2), rot=bore.box_rot,
            chamfer=.12, taper=(.85, .85))
    a.pivot('Muzzle_main', (0, MUZ[1] - TP[1], MUZ[2] - TP[2]), 'Turret')
    K.soot(a, MUZ, radius=2.0, k=.4)
    # The loading crane on the turret's rear (Part_crane).
    c = a.pivot('Part_crane', (-2.3, 10.0 - TP[1], 5.6 - TP[2]), 'Turret')
    k.lathe(a.part('Crane_post', 'CraneYellow', c), [(.25, -.3), (.25, 1.6), (.18, 1.7)], seg=8)
    a.part('Crane_jib', 'CraneYellow', c).limb((0, 0, 1.6), (0, -4.0, 2.6), .25, .3, bevel=.02)
    a.part('Kit_cables', 'Undercarriage', c).tube([(0, -4.0, 2.5), (0, -4.0, .8)], .03, seg=4)
    K.tone(a, 'Part_main', k=.92)


def _rear(a):
    """Capacitor banks with cable runs, the fire-control cabin (Part_generator) with its radar, the CIWS."""
    for i, y in enumerate((5.8, 7.6, 15.2)):
        k.block(a.part('Capacitor_banks', 'Armor'), (3.6, 1.5, 2.1), loc=(0, y, DECK + 1.05), chamfer=.08)
        for x in (-1.2, -.4, .4, 1.2):
            a.part('Capacitor_caps', 'Steel').cyl(.18, .25, loc=(x, y, DECK + 2.2), seg=8, bevel=0)
        a.part('Capacitor_glow', 'Energy').box((3.2, .05, .12), loc=(0, y - .72, DECK + 1.1), bevel=0)
    cab = a.part('Kit_cables', 'Rubber')
    for x in (-.8, 0, .8):
        cab.tube([(x, 5.1, DECK + .6), (x * .8, 3.6, DECK + .3), (x * .5, 2.2, DECK + .9)], .08, seg=5)
    p = a.pivot('Part_generator', (0, 11.2, DECK))
    k.extrude(a.part('Hull_cabin', 'Plaster', p), [(-1.7, -1.6), (1.7, -1.6), (1.9, 1.6), (-1.9, 1.6)], 2.2,
              loc=(0, 0, 1.1), axis='Z', chamfer=.06, corner=.06, taper=(.88, .9), caps=(False, True))
    a.part('Cabin_windows', 'Lamp', p).box((3.0, .05, .35), loc=(0, -1.48, 1.7), rot=(.1, 0, 0), bevel=0)
    a.part('Team_band', 'Team', p).box((3.44, 3.24, .2), loc=(0, 0, 2.0), bevel=0)
    k.lathe(a.part('Radar_post', 'Steel', p), [(.15, 2.2), (.15, 3.2), (.25, 3.25)], seg=8)
    k.extrude(a.part('Radar_array', 'PlasterWhite', p), [(-1.0, -.06), (1.0, -.06), (.9, .06), (-.9, .06)], .7,
              loc=(0, 0, 3.7), rot=(-.3, 0, 0), axis='Z', chamfer=.015)
    K.whip_antenna(a.part('Antennas', 'Steel', p), (1.4, 1.2, 2.2), h=1.6, r=.03)
    K.tone(a, 'Part_generator', k=.88)
    for i, x in enumerate((2.55, -2.55)):
        part = K.name('Part_mg', i)
        p = a.pivot(part, (x, 12.1, DECK))
        k.lathe(a.part('Ciws_base' + ('' if i == 0 else '_001'), 'Armor', p), [(.6, 0), (.6, .4), (.5, .55), (0, .6)],
                seg=10)
        m = a.pivot(K.name('Mount_mg', i), (0, 0, .66), part)
        tag = '' if i == 0 else '_001'
        a.part('Ciws_dome' + tag, 'PlasterWhite', m).sphere(.45, loc=(0, .1, .45), seg=10, rings=6)
        k.block(a.part('Ciws_body' + tag, 'Armor', m), (.6, .9, .55), loc=(0, .1, .1), chamfer=.04)
        for dx in (-.06, .06):
            a.part('Ciws_barrels' + tag, 'Steel', m).cyl(.04, 1.8, loc=(dx, -1.75, .62), rot=(R90, 0, 0), seg=6,
                                                        bevel=0)
        a.pivot(K.name('Muzzle_mg', i), (0, -2.67, .62), K.name('Mount_mg', i))
        K.tone(a, part, k=.88)


def _front(a):
    """The two 40 mm turrets forward (Part_gun / .001 > Mount_gun)."""
    for i, x in enumerate((2.6, -2.6)):
        part = K.name('Part_gun', i)
        p = a.pivot(part, (x, -11.3, DECK))
        tag = '' if i == 0 else '_001'
        k.lathe(a.part('Gun_ring' + tag, 'Armor', p), [(.9, 0), (.9, .5), (.75, .7), (0, .75)], seg=12)
        m = a.pivot(K.name('Mount_gun', i), (0, 0, .8), part)
        k.extrude(a.part('Gun_house' + tag, 'Armor', m), [(-.6, -.8), (.6, -.8), (.8, -.2), (.8, .7), (-.8, .7),
                                                          (-.8, -.2)], .7, loc=(0, 0, .35), axis='Z', chamfer=.04,
                  corner=.04, taper=(.8, .85), caps=(False, True))
        k.lathe(a.part('Gun_barrel' + tag, 'Steel', m), [(.09, 0), (.07, .2), (.065, 2.2), (.09, 2.3), (0, 2.35)],
                loc=(0, -.8, .31), rot=K.FORWARD, seg=8)
        a.pivot(K.name('Muzzle_gun', i), (0, -3.15, .31), K.name('Mount_gun', i))
        K.tone(a, part, k=.88)


def rail_supergun(a):
    K.suffixed(a)
    _track(a)
    _carriage(a)
    _gun(a)
    _rear(a)
    _front(a)
    k.clean(a)


BUILDERS = {'rail_supergun': (rail_supergun, dict(ao_distance=1.5, grime_height=.6, ao_strength=.7))}
