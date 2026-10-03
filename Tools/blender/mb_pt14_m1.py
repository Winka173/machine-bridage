"""Play-test 14 model wave M1 (lane models): the ground bosses redrawn from scratch at 3.5 x the boss budget
(owner, Docs/prompts/playtest14_vi.txt: boss notes and "Bo sung 03/10"; DECISIONS "Play-test 14 model wave M1").

- fortress_bastion: the tracked casemate fortress. Its guns sit where a real casemate carries them: two twin 100 mm
  and two Bofors 40 mm in turning sponsons on the hull sides (front and rear quarters, matching their data arcs),
  the ZU-23-2 pair on side galleries at mid length, the 155 mm in the bow ball mount, the 240 mm mortar turret on
  the citadel and the Kornet pair behind it.
- bastion_mk0: its own model (it drew fortress_bastion). Brandt's prototype: a riveted girder-and-plate box on
  narrow tracks, the mortar on an open pedestal mount, two twin 100 mm in side sponsons, scaffolding, tarpaulins.
- mobile_fortress (Jotunn): the crawler fortress, with exactly two symmetric rocket launchers at the rear; the SAM
  moved to the bridge roof, the 125 mm (mount 5, slot "missile", aimed with the hull) a bow casemate gun.
- fenrir: its own model (it drew mobile_fortress): an articulated two-unit tracked winter raider (DT-30 read), the
  twin 35 mm flak turret on the front unit, the two 300 mm rocket pods and the target-marking radar on the rear unit.
- behemoth_inferno: the Behemoth's design (four tracks, wide flat hull, sloped glacis, faceted long turret) at a
  smaller size, the secondary guns gone, the twin flame projectors thinner than the Behemoth's 152 mm pair, the
  125 mm thermobaric gun turret on the glacis, the flak mount on the turret roof, the red fuel tanks at the rear.

Every round leaves from a barrel, tube or rail with its Muzzle_* point at the mouth (owner 03/10). Runtime names: each
builder's docstring. Built from frontier_kit / mb_kit27 / mb_kit35 primitives only; no other model's builder.
Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Matrix, Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w5parts as W

R90 = math.pi / 2
TAU = math.tau


def _n(base, i):
    return K.name(base, i)


def _per_barrel(a, muzzle, tag, xs):
    """Muzzle_b<k>_<tag> under the pivot `muzzle`, one per barrel at the x offsets `xs` (left to right)."""
    for i, x in enumerate(sorted(xs)):
        a.pivot(f'Muzzle_b{i + 1}_{tag}', (x, 0, 0), muzzle)


def _tag(slot, index):
    return slot if index == 0 else f'{slot}_{index:03d}'


def _rot_y(v, u):
    """(x, y) turned by u about Z."""
    x, y = v
    return (x * math.cos(u) - y * math.sin(u), x * math.sin(u) + y * math.cos(u))


# ============================================================================= fortress_bastion
B_TX = 3.05          # track centre line
B_WALL = 3.68        # casemate wall at the sponson line
B_DECK = 4.6         # the deck
B_CIT = 5.95         # the citadel roof
B_SPONSON = ((0, 1, -4.35), (1, -1, -4.35), (2, 1, 4.25), (3, -1, 4.25))     # (index, side, y)


def _bastion_running_gear(a):
    K.tracks(a, B_TX, 15.5, 1.78, .6, 9, 1.0, sprocket_end=1, cleat_pitch=.3, teeth=14, rollers=4)
    for s in (-1, 1):
        K.side_skirt(a, 3.66, -7.45, 7.25, 2.42, 1.3, s, panels=7, t=.12, mat='Armor')
        for y in (-7.0, -2.4, 2.4, 7.0):
            K.dust(a, (s * B_TX, y, .45), radius=2.3, k=.24)
    # Spare track links hung on the skirts between the sponsons, mud flaps at the ends.
    links = a.part('Spare_links', 'Undercarriage')
    pins = a.part('Spare_pins', 'Steel')
    for s in (-1, 1):
        for i in range(5):
            y = -1.9 + i * .95
            links.box((.07, .86, .28), loc=(s * 3.79, y, 1.85), bevel=.01)
            pins.cyl(.03, .1, loc=(s * 3.85, y, 1.95), rot=(0, R90, 0), seg=6, bevel=0)
        for y in (-7.55, 7.35):
            a.part('Mud_flaps', 'Rubber').box((1.05, .04, .7), loc=(s * B_TX, y, 1.15), bevel=0)


def _bastion_hull(a):
    """The lower hull between the tracks, the casemate (lofted: sloped walls, a raked glacis and stern), the deck
    edge, the citadel, the bow casemate box."""
    lower = a.part('Hull', 'Armor')
    K.chamfer_box(lower, (4.9, 15.2, 1.75), loc=(0, 0, 1.45), c=.1)
    k.extrude(lower, [(-8.05, .7), (-7.35, .7), (-7.35, 2.38), (-8.25, 2.05)], 5.0, axis='X', chamfer=.06)
    k.extrude(lower, [(7.35, .7), (7.95, .75), (8.05, 2.1), (7.35, 2.38)], 5.0, axis='X', chamfer=.06)
    body = a.part('Body', 'Team')
    K.section_loft(body, [
        (-8.15, [(0, 2.05), (3.1, 2.05), (3.15, 2.6), (2.35, 3.75), (0, 3.85)]),
        (-7.05, [(0, 2.35), (3.7, 2.35), (3.72, 3.15), (2.9, B_DECK), (0, B_DECK)]),
        (6.75, [(0, 2.35), (3.7, 2.35), (3.72, 3.15), (2.9, B_DECK), (0, B_DECK)]),
        (7.9, [(0, 2.35), (3.4, 2.35), (3.42, 3.0), (2.6, 4.15), (0, 4.25)])])
    # Deck plates (inset), the deck edge rail line, the team band along the shoulders.
    deck = a.part('Deck', 'Armor')
    for y0, y1 in ((-6.7, -2.3), (3.75, 6.5)):
        for x in (-1.4, 1.4):
            K.panel(a, deck, (2.5, y1 - y0 - .1), (x, (y0 + y1) / 2, B_DECK), (0, 0, 1), t=.04, rivet=.45)
    for s in (-1, 1):
        a.part('Team_band', 'Team').box((.04, 12.6, .22), loc=(s * 3.33, .1, 3.86), rot=(0, s * .69, 0), bevel=0)
    # The citadel on the deck: sloped cast walls, the roof inset, vision blocks round it.
    cit = a.part('Citadel', 'Team')
    k.extrude(cit, [(-2.3, -2.8), (2.3, -2.8), (2.3, 2.8), (-2.3, 2.8)], B_CIT - B_DECK + .05,
              loc=(0, .8, (B_CIT + B_DECK) / 2 - .02), axis='Z', chamfer=.08, corner=.35, taper=(.84, .88))
    k.inset(cit, lambda c, n, f: n.z > .9 and c.z > B_CIT - .02, width=.22, depth=-.03)
    glass = a.part('Glass', 'Glass')
    vb = a.part('Vision_blocks', 'Armor')
    for x in (-1.2, 0, 1.2):
        k.block(vb, (.42, .18, .2), loc=(x, -2.05, B_DECK + .6), rot=(-.2, 0, 0), chamfer=0)
        glass.box((.34, .02, .09), loc=(x, -2.15, B_DECK + .64), rot=(-.2, 0, 0), bevel=0)
    for s in (-1, 1):
        for y in (-.6, 1.6):
            k.block(vb, (.18, .42, .2), loc=(s * 2.2, y, B_DECK + .6), rot=(0, s * .2, 0), chamfer=0)
            glass.box((.02, .34, .09), loc=(s * 2.3, y, B_DECK + .64), rot=(0, s * .2, 0), bevel=0)
    # The bow casemate box round the 155 mm ball mount, its cheek plates.
    bow = a.part('Casemate', 'Armor')
    k.extrude(bow, [(-1.25, 2.4), (1.25, 2.4), (1.0, 4.0), (-1.0, 4.0)], .95, loc=(0, -8.38, 0), axis='Y',
              chamfer=.07, corner=.06)
    for s in (-1, 1):
        K.armour_plate(a, a.part('Plates', 'Armor'), (.7, 1.5, .1), (s * 1.3, -8.45, 3.2), rot=(0, s * .5, R90),
                       rivet=.4)


def _bastion_rivets(a):
    rv = a.part('Kit_rivets', 'Steel')
    for s in (-1, 1):
        K.rivet_line(rv, (s * 3.7, -6.9, 2.45), (s * 3.7, 6.6, 2.45), (s, 0, 0), pitch=.3, r=.026)
        K.rivet_line(rv, (s * 2.92, -6.9, B_DECK - .03), (s * 2.92, 6.6, B_DECK - .03), (s * .6, 0, .8), pitch=.3,
                     r=.026)
        K.rivet_line(rv, (s * 2.25, -1.9, B_DECK + .15), (s * 2.25, 3.4, B_DECK + .15), (s, 0, .2), pitch=.28,
                     r=.024)
    K.rivet_line(rv, (-2.8, -7.1, 4.5), (2.8, -7.1, 4.5), (0, -.6, .8), pitch=.3, r=.026)
    K.rivet_line(rv, (-3.3, 7.92, 3.6), (3.3, 7.92, 3.6), (0, 1, .3), pitch=.3, r=.026)


def _bastion_armour(a):
    """Riveted applique plates on the casemate walls between the sponsons (two rows), the glacis plates, chevrons,
    pistol ports, lamps, tow hooks and shackles, grab handles, ladders, the deck railing stanchions."""
    arm = a.part('Plates', 'Armor')
    for s in (-1, 1):
        for i in range(3):
            y = -1.9 + i * 1.9
            K.armour_plate(a, arm, (.75, 1.75, .1), (s * 3.66, y, 2.78), rot=(0, s * R90 * 1.0, 0), rivet=.4)
            K.armour_plate(a, arm, (.95, 1.75, .1), (s * 3.33, y, 3.85), rot=(0, s * .69, 0), rivet=.4)
        for y in (-6.4, 6.1):
            K.armour_plate(a, arm, (.95, 1.3, .1), (s * 3.33, y, 3.85), rot=(0, s * .69, 0), rivet=.4)
        # Pistol ports with their swing covers between the plates.
        for y in (-2.85, 2.85):
            k.lathe(a.part('Ports', 'Steel'), [(.13, 0), (.13, .06), (.09, .08), (0, .08)], loc=(s * 3.72, y, 2.8),
                    rot=(0, s * R90, 0), seg=8)
    for i in range(4):
        x = -1.65 + i * 1.1
        K.armour_plate(a, arm, (1.0, 1.25, .12), (x, -7.62, 3.27), rot=(1.0, 0, 0), rivet=.35)
    chev = a.part('Bow_chevrons', 'SafetyStripe')
    for i in range(5):
        chev.box((.5, .04, .16), loc=(-2.0 + i * 1.0, -8.17, 1.45), rot=(0, .6, 0), bevel=0)
    for s in (-1, 1):
        K.lamp(a, (s * 2.55, -8.0, 2.55), (0, -1, 0), r=.17)
        K.lamp(a, (s * 2.3, 7.9, 3.0), (0, 1, 0), r=.12, glow='LavaGlow', guard=False)
        K.tow_hook(a.part('Hull_steel', 'Steel'), (s * 1.7, -8.3, 1.35), facing=(0, -1, 0), size=.3)
        K.tow_hook(a.part('Hull_steel', 'Steel'), (s * 1.7, 8.1, 1.4), facing=(0, 1, 0), size=.28)
        a.part('Shackles', 'Hazard').torus(.12, .03, loc=(s * 2.2, -8.25, 1.75), rot=(R90, 0, 0), seg=10, ring=4)
    K.periscope(a, (.9, -7.15, 4.45), facing=(0, -1, 0), size=(.36, .3, .26))
    K.periscope(a, (-.9, -7.15, 4.45), facing=(0, -1, 0), size=(.36, .3, .26))
    a.part('Driver_visor', 'Glass').box((.9, .03, .12), loc=(0, -7.92, 3.72), rot=(1.0, 0, 0), bevel=0)
    for (x, y) in ((1.4, -5.2), (-1.5, -4.0), (-1.3, 5.6)):
        K.hatch_round(a, (x, y, B_DECK + .02), r=.46, periscopes=2)
    K.hatch_rect(a, (0, 3.0, B_CIT), (1.0, .9))
    K.ladder(a.part('Ladders', 'Steel'), (-3.78, 1.9, .9), (-3.55, 1.9, B_DECK - .1), width=.55, step=.36, r=.035)
    K.ladder(a.part('Ladders', 'Steel'), (-2.3, 3.75, B_DECK), (-1.95, 3.5, B_CIT), width=.5, step=.34, r=.03)
    rails = a.part('Railings', 'Steel')
    for s in (-1, 1):
        for y in (-6.8, -5.4, 5.0, 6.4):
            rails.tube([(s * 2.82, y, B_DECK), (s * 2.82, y, B_DECK + .75)], .03, seg=6)
        rails.tube([(s * 2.82, -6.8, B_DECK + .75), (s * 2.82, -5.4, B_DECK + .75)], .025, seg=6)
        rails.tube([(s * 2.82, 5.0, B_DECK + .75), (s * 2.82, 6.4, B_DECK + .75)], .025, seg=6)
    gr = a.part('Kit_handles', 'Steel')
    for s in (-1, 1):
        for y in (-4.0, -.5, 2.4):
            K.handle(gr, (s * 2.92, y - .3, 4.45), (s * 2.92, y + .3, 4.45), (s * .7, 0, .7), h=.07)


def _bastion_rear(a):
    """The engine deck (grilles, smokestacks with soot), the repair crane and welding gear, drums, the cable reel,
    the stern door, exhaust mufflers, a searchlight, a beacon, antennas, tarpaulin and stowage."""
    for s in (-1, 1):
        K.grille(a, (s * 1.45, 5.45, B_DECK + .03), 2.0, 1.5, facing=(0, 0, 1), slats=8, frame_mat='Team')
        K.smokestack(a, (s * 2.35, 7.0, B_DECK), r=.26, h=1.8)
        K.exhaust(a, (s * 2.6, 8.0, 2.9), r=.1, length=.6, direction=(0, .5, 1), muffler=True)
    st = a.part('Crane', 'CraneYellow')
    k.lathe(st, [(.34, 0), (.34, .3), (.22, .42), (.22, 1.45)], loc=(-1.45, 4.3, B_CIT - .05), seg=12, worn=(1,))
    st.limb((-1.45, 4.3, B_CIT + 1.3), (-2.95, 2.9, B_CIT + 2.3), .2, .24, bevel=.02)
    steel = a.part('Crane_steel', 'Steel')
    steel.limb((-1.45, 4.3, B_CIT + .6), (-2.2, 3.6, B_CIT + 1.75), .1, .1, bevel=0)
    steel.tube([(-2.95, 2.9, B_CIT + 2.25), (-2.95, 2.9, B_CIT + .95)], .02, seg=4)
    k.block(a.part('Hook_block', 'Hazard'), (.22, .16, .28), loc=(-2.95, 2.9, B_CIT + .8), chamfer=.02)
    # The crane stands on a pad behind the citadel.
    k.block(a.part('Crane_pad', 'Armor'), (1.1, 1.1, B_CIT - B_DECK - .05), loc=(-1.45, 4.3, B_DECK), chamfer=.05)
    for i, mat in enumerate(('Steel', 'BarrelRed', 'Steel', 'BarrelRed')):
        k.lathe(a.part('Gas_bottles', mat), [(.12, 0), (.12, 1.0), (.08, 1.1), (0, 1.14)],
                loc=(1.6 + i * .28, 7.2, B_DECK), seg=10, worn=(1,))
    a.part('Bottle_rack', 'Steel').box((1.3, .34, .06), loc=(2.0, 7.2, B_DECK + .7), bevel=0)
    k.lathe(a.part('Cable_reel', 'Steel'), [(.45, -.3), (.45, -.26), (.28, -.26), (.28, .26), (.45, .26), (.45, .3)],
            loc=(2.2, 3.95, B_DECK + .48), rot=(0, R90, 0), seg=12)
    a.part('Kit_cables', 'Rubber').torus(.36, .07, loc=(2.2, 3.95, B_DECK + .48), rot=(0, R90, 0), seg=14, ring=5)
    for i in range(3):
        K.fuel_drum(a.part('Drums', 'Fuel'), a.part('Drum_bands', 'Steel'), (-2.2 + i * .62, 7.3, B_DECK), r=.28,
                    h=.86)
    # Stern: the door, the spare road wheel, jerrycans in a rack.
    K.hatch_rect(a, (0, 7.97, 3.0), (1.1, 1.3), normal=(0, 1, .25))
    k.lathe(a.part('Spare_wheel', 'Rubber'), [(.4, -.12), (.6, -.1), (.6, .1), (.4, .12)], loc=(1.9, 8.1, 3.0),
            rot=(R90, 0, 0), seg=16)
    a.part('Spare_wheel_hub', 'Armor').cyl(.4, .2, loc=(1.9, 8.1, 3.0), rot=(R90, 0, 0), seg=16, bevel=.02)
    for i in range(3):
        K.jerrycan(a.part('Jerrycans', 'Fuel'), (-1.55 - i * .4, 8.05, 2.75), rot=(0, 0, R90))
    a.part('Jerrycan_rack', 'Steel').box((1.4, .1, .05), loc=(-1.95, 8.12, 2.5), bevel=0)
    K.floodlight(a, (1.9, -1.5, B_CIT), facing=(0, -1, -.3), pole=1.1)
    K.beacon(a, (-1.9, -1.3, B_CIT), r=.16)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-1.8, 3.2, B_CIT), h=2.6, r=.05)
    K.whip_antenna(a.part('Antennas', 'Steel'), (1.9, -.9, B_CIT), h=1.8, r=.045)
    K.mesh_antenna(a.part('Antennas', 'Steel'), (0, 6.6, B_DECK + .55), w=1.0, h=.5, normal=(0, 1, .2))
    K.net_roll(a.part('Stowage', 'Canvas'), a.part('Kit_straps', 'Undercarriage'), (0, -2.55, B_DECK + .2),
               length=2.2, r=.22)
    for i in range(2):
        K.crate(a.part('Ammo_boxes', 'Crate'), a.part('Kit_latches', 'Steel'), (.8, .5, .45),
                (-1.9 + i * .9, -6.3, B_DECK + .02), bands=2)
    for s in (-1, 1):
        K.soot(a, (s * 2.35, 7.0, B_DECK + 1.8), radius=1.3, k=.45)
        K.soot(a, (s * 2.6, 8.3, 3.4), radius=.8, k=.35)
        # Smoke dischargers on the citadel's front corners, entrenching tools racked on the casemate's front quarter.
        K.smoke_dischargers(a, 1.85, -1.75, B_CIT - .2, s, count=4)
        for j in range(2):
            y = -6.55 + j * .55
            a.part('Tool_racks', 'Steel').box((.05, .45, .06), loc=(s * 3.52, y, 3.35), rot=(0, s * .69, 0), bevel=0)
            a.part('Tools', 'Wood').limb((s * 3.45, y, 2.9), (s * 3.2, y, 4.0), .06, .06, bevel=0)
            a.part('Tools', 'Steel').box((.04, .26, .32), loc=(s * 3.5, y, 2.75), rot=(0, s * .69, 0), bevel=0)
        for j in range(3):
            a.part('Sandbags', 'Sandbag').box((.62, .34, .16), loc=(s * (1.0 + j * .62) * .9, -6.85, B_DECK + .09),
                                              bevel=.05)
            a.part('Sandbags', 'Sandbag').box((.62, .34, .16), loc=(s * (1.3 + j * .62) * .85, -6.82, B_DECK + .24),
                                              rot=(0, 0, .08 * s), bevel=.05)


def _bastion_sponson(a, index, s, y):
    """One side sponson: the fixed shelf and outer collar on the casemate wall, and on Mount_gun[.NNN] the turning
    gun house (faceted drum, sloped roof, mantlet, vision block, hatch) with twin 100 mm (front) or a Bofors 40 mm
    (rear), Muzzle_gun[.NNN] at the barrel mouths (per-barrel muzzles on the twins)."""
    x = s * 4.1
    z = 2.72
    # The fixed sponson shelf: a half-octagon bay out of the wall, gussets under it, the bolted outer collar.
    shelf = a.part('Sponsons', 'Armor')
    poly = [(s * 3.45, y - 1.15)]
    for i in range(7):
        u = -R90 + i * math.pi / 6
        poly.append((s * (3.9 + math.cos(u) * 1.1), y + math.sin(u) * 1.15))
    poly.append((s * 3.45, y + 1.15))
    if s < 0:
        poly = poly[::-1]
    k.extrude(shelf, poly, .34, loc=(0, 0, z - .17), axis='Z', chamfer=.05)
    for dy in (-.6, .6):
        shelf.limb((s * 3.7, y + dy, 1.95), (s * 4.7, y + dy, z - .3), .1, .14, bevel=.01)
    K.bolt_ring(a.part('Kit_bolts', 'Steel'), (x, y, z + .005), (0, 0, 1), 1.08, 16, r=.022, h=.02)
    key = _n('Mount_gun', index)
    m = a.pivot(key, (x, y, z))
    twin = index < 2
    sc = 1.0 if twin else .86
    house = a.part('Gun_house', 'Team', m)
    rings = []
    for zz, r in ((0.02, 1.0), (.72 * sc, 1.04), (1.15 * sc, .76)):
        ring = []
        for i in range(8):
            u = i * TAU / 8 + TAU / 16
            ring.append((math.cos(u) * r, math.sin(u) * r * 1.05))
        rings.append((zz, ring))
    W.poly_turret(house, rings, chamfer=.05)
    K.turret_ring(a.part('Gun_ring', 'Steel', m), (0, 0, -.02), 1.02, h=.1)
    # The mantlet across the front, its cheek plates, the barrels.
    mz = .58 * sc
    K.chamfer_box(a.part('Gun_mantlet', 'Armor', m), (1.2 if twin else .8, .5, .62 * sc), loc=(0, -1.05, mz - .3 * sc),
                  c=.06)
    tag = _tag('gun', index)
    if twin:
        L, r = 3.3, .075
        for bx in (-.26, .26):
            K.gun_barrel(a, 'Gun_barrels', key, bx, -1.28, mz, L, r, seg=12, extractor=(.42, 1.5, .4),
                         brake_name='Gun_brakes', brake='baffle')
        tip = -1.28 - L - .3
        mzp = a.pivot(_n('Muzzle_gun', index), (0, tip, mz), key)
        _per_barrel(a, mzp, tag, (-.26, .26))
    else:
        L, r = 2.7, .055
        K.gun_barrel(a, 'Gun_barrels', key, 0, -1.28, mz, L, r, seg=10, extractor=(.3, 1.9, .55), brake_name=None)
        k.lathe(a.part('Gun_flash', 'Undercarriage', m), [(.075, 0), (.085, .32), (.06, .34), (0, .34)],
                loc=(0, -1.28 - L - .32, mz), rot=K.BACKWARD, seg=10)
        # The Bofors' loader frame and clip rack on the house's back.
        k.block(a.part('Clip_rack', 'Crate', m), (.55, .3, .38), loc=(0, 1.02, .5 * sc), chamfer=.03)
        tip = -1.28 - L - .34
        a.pivot(_n('Muzzle_gun', index), (0, tip, mz), key)
    # Vision block, the commander's hatch and a lamp on the house.
    K.periscope(a, (-.38 * s, -.5, 1.15 * sc), facing=(0, -1, 0), parent=key, size=(.24, .2, .18))
    K.hatch_round(a, (.32 * s, .28, 1.15 * sc), r=.3, parent=key, periscopes=1, seg=12)
    K.lamp(a, (.7 * s, -.8, .8 * sc), (0, -1, 0), r=.08, parent=key)
    for i in range(6):
        u = i * TAU / 6
        a.part('Gun_house_bolts', 'Steel', m).cyl(.03, .03, loc=(math.cos(u) * .92, math.sin(u) * .96, .74 * sc),
                                                  seg=6, bevel=0)
    K.tone(a, key, k=.92)
    K.soot(a, (x, y + tip, z + mz), radius=.7, k=.4)


def _bastion_weapons(a):
    """The mortar turret on the citadel (Turret: Main_cannon, its breech, buffers, bore; Muzzle_main), the four side
    sponsons (Mount_gun .. .003), the bow 155 mm (Mount_gun.004), the Kornet pair (Part_missile / Mount_missile), the
    ZU-23-2 pair on the side galleries (Mount_mg, Mount_mg.001)."""
    t = a.pivot('Turret', (0, .6, B_CIT))
    tt = a.part('Turret_armor', 'Armor', t)
    k.lathe(tt, [(1.82, 0), (1.88, .1), (1.88, .32), (1.66, .5), (1.2, .58), (0, .6)], seg=28, worn=(2, 3))
    K.turret_ring(a.part('Turret_steel', 'Steel', t), (0, 0, -.04), 1.88, h=.12)
    # The two side frames carrying the trunnions (faceted cheeks with lightening holes), the cradle.
    for s in (-1, 1):
        k.extrude(tt, [(-1.0, .45), (1.15, .45), (.95, 1.8), (-.25, 2.0)], .24, loc=(s * .78, 0, 0), axis='X',
                  chamfer=.03, corner=.05)
        a.part('Turret_steel', 'Steel', t).cyl(.16, .12, loc=(s * .92, .3, 1.15), rot=(0, R90, 0), seg=12, bevel=.01)
    m = Matrix.Translation(Vector((0, .3, 1.15))) @ Matrix.Rotation(math.radians(-60), 4, 'X')
    rot = tuple((m @ Matrix.Rotation(R90, 4, 'X')).to_euler('XYZ'))
    L = 3.25
    k.lathe(a.part('Main_cannon', 'Steel', t), [(.32, -.6), (.32, .2), (.28, .32), (.28, 1.2), (.3, 1.25), (.3, 1.35),
                                                (.27, 1.4), (.27, L - .25), (.34, L - .2), (.34, L), (.21, L),
                                                (.21, L - .1), (0, L - .1)],
            loc=tuple(m @ Vector((0, 0, 0))), rot=rot, seg=18, worn=(2, 9))
    k.lathe(a.part('Main_cannon_breech', 'Armor', t), [(0, -1.15), (.44, -1.1), (.47, -.62), (.38, -.5)],
            loc=tuple(m @ Vector((0, 0, 0))), rot=rot, seg=16)
    for sx in (-1, 1):
        a.part('Main_cannon_buffer', 'Steel', t).limb(tuple(m @ Vector((sx * .38, -.3, .1))),
                                                     tuple(m @ Vector((sx * .38, -.3, -1.35))), .11, .11, bevel=0)
    k.lathe(a.part('Main_cannon_bore', 'Undercarriage', t), [(.17, 0), (.17, .02), (0, .02)],
            loc=tuple(m @ Vector((0, -L + .11, 0))), rot=rot, seg=14)
    tip = m @ Vector((0, -L, 0))
    a.pivot('Muzzle_main', tuple(tip), 'Turret')
    # The loading tray and a ready rack of 240 mm bombs on the turret's back, the hatch, a sight.
    tray = a.part('Loader_tray', 'Steel', t)
    tray.box((.5, 1.4, .06), loc=(0, 1.5, .75), rot=(.35, 0, 0), bevel=0)
    for sx in (-1, 1):
        tray.box((.05, 1.4, .18), loc=(sx * .26, 1.5, .8), rot=(.35, 0, 0), bevel=0)
    for i in range(3):
        k.lathe(a.part('Ready_bombs', 'Fuel', t), [(0, -.55), (.12, -.45), (.15, -.2), (.15, .35), (.1, .5),
                                                   (0, .55)], loc=(-.7 + i * .7, 1.55, .38), rot=(R90, 0, 0), seg=10)
    a.part('Bomb_rack', 'Armor', t).box((2.2, .3, .08), loc=(0, 1.55, .2), bevel=0)
    K.hatch_round(a, (1.1, -.9, .55), r=.38, parent='Turret', periscopes=1, seg=12)
    K.periscope(a, (-1.1, -.95, .55), facing=(0, -1, 0), parent='Turret', size=(.3, .24, .22))
    K.soot(a, (0, .6 + tip.y, B_CIT + tip.z), radius=1.0, k=.45)
    K.tone(a, 'Turret', k=.95)
    for index, s, y in B_SPONSON:
        _bastion_sponson(a, index, s, y)
    # The bow 155 mm in its ball mantlet (Mount_gun.004).
    key = _n('Mount_gun', 4)
    bm = a.pivot(key, (0, -8.72, 3.2))
    k.lathe(a.part('Bow_mantlet', 'Armor', bm), [(0, -.55), (.6, -.48), (.74, 0), (.62, .42), (0, .5)],
            rot=K.FORWARD, seg=16)
    K.bolt_ring(a.part('Kit_bolts', 'Steel', bm), (0, -.42, 0), (0, -1, 0), .55, 10, r=.022, h=.02)
    K.gun_barrel(a, 'Bow_barrel', key, 0, -.5, 0, 4.7, .12, seg=14, extractor=(.4, 1.5, .55), brake_name=None)
    k.lathe(a.part('Bow_brake', 'Undercarriage', bm), [(.13, 0), (.22, .04), (.22, .5), (.13, .54), (0, .54)],
            loc=(0, -5.74, 0), rot=K.BACKWARD, seg=12)
    for dz in (.12, .3):
        a.part('Bow_brake', 'Undercarriage', bm).box((.5, .06, .12), loc=(0, -5.74 + dz, 0), bevel=0)
    a.pivot(_n('Muzzle_gun', 4), (0, -5.76, 0), key)
    K.soot(a, (0, -14.4, 3.2), radius=.6, k=.3)
    # The Kornet pair on the citadel roof behind the mortar (Part_missile, its Mount_missile).
    pm = a.pivot('Part_missile', (1.42, 2.75, B_CIT))
    k.block(a.part('Kornet_base', 'Armor', pm), (.9, .9, .28), loc=(0, 0, .02), chamfer=.04)
    km = a.pivot('Mount_missile', (0, 0, .45), 'Part_missile')
    k.block(a.part('Kornet_cradle', 'Armor', km), (.75, .5, .4), loc=(0, .2, -.1), chamfer=.03)
    for x in (-.24, .24):
        k.lathe(a.part('Kornet_tubes', 'Team', km), [(.1, -.95), (.1, .7), (.12, .72), (.12, .82), (.07, .82),
                                                     (.07, .78), (0, .78)],
                loc=(x, .05, .35), rot=(R90 - .25, 0, 0), seg=12, caps=(True, False))
        for f in (-.6, .3):
            a.part('Kornet_bands', 'Steel', km).torus(.105, .02, loc=(x, .05 - f * math.cos(.25),
                                                                      .35 + f * math.sin(.25)),
                                                      rot=(R90 - .25, 0, 0), seg=12, ring=4)
    K.periscope(a, (0, .5, .3), facing=(0, -1, 0), parent='Mount_missile', size=(.22, .2, .22))
    mzk = a.pivot('Muzzle_missile', (0, .05 - .82 * math.cos(.25), .35 + .82 * math.sin(.25)), 'Mount_missile')
    _per_barrel(a, mzk, 'missile', (-.24, .24))
    K.tone(a, 'Part_missile', k=.9)
    # The ZU-23-2 pair on the side galleries at mid length (the roof-gun rule: they stand on a gallery and a column).
    for i, s in enumerate((1, -1)):
        x, y = s * 3.42, 1.25
        gal = a.part('Galleries', 'Armor')
        k.extrude(gal, [(s * 2.75, y - .85), (s * 3.95, y - .7), (s * 3.95, y + .7), (s * 2.75, y + .85)], .16,
                  loc=(0, 0, B_DECK + .05), axis='Z', chamfer=.03)
        for dy in (-.55, .55):
            gal.limb((s * 3.25, y + dy, 3.55), (s * 3.9, y + dy, B_DECK - .05), .08, .1, bevel=0)
        rail = a.part('Railings', 'Steel')
        rail.tube([(s * 3.92, y - .65, B_DECK + .13), (s * 3.92, y - .65, B_DECK + .75),
                   (s * 3.92, y + .65, B_DECK + .75), (s * 3.92, y + .65, B_DECK + .13)], .025, seg=6)
        ped = a.part('Zu_pedestals', 'Steel')
        k.lathe(ped, [(.45, 0), (.45, .07), (.2, .15), (.18, .55), (.32, .6), (.32, .67)], loc=(x, y, B_DECK + .13),
                seg=12, worn=(1, 4))
        key = _n('Mount_mg', i)
        zm = a.pivot(key, (x, y, B_DECK + .8))
        zh = a.part('Zu_carriage', 'Armor', zm)
        k.block(zh, (.8, .95, .14), loc=(0, .1, .02), chamfer=.02)
        for sx in (-1, 1):
            k.block(zh, (.1, .62, .42), loc=(sx * .25, 0, .12), chamfer=.015)
            K.gun_barrel(a, 'Zu_barrels', key, sx * .13, .2, .3, 2.4, .043, seg=8, extractor=(.3, 1.7, .25),
                         brake_name=None)
            k.lathe(a.part('Zu_flash', 'Undercarriage', zm), [(.05, 0), (.06, .18), (.045, .2), (0, .2)],
                    loc=(sx * .13, .2 - 2.4 - .2, .3), rot=K.BACKWARD, seg=8)
            k.block(a.part('Zu_magazines', 'Crate', zm), (.12, .38, .3), loc=(sx * .38, .05, .28), chamfer=.015)
        K.chamfer_box(a.part('Zu_shield', 'Armor', zm), (.85, .05, .45), loc=(0, -.45, .32), c=.01)
        K.chamfer_box(a.part('Zu_seats', 'Canvas', zm), (.28, .25, .08), loc=(-s * .48, .55, .3), c=.015)
        mk = a.pivot(_n('Muzzle_mg', i), (0, .2 - 2.4 - .22, .3), key)
        _per_barrel(a, mk, _tag('mg', i), (-.13, .13))
        K.tone(a, key, k=.92)


def fortress_bastion(a):
    """Fortress Bastion (see the module docstring). Runtime: Turret / Main_cannon* / Muzzle_main (mortar),
    Mount_gun .. .003 + Muzzle_gun .. .003 (the side sponsons: turret_fl, turret_fr, turret_rl, turret_rr),
    Mount_gun.004 / Muzzle_gun.004 (casemate), Part_missile / Mount_missile / Muzzle_missile (kornet), Mount_mg /
    .001 + Muzzle_mg / .001 (zu23_l / _r; the hmg mounts 6 and 7 fire from them too); per-barrel muzzles."""
    K.suffixed(a)
    _bastion_running_gear(a)
    _bastion_hull(a)
    _bastion_armour(a)
    _bastion_rivets(a)
    _bastion_rear(a)
    _bastion_weapons(a)
    k.clean(a)


# ============================================================================= mobile_fortress (Jotunn)
J_DECK = 4.0
J_TRUCKS = (-5.3, 5.25)


def _jotunn_trucks(a):
    """The four corner crawler trucks (two track units each), their frames, mudguards, the jacking cylinders up to
    the platform, the hazard bands, the corner lamps and boarding steps."""
    for yc in J_TRUCKS:
        wheels = [yc - 1.36 + i * .68 for i in range(5)]
        for tx in (2.62, 3.82):
            W.running_gear(a, tx, .9, .4, wheels, (yc - 1.82, .54, .36), (yc + 1.8, .58, .38), rollers=(yc - .7, yc + .7),
                           roller_z=1.02, top_hidden=None, disc_mat='Armor', seg=16, link_pitch=.3, wheel_w=.22,
                           dust=.22, teeth=11)
        front = yc < 0
        for s in (-1, 1):
            K.chamfer_box(a.part('Truck_frames', 'Armor'), (2.35, 4.15, .62), loc=(s * 3.22, yc, 1.62), c=.07)
            K.fender(a.part('Mudguards', 'Team'), 3.22, yc - 2.15, yc + 2.15, 1.98, 2.5, s, lip=.12)
            for dy in (-1.25, 0, 1.25):
                k.lathe(a.part('Jacks', 'Steel'), [(.26, 0), (.26, .12), (.2, .16), (.2, .48), (.16, .52), (.16, .72)],
                        loc=(s * 3.22, yc + dy, 1.95), seg=12, worn=(1, 3))
                a.part('Jack_boots', 'Rubber').cyl(.24, .14, loc=(s * 3.22, yc + dy, 2.2), seg=12, bevel=.02)
            a.part('Hazard_bands', 'Hazard').box((.03, 3.7, .16), loc=(s * 4.48, yc, 1.66), bevel=0)
            ly = yc - 2.1 if front else yc + 2.1
            K.lamp(a, (s * 3.25, ly, 1.65), (0, -1 if front else 1, 0), r=.13, guard=True,
                   glow='Lamp' if front else 'LavaGlow')
            st = a.part('Steps', 'Steel')
            for j in range(3):
                st.box((.5, .3, .04), loc=(s * 4.52, yc + (1.3 if front else -1.3), .55 + j * .42), bevel=0)
            st.box((.04, .3, 1.4), loc=(s * 4.78, yc + (1.3 if front else -1.3), 1.1), bevel=0)


def _jotunn_platform(a):
    """The platform slab (lofted, chamfered), the cross girders under it between the trucks, deck plates, railings,
    hazard edges, ladders, the team band, the fuel tank row and the crane on the left side."""
    K.section_loft(a.part('Hull', 'Team'), [
        (-8.0, [(0, 2.85), (3.85, 2.85), (4.3, 3.3), (4.0, 3.95), (0, 3.95)]),
        (-7.25, [(0, 2.62), (4.15, 2.62), (4.62, 3.25), (4.3, J_DECK), (0, J_DECK)]),
        (7.2, [(0, 2.62), (4.15, 2.62), (4.62, 3.25), (4.3, J_DECK), (0, J_DECK)]),
        (7.95, [(0, 2.85), (3.85, 2.85), (4.3, 3.3), (4.0, 3.95), (0, 3.95)])])
    gird = a.part('Girders', 'Undercarriage')
    for y in (-2.6, -1.0, .6, 2.2):
        gird.box((7.4, .32, .5), loc=(0, y, 2.38), bevel=.02)
    for x in (-1.6, 1.6):
        gird.box((.3, 5.6, .4), loc=(x, -.2, 2.4), bevel=.02)
    dp = a.part('Deck', 'Armor')
    for col in range(2):
        for y in (-3.95, 5.2):
            K.panel(a, dp, (3.55, 1.7), (-1.9 + col * 3.8, y, J_DECK), (0, 0, 1), t=.04, rivet=.45)
    for s in (-1, 1):
        K.railing(a.part('Railings', 'Steel'), [(s * 4.18, -7.0, J_DECK), (s * 4.18, -4.3, J_DECK)], h=.9, post=.9,
                  r=.035)
        K.railing(a.part('Railings', 'Steel'), [(s * 4.18, 4.2, J_DECK), (s * 4.18, 7.1, J_DECK)], h=.9, post=.95,
                  r=.035)
        a.part('Plough_stripes', 'Hazard').box((.04, 14.2, .2), loc=(s * 4.63, 0, 3.25), bevel=0)
        a.part('Team_band', 'Team').box((.03, 9.5, .32), loc=(s * 4.47, -.4, 3.62), rot=(0, -s * .4, 0), bevel=0)
        K.ladder(a.part('Ladders', 'Steel'), (s * 4.72, -2.55, .25), (s * 4.72, -2.55, 3.2), width=.6, step=.38)
        a.part('Hazard_bands', 'Hazard').box((.16, 14.0, .02), loc=(s * 3.86, 0, J_DECK + .01), bevel=0)
        for y in (-1.7, 1.2):
            K.panel(a, a.part('Deck', 'Armor'), (2.4, .6), (s * 4.47, y, 3.62), (s * .92, 0, .39), t=.05, rivet=.35)
    # The external fuel tanks under the right deck edge, on cradles.
    for j in range(3):
        k.lathe(a.part('Fuel_tanks', 'Armor'), [(0, -.8), (.36, -.76), (.4, -.5), (.4, .5), (.36, .76), (0, .8)],
                loc=(-4.0, -1.7 + j * 1.75, 2.2), rot=K.FORWARD, seg=12)
        for f in (-.45, .45):
            a.part('Tank_straps', 'Steel').torus(.41, .025, loc=(-4.0, -1.7 + j * 1.75 + f, 2.2), rot=(R90, 0, 0),
                                                 seg=12, ring=3)
    rv = a.part('Kit_rivets', 'Steel')
    for s in (-1, 1):
        K.rivet_line(rv, (s * 4.4, -7.1, 3.0), (s * 4.4, 7.1, 3.0), (s * .8, 0, -.6), pitch=.3, r=.025)
        K.rivet_line(rv, (s * 4.48, -7.1, 3.48), (s * 4.48, 7.1, 3.48), (s * .92, 0, .39), pitch=.3, r=.025)
        for yc in J_TRUCKS:
            K.rivet_line(rv, (s * 4.4, yc - 1.95, 1.75), (s * 4.4, yc + 1.95, 1.75), (s, 0, 0), pitch=.25, r=.025)
            K.rivet_line(rv, (s * 2.04, yc - 1.95, 1.75), (s * 2.04, yc + 1.95, 1.75), (-s, 0, 0), pitch=.25, r=.025)
    for y in (-8.0, 7.95):
        K.rivet_line(rv, (-3.8, y + (.02 if y > 0 else -.02), 3.4), (3.8, y + (.02 if y > 0 else -.02), 3.4),
                     (0, 1 if y > 0 else -1, 0), pitch=.3, r=.025)
    W.lifting_eyes(a.part('Kit_tow', 'Steel'), [(s * 4.15, y, J_DECK + .05) for s in (-1, 1) for y in (-6.7, 6.7)],
                   r=.14)
    W.tow_set(a, -8.02, 3.25, 2.8, (0, -1, 0))
    W.tow_set(a, 7.98, 3.25, 2.8, (0, 1, 0))
    cr = a.part('Crane', 'CraneYellow')
    cr.cyl(.24, 2.0, loc=(3.55, 2.9, J_DECK + 1.0), seg=12, bevel=.02)
    cr.limb((3.55, 2.9, J_DECK + 1.9), (5.6, 1.6, J_DECK + 2.6), .18, .26, bevel=.02)
    a.part('Crane_steel', 'Steel').limb((3.55, 2.9, J_DECK + 1.2), (4.4, 2.35, J_DECK + 2.15), .1, .1, bevel=0)
    a.part('Kit_cables', 'Steel').tube([(5.6, 1.6, J_DECK + 2.5), (5.6, 1.6, J_DECK - .2)], .025, seg=4)
    k.block(a.part('Crane_hook', 'Hazard'), (.24, .2, .3), loc=(5.6, 1.6, J_DECK - .45), chamfer=.02)
    k.lathe(a.part('Crane_load', 'Crate'), [(.0, 0), (.42, 0), (.42, .7), (0, .7)], loc=(5.6, 1.6, J_DECK - 1.25),
            seg=10)
    for j in range(4):
        K.crate(a.part('Ammo_crates', 'Crate'), a.part('Kit_latches', 'Steel'), (.85, .58, .48),
                (2.9 + (j % 2) * .95, -3.75 + (j // 2) * .68, J_DECK + .02), bands=2)
    K.net_roll(a.part('Stowage', 'Canvas'), a.part('Kit_straps', 'Undercarriage'), (-3.3, -3.7, J_DECK + .22),
               length=1.8, r=.22, axis='Y')


def _jotunn_bridge(a):
    """The glazed command bridge on the bow (the Kharkovchanka read): the raked window band in its frames, wipers,
    the roof with the SAM box (Mount_missile.001), the sight, an antenna; the flak cupolas on the front corners
    (Mount_mg left, .001 right) with twin 35 mm; the 125 mm bow casemate gun under the bridge (Mount_missile,
    aimed with the hull)."""
    br = a.part('Bridge', 'Team')
    W.poly_turret(br, [(J_DECK, [(-2.35, -7.45), (2.35, -7.45), (2.65, -6.3), (2.65, -4.5), (-2.65, -4.5),
                                 (-2.65, -6.3)]),
                       (J_DECK + .55, [(-2.35, -7.5), (2.35, -7.5), (2.65, -6.35), (2.65, -4.5), (-2.65, -4.5),
                                       (-2.65, -6.35)]),
                       (J_DECK + 1.65, [(-1.95, -6.8), (1.95, -6.8), (2.35, -6.05), (2.35, -4.6), (-2.35, -4.6),
                                        (-2.35, -6.05)])], chamfer=.05)
    for i in range(5):
        x = -1.6 + i * .8
        a.part('Windows', 'Glass').mesh([(x - .34, -7.52, J_DECK + .62), (x + .34, -7.52, J_DECK + .62),
                                         (x + .3, -6.87, J_DECK + 1.48), (x - .3, -6.87, J_DECK + 1.48)],
                                        [(0, 1, 2, 3)])
        a.part('Window_frames', 'Armor').box((.07, .1, 1.07), loc=(x + .4, -7.2, J_DECK + 1.05), rot=(-.85, 0, 0),
                                             bevel=0)
        a.part('Wipers', 'Undercarriage').limb((x, -7.5, J_DECK + .66), (x + .15, -7.25, J_DECK + 1.0), .02, .02,
                                               bevel=0)
    for s in (-1, 1):
        a.part('Windows', 'Glass').mesh([(s * 2.4, -7.25, J_DECK + .62), (s * 2.67, -6.3, J_DECK + .62),
                                         (s * 2.37, -6.05, J_DECK + 1.48), (s * 2.0, -6.8, J_DECK + 1.48)],
                                        [(0, 1, 2, 3) if s > 0 else (3, 2, 1, 0)])
        a.part('Visor', 'Armor').box((.08, 1.4, .06), loc=(s * 2.55, -5.4, J_DECK + 1.4), bevel=0)
    a.part('Window_frames', 'Armor').box((4.75, .12, .1), loc=(0, -7.5, J_DECK + .57), bevel=0)
    a.part('Sun_visor', 'Armor').box((4.0, .55, .05), loc=(0, -6.85, J_DECK + 1.68), rot=(.15, 0, 0), bevel=0)
    a.part('Bridge_roof', 'Medical').box((3.8, 1.3, .04), loc=(0, -5.35, J_DECK + 1.67), bevel=0)
    K.chamfer_box(a.part('Sight', 'Armor'), (.6, .5, .4), loc=(1.4, -5.3, J_DECK + 1.85), c=.04)
    a.part('Periscope', 'Glass').box((.42, .01, .2), loc=(1.4, -5.56, J_DECK + 1.87), bevel=0)
    K.whip_antenna(a.part('Antenna', 'Steel'), (1.95, -4.85, J_DECK + 1.65), h=2.2, lean=.05)
    K.beacon(a, (.4, -4.85, J_DECK + 1.65), r=.12)
    K.hatch_rect(a, (-.3, -4.95, J_DECK + 1.66), (.7, .5))
    # The SAM box on the bridge roof (Mount_missile.001): turntable, the tilted four-cell box, its radar plate.
    sm = a.pivot(_n('Mount_missile', 1), (-1.25, -5.5, J_DECK + 1.68))
    k.lathe(a.part('Sam_base', 'Steel', sm), [(.5, 0), (.52, .05), (.52, .15), (.45, .18)], seg=14)
    K.chamfer_box(a.part('Sam_pedestal', 'Armor', sm), (.6, .6, .5), loc=(0, .1, .15), c=.04)
    sb = Matrix.Translation(Vector((0, .05, .95))) @ Matrix.Rotation(-.45, 4, 'X')
    k.block(a.part('Sam_box', 'Team', sm), (.95, 1.3, .72), loc=tuple(sb @ Vector((0, 0, -.36))), rot=(-.45, 0, 0),
            chamfer=.04)
    face = a.part('Tubes_bore', 'Undercarriage', sm)
    for dx in (-.21, .21):
        for dz in (-.16, .16):
            face.cyl(.13, .04, loc=tuple(sb @ Vector((dx, -.655, -.36 + dz))), rot=(R90 - .45, 0, 0), seg=10,
                     bevel=0)
    k.block(a.part('Sam_radar', 'Armor', sm), (.75, .08, .55), loc=(0, .68, .95), chamfer=.015)
    a.pivot(_n('Muzzle_missile', 1), tuple(sb @ Vector((0, -.68, -.36))), sm)
    K.tone(a, 'Mount_missile', k=.92)
    # The flak cupolas on the deck's front corners.
    for i, s in ((0, 1), (1, -1)):
        key = _n('Mount_mg', i)
        m = a.pivot(key, (s * 3.3, -6.15, J_DECK + .32))
        k.lathe(a.part('Cupola_ring', 'Steel'), [(.82, 0), (.86, .05), (.86, .28), (.8, .32)],
                loc=(s * 3.3, -6.15, J_DECK), seg=16)
        k.lathe(a.part('Flak_cupola', 'Team', m), [(.78, -.02), (.78, .2), (.72, .4), (.55, .62), (.3, .74), (0, .77)],
                seg=16, worn=(2, 3))
        k.block(a.part('Flak_mantlet', 'Armor', m), (.7, .35, .42), loc=(0, -.66, .2), chamfer=.04)
        for dx in (-.14, .14):
            K.gun_barrel(a, 'Flak_barrels', key, dx, -.8, .32, 1.7, .04, seg=8, extractor=(.35, 1.7, .3),
                         brake_name=None)
            k.lathe(a.part('Flak_flash', 'Undercarriage', m), [(.05, 0), (.065, .2), (.05, .22), (0, .22)],
                    loc=(dx, -.8 - 1.7 - .22, .32), rot=K.BACKWARD, seg=8)
        a.part('Flak_glass', 'Glass', m).box((.3, .02, .1), loc=(.3, -.62, .52), rot=(-.5, 0, .3), bevel=0)
        k.block(a.part('Flak_radar', 'Armor', m), (.4, .06, .3), loc=(0, .55, .78), chamfer=.01)
        mk = a.pivot(_n('Muzzle_mg', i), (0, -.8 - 1.7 - .24, .32), key)
        _per_barrel(a, mk, _tag('mg', i), (-.14, .14))
    # The 125 mm bow gun in its ball mount under the bridge (Mount_missile: the def's mount 5 fires a 125 mm round
    # from the "missile" slot, aimed with the hull).
    bow = a.part('Bow_casemate', 'Armor')
    k.extrude(bow, [(-1.0, 2.75), (1.0, 2.75), (.85, 3.9), (-.85, 3.9)], .5, loc=(0, -8.15, 0), axis='Y',
              chamfer=.06, corner=.05)
    gm = a.pivot('Mount_missile', (0, -8.45, 3.3))
    k.lathe(a.part('Bow_mantlet', 'Steel', gm), [(0, -.45), (.48, -.38), (.56, 0), (.48, .35), (0, .4)],
            rot=K.FORWARD, seg=16)
    K.gun_barrel(a, 'Bow_barrel', gm, 0, -.42, 0, 2.7, .085, seg=12, extractor=(.45, 1.6, .4),
                 brake_name='Bow_collar', brake='collar')
    a.pivot('Muzzle_missile', (0, -.42 - 2.7 - .14, 0), gm)
    K.soot(a, (0, -11.6, 3.3), radius=.5, k=.3)


def _jotunn_core(a):
    """The armoured core block carrying the turret: battered walls with vents and grilles, appliqué plates, the
    hatch and ladder up, exhaust stacks, the EMP radar mast (Radar spins)."""
    core = a.part('Core', 'Team')
    k.block(core, (6.0, 7.5, 2.2), loc=(0, .35, J_DECK), chamfer=.1, taper=(.9, .9))
    for s in (-1, 1):
        K.grille(a, (s * 2.92, .6, J_DECK + 1.05), 2.8, .75, facing=(s, 0, .12), slats=8, frame_mat='Team')
        K.smokestack(a, (s * 2.45, 3.55, J_DECK + 2.15), r=.27, h=1.2, mat='Steel')
        K.armour_plate(a, a.part('Plates', 'Armor'), (2.4, 1.5, .12), (s * 2.86, -2.25, J_DECK + 1.1),
                       rot=(0, s * 1.47, 0), rivet=.4)
        K.armour_plate(a, a.part('Plates', 'Armor'), (2.0, 1.0, .1), (s * 2.86, 3.2, J_DECK + 1.15),
                       rot=(0, s * 1.47, 0), rivet=.4)
    K.armour_plate(a, a.part('Plates', 'Armor'), (4.5, 1.6, .12), (0, -3.18, J_DECK + 1.1), rot=(R90 - .1, 0, 0),
                   rivet=.45)
    K.hatch_round(a, (-2.15, -2.6, J_DECK + 2.2), r=.42, periscopes=0, seg=12)
    wl = a.part('Kit_welds', 'Steel')
    for s in (-1, 1):
        K.weld(wl, [(s * 2.98, -3.35, J_DECK + .05), (s * 2.72, -3.0, J_DECK + 2.15)], r=.03)
        K.weld(wl, [(s * 2.98, 4.05, J_DECK + .05), (s * 2.72, 3.7, J_DECK + 2.15)], r=.03)
        K.rivet_line(a.part('Kit_rivets', 'Steel'), (s * 2.95, -3.0, J_DECK + .4), (s * 2.95, 3.7, J_DECK + .4),
                     (s, 0, .05), pitch=.3, r=.025)
    K.ladder(a.part('Ladders', 'Steel'), (2.25, -3.55, J_DECK), (2.25, -3.3, J_DECK + 2.2), width=.5, step=.35)
    k.lathe(a.part('Radar_mast', 'Steel'), [(.32, 6.2), (.32, 6.35), (.17, 6.45), (.15, 7.35), (.22, 7.42)],
            loc=(0, 4.25, 0), seg=12)
    for s in (-1, 1):
        a.part('Radar_mast', 'Steel').limb((s * .9, 3.7, 6.2), (0, 4.2, 7.0), .06, .06, bevel=0)
    r = a.pivot('Radar', (0, 4.25, 7.48))
    K.dish(a.part('Radar_dish', 'Medical', r), a.part('Radar_feed', 'Steel', r), (0, 0, .42), r=.8,
           normal=(0, -.6, .8), seg=18)
    a.part('Radar_drive', 'Armor', r).cyl(.24, .22, loc=(0, 0, .06), seg=12, bevel=.01)
    a.part('Radar_emitter', 'Energy', r).cyl(.09, .1, loc=(0, -.28, .78), seg=8, bevel=0)
    for x, y in ((1.75, -2.6), (-1.75, 3.1)):
        a.part('Vents', 'Steel').cyl(.18, .4, loc=(x, y, J_DECK + 2.4), seg=10, bevel=0)
        a.part('Vents', 'Armor').cyl(.28, .06, loc=(x, y, J_DECK + 2.62), r2=.18, seg=10, bevel=0)
    for s in (-1, 1):
        K.soot(a, (s * 2.45, 3.55, J_DECK + 3.35), radius=1.1, k=.5)


def _jotunn_turret(a):
    """The main turret (2A44 203 mm) on the Turret pivot: the faceted gun house with cheek plates, the long barrel
    with recoil cylinders and the brake (Main_cannon / Muzzle_brake, Muzzle_main), the loading tray, and the second
    gun on its roof mount (Mount_gun, its own house and barrel, Muzzle_gun), the cupola, hatches, antenna."""
    t = a.pivot('Turret', (0, 1.0, J_DECK + 2.25))
    K.turret_ring(a.part('Turret_steel', 'Steel', t), (0, 0, -.08), 2.35, h=.14)
    W.poly_turret(a.part('Turret_body', 'Team', t), [
        (0, [(-1.45, -2.35), (1.45, -2.35), (2.25, -1.25), (2.25, 2.45), (-2.25, 2.45), (-2.25, -1.25)]),
        (.75, [(-1.35, -2.5), (1.35, -2.5), (2.3, -1.35), (2.3, 2.5), (-2.3, 2.5), (-2.3, -1.35)]),
        (1.25, [(-1.12, -2.05), (1.12, -2.05), (2.0, -1.1), (2.0, 2.3), (-2.0, 2.3), (-2.0, -1.1)])], chamfer=.06)
    for s in (-1, 1):
        K.armour_plate(a, a.part('Turret_armor', 'Armor', t), (1.45, 1.05, .1), (s * 1.8, -1.9, .62),
                       rot=(0, 0, s * .9), rivet=.33)
        a.part('Turret_steel', 'Steel', t).cyl(.12, 2.1, loc=(s * .34, -3.0, .98), rot=K.FORWARD, seg=10, bevel=0)
        K.smoke_dischargers(a, 2.05, .3, .9, s, count=4, parent='Turret')
    K.chamfer_box(a.part('Turret_armor', 'Armor', t), (1.15, .75, .95), loc=(0, -2.55, .78), c=.06)
    K.gun_barrel(a, 'Main_cannon', t, 0, -2.9, .78, 4.25, .17, seg=16, extractor=(.3, 1.4, .65), brake='baffle')
    a.pivot('Muzzle_main', (0, -2.9 - 4.25 - .3, .78), t)
    tray = a.part('Turret_steel', 'Steel', t)
    for z in (.3, .82):
        tray.tube([(-1.95, 2.55, z), (-1.95, 3.05, z), (1.95, 3.05, z), (1.95, 2.55, z)], .035, seg=5)
    for x in (-1.95, -.97, 0, .97, 1.95):
        tray.tube([(x, 3.05, .3), (x, 3.05, .82)], .03, seg=5)
    for i in range(3):
        k.lathe(a.part('Ready_shells', 'Gilded', t), [(0, -.5), (.1, -.42), (.1, .35), (.07, .45), (0, .5)],
                loc=(-1.2 + i * .35, 2.8, .55), rot=(0, R90, 0), seg=8)
    # The second gun on the roof (Mount_gun).
    m = a.pivot('Mount_gun', (0, 1.1, 1.25), t)
    k.lathe(a.part('Gun2_base', 'Steel', m), [(.62, -.08), (.66, -.04), (.66, .06), (.6, .08)], seg=14)
    W.poly_turret(a.part('Gun2_house', 'Armor', m), [
        (.05, [(-.42, -.75), (.42, -.75), (.62, -.32), (.62, .72), (-.62, .72), (-.62, -.32)]),
        (.62, [(-.34, -.58), (.34, -.58), (.52, -.24), (.52, .64), (-.52, .64), (-.52, -.24)])], chamfer=.03)
    K.gun_barrel(a, 'Gun2_barrel', m, 0, -.75, .42, 2.45, .085, seg=12, extractor=(.4, 1.5, .32),
                 brake_name='Gun2_brake', brake='baffle')
    a.part('Gun2_sleeve', 'Canvas', m).cyl(.16, .22, loc=(0, -.8, .42), rot=K.FORWARD, seg=10, bevel=0)
    a.pivot('Muzzle_gun', (0, -.75 - 2.45 - .3, .42), m)
    k.ring(a.part('Cupola_top', 'Armor', t), [(.38, 0), (.46, 0), (.46, .24), (.38, .24)], loc=(-1.3, 1.6, 1.25),
           seg=14)
    K.hatch_round(a, (1.35, 1.6, 1.25), r=.4, parent=t, periscopes=2, seg=12, mat='Armor')
    a.part('Team_band', 'Team', t).box((2.6, 1.3, .02), loc=(0, -.4, 1.255), bevel=0)
    K.whip_antenna(a.part('Antenna', 'Steel', t), (-1.75, 2.1, 1.25), h=1.1, lean=.15)
    K.soot(a, (0, 1.0 - 7.4, J_DECK + 3.0), radius=1.2, k=.45)


def _jotunn_rear(a):
    """The rear deck: exactly two rocket launchers, one each side of the centre line (Mount_rocket left, .001 right:
    turntable, erector arms, the 12-tube 300 mm pod with its tube face), and between them the generator housing with
    its exhausts (no third launcher)."""
    for i, s in ((0, 1), (1, -1)):
        key = _n('Mount_rocket', i)
        m = a.pivot(key, (s * 2.15, 6.0, J_DECK + .3))
        k.lathe(a.part('Launcher_base', 'Steel'), [(.78, 0), (.82, .05), (.82, .22), (.76, .26)],
                loc=(s * 2.15, 6.0, J_DECK), seg=16)
        k.lathe(a.part('Launcher_turntable', 'Armor', m), [(.72, -.05), (.72, .12), (.6, .2), (0, .22)], seg=16)
        for sx in (-1, 1):
            k.block(a.part('Launcher_cheeks', 'Armor', m), (.12, 1.1, .7), loc=(sx * .62, .25, .15), chamfer=.03)
            a.part('Launcher_rams', 'Steel', m).tube([(sx * .5, .9, .2), (sx * .5, .35, 1.05)], .07, seg=8)
        rot = (-.42, 0, 0)
        mm = Matrix.Translation(Vector((0, .05, 1.1))) @ Matrix.Rotation(-.42, 4, 'X')
        k.block(a.part('Pod_box', 'Team', m), (1.62, 2.75, 1.18), loc=tuple(mm @ Vector((0, 0, -.58))), rot=rot,
                chamfer=.05)
        face = a.part('Tubes_bore', 'Undercarriage', m)
        rims = a.part('Pod_rims', 'Steel', m)
        for ix in range(4):
            for iz in range(3):
                p = mm @ Vector((-.54 + ix * .36, -1.385, -.6 + iz * .34))
                face.cyl(.135, .04, loc=tuple(p), rot=(R90 - .42, 0, 0), seg=10, bevel=0)
                rims.torus(.145, .022, loc=tuple(mm @ Vector((-.54 + ix * .36, -1.38, -.6 + iz * .34))),
                           rot=(R90 - .42, 0, 0), seg=10, ring=4)
        for f in (-.7, .5):
            a.part('Pod_straps', 'Steel', m).box((1.66, .08, 1.22), loc=tuple(mm @ Vector((0, f, -.58))), rot=rot,
                                                 bevel=0)
        a.part('Pod_hazard', 'SafetyStripe', m).box((1.4, .02, .1), loc=tuple(mm @ Vector((0, 1.385, -.2))), rot=rot,
                                                     bevel=0)
        tip = mm @ Vector((0, -1.41, -.6))
        a.pivot(_n('Muzzle_rocket', i), tuple(tip), key)
        K.tone(a, key, k=.93)
    gen = a.part('Generator', 'Armor')
    k.block(gen, (1.6, 2.6, 1.1), loc=(0, 6.1, J_DECK), chamfer=.08)
    K.grille(a, (0, 6.1, J_DECK + 1.12), 1.2, 2.0, facing=(0, 0, 1), slats=7, frame_mat='Team')
    for x in (-.45, .45):
        K.exhaust(a, (x, 7.3, J_DECK + 1.0), r=.09, length=.6, direction=(0, .3, 1), muffler=True)
        K.soot(a, (x, 7.5, J_DECK + 1.7), radius=.7, k=.45)
    a.part('Hazard_bands', 'Hazard').box((1.7, .04, .14), loc=(0, 7.42, J_DECK + .3), bevel=0)


def mobile_fortress(a):
    """Jotunn (see the module docstring). Runtime (the def's parts): Main_cannon / Muzzle_brake (howitzer),
    Mount_rocket / .001 (rockets_l / _r), Mount_mg / .001 (flak_l / _r), Radar (emp), Mount_gun on the turret roof
    (howitzer_2), Mount_missile.001 on the bridge roof (sam), Mount_missile / Muzzle_missile the bow 125 mm (part
    missiles); Turret, Muzzle_main; per-barrel muzzles on the flak twins."""
    K.suffixed(a)
    _jotunn_trucks(a)
    _jotunn_platform(a)
    _jotunn_bridge(a)
    _jotunn_core(a)
    _jotunn_turret(a)
    _jotunn_rear(a)
    k.clean(a)


# ============================================================================= fenrir
F_FRONT = (-7.85, -.95)      # the front unit's ends
F_REAR = (.6, 7.75)          # the rear unit's ends
F_DECK = 2.42


def _fenrir_running_gear(a):
    """Two track pairs, one under each unit (DT-30 style: wide belts, small road wheels, skirt-less), mudguards
    with snow caked on them, the articulation joint (yoke, rams, bellows) between the units."""
    for wheels, idler, sprocket in (([-6.85 + i * .98 for i in range(6)], (-7.45, .64, .4), (-1.4, .66, .42)),
                                    ([1.25 + i * .98 for i in range(6)], (7.3, .64, .4), (1.0, .66, .42))):
        W.running_gear(a, 1.95, 1.05, .42, wheels, idler, sprocket, rollers=(), roller_z=None, disc_mat='Armor',
                       seg=16, link_pitch=.26, wheel_w=.26, dust=.3, teeth=12, top_hidden=1.0)
    for y0, y1 in (F_FRONT, F_REAR):
        for s in (-1, 1):
            K.fender(a.part('Mudguards', 'Team'), 1.95, y0 + .1, y1 - .1, 1.32, 1.3, s, lip=.2)
            for j in range(3):
                y = y0 + (j + .5) * (y1 - y0) / 3
                a.part('Snow_caps', 'Snow').box((1.0, 1.4 + j * .3, .08), loc=(s * 1.95, y, 1.36), taper=(.8, .85),
                                                bevel=.03)
            K.dust(a, (s * 1.95, (y0 + y1) / 2, .2), radius=3.0, k=.2)
    # The articulation unit: a steel yoke from each hull, the turntable, two steering rams, the rubber bellows.
    j = a.part('Coupling', 'Steel')
    k.block(j, (1.4, 1.0, .5), loc=(0, -1.1, .95), chamfer=.04)
    k.block(j, (1.4, 1.0, .5), loc=(0, .65, .95), chamfer=.04)
    k.lathe(a.part('Coupling_ring', 'Armor'), [(.6, 0), (.62, .05), (.62, .3), (.55, .34)], loc=(0, -.25, .92),
            seg=16)
    for s in (-1, 1):
        a.part('Coupling_rams', 'Steel').tube([(s * .85, -1.4, 1.25), (s * .75, .9, 1.25)], .08, seg=8)
        a.part('Coupling_rams', 'Undercarriage').tube([(s * .85, -1.4, 1.25), (s * .82, -.5, 1.25)], .11, seg=8)
    k.lathe(a.part('Bellows', 'Rubber'), [(.75, -.62), (.85, -.5), (.75, -.38), (.85, -.25), (.75, -.12), (.85, 0),
                                          (.75, .12), (.85, .25), (.75, .38), (.85, .5), (.75, .62)],
            loc=(0, -.17, 1.9), rot=(R90, 0, 0), seg=14, caps=(False, False))


def _fenrir_front(a):
    """The front unit: the lofted hull over its tracks, the cab with the raked wrap-round windscreen, doors, lamps,
    the bull bar and winch, the engine deck with grilles and exhausts, and the twin 35 mm flak turret on its
    barbette (Mount_mg, Muzzle_mg with the per-barrel muzzles) with the fire-control radar on its back."""
    K.section_loft(a.part('Hull', 'Team'), [
        (-7.95, [(0, 1.3), (2.15, 1.3), (2.35, 1.65), (2.1, 2.05), (0, 2.1)]),
        (-7.35, [(0, 1.1), (2.6, 1.1), (2.7, 1.75), (2.58, F_DECK), (0, F_DECK)]),
        (-1.35, [(0, 1.1), (2.6, 1.1), (2.7, 1.75), (2.58, F_DECK), (0, F_DECK)]),
        (-.95, [(0, 1.2), (2.3, 1.2), (2.4, 1.75), (2.25, 2.3), (0, 2.32)])])
    cab = a.part('Cab', 'Team')
    W.poly_turret(cab, [(F_DECK - .05, [(-2.45, -7.35), (2.45, -7.35), (2.55, -6.6), (2.55, -4.2), (-2.55, -4.2),
                                        (-2.55, -6.6)]),
                        (F_DECK + .6, [(-2.4, -7.5), (2.4, -7.5), (2.55, -6.7), (2.55, -4.2), (-2.55, -4.2),
                                       (-2.55, -6.7)]),
                        (F_DECK + 1.7, [(-2.1, -6.75), (2.1, -6.75), (2.35, -6.2), (2.35, -4.35), (-2.35, -4.35),
                                        (-2.35, -6.2)])], chamfer=.06)
    glass = a.part('Windows', 'Glass')
    frames = a.part('Window_frames', 'Armor')
    z0, z1 = F_DECK + .68, F_DECK + 1.6
    for i in range(4):
        x = -1.5 + i * 1.0
        glass.mesh([(x - .44, -7.53, z0), (x + .44, -7.53, z0), (x + .4, -6.82, z1), (x - .4, -6.82, z1)],
                   [(0, 1, 2, 3)])
        if i < 3:
            frames.box((.08, .1, 1.15), loc=(x + .5, -7.18, (z0 + z1) / 2), rot=(-.79, 0, 0), bevel=0)
        a.part('Wipers', 'Undercarriage').limb((x, -7.5, z0 + .05), (x + .2, -7.2, z0 + .45), .025, .025, bevel=0)
    for s in (-1, 1):
        glass.mesh([(s * 2.43, -7.3, z0), (s * 2.57, -6.6, z0), (s * 2.37, -6.25, z1), (s * 2.12, -6.72, z1)],
                   [(0, 1, 2, 3) if s > 0 else (3, 2, 1, 0)])
        K.door(a, (s * 2.56, -5.3, F_DECK + .15), size=(.9, 1.4), normal=(s, 0, 0))
        a.part('Windows', 'Glass').box((.02, .6, .45), loc=(s * 2.57, -5.3, F_DECK + 1.15), bevel=0)
        K.mirror(a.part('Mirrors', 'Steel'), (s * 2.55, -7.0, F_DECK + 1.2), s)
        K.lamp(a, (s * 1.85, -7.98, 1.8), (0, -1, 0), r=.15)
        K.lamp(a, (s * 1.2, -6.85, F_DECK + 1.72), (0, -1, 0), r=.1, guard=False)
    frames.box((5.0, .12, .1), loc=(0, -7.52, z0 - .06), bevel=0)
    a.part('Sun_visor', 'Armor').box((4.4, .45, .05), loc=(0, -6.85, F_DECK + 1.73), rot=(.12, 0, 0), bevel=0)
    a.part('Cab_roof', 'Medical').box((3.9, 2.0, .04), loc=(0, -5.5, F_DECK + 1.72), bevel=0)
    K.hatch_round(a, (.9, -5.0, F_DECK + 1.72), r=.36, periscopes=0, seg=12)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-1.9, -4.6, F_DECK + 1.72), h=2.4, r=.03, lean=.08)
    K.whip_antenna(a.part('Antennas', 'Steel'), (1.9, -4.6, F_DECK + 1.72), h=1.6, r=.03, lean=.08)
    K.beacon(a, (-.6, -4.7, F_DECK + 1.72), r=.12)
    # The V snow plough on the bow (its push arms and rams), the winch above it, tow hooks.
    pl = a.part('Plough', 'Armor')
    k.extrude(pl, [(-2.55, -8.05), (0, -8.75), (2.55, -8.05), (2.55, -7.9), (0, -8.58), (-2.55, -7.9)], .95,
              loc=(0, 0, .72), axis='Z', chamfer=.03)
    haz = a.part('Plough_stripes', 'SafetyStripe')
    for s in (-1, 1):
        for j in range(3):
            x = s * (.45 + j * .75)
            yy = -8.75 + abs(x) * .7 / 2.55
            haz.box((.32, .03, .2), loc=(x, yy - .03, .95), rot=(0, .6 * s, -s * .27), bevel=0)
        a.part('Plough_arms', 'Steel').limb((s * 1.6, -8.25, .6), (s * 1.6, -7.6, .95), .14, .16, bevel=.01)
        a.part('Plough_arms', 'Steel').tube([(s * .8, -8.45, 1.05), (s * .9, -7.75, 1.5)], .07, seg=8)
        a.part('Snow_caps', 'Snow').box((1.6, .35, .1), loc=(s * 1.1, -8.25, 1.2), rot=(0, 0, -s * .27),
                                        taper=(.8, .7), bevel=.03)
    pl.box((5.15, .07, .12), loc=(0, -8.0, .3), bevel=0)
    a.part('Winch', 'CraneYellow').cyl(.2, 1.0, loc=(0, -7.98, 1.62), rot=(0, R90, 0), seg=12, bevel=.02)
    W.tow_set(a, -7.98, 1.3, 1.3, (0, -1, 0))
    # Riveted side plates and stowage bins along the front unit, the roof rack on the cab.
    for s in (-1, 1):
        for j in range(3):
            K.armour_plate(a, a.part('Side_plates', 'Armor'), (1.25, .55, .07), (s * 2.67, -3.75 + j * 1.3, 2.0),
                           rot=(0, s * R90, 0), rivet=.3)
        K.crate(a.part('Bins', 'Crate'), a.part('Kit_latches', 'Steel'), (.38, 1.1, .5), (s * 2.75, -1.75, 1.75),
                bands=1)
    rack = a.part('Roof_rack', 'Steel')
    rack.tube([(-1.6, -6.3, F_DECK + 1.95), (1.6, -6.3, F_DECK + 1.95), (1.6, -4.6, F_DECK + 1.95),
               (-1.6, -4.6, F_DECK + 1.95), (-1.6, -6.3, F_DECK + 1.95)], .03, seg=5)
    for x in (-1.6, 1.6):
        for y in (-6.3, -4.6):
            rack.tube([(x, y, F_DECK + 1.72), (x, y, F_DECK + 1.95)], .03, seg=5)
    K.crate(a.part('Bins', 'Crate'), a.part('Kit_latches', 'Steel'), (1.2, .7, .4), (-.6, -5.6, F_DECK + 1.74),
            bands=2)
    for j in range(2):
        K.jerrycan(a.part('Jerrycans', 'Fuel'), (.9 + j * .35, -5.9, F_DECK + 1.74))
    a.part('Snow_caps', 'Snow').box((2.6, 1.0, .07), loc=(.3, -5.2, F_DECK + 1.79), taper=(.85, .8), bevel=.03)
    # The engine deck behind the cab: grilles, exhaust stacks, the turret barbette.
    for s in (-1, 1):
        K.grille(a, (s * 1.75, -2.4, F_DECK + .02), .9, 2.2, facing=(0, 0, 1), slats=7, frame_mat='Team')
        K.exhaust(a, (s * 2.2, -3.95, F_DECK + .1), r=.1, length=1.1, direction=(0, .1, 1), muffler=True)
        K.soot(a, (s * 2.2, -3.9, F_DECK + 1.3), radius=.8, k=.45)
    k.lathe(a.part('Barbette', 'Armor'), [(.95, 0), (.95, .38), (.88, .44)], loc=(0, -2.55, F_DECK), seg=18,
            worn=(1,))
    key = 'Mount_mg'
    m = a.pivot(key, (0, -2.55, F_DECK + .44))
    K.turret_ring(a.part('Flak_ring', 'Steel', m), (0, 0, -.02), .86, h=.1)
    W.poly_turret(a.part('Flak_house', 'Team', m), [
        (0, [(-.55, -.9), (.55, -.9), (.85, -.45), (.85, .75), (-.85, .75), (-.85, -.45)]),
        (.55, [(-.5, -.95), (.5, -.95), (.85, -.48), (.85, .8), (-.85, .8), (-.85, -.48)]),
        (.85, [(-.38, -.7), (.38, -.7), (.66, -.36), (.66, .68), (-.66, .68), (-.66, -.36)])], chamfer=.04)
    for s in (-1, 1):
        k.block(a.part('Flak_pods', 'Armor', m), (.28, 1.1, .4), loc=(s * 1.0, -.15, .2), chamfer=.04)
        K.gun_barrel(a, 'Flak_barrels', key, s * 1.0, -.7, .4, 2.0, .045, seg=8, extractor=(.3, 1.8, .35),
                     brake_name=None)
        k.lathe(a.part('Flak_flash', 'Undercarriage', m), [(.055, 0), (.075, .26), (.055, .28), (0, .28)],
                loc=(s * 1.0, -.7 - 2.0 - .28, .4), rot=K.BACKWARD, seg=8)
    mk = a.pivot('Muzzle_mg', (0, -.7 - 2.0 - .3, .4), key)
    _per_barrel(a, mk, 'mg', (-1.0, 1.0))
    k.block(a.part('Flak_radar', 'Armor', m), (.7, .1, .5), loc=(0, .85, .95), rot=(.2, 0, 0), chamfer=.02)
    a.part('Flak_radar_face', 'Undercarriage', m).box((.6, .02, .4), loc=(0, .79, 1.0), rot=(.2, 0, 0), bevel=0)
    a.part('Flak_radar_post', 'Steel', m).cyl(.06, .3, loc=(0, .85, .7), seg=8, bevel=0)
    a.part('Flak_glass', 'Glass', m).box((.34, .02, .1), loc=(.35, -.83, .62), rot=(-.5, 0, 0), bevel=0)
    K.tone(a, key, k=.93)


def _fenrir_rear(a):
    """The rear unit: its lofted hull, the two 300 mm rocket pods side by side (Mount_rocket left, .001 right: a
    turntable, the erector and a six-tube pod with its tube face, Muzzle_rocket at the face), the target-marking
    radar on its folding mast (Radar spins), stowage, rails, tail lamps."""
    K.section_loft(a.part('Hull_rear', 'Team'), [
        (.55, [(0, 1.2), (2.3, 1.2), (2.4, 1.75), (2.25, 2.3), (0, 2.32)]),
        (.95, [(0, 1.1), (2.6, 1.1), (2.7, 1.75), (2.58, F_DECK), (0, F_DECK)]),
        (7.3, [(0, 1.1), (2.6, 1.1), (2.7, 1.75), (2.58, F_DECK), (0, F_DECK)]),
        (7.85, [(0, 1.3), (2.3, 1.3), (2.45, 1.7), (2.3, 2.15), (0, 2.2)])])
    dp = a.part('Deck', 'Armor')
    for y in (1.55, 6.55):
        K.panel(a, dp, (4.6, .9), (0, y, F_DECK), (0, 0, 1), t=.04, rivet=.4)
    for i, s in ((0, 1), (1, -1)):
        key = _n('Mount_rocket', i)
        m = a.pivot(key, (s * 1.22, 3.8, F_DECK + .22))
        k.lathe(a.part('Launcher_base', 'Steel'), [(.62, 0), (.66, .05), (.66, .2), (.6, .24)],
                loc=(s * 1.22, 3.8, F_DECK), seg=16)
        k.lathe(a.part('Launcher_turntable', 'Armor', m), [(.58, -.04), (.58, .1), (.48, .17), (0, .19)], seg=16)
        k.block(a.part('Launcher_cradle', 'Armor', m), (.85, 1.2, .5), loc=(0, .4, .05), chamfer=.04)
        mm = Matrix.Translation(Vector((0, .15, .85))) @ Matrix.Rotation(-.35, 4, 'X')
        k.block(a.part('Pod_box', 'Team', m), (1.02, 3.0, .74), loc=tuple(mm @ Vector((0, 0, -.37))), rot=(-.35, 0, 0),
                chamfer=.05)
        face = a.part('Tubes_bore', 'Undercarriage', m)
        rims = a.part('Pod_rims', 'Steel', m)
        for ix in range(3):
            for iz in range(2):
                p = mm @ Vector((-.3 + ix * .3, -1.51, -.54 + iz * .34))
                face.cyl(.13, .04, loc=tuple(p), rot=(R90 - .35, 0, 0), seg=10, bevel=0)
                rims.torus(.14, .022, loc=tuple(p), rot=(R90 - .35, 0, 0), seg=10, ring=4)
        for f in (-.9, .2, 1.1):
            a.part('Pod_straps', 'Steel', m).box((1.06, .08, .78), loc=tuple(mm @ Vector((0, f, -.37))),
                                                 rot=(-.35, 0, 0), bevel=0)
        a.part('Launcher_rams', 'Steel', m).tube([(0, .9, .1), (0, .45, .62)], .07, seg=8)
        a.pivot(_n('Muzzle_rocket', i), tuple(mm @ Vector((0, -1.53, -.37))), key)
        a.part('Pod_snow', 'Snow', m).box((.9, 2.2, .06), loc=tuple(mm @ Vector((0, .2, .02))), rot=(-.35, 0, 0),
                                          taper=(.85, .9), bevel=.02)
        K.tone(a, key, k=.93)
    # The folding radar mast at the stern (the target-marking radar the card names).
    k.block(a.part('Mast_base', 'Armor'), (1.0, 1.0, .5), loc=(0, 6.75, F_DECK), chamfer=.05)
    k.lathe(a.part('Mast', 'Steel'), [(.16, 0), (.16, 1.3), (.12, 1.35), (.12, 2.1), (.18, 2.15), (.18, 2.2)],
            loc=(0, 6.75, F_DECK + .5), seg=10)
    a.part('Mast', 'Steel').tube([(0, 7.2, F_DECK + .5), (0, 6.8, F_DECK + 1.7)], .05, seg=6)
    r = a.pivot('Radar', (0, 6.75, F_DECK + 2.75))
    k.block(a.part('Radar_array', 'Armor', r), (1.8, .22, .62), loc=(0, 0, -.05), chamfer=.04)
    a.part('Radar_face', 'Undercarriage', r).box((1.62, .02, .5), loc=(0, -.12, .26), bevel=0)
    a.part('Radar_drive', 'Steel', r).cyl(.15, .16, loc=(0, 0, -.12), seg=10, bevel=0)
    # Stowage, rails, lamps, jerrycans, spare links, a tarpaulin bundle.
    rails = a.part('Railings', 'Steel')
    for s in (-1, 1):
        K.railing(rails, [(s * 2.5, 1.2, F_DECK), (s * 2.5, 2.4, F_DECK)], h=.6, post=1.2, r=.03)
        K.lamp(a, (s * 1.9, 7.88, 1.85), (0, 1, 0), r=.11, glow='LavaGlow', guard=False)
        for j in range(3):
            K.jerrycan(a.part('Jerrycans', 'Fuel'), (s * 2.66, 5.4 + j * .42, 1.55), rot=(0, 0, R90))
        a.part('Jerry_rack', 'Steel').box((.08, 1.4, .05), loc=(s * 2.72, 5.82, 1.3), bevel=0)
        K.crate(a.part('Stowage', 'Crate'), a.part('Kit_latches', 'Steel'), (.55, 1.4, .5), (s * 2.0, 6.1, F_DECK),
                bands=2)
    K.net_roll(a.part('Stowage', 'Canvas'), a.part('Kit_straps', 'Undercarriage'), (0, 1.6, F_DECK + .22),
               length=2.6, r=.2)
    for s in (-1, 1):
        for j in range(3):
            K.armour_plate(a, a.part('Side_plates', 'Armor'), (1.3, .55, .07), (s * 2.67, 1.6 + j * 1.4, 2.0),
                           rot=(0, s * R90, 0), rivet=.3)
        a.part('Team_band', 'Team').box((.03, 5.6, .16), loc=(s * 2.72, 4.2, 1.5), bevel=0)
        for y in (2.0, 4.4):
            a.part('Tool_racks', 'Steel').box((.06, 1.3, .05), loc=(s * 2.75, y, 1.4), bevel=0)
            a.part('Tools', 'Wood').limb((s * 2.8, y - .6, 1.42), (s * 2.8, y + .6, 1.42), .06, .06, bevel=0)
    for j in range(4):
        a.part('Spare_links', 'Undercarriage').box((.95, .24, .06), loc=(0, 7.82, 1.4 + j * .2), rot=(R90 - .2, 0, 0),
                                                   bevel=0)
    W.tow_set(a, 7.86, 1.25, 1.2, (0, 1, 0))
    K.hatch_rect(a, (0, 7.86, 1.9), (.9, .5), normal=(0, 1, .4))


def _fenrir_kit(a):
    rv = a.part('Kit_rivets', 'Steel')
    for s in (-1, 1):
        for y0, y1 in ((-7.2, -1.4), (1.0, 7.2)):
            K.rivet_line(rv, (s * 2.7, y0, 1.6), (s * 2.7, y1, 1.6), (s, 0, 0), pitch=.28, r=.022)
            K.rivet_line(rv, (s * 2.6, y0, F_DECK - .05), (s * 2.6, y1, F_DECK - .05), (s, 0, .2), pitch=.28, r=.022)
        K.rivet_line(rv, (s * 2.56, -7.2, F_DECK + .35), (s * 2.56, -4.3, F_DECK + .35), (s, 0, 0), pitch=.25, r=.02)
    k.lathe(a.part('Fuel_cell', 'Fuel'), [(0, -.75), (.32, -.7), (.36, -.5), (.36, .5), (.32, .7), (0, .75)],
            loc=(-2.95, -2.6, 1.95), rot=K.FORWARD, seg=12)
    for f in (-.4, .4):
        a.part('Fuel_cell_straps', 'Steel').torus(.37, .025, loc=(-2.95, -2.6 + f, 1.95), rot=(R90, 0, 0), seg=12, ring=3)
    a.part('Fuel_cell_bracket', 'Steel').box((.4, 1.4, .06), loc=(-2.85, -2.6, 1.58), bevel=0)
    k.lathe(a.part('Spare_track_roll', 'Undercarriage'), [(.25, -.5), (.45, -.5), (.45, .5), (.25, .5)],
            loc=(3.05, 5.0, 1.75), rot=(0, R90, 0), seg=14)
    a.part('Spare_track_roll', 'Steel').box((.5, .7, .06), loc=(2.95, 5.0, 1.27), bevel=0)
    K.floodlight(a, (2.3, 2.5, F_DECK), facing=(1, -.4, -.2), pole=1.3)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-2.2, 7.2, F_DECK), h=2.2, r=.03, lean=.1)


def fenrir(a):
    """Fenrir (see the module docstring). Runtime (the def keeps rockets_l / rockets_r / flak_l of mobile_fortress):
    Mount_rocket / .001 + Muzzle_rocket / .001 (the pods), Mount_mg + Muzzle_mg (the flak twin, per-barrel muzzles),
    Radar (spins). No Main_cannon, Mount_gun, Mount_mg.001 or Mount_missile.001 (the parts it drops are hidden by
    those names)."""
    K.suffixed(a)
    _fenrir_running_gear(a)
    _fenrir_front(a)
    _fenrir_rear(a)
    _fenrir_kit(a)
    k.clean(a)


# ============================================================================= behemoth_inferno
IN_TURRET = (0.0, .4, 3.05)
IN_SUPER = 2.98          # the superstructure roof the turret turns on


def _inferno_hull(a):
    """The Behemoth's frame, smaller: two track units a side (the inner pair under the hull, the outer pair under
    the armoured skirts), the wide low hull with the sloped glacis, the raised superstructure carrying the turret
    ring, fenders, the glacis plates, hatches, vision blocks, lamps, the searchlight, tow gear."""
    wheels = [-4.1 + i * 1.08 for i in range(8)]
    for tx in (1.75, 2.85):
        W.running_gear(a, tx, .8, .42, wheels, (-5.0, .6, .36), (4.6, .64, .38), rollers=(-2.0, .2, 2.4),
                       roller_z=1.0, top_hidden=.95, disc_mat='Armor', seg=16, link_pitch=.32, wheel_w=.22, dust=.24,
                       teeth=11)
    K.section_loft(a.part('Hull', 'Team'), [
        (-5.75, [(0, .95), (1.0, .95), (1.1, 1.12), (2.5, 1.12), (2.7, 1.35), (2.55, 1.55), (0, 1.62)]),
        (-4.7, [(0, .75), (1.2, .75), (1.3, 1.08), (3.15, 1.08), (3.35, 1.5), (3.2, 2.15), (0, 2.3)]),
        (4.4, [(0, .75), (1.2, .75), (1.3, 1.08), (3.15, 1.08), (3.35, 1.5), (3.2, 2.3), (0, 2.42)]),
        (5.45, [(0, .95), (1.0, .95), (1.1, 1.12), (2.85, 1.12), (3.05, 1.4), (2.95, 2.1), (0, 2.18)])])
    # The raised superstructure (sloped walls) under the turret.
    sup = a.part('Superstructure', 'Armor')
    k.extrude(sup, [(-2.35, -2.6), (2.35, -2.6), (2.35, 2.75), (-2.35, 2.75)], IN_SUPER - 2.2, loc=(0, .1,
              (IN_SUPER + 2.2) / 2), axis='Z', chamfer=.07, corner=.25, taper=(.9, .94))
    K.turret_ring(a.part('Ring', 'Steel'), (IN_TURRET[0], IN_TURRET[1], IN_SUPER - .02), 1.95, h=.12)
    # Armoured skirts with rubber flaps, the fenders, the team band.
    for s in (-1, 1):
        for j in range(6):
            yc = -4.35 + (j + .5) * 1.45
            K.armour_plate(a, a.part('Skirts', 'Armor'), (1.4, .72, .08), (s * 3.42, yc, 1.0), rot=(0, s * R90, 0),
                           rivet=.42)
            a.part('Skirt_edge', 'Rubber').box((.05, 1.38, .14), loc=(s * 3.44, yc, .56), bevel=0)
        a.part('Team_band', 'Team').box((.03, 7.6, .22), loc=(s * 3.37, -.1, 1.75), rot=(0, s * .3, 0), bevel=0)
        K.lamp(a, (s * 2.1, -5.8, 1.35), (0, -1, .1), r=.13, guard=True)
        a.part('Tail_lights', 'LavaGlow').box((.2, .03, .1), loc=(s * 2.3, 5.5, 1.75), bevel=0)
    # Glacis: composite modules, the driver's hatches and vision blocks, the searchlight, chevrons, tow hooks.
    for i in range(4):
        K.armour_plate(a, a.part('Armor', 'Armor'), (1.08, .95, .12), (-1.65 + i * 1.1, -5.22, 1.85),
                       rot=(-1.1, 0, 0), rivet=.38)
    for x in (-1.45, 1.45):
        K.hatch_round(a, (x, -4.3, 2.3), r=.34, periscopes=2, seg=12)
        a.part('Vision_blocks', 'Glass').box((.42, .03, .09), loc=(x, -4.66, 2.28), rot=(-.4, 0, 0), bevel=0)
    k.lathe(a.part('Searchlight', 'Armor'), [(.18, -.16), (.2, .13), (.15, .18)], loc=(2.35, -4.75, 2.32),
            rot=K.FORWARD, seg=12)
    a.part('Lamps', 'Lamp').cyl(.16, .02, loc=(2.35, -4.92, 2.32), rot=K.FORWARD, seg=12, bevel=0)
    chev = a.part('Glacis_chevrons', 'SafetyStripe')
    for i in range(4):
        chev.box((.45, .04, .14), loc=(-1.2 + i * .8, -5.78, 1.3), rot=(0, .6, 0), bevel=0)
    W.tow_set(a, -5.8, 1.05, 1.3, (0, -1, 0))
    W.tow_set(a, 5.5, 1.1, 1.3, (0, 1, 0))
    # Heat shields and the scorched glacis under the projectors.
    for x in (-.45, .45):
        K.soot(a, (x, -5.2, 2.0), radius=1.1, k=.45)
    for s in (-1, 1):
        K.periscope(a, (s * 1.9, -2.55, IN_SUPER), facing=(0, -1, 0), size=(.28, .22, .2))
        K.grille(a, (s * 2.3, 1.0, 2.6), 2.2, .45, facing=(s, 0, .3), slats=6, frame_mat='Team')


def _inferno_turret(a):
    """The main turret on the Turret pivot (the Behemoth's long faceted house, smaller): the cheek blocks, the
    mantlet and the twin flame projectors, thinner than the Behemoth's 152 mm pair (Main_cannon right, Main_cannon_2
    left, each with its _jacket and _hose; Muzzle_brake[_2] the nozzle with _glow and _pilot), Muzzle_main between
    them, the flak mount on the roof (Mount_mg, Muzzle_mg, per-barrel muzzles), cupola, sight, bustle rack."""
    t = a.pivot('Turret', IN_TURRET)
    K.turret_ring(a.part('Turret_steel', 'Steel', t), (0, 0, -.1), 1.95, h=.12)
    W.poly_turret(a.part('Turret_body', 'Team', t), [
        (0, [(-1.05, -2.2), (1.05, -2.2), (1.95, -1.2), (2.0, 1.75), (1.6, 2.3), (-1.6, 2.3), (-2.0, 1.75),
             (-1.95, -1.2)]),
        (.55, [(-.98, -2.38), (.98, -2.38), (2.05, -1.28), (2.1, 1.8), (1.7, 2.38), (-1.7, 2.38), (-2.1, 1.8),
               (-2.05, -1.28)]),
        (.95, [(-.8, -1.9), (.8, -1.9), (1.72, -1.05), (1.76, 1.62), (1.45, 2.12), (-1.45, 2.12), (-1.76, 1.62),
               (-1.72, -1.05)])], chamfer=.05)
    for s in (-1, 1):
        W.poly_turret(a.part('Turret_armor', 'Armor', t), [
            (.05, [(s * 1.1, -2.25), (s * 2.0, -1.25), (s * 2.0, -.75), (s * 1.22, -1.6)]),
            (.88, [(s * 1.02, -2.28), (s * 2.07, -1.32), (s * 2.07, -.75), (s * 1.15, -1.65)])], chamfer=.02)
        K.smoke_dischargers(a, 1.95, .2, .7, s, count=3, parent='Turret')
    K.chamfer_box(a.part('Gun_mantlet', 'Armor', t), (1.55, .5, .72), loc=(0, -2.45, .48), c=.06)
    y0, y1, z = -2.68, -5.9, .5
    for x, n in ((-.45, ''), (.45, '_2')):
        L = y0 - y1
        k.lathe(a.part(f'Main_cannon{n}', 'Steel', t), [(.1, 0), (.1, .08), (.075, .12), (.075, L - .3), (.085, L - .26),
                                                        (.085, L)], loc=(x, y0, z), rot=K.FORWARD, seg=12, worn=(1,))
        k.lathe(a.part(f'Main_cannon{n}_jacket', 'Armor', t), [(.15, 0), (.17, .05), (.17, 1.3), (.15, 1.38),
                                                               (.09, 1.42)], loc=(x, y0, z), rot=K.FORWARD, seg=12,
                worn=(2,))
        for f in (.55, .9):
            a.part(f'Main_cannon{n}_jacket', 'Armor', t).torus(.1, .02, loc=(x, y0 - L * f, z), rot=(R90, 0, 0),
                                                              seg=10, ring=4)
        a.part(f'Main_cannon{n}_hose', 'Rubber', t).tube([(x, y0 + .45, z + .32), (x, y0 - .2, z + .24),
                                                           (x, y1 + 1.0, z + .17)], .045, seg=6)
        k.lathe(a.part(f'Muzzle_brake{n}', 'Charred', t), [(.09, 0), (.14, .07), (.16, .26), (.12, .33),
                                                           (.065, .35)], loc=(x, y1, z), rot=K.FORWARD, seg=12)
        a.part(f'Muzzle_brake{n}_glow', 'LavaGlow', t).cyl(.07, .02, loc=(x, y1 - .36, z), rot=K.FORWARD, seg=10,
                                                            bevel=0)
        a.part(f'Muzzle_brake{n}_pilot', 'Steel', t).tube([(x, y1 + .9, z - .17), (x, y1 - .08, z - .17)], .022,
                                                           seg=5)
        a.part(f'Muzzle_brake{n}_glow', 'LavaGlow', t).cyl(.034, .04, loc=(x, y1 - .12, z - .17), rot=K.FORWARD,
                                                            seg=6, bevel=0)
        for f in (.35, .65):
            a.part('Heat_shields', 'Steel', t).box((.3, .5, .025), loc=(x, y1 + (y0 - y1) * f, z + .16), bevel=0)
    a.pivot('Muzzle_main', (0, y1 - .36, z), 'Turret')
    # The fuel feed manifold on the turret's back.
    k.block(a.part('Feed_manifold', 'Steel', t), (1.2, .4, .3), loc=(0, 2.1, .4), chamfer=.03)
    # The flak mount on the roof, right (Mount_mg).
    key = 'Mount_mg'
    m = a.pivot(key, (-.85, .7, .95), t)
    k.lathe(a.part('AA_mount', 'Armor', m), [(.4, 0), (.4, .08), (.3, .14), (.28, .28)], seg=12)
    k.block(a.part('AA_shield', 'Team', m), (.72, .08, .42), loc=(0, -.34, .4), rot=(-.2, 0, 0), chamfer=.015)
    for dx in (-.1, .1):
        k.lathe(a.part('AA_guns', 'Steel', m), [(.038, 0), (.038, .25), (.03, .28), (.03, 1.3), (.042, 1.33),
                                                (.042, 1.42), (0, 1.43)], loc=(dx, -.12, .4), rot=K.FORWARD, seg=8)
    K.chamfer_box(a.part('AA_ammo', 'Crate', m), (.22, .38, .28), loc=(.28, .14, .38), c=.02)
    mk = a.pivot('Muzzle_mg', (0, -1.55, .4), key)
    _per_barrel(a, mk, 'mg', (-.1, .1))
    # Cupola, sight, hatch, bustle rack with stowage, antennas.
    k.ring(a.part('Cupola_top', 'Armor', t), [(.34, 0), (.42, 0), (.42, .22), (.34, .22)], loc=(.95, .65, .95),
           seg=14)
    K.hatch_round(a, (.95, .65, 1.15), r=.32, parent=t, periscopes=0, seg=12)
    K.chamfer_box(a.part('Sight', 'Armor', t), (.36, .4, .32), loc=(1.15, -1.25, 1.08), c=.04)
    a.part('Periscope', 'Glass', t).box((.26, .01, .14), loc=(1.15, -1.46, 1.1), bevel=0)
    rk = a.part('Turret_steel', 'Steel', t)
    for zz in (.28, .72):
        rk.tube([(-1.6, 2.35, zz), (-1.6, 2.75, zz), (1.6, 2.75, zz), (1.6, 2.35, zz)], .03, seg=5)
    for x in (-1.6, -.8, 0, .8, 1.6):
        rk.tube([(x, 2.75, .28), (x, 2.75, .72)], .028, seg=5)
    K.net_roll(a.part('Stowage', 'Canvas', t), a.part('Kit_straps', 'Undercarriage', t), (-.6, 2.55, .45),
               length=1.4, r=.18)
    for x in (-1.5, 1.5):
        K.whip_antenna(a.part('Antennas', 'Steel', t), (x, 1.9, .95), h=1.1, lean=.15)
    K.soot(a, (0, IN_TURRET[1] + y1, IN_TURRET[2] + z), radius=1.4, k=.5)


def _inferno_glacis(a):
    """The 125 mm thermobaric gun turret on the glacis (Mount_rocket, part thermo): the barbette, a cast low dome,
    the autoloader bustle, the mantlet, the short heavy barrel (sleeve, extractor, reference collar), sights;
    Muzzle_rocket at the mouth."""
    a.part('Gun_barbette', 'Armor').cyl(.82, .42, loc=(0, -3.4, 2.15), seg=20, bevel=.02)
    K.bolt_ring(a.part('Gun_barbette_bolts', 'Steel'), (0, -3.4, 2.365), (0, 0, 1), .76, 14, r=.02, h=.02)
    m = a.pivot('Mount_rocket', (0, -3.4, 2.38))
    K.turret_ring(a.part('Thermo_ring', 'Steel', m), (0, 0, -.03), .74, h=.09)
    k.lathe(a.part('Thermo_house', 'Team', m), [(.76, 0), (.78, .08), (.74, .28), (.6, .46), (.36, .57), (0, .6)],
            loc=(0, .05, .02), seg=20, worn=(1, 2))
    k.extrude(a.part('Thermo_bustle', 'Armor', m), [(-.48, .42), (.48, .42), (.4, 1.05), (-.4, 1.05)], .38,
              loc=(0, 0, .1), axis='Z', chamfer=.04, corner=.06)
    mant = a.part('Thermo_mantlet', 'Armor', m)
    mant.cyl(.22, .58, loc=(0, -.76, .34), rot=(0, R90, 0), seg=14, bevel=.02)
    k.block(mant, (.6, .3, .38), loc=(0, -.62, .32), chamfer=.05)
    K.gun_barrel(a, 'Thermo_barrel', 'Mount_rocket', 0, -.96, .34, 1.6, .105, seg=14, extractor=(.42, 1.5, .38),
                 brake_name='Thermo_collar', brake='collar', sleeve=1.25)
    a.pivot('Muzzle_rocket', (0, -.96 - 1.6 - .16, .34), 'Mount_rocket')
    K.chamfer_box(a.part('Thermo_sight', 'Armor', m), (.2, .28, .18), loc=(.3, -.2, .62), c=.02)
    a.part('Thermo_glass', 'Glass', m).box((.15, .012, .09), loc=(.3, -.345, .64), bevel=0)
    a.part('Thermo_hazard', 'SafetyStripe', m).box((.7, .02, .07), loc=(0, 1.06, .38), bevel=0)
    K.soot(a, (0, -6.1, 2.72), radius=.45, k=.35)
    K.tone(a, 'Mount_rocket', k=.9)


def _inferno_rear(a):
    """The engine deck: the red fuel tanks lying across it on cradles (the fuel part: Fuel_tanks, Tank_straps,
    Tank_hazard), the feed hoses to the turret, grilles, exhausts with soot, extinguishers, stowage."""
    tanks = a.part('Fuel_tanks', 'BarrelRed')
    straps = a.part('Tank_straps', 'Steel')
    haz = a.part('Tank_hazard', 'SafetyStripe')
    for y in (3.75, 4.7):
        k.lathe(tanks, [(0, -1.25), (.3, -1.23), (.4, -1.1), (.42, -.85), (.42, .85), (.4, 1.1), (.3, 1.23),
                        (0, 1.25)], loc=(0, y, 2.88), rot=(0, R90, 0), seg=16, worn=(3, 4))
        for x in (-.7, .7):
            straps.torus(.435, .03, loc=(x, y, 2.88), rot=(0, R90, 0), seg=16, ring=4)
            straps.box((.12, .2, .45), loc=(x, y, 2.48), bevel=0)
        haz.box((.38, .04, .38), loc=(0, y - .42, 2.88), rot=(0, .78, 0), bevel=0)
    hose = a.part('Hoses', 'Rubber')
    for x in (-.3, .3):
        hose.tube([(x, 3.4, 2.92), (x * 1.4, 3.0, 3.0), (x * 1.6, 2.7, 3.2)], .065, seg=6)
    for s in (-1, 1):
        K.exhaust(a, (s * 2.4, 5.2, 1.95), r=.11, length=.65, direction=(0, .4, 1), muffler=True)
        K.soot(a, (s * 2.4, 5.5, 2.65), radius=.9, k=.4)
        K.grille(a, (s * 1.85, 3.0, 2.38), .9, 1.0, facing=(0, 0, 1), slats=5)
        k.lathe(a.part('Extinguishers', 'BarrelRed'), [(.09, 0), (.09, .55), (.055, .6), (0, .64)],
                loc=(s * 2.75, 2.3, 2.2), rot=(s * .3, 0, 0), seg=8, worn=(1,))
        for j in range(3):
            a.part('Spare_links', 'Undercarriage').box((.8, .2, .06), loc=(s * 2.6, -3.3 + j * .24, 2.1),
                                                       rot=(0, s * .45, 0), bevel=0)
    K.crate(a.part('Ammo_locker', 'Crate'), a.part('Kit_latches', 'Steel'), (1.0, .6, .45), (-1.6, -2.0, 2.98),
            bands=2)
    for j in range(3):
        K.jerrycan(a.part('Jerrycans', 'Fuel'), (2.85, 1.4 + j * .42, 2.0), rot=(0, 0, R90))
    K.ladder(a.part('Ladders', 'Steel'), (3.5, 3.4, .3), (3.5, 3.4, 1.6), width=.45, step=.3)


def _inferno_kit(a):
    rv = a.part('Kit_rivets', 'Steel')
    for s in (-1, 1):
        K.rivet_line(rv, (s * 3.3, -4.5, 1.45), (s * 3.3, 4.3, 1.45), (s, 0, .3), pitch=.28, r=.024)
        K.rivet_line(rv, (s * 3.15, -4.5, 2.05), (s * 3.15, 4.3, 2.2), (s * .3, 0, 1), pitch=.28, r=.024)
        K.rivet_line(rv, (s * 2.33, -2.4, 2.6), (s * 2.33, 2.7, 2.6), (s, 0, .2), pitch=.26, r=.022)
    K.weld(a.part('Kit_welds', 'Steel'), [(-3.1, -4.68, 2.17), (3.1, -4.68, 2.17)], r=.03)
    K.rivet_line(rv, (-2.2, -2.62, 2.75), (2.2, -2.62, 2.75), (0, -1, .3), pitch=.26, r=.022)
    # Stowage bins on the hull's sides, different lengths, the pioneer tools, the tow cable on the left skirts.
    for s, bins in ((1, ((-1.6, .9), (.2, 1.3))), (-1, ((-2.2, 1.1), (-.6, .7), (.9, 1.5)))):
        for y, L in bins:
            K.crate(a.part('Bins', 'Crate'), a.part('Kit_latches', 'Steel'), (.42, L, .42), (s * 3.25, y, 1.9),
                    bands=1)
    K.tow_cable(a.part('Kit_cables', 'Steel'), [(3.47, -3.8, 1.25), (3.5, -1.0, 1.32), (3.47, 2.4, 1.25)], r=.045)
    for j, L in enumerate((1.3, 1.1, 1.5)):
        a.part('Tools', 'Wood').limb((-3.3, -3.6 + j * .6, 2.3), (-3.3, -3.6 + j * .6 + L, 2.3), .05, .05, bevel=0)
        a.part('Tools', 'Steel').box((.04, .22 + j * .04, .3), loc=(-3.3, -3.6 + j * .6, 2.3), bevel=0)
    # Turret side boxes and the grab rails.
    for s, L in ((1, 1.1), (-1, .8)):
        K.crate(a.part('Turret_bins', 'Crate', 'Turret'), a.part('Kit_latches', 'Steel', 'Turret'), (.35, L, .45),
                (s * 2.2, .7, .25), bands=1)
    gr = a.part('Kit_handles', 'Steel', 'Turret')
    for s in (-1, 1):
        for y in (-.6, .9):
            K.handle(gr, (s * 1.9, y - .25, .78), (s * 1.9, y + .25, .78), (s, 0, .3), h=.06)
    # Engine deck: access hatches, the air filters, deck rails, spare links, mudflaps.
    for x, y in ((1.2, 1.8), (-1.2, 1.8)):
        K.hatch_rect(a, (x, y + .9, 2.38), (.7, .6))
    for s in (-1, 1):
        k.lathe(a.part('Air_filters', 'Armor'), [(.2, 0), (.2, .55), (.24, .6), (.24, .7), (0, .72)],
                loc=(s * 2.55, 4.6, 2.2), seg=10, worn=(2,))
        a.part('Mud_flaps', 'Rubber').box((.8, .04, .55), loc=(s * 2.3, 5.5, .9), bevel=0)
        a.part('Mud_flaps', 'Rubber').box((.7, .04, .45), loc=(s * 2.3, -5.6, .95), bevel=0)
    rail = a.part('Railings', 'Steel')
    rail.tube([(-1.5, 5.25, 2.2), (-1.5, 5.35, 2.65), (1.5, 5.35, 2.65), (1.5, 5.25, 2.2)], .03, seg=5)
    # Heat-scorched glacis plate under the nozzles, its bolted shield.
    K.armour_plate(a, a.part('Heat_plate', 'Charred'), (2.0, .7, .06), (0, -5.1, 1.98), rot=(-1.1, 0, 0), rivet=.3)


def behemoth_inferno(a):
    """Inferno (see the module docstring). Runtime: Turret, Main_cannon / Main_cannon_2 with _jacket / _hose,
    Muzzle_brake[_2] with _glow / _pilot (flamer_r / flamer_l), Muzzle_main, Mount_rocket / Muzzle_rocket (thermo),
    Mount_mg / Muzzle_mg on the turret roof (flak), Fuel_tanks / Tank_straps / Tank_hazard (fuel)."""
    K.suffixed(a)
    _inferno_hull(a)
    _inferno_turret(a)
    _inferno_glacis(a)
    _inferno_rear(a)
    _inferno_kit(a)
    k.clean(a)


# ============================================================================= bastion_mk0
M_DECK = 4.15
M_TOP = 5.3


def _mk0_running_gear(a):
    """Exposed prototype running gear: small road wheels in sprung bogie pairs (bogie frames, leaf springs), the
    long track frame girder along each side, the idler at the front and the sprocket at the back, return rollers,
    no skirts."""
    wheels = [-6.55 + i * 1.19 for i in range(12)]
    W.running_gear(a, 3.0, .95, .36, wheels, (-7.55, .78, .42), (7.5, .82, .46), rollers=(-4.5, -1.5, 1.5, 4.5),
                   roller_z=1.25, top_hidden=None, disc_mat='Armor', seg=14, link_pitch=.3, wheel_w=.2, dust=.3,
                   teeth=10)
    bog = a.part('Suspension_arms', 'Armor')
    spr = a.part('Leaf_springs', 'Steel')
    for s in (-1, 1):
        for i in range(6):
            yc = (wheels[2 * i] + wheels[2 * i + 1]) / 2
            k.block(bog, (.18, 1.35, .34), loc=(s * 3.5, yc, .22), chamfer=.03)
            K.leaf_spring(spr, s * 3.5, yc, .78, 1.0, leaves=4, w=.12)
            spr.cyl(.07, .25, loc=(s * 3.55, yc, .45), rot=(0, R90, 0), seg=8, bevel=0)
        gird = a.part('Track_frames', 'Steel')
        gird.box((.12, 14.4, .5), loc=(s * 3.6, 0, 1.05), bevel=.01)
        gird.box((.3, 14.4, .06), loc=(s * 3.55, 0, 1.3), bevel=0)
        gird.box((.3, 14.4, .06), loc=(s * 3.55, 0, .8), bevel=0)
        for y in [-6.6 + j * 1.2 for j in range(12)]:
            gird.box((.14, .06, .5), loc=(s * 3.67, y, 1.05), bevel=0)


def _mk0_hull(a):
    """The riveted box hull (vertical walls, a raked bow plate, a stepped stern), the fighting compartment on top
    (vertical walls, vision slits), rivet rows along every plate seam, the deck girders and scaffold rails."""
    K.chamfer_box(a.part('Hull', 'Armor'), (4.8, 14.6, 1.0), loc=(0, 0, 1.25), c=.06)
    K.section_loft(a.part('Body', 'Team'), [
        (-7.95, [(0, 1.6), (2.7, 1.6), (2.7, 2.7), (2.3, 3.45), (0, 3.5)]),
        (-6.85, [(0, 1.4), (3.4, 1.4), (3.4, 3.85), (3.2, M_DECK), (0, M_DECK)]),
        (6.65, [(0, 1.4), (3.4, 1.4), (3.4, 3.85), (3.2, M_DECK), (0, M_DECK)]),
        (7.75, [(0, 1.5), (3.15, 1.5), (3.15, 3.5), (2.95, 3.75), (0, 3.8)])])
    fc = a.part('Fighting_compartment', 'Team')
    k.extrude(fc, [(-2.4, -2.9), (2.4, -2.9), (2.4, 2.9), (-2.4, 2.9)], M_TOP - M_DECK + .05,
              loc=(0, .5, (M_TOP + M_DECK) / 2 - .02), axis='Z', chamfer=.04, corner=.08, taper=(.97, .97))
    rv = a.part('Kit_rivets', 'Steel')
    for s in (-1, 1):
        for z in (1.55, 2.6, 3.7):
            K.rivet_line(rv, (s * 3.41, -6.7, z), (s * 3.41, 6.5, z), (s, 0, 0), pitch=.24, r=.022)
        for y in (-5.0, -2.2, 1.0, 3.6, 6.0):
            K.rivet_line(rv, (s * 3.41, y, 1.5), (s * 3.41, y, 3.8), (s, 0, 0), pitch=.24, r=.022)
        K.rivet_line(rv, (s * 2.36, -2.3, M_DECK + .1), (s * 2.36, 3.3, M_DECK + .1), (s, 0, 0), pitch=.25, r=.02)
        K.rivet_line(rv, (s * 2.36, -2.3, M_TOP - .1), (s * 2.36, 3.3, M_TOP - .1), (s, 0, 0), pitch=.25, r=.02)
        for y in (-1.6, .2, 2.0):
            a.part('Vision_slits', 'Undercarriage').box((.03, .7, .1), loc=(s * 2.36, y, M_DECK + .75), bevel=0)
            a.part('Slit_hoods', 'Armor').box((.12, .82, .05), loc=(s * 2.4, y, M_DECK + .84), bevel=0)
    for x in (-1.2, 0, 1.2):
        a.part('Vision_slits', 'Undercarriage').box((.7, .03, .1), loc=(x, -2.38, M_DECK + .75), bevel=0)
        a.part('Slit_hoods', 'Armor').box((.82, .12, .05), loc=(x, -2.42, M_DECK + .84), bevel=0)
    K.rivet_line(rv, (-2.6, -7.5, 3.0), (2.6, -7.5, 3.0), (0, -1, .6), pitch=.24, r=.022)
    # The bow plate: the driver's visor, a tow bar, headlamps in tubs.
    a.part('Driver_visor', 'Undercarriage').box((1.0, .03, .14), loc=(0, -7.62, 3.0), rot=(.95, 0, 0), bevel=0)
    a.part('Visor_hood', 'Armor').box((1.15, .2, .06), loc=(0, -7.55, 3.12), rot=(.95, 0, 0), bevel=0)
    for s in (-1, 1):
        k.lathe(a.part('Lamp_tubs', 'Armor'), [(.2, 0), (.22, .25), (.2, .28)], loc=(s * 2.2, -7.9, 2.3),
                rot=K.FORWARD, seg=10)
        a.part('Lamps', 'Lamp').cyl(.17, .02, loc=(s * 2.2, -8.2, 2.3), rot=K.FORWARD, seg=10, bevel=0)
        K.tow_hook(a.part('Hull_steel', 'Steel'), (s * 1.6, -8.0, 1.75), facing=(0, -1, 0), size=.28)
        a.part('Tail_lamps', 'LavaGlow').box((.18, .03, .1), loc=(s * 2.6, 7.78, 3.3), bevel=0)
    a.part('Tow_bar', 'Steel').tube([(-1.6, -8.1, 1.75), (0, -8.45, 1.6), (1.6, -8.1, 1.75)], .05, seg=6)
    # Deck girders and the scaffold rails (a prototype on trials).
    st = a.part('Scaffold', 'Steel')
    for s in (-1, 1):
        for y in (-6.6, -4.6, 4.2, 6.2):
            st.tube([(s * 3.15, y, M_DECK), (s * 3.15, y, M_DECK + 1.0)], .035, seg=6)
        st.tube([(s * 3.15, -6.6, M_DECK + 1.0), (s * 3.15, -4.6, M_DECK + 1.0)], .03, seg=6)
        st.tube([(s * 3.15, 4.2, M_DECK + 1.0), (s * 3.15, 6.2, M_DECK + 1.0)], .03, seg=6)
        st.tube([(s * 3.15, -6.6, M_DECK + .5), (s * 3.15, -4.6, M_DECK + .5)], .025, seg=6)
    gird = a.part('Deck_girders', 'Undercarriage')
    for y in (-6.0, -3.6, 4.6, 6.4):
        gird.box((6.2, .2, .12), loc=(0, y, M_DECK + .06), bevel=0)
    K.hatch_rect(a, (1.3, -5.2, M_DECK + .02), (.9, .9))
    K.hatch_rect(a, (-1.3, 5.3, M_DECK + .02), (.9, .9))
    K.door(a, (-3.42, 1.5, 1.6), size=(.9, 1.6), normal=(-1, 0, 0))
    K.ladder(a.part('Ladders', 'Steel'), (3.55, 1.6, .7), (3.45, 1.6, M_DECK), width=.5, step=.38)


def _mk0_rear(a):
    """The prototype's rear: the radiator box with its grille, two tall exhaust pipes with mufflers, the canvas
    tarpaulin over the engine deck lashed down, tool boxes, a workbench crate, test markings, a pennant pole."""
    k.block(a.part('Radiator', 'Armor'), (3.6, 1.0, 1.0), loc=(0, 7.35, 3.2), chamfer=.05)
    K.grille(a, (0, 7.86, 3.7), 3.0, .7, facing=(0, 1, 0), slats=7, frame_mat='Team')
    for s in (-1, 1):
        k.lathe(a.part('Exhaust_pipes', 'Rust'), [(.13, 0), (.13, 1.8), (.17, 1.85), (.17, 2.25), (.13, 2.3),
                                                  (.13, 2.6)], loc=(s * 2.6, 6.4, M_DECK), seg=10, worn=(2,))
        a.part('Exhaust_pipes', 'Rust').tube([(s * 2.6, 6.4, M_DECK + 2.6), (s * 2.6, 6.7, M_DECK + 2.85)], .13, seg=10)
        K.soot(a, (s * 2.6, 6.7, M_DECK + 2.9), radius=.9, k=.55)
    # The tarpaulin: a lumpy canvas loft over the engine deck, its ropes.
    tarp = a.part('Tarp', 'Canvas')
    rings = []
    for y, h in ((3.55, .25), (4.3, .55), (5.3, .62), (6.2, .5), (6.75, .2)):
        ring = []
        for i in range(9):
            u = math.pi * i / 8
            x = -2.7 * math.cos(u)
            zz = M_DECK + .02 + h * math.sin(u) * (1 + .12 * math.sin(i * 1.7 + y))
            ring.append((x, y, zz))
        ring += [(2.7, y, M_DECK + .01), (-2.7, y, M_DECK + .01)][::-1][1:]
        rings.append(ring)
    tarp.loft(rings)
    rope = a.part('Kit_straps', 'Undercarriage')
    for y in (4.3, 5.3, 6.2):
        rope.tube([(-2.72, y, M_DECK + .03), (-2.0, y, M_DECK + .45), (0, y, M_DECK + .66), (2.0, y, M_DECK + .45),
                   (2.72, y, M_DECK + .03)], .025, seg=4)
    for i in range(2):
        K.crate(a.part('Tool_boxes', 'Crate'), a.part('Kit_latches', 'Steel'), (.9, .5, .45),
                (-2.0 + i * 1.0, -6.4, M_DECK + .02), bands=1)
    K.crate(a.part('Tool_boxes', 'Crate'), a.part('Kit_latches', 'Steel'), (1.1, .6, .55), (2.2, -3.3, M_DECK + .02),
            bands=2)
    for i in range(4):
        a.part('Test_marks', 'SafetyStripe').box((.04, .5, .12), loc=(3.42, -6.0 + i * .7, 3.5), rot=(.7, 0, 0),
                                                 bevel=0)
    pole = a.part('Pennant_pole', 'Steel')
    pole.cyl(.035, 2.2, loc=(-2.0, 3.2, M_TOP + 1.1), seg=6, bevel=0)
    a.part('Pennant', 'ContainerRed').mesh([(-2.0, 3.2, M_TOP + 2.15), (-2.0, 3.95, M_TOP + 1.95),
                                            (-2.0, 3.2, M_TOP + 1.75)], [(0, 1, 2)])
    K.whip_antenna(a.part('Antennas', 'Steel'), (2.0, 3.0, M_TOP), h=2.0, r=.04)
    K.fuel_drum(a.part('Drums', 'Fuel'), a.part('Drum_bands', 'Steel'), (2.6, 3.95, M_DECK), r=.28, h=.86)
    K.fuel_drum(a.part('Drums', 'Fuel'), a.part('Drum_bands', 'Steel'), (2.6, -2.2, M_DECK), r=.28, h=.86)


def _mk0_sponson(a, index, s):
    """A front side sponson of the prototype on Mount_gun[.NNN]: a riveted half-drum bay out of the wall with a flat
    gun shield and the twin 100 mm (plain barrels with reference collars), Muzzle_gun[.NNN] and the per-barrel
    muzzles; the fixed bay frame and its bracket on the hull."""
    y = -4.35
    x = s * 4.0
    z = 2.5
    bay = a.part('Sponson_bay', 'Armor')
    k.block(bay, (1.4, 2.5, .26), loc=(s * 3.9, y, z - .26), chamfer=.04)
    bay.limb((s * 3.42, y - .7, 1.5), (s * 3.95, y - .7, z - .25), .1, .12, bevel=0)
    bay.limb((s * 3.42, y + .7, 1.5), (s * 3.95, y + .7, z - .25), .1, .12, bevel=0)
    key = _n('Mount_gun', index)
    m = a.pivot(key, (x, y, z))
    drum = a.part('Sponson_drum', 'Team', m)
    k.lathe(drum, [(1.0, 0), (1.0, 1.2), (.93, 1.28), (0, 1.3)], seg=18, worn=(1, 2))
    k.block(a.part('Sponson_shield', 'Armor', m), (1.45, .18, 1.15), loc=(0, -1.0, .06), chamfer=.04)
    rv = a.part('Kit_rivets', 'Steel', m)
    for i in range(12):
        u = i * TAU / 12
        rv.cyl(.025, .03, loc=(math.cos(u) * 1.0, math.sin(u) * 1.0, 1.05), rot=(0, R90, u), seg=6, bevel=0)
    for bx in (-.27, .27):
        K.gun_barrel(a, 'Sponson_barrels', key, bx, -1.1, .62, 2.9, .07, seg=10, extractor=(.5, 1.45, .3),
                     brake_name='Sponson_collars', brake='collar')
    mz = a.pivot(_n('Muzzle_gun', index), (0, -1.1 - 2.9 - .14, .62), key)
    _per_barrel(a, mz, _tag('gun', index), (-.27, .27))
    a.part('Sponson_slit', 'Undercarriage', m).box((.4, .03, .08), loc=(.4 * s, -1.1, .95), bevel=0)
    K.tone(a, key, k=.9)
    K.soot(a, (x, y - 3.9, z + .55), radius=.6, k=.35)


def _mk0_mortar(a):
    """The 240 mm mortar on an open pedestal mount on the fighting compartment (Turret: the turntable, the open side
    frames, a front splinter shield, the tube with its breech and buffers: Main_cannon*, Muzzle_main), the
    parapet round the roof opening."""
    par = a.part('Parapet', 'Armor')
    for s in (-1, 1):
        par.box((.1, 4.2, .45), loc=(s * 2.0, .5, M_TOP + .22), bevel=.01)
    par.box((4.0, .1, .45), loc=(0, -1.6, M_TOP + .22), bevel=.01)
    t = a.pivot('Turret', (0, .55, M_TOP))
    k.lathe(a.part('Turret_armor', 'Steel', t), [(1.45, 0), (1.5, .06), (1.5, .2), (1.35, .24), (0, .25)], seg=24,
            worn=(2,))
    for s in (-1, 1):
        fr = a.part('Mortar_frames', 'Armor', t)
        k.extrude(fr, [(-.7, .25), (.9, .25), (.7, 1.5), (-.05, 1.6)], .14, loc=(s * .55, 0, 0), axis='X',
                  chamfer=.02, corner=.04)
        a.part('Mortar_frames', 'Steel', t).cyl(.13, .1, loc=(s * .66, .25, 1.15), rot=(0, R90, 0), seg=10, bevel=0)
    k.block(a.part('Mortar_shield', 'Armor', t), (1.9, .1, .9), loc=(0, -1.2, .25), rot=(-.25, 0, 0), chamfer=.03)
    m = Matrix.Translation(Vector((0, .25, 1.15))) @ Matrix.Rotation(math.radians(-55), 4, 'X')
    rot = tuple((m @ Matrix.Rotation(R90, 4, 'X')).to_euler('XYZ'))
    L = 3.0
    k.lathe(a.part('Main_cannon', 'Steel', t), [(.3, -.55), (.3, .15), (.26, .25), (.26, L - .2), (.31, L - .16),
                                                (.31, L), (.2, L), (.2, L - .1), (0, L - .1)],
            loc=tuple(m @ Vector((0, 0, 0))), rot=rot, seg=16, worn=(2, 5))
    k.lathe(a.part('Main_cannon_breech', 'Armor', t), [(0, -1.0), (.4, -.95), (.42, -.55), (.34, -.45)],
            loc=tuple(m @ Vector((0, 0, 0))), rot=rot, seg=14)
    for sx in (-1, 1):
        a.part('Main_cannon_buffer', 'Steel', t).limb(tuple(m @ Vector((sx * .34, -.25, .1))),
                                                     tuple(m @ Vector((sx * .34, -.25, -1.2))), .09, .09, bevel=0)
    for f in (.4, .8):
        a.part('Main_cannon_bands', 'Steel', t).torus(.285, .03, loc=tuple(m @ Vector((0, -L * f, 0))),
                                                      rot=rot, seg=16, ring=4)
    tip = m @ Vector((0, -L, 0))
    a.pivot('Muzzle_main', tuple(tip), 'Turret')
    for i in range(2):
        k.lathe(a.part('Ready_bombs', 'Fuel', t), [(0, -.5), (.11, -.4), (.14, -.18), (.14, .32), (.09, .45),
                                                   (0, .5)], loc=(-.5 + i * 1.0, 1.25, .45), rot=(R90, 0, 0), seg=10)
    K.soot(a, (0, .55 + tip.y, M_TOP + tip.z), radius=.9, k=.45)


def _mk0_kit(a):
    rib = a.part('Ribs', 'Armor')
    seam = a.part('Plate_seams', 'Armor')
    for s in (-1, 1):
        for j, y in enumerate((-6.2, -3.0, -.6, 2.2, 4.8)):
            h = 2.1 + .07 * j
            rib.box((.12, .16 + .02 * j, h), loc=(s * 3.46, y, 1.45 + h / 2), bevel=.01)
        for z, L in ((2.05, 13.2), (3.15, 13.0)):
            seam.box((.05, L, .07), loc=(s * 3.43, 0, z), bevel=0)
        # Fenders over the track ends, the track adjusters, lifting eyes.
        K.fender(a.part('Fenders', 'Team'), 3.0, -8.0, -6.6, 1.45, 1.1, s, lip=.1)
        K.fender(a.part('Fenders', 'Team'), 3.0, 6.7, 7.95, 1.5, 1.1, s, lip=.1)
        a.part('Adjusters', 'Steel').tube([(s * 3.5, -7.35, .8), (s * 3.5, -6.5, 1.05)], .05, seg=6)
        a.part('Adjusters', 'Steel').cyl(.09, .2, loc=(s * 3.5, -6.6, 1.03), rot=(R90 - .3, 0, 0), seg=6, bevel=0)
        W.lifting_eyes(a.part('Kit_tow', 'Steel'), [(s * 3.0, -6.9, M_DECK + .05), (s * 3.0, 6.6, M_DECK + .05)],
                       r=.12)
    # Coolant pipes from the radiator along the deck, the engine-deck access plates.
    pipe = a.part('Pipes', 'Pipe')
    for x in (-.5, .5):
        pipe.tube([(x, 6.85, 3.9), (x, 6.5, M_DECK + .2), (x * 1.6, 3.4, M_DECK + .2), (x * 1.6, 3.0, M_DECK + .5)],
                  .07, seg=8)
    # The observation cupola on the fighting compartment, handrails round its roof.
    k.lathe(a.part('Cupola', 'Armor'), [(.42, 0), (.42, .36), (.36, .42), (0, .44)], loc=(1.6, -1.8, M_TOP),
            seg=14, worn=(1,))
    for i in range(4):
        u = i * TAU / 4
        K.periscope(a, (1.6 + math.sin(u) * .4, -1.8 - math.cos(u) * .4, M_TOP + .2),
                    facing=(math.sin(u), -math.cos(u), 0), size=(.16, .14, .12))
    hr = a.part('Kit_handles', 'Steel')
    for s in (-1, 1):
        K.handle(hr, (s * 2.25, -2.0, M_TOP + .02), (s * 2.25, -.6, M_TOP + .02), (0, 0, 1), h=.12)
        K.handle(hr, (s * 2.25, 1.8, M_TOP + .02), (s * 2.25, 3.0, M_TOP + .02), (0, 0, 1), h=.12)
    # Stowage of many sizes on the front deck and the sides.
    for (x, y, size) in ((-2.3, -4.0, (.7, .45, .4)), (-1.4, -4.1, (.55, .5, .35)), (.2, -6.7, (1.3, .45, .3)),
                         (2.6, -6.9, (.5, .4, .55))):
        K.crate(a.part('Stowage', 'Crate'), a.part('Kit_latches', 'Steel'), size, (x, y, M_DECK + .02), bands=1)
    for j, L in enumerate((1.2, 1.4)):
        a.part('Tools', 'Wood').limb((-3.48, -1.0 + j * .5, 2.4), (-3.48, -1.0 + j * .5 + L, 2.4), .05, .05,
                                     bevel=0)
    k.lathe(a.part('Spare_wheel', 'Rubber'), [(.24, -.1), (.36, -.09), (.36, .09), (.24, .1)],
            loc=(3.62, 2.9, 2.75), rot=(0, R90, 0), seg=14)
    a.part('Spare_wheel_hub', 'Armor').cyl(.24, .16, loc=(3.62, 2.9, 2.75), rot=(0, R90, 0), seg=14, bevel=.02)
    # The trials crew's rack hung on the left flank only: a slatted shelf on brackets with crates and a drum.
    shelf = a.part('Side_rack', 'Steel')
    shelf.box((.75, 2.7, .06), loc=(3.8, 5.3, 2.35), bevel=0)
    for y in (4.1, 5.3, 6.5):
        shelf.limb((3.45, y, 1.75), (4.1, y, 2.33), .06, .06, bevel=0)
    for (y, size) in ((4.5, (.6, .7, .45)), (5.35, (.55, .55, .6))):
        K.crate(a.part('Side_crates', 'Crate'), a.part('Kit_latches', 'Steel'), size, (3.82, y, 2.38), bands=1)
    K.fuel_drum(a.part('Drums', 'Fuel'), a.part('Drum_bands', 'Steel'), (3.85, 6.2, 2.38), r=.28, h=.8)
    K.tow_cable(a.part('Kit_cables', 'Steel'), [(-3.47, 3.0, 2.6), (-3.5, 4.6, 2.75), (-3.47, 6.2, 2.6)], r=.04)
    # Shell crates beside the mortar, the bomb hoist's davit.
    for i, (x, y) in enumerate(((-1.4, 2.6), (-.8, 2.75), (1.3, 2.7))):
        K.crate(a.part('Bomb_crates', 'Crate'), a.part('Kit_latches', 'Steel'), (.5 + .05 * i, .8, .35),
                (x, y, M_TOP), bands=1)
    dav = a.part('Davit', 'CraneYellow')
    dav.cyl(.08, 1.6, loc=(1.75, 2.9, M_TOP + .8), seg=8, bevel=0)
    dav.limb((1.75, 2.9, M_TOP + 1.55), (1.0, 2.4, M_TOP + 1.75), .07, .07, bevel=0)
    a.part('Kit_cables', 'Steel').tube([(1.0, 2.4, M_TOP + 1.7), (1.0, 2.4, M_TOP + .9)], .015, seg=4)


def bastion_mk0(a):
    """Bastion Mk.0 (see the module docstring), its own model (it drew fortress_bastion). Runtime (the def keeps the
    mortar, turret_fl and turret_fr of fortress_bastion): Turret / Main_cannon* / Muzzle_main (mortar), Mount_gun /
    .001 + Muzzle_gun / .001 (the front sponsons, left / right, per-barrel muzzles). None of the dropped parts' names
    (Mount_gun.002-.004, Part_missile, Mount_mg) are used."""
    K.suffixed(a)
    _mk0_running_gear(a)
    _mk0_hull(a)
    _mk0_rear(a)
    _mk0_sponson(a, 0, 1)
    _mk0_sponson(a, 1, -1)
    _mk0_mortar(a)
    _mk0_kit(a)
    k.clean(a)


BUILDERS = {
    'fortress_bastion': (fortress_bastion, dict(ao_distance=1.0, grime_height=1.4, ao_strength=.75)),
    'mobile_fortress': (mobile_fortress, dict(ao_distance=1.1, grime_height=1.0, ao_strength=.72)),
    'fenrir': (fenrir, dict(ao_distance=.9, grime_height=1.0, ao_strength=.75)),
    'behemoth_inferno': (behemoth_inferno, dict(ao_distance=.9, grime_height=.9, ao_strength=.74)),
    'bastion_mk0': (bastion_mk0, dict(ao_distance=1.0, grime_height=1.3, ao_strength=.75)),
}
