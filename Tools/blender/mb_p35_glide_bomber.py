"""Prompt 35 wave 6 (lane B): the glide bomber rebuilt from scratch (spec: Tools/blender/specs/glide_bomber.json).

An Su-34-class strike fighter-bomber with UMPK glide bombs (the def's modelSize 9.3 x 5.9 x 2.4 m; about 0.42 x the
real aircraft): the broad flat "platypus" nose with its chines, the side-by-side cockpit under a wide canopy with
frames, the canards, the long blended leading-edge root extensions over the intakes, the two engine nacelles spaced
by the tunnel, the intakes under the root extensions with their ramps and dark ducts, the Flanker wing with the tip
launch rails, the twin fins with rudders, the tailplanes, the two ventral fins, the central tail stinger with its
radar, the nozzles with petals and glow; under the wings two FAB-500 bombs with their UMPK glide wing kits and tail
fins on heavy pylons (`Bombs`), the centre-line rack under the tunnel (`Muzzle_missile`), two rows of flare
dispensers a side on the nacelles (the wrapper's `Mount_Flare_L` / `_L2` / `_R` / `_R2` / `_TL` / `_TR`), the
refuelling probe, pitot, blade antennas, lights and Team bands. Jet rule: no insets or panel greebles on the skin.

Its own fuselage, wing and tails (not interceptor_jet's or fighter_jet's). Runtime nodes kept: `Muzzle_missile`;
the wrappers add `Part_wing` and the `Mount_Flare_*` points; old part names `Fuselage`, `Nose_flat`, `Nacelles`,
`Wings`, `Fins`, `Tails`, `Canopy`, `Bombs`, `Bomb_wings`, `Flares`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
NOSE, TAIL = -4.65, 4.6


def _fuselage(a):
    fus = a.part('Fuselage', 'Team')
    rings = []
    # The forward fuselage: the flat wide nose, the cockpit section, blending into the centre body.
    for y, w, top, bot in ((-4.6, .2, .08, -.04), (-4.2, .36, .16, -.1), (-3.6, .46, .3, -.2), (-2.9, .5, .44, -.26),
                           (-2.1, .52, .46, -.28), (-1.2, .5, .36, -.24), (.2, .44, .28, -.18), (1.8, .32, .24, -.14),
                           (3.0, .2, .18, -.1), (4.0, .12, .12, -.06)):
        rings.append([(-w * .7, y, top), (w * .7, y, top), (w, y, (top + bot) * .5), (w * .7, y, bot), (-w * .7, y, bot),
                      (-w, y, (top + bot) * .5)])
    k.sharp_loft(fus, rings, chamfer=.02)
    nf = a.part('Nose_flat', 'Armor')
    nf.loft([[(0, NOSE - .02, .02)], [(-.22, -4.45, .08), (.22, -4.45, .08), (.28, -4.45, .0), (-.28, -4.45, .0)],
             [(-.38, -4.0, .14), (.38, -4.0, .14), (.48, -4.0, .0), (-.48, -4.0, .0)]])
    # The wide canopy over the side-by-side seats, its frames.
    a.part('Canopy', 'Glass').loft([[(-.36, -3.4, .32), (.36, -3.4, .32), (.3, -3.4, .4), (-.3, -3.4, .4)],
                                    [(-.4, -2.8, .44), (.4, -2.8, .44), (.32, -2.8, .7), (-.32, -2.8, .7)],
                                    [(-.38, -2.2, .48), (.38, -2.2, .48), (.3, -2.2, .64), (-.3, -2.2, .64)]])
    fr = a.part('Canopy_frames', 'Armor')
    for y, z in ((-3.4, .42), (-2.8, .72), (-2.2, .66)):
        fr.tube([(-.38, y, z - .2), (0, y, z), (.38, y, z - .2)], .018, seg=4)
    fr.tube([(0, -3.4, .43), (0, -2.2, .67)], .016, seg=3)
    # Canards on the root extensions' front.
    K.wing(a.part('Canards', 'Team'), (-2.75, .55), (-2.45, .25), .65, x0=.5, z=.2, t=.05)
    # The engine nacelles with the tunnel between, intakes below the root extensions, nozzles.
    for s in (-1, 1):
        x = s * .55
        nac = a.part('Nacelles', 'Armor')
        nac.loft([[(x - .28, y, z0 - .28), (x + .28, y, z0 - .28), (x + .3, y, z0 + .18), (x - .3, y, z0 + .18)]
                  for y, z0 in ((-1.6, -.18), (.5, -.12), (2.8, -.08), (3.85, -.05))])
        k.extrude(a.part('Intakes', 'Armor'), [(-.26, -.24), (.26, -.24), (.26, .2), (-.26, .2)], 1.0,
                  loc=(x, -1.9, -.42), axis='Y', chamfer=.03)
        a.part('Intake_dark', 'Undercarriage').box((.4, .03, .34), loc=(x, -2.41, -.44), bevel=0)
        a.part('Intakes', 'Armor').box((.5, .45, .03), loc=(x, -2.2, -.2), rot=(.2, 0, 0), bevel=0)
        k.lathe(a.part('Nozzles', 'Steel'), [(.27, 0), (.27, .1), (.24, .3), (.21, .42), (.22, .44)],
                loc=(x, 3.85, -.05), rot=K.BACKWARD, seg=12, caps=(False, False), worn=(1,))
        pet = a.part('Nozzle_petals', 'Undercarriage')
        for i in range(12):
            u = i * TAU / 12
            pet.box((.05, .14, .01), loc=(x + math.cos(u) * .22, 4.22, -.05 + math.sin(u) * .22), rot=(0, -u, 0),
                    bevel=0)
        a.part('Exhaust_glow', 'LavaGlow').cyl(.18, .02, loc=(x, 4.22, -.05), rot=K.BACKWARD, seg=12, bevel=0)
        K.soot(a, (x, 4.35, -.05), radius=.45, k=.35)
    # The tail stinger between the nozzles with its rear radar.
    k.lathe(a.part('Stinger', 'Team'), [(.16, 0), (.17, 1.2), (.12, 1.6), (0, 1.7)], loc=(0, 3.0, .05), rot=K.BACKWARD,
            seg=10, worn=(1,))
    a.part('Stinger_radar', 'Undercarriage').cyl(.08, .05, loc=(0, 4.65, .05), rot=K.BACKWARD, seg=8, bevel=0)


def _wings(a):
    w = a.part('Wings', 'Team')
    # The root extensions blending into the wing, then the trapezoidal outer wing to the tip rails.
    K.wing(w, (-2.0, 3.2), (.95, 1.0), 2.3, x0=.6, z=.12, t=.05, dihedral=-.03, crank=(.18, -.85, 2.3))
    for s in (-1, 1):
        a.part('Wingtip_rails', 'Armor').box((.06, 1.1, .06), loc=(s * 2.92, 1.25, .06), bevel=0)
        a.part('Wing_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.05, .08, .05), loc=(s * 2.95, .65, .06),
                                                                          bevel=0)
        K.fin(a.part('Fins', 'Team'), (2.45, 1.3), (3.5, .6), 1.4, x=s * .62, z0=.12, t=.06, cant=s * .04)
        a.part('Rudders', 'Armor').box((.04, .3, .85), loc=(s * (.62 + .03), 3.85, .7), bevel=0)
        K.fin(a.part('Ventral_fins', 'Armor'), (2.9, .7), (3.3, .4), -.5, x=s * .7, z0=-.32, t=.06, cant=-s * .2)
        a.part('Team_band', 'Team').box((.012, .45, .25), loc=(s * (.62 + .02), 3.2, .85), bevel=0)
    K.wing(a.part('Tails', 'Team'), (3.1, 1.15), (3.85, .5), 1.25, x0=.75, z=-.02, t=.05, dihedral=-.04)


def _stores(a):
    # Two FAB-500 with UMPK glide kits under the wings on heavy pylons.
    for s in (-1, 1):
        x = s * 1.55
        K.pylon(a.part('Pylons', 'Armor'), x, -.1, 1.0, .1, -.24, w=.08)
        k.lathe(a.part('Bombs', 'Armor'), [(0, -.9), (.12, -.8), (.19, -.5), (.2, .4), (.14, .75), (.1, .85)],
                loc=(x, .45, -.52), rot=K.BACKWARD, seg=12, worn=(2,))
        bw = a.part('Bomb_wings', 'Steel')
        bw.box((1.5, .22, .025), loc=(x, .25, -.31), bevel=0)
        bw.box((.15, .35, .1), loc=(x, .25, -.35), bevel=0)
        for i in range(4):
            u = i * R90 + TAU / 8
            bw.box((.01, .26, .22), loc=(x + math.cos(u) * .15, 1.2, -.52 + math.sin(u) * .15), rot=(0, -u, 0), bevel=0)
        a.part('Bomb_bands', 'Hazard').cyl(.205, .04, loc=(x, -.1, -.52), rot=K.FORWARD, seg=12, bevel=0)
        K.missile(a, (s * 2.92, .5, .0), .045, 1.0, direction=(0, -1, 0), fins=4)
    # The centre-line rack under the tunnel, the main weapon's launch point.
    a.part('Racks', 'Undercarriage').box((.4, 1.4, .12), loc=(0, .3, -.36), bevel=0)
    a.pivot('Muzzle_missile', (0, .3, -.5))
    # Two rows of flare dispensers a side on the nacelles' rear, the probe, pitot, antennas, lights.
    for s in (-1, 1):
        for y in (3.15, 3.7):
            K.flare_dispenser(a, (s * .86, y, .05), normal=(s, 0, .2), cols=2, rows=2, cell=.05)
    a.part('Antennas', 'Steel').tube([(.3, -3.2, .3), (.36, -4.1, .22)], .022, seg=5)
    a.part('Antennas', 'Steel').tube([(0, -4.55, .04), (0, -4.7, .04)], .012, seg=4)
    for y, z, n in ((-1.6, .38, (0, 0, 1)), (1.0, .28, (0, 0, 1)), (.0, -.3, (0, 0, -1))):
        K.blade_antenna(a.part('Antennas', 'Steel'), (0, y, z), h=.12, chord=.12, normal=n)
    a.part('Lamps', 'Lamp').box((.05, .05, .04), loc=(0, -1.6, -.3), bevel=0)
    a.part('Beacons', 'LavaGlow').box((.05, .08, .04), loc=(0, 1.6, .3), bevel=0)
    a.pivot('Point_fire', (0, .5, .4))
    a.pivot('Point_exhaust', (0, 4.3, -.05))


def glide_bomber(a):
    """The glide bomber: see the module docstring."""
    _fuselage(a)
    _wings(a)
    _stores(a)
    P.merge_parts(a, {'Canopy_frames': 'Rudders', 'Wingtip_rails': 'Pylons', 'Stinger_radar': 'Intake_dark',
                      'Missile_bands': 'Bomb_bands', 'Missile_seekers': 'Canopy', 'Missile_fins': 'Bomb_wings',
                      'Ventral_fins': 'Rudders', 'Stinger': 'Fuselage', 'Canards': 'Tails'})
    k.clean(a)


BUILDERS = {
    'glide_bomber': (glide_bomber, dict(ao_distance=.4, ground=False)),
}
