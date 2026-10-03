"""Prompt 35 wave 9 (lane C): the Shahed launch truck rebuilt from scratch (spec: Tools/blender/specs/shahed_truck.json).

A 6x6 military truck carrying the five-rail launch box for Shahed-136 (Geran-2) delta drones (unit_refs: Shahed-136;
the sheet: a truck launching delta-wing Shahed drones from a five-rail rack; the def's modelSize 6.65 x 2.3 x
2.87 m): the bonneted cab (the bonnet with its grille and lamps, the flat windscreen, doors, the canvas-backed
rear window, mirrors), the ladder frame on three axles with lugged tyres and wings; on the bed the turntable
(`Turret`) with the launch box: its frame of five rails stacked one above the other, raised at the front, with
a drone on each (the delta wing, the fuselage with its nose, the wingtip fins, the pusher propeller and the
booster under the tail), the box's side bracing and the stencilled team band; the self-defence 12.7 mm standing
on its post on the cab roof ring (`Mount_mg`, the def's free hmg_selfdef_15), jerrycans, the spare wheel, a tarp.

Runtime nodes kept: `Turret`, `Muzzle_main` (the top drone's nose), `Mount_mg`, `Muzzle_mg`, `Point_exhaust`,
`Point_fire`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WR = .48
AXLES = (-2.05, 1.05, 2.25)
TX = .82
FZ = .95
NOSE, TAIL = -3.3, 3.3


def _cab(a):
    bon = a.part('Body', 'Team')
    C.section_loft(bon, [
        (NOSE + .02, [(0, FZ), (.62, FZ), (.64, 1.5), (.55, 1.6), (0, 1.62)]),
        (NOSE + .1, [(0, FZ - .05), (.66, FZ - .05), (.68, 1.55), (.58, 1.68), (0, 1.7)]),
        (NOSE + 1.2, [(0, FZ - .05), (.68, FZ - .05), (.7, 1.6), (.62, 1.74), (0, 1.76)]),
    ])
    for s in (-1, 1):
        fw = a.part('Fenders', 'Team')
        k.extrude(fw, [(-.55, 0), (.5, 0), (.4, .25), (-.45, .22)], .32, loc=(s * .95, NOSE + .75, WR * 2 - .1),
                  axis='X', chamfer=.02)
        K.lamp(a, (s * .9, NOSE + .3, 1.2), (0, -1, 0), r=.08, guard=True)
    K.grille(a, (0, NOSE + .03, 1.25), .9, .45, facing=(0, -1, 0), slats=7, frame_mat='Steel')
    cab = a.part('Cab', 'Team')
    C.section_loft(cab, [
        (NOSE + 1.15, [(0, FZ - .05), (1.08, FZ - .05), (1.1, 1.6), (1.02, 1.7), (0, 1.72)]),
        (NOSE + 1.6, [(0, FZ - .05), (1.1, FZ - .05), (1.12, 1.62), (.98, 2.38), (0, 2.4)]),
        (NOSE + 2.6, [(0, FZ - .05), (1.1, FZ - .05), (1.12, 1.62), (1.0, 2.4), (0, 2.42)]),
    ])
    K.windscreen(a, [(-.92, NOSE + 1.2, 1.78), (.92, NOSE + 1.2, 1.78), (.85, NOSE + 1.55, 2.3),
                     (-.85, NOSE + 1.55, 2.3)], frame_mat='Team', wipers=2)
    for s in (-1, 1):
        a.part('Glass', 'Glass').box((.01, .55, .34), loc=(s * 1.07, NOSE + 2.05, 2.03), rot=(0, s * .14, 0), bevel=0)
        dr = a.part('Doors', 'Team')
        dr.box((.012, .02, .8), loc=(s * 1.115, NOSE + 2.45, 1.4), bevel=0)
        dr.box((.012, .02, .8), loc=(s * 1.115, NOSE + 1.65, 1.4), bevel=0)
        K.handle(a.part('Kit_steel', 'Steel'), (s * 1.12, NOSE + 2.2, 1.6), (s * 1.12, NOSE + 2.3, 1.6), (s, 0, 0),
                 h=.025, r=.01)
        K.mirror(a.part('Kit_steel', 'Steel'), (s * 1.05, NOSE + 1.3, 2.0), s, arm=.08, size=(.05, .02, .16))
        a.part('Steps', 'Steel').box((.1, .4, .03), loc=(s * 1.05, NOSE + 2.05, .65), bevel=0)
    bp = a.part('Bumper', 'Steel')
    K.chamfer_box(bp, (2.1, .12, .2), loc=(0, NOSE, FZ - .2), c=.03)
    for s in (-1, 1):
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .45, NOSE - .06, FZ - .25), facing=(0, -1, 0), size=.07)
    # The roof ring and the self-defence 12.7 mm on its post.
    k.ring(a.part('MG_ring', 'Armor'), [(.3, 0), (.36, 0), (.36, .08), (.3, .08)], loc=(.4, NOSE + 2.15, 2.41),
           seg=10)
    K.pintle_mg(a, None, (.4, NOSE + 2.15, 2.48), post=.12, length=1.0, scale=.85)


def _chassis(a):
    fr = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        fr.box((.14, 6.4, .24), loc=(s * .42, 0, FZ - .12), bevel=0)
    ax = a.part('Axles', 'Undercarriage')
    for y in AXLES:
        K.axle(ax, y, WR, TX - .1, r=.06)
        for s in (-1, 1):
            K.tread_wheel(a, (s * TX, y, WR), WR, .36, s, seg=12)
    for s in (-1, 1):
        K.leaf_spring(a.part('Leaf_springs', 'Undercarriage'), s * .42, 1.65, WR + .18, 1.5, leaves=3)
        a.part('Mud_wings', 'Team').box((.42, 2.3, .04), loc=(s * (TX + .02), 1.65, WR * 2 + .1), bevel=0)
        a.part('Tail_lamps', 'Lamp').box((.1, .02, .07), loc=(s * .9, TAIL - .02, FZ + .05), bevel=0)
    K.exhaust(a, (.85, NOSE + 2.75, 1.4), r=.05, length=1.2, direction=(0, 0, 1))
    a.pivot('Point_exhaust', (.85, NOSE + 2.75, 2.65))
    a.pivot('Point_fire', (0, 1.0, 1.6))
    C.jerry_rack(a, (-1.0, -.55, FZ - .45), count=2, axis='Y')
    K.tread_wheel(a, (.98, -.45, FZ - .12), .4, .26, 1, seg=10, tyre='Spare_wheel', rim='Spare_wheel_rim')


def _bed(a):
    bed = a.part('Bed', 'Team')
    k.extrude(bed, [(-1.1, -.6), (1.1, -.6), (1.1, TAIL), (-1.1, TAIL)], .08, loc=(0, 0, FZ + .04), axis='Z',
              chamfer=.01, corner=.02, caps=(False, True))
    for s in (-1, 1):
        K.plate(bed, (.04, 3.9, .3), loc=(s * 1.1, 1.35, FZ + .23), chamfer=.006)
    K.net_roll(a.part('Tarp', 'Canvas'), a.part('Kit_straps', 'Steel'), (0, -.45, FZ + .2), length=1.9, r=.12)


def _drone(a, t, tail, pitch, i):
    """One Shahed-136 on its rail: delta wing, fuselage, nose, wingtip fins, pusher, booster."""
    rot = (R90 - pitch, 0, 0)
    d = (0, -math.cos(pitch), math.sin(pitch))
    up = (0, math.sin(pitch), math.cos(pitch))

    def at(f, u=0.0, x=0.0):
        return (x, tail[1] + d[1] * f + up[1] * u, tail[2] + d[2] * f + up[2] * u)
    L = 3.1
    k.lathe(a.part('Drones', 'Plaster', t), [(.0, 0), (.09, .05), (.13, .3), (.13, L * .8), (.1, L * .93),
                                            (0, L)], loc=at(0), rot=rot, seg=8, worn=(3,))
    # The delta wing: a thin slab from the tail's span to the apex behind the nose.
    span = 1.0
    wing = a.part('Drone_wings', 'Plaster', t)
    pts = [(-span, 0), (span, 0), (.12, L * .78), (-.12, L * .78)]
    verts = []
    for th in (-.025, .025):
        for px, py in pts:
            p = at(py, th, px)
            verts.append(p)
    wing.mesh(verts, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)])
    fins = a.part('Drone_fins', 'Plaster', t)
    for s in (-1, 1):
        base = at(.12, .02, s * (span - .05))
        fins.box((.02, .35, .3), loc=(base[0], base[1], base[2] + .15), rot=(-pitch, 0, 0), bevel=0)
    a.part('Drone_props', 'Undercarriage', t).box((.5, .03, .06), loc=at(-.05), rot=(-pitch, 0, .6 * i), bevel=0)
    a.part('Drone_boosters', 'Steel', t).cyl(.06, .5, loc=at(.3, -.17), rot=rot, seg=6, bevel=0)
    a.part('Drone_noses', 'Undercarriage', t).cyl(.05, .1, loc=at(L - .05), rot=rot, seg=6, bevel=0)
    return at(L + .02)


def _launcher(a):
    """The turntable and the five-rail launch box (`Turret`) with a drone on each rail."""
    t = a.pivot('Turret', (0, 1.4, FZ + .12))
    k.lathe(a.part('Turntable', 'Steel', t), [(.6, 0), (.6, .06), (.5, .12), (0, .13)], seg=12, worn=(1,))
    pitch = math.radians(8)
    d = (0, -math.cos(pitch), math.sin(pitch))
    fr = a.part('Launcher_frame', 'Team', t)
    rails = a.part('Rails', 'Steel', t)
    y_tail = 1.5
    tip = None
    for i in range(5):
        tail = (0, y_tail, .24 + i * .24)
        tip = _drone(a, t, tail, pitch, i)
        rails.box((.1, 3.0, .05), loc=(0, tail[1] + d[1] * 1.5, tail[2] - .17 + d[2] * 1.5), rot=(-pitch, 0, 0),
                  bevel=0)
    # The box's corner posts and side bracing (it frames the stack), the team band.
    for s in (-1, 1):
        for f in (0, 2.9):
            y = y_tail + d[1] * f
            z0 = .15 + d[2] * f
            fr.box((.08, .08, 1.2), loc=(s * 1.08, y, z0 + .6), rot=(-pitch, 0, 0), bevel=0)
        fr.tube([(s * 1.08, y_tail, .2), (s * 1.08, y_tail + d[1] * 2.9, 1.3 + d[2] * 2.9)], .03, seg=4)
        fr.box((.06, 3.0, .08), loc=(s * 1.08, y_tail + d[1] * 1.45, 1.33 + d[2] * 1.45), rot=(-pitch, 0, 0), bevel=0)
        fr.box((.06, 3.0, .08), loc=(s * 1.08, y_tail + d[1] * 1.45, .12 + d[2] * 1.45), rot=(-pitch, 0, 0), bevel=0)
    a.part('Team_band', 'Team', t).box((.02, 1.2, .2), loc=(1.11, y_tail + d[1] * 1.5, .5 + d[2] * 1.5),
                                       rot=(-pitch, 0, 0), bevel=0)
    a.part('Launcher_rams', 'Steel', t).limb((0, .4, .05), (0, -.6, .3), .06, .07, bevel=0)
    a.pivot('Muzzle_main', tip, t)


def shahed_truck(a, detail=False):
    """The Shahed launch truck: see the module docstring."""
    _cab(a)
    _chassis(a)
    _bed(a)
    _launcher(a)
    K.dust(a, (0, 0, .3), radius=3.2, k=.14)
    k.clean(a)


BUILDERS = {
    'shahed_truck': (shahed_truck, dict(ao_distance=.4, grime_height=.45)),
}
