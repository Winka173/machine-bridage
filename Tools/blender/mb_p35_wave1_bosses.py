"""Prompt 35 wave 1 (lane A): five bosses rebuilt from scratch, each from its own spec (Tools/blender/specs/<id>.json)
on the kit35 library, no hull shared with a sibling. DECISIONS "Prompt 35 wave 1 (lane A)".

- fortress_bastion: Orlov's "toughest fortress". A Sandcrawler-like tracked casemate of thick riveted plate (sloped
  walls narrowing to the deck) on two long track units under armour skirts; the 155 mm bow casemate gun; four
  turrets on the deck corners (twin 100 mm forward, 40 mm Bofors aft); a raised citadel carrying the 2B8-class
  240 mm mortar turret and the twin Kornet launcher; two ZU-23-2 on raised pedestals at the flanks; the repair crane
  and welding gear on the rear deck (it patches itself up once).
- fortress_hive: the drone fortress. A crawler-transporter: a flat girder platform high on four corner trucks of two
  tracks each, with levelling rams, two operator cabs on opposite corners and generator houses; on the deck a vaulted
  drone hangar with bay doors and parked drones, the EMP emitter dome on its roof and the jammer array at its front
  (both weak points the card names), two Lancet launch rails at the rear, the SAM box between them, twin flak at the
  front corners.
- behemoth_inferno, behemoth_tempest, stymphalos: see their sections below.

Runtime nodes are the old models' (boss parts and mountWeapons in balance.json unchanged): see each builder.
Built only from frontier_kit / mb_kit27 primitives and mb_kit35; no other model's builder or mesh.
Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Matrix, Vector

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau


def _key(base, i):
    """The builder's name for the i-th pivot of a series (base, base__001 ...; renamed base.001 after the finish)."""
    return K.name(base, i)


# ============================================================================= fortress_bastion
B_DECK = 4.25           # the casemate deck (turret rings)
B_CIT = 5.5             # the citadel roof


def _bastion_running_gear(a):
    K.tracks(a, 3.75, 15.4, 1.75, .62, 8, 1.1, sprocket_end=1, cleat_pitch=.42, teeth=11, rollers=4)
    for s in (-1, 1):
        K.side_skirt(a, 4.42, -7.5, 7.3, 2.45, 1.35, s, panels=6, t=.14, mat='Armor')
        K.dust(a, (s * 3.75, -7.4, .5), radius=2.4, k=.25)
        K.dust(a, (s * 3.75, 7.2, .5), radius=2.4, k=.25)
        K.dust(a, (s * 3.75, 0, .4), radius=5.0, k=.15)
    # Spare track links hung on the skirts.
    links = a.part('Spare_links', 'Undercarriage')
    for s in (-1, 1):
        for i in range(4):
            links.box((.08, .9, .3), loc=(s * 4.56, -6.4 + i * .95, 1.9), bevel=0)


def _bastion_hull(a):
    """The lower hull between the tracks, the Sandcrawler casemate (lofted: sloped walls, sloped glacis and stern),
    the deck, the citadel, the bow casemate."""
    lower = a.part('Hull', 'Armor')
    K.chamfer_box(lower, (6.3, 15.6, 1.8), loc=(0, -.1, 1.55), c=.12)
    k.extrude(lower, [(-8.1, .75), (-7.3, .75), (-7.3, 2.45), (-8.25, 2.1)], 6.0, loc=(0, 0, 0), axis='X',
              chamfer=.08)
    body = a.part('Body', 'Team')
    rings = []
    for y, hb, ht, zt in ((-7.65, 4.0, 3.0, 3.25), (-6.5, 4.5, 3.55, B_DECK), (6.7, 4.5, 3.55, B_DECK),
                          (7.75, 4.3, 3.3, 3.85)):
        rings.append([(-hb, y, 2.45), (hb, y, 2.45), (ht, y, zt), (-ht, y, zt)])
    body.loft(rings)
    k.inset(body, lambda c, n, f: n.z > .9 and c.z > B_DECK - .05, width=.35, depth=-.03)
    # The citadel on the deck: sloped walls, its roof inset.
    cit = a.part('Citadel', 'Team')
    k.extrude(cit, [(-2.35, -1.5), (2.35, -1.5), (2.35, 3.6), (-2.35, 3.6)], B_CIT - B_DECK + .05,
              loc=(0, 0, (B_CIT + B_DECK) / 2), axis='Z', chamfer=.08, corner=.3, taper=(.82, .9))
    k.inset(cit, lambda c, n, f: n.z > .9 and c.z > B_CIT - .02, width=.25, depth=-.03)
    # The bow casemate for the 155 mm gun.
    bow = a.part('Casemate', 'Armor')
    k.extrude(bow, [(-1.35, 2.45), (1.35, 2.45), (1.1, 4.0), (-1.1, 4.0)], 1.7, loc=(0, -8.0, 0), axis='Y',
              chamfer=.08, corner=.06)


def _bastion_armour(a):
    """Thick riveted appliqué plates on the casemate walls (each its own plate), the general's stripe along the deck
    edge, hazard chevrons on the bow, vision blocks, hatches, ladders, lamps, tow hooks."""
    arm = a.part('Plates', 'Armor')
    for s in (-1, 1):
        for i in range(5):
            y = -5.2 + i * 2.6
            K.armour_plate(a, arm, (.9, 2.3, .12), (s * 4.27, y, 3.0), rot=(0, s * 1.08, 0), rivet=.55)
            K.armour_plate(a, arm, (.7, 2.3, .12), (s * 3.83, y, 3.85), rot=(0, s * 1.08, 0), rivet=.55)
        a.part('Team_band', 'Team').box((.24, 13.0, .05), loc=(s * 3.68, 0, B_DECK - .17), rot=(0, s * 1.08, 0),
                                        bevel=0)
    chev = a.part('Bow_chevrons', 'SafetyStripe')
    for i in range(5):
        chev.box((.55, .05, .18), loc=(-2.4 + i * 1.2, -8.16, 1.4), rot=(0, .6, 0), bevel=0)
    for s in (-1, 1):
        K.armour_plate(a, arm, (2.2, 1.3, .14), (s * 1.9, -7.04, 3.82), rot=(.72, 0, 0), rivet=.45)
        K.periscope(a, (s * 2.4, -6.6, B_DECK + .02), facing=(0, -1, 0), size=(.36, .3, .26))
    for (x, y) in ((1.3, -5.0), (-1.4, 5.4)):
        K.hatch_round(a, (x, y, B_DECK), r=.48, periscopes=2)
    K.hatch_rect(a, (0, 3.2, B_CIT), (1.0, 1.0))
    K.ladder(a.part('Ladders', 'Steel'), (-4.62, 3.0, .9), (-4.0, 3.0, B_DECK), width=.55, step=.38, r=.035)
    K.ladder(a.part('Ladders', 'Steel'), (2.0, 3.65, B_DECK), (2.0, 3.65, B_CIT), width=.5, step=.35, r=.03)
    for s in (-1, 1):
        K.lamp(a, (s * 2.9, -7.75, 3.0), (0, -1, 0), r=.18)
        K.lamp(a, (s * 3.2, 7.78, 3.4), (0, 1, 0), r=.14, glow='LavaGlow', guard=False)
        K.tow_hook(a.part('Hull_steel', 'Steel'), (s * 1.8, -8.25, 1.4), facing=(0, -1, 0), size=.3)


def _bastion_rear(a):
    """The engine deck (grilles, smokestacks), the repair crane and welding gear, fuel drums, a searchlight, a
    beacon, antennas."""
    for s in (-1, 1):
        K.grille(a, (s * 2.2, 6.2, B_DECK + .02), 2.2, 1.6, facing=(0, 0, 1), slats=7)
        K.smokestack(a, (s * 3.0, 7.2, B_DECK), r=.28, h=1.7)
    st = a.part('Crane', 'CraneYellow')
    k.lathe(st, [(.35, 0), (.35, .3), (.22, .4), (.22, 1.4)], loc=(-1.2, 4.8, B_CIT), seg=10, worn=(1,))
    st.limb((-1.2, 4.8, B_CIT + 1.3), (-2.9, 3.6, B_CIT + 2.3), .2, .24, bevel=0)
    steel = a.part('Crane_steel', 'Steel')
    steel.limb((-1.2, 4.8, B_CIT + .6), (-2.1, 4.15, B_CIT + 1.7), .1, .1, bevel=0)
    steel.tube([(-2.9, 3.6, B_CIT + 2.25), (-2.9, 3.6, B_CIT + .9)], .02, seg=4)
    k.block(a.part('Hook_block', 'Hazard'), (.2, .14, .26), loc=(-2.9, 3.6, B_CIT + .8), chamfer=.02)
    for i, mat in enumerate(('Steel', 'BarrelRed', 'Steel')):
        k.lathe(a.part('Gas_bottles', mat), [(.12, 0), (.12, 1.0), (.08, 1.1), (0, 1.14)],
                loc=(-3.3 + i * .3, 5.9, B_DECK), seg=8, worn=(1,))
    k.lathe(a.part('Cable_reel', 'Steel'), [(.45, -.3), (.45, -.26), (.28, -.26), (.28, .26), (.45, .26), (.45, .3)],
            loc=(3.1, 5.2, B_DECK + .45), rot=(0, R90, 0), seg=10)
    for i in range(2):
        K.fuel_drum(a.part('Drums', 'Fuel'), a.part('Drum_bands', 'Steel'), (3.0 - i * .65, 4.0, B_DECK), r=.3,
                    h=.9)
    K.floodlight(a, (2.0, -1.2, B_CIT), facing=(0, -1, -.3), pole=1.1)
    K.beacon(a, (-2.0, -1.1, B_CIT), r=.16)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-2.0, 3.3, B_CIT), h=2.6, r=.05)
    K.whip_antenna(a.part('Antennas', 'Steel'), (2.1, 2.9, B_CIT), h=1.8, r=.045)
    K.soot(a, (3.0, 7.2, B_DECK + 1.7), radius=1.4, k=.4)
    K.soot(a, (-3.0, 7.2, B_DECK + 1.7), radius=1.4, k=.4)


def _bastion_turret(a, index, loc, twin, big):
    """One deck turret on Mount_gun[.NNN] (its own breakable part): a house with sloped front and cheeks, a riveted
    glacis plate, the commander's hatch, a sight, the barrels (twin 100 mm forward, a Bofors 40 mm aft) ending at
    Muzzle_gun[.NNN]."""
    key = _key('Mount_gun', index)
    m = a.pivot(key, loc)
    sc = 1.0 if big else .8
    house = a.part('Gun_house', 'Armor', m)
    k.extrude(house, [(-1.2 * sc, -1.1 * sc), (1.2 * sc, -1.1 * sc), (1.25 * sc, .9 * sc), (.9 * sc, 1.3 * sc),
                      (-.9 * sc, 1.3 * sc), (-1.25 * sc, .9 * sc)], .95 * sc, loc=(0, 0, .5 * sc), axis='Z',
              chamfer=.08, corner=.06, taper=(.82, .86))
    K.turret_ring(a.part('Gun_ring', 'Steel', m), (0, 0, .02), 1.25 * sc, h=.12)
    K.armour_plate(a, a.part('Gun_plates', 'Armor', m), (1.6 * sc, .6 * sc, .1), (0, -1.12 * sc, .5 * sc),
                   rot=(-1.25, 0, 0), rivet=.25, parent=key)
    K.hatch_round(a, (.45 * sc, .45 * sc, .98 * sc), r=.32 * sc, parent=key, periscopes=1)
    K.periscope(a, (-.5 * sc, -.4 * sc, .97 * sc), facing=(0, -1, 0), parent=key, size=(.24, .2, .18))
    mz = .36 * sc
    length = 2.55
    y_tip = -2.73
    if twin:
        for x in (-.3, .3):
            K.gun_barrel(a, 'Gun_barrels', key, x, y_tip + length, mz, length, .07, seg=10,
                         extractor=(.45, 1.5, .35), brake_name=None)
    else:
        K.gun_barrel(a, 'Gun_barrels', key, 0, y_tip + length, mz, length, .055, seg=10, extractor=(.3, 1.6, .3),
                     brake_name=None)
        k.lathe(a.part('Gun_flash', 'Undercarriage', m), [(.09, 0), (.09, .3), (.07, .32), (0, .32)],
                loc=(0, y_tip + .3, mz), rot=K.BACKWARD, seg=8)
    a.pivot(_key('Muzzle_gun', index), (0, y_tip, mz), key)
    return m


def _bastion_weapons(a):
    """The mortar turret on the citadel (Turret: Main_cannon and its breech, buffers and bore), the four deck
    turrets, the bow 155 mm (Mount_gun.004), the Kornet pair (Part_missile / Mount_missile), the ZU-23-2 pair on
    raised pedestals (Mount_mg, Mount_mg.001)."""
    t = a.pivot('Turret', (0, 1.0, 5.54))
    tt = a.part('Turret_armor', 'Armor', t)
    k.lathe(tt, [(1.9, 0), (1.95, .1), (1.95, .3), (1.75, .45), (0, .45)], seg=24, worn=(2, 3))
    K.turret_ring(a.part('Turret_steel', 'Steel', t), (0, 0, -.04), 1.95, h=.12)
    for s in (-1, 1):
        k.extrude(tt, [(-.9, .4), (1.2, .4), (1.0, 1.7), (-.2, 1.9)], .22, loc=(s * .75, 0, 0), axis='X',
                  chamfer=.03, corner=.04)
    # The 240 mm tube raised 62 degrees forward on its trunnions between the side frames.
    m = Matrix.Translation(Vector((0, .3, 1.05))) @ Matrix.Rotation(math.radians(-60), 4, 'X')
    rot = tuple((m @ Matrix.Rotation(R90, 4, 'X')).to_euler('XYZ'))
    L = 3.1
    k.lathe(a.part('Main_cannon', 'Steel', t), [(.31, -.6), (.31, .2), (.27, .3), (.27, L - .25), (.33, L - .2),
                                                (.33, L), (.2, L), (.2, L - .1), (0, L - .1)],
            loc=tuple(m @ Vector((0, 0, 0))), rot=rot, seg=16, worn=(2, 5))
    k.lathe(a.part('Main_cannon_breech', 'Armor', t), [(0, -1.1), (.42, -1.05), (.45, -.6), (.36, -.5)],
            loc=tuple(m @ Vector((0, 0, 0))), rot=rot, seg=14)
    for s in (-1, 1):
        a.part('Main_cannon_buffer', 'Steel', t).limb(tuple(m @ Vector((s * .35, -.3, 0))),
                                                     tuple(m @ Vector((s * .35, -.3, -1.3))), .1, .1, bevel=0)
    k.lathe(a.part('Main_cannon_bore', 'Undercarriage', t), [(.16, 0), (.16, .02), (0, .02)],
            loc=tuple(m @ Vector((0, -L + .11, 0))), rot=rot, seg=12)
    tip = m @ Vector((0, -L, 0))
    a.pivot('Muzzle_main', tuple(tip), 'Turret')
    K.hatch_round(a, (1.1, 1.0, .45), r=.4, parent='Turret', periscopes=1)
    K.soot(a, (0, 1.0 + tip.y, 5.54 + tip.z), radius=1.0, k=.45)
    _bastion_turret(a, 0, (3.2, -6.0, 4.37), twin=True, big=True)
    _bastion_turret(a, 1, (-3.2, -6.0, 4.37), twin=True, big=True)
    _bastion_turret(a, 2, (2.6, 6.25, 4.37), twin=False, big=False)
    _bastion_turret(a, 3, (-2.6, 6.25, 4.37), twin=False, big=False)
    # The bow 155 mm in its ball mantlet (Mount_gun.004).
    key = _key('Mount_gun', 4)
    bm = a.pivot(key, (0, -8.6, 3.2))
    k.lathe(a.part('Bow_mantlet', 'Armor', bm), [(0, -.55), (.62, -.45), (.75, 0), (.62, .4), (0, .5)],
            rot=K.FORWARD, seg=14)
    K.gun_barrel(a, 'Bow_barrel', key, 0, -.5, .1, 5.1, .12, seg=14, extractor=(.4, 1.5, .55), brake_name=None)
    k.lathe(a.part('Bow_brake', 'Undercarriage', bm), [(.12, 0), (.22, .05), (.22, .45), (.12, .5), (0, .5)],
            loc=(0, -5.6, .1), rot=K.BACKWARD, seg=10)
    a.pivot(_key('Muzzle_gun', 4), (0, -5.6, .1), key)
    K.tone(a, 'Mount_gun', k=.9)
    # The Kornet pair on the citadel (Part_missile, its Mount_missile).
    pm = a.pivot('Part_missile', (.85, 3.75, 5.5))
    k.block(a.part('Kornet_base', 'Armor', pm), (.9, .9, .3), loc=(0, 0, .15), chamfer=.04)
    km = a.pivot('Mount_missile', (0, 0, .5), 'Part_missile')
    k.block(a.part('Kornet_cradle', 'Armor', km), (.75, .5, .45), loc=(0, .2, .2), chamfer=.03)
    for x in (-.28, .28):
        k.lathe(a.part('Kornet_tubes', 'Team', km), [(.09, -.9), (.09, .7), (.11, .72), (.11, .8)],
                loc=(x, .05, .55), rot=(R90 + .3, 0, 0), seg=10, caps=(True, False))
    K.periscope(a, (0, .45, .5), facing=(0, -1, 0), parent='Mount_missile', size=(.2, .18, .2))
    a.pivot('Muzzle_missile', (.28, -.75, .8), 'Mount_missile')
    K.tone(a, 'Part_missile', k=.9)
    # The ZU-23-2 pair on raised pedestals over the flanks (the roof-gun rule): column, ring, carriage, magazines.
    for i, s in enumerate((1, -1)):
        x, y = s * 3.9, 1.5
        ped = a.part('Zu_pedestals', 'Steel')
        k.lathe(ped, [(.5, 0), (.5, .08), (.22, .16), (.2, .82), (.34, .88), (.34, .95)], loc=(x, y, B_DECK), seg=12,
                worn=(1, 4))
        key = _key('Mount_mg', i)
        zm = a.pivot(key, (x, y, 5.2))
        zh = a.part('Zu_carriage', 'Armor', zm)
        k.block(zh, (.75, .9, .14), loc=(0, .1, .05), chamfer=.02)
        for sx in (-1, 1):
            k.block(zh, (.1, .6, .42), loc=(sx * .24, 0, .3), chamfer=.015)
            K.gun_barrel(a, 'Zu_barrels', key, sx * .13, .2, .3, 2.45, .045, seg=8, extractor=(.3, 1.6, .25),
                         brake_name=None)
            k.block(a.part('Zu_magazines', 'Armor', zm), (.11, .36, .3), loc=(sx * .37, .05, .38), chamfer=.015)
        mk = _key('Muzzle_mg', i)
        a.pivot(mk, (0, -2.25, .3), key)
        tag = 'mg' if i == 0 else f'mg_{i:03d}'
        for b, sx in enumerate((1, -1)):
            a.pivot(f'Muzzle_b{b + 1}_{tag}', (sx * .13, 0, 0), mk)
        K.chamfer_box(a.part('Zu_seats', 'Canvas', zm), (.3, .25, .08), loc=(s * .5, .55, .3), c=.015)


def fortress_bastion(a):
    """Fortress Bastion: see the module docstring."""
    K.suffixed(a)
    _bastion_running_gear(a)
    _bastion_hull(a)
    _bastion_armour(a)
    _bastion_rear(a)
    _bastion_weapons(a)
    k.clean(a)


# ============================================================================= fortress_hive
H_DECK = 4.2
TRUCKS = ((3.3, -5.1), (-3.3, -5.1), (3.3, 4.8), (-3.3, 4.8))


def _hive_track(a, cx, cy, length=3.6, height=1.3, width=.85):
    """One crawler tread (the hive's own): a stadium belt with steel shoes, road wheels behind its faces."""
    belt = a.part('Tracks', 'Undercarriage')
    r = height / 2
    prof = []
    for e in (1, -1):
        for j in range(7):
            u = -R90 + j * math.pi / 6
            prof.append((e * (length / 2 - r + math.cos(u) * r), r + e * math.sin(u) * r))
    k.extrude(belt, prof, width, loc=(cx, cy, 0), axis='X', chamfer=.02)
    shoes = a.part('Track_shoes', 'Steel')
    path = [(cx, cy + y, z) for y, z in prof] + [(cx, cy + prof[0][0], prof[0][1])]
    for p, t in k.along(path, pitch=.38):
        shoes.box((width + .06, .12, .06), loc=(p.x, p.y, p.z), rot=(math.atan2(t.z, t.y), 0, 0), bevel=0)
    discs = a.part('Wheels', 'Team')
    hubs = a.part('Hubs', 'Steel')
    for s in (-1, 1):
        for j in range(4):
            y = cy - length / 2 + r + j * (length - 2 * r) / 3
            x = cx + s * (width / 2 + .03)
            k.lathe(discs, [(0, -.05), (r * .62, -.05), (r * .62, .05), (r * .3, .07)], loc=(x, y, r),
                    rot=(0, s * R90, 0), seg=10, caps=(True, False))
            hubs.cyl(r * .2, .08, loc=(x + s * .05, y, r), rot=(0, R90, 0), seg=6, bevel=0)


def _hive_trucks(a):
    """Four corner trucks: two treads each, the truck frame with its gear case, the levelling rams and guide tubes
    up to the platform, mud on the treads."""
    frame = a.part('Truck_frames', 'Armor')
    steel = a.part('Truck_steel', 'Steel')
    for cx, cy in TRUCKS:
        for dx in (-.62, .62):
            _hive_track(a, cx + dx, cy)
        K.chamfer_box(frame, (2.5, 3.0, .7), loc=(cx, cy, 1.65), c=.08)
        for dy in (-1.0, 1.0):
            k.lathe(steel, [(.32, 0), (.32, .5), (.24, .55), (.24, 1.45)], loc=(cx + .55, cy + dy, 2.0), seg=10,
                    worn=(1,))
            k.lathe(steel, [(.2, 0), (.2, 1.4)], loc=(cx - .55, cy + dy, 2.0), seg=8)
        K.chamfer_box(a.part('Gear_cases', 'Team'), (.6, .8, .6),
                      loc=(cx + (1.0 if cx > 0 else -1.0), cy + 1.1, 1.5), c=.05)
        K.dust(a, (cx, cy, .4), radius=2.8, k=.28)


def _hive_platform(a):
    """The girder platform: the deck slab with its tread inset, side girders with diagonal braces, railings, two
    operator cabs on opposite corners, generator houses with stacks, ladders."""
    deck = a.part('Deck', 'Team')
    K.chamfer_box(deck, (9.1, 14.2, .5), loc=(0, -.15, H_DECK - .25), c=.08)
    k.inset(deck, lambda c, n, f: n.z > .9 and c.z > H_DECK - .03, width=.3, depth=-.025)
    gird = a.part('Girders', 'Armor')
    for s in (-1, 1):
        K.chamfer_box(gird, (.35, 14.2, .65), loc=(s * 4.38, -.15, 3.38), c=.04)
        for i in range(8):
            y = -7.1 + i * 1.7
            gird.limb((s * 4.38, y, 3.05), (s * 4.38, y + .85, 3.7), .12, .12, bevel=0)
            gird.limb((s * 4.38, y + .85, 3.7), (s * 4.38, y + 1.7, 3.05), .12, .12, bevel=0)
    for y in (-7.05, 6.75):
        K.chamfer_box(gird, (9.0, .4, .65), loc=(0, y, 3.38), c=.04)
    K.railing(a.part('Railings', 'Steel'), [(-4.45, -7.15, H_DECK), (4.45, -7.15, H_DECK), (4.45, 6.85, H_DECK),
                                            (-4.45, 6.85, H_DECK), (-4.45, -7.15, H_DECK)], h=1.0, post=1.6, r=.035)
    a.part('Deck_hazard', 'SafetyStripe').box((8.8, .06, .25), loc=(0, -7.26, H_DECK - .15), bevel=0)
    # Operator cabs at the front-left and rear-right corners, hung off the girders.
    for (x, y, face) in ((3.9, -7.15, -1), (-3.9, 6.85, 1)):
        cab = a.part('Cab', 'Team')
        K.chamfer_box(cab, (1.6, 1.4, 1.5), loc=(x, y + face * .7, 2.75), c=.08)
        a.part('Windows', 'Glass').box((1.4, .04, .6), loc=(x, y + face * 1.41, 3.05), bevel=0)
        a.part('Windows', 'Glass').box((.04, 1.0, .6), loc=(x + (.81 if x > 0 else -.81), y + face * .7, 3.05),
                                       bevel=0)
        K.lamp(a, (x, y + face * 1.42, 2.3), (0, face, 0), r=.13)
    # Generator houses along both sides of the deck, their stacks and louvres.
    for s in (-1, 1):
        gh = a.part('Generator_houses', 'Armor')
        K.chamfer_box(gh, (1.3, 5.0, 1.3), loc=(s * 3.55, 2.3, H_DECK + .65), c=.08)
        K.grille(a, (s * 4.21, 2.3, H_DECK + .7), 3.6, .7, facing=(s, 0, 0), slats=8)
        K.smokestack(a, (s * 3.4, 4.3, H_DECK + 1.3), r=.2, h=1.2)
        K.ladder(a.part('Ladders', 'Steel'), (s * 4.6, -2.0 + s * 1.0, .2), (s * 4.6, -2.0 + s * 1.0, H_DECK),
                 width=.5, step=.38, r=.03)
    K.dust(a, (0, 0, .2), radius=9.0, k=.12)


def _hive_hangar(a):
    """The vaulted drone hangar on the deck: the arched roof with its ribs, three bay openings a side with sills and
    parked Lancet-class drones, the end walls; the EMP emitter dome on the roof (weak point: glowing dome, coils,
    hazard ring) and the jammer array at the hangar's front (weak point)."""
    y0, y1 = -4.5, 2.9
    hw = 2.5
    hb = a.part('Body_hangar', 'Team')
    prof = [(-hw, H_DECK), (hw, H_DECK)] + [(math.cos(j * math.pi / 8) * hw, H_DECK + 1.0 +
                                             math.sin(j * math.pi / 8) * 1.45) for j in range(9)]
    k.extrude(hb, prof, y1 - y0, loc=(0, (y0 + y1) / 2, 0), axis='Y', chamfer=.06)
    ribs = a.part('Hangar_ribs', 'Armor')
    for i in range(6):
        y = y0 + .3 + i * (y1 - y0 - .6) / 5
        pts = [(math.cos(j * math.pi / 8) * (hw + .06), y, H_DECK + 1.0 + math.sin(j * math.pi / 8) * 1.51)
               for j in range(9)]
        ribs.tube([(hw + .06, y, H_DECK)] + pts + [(-hw - .06, y, H_DECK)], .07, seg=4)
    dark = a.part('Bay_openings', 'Undercarriage')
    sills = a.part('Bay_sills', 'Hazard')
    drones = a.part('Drone_airframe', 'Armor')
    wings = a.part('Drone_wings', 'Steel')
    for s in (-1, 1):
        for i in range(3):
            y = y0 + 1.25 + i * 2.45
            dark.box((.05, 1.9, 1.15), loc=(s * (hw + .01), y, H_DECK + .7), bevel=0)
            sills.box((.25, 2.1, .1), loc=(s * (hw + .1), y, H_DECK + .1), bevel=0)
            k.lathe(drones, [(0, -.6), (.1, -.5), (.12, -.2), (.12, .45), (.08, .6), (0, .62)],
                    loc=(s * (hw - .35), y, H_DECK + .55), rot=K.FORWARD, seg=8)
            for yy, span in ((-.2, .45), (.4, .35)):
                for ang in (.78, -.78):
                    wings.box((span * 2, .1, .015), loc=(s * (hw - .35), y + yy, H_DECK + .55),
                              rot=(0, ang, 0), bevel=0)
    for y in (y0 - .02, y1 + .02):
        a.part('Hangar_walls', 'Armor').box((hw * 2 - .1, .06, 1.0), loc=(0, y, H_DECK + .5), bevel=0)
    K.door(a, (0, y0 - .06, H_DECK), (1.2, 1.9), normal=(0, -1, 0), mat='Armor')
    emp = (0, 1.0, H_DECK + 2.42)
    k.lathe(a.part('Emp_drum', 'Armor'), [(1.0, 0), (1.0, .3), (.85, .4), (0, .4)], loc=emp, seg=18)
    k.lathe(a.part('Emp_dome', 'Alloy'), [(.8, 0), (.75, .35), (.55, .65), (.25, .82), (0, .86)],
            loc=(emp[0], emp[1], emp[2] + .4), seg=18)
    coils = a.part('Emp_coils', 'Steel')
    for j in range(3):
        coils.torus(.82 - j * .12, .04, loc=(emp[0], emp[1], emp[2] + .45 + j * .2), seg=18, ring=4)
    a.part('Emp_hazard', 'SafetyStripe').cyl(1.02, .08, loc=(emp[0], emp[1], emp[2] + .25), seg=18, bevel=0)
    jx, jy = 0, -3.0
    k.block(a.part('Jammer_box', 'Armor'), (1.0, .7, .6), loc=(jx, jy, H_DECK + 2.52), chamfer=.04)
    a.part('Jammer_mast', 'Steel').cyl(.07, 1.5, loc=(jx, jy, H_DECK + 3.1), seg=8, bevel=0)
    for j in range(3):
        u = j * TAU / 3
        K.mesh_antenna(a.part('Jammer_panels', 'Steel'), (jx + math.sin(u) * .35, jy - math.cos(u) * .35,
                                                          H_DECK + 3.55), w=.5, h=.55,
                       normal=(math.sin(u), -math.cos(u), 0), bars=4)
    for dx in (-.4, .4):
        K.whip_antenna(a.part('Antennas', 'Steel'), (jx + dx, jy + .2, H_DECK + 2.8), h=1.2, r=.03)
    K.beacon(a, (1.4, 1.0, H_DECK + 2.35), r=.12)


def _hive_weapons(a):
    """Two Lancet launch rails at the rear (Mount_missile, .001), the SAM box (Mount_rocket) between them, twin flak
    at the front corners (Mount_mg, .001)."""
    for i, s in enumerate((1, -1)):
        key = _key('Mount_missile', i)
        m = a.pivot(key, (s * 1.85, 5.8, 4.3))
        K.chamfer_box(a.part('Rack_base', 'Armor', m), (1.3, 1.4, .4), loc=(0, .2, .2), c=.05)
        rot = (.62, 0, 0)
        mm = Matrix.Translation(Vector((0, -.1, .95))) @ Matrix.Rotation(.62, 4, 'X')
        rails = a.part('Rack_rails', 'Steel', m)
        for x in (-.32, .32):
            rails.box((.08, 2.6, .1), loc=tuple(mm @ Vector((x, 0, 0))), rot=rot, bevel=0)
        k.block(a.part('Rack_ramp', 'Team', m), (.9, 2.5, .08), loc=tuple(mm @ Vector((0, 0, -.1))), rot=rot,
                chamfer=0)
        rails.limb((0, .6, .4), tuple(mm @ Vector((0, .6, -.15))), .1, .1, bevel=0)
        for yy in (-.65, .55):
            c = mm @ Vector((0, yy, .18))
            k.lathe(a.part('Rack_drones', 'Armor', m), [(0, -.55), (.1, -.45), (.11, -.15), (.11, .45), (.07, .55),
                                                        (0, .57)], loc=tuple(c), rot=(rot[0] + R90, 0, 0), seg=8)
            for dyy, span in ((-.18, .42), (.38, .32)):
                for ang in (.78, -.78):
                    a.part('Rack_wings', 'Steel', m).box((span * 2, .09, .015),
                                                         loc=tuple(mm @ Vector((0, yy + dyy, .18))),
                                                         rot=(rot[0], ang, 0), bevel=0)
        a.part('Rack_stripe', 'SafetyStripe', m).box((.95, .06, .1), loc=tuple(mm @ Vector((0, -1.25, 0))), rot=rot,
                                                     bevel=0)
        a.pivot(_key('Muzzle_missile', i), (0, -1.05, 1.65), key)
    K.tone(a, 'Mount_missile', k=.9)
    a.part('Sam_pedestal', 'Steel').cyl(.35, 1.3, loc=(0, 3.6, H_DECK + .65), seg=12, bevel=0)
    sm = a.pivot('Mount_rocket', (0, 3.6, 5.5))
    k.lathe(a.part('Sam_base', 'Armor', sm), [(.75, 0), (.75, .15), (.6, .25), (0, .25)], seg=16)
    mm = Matrix.Translation(Vector((0, .2, .85))) @ Matrix.Rotation(.75, 4, 'X')
    rot = tuple(mm.to_euler('XYZ'))
    k.block(a.part('Sam_box', 'Team', sm), (1.25, 2.2, 1.0), loc=tuple(mm @ Vector((0, 0, 0))), rot=rot, chamfer=.05)
    caps = a.part('Sam_caps', 'Canvas', sm)
    for x in (-.3, .3):
        for z in (-.24, .24):
            caps.cyl(.24, .03, loc=tuple(mm @ Vector((x, -1.11, z))), rot=(rot[0] + R90, 0, 0), seg=10, bevel=0)
    for s in (-1, 1):
        k.block(a.part('Sam_yoke', 'Armor', sm), (.15, .6, .9), loc=(s * .7, .2, .55), chamfer=.03)
    a.pivot('Muzzle_rocket', (0, -.64, 1.4), 'Mount_rocket')
    K.tone(a, 'Mount_rocket', k=.92)
    for i, s in enumerate((1, -1)):
        key = _key('Mount_mg', i)
        m = a.pivot(key, (s * 3.2, -6.0, 4.37))
        K.turret_ring(a.part('Flak_ring', 'Steel', m), (0, 0, 0), .8, h=.1)
        k.extrude(a.part('Flak_house', 'Armor', m), [(-.75, -.7), (.75, -.7), (.8, .6), (.5, .85), (-.5, .85),
                                                      (-.8, .6)], .75, loc=(0, 0, .45), axis='Z', chamfer=.05,
                  corner=.05, taper=(.86, .9))
        for x in (-.55, .55):
            K.gun_barrel(a, 'Flak_barrels', key, x, -.4, .3, 1.65, .045, seg=8, extractor=(.4, 1.5, .25),
                         brake_name=None)
            k.block(a.part('Flak_drums', 'Armor', m), (.25, .6, .45), loc=(x, .0, .35), chamfer=.03)
        a.pivot(_key('Muzzle_mg', i), (0, -2.07, .3), key)
        K.dish(a.part('Flak_radar', 'Steel', m), a.part('Flak_radar_feed', 'Steel', m), (0, .5, 1.05), r=.32,
               normal=(0, -1, .2), seg=10)
    K.tone(a, 'Mount_mg', k=.9)


def fortress_hive(a):
    """Fortress Hive: see the module docstring."""
    K.suffixed(a)
    _hive_trucks(a)
    _hive_platform(a)
    _hive_hangar(a)
    _hive_weapons(a)
    k.clean(a)


BUILDERS = {
    'fortress_bastion': (fortress_bastion, dict(ao_distance=1.0, grime_height=1.5)),
    'fortress_hive': (fortress_hive, dict(ao_distance=1.0, grime_height=1.5)),
}
