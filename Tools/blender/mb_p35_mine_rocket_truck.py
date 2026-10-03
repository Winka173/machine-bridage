"""Prompt 35 wave 11 (lane C): the remote mine-laying rocket truck rebuilt from scratch (spec: Tools/blender/specs/mine_rocket_truck.json).

The ISDM Zemledeliye pattern (two 25-tube 122 mm packages that scatter mine-carrying rockets) on a three-axle
cab-over truck of the KamAZ-5350 family, sized to the def's modelSize 6.09 x 2.0 x 2.6 m: the flat-fronted cab with
its grille, bumper, lamps, the two-pane windscreen behind folding armoured shutters, doors, steps and mirrors; the
ladder frame on a front axle and the rear tandem with lugged tyres, mud wings, the fuel tank, battery box and air
tanks, the exhaust stack behind the cab and the spare wheel; on the rear deck the turntable (`Turret`) carrying the
elevating cradle and the two launch packages, each a 5 x 5 block of tubes with their mouths, end frames, lifting
eyes and stencil bands, raised a little over the cab; two rear stabiliser jacks, a ladder, jerrycans, a toolbox and
a tarp roll. No gun (the def's weapon is none: the mines are a special ability).

Runtime nodes kept where they were: `Turret` (0, 1.25, 1.22), `Muzzle_main` (0, -.45, 2.1, the packages' face),
`Point_exhaust` (.85, 2.9, 1.0), `Point_fire` (0, 1.0, 1.3); old names kept (`Tubes`, `Tubes_bore`, `Hatches`).
Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WR = .44
AXLES = (-1.85, .95, 2.15)
TX = .76
FZ = .86
NOSE, TAIL = -3.0, 3.05


def _cab(a):
    cab = a.part('Cab', 'Team')
    y0, y1 = NOSE + .05, NOSE + 1.55
    CW = .92 / .99           # the cab's outline below is drawn 1.98 m wide, narrowed to 1.84 m
    C.section_loft(cab, [(y, [(x * CW, z) for x, z in half]) for y, half in (
        (y0, [(0, FZ + .05), (.95, FZ + .05), (.97, 1.7), (.93, 1.75), (.85, 1.76), (0, 1.76)]),
        (y0 + .1, [(0, FZ), (.98, FZ), (.99, 1.75), (.96, 1.85), (.88, 1.88), (0, 1.88)]),
        (y0 + .45, [(0, FZ), (.98, FZ), (.99, 1.75), (.96, 2.3), (.88, 2.44), (0, 2.46)]),
        (y1, [(0, FZ), (.98, FZ), (.99, 1.75), (.96, 2.3), (.88, 2.44), (0, 2.46)]))])
    K.grille(a, (0, NOSE + .02, 1.25), 1.1, .38, facing=(0, -1, 0), slats=6, frame_mat='Steel')
    # Two-pane windscreen and its folding armoured shutters, raised.
    for s in (-1, 1):
        K.windscreen(a, [(s * .05, NOSE + .19, 1.92), (s * .8, NOSE + .19, 1.92), (s * .76, NOSE + .44, 2.36),
                         (s * .05, NOSE + .44, 2.36)][::s], frame_mat='Team', wipers=1)
        sh = a.part('Shutters', 'Armor')
        K.plate(sh, (.78, .04, .34), loc=(s * .45, NOSE + .38, 2.55), rot=(-1.3, 0, 0), chamfer=.006)
        a.part('Kit_hinges', 'Steel').cyl(.02, .7, loc=(s * .45, NOSE + .48, 2.46), rot=(0, R90, 0), seg=6, bevel=0)
        K.lamp(a, (s * .72, NOSE - .02, 1.05), (0, -1, 0), r=.075, guard=True)
        a.part('Glass', 'Glass').box((.01, .5, .32), loc=(s * .915, NOSE + .85, 1.98), bevel=0)
        dr = a.part('Doors', 'Team')
        dr.box((.012, .02, .9), loc=(s * .92, NOSE + 1.2, 1.5), bevel=0)
        dr.box((.012, .02, .9), loc=(s * .92, NOSE + .45, 1.5), bevel=0)
        K.handle(a.part('Kit_steel', 'Steel'), (s * .925, NOSE + 1.0, 1.6), (s * .925, NOSE + 1.1, 1.6), (s, 0, 0),
                 h=.025, r=.01)
        K.mirror(a.part('Kit_steel', 'Steel'), (s * .9, NOSE + .25, 2.05), s, arm=.05, size=(.04, .02, .18))
        st = a.part('Steps', 'Steel')
        st.box((.14, .4, .03), loc=(s * .84, NOSE + .8, .62), bevel=0)
        st.box((.14, .4, .03), loc=(s * .84, NOSE + .8, .32), bevel=0)
    bp = a.part('Bumper', 'Steel')
    K.chamfer_box(bp, (1.86, .14, .22), loc=(0, NOSE - .02, FZ - .12), c=.03)
    for s in (-1, 1):
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .4, NOSE - .1, FZ - .18), facing=(0, -1, 0), size=.07)
    a.part('Sun_visor', 'Team').box((1.6, .25, .03), loc=(0, NOSE + .5, 2.47), rot=(-.25, 0, 0), bevel=0)
    rf = a.part('Roof_kit', 'Steel')
    rf.box((.5, .3, .1), loc=(-.4, NOSE + 1.0, 2.5), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (.7, NOSE + 1.35, 2.46), h=.25, r=.02, lean=.12)
    K.beacon(a, (-.4, NOSE + 1.0, 2.55), r=.07)


def _chassis(a):
    fr = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        fr.box((.14, 5.9, .22), loc=(s * .42, .05, FZ - .11), bevel=0)
    ax = a.part('Axles', 'Undercarriage')
    for y in AXLES:
        K.axle(ax, y, WR, TX - .1, r=.06)
        for s in (-1, 1):
            K.tread_wheel(a, (s * TX, y, WR), WR, .34, s, seg=12)
    for s in (-1, 1):
        K.leaf_spring(a.part('Leaf_springs', 'Undercarriage'), s * .42, 1.55, WR + .17, 1.6, leaves=3)
        a.part('Mud_wings', 'Team').box((.4, 2.1, .04), loc=(s * (TX + .02), 1.55, WR * 2 + .08), bevel=0)
        a.part('Mud_wings', 'Team').box((.4, .9, .04), loc=(s * (TX + .02), AXLES[0], WR * 2 + .06), bevel=0)
        a.part('Tail_lamps', 'LavaGlow').box((.12, .02, .07), loc=(s * .85, TAIL, FZ - .05), bevel=0)
    # Fuel tank and battery box on the right, air tanks on the left.
    k.lathe(a.part('Fuel_tank', 'Steel'), [(.22, -.4), (.22, .4)], loc=(-.72, -.6, FZ - .25), rot=K.FORWARD, seg=12)
    C.stowage_box(a, (.36, .5, .32), (.75, -.6, FZ - .52), mat='Undercarriage', name='Battery_box')
    for dy in (-.1, .25):
        a.part('Air_tanks', 'Steel').cyl(.1, .5, loc=(.68, dy + .2, FZ - .2), rot=K.FORWARD, seg=8, bevel=0)
    # Exhaust stack behind the cab, the spare wheel.
    K.exhaust(a, (.85, NOSE + 1.65, 1.0), r=.05, length=1.5, direction=(0, 0, 1))
    a.pivot('Point_exhaust', (.85, 2.9, 1.0))
    a.pivot('Point_fire', (0, 1.0, 1.3))
    K.tread_wheel(a, (-.3, NOSE + 1.75, 1.35), .38, .26, 1, seg=10, tyre='Spare_wheel', rim='Spare_wheel_rim')
    a.part('Kit_racks', 'Steel').box((.6, .08, .9), loc=(-.3, NOSE + 1.68, 1.25), bevel=0)
    # Rear stabiliser jacks.
    for s in (-1, 1):
        K.outrigger(a.part('Outriggers', 'Steel'), a.part('Jack_pads', 'Undercarriage'), (s * .5, 2.75, FZ - .05), s,
                    reach=.42, drop=.6, w=.16)


def _deck(a):
    deck = a.part('Body', 'Team')
    k.extrude(deck, [(-1.0, -1.35), (1.0, -1.35), (1.0, TAIL), (-1.0, TAIL)], .1, loc=(0, 0, FZ + .05), axis='Z',
              chamfer=.012, corner=.02, caps=(False, True))
    for s in (-1, 1):
        K.plate(deck, (.04, 4.3, .22), loc=(s * 1.0, .85, FZ + .18), chamfer=.006)
    C.jerry_rack(a, (-.65, -1.15, FZ + .1), count=3, axis='X')
    C.stowage_box(a, (.6, .35, .3), (.55, -1.15, FZ + .1), name='Toolbox')
    K.net_roll(a.part('Tarp', 'Canvas'), a.part('Kit_straps', 'Steel'), (0, 2.85, FZ + .22), length=1.7, r=.11)
    K.ladder(a.part('Ladders', 'Steel'), (.0, TAIL + .02, .45), (.0, TAIL + .02, FZ + .1), width=.3, step=.2)


def _launcher(a):
    """The turntable, the elevating cradle and the two 25-tube packages (`Turret`)."""
    t = a.pivot('Turret', (0, 1.25, 1.22))
    k.lathe(a.part('Turntable', 'Steel', t), [(.7, -.2), (.7, -.12), (.6, -.06), (.45, 0)], seg=14, worn=(1,))
    cr = a.part('Turret_cradle', 'Armor', t)
    for s in (-1, 1):
        k.extrude(cr, [(-.6, 0), (.6, 0), (.45, .38), (-.4, .32)], .08, loc=(s * .55, .2, 0), axis='X',
                  chamfer=.015)
    cr.box((1.2, .9, .1), loc=(0, .2, .02), bevel=0)
    pitch = math.radians(7)
    # The packages' face sits on Muzzle_main (0, -1.7, .88 from the pivot); 3.3 m long boxes.
    face = (0, -1.7, .88)
    Lp = 3.3
    d = (0, math.cos(pitch), -math.sin(pitch))                 # from the face backwards
    centre = (0, face[1] + d[1] * Lp / 2, face[2] + d[2] * Lp / 2)
    rot = (-pitch, 0, 0)
    box = a.part('Tubes', 'Team', t)
    bore = a.part('Tubes_bore', 'Undercarriage', t)
    frm = a.part('Pack_frames', 'Steel', t)
    pw, ph = .82, .78
    for s in (-1, 1):
        cx = s * .43
        k.block(box, (pw, Lp, ph), loc=(cx, centre[1], centre[2]), rot=rot, chamfer=.03, ends=(True, True))
        for f in (.04, .5, .96):
            c = (cx, face[1] + d[1] * Lp * f, face[2] + d[2] * Lp * f)
            frm.box((pw + .05, .08, ph + .05), loc=c, rot=rot, bevel=0)
        # 5 x 5 tube mouths on the front face.
        for i in range(5):
            for j in range(5):
                x = cx + (i - 2) * .15
                z = face[2] + (j - 2) * .145
                y = face[1] - .005 + (z - face[2]) * math.tan(pitch)
                bore.cyl(.058, .04, loc=(x, y, z), rot=(R90 - pitch, 0, 0), seg=6, bevel=0)
        band = a.part('Stencil_bands', 'Hazard', t)
        band.box((pw + .01, .12, ph + .01), loc=(cx, face[1] + d[1] * .35, face[2] + d[2] * .35), rot=rot, bevel=0)
        eyes = a.part('Lift_eyes', 'Steel', t)
        for f in (.2, .8):
            c = (cx, face[1] + d[1] * Lp * f, face[2] + d[2] * Lp * f + ph / 2 + .03)
            k.ring(eyes, [(.04, -.01), (.06, -.01), (.06, .01), (.04, .01)], loc=c, rot=(0, R90, 0), seg=6)
    # Elevation rams from the cradle to the packages.
    for s in (-1, 1):
        a.part('Rams', 'Steel', t).limb((s * .2, -.3, .05), (s * .2, -.9, .62), .07, .07, bevel=0)
    a.part('Hatches', 'Steel', t).box((.5, .3, .03), loc=(0, centre[1] + .6, centre[2] + ph / 2 + .02), rot=rot,
                                      bevel=0)
    a.pivot('Muzzle_main', face, t)
    K.soot(a, (0, -.45, 2.1), radius=.6, k=.25)


def mine_rocket_truck(a, detail=False):
    """The mine-laying rocket truck: see the module docstring."""
    _cab(a)
    _chassis(a)
    _deck(a)
    _launcher(a)
    K.dust(a, (0, 0, .3), radius=3.0, k=.14)
    k.clean(a)


BUILDERS = {
    'mine_rocket_truck': (mine_rocket_truck, dict(ao_distance=.4, grime_height=.45)),
}
