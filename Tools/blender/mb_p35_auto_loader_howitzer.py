"""Prompt 35 wave 11 (lane C): the auto-loading howitzer rebuilt from scratch (spec: Tools/blender/specs/auto_loader_howitzer.json).

The XM2001 Crusader (the def's gun_155_crusader, modelSize 7.86 x 3.14 x 2.88 m; about 0.95 x the real vehicle):
the hull with the three-man crew compartment in front (three hatches with periscope blocks under a sloped glacis),
the turbine bay at the rear with its exhaust louvres and the resupply docking port in the rear plate, six road
wheels a side with the front sprocket, the rear idler and return rollers under full-length armoured skirts with a
rubber lower flap; the large unmanned turret set aft, a faceted wedge with sharply raked cheeks, its long bustle
holding the automatic loader (the ammunition door on the left, the bustle vents), the XM297 56-calibre barrel on a
deep mantlet with its cradle, thermal sleeve bands, bore evacuator and a single-baffle brake; the sensor mast and
GPS antenna on the roof, smoke dischargers, stowage bins on the bustle sides, the travel lock on the glacis, lamps,
tow hooks, jerrycans and a cable reel. No machine gun is drawn (the def has none): the old `Mount_mg` / `Muzzle_mg`
stay as plain pivots on the commander's sight.

Runtime nodes kept where they were: `Turret` (0, 1.0, 1.2), `Muzzle_main` (0, -4.0, 1.75), `Mount_mg`
(.55, 1.2, 2.36), `Muzzle_mg` (.55, .36, 2.57), `Point_exhaust` (.6, 3.95, .95), `Point_fire` (0, 1.1, 1.3); old
names kept (`Main_cannon`, `Main_cannon_cradle`, `Muzzle_brake`, `Turret_body`, `Turret_armor`, `Hatches`).
Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TX, TW = 1.2, .5
WR = .3
WHEELS = (-1.95, -1.15, -.38, .4, 1.18, 1.95)
TOP = 1.2
NOSE, TAIL = -3.0, 3.0
TUR = (0, 1.0, TOP)


def _hull(a):
    hull = a.part('Hull', 'Team')
    prof = [(NOSE, .62), (NOSE + .1, .8), (-1.9, TOP), (TAIL - .1, TOP), (TAIL, 1.05), (TAIL, .5), (2.7, .36),
            (-2.65, .36)]
    k.extrude(hull, prof, 2.3, axis='X', chamfer=.06, corner=.03)
    low = a.part('Hull_lower', 'Armor')
    k.extrude(low, [(NOSE + .1, .64), (-2.6, .34), (2.7, .34), (2.9, .6)], (TX - TW / 2) * 2, axis='X', chamfer=.02)
    # Full-length skirts with a rubber lower flap, sponson tops.
    for s in (-1, 1):
        K.fender(a.part('Fenders', 'Team'), TX + .03, NOSE + .25, TAIL - .1, .98, .56, s, lip=.03)
        sk = a.part('Skirts', 'Team')
        for j in range(5):
            y = -2.3 + j * 1.12
            sk.box((.04, 1.08, .38), loc=(s * (TX + .3), y, .76), bevel=0)
            a.part('Skirt_bolts', 'Steel').box((.02, .9, .03), loc=(s * (TX + .325), y, .9), bevel=0)
        a.part('Skirt_flaps', 'Rubber').box((.02, 5.6, .14), loc=(s * (TX + .3), .1, .5), bevel=0)
    # The crew compartment: three hatches with periscope blocks under the glacis.
    for x, peri in ((-.65, False), (0, True), (.65, False)):
        C.hatch(a, (x, -1.65, TOP), r=.26, periscope=peri)
    for x in (-.65, .65):
        K.periscope(a, (x, -1.97, TOP - .02), facing=(0, -1, .4), size=(.16, .1, .08))
    # Glacis: lamps, tow hooks, the travel lock, a cable reel.
    for s in (-1, 1):
        K.lamp(a, (s * .9, -2.82, .95), (0, -1, .4), r=.065, guard=True)
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .55, NOSE - .02, .58), facing=(0, -1, 0), size=.08)
    tl = a.part('Travel_lock', 'Steel')
    for s in (-1, 1):
        tl.limb((s * .3, -2.45, 1.02), (s * .06, -2.7, 1.66), .05, .05, bevel=0)
    k.block(tl, (.34, .18, .1), loc=(0, -2.7, 1.64), chamfer=.02)
    K.hinge(a.part('Kit_steel', 'Steel'), (-.36, -2.45, 1.0), (.36, -2.45, 1.0), r=.03, knuckles=3)
    C.cable_reel(a, (-1.0, -2.3, TOP + .1), r=.14, w=.28, axis='Y')
    # The turbine bay: louvres, the exhaust in the rear plate, the resupply port, tail lamps.
    K.grille(a, (.55, 2.35, TOP + .02), .8, .9, facing=(0, 0, 1), slats=7, frame_mat='Team')
    K.grille(a, (-.55, 2.35, TOP + .02), .8, .9, facing=(0, 0, 1), slats=7, frame_mat='Team')
    k.ring(a.part('Exhaust', 'Steel'), [(.16, -.04), (.22, -.04), (.22, .04), (.16, .04)], loc=(.6, TAIL + .01, .95),
           rot=(R90, 0, 0), seg=10)
    a.part('Exhaust_soot', 'Undercarriage').cyl(.16, .02, loc=(.6, TAIL, .95), rot=(R90, 0, 0), seg=10, bevel=0)
    a.pivot('Point_exhaust', (.6, 3.95, .95))
    K.soot(a, (.6, TAIL + .05, .95), radius=.4, k=.4)
    port = a.part('Hatches', 'Armor')
    K.plate(port, (.7, .04, .45), loc=(-.45, TAIL + .02, .82))
    K.handle(a.part('Kit_steel', 'Steel'), (-.2, TAIL + .05, .75), (-.2, TAIL + .05, .9), (0, 1, 0), h=.04, r=.012)
    for s in (-1, 1):
        a.part('Tail_lamps', 'LavaGlow').box((.08, .02, .05), loc=(s * 1.0, TAIL + .02, 1.1), bevel=0)
    a.pivot('Point_fire', (0, 1.1, 1.3))
    C.jerry_rack(a, (.9, -2.2, TOP + .02), count=2, axis='X')


def _running_gear(a):
    for s in (-1, 1):
        C.running_gear(a, s, TX, TW, WHEELS, WR, sprocket=(-2.6, .56, .27), idler=(2.62, .5, .26),
                       rollers=[(-1.55, .76), (1.55, .76)], pitch=.26, hide_top=(-2.5, 2.5, .66),
                       disc_mat='Armor', wheel_w=.18, seg=8, teeth=12)


def _turret(a):
    t = a.pivot('Turret', TUR)
    K.turret_ring(a.part('Turret_ring', 'Armor'), TUR, 1.0, h=.06)
    body = a.part('Turret_body', 'Team', t)
    # A faceted wedge: sharply raked cheeks closing on the mantlet, a long bustle.
    bot = [(-.55, -1.65), (.55, -1.65), (1.35, -.7), (1.38, 2.0), (1.2, 2.3), (-1.2, 2.3), (-1.38, 2.0),
           (-1.35, -.7)]
    top = [(-.5, -1.2), (.5, -1.2), (1.15, -.45), (1.2, 1.9), (1.05, 2.15), (-1.05, 2.15), (-1.2, 1.9),
           (-1.15, -.45)]
    C.slab_loft(body, bot, top, 0, .82)
    arm = a.part('Turret_armor', 'Armor', t)
    for s in (-1, 1):
        K.plate(arm, (.05, 1.15, .5), loc=(s * .93, -1.17, .42), rot=(0, 0, s * .87), chamfer=.01)
    k.block(arm, (2.1, 2.9, .05), loc=(0, .55, .845), chamfer=.015)
    # The ammunition door on the left of the bustle, vents, stowage bins on both sides.
    K.plate(a.part('Hatches', 'Armor', t), (.03, .9, .5), loc=(1.39, 1.3, .42), chamfer=.008)
    K.hinge(a.part('Kit_steel', 'Steel', t), (1.41, .82, .2), (1.41, .82, .65), r=.022, knuckles=3)
    K.grille(a, (0, 2.24, .45), .9, .35, facing=(0, 1, 0), slats=5, parent=t, frame_mat='Armor')
    for s, y in ((-1, 1.2), (1, 1.95)):
        C.stowage_box(a, (.25, .7 if s < 0 else .45, .38), (s * 1.5, y, .2), parent=t, name='Stowage')
    C.stowage_box(a, (1.2, .3, .3), (0, 2.45, .3), parent=t, name='Stowage')
    # The deep mantlet, the cradle, the XM297 56-calibre barrel.
    man = a.part('Mantlet', 'Armor', t)
    k.extrude(man, [(-.25, -.3), (.18, -.33), (.24, .3), (-.18, .33)], .9, loc=(0, -1.6, .5), axis='X',
              chamfer=.04, corner=.03)
    cr = a.part('Main_cannon_cradle', 'Steel', t)
    k.lathe(cr, [(.17, 0), (.17, .55), (.13, .62), (0, .62)], loc=(0, -1.75, .55), rot=K.FORWARD, seg=12, worn=(1,))
    for s in (-1, 1):
        cr.cyl(.06, .6, loc=(s * .18, -2.05, .47), rot=K.FORWARD, seg=8, bevel=0)
    C.gun_tube(a, 'Main_cannon', t, (0, -2.35, .55), 2.35, .082, seg=12, sleeve=3, extractor=(.3, 1.55),
               brake='plain', brake_name='Muzzle_brake')
    # A single-baffle brake block over the plain collar.
    bp = a.part('Muzzle_brake', 'Steel', t)
    k.extrude(bp, [(-.13, -.1), (.13, -.1), (.13, .1), (-.13, .1)], .3, loc=(0, -4.83, .55), axis='Y', chamfer=.02,
              corner=.02)
    a.pivot('Muzzle_main', (0, -5.0, .55), t)
    K.soot(a, (0, -4.0, 1.75), radius=.4, k=.35)
    # Sensor mast, GPS dome, the commander's sight (the old MG pivots ride on it), smoke dischargers, whips.
    mast = a.part('Sensor_mast', 'Steel', t)
    mast.cyl(.05, .5, loc=(-.7, 1.6, 1.1), seg=8, bevel=0)
    k.block(a.part('Sensor', 'Armor', t), (.3, .22, .2), loc=(-.7, 1.6, 1.45), chamfer=.02, ends=(True, True))
    a.part('Glass', 'Glass', t).box((.2, .02, .1), loc=(-.7, 1.49, 1.45), bevel=0)
    k.lathe(a.part('Gps_dome', 'Plaster', t), [(.1, 0), (.1, .03), (.06, .08), (0, .09)], loc=(.3, 1.9, .87), seg=8)
    k.lathe(a.part('Sight', 'Armor', t), [(.2, 0), (.2, .16), (.15, .2), (0, .21)], loc=(.55, .2, .86), seg=10,
            worn=(1,))
    K.periscope(a, (.55, .05, 1.1), facing=(0, -1, 0), parent=t, size=(.22, .18, .16))
    a.pivot('Mount_mg', (.55, .2, 1.16), t)
    a.pivot('Muzzle_mg', (0, -.84, .21), 'Mount_mg')
    for s in (-1, 1):
        K.smoke_dischargers(a, 1.2, -.55, .7, s, count=3, parent=t)
        K.whip_antenna(a.part('Antennas', 'Steel', t), (s * .95, 2.0, .87), h=.35)
    a.part('Team_band', 'Team', t).box((.01, 2.2, .1), loc=(1.37, .8, .65), bevel=0)
    a.part('Team_band', 'Team', t).box((.01, 2.2, .1), loc=(-1.37, .8, .65), bevel=0)


def auto_loader_howitzer(a, detail=False):
    """The auto-loading howitzer: see the module docstring."""
    _hull(a)
    _running_gear(a)
    _turret(a)
    K.dust(a, (0, 0, .3), radius=3.2, k=.12)
    k.clean(a)


BUILDERS = {
    'auto_loader_howitzer': (auto_loader_howitzer, dict(ao_distance=.5, grime_height=.5)),
}
