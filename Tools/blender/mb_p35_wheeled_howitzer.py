"""Prompt 35 wave 11 (lane C): the CAESAR wheeled howitzer rebuilt from scratch (spec: Tools/blender/specs/wheeled_howitzer.json).

The CAESAR 6x6 (the def's caesar_155, modelSize 8.0 x 2.1 x 3.0 m: about 0.8 x the real 10 m truck). Kept from the
fix L8 build (DECISIONS "Sửa lỗi tổng hợp L8"): the forward armoured cab with the crew compartment behind it, the
long gun platform with its lockers, the travel-lock A-frame behind the cab carrying the barrel, the gun mount with
trunnion cheeks, recoil cylinders and cradle, the 52-calibre barrel with its double-baffle brake, the firing spade
on its arms, the node places. New to prompt 35's standard: the cab as a lofted body (raked armoured windscreen in a
frame, side windows, four doors with handles and steps, the grille, lamps under guards, mirrors, the roof hatch,
whips and the beacon), the ladder frame on three axles with leaf springs and lugged tyres under proper wings, the
fuel tank and air tanks, the exhaust behind the cab, the breech ring with its block, loading tray and rammer,
the elevating arcs and equilibrators, the gun layer's sight and seat, the rear jacks beside the spade, the ready
ammunition lockers with hinged lids, a stowed cleaning staff, jerrycans and a tarp.

Runtime nodes kept where they were: `Turret` (0, 2.3, 1.2), `Main_cannon`, `Muzzle_brake`, `Muzzle_main`
(0, -3.96, 2.51), `Point_exhaust` (.85, -1.9, 2.0), `Point_fire` (0, 0, 1.4). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WR = .46
AXLES = (-2.6, 1.15, 2.55)
TX = .76
FZ = .9
NOSE, TAIL = -3.75, 3.95
CAB0, CAB1 = NOSE + .05, NOSE + 2.85     # the cab and crew compartment


def _cab(a):
    cab = a.part('Cab', 'Team')
    half = [(0, FZ), (.98, FZ), (1.0, 1.6), (.92, 2.08), (.8, 2.16), (0, 2.18)]
    low = [(0, FZ + .05), (.95, FZ + .05), (.97, 1.5), (.94, 1.55), (.85, 1.57), (0, 1.57)]
    mid = [(0, FZ), (.98, FZ), (1.0, 1.6), (.96, 1.68), (.86, 1.7), (0, 1.7)]
    C.section_loft(cab, [(CAB0, low), (CAB0 + .12, mid), (CAB0 + .62, half), (CAB1, half)])
    K.grille(a, (0, CAB0 + .01, 1.3), 1.2, .4, facing=(0, -1, 0), slats=7, frame_mat='Steel')
    for s in (-1, 1):
        K.windscreen(a, [(s * .04, CAB0 + .16, 1.76), (s * .82, CAB0 + .16, 1.76), (s * .74, CAB0 + .58, 2.08),
                         (s * .04, CAB0 + .58, 2.08)][::s], frame_mat='Armor', wipers=1)
        K.lamp(a, (s * .78, CAB0 - .02, 1.1), (0, -1, 0), r=.075, guard=True)
        for wy in (CAB0 + 1.0, CAB0 + 2.1):
            a.part('Glass', 'Glass').box((.01, .45, .26), loc=(s * .995, wy, 1.83), bevel=0)
            a.part('Window_frames', 'Armor').box((.02, .52, .33), loc=(s * .99, wy, 1.83), bevel=0)
        dr = a.part('Doors', 'Team')
        for y in (CAB0 + .62, CAB0 + 1.4, CAB0 + 1.6, CAB0 + 2.6):
            dr.box((.012, .02, .9), loc=(s * 1.0, y, 1.38), bevel=0)
        for y in (CAB0 + 1.25, CAB0 + 2.4):
            K.handle(a.part('Kit_handles', 'Steel'), (s * 1.005, y, 1.5), (s * 1.005, y + .1, 1.5), (s, 0, 0),
                     h=.025, r=.01)
            a.part('Steps', 'Steel').box((.12, .45, .03), loc=(s * .94, y - .1, .62), bevel=0)
        K.mirror(a.part('Kit_steel', 'Steel'), (s * .95, CAB0 + .5, 1.95), s, arm=.04, size=(.04, .02, .2))
    bp = a.part('Bumper', 'Steel')
    K.chamfer_box(bp, (1.9, .15, .22), loc=(0, NOSE - .02, FZ - .12), c=.03)
    for s in (-1, 1):
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .45, NOSE - .1, FZ - .18), facing=(0, -1, 0), size=.07)
    C.hatch(a, (.35, CAB0 + 1.9, 2.18), r=.26)
    ant = a.part('Antennas', 'Steel')
    K.whip_antenna(ant, (-.75, CAB1 - .15, 2.18), h=.75, r=.02, lean=.1)
    K.whip_antenna(ant, (.75, CAB1 - .15, 2.18), h=.7, r=.02, lean=.1)
    K.beacon(a, (-.4, CAB0 + 1.2, 2.18), r=.07)
    a.part('Team_band', 'Team').box((.02, 1.2, .2), loc=(1.005, CAB0 + 1.9, 1.15), bevel=0)


def _chassis(a):
    fr = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        fr.box((.14, 7.4, .22), loc=(s * .42, .1, FZ - .11), bevel=0)
    ax = a.part('Axles', 'Undercarriage')
    for y in AXLES:
        K.axle(ax, y, WR, TX - .1, r=.06)
        for s in (-1, 1):
            K.tread_wheel(a, (s * TX, y, WR), WR, .34, s, seg=12)
    for s in (-1, 1):
        K.leaf_spring(a.part('Leaf_springs', 'Undercarriage'), s * .42, 1.85, WR + .17, 1.7, leaves=3)
        K.leaf_spring(a.part('Leaf_springs', 'Undercarriage'), s * .42, AXLES[0], WR + .17, 1.1, leaves=3)
        wing = a.part('Mud_wings', 'Team')
        wing.box((.36, 2.2, .04), loc=(s * (TX + .02), 1.85, WR * 2 + .1), bevel=0)
        wing.box((.04, 2.2, .18), loc=(s * (TX + .19), 1.85, WR * 2 + .02), bevel=0)
        a.part('Tail_lamps', 'LavaGlow').box((.12, .02, .07), loc=(s * .85, TAIL - .02, FZ + .05), bevel=0)
    k.lathe(a.part('Fuel_tank', 'Steel'), [(.2, -.45), (.2, .45)], loc=(-.72, -.55, FZ - .25), rot=K.FORWARD, seg=12)
    for dy in (-.55, -.2):
        a.part('Air_tanks', 'Steel').cyl(.09, .32, loc=(.7, dy, FZ - .25), rot=K.FORWARD, seg=8, bevel=0)
    K.exhaust(a, (.85, -1.9, 1.0), r=.05, length=1.0, direction=(0, 0, 1))
    a.pivot('Point_exhaust', (.85, -1.9, 2.0))
    a.pivot('Point_fire', (0, 0, 1.4))


def _platform(a):
    """Gun platform, lockers, travel lock, stowage."""
    y0 = CAB1
    plat = a.part('Bed', 'Armor')
    k.extrude(plat, [(-1.0, y0), (1.0, y0), (1.0, TAIL - .3), (-1.0, TAIL - .3)], .5, loc=(0, 0, FZ + .25),
              axis='Z', chamfer=.03, corner=.04)
    k.block(a.part('Deck_plate', 'MetalSheet'), (1.8, TAIL - .4 - y0, .03), loc=(0, (y0 + TAIL - .3) / 2, FZ + .515),
            chamfer=0)
    lk = a.part('Lockers', 'Team')
    lids = a.part('Lockers', 'Team')
    for s in (-1, 1):
        k.block(lk, (.42, 2.0, .62), loc=(s * .78, y0 + 1.25, FZ + .5 + .31), chamfer=.03)
        for i in range(3):
            yy = y0 + .55 + i * .66
            lids.box((.012, .58, .5), loc=(s * .995, yy, FZ + .81), bevel=0)
            a.part('Kit_latches', 'Steel').box((.02, .06, .05), loc=(s * 1.0, yy, FZ + 1.0), bevel=0)
    # Travel lock A-frame just behind the cab, the barrel lying in its cradle.
    tl = a.part('Travel_lock', 'Steel')
    for s in (-1, 1):
        tl.limb((s * .5, y0 + .15, FZ + .5), (s * .06, y0 + .15, 2.06), .07, .07, bevel=0)
    k.block(tl, (.36, .2, .14), loc=(0, y0 + .15, 2.1), chamfer=.02)
    tl.limb((0, y0 + .15, FZ + .5), (0, y0 + .7, FZ + .5), .06, .06, bevel=0)
    C.jerry_rack(a, (-.25, y0 + .45, FZ + .52), count=2, axis='X')
    K.net_roll(a.part('Tarp', 'Canvas'), a.part('Kit_straps', 'Steel'), (.35, y0 + .5, FZ + .65), length=.6, r=.1,
               axis='X')
    k.lathe(a.part('Cleaning_staff', 'Wood'), [(.025, 0), (.025, 2.2), (0, 2.2)], loc=(.6, y0 + 2.4, FZ + 1.17),
            rot=K.FORWARD, seg=5)
    # Rear jacks beside the spade, the spade on its arms.
    for s in (-1, 1):
        K.outrigger(a.part('Outriggers', 'Steel'), a.part('Jack_pads', 'Undercarriage'), (s * .45, 3.2, FZ),
                    s, reach=.45, drop=.55, w=.16)
    sp = a.part('Spade', 'Armor')
    k.extrude(sp, [(-.95, 0), (.95, 0), (.8, .85), (.25, .95), (-.25, .95), (-.8, .85)], .14, loc=(0, 3.85, .25),
              rot=(R90 + .35, 0, 0), axis='Z', chamfer=.02, corner=.03)
    ribs = a.part('Spade', 'Armor')
    for x in (-.5, 0, .5):
        ribs.box((.05, .1, .7), loc=(x, 3.95, .62), rot=(-.35, 0, 0), bevel=0)
    for s in (-1, 1):
        a.part('Spade_arms', 'Steel').limb((s * .6, 3.15, FZ), (s * .6, 3.78, .6), .12, .12, bevel=0)
        a.part('Spade_arms', 'Steel').limb((s * .25, 3.1, FZ + .1), (s * .25, 3.85, .85), .07, .07, bevel=0)


def _gun(a):
    """The gun mount on its pivot (Turret): cheeks, cradle, recoil cylinders, barrel, breech, tray, sight."""
    t = a.pivot('Turret', (0, 2.3, 1.2))
    k.block(a.part('Mount', 'Team', t), (1.5, 1.3, .4), loc=(0, .1, .2), chamfer=.05)
    k.lathe(a.part('Elevating_arcs', 'Steel', t), [(.6, 0), (.66, 0), (.66, .06), (.6, .06)], loc=(0, .1, .0), seg=14)
    cheeks = a.part('Cheeks', 'Armor', t)
    for s in (-1, 1):
        k.extrude(cheeks, [(-.6, .4), (.6, .4), (.45, 1.15), (-.2, 1.2), (-.6, .8)], .12, loc=(s * .45, 0, 0),
                  axis='X', chamfer=.02, corner=.02)
        # The elevating arc and the equilibrator on each cheek.
        arc = a.part('Elevating_arcs', 'Steel', t)
        pts = [(s * .53, -.2 + .5 * math.sin(u), .9 - .5 * math.cos(u)) for u in
               (math.radians(v) for v in (-10, 15, 40, 65))]
        for p0, p1 in zip(pts, pts[1:]):
            arc.limb(p0, p1, .05, .08, bevel=0)
        a.part('Elevating_arcs', 'Steel', t).limb((s * .55, .4, .45), (s * .55, -.35, 1.02), .09, .09, bevel=0)
    pitch = math.radians(4)
    k.block(a.part('Cradle', 'Armor', t), (.5, 1.6, .34), loc=(0, -.3, .78), chamfer=.04, ends=(True, True))
    rot = (R90 - pitch, 0, 0)
    L = 5.6
    r = .09
    y0, z0 = -.4, .9
    k.lathe(a.part('Main_cannon', 'Steel', t), [(r * 1.4, 0), (r * 1.4, 1.2), (r * 1.1, 1.3), (r, 1.4), (r * .9, L),
                                                 (0, L)], loc=(0, y0, z0), rot=rot, seg=12, worn=(1, 3))
    dz = math.sin(pitch)
    dy = -math.cos(pitch)

    def along(f, up=0.0):
        return (0, y0 + dy * f + dz * up * 0, z0 + dz * f + up)
    k.lathe(a.part('Main_cannon_evacuator', 'Steel', t), [(r * .98, -.18), (r * 1.45, -.12), (r * 1.45, .12),
                                                           (r * .98, .18)], loc=along(L * .55), rot=rot, seg=12,
            worn=(1, 2))
    bp = a.part('Muzzle_brake', 'Steel', t)
    for j, f in enumerate((L + .1, L + .32)):
        k.lathe(bp, [(r * .9, -r * .9), (r * 1.7, -r * .8), (r * 1.7, r * .8), (r * .9, r * .9)], loc=along(f),
                rot=rot, seg=12, worn=(1, 2))
    bp.cyl(r * .95, .5, loc=along(L + .21), rot=rot, seg=12, bevel=0)
    a.pivot('Muzzle_main', (0, -.4 - 5.875 * math.cos(pitch), .9 + 5.875 * math.sin(pitch)), t)
    rec = a.part('Recoil_cylinders', 'Steel', t)
    for s in (-1, 1):
        k.lathe(rec, [(0, 0), (.06, 0), (.06, 1.5), (0, 1.5)], loc=(s * .18, .3, 1.08), rot=rot, seg=8)
    br = a.part('Breech', 'Steel', t)
    k.block(br, (.42, .5, .42), loc=(0, .55, .72), chamfer=.04, ends=(True, True))
    k.block(br, (.3, .12, .3), loc=(0, .86, .72), chamfer=.02, ends=(True, True))
    a.part('Loading_tray', 'Steel', t).box((.3, .7, .05), loc=(0, 1.2, .55), rot=(-.1, 0, 0), bevel=0)
    a.part('Rammer', 'Undercarriage', t).cyl(.07, .6, loc=(.25, 1.1, .6), rot=K.FORWARD, seg=8, bevel=0)
    K.periscope(a, (-.62, -.2, 1.2), facing=(0, -1, 0), parent=t, size=(.16, .2, .16))
    seat = a.part('Rammer', 'Undercarriage', t)
    seat.box((.3, .3, .06), loc=(-.75, .35, .5), bevel=0)
    seat.box((.3, .05, .3), loc=(-.75, .5, .65), bevel=0)
    K.soot(a, (0, -3.96, 2.51), radius=.5, k=.35)


def wheeled_howitzer(a, detail=False):
    """The CAESAR wheeled howitzer: see the module docstring."""
    _cab(a)
    _chassis(a)
    _platform(a)
    _gun(a)
    K.dust(a, (0, 0, .3), radius=3.6, k=.14)
    k.clean(a)


BUILDERS = {
    'wheeled_howitzer': (wheeled_howitzer, dict(ao_distance=.45, grime_height=.45)),
}
