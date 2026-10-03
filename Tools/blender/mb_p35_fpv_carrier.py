"""Prompt 35 wave 4 (lane C): the FPV drone carrier rebuilt from scratch (spec: Tools/blender/specs/fpv_carrier.json).

An RG-33L 6x6 MRAP (unit_refs' second vehicle; the lancet truck already is the Typhoon-K) carrying an FPV drone
launcher (the def's modelSize 7.41 x 2.04 x 2.88 m): the V-hull under the tall monocoque crew capsule with its big
armoured side windows and the steep windscreen, the engine hood ahead with its grille and the bull bar, the front
axle and the rear tandem with lugged tyres, the rear door with its step; on the rear roof the launcher box on its
turntable (`Turret`): a four-by-four grid of launch cells with lids, quadcopters ready in the open top row, the
control antenna mast; the M2 in a raised ring turret on the cab roof (the def's free `hmg_selfdef_18`).

Runtime nodes kept: `Turret`, `Muzzle_main`, `Mount_mg`, `Muzzle_mg`, `Point_exhaust`, `Point_fire` (the wrapper
adds `Part_wheel` / `Part_wheelb`). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WR = .48
AX = (-2.35, .95, 2.15)
TRACK = .78


def _hull(a):
    # The V-hull under everything, its deflector plates.
    v = a.part('Hull', 'Armor')
    C.section_loft(v, [(-1.6, [(0, .58), (.5, .7), (.82, .95), (.82, 1.1), (0, 1.1)]),
                       (3.5, [(0, .58), (.5, .7), (.82, .95), (.82, 1.1), (0, 1.1)])])
    # The crew capsule: tall, sides leaning in, the steep windscreen; the engine hood ahead of it.
    cab = a.part('Cab', 'Team')
    C.section_loft(cab, [
        (-1.55, [(0, 1.1), (.98, 1.1), (.92, 2.05), (.78, 2.25), (0, 2.28)]),
        (-1.0, [(0, 1.1), (1.0, 1.1), (.94, 2.2), (.8, 2.42), (0, 2.45)]),
        (3.55, [(0, 1.1), (1.0, 1.1), (.94, 2.2), (.8, 2.42), (0, 2.45)]),
    ])
    hood = a.part('Body', 'Team')
    C.section_loft(hood, [(-3.4, [(0, .9), (.82, .9), (.8, 1.45), (.6, 1.55), (0, 1.56)]),
                          (-1.5, [(0, .95), (.9, .95), (.88, 1.72), (.66, 1.85), (0, 1.86)])])
    K.grille(a, (0, -3.42, 1.22), 1.1, .45, facing=(0, -1, 0), slats=6, frame_mat='Team')
    bb = a.part('Bull_bar', 'Steel')
    k.sweep(bb, [(-.03, -.03), (.03, -.03), (.03, .03), (-.03, .03)],
            [(-.8, -3.45, .75), (-.8, -3.6, 1.0), (-.6, -3.62, 1.4), (.6, -3.62, 1.4), (.8, -3.6, 1.0), (.8, -3.45, .75)])
    for s in (-1, 1):
        K.lamp(a, (s * .62, -3.43, 1.45), (0, -1, 0), r=.07, guard=False)
        K.mirror(a.part('Kit_steel', 'Steel'), (s * .9, -1.4, 1.95), s, arm=.06)
    # Windows: the steep two-pane windscreen, the big side windows, the rear door's window.
    K.windscreen(a, [(-.92, -1.53, 1.75), (-.05, -1.53, 1.75), (-.05, -1.05, 2.22), (-.85, -1.05, 2.22)],
                 frame_mat='Team', wipers=1)
    K.windscreen(a, [(.05, -1.53, 1.75), (.92, -1.53, 1.75), (.85, -1.05, 2.22), (.05, -1.05, 2.22)],
                 frame_mat='Team', wipers=1)
    gl = a.part('Windows', 'Glass')
    for s in (-1, 1):
        for y in (-.6, .2, 1.0, 1.8):
            gl.box((.02, .5, .38), loc=(s * .965, y, 1.85), rot=(0, s * .055, 0), bevel=0)
        a.part('Team_band', 'Team').box((.012, 4.4, .09), loc=(s * .995, 1.0, 1.5), bevel=0)
        a.part('Tail_lamps', 'LavaGlow').box((.08, .02, .1), loc=(s * .8, 3.56, 1.4), bevel=0)
    door = a.part('Hatches', 'Armor')
    K.plate(door, (.8, .04, 1.2), loc=(0, 3.57, 1.65))
    gl.box((.36, .02, .3), loc=(0, 3.6, 1.95), bevel=0)
    st = a.part('Kit_steel', 'Steel')
    K.handle(st, (.3, 3.62, 1.7), (.3, 3.62, 1.85), (0, 1, 0), h=.04, r=.012)
    for z in (1.3, 2.1):
        K.hinge(st, (-.4, 3.6, z - .1), (-.4, 3.6, z + .1), r=.025, knuckles=2)
    k.block(a.part('Steps', 'Steel'), (.7, .25, .04), loc=(0, 3.68, .8), chamfer=0)
    # The exhaust stack beside the capsule, the side stowage bins, fuel tank.
    K.exhaust(a, (-1.0, -1.45, 1.8), r=.06, length=.7, direction=(0, 0, 1), muffler=True, cap=True)
    a.pivot('Point_exhaust', (-1.0, -1.45, 2.55))
    for s in (-1, 1):
        C.stowage_box(a, (.22, 1.0, .35), (s * .92, -.1, .78), mat='Armor', latches=2)
    k.block(a.part('Fuel_tank', 'Armor'), (.22, .9, .4), loc=(-.92, 1.55, .72), chamfer=.03)
    a.pivot('Point_fire', (0, .5, 2.0))


def _chassis(a):
    ax = a.part('Axles', 'Undercarriage')
    for y in AX:
        ax.cyl(.08, TRACK * 2 - .2, loc=(0, y, WR), rot=(0, R90, 0), seg=8, bevel=0)
        ax.box((.36, .36, .3), loc=(0, y, WR), bevel=0)
        for s in (-1, 1):
            C.lugged_tyre(a, (s * TRACK, y, WR), WR, .36, s, lugs=10, seg=12, nuts=4)
            ax.limb((s * .5, y - .3, .75), (s * .6, y, WR + .1), .05, .05, bevel=0)      # suspension arm
    a.part('Undercarriage', 'Undercarriage').box((.9, 5.6, .2), loc=(0, .1, .62), bevel=0)
    fl = a.part('Fender_flares', 'Undercarriage')
    for y in AX:
        for s in (-1, 1):
            fl.box((.3, 1.15, .04), loc=(s * .86, y, WR * 2 + .12), bevel=0)


def _launcher(a):
    """The FPV launcher box on its turntable on the rear roof (`Turret`): a 4 x 4 grid of cells."""
    t = a.pivot('Turret', (0, 2.25, 2.45))
    k.ring(a.part('Turret_ring', 'Armor'), [(.55, 0), (.6, 0), (.6, .08), (.55, .08)], loc=(0, 2.25, 2.45), seg=14)
    box = a.part('Launcher', 'Team', t)
    k.block(box, (1.5, 1.6, .06), loc=(0, 0, .06), chamfer=0)
    cells = a.part('Launch_cells', 'Armor', t)
    lids = a.part('Cell_lids', 'Armor', t)
    for i in range(4):
        for j in range(4):
            x, y = (i - 1.5) * .36, (j - 1.5) * .38
            cells.box((.33, .35, .22), loc=(x, y, .23), bevel=0)
            if j == 0:
                lids.box((.3, .02, .3), loc=(x, y - .2, .48), rot=(-.4, 0, 0), bevel=0)        # open lid
            else:
                lids.box((.3, .32, .02), loc=(x, y, .35), bevel=0)
    # Quadcopters ready in the open front row.
    dr = a.part('Drones', 'Undercarriage', t)
    for i in range(4):
        x = (i - 1.5) * .36
        dr.box((.08, .12, .05), loc=(x, -.57, .32), bevel=0)
        for dx, dy in ((-.1, -.1), (.1, -.1), (-.1, .1), (.1, .1)):
            dr.box((.12, .015, .01), loc=(x + dx, -.57 + dy, .35), rot=(0, 0, .8), bevel=0)
    a.pivot('Muzzle_main', (0, -.6, .45), t)
    mast = a.part('Antennas', 'Steel', t)
    K.whip_antenna(mast, (.7, .7, .1), h=.5)
    k.block(a.part('Antennas', 'Steel', t), (.25, .06, .3), loc=(-.6, .78, .1), chamfer=0)


def _gun(a):
    """The M2 in a raised ring turret on the cab roof (the free secondary)."""
    k.ring(a.part('Gun_ring', 'Armor'), [(.38, 0), (.45, 0), (.45, .12), (.4, .15)], loc=(0, -.4, 2.45), seg=14,
           worn=(2,))
    C.hatch(a, (0, .45, 2.45), r=.26)
    K.pintle_mg(a, None, (0, -.4, 2.52), post=.05, length=1.0)


def fpv_carrier(a, detail=False):
    """The FPV drone carrier: see the module docstring."""
    _hull(a)
    _chassis(a)
    _launcher(a)
    _gun(a)
    K.dust(a, (0, 0, .3), radius=3.5, k=.16)
    k.clean(a)


BUILDERS = {
    'fpv_carrier': (fpv_carrier, dict(ao_distance=.5, grime_height=.6)),
}
