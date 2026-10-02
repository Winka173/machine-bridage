"""Prompt 27 wave 3 (DECISIONS "27 wave 3a ..."): ground vehicles rebuilt on the V2 kit (mb_kit27 + mb_parts27), merged
last in build_assets.all_builders() so these builders win. Same models as before: every runtime node name, pivot,
material, proportion and `_hd` twin kept (see Docs/models/WAVE3_PLAN.md).

Pass 3b: laser_tank, flame_tank, twin_tank, bmpt, ifv, elite_apc (on the new ifv), armored_bulldozer, engineer_vehicle.

Pass 3a (tanks): heavy_tank (+hd), light_tank (+hd), tank_destroyer (+hd), titan_tank, turtle_tank, and the three elites
on their rebuilt bases (elite_heavy_tank, elite_mbt on the V2 main_battle_tank, elite_tank_destroyer).
"""
import math
import random

from mathutils import Vector

import mb_detail as hd
import mb_kit27 as k
import mb_p25_models2 as m2
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


# ============================================================================= elites on the rebuilt bases
def _mbt_v2(a):
    exp.main_battle_tank(a)


def _opts(name):
    if name in ('flame_tank', 'twin_tank'):
        import mb_p25_models as p25
        return p25.BUILDERS[name][1]
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
    'elite_mbt': (m2._elite_on(_mbt_v2, roof=(.12, -.78, .72), bands=(('', (0, -4.56, .38), .124),), kit=False),
                  _opts('elite_mbt')),
    'elite_heavy_tank': (m2._elite_on(heavy_tank, roof=(.1, -.6, .56), bands=(('', (0, -4.78, .32), .16),), kit=False),
                         _opts('elite_heavy_tank')),
    'elite_tank_destroyer': (m2._elite_on(tank_destroyer, roof=(.1, -.45, .5), bands=(('', (0, -4.4, .27), .11),),
                                          kit=False), _opts('elite_tank_destroyer')),
}
