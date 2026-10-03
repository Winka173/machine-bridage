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



# ============================================================================= behemoth_inferno
# Hegemon flame tank on an Object 279 frame: an elliptical cast hull shell over four narrow tracks, a squat cast
# turret with twin flame projectors (jackets, fuel hoses, nozzles with pilot flames), a TOS-1A-style thermobaric
# rocket box on the glacis, a flak gun on the turret roof, the red fuel tanks strapped on the rear deck (its weak
# point, the card's "fuel" part). Runtime nodes: Turret with Main_cannon / Main_cannon_2 and their _hose, _jacket,
# Muzzle_brake[_2] with _glow, _pilot (parts flamer_r / flamer_l), Muzzle_main, Mount_rocket / Muzzle_rocket
# (thermo), Mount_mg / Muzzle_mg on the turret (flak), Fuel_tanks / Tank_straps / Tank_hazard (fuel).
I_TURRET = (0.0, 0.4, 3.57)


def _inferno_shell_ring(y, W, H):
    fz = (0, .25, .52, .78, 1.0)
    xs = (1.0, .98, .85, .6, .25)
    left = [(-W * x, y, 1.0 + (H - 1.0) * f) for x, f in zip(xs, fz)]
    right = [(W * x, y, 1.0 + (H - 1.0) * f) for x, f in reversed(list(zip(xs, fz)))]
    return left + right


def _inferno_hull(a):
    K.tracks(a, 1.25, 10.6, .95, .3, 6, .62, sprocket_end=1, cleat_pitch=.3, teeth=9, rollers=2)
    K.tracks(a, 2.5, 10.6, .95, .3, 6, .62, sprocket_end=1, cleat_pitch=.3, teeth=9, rollers=2)
    for s in (-1, 1):
        K.dust(a, (s * 1.9, -5.2, .4), radius=2.0, k=.28)
        K.dust(a, (s * 1.9, 5.0, .4), radius=2.0, k=.28)
    shell = a.part('Hull', 'Team')
    rings = []
    for y, W, H in ((-6.4, .9, 1.25), (-6.0, 2.0, 1.75), (-5.0, 2.85, 2.2), (-3.2, 3.2, 2.5), (-.8, 3.25, 2.75),
                    (1.8, 3.25, 2.75), (4.0, 3.15, 2.55), (5.4, 2.8, 2.25), (6.1, 2.1, 1.9)):
        rings.append(_inferno_shell_ring(y, W, H))
    shell.loft(rings)
    # The belly between the track pairs, the flange's lower lip.
    k.block(a.part('Belly', 'Undercarriage'), (1.4, 10.0, .5), loc=(0, -.1, .7), chamfer=.04)
    lip = a.part('Flange_lip', 'Armor')
    for s in (-1, 1):
        lip.tube([(s * 2.0, -6.0, 1.03), (s * 2.85, -5.0, 1.01), (s * 3.25, -.8, 1.01), (s * 3.25, 1.8, 1.01),
                  (s * 3.15, 4.0, 1.01), (s * 2.8, 5.4, 1.03), (s * 2.1, 6.1, 1.05)], .07, seg=4)
    # Glacis hazard chevrons, the general's stripe on the shell's shoulders, the turret ring collar.
    chev = a.part('Glacis_chevrons', 'SafetyStripe')
    for i in range(4):
        chev.box((.5, .05, .16), loc=(-1.2 + i * .8, -6.08, 1.55), rot=(-.5, .6, 0), bevel=0)
    for s in (-1, 1):
        a.part('Team_band', 'Team').box((.05, 6.0, .18), loc=(s * 2.55, .5, 2.35), rot=(0, s * .9, 0), bevel=0)
    K.turret_ring(a.part('Ring', 'Steel'), (I_TURRET[0], I_TURRET[1], 2.72), 1.75, h=.14)
    # Stiffener ribs over the shell (the cast shell's joints), following its section.
    ribs = a.part('Shell_ribs', 'Armor')
    for y, W, H in ((-4.2, 3.05, 2.38), (-2.0, 3.24, 2.62), (3.0, 3.22, 2.68), (4.8, 3.0, 2.42)):
        ribs.tube([(px * 1.012, py, pz + .015) for px, py, pz in _inferno_shell_ring(y, W, H)], .05, seg=4)
    # Shoulder stowage: bins on the rear shoulders (the right one longer), grab rails, a jerrycan rack on the
    # left, vision blocks forward, a tow cable along the right flank.
    bins = a.part('Stowage', 'Crate')
    straps = a.part('Kit_straps', 'Steel')
    K.crate(bins, straps, (.7, 1.6, .45), (2.35, 2.6, 1.9), rot=(0, .55, 0), bands=2)
    K.crate(bins, straps, (.7, 1.0, .45), (-2.35, 2.9, 1.9), rot=(0, -.55, 0), bands=1)
    for i in range(3):
        K.jerrycan(a.part('Jerrycans', 'Fuel'), (-2.55, 1.1 + i * .45, 1.75), rot=(0, -.55, R90), scale=1.4)
    rails = a.part('Grab_rails', 'Steel')
    for s in (-1, 1):
        for y in (-3.2, -1.6, .8):
            K.handle(rails, (s * 2.3, y - .3, 2.25), (s * 2.3, y + .3, 2.25), (s * .6, 0, .8), h=.08, r=.02)
        K.periscope(a, (s * 1.5, -4.9, 2.18), facing=(0, -1, 0), size=(.26, .2, .18))
    K.tow_cable(a.part('Kit_cables', 'Steel'), [(-2.95, -4.6, 1.45), (-3.15, -1.0, 1.45), (-3.1, 3.4, 1.45)], r=.05)


def _inferno_turret(a):
    t = a.pivot('Turret', I_TURRET)
    body = a.part('Turret_body', 'Team', t)
    k.lathe(body, [(1.7, -.85), (1.8, -.7), (1.78, -.35), (1.5, 0), (1.05, .25), (0, .32)], loc=(0, 0, .55),
            seg=24, worn=(1, 2))
    k.extrude(a.part('Turret_armor', 'Armor', t), [(-1.0, .9), (1.0, .9), (.8, 2.15), (-.8, 2.15)], .75,
              loc=(0, 0, .1), axis='Z', chamfer=.06, corner=.1)                                # the bustle
    # The twin projectors: a jacketed tube each side of the mantlet, a fuel hose along its top, the nozzle, the
    # glowing ring and the pilot flame tube under it.
    k.block(a.part('Mantlet', 'Armor', t), (2.0, .7, .8), loc=(0, -1.55, .4), chamfer=.08)
    y0, y1, z = -1.8, -5.85, .5
    for x, n in ((.6, ''), (-.6, '_2')):
        k.lathe(a.part(f'Main_cannon{n}', 'Steel', t), [(.13, 0), (.13, y0 - y1 - .35), (.1, y0 - y1 - .3),
                                                        (.1, y0 - y1)], loc=(x, y1, z), rot=K.BACKWARD, seg=12,
                worn=(1,))
        k.lathe(a.part(f'Main_cannon{n}_jacket', 'Armor', t), [(.22, 0), (.24, .05), (.24, 1.5), (.2, 1.6), (.13, 1.65)],
                loc=(x, y0 - 1.65, z), rot=K.FORWARD, seg=12, worn=(2,))
        a.part(f'Main_cannon{n}_hose', 'Rubber', t).tube([(x, y0 + .4, z + .3), (x, y0 - .2, z + .25),
                                                           (x, y1 + 1.2, z + .2)], .05, seg=5)
        k.lathe(a.part(f'Muzzle_brake{n}', 'Charred', t), [(.1, 0), (.17, .08), (.2, .3), (.15, .38), (.08, .4)],
                loc=(x, y1, z), rot=K.FORWARD, seg=12)
        a.part(f'Muzzle_brake{n}_glow', 'LavaGlow', t).cyl(.09, .02, loc=(x, y1 - .41, z), rot=K.FORWARD, seg=10,
                                                            bevel=0)
        pilot = a.part(f'Muzzle_brake{n}_pilot', 'Steel', t)
        pilot.tube([(x, y1 + .9, z - .2), (x, y1 - .1, z - .2)], .025, seg=4)
        a.part(f'Muzzle_brake{n}_glow', 'LavaGlow', t).cyl(.04, .05, loc=(x, y1 - .14, z - .2), rot=K.FORWARD,
                                                            seg=6, bevel=0)
        for f in (.3, .6):
            a.part('Heat_shields', 'Steel', t).box((.36, .5, .03), loc=(x, y1 + (y0 - y1) * f, z + .2), bevel=0)
    a.pivot('Muzzle_main', (0, -5.99, .55), 'Turret')
    K.soot(a, (0, I_TURRET[1] - 5.9, I_TURRET[2] + .5), radius=1.6, k=.5)
    # Roof: the commander's cupola, the gunner's hatch, periscopes, smoke dischargers, the flak gun on its ring.
    K.hatch_round(a, (.75, .35, .82), r=.38, parent='Turret', periscopes=3)
    K.periscope(a, (-.2, -.9, .82), facing=(0, -1, 0), parent='Turret', size=(.26, .2, .2))
    for s in (-1, 1):
        K.smoke_dischargers(a, 1.55, -.3, .5, s, count=3, parent='Turret')
    fm = a.pivot('Mount_mg', (-.9, .75, 1.03), 'Turret')
    K.turret_ring(a.part('Flak_ring', 'Steel', fm), (0, 0, -.05), .42, h=.08)
    k.block(a.part('Flak_house', 'Armor', fm), (.7, .75, .4), loc=(0, .05, .2), chamfer=.04)
    for x in (-.2, .2):
        K.gun_barrel(a, 'Flak_barrels', 'Mount_mg', x, -.3, .42, 1.25, .04, seg=8, extractor=(.4, 1.5, .2),
                     brake_name=None)
    a.pivot('Muzzle_mg', (0, -1.6, .42), 'Mount_mg')
    K.whip_antenna(a.part('Antennas', 'Steel', t), (-1.2, 1.6, .65), h=1.4, r=.035)


def _inferno_glacis(a):
    """The thermobaric rocket box on the glacis (Mount_rocket): a pedestal, the 4 x 6 tube box raised 20 degrees."""
    a.part('Rocket_pedestal', 'Steel').cyl(.35, .35, loc=(0, -3.45, 2.45), seg=10, bevel=0)
    m = a.pivot('Mount_rocket', (0, -3.45, 2.63))
    mm = Matrix.Translation(Vector((0, -.15, .45))) @ Matrix.Rotation(math.radians(-20), 4, 'X')
    rot = tuple(mm.to_euler('XYZ'))
    k.block(a.part('Rocket_box', 'Team', m), (1.7, 1.4, .8), loc=tuple(mm @ Vector((0, 0, 0))), rot=rot,
            chamfer=.05)
    mouths = a.part('Rocket_mouths', 'Undercarriage', m)
    rims = a.part('Rocket_rims', 'Steel', m)
    fm = mm @ Matrix.Rotation(R90, 4, 'X')
    frot = tuple(fm.to_euler('XYZ'))
    for i in range(6):
        for j in range(4):
            c = mm @ Vector(((i - 2.5) * .26, -.71, (j - 1.5) * .18))
            rims.cyl(.085, .03, loc=tuple(c), rot=frot, seg=6, bevel=0)
            mouths.cyl(.065, .035, loc=tuple(c), rot=frot, seg=6, bevel=0)
    a.pivot('Muzzle_rocket', (0, -1.03, .83), 'Mount_rocket')
    K.tone(a, 'Mount_rocket', k=.9)


def _inferno_rear(a):
    """The red fuel tanks (the fuel part: Fuel_tanks, Tank_straps, Tank_hazard), their feed lines to the turret,
    exhausts with soot, grilles, lamps, extinguishers, spare links."""
    tanks = a.part('Fuel_tanks', 'BarrelRed')
    straps = a.part('Tank_straps', 'Steel')
    haz = a.part('Tank_hazard', 'SafetyStripe')
    for y in (4.1, 5.0):
        k.lathe(tanks, [(0, -1.3), (.32, -1.28), (.42, -1.15), (.44, -.9), (.44, .9), (.42, 1.15), (.32, 1.28),
                        (0, 1.3)], loc=(0, y, 2.85), rot=(0, R90, 0), seg=14, worn=(3, 4))
        for x in (-.7, .7):
            straps.torus(.455, .03, loc=(x, y, 2.85), rot=(0, R90, 0), seg=14, ring=3)
        haz.box((.4, .04, .4), loc=(0, y - .44, 2.85), rot=(0, .78, 0), bevel=0)
    for y in (4.1, 5.0):
        for x in (-1.0, 1.0):
            straps.box((.12, .2, .45), loc=(x, y, 2.4), bevel=0)                                # cradles
    hose = a.part('Hoses', 'Rubber')
    for x in (-.3, .3):
        hose.tube([(x, 3.75, 2.9), (x * 1.5, 3.0, 2.95), (x * 2, 2.3, 3.0)], .07, seg=6)
    for s in (-1, 1):
        K.exhaust(a, (s * 2.1, 5.3, 2.05), r=.12, length=.7, direction=(0, .4, 1), muffler=True)
        K.grille(a, (s * 1.6, 3.0, 2.68), 1.2, .9, facing=(0, 0, 1), slats=5)
        K.lamp(a, (s * 1.8, -5.9, 1.9), (0, -1, 0), r=.13)
        K.lamp(a, (s * 1.6, 6.05, 2.0), (0, 1, 0), r=.1, glow='LavaGlow', guard=False)
        k.lathe(a.part('Extinguishers', 'BarrelRed'), [(.1, 0), (.1, .6), (.06, .66), (0, .7)],
                loc=(s * 2.35, 2.6, 2.32), rot=(s * .55, 0, 0), seg=8, worn=(1,))
    links = a.part('Spare_links', 'Undercarriage')
    for i in range(3):
        links.box((.5, .2, .06), loc=(-1.3 + i * .55, -4.6, 2.32), rot=(-.35, 0, 0), bevel=0)
    K.hatch_round(a, (1.2, -4.1, 2.25), r=.36, periscopes=1)
    K.soot(a, (2.1, 5.6, 2.8), radius=1.0, k=.4)
    K.soot(a, (-2.1, 5.6, 2.8), radius=1.0, k=.4)


def behemoth_inferno(a):
    """Behemoth Inferno: see the section notes."""
    K.suffixed(a)
    _inferno_hull(a)
    _inferno_turret(a)
    _inferno_glacis(a)
    _inferno_rear(a)
    k.clean(a)


# ============================================================================= behemoth_tempest
# Hegemon railgun tank, its own hull (not the inferno's shell): a tall slab-sided superheavy on two broad tracks
# under rhomboid guards, a low front deck carrying two coilgun mounts (Mount_gun, .001), the superstructure with an
# angular turret and its long twin-rail EMRG barrel (Main_cannon*, coils glowing before it fires), the interceptor
# laser on the turret roof (Aps_faces / Aps_tubes / Aps_tubes_bore, Mount_APS), the shield emitter turning on its
# mast (Radar), capacitor banks and cooling fins on the rear deck.
T_TURRET = (0.0, 0.4, 3.57)
T_FRONT = 2.5       # the front deck
T_DECK = 3.1        # the superstructure's deck


def _tempest_hull(a):
    K.tracks(a, 2.45, 12.0, 1.6, .42, 7, 1.0, sprocket_end=-1, cleat_pitch=.36, teeth=11, rollers=3)
    for s in (-1, 1):
        K.dust(a, (s * 2.45, -5.8, .5), radius=2.2, k=.28)
        K.dust(a, (s * 2.45, 5.7, .5), radius=2.2, k=.28)
    hull = a.part('Hull', 'Team')
    k.extrude(hull, [(-6.25, .6), (6.0, .6), (6.15, 2.2), (5.4, T_DECK), (-2.4, T_DECK), (-2.4, T_FRONT),
                     (-5.0, T_FRONT), (-6.3, 1.25)], 3.8, loc=(0, 0, 0), axis='X', chamfer=.1, corner=.06)
    k.inset(hull, lambda c, n, f: n.z > .9 and c.z > T_DECK - .05, width=.3, depth=-.03)
    # Rhomboid track guards: a tall plate over each track with raked ends, its top cover, the bolt rows.
    for s in (-1, 1):
        k.extrude(a.part('Skirts', 'Team'), [(-6.1, .75), (5.95, .75), (6.2, 1.5), (5.6, 2.25), (-5.6, 2.25),
                                             (-6.35, 1.4)], .22, loc=(s * 3.03, 0, 0), axis='X', chamfer=.04,
                  corner=.05)
        k.block(a.part('Guard_tops', 'Armor'), (1.3, 11.2, .14), loc=(s * 2.45, 0, 2.3), chamfer=.03)
        K.rivet_line(a.part('Kit_rivets', 'Steel'), (s * 3.15, -5.4, 2.05), (s * 3.15, 5.4, 2.05), (s, 0, 0),
                     pitch=.6, r=.04, h=.04, seg=4)
        K.rivet_line(a.part('Kit_rivets', 'Steel'), (s * 3.15, -5.6, 1.0), (s * 3.15, 5.6, 1.0), (s, 0, 0),
                     pitch=.6, r=.04, h=.04, seg=4)
        a.part('Team_band', 'Armor').box((.04, 10.4, .18), loc=(s * 3.15, 0, 1.6), bevel=0)
    chev = a.part('Glacis_chevrons', 'SafetyStripe')
    for i in range(4):
        chev.box((.5, .05, .16), loc=(-1.2 + i * .8, -5.7, 1.9), rot=(-.9, .6, 0), bevel=0)
    for s in (-1, 1):
        K.lamp(a, (s * 1.4, -6.05, 1.7), (0, -1, 0), r=.13)
        K.lamp(a, (s * 1.3, 6.1, 2.0), (0, 1, 0), r=.1, glow='LavaGlow', guard=False)
        K.tow_hook(a.part('Hull_steel', 'Steel'), (s * 1.0, -6.3, 1.1), facing=(0, -1, 0), size=.22)
        K.periscope(a, (s * 1.2, -2.6, T_FRONT + .02), facing=(0, -1, 0), size=(.26, .22, .2))
    K.hatch_round(a, (-1.2, -1.2, T_DECK), r=.38, periscopes=2)
    K.turret_ring(a.part('Ring', 'Steel'), (T_TURRET[0], T_TURRET[1], T_DECK), 1.65, h=.14)


def _tempest_rear(a):
    """Capacitor banks (cylinders with glowing bands), the cooling fins along the superstructure, cable runs to the
    turret, generator stacks, the shield emitter mast with the Radar pivot."""
    caps = a.part('Capacitors', 'Armor')
    bands = a.part('Capacitor_bands', 'Energy')
    for row, y in enumerate((3.4, 4.3)):
        for i in range(4):
            x = -1.35 + i * .9
            k.lathe(caps, [(.32, 0), (.32, .7), (.26, .78), (.1, .82), (0, .82)], loc=(x, y + (.2 if x > 0 else 0), T_DECK),
                    seg=10, worn=(1,))
            bands.cyl(.33, .06, loc=(x, y + (.2 if x > 0 else 0), T_DECK + .45), seg=10, bevel=0)
    fins = a.part('Cooling_fins', 'Steel')
    for s in (-1, 1):
        for i in range(10):
            fins.box((.25, .05, .55), loc=(s * 1.98, 1.2 + i * .4, T_DECK - .4), bevel=0)
    cables = a.part('Kit_cables', 'Undercarriage')
    for x in (-.5, .5):
        cables.tube([(x, 3.3, T_DECK + .5), (x * 1.4, 2.6, T_DECK + .1), (x * 1.8, 1.8, T_DECK + .05)], .06, seg=5)
    for s in (-1, 1):
        K.smokestack(a, (s * 1.5, 5.4, T_DECK - .1), r=.16, h=1.0)
    # The shield emitter on its mast: the mast, the Radar pivot with the ring and three emitter prongs.
    a.part('Emitter_mast', 'Steel').cyl(.12, 2.2, loc=(0, 3.3, T_DECK + 1.1), seg=8, bevel=0)
    r = a.pivot('Radar', (0, 3.3, 5.45))
    k.lathe(a.part('Emitter_hub', 'Armor', r), [(.3, -.15), (.3, .1), (.2, .2), (0, .22)], seg=10)
    a.part('Emitter_ring', 'Energy', r).torus(.65, .05, loc=(0, 0, .35), seg=18, ring=4)
    for j in range(3):
        u = j * TAU / 3
        a.part('Emitter_prongs', 'Steel', r).tube([(0, 0, .1), (math.cos(u) * .65, math.sin(u) * .65, .35)], .04,
                                                   seg=4)
    K.soot(a, (1.5, 5.4, T_DECK + .9), radius=.8, k=.35)
    K.soot(a, (-1.5, 5.4, T_DECK + .9), radius=.8, k=.35)


def _tempest_turret(a):
    t = a.pivot('Turret', T_TURRET)
    body = a.part('Turret_body', 'Team', t)
    k.extrude(body, [(-1.5, -1.9), (1.5, -1.9), (1.75, -.6), (1.6, 1.9), (-1.6, 1.9), (-1.75, -.6)], .95,
              loc=(0, 0, .45), axis='Z', chamfer=.08, corner=.06, taper=(.84, .9))
    k.extrude(a.part('Turret_armor', 'Armor', t), [(-1.1, 1.9), (1.1, 1.9), (.95, 2.8), (-.95, 2.8)], .7,
              loc=(0, 0, .4), axis='Z', chamfer=.05, corner=.05)                               # the bustle
    K.hatch_round(a, (.9, .7, .93), r=.34, parent='Turret', periscopes=2)
    for s in (-1, 1):
        K.smoke_dischargers(a, 1.6, -.5, .55, s, count=3, parent='Turret')
    # The EMRG barrel: the sleeve at the mantlet, two rails with the insulating casing between them, coil frames
    # with glowing coils every metre, the square muzzle shroud. All Main_cannon* (the railgun part).
    y0, y1, z = -1.9, -9.75, .52
    k.block(a.part('Main_cannon_sleeve', 'Armor', t), (.95, 1.4, .8), loc=(0, y0 - .5, z - .4), chamfer=.06)
    L = y0 - .8 - y1
    for x in (-.2, .2):
        k.block(a.part('Main_cannon_rails', 'Steel', t), (.14, L, .3), loc=(x, (y0 - .8 + y1) / 2, z - .15),
                chamfer=.02)
    k.block(a.part('Main_cannon', 'Armor', t), (.26, L, .18), loc=(0, (y0 - .8 + y1) / 2, z - .09), chamfer=.02)
    for i in range(7):
        y = y0 - 1.3 - i * 1.0
        k.block(a.part('Main_cannon_coil_frames', 'Armor', t), (.7, .16, .56), loc=(0, y, z - .28), chamfer=.03)
        a.part('Main_cannon_coils', 'Energy', t).box((.74, .07, .6), loc=(0, y, z), bevel=0)
    k.block(a.part('Muzzle_brake', 'Armor', t), (.62, .45, .5), loc=(0, y1 + .22, z - .25), chamfer=.04)
    a.part('Muzzle_brake_bore', 'Undercarriage', t).box((.32, .02, .14), loc=(0, y1 - .01, z), bevel=0)
    a.pivot('Muzzle_main', (0, y1 - .09, z), 'Turret')
    K.soot(a, (0, T_TURRET[1] + y1, T_TURRET[2] + z), radius=1.1, k=.4)
    # The interceptor laser on the roof (Aps_*; Mount_APS): a small turret, its sensor faces, the emitter tube.
    ap = a.pivot('Mount_APS', (0, -.8, .83), 'Turret')
    k.lathe(a.part('Aps_base', 'Armor', ap), [(.35, 0), (.35, .12), (.28, .18), (0, .18)], seg=12)
    k.block(a.part('Aps_faces', 'Glass', ap), (.4, .3, .28), loc=(0, 0, .32), chamfer=.03)
    k.lathe(a.part('Aps_tubes', 'Steel', ap), [(.07, 0), (.07, .55), (.09, .6), (.09, .65)], loc=(0, -.12, .36),
            rot=K.FORWARD, seg=8)
    a.part('Aps_tubes_bore', 'Energy', ap).cyl(.05, .02, loc=(0, -.78, .36), rot=K.FORWARD, seg=8, bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (-1.2, 2.3, .78), h=1.3, r=.035)


def _tempest_coilguns(a):
    """Two coilgun mounts on the front deck (Mount_gun, .001; parts coil_l / coil_r): a ring, a boxy house, two
    rails with coil rings, the muzzle."""
    for i, s in enumerate((1, -1)):
        key = _key('Mount_gun', i)
        m = a.pivot(key, (s * .9, -3.3, 2.62))
        K.turret_ring(a.part('Coil_ring', 'Steel', m), (0, 0, -.08), .5, h=.08)
        k.block(a.part('Coil_house', 'Armor', m), (.9, 1.0, .5), loc=(0, .1, .22), chamfer=.05, taper=(.9, .9))
        for x in (-.1, .1):
            k.block(a.part('Coil_rails', 'Steel', m), (.08, 2.9, .12), loc=(x, -1.85, .32), chamfer=.01)
        for j in range(4):
            a.part('Coil_rings', 'Energy', m).box((.36, .06, .3), loc=(0, -.8 - j * .6, .32), bevel=0)
        k.block(a.part('Coil_muzzle', 'Armor', m), (.34, .2, .26), loc=(0, -3.25, .32), chamfer=.02)
        a.pivot(_key('Muzzle_gun', i), (0, -3.33, .32), key)
    K.tone(a, 'Mount_gun', k=.9)


def behemoth_tempest(a):
    """Behemoth Tempest: see the section notes."""
    K.suffixed(a)
    _tempest_hull(a)
    _tempest_rear(a)
    _tempest_turret(a)
    _tempest_coilguns(a)
    k.clean(a)


# ============================================================================= stymphalos
# Sen's jet UAV swarm: eight Loyal-Wingman jet drones in a V (its own drone, not the stymphalos_drone unit's):
# a chined trapezoid fuselage, a dorsal intake, swept wings, canted twin tails, a flat exhaust. Each drone on its
# Part_drone[.NNN] node at the old positions; the lead carries the flak pod (Mount_mg) and the drone bay's
# Muzzle_missile, the first pair the gun pods (Mount_gun, .001), the tail drone the second bay (Mount_missile.001).
DRONES = ((0.0, -6.0, 1.8), (3.6, -2.6, 1.55), (-3.6, -2.6, 1.55), (7.2, .8, 1.3), (-7.2, .8, 1.3),
          (10.8, 4.2, 1.05), (-10.8, 4.2, 1.05), (0.0, 3.4, .8))


def _drone_ring(y, w, h, zc=0.0):
    pts = [(-w, 0), (-w * .9, h * .3), (-w * .72, h * .62), (-w * .45, h * .9), (-w * .2, h), (w * .2, h),
           (w * .45, h * .9), (w * .72, h * .62), (w * .9, h * .3), (w, 0), (w * .7, -h * .32), (-w * .7, -h * .32)]
    return [(x, y, z + zc) for x, z in pts]


def _drone(a, i, loc):
    key = _key('Part_drone', i)
    p = a.pivot(key, loc)
    body = a.part('Fuselage', 'Armor', p)
    rings = [[(0, -2.55, -.02)]]
    for y, w, h in ((-2.3, .12, .1), (-2.0, .25, .19), (-1.5, .4, .3), (-1.0, .48, .36), (-.4, .54, .41),
                    (.4, .56, .42), (1.0, .54, .41), (1.6, .48, .36), (2.2, .38, .28), (2.45, .3, .2)):
        rings.append(_drone_ring(y, w, h))
    body.loft(rings)
    spine = a.part('Fins', 'Team', p)
    k.block(spine, (.32, 2.6, .05), loc=(0, .4, .42), chamfer=0)
    # Dorsal intake: the box mouth behind the nose, its dark duct.
    K.intake(a.part('Fuselage', 'Armor', p), a.part('Nozzles', 'Undercarriage', p), (0, -.75, .5), .5, .22, .55,
             facing=(0, -1, 0), lip=.03)
    # Wings: swept, tapered, a little dihedral; wingtip lights; the flat exhaust and its glow.
    K.wing(a.part('Wings', 'Armor', p), (-.35, 1.9), (1.05, .62), 1.75, x0=.45, z=.05, t=.06, dihedral=.04)
    a.part('Wing_lights', 'TeamGlow', p).box((.06, .2, .04), loc=(2.18, 1.3, .13), bevel=0)
    a.part('Wing_lights', 'TeamGlow', p).box((.06, .2, .04), loc=(-2.18, 1.3, .13), bevel=0)
    for s in (-1, 1):
        K.fin(a.part('Fins', 'Team', p), (1.45, 1.0), (2.15, .45), .82, x=s * .36, z0=.3, t=.06, cant=s * .45)
    k.block(a.part('Nozzles', 'Undercarriage', p), (.62, .2, .22), loc=(0, 2.5, .08), chamfer=.02)
    a.part('Nozzle_glow', 'Energy', p).box((.5, .03, .12), loc=(0, 2.61, .08), bevel=0)
    # Sensor windows under the nose, blade antennas, panel lines.
    a.part('Glass', 'Glass', p).box((.22, .3, .02), loc=(0, -1.75, -.08), rot=(.15, 0, 0), bevel=0)
    K.blade_antenna(a.part('Antennas', 'Steel', p), (0, .9, .44), h=.16, chord=.14)
    K.blade_antenna(a.part('Antennas', 'Steel', p), (0, -.2, -.17), h=.12, chord=.1, normal=(0, 0, -1))
    lines = a.part('Nozzles', 'Undercarriage', p)
    for y in (-1.2, -.1, 1.1):
        lines.box((.9, .02, .01), loc=(0, y, .415 if abs(y) < 1.5 else .35), bevel=0)
    # Control surfaces on the wings' trailing edges (ailerons, flaps) and the tails' rudders.
    surf = a.part('Fins', 'Team', p)
    for s in (-1, 1):
        for x0, x1, yl in ((.6, 1.3, 1.45), (1.35, 2.05, 1.62)):
            surf.box((x1 - x0, .22, .025), loc=(s * (x0 + x1) / 2, yl, .06), bevel=0)
        surf.box((.03, .2, .45), loc=(s * .52, 2.32, .62), rot=(0, s * .45, 0), bevel=0)
    # Wing pylons with the small missiles (the card's "small missiles"), a nose probe, the sensor fairing on the
    # chin, the gear doors' outlines.
    for s in (-1, 1):
        a.part('Antennas', 'Steel', p).box((.05, .5, .12), loc=(s * 1.25, .9, -.05), bevel=0)
        K.missile(a, (s * 1.25, 1.55, -.16), .055, 1.0, direction=(0, -1, 0), fins=4, parent=key, band=True)
    k.lathe(a.part('Antennas', 'Steel', p), [(.02, 0), (.012, .25), (0, .3)], loc=(0, -2.5, 0), rot=K.FORWARD, seg=5)
    k.lathe(a.part('Glass', 'Glass', p), [(.14, 0), (.12, .06), (.06, .1), (0, .11)],
            loc=(0, -1.2, -.12), rot=(math.pi, 0, 0), seg=8)
    for y, ln in ((-1.5, .5), (.3, .9)):
        for s in (-1, 1):
            lines.box((.012, ln, .01), loc=(s * .15, y, -.14), bevel=0)
    return key


def _stymphalos_fits(a):
    """The weapons on the drones: the lead's flak pod (Mount_mg) and bay (Muzzle_missile), the first pair's gun
    pods (Mount_gun, .001), the tail drone's bay (Mount_missile.001); the bays' doors open under the bellies."""
    lead = _key('Part_drone', 0)
    fm = a.pivot('Mount_mg', (0, .5, .5), lead)
    k.lathe(a.part('Flak_base', 'Armor', fm), [(.28, 0), (.28, .08), (.22, .12), (0, .12)], seg=10)
    k.block(a.part('Flak_pod', 'Team', fm), (.42, .6, .26), loc=(0, .0, .22), chamfer=.04)
    for x in (-.09, .09):
        a.part('Flak_barrels', 'Steel', fm).cyl(.025, .8, loc=(x, -.6, .14), rot=K.FORWARD, seg=6, bevel=0)
    a.pivot('Muzzle_mg', (0, -.92, .12), 'Mount_mg')
    a.pivot('Muzzle_missile', (0, -.4, -.2), lead)
    for key in (lead, _key('Part_drone', 7)):
        a.part('Bay_doors', 'Undercarriage', key).box((.5, 1.1, .02), loc=(0, .1, -.17), bevel=0)
        for s in (-1, 1):
            a.part('Bay_door_leaves', 'Armor', key).box((.02, 1.0, .25), loc=(s * .27, .1, -.28), rot=(0, s * .3, 0),
                                                       bevel=0)
    for i, s in enumerate((1, -1)):
        dk = _key('Part_drone', 1 + i)
        gk = _key('Mount_gun', i)
        gm = a.pivot(gk, (0, -.9, -.3), dk)
        k.lathe(a.part('Gun_pods', 'Armor', gm), [(0, -.3), (.1, -.2), (.12, .1), (.12, .6), (.08, .7), (0, .72)],
                loc=(0, 0, 0), rot=K.BACKWARD, seg=8)
        a.part('Gun_barrels', 'Steel', gm).cyl(.025, .5, loc=(0, -.7, 0), rot=K.FORWARD, seg=6, bevel=0)
        a.pivot(_key('Muzzle_gun', i), (0, -.96, 0), gk)
    tail = _key('Part_drone', 7)
    tm = a.pivot('Mount_missile__001', (0, 0, -.42), tail)
    k.block(a.part('Bay_rack', 'Steel', tm), (.3, .9, .08), loc=(0, -.2, .1), chamfer=0)
    a.pivot('Muzzle_missile__001', (0, -1.15, 0), 'Mount_missile__001')


def stymphalos(a):
    """Stymphalos: see the section notes."""
    K.suffixed(a)
    for i, loc in enumerate(DRONES):
        _drone(a, i, loc)
    _stymphalos_fits(a)
    k.clean(a)

BUILDERS = {
    'fortress_bastion': (fortress_bastion, dict(ao_distance=1.0, grime_height=1.5)),
    'fortress_hive': (fortress_hive, dict(ao_distance=1.0, grime_height=1.5)),
    'behemoth_inferno': (behemoth_inferno, dict(ao_distance=.8, grime_height=1.2)),
    'behemoth_tempest': (behemoth_tempest, dict(ao_distance=.8, grime_height=1.2)),
    'stymphalos': (stymphalos, dict(ao_distance=.4, ground=False)),
}
