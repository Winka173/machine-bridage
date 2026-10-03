"""Prompt 35 wave 3 (lane B): the 40 mm AA gun tower rebuilt from scratch (spec: Tools/blender/specs/aa_gun_tower.json).

A Bofors 40 mm L/70 dug in by the Accord (the def's modelSize 5.5 x 5.5 x 3.2 m): an irregular earth pad edged with
sleepers, a round gun pit of sandbags (two courses, open at the rear for the crew), the gun's cruciform carriage with
its four outrigger arms on jack pads, and on it the turning mount (`Turret`): the two cheeks and the elevating arc,
the cradle with the long L/70 barrel (recoil-spring jacket, conical flash hider) raised 25 degrees, the loader
housing with the vertical magazine guide and a four-round clip in it, the front shield plates, the layer's and the
trainer's seats with their reflex sights; behind the pit the fire-control radar dish on a tripod mast, its cable to
the gun; ready-use clip racks, ammunition crates, spent cases, a field telephone; the Team colour on the shield.

Its own body: not the heavy flak tower's (a KS-19 on its platform in a timber revetment) nor the AA turret family's.
Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`; the old part names `Turntable`, `Mount`,
`Shield`, `Clips`, `Pad`, `Radar_dish`, `Radar_post`, `Sandbags`. Metres, +Z up, -Y front, +X left.
"""
import math
import random

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
PAD = .25
TZ = PAD + .62              # the mount's yaw plane
ELEV = math.radians(25)


def _emplacement(a, rng):
    outline = [(-2.6, -2.3), (-.8, -2.6), (1.4, -2.45), (2.65, -1.5), (2.55, .7), (2.4, 2.35), (.4, 2.6),
               (-1.6, 2.4), (-2.6, 1.3), (-2.7, -.6)]
    P.earth_pad(a, outline, PAD)
    wood = a.part('Base_timbers', 'Wood')
    for (x0, y0), (x1, y1) in (((-2.6, -2.3), (1.4, -2.45)), ((2.65, -1.5), (2.55, .7))):
        L = math.hypot(x1 - x0, y1 - y0)
        k.block(wood, (L, .2, .2), loc=((x0 + x1) / 2, (y0 + y1) / 2, PAD * .6),
                rot=(0, 0, math.atan2(y1 - y0, x1 - x0)), chamfer=.03)
    # The gun pit: a ring of sandbags round the front and sides, open at the rear (the crew's way in).
    R = 2.05
    path = [(math.sin(t) * R, -math.cos(t) * R, PAD) for t in [math.radians(d) for d in range(-140, 141, 14)]]
    P.sandbag_run(a, path, courses=2, bag=(.66, .38, .2), part='Sandbags', seed=61, lean=True)
    for t in (-140, 140):
        x, y = math.sin(math.radians(t)) * R, -math.cos(math.radians(t)) * R
        wood.cyl(.07, .7, loc=(x, y + .15, PAD + .35), seg=6, bevel=0)
    # The Pad: the levelled timber floor of the pit under the carriage.
    floor = a.part('Pad', 'Wood')
    for i in range(7):
        floor.box((2.6, .3, .05), loc=(0, -.9 + i * .3, PAD + .025), bevel=0)
    for i in range(10):
        u = i * math.tau / 10
        K.dust(a, (math.cos(u) * 2.3, math.sin(u) * 2.3, PAD), radius=1.0, k=.28)
    K.dust(a, (0, 0, PAD), radius=2.8, k=.18)


def _carriage(a):
    """The towed carriage, wheels off: the cruciform with four outrigger arms on jack pads (fixed, `Turntable`)."""
    tt = a.part('Turntable', 'Armor')
    k.block(tt, (1.3, 1.3, .22), loc=(0, .2, PAD + .3), chamfer=.06)
    for i in range(4):
        u = i * R90 + math.pi / 4
        dx, dy = math.cos(u), math.sin(u)
        tt.limb((dx * .5, .2 + dy * .5, PAD + .3), (dx * 1.55, .2 + dy * 1.55, PAD + .18), .18, .14, bevel=0)
        jack = a.part('Jacks', 'Steel')
        k.lathe(jack, [(.18, 0), (.18, .04), (.05, .06), (.05, .2)], loc=(dx * 1.6, .2 + dy * 1.6, PAD + .05), seg=8)
    k.ring(a.part('Race', 'Steel'), [(.5, -.03), (.58, -.03), (.58, .04), (.5, .04)], loc=(0, .2, TZ - .2), seg=16)
    bolts = a.part('Kit_bolts', 'Steel')
    K.bolt_ring(bolts, (0, .2, TZ - .16), (0, 0, 1), .54, 12, r=.025, h=.03)
    for i in range(4):
        u = i * R90 + math.pi / 4
        for f in (.8, 1.2):
            bolts.cyl(.03, .04, loc=(math.cos(u) * f, .2 + math.sin(u) * f, PAD + .3), seg=6, bevel=0)


def _mount(a):
    t = a.pivot('Turret', (0, .2, TZ))
    mount = a.part('Mount', 'Team', t)
    k.lathe(mount, [(.62, -.2), (.64, -.15), (.64, -.05), (.55, 0), (0, 0)], seg=16, worn=(2,))
    # The two cheeks carrying the trunnions, the elevating arc on the right cheek.
    for s in (-1, 1):
        k.extrude(mount, [(-.45, 0), (.45, 0), (.3, .55), (-.15, .7), (-.4, .4)], .08, loc=(s * .33, 0, 0),
                  axis='X', chamfer=.02)
    arc = a.part('Elevation_arc', 'Steel', t)
    k.sweep(arc, [(-.02, -.03), (.02, -.03), (.02, .03), (-.02, .03)],
            [(-.42, .55 * math.cos(u) - .1, .25 + .55 * math.sin(u)) for u in [math.radians(d) for d in range(-10, 90, 15)]])
    for s in (-1, 1):
        k.lathe(a.part('Handwheels', 'Steel', t), [(.12, -.015), (.12, .015)], loc=(s * .55, .35, .45),
                rot=(0, R90, 0), seg=10)
    g = P.Elev((0, -.05, .62), ELEV)
    # The cradle and the loader housing behind the trunnions, the vertical magazine guide on top with a clip.
    cr = a.part('Cradle', 'Armor', t)
    k.block(cr, (.42, .8, .34), loc=g.at(-.05), rot=g.box_rot, chamfer=.04)
    load = a.part('Loader', 'Undercarriage', t)
    k.block(load, (.34, .7, .4), loc=g.at(-.5, up=.02), rot=g.box_rot, chamfer=.03)
    guide = a.part('Clips', 'Steel', t)
    for dx in (-.09, .09):
        guide.box((.03, .05, .55), loc=g.at(-.45, dx, up=.45), rot=g.box_rot, bevel=0)
    for j in range(4):
        k.lathe(a.part('Clip_rounds', 'Hazard', t), [(.02, 0), (.02, .26), (.012, .32), (0, .34)],
                loc=g.at(-.48 + j * .01, -.06 + j * .04, up=.28 + j * .03), rot=(-ELEV, 0, 0), seg=6)
    # The barrel: the recoil-spring jacket, the long bore and the conical flash hider.
    bp = a.part('Main_cannon', 'Steel', t)
    k.lathe(bp, [(.085, 0), (.085, .7), (.06, .74), (.045, .8), (.045, 2.35), (0, 2.35)], loc=g.at(.15),
            rot=g.lathe_rot, seg=10, worn=(1,))
    for f in (.3, .6):
        bp.cyl(.095, .04, loc=g.at(.15 + f), rot=g.lathe_rot, seg=10, bevel=0)
    fh = a.part('Muzzle_brake', 'Undercarriage', t)
    k.lathe(fh, [(.045, 0), (.06, .02), (.1, .3), (.105, .32), (.085, .32), (0, .32)], loc=g.at(2.48),
            rot=g.lathe_rot, seg=10)
    a.pivot('Muzzle_main', g.at(2.81), t)
    # The front shield: three plates, the middle one with the barrel slot; Team colour.
    sh = a.part('Shield', 'Team', t)
    for s, ang in ((-1, .5), (0, 0), (1, -.5)):
        x = s * .52
        k.extrude(sh, [(-.28, 0), (.28, 0), (.24, .75), (-.24, .75)], .03, loc=(x, -.55 + abs(s) * .12, .25),
                  rot=(R90 - .2, 0, ang), axis='Z', chamfer=.008, corner=.02)
    rv = a.part('Kit_rivets', 'Steel', t)
    for s in (-1, 1):
        a.part('Shield_struts', 'Steel', t).limb((s * .5, -.48, .6), (s * .33, -.1, .5), .03, .03, bevel=0)
        for j in range(4):
            rv.cyl(.018, .03, loc=(s * (.4 + j * .06), -.47 - j * .035, .9), rot=(R90, 0, 0), seg=5, bevel=0)
    for j in range(5):
        rv.cyl(.018, .03, loc=(-.2 + j * .1, -.58, .92), rot=(R90, 0, 0), seg=5, bevel=0)
    # Grab handles on the cheeks, the firing pedals, the elevation lock.
    for s in (-1, 1):
        K.handle(a.part('Kit_handles', 'Steel', t), (s * .38, .25, .5), (s * .38, .4, .5), (s, 0, 0), h=.05, r=.012)
        a.part('Pedals', 'Undercarriage', t).box((.12, .2, .03), loc=(s * .62, -.05, .12), rot=(.3, 0, 0), bevel=0)
    # The layer's and the trainer's seats with their reflex sights.
    seat = a.part('Seats', 'Canvas', t)
    sight = a.part('Sights', 'Armor', t)
    glass = a.part('Glass', 'Glass', t)
    for s in (-1, 1):
        K.chamfer_box(seat, (.3, .28, .06), loc=(s * .62, .25, .5), c=.012)
        K.chamfer_box(seat, (.3, .05, .3), loc=(s * .62, .4, .66), c=.012)
        a.part('Seat_posts', 'Steel', t).limb((s * .55, .25, .1), (s * .62, .25, .47), .05, .05, bevel=0)
        sight.box((.04, .04, .4), loc=(s * .5, -.05, .75), bevel=0)
        k.block(sight, (.12, .16, .12), loc=(s * .5, -.05, .97), chamfer=.015)
        glass.box((.09, .01, .07), loc=(s * .5, -.135, 1.0), bevel=0)
    return t


def _radar(a):
    """The fire-control radar behind the pit: a tripod mast, the dish on its yoke, the cable to the gun."""
    x, y = -1.85, 1.95
    post = a.part('Radar_post', 'Steel')
    for i in range(3):
        u = i * math.tau / 3 + .4
        post.limb((x + math.cos(u) * .55, y + math.sin(u) * .55, PAD), (x, y, PAD + 1.6), .05, .05, bevel=0)
    post.cyl(.06, .5, loc=(x, y, PAD + 1.8), seg=8, bevel=0)
    k.block(a.part('Radar_box', 'Armor'), (.4, .3, .3), loc=(x, y, PAD + 2.1), chamfer=.03)
    dish = a.part('Radar_dish', 'Steel')
    feed = a.part('Radar_feed', 'Undercarriage')
    K.dish(dish, feed, (x, y - .15, PAD + 2.45), r=.45, normal=(.35, -1, .25), seg=14)
    a.part('Kit_cables', 'Undercarriage').tube([(x, y, PAD + .05), (-1.1, 1.2, PAD + .03), (-.4, .6, PAD + .05)],
                                               .02, seg=4)


def _kit(a, rng):
    # Ready-use clip racks (wooden racks of upright four-round clips) and crates inside the pit's rear.
    rack = a.part('Clip_racks', 'Wood')
    rounds = a.part('Clip_rounds', 'Hazard')
    for x in (1.3, -1.3):
        k.block(rack, (.7, .3, .45), loc=(x, 1.25, PAD + .225), chamfer=.02)
        for j in range(5):
            for dy in (-.07, .07):
                rounds.cyl(.022, .3, loc=(x - .28 + j * .14, 1.25 + dy, PAD + .55), seg=5, bevel=0)
                a.part('Clip_tips', 'Steel').cyl(.014, .05, loc=(x - .28 + j * .14, 1.25 + dy, PAD + .72), seg=5,
                                                 bevel=0)
    k.lathe(a.part('Extinguishers', 'BarrelRed'), [(.07, 0), (.07, .38), (.04, .44), (0, .46)], loc=(-.5, 1.75, PAD),
            seg=8, worn=(1,))
    P.toolbox(a, (.5, 1.75, PAD + .15), (.5, .25, .3))
    crates = a.part('Crates', 'Crate')
    straps = a.part('Kit_straps', 'Steel')
    K.crate(crates, straps, (.8, .45, .35), (1.95, 2.1, PAD), rot=(0, 0, .3))
    K.crate(crates, straps, (.8, .45, .35), (1.95, 2.1, PAD + .35), rot=(0, 0, .22), bands=1)
    # Spent cases on the pit floor, a field telephone on a stake, a whip antenna.
    cases = a.part('Spent_cases', 'Hazard')
    for j in range(7):
        cases.cyl(.022, .3, loc=(rng.uniform(-.9, .9), rng.uniform(-.2, 1.0), PAD + .07),
                  rot=(R90, 0, rng.uniform(0, 3)), seg=5, bevel=0)
    a.part('Stakes', 'Wood').cyl(.04, .9, loc=(.7, 1.9, PAD + .45), seg=5, bevel=0)
    k.block(a.part('Field_phone', 'Armor'), (.22, .12, .18), loc=(.7, 1.83, PAD + .8), chamfer=.015)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-2.2, 1.0, PAD + .3), h=1.4, r=.025)
    K.net_roll(a.part('Tarp', 'Canvas'), a.part('Kit_straps', 'Undercarriage'), (1.4, -1.5, PAD + .42), length=1.3,
               r=.13, axis='Y')


def aa_gun_tower(a):
    """The 40 mm AA gun tower: see the module docstring."""
    rng = random.Random(3551)
    _emplacement(a, rng)
    _carriage(a)
    _mount(a)
    _radar(a)
    _kit(a, rng)
    k.clean(a)


BUILDERS = {
    'aa_gun_tower': (aa_gun_tower, dict(ao_distance=.55, grime_height=.6)),
}
