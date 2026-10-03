"""Prompt 35 wave 4 (lane C): the self-propelled howitzer rebuilt from scratch (spec: Tools/blender/specs/artillery.json).

An M109A7 "Paladin PIM" (the sheet's choice over the CAESAR; the def's modelSize 7.86 x 3.14 x 2.88 m, the gun's
overhang inside the length): the low aluminium hull with the engine on the front right and the driver's hatch on
the front left, the folding travel lock on the nose, seven road wheels a side with the front sprocket and rear
idler under light skirts, the two recoil spades folded on the rear plate beside the rear door; the big flat-sided
turret set aft with its long bustle, side doors and stowage racks, the M284 155 mm barrel (more than half the
vehicle's length out past the nose) with its bore evacuator and double-baffle muzzle brake on the cradle and
mantlet; the commander's cupola on the right with the M2 on a raised ring (the def's free `hmg_selfdef_15`, owner's
roof-gun rule); smoke dischargers on the turret front corners.

Runtime nodes kept: `Turret`, `Main_cannon`, `Main_cannon_cradle`, `Muzzle_brake`, `Muzzle_main`, `Mount_mg`,
`Muzzle_mg`, `Point_exhaust`, `Point_fire`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TX, TW = 1.18, .46
WR = .27
WHEELS = (-2.0, -1.33, -.66, 0.0, .66, 1.33, 2.0)
TOP = 1.18
NOSE, TAIL = -2.62, 2.85
TUR = (0, .95, TOP)


def _hull(a):
    hull = a.part('Hull', 'Team')
    prof = [(NOSE, .7), (-1.9, TOP), (TAIL, TOP), (TAIL + .04, .5), (2.6, .36), (-2.4, .36)]
    k.extrude(hull, prof, 2.5, axis='X', chamfer=.06, corner=.03)
    low = a.part('Hull_lower', 'Armor')
    k.extrude(low, [(NOSE + .1, .68), (-2.3, .34), (2.6, .34), (2.7, .7)], (TX - TW / 2) * 2, axis='X', chamfer=.02)
    # Light steel skirts over the top run, the fenders, team bands.
    for s in (-1, 1):
        K.fender(a.part('Fenders', 'Team'), TX + .02, NOSE + .2, TAIL - .05, .9, .5, s, lip=.03)
        sk = a.part('Skirts', 'Armor')
        for j in range(4):
            sk.box((.025, 1.12, .26), loc=(s * (TX + .25), -1.7 + j * 1.15, .75), bevel=0)
        a.part('Team_band', 'Team').box((.01, 2.6, .08), loc=(s * 1.255, .3, 1.05), bevel=0)
    # The driver's hatch (front left), the engine grilles and exhaust (front right), lamps, tow hooks.
    C.hatch(a, (.6, -1.75, TOP), r=.27, periscope=True)
    K.grille(a, (-.55, -1.55, TOP + .02), .85, .8, facing=(0, 0, 1), slats=6, frame_mat='Team')
    K.grille(a, (-.55, -2.18, 1.0), .7, .25, facing=(0, -1, .7), slats=4, frame_mat='Team')
    K.exhaust(a, (-1.12, -1.1, TOP - .05), r=.06, length=.35, direction=(-1, 0, .3), muffler=False, cap=False)
    a.pivot('Point_exhaust', (-1.25, -1.1, TOP + .05))
    for s in (-1, 1):
        K.lamp(a, (s * .95, -2.2, 1.0), (0, -1, .3), r=.065, guard=True)
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .5, NOSE - .02, .6), facing=(0, -1, 0), size=.08)
    # The travel lock: an A-frame hinged on the nose, its cradle cup up at the barrel.
    tl = a.part('Travel_lock', 'Steel')
    for s in (-1, 1):
        tl.limb((s * .32, -2.3, .95), (s * .06, -2.55, 1.72), .05, .05, bevel=0)
    k.block(tl, (.36, .18, .1), loc=(0, -2.56, 1.68), chamfer=.02)
    K.hinge(a.part('Kit_steel', 'Steel'), (-.4, -2.28, .93), (.4, -2.28, .93), r=.03, knuckles=3)
    # The rear: the door with its handle, the two recoil spades folded up, tail lamps.
    door = a.part('Hatches', 'Armor')
    K.plate(door, (.9, .04, .62), loc=(0, TAIL + .03, .8))
    K.handle(a.part('Kit_steel', 'Steel'), (.3, TAIL + .06, .8), (.3, TAIL + .06, .95), (0, 1, 0), h=.04, r=.012)
    sp = a.part('Spades', 'Armor')
    for s in (-1, 1):
        k.extrude(sp, [(-.25, 0), (.25, 0), (.18, .55), (-.18, .55)], .06, loc=(s * .85, TAIL + .1, .45),
                  rot=(R90, 0, 0), axis='Z', chamfer=.01)
        a.part('Tail_lamps', 'LavaGlow').box((.08, .02, .05), loc=(s * 1.15, TAIL + .03, 1.08), bevel=0)
    a.pivot('Point_fire', (0, 0, TOP + .5))
    C.cable_reel(a, (1.15, -1.3, TOP + .12), r=.15, w=.3, axis='Y')


def _running_gear(a):
    for s in (-1, 1):
        C.running_gear(a, s, TX, TW, WHEELS, WR, sprocket=(-2.4, .5, .25), idler=(2.45, .46, .24),
                       rollers=[(-1.0, .68), (.66, .68)], pitch=.22, hide_top=(-2.2, 2.3, .62), disc_mat='Armor',
                       wheel_w=.17, seg=8, teeth=12)


def _turret(a):
    t = a.pivot('Turret', TUR)
    K.turret_ring(a.part('Turret_ring', 'Armor'), TUR, .95, h=.05)
    body = a.part('Turret_body', 'Team', t)
    # The big box: a sloped front, flat sides leaning in a little, the long bustle over the rear plate.
    bot = [(-.95, -1.55), (.95, -1.55), (1.3, -1.2), (1.32, 2.1), (1.15, 2.2), (-1.15, 2.2), (-1.32, 2.1),
           (-1.3, -1.2)]
    top = [(-.8, -1.15), (.8, -1.15), (1.2, -.85), (1.22, 2.05), (1.05, 2.15), (-1.05, 2.15), (-1.22, 2.05),
           (-1.2, -.85)]
    C.slab_loft(body, bot, top, 0, .92)
    roof = a.part('Turret_roof', 'Armor', t)
    k.block(roof, (2.0, 2.7, .05), loc=(0, .55, .92), chamfer=.015)
    # Side doors with hinges, stowage racks along the sides, the bustle rear door, vents.
    for s in (-1, 1):
        K.plate(a.part('Turret_doors', 'Armor', t), (.03, .7, .6), loc=(s * 1.3, .2, .45), chamfer=.008)
        K.hinge(a.part('Kit_steel', 'Steel', t), (s * 1.33, -.13, .2), (s * 1.33, -.13, .7), r=.022, knuckles=3)
        rk = a.part('Racks', 'Steel', t)
        for z in (.35, .75):
            rk.box((.03, 1.1, .03), loc=(s * 1.42, 1.35, z), bevel=0)
        for y in (.85, 1.35, 1.85):
            rk.box((.12, .03, .45), loc=(s * 1.37, y, .55), bevel=0)
        C.ammo_tins(a, (s * 1.4, 1.35, .38), n=3, size=(.11, .26, .18), parent=t, axis='Y')
    K.plate(a.part('Turret_doors', 'Armor', t), (.9, .03, .6), loc=(0, 2.19, .45), chamfer=.008)
    K.grille(a, (-.6, 1.6, .95), .5, .4, facing=(0, 0, 1), slats=4, parent=t, frame_mat='Armor')
    # Mantlet, cradle and the M284 barrel with its bore evacuator and double-baffle brake.
    man = a.part('Mantlet', 'Armor', t)
    k.extrude(man, [(-.2, -.3), (.15, -.32), (.2, .3), (-.15, .32)], .8, loc=(0, -1.5, .55), axis='X', chamfer=.04,
              corner=.03)
    cr = a.part('Main_cannon_cradle', 'Steel', t)
    k.lathe(cr, [(.16, 0), (.16, .6), (.13, .66), (0, .66)], loc=(0, -1.6, .55), rot=K.FORWARD, seg=12, worn=(1,))
    for s in (-1, 1):
        cr.cyl(.06, .7, loc=(s * .17, -1.95, .48), rot=K.FORWARD, seg=8, bevel=0)      # recuperator cylinders
    C.gun_tube(a, 'Main_cannon', t, (0, -2.2, .55), 3.2, .085, seg=12, extractor=(.32, 1.6), brake='double',
               brake_name='Muzzle_brake')
    a.pivot('Muzzle_main', (0, -5.85, .55), t)
    # The commander's cupola (right) with its periscopes and the M2 on a raised ring, the loader's hatch (left),
    # smoke dischargers on the front corners, aerials, the team band.
    cup = a.part('Cupola', 'Armor', t)
    k.ring(cup, [(.32, .92), (.4, .92), (.4, 1.08), (.34, 1.12)], loc=(-.62, .1, 0), seg=14, worn=(2,))
    for i in range(4):
        u = i * R90 + .4
        K.periscope(a, (-.62 + math.cos(u) * .38, .1 + math.sin(u) * .38, 1.04), facing=(math.cos(u), math.sin(u), 0),
                    parent=t, size=(.1, .08, .07))
    K.pintle_mg(a, t, (-.62, .1, 1.12), post=.18, length=1.1)
    C.hatch(a, (.62, .3, .94), r=.27, parent=t, periscope=True)
    for s in (-1, 1):
        K.smoke_dischargers(a, 1.18, -1.05, .8, s, count=3, parent=t)
    for x in (.9, -.95):
        K.whip_antenna(a.part('Antennas', 'Steel', t), (x, 1.9, .94), h=.3)
    a.part('Team_band', 'Team', t).box((.01, 2.6, .1), loc=(1.29, .5, .78), bevel=0)
    a.part('Team_band', 'Team', t).box((.01, 2.6, .1), loc=(-1.29, .5, .78), bevel=0)
    a.part('Team_roof', 'Team', t).box((1.0, .5, .01), loc=(0, 1.5, .955), bevel=0)


def artillery(a, detail=False):
    """The self-propelled howitzer: see the module docstring."""
    _hull(a)
    _running_gear(a)
    _turret(a)
    K.dust(a, (0, 0, .3), radius=3.0, k=.12)
    k.clean(a)


BUILDERS = {
    'artillery': (artillery, dict(ao_distance=.5, grime_height=.5)),
}
