"""Prompt 35 wave 4 (lane C): the tank destroyer rebuilt from scratch (spec: Tools/blender/specs/tank_destroyer.json).

A 2S25 Sprut-SD (the def's modelSize 7.89 x 2.62 x 2.04 m, the gun's overhang inside the length): the low
air-droppable hull of the BMD-3 family stretched to seven small road wheels a side on hydropneumatic arms, the
front idler and the rear sprocket with four return rollers; the sharp lower nose under a steep glacis carrying
the folded trim vane; the two water-jet outlets on the rear plate; the low welded turret with sloped cheeks and a
bustle basket, the very long 2A75 125 mm smoothbore (thermal sleeve bands, fume extractor, a plain muzzle with
no brake) on its mantlet; the commander's panoramic sight, the gunner's sight and laser box; the 12.7 mm on a
raised pintle (the def's free `hmg_roof`, owner's roof-gun rule); Tucha smoke dischargers; fender bins.

Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake` (the plain muzzle collar), `Muzzle_main`, `Mount_mg`,
`Muzzle_mg`, `Point_exhaust`, `Point_fire`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TX, TW = 1.0, .44
WR = .25
WHEELS = (-1.95, -1.3, -.65, 0.0, .65, 1.3, 1.95)
TOP = 1.05
NOSE, TAIL = -2.62, 2.72
TUR = (0, .05, TOP)


def _hull(a):
    hull = a.part('Hull', 'Team')
    # Sections front to rear (half outlines bottom centre -> top centre): the sharp lower nose, the glacis, the
    # sponsons over the tracks with their sides leaning in, the rear plate.
    def sec(w_low, z_low, w_sp, z_sp, w_top, z_top):
        return [(0, z_low), (w_low, z_low), (w_low, z_sp - .12), (w_sp, z_sp), (w_top, z_top), (0, z_top)]
    C.section_loft(hull, [
        (NOSE, sec(.6, .55, .7, .6, .62, .64)),
        (NOSE + .35, sec(.72, .36, 1.2, .62, 1.06, .78)),
        (-1.75, sec(.76, .32, 1.3, .66, 1.12, TOP)),
        (2.45, sec(.76, .32, 1.3, .66, 1.12, TOP)),
        (TAIL, sec(.74, .4, 1.26, .66, 1.08, TOP - .05)),
    ])
    lip = a.part('Skirt_edge', 'Armor')
    for s in (-1, 1):
        lip.box((.04, 4.4, .08), loc=(s * 1.29, -.1, .6), bevel=0)
        a.part('Skirts', 'Rubber').box((.02, .7, .22), loc=(s * 1.3, -2.15, .46), rot=(.15, 0, 0), bevel=0)
        a.part('Team_band', 'Team').box((.01, 2.4, .07), loc=(s * 1.22, .6, .95), rot=(0, s * .25, 0), bevel=0)
    # The folded trim vane on the glacis, the driver's hatch with periscopes, lamps, tow hooks.
    vane = a.part('Trim_vane', 'Armor')
    K.plate(vane, (1.9, .5, .035), loc=(0, -2.25, .73), rot=(-.75, 0, 0), chamfer=.01)
    for x in (-.6, 0, .6):
        vane.box((.04, .46, .03), loc=(x, -2.23, .75), rot=(-.75, 0, 0), bevel=0)
    hd = a.part('Hatches', 'Armor')
    k.lathe(hd, [(0, .06), (.22, .055), (.26, .03), (.26, 0)], loc=(0, -1.45, TOP), seg=12, worn=(2,))
    for x in (-.25, 0, .25):
        K.periscope(a, (x, -1.75, TOP + .01), facing=(0, -1, 0), size=(.12, .07, .06))
    for s in (-1, 1):
        K.lamp(a, (s * .95, -1.95, .98), (0, -1, .15), r=.06, guard=True)
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .45, NOSE - .02, .55), facing=(0, -1, 0), size=.07)
    # The engine deck: grilles, the exhaust louvres on both rear corners; the two water-jet outlets on the rear.
    K.grille(a, (0, 2.0, TOP + .02), 1.3, .8, facing=(0, 0, 1), slats=6, frame_mat='Team')
    for s in (-1, 1):
        K.grille(a, (s * .85, 1.2, TOP + .02), .4, .5, facing=(0, 0, 1), slats=3, frame_mat='Team')
        k.lathe(a.part('Waterjets', 'Armor'), [(.16, 0), (.2, .04), (.2, .16), (.14, .2)], loc=(s * .5, TAIL, .62),
                rot=K.BACKWARD, seg=12, worn=(2,))
        a.part('Waterjets_dark', 'Undercarriage').cyl(.13, .02, loc=(s * .5, TAIL + .19, .62), rot=K.BACKWARD, seg=12,
                                                      bevel=0)
        a.part('Tail_lamps', 'LavaGlow').box((.08, .02, .05), loc=(s * 1.0, TAIL + .01, .95), bevel=0)
    K.tow_hook(a.part('Kit_steel', 'Steel'), (0, TAIL + .02, .5), facing=(0, 1, 0), size=.07)
    a.pivot('Point_exhaust', (-1.05, 1.9, TOP))
    a.pivot('Point_fire', (0, 1.4, TOP + .3))
    # Fender bins and the tow cable along the sponsons.
    for s in (-1, 1):
        C.stowage_box(a, (.36, .8, .22), (s * 1.08, 1.6, TOP - .02), mat='Armor', latches=2)
    C.cable_reel(a, (-1.05, -1.1, TOP + .12), r=.15, w=.3, axis='Y')
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (1.05, -.9, TOP - .02), rot=(0, 0, R90))


def _running_gear(a):
    for s in (-1, 1):
        C.running_gear(a, s, TX, TW, WHEELS, WR, sprocket=(2.42, .44, .23), idler=(-2.38, .46, .22),
                       rollers=[(-1.6, .63), (-.35, .64), (.95, .64), (2.0, .63)], pitch=.22, disc_mat='Armor',
                       wheel_w=.16, seg=10, teeth=13, idler_spokes=4)
        arms = a.part('Suspension', 'Undercarriage')
        for y in WHEELS:
            C.wheel_arm(arms, s, TX - .17, y, WR, length=.32, back=1, r=.04)


def _turret(a):
    t = a.pivot('Turret', TUR)
    K.turret_ring(a.part('Turret_ring', 'Armor'), TUR, .82, h=.05)
    body = a.part('Turret_body', 'Team', t)
    # The low welded turret: a sharp front, the cheeks sloping back, the sides leaning in, the rear bustle.
    bot = [(-.35, -1.05), (.35, -1.05), (.95, -.55), (.98, .75), (.75, 1.25), (-.75, 1.25), (-.98, .75), (-.95, -.55)]
    top = [(-.25, -.8), (.25, -.8), (.75, -.42), (.8, .7), (.62, 1.12), (-.62, 1.12), (-.8, .7), (-.75, -.42)]
    C.slab_loft(body, bot, top, 0, .5)
    k.block(a.part('Turret_roof', 'Armor', t), (1.1, 1.0, .04), loc=(0, .35, .5), chamfer=.01)
    # The mantlet and the long 2A75 gun with its sleeve bands and fume extractor, a plain muzzle.
    man = a.part('Mantlet', 'Armor', t)
    k.extrude(man, [(-.15, -.18), (.12, -.2), (.16, .18), (-.12, .2)], .5, loc=(0, -1.05, .28), axis='X',
              chamfer=.03, corner=.02)
    C.gun_tube(a, 'Main_cannon', t, (0, -1.15, .28), 3.95, .075, seg=12, sleeve=4, extractor=(.38, 1.75),
               brake='plain', brake_name='Muzzle_brake')
    a.pivot('Muzzle_main', (0, -5.18, .28), t)
    # Sights: the commander's panoramic sight (left rear), the gunner's sight and laser box (right front).
    cs = a.part('Sight', 'Armor', t)
    k.lathe(cs, [(.12, 0), (.12, .18), (.15, .2), (.15, .32), (0, .34)], loc=(.42, .25, .5), seg=10, worn=(3,))
    k.block(cs, (.28, .3, .22), loc=(-.5, -.45, .5), chamfer=.03)
    a.part('Glass', 'Glass', t).box((.2, .01, .1), loc=(-.5, -.605, .62), bevel=0)
    a.part('Glass', 'Glass', t).box((.18, .01, .06), loc=(.42, .1, .76), rot=(0, 0, 0), bevel=0)
    C.hatch(a, (.4, .7, .54), r=.25, parent=t, periscope=True)
    C.hatch(a, (-.4, .5, .54), r=.22, parent=t, periscope=True)
    # The free 12.7 mm on a raised pintle behind the gunner's hatch.
    K.pintle_mg(a, t, (-.45, .95, .5), post=.14, length=1.0)
    # Tucha dischargers, the bustle basket with its stowage, aerial, the team band.
    for s in (-1, 1):
        sp = a.part('Smoke_launchers', 'Armor', t)
        for j in range(3):
            sp.cyl(.04, .2, loc=(s * (.8 + j * .02), -.35 + j * .12, .42), rot=(R90 - .45, 0, s * .7), seg=8,
                   bevel=0)
        a.part('Smoke_brackets', 'Steel', t).box((.06, .4, .06), loc=(s * .86, -.23, .34), bevel=0)
    bk = a.part('Racks', 'Steel', t)
    k.sweep(bk, [(-.015, -.015), (.015, -.015), (.015, .015), (-.015, .015)],
            [(.72, 1.15, .2), (.72, 1.5, .2), (-.72, 1.5, .2), (-.72, 1.15, .2)])
    k.sweep(bk, [(-.015, -.015), (.015, -.015), (.015, .015), (-.015, .015)],
            [(.72, 1.15, .45), (.72, 1.5, .45), (-.72, 1.5, .45), (-.72, 1.15, .45)])
    a.part('Stowage', 'Canvas', t).box((1.1, .3, .22), loc=(0, 1.33, .33), bevel=.04)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (.7, 1.0, .5), h=.35)
    a.part('Team_band', 'Team', t).box((1.62, .01, .08), loc=(0, 1.255, .25), bevel=0)


def tank_destroyer(a, detail=False):
    """The tank destroyer: see the module docstring."""
    _hull(a)
    _running_gear(a)
    _turret(a)
    K.dust(a, (0, 0, .3), radius=3.0, k=.12)
    k.clean(a)


BUILDERS = {
    'tank_destroyer': (tank_destroyer, dict(ao_distance=.45, grime_height=.45)),
}
