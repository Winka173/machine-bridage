"""Prompt 27 wave 1a (DECISIONS "27 wave 1a"): the prompt 26 pass 2 stand-ins built as real models on the V2 kit
(mb_kit27 primitives + mb_parts27 parts), merged last in build_assets.all_builders() so these builders win.

  * ixion: Ixion, the armoured BelAZ-75710-class mine truck (prompt 26 D1): 26 x 12 x 10 m (its def's modelSize, so
    the view's fit is 1:1). A Team armoured box body on the frame, its canopy over a left-offset mine-yellow cab, a
    welded T-72-class turret (125 mm) on the body roof, six big tyres on three axles (one front, two rear), a V ram
    across the front, the BelAZ upper deck with its diagonal stair, the mine dispenser under the tail. Nodes for every
    boss part (balance.json `ixion.parts`): `Part_wheel` / `Part_wheel.001` (front tyres left, right), `Part_tyre`,
    `.001`, `.002`, `.003` (the rear tyres l1, r1, l2, r2, part kind `reartyre`), `Turret` (part `gun`, kind `hulltower`: the turret with its
    `Main_cannon`, `Muzzle_brake`, `Muzzle_main`), `Part_cab` (the cab, holding the roof MGs `Mount_mg` / `Mount_mg.001`
    with `Muzzle_mg` / `Muzzle_mg.001`: mountWeapons 1 and 2). `Point_mines` marks the dispenser mouth for a later
    mine-strip view (not used by game code yet), `Point_exhaust` / `Point_fire` as every truck.
  * rail_supergun (Gungnir) rebuilt in place (prompt 26 D2): the US Navy EMRG scaled up on its railway carriage, the
    BZhRK-style train round it. Same lower carriage, bed, bounds, pivots and part nodes as mb_p16_arms.rail_supergun
    (Part_main, Turret, Part_gun / .001, Part_mg / .001, Part_generator, Part_crane, every Main_cannon* name,
    Muzzle_brake, Muzzle_main at the same point), the Gustav-style upper carriage replaced: chamfered mount walls with
    pulse-forming-network cabinets and power conduits, a square-section rail launcher (tapering box barrel, clamp
    bands, busbars on standoffs where the truss was, a square muzzle shroud and bore), sabot slugs on the trolley. Two
    capacitor cars stand coupled ahead of the carriage under the barrel, one per track, cabled to its deck;
    Part_generator carries a fire-control radar panel.
  * rail_tractor rebuilt in place: a modern Bo-Bo diesel shunter (TEM7 / BZhRK DM62 lineage) on two bogies, same
    11.35 x 3.05 x 5.53 m and the same buffers, so Gungnir's attach points stay.

Conventions are frontier_kit's: metres, +Z up, Blender -Y is the front, +X the vehicle's left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_parts27 as parts
from mb_bosses import _plate_bolts, _railing
from mb_phase2 import _suffixed
from mb_phase8 import (RAIL_TOP, SG_BOGIES, SG_DECK, SG_END, SG_TRACKS, _genset, _headstock, _rail_bogie,
                       _track_bed, autocannon, ciws, pv)
from mb_themes import ladder
from mb_vehicles import ACROSS, FORWARD, R90
from mb_vehicles2 import _axis

TAU = math.tau
SQ = [(-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5)]


def _sq(w, h=None):
    h = w if h is None else h
    return [(x * w, y * h) for x, y in SQ]


# ============================================================================= Ixion
IX_R, IX_W, IX_X = 2.45, 1.9, 5.0           # tyre radius, width, centre |x|
# Part nodes (ModelLibrary.PartPattern: Part_<letters>[.NNN]; '__' becomes '.' on finish): front tyres left, right;
# rear tyres left 1, right 1, left 2, right 2 (parts wheel_l, wheel_r, rear_l1, rear_r1, rear_l2, rear_r2).
IX_TYRES = (('Part_wheel', 1, -8.5), ('Part_wheel__001', -1, -8.5),
            ('Part_tyre', 1, 3.0), ('Part_tyre__001', -1, 3.0),
            ('Part_tyre__002', 1, 9.0), ('Part_tyre__003', -1, 9.0))
IX_DECK = 5.75                               # top of the BelAZ upper deck
IX_ROOF = 8.4                                # body and canopy roof
IX_TURRET = (0.0, 1.5, 8.7)                  # turret ring centre (part `gun` at the sim's (0, -1.5, 6.5))
IX_CAB = (3.7, -9.6, IX_DECK)                # cab base centre, left of the hood (part `cab` at (-3.6, 9.5, 5))


def _ix_tyre(a, name, s, y, i):
    """One mining tyre on its own Part_* node at its centre: a revolved casing with rounded shoulders, chevron tread
    lugs, a mine-yellow dished rim with a hub and wheel nuts on the outer face (side s)."""
    p = a.pivot(name, (s * IX_X, y, IX_R))
    rot = parts.side_rot(s)
    R, h = IX_R - .12, IX_W / 2         # the casing; the lugs stand 0.12 m proud, to the ground at z 0
    tyre = a.part(f'Tyre_{i}', 'Rubber', p)
    k.lathe(tyre, [(1.52, -h + .04), (R - .3, -h), (R - .07, -h + .14), (R, -h + .45), (R, h - .45),
                   (R - .07, h - .14), (R - .3, h), (1.52, h - .04)], rot=rot, seg=24, worn=(3, 4))
    n = 22
    for i in range(n):
        for side in (-1, 1):
            th = (i + (.5 if side > 0 else 0)) * TAU / n
            q = R + .04
            tyre.box((.78, .46, .16), loc=(s * side * .36, q * math.sin(th), q * math.cos(th)),
                     rot=(-th, 0, s * side * .32), bevel=0)
    rim = a.part(f'Rim_{i}', 'Hazard', p)
    m = h - .04
    k.lathe(rim, [(1.56, m - .05), (1.56, m + .03), (1.42, m + .05), (1.3, m - .12), (.62, m - .14), (.56, m + .06),
                  (.3, m + .1), (0, m + .1)], rot=rot, seg=20, worn=(1, 5))
    nuts = [(s * (m - .1), .44 * math.cos(u), .44 * math.sin(u)) for u in (j * TAU / 8 for j in range(8))]
    rim.bolts(nuts, r=.07, h=.09, rot=rot, seg=6, bevel=0)


def _ix_mg(a, parent, loc, tag, sc=2.0):
    """A 12.7 mm roof machine gun on its own `Mount_mg<tag>` yaw pivot, mb_parts27.mg_mount scaled `sc` times for a
    26 m boss (the library's is sized for a tank roof): pintle, receiver, barrel with its flash hider, ammunition box,
    a small shield. `Muzzle_mg<tag>` at the barrel's tip."""
    mount = a.pivot(f'Mount_mg{tag}', loc, parent)
    mg = a.part(f'MG{tag}', 'Steel', mount)
    k.lathe(mg, [(.075 * sc, 0), (.075 * sc, .03 * sc), (.05 * sc, .05 * sc), (.045 * sc, .14 * sc)], seg=8, worn=(1,))
    k.extrude(mg, [(-.16 * sc, .13 * sc), (.2 * sc, .13 * sc), (.2 * sc, .25 * sc), (.02 * sc, .28 * sc),
                   (-.16 * sc, .27 * sc)], .14 * sc, axis='X', chamfer=.012 * sc, corner=.015 * sc)
    length = .9 * sc
    front = -.16 * sc
    k.lathe(mg, [(.04 * sc, 0), (.04 * sc, .22 * sc), (.03 * sc, .25 * sc), (.03 * sc, length - .1 * sc),
                 (.05 * sc, length - .08 * sc), (.05 * sc, length)], loc=(0, front + .04 * sc, .21 * sc), rot=FORWARD,
            seg=8, worn=(4,))
    arm = a.part(f'MG_armour{tag}', 'Armor', mount)
    k.block(arm, (.12 * sc, .2 * sc, .14 * sc), loc=(.14 * sc, .04 * sc, .19 * sc), chamfer=.015 * sc)
    k.extrude(arm, [(-.26 * sc, -.15 * sc), (.26 * sc, -.15 * sc), (.22 * sc, .18 * sc), (-.22 * sc, .18 * sc)],
              .05 * sc, loc=(0, -.26 * sc, .27 * sc), rot=(-.12 + R90, 0, 0), axis='Z', chamfer=.012 * sc)
    a.pivot(f'Muzzle_mg{tag}', (0, front - length + .02 * sc, .21 * sc), mount)


def ixion(a):
    """Ixion, the armoured BelAZ-75710 mine truck: see the module docstring."""
    _suffixed(a)
    team, arm = a.part('Hull', 'Team'), a.part('Armor', 'Armor')
    steel, dark = a.part('Steel', 'Steel'), a.part('Chassis', 'Undercarriage')
    yel = a.part('Mine_yellow', 'Hazard')

    # Running gear: six tyres on their part nodes, axle housings, the frame and suspension.
    for i, (name, s, y) in enumerate(IX_TYRES):
        _ix_tyre(a, name, s, y, i)
    for y in (-8.5, 3.0, 9.0):
        k.lathe(dark, [(.5, -IX_X + .9), (.55, -IX_X + 1.1), (.55, IX_X - 1.1), (.5, IX_X - .9)],
                loc=(0, y, IX_R), rot=(0, R90, 0), seg=12)
        if y > 0:
            k.block(dark, (1.7, 1.5, 1.5), loc=(0, y, IX_R), chamfer=.12)                       # differentials
    with k.mirrored(dark):
        k.block(dark, (.9, 23.2, 1.3), loc=(1.75, -.3, 2.75), chamfer=.06)                       # frame rails
    for y in (-11.6, -5.4, 0.0, 6.0, 11.4):
        k.block(dark, (2.6, .5, .7), loc=(0, y, 2.75), chamfer=.04)                              # cross members
    with k.mirrored(steel):
        k.lathe(steel, [(.32, 0), (.32, 1.5), (.24, 1.56), (.24, 2.6)], loc=(3.0, -8.5, 2.9), seg=10, worn=(1,))
        for y in (3.0, 9.0):
            k.lathe(steel, [(.3, 0), (.3, 1.2), (.22, 1.26), (.22, 2.2)], loc=(3.1, y, 2.9), seg=10, worn=(1,))
        steel.limb((2.3, -4.6, 3.3), (2.5, -5.6, 5.3), .5, .5, bevel=0)                             # hoist rams
    for s in (-1, 1):
        k.block(arm, (.22, 6.0, 2.6), loc=(s * 5.8, -2.7, 3.8), chamfer=.05)                     # side skirts
        steel.bolts([(s * 5.92, y, z) for y in (-5.2, -3.6, -2.0, -.4) for z in (2.9, 4.7)], r=.08, h=.06,
                    rot=parts.side_rot(s), seg=6, bevel=0)

    # The front: engine hood between the front tyres, its radiator grille behind an armour guard, the upper deck
    # across the whole width, the diagonal stair over the grille, lamps.
    k.block(yel, (5.0, 6.4, 2.85), loc=(0, -9.2, 4.0), chamfer=.1)                               # hood, z 2.6..5.4
    a.part('Grille', 'Undercarriage').grille(4.2, 2.1, loc=(0, -12.42, 4.05), slats=7, depth=.08, thickness=.08)
    for x in (-1.8, -.9, 0.0, .9, 1.8):
        k.block(arm, (.2, .22, 2.5), loc=(x, -12.6, 4.0), chamfer=.04)                           # grille guard
    k.block(yel, (12.0, 7.0, .35), loc=(0, -9.1, IX_DECK - .175), chamfer=.06)                   # upper deck
    k.inset(yel, lambda c, n, f: n.z > .9 and c.z > IX_DECK - .05 and c.y < -6, width=.25, depth=.03)
    rail = a.part('Railings', 'Steel')
    sq = _sq(.09)
    k.sweep(rail, sq, [(-5.9, -6.0, IX_DECK), (-5.9, -6.0, IX_DECK + 1.0), (-5.9, -12.45, IX_DECK + 1.0),
                       (1.5, -12.45, IX_DECK + 1.0)])
    for x, y in ((-5.9, -8.0), (-5.9, -10.2), (-5.9, -12.45), (-3.6, -12.45), (-1.2, -12.45), (1.5, -12.45)):
        rail.box((.08, .08, 1.0), loc=(x, y, IX_DECK + .5), bevel=0)
    # Stair: up from the right end of the ram to the deck's left, across the grille (the BelAZ's signature).
    sz0, sz1, sx0, sx1, sy = 3.3, IX_DECK, -3.4, 1.2, -12.7
    k.sweep(rail, sq, [(sx0 - .3, sy, sz0 + .9), (sx1 - .3, sy, sz1 + .9)])
    for i in range(7):
        t = (i + .5) / 7
        k.block(steel, (.62, .4, .12), loc=(sx0 + (sx1 - sx0) * t, sy, sz0 + (sz1 - sz0) * t), chamfer=0)
    dark.limb((sx0, sy, sz0), (sx1, sy, sz1), .14, .4, bevel=0)                                    # stringer
    lamps = a.part('Lamps', 'Lamp')
    for x in (-4.9, -3.9, 3.9, 4.9):
        k.block(arm, (.7, .3, .45), loc=(x, -12.62, IX_DECK - .45), chamfer=.04)
        lamps.box((.5, .05, .28), loc=(x, -12.79, IX_DECK - .45), bevel=0)

    # The V ram across the front, 0.4 .. 3.3 m up, its nose 13 m ahead of the centre, a steel cutting edge, its
    # push frame back to the chassis and a hazard band along the top.
    ram = a.part('Ram', 'Armor')
    k.extrude(ram, [(0, -13.0), (5.5, -11.45), (5.5, -11.1), (0, -12.58), (-5.5, -11.1), (-5.5, -11.45)], 2.9,
              loc=(0, 0, 1.85), axis='Z', chamfer=.1, corner=.06)
    k.sweep(steel, _sq(.12, .2), [(-5.4, -11.5, .5), (0, -12.75, .5), (5.4, -11.5, .5)])
    with k.mirrored(dark):
        dark.limb((1.6, -12.3, 1.9), (1.75, -11.0, 2.4), .45, .45, bevel=0)
        dark.limb((4.2, -11.6, 2.4), (2.2, -10.9, 2.7), .35, .35, bevel=0)
    stripe = a.part('Ram_stripes', 'SafetyStripe')
    for s in (-1, 1):
        for i in range(5):
            t = (i + .5) / 5
            x = s * 5.2 * t
            yv = -12.98 + 1.47 * t + .2
            stripe.box((.5, .16, .16), loc=(x, yv, 3.32), rot=(0, 0, s * .27), bevel=0)

    # The cab, left of the hood under the canopy, on its part node: mine yellow, armoured vision louvres, glass,
    # and the two roof MGs standing on the canopy above it.
    pcab = a.pivot('Part_cab', IX_CAB)
    cab = a.part('Cab', 'Hazard', pcab)
    k.block(cab, (4.0, 4.2, 2.2), loc=(0, 0, 1.1), chamfer=.1)
    glass = a.part('Cab_glass', 'Glass', pcab)
    glass.box((3.1, .05, .75), loc=(0, -2.12, 1.45), bevel=0)
    glass.box((.05, 2.8, .75), loc=(2.02, -.3, 1.45), bevel=0)
    glass.box((.05, 1.2, .75), loc=(-2.02, -1.2, 1.45), bevel=0)
    carm = a.part('Cab_armour', 'Armor', pcab)
    for z in (1.18, 1.45, 1.72):
        carm.box((3.3, .16, .1), loc=(0, -2.2, z), bevel=0)
        carm.box((.16, 3.0, .1), loc=(2.1, -.3, z), bevel=0)
    k.block(carm, (3.9, .22, .85), loc=(0, -2.2, .45), chamfer=.04)
    k.block(carm, (.22, 4.0, .85), loc=(2.1, 0, .45), chamfer=.04)
    for tag, x in (('', -.9), ('__001', 1.1)):
        k.lathe(carm, [(.42, 0), (.42, .12), (.3, .18)], loc=(x, -.8, IX_ROOF - IX_DECK), seg=12, worn=(1,))
        _ix_mg(a, 'Part_cab', (x, -.8, IX_ROOF - IX_DECK + .18), tag)

    # Right of the hood: air cleaners and an armoured equipment box, the exhaust stacks under the canopy.
    k.block(arm, (3.4, 3.2, 1.3), loc=(-3.9, -10.0, IX_DECK + .65), chamfer=.08)
    for y in (-8.0, -11.3):
        k.lathe(steel, [(.55, 0), (.55, 1.25), (.42, 1.36), (0, 1.38)], loc=(-4.9, y + 1.0, IX_DECK), seg=14,
                worn=(1,))
    for x in (-2.2, -3.0):
        k.lathe(steel, [(.24, 0), (.24, 1.5), (.3, 1.56), (.3, 1.72)], loc=(x, -6.9, IX_DECK), seg=10, worn=(2,))
    a.pivot('Point_exhaust', (-2.6, -6.9, IX_DECK + 1.8))
    a.pivot('Point_fire', (0, -9.2, IX_DECK + .2))

    # The armoured body: a side profile extruded across the truck (floor 5.3 m over the tyres, roof 8.4, the dump
    # tail rising to 13 m behind), a V keel between the rear tyres, ribs, appliqué slabs and the top rails.
    body = [(-6.0, 5.3), (11.0, 5.3), (13.0, 7.9), (13.0, 8.95), (12.05, 8.95), (11.5, IX_ROOF), (-6.0, IX_ROOF)]
    k.extrude(team, body, 11.6, axis='X', chamfer=.12, corner=.1)
    k.inset(team, lambda c, n, f: n.z > .9 and c.z > IX_ROOF - .05, width=.35, depth=.035)
    k.extrude(dark, [(-3.4, 5.35), (3.4, 5.35), (2.4, 4.3), (-2.4, 4.3)], 15.5, loc=(0, 2.4, 0), axis='Y', chamfer=.08)
    k.block(team, (11.8, 6.4, .35), loc=(0, -9.0, IX_ROOF - .175), chamfer=.06)                    # canopy
    with k.mirrored(team):
        for y in (-4.6, -.6, 3.6, 7.6, 11.0):
            k.block(team, (.2, .4, 3.1), loc=(5.86, y, 6.85), chamfer=.04)                       # ribs
        k.block(team, (.32, 19.0, .3), loc=(5.7, 3.5, IX_ROOF + .15), chamfer=.05)                 # top rails
    for s in (-1, 1):
        for y0, y1 in ((-4.4, -.8), (-.4, 3.4), (3.8, 7.4)):
            k.block(arm, (.14, y1 - y0 - .2, 2.2), loc=(s * 5.86, (y0 + y1) / 2, 6.75), chamfer=.04)   # appliqué
        steel.box((.3, .3, 2.3), loc=(s * 5.85, -12.0, IX_DECK + 1.15), bevel=0)                    # canopy posts
    band = a.part('Canopy_band', 'Charred')
    band.box((11.6, .06, .3), loc=(0, -12.23, IX_ROOF - .2), bevel=0)
    for i in range(12):
        stripe.box((.32, .07, .42), loc=(-5.3 + i * .96, -12.25, IX_ROOF - .2), rot=(0, .7, 0), bevel=0)
    k.greebles(arm, (0, 9.6, IX_ROOF), (1, 0, 0), (0, 1, 0), (8.0, 3.6), 5, seed=2711, height=(.18, .42),
               chamfer=.04, avoid=((IX_TURRET, 3.0),))
    k.greebles(arm, (0, -9.6, IX_ROOF), (1, 0, 0), (0, 1, 0), (9.0, 4.0), 4, seed=2712, height=(.15, .32),
               chamfer=.04)
    # The welded adapter plate under the turret, its weld bead.
    k.block(arm, (5.8, 5.8, .3), loc=(0, IX_TURRET[1], IX_ROOF + .15), chamfer=.08)
    k.ring(a.part('Welds', 'Charred'), [(2.9, -.02), (3.0, .04), (2.9, .08)], loc=(0, IX_TURRET[1], IX_ROOF),
           seg=24)

    # The tail: the mine dispenser and its chute, tail lights.
    k.block(arm, (3.2, 1.6, 1.6), loc=(0, 11.9, 3.3), chamfer=.08)
    k.extrude(steel, [(-.9, 0), (.9, 0), (.7, -1.3), (-.7, -1.3)], .9, loc=(0, 12.4, 2.6), axis='Y', chamfer=.04)
    a.pivot('Point_mines', (0, 12.9, 1.3))
    tail = a.part('Tail_lamps', 'LavaGlow')
    for s in (-1, 1):
        tail.box((.6, .05, .3), loc=(s * 4.6, 12.97, 7.2), bevel=0)

    # The T-72-class turret on its ring: a cast dome, Kontakt-style ERA bricks over the front arc, the mantlet and
    # 125 mm gun, the commander's cupola and gunner's hatch, the IR searchlight, stowage, snorkel, a short antenna.
    t = a.pivot('Turret', IX_TURRET)
    tt = a.part('Turret_body', 'Team', t)
    k.lathe(tt, [(2.05, 0), (2.22, .16), (2.3, .34), (2.12, .68), (1.62, .95), (.9, 1.06), (0, 1.1)], seg=28,
            worn=(2,))
    tarm = a.part('Turret_armor', 'Armor', t)
    tst = a.part('Turret_steel', 'Steel', t)
    k.ring(tst, [(1.95, -.02), (2.15, -.02), (2.15, .08), (1.95, .08)], seg=24)
    for row, (rr, z, tilt) in enumerate(((2.2, .42, .25), (1.95, .8, .7))):
        for i in range(9):
            u = math.radians(-58 + i * 14.5 + row * 7)
            d = Vector((math.sin(u), -math.cos(u), 0))
            tarm.box((.62, .26, .36), loc=(d.x * rr, d.y * rr, z), rot=(-tilt * math.cos(u), tilt * math.sin(u), u),
                     bevel=0)
    k.block(tarm, (1.2, .6, .8), loc=(0, -2.15, .52), chamfer=.06)                                # mantlet
    y0, length, z = -2.42, 7.0, .52
    parts.barrel(a, 'Main_cannon', t, 0, y0, z, length, .13, seg=14, sleeve=1.25, extractor=(.4, 1.6, .5),
                 brake_name='Muzzle_brake', brake='collar')
    a.pivot('Muzzle_main', (0, y0 - length - .15, z), t)
    parts.hatch(a, .95, .4, 1.0, .46, parent=t, seg=12)
    k.lathe(tarm, [(.5, -.1), (.52, .02), (.46, .1)], loc=(.95, .4, .98), seg=12)
    parts.hatch(a, -.95, .5, .98, .4, parent=t, seg=12)
    k.lathe(tst, [(.3, 0), (.3, .5), (.26, .52), (0, .53)], loc=(-.95, -1.55, .92), rot=FORWARD, seg=12, worn=(1,))
    for s in (-1, 1):
        k.block(tarm, (.5, 1.6, .55), loc=(s * 1.95, 1.0, .45), rot=(0, 0, -s * .5), chamfer=.05)   # stowage
    k.lathe(tst, [(.18, -1.4), (.18, 1.4)], loc=(0, 2.25, .6), rot=(0, R90, 0), seg=10)            # snorkel
    k.block(tarm, (2.2, .5, .5), loc=(0, 2.05, .35), chamfer=.05)
    ant = a.part('Antennas', 'Steel', t)
    parts.antenna(ant, (1.3, 1.5, .78), h=.28, r=.06)
    k.clean(a)


# ============================================================================= Gungnir (rail_supergun)
def _sg_lower(a, team, armor, steel, dark):
    """mb_phase8.rail_supergun's lower carriage (unchanged geometry and places) with its track bed run on under the
    two capacitor cars ahead, the deck and girders on the kit's chamfered blocks."""
    rt = RAIL_TOP
    _track_bed(a, SG_TRACKS, -28.4, 26.0)
    for x in SG_TRACKS:
        for y in SG_BOGIES:
            _rail_bogie(a, x, y, 4, 1.25, .5, z0=rt)
        for yc in (-6.5, 6.5):
            k.block(dark, (2.0, 11.6, .5), loc=(x, yc, rt + 1.35), chamfer=.04)                    # span bolsters
            for yb in (yc - 3.25, yc + 3.25):
                steel.cyl(.42, .16, loc=(x, yb, rt + 1.08), seg=12, bevel=0)                         # centre pivots
        k.block(team, (1.7, 2 * SG_END - .3, 1.5), loc=(x, 0, rt + 2.35), chamfer=.06)              # main girder
        s = 1 if x > 0 else -1
        for y in (-11.5, -8.0, -4.8, -1.6, 1.6, 4.8, 8.0, 11.5):                                     # girder ribs
            armor.box((.08, .22, 1.3), loc=(x + s * .87, y, rt + 2.35), bevel=0)
        _plate_bolts(steel, x + s * .9, [y + dy for y in SG_BOGIES for dy in (-.8, .8)], rt + 3.0, r=.04, h=.04)
        for end, face in ((-1, -SG_END), (1, SG_END)):
            _headstock(a, x, face, end, rt)
    for y in (-12.0, -8.0, -1.8, 1.8, 8.0, 12.0):
        dark.box((3.4, .5, 1.2), loc=(0, y, 2.8), bevel=.02, seg=1)                                  # cross girders
    k.block(armor, (7.0, 2 * SG_END - .2, .14), loc=(0, 0, SG_DECK - .07), chamfer=.03)              # deck
    tread = a.part('Deck_tread', 'Undercarriage')
    for s in (-1, 1):
        tread.box((.8, 2 * SG_END - 1.0, .02), loc=(s * 3.0, 0, SG_DECK + .005), bevel=0)
    for x in (-2.4, 2.4):
        team.box((1.6, 4.2, .04), loc=(x, 10.6, SG_DECK), bevel=0)
    team.box((1.8, 3.8, .04), loc=(0, -10.8, SG_DECK), bevel=0)
    rail = a.part('Railings', 'Steel')
    for s in (-1, 1):
        _railing(rail, [(s * 3.42, -8.4, SG_DECK), (s * 3.42, -12.9, SG_DECK)], every=1.5)
        _railing(rail, [(s * 3.42, 8.4, SG_DECK), (s * 3.42, 12.9, SG_DECK)], every=1.5)
        for end in (-1, 1):
            ladder(a.part('Ladders', 'Steel'), (s * 3.62, end * 12.5, rt), SG_DECK + .9, 0, width=.44, step=.34,
                   rung=.03)
    steel.cyl(2.9, .16, loc=(0, 0, SG_DECK + .06), seg=32, bevel=.02, bseg=1)                         # slewing ring
    for i in range(16):
        u = i * TAU / 16
        steel.box((.2, .3, .12), loc=(math.cos(u) * 3.05, math.sin(u) * 3.05, SG_DECK + .04), rot=(0, 0, u), bevel=0)


def _capacitor_car(a, x, y0, y1, seed):
    """A capacitor car on track x between its headstock faces y0 (front) and y1 (rear, coupled to the gun
    carriage): two two-axle bogies, an underframe, a Team container of capacitor banks with raised panels and ribs,
    high-voltage stripes, roof fans, insulators and a cable tray, its power cables to the carriage's deck."""
    rt = RAIL_TOP
    team, armor = a.part('Car_body', 'Team'), a.part('Car_armour', 'Armor')
    steel, dark = a.part('Car_steel', 'Steel'), a.part('Car_frame', 'Undercarriage')
    L, mid = y1 - y0, (y0 + y1) / 2
    for yb in (y0 + 2.3, y1 - 2.3):
        _rail_bogie(a, x, yb, 2, 1.8, .45, z0=rt)
    k.block(dark, (2.7, L - .3, .5), loc=(x, mid, rt + 1.35), chamfer=.04)
    _headstock(a, x, y0, -1, rt)
    _headstock(a, x, y1, 1, rt)
    before = k.snapshot(team)
    k.block(team, (2.8, L - 1.0, 2.6), loc=(x, mid, rt + 2.9), chamfer=.1)                          # z 1.96 .. 4.56
    top = rt + 4.2
    k.inset(team, lambda c, n, f: abs(n.x) > .9, width=.18, depth=.03, since=before)
    s = 1 if x > 0 else -1
    for yr in [y0 + 1.6 + i * 2.0 for i in range(int((L - 3.0) / 2.0) + 1)]:
        armor.box((.1, .18, 2.4), loc=(x + s * 1.44, yr, rt + 2.85), bevel=0)                         # ribs
    stripe = a.part('Car_stripes', 'SafetyStripe')
    for yb in (y0 + .9, y1 - .9):
        stripe.box((2.86, .3, .22), loc=(x, yb, rt + 3.9), bevel=0)
    for yf in (mid - 3.0, mid + 1.0):                                                                # roof fans
        k.ring(steel, [(.7, 0), (.78, 0), (.78, .22), (.7, .22)], loc=(x, yf, top + .05), seg=16, worn=(2,))
        dark.cyl(.7, .06, loc=(x, yf, top + .1), seg=16, bevel=0)
    for yi in (mid - 5.0, mid + 3.4, mid + 4.8):                                                    # insulators
        k.lathe(steel, [(.16, 0), (.26, .08), (.16, .16), (.26, .24), (.16, .32), (.12, .45), (0, .46)],
                loc=(x - s * .7, yi, top + .05), seg=8)
    k.block(steel, (.4, L - 2.0, .16), loc=(x - s * .7, mid, top + .13), chamfer=0)                   # cable tray
    k.greebles(armor, (x + s * .4, mid - 1.0, top + .05), (1, 0, 0), (0, 1, 0), (1.2, 4.0), 4, seed=seed,
               height=(.12, .3), chamfer=.03)
    cables = a.part('Cables', 'Rubber')
    for dx in (-.35, .35):
        k.sweep(cables, k.round_corners(_sq(.24), .06), [(x + dx, y1 - .8, top + .02), (x + dx, y1 + .1, top - .3),
                                                         (x * .75 + dx, y1 + .7, SG_DECK + .7),
                                                         (x * .75 + dx, y1 + 1.2, SG_DECK + .12)])


def _sg_slug(a, t, loc):
    """A sabot slug on the trolley: the dart and its three-petal sabot (Hazard bands)."""
    a.part('Shell', 'Steel', t).lathe([(.16, 0), (.16, 1.6), (.1, 2.1), (0, 2.35)], loc=loc, rot=FORWARD, seg=12)
    sab = a.part('Shell_bands', 'Hazard', t)
    k.lathe(sab, [(.2, -.2), (.42, -.1), (.42, .9), (.2, 1.1)], loc=loc, rot=FORWARD, seg=12, worn=(1, 2))


def rail_supergun(a):
    """Gungnir's railway EMRG: see the module docstring. Part nodes and places as mb_p16_arms.rail_supergun."""
    _suffixed(a)
    armor, steel = a.part('Armor', 'Armor'), a.part('Steel', 'Steel')
    dark, team = a.part('Chassis', 'Undercarriage'), a.part('Hull', 'Team')
    _sg_lower(a, team, armor, steel, dark)
    # Boss parts on the lower carriage: the two 40 mm guns, the CIWS, the fire-control / generator module.
    for name, x in (('Part_gun', 2.6), ('Part_gun.001', -2.6)):
        pg = pv(a, name, (x, -11.3, SG_DECK))
        tag = name[5:].replace('.', '_')
        a.part(f'Pedestal_{tag}', 'Armor', pg).cyl(.8, .8, loc=(0, 0, .4), seg=18, bevel=.04, bseg=1)
        a.part(f'Pedestal_band_{tag}', 'SafetyStripe', pg).cyl(.82, .12, loc=(0, 0, .62), seg=18, bevel=0)
        autocannon(a, name.replace('Part_', 'Mount_'), (0, 0, .8), parent=name, length=2.4, r=.065,
                   size=(1.1, 1.3, .6))
    for name, x in (('Part_mg', 2.55), ('Part_mg.001', -2.55)):
        pg = pv(a, name, (x, 12.1, SG_DECK))
        tag = name[5:].replace('.', '_')
        a.part(f'Pedestal_{tag}', 'Armor', pg).cyl(.78, .68, loc=(0, 0, .32), seg=18, bevel=.04, bseg=1)
        a.part(f'Pedestal_band_{tag}', 'SafetyStripe', pg).cyl(.8, .1, loc=(0, 0, .45), seg=18, bevel=0)
        ciws(a, name.replace('Part_', 'Mount_'), (0, 0, .66), parent=name)
    pgen = pv(a, 'Part_generator', (0, 11.2, SG_DECK))
    _genset(a, pgen, (0, 0, 0))
    radar = a.part('Genset_radar', 'Team', pgen)
    a.part('Genset_mast', 'Steel', pgen).box((.24, .24, .9), loc=(0, .2, 1.85), bevel=0)
    k.block(radar, (2.0, .3, 1.3), loc=(0, .05, 2.75), rot=(-.35, 0, 0), chamfer=.05)
    k.inset(radar, lambda c, n, f: n.y < -.8, width=.1, depth=-.02)

    # The capacitor cars ahead, under the barrel, coupled to the carriage's front buffers.
    for i, x in enumerate(SG_TRACKS):
        _capacitor_car(a, x, -27.9, -SG_END - .76, seed=2721 + i)

    # Upper carriage on `Turret`, inside Part_main.
    pm = pv(a, 'Part_main', (0, 0, SG_DECK))
    t = a.pivot('Turret', (0, 0, .14), pm)
    tarm, tsteel = a.part('Turret_armor', 'Armor', t), a.part('Turret_steel', 'Steel', t)
    tteam, tdark = a.part('Turret_walls', 'Team', t), a.part('Turret_dark', 'Undercarriage', t)
    k.block(tarm, (6.2, 13.5, .6), loc=(0, .25, .3), chamfer=.06)                                   # base
    tsteel.cyl(2.75, .12, loc=(0, 0, .02), seg=32, bevel=0)
    wall = [(-6.2, .55), (6.9, .55), (6.9, 3.4), (4.6, 5.5), (3.0, 6.7), (-.8, 6.7), (-2.8, 5.0), (-6.2, 2.2)]
    T = Vector((0, 1.0, 5.2))                                                                         # trunnion
    for s in (-1, 1):
        k.extrude(tteam, wall, .9, loc=(s * 2.05, 0, 0), axis='X', chamfer=.08, corner=.12)
        tsteel.cyl(1.05, .22, loc=(s * 2.6, T.y, T.z), rot=ACROSS, seg=20, bevel=.03, bseg=1)         # trunnion boss
        tarm.cyl(.55, .3, loc=(s * 2.68, T.y, T.z), rot=ACROSS, seg=14, bevel=.03, bseg=1)
        _plate_bolts(tsteel, s * 2.72, (T.y - .8, T.y + .8), T.z - .8, r=.05, h=.05)
        k.block(tarm, (.12, 3.6, .14), loc=(s * 2.53, 1.1, 6.62), chamfer=0)                          # coping
        ladder(a.part('Turret_ladders', 'Steel', t), (s * 2.62, -5.3, .6), 2.9, 0, width=.44, step=.34, rung=.03)
        tdark.box((.46, 1.0, 1.4), loc=(s * 1.4, .45, 1.3), bevel=.03, seg=1)                          # gearboxes
        # Pulse-forming-network cabinets on the walls' outer faces, their raised doors and the power conduits.
        for yc, ln, h in ((-4.2, 3.2, 2.0), (4.4, 2.6, 2.4)):
            k.block(tarm, (.5, ln, h), loc=(s * 2.76, yc, .6 + h / 2), chamfer=.05)
        for dz in (.0, .32):
            k.sweep(tsteel, k.round_corners(_sq(.2), .05),
                    [(s * 2.9, -2.6, 2.0 + dz), (s * 2.9, -.4, 2.0 + dz), (s * 2.85, .2, T.z - 1.2 + dz)])
        tdark.grille(2.0, 1.0, loc=(s * 2.52, 2.4, 1.6), rot=(0, 0, R90), slats=5, depth=.05, thickness=.05)
    k.inset(tarm, lambda c, n, f: abs(n.x) > .9 and abs(c.x) > 2.95 and .7 < c.z < 3.2, width=.12, depth=.025)
    # Breech platform, the rear loading platform on struts, railings, ladder.
    k.block(tarm, (3.1, 2.7, .25), loc=(0, 5.55, 2.72), chamfer=.03)
    for x in (-1.2, 1.2):
        tsteel.box((.14, .14, 2.1), loc=(x, 5.0, 1.6), bevel=0)
        tsteel.box((.14, .14, 2.1), loc=(x, 6.6, 1.6), bevel=0)
    k.block(tarm, (6.2, 3.8, .3), loc=(0, 8.8, 1.75), chamfer=.04)
    for x in (-2.7, -.9, .9, 2.7):
        tsteel.limb((x, 6.7, .55), (x, 9.8, 1.62), .16, .16, bevel=0)
    trail = a.part('Turret_rails', 'Steel', t)
    _railing(trail, [(-3.0, 7.0, 1.9), (-3.0, 10.6, 1.9), (3.0, 10.6, 1.9), (3.0, 7.0, 1.9)], every=1.3)
    ladder(a.part('Turret_ladders', 'Steel', t), (0, 6.95, 1.9), 2.95, 0, width=.5, step=.3, rung=.03)
    # The fire-control cabin on the loading platform, its glass and roof.
    cab = a.part('Cabin', 'Team', t)
    k.block(cab, (1.9, 2.3, 2.0), loc=(2.0, 9.25, 2.9), chamfer=.06)
    k.block(tarm, (2.1, 2.5, .14), loc=(2.0, 9.25, 3.97), chamfer=.03)
    cglass = a.part('Cabin_glass', 'Glass', t)
    for y in (8.7, 9.8):
        cglass.box((.04, .7, .5), loc=(2.96, y, 3.2), bevel=0)
    cglass.box((1.2, .04, .5), loc=(2.0, 8.09, 3.2), bevel=0)
    parts.antenna(a.part('Antennas', 'Steel', t), (2.7, 10.2, 4.04), h=1.4, r=.06)
    # Sabot slugs on the trolley.
    trol = a.part('Trolley', 'Undercarriage', t)
    trol.box((1.0, 4.2, .2), loc=(-.4, 8.8, 2.1), bevel=.02, seg=1)
    for y in (7.2, 10.4):
        for x in (-.8, 0.0):
            a.part('Trolley_wheels', 'Steel', t).cyl(.14, .08, loc=(x, y, 2.0), rot=ACROSS, seg=8, bevel=0)
    for x in (-.65, -.15):
        _sg_slug(a, t, (x, 10.3, 2.62))
    # Ammunition jib crane (Part_crane), as before.
    pc = pv(a, 'Part_crane', (-2.3, 10.0, 1.9), 'Turret')
    crane = a.part('Crane', 'Hazard', pc)
    csteel = a.part('Crane_steel', 'Steel', pc)
    csteel.cyl(.36, .2, loc=(0, 0, .1), seg=14, bevel=.02, bseg=1)
    crane.cyl(.2, 3.4, loc=(0, 0, 1.9), seg=12, bevel=.02, bseg=1)
    crane.limb((0, 0, 3.4), (1.7, -2.6, 3.4), .26, .34, bevel=.03)
    crane.limb((0, 0, 2.2), (.9, -1.4, 3.25), .14, .14, bevel=0)
    csteel.box((.4, .5, .3), loc=(-.1, .3, 3.4), bevel=.02, seg=1)
    csteel.tube([(1.62, -2.48, 3.22), (1.62, -2.48, 1.55)], .025, seg=4)
    csteel.box((.2, .16, .26), loc=(1.62, -2.48, 1.45), bevel=0)

    _emrg(a, t, tsteel, T)
    k.clean(a)


def _emrg(a, t, tsteel, T):
    """The rail launcher at 10 degrees, every elevating part a Main_cannon* child of the Turret (the names and
    materials of the old gun): a square-section barrel tapering from 2.0 x 2.2 m at the breech to 1.44 x 1.4 at the
    muzzle (`Main_cannon`), the containment housing over the rear 15 m (`_jacket`), clamp bands (`_hoops`), the
    breech and its power-feed block (`_breech`, `_block`), cradle, recoil buffers, elevating arcs, busbars on
    standoffs along the top (`_truss`), the square muzzle shroud (`Muzzle_brake`) and bore (`_bore`)."""
    p = math.radians(10)
    at = _axis(T, p)
    brot = (-p, 0, 0)

    def half(sv):
        f = min(max((sv - .6) / 38.0, 0.0), 1.0)
        return 1.0 - .28 * f, 1.1 - .4 * f

    def box_along(part, s0, s1, grow=0.0, up=0.0, chamfer=.06, corner=.1):
        w0, h0 = half(s0)
        w1, h1 = half(s1)
        prof = [(-(w1 + grow), -(h1 + grow)), (w1 + grow, -(h1 + grow)), (w1 + grow, h1 + grow),
                (-(w1 + grow), h1 + grow)]
        k.extrude(part, prof, s1 - s0, loc=tuple(at((s0 + s1) / 2, up)), rot=brot, axis='Y', chamfer=chamfer,
                  corner=corner, taper=((w0 + grow) / (w1 + grow), (h0 + grow) / (h1 + grow)))

    box_along(a.part('Main_cannon', 'Armor', t), .6, 38.6, chamfer=.08, corner=.14)
    box_along(a.part('Muzzle_brake', 'Armor', t), 38.55, 39.4, grow=.06, chamfer=.05, corner=.1)
    a.part('Main_cannon_bore', 'Charred', t).box((.56, .02, .5), loc=tuple(at(39.41)), rot=brot, bevel=0)
    box_along(a.part('Main_cannon_jacket', 'Team', t), .6, 15.6, grow=.12, chamfer=.1, corner=.18)
    hoops = a.part('Main_cannon_hoops', 'Steel', t)
    for sv, g in ((1.2, .22), (5.0, .22), (9.0, .22), (13.0, .22), (15.45, .22), (21.0, .1), (27.0, .1),
                  (33.0, .1)):
        box_along(hoops, sv - .15, sv + .15, grow=g, chamfer=.03, corner=.06)
    breech = a.part('Main_cannon_breech', 'Armor', t)
    k.block(breech, (2.6, 3.1, 2.6), loc=tuple(at(-.95)), rot=brot, chamfer=.08)
    bsteel = a.part('Main_cannon_block', 'Steel', t)
    bsteel.box((3.1, .7, .8), loc=tuple(at(-1.9, .1)), rot=brot, bevel=.03, seg=1)
    bsteel.box((.5, .3, .5), loc=tuple(at(-2.6, .4, .6)), rot=brot, bevel=.02, seg=1)
    cradle = a.part('Main_cannon_cradle', 'Armor', t)
    cradle.box((2.8, 10.0, .3), loc=tuple(at(5.0, -1.45)), rot=brot, bevel=.03, seg=1)
    for sd in (-1.5, 1.5):
        cradle.box((.3, 10.0, 2.3), loc=tuple(at(5.0, -.25, sd)), rot=brot, bevel=.03, seg=1)
    recoil = a.part('Main_cannon_recoil', 'Steel', t)
    for sd in (-.62, .62):
        recoil.cyl(.32, 8.6, loc=tuple(at(4.6, 1.55, sd)), rot=(R90 - p, 0, 0), seg=14, bevel=.02, bseg=1)
    recoil.box((2.1, .5, .5), loc=tuple(at(8.9, 1.45)), rot=brot, bevel=.03, seg=1)
    recoil.cyl(.4, 3.3, loc=tuple(T), rot=ACROSS, seg=16, bevel=.02, bseg=1)
    arc = a.part('Main_cannon_arcs', 'Steel', t)
    down = -Vector((0, math.sin(p), math.cos(p)))
    fwd = Vector((0, -math.cos(p), math.sin(p)))
    R = 2.9
    for sd in (-1.5, 1.5):
        pts = [T + (down * math.cos(ph) + fwd * math.sin(ph)) * R
               for ph in (math.radians(55) * i / 11 for i in range(12))]
        for q0, q1 in zip(pts, pts[1:]):
            arc.limb((sd, q0.y, q0.z), (sd, q1.y, q1.z), .2, .3, bevel=0)
        for q in (pts[0], pts[5], pts[11]):
            arc.limb((sd, T.y, T.z), (sd, q.y, q.z), .16, .16, bevel=0)
    for sd in (-1.5, 1.5):
        q = T + down * (R + .38)
        tsteel.cyl(.32, .3, loc=(sd, q.y, q.z), rot=ACROSS, seg=12, bevel=0)
    # Busbars along the barrel's top on standoffs (where the old queen-post truss stood).
    bus = a.part('Main_cannon_truss', 'Steel', t)
    for sd in (-.5, .5):
        h0, h1 = half(16.0)[1] + .4, half(34.0)[1] + .3
        k.sweep(bus, _sq(.24, .2), [tuple(at(15.8, h0, sd)), tuple(at(34.0, h1, sd))])
        for sv in (18.0, 24.0, 30.0):
            hh = half(sv)[1]
            bus.box((.16, .16, .36), loc=tuple(at(sv, hh + .2, sd)), rot=brot, bevel=0)
    a.pivot('Muzzle_main', tuple(at(39.4)), t)


# ============================================================================= rail_tractor
def rail_tractor(a):
    """A modern Bo-Bo diesel shunter (TEM7 / BZhRK DM62 lineage), one of Gungnir's two tractors: 11.35 m over the
    buffers, 3.05 m wide, wheels on the rail heads at z = 0. Two two-axle bogies, an underframe with the fuel tank
    between them, a long hood with side grilles and roof radiator fans, a full-width cab with big windows, a roof
    air-conditioning pod, horns and a radio antenna, a short rear hood, handrails, steps, hazard headstocks and
    buffers at both ends (mb_phase8._headstock, the old faces at +-5.3). No weapon, no pivots."""
    _suffixed(a)
    team, armor = a.part('Hull', 'Team'), a.part('Armor', 'Armor')
    steel, dark = a.part('Steel', 'Steel'), a.part('Chassis', 'Undercarriage')
    for y in (-3.3, 3.3):
        _rail_bogie(a, 0, y, 2, 2.0, .5, z0=0.0)
        with k.mirrored(dark):
            k.block(dark, (.22, 3.4, .55), loc=(1.18, y, .78), chamfer=.04)                           # bogie frames
    k.block(dark, (2.7, 10.3, .34), loc=(0, 0, 1.09), chamfer=.04)                                    # underframe
    k.block(armor, (2.3, 2.6, .8), loc=(0, 0, .62), chamfer=.08)                                      # fuel tank
    armor.box((3.0, 10.3, .12), loc=(0, 0, 1.26), bevel=.02, seg=1)                                   # running boards
    for s in (-1, 1):
        armor.box((.05, 10.1, .2), loc=(s * 1.5, 0, 1.16), bevel=0)                                    # valances
    for end in (-1, 1):
        _headstock(a, 0, end * 5.3, end, 0.0, width=2.9)
        for s in (-1, 1):
            steel.box((.32, .24, .04), loc=(s * 1.28, end * 4.95, .82), bevel=0)
            steel.box((.04, .04, .5), loc=(s * 1.42, end * 4.95, 1.02), bevel=0)
    hood = [(-.98, 1.32), (.98, 1.32), (.98, 2.75), (.78, 3.05), (-.78, 3.05), (-.98, 2.75)]
    k.extrude(team, hood, 3.5, loc=(0, -3.2, 0), axis='Y', chamfer=.08, corner=.06)                    # long hood
    k.extrude(team, [(-.95, 1.32), (.95, 1.32), (.95, 2.5), (.76, 2.75), (-.76, 2.75), (-.95, 2.5)], 3.3,
              loc=(0, 3.25, 0), axis='Y', chamfer=.08, corner=.06)                                    # short hood
    cab = [(-1.45, 1.32), (1.45, 1.32), (1.45, 3.65), (1.2, 4.15), (-1.2, 4.15), (-1.45, 3.65)]
    k.extrude(team, cab, 2.9, loc=(0, 0, 0), axis='Y', chamfer=.1, corner=.08)
    glass = a.part('Windows', 'Glass')
    for end in (-1, 1):
        for x in (-.62, .62):
            glass.box((1.0, .04, .8), loc=(x, end * 1.46, 3.2), bevel=0)
    for s in (-1, 1):
        glass.box((.04, 1.4, .7), loc=(s * 1.46, -.2, 3.2), bevel=0)
        k.block(armor, (.06, .9, 1.7), loc=(s * 1.47, .85, 2.25), chamfer=0)                          # cab doors
        for i in range(2):
            steel.box((.3, .5, .04), loc=(s * 1.35, .85, .82 + i * .25), bevel=0)                    # steps
        dark.grille(2.2, .7, loc=(s * .99, -3.4, 2.15), rot=(0, 0, R90), slats=5, depth=.05, thickness=.04)
        dark.grille(1.6, .55, loc=(s * .96, 3.4, 1.95), rot=(0, 0, R90), slats=4, depth=.05, thickness=.04)
    for yf in (-4.0, -2.4):                                                                           # roof fans
        k.ring(steel, [(.48, 0), (.55, 0), (.55, .12), (.48, .12)], loc=(0, yf, 3.05), seg=14, worn=(2,))
        dark.cyl(.48, .04, loc=(0, yf, 3.1), seg=14, bevel=0)
    k.lathe(steel, [(.16, 0), (.16, .45), (.2, .5), (.2, .58)], loc=(.45, -1.75, 3.05), seg=10, worn=(2,))
    k.block(armor, (1.5, 1.4, .28), loc=(0, .1, 4.29), chamfer=.05)                                  # AC pod
    for x in (-.5, -.3):
        k.lathe(steel, [(.06, 0), (.06, .2), (.12, .4), (0, .41)], loc=(x, -1.0, 4.18), rot=FORWARD, seg=8)
    parts.antenna(a.part('Antenna', 'Steel'), (.75, .8, 4.15), h=1.3, r=.05)
    lamps, tail = a.part('Lamps', 'Lamp'), a.part('Tail_lamps', 'LavaGlow')
    for s in (-1, 1):
        lamps.box((.22, .04, .16), loc=(s * .55, -4.97, 2.75), bevel=0)
        tail.box((.22, .04, .16), loc=(s * .55, 4.92, 2.5), bevel=0)
        for end in (-1, 1):
            armor.box((.22, .16, .22), loc=(s * 1.2, end * 5.07, 1.43), bevel=.02, seg=1)
            a.part('Marker_lamps' if end < 0 else 'Tail_lamps', 'Lamp' if end < 0 else 'LavaGlow').box(
                (.14, .04, .12), loc=(s * 1.2, end * 5.155, 1.45), bevel=0)
    rail = a.part('Handrails', 'Steel')
    for s in (-1, 1):
        for y0, y1 in ((-4.85, -1.6), (1.6, 4.85)):
            k.sweep(rail, _sq(.05), [(s * 1.42, y0, 2.3), (s * 1.42, y1, 2.3)])
            for y in (y0, (y0 + y1) / 2, y1):
                rail.box((.04, .04, 1.0), loc=(s * 1.42, y, 1.82), bevel=0)
    k.greebles(armor, (0, 3.6, 2.75), (1, 0, 0), (0, 1, 0), (1.2, 2.0), 3, seed=2731, height=(.06, .14),
               chamfer=.02)
    k.clean(a)


BUILDERS = {
    'ixion': (ixion, dict(ao_distance=1.0, grime_height=1.4)),
    'rail_supergun': (rail_supergun, dict(ao_distance=1.4, grime_height=.8)),
    'rail_tractor': (rail_tractor, dict(ao_distance=.8, grime_height=.7)),
}
