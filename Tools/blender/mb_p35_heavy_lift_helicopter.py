"""Prompt 35 wave 10 (lane B): the heavy-lift helicopter rebuilt from scratch (spec:
Tools/blender/specs/heavy_lift_helicopter.json).

A Mi-26 class heavy-lift helicopter (the def's modelSize 7.59 x 6.58 x 2.1 m: the rotor disc sets the width;
unarmed transport with flares): the deep box cabin with its rounded belly, the glazed nose with the chin windows and
the stepped flight deck (framed windscreen, side blisters), the row of round cabin windows, the crew door front left
with its step, the two engines on the roof ahead of the rotor (dust-filter intakes, nacelle seams, exhausts angled
out, the gearbox fairing), the eight-blade main rotor (`Rotor`) on its mast, the tail boom rising to the swept fin
with the five-blade tail rotor on the right (`Tail_rotor`), the stabilisers, the main gear in two sponsons with twin
wheels and the twin nose wheel, the rear clamshell doors and ramp, the cargo hook under the belly, the UV-26 flare
launchers on the rear flanks (the Mount_Flare points come from the flare wrapper), the red beacons, nav lights,
antennas, Team bands.

Runtime nodes kept: `Rotor` (0, -0.3, 1.72) with `Rotor_hub` / `_grips` / `_blades` / `_tips`, `Tail_rotor`
(-0.13, 3.9, 1.3) with its hub / blades / tips, `Muzzle_main` (the old file's, at the nose), `Point_fire`,
`Point_exhaust`. Built only from frontier_kit / mb_kit27 primitives, mb_kit35 and lane B's helpers; no other model's
builder. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
ROTOR = (0, -.3, 1.72)
TR = (-.13, 3.9, 1.3)


def _fuselage(a):
    body = a.part('Fuselage', 'Team')
    E = K.ellipse_half
    stations = [(-3.32, E(.12, .14, .62, n=6)), (-3.2, E(.3, .3, .66, n=6)), (-2.95, E(.42, .44, .74, n=6, flat=.15)),
                (-2.55, E(.48, .55, .82, n=6, flat=.3)), (-1.9, E(.5, .55, .85, n=6, flat=.4)),
                (1.6, E(.5, .55, .85, n=6, flat=.4)), (2.1, E(.42, .45, .9, n=6, flat=.3)),
                (2.45, E(.25, .3, 1.05, n=6)), (3.6, E(.09, .1, 1.3, n=6)), (3.75, E(.06, .06, 1.32, n=6))]
    K.section_loft(body, stations)
    # Flight deck glazing: the framed windscreen, side blisters, chin windows; the frames.
    g = a.part('Glass', 'Glass')
    g.mesh([(-.36, -3.12, .95), (.36, -3.12, .95), (.3, -2.82, 1.22), (-.3, -2.82, 1.22)], [(0, 1, 2, 3)])
    for s in (-1, 1):
        g.mesh([(s * .43, -3.0, .78), (s * .49, -2.6, .8), (s * .47, -2.6, 1.15), (s * .4, -2.9, 1.08)],
               [(0, 1, 2, 3) if s > 0 else (3, 2, 1, 0)])
        g.box((.12, .2, .02), loc=(s * .16, -3.2, .5), rot=(.6, 0, 0), bevel=0)
    fr = a.part('Canopy_frames', 'Armor')
    for x in (-.12, .12):
        fr.box((.03, .4, .03), loc=(x, -2.97, 1.09), rot=(-.73, 0, 0), bevel=0)
    fr.box((.74, .03, .03), loc=(0, -2.82, 1.22), bevel=0)
    # The round cabin windows, the crew door with its step, Team bands, panel seams.
    P.portholes(a, [(.505, y, 1.0) for y in (-1.5, -.9, -.3, .3, .9)], (1, 0, 0), r=.07, seg=8)
    P.portholes(a, [(-.505, y, 1.0) for y in (-.9, -.3, .3, .9)], (-1, 0, 0), r=.07, seg=8)
    a.part('Doors', 'Armor').box((.02, .4, .6), loc=(.505, -2.15, .72), bevel=0)
    P.step(a, (.52, -2.15, .28), w=.25, d=.12)
    band = a.part('Team_band', 'Team')
    for s in (-1, 1):
        band.box((.012, 3.2, .08), loc=(s * .505, -.3, .62), bevel=0)
    seams = a.part('Panel_seams', 'Undercarriage')
    for y in (-1.9, -1.2, -.4, .4, 1.2):
        for s in (-1, 1):
            seams.box((.01, .015, .55), loc=(s * .505, y, .8), bevel=0)
    # Rear clamshell doors and the ramp line, the cargo hook under the belly.
    for s in (-1, 1):
        a.part('Hatches', 'Armor').box((.02, .55, .5), loc=(s * .44, 2.05, .78), rot=(0, 0, -s * .3), bevel=0)
    a.part('Ramp_seam', 'Undercarriage').box((.6, .015, .02), loc=(0, 2.15, .42), bevel=0)
    a.part('Cargo_hook', 'Steel').tube([(0, -.3, .32), (0, -.3, .18), (.04, -.3, .12)], .02, seg=4)
    a.pivot('Muzzle_main', (0, -3.3, .85))
    a.pivot('Point_fire', (0, -.3, 1.0))


def _engines(a):
    """Two engines on the roof ahead of the rotor, the gearbox fairing, the mast."""
    fair = a.part('Fuselage_fairing', 'Team')
    K.section_loft(fair, [(-2.2, K.ellipse_half(.2, .05, 1.38, n=4)), (-1.9, K.ellipse_half(.42, .22, 1.42, n=4)),
                          (.6, K.ellipse_half(.42, .25, 1.45, n=4)), (1.2, K.ellipse_half(.2, .06, 1.4, n=4))])
    for i, s in enumerate((-1, 1)):
        x = s * .25
        k.lathe(a.part('Engines', 'Armor'), [(.0, -1.15), (.15, -1.1), (.16, -.4), (.16, .3), (.12, .55), (.09, .6)],
                loc=(x, -.9, 1.6), rot=K.BACKWARD, seg=10, worn=(2,))
        k.lathe(a.part('Intakes', 'Undercarriage'), [(.11, 0), (.15, .02), (.15, .1), (.11, .12)],
                loc=(x, -2.05, 1.6), rot=K.FORWARD, seg=10, caps=(False, False))
        a.part('Intake_screens', 'Steel').cyl(.13, .02, loc=(x, -2.0, 1.6), rot=(R90, 0, 0), seg=10, bevel=0)
        k.lathe(a.part('Exhaust', 'Charred'), [(.1, 0), (.12, .25), (.1, .25)], loc=(x + s * .05, -.3, 1.6),
                rot=(-R90, 0, s * .4), seg=8, caps=(True, False))
        K.soot(a, (x + s * .15, -.05, 1.6), radius=.4, k=.4)
        for y in (-1.7, -1.3, -.9):
            a.part('Engine_seams', 'Undercarriage').box((.33, .015, .015), loc=(x, y, 1.76), bevel=0)
    a.pivot('Point_exhaust', (.3, -.05, 1.6))
    a.part('Rotor_mast', 'Steel').cyl(.07, .25, loc=(ROTOR[0], ROTOR[1], 1.6), seg=8, bevel=0)


def _tail(a):
    """The swept fin, stabilisers, the tail rotor; the gear; flares, lights and antennas."""
    fin = a.part('Tail_fin', 'Team')
    k.extrude(fin, [(3.35, 1.25), (3.85, 1.25), (4.0, 2.05), (3.8, 2.05)], .07, loc=(0, 0, 0), axis='X', chamfer=.01)
    for s in (-1, 1):
        k.block(a.part('Tailplanes', 'Team'), (.6, .25, .04), loc=(s * .36, 3.3, 1.25), chamfer=.01, taper=(1, .7))
    tr = a.pivot('Tail_rotor', TR)
    K.tail_rotor(a, tr, 5, .55, .07, side=-1)
    a.part('Tail_skid', 'Steel').tube([(0, 3.3, 1.05), (0, 3.45, .75), (0, 3.6, .78)], .02, seg=4)
    # Main gear in sponsons with twin wheels, the twin nose wheel.
    for s in (-1, 1):
        k.extrude(a.part('Sponsons', 'Team'), [(-.0, 0), (.25, 0), (.2, .35), (0, .4)], 1.1,
                  loc=(s * .5, .55, .32), rot=(0, 0, 0 if s > 0 else math.pi), axis='Y', chamfer=.02)
        K.landing_gear(a, (s * .72, .55, .42), wheel_r=.15, leg=.27, width=.09, twin=True)
    K.landing_gear(a, (0, -2.65, .4), wheel_r=.12, leg=.28, width=.08, twin=True)
    # The UV-26 flare launchers on the rear flanks, beacons, nav lights, antennas.
    for s in (-1, 1):
        k.block(a.part('Launchers_flares', 'Armor'), (.06, .35, .2), loc=(s * .5, 1.75, .85), chamfer=.01)
        cells = a.part('Flare_cells', 'Undercarriage')
        for i in range(3):
            for j in range(2):
                cells.box((.01, .08, .06), loc=(s * .535, 1.65 + i * .1, .8 + j * .09), bevel=0)
        a.part('Nav_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.05, .08, .05),
                                                                         loc=(s * .75, .55, .6), bevel=0)
    a.part('Beacons', 'BarrelRed').sphere(.05, loc=(0, .9, 1.42), seg=8, rings=4)
    a.part('Beacons', 'BarrelRed').sphere(.04, loc=(0, -1.2, .29), seg=8, rings=4)
    ant = a.part('Antennas', 'Steel')
    K.blade_antenna(ant, (0, 1.4, 1.38), h=.18, chord=.12)
    K.blade_antenna(ant, (0, -1.6, .3), h=.12, chord=.1, normal=(0, 0, -1))
    K.whip_antenna(ant, (.2, 2.4, 1.08), h=.3, r=.012, lean=.5)
    a.part('Pitot', 'Steel').cyl(.012, .25, loc=(.25, -3.15, .9), rot=(R90, 0, 0), seg=5, bevel=0)


def heavy_lift_helicopter(a):
    _fuselage(a)
    _engines(a)
    _tail(a)
    r = a.pivot('Rotor', ROTOR)
    K.rotor_head(a, r, 8, 3.29, .2, hub=.2, cap=.14, stripe=.25)
    k.clean(a)


BUILDERS = {'heavy_lift_helicopter': (heavy_lift_helicopter, dict(ao_distance=.4, grime_height=.2, ground=False))}
