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

Conventions are frontier_kit's: metres, +Z up, Blender -Y is the front, +X the vehicle's left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_parts27 as parts
from mb_p20_bosses import gun_turret
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


BUILDERS = {
    'monster': (monster, dict(ao_distance=.85, grime_height=.9)),
    'nyx': (nyx, dict(ao_distance=1.0, grime_height=.8)),
}
