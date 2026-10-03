"""Prompt 35 wave 10 (lane B): the heavy bomber rebuilt from scratch (spec: Tools/blender/specs/heavy_bomber.json).

unit_refs B-52 Stratofortress (FAB-500, Kh-101); unit_sheet: an eight-engined bomber, the engines hung in four pairs
under a long swept wing, a long body and a tall fin, the biggest of the player's aircraft (the def's modelSize
19.8 x 22.62 x 5.7 m, 0.4 x a B-52). The long slab-sided fuselage with the stepped cockpit (windscreen panes,
eyebrow windows), the nose radome and the chin sensor turrets, the shoulder wing (35 degrees of sweep, anhedral,
the outrigger gear pods near the tips, flap and spoiler seams as paint), four twin-engine pods on their pylons
(intake lips, fan faces, nozzles), the tall fin with its rudder seam and the all-moving tailplane, the quad
12.7 mm tail turret (`Mount_gun`, the def's free tail guns), the cruise missiles on the inner-wing pylons
(`Muzzle_rocket` / `.001`), the bomb bay with its two doors on hinge pivots (`Part_bay_door_L` / `_R`: a later
bomb-run pass opens them) over the racked FAB-500 load (`Muzzle_missile`, the drop point), the flare dispensers,
the refuelling receptacle, antennas, beacons, the Team stripes on the spine and the flanks. Jet rule: no insets or
greebles on the skin; panel lines are paint.

Runtime nodes kept at their old places: `Muzzle_gun` (0, 10.15, 0.42), `Muzzle_missile` (0, 0.25, -0.9),
`Muzzle_rocket` / `.001` (-/+2.0, -1.32, -0.02), `Point_fire`, `Point_exhaust` (Part_wing and the Mount_Flare points
come from the wrappers); new: `Mount_gun` (the free tail guns), `Part_bay_door_L` / `_R`. Built only from
frontier_kit / mb_kit27 primitives, mb_kit35 and lane B's helpers; no other model's builder. Metres, +Z up, -Y
front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
WZ = .55                 # wing root height
LE0, C0 = -2.3, 5.4      # wing root leading edge, chord
LE1, C1 = 5.6, 1.6       # wing tip
SPAN = 11.3
ANH = -.05


def wing_at(x):
    """(leading edge y, chord, z) of the wing at span |x|."""
    f = min(1.0, max(0.0, (abs(x) - .6) / (SPAN - .6)))
    return LE0 + (LE1 - LE0) * f, C0 + (C1 - C0) * f, WZ + math.tan(ANH) * (abs(x) - .6)


def _fuselage(a):
    body = a.part('Fuselage', 'Team')
    E = K.ellipse_half
    st = [(-9.9, E(.08, .08, -.05, n=6)), (-9.6, E(.45, .42, -.02, n=6)), (-8.9, E(.68, .7, .05, n=6)),
          (-7.9, E(.72, .82, .1, n=6, flat=.15)), (-6.0, E(.72, .82, .05, n=6, flat=.25)),
          (5.5, E(.7, .8, .05, n=6, flat=.25)), (8.2, E(.48, .55, .2, n=6, flat=.1)), (9.6, E(.22, .25, .38, n=6))]
    K.section_loft(body, st)
    # The stepped cockpit: windscreen panes, eyebrow windows, frames.
    g = a.part('Cockpit_glass', 'Glass')
    for i, x in enumerate((-.42, -.14, .14, .42)):
        g.mesh([(x - .13, -8.95, .62), (x + .13, -8.95, .62), (x + .11, -8.62, .84), (x - .11, -8.62, .84)],
               [(0, 1, 2, 3)])
    for s in (-1, 1):
        g.mesh([(s * .64, -8.75, .55), (s * .68, -8.2, .62), (s * .62, -8.2, .82), (s * .56, -8.6, .8)],
               [(0, 1, 2, 3) if s > 0 else (3, 2, 1, 0)])
    a.part('Canopy_frames', 'Armor').box((1.0, .04, .04), loc=(0, -8.62, .85), bevel=0)
    k.lathe(a.part('Radome', 'Charred'), [(0, 0), (.3, .12), (.42, .32), (.44, .4)], loc=(0, -9.92, -.05),
            rot=K.BACKWARD, seg=10)
    for s in (-1, 1):
        a.part('Sensor_turrets', 'Glass').sphere(.16, loc=(s * .3, -8.9, -.62), seg=8, rings=5)
    # Team stripes on the spine and flanks, panel lines (paint).
    tb = a.part('Team_band', 'Team')
    tb.box((.3, 13.0, .02), loc=(0, -1.0, .9), bevel=0)
    for s in (-1, 1):
        tb.box((.02, 9.0, .18), loc=(s * .725, -2.0, .1), bevel=0)
    lines = a.part('Panel_lines', 'Undercarriage')
    for y in (-7.0, -5.0, -3.0, 3.5, 5.5, 7.4):
        for s in (-1, 1):
            lines.box((.01, .02, 1.1), loc=(s * (.72 if y < 6 else .62), y, .05), bevel=0)
    a.part('Refuel_receptacle', 'Hazard').box((.3, .6, .02), loc=(0, -6.4, .93), bevel=0)
    a.pivot('Point_fire', (0, 0, 1.0))


def _wing(a):
    w = a.part('Wing', 'Team')
    K.wing(w, (LE0, C0), (LE1, C1), SPAN - .6, x0=.6, z=WZ, t=.1, dihedral=ANH)
    # Flap / spoiler seams and the leading-edge line as paint, the outrigger gear pods, tip lights, tanks.
    seams = a.part('Wing_seams', 'Undercarriage')
    for s in (-1, 1):
        for x0, x1 in ((1.2, 4.6), (4.8, 8.0)):
            le0, c0, z0 = wing_at(x0)
            le1, c1, z1 = wing_at(x1)
            ya, yb = le0 + c0 * .78, le1 + c1 * .78
            ang = math.atan2(yb - ya, x1 - x0)
            seams.box((math.hypot(x1 - x0, yb - ya), .05, .02),
                      loc=(s * (x0 + x1) / 2, (ya + yb) / 2, (z0 + z1) / 2 + .06), rot=(0, 0, s * ang), bevel=0)
        le, c, z = wing_at(9.4)
        k.lathe(a.part('Gear_pods', 'Armor'), [(0, 0), (.12, .2), (.14, .6), (.1, 1.0), (0, 1.1)],
                loc=(s * 9.4, le - .2, z - .25), rot=K.BACKWARD, seg=8)
        le, c, z = wing_at(10.6)
        k.lathe(a.part('Drop_tanks', 'Armor'), [(0, 0), (.16, .4), (.18, 1.2), (.1, 2.0), (0, 2.1)],
                loc=(s * 10.6, le - .5, z - .3), rot=K.BACKWARD, seg=8)
        le, c, z = wing_at(SPAN)
        a.part('Wing_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.1, .2, .06),
                                                                         loc=(s * (SPAN - .05), le + .3, z), bevel=0)


def _engines(a):
    """Four twin-engine pods on pylons under the wing."""
    for s in (-1, 1):
        for x in (3.3, 6.6):
            le, c, z = wing_at(x)
            px, py, pz = s * x, le - 1.3, z - .75
            K.pylon(a.part('Pylons', 'Armor'), px, le - .4, le + 1.2, z - .02, pz + .3, w=.12)
            for dx in (-.27, .27):
                ex = px + dx
                k.lathe(a.part('Engine_pods', 'Armor'), [(.22, 0), (.27, .12), (.28, .8), (.25, 1.6), (.18, 2.1)],
                        loc=(ex, py, pz), rot=K.BACKWARD, seg=10, worn=(1,))
                k.lathe(a.part('Intake_lips', 'Steel'), [(.18, -.02), (.24, -.04), (.27, .1), (.22, .1)],
                        loc=(ex, py, pz), rot=K.BACKWARD, seg=10, caps=(False, False))
                a.part('Intakes', 'Undercarriage').cyl(.2, .03, loc=(ex, py + .1, pz), rot=(R90, 0, 0), seg=10,
                                                       bevel=0)
                k.lathe(a.part('Nozzles', 'Charred'), [(.17, 0), (.14, .3), (.1, .3)], loc=(ex, py + 2.1, pz),
                        rot=K.BACKWARD, seg=10, caps=(False, True))
                K.soot(a, (ex, py + 2.4, pz), radius=.6, k=.35)
    a.pivot('Point_exhaust', (6.6, 1.88, -.01))


def _tail(a):
    fin = a.part('Tail_fin', 'Team')
    K.fin(fin, (5.8, 3.4), (8.6, 1.5), 3.75, x=0, z0=.75, t=.08)
    a.part('Rudder_seam', 'Undercarriage').box((.17, .04, 3.2), loc=(0, 8.6, 2.6), rot=(-.32, 0, 0), bevel=0)
    a.part('Team_band', 'Team').box((.18, 1.4, .2), loc=(0, 8.9, 4.1), rot=(-.35, 0, 0), bevel=0)
    tp = a.part('Tailplanes', 'Team')
    K.wing(tp, (7.2, 2.0), (8.9, .8), 4.0, x0=.3, z=.35, t=.08, dihedral=0)
    K.beacon(a, (0, 9.8, 4.48), r=.06)
    # The quad 12.7 mm tail turret (the def's free tail guns).
    m = a.pivot('Mount_gun', (0, 9.6, .4))
    k.lathe(a.part('Tail_turret', 'Armor', m), [(0, -.35), (.22, -.25), (.26, 0), (.2, .25), (0, .3)],
            rot=K.FORWARD, seg=10)
    for dx in (-.08, .08):
        for dz in (-.06, .06):
            a.part('Guns', 'Steel', m).cyl(.022, .5, loc=(dx, .45, .02 + dz), rot=(R90, 0, 0), seg=6, bevel=0)
    a.part('Glass', 'Glass', m).box((.2, .02, .12), loc=(0, .18, .2), rot=(.6, 0, 0), bevel=0)
    a.pivot('Muzzle_gun', (0, .55, .02), m)
    for s in (-1, 1):
        K.flare_dispenser(a, (s * .3, 8.2, -.35), normal=(s * .5, 0, -1), cols=3, rows=2)


def _bay_and_stores(a):
    """The bomb bay: two doors on hinge pivots over the racked FAB-500 load; the cruise missiles on pylons."""
    for side, s in (('L', 1), ('R', -1)):
        p = a.pivot(f'Part_bay_door_{side}', (s * .55, .25, -.72))
        k.block(a.part(f'Bay_door_{side.lower()}', 'Armor', p), (.55, 4.4, .05), loc=(-s * .27, 0, -.02),
                chamfer=.01)
        a.part('Bay_bands', 'Hazard', p).box((.5, .08, .015), loc=(-s * .27, -2.15, -.05), bevel=0)
        a.part('Kit_hinges', 'Steel', p).box((.04, 4.2, .04), loc=(0, 0, 0), bevel=0)
    racks = a.part('Bomb_racks', 'Steel')
    racks.box((.06, 4.2, .06), loc=(0, .25, -.45), bevel=0)
    for i in range(6):
        K.bomb(a, (0, -1.6 + i * .74, -.6), .14, .65)
    a.pivot('Muzzle_missile', (0, .25, -.9))
    for i, s in enumerate((-1, 1)):
        le, c, z = wing_at(2.0)
        K.pylon(a.part('Pylons', 'Armor'), s * 2.0, le, le + 1.4, z - .03, z - .4, w=.1)
        K.missile(a, (s * 2.0, 1.4, z - .58), .14, 2.6, direction=(0, -1, 0), fins=4, body='Missiles')
        a.pivot(K.name('Muzzle_rocket', i), (s * 2.0, -1.32, -.02))
    ant = a.part('Antennas', 'Steel')
    for y in (-4.0, 2.0):
        K.blade_antenna(ant, (0, y, .92), h=.25, chord=.18)
    K.blade_antenna(ant, (0, -3.0, -.78), h=.2, chord=.14, normal=(0, 0, -1))
    a.part('Beacons', 'BarrelRed').sphere(.06, loc=(0, 3.0, .93), seg=8, rings=4)
    a.part('Beacons', 'BarrelRed').sphere(.06, loc=(0, -2.6, -.8), seg=8, rings=4)


MERGE = {n: 'Intake_lips' for n in ('Bomb_racks', 'Bomb_fins')}
MERGE.update({n: 'Engine_pods' for n in ('Gear_pods', 'Drop_tanks', 'Canopy_frames', 'Bombs_body')})
MERGE.update({n: 'Panel_lines' for n in ('Wing_seams', 'Rudder_seam', 'Intakes')})
MERGE.update({n: 'Fuselage' for n in ('Tailplanes', 'Team_band')})
MERGE.update({'Bomb_bands': 'Refuel_receptacle', 'Sensor_turrets': 'Cockpit_glass', 'Radome': 'Nozzles'})


def heavy_bomber(a):
    K.suffixed(a)
    _fuselage(a)
    _wing(a)
    _engines(a)
    _tail(a)
    _bay_and_stores(a)
    P.merge_parts(a, MERGE)
    k.clean(a)


BUILDERS = {'heavy_bomber': (heavy_bomber, dict(ao_distance=.6, grime_height=.2, ground=False))}
