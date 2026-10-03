"""Prompt 35 wave 2 (lane A): the gun turret and its auto-cannon branch rebuilt from scratch on one casemate (owner
decision 4), each from its own spec (Tools/blender/specs/<id>.json). DECISIONS "Prompt 35 wave 2 (lane A)".

The sheet: a tank turret on a square concrete base with a long 120 mm barrel (unit_refs: Rh-120 L/44, a T-55 / T-72
turret buried as a fortification). A Hegemon casemate, 4.6 x 5 m: a cast apron with precast joints, the battered
(20-degree) concrete casemate with its race ring, the crew's entry box with a sloping steel hatch at the rear, sandbag
corners and a concertina coil at the front, ammunition stacks, spent cases and a floodlight on the apron. On the race:

- gun_turret (turret_gun_120): a welded Leopard-2A4-class turret, faceted and sloped, with the mantlet, the Rh-120
  L/44 barrel (thermal sleeve, fume extractor, muzzle reference collar), the coaxial MG, commander's cupola and
  loader's hatch, the gunner's sight, a panoramic periscope, smoke dischargers, Team side plates, the open stowage
  basket on the bustle and two whip antennas.
- gun_turret_b (gun_57_auto, unit_refs AU-220M 57 mm, "two barrels"): an unmanned angular gun module with a twin
  57 mm mount (each barrel with its perforated brake), the ammunition feed housing, an electro-optical sight ball,
  and the fire-control radar panel turning on a rear mast (`Radar`).

Runtime nodes (kept): `Turret`, `Main_cannon` (+ `Main_cannon_2` on _b), `Muzzle_brake` (+ `_2`), `Muzzle_main`,
`Muzzle_coax`, `Radar` (_b). Built only from frontier_kit / mb_kit27 primitives, mb_kit35 and the wave's lean helpers
(mb_p35_w2parts); no other model's builder. Metres, +Z up, -Y front, +X left. Each under 6,000 triangles.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w2parts as W

R90 = math.pi / 2
TAU = math.tau
APRON = .1
DECK = 1.25           # casemate deck
TZ = 1.34             # the Turret pivot's height (the old model's)


def casemate(a):
    """The apron, the battered casemate with its race, the rear entry, the yard round it."""
    k.extrude(a.part('Base_apron', 'Concrete'), [(-2.45, -2.5), (2.45, -2.5), (2.45, 2.3), (1.6, 2.5), (-2.45, 2.5)],
              APRON, loc=(0, 0, APRON / 2), axis='Z', corner=.05, taper=(.97, .97), caps=(False, True))
    j = a.part('Base_joints', 'Undercarriage')
    for i in range(-2, 3):
        j.box((4.7, .03, .01), loc=(0, i * 1.0, APRON + .003), bevel=0)
        j.box((.03, 4.8, .01), loc=(i * 1.0, 0, APRON + .003), bevel=0)
    # The casemate: battered walls (20 degrees), a deck with precast joints, the Team band and form ties.
    k.extrude(a.part('Base', 'Plaster'), [(-2.3, -2.3), (2.3, -2.3), (2.3, 2.3), (-2.3, 2.3)], DECK - APRON,
              loc=(0, 0, APRON + (DECK - APRON) / 2), axis='Z', chamfer=.05, corner=.08, taper=(.82, .82),
              caps=(False, True))
    dj = a.part('Deck_joints', 'Undercarriage')
    for v in (-1.3, 1.3):
        dj.box((3.6, .03, .01), loc=(0, v, DECK + .003), bevel=0)
        dj.box((.03, 3.6, .01), loc=(v, 0, DECK + .003), bevel=0)
    team = a.part('Team_band', 'Team')
    for s in (-1, 1):
        team.box((.03, 3.6, .16), loc=(s * 2.035, 0, DECK - .2), rot=(0, s * .35, 0), bevel=0)
        team.box((3.6, .03, .16), loc=(0, s * 2.035, DECK - .2), rot=(-s * .35, 0, 0), bevel=0)
    ties = a.part('Base_ties', 'Steel')
    for s in (-1, 1):
        for f in (-1.2, 0, 1.2):
            ties.cyl(.03, .03, loc=(s * 2.2, f, APRON + .35), rot=(0, R90 - s * .35, 0), seg=4, bevel=0)
            ties.cyl(.03, .03, loc=(f, -2.2 * s, APRON + .35), rot=(R90 + s * .35, 0, 0), seg=4, bevel=0)
    W.lift_lines(a, (0, -2.12, APRON), 'x', 3.9, (.6,), -1)
    k.ring(a.part('Race', 'Steel'), [(1.55, -.02), (1.68, -.02), (1.68, .06), (1.62, .1), (1.55, .1)],
           loc=(0, 0, DECK), seg=20, worn=(3,))
    eyes = a.part('Kit_hooks', 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            eyes.box((.14, .04, .08), loc=(sx * 1.85, sy * 1.85, DECK + .04), rot=(0, 0, .78 * sx * sy), bevel=0)
    # The rear entry: a cast box with a sloping steel hatch, handles, the step and a hand rail.
    k.extrude(a.part('Entry', 'Plaster'), [(-.65, -.4), (.65, -.4), (.65, .4), (-.65, .4)], .62,
              loc=(-.9, 2.5, APRON + .31), axis='Z', corner=.04, caps=(False, True))
    k.block(a.part('Hatches', 'Armor'), (1.05, .7, .06), loc=(-.9, 2.5, APRON + .64), rot=(.25, 0, 0), chamfer=.015)
    K.handle(a.part('Kit_handles', 'Steel'), (-1.15, 2.72, APRON + .74), (-.65, 2.72, APRON + .74), (0, .2, 1))
    K.hinge(a.part('Kit_hinges', 'Steel'), (-1.3, 2.22, APRON + .66), (-.5, 2.22, APRON + .66), r=.025)
    rail = a.part('Railings', 'Steel')
    rail.tube([(-1.65, 2.2, APRON), (-1.65, 2.2, APRON + 1.0), (-1.65, 2.95, APRON + 1.0), (-1.65, 2.95, APRON)], .02,
              seg=4)
    rail.tube([(-1.65, 2.2, APRON + .5), (-1.65, 2.95, APRON + .5)], .015, seg=4)
    # The yard: sandbag corners at the front, a concertina along the front edge, an ammunition stack, spent cases, a
    # jerrycan, an extinguisher, the floodlight on the rear-left corner, a sign.
    W.bags(a, [(2.4, -1.2, APRON), (2.4, -2.4, APRON), (1.2, -2.4, APRON)], layers=2, bag=(.6, .3, .17), seed=4)
    W.bags(a, [(-1.2, -2.42, APRON), (-2.4, -2.42, APRON), (-2.4, -1.6, APRON)], layers=2, bag=(.6, .3, .17), seed=5)
    K.wire_fence(a, [(-.9, -2.55, APRON), (.9, -2.55, APRON)], h=.5, post=.9, strands=2, concertina=True)
    W.stack(a, (2.15, 1.3, APRON), n=3, size=(.55, .3, .24), yaw=R90, seed=6)
    W.stack(a, (2.15, .65, APRON), n=2, size=(.55, .3, .24), yaw=R90 + .1, seed=7)
    cases = a.part('Spent_cases', 'Gilded')
    for i, (x, y, yaw) in enumerate(((1.4, 2.25, .3), (1.6, 2.1, 1.2), (1.25, 1.95, 2.0), (1.75, 2.35, -.4))):
        k.lathe(cases, [(.065, 0), (.065, .5), (.05, .58), (0, .58)], loc=(x, y, APRON + .065),
                rot=(R90, 0, yaw), seg=6)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (2.0, 2.15, APRON), rot=(0, 0, .2))
    k.lathe(a.part('Extinguishers', 'BarrelRed'), [(.07, 0), (.07, .4), (.04, .46), (0, .48)], loc=(-.1, 2.45, APRON),
            seg=8, worn=(1,))
    K.floodlight(a, (2.3, 2.35, APRON), facing=(-.4, -1, -.5), pole=2.6)
    a.part('Signs', 'PlasterWhite').box((.6, .04, .4), loc=(-2.2, 2.4, APRON + .75), bevel=0)
    a.part('Sign_posts', 'Steel').cyl(.03, .8, loc=(-2.2, 2.43, APRON + .4), seg=5, bevel=0)
    a.part('Hazard_marks', 'Hazard').box((.56, .045, .07), loc=(-2.2, 2.38, APRON + .92), bevel=0)
    for i in range(6):
        u = i * TAU / 6
        K.dust(a, (math.cos(u) * 2.4, math.sin(u) * 2.4, APRON), radius=1.0, k=.3)


def _turret_shell(a, t, plan, h, mat='Armor', taper=.86):
    """A welded turret: the plan outline extruded up h with sloped (tapered) sides, its underside left open."""
    k.extrude(a.part('Turret_body', mat, t), plan, h, loc=(0, 0, .08 + h / 2), axis='Z', chamfer=.04, corner=.04,
              taper=(taper, taper), caps=(False, True))


def gun_turret(a):
    """gun_turret: the Leopard-2A4-class turret with the Rh-120 L/44 (see the module docstring)."""
    casemate(a)
    t = a.pivot('Turret', (0, 0, TZ))
    h = .78
    top = .08 + h
    _turret_shell(a, t, [(-.75, -2.0), (.75, -2.0), (1.65, -1.2), (1.65, 1.6), (1.35, 2.4), (-1.35, 2.4), (-1.65, 1.6),
                         (-1.65, -1.2)], h)
    # Team side plates (spaced armour) and the roof plates' weld seams.
    sp = a.part('Turret_skirts', 'Team', t)
    for s in (-1, 1):
        k.extrude(sp, [(-1.0, .1), (1.5, .1), (1.4, .66), (-1.0, .62)], .05, loc=(s * 1.66, 0, 0), axis='X',
                  chamfer=.012)
    K.weld(a.part('Kit_welds', 'Charred', t), [(-.7, -1.8, top + .005), (.7, -1.8, top + .005)])
    K.weld(a.part('Kit_welds', 'Charred', t), [(-1.3, 1.0, top + .005), (1.3, 1.0, top + .005)])
    # The mantlet, the gun, the coaxial MG.
    k.block(a.part('Mantlet', 'Armor', t), (.95, .5, .55), loc=(0, -2.1, .38), chamfer=.05)
    K.gun_barrel(a, 'Main_cannon', t, 0, -2.25, .66, 3.6, .11, seg=10, extractor=(.4, 1.6, .45), brake='collar')
    a.pivot('Muzzle_main', (0, -5.97, .66), t)
    a.part('Coax', 'Steel', t).cyl(.03, 1.05, loc=(.42, -2.36, .47), rot=(R90, 0, 0), seg=6, bevel=0)
    a.pivot('Muzzle_coax', (.42, -2.88, .47), t)
    # Roof: commander's cupola (left rear) with periscopes, the loader's hatch, the gunner's sight block, the
    # panoramic periscope, the wind sensor, the ventilator.
    K.hatch_round(a, (.75, .4, top), r=.36, parent=t, periscopes=4, seg=12)
    K.hatch_rect(a, (-.75, .6, top), (.6, .75), parent=t)
    k.block(a.part('Sight', 'Armor', t), (.4, .55, .38), loc=(-.95, -1.25, top), chamfer=.04)
    a.part('Glass', 'Glass', t).box((.3, .03, .16), loc=(-.95, -1.53, top + .22), bevel=0)
    K.periscope(a, (.85, -.5, top), facing=(0, -1, 0), parent=t, size=(.22, .2, .32))
    a.part('Wind_sensor', 'Steel', t).cyl(.015, .55, loc=(0, 1.9, top + .27), seg=4, bevel=0)
    k.lathe(a.part('Vents', 'Steel', t), [(.14, 0), (.14, .08), (.1, .12), (0, .12)], loc=(0, 1.3, top), seg=8)
    K.smoke_dischargers(a, 1.35, -.9, .65, 1, count=4, parent=t)
    K.smoke_dischargers(a, 1.35, -.9, .65, -1, count=4, parent=t)
    # The bustle stowage basket: an open frame of tubes with a tarp roll and boxes inside, two whips.
    bk = a.part('Racks', 'Steel', t)
    y0, y1 = 2.42, 2.95
    for z in (.3, .75):
        bk.tube([(-1.3, y0, z), (-1.3, y1, z), (1.3, y1, z), (1.3, y0, z)], .02, seg=4, caps=False)
    for x in (-1.3, -.65, 0, .65, 1.3):
        bk.tube([(x, y1, .3), (x, y1, .75)], .018, seg=4)
    bk.box((2.6, .5, .03), loc=(0, (y0 + y1) / 2, .3), bevel=0)
    K.net_roll(a.part('Tarp', 'Canvas', t), a.part('Kit_straps', 'Steel', t), (0, 2.68, .48), length=1.8, r=.16)
    W.stack(a, (-.95, 2.7, .32), n=1, size=(.5, .3, .26), yaw=0, parent=t, seed=8)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (1.1, 2.2, top), h=1.75, r=.022)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (-1.1, 2.2, top), h=1.6, r=.022)
    k.clean(a)


def gun_turret_b(a):
    """gun_turret_b: the unmanned 57 mm gun module with its radar mast (see the module docstring)."""
    casemate(a)
    t = a.pivot('Turret', (0, 0, TZ))
    h = .85
    top = .08 + h
    # A flatter, angular module: the low hull, a raised gun house with a sharply sloped front.
    _turret_shell(a, t, [(-1.0, -1.3), (1.0, -1.3), (1.5, -.7), (1.5, 1.7), (1.2, 2.1), (-1.2, 2.1), (-1.5, 1.7),
                         (-1.5, -.7)], .45, mat='Team', taper=.9)
    k.extrude(a.part('Gun_house', 'Armor', t), [(-.75, -1.6), (.75, -1.6), (.9, -1.0), (.9, 1.0), (-.9, 1.0),
                                                (-.9, -1.0)], .45, loc=(0, 0, .53 + .225), axis='Z', chamfer=.03,
              corner=.03, taper=(.78, .85), caps=(False, True))
    # The twin 57 mm on a cradle: two barrels with perforated brakes (Main_cannon / Main_cannon_2).
    k.block(a.part('Mantlet', 'Armor', t), (.8, .35, .4), loc=(0, -1.62, .42), chamfer=.04)
    for s, nm, br in ((-1, 'Main_cannon', 'Muzzle_brake'), (1, 'Main_cannon_2', 'Muzzle_brake_2')):
        x = s * .17
        k.lathe(a.part(nm, 'Steel', t), [(.075, 0), (.075, .25), (.055, .3), (.05, 2.0), (.045, 2.32), (0, 2.32)],
                loc=(x, -1.75, .58), rot=K.FORWARD, seg=8, worn=(1,))
        k.lathe(a.part(br, 'Undercarriage', t), [(.07, 2.3), (.07, 2.52), (.03, 2.52), (0, 2.52)],
                loc=(x, -1.75, .58), rot=K.FORWARD, seg=8)
        bp = a.part('Brake_ports', 'Charred', t)
        for f in (2.36, 2.44):
            bp.box((.15, .025, .025), loc=(x, -1.75 - f, .58), bevel=0)
    a.pivot('Muzzle_main', (-.17, -4.27, .58), t)
    a.part('Coax', 'Steel', t).cyl(.03, .9, loc=(.42, -2.43, .47), rot=(R90, 0, 0), seg=6, bevel=0)
    a.pivot('Muzzle_coax', (.42, -2.88, .47), t)
    # The ammunition feed housing on the left, its chute; the sight ball on the roof right; a hatch; vents.
    k.block(a.part('Feed_housing', 'Armor', t), (.5, 1.2, .5), loc=(1.15, .1, .53), chamfer=.04)
    a.part('Feed_chute', 'Steel', t).tube([(.9, -.4, .85), (.55, -.9, .95), (.25, -1.2, .8)], .06, seg=6)
    k.lathe(a.part('Sight', 'Armor', t), [(.06, 0), (.06, .18), (0, .18)], loc=(-.6, -.6, top), seg=8)
    a.part('Sight', 'Armor', t).sphere(.2, loc=(-.6, -.6, top + .32), seg=12, rings=8)
    a.part('Glass', 'Glass', t).box((.18, .03, .12), loc=(-.6, -.8, top + .32), bevel=0)
    K.hatch_rect(a, (.3, .5, top - .02), (.55, .6), parent=t)
    K.grille(a, (-1.5, .8, .32), .9, .25, facing=(-1, 0, 0), slats=5, parent=t)
    K.grille(a, (1.5, .8, .32), .9, .25, facing=(1, 0, 0), slats=5, parent=t)
    K.smoke_dischargers(a, 1.2, -.7, .4, 1, count=3, parent=t)
    K.smoke_dischargers(a, 1.2, -.7, .4, -1, count=3, parent=t)
    # The radar mast at the rear: a lattice of three legs, the Radar pivot turning a flat panel; a whip antenna.
    ms = a.part('Mast', 'Steel', t)
    mz = 1.57
    for (x, y) in ((-.25, 1.45), (.25, 1.45), (0, 1.95)):
        ms.tube([(x, y, .5), (x * .3, 1.65 + (y - 1.65) * .3, mz - .1)], .03, seg=4)
    for z in (.85, 1.2):
        f = (z - .5) / (mz - .6)
        pts = [(x * (1 - .7 * f), 1.65 + (y - 1.65) * (1 - .7 * f), z) for (x, y) in ((-.25, 1.45), (.25, 1.45), (0, 1.95))]
        ms.tube(pts + pts[:1], .015, seg=3, caps=False)
    r = a.pivot('Radar', (0, 1.65, mz), t)
    k.block(a.part('Radar_array', 'Armor', r), (1.3, .1, .55), loc=(0, 0, 0), chamfer=.02)
    a.part('Radar_face', 'Undercarriage', r).box((1.2, .02, .45), loc=(0, -.06, .275), bevel=0)
    a.part('Radar_frame', 'Steel', r).box((.06, .06, .3), loc=(0, .08, .05), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (-1.0, 1.8, .53), h=1.9, r=.022)
    k.clean(a)


BUILDERS = {
    'gun_turret': (gun_turret, dict(ao_distance=.7, grime_height=.45, ao_strength=.65)),
    'gun_turret_b': (gun_turret_b, dict(ao_distance=.7, grime_height=.45, ao_strength=.65)),
}
