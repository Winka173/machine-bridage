"""Prompt 35 wave 3 (lane B): the inflatable decoy rebuilt from scratch (spec: Tools/blender/specs/inflatable_decoy.json).

An inflatable gun turret of the kind used in the war in Ukraine (Strings note.inflatable_decoy; it mimics the gun
turret; the def's modelSize 5.0 x 4.6 x 2.6 m): on a ground sheet pegged at its corners, a ring of inflated lobes
printed to pass for sandbags, the turret's body as an inflated drum with its welded seams, the dome on it with a
puffed mantlet and the long inflated barrel sagging a little under its own weight, a fabric muzzle brake; hatches and
vision blocks only painted on, a painted Team band; a fibreglass whip; the giveaways for a close look: the tethers
from the dome and the barrel to stakes, the petrol blower humming beside it with its hose, a repair patch, the
folded transport bag.

Its own body: no shape is taken from the gun turret (it only copies the outline). It does not turn (no `Turret`: the
def is unarmed). Old part names kept: `Fabric`, `Skin`, `Seams`, `Blower`, `Stakes`, `Tethers`.
Metres, +Z up, -Y front, +X left.
"""
import math
import random

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
DRUM_R, DRUM_H = 1.25, .95
DZ = .05 + DRUM_H                # top of the drum
DOME = (0, .15, DZ)


def _ground(a, rng):
    k.block(a.part('Pad', 'Canvas'), (4.6, 4.1, .02), loc=(0, .1, .01), rot=(0, 0, .06), chamfer=0)   # laid a little askew
    # The printed "sandbag" ring: inflated lobes round the front and sides, open at the back.
    lobes = a.part('Walls', 'Sandbag')
    R = 1.85
    for i in range(15):
        t = math.radians(-130 + i * (260 / 14))
        x, y = math.sin(t) * R, .1 - math.cos(t) * R
        lobes.sphere((.42, .26, .26), loc=(x, y, .26), rot=(0, 0, t), seg=8, rings=5)
        if i % 2 == 0:
            lobes.sphere((.38, .23, .2), loc=(x * .99, y * .99 + .01, .6), rot=(0, 0, t + .2), seg=7, rings=4)
    lines = a.part('Lobe_print', 'Charred')
    for i in range(14):
        t = math.radians(-130 + (i + .5) * (260 / 14))
        lines.box((.02, .5, .3), loc=(math.sin(t) * (R + .02), .1 - math.cos(t) * (R + .02), .3), rot=(0, 0, t),
                  bevel=0)
    for i in range(6):
        K.dust(a, (rng.uniform(-2, 2), rng.uniform(-2, 2), 0), radius=1.2, k=.22)


def _turret(a):
    skin = a.part('Skin', 'Team')
    # The drum: bulged sides and a rolled top edge (an inflated cushion, not a hard cylinder).
    k.lathe(skin, [(DRUM_R * .9, .05), (DRUM_R, .12), (DRUM_R * 1.04, .5), (DRUM_R, DRUM_H - .08),
                   (DRUM_R * .9, DRUM_H + .02), (0, DRUM_H + .03)], loc=(0, .15, 0), seg=18)
    seams = a.part('Seams', 'Undercarriage')
    for i in range(8):
        u = i * math.tau / 8
        seams.box((.02, .02, DRUM_H - .15), loc=(math.cos(u) * DRUM_R * 1.035, .15 + math.sin(u) * DRUM_R * 1.035,
                                                  .5), rot=(0, 0, u), bevel=0)
    # The dome, the puffed mantlet, the long barrel sagging, the fabric muzzle brake.
    dome = a.part('Dome', 'Team')
    k.lathe(dome, [(1.0, 0), (1.05, .12), (.95, .45), (.7, .68), (.3, .78), (0, .8)], loc=DOME, seg=16)
    fab = a.part('Fabric', 'Armor')
    fab.sphere((.42, .35, .32), loc=(0, DOME[1] - .95, DZ + .38), seg=12, rings=7)
    pts = []
    for i in range(7):
        f = i / 6
        pts.append((0, DOME[1] - 1.1 - f * 1.75, DZ + .38 - .15 * f * f))     # the sag grows towards the muzzle
    fab.tube(pts, .12, seg=10)
    k.lathe(fab, [(.12, 0), (.19, .04), (.19, .3), (.12, .34), (0, .34)], loc=pts[-1], rot=(R90 + .09, 0, 0), seg=10)
    # Painted-on hatches and vision blocks, the painted Team band, a repair patch.
    paint = a.part('Painted_hatches', 'Charred')
    for (x, y, r) in ((.4, .5, .3), (-.35, .65, .25)):
        paint.cyl(r, .01, loc=(x, DOME[1] + y - .15, DZ + .8 - .1 * (abs(x) + abs(y))), seg=12, bevel=0)
    for i in range(4):
        u = math.radians(-60 + i * 40)
        paint.box((.16, .01, .08), loc=(math.sin(u) * .96, DOME[1] - math.cos(u) * .96, DZ + .35), rot=(0, 0, u),
                  bevel=0)
    a.part('Team_band', 'Team').cyl(DRUM_R * 1.045, .14, loc=(0, .15, .62), seg=18, bevel=0)
    a.part('Patches', 'Canvas').box((.3, .02, .25), loc=(.75, .15 - DRUM_R * .8, .45), rot=(0, 0, .65), bevel=0)
    K.whip_antenna(a.part('Antenna', 'Steel'), (.55, DOME[1] + .55, DZ + .55), h=.9, r=.018, lean=.12)


def _rigging(a, rng):
    """Tethers from the dome, the barrel and the drum to stakes; the blower with its hose; the folded bag."""
    teth = a.part('Tethers', 'Undercarriage')
    stakes = a.part('Stakes', 'Steel')
    anchors = [((.75, DOME[1] - .3, DZ + .55), (2.05, -1.4)), ((-.75, DOME[1] - .3, DZ + .55), (-2.05, -1.4)),
               ((.6, DOME[1] + .5, DZ + .5), (2.0, 1.9)), ((-.6, DOME[1] + .5, DZ + .5), (-2.0, 1.9)),
               ((0, DOME[1] - 2.0, DZ + .3), (.6, -2.35)), ((0, DOME[1] - 2.0, DZ + .3), (-.6, -2.35))]
    for (p, (sx, sy)) in anchors:
        teth.tube([p, (sx, sy, .08)], .01, seg=3)
        stakes.box((.03, .03, .3), loc=(sx, sy, .1), rot=(.3 * math.copysign(1, sy), 0, 0), bevel=0)
    # The petrol blower on the ground at the back right, its fan guard, the hose into the drum.
    bx, by = -1.75, 1.35
    k.block(a.part('Blower', 'Armor'), (.45, .35, .35), loc=(bx, by, .2), chamfer=.04)
    k.ring(a.part('Blower_guard', 'Steel'), [(.13, 0), (.16, 0), (.16, .04), (.13, .04)], loc=(bx, by - .19, .22),
           rot=(R90, 0, 0), seg=12)
    a.part('Blower_frame', 'Steel').tube([(bx - .25, by - .2, .02), (bx - .25, by - .2, .45), (bx + .25, by - .2, .45),
                                          (bx + .25, by - .2, .02)], .015, seg=4)
    a.part('Hose', 'Rubber').tube([(bx + .15, by - .1, .2), (-1.2, 1.0, .1), (-.9, .55, .3)], .06, seg=8)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (bx + .45, by + .3, 0), rot=(0, 0, .5))
    k.block(a.part('Transport_bag', 'Canvas'), (.9, .5, .3), loc=(1.75, -1.85, .15), rot=(0, 0, .3), chamfer=.1,
            taper=(.9, .8))


def inflatable_decoy(a):
    """The inflatable decoy: see the module docstring."""
    rng = random.Random(3641)
    _ground(a, rng)
    _turret(a)
    _rigging(a, rng)
    k.clean(a)


BUILDERS = {
    'inflatable_decoy': (inflatable_decoy, dict(ao_distance=.5, grime_height=.4)),
}
