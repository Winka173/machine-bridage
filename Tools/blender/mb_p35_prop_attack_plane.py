"""Prompt 35 wave 11 (lane C): the turboprop light attack aircraft rebuilt from scratch (spec: Tools/blender/specs/prop_attack_plane.json).

An EMB-314 Super Tucano (A-29) pattern (the def's modelSize 6.15 x 6.04 x 1.84 m: about 0.54 x the real aircraft):
the long turboprop nose with its cowling panels, the chin intake, the exhaust stubs either side, the spinner and
the five-bladed propeller (`Propeller`); the stepped tandem canopy with its frame bows and the two crew; the low
straight-tapered wing with dihedral, its ailerons and flaps scribed, wingtip lights; the tall swept fin with its
dorsal fillet and rudder, the tailplanes with their elevators, the ventral strake; the main gear doors and the nose
gear doors closed; two pylons carrying seven-shot Hydra pods (the def's scout_rockets) and the 12.7 mm gun in its
fairing on the left wing (the def's main hmg_roof: `Muzzle_gun` / `Muzzle_main`); flare dispensers under the rear
fuselage, aerials, the pitot, team bands.

Runtime nodes kept where they were: `Propeller` (0, -2.66, .82), `Muzzle_gun` and `Muzzle_main` (-2.3, -1.1, .62),
`Muzzle_rocket` / `.001` (-1.5 / 1.5, -.75, .22), `Point_exhaust` (.3, -2.0, .55), `Point_fire` (0, -.2, .8); the
wrappers add `Part_wing` and `Mount_Flare_*`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C
import mb_parts27 as p27
from mb_air import _blade

R90 = math.pi / 2
TAU = math.tau
ZC = .8              # the fuselage's centre line


def _fuselage(a):
    body = a.part('Fuselage', 'Team')
    E = C.ellipse_half
    C.section_loft(body, [
        (-2.58, E(.13, .13, ZC + .02, 10)),
        (-2.45, E(.21, .22, ZC, 10)),
        (-2.1, E(.25, .27, ZC - .01, 10)),
        (-1.5, E(.27, .3, ZC, 10)),
        (-1.0, E(.29, .33, ZC + .03, 10)),
        (-.6, E(.3, .34, ZC + .04, 10)),
        (-.2, E(.3, .34, ZC + .05, 10)),
        (.5, E(.28, .32, ZC + .07, 10)),
        (1.3, E(.21, .25, ZC + .1, 10)),
        (1.8, E(.17, .21, ZC + .12, 10)),
        (2.2, E(.13, .17, ZC + .14, 10)),
        (2.95, E(.06, .08, ZC + .18, 10)),
    ])
    # Cowling panel lines, the chin intake, the exhaust stubs.
    cow = a.part('Cowl_seams', 'Undercarriage')
    for y in (-2.25, -1.75):
        k.ring(cow, [(.24, -.008), (.272, -.008), (.272, .008), (.24, .008)], loc=(0, y, ZC), rot=K.FORWARD, seg=12)
    K.intake(a.part('Intakes', 'Team'), a.part('Intake_dark', 'Undercarriage'), (0, -2.38, ZC - .26), .2, .1, .3,
             facing=(0, -1, 0), lip=.02)
    for s in (-1, 1):
        ex = a.part('Exhausts', 'Steel')
        k.lathe(ex, [(.045, 0), (.05, .1), (.042, .14)], loc=(s * .27, -1.95, ZC - .2),
                rot=K.rot_to((s * .6, .7, -.2)), seg=8, worn=(1,))
        K.soot(a, (s * .32, -1.85, ZC - .22), radius=.3, k=.35)
        a.part('Team_band', 'Team').box((.01, .4, .08), loc=(s * .285, .9, ZC + .05), bevel=0)
    a.pivot('Point_exhaust', (.3, -2.0, .55))
    a.pivot('Point_fire', (0, -.2, .8))
    # The tandem canopy (two stepped bubbles), its bows and sills, the crew.
    glass = a.part('Canopy', 'Glass')
    C.section_loft(glass, [
        (-1.35, E(.05, .05, ZC + .3, 6)),
        (-1.2, E(.2, .17, ZC + .3, 6)),
        (-.85, E(.25, .26, ZC + .32, 6)),
        (-.45, E(.25, .3, ZC + .34, 6)),
        (-.05, E(.24, .33, ZC + .35, 6)),
        (.35, E(.22, .3, ZC + .34, 6)),
        (.75, E(.12, .14, ZC + .32, 6)),
    ])
    fr = a.part('Canopy_frames', 'Team')
    for y, w, h, z in ((-1.2, .2, .17, ZC + .3), (-.55, .25, .29, ZC + .335), (.05, .24, .33, ZC + .35)):
        pts = [(x * 1.02, y, zz) for x, zz in E(w, h, z, 6)][2:]
        fr.tube(pts + [(-x, yy, zz) for x, yy, zz in reversed(pts[:-1])], .014, seg=4)
    crew = a.part('Crew', 'Suit')
    for y, z in ((-.7, ZC + .4), (-.05, ZC + .46)):
        crew.sphere(.09, loc=(0, y, z), seg=8, rings=5)
    for s in (-1, 1):
        K.grille(a, (s * .27, -1.65, ZC + .05), .3, .14, facing=(s, 0, .25), slats=4, frame_mat='Team')
        rv = a.part('Kit_rivets', 'Steel')
        K.rivet_line(rv, (s * .3, -1.4, ZC - .1), (s * .27, .9, ZC - .08), (s, 0, 0), pitch=.16, r=.01, h=.008, seg=4)
        K.rivet_line(rv, (s * .26, -2.3, ZC + .12), (s * .29, -1.4, ZC + .14), (s, 0, .3), pitch=.15, r=.01, h=.008,
                     seg=4)
    seats = a.part('Seats', 'Undercarriage')
    for y, z in ((-.62, ZC + .28), (.03, ZC + .34)):
        seats.box((.26, .1, .42), loc=(0, y + .14, z), bevel=0)
    a.part('Seats', 'Undercarriage').box((.12, .02, .1), loc=(0, -1.05, ZC + .42), rot=(.4, 0, 0), bevel=0)
    a.part('Antennas', 'Steel').tube([(.9, -1.0, .52), (.9, -1.25, .52)], .01, seg=4)
    K.blade_antenna(a.part('Antennas', 'Steel'), (0, 1.0, ZC + .35), h=.12, chord=.1)
    K.blade_antenna(a.part('Antennas', 'Steel'), (0, .2, ZC - .33), h=.08, chord=.08, normal=(0, 0, -1))


def _wings_tail(a):
    wing = a.part('Wings', 'Team')
    dih = math.radians(5)
    K.wing(wing, (-.95, 1.15), (-.6, .55), 2.75, x0=.27, z=.48, t=.13, dihedral=dih)
    sc = a.part('Wing_seams', 'Undercarriage')
    for s in (-1, 1):
        for x0, x1 in ((.6, 1.7), (1.8, 2.8)):
            z0 = .48 + math.tan(dih) * (x0 - .27) + .05
            z1 = .48 + math.tan(dih) * (x1 - .27) + .04
            y0 = -.95 + .35 * (x0 - .27) / 2.75 + 1.15 - .28 * (x0 - .27) / 2.75 - .22
            y1 = -.95 + .35 * (x1 - .27) / 2.75 + 1.15 - .28 * (x1 - .27) / 2.75 - .2
            sc.limb((s * x0, y0, z0), (s * x1, y1, z1), .015, .012, bevel=0)
        tip_z = .48 + math.tan(dih) * 2.75
        a.part('Wing_lights', 'Lamp' if s > 0 else 'LavaGlow').box((.04, .1, .04), loc=(s * 3.03, -.4, tip_z),
                                                                     bevel=0)
    # Fin with dorsal fillet and rudder line, tailplanes, ventral strake.
    fin = a.part('Tail', 'Team')
    K.fin(fin, (2.25, .78), (2.72, .42), .82, x=0, z0=ZC + .2, t=.1)
    k.extrude(fin, [(1.3, ZC + .26), (2.35, ZC + .26), (2.35, ZC + .5)], .05, axis='X', chamfer=0)
    a.part('Wing_seams', 'Undercarriage').limb((0, 2.85, ZC + .25), (0, 3.02, ZC + 1.0), .108, .012, bevel=0)
    tp = a.part('Tailplanes', 'Team')
    K.wing(tp, (2.45, .5), (2.68, .28), 1.0, x0=.08, z=ZC + .12, t=.1, dihedral=math.radians(3))
    a.part('Tail', 'Team').box((.03, .5, .12), loc=(0, 2.6, ZC - .1), rot=(.2, 0, 0), bevel=0)
    # Gear doors, closed.
    gd = a.part('Gear_doors', 'Undercarriage')
    for s in (-1, 1):
        gd.box((.32, .55, .012), loc=(s * .85, -.55, .42), rot=(0, s * dih, 0), bevel=0)
    gd.box((.12, .4, .012), loc=(0, -2.0, ZC - .26), bevel=0)
    # Flap-track fairings and wingtip fairings.
    ft = a.part('Flap_fairings', 'Team')
    for s in (-1, 1):
        for x in (.8, 1.6, 2.3):
            z = .48 + math.tan(dih) * (x - .27) - .04
            k.lathe(ft, [(0, 0), (.035, .06), (.035, .3), (0, .38)], loc=(s * x, .05, z), rot=K.BACKWARD, seg=6)
        z = .48 + math.tan(dih) * 2.75
        k.lathe(ft, [(0, 0), (.04, .1), (.04, .45), (0, .55)], loc=(s * 3.02, -.65, z), rot=K.BACKWARD, seg=6)
    # Centreline pylon and drop tank.
    K.pylon(a.part('Pylons', 'Armor'), 0, -.7, -.1, ZC - .32, ZC - .42, w=.06)
    k.lathe(a.part('Drop_tanks', 'Plaster'), [(0, 0), (.07, .12), (.11, .35), (.11, .85), (.07, 1.1), (0, 1.2)],
            loc=(0, -1.0, ZC - .55), rot=K.BACKWARD, seg=10, worn=(2, 3))
    K.flare_dispenser(a, (.12, 1.5, ZC - .2), normal=(.3, 0, -1), cols=3, rows=2, cell=.05)
    K.flare_dispenser(a, (-.12, 1.5, ZC - .2), normal=(-.3, 0, -1), cols=3, rows=2, cell=.05)


def _weapons(a):
    """Two pylons with Hydra pods, the 12.7 mm gun fairing on the left wing."""
    py = a.part('Pylons', 'Armor')
    for s, idx in ((-1, ''), (1, '__001')):
        x = s * 1.5
        zw = .48 + math.tan(math.radians(5)) * (1.5 - .27)
        K.pylon(py, x, -.65, -.05, zw - .02, .34, w=.06)
        p27.rocket_pod(a, x, -.73, .22, .1, .85, s, seg=10)
        a.pivot('Muzzle_rocket' + idx, (x, -.75, .22))
    # The gun fairing on the left wing's leading edge, its barrel and the muzzle.
    x = -2.3
    zg = .62
    k.lathe(a.part('Gun_fairing', 'Armor'), [(0, -.05), (.06, .0), (.075, .15), (.07, .6), (0, .7)],
            loc=(x, -.82, zg), rot=K.BACKWARD, seg=8, worn=(2,))
    gun = a.part('Guns', 'Steel')
    k.lathe(gun, [(.022, 0), (.022, .28), (.03, .29), (.03, .34), (0, .34)], loc=(x, -.78, zg), rot=K.FORWARD, seg=6)
    a.pivot('Muzzle_gun', (x, -1.1, zg))
    a.pivot('Muzzle_main', (x, -1.1, zg))
    K.soot(a, (x, -1.1, zg), radius=.2, k=.3)


def _propeller(a):
    p = a.pivot('Propeller', (0, -2.66, .82))
    sp = a.part('Spinner', 'Team', p)
    k.lathe(sp, [(.0, -.3), (.07, -.25), (.12, -.13), (.14, .0), (.14, .08)], rot=K.BACKWARD, seg=12, worn=(3,))
    bl = a.part('Propeller_blades', 'Undercarriage', p)
    tips = a.part('Propeller_tips', 'Hazard', p)
    R = .64
    for j in range(5):
        u = j * TAU / 5 + .3
        d = (math.cos(u), 0, math.sin(u))
        e = (-math.sin(u), 0, math.cos(u))
        _blade(bl, tips, d, e, (0, -1, 0), .1, R, .1, .05, pitch=.55, stripe=.05, tip=.03, droop=0)


def prop_attack_plane(a, detail=False):
    """The turboprop light attack aircraft: see the module docstring."""
    K.suffixed(a)
    _fuselage(a)
    _wings_tail(a)
    _weapons(a)
    _propeller(a)
    k.clean(a)


BUILDERS = {
    'prop_attack_plane': (prop_attack_plane, dict(ao_distance=.25, grime_height=.0)),
}
