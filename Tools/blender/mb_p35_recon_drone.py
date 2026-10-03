"""Prompt 35 wave 4 (lane C): the reconnaissance drone rebuilt from scratch (spec: Tools/blender/specs/recon_drone.json).

A Bayraktar TB2 (the def's modelSize 2.67 x 4.83 x 0.48 m, 0.4 x the real one): the slender fuselage with its
rounded nose, the EO/IR sensor ball under the chin, the long high-mounted straight tapered wing with ailerons and
flaps, the twin tail booms joined by the inverted-V tail, the pusher propeller behind the engine bay with its
cooling scoops and exhaust stubs, two MAM-L glide bombs on the inner pylons (empty outer pylons), satcom and blade
aerials, navigation lights. Flying (no landing gear drawn).

Runtime nodes kept: `Propeller` (+ `Propeller_blades`, `Propeller_hub`), `Muzzle_missile`, `Muzzle_missile.001`,
`Muzzle_gun` (the laser designator in the sensor ball), `Point_exhaust`, `Point_fire`. Metres, +Z up, -Y front,
+X left. The real TB2 has no flare dispenser (spec "merged" for the gate's jet role).
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WING_Z = .1


def _fuselage(a):
    body = a.part('Fuselage', 'Team')
    stations = [(-1.3, .03, .03, -.02), (-1.27, .06, .062, -.02), (-1.22, .088, .092, -.02), (-1.15, .108, .114, -.01),
                (-1.05, .122, .13, -.005), (-.9, .13, .14, 0.0), (-.7, .134, .146, .005), (-.4, .135, .15, .01),
                (0.0, .135, .15, .02), (.35, .13, .145, .02), (.65, .115, .128, .02), (.88, .097, .106, .02),
                (1.05, .075, .082, .02), (1.18, .05, .055, .02)]
    C.section_loft(body, [(y, C.ellipse_half(w, h, zc, 16)) for y, w, h, zc in stations])
    # The sensor ball under the chin on its gimbal, the laser window (`Muzzle_gun`).
    a.part('Sensor', 'Armor').cyl(.04, .05, loc=(0, -.95, -.13), seg=10, bevel=0)
    k.lathe(a.part('Sensor_ball', 'Armor'), [(0, -.09), (.05, -.08), (.075, -.04), (.08, 0), (.07, .04), (.04, .06),
                                            (0, .065)], loc=(0, -.95, -.19), seg=20)
    a.part('Glass', 'Glass').box((.06, .02, .05), loc=(0, -1.025, -.205), bevel=0)
    a.pivot('Muzzle_gun', (0, -1.04, -.205))
    # The engine bay: cooling scoops on top, the exhaust stubs, the access panels.
    for s in (-1, 1):
        K.intake(a.part('Intakes', 'Team'), a.part('Intake_ducts', 'Undercarriage'), (s * .06, .55, .15), .07, .04,
                 .12, facing=(0, -1, .3), lip=.008)
        k.lathe(a.part('Exhausts', 'Steel'), [(.016, 0), (.018, .06), (.014, .08)], loc=(s * .11, .95, -.03),
                rot=(R90 + .3, 0, s * .6), seg=6)
    K.soot(a, (0, 1.05, 0), radius=.2, k=.4)
    a.pivot('Point_exhaust', (0, 1.0, 0))
    a.pivot('Point_fire', (0, .2, .05))
    pn = a.part('Panels', 'Armor')
    for y in (-.6, .2):
        pn.box((.12, .2, .01), loc=(0, y, .148), bevel=0)
    # Aerials: the satcom hump, blade aerials top and bottom.
    k.lathe(a.part('Antennas', 'Armor'), [(.07, 0), (.06, .02), (0, .025)], loc=(0, -.35, .14), seg=14)
    K.blade_antenna(a.part('Antennas', 'Steel'), (0, .3, .14), h=.08, chord=.07)
    K.blade_antenna(a.part('Antennas', 'Steel'), (0, .1, -.13), h=.06, chord=.06, normal=(0, 0, -1))
    for s in (-1, 1):
        a.part('Team_band', 'Team').box((.01, .5, .05), loc=(s * .13, -.4, .02), bevel=0)


def _wing(a):
    wing = a.part('Wings', 'Team')
    # Straight tapered wing: six airfoil sections a side (the TB2's taper starts beyond the booms).
    for s in (-1, 1):
        rings = []
        for f, lead, chord in ((0, -.25, .44), (.12, -.25, .44), (.3, -.24, .4), (.55, -.22, .34), (.8, -.2, .29),
                               (1.0, -.18, .25)):
            x = .02 + 2.38 * f
            ring = [(s * px, py, pz + math.tan(.015) * 2.38 * f) for px, py, pz in K._foil_ring(lead, chord, .13, x, WING_Z)]
            rings.append(ring if s > 0 else list(reversed(ring)))
        wing.loft(rings, bevel=0)
    # Ailerons and flaps along the trailing edge (separate surfaces), the wing lights, the boom roots.
    cs = a.part('Flaps', 'Armor')
    for s in (-1, 1):
        for x0, x1, yy in ((.2, .75, .17), (.8, 1.35, .15), (1.45, 2.2, .1)):
            cs.box((x1 - x0, .07, .012), loc=(s * (x0 + x1) / 2, yy, WING_Z + .01 + abs(x0 + x1) * .015), bevel=0)
        a.part('Wing_lights', 'Lamp' if s > 0 else 'LavaGlow').box((.03, .05, .02), loc=(s * 2.4, -.12, WING_Z + .07),
                                                                    bevel=0)
    a.part('Team_band', 'Team').box((.3, .2, .005), loc=(1.5, -.1, WING_Z + .05), bevel=0)
    a.part('Team_band', 'Team').box((.3, .2, .005), loc=(-1.5, -.1, WING_Z + .05), bevel=0)


def _tail(a):
    """The twin booms from the wing, joined at their ends by the inverted-V tail."""
    boom = a.part('Tail_booms', 'Team')
    for s in (-1, 1):
        k.lathe(boom, [(0, -.05), (.03, .0), (.04, .1), (.035, 1.2), (.025, 1.35), (0, 1.37)],
                loc=(s * .6, -.1, WING_Z - .02), rot=K.BACKWARD, seg=14)
    tail = a.part('Tail', 'Team')
    for s in (-1, 1):
        # An inverted-V half: from the boom's end down and inwards to the joint under the centre line.
        x0, z0 = s * .6, WING_Z - .02
        x1, z1 = s * .02, -.19
        rings = []
        for f in (0, .33, .66, 1.0):
            x, z, lead, chord = x0 + (x1 - x0) * f, z0 + (z1 - z0) * f, 1.0 + .05 * f, .26 - .06 * f
            rings.append([(x, lead + chord * (1 - u) / 2, z + v * .012) for u, v in K.FOIL])
        tail.loft(rings, bevel=0)
        a.part('Rudders', 'Armor').box((.02, .07, .02), loc=((x0 + x1) / 2, 1.24, (z0 + z1) / 2), bevel=0)


def _propeller(a):
    pr = a.pivot('Propeller', (0, 1.25, .02))
    k.lathe(a.part('Propeller_hub', 'Steel', pr), [(.05, -.03), (.055, 0), (.04, .06), (0, .1)], rot=K.BACKWARD,
            seg=12)
    bl = a.part('Propeller_blades', 'Armor', pr)
    for s in (-1, 1):
        rings = []
        for r, chord, tw in ((.04, .05, .55), (.09, .052, .45), (.15, .046, .35), (.21, .04, .27), (.27, .028, .2)):
            rings.append([(s * r, chord * math.cos(tw) * u, s * chord * math.sin(tw) * u + .006 * v)
                          for u, v in ((-1, 0), (0, 1), (1, 0), (0, -1))])
        bl.loft(rings, bevel=0)


def _stores(a):
    py = a.part('Pylons', 'Armor')
    for s in (-1, 1):
        for x in (.75, 1.15):
            K.pylon(py, s * x, -.28, -.02, WING_Z - .02, WING_Z - .1, w=.03)
    for s, name in ((1, 'Muzzle_missile.001'), (-1, 'Muzzle_missile')):
        K.missile(a, (s * .75, -.1, WING_Z - .14), .025, .55, direction=(0, -1, 0), fins=4)   # nose forward (kit fixed in wave 5)
        a.pivot(name.replace('.001', '__001'), (s * .75, -.67, WING_Z - .14))


def recon_drone(a, detail=False):
    """The reconnaissance drone: see the module docstring."""
    K.suffixed(a)
    _fuselage(a)
    _wing(a)
    _tail(a)
    _propeller(a)
    _stores(a)
    k.clean(a)


BUILDERS = {
    'recon_drone': (recon_drone, dict(ao_distance=.15, grime_height=.0)),
}
