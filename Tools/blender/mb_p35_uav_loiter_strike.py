"""Prompt 35 wave 7 (lane C): the loitering strike UAV rebuilt from scratch (spec: Tools/blender/specs/uav_loiter_strike.json).

An MQ-1C Gray Eagle (the old stand-in builder's reference; the def's modelSize 4.25 x 8.04 x 1.24 m): the slim
fuselage with the bulbous satcom nose and its access panels, the EO/IR ball under the chin, the heavy-fuel engine
bay with its dorsal intake, the cooler scoop and the exhaust stubs, the long straight high wing with flaperons and
tip lights, the inverted-V tail with the ventral fin, the three-blade pusher propeller (`Propeller`), and two pylons
with M299 twin rails carrying four Hellfires (`Muzzle_missile` on the right rail, `Muzzle_missile.001` on the left).
The stores are lane C's lean `store` (nose forward, two parts), so the file stays under the jet renderer cap.

Runtime nodes kept: `Propeller`, `Muzzle_missile`, `Muzzle_missile.001`, `Point_exhaust`, `Point_fire` (the wrapper
adds `Part_wing`). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WING_Z = .2
SPAN = 4.0


def _fuselage(a):
    body = a.part('Fuselage', 'Team')
    # Stations (y, half width, half height, centre z): the bulbous satcom nose rising above the slim body.
    st = [(-2.12, .03, .03, .0), (-2.08, .1, .1, .02), (-2.0, .15, .16, .04), (-1.9, .19, .21, .06), (-1.72, .23, .28, .1),
          (-1.5, .24, .3, .1), (-1.2, .22, .27, .07), (-.85, .2, .23, .03), (-.4, .19, .21, .01), (.1, .18, .2, 0.0),
          (.6, .17, .18, .0), (1.05, .14, .15, .0), (1.45, .1, .11, .0), (1.72, .07, .075, .0), (1.86, .05, .05, .0)]
    C.section_loft(body, [(y, C.ellipse_half(w, h, zc, 16)) for y, w, h, zc in st])
    # The EO/IR ball under the chin on its yoke, the window.
    a.part('Sensor', 'Armor').cyl(.05, .07, loc=(0, -1.55, -.2), seg=10, bevel=0)
    k.lathe(a.part('Sensor_ball', 'Armor'), [(0, -.12), (.07, -.11), (.1, -.05), (.105, 0), (.09, .05), (.04, .07),
                                            (0, .075)], loc=(0, -1.55, -.3), seg=20)
    a.part('Glass', 'Glass').box((.08, .02, .06), loc=(0, -1.655, -.31), bevel=0)
    # The engine bay: the dorsal intake, the ventral cooler scoop, the two exhaust stubs.
    K.intake(a.part('Intakes', 'Team'), a.part('Intake_ducts', 'Undercarriage'), (0, .55, .18), .14, .06, .26,
             facing=(0, -1, .3), lip=.01)
    K.intake(a.part('Intakes', 'Team'), a.part('Intake_ducts', 'Undercarriage'), (0, .9, -.15), .12, .05, .22,
             facing=(0, -1, -.3), lip=.01)
    for s in (-1, 1):
        k.lathe(a.part('Exhausts', 'Steel'), [(.025, 0), (.03, .09), (.024, .12)], loc=(s * .12, 1.3, -.02),
                rot=(R90 + .25, 0, s * .8), seg=8)
    K.soot(a, (0, 1.5, 0), radius=.3, k=.4)
    a.pivot('Point_exhaust', (0, 1.5, .02))
    a.pivot('Point_fire', (0, .2, .1))
    # Aerials: the satcom bump, blades; access panels; the Team bands.
    for y in (-.3, .3):
        K.blade_antenna(a.part('Antennas', 'Steel'), (0, y, .2), h=.09, chord=.08)
    K.blade_antenna(a.part('Antennas', 'Steel'), (0, -.8, -.22), h=.07, chord=.07, normal=(0, 0, -1))
    a.part('Antennas', 'Armor').cyl(.012, .5, loc=(.1, -1.0, -.1), rot=(0, R90 - .3, 0), seg=4, bevel=0)
    pn = a.part('Panels', 'Armor')
    for y, w in ((-1.45, .3), (-.9, .26), (-.2, .24), (.4, .22)):
        pn.box((w, .26, .01), loc=(0, y, .22 + (.08 if y < -1.2 else 0)), bevel=0)
    for s in (-1, 1):
        a.part('Team_band', 'Team').box((.01, .8, .05), loc=(s * .19, -.5, .0), bevel=0)
    k.lathe(a.part('Antennas', 'Steel'), [(.012, 0), (.012, .3), (.006, .38), (0, .38)], loc=(.6, -.5, WING_Z),
            rot=K.FORWARD, seg=6)                                                       # the pitot boom
    a.part('Lamps', 'Lamp').sphere(.025, loc=(0, -1.3, -.21), seg=8, rings=4)            # the landing lamp


def _wing(a):
    wing = a.part('Wings', 'Team')
    for s in (-1, 1):
        rings = []
        for f, lead, chord in ((0, -.52, .5), (.08, -.52, .5), (.2, -.51, .47), (.3, -.5, .44), (.42, -.485, .4),
                               (.55, -.47, .37), (.68, -.46, .335), (.8, -.45, .3), (.9, -.44, .27), (.97, -.433, .25),
                               (1.0, -.43, .24)):
            x = .12 + (SPAN - .12) * f
            ring = [(s * px, py, pz + math.tan(.03) * (SPAN - .12) * f) for px, py, pz in
                    K._foil_ring(lead, chord, .13, x, WING_Z)]
            rings.append(ring if s > 0 else list(reversed(ring)))
        wing.loft(rings, bevel=0)
        cs = a.part('Flaps', 'Armor')
        for x0, x1 in ((.4, 1.6), (1.7, 2.9), (3.0, 3.8)):
            f = ((x0 + x1) / 2 - .12) / (SPAN - .12)
            cs.box((x1 - x0, .07, .014), loc=(s * (x0 + x1) / 2, -.52 + (.5 - .26 * f) - .04,
                                             WING_Z + .01 + math.tan(.03) * (x0 + x1) / 2), bevel=0)
        a.part('Wing_lights', 'Lamp' if s > 0 else 'LavaGlow').box((.04, .05, .02),
                                                                    loc=(s * SPAN, -.33, WING_Z + .13), bevel=0)
        a.part('Team_band', 'Team').box((.35, .26, .005), loc=(s * 3.1, -.3, WING_Z + .11), bevel=0)
    # The wing root fairing over the fuselage.
    k.block(a.part('Wing_root', 'Team'), (.32, .6, .06), loc=(0, -.25, WING_Z + .03), chamfer=.02)


def _tail(a):
    tail = a.part('Tail', 'Team')
    for s in (-1, 1):
        K.fin(tail, (1.3, .42), (1.55, .22), -.72, x=s * .04, z0=-.04, t=.1, cant=-s * .78)
    K.fin(tail, (1.4, .3), (1.55, .18), -.42, x=0, z0=-.08, t=.1)
    rd = a.part('Rudders', 'Armor')
    for s in (-1, 1):
        rd.box((.02, .08, .4), loc=(s * .3, 1.75, -.36), rot=(0, -s * .78, 0), bevel=0)


def _propeller(a):
    pr = a.pivot('Propeller', (0, 1.96, 0))
    k.lathe(a.part('Fuselage', 'Team'), [(.05, -.1), (.06, 0), (.05, .1)], loc=(0, 1.87, 0), rot=K.BACKWARD, seg=12)
    k.lathe(a.part('Propeller_hub', 'Steel', pr), [(.07, -.04), (.08, 0), (.06, .09), (0, .16)], rot=K.BACKWARD,
            seg=14)
    bl = a.part('Propeller_blades', 'Armor', pr)
    for j in range(3):
        u0 = j * math.tau / 3 + .3
        d = (math.cos(u0), math.sin(u0))
        rings = []
        for r, chord, tw in ((.06, .07, .62), (.13, .078, .54), (.2, .08, .47), (.27, .076, .41), (.34, .068, .35),
                             (.41, .058, .3), (.47, .045, .26), (.52, .028, .22)):
            rings.append([(d[0] * r, chord * math.cos(tw) * uu, d[1] * r + chord * math.sin(tw) * uu + .01 * vv)
                          for uu, vv in ((-1, 0), (0, 1), (1, 0), (0, -1))])
        bl.loft(rings, bevel=0)


def _stores(a):
    py = a.part('Pylons', 'Armor')
    rk = a.part('Racks', 'Steel')
    for s, mname in ((1, 'Muzzle_missile__001'), (-1, 'Muzzle_missile')):
        x = s * 1.55
        K.pylon(py, x, -.5, -.18, WING_Z - .02, WING_Z - .14, w=.05)
        rk.box((.16, .5, .03), loc=(x, -.33, WING_Z - .16), bevel=0)
        for dx in (-.055, .055):
            C.store(a, (x + dx, .02, WING_Z - .21), .034, .7, kind='missile', seg=10)
        a.pivot(mname, (x, -.72, WING_Z - .21))


def uav_loiter_strike(a, detail=False):
    """The loitering strike UAV: see the module docstring."""
    K.suffixed(a)
    _fuselage(a)
    _wing(a)
    _tail(a)
    _propeller(a)
    _stores(a)
    k.clean(a)


BUILDERS = {
    'uav_loiter_strike': (uav_loiter_strike, dict(ao_distance=.2, ao_strength=.15, ground=False)),
}
