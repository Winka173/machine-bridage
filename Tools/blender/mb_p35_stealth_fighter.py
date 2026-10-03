"""Prompt 35 wave 9 (lane C): the stealth fighter rebuilt from scratch (spec: Tools/blender/specs/stealth_fighter.json).

A fifth-generation stealth fighter after unit_refs (F-22 Raptor's trapezoid wing, caret intakes, 2D nozzles and two
canted tails; the J-20's long chined nose; the F-35's one-piece canopy; GAU-22/A 25 mm; play-test 9 / DECISIONS
23M: steel grey, the team colour only on the fin tips, wingtips and canopy edge; the def's modelSize 7.6 x 5.5 x
1.28 m): the flat faceted fuselage with the sharp chine from the nose flaring into the wing roots, the one-piece
canopy on its frame, the caret intakes with their diverterless bumps, the broad trapezoid wing with its
sawtooth panel lines, the all-moving stabilators, the two outward-canted fins, the two flat 2D nozzles with their
dark throats; the weapon bays open for the attack: the two side bays' doors up with an AIM-9X on each trapeze
(`Racks`, `Muzzle_missile`) and the main bay's doors hanging open over two GBU-39s and an AIM-120 (`Muzzle_bomb`),
the gun port over the right wing root (`Muzzle_gun`), the flare dispensers under the rear fuselage (`Flares`).

Runtime nodes kept: `Muzzle_missile`, `Muzzle_bomb`, `Muzzle_gun`, `Point_exhaust`, `Point_fire` (the wrappers add
`Part_wing` and `Mount_Flare_*`). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
BODY = 'Armor'
ZC = .42             # the fuselage's chine height
NOSE, TAIL = -3.8, 3.75


def _fuselage(a):
    f = a.part('Fuselage', BODY)

    def sec(w, bot, top, chine=ZC, hump=.0):
        return [(0, bot), (w * .35, bot + .01), (w * .7, bot + .04), (w * .92, chine - .03), (w, chine),
                (w * .8, chine + (top - chine) * .45), (w * .55, top - .03 + hump * .6), (w * .25, top + hump * .95),
                (0, top + hump)]
    C.section_loft(f, [
        (NOSE, sec(.03, ZC - .01, ZC + .01)),
        (NOSE + .5, sec(.16, ZC - .08, ZC + .08)),
        (NOSE + .85, sec(.25, ZC - .11, ZC + .11, hump=.02)),
        (NOSE + 1.2, sec(.32, ZC - .14, ZC + .14, hump=.04)),
        (NOSE + 1.55, sec(.4, ZC - .17, ZC + .15, hump=.08)),
        (-1.9, sec(.5, ZC - .2, ZC + .16, hump=.1)),
        (-1.0, sec(.78, ZC - .22, ZC + .17, hump=.06)),
        (-.2, sec(.84, ZC - .22, ZC + .17, hump=.03)),
        (.6, sec(.86, ZC - .22, ZC + .16)),
        (1.4, sec(.84, ZC - .21, ZC + .15)),
        (2.2, sec(.8, ZC - .2, ZC + .14)),
        (3.1, sec(.62, ZC - .15, ZC + .12)),
        (3.45, sec(.55, ZC - .12, ZC + .1)),
    ])
    # The one-piece canopy, its frame with the team-coloured edge.
    k.lathe(a.part('Canopy', 'Glass'), [(0, -.55), (.12, -.5), (.17, -.3), (.18, 0), (.16, .3), (.1, .5), (0, .58)],
            loc=(0, -2.35, ZC + .2), rot=K.FORWARD, seg=16)
    fr = a.part('Canopy_frame', 'Team')
    fr.tube([(-.17, -2.85, ZC + .17), (-.18, -2.35, ZC + .22), (-.15, -1.8, ZC + .2)], .015, seg=4)
    fr.tube([(.17, -2.85, ZC + .17), (.18, -2.35, ZC + .22), (.15, -1.8, ZC + .2)], .015, seg=4)
    # The caret intakes under the chines with their bumps.
    for s in (-1, 1):
        K.intake(a.part('Intakes', BODY), a.part('Panel_lines', 'Undercarriage'), (s * .62, -1.45, ZC - .1), .26, .3,
                 .55, facing=(s * .25, -1, 0), lip=.025)
        a.part('Kit_steel', 'Steel').box((.02, .02, .32), loc=(s * .74, -1.72, ZC - .1), rot=(0, 0, s * .25),
                                           bevel=0)
        k.lathe(a.part('Fuselage', BODY), [(.12, 0), (.1, .1), (0, .14)], loc=(s * .45, -1.6, ZC - .05),
                rot=(0, s * R90, 0), seg=8)
    # The 2D nozzles and their dark throats, the tail boom between them.
    for s in (-1, 1):
        nz = a.part('Nozzles', 'Steel')
        k.extrude(nz, [(-.17, -.1), (.17, -.1), (.15, .1), (-.15, .1)], .45, loc=(s * .3, 3.55, ZC - .04),
                  axis='Y', chamfer=.015, corner=.02)
        a.part('Exhaust_glow', 'Undercarriage').box((.26, .02, .14), loc=(s * .3, 3.785, ZC - .04), bevel=0)
        a.part('Kit_steel', 'Steel').box((.32, .3, .02), loc=(s * .3, 3.7, ZC + .07), rot=(-.12, 0, 0), bevel=0)
    a.part('Fuselage', BODY).box((.18, .7, .1), loc=(0, 3.45, ZC + .02), bevel=0)
    a.pivot('Point_exhaust', (.3, 3.82, ZC - .04))
    a.pivot('Point_fire', (0, .8, ZC + .1))
    # The gun port over the right wing root, panel lines, the air data probes.
    a.part('Panel_lines', 'Undercarriage').box((.12, .2, .03), loc=(-.72, -.6, ZC + .12), bevel=0)
    a.pivot('Muzzle_gun', (-.72, -.72, ZC + .12))
    pl = a.part('Panel_lines', 'Undercarriage')
    for y in (-1.2, .1, 1.5):
        pl.box((1.2, .015, .005), loc=(0, y, ZC + .17), bevel=0)
    for s in (-1, 1):
        a.part('Kit_steel', 'Steel').box((.02, .12, .02), loc=(s * .2, NOSE + 1.0, ZC + .05), bevel=0)
    K.flare_dispenser(a, (0, 2.9, ZC - .2), normal=(0, 0, -1), cols=3, rows=2, cell=.05)
    # Sensors (the distributed aperture windows, the nose EO window), blade antennas, formation light strips,
    # the refuelling door, the retracted gear doors' sawtooth seams.
    sen = a.part('Sensor', 'Glass')
    sen.box((.1, .12, .02), loc=(0, NOSE + .9, ZC - .11), rot=(.2, 0, 0), bevel=0)
    for s in (-1, 1):
        sen.box((.02, .08, .06), loc=(s * .3, -2.6, ZC + .05), rot=(0, 0, s * .2), bevel=0)
        sen.box((.06, .08, .02), loc=(s * .45, .9, ZC + .18), bevel=0)
        a.part('Lamps', 'Lamp').box((.015, .25, .015), loc=(s * .78, -.4, ZC + .02), rot=(0, 0, s * .12), bevel=0)
    ant = a.part('Antennas', 'Steel')
    for y, z, nrm in ((-1.3, ZC + .26, (0, 0, 1)), (1.8, ZC - .2, (0, 0, -1)), (-.4, ZC - .22, (0, 0, -1))):
        K.blade_antenna(ant, (0, y, z), h=.1, chord=.12, normal=nrm)
    a.part('Panel_lines', 'Undercarriage').box((.16, .3, .01), loc=(0, -.2, ZC + .21), bevel=0)
    gd = a.part('Panel_lines', 'Undercarriage')
    for x, y, l in ((0, -2.3, .55), (.5, .2, .7), (-.5, .2, .7)):
        gd.tube([(x - .1, y - l / 2, ZC - .225), (x + .1, y - l / 2 + .08, ZC - .225), (x + .1, y + l / 2 - .08, ZC - .225),
                 (x - .1, y + l / 2, ZC - .225), (x - .1, y - l / 2, ZC - .225)], .006, seg=3)


def _wings(a):
    w = a.part('Wings', BODY)
    K.wing(w, (-1.25, 2.75), (1.05, .75), 2.15, x0=.6, z=ZC, t=.045)
    tip = a.part('Wingtips', 'Team')
    for s in (-1, 1):
        tip.box((.05, .7, .03), loc=(s * 2.72, 1.42, ZC), rot=(0, 0, s * .03), bevel=0)
        a.part('Fuselage', BODY).box((.9, .3, .02), loc=(s * 1.4, 1.9, ZC - .01), rot=(.1, 0, s * -.05), bevel=0)
        a.part('Panel_lines', 'Undercarriage').box((1.5, .015, .005), loc=(s * 1.4, .4, ZC + .04), rot=(0, 0, s * -.5),
                                                   bevel=0)
    # The two-tone grey camouflage (lighter patches over the wings) and the sawtooth panel seams.
    cam = a.part('Camo_panels', 'Steel')
    import random
    rng = random.Random(23)
    for s in (-1, 1):
        for x0, y0, w0, l0 in ((1.0, .2, .7, .9), (1.9, 1.0, .5, .55), (1.3, 1.65, .45, .35), (.5, -.6, .3, .5)):
            pts = [(s * (x0 - w0 / 2), y0 - l0 / 2), (s * (x0 + w0 / 2), y0 - l0 / 2 + rng.uniform(.1, .3)),
                   (s * (x0 + w0 / 2 - .1), y0 + l0 / 2), (s * (x0 - w0 / 2 + .1), y0 + l0 / 2 - rng.uniform(0, .2))]
            if s < 0:
                pts = pts[::-1]
            z = ZC + .035 + (.01 if x0 < .7 else 0)
            cam.mesh([(px, py, z) for px, py in pts], [(0, 1, 2, 3)])
        saw = a.part('Panel_lines', 'Undercarriage')
        for j in range(5):
            saw.box((.12, .012, .004), loc=(s * (1.0 + j * .3), 1.1 + j * .05, ZC + .038), rot=(0, 0, s * .6), bevel=0)
    for y0, l0 in ((-1.5, .7), (.2, .9), (1.9, .7)):
        cam.mesh([(-.3, y0, ZC + .2), (.3, y0 + .1, ZC + .2), (.25, y0 + l0, ZC + .18), (-.22, y0 + l0 - .15, ZC + .18)],
                 [(0, 1, 2, 3)])
    st = a.part('Tailplanes', BODY)
    K.wing(st, (2.45, 1.25), (3.25, .5), 1.15, x0=.55, z=ZC - .02, t=.04)
    fins = a.part('Fins', BODY)
    for s in (-1, 1):
        K.fin(fins, (1.85, 1.45), (2.75, .65), .7, x=s * .55, z0=ZC + .08, t=.06, cant=s * .48)
        top = (s * (.55 + math.sin(.48) * .7), 2.95, ZC + .08 + .7 * math.cos(.48) * .98)
        a.part('Fin_tips', 'Team').box((.05, .62, .05), loc=top, rot=(0, s * .48, 0), bevel=0)
        a.part('Kit_steel', 'Steel').box((.03, .25, .5), loc=(s * (.55 + math.sin(.48) * .4), 3.0, ZC + .45),
                                       rot=(0, s * .48, 0), bevel=0)


def _bays(a):
    """The open weapon bays: side bays with an AIM-9X each, the main bay with two GBU-39s and an AIM-120."""
    for s in (-1, 1):
        x = s * .62
        a.part('Bay_doors', BODY).box((.03, 1.0, .22), loc=(x + s * .1, -.6, ZC - .02), rot=(0, s * .5, 0), bevel=0)
        rk = a.part('Racks', 'Steel')
        rk.box((.03, .5, .12), loc=(x + s * .1, -.6, ZC - .2), rot=(0, -s * .5, 0), bevel=0)
        C.store(a, (x + s * .2, -.15, ZC - .3), .045, 1.0, seg=10)
        if s > 0:
            a.pivot('Muzzle_missile', (x + s * .2, -1.17, ZC - .3))
    # The main bay: the doors hanging open, the stores on their racks.
    for s in (-1, 1):
        a.part('Bay_doors', BODY).box((.02, 1.8, .34), loc=(s * .4, .5, ZC - .38), rot=(0, s * .15, 0), bevel=0)
    a.part('Panel_lines', 'Undercarriage').box((.62, 1.8, .02), loc=(0, .5, ZC - .2), bevel=0)
    rk = a.part('Racks', 'Steel')
    for x in (-.16, .16):
        rk.box((.04, 1.2, .05), loc=(x, .5, ZC - .25), bevel=0)
    for x in (-.16, .16):
        C.store(a, (x, 1.15, ZC - .33), .055, 1.2, kind='bomb', body='Bombs', body_mat='Steel', fins='Bomb_fins')
    C.store(a, (0, 1.25, ZC - .44), .06, 1.5, seg=10)
    a.pivot('Muzzle_bomb', (.16, -.1, ZC - .33))


def stealth_fighter(a, detail=False):
    """The stealth fighter: see the module docstring."""
    _fuselage(a)
    _wings(a)
    _bays(a)
    k.clean(a)


BUILDERS = {
    'stealth_fighter': (stealth_fighter, dict(ao_distance=.25, grime_height=.0)),
}
