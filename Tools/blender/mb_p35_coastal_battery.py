"""Prompt 35 wave 10 (lane B): the coastal battery rebuilt from scratch (spec: Tools/blender/specs/coastal_battery.json).

unit_refs: A-222 Bereg, an AK-130 mount set ashore, K-300P Bastion-P, M284 155 mm: a shore gun position (the def's
gun_155_coastal, one barrel, turretTurnRate 18; no modelSize: the old file's 10.25 x 8.21 x 4.63 m). Not the heavy
turret's barbette: a sunken Hegemon gun pit. A battered concrete apron with its expansion joints, the round gun well
with its race and the curved front parapet (cast, stepped, with drain slots and a Team band), the single 155 mm
naval-type mount (`Turret`) in a faceted gun house offset on the race like an AK-130 single (the gun on the left,
the layer's cabin on the right with its sight hood and vision blocks), the long barrel with its fume extractor and
brake, the loading hatch and ammunition hoist at the rear of the house, a pintle MG; behind the well the earth
traverse with two ready-magazine doors in cast portals and ventilation pipes, the ready-use shell rail, the
fire-control post (a small concrete tower with the rangefinder bar and the lattice mast with the surface radar), a
floodlight, sandbags and a camouflage net over the magazine, a ladder down into the well.

Runtime nodes kept at their old places: `Turret` (0, 0.4, 2.04), `Muzzle_main` (-0.5, -5.99, 2.89). Built only from
frontier_kit / mb_kit27 primitives, mb_kit35, the wave 2 helpers and lane B's; no other model's builder. Metres, +Z
up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w2parts as W
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
AP = .12               # apron height
WELL = 1.55            # gun well floor (the race's top)
TY, TZ = .4, 2.04


def _apron(a):
    k.extrude(a.part('Base', 'Concrete'), [(-4.0, -3.4), (-1.6, -3.9), (1.6, -3.9), (4.0, -3.4), (4.1, 3.0),
                                           (3.3, 4.2), (-3.4, 4.2), (-4.1, 3.0)], AP, loc=(0, 0, AP / 2), axis='Z',
              corner=.06, taper=(.97, .97), caps=(False, True))
    j = a.part('Base_joints', 'Undercarriage')
    for v in (-2.4, -1.2, 0, 1.2, 2.4, 3.6):
        j.box((7.9, .03, .01), loc=(0, v, AP + .003), bevel=0)
    for v in (-2.6, 2.6):
        j.box((.03, 7.9, .01), loc=(v, 0, AP + .003), bevel=0)
    # The gun well: a battered round plinth up to the race, its deck seams, the race ring.
    k.lathe(a.part('Block_well', 'Plaster'), [(3.0, AP), (2.75, WELL - .1), (2.7, WELL), (0, WELL)], loc=(0, TY, 0),
            seg=20, worn=(1,))
    for z in (.6, 1.1):
        r = 3.0 - .25 * (z - AP) / (WELL - .1 - AP) + .01
        a.part('Lift_joints', 'Undercarriage').torus(r, .015, loc=(0, TY, z), seg=20, ring=3)
    k.ring(a.part('Race', 'Steel'), [(2.2, WELL - .02), (2.35, WELL - .02), (2.35, WELL + .08), (2.2, WELL + .08)],
           loc=(0, TY, 0), seg=18)
    bolts = a.part('Kit_bolts', 'Steel')
    for i in range(16):
        u = i * TAU / 16
        bolts.cyl(.04, .05, loc=(math.cos(u) * 2.45, TY + math.sin(u) * 2.45, WELL + .02), seg=4, bevel=0)
    # The curved front parapet: stepped cast wall round the front arc, drain slots, a Team band.
    wall = a.part('Walls', 'Plaster')
    for i in range(9):
        u0 = math.radians(205 + i * 14.4)
        u1 = u0 + math.radians(14.4)
        um = (u0 + u1) / 2
        r = 3.45
        x, y = math.cos(um) * r, TY + math.sin(um) * r
        k.extrude(wall, [(-.45, 0), (.45, 0), (.3, 1.25), (.05, 2.05), (-.25, 2.05), (-.45, 1.5)], r * (u1 - u0) + .02,
                  loc=(x, y, AP), rot=(0, 0, um + R90), axis='X', chamfer=.02)
        a.part('Drain_slots', 'Undercarriage').box((.25, .04, .1), loc=(math.cos(um) * 3.92, TY + math.sin(um) * 3.92,
                                                                         AP + .12), rot=(0, 0, um + R90), bevel=0)
    band = [(math.cos(u) * 3.84, TY + math.sin(u) * 3.84, AP + 1.1) for u in
            (math.radians(205 + d * 8) for d in range(17))]
    a.part('Team_band', 'Team').tube(band, .06, seg=4, caps=False)


def _gun(a):
    t = a.pivot('Turret', (0, TY, TZ))
    plan = [(-1.6, -1.9), (1.4, -1.9), (2.0, -1.0), (2.0, 1.9), (1.5, 2.4), (-1.5, 2.4), (-2.0, 1.9), (-2.0, -1.0)]
    h = 1.45
    k.extrude(a.part('Turret_body', 'Armor', t), plan, h, loc=(0, 0, -.45 + h / 2), axis='Z', chamfer=.05,
              corner=.05, taper=(.8, .84), caps=(False, True))
    top = -.45 + h
    a.part('Turret_band', 'Team', t).box((.03, 2.8, .25), loc=(-1.93, .4, .3), rot=(0, .1, 0), bevel=0)
    # The gun on the left: mantlet, barrel with fume extractor and brake.
    gx = -.5
    k.block(a.part('Mantlet', 'Armor', t), (.75, .55, .8), loc=(gx, -2.0, .4), chamfer=.06)
    L = 6.39 - 2.2
    k.lathe(a.part('Main_cannon', 'Steel', t), [(.2, 0), (.16, .15), (.16, 1.0), (.21, 1.1), (.21, 1.8), (.15, 1.9),
                                                (.13, L - .45), (0, L - .45)], loc=(gx, -2.2, .85), rot=K.FORWARD,
            seg=10, worn=(4,))
    k.lathe(a.part('Muzzle_brake', 'Undercarriage', t), [(.12, L - .47), (.22, L - .45), (.22, L), (.1, L), (0, L - .02)],
            loc=(gx, -2.2, .85), rot=K.FORWARD, seg=10, worn=(1,))
    for f in (.15, .3):
        a.part('Brake_ports', 'Charred', t).box((.46, .06, .07), loc=(gx, -2.2 - L + f, .85), bevel=0)
    a.pivot('Muzzle_main', (gx, -6.39, .85), t)
    # The layer's cabin on the right: a raised hood with vision blocks and the sight.
    k.extrude(a.part('Turret_cab', 'Armor', t), [(.4, -1.6), (1.6, -1.6), (1.75, -.6), (1.6, .4), (.4, .4)], .45,
              loc=(0, 0, top + .22), axis='Z', chamfer=.04, corner=.03, taper=(.88, .88), caps=(False, True))
    for x in (.7, 1.0, 1.3):
        a.part('Glass', 'Glass', t).box((.18, .03, .1), loc=(x, -1.55, top + .32), rot=(.25, 0, 0), bevel=0)
    k.block(a.part('Sight', 'Armor', t), (.3, .35, .3), loc=(1.0, -.6, top + .6), chamfer=.03)
    # Roof: loading hatch, ammunition hoist trunk at the rear, vents, the pintle MG, a whip; seams and welds.
    k.block(a.part('Hatches', 'Armor', t), (.8, .7, .06), loc=(-.6, .9, top), chamfer=0)
    K.handle(a.part('Kit_handles', 'Steel', t), (-.8, .9, top + .06), (-.4, .9, top + .06), (0, 0, 1), h=.06)
    k.block(a.part('Hoist_trunk', 'Armor', t), (.9, .7, 1.6), loc=(0, 2.5, -.3), chamfer=.04)
    for x in (-1.2, 1.2):
        k.lathe(a.part('Vents', 'Steel', t), [(.13, 0), (.13, .1), (.09, .13), (0, .13)], loc=(x, 1.8, top - .03),
                seg=8)
    K.pintle_mg(a, t, (-1.0, -.2, top), scale=1.1, post=.3, riser=.12)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (1.3, 1.9, top - .02), h=1.2, r=.022)
    K.weld(a.part('Kit_welds', 'Charred', t), [(-1.5, -.2, top + .005), (1.5, -.2, top + .005)])
    seams = a.part('Panel_seams', 'Charred', t)
    for y in (-.6, .8):
        for s in (-1, 1):
            seams.box((.02, .04, 1.2), loc=(s * 1.9, y, .2), rot=(0, -s * .1, 0), bevel=0)
    a.part('Hazard_marks', 'Hazard', t).box((1.6, .03, .1), loc=(0, 2.35, top - .3), bevel=0)


def _rear(a):
    """The earth traverse with the ready magazines, the shell rail, the fire-control post, net and fittings."""
    berm = a.part('Berm', 'Dirt')
    k.extrude(berm, [(-.9, 0), (.9, 0), (.5, 1.4), (-.5, 1.4)], 7.2, loc=(0, 3.85, AP), axis='X', caps=(True, True))
    for i, x in enumerate((-1.8, 1.8)):
        W.slab(a.part('Walls_portals', 'Plaster'), (1.5, .5, 1.5), (x, 3.0, AP), caps=(False, True))
        K.door(a, (x, 2.74, AP + .05), (.9, 1.2), normal=(0, -1, 0), mat='Armor')
        a.part('Door_hazard', 'Hazard').box((1.2, .04, .1), loc=(x, 2.74, AP + 1.4), bevel=0)
        k.lathe(a.part('Vent_pipes', 'Steel'), [(.08, 0), (.08, .6), (.14, .62), (.14, .75), (0, .78)],
                loc=(x + .5, 3.9, AP + 1.3), seg=8)
    a.part('Berm_sod', 'Grass').box((7.0, 1.2, .03), loc=(0, 4.15, AP + 1.42), bevel=0)
    rail = a.part('Shell_rail', 'Steel')
    rail.box((3.0, .08, .06), loc=(0, 2.4, AP + .7), bevel=0)
    for x in (-1.4, 1.4):
        rail.box((.06, .06, .7), loc=(x, 2.4, AP + .35), bevel=0)
    for i in range(7):
        k.lathe(a.part('Shells', 'Gilded'), [(.075, 0), (.075, .55), (.04, .7), (0, .74)],
                loc=(-1.0 + i * .33, 2.5, AP), seg=6, caps=(False, True))
    # The fire-control post at the right rear: a small cast tower, the rangefinder bar, the radar mast.
    fx, fy = -3.2, 2.2
    k.extrude(a.part('Walls_post', 'Plaster'), [(-.6, -.6), (.6, -.6), (.6, .6), (-.6, .6)], 2.4, loc=(fx, fy, AP + 1.2),
              axis='Z', corner=.08, taper=(.85, .85), caps=(False, True))
    k.block(a.part('Roof', 'Armor'), (1.25, 1.25, .12), loc=(fx, fy, AP + 2.46), chamfer=.03)
    a.part('Glass', 'Glass').box((.8, .03, .12), loc=(fx, fy - .52, AP + 2.1), rot=(.1, 0, 0), bevel=0)
    k.block(a.part('Rangefinder', 'Armor'), (1.6, .25, .22), loc=(fx, fy, AP + 2.65), chamfer=.03)
    for s in (-1, 1):
        k.lathe(a.part('Rangefinder', 'Armor'), [(.13, -.12), (.13, .12)], loc=(fx + s * .82, fy, AP + 2.65),
                rot=(0, R90, 0), seg=8)
    mast = a.part('Mast', 'Steel')
    for dx, dy in ((-.15, -.15), (.15, -.15), (0, .18)):
        mast.tube([(fx + dx, fy + dy + .3, AP + 2.5), (fx + dx * .3, fy + .3 + dy * .3, 4.25)], .025, seg=4)
    k.extrude(a.part('Radar', 'PlasterWhite'), [(-.6, -.04), (.6, -.04), (.5, .04), (-.5, .04)], .25,
              loc=(fx, fy + .3, 4.35), axis='Z', chamfer=.008)
    K.ladder(a.part('Ladders', 'Steel'), (fx + .62, fy, AP), (fx + .62, fy, AP + 2.6), width=.4, step=.3, r=.018)
    K.ladder(a.part('Ladders', 'Steel'), (2.2, 1.6, AP), (2.0, 1.4, WELL), width=.45, step=.3, r=.018)
    K.floodlight(a, (3.7, 2.8, AP), facing=(-.6, -1, -.4), pole=3.2)
    P.camo_net(a, [(-3.6, 3.2, 1.9), (3.6, 3.2, 1.9), (3.4, 4.6, 1.4), (-3.4, 4.6, 1.4)], .3, AP + .2, garnish=6,
               seed=4)
    W.bags(a, [(3.2, -3.2, AP), (3.95, -2.0, AP), (4.0, -.5, AP)], layers=2, bag=(.6, .3, .17), seed=61)
    W.bags(a, [(-4.0, -.5, AP), (-3.95, -2.0, AP), (-3.2, -3.2, AP)], layers=1, bag=(.6, .3, .17), seed=62)
    W.stack(a, (3.3, 1.2, AP), n=3, size=(.55, .3, .24), yaw=.3, seed=63)
    k.lathe(a.part('Extinguishers', 'BarrelRed'), [(.07, 0), (.07, .4), (.04, .46), (0, .48)], loc=(1.2, 2.75, AP),
            seg=8)
    for i in range(8):
        u = i * TAU / 8
        K.dust(a, (math.cos(u) * 3.7, math.sin(u) * 3.7, AP), radius=1.4, k=.3)


def coastal_battery(a):
    _apron(a)
    _gun(a)
    _rear(a)
    k.clean(a)


BUILDERS = {'coastal_battery': (coastal_battery, dict(ao_distance=.8, grime_height=.5, ao_strength=.65))}
