"""Prompt 35 wave 7 (lane C): the minefield and its scatter branch rebuilt from scratch (specs:
Tools/blender/specs/minefield.json, minefield_b.json).

Flat props on the def's 5 x 5 m footprint (passable, untargetable), drawn to read from the battle camera:

- minefield (mines_at): a patch of disturbed earth with spoil mounds and wheel ruts, TM-62M anti-tank mines
  half-buried in their spoil rings (two exposed with the MVCh-62 pressure fuze and the carry handle), the perimeter
  marked with pickets, warning tape and red triangle signs on stakes.
- minefield_b (the orphan "scatter mines" branch): the same earth patch and perimeter, so it reads as the field
  upgraded, with PTM-3 bar mines scattered over it and the six-tube scatter dispenser module on its skid in the
  rear-left corner (tubes angled up and out, the control box and the cable reel).

The mines are a larger-than-life 1.5 x so a 28 px-per-metre camera still shows them (the old files did the same).
No runtime nodes (the old files had none). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TAU = math.tau
HALF = 2.4


def _patch(a, seed=0, rng=None):
    """The earth patch, its trampled spots and ruts, stones and tufts, the marked perimeter with signs. With `rng`
    (wave 12's minefield_a) the stones and tufts are scattered at random instead of on the low-discrepancy rows."""
    k.extrude(a.part('Ground_patch', 'Sandstone'), C.octagon(4.75, 4.75, .55), .05, loc=(0, 0, .025), axis='Z',
              corner=.05, taper=(.97, .97), caps=(False, True))
    spots = a.part('Mine_earth', 'Dirt')
    for i, (x, y, w, d, r) in enumerate(((-1.3, 1.6, .9, .5, .4), (1.4, -1.5, .8, .45, -.3), (.2, .3, 1.1, .35, .9),
                                         (-1.6, -1.2, .7, .4, 1.4), (1.7, 1.2, .6, .4, 2.0), (-.4, -1.9, .8, .3, .2))):
        spots.box((w, d, .012), loc=(x, y, .052 + i * .001), rot=(0, 0, r + seed), bevel=0)
    rut = a.part('Ruts', 'Dirt')
    for s_ in (-1, 1):
        rut.box((.3, 4.5, .02), loc=(s_ * .9 + .3, 0, .058), rot=(0, 0, .12), bevel=0)
        for j in range(6):
            rut.box((.32, .06, .03), loc=(s_ * .9 + .3 + .12 * (j - 2.5) * .1, -2.0 + j * .8, .065), rot=(0, 0, .12),
                    bevel=0)
    rk = a.part('Stones', 'Rock')
    for i in range(30):
        x = -2.15 + 4.3 * ((i * .618 + seed * .17) % 1.0)
        y = -2.15 + 4.3 * ((i * .382 + seed * .31) % 1.0)
        if rng:
            x, y = rng.uniform(-2.15, 2.15), rng.uniform(-2.15, 2.15)
        sz = .06 + (i % 4) * .03
        rk.box((sz, sz * 1.3, sz * .6), loc=(x, y, .05 + sz * .2), rot=(i * .7, i * .3, i * 1.3), bevel=0)
    tf = a.part('Tufts', 'FoliageDark')
    for i in range(16):
        x = -2.2 + 4.4 * ((i * .7548 + seed * .23) % 1.0)
        y = -2.2 + 4.4 * ((i * .5698 + seed * .41) % 1.0)
        if rng:
            x, y = rng.uniform(-2.2, 2.2), rng.uniform(-2.2, 2.2)
        tf.cyl(.09, .14 + (i % 3) * .04, loc=(x, y, .12), rot=(0, 0, i * .7), seg=4, r2=.01, bevel=0)
    # The perimeter: pickets every 0.6 m, two strands of warning tape, red triangle signs on tall stakes.
    pk = a.part('Pickets', 'Wood')
    tape = a.part('Tape', 'Hazard')
    pts = []
    n = 8
    for side in range(4):
        for j in range(n):
            f = -HALF + j * (2 * HALF / n)
            pts.append([(f, -HALF), (HALF, f), (-f, HALF), (-HALF, -f)][side])
    for i, (x, y) in enumerate(pts):
        pk.cyl(.028, .75 + .05 * (i % 2), loc=(x, y, .38), seg=5, bevel=0)
        x2, y2 = pts[(i + 1) % len(pts)]
        L = math.hypot(x2 - x, y2 - y)
        for z in (.66, .36):
            tape.box((.012, L, .045), loc=((x + x2) / 2, (y + y2) / 2, z - .03 * (i % 2)),
                     rot=(0, 0, math.atan2(-(x2 - x), y2 - y)), bevel=0)
    sg = a.part('Signs', 'BarrelRed')
    back = a.part('Sign_backs', 'Team')
    stake = a.part('Sign_stakes', 'Steel')
    for x, y, yaw in ((-HALF, -HALF, .78), (HALF, -HALF, -.78), (0, -HALF, 0), (HALF, HALF, -2.4), (-HALF, HALF, 2.4),
                      (HALF, 0, -R90), (-HALF, 0, R90)):
        stake.cyl(.025, 1.05, loc=(x, y, .52), seg=5, bevel=0)
        tri = [(-.2, .7), (.2, .7), (0, 1.05)]
        k.extrude(sg, tri, .02, loc=(x, y, 0), rot=(0, 0, yaw), axis='Y', chamfer=0)
        k.extrude(back, tri, .01, loc=(x + math.sin(yaw) * .016, y + math.cos(yaw) * .016, 0), rot=(0, 0, yaw),
                  axis='Y', chamfer=0)
        a.part('Sign_marks', 'PlasterWhite').box((.05, .03, .14), loc=(x, y, .84), rot=(0, 0, yaw), bevel=0)
    for i in range(5):
        u = i * TAU / 5 + seed
        K.dust(a, (math.cos(u) * 1.6, math.sin(u) * 1.6, .05), radius=1.4, k=.35)


def _tm62(a, loc, exposed=False, tilt=(0, 0)):
    """A TM-62M: the drum body with its rim, the fuze well, the MVCh-62 fuze and the carry handle; buried ones sit in
    a spoil ring with only the top showing."""
    x, y, z = loc
    r = .3
    sink = 0 if exposed else .09
    k.lathe(a.part('Mine_bodies', 'Armor'), [(r * .2, 0), (r, .01), (r * 1.03, .05), (r * 1.03, .1), (r, .15),
                                            (r * .35, .17), (0, .17)], loc=(x, y, z - sink), rot=(tilt[0], tilt[1], 0),
            seg=14, worn=(2, 3, 4))
    k.lathe(a.part('Mine_fuzes', 'Steel'), [(.09, 0), (.09, .04), (.06, .06), (.06, .09), (0, .1)],
            loc=(x, y, z - sink + .17), rot=(tilt[0], tilt[1], 0), seg=10, worn=(1,))
    a.part('Mine_plates', 'Undercarriage').cyl(.04, .015, loc=(x, y, z - sink + .275), seg=8, bevel=0)
    if exposed:
        K.handle(a.part('Mine_plates', 'Undercarriage'), (x - .1, y + r * 1.03, z + .08), (x + .1, y + r * 1.03, z + .08),
                 (0, 1, 0), h=.05, r=.012)
    else:
        k.lathe(a.part('Mine_earth', 'Dirt'), [(r * 1.0, .1), (r * 1.25, .07), (r * 1.7, .02), (r * 1.9, 0)],
                loc=(x, y, z - .04), seg=12, caps=(False, False), worn=(1,))


def minefield(a, detail=False):
    """The minefield (see the module docstring)."""
    _patch(a)
    for i, (x, y) in enumerate(((-1.4, -1.5), (.2, -1.7), (1.5, -.6), (-.6, -.2), (.9, .9), (-1.6, 1.0), (.0, 1.8))):
        _tm62(a, (x, y, .05), exposed=i in (2, 5), tilt=(.08 if i == 2 else 0, -.1 if i == 5 else 0))
    k.clean(a)


def minefield_b(a, detail=False):
    """The scatter-mine field (see the module docstring)."""
    _patch(a, seed=1)
    # PTM-3 bar mines strewn over the patch (12), each a long box body with its end caps.
    for i in range(12):
        x = -1.9 + 3.6 * ((i * .618 + .2) % 1.0)
        y = -1.9 + 3.6 * ((i * .382 + .5) % 1.0)
        if x > .7 and y > .6:
            x -= 1.7                                   # keep the dispenser corner clear
        yaw = i * 1.3
        roll = (i % 3 - 1) * .12
        k.block(a.part('Mine_bodies', 'Armor'), (.18, .5, .14), loc=(x, y, .12), rot=(roll, 0, yaw), chamfer=.03)
        c, s = math.cos(yaw), math.sin(yaw)
        for d in (-1, 1):
            a.part('Mine_caps', 'Undercarriage').box((.19, .04, .15), loc=(x - s * d * .26, y + c * d * .26, .12),
                                                     rot=(roll, 0, yaw), bevel=0)
    # The six-tube dispenser module on its skid in the rear-left corner, the control box and the cable reel.
    sk = a.part('Skid', 'Steel')
    for s in (-1, 1):
        sk.box((.08, 1.5, .1), loc=(1.45 + s * .45, 1.5, .1), bevel=0)
    for y in (.95, 2.05):
        sk.box((1.0, .08, .08), loc=(1.45, y, .19), bevel=0)
    dp = a.part('Dispenser', 'Team')
    K.chamfer_box(dp, (.9, 1.1, .32), loc=(1.45, 1.5, .39), c=.04)
    tb = a.part('Dispenser_tubes', 'Armor')
    for i in range(6):
        col, row = i % 3, i // 3
        u = (col - 1) * .45
        k.lathe(tb, [(.11, 0), (.11, .55), (.09, .58), (0, .58)], loc=(1.45 + (col - 1) * .28, 1.25 + row * .5, .55),
                rot=(-.5 + row * .2, u, 0), seg=10, worn=(1, 2))
    a.part('Tube_mouths', 'Undercarriage').box((.7, .9, .02), loc=(1.45, 1.5, .555), bevel=0)
    k.block(a.part('Control_box', 'Armor'), (.3, .2, .35), loc=(.75, 1.0, .225), chamfer=.02)
    C.cable_reel(a, (.75, 1.9, .3), r=.2, w=.25, axis='X')
    a.part('Tow_cable', 'Rubber').tube([(.75, 1.0, .4), (.4, .6, .08), (-.6, .2, .08)], .02, seg=4)
    k.clean(a)


BUILDERS = {
    'minefield': (minefield, dict(ao_distance=.3, grime_height=.2)),
    'minefield_b': (minefield_b, dict(ao_distance=.3, grime_height=.2)),
}
