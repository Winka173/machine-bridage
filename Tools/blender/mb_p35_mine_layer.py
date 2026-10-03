"""Prompt 35 wave 4 (lane C): the mine layer rebuilt from scratch (spec: Tools/blender/specs/mine_layer.json).

A GMZ-3 tracked minelayer (the def's modelSize 7.62 x 2.7 x 1.97 m): the long low hull with the armoured cab on
the front left (vision blocks, the driver's hatch), the commander's cupola on the front right carrying the PKT on
its raised mount (the main weapon, on `Turret`), seven road wheels a side with the front sprocket, rear idler and
return rollers; the flat roof carrying the stacked mine boxes in their rack and the loading hatches; on the rear
the inclined mine chute down to the furrow plough lowered behind on its arms, the conveyor housing and the depth
wheel; fender stowage.

Runtime nodes kept: `Turret`, `Turret_mount`, `Turret_body`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`,
`Point_exhaust`, `Point_fire`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TX, TW = 1.0, .46
WR = .27
WHEELS = (-2.35, -1.65, -.95, -.25, .45, 1.15, 1.85)
TOP = 1.32
NOSE, TAIL = -3.25, 2.85


def _hull(a):
    hull = a.part('Hull', 'Team')
    def sec(wl, zl, ws, zs, wt, zt):
        return [(0, zl), (wl, zl), (wl, zs - .1), (ws, zs), (wt, zt), (0, zt)]
    C.section_loft(hull, [
        (NOSE, sec(.6, .55, .7, .62, .62, .7)),
        (NOSE + .5, sec(.74, .36, 1.22, .68, 1.12, 1.0)),
        (-2.1, sec(.76, .34, 1.26, .7, 1.16, TOP)),
        (TAIL - .1, sec(.76, .34, 1.26, .7, 1.16, TOP)),
        (TAIL, sec(.74, .38, 1.24, .7, 1.14, TOP - .05)),
    ])
    for s in (-1, 1):
        a.part('Skirt_edge', 'Armor').box((.04, 5.6, .08), loc=(s * 1.25, -.2, .62), bevel=0)
        a.part('Team_band', 'Team').box((.01, 3.2, .08), loc=(s * 1.2, .3, 1.05), rot=(0, s * .1, 0), bevel=0)
    # The armoured cab front left: raised roof with vision blocks, the driver's hatch; lamps, tow hooks.
    cab = a.part('Cab', 'Team')
    C.slab_loft(cab, [(.05, -2.85), (1.05, -2.85), (1.12, -1.6), (.05, -1.6)],
                [(.12, -2.65), (1.0, -2.65), (1.05, -1.65), (.12, -1.65)], TOP - .05, TOP + .22)
    gl = a.part('Glass', 'Glass')
    for x in (.3, .6, .88):
        gl.box((.2, .02, .08), loc=(x, -2.78, TOP + .1), rot=(-.6, 0, 0), bevel=0)
    C.hatch(a, (.58, -2.1, TOP + .22), r=.24)
    for s in (-1, 1):
        K.lamp(a, (s * 1.0, -2.75, 1.05), (0, -1, .2), r=.06, guard=True)
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .5, NOSE - .02, .52), facing=(0, -1, 0), size=.07)
    K.grille(a, (-.55, -1.2, TOP + .02), .8, .6, facing=(0, 0, 1), slats=5, frame_mat='Team')
    K.exhaust(a, (-1.18, -.7, 1.15), r=.06, length=.35, direction=(-1, 0, .3), muffler=False, cap=False)
    # The TDA thermal smoke apparatus vents through the exhaust louvre (Soviet tracked chassis).
    a.part('Smoke_tda', 'Steel').box((.05, .34, .14), loc=(-1.24, -.7, 1.0), bevel=0)
    a.pivot('Point_exhaust', (-1.25, -.7, 1.25))
    a.pivot('Point_fire', (0, .5, TOP + .3))


def _cupola(a):
    """The commander's cupola front right with the PKT on its raised mount (`Turret`)."""
    loc = (-.6, -2.2, TOP)
    k.lathe(a.part('Turret_mount', 'Armor'), [(.42, 0), (.44, .05), (.42, .18), (.34, .22)], loc=loc, seg=14,
            worn=(1, 2))
    for i in range(4):
        u = -R90 + (i - 1.5) * .6
        K.periscope(a, (loc[0] + math.cos(u) * .42, loc[1] + math.sin(u) * .42, TOP + .12),
                    facing=(math.cos(u), math.sin(u), 0), size=(.1, .07, .06))
    t = C.roof_gun(a, (loc[0], loc[1], TOP + .22), pivot='Turret', post=.12, length=1.0, scale=.85, shield=True)
    k.lathe(a.part('Turret_body', 'Armor', t), [(.3, -.12), (.32, -.1), (.32, -.06), (.28, -.04)], seg=12)


def _mines(a):
    """The roof: the rack of stacked mine boxes, loading hatches; the rear: chute, conveyor housing, plough."""
    rk = a.part('Racks', 'Steel')
    k.sweep(rk, [(-.02, -.02), (.02, -.02), (.02, .02), (-.02, .02)],
            [(1.05, -1.3, TOP + .3), (1.05, 2.4, TOP + .3), (-1.05, 2.4, TOP + .3), (-1.05, -1.3, TOP + .3)],
            closed=True)
    for x in (-1.05, 1.05):
        for y in (-1.3, .55, 2.4):
            rk.box((.03, .03, .3), loc=(x, y, TOP + .15), bevel=0)
    crates = a.part('Crates', 'Crate')
    bands = a.part('Kit_straps', 'Steel')
    for i, (x, y, n) in enumerate(((.6, -.9, 2), (.6, -.25, 1), (-.1, -.9, 1), (-.1, -.2, 2), (.6, .4, 2),
                                   (-.1, .5, 1), (-.7, .5, 2), (.6, 1.1, 1), (-.1, 1.15, 2))):
        for j in range(n):
            K.crate(crates, bands, (.62, .58, .16), (x, y, TOP + .02 + j * .17), bands=1)
    C.hatch(a, (-.7, 1.3, TOP), r=.26)
    C.hatch(a, (-.7, -.6, TOP), r=.26)
    # The conveyor housing on the rear plate, the inclined chute down to the plough.
    hs = a.part('Conveyor', 'Team')
    k.block(hs, (.7, .5, .7), loc=(0, TAIL + .2, .55), chamfer=.04)
    ch = a.part('Mine_chute', 'Armor')
    k.extrude(ch, [(-.25, 0), (.25, 0), (.25, .05), (.2, .05), (.2, .2), (-.2, .2), (-.2, .05), (-.25, .05)], 1.0,
              loc=(0, TAIL + .85, .5), rot=(-.55, 0, 0), axis='Y', chamfer=0)
    for i in range(3):
        a.part('Mines', 'Armor').cyl(.13, .08, loc=(0, TAIL + .6 + i * .24, .66 - i * .13), rot=(-.55, 0, 0), seg=10,
                                     bevel=0)
    # The furrow plough on its arms with the depth wheel.
    pl = a.part('Plough', 'Steel')
    for s in (-1, 1):
        pl.limb((s * .55, TAIL, .55), (s * .4, TAIL + 1.15, .2), .05, .05, bevel=0)
    k.extrude(pl, [(-.2, 0), (.25, 0), (.1, .35), (-.15, .3)], .8, loc=(0, TAIL + 1.2, .02), axis='X', chamfer=.02)
    a.part('Plough_share', 'Undercarriage').box((.7, .3, .08), loc=(0, TAIL + 1.15, .04), rot=(.4, 0, 0), bevel=0)
    k.lathe(a.part('Plough_wheel', 'Rubber'), [(.12, -.06), (.18, -.05), (.18, .05), (.12, .06)],
            loc=(.62, TAIL + 1.05, .18), rot=(0, R90, 0), seg=10)
    for s in (-1, 1):
        a.part('Tail_lamps', 'LavaGlow').box((.08, .02, .05), loc=(s * .95, TAIL + .01, 1.1), bevel=0)
    C.stowage_box(a, (.4, .8, .24), (1.1, -1.6, .7), mat='Armor', latches=2)


def _running_gear(a):
    for s in (-1, 1):
        C.running_gear(a, s, TX, TW, WHEELS, WR, sprocket=(-2.95, .5, .24), idler=(2.55, .45, .23),
                       rollers=[(-2.0, .64), (-.6, .65), (.8, .65)], pitch=.22, disc_mat='Armor', wheel_w=.16, seg=8,
                       teeth=11)


def mine_layer(a, detail=False):
    """The mine layer: see the module docstring."""
    _hull(a)
    _cupola(a)
    _mines(a)
    _running_gear(a)
    K.dust(a, (0, TAIL + 1.1, .1), radius=1.0, k=.35)
    K.dust(a, (0, 0, .3), radius=3.5, k=.12)
    k.clean(a)


BUILDERS = {
    'mine_layer': (mine_layer, dict(ao_distance=.5, grime_height=.5)),
}
