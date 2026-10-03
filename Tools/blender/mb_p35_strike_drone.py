"""Prompt 35 wave 4 (lane C): the strike drone rebuilt from scratch (spec: Tools/blender/specs/strike_drone.json).

An MQ-9 Reaper (the def's modelSize 4.25 x 8.04 x 1.24 m, 0.4 x the real one): the fuselage with the bulbous
satcom nose, the EO/IR turret under the chin, the very long straight wing (twice the fuselage) with its flaps and
ailerons, the Y tail (two fins canted up, the ventral fin down), the three-bladed pusher propeller (`Propeller`)
behind the turboprop bay with its dorsal intake, ventral cooler scoop and the exhaust stubs; under the wings the
outer stations with twin Hellfire rails and the inner stations with GBU-39 small-diameter bombs on their racks;
satcom and blade aerials, navigation lights. Flying (gear retracted).

Runtime nodes kept: `Propeller` (+ `Propeller_blades`, `Propeller_hub`), `Muzzle_missile`, `Muzzle_missile.001`,
`Muzzle_rocket`, `Muzzle_rocket.001`, `Point_exhaust`, `Point_fire`. Metres, +Z up, -Y front, +X left. The real
Reaper has no flare dispenser (spec "merged" for the gate's jet role).
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WING_Z = .06


def _fuselage(a):
    body = a.part('Fuselage', 'Team')
    st = [(-2.12, .04, .04, .02), (-2.06, .12, .13, .04), (-1.95, .19, .22, .07), (-1.78, .23, .29, .1),
          (-1.55, .245, .31, .1), (-1.25, .24, .29, .08), (-.9, .225, .26, .05), (-.5, .21, .23, .02),
          (0.0, .2, .21, 0.0), (.5, .185, .19, 0.0), (1.0, .16, .165, 0.0), (1.4, .125, .13, .0),
          (1.7, .09, .095, 0.0), (1.9, .06, .06, 0.0)]
    C.section_loft(body, [(y, C.ellipse_half(w, h, zc, 14)) for y, w, h, zc in st])
    # The EO/IR turret under the chin, its window.
    a.part('Sensor', 'Armor').cyl(.06, .08, loc=(0, -1.72, -.22), seg=12, bevel=0)
    k.lathe(a.part('Sensor_ball', 'Armor'), [(0, -.13), (.08, -.12), (.115, -.06), (.12, 0), (.1, .06), (.05, .08),
                                            (0, .085)], loc=(0, -1.72, -.33), seg=20)
    a.part('Glass', 'Glass').box((.09, .02, .07), loc=(0, -1.84, -.34), bevel=0)
    # The turboprop bay: the dorsal intake, the ventral cooler scoop, the exhaust stubs.
    K.intake(a.part('Intakes', 'Team'), a.part('Intake_ducts', 'Undercarriage'), (0, .7, .2), .16, .07, .3,
             facing=(0, -1, .25), lip=.01)
    K.intake(a.part('Intakes', 'Team'), a.part('Intake_ducts', 'Undercarriage'), (0, .2, -.2), .14, .06, .28,
             facing=(0, -1, -.25), lip=.01)
    for s in (-1, 1):
        k.lathe(a.part('Exhausts', 'Steel'), [(.03, 0), (.035, .1), (.028, .14)], loc=(s * .15, 1.4, .02),
                rot=(R90 + .2, 0, s * .7), seg=8)
    K.soot(a, (0, 1.6, .02), radius=.3, k=.4)
    a.pivot('Point_exhaust', (0, 1.6, .05))
    a.pivot('Point_fire', (0, .3, .1))
    # Aerials and access panels.
    k.lathe(a.part('Antennas', 'Armor'), [(.1, 0), (.08, .03), (0, .04)], loc=(0, -.6, .225), seg=14)
    for y in (-.2, .3):
        K.blade_antenna(a.part('Antennas', 'Steel'), (0, y, .21), h=.1, chord=.09)
    K.blade_antenna(a.part('Antennas', 'Steel'), (0, -.9, -.24), h=.08, chord=.08, normal=(0, 0, -1))
    pn = a.part('Panels', 'Armor')
    for y in (-1.0, -.3, .4):
        pn.box((.18, .3, .01), loc=(0, y, .22 - abs(y) * .01), bevel=0)
    for s in (-1, 1):
        a.part('Team_band', 'Team').box((.01, .9, .06), loc=(s * .2, -.6, .0), bevel=0)


def _wing(a):
    wing = a.part('Wings', 'Team')
    for s in (-1, 1):
        rings = []
        for f, lead, chord in ((0, -.4, .55), (.1, -.4, .54), (.3, -.38, .47), (.5, -.36, .41), (.7, -.34, .35),
                               (.88, -.32, .3), (1.0, -.31, .26)):
            x = .15 + 3.87 * f
            ring = [(s * px, py, pz + math.tan(.02) * 3.87 * f) for px, py, pz in
                    K._foil_ring(lead, chord, .12, x, WING_Z)]
            rings.append(ring if s > 0 else list(reversed(ring)))
        wing.loft(rings, bevel=0)
        cs = a.part('Flaps', 'Armor')
        for x0, x1 in ((.3, 1.3), (1.4, 2.5), (2.6, 3.7)):
            f = (x0 + x1) / 2 / 3.87
            cs.box((x1 - x0, .08, .015), loc=(s * (x0 + x1) / 2, -.4 + (.55 - .29 * f) - .05,
                                             WING_Z + .01 + math.tan(.02) * (x0 + x1) / 2), bevel=0)
        a.part('Wing_lights', 'Lamp' if s > 0 else 'LavaGlow').box((.04, .06, .02), loc=(s * 4.0, -.28, WING_Z + .08),
                                                                    bevel=0)
        a.part('Team_band', 'Team').box((.4, .3, .005), loc=(s * 3.0, -.2, WING_Z + .09), bevel=0)


def _tail(a):
    tail = a.part('Tail', 'Team')
    for s in (-1, 1):
        K.fin(tail, (1.38, .42), (1.62, .2), .6, x=s * .05, z0=.08, t=.1, cant=s * .8)
    K.fin(tail, (1.45, .36), (1.62, .2), -.42, x=0, z0=-.08, t=.1)
    a.part('Rudders', 'Armor').box((.02, .08, .3), loc=(0, 1.78, -.3), bevel=0)


def _propeller(a):
    pr = a.pivot('Propeller', (0, 1.98, 0))
    k.lathe(a.part('Propeller_hub', 'Steel', pr), [(.08, -.05), (.09, 0), (.07, .1), (0, .18)], rot=K.BACKWARD,
            seg=14)
    bl = a.part('Propeller_blades', 'Armor', pr)
    for j in range(3):
        u0 = j * math.tau / 3
        d = (math.cos(u0), math.sin(u0))
        rings = []
        for r, chord, tw in ((.07, .08, .6), (.2, .085, .45), (.35, .07, .33), (.48, .05, .25), (.58, .03, .2)):
            rings.append([(d[0] * r - d[1] * chord * math.cos(tw) * uu * 0, chord * math.cos(tw) * uu,
                           d[1] * r + chord * math.sin(tw) * uu + .01 * vv) for uu, vv in ((-1, 0), (0, 1), (1, 0),
                                                                                         (0, -1))])
        bl.loft(rings, bevel=0)


def _stores(a):
    py = a.part('Pylons', 'Armor')
    rk = a.part('Racks', 'Steel')
    for s, mname, bname in ((1, 'Muzzle_missile.001', 'Muzzle_rocket.001'), (-1, 'Muzzle_missile', 'Muzzle_rocket')):
        # The outer station: a pylon with the twin Hellfire rail.
        xo = s * 1.9
        K.pylon(py, xo, -.42, -.12, WING_Z - .01, WING_Z - .12, w=.05)
        rk.box((.16, .45, .03), loc=(xo, -.3, WING_Z - .14), bevel=0)
        for dx in (-.055, .055):
            K.missile(a, (xo + dx, -.05, WING_Z - .19), .035, .65, direction=(0, 1, 0), fins=4)
        a.pivot(mname.replace('.001', '__001'), (xo, -.72, WING_Z - .19))
        # The inner station: a pylon with the GBU-39 rack (two bombs).
        xi = s * .95
        K.pylon(py, xi, -.45, -.12, WING_Z - .01, WING_Z - .12, w=.05)
        rk.box((.18, .5, .04), loc=(xi, -.3, WING_Z - .14), bevel=0)
        for dx in (-.06, .06):
            k.lathe(a.part('Bombs_body', 'Armor'), [(0, -.4), (.03, -.36), (.045, -.25), (.045, .25), (.03, .35),
                                                    (0, .38)], loc=(xi + dx, -.3, WING_Z - .21), rot=K.BACKWARD,
                    seg=8, worn=(2,))
            for f in range(4):
                u = f * R90 + math.pi / 4
                a.part('Bomb_fins', 'Steel').box((.004, .1, .05), loc=(xi + dx + math.cos(u) * .05, .0,
                                                                    WING_Z - .21 + math.sin(u) * .05),
                                                 rot=(0, u, 0), bevel=0)
        a.pivot(bname.replace('.001', '__001'), (xi, -.72, WING_Z - .21))


def strike_drone(a, detail=False):
    """The strike drone: see the module docstring."""
    K.suffixed(a)
    _fuselage(a)
    _wing(a)
    _tail(a)
    _propeller(a)
    _stores(a)
    k.clean(a)


BUILDERS = {
    'strike_drone': (strike_drone, dict(ao_distance=.2, grime_height=.0)),
}
