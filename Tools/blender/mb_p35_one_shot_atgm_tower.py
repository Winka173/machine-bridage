"""Prompt 35 wave 3 (lane B): the one-shot ATGM battery rebuilt from scratch (spec:
Tools/blender/specs/one_shot_atgm_tower.json).

An automatic Kornet-class launcher the Accord sets on a field-built crib (the def's modelSize 4.8 x 4.8 x 3.6 m; the
tower fires its clip of eight, then has to be bought again): a square crib of railway sleepers laid crosswise in
alternate courses, filled with earth and capped with a course of sandbags, a sleeper stair up its back; on the crib's
deck a steel pedestal and the turning launcher (`Turret`): an armoured cradle holding eight transport-launch
containers in two rows of four (their dark bores, the Team bands round the pack), the guidance unit with its thermal
sight and laser window under a sun hood, a warning beacon; a cable down to the remote operator's foxhole behind the
crib (a sandbagged scrape with the control console and a whip antenna); two spare-round crates and three spent tubes
thrown on the ground.

Its own body: no shape is shared with the ATGM tower family (Kornet towers on lattice legs) or the other towers.
Runtime nodes kept: `Turret`, `Muzzle_main` (the weapon's one muzzle), `Muzzle_missile` (the old file's second
launch point); old part names `Slab`, `Sandbags`, `Pedestal`, `Turntable`, `Deck`, `Launcher`, `Tubes`,
`Launcher_bores`, `Launcher_hood`, `Launcher_bands`, `Steps`, `Crates`, `Antennas`, `Beacon`. Metres, +Z up, -Y front.
"""
import math
import random

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
C = 2.4                 # the crib's side
CZ = 1.36               # the crib's top (sleepers)
TOP = CZ + .17          # the deck on the sandbag cap
TT = (0, -.15, TOP + .55)
ELEV = math.radians(6)


def _crib(a, rng):
    P.earth_pad(a, [(-1.75, -1.6), (-.2, -1.85), (1.6, -1.7), (1.85, -.2), (1.7, 1.75), (.1, 1.9), (-1.7, 1.7),
                    (-1.9, .1)], .1, taper=.88)
    slab = a.part('Slab', 'Wood')                     # the sleeper footing the crib stands on
    for s in (-1, 1):
        k.block(slab, (C + .4, .26, .08), loc=(0, s * (C / 2 - .05), .14), chamfer=0)
    crib = a.part('Crib', 'LogWood')
    # The earth fill showing between the sleepers (its four faces only: top and bottom are never seen).
    h, z0, f = CZ - .18, .18, C / 2 - .15
    q = [(-f, -f), (f, -f), (f, f), (-f, f)]
    verts = [(x, y, z0) for x, y in q] + [(x, y, z0 + h) for x, y in q]
    a.part('Crib_fill', 'Dirt').mesh(verts, [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
    z, course = .18, 0
    while z < CZ - .05:
        for s in (-1, 1):
            jl = rng.uniform(-.06, .1)
            if course % 2 == 0:
                k.block(crib, (C + .25 + jl, .22, .17), loc=(rng.uniform(-.04, .04), s * (C / 2 - .11), z + .085),
                        chamfer=.025)
            else:
                k.block(crib, (.22, C + .25 + jl, .17), loc=(s * (C / 2 - .11), rng.uniform(-.04, .04), z + .085),
                        chamfer=.025)
        # Steel spikes pinning the course to the one below (two per sleeper end, both faces).
        for s in (-1, 1):
            for e in (-1, 1):
                if course % 2 == 0:
                    a.part('Kit_spikes', 'Steel').box((.03, .02, .03), loc=(e * (C / 2 - .05), s * C / 2 + s * .005,
                                                                           z + .1), bevel=0)
                else:
                    a.part('Kit_spikes', 'Steel').box((.02, .03, .03), loc=(s * C / 2 + s * .005, e * (C / 2 - .05),
                                                                           z + .1), bevel=0)
        z += .17
        course += 1
    # The sandbag cap on the crib, the deck boards inside it.
    sq = [(-C / 2 + .2, -C / 2 + .2, CZ), (C / 2 - .2, -C / 2 + .2, CZ), (C / 2 - .2, C / 2 - .2, CZ),
          (-C / 2 + .2, C / 2 - .2, CZ)]
    P.sandbag_run(a, sq, courses=1, bag=(.6, .36, .18), part='Sandbags', seed=101, closed=True, lean=True)
    deck = a.part('Deck', 'Wood')
    for j in range(6):
        deck.box((C - .5, .28, .04), loc=(0, -C / 2 + .45 + j * .3, TOP - .02), bevel=0)
    # Ready kit on the deck's rear corners: two ammunition boxes, a jerrycan, an extinguisher.
    P.ammo_box(a, (-.75, .75, TOP), size=(.5, .3, .26), rot=(0, 0, .2))
    P.ammo_box(a, (-.75, .75, TOP + .26), size=(.5, .3, .26), rot=(0, 0, .1))
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (.8, .8, TOP), rot=(0, 0, 1.4))
    k.lathe(a.part('Extinguishers', 'BarrelRed'), [(.07, 0), (.07, .38), (.04, .44), (0, .46)], loc=(.75, .3, TOP),
            seg=8, worn=(1,))
    # A course of sandbags along the crib's front foot (splinter protection), the sleeper stair up the back.
    P.sandbag_run(a, [(-C / 2 - .1, -C / 2 - .3, .1), (C / 2 + .1, -C / 2 - .3, .1)], courses=2, bag=(.6, .34, .17),
                  part='Sandbags', seed=103, lean=True)
    st = a.part('Steps', 'Wood')
    for j in range(6):
        k.block(st, (.8 + rng.uniform(-.05, .05), .32, .22), loc=(.6, C / 2 + .95 - j * .16, .1 + j * .22 + .11),
                chamfer=0)
    for i in range(10):
        u = i * math.tau / 10
        K.dust(a, (math.cos(u) * 1.6, math.sin(u) * 1.6, .1), radius=1.1, k=.3)


def _launcher(a):
    ped = a.part('Pedestal', 'Armor')
    k.lathe(ped, [(.45, 0), (.45, .05), (.22, .12), (.18, .45), (.28, .5), (0, .5)], loc=(TT[0], TT[1], TOP), seg=12,
            worn=(1, 4))
    for i in range(4):
        u = i * R90 + math.pi / 4
        ped.box((.03, .3, .3), loc=(TT[0] + math.cos(u) * .25, TT[1] + math.sin(u) * .25, TOP + .15), rot=(0, 0, u),
                bevel=0)
    k.ring(a.part('Turntable', 'Steel'), [(.3, -.03), (.38, -.03), (.38, .04), (.3, .04)], loc=TT, seg=14)
    K.bolt_ring(a.part('Kit_bolts', 'Steel'), (TT[0], TT[1], TOP + .03), (0, 0, 1), .38, 8, r=.025, h=.03)
    t = a.pivot('Turret', TT)
    # The yoke carrying the cradle on trunnions.
    yk = a.part('Armor', 'Armor', t)
    k.lathe(yk, [(.38, 0), (.38, .08), (0, .1)], seg=14)
    for s in (-1, 1):
        k.extrude(yk, [(-.22, .05), (.22, .05), (.12, .62), (-.12, .62)], .08, loc=(s * .66, 0, 0), axis='X',
                  chamfer=.02)
    g = P.Elev((0, 0, .62), ELEV)
    # The cradle: an armoured frame holding the 2 x 4 pack of containers.
    box = a.part('Launcher', 'Armor', t)
    k.block(box, (1.34, 1.7, .1), loc=g.at(-.1, up=-.43), rot=g.box_rot, chamfer=.02)
    k.block(box, (1.34, 1.7, .08), loc=g.at(-.1, up=.45), rot=g.box_rot, chamfer=.02)
    for s in (-1, 1):
        k.block(box, (.06, 1.7, .9), loc=g.at(-.1, s * .67), rot=g.box_rot, chamfer=.015)
    tubes = a.part('Tubes', 'Team', t)
    bores = a.part('Launcher_bores', 'Undercarriage', t)
    caps = a.part('Tube_caps', 'Steel', t)
    first = None
    for row in range(2):
        for col in range(4):
            dx, up = -.45 + col * .3, -.17 + row * .34
            k.lathe(tubes, [(.125, -.95), (.135, -.92), (.135, .72), (.125, .75)], loc=g.at(-.1, dx, up),
                    rot=g.lathe_rot, seg=10)
            bores.cyl(.095, .02, loc=g.at(.66, dx, up), rot=g.lathe_rot, seg=10, bevel=0)
            caps.cyl(.14, .04, loc=g.at(-1.02, dx, up), rot=g.lathe_rot, seg=10, bevel=0)
            if first is None:
                first = (dx, up)
    bands = a.part('Launcher_bands', 'Team', t)
    for z in (-.55, .3):
        bands.box((1.36, .06, .94), loc=g.at(z), rot=g.box_rot, bevel=0)
    a.pivot('Muzzle_main', g.at(.78, first[0], first[1]), t)
    a.pivot('Muzzle_missile', g.at(.78, -first[0], first[1]), t)
    # The guidance unit on top: thermal sight and laser window under a sun hood; the warning beacon behind it.
    gu = a.part('Guidance', 'Armor', t)
    k.block(gu, (.42, .5, .3), loc=g.at(-.15, .25, up=.65), rot=g.box_rot, chamfer=.03)
    k.extrude(a.part('Launcher_hood', 'Armor', t), [(-.24, 0), (.24, 0), (.24, .02), (-.24, .02)], .25,
              loc=g.at(.18, .25, up=.82), rot=(-ELEV, 0, 0), axis='Y', chamfer=0)
    glass = a.part('Glass', 'Glass', t)
    for dx in (.17, .33):
        glass.cyl(.06, .02, loc=g.at(.11, dx, up=.65), rot=g.lathe_rot, seg=10, bevel=0)
    K.beacon(a, g.at(-.55, -.3, up=.5), parent=t, r=.07)
    K.handle(a.part('Kit_handles', 'Steel', t), g.at(-.5, .25, up=.81), g.at(-.2, .25, up=.81), (0, 0, 1), h=.06,
             r=.012)
    a.part('Kit_cables', 'Undercarriage', t).tube([g.at(-.6, .3, up=.5), (.3, .6, .25), (.2, .3, .05)], .02, seg=4)
    return t


def _ground(a, rng):
    # The remote operator's foxhole behind the crib (rear left): a sandbagged scrape, the console, the whip.
    fx, fy = -1.45, 1.75
    ring = [(fx + math.cos(u) * .65, fy + math.sin(u) * .65, .02) for u in [i * math.tau / 9 for i in range(9)]]
    P.sandbag_run(a, ring[1:] + ring[:1], courses=2, bag=(.5, .3, .15), part='Sandbags', seed=102, lean=True)
    k.block(a.part('Console', 'Armor'), (.4, .3, .32), loc=(fx, fy - .1, .3), chamfer=.03)
    a.part('Console_screen', 'Glass').box((.28, .01, .16), loc=(fx, fy - .255, .36), rot=(-.3, 0, 0), bevel=0)
    a.part('Console_legs', 'Steel').box((.3, .2, .14), loc=(fx, fy - .1, .07), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (fx - .25, fy + .2, .4), h=1.8, r=.025, lean=.08)
    P.camo_net(a, [(fx - .75, fy - .55, 1.15), (fx + .7, fy - .6, 1.2), (fx + .1, fy + .75, 1.0)], .15, 0.0,
               garnish=6, seed=104)
    a.part('Kit_cables', 'Undercarriage').tube([(fx + .2, fy - .1, .1), (-.6, 1.4, .05), (.2, 1.3, .1),
                                                (.2, .3 + C / 2 - 1.0, CZ * .5)], .02, seg=4)
    # Spare-round crates, three spent containers thrown down, stones.
    crates = a.part('Crates', 'Crate')
    straps = a.part('Kit_straps', 'Steel')
    K.crate(crates, straps, (1.25, .36, .3), (1.6, .8, .1), rot=(0, 0, R90 + .15), bands=2)
    K.crate(crates, straps, (1.25, .36, .3), (1.6, .1, .1), rot=(0, 0, R90 - .1), bands=2)
    spent = a.part('Spent_tubes', 'Team')
    for j, (x, y, r) in enumerate(((-1.6, -.6, .4), (-1.55, .15, -.3), (1.55, -1.05, 1.2))):
        k.lathe(spent, [(.11, -.75), (.12, -.72), (.12, .72), (.11, .75)], loc=(x, y, .22), rot=(R90, 0, r), seg=8)
    st = a.part('Stones', 'Rock')
    for j in range(16):
        z = rng.uniform(.05, .12)
        st.box((z * 1.3, z, z * .7), loc=(rng.uniform(-1.6, 1.6), rng.uniform(-1.8, -1.5), .1 + z * .1),
               rot=(0, 0, rng.uniform(0, 3)), bevel=0)


def one_shot_atgm_tower(a):
    """The one-shot ATGM battery: see the module docstring."""
    rng = random.Random(3591)
    _crib(a, rng)
    _launcher(a)
    _ground(a, rng)
    k.clean(a)


BUILDERS = {
    'one_shot_atgm_tower': (one_shot_atgm_tower, dict(ao_distance=.55, grime_height=.6)),
}
