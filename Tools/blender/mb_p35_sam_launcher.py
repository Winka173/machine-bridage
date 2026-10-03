"""Prompt 35 wave 4 (lane C): the SAM launcher rebuilt from scratch (spec: Tools/blender/specs/sam_launcher.json).

A 9A310 Buk TELAR (the def's modelSize 7.18 x 2.7 x 2.97 m): the long GM-569 tracked chassis with the crew cab
on the front (vision blocks, hatches), the engine louvres at the rear, six road wheels a side with the rear
sprocket, front idler and return rollers, side skirts over the top run; the turret platform over the middle and
rear with the Fire Dome engagement radar in its cylindrical housing at its front and the launcher cradle behind it
carrying the four 9M317 missiles on their rails, raised towards the target over the radar; the pintle 12.7 mm
on a raised post at the commander's hatch (`Mount_mg`, kept from the old file; the sheet lists it).

Runtime nodes kept: `Turret`, `Turret_body`, `Launcher_cradle`, `Launcher_face`, `Launcher_missiles`,
`Launcher_missiles_fins`, `Launcher_rails`, `Radar_array`, `Radar_dome`, `Muzzle_main`, `Mount_mg`, `Muzzle_mg`,
`Point_exhaust`, `Point_fire`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TX, TW = 1.02, .46
WR = .3
WHEELS = (-2.25, -1.38, -.51, .36, 1.23, 2.1)
TOP = 1.28
NOSE, TAIL = -3.55, 3.45
TUR = (0, .55, TOP)
EL = .18               # the missiles' elevation (radians)


def _hull(a):
    hull = a.part('Hull', 'Team')
    def sec(wl, zl, ws, zs, wt, zt):
        return [(0, zl), (wl, zl), (wl, zs - .1), (ws, zs), (wt, zt), (0, zt)]
    C.section_loft(hull, [
        (NOSE, sec(.6, .55, .7, .6, .62, .68)),
        (NOSE + .55, sec(.76, .36, 1.26, .68, 1.14, 1.05)),
        (-2.2, sec(.78, .34, 1.3, .7, 1.2, TOP)),
        (TAIL - .1, sec(.78, .34, 1.3, .7, 1.2, TOP)),
        (TAIL, sec(.76, .38, 1.28, .7, 1.18, TOP - .06)),
    ])
    for s in (-1, 1):
        sk = a.part('Skirts', 'Armor')
        for j in range(5):
            sk.box((.025, 1.06, .2), loc=(s * 1.29, -2.0 + j * 1.08, .62), bevel=0)
        a.part('Team_band', 'Team').box((.01, 3.4, .08), loc=(s * 1.25, .4, 1.05), rot=(0, s * .1, 0), bevel=0)
    # The crew cab across the front: a raised roof with vision blocks, two hatches; lamps, tow hooks.
    cab = a.part('Cab', 'Team')
    C.slab_loft(cab, [(-1.15, -2.75), (1.15, -2.75), (1.2, -1.45), (-1.2, -1.45)],
                [(-1.05, -2.5), (1.05, -2.5), (1.1, -1.5), (-1.1, -1.5)], TOP - .05, TOP + .25)
    gl = a.part('Glass', 'Glass')
    for x in (-.8, -.45, .45, .8):
        gl.box((.24, .02, .09), loc=(x, -2.66, TOP + .1), rot=(-.75, 0, 0), bevel=0)
    C.hatch(a, (.55, -2.0, TOP + .25), r=.24, periscope=True)
    C.hatch(a, (-.55, -2.0, TOP + .25), r=.24)
    K.pintle_mg(a, None, (-.55, -1.65, TOP + .25), post=.2, length=1.0)
    for s in (-1, 1):
        K.lamp(a, (s * 1.0, -2.85, 1.0), (0, -1, .25), r=.065, guard=True)
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .5, NOSE - .02, .5), facing=(0, -1, 0), size=.08)
    # The engine louvres and the exhaust at the rear, the rear plate's lamps and tow hook, stowage bins.
    K.grille(a, (0, 2.85, TOP + .02), 1.6, .7, facing=(0, 0, 1), slats=6, frame_mat='Team')
    K.grille(a, (1.22, 2.6, 1.0), .5, .2, facing=(1, 0, 0), slats=3, frame_mat='Team')
    # The TDA thermal smoke apparatus vents through the exhaust louvre (Soviet tracked chassis).
    a.part('Smoke_tda', 'Steel').box((.05, .34, .14), loc=(1.29, 2.6, .85), bevel=0)
    a.pivot('Point_exhaust', (1.28, 2.6, 1.0))
    for s in (-1, 1):
        a.part('Tail_lamps', 'LavaGlow').box((.08, .02, .05), loc=(s * 1.0, TAIL + .01, 1.1), bevel=0)
        C.stowage_box(a, (.3, .7, .24), (s * 1.05, -1.1, TOP - .02), mat='Armor', latches=1)
    K.tow_hook(a.part('Kit_steel', 'Steel'), (0, TAIL + .02, .55), facing=(0, 1, 0), size=.08)
    a.pivot('Point_fire', (0, 2.4, TOP + .3))


def _running_gear(a):
    for s in (-1, 1):
        C.running_gear(a, s, TX, TW, WHEELS, WR, sprocket=(2.95, .52, .26), idler=(-2.95, .5, .25),
                       rollers=[(-1.8, .72), (-.07, .72), (1.65, .72)], pitch=.22, hide_top=(-2.6, 2.7, .62),
                       disc_mat='Armor', wheel_w=.17, seg=8, teeth=12)


def _turret(a):
    t = a.pivot('Turret', TUR)
    K.turret_ring(a.part('Turret_ring', 'Armor'), TUR, .95, h=.05)
    body = a.part('Turret_body', 'Team', t)
    bot = [(-1.0, -1.3), (1.0, -1.3), (1.18, -1.05), (1.18, 2.4), (-1.18, 2.4), (-1.18, -1.05)]
    top = [(-.92, -1.2), (.92, -1.2), (1.1, -.98), (1.1, 2.3), (-1.1, 2.3), (-1.1, -.98)]
    C.slab_loft(body, bot, top, 0, .3)
    # The Fire Dome radar: the cylindrical housing standing on the platform's front, its flat array face forward.
    dome = a.part('Radar_dome', 'Team', t)
    k.lathe(dome, [(.62, .3), (.66, .35), (.66, 1.0), (.6, 1.1), (.3, 1.2), (0, 1.22)], loc=(0, -.6, 0), seg=16,
            worn=(1, 3))
    arr = a.part('Radar_array', 'Undercarriage', t)
    k.block(arr, (.95, .08, .72), loc=(0, -1.22, .36), chamfer=.015)
    a.part('Radar_rim', 'Armor', t).box((1.05, .06, .06), loc=(0, -1.24, 1.1), bevel=0)
    for s in (-1, 1):
        a.part('Kit_steel', 'Steel', t).box((.06, .5, .7), loc=(s * .5, -1.0, .7), bevel=0)
    # The launcher cradle on its trunnion frame behind the radar, the four missiles on their rails raised.
    fr = a.part('Launcher_frame', 'Steel', t)
    for s in (-1, 1):
        k.extrude(fr, [(-.4, 0), (.4, 0), (.15, .5), (-.15, .5)], .1, loc=(s * .85, 1.1, .3), axis='X', chamfer=.01)
    cradle = a.part('Launcher_cradle', 'Armor', t)
    cy, cz = 1.1, .88
    c, s_ = math.cos(EL), math.sin(EL)

    def along(d, x=0.0, up=0.0):
        """A point d metres forward along the raised launcher axis (and up off it)."""
        return (x, cy - d * c - up * s_, cz + d * s_ + up * c)
    k.block(cradle, (1.7, 3.0, .12), loc=along(.3, 0, -.12), rot=(EL, 0, 0), chamfer=.02)
    a.part('Cradle_trunnion', 'Steel', t).cyl(.1, 1.9, loc=(0, cy, cz - .05), rot=(0, R90, 0), seg=10, bevel=0)
    rails = a.part('Launcher_rails', 'Steel', t)
    mis = a.part('Launcher_missiles', 'Fuel', t)
    fins = a.part('Launcher_missiles_fins', 'Steel', t)
    for x in (-.62, -.21, .21, .62):
        rails.box((.08, 3.0, .06), loc=along(.3, x, .02), rot=(EL, 0, 0), bevel=0)
        k.lathe(mis, [(0, -2.6), (.07, -2.45), (.16, -2.1), (.17, -1.8), (.17, 2.0), (.15, 2.1), (.1, 2.12)],
                loc=along(.3 + .05, x, .22), rot=(R90 - EL + math.pi, 0, 0), seg=10, worn=(3,))
        for i in range(4):
            u = i * R90 + math.pi / 4
            for d, span, chord in ((-1.65, .22, .5), (1.85, .18, .28)):
                p = along(.35 - d, x, .22)
                fins.box((.01, chord, span), loc=(p[0] + math.cos(u) * (.17 + span / 2) * .9,
                                                  p[1] - math.sin(u) * (.17 + span / 2) * .9 * s_,
                                                  p[2] + math.sin(u) * (.17 + span / 2) * .9 * c),
                         rot=(EL, u - R90, 0), bevel=0)
        a.part('Missile_bands', 'Hazard', t).cyl(.175, .04, loc=along(.3 + 1.2, x, .22), rot=(R90 - EL, 0, 0), seg=10,
                                                  bevel=0)
    face = a.part('Launcher_face', 'Undercarriage', t)
    face.box((1.6, .02, .4), loc=along(2.95, 0, .22), rot=(EL, 0, 0), bevel=0)
    a.pivot('Muzzle_main', along(3.0, 0, .22), t)
    # Platform furniture: the cable trunk, the crew access ladder rungs, aerials, the team band.
    a.part('Kit_cables', 'Undercarriage', t).tube([(-.9, .2, .32), (-.95, .9, .5), (-.85, 1.1, 1.0)], .04, seg=5)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (1.0, 2.1, .3), h=.4)
    a.part('Team_band', 'Team', t).box((.01, 3.0, .08), loc=(1.15, .6, .15), bevel=0)
    a.part('Team_band', 'Team', t).box((.01, 3.0, .08), loc=(-1.15, .6, .15), bevel=0)


def sam_launcher(a, detail=False):
    """The SAM launcher: see the module docstring."""
    _hull(a)
    _running_gear(a)
    _turret(a)
    K.dust(a, (0, 0, .3), radius=3.5, k=.12)
    k.clean(a)


BUILDERS = {
    'sam_launcher': (sam_launcher, dict(ao_distance=.5, grime_height=.5)),
}
