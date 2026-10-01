"""Prompt 27 wave 1b, part (DECISIONS "27 wave 1a + 1b (part)"): two of the prompt 25 batch D stand-in bosses built as
their own models on the V2 kit (mb_kit27 primitives + mb_parts27 parts), merged last in build_assets.all_builders().

Both are variants (`variantOf`): they inherit their parent's built parts and mounts, so each model carries every node
those parts and mounts name, near the places the resized data puts them (parent `at` x parent size x variant size).

  * monster (Orlov's Monster, variant of fortress_bastion): a post-1945 super-heavy self-propelled gun after the 2B1
    Oka and Object 271 (DECISIONS 26CD; the Landkreuzer P. 1500 layout of the old brief, its WW2 look dropped):
    40.3 x 22.1 x 13 m (its modelSize). A long armoured hull on four double-track clusters (`Part_track`,
    `Part_track.001` front left / right, `.002` / `.003` rear left / right, nodes for a later track-break rule), the
    800 mm gun half the hull long on `Turret` (`Main_cannon*`, `Muzzle_brake`, `Muzzle_main`, its cradle on
    `Part_barrel`), the 155 mm bow turret (`Mount_gun.004`), four 40 mm flak mounts at the corners (`Mount_gun` ..
    `.003`), two ZU-23 sponsons (`Mount_mg`, `.001`), the Kornet launcher (`Part_missile` > `Mount_missile` >
    `Muzzle_missile`).
  * nyx (Kessler's Nyx, variant of leviathan keeping turret_fore, vls, ciws_fore, ciws_aft): a Zumwalt-style
    stealth destroyer, 53 x 8.9 x 11 m (its modelSize, keel 1.6 m under the waterline at z 0): a tumblehome hull
    with its reverse-raked wave-piercing bow, the faceted pyramid deckhouse with flush radar faces, a railgun in a
    faceted turret on the foredeck (`Part_gun` > `Mount_gun` > `Muzzle_gun`), peripheral VLS banks along the deck
    edges (`Part_vls`), two CIWS (`Part_mg` > `Mount_mg`, `Part_mg.001` > `Mount_mg.001`), the helicopter deck aft.
  * cerberus (Cerberus, variant of behemoth keeping main_gun, flak_r, flak_l, rocket_pod): three big-wheeled cars
    coupled by drawbars, 16.2 x 7.0 x 5.4 m (modelSize 16.3 x 8.4 x 5.5: a road train cannot be 8.4 m wide; the wide
    stance of the tyres on outboard axles gives 7.0, -17 % on width / length). Each car on its own node for a later
    coupling-break rule: `Part_tractor` (the 125 mm `Turret` with `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, the
    30 mm RWS `Mount_gun`), `Part_middle` (the anti-air car: flak `Mount_mg` right / `.001` left, the radar panel,
    the fixed missile packs `Muzzle_missile` / `.001`), `Part_trailer` (the rocket pod `Mount_rocket`, rear guns
    `Mount_gun.001` / `.002`). The behemoth's mount set, so its inherited weapon list keeps its slots.
  * stymphalos (Stymphalos, variant of drone_mothership keeping drone_bay, drone_bay_2, flak_top): eight delta-wing
    jet drones (5.2 m long, 4.4 m span each) in a V, 15.4 x 26.0 x 2.6 m (the def gets that modelSize), every drone
    on its own node (`Part_drone` lead .. `Part_drone.007` the slot drone behind it) for a later swarm rule. The lead
    carries the dorsal flak `Mount_mg` and `Muzzle_missile`, the slot drone the bay pod `Mount_missile.001`, two arm
    drones `Mount_gun` / `.001`. `stymphalos_drone` is one drone alone (`Muzzle_gun` nose gun), unlisted until the
    swarm rule spawns drones as units.
  * hydra_sub (Hydra, variant of typhon keeping doors_l, doors_r, deck_gun, rudder; `hydra.glb` is the Hydra 70
    rocket, so the boss model is `hydra_sub`): a small VLS submarine, 34.8 x 7.2 x 7.8 m, hull axis at z 0: a lathed
    pressure hull, the sail with fairwater planes and a SAM box (`Mount_missile` > `Muzzle_missile`), the deck gun
    (`Mount_gun`), ten launch tubes along the back on `Part_doors_l` / `Part_doors_r` (the parent's names), six FPV
    quadcopters on the drone deck aft (`Part_drone` .. `Part_drone.005`, nodes for a later launch rule), cruciform
    stern planes and a pump-jet on `Part_rudder`. Built with ground=False (it floats; no ground AO under the hull).

Conventions are frontier_kit's: metres, +Z up, Blender -Y is the front, +X the vehicle's left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_parts27 as parts
from mb_p20_bosses import _tag, gun_turret
from mb_phase2 import _suffixed
from mb_phase8 import autocannon, ciws, pv
from mb_vehicles import ACROSS, FORWARD, R90

TAU = math.tau


def _sq(w, h=None):
    h = w if h is None else h
    return [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]


# ============================================================================= Monster
MN_HALF = 20.15                 # half length
MN_DECK = 6.4                   # hull roof
MN_TRACKS = (('Part_track', 1, -11.6), ('Part_track__001', -1, -11.6),
             ('Part_track__002', 1, 11.4), ('Part_track__003', -1, 11.4))
MN_CX = 8.6                     # track cluster centre |x|


def _mn_track(a, name, s, y, i):
    """A double track cluster on its own Part_* node: two belts (a chamfered strip swept round idler and sprocket,
    cleats along it), road wheels, the idler and the sprocket on the outer face."""
    p = a.pivot(name, (s * MN_CX, y, 0))
    belt = a.part(f'Track_belt_{i}', 'Undercarriage', p)
    wheels = a.part(f'Track_wheels_{i}', 'Armor', p)
    ye, zc, rc = 6.6, 1.33, 1.1
    loop = [(0, -ye, zc - rc), (0, ye, zc - rc)]
    loop += [(0, ye + rc * math.sin(u), zc - rc * math.cos(u)) for u in (j * math.pi / 6 for j in range(1, 6))]
    loop += [(0, ye, zc + rc), (0, 0, zc + rc - .08), (0, -ye, zc + rc)]
    loop += [(0, -ye - rc * math.sin(u), zc + rc * math.cos(u)) for u in (j * math.pi / 6 for j in range(1, 6))]
    for dx in (-1.15, 1.15):
        path = [(dx, py, pz) for _, py, pz in loop]
        k.sweep(belt, k.round_corners(_sq(2.1, .3), .05), path, closed=True)
        for pt, tan in k.along(path, pitch=.62, closed=True):
            n = tan.cross(Vector((1, 0, 0))).normalized()
            rot = Vector((0, 1, 0)).rotation_difference(tan).to_euler('XYZ')
            belt.box((2.0, .24, .1), loc=tuple(pt + n * .18), rot=tuple(rot), bevel=0)
        side = 1 if dx * s > 0 else -1          # this belt's outer face, away from the hull or towards it
        for wy in (-4.4, -2.2, 0.0, 2.2, 4.4):
            k.lathe(wheels, [(.45, -.85), (.82, -.8), (.82, .8), (.45, .85), (0, .88)], loc=(dx, wy, 1.03),
                    rot=parts.side_rot(s * side), seg=12, worn=(1,))
        for wy in (-ye, ye):
            k.lathe(wheels, [(.5, -.9), (1.0, -.85), (1.0, .85), (.5, .9), (0, .95)], loc=(dx, wy, zc),
                    rot=parts.side_rot(s), seg=14, worn=(1,))


def _kornet(a, loc, sc=1.8):
    """mb_p16_arms.fortress_bastion's twin Kornet launcher, `sc` times larger for a 40 m boss: `Part_missile` >
    `Mount_missile` > `Muzzle_missile` at the left tube's mouth."""
    pm = pv(a, 'Part_missile', loc)
    k.lathe(a.part('Atgm_pedestal', 'Armor', pm), [(.36 * sc, 0), (.36 * sc, .06 * sc), (.2 * sc, .1 * sc),
                                                   (.2 * sc, .5 * sc)], seg=14, worn=(1,))
    m = pv(a, 'Mount_missile', (0, 0, .5 * sc), 'Part_missile')
    arm = a.part('Atgm_armor', 'Armor', m)
    k.block(arm, (.3 * sc, .3 * sc, .5 * sc), loc=(0, .05 * sc, .32 * sc), chamfer=.03 * sc)
    k.block(a.part('Atgm_cradle', 'Team', m), (.74 * sc, .44 * sc, .12 * sc), loc=(0, -.05 * sc, .62 * sc),
            chamfer=.02 * sc)
    tz = .8 * sc
    tubes = a.part('Launch_tubes', 'Team', m)
    for s in (1, -1):
        x = s * .28 * sc
        k.lathe(tubes, [(.06 * sc, -.03), (.088 * sc, 0), (.088 * sc, 1.2 * sc), (.075 * sc, 1.24 * sc)],
                loc=(x, .5 * sc, tz), rot=FORWARD, seg=12, worn=(1,))
        a.part('Launch_tubes_bore', 'Charred', m).cyl(.06 * sc, .02, loc=(x, -.72 * sc, tz), rot=FORWARD, seg=10,
                                                      bevel=0)
    k.block(arm, (.3 * sc, .4 * sc, .3 * sc), loc=(0, -.2 * sc, .82 * sc), chamfer=.03 * sc)
    a.part('Atgm_sight_glass', 'Glass', m).box((.16 * sc, .02, .12 * sc), loc=(0, -.405 * sc, .86 * sc), bevel=0)
    pv(a, 'Muzzle_missile', (.28 * sc, -.75 * sc, tz), 'Mount_missile')


def monster(a):
    """Monster, the 800 mm self-propelled gun: see the module docstring."""
    _suffixed(a)
    team, arm = a.part('Hull', 'Team'), a.part('Armor', 'Armor')
    steel, dark = a.part('Steel', 'Steel'), a.part('Chassis', 'Undercarriage')
    for i, (name, s, y) in enumerate(MN_TRACKS):
        _mn_track(a, name, s, y, i)
    # The hull: a side profile across the hull, a long glacis, the rear plate; the fenders over each cluster with
    # their skirts, the ZU-23 sponsons between the clusters.
    side = [(-MN_HALF, 2.6), (-17.0, 1.3), (18.5, 1.3), (19.9, 2.4), (19.9, 6.0), (18.8, MN_DECK), (-16.2, MN_DECK),
            (-MN_HALF, 3.6)]
    k.extrude(arm, side, 12.6, axis='X', chamfer=.14, corner=.12)
    k.inset(arm, lambda c, n, f: n.z > .9 and c.z > MN_DECK - .05, width=.4, depth=.04)
    k.inset(arm, lambda c, n, f: abs(n.x) > .9, width=.3, depth=.035)
    for _, s, y in MN_TRACKS:
        k.block(team, (4.7, 15.6, .35), loc=(s * MN_CX, y, 2.9), chamfer=.06)                        # fenders
        k.block(arm, (.2, 15.2, 1.0), loc=(s * 10.85, y, 2.35), chamfer=0)                            # skirts
        for yb in (y - 5.0, y, y + 5.0):
            k.block(dark, (2.4, .5, .6), loc=(s * 6.9, yb, 2.85), chamfer=.04)                       # brackets
    for s in (-1, 1):
        k.block(arm, (2.4, 3.2, 4.4), loc=(s * 7.3, 2.4, 4.5), chamfer=.1)                            # sponsons
    # Lamps, tow eyes, exhausts at the rear.
    lamps = a.part('Lamps', 'Lamp')
    for s in (-1, 1):
        k.block(arm, (.9, .4, .6), loc=(s * 4.6, -MN_HALF + 1.4, 4.4), rot=(-.9, 0, 0), chamfer=.05)
        lamps.box((.6, .05, .35), loc=(s * 4.6, -MN_HALF + 1.15, 4.2), rot=(-.9, 0, 0), bevel=0)
        for x in (s * 2.2, s * 3.2):
            k.lathe(steel, [(.32, 0), (.32, 1.3), (.4, 1.36), (.4, 1.6)], loc=(x, 18.2, MN_DECK), seg=12, worn=(2,))
    a.pivot('Point_exhaust', (2.7, 18.2, MN_DECK + 1.8))
    a.pivot('Point_fire', (0, 14.0, MN_DECK + .2))

    # The superstructure under the gun, its raised plates, greebles fore and aft.
    k.extrude(team, [(-3.9, MN_DECK), (3.9, MN_DECK), (3.9, 7.4), (3.3, 8.0), (-3.3, 8.0), (-3.9, 7.4)], 20.0,
              loc=(0, 4.0, 0), axis='Y', chamfer=.12, corner=.1)
    k.greebles(arm, (0, 16.4, 8.0), (1, 0, 0), (0, 1, 0), (5.6, 2.6), 4, seed=2741, height=(.2, .45), chamfer=.04)
    k.greebles(arm, (0, -15.0, MN_DECK), (1, 0, 0), (0, 1, 0), (9.0, 2.4), 5, seed=2742, height=(.2, .45),
               chamfer=.04, avoid=(((0, -12.05, MN_DECK), 2.4),))

    # The 155 mm bow turret, the four corner flak mounts on their tubs, the ZU-23s, the Kornet.
    gun_turret(a, 'Mount_gun.004', 'Muzzle_gun.004', (0, -12.05, MN_DECK), w=3.0, d=3.4, h=1.3, barrel=5.6, r=.17)
    for mount, x, y in (('Mount_gun', 5.07, -9.51), ('Mount_gun.001', -5.07, -9.51),
                        ('Mount_gun.002', 4.9, 9.9), ('Mount_gun.003', -4.9, 9.9)):
        k.lathe(arm, [(1.15, 0), (1.15, .85), (1.0, 1.0)], loc=(x, y, MN_DECK), seg=16, worn=(1,))
        autocannon(a, mount, (x, y, MN_DECK + 1.0), length=3.2, r=.09, size=(1.6, 1.9, .8))
    for s, mount in ((1, 'Mount_mg'), (-1, 'Mount_mg.001')):
        autocannon(a, mount, (s * 7.3, 2.4, 6.7), length=2.4, r=.06, size=(1.3, 1.5, .7), body='Armor')
    _kornet(a, (2.6, 12.6, 8.0))

    # The 800 mm gun on `Turret`: a faceted housing, the cradle on `Part_barrel`, the barrel 18.5 m from the
    # mantlet at 7 degrees, a double-baffle brake.
    t = a.pivot('Turret', (0, 3.0, 8.0))
    house = a.part('Turret_body', 'Team', t)
    k.extrude(house, [(-3.4, 0), (3.4, 0), (3.4, 1.4), (2.6, 2.6), (-2.6, 2.6), (-3.4, 1.4)], 9.0,
              loc=(0, .5, 0), axis='Y', chamfer=.12, corner=.1)
    k.inset(house, lambda c, n, f: n.z > .9, width=.3, depth=.03)
    tarm, tst = a.part('Turret_armor', 'Armor', t), a.part('Turret_steel', 'Steel', t)
    k.ring(tst, [(3.0, -.02), (3.25, -.02), (3.25, .12), (3.0, .12)], seg=28)
    p = math.radians(7)
    d = Vector((0, -math.cos(p), math.sin(p)))
    root = Vector((0, -4.0, 1.6))
    k.block(tarm, (3.0, 1.0, 2.4), loc=(0, -3.9, 1.5), chamfer=.1)                                  # mantlet
    pb = root + d * 2.2
    a.pivot('Part_barrel', tuple(pb), 'Turret')
    k.block(a.part('Barrel_cradle', 'Armor', 'Part_barrel'), (2.2, 4.4, 2.2), loc=(0, 0, -1.1), rot=(-p, 0, 0),
            chamfer=.08)
    L = 18.5
    parts.barrel(a, 'Main_cannon', t, 0, root.y, root.z, L, .7, seg=20, sleeve=1.25, extractor=(.32, 1.32, 1.6),
                 brake_name='Muzzle_brake', brake='baffle', rot=(R90 - p, 0, 0))
    a.pivot('Muzzle_main', tuple(root + d * (L + .3)), t)
    parts.hatch(a, 1.6, 2.2, 2.6, .6, parent=t, seg=12)
    parts.hatch(a, -1.6, 2.8, 2.6, .55, parent=t, seg=12)
    k.block(tarm, (1.2, 1.4, .8), loc=(-1.6, .6, 3.0), chamfer=.06)                                # sight
    a.part('Turret_glass', 'Glass', t).box((.8, .04, .4), loc=(-1.6, -.12, 3.05), bevel=0)
    k.greebles(tarm, (0, 3.8, 2.6), (1, 0, 0), (0, 1, 0), (4.6, 1.4), 3, seed=2743, height=(.2, .4), chamfer=.04)
    parts.antenna(a.part('Antennas', 'Steel', t), (2.6, 4.3, 2.6), h=.6, r=.07)
    k.clean(a)


# ============================================================================= Nyx
NX_DECK = 3.0


def _nx_ring(y, sx, kb, dt):
    """Hull section at y: keel kb, bilge, the beam at the waterline, the tumblehome to the deck edge at dt."""
    return [(0, y, kb), (-3.9 * sx, y, kb * .55), (-4.45 * sx, y, .4), (-3.6 * sx, y, dt), (3.6 * sx, y, dt),
            (4.45 * sx, y, .4), (3.9 * sx, y, kb * .55)]


def nyx(a):
    """Nyx, the Zumwalt-style stealth destroyer: see the module docstring."""
    _suffixed(a)
    team, arm = a.part('Hull', 'Team'), a.part('Armor', 'Armor')
    steel, dark = a.part('Steel', 'Steel'), a.part('Dark', 'Undercarriage')
    rings = [[(0, -26.5, .5)],
             _nx_ring(-24.6, .26, -.3, 1.7),
             _nx_ring(-20.5, .6, -1.1, NX_DECK),
             _nx_ring(-12.0, .93, -1.6, NX_DECK),
             _nx_ring(0.0, 1.0, -1.6, NX_DECK),
             _nx_ring(16.0, 1.0, -1.5, NX_DECK),
             _nx_ring(26.4, .94, -.9, NX_DECK)]
    k.sharp_loft(team, rings, chamfer=.08, corners=[3, 4])
    # Deck plating: raised panels and the helicopter deck's markings aft.
    k.block(a.part('Helo_deck', 'MetalSheet'), (6.6, 13.0, .08), loc=(0, 19.6, NX_DECK + .04), chamfer=0)
    mark = a.part('Deck_marks', 'SafetyStripe')
    k.ring(mark, [(2.2, 0), (2.45, 0), (2.45, .02), (2.2, .02)], loc=(0, 20.0, NX_DECK + .08), seg=24)
    mark.box((.2, 10.0, .02), loc=(0, 20.0, NX_DECK + .09), bevel=0)
    k.greebles(arm, (0, -18.5, NX_DECK), (1, 0, 0), (0, 1, 0), (3.0, 3.0), 3, seed=2751, height=(.08, .2),
               chamfer=.02)

    # The deckhouse: a faceted pyramid from the deck (y -6 .. 12) to its crown, flush radar faces, the hangar.
    def house(z, hx, y0, y1):
        return [(-hx, y0, z), (hx, y0, z), (hx, y1, z), (-hx, y1, z)]
    k.sharp_loft(team, [house(NX_DECK, 2.7, -6.0, 12.0), house(8.0, 1.6, -2.7, 9.6), house(8.9, 1.25, -2.1, 9.0)],
                 chamfer=.1)
    panels = a.part('Radar_faces', 'Undercarriage')
    for y, rotz, s in ((-4.25, 0.0, 0), (10.9, math.pi, 0)):
        panels.box((1.9, .06, 1.9), loc=(0, y, 6.6), rot=(-.53 if y < 0 else .53, 0, rotz), bevel=0)
    for s in (-1, 1):
        panels.box((.06, 2.2, 1.9), loc=(s * 1.98, 2.0, 6.6), rot=(0, s * -.2, 0), bevel=0)
    k.block(dark, (3.0, .1, 2.0), loc=(0, 12.0, NX_DECK + 1.0), chamfer=0)                          # hangar door
    k.block(arm, (1.2, 1.0, .5), loc=(0, 3.4, 9.15), chamfer=.06)                                   # crown sensors

    # The railgun in its faceted turret on the foredeck.
    pg = pv(a, 'Part_gun', (0, -13.2, NX_DECK))
    k.lathe(a.part('Gun_ring', 'Steel', pg), [(1.9, 0), (2.0, .05), (2.0, .16), (1.85, .2)], seg=20, worn=(2,))
    m = pv(a, 'Mount_gun', (0, 0, .2), 'Part_gun')
    k.sharp_loft(a.part('Gun_house', 'Team', m), [house(0, 1.8, -1.8, 2.3), house(1.3, 1.25, -1.0, 1.9)],
                 chamfer=.06)
    rail = a.part('Gun_rails', 'Armor', m)
    k.extrude(rail, [(-.32, -.36), (.32, -.36), (.32, .36), (-.32, .36)], 8.4, loc=(0, -5.1, .75), axis='Y',
              chamfer=.04, corner=.06, taper=(1.25, 1.2))
    bands = a.part('Gun_bands', 'Steel', m)
    for yb in (-2.4, -4.6, -6.8):
        bands.box((.82, .3, .9), loc=(0, yb, .75), bevel=0)
    a.part('Gun_bore', 'Charred', m).box((.36, .02, .4), loc=(0, -9.32, .75), bevel=0)
    pv(a, 'Muzzle_gun', (0, -9.35, .75), 'Mount_gun')

    # Peripheral VLS banks along the deck edges beside the deckhouse (one part).
    pvls = pv(a, 'Part_vls', (0, 3.45, NX_DECK))
    vls = a.part('Vls_hatches', 'Armor', pvls)
    for s in (-1, 1):
        for j in range(6):
            k.block(vls, (.62, 1.0, .14), loc=(s * 3.12, -4.6 + j * 1.15, .07), chamfer=.02)
    # The two CIWS: forward on a bracket off the deckhouse's front face, aft on a sponson behind it.
    for name, mount, loc, z0 in (('Part_mg', 'Mount_mg', (-2.09, -4.9, 6.1), 6.1), ('Part_mg.001', 'Mount_mg.001',
                                                                                  (1.29, 12.9, NX_DECK), NX_DECK)):
        pc = pv(a, name, loc)
        k.lathe(a.part(f'Ciws_base_{name[-3:]}', 'Armor', pc), [(.8, -.02), (.85, .05), (.85, .3), (.75, .34)],
                seg=16, worn=(2,))
        if z0 > NX_DECK + 1:
            k.block(a.part(f'Ciws_bracket_{name[-3:]}', 'Armor', pc), (1.4, 1.4, z0 - NX_DECK), loc=(.3, .6, -(z0 - NX_DECK) / 2),
                    chamfer=.05)
        ciws(a, mount, (0, 0, .34), parent=name, length=1.9)
    k.clean(a)


# ============================================================================= Hydra
HY_R = 2.5                      # pressure hull radius (axis at z 0, the waterline near the top)


def _fpv(a, name, loc):
    """One FPV quadcopter on its launch cell, on its own `Part_drone*` node (a later launch rule hides it): a flat
    body, four arms on the diagonals, four rotor discs, the camera nose and a warhead tube under it."""
    p = pv(a, name, loc)
    t = name[-3:] if '.' in name else '000'
    body = a.part(f'Fpv_body_{t}', 'Team', p)
    k.block(body, (.42, .56, .16), loc=(0, 0, .06), chamfer=.03)
    arms = a.part(f'Fpv_arms_{t}', 'Undercarriage', p)
    for sx in (-1, 1):
        for sy in (-1, 1):
            u = math.atan2(sy, sx)
            arms.box((.62, .07, .05), loc=(sx * .2, sy * .22, .12), rot=(0, 0, u), bevel=0)
            k.lathe(arms, [(.07, 0), (.07, .1), (0, .1)], loc=(sx * .4, sy * .43, .1), seg=8)
            a.part(f'Fpv_rotors_{t}', 'Steel', p).cyl(.24, .02, loc=(sx * .4, sy * .43, .21), seg=14, bevel=0)
    a.part(f'Fpv_eye_{t}', 'Glass', p).box((.12, .04, .08), loc=(0, -.29, .1), bevel=0)
    k.lathe(a.part(f'Fpv_charge_{t}', 'Armor', p), [(.07, .0), (.08, .32), (.05, .38)], loc=(0, -.1, .02),
            rot=FORWARD, seg=10)


def hydra_sub(a):
    """Hydra, the drone submarine: see the module docstring."""
    _suffixed(a)
    team, arm = a.part('Hull', 'Team'), a.part('Armor', 'Armor')
    steel, dark = a.part('Steel', 'Steel'), a.part('Hull_low', 'Undercarriage')
    # The pressure hull as one lathe along the length (stern cone to the round bow), the dark lower half a second
    # skin just inside it below the waterline band, the casing deck on top.
    k.lathe(team, [(.32, -15.6), (1.05, -14.0), (1.95, -10.8), (HY_R, -6.0), (HY_R, 9.2), (2.3, 12.6), (1.75, 15.0),
                   (.95, 16.7), (.3, 17.3), (0, 17.4)], rot=FORWARD, seg=22, worn=(4,))
    k.block(dark, (5.06, 23.0, .5), loc=(0, -1.0, -.35), chamfer=0)                                   # boot topping
    k.block(a.part('Casing', 'MetalSheet'), (1.9, 25.0, .32), loc=(0, -1.2, HY_R - .12), chamfer=.04)
    k.greebles(arm, (0, -12.8, HY_R + .2), (1, 0, 0), (0, 1, 0), (1.4, 2.4), 3, seed=2761, height=(.08, .16),
               chamfer=.02)
    # Bow planes forward, the sail with its fairwater planes, the SAM box on the sail (`Mount_missile`), masts.
    k.block(arm, (5.4, 1.3, .2), loc=(0, -11.6, .9), chamfer=0)
    sail = [(0, -6.9), (.55, -6.6), (.85, -5.8), (.85, -2.6), (.55, -1.2), (0, -.9), (-.55, -1.2), (-.85, -2.6),
            (-.85, -5.8), (-.55, -6.6)]
    k.extrude(team, sail, 2.3, loc=(0, 0, HY_R + 1.05), axis='Z', chamfer=.1, taper=(.86, .92))
    k.block(arm, (4.2, 1.0, .18), loc=(0, -4.9, 3.75), chamfer=0)
    a.part('Sail_glass', 'Glass').box((.9, .05, .22), loc=(0, -6.72, 4.0), rot=(.4, 0, 0), bevel=0)
    for x, y, h in ((0, -3.0, .55), (.3, -2.2, .4), (-.3, -1.8, .3)):
        k.lathe(steel, [(.1, 0), (.1, h), (.06, h + .06)], loc=(x, y, 4.75), seg=8, worn=(1,))
    m = pv(a, 'Mount_missile', (0, -4.6, 4.75))
    k.block(a.part('Sam_base', 'Armor', m), (.7, .7, .2), chamfer=.03)
    box = a.part('Sam_box', 'Team', m)
    k.block(box, (1.0, 1.4, .5), loc=(0, 0, .18), rot=(.12, 0, 0), chamfer=.05)
    caps = a.part('Sam_caps', 'Charred', m)
    for x in (-.25, .25):
        caps.cyl(.16, .03, loc=(x, -.72, .45), rot=FORWARD, seg=10, bevel=0)
    pv(a, 'Muzzle_missile', (0, -.75, .45), 'Mount_missile')
    # The deck gun forward of the sail (`Mount_gun`).
    autocannon(a, 'Mount_gun', (0, -9.6, HY_R + .05), length=2.6, r=.08, size=(1.3, 1.6, .6))
    # The vertical launch tubes along the back aft of the sail: a raised casing, two rows of five hatches, one row
    # on each door node (`Part_doors_l` / `_r`, the parent's names).
    k.block(arm, (2.9, 8.4, .42), loc=(0, 3.7, HY_R - .2), chamfer=.08)
    for s, name in ((1, 'Part_doors_l'), (-1, 'Part_doors_r')):
        pd = pv(a, name, (s * .7, 3.7, HY_R + .03))
        lids = a.part(f'Vls_lids_{name[-1]}', 'Team', pd)
        rims = a.part(f'Vls_rims_{name[-1]}', 'Hazard', pd)
        for j in range(5):
            y = -3.2 + j * 1.6
            k.lathe(lids, [(.5, 0), (.5, .06), (.42, .1), (0, .1)], loc=(0, y, 0), seg=14, worn=(1,))
            k.ring(rims, [(.55, -.01), (.6, -.01), (.6, .04), (.55, .04)], loc=(0, y, 0), seg=14)
    # The drone deck aft: a dark tray with six FPV quadcopters on their cells (`Part_drone` .. `.005`).
    k.block(dark, (2.4, 4.6, .14), loc=(0, 10.9, HY_R - .02), chamfer=0)
    for i, (x, y) in enumerate((x, y) for y in (9.4, 10.9, 12.4) for x in (.62, -.62)):
        _fpv(a, 'Part_drone' if i == 0 else f'Part_drone.{i:03d}', (x, y, HY_R + .12))
    # The stern: cruciform planes on `Part_rudder` (the horizontal pair gives the beam), the shrouded pump-jet.
    pr = pv(a, 'Part_rudder', (0, 14.6, 0))
    fins = a.part('Rudder_fins', 'Armor', pr)
    for u, rc, h in ((0, 2.15, 2.9), (math.pi, 2.15, 2.9), (R90, 1.55, 1.7), (-R90, 1.55, 1.7)):
        fins.box((.2, 2.0, h), loc=(math.cos(u) * rc, .3, math.sin(u) * rc), rot=(0, R90 - u, 0), taper=(1, .55),
                 bevel=.04, seg=1)
    k.ring(a.part('Pumpjet', 'Team', pr), [(.75, -.6), (1.05, -.7), (1.05, -1.8), (.85, -1.9)], rot=FORWARD, seg=18,
           worn=(1,))
    k.lathe(a.part('Pumpjet_hub', 'Steel', pr), [(.36, -1.0), (.32, -2.4), (0, -2.8)], rot=FORWARD, seg=12)
    k.clean(a)


# ============================================================================= Cerberus
CB_R, CB_W, CB_X = 1.0, .85, 3.0        # tyre radius, width, axle half-track (the wide big-wheeled stance)


def _cb_body(a, name, y0, y1, axles, h=1.3, deck=1.55, nose=0.0):
    """One of the three cars on its own `Part_*` node: a ladder chassis, an armoured body with a sloped nose
    (`nose` m of glacis), fenders over every wheel, the big tyres with dished hubs. Returns the node key."""
    yc = (y0 + y1) / 2
    p = a.pivot(name, (0, yc, 0))
    t = name[5:]
    team, arm = a.part(f'Body_{t}', 'Team', p), a.part(f'Body_armor_{t}', 'Armor', p)
    dark = a.part(f'Chassis_{t}', 'Armor', p)
    L = y1 - y0
    k.block(dark, (2.0, L - .3, .45), loc=(0, 0, deck - .45), chamfer=.04)
    prof = [(-L / 2, deck), (L / 2, deck), (L / 2, deck + h), (-L / 2 + nose, deck + h), (-L / 2, deck + h * .45)]
    k.extrude(team, prof, 4.4, axis='X', chamfer=.08, corner=.06)
    k.inset(team, lambda c, n, f: n.z > .9, width=.22, depth=.025)
    tyres, hubs = a.part(f'Tyres_{t}', 'Undercarriage', p), a.part(f'Hubs_{t}', 'Team', p)
    for ya in axles:
        y = ya - yc
        for sx in (-1, 1):
            k.lathe(tyres, [(CB_R * .8, -CB_W / 2), (CB_R * .92, -CB_W / 2), (CB_R, -CB_W / 2 + .1), (CB_R, CB_W / 2 - .1),
                            (CB_R * .92, CB_W / 2), (CB_R * .8, CB_W / 2)], loc=(sx * CB_X, y, CB_R),
                    rot=parts.side_rot(sx), seg=16, caps=(False, False), worn=(2, 3))
            for hs in (sx, -sx):
                k.lathe(hubs, [(CB_R * .8, CB_W / 2 - .02), (CB_R * .62, CB_W / 2 - .1), (CB_R * .22, CB_W / 2 - .06),
                               (0, CB_W / 2 - .04)], loc=(sx * CB_X, y, CB_R), rot=parts.side_rot(hs), seg=12, worn=(0,))
            k.block(team, (1.05, 2.3, .16), loc=(sx * (CB_X - .05), y, 2.12), chamfer=.04)            # fender
            k.block(dark, (.9, .5, .7), loc=(sx * 2.45, y, 1.15), chamfer=.04)                        # axle housing
    return p


def cerberus(a):
    """Cerberus, the three-car convoy: see the module docstring."""
    _suffixed(a)
    steel, dark = a.part('Steel', 'Steel'), a.part('Couplings', 'Armor')
    # The tractor with the 125 mm turret, the anti-air car, the rocket trailer.
    pt = _cb_body(a, 'Part_tractor', -7.2, -2.0, (-6.0, -3.2), h=1.35, nose=1.3)
    pm = _cb_body(a, 'Part_middle', -.55, 3.25, (.35, 2.35), h=1.1)
    pr = _cb_body(a, 'Part_trailer', 4.45, 8.15, (5.45, 7.0), h=.9, deck=1.6)
    # Couplings: a drawbar with a hitch eye and an air line between each pair.
    for y0, y1 in ((-2.15, -.4), (3.1, 4.6)):
        k.block(dark, (.5, y1 - y0, .3), loc=(0, (y0 + y1) / 2, 1.25), chamfer=.04)
        k.ring(steel, [(.22, -.08), (.3, -.08), (.3, .08), (.22, .08)], loc=(0, y1 - .1, 1.4), seg=12)
        steel.cyl(.06, y1 - y0, loc=(.6, (y0 + y1) / 2, 1.75), rot=FORWARD, seg=6, bevel=0)
    # Tractor: driver's vision block, lamps, the turret (`Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`), the
    # 30 mm RWS on its roof (`Mount_gun`).
    a.part('Tractor_glass', 'Glass', pt).box((1.6, .05, .25), loc=(0, -2.3, 2.35), rot=(.8, 0, 0), bevel=0)
    lamps = a.part('Lamps', 'Lamp', pt)
    for sx in (-1, 1):
        lamps.box((.4, .05, .22), loc=(sx * 1.6, -2.63, 2.0), bevel=0)
    tz = 1.55 + 1.35
    t = a.pivot('Turret', (0, -3.0, tz))
    house = a.part('Turret_body', 'Team', t)
    k.extrude(house, [(-1.55, 0), (1.55, 0), (1.4, .7), (1.0, .95), (-1.0, .95), (-1.4, .7)], 3.0, loc=(0, .3, 0),
              axis='Y', chamfer=.08, corner=.05)
    tarm = a.part('Turret_armor', 'Armor', t)
    k.ring(a.part('Turret_ring', 'Steel', t), [(1.3, -.02), (1.45, -.02), (1.45, .08), (1.3, .08)], seg=24)
    k.block(tarm, (1.0, .5, .6), loc=(0, -1.35, .18), chamfer=.05)                                    # mantlet
    parts.barrel(a, 'Main_cannon', t, 0, -1.55, .5, 3.4, .12, seg=14, extractor=(.45, 1.55, .4),
                 brake_name='Muzzle_brake', brake='collar')
    a.pivot('Muzzle_main', (0, -5.1, .5), t)
    parts.hatch(a, .6, .6, .95, .32, parent=t, seg=10)
    k.greebles(tarm, (0, 1.4, .95), (1, 0, 0), (0, 1, 0), (1.8, .6), 3, seed=2771, height=(.1, .2), chamfer=.03)
    autocannon(a, 'Mount_gun', (-.65, -.3, .95), parent='Turret', length=1.1, r=.05, size=(.6, .7, .32),
               body='Armor')
    # Anti-air car: a raised pedestal, two 30 mm flak turrets side by side (`Mount_mg` right, `.001` left, the
    # parts' sides), the search radar panel between them, two fixed missile packs (`Muzzle_missile`, `.001`).
    k.block(a.part('Aa_pedestal', 'Team', pm), (3.0, 2.0, .9), loc=(0, .1, 3.1), chamfer=.08)
    for mount, x in (('Mount_mg', -.97), ('Mount_mg.001', .97)):
        autocannon(a, mount, (x, .05, 3.55), parent='Part_middle', length=2.0, r=.06, size=(1.1, 1.4, .6))
    mast = a.part('Aa_mast', 'Steel', pm)
    k.lathe(mast, [(.12, 0), (.12, 2.0), (.08, 2.05)], loc=(0, 1.3, 2.65), seg=8, worn=(1,))
    k.block(a.part('Aa_radar', 'Armor', pm), (1.7, .16, .9), loc=(0, 1.3, 5.0), rot=(-.25, 0, 0),
            chamfer=.03)
    packs = a.part('Missile_packs', 'Team', pm)
    caps = a.part('Missile_caps', 'Charred', pm)
    for i, sx in enumerate((-1, 1)):
        k.block(packs, (.75, 1.7, .55), loc=(sx * 1.75, .8, 2.95), rot=(.15, 0, 0), chamfer=.04)
        for dx in (-.18, .18):
            caps.cyl(.13, .03, loc=(sx * 1.75 + dx, -.06, 3.07), rot=FORWARD, seg=8, bevel=0)
        pv(a, 'Muzzle_missile' if i == 0 else 'Muzzle_missile.001', (sx * 1.75, -.1, 3.1), 'Part_middle')
    # Rocket trailer: the 12-tube rocket pod (`Mount_rocket`), two rear 30 mm guns (`Mount_gun.001`, `.002`).
    m = a.pivot('Mount_rocket', (0, -.1, 2.5), pr)
    k.lathe(a.part('Rocket_ring', 'Steel', m), [(.9, 0), (.95, .06), (.95, .18), (.85, .22)], seg=18, worn=(2,))
    pod = a.part('Rocket_pod', 'Team', m)
    k.block(pod, (2.4, 2.9, 1.1), loc=(0, 0, .55), rot=(.14, 0, 0), chamfer=.08)
    tubes = a.part('Rocket_tubes', 'Charred', m)
    for i in range(4):
        for j in range(3):
            tubes.cyl(.17, .03, loc=(-.84 + i * .56, -1.42, .62 + j * .36 - .2), rot=(R90 + .14, 0, 0), seg=8, bevel=0)
    pv(a, 'Muzzle_rocket', (0, -1.48, .62), 'Mount_rocket')
    for mount, x in (('Mount_gun.001', 1.5), ('Mount_gun.002', -1.5)):
        autocannon(a, mount, (x, 1.35, 2.5), parent='Part_trailer', length=1.1, r=.05, size=(.6, .7, .32),
                   body='Armor')
    k.clean(a)


# ============================================================================= Stymphalos
SY_L, SY_SPAN = 5.2, 4.4                # one drone's length and span
SY_SLOTS = [(0.0, -6.0, 1.8)] + [(s * 3.6 * i, -6.0 + 3.4 * i, 1.8 - .25 * i) for i in (1, 2, 3) for s in (1, -1)] \
    + [(0.0, 3.4, .8)]                  # the lead, three pairs, the slot drone behind the lead (all above z 0)


def _sy_drone(a, tag, parent=None):
    """One delta-wing jet drone round `parent` (its node, or the root): a faceted lofted body, the cranked delta wing
    with a worn leading edge, the dorsal intake, two canted fins, the nozzle with a small glow. Nose at -Y."""
    team, arm = a.part(f'Dr_body_{tag}', 'Team', parent), a.part(f'Dr_armor_{tag}', 'Armor', parent)
    h = SY_L / 2

    def ring(y, w, t, b):
        return [(0, y, t), (w, y, t * .4), (w * .8, y, -b * .5), (0, y, -b), (-w * .8, y, -b * .5), (-w, y, t * .4)]
    k.sharp_loft(team, [[(0, -h, 0)], ring(-h + .7, .22, .2, .14), ring(-h + 1.8, .42, .38, .26), ring(.4, .5, .42, .3),
                        ring(h - .7, .42, .3, .24), ring(h - .1, .3, .22, .2)], chamfer=.04)
    wing = [(0, -h + 1.0), (SY_SPAN / 2 * .32, -.4), (SY_SPAN / 2, h - .9), (SY_SPAN / 2 - .15, h - .45),
            (.4, h - .55), (-.4, h - .55), (-SY_SPAN / 2 + .15, h - .45), (-SY_SPAN / 2, h - .9), (-SY_SPAN / 2 * .32, -.4)]
    k.extrude(team, wing, .14, loc=(0, 0, -.05), axis='Z', chamfer=.04)
    k.block(arm, (.5, 1.5, .2), loc=(0, -.4, .42), chamfer=.04)                                       # intake
    a.part(f'Dr_intake_{tag}', 'Charred', parent).box((.42, .04, .14), loc=(0, -1.16, .44), bevel=0)
    for sx in (1, -1):
        arm.box((.08, .9, .75), loc=(sx * .42, h - .75, .55), rot=(.0, sx * .45, 0), taper=(1, .6), shift=(0, .2),
                bevel=0)
    k.lathe(a.part(f'Dr_nozzle_{tag}', 'Steel', parent), [(.2, -.25), (.24, 0), (.2, .02)], loc=(0, h - .1, .02),
            rot=(-R90, 0, 0), seg=10, worn=(1,))
    a.part(f'Dr_glow_{tag}', 'Energy', parent).cyl(.15, .02, loc=(0, h + .02, .02), rot=FORWARD, seg=10, bevel=0)
    a.part(f'Dr_eye_{tag}', 'Glass', parent).box((.16, .3, .06), loc=(0, -h + 1.1, .22), rot=(.2, 0, 0), bevel=0)


def stymphalos(a):
    """Stymphalos, eight jet drones in V formation: see the module docstring."""
    _suffixed(a)
    names = ['Part_drone'] + [f'Part_drone.{i:03d}' for i in range(1, 8)]
    for i, (name, loc) in enumerate(zip(names, SY_SLOTS)):
        _sy_drone(a, f'{i}', pv(a, name, loc))
    # The lead: the dorsal flak turret `Mount_mg` (part flak_top). The slot drone: the drone bay pod
    # `Mount_missile.001` (part drone_bay_2). The arms: the parent's other kept slots (`Mount_gun`, `.001`,
    # `Muzzle_missile`). The variant drops the bow cannon, the gondola cannon and the rear flak (their nodes
    # `Turret`, `Mount_main.001`, `Mount_mg.001` would be hidden), so they are not built.
    m = pv(a, 'Mount_mg', (0, .5, .5), 'Part_drone')
    k.lathe(a.part('Flak_ring', 'Armor', m), [(.3, 0), (.3, .08), (.2, .18), (0, .2)], seg=12)
    for x in (-.09, .09):
        k.lathe(a.part('Flak_barrels', 'Steel', m), [(.04, 0), (.04, .8), (0, .8)], loc=(x, -.1, .12), rot=FORWARD,
                seg=6)
    pv(a, 'Muzzle_mg', (0, -.92, .12), 'Mount_mg')
    m = pv(a, 'Mount_missile.001', (0, 0, -.42), 'Part_drone.007')
    pod = a.part('Bay_pod', 'Armor', m)
    k.lathe(pod, [(0, -1.1), (.2, -.95), (.24, -.5), (.24, .8), (.16, 1.0), (0, 1.05)], rot=FORWARD, seg=10)
    pv(a, 'Muzzle_missile.001', (0, -1.15, 0), 'Mount_missile.001')
    for mount, parent in (('Mount_gun', 'Part_drone.001'), ('Mount_gun.001', 'Part_drone.002')):
        m = pv(a, mount, (0, -.9, -.3), parent)
        k.lathe(a.part(f'Gun_pod_{_tag(mount)}', 'Armor', m), [(0, -.5), (.13, -.42), (.15, 0), (.12, .5), (0, .55)],
                rot=FORWARD, seg=8)
        a.part(f'Gun_bore_{_tag(mount)}', 'Steel', m).cyl(.04, .5, loc=(0, -.7, 0), rot=FORWARD, seg=6, bevel=0)
        pv(a, mount.replace('Mount_', 'Muzzle_'), (0, -.96, 0), mount)
    pv(a, 'Muzzle_missile', (0, -.4, -.2), 'Part_drone')
    k.clean(a)


def stymphalos_drone(a):
    """One Stymphalos drone on its own (for a later swarm rule that spawns them as separate units): the same airframe
    with its nose gun (`Muzzle_gun`)."""
    _suffixed(a)
    _sy_drone(a, 'solo')
    a.part('Nose_gun', 'Steel').cyl(.04, .5, loc=(0, -SY_L / 2 + .9, -.18), rot=FORWARD, seg=6, bevel=0)
    a.pivot('Muzzle_gun', (0, -SY_L / 2 + .62, -.18))
    k.clean(a)


BUILDERS = {
    'monster': (monster, dict(ao_distance=.85, grime_height=.9)),
    'nyx': (nyx, dict(ao_distance=1.0, grime_height=.8)),
    'cerberus': (cerberus, dict(ao_distance=.5, ao_strength=.6, grime_height=.3)),
    'stymphalos': (stymphalos, dict(ao_distance=.5, ao_strength=.7, ground=False)),
    'stymphalos_drone': (stymphalos_drone, dict(ao_distance=.5, ao_strength=.7, ground=False)),
    'hydra_sub': (hydra_sub, dict(ao_distance=.7, ao_strength=.75, ground=False)),
}
