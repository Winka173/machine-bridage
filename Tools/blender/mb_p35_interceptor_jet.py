"""Prompt 35 wave 6 (lane B): the interceptor jet rebuilt from scratch (spec: Tools/blender/specs/interceptor_jet.json).

A MiG-31BM-class heavy interceptor (the def's modelSize 9.1 x 5.4 x 2.5 m; about 0.4 x the real aircraft): the long
lofted fuselage from the radome back to the twin engine nacelles, the tandem two-seat canopy with its frames, the big
rectangular side intakes with their splitter plates and dark ducts, the shoulder-mounted trapezoidal wing with the
leading-edge root extensions and the wing fences, the twin canted fins with the rudders, the all-moving tailplanes
and the two ventral fins, the two large nozzles with petals and the afterburner glow; four long-range R-37M
missiles under the fuselage in tandem pairs on their recesses (`Muzzle_missile`), two wing pylons, the anti-radar
missile on the right pylon on its own pivot (`Mount_aam` > `Muzzle_aam`: the def's free secondary), the flare
dispensers on the rear fuselage sides (the wrapper puts `Mount_Flare_*` on them), the refuelling probe, pitot, blade
antennas, lights and the Team bands. Jet rule: no insets or panel greebles on the skin.

Its own fuselage, wing and tails (not glide_bomber's or fighter_jet's). Runtime nodes kept: `Muzzle_missile`,
`Mount_Flare_L` / `_R` / `_TL` / `_TR` (from the wrapper), `Part_wing` (the wrapper); new: `Mount_aam`, `Muzzle_aam`.
Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
NOSE, TAIL = -4.55, 4.0


def _fuselage(a):
    fus = a.part('Fuselage', 'Team')
    rings = [[(0, NOSE, .05)]]
    # Stations: radome, cockpit, the boxy intake section, the wide engine section, the nacelles' ends.
    for y, w, top, bot in ((-4.25, .14, .2, -.1), (-3.8, .26, .32, -.2), (-3.2, .36, .44, -.28), (-2.5, .42, .55, -.32),
                           (-1.8, .45, .48, -.34), (-.8, .5, .42, -.36), (.6, .56, .4, -.36), (2.0, .58, .38, -.35),
                           (3.2, .55, .34, -.3), (3.75, .5, .3, -.26)):
        rings.append([(-w * .55, y, top), (w * .55, y, top), (w, y, (top + bot) * .5 + .05), (w * .9, y, bot),
                      (-w * .9, y, bot), (-w, y, (top + bot) * .5 + .05)])
    k.sharp_loft(fus, rings, chamfer=.02)
    a.part('Radome', 'Armor').loft([[(0, NOSE - .02, .05)]] + [
        [(math.cos(u) * r, y, .05 + math.sin(u) * r) for u in [i * TAU / 10 for i in range(10)]]
        for y, r in ((-4.35, .08), (-4.1, .16))])
    # The tandem canopy: two bubbles and their frames.
    can = a.part('Canopy', 'Glass')
    for y0, y1 in ((-3.45, -2.85), (-2.75, -2.15)):
        can.loft([[(-.2, y0, .38), (.2, y0, .38), (.16, y0, .55), (-.16, y0, .55)],
                  [(-.24, (y0 + y1) / 2, .45), (.24, (y0 + y1) / 2, .45), (.18, (y0 + y1) / 2, .7),
                   (-.18, (y0 + y1) / 2, .7)],
                  [(-.24, y1, .5), (.24, y1, .5), (.18, y1, .68), (-.18, y1, .68)]])
    fr = a.part('Canopy_frames', 'Armor')
    for y, z in ((-3.45, .5), (-2.8, .64), (-2.15, .62)):
        fr.tube([(-.23, y, z - .12), (0, y, z + .06), (.23, y, z - .12)], .018, seg=4)
    fr.tube([(0, -3.45, .56), (0, -2.15, .72)], .015, seg=3)
    # The spine behind the canopy, the dorsal fairing between the fins.
    k.extrude(a.part('Spine', 'Team'), [(-2.1, .4), (2.6, .38), (3.2, .3), (-2.1, .3)], .32, axis='X', chamfer=.03)
    # Big rectangular intakes with splitter plates, the dark ducts and the variable ramps.
    for s in (-1, 1):
        k.extrude(a.part('Intakes', 'Armor'), [(-.24, -.3), (.24, -.3), (.26, .32), (-.24, .32)], 2.6,
                  loc=(s * .58, -1.05, .02), axis='Y', chamfer=.03, taper=(1.0, .9))
        a.part('Intake_dark', 'Undercarriage').box((.38, .03, .5), loc=(s * .58, -2.36, .03), bevel=0)
        a.part('Intake_lips', 'Steel').box((.03, .5, .62), loc=(s * .32, -2.15, .03), bevel=0)
        a.part('Intake_ramps', 'Armor').box((.34, .5, .04), loc=(s * .58, -2.15, .3), rot=(.15, 0, 0), bevel=0)
        # Engine nacelles' sides and the two nozzles with petals and the afterburner glow.
        x = s * .3
        k.lathe(a.part('Nozzles', 'Steel'), [(.3, 0), (.3, .1), (.27, .3), (.24, .45), (.25, .47)], loc=(x, 3.6, .02),
                rot=K.BACKWARD, seg=12, caps=(False, False), worn=(1,))
        pet = a.part('Nozzle_petals', 'Undercarriage')
        for i in range(10):
            u = i * TAU / 10
            pet.box((.06, .2, .01), loc=(x + math.cos(u) * .25, 4.08, .02 + math.sin(u) * .25), rot=(0, -u, 0),
                    bevel=0)
        a.part('Exhaust_glow', 'LavaGlow').cyl(.2, .02, loc=(x, 3.98, .02), rot=K.BACKWARD, seg=12, bevel=0)
        K.soot(a, (x, 4.1, .02), radius=.5, k=.35)


def _wings(a):
    w = a.part('Wings', 'Team')
    K.wing(w, (-1.2, 2.4), (1.15, .9), 2.15, x0=.55, z=.3, t=.06, dihedral=-.05)
    # Leading-edge root extensions and the wing fences.
    for s in (-1, 1):
        k.extrude(w, [(s * .45, -2.1), (s * .45, -.9), (s * .95, -.9)] if s > 0 else [(s * .45, -2.1), (s * .95, -.9), (s * .45, -.9)],
                  .05, loc=(0, 0, .31), axis='Z', chamfer=.01)
        a.part('Wing_fences', 'Armor').box((.02, .7, .06), loc=(s * 1.75, .1, .32), bevel=0)
        a.part('Wing_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.06, .1, .04), loc=(s * 2.68, .7, .26),
                                                                          bevel=0)
        # The twin canted fins with rudders, the tailplanes, the ventral fins.
        K.fin(a.part('Fins', 'Team'), (2.35, 1.4), (3.25, .7), 1.25, x=s * .42, z0=.35, t=.06, cant=s * .1)
        a.part('Rudders', 'Armor').box((.04, .28, .9), loc=(s * (.42 + .07), 3.65, .95), rot=(0, s * .1, 0), bevel=0)
        K.fin(a.part('Ventral_fins', 'Armor'), (2.7, .9), (3.2, .5), -.7, x=s * .55, z0=-.3, t=.06, cant=-s * .3)
    K.wing(a.part('Tailplanes', 'Team'), (2.85, 1.15), (3.6, .55), 1.1, x0=.55, z=.08, t=.05, dihedral=-.04)
    for s in (-1, 1):
        a.part('Team_band', 'Team').box((.012, .5, .3), loc=(s * (.42 + .12 * s * s), 3.0, 1.05), rot=(0, s * .1, 0),
                                        bevel=0)


def _stores(a):
    # Four R-37M in tandem pairs under the fuselage, on their recesses (`Muzzle_missile`).
    rec = a.part('Racks', 'Undercarriage')
    for x in (-.32, .32):
        rec.box((.18, 3.6, .05), loc=(x, .2, -.37), bevel=0)
        for y in (-1.3, 1.5):
            K.missile(a, (x, y - .95, -.47), .085, 1.95, direction=(0, -1, 0), fins=4)
    a.pivot('Muzzle_missile', (0, -.2, -.55))
    # Wing pylons; the anti-radar missile on the right pylon on its own pivot (`Mount_aam`).
    for s in (-1, 1):
        K.pylon(a.part('Pylons', 'Armor'), s * 1.55, -.5, .4, .27, .12, w=.06)
    m = a.pivot('Mount_aam', (-1.55, -.05, .02))
    K.missile(a, (0, -.9, -.06), .075, 1.6, direction=(0, -1, 0), fins=4, parent=m, body='Missile_aam')
    a.pivot('Muzzle_aam', (0, -1.0, -.06), m)
    K.missile(a, (1.55, -.95, -.04), .075, 1.6, direction=(0, -1, 0), fins=4)
    # Flare dispensers on the rear fuselage sides, the refuelling probe, pitot, antennas, lights.
    for s in (-1, 1):
        K.flare_dispenser(a, (s * .58, 2.6, -.1), normal=(s, 0, -.3), cols=2, rows=3, cell=.05)
    a.part('Probe', 'Steel').tube([(-.25, -3.0, .35), (-.32, -3.9, .3)], .025, seg=5)
    a.part('Probe', 'Steel').tube([(0, -4.4, .05), (0, -4.7, .05)], .012, seg=4)
    for y, z, n in ((-1.5, .44, (0, 0, 1)), (1.2, .4, (0, 0, 1)), (.3, -.36, (0, 0, -1))):
        K.blade_antenna(a.part('Antennas', 'Steel'), (0, y, z), h=.12, chord=.12, normal=n)
    a.part('Lamps', 'Lamp').box((.05, .05, .04), loc=(0, -1.0, -.38), bevel=0)
    a.part('Beacons', 'LavaGlow').box((.05, .08, .04), loc=(0, 1.8, .45), bevel=0)
    a.pivot('Point_fire', (0, .5, .5))
    a.pivot('Point_exhaust', (0, 4.05, .02))


def interceptor_jet(a):
    """The interceptor jet: see the module docstring."""
    _fuselage(a)
    _wings(a)
    _stores(a)
    P.merge_parts(a, {'Intake_ramps': 'Intakes', 'Wing_fences': 'Rudders', 'Probe': 'Antennas',
                      'Intake_lips': 'Antennas'})
    k.clean(a)


BUILDERS = {
    'interceptor_jet': (interceptor_jet, dict(ao_distance=.4, ground=False)),
}
