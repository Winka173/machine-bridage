"""Prompt 35 wave 7 (lane C): the guard tower's gun-nest branch rebuilt from scratch (spec: Tools/blender/specs/guard_tower_b.json).

guard_tower.nest (autocannon_25, the def's tower_ac25: an M242 25 mm; vision 48 against the base's 60) as an upgrade
of the guard tower (mb_p27_wave6, trimmed in wave 2): the base's cast blockhouse kept at its 3.5 x 3.5 m footprint
(the door, the firing slits, the wall lamp, the base plates and the stubs of the steel corner legs, in the base's
Concrete / Armor / Steel), the lattice and the cabin taken down and the roof turned into a gun nest: a steel deck
with its grate, Team kick plates and railings, a sandbag parapet, the shielded M242 on its pedestal turret (`Turret`:
the cradle, the feed chute, the ammunition box), the 40 mm launcher on its socket on the parapet (`Mount_gun` /
`Muzzle_gun`, kept from the old file), ready-ammunition boxes, the ladder up the side, a whip and the beacon.

Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Mount_gun`, `Muzzle_gun`. Metres, +Z up,
-Y front, +X left. Under 6,000 triangles (owner decision 6).
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w2parts as W

R90 = math.pi / 2
TAU = math.tau
H = 2.94            # blockhouse height (the base's)
D = H + .14         # deck top


def _blockhouse(a):
    k.extrude(a.part('Blockhouse', 'Concrete'), [(-1.75, -1.75), (1.75, -1.75), (1.75, 1.75), (-1.75, 1.75)], H,
              loc=(0, 0, H / 2 - .02), axis='Z', chamfer=.05, corner=.06, taper=(.97, .97), caps=(False, True))
    W.lift_lines(a, (0, -1.72, 0), 'x', 3.3, (.9, 1.8), -1)
    W.lift_lines(a, (0, 1.72, 0), 'x', 3.3, (.9, 1.8), 1)
    # The door at the rear, the firing slits, the wall lamp, the stencil plate.
    K.door(a, (0, 1.76, .3), (.9, 1.8), normal=(0, 1, 0), mat='Armor')
    sl = a.part('Slits', 'Undercarriage')
    for x in (-.8, .8):
        sl.box((.5, .04, .14), loc=(x, -1.735, 2.2), bevel=0)
    for s in (-1, 1):
        sl.box((.04, .5, .14), loc=(s * 1.735, -.6, 2.2), bevel=0)
        sl.box((.04, .5, .14), loc=(s * 1.735, .7, 2.2), bevel=0)
    K.lamp(a, (.72, 1.78, 2.25), (0, 1, -.3), r=.07, guard=True)
    a.part('Stencil', 'PlasterWhite').box((.7, .02, .2), loc=(-.72, 1.76, 2.05), bevel=0)
    # The stubs of the base tower's steel legs on their base plates at the corners.
    for sx in (-1, 1):
        for sy in (-1, 1):
            a.part('Base_plates', 'Steel').box((.34, .34, .06), loc=(sx * 1.6, sy * 1.6, .31), bevel=0)
            leg = a.part('Tower_frame', 'Armor')
            leg.box((.16, .16, H + .45), loc=(sx * 1.6, sy * 1.6, .3 + (H + .45) / 2), bevel=.02)
            a.part('Leg_gussets', 'Steel').box((.04, .3, .3), loc=(sx * 1.6, sy * 1.6 - sy * .2, D - .2),
                                               rot=(sy * .6, 0, 0), bevel=0)
    # The battered plinth round the foot of the walls, bolt rows on the leg base plates.
    k.extrude(a.part('Base', 'Concrete'), [(-1.9, -1.9), (1.9, -1.9), (1.9, 1.9), (-1.9, 1.9)], .4,
              loc=(0, 0, .2), axis='Z', chamfer=.03, taper=(.9, .9), caps=(False, True))
    bp = a.part('Kit_bolts', 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            W.bolt_grid(bp, (sx * 1.6, sy * 1.6, .34), 2, 2, .2)
    # Wall kit: junction boxes and conduits with clamps, the field telephone box, vent grilles, rung handles.
    fit = a.part('Fittings', 'Steel')
    for x, y, nx, ny in ((-1.2, -1.76, 0, -1), (1.2, -1.76, 0, -1), (-1.76, .2, -1, 0), (1.76, -.2, 1, 0),
                         (1.2, 1.76, 0, 1)):
        fit.box((.2 if nx == 0 else .08, .08 if nx == 0 else .2, .26), loc=(x + nx * .03, y + ny * .03, 1.4), bevel=0)
        fit.box((.04 if nx == 0 else .04, .04, 1.0), loc=(x + nx * .04, y + ny * .04, 2.0), bevel=0)
        for zc in (1.7, 2.1, 2.5):
            fit.box((.08 if nx == 0 else .06, .06 if nx == 0 else .08, .03), loc=(x + nx * .05, y + ny * .05, zc),
                    bevel=0)
    k.block(a.part('Phone_box', 'Armor'), (.3, .12, .36), loc=(-1.2, 1.8, 1.3), chamfer=.015)
    for s in (-1, 1):
        K.grille(a, (s * 1.76, .9, 1.1), .5, .3, facing=(s, 0, 0), slats=4, frame_mat='Concrete')
    K.grille(a, (0, -1.76, 1.0), .6, .3, facing=(0, -1, 0), slats=4, frame_mat='Concrete')
    # The plinth's kit: jerrycans and a fuel drum against the left wall, the spare barrel case on the right ledge.
    K.fuel_drum(a.part('Fuel_drums', 'BarrelRed'), a.part('Kit_bands', 'Steel'), (1.55, -.9, .4), r=.18, h=.55)
    k.block(a.part('Barrel_case', 'Wood'), (.18, 1.2, .16), loc=(-1.8, -.6, .48), chamfer=.02)
    for i in range(6):
        u = i * TAU / 6
        K.dust(a, (math.cos(u) * 2.0, math.sin(u) * 2.0, 0), radius=1.0, k=.3)


def _deck(a):
    k.block(a.part('Walkway', 'Armor'), (3.6, 3.6, .14), loc=(0, 0, D - .07), chamfer=.02)
    a.part('Walkway_grate', 'Undercarriage').box((3.3, 3.3, .02), loc=(0, 0, D + .005), bevel=0)
    kp = a.part('Kick_plates', 'Team')
    for s in (-1, 1):
        kp.box((3.58, .03, .16), loc=(0, s * 1.79, D + .06), bevel=0)
        kp.box((.03, 3.58, .16), loc=(s * 1.79, 0, D + .06), bevel=0)
    # The sandbag parapet round the front and sides (open at the rear for the ladder), the rear railing.
    W.bags(a, [(1.55, .9, D), (1.55, -1.55, D), (-1.55, -1.55, D), (-1.55, .9, D)], layers=2, bag=(.5, .28, .16),
           seed=61)
    W.bags(a, [(1.55, .5, D + .32), (1.55, -1.55, D + .32), (-1.55, -1.55, D + .32), (-1.55, .5, D + .32)], layers=1,
           bag=(.42, .24, .13), seed=66)
    K.railing(a.part('Railing', 'Steel'), [(-1.72, 1.0, D), (-1.72, 1.72, D), (1.72, 1.72, D), (1.72, 1.35, D)], h=1.0,
              post=.8)
    K.ladder(a.part('Ladder', 'Steel'), (1.86, 1.05, .4), (1.8, 1.05, D + .9), width=.45, step=.3)
    # Ready-ammunition boxes, a whip, the beacon.
    W.stack(a, (-1.0, 1.1, D), n=3, size=(.5, .28, .2), yaw=.1, seed=62)
    W.stack(a, (.55, 1.25, D), n=2, size=(.5, .28, .2), yaw=-.2, seed=63)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (-1.3, .3, D), rot=(0, 0, .2))
    K.crate(a.part('Crates', 'Crate'), a.part('Kit_straps', 'Steel'), (.45, .35, .3), (1.0, .55, D), bands=1)
    k.block(a.part('Radio', 'Armor'), (.3, .2, .25), loc=(-1.25, -.4, D + .125), chamfer=.015)
    a.part('Radio_handset', 'Rubber').tube([(-1.12, -.4, D + .2), (-1.0, -.55, D + .1), (-.9, -.7, D + .02)], .015,
                                           seg=4)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-1.5, 1.55, D), h=1.4, r=.022)
    # Distinct small kit: the gas bottle, an extinguisher, the spotting scope on its tripod, a sand bucket, a horn.
    k.lathe(a.part('Gas_bottles', 'Steel'), [(.1, 0), (.1, .7), (.06, .78), (.03, .82), (0, .84)], loc=(1.3, 1.45, D),
            seg=8, worn=(1,))
    k.lathe(a.part('Extinguishers', 'BarrelRed'), [(.07, 0), (.07, .38), (.04, .44), (0, .46)], loc=(-.2, 1.5, D),
            seg=8, worn=(1,))
    sc = a.part('Scope', 'Armor')
    k.lathe(sc, [(.05, 0), (.05, .08), (.035, .1), (.035, .38), (.045, .42), (0, .44)], loc=(-1.1, -1.1, D + .75),
            rot=K.FORWARD, seg=8)
    for j in range(3):
        u = j * TAU / 3
        a.part('Scope_tripod', 'Steel').limb((-1.1, -1.0, D + .72), (-1.1 + math.cos(u) * .25, -1.0 + math.sin(u) * .25,
                                                                     D), .015, .015, bevel=0)
    k.lathe(a.part('Buckets', 'Crate'), [(.1, 0), (.13, .25), (.12, .26), (0, .03)], loc=(.2, 1.45, D), seg=8)
    k.lathe(a.part('Horn', 'PlasterWhite'), [(.03, 0), (.04, .1), (.14, .3), (.13, .31)], loc=(-1.6, 1.6, D + 1.0),
            rot=(R90 + .3, 0, 2.6), seg=8, caps=(False, False))
    cases = a.part('Spent_cases', 'Gilded')
    for i, (x, y, yaw) in enumerate(((.5, .3, .3), (.7, .1, 1.2), (.35, .55, 2.0), (-.4, .4, -.4), (-.6, .2, .9))):
        k.lathe(cases, [(.022, 0), (.022, .2), (.016, .24), (0, .24)], loc=(x, y, D + .03), rot=(R90, 0, yaw), seg=6)
    K.beacon(a, (-1.5, 1.55, D + .02), r=.06)


def _gun(a):
    """The shielded M242 on its pedestal turret."""
    k.lathe(a.part('Pedestal', 'Armor'), [(.42, 0), (.42, .06), (.2, .1), (.16, .55), (.22, .6), (0, .6)],
            loc=(-.35, -.2, D), seg=12, worn=(1, 3))
    t = a.pivot('Turret', (-.35, -.2, D + .6))
    cr = a.part('Gun_cradle', 'Armor', t)
    for s in (-1, 1):
        k.block(cr, (.04, .55, .32), loc=(s * .16, -.05, .14), chamfer=.01)
    k.lathe(cr, [(.04, -.2), (.04, .2)], loc=(0, -.05, .2), rot=(0, R90, 0), seg=8)
    rc = a.part('Gun_receiver', 'Undercarriage', t)
    k.block(rc, (.22, .9, .24), loc=(0, .05, .22), chamfer=.02)
    L = 1.85
    k.lathe(a.part('Main_cannon', 'Steel', t), [(.05, 0), (.05, .2), (.035, .25), (.03, L), (0, L)],
            loc=(0, -.4, .24), rot=K.FORWARD, seg=8, worn=(1,))
    k.lathe(a.part('Muzzle_brake', 'Undercarriage', t), [(.03, 0), (.05, .03), (.05, .2), (.04, .22), (0, .22)],
            loc=(0, -.4 - L + .05, .24), rot=K.FORWARD, seg=8)
    a.pivot('Muzzle_main', (0, -.4 - L - .19, .24), t)
    sh = a.part('Gun_shield', 'Team', t)
    k.extrude(sh, [(-.6, -.25), (.6, -.25), (.55, .45), (.2, .52), (-.2, .52), (-.55, .45)], .04,
              loc=(0, -.55, .2), rot=(R90 - .15, 0, 0), axis='Z', chamfer=.01, corner=.01)
    for s in (-1, 1):
        k.extrude(sh, [(-.2, -.25), (.2, -.25), (.18, .4), (-.18, .4)], .035, loc=(s * .66, -.42, .2),
                  rot=(R90, 0, s * .6), axis='Z', chamfer=.008)
    a.part('Gun_sight', 'Armor', t).box((.1, .2, .12), loc=(-.22, -.3, .52), bevel=0)
    a.part('Glass', 'Glass', t).box((.07, .01, .06), loc=(-.22, -.405, .53), bevel=0)
    k.block(a.part('Ammo_boxes', 'Crate', t), (.24, .4, .3), loc=(.3, .2, .12), chamfer=.015)
    a.part('Feed_chute', 'Steel', t).tube([(.2, .1, .26), (.12, 0, .3), (.08, -.1, .28)], .04, seg=5)
    # The 40 mm launcher on its socket on the left front parapet (the old Mount_gun / Muzzle_gun).
    a.part('AGL_socket', 'Steel').cyl(.05, .3, loc=(1.15, -1.5, D + .65), seg=6, bevel=0)
    m = a.pivot('Mount_gun', (1.15, -1.5, D + .82))
    ag = a.part('AGL', 'Undercarriage', m)
    k.block(ag, (.2, .5, .18), loc=(0, 0, .05), chamfer=.015)
    a.part('AGL', 'Steel', m).cyl(.04, .35, loc=(0, -.4, .07), rot=K.FORWARD, seg=6, bevel=0)
    k.block(a.part('AGL_ammo', 'Crate', m), (.16, .2, .16), loc=(.17, .05, .02), chamfer=.01)
    a.pivot('Muzzle_gun', (0, -.58, .07), m)


def guard_tower_b(a, detail=False):
    """The gun-nest branch (see the module docstring)."""
    _blockhouse(a)
    _deck(a)
    _gun(a)
    k.clean(a)


BUILDERS = {
    'guard_tower_b': (guard_tower_b, dict(ao_distance=.6, grime_height=.4, ao_strength=.65)),
}
