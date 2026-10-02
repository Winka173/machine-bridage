"""Prompt 27 wave 3 (DECISIONS "27 wave 3a ..."): ground vehicles rebuilt on the V2 kit (mb_kit27 + mb_parts27), merged
last in build_assets.all_builders() so these builders win. Same models as before: every runtime node name, pivot,
material, proportion and `_hd` twin kept (see Docs/models/WAVE3_PLAN.md).

Pass 3g: microwave_vehicle, nlos_atgm_vehicle, radar_atgm_vehicle, radar_scout, recoilless_jeep, shorad_vehicle, sp_mortar,
wheeled_howitzer.

Pass 3f: wheeled_gun, zu23_technical, rocket_technical, hover_gunboat, aa_gun_vehicle, airborne_vehicle,
fibre_fpv_carrier, interceptor_drone_vehicle.

Pass 3e: supply_truck, ammo_carrier, counter_battery_radar, ew_jammer, railgun_truck, shahed_truck, vbied, bunker_vehicle.

Pass 3d: mlrs, elite_mlrs (on the new mlrs), heavy_rocket_artillery, thermobaric_launcher, ballistic_launcher,
long_sam, sam_launcher, iron_beam.

Pass 3c: aa_vehicle (+hd), artillery (+hd), heavy_aa, elite_aa (on the new aa_vehicle), mortar_carrier, mine_layer,
smoke_carrier, shield_carrier.

Pass 3b: laser_tank, flame_tank, twin_tank, bmpt, ifv, elite_apc (on the new ifv), armored_bulldozer, engineer_vehicle.

Pass 3a (tanks): heavy_tank (+hd), light_tank (+hd), tank_destroyer (+hd), titan_tank, turtle_tank, and the three elites
on their rebuilt bases (elite_heavy_tank, elite_mbt on the V2 main_battle_tank, elite_tank_destroyer).
"""
import functools
import math
import random

from mathutils import Vector

import mb_detail as hd
import mb_kit27 as k
import mb_p25_models2 as m2
import mb_p25_new as pn
import mb_p27_experiment as exp
import mb_parts27 as parts
import mb_vehicles as mv
from mb_p25_models2 import _lights, _ellipsoid_at
from mb_vehicles import ACROSS, FORWARD, R90

TAU = math.tau


def _hatch(*args, **kw):
    kw.setdefault('seg', 8)         # octagonal coamings: the triangle budget (1.6 x) is tight on the lean old tanks
    parts.hatch(*args, **kw)


def _turret_loft(turret, outline, z1, z2, taper, chamfer=.045):
    """The turret shell as a sharp-edged loft: `outline` (x, y) at the base, narrowing by `taper` at z2 (roof)."""
    def ring(z, scale, off=0.0):
        pts = [(x * scale, y * scale) for x, y in outline]
        if off:
            pts = k.offset2d(pts, off)
        return [(x, y, z) for x, y in pts]
    k.sharp_loft(turret, [ring(.03, 1.0), ring(z1, (1 + taper) / 2 + .02), ring(z2, taper, .05)], chamfer=chamfer)


# ============================================================================= heavy tank (Object 195 / T-95)
def heavy_tank(a, detail=False):
    """Heavy tank (m2.heavy_tank) on the V2 kit: extruded hulls with chamfers, V2 running gear, library hatches, a
    one-surface 152 mm barrel with a baffle brake, smoke launchers; same nodes and pivots."""
    hd.mark(a, detail)
    parts.track_unit(a, 1.16, 6.2, .8, .3, 7, .5, sprocket_end=1, cleat_pitch=.3)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    half = 3.2
    k.extrude(armor, [(-half + .2, .38), (-half - .1, .66), (-half + .1, .86), (half - .1, .86), (half, .56),
                      (half - .15, .38)], 1.8, axis='X', chamfer=.04, corner=.03)
    k.extrude(hull, [(-half - .12, .82), (-half + .9, 1.3), (half - .05, 1.32), (half + .02, .82)], 2.9, axis='X',
              chamfer=.06, corner=.04)
    k.inset(hull, lambda c, n, f: n.z > .5 and n.y < -.2 and c.y < -2.0, width=.07, depth=.012)
    k.inset(hull, lambda c, n, f: n.y > .8, width=.04, depth=.01)
    for s in (-1, 1):
        mv._skirt(a, s, 1.45, -half + .2, half - .4, .62, 1.2, 3, thick=.08, bolts=False)
        _lights(a, (s * 1.05,), -half + .08, 1.08, size=(.14, .04, .1))
        _lights(a, (s * 1.1,), half + .03, 1.1, facing=1, size=(.12, .04, .08), lamp='Alloy')
        k.block(armor, (.46, 1.0, .18), loc=(s * 1.2, half - .55, 1.35), chamfer=.03)                 # fender bins
    for dx in (-.5, 0, .5):                                                                         # crew capsule
        _hatch(a, dx, -half + 1.35, 1.28, .2, handle=False)
    mv._periscopes(a, [(dx, -half + 1.05, 1.24, 0) for dx in (-.5, 0, .5)])
    a.part('Deck', 'Undercarriage').grille(1.6, 1.0, loc=(0, half - 1.1, 1.33), rot=(-R90, 0, 0), slats=6,
                                           depth=.05, thickness=.04)
    a.pivot('Point_exhaust', (1.2, half, 1.0))
    a.pivot('Point_fire', (0, half - 1.1, 1.38))
    steel.cyl(.95, .08, loc=(0, .45, 1.32), seg=16, bevel=0)                                           # turret ring
    t = a.pivot('Turret', (0, .45, 1.32))
    turret = a.part('Turret_body', 'Team', t)
    _turret_loft(turret, [(-.4, -1.25), (.4, -1.25), (1.08, -.8), (1.1, .9), (.9, 1.3), (-.9, 1.3), (-1.1, .9),
                          (-1.08, -.8)], .5, .55, .88, chamfer=.05)
    k.inset(turret, lambda c, n, f: n.z > .95, width=.08, depth=.012)
    tarm = a.part('Turret_armor', 'Armor', t)
    k.block(tarm, (.7, .36, .5), loc=(0, -1.3, .3), chamfer=.04, taper=(.9, .9))                      # mantlet
    for s in (-1, 1):
        k.block(tarm, (.5, .1, .45), loc=(s * .72, -1.08, .3), rot=(0, 0, s * .6), chamfer=.02)       # cheek plates
        parts.smoke_launcher(a, a.part('Smoke', 'Steel', t), 1.02, -.15, .46, s, count=2, gap=.09, r=.05, depth=.15)
    k.block(tarm, (.36, .3, .22), loc=(-.6, -.4, .66), chamfer=.03)                                    # sight
    a.part('Sight', 'Glass', t).box((.26, .03, .12), loc=(-.6, -.56, .67), bevel=0)
    k.greebles(tarm, (0, .92, .55), (1, 0, 0), (0, 1, 0), (1.3, .5), 4, seed=2711, height=(.05, .11), chamfer=.012,
               avoid=(((.55, .5, .55), .3),))
    y0, length, z = -1.48, 3.78, .32
    parts.barrel(a, 'Main_cannon', t, 0, y0, z, length, .12, seg=16 if detail else 10, sleeve=1.25,
                 extractor=(.44, 1.58, .5), brake_name='Muzzle_brake', brake='baffle')
    a.pivot('Muzzle_main', (0, y0 - length - .42, z), t)
    mv._coax(a, t, .3, -1.38, .42, length=.5, housing=.26)
    mv._roof_mg(a, t, (.55, .5, .56), length=.7, shield=False)
    if detail:
        det = a.part('Turret_bolts', 'Steel', t)
        for dx in (-.22, .22):
            for dz in (-.14, .14):
                hd.bolt(det, (dx, -1.49, .3 + dz), hd.FRONT, r=.018, h=.024)
        mv._eyes(a, [(s * .85, -.3, .56, 0) for s in (-1, 1)], parent=t)
        mv._vent(a, .1, .9, .56, parent=t)
        for u in (.1, .9):
            mv._glacis_bolts(a, (-half - .12, .82), (-half + .9, 1.3), u, -1.3, 1.3, 11)
    k.clean(a)


# ============================================================================= light tank (PT-76 / ZBD-05)
def light_tank(a, detail=False):
    """Light tank (m2.light_tank) on the V2 kit: the boat hull as a sharp-edged loft, V2 running gear, a lathed turret,
    the thin 57 mm barrel as one surface; same nodes and pivots."""
    hd.mark(a, detail)
    parts.track_unit(a, 1.02, 4.3, .62, .29, 6, .42, sprocket_end=1, teeth=6, cleat_pitch=.3)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    k.extrude(armor, [(-2.2, .34), (-2.5, .6), (-2.2, .76), (2.45, .76), (2.55, .5), (2.4, .34)], 1.62, axis='X',
              chamfer=.04, corner=.03)
    rings = []
    for y, hw, z0, z1 in ((-3.05, .14, .72, .95), (-2.7, .8, .58, 1.1), (-2.1, 1.24, .58, 1.2), (2.3, 1.26, .62, 1.22),
                          (2.62, 1.2, .64, 1.14)):
        rings.append([(hw, y, z0), (hw, y, z1), (-hw, y, z1), (-hw, y, z0)])
    k.sharp_loft(hull, rings, chamfer=.04)
    for s in (-1, 1):
        k.block(armor, (.05, 4.3, .22), loc=(s * 1.28, .05, .76), chamfer=0)                       # track guards
        _lights(a, (s * .85,), -2.4, 1.0, size=(.14, .04, .1))
        _lights(a, (s * 1.0,), 2.63, 1.0, facing=1, size=(.12, .04, .08), lamp='Alloy')
        k.lathe(a.part('Jet_ports', 'Undercarriage'), [(.16, 0), (.16, .05), (.1, .05)], loc=(s * .55, 2.58, .78),
                rot=FORWARD, seg=8, worn=(1,))
    k.block(armor, (1.6, .6, .06), loc=(0, -2.5, .92), rot=(.5, 0, 0), chamfer=0)                       # trim vane
    a.part('Deck', 'Undercarriage').grille(1.2, .9, loc=(0, 1.6, 1.2), rot=(-R90, 0, 0), slats=5, depth=.05,
                                           thickness=.04)
    _hatch(a, .0, -1.88, 1.17, .2, handle=False)                                                # driver
    mv._periscopes(a, [(dx, -2.06, 1.14, 0) for dx in (-.15, 0, .15)])
    a.pivot('Point_exhaust', (.8, 2.6, 1.0))
    a.pivot('Point_fire', (0, 1.6, 1.25))
    steel.cyl(.82, .08, loc=(0, -.6, 1.22), seg=16, bevel=0)
    t = a.pivot('Turret', (0, -.6, 1.22))
    k.lathe(a.part('Turret_body', 'Team', t), [(.9, 0), (.9, .1), (.82, .34), (.72, .46), (.6, .5), (0, .5)],
            loc=(0, .05, 0), seg=24 if detail else 16, worn=(1, 4))
    tarm = a.part('Turret_armor', 'Armor', t)
    k.block(tarm, (.46, .3, .3), loc=(0, -.86, .24), chamfer=.03, taper=(.85, .9))                      # mantlet
    k.lathe(a.part('Cupola', 'Armor', t), [(.26, .4), (.26, .52), (.2, .6), (0, .6)], loc=(-.35, .25, 0), seg=12,
            worn=(1,))
    _hatch(a, .35, .3, .5, .2, parent=t, seg=10, handle=False)
    k.block(tarm, (.36, .36, .18), loc=(0, .72, .24), chamfer=.02)                                      # bustle box
    y0, length, z = -.98, 1.95, .25
    parts.barrel(a, 'Main_cannon', t, 0, y0, z, length, .07, seg=12 if detail else 8, sleeve=1.36,
                 extractor=(.3, 1.5, .3), brake_name='Muzzle_brake', brake='collar')
    a.pivot('Muzzle_main', (0, y0 - length - .22, z), t)
    mv._coax(a, t, .26, -.86, .3, length=.34, housing=.22)
    if detail:
        det = a.part('Turret_bolts', 'Steel', t)
        hd.bolt_ring(det, hd.frame((0, .05, .51)), .62, 12, r=.014, h=.02)
        hd.bolt_ring(det, hd.frame((-.35, .25, .65)), .2, 6, r=.012, h=.018)
        mv._periscopes(a, [(-.35 + .22 * math.cos(u), .25 + .22 * math.sin(u), .58, u + R90) for u in (-2.2, -1.2)],
                       parent=t)
        mv._eyes(a, [(s * .7, -.3, .42, 0) for s in (-1, 1)], parent=t)
        for s in (-1, 1):
            hd.bolt_line(a.part('Hull_bolts', 'Steel'), (s * 1.27, -1.7, 1.0), (s * 1.27, 2.0, 1.0), 10,
                         rot=hd.side_rot(s), r=.014, h=.02)
    k.clean(a)


# ============================================================================= tank destroyer (2S25 Sprut-SD)
def tank_destroyer(a, detail=False):
    """Tank destroyer (m2.tank_destroyer) on the V2 kit: extruded hulls, V2 running gear, a lofted low turret, the long
    125 mm barrel as one surface; same nodes and pivots."""
    hd.mark(a, detail)
    parts.track_unit(a, 1.04, 5.4, .64, .24, 7, .42, sprocket_end=1, teeth=6, cleat_pitch=.3)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    k.extrude(armor, [(-2.55, .34), (-2.85, .58), (-2.7, .74), (2.7, .74), (2.8, .5), (2.65, .34)], 1.64, axis='X',
              chamfer=.04, corner=.03)
    k.extrude(hull, [(-2.85, .68), (-2.2, 1.18), (2.78, 1.2), (2.84, .68)], 2.5, axis='X', chamfer=.05, corner=.04)
    k.inset(hull, lambda c, n, f: n.z > .5 and n.y < -.2 and c.y < -2.0, width=.07, depth=.012)
    k.inset(hull, lambda c, n, f: n.y > .8, width=.04, depth=.01)
    for s in (-1, 1):
        _lights(a, (s * .95,), -2.7, 1.0, size=(.14, .04, .1))
        _lights(a, (s * 1.05,), 2.85, .98, facing=1, size=(.12, .04, .08), lamp='Alloy')
        k.block(armor, (.08, 5.0, .26), loc=(s * 1.25, .05, .9), chamfer=0)                         # side plates
    _hatch(a, 0, -1.95, 1.17, .22, handle=False)
    mv._periscopes(a, [(dx, -2.17, 1.12, 0) for dx in (-.16, 0, .16)])
    a.part('Deck', 'Undercarriage').grille(1.3, .8, loc=(0, 2.0, 1.21), rot=(-R90, 0, 0), slats=5, depth=.05,
                                           thickness=.04)
    a.pivot('Point_exhaust', (1.0, 2.86, .95))
    a.pivot('Point_fire', (0, 2.0, 1.25))
    steel.cyl(.86, .08, loc=(0, -.1, 1.2), seg=16, bevel=0)
    t = a.pivot('Turret', (0, -.1, 1.2))
    turret = a.part('Turret_body', 'Team', t)
    _turret_loft(turret, [(-.4, -1.0), (.4, -1.0), (1.0, -.55), (1.02, .8), (.8, 1.2), (-.8, 1.2), (-1.02, .8),
                          (-1.0, -.55)], .42, .5, .9, chamfer=.04)
    tarm = a.part('Turret_armor', 'Armor', t)
    k.block(tarm, (.5, .3, .36), loc=(0, -1.04, .26), chamfer=.03, taper=(.9, .9))                      # mantlet
    k.block(tarm, (.3, .3, .2), loc=(-.5, -.3, .58), chamfer=.03)                                        # sight
    a.part('Sight', 'Glass', t).box((.2, .03, .1), loc=(-.5, -.46, .58), bevel=0)
    k.block(tarm, (1.3, .3, .26), loc=(0, 1.3, .24), chamfer=.03)                                        # bustle bins
    k.greebles(tarm, (0, .5, .5), (1, 0, 0), (0, 1, 0), (1.2, .5), 3, seed=2713, height=(.04, .09), chamfer=.01,
               avoid=(((.5, .35, .5), .3),))
    _hatch(a, .5, .35, .5, .22, parent=t, seg=10, handle=False)
    y0, length, z = -1.18, 3.6, .27
    parts.barrel(a, 'Main_cannon', t, 0, y0, z, length, .08, seg=16 if detail else 10, sleeve=1.25,
                 extractor=(.45, 1.62, .4), brake_name='Muzzle_brake', brake='collar')
    a.pivot('Muzzle_main', (0, y0 - length - .14, z), t)
    mv._roof_mg(a, t, (.5, .35, .52), length=.7, shield=False)
    if detail:
        det = a.part('Turret_bolts', 'Steel', t)
        for dx in (-.16, .16):
            for dz in (-.1, .1):
                hd.bolt(det, (dx, -1.2, .26 + dz), hd.FRONT, r=.016, h=.022)
        for s in (-1, 1):
            hd.bolt_line(a.part('Hull_bolts', 'Steel'), (s * 1.3, -2.0, .98), (s * 1.3, 2.2, .98), 10,
                         rot=hd.side_rot(s), r=.014, h=.02)
        mv._periscopes(a, [(-.5 + .2 * math.cos(u), .35 + .2 * math.sin(u), .5, u + R90) for u in (-2.2, -1.2)],
                       parent=t)
        mv._eyes(a, [(s * .8, -.3, .5, 0) for s in (-1, 1)], parent=t)
    k.clean(a)


# ============================================================================= titan tank (Object 279 / Ratte)
def titan_tank(a):
    """Super tank (m2.titan_tank) on the V2 kit: V2 running gear on all four tracks, extruded hulls, a lofted turret, the
    twin 140 mm barrels as lathed surfaces; same nodes, pivots and gilt bands."""
    from mb_phase2 import _suffixed
    _suffixed(a)
    hd.mark(a, False)
    parts.track_unit(a, 2.24, 8.0, .98, .34, 6, .6, sprocket_end=1, teeth=6, cleat_pitch=.3)
    parts.track_unit(a, 1.5, 7.4, .9, .32, 4, .56, sprocket_end=1, teeth=5, cleat_pitch=.6, wheel_seg=6,
                     return_rollers=1)           # inner pair
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    gilt = a.part('Gilt', 'Gilded')
    k.extrude(armor, [(-3.3, .4), (-3.7, .7), (-3.5, .92), (3.7, .92), (3.8, .6), (3.5, .4)], 2.3, axis='X',
              chamfer=.04, corner=.03)
    k.extrude(hull, [(-4.05, .92), (-2.7, 1.6), (3.95, 1.62), (4.05, .92)], 3.96, axis='X', chamfer=.06, corner=.04)
    k.inset(hull, lambda c, n, f: n.z > .5 and n.y < -.2 and c.y < -2.0, width=.09, depth=.012)
    k.inset(hull, lambda c, n, f: n.y > .8, width=.05, depth=.01)
    for s in (-1, 1):
        mv._skirt(a, s, 2.56, -3.9, 3.9, .75, 1.3, 3, thick=.1, bolts=False)                          # outer skirts
        k.block(hull, (.62, 7.9, .1), loc=(s * 2.24, 0, 1.33), chamfer=0)                              # outer fenders
        k.block(armor, (.5, 1.1, .5), loc=(s * 2.2, 2.9, 1.6), chamfer=.04)                            # rear bins
        gilt.box((.06, 5.0, .08), loc=(s * 2.62, 0, 1.24), bevel=0)                                    # gilt skirt band
        k.block(steel, (.2, .2, .16), loc=(s * .7, -3.75, .72), chamfer=0)                             # tow hooks
        # The front corner sub-turrets: a small dome with twin machine guns each.
        k.lathe(armor, [(.42, 0), (.42, .26), (.38, .3), (0, .3)], loc=(s * 1.55, -2.9, 1.37), seg=14, worn=(1,))
        a.part('Sub_turrets', 'Team').sphere((.38, .38, .24), loc=(s * 1.55, -2.9, 1.67), seg=12, rings=5, cut=0)
        for dx in (-.08, .08):
            steel.cyl(.045, .6, loc=(s * 1.55 + dx, -3.45, 1.72), rot=FORWARD, seg=6, bevel=0)
    _lights(a, (-1.0, 1.0), -3.75, 1.02)
    _lights(a, (-1.5, 1.5), 4.06, 1.2, facing=1, size=(.16, .04, .1), lamp='Alloy')
    _hatch(a, 0, -2.45, 1.52, .28, handle=False)                                                  # driver
    mv._periscopes(a, [(dx, -2.75, 1.47, 0) for dx in (-.18, 0, .18)])
    a.part('Deck', 'Undercarriage').grille(2.0, 1.0, loc=(0, 3.4, 1.63), rot=(-R90, 0, 0), slats=5, depth=.07,
                                           thickness=.05)
    for s in (-1, 1):
        mv._exhaust(a, s * 1.2, 4.05, 1.25, .5, .24)
    k.greebles(armor, (0, .6, 1.62), (1, 0, 0), (0, 1, 0), (3.0, 1.2), 5, seed=2714, height=(.05, .12), chamfer=.015,
               avoid=(((0, -.3, 1.62), 1.8), ((0, 2.55, 1.62), .7)))
    steel.cyl(1.55, .1, loc=(0, -.3, 1.62), seg=20, bevel=0)                                           # turret ring
    a.pivot('Point_exhaust', (1.2, 4.1, 1.25))
    a.pivot('Point_fire', (0, 3.4, 1.7))
    # The rear sub-turret on its own mount, at the back of the deck.
    m = a.pivot('Mount_mg', (0, 2.55, 1.62))
    k.lathe(a.part('Rear_turret', 'Team', m), [(.5, 0), (.5, .3), (.42, .36), (0, .36)], seg=14, worn=(1,))
    k.block(a.part('Rear_turret_armor', 'Armor', m), (.34, .3, .24), loc=(0, -.42, .26), chamfer=.03)
    a.part('RWS_gun', 'Steel', m).cyl(.06, .8, loc=(0, -.95, .28), rot=FORWARD, seg=6, bevel=0)
    a.pivot('Muzzle_mg', (0, -1.38, .28), m)
    # The big wide turret.
    t = a.pivot('Turret', (0, -.3, 1.62))
    turret = a.part('Turret_body', 'Team', t)
    _turret_loft(turret, [(-.9, -2.1), (.9, -2.1), (1.75, -1.4), (1.8, 1.2), (1.5, 1.95), (-1.5, 1.95), (-1.8, 1.2),
                          (-1.75, -1.4)], .9, .95, .9, chamfer=.06)
    k.inset(turret, lambda c, n, f: n.z > .95, width=.1, depth=.012)
    tarm = a.part('Turret_armor', 'Armor', t)
    k.block(tarm, (2.0, .4, .7), loc=(0, -2.12, .5), chamfer=.05, taper=(.92, .9))                     # mantlet
    for s in (-1, 1):
        k.block(tarm, (.7, .1, .7), loc=(s * 1.35, -1.8, .48), rot=(0, 0, s * .66), chamfer=.02)        # cheek plates
        k.block(tarm, (.24, 1.5, .5), loc=(s * 1.78, .5, .42), chamfer=.03)                            # side bins
        k.block(a.part('APS', 'Steel', t), (.3, .3, .2), loc=(s * 1.1, .9, 1.03), chamfer=.02)        # APS blocks
    k.block(tarm, (2.6, .5, .5), loc=(0, 2.0, .42), chamfer=.04)                                       # bustle box
    k.greebles(tarm, (0, 1.2, .95), (1, 0, 0), (0, 1, 0), (2.4, 1.0), 4, seed=2715, height=(.05, .1), chamfer=.012,
               avoid=(((-.9, .5, .95), .45), ((.9, .5, .95), .45)))
    a.part('Turret_gilt', 'Gilded', t).box((3.2, .06, .1), loc=(0, -1.0, .96), bevel=0)
    k.lathe(a.part('Cupola', 'Armor', t), [(.38, .88), (.38, 1.06), (.3, 1.14), (0, 1.14)], loc=(-.9, .5, 0), seg=12,
            worn=(1,))
    _hatch(a, .9, .5, .95, .3, parent=t, seg=10, handle=False)
    a.part('Sight', 'Glass', t).box((.3, .03, .14), loc=(-.9, .15, 1.1), bevel=0)
    # Twin 140 mm guns, drawn 15 % thick, 2.5 m past the nose.
    y0, length, z = -2.32, 4.35, .52
    for x, suffix in ((-.62, ''), (.62, '_2')):
        parts.barrel(a, f'Main_cannon{suffix}', t, x, y0, z, length, .12, seg=10, sleeve=1.25,
                     extractor=(.4, 1.58, .5), brake_name=f'Muzzle_brake{suffix}', brake='collar')
        a.part(f'Main_cannon{suffix}_gilt', 'Gilded', t).cyl(.16, .08, loc=(x, y0 - length * .12, z), rot=FORWARD,
                                                             seg=10, bevel=0)
    a.pivot('Muzzle_main', (-.62, y0 - length - .24, z), t)
    mv._coax(a, t, 0, -2.3, .7, length=.45, housing=.28)
    # The ATGM pods on the turret sides: two-round boxes, their tube mouths the launch face.
    for s in (-1, 1):
        x = s * 1.95
        k.block(a.part('ATGM_pod', 'Armor', t), (.36, 1.1, .36), loc=(x, -.8, .9), chamfer=.03)
        k.block(tarm, (.2, .4, .2), loc=(s * 1.8, -.7, .78), chamfer=0)                                # pod mounts
        for dz in (-.08, .08):
            a.part('Tubes_bore', 'Undercarriage', t).cyl(.07, .03, loc=(x, -1.36, .9 + dz), rot=FORWARD, seg=8,
                                                         bevel=0)
    a.pivot('Muzzle_missile', (-1.95, -1.38, .9), t)
    a.pivot('Muzzle_missile__001', (1.95, -1.38, .9), t)
    k.clean(a)


# ============================================================================= turtle tank (T-72 under a shell)
def turtle_tank(a):
    """Turtle tank (m2.turtle_tank) on the V2 kit: V2 running gear under the shell's edge, the shell a finer ellipsoid
    with seams, patches and netting as before, a lathed barrel with a collar brake; same nodes and pivots."""
    rng = random.Random(7272)
    hd.mark(a, False)
    parts.track_unit(a, 1.12, 5.4, .75, .3, 6, .46, sprocket_end=1, teeth=6, cleat_pitch=.3)
    armor = a.part('Armor', 'Armor')
    k.extrude(armor, [(-2.6, .38), (-2.9, .62), (-2.7, .84), (2.75, .84), (2.85, .55), (2.7, .38)], 1.72, axis='X',
              chamfer=.04, corner=.03)
    r, c = (1.5, 3.05, 2.3), (0, .15, .42)
    a.part('Shell', 'Team').sphere(r, loc=c, seg=18, rings=8, cut=0)
    seams = a.part('Shell_seams', 'Armor')
    for y in (-1.6, -.5, .6, 1.7):
        kk = math.sqrt(max(0, 1 - ((y - c[1]) / r[1]) ** 2))
        seams.box((.08, .12, .08), loc=(0, y, c[2] + r[2] * kk + .02), bevel=0)
    plates = ('MetalSheet', 'Rust', 'Armor')
    for i in range(14):
        u, v = rng.uniform(0, TAU), rng.uniform(.15, 1.0)
        p, n = _ellipsoid_at(r, c, u, v)
        rot = Vector((0, 0, 1)).rotation_difference(n).to_euler('XYZ')
        m = plates[i % 3]
        k.block(a.part(f'Shell_patches_{m}', m), (rng.uniform(.5, .9), rng.uniform(.5, 1.0), .05),
                loc=tuple(p + n * .02), rot=tuple(rot), chamfer=0)
    net = a.part('Anti_drone_net', 'Undercarriage')
    for kk in range(-2, 3):
        u = R90 + kk * .1
        pts = [_ellipsoid_at(r, c, u, v)[0] for v in (.55, .9, 1.25)]
        for p, q in zip(pts, pts[1:]):
            net.limb(tuple(p + Vector((0, 0, .03))), tuple(q + Vector((0, 0, .03))), .04, .04, bevel=0)
    for kk in range(-2, 3):
        pts = [_ellipsoid_at(r, c, u, .55 + kk * .12)[0] for u in (R90 - .5, R90, R90 + .5)]
        for p, q in zip(pts, pts[1:]):
            net.limb(tuple(p + Vector((0, 0, .03))), tuple(q + Vector((0, 0, .03))), .04, .04, bevel=0)
    slits = a.part('Slits', 'Undercarriage')
    for u in (-R90 - .35, -R90 + .35):
        p, n = _ellipsoid_at(r, c, u, .35)
        slits.box((.5, .06, .08), loc=tuple(p + n * .015), rot=(0, 0, u + R90), bevel=0)
    p, n = _ellipsoid_at(r, c, -R90, .33)
    slits.box((.5, .1, .4), loc=tuple(p + n * .01), rot=(-.4, 0, 0), bevel=0)                          # gun slot
    a.pivot('Point_exhaust', (.9, 2.9, .9))
    a.pivot('Point_fire', (0, .3, 2.6))
    t = a.pivot('Turret', (0, .1, 1.3))
    a.part('Turret_body', 'Armor', t).sphere((.95, 1.0, .6), loc=(0, 0, 0), seg=12, rings=5, cut=0)
    y0, length, z = -.9, 3.3, .45
    parts.barrel(a, 'Main_cannon', t, 0, y0, z, length, .085, seg=10, sleeve=1.3, extractor=(.5, 1.6, .4),
                 brake_name='Muzzle_brake', brake='collar')
    a.pivot('Muzzle_main', (0, y0 - length - .14, z), t)
    mv._coax(a, t, -.22, -2.9, .45, length=.3, housing=.2)
    k.clean(a)


# ============================================================================= laser tank
def laser_tank(a):
    """Laser tank (m2.laser_tank) on the V2 kit: extruded hulls, V2 running gear, a chamfered turret block, the beam
    director's housing lathed; same nodes, pivots and glowing radiators."""
    hd.mark(a, False)
    parts.track_unit(a, 1.1, 5.6, .72, .28, 6, .46, sprocket_end=1, teeth=6, cleat_pitch=.3)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    k.extrude(armor, [(-2.7, .36), (-3.0, .62), (-2.8, .82), (2.85, .82), (2.95, .55), (2.8, .36)], 1.72, axis='X',
              chamfer=.04, corner=.03)
    k.extrude(hull, [(-3.05, .78), (-2.3, 1.3), (2.95, 1.32), (3.02, .78)], 2.7, axis='X', chamfer=.05, corner=.04)
    k.inset(hull, lambda c, n, f: n.z > .5 and n.y < -.2 and c.y < -2.2, width=.07, depth=.012)
    k.inset(hull, lambda c, n, f: n.y > .8, width=.04, depth=.01)
    glow = a.part('Radiator_glow', 'Energy')
    for s in (-1, 1):
        k.block(a.part('Radiators', 'Undercarriage'), (.06, 3.2, .3), loc=(s * 1.36, .6, 1.08), chamfer=0)
        for i in range(4):
            glow.box((.03, .6, .06), loc=(s * 1.395, -.6 + i * .8, 1.08), bevel=0)
        _lights(a, (s * 1.0,), -2.95, 1.0, size=(.14, .04, .1))
        _lights(a, (s * 1.05,), 3.03, 1.05, facing=1, size=(.12, .04, .08), lamp='Alloy')
    _hatch(a, .7, -2.0, 1.3, .2, handle=False)
    a.part('Deck', 'Undercarriage').grille(1.4, .9, loc=(0, 2.1, 1.33), rot=(-R90, 0, 0), slats=5, depth=.05,
                                           thickness=.04)
    a.pivot('Point_exhaust', (1.0, 3.0, 1.0))
    a.pivot('Point_fire', (0, 2.1, 1.4))
    steel.cyl(.9, .08, loc=(0, -.3, 1.32), seg=16, bevel=0)
    t = a.pivot('Turret', (0, -.3, 1.32))
    turret = a.part('Turret_body', 'Team', t)
    k.block(turret, (1.8, 2.0, .5), loc=(0, .3, .25), chamfer=.06, taper=(.9, .9))
    k.inset(turret, lambda c, n, f: n.z > .95, width=.08, depth=.012)
    tarm = a.part('Turret_armor', 'Armor', t)
    k.greebles(tarm, (0, .8, .5), (1, 0, 0), (0, 1, 0), (1.3, .7), 3, seed=2721, height=(.05, .1), chamfer=.012)
    for s in (-1, 1):
        k.block(a.part('Director_trunnions', 'Armor', t), (.2, .6, 1.0), loc=(s * .95, -.95, .55), chamfer=.03)
    tilt = math.radians(40)
    axis = Vector((0, -math.cos(tilt), math.sin(tilt)))
    c = Vector((0, -1.1, .75))
    rot = (R90 - tilt, 0, 0)
    k.lathe(a.part('Main_cannon_head', 'Armor', t), [(0, -.13), (.66, -.13), (.72, -.09), (.72, .09), (.66, .13),
                                                      (0, .13)], loc=tuple(c), rot=rot, seg=16, worn=(2, 3))
    a.part('Main_cannon_hood', 'TeamGlow', t).cyl(.68, .04, loc=tuple(c + axis * .14), rot=rot, seg=16, bevel=0)
    a.part('Main_cannon_lens', 'Glass', t).cyl(.6, .04, loc=tuple(c + axis * .15), rot=rot, seg=16, bevel=0)
    k.lathe(a.part('Main_cannon', 'Steel', t), [(.12, 0), (.12, .08), (.06, .2), (0, .2)],
            loc=tuple(c + axis * .25), rot=rot, seg=8, worn=(1,))
    a.part('Sight', 'Glass', t).box((.2, .03, .12), loc=(.6, -.72, .4), bevel=0)
    a.pivot('Muzzle_main', tuple(c + axis * .4), t)
    k.clean(a)


# ============================================================================= flame tank (TO-55)
def flame_tank(a):
    """Flame tank (mb_p25_models.flame_tank) on the V2 kit: V2 running gear, extruded T-55 hull, a lathed dome turret,
    fuel tanks as rounded lathed drums, the projector as one surface with a collar and the pilot-light glow."""
    hd.mark(a, False)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    parts.track_unit(a, 1.03, 5.1, .74, .31, 5, .46, sprocket_end=1, cleat_pitch=.3)
    top = .74
    for s in (-1, 1):
        k.block(armor, (.5, 5.3, .05), loc=(s * 1.08, -.05, top + .04), chamfer=0)                        # fenders
        for y in (-1.2, .1):
            k.block(armor, (.38, .9, .28), loc=(s * 1.1, y, top + .2), chamfer=.03)                       # fender boxes
        mv._headlight(a, s * .7, -2.62, .88, guard=False)
        mv._taillight(a, s * .8, 2.6, .8)
    k.extrude(hull, [(-2.6, .42), (-2.64, .62), (-1.75, 1.04), (2.5, 1.06), (2.6, .9), (2.6, .45)], 1.6, axis='X',
              chamfer=.05, corner=.04)
    k.inset(hull, lambda c, n, f: n.z > .5 and n.y < -.2 and c.y < -1.6, width=.07, depth=.012)
    k.block(armor, (1.5, .9, .05), loc=(0, .95, 1.08), chamfer=0)                                      # engine grille
    a.part('Deck', 'Undercarriage').grille(1.3, .8, loc=(0, .95, 1.1), rot=(-R90, 0, 0), slats=5, depth=.08,
                                           thickness=.05)
    _hatch(a, .5, -1.62, 1.04, .2, handle=False)                                                       # driver
    fuel = a.part('Fuel_tanks', 'BarrelRed')
    for s in (-1, 1):
        xx = s * .5
        k.lathe(fuel, [(0, -.8), (.3, -.8), (.36, -.7), (.36, .7), (.3, .8), (0, .8)], loc=(xx, 2.25, 1.44),
                rot=FORWARD, seg=12, worn=(2, 3))
        for y in (1.7, 2.8):
            k.ring(steel, [(.36, -.04), (.39, -.04), (.39, .04), (.36, .04)], loc=(xx, y, 1.44), rot=FORWARD, seg=12,
                   worn=(1,))
        k.block(armor, (.62, 1.5, .22), loc=(xx, 2.25, 1.12), chamfer=.03)                              # cradle
        steel.box((.12, .9, .12), loc=(s * .22, 1.1, 1.18), bevel=0)                                  # feed pipe
    a.pivot('Point_exhaust', (.9, 2.62, .9))
    a.pivot('Point_fire', (0, 2.25, 1.8))
    t = a.pivot('Turret', (0, -.45, 1.05))
    k.lathe(a.part('Turret_body', 'Team', t), [(1.0, -.12), (1.0, .0), (.95, .22), (.8, .42), (.55, .58), (.25, .65),
                                                (0, .66)], seg=20, worn=(1, 3))
    steel.cyl(.96, .1, loc=(0, -.45, 1.03), seg=16, bevel=0)                                           # turret ring
    tarm = a.part('Turret_armor', 'Armor', t)
    k.block(tarm, (.46, .36, .42), loc=(0, -.92, .3), chamfer=.05, taper=(.85, .85))                   # mantlet
    k.lathe(a.part('Cupola', 'Armor', t), [(.26, .58), (.26, .74), (.2, .82), (0, .82)], loc=(-.35, .3, 0), seg=12,
            worn=(1,))
    _hatch(a, .38, .35, .6, .22, parent=t, seg=10)                                                      # loader
    k.block(tarm, (.32, .24, .28), loc=(-.42, -.86, .52), chamfer=.03)                                  # searchlight
    a.part('Lamps', 'Lamp', t).box((.26, .03, .2), loc=(-.42, -.99, .52), bevel=0)
    k.greebles(tarm, (0, .2, .62), (1, 0, 0), (0, 1, 0), (.9, .5), 3, seed=2722, height=(.04, .08), chamfer=.01,
               avoid=(((-.35, .3, .62), .35), ((.38, .35, .62), .35)))
    y0, length_p, z = -1.1, 2.3, .3
    parts.barrel(a, 'Main_cannon', t, 0, y0, z, length_p, .12, seg=12, sleeve=1.42, extractor=(.4, 1.42, 1.1),
                 brake_name='Muzzle_brake', brake='collar')
    a.part('Muzzle_brake_glow', 'Alloy', t).cyl(.1, .03, loc=(0, y0 - length_p - .2, z), rot=FORWARD, seg=10,
                                                bevel=0)
    a.pivot('Muzzle_main', (0, y0 - length_p - .22, z), t)
    mv._coax(a, t, .36, -1.02, .38, length=.36, housing=.24)
    k.clean(a)


# ============================================================================= twin tank (the MBT 15 % larger)
def twin_tank(a, detail=False):
    """Twin-gun tank (mb_p25_models.twin_tank) on the V2 kit: the V2 main battle tank drawn with the wide turret and two
    barrels, then scaled 1.15; `Main_cannon` / `_2`, `Muzzle_brake` / `_2` and every other node as before."""
    import mb_p25_models as p25
    w = 1.18
    hd.mark(a, detail)
    half = p25.MBT_HULL / 2
    parts.track_unit(a, 1.18, 5.72, .86, .27, 7, .5, sprocket_end=1, cleat_pitch=.3)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    k.extrude(armor, [(-2.55, .4), (-2.97, .8), (-2.9, .95), (2.88, .95), (2.9, .5), (2.62, .4)], 1.84, axis='X',
              chamfer=.04, corner=.03)
    k.extrude(hull, [(-half - .02, .84), (-2.05, 1.18), (2.78, 1.21), (half, 1.08), (half, .88)], 2.9, axis='X',
              chamfer=.06, corner=.04)
    k.inset(hull, lambda c, n, f: n.z > .5 and n.y < -.2 and c.y < -2.0, width=.07, depth=.012)
    k.inset(hull, lambda c, n, f: n.y > .8, width=.04, depth=.01)
    for s in (-1, 1):
        mv._skirt(a, s, 1.47, -2.82, -1.52, .5, 1.17, 1, thick=.1, bolts=False)
        mv._skirt(a, s, 1.46, -1.49, 2.55, .56, 1.17, 2, thick=.07, bolts=False)
        k.block(steel, (.16, .16, .12), loc=(s * .42, -2.99, .66), chamfer=.02)                  # tow hooks
        mv._headlight(a, s * 1.12, -2.72, 1.1, guard=False)
        mv._taillight(a, s * 1.1, half + .02, 1.0)
        mv._exhaust(a, s * .5, half + .02, .72, .5, .22)
        k.block(armor, (.46, .95, .2), loc=(s * 1.18, 1.95, 1.29), chamfer=.03)                  # fender bins
        k.block(armor, (.36, .3, .1), loc=(s * .75, .95, 1.24), chamfer=.02)                     # deck fillers
    _hatch(a, -.45, -1.72, 1.18, .24, handle=False)
    mv._periscopes(a, [(-.45 + dx, -2.05, 1.18, 0) for dx in (-.17, 0, .17)])
    a.part('Deck', 'Undercarriage').grille(1.5, .9, loc=(0, 1.92, 1.19), rot=(-R90, 0, 0), slats=6, depth=.1,
                                           thickness=.05)
    mv._grille_frame(a, 0, 1.92, 1.21, 1.5, .9)
    steel.cyl(1.02, .1, loc=(p25.MBT_TURRET[0], p25.MBT_TURRET[1], 1.21), seg=16, bevel=0)       # turret ring
    a.pivot('Point_exhaust', (0, half + .1, .75))
    a.pivot('Point_fire', (0, 1.92, 1.25))

    t = a.pivot('Turret', p25.MBT_TURRET)
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-.3, -1.5), (.3, -1.5), (1.12, -1.02), (1.2, -.85), (1.2, 1.05), (1.08, 1.72), (.92, 1.9),
               (-.92, 1.9), (-1.08, 1.72), (-1.2, 1.05), (-1.2, -.85), (-1.12, -1.02)]
    outline = [(x * w + (.3 * (1 if x > 0 else -1) if abs(x) < .5 else 0), y) for x, y in outline]
    _turret_loft(turret, outline, .66, .71, .93, chamfer=.045)
    k.inset(turret, lambda c, n, f: n.z > .95, width=.08, depth=.012)
    tarm = a.part('Turret_armor', 'Armor', t)
    k.block(tarm, (1.36, .34, .46), loc=(0, -1.52, .38), chamfer=.04, taper=(.92, .9))           # mantlet
    for s in (-1, 1):
        k.block(tarm, (.62, .1, .44), loc=(s * .72 * w * 1.2, -1.3, .37), rot=(0, 0, s * .54), chamfer=.02)
    k.block(tarm, (1.62 * w, .34, .42), loc=(0, 2.05, .36), chamfer=.03)                         # bustle box
    a.part('Tarp', 'Canvas', t).cyl(.13, 1.3 * w, loc=(0, 2.02, .7), rot=ACROSS, seg=8, bevel=0)
    for s in (-1, 1):
        k.block(tarm, (.18, 1.1, .4), loc=(s * 1.36, 1.0, .28), chamfer=.03)                     # bustle bins
        parts.smoke_launcher(a, a.part('Smoke', 'Steel', t), 1.07 * w, -.5, .58, s, count=3, gap=.08, r=.05,
                             depth=.15)
    k.greebles(tarm, (0, 1.35, .72), (1, 0, 0), (0, 1, 0), (1.2, .5), 3, seed=2723, height=(.05, .1), chamfer=.012)
    k.lathe(a.part('Turret_steel', 'Steel', t), [(.15, -.08), (.15, .06), (.13, .08)], loc=(-.62 * w, .2, .78),
            seg=12, worn=(1,))
    k.block(tarm, (.34, .3, .17), loc=(-.62 * w, .2, .92), chamfer=.03)
    glass = a.part('Sight', 'Glass', t)
    glass.box((.24, .03, .1), loc=(-.62 * w, .04, .93), bevel=0)
    k.block(tarm, (.36, .42, .24), loc=(-.66 * w, -.95, .8), chamfer=.03)
    glass.box((.26, .03, .13), loc=(-.66 * w, -1.17, .82), bevel=0)
    _hatch(a, .55 * w, .45, .72, .27, parent=t, seg=10)
    mv._periscopes(a, [(.55 * w, .08, .72, 0)], parent=t)
    y0, length, z = -1.66, 3.26, .38
    for x, suffix in ((-.38, ''), (.38, '_2')):
        parts.barrel(a, f'Main_cannon{suffix}', t, x, y0, z, length, .085, seg=14 if detail else 10, sleeve=1.235,
                     extractor=(.4, 1.65, .42), brake_name=f'Muzzle_brake{suffix}', brake='collar')
    a.pivot('Muzzle_main', (0, y0 - length - .15, z), t)
    mv._coax(a, t, 0, -1.6, .56, length=.4, housing=.26)
    parts.mg_mount(a, t, (.55 * w, .45, .74), length=.8, shield=False)
    if detail:
        for u in (.08, .92):
            mv._glacis_bolts(a, (-half - .02, .84), (-2.05, 1.18), u, -1.3, 1.3, 11)
        for s in (-1, 1):
            mv._shackle(a, s * .42, -3.07, .56)
            mv._filler(a, s * .75, 1.2, 1.21)
        mv._eyes(a, [(s * 1.25, -1.9, 1.19, 0) for s in (-1, 1)] + [(s * 1.25, 2.5, 1.21, R90) for s in (-1, 1)])
        mv._eyes(a, [(-.95, 1.5, .72, 0), (.95, 1.5, .72, 0), (.85, -.7, .72, -.5)], parent=t)
        mv._vent(a, .1, 1.1, .72, parent=t)
    p25._scale_asset(a, p25.TWIN_K)
    k.clean(a)


# ============================================================================= IFV (M2 Bradley)
def ifv(a):
    """Infantry fighting vehicle (m2.ifv) on the V2 kit: extruded hulls, V2 running gear, a lofted turret, the 25 mm
    gun as one surface, a chamfered TOW box; same nodes (Launcher_box, Tubes, Muzzle_missile) and pivots."""
    hd.mark(a, False)
    parts.track_unit(a, 1.23, 5.0, .78, .27, 6, .42, sprocket_end=-1, cleat_pitch=.3)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    k.extrude(armor, [(-2.25, .38), (-2.55, .66), (-2.4, .86), (2.45, .86), (2.55, .6), (2.4, .38)], 1.9, axis='X',
              chamfer=.04, corner=.03)
    k.extrude(hull, [(-2.58, .8), (-1.85, 1.62), (2.52, 1.64), (2.58, .8)], 2.86, axis='X', chamfer=.05, corner=.04)
    k.inset(hull, lambda c, n, f: n.z > .5 and n.y < -.2 and c.y < -1.9, width=.07, depth=.012)
    for s in (-1, 1):
        mv._skirt(a, s, 1.46, -2.3, 2.35, .52, .98, 3, thick=.07, bolts=False)
        k.block(steel, (.14, .16, .12), loc=(s * .6, -2.6, .6), chamfer=0)                           # tow hooks
        _lights(a, (s * 1.18,), -2.2, 1.12, size=(.16, .04, .1))
        _lights(a, (s * 1.2,), 2.59, 1.2, facing=1, size=(.12, .04, .08), lamp='Alloy')
    k.block(armor, (1.5, .08, 1.0), loc=(0, 2.59, 1.1), chamfer=.02)                                  # rear ramp
    _hatch(a, .8, -1.55, 1.62, .23, handle=False)                                                    # driver (left)
    mv._periscopes(a, [(.8 + dx, -1.84, 1.58, 0) for dx in (-.15, .15)])
    a.part('Deck', 'Undercarriage').grille(.8, .7, loc=(-.75, -1.45, 1.63), rot=(-R90, 0, 0), slats=4, depth=.05,
                                           thickness=.04)                                           # engine (right)
    _hatch(a, -.5, 1.9, 1.64, .3, handle=False)                                                      # cargo hatch
    k.greebles(armor, (0, 1.2, 1.64), (1, 0, 0), (0, 1, 0), (2.0, 2.0), 4, seed=2724, height=(.04, .08),
               chamfer=.01, avoid=(((.22, -.25, 1.64), .9), ((-.5, 1.9, 1.64), .45), ((-.75, -1.45, 1.64), .6)))
    a.pivot('Point_exhaust', (-1.3, -1.2, 1.7))
    a.pivot('Point_fire', (0, 1.3, 1.7))
    t = a.pivot('Turret', (.22, -.25, 1.64))
    steel.cyl(.78, .08, loc=(.22, -.25, 1.64), seg=16, bevel=0)                                      # ring
    turret = a.part('Turret_body', 'Team', t)
    _turret_loft(turret, [(-.55, -.9), (.55, -.9), (.8, -.55), (.8, .75), (-.8, .75), (-.8, -.55)], .5, .6, .9,
                 chamfer=.04)
    tarm = a.part('Turret_armor', 'Armor', t)
    k.block(tarm, (.5, .3, .36), loc=(0, -.98, .3), chamfer=.03, taper=(.85, .9))                    # mantlet
    k.block(tarm, (.3, .3, .24), loc=(-.5, .1, .7), chamfer=.03)                                      # sight
    a.part('Sight', 'Glass', t).box((.2, .03, .12), loc=(-.5, -.06, .7), bevel=0)
    _hatch(a, .35, .35, .6, .22, parent=t, seg=10, handle=False)
    for s in (-1, 1):
        parts.smoke_launcher(a, a.part('Smoke', 'Steel', t), .72, -.4, .45, s, count=2, gap=.08, r=.05, depth=.14)
    y0, length = -1.1, 1.43
    parts.barrel(a, 'Main_cannon', t, 0, y0, .3, length, .06, seg=8, sleeve=1.3, extractor=(.35, 1.45, .3),
                 brake_name='Muzzle_brake', brake='collar')
    a.pivot('Muzzle_main', (0, -2.63, .3), t)
    mv._coax(a, t, -.22, -.95, .36, length=.34, housing=.22)
    k.block(a.part('Launcher_arm', 'Armor', t), (.16, .5, .2), loc=(.85, .1, .38), chamfer=0)
    k.block(a.part('Launcher_box', 'Armor', t), (.44, 1.3, .4), loc=(1.02, -.15, .55), chamfer=.04)
    for dx in (-.1, .1):
        a.part('Tubes', 'Undercarriage', t).cyl(.075, .03, loc=(1.02 + dx, -.81, .55), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_missile', (1.02, -.86, .55), t)
    k.clean(a)


# ============================================================================= T-72 hull (BMPT)
def _t72_v2(a, length=5.6):
    """m2._t72_hull on the V2 kit: V2 running gear, extruded hulls, library hatch; returns the deck height."""
    half = length / 2
    parts.track_unit(a, 1.1, length - .2, .74, .3, 6, .46, sprocket_end=1, teeth=6, cleat_pitch=.3)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    k.extrude(armor, [(-half + .2, .38), (-half - .08, .64), (-half + .1, .84), (half - .1, .84), (half, .56),
                      (half - .15, .38)], 1.72, axis='X', chamfer=.04, corner=.03)
    k.extrude(hull, [(-half - .1, .8), (-half + .8, 1.26), (half - .05, 1.28), (half + .02, .8)], 2.24, axis='X',
              chamfer=.05, corner=.04)
    k.inset(hull, lambda c, n, f: n.z > .5 and n.y < -.2 and c.y < -half + .9, width=.07, depth=.012)
    for s in (-1, 1):
        k.block(armor, (.52, length - .3, .06), loc=(s * 1.14, 0, 1.18), chamfer=0)                   # fenders
        a.part('Skirts', 'Rubber').box((.05, length - .9, .36), loc=(s * 1.4, -.1, .98), bevel=0)
        k.block(armor, (.42, .9, .24), loc=(s * 1.14, half - .75, 1.33), chamfer=.03)                 # fender boxes
        _lights(a, (s * .85,), -half + .12, 1.05, size=(.14, .04, .1))
        _lights(a, (s * .9,), half + .02, 1.05, facing=1, size=(.12, .04, .08), lamp='Alloy')
    _hatch(a, 0, -half + 1.05, 1.24, .2, handle=False)
    mv._periscopes(a, [(dx, -half + .82, 1.2, 0) for dx in (-.14, .14)])
    a.part('Deck', 'Undercarriage').grille(1.4, .9, loc=(0, half - 1.0, 1.29), rot=(-R90, 0, 0), slats=5, depth=.05,
                                           thickness=.04)
    a.pivot('Point_exhaust', (1.2, half - .4, 1.0))
    a.pivot('Point_fire', (0, half - 1.0, 1.35))
    return 1.28


def bmpt(a):
    """BMPT (m2.bmpt) on the V2 kit: the V2 T-72 hull, a lofted wide turret, lathed 30 mm barrels, chamfered Ataka
    boxes; same nodes (Blade, Muzzle_agl_l/_r, Main_cannon/_2, Launch_tubes, Muzzle_missile and its .001)."""
    from mb_phase2 import _suffixed
    _suffixed(a)
    hd.mark(a, False)
    z = _t72_v2(a, 5.6)
    armor = a.part('Armor', 'Armor')
    b = a.pivot('Blade', (0, -2.95, .55))
    k.block(a.part('Blade_plate', 'Armor', b), (2.4, .12, .5), loc=(0, -.15, -.1), rot=(-.25, 0, 0), chamfer=.02)
    for s in (-1, 1):
        k.block(armor, (.4, .9, .34), loc=(s * 1.14, -2.35, 1.38), chamfer=.03)                       # AGL pods
        k.lathe(a.part('AGL', 'Steel'), [(.06, 0), (.06, .5), (.08, .52), (0, .52)], loc=(s * 1.14, -2.7, 1.4),
                rot=FORWARD, seg=8, worn=(1,))
    a.pivot('Muzzle_agl_l', (1.14, -3.24, 1.4))
    a.pivot('Muzzle_agl_r', (-1.14, -3.24, 1.4))
    t = a.pivot('Turret', (0, .3, z))
    a.part('Turret_steel', 'Steel', t).cyl(.95, .1, loc=(0, 0, .05), seg=16, bevel=0)
    turret = a.part('Turret_body', 'Team', t)
    _turret_loft(turret, [(-.6, -1.1), (.6, -1.1), (1.1, -.7), (1.15, .9), (.9, 1.2), (-.9, 1.2), (-1.15, .9),
                          (-1.1, -.7)], .5, .8, .92, chamfer=.04)
    k.inset(turret, lambda c, n, f: n.z > .75, width=.08, depth=.012)
    tarm = a.part('Turret_armor', 'Armor', t)
    k.block(tarm, (.4, .34, .3), loc=(0, -1.12, .66), chamfer=.03)                                   # sight
    a.part('Sight', 'Glass', t).box((.26, .03, .14), loc=(0, -1.3, .68), bevel=0)
    for s, suffix in ((1, ''), (-1, '_2')):
        x = s * 1.28
        k.block(tarm, (.34, 1.1, .4), loc=(x, -.35, .42), chamfer=.03)                              # gun housings
        gun = a.part(f'Main_cannon{suffix}', 'Steel', t)
        brake = a.part(f'Muzzle_brake{suffix}', 'Undercarriage', t)
        for dz in (-.07, .07):
            k.lathe(gun, [(.05, 0), (.05, .1), (.06, .14), (.05, .2), (.05, 1.2), (.04, 1.3), (0, 1.3)],
                    loc=(x, -.85, .42 + dz), rot=FORWARD, seg=6, worn=(2,))
            k.ring(brake, [(.035, 1.28), (.065, 1.28), (.065, 1.4), (.035, 1.4)], loc=(x, -.85, .42 + dz),
                   rot=FORWARD, seg=6, worn=(1,))
        k.block(a.part('ATGM_box', 'Team', t), (.36, 1.5, .36), loc=(x, -.2, .86), chamfer=.04)
        k.block(a.part('ATGM_bands', 'Armor', t), (.4, .12, .4), loc=(x, .3, .86), chamfer=0)
        for dx in (-.08, .08):
            a.part('Launch_tubes', 'Undercarriage', t).cyl(.07, .03, loc=(x + dx, -.96, .86), rot=FORWARD, seg=6,
                                                           bevel=0)
        a.pivot('Muzzle_missile' if s > 0 else 'Muzzle_missile__001', (x, -1.0, .86), t)
    a.pivot('Muzzle_main', (1.28, -2.3, .42), t)
    mv._coax(a, t, .3, -1.1, .38, length=.3, housing=.2)
    _hatch(a, -.5, .5, .55, .22, parent=t, seg=10, handle=False)
    k.greebles(tarm, (0, .55, .5), (1, 0, 0), (0, 1, 0), (1.3, .6), 1, seed=2725, height=(.04, .09), chamfer=.01,
               avoid=(((-.5, .5, .5), .35),))
    k.clean(a)


# ============================================================================= engineer vehicle (BREM-1)
def engineer_vehicle(a):
    """Engineer and recovery vehicle (m2.engineer_vehicle) on the V2 kit: V2 running gear, extruded hulls, chamfered
    blade, crane and platform, a lathed cupola; same nodes (Blade, Turret, Main_cannon, Muzzle_main)."""
    hd.mark(a, False)
    parts.track_unit(a, 1.1, 5.7, .76, .3, 6, .46, sprocket_end=1, teeth=6, cleat_pitch=.3)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    k.extrude(armor, [(-2.7, .38), (-2.95, .64), (-2.75, .84), (2.8, .84), (2.92, .56), (2.75, .38)], 1.72, axis='X',
              chamfer=.04, corner=.03)
    k.extrude(hull, [(-3.0, .8), (-2.2, 1.2), (2.85, 1.24), (2.95, .8)], 2.8, axis='X', chamfer=.05, corner=.04)
    k.inset(hull, lambda c, n, f: n.z > .5 and n.y < -.2 and c.y < -2.2, width=.07, depth=.012)
    for s in (-1, 1):
        k.block(armor, (.5, 5.6, .06), loc=(s * 1.15, 0, 1.2), chamfer=0)                              # fenders
        _lights(a, (s * 1.0,), -2.65, 1.1, size=(.14, .04, .1))
        _lights(a, (s * 1.05,), 2.96, 1.05, facing=1, size=(.12, .04, .08), lamp='Alloy')
        steel.limb((s * 1.1, -2.8, .72), (s * 1.3, -3.2, .5), .12, .12, bevel=0)                      # blade arms
    b = a.pivot('Blade', (0, -3.1, .55))
    k.block(a.part('Blade_plate', 'Armor', b), (3.0, .14, .8), loc=(0, -.2, -.05), rot=(-.2, 0, 0), chamfer=.04)
    k.block(a.part('Blade_edge', 'Steel', b), (3.0, .12, .1), loc=(0, -.28, -.46), chamfer=0)
    a.part('Blade_stripe', 'Hazard', b).box((3.02, .02, .1), loc=(0, -.29, .2), rot=(-.2, 0, 0), bevel=0)
    k.lathe(a.part('Crane', 'Armor'), [(.36, -.25), (.36, .22), (.3, .27), (0, .27)], loc=(.8, -1.6, 1.48), seg=12,
            worn=(1,))
    boom = a.part('Boom_inner', 'Armor')
    boom.limb((.8, -1.6, 1.75), (-.85, 2.7, 1.6), .3, .3, bevel=.03, seg=1)
    k.block(boom, (.34, .4, .34), loc=(.8, -1.6, 1.8), chamfer=.03)
    a.part('Boom_stripes', 'Hazard').limb((.2, -.05, 1.9), (-.5, 1.75, 1.84), .32, .04, bevel=0)
    k.block(steel, (.2, .2, .26), loc=(-.85, 2.7, 1.36), chamfer=0)                                    # hook block
    k.block(steel, (.3, .3, .4), loc=(-.85, 2.7, 1.44), chamfer=.02)                                   # boom rest
    k.block(armor, (1.3, 1.5, .1), loc=(.55, 2.1, 1.3), chamfer=0)                                     # platform
    k.block(armor, (1.3, .08, .3), loc=(.55, 1.35, 1.44), chamfer=0)                                   # rail
    k.block(a.part('Track_links', 'Undercarriage'), (.9, .5, .12), loc=(.55, 2.2, 1.41), chamfer=.02)
    steel.box((.1, 1.8, .1), loc=(-1.3, .5, 1.3), bevel=0)                                             # tow bar
    k.greebles(armor, (-.3, 1.1, 1.25), (1, 0, 0), (0, 1, 0), (1.4, 1.2), 1, seed=2726, height=(.04, .08),
               chamfer=.01)
    a.pivot('Point_exhaust', (-1.2, 2.9, 1.1))
    a.pivot('Point_fire', (0, 1.8, 1.3))
    t = a.pivot('Turret', (-.75, -1.3, 1.24))
    k.lathe(a.part('Cupola', 'Team', t), [(.42, -.02), (.42, .22), (.36, .3), (0, .3)], seg=14, worn=(1,))
    gun = a.part('Main_cannon', 'Steel', t)
    k.block(gun, (.14, .4, .16), loc=(0, -.1, .42), chamfer=.02)
    k.lathe(gun, [(.05, 0), (.05, .7), (.07, .72), (.07, .8), (0, .8)], loc=(0, -.35, .42), rot=FORWARD, seg=6,
            worn=(1,))
    k.ring(a.part('Muzzle_brake', 'Undercarriage', t), [(.04, .78), (.07, .78), (.07, .88), (.04, .88)],
           loc=(0, -.35, .42), rot=FORWARD, seg=6, worn=(1,))
    a.pivot('Muzzle_main', (0, -1.2, .42), t)
    k.clean(a)


# ============================================================================= armoured bulldozer (D9R)
def armored_bulldozer(a):
    """Armoured bulldozer (m2.armored_bulldozer) on the V2 kit: extruded track frames with V2 wheels and sprocket,
    chamfered frame, engine box, caged cab and ripper, the blade moldboard extruded; same nodes (Blade, Mount_mg)."""
    hd.mark(a, False)
    armor = a.part('Armor', 'Armor')
    hull = a.part('Hull', 'Team')
    steel = a.part('Steel', 'Steel')
    belt = a.part('Tracks', 'Undercarriage')
    circles = [(-2.0, .38, .38), (1.75, .36, .36), (1.1, 1.62, .5)]
    outline = mv._hull2d([(cy + rr * math.cos(i * TAU / 14), cz + rr * math.sin(i * TAU / 14))
                          for cy, cz, rr in circles for i in range(14)])
    for s in (-1, 1):
        x = s * 1.2
        k.extrude(belt, outline, .66, loc=(x, 0, -.02), axis='X', chamfer=.02)
        for (py, pz), (ty, tz) in mv._perimeter(outline, .6, .05):
            k.block(belt, (.7, .1, .06), loc=(x, py + tz * .015, pz - .02 - ty * .015),
                    rot=(math.atan2(tz, ty), 0, 0), chamfer=0)
        parts.sprocket(a, (s * 1.5, 1.1, 1.6), .46, 9, .2, s)
        parts.road_wheel(a, (s * 1.5, -2.0, .38), .3, .16, s, seg=8)
        for y in (-1.2, -.3, .6):
            parts.road_wheel(a, (s * 1.5, y, .24), .22, .14, s, seg=6)
        k.block(hull, (.72, 3.4, .12), loc=(x, -.3, .92), chamfer=.02)                                # track guards
        steel.limb((s * 1.62, -.4, .5), (s * 1.62, -2.7, .55), .16, .2, bevel=0)
    k.block(armor, (1.7, 4.4, .8), loc=(0, -.1, .75), chamfer=.04)                                     # main frame
    k.block(hull, (1.9, 2.3, 1.05), loc=(0, -1.4, 1.62), chamfer=.06, taper=(.9, .95))                 # engine box
    a.part('Deck', 'Undercarriage').grille(1.2, .4, loc=(0, -2.56, 1.55), slats=4, depth=.05, thickness=.05)
    k.block(hull, (2.2, 1.9, .5), loc=(0, .9, 1.4), chamfer=.04)                                        # cab deck
    cab = a.part('Cab', 'Team')
    k.block(cab, (1.9, 1.6, 1.35), loc=(0, .9, 2.32), chamfer=.07, taper=(.92, .92))
    glass = a.part('Glass', 'Glass')
    for s in (-1, 1):
        glass.box((.03, 1.1, .6), loc=(s * .96, .9, 2.4), bevel=0)
    glass.box((1.4, .03, .6), loc=(0, .08, 2.4), bevel=0)
    cage = a.part('Cage', 'Steel')
    for xx in (-.4, 0, .4):
        cage.box((.1, .1, .7), loc=(xx, .02, 2.4), bevel=0)                                           # front bars
    for y in (.5, 1.3):
        for s in (-1, 1):
            cage.box((.1, .1, .7), loc=(s * 1.0, y, 2.4), bevel=0)
    k.block(armor, (2.0, 1.7, .12), loc=(0, .9, 3.05), chamfer=.03)                                    # cab roof
    k.block(steel, (1.4, .3, .3), loc=(0, 2.35, 1.1), chamfer=.03)                                     # ripper beam
    k.block(steel, (.3, .3, 1.1), loc=(0, 2.55, .55), rot=(.35, 0, 0), chamfer=.03)
    _lights(a, (-.7, .7), -2.56, 2.0, size=(.16, .04, .1))
    a.pivot('Point_exhaust', (.5, -1.2, 2.3))
    k.lathe(steel, [(.1, 0), (.1, .5), (.13, .52), (0, .52)], loc=(.5, -1.2, 2.05), seg=8, worn=(1,))   # stack
    a.pivot('Point_fire', (0, -1.4, 2.2))
    b = a.pivot('Blade', (0, -2.7, .55))
    board = a.part('Blade_moldboard', 'Team', b)
    prof = [(-.55, -.5), (-.42, -.2), (-.3, .2), (-.3, .6), (-.46, .95), (-.3, .98), (-.12, .6), (-.12, .2), (-.25, -.2),
            (-.36, -.5)]
    k.extrude(board, prof, 3.7, axis='X', chamfer=.03)
    k.block(a.part('Blade_edge', 'Steel', b), (3.7, .16, .12), loc=(0, -.48, -.5), chamfer=0)
    k.block(a.part('Blade_back', 'Armor', b), (3.2, .12, 1.0), loc=(0, -.05, .25), chamfer=.02)
    for s in (-1, 1):
        a.part('Blade_rams', 'Armor', b).limb((s * .8, 0, .3), (s * .8, 1.4, 1.1), .16, .16, bevel=0)
        a.part('Blade_pins', 'Steel', b).cyl(.1, .3, loc=(s * 1.62, 0, 0), rot=ACROSS, seg=8, bevel=0)
    m = a.pivot('Mount_mg', (0, .8, 3.11))
    k.block(a.part('RWS_body_mg', 'Armor', m), (.44, .5, .32), loc=(0, .05, .2), chamfer=.04)
    k.lathe(a.part('RWS_steel_mg', 'Steel', m), [(.05, 0), (.05, .7), (.07, .72), (.07, .8), (0, .8)],
            loc=(0, -.2, .22), rot=FORWARD, seg=6, worn=(1,))
    a.pivot('Muzzle_mg', (0, -.95, .22), m)
    k.clean(a)


# ============================================================================= pass 3c: air defence, artillery, support
def _truck_v2(a, front, rear, axles, r=.45, tw=.34, width=1.96, cab=1.55, roof=2.0, mg=None):
    """The forward-control military truck of m2._truck on the V2 kit (extruded cab, V2 wheels, chamfered plates); same
    parts, same geometry. Returns the bed's floor height."""
    hd.mark(a, False)
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    top = 2 * r + .06
    wx = width / 2 - tw / 2 - .01
    dark.box((1.0, rear - front - .4, .28), loc=(0, (front + rear) / 2 + .15, r + .22), bevel=0)
    for s in (-1, 1):
        for y in axles:
            parts.road_wheel(a, (s * wx, y, r), r, tw, s, seg=8)
    groups = [[axles[0]]]
    for y in axles[1:]:
        if y - groups[-1][-1] < 2 * r + .4:
            groups[-1].append(y)
        else:
            groups.append([y])
    for s in (-1, 1):
        for g in groups:
            k.block(armor, (tw + .1, g[-1] - g[0] + 2 * r + .2, .07), loc=(s * wx, (g[0] + g[-1]) / 2, top + .02),
                    chamfer=.02)
        a.part('Tanks', 'Armor').cyl(.2, .9, loc=(s * (wx - .06), (axles[0] + axles[1]) / 2 + .15, r + .15),
                                     rot=FORWARD, seg=8, bevel=0)
        a.part('Glass', 'Glass').box((.03, cab * .42, .38), loc=(s * (width / 2 + .005), front + cab * .45, roof - .3),
                                     bevel=0)
        steel.box((.18, .4, .06), loc=(s * (width / 2 - .08), front + cab * .5, top - .16), bevel=0)
    k.extrude(body, [(front + .04, top), (front, top + .45), (front + .12, roof - .02), (front + cab - .05, roof),
                     (front + cab, top)], width, axis='X', chamfer=.05, corner=.04)
    k.block(body, (1.1, cab * .7, top - r * .9), loc=(0, front + cab * .38, r * .9 + (top - r * .9) / 2 - .02),
            chamfer=.03)
    dark.grille(.9, .3, loc=(0, front - .02, top - .2), slats=4, depth=.05, thickness=.05)
    glass = a.part('Glass', 'Glass')
    for s in (-1, 1):
        glass.box((width / 2 - .14, .04, .44), loc=(s * (width / 4 + .02), front + .08, roof - .3), rot=(-.18, 0, 0),
                  bevel=0)
    k.block(steel, (width + .04, .16, .22), loc=(0, front - .06, r + .18), chamfer=.03)
    armor.box((width - .3, .1, .08), loc=(0, front + .12, roof - .02), rot=(-.2, 0, 0), bevel=0)
    _lights(a, (-(width / 2 - .25), width / 2 - .25), front - .02, top - .12)
    _lights(a, (-(width / 2 - .15), width / 2 - .15), rear + .02, top - .05, facing=1, size=(.16, .04, .1), lamp='Alloy')
    if mg is not None:
        mv._roof_mg(a, None, (mg[0], mg[1], roof), length=.75)
    a.pivot('Point_exhaust', (width / 2 - .2, front + cab + .1, roof + .1))
    steel.cyl(.07, .9, loc=(width / 2 - .2, front + cab + .1, roof - .35), seg=8, bevel=0)
    return top + .14


def aa_vehicle(a, detail=False):
    """Self-propelled AA gun (Gepard, m2.aa_vehicle) on the V2 kit: V2 running gear, extruded hull and turret, a 35 mm
    barrel on each side as one revolved surface, the dishes, the missile box; same nodes and pivots."""
    hd.mark(a, detail)
    parts.track_unit(a, 1.24, 5.6, .72, .28, 7, .44, sprocket_end=1, cleat_pitch=.44, teeth=6, wheel_seg=7)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    k.extrude(armor, [(-2.55, .36), (-2.85, .62), (-2.7, .82), (2.75, .82), (2.85, .55), (2.7, .36)], 1.86, axis='X',
              chamfer=.04, corner=.03)
    k.extrude(hull, [(-2.95, .78), (-2.2, 1.3), (2.8, 1.32), (2.88, .78)], 2.94, axis='X', chamfer=.06, corner=.04)
    for s in (-1, 1):
        mv._skirt(a, s, 1.48, -2.7, 2.6, .5, .96, 3, thick=.07, bolts=False)
        _lights(a, (s * 1.15,), -2.55, 1.1, size=(.16, .04, .1))
        _lights(a, (s * 1.2,), 2.9, 1.08, facing=1, size=(.12, .04, .08), lamp='Alloy')
        k.block(armor, (.4, .9, .26), loc=(s * 1.2, 2.2, 1.44), chamfer=.03)
    a.part('Deck', 'Undercarriage').grille(1.4, 1.0, loc=(0, 1.9, 1.33), rot=(-R90, 0, 0), slats=5, depth=.05,
                                           thickness=.04)
    _hatch(a, .7, -2.35, 1.12, .22, handle=False)
    a.pivot('Point_exhaust', (1.0, 2.9, 1.1))
    a.pivot('Point_fire', (0, 1.9, 1.4))
    t = a.pivot('Turret', (0, -.1, 1.32))
    steel.cyl(1.0, .08, loc=(0, -.1, 1.32), seg=14, bevel=0)
    k.extrude(a.part('Turret_body', 'Team', t), [(-1.0, -1.05), (1.0, -1.05), (1.0, 1.25), (-1.0, 1.25)], .8,
              loc=(0, 0, .4), axis='Z', chamfer=.05, corner=.04, taper=.94)
    tarm = a.part('Turret_armor', 'Armor', t)
    for s, suffix in ((-1, ''), (1, '_2')):
        x = s * 1.22
        k.block(tarm, (.42, 1.5, .55), loc=(x, -.25, .5), chamfer=.04)
        parts.barrel(a, f'Main_cannon{suffix}', t, x, -.95, .55, 2.35, .07, seg=12 if detail else 8, sleeve=1.2,
                     extractor=(.3, 1.3, .5), brake_name=f'Muzzle_brake{suffix}', brake='collar')
    a.pivot('Muzzle_main', (-1.22, -3.42, .55), t)
    mv._dish(a.part('Tracking_radar', 'Armor', t), (0, -1.08, .5), .42, .42, depth=.14, seg=12, tilt=.1)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tsteel.cyl(.1, .12, loc=(0, 1.0, .84), seg=8, bevel=0)
    r = a.pivot('Radar', (0, 1.0, .88), t)
    a.part('Radar_mast', 'Steel', r).box((.14, .14, .16), loc=(0, 0, .08), bevel=0)
    mv._dish(a.part('Radar_dish', 'Armor', r), (0, .05, .33), .62, .32, depth=.16, seg=12, tilt=.15)
    k.block(a.part('Launcher_box', 'Armor', t), (.4, 1.0, .3), loc=(.72, .7, .96), chamfer=.03)
    for dx in (-.09, .09):
        a.part('Launch_tubes', 'Undercarriage', t).cyl(.07, .03, loc=(.72 + dx, .19, .96), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_missile', (.72, .14, .96), t)
    _hatch(a, -.55, .5, .8, .24, parent=t, seg=10, handle=False)
    if detail:
        det = a.part('Turret_bolts', 'Steel', t)
        for s in (-1, 1):
            hd.bolt_line(det, (s * 1.44, -.9, .7), (s * 1.44, .4, .7), 6, rot=hd.side_rot(s), r=.014, h=.02)
            hd.bolt_line(a.part('Hull_bolts', 'Steel'), (s * 1.48, -2.3, 1.1), (s * 1.48, 2.3, 1.1), 10,
                         rot=hd.side_rot(s), r=.014, h=.02)
        mv._eyes(a, [(s * .9, -.8, .8, 0) for s in (-1, 1)], parent=t)
    k.clean(a)


def artillery(a, detail=False):
    """Self-propelled howitzer (M109A7, m2.artillery) on the V2 kit: V2 running gear, extruded hull, a chamfered
    turret, the 155 mm barrel as one revolved surface with a baffle brake, the travel lock; same nodes and pivots."""
    hd.mark(a, detail)
    parts.track_unit(a, 1.3, 4.9, .8, .28, 7, .42, sprocket_end=-1, cleat_pitch=.3)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    k.extrude(armor, [(-2.2, .38), (-2.46, .66), (-2.3, .9), (2.4, .9), (2.46, .5), (2.3, .38)], 2.08, axis='X',
              chamfer=.04, corner=.03)
    k.extrude(hull, [(-2.47, .84), (-1.72, 1.24), (2.44, 1.26), (2.48, .84)], 3.02, axis='X', chamfer=.06, corner=.04)
    k.inset(hull, lambda c, n, f: n.y > .8, width=.05, depth=.01)
    for s in (-1, 1):
        _lights(a, (s * 1.2,), -2.2, 1.02, size=(.16, .04, .1))
        _lights(a, (s * 1.25,), 2.49, 1.05, facing=1, size=(.12, .04, .08), lamp='Alloy')
        steel.box((.14, .16, .12), loc=(s * .6, -2.5, .62), bevel=0)
        k.block(armor, (.1, .9, .3), loc=(s * 1.46, -1.25, 1.12), chamfer=.02)
    _hatch(a, .75, -1.62, 1.24, .24, handle=False)
    mv._periscopes(a, [(.75 + dx, -1.93, 1.2, 0) for dx in (-.16, .16)])
    deck = a.part('Deck', 'Undercarriage')
    deck.grille(.9, .7, loc=(-.72, -1.6, 1.22), rot=(-.5, 0, 0), slats=4, depth=.06, thickness=.05)
    k.block(armor, (1.1, .06, .95), loc=(0, 2.49, .78), chamfer=.02)
    lock = a.part('Travel_lock', 'Steel')
    for s in (-1, 1):
        lock.limb((s * .42, -2.28, .98), (s * .12, -1.62, 1.33), .1, .1, bevel=0)
    k.block(lock, (.4, .16, .14), loc=(0, -1.6, 1.36), chamfer=.02)
    a.pivot('Point_exhaust', (-1.0, -1.9, 1.3))
    a.pivot('Point_fire', (0, -1.2, 1.3))
    t = a.pivot('Turret', (0, .95, 1.26))
    steel.cyl(1.1, .08, loc=(0, .95, 1.26), seg=16, bevel=0)
    tbody = a.part('Turret_body', 'Team', t)
    k.extrude(tbody, [(-1.24, -1.25), (1.24, -1.25), (1.36, -1.05), (1.36, 1.35), (-1.36, 1.35), (-1.36, -1.05)], 1.1,
              loc=(0, 0, .6), axis='Z', chamfer=.05, corner=.04, taper=.97)
    k.inset(tbody, lambda c, n, f: n.z > .8, width=.08, depth=.012)
    tarm = a.part('Turret_armor', 'Armor', t)
    k.block(tarm, (.9, .34, .7), loc=(0, -1.33, .55), chamfer=.04, taper=(.9, .9))
    for s in (-1, 1):
        k.block(tarm, (.06, .8, .75), loc=(s * 1.37, .1, .55), chamfer=.02)
        k.block(tarm, (.3, .9, .4), loc=(s * 1.42, .8, .7), chamfer=.03)
    k.block(tarm, (2.2, .36, .3), loc=(0, 1.52, .5), chamfer=.03)
    a.part('Tarp', 'Canvas', t).cyl(.16, 1.8, loc=(0, 1.52, .78), rot=ACROSS, seg=8, bevel=0)
    _hatch(a, .6, .45, 1.15, .26, parent=t, seg=10, handle=False)
    k.lathe(a.part('Cupola', 'Armor', t), [(.36, 0), (.36, .2), (.3, .24)], loc=(-.75, -.45, 1.1), seg=12, worn=(1,))
    k.block(tarm, (.4, .3, .26), loc=(.2, -.98, 1.24), chamfer=.03)
    a.part('Sight', 'Glass', t).box((.3, .03, .14), loc=(.2, -1.14, 1.25), bevel=0)
    parts.mg_mount(a, t, (-.75, -.45, 1.3), length=.8, shield=False)
    k.greebles(tarm, (0, .4, 1.15), (1, 0, 0), (0, 1, 0), (1.6, 1.4), 4, seed=2732, height=(.05, .1), chamfer=.012)
    y0, length, z = -1.5, 4.3, .55
    parts.barrel(a, 'Main_cannon', t, 0, y0, z, length, .115, seg=14 if detail else 10, sleeve=1.1,
                 extractor=(.62, 1.46, .7), brake_name='Muzzle_brake', brake='baffle')
    k.block(a.part('Main_cannon_cradle', 'Armor', t), (.44, .9, .4), loc=(0, -1.2, .52), chamfer=.03)
    a.pivot('Muzzle_main', (0, y0 - length - .4, z), t)
    if detail:
        det = a.part('Turret_bolts', 'Steel', t)
        for dx in (-.3, .3):
            for dz in (-.22, .22):
                hd.bolt(det, (dx, -1.51, .55 + dz), hd.FRONT, r=.02, h=.026)
        hd.bolt_ring(det, hd.frame((-.75, -.45, 1.31)), .3, 8, r=.014, h=.02)
        for s in (-1, 1):
            hd.bolt_line(det, (s * 1.41, -.25, .85), (s * 1.41, .45, .85), 5, rot=hd.side_rot(s), r=.014, h=.02)
        mv._periscopes(a, [(-.75 + .3 * math.cos(u), -.45 + .3 * math.sin(u), 1.22, u + R90)
                           for u in (-2.4, -1.6, -.8)], parent=t)
        mv._vent(a, .1, 1.0, 1.16, parent=t)
        mv._eyes(a, [(s * 1.2, -1.05, 1.16, 0) for s in (-1, 1)], parent=t)
        mv._glacis_bolts(a, (-2.47, .84), (-1.72, 1.24), .5, -1.4, 1.4, 12)
    k.clean(a)


def heavy_aa(a):
    """Gun-missile air defence (Pantsir-S1, m2.heavy_aa) on the V2 kit: the V2 truck, an extruded combat module with
    twin 30 mm barrels a side as revolved surfaces, chamfered missile packs, the radars; every node as before."""
    from mb_phase2 import _suffixed
    _suffixed(a)
    z = _truck_v2(a, -4.8, 4.8, (-3.95, -2.75, 1.5, 2.7), r=.5, width=2.1, cab=1.6, roof=2.15)
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    k.block(body, (2.06, 1.9, .92), loc=(0, -2.1, z + .46), chamfer=.05)
    k.inset(body, lambda c, n, f: abs(n.x) > .9, width=.12, depth=.012)
    a.part('Glass', 'Glass').box((.03, .5, .28), loc=(1.04, -2.3, z + .6), bevel=0)
    k.block(armor, (2.1, 5.8, .16), loc=(0, 1.9, z + .02), chamfer=.03)
    for s in (-1, 1):
        steel.box((.14, .14, .6), loc=(s * .95, 4.3, z - .45), bevel=0)
    a.pivot('Point_fire', (0, -2.1, z + 1.0))
    t = a.pivot('Turret', (0, 1.6, z + .1))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(.8, .1, loc=(0, 0, .05), seg=14, bevel=0)
    k.extrude(a.part('Turret_body', 'Team', t), [(-.62, -1.0), (.62, -1.0), (.72, -.75), (.72, 1.0), (-.72, 1.0),
                                                 (-.72, -.75)], .7, loc=(0, 0, .45), axis='Z', chamfer=.05,
              corner=.03, taper=.94)
    k.block(tarm, (.4, .28, .3), loc=(0, -1.06, .6), chamfer=.03)
    a.part('Sight', 'Glass', t).box((.26, .03, .16), loc=(0, -1.21, .62), bevel=0)
    for s, suffix in ((-1, ''), (1, '_2')):
        x = s * .86
        k.block(tarm, (.3, 1.2, .36), loc=(x, -.3, .36), chamfer=.04)
        for dx in (-.07, .07):
            parts.barrel(a, f'Main_cannon{suffix}', t, x + dx, -.9, .36, 1.9, .045, seg=8, sleeve=1.2,
                         extractor=(.4, 1.3, .4), brake_name=f'Muzzle_brake{suffix}', brake='collar')
    a.pivot('Muzzle_main', (-.86, -2.96, .36), t)
    for s in (-1, 1):
        for xc in (.6, 1.1):
            x = s * xc
            k.block(a.part('Pack_box', 'Team', t), (.44, 2.3, .22), loc=(x, -.2, .92), chamfer=.03)
            frame = a.part('Pack_frame', 'Armor', t)
            for y in (-1.1, .7):
                frame.box((.48, .14, .26), loc=(x, y, .92), bevel=0)
            for dx in (-.14, 0, .14):
                a.part('Pack_tubes', 'Undercarriage', t).cyl(.055, .04, loc=(x + dx, -1.36, .92), rot=FORWARD, seg=8,
                                                             bevel=0)
            a.part('Missile_pack', 'Undercarriage', t).cyl(.05, 2.32, loc=(x, -.24, .92), rot=FORWARD, seg=6, bevel=0)
            tsteel.box((.12, .3, .3), loc=(x - s * .2, .2, .72), bevel=0)
            a.pivot('Muzzle_missile' + ('' if x == -1.1 else '__%03d' % (1 + [-.6, .6, 1.1].index(x))),
                    (x, -1.43, .92), t)
    r = a.pivot('Radar', (0, -.3, .8), t)
    a.part('Radar_mast', 'Steel', r).cyl(.08, .16, loc=(0, 0, .08), seg=8, bevel=0)
    mv._dish(a.part('Radar_dish', 'Armor', r), (0, .05, .42), .32, .32, depth=.12, seg=12, tilt=.15)
    rs = a.pivot('Radar_search', (0, .75, .8), t)
    a.part('Search_mount', 'Steel', rs).box((.2, .2, .2), loc=(0, 0, .1), bevel=0)
    k.block(a.part('Search_panel', 'Armor', rs), (1.2, .14, .45), loc=(0, .05, .4), rot=(.2, 0, 0), chamfer=.03)
    a.part('Search_array', 'MetalSheet', rs).box((1.08, .03, .38), loc=(0, .13, .41), rot=(.2, 0, 0), bevel=0)
    k.greebles(tarm, (0, .2, .72), (1, 0, 0), (0, 1, 0), (.5, .8), 2, seed=2733, height=(.04, .08), chamfer=.012)
    k.clean(a)


def _m113_v2(a, cupola=True):
    """The M113 hull of the smoke and mortar carriers (m2._m113) on the V2 kit; returns the roof height."""
    hd.mark(a, False)
    parts.track_unit(a, .88, 3.7, .62, .25, 5, .36, sprocket_end=-1, cleat_pitch=.5, teeth=6, wheel_seg=6)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    roof = 1.72
    k.extrude(armor, [(-1.7, .36), (-1.9, .6), (-1.8, .74), (1.85, .74), (1.95, .5), (1.8, .36)], 1.36, axis='X',
              chamfer=.03, corner=.03)
    k.extrude(hull, [(-1.96, .66), (-1.98, 1.02), (-1.4, roof - .02), (1.9, roof), (1.96, .66)], 2.16, axis='X',
              chamfer=.05, corner=.04)
    k.inset(hull, lambda c, n, f: abs(n.x) > .9 and c.z < 1.4, width=.1, depth=.012)
    armor.box((1.9, .5, .05), loc=(0, -1.96, 1.1), rot=(.5, 0, 0), bevel=0)
    k.block(armor, (1.3, .06, 1.0), loc=(0, 1.97, .95), chamfer=.02)
    for s in (-1, 1):
        _lights(a, (s * .75,), -1.99, 1.0, size=(.14, .04, .1))
        _lights(a, (s * .85,), 1.97, 1.4, facing=1, size=(.12, .04, .08), lamp='Alloy')
    _hatch(a, .6, -1.15, roof, .2, handle=False)
    a.part('Deck', 'Undercarriage').grille(.6, .5, loc=(-.55, -1.05, roof + .005), rot=(-R90, 0, 0), slats=3,
                                           depth=.04, thickness=.04)
    a.pivot('Point_exhaust', (-.95, -1.3, roof - .2))
    if cupola:
        t = a.pivot('Turret', (-.1, -.55, roof))
        k.lathe(a.part('Cupola', 'Armor', t), [(.34, 0), (.34, .2), (.3, .24)], seg=10, worn=(1,))
        k.block(a.part('Gun_shield', 'Armor', t), (.6, .06, .34), loc=(0, -.36, .42), chamfer=0)
        k.block(a.part('Main_cannon', 'Steel', t), (.14, .4, .14), loc=(0, -.1, .38), chamfer=.02)
        parts.barrel(a, 'Main_cannon', t, 0, -.28, .38, .7, .05, seg=8, sleeve=1.3, extractor=(.5, 1.3, .2),
                     brake_name='Muzzle_brake', brake='collar')
        a.pivot('Muzzle_main', (0, -1.14, .38), t)
    return roof


def smoke_carrier(a):
    """Smoke generator carrier (M1059, m2.smoke_carrier) on the V2 kit: the V2 M113, a revolved generator drum with
    bands and a stack, the fuel drum, four-tube launchers; same nodes."""
    roof = _m113_v2(a)
    k.lathe(a.part('Generator', 'MetalSheet'), [(.31, -.85), (.36, -.8), (.36, .8), (.31, .85)],
            loc=(0, 1.2, roof + .38), rot=ACROSS, seg=12, worn=(1, 2))
    for x in (.5, -.5):
        k.ring(a.part('Generator_bands', 'Armor'), [(.36, -.04), (.395, -.04), (.395, .04), (.36, .04)],
               loc=(x, 1.2, roof + .38), rot=ACROSS, seg=12)
    k.block(a.part('Steel', 'Steel'), (.6, .5, .2), loc=(0, 1.2, roof + .06), chamfer=.02)
    k.lathe(a.part('Exhaust', 'Undercarriage'), [(.12, -.25), (.12, .22), (.09, .25), (0, .25)],
            loc=(.7, 1.75, roof + .6), rot=(-.6, 0, 0), seg=8, worn=(2,))
    k.lathe(a.part('Fuel', 'BarrelRed'), [(.18, -.25), (.2, -.22), (.2, .22), (.18, .25)],
            loc=(-.72, 1.72, roof + .25), seg=10, worn=(1, 2))
    for s in (-1, 1):
        k.block(a.part('Smoke_brackets', 'Armor'), (.16, .46, .05), loc=(s * .95, -1.2, roof - .2), chamfer=0)
        for i in range(4):
            k.lathe(a.part('Smoke', 'Steel'), [(.05, -.09), (.055, .09), (.036, .09), (0, .05)],
                    loc=(s * .95, -1.35 + i * .1, roof - .12), rot=(.6, 0, s * .5), seg=6, worn=(1,))
    a.pivot('Point_fire', (0, 1.2, roof + .8))
    k.clean(a)


def mortar_carrier(a):
    """Mortar carrier (M1064, m2.mortar_carrier) on the V2 kit: the V2 M113 without the cupola, the open roof hatch with
    chamfered lids, the 120 mm tube as a revolved surface on its turntable; same nodes."""
    roof = _m113_v2(a, cupola=False)
    a.part('Hatch_well', 'Undercarriage').box((1.5, 1.6, .04), loc=(0, .85, roof + .002), bevel=0)
    for s in (-1, 1):
        k.block(a.part('Hatch_lids', 'Team'), (.06, 1.5, .72), loc=(s * 1.12, .85, roof + .02), chamfer=.01)
        k.block(a.part('Armor', 'Armor'), (.08, 1.6, .1), loc=(s * .8, .85, roof + .05), chamfer=0)
    parts.mg_mount(a, None, (.55, -.9, roof), length=.75, shield=True)
    a.pivot('Point_fire', (0, .85, roof))
    t = a.pivot('Turret', (0, .85, .85))
    a.part('Turret_steel', 'Steel', t).cyl(.5, .1, loc=(0, 0, .05), seg=12, bevel=0)
    k.block(a.part('Turret_armor', 'Armor', t), (.5, .5, .3), loc=(0, .1, .25), chamfer=.03)
    ang = math.radians(65)
    axis = Vector((0, -math.cos(ang), math.sin(ang)))
    base = Vector((0, .15, .35))
    length = 2.1
    rot = (R90 - ang, 0, 0)
    k.lathe(a.part('Mortar_tube', 'Steel', t), [(.13, 0), (.13, length), (.09, length), (.09, length - .12),
                                                 (0, length - .12)], loc=tuple(base), rot=rot, seg=10, worn=(1,))
    k.ring(a.part('Mortar_tube_ring', 'Armor', t), [(.14, length - .1), (.18, length - .1), (.18, length), (.14, length)],
           loc=tuple(base), rot=rot, seg=10)
    a.part('Sight', 'Glass', t).box((.1, .14, .1), loc=(.2, -.3, 1.0), bevel=0)
    a.part('Turret_armor', 'Armor', t).limb((0, .1, .4), tuple(base + axis * .9), .08, .08, bevel=0)
    a.pivot('Muzzle_main', tuple(base + axis * (length + .05)), t)
    k.clean(a)


def mine_layer(a):
    """Tracked minelayer (GMZ-3, m2.mine_layer) on the V2 kit: V2 running gear, extruded hull, chamfered mine cassettes
    in a grid, the inclined chute with mines, the machine-gun cupola with a revolved barrel; same nodes."""
    hd.mark(a, False)
    parts.track_unit(a, 1.07, 5.9, .7, .27, 7, .44, sprocket_end=-1, cleat_pitch=.56, teeth=6, wheel_seg=7)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    k.extrude(armor, [(-2.8, .36), (-3.05, .6), (-2.9, .8), (2.85, .8), (2.95, .55), (2.8, .36)], 1.66, axis='X',
              chamfer=.04, corner=.03)
    k.extrude(hull, [(-3.05, .76), (-2.35, 1.32), (2.9, 1.34), (2.98, .76)], 2.58, axis='X', chamfer=.06, corner=.04)
    for s in (-1, 1):
        _lights(a, (s * 1.0,), -2.95, 1.0, size=(.14, .04, .1))
        armor.box((.5, 5.8, .06), loc=(s * 1.07, 0, 1.18), bevel=0)
    _hatch(a, .75, -2.1, 1.32, .22, handle=False)
    racks = a.part('Mine_racks', 'Armor')
    boxes = a.part('Mines', 'Crate')
    for i in range(3):
        for j in range(4):
            x, y = -.72 + i * .72, -.95 + j * .78
            k.block(boxes, (.62, .68, .34), loc=(x, y, 1.52), chamfer=0)
            a.part('Mine_fuzes', 'Hazard').box((.5, .08, .02), loc=(x, y - .2, 1.7), bevel=0)
    racks.box((2.3, 3.3, .1), loc=(0, .22, 1.37), bevel=0)
    ang = math.radians(40)
    chute = a.part('Chute', 'Steel')
    top = Vector((0, 2.9, 1.3))
    down = Vector((0, math.cos(ang), -math.sin(ang)))
    length = 1.35 / math.sin(ang)
    chute.box((.7, length, .08), loc=tuple(top + down * (length / 2)), rot=(-ang, 0, 0), bevel=0)
    for s in (-1, 1):
        chute.box((.06, length, .26), loc=tuple(top + down * (length / 2) + Vector((s * .36, 0, .1))), rot=(-ang, 0, 0),
                  bevel=0)
        steel.limb((s * .5, 2.7, 1.2), tuple(top + down * (length * .6) + Vector((s * .4, 0, 0))), .1, .1, bevel=0)
    for kk in (.35, .55, .75):
        a.part('Chute_mines', 'Crate').cyl(.2, .1, loc=tuple(top + down * (length * kk) + Vector((0, 0, .1))),
                                           rot=(-ang, 0, 0), seg=10, bevel=0)
    a.pivot('Point_exhaust', (-.9, -2.2, 1.35))
    a.pivot('Point_fire', (0, .2, 1.7))
    t = a.pivot('Turret', (-.6, -1.9, 1.34))
    k.lathe(a.part('Turret_body', 'Team', t), [(.36, 0), (.36, .24), (.3, .3)], seg=10, worn=(1,))
    k.block(a.part('Main_cannon', 'Steel', t), (.14, .36, .14), loc=(0, -.05, .48), chamfer=.02)
    parts.barrel(a, 'Main_cannon', t, 0, -.2, .48, .66, .05, seg=8, sleeve=1.3, extractor=(.5, 1.3, .2),
                 brake_name='Muzzle_brake', brake='collar')
    a.part('Turret_mount', 'Steel', t).box((.1, .1, .2), loc=(0, 0, .36), bevel=0)
    a.pivot('Muzzle_main', (0, -1.0, .48), t)
    k.clean(a)


def shield_carrier(a):
    """Shield projector (Boxer 8x8 with the field emitter, m2.shield_carrier) on the V2 kit: V2 wheels, an extruded
    hull with chamfers and insets, the revolved emitter drum, ring and core, the remote machine gun; same nodes."""
    hd.mark(a, False)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    a.part('Chassis', 'Undercarriage').box((1.5, 5.0, .3), loc=(0, 0, .5), bevel=0)
    for s in (-1, 1):
        for y in (-2.2, -1.1, .9, 2.0):
            parts.road_wheel(a, (s * .95, y, .45), .45, .34, s, seg=8)
    k.extrude(hull, [(-2.8, .55), (-3.15, .95), (-2.3, 1.72), (2.95, 1.74), (3.12, .6)], 2.36, axis='X', chamfer=.06,
              corner=.05)
    k.inset(hull, lambda c, n, f: abs(n.x) > .9 and c.z > .9, width=.12, depth=.012)
    k.inset(hull, lambda c, n, f: n.y > .8, width=.05, depth=.01)
    for s in (-1, 1):
        k.block(armor, (.08, 5.2, .5), loc=(s * 1.19, .05, 1.2), chamfer=.02)
        _lights(a, (s * .8,), -2.95, 1.1, size=(.14, .04, .1))
        _lights(a, (s * .9,), 3.13, 1.2, facing=1, size=(.12, .04, .08), lamp='Alloy')
    k.block(armor, (1.3, .06, 1.0), loc=(0, 3.13, 1.1), chamfer=.02)
    _hatch(a, .6, -2.05, 1.72, .2, handle=False)
    a.pivot('Point_exhaust', (-.9, -1.6, 1.8))
    a.pivot('Point_fire', (0, 1.8, 1.8))
    k.lathe(a.part('Emitter_base', 'Armor'), [(.95, -.15), (.95, .12), (.88, .15)], loc=(0, .5, 1.87), seg=16,
            worn=(1,))
    e = a.pivot('Emitter', (0, .5, 2.02))
    k.ring(a.part('Emitter_ring', 'TeamGlow', e), [(.9, -.05), (.98, -.09), (1.06, -.05), (1.06, .09), (.98, .13),
                                                    (.9, .09)], loc=(0, 0, .02), seg=20)
    a.part('Emitter_dish', 'MetalSheet', e).sphere((.9, .9, .42), loc=(0, 0, 0), seg=16, rings=6, cut=0)
    k.lathe(a.part('Emitter_core', 'Steel', e), [(.16, 0), (.16, .26), (.1, .3), (0, .3)], loc=(0, 0, .35), seg=10,
            worn=(2,))
    a.part('Emitter_glow', 'TeamGlow', e).sphere(.14, loc=(0, 0, .7), seg=8, rings=5)
    for kk in range(4):
        u = kk * R90 + math.pi / 4
        a.part('Emitter_prongs', 'Armor', e).limb((math.cos(u) * .55, math.sin(u) * .55, .25),
                                                  (math.cos(u) * .2, math.sin(u) * .2, .6), .08, .08, bevel=0)
    t = a.pivot('Turret', (-.55, -1.5, 1.74))
    k.lathe(a.part('RWS_ring', 'Armor', t), [(.3, 0), (.3, .1), (.26, .12)], seg=10, worn=(1,))
    k.block(a.part('RWS_body', 'Armor', t), (.4, .5, .3), loc=(0, .05, .3), chamfer=.03)
    parts.barrel(a, 'Main_cannon', t, 0, -.2, .32, .62, .05, seg=8, sleeve=1.3, extractor=(.5, 1.3, .2),
                 brake_name='Muzzle_brake', brake='collar')
    a.pivot('Muzzle_main', (0, -1.0, .32), t)
    k.clean(a)


# ============================================================================= pass 3d: rocket, missile and beam vehicles
def mlrs(a):
    """M142 HIMARS on the V2 truck: extruded cab, V2 wheels, the six-round pod as a chamfered block in its frame on the
    turntable, rim-ringed tubes; every node as before (`Turret`, `Pod`, `Tubes`, `Tubes_bore`, `Muzzle_main`, MG)."""
    z = _truck_v2(a, -2.8, 2.8, (-2.05, .95, 2.05), r=.42, width=1.92, cab=1.55, roof=2.0, mg=(.4, -2.1))
    k.block(a.part('Bed', 'Armor'), (1.9, 4.0, .14), loc=(0, .75, z - .05), chamfer=.03)
    for s in (-1, 1):
        a.part('Steel', 'Steel').box((.14, .14, .5), loc=(s * .85, 2.5, z - .4), bevel=0)             # jacks
    a.pivot('Point_fire', (0, 1.0, z + .9))
    t = a.pivot('Turret', (0, 1.55, z + .02))
    a.part('Turret_steel', 'Steel', t).cyl(.55, .12, loc=(0, 0, .06), seg=12, bevel=0)
    k.block(a.part('Turret_armor', 'Armor', t), (1.4, .7, .3), loc=(0, .6, .25), chamfer=.04)
    L, W, H = 3.7, 1.24, .82
    pitch = .14
    rot = (-pitch, 0, 0)
    fm = mv._frame((0, 1.5, .64), rot)
    along = Vector((0, -math.cos(pitch), math.sin(pitch)))
    c = fm @ Vector((0, -L / 2, 0))
    pod = a.part('Pod', 'Team', t)
    k.block(pod, (W, L, H), loc=tuple(c), rot=rot, chamfer=.06)
    k.inset(pod, lambda cc, n, f: abs(n.x) > .9, width=.12, depth=.012)
    frame = a.part('Pod_frame', 'Armor', t)
    for y in (-1.5, 0, 1.5):
        k.block(frame, (W + .08, .14, H + .08), loc=tuple(fm @ Vector((0, -L / 2 + y, 0))), rot=rot, chamfer=.02)
    tubes = a.part('Tubes', 'Undercarriage', t)
    bores = a.part('Tubes_bore', 'Crate', t)
    rr = (R90 - pitch, 0, 0)
    for i in range(3):
        for j in range(2):
            p = fm @ Vector((-.38 + i * .38, -L, -.18 + j * .36))
            k.ring(tubes, [(.11, -.01), (.15, -.01), (.15, .03), (.11, .03)], loc=tuple(p), rot=rr, seg=8)
            k.lathe(bores, [(.11, 0), (.11, .02)], loc=tuple(p + along * .02), rot=rr, seg=8)
    v = Vector((0, math.cos(pitch), -math.sin(pitch)))
    k.greebles(pod, tuple(fm @ Vector((0, -L / 2 - .2, H / 2))), (1, 0, 0), tuple(v), (.9, 2.4), 3, seed=2741,
               height=(.04, .08), chamfer=.012)
    a.pivot('Muzzle_main', tuple(fm @ Vector((0, -L - .09, 0))), t)
    k.clean(a)


def _maz543_v2(a, front, rear, axles, r=.55):
    """m2._maz543 on the V2 kit (V2 wheels, extruded cabs, chamfered boxes). Returns (Body, Armor, Steel)."""
    hd.mark(a, False)
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    dark.box((1.1, rear - front - .32, .34), loc=(0, (front + rear) / 2 + .34, .78), bevel=0)
    for s in (-1, 1):
        for y in axles:
            parts.road_wheel(a, (s * .94, y, r), r, .42, s, seg=8)
        for pair in (axles[:2], axles[2:]):
            k.block(armor, (.52, 3.0, .08), loc=(s * .94, (pair[0] + pair[1]) / 2, 1.16), chamfer=.02)
        k.extrude(body, [(front + .05, 1.1), (front, 1.6), (front + .3, 2.35), (front + 1.6, 2.4), (front + 1.7, 1.1)],
                  .9, loc=(s * .75, 0, 0), axis='X', chamfer=.05, corner=.04)
        a.part('Glass', 'Glass').box((.7, .04, .42), loc=(s * .75, front + .16, 2.0), rot=(-.38, 0, 0), bevel=0)
        a.part('Glass', 'Glass').box((.03, .7, .36), loc=(s * 1.205, front + 1.0, 2.0), bevel=0)
        steel.box((.14, .14, .7), loc=(s * 1.0, rear - .22, .75), bevel=0)
        steel.box((.34, .34, .05), loc=(s * 1.0, rear - .22, .03), bevel=0)
        a.part('Tanks', 'Armor').cyl(.22, 1.1, loc=(s * .8, (axles[1] + axles[2]) / 2, .72), rot=FORWARD, seg=8,
                                     bevel=0)
    k.block(body, (.56, 1.5, .9), loc=(0, front + .8, 1.55), chamfer=.04, taper=(.9, .9))
    dark.grille(.44, .4, loc=(0, front + .04, 1.4), slats=3, depth=.05, thickness=.04)
    k.block(steel, (2.3, .16, .24), loc=(0, front - .04, .8), chamfer=.03)
    _lights(a, (-.9, .9), front - .02, 1.2)
    _lights(a, (-1.05, 1.05), rear, 1.0, facing=1, size=(.14, .04, .1), lamp='Alloy')
    a.pivot('Point_exhaust', (0, front + 1.3, 2.05))
    return body, armor, steel


def long_sam(a):
    """S-400 5P85 TEL on the V2 MAZ-543: the erector with four 6 m canisters as revolved tubes, bumped rims and covers;
    every node as before (`Turret`, `Launcher_*`, `Muzzle_missile`, `Muzzle_main`)."""
    body, armor, steel = _maz543_v2(a, -5.6, 5.12, (-4.3, -2.75, .75, 2.3))
    k.block(body, (2.3, 1.4, .75), loc=(0, -3.0, 1.4), chamfer=.05)
    k.block(armor, (2.36, 7.6, .14), loc=(0, 1.3, 1.25), chamfer=.03)
    for y in (-1.7, 3.7):
        k.block(armor, (2.0, .3, .5), loc=(0, y, 1.55), chamfer=.03)
    a.pivot('Point_fire', (0, -3.0, 1.8))
    t = a.pivot('Turret', (0, 4.0, 1.48))
    frame = a.part('Launcher_frame', 'Armor', t)
    k.block(frame, (2.4, .5, .5), loc=(0, .45, .76), chamfer=.04)
    for y in (-5.4, -3.2, -1.0):
        k.block(frame, (2.46, .22, .66), loc=(0, y, .78), chamfer=.02)
    for s in (-1, 1):
        steel.box((.2, .5, .6), loc=(s * 1.05, 4.2, 1.55), bevel=0)
    tubes = a.part('Launcher_tubes', 'Team', t)
    ends = a.part('Launcher_ends', 'Armor', t)
    covers = a.part('Launcher_covers', 'Undercarriage', t)
    z, front, length = .78, -6.9, 6.0
    for x in (-.87, -.29, .29, .87):
        k.lathe(tubes, [(.27, 0), (.27, length)], loc=(x, front + length, z), rot=FORWARD, seg=10)
        for y0 in (front + .14, front + length):
            k.ring(ends, [(.265, 0), (.3, .07), (.265, .14)], loc=(x, y0, z), rot=FORWARD, seg=10)
        k.lathe(covers, [(.25, 0), (.25, .03)], loc=(x, front + .005, z), rot=FORWARD, seg=10)
    k.greebles(body, (0, -3.0, 1.78), (1, 0, 0), (0, 1, 0), (1.8, 1.0), 3, seed=2742, height=(.04, .09),
               chamfer=.012)
    a.pivot('Muzzle_missile', (0, front - .05, z), t)
    a.pivot('Muzzle_main', (0, front - .05, z), t)
    k.clean(a)


def heavy_rocket_artillery(a):
    """BM-30 Smerch on the V2 MAZ-543: equipment box, bed, the pack of 12 revolved 300 mm tubes in chamfered frames;
    every node as before."""
    front = -4.85
    body, armor, steel = _maz543_v2(a, front, 4.85, (-3.55, -2.0, 1.5, 3.05), r=.5)
    k.block(body, (2.3, 1.3, .75), loc=(0, front + 2.45, 1.4), chamfer=.05)
    k.block(armor, (2.3, 6.3, .14), loc=(0, 1.5, 1.25), chamfer=.03)
    mv._roof_mg(a, None, (-.75, front + 1.2, 2.4), length=.7, shield=False)
    a.pivot('Point_fire', (0, front + 2.45, 1.8))
    t = a.pivot('Turret', (0, 3.4, 1.32))
    a.part('Turret_steel', 'Steel', t).cyl(.7, .14, loc=(0, 0, .07), seg=12, bevel=0)
    k.block(a.part('Turret_armor', 'Armor', t), (1.6, .8, .3), loc=(0, .1, .3), chamfer=.04)
    L = 6.0
    c = Vector((0, .3 - L / 2, 1.0))
    frame = a.part('Pack_frame', 'Armor', t)
    for y in (-5.3, -3.0, -.8):
        k.block(frame, (1.86, .18, 1.44), loc=(0, y + .3, c.z), chamfer=.03)
    tubes = a.part('Tubes', 'Team', t)
    bores = a.part('Tube_bores', 'Undercarriage', t)
    for i in range(4):
        for j in range(3):
            p = Vector((-.63 + i * .42, 0, c.z - .42 + j * .42))
            k.lathe(tubes, [(.2, 0), (.2, L)], loc=(p.x, c.y + L / 2, p.z), rot=FORWARD, seg=8)
            k.ring(tubes, [(.19, 0), (.215, .05), (.19, .1)], loc=(p.x, c.y - L / 2 + .1, p.z), rot=FORWARD, seg=8)
            k.lathe(bores, [(.15, 0), (.15, .03)], loc=(p.x, c.y - L / 2 + .005, p.z), rot=FORWARD, seg=8)
    k.block(a.part('Cable_box', 'Armor', t), (.5, .4, .4), loc=(.6, .5, .6), chamfer=.04)
    k.greebles(body, (0, front + 2.45, 1.78), (1, 0, 0), (0, 1, 0), (1.8, 1.0), 3, seed=2743, height=(.04, .09),
               chamfer=.012)
    a.pivot('Muzzle_main', (0, c.y - L / 2 - .08, c.z), t)
    k.clean(a)


def ballistic_launcher(a):
    """Iskander-M on the V2 truck: chamfered compartments and deck, the erector with the missile as revolved parts
    (body, ogive nose, tail, hazard band), grid fins and the split casing, drawn 20 degrees up as before."""
    z = _truck_v2(a, -5.25, 5.25, (-4.2, -2.75, 1.2, 2.65), r=.5, width=2.45, cab=2.1, roof=2.2, mg=(-.5, -4.3))
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    k.block(body, (2.4, 1.2, 1.0), loc=(0, -2.5, z + .5), chamfer=.05)
    k.inset(body, lambda c, n, f: abs(n.x) > .9 and c.y > -3.0, width=.12, depth=.012)
    k.block(armor, (2.4, 7.3, .14), loc=(0, 1.55, z + .02), chamfer=.03)
    for s in (-1, 1):
        k.block(armor, (.3, 6.0, .4), loc=(s * 1.05, 1.4, z - .3), chamfer=.02)
        a.part('Steel', 'Steel').box((.14, .14, .6), loc=(s * 1.05, 4.9, z - .45), bevel=0)
    a.pivot('Point_fire', (0, -2.5, z + 1.1))
    t = a.pivot('Turret', (0, 4.7, z + .25))
    pitch = math.radians(20)
    rot = (-pitch, 0, 0)
    rr = (R90 - pitch, 0, 0)
    fm = mv._frame((0, 0, .1), rot)
    L, R = 5.9, .38

    def at(y, zz=.2 + R):
        return tuple(fm @ Vector((0, y, zz)))
    k.block(a.part('Erector', 'Armor', t), (1.2, L - .3, .2), loc=tuple(fm @ Vector((0, -L / 2, 0))), rot=rot,
            chamfer=.03)
    for s in (-1, 1):
        k.block(a.part('Erector_arms', 'Armor', t), (.14, L * .8, .5),
                loc=tuple(fm @ Vector((s * .6, -L * .42, .25))), rot=rot, chamfer=.02)
    k.lathe(a.part('Missile_body', 'Fuel', t), [(R, 0), (R, L * .72)], loc=at(-L * .08), rot=rr, seg=12)
    k.lathe(a.part('Missile_nose', 'Crate', t), [(R, 0), (R * .88, L * .05), (R * .55, L * .12), (0, L * .2)],
            loc=at(-L * .8), rot=rr, seg=12, caps=(True, False))
    k.lathe(a.part('Missile_tail', 'Undercarriage', t), [(R * .9, 0), (R * .9, .2), (R * .7, .3)], loc=at(.05),
            rot=rr, seg=12)
    k.ring(a.part('Missile_band', 'Hazard', t), [(R - .02, 0), (R + .01, 0), (R + .01, .12), (R - .02, .12)],
           loc=at(-L * .6 + .06), rot=rr, seg=12)
    fins = a.part('Missile_grid_fins', 'Armor', t)
    for n in range(4):
        u = math.pi / 4 + n * R90
        fins.box((.05, .5, .34),
                 loc=tuple(fm @ Vector((math.sin(u) * (R + .15), -.55, .2 + R + math.cos(u) * (R + .15)))),
                 rot=(-pitch, u, 0), bevel=0)
    for s in (-1, 1):
        k.block(a.part('Missile_casing', 'Team', t), (.12, L * .92, .62),
                loc=tuple(fm @ Vector((s * (R + .12), -L * .48, .2 + R * .8))), rot=rot, chamfer=.02)
    a.pivot('Muzzle_main', tuple(fm @ Vector((0, -L - .05, .2 + R))), t)
    k.clean(a)


def thermobaric_launcher(a):
    """TOS-1A on the V2 T-72 hull: the 24-tube launcher box as a chamfered block with chamfered armour bands and
    revolved tube rims and faces; every node as before."""
    hd.mark(a, False)
    z = _t72_v2(a, 5.9)
    mv._roof_mg(a, None, (-1.05, 2.65, z), length=.7, shield=False)
    t = a.pivot('Turret', (0, .5, z))
    a.part('Turret_steel', 'Steel', t).cyl(.9, .12, loc=(0, 0, .06), seg=14, bevel=0)
    k.block(a.part('Turret_armor', 'Armor', t), (1.4, 1.2, .3), loc=(0, .5, .26), chamfer=.04)
    L, W, H = 4.0, 2.3, 1.0
    c = Vector((0, -.55, .4 + H / 2 + .02))
    launcher = a.part('Launcher', 'Team', t)
    k.block(launcher, (W, L, H), loc=tuple(c), chamfer=.07)
    k.inset(launcher, lambda cc, n, f: n.z > .9, width=.14, depth=.012)
    arm = a.part('Launcher_armor', 'Armor', t)
    for y in (-1.6, 0, 1.6):
        k.block(arm, (W + .1, .16, H + .1), loc=tuple(c + Vector((0, y, 0))), chamfer=.03)
    face = a.part('Launcher_face', 'Undercarriage', t)
    tubes = a.part('Tubes', 'Steel', t)
    for i in range(6):
        for j in range(4):
            p = c + Vector((-.9 + i * .36, -L / 2, -.36 + j * .24))
            k.lathe(tubes, [(.12, 0), (.12, .06)], loc=(p.x, p.y + .01, p.z), rot=FORWARD, seg=6)
            k.lathe(face, [(.09, 0), (.09, .03)], loc=(p.x, p.y - .035, p.z), rot=FORWARD, seg=6)
    a.part('Sight', 'Glass', t).box((.2, .03, .12), loc=(.9, -.4, .5), bevel=0)
    k.greebles(launcher, tuple(c + Vector((0, .3, H / 2))), (1, 0, 0), (0, 1, 0), (1.6, 2.4), 3, seed=2744,
               height=(.04, .09), chamfer=.012)
    tip = c + Vector((0, -L / 2 - .1, 0))
    a.pivot('Muzzle_rocket', tuple(tip), t)
    a.pivot('Muzzle_main', tuple(tip), t)
    k.clean(a)


def _sam_round_v2(a, t, x, y_nose, z, length, r):
    """m2._sam_round with revolved body and nose and the wings and tail fins as crossed plates (same parts)."""
    B = length - r * 2.4
    k.lathe(a.part('Launcher_missiles', 'Fuel', t), [(r * .8, 0), (r, .1), (r, B)], loc=(x, y_nose + length, z),
            rot=FORWARD, seg=8)
    k.lathe(a.part('Launcher_face', 'Armor', t), [(r, 0), (r * .75, r), (r * .35, r * 1.9), (0, r * 2.4)],
            loc=(x, y_nose + r * 2.4, z), rot=FORWARD, seg=8, caps=(True, False))
    fins = a.part('Launcher_missiles_fins', 'MetalSheet', t)
    for (span, chord), yc in (((.2, 1.3), y_nose + length * .45), ((.26, .45), y_nose + length - .225 - .04)):
        for n in range(2):
            u = math.pi / 4 + n * R90
            fins.box((.04, chord, 2 * (r + span - .02)), loc=(x, yc, z), rot=(0, u, 0), bevel=0)


def sam_launcher(a):
    """Buk-M1 9A310 on the V2 tracked hull: extruded hull and armour, the Fire Dome drum and dome as revolved parts,
    four 4.44 m rounds as revolved bodies on chamfered rails; every node as before."""
    hd.mark(a, False)
    parts.track_unit(a, 1.07, 7.0, .72, .28, 6, .44, sprocket_end=1, teeth=6, cleat_pitch=.3)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    k.extrude(armor, [(-3.4, .36), (-3.6, .62), (-3.4, .8), (3.4, .8), (3.55, .6), (3.4, .36)], 1.66, axis='X',
              chamfer=.04, corner=.03)
    k.extrude(hull, [(-3.62, .74), (-3.0, 1.18), (3.45, 1.2), (3.55, .74)], 2.6, axis='X', chamfer=.05, corner=.04)
    k.inset(hull, lambda c, n, f: n.z > .5 and c.y < -3.0, width=.08, depth=.012)
    k.block(armor, (.9, 1.0, .4), loc=(.62, -2.65, 1.34), chamfer=.04, taper=(.9, .85))
    a.part('Glass', 'Glass').box((.6, .03, .18), loc=(.62, -3.16, 1.38), bevel=0)
    _lights(a, (-1.0, 1.0), -3.45, 1.0, size=(.16, .04, .1))
    _lights(a, (-1.1, 1.1), 3.56, 1.0, facing=1, size=(.14, .04, .1), lamp='Alloy')
    a.part('Deck', 'Undercarriage').grille(1.2, .8, loc=(-.55, 3.0, 1.19), rot=(-R90, 0, 0), slats=4, depth=.05,
                                           thickness=.05)
    mv._roof_mg(a, None, (.62, -2.65, 1.54), length=.75, shield=False)
    a.pivot('Point_exhaust', (-.9, 3.4, 1.1))
    a.pivot('Point_fire', (0, 3.0, 1.25))
    t = a.pivot('Turret', (0, .4, 1.2))
    steel.cyl(1.0, .08, loc=(0, .4, 1.2), seg=14, bevel=0)
    k.block(a.part('Turret_body', 'Team', t), (2.1, 2.6, .5), loc=(0, .1, .25), chamfer=.06, taper=(.95, .95))
    tarm = a.part('Turret_armor', 'Armor', t)
    k.lathe(tarm, [(.5, 0), (.55, .05), (.55, .55), (.5, .6)], loc=(0, -1.05, .5), seg=12)
    k.lathe(a.part('Radar_dome', 'Team', t), [(.58, 0), (.58, .03), (.42, .09), (0, .11)], loc=(0, -1.05, 1.09),
            seg=12)
    a.part('Radar_array', 'Undercarriage', t).box((.8, .06, .5), loc=(0, -1.6, .8), bevel=0)
    y_nose, zz, length = -2.35, 1.42, 4.44
    frame = a.part('Launcher_cradle', 'Armor', t)
    k.block(frame, (2.1, .5, .3), loc=(0, 1.55, 1.0), chamfer=.03)
    for s in (-1, 1):
        k.block(tarm, (.2, .6, .7), loc=(s * .95, 1.55, .72), chamfer=.03)
        frame.box((.14, 3.2, .16), loc=(s * .95, .2, 1.18), bevel=0)
    rails = a.part('Launcher_rails', 'Steel', t)
    for x in (-.9, -.3, .3, .9):
        rails.box((.12, 3.4, .1), loc=(x, .1, zz - .23), bevel=0)
        _sam_round_v2(a, t, x, y_nose, zz, length, .17)
    k.greebles(tarm, (0, 1.0, .5), (1, 0, 0), (0, 1, 0), (1.6, .8), 2, seed=2745, height=(.04, .08), chamfer=.012)
    a.pivot('Muzzle_main', (0, y_nose - .06, zz), t)
    k.clean(a)


def iron_beam(a):
    """Iron Beam on the V2 truck: chamfered container with inset roof panel, revolved fan shrouds, the beam director
    pod and glowing bezel as before, radar panel on its mast; every node as before."""
    z = _truck_v2(a, -4.0, 4.0, (-3.2, -2.05, 1.85, 2.95), r=.46)
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    box = a.part('Body', 'Team')
    k.block(box, (1.96, 6.2, .75), loc=(0, .85, z + .375), chamfer=.06)
    k.inset(box, lambda c, n, f: n.z > .9, width=.12, depth=.012)
    grilles = a.part('Fan_grilles', 'Undercarriage')
    for s in (-1, 1):
        for y in (-.9, .9, 2.7):
            grilles.grille(1.3, .45, loc=(s * .99, y, z + .38), rot=(0, 0, s * R90), slats=4, depth=.05,
                           thickness=.05)
    for y in (1.3, 2.5):
        k.ring(armor, [(.35, 0), (.42, 0), (.42, .1), (.35, .1)], loc=(0, y, z + .76), seg=12)
        grilles.cyl(.36, .03, loc=(0, y, z + .86), seg=12, bevel=0)
    a.part('Coolant_pipes', 'Steel').box((.12, 4.0, .12), loc=(.7, 1.3, z + .81), bevel=0)
    a.pivot('Point_fire', (0, 2.0, z + 1.0))
    t = a.pivot('Turret', (0, -1.25, z + .75))
    steel.cyl(.62, .1, loc=(0, -1.25, z + .77), seg=14, bevel=0)
    k.block(a.part('Turret_body', 'Team', t), (1.4, 1.5, .7), loc=(0, .05, .4), chamfer=.07, taper=(.9, .92))
    tarm = a.part('Turret_armor', 'Armor', t)
    for s in (-1, 1):
        k.block(tarm, (.14, .8, .6), loc=(s * .77, .05, .45), chamfer=.03)
    tilt = math.radians(30)
    axis = Vector((0, -math.cos(tilt), math.sin(tilt)))
    c = Vector((0, -.6, .45))
    rr = (R90 - tilt, 0, 0)
    k.lathe(a.part('Main_cannon_pod', 'Armor', t), [(.42, 0), (.46, .04), (.46, .46), (.42, .5)],
            loc=tuple(c - axis * .15), rot=rr, seg=14)
    a.part('Main_cannon_glow', 'TeamGlow', t).cyl(.43, .04, loc=tuple(c + axis * .36), rot=rr, seg=14, bevel=0)
    a.part('Main_cannon_window', 'Glass', t).cyl(.37, .05, loc=tuple(c + axis * .37), rot=rr, seg=14, bevel=0)
    k.block(a.part('Main_cannon_sensor', 'Steel', t), (.3, .3, .2), loc=(.5, .1, .85), chamfer=.03)
    a.part('Main_cannon_lens', 'Glass', t).box((.2, .03, .12), loc=(.5, -.06, .86), bevel=0)
    a.pivot('Muzzle_main', tuple(c + axis * .6), t)
    steel.box((.16, .16, .5), loc=(0, 3.5, z + 1.0), bevel=0)
    r = a.pivot('Radar', (0, 3.5, z + 1.25))
    k.block(a.part('Radar_panel', 'Armor', r), (1.2, .14, .5), loc=(0, 0, .25), rot=(-.25, 0, 0), chamfer=.03)
    a.part('Radar_face', 'Undercarriage', r).box((1.08, .03, .4), loc=(0, -.08, .25), rot=(-.25, 0, 0), bevel=0)
    k.greebles(box, (0, .85, z + .75), (1, 0, 0), (0, 1, 0), (1.5, 3.0), 3, seed=2746, height=(.04, .09),
               chamfer=.012)
    k.clean(a)


# ============================================================================= pass 3e: support, radar and special trucks
def _ybox(shape, size, loc, rot=(0, 0, 0), chamfer=.03):
    """A chamfered box whose depth runs along its local Y (rails, panels, bars): `size` = (x, y, z) as for a box."""
    sx, sy, sz = size
    c = 0.0 if min(size) < k.SMALL else min(chamfer, sx * .3, sy * .3, sz * .3)
    k.extrude(shape, [(-sx / 2, -sz / 2), (sx / 2, -sz / 2), (sx / 2, sz / 2), (-sx / 2, sz / 2)], sy, loc=loc, rot=rot,
              axis='Y', chamfer=c, corner=c)


def _ring_gun_v2(a, loc, length=.6, ring=.34, z=.31, y0=-.15):
    """m2._ring_gun on the V2 kit: a lathed ring, a chamfered gun body, a revolved barrel with a muzzle ring; same
    nodes (`Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`)."""
    t = a.pivot('Turret', loc)
    k.lathe(a.part('Ring', 'Armor', t), [(ring, 0), (ring, .08), (ring - .05, .1)], seg=12, worn=(1,))
    a.part('Mount', 'Steel', t).box((.1, .1, .18), loc=(0, .05, .16), bevel=0)
    gun = a.part('Main_cannon', 'Steel', t)
    k.block(gun, (.14, .4, .15), loc=(0, .05, z - .01), chamfer=.02)
    r = .06
    k.lathe(gun, [(r, 0), (r, .06), (r * .8, .1), (r * .8, length), (r * .5, length), (r * .5, length - .06),
                  (0, length - .06)], loc=(0, y0, z), rot=FORWARD, seg=8)
    k.ring(a.part('Muzzle_brake', 'Undercarriage', t), [(r * .55, length), (r * 1.25, length), (r * 1.25, length + .12),
                                                       (r * .55, length + .12)], loc=(0, y0, z), rot=FORWARD, seg=8)
    k.block(a.part('Ammo_box', 'Armor', t), (.16, .2, .16), loc=(.16, .08, .26), chamfer=.02)
    a.pivot('Muzzle_main', (0, y0 - length - .12, z), t)
    return t


# ----------------------------------------------------------------------------- HEMTT pair
def _hemtt_v2(a):
    """m2._hemtt on the V2 kit (V2 wheels, an extruded cab with chamfers and door insets, chamfered boxes, the lathed
    ring gun); same parts and geometry. Returns the load bed's floor height."""
    hd.mark(a, False)
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    dark.box((1.1, 7.9, .3), loc=(0, .05, .72), bevel=0)
    for s in (-1, 1):
        for y in m2.HEMTT_AXLES:
            parts.road_wheel(a, (s * .79, y, .48), .48, .36, s, seg=8)
    for s in (-1, 1):
        k.block(armor, (.44, 1.95, .08), loc=(s * .79, -2.54, 1.02), chamfer=.02)
        k.block(armor, (.44, 2.1, .08), loc=(s * .79, 1.8, 1.02), chamfer=.02)
        steel.box((.14, .5, .14), loc=(s * .88, -.5, .86), bevel=0)
        a.part('Tanks', 'Armor').cyl(.22, 1.0, loc=(s * .74, -.35, .72), rot=FORWARD, seg=8, bevel=0)
        a.part('Glass', 'Glass').box((.03, .7, .42), loc=(s * .985, -3.25, 1.72), bevel=0)
        steel.box((.2, .42, .06), loc=(s * .9, -3.6, .78), bevel=0)
    k.extrude(body, [(-4.06, 1.02), (-4.1, 1.45), (-3.98, 2.04), (-2.45, 2.06), (-2.4, 1.02)], 1.98, axis='X',
              chamfer=.05, corner=.04)
    k.inset(body, lambda c, n, f: abs(n.x) > .9, width=.12, depth=.012)
    k.block(body, (1.2, .9, .5), loc=(0, -3.62, .8), chamfer=.03)
    dark.grille(1.0, .34, loc=(0, -4.08, .82), slats=4, depth=.05, thickness=.05)
    dark.grille(1.3, .3, loc=(0, -4.1, 1.26), slats=3, depth=.05, thickness=.05)
    glass = a.part('Glass', 'Glass')
    for s in (-1, 1):
        glass.box((.84, .04, .48), loc=(s * .45, -4.03, 1.76), rot=(-.2, 0, 0), bevel=0)
    k.block(steel, (2.0, .16, .22), loc=(0, -4.16, .66), chamfer=.03)
    _lights(a, (-.72, .72), -4.1, .98)
    _lights(a, (-.8, .8), 4.08, 1.0, facing=1, size=(.16, .04, .1), lamp='Alloy')
    armor.box((1.6, .1, .08), loc=(0, -3.99, 2.04), rot=(-.2, 0, 0), bevel=0)
    k.block(armor, (1.5, .4, .95), loc=(0, -2.2, 1.45), chamfer=.04)
    steel.cyl(.08, 1.0, loc=(.62, -2.2, 1.9), seg=8, bevel=0)
    k.block(armor, (.3, .3, .5), loc=(-.62, -2.2, 2.05), chamfer=.03)
    _ring_gun_v2(a, (-.42, -3.3, 2.06))
    a.pivot('Point_exhaust', (.62, -2.2, 2.42))
    a.pivot('Point_fire', (0, -3.2, 2.1))
    return 1.12


def supply_truck(a):
    """Supply truck (M977 HEMTT cargo truck) on the V2 HEMTT: a chamfered bed with drop sides, the tarpaulin as an
    extruded rounded canvas cover on its bows, the crates showing at the open tail, the tailgate down; same nodes."""
    z = _hemtt_v2(a)
    armor = a.part('Armor', 'Armor')
    k.block(a.part('Bed', 'Team'), (1.98, 6.1, .14), loc=(0, 1.0, z + .07), chamfer=.02)
    for s in (-1, 1):
        k.block(armor, (.06, 6.1, .42), loc=(s * .97, 1.0, z + .35), chamfer=.01)
    k.block(armor, (1.98, .06, .42), loc=(0, -2.03, z + .35), chamfer=.01)
    prof = [(-.99, z + .5), (-.99, 1.86), (-.8, 2.02), (-.3, 2.08), (.3, 2.08), (.8, 2.02), (.99, 1.86), (.99, z + .5)]
    tarp = a.part('Tarp', 'Canvas')
    k.extrude(tarp, prof, 4.0, loc=(0, -.02, 0), axis='Y', chamfer=.05, corner=.04)
    straps = a.part('Straps', 'Undercarriage')
    for y in (-1.3, -.3, .7, 1.7):
        straps.box((2.02, .1, .06), loc=(0, y, 2.07), bevel=0)
    m2._crate_stack(a, -.86, .86, 2.1, 3.85, z + .14, 2, 3, 3)
    k.block(a.part('Ammo_boxes', 'Armor'), (.5, .34, .28), loc=(-.55, 2.35, z + .9), chamfer=.03)
    k.block(a.part('Fuel_cans', 'Hazard'), (.3, .5, .36), loc=(.62, 3.6, z + .79), chamfer=.04)
    k.block(armor, (1.9, .06, .42), loc=(0, 4.1, z - .2), chamfer=.01)
    k.clean(a)


def ammo_carrier(a):
    """Ammunition carrier (HEMTT with a load-handling bed) on the V2 HEMTT: chamfered bed and pedestal, the steel rack,
    the crate stack, the knuckle crane with a lathed column and chamfered boom, outriggers; same nodes."""
    z = _hemtt_v2(a)
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    k.block(a.part('Bed', 'Team'), (1.98, 5.4, .14), loc=(0, .65, z + .07), chamfer=.02)
    rack = a.part('Rack', 'Armor')
    for s in (-1, 1):
        for y in (-1.95, -.6, .75, 2.1, 3.3):
            rack.box((.1, .1, .82), loc=(s * .93, y, z + .55), bevel=0)
        for zz in (.5, .95):
            rack.box((.1, 5.35, .1), loc=(s * .93, .67, z + zz), bevel=0)
    rack.box((1.96, .1, .1), loc=(0, -1.95, z + .95), bevel=0)
    m2._crate_stack(a, -.84, .84, -1.85, 3.2, z + .14, 3, 3, 5)
    k.block(armor, (1.7, .6, .4), loc=(0, 3.72, z + .2), chamfer=.05)
    k.lathe(a.part('Crane', 'Hazard'), [(.24, -.35), (.24, .3), (.2, .35), (0, .35)], loc=(.45, 3.72, z + .75), seg=10,
            worn=(1,))
    boom = a.part('Crane_boom', 'Hazard')
    _ybox(boom, (.22, 2.8, .24), (.45, 2.3, z + 1.16), rot=(-.06, 0, 0), chamfer=.03)
    k.block(boom, (.2, .5, .3), loc=(.45, 3.62, z + 1.2), chamfer=.03)
    k.block(steel, (.16, .16, .2), loc=(.45, .95, z + 1.02), chamfer=.02)
    for s in (-1, 1):
        steel.box((.14, .2, .5), loc=(s * .92, 3.72, z - .1), bevel=0)
    k.clean(a)


# ----------------------------------------------------------------------------- radar, jammer
def counter_battery_radar(a):
    """Counter-battery radar (AN/TPQ-53 on an FMTV 6x6) on the V2 truck: chamfered shelter with side insets, cooling
    unit, generator, the phased-array panel as a chamfered slab on a chamfered yoke at 45 degrees on its turntable
    (`Radar`); the cab-roof machine gun; same nodes."""
    z = _truck_v2(a, -3.2, 3.2, (-2.4, 1.05, 2.15), mg=(-.45, -2.5))
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    k.block(a.part('Bed', 'Armor'), (1.96, 4.9, .12), loc=(0, .75, z - .06), chamfer=.02)
    k.block(body, (1.9, 1.7, 1.2), loc=(0, -.72, z + .6), chamfer=.06)
    k.inset(body, lambda c, n, f: abs(n.x) > .9 and c.y > -1.55 and c.z > z, width=.12, depth=.012)
    k.block(armor, (1.2, .8, .3), loc=(0, -.72, z + 1.35), chamfer=.04)
    a.part('Fan_grilles', 'Undercarriage').cyl(.28, .04, loc=(0, -.72, z + 1.51), seg=10, bevel=0)
    k.block(armor, (.6, .6, .5), loc=(-.6, .4, z + .25), chamfer=.04)
    a.part('Generator_panel', 'Undercarriage').box((.03, .44, .3), loc=(-.91, .4, z + .25), bevel=0)
    steel.cyl(.6, .12, loc=(0, 1.9, z + .06), seg=14, bevel=.02, bseg=1)
    for s in (-1, 1):
        steel.box((.14, .14, .6), loc=(s * .9, 3.0, z - .45), bevel=0)
        steel.box((.3, .3, .05), loc=(s * .9, 3.0, .03), bevel=0)
    r = a.pivot('Radar', (0, 1.9, z + .12))
    tilt = math.radians(45)
    up = Vector((0, -math.sin(tilt), math.cos(tilt)))
    back = Vector((0, math.cos(tilt), math.sin(tilt)))
    yoke = a.part('Radar_yoke', 'Armor', r)
    k.block(yoke, (1.0, .5, .3), loc=(0, 0, .15), chamfer=.04)
    for s in (-1, 1):
        yoke.limb((s * .5, 0, .2), tuple(Vector((s * .5, 0, 0)) + up * .8 + back * -.12), .12, .16, bevel=0)
    centre = Vector((0, 0, .2)) + up * .95
    _ybox(a.part('Radar_panel', 'Team', r), (2.3, .16, 1.9), tuple(centre), rot=(tilt, 0, 0), chamfer=.04)
    a.part('Radar_face', 'MetalSheet', r).box((2.14, .03, 1.74), loc=tuple(centre + back * .09), rot=(tilt, 0, 0),
                                              bevel=0)
    seams = a.part('Radar_seams', 'Undercarriage', r)
    for kk in (-.55, 0, .55):
        seams.box((2.16, .03, .05), loc=tuple(centre + back * .11 + up * kk), rot=(tilt, 0, 0), bevel=0)
    _ybox(a.part('Radar_iff', 'Armor', r), (1.4, .14, .16), tuple(centre + up * 1.0), rot=(tilt, 0, 0), chamfer=.02)
    a.pivot('Point_fire', (0, -.7, z + 1.3))
    k.clean(a)


def ew_jammer(a):
    """Electronic-warfare jammer (Krasukha-4 on a BAZ-6910 8x8) on the V2 truck: chamfered equipment body with
    insets, the round dish on its turntable (`Radar`), the lathed remote gun (`Turret`, `Main_cannon`); same nodes."""
    z = _truck_v2(a, -4.4, 4.4, (-3.55, -2.35, 1.95, 3.15), r=.48, width=2.3, cab=1.7, roof=2.2)
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    k.block(body, (2.3, 5.2, .9), loc=(0, .15, z + .45), chamfer=.06)
    for y in (-1.6, -.2, 1.2):
        a.part('Doors', 'Armor').box((.04, .8, .7), loc=(1.16, y, z + .42), bevel=0)
    k.block(armor, (1.2, .8, .3), loc=(0, -1.6, z + 1.05), chamfer=.04)
    steel.cyl(.7, .2, loc=(0, 2.9, z + 1.0), seg=14, bevel=0)
    for s in (-1, 1):
        steel.box((.14, .14, .6), loc=(s * 1.05, 3.9, z - .45), bevel=0)
    a.pivot('Point_fire', (0, -.5, z + 1.0))
    r = a.pivot('Radar', (0, 2.9, z + 1.1))
    k.block(a.part('Radar_mast', 'Steel', r), (.5, .5, .3), loc=(0, 0, .15), chamfer=.04)
    tilt = math.radians(58)
    dish_c = Vector((0, .15, .55))
    mv._dish(a.part('Radar_dish', 'MetalSheet', r), tuple(dish_c), 1.38, 1.38, depth=.35, seg=16, tilt=tilt)
    a.part('Radar_feed', 'Armor', r).limb(tuple(dish_c), tuple(dish_c + Vector((0, -math.cos(tilt), math.sin(tilt)))
                                                              * .9), .12, .12, bevel=0)
    k.greebles(body, (0, -.6, z + .9), (1, 0, 0), (0, 1, 0), (1.6, 1.4), 3, seed=2752, height=(.04, .08),
               chamfer=.012)
    t = a.pivot('Turret', (-.5, -3.3, 2.2))
    k.lathe(a.part('RWS_ring', 'Armor', t), [(.3, 0), (.3, .08), (.26, .1)], seg=10, worn=(1,))
    gun = a.part('Main_cannon', 'Steel', t)
    k.block(gun, (.14, .36, .16), loc=(0, .05, .24), chamfer=.02)
    k.lathe(gun, [(.05, 0), (.05, .08), (.04, .12), (.04, .6), (.025, .6), (.025, .52), (0, .52)], loc=(0, -.13, .24),
            rot=FORWARD, seg=6)
    k.ring(a.part('Muzzle_brake', 'Undercarriage', t), [(.04, .6), (.075, .6), (.075, .7), (.04, .7)],
           loc=(0, -.13, .24), rot=FORWARD, seg=6)
    a.pivot('Muzzle_main', (0, -.84, .24), t)
    k.clean(a)


# ----------------------------------------------------------------------------- railgun truck, Shahed launcher
def railgun_truck(a):
    """Railgun truck (8x8) on the V2 truck: chamfered capacitor module with glowing radiator panels, the turret with a
    chamfered body and breech, the two long guide rails as chamfered bars, capacitor coils, muzzle frame and rams;
    same nodes."""
    z = _truck_v2(a, -4.85, 4.85, (-3.95, -2.65, 1.75, 3.05), r=.5, width=2.4, cab=1.7, roof=2.2)
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    k.block(body, (2.36, 3.0, 1.0), loc=(0, -1.35, z + .5), chamfer=.06)
    glow = a.part('Radiator_glow', 'Energy')
    for s in (-1, 1):
        for y in (-2.3, -1.35, -.4):
            a.part('Radiators', 'Undercarriage').box((.04, .8, .7), loc=(s * 1.19, y, z + .5), bevel=0)
            glow.box((.03, .7, .08), loc=(s * 1.215, y, z + .5), bevel=0)
    k.block(armor, (2.36, 3.7, .14), loc=(0, 2.95, z + .02), chamfer=.02)
    k.greebles(body, (0, -1.35, z + 1.0), (1, 0, 0), (0, 1, 0), (1.8, 2.4), 3, seed=2753, height=(.04, .09),
               chamfer=.012)
    a.pivot('Point_fire', (0, -1.35, z + 1.1))
    t = a.pivot('Turret', (0, 2.95, z + .1))
    a.part('Turret_steel', 'Steel', t).cyl(.9, .12, loc=(0, 0, .06), seg=14, bevel=0)
    k.block(a.part('Turret_body', 'Team', t), (1.8, 2.0, .9), loc=(0, .3, .57), chamfer=.06, taper=(.9, .92))
    k.block(a.part('Turret_armor', 'Armor', t), (1.2, .6, .7), loc=(0, -.85, .95), chamfer=.05)
    k.block(a.part('Main_cannon_breech', 'Steel', t), (1.0, .8, .6), loc=(0, -.9, 1.3), chamfer=.05)
    y0, L, zc = -1.3, 6.3, 1.35
    rails = a.part('Main_cannon_rails', 'MetalSheet', t)
    for x in (-.3, .3):
        _ybox(rails, (.22, L, .32), (x, y0 - L / 2, zc), chamfer=.03)
    bands = a.part('Main_cannon_bands', 'Armor', t)
    coil = a.part('Main_cannon_glow', 'Energy', t)
    for kk in range(5):
        y = y0 - .6 - kk * 1.1
        _ybox(bands, (.9, .18, .4), (0, y, zc), chamfer=.03)
        coil.box((.92, .05, .42), loc=(0, y - .12, zc), bevel=0)
    _ybox(a.part('Muzzle_brake', 'Armor', t), (.9, .3, .44), (0, y0 - L - .1, zc), chamfer=.04)
    a.pivot('Muzzle_main', (0, y0 - L - .3, zc), t)
    a.part('Rams', 'Armor', t).box((.2, .2, .7), loc=(0, -.4, .75), rot=(.5, 0, 0), bevel=0)
    a.part('Ram_rods', 'Steel', t).box((.12, .12, .6), loc=(0, -.62, 1.05), rot=(.5, 0, 0), bevel=0)
    k.clean(a)


def _shahed_drone_v2(a, t, c, pitch, span=2.3, length=1.85):
    """m2._shahed_drone with the delta extruded, the fuselage and nose revolved; same parts."""
    rot = (-pitch, 0, 0)
    fm = mv._frame(tuple(c), rot)
    h = length / 2
    air = a.part('Drone_airframe', 'Fuel', t)
    k.extrude(air, [(0, -h), (span / 2, h * .82), (span / 2 - .12, h), (-span / 2 + .12, h), (-span / 2, h * .82)], .07,
              loc=tuple(c), rot=rot, axis='Z')
    for s in (-1, 1):
        air.box((.05, .34, .26), loc=tuple(fm @ Vector((s * (span / 2 - .05), h * .8, .12))), rot=rot, bevel=0)
    rr = (R90 - pitch, 0, 0)
    k.lathe(air, [(0, -h * .78), (.1, -h * .74), (.1, h * .6), (.06, h * .76), (0, h * .78)],
            loc=tuple(fm @ Vector((0, .05, .05))), rot=rr, seg=6)
    a.part('Drone_nose', 'Undercarriage', t).cyl(.1, .24, r2=.02, loc=tuple(fm @ Vector((0, -h - .06, .05))), rot=rr,
                                                 seg=6, bevel=0)
    a.part('Drone_engine', 'Armor', t).cyl(.09, .3, loc=tuple(fm @ Vector((0, h - .1, .14))), rot=rr, seg=6, bevel=0)
    a.part('Drone_prop', 'Undercarriage', t).box((.56, .04, .07), loc=tuple(fm @ Vector((0, h + .08, .14))), rot=rot,
                                                 bevel=0)


def shahed_truck(a):
    """Shahed launcher (6x6 truck, five-rail rack) on the V2 truck: chamfered bed, the same staircase rack, five
    Shahed deltas with revolved fuselages; same nodes (`Turret`, `Muzzle_main`, the rack parts)."""
    z = _truck_v2(a, -3.2, 3.2, (-2.4, 1.05, 2.15), mg=(.45, -2.5))
    armor = a.part('Armor', 'Armor')
    k.block(a.part('Bed', 'Team'), (1.96, 4.9, .14), loc=(0, .75, z - .05), chamfer=.02)
    for s in (-1, 1):
        armor.box((.08, 4.9, .3), loc=(s * .95, .75, z + .12), bevel=0)
        a.part('Steel', 'Steel').box((.14, .14, .55), loc=(s * .9, 3.0, z - .42), bevel=0)
    a.pivot('Point_fire', (0, -1.0, z + .3))
    t = a.pivot('Turret', (0, 1.0, z + .02))
    a.part('Turntable', 'Steel', t).cyl(.5, .12, loc=(0, 0, .06), seg=12, bevel=0)
    pitch = .19
    hinge = Vector((0, 2.0, .3))
    along = Vector((0, -math.cos(pitch), math.sin(pitch)))
    normal = Vector((0, math.sin(pitch), math.cos(pitch)))
    rot = (-pitch, 0, 0)
    rack = a.part('Rack', 'Armor', t)
    for s in (-1, 1):
        rack.box((.12, 4.1, .14), loc=tuple(hinge + along * 2.05 + Vector((s * .82, 0, 0))), rot=rot, bevel=0)
    for u in (.3, 1.6, 2.9):
        rack.box((1.76, .12, .12), loc=tuple(hinge + along * u), rot=rot, bevel=0)
    rails = a.part('Rack_rails', 'Steel', t)
    top = None
    for kk in range(5):
        u, n = .95 + kk * .5, .14 + kk * .12
        rails.box((.14, 1.7, .08), loc=tuple(hinge + along * (u + .1) + normal * (n - .07)), rot=rot, bevel=0)
        rack.box((.12, .12, max(.12, n)), loc=tuple(hinge + along * (u + .8) + normal * (n / 2 - .02)), rot=rot,
                 bevel=0)
        c = hinge + along * u + normal * n
        _shahed_drone_v2(a, t, c, pitch)
        top = c + along * 1.25
    a.part('Ram_rods', 'Steel', t).box((.1, .1, 1.2), loc=(0, .2, .55), rot=(.55, 0, 0), bevel=0)
    a.part('Rams', 'Armor', t).box((.16, .16, .5), loc=(0, .05, .28), rot=(.55, 0, 0), bevel=0)
    a.pivot('Muzzle_main', tuple(top + normal * .05), t)
    k.clean(a)


# ----------------------------------------------------------------------------- VBIED
def _pickup_v2(a, body_mat='Team', plated=False):
    """m2._pickup on the V2 kit (V2 wheels, an extruded cab with chamfers, chamfered bed and bumpers); same parts and
    geometry. Returns the bed floor height."""
    hd.mark(a, False)
    body = a.part('Body', body_mat)
    dark = a.part('Chassis', 'Undercarriage')
    steel = a.part('Steel', 'Steel')
    dark.box((1.0, 3.9, .22), loc=(0, 0, .42), bevel=0)
    for s in (-1, 1):
        for y in m2.PICKUP_AXLES:
            parts.road_wheel(a, (s * .62, y, .33), .33, .24, s, seg=8, disc_mat='Steel')
    k.extrude(body, [(-2.1, .5), (-2.12, .86), (-1.45, .98), (-.98, 1.02), (-.72, 1.44), (-.12, 1.44), (-.06, .5)], 1.44,
              axis='X', chamfer=.04, corner=.04)
    for s in (-1, 1):
        dark.box((.18, .9, .2), loc=(s * .66, m2.PICKUP_AXLES[0], .72), bevel=0)
        dark.box((.18, .9, .2), loc=(s * .66, m2.PICKUP_AXLES[1], .72), bevel=0)
        if not plated:
            a.part('Glass', 'Glass').box((.03, .55, .32), loc=(s * .725, -.42, 1.2), bevel=0)
    if not plated:
        a.part('Glass', 'Glass').box((1.26, .04, .36), loc=(0, -.85, 1.22), rot=(-.95, 0, 0), bevel=0)
    k.block(body, (1.44, 2.1, .12), loc=(0, 1.0, .72), chamfer=.02)
    for s in (-1, 1):
        body.box((.06, 2.1, .42), loc=(s * .69, 1.0, .98), bevel=0)
    body.box((1.44, .06, .42), loc=(0, -.02, .98), bevel=0)
    body.box((1.44, .06, .4), loc=(0, 2.04, .97), bevel=0)
    k.block(steel, (1.5, .14, .16), loc=(0, -2.16, .56), chamfer=.03)
    k.block(steel, (1.5, .12, .14), loc=(0, 2.1, .56), chamfer=.02)
    _lights(a, (-.52, .52), -2.13, .78, size=(.22, .04, .1))
    _lights(a, (-.62, .62), 2.08, .9, facing=1, size=(.1, .04, .16), lamp='Alloy')
    dark.grille(.7, .2, loc=(0, -2.13, .66), slats=2, depth=.04, thickness=.04)
    a.pivot('Point_exhaust', (.45, 2.1, .45))
    return .78


def vbied(a):
    """Armoured suicide car on the V2 pickup: the same patched plates (three of the roof plates as uneven five-sided
    steel sheets), a chamfered ram plate, the boxed-in bed, spare wheel and sandbags; same nodes, same seed."""
    rng = random.Random(4104)
    _pickup_v2(a, body_mat='Rust', plated=True)
    mats = ('MetalSheet', 'Rust', 'Armor', 'Team')
    for kk, (x, y, z, w, d, h, rot) in enumerate((
            (.0, -1.75, 1.0, 1.52, .7, .08, (-.18, 0, 0)), (.0, -1.2, 1.06, 1.5, .55, .08, (-.05, 0, 0)),
            (.0, -.4, 1.5, 1.52, .72, .08, (0, 0, .04)), (.76, -.45, 1.12, .08, .9, .6, (0, 0, .02)),
            (-.76, -.45, 1.12, .08, .9, .6, (0, 0, -.03)), (.78, -1.5, .8, .08, 1.0, .42, (0, 0, .05)),
            (-.78, -1.5, .8, .08, 1.0, .42, (0, 0, -.04)))):
        part = a.part(f'Plates_{mats[kk % 4]}', mats[kk % 4])
        if h <= .08 and kk < 3:
            j = rng.uniform(.05, .12)
            k.extrude(part, [(-w / 2, -d / 2), (w / 2 - j, -d / 2), (w / 2, -d / 2 + j), (w / 2, d / 2),
                             (-w / 2 + j, d / 2), (-w / 2, d / 2 - j)], h, loc=(x, y, z), rot=rot, axis='Z')
        else:
            part.box((w, d, h), loc=(x, y, z), rot=rot, bevel=0)
    slits = a.part('Slits', 'Undercarriage')
    slits.box((.9, .04, .06), loc=(0, -.88, 1.3), rot=(-.95, 0, 0), bevel=0)
    for s in (-1, 1):
        slits.box((.03, .4, .05), loc=(s * .81, -.45, 1.28), bevel=0)
    _ybox(a.part('Ram_plate', 'Armor'), (1.62, .2, .75), (0, -2.28, .72), rot=(-.12, 0, 0), chamfer=.04)
    for kk in range(4):
        w, d = rng.uniform(.62, .78), rng.uniform(.9, 1.1)
        x = (-1) ** kk * .37
        y = .55 if kk < 2 else 1.5
        a.part(f'Plates_{mats[(kk + 1) % 4]}', mats[(kk + 1) % 4]).box(
            (w, d, .1), loc=(x, y, 1.3 + rng.uniform(0, .06)), rot=(rng.uniform(-.05, .05), rng.uniform(-.05, .05), 0),
            bevel=0)
    k.block(a.part('Bed_box', 'Armor'), (1.4, 2.0, .5), loc=(0, 1.0, 1.02), chamfer=.03)
    k.lathe(a.part('Spare_wheel', 'Rubber'), [(.2, -.1), (.3, -.07), (.3, .07), (.2, .1)], loc=(.2, 1.3, 1.46), seg=10,
            worn=(1,))
    k.block(a.part('Sandbags', 'Sandbag'), (.5, .3, .2), loc=(-.35, 1.7, 1.45), chamfer=.05)
    t = a.pivot('Turret', (0, -.4, 1.54))
    k.lathe(a.part('Hatch', 'Armor', t), [(.22, 0), (.22, .06), (.17, .08), (0, .08)], seg=8, worn=(1,))
    a.pivot('Muzzle_main', (0, -2.06, -.9), t)
    a.pivot('Point_fire', (0, 1.0, 1.4))
    k.clean(a)


# ----------------------------------------------------------------------------- bunker vehicle
def bunker_vehicle(a):
    """Deployable bunker vehicle (m2.bunker_vehicle) on the V2 kit: the lean track units kept (the model has 9 moving
    parts and sits near its budget), extruded hull and armour with chamfers and insets, chamfered side plates, blade
    and bins, an extruded turret with a revolved 105 mm barrel; every Deploy_* pivot, node and the emplacement as
    before."""
    from mb_p21_models import BERM_REST
    from mb_pt5_models import _emplacement
    hd.mark(a, False)
    m2._lean_tracks(a, 1.38, 7.0, .9, .3, 7, .6, sprocket=1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    k.extrude(armor, [(-3.3, .4), (-3.7, .72), (-3.5, .96), (3.35, .96), (3.55, .62), (3.35, .4)], 2.1, axis='X',
              chamfer=.04, corner=.03)
    k.extrude(hull, [(-3.76, .92), (-2.6, 1.7), (3.3, 1.72), (3.56, 1.1), (3.56, .92)], 3.6, axis='X', chamfer=.06,
              corner=.05)
    k.inset(hull, lambda c, n, f: n.x > .9 or n.x < -.9, width=.14, depth=.012)
    for s in (-1, 1):
        _lights(a, (s * 1.2,), -3.3, 1.3, size=(.16, .04, .1))
        _lights(a, (s * 1.5,), 3.57, 1.25, facing=1, size=(.12, .04, .08), lamp='Alloy')
        _hatch(a, s * .6, -2.3, 1.7, .24, handle=False)
        steel.cyl(.09, .3, loc=(s * .9, 3.62, 1.35), rot=FORWARD, seg=8, bevel=0)
        k.block(armor, (.18, .5, .36), loc=(s * 1.62, -2.55, .86), chamfer=.03)
    a.part('Deck', 'Undercarriage').grille(1.6, 1.0, loc=(0, 2.55, 1.73), rot=(-R90, 0, 0), slats=5, depth=.06,
                                           thickness=.04)
    steel.cyl(.78, .09, loc=(0, -.3, 1.705), seg=18, bevel=0)
    a.pivot('Point_exhaust', (.9, 3.7, 1.35))
    a.pivot('Point_fire', (0, 2.55, 1.8))
    for s, name in ((1, 'Deploy_plate_l'), (-1, 'Deploy_plate_r')):
        for y in (-2.1, -.2, 1.7):
            steel.box((.16, .34, .16), loc=(s * 1.8, y, 1.12), bevel=0)
        p = a.pivot(name, (s * 1.86, 0, 1.14))
        a.part(f'{name}_slab', 'Team', p).box((.1, 5.3, 1.02), loc=(s * .06, -.2, .53), bevel=.03, seg=1,
                                             taper=(1, .96))
        ribs = a.part(f'{name}_ribs', 'Armor', p)
        for y in (-2.3, -.2, 1.9):
            ribs.box((.07, .14, .9), loc=(s * .14, y, .5), bevel=0)
        ribs.box((.07, 5.0, .1), loc=(s * .14, -.2, .98), bevel=0)
        a.part(f'{name}_hinge', 'Steel', p).cyl(.07, 5.1, loc=(0, -.2, 0), rot=FORWARD, seg=6, bevel=0)
    p = a.pivot('Deploy_blade', (0, -2.55, .86))
    arms = a.part('Deploy_blade_arms', 'Steel', p)
    for s in (-1, 1):
        arms.limb((s * 1.62, 0, 0), (s * 1.62, -1.75, -.18), .14, .16, bevel=0)
        arms.limb((s * 1.0, -.4, -.35), (s * 1.3, -1.7, .05), .1, .1, bevel=0)
    board = [(-1.72, -.52), (-1.95, -.5), (-2.02, -.25), (-2.04, .05), (-1.98, .35), (-1.86, .52), (-1.76, .5),
             (-1.84, .3), (-1.88, .05), (-1.86, -.22), (-1.74, -.42)]
    k.extrude(a.part('Deploy_blade_plate', 'Armor', p), board, 3.9, axis='X', chamfer=.025)
    a.part('Deploy_blade_edge', 'Steel', p).box((3.86, .1, .09), loc=(0, -1.99, -.54), bevel=0)
    for xx in (-1.2, 0, 1.2):
        a.part('Deploy_blade_ribs', 'Armor', p).box((.1, .14, .8), loc=(xx, -1.72, -.02), bevel=0)
    for s, name in ((1, 'Deploy_spade_l'), (-1, 'Deploy_spade_r')):
        x = s * .8
        for dx in (-.38, .38):
            armor.box((.16, .2, .22), loc=(x + dx, 3.6, .72), bevel=0)
        p = a.pivot(name, (x, 3.66, .72))
        a.part(f'{name}_blade', 'Armor', p).box((.9, .08, 1.15), loc=(0, .1, .62), bevel=.02, seg=1)
        a.part(f'{name}_hinge', 'Steel', p).cyl(.07, .56, rot=ACROSS, seg=6, bevel=0)
        teeth = a.part(f'{name}_teeth', 'Steel', p)
        for dx in (-.33, -.11, .11, .33):
            teeth.box((.14, .06, .16), loc=(dx, .1, 1.24), bevel=0, taper=(.4, 1))
    r = a.pivot('Deploy_riser', (0, -.3, 1.72))
    a.part('Deploy_riser_column', 'Steel', r).cyl(.6, .9, loc=(0, 0, -.43), seg=14, bevel=0)
    a.part('Deploy_riser_bands', 'Armor', r).cyl(.63, .08, loc=(0, 0, -.22), seg=14, bevel=0)
    t = a.pivot('Turret', (0, 0, .04), r)
    k.extrude(a.part('Turret_body', 'Team', t), [(-.8, -1.35), (.8, -1.35), (1.4, -.8), (1.45, .9), (1.1, 1.45),
                                                 (-1.1, 1.45), (-1.45, .9), (-1.4, -.8)], .62, loc=(0, 0, .31),
              axis='Z', chamfer=.05, taper=.86)
    tarm = a.part('Turret_armor', 'Armor', t)
    k.block(tarm, (.9, .42, .54), loc=(0, -1.42, .34), chamfer=.04, taper=(.9, .9))
    k.block(tarm, (2.0, .4, .36), loc=(0, 1.45, .3), chamfer=.04)
    k.block(a.part('Turret_steel', 'Steel', t), (.22, .26, .22), loc=(.7, -.6, .72), chamfer=.02)
    a.part('Sight', 'Glass', t).box((.16, .04, .1), loc=(.7, -.74, .74), bevel=0)
    _hatch(a, -.55, .3, .62, .28, parent=t, seg=10, handle=False)
    for s in (-1, 1):
        mv._smoke(a, a.part('Smoke', 'Steel', t), 1.0, -.7, .66, s, count=3, gap=.08, r=.045, depth=.16)
    y0, length, z = -1.62, 4.0, .36
    parts.barrel(a, 'Main_cannon', t, 0, y0, z, length, .085, seg=10, sleeve=1.3, extractor=(.5, 1.3, .2),
                 brake_name='Muzzle_brake', brake='collar')
    a.pivot('Muzzle_main', (0, y0 - length - .2, z), t)
    mg = a.part('MG_port', 'Steel', t)
    mg.box((.12, .3, .12), loc=(.55, -1.4, .3), bevel=0)
    mg.cyl(.05, .45, loc=(.55, -1.75, .3), rot=FORWARD, seg=6, bevel=0)
    a.pivot('Muzzle_mg', (.55, -1.99, .3), t)
    _emplacement(a)
    a.pivots['Deploy_berm'].scale = (BERM_REST,) * 3
    k.clean(a)


# ============================================================================= pass 3f: wheeled, technicals, hover, light
def wheeled_gun(a):
    """Wheeled tank destroyer (Centauro II, m2.wheeled_gun) on the V2 kit: V2 wheels, an extruded hull with chamfers and
    insets, a lofted turret, the 120 mm gun as one surface; same nodes (`Turret`, `Main_cannon`, `Muzzle_brake`,
    `Muzzle_main`, `Muzzle_coax`, `Mount_mg`, `Muzzle_mg`) and pivots."""
    hd.mark(a, False)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    a.part('Chassis', 'Undercarriage').box((1.5, 5.4, .3), loc=(0, 0, .5), bevel=0)
    for s in (-1, 1):
        for y in (-2.0, -1.0, .8, 1.8):
            parts.road_wheel(a, (s * .94, y, .46), .46, .34, s, seg=8)
    k.extrude(hull, [(-2.6, .58), (-3.0, .9), (-2.2, 1.42), (2.8, 1.44), (2.95, .66)], 2.2, axis='X', chamfer=.06,
              corner=.04)
    k.inset(hull, lambda c, n, f: n.z > .5 and n.y < -.2 and c.y < -1.9, width=.07, depth=.012)
    for s in (-1, 1):
        k.block(armor, (.42, 2.2, .07), loc=(s * .94, -1.5, 1.0), chamfer=.02)                          # fenders
        k.block(armor, (.42, 2.2, .07), loc=(s * .94, 1.3, 1.0), chamfer=.02)
        k.block(armor, (.08, 5.0, .4), loc=(s * 1.14, .1, 1.2), chamfer=.02)                            # side armour
        _lights(a, (s * .75,), -2.85, 1.05, size=(.14, .04, .1))
        _lights(a, (s * .85,), 2.96, 1.1, facing=1, size=(.12, .04, .08), lamp='Alloy')
    _hatch(a, .8, -2.12, 1.42, .17, handle=False)
    a.part('Deck', 'Undercarriage').grille(1.2, .8, loc=(0, 2.2, 1.45), rot=(-R90, 0, 0), slats=4, depth=.05,
                                           thickness=.04)
    a.pivot('Point_exhaust', (-.8, 2.9, 1.1))
    a.pivot('Point_fire', (0, 2.2, 1.5))
    steel.cyl(.95, .08, loc=(0, -.1, 1.44), seg=16, bevel=0)
    t = a.pivot('Turret', (0, -.1, 1.44))
    _turret_loft(a.part('Turret_body', 'Team', t),
                 [(-.35, -1.35), (.35, -1.35), (1.08, -.9), (1.12, 1.0), (.9, 1.75), (-.9, 1.75), (-1.12, 1.0),
                  (-1.08, -.9)], .32, .6, .92, chamfer=.04)
    tarm = a.part('Turret_armor', 'Armor', t)
    k.block(tarm, (.6, .3, .42), loc=(0, -1.4, .3), chamfer=.04, taper=(.9, .9))                       # mantlet
    k.block(tarm, (.34, .3, .2), loc=(-.55, -.6, .7), chamfer=.03)                                     # sight
    a.part('Sight', 'Glass', t).box((.24, .03, .1), loc=(-.55, -.76, .7), bevel=0)
    k.block(tarm, (1.6, .3, .32), loc=(0, 1.85, .36), chamfer=.03)                                     # bustle box
    for s in (-1, 1):
        parts.smoke_launcher(a, a.part('Smoke', 'Steel', t), 1.0, -.4, .5, s, count=2, gap=.08, r=.05, depth=.14)
    _hatch(a, .5, .4, .6, .24, parent=t, seg=10, handle=False)
    y0, length, z = -1.52, 4.2, .32
    parts.barrel(a, 'Main_cannon', t, 0, y0, z, length, .08, seg=10, sleeve=1.25, extractor=(.42, 1.62, .4),
                 brake_name='Muzzle_brake', brake='collar')
    a.pivot('Muzzle_main', (0, y0 - length - .16, z), t)
    mv._coax(a, t, -.3, -1.4, .38, length=.36, housing=.24)
    mv._roof_mg(a, t, (.5, .4, .62), length=.75, shield=False)
    k.clean(a)


def zu23_technical(a):
    """Anti-aircraft technical (ZU-23-2 on the pickup, m2.zu23_technical) on the V2 pickup: lathed carriage ring,
    chamfered cradle and receivers, the two 23 mm barrels as one revolved surface each with their flash hiders; same
    nodes (`Turret`, `Main_cannon`/`_2`, `Muzzle_brake`/`_2`, `Muzzle_main`)."""
    z = _pickup_v2(a)
    a.pivot('Point_fire', (0, 1.0, 1.0))
    t = a.pivot('Turret', (0, 1.1, z))
    k.lathe(a.part('Gun_carriage', 'Armor', t), [(.45, 0), (.45, .12), (.38, .15), (.2, .15)], seg=10, worn=(1,))
    k.block(a.part('Turret_armor', 'Armor', t), (.6, .7, .3), loc=(0, .05, .3), chamfer=.03)             # cradle
    for s, suffix in ((1, ''), (-1, '_2')):
        x = s * .16
        k.block(a.part(f'Main_cannon{suffix}', 'Steel', t), (.14, .6, .16), loc=(x, -.15, .55), chamfer=.02)
        parts.barrel(a, f'Main_cannon{suffix}', t, x, -.43, .55, 1.85, .045, seg=6, sleeve=1.1,
                     extractor=(.55, 1.3, .22), brake_name=f'Muzzle_brake{suffix}', brake='collar')
        k.block(a.part('Ammo_boxes', 'Crate', t), (.2, .4, .3), loc=(s * .42, -.05, .55), chamfer=.02)
        k.block(a.part('Seats', 'Canvas', t), (.26, .24, .1), loc=(s * .3, .5, .42), chamfer=.02)
    a.part('Sight', 'Glass', t).box((.1, .1, .1), loc=(.3, .2, .75), bevel=0)
    a.pivot('Muzzle_main', (.16, -2.46, .55), t)
    k.clean(a)


def rocket_technical(a):
    """Rocket technical (Type 63 on the pickup, m2.rocket_technical) on the V2 pickup: lathed turntable, chamfered
    cradle, twelve revolved tubes with rim collars and dark bore discs in three chamfered bands, the cab-roof machine
    gun; same nodes (`Turret`, `Rocket_tubes`, `Tubes_bore`, `Muzzle_main`, `Mount_mg`, `Muzzle_mg`)."""
    z = _pickup_v2(a)
    mv._roof_mg(a, None, (.3, -.72, 1.44), length=.7, shield=False)
    a.pivot('Point_fire', (0, 1.0, 1.0))
    t = a.pivot('Turret', (0, 1.05, z))
    k.lathe(a.part('Turret_steel', 'Steel', t), [(.32, 0), (.32, .1), (.26, .12), (.1, .12)], seg=12, worn=(1,))
    k.block(a.part('Turret_armor', 'Armor', t), (.5, .5, .36), loc=(0, .1, .28), chamfer=.03)             # cradle
    tilt = .12
    rot = (R90 - tilt, 0, 0)
    axis = Vector((0, -math.cos(tilt), math.sin(tilt)))
    c = Vector((0, -.1, .72))
    tubes = a.part('Rocket_tubes', 'Crate', t)
    bores = a.part('Tubes_bore', 'Undercarriage', t)
    for row in range(3):
        for col in range(4):
            p = c + Vector((-.3 + col * .2, 0, -.2 + row * .2))
            k.lathe(tubes, [(.06, -.6), (.085, -.6), (.085, .54), (.1, .57), (.1, .61), (.06, .61)], loc=tuple(p),
                    rot=rot, seg=8, worn=(3,))
            bores.cyl(.06, .02, loc=tuple(p + axis * .61), rot=rot, seg=8, bevel=0)
    bands = a.part('Pod_bands', 'Armor', t)
    for kk in (-.35, .35):
        k.block(bands, (.86, .06, .66), loc=tuple(c + axis * kk), rot=(-tilt, 0, 0), chamfer=.02)
    a.pivot('Muzzle_main', tuple(c + axis * .66), t)
    k.clean(a)


def hover_gunboat(a):
    """Escort hovercraft (AK-630, m2.hover_gunboat) on the V2 kit: the hull a sharp-edged loft on the same stations,
    an extruded wheelhouse with chamfers, the six-barrel AK-630 as a cluster of thin revolved barrels, the fan ducts
    as revolved rings; same nodes (`Mount_mg`, `Muzzle_mg`, `Radar`, `Propeller`, `Propeller_2`) and pivots."""
    hd.mark(a, False)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    stations = ((-7.0, .25), (-6.6, 1.05), (-5.8, 1.6), (-4.2, 1.92), (-1.0, 1.95), (2.5, 1.85), (5.2, 1.6),
                (6.7, 1.35), (7.0, 1.1))
    a.part('Skirt', 'Rubber').loft([[(hw * .86, y, 0), (hw, y, .5), (hw * .96, y, .95), (-hw * .96, y, .95),
                                     (-hw, y, .5), (-hw * .86, y, 0)] for y, hw in stations], bevel=0)
    k.sharp_loft(hull, [[(hw * .95, y, .9), (hw * .9, y, 1.45), (-hw * .9, y, 1.45), (-hw * .95, y, .9)]
                        for y, hw in stations], chamfer=.05)
    a.part('Skirt_band', 'Undercarriage').loft([[(hw * 1.005, y, .42), (hw * 1.005, y, .56), (-hw * 1.005, y, .56),
                                                 (-hw * 1.005, y, .42)] for y, hw in stations[1:-1]], bevel=0)
    # the wheelhouse amidships
    k.extrude(hull, [(-2.6, 1.4), (-2.2, 2.45), (.8, 2.5), (1.0, 1.4)], 2.3, axis='X', chamfer=.06, corner=.04)
    k.inset(hull, lambda c, n, f: abs(n.x) > .9 and c.z > 1.7, width=.14, depth=.01)
    glass = a.part('Glass', 'Glass')
    glass.box((2.0, .05, .34), loc=(0, -2.34, 2.12), rot=(-.36, 0, 0), bevel=0)
    for s in (-1, 1):
        glass.box((.04, 1.6, .3), loc=(s * 1.16, -.9, 2.1), bevel=0)
    k.block(armor, (1.4, 1.2, .12), loc=(0, -.5, 2.54), chamfer=.02)                                   # roof
    _hatch(a, .4, -.3, 2.6, .17, handle=False)
    k.block(steel, (.16, .16, 1.0), loc=(0, .2, 3.05), chamfer=0)                                      # mast
    r = a.pivot('Radar', (0, .2, 3.55))
    k.block(a.part('Radar_bar', 'Armor', r), (1.1, .16, .12), loc=(0, 0, .06), chamfer=.02)
    a.part('Beacon', 'TeamGlow').box((.12, .12, .1), loc=(0, .2, 3.5), bevel=0)
    # the AK-630 on the foredeck
    m = a.pivot('Mount_mg', (0, -4.4, 1.45))
    mount = a.part('CIWS_mount', 'Armor', m)
    k.lathe(mount, [(.6, 0), (.6, .24), (.52, .3), (.3, .3)], seg=14, worn=(1,))
    k.block(mount, (.9, 1.0, .55), loc=(0, .1, .55), chamfer=.06, taper=(.8, .8))
    guns = a.part('CIWS_barrels', 'Steel', m)
    for i in range(6):
        u = i * TAU / 6
        k.lathe(guns, [(.045, 0), (.045, 1.45), (.055, 1.48), (.055, 1.52), (0, 1.52)],
                loc=(math.cos(u) * .1, -.35, .58 + math.sin(u) * .1), rot=FORWARD, seg=6)
    for d0 in (.9, 1.42):
        k.ring(guns, [(.12, d0), (.2, d0), (.2, d0 + .1), (.12, d0 + .1)], loc=(0, -.35, .58), rot=FORWARD, seg=8)
    a.pivot('Muzzle_mg', (0, -1.9, .58), m)
    # two ducted fans aft on pylons, their rudders behind
    for s, name in ((1, 'Propeller'), (-1, 'Propeller_2')):
        x, y, z = s * .95, 5.3, 2.35
        k.ring(a.part('Fan_ducts', 'Team'), [(.83, 0), (.95, 0), (.95, .52), (1.0, .6), (.83, .6)],
               loc=(x, y - .3, z), rot=(-R90, 0, 0), seg=14, worn=(3,))
        k.ring(armor, [(.9, .58), (1.02, .58), (1.02, .66), (.9, .66)], loc=(x, y - .3, z), rot=(-R90, 0, 0), seg=14)
        k.block(steel, (.16, .5, .9), loc=(x, y, 1.45 + .45), chamfer=0)                              # pylon
        p = a.pivot(name, (x, y - .05, z))
        k.lathe(a.part('Fan_hubs', 'Armor', p), [(.18, -.2), (.18, .12), (.12, .2), (0, .2)], rot=FORWARD, seg=10)
        blades = a.part('Fan_blades', 'Undercarriage', p)
        for i in range(5):
            u = i * TAU / 5
            blades.box((.2, .05, .72), loc=(math.cos(u) * .48, 0, math.sin(u) * .48), rot=(0, -u + R90, 0), bevel=0)
        for dx in (-.35, .35):
            k.block(armor, (.06, .5, 1.5), loc=(x + dx, y + .75, z), chamfer=0)                       # rudders
    a.pivot('Point_exhaust', (0, 5.9, 2.3))
    a.pivot('Point_fire', (0, -.5, 2.6))
    k.clean(a)


def _tracked_v2(a, length, width, glacis, height, wheels, cleat=.44):
    """pn._tracked on the V2 kit (V2 track units, an extruded hull with a chamfered glacis); returns the hull top."""
    parts.track_unit(a, width / 2 - .25, length, .77, .26, wheels, .46, sprocket_end=1, cleat_pitch=cleat, teeth=6,
                     wheel_seg=7)
    hull = a.part('Hull', 'Team')
    y0, y1 = -length / 2, length / 2
    k.extrude(hull, [(y0, .55), (y0 + .05, .8), (y0 + glacis, height), (y1 - .1, height), (y1, height - .2),
                     (y1, .55)], width - .5, axis='X', chamfer=.05, corner=.04)
    k.inset(hull, lambda c, n, f: n.z > .5 and n.y < -.2 and c.y < y0 + glacis + .3, width=.07, depth=.012)
    armor = a.part('Armor', 'Armor')
    for s in (-1, 1):
        k.block(armor, (.6, length * .92, .06), loc=(s * (width / 2 - .25), -.03, .82), chamfer=.02)      # fenders
        _lights(a, (s * (width / 2 - .5),), y0 + .02, height - .3, size=(.16, .04, .1))
        _lights(a, (s * (width / 2 - .5),), y1 + .02, height - .4, facing=1, size=(.12, .04, .08), lamp='Alloy')
    a.pivot('Point_exhaust', (width / 2 - .45, y1 - .3, height))
    a.pivot('Point_fire', (0, 0, height + .2))
    return height


def aa_gun_vehicle(a):
    """Tracked 40 mm SPAAG (CV90 AA look, mb_p25_new.aa_gun_vehicle) on the V2 kit: V2 running gear, an extruded
    hull and turret, the 40 mm gun as one revolved surface, the search radar on its mast; same nodes."""
    hd.mark(a, False)
    top = _tracked_v2(a, 5.3, 2.5, .6, 1.55, 6)
    steel = a.part('Steel', 'Steel')
    t = a.pivot('Turret', (0, .3, top))
    _hatch(a, .6, -1.7, top, .2, handle=False)
    a.part('Deck', 'Undercarriage').grille(1.0, .8, loc=(-.5, 1.8, top + .01), rot=(-R90, 0, 0), slats=4, depth=.05,
                                           thickness=.04)
    k.extrude(a.part('Turret_body', 'Team', t), [(-.55, -1.0), (.55, -1.0), (.85, -.5), (.85, .9), (-.85, .9),
                                                 (-.85, -.5)], .7, loc=(0, 0, .35), axis='Z', chamfer=.05, corner=.04,
              taper=.88)
    steel.cyl(.6, .08, loc=(0, .3, top), seg=14, bevel=0)
    pitch = math.radians(20)
    parts.barrel(a, 'Main_cannon', t, 0, -1.0, .45, 2.2, .07, seg=10, sleeve=1.25, extractor=(.4, 1.5, .4),
                 brake_name='Muzzle_brake', brake='collar', rot=(R90 - pitch, 0, 0))
    d = 2.36
    a.pivot('Muzzle_main', (0, -1.0 - d * math.cos(pitch), .45 + d * math.sin(pitch)), t)
    k.block(a.part('Turret_armor', 'Armor', t), (.5, .4, .4), loc=(0, -1.0, .45), chamfer=.03, taper=(.9, .9))
    r = a.pivot('Radar', (0, .9, .95), t)
    k.lathe(a.part('Radar_mast', 'Steel', r), [(.1, -.25), (.1, 0), (.06, .02), (.06, .08)], seg=8)
    k.block(a.part('Radar_panel', 'Armor', r), (1.0, .1, .45), loc=(0, 0, .22), chamfer=.02)
    pn._stripes(a, 3.5, 2.0, top)
    k.clean(a)


def airborne_vehicle(a):
    """Light airborne IFV (BMD-4 look, mb_p25_new.airborne_vehicle) on the V2 kit: V2 running gear, an extruded hull
    and turret, the 100 mm gun as one surface, the coaxial gun; the pallet-and-canopies variant
    (`airborne_vehicle_chute`) keeps its old build."""
    hd.mark(a, False)
    top = _tracked_v2(a, 4.8, 2.5, .9, 1.3, 5)
    t = a.pivot('Turret', (0, .2, top))
    _hatch(a, .6, -1.55, top, .2, handle=False)
    k.extrude(a.part('Turret_body', 'Team', t), [(-.5, -.85), (.5, -.85), (.75, -.4), (.75, .85), (-.75, .85),
                                                 (-.75, -.4)], .55, loc=(0, 0, .28), axis='Z', chamfer=.05, corner=.04,
              taper=.86)
    parts.barrel(a, 'Main_cannon', t, 0, -.85, .35, 1.9, .09, seg=10, sleeve=1.3, extractor=(.45, 1.5, .3),
                 brake_name='Muzzle_brake', brake='collar')
    a.pivot('Muzzle_main', (0, -.85 - 1.9 - .2, .35), t)
    mv._coax(a, t, .35, -.85, .35, length=.9, housing=.3)
    k.block(a.part('Turret_armor', 'Armor', t), (.5, .3, .4), loc=(0, -.85, .3), chamfer=.03, taper=(.9, .9))
    pn._stripes(a, 2.8, 2.0, top)
    k.clean(a)


def fibre_fpv_carrier(a):
    """4x4 armoured pickup with an FPV rack and two cable spools (mb_p25_new.fibre_fpv_carrier) on the V2 kit: V2
    wheels, an extruded cab, a chamfered bed, revolved flanged spools; same nodes (`Turret`, `Muzzle_main`)."""
    hd.mark(a, False)
    body = a.part('Hull', 'Team')
    a.part('Chassis', 'Undercarriage').box((1.3, 4.0, .22), loc=(0, 0, .5), bevel=0)
    for s in (-1, 1):
        for y in (-1.5, 1.4):
            parts.road_wheel(a, (s * .82, y, .42), .42, .3, s, seg=8)
    k.extrude(body, [(-2.2, .5), (-2.2, .95), (-1.55, 1.1), (-1.25, 1.62), (-.25, 1.62), (-.2, .5)], 1.9, axis='X',
              chamfer=.06, corner=.04)
    k.inset(body, lambda c, n, f: abs(n.x) > .9 and c.y < -.6, width=.09, depth=.012)
    bed = a.part('Bed', 'Armor')
    k.block(bed, (1.8, 2.5, .08), loc=(0, 1.05, .84), chamfer=.02)
    for s in (-1, 1):
        k.block(bed, (.08, 2.5, .42), loc=(s * .9, 1.05, 1.03), chamfer=0)
    k.block(bed, (1.8, .08, .42), loc=(0, 2.3, 1.03), chamfer=0)
    k.block(bed, (1.8, .08, .42), loc=(0, -.2, 1.03), chamfer=0)
    glass = a.part('Glass', 'Glass')
    glass.box((1.6, .05, .35), loc=(0, -2.21, 1.3), bevel=0)
    for s in (-1, 1):
        glass.box((.04, .7, .3), loc=(s * .96, -1.0, 1.35), bevel=0)
    k.block(a.part('Steel', 'Steel'), (2.0, .14, .18), loc=(0, -2.28, .6), chamfer=.03)
    _lights(a, (-.7, .7), -2.21, .85, size=(.2, .04, .1))
    t = a.pivot('Turret', (0, 1.2, .95))
    k.block(a.part('Rack', 'Steel', t), (1.2, .9, .12), loc=(0, 0, .3), rot=(.25, 0, 0), chamfer=.02)
    drones = a.part('Drones', 'Undercarriage', t)
    for x in (-.35, .35):
        k.block(drones, (.45, .45, .12), loc=(x, 0, .42), rot=(.25, 0, 0), chamfer=.03)
    a.pivot('Muzzle_main', (0, -.4, .6), t)
    spools = a.part('Spools', 'Hazard')
    for x in (-.55, .55):
        k.lathe(spools, [(0, -.175), (.3, -.175), (.3, -.13), (.2, -.11), (.2, .11), (.3, .13), (.3, .175), (0, .175)],
                loc=(x, 1.95, 1.2), rot=ACROSS, seg=12, worn=(1, 6))
    k.block(a.part('Spool_frame', 'Armor'), (1.7, .12, .1), loc=(0, 1.95, .98), chamfer=0)
    a.pivot('Point_exhaust', (.7, 2.3, .7))
    a.pivot('Point_fire', (0, 0, 1.6))
    k.clean(a)


def interceptor_drone_vehicle(a):
    """4x4 tactical truck (JLTV look) with a hexagonal interceptor-drone launcher (mb_p25_new.interceptor_drone_vehicle)
    on the V2 kit: V2 wheels, an extruded cab, a chamfered bed, the hex box as a revolved six-sided body in bands;
    same nodes (`Turret`, `Muzzle_main`)."""
    hd.mark(a, False)
    body = a.part('Hull', 'Team')
    a.part('Chassis', 'Undercarriage').box((1.4, 4.4, .22), loc=(0, 0, .5), bevel=0)
    for s in (-1, 1):
        for y in (-1.6, 1.55):
            parts.road_wheel(a, (s * .86, y, .45), .45, .32, s, seg=8)
    k.extrude(body, [(-2.4, .5), (-2.4, 1.1), (-1.8, 1.25), (-1.45, 1.7), (-.3, 1.7), (-.3, .5)], 2.0, axis='X',
              chamfer=.06, corner=.04)
    k.inset(body, lambda c, n, f: abs(n.x) > .9 and c.y < -.7, width=.1, depth=.012)
    k.block(a.part('Bed', 'Armor'), (2.0, 2.6, .6), loc=(0, 1.1, .85), chamfer=.04)
    glass = a.part('Glass', 'Glass')
    glass.box((1.7, .05, .35), loc=(0, -2.41, 1.35), bevel=0)
    for s in (-1, 1):
        glass.box((.04, .8, .34), loc=(s * 1.01, -1.2, 1.4), bevel=0)
    k.block(a.part('Steel', 'Steel'), (2.1, .14, .18), loc=(0, -2.46, .6), chamfer=.03)
    _lights(a, (-.7, .7), -2.4, .95, size=(.2, .04, .1))
    _lights(a, (-.8, .8), 2.42, .8, facing=1, size=(.12, .04, .1), lamp='Alloy')
    _hatch(a, .5, -.9, 1.7, .2, handle=False)
    t = a.pivot('Turret', (0, 1.2, 1.15))
    pitch = .5
    rot = (R90 - pitch, 0, 0)
    k.lathe(a.part('Launcher_ring', 'Armor', t), [(.5, 0), (.5, .1), (.4, .12), (.2, .12)], seg=12, worn=(1,))
    k.lathe(a.part('Launcher', 'Team', t), [(0, -.8), (.54, -.8), (.6, -.74), (.6, .74), (.54, .8), (0, .8)],
            loc=(0, 0, .75), rot=rot, seg=6, worn=(1, 4))
    for kk in (-.4, .35):
        k.ring(a.part('Launcher_bands', 'Armor', t), [(.59, -.04), (.65, -.04), (.65, .04), (.59, .04)],
               loc=(0, -math.cos(pitch) * kk, .75 + math.sin(pitch) * kk), rot=rot, seg=6)
    front = (0, -.82 * math.cos(pitch), .75 + .82 * math.sin(pitch))
    pn._tube_faces(a, t, front, pitch, [(0, 0)] + [(math.cos(i * TAU / 6) * .35, math.sin(i * TAU / 6) * .35)
                                                    for i in range(6)], .12)
    a.pivot('Muzzle_main', front, t)
    k.block(a.part('Radar_panel', 'Armor'), (.7, .1, .5), loc=(.7, -.3, 1.95), chamfer=.02)
    k.block(a.part('Radar_mast', 'Steel'), (.1, .1, .3), loc=(.7, -.3, 1.8), chamfer=0)
    a.pivot('Point_exhaust', (.8, 2.4, .8))
    a.pivot('Point_fire', (0, 0, 1.7))
    k.clean(a)


# ============================================================================= pass 3g: sensor, ATGM, mortar and gun vehicles
def _truck_pn_v2(a, length, width, cab, axles, r=.45, bed_h=1.25, cab_h=2.0, armoured=True,
                  chassis='Undercarriage'):
    """pn._truck on the V2 kit (extruded cab with a sloped screen, V2 wheels, chamfered bed, deck plate, bumper, grille);
    same parts and geometry. Returns the bed top."""
    hd.mark(a, False)
    body = a.part('Hull', 'Team' if armoured else 'Armor')
    plate = a.part('Deck_plate', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    y0 = -length / 2
    dark.box((width * .8, length * .95, .3), loc=(0, 0, r + .05), bevel=0)
    step = (length - 1.2) / max(1, axles - 1)
    ys = [y0 + .8 + step * i for i in range(axles)]
    for s in (-1, 1):
        for y in ys:
            parts.road_wheel(a, (s * (width / 2 - .17), y, r), r, .32, s, seg=8)
    k.extrude(body, [(y0, r), (y0, cab_h - .55), (y0 + .4, cab_h), (y0 + cab - .05, cab_h), (y0 + cab, r)], width,
              axis='X', chamfer=.05, corner=.04)
    k.inset(body, lambda c, n, f: abs(n.x) > .9 and c.y < y0 + cab - .1 and c.z > r + .3, width=.08, depth=.012)
    k.block(body, (width, length - cab - .05, bed_h - r), loc=(0, y0 + cab + (length - cab) / 2, r + (bed_h - r) / 2),
            chamfer=.05)
    k.block(plate, (width - .2, length - cab - .3, .05), loc=(0, y0 + cab + (length - cab) / 2 + .05, bed_h + .02),
            chamfer=.02)
    glass = a.part('Glass', 'Glass')
    glass.box((width * .78, .04, .5), loc=(0, y0 + .18, cab_h - .27), rot=(-.63, 0, 0), bevel=0)
    for s in (-1, 1):
        glass.box((.03, cab * .38, .34), loc=(s * (width / 2 + .005), y0 + cab * .52, cab_h - .4), bevel=0)
        steel.box((.14, .3, .05), loc=(s * (width / 2 - .05), y0 + cab * .5, r + .2), bevel=0)
    k.block(steel, (width + .04, .16, .2), loc=(0, y0 - .05, r + .12), chamfer=.03)
    dark.grille(.9, .3, loc=(0, y0 - .02, r + .75), slats=3, depth=.05, thickness=.05)
    _lights(a, (-(width / 2 - .25), width / 2 - .25), y0 - .02, r + .5)
    _lights(a, (-(width / 2 - .2), width / 2 - .2), y0 + length + .02, r + .55, facing=1, size=(.16, .04, .1),
            lamp='Alloy')
    a.pivot('Point_exhaust', (width / 2 - .2, y0 + cab, cab_h))
    a.pivot('Point_fire', (0, 0, bed_h + .2))
    return bed_h


def _launcher_v2(a, parent, loc, size, cells, pitch, mat='Armor', tube_mat='Undercarriage'):
    """pn._launcher_box on the V2 kit: a chamfered box tilted up by `pitch`, ringed tube mouths, side rails; returns the
    front centre like the original."""
    w, d, h = size
    box = a.part('Launcher', mat, parent)
    k.block(box, size, loc=loc, rot=(-pitch, 0, 0), chamfer=.05, ends=(True, True))
    c, s = math.cos(pitch), math.sin(pitch)
    front = (loc[0], loc[1] - (d / 2 + .02) * c, loc[2] + (d / 2 + .02) * s)
    tubes = a.part('Tubes', tube_mat, parent)
    rr = min(w / cells[0], h / cells[1]) * .36
    for i in range(cells[0]):
        for j in range(cells[1]):
            x = (i - (cells[0] - 1) / 2) * w / cells[0]
            u = (j - (cells[1] - 1) / 2) * h / cells[1]
            k.lathe(tubes, [(0, 0), (rr, 0), (rr * 1.12, .02), (rr * 1.12, .04)],
                    loc=(front[0] + x, front[1] + u * s, front[2] + u * c), rot=(R90 - pitch, 0, 0), seg=10)
    rails = a.part('Launcher_rails', 'Steel', parent)
    for sx in (-1, 1):
        _ybox(rails, (.07, d * .9, .09), (loc[0] + sx * (w / 2 + .02), loc[1], loc[2]), rot=(-pitch, 0, 0), chamfer=.01)
    return front


def microwave_vehicle(a):
    """6x6 microwave-emitter truck (pn.microwave_vehicle) on the V2 kit: V2 truck, generator housing with vents, lathed
    pedestal, framed emitter panel with ribs; same nodes."""
    top = _truck_pn_v2(a, 5.8, 2.1, 1.8, 3, r=.45, bed_h=1.2)
    k.block(a.part('Generators', 'Armor'), (1.8, 1.2, .7), loc=(0, .5, top + .35), chamfer=.06)
    a.part('Generator_vents', 'Undercarriage').grille(.8, .4, loc=(.92, .5, top + .35), rot=(0, 0, R90), slats=3, depth=.05,
                                                      thickness=.04)
    k.lathe(a.part('Gen_stack', 'Steel'), [(.07, 0), (.07, .5)], loc=(.6, 1.0, top + .7), seg=8)
    t = a.pivot('Turret', (0, 1.8, top))
    k.lathe(a.part('Pedestal', 'Armor', t), [(.5, 0), (.5, .08), (.35, .14), (.35, .55), (.46, .6)], seg=12, worn=(1,))
    em = a.part('Emitter', 'Team', t)
    _ybox(em, (1.8, .25, 1.4), (0, -.15, 1.2), rot=(-.15, 0, 0), chamfer=.06)
    face = a.part('Emitter_face', 'Undercarriage', t)
    _ybox(face, (1.6, .05, 1.2), (0, -.3, 1.2), rot=(-.15, 0, 0), chamfer=0)
    rib = a.part('Emitter_ribs', 'Steel', t)
    for x in (-.4, 0, .4):
        _ybox(rib, (.05, .05, 1.1), (x, -.34, 1.2), rot=(-.15, 0, 0), chamfer=0)
    for sx in (-1, 1):
        _ybox(rib, (.1, .5, .12), (sx * .55, .05, .62), rot=(.5, 0, 0), chamfer=.01)
    a.pivot('Muzzle_main', (0, -.35, 1.2), t)
    pn._stripes(a, 2.0, 2.1, 2.0, y=-2.0)
    k.clean(a)


def nlos_atgm_vehicle(a):
    """6x6 NLOS-ATGM truck (pn.nlos_atgm_vehicle) on the V2 kit: V2 truck, a ringed four-cell launcher on a hinge block,
    lathed sensor mast with a lens head, roof MG; same nodes."""
    top = _truck_pn_v2(a, 6.0, 2.1, 1.9, 3, r=.45, bed_h=1.2)
    t = a.pivot('Turret', (0, 1.4, top))
    k.block(a.part('Hinge', 'Armor', t), (1.4, .8, .35), loc=(0, .5, .2), chamfer=.04)
    front = _launcher_v2(a, t, (0, 0, .7), (1.6, 1.8, .9), (2, 2), math.radians(30), mat='Team', tube_mat='Steel')
    a.pivot('Muzzle_missile', front, t)
    k.lathe(a.part('Sensor_mast', 'Steel'), [(.08, -.5), (.08, -.15), (.06, -.13), (.06, .3)], loc=(-.7, -1.6, 2.5), seg=8)
    k.block(a.part('Sensor', 'Glass'), (.3, .3, .25), loc=(-.7, -1.6, 2.9), chamfer=.04)
    k.block(a.part('Sensor_body', 'Armor'), (.36, .36, .06), loc=(-.7, -1.6, 2.78), chamfer=.01)
    mv._roof_mg(a, None, (.5, -2.3, 2.0), length=.6, shield=False)
    pn._stripes(a, 1.6, 2.1, 2.0, y=-2.0)
    k.clean(a)


def radar_atgm_vehicle(a):
    """Khrizantema-S (pn.radar_atgm_vehicle) on the V2 kit: V2 tracked hull, twin rails on raised arms, a revolved
    missile, the radar box with a lens; same nodes."""
    top = _tracked_v2(a, 5.6, 2.5, 1.0, 1.45, 6)
    t = a.pivot('Turret', (0, -.8, top))
    rails = a.part('Rails', 'Armor', t)
    for x in (-.45, .45):
        _ybox(rails, (.25, 2.2, .25), (x, -.4, .5), rot=(.3, 0, 0), chamfer=.04)
    arms = a.part('Rail_arms', 'Steel', t)
    for x in (-.45, .45):
        k.block(arms, (.12, .3, .45), loc=(x, .2, .22), chamfer=.02)
    k.lathe(a.part('Missiles', 'Steel', t), [(0, -.9), (.1, -.9), (.1, .5), (.08, .7), (.04, .9), (0, .92)],
            loc=(0, -.5, .72), rot=(R90 - .3, 0, 0), seg=8)
    a.pivot('Muzzle_missile', (0, -1.55, .85), t)
    r = a.pivot('Radar', (0, 1.4, top + .1))
    k.block(a.part('Radar_box', 'Medical', r), (1.2, .9, .8), loc=(0, 0, .45), chamfer=.08)
    k.block(a.part('Radar_lens', 'Glass', r), (.9, .05, .5), loc=(0, -.46, .5), chamfer=0)
    _hatch(a, .8, .4, top, .2, handle=False)
    pn._stripes(a, 3.0, 2.0, top)
    k.clean(a)


def recoilless_jeep(a):
    """106 mm recoilless jeep (pn.recoilless_jeep) on the V2 kit: V2 wheels, an extruded body with a windscreen frame, a
    revolved barrel, the breech and a spare wheel; same nodes."""
    hd.mark(a, False)
    body = a.part('Body', 'Team')
    steel = a.part('Steel', 'Steel')
    a.part('Chassis', 'Undercarriage').box((1.2, 3.0, .22), loc=(0, 0, .45), bevel=0)
    for s in (-1, 1):
        for y in (-1.05, .95):
            parts.road_wheel(a, (s * .57, y, .33), .33, .24, s, seg=8)
    k.extrude(body, [(-1.5, .5), (-1.5, .8), (-1.35, .93), (-.3, .93), (-.3, 1.05), (1.4, 1.05), (1.4, .5)], 1.4,
              axis='X', chamfer=.05, corner=.04)
    k.inset(body, lambda c, n, f: abs(n.x) > .9 and c.y > -.2, width=.08, depth=.012)
    a.part('Glass', 'Glass').box((1.2, .03, .3), loc=(0, -.3, 1.2), rot=(-.25, 0, 0), bevel=0)
    for s in (-1, 1):
        k.block(steel, (.05, .05, .35), loc=(s * .62, -.3, 1.05), chamfer=0)
        k.block(steel, (.1, .14, .1), loc=(s * .62, -1.1, .98), chamfer=0)
    k.block(steel, (1.44, .05, .06), loc=(0, -.3, 1.38), chamfer=0)
    k.block(steel, (1.5, .12, .14), loc=(0, -1.58, .55), chamfer=.02)
    _lights(a, (-.5, .5), -1.52, .78, size=(.18, .04, .12))
    a.part('Grille', 'Undercarriage').grille(.7, .22, loc=(0, -1.52, .68), slats=2, depth=.04, thickness=.04)
    for s in (-1, 1):
        k.block(a.part('Seats', 'Armor'), (.4, .4, .3), loc=(s * .35, .1, 1.05), chamfer=.04)
    k.lathe(a.part('Spare', 'Undercarriage'), [(0, -.1), (.28, -.1), (.3, -.06), (.3, .06), (.28, .1), (0, .1)],
            loc=(0, 1.4, .85), rot=(R90, 0, 0), seg=10)
    t = a.pivot('Turret', (0, .6, 1.05))
    k.lathe(a.part('Pedestal', 'Steel', t), [(.1, 0), (.1, .35), (.14, .37)], seg=8)
    parts.barrel(a, 'Main_cannon', t, 0, 1.2, .4, 3.0, .075, seg=10, sleeve=1.2, extractor=(.45, 1.35, .4),
                 brake_name='Muzzle_brake', brake='collar')
    a.pivot('Muzzle_main', (0, 1.2 - 3.23, .4), t)
    k.lathe(a.part('Breech', 'Steel', t), [(.12, -.15), (.12, .2), (.08, .26), (.08, .3)], loc=(0, 1.35, .4), rot=FORWARD,
            seg=10)
    a.pivot('Point_exhaust', (.5, 1.4, .5))
    a.pivot('Point_fire', (0, 0, 1.2))
    k.clean(a)


def shorad_vehicle(a):
    """Avenger SHORAD (pn.shorad_vehicle) on the V2 kit: V2 wheels, extruded 4x4 body, a turret with two Stinger pods,
    a sensor box and the roof MG; same nodes."""
    hd.mark(a, False)
    body = a.part('Hull', 'Team')
    steel = a.part('Steel', 'Steel')
    a.part('Chassis', 'Undercarriage').box((1.2, 3.4, .22), loc=(0, 0, .45), bevel=0)
    for s in (-1, 1):
        for y in (-1.2, 1.1):
            parts.road_wheel(a, (s * .76, y, .38), .38, .26, s, seg=8)
    k.extrude(body, [(-1.85, .5), (-1.85, .85), (-1.55, 1.12), (-.35, 1.12), (-.3, 1.45), (1.3, 1.45), (1.3, .5)], 1.8,
              axis='X', chamfer=.05, corner=.04)
    k.inset(body, lambda c, n, f: abs(n.x) > .9 and c.y > -.2, width=.08, depth=.012)
    glass = a.part('Glass', 'Glass')
    glass.box((1.5, .05, .35), loc=(0, -.36, 1.3), bevel=0)
    for s in (-1, 1):
        glass.box((.03, .7, .3), loc=(s * .905, .05, 1.2), bevel=0)
        k.block(a.part('Fenders', 'Armor'), (.3, 1.2, .06), loc=(s * .78, -1.2, .8), chamfer=.02)
    k.block(steel, (1.84, .14, .18), loc=(0, -1.9, .6), chamfer=.03)
    _lights(a, (-.6, .6), -1.87, .78, size=(.2, .04, .1))
    a.part('Grille', 'Undercarriage').grille(.8, .2, loc=(0, -1.87, .66), slats=2, depth=.04, thickness=.04)
    t = a.pivot('Turret', (0, .6, 1.45))
    k.lathe(a.part('Ring', 'Steel', t), [(.5, 0), (.5, .06), (.4, .08)], seg=12)
    k.block(a.part('Turret_body', 'Armor', t), (.7, .7, .6), loc=(0, 0, .3), chamfer=.06, taper=(.92, .92))
    k.block(a.part('Sensor_box', 'Armor', t), (.28, .3, .26), loc=(0, -.45, .5), chamfer=.03)
    a.part('Sensor_lens', 'Glass', t).box((.18, .03, .14), loc=(0, -.62, .5), bevel=0)
    front = None
    for s in (-1, 1):
        front = _launcher_v2(a, t, (s * .6, 0, .45), (.4, .9, .4), (2, 2), math.radians(10), mat='Team')
    a.pivot('Muzzle_missile', (0, front[1], front[2]), t)
    mv._roof_mg(a, None, (.55, -.4, 1.5), length=.6, shield=False)
    a.pivot('Point_exhaust', (.8, 1.2, .8))
    a.pivot('Point_fire', (0, 0, 1.6))
    k.clean(a)


def wheeled_howitzer(a):
    """CAESAR 6x6 truck howitzer (pn.wheeled_howitzer) on the V2 kit: V2 truck, mount block with a cradle, the 155 mm
    barrel as one surface with a baffle brake, the firing spade on arms; same nodes."""
    top = _truck_pn_v2(a, 7.4, 2.1, 1.8, 3, r=.45, bed_h=1.2, armoured=False)
    t = a.pivot('Turret', (0, 2.3, top))
    k.block(a.part('Mount', 'Team', t), (1.6, 1.6, .7), loc=(0, 0, .35), chamfer=.06)
    k.block(a.part('Cradle', 'Armor', t), (.5, 1.2, .3), loc=(0, -.3, .78), chamfer=.04)
    pitch = math.radians(4)
    parts.barrel(a, 'Main_cannon', t, 0, -.4, .9, 5.6, .09, seg=10, sleeve=1.2, extractor=(.38, 1.5, .5),
                 brake_name='Muzzle_brake', brake='baffle', rot=(R90 - pitch, 0, 0))
    d = 5.875
    a.pivot('Muzzle_main', (0, -.4 - d * math.cos(pitch), .9 + d * math.sin(pitch)), t)
    _ybox(a.part('Spade', 'Armor'), (2.0, .2, 1.0), (0, 3.75, .6), rot=(.3, 0, 0), chamfer=.03)
    for s in (-1, 1):
        _ybox(a.part('Spade_arms', 'Steel'), (.14, 1.0, .14), (s * .6, 3.35, .8), rot=(-.25, 0, 0), chamfer=.01)
    k.block(a.part('Ammo_racks', 'Crate'), (.5, 1.0, .5), loc=(.5, 1.0, top + .25), chamfer=.03)
    pn._stripes(a, 1.7, 2.1, 2.0, y=-2.8)
    k.clean(a)


def sp_mortar(a):
    """8x8 twin-barrel mortar vehicle (pn.sp_mortar) on the V2 kit: V2 wheels, extruded hull and turret, two revolved
    120 mm barrels, the roof MG; same nodes."""
    hd.mark(a, False)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    a.part('Chassis', 'Undercarriage').box((1.6, 5.8, .3), loc=(0, 0, .55), bevel=0)
    for s in (-1, 1):
        for y in (-2.3, -1.05, .45, 1.7):
            parts.road_wheel(a, (s * .98, y, .45), .45, .3, s, seg=8)
    k.extrude(hull, [(-3.1, .6), (-3.1, 1.05), (-2.3, 1.75), (3.1, 1.75), (3.1, .6)], 2.3, axis='X', chamfer=.06, corner=.04)
    k.inset(hull, lambda c, n, f: abs(n.x) > .9 and c.z > .9, width=.1, depth=.012)
    for s in (-1, 1):
        for y in (-1.7, .55):
            k.block(armor, (.36, 1.9, .06), loc=(s * .96, y, 1.02), chamfer=.02)
        _lights(a, (s * .8,), -3.12, 1.0, size=(.16, .04, .1))
        _lights(a, (s * .9,), 3.12, 1.0, facing=1, size=(.12, .04, .08), lamp='Alloy')
    a.part('Deck', 'Undercarriage').grille(1.0, .8, loc=(0, 2.4, 1.76), rot=(-R90, 0, 0), slats=4, depth=.05, thickness=.04)
    _hatch(a, .7, -1.9, 1.75, .2, handle=False)
    t = a.pivot('Turret', (0, .5, 1.75))
    steel.cyl(.85, .08, loc=(0, .5, 1.75), seg=14, bevel=0)
    k.extrude(a.part('Turret_body', 'Armor', t), [(-.95, -1.0), (.95, -1.0), (.95, 1.0), (-.95, 1.0)], .7, loc=(0, 0, .35),
              axis='Z', chamfer=.06, corner=.05, taper=.9)
    pitch = math.radians(12)
    for x, suffix in ((-.3, ''), (.3, '_2')):
        parts.barrel(a, f'Main_cannon{suffix}', t, x, -.9, .45, 1.4, .1, seg=10, sleeve=1.2, extractor=(.5, 1.3, .2),
                     brake_name=f'Muzzle_brake{suffix}', brake='collar', rot=(R90 - pitch, 0, 0))
    k.block(a.part('Turret_armor', 'Armor', t), (.9, .3, .4), loc=(0, -.95, .4), chamfer=.04, taper=(.9, .9))
    a.pivot('Muzzle_main', (0, -2.35, .75), t)
    mv._roof_mg(a, t, (.7, .6, .7), length=.6, shield=False)
    a.pivot('Point_exhaust', (1.0, 2.6, 1.4))
    a.pivot('Point_fire', (0, 0, 1.9))
    pn._stripes(a, 3.0, 2.0, 1.75, y=-1.4)
    k.clean(a)


def radar_scout(a):
    """Fennek-style 4x4 scout (pn.radar_scout) on the V2 kit: V2 wheels, extruded wedge hull, a lathed telescopic mast
    with a lens head, the roof MG on a ring; same nodes."""
    hd.mark(a, False)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    a.part('Chassis', 'Undercarriage').box((1.5, 3.6, .25), loc=(0, 0, .55), bevel=0)
    for s in (-1, 1):
        for y in (-1.4, 1.35):
            parts.road_wheel(a, (s * .84, y, .45), .45, .3, s, seg=8)
    k.extrude(hull, [(-2.3, .55), (-2.3, .8), (-1.3, 1.45), (2.2, 1.45), (2.3, 1.2), (2.3, .55)], 2.0, axis='X', chamfer=.06,
              corner=.04)
    k.inset(hull, lambda c, n, f: abs(n.x) > .9 and c.z > .8, width=.08, depth=.012)
    for s in (-1, 1):
        k.block(armor, (.3, 1.2, .06), loc=(s * .85, -1.4, .95), chamfer=.02)
        k.block(armor, (.3, 1.2, .06), loc=(s * .85, 1.35, .95), chamfer=.02)
        _lights(a, (s * .65,), -2.31, .75, size=(.16, .04, .1))
    k.lathe(a.part('Mast', 'Steel'), [(.11, -1.2), (.11, -.5), (.09, -.48), (.09, .2), (.07, .22), (.07, 1.2)],
            loc=(0, .8, 2.65), seg=8)
    k.block(a.part('Sensor_head', 'Armor'), (.5, .4, .45), loc=(0, .8, 4.0), chamfer=.05)
    a.part('Sensor_lens', 'Glass').box((.34, .03, .22), loc=(0, .59, 4.05), bevel=0)
    a.part('Deck', 'Undercarriage').grille(.9, .6, loc=(0, 1.6, 1.46), rot=(-R90, 0, 0), slats=3, depth=.05, thickness=.04)
    t = a.pivot('Turret', (0, -.3, 1.45))
    k.lathe(a.part('Ring', 'Armor', t), [(.35, 0), (.35, .1), (.3, .12)], seg=12, worn=(1,))
    gun = a.part('MG', 'Steel', t)
    k.block(gun, (.14, .4, .16), loc=(0, 0, .3), chamfer=.02)
    k.lathe(gun, [(.04, 0), (.04, .7), (.06, .72), (.06, .8)], loc=(0, -.15, .3), rot=FORWARD, seg=8)
    a.pivot('Muzzle_mg', (0, -.95, .3), t)
    a.pivot('Point_exhaust', (.8, 2.2, 1.0))
    a.pivot('Point_fire', (0, 0, 1.6))
    pn._stripes(a, 2.6, 2.0, 1.45, y=.3)
    k.clean(a)


# ============================================================================= elites on the rebuilt bases
# ----------------------------------------------------------------------------- pass 3h
def armored_car(a):
    """Pandur-class 6x6 armoured car (m25.armored_car) on the V2 kit: V2 wheels, an extruded hull with chamfers and a door
    inset, a revolved round turret, a 25 mm barrel as one surface; same nodes (`Turret`, `Main_cannon`, `Muzzle_brake`,
    `Muzzle_main`, `Muzzle_coax`) and pivots."""
    hd.mark(a, False)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    a.part('Undercarriage', 'Undercarriage').box((1.4, 3.4, .2), loc=(0, 0, .33), bevel=0)
    k.extrude(hull, [(-1.8, .36), (-2.15, .64), (-2.07, .75), (-1.18, 1.0), (1.85, 1.02), (2.15, .82), (2.15, .45),
                     (1.85, .36)], 1.66, axis='X', chamfer=.05, corner=.04)
    k.inset(hull, lambda c, n, f: abs(n.x) > .9 and c.y < .0 and c.y > -1.0 and c.z > .5, width=.07, depth=.012)
    for s in (-1, 1):
        for y in (-1.3, .4, 1.36):
            parts.road_wheel(a, (s * .84, y, .38), .38, .3, s, seg=8)
        k.block(armor, (.36, 1.0, .06), loc=(s * .86, -1.3, .83), chamfer=.015)                      # front arch
        k.block(armor, (.36, 2.0, .06), loc=(s * .86, .88, .83), chamfer=.015)                       # rear arches
        _lights(a, (s * .6,), -2.1, .8, size=(.16, .04, .1))
        _lights(a, (s * .66,), 2.16, .86, facing=1, size=(.12, .04, .08), lamp='Alloy')
        steel.box((.14, .12, .1), loc=(s * .45, -2.17, .5), bevel=0)                                 # tow eyes
    _hatch(a, .42, -1.0, .96, .22, handle=False)
    mv._periscopes(a, [(.42 + dx, -1.28, .92, 0) for dx in (-.14, .14)])
    mv._exhaust(a, -.5, 2.15, .72, .34, .18)
    a.part('Deck', 'Undercarriage').grille(.9, .6, loc=(-.2, 1.45, 1.04), rot=(-R90, 0, 0), slats=4, depth=.05,
                                           thickness=.04)
    k.block(armor, (.5, .7, .06), loc=(.55, 1.5, 1.04), chamfer=.01)
    a.pivot('Point_exhaust', (-.5, 2.2, .72))
    a.pivot('Point_fire', (0, 1.4, 1.04))
    t = a.pivot('Turret', (0, .0, 1.02))
    k.lathe(a.part('Turret_body', 'Team', t), [(0, .01), (.62, .01), (.62, .05), (.52, .32), (0, .33)], seg=12,
            worn=(1, 2))
    tarm = a.part('Turret_armor', 'Armor', t)
    k.block(tarm, (.42, .3, .26), loc=(0, -.58, .18), chamfer=.04, taper=(.85, .9))                  # mantlet
    k.block(tarm, (.3, .26, .16), loc=(-.34, -.1, .39), chamfer=.03)                                  # sight
    a.part('Sight', 'Glass', t).box((.2, .03, .08), loc=(-.34, -.24, .4), bevel=0)
    _hatch(a, .28, .12, .33, .2, parent=t, seg=10, handle=False)
    for s in (-1, 1):
        parts.smoke_launcher(a, a.part('Smoke', 'Steel', t), .5, .2, .27, s, count=3, gap=.07, r=.045, depth=.14)
    y0, length, z = -.62, 1.9, .18
    parts.barrel(a, 'Main_cannon', t, 0, y0, z, length, .06, seg=8, sleeve=1.25, extractor=(.4, 1.5, .3),
                 brake_name='Muzzle_brake', brake='collar')
    a.pivot('Muzzle_main', (0, y0 - length - .14, z), t)
    mv._coax(a, t, .26, -.62, .24, length=.34, housing=.22)
    k.clean(a)


def _mrap_v2(a):
    """m25._mrap on the V2 kit (V2 wheels, an extruded armoured cab with chamfers, insets and a two-pane screen, a V-hull
    belly, a winch bumper, the pintle MG); same parts and geometry. Returns the chassis top height."""
    hd.mark(a, False)
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    dark.box((1.3, 6.9, .3), loc=(0, -.1, .72), bevel=0)
    k.extrude(dark, [(-.95, .86), (.95, .86), (.35, .5), (-.35, .5)], 3.0, loc=(0, -2.4, 0), axis='Y', chamfer=.02)
    for s in (-1, 1):
        for y in (-2.35, 1.1, 2.45):
            parts.road_wheel(a, (s * .8, y, .5), .5, .38, s, seg=8)
        k.block(armor, (.42, 1.2, .06), loc=(s * .8, -2.35, 1.07), chamfer=.015)
        k.block(armor, (.42, 2.6, .06), loc=(s * .8, 1.78, 1.07), chamfer=.015)
        _lights(a, (s * .7,), -3.66, 1.12, size=(.16, .04, .1))
        _lights(a, (s * .75,), 3.48, 1.0, facing=1, size=(.12, .04, .08), lamp='Alloy')
        k.block(armor, (.06, .8, .9), loc=(s * .97, -2.2, 1.55), chamfer=.015)                      # door armour
        a.part('Glass', 'Glass').box((.03, .44, .3), loc=(s * .985, -2.2, 1.95), bevel=0)
        steel.box((.2, .5, .06), loc=(s * .9, -2.2, .98), bevel=0)                                  # steps
    k.extrude(body, [(-3.62, .82), (-3.66, 1.1), (-3.5, 1.5), (-3.1, 2.28), (-1.5, 2.3), (-1.5, .82)], 1.9, axis='X',
              chamfer=.05, corner=.04)
    k.inset(body, lambda c, n, f: abs(n.x) > .9 and c.y < -1.7 and c.y > -3.0 and c.z > 1.0, width=.08, depth=.012)
    glass = a.part('Glass', 'Glass')
    for s in (-1, 1):
        glass.box((.8, .04, .56), loc=(s * .44, -3.32, 1.9), rot=(-.44, 0, 0), bevel=0)
    k.block(steel, (1.9, .16, .2), loc=(0, -3.72, .9), chamfer=.03)                                 # bumper
    k.lathe(armor, [(.1, -.3), (.1, .3)], loc=(0, -3.8, .9), rot=(0, R90, 0), seg=8)                # winch
    k.block(armor, (1.7, .12, .1), loc=(0, -3.18, 2.2), rot=(-.44, 0, 0), chamfer=.01)             # sun visor
    parts.mg_mount(a, None, (.4, -2.35, 2.3), length=.8)
    a.pivot('Point_exhaust', (-.95, -1.6, 2.1))
    return .87


def fpv_carrier(a):
    """FPV drone launcher (m25.fpv_carrier) on the V2 kit: the V2 MRAP, a chamfered rear module with add-on plates, and the
    4 x 5 launch rack with its drones; same nodes (`Turret`, `Launch_cells`, `Muzzle_main`, `Mount_mg`, `Muzzle_mg`)."""
    top = _mrap_v2(a)
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    k.block(body, (1.96, 4.9, 1.46), loc=(0, .98, top + .73), chamfer=.06)                          # rear module
    k.block(armor, (.9, .06, 1.1), loc=(0, 3.44, top + .66), chamfer=.015)                          # rear door
    for s in (-1, 1):
        k.block(armor, (.06, 3.4, .5), loc=(s * .99, .6, top + .95), chamfer=.015)                  # add-on plates
    _hatch(a, -.45, -.6, top + 1.46, .25, handle=False)
    a.pivot('Point_fire', (0, .2, top + 1.5))
    t = a.pivot('Turret', (0, 2.1, top + 1.46))
    k.lathe(a.part('Rack_base', 'Steel', t), [(0, 0), (.5, 0), (.5, .12), (0, .12)], seg=10)
    k.block(a.part('Rack_frame', 'Armor', t), (1.72, 2.1, .36), loc=(0, 0, .3), chamfer=.03)
    cells = a.part('Launch_cells', 'Undercarriage', t)
    drones = a.part('Rack_drones', 'Steel', t)
    for i in range(4):
        for j in range(5):
            x, y = -.63 + i * .42, -.8 + j * .4
            cells.box((.34, .32, .04), loc=(x, y, .49), bevel=0)
            if (i + j) % 3 == 0:
                drones.box((.26, .1, .05), loc=(x, y, .52), rot=(0, 0, .785), bevel=0)
                drones.box((.26, .1, .05), loc=(x, y, .52), rot=(0, 0, -.785), bevel=0)
    a.part('Rack_lights', 'TeamGlow', t).box((1.6, .06, .06), loc=(0, -1.07, .4), bevel=0)
    a.pivot('Muzzle_main', (0, 0, .52), t)
    k.clean(a)


def lancet_truck(a):
    """Lancet launcher (m25.lancet_truck) on the V2 kit: the V2 MRAP, a railed bed with the control station, the folded
    mast, the 2 x 3 canister box on its hinge with two rams; same nodes (`Turret`, `Box_shell`, `Box_face`, `Cells`,
    `Munition_wings`, `Rams`, `Muzzle_main`) and pivots."""
    top = _mrap_v2(a)
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    k.block(a.part('Bed', 'Team'), (1.96, 4.9, .14), loc=(0, .98, top + .07), chamfer=.02)
    for s in (-1, 1):
        k.block(armor, (.08, 4.9, .36), loc=(s * .96, .98, top + .3), chamfer=0)                    # side rails
    k.block(a.part('Body', 'Team'), (1.5, 1.2, 1.2), loc=(0, -.8, top + .74), chamfer=.06)          # control station
    k.block(steel, (.14, 1.6, .14), loc=(.55, .2, top + 1.42), chamfer=.01)                         # folded mast
    a.part('Sensor', 'Glass').sphere(.16, loc=(.55, 1.05, top + 1.42), seg=8, rings=5)
    a.pivot('Point_fire', (0, -.8, top + 1.4))
    t = a.pivot('Turret', (0, 2.2, top + .2))
    k.lathe(a.part('Rack_base', 'Steel', t), [(0, 0), (.45, 0), (.45, .14), (0, .14)], seg=10)
    pitch = .21
    hinge = Vector((0, .9, .36))
    along = Vector((0, -math.cos(pitch), math.sin(pitch)))
    up = Vector((0, math.sin(pitch), math.cos(pitch)))
    rot = (-pitch, 0, 0)
    L, W, H = 2.7, 1.2, .7
    centre = hinge + along * (L / 2) + up * (H / 2)
    k.block(a.part('Box_shell', 'Armor', t), (W, L, H), loc=tuple(centre), rot=rot, chamfer=.04, ends=(True, True))
    front = hinge + along * L + up * (H / 2)
    a.part('Box_face', 'Undercarriage', t).box((W - .1, .04, H - .1), loc=tuple(front + along * .01), rot=rot, bevel=0)
    cells = a.part('Cells', 'Team', t)
    wings = a.part('Munition_wings', 'Fuel', t)
    for i in range(3):
        for j in range(2):
            c = front + along * .03 + Vector((-.38 + i * .38, 0, 0)) + up * (-.16 + j * .32)
            cells.box((.3, .06, .28), loc=tuple(c), rot=rot, bevel=0)
            if (i + j) % 2 == 0:
                wings.box((.26, .04, .04), loc=tuple(c + along * .03), rot=(-pitch, 0, .785), bevel=0)
                wings.box((.26, .04, .04), loc=tuple(c + along * .03), rot=(-pitch, 0, -.785), bevel=0)
    a.part('Stripes', 'Hazard', t).box((W + .02, .12, H + .02), loc=tuple(hinge + along * (L * .7) + up * (H / 2)),
                                       rot=rot, bevel=0)
    rams = a.part('Rams', 'Steel', t)
    for s in (-1, 1):
        rams.limb((s * .5, -.6, .16), tuple(Vector((s * .5, 0, 0)) + hinge + along * 1.5), .1, .1, bevel=0)
    a.pivot('Muzzle_main', tuple(front + along * .08), t)
    k.clean(a)


def command_vehicle(a):
    """Stryker CV / BTR-80 KShM command vehicle (m25.command_vehicle) on the V2 kit: V2 wheels, an extruded 8x8 hull with
    chamfers and a ramp inset, side armour, the antenna ring, the folded mast, a lathed dish and a rolled tent; same nodes
    (`Mount_mg`, `Muzzle_mg`) and pivots."""
    hd.mark(a, False)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    a.part('Undercarriage', 'Undercarriage').box((1.4, 4.8, .2), loc=(0, 0, .42), bevel=0)
    k.extrude(hull, [(-2.4, .42), (-2.78, .62), (-2.72, .95), (-2.05, 1.5), (2.62, 1.55), (2.8, 1.42), (2.8, .5),
                     (2.45, .42)], 1.86, axis='X', chamfer=.05, corner=.04)
    k.inset(hull, lambda c, n, f: abs(n.x) > .9 and c.y > -1.4 and c.y < 1.0 and c.z > .8, width=.08, depth=.012)
    for s in (-1, 1):
        for y in (-1.95, -1.05, .75, 1.65):
            parts.road_wheel(a, (s * .86, y, .42), .42, .32, s, seg=8)
        k.block(armor, (.08, 4.4, .5), loc=(s * .98, .1, 1.1), chamfer=.02)                          # side armour
        _lights(a, (s * .62,), -2.8, .95, size=(.16, .04, .1))
        _lights(a, (s * .7,), 2.81, 1.0, facing=1, size=(.12, .04, .08), lamp='Alloy')
    _hatch(a, -.45, -1.65, 1.5, .22, handle=False)
    mv._periscopes(a, [(-.45 + dx, -1.95, 1.48, 0) for dx in (-.14, .14)])
    k.block(armor, (1.1, .06, 1.0), loc=(0, 2.83, .95), chamfer=.015)                               # rear ramp
    mv._exhaust(a, -.7, 2.8, .7, .3, .18)
    beacons = a.part('Beacons', 'TeamGlow')
    for x, y in ((.8, .2), (-.8, .2), (.8, 1.1), (-.8, 1.1), (.72, 2.1), (-.72, 2.1)):
        k.lathe(steel, [(.08, 0), (.08, .12), (.05, .16), (.05, .52)], loc=(x, y, 1.55), seg=8)       # base and stub
        beacons.box((.1, .1, .08), loc=(x, y, 2.1), bevel=0)
    mast = a.part('Mast', 'Armor')
    for y in (.35, 1.95):
        k.block(mast, (.3, .14, .22), loc=(-.2, y, 1.66), chamfer=.015)                              # cradles
    k.block(steel, (.2, 2.5, .2), loc=(-.2, 1.1, 1.84), chamfer=.02)                                 # folded mast
    k.block(mast, (.4, .34, .3), loc=(-.2, -.3, 1.86), chamfer=.03)                                  # sensor head
    a.part('Sensor', 'Glass').box((.3, .03, .16), loc=(-.2, -.48, 1.88), bevel=0)
    k.lathe(a.part('Dish', 'Medical'), [(0, .04), (.2, .06), (.36, .16), (.33, .15), (.18, .08), (0, .06)],
            loc=(.3, 1.55, 1.64), rot=(.35, 0, 0), seg=12, worn=(2,))
    k.lathe(steel, [(.06, 0), (.06, .14)], loc=(.3, 1.55, 1.58), seg=6)
    k.lathe(a.part('Tent', 'Canvas'), [(0, -.8), (.18, -.8), (.22, -.74), (.22, .74), (.18, .8), (0, .8)],
            loc=(0, 2.45, 1.78), rot=(0, R90, 0), seg=10, worn=(2, 3))
    for x in (-.6, .6):
        k.lathe(a.part('Straps', 'Undercarriage'), [(.2, -.03), (.235, -.03), (.235, .03), (.2, .03)],
                loc=(x, 2.45, 1.78), rot=(0, R90, 0), seg=10)
    parts.mg_mount(a, None, (.5, -1.4, 1.52), length=.75)
    a.pivot('Point_exhaust', (-.7, 2.85, .7))
    a.pivot('Point_fire', (0, .8, 1.6))
    k.clean(a)


def scout_jeep(a, detail=False):
    """Scout jeep (m25.scout_jeep, M151 class) on the V2 kit, drawn at mb_vehicles' size and scaled by JEEP_K like the old
    one: V2 wheels, an extruded hood and tub with chamfers, block seats, a framed windscreen and roll bar, the seated driver
    and gunner (`Turret`), a revolved barrel as `Main_cannon`; the `_hd` twin adds mirrors, roll-bar braces, hood latches,
    steering wheel, tow hooks and mud flaps (the wheels' bolts and the MG are the kit's own detail). Same nodes."""
    import mb_p25_models as p25
    hd.mark(a, detail)
    body = a.part('Body', 'Team')
    steel = a.part('Steel', 'Steel')
    armor = a.part('Armor', 'Armor')
    chassis = a.part('Chassis', 'Undercarriage')
    seats = a.part('Seats', 'Canvas')
    chassis.box((1.45, 3.7, .26), loc=(0, 0, .55), bevel=0)
    for sx in (-1, 1):
        for y in (-1.25, 1.2):
            parts.road_wheel(a, (sx * .86, y, .42), .42, .34, sx, seg=12 if detail else 8)
            k.block(body, (.46, 1.05, .1), loc=(sx * .9, y, .92), chamfer=.03, taper=(1, .8))        # fenders
        k.block(steel, (.14, 1.3, .06), loc=(sx * .9, -.05, .64), chamfer=0)                         # side steps
    k.extrude(body, [(-2.0, .62), (-2.0, .96), (-1.1, 1.12), (-.36, 1.14), (-.36, .62)], 1.7, axis='X', chamfer=.05,
              corner=.04)
    k.block(body, (1.72, 2.3, .52), loc=(0, .8, .88), chamfer=.05)
    k.inset(body, lambda c, n, f: abs(n.x) > .9 and c.y > -.2 and c.z > .8, width=.08, depth=.012)
    chassis.grille(.7, .45, loc=(0, -.78, 1.15), rot=(-R90, 0, 0), slats=4, depth=.06, thickness=.04)   # louvres
    for x, y in ((-.38, -.05), (.38, -.05), (-.48, 1.0), (.48, 1.0)):
        k.block(seats, (.44, .44, .12), loc=(x, y, 1.19), chamfer=.03)
        k.block(seats, (.44, .1, .4), loc=(x, y + .25, 1.4), rot=(-.12, 0, 0), chamfer=.015)
    for x0, x1, y, h in ((-.82, .82, -.36, .54), (-.82, .82, 1.55, .66)):
        for x in (x0, x1):
            steel.box((.1, .1, h), loc=(x, y, 1.12 + h / 2), bevel=0)
        k.block(steel, (x1 - x0 + .1, .1, .1), loc=(0, y, 1.12 + h), chamfer=.01)
    a.part('Glass', 'Glass').box((1.54, .03, .42), loc=(0, -.38, 1.39), rot=(-.12, 0, 0), bevel=0)
    for sx in (-1, 1):
        _lights(a, (sx * .55,), -2.0, .8, size=(.16, .04, .12))
        _lights(a, (sx * .72,), 1.96, .72, facing=1, size=(.12, .04, .08), lamp='Alloy')
        k.block(a.part('Jerrycans', 'Hazard'), (.3, .16, .4), loc=(sx * .58, 2.0, 1.05), chamfer=.03)
    chassis.grille(.64, .26, loc=(0, -2.03, .8), slats=3, depth=.05, thickness=.05)
    k.block(steel, (1.5, .12, .14), loc=(0, -2.05, .6), chamfer=.03)                                 # bumper
    k.lathe(a.part('Spare', 'Undercarriage'), [(0, -.11), (.34, -.11), (.36, -.07), (.36, .07), (.34, .11), (0, .11)],
            loc=(0, 2.03, 1.02), rot=FORWARD, seg=12 if detail else 10, worn=(2,))
    k.lathe(armor, [(0, -.12), (.2, -.12), (.2, .12), (0, .12)], loc=(0, 2.03, 1.02), rot=FORWARD, seg=8)
    k.block(armor, (.4, .34, .3), loc=(.55, 1.65, 1.26), chamfer=.02)                                # radio
    k.block(a.part('Ammo_boxes', 'Crate'), (.4, .3, .24), loc=(-.52, 1.65, 1.23), chamfer=.02)
    a.part('Beacon', 'TeamGlow').box((.1, .1, .08), loc=(.72, 1.75, 1.45), bevel=0)
    p25._crew(a, (-.38, -.02, 1.18))                                                                 # the driver
    t = a.pivot('Turret', (0, .72, 1.14))
    k.lathe(a.part('Mount', 'Steel', t), [(.08, 0), (.08, .5), (.12, .52)], seg=8)
    k.block(a.part('Gun_shield', 'Armor', t), (.66, .08, .42), loc=(0, -.22, .66), chamfer=.02, taper=(.9, 1))
    cannon = a.part('Main_cannon', 'Steel', t)
    k.block(cannon, (.16, .44, .18), loc=(0, 0, .64), chamfer=.02)
    y0, length, z = -.2, .96, .66
    parts.barrel(a, 'Main_cannon', t, 0, y0, z, length, .06, seg=10 if detail else 8, sleeve=1.1, extractor=(.45, 1.3, .2))
    k.block(a.part('Ammo_box', 'Armor', t), (.2, .18, .16), loc=(.18, .05, .56), chamfer=.02)
    a.pivot('Muzzle_main', (0, y0 - length, z), t)
    p25._crew(a, (0, .55, .5), parent='Turret', gunner=True)                                         # the gunner
    a.pivot('Point_exhaust', (.6, 2.0, .55))
    a.pivot('Point_fire', (0, -1.2, 1.15))
    if detail:
        for sx in (-1, 1):
            k.block(armor, (.04, .13, .17), loc=(sx * 1.0, -.43, 1.33), chamfer=.01)                 # mirrors
            steel.limb((sx * .82, -.36, 1.3), (sx * .98, -.42, 1.3), .035, .035, bevel=0)
            steel.limb((sx * .82, 1.55, 1.74), (sx * .82, 1.9, 1.14), .05, .05, bevel=0)             # roll-bar braces
            steel.box((.04, .1, .06), loc=(sx * .86, -1.55, 1.0), bevel=0)                            # hood latches
            steel.box((.1, .14, .1), loc=(sx * .5, -2.14, .6), bevel=0)                               # tow hooks
            a.part('Mud_flaps', 'Undercarriage').box((.34, .03, .26), loc=(sx * .86, -.78, .75), bevel=0)
        chassis.cyl(.16, .03, loc=(-.38, -.18, 1.42), rot=(-.9, 0, 0), seg=10, bevel=0)             # steering wheel
        det = a.part('Jeep_bolts', 'Steel')
        for sx in (-1, 1):
            hd.bolt_line(det, (sx * .9, -1.05, .98), (sx * .9, .4, .98), 6, rot=hd.side_rot(sx), r=.014, h=.02)
    p25._scale_asset(a, p25.JEEP_K)
    k.clean(a)


# ----------------------------------------------------------------------------- grad_truck (BM-21 Grad)
def grad_truck(a):
    """BM-21 Grad on an Ural-375D 6x6 (mb_artillery.grad_truck) on the V2 kit: V2 wheels, an extruded hood, fenders and
    cab with chamfers, chamfered blocks, the rocket pack's tubes as the old 40 six-sided bores (the triangle budget: this
    model may not grow); same nodes (`Turret`, `Muzzle_main`, `Mount_mg`, `Muzzle_mg`) and pivots."""
    from mb_vehicles3 import _jack
    hd.mark(a, False)
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    glass = a.part('Windows', 'Glass')
    axles = (-2.75, 1.15, 2.55)
    for y in axles:
        for s in (-1, 1):
            parts.road_wheel(a, (s * 1.0, y, .54), .54, .4, s, seg=10)
    for s in (-1, 1):
        dark.box((.18, 7.1, .26), loc=(s * .42, -.05, .86), bevel=0)                            # frame rails
    for y in axles:
        dark.box((1.56, .2, .16), loc=(0, y, .54), bevel=0)                                      # axle beams
    for y in (1.15, 2.55):
        dark.box((.3, .38, .3), loc=(0, y, .74), bevel=0)                                        # differentials
    k.block(steel, (2.3, .18, .2), loc=(0, -3.62, .8), chamfer=.03)                              # bumper
    for s in (-1, 1):
        steel.box((.14, .16, .14), loc=(s * .55, -3.74, .8), bevel=0)                            # tow hooks
    k.lathe(dark, [(.09, -.25), (.09, .25)], loc=(0, -3.52, .96), rot=(0, R90, 0), seg=8)        # winch drum
    k.extrude(body, [(-3.5, .95), (-3.52, 1.62), (-3.3, 1.74), (-2.05, 1.8), (-2.05, .95)], 1.12, axis='X',
              chamfer=.04, corner=.03)                                                           # hood
    for x in (-.3, 0, .3):
        dark.box((.07, .04, .5), loc=(x, -3.525, 1.28), bevel=0)                                 # grille slots
    for x in (-.45, -.15, .15, .45):
        dark.box((.05, .04, .5), loc=(x, -3.525, 1.28), bevel=0)
    for s in (-1, 1):
        steel.box((.05, .5, .04), loc=(s * .45, -2.75, 1.79), bevel=0)                           # hood latches
        dark.grille(.7, .26, loc=(s * .565, -2.7, 1.5), rot=(0, 0, s * R90), slats=3, depth=.04, thickness=.03)
    for s in (-1, 1):
        x = s * .9
        k.extrude(body, [(-3.5, 1.04), (-3.46, 1.26), (-3.25, 1.4), (-2.05, 1.42), (-2.05, 1.22), (-3.2, 1.2)], .66,
                  loc=(x, 0, 0), axis='X', chamfer=.03, corner=.03)                              # front fenders
        k.block(armor, (.6, .06, .5), loc=(x, -2.08, 1.0), chamfer=.01)                          # fender back
        _lights(a, (s * .78,), -3.5, 1.2, size=(.2, .04, .14))
        a.part('Marker_lights', 'Alloy').box((.1, .1, .07), loc=(s * 1.1, -3.1, 1.44), bevel=0)
    k.extrude(body, [(-2.06, 1.2), (-2.06, 1.82), (-1.96, 2.44), (-.8, 2.44), (-.8, 1.2)], 2.3, axis='X', chamfer=.05,
              corner=.04)                                                                        # cab
    k.inset(body, lambda c, n, f: abs(n.x) > .9 and c.y < -1.0 and c.y > -1.95 and c.z > 1.5, width=.07, depth=.012)
    for s in (-1, 1):
        glass.box((.98, .04, .5), loc=(s * .54, -2.02, 2.12), rot=(-.16, 0, 0), bevel=0)
        glass.box((.04, .56, .4), loc=(s * 1.155, -1.62, 2.1), bevel=0)
        steel.box((.04, .16, .05), loc=(s * 1.165, -1.3, 1.9), bevel=0)                          # handles
        steel.box((.3, .24, .04), loc=(s * 1.08, -1.55, .98), bevel=0)                           # steps
        steel.tube([(s * 1.14, -1.95, 2.3), (s * 1.22, -2.1, 2.34)], .016, seg=4)                # mirrors
        k.block(armor, (.05, .16, .26), loc=(s * 1.25, -2.14, 2.26), chamfer=.01)
        k.lathe(steel, [(0, -.45), (.24, -.45), (.24, .45), (0, .45)], loc=(s * .8, -1.45, .78), rot=FORWARD, seg=10,
                worn=(1, 2))                                                                     # fuel tanks
        for y in (-1.75, -1.15):
            dark.box((.52, .04, .52), loc=(s * .8, y, .78), bevel=0)
    armor.box((.08, .04, .5), loc=(0, -2.035, 2.12), rot=(-.16, 0, 0), bevel=0)                  # centre pillar
    k.block(armor, (2.2, .12, .06), loc=(0, -2.02, 2.47), rot=(-1.2, 0, 0), chamfer=.01)         # folded shutters
    for s in (-1, 1):
        k.block(armor, (1.02, .5, .05), loc=(s * .54, -1.8, 2.49), chamfer=.012)
    k.block(a.part('Canvas_top', 'Canvas'), (2.2, .9, .12), loc=(0, -1.12, 2.48), chamfer=.04, taper=(.97, .95))
    steel.box((2.26, .05, .05), loc=(0, -.85, 2.46), bevel=0)                                    # top bow
    k.block(armor, (1.9, .08, .66), loc=(0, -.73, 2.02), chamfer=.015)                           # blast shield
    for s in (-1, 1):
        steel.box((.06, .1, .06), loc=(s * .8, -.76, 2.3), bevel=0)                              # shield brackets
        steel.box((.06, .1, .06), loc=(s * .8, -.76, 1.75), bevel=0)
    k.lathe(armor, [(0, 0), (.3, 0), (.3, .08), (.24, .1), (0, .1)], loc=(.5, -1.6, 2.5), seg=12, worn=(1,))   # MG ring
    parts.mg_mount(a, None, (.5, -1.6, 2.58), length=.8)
    k.lathe(steel, [(.03, 0), (.03, 1.3)], loc=(-1.05, -.9, 2.44), seg=4)                       # antenna
    # Behind the cab: spare wheel, air cleaner and battery box.
    k.lathe(a.part('Tyres', 'Undercarriage'), [(.3, -.17), (.5, -.15), (.5, .15), (.3, .17)], loc=(-.72, -.35, 1.12),
            rot=(0, R90, 0), seg=12, worn=(2,))
    k.lathe(a.part('Hubs', 'Steel'), [(0, -.19), (.26, -.19), (.26, .19), (0, .19)], loc=(-.72, -.35, 1.12),
            rot=(0, R90, 0), seg=10)
    steel.box((.08, .3, .7), loc=(-.5, -.35, .98), bevel=0)                                      # spare carrier
    k.lathe(armor, [(0, -.3), (.18, -.3), (.18, .3), (0, .3)], loc=(.75, -.45, 1.28), seg=10)    # air cleaner
    k.block(armor, (.46, .5, .4), loc=(.78, -.35, .78), chamfer=.02)                             # battery box
    # Bed, tool lockers, mudguards, rear lights, jacks.
    k.block(body, (2.2, 4.3, .14), loc=(0, 1.55, 1.2), chamfer=.03)
    for s in (-1, 1):
        armor.box((.06, 4.3, .08), loc=(s * 1.1, 1.55, 1.28), bevel=0)
        k.block(armor, (.5, 2.5, .06), loc=(s * 1.0, 1.85, 1.3), chamfer=.015)                   # mudguards
        k.block(armor, (.5, .06, .44), loc=(s * 1.0, .6, 1.08), chamfer=.01)
        a.part('Mud_flaps', 'Undercarriage').box((.44, .04, .4), loc=(s * 1.0, 3.2, .72), bevel=0)
        _lights(a, (s * .95,), 3.64, 1.1, facing=1, size=(.12, .04, .08), lamp='Alloy')
        _jack(a, s * .85, 3.35, 1.2, pad=.16)
    k.block(armor, (.36, .9, .4), loc=(.98, .2, .82), chamfer=.03)                               # tool locker
    steel.box((.03, .06, .08), loc=(1.165, .2, .9), bevel=0)
    k.block(steel, (2.2, .16, .18), loc=(0, 3.6, .86), chamfer=.03)                              # rear bumper
    steel.box((.14, .14, 1.0), loc=(0, -.2, 1.44), bevel=0)                                      # travel rest
    for s in (-1, 1):
        steel.limb((s * .36, -.2, 1.26), (s * .06, -.2, 1.7), .07, .07, bevel=0)                 # braces
    k.block(armor, (.9, .16, .1), loc=(0, -.2, 1.9), chamfer=.015)                               # rest beam
    a.part('Rest_pad', 'Undercarriage').box((.6, .14, .05), loc=(0, -.2, 1.965), bevel=0)

    # Launcher: turntable, base, brackets and the 40-tube pack on its rear hinge.
    t = a.pivot('Turret', (0, 2.25, 1.27))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    k.lathe(tsteel, [(0, 0), (.82, 0), (.82, .1), (0, .1)], loc=(0, 0, -.02), seg=16, worn=(1, 2))   # turntable
    k.block(tarm, (1.4, 1.3, .32), loc=(0, .05, .22), chamfer=.04, taper=(.94, .94))             # base
    L, cols, rows, pitch_x, pitch_z, r = 3.0, 10, 4, .16, .158, .066
    W, H = cols * pitch_x, rows * pitch_z
    hinge = Vector((0, .22, .84))
    centre = hinge + Vector((0, -L / 2 + .06, H / 2 + .04))
    for s in (-1, 1):
        k.extrude(tarm, [(-.5, .06), (.5, .06), (.36, .74), (.3, .96), (.1, .96), (-.3, .6)], .1,
                  loc=(s * (W / 2 + .12), 0, 0), axis='X', chamfer=.015, corner=.02)             # brackets
        tsteel.cyl(.1, .06, loc=(s * (W / 2 + .19), hinge.y, hinge.z), rot=ACROSS, seg=8, bevel=0)  # hinge caps
        tsteel.limb((s * .45, -.55, .36), (s * .45, -.78, .76), .1, .1, bevel=0)                 # elevation screws
    tsteel.cyl(.06, W + .4, loc=hinge, rot=ACROSS, seg=6, bevel=0)                               # hinge axle
    k.block(tarm, (.22, .3, .34), loc=(-.62, -.45, .55), chamfer=.02)                            # laying sight
    a.part('Sight', 'Glass', t).box((.16, .03, .1), loc=(-.62, -.61, .6), bevel=0)
    tubes = a.part('Rocket_tubes', 'Team', t)
    front = centre.y - L / 2
    for i in range(cols):
        for j in range(rows):
            x = (i - (cols - 1) / 2) * pitch_x
            z = centre.z + (j - (rows - 1) / 2) * pitch_z
            k.lathe(tubes, [(r, 0), (r, L), (r * .76, L), (r * .76, L - .14)], loc=(x, front + L, z), rot=FORWARD,
                    seg=6)
    a.part('Rocket_tubes_face', 'Undercarriage', t).box((W - .02, .02, H - .02), loc=(0, front + .07, centre.z),
                                                       bevel=0)
    frame = a.part('Rocket_tubes_frame', 'Armor', t)
    for y in (front + .22, centre.y + .05, front + L - .2):                                      # frames
        k.block(frame, (W + .1, .1, H + .1), loc=(0, y, centre.z), chamfer=.015)
    for s in (-1, 1):
        frame.box((.05, L - .5, .1), loc=(s * (W / 2 + .06), centre.y + .05, centre.z), bevel=0)  # side bars
    k.block(frame, (.5, L - .4, .12), loc=(0, centre.y + .05, centre.z - H / 2 - .08), chamfer=.02)   # spine
    frame.box((.14, .22, .16), loc=(0, hinge.y - .06, hinge.z + .04), bevel=0)                   # hinge lug
    a.part('Rocket_tubes_cables', 'Undercarriage', t).box((.12, L - .6, .06),
                                                          loc=(W / 2 - .3, centre.y + .1, centre.z + H / 2 + .05),
                                                          bevel=0)
    a.pivot('Muzzle_main', (0, front - .01, centre.z), t)
    k.clean(a)


def _mbt_v2(a):
    exp.main_battle_tank(a)


def _opts(name):
    import mb_p25_models as p25
    if name in ('flame_tank', 'twin_tank', 'armored_car', 'command_vehicle', 'fpv_carrier', 'lancet_truck',
                'scout_jeep'):
        return p25.BUILDERS[name][1]
    if name in ('sea_corvette', 'missile_boat', 'landing_craft'):
        import mb_naval
        return mb_naval.BUILDERS[name][1]
    if name == 'grad_truck':
        import mb_artillery
        return mb_artillery.BUILDERS[name][1]
    if name in pn.BUILDERS:
        return pn.BUILDERS[name][1]
    return m2.BUILDERS[name][1]


BUILDERS = {
    'heavy_tank': (heavy_tank, _opts('heavy_tank')),
    'light_tank': (light_tank, _opts('light_tank')),
    'tank_destroyer': (tank_destroyer, _opts('tank_destroyer')),
    'titan_tank': (titan_tank, _opts('titan_tank')),
    'turtle_tank': (turtle_tank, _opts('turtle_tank')),
    'laser_tank': (laser_tank, _opts('laser_tank')),
    'flame_tank': (flame_tank, _opts('flame_tank')),
    'twin_tank': (twin_tank, _opts('twin_tank')),
    'bmpt': (bmpt, _opts('bmpt')),
    'ifv': (ifv, _opts('ifv')),
    'elite_apc': (m2._elite_on(ifv, roof=(-.1, -.3, .6), bands=(('', (0, -2.3, .3), .08),)), _opts('elite_apc')),
    'armored_bulldozer': (armored_bulldozer, _opts('armored_bulldozer')),
    'engineer_vehicle': (engineer_vehicle, _opts('engineer_vehicle')),
    'aa_vehicle': (aa_vehicle, _opts('aa_vehicle')),
    'aa_vehicle_hd': (functools.partial(aa_vehicle, detail=True), _opts('aa_vehicle')),
    'artillery': (artillery, _opts('artillery')),
    'artillery_hd': (functools.partial(artillery, detail=True), _opts('artillery')),
    'heavy_aa': (heavy_aa, _opts('heavy_aa')),
    'elite_aa': (m2._elite_on(aa_vehicle, roof=(0, -.45, .8), bands=(('', (-1.22, -3.0, .55), .095),
                                                                      ('_2', (1.22, -3.0, .55), .095))),
                 _opts('elite_aa')),
    'mortar_carrier': (mortar_carrier, _opts('mortar_carrier')),
    'mine_layer': (mine_layer, _opts('mine_layer')),
    'smoke_carrier': (smoke_carrier, _opts('smoke_carrier')),
    'shield_carrier': (shield_carrier, _opts('shield_carrier')),
    'elite_mbt': (m2._elite_on(_mbt_v2, roof=(.12, -.78, .72), bands=(('', (0, -4.56, .38), .124),), kit=False),
                  _opts('elite_mbt')),
    'elite_heavy_tank': (m2._elite_on(heavy_tank, roof=(.1, -.6, .56), bands=(('', (0, -4.78, .32), .16),), kit=False),
                         _opts('elite_heavy_tank')),
    'elite_tank_destroyer': (m2._elite_on(tank_destroyer, roof=(.1, -.45, .5), bands=(('', (0, -4.4, .27), .11),),
                                          kit=False), _opts('elite_tank_destroyer')),
    'mlrs': (mlrs, _opts('mlrs')),
    'elite_mlrs': (m2._elite_on(mlrs, cab=(-.2, -2.2, 2.0)), _opts('elite_mlrs')),
    'heavy_rocket_artillery': (heavy_rocket_artillery, _opts('heavy_rocket_artillery')),
    'thermobaric_launcher': (thermobaric_launcher, _opts('thermobaric_launcher')),
    'ballistic_launcher': (ballistic_launcher, _opts('ballistic_launcher')),
    'long_sam': (long_sam, _opts('long_sam')),
    'sam_launcher': (sam_launcher, _opts('sam_launcher')),
    'iron_beam': (iron_beam, _opts('iron_beam')),
    'supply_truck': (supply_truck, _opts('supply_truck')),
    'ammo_carrier': (ammo_carrier, _opts('ammo_carrier')),
    'counter_battery_radar': (counter_battery_radar, _opts('counter_battery_radar')),
    'ew_jammer': (ew_jammer, _opts('ew_jammer')),
    'railgun_truck': (railgun_truck, _opts('railgun_truck')),
    'shahed_truck': (shahed_truck, _opts('shahed_truck')),
    'vbied': (vbied, _opts('vbied')),
    'bunker_vehicle': (bunker_vehicle, _opts('bunker_vehicle')),
    'wheeled_gun': (wheeled_gun, _opts('wheeled_gun')),
    'zu23_technical': (zu23_technical, _opts('zu23_technical')),
    'rocket_technical': (rocket_technical, _opts('rocket_technical')),
    'hover_gunboat': (hover_gunboat, _opts('hover_gunboat')),
    'aa_gun_vehicle': (aa_gun_vehicle, dict(_opts('aa_gun_vehicle'), ao_strength=.55)),
    'airborne_vehicle': (airborne_vehicle, _opts('airborne_vehicle')),
    'fibre_fpv_carrier': (fibre_fpv_carrier, _opts('fibre_fpv_carrier')),
    'interceptor_drone_vehicle': (interceptor_drone_vehicle, _opts('interceptor_drone_vehicle')),
    'microwave_vehicle': (microwave_vehicle, dict(_opts('microwave_vehicle'), ao_strength=.65)),
    'nlos_atgm_vehicle': (nlos_atgm_vehicle, dict(_opts('nlos_atgm_vehicle'), ao_strength=.35)),
    'radar_atgm_vehicle': (radar_atgm_vehicle, dict(_opts('radar_atgm_vehicle'), ao_strength=.35)),
    'radar_scout': (radar_scout, dict(_opts('radar_scout'), ao_strength=.65)),
    'recoilless_jeep': (recoilless_jeep, dict(_opts('recoilless_jeep'), ao_strength=.65)),
    'shorad_vehicle': (shorad_vehicle, dict(_opts('shorad_vehicle'), ao_strength=.65)),
    'sp_mortar': (sp_mortar, dict(_opts('sp_mortar'), ao_strength=.65)),
    'wheeled_howitzer': (wheeled_howitzer, dict(_opts('wheeled_howitzer'), ao_strength=.65)),
    'armored_car': (armored_car, dict(_opts('armored_car'), ao_strength=.65)),
    'command_vehicle': (command_vehicle, dict(_opts('command_vehicle'), ao_strength=.65)),
    'fpv_carrier': (fpv_carrier, dict(_opts('fpv_carrier'), ao_strength=.65)),
    'lancet_truck': (lancet_truck, dict(_opts('lancet_truck'), ao_strength=.65)),
    'scout_jeep': (scout_jeep, dict(_opts('scout_jeep'), ao_strength=.65)),
    'scout_jeep_hd': (functools.partial(scout_jeep, detail=True), dict(_opts('scout_jeep'), ao_strength=.65)),
    'grad_truck': (grad_truck, dict(_opts('grad_truck'), ao_strength=.65)),
}
