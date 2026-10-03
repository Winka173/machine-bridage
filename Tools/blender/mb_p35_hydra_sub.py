"""Prompt 35 wave 6 (lane B): Hydra, the drone submarine, rebuilt from scratch (spec: Tools/blender/specs/hydra_sub.json).

General Hung's Hydra (variant of typhon keeping doors_l, doors_r, deck_gun, rudder; BossText: a small submarine with
vertical launch tubes along its back, it surfaces to launch drones; tip: the launch doors carry its missiles, the
deck gun only shoots when it is up). A small surfaced SSGN in the Yasen / Oscar line, its features drawn 1.3-1.5 x
for the boss read (the def's modelSize 34.8 x 7.2 x 8 m, hull axis at z 0, the waterline just above): the lathed
pressure hull with the bow dome, the dark anechoic-tiled lower half and the hull's tile seams, the free-flooding
casing deck with its limber holes and the safety track; the tall sail with its fairwater planes, the windows of the
bridge cockpit, the masts (periscope, radar, snorkel, the comms mast) and the SAM box on top (`Mount_missile` >
`Muzzle_missile`); the 100 mm deck gun in its faceted mount forward of the sail (`Mount_gun` > `Muzzle_gun`); the
weak points: ten launch tubes behind the sail under two rows of riveted hatch plates one shade off the hull
(`Part_doors_l`, `Part_doors_r`), the drone deck aft with six FPV quadcopters on their pads (`Part_drone` ..
`Part_drone.005`), the cruciform stern planes and the shrouded pump-jet (`Part_rudder`); bollards, cleats, the
capstan, the escape hatches, warning lights, Hung's colour bands.

Its own hull: nothing is taken from typhon or another boss. Runtime nodes kept: `Mount_gun`, `Muzzle_gun`,
`Mount_missile`, `Muzzle_missile`, `Part_doors_l`, `Part_doors_r`, `Part_rudder`, `Part_drone` .. `.005` (the
wrapper twins the deck gun's barrel and adds the per-barrel muzzles). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
BOW, STERN = -17.4, 17.4
R = 2.45                         # pressure hull radius
DECK = 2.55                      # casing deck height


def hull_r(y):
    """The pressure hull's radius at y: the round bow, the parallel middle body, the long stern cone."""
    if y < -13.0:
        f = (y - BOW) / 4.4
        return R * math.sqrt(max(0.0, 1 - (1 - f) ** 2))
    if y > 9.0:
        f = (y - 9.0) / (STERN - 9.0)
        return R * (1 - .78 * f ** 1.4)
    return R


def _hull(a):
    prof = [(0, 0)]
    ys = [BOW + .3, -16.4, -15.4, -14.2, -13.0, -6.0, 3.0, 9.0, 11.5, 13.5, 15.2, 16.4, STERN - .1]
    hull = a.part('Hull', 'Team')
    for y in ys:
        prof.append((max(hull_r(y), .3), y))
    k.lathe(hull, [(r, -y) for r, y in prof[1:]], loc=(0, 0, 0), rot=(R90, 0, 0), seg=24, caps=(True, True))
    # The dark anechoic-tiled lower half (a skin just outside it below the waterline band), the tile seams.
    low = a.part('Hull_low', 'Undercarriage')
    rings = []
    for y in ys[1:-1]:
        r = max(hull_r(y), .3) + .015
        rings.append([(math.cos(u) * r, y, math.sin(u) * r) for u in [math.pi + i * math.pi / 8 for i in range(9)]])
    for ra, rb in zip(rings, rings[1:]):
        for i in range(8):
            low.mesh([ra[i], rb[i], rb[i + 1], ra[i + 1]], [(0, 1, 2, 3)])
    tiles = a.part('Hull_tiles', 'Rubber')
    for y in range(-12, 9, 2):
        for u in (math.pi * 1.1, math.pi * 1.25, math.pi * 1.75, math.pi * 1.9):
            tiles.box((.04, 1.6, .04), loc=(math.cos(u) * (R + .03), y + .5, math.sin(u) * (R + .03)), rot=(0, u, 0),
                      bevel=0)
    for s in (-1, 1):
        a.part('Boot_top', 'Hazard').box((.03, 22.0, .12), loc=(s * (R + .02), -2.0, .25), bevel=0)
        a.part('Team_band', 'Team').box((.03, 6.0, .5), loc=(s * (R * .93 + .03), -10.0, 1.0), rot=(0, s * -.4, 0),
                                        bevel=0)
    # The casing deck on top, its limber holes along both sides, the safety track, escape hatches.
    k.extrude(a.part('Deck', 'Armor'), [(-1.3, -13.5), (1.3, -13.5), (1.6, -10.0), (1.6, 9.5), (1.0, 13.0), (-1.0, 13.0),
                                        (-1.6, 9.5), (-1.6, -10.0)], .35, loc=(0, 0, DECK - .1), axis='Z', chamfer=.04,
              corner=.1)
    holes = a.part('Limber_holes', 'Undercarriage')
    for s in (-1, 1):
        for i in range(22):
            y = -12.0 + i * 1.0
            holes.box((.02, .5, .12), loc=(s * (1.61 if -10 < y < 9.5 else 1.35), y, DECK - .05), bevel=0)
    a.part('Safety_track', 'Steel').box((.12, 24.0, .02), loc=(0, -.5, DECK + .085), bevel=0)
    for y in (-11.0, 8.0):
        K.hatch_round(a, (0.6, y, DECK + .07), r=.35, periscopes=0, seg=12)
    bol = a.part('Bollards', 'Steel')
    for s in (-1, 1):
        for y in (-12.5, -7.5, 7.0, 11.5):
            bol.cyl(.1, .22, loc=(s * 1.1, y, DECK + .18), seg=8, bevel=0)
    k.lathe(a.part('Capstan', 'Steel'), [(.3, 0), (.3, .1), (.22, .15), (.22, .35), (.3, .4), (0, .4)],
            loc=(0, -12.6, DECK + .07), seg=10)


def _sail(a):
    sail = a.part('Sail', 'Team')
    rings = []
    for z, f, r, w in ((DECK, -6.4, -1.6, .95), (4.2, -6.0, -2.0, .85), (4.95, -5.6, -2.3, .78)):
        rings.append([(0, f, z), (w * .7, f + .5, z), (w, f + 1.6, z), (w * .8, r - .3, z), (0, r, z), (-w * .8, r - .3, z),
                      (-w, f + 1.6, z), (-w * .7, f + .5, z)])
    k.sharp_loft(sail, rings, chamfer=.04)
    # The fairwater planes, the bridge cockpit windows, the masts.
    K.wing(a.part('Sail_planes', 'Armor'), (-5.3, 1.5), (-4.95, .95), 1.9, x0=.9, z=3.9, t=.08)
    K.ladder(a.part('Ladders', 'Steel'), (1.0, -3.0, DECK + .1), (.82, -3.0, 4.9), width=.4, step=.3)
    glass = a.part('Glass', 'Glass')
    for x in (-.35, 0, .35):
        glass.box((.28, .03, .18), loc=(x, -5.92, 4.75), rot=(.3, 0, 0), bevel=0)
    masts = a.part('Masts', 'Steel')
    for x, y, h, r in ((0, -4.0, .42, .1), (.35, -3.5, .3, .08), (-.35, -3.2, .38, .12), (0, -2.7, .25, .07)):
        masts.cyl(r, h, loc=(x, y, 4.95 + h / 2), seg=8, bevel=0)
    k.block(a.part('Radar_mast', 'Armor'), (.4, .25, .16), loc=(.35, -3.5, 5.22), chamfer=.03)
    a.part('Warning_lights', 'LavaGlow').box((.08, .08, .06), loc=(0, -4.0, 5.38), bevel=0)
    # The SAM box on top of the sail (`Mount_missile`), its four cells.
    m = a.pivot('Mount_missile', (0, -4.6, 4.75))
    k.block(a.part('Launcher_box', 'Armor', m), (.8, 1.3, .55), loc=(0, .1, .22), chamfer=.04)
    cells = a.part('Launcher_tubes_bore', 'Undercarriage', m)
    for x in (-.18, .18):
        for z in (.36, .62):
            cells.box((.26, .02, .2), loc=(x, -.56, z), bevel=0)
    a.pivot('Muzzle_missile', (0, -.75, .45), m)


def _deck_gun(a):
    """The 100 mm deck gun forward of the sail on its faceted mount (`Mount_gun`), a single barrel."""
    k.lathe(a.part('Gun_ring_gun', 'Steel'), [(.95, 0), (.95, .1), (.85, .15), (0, .15)], loc=(0, -9.6, DECK + .07),
            seg=16)
    m = a.pivot('Mount_gun', (0, -9.6, 2.55))
    rings = []
    for z, f, w, r in ((.1, -.9, .8, 1.1), (.75, -.6, .7, 1.05), (1.0, -.1, .45, .9)):
        rings.append([(-w * .55, f, z), (w * .55, f, z), (w, f + .5, z), (w, r, z), (-w, r, z), (-w, f + .5, z)])
    k.sharp_loft(a.part('Gun_house_gun', 'Team', m), rings, chamfer=.04)
    k.lathe(a.part('Gun_steel_gun', 'Steel', m), [(.12, 0), (.12, .2), (.08, .3), (.065, 2.6), (0, 2.6)],
            loc=(0, -.85, .31), rot=K.FORWARD, seg=10, worn=(1,))
    k.lathe(a.part('Gun_brake_gun', 'Undercarriage', m), [(.065, 0), (.09, .03), (.09, .22), (.07, .25), (0, .25)],
            loc=(0, -3.3, .31), rot=K.FORWARD, seg=10)
    a.pivot('Muzzle_gun', (0, -3.5, .31), m)
    a.part('Gun_glass_gun', 'Glass', m).box((.25, .02, .1), loc=(.4, -.65, .65), bevel=0)
    K.soot(a, (0, -13.1, 2.86), radius=.7, k=.35)


def _tubes(a):
    """The weak points: ten launch tubes under two rows of riveted hatches, one shade off (`Part_doors_l` / `_r`)."""
    for name, s in (('Part_doors_l', 1), ('Part_doors_r', -1)):
        p = a.pivot(name, (s * .7, 3.7, 2.53))
        plates = a.part(name.replace('Part_', 'Door_') + '_plates', 'Armor', p)
        rivets = a.part('Kit_rivets', 'Steel', p)
        for i in range(5):
            y = -3.0 + i * 1.5
            k.block(plates, (1.1, 1.3, .12), loc=(0, y, .02), chamfer=.03)
            for dx in (-.42, .42):
                for dy in (-.5, .5):
                    rivets.box((.06, .06, .04), loc=(dx, y + dy, .15), bevel=0)
            a.part('Door_hinges', 'Steel', p).cyl(.05, .9, loc=(-s * .5, y, .12), rot=(0, R90, 0), seg=6, bevel=0)
        a.part('Door_bands', 'BarrelRed', p).box((.06, 7.2, .02), loc=(s * .56, 0, .09), bevel=0)
        K.tone(a, name, k=.86)


def _drones(a):
    """The drone deck aft: six FPV quadcopters on their pads (`Part_drone` .. `.005`)."""
    k.block(a.part('Drone_deck', 'Armor'), (2.3, 4.6, .1), loc=(0, 10.9, DECK + .1), chamfer=.03)
    marks = a.part('Drone_marks', 'Hazard')
    for i, (x, y) in enumerate(((.62, 9.4), (-.62, 9.4), (.62, 10.9), (-.62, 10.9), (.62, 12.4), (-.62, 12.4))):
        marks.box((.9, .9, .01), loc=(x, y, DECK + .205), bevel=0)
        p = a.pivot(K.name('Part_drone', i), (x, y, 2.62))
        k.block(a.part('Fpv_body', 'Team', p), (.22, .34, .12), loc=(0, 0, .1), chamfer=.02)
        arms = a.part('Fpv_arms', 'Undercarriage', p)
        rot = a.part('Fpv_rotors', 'Rubber', p)
        for ax, ay in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            arms.tube([(0, 0, .14), (ax * .26, ay * .26, .16)], .02, seg=4)
            rot.cyl(.16, .015, loc=(ax * .26, ay * .26, .2), seg=8, bevel=0)
        a.part('Fpv_charge', 'Fuel', p).cyl(.05, .3, loc=(0, -.05, .02), rot=K.FORWARD, seg=6, bevel=0)
        a.part('Fpv_eye', 'Glass', p).box((.06, .03, .05), loc=(0, -.18, .12), bevel=0)


def _stern(a):
    """The cruciform stern planes and the shrouded pump-jet on `Part_rudder`."""
    p = a.pivot('Part_rudder', (0, 14.6, 0))
    pl = a.part('Stern_planes', 'Armor', p)
    for ang in (0, R90, math.pi, -R90):
        c, s = math.cos(ang), math.sin(ang)
        pl.loft([[(c * .5, -.6, s * .5), (c * .5, .9, s * .5), (c * .5 - s * .06, .9, s * .5 + c * .06),
                  (c * .5 - s * .06, -.6, s * .5 + c * .06)],
                 [(c * (3.55 if abs(c) > .5 else 2.4), .3, s * (3.55 if abs(c) > .5 else 2.4)),
                  (c * (3.55 if abs(c) > .5 else 2.4), 1.35, s * (3.55 if abs(c) > .5 else 2.4)),
                  (c * (3.55 if abs(c) > .5 else 2.4) - s * .04, 1.35, s * (3.55 if abs(c) > .5 else 2.4) + c * .04),
                  (c * (3.55 if abs(c) > .5 else 2.4) - s * .04, .3, s * (3.55 if abs(c) > .5 else 2.4) + c * .04)]])
    for sx in (-1, 1):
        a.part('Plane_tips', 'Steel', p).box((.08, 1.1, .3), loc=(sx * 3.55, .8, 0), bevel=0)
    k.ring(a.part('Pump_jet', 'Team', p), [(.85, 1.6), (1.0, 1.6), (1.05, 2.3), (.95, 2.75), (.85, 2.75)],
           rot=(-R90, 0, 0), seg=16, worn=(2,))
    a.part('Pump_jet_dark', 'Undercarriage', p).cyl(.8, .05, loc=(0, 2.7, 0), rot=K.BACKWARD, seg=16, bevel=0)
    k.lathe(a.part('Pump_hub', 'Steel', p), [(0, 0), (.3, .1), (.35, .6), (0, .9)], loc=(0, 1.8, 0), rot=K.BACKWARD,
            seg=10)
    K.tone(a, 'Part_rudder', k=.88)


def _fittings(a):
    """The flank sonar arrays on both sides (panels of different lengths), casing vents, fittings and sensor domes."""
    arr = a.part('Flank_arrays', 'Armor')
    for s in (-1, 1):
        for i, (y, L) in enumerate(((-11.5, 2.2), (-8.6, 2.8), (-5.2, 3.2), (-1.4, 2.6), (2.0, 3.0), (5.6, 2.4))):
            u = s * .28
            x, z = s * (R + .04) * math.cos(u), (R + .04) * math.sin(-.28)
            arr.box((.06, L, .7 + .1 * (i % 3)), loc=(x, y, z + .2), rot=(0, -u, 0), bevel=0)
    P.clutter(a, 'Casing_fittings', 'Steel', -1.2, 1.2, -9.0, -7.0, DECK + .25, 6, seed=61, size=(.15, .5),
              height=(.08, .3), gap=.15)
    P.clutter(a, 'Casing_fittings', 'Steel', -1.3, 1.3, 7.5, 8.6, DECK + .25, 5, seed=62, size=(.15, .45),
              height=(.08, .3), gap=.15)
    P.clutter(a, 'Casing_fittings', 'Steel', -1.2, 1.2, -1.2, -.2, DECK + .25, 4, seed=63, size=(.15, .4),
              height=(.08, .25), gap=.15)
    for y in (-15.0, -14.2):
        k.lathe(a.part('Sensor_domes', 'Armor'), [(.25, 0), (.25, .1), (0, .3)], loc=(0, y, DECK - .55 + (y + 15) * .3),
                seg=8)
    for s in (-1, 1):
        a.part('Nav_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.1, .1, .08), loc=(s * .78, -5.0, 4.6),
                                                                          bevel=0)


def hydra_sub(a):
    """Hydra: see the module docstring."""
    K.suffixed(a)
    _hull(a)
    _sail(a)
    _deck_gun(a)
    _tubes(a)
    _drones(a)
    _stern(a)
    _fittings(a)
    k.clean(a)


BUILDERS = {
    'hydra_sub': (hydra_sub, dict(ao_distance=1.0, grime_height=.45)),
}
