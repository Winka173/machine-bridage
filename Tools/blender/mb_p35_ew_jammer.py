"""Prompt 35 wave 9 (lane C): the EW jammer rebuilt from scratch (spec: Tools/blender/specs/ew_jammer.json).

The Krasukha-4 on the BAZ-6910-022 8x8 (unit_refs: Krasukha-4, Leer-3; the def's modelSize 9.01 x 2.76 x 3.83
m): the BAZ's forward crew cab with its flat raked windscreen, four doors and side windows, the grille and bumper
below, lamps and mirrors; four axles in two pairs on lugged tyres with wings; the long equipment van behind it
(side doors, ladders, the air-conditioning units and generator grilles, cable reels in their lockers); on the
van's rear the jammer's big curved reflector on its turning pedestal (`Radar`: the reflector with its ribs, the
feed boom and the horn cluster) and the folded telescopic mast along the roof; the self-defence 12.7 mm standing
on its post on the cab roof (`Turret`, the def's main hmg_selfdef_15, MODEL_STANDARD "Roof guns"); whips,
toolboxes, the spare wheel.

Runtime nodes kept: `Turret`, `Muzzle_main` (the roof gun's), `Radar`, `Point_exhaust`, `Point_fire`. Metres,
+Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WR = .58
AXLES = (-2.95, -1.6, 1.35, 2.7)
TX = .96
FZ = 1.0
NOSE, TAIL = -4.5, 4.5
VAN_TOP = 2.95


def _cab(a):
    cab = a.part('Cab', 'Team')
    C.section_loft(cab, [
        (NOSE, [(0, FZ - .2), (1.2, FZ - .2), (1.22, 1.55), (1.15, 1.62), (0, 1.62)]),
        (NOSE + .55, [(0, FZ - .2), (1.24, FZ - .2), (1.25, 1.6), (1.02, 2.82), (0, 2.85)]),
        (NOSE + 2.0, [(0, FZ - .2), (1.24, FZ - .2), (1.25, 1.6), (1.04, 2.86), (0, 2.88)]),
    ])
    K.windscreen(a, [(-1.05, NOSE + .06, 1.7), (1.05, NOSE + .06, 1.7), (.9, NOSE + .5, 2.7), (-.9, NOSE + .5, 2.7)],
                 frame_mat='Team', wipers=2)
    for s in (-1, 1):
        gl = a.part('Glass', 'Glass')
        for y in (NOSE + .85, NOSE + 1.6):
            gl.box((.01, .55, .42), loc=(s * 1.15, y, 2.15), rot=(0, s * .18, 0), bevel=0)
        dr = a.part('Doors', 'Team')
        for y in (NOSE + .85, NOSE + 1.6):
            dr.box((.012, .02, .75), loc=(s * 1.255, y + .36, 1.35), bevel=0)
            K.handle(a.part('Kit_steel', 'Steel'), (s * 1.26, y + .15, 1.55), (s * 1.26, y + .25, 1.55), (s, 0, 0),
                     h=.025, r=.01)
        K.mirror(a.part('Kit_steel', 'Steel'), (s * 1.18, NOSE + .2, 2.05), s, arm=.08, size=(.05, .02, .18))
        K.lamp(a, (s * .9, NOSE - .01, 1.25), (0, -1, 0), r=.08, guard=True)
        st = a.part('Steps', 'Steel')
        st.box((.1, .5, .03), loc=(s * 1.2, NOSE + .85, .7), bevel=0)
    K.grille(a, (0, NOSE - .01, 1.25), 1.2, .4, facing=(0, -1, 0), slats=5, frame_mat='Steel')
    bp = a.part('Bumper', 'Steel')
    K.chamfer_box(bp, (2.5, .14, .22), loc=(0, NOSE - .02, FZ - .25), c=.03)
    for s in (-1, 1):
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .5, NOSE - .08, FZ - .3), facing=(0, -1, 0), size=.08)
    # The self-defence 12.7 mm on its post on the cab roof (the def's main weapon).
    C.roof_gun(a, (.45, NOSE + 1.35, 2.87), pivot='Turret', barrel='Main_cannon', brake='Muzzle_brake',
               muzzle='Muzzle_main', post=.3, length=1.1, scale=.9, shield=True, mat='Team')


def _chassis(a):
    fr = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        fr.box((.18, 8.6, .3), loc=(s * .5, .1, FZ - .15), bevel=0)
    ax = a.part('Axles', 'Undercarriage')
    for i, y in enumerate(AXLES):
        K.axle(ax, y, WR, TX - .1, r=.07, diff=i in (1, 3))
        for s in (-1, 1):
            K.tread_wheel(a, (s * TX, y, WR), WR, .42, s, seg=12)
    wing = a.part('Mud_wings', 'Team')
    for y in AXLES[1:]:
        for s in (-1, 1):
            wing.box((.5, 1.4, .04), loc=(s * (TX + .03), y, WR * 2 + .1), bevel=0)
    K.exhaust(a, (1.15, NOSE + 2.15, FZ + .3), r=.07, length=1.0, direction=(0, 0, 1))
    a.pivot('Point_exhaust', (1.15, NOSE + 2.15, FZ + 1.35))
    a.pivot('Point_fire', (0, .5, VAN_TOP))
    for s in (-1, 1):
        a.part('Tail_lamps', 'Lamp').box((.12, .02, .08), loc=(s * 1.05, TAIL - .02, FZ), bevel=0)
        C.stowage_box(a, (.32, 1.0, .32), (s * 1.05, -.15, FZ - .55), mat='Team', latches=2)
    K.tread_wheel(a, (-1.05, 2.05, FZ - .2), .45, .3, -1, seg=10, tyre='Spare_wheel', rim='Spare_wheel_rim')


def _van(a):
    y0, y1 = NOSE + 2.15, TAIL - .1
    van = a.part('Body', 'Team')
    C.slab_loft(van, C.octagon(2.5, y1 - y0, .1, y0=(y0 + y1) / 2), C.octagon(2.2, y1 - y0 - .2, .14,
                                                                             y0=(y0 + y1) / 2),
                FZ + .05, VAN_TOP, mid=(C.octagon(2.5, y1 - y0, .1, y0=(y0 + y1) / 2), VAN_TOP - .3))
    st = a.part('Kit_steel', 'Steel')
    for s in (-1, 1):
        for y in (-1.3, .2, 1.7, 3.2):
            st.box((.02, .04, 1.6), loc=(s * 1.255, y, FZ + .9), bevel=0)
    K.door(a, (1.255, -.5, FZ + .2), size=(.7, 1.3), normal=(1, 0, 0), mat='Team')
    K.door(a, (0, y1 + .01, FZ + .2), size=(.8, 1.4), normal=(0, 1, 0), mat='Team')
    K.ladder(a.part('Ladders', 'Steel'), (-.6, y1 + .06, FZ + .1), (-.6, y1 + .06, VAN_TOP), width=.4, step=.3)
    # Air-conditioning units and generator grilles, lockers with cable reels.
    for i, y in enumerate((-1.5, 2.6)):
        k.block(a.part('Air_con', 'Armor'), (.8, .6, .3), loc=(-.4 if i else .4, y, VAN_TOP + .15), chamfer=.03)
        K.grille(a, (-.4 if i else .4, y, VAN_TOP + .31), .6, .4, facing=(0, 0, 1), slats=4, frame_mat='Armor')
    for s in (-1, 1):
        K.grille(a, (s * 1.255, 2.4, FZ + .7), .9, .5, facing=(s, 0, 0), slats=5, frame_mat='Team')
    C.cable_reel(a, (-1.0, .9, FZ - .35), r=.22, w=.35, axis='X')
    # The folded telescopic mast along the roof and its cradle, the whips.
    ms = a.part('Masts', 'Steel')
    ms.cyl(.09, 3.0, loc=(.7, .7, VAN_TOP + .2), rot=K.FORWARD, seg=8, bevel=0)
    ms.cyl(.065, .5, loc=(.7, -.95, VAN_TOP + .2), rot=K.FORWARD, seg=8, bevel=0)
    for y in (-.6, 1.9):
        ms.box((.25, .08, .2), loc=(.7, y, VAN_TOP + .08), bevel=0)
    for x, y in ((-1.0, -1.3), (1.0, 3.6)):
        K.whip_antenna(a.part('Antennas', 'Steel'), (x, y, VAN_TOP), h=.75, r=.015)
    rl = a.part('Railings', 'Steel')
    rl.tube([(-1.1, -1.85, VAN_TOP + .25), (-1.1, 4.3, VAN_TOP + .25)], .02, seg=4)
    for y in (-1.8, 0, 1.8, 3.6):
        rl.limb((-1.1, y, VAN_TOP), (-1.1, y, VAN_TOP + .25), .015, .015, bevel=0)


def _reflector(a):
    """The jammer's curved reflector on its turning pedestal (`Radar`)."""
    k.lathe(a.part('Radar_base', 'Armor'), [(.55, 0), (.55, .12), (.45, .18), (0, .2)], loc=(0, 3.0, VAN_TOP), seg=12)
    r = a.pivot('Radar', (0, 3.0, VAN_TOP + .2))
    a.part('Radar_mast', 'Steel', r).cyl(.12, .35, loc=(0, 0, .17), seg=8, bevel=0)
    tilt = math.radians(64)            # the reflector lies back (its face to the sky behind)
    face = a.part('Radar_dish', 'Armor', r)
    w, h, sag = 2.5, 1.5, .25
    cols, rows = 6, 3
    verts, faces = [], []
    for j in range(rows + 1):
        for i in range(cols + 1):
            u = i / cols - .5
            v = j / rows
            x = u * w
            yz = sag * (4 * u * u)                     # curved across: the edges forward
            zz = .15 + v * h
            y = -yz + (zz - .15) * math.sin(tilt)
            verts.append((x, y, zz * math.cos(tilt) + .15 * (1 - math.cos(tilt))))
    for j in range(rows):
        for i in range(cols):
            q = j * (cols + 1) + i
            faces.append((q, q + 1, q + cols + 2, q + cols + 1))
    n = len(verts)
    verts += [(x, y + .05, z) for x, y, z in verts]
    faces += [tuple(n + i for i in reversed(f)) for f in faces]
    face.mesh(verts, faces)
    rib = a.part('Radar_ribs', 'Steel', r)
    for i in range(cols + 1):
        p = [verts[j * (cols + 1) + i] for j in range(rows + 1)]
        rib.tube([(x, y + .08, z) for x, y, z in p], .025, seg=4)
    a.part('Radar_feed', 'Steel', r).limb((0, .1, .35), (0, -.9, .75), .04, .04, bevel=0)
    hc = a.part('Radar_horns', 'Undercarriage', r)
    for dx in (-.15, .15):
        for dz in (-.1, .1):
            k.extrude(hc, [(-.06, -.05), (.06, -.05), (.1, .08), (-.1, .08)], .2, loc=(dx, -.95, .75 + dz),
                      axis='Y', chamfer=0)
    a.part('Team_band', 'Team', r).box((2.0, .12, .02), loc=(0, .75, .78), rot=(tilt - R90 + R90, 0, 0), bevel=0)


def ew_jammer(a, detail=False):
    """The Krasukha-4: see the module docstring."""
    _cab(a)
    _chassis(a)
    _van(a)
    _reflector(a)
    K.dust(a, (0, 0, .3), radius=4.2, k=.14)
    k.clean(a)


BUILDERS = {
    'ew_jammer': (ew_jammer, dict(ao_distance=.45, grime_height=.5)),
}
