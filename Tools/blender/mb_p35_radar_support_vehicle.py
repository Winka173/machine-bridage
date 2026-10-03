"""Prompt 35 wave 10 (lane B): the radar support vehicle rebuilt from scratch (spec:
Tools/blender/specs/radar_support_vehicle.json).

A Giraffe AMB / Kasta-class mobile radar on a 4x4 (the def's modelSize 4.6 x 2.0 x 4.0 m; class Scout,
hmg_selfdef_15): the armoured bonneted cab (the bonnet with its grille and lamps, the raked two-piece windscreen with
wipers, side windows, doors and steps, mirrors), the remote 12.7 mm station on a raised ring over the cab roof
(`Turret`: the roof-gun rule), four wheels on two axles with fenders and mud flaps, the equipment shelter on the
bed (Team bands, louvres, the A/C unit, a door with steps, cable ports), the generator box, four stabiliser jacks on
outriggers, the telescopic mast in three sections with its guy points and the flat phased array on its turning head
(`Radar`: the panel, the cell grid, the IFF bar, the head box), whips, jerrycans, a spare wheel.

Runtime nodes kept: `Turret` (0, -1.4, 1.75), `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Radar` (0, 1.3, 3.2),
`Point_fire`, `Point_exhaust` (Part_wheel / Part_wheelb come from the prompt 34 wrapper). Built only from
frontier_kit / mb_kit27 primitives, mb_kit35 and lane B's helpers; no other model's builder. Metres, +Z up, -Y
front, +X left. Under 7,500 triangles.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
WR, WW, TRACK = .46, .3, .8
AXLES = (-1.5, 1.5)
BED = 1.05


def _chassis(a):
    fr = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        K.chamfer_box(fr, (.1, 4.3, .22), loc=(s * .38, 0, .78), c=.02)
    susp = a.part('Suspension', 'Steel')
    for y in AXLES:
        for s in (-1, 1):
            P.tread_wheel(a, (s * TRACK, y, WR), WR, WW, s, seg=12, rim_seg=8, nuts=6, depth=.05)
            K.dust(a, (s * TRACK, y, .1), radius=.85, k=.3)
            P.leaf_pack(susp, s * .38, y, WR + .2, .9, leaves=3)
        K.axle(a.part('Axles', 'Undercarriage'), y, WR, .5, r=.08, diff=True)
    for s in (-1, 1):
        fen = a.part('Fenders', 'Armor')
        for y in AXLES:
            k.block(fen, (.36, 1.1, .05), loc=(s * TRACK, y, 1.05), chamfer=0)
            P.mudflap(a, (s * TRACK, y + .56, 1.03), w=.34, h=.36)
    P.fuel_tank(a, (-.68, -.25, .62), .8, .2)
    a.pivot('Point_fire', (0, 0, 1.5))


def _cab(a):
    """The armoured bonneted cab: bonnet y -2.3..-1.6, cab -1.6..-.7, roof 1.7."""
    cab = a.part('Cab', 'Team')
    rings = []
    for y, top, half, zb in ((-2.3, .98, .82, .7), (-1.65, 1.3, .9, .65), (-1.55, 1.75, .95, .65),
                             (-.7, 1.75, .95, .65)):
        rings.append([(-half, y, zb), (half, y, zb), (half, y, top - .15), (half - .1, y, top), (-half + .1, y, top),
                      (-half, y, top - .15)])
    k.sharp_loft(cab, rings, chamfer=.03)
    K.grille(a, (0, -2.31, .84), .9, .22, facing=(0, -1, 0), slats=6, frame_mat='Armor')
    k.block(a.part('Bumper', 'Armor'), (1.9, .15, .2), loc=(0, -2.35, .72), chamfer=.02)
    K.windscreen(a, [(-.85, -1.6, 1.32), (.85, -1.6, 1.32), (.8, -1.45, 1.68), (-.8, -1.45, 1.68)], frame_mat='Armor',
                 wipers=2)
    glass = a.part('Glass', 'Glass')
    for s in (-1, 1):
        glass.box((.02, .45, .3), loc=(s * .955, -1.15, 1.45), bevel=0)
        a.part('Door_seams', 'Undercarriage').box((.012, .02, .8), loc=(s * .958, -.85, 1.1), bevel=0)
        K.handle(a.part('Kit_handles', 'Steel'), (s * .97, -1.0, 1.25), (s * .97, -.85, 1.25), (s, 0, 0), h=.035)
        P.step(a, (s * .85, -1.15, .55), w=.34, d=.2)
        K.mirror(a.part('Cab_fit', 'Steel'), (s * .96, -1.55, 1.5), s, arm=.04, size=(.04, .1, .2))
        K.lamp(a, (s * .65, -2.32, .88), (0, -1, 0), r=.08, mat='Armor', guard=True)
        a.part('Lamps', 'Alloy').box((.1, .02, .05), loc=(s * .78, -2.31, .94), bevel=0)
    K.exhaust(a, (-.85, -1.2, .5), r=.04, length=.3, direction=(0, 0, -1), muffler=False, cap=False)
    a.pivot('Point_exhaust', (.6, 2.3, .8))
    # The remote 12.7 mm station on a raised ring over the cab roof.
    P.raised_gun(a, (0, -1.4, 1.75 - .2), parent=None, pivot='Turret', barrel='Main_cannon', brake='Muzzle_brake',
                 muzzle='Muzzle_main', riser=.13, ring_r=.3, post=.05, length=.7, shield=True, ring=True,
                 shield_k=.7)
    k.block(a.part('Rws_sensor', 'Armor'), (.2, .22, .18), loc=(-.4, -1.2, 1.76), chamfer=.02)
    a.part('Glass', 'Glass').box((.14, .012, .09), loc=(-.4, -1.315, 1.8), bevel=0)


def _body(a):
    k.block(a.part('Bed', 'Armor'), (1.9, 3.0, .1), loc=(0, .8, BED), chamfer=.02)
    W_, D_, H_ = 1.85, 2.0, 1.0
    W2 = a.part('Shelter', 'Plaster')
    k.block(W2, (W_, D_, H_), loc=(0, .45, BED + .05 + H_ / 2), chamfer=.04)
    for s in (-1, 1):
        a.part('Team_band', 'Team').box((.012, D_, .12), loc=(s * (W_ / 2 + .006), .45, BED + .85), bevel=0)
    K.grille(a, (.93, .2, BED + .6), .5, .35, facing=(1, 0, 0), slats=4)
    k.block(a.part('Ac_unit', 'PlasterWhite'), (.5, .18, .4), loc=(-.4, 1.54, BED + .6), chamfer=.015)
    a.part('Doors', 'Armor').box((.55, .02, .85), loc=(.45, 1.46, BED + .5), bevel=0)
    P.step(a, (.45, 1.65, BED - .25), w=.4, d=.2)
    for x in (-.6, -.3):
        a.part('Cable_ports', 'Steel').cyl(.05, .06, loc=(x, 1.47, BED + .3), rot=(R90, 0, 0), seg=8, bevel=0)
    k.block(a.part('Generator', 'Armor'), (1.3, .55, .55), loc=(0, 2.0, BED + .33), chamfer=.03)
    K.grille(a, (0, 2.28, BED + .35), .8, .3, facing=(0, 1, 0), slats=4)
    for y in (-.35, 2.15):
        for s in (-1, 1):
            K.outrigger(a.part('Outriggers', 'Steel'), a.part('Jack_pads', 'Steel'), (s * .9, y, BED - .05), s,
                        reach=.06, drop=BED - .2, w=.14)
    # The telescopic mast in three sections, collars and guy points, on a base box at the shelter's rear.
    mx, my = 0, 1.3
    k.block(a.part('Mast_base', 'Armor'), (.5, .5, .2), loc=(mx, my, BED + H_ + .05), chamfer=.02)
    for i, (r, z0, z1) in enumerate(((.13, BED + H_ + .15, 2.55), (.1, 2.5, 2.95), (.075, 2.9, 3.15))):
        k.lathe(a.part('Mast', 'Steel'), [(r, z0), (r, z1), (r + .02, z1), (r + .02, z1 + .05)], loc=(mx, my, 0), seg=8)
    for s in (-1, 1):
        a.part('Guy_points', 'Steel').box((.06, .06, .06), loc=(s * .14, my, 2.5), bevel=0)
    a.part('Kit_cables', 'Rubber').tube([(mx + .15, my, 2.4), (mx + .2, my - .1, BED + H_ + .2),
                                         (-.2, .9, BED + H_ + .05)], .025, seg=3)
    r = a.pivot('Radar', (mx, my, 3.2))
    k.block(a.part('Radar_head', 'Armor', r), (.35, .3, .25), loc=(0, 0, .02), chamfer=.02)
    k.extrude(a.part('Radar_panel', 'PlasterWhite', r), [(-.7, -.06), (.7, -.06), (.65, .06), (-.65, .06)], .65,
              loc=(0, -.12, .42), rot=(-.2, 0, 0), axis='Z', chamfer=.012)
    cells = a.part('Radar_cells', 'Undercarriage', r)
    for i in range(5):
        for j in range(3):
            cells.box((.22, .02, .17), loc=(-.52 + i * .26, -.19 - (j - 1) * .04, .42 + (j - 1) * .2),
                      rot=(-.2, 0, 0), bevel=0)
    k.block(a.part('Radar_cabin', 'Armor', r), (1.3, .08, .12), loc=(0, -.1, .8), chamfer=.01)
    # Whips, jerrycans, spare wheel, the beacon.
    for x in (-.8, .8):
        K.whip_antenna(a.part('Antennas', 'Steel'), (x, 1.35, BED + H_ + .05), h=1.1, r=.02, lean=.1)
    K.jerrycan(a.part('Jerrycans', 'Armor'), (.65, -.65, BED + .05))
    K.jerrycan(a.part('Jerrycans', 'Armor'), (.35, -.65, BED + .05))
    k.lathe(a.part('Spare_wheel', 'Rubber'), [(.22, -.13), (.42, -.13), (.46, -.09), (.46, .09), (.42, .13),
                                             (.22, .13)], loc=(-.6, -.55, BED + .5), rot=(0, R90, 0), seg=12,
            caps=(False, False))
    K.beacon(a, (.6, -.2, BED + H_ + .05), r=.06)


def radar_support_vehicle(a):
    _chassis(a)
    _cab(a)
    _body(a)
    k.clean(a)


BUILDERS = {'radar_support_vehicle': (radar_support_vehicle, dict(ao_distance=.5, grime_height=.6))}
