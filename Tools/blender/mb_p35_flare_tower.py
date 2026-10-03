"""Prompt 35 wave 10 (lane B): the illumination-flare tower rebuilt to prompt 35's standard (spec:
Tools/blender/specs/flare_tower.json), keeping what fix L8 got right (DECISIONS "Sửa lỗi tổng hợp L8"): the
four-legged braced steel tower on concrete footings, the plank deck with a sandbag parapet and the ladder, the canvas
sun roof on posts, ready-use crates, the aerial, and the eight-tube flare-mortar rack turning on its yoke.

Prompt 35 adds what the scan asked for (tiers 0.18 of the tower gold, few brightness regions): angle-iron legs with
gussets and base plates bolted to the footings, X-bracing on every face in two bays, the deck frame with its Team band
and every plank its own board, a lean two-course parapet with an opening for the ladder, the ladder's safety cage,
roof ropes to pegs, the rack's cradle, elevating arc and hand wheel, every tube with its muzzle ring, the flare
rounds in open crates, a signal lamp, a field telephone, fire buckets.

Runtime nodes kept at their old places: `Turret` (0, 0, 3.2), `Muzzle_main` (0, -0.24, 1.09 on it). Built only from
frontier_kit / mb_kit27 primitives, mb_kit35 and lane B's helpers; no other model's builder. Metres, +Z up, -Y
front, +X left. Under 6,000 triangles.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
H0, H1, HW0, HW1 = .25, 2.9, 1.45, 1.15


def _half(z):
    return HW0 + (HW1 - HW0) * (z - H0) / (H1 - H0)


def _legs(a):
    feet = a.part('Footing', 'Concrete')
    legs = a.part('Legs', 'Armor')
    bolts = a.part('Kit_bolts', 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            k.block(feet, (.6, .6, .25), loc=(sx * HW0, sy * HW0, 0), chamfer=.04, ends=(False, True))
            a.part('Base_plates', 'Steel').box((.34, .34, .03), loc=(sx * HW0, sy * HW0, H0 + .015), bevel=0)
            for dx in (-.12, .12):
                for dy in (-.12, .12):
                    bolts.cyl(.025, .05, loc=(sx * HW0 + dx, sy * HW0 + dy, H0 + .04), seg=5, bevel=0)
            # The angle-iron leg: two flanges.
            p0, p1 = (sx * HW0, sy * HW0, H0), (sx * HW1, sy * HW1, H1)
            legs.limb((p0[0], p0[1] - sy * .05, p0[2]), (p1[0], p1[1] - sy * .05, p1[2]), .16, .025, bevel=0)
            legs.limb((p0[0] - sx * .05, p0[1], p0[2]), (p1[0] - sx * .05, p1[1], p1[2]), .025, .16, bevel=0)
    br = a.part('Braces', 'Steel')
    gus = a.part('Gussets', 'Armor')
    for z0, z1 in ((H0 + .15, 1.6), (1.6, H1 - .12)):
        f0, f1 = _half(z0), _half(z1)
        for s in (-1, 1):
            for d in (-1, 1):
                br.tube([(-f0 * d, s * f0, z0), (f1 * d, s * f1, z1)], .03, seg=4)
                br.tube([(s * f0, -f0 * d, z0), (s * f1, f1 * d, z1)], .03, seg=4)
        for s in (-1, 1):
            br.limb((-f1, s * f1, z1), (f1, s * f1, z1), .07, .07, bevel=0)
            br.limb((s * f1, -f1, z1), (s * f1, f1, z1), .07, .07, bevel=0)
            for d in (-1, 1):
                gus.box((.16, .02, .16), loc=(d * f1 * .93, s * (f1 + .02), z1), rot=(0, .78, 0), bevel=0)


def _deck(a):
    z = H1
    k.block(a.part('Deck_frame', 'Armor'), (3.0, 3.0, .14), loc=(0, 0, z), chamfer=.03)
    band = a.part('Team_band', 'Team')
    for s in (-1, 1):
        band.box((3.02, .02, .08), loc=(0, s * 1.505, z - .02), bevel=0)
        band.box((.02, 3.02, .08), loc=(s * 1.505, 0, z - .02), bevel=0)
    deck = a.part('Planks', 'Wood')
    for i in range(10):
        deck.box((3.06 - (i % 3) * .04, .27, .05), loc=((i % 2) * .02, -1.37 + i * .305, z + .095), bevel=0)
    nails = a.part('Kit_nails', 'Steel')
    for i in range(10):
        for x in (-1.4, 1.4):
            nails.box((.03, .03, .01), loc=(x, -1.37 + i * .305, z + .12), bevel=0)
    rv = a.part('Kit_rivets', 'Steel')
    for i in range(9):
        for s in (-1, 1):
            rv.box((.04, .02, .04), loc=(-1.3 + i * .325, s * 1.51, z), bevel=0)
            rv.box((.02, .04, .04), loc=(s * 1.51, -1.3 + i * .325, z), bevel=0)
    zb = z + .12
    P.sandbag_run(a, [(-1.35, 1.35, zb), (1.35, 1.35, zb)], courses=2, bag=(.55, .28, .15), seed=1, lean=True)
    for s in (-1, 1):
        P.sandbag_run(a, [(s * 1.35, 1.05, zb), (s * 1.35, -1.05, zb)], courses=2, bag=(.55, .28, .15), seed=2 + s,
                      lean=True)
        P.sandbag_run(a, [(s * 1.35, -1.35, zb), (s * .62, -1.35, zb)], courses=2, bag=(.55, .28, .15), seed=4 + s,
                      lean=True)
    # The ladder up the front opening, its safety cage.
    K.ladder(a.part('Ladders', 'Steel'), (0, -1.75, 0), (0, -1.42, H1 + .9), width=.5, step=.3, r=.022)
    cage = a.part('Ladder_cage', 'Steel')
    for zz in (1.6, 2.2):
        cage.tube([(-.3, -1.55, zz), (-.35, -1.95, zz), (.35, -1.95, zz), (.3, -1.55, zz)], .014, seg=3, caps=False)
    for x in (-.3, .3):
        cage.tube([(x, -1.95, 1.5), (x, -1.95, 2.3)], .012, seg=3, caps=False)
    # The canvas sun roof on four posts, guy ropes to pegs on the deck edge.
    posts = a.part('Roof_posts', 'Wood')
    for sx in (-1, 1):
        for sy in (-1, 1):
            posts.box((.09, .09, 1.62), loc=(sx * 1.3, sy * 1.3, H1 + 1.0), bevel=0)
    k.extrude(a.part('Roof', 'Canvas'), [(-1.55, 0), (1.55, 0), (1.55, .06), (0, .32), (-1.55, .06)], 3.1,
              loc=(0, 0, H1 + 1.78), axis='Y', chamfer=0, corner=.02)
    a.part('Roof_ridge', 'Wood').box((.08, 3.15, .08), loc=(0, 0, H1 + 2.1), bevel=0)
    rope = a.part('Kit_straps', 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            rope.tube([(sx * 1.55, sy * 1.5, H1 + 1.8), (sx * 1.62, sy * 1.62, H1 + .1)], .008, seg=3)


def _rack(a):
    """The eight-tube flare-mortar rack on its yoke (`Turret`), elevated 55 degrees."""
    t = a.pivot('Turret', (0, 0, 3.2))
    k.lathe(a.part('Ring', 'Steel', t), [(.42, 0), (.42, .06), (.3, .09), (.16, .12), (.16, .42)], seg=12, worn=(1,))
    yoke = a.part('Yoke', 'Armor', t)
    for s in (-1, 1):
        k.block(yoke, (.08, .34, .55), loc=(s * .44, 0, .44), chamfer=.02)
        a.part('Trunnions', 'Steel', t).cyl(.07, .08, loc=(s * .5, 0, .62), rot=(0, R90, 0), seg=8, bevel=0)
    yoke.box((.96, .2, .08), loc=(0, 0, .2), bevel=0)
    pitch = math.radians(55)
    c, s = math.cos(pitch), math.sin(pitch)
    base = (0, -.2 + .55 * c, 1.0 - .55 * s)
    k.block(a.part('Turret_launcher', 'Team', t), (.76, .42, .5), loc=base, rot=(R90 - pitch, 0, 0), chamfer=.04,
            ends=(True, True))
    k.block(a.part('Cradle', 'Armor', t), (.8, .2, .12), loc=(0, base[1] + .12, base[2] - .2), rot=(R90 - pitch, 0, 0),
            chamfer=.02)
    for i in range(4):
        for j in range(2):
            x = -.27 + i * .18
            u = -.1 + j * .2
            loc = (x, -.2 + u * s, 1.0 + u * c)
            k.lathe(a.part('Tubes', 'Undercarriage', t), [(.06, -.5), (.065, 0), (.07, .0), (.07, .04), (0, .04)],
                    loc=loc, rot=(R90 - pitch, 0, 0), seg=8)
            k.ring(a.part('Tube_rings', 'Steel', t), [(.07, .02), (.085, .02), (.085, .07), (.07, .07)], loc=loc,
                   rot=(R90 - pitch, 0, 0), seg=8)
    # Elevating arc and hand wheel on the left.
    arc = [(.5, -.3 * math.cos(v), .62 - .3 * math.sin(v)) for v in (0, .4, .8, 1.2)]
    a.part('Elevating_arc', 'Steel', t).tube(arc, .02, seg=4)
    a.part('Hand_wheel', 'Steel', t).torus(.12, .015, loc=(.58, .1, .5), rot=(0, R90, 0), seg=10, ring=3)
    a.pivot('Muzzle_main', (0, -.24, 1.09), t)


def flare_tower(a):
    _legs(a)
    _deck(a)
    _rack(a)
    z = H1 + .12
    # Ready-use crates (one open with rounds), the signal lamp, field phone, buckets, the aerial.
    for x, yaw in ((-1.0, .05), (-.45, -.1)):
        K.crate(a.part('Crates', 'Crate'), a.part('Kit_straps', 'Steel'), (.48, .34, .3), (x, .85, z), rot=(0, 0, yaw),
                bands=1)
    k.block(a.part('Crates', 'Crate'), (.5, .36, .16), loc=(.75, .85, z + .08), chamfer=0)
    for i in range(6):
        k.lathe(a.part('Flare_rounds', 'BarrelRed'), [(.045, 0), (.045, .2), (0, .26)],
                loc=(.6 + (i % 3) * .15, .78 + (i // 3) * .15, z + .16), seg=6)
    K.whip_antenna(a.part('Antenna', 'Steel'), (-1.25, -1.2, z), h=1.6, r=.025)
    k.block(a.part('Signal_lamp', 'Armor'), (.22, .3, .22), loc=(1.15, -1.0, z + .5), chamfer=.02)
    a.part('Lamps', 'Lamp').cyl(.08, .02, loc=(1.15, -1.16, z + .5), rot=(R90, 0, 0), seg=10, bevel=0)
    a.part('Lamp_post', 'Steel').cyl(.03, .4, loc=(1.15, -1.0, z + .2), seg=5, bevel=0)
    k.block(a.part('Field_phone', 'Armor'), (.2, .12, .18), loc=(-1.1, .3, z + .55), chamfer=.01)
    for i in range(2):
        k.lathe(a.part('Fire_buckets', 'BarrelRed'), [(.08, 0), (.11, .22), (0, .22)], loc=(.9 + i * .25, -1.62, 1.2),
                seg=8, caps=(True, False))
    a.part('Bucket_rail', 'Steel').box((.7, .04, .04), loc=(1.0, -1.58, 1.42), bevel=0)
    rk = a.part('Stones', 'Rock')
    for i in range(18):
        u = i * 2.39996
        r = 1.0 + (i % 5) * .2
        sz = .07 + (i % 3) * .04
        rk.box((sz, sz * 1.3, sz * .6), loc=(math.cos(u) * r, math.sin(u) * r, sz * .2), rot=(i * .7, 0, i), bevel=0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            K.dust(a, (sx * HW0, sy * HW0, 0), radius=.9, k=.3)
    K.soot(a, (0, -.5, 4.2), radius=.6, k=.35)
    k.clean(a)


BUILDERS = {'flare_tower': (flare_tower, dict(ao_distance=.5, grime_height=.4, ao_strength=.6))}
