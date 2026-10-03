"""Prompt 35 wave 9 (lane C): the Earth Borer boss rebuilt from scratch (spec: Tools/blender/specs/earth_borer.json).

'Earth Worm', an armoured three-segment boring machine (unit_refs: the Soviet "Battle Mole", a tunnel boring
machine, 2A70 100 mm; the old file's 23.5 x 5.8 x 6.9 m kept): the drill segment at the front with the cutter
ring and its disc cutters, the conical drill head with its spiral flights and teeth turning on `Propeller`
(`Part_drill`, the breakable drill that stops the burrowing; `Muzzle_main` at its tip, the def's main
borer_drill); the round armoured middle segment with riveted ring bands, the team band, vision blocks, hatches and
the two 100 mm turrets on its back (`Part_gun` / `Part_gun.001`, each with `Mount_gun` / `Muzzle_gun`: the def's two
borer_cannon); the rear segment with the engine house (`Part_engine`: grilles, exhaust stacks, the radiator
fans), the spoil conveyor and pipes out of the tail; the armoured bellows joints between the segments; three
track units a side under the segments with their skirts; ladders, railings, lamps, beacons.

Runtime nodes kept: `Propeller`, `Part_drill`, `Part_gun`, `Part_gun.001`, `Mount_gun`, `Mount_gun.001`, `Muzzle_gun`,
`Muzzle_gun.001`, `Part_engine` (at the old positions); `Muzzle_main` added (the drill's tip: the def's three
weapons need three muzzles). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TAU = math.tau
ZC = 3.3             # the hull's axis height
R = 2.35             # the hull's radius
SEGS = ((-6.6, -2.3), (-1.7, 4.0), (4.6, 11.3))


def _tracks(a):
    import mb_vehicles as mv
    for y0, y1 in ((-6.4, -2.6), (-1.4, 3.7), (4.9, 10.9)):
        L = y1 - y0
        pts = []
        for cy, cz, r in ((y0 + .7, .7, .7), (y1 - .7, .7, .7)):
            for i in range(14):
                u = i * TAU / 14
                pts.append((cy + r * math.cos(u), cz + r * math.sin(u)))
        outline = mv._hull2d(pts)
        for s in (-1, 1):
            x = s * 2.15
            k.extrude(a.part('Tracks', 'Undercarriage'), outline, 1.25, loc=(x, 0, 0), axis='X', chamfer=0)
            links = a.part('Track_links', 'Undercarriage')
            for (py, pz), (ty, tz) in mv._perimeter(outline, .5, 0.0):
                links.box((1.32, .18, .09), loc=(x, py + tz * .03, pz - ty * .03), rot=(math.atan2(tz, ty), 0, 0),
                          bevel=0)
            for yy in [y0 + .7 + i * (L - 1.4) / 3 for i in range(4)]:
                k.lathe(a.part('Wheels', 'Steel'), [(.55, -.15), (.55, .15)], loc=(x + s * .55, yy, .7), rot=(0, R90, 0),
                        seg=10)
            sk = a.part('Skirts', 'Armor')
            sk.box((.08, L + .2, .7), loc=(s * 2.86, (y0 + y1) / 2, 1.35), bevel=0)
            a.part('Hazard_marks', 'Hazard').box((.02, L * .5, .15), loc=(s * 2.91, (y0 + y1) / 2, 1.55), bevel=0)


def _segments(a):
    hull = a.part('Hull', 'Team')
    for i, (y0, y1) in enumerate(SEGS):
        r0 = R + (.15 if i == 0 else 0)
        k.lathe(hull, [(r0 - .3, 0), (r0, .3), (r0, y1 - y0 - .3), (r0 - .3, y1 - y0)], loc=(0, y0, ZC),
                rot=K.BACKWARD, seg=16, caps=(i == 2, i == 2), worn=(1, 2))
        bands = a.part('Bands', 'Armor')
        for f in (.08, .92):
            bands.cyl(r0 + .06, .25, loc=(0, y0 + (y1 - y0) * f, ZC), rot=K.FORWARD, seg=16, bevel=0)
        rv = a.part('Kit_rivets', 'Steel')
        for j in range(12):
            u = j * TAU / 12
            for f in (.08, .92):
                rv.cyl(.05, .06, loc=(math.cos(u) * (r0 + .1), y0 + (y1 - y0) * f, ZC + math.sin(u) * (r0 + .1)),
                       rot=(0, R90, u), seg=5, bevel=0)
        # The flat armoured deck on top of each segment (the turrets and the engine house stand on it).
        k.block(a.part('Deck', 'Armor'), (2.8, y1 - y0 - .8, .2), loc=(0, (y0 + y1) / 2, ZC + R - .25), chamfer=.04)
    for yj in (-2.0, 4.3):           # the bellows joints
        jn = a.part('Joints', 'Rubber')
        for j in range(3):
            jn.cyl(R - .25 + (j % 2) * .12, .15, loc=(0, yj - .2 + j * .2, ZC), rot=K.FORWARD, seg=14, bevel=0)
        a.part('Joint_links', 'Steel').limb((0, yj - .5, ZC + R - .3), (0, yj + .5, ZC + R - .3), .12, .12, bevel=0)
    for s in (-1, 1):
        a.part('Team_band', 'Team').box((.04, 4.6, .4), loc=(s * (R + .02), 1.15, ZC + .3), bevel=0)
        for y in (-.5, 1.5):
            a.part('Visors', 'Glass').box((.04, .35, .12), loc=(s * (R - .05), y, ZC + 1.3), rot=(0, s * .55, 0),
                                          bevel=0)
        K.ladder(a.part('Ladders', 'Steel'), (s * (R + .1), 2.8, 1.5), (s * (R - .3), 2.8, ZC + R - .2), width=.5,
                 step=.35)
    for y in (-5.0, 1.2, 9.4):
        C.hatch(a, (0, y, ZC + R - .15), r=.4)
    rl = a.part('Railings', 'Steel')
    for s in (-1, 1):
        rl.tube([(s * 1.35, -1.4, ZC + R + .5), (s * 1.35, 3.6, ZC + R + .5)], .035, seg=4)
        for yy in (-1.4, 1.1, 3.6):
            rl.limb((s * 1.35, yy, ZC + R - .15), (s * 1.35, yy, ZC + R + .5), .03, .03, bevel=0)
    for s in (-1, 1):
        K.lamp(a, (s * 1.6, -6.0, ZC + 1.6), (0, -1, 0), r=.15, guard=True)
    K.beacon(a, (.0, 10.4, ZC + R - .15), r=.15)


def _drill(a):
    """The cutter ring and the drill head turning on `Propeller` (boss part drill)."""
    pd = a.pivot('Part_drill', (0, -6.8, 3.3))
    ring = a.part('Drill_ring', 'Steel', pd)
    k.lathe(ring, [(R - .2, .2), (R + .35, .1), (R + .35, -.3), (R - .4, -.45)], rot=K.FORWARD, seg=18, worn=(1, 2))
    cut = a.part('Drill_cutters', 'Undercarriage', pd)
    for j in range(12):
        u = j * TAU / 12
        cut.cyl(.22, .14, loc=(math.cos(u) * (R + .1), -.4, math.sin(u) * (R + .1)), rot=(0, R90, u), seg=8, bevel=0)
    p = a.pivot('Propeller', (0, 0, 0), pd)
    k.lathe(a.part('Drill_cone', 'Steel', p), [(1.95, 0), (1.8, .6), (1.2, 2.3), (.55, 3.8), (.15, 4.75), (0, 4.8)],
            rot=K.FORWARD, seg=16, worn=(2, 4))
    fl = a.part('Drill_flights', 'Armor', p)
    for start in (0, math.pi):
        pts = []
        for i in range(17):
            f = i / 16
            rr = 1.95 - 1.7 * f + .22
            u = start + f * TAU * 1.6
            pts.append((math.cos(u) * rr, -.2 - f * 4.3, math.sin(u) * rr))
        fl.tube(pts, .09, seg=4)
    th = a.part('Drill_teeth', 'Undercarriage', p)
    for i in range(18):
        f = (i + .5) / 18
        u = f * TAU * 1.6 + (i % 2) * math.pi
        rr = 1.95 - 1.7 * f + .3
        th.box((.18, .18, .3), loc=(math.cos(u) * rr, -.2 - f * 4.3, math.sin(u) * rr), rot=(0, 0, u), bevel=0)
    k.lathe(a.part('Drill_tip', 'Undercarriage', p), [(.2, 0), (.12, .2), (0, .35)], loc=(0, -4.7, 0),
            rot=K.FORWARD, seg=8)
    a.pivot('Muzzle_main', (0, -5.06, 0), pd)


def _guns(a):
    """The two 100 mm turrets on the middle segment (boss parts gun_l / gun_r)."""
    for i, (x, y) in enumerate(((1.3, -.2), (-1.3, 3.2))):
        tag = '' if i == 0 else '_r'
        p = a.pivot(K.name('Part_gun', i), (x, y, 5.63))
        m = a.pivot(K.name('Mount_gun', i), (0, 0, 0), p)
        g = a.part(f'Gun_house{tag}', 'Team', m)
        C.slab_loft(g, C.octagon(1.7, 2.1, .45, y0=.2), C.octagon(1.2, 1.4, .3, y0=.3), 0, .62)
        a.part(f'Gun_ring{tag}', 'Steel', m).cyl(.95, .1, loc=(0, 0, .02), seg=12, bevel=0)
        k.block(a.part(f'Gun_bustle{tag}', 'Armor', m), (1.1, .6, .4), loc=(0, 1.3, .32), chamfer=.04)
        K.whip_antenna(a.part('Antennas', 'Steel', m), (-.55, 1.2, .62), h=1.0, r=.02)
        k.extrude(a.part(f'Gun_mantlet{tag}', 'Armor', m), [(-.12, -.15), (.1, -.17), (.14, .15), (-.1, .17)], .4,
                  loc=(0, -.68, .3), axis='X', chamfer=.02)
        k.lathe(a.part(f'Gun_barrel{tag}', 'Steel', m), [(.09, 0), (.09, .3), (.065, .38), (.06, 1.55), (0, 1.55)],
                loc=(0, -.75, .3), rot=K.FORWARD, seg=10, worn=(1,))
        k.lathe(a.part(f'Gun_brake{tag}', 'Undercarriage', m), [(.07, 0), (.1, .03), (.1, .2), (.07, .22), (0, .22)],
                loc=(0, -2.28, .3), rot=K.FORWARD, seg=10)
        K.periscope(a, (.3, -.2, .55), facing=(0, -1, 0), parent=m, size=(.14, .12, .1))
        a.pivot(K.name('Muzzle_gun', i), (0, -2.3, .3), m)


def _engine(a):
    """The engine house on the rear segment (boss part engine), stacks, fans; the spoil conveyor and pipes."""
    p = a.pivot('Part_engine', (0, 7.3, 4.9))
    eh = a.part('Engine_house', 'Armor', p)
    C.slab_loft(eh, C.octagon(2.6, 4.6, .3), C.octagon(2.1, 4.0, .3), .6, 1.7)
    K.grille(a, (0, 0, 1.71), 1.8, 3.2, facing=(0, 0, 1), slats=9, parent=p, frame_mat='Armor')
    for s in (-1, 1):
        K.exhaust(a, (s * .9, 1.8, 1.3), r=.14, length=.55, direction=(0, 0, 1), parent=p)
        k.ring(a.part('Fans', 'Steel', p), [(.35, 1.72), (.42, 1.72), (.42, 1.78), (.35, 1.78)], loc=(s * .55, -1.4, 0),
               seg=10)
        a.part('Fans', 'Undercarriage', p).cyl(.35, .02, loc=(s * .55, -1.4, 1.74), seg=10, bevel=0)
    cv = a.part('Conveyor', 'Steel')
    cv.box((1.0, 3.0, .25), loc=(1.3, 12.1, ZC + 1.1), rot=(-.35, 0, .25), bevel=0)
    a.part('Conveyor_belt', 'Undercarriage').box((.8, 3.0, .05), loc=(1.3, 12.1, ZC + 1.25), rot=(-.35, 0, .25), bevel=0)
    a.part('Spoil_pipes', 'Rust').limb((-1.2, 9.0, ZC - .9), (-1.6, 12.2, ZC - 1.3), .25, .25, bevel=0)
    for s in (-1, 1):
        a.part('Tail_lamps', 'Lamp').box((.2, .03, .12), loc=(s * 1.4, 11.32, ZC + .6), bevel=0)


def _kit(a):
    """One-sided fittings: the spoil chute and its boom on the left, side lockers, the sensor mast, jacks."""
    # The left side's spoil chute boom (raised) and the lockers on the right.
    a.part('Chute_boom', 'Rust').limb((R - .2, 5.6, ZC + 1.4), (1.7, 9.6, ZC + R + .9), .3, .25, bevel=0)
    k.block(a.part('Chute', 'Rust'), (.8, 1.2, .6), loc=(1.75, 9.9, ZC + R + .6), rot=(.5, 0, 0), chamfer=.04)
    a.part('Hazard_marks', 'Hazard').box((.05, 1.0, .25), loc=(2.15, 7.6, ZC + 2.2), rot=(.6, 0, 0), bevel=0)
    for y in (-5.6, -4.2, 5.4, 6.8, 8.2):
        C.stowage_box(a, (.45, 1.1, .7), (-(R + .15), y, ZC - .3), mat='Armor', latches=2)
    # The sensor mast on the drill segment with its radar head, the hydraulic jacks along the front.
    a.part('Masts', 'Steel').cyl(.1, 1.6, loc=(-.9, -4.4, ZC + R + .6), seg=8, bevel=0)
    k.block(a.part('Sensor', 'Armor'), (.7, .3, .4), loc=(-.9, -4.4, ZC + R + 1.5), chamfer=.03)
    a.part('Glass', 'Glass').box((.5, .02, .2), loc=(-.9, -4.56, ZC + R + 1.6), bevel=0)
    for u in (.6, 2.5, 3.8, 5.6):
        a.part('Jacks', 'Steel').limb((math.cos(u) * (R - .1), -6.2, ZC + math.sin(u) * (R - .1)),
                                      (math.cos(u) * (R - .1), -3.0, ZC + math.sin(u) * (R - .1)), .12, .14, bevel=0)
    C.cable_reel(a, (1.2, 9.0, ZC + R + .05), r=.45, w=.6, axis='X')
    # The pump unit hung on the right side in the gap between the track units.
    k.block(a.part('Pump_unit', 'Armor'), (.7, 1.0, 1.2), loc=(-2.55, 4.3, ZC - .3), chamfer=.05)
    K.grille(a, (-2.91, 4.3, ZC - .1), .8, .7, facing=(-1, 0, 0), slats=4, frame_mat='Armor')
    a.part('Kit_cables', 'Undercarriage').tube([(-2.6, 4.7, ZC + .3), (-2.2, 5.6, ZC + 1.4)], .05, seg=4)
    C.jerry_rack(a, (-1.0, 8.6, ZC + R - .15), count=3, axis='Y')


def earth_borer(a, detail=False):
    """The Earth Borer boss: see the module docstring."""
    K.suffixed(a)
    _tracks(a)
    _segments(a)
    _drill(a)
    _guns(a)
    _engine(a)
    _kit(a)
    K.dust(a, (0, 0, .4), radius=8.0, k=.16)
    k.clean(a)


BUILDERS = {
    'earth_borer': (earth_borer, dict(ao_distance=1.2, grime_height=1.6)),
}
