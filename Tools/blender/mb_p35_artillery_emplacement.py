"""Prompt 35 wave 9 (lane C): the artillery emplacement rebuilt from scratch (spec:
Tools/blender/specs/artillery_emplacement.json).

A dug-in towed 155 mm howitzer (balance.json howitzer_fixed: the M284 155 mm; unit_refs: a towed 152 / 155 mm
howitzer in a sandbag pit; drawn as an M198-class split-trail gun so it reads as artillery, not as a tank gun): the
round gun pit (the def's 6.5 x 6.5 m tower; the old file's 8.5 x 6.8 m with the barrel's overhang kept) with its
earth revetment, a sandbag course on its crest and the gap at the rear for the prime mover; the firing platform,
the gun on it (`Turret`: the lower carriage on its float, the trails splayed to their spades, the upper carriage,
the cradle with the recuperator and recoil cylinders over the long barrel and its double-baffle muzzle brake, the
equilibrators, the sight and the shield-less layer's seat); the ammunition bay in the revetment's rear arms with
shells on pallets and charge canisters, the aiming stakes and the aiming circle on its tripod, the radio box with
its whip, a camouflage net on poles over the rear, spent charge cases and tools.

`build_pit(a)` / `build_bay(a)` are the site, for the counter-battery and mortar branches (wave 10) to stand in.

Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, and the old file's `Mount_mg` /
`Muzzle_mg` (plain pivots on the trail; the def carries no machine gun). Metres, +Z up, -Y front, +X left. Under
6,000 triangles.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TAU = math.tau
G = .04
R_PIT = 2.75        # the revetment's centre line


def build_pit(a, seed=0):
    """The gun pit: earth revetment, sandbag crest, the firing platform; the rear gap faces +Y."""
    gap = math.radians(38)
    pts = []
    n = 16
    for i in range(n + 1):
        u = R90 + gap + (TAU - 2 * gap) * i / n          # from the gap's left edge round the front
        pts.append((math.cos(u) * R_PIT, math.sin(u) * R_PIT, G))
    k.sweep(a.part('Berm', 'Dirt'), [(.45, 0), (-.45, 0), (-.2, -.62), (.2, -.62)], pts, caps=True, worn=(2,))
    K.sandbag_run(a, [(x * .99, y * .99, G + .62) for x, y, _ in pts], courses=1, bag=(.6, .32, .15),
                  part='Sandbags', seed=seed + 3, lean=True)
    front = [p for p in pts if p[1] < -1.2]
    K.sandbag_run(a, [(x * .99, y * .99, G + .77) for x, y, _ in front], courses=1, bag=(.6, .32, .15),
                  part='Sandbags', seed=seed + 8, lean=True)
    turf = a.part('Berm_turf', 'Grass')
    for i in range(0, n, 3):
        u = R90 + gap + (TAU - 2 * gap) * (i + .5) / n
        turf.box((.7, .35, .03), loc=(math.cos(u) * (R_PIT + .32), math.sin(u) * (R_PIT + .32), G + .3),
                 rot=(-.7, 0, u - R90), bevel=0)
    # The firing platform: timber baulks under the gun's float.
    pl = a.part('Floor', 'Wood')
    for i in range(5):
        pl.box((2.4 + .12 * (i % 2), .3, .1), loc=(0, -.35 + i * .4, G + .05), bevel=0)


def build_bay(a, seed=0):
    """The rear arms' ammunition bay, the aiming stakes and circle, the radio and its whip, the net, clutter."""
    for s in (-1, 1):
        x0 = s * 1.75
        pal = a.part('Pallets', 'Wood')
        k.block(pal, (.9, .7, .1), loc=(x0, 1.85, G + .05), chamfer=0)
        sh = a.part('Shells', 'Fuel')
        fz = a.part('Fuzes', 'Steel')
        for j in range(4):
            for r in range(2):
                k.lathe(sh, [(.075, 0), (.078, .5), (.05, .62), (0, .62)], loc=(x0 - .3 + j * .2, 1.7 + r * .3,
                                                                                G + .1), seg=6, worn=(2,))
                k.lathe(fz, [(.05, 0), (.02, .1), (0, .11)], loc=(x0 - .3 + j * .2, 1.7 + r * .3, G + .72), seg=5)
        bx = a.part('Ammo_boxes', 'Crate')
        for j in range(2):
            k.block(bx, (.5 - .04 * j, .32, .22), loc=(x0 + s * .05, 2.6, G + .11 + j * .22), rot=(0, 0, .1 * j * s),
                    chamfer=.012)
            a.part('Kit_handles', 'Steel').box((.03, .16, .02), loc=(x0 + s * .32, 2.6, G + .16 + j * .22), bevel=0)
        cn = a.part('Charges', 'Canvas')
        for j in range(3):
            cn.cyl(.1, .55, loc=(x0 + s * .25, 2.35 - j * .0, G + .1 + .1 + j * .2), rot=(0, R90, 0), seg=8, bevel=0)
    # Aiming stakes in front, the aiming circle on its tripod, the radio box and its whip at the rear.
    C.pickets(a, [(x, -3.75 - .1 * math.cos(x), G) for x in (-2.4, -1.4, -.4, .6, 1.6, 2.4)], h=.8)
    stk = a.part('Aiming_stakes', 'Hazard')
    for x in (-.25, .25):
        stk.box((.04, .04, 1.4), loc=(x, -4.2, G + .7), bevel=0)
    tri = a.part('Tripod', 'Steel')
    for i in range(3):
        u = i * TAU / 3
        tri.limb((-1.2 + math.cos(u) * .35, 2.95 + math.sin(u) * .35, G), (-1.2, 2.95, G + 1.1), .015, .015, bevel=0)
    k.block(a.part('Sight', 'Armor'), (.18, .18, .14), loc=(-1.2, 2.95, G + 1.17), chamfer=.02)
    k.block(a.part('Radio', 'Armor'), (.45, .3, .38), loc=(1.25, 2.85, G + .19), chamfer=.03)
    K.whip_antenna(a.part('Antennas', 'Steel'), (1.4, 2.85, G + .38), h=2.85, r=.016)
    a.part('Kit_cables', 'Undercarriage').tube([(1.1, 2.8, G + .2), (.6, 1.6, G + .03), (.1, .8, G + .2)], .012,
                                               seg=4)
    K.camo_net(a, [(-2.2, 3.0, 1.5), (2.2, 3.0, 1.5), (2.0, 1.9, 1.7), (-2.0, 1.9, 1.7)], .2, G, part='Camo_net',
               garnish=8, seed=seed + 1)
    C.casings(a, (0, 1.2), 1.4, 7, r=.08, length=(.3, .45), seed=seed + 7, z=G, part='Charge_cases', mat='Gilded')
    C.entrenching_tools(a, (2.2, -1.2, G), yaw=R90, lean=.45)
    C.helmets(a, [(-1.9, -1.0, G), (1.6, .7, G)])
    a.part('Extinguisher', 'BarrelRed').cyl(.07, .45, loc=(-2.0, 1.0, G + .225), seg=8, bevel=0)
    K.dust(a, (0, 0, G), radius=3.0, k=.14)


def _gun(a):
    """The M198-class howitzer on its float (`Turret`): carriage, trails, cradle, barrel, brake, sight."""
    t = a.pivot('Turret', (0, .6, G + .12))
    # The float (firing base) and the lower carriage.
    k.lathe(a.part('Gun_carriage', 'Team', t), [(.62, 0), (.62, .06), (.4, .14), (0, .15)], seg=12, worn=(1,))
    lc = a.part('Gun_carriage', 'Team', t)
    C.slab_loft(lc, C.octagon(1.0, 1.1, .2, y0=0), C.octagon(.7, .8, .15, y0=-.05), .15, .55)
    # The split trails splayed to their spades, the hand-spikes, the wheels raised on their arms.
    for s in (-1, 1):
        u = s * .42
        end = (math.sin(u) * 2.85, math.cos(u) * 2.85 + .2)
        tr = a.part('Gun_trails', 'Team', t)
        tr.limb((s * .3, .35, .35), (end[0], end[1], .12), .11, .07, bevel=0)
        k.block(a.part('Gun_spades', 'Steel', t), (.55, .1, .4), loc=(end[0], end[1] + .1, -.1), rot=(0, 0, -u),
                chamfer=.02)
        a.part('Gun_steel', 'Steel', t).limb((end[0] - s * .1, end[1] - .2, .25), (end[0] - s * .1, end[1] - .2, .7),
                                             .02, .02, bevel=0)
        C.plain_wheel(a, (s * 1.05, .6, .58), .5, .3, s, seg=12, parent=t)
        a.part('Gun_steel', 'Steel', t).limb((s * .45, .45, .45), (s * .9, .6, .58), .06, .06, bevel=0)
    # The upper carriage, the cradle, the recuperator and recoil cylinders, the equilibrators.
    uc = a.part('Gun_armor', 'Armor', t)
    for s in (-1, 1):
        k.extrude(uc, [(-.5, 0), (.55, 0), (.35, .75), (-.15, .85)], .08, loc=(s * .36, 0, .55), axis='X',
                  chamfer=.015, corner=.02)
    pitch = math.radians(12)
    tz = 1.35
    a.part('Gun_steel', 'Steel', t).cyl(.09, .9, loc=(0, .05, tz), rot=(0, R90, 0), seg=8, bevel=0)
    rot = (R90 - pitch, 0, 0)
    d = (0, -math.cos(pitch), math.sin(pitch))

    def at(f, up=0.0):
        return (0, .05 + d[1] * f - math.sin(pitch) * up * 0, tz + d[2] * f + math.cos(pitch) * up)
    cr = a.part('Cradle', 'Armor', t)
    k.lathe(cr, [(.2, -.6), (.22, -.55), (.22, 1.5), (.18, 1.6)], loc=at(0), rot=rot, seg=10, worn=(1, 2))
    rc = a.part('Recoil_cylinders', 'Steel', t)
    for x, up in ((-.13, .25), (.13, .25), (0, -.24)):
        rc.cyl(.07, 2.0, loc=(x,) + at(.6, up)[1:], rot=rot, seg=8, bevel=0)
    eq = a.part('Equilibrators', 'Steel', t)
    for s in (-1, 1):
        eq.limb((s * .42, -.2, .7), (s * .32, -.75, tz + .05), .06, .05, bevel=0)
    # The breech, the long barrel and the double-baffle muzzle brake.
    k.block(a.part('Breech', 'Steel', t), (.32, .45, .32), loc=(0, .05 - d[1] * .55, tz - .16 - d[2] * .55),
            rot=(-pitch, 0, 0), chamfer=.03)
    L = 4.5
    k.lathe(a.part('Main_cannon', 'Steel', t), [(.12, 0), (.12, .6), (.09, .7), (.075, L), (0, L)], loc=at(.9),
            rot=rot, seg=12, worn=(1,))
    tip = at(.9 + L)
    bp = a.part('Muzzle_brake', 'Undercarriage', t)
    for f in (-.12, -.42):
        k.lathe(bp, [(.08, -.1), (.16, -.08), (.16, .08), (.08, .1)], loc=(0, tip[1] - d[1] * f, tip[2] - d[2] * f),
                rot=rot, seg=10, worn=(1, 2))
    bp.cyl(.085, .5, loc=(0, tip[1] + d[1] * .27 * -1, tip[2] - d[2] * .27), rot=rot, seg=10, bevel=0)
    a.pivot('Muzzle_main', (0, tip[1] - .04, tip[2] + .01), t)
    # The sight on the left, the layer's seat and handwheels, the rammer tray, the old file's MG pivots.
    sg = a.part('Gun_sight', 'Armor', t)
    k.block(sg, (.12, .3, .22), loc=(.42, -.2, tz + .25), chamfer=.02)
    a.part('Glass', 'Glass', t).box((.08, .01, .08), loc=(.42, -.36, tz + .38), bevel=0)
    hw = a.part('Handwheels', 'Steel', t)
    for s in (-1, 1):
        k.ring(hw, [(.13, -.015), (.15, -.015), (.15, .015), (.13, .015)], loc=(s * .56, .05, .95),
               rot=(0, R90, 0), seg=10)
    a.part('Gun_seat', 'Rubber', t).box((.25, .25, .06), loc=(.6, .45, .9), bevel=0)
    a.part('Gun_steel', 'Steel', t).box((.25, .9, .04), loc=(0, 1.0, .95), rot=(.25, 0, 0), bevel=0)
    m = a.pivot('Mount_mg', (-.85, 1.5, .4), t)
    a.pivot('Muzzle_mg', (0, -.6, .1), m)


def artillery_emplacement(a, detail=False):
    """The artillery emplacement: see the module docstring."""
    build_pit(a)
    build_bay(a)
    _gun(a)
    k.clean(a)


BUILDERS = {
    'artillery_emplacement': (artillery_emplacement, dict(ao_distance=.45, grime_height=.35)),
}
