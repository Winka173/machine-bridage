"""Prompt 35 wave 3 (lane B): the heavy flak tower rebuilt from scratch (spec: Tools/blender/specs/heavy_flak_tower.json).

A KS-19-class 100 mm heavy anti-aircraft gun in a fixed field site built by the Accord (the def's modelSize 7.0 x 6.0 x
3.4 m): an octagonal pit revetted with stacked logs behind an earth berm, open at the rear with log steps; on a timber
floor the gun's pedestal (a cone on cross beams) and on it the turning mount (`Turret`): the carriage cheeks and
trunnions, the cradle with the recuperator over and the recoil buffer under the barrel, the long barrel raised 15
degrees with its multi-baffle muzzle brake, the breech with the loading tray and the fuse setter, the wide gun shield
with its angled wings, the layers' seats and sight boxes; ready shells in racks and ammunition boxes in the revetment's
niches, the optical rangefinder on its tripod behind the pit, a field telephone and a whip. Trimmed under the tower
cap (owner decision 6: the old file had 8,902 triangles; at most 1.5 x 4,000).

Its own body: not the 40 mm AA tower's (a Bofors on its cruciform carriage in a sandbag ring). Runtime nodes kept:
`Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`; old part names `Pedestal`, `Carriage`, `Trunnions`,
`Recuperators`, `Breech`, `Gun_shield`, `Sight_box`, `Revetment`, `Platform`, `Base`, `Shells`, `Ammo_boxes`,
`Rangefinder`, `Antenna`. Metres, +Z up, -Y front, +X left.
"""
import math
import random

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
PAD = 0.0                       # the ground (the old earth pad is gone: the site is dug in)
FLOOR = .25                     # the timber floor's top
Y0 = .45                        # the pit's centre line
TURN = (0, Y0, FLOOR + .75)      # the mount's yaw pivot
ELEV = math.radians(15)
RI = 2.3                        # the revetment's inner radius
WALL = .95                      # the log wall's height above the floor


def _site(a, rng):
    # The berm round the log wall: an octagonal ring of sloped earth, open at the rear.
    berm = a.part('Berm', 'Dirt')
    for i in range(8):
        if i == 4:
            continue                                   # the rear side (+Y) is the way in
        u = i * math.tau / 8 - R90                     # the side's middle (side 0 faces the front, -Y)
        c = ((RI + .3) * math.cos(u), Y0 + (RI + .3) * math.sin(u))
        k.block(berm, (2.1, .75, WALL * .62), loc=(c[0], c[1], PAD + WALL * .31), rot=(0, 0, u + R90),
                chamfer=.1, taper=(.92, .5))
    # The revetment: logs stacked four high on each side of the octagon, posts at the corners.
    logs = a.part('Revetment', 'LogWood')
    posts = a.part('Revetment_posts', 'Wood')
    for i in range(8):
        if i == 4:
            continue
        u0 = i * math.tau / 8 - R90 - math.tau / 16
        u1 = u0 + math.tau / 8
        p0 = (RI * math.cos(u0), Y0 + RI * math.sin(u0))
        p1 = (RI * math.cos(u1), Y0 + RI * math.sin(u1))
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        for j in range(4):
            z = FLOOR + .12 + j * .23
            jl, jr = rng.uniform(-.1, .14), rng.uniform(-.015, .015)     # every log cut a little differently
            logs.cyl(.12 + jr, L + .16 + jl, loc=((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, z), rot=(0, R90, ang),
                     seg=6, bevel=0)
        posts.cyl(.09, WALL + .2, loc=(p0[0], p0[1], FLOOR + (WALL + .2) / 2), seg=6, bevel=0)
        # A course of sandbags along the crest of the log wall.
        P.sandbag_run(a, [(p0[0] * 1.03, (p0[1] - Y0) * 1.03 + Y0, FLOOR + WALL),
                          (p1[0] * 1.03, (p1[1] - Y0) * 1.03 + Y0, FLOOR + WALL)], courses=1, bag=(.62, .36, .18),
                      part='Sandbags', seed=80 + i, lean=True)
    # The timber floor (the site's base, dug in so it sits at the pad height) and the log steps at the rear entrance.
    floor = a.part('Base', 'Wood')
    k.extrude(floor, [(RI * math.cos(u), Y0 + RI * math.sin(u)) for u in [i * math.tau / 8 - R90 - math.tau / 16 for i in range(8)]],
              FLOOR, loc=(0, 0, FLOOR / 2), axis='Z', chamfer=0)
    for j in range(7):
        a.part('Floor_planks', 'Wood').box((.02, 3.2 + rng.uniform(0, .8), .012), loc=(-1.5 + j * .5, Y0, FLOOR + .004),
                                           bevel=0)
    for j in range(2):
        logs.cyl(.1, 1.4, loc=(0, Y0 + RI + .15 + j * .28, .12 + j * .1), rot=(0, R90, 0), seg=6, bevel=0)
    for i in range(10):
        u = i * math.tau / 10
        K.dust(a, (math.cos(u) * 2.7, Y0 + math.sin(u) * 2.7, PAD), radius=1.2, k=.3)
    K.dust(a, (0, Y0, FLOOR), radius=2.3, k=.22)


def _gun(a):
    # The pedestal: cross beams on the floor, the cone, the race ring.
    ped = a.part('Pedestal', 'Armor')
    beams = a.part('Platform', 'LogWood')
    for ang in (0, R90):
        k.block(beams, (2.6, .3, .2), loc=(TURN[0], TURN[1], FLOOR + .1), rot=(0, 0, ang), chamfer=.03)
    k.lathe(ped, [(.75, 0), (.75, .06), (.5, .4), (.45, .62), (0, .62)], loc=(TURN[0], TURN[1], FLOOR + .1), seg=14,
            worn=(1,))
    K.bolt_ring(a.part('Kit_bolts', 'Steel'), (TURN[0], TURN[1], FLOOR + .2), (0, 0, 1), .68, 12, r=.03, h=.04)
    t = a.pivot('Turret', TURN)
    car = a.part('Carriage', 'Team', t)
    k.lathe(car, [(.7, -.04), (.72, 0), (.72, .1), (.62, .14), (0, .14)], seg=16, worn=(2,))
    for s in (-1, 1):
        k.extrude(car, [(-.55, .1), (.55, .1), (.35, .95), (-.25, 1.05), (-.5, .6)], .1, loc=(s * .42, 0, 0),
                  axis='X', chamfer=.025)
    g = P.Elev((0, -.05, .95), ELEV)
    tr = a.part('Trunnions', 'Steel', t)
    tr.cyl(.1, 1.0, loc=g.at(0), rot=(0, R90, 0), seg=10, bevel=0)
    cr = a.part('Cradle', 'Armor', t)
    k.block(cr, (.5, 1.9, .42), loc=g.at(.25), rot=g.box_rot, chamfer=.05)
    rec = a.part('Recuperators', 'Steel', t)
    k.lathe(rec, [(.11, 0), (.11, 1.7), (.08, 1.78)], loc=g.at(-.5, up=.3), rot=g.lathe_rot, seg=10)
    k.lathe(rec, [(.09, 0), (.09, 1.5), (.06, 1.56)], loc=g.at(-.4, up=-.27), rot=g.lathe_rot, seg=8)
    br = a.part('Breech', 'Undercarriage', t)
    k.block(br, (.48, .6, .46), loc=g.at(-.95), rot=g.box_rot, chamfer=.04)
    a.part('Loading_tray', 'Steel', t).box((.34, 1.0, .04), loc=g.at(-1.6, up=-.15), rot=g.box_rot, bevel=0)
    fs = a.part('Fuse_setter', 'Armor', t)
    k.block(fs, (.32, .45, .35), loc=(.62, .5, .62), chamfer=.03)
    a.part('Fuse_dials', 'Steel', t).cyl(.08, .03, loc=(.62, .27, .7), rot=(R90, 0, 0), seg=10, bevel=0)
    # The barrel: collar, tube tapering, the multi-baffle muzzle brake.
    bp = a.part('Main_cannon', 'Steel', t)
    k.lathe(bp, [(.12, 0), (.12, .3), (.09, .38), (.075, 1.2), (.065, 2.95), (0, 2.95)], loc=g.at(.9),
            rot=g.lathe_rot, seg=12, worn=(1,))
    mb = a.part('Muzzle_brake', 'Undercarriage', t)
    prof = [(.065, 0)]
    for j in range(4):
        z = .05 + j * .1
        prof += [(.11, z), (.11, z + .06), (.08, z + .07)]
    prof += [(.08, .48), (0, .48)]
    k.lathe(mb, prof, loc=g.at(3.82), rot=g.lathe_rot, seg=10)
    a.pivot('Muzzle_main', g.at(4.31), t)
    # The wide gun shield with its angled wings (Team), riveted.
    sh = a.part('Gun_shield', 'Team', t)
    k.extrude(sh, [(-.5, 0), (.5, 0), (.5, 1.05), (.18, 1.15), (-.18, 1.15), (-.5, 1.05)], .035, loc=(0, -.75, .2),
              rot=(R90 - .12, 0, 0), axis='Z', chamfer=.008)
    for s in (-1, 1):
        k.extrude(sh, [(-.42, 0), (.42, 0), (.38, .95), (-.38, .95)], .035, loc=(s * .85, -.55, .2),
                  rot=(R90 - .1, 0, -s * .55), axis='Z', chamfer=.008)
    rv = a.part('Kit_rivets', 'Steel', t)
    for j in range(8):
        rv.cyl(.018, .03, loc=(-.42 + j * .12, -.69, 1.2), rot=(R90, 0, 0), seg=5, bevel=0)
    # The layers' seats and the sight boxes on both sides.
    for s in (-1, 1):
        K.chamfer_box(a.part('Seats', 'Canvas', t), (.3, .3, .07), loc=(s * .75, .2, .55), c=.012)
        a.part('Seat_posts', 'Steel', t).limb((s * .55, .2, .12), (s * .75, .2, .52), .05, .05, bevel=0)
        k.block(a.part('Sight_box', 'Armor', t), (.22, .3, .25), loc=(s * .62, -.15, 1.0), chamfer=.025)
        a.part('Glass', 'Glass', t).box((.14, .01, .08), loc=(s * .62, -.305, 1.05), bevel=0)
        k.lathe(a.part('Handwheels', 'Steel', t), [(.13, -.012), (.13, .012)], loc=(s * .68, .05, .7),
                rot=(0, R90, 0), seg=10)
    return t


def _kit(a, rng):
    # Ammunition boxes in two niches cut in the log wall (front left, front right), ready shells in racks at the rear.
    boxes = a.part('Ammo_boxes', 'Crate')
    bands = a.part('Crate_bands', 'Steel')
    for x, y, r in ((-1.75, -.9, .8), (1.75, -.9, -.8)):
        for j in range(2):
            K.crate(boxes, bands, (.8, .32, .26), (x, y, FLOOR + j * .26), rot=(0, 0, r + j * .05), bands=1)
    shells = a.part('Shells', 'Hazard')
    tips = a.part('Shell_tips', 'Steel')
    rack = a.part('Shell_racks', 'Wood')
    for x0 in (-1.5, 1.0):
        rack.box((.06, .5, .6), loc=(x0 - .05, 2.05, FLOOR + .3), bevel=0)
        rack.box((.06, .5, .6), loc=(x0 + .65, 2.05, FLOOR + .3), bevel=0)
        for j in range(5):
            x = x0 + .05 + j * .11
            shells.cyl(.05, .8, loc=(x, 2.05, FLOOR + .3), rot=(R90, 0, 0), seg=6, bevel=0)
            tips.cyl(.03, .14, loc=(x, 1.6, FLOOR + .3), rot=(R90, 0, 0), seg=5, bevel=0)
    # Spent cases on the floor.
    for j in range(5):
        shells.cyl(.055, .7, loc=(rng.uniform(-1.2, 1.2), rng.uniform(1.0, 1.7), FLOOR + .055),
                   rot=(R90, 0, rng.uniform(-.8, .8) + R90), seg=6, bevel=0)
    # The optical rangefinder on its tripod behind the pit (rear right), its operator's stool.
    x, y = -2.3, 2.45
    rf = a.part('Rangefinder', 'Armor')
    for i in range(3):
        u = i * math.tau / 3 + .5
        a.part('Rangefinder_tripod', 'Steel').limb((x + math.cos(u) * .45, y + math.sin(u) * .45, PAD),
                                                   (x, y, PAD + 1.25), .04, .04, bevel=0)
    k.lathe(rf, [(.07, -.8), (.09, -.75), (.09, .75), (.07, .8)], loc=(x, y, PAD + 1.38), rot=(0, R90, .3), seg=8)
    k.block(rf, (.22, .2, .2), loc=(x, y, PAD + 1.3), chamfer=.03)
    for s in (-1, 1):
        a.part('Glass', 'Glass').cyl(.06, .02, loc=(x + s * .76 * math.cos(.3), y + s * .76 * math.sin(.3),
                                                    PAD + 1.38), rot=(0, R90, .3), seg=8, bevel=0)
    # Crew kit: helmets, a jerrycan, an extinguisher, a shovel and a pick against the wall, stones thrown up round
    # the berm (each its own size).
    for x, y in ((-1.0, 1.9), (-.8, 2.0)):
        a.part('Helmets', 'Crate').sphere(.13, loc=(x, y, FLOOR), seg=8, rings=6, cut=0)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (1.5, 1.6, FLOOR), rot=(0, 0, .6))
    k.lathe(a.part('Extinguishers', 'BarrelRed'), [(.07, 0), (.07, .38), (.04, .44), (0, .46)], loc=(-1.6, 1.3, FLOOR),
            seg=8, worn=(1,))
    tools = a.part('Tools', 'Steel')
    tools.tube([(1.95, .1, FLOOR + .02), (2.05, .2, FLOOR + 1.0)], .018, seg=4)
    tools.box((.22, .03, .28), loc=(1.96, .1, FLOOR + .13), rot=(.1, 0, .8), bevel=0)
    tools.tube([(1.9, -.4, FLOOR + .02), (2.0, -.3, FLOOR + .9)], .018, seg=4)
    tools.box((.45, .04, .05), loc=(2.0, -.3, FLOOR + .9), rot=(0, .3, .8), bevel=0)
    st = a.part('Stones', 'Rock')
    for j in range(14):
        z = rng.uniform(.06, .14)
        u = rng.uniform(0, math.tau)
        r = rng.uniform(2.95, 3.05)
        st.box((z * 1.4, z, z * .7), loc=(math.cos(u) * r * .98, Y0 + math.sin(u) * r * .9, z * .2),
               rot=(rng.uniform(-.3, .3), rng.uniform(-.3, .3), rng.uniform(0, 3)), bevel=0)
    # The field telephone on a post, a whip antenna, the cable into the pit.
    a.part('Stakes', 'Wood').cyl(.04, 1.0, loc=(2.3, 2.3, PAD + .5), seg=5, bevel=0)
    k.block(a.part('Field_phone', 'Armor'), (.22, .12, .18), loc=(2.3, 2.23, PAD + .9), chamfer=.015)
    K.whip_antenna(a.part('Antenna', 'Steel'), (2.5, 2.5, PAD + .3), h=1.6, r=.025, lean=.1)
    a.part('Kit_cables', 'Undercarriage').tube([(2.3, 2.3, PAD + .05), (1.4, 2.9, PAD + .02), (.6, 3.05, PAD + .2),
                                                (.2, 2.6, FLOOR + .03)], .02, seg=4)


def heavy_flak_tower(a):
    """The heavy flak tower: see the module docstring."""
    rng = random.Random(3571)
    _site(a, rng)
    _gun(a)
    _kit(a, rng)
    k.clean(a)


BUILDERS = {
    'heavy_flak_tower': (heavy_flak_tower, dict(ao_distance=.6, grime_height=.6)),
}
