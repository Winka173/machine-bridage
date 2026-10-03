"""Prompt 35 wave 4 (lane C): the 40 mm AA gun vehicle rebuilt from scratch (spec: Tools/blender/specs/aa_gun_vehicle.json).

A CV9040 AAV (the def's modelSize 5.9 x 2.5 x 2.7 m): the CV90 hull with its sharp wedge nose and long upper
glacis, the tall troop hull with the rear door, seven road wheels a side under steel skirts, the front sprocket
and rear idler; the Bofors turret with the long 40 mm L/70 gun (perforated cooling jacket, flash suppressor) in
its mantlet, the coaxial 7.62 mm, the commander's sight, smoke dischargers on both cheeks; the search radar
array turning on its mast over the turret rear (`Radar`).

Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Radar`, `Radar_mast`, `Radar_panel`,
`Point_exhaust`, `Point_fire`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TX, TW = .94, .42
WR = .26
WHEELS = (-1.95, -1.32, -.68, -.04, .6, 1.24, 1.88)
TOP = 1.32
NOSE, TAIL = -2.75, 2.72
TUR = (0, -.35, TOP)


def _hull(a):
    hull = a.part('Hull', 'Team')
    def sec(wl, zl, ws, zs, wt, zt):
        return [(0, zl), (wl, zl), (wl, zs - .1), (ws, zs), (wt, zt), (0, zt)]
    # The CV90's wedge: a sharp lower nose, the long upper glacis, the tall hull leaning in above the sponsons.
    C.section_loft(hull, [
        (NOSE, sec(.55, .62, .62, .66, .55, .7)),
        (NOSE + .45, sec(.72, .38, 1.12, .7, 1.0, .86)),
        (-1.55, sec(.74, .34, 1.17, .72, 1.08, TOP)),
        (2.55, sec(.74, .34, 1.17, .72, 1.08, TOP)),
        (TAIL, sec(.72, .4, 1.15, .72, 1.06, TOP - .06)),
    ])
    for s in (-1, 1):
        sk = a.part('Skirts', 'Team')
        for j in range(4):
            sk.box((.025, 1.08, .32), loc=(s * 1.19, -1.6 + j * 1.1, .6), bevel=0)
        a.part('Skirt_flaps', 'Rubber').box((.02, 4.4, .06), loc=(s * 1.19, -.05, .41), bevel=0)
        a.part('Team_band', 'Team').box((.01, 2.6, .07), loc=(s * 1.13, .4, 1.08), rot=(0, s * .1, 0), bevel=0)
    # Driver's hatch (front left), the engine grilles (front right), lamps, tow hooks, the glacis rivets.
    C.hatch(a, (.5, -1.7, .97), r=.24, periscope=True)
    K.grille(a, (-.45, -1.75, .98), .75, .55, facing=(0, -.3, 1), slats=5, frame_mat='Team')
    for s in (-1, 1):
        K.lamp(a, (s * .85, -2.35, .82), (0, -1, .2), r=.06, guard=True)
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .4, NOSE - .02, .6), facing=(0, -1, 0), size=.07)
    K.exhaust(a, (-1.1, -1.25, 1.0), r=.05, length=.3, direction=(-1, 0, .2), muffler=False, cap=False)
    a.pivot('Point_exhaust', (-1.2, -1.25, 1.05))
    # The rear door with its hinges and handle, the roof hatches over the troop space, stowage racks.
    door = a.part('Hatches', 'Armor')
    K.plate(door, (.9, .04, .8), loc=(0, TAIL + .02, .82))
    st = a.part('Kit_steel', 'Steel')
    for z in (.55, 1.05):
        K.hinge(st, (.47, TAIL + .05, z - .1), (.47, TAIL + .05, z + .1), r=.025, knuckles=2)
    K.handle(st, (-.3, TAIL + .05, .8), (-.3, TAIL + .05, .95), (0, 1, 0), h=.04, r=.012)
    for x in (-.5, .5):
        C.hatch(a, (x, 1.7, TOP), r=.26)
    for s in (-1, 1):
        a.part('Tail_lamps', 'LavaGlow').box((.08, .02, .05), loc=(s * .9, TAIL + .01, 1.12), bevel=0)
        C.stowage_box(a, (.3, .9, .26), (s * .92, 1.1, TOP - .02), mat='Armor', latches=2)
    a.pivot('Point_fire', (0, 1.2, TOP + .3))


def _running_gear(a):
    for s in (-1, 1):
        C.running_gear(a, s, TX, TW, WHEELS, WR, sprocket=(-2.35, .5, .24), idler=(2.38, .45, .23),
                       rollers=[(-1.0, .63), (.9, .63)], pitch=.21, hide_top=(-2.2, 2.2, .55), disc_mat='Armor',
                       wheel_w=.16, seg=8, teeth=11)


def _turret(a):
    t = a.pivot('Turret', TUR)
    K.turret_ring(a.part('Turret_ring', 'Armor'), TUR, .8, h=.05)
    body = a.part('Turret_body', 'Team', t)
    bot = [(-.4, -1.0), (.4, -1.0), (.92, -.6), (.95, .9), (.72, 1.15), (-.72, 1.15), (-.95, .9), (-.92, -.6)]
    top = [(-.3, -.78), (.3, -.78), (.78, -.45), (.8, .82), (.6, 1.02), (-.6, 1.02), (-.8, .82), (-.78, -.45)]
    C.slab_loft(body, bot, top, 0, .55)
    k.block(a.part('Turret_roof', 'Armor', t), (1.3, 1.4, .04), loc=(0, .2, .55), chamfer=.01)
    # Mantlet, the 40 mm L/70: cooling jacket with its rows of holes, the barrel, the flash suppressor.
    man = a.part('Mantlet', 'Armor', t)
    k.extrude(man, [(-.18, -.2), (.12, -.22), (.18, .2), (-.12, .22)], .46, loc=(0, -1.0, .3), axis='X', chamfer=.03,
              corner=.02)
    gun = a.part('Main_cannon', 'Steel', t)
    k.lathe(gun, [(.075, 0), (.075, .85), (.05, .9), (.042, 1.5), (0, 1.5)], loc=(0, -1.12, .3), rot=K.FORWARD,
            seg=10, worn=(1,))
    holes = a.part('Main_cannon_holes', 'Undercarriage', t)
    for j in range(5):
        for u in (0, R90, 2 * R90, 3 * R90):
            holes.box((.02, .07, .02), loc=(math.cos(u) * .076, -1.25 - j * .12, .3 + math.sin(u) * .076),
                      rot=(0, u, 0), bevel=0)
    k.lathe(a.part('Muzzle_brake', 'Undercarriage', t), [(.045, 0), (.07, .04), (.07, .3), (.055, .34), (0, .34)],
            loc=(0, -2.6, .3), rot=K.FORWARD, seg=10, worn=(1,))
    a.pivot('Muzzle_main', (0, -2.95, .3), t)
    a.part('MG_coax', 'Steel', t).cyl(.02, .4, loc=(.26, -1.15, .32), rot=K.FORWARD, seg=6, bevel=0)
    # The commander's sight head, the gunner's sight window, hatches, smoke dischargers, the bustle bin.
    sh = a.part('Sight', 'Armor', t)
    k.lathe(sh, [(.11, 0), (.11, .14), (.14, .16), (.14, .3), (0, .32)], loc=(.42, -.15, .55), seg=10, worn=(3,))
    a.part('Glass', 'Glass', t).box((.14, .01, .07), loc=(.42, -.29, .78), bevel=0)
    a.part('Glass', 'Glass', t).box((.22, .01, .08), loc=(-.45, -.6, .48), rot=(.5, 0, 0), bevel=0)
    C.hatch(a, (.42, .45, .57), r=.24, parent=t, periscope=True)
    C.hatch(a, (-.42, .35, .57), r=.22, parent=t)
    for s in (-1, 1):
        K.smoke_dischargers(a, .85, -.3, .38, s, count=3, parent=t)
    C.stowage_box(a, (1.1, .3, .32), (0, 1.25, .12), mat='Armor', latches=2, parent=t)
    # The search radar on its mast over the turret rear, the array turning on `Radar`.
    mast = a.part('Radar_mast', 'Steel', t)
    k.lathe(mast, [(.16, .55), (.16, .6), (.07, .68), (.06, .95)], loc=(0, .78, 0), seg=10, worn=(1,))
    r = a.pivot('Radar', (0, .78, .95), t)
    pan = a.part('Radar_panel', 'Armor', r)
    k.block(pan, (1.1, .14, .48), loc=(0, 0, 0), chamfer=.02)
    a.part('Radar_face', 'Undercarriage', r).box((1.0, .01, .4), loc=(0, -.075, .24), bevel=0)
    a.part('Radar_face', 'Undercarriage', r).box((.2, .2, .1), loc=(0, .1, .05), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (-.7, .8, .55), h=.3)
    for s in (-1, 1):
        a.part('Team_band', 'Team', t).box((.01, 1.3, .07), loc=(s * .87, .2, .3), rot=(0, s * .1, 0), bevel=0)


def aa_gun_vehicle(a, detail=False):
    """The 40 mm AA gun vehicle: see the module docstring."""
    _hull(a)
    _running_gear(a)
    _turret(a)
    K.dust(a, (0, 0, .3), radius=3.0, k=.12)
    k.clean(a)


BUILDERS = {
    'aa_gun_vehicle': (aa_gun_vehicle, dict(ao_distance=.5, grime_height=.5)),
}
