"""Machine Brigade premium aircraft (bought with coins), built with frontier_kit and mb_air's
fixed-wing kit.

Conventions as in mb_air.py: metres, +Z up, Blender -Y is the nose, origin at the fuselage centre
(they fly). Team / TeamGlow parts are recoloured per army at runtime.
  * heavy_bomber: strategic bomber (B-52 lineage). `Bombs` is a pivot at the bomb bay holding
    the rack of twelve bombs under the open bay doors (hidden once they drop); `Muzzle_gun` at the
    tail turret's four barrels, which point backwards (+Y).
  * stealth_bomber: faceted flying wing (B-2 lineage). `Bombs` is a pivot at the twin bomb bays
    holding six guided bombs behind the open doors.
  * sky_gunship: side-firing gunship (AC-130 lineage). `Propeller`, `Propeller_2`, `Propeller_3`
    and `Propeller_4` (engines one to four, left to right) spin about local Y. Its guns fire out of
    the left side (-X): `Muzzle_main` at the 105 mm howitzer, `Muzzle_gun` at the 40 mm cannon
    and `Muzzle_mg` at the 25 mm gatling.
"""
import math

from mathutils import Vector

from mb_air import (ACROSS, BACKWARD, FORWARD, LEFT, R90, RIGHT, Planform, _bomb, _dome, _naca, _patch, _prop_blade,
                    _pylon, _revolve, _ring_at, _sec, _skin_offsets, _skin_panel, _skin_z, _store_parts, _upright,
                    _wing)
from mb_vehicles import _frame


def _deck_side(rings, y, z=.78):
    """Half-width of a dome loft at height z (for windows set into its sides)."""
    ring = _ring_at(rings, y)
    side = [q for q in ring if q[0] > 0]
    for q0, q1 in zip(side, side[1:]):
        if (q0[2] - z) * (q1[2] - z) <= 0:
            k = (z - q0[2]) / ((q1[2] - q0[2]) or 1e-9)
            return q0[0] + (q1[0] - q0[0]) * k
    return side[0][0]


def _twin_pod(a, x, y, z, r=.3, length=2.2, gap=.33):
    """Two turbofans side by side in one pod (B-52 style) with their intakes at y: cowls, dark fan
    faces with bullets, dark exhausts with a glowing ring, joined by a web."""
    cowl = a.part('Nacelles', 'Team')
    dark = a.part('Fan_faces', 'Undercarriage')
    steel = a.part('Steel', 'Steel')
    glow = a.part('Exhaust_glow', 'Alloy')
    L = length
    for dx in (-gap, gap):
        cx = x + dx
        _revolve(cowl, [(r * .84, .3), (r * .88, 0), (r, .1), (r, L * .72), (r * .78, L), (r * .68, L), (r * .8, .4)],
                 (cx, y, z), BACKWARD, 12)
        dark.cyl(r * .76, .05, loc=(cx, y + .34, z), rot=FORWARD, seg=10, bevel=0)
        steel.cyl(r * .22, r * .5, r2=.01, loc=(cx, y + .3, z), rot=FORWARD, seg=8, bevel=0)
        dark.cyl(r * .64, .05, loc=(cx, y + L * .86, z), rot=FORWARD, seg=10, bevel=0)
        glow.torus(r * .5, r * .05, loc=(cx, y + L - .06, z), rot=FORWARD, seg=10, ring=3)
    cowl.box((gap * 2, L * .6, r * .9), loc=(x, y + L * .45, z), bevel=.04, seg=1)


def heavy_bomber(a):
    """Strategic bomber (B-52 lineage): a long slab-sided fuselage with a stepped cockpit, chin
    sensor turrets and a refuelling slipway, a shoulder wing swept 35 degrees with flaps, spoilers
    and underwing tanks, four twin-engine pods on pylons, a tall fin with rudder, a quad-gun tail
    turret under its radar, and a bomb bay under the wing whose doors hang open over a rack of
    twelve bombs. Fuselage about 16 m, span about 18 m."""
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    moving = a.part('Control_surfaces', 'Armor')
    panels = a.part('Panels', 'Team')
    glow = a.part('Wing_lights', 'TeamGlow')
    glass = a.part('Canopy', 'Glass')

    def sec(y, w, zb, zt):
        return _sec(y, w, zb, zt, n=16, pt=2.6, pb=3.2)
    hull = [sec(-7.7, .35, -.45, .15), sec(-7.1, .6, -.72, .45), sec(-6.2, .78, -.82, .66), sec(-4.8, .86, -.85, .74),
            sec(-1.6, .88, -.85, .76), sec(2.1, .88, -.84, .76), sec(4.4, .8, -.7, .74), sec(6.2, .62, -.45, .7),
            sec(7.6, .36, -.12, .58), sec(8.15, .22, .02, .42)]
    body.loft(hull[:5], bevel=.02, seg=1)
    body.loft(hull[5:], bevel=.02, seg=1)
    # Bomb bay between the two lofts: an open-bottomed section with side walls and a roof.
    zr = .15
    bay = []
    for y in (-1.6, 2.1):
        ring = sec(y, .88, -.85 + (.01 if y > 0 else 0), .76)
        x2, z2 = ring[2][0], ring[2][2]
        xi = x2 - .06
        bay.append(ring[2:15] + [(-xi, y, z2), (-xi, y, zr), (xi, y, zr), (xi, y, z2)])
    body.loft(bay, bevel=0)
    liner = []
    for y in (-1.58, 2.08):
        liner.append([(xi - .015, y, z2), (xi - .015, y, zr - .015), (-xi + .015, y, zr - .015), (-xi + .015, y, z2),
                      (-xi + .045, y, z2), (-xi + .045, y, zr - .045), (xi - .045, y, zr - .045), (xi - .045, y, z2)])
    dark.loft(liner, bevel=0)
    for y in (-1.58, 2.08):
        dark.box((2 * (xi - .03), .02, zr - .03 - z2), loc=(0, y, (zr - .03 + z2) / 2), bevel=0)
    doors = a.part('Bay_doors', 'Team')
    for s in (-1, 1):                                      # doors hinged at the keel lines, hanging open
        tilt = .26
        c = Vector((s * x2, .25, z2)) + Vector((s * math.sin(tilt), 0, -math.cos(tilt))) * .36
        doors.box((.04, 3.5, .72), loc=tuple(c), rot=(0, -s * tilt, 0), bevel=.01, seg=1)
    # The rack: twelve bombs in three columns, two layers and two rows, hung from steel beams.
    b = a.pivot('Bombs', (0, .25, -.3))
    a.pivot('Muzzle_missile', (0, .25, -.9))
    bombs = _store_parts(a, b)
    rack = a.part('Bomb_rack', 'Steel')
    for x in (-.38, 0, .38):
        for zl in (.14, -.2):
            rack.box((.05, 3.44, .03), loc=(x, .25, -.3 + zl + .165), bevel=0)
            for yy in (-.9, .9):
                _bomb(bombs, (x, yy, zl), length=1.5, r=.14, seg=8, lean=True)
        rack.box((.03, .03, zr - .01), loc=(x, -1.4, (zr + .01) / 2), bevel=0)
        rack.box((.03, .03, zr - .01), loc=(x, 1.9, (zr + .01) / 2), bevel=0)
    # Chin radome, sensor turrets and the stepped flight deck with its window band.
    armor.loft([[(0, -8.05, -.22)], _sec(-7.9, .2, -.36, .0, n=16), _sec(-7.62, .33, -.47, .12, n=16)], bevel=.01)
    for s in (-1, 1):
        armor.sphere(.16, loc=(s * .3, -7.05, -.7), seg=10, rings=6)
        glass.cyl(.08, .03, loc=(s * .3, -7.2, -.72), rot=FORWARD, seg=8, bevel=0)
    deck = [_dome(y, w, _skin_z(hull, y, w) - .04, z1) for y, w, z1 in
            ((-7.35, .34, .42), (-7.1, .48, .66), (-6.85, .6, .86), (-6.45, .66, .94), (-6.1, .7, .98),
             (-5.3, .66, .92), (-4.6, .5, .82))]
    # The windscreen is a glass slice of the flight-deck loft itself (no skin to z-fight with).
    body.loft(deck[:2], bevel=.02, seg=1)
    glass.loft(deck[1:4], bevel=0)
    body.loft(deck[3:] + [[(0, -3.9, .72)]], bevel=.02, seg=1)
    frames = a.part('Canopy_frames', 'Armor')
    edge = [_ring_at(deck, y) for y in (-7.1, -6.45)]
    for i in (2, 4, 6):
        frames.tube([(q[i][0], q[i][1], q[i][2] + .02) for q in edge], .022, seg=5)
    frames.tube([(q[0], q[1], q[2] + .02) for q in edge[1][1:8]], .022, seg=5)
    for s in (-1, 1):
        glass.box((.03, .5, .16), loc=(s * _deck_side(deck, -5.6), -5.6, .78), bevel=0)        # side windows
    # Refuelling slipway behind the cockpit, antennas and formation lights along the spine.
    _patch(dark, hull, -4.4, -3.7, 7, 9, out=.013, inn=.012, bevel=0)
    haz = a.part('Slipway_lines', 'Hazard')
    for s in (-1, 1):
        haz.box((.03, 1.3, .03), loc=(s * .16, -3.6, _skin_z(hull, -3.6, .16)), bevel=0)
        glow.box((.02, .6, .04), loc=(s * .875, -3.0, .1), bevel=0)
    for y in (-2.6, 3.2):
        steel.box((.02, .26, .2), loc=(0, y, _skin_z(hull, y, 0) + .07), rot=(-.35, 0, 0), bevel=0, taper=(1, .5))
    steel.box((.02, .26, .2), loc=(0, -4.2, -.93), rot=(.35, 0, 0), bevel=0, taper=(1, .5))
    # Shoulder wing swept 35 degrees: flaps and outer ailerons, spoiler panels, fuel access panels.
    wing = Planform(.7, 9.0, -2.6, 3.15, 4.3, 1.3, .44, .12, .45, .3)
    spoilers = a.part('Spoilers', 'Armor')
    for frame in (RIGHT, LEFT):
        _wing(body, moving, wing, frame, cs=[(1.0, 4.0, .76), (4.0, 7.0, .76), (7.0, 8.7, .74)])
        _skin_panel(spoilers, wing, frame, 2.0, 3.8, .56, .7)
        _skin_panel(spoilers, wing, frame, 4.3, 6.6, .56, .7)
        _skin_panel(panels, wing, frame, 1.4, 3.0, .15, .42)
        _skin_panel(panels, wing, frame, 5.0, 6.8, .18, .45)
    # Four twin-engine pods on swept pylons, underwing tanks near the tips.
    pylons = a.part('Pylons', 'Armor')
    tanks = a.part('Tanks', 'Team')
    for s in (-1, 1):
        for x in (2.9, 5.5):
            le, zb = wing.le(x), wing.bottom(x)
            z = zb - .62
            _twin_pod(a, s * x, le - 1.6, z)
            pylons.prism([(le - .9, z + .2), (le + .7, zb + .06), (le + 1.4, zb + .06), (le + .1, z + .2)], .12,
                         loc=(s * x, 0, 0), bevel=.02)
        x = 7.45
        le, zb = wing.le(x), wing.bottom(x)
        tanks.lathe([(.04, 2.7), (.14, 2.45), (.22, 1.9), (.22, .8), (.15, .25), (0, 0)],
                    loc=(s * x, le - 1.1, zb - .3), rot=BACKWARD, seg=12)
        _pylon(pylons, s * x, le - .3, le + .8, zb + .05, zb - .1, w=.08)
        glow.box((.05, .14, .06), loc=(s * 9.0, wing.le(9.0) + .1, wing.at(9.0)[3]), bevel=.01, seg=1)
    # Tailplane with elevators and the tall fin with its rudder.
    stab = Planform(.35, 3.1, 5.3, 6.7, 2.1, .9, .14, .07, .38)
    for frame in (RIGHT, LEFT):
        _wing(body, moving, stab, frame, cs=[(.6, 3.0, .7)])
    fin = Planform(0, 3.9, 4.9, 6.9, 2.6, 1.1, .16, .08)
    _wing(body, moving, fin, _upright(0, .55, 0), cs=[(.35, 3.6, .7)], lower=1.0)
    a.part('Beacon', 'TeamGlow').sphere(.06, loc=(0, 7.4, 4.47), seg=8, rings=5)
    # Tail turret: four guns under a fire-control radar, pointing backwards.
    armor.sphere((.27, .3, .26), loc=(0, 8.28, .22), seg=12, rings=8)
    armor.sphere(.19, loc=(0, 7.95, .62), seg=10, rings=6)
    guns = a.part('Tail_guns', 'Steel')
    guns.box((.3, .2, .24), loc=(0, 8.52, .22), bevel=.03, seg=1)
    for dx in (-.075, .075):
        for dz in (-.07, .07):
            guns.cyl(.022, .62, loc=(dx, 8.9, .22 + dz), rot=BACKWARD, seg=6, bevel=0)
            guns.cyl(.034, .09, loc=(dx, 9.18, .22 + dz), rot=BACKWARD, seg=6, bevel=0)
    a.pivot('Muzzle_gun', (0, 9.25, .22))


# ----------------------------------------------------------------------------- stealth bomber
SW_U = (0, .03, .1, .2, .32, .46, .62, .78, .9, 1)


def _sw_ring(pf, s, notch=None, lower=.5):
    """Flying-wing section at span s (span, y, z). notch = (y0, y1, z_roof) cuts a bomb bay out of
    the lower surface between y0 and y1 (walls and a roof)."""
    le, c, t, h = pf.at(s)
    up, lo = t / (1 + lower), t * lower / (1 + lower)

    def zl(u):
        return h - max(lo * _naca(u), .007)
    ring = [(s, le + u * c, h + max(up * _naca(u), .007)) for u in reversed(SW_U)]
    if notch is None:
        return ring + [(s, le + u * c, zl(u)) for u in SW_U[1:]]
    y0, y1, zr = notch
    u0, u1 = (y0 - le) / c, (y1 - le) / c
    ring += [(s, le + u * c, zl(u)) for u in (.03, .1, .2)]
    ring += [(s, y0, zl(u0)), (s, y0, zr), (s, y1, zr), (s, y1, zl(u1))]
    return ring + [(s, le + u * c, zl(u)) for u in (.9, 1)]


def stealth_bomber(a):
    """Stealth bomber (B-2 lineage): a faceted flying wing swept 33 degrees with a double-W
    sawtooth trailing edge, a humped crew section with four windscreen panels, serrated dorsal
    intakes, exhaust trenches glowing ahead of heat-tiled aft decks, split elevons, and twin bomb
    bays whose doors hang open under six laser-guided bombs. Span about 16 m."""
    wing = a.part('Wing', 'Team', flat=True)
    armor = a.part('Armor', 'Armor', flat=True)
    dark = a.part('Undercarriage', 'Undercarriage')
    moving = a.part('Control_surfaces', 'Armor', flat=True)
    glow = a.part('Wing_lights', 'TeamGlow')
    # Planform: leading edge straight out to the tips, trailing edge as a double W.
    pa = Planform(0, 1.9, -3.2, -1.965, 6.4, 3.915, 1.1, .5, .1, .05)
    pb = Planform(1.9, 3.9, -1.965, -.665, 3.915, 3.865, .5, .3, .05, .02)
    pc = Planform(3.9, 8.0, -.665, 2.0, 3.865, .55, .3, .06, .02, .06)
    zr = .26
    bay = (-1.0, 1.0, zr)
    for frame in (RIGHT, LEFT):
        wing.loft([[frame(*q) for q in _sw_ring(pa, s, bay)] for s in (0, 1.1)], bevel=0)
        wing.loft([[frame(*q) for q in _sw_ring(pf, s)] for pf, s in ((pa, 1.1), (pa, 1.9), (pb, 2.2), (pb, 3.5),
                                                                       (pb, 3.9))], bevel=0)
        # Outer panel with split elevons along its trailing edge.
        _wing(wing, moving, pc, frame, cs=[(4.3, 5.9, .8), (6.0, 7.6, .78)], lower=.5, bevel=0)
    # Twin bomb bays: dark liner, a keel between them and doors hanging open at the bay edges.
    dark.box((2.14, 1.95, .02), loc=(0, 0, zr - .015), bevel=0)
    for y in (-.975, .975):
        dark.box((2.14, .02, .3), loc=(0, y, zr - .175), bevel=0)
    for s in (-1, 1):
        dark.box((.02, 1.95, .3), loc=(s * 1.075, 0, zr - .175), bevel=0)
    armor.box((.08, 2.0, .38), loc=(0, 0, zr - .15), bevel=0)
    doors = a.part('Bay_doors', 'Team', flat=True)
    zh = pa.bottom(.6, .5)
    for s in (-1, 1):
        for x, tilt in ((.1, -.15), (1.08, .3)):
            c = Vector((s * x, 0, zh)) + Vector((s * math.sin(tilt) * .25, 0, -math.cos(tilt) * .25))
            doors.box((.03, 1.9, .5), loc=tuple(c), rot=(0, -s * tilt, 0), bevel=0)
    b = a.pivot('Bombs', (0, 0, 0))
    a.pivot('Muzzle_missile', (0, 0, -.5))
    bombs = _store_parts(a, b)
    for s in (-1, 1):
        for x in (.24, .57, .9):
            _bomb(bombs, (s * x, 0, zr - .21), length=1.8, r=.15, seg=8, guided=True)
    rack = a.part('Bomb_rack', 'Steel')
    for s in (-1, 1):
        rack.box((.84, .06, .04), loc=(s * .57, -.5, zr - .04), bevel=0)
        rack.box((.84, .06, .04), loc=(s * .57, .5, zr - .04), bevel=0)
    # Crew hump on the centreline with four windscreen panes; edge strips outline the planform.
    glass = a.part('Canopy', 'Glass', flat=True)
    hump = []
    for y, w, rise in ((-3.0, .28, .02), (-2.6, .62, .2), (-2.05, .74, .27), (-1.35, .62, .18), (-.6, .3, .03)):
        base = min(_sw_top(pa, x, y) for x in (0, w * .5, w)) - .03
        hump.append(_dome(y, w, base, _sw_top(pa, 0, y) + rise, n=11))
    wing.loft(hump, bevel=0)
    for i0, i1 in ((1, 2), (3, 4), (6, 7), (8, 9)):
        _patch(glass, hump, -2.72, -2.3, i0, i1, out=.02, inn=.012, bevel=0)
    # Edge strips run tip to tip through the wing lofts' stations, so their facets stay parallel.
    le_st = ((pa, 0), (pa, 1.1), (pa, 1.9), (pb, 2.2), (pb, 3.5), (pb, 3.9), (pc, 4.3), (pc, 5.9), (pc, 6.0), (pc, 7.6),
             (pc, 8.0))
    _edge_strip(armor, le_st, 0, .03)                                                          # leading edge
    _edge_strip(armor, le_st[:6], .95, .99)       # trailing edge (its buried end meets the elevon panel at 3.9)
    for frame in (RIGHT, LEFT):
        pan = a.part('Panels', 'Team', flat=True)
        _skin_panel(pan, pb, frame, 2.2, 3.5, .2, .46, out=.02, inn=.012, lower=.5)
        _skin_panel(pan, pb, frame, 2.2, 3.5, .62, .78, out=.02, inn=.012, lower=.5)
        _skin_panel(pan, pc, frame, 6.2, 7.2, .2, .46, out=.02, inn=.012, lower=.5)
    # Serrated dorsal intakes and the exhaust trenches with heat-tiled decks behind them.
    tiles = a.part('Exhaust_decks', 'Armor', flat=True)
    for frame in (RIGHT, LEFT):
        s0, s1 = .9, 1.75
        rings = []
        for y, w, rise in ((-1.35, .44, .26), (-.8, .42, .19), (-.1, .32, .08), (.5, .12, .01)):
            xs = (s0 + s1) / 2
            base = min(_sw_top(pa, x, y) for x in (xs - w, xs, xs + w)) - .03
            rings.append([frame(xs + q[0], y, q[2]) for q in _dome(y, w, base, _sw_top(pa, xs, y) + rise, n=7)])
        wing.loft(rings, bevel=0)
        mouth = rings[0]
        dark.loft([[tuple(Vector(q) + Vector((0, -.012, 0))) for q in mouth],
                   [tuple(Vector(q) + Vector((0, -.004, 0))) for q in mouth]], bevel=0)
        for k in range(4):                                                               # serrated lip
            xk = s0 + .08 + k * (s1 - s0 - .16) / 3
            zt = _sw_top(pa, (s0 + s1) / 2, -1.35) + .26
            armor.prism([(-1.37, zt - .05), (-1.52, zt + .01), (-1.37, zt + .02)], .1, loc=frame(xk, 0, 0), bevel=0)
        _skin_panel(dark, pa, frame, 1.0, 1.8, .6, .74, out=.012, inn=.012, lower=.5)           # exhaust trench
        _skin_panel(a.part('Exhaust_glow', 'Alloy'), pa, frame, 1.08, 1.72, .66, .69, out=.024, inn=.01, lower=.5)
        _skin_panel(tiles, pa, frame, 1.0, 1.8, .76, .92, out=.012, inn=.012, lower=.5)
        _skin_panel(a.part('Panels', 'Team', flat=True), pc, frame, 4.5, 5.6, .2, .46, out=.02, inn=.012, lower=.5)
        armor.box((.04, .7, .2), loc=frame(1.325, -1.05, _sw_top(pa, 1.325, -1.05) + .08), bevel=0)  # splitter
    for s in (-1, 1):
        glow.box((.05, .16, .04), loc=(s * 8.01, 1.97, .07), bevel=0)
        a.part('Steel', 'Steel').box((.02, .2, .12), loc=(s * .8, -.6, _sw_top(pa, .8, -.6) + .04), rot=(-.4, 0, 0),
                                     bevel=0, taper=(1, .5))
    a.part('Beacon', 'TeamGlow').sphere(.05, loc=(0, .8, _sw_top(pa, 0, .8) + .01), seg=8, rings=5)


def _edge_strip(part, stations, u0, u1, out=.02, inn=.012, lower=.5):
    """One continuous strip on a flying wing's upper skin between chord fractions u0..u1 through
    [(planform, span)...] stations, mirrored into a single loft from tip to tip: leading- and
    trailing-edge outlines."""
    us = [u0] + [u for u in SW_U if u0 + .02 < u < u1 - .02] + [u1]
    rings = []
    for frame, seq in ((LEFT, stations[:0:-1]), (RIGHT, stations)):
        for pf, s in seq:
            le, c, t, h = pf.at(s)
            up = t / (1 + lower)
            top, bot = _skin_offsets([(le + u * c, h + max(up * _naca(u), .007)) for u in us], out, inn)
            rings.append([frame(s, y, z) for y, z in top + bot[::-1]])
    part.loft(rings, bevel=0)


def _sw_top(pf, s, y, lower=.5):
    """Upper-skin height of a flying-wing planform at span s and chord position y."""
    le, c, t, h = pf.at(s)
    return h + max(t / (1 + lower) * _naca((y - le) / c), .007)


# ----------------------------------------------------------------------------- sky gunship
def _turboprop(a, x, y0, zc, pivot, te, side, blades=6):
    """Turboprop nacelle slung under the wing from its nose at y0 back past the trailing edge te:
    an oil-cooler scoop under the spinner, cowl flaps, an exhaust stack on the outboard side
    (side = +1 or -1) and a six-blade propeller on the pivot (spins about Y)."""
    body = a.part('Nacelles', 'Team')
    rings = [_sec(y0, .2, zc - .2, zc + .22, n=12), _sec(y0 + .35, .3, zc - .36, zc + .3, n=12),
             _sec(y0 + 1.5, .32, zc - .38, zc + .32, n=12), _sec(te - .3, .26, zc - .27, zc + .24, n=12),
             _sec(te + .35, .1, zc - .1, zc + .1, n=12)]
    body.loft([[(x + q[0], q[1], q[2]) for q in r] for r in rings], bevel=.02, seg=1)
    body.box((.26, .55, .2), loc=(x, y0 + .45, zc - .34), bevel=.04, seg=1, taper=(.9, .9))      # oil cooler
    a.part('Undercarriage', 'Undercarriage').box((.2, .03, .12), loc=(x, y0 + .17, zc - .35), bevel=0)
    flaps = a.part('Cowl_flaps', 'Armor')
    for k in range(4):                                                                       # cowl flaps
        ang = -.9 + k * .6
        flaps.box((.16, .12, .025), loc=(x + math.sin(ang) * .33, y0 + 1.05, zc + math.cos(ang) * .35 - .02),
                  rot=(0, ang, 0), bevel=0)
    steel = a.part('Exhaust_stacks', 'Steel')
    steel.cyl(.07, .45, loc=(x + side * .27, y0 + 2.0, zc - .12), rot=(-R90 + .15, 0, -side * .35), seg=8, bevel=0)
    m = _frame((x + side * .27, y0 + 2.0, zc - .12), (-R90 + .15, 0, -side * .35))
    a.part('Exhaust_bores', 'Undercarriage').cyl(.05, .02, loc=tuple(m @ Vector((0, 0, .235))),
                                                  rot=(-R90 + .15, 0, -side * .35), seg=8, bevel=0)
    p = a.pivot(pivot, (x, y0 - .04, zc + .02))
    a.part(f'{pivot}_hub', 'Armor', p).lathe([(.19, -.02), (.18, .12), (.12, .28), (0, .38)], rot=FORWARD, seg=12)
    bl = a.part(f'{pivot}_blades', 'Armor', p)
    tips = a.part(f'{pivot}_tips', 'Hazard', p)
    for k in range(blades):
        phi = k * math.tau / blades
        _prop_blade(bl, phi, .1, .74, .2, .13, .05, .022, .9, .45, axis_y=-.14)
        _prop_blade(tips, phi, .74, .86, .13, .1, .022, .018, .45, .35, axis_y=-.14)


def _side_gun(loc, tilt=.14):
    """A barrel out of the left side (-X) from loc, tilted down by `tilt`: returns a function giving
    the point t metres along the barrel, and the rotation that lays a cylinder along it."""
    d = Vector((-math.cos(tilt), 0, -math.sin(tilt)))
    return (lambda t: tuple(Vector(loc) + d * t)), (0, -R90 - tilt, 0)


def sky_gunship(a):
    """Side-firing gunship (AC-130 lineage): a round transport fuselage with a radome nose, flight
    deck windows and a refuelling probe, gear sponsons, a high wing with flaps, ailerons, flap-track
    fairings and underwing tanks, four turboprops with six-blade `Propeller`..`Propeller_4`, an
    upswept tail with a tall fin, and the left-side battery: a 105 mm howitzer (`Muzzle_main`), a
    40 mm cannon (`Muzzle_gun`) and a 25 mm gatling (`Muzzle_mg`), with sensor turrets under the
    nose and behind the gear. Span about 17 m."""
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    moving = a.part('Control_surfaces', 'Armor')
    panels = a.part('Panels', 'Team')
    glow = a.part('Wing_lights', 'TeamGlow')
    glass = a.part('Canopy', 'Glass')
    frames = a.part('Canopy_frames', 'Armor')

    def sec(y, w, zb, zt):
        return _sec(y, w, zb, zt, n=24, pt=2.2, pb=2.4)
    hull = [sec(-5.85, .5, -.62, .52), sec(-5.35, .82, -.86, .86), sec(-4.7, .95, -.92, .98), sec(-3.6, .98, -.93, 1.0),
            sec(2.4, .98, -.93, 1.0), sec(3.3, .96, -.74, 1.0), sec(4.3, .88, -.36, .98), sec(5.2, .7, .06, .95),
            sec(5.9, .44, .38, .9), sec(6.4, .22, .56, .82)]
    body.loft(hull + [[(0, 6.66, .7)]], bevel=.02, seg=1)
    armor.loft([[(0, -6.36, -.12)], _sec(-6.2, .24, -.4, .14, n=24), _sec(-5.8, .47, -.6, .42, n=24)], bevel=0)
    # Flight deck: windscreen on the nose slope with posts, eyebrow and side windows.
    _patch(glass, hull, -5.85, -5.35, 9, 15, out=.02, inn=.012, bevel=0)
    for i in (10, 12, 14):
        frames.tube([tuple(Vector(r_[i]) + Vector((0, 0, .03))) for r_ in (hull[0], hull[1])], .022, seg=5)
    frames.tube([tuple(Vector(q) + Vector((0, 0, .03))) for q in hull[1][9:16]], .022, seg=5)
    _patch(glass, hull, -5.2, -4.85, 10, 14, out=.02, inn=.012, bevel=0)
    for s in (-1, 1):
        glass.box((.03, .42, .26), loc=(s * .905, -5.0, .56), rot=(0, 0, s * -.12), bevel=0)
        glass.box((.03, .3, .2), loc=(s * .96, -4.45, .55), bevel=0)
    steel.tube([(.42, -4.3, .96), (.46, -5.6, 1.08), (.48, -6.5, 1.1)], .035, seg=8)                # refuelling probe
    steel.cyl(.05, .12, r2=.03, loc=(.48, -6.55, 1.1), rot=FORWARD, seg=8, bevel=0)
    # Round troop windows, a crew door, a paratroop door and countermeasure dispensers.
    for s, ys in ((-1, (-2.3, -1.4)), (1, (-2.6, -1.3, 1.0, 3.6))):
        for y in ys:
            glass.cyl(.11, .04, loc=(s * .975, y, .45), rot=ACROSS, seg=10, bevel=0)
    _patch(panels, hull, -4.7, -3.6, 15, 17, out=.018, inn=.012, bevel=.005)                     # crew door
    _patch(panels, hull, 2.4, 3.3, 5, 7, out=.018, inn=.012, bevel=.005)                        # paratroop door
    for s in (-1, 1):
        armor.box((.1, .6, .3), loc=(s * .88, 4.3, .45), rot=(0, 0, s * .12), bevel=.02, seg=1)
        dark.grille(.5, .22, loc=(s * .935, 4.3, .45), rot=(0, 0, s * (R90 + .12)), slats=3, depth=.03, thickness=.03)
        glow.box((.02, .6, .04), loc=(s * .965, -3.0, .1), bevel=0)                              # formation lights
    for y, z in ((-2.0, 1.0), (1.9, 1.0), (3.6, .98), (-.5, -.93)):
        steel.box((.02, .28, .2), loc=(0, y, z + (.08 if z > 0 else -.08)), rot=(-.35 if z > 0 else .35, 0, 0),
                  bevel=0, taper=(1, .5))
    # Main gear sponsons low on both sides.
    for s in (-1, 1):
        spon = [[(s * .86 + q[0], q[1], q[2]) for q in _sec(y, w, -1.0, -.25, n=12)] for y, w in
                ((-1.35, .24), (-.6, .3), (1.5, .3), (2.2, .22))]
        body.loft([[(s * .86, -1.95, -.6)]] + spon + [[(s * .86, 2.7, -.6)]], bevel=.02, seg=1)
    # High wing on a root fairing: flaps and ailerons, flap-track fairings, leading-edge de-icing boots.
    body.loft([_dome(y, w, _skin_z(hull, y, w) - .04, z1) for y, w, z1 in
               ((-1.5, .4, 1.04), (-.9, .72, 1.2), (1.4, .72, 1.2), (2.2, .4, 1.04))], bevel=.02, seg=1)
    wing = Planform(0, 8.5, -.9, -.6, 2.3, 1.15, .36, .14, 1.1, 1.18)
    boots = a.part('Deicing_boots', 'Armor')
    tracks = a.part('Flap_tracks', 'Armor')
    for frame in (RIGHT, LEFT):
        _wing(body, moving, wing, frame, cs=[(.95, 4.9, .7), (5.0, 8.25, .7)], bevel=0)    # the boot covers the LE
        _skin_panel(boots, wing, frame, 0, 0, 0, .1, stations=(.95, 4.9, 5.0, 8.25))
        _skin_panel(panels, wing, frame, 1.2, 2.0, .2, .5)
        _skin_panel(panels, wing, frame, 5.4, 7.0, .22, .52)
        for x in (1.4, 3.3, 5.6, 7.2):
            te, zb = wing.te(x), wing.bottom(x, .8)
            tracks.loft([[frame(x + q[0], q[1], q[2]) for q in _sec(y, .06, zb - h, zb + .03, n=6)]
                         for y, h in ((te - .75, .03), (te - .2, .12), (te + .25, .06))], bevel=0)
    for s in (-1, 1):
        glow.box((.06, .16, .06), loc=(s * 8.52, wing.le(8.5) + .15, wing.at(8.5)[3]), bevel=.01, seg=1)
    # Four turboprops (engines one to four, left to right) and the underwing tanks between them.
    for pivot, x in (('Propeller', -4.5), ('Propeller_2', -2.4), ('Propeller_3', 2.4), ('Propeller_4', 4.5)):
        _turboprop(a, x, wing.le(abs(x)) - 1.9, .9, pivot, wing.te(abs(x)), 1 if x > 0 else -1)
    tanks = a.part('Tanks', 'Team')
    pylons = a.part('Pylons', 'Armor')
    for s in (-1, 1):
        x = s * 3.45
        zb = wing.bottom(3.45)
        tanks.lathe([(0, 0), (.14, .25), (.26, .8), (.26, 2.2), (.16, 2.85), (.04, 3.1)], loc=(x, -2.2, zb - .4),
                    rot=BACKWARD, seg=12)
        _pylon(pylons, x, -1.2, .3, zb + .05, zb - .15, w=.08)
    # Upswept tail: tailplane with elevators and de-icing boots, the tall fin with its rudder.
    stab = Planform(.2, 3.35, 4.8, 5.55, 1.5, .85, .14, .07, .83)
    for frame in (RIGHT, LEFT):
        _wing(body, moving, stab, frame, cs=[(.4, 3.2, .68)], bevel=0)
        _skin_panel(boots, stab, frame, .4, 3.2, 0, .1)
    fin = Planform(0, 3.3, 4.25, 5.75, 2.3, 1.15, .2, .1)
    _wing(body, moving, fin, _upright(0, .76, 0), cs=[(.3, 3.1, .66)], lower=1.0)
    a.part('Beacon', 'TeamGlow').sphere(.06, loc=(0, 5.95, 4.08), seg=8, rings=5)
    # The left-side battery, front to back: 25 mm gatling, 40 mm cannon, 105 mm howitzer.
    guns = a.part('Guns', 'Steel')
    ports = a.part('Gun_ports', 'Armor')
    at, rot = _side_gun((-.97, -3.3, .0))                                                     # 25 mm gatling
    ports.box((.16, .5, .42), loc=(-.95, -3.3, .02), bevel=.03, seg=1)
    guns.cyl(.08, .14, loc=at(.1), rot=rot, seg=10, bevel=0)
    for k in range(5):
        ang = k * math.tau / 5
        off = Vector((0, math.cos(ang) * .05, math.sin(ang) * .05))
        guns.cyl(.02, .72, loc=tuple(Vector(at(.5)) + off), rot=rot, seg=5, bevel=0)
    guns.cyl(.075, .06, loc=at(.8), rot=rot, seg=10, bevel=0)
    a.pivot('Muzzle_mg', at(.89))
    at, rot = _side_gun((-.97, .3, .05))                                                      # 40 mm cannon
    ports.box((.18, .7, .5), loc=(-.95, .3, .07), bevel=.03, seg=1)
    guns.cyl(.085, .36, loc=at(.2), rot=rot, seg=10, bevel=.01, bseg=1)
    guns.cyl(.065, 1.0, loc=at(.6), rot=rot, seg=10, bevel=0)
    guns.cyl(.09, .2, r2=.06, loc=at(1.12), rot=rot, seg=10, bevel=0)
    a.pivot('Muzzle_gun', at(1.24))
    at, rot = _side_gun((-.97, 2.85, .02))                                                    # 105 mm howitzer
    ports.box((.22, 1.0, .72), loc=(-.94, 2.85, .05), bevel=.04, seg=1)
    guns.cyl(.13, .5, loc=at(.25), rot=rot, seg=12, bevel=.015, bseg=1)
    guns.cyl(.085, 1.5, loc=at(.85), rot=rot, seg=12, bevel=0)
    a.part('Howitzer_brake', 'Undercarriage').box((.2, .28, .24), loc=at(1.62), rot=(0, -.14, 0), bevel=.03, seg=1)
    a.pivot('Muzzle_main', at(1.76))
    # Sensor turrets: a ball under the nose and another behind the left gear sponson.
    sensor = a.part('Sensor', 'Glass')
    for (x, y, z), rr in (((-.5, -4.7, -.98), .24), ((-.66, 2.45, -.82), .18)):
        armor.cyl(rr * .45, .2, loc=(x, y, z + rr * .9), seg=10, bevel=0)
        armor.sphere(rr, loc=(x, y, z), seg=12, rings=8)
        sensor.cyl(rr * .42, .04, loc=(x - rr + .012, y, z - rr * .15), rot=ACROSS, seg=10, bevel=0)
        sensor.cyl(rr * .2, .04, loc=(x - rr * .8 + .01, y - rr * .55, z + rr * .1), rot=(0, R90, .6), seg=8, bevel=0)


# name: (builder, Asset options). They fly: no ground occlusion or grime.
BUILDERS = {
    'heavy_bomber': (heavy_bomber, dict(ao_distance=.9, ground=False)),
    'stealth_bomber': (stealth_bomber, dict(ao_distance=.8, ground=False)),
    'sky_gunship': (sky_gunship, dict(ao_distance=.9, ground=False)),
}
