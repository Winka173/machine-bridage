"""Prompt 35 wave 7 (lane C): the radar-guided anti-tank missile carrier rebuilt from scratch (spec:
Tools/blender/specs/radar_atgm_vehicle.json).

A 9P157-2 Khrizantema-S (the def's `khrizantema`; no unit_refs row, the old builders drew it; the def's modelSize
5.8 x 2.5 x 2.3 m, 0.8 x the real BMP-3 chassis): the low hull with the long flat glacis, the folded splash board
and the trim vane, six road wheels a side with the front idler, the rear sprocket and three return rollers, the
float boxes over the tracks, the raised rear deck with its grilles and the two rear doors with steps; no turret: the
launch assembly on a low turntable on the front roof (`Turret`), its cradle carrying the 1L32-1 guidance radar head
on a raised arm in the middle (`Radar`) and two launch rails with two missile tubes each; the operator's sight,
the driver's periscopes, smoke dischargers, a rack of reload tubes, bins and aerials.

Runtime nodes kept: `Turret`, `Radar`, `Radar_box`, `Muzzle_missile`, `Point_exhaust`, `Point_fire`. Metres, +Z up,
-Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TX, TW = .98, .42
WR = .27
WHEELS = (-1.72, -1.03, -.34, .35, 1.04, 1.73)
TOP = 1.2
NOSE, TAIL = -2.88, 2.78
TUR = (0, -.85, TOP)


def _hull(a):
    hull = a.part('Hull', 'Team')
    prof = [(NOSE, .5), (NOSE + .18, .66), (-1.2, TOP - .1), (1.0, TOP - .05), (1.18, TOP + .06), (TAIL - .04, TOP + .06),
            (TAIL, .42), (-2.45, .34)]
    k.extrude(hull, prof, 1.98, axis='X', chamfer=.045, corner=.02)
    low = a.part('Hull_lower', 'Armor')
    k.extrude(low, [(NOSE + .12, .48), (-2.4, .32), (2.65, .32), (2.69, .72)], (TX - TW / 2) * 2, axis='X',
              chamfer=.02)
    for s in (-1, 1):
        K.fender(a.part('Fenders', 'Team'), TX + .02, NOSE + .2, TAIL - .05, .82, .45, s, lip=.025)
        sk = a.part('Skirts', 'Armor')
        for j in range(4):
            K.plate(sk, (.13, 1.12, .27), loc=(s * (TX + .26), -1.7 + j * 1.16, .71), chamfer=.012)
        a.part('Team_band', 'Team').box((.012, 4.3, .05), loc=(s * (TX + .33), -.05, .78), bevel=0)
    # The folded splash board on the glacis, the driver's hatch with periscopes, lamps, tow hooks, smoke.
    g0, g1 = (NOSE + .18, .66), (-1.2, TOP - .1)
    ang = math.atan2(g1[1] - g0[1], g1[0] - g0[0])
    gy, gz = (g0[0] + g1[0]) / 2, (g0[1] + g1[1]) / 2
    K.plate(a.part('Trim_vane', 'Armor'), (1.85, .55, .035), loc=(0, gy - .15, gz + .03), rot=(ang, 0, 0),
            chamfer=.01)
    rib = a.part('Trim_vane_ribs', 'Armor')
    for x in (-.7, -.23, .23, .7):
        rib.box((.035, .52, .04), loc=(x, gy - .15, gz + .05), rot=(ang, 0, 0), bevel=0)
    C.hatch(a, (.55, -1.5, TOP - .1), r=.22, periscope=False)
    for x in (.3, .55, .8):
        K.periscope(a, (x, -1.74, TOP - .1), facing=(0, -1, .2), size=(.11, .06, .05))
    for s in (-1, 1):
        K.lamp(a, (s * .9, -1.62, TOP - .06), (0, -1, .15), r=.055, guard=True)
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .45, NOSE - .02, .5), facing=(0, -1, 0), size=.06)
        K.smoke_dischargers(a, .85, -1.3, TOP - .02, s, count=3)
    # The rear: doors with vision blocks and steps, the troop hatches, the raised engine deck with grilles.
    for s in (-1, 1):
        K.plate(a.part('Doors', 'Armor'), (.5, .04, .68), loc=(s * .3, TAIL + .02, .82), chamfer=.01)
        a.part('Glass', 'Glass').box((.12, .01, .07), loc=(s * .3, TAIL + .045, 1.02), bevel=0)
        K.handle(a.part('Kit_steel', 'Steel'), (s * .15, TAIL + .05, .78), (s * .15, TAIL + .05, .9), (0, 1, 0),
                 h=.035)
        k.block(a.part('Steps', 'Steel'), (.4, .18, .035), loc=(s * .3, TAIL + .12, .42), chamfer=0)
        C.hatch(a, (s * .45, 1.75, TOP + .06), r=.22)
        a.part('Tail_lamps', 'LavaGlow').box((.07, .02, .04), loc=(s * .92, TAIL, 1.14), bevel=0)
    K.grille(a, (0, 2.42, TOP + .08), 1.3, .4, facing=(0, 0, 1), slats=6, frame_mat='Team')
    K.grille(a, (.95, 1.0, TOP + .02), .32, .7, facing=(1, 0, .6), slats=4, frame_mat='Team')
    K.exhaust(a, (-1.0, .8, TOP - .05), r=.06, length=.25, direction=(-1, 0, .3), muffler=False, cap=False)
    a.pivot('Point_exhaust', (-1.18, .8, TOP))
    a.pivot('Point_fire', (0, 1.3, TOP + .3))
    # Reload tubes in a rack on the rear deck, bins on the rear fenders, a tow cable, aerials.
    rk = a.part('Racks', 'Steel')
    for x in (-.55, .55):
        rk.box((.06, .9, .05), loc=(x, .9, TOP + .1), bevel=0)
    tb = a.part('Reload_tubes', 'Armor')
    for i, x in enumerate((-.25, .0, .25)):
        tb.cyl(.08, 1.2, loc=(x, .9, TOP + .2), rot=K.FORWARD, seg=8, bevel=.01)
    a.part('Kit_straps', 'Steel').box((.8, .04, .03), loc=(0, .9, TOP + .28), bevel=0)
    for s in (-1, 1):
        C.stowage_box(a, (.32, .6, .22), (s * (TX + .06), 2.15, .9), mat='Armor', latches=2)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.8, 2.1, TOP + .06), h=.8)
    K.tow_cable(a.part('Tow_cable', 'Undercarriage'), [(-.9, -.7, TOP - .07), (-.9, .5, TOP - .05)], r=.022)


def _running_gear(a):
    for s in (-1, 1):
        C.running_gear(a, s, TX, TW, WHEELS, WR, sprocket=(2.43, .46, .24), idler=(-2.32, .47, .23),
                       rollers=[(-1.35, .78), (.0, .79), (1.4, .78)], pitch=.2, disc_mat='Armor',
                       wheel_w=.15, seg=9, teeth=12, idler_spokes=5, hide_top=(-2.0, 2.35, .74))
        arms = a.part('Suspension', 'Undercarriage')
        for y in WHEELS:
            C.wheel_arm(arms, s, TX - .17, y, WR, length=.28, back=1, r=.038)


def _launcher(a):
    t = a.pivot('Turret', TUR)
    k.lathe(a.part('Turntable', 'Armor', t), [(.62, 0), (.62, .07), (.5, .12), (0, .12)], seg=16, worn=(1,))
    # The cradle across the turntable: trunnion blocks, the cross beam; the radar arm and the two rails.
    cr = a.part('Cradle', 'Armor', t)
    for s in (-1, 1):
        K.chamfer_box(cr, (.18, .4, .3), loc=(s * .45, 0, .27), c=.03)
    k.lathe(cr, [(.07, -.55), (.07, .55)], loc=(0, 0, .36), rot=(0, R90, 0), seg=8)
    arm = a.part('Radar_arm', 'Steel', t)
    arm.limb((0, .1, .36), (0, -.05, .6), .06, .05, bevel=0)
    arm.limb((.12, .15, .2), (0, -.02, .52), .035, .035, bevel=0)
    r = a.pivot('Radar', (0, -.05, .62), t)
    rb = a.part('Radar_box', 'Team', r)
    K.chamfer_box(rb, (.52, .42, .36), loc=(0, 0, .14), c=.05)
    a.part('Radar_face', 'Undercarriage', r).box((.44, .02, .28), loc=(0, -.215, .15), bevel=0)
    k.lathe(a.part('Radar_dome', 'Glass', r), [(.12, 0), (.11, .06), (0, .09)], loc=(0, 0, .32), seg=10)
    lnch = a.part('Launcher', 'Team', t)
    tubes = a.part('Tubes', 'Undercarriage', t)
    caps = a.part('Tube_caps', 'Hazard', t)
    for s in (-1, 1):
        x = s * .62
        K.chamfer_box(lnch, (.12, 1.5, .12), loc=(x, -.1, .48), c=.02)        # the rail beam
        for dz in (.0, .18):
            k.lathe(a.part('Missiles', 'Team', t), [(.075, -.75), (.075, .75)], loc=(x, -.15, .6 + dz),
                    rot=K.FORWARD, seg=8)
            tubes.cyl(.065, .02, loc=(x, -.905, .6 + dz), rot=K.FORWARD, seg=8, bevel=0)
            caps.box((.15, .02, .03), loc=(x, -.92, .68 + dz), bevel=0)
        st = a.part('Kit_steel', 'Steel', t)
        for y in (-.6, .4):
            st.box((.17, .04, .32), loc=(x, y, .66), bevel=0)
    a.pivot('Muzzle_missile', (.62, -.95, .6), t)
    # The operator's sight on the turntable's rear, its glass.
    sg = a.part('Sight', 'Armor', t)
    K.chamfer_box(sg, (.26, .28, .22), loc=(-.25, .42, .23), c=.03)
    a.part('Glass', 'Glass', t).box((.18, .01, .09), loc=(-.25, .275, .26), bevel=0)


def radar_atgm_vehicle(a, detail=False):
    """The radar ATGM carrier: see the module docstring."""
    _hull(a)
    _running_gear(a)
    _launcher(a)
    K.dust(a, (0, 0, .3), radius=2.8, k=.12)
    k.clean(a)


BUILDERS = {
    'radar_atgm_vehicle': (radar_atgm_vehicle, dict(ao_distance=.45, grime_height=.5)),
}
