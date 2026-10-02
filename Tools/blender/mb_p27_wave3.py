"""Prompt 27 wave 3 (DECISIONS "27 wave 3a ..."): ground vehicles rebuilt on the V2 kit (mb_kit27 + mb_parts27), merged
last in build_assets.all_builders() so these builders win. Same models as before: every runtime node name, pivot,
material, proportion and `_hd` twin kept (see Docs/models/WAVE3_PLAN.md).

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


# ============================================================================= elites on the rebuilt bases
def _mbt_v2(a):
    exp.main_battle_tank(a)


def _opts(name):
    return m2.BUILDERS[name][1]


BUILDERS = {
    'heavy_tank': (heavy_tank, _opts('heavy_tank')),
    'light_tank': (light_tank, _opts('light_tank')),
    'tank_destroyer': (tank_destroyer, _opts('tank_destroyer')),
    'titan_tank': (titan_tank, _opts('titan_tank')),
    'turtle_tank': (turtle_tank, _opts('turtle_tank')),
    'elite_mbt': (m2._elite_on(_mbt_v2, roof=(.12, -.78, .72), bands=(('', (0, -4.56, .38), .124),), kit=False),
                  _opts('elite_mbt')),
    'elite_heavy_tank': (m2._elite_on(heavy_tank, roof=(.1, -.6, .56), bands=(('', (0, -4.78, .32), .16),), kit=False),
                         _opts('elite_heavy_tank')),
    'elite_tank_destroyer': (m2._elite_on(tank_destroyer, roof=(.1, -.45, .5), bands=(('', (0, -4.4, .27), .11),),
                                          kit=False), _opts('elite_tank_destroyer')),
}
