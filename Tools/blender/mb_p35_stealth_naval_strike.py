"""Prompt 35 wave 6 (lane B): the stealth naval strike aircraft rebuilt from scratch (spec: Tools/blender/specs/stealth_naval_strike.json).

An A-12 Avenger II-class carrier flying wing (the def's modelSize 8.4 x 21 x 1.5 m): the isosceles "flying Dorito"
planform, one airfoil loft from tip to tip with the straight trailing edge and the clipped tips, the carrier
fold hinge lines outboard, the blended centre body over the crew compartment and weapon bays (the fuselage role),
the tandem two-seat canopy with its frames, the two intakes under the leading edge either side of the nose, the
flat exhaust troughs over the trailing edge (the aft centre section is the tail role), the elevon and spoiler
seams along the trailing edge; underneath the two weapon bays with their doors and racks, the bomb load
semi-recessed in them (`Bombs` > bomb bodies, `Muzzle_missile`), two standoff missiles on pylons under the wings
(`Muzzle_rocket`, `Muzzle_rocket.001`), flush flare dispensers, the refuelling probe, wing lights and Team
markings. Jet rule: no insets or panel greebles on the skin.

Its own wing (not stealth_bomber's sawtooth B-2 loft: 60 % shared before). Runtime nodes kept: `Muzzle_missile`,
`Muzzle_rocket`, `Muzzle_rocket.001`, `Bombs`, `Point_exhaust`, `Point_fire`; the wrapper adds `Part_wing` (the left
wing along its whole length); old part names `Wing`, `Canopy`, `Canopy_frames`, `Intakes`, `Exhaust_trough`,
`Exhaust_glow`, `Bay_doors`, `Fold_seam`, `Standoff_missile`, `Bomb_*`, `Wing_lights`. Metres, +Z up, -Y front,
+X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
APEX, TE = -4.2, 4.16
TIP_X, TIP_LE = 10.1, 3.3


def le_y(x):
    """The leading edge's y at span position |x| (straight from the apex to the clipped tip)."""
    return APEX + (TIP_LE - APEX) * min(1.0, abs(x) / TIP_X)


def _wing(a):
    w = a.part('Wing', 'Team')
    K.wing(w, (APEX, TE - APEX), (TIP_LE, TE - TIP_LE), TIP_X, x0=0.0, z=0.0, t=.085, dihedral=0.0,
           crank=(.3, le_y(.3 * TIP_X), TE - le_y(.3 * TIP_X)))
    # The clipped tips' edge caps, the fold hinge lines, the elevon and spoiler seams on the trailing edge.
    seam = a.part('Fold_seam', 'Undercarriage')
    for s in (-1, 1):
        xf = s * 6.2
        y0 = le_y(6.2)
        seam.box((.04, TE - y0 - .1, .015), loc=(xf, (y0 + TE) / 2, .1 - .05 * abs(xf) / TIP_X), bevel=0)
        for x0, x1 in ((1.6, 4.0), (4.2, 6.0), (6.4, 8.6)):
            seam.box((x1 - x0, .03, .012), loc=(s * (x0 + x1) / 2, TE - .7, .07), bevel=0)
            seam.box((.03, .7, .012), loc=(s * x0, TE - .35, .07), bevel=0)
        a.part('Wing_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.08, .14, .05), loc=(s * (TIP_X - .1), 3.6, 0),
                                                                          bevel=0)
        a.part('Team_band', 'Team').box((1.2, .5, .012), loc=(s * 7.8, 3.3, .09), rot=(0, 0, s * .1), bevel=0)


def _body(a):
    """The blended centre body (fuselage), the canopy, intakes, exhaust troughs, the aft centre section (tail)."""
    body = a.part('Fuselage', 'Team')
    rings = [[(0, APEX + .05, .05)]]
    for y, w, top in ((-3.6, .5, .28), (-2.8, .9, .45), (-1.6, 1.25, .55), (.0, 1.4, .52), (1.6, 1.4, .42),
                      (3.0, 1.2, .3), (TE - .25, 1.0, .16)):
        rings.append([(-w, y, .02), (-w * .6, y, top * .85), (0, y, top), (w * .6, y, top * .85), (w, y, .02),
                      (w * .6, y, -.22), (0, y, -.28), (-w * .6, y, -.22)])
    k.sharp_loft(body, rings, chamfer=.02)
    can = a.part('Canopy', 'Glass')
    can.loft([[(0, -3.3, .4)],
              [(-.22, -2.9, .5), (.22, -2.9, .5), (.15, -2.9, .66), (-.15, -2.9, .66)],
              [(-.26, -2.0, .6), (.26, -2.0, .6), (.18, -2.0, .86), (-.18, -2.0, .86)],
              [(-.24, -1.2, .58), (.24, -1.2, .58), (.16, -1.2, .7), (-.16, -1.2, .7)],
              [(0, -.8, .58)]])
    fr = a.part('Canopy_frames', 'Armor')
    for y, z in ((-2.9, .68), (-2.0, .88), (-1.2, .72)):
        fr.tube([(-.24, y, z - .14), (0, y, z), (.24, y, z - .14)], .016, seg=4)
    # Two intakes under the leading edge either side of the nose, their dark ducts.
    for s in (-1, 1):
        x = s * 1.25
        y = le_y(1.25) + .55
        k.extrude(a.part('Intakes', 'Armor'), [(-.38, -.12), (.38, -.12), (.32, .08), (-.32, .08)], .9,
                  loc=(x, y + .3, -.16), axis='Y', chamfer=.02)
        a.part('Intake_dark', 'Undercarriage').box((.6, .02, .14), loc=(x, y - .16, -.17), bevel=0)
    # The aft centre section and the two flat exhaust troughs on top of it.
    k.extrude(a.part('Tail_section', 'Armor'), [(-1.3, -.04), (1.3, -.04), (1.1, .14), (-1.1, .14)], 1.2,
              loc=(0, TE - .6, .0), axis='Y', chamfer=.02)
    for s in (-1, 1):
        x = s * .62
        k.extrude(a.part('Exhaust_trough', 'Undercarriage'), [(-.42, 0), (.42, 0), (.38, .08), (-.38, .08)], 1.4,
                  loc=(x, TE - .7, .12), axis='Y', chamfer=.01)
        a.part('Exhaust_glow', 'LavaGlow').box((.66, .02, .05), loc=(x, TE + .02, .17), bevel=0)
        K.soot(a, (x, TE, .15), radius=.8, k=.35)
    a.pivot('Point_exhaust', (2.0, 4.0, .2))
    a.pivot('Point_fire', (0, .5, .7))
    # The refuelling probe, blade antennas.
    a.part('Probe', 'Steel').tube([(.35, -3.0, .38), (.45, -3.9, .3)], .025, seg=5)
    for y, z, n in ((-.4, .5, (0, 0, 1)), (2.2, .38, (0, 0, 1)), (.6, -.3, (0, 0, -1))):
        K.blade_antenna(a.part('Antennas', 'Steel'), (0, y, z), h=.12, chord=.14, normal=n)


def _stores(a):
    # Two weapon bays either side of the centre line: doors (closed edges), racks, the bomb load half out.
    doors = a.part('Bay_doors', 'Armor')
    racks = a.part('Racks', 'Undercarriage')
    for s in (-1, 1):
        x = s * .62
        doors.box((.5, 2.6, .02), loc=(x, .5, -.29), bevel=0)
        racks.box((.08, 2.2, .06), loc=(x, .5, -.27), bevel=0)
    b = a.pivot('Bombs', (0, 0, 0))
    for s in (-1, 1):
        for dy in (-.6, .9):
            k.lathe(a.part('Bomb_bodies', 'Armor', b), [(0, -.75), (.09, -.68), (.14, -.4), (.14, .45), (.1, .65),
                                                        (.06, .72)], loc=(s * .62, .45 + dy, -.42), rot=K.BACKWARD,
                    seg=10, worn=(2,))
            a.part('Bomb_seekers', 'Glass', b).cyl(.05, .02, loc=(s * .62, .45 + dy - .76, -.42), rot=K.FORWARD, seg=6,
                                                   bevel=0)
            a.part('Bomb_bands', 'Hazard', b).cyl(.145, .04, loc=(s * .62, .45 + dy - .2, -.42), rot=K.FORWARD, seg=10,
                                                  bevel=0)
            a.part('Bomb_fuzes', 'Steel', b).cyl(.03, .08, loc=(s * .62, .45 + dy + .78, -.42), rot=K.FORWARD, seg=6,
                                                 bevel=0)
    a.pivot('Muzzle_missile', (0, 0, -.5))
    # Two standoff missiles on pylons under the wings (`Muzzle_rocket` / `.001`).
    for i, s in enumerate((-1, 1)):
        for x, zc, main in ((s * 3.0, -.36, True), (s * 5.4, -.3, False)):
            K.pylon(a.part('Pylons', 'Armor'), x, le_y(abs(x)) + 1.0, le_y(abs(x)) + 2.0, -.05, zc + .13, w=.07)
            y = le_y(abs(x)) + 1.55
            k.lathe(a.part('Standoff_missile', 'Fuel'), [(0, -1.0), (.1, -.85), (.13, -.6), (.13, .8), (.1, 1.0)],
                    loc=(x, y, zc), rot=K.BACKWARD, seg=10, worn=(2,))
            fins = a.part('Standoff_fins', 'Steel')
            fins.box((.6, .25, .015), loc=(x, y + .4, zc), bevel=0)
            fins.box((.015, .25, .4), loc=(x, y + .9, zc), bevel=0)
            if main:
                a.pivot(K.name('Muzzle_rocket', i), (x, 1.28, -.32))
    # Flush flare dispensers under the outer wing roots.
    for s in (-1, 1):
        K.flare_dispenser(a, (s * 2.2, 3.2, -.09), normal=(0, 0, -1), cols=3, rows=2, cell=.07)


def _edges(a):
    """Flush edge treatments (paint, no relief): the dark radar-absorbent bands along the leading and trailing
    edges, the sawtooth outlines of the access panels and gear doors, the walkway lines, wing-root markings."""
    ram = a.part('Ram_edges', 'Undercarriage')
    for s in (-1, 1):
        # Leading-edge band on the top skin, in segments following the edge.
        for i in range(10):
            xa, xb = 1.0 + i * .9, 1.0 + (i + 1) * .9
            ya, yb = le_y(xa), le_y(xb)
            za = .085 * (TE - ya) * .38 * (1 - .0 * xa) + .01
            ram.mesh([(s * xa, ya + .12, za * .9), (s * xb, yb + .12, za * .9), (s * xb, yb + .5, za),
                      (s * xa, ya + .5, za)], [(0, 1, 2, 3) if s > 0 else (3, 2, 1, 0)])
        ram.mesh([(s * 1.3, TE - .25, .05), (s * 9.6, TE - .25, .03), (s * 9.6, TE - .02, .015),
                  (s * 1.3, TE - .02, .02)], [(0, 1, 2, 3) if s > 0 else (3, 2, 1, 0)])
    saw = a.part('Panel_lines', 'Armor')
    for s in (-1, 1):
        for (xc, yc, w, d) in ((2.4, .6, 1.0, 1.4), (3.6, 1.8, .9, 1.1), (4.9, 2.4, .8, .9), (2.2, 2.6, .8, .7),
                               (7.2, 3.1, .7, .5)):
            z = .085 * (TE - le_y(xc)) * .3
            for k_ in range(4):
                x0 = xc - w / 2 + k_ * w / 4
                saw.mesh([(s * x0, yc - d / 2, z), (s * (x0 + w / 8), yc - d / 2 - .1, z),
                          (s * (x0 + w / 4), yc - d / 2, z), (s * (x0 + w / 4), yc - d / 2 + .04, z),
                          (s * x0, yc - d / 2 + .04, z)], [(0, 1, 2, 3, 4) if s > 0 else (4, 3, 2, 1, 0)])
            for xx in (xc - w / 2, xc + w / 2):
                saw.box((.04, d, .01), loc=(s * xx, yc, z), bevel=0)
            saw.box((w, .04, .01), loc=(s * xc, yc + d / 2, z), bevel=0)
    walk = a.part('Walkways', 'Medical')
    for s in (-1, 1):
        walk.box((.03, 2.2, .01), loc=(s * 1.55, -.5, .42), rot=(0, s * -.1, 0), bevel=0)
        walk.box((.03, 2.2, .01), loc=(s * 1.85, -.5, .38), rot=(0, s * -.1, 0), bevel=0)


def top_z(x, y):
    """The wing's upper skin height at (x, y) (the kit's airfoil, t = 0.085 of the chord)."""
    le = le_y(x)
    chord = TE - le
    u = min(1.0, max(0.0, (y - le) / chord))
    pts = ((0, 0), (.2, .55), (.45, 1.0), (.675, .8), (1.0, 0))
    for (u0, v0), (u1, v1) in zip(pts, pts[1:]):
        if u <= u1:
            v = v0 + (v1 - v0) * (u - u0) / (u1 - u0)
            break
    return v * .085 * chord * .5


def _tape(a):
    """Radar-absorbent tape over the panel seams (flush paint lines on the skin): chordwise lines every metre and
    three spanwise lines, each laid in short segments on the airfoil."""
    tape = a.part('Ram_tape', 'Armor')
    w = .05

    def strip(p0, p1, n):
        for i in range(n):
            xa = p0[0] + (p1[0] - p0[0]) * i / n
            ya = p0[1] + (p1[1] - p0[1]) * i / n
            xb = p0[0] + (p1[0] - p0[0]) * (i + 1) / n
            yb = p0[1] + (p1[1] - p0[1]) * (i + 1) / n
            dx, dy = xb - xa, yb - ya
            L = math.hypot(dx, dy) or 1
            nx, ny = -dy / L * w / 2, dx / L * w / 2
            za, zb = top_z(xa, ya) + .012, top_z(xb, yb) + .012
            quad = [(xa - nx, ya - ny, za), (xb - nx, yb - ny, zb), (xb + nx, yb + ny, zb), (xa + nx, ya + ny, za)]
            tape.mesh(quad, [(0, 1, 2, 3)])
    for s in (-1, 1):
        for i in range(12):
            x = s * (1.7 + i * .65)
            y0 = le_y(abs(x)) + .3
            strip((x, y0), (x, TE - .3), 6)
        for f in (.22, .38, .55, .7, .85):
            x0, x1 = 1.6, 9.0
            strip((s * x0, le_y(x0) + f * (TE - le_y(x0))), (s * x1, le_y(x1) + f * (TE - le_y(x1))), 12)


def stealth_naval_strike(a):
    """The stealth naval strike aircraft: see the module docstring."""
    K.suffixed(a)
    _wing(a)
    _body(a)
    _stores(a)
    _edges(a)
    _tape(a)
    P.merge_parts(a, {'Probe': 'Antennas', 'Intake_dark': 'Fold_seam', 'Standoff_fins': 'Antennas'})
    k.clean(a)


BUILDERS = {
    'stealth_naval_strike': (stealth_naval_strike, dict(ao_distance=.6, ground=False)),
}
