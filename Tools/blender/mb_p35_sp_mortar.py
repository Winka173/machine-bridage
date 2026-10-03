"""Prompt 35 wave 10 (lane B): the self-propelled mortar rebuilt to prompt 35's standard (spec:
Tools/blender/specs/sp_mortar.json), keeping what fix L8 got right (DECISIONS "Sửa lỗi tổng hợp L8"): a Patria AMV
8x8 with the AMOS twin 120 mm mortar turret (the def's modelSize 6.3 x 2.3 x 2.5 m; amos_120, the 12.7 mm
self-defence MG on the roof): the raked glacis, the tapered flanks and wheel arches, axles, the driver's hatch with
vision blocks, stowage bins, smoke dischargers, the faceted twin-mortar turret and the roof MG where they were.

Prompt 35 adds what the scan asked for (tiers, brightness regions, a hull lower than the old 2.73 m): the AMV's
wedge nose with the trim vane, the engine deck front right with its louvres and exhaust, the double wishbones on
every wheel, the add-on side armour with bolts, the turret's two long barrels side by side in their big welded
mantlet with the recoil sleeves, the sight heads, the loader's and commander's hatches, the roof MG on a raised
ring with its shield (the roof-gun rule), the rear door with steps, tail lamps, mud flaps, mirrors, a net roll,
jerrycans, whips and Team bands.

Runtime nodes kept: `Turret` (0, 0.5, 1.75), `Turret_body`, `Turret_armor`, `Turret_bustle`, `Main_cannon` / `_2`,
`Muzzle_brake` / `_2`, `Muzzle_main` (0, -1.85, 2.5), `Mount_mg` / `Muzzle_mg`, `Point_fire`, `Point_exhaust`.
Built only from frontier_kit / mb_kit27 primitives, mb_kit35 and lane B's helpers; no other model's builder.
Metres, +Z up, -Y front, +X left. Under 7,500 triangles.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
WR, WW, TRACK = .46, .3, .93
AXLES = (-2.1, -1.05, .45, 1.5)
FRONT, REAR = -3.05, 3.15
HALF = 1.0
ROOF = 1.72


def _hatch(a, loc, r=None, size=None, parent=None):
    """A lean hatch: a round lid on its collar (r) or a square plate (size), the hinge and the handle."""
    x, y, z = loc
    if r:
        k.lathe(a.part('Hatches', 'Armor', parent), [(r, 0), (r, .06), (r * .9, .1), (0, .11)], loc=loc, seg=10)
        hy = y + r
    else:
        k.block(a.part('Hatches', 'Armor', parent), (size[0], size[1], .05), loc=loc, chamfer=.01)
        hy = y + size[1] / 2
    a.part('Kit_hinges', 'Steel', parent).box((.2, .05, .05), loc=(x, hy, z + .04), bevel=0)
    a.part('Kit_handles', 'Steel', parent).box((.14, .03, .03), loc=(x, y - (r or size[1] / 2) * .5, z + .1), bevel=0)


def _running_gear(a):
    frame = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        K.chamfer_box(frame, (.12, 5.4, .22), loc=(s * .42, 0, .6), c=.02)
    susp = a.part('Suspension', 'Steel')
    for y in AXLES:
        for s in (-1, 1):
            P.tread_wheel(a, (s * TRACK, y, WR), WR, WW, s, seg=10, rim_seg=6, nuts=0, depth=.05)
            K.dust(a, (s * TRACK, y, .1), radius=.85, k=.28)
            susp.tube([(s * .42, y - .22, WR + .05), (s * (TRACK - .2), y, WR + .02),
                       (s * .42, y + .22, WR + .05)], .03, seg=4)
        K.axle(a.part('Axles', 'Undercarriage'), y, WR, .5, r=.08, diff=y in (AXLES[1], AXLES[2]))
    a.pivot('Point_fire', (0, 0, 1.9))


def _hull(a):
    hull = a.part('Hull', 'Team')
    rings = []
    # The AMV's sections: a wedge nose (the long lower glacis), vertical lower sides, upper sides leaning in.
    for y, yb, zr, wl in ((FRONT, FRONT + .75, .95, .55), (FRONT + .45, FRONT + .75, 1.3, .8),
                          (FRONT + 1.25, FRONT + 1.1, ROOF, 1.0), (REAR - .1, REAR, ROOF, 1.0),
                          (REAR, REAR, ROOF - .12, 1.0)):
        rings.append([(-.45, yb, .52), (.45, yb, .52), (HALF * wl, yb, .85), (HALF * wl, y, 1.25),
                      (HALF * wl - .18, y, zr), (-HALF * wl + .18, y, zr), (-HALF * wl, y, 1.25), (-HALF * wl, yb, .85)])
    k.sharp_loft(hull, rings, chamfer=.035)
    # The trim vane folded on the nose, the tow hooks, the lamps.
    k.block(a.part('Trim_vane', 'Armor'), (1.3, .06, .4), loc=(0, FRONT + .2, 1.05), rot=(-.6, 0, 0), chamfer=.01)
    for s in (-1, 1):
        a.part('Kit_hooks', 'Steel').box((.1, .12, .1), loc=(s * .45, FRONT + .3, .7), bevel=0)
        K.lamp(a, (s * .7, FRONT + .55, 1.22), (0, -1, .2), r=.06, mat='Armor', guard=False)
        K.mirror(a.part('Cab_fit', 'Steel'), (s * (HALF - .15), FRONT + 1.1, 1.62), s, arm=.05, size=(.03, .1, .14))
    # Add-on side armour panels with bolts, fenders and mud flaps.
    arm = a.part('Armor', 'Armor')
    bolts = a.part('Kit_bolts', 'Steel')
    for s in (-1, 1):
        for y, L in ((-1.6, .5), (-.3, 1.2), (1.0, .5), (2.4, 1.1)):
            k.block(arm, (.05, L, .4), loc=(s * (HALF + .025), y, 1.08), chamfer=.012)
            for dy in (-L * .38, L * .38):
                bolts.box((.03, .04, .04), loc=(s * (HALF + .055), y + dy, 1.22), bevel=0)
        fen = a.part('Fenders', 'Undercarriage')
        for y0, y1 in ((AXLES[0] - .52, AXLES[1] + .52), (AXLES[2] - .52, AXLES[3] + .52)):
            k.block(fen, (.3, y1 - y0, .04), loc=(s * TRACK, (y0 + y1) / 2, .98), chamfer=0)
            P.mudflap(a, (s * TRACK, y1, .74), w=.32, h=.28)
        a.part('Team_band', 'Team').box((.012, 4.0, .09), loc=(s * (HALF + .006), .3, 1.38), bevel=0)
    # Driver front left (hatch, vision blocks), engine deck front right (louvres, exhaust).
    _hatch(a, (.45, FRONT + 1.5, ROOF), size=(.45, .5))
    glass = a.part('Glass', 'Glass')
    for dx in (-.12, .12):
        glass.box((.12, .02, .08), loc=(.45 + dx, FRONT + 1.22, ROOF - .03), rot=(.5, 0, 0), bevel=0)
    K.grille(a, (-.45, FRONT + 1.0, 1.5), .6, .45, facing=(0, -.6, .8), slats=6, frame_mat='Armor')
    K.grille(a, (-.45, FRONT + 1.75, ROOF + .01), .55, .5, facing=(0, 0, 1), slats=5, frame_mat='Armor')
    K.exhaust(a, (-HALF - .04, -1.5, 1.4), r=.05, length=.25, direction=(0, 0, 1), muffler=False, cap=True)
    a.pivot('Point_exhaust', (-.9, -1.5, 1.7))
    K.soot(a, (-HALF - .05, -1.5, 1.7), radius=.5, k=.45)
    for s in (-1, 1):
        for y in (.2, 1.4):
            glass.box((.02, .2, .09), loc=(s * (HALF - .09), y, 1.6), rot=(0, s * .45, 0), bevel=0)
    # Rear door, steps, tail lamps; stowage bins, jerrycans, net roll, whips.
    K.plate(a.part('Hatches', 'Armor'), (1.0, .04, .95), loc=(0, REAR + .015, 1.1))
    K.hinge(a.part('Kit_hinges', 'Steel'), (-.35, REAR + .04, .64), (.35, REAR + .04, .64), r=.025, knuckles=3)
    K.handle(a.part('Kit_handles', 'Steel'), (.35, REAR + .04, 1.15), (.35, REAR + .04, 1.35), (0, 1, 0), h=.04)
    for s in (-1, 1):
        a.part('Tail_lamps', 'LavaGlow').box((.1, .01, .07), loc=(s * .8, REAR + .02, 1.5), bevel=0)
        P.step(a, (s * .35, REAR + .1, .56), w=.28, d=.18)
    P.toolbox(a, (HALF + .08, 2.2, 1.45), (.16, 1.2, .4), mat='Armor')
    P.toolbox(a, (-HALF - .08, 2.2, 1.45), (.16, 1.2, .4), mat='Armor')
    K.jerrycan(a.part('Jerrycans', 'Armor'), (.55, REAR - .35, ROOF))
    K.jerrycan(a.part('Jerrycans', 'Armor'), (.25, REAR - .35, ROOF))
    K.net_roll(a.part('Stowage', 'Canvas'), a.part('Kit_straps', 'Undercarriage'), (-.4, REAR - .35, ROOF + .02),
               length=.9, r=.12, axis='X')
    for x in (-.8, .8):
        K.whip_antenna(a.part('Antennas', 'Steel'), (x, 2.6, ROOF), h=.8, r=.02, lean=.15)


def _turret(a):
    """The AMOS twin 120 mm turret (`Turret`): faceted body, bustle, the welded mantlet, two barrels, hatches, MG."""
    t = a.pivot('Turret', (0, .5, 1.75))
    k.extrude(a.part('Turret_body', 'Armor', t), [(-.75, -1.3), (.75, -1.3), (1.0, -.7), (1.0, .7), (.85, 1.0),
                                                  (-.85, 1.0), (-1.0, .7), (-1.0, -.7)], .55, loc=(0, 0, .3),
              axis='Z', chamfer=.04, corner=.04, taper=(.82, .86), caps=(False, True))
    k.extrude(a.part('Turret_bustle', 'Armor', t), [(-.8, .9), (.8, .9), (.85, 1.6), (.65, 1.85), (-.65, 1.85),
                                                    (-.85, 1.6)], .45, loc=(0, 0, .3), axis='Z', chamfer=.03,
              corner=.03, taper=(.9, .9), caps=(False, True))
    top = .575
    k.block(a.part('Turret_armor', 'Team', t), (1.25, .55, .6), loc=(0, -1.35, .42), chamfer=.06, taper=(.9, .85))
    for i, x in enumerate((-.28, .28)):
        sfx = '' if i == 0 else '_2'
        base = (x, -1.6, .72)
        k.lathe(a.part('Recoil_sleeves', 'Armor', t), [(.15, 0), (.15, .45), (.12, .5)], loc=base, rot=K.FORWARD,
                seg=10)
        k.lathe(a.part('Main_cannon' + sfx, 'Steel', t), [(.11, .45), (.1, .6), (.1, .75), (0, .75)],
                loc=base, rot=K.FORWARD, seg=10, worn=(1,))
        k.lathe(a.part('Muzzle_brake' + sfx, 'Undercarriage', t), [(.1, .7), (.125, .72), (.125, .75), (.08, .75),
                                                                   (0, .74)], loc=base, rot=K.FORWARD, seg=10)
    a.pivot('Muzzle_main', (0, -2.35, .75), t)
    # Sight heads, hatches, vents, the raised roof MG (Mount_mg), smoke dischargers, Team band, hazard marks.
    for x, w in ((.55, .25), (-.55, .2)):
        k.block(a.part('Sight', 'Armor', t), (w, .3, .25), loc=(x, -.6, top), chamfer=.03)
        a.part('Glass', 'Glass', t).box((w * .8, .02, .12), loc=(x, -.76, top + .14), bevel=0)
    _hatch(a, (-.35, .35, top), r=.3, parent=t)
    _hatch(a, (.35, .5, top), size=(.42, .45), parent=t)
    P.raised_gun(a, (.7, .6, top - .02), parent=t, pivot='Mount_mg', barrel='MG_barrel', brake='MG_brake',
                 muzzle='Muzzle_mg', riser=.05, ring_r=.25, post=.06, length=.85, shield=True, ring=True, tag='_mg',
                 shield_k=.6)
    for s in (-1, 1):
        K.smoke_dischargers(a, s * .95, -.4, .5, s, count=2, parent=t)
        a.part('Turret_band', 'Team', t).box((.02, 1.4, .1), loc=(s * .96, .1, .45), rot=(0, -s * .12, 0), bevel=0)
    k.block(a.part('Bins', 'Crate', t), (1.3, .25, .3), loc=(0, 1.95, .5), chamfer=.02)


def sp_mortar(a):
    _running_gear(a)
    _hull(a)
    _turret(a)
    k.clean(a)


BUILDERS = {'sp_mortar': (sp_mortar, dict(ao_distance=.5, grime_height=.6))}
