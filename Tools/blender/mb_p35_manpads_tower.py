"""Prompt 35 wave 10 (lane B): the MANPADS post rebuilt from scratch (spec: Tools/blender/specs/manpads_tower.json).

A Djigit / Strelets-class twin MANPADS mount in a field pit (the def's modelSize 3.2 x 3.2 x 2.4 m, sam): a dug earth
pad, a ring of sandbags three courses high open at the rear with its entrance steps, duckboards inside, the pedestal
tripod with its levelling feet and the traversing head (`Turret`) carrying the gunner's seat, the reflex sight on its
arm, two launch tubes with their grip stocks and battery units (`Muzzle_missile` / `.001` at the mouths,
`Muzzle_main` between them), the IFF interrogator antenna; spare missile cases, ammunition boxes, the radio with its
whip on the parapet, a camouflage net corner on two poles, a binocular post.

Runtime nodes kept at their old places: `Turret` (0, -0.1, 1.0), `Muzzle_main`, `Muzzle_missile`, `Muzzle_missile.001`.
Built only from frontier_kit / mb_kit27 primitives, mb_kit35 and lane B's helpers; no other model's builder.
Metres, +Z up, -Y front, +X left. Under 6,000 triangles (towers seen in numbers).
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
G = .12


def manpads_tower(a):
    P.earth_pad(a, [(-1.6, -1.55), (-.4, -1.62), (1.0, -1.58), (1.6, -1.2), (1.58, .6), (1.3, 1.6), (-.2, 1.62),
                    (-1.4, 1.5), (-1.62, .2)], G, bottom=False)
    # The sandbag ring, open at the rear (entrance between -125 and -55 degrees of the rear arc).
    ring = [(math.cos(u) * 1.32, math.sin(u) * 1.32, G) for u in
            (math.radians(d) for d in range(110, 440, 22))]
    P.sandbag_run(a, ring, courses=3, bag=(.5, .28, .14), seed=3, lean=True)
    st = a.part('Steps', 'Wood')
    for i in range(2):
        st.box((.7, .25, .06), loc=(.05, 1.25 + i * .22, G + .18 - i * .1), bevel=0)
    fl = a.part('Floor', 'Wood')
    for i in range(7):
        fl.box((1.8, .16, .04), loc=(0, -.9 + i * .28, G + .02), rot=(0, 0, .02 * (i % 3 - 1)), bevel=0)
    # The pedestal tripod with levelling feet, the column.
    ped = a.part('Pedestal', 'Armor')
    for i in range(3):
        u = i * TAU / 3 + R90
        ped.limb((0, -.1, .75), (math.cos(u) * .6, -.1 + math.sin(u) * .6, G + .04), .05, .05, bevel=0)
        a.part('Kit_bolts', 'Steel').cyl(.07, .04, loc=(math.cos(u) * .6, -.1 + math.sin(u) * .6, G + .02), seg=6,
                                        bevel=0)
    k.lathe(ped, [(.07, .7), (.07, .95), (.11, .97), (.11, 1.0)], loc=(0, -.1, 0), seg=8)
    t = a.pivot('Turret', (0, -.1, 1.0))
    k.lathe(a.part('Turret_head', 'Armor', t), [(.12, 0), (.14, .05), (.14, .14), (0, .16)], seg=8)
    # Seat on its arm behind the head, the foot rest.
    a.part('Seat_arm', 'Steel', t).limb((0, .1, .1), (0, .55, -.15), .05, .05, bevel=0)
    k.block(a.part('Seat', 'Canvas', t), (.36, .32, .07), loc=(0, .6, -.13), chamfer=.02)
    k.block(a.part('Seat', 'Canvas', t), (.34, .06, .35), loc=(0, .78, .05), rot=(-.2, 0, 0), chamfer=.02)
    # The yoke carrying the two tubes, elevated to the old muzzles.
    e = math.atan2(.83 - .3, .68 + .7)
    yoke = a.part('Yoke', 'Armor', t)
    for s in (-1, 1):
        yoke.box((.05, .16, .3), loc=(s * .36, 0, .25), bevel=0)
    yoke.box((.77, .1, .06), loc=(0, 0, .12), bevel=0)
    for i, s in enumerate((-1, 1)):
        x = s * .2
        bore = P.Elev((x, .7, .3), e)
        L = math.hypot(.68 + .7, .83 - .3)
        mid = bore.at(L / 2)
        k.lathe(a.part('Tubes', 'Team', t), [(.045, -L / 2), (.06, -L / 2 + .02), (.05, -L / 2 + .2), (.05, L / 2 - .1),
                                             (.058, L / 2 - .08), (.058, L / 2), (.045, L / 2)],
                loc=mid, rot=bore.lathe_rot, seg=10, worn=(4,))
        for f in (.25, .7):
            a.part('Tube_bands', 'Steel', t).cyl(.062, .05, loc=bore.at(L * f), rot=bore.lathe_rot, seg=10, bevel=0)
        # Grip stock, battery coolant unit, the seeker cap ring.
        a.part('Grip_stocks', 'Undercarriage', t).box((.06, .22, .1), loc=bore.at(L * .55, up=-.1), rot=bore.box_rot,
                                                       bevel=0)
        k.lathe(a.part('Battery_units', 'Steel', t), [(.03, -.07), (.035, -.06), (.035, .07), (0, .08)],
                loc=bore.at(L * .62, dx=s * .08, up=-.08), rot=bore.lathe_rot, seg=6)
        a.part('Seeker_caps', 'BarrelRed', t).cyl(.055, .02, loc=bore.at(L + .005), rot=bore.lathe_rot, seg=10,
                                                  bevel=0)
        a.pivot(K.name('Muzzle_missile', i), (x, -.68, .83), t)
    a.pivot('Muzzle_main', (0, -.68, .83), t)
    # The reflex sight on its arm between the tubes, the IFF interrogator antenna.
    a.part('Sight_arm', 'Steel', t).limb((0, .1, .3), (0, -.1, .55), .03, .03, bevel=0)
    k.block(a.part('Sight', 'Armor', t), (.1, .16, .12), loc=(0, -.12, .6), chamfer=.01)
    a.part('Glass', 'Glass', t).box((.08, .02, .08), loc=(0, -.2, .62), bevel=0)
    K.mesh_antenna(a.part('Antennas', 'Steel', t), (.0, .25, .75), w=.3, h=.22, normal=(0, -1, .2), bars=3)
    # Spare missile cases, ammunition boxes, the radio with its whip, the camouflage net corner, binocular post.
    cs = a.part('Missile_cases', 'Crate')
    for i, (x, y, r) in enumerate(((-.85, .55, .3), (-.75, .25, .25))):
        k.block(cs, (.28, 1.25, .22), loc=(x, y, G + .12 + i * .0), rot=(0, 0, r), chamfer=.02)
        a.part('Kit_latches', 'Steel').box((.3, .05, .05), loc=(x, y, G + .24), rot=(0, 0, r), bevel=0)
    P.ammo_box(a, (.8, .5, G), rot=(0, 0, .4))
    P.ammo_box(a, (.85, .1, G), rot=(0, 0, -.2))
    k.block(a.part('Radio_box', 'Armor'), (.32, .22, .28), loc=(1.25, -.85, G + .43 + .14), chamfer=.02)
    K.whip_antenna(a.part('Antennas', 'Steel'), (1.3, -.85, G + .71), h=1.4, r=.02)
    P.camo_net(a, [(-1.45, .6, 1.5), (-1.25, 1.45, 1.4), (-.3, 1.5, 1.2)], .15, G, garnish=4, seed=5)
    a.part('Binocular_post', 'Wood').cyl(.03, .9, loc=(1.0, -1.05, G + .45 + .4), seg=5, bevel=0)
    k.block(a.part('Binoculars', 'Undercarriage'), (.2, .12, .08), loc=(1.0, -1.08, G + 1.34), chamfer=.01)
    a.part('Team_band', 'Team').box((.5, .05, .12), loc=(-1.1, -.95, G + .4), rot=(0, 0, -.75), bevel=0)
    for i in range(6):
        u = i * TAU / 6
        K.dust(a, (math.cos(u) * 1.4, math.sin(u) * 1.4, G), radius=.9, k=.3)
    k.clean(a)


BUILDERS = {'manpads_tower': (manpads_tower, dict(ao_distance=.5, grime_height=.3, ao_strength=.6))}
