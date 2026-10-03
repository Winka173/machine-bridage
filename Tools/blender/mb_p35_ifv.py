"""Prompt 35 wave 3 (lane B): the infantry fighting vehicle rebuilt from scratch (spec: Tools/blender/specs/ifv.json).

An M2A2 Bradley (unit_sheet: 0.8 x the real vehicle; the def's modelSize 5.48 x 3.02 x 2.5 m): the tall box hull with
its steep upper glacis and lower nose plate, the driver's hatch and periscopes on the front left, the engine grilles
and exhaust on the front right, the big rear ramp with its door; six road wheels a side, the front sprocket, the rear
idler and a linked track under bolted armour skirts (they hide the return rollers: not built); the two-man
turret set off to the left: the 30 mm cannon in its mantlet with the coaxial machine gun beside it, the twin TOW
launcher box on the turret's left cheek on its arm (the runtime raises it: `Launcher_*`, `Tubes`, `Muzzle_missile` stay direct children of `Turret`),
the gunner's sight head, the commander's viewer and hatch, three-tube smoke grenade launchers on both front corners,
the stowage basket at the turret's rear, a pintle machine gun for the commander on a post (MODEL_STANDARD "Roof
guns"); stowage boxes, water cans and the Team bands on the hull.

Its own hull: nothing is taken from the elite APC or the other tracked models.
Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Coax`, `Muzzle_coax`, `Launcher_box`,
`Launcher_arm`, `Tubes`, `Muzzle_missile`, `Point_exhaust`, `Point_fire`; named for the gate: `Mantlet`, `Idlers`,
`Skirts`, `Mount_mg`, `Stowage`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TX, TW = 1.12, .46
WR = .29
WHEELS = (-1.78, -1.12, -.46, .2, .86, 1.52)
ROOF = 1.52
NOSE, TAIL = -2.72, 2.62
HALF = 1.42                      # the upper hull's half width
TURRET = (.22, -.15, ROOF)


def _hull(a):
    hull = a.part('Hull', 'Team')
    prof = [(TAIL, .5), (TAIL + .02, ROOF - .04), (TAIL - .06, ROOF), (-.85, ROOF), (NOSE + .18, 1.0),
            (NOSE, .82), (NOSE + .35, .48)]
    k.extrude(hull, prof, HALF * 2, axis='X', chamfer=.05, corner=.02)
    low = a.part('Hull_lower', 'Armor')
    k.extrude(low, [(TAIL - .05, .38), (NOSE + .5, .38), (NOSE + .35, .52), (TAIL - .05, .52)], 1.8, axis='X',
              chamfer=.02)
    # The glacis: the driver's hatch and periscopes (left), the engine grilles (right), headlamps, tow hooks.
    g0, g1 = (NOSE + .18, 1.0), (-.85, ROOF)
    ang = math.atan2(g1[1] - g0[1], g1[0] - g0[0])
    def on_glacis(f, x, up=.0):
        y = g0[0] + (g1[0] - g0[0]) * f
        z = g0[1] + (g1[1] - g0[1]) * f
        return (x, y - math.sin(ang) * up, z + math.cos(ang) * up)
    K.hatch_rect(a, on_glacis(.62, .65, .02), size=(.55, .6), normal=(0, -math.sin(ang), math.cos(ang)))
    for dx in (-.2, 0, .2):
        K.periscope(a, on_glacis(.35, .65 + dx, .02), facing=(0, -1, 0), size=(.14, .1, .09))
    K.grille(a, on_glacis(.55, -.6, .03), .9, .7, facing=(0, -math.sin(ang), math.cos(ang)), slats=6,
             frame_mat='Armor')
    for s in (-1, 1):
        K.lamp(a, (s * 1.2, NOSE + .14, .96), (0, -1, .1), r=.06, mat='Armor', guard=True)
        K.tow_hook(a.part('Kit_hooks', 'Steel'), (s * .55, NOSE + .1, .62), facing=(0, -1, 0), size=.08)
    # The exhaust louvre on the right side front, its soot.
    K.grille(a, (-HALF - .01, -1.75, 1.25), .5, .25, facing=(-1, 0, 0), slats=3, frame_mat='Armor')
    a.pivot('Point_exhaust', (-HALF - .05, -1.75, 1.25))
    K.soot(a, (-HALF - .05, -1.6, 1.25), radius=.5, k=.4)
    a.pivot('Point_fire', (0, .9, 1.7))
    # The rear ramp: its seams, the door, hinges, tail lamps, the trim of fuel cell boxes either side.
    dark = a.part('Hull_dark', 'Undercarriage')
    for x in (-.75, .75):
        dark.box((.02, .012, 1.0), loc=(x, TAIL + .025, .98), bevel=0)
    dark.box((1.5, .012, .02), loc=(0, TAIL + .025, 1.47), bevel=0)
    K.plate(a.part('Hatches', 'Armor'), (.5, .04, .85), loc=(-.25, TAIL + .03, .98))
    K.handle(a.part('Kit_handles', 'Steel'), (-.05, TAIL + .05, .9), (-.05, TAIL + .05, 1.05), (0, 1, 0), h=.04)
    for x in (-.5, .5):
        K.hinge(a.part('Kit_hinges', 'Steel'), (x - .12, TAIL + .05, .52), (x + .12, TAIL + .05, .52), r=.025,
                knuckles=2)
    for s in (-1, 1):
        a.part('Tail_lamps', 'LavaGlow').box((.1, .01, .07), loc=(s * 1.15, TAIL + .03, 1.35), bevel=0)
    # Fenders over the tracks, stowage boxes on the rear of them, water cans, Team bands above the skirts.
    fen = a.part('Fenders', 'Team')
    for s in (-1, 1):
        K.fender(fen, TX + .06, NOSE + .3, TAIL, 1.14, .55, s, lip=.03)
        P.toolbox(a, (s * (TX + .08), 1.95, 1.3), (.42, .9, .32), mat='Armor')
        a.part('Team_band', 'Team').box((.012, 2.8, .12), loc=(s * (HALF + .006), -.4, 1.35), bevel=0)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (-(TX + .08), 1.1, 1.14), rot=(0, 0, R90))
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (-(TX + .08), .8, 1.14), rot=(0, 0, R90))


def _skirts(a):
    """Bolted armour skirts the full length (four panels a side), a row of big bolts on each."""
    sk = a.part('Skirts', 'Team')
    bolts = a.part('Kit_bolts', 'Steel')
    L = (TAIL - .1 - NOSE - .45) / 4
    for s in (-1, 1):
        for i in range(4):
            yc = NOSE + .45 + (i + .5) * L
            k.block(sk, (.05, L - .03, .56), loc=(s * (TX + .28), yc, .86), chamfer=0)
            for j in range(2):
                bolts.cyl(.025, .03, loc=(s * (TX + .31), yc - L * .3 + j * L * .6, 1.05), rot=(0, R90, 0), seg=5,
                          bevel=0)
        a.part('Skirt_edge', 'Rubber').box((.03, TAIL - NOSE - .6, .08), loc=(s * (TX + .28), (TAIL + NOSE) / 2 + .1,
                                                                           .55), bevel=0)


def _turret(a):
    t = a.pivot('Turret', TURRET)
    body = a.part('Turret_body', 'Team', t)
    rings = []
    for z, f, w, r in ((0, -.95, .92, 1.05), (.42, -1.0, .92, 1.1), (.66, -.65, .8, 1.0)):
        rings.append([(-w * .7, f, z), (w * .7, f, z), (w, f + .35, z), (w, r - .1, z), (w - .1, r, z),
                      (-w + .1, r, z), (-w, r - .1, z), (-w, f + .35, z)])
    k.sharp_loft(body, rings, chamfer=.04)
    K.turret_ring(a.part('Turret_steel', 'Steel', t), (0, 0, -.04), .82, h=.06)
    # Spaced armour plates bolted on the turret cheeks.
    arm = a.part('Turret_armor', 'Armor', t)
    for s in (-1, 1):
        k.block(arm, (.05, .9, .38), loc=(s * .95, -.1, .22), chamfer=0)
    # The mantlet, the 30 mm gun, the coax beside it.
    k.block(a.part('Mantlet', 'Armor', t), (.5, .3, .32), loc=(-.1, -1.05, .32), chamfer=.04)
    k.lathe(a.part('Main_cannon', 'Steel', t), [(.07, 0), (.07, .3), (.045, .35), (.035, 1.5), (0, 1.5)],
            loc=(-.1, -1.2, .32), rot=K.FORWARD, seg=10, worn=(1,))
    k.lathe(a.part('Muzzle_brake', 'Undercarriage', t), [(.035, 0), (.055, .02), (.055, .18), (.04, .2), (0, .2)],
            loc=(-.1, -2.68, .32), rot=K.FORWARD, seg=10)
    a.pivot('Muzzle_main', (-.1, -2.9, .32), t)
    k.lathe(a.part('Coax', 'Steel', t), [(.025, 0), (.025, .4), (0, .41)], loc=(-.38, -1.1, .3), rot=K.FORWARD, seg=6)
    a.pivot('Muzzle_coax', (-.38, -1.52, .3), t)
    # The TOW launcher on its arm on the left cheek (direct children of the turret: the runtime raises them).
    a.part('Launcher_arm', 'Armor', t).box((.12, .5, .3), loc=(.94, .25, .3), bevel=0)
    lb = a.part('Launcher_box', 'Team', t)
    k.block(lb, (.42, 1.15, .42), loc=(1.08, -.05, .32), chamfer=.03)
    tubes = a.part('Tubes', 'Undercarriage', t)
    for dz in (-.1, .1):
        tubes.cyl(.08, .03, loc=(1.08, -.64, .53 + dz), rot=K.FORWARD, seg=10, bevel=0)
        a.part('Tube_rims', 'Steel', t).box((.36, .02, .02), loc=(1.08, -.63, .53 + dz + .1), bevel=0)
    a.pivot('Muzzle_missile', (1.08, -.7, .53), t)
    # The gunner's sight head (right front), the commander's viewer, the hatches.
    gs = a.part('Sight', 'Armor', t)
    k.block(gs, (.32, .4, .3), loc=(-.5, -.55, .8), chamfer=.03)
    a.part('Glass', 'Glass', t).box((.24, .01, .14), loc=(-.5, -.755, .84), bevel=0)
    K.periscope(a, (-.45, .35, .66), facing=(0, -1, 0), parent=t, size=(.22, .22, .2))
    K.hatch_round(a, (-.45, .55, .66), r=.3, parent=t, periscopes=2, seg=10)
    K.hatch_round(a, (.4, .3, .66), r=.28, parent=t, periscopes=1, seg=10)
    for s in (-1, 1):
        K.smoke_dischargers(a, .72, -.78, .5, s, count=3, parent=t)
    # The stowage basket at the turret rear with bags and a rolled tarp.
    st = a.part('Stowage', 'Canvas', t)
    rack = a.part('Racks', 'Steel', t)
    rack.tube([(-.85, 1.0, .1), (-.85, 1.45, .1), (.85, 1.45, .1), (.85, 1.0, .1)], .02, seg=4)
    rack.tube([(-.85, 1.0, .45), (-.85, 1.45, .45), (.85, 1.45, .45), (.85, 1.0, .45)], .02, seg=4)
    for x in (-.85, -.3, .3, .85):
        rack.box((.03, .03, .36), loc=(x, 1.45, .27), bevel=0)
    for (x, w) in ((-.5, .55), (.2, .5), (.62, .3)):
        k.block(st, (w, .38, .3), loc=(x, 1.22, .27), chamfer=.06, taper=(.92, .9))
    P.canvas_roll(a, (0, 1.25, .5), 1.4, r=.09)
    a.part('Team_band', 'Team', t).box((1.2, .8, .015), loc=(0, .2, .67), bevel=0)
    K.whip_antenna(a.part('Turret_steel', 'Steel', t), (-.75, .9, .66), h=.32, r=.02, lean=.15)
    K.whip_antenna(a.part('Turret_steel', 'Steel', t), (.75, .9, .66), h=.3, r=.02, lean=.15)
    # The commander's pintle M240 on a post by his hatch (the roof-gun rule).
    P.raised_gun(a, (-.45, .1, .66), parent=t, pivot='Mount_mg', barrel='MG', brake='MG_flash', muzzle='Muzzle_mg',
                 riser=.05, ring_r=.2, post=.1, length=.85, shield=False, ring=False, mat='Armor', tag='_cdr')


def ifv(a):
    """The infantry fighting vehicle: see the module docstring."""
    _hull(a)
    P.track_run(a, TX, TW, WHEELS, WR, sprocket=(-2.38, .58, .26), idler=(2.2, .48, .25), rollers=(),
                roller_z=.82, wheel_w=.16, hide_top=(-2.2, 2.0, .7), disc_mat='Armor', wheel_seg=9)
    _skirts(a)
    _turret(a)
    k.clean(a)


BUILDERS = {
    'ifv': (ifv, dict(ao_distance=.5, grime_height=.6)),
}
