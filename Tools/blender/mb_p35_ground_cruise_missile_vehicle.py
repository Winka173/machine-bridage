"""Prompt 35 wave 9 (lane C): the ground cruise missile vehicle rebuilt from scratch (spec:
Tools/blender/specs/ground_cruise_missile_vehicle.json).

A Typhon-class ground-launched cruise missile launcher (balance.json: the Typhon MRC-class stand-in; drawn as the
Typhon launcher's four-cell Mk 41 box on an FMTV-class 6x6 so one vehicle carries it, the def's modelSize 7.18 x
2.7 x 2.97 m): the flat-fronted cab-forward FMTV cab with its split windscreen, doors, mirrors, the grille, bumper
and lamps; the ladder frame on three axles with big lugged tyres, wings and mud flaps; on the bed the turntable
(`Turret`) with the erector cradle and the 2 x 2 Mk 41 cell box lying forward (its cell hatches on the front face,
the stiffening ribs, the lifting eyes, the team band), the erecting rams at the rear; the launcher's control
box and generator behind the cab, the rear outrigger jacks, toolboxes, jerrycans, the spare wheel.

Runtime nodes kept: `Turret`, `Muzzle_main` (the cell box's front face), `Point_exhaust`, `Point_fire`
(the wrapper adds `Part_wheel` / `Part_wheelb`). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WR = .52
AXLES = (-2.4, .95, 2.25)
TX = .95
FZ = .98
NOSE, TAIL = -3.55, 3.55


def _cab(a):
    cab = a.part('Cab', 'Team')
    C.section_loft(cab, [
        (NOSE, [(0, FZ - .2), (1.15, FZ - .2), (1.18, 1.55), (1.12, 1.62), (0, 1.62)]),
        (NOSE + .5, [(0, FZ - .2), (1.2, FZ - .2), (1.22, 1.6), (.9, 2.62), (0, 2.65)]),
        (NOSE + 1.65, [(0, FZ - .2), (1.2, FZ - .2), (1.22, 1.6), (.92, 2.66), (0, 2.68)]),
    ])
    for s in (-1, 1):
        K.windscreen(a, [(.05, NOSE + .14, 1.72), (1.0, NOSE + .14, 1.72), (.78, NOSE + .46, 2.55), (.05, NOSE + .46, 2.55)]
                     if s > 0 else
                     [(-1.0, NOSE + .14, 1.72), (-.05, NOSE + .14, 1.72), (-.05, NOSE + .46, 2.55), (-.78, NOSE + .46, 2.55)],
                     frame_mat='Team', wipers=1)
        a.part('Glass', 'Glass').box((.01, .6, .4), loc=(s * 1.09, NOSE + 1.05, 2.12), rot=(0, s * .3, 0), bevel=0)
        dr = a.part('Doors', 'Team')
        dr.box((.012, .02, .85), loc=(s * 1.225, NOSE + 1.35, 1.45), bevel=0)
        dr.box((.012, .02, .85), loc=(s * 1.225, NOSE + .45, 1.45), bevel=0)
        K.handle(a.part('Kit_steel', 'Steel'), (s * 1.23, NOSE + 1.1, 1.6), (s * 1.23, NOSE + 1.2, 1.6), (s, 0, 0),
                 h=.025, r=.01)
        K.mirror(a.part('Kit_steel', 'Steel'), (s * 1.17, NOSE + .3, 1.95), s, arm=.08, size=(.06, .02, .25))
        K.lamp(a, (s * .9, NOSE - .01, 1.2), (0, -1, 0), r=.075, guard=True)
        a.part('Steps', 'Steel').box((.1, .45, .03), loc=(s * 1.15, NOSE + .9, .7), bevel=0)
    K.grille(a, (0, NOSE - .01, 1.25), 1.2, .45, facing=(0, -1, 0), slats=6, frame_mat='Steel')
    bp = a.part('Bumper', 'Steel')
    K.chamfer_box(bp, (2.4, .14, .22), loc=(0, NOSE - .03, FZ - .22), c=.03)
    for s in (-1, 1):
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .5, NOSE - .09, FZ - .26), facing=(0, -1, 0), size=.08)
    C.hatch(a, (.4, NOSE + 1.0, 2.66), r=.24, mat='Team')
    K.exhaust(a, (1.1, NOSE + 1.75, 1.6), r=.06, length=1.0, direction=(0, 0, 1))
    a.pivot('Point_exhaust', (1.1, NOSE + 1.75, 2.65))


def _chassis(a):
    fr = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        fr.box((.16, 6.9, .28), loc=(s * .45, 0, FZ - .14), bevel=0)
    ax = a.part('Axles', 'Undercarriage')
    for y in AXLES:
        K.axle(ax, y, WR, TX - .1, r=.065)
        for s in (-1, 1):
            K.tread_wheel(a, (s * TX, y, WR), WR, .4, s, seg=12)
    for s in (-1, 1):
        a.part('Mud_wings', 'Team').box((.46, 2.5, .04), loc=(s * (TX + .02), 1.6, WR * 2 + .1), bevel=0)
        a.part('Mudflaps', 'Rubber').box((.4, .02, .32), loc=(s * (TX + .02), 2.87, .6), bevel=0)
        a.part('Tail_lamps', 'Lamp').box((.1, .02, .07), loc=(s * 1.0, TAIL - .02, FZ), bevel=0)
        C.stowage_box(a, (.3, .9, .3), (s * 1.05, -.6, FZ - .5), mat='Team', latches=2)
    C.jerry_rack(a, (-1.12, 1.6, FZ + .05), count=2, axis='Y')
    K.tread_wheel(a, (1.1, 1.6, FZ + .25), .42, .28, 1, seg=10, tyre='Spare_wheel', rim='Spare_wheel_rim')
    jk = a.part('Outriggers', 'Steel')
    pads = a.part('Outrigger_pads', 'Steel')
    for s in (-1, 1):
        K.outrigger(jk, pads, (s * .45, TAIL - .35, FZ - .05), s, reach=.6, drop=.35, w=.15)
    a.pivot('Point_fire', (0, .6, 2.0))


def _bed(a):
    """The bed, the control box and generator behind the cab."""
    bed = a.part('Bed', 'Team')
    k.extrude(bed, [(-1.2, -1.8), (1.2, -1.8), (1.2, TAIL), (-1.2, TAIL)], .08, loc=(0, 0, FZ + .04), axis='Z',
              chamfer=.01, corner=.02, caps=(False, True))
    ctl = a.part('Body', 'Team')
    C.slab_loft(ctl, C.octagon(2.3, .9, .06, y0=-1.4), C.octagon(1.7, .6, .08, y0=-1.4), FZ + .08, 2.3)
    K.grille(a, (.85, -1.4, FZ + .75), .5, .4, facing=(1, 0, 0), slats=4, frame_mat='Team')
    K.door(a, (-1.1, -1.4, FZ + .2), size=(.45, .8), normal=(-1, 0, 0), mat='Team')
    K.whip_antenna(a.part('Antennas', 'Steel'), (.7, -1.5, 2.3), h=.5, r=.014)


def _launcher(a):
    """The turntable, the cradle and the four-cell Mk 41 box lying forward (`Turret`)."""
    t = a.pivot('Turret', (0, 1.62, FZ + .12))
    k.lathe(a.part('Turret_base', 'Steel', t), [(.75, 0), (.75, .08), (.6, .14), (0, .15)], seg=14, worn=(1,))
    cr = a.part('Turret_steel', 'Steel', t)
    for s in (-1, 1):
        k.extrude(cr, [(-.9, .1), (1.0, .1), (.9, .4), (-.8, .38)], .08, loc=(s * .7, 0, 0), axis='X', chamfer=.01)
    W, H, L = 1.55, 1.25, 4.4
    box = a.part('Launcher_box', 'Team', t)
    cz = .42 + H / 2
    C.slab_loft(box, [(-W / 2, -L / 2 - .3), (W / 2, -L / 2 - .3), (W / 2, L / 2 - .3), (-W / 2, L / 2 - .3)],
                [(-W / 2 + .1, -L / 2 - .3), (W / 2 - .1, -L / 2 - .3), (W / 2 - .1, L / 2 - .3),
                 (-W / 2 + .1, L / 2 - .3)], .42, .42 + H,
                mid=([(-W / 2, -L / 2 - .3), (W / 2, -L / 2 - .3), (W / 2, L / 2 - .3), (-W / 2, L / 2 - .3)], .42 + H - .15))
    yf = -L / 2 - .3
    hp = a.part('Launcher_hatches', 'Armor', t)
    hf = a.part('Launcher_hatch_fittings', 'Steel', t)
    for cx in (-.37, .37):
        for zz in (cz - .3, cz + .28):
            k.block(hp, (.6, .05, .5), loc=(cx, yf - .025, zz), chamfer=.012)       # centred on its cell
            hf.box((.08, .03, .08), loc=(cx, yf - .06, zz + .2), bevel=0)
            hf.box((.4, .02, .03), loc=(cx, yf - .055, zz), bevel=0)
    rib = a.part('Launcher_ribs', 'Steel', t)
    for f in (-.35, -.1, .15, .4):
        rib.box((W + .04, .06, .05), loc=(0, f * L - .3, .42 + H - .1), bevel=0)
        for s in (-1, 1):
            rib.box((.04, .06, H - .15), loc=(s * (W / 2 + .01), f * L - .3, .42 + (H - .15) / 2), bevel=0)
    for s in (-1, 1):
        for y in (-1.6, 1.0):
            K.handle(a.part('Launcher_handles', 'Steel', t), (s * .55, y, .42 + H + .01), (s * .55, y + .12, .42 + H + .01),
                     (0, 0, 1), h=.05, r=.012)
    a.part('Launcher_band', 'Team', t).box((.02, 1.6, .2), loc=(W / 2 + .03, -.4, cz + .3), bevel=0)
    a.part('Launcher_hazard', 'Hazard', t).box((W - .1, .02, .08), loc=(0, yf - .01, .42 + H - .05), bevel=0)
    a.pivot('Muzzle_main', (0, yf - .08, cz), t)
    # Play-test 13 (lane B): the box is an erector. Everything on it is named Launcher_* so ModelLibrary puts it on
    # the runtime `Elevation` pivot; the pivot lands 6 % in from the box's rear and 30 % up it (C.elevation_pivot),
    # and the trunnion, its lugs and the brackets are built exactly there, so the box swings up about its rear
    # hinge to fire (VehicleView Erectors: raised 80 degrees from this flat travel pose) and lies down to drive.
    hx, hy, hz = C.elevation_pivot(a, t)
    a.part('Launcher_hinge', 'Steel', t).cyl(.07, 1.9, loc=(hx, hy, hz), rot=(0, R90, 0), seg=10, bevel=0)
    lug = a.part('Launcher_lugs', 'Armor', t)
    rr = a.part('Launcher_rams', 'Steel', t)
    for s in (-1, 1):
        lug.box((.04, .3, .32), loc=(s * (W / 2 + .035), hy, hz), bevel=0)
        # The erecting rams along the box's sides, their feet at the hinge brackets.
        rr.limb((s * .86, hy - .35, hz - .05), (s * .86, .1, hz + .38), .08, .08, bevel=0)
        rr.limb((s * .86, .1, hz + .38), (s * .86, -.7, hz + .5), .05, .05, bevel=0)
    # The fixed frame on the turntable and the hinge brackets standing on it (they stay down when the box rises).
    fr = a.part('Turret_frame', 'Steel', t)
    K.chamfer_box(fr, (2.0, 1.0, .07), loc=(0, hy - .15, .185), c=.02)
    br = a.part('Turret_brackets', 'Armor', t)
    for s in (-1, 1):
        k.extrude(br, [(hy - .45, .22), (hy + .3, .22), (hy + .14, hz + .12), (hy - .14, hz + .12)], .05,
                  loc=(s * .9, 0, 0), axis='X')


def ground_cruise_missile_vehicle(a, detail=False):
    """The Typhon-class cruise missile launcher: see the module docstring."""
    _cab(a)
    _chassis(a)
    _bed(a)
    _launcher(a)
    K.dust(a, (0, 0, .3), radius=3.4, k=.14)
    k.clean(a)


BUILDERS = {
    'ground_cruise_missile_vehicle': (ground_cruise_missile_vehicle, dict(ao_distance=.45, grime_height=.5)),
}
