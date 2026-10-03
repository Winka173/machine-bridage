"""Prompt 35 wave 10 (lane B): the command airship ("Sky Admiral") rebuilt from scratch (spec:
Tools/blender/specs/command_airship.json).

unit_refs: Airlander 10, Lockheed P-791 (modern hybrid airships), the Kirov airship (Red Alert 2) for the media
read; "a flying battleship with two gas envelopes". Drawn as the old file's size (45.5 x 31.5 x 16.1 m; the def has
no modelSize): two long envelopes side by side (Team, the lift role) with their ballonet seams, catenary bands,
nose battens and cruciform tail fins, joined by the armoured spine deck carrying the two dual-purpose turrets
(`Part_gun` > `Mount_gun`, `Part_gun.001` > `Mount_gun.001`: the 57 mm gun with a twin 30 mm beside it, one muzzle a
barrel) and the radar mast (`Part_radar` > `Radar`: the spinning array); under the spine the keel gondola: the
bridge with its window band and the command deck forward, the bomb bay (the def's bomb_bay hit area) with its two
doors on hinge pivots (`Part_bay_door_L` / `_R`: a later bomb-run pass opens them) over the racked bombs, the two
drone hangars (`Part_hangar` / `.001` with their doors, rails, cradles and drones; `Muzzle_door_l` / `_r`), the
portholes, railings, floodlights and the antenna farm; under each envelope the 105 mm ball pod on its strut
(`Mount_gun.002` / `.003`); outboard the four engine nacelles on their pylons (`Part_engine` .. `.003`: the weak
points the tip names, riveted and one shade off) with their propellers (`Propeller`, `_2`, `_3`, `_4`), beacons, nav
lights, the flag. Boss rule: drawn for the read, the breakable parts on their own nodes.

Runtime nodes kept at their old places: every `Part_*`, `Mount_*`, `Muzzle_*`, `Propeller*` and `Radar` of the old
file; new: `Muzzle_b1_gun` / `_b2_gun` and `_gun_001` (the twin 30 mm barrels: the def's eight mounts want eight
muzzles), `Part_bay_door_L` / `_R`. Built only from frontier_kit / mb_kit27 primitives, mb_kit35 and lane B's
helpers; no other model's builder. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
EX, EZ = 7.4, 1.0        # envelope centre line (x = +/-EX, z = EZ)
ER, EH = 4.6, 4.5        # envelope half width / half height
EY0, EY1 = -21.5, 21.0   # envelope nose / tail
DECK = 2.6               # spine deck top
GZ0, GZ1 = -4.2, -1.2    # keel gondola bottom / top


def env_r(y):
    """Envelope radius factor along its length (a blunt nose, a long tail taper)."""
    f = (y - EY0) / (EY1 - EY0)
    if f < .18:
        return math.sqrt(max(0.0, 1 - ((.18 - f) / .18) ** 2))
    if f > .62:
        return max(.08, math.cos((f - .62) / .38 * R90 * .92))
    return 1.0


def _envelopes(a):
    seg = 16
    for s in (-1, 1):
        rings = []
        for y in (EY0, -20.7, -19.5, -17.5, -14.5, -10.0, 0.0, 5.0, 9.0, 12.5, 15.5, 18.0, 19.8, EY1):
            f = env_r(y)
            rings.append([(s * EX + math.cos(u) * ER * f, y, EZ + math.sin(u) * EH * f)
                          for u in (i * TAU / seg for i in range(seg))])
        rings[0] = [(s * EX, EY0, EZ)]
        rings[-1] = [(s * EX, EY1 + .3, EZ)]
        a.part('Envelopes', 'Team').loft(rings, bevel=0)
        # Ballonet seams and catenary bands (circumferential), the nose battens, the ridge line.
        band = a.part('Envelope_bands', 'Undercarriage')
        for y in (-16.0, -12.5, -9.0, -5.5, -2.0, 1.5, 5.0, 8.5, 12.0):
            f = env_r(y)
            band.torus(ER * f + .02, .06, loc=(s * EX, y, EZ), rot=(R90, 0, 0), seg=seg, ring=3)
            # Squash the ring to the envelope's height (scale the last 16*3 verts).
            vs = band.bm.verts[-seg * 3:]
            for v in vs:
                v.co.z = EZ + (v.co.z - EZ) * EH / ER
        for i in range(8):
            u = i * TAU / 8
            pts = [(s * EX + math.cos(u) * ER * env_r(y) * 1.004, y, EZ + math.sin(u) * EH * env_r(y) * 1.004)
                   for y in (-21.0, -20.2, -18.8, -17.0)]
            a.part('Nose_battens', 'Armor').tube(pts, .07, seg=4, caps=False)
        a.part('Team_band', 'Team').box((.4, 30.0, .05), loc=(s * EX, -2.0, EZ + EH + .02), bevel=0)
        # The cruciform tail fins (an X, as on the hybrids), their control surfaces.
        fin = a.part('Tail_fins', 'Armor')
        for j in range(4):
            u = TAU / 8 + j * R90
            c, sn = math.cos(u), math.sin(u)
            r0 = ER * env_r(16.5) * .95
            pts = [(s * EX + c * r0, 14.0, EZ + sn * r0 * EH / ER), (s * EX + c * r0, 19.2, EZ + sn * r0 * EH / ER),
                   (s * EX + c * (r0 + 3.0), 20.0, EZ + sn * (r0 + 3.0)), (s * EX + c * (r0 + 3.0), 17.4,
                                                                             EZ + sn * (r0 + 3.0))]
            fin.mesh(pts + [(x + .12 * sn, y, z - .12 * c) for x, y, z in pts],
                     [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)])
            a.part('Fin_rudders', 'Undercarriage').box((.14, .3, 2.6), loc=(s * EX + c * (r0 + 1.5), 19.55,
                                                                             EZ + sn * (r0 + 1.5)),
                                                       rot=(0, -math.atan2(c, sn), 0), bevel=0)
        a.part('Nav_lights', 'LavaGlow' if s > 0 else 'SignalGreen').sphere(.25, loc=(s * (EX + ER), -6.0, EZ),
                                                                            seg=8, rings=4)


def env_pt(s, u, y, lift=0.0):
    """A point on the envelope (side s) at angle u (0 = outboard for s > 0) and station y, `lift` metres off it."""
    f = env_r(y)
    return (s * EX + math.cos(u) * (ER * f + lift), y, EZ + math.sin(u) * (EH * f + lift))


def _envelope_skin(a):
    """Gore seams, the ridge walkway, solar arrays (left), the observation blister and antenna farm (right),
    vents and mooring points: the read of the big skins from the battle camera."""
    seam = a.part('Gore_seams', 'Charred')
    for s in (-1, 1):
        for u in (math.radians(d) for d in (20, 50, 75, 105, 130, 160)):
            uu = u if s > 0 else math.pi - u
            seam.tube([env_pt(s, uu, y, .03) for y in (-19.5, -17.0, -13.0, -6.0, 3.0, 10.0, 14.5, 17.5)], .05,
                      seg=3, caps=False)
        walk = a.part('Ridge_walkway', 'Undercarriage')
        walk.box((.8, 26.0, .06), loc=(s * EX, -2.5, EZ + EH + .05), bevel=0)
        posts = a.part('Ridge_rails', 'Steel')
        for y in range(-15, 11, 2):
            for d in (-.42, .42):
                posts.box((.05, .05, .6), loc=(s * EX + d, y, EZ + EH + .35), bevel=0)
        for d in (-.42, .42):
            posts.box((.04, 26.0, .04), loc=(s * EX + d, -2.5, EZ + EH + .62), bevel=0)
        vents = a.part('Envelope_vents', 'Steel')
        for j, y in enumerate((-13.5, -7.5, -1.0, 6.5, 11.0)):
            vents.cyl(.3 + .05 * j, .25 + .03 * j, loc=(s * (EX + 1.4), y, EZ + EH * .93), seg=8, bevel=0)
        for y in (-18.0, 15.0):
            a.part('Mooring_points', 'Hazard').box((.4, .4, .3), loc=(s * EX, y, EZ - EH * env_r(y) + .05), bevel=0)
    # Solar arrays on the left envelope's top (each panel its own size), a trunk cable.
    sol = a.part('Solar_panels', 'Glass')
    frame = a.part('Solar_frames', 'Steel')
    for i, y in enumerate(range(-13, 10, 2)):
        for u in (math.radians(62), math.radians(118)):
            x, yy, z = env_pt(1, u, y, .06)
            w, d = 1.1 + .04 * (i % 4), 1.5 + .05 * (i % 3)
            sol.box((w, d, .04), loc=(x, yy, z), rot=(0, (R90 - u), 0), bevel=0)
            frame.box((w + .1, .06, .06), loc=(x, yy - d / 2, z), rot=(0, (R90 - u), 0), bevel=0)
    # The observation blister on the right envelope's outboard flank, the antenna farm on its ridge.
    x, y, z = env_pt(-1, math.pi, -4.0)
    k.lathe(a.part('Observation_blister', 'Armor'), [(0, -2.4), (1.0, -2.0), (1.3, -.5), (1.3, 1.2), (.9, 2.2),
                                                      (0, 2.5)], loc=(x - .6, y, z), rot=K.FORWARD, seg=12)
    a.part('Command_windows', 'Glass').box((.05, 2.6, .5), loc=(x - 1.88, y, z + .3), bevel=0)
    ant = a.part('Antenna', 'Steel')
    for j, y in enumerate((-12.0, -9.5, 7.0, 9.0)):
        ant.cyl(.05, 2.0 + .5 * j, loc=(-EX + .2, y, EZ + EH + 1.0 + .25 * j), seg=5, bevel=0)
    K.dish(a.part('Dish', 'PlasterWhite'), a.part('Dish_feed', 'Steel'), (-EX, 3.0, EZ + EH + .6), r=.9,
           normal=(-.3, -.5, 1), seg=14)


def _spine(a):
    """The armoured spine deck between the envelopes: deck, sloped armour flanks, railings, deck clutter, turrets."""
    k.extrude(a.part('Deck_armor', 'Armor'), [(-2.6, 0), (2.6, 0), (2.1, .9), (-2.1, .9)], 30.0,
              loc=(0, -2.0, DECK - .9), axis='Y', chamfer=.06)
    P.plane(a.part('Deck', 'Steel'), -2.1, 2.1, -17.0, 13.0, DECK + .005)
    lines = a.part('Deck_lines', 'Undercarriage')
    for y in range(-16, 13, 2):
        lines.box((4.1, .04, .01), loc=(0, y, DECK + .01), bevel=0)
    K.railing(a.part('Railings', 'Steel'), [(2.05, -16.5, DECK), (2.05, 12.5, DECK)], h=.9, post=1.5, r=.03)
    K.railing(a.part('Railings', 'Steel'), [(-2.05, -16.5, DECK), (-2.05, 12.5, DECK)], h=.9, post=1.5, r=.03)
    # Struts from the deck down into each envelope (the joining truss).
    tr = a.part('Spine_truss', 'Undercarriage')
    for y in (-14.0, -8.0, -2.0, 4.0, 10.0):
        for s in (-1, 1):
            tr.tube([(s * 2.4, y, DECK - .7), (s * (EX - ER * .55), y + 1.0, EZ + 2.2)], .12, seg=5)
            tr.tube([(s * 2.4, y, DECK - .7), (s * (EX - ER * .7), y - 1.0, EZ - 1.0)], .1, seg=5)
    P.clutter(a, 'Deck_lockers', 'Armor', -1.9, 1.9, -9.0, -5.5, DECK, 14, seed=11, size=(.3, .9), height=(.2, .7))
    P.clutter(a, 'Deck_fittings', 'Steel', -1.9, 1.9, 1.5, 7.5, DECK, 18, seed=12, size=(.2, .7), height=(.15, .5))
    P.clutter(a, 'Deck_crates', 'Crate', -1.9, 1.9, -1.0, 1.0, DECK, 6, seed=13, size=(.4, .9), height=(.3, .6))
    for y in (-11.5, 8.0):
        K.hatch_rect(a, (1.2, y, DECK), size=(.8, .9))
    K.beacon(a, (1.6, 12.6, DECK), r=.15)
    a.part('Flag_pole', 'Steel').cyl(.06, 3.0, loc=(-1.6, 12.4, DECK + 1.5), seg=6, bevel=0)
    a.part('Flag', 'Team').box((.06, 1.6, 1.0), loc=(-1.6, 13.2, DECK + 2.5), rot=(0, 0, .1), bevel=0)


def _turret(a, i, y):
    """A dual-purpose turret: the barbette (`Part_gun`), the 57 mm house (`Mount_gun`), the twin 30 mm beside it."""
    part = K.name('Part_gun', i)
    p = a.pivot(part, (0, y, 3.0))
    tag = '' if i == 0 else '_001'
    k.lathe(a.part('Barbette' + tag, 'Armor', p), [(1.5, -.4), (1.45, -.05), (1.35, 0), (0, 0)], seg=16, worn=(1,))
    a.part('Barbette_band' + tag, 'Team', p).cyl(1.47, .14, loc=(0, 0, -.22), seg=16, bevel=0)
    m = a.pivot(K.name('Mount_gun', i), (0, 0, 0), part)
    k.extrude(a.part('Gun_house' + tag, 'Armor', m), [(-.95, -1.1), (.95, -1.1), (1.25, -.4), (1.25, .9), (.9, 1.3),
                                                      (-.9, 1.3), (-1.25, .9), (-1.25, -.4)], .9,
              loc=(0, 0, .45), axis='Z', chamfer=.05, corner=.05, taper=(.8, .85), caps=(False, True))
    k.block(a.part('Gun_mantlet' + tag, 'Armor', m), (.6, .4, .5), loc=(0, -1.2, .35), chamfer=.04)
    k.lathe(a.part('Gun_barrel' + tag, 'Steel', m), [(.13, 0), (.11, .3), (.1, 1.7), (.13, 1.8), (.13, 2.05),
                                                     (0, 2.05)], loc=(0, -1.25, .33), rot=K.FORWARD, seg=10, worn=(3,))
    a.pivot(K.name('Muzzle_gun', i), (0, -3.25, .33), K.name('Mount_gun', i))
    for j, dx in enumerate((-.85, .85)):
        a.part('Gun_twin' + tag, 'Steel', m).cyl(.05, 1.3, loc=(dx, -1.65, .22), rot=(R90, 0, 0), seg=6, bevel=0)
        a.part('Gun_twin_box' + tag, 'Armor', m).box((.3, .5, .3), loc=(dx, -.8, .22), bevel=0)
        a.pivot(f'Muzzle_b{j + 1}_gun{tag}', (dx, -2.3, .22), K.name('Mount_gun', i))
    a.part('Gun_glass' + tag, 'Glass', m).box((.5, .03, .12), loc=(.6, -.95, .8), rot=(.3, 0, 0), bevel=0)
    K.periscope(a, (-.5, .3, .9), parent=m)
    k.lathe(a.part('Gun_ring' + tag, 'Steel', p), [(1.32, 0), (1.32, .06), (1.2, .08)], seg=16)


def _radar(a):
    p = a.pivot('Part_radar', (0, -3.2, 6.66))
    ms = a.part('Radar_mast', 'Steel', p)
    for dx, dy in ((-.8, -.8), (.8, -.8), (.8, .8), (-.8, .8)):
        ms.tube([(dx, dy, DECK - 6.66), (dx * .3, dy * .3, 0)], .08, seg=4)
    for z in (-3.0, -1.5):
        f = .3 + .7 * (-z) / (6.66 - DECK)
        pts = [(dx * f, dy * f, z) for dx, dy in ((-.8, -.8), (.8, -.8), (.8, .8), (-.8, .8), (-.8, -.8))]
        ms.tube(pts, .04, seg=3, caps=False)
    k.lathe(a.part('Radar_platform', 'Armor', p), [(1.0, -.1), (1.0, .05), (0, .05)], seg=12)
    K.railing(a.part('Railings', 'Steel', p), [(math.cos(u), math.sin(u), .05) for u in (j * TAU / 10 for j in range(9))],
              h=.6, post=.6, r=.02)
    r = a.pivot('Radar', (0, 0, 1.72), 'Part_radar')
    k.block(a.part('Radar_turntable', 'Armor', r), (.7, .7, .3), loc=(0, 0, -.2), chamfer=.04)
    a.part('Radar_post', 'Steel', r).cyl(.12, .6, loc=(0, 0, .2), seg=8, bevel=0)
    k.extrude(a.part('Radar_array', 'PlasterWhite', r), [(-2.0, -.1), (2.0, -.1), (1.8, .1), (-1.8, .1)], .9,
              loc=(0, 0, .9), rot=(-.25, 0, 0), axis='Z', chamfer=.02)
    grid = a.part('Radar_grid', 'Undercarriage', r)
    for j in range(7):
        grid.box((.04, .03, .8), loc=(-1.5 + j * .5, -.14, .9), rot=(-.25, 0, 0), bevel=0)
    a.part('Radar_iff', 'Steel', r).box((3.4, .1, .12), loc=(0, -.05, 1.45), bevel=0)


def _gondola(a):
    """The keel gondola: bridge, command deck, bomb bay with its door pivots, hangars, portholes, antennas."""
    hull = a.part('Hull_gondola', 'Armor')
    rings = []
    for y, w, zb, zt in ((-16.0, .6, -2.4, -1.6), (-15.2, 2.0, -3.6, -1.2), (-13.0, 2.6, -4.2, -1.2),
                         (8.5, 2.6, -4.2, -1.2), (10.0, 1.6, -3.2, -1.2), (10.6, .5, -2.0, -1.4)):
        rings.append([(-w * .7, y, zb), (w * .7, y, zb), (w, y, zb + .7), (w, y, zt), (-w, y, zt), (-w, y, zb + .7)])
    k.sharp_loft(hull, rings, chamfer=.06)
    g = a.part('Command_windows', 'Glass')
    for s in (-1, 1):
        g.box((.04, 4.5, .45), loc=(s * 2.42, -11.5, -2.2), rot=(0, s * .5, 0), bevel=0)
    g.box((2.6, .05, .5), loc=(0, -15.25, -2.5), rot=(-.6, 0, 0), bevel=0)
    a.part('Bridge_band', 'Team').box((5.24, 22.0, .2), loc=(0, -2.8, -1.45), bevel=0)
    P.portholes(a, [(2.62, y, -2.5) for y in range(-7, 8, 2)], (1, 0, 0), r=.18, seg=8)
    P.portholes(a, [(-2.62, y, -2.5) for y in range(-7, 8, 2)], (-1, 0, 0), r=.18, seg=8)
    for (x, y) in ((1.6, -14.4), (-1.6, -14.4)):
        K.floodlight(a, (x, y, -3.5), facing=(0, -1, -.6), pole=.3)
    ant = a.part('Antenna', 'Steel')
    for y in (-10.0, -6.0, 5.0):
        ant.cyl(.04, 1.4, loc=(1.8, y, GZ0 - .6), seg=5, bevel=0)
    # The bomb bay (the def's bomb_bay hit area at the front belly): two doors on hinge pivots, racked bombs.
    for side, s in (('L', 1), ('R', -1)):
        p = a.pivot(f'Part_bay_door_{side}', (s * 1.4, -8.5, GZ0 + .02))
        K.armour_plate(a, a.part(f'Bay_door_{side.lower()}', 'Armor', p), (1.35, 4.2, .1), (-s * .68, 0, -.06),
                       rivet=.4, parent=p)
        a.part('Bay_bands', 'Hazard', p).box((1.3, .14, .02), loc=(-s * .68, -2.05, -.12), bevel=0)
        a.part('Kit_hinges', 'Steel', p).box((.08, 4.0, .08), loc=(0, 0, 0), bevel=0)
        K.tone(a, f'Part_bay_door_{side}', k=.86)
    for j in range(5):
        for s in (-1, 1):
            K.bomb(a, (s * .55, -10.2 + j * .85, GZ0 + .45), .22, .8)
    a.part('Bomb_racks', 'Steel').box((1.6, 4.0, .08), loc=(0, -8.5, GZ0 + .8), bevel=0)
    # The two drone hangars (doors, rails, cradle, a drone each).
    for i, s in enumerate((1, -1)):
        part = K.name('Part_hangar', i)
        p = a.pivot(part, (s * 1.3, 3.0, -2.2))
        tag = '' if i == 0 else '_001'
        k.block(a.part('Hangar' + tag, 'Armor', p), (1.4, 3.6, .1), loc=(0, 0, -1.95), chamfer=.02)
        for d in (-1, 1):
            a.part('Hangar_doors' + tag, 'Armor', p).box((.68, 3.4, .06), loc=(d * .36, 0, -2.06),
                                                         rot=(0, d * .25, 0), bevel=0)
        a.part('Hangar_rail' + tag, 'Steel', p).box((.1, 3.2, .1), loc=(0, 0, -1.7), bevel=0)
        k.block(a.part('Launch_cradle' + tag, 'Steel', p), (.6, .8, .25), loc=(0, -1.0, -1.75), chamfer=.02)
        k.extrude(a.part('Drones' + tag, 'Team', p), [(-.5, -.1), (.5, -.1), (.1, .1), (-.1, .1)], 1.4,
                  loc=(0, -1.0, -1.95), axis='Y', chamfer=.02)
        a.part('Drone_lights' + tag, 'LavaGlow', p).box((.08, .08, .05), loc=(0, -1.7, -1.9), bevel=0)
        a.pivot('Muzzle_door_' + ('l' if i == 0 else 'r'), (0, -1.5, -2.05), part)


def _pods(a):
    """The 105 mm ball pods under the envelopes (`Mount_gun.002` / `.003`) on their struts."""
    for i, s in enumerate((1, -1)):
        x = s * 7.5
        a.part('Pod_struts', 'Steel').tube([(x, -1.6, EZ - EH * .95), (x, -1.6, -2.7)], .25, seg=6)
        k.lathe(a.part('Pod_housings', 'Armor'), [(0, -1.4), (.8, -1.2), (1.0, -.5), (1.0, .4), (.7, .9), (0, 1.0)],
                loc=(x, -1.6, -2.7), seg=12, worn=(2,))
        m = a.pivot(K.name('Mount_gun', 2 + i), (x, -1.6, -3.4))
        tag = '_002' if i == 0 else '_003'
        a.part('Pod_ball' + tag, 'Armor', m).sphere(.75, seg=12, rings=8)
        k.lathe(a.part('Pod_barrel' + tag, 'Steel', m), [(.14, 0), (.12, .2), (.11, 2.2), (.15, 2.3), (.15, 2.6),
                                                         (0, 2.6)], loc=(0, -.7, -.15), rot=(R90 + .17, 0, 0), seg=10)
        a.pivot(K.name('Muzzle_gun', 2 + i), (0, -3.3, -.45), K.name('Mount_gun', 2 + i))


def _engines(a):
    props = ('Propeller', 'Propeller_2', 'Propeller_3', 'Propeller_4')
    for i, (x, y) in enumerate(((14.3, -9.0), (-14.3, -9.0), (14.3, 8.0), (-14.3, 8.0))):
        part = K.name('Part_engine', i)
        p = a.pivot(part, (x, y, 1.0))
        s = 1 if x > 0 else -1
        tag = '' if i == 0 else f'_00{i}'
        a.part('Pylon_engine' + tag, 'Armor', p).limb((0, 0, 0), (-s * 3.4, 0, .2), .6, .9, bevel=.05)
        k.lathe(a.part('Nacelle_engine' + tag, 'Armor', p), [(.0, -3.2), (.75, -3.0), (1.05, -2.2), (1.1, .2),
                                                            (.8, 1.4), (.4, 1.8)], rot=K.FORWARD, seg=12, worn=(2,))
        for yy in (-2.0, -.6):
            a.part('Nacelle_bands_engine' + tag, 'Steel', p).cyl(1.12, .12, loc=(0, yy, 0), rot=(R90, 0, 0), seg=12,
                                                                 bevel=0)
        K.grille(a, (0, -.4, 1.08), 1.0, .8, facing=(0, 0, 1), slats=5, parent=part)
        rv = a.part('Kit_rivets', 'Steel', p)
        for yy in (-2.6, -1.3, 0.0, 1.0):
            for u in (.6, 1.2, 1.9, 2.5):
                rv.box((.08, .08, .05), loc=(math.cos(u) * 1.1, yy, math.sin(u) * 1.1), bevel=0)
        K.exhaust(a, (s * .6, 1.5, .4), r=.15, length=.6, direction=(0, 1, .3), parent=part, muffler=False)
        K.tone(a, part, k=.84)
        pr = a.pivot(props[i], (0, -3.21, 0), part)
        k.lathe(a.part(props[i] + '_hub', 'Steel', pr), [(.35, -.2), (.35, .2), (.2, .4), (0, .5)], rot=K.FORWARD,
                seg=10)
        bl = a.part(props[i] + '_blades', 'Undercarriage', pr)
        for j in range(4):
            u = j * TAU / 4 + .3
            bl.box((.36, .06, 2.1), loc=(math.cos(u) * 1.15, -.05, math.sin(u) * 1.15), rot=(0, -u + R90, 0), bevel=0)
        a.part(props[i] + '_tips', 'Hazard', pr).box((.38, .07, .3), loc=(math.cos(.3) * 2.05, -.05,
                                                                          math.sin(.3) * 2.05),
                                                     rot=(0, -.3 + R90, 0), bevel=0)


def command_airship(a):
    K.suffixed(a)
    _envelopes(a)
    _envelope_skin(a)
    _spine(a)
    _turret(a, 0, -13.2)
    _turret(a, 1, 10.2)
    _radar(a)
    _gondola(a)
    _pods(a)
    _engines(a)
    k.clean(a)


BUILDERS = {'command_airship': (command_airship, dict(ao_distance=1.6, grime_height=.2, ground=False))}
