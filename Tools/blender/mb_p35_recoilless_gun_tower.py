"""Prompt 35 wave 10 (lane B): the recoilless gun post rebuilt from scratch (spec:
Tools/blender/specs/recoilless_gun_tower.json).

An SPG-9 Kopyo 73 mm emplacement (the def's modelSize 4.2 x 4.2 x 3.0 m, spg9_73mm): a dug earth pad, a horseshoe of
sandbags open at the rear with a timber revetment inside and a back-blast trench behind (scorched), the gun on its
tripod (three splayed legs with spades, the traversing head `Turret`): the cradle, the 2.1 m smooth tube with its
venturi breech and blast cone, the PGO-9 sight on its bracket, the firing grip, the split gun shield; rounds in their
cases and loose, ammunition boxes, a stake fence with tape at the rear, the radio mast with its flag.

Runtime nodes kept at their old places: `Turret` (0, -0.1, 1.05), `Main_cannon`, `Muzzle_brake`, `Muzzle_main` (the
tube's mouth 2.04 m ahead of the pivot). Built only from frontier_kit / mb_kit27 primitives, mb_kit35 and lane B's
helpers; no other model's builder. Metres, +Z up, -Y front, +X left. Under 6,000 triangles.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
G = .12


def recoilless_gun_tower(a):
    P.earth_pad(a, [(-2.05, -1.9), (-.6, -2.08), (1.2, -2.0), (2.05, -1.4), (2.0, .9), (1.6, 2.0), (-.4, 2.08),
                    (-1.9, 1.7), (-2.08, .2)], G, bottom=False)
    ring = [(math.cos(u) * 1.7, math.sin(u) * 1.7 - .1, G) for u in (math.radians(d) for d in range(118, 425, 16))]
    P.sandbag_run(a, ring, courses=3, bag=(.55, .3, .15), seed=7, lean=True)
    rev = a.part('Revetment', 'Wood')
    for u in (math.radians(d) for d in range(160, 390, 38)):
        rev.box((.1, .1, .5), loc=(math.cos(u) * 1.45, math.sin(u) * 1.45 - .1, G + .25), rot=(0, 0, u), bevel=0)
    # The back-blast trench behind the gun, scorched.
    a.part('Trench', 'Charred').box((1.0, 1.3, .01), loc=(0, 1.45, G + .006), bevel=0)
    a.part('Scorch', 'Charred').box((1.4, .5, .006), loc=(0, 1.72, G + .004), rot=(0, 0, .1), bevel=0)
    fl = a.part('Floor', 'Wood')
    for i in range(6):
        fl.box((2.2, .18, .04), loc=(0, -1.0 + i * .3, G + .02), rot=(0, 0, .015 * (i % 3 - 1)), bevel=0)
    # The tripod: three splayed legs with spades, the head.
    tri = a.part('Tripod', 'Armor')
    for u in (R90 + .0, R90 + 2.3, R90 - 2.3):
        foot = (math.cos(u) * .85, -.1 - math.sin(u) * .85, G + .03)
        tri.limb((0, -.1, .8), foot, .05, .05, bevel=0)
        a.part('Spades', 'Steel').box((.16, .04, .14), loc=(foot[0], foot[1], G + .05), rot=(0, 0, u), bevel=0)
    t = a.pivot('Turret', (0, -.1, 1.05))
    k.lathe(a.part('Turret_head', 'Armor', t), [(.1, -.2), (.12, -.15), (.12, .02), (0, .05)], seg=8)
    cr = a.part('Cradle', 'Armor', t)
    k.block(cr, (.18, .7, .14), loc=(0, -.45, .3), chamfer=.02)
    for s in (-1, 1):
        cr.box((.03, .1, .3), loc=(s * .1, -.45, .15), bevel=0)
    # The tube: venturi breech at the rear, the barrel, the mouth ring; elevated a little to the old muzzle.
    e = math.atan2(.45 - .34, 2.04 + .35)
    bore = P.Elev((0, .35, .34), e)
    L = math.hypot(2.04 + .35, .45 - .34)
    k.lathe(a.part('Main_cannon', 'Team', t), [(.06, 0), (.075, .05), (.075, .45), (.055, .55), (.05, L - .12),
                                               (.06, L - .08), (0, L - .08)], loc=bore.base, rot=bore.lathe_rot,
            seg=10, worn=(2,))
    k.lathe(a.part('Muzzle_brake', 'Undercarriage', t), [(.06, L - .1), (.068, L - .08), (.068, L), (.045, L),
                                                         (.045, L - .04), (0, L - .04)], loc=bore.base,
            rot=bore.lathe_rot, seg=10)
    k.lathe(a.part('Venturi', 'Steel', t), [(.0, -.02), (.09, 0), (.13, -.22), (.12, -.26), (.07, -.06), (0, -.05)],
            loc=bore.base, rot=bore.lathe_rot, seg=10)
    for f in (.32, .62):
        a.part('Tube_bands', 'Steel', t).cyl(.064, .05, loc=bore.at(L * f), rot=bore.lathe_rot, seg=10, bevel=0)
    a.pivot('Muzzle_main', (0, -2.04, .45), t)
    # The PGO-9 sight on its bracket on the left, the grip and trigger, the split shield.
    a.part('Sight_bracket', 'Steel', t).box((.18, .04, .04), loc=(.1, -.25, .38), bevel=0)
    k.block(a.part('Sight', 'Armor', t), (.08, .26, .12), loc=(.2, -.25, .42), chamfer=.01)
    a.part('Glass', 'Glass', t).box((.05, .02, .05), loc=(.2, .11 - .25, .44), bevel=0)
    a.part('Grip', 'Undercarriage', t).box((.05, .08, .18), loc=(-.1, -.05, .22), rot=(.3, 0, 0), bevel=0)
    sh = a.part('Gun_shield', 'Armor', t)
    for s in (-1, 1):
        k.extrude(sh, [(-.32, -.25), (.32, -.25), (.28, .25), (-.28, .25)], .02, loc=(s * .38, -.85, .35),
                  rot=(R90 - .12, 0, s * .2), axis='Z', chamfer=.006)
    a.part('Team_band', 'Team', t).box((.02, .3, .1), loc=(.56, -.9, .45), rot=(0, 0, .2), bevel=0)
    # Rounds: cases, loose PG-9 rounds on a tray, ammunition boxes; the stake fence with tape; mast and flag.
    for i, (x, y, r) in enumerate(((-1.0, .55, .4), (-.9, .9, .3))):
        k.block(a.part('Ammo_cases', 'Crate'), (.35, 1.1, .25), loc=(x, y, G + .125), rot=(0, 0, r), chamfer=.02)
        a.part('Kit_latches', 'Steel').box((.37, .05, .05), loc=(x, y, G + .24), rot=(0, 0, r), bevel=0)
    tray = a.part('Round_tray', 'Wood')
    tray.box((.5, .8, .05), loc=(.95, .5, G + .25), rot=(0, 0, -.3), bevel=0)
    for i in range(3):
        x, y = .95 - .14 + i * .14, .5
        k.lathe(a.part('Rounds', 'Gilded'), [(0, -.4), (.04, -.36), (.04, .1), (.035, .2), (0, .32)],
                loc=(x + i * .02, y - i * .04, G + .32), rot=(R90, 0, -.3), seg=6)
    P.ammo_box(a, (1.05, -.2, G), rot=(0, 0, .3))
    for (x, y) in ((-1.85, 1.25), (-1.0, 1.95), (1.0, 1.95), (1.85, 1.25)):
        a.part('Stakes', 'Wood').cyl(.03, .9, loc=(x, y, G + .45), seg=5, bevel=0)
    a.part('Tape', 'Hazard').tube([(-1.85, 1.25, G + .75), (-1.0, 1.95, G + .72), (1.0, 1.95, G + .74),
                                   (1.85, 1.25, G + .73)], .012, seg=3, caps=False)
    a.part('Flag_pole', 'Steel').cyl(.025, 2.8, loc=(-1.75, -1.1, G + 1.4), seg=6, bevel=0)
    a.part('Flag', 'Team').box((.03, .55, .35), loc=(-1.75, -.83, G + 2.6), rot=(0, 0, .15), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (1.6, -1.0, G + .45), h=1.9, r=.02)
    k.block(a.part('Radio_box', 'Armor'), (.32, .22, .28), loc=(1.55, -.75, G + .45 + .14), chamfer=.02)
    # Tier 3: stones and clods on the pad, spent caps and the sandbag ties.
    rk = a.part('Stones', 'Rock')
    for i in range(34):
        u = i * 2.39996
        r = 1.95 + .1 * math.sin(i * 1.7)
        sz = .07 + (i % 4) * .03
        rk.box((sz, sz * 1.3, sz * .6), loc=(math.cos(u) * r * .97, math.sin(u) * r * .95, G + sz * .2),
               rot=(i * .7, i * .3, i * 1.3), bevel=0)
    caps = a.part('Spent_caps', 'Steel')
    for i in range(8):
        caps.cyl(.04, .05, loc=(-.4 + (i % 4) * .25, 1.05 + (i // 4) * .2, G + .03), seg=6, bevel=0)
    ties = a.part('Bag_ties', 'Canvas')
    for u in (math.radians(d) for d in range(126, 420, 21)):
        ties.box((.06, .06, .05), loc=(math.cos(u) * 1.72, math.sin(u) * 1.72 - .1, G + .45), rot=(0, 0, u), bevel=0)
    for i in range(6):
        u = i * TAU / 6
        K.dust(a, (math.cos(u) * 1.8, math.sin(u) * 1.8, G), radius=1.0, k=.3)
    K.soot(a, (0, 1.3, G + .3), radius=1.2, k=.4)
    k.clean(a)


BUILDERS = {'recoilless_gun_tower': (recoilless_gun_tower, dict(ao_distance=.5, grime_height=.3, ao_strength=.6))}
