"""Prompt 35 wave 2 (lane A): the shield tower and its dome branch rebuilt from scratch on one plinth (owner decision
4), each from its own spec (Tools/blender/specs/<id>.json). DECISIONS "Prompt 35 wave 2 (lane A)".

The sheet: a tall shield emitter tower with a glowing team-coloured ring (the dome itself is the runtime's effect).
No real reference (unit_refs: Shield Battery, Shield Generator): built as Hegemon field equipment. A hexagonal cast
plinth with a sloped kerb and joints, a broken ring of jersey barriers, two prefabricated capacitor cabins with their
roofs, vents and cable trays, and the pylon: a tapered hexagonal core braced by three lattice legs, an access ladder
with its cage to a railed service platform, conduits up the core, the TeamGlow emitter rings, beacons and a lightning
rod.

- shield_tower: the crown is the emitter head: a glowing sphere held in three claws, a collar of capacitor drums.
- shield_tower_a (the bulwark branch: the dome): the crown is the dome projector: a wide upturned dish of glowing
  segments on three struts, three emitter arms reaching out from the platform, a third capacitor bank on the plinth.

No runtime node (the old files had none). Built only from frontier_kit / mb_kit27 primitives, mb_kit35 and the
wave's lean helpers; no other model's builder. Metres, +Z up, -Y front, +X left. Each under 6,000 triangles.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w2parts as W

R90 = math.pi / 2
TAU = math.tau
PAD = .4
PLAT = 5.2                 # service platform height


def _hexagon(r, rot=0.0):
    return [(r * math.cos(rot + i * TAU / 6), r * math.sin(rot + i * TAU / 6)) for i in range(6)]


def plinth(a, banks=2):
    """The plinth, barriers, capacitor cabins and the pylon with its platform (common to both)."""
    k.extrude(a.part('Base', 'Concrete'), [(x, y) for x, y in _hexagon(3.6, .0)], PAD, loc=(0, 0, PAD / 2), axis='Z',
              corner=.05, taper=(.88, .88), caps=(False, True))
    j = a.part('Base_joints', 'Undercarriage')
    for u in range(6):
        t = u * TAU / 6 + TAU / 12
        j.box((3.0, .03, .01), loc=(math.cos(t) * 1.55, math.sin(t) * 1.55, PAD + .003), rot=(0, 0, t), bevel=0)
    k.ring(a.part('Base_ring', 'Hazard'), [(1.5, PAD), (1.62, PAD), (1.62, PAD + .012), (1.5, PAD + .012)], seg=18)
    # A broken ring of jersey barriers round the plinth.
    bar = a.part('Barriers', 'Concrete')
    for u in (0, 1, 2, 4, 5):
        t = u * TAU / 6 + TAU / 12
        x, y = math.cos(t) * 3.0, math.sin(t) * 3.0
        k.extrude(bar, [(-.3, 0), (.3, 0), (.12, .25), (.08, .8), (-.08, .8), (-.12, .25)], 1.5, loc=(x, y, PAD),
                  rot=(0, 0, t + R90), axis='X', chamfer=0)
        a.part('Barrier_stripes', 'SafetyStripe').box((1.5, .02, .1), loc=(x * 1.07, y * 1.07, PAD + .55),
                                                      rot=(0, 0, t + R90), bevel=0)
    # The capacitor cabins (prefabricated boxes with roofs, vents, doors, cable trays to the pylon).
    for i in range(banks):
        t = (-.65, .65, math.pi)[i] + math.pi / 2
        cx, cy = math.cos(t) * 1.95, math.sin(t) * 1.95
        yaw = t + R90
        W.slab(a.part('Shelter', 'Plaster'), (1.5, 1.0, 1.4), (cx, cy, PAD), caps=(False, False), rot=(0, 0, yaw))
        k.block(a.part('Roof', 'Armor'), (1.65, 1.15, .12), loc=(cx, cy, PAD + 1.46), rot=(0, 0, yaw), chamfer=.03)
        c, s = math.cos(yaw), math.sin(yaw)
        K.grille(a, (cx + s * .51, cy - c * .51, PAD + .9), .9, .3, facing=(s, -c, 0), slats=4)
        a.part('Doors', 'Armor').box((.6, .03, 1.1), loc=(cx - s * .51 + c * .3, cy + c * .51 + s * .3, PAD + .6),
                                     rot=(0, 0, yaw), bevel=0)
        a.part('Team_band', 'Team').box((1.52, 1.02, .14), loc=(cx, cy, PAD + 1.2), rot=(0, 0, yaw), bevel=0)
        k.lathe(a.part('Vents', 'Steel'), [(.1, 0), (.1, .25), (.18, .27), (0, .34)], loc=(cx, cy, PAD + 1.52), seg=8)
        a.part('Cable_trays', 'Steel').box((.25, 1.2, .08), loc=(cx * .6, cy * .6, PAD + .9), rot=(0, 0, t + R90 * 0),
                                           bevel=0)
    # The pylon: the tapered hexagonal core, three lattice legs with bracing, conduits, the emitter rings.
    k.extrude(a.part('Walls_core', 'Armor'), _hexagon(.75), PLAT + 2.0 - PAD, loc=(0, 0, (PLAT + 2.0 + PAD) / 2),
              axis='Z', corner=.03, taper=(.62, .62), caps=(False, True))
    legs = a.part('Mast', 'Steel')
    for i in range(3):
        t = i * TAU / 3 + R90
        b = (math.cos(t) * 1.35, math.sin(t) * 1.35)
        top = (math.cos(t) * .55, math.sin(t) * .55)
        legs.tube([(b[0], b[1], PAD), (top[0], top[1], PLAT + 1.6)], .06, seg=5)
        k.block(a.part('Footings', 'Concrete'), (.4, .4, .2), loc=(b[0], b[1], PAD + .1), chamfer=.03)
        for z0, z1 in ((PAD + .3, 2.4), (2.4, 4.2)):
            f0, f1 = (z0 - PAD) / (PLAT + 1.2), (z1 - PAD) / (PLAT + 1.2)
            p0 = (b[0] + (top[0] - b[0]) * f0, b[1] + (top[1] - b[1]) * f0)
            p1 = (b[0] + (top[0] - b[0]) * f1, b[1] + (top[1] - b[1]) * f1)
            legs.tube([(p0[0], p0[1], z0), (p1[0] * .55, p1[1] * .55, z1)], .03, seg=4)
    for z in (2.4, 4.2):
        f = (z - PAD) / (PLAT + 1.2)
        rr = 1.35 + (.55 - 1.35) * f
        pts = [(math.cos(i * TAU / 3 + R90) * rr, math.sin(i * TAU / 3 + R90) * rr, z) for i in range(4)]
        legs.tube(pts, .03, seg=4, caps=False)
    con = a.part('Conduits', 'Undercarriage')
    for i in range(3):
        t = i * TAU / 3 + .5
        con.tube([(math.cos(t) * .78, math.sin(t) * .78, PAD), (math.cos(t) * .5, math.sin(t) * .5, PLAT + 1.6)], .04,
                 seg=4)
    glow = a.part('Emitter_rings', 'TeamGlow')
    for z, r in ((1.6, .82), (3.2, .72), (6.6, .55)):
        glow.torus(r, .06, loc=(0, 0, z), seg=14, ring=4)
    # The service platform with its railing, the ladder with its cage up the core.
    k.lathe(a.part('Roof_deck', 'Steel'), [(1.5, -.08), (1.5, .04), (0, .04)], loc=(0, 0, PLAT), seg=12)
    a.part('Platform_band', 'Team').cyl(1.52, .1, loc=(0, 0, PLAT - .1), seg=12, bevel=0)
    rail = [(math.cos(i * TAU / 12) * 1.45, math.sin(i * TAU / 12) * 1.45, PLAT) for i in range(1, 12)]
    K.railing(a.part('Railings', 'Steel'), rail, h=.95, post=.75, r=.018)
    K.ladder(a.part('Ladders', 'Steel'), (1.5, 0, PAD), (1.5, 0, PLAT + .9), width=.45, step=.35, r=.02)
    cage = a.part('Ladder_cage', 'Steel')
    for z in (2.6, 3.6, 4.6):
        cage.tube([(1.5, -.25, z), (1.85, -.25, z), (1.85, .25, z), (1.5, .25, z)], .014, seg=3, caps=False)
    cage.tube([(1.85, 0, 2.6), (1.85, 0, PLAT)], .014, seg=3, caps=False)
    K.beacon(a, (1.1, 1.0, PLAT + .04))
    # Tier 3: insulator stacks and clamps on the conduits, anchor bolts at the footings and round the core, the
    # platform's marker lamps, capacitor caps on the cabin roofs.
    ins = a.part('Insulators', 'PlasterWhite')
    clamp = a.part('Kit_clamps', 'Steel')
    for i in range(3):
        t = i * TAU / 3 + .5
        for j in range(6):
            f = (j + .5) / 6
            r = .78 + (.5 - .78) * f
            z = PAD + (PLAT + 1.2) * f
            if j % 2:
                for dz in (-.06, 0, .06):
                    ins.cyl(.07, .03, loc=(math.cos(t) * (r + .05), math.sin(t) * (r + .05), z + dz), seg=6, bevel=0)
            else:
                clamp.box((.12, .1, .05), loc=(math.cos(t) * r, math.sin(t) * r, z), rot=(0, 0, t), bevel=0)
    bolts = a.part('Kit_bolts', 'Steel')
    for i in range(3):
        t = i * TAU / 3 + R90
        W.bolt_grid(bolts, (math.cos(t) * 1.35, math.sin(t) * 1.35, PAD + .2), 2, 2, .26, r=.03, h=.04, seg=4)
    for i in range(12):
        t = i * TAU / 12
        bolts.cyl(.035, .04, loc=(math.cos(t) * .95, math.sin(t) * .95, PAD), seg=4, bevel=0)
    for i in range(6):
        t = i * TAU / 6 + .26
        a.part('Lamps', 'Lamp').box((.08, .08, .08), loc=(math.cos(t) * 1.45, math.sin(t) * 1.45, PLAT + 1.0),
                                    bevel=0)
    for i in range(banks):
        t = (-.65, .65, math.pi)[i] + math.pi / 2
        cx, cy = math.cos(t) * 1.95, math.sin(t) * 1.95
        for d in (-.45, -.15, .15, .45):
            a.part('Capacitor_caps', 'Steel').cyl(.07, .14, loc=(cx + math.cos(t + R90) * d,
                                                                 cy + math.sin(t + R90) * d, PAD + 1.57), seg=6,
                                                  bevel=0)
        K.rivet_line(a.part('Kit_rivets', 'Steel'), (cx + math.cos(t + R90) * .7 + math.cos(t) * .51,
                                                     cy + math.sin(t + R90) * .7 + math.sin(t) * .51, PAD + 1.3),
                     (cx - math.cos(t + R90) * .7 + math.cos(t) * .51, cy - math.sin(t + R90) * .7 + math.sin(t) * .51,
                      PAD + 1.3), (math.cos(t), math.sin(t), 0), pitch=.2, r=.016)
    for u in range(6):
        t = u * TAU / 6
        a.part('Base_joints', 'Undercarriage').box((1.2, .03, .01), loc=(math.cos(t) * 2.6, math.sin(t) * 2.6, PAD + .003), rot=(0, 0, t + R90), bevel=0)
    K.floodlight(a, (-3.1, -1.0, PAD), facing=(.8, .2, .3), pole=2.4)
    k.block(a.part('Junction_box', 'Armor'), (.4, .3, .5), loc=(.0, -1.2, PAD + .25), chamfer=.02)
    a.part('Hazard_marks', 'Hazard').box((.6, .02, .1), loc=(0, -1.36, PAD + .4), bevel=0)
    for i in range(6):
        u = i * TAU / 6
        K.dust(a, (math.cos(u) * 3.0, math.sin(u) * 3.0, PAD), radius=1.2, k=.28)


def shield_tower(a):
    """shield_tower: the emitter head on top of the core (see the module docstring)."""
    plinth(a)
    zc = PLAT + 2.0
    k.lathe(a.part('Emitter_collar', 'Armor'), [(.55, 0), (.6, .1), (.6, .35), (.4, .45), (0, .45)], loc=(0, 0, zc),
            seg=12, worn=(2,))
    for i in range(6):
        t = i * TAU / 6
        a.part('Capacitors', 'Steel').cyl(.12, .45, loc=(math.cos(t) * .62, math.sin(t) * .62, zc - .1), seg=8,
                                          bevel=0)
    a.part('Emitter', 'TeamGlow').sphere(.5, loc=(0, 0, zc + .95), seg=14, rings=8)
    claws = a.part('Emitter_claws', 'Armor')
    for i in range(3):
        t = i * TAU / 3
        c, s = math.cos(t), math.sin(t)
        claws.tube([(c * .5, s * .5, zc + .4), (c * .72, s * .72, zc + .9), (c * .45, s * .45, zc + 1.45)], .07, seg=5)
    K.whip_antenna(a.part('Antennas', 'Steel'), (0, 0, zc + 1.45), h=.75, r=.03)
    k.clean(a)


def shield_tower_a(a):
    """shield_tower_a: the dome projector dish and emitter arms (see the module docstring)."""
    plinth(a, banks=3)
    zc = PLAT + 2.0
    k.lathe(a.part('Emitter_collar', 'Armor'), [(.55, 0), (.6, .1), (.6, .3), (0, .3)], loc=(0, 0, zc), seg=12)
    st = a.part('Dish_struts', 'Steel')
    for i in range(3):
        t = i * TAU / 3
        st.tube([(math.cos(t) * .4, math.sin(t) * .4, zc + .3), (math.cos(t) * 1.4, math.sin(t) * 1.4, zc + 1.0)],
                .05, seg=4)
    # The dish: an upturned bowl of eight glowing segments in a steel rim.
    k.lathe(a.part('Dome_dish', 'Armor'), [(0, zc + .55), (.6, zc + .62), (1.3, zc + .9), (1.75, zc + 1.25),
                                           (1.8, zc + 1.35)], seg=16, caps=(False, False), worn=(3,))
    seg_part = a.part('Dome_segments', 'TeamGlow')
    for i in range(8):
        t = i * TAU / 8
        seg_part.box((.5, .22, .03), loc=(math.cos(t) * 1.05, math.sin(t) * 1.05, zc + .8), rot=(0, -.5, t), bevel=0)
    a.part('Dome_rim', 'Steel').torus(1.8, .05, loc=(0, 0, zc + 1.35), seg=16, ring=4)
    a.part('Emitter', 'TeamGlow').sphere(.28, loc=(0, 0, zc + .75), seg=10, rings=6)
    # Three emitter arms from the platform: an arm, its glowing tip.
    for i in range(3):
        t = i * TAU / 3 + R90 / 3
        c, s = math.cos(t), math.sin(t)
        a.part('Emitter_arms', 'Armor').tube([(c * .6, s * .6, PLAT + .6), (c * 2.2, s * 2.2, PLAT + 1.4)], .07,
                                             seg=5)
        a.part('Emitter_tips', 'TeamGlow').sphere(.16, loc=(c * 2.25, s * 2.25, PLAT + 1.45), seg=8, rings=5)
    K.whip_antenna(a.part('Antennas', 'Steel'), (.3, .3, zc + .3), h=1.0, r=.025)
    k.clean(a)


BUILDERS = {
    'shield_tower': (shield_tower, dict(ao_distance=.8, grime_height=.5, ao_strength=.65)),
    'shield_tower_a': (shield_tower_a, dict(ao_distance=.8, grime_height=.5, ao_strength=.65)),
}
