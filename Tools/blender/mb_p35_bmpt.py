"""Prompt 35 wave 4 (lane C): the tank support vehicle rebuilt from scratch (spec: Tools/blender/specs/bmpt.json).

A BMPT "Terminator" on the T-72 hull (the def's modelSize 6.08 x 2.96 x 2.39 m): the T-72's glacis under Kontakt-5
blocks with the splash board, the self-entrenching blade under the nose (`Blade`), six large road wheels a side
with three return rollers, the front idler and rear sprocket, rubber skirts carrying ERA cassettes, the fuel
drums and the unditching log on the rear; the two AG-17D grenade launchers in armoured boxes on the front fenders
(`Muzzle_agl_l` / `_r`); the low wide turret with the weapon module on its roof: two 2A42 30 mm guns side by side
in one cradle with the coaxial PKT, the two armoured Ataka launcher boxes either side of the turret (two tubes
each), the gunner's and commander's sights, Tucha smoke dischargers and the rear stowage basket.

Runtime nodes kept: `Turret`, `Main_cannon`, `Main_cannon_2`, `Muzzle_brake`, `Muzzle_brake_2`, `Muzzle_main`, `Coax`,
`Muzzle_coax`, `Muzzle_missile` (x2), `Muzzle_agl_l`, `Muzzle_agl_r`, `Blade`, `Blade_plate`, `Point_exhaust`,
`Point_fire`. Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TX, TW = 1.14, .5
WR = .35
WHEELS = (-1.85, -1.08, -.31, .46, 1.23, 2.0)
TOP = 1.28
NOSE, TAIL = -2.95, 2.95
TUR = (0, -.05, TOP)


def _hull(a):
    hull = a.part('Hull', 'Team')
    prof = [(NOSE, .62), (-2.0, TOP), (2.8, TOP), (TAIL, .95), (TAIL - .05, .45), (-2.6, .36)]
    k.extrude(hull, prof, 2.2, axis='X', chamfer=.05, corner=.03)
    low = a.part('Hull_lower', 'Armor')
    k.extrude(low, [(NOSE + .15, .6), (-2.55, .34), (2.8, .34), (2.85, .75)], (TX - TW / 2) * 2, axis='X', chamfer=.02)
    for s in (-1, 1):
        K.fender(a.part('Fenders', 'Team'), TX + .02, NOSE + .1, TAIL - .05, .98, .54, s, lip=.03)
        # Rubber skirts with a row of ERA cassettes on the front half.
        sk = a.part('Skirts', 'Rubber')
        for j in range(5):
            sk.box((.025, 1.0, .36), loc=(s * (TX + .27), -2.0 + j * 1.02, .78), bevel=0)
        era = a.part('Era_bricks', 'Armor')
        for j in range(5):
            era.box((.07, .44, .3), loc=(s * (TX + .32), -2.35 + j * .48, .8), bevel=0)
        a.part('Team_band', 'Team').box((.01, 1.6, .08), loc=(s * (TX + .3), 1.6, .82), bevel=0)
    # The glacis: Kontakt-5 blocks in two rows, the splash board, the driver's hatch with periscope, lamps.
    g0, g1 = Vector((0, NOSE, .62)), Vector((0, -2.0, TOP))
    d = (g1 - g0).normalized()
    ang = math.atan2(d.z, -d.y)
    era = a.part('Era_bricks', 'Armor')
    for i in range(5):
        for j in range(2):
            c = g0 + d * (.25 + j * .42)
            era.box((.4, .38, .1), loc=((i - 2) * .43, c.y - .03, c.z + .05), rot=(ang - R90, 0, 0), bevel=0)
    a.part('Deck_plates', 'Armor').box((2.0, .05, .1), loc=(0, -2.08, TOP + .02), rot=(-.4, 0, 0), bevel=0)
    C.hatch(a, (0, -1.75, TOP), r=.24, periscope=True)
    for s in (-1, 1):
        K.lamp(a, (s * 1.02, -2.35, 1.02), (0, -1, .2), r=.06, guard=True)
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .5, NOSE - .02, .5), facing=(0, -1, 0), size=.08)
    # The self-entrenching blade under the nose (`Blade`, a runtime part; Blade_plate is its mesh).
    b = a.pivot('Blade', (0, NOSE + .1, .45))
    bp = a.part('Blade_plate', 'Armor', b)
    k.extrude(bp, [(-.12, -.12), (.05, -.14), (.1, .14), (-.03, .16)], 2.1, axis='X', chamfer=.02)
    for x in (-.7, .7):
        bp.box((.06, .3, .08), loc=(x, .2, .05), bevel=0)
    # The engine deck: grilles, the exhaust louvre on the left fender, the two fuel drums and the log on the rear.
    K.grille(a, (0, 2.25, TOP + .02), 1.5, .8, facing=(0, 0, 1), slats=7, frame_mat='Team')
    K.grille(a, (TX + .02, 1.75, 1.0), .4, .18, facing=(0, 0, 1), slats=3, frame_mat='Armor')
    a.pivot('Point_exhaust', (TX + .02, 1.8, 1.05))
    for x in (-.55, .55):
        K.fuel_drum(a.part('Drums', 'Fuel'), a.part('Kit_steel', 'Steel'), (x, TAIL + .15, .95), r=.22, h=.75,
                    lying=True)
    k.lathe(a.part('Log', 'Wood'), [(.1, -1.0), (.12, -.97), (.12, .97), (.1, 1.0)], loc=(0, TAIL + .1, 1.3),
            rot=(0, R90, 0), seg=8)
    for s in (-1, 1):
        a.part('Tail_lamps', 'LavaGlow').box((.08, .02, .05), loc=(s * 1.05, TAIL - .02, 1.05), bevel=0)
    a.pivot('Point_fire', (0, 1.7, TOP + .3))
    # Fender furniture: fuel cells on the right, bins on the left.
    for y in (-.4, .4):
        K.chamfer_box(a.part('Fuel_cells', 'Armor'), (.48, .7, .32), loc=(-(TX + .02), y, .99), c=.04)
    C.stowage_box(a, (.48, .8, .3), (TX + .02, 0, .99), mat='Armor', latches=2)


def _agl(a, s):
    """An AG-17D grenade launcher in its armoured box on the front fender (s = 1 left: `Muzzle_agl_l`)."""
    x, y, z = s * (TX + .02), -2.35, 1.0
    box = a.part('Agl_boxes', 'Team')
    k.extrude(box, [(-.3, 0), (.32, 0), (.32, .2), (-.1, .32), (-.3, .3)], .42, loc=(x, y, z), axis='X', chamfer=.02,
              corner=.02)
    a.part('Agl_barrels', 'Steel').cyl(.035, .35, loc=(x, y - .42, z + .14), rot=K.FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_agl_l' if s > 0 else 'Muzzle_agl_r', (x, y - .6, z + .14))


def _running_gear(a):
    for s in (-1, 1):
        C.running_gear(a, s, TX, TW, WHEELS, WR, sprocket=(2.62, .52, .27), idler=(-2.7, .5, .26),
                       rollers=[(-1.45, .82), (.07, .82), (1.6, .82)], pitch=.22, hide_top=(-2.5, 2.5, .64),
                       disc_mat='Armor', wheel_w=.19, seg=8, teeth=12)
        _agl(a, s)


def _turret(a):
    t = a.pivot('Turret', TUR)
    K.turret_ring(a.part('Turret_ring', 'Armor'), TUR, .95, h=.05)
    body = a.part('Turret_body', 'Team', t)
    bot = [(-.5, -1.15), (.5, -1.15), (1.1, -.6), (1.12, .85), (.85, 1.15), (-.85, 1.15), (-1.12, .85), (-1.1, -.6)]
    top = [(-.4, -.95), (.4, -.95), (.95, -.5), (.97, .78), (.72, 1.02), (-.72, 1.02), (-.97, .78), (-.95, -.5)]
    C.slab_loft(body, bot, top, 0, .5)
    # The weapon module on the roof: its armoured cradle (mantlet), the twin 2A42 guns, the coaxial PKT.
    man = a.part('Mantlet', 'Armor', t)
    k.extrude(man, [(-.45, 0), (.35, 0), (.45, .14), (.2, .32), (-.45, .3)], .7, loc=(0, -.4, .5), axis='X',
              chamfer=.03, corner=.02)
    for x, tag in ((.16, ''), (-.16, '_2')):
        gun = a.part(f'Main_cannon{tag}', 'Steel', t)
        k.lathe(gun, [(.06, 0), (.06, .3), (.04, .34), (.032, 1.6), (0, 1.6)], loc=(x, -.8, .68), rot=K.FORWARD, seg=8,
                worn=(1,))
        k.lathe(a.part(f'Muzzle_brake{tag}', 'Undercarriage', t), [(.032, 0), (.05, .03), (.05, .2), (0, .2)],
                loc=(x, -2.38, .68), rot=K.FORWARD, seg=8, worn=(1,))
    a.pivot('Muzzle_main', (.16, -2.6, .68), t)
    co = a.pivot('Coax', (.36, -.8, .64), t)
    a.part('MG_coax', 'Steel', co).cyl(.02, .5, loc=(0, -.25, 0), rot=K.FORWARD, seg=6, bevel=0)
    a.pivot('Muzzle_coax', (0, -.52, 0), co)
    # The two armoured Ataka launcher boxes either side, two tubes each.
    for s, name in ((1, 'Muzzle_missile'), (-1, 'Muzzle_missile.001')):
        lb = a.part('Missile_boxes', 'Team', t)
        k.extrude(lb, [(-.15, -.18), (.15, -.18), (.15, .18), (-.15, .18)], 1.3, loc=(s * 1.12, -.25, .55),
                  axis='Y', chamfer=.03, corner=.03)
        a.part('Launcher_covers', 'Undercarriage', t).box((.24, .01, .28), loc=(s * 1.12, -.905, .55), bevel=0)
        a.part('Kit_steel', 'Steel', t).box((.12, .4, .08), loc=(s * 1.0, -.25, .38), bevel=0)
        a.pivot(name.replace('.001', '__001'), (s * 1.12, -.92, .55), t)
    # Sights: the gunner's box on the left, the commander's panoramic head on the right rear.
    k.block(a.part('Sight', 'Armor', t), (.32, .36, .3), loc=(.5, .25, .5), chamfer=.03)
    a.part('Glass', 'Glass', t).box((.24, .01, .14), loc=(.5, .065, .68), bevel=0)
    k.lathe(a.part('Sight', 'Armor', t), [(.1, 0), (.1, .34), (.16, .36), (.16, .5), (0, .52)],
            loc=(-.5, .45, .5), seg=10, worn=(3,))
    a.part('Glass', 'Glass', t).box((.16, .01, .08), loc=(-.5, .29, .93), bevel=0)
    C.hatch(a, (.5, .72, .52), r=.22, parent=t, periscope=True, facing=(0, 1, 0))
    C.hatch(a, (-.5, .82, .52), r=.22, parent=t)
    for s in (-1, 1):
        sp = a.part('Smoke_launchers', 'Armor', t)
        for j in range(4):
            sp.cyl(.04, .2, loc=(s * (.98 - j * .04), .3 + j * .12, .32), rot=(R90 - .5, 0, s * 1.1), seg=8, bevel=0)
    rk = a.part('Racks', 'Steel', t)
    k.sweep(rk, [(-.015, -.015), (.015, -.015), (.015, .015), (-.015, .015)],
            [(.8, 1.05, .3), (.8, 1.4, .3), (-.8, 1.4, .3), (-.8, 1.05, .3)])
    a.part('Stowage', 'Canvas', t).box((1.3, .3, .22), loc=(0, 1.24, .2), bevel=.04)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (.8, .9, .5), h=.3)
    for s in (-1, 1):
        a.part('Team_band', 'Team', t).box((.01, 1.2, .07), loc=(s * 1.04, .35, .2), rot=(0, s * .3, 0), bevel=0)


def bmpt(a, detail=False):
    """The tank support vehicle: see the module docstring."""
    K.suffixed(a)
    _hull(a)
    _running_gear(a)
    _turret(a)
    K.dust(a, (0, 0, .3), radius=3.0, k=.12)
    k.clean(a)


BUILDERS = {
    'bmpt': (bmpt, dict(ao_distance=.5, grime_height=.5)),
}
