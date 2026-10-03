"""Prompt 35 wave 4 (lane C): the attack jet rebuilt from scratch (spec: Tools/blender/specs/attack_jet.json).

A Su-25 "Frogfoot" (the def's modelSize 6.15 x 6.04 x 1.84 m, 0.4 x the real one): the long drooped nose with the
laser rangefinder window, the armoured cockpit with its small framed canopy and the rear-view periscope, the big
intakes under the wing roots, the two engines in nacelles along the fuselage sides with their plain nozzles, the
tall fin with the rudder, the tailplanes with dihedral, the beaver-tail cone with the chaff / flare dispensers; the
shoulder-mounted tapered wing with the wingtip pods (split airbrakes), slats and flaps, five pylons a wing carrying
FAB-250 bombs, B-8 rocket pods, Kh-29 missiles and R-60s on the outer rails (the def's free `r60`: `Mount_aam`);
the GSh-30-2 twin barrels under the nose (`Gun`).

Runtime nodes kept: `Gun`, `Muzzle_gun`, `Muzzle_main`, `Pods`, `Muzzle_rocket` (x2), `Muzzle_missile` (x2), `Muzzle_aam`
(+ `Mount_aam`, which the old file lacked), `Point_exhaust`, `Point_fire` (the wrappers add `Part_wing` and
`Mount_Flare_L / _R / _TL / _TR` at the `Flares`). Metres, +Z up, -Y front, +X left.
"""
import functools
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C
import mb_parts27 as p27

R90 = math.pi / 2
WING_Z = .12


def _fuselage(a):
    body = a.part('Fuselage', 'Team')
    # Nose to tail cone: the drooped nose, the cockpit, the waist between the nacelles.
    st = [(-3.08, .03, .03, -.12), (-3.0, .08, .08, -.11), (-2.8, .14, .15, -.09), (-2.5, .19, .2, -.06),
          (-2.15, .23, .25, -.02), (-1.8, .26, .29, .0), (-1.4, .27, .3, .01), (-.9, .26, .29, .02),
          (-.2, .24, .27, .03), (.6, .22, .26, .04), (1.4, .21, .25, .05), (2.1, .19, .22, .07),
          (2.6, .15, .17, .08), (2.95, .09, .1, .09), (3.08, .04, .04, .09)]
    C.section_loft(body, [(y, C.ellipse_half(w, h, zc, 12)) for y, w, h, zc in st])
    # The laser rangefinder window in the nose tip, the pitot, the cockpit canopy with its frame and periscope.
    a.part('Glass', 'Glass').cyl(.05, .02, loc=(0, -3.08, -.12), rot=K.FORWARD, seg=10, bevel=0)
    a.part('Antennas', 'Steel').cyl(.008, .3, loc=(.12, -2.9, -.08), rot=K.FORWARD, seg=4, bevel=0)
    can = a.part('Canopy', 'Glass')
    C.section_loft(can, [(-2.35, C.ellipse_half(.06, .05, .2, 8)), (-2.15, C.ellipse_half(.17, .14, .2, 8)),
                         (-1.85, C.ellipse_half(.2, .17, .22, 8)), (-1.6, C.ellipse_half(.17, .14, .22, 8)),
                         (-1.42, C.ellipse_half(.08, .06, .22, 8))])
    fr = a.part('Canopy_frames', 'Armor')
    for y, w, h in ((-2.15, .175, .145), (-1.85, .205, .175)):
        pts = [(x * 1.01, y, z) for x, z in C.ellipse_half(w, h, .2 if y < -2 else .22, 8)][3:]
        fr.tube(pts + [(-x, yy, z) for x, yy, z in reversed(pts[:-1])], .012, seg=4)
    fr.box((.03, .03, .1), loc=(0, -1.62, .42), bevel=0)                                   # periscope
    # The intakes under the wing roots and the engine nacelles along the sides, their nozzles.
    nac = a.part('Nacelles', 'Team')
    for s in (-1, 1):
        x = s * .36
        k.lathe(nac, [(.12, 0), (.17, .3), (.18, 1.2), (.17, 2.6), (.14, 3.2), (.12, 3.4)], loc=(x, -1.05, -.04),
                rot=K.BACKWARD, seg=12, worn=(2,))
        K.intake(a.part('Intakes', 'Team'), a.part('Intake_ducts', 'Undercarriage'), (s * .4, -1.05, -.06), .2, .26,
                 .3, facing=(0, -1, 0), lip=.02)
        k.lathe(a.part('Nozzles', 'Steel'), [(.12, 0), (.125, .08), (.11, .2), (.1, .22)], loc=(x, 2.33, -.04),
                rot=K.BACKWARD, seg=12, worn=(1,))
        a.part('Intake_ducts', 'Undercarriage').cyl(.09, .02, loc=(x, 2.55, -.04), rot=K.BACKWARD, seg=12, bevel=0)
        K.soot(a, (x, 2.55, -.04), radius=.3, k=.4)
        # The chaff / flare dispensers on the nacelle tops (ASO-2V).
        K.flare_dispenser(a, (s * .3, 1.9, .14), normal=(s * .3, 0, 1), cols=4, rows=2, cell=.05)
    a.pivot('Point_exhaust', (.36, 2.6, -.04))
    a.pivot('Point_fire', (0, .3, .2))
    # The GSh-30-2 under the nose (left), its twin barrels.
    gun = a.part('Gun', 'Steel')
    k.block(gun, (.1, .5, .08), loc=(.12, -2.25, -.32), chamfer=.01)
    for dx in (-.02, .02):
        gun.cyl(.014, .5, loc=(.12 + dx, -2.7, -.27), rot=K.FORWARD, seg=6, bevel=0)
    a.pivot('Muzzle_gun', (.12, -2.97, -.27))
    a.pivot('Muzzle_main', (.12, -2.97, -.27))
    # Aerials, panels, the team bands.
    K.blade_antenna(a.part('Antennas', 'Steel'), (0, -.8, .3), h=.1, chord=.1)
    K.blade_antenna(a.part('Antennas', 'Steel'), (0, .8, -.21), h=.08, chord=.08, normal=(0, 0, -1))
    for s in (-1, 1):
        body.box((.01, .8, .07), loc=(s * .245, -2.0, -.05), bevel=0)


def _tail(a):
    tail = a.part('Tail', 'Team')
    K.fin(tail, (1.85, 1.15), (2.6, .5), 1.28, x=0, z0=.2, t=.08)
    tail.box((.03, .2, .8), loc=(0, 2.98, .8), rot=(-.2, 0, 0), bevel=0)                    # the rudder
    tp = a.part('Tailplane', 'Team')
    K.wing(tp, (2.15, .75), (2.55, .35), 1.05, x0=.15, z=.12, t=.07, dihedral=.12)
    # The beaver-tail cone with its dispenser.
    k.lathe(a.part('Fuselage', 'Team'), [(.1, 0), (.09, .2), (.05, .4), (0, .45)], loc=(0, 2.9, .05),
            rot=K.BACKWARD, seg=10)
    K.flare_dispenser(a, (0, 3.2, -.02), normal=(0, 0, -1), cols=2, rows=2, cell=.04)


def _wing(a):
    wing = a.part('Wing', 'Team')
    for s in (-1, 1):
        rings = []
        for f, lead, chord in ((0, -.95, 1.5), (.25, -.75, 1.25), (.5, -.55, 1.0), (.75, -.35, .8), (1.0, -.15, .62)):
            x = .25 + 2.65 * f
            ring = [(s * px, py, pz - math.tan(.04) * 2.65 * f) for px, py, pz in K._foil_ring(lead, chord, .1, x, WING_Z)]
            rings.append(ring if s > 0 else list(reversed(ring)))
        wing.loft(rings, bevel=0)
        # Slats and flaps, the wingtip pod with its split airbrakes, the navigation light.
        cs = a.part('Wing', 'Team')
        for x0, x1 in ((.4, 1.4), (1.5, 2.6)):
            f = ((x0 + x1) / 2 - .25) / 2.65
            lead = -.95 + .8 * f
            chord = 1.5 - .88 * f
            zc = WING_Z - math.tan(.04) * 2.65 * f
            cs.box((x1 - x0, .12, .02), loc=(s * (x0 + x1) / 2, lead + chord - .08, zc + .005), rot=(0, 0, -s * .05),
                   bevel=0)
            cs.box((x1 - x0, .08, .02), loc=(s * (x0 + x1) / 2, lead + .03, zc + .01), rot=(0, 0, -s * .3), bevel=0)
        xt = s * 2.95
        zt = WING_Z - math.tan(.04) * 2.65
        k.lathe(a.part('Wingtip_pods', 'Team'), [(0, -.55), (.05, -.48), (.07, -.3), (.07, .3), (.04, .45), (0, .5)],
                loc=(xt, .0, zt), rot=K.BACKWARD, seg=10)
        a.part('Wingtip_pods', 'Team').box((.12, .2, .015), loc=(xt, .5, zt + .04), rot=(.35, 0, 0), bevel=0)  # airbrakes
        a.part('Wingtip_pods', 'Team').box((.12, .2, .015), loc=(xt, .5, zt - .04), rot=(-.35, 0, 0), bevel=0)
        a.part('Wing_lights', 'Lamp').box((.03, .06, .03), loc=(xt, -.55, zt), bevel=0)
        a.part('Wing', 'Team').box((.5, .35, .005), loc=(s * 2.2, -.1, WING_Z + .05 - math.tan(.04) * 1.9),
                                        bevel=0)


def _stores(a):
    """Five pylons a wing: FAB-250 (inner), B-8 pods, Kh-29, an empty station, R-60 (outer)."""
    py = a.part('Pylons', 'Armor')
    def zw(x):
        return WING_Z - .06 - math.tan(.04) * (abs(x) - .25)
    for s in (-1, 1):
        for x in (.75, 1.15, 1.55, 1.95, 2.45):
            K.pylon(py, s * x, -.55 + (x - .75) * .3, -.05 + (x - .75) * .3, zw(x), zw(x) - .1, w=.05)
    for s in (-1, 1):
        x = s * .75
        C.store(a, (x, .25, zw(.75) - .22), .1, .9, body='Bombs_body', body_mat='Armor', kind='bomb')
    for s, name in ((1, 'Muzzle_rocket.001'), (-1, 'Muzzle_rocket')):
        x = s * 1.15
        p27.rocket_pod(a, x, -.75, zw(1.15) - .2, .11, .95, s, seg=12)
        a.pivot(name.replace('.001', '__001'), (x, -.77, zw(1.15) - .2))
    for s, name in ((1, 'Muzzle_missile.001'), (-1, 'Muzzle_missile')):
        x = s * 1.55
        C.store(a, (x, .35, zw(1.55) - .2), .07, 1.0)
        a.pivot(name.replace('.001', '__001'), (x, -.7, zw(1.55) - .2))
    # The R-60 on the left outer rail, on its own free mount (`Mount_aam`); its twin on the right is a dummy load.
    m = a.pivot('Mount_aam', (2.45, .15, zw(2.45) - .14))
    C.store(a, (0, .3, 0), .035, .65, parent=m)
    a.pivot('Muzzle_aam', (0, -.37, 0), m)
    C.store(a, (-2.45, .45, zw(2.45) - .14), .035, .65)


def attack_jet(a, detail=False):
    """The attack jet: see the module docstring."""
    K.suffixed(a)
    _fuselage(a)
    _tail(a)
    _wing(a)
    _stores(a)
    k.clean(a)


OPTS = dict(ao_distance=.25, grime_height=.0)
BUILDERS = {
    'attack_jet': (attack_jet, OPTS),
    # The PC High twin is the same model (it replaces the prompt 27 wave 4b attack_jet_hd).
    'attack_jet_hd': (functools.partial(attack_jet, detail=True), OPTS),
}
