"""Prompt 35 wave 7 (lane C): the armoured car rebuilt from scratch (spec: Tools/blender/specs/armored_car.json).

A Steyr Pandur I 6x6 (unit_refs and the sheet: a six-wheeler with exposed wheels, a box hull sloped at the front and
a small turret in the middle with a long 25 mm gun; the def's modelSize 4.78 x 2.08 x 1.49 m, 0.8 x real): the
welded hull with its sharp V nose under the sloped glacis, the upper sides leaning in, the driver's hatch with its
vision blocks, the headlamps in their guards, three exposed axles on lugged tyres with hubs and suspension arms, the
rear door with its window and step, roof hatches; the one-man turret with the M242 25 mm on its mantlet, the
coaxial MG, the gunner's sight and the smoke dischargers; side bins, jerrycans, tow points and aerials.

Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Coax`, `Muzzle_coax`, `Hatches`,
`Point_exhaust`, `Point_fire` (the wrapper adds `Part_wheel` / `Part_wheelb`). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WR = .36
AX = (-1.25, -.05, 1.15)
TRACK = .82
TOP = 1.02
NOSE, TAIL = -2.05, 2.1
TUR = (0, -.15, TOP)


def _hull(a):
    hull = a.part('Hull', 'Team')
    # Sections: the sharp V nose, the glacis, the box with its upper sides leaning in, the rear plate.
    C.section_loft(hull, [
        (NOSE, [(0, .42), (.25, .45), (.42, .55), (.5, .62), (.46, .66), (0, .66)]),
        (NOSE + .5, [(0, .3), (.42, .3), (.72, .55), (.8, .72), (.68, .9), (0, .92)]),
        (-.9, [(0, .3), (.45, .3), (.75, .55), (.84, .72), (.7, TOP), (0, TOP)]),
        (TAIL, [(0, .32), (.45, .32), (.75, .55), (.84, .72), (.7, TOP - .02), (0, TOP - .02)]),
    ])
    a.part('Hull_lower', 'Armor').box((.9, 3.6, .14), loc=(0, .05, .3), bevel=0)
    for s in (-1, 1):
        a.part('Team_band', 'Team').box((.012, 2.6, .06), loc=(s * .815, .3, .75), rot=(0, 0, 0), bevel=0)
    # The glacis: the driver's hatch with three vision blocks, the headlamps in guards, tow hooks, the trim plate.
    C.hatch(a, (.35, -1.25, .93), r=.2)
    gl = a.part('Glass', 'Glass')
    for x in (.15, .35, .55):
        gl.box((.12, .02, .05), loc=(x, -1.47, .91), rot=(-.6, 0, 0), bevel=0)
    for s in (-1, 1):
        K.lamp(a, (s * .55, NOSE + .3, .64), (0, -1, .2), r=.055, guard=True)
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .3, NOSE + .05, .45), facing=(0, -1, -.3), size=.06)
        # Side vision blocks and the crew door outline on the upper sides.
        for y in (.3, 1.0):
            gl.box((.02, .14, .06), loc=(s * .78, y, .86), rot=(0, s * .5, 0), bevel=0)
        a.part('Tail_lamps', 'LavaGlow').box((.07, .02, .05), loc=(s * .62, TAIL + .01, .85), bevel=0)
    K.plate(a.part('Trim_plate', 'Armor'), (.9, .25, .03), loc=(0, NOSE + .2, .62), rot=(-.4, 0, 0))
    # The rear door with its window and step, the roof hatches, the exhaust louvre on the right side.
    dr = a.part('Doors', 'Armor')
    K.plate(dr, (.7, .04, .55), loc=(0, TAIL + .02, .68), chamfer=.01)
    gl.box((.2, .01, .1), loc=(0, TAIL + .045, .82), bevel=0)
    K.handle(a.part('Kit_steel', 'Steel'), (.25, TAIL + .05, .65), (.25, TAIL + .05, .78), (0, 1, 0), h=.03)
    for z in (.5, .85):
        K.hinge(a.part('Kit_steel', 'Steel'), (-.36, TAIL + .03, z - .06), (-.36, TAIL + .03, z + .06), r=.02,
                knuckles=2)
    k.block(a.part('Steps', 'Steel'), (.45, .16, .03), loc=(0, TAIL + .1, .32), chamfer=0)
    for x in (-.35, .35):
        K.plate(a.part('Hatches', 'Armor'), (.42, .5, .04), loc=(x, 1.35, TOP + .02), chamfer=.01)
        a.part('Kit_steel', 'Steel').box((.36, .04, .03), loc=(x, 1.62, TOP + .03), bevel=0)
        a.part('Kit_steel', 'Steel').box((.04, .2, .03), loc=(x, 1.2, TOP + .05), bevel=0)
    K.grille(a, (-.8, -.6, .8), .5, .2, facing=(-1, 0, .3), slats=4, frame_mat='Team')
    a.pivot('Point_exhaust', (-.85, -.6, .9))
    a.pivot('Point_fire', (0, .5, TOP + .2))
    # Stowage: side bins over the rear axle, a jerrycan pair on the rear corner, aerials.
    for s in (-1, 1):
        C.stowage_box(a, (.16, .6, .22), (s * .78, .55, .75), mat='Armor', latches=1)
    K.whip_antenna(a.part('Antennas', 'Steel'), (.6, 1.8, TOP - .01), h=.38, r=.02)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.6, 1.8, TOP - .01), h=.3, r=.02)


def _wheels(a):
    ax = a.part('Axles', 'Undercarriage')
    for y in AX:
        K.axle(ax, y, WR, TRACK - .14, r=.065)
        for s in (-1, 1):
            C.lugged_tyre(a, (s * TRACK, y, WR), WR, .3, s, lugs=8, seg=11, nuts=4)
            a.part('Suspension', 'Undercarriage').limb((s * .45, y + .3, .55), (s * .64, y, WR + .05), .04, .04,
                                                       bevel=0)
    fl = a.part('Fender_flares', 'Armor')
    for y in AX:
        for s in (-1, 1):
            fl.box((.3, .85, .03), loc=(s * .87, y, WR * 2 + .06), rot=(0, s * .25, 0), bevel=0)


def _turret(a):
    t = a.pivot('Turret', TUR)
    K.turret_ring(a.part('Turret_ring', 'Armor'), TUR, .6, h=.05)
    body = a.part('Turret_body', 'Team', t)
    bot = [(-.35, -.62), (.35, -.62), (.66, -.3), (.68, .45), (.5, .72), (-.5, .72), (-.68, .45), (-.66, -.3)]
    top = [(-.25, -.42), (.25, -.42), (.5, -.2), (.52, .38), (.38, .58), (-.38, .58), (-.52, .38), (-.5, -.2)]
    C.slab_loft(body, bot, top, 0, .34)
    K.plate(a.part('Turret_roof', 'Armor', t), (.7, .6, .025), loc=(0, .12, .35))
    # The mantlet and the long M242 with its muzzle brake, the coax.
    K.chamfer_box(a.part('Mantlet', 'Armor', t), (.34, .24, .22), loc=(0, -.66, .2), c=.03)
    end = C.gun_tube(a, 'Main_cannon', t, (0, -.76, .22), 1.55, .032, seg=8, sleeve=0, brake='pepper',
                     brake_name='Muzzle_brake', taper=1.0)
    a.pivot('Muzzle_main', (0, end[1] - .16, .22), t)
    a.part('Coax', 'Steel', t).cyl(.018, .4, loc=(.18, -.75, .15), rot=K.FORWARD, seg=6, bevel=0)
    a.pivot('Muzzle_coax', (.18, -.96, .15), t)
    # The gunner's sight and hatch, the smoke dischargers on both cheeks, the team band.
    K.periscope(a, (.3, -.3, .35), facing=(0, -1, 0), parent=t, size=(.16, .14, .13))
    C.hatch(a, (-.18, .2, .36), r=.2, parent=t)
    for s in (-1, 1):
        sm = a.part('Smoke_launchers', 'Armor', t)
        for j in range(3):
            sm.cyl(.03, .15, loc=(s * (.6 + j * .015), -.1 + j * .09, .26), rot=(R90 - .5, 0, s * .8), seg=8, bevel=0)
    a.part('Team_band', 'Team', t).box((1.0, .015, .05), loc=(0, .715, .16), bevel=0)


def armored_car(a, detail=False):
    """The armoured car: see the module docstring."""
    _hull(a)
    _wheels(a)
    _turret(a)
    K.dust(a, (0, 0, .3), radius=2.4, k=.14)
    k.clean(a)


BUILDERS = {
    'armored_car': (armored_car, dict(ao_distance=.4, grime_height=.45)),
}
