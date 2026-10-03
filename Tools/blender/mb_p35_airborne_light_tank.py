"""Prompt 35 wave 6 (lane B): the airborne light tank rebuilt from scratch (spec: Tools/blender/specs/airborne_light_tank.json).

An M8 AGS / M10 Booker-class air-droppable light tank (the def's modelSize 6.39 x 2.61 x 1.89 m with the gun): a
welded box hull with a sloped glacis and the bolt-on Level II armour modules (their bolt heads in rows), the
driver's hatch on the centre line with periscopes, the rear engine louvres; six road wheels a side, the rear
sprocket, the front idler on its tensioner and a linked track under short hinged skirts; the low three-man turret
with flat bolted cheek modules, the bustle autoloader with blow-out panels, the 105 mm gun with its pepper-pot
muzzle brake and fume extractor in a bolted mantlet, the coax, the commander's cupola with the M2 on a raised
pintle (MODEL_STANDARD "Roof guns"), the gunner's sight head, two four-tube smoke dischargers; stowage bins, a
tarp roll, water cans, tow cable, lamps, hooks, whips and Team bands.

Its own hull and turret (the paradrop variant `airborne_light_tank_chute` keeps its old build). Runtime nodes kept:
`Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Coax`, `Muzzle_coax`, `Point_exhaust`, `Point_fire`; new for
the gate: `Mantlet`, `Idlers`, `Mount_mg` / `Muzzle_mg` (the commander's M2, no data weapon), `Stowage`. Metres,
+Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TX, TW = 1.0, .44
WR = .26
WHEELS = (-1.45, -.82, -.19, .44, 1.07, 1.7)
NOSE, TAIL = -2.18, 3.18
DECK = 1.0
HALF = 1.1
TURRET = (0.0, .5, DECK)


def _hull(a):
    hull = a.part('Hull', 'Team')
    prof = [(TAIL, .45), (TAIL + .02, DECK - .1), (TAIL - .12, DECK), (-.75, DECK), (NOSE + .2, .82), (NOSE, .7),
            (NOSE + .4, .36), (TAIL - .3, .36)]
    k.extrude(hull, prof, HALF * 2, axis='X', chamfer=.045, corner=.02)
    k.extrude(a.part('Hull_lower', 'Armor'), [(TAIL - .1, .3), (NOSE + .5, .3), (NOSE + .4, .42), (TAIL - .1, .42)],
              1.6, axis='X', chamfer=.02)
    # The bolt-on Level II modules: glacis plates and side plates with their bolt rows.
    mods = a.part('Armor_modules', 'Armor')
    bolts = a.part('Kit_bolts', 'Steel')
    g0, g1 = (NOSE + .2, .82), (-.75, DECK)
    ang = math.atan2(g1[1] - g0[1], g1[0] - g0[0])
    nrm = (0, -math.sin(ang), math.cos(ang))

    def on_glacis(f, x, up=.0):
        y = g0[0] + (g1[0] - g0[0]) * f
        z = g0[1] + (g1[1] - g0[1]) * f
        return (x, y - math.sin(ang) * up, z + math.cos(ang) * up)
    grot = (ang, 0, 0)
    for x in (-.62, .62):
        k.block(mods, (.9, 1.25, .05), loc=on_glacis(.5, x, .0), rot=grot, chamfer=.02)
        for f in (.15, .85):
            for dx in (-.33, .33):
                bolts.cyl(.025, .03, loc=on_glacis(f, x + dx, .05), rot=grot, seg=6, bevel=0)
    for s in (-1, 1):
        for i, y in enumerate((-1.2, -.2, .8, 1.8)):
            k.block(mods, (.05, .9, .34), loc=(s * (HALF + .025), y, .8), chamfer=.015)
            for dy in (-.35, .35):
                bolts.cyl(.022, .03, loc=(s * (HALF + .055), y + dy, .9), rot=(0, R90, 0), seg=6, bevel=0)
    K.hatch_rect(a, on_glacis(.75, 0, .055), size=(.55, .55), normal=nrm)
    for dx in (-.2, 0, .2):
        K.periscope(a, on_glacis(.4, dx, .055), facing=(0, -1, 0), size=(.13, .1, .08))
    for s in (-1, 1):
        K.lamp(a, (s * .95, NOSE + .14, .8), (0, -1, .1), r=.06, mat='Armor', guard=True)
        K.tow_hook(a.part('Kit_hooks', 'Steel'), (s * .5, NOSE + .06, .5), facing=(0, -1, 0), size=.08)
        K.fender(a.part('Fenders', 'Team'), TX + .02, NOSE + .1, NOSE + .6, .8, .48, s, lip=.035)
    # The engine deck: two louvre banks, the rear exhaust grille, tail lamps, the tow cable.
    K.grille(a, (.45, 2.35, DECK + .01), .7, .9, facing=(0, 0, 1), slats=6, frame_mat='Armor')
    K.grille(a, (-.45, 2.35, DECK + .01), .7, .9, facing=(0, 0, 1), slats=6, frame_mat='Armor')
    K.grille(a, (.55, TAIL + .03, .75), .6, .25, facing=(0, 1, 0), slats=4, frame_mat='Armor')
    a.pivot('Point_exhaust', (.55, TAIL - .04, .8))
    K.soot(a, (.55, TAIL + .1, .78), radius=.6, k=.45)
    a.pivot('Point_fire', (0, 1.0, 1.1))
    for s in (-1, 1):
        a.part('Tail_lamps', 'LavaGlow').box((.1, .01, .06), loc=(s * .9, TAIL + .03, .9), bevel=0)
    K.tow_cable(a.part('Tow_cable', 'Steel'), [(.9, TAIL + .02, .55), (.2, TAIL + .04, .6), (-.6, TAIL + .03, .55)],
                r=.025)
    # Stowage bins on the rear fenders, water cans, Team bands.
    for s in (-1, 1):
        P.toolbox(a, (s * (TX + .08), 2.55, DECK + .12), (.38, .9, .26), mat='Armor')
        a.part('Team_band', 'Team').box((.012, 2.4, .1), loc=(s * (HALF + .055), .3, .58), bevel=0)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (-(TX + .1), 1.6, DECK + .02), rot=(0, 0, R90))
    K.jerrycan(a.part('Jerrycans', 'Fuel'), ((TX + .1), 1.6, DECK + .02), rot=(0, 0, R90))


def _skirts(a):
    for s in (-1, 1):
        K.side_skirt(a, TX + .27, NOSE + .55, TAIL - .2, .96, .4, s, panels=4, t=.04, mat='Team', bolts=False,
                     hinged=False)
        a.part('Skirt_edge', 'Rubber').box((.03, TAIL - NOSE - .8, .06), loc=(s * (TX + .27), (TAIL + NOSE) / 2 + .2,
                                                                         .53), bevel=0)


def _turret(a):
    t = a.pivot('Turret', TURRET)
    body = a.part('Turret_body', 'Team', t)
    rings = []
    for z, f, wf, w, r in ((0, -1.05, .7, 1.0, 1.15), (.32, -1.12, .75, 1.04, 1.2), (.5, -.85, .62, .95, 1.12)):
        rings.append([(-wf, f, z), (wf, f, z), (w, f + .4, z), (w, r, z), (-w, r, z), (-w, f + .4, z)])
    k.sharp_loft(body, rings, chamfer=.035)
    K.turret_ring(a.part('Turret_steel', 'Steel', t), (0, 0, -.04), .82, h=.05)
    # Bolted flat cheek modules; the bustle autoloader with its blow-out panels.
    arm = a.part('Turret_armor', 'Armor', t)
    bolts = a.part('Kit_bolts', 'Steel', t)
    for s in (-1, 1):
        k.block(arm, (.05, 1.2, .34), loc=(s * 1.06, .0, .08), chamfer=.015)
        for dy in (-.45, 0, .45):
            bolts.cyl(.02, .03, loc=(s * 1.09, dy, .36), rot=(0, R90, 0), seg=6, bevel=0)
    bus = a.part('Bustle', 'Team', t)
    k.extrude(bus, [(1.1, .02), (1.85, .06), (1.9, .44), (1.1, .48)], 1.7, axis='X', chamfer=.03, corner=.02)
    pan = a.part('Blowout_panels', 'Armor', t)
    for x in (-.42, .42):
        pan.box((.72, .55, .02), loc=(x, 1.5, .47), bevel=0)
    # The bolted mantlet, the 105 mm gun, its fume extractor and pepper-pot brake; the coax.
    mant = a.part('Mantlet', 'Armor', t)
    k.block(mant, (.62, .28, .4), loc=(0, -1.16, .08), chamfer=.04)
    for dx in (-.24, .24):
        for dz in (.14, .4):
            bolts.cyl(.02, .03, loc=(dx, -1.31, dz), rot=K.FORWARD, seg=6, bevel=0)
    k.lathe(a.part('Main_cannon', 'Steel', t), [(.085, 0), (.085, .25), (.065, .3), (.06, 2.1), (0, 2.1)],
            loc=(0, -1.3, .3), rot=K.FORWARD, seg=12, worn=(1,))
    k.lathe(a.part('Fume_extractor', 'Armor', t), [(.06, 0), (.1, .06), (.1, .42), (.06, .48)], loc=(0, -2.15, .3),
            rot=K.FORWARD, seg=12, worn=(1, 2))
    brake = a.part('Muzzle_brake', 'Undercarriage', t)
    k.lathe(brake, [(.06, 0), (.095, .03), (.095, .32), (.07, .35), (0, .35)], loc=(0, -3.38, .3), rot=K.FORWARD,
            seg=12)
    holes = a.part('Brake_holes', 'Rubber', t)
    for i in range(4):
        for u in (0, 1):
            holes.box((.02, .05, .2), loc=((-.097 if u else .097), -3.45 - i * .07, .3), bevel=0)
    a.pivot('Muzzle_main', (0, -3.75, .3), t)
    k.lathe(a.part('Coax', 'Steel', t), [(.025, 0), (.025, .3), (0, .31)], loc=(.3, -1.22, .34), rot=K.FORWARD, seg=6)
    a.pivot('Muzzle_coax', (.3, -1.53, .34), t)
    # The gunner's sight head, the commander's cupola with its M2, the loader's hatch.
    k.block(a.part('Sight', 'Armor', t), (.3, .34, .24), loc=(.5, -.7, .5), chamfer=.03)
    a.part('Glass', 'Glass', t).box((.22, .012, .12), loc=(.5, -.875, .6), bevel=0)
    K.hatch_round(a, (.4, .25, .5), r=.26, parent=t, periscopes=0, seg=10)
    k.lathe(a.part('Cupola', 'Armor', t), [(.36, 0), (.36, .1), (.3, .16), (0, .16)], loc=(-.45, .1, .5), seg=12,
            worn=(1,))
    for i in range(3):
        u = -R90 + (i - 1) * .6
        K.periscope(a, (-.45 + math.cos(u) * .3, .1 + math.sin(u) * .3, .58), facing=(math.cos(u), math.sin(u), 0),
                    parent=t, size=(.1, .08, .07))
    P.raised_gun(a, (-.45, .1, .64), parent=t, pivot='Mount_mg', barrel='MG', brake='MG_flash', muzzle='Muzzle_mg',
                 riser=.02, ring_r=.2, post=.06, length=.95, shield=False, ring=False, mat='Armor', tag='_cdr')
    for s in (-1, 1):
        K.smoke_dischargers(a, .98, -.65, .3, s, count=3, parent=t)
    # Stowage on the bustle's sides, a tarp roll, whips, the Team band.
    st = a.part('Stowage', 'Canvas', t)
    rack = a.part('Racks', 'Steel', t)
    for s in (-1, 1):
        k.block(st, (.2, .55, .26), loc=(s * 1.0, 1.4, .2), chamfer=.05, taper=(.9, .9))
        rack.tube([(s * .95, 1.1, .42), (s * 1.12, 1.1, .42), (s * 1.12, 1.75, .42), (s * .95, 1.75, .42)], .015,
                  seg=4)
    P.canvas_roll(a, (0, 1.93, .3), 1.4, r=.08)
    K.whip_antenna(a.part('Turret_steel', 'Steel', t), (-.8, 1.55, .48), h=.36, r=.02, lean=.15)
    K.whip_antenna(a.part('Turret_steel', 'Steel', t), (.8, 1.55, .48), h=.34, r=.02, lean=.15)
    a.part('Team_band', 'Team', t).box((1.4, .4, .012), loc=(0, -.35, .505), bevel=0)
    K.soot(a, (0, -3.25, 1.3), radius=.45, k=.35)


def airborne_light_tank(a):
    """The airborne light tank: see the module docstring."""
    _hull(a)
    P.track_run(a, TX, TW, WHEELS, WR, sprocket=(2.42, .5, .25), idler=(-1.98, .47, .24), rollers=(),
                roller_z=.74, wheel_w=.15, hide_top=(-1.8, 2.2, .62), disc_mat='Armor', wheel_seg=9)
    _skirts(a)
    _turret(a)
    k.clean(a)


BUILDERS = {
    'airborne_light_tank': (airborne_light_tank, dict(ao_distance=.5, grime_height=.55)),
}
