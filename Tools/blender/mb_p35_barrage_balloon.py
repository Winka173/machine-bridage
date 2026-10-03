"""Prompt 35 wave 3 (lane B): the radar aerostat rebuilt from scratch (spec: Tools/blender/specs/barrage_balloon.json).

A tethered radar aerostat in the style of the US Army JLENS (Strings unit.barrage_balloon; the def's modelSize
9.0 x 4.0 x 16.0 m: the envelope rides above the base at the top of that box): the streamlined white envelope with
its three tail fins in an inverted Y, the ballonet seams, the radar radome bulging under the forward belly with its
equipment gondola, the rigging lines meeting at the confluence point and the tether running down to the mobile
mooring station: a turning platform on outriggers with the mooring mast, the tether winch and its drum, the operator
shelter with antennas, generator, and a wire fence round the site; Team bands round the envelope and the shelter.

Its own body: no shape is shared with the command airship or the C-RAM family.
Old part names kept: `Envelope`, `Fins`, `Cable`, `Winch`, `Drum`, `Pad`, `Team_bands`, `Tyres`, `Hubs`.
Metres, +Z up, -Y front (the nose), +X left.
"""
import math
import random

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
EZ = 13.8               # the envelope's axis height
EL = 8.6                # the envelope's length
ER = 1.85               # its greatest radius
EY0 = -4.3              # the nose


def _profile():
    """(radius, y) along the envelope: a blunt nose, the greatest girth at a third, a long taper to the tail."""
    pts = []
    for f in (0, .02, .06, .12, .2, .3, .4, .52, .64, .76, .87, .95, 1.0):
        if f < .33:
            r = ER * math.sqrt(max(0, 1 - ((.33 - f) / .33) ** 2))
        else:
            r = ER * (1 - ((f - .33) / .67) ** 1.6 * .88)
        pts.append((max(r, .02), EY0 + f * EL))
    return pts


def _envelope(a):
    prof = _profile()
    # A lathe round the Y axis: the profile's (radius, axial position) with the axis turned onto Y.
    env = a.part('Envelope', 'PlasterWhite')
    k.lathe(env, [(r, y - EY0) for r, y in prof], loc=(0, EY0, EZ), rot=(-R90, 0, 0), seg=20)
    seams = a.part('Envelope_seams', 'Concrete')
    for u in (math.radians(d) for d in (40, 140, 220, 320)):
        pts = [(math.cos(u) * (r + .015), y, EZ + math.sin(u) * (r + .015)) for r, y in prof[1:-1]]
        seams.tube(pts, .025, seg=3)
    bands = a.part('Team_bands', 'Team')
    for f in (3, 8):
        r, y = prof[f]
        bands.cyl(r + .03, .35, loc=(0, y, EZ), rot=(R90, 0, 0), seg=20, bevel=0)
    # Three tail fins in an inverted Y (one up, two down at 120 degrees), each with its trailing rudder edge.
    fins = a.part('Fins', 'PlasterWhite')
    for ang in (R90, R90 + math.tau / 3, R90 - math.tau / 3):
        y0 = EY0 + EL * .7
        root_r = prof[9][0]
        prof2 = [(y0, root_r * .9), (EY0 + EL + .2, root_r * .4), (EY0 + EL + .25, root_r * .4 + 1.6),
                 (y0 + 1.2, root_r * .9 + 1.4)]
        verts, faces = [], []
        c, s = math.cos(ang), math.sin(ang)
        for t in (-.06, .06):
            for (y, rr) in prof2:
                verts.append((c * rr - s * t, y, EZ + s * rr + c * t))
        faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
        fins.mesh(verts, faces)
        a.part('Fin_edges', 'Team').box((.14, .5, 1.5), loc=(c * (root_r * .4 + .85), EY0 + EL + .02,
                                                             EZ + s * (root_r * .4 + .85)),
                                        rot=(0, -(ang - R90), 0), bevel=0)
    # The radome under the forward belly and its gondola, the confluence rigging, the tether.
    rad = a.part('Radome', 'Fuel')
    rad.sphere((1.0, 1.6, .7), loc=(0, EY0 + 2.6, EZ - ER + .1), seg=14, rings=7)
    k.block(a.part('Gondola', 'Armor'), (.7, 1.2, .35), loc=(0, EY0 + 4.2, EZ - ER * .92 - .25), chamfer=.06)
    conf = (0, EY0 + 3.3, EZ - ER - 1.6)
    rig = a.part('Rigging', 'Undercarriage')
    for (dx, dy) in ((-.9, -1.2), (.9, -1.2), (-1.1, .6), (1.1, .6), (0, 2.2)):
        rig.tube([conf, (dx, EY0 + 3.3 + dy, EZ - math.sqrt(max(0, ER * ER - dx * dx)) * .9)], .015, seg=3)
    return conf


def _station(a, conf, rng):
    """The mobile mooring station: platform on outriggers, mooring mast, winch and drum, the tether up."""
    pad = a.part('Pad', 'Armor')
    k.lathe(pad, [(1.75, 0), (1.75, .25), (1.65, .32), (0, .32)], loc=(0, .4, .15), seg=18, worn=(1,))
    for i in range(4):
        u = i * R90 + math.pi / 4
        a.part('Outriggers', 'Steel').limb((math.cos(u) * 1.4, .4 + math.sin(u) * 1.4, .3),
                                           (math.cos(u) * 1.9, .4 + math.sin(u) * 1.75, .06), .12, .12, bevel=0)
        a.part('Jack_pads', 'Wood').box((.35, .35, .06), loc=(math.cos(u) * 1.9, .4 + math.sin(u) * 1.75, .03),
                                       bevel=0)
    # The carrier's wheels under the platform (two axles), the mast, the winch drum.
    for y in (-.6, 1.4):
        for s in (-1, 1):
            P.tread_wheel(a, (s * 1.1, y, .32), .3, .22, s, seg=12, rim_seg=6, rim='Hubs')
    mast = a.part('Mast', 'Steel')
    for (dx, dy) in ((-.15, -.15), (.15, -.15), (.15, .15), (-.15, .15)):
        mast.limb((dx * 2, .4 + dy * 2, .47), (dx * .6, .4 + dy * .6, 4.2), .05, .05, bevel=0)
    k.lathe(mast, [(.25, 0), (.25, .12), (.1, .2), (0, .2)], loc=(0, .4, 4.2), seg=10)
    k.lathe(a.part('Drum', 'Team'), [(.45, -.5), (.45, .5)], loc=(0, 1.2, .95), rot=(0, R90, 0), seg=14)
    for s in (-1, 1):
        a.part('Drum_flanges', 'Steel').cyl(.6, .05, loc=(s * .52, 1.2, .95), rot=(0, R90, 0), seg=14, bevel=0)
    k.block(a.part('Winch', 'Armor'), (.7, .6, .55), loc=(0, 1.9, .75), chamfer=.04)
    a.part('Cable', 'Undercarriage').tube([(0, 1.2, 1.4), (0, .45, 4.35), conf], .03, seg=4)


def _site(a, rng):
    # The operator shelter (a short container) at the rear with its antennas and the generator.
    sx, sy = 0, 3.55
    k.block(a.part('Shelter', 'Team'), (2.2, 1.3, 1.3), loc=(sx, sy, .65), chamfer=.04)
    ribs = a.part('Shelter_ribs', 'Armor')
    for j in range(7):
        ribs.box((.06, 1.32, 1.2), loc=(sx - .9 + j * .3, sy, .65), bevel=0)
    K.door(a, (sx + 1.11, sy, 0), size=(.7, 1.1), normal=(1, 0, 0))
    ant = a.part('Antennas', 'Steel')
    for x in (-.8, .7):
        K.whip_antenna(ant, (sx + x, sy + .3, 1.3), h=1.4, r=.02, lean=.05)
    K.dish(a.part('Dish', 'Steel'), a.part('Dish_feed', 'Undercarriage'), (sx - .3, sy - .2, 1.6), r=.35,
           normal=(0, -1, 1), seg=12)
    a.part('Team_bands', 'Team').box((2.22, .02, .2), loc=(sx, sy - .66, 1.0), bevel=0)
    k.block(a.part('Generator', 'Armor'), (.7, .9, .6), loc=(-1.45, -2.6, .3), chamfer=.04)
    a.part('Generator_stack', 'Steel').cyl(.05, .4, loc=(-1.6, -2.4, .8), seg=8, bevel=0)
    a.part('Kit_cables', 'Undercarriage').tube([(-1.45, -2.1, .1), (-.9, -.8, .05), (-.4, .1, .3)], .025, seg=4)
    # The wire fence round the site (gate role "walls"), posts and strands, a sign.
    fence = a.part('Fence', 'Steel')
    corners = [(-1.95, -4.3), (1.95, -4.3), (1.95, 4.35), (-1.95, 4.35)]
    for i in range(4):
        p, q = corners[i], corners[(i + 1) % 4]
        n = max(1, int(math.hypot(q[0] - p[0], q[1] - p[1]) / 1.4))
        for j in range(n):
            f = j / n
            fence.box((.05, .05, 1.4), loc=(p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f, .7), bevel=0)
        for z in (.45, 1.0, 1.35):
            fence.tube([(p[0], p[1], z), (q[0], q[1], z)], .008, seg=3)
    a.part('Signs', 'Hazard').box((.5, .02, .35), loc=(.6, -4.31, .9), bevel=0)
    for i in range(6):
        K.dust(a, (rng.uniform(-1.8, 1.8), rng.uniform(-4, 4), 0), radius=1.2, k=.22)


def barrage_balloon(a):
    """The radar aerostat: see the module docstring."""
    rng = random.Random(3651)
    conf = _envelope(a)
    _station(a, conf, rng)
    _site(a, rng)
    k.clean(a)


BUILDERS = {
    'barrage_balloon': (barrage_balloon, dict(ao_distance=.8, grime_height=.6)),
}
