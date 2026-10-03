"""Prompt 35 wave 3 (lane B): the mortar carrier rebuilt from scratch (spec: Tools/blender/specs/mortar_carrier.json).

An M1064-class 120 mm mortar carrier on the M113 hull (unit_sheet: the rear roof hatch opened wide, the 120 mm
mortar raised through it; 0.8 x the real vehicle; the def's modelSize 4.21 x 2.3 x 3.2 m with the tube up): the
aluminium box hull with its rounded plate edges, the long sloped glacis with the folded trim vane, the driver's hatch
and periscopes front left, the engine grilles and exhaust front right; the big three-leaf mortar hatch over the rear
roof folded open (the leaves standing up and out), and in the well the mortar on its turntable (`Turret`): the
traverse ring, the bipod and elevation mechanism (`Elevation`), the sight with its collimator, the long tube raised
70 degrees with its blast ring (`Muzzle_main` at the mouth), ready rounds in a rack beside it; the dismount baseplate
carried on the left side, the bipod legs and aiming stakes stowed; the commander's cupola with the M2 on its raised
ring behind a shield (`Mount_mg`, the free self-defence gun; MODEL_STANDARD "Roof guns"); five road wheels a side,
the front sprocket, the rear idler, the track; smoke launchers, the rear ramp and fuel tanks; Team bands.

Its own hull: nothing is taken from the smoke carrier (another M113 with a smoke generator, mb_p35_smoke_carrier).
Runtime nodes kept: `Turret`, `Muzzle_main`, `Mount_mg`, `Muzzle_mg`, `Point_exhaust`, `Point_fire`; old part names
`Hull`, `Mortar_tube`, `Mortar_tube_ring`, `Hatch_well`, `Hatch_lids`, `Sight`, `MG`, `MG_ammo`, `MG_shield`; named
for the gate: `Elevation` (the mantlet role), `Idlers`, `Skirt_edge` (the sponson lip hides the top run), `Stowage`.
Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
HALF = 1.02
ROOF = 1.5
LIP = .82
WR = .26
WHEELS = (-1.28, -.65, -.02, .61, 1.24)
TX, TW = .8, .36
HATCH = (0, .85, ROOF)           # the mortar hatch's centre
ELEV = math.radians(70)


def _hull(a):
    hull = a.part('Hull', 'Team')
    prof = [(2.06, LIP), (-1.72, LIP), (-2.08, .88), (-2.08, .96), (-1.25, ROOF), (2.04, ROOF), (2.06, ROOF - .05)]
    k.extrude(hull, prof, HALF * 2, axis='X', chamfer=.09, corner=.03)
    k.extrude(a.part('Hull_lower', 'Armor'), [(2.02, .38), (-1.6, .38), (-2.05, .66), (-2.07, LIP + .02),
                                              (2.02, LIP + .02)], 1.3, axis='X', chamfer=.03, corner=.02)
    lip = a.part('Skirt_edge', 'Armor')
    for s in (-1, 1):
        lip.box((.04, 3.7, .09), loc=(s * (HALF - .02), .17, LIP - .03), bevel=0)
        a.part('Team_band', 'Team').box((.012, 2.0, .1), loc=(s * (HALF + .006), -.7, ROOF - .22), bevel=0)
    # Trim vane on the glacis, its hinges; lamps; tow hooks; smoke launchers on the glacis corners.
    g0, g1 = (-2.08, .96), (-1.25, ROOF)
    ang = math.atan2(g1[1] - g0[1], g1[0] - g0[0])
    c = (0, g0[0] + (g1[0] - g0[0]) * .5 - math.sin(ang) * .04, g0[1] + (g1[1] - g0[1]) * .5 + math.cos(ang) * .04)
    K.plate(a.part('Trim_vane', 'Armor'), (HALF * 2 - .25, .66, .04), loc=c, rot=(ang, 0, 0), chamfer=.012)
    for x in (-.65, .65):
        K.hinge(a.part('Kit_hinges', 'Steel'), (x - .1, -2.1, .92), (x + .1, -2.1, .92), r=.02, knuckles=2)
    for s in (-1, 1):
        K.lamp(a, (s * .9, -2.1, .86), (0, -1, 0), r=.055, mat='Armor', guard=True)
        K.tow_hook(a.part('Kit_hooks', 'Steel'), (s * .5, -2.08, .6), facing=(0, -1, 0), size=.07)
        K.smoke_dischargers(a, HALF - .32, -1.38, ROOF - .06, s, count=3)
    # Driver's hatch and periscopes (front left), engine grilles (front right), the exhaust on the right side.
    K.hatch_round(a, (.55, -.95, ROOF), r=.28, periscopes=3, seg=10)
    K.grille(a, (-.5, -.9, ROOF + .02), .65, .55, facing=(0, 0, 1), slats=5, frame_mat='Armor')
    K.exhaust(a, (-HALF - .05, -1.05, 1.15), r=.055, length=.42, direction=(0, 0, 1), muffler=False, cap=True)
    a.pivot('Point_exhaust', (-HALF - .05, -1.05, 1.6))
    K.soot(a, (-HALF - .05, -1.05, 1.6), radius=.4, k=.4)
    a.pivot('Point_fire', (0, .3, 1.3))
    # The rear: the ramp seams and door, hinges, the armoured fuel tanks either side, tail lamps.
    dark = a.part('Hull_dark', 'Undercarriage')
    for x in (-.6, .6):
        dark.box((.02, .012, .95), loc=(x, 2.065, .98), bevel=0)
    K.plate(a.part('Hatches', 'Armor'), (.42, .04, .75), loc=(-.22, 2.07, 1.0))
    for x in (-.42, .42):
        K.hinge(a.part('Kit_hinges', 'Steel'), (x - .1, 2.09, .52), (x + .1, 2.09, .52), r=.022, knuckles=2)
    for s in (-1, 1):
        k.block(a.part('Fuel_tanks', 'Armor'), (.34, .26, .85), loc=(s * .9, 2.19, 1.0), chamfer=.04)
        a.part('Tail_lamps', 'LavaGlow').box((.09, .01, .06), loc=(s * .9, 2.325, 1.28), bevel=0)


def _mortar_hatch(a):
    """The three-leaf mortar hatch over the rear roof, folded open: the well's coaming and the leaves standing out."""
    x0, y0, z0 = HATCH
    k.ring(a.part('Hatch_well', 'Armor'), [(.62, 0), (.7, 0), (.7, .06), (.62, .06)], loc=HATCH, seg=18)
    k.lathe(a.part('Hatch_floor', 'Undercarriage'), [(.66, -.02), (0, -.02)], loc=(x0, y0, z0 - .3), seg=14)
    lids = a.part('Hatch_lids', 'Armor')
    hin = a.part('Hatch_fittings', 'Steel')
    for i, u in enumerate((math.radians(90), math.radians(210), math.radians(330))):
        cx, cy = x0 + math.cos(u) * .7, y0 + math.sin(u) * .7
        # Each leaf hinged on the coaming, swung up past vertical and leaning out.
        k.block(lids, (.72, .05, .58), loc=(cx + math.cos(u) * .1, cy + math.sin(u) * .1, z0 + .3),
                rot=(.25, 0, u - R90), chamfer=.015)
        K.hinge(hin, (cx - math.sin(u) * .25, cy + math.cos(u) * .25, z0 + .05),
                (cx + math.sin(u) * .25, cy - math.cos(u) * .25, z0 + .05), r=.022, knuckles=2)


def _mortar(a):
    t = a.pivot('Turret', (HATCH[0], HATCH[1], HATCH[2] - .25))
    k.ring(a.part('Turret_steel', 'Steel', t), [(.45, -.03), (.55, -.03), (.55, .05), (.45, .05)], seg=16)
    k.lathe(a.part('Turret_armor', 'Armor', t), [(.5, 0), (.5, .06), (0, .07)], seg=16)
    g = P.Elev((0, .3, .12), ELEV)
    # The breech cap and base socket, the tube raised 70 degrees with its blast ring, the muzzle.
    tube = a.part('Mortar_tube', 'Steel', t)
    k.lathe(tube, [(.11, 0), (.11, .14), (.085, .2), (.08, 1.85), (0, 1.85)], loc=g.at(0), rot=g.lathe_rot, seg=12,
            worn=(1,))
    k.lathe(a.part('Mortar_tube_ring', 'Undercarriage', t), [(.08, 0), (.12, .03), (.12, .12), (.09, .14), (0, .14)],
            loc=g.at(1.8), rot=g.lathe_rot, seg=12)
    a.pivot('Muzzle_main', g.at(1.98), t)
    # The bipod and the elevation mechanism (the gate's mantlet), the traversing screw and the sight.
    yoke = g.at(1.0)
    el = a.part('Elevation', 'Armor', t)
    k.block(el, (.24, .16, .16), loc=yoke, rot=g.box_rot, chamfer=.02)
    for s in (-1, 1):
        el.limb((yoke[0] + s * .05, yoke[1], yoke[2] - .05), (s * .42, -.35, .05), .045, .045, bevel=0)
    a.part('Elevation_screw', 'Steel', t).limb((0, yoke[1] + .02, yoke[2] - .08), (0, -.1, .08), .04, .04, bevel=0)
    sight = a.part('Sight', 'Armor', t)
    k.block(sight, (.12, .18, .14), loc=(yoke[0] + .2, yoke[1], yoke[2] + .1), chamfer=.015)
    a.part('Glass', 'Glass', t).box((.08, .01, .06), loc=(yoke[0] + .2, yoke[1] - .095, yoke[2] + .12), bevel=0)
    # Ready rounds in a rack on the well's right side.
    rack = a.part('Round_rack', 'Wood', t)
    rounds = a.part('Rounds', 'Hazard', t)
    rack.box((.06, .5, .45), loc=(-.48, .05, .25), bevel=0)
    for j in range(4):
        k.lathe(rounds, [(0, 0), (.06, .06), (.06, .4), (.03, .55), (0, .6)], loc=(-.42, -.15 + j * .13, .02), seg=8)
    return t


def _cupola(a):
    loc = (-.5, -.15, ROOF)
    cup = a.part('Cupola', 'Armor')
    k.ring(cup, [(.36, 0), (.44, 0), (.44, .12), (.39, .15), (.36, .15)], loc=loc, seg=14, worn=(2,))
    glass = a.part('Glass', 'Glass')
    for i in range(5):
        u = i * math.tau / 5 + .2
        x, y = loc[0] + math.cos(u) * .43, loc[1] + math.sin(u) * .43
        cup.box((.11, .08, .08), loc=(x, y, ROOF + .1), rot=(0, 0, u + R90), bevel=0)
        glass.box((.08, .01, .04), loc=(x + math.cos(u) * .045, y + math.sin(u) * .045, ROOF + .11),
                  rot=(0, 0, u + R90), bevel=0)
    P.raised_gun(a, (loc[0], loc[1], ROOF + .15), pivot='Mount_mg', barrel='MG', brake='MG_flash',
                 muzzle='Muzzle_mg', riser=.06, ring_r=.37, post=.14, length=1.05, shield=True, shield_k=.85,
                 tag='_cdr')
    k.block(a.part('MG_ammo', 'Crate'), (.12, .28, .18), loc=(loc[0] - .55, loc[1] + .1, ROOF + .09), chamfer=.012)


def _stowage(a):
    """The dismount baseplate on the left side, the bipod legs and aiming stakes stowed, crates on the roof."""
    bp = a.part('Baseplate', 'Armor')
    k.lathe(bp, [(.42, 0), (.42, .04), (.3, .08), (.12, .1), (0, .1)], loc=(HALF + .02, .7, 1.1), rot=(0, R90, 0),
            seg=14, worn=(1,))
    a.part('Kit_straps', 'Steel').box((.02, .06, .9), loc=(HALF + .12, .7, 1.1), bevel=0)
    for s in (-1, 1):
        a.part('Kit_brackets', 'Steel').box((.1, .06, .06), loc=(HALF + .03, .7 + s * .35, 1.1), bevel=0)
    st = a.part('Stowage', 'Canvas')
    k.lathe(st, [(.06, -.7), (.06, .7)], loc=(-HALF - .05, .9, 1.25), rot=K.FORWARD, seg=8)    # the stakes' bag
    poles = a.part('Aiming_posts', 'Hazard')
    for j in range(3):
        poles.cyl(.018, 1.2, loc=(-HALF - .04, .9 + (j - 1) * .05, 1.36), rot=(R90, 0, 0), seg=5, bevel=0)
    K.crate(a.part('Crates', 'Crate'), a.part('Kit_straps', 'Steel'), (.5, .4, .25), (.6, -.25, ROOF), bands=1)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (-HALF + .15, 1.85, ROOF), rot=(0, 0, R90))


def mortar_carrier(a):
    """The mortar carrier: see the module docstring."""
    _hull(a)
    P.track_run(a, TX, TW, WHEELS, WR, sprocket=(-1.85, .58, .24), idler=(1.9, .46, .23), rollers=(),
                wheel_w=.14, hide_top=(-1.7, 1.75, .66), disc_mat='Armor', wheel_seg=9, link_pitch=.22)
    _mortar_hatch(a)
    _mortar(a)
    _cupola(a)
    _stowage(a)
    k.clean(a)


BUILDERS = {
    'mortar_carrier': (mortar_carrier, dict(ao_distance=.45, grime_height=.55)),
}
