"""Prompt 35 wave 4 (lane C): the anti-aircraft gun tank rebuilt from scratch (spec: Tools/blender/specs/aa_vehicle.json).

A Flakpanzer Gepard (the def's modelSize 6.44 x 3.06 x 2.92 m): the Leopard 1 hull (wedge nose with the upper
glacis, vertical sides behind steel skirts, seven road wheels a side, the front idler and the rear sprocket,
the engine deck with its grilles); the big box turret with the two Oerlikon KDA 35 mm guns in armoured mounts
outside its cheeks (feed covers, ribbed barrels, muzzle velocity radars at their tips), the round tracking radar
dish on the turret front, the wide search radar turning on its mast over the turret rear (`Radar`), the two
banks of four smoke dischargers; the twin Stinger box on its own pivot on the rear roof (the def's free `sam`
secondary, `Mount_missile`: an upgrade, the real Gepard carries no missiles).

Runtime nodes kept: `Turret`, `Main_cannon`, `Main_cannon_2`, `Muzzle_brake`, `Muzzle_brake_2`, `Muzzle_main`,
`Radar`, `Radar_dish`, `Radar_mast`, `Launcher_box`, `Muzzle_missile` (+ `Mount_missile`, which the old file lacked),
`Point_exhaust`, `Point_fire`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TX, TW = 1.12, .48
WR = .3
WHEELS = (-1.95, -1.3, -.65, 0.0, .65, 1.3, 1.95)
TOP = 1.06
NOSE, TAIL = -2.92, 2.88
TUR = (0, -.2, TOP)


def _hull(a):
    hull = a.part('Hull', 'Team')
    prof = [(NOSE, .58), (NOSE + .25, .72), (-2.05, TOP), (2.7, TOP), (TAIL, .8), (TAIL - .05, .38), (-2.5, .36)]
    k.extrude(hull, prof, 2.4, axis='X', chamfer=.05, corner=.025)
    low = a.part('Hull_lower', 'Armor')
    k.extrude(low, [(NOSE + .15, .56), (-2.45, .34), (2.7, .34), (2.75, .7)], (TX - TW / 2) * 2, axis='X',
              chamfer=.02)
    for s in (-1, 1):
        K.fender(a.part('Fenders', 'Team'), TX + .02, NOSE + .15, TAIL - .05, .88, .5, s, lip=.03)
        sk = a.part('Skirts', 'Team')
        for j in range(5):
            sk.box((.025, .96, .34), loc=(s * (TX + .26), -2.1 + j * 1.0, .7), bevel=0)
        a.part('Skirt_flaps', 'Rubber').box((.02, 4.9, .07), loc=(s * (TX + .26), -.1, .5), bevel=0)
        a.part('Team_band', 'Team').box((.01, 2.4, .07), loc=(s * (TX + .275), .5, .78), bevel=0)
    # The driver's hatch and periscopes (front right), the headlamp clusters, tow hooks, the glacis bolts.
    C.hatch(a, (-.55, -1.75, TOP), r=.26, periscope=True)
    for s in (-1, 1):
        K.lamp(a, (s * .95, -2.3, .95), (0, -1, .3), r=.07, guard=True)
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .55, NOSE - .02, .5), facing=(0, -1, 0), size=.08)
    K.rivet_line(a.part('Kit_steel', 'Steel'), (-1.0, -2.45, .83), (1.0, -2.45, .83), (0, -.6, .8), pitch=.16,
                 r=.015)
    # The engine deck: two big grille panels, the access plates, the exhaust grilles on both rear corners.
    for x in (-.5, .5):
        K.grille(a, (x, 1.95, TOP + .02), .8, 1.0, facing=(0, 0, 1), slats=7, frame_mat='Team')
    K.plate(a.part('Deck_plates', 'Armor'), (1.4, .4, .02), loc=(0, 1.15, TOP + .01))
    for s in (-1, 1):
        K.grille(a, (s * .95, TAIL - .02, .72), .4, .25, facing=(0, 1, 0), slats=3, frame_mat='Team')
        a.part('Tail_lamps', 'LavaGlow').box((.08, .02, .05), loc=(s * 1.05, TAIL - .02, .95), bevel=0)
    a.pivot('Point_exhaust', (.95, TAIL, .75))
    a.pivot('Point_fire', (0, 1.6, TOP + .3))
    # Fender stowage: bins on the front fenders, the tow cable on the left.
    for s in (-1, 1):
        C.stowage_box(a, (.42, .6, .24), (s * (TX + .02), -2.3, .88), mat='Armor', latches=1)
    a.part('Tow_cable', 'Undercarriage').tube([(1.12, -1.5, .92), (1.12, 1.9, .92)], .03, seg=5)


def _running_gear(a):
    for s in (-1, 1):
        C.running_gear(a, s, TX, TW, WHEELS, WR, sprocket=(2.5, .5, .27), idler=(-2.55, .48, .26),
                       rollers=[(-1.3, .72), (0, .72), (1.3, .72)], pitch=.22, hide_top=(-2.4, 2.4, .6),
                       disc_mat='Armor', wheel_w=.18, seg=8, teeth=12)


def _gun(a, t, s):
    """One KDA 35 mm in its armoured mount outside the turret cheek on side s."""
    tag = '' if s > 0 else '_2'
    x = s * 1.36
    mt = a.part('Cradle', 'Team', t)
    k.extrude(mt, [(-.75, -.2), (.5, -.2), (.6, .05), (.45, .24), (-.6, .24), (-.8, .05)], .32, loc=(x, -.2, .5),
              axis='X', chamfer=.03, corner=.03)
    a.part('Gun_feeds', 'Armor', t).box((.2, .5, .18), loc=(x + s * .2, .05, .62), bevel=0)
    bar = a.part(f'Main_cannon{tag}', 'Steel', t)
    k.lathe(bar, [(.09, 0), (.09, .18), (.055, .22), (.045, 2.1), (0, 2.1)], loc=(x, -.95, .52), rot=K.FORWARD,
            seg=10, worn=(1,))
    for j in range(5):
        bar.cyl(.06, .04, loc=(x, -1.25 - j * .14, .52), rot=K.FORWARD, seg=10, bevel=0)     # cooling rings
    br = a.part(f'Muzzle_brake{tag}', 'Undercarriage', t)
    k.lathe(br, [(.05, 0), (.075, .04), (.075, .22), (.06, .26), (0, .26)], loc=(x, -3.02, .52), rot=K.FORWARD,
            seg=10, worn=(1,))
    a.part('Gun_radars', 'Armor', t).box((.08, .14, .12), loc=(x, -3.12, .61), bevel=0)   # v0 radar
    return (x, -3.3, .52)


def _turret(a):
    t = a.pivot('Turret', TUR)
    K.turret_ring(a.part('Turret_ring', 'Armor'), TUR, .95, h=.05)
    body = a.part('Turret_body', 'Team', t)
    bot = [(-.75, -1.3), (.75, -1.3), (1.15, -.95), (1.18, 1.25), (.95, 1.45), (-.95, 1.45), (-1.18, 1.25),
           (-1.15, -.95)]
    top = [(-.62, -1.05), (.62, -1.05), (1.0, -.75), (1.04, 1.18), (.85, 1.35), (-.85, 1.35), (-1.04, 1.18),
           (-1.0, -.75)]
    C.slab_loft(body, bot, top, 0, .85)
    k.block(a.part('Turret_roof', 'Armor', t), (1.7, 2.0, .04), loc=(0, .2, .85), chamfer=.01)
    left = _gun(a, t, 1)
    _gun(a, t, -1)
    a.pivot('Muzzle_main', left, t)
    # The tracking radar dish on the turret front in its housing, the sights, hatches with periscopes.
    trk = a.part('Radar_tracker', 'Armor', t)
    k.lathe(trk, [(0, -.06), (.4, -.04), (.44, .04), (.44, .1)], loc=(0, -1.25, .55), rot=K.FORWARD, seg=16,
            worn=(2,))
    a.part('Radar_tracker_face', 'Undercarriage', t).cyl(.36, .02, loc=(0, -1.36, .55), rot=K.FORWARD, seg=16, bevel=0)
    k.block(a.part('Sight', 'Armor', t), (.24, .26, .2), loc=(.45, -.6, .85), chamfer=.03)
    a.part('Glass', 'Glass', t).box((.18, .01, .08), loc=(.45, -.735, .96), bevel=0)
    C.hatch(a, (.45, .1, .87), r=.26, parent=t, periscope=True)
    C.hatch(a, (-.45, .1, .87), r=.26, parent=t, periscope=True)
    # The search radar mast over the rear roof and the wide dish turning on it (`Radar`).
    mast = a.part('Radar_mast', 'Steel', t)
    k.lathe(mast, [(.18, .85), (.18, .9), (.09, .98), (.08, 1.45)], loc=(0, 1.0, 0), seg=10, worn=(1,))
    for s in (-1, 1):
        mast.limb((s * .3, 1.2, .86), (0, 1.0, 1.3), .03, .03, bevel=0)
    r = a.pivot('Radar', (0, 1.0, 1.5), t)
    dish = a.part('Radar_dish', 'Armor', r)
    # The reflector: six curved panels side by side (a parabola across), taller in the middle, a rim tube.
    for i in range(6):
        u = (i - 2.5) / 2.5
        h = .6 * math.sqrt(1 - .45 * u * u)
        k.block(dish, (.27, .035, h), loc=(u * .66, .12 * u * u - .02, -h / 2), rot=(0, 0, -math.atan(.24 * u / .66 * 2.5)),
                chamfer=.008)
    a.part('Radar_feed', 'Steel', r).box((1.5, .04, .04), loc=(0, .1, -.32), bevel=0)
    a.part('Radar_feed', 'Steel', r).limb((0, .1, 0), (0, -.35, .0), .03, .03, bevel=0)
    a.part('Radar_feed', 'Steel', r).box((.1, .1, .1), loc=(0, -.38, 0), bevel=.01)
    # The twin Stinger box on its own pivot on the left rear roof (`Mount_missile`, the old `Launcher_box`).
    m = a.pivot('Mount_missile', (.7, .85, .89), t)
    a.part('Launcher_post', 'Steel', m).cyl(.06, .3, loc=(0, 0, .15), seg=8, bevel=0)
    k.block(a.part('Launcher_box', 'Armor', m), (.36, .9, .3), loc=(0, 0, .3), chamfer=.03)
    a.part('Launcher_covers', 'Undercarriage', m).box((.3, .01, .22), loc=(0, -.455, .45), bevel=0)
    a.pivot('Muzzle_missile', (0, -.47, .45), m)
    # Smoke dischargers (two banks of four), rear bin, aerials, team bands.
    for s in (-1, 1):
        K.smoke_dischargers(a, 1.0, .6, .62, s, count=3, parent=t)
    C.stowage_box(a, (1.2, .32, .35), (0, 1.55, .3), mat='Armor', latches=2, parent=t)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (-.8, 1.2, .87), h=.35)
    for s in (-1, 1):
        a.part('Team_band', 'Team', t).box((.01, 1.6, .08), loc=(s * 1.13, .3, .4), rot=(0, s * .05, 0), bevel=0)


def aa_vehicle(a, detail=False):
    """The anti-aircraft gun tank: see the module docstring."""
    _hull(a)
    _running_gear(a)
    _turret(a)
    K.dust(a, (0, 0, .3), radius=3.0, k=.12)
    k.clean(a)


BUILDERS = {
    'aa_vehicle': (aa_vehicle, dict(ao_distance=.5, grime_height=.5)),
}
