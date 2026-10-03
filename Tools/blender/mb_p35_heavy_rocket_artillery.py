"""Prompt 35 wave 9 (lane C): the heavy rocket artillery rebuilt from scratch (spec:
Tools/blender/specs/heavy_rocket_artillery.json).

The 9A52-2 Smerch on the MAZ-543M 8x8 (unit_refs: BM-30 Smerch, 9M55 300 mm, twelve tubes; the def's modelSize
10 x 2.44 x 3.03 m): the MAZ-543M's two cabs either side of the engine bay (the left one longer, with the crew
door), their raked windscreens, the grille between them; four axles in two pairs on lugged tyres with mud wings;
behind the cabs the stowed rammer frame and the cable reel; at the rear the turntable (`Turret`) with the
elevating cradle and the pack of twelve 300 mm tubes in three rows of four laid forward over the cabs (bands,
the guide rails, the hazard-banded muzzles, `Tubes`), the travel lock at the front, the rear stabilising jacks
and the spade; toolboxes, jerrycans, the spare wheel.

Runtime nodes kept: `Turret`, `Tubes`, `Muzzle_main`, the old file's `Mount_mg` / `Muzzle_mg` (plain pivots on the
left cab's roof; the def has no secondary), `Point_exhaust`, `Point_fire`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WR = .58
AXLES = (-3.05, -1.75, 1.6, 2.9)
TX = .83
FZ = 1.0             # frame top
NOSE, TAIL = -5.0, 4.95


def _cabs(a):
    for s in (-1, 1):
        x0 = s * .7
        ln = 1.85 if s > 0 else 1.5
        cab = a.part('Cab', 'Team')
        C.slab_loft(cab, [(x0 - .4, NOSE + .05), (x0 + .4, NOSE + .05), (x0 + .4, NOSE + ln), (x0 - .4, NOSE + ln)],
                    [(x0 - .32, NOSE + .5), (x0 + .32, NOSE + .5), (x0 + .3, NOSE + ln - .42),
                     (x0 - .3, NOSE + ln - .42)], FZ - .12, 2.28,
                    mid=([(x0 - .4, NOSE + .1), (x0 + .4, NOSE + .1), (x0 + .4, NOSE + ln), (x0 - .4, NOSE + ln)], 1.58))
        K.windscreen(a, [(x0 - .34, NOSE + .14, 1.64), (x0 + .34, NOSE + .14, 1.64), (x0 + .28, NOSE + .46, 2.2),
                         (x0 - .28, NOSE + .46, 2.2)], frame_mat='Team', wipers=1)
        gl = a.part('Glass', 'Glass')
        gl.box((.01, .55, .36), loc=(x0 + s * .37, NOSE + .95, 1.93), rot=(0, s * .1, 0), bevel=0)
        dr = a.part('Doors', 'Team')
        dr.box((.012, .65, .7), loc=(x0 + s * .405, NOSE + .95, 1.3), bevel=0)
        K.handle(a.part('Kit_steel', 'Steel'), (x0 + s * .415, NOSE + 1.15, 1.45), (x0 + s * .415, NOSE + 1.25, 1.45),
                 (s, 0, 0), h=.025, r=.01)
        K.mirror(a.part('Kit_steel', 'Steel'), (x0 + s * .38, NOSE + .3, 1.85), s, arm=.05, size=(.04, .02, .15))
        K.lamp(a, (x0 + s * .18, NOSE + .02, 1.1), (0, -1, 0), r=.075, guard=True)
        K.periscope(a, (x0, NOSE + .85, 2.28), facing=(0, -1, 0), size=(.14, .1, .08))
    eng = a.part('Hull', 'Team')
    C.slab_loft(eng, [(-.29, NOSE + .1), (.29, NOSE + .1), (.29, NOSE + 1.5), (-.29, NOSE + 1.5)],
                [(-.27, NOSE + .55), (.27, NOSE + .55), (.27, NOSE + 1.5), (-.27, NOSE + 1.5)], FZ - .2, FZ + .62)
    K.grille(a, (0, NOSE + .14, FZ + .05), .48, .3, facing=(0, -1, 0), slats=4, frame_mat='Steel')
    K.grille(a, (0, NOSE + .34, FZ + .4), .46, .42, facing=(0, -.87, .5), slats=5, frame_mat='Steel')
    bp = a.part('Bumper', 'Steel')
    K.chamfer_box(bp, (2.3, .12, .2), loc=(0, NOSE, FZ - .22), c=.03)
    for s in (-1, 1):
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .45, NOSE - .05, FZ - .26), facing=(0, -1, 0), size=.08)
    m = a.pivot('Mount_mg', (.7, NOSE + 1.4, 2.3))
    a.pivot('Muzzle_mg', (0, -.5, .2), m)


def _chassis(a):
    fr = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        fr.box((.16, 9.4, .3), loc=(s * .45, 0, FZ - .15), bevel=0)
    ax = a.part('Axles', 'Undercarriage')
    for y in AXLES:
        K.axle(ax, y, WR, TX - .1, r=.07)
        for s in (-1, 1):
            K.tread_wheel(a, (s * TX, y, WR), WR, .4, s, seg=12)
    wing = a.part('Mud_wings', 'Team')
    for y0, y1 in ((AXLES[0], AXLES[1]), (AXLES[2], AXLES[3])):
        for s in (-1, 1):
            K.plate(wing, (.46, y1 - y0 + 1.3, .04), loc=(s * (TX + .02), (y0 + y1) / 2, WR * 2 + .1), chamfer=.01)
    # The rammer frame and the cable reel behind the cabs, the crew bench box.
    rf = a.part('Racks', 'Steel')
    sq = [(-.02, -.02), (.02, -.02), (.02, .02), (-.02, .02)]
    k.sweep(rf, sq, [(-.9, -3.0, FZ + .1), (-.9, -3.0, FZ + 1.0), (.9, -3.0, FZ + 1.0), (.9, -3.0, FZ + .1)])
    C.cable_reel(a, (.6, -2.6, FZ + .25), r=.22, w=.4, axis='X')
    C.stowage_box(a, (1.0, .6, .45), (-.45, -2.55, FZ), mat='Team', latches=2)
    for s in (-1, 1):
        C.stowage_box(a, (.3, 1.1, .3), (s * .98, -.1, FZ - .5), mat='Team', latches=2)
    C.jerry_rack(a, (-1.02, .9, FZ - .5), count=2, axis='Y')
    K.tread_wheel(a, (.98, .95, FZ - .2), .42, .28, 1, seg=10, tyre='Spare_wheel', rim='Spare_wheel_rim')
    K.exhaust(a, (-.95, -2.35, FZ + .2), r=.07, length=.8, direction=(0, 0, 1))
    a.pivot('Point_exhaust', (-.95, -2.35, FZ + 1.05))
    a.pivot('Point_fire', (0, .5, FZ + .8))
    for s in (-1, 1):
        a.part('Tail_lamps', 'Lamp').box((.1, .02, .08), loc=(s * .95, TAIL - .02, FZ), bevel=0)
    # The rear jacks and the spade.
    jk = a.part('Outriggers', 'Steel')
    pads = a.part('Outrigger_pads', 'Steel')
    for s in (-1, 1):
        K.outrigger(jk, pads, (s * .45, TAIL - .5, FZ - .05), s, reach=.55, drop=.3, w=.14)
    k.block(a.part('Spade', 'Steel'), (1.6, .12, .45), loc=(0, TAIL - .05, .35), rot=(.25, 0, 0), chamfer=.02)


def _launcher(a):
    """The turntable, the cradle and the twelve tubes laid forward (`Turret`)."""
    t = a.pivot('Turret', (0, 2.6, FZ + .1))
    k.lathe(a.part('Turntable', 'Team', t), [(.9, 0), (.9, .12), (.75, .2), (0, .22)], seg=14, worn=(1,))
    cr = a.part('Cradle', 'Armor', t)
    for s in (-1, 1):
        k.extrude(cr, [(-.6, .15), (.5, .15), (.35, .95), (-.4, .9)], .1, loc=(s * .66, 0, .05), axis='X',
                  chamfer=.015, corner=.02)
    pitch = math.radians(2)
    rot = (R90 - pitch, 0, 0)
    d = (0, -math.cos(pitch), math.sin(pitch))
    L = 7.4
    tubes = a.part('Tubes', 'Team', t)
    bores = a.part('Tubes_bore', 'Undercarriage', t)
    marks = a.part('Tube_marks', 'Hazard', t)
    y0, z0 = 1.25, .95                # the pack's rear end (relative to the turntable)
    for row in range(3):
        for col in range(4):
            x = (col - 1.5) * .3
            z = z0 + row * .3
            k.lathe(tubes, [(.15, 0), (.15, L)], loc=(x, y0, z), rot=rot, seg=8, caps=(True, False))
            tip = (x, y0 + d[1] * L, z + d[2] * L)
            bores.cyl(.12, .02, loc=tip, rot=rot, seg=8, bevel=0)
            marks.cyl(.155, .1, loc=(x, tip[1] - d[1] * .2, tip[2] - d[2] * .2), rot=rot, seg=8, bevel=0)
    bands = a.part('Tube_bands', 'Steel', t)
    for f in (.12, .42, .72, .95):
        yy, zz = y0 + d[1] * L * f, z0 + .3 + d[2] * L * f
        bands.box((1.28, .08, .96), loc=(0, yy, zz), rot=(-pitch, 0, 0), bevel=0)
    rails = a.part('Rails', 'Steel', t)
    for s in (-1, 1):
        rails.box((.05, L, .05), loc=(s * .66, y0 + d[1] * L / 2, z0 + .3 + d[2] * L / 2), rot=(-pitch, 0, 0), bevel=0)
    a.pivot('Muzzle_main', (0, y0 + d[1] * (L + .05), z0 + .3 + d[2] * L), t)
    # The travel lock on the frame behind the cabs (the tubes rest on it), the layer's sight box.
    lk = a.part('Travel_lock', 'Steel')
    for s in (-1, 1):
        lk.limb((s * .5, -2.0, FZ), (s * .45, -2.0, FZ + .9), .05, .05, bevel=0)
    lk.box((1.1, .1, .08), loc=(0, -2.0, FZ + .92), bevel=0)
    k.block(a.part('Sight', 'Armor', t), (.2, .25, .25), loc=(.8, .2, .55), chamfer=.02)


def heavy_rocket_artillery(a, detail=False):
    """The 9A52-2 Smerch: see the module docstring."""
    _cabs(a)
    _chassis(a)
    _launcher(a)
    K.dust(a, (0, 0, .3), radius=4.6, k=.14)
    k.clean(a)


BUILDERS = {
    'heavy_rocket_artillery': (heavy_rocket_artillery, dict(ao_distance=.45, grime_height=.5)),
}
