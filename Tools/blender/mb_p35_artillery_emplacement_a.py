"""Prompt 35 wave 10 (lane B): artillery_emplacement_a, the counter-battery branch (artillery_emplacement.cb,
howitzer_cb; unit_refs M284 155 mm), rebuilt from scratch (spec: Tools/blender/specs/artillery_emplacement_a.json) as
an upgrade of the emplacement lane A built for the mortar branch in wave 2 (artillery_emplacement_b): the same
U-shaped earth berm open at the rear with sandbag courses on its crest (a newer canvas course on the front), the
timber revetment inside, the plank floor, the sod on the slopes, a camouflage net over the rear right, ammunition
stacks, aiming posts, stones and ground patches, the crew MG on a pintle post on the front-left parapet.

The branch's own gun and sensor: a towed 155 mm howitzer (M198 / M777 class) dug in on its firing platform: the
split trails spread back to their spades, the lower carriage with the traverse ring and the jack, the upper carriage
with its side plates and the equilibrators, the cradle with the recoil cylinders, the long L/39 barrel raised 18
degrees with its thermal jacket and the double-baffle muzzle brake, the breech and the loading tray; and the
counter-battery radar on the front-right corner of the berm (a small phased-array, AN/TPQ-50 class: its turning
panel `Radar` on a turntable, a lattice mast on a cast pad, a cable run to the command box), the shell and charge
store under a tarp.

Runtime nodes kept at their old places: `Turret` (0, 0, 0.09) with `Muzzle_main` (0, -6.57, 3.74), `Radar`
(-2.75, -2.55, 2.35), `Mount_mg` / `Muzzle_mg` (the parapet gun). Built only from frontier_kit / mb_kit27
primitives, mb_kit35, the wave 2 helpers and lane B's; no other model's builder. Metres, +Z up, -Y front, +X left.
Under 6,000 triangles.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w2parts as W
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
G = .09


def _emplacement(a):
    k.extrude(a.part('Base', 'Dirt'), [(-3.4, -3.3), (-1.6, -3.5), (.4, -3.32), (2.2, -3.55), (3.45, -3.1),
                                       (3.3, -1.2), (3.55, .8), (3.3, 2.6), (3.05, 3.45), (1.0, 3.3), (-.9, 3.55),
                                       (-2.6, 3.35), (-3.45, 2.5), (-3.25, .6), (-3.55, -1.3)], G,
              loc=(0, 0, G / 2), axis='Z', corner=.05, taper=(.97, .97), caps=(False, True))
    berm = a.part('Berm', 'Dirt')
    k.extrude(berm, [(-.6, 0), (.6, 0), (.2, .65), (-.2, .65)], 6.6, loc=(0, -2.85, G), axis='X', caps=(True, True))
    for s in (-1, 1):
        k.extrude(berm, [(-.6, 0), (.6, 0), (.2, .65), (-.2, .65)], 5.0, loc=(s * 2.95, .15, G), rot=(0, 0, R90),
                  axis='X', caps=(True, True))
    W.bags(a, [(-2.9, -2.85, G + .65), (-1.0, -2.85, G + .65)], layers=1, bag=(.6, .32, .18), seed=43)
    W.bags(a, [(1.0, -2.85, G + .65), (2.9, -2.85, G + .65)], layers=1, bag=(.6, .32, .18), seed=44)
    for s in (-1, 1):
        W.bags(a, [(s * 2.95, -2.4, G + .65), (s * 2.95, 2.5, G + .65)], layers=1, bag=(.6, .32, .18), seed=45 + s)
    W.bags(a, [(-2.6, -2.85, G + .83), (-1.1, -2.85, G + .83)], layers=1, bag=(.6, .32, .18), seed=47, mat='Canvas',
           name='Sandbags_new')
    rev = a.part('Revetment', 'Wood')
    for x in (-1.8, -.6, .6, 1.8):
        rev.box((.12, .12, .8), loc=(x, -2.25, G + .4), bevel=0)
    rev.box((4.4, .06, .25), loc=(0, -2.22, G + .55), bevel=0)
    rev.box((4.4, .06, .25), loc=(0, -2.22, G + .2), bevel=0)
    for s in (-1, 1):
        for y in (-1.3, 0, 1.3):
            rev.box((.12, .12, .8), loc=(s * 2.25, y, G + .4), bevel=0)
        rev.box((.06, 3.6, .25), loc=(s * 2.22, 0, G + .5), bevel=0)
    fl = a.part('Floor', 'Wood')
    for i in range(10):
        fl.box((3.2, .2, .05), loc=(0, -1.6 + i * .3, G + .025), rot=(0, 0, .01 * (i % 3 - 1)), bevel=0)
    for (x, y, w, d, yaw, tilt) in ((0, -3.25, 6.0, .35, 0, .55), (0, -2.45, 4.0, .3, 0, -.55),
                                    (3.35, .2, 4.4, .35, R90, .55), (-3.35, .2, 4.4, .35, R90, .55)):
        mat = 'Grass' if tilt > 0 else 'FoliageDark'
        size, rot = ((w, d, .03), (tilt, 0, 0)) if yaw == 0 else ((d, w, .03), (0, tilt * (1 if x > 0 else -1), 0))
        a.part(f'Berm_sod_{mat.lower()}', mat).box(size, loc=(x, y, G + .33), rot=rot, bevel=0)
    K.pintle_mg(a, None, (1.73, -2.47, .72), post=.4, scale=1.0, length=.9)
    # The camouflage net over the rear right, ammunition stacks, charge cans, aiming posts.
    P.camo_net(a, [(-2.3, 1.2, 2.0), (-.9, 1.2, 2.2), (-.9, 3.1, 1.9), (-2.3, 3.1, 1.8)], .35, G, garnish=5, seed=8)
    W.stack(a, (1.9, 2.6, G), n=3, size=(.55, .3, .24), yaw=.2, seed=48)
    for i in range(4):
        a.part('Charge_cans', 'Fuel').cyl(.13, .55, loc=(.6 + i * .3, 2.4, G + .28), seg=8, bevel=0)
    k.extrude(a.part('Tarp', 'Canvas'), [(-.7, 0), (.7, 0), (.6, .45), (-.6, .45)], 1.4, loc=(-1.6, 2.1, G), axis='X',
              chamfer=.03)
    for (x, y) in ((-2.0, -1.6), (2.0, -1.6)):
        a.part('Aiming_posts', 'Hazard').cyl(.03, 2.2, loc=(x, y, G + 1.1), seg=5, bevel=0)
        a.part('Aiming_bands', 'Charred').cyl(.034, .15, loc=(x, y, G + 1.0), seg=5, bevel=0)
    rk = a.part('Stones', 'Rock')
    for i in range(26):
        x = -3.2 + 6.4 * ((i * .618) % 1.0)
        y = -3.2 + 6.5 * ((i * .382 + .29) % 1.0)
        if abs(x) < 2.3 and -2.3 < y < 2.0 and abs(x) > 1.4:
            continue
        sz = .1 + (i % 4) * .04
        rk.box((sz, sz * 1.3, sz * .6), loc=(x, y, G + sz * .2), rot=(i * .7, i * .3, i * 1.3), bevel=0)
    # Shell pallets with the 155 mm rounds standing, a second sandbag course on the side berms, jerrycans.
    pal = a.part('Pallets', 'Wood')
    for (x, y) in ((1.6, 1.0),):
        pal.box((.9, .7, .12), loc=(x, y, G + .06), bevel=0)
        for i in range(3):
            for j in range(2):
                k.lathe(a.part('Shells', 'Gilded'), [(.075, 0), (.075, .55), (.04, .7), (0, .74)],
                        loc=(x - .27 + i * .27, y - .15 + j * .3, G + .12), seg=6, caps=(False, True))
    for s in (-1, 1):
        W.bags(a, [(s * 2.95, -2.1, G + .83), (s * 2.95, .4, G + .83)], layers=1, bag=(.6, .32, .18), seed=49 + s,
               mat='Canvas', name='Sandbags_new')
    for i in range(3):
        K.jerrycan(a.part('Jerrycans', 'Armor'), (-.6 + i * .3, 2.9, G), rot=(0, 0, .1 * i))
    for i, (x, y, w, yaw, mat) in enumerate(((-1.7, -1.6, .8, .4, 'Sandstone'), (1.6, -1.7, .7, 1.2, 'Rock'),
                                             (-1.75, .1, .7, 2.0, 'SandstoneDark'), (1.7, .2, .6, .7, 'Sandstone'),
                                             (-1.0, 3.0, .8, 1.6, 'Rock'), (.6, 3.05, .7, .3, 'FoliageDark'),
                                             (2.6, 3.0, .6, 1.0, 'SandstoneDark'), (-1.6, -.8, .5, 2.4, 'Charred'),
                                             (1.3, -1.0, .5, .5, 'Charred'), (0, 2.75, .6, 1.4, 'Sandstone'),
                                             (-3.1, -3.0, .7, .5, 'Grass'), (3.1, 3.0, .6, .9, 'Grass'))):
        a.part(f'Ground_{mat.lower()}', mat).box((w, w * .7, .006), loc=(x, y, G + .003 + (i % 3) * .001),
                                                 rot=(0, 0, yaw), bevel=0)
    a.part('Scorch', 'Charred').box((1.8, 1.0, .006), loc=(0, -1.9, G + .004), bevel=0)


def _howitzer(a):
    t = a.pivot('Turret', (0, 0, .09))
    # Lower carriage: the traverse ring on the firing platform, the jack, the split trails spread to their spades.
    k.lathe(a.part('Firing_base', 'Armor', t), [(.85, 0), (.85, .1), (.7, .16), (.5, .2), (0, .2)], seg=12, worn=(1,))
    trails = a.part('Trails', 'Team', t)
    for s in (-1, 1):
        end = (s * 1.7, 2.7, .12)
        trails.limb((s * .3, .3, .45), end, .2, .22, bevel=.02)
        k.block(a.part('Spades', 'Armor', t), (.5, .1, .4), loc=(end[0], end[1] + .1, end[2] - .05), chamfer=.01)
        a.part('Trail_handles', 'Steel', t).tube([(end[0] - .15, end[1] - .2, end[2] + .15),
                                                  (end[0] - .15, end[1] - .2, end[2] + .35),
                                                  (end[0] + .15, end[1] - .2, end[2] + .35),
                                                  (end[0] + .15, end[1] - .2, end[2] + .15)], .02, seg=4)
    # Upper carriage: side plates, equilibrators, the cradle and recoil cylinders, the barrel.
    tr = (0, .2, 1.4)                           # trunnion
    e = math.atan2(3.65 - tr[2], 6.57 + tr[1])
    bore = P.Elev(tr, e)
    car = a.part('Carriage', 'Armor', t)
    for s in (-1, 1):
        k.extrude(car, [(-.7, 0), (.6, 0), (.3, 1.0), (-.2, 1.25), (-.5, 1.0)], .06, loc=(s * .42, .25, .38),
                  rot=(0, 0, R90), axis='X', chamfer=.01)
        a.part('Equilibrators', 'Steel', t).tube([(s * .5, .8, .6), (s * .5, -.6, 1.55)], .07, seg=6)
        a.part('Trunnions', 'Steel', t).cyl(.1, .1, loc=(s * .5, tr[1], tr[2]), rot=(0, R90, 0), seg=8, bevel=0)
    k.block(a.part('Cradle', 'Armor', t), (.5, 1.9, .4), loc=bore.at(.4, up=-.12), rot=bore.box_rot, chamfer=.04)
    for s in (-1, 1):
        k.lathe(a.part('Recoil_cyl', 'Steel', t), [(.07, -.9), (.07, .9)], loc=bore.at(.4, dx=s * .2, up=-.3),
                rot=bore.lathe_rot, seg=8)
    L = math.hypot(6.57 + tr[1], 3.65 - tr[2])
    k.lathe(a.part('Main_cannon', 'Steel', t), [(.0, -1.15), (.22, -1.1), (.22, -.5), (.17, -.4), (.17, 1.2),
                                                (.14, 1.4), (.11, L - .7), (0, L - .7)], loc=tr, rot=bore.lathe_rot,
            seg=10, worn=(3,))
    k.lathe(a.part('Thermal_jacket', 'Team', t), [(.15, .9), (.15, 2.6)], loc=tr, rot=bore.lathe_rot, seg=10)
    k.lathe(a.part('Muzzle_brake', 'Undercarriage', t), [(.1, L - .72), (.2, L - .7), (.2, L - .02), (.08, L),
                                                         (0, L - .02)], loc=tr, rot=bore.lathe_rot, seg=10)
    for f in (.25, .5):
        a.part('Brake_ports', 'Charred', t).box((.44, .06, .07), loc=bore.at(L - f), rot=bore.box_rot, bevel=0)
    a.part('Breech_block', 'Armor', t).box((.4, .3, .4), loc=bore.at(-1.0), rot=bore.box_rot, bevel=0)
    k.block(a.part('Loading_tray', 'Steel', t), (.35, .9, .06), loc=bore.at(-1.6, up=-.25), rot=bore.box_rot,
            chamfer=0)
    k.block(a.part('Sight', 'Armor', t), (.16, .3, .2), loc=(.55, -.1, 1.55), chamfer=.01)
    a.part('Glass', 'Glass', t).box((.03, .02, .08), loc=(.55, -.26, 1.6), bevel=0)
    k.extrude(a.part('Gun_shield', 'Armor', t), [(-.55, 0), (.55, 0), (.5, .7), (-.5, .7)], .03,
              loc=(-.8, -.4, .75), rot=(R90 - .1, 0, .25), axis='Z', chamfer=.005)
    # The road wheels raised off the ground on their arms (firing position), the hub caps.
    for s in (-1, 1):
        K.tread_wheel(a, (s * 1.05, -.2, .62), .55, .32, s, seg=14, parent=t, nuts=6)
        a.part('Wheel_arms', 'Armor', t).limb((s * .5, .1, .6), (s * .9, -.2, .62), .12, .14, bevel=0)
    a.pivot('Muzzle_main', (0, -6.57, 3.65), t)
    K.soot(a, (0, -6.3, 3.5), radius=.8, k=.35)


def _radar(a):
    rx, ry = -2.75, -2.55
    k.block(a.part('Radar_pad', 'Concrete'), (1.1, 1.1, .25), loc=(rx, ry, G + .65 + .12), chamfer=.03)
    ms = a.part('Radar_mast', 'Steel')
    for dx, dy in ((-.3, -.3), (.3, -.3), (.3, .3), (-.3, .3)):
        ms.tube([(rx + dx, ry + dy, G + .9), (rx + dx * .35, ry + dy * .35, 2.2)], .03, seg=4)
    for z in (1.3, 1.8):
        f = 1 - .65 * (z - G - .9) / (2.2 - G - .9)
        pts = [(rx + dx * f, ry + dy * f, z) for dx, dy in ((-.3, -.3), (.3, -.3), (.3, .3), (-.3, .3), (-.3, -.3))]
        ms.tube(pts, .012, seg=3, caps=False)
    r = a.pivot('Radar', (rx, ry, 2.35))
    k.block(a.part('Radar_turntable', 'Armor', r), (.35, .35, .16), loc=(0, 0, -.1), chamfer=.02)
    k.extrude(a.part('Radar_panel', 'PlasterWhite', r), [(-.55, -.07), (.55, -.07), (.5, .07), (-.5, .07)], .8,
              loc=(0, -.05, .45), rot=(-.3, 0, 0), axis='Z', chamfer=.012)
    cells = a.part('Radar_cells', 'Undercarriage', r)
    for i in range(4):
        for j in range(3):
            cells.box((.2, .02, .18), loc=(-.36 + i * .24, -.135 - (j - 1) * .07, .45 + (j - 1) * .23),
                      rot=(-.3, 0, 0), bevel=0)
    k.block(a.part('Radar_box', 'Armor', r), (.4, .25, .3), loc=(0, .2, .1), chamfer=.02)
    a.part('Kit_cables', 'Undercarriage').tube([(rx, ry + .3, G + .9), (rx + .5, ry + 1.2, G + .3),
                                                (-1.6, -.4, G + .3)], .025, seg=3)
    k.block(a.part('Command_box', 'Armor'), (.5, .4, .45), loc=(-1.6, -.4, G + .22), chamfer=.02)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-1.75, -.3, G + .45), h=2.6, r=.022)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-2.4, -2.2, G + .9), h=2.4, r=.02)
    a.part('Flag_pole', 'Steel').cyl(.025, 3.0, loc=(3.1, 2.9, G + 1.5), seg=6, bevel=0)
    a.part('Flag', 'Team').box((.03, .6, .4), loc=(3.1, 2.6, G + 2.8), rot=(0, 0, .12), bevel=0)


def artillery_emplacement_a(a):
    _emplacement(a)
    _howitzer(a)
    _radar(a)
    for i in range(8):
        u = i * TAU / 8
        K.dust(a, (math.cos(u) * 2.6, math.sin(u) * 2.6, G), radius=1.2, k=.3)
    k.clean(a)


BUILDERS = {'artillery_emplacement_a': (artillery_emplacement_a, dict(ao_distance=.5, grime_height=.15,
                                                                      ao_strength=.5))}
