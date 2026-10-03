"""Prompt 35 wave 7 (lane C): the aerial tanker rebuilt from scratch (spec: Tools/blender/specs/aerial_tanker.json).

An Ilyushin Il-78M Midas (no sheet row; the def's modelSize 19.8 x 22.62 x 5.7 m fits its 46.6 m length, 50.5 m span
and T-tail at about 0.43 x real): the round fuselage with the glazed navigator's nose under the cockpit windows, the
main gear sponsons on the lower sides with the flare dispensers, the cargo ramp lines under the upswept rear and the
tail gunner's station at its end (`Muzzle_gun`, kept from the old file), the high swept wing with anhedral, its flap
track fairings and tip lights, four turbofans on pylons (intake lips, nacelles, nozzles with the reverser cascades),
the T-tail with the swept fin and the tailplane on top, and the three UPAZ refuelling pods (two under the outer wings,
one on the rear fuselage's left side) with their ram-air turbines, hoses and drogues.

Runtime nodes kept: `Muzzle_gun`, `Point_exhaust`, `Point_fire` (the wrappers add `Part_wing` and `Mount_Flare_*`).
Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
R = 1.02                     # fuselage half width
WZ = 1.0                     # wing root height
SPAN = 11.3                  # half span
ENG = (3.7, 6.5)             # engine stations (x)


def _fuselage(a):
    body = a.part('Fuselage', 'Team')
    # Stations (y, half width, half height, centre z): the nose under the cockpit, the long round barrel, the upswept
    # rear rising to the tail turret.
    st = [(-9.9, .12, .14, -.15), (-9.75, .45, .5, -.12), (-9.45, .7, .78, -.06), (-9.0, .88, .95, -.02),
          (-8.3, .98, 1.04, 0), (-7.0, R, 1.06, 0), (3.0, R, 1.06, 0), (5.0, .96, .96, .12), (6.8, .78, .74, .32),
          (8.3, .55, .5, .52), (9.3, .36, .34, .66), (9.75, .22, .22, .72)]
    C.section_loft(body, [(y, C.ellipse_half(w, h, zc, 14)) for y, w, h, zc in st])
    # The glazed navigator's nose (lower) and the cockpit windows (upper), the radome under the chin.
    gl = a.part('Glass', 'Glass')
    k.lathe(gl, [(0, 0), (.32, .06), (.42, .2), (.44, .32)], loc=(0, -9.62, -.32), rot=K.FORWARD, seg=12)
    for s in (-1, 1):
        for j in range(3):
            gl.box((.02, .3, .2), loc=(s * (.55 + j * .1), -9.05 + j * .32, .62 - j * .02), rot=(0, s * .55, 0),
                   bevel=0)
        gl.box((.02, .5, .3), loc=(s * .78, -8.6, -.15), rot=(0, s * .25, 0), bevel=0)        # navigator's side panes
    gl.box((.7, .02, .22), loc=(0, -9.32, .72), rot=(-.9, 0, 0), bevel=0)
    k.lathe(a.part('Radome', 'Armor'), [(0, 0), (.3, .1), (.42, .35), (.44, .7)], loc=(0, -9.15, -.66),
            rot=K.FORWARD, seg=12)
    # The main gear sponsons along the lower sides, the flare dispensers on their rear ends.
    sp = a.part('Sponsons', 'Team')
    for s in (-1, 1):
        k.extrude(sp, [(-2.6, -1.0), (2.6, -1.0), (3.2, -.65), (2.8, -.3), (-2.8, -.3), (-3.2, -.65)], .5,
                  loc=(s * .86, 0, 0), axis='X', chamfer=.08, corner=.06)
        K.flare_dispenser(a, (s * 1.12, 2.85, -.62), normal=(s, .3, -.3), cols=4, rows=2, cell=.09)
    # Panels: the crew door, the cargo ramp and its doors' lines, the Team band, beacons, aerials.
    pn = a.part('Panels', 'Armor')
    pn.box((.02, .5, .9), loc=(1.03, -7.5, -.1), bevel=0)
    for s in (-1, 1):
        pn.box((.02, 2.4, .03), loc=(s * .55, 7.2, -.06 + .28), rot=(-.3, 0, s * .0), bevel=0)
        a.part('Team_band', 'Team').box((.02, 6.0, .22), loc=(s * 1.02, -2.0, .35), bevel=0)
    pn.box((1.0, 2.6, .02), loc=(0, 7.1, -.12), rot=(-.32, 0, 0), bevel=0)
    K.beacon(a, (0, -2.0, 1.06), r=.12)
    K.beacon(a, (0, 1.0, -1.06), r=.12)
    for y in (-6.0, -3.5, 4.5):
        K.blade_antenna(a.part('Antennas', 'Steel'), (0, y, 1.05), h=.35, chord=.3)
    K.blade_antenna(a.part('Antennas', 'Steel'), (0, -5.0, -1.05), h=.3, chord=.25, normal=(0, 0, -1))
    # The tail gunner's station: a glazed turret at the end of the upswept rear (the old file's Muzzle_gun).
    tt = a.part('Tail_turret', 'Armor')
    k.lathe(tt, [(.24, 0), (.24, .2), (.18, .45), (0, .5)], loc=(0, 9.7, .72), rot=K.BACKWARD, seg=10)
    gl.box((.3, .02, .14), loc=(0, 9.95, .85), rot=(.6, 0, 0), bevel=0)
    tt.cyl(.03, .5, loc=(0, 10.3, .62), rot=K.BACKWARD, seg=6, bevel=0)
    a.pivot('Muzzle_gun', (0, 10.56, .62))
    a.pivot('Point_fire', (0, 0, .6))


def _wing(a):
    wing = a.part('Wings', 'Team')
    rings_l, rings_r = [], []
    an = math.radians(-3)
    for f, lead, chord in ((0, -2.1, 4.4), (.12, -1.75, 4.1), (.35, -.65, 3.1), (.6, .55, 2.3), (.85, 1.75, 1.6),
                           (1.0, 2.45, 1.25)):
        x = .4 + (SPAN - .4) * f
        for s, rings in ((1, rings_l), (-1, rings_r)):
            ring = [(s * px, py, pz + math.tan(an) * (SPAN - .4) * f) for px, py, pz in
                    K._foil_ring(lead, chord, .12, x, WZ)]
            rings.append(ring if s > 0 else list(reversed(ring)))
    wing.loft(rings_l, bevel=0)
    wing.loft(rings_r, bevel=0)
    k.block(a.part('Wing_root', 'Team'), (2.0, 4.4, .3), loc=(0, .1, WZ + .05), chamfer=.1)
    # Flap track fairings under the trailing edge, the tip lights.
    fl = a.part('Flaps', 'Armor')
    for s in (-1, 1):
        for x in (2.2, 5.0, 7.8, 9.8):
            f = (x - .4) / (SPAN - .4)
            lead = -2.1 + (2.45 + 2.1) * f
            chord = 4.4 - (4.4 - 1.25) * f
            z = WZ + math.tan(an) * (x - .4) - .1
            fl.box((.18, .9, .16), loc=(s * x, lead + chord - .25, z), bevel=0)
        a.part('Wing_lights', 'Lamp' if s > 0 else 'LavaGlow').box((.12, .2, .08),
                                                                    loc=(s * (SPAN + .02), 2.9, WZ - .6), bevel=0)


def _engines(a):
    an = math.radians(-3)
    for s in (-1, 1):
        for x in ENG:
            f = (x - .4) / (SPAN - .4)
            lead = -2.1 + (2.45 + 2.1) * f
            zw = WZ + math.tan(an) * (x - .4)
            y0 = lead - 1.6
            zc = zw - .85
            k.lathe(a.part('Engines', 'Team'), [(.44, 0), (.5, .3), (.52, 1.2), (.46, 2.0), (.36, 2.4)],
                    loc=(s * x, y0, zc), rot=K.BACKWARD, seg=14, worn=(1, 3))
            k.lathe(a.part('Intakes', 'Steel'), [(.36, -.02), (.46, 0), (.47, .06), (.4, .12)], loc=(s * x, y0, zc),
                    rot=K.BACKWARD, seg=14)
            a.part('Intake_ducts', 'Undercarriage').cyl(.38, .05, loc=(s * x, y0 + .12, zc), rot=K.BACKWARD, seg=14,
                                                        bevel=0)
            k.lathe(a.part('Nozzles', 'Steel'), [(.36, 2.38), (.3, 2.65), (.24, 2.8), (.2, 2.8)],
                    loc=(s * x, y0, zc), rot=K.BACKWARD, seg=12)
            a.part('Nozzle_cascades', 'Undercarriage').cyl(.47, .25, loc=(s * x, y0 + 1.5, zc), rot=K.BACKWARD,
                                                           seg=14, bevel=0)
            K.pylon(a.part('Pylons', 'Armor'), s * x, lead - .2, lead + 1.6, zw - .05, zc + .4, w=.16)
            K.soot(a, (s * x, y0 + 2.9, zc), radius=.6, k=.5)
    a.pivot('Point_exhaust', (ENG[0], -2.1 + 4.55 * (ENG[0] - .4) / (SPAN - .4) + 1.3, WZ - 1.0))


def _tail(a):
    tail = a.part('Tail', 'Team')
    K.fin(tail, (6.1, 3.0), (8.3, 1.7), 3.3, x=0, z0=.9, t=.1)
    # The tailplane on top of the fin (swept, slight anhedral).
    K.wing(tail, (7.9, 1.9), (9.2, .9), 3.8, x0=.15, z=4.2, t=.09, dihedral=math.radians(-4))
    k.block(a.part('Tail_cap', 'Team'), (.4, 2.0, .3), loc=(0, 8.8, 4.2), chamfer=.08)
    rd = a.part('Rudders', 'Armor')
    rd.box((.08, .2, 2.8), loc=(0, 8.95, 2.65), rot=(-.3, 0, 0), bevel=0)
    for s in (-1, 1):
        rd.box((3.0, .2, .05), loc=(s * 1.9, 9.75, 4.07), rot=(0, 0, s * .25), bevel=0)
    K.beacon(a, (0, 8.8, 4.37), r=.1)


def _pods(a):
    """The three UPAZ pods: under both outer wings and on the rear fuselage's left side; hoses and drogues trail."""
    an = math.radians(-3)
    spots = []
    for s in (-1, 1):
        x = s * 9.0
        f = (abs(x) - .4) / (SPAN - .4)
        lead = -2.1 + (2.45 + 2.1) * f
        zw = WZ + math.tan(an) * (abs(x) - .4)
        K.pylon(a.part('Pylons', 'Armor'), x, lead + .1, lead + 1.1, zw - .05, zw - .45, w=.12)
        spots.append((x, lead - .4, zw - .65))
    spots.append((1.25, 4.5, -.55))
    k.extrude(a.part('Pylons', 'Armor'), [(4.3, -.7), (6.0, -.7), (5.8, -.3), (4.5, -.3)], .25, loc=(1.1, 0, 0),
              axis='X', chamfer=.03)
    for x, y, z in spots:
        k.lathe(a.part('Pods', 'Team'), [(0, -.05), (.18, .1), (.3, .5), (.32, 1.5), (.26, 2.3), (.16, 2.6)],
                loc=(x, y, z), rot=K.BACKWARD, seg=12, worn=(2,))
        tb = a.part('Pod_turbines', 'Steel')
        for j in range(3):
            u = j * math.tau / 3
            tb.box((.03, .02, .4), loc=(x + math.cos(u) * .2, y - .12, z + math.sin(u) * .2), rot=(0, u, 0), bevel=0)
        a.part('Hoses', 'Rubber').tube([(x, y + 2.6, z), (x, y + 3.6, z - .25), (x, y + 4.3, z - .5)], .05, seg=6)
        k.lathe(a.part('Drogues', 'Steel'), [(.06, 0), (.12, .1), (.35, .55), (.33, .6)], loc=(x, y + 4.3, z - .5),
                rot=K.BACKWARD, seg=12, caps=(False, False))


def aerial_tanker(a, detail=False):
    """The aerial tanker: see the module docstring."""
    _fuselage(a)
    _wing(a)
    _engines(a)
    _tail(a)
    _pods(a)
    k.clean(a)


BUILDERS = {
    'aerial_tanker': (aerial_tanker, dict(ao_distance=.8, ao_strength=.15, ground=False)),
}
