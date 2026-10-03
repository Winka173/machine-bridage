"""Prompt 35 wave 4 (lane C): the demolition line vehicle rebuilt from scratch
(spec: Tools/blender/specs/demolition_line_vehicle.json).

An M1150 Assault Breacher Vehicle (the def's modelSize 6.45 x 3.02 x 2.02 m): the Abrams hull (shallow glacis,
flat deck, the big exhaust grille on the rear plate, seven road wheels a side behind the heavy skirts, the rear
sprocket and front idler); the full-width mine plough on its push arms ahead of the nose (the curved mouldboard,
the tines, the depth skids); the low armoured box turret carrying the two MICLIC line-charge launcher boxes on
its rear, tilted up, with the rocket noses showing; the remote weapon station with the M2 on its cradle and the
sensor head on the turret front (the main weapon, on `Turret`); the lane-marking dispensers on the rear corners.

Runtime nodes kept: `Turret`, `Turret_body`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Point_exhaust`,
`Point_fire`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TX, TW = 1.1, .5
WR = .29
WHEELS = (-1.9, -1.25, -.6, .05, .7, 1.35, 2.0)
TOP = 1.0
NOSE, TAIL = -2.55, 3.05
TUR = (0, .25, TOP)


def _hull(a):
    hull = a.part('Hull', 'Team')
    prof = [(NOSE, .62), (-1.6, TOP), (2.95, TOP), (TAIL, .92), (TAIL - .03, .45), (-2.3, .34)]
    k.extrude(hull, prof, 2.3, axis='X', chamfer=.05, corner=.03)
    low = a.part('Hull_lower', 'Armor')
    k.extrude(low, [(NOSE + .1, .6), (-2.25, .32), (2.9, .32), (2.95, .7)], (TX - TW / 2) * 2, axis='X', chamfer=.02)
    for s in (-1, 1):
        K.fender(a.part('Fenders', 'Team'), TX + .03, NOSE + .1, TAIL - .05, .9, .5, s, lip=.03)
        sk = a.part('Skirts', 'Team')
        sk.box((.08, 1.1, .5), loc=(s * (TX + .29), -1.9, .68), bevel=.02)       # the thick front skirt
        for j in range(4):
            sk.box((.03, .98, .42), loc=(s * (TX + .28), -.85 + j * 1.0, .7), bevel=0)
        K.rivet_line(a.part('Kit_steel', 'Steel'), (s * (TX + .34), -2.35, .8), (s * (TX + .34), -1.45, .8), (s, 0, 0),
                     pitch=.15, r=.016)
        a.part('Team_band', 'Team').box((.012, 2.6, .08), loc=(s * (TX + .3), .7, .82), bevel=0)
    # The driver's hatch with its three periscopes, lamps, tow eyes.
    C.hatch(a, (0, -1.35, TOP), r=.25, periscope=True)
    for x in (-.25, .25):
        K.periscope(a, (x, -1.6, TOP + .01), facing=(0, -1, 0), size=(.12, .07, .06))
    for s in (-1, 1):
        K.lamp(a, (s * 1.0, -2.0, .92), (0, -1, .2), r=.06, guard=True)
    # The engine deck and the big exhaust grille across the rear plate, the lane-marking dispensers on the corners.
    K.grille(a, (0, 2.25, TOP + .02), 1.6, 1.0, facing=(0, 0, 1), slats=7, frame_mat='Team')
    K.grille(a, (0, TAIL + .01, .7), 1.4, .35, facing=(0, 1, 0), slats=5, frame_mat='Armor')
    a.pivot('Point_exhaust', (0, TAIL + .05, .7))
    lm = a.part('Lane_markers', 'Armor')
    for s in (-1, 1):
        k.block(lm, (.3, .3, .5), loc=(s * 1.0, TAIL - .1, TOP), chamfer=.03)
        a.part('Lane_marker_tops', 'Hazard').box((.3, .3, .06), loc=(s * 1.0, TAIL - .1, TOP + .52), bevel=0)
        a.part('Tail_lamps', 'LavaGlow').box((.08, .02, .05), loc=(s * .95, TAIL + .01, .95), bevel=0)
    a.pivot('Point_fire', (0, 1.8, TOP + .3))
    C.stowage_box(a, (.42, .9, .26), (TX + .03, 1.6, .9), mat='Armor', latches=2)
    C.jerry_rack(a, (-(TX + .03), 1.6, .9), count=2, axis='Y', rot=(0, 0, R90))


def _plough(a):
    """The full-width mine plough: push arms from the hull, the curved mouldboard, tines and depth skids."""
    pa = a.part('Plow_arms', 'Armor')
    for s in (-1, 1):
        pa.limb((s * 1.15, -1.9, .55), (s * 1.2, -2.85, .35), .07, .1, bevel=0)
        pa.limb((s * .8, NOSE + .1, .75), (s * .9, -2.95, .55), .05, .05, bevel=0)        # lift rams
    mb = a.part('Mine_plow', 'Team')
    prof = [(0, 0), (.08, .05), (.12, .2), (.1, .45), (.02, .62), (-.04, .62), (.03, .45), (.05, .2), (0, .06)]
    k.extrude(mb, [(-y - 3.0, z + .15) for y, z in prof], 3.0, axis='X', chamfer=.02, corner=0)
    tn = a.part('Plow_tines', 'Steel')
    for i in range(13):
        x = (i - 6) * .23
        tn.limb((x, -3.05, .22), (x, -3.3, .02), .025, .05, bevel=0)
    sk = a.part('Plow_skids', 'Steel')
    for s in (-1, 1):
        k.extrude(sk, [(-3.35, .02), (-2.85, .02), (-2.8, .12), (-3.3, .12), (-3.42, .1)], .06, loc=(s * 1.45, 0, 0),
                  axis='X', chamfer=0)
    a.part('Plow_marks', 'Hazard').box((.25, .02, .3), loc=(1.35, -3.1, .55), bevel=0)
    a.part('Plow_marks', 'Hazard').box((.25, .02, .3), loc=(-1.35, -3.1, .55), bevel=0)


def _running_gear(a):
    for s in (-1, 1):
        C.running_gear(a, s, TX, TW, WHEELS, WR, sprocket=(2.6, .5, .26), idler=(-2.35, .5, .25),
                       rollers=[(-1.2, .66), (.7, .66)], pitch=.22, hide_top=(-2.4, 2.5, .5), disc_mat='Armor',
                       wheel_w=.18, seg=8, teeth=12)


def _turret(a):
    t = a.pivot('Turret', TUR)
    K.turret_ring(a.part('Turret_ring', 'Armor'), TUR, .9, h=.05)
    body = a.part('Turret_body', 'Team', t)
    bot = [(-.55, -1.35), (.55, -1.35), (1.05, -.9), (1.08, 1.4), (-1.08, 1.4), (-1.05, -.9)]
    top = [(-.45, -1.05), (.45, -1.05), (.92, -.7), (.95, 1.3), (-.95, 1.3), (-.92, -.7)]
    C.slab_loft(body, bot, top, 0, .45)
    # The two MICLIC launcher boxes on the rear, tilted up, rocket noses at their fronts.
    for s in (-1, 1):
        mc = a.part('Miclic_boxes', 'Armor', t)
        k.block(mc, (.75, 1.5, .42), loc=(s * .5, .55, .48), rot=(.28, 0, 0), chamfer=.04)
        a.part('Miclic_rockets', 'Fuel', t).cyl(.13, .3, loc=(s * .5, -.25, .78), rot=(R90 + .28, 0, 0), seg=10,
                                               bevel=0)
        a.part('Kit_steel', 'Steel', t).box((.05, .3, .4), loc=(s * .5, 1.2, .45), bevel=0)
        a.part('Team_band', 'Team', t).box((.76, .5, .01), loc=(s * .5, .6, .91), rot=(.28, 0, 0), bevel=0)
    # The remote weapon station on the front right: the turned base, the cradle (mantlet), the M2, the sensors.
    rws = a.part('Rws', 'Armor', t)
    k.lathe(rws, [(.24, .45), (.24, .5), (.14, .58), (.12, .7)], loc=(-.45, -.55, 0), seg=10, worn=(1,))
    cr = a.part('Cradle', 'Armor', t)
    k.block(cr, (.36, .4, .2), loc=(-.45, -.55, .7), chamfer=.02)
    gun = a.part('Main_cannon', 'Steel', t)
    k.lathe(gun, [(.04, 0), (.04, .22), (.026, .26), (.022, 1.05), (0, 1.05)], loc=(-.45, -.8, .84), rot=K.FORWARD,
            seg=8, worn=(1,))
    k.lathe(a.part('Muzzle_brake', 'Undercarriage', t), [(.022, 0), (.035, .02), (.035, .1), (0, .1)],
            loc=(-.45, -1.85, .84), rot=K.FORWARD, seg=8, worn=(1,))
    a.pivot('Muzzle_main', (-.45, -1.97, .84), t)
    k.block(a.part('Sensor', 'Armor', t), (.18, .22, .18), loc=(-.7, -.6, .78), chamfer=.02)
    a.part('Glass', 'Glass', t).box((.14, .01, .1), loc=(-.7, -.715, .87), bevel=0)
    C.ammo_tins(a, (-.2, -.55, .72), n=1, size=(.12, .3, .2), parent=t)
    C.hatch(a, (.5, -.55, .45), r=.24, parent=t, periscope=True)
    for s in (-1, 1):
        K.smoke_dischargers(a, .98, -.75, .35, s, count=3, parent=t)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (.9, -.2, .45), h=.3)


def demolition_line_vehicle(a, detail=False):
    """The demolition line vehicle: see the module docstring."""
    _hull(a)
    _plough(a)
    _running_gear(a)
    _turret(a)
    K.dust(a, (0, -2.8, .2), radius=1.5, k=.3)
    K.dust(a, (0, 0, .3), radius=3.0, k=.12)
    k.clean(a)


BUILDERS = {
    'demolition_line_vehicle': (demolition_line_vehicle, dict(ao_distance=.5, grime_height=.5)),
}
