"""Prompt 27 stand-in sweep (DECISIONS "27 stand-in sweep (lead pass, 2026-10-02)"; Docs/models/STANDIN_AUDIT.md):
the four defs that still drew another def's model get models of their own on the V2 kit (mb_kit27 primitives +
mb_parts27 parts), merged last in build_assets.all_builders(). Each keeps the runtime nodes its borrowed model gave
the def's weapon (no `Mount_*` or coaxial gun the def does not fire: ModelLibrary would strip them anyway). Sizes are
the sheet's drawn sizes ("Kich thuoc hien") divided by the def's `scale`: length along Y with the front at -Y (the gun
or nose counted), width along X, height along Z, ground at z 0.

  coastal_battery    was heavy_turret: a twin 130 mm AK-130-class turret on a battered concrete drum among shore
                     rocks, a fire-control director at the back (10.3 x 8.0 m)
  super_gun          was heavy_turret x 1.8: a twin super-heavy gun (2A3 Kondensator calibre, 1957) on a stepped
                     citadel, barrels raised 24 degrees, a shell hoist with a loading crane (10.3 x 8.0 m model units,
                     18.5 x 14.4 m drawn)
  bulwark_post       was mg_bunker x 0.8: a round sandbag gun post with an NSV 12.7 mm on a tripod behind a shield
                     (4.4 m model units, 3.5 m drawn)
  uav_loiter_strike  was strike_drone (the MQ-9): an MQ-1C Gray Eagle, slim wing, inverted-V tail, satcom hump,
                     four Hellfires (4.25 x 8.04 x 1.24 m, the def's modelSize)
"""
import math
import random

import mb_detail as hd
import mb_kit27 as k
import mb_p25_models2 as m2
import mb_parts27 as parts
from frontier_kit import chamfered
from mb_air import LEFT, RIGHT, Planform, _surface, _upright
from mb_p27_wave1c import _house
from mb_phase2 import _suffixed
from mb_vehicles import FORWARD, R90

TAU = math.tau
OPTS = dict(ao_distance=.6, ao_strength=.15, grime_height=.05)


# ----------------------------------------------------------------------------- shared helpers
def _rock(part, x, y, w, d, h, yaw, seed):
    """A faceted shore boulder on the ground: an irregular seven-sided outline extruded up, the top drawn in."""
    rng = random.Random(seed)
    pts = []
    for i in range(7):
        u = TAU * i / 7 + rng.uniform(-.18, .18)
        r = rng.uniform(.78, 1.0)
        pts.append((math.cos(u) * w / 2 * r, math.sin(u) * d / 2 * r))
    k.extrude(part, pts, h, loc=(x, y, h / 2), rot=(0, 0, yaw), axis='Z', chamfer=min(.14, h * .22),
              taper=(rng.uniform(.5, .66), rng.uniform(.52, .7)), ends=(False, True))


def _stripes(a, r, z, n, w=.42, d=.2):
    """A hazard-striped collar round a turret race: n alternating plates on a circle."""
    for i in range(n):
        u = (i + .5) * TAU / n
        a.part('Collar_band', 'SafetyStripe' if i % 2 else 'Charred').box(
            (w, d, .04), loc=(r * math.cos(u), r * math.sin(u), z), rot=(0, 0, u + R90), bevel=0)


def _bag_ring(a, radius, courses, seed, gap_u, gap_w, n, bag, z0=.14):
    """Courses of sandbags round a circle (`Sandbags`) with an entrance gap of half-angle gap_w round angle gap_u
    through every course (mb_p27_wave1c._sand_ring bridges its top course over the gap)."""
    rng = random.Random(seed)
    sand = a.part('Sandbags', 'Sandbag')
    for course in range(courses):
        for i in range(n):
            u = TAU * (i + .5 * (course % 2)) / n
            if abs(((u - gap_u + math.pi) % TAU) - math.pi) < gap_w:
                continue
            r = radius + rng.uniform(-.025, .025)
            k.block(sand, (bag[0] + rng.uniform(-.04, .04), bag[1], bag[2]),
                    loc=(math.cos(u) * r, math.sin(u) * r, z0 + course * bag[2]), rot=(0, 0, u + R90), chamfer=0)


def _gun_dir(e):
    """Lathe rotation for a barrel pointing forward (-Y) and raised e radians."""
    return (R90 - e, 0, 0)


# ============================================================================= coastal battery
def coastal_battery(a):
    """Coastal gun battery (10.3 x 8.0 x 4.6 m) after the AK-130 twin mount set ashore: a chamfered concrete apron
    among faceted shore rocks, a battered concrete drum with a Team band, a hazard collar round the race, a rear
    portal with a steel door; on the drum the low faceted Team gun house (`Turret`) with a bolted mantlet, two 130 mm
    barrels (`Main_cannon`, `Main_cannon_2`, `Muzzle_brake`, `Muzzle_brake_2`, `Muzzle_main`), hatches, a rangefinder
    bar, vents; a fire-control director (a concrete post with a radar cabin and dish, static) at the back left."""
    _suffixed(a)
    conc = a.part('Apron', 'Concrete')
    k.extrude(conc, chamfered(7.6, 7.7, 1.3), .3, loc=(0, .3, .15), axis='Z', chamfer=.05, ends=(False, True))
    # shore rocks round the front and sides (low: the guns sweep over them)
    rocks = a.part('Rocks', 'Rock')
    for i, (x, y, w, d, h) in enumerate(((-2.9, -3.3, 2.1, 1.5, 1.0), (-1.2, -3.9, 1.6, 1.0, .6),
                                         (1.1, -3.7, 1.8, 1.2, .75), (2.95, -3.0, 2.0, 1.7, 1.15),
                                         (3.45, -1.0, 1.1, 1.8, .8), (-3.45, -1.3, 1.1, 2.0, .9),
                                         (-3.4, 1.4, 1.2, 1.5, .55), (3.4, 1.7, 1.2, 1.3, .6))):
        _rock(rocks, x, y, w, d, h, i * 1.3, 2701 + i)
    pebbles = a.part('Pebbles', 'Rock')
    for i, (x, y) in enumerate(((-2.0, -3.0), (.1, -3.8), (2.1, -3.2), (-3.6, .2), (3.6, .4))):
        _rock(pebbles, x, y, .5, .4, .28, i * 2.1, 2711 + i)
    # the drum, its band, the race
    oy = .4
    k.lathe(a.part('Drum', 'Concrete'), [(2.8, .28), (2.8, .36), (2.55, 1.74), (2.62, 1.8), (2.62, 1.96), (0, 1.96)],
            loc=(0, oy, 0), seg=24, worn=(3, 4))
    k.ring(a.part('Drum_band', 'Team'), [(2.58, 1.3), (2.66, 1.3), (2.66, 1.62), (2.58, 1.62)], loc=(0, oy, 0), seg=24)
    k.ring(a.part('Race', 'Steel'), [(2.05, 1.94), (2.24, 1.94), (2.24, 2.04), (2.05, 2.04)], loc=(0, oy, 0), seg=24)
    for i in range(24):
        u = (i + .5) * TAU / 24
        a.part('Collar_band', 'SafetyStripe' if i % 2 else 'Charred').box(
            (.5, .26, .04), loc=(2.42 * math.cos(u), oy + 2.42 * math.sin(u), 1.97), rot=(0, 0, u + R90), bevel=0)
    # rear portal: concrete block, steel door, lamp, steps
    k.block(conc, (2.0, 1.3, 1.65), loc=(0, oy + 2.95, .3 + .825), chamfer=.06)
    k.block(a.part('Portal_roof', 'Team'), (2.2, 1.45, .16), loc=(0, oy + 2.95, 2.03), chamfer=.04)
    k.block(a.part('Door', 'Steel'), (1.0, .08, 1.15), loc=(0, oy + 3.62, .9), chamfer=0)
    for x in (-.25, .25):
        a.part('Door_ribs', 'Armor').box((.08, .05, 1.05), loc=(x, oy + 3.67, .9), bevel=0)
    a.part('Door_lamp', 'Lamp').box((.16, .06, .1), loc=(.72, oy + 3.62, 1.6), bevel=0)
    k.block(a.part('Steps', 'Concrete'), (1.3, .3, .1), loc=(0, oy + 3.71, .32), chamfer=0)
    # fire-control director at the back left: a concrete post, a radar cabin, a dish (static)
    dx, dy = -2.75, 2.9
    k.block(conc, (1.1, 1.1, 2.2), loc=(dx, dy, .3 + 1.1), chamfer=.06, taper=(.85, .85))
    k.block(a.part('FC_cabin', 'Team'), (1.0, 1.05, .6), loc=(dx, dy, 2.8), chamfer=.05)
    k.block(a.part('FC_cabin_roof', 'Armor'), (1.1, 1.15, .1), loc=(dx, dy, 3.15), chamfer=0)
    a.part('FC_glass', 'Glass').box((.8, .04, .2), loc=(dx, dy - .53, 2.88), bevel=0)
    k.lathe(a.part('FC_post', 'Steel'), [(.1, 3.2), (.1, 3.55), (.16, 3.6)], loc=(dx, dy, 0), seg=8)
    k.lathe(a.part('FC_dish', 'MetalSheet'), [(0, -.04), (.62, .12), (.66, .18), (.6, .17), (0, .03)],
            loc=(dx, dy - .1, 3.95), rot=(R90 - .35, 0, 0), seg=16, worn=(2,))
    k.lathe(a.part('FC_feed', 'Armor'), [(.06, 0), (.06, .4), (.1, .45), (0, .48)], loc=(dx, dy - .15, 3.95),
            rot=(R90 - .35, 0, 0), seg=6)
    # ---------------------------------------------------------------- turret
    t = a.pivot('Turret', (0, oy, 2.04))
    k.lathe(a.part('Turret_ring', 'Armor', t), [(2.0, 0), (2.0, .12), (1.92, .16)], seg=20, worn=(1,))
    plan = [(-1.7, -2.0), (1.7, -2.0), (2.2, -1.0), (2.2, 2.3), (1.8, 2.65), (-1.8, 2.65), (-2.2, 2.3), (-2.2, -1.0)]
    _house(a.part('Gun_house', 'Team', t), plan, 1.85, .12, ch=.08, taper=(.86, .9))
    top = 1.97
    zg = .85
    k.block(a.part('Mantlet', 'Armor', t), (2.1, .42, .8), loc=(0, -2.0, zg - .4), chamfer=.05)
    a.part('Mantlet_bolts', 'Steel', t).bolts([(x, -2.22, z) for x in (-.85, -.3, .3, .85) for z in (.62, 1.08)],
                                              r=.035, h=.03, rot=(R90, 0, 0), seg=5, bevel=0)
    L, r = 4.1, .09
    for name, brake, x in (('Main_cannon', 'Muzzle_brake', -.5), ('Main_cannon_2', 'Muzzle_brake_2', .5)):
        parts.barrel(a, name, t, x, -2.15, zg, L, r, seg=12, sleeve=1.25, extractor=(.4, 1.5, .5),
                     brake_name=brake, brake='collar')
    a.pivot('Muzzle_main', (-.5, -2.15 - L - .14, zg), t)
    # roof: hatches, sight hood, rangefinder bar, vents, kit
    parts.hatch(a, -.9, .9, top, .3, parent=t)
    parts.hatch(a, .9, 1.4, top, .3, parent=t)
    k.block(a.part('Sight_hood', 'Armor', t), (.5, .6, .3), loc=(-.95, -.65, top + .15), chamfer=.04)
    a.part('Sight_glass', 'Glass', t).box((.36, .04, .14), loc=(-.95, -.96, top + .17), bevel=0)
    k.block(a.part('Rangefinder', 'Armor', t), (3.5, .32, .3), loc=(0, 2.05, top + .15), chamfer=.04)
    for s in (-1, 1):
        a.part('Rangefinder_glass', 'Glass', t).box((.04, .2, .16), loc=(s * 1.76, 2.05, top + .16), bevel=0)
    for x in (-.4, .4):
        k.lathe(a.part('Vents', 'Steel', t), [(.12, 0), (.12, .2), (.18, .24), (.18, .28)], loc=(x, 1.0, top),
                seg=8, worn=(2,))
    k.greebles(a.part('Roof_kit', 'MetalSheet', t), (.2, .2, top), (1, 0, 0), (0, 1, 0), (2.2, 1.4), 4, seed=2721,
               height=(.05, .12), chamfer=.012)
    k.block(a.part('Loading_door', 'Armor', t), (1.2, .08, .9), loc=(0, 2.62, .75), rot=(-.16, 0, 0), chamfer=0)
    parts.antenna(a.part('Antennas', 'Steel', t), (1.55, 2.2, top), h=.45, r=.045, seg=6)
    a.part('Beacon', 'TeamGlow').sphere(.08, loc=(dx, dy, 3.65), seg=6, rings=4)
    k.clean(a)


# ============================================================================= super gun
def super_gun(a):
    """The fortress super-gun (10.3 x 8.0 x 5.3 model units; drawn at the def's scale 1.8, 18.5 x 14.4 x 9.6 m): a
    stepped concrete citadel (a chamfered lower step with a scorched blast apron in front, an octagonal upper drum
    with a Team fascia and a hazard collar), a shell hoist house at the back with its rail and a trolley of two huge
    shells, a yellow loading crane; on the drum the big Team gun house (`Turret`) with an armoured cradle, recuperators
    and two very long barrels raised 24 degrees with baffle brakes (`Main_cannon`, `Main_cannon_2`, `Muzzle_brake`,
    `Muzzle_brake_2`, `Muzzle_main`), a commander's cupola, hatches, rangefinder ears and vents."""
    _suffixed(a)
    conc = a.part('Citadel', 'Concrete')
    k.extrude(conc, chamfered(8.0, 7.8, 1.4), .55, loc=(0, 0, .275), axis='Z', chamfer=.06, ends=(False, True))
    k.block(a.part('Blast_apron', 'Charred'), (4.6, 1.3, .05), loc=(0, -3.1, .575), chamfer=0)
    for s in (-1, 1):
        k.block(a.part('Apron_kerbs', 'SafetyStripe'), (.14, 1.3, .1), loc=(s * 2.35, -3.1, .6), chamfer=0)
    # upper drum: an octagon with flat faces front and back
    k.lathe(conc, [(3.1, .55), (3.1, .62), (2.85, 1.86), (2.92, 1.9), (2.92, 2.0), (0, 2.0)], rot=(0, 0, math.pi / 8),
            seg=8, worn=(3, 4))
    k.ring(a.part('Fascia', 'Team'), [(2.9, 1.45), (2.98, 1.45), (2.98, 1.84), (2.9, 1.84)], rot=(0, 0, math.pi / 8),
           seg=8)
    ty = 0.0
    k.ring(a.part('Race', 'Steel'), [(2.2, 1.98), (2.4, 1.98), (2.4, 2.08), (2.2, 2.08)], loc=(0, ty, 0), seg=24)
    for i in range(24):
        u = (i + .5) * TAU / 24
        a.part('Collar_band', 'SafetyStripe' if i % 2 else 'Charred').box(
            (.5, .26, .04), loc=(2.58 * math.cos(u), ty + 2.58 * math.sin(u), 2.01), rot=(0, 0, u + R90), bevel=0)
    # shell hoist house on the lower step at the back left, rails and a trolley with two shells at the back right
    k.block(conc, (2.4, .9, 1.4), loc=(-1.3, 3.4, .55 + .7), chamfer=.06)
    k.block(a.part('Hoist_roof', 'Team'), (2.6, 1.05, .16), loc=(-1.3, 3.4, 2.03), chamfer=.04)
    k.block(a.part('Hoist_door', 'Steel'), (1.1, .08, 1.0), loc=(-1.3, 3.86, 1.07), chamfer=0)
    for j in range(5):
        a.part('Door_hazard', 'SafetyStripe' if j % 2 else 'Charred').box((.24, .05, .14),
                                                                         loc=(-1.78 + j * .24, 3.88, 1.64), bevel=0)
    rails = a.part('Rails', 'Steel')
    for y in (3.12, 3.62):
        rails.box((2.0, .08, .06), loc=(1.6, y, .58), bevel=0)
    k.block(a.part('Trolley', 'Armor'), (1.3, .9, .22), loc=(1.6, 3.37, .72), chamfer=.03)
    for y in (3.17, 3.57):
        k.lathe(a.part('Shells', 'Fuel'), [(.17, 0), (.17, .78), (.12, 1.0), (.04, 1.12), (0, 1.14)],
                loc=(1.03, y, 1.0), rot=(0, R90, 0), seg=10, worn=(1,))
        k.ring(a.part('Shell_bands', 'Hazard'), [(.172, .5), (.18, .5), (.18, .62), (.172, .62)], loc=(1.03, y, 1.0),
               rot=(0, R90, 0), seg=10)
    # loading crane at the back right: a slewing post and a boxed jib over the trolley, hook block
    crane = a.part('Crane', 'CraneYellow')
    k.lathe(crane, [(.26, .55), (.26, .7), (.18, .78), (.18, 3.3), (.24, 3.36), (.24, 3.5)], loc=(3.0, 2.9, 0),
            seg=10, worn=(1, 4))
    crane.limb((3.0, 2.9, 3.42), (1.6, 3.37, 3.7), .26, .26, bevel=.02)
    crane.limb((3.0, 2.9, 3.2), (2.05, 3.22, 3.62), .14, .14, bevel=0)
    a.part('Crane_cable', 'Steel').limb((1.6, 3.37, 3.6), (1.6, 3.37, 2.45), .06, .06, bevel=0)
    k.block(a.part('Hook_block', 'Armor'), (.3, .22, .3), loc=(1.6, 3.37, 2.3), chamfer=.03)
    # ---------------------------------------------------------------- turret
    t = a.pivot('Turret', (0, ty, 2.06))
    k.lathe(a.part('Turret_ring', 'Armor', t), [(2.1, 0), (2.1, .12), (2.0, .16)], seg=22, worn=(1,))
    plan = [(-1.8, -1.9), (1.8, -1.9), (2.2, -1.0), (2.2, 2.0), (1.8, 2.4), (-1.8, 2.4), (-2.2, 2.0), (-2.2, -1.0)]
    _house(a.part('Gun_house', 'Team', t), plan, 1.75, .12, ch=.08, taper=(.88, .92))
    top = 1.87
    e = math.radians(24)
    rot = _gun_dir(e)
    zg, y0 = .95, -1.9
    k.block(a.part('Cradle', 'Armor', t), (2.6, 1.3, 1.0), loc=(0, y0, zg), rot=(-e, 0, 0), chamfer=.06)
    a.part('Cradle_bolts', 'Steel', t).bolts([(x, y0 - .62, zg + .1) for x in (-1.1, -.4, .4, 1.1)], r=.04, h=.04,
                                            rot=(R90 - e, 0, 0), seg=5, bevel=0)
    L, r = 4.58, .16
    for name, brake, x in (('Main_cannon', 'Muzzle_brake', -.75), ('Main_cannon_2', 'Muzzle_brake_2', .75)):
        parts.barrel(a, name, t, x, y0, zg, L, r, seg=14, sleeve=1.25, extractor=(.36, 1.4, .6),
                     brake_name=brake, brake='baffle', rot=rot)
        k.lathe(a.part('Recuperators', 'Steel', t), [(.13, 0), (.13, 1.5), (.09, 1.58), (0, 1.6)],
                loc=(x, y0 + .1, zg + .38), rot=rot, seg=10, worn=(1,))
    a.pivot('Muzzle_main', (-.75, y0 - (L + .3) * math.cos(e), zg + (L + .3) * math.sin(e)), t)
    # roof: commander's cupola, hatches, rangefinder ears, vents, kit; a loading door at the back
    k.lathe(a.part('Cupola', 'Armor', t), [(.42, 0), (.42, .3), (.34, .38), (0, .4)], loc=(-1.2, .5, top), seg=12,
            worn=(1, 2))
    glass = a.part('Cupola_glass', 'Glass', t)
    for j in range(5):
        u = -R90 + (j - 2) * .55
        glass.box((.16, .04, .08), loc=(-1.2 + .42 * math.cos(u), .5 + .42 * math.sin(u), top + .2),
                  rot=(0, 0, u + R90), bevel=0)
    parts.hatch(a, 1.1, .8, top, .32, parent=t)
    parts.hatch(a, .1, 1.6, top, .32, parent=t)
    k.block(a.part('Rangefinder', 'Armor', t), (4.6, .36, .32), loc=(0, 1.95, top - .2), chamfer=.04)
    for s in (-1, 1):
        a.part('Rangefinder_glass', 'Glass', t).box((.04, .24, .18), loc=(s * 2.31, 1.95, top - .19), bevel=0)
    for x in (-.4, .5):
        k.lathe(a.part('Vents', 'Steel', t), [(.13, 0), (.13, .22), (.2, .26), (.2, .3)], loc=(x, -.4, top), seg=8,
                worn=(2,))
    k.greebles(a.part('Roof_kit', 'MetalSheet', t), (.3, .5, top), (1, 0, 0), (0, 1, 0), (2.4, 1.6), 5, seed=2731,
               height=(.05, .14), chamfer=.012)
    k.block(a.part('Loading_door', 'Armor', t), (1.4, .08, 1.0), loc=(0, 2.38, .8), rot=(-.16, 0, 0), chamfer=0)
    parts.antenna(a.part('Antennas', 'Steel', t), (1.6, 2.0, top), h=.45, r=.05, seg=6)
    a.part('Lamps', 'Lamp').box((.18, .06, .1), loc=(-.5, 3.87, 1.6), bevel=0)
    a.part('Beacon', 'TeamGlow').sphere(.09, loc=(3.0, 2.9, 3.58), seg=6, rings=4)
    k.clean(a)


# ============================================================================= bulwark post
def bulwark_post(a):
    """A field gun post (4.4 x 4.4 x 2.4 model units; drawn at the def's scale 0.8, 3.5 x 3.5 x 1.9 m): a round
    ring of sandbags, four courses with a gap at the back, round a Team plank floor; in the middle a tripod with an
    NSV 12.7 mm heavy machine gun on its head (`Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`) behind a Team
    shield, an ammunition box, ammunition crates, a radio with a short antenna and a flag."""
    _suffixed(a)
    k.lathe(a.part('Floor', 'Team'), [(0, 0), (1.7, 0), (1.7, .08), (1.62, .12), (0, .12)], seg=18, worn=(2,))
    _bag_ring(a, 1.9, 4, 2741, R90, .35, 16, (.74, .42, .24))
    bags = a.part('Sandbags', 'Sandbag')
    for s in (-1, 1):                                                                      # the entrance's cheeks
        k.block(bags, (.42, .74, .24), loc=(s * .64, 1.8, .14), rot=(0, 0, s * .2), chamfer=0)
    # tripod: three legs from the floor to the head
    zh = .92
    legs = a.part('Tripod', 'Steel')
    for j in range(3):
        u = R90 + j * TAU / 3
        legs.limb((math.cos(u) * .62, math.sin(u) * .62, .1), (0, 0, zh - .08), .1, .1, bevel=0)
    k.lathe(a.part('Tripod_head', 'Steel'), [(.14, zh - .12), (.14, zh - .02), (.1, zh)], seg=10, worn=(1,))
    # the gun on its turning head
    t = a.pivot('Turret', (0, 0, zh))
    zg = .24
    k.lathe(a.part('Cradle', 'Steel', t), [(.09, 0), (.09, .06), (.06, .1), (.05, .16)], seg=8, worn=(1,))
    k.block(a.part('Receiver', 'Armor', t), (.22, .9, .2), loc=(0, .12, zg), chamfer=.03)
    k.block(a.part('Feed_cover', 'Armor', t), (.2, .4, .08), loc=(0, .05, zg + .13), rot=(-.08, 0, 0), chamfer=0)
    k.block(a.part('Grips', 'Steel', t), (.06, .16, .2), loc=(0, .62, zg - .04), rot=(.35, 0, 0), chamfer=0)
    yb = -.33
    k.lathe(a.part('Main_cannon', 'Steel', t), [(.07, -.02), (.07, .16), (.055, .2), (.05, 1.25), (.04, 1.27),
                                                 (0, 1.27)], loc=(0, yb, zg), rot=FORWARD, seg=10, worn=(1,))
    k.lathe(a.part('Muzzle_brake', 'Undercarriage', t), [(.055, 1.24), (.075, 1.28), (.075, 1.44), (.06, 1.46),
                                                         (0, 1.42)], loc=(0, yb, zg), rot=FORWARD, seg=10, worn=(2,))
    a.pivot('Muzzle_main', (0, yb - 1.47, zg), t)
    k.extrude(a.part('Gun_shield', 'Team', t), [(-.46, -.3), (.46, -.3), (.4, .3), (-.4, .3)], .05,
              loc=(0, -.42, zg + .08), rot=(R90 - .14, 0, 0), axis='Z', chamfer=.012)
    k.block(a.part('Ammo_box', 'Armor', t), (.2, .32, .22), loc=(.24, .1, zg - .06), chamfer=.02)
    # crates, the radio, the antenna, a flag
    k.block(a.part('Crates', 'Crate'), (.6, .44, .34), loc=(1.05, .55, .29), rot=(0, 0, .5), chamfer=.03)
    k.block(a.part('Crates', 'Crate'), (.56, .42, .3), loc=(1.1, .1, .27), rot=(0, 0, .2), chamfer=.03)
    k.block(a.part('Crates', 'Crate'), (.5, .4, .3), loc=(-1.1, .45, .27), rot=(0, 0, -.4), chamfer=.03)
    k.block(a.part('Radio', 'Armor'), (.36, .26, .42), loc=(-1.0, .95, .33), rot=(0, 0, -.6), chamfer=.03)
    parts.antenna(a.part('Antennas', 'Steel'), (-1.05, 1.0, .54), h=1.35, r=.045, seg=6)
    a.part('Flag_pole', 'Steel').cyl(.035, 1.6, loc=(1.62, 1.1, 1.6), seg=6, bevel=0)
    a.part('Flag', 'Team').box((.55, .03, .34), loc=(1.62 + .3, 1.1, 2.22), bevel=0)
    a.part('Beacon', 'TeamGlow').sphere(.06, loc=(-1.05, 1.0, 1.94), seg=6, rings=4)
    k.clean(a)


# ============================================================================= loitering strike UAV
def uav_loiter_strike(a):
    """Loitering strike UAV after the MQ-1C Gray Eagle (4.25 x 8.04 x 1.24 m, the def's modelSize: 0.5 x real): a slim
    Team body with the satcom hump over the nose and the engine scoop on the back, a long high straight wing (from
    above, nearly twice the length), the inverted-V tail and a ventral fin, a chin sensor ball, a three-blade pusher
    (`Propeller`), two Hellfires on twin-rail launchers under each wing (`Missiles`, `Muzzle_missile`, `.001`)."""
    _suffixed(a)
    hd.mark(a, False)
    body = a.part('Fuselage', 'Team')
    m2._fuselage(body, ((-1.95, .13, -.13, .13), (-1.55, .22, -.2, .3), (-1.1, .23, -.21, .3),
                        (-.4, .21, -.19, .2), (.7, .15, -.13, .13), (1.75, .08, -.06, .07)),
                 nose=(0, -2.15, -.02), tail=(0, 1.86, 0), n=10)
    wing = Planform(.16, 4.02, -.26, -.12, .5, .25, .08, .035, .16, .23)
    for frame in (RIGHT, LEFT):
        _surface(body, wing, frame, bevel=0)
    fin = Planform(0, .82, 1.3, 1.62, .48, .26, .05, .02)
    for s in (-1, 1):
        _surface(body, fin, _upright(s * .06, -.05, 3 * math.pi / 4), lower=1.0, bevel=0)
        a.part('Wing_lights', 'TeamGlow').box((.06, .1, .05), loc=(s * 4.0, -.08, .24), bevel=0)
    _surface(body, Planform(0, .3, 1.45, 1.62, .3, .2, .04, .02), _upright(0, -.06, math.pi), lower=1.0, bevel=0)
    # engine scoop and exhaust on the back, satcom hump seam, sensor ball under the chin
    k.block(a.part('Engine_scoop', 'Armor'), (.16, .5, .1), loc=(0, .55, .17), chamfer=0, taper=(1, .7))
    k.lathe(a.part('Exhaust', 'Undercarriage'), [(.05, 0), (.05, .14), (.035, .16)], loc=(.09, 1.25, .1),
            rot=(-R90, 0, 0), seg=6)
    k.lathe(a.part('Sensor_mount', 'Armor'), [(.09, 0), (.09, -.12), (.12, -.17)], loc=(0, -1.7, -.15), seg=8)
    a.part('Sensor', 'Glass').sphere(.11, loc=(0, -1.7, -.26), seg=8, rings=5)
    parts.antenna(a.part('Antennas', 'Steel'), (0, .1, .17), h=.12, r=.03, seg=6)
    # pusher propeller
    p = a.pivot('Propeller', (0, 1.88, 0))
    k.lathe(a.part('Propeller_hub', 'Armor', p), [(.1, 0), (.1, .1), (.07, .18), (0, .23)], rot=(-R90, 0, 0),
            seg=8, worn=(1,))
    bl = a.part('Propeller_blades', 'Undercarriage', p)
    for i in range(3):
        u = i * TAU / 3 + R90
        k.block(bl, (.1, .03, .58), loc=(math.cos(u) * .31, .02, math.sin(u) * .31), rot=(0, -u + R90, 0),
                chamfer=0, taper=(.55, 1))
    # two twin-rail launchers with Hellfires under each wing
    rails = a.part('Pylons', 'Armor')
    mis = a.part('Missiles', 'Fuel')
    seek = a.part('Missile_seekers', 'Glass')
    fins = a.part('Missile_fins', 'Armor')
    points = []
    for s in (-1, 1):
        x = s * 1.55
        parts.pylon(rails, x, -.3, .1, wing.at(1.55)[3], -.02, w=.05)
        k.block(rails, (.2, .5, .05), loc=(x, -.1, -.05), chamfer=0)
        for dx in (-.08, .08):
            mx = x + dx
            k.lathe(mis, [(.045, 0), (.045, .6), (.036, .66)], loc=(mx, .22, -.12), rot=FORWARD, seg=6,
                    caps=(True, False), worn=(1,))
            k.lathe(seek, [(.036, .66), (.025, .7), (0, .72)], loc=(mx, .22, -.12), rot=FORWARD, seg=6,
                    caps=(False, False))
            fins.box((.13, .08, .012), loc=(mx, .17, -.12), bevel=0)
        points.append((x, -.52, -.12))
    m2._launch_muzzles(a, 'missile', points)
    a.pivot('Point_exhaust', (.09, 1.4, .1))
    a.pivot('Point_fire', (0, 0, .2))
    k.clean(a)


BUILDERS = {
    'coastal_battery': (coastal_battery, dict(OPTS)),
    'super_gun': (super_gun, dict(OPTS, ao_distance=.9)),
    'bulwark_post': (bulwark_post, dict(OPTS, ao_distance=.4)),
    'uav_loiter_strike': (uav_loiter_strike, dict(ao_distance=.3, ao_strength=.15, ground=False)),
}
