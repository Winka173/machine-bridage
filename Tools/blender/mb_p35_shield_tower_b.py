"""Prompt 35 wave 10 (lane B): shield_tower_b, the ward branch of the shield tower (shield_tower.ward: it projects
shields onto the towers round it; unit_refs: Shield Battery, StarCraft II), rebuilt from scratch (spec:
Tools/blender/specs/shield_tower_b.json) as an upgrade of the wave 2 base (mb_p35_wave2_shield: the hexagonal cast
plinth with its kerb, joints and hazard ring, the broken ring of jersey barriers with safety stripes, the
prefabricated capacitor cabins with roofs, louvres, doors, vents, Team bands and capacitor caps, the TeamGlow emitter
rings, insulators and clamps). Same plinth, same parts and materials, built here in this script.

The ward crown: instead of the base's tall emitter pylon (9.5 m) the branch keeps the old file's low, wide outline
(8.3 x 8.3 x 4.5 m): a short tapered hexagonal core with conduits and glowing rings, a railed service deck, and three
lattice emitter arms reaching out past the plinth, each carrying a ward projector (a dish of glowing segments in a
steel rim, aimed outwards at the towers it covers) on a swivel, cable runs along the arms, a third capacitor bank,
beacons and a floodlight.

No runtime node (the old file had none; the def is unarmed). Built only from frontier_kit / mb_kit27 primitives,
mb_kit35 and the wave 2 helpers (mb_p35_w2parts); no other model's builder. Metres, +Z up, -Y front, +X left. Under
6,000 triangles.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w2parts as W
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
PAD = .4
DECK = 2.9
ARMS = (R90, R90 + TAU / 3, R90 - TAU / 3)


def _hexagon(r, rot=0.0):
    return [(r * math.cos(rot + i * TAU / 6), r * math.sin(rot + i * TAU / 6)) for i in range(6)]


def _plinth(a):
    k.extrude(a.part('Base', 'Concrete'), _hexagon(3.6), PAD, loc=(0, 0, PAD / 2), axis='Z', corner=.05,
              taper=(.88, .88), caps=(False, True))
    j = a.part('Base_joints', 'Undercarriage')
    for u in range(6):
        t = u * TAU / 6 + TAU / 12
        j.box((3.0, .03, .01), loc=(math.cos(t) * 1.55, math.sin(t) * 1.55, PAD + .003), rot=(0, 0, t), bevel=0)
        t2 = u * TAU / 6
        j.box((1.2, .03, .01), loc=(math.cos(t2) * 2.6, math.sin(t2) * 2.6, PAD + .003), rot=(0, 0, t2 + R90), bevel=0)
    k.ring(a.part('Base_ring', 'Hazard'), [(1.5, PAD), (1.62, PAD), (1.62, PAD + .012), (1.5, PAD + .012)], seg=18)
    bar = a.part('Barriers', 'Concrete')
    for u in (0, 1, 3, 4, 5):
        t = u * TAU / 6 + TAU / 12
        x, y = math.cos(t) * 3.0, math.sin(t) * 3.0
        k.extrude(bar, [(-.3, 0), (.3, 0), (.12, .25), (.08, .8), (-.08, .8), (-.12, .25)], 1.5, loc=(x, y, PAD),
                  rot=(0, 0, t + R90), axis='X', chamfer=0)
        a.part('Barrier_stripes', 'SafetyStripe').box((1.5, .02, .1), loc=(x * 1.07, y * 1.07, PAD + .55),
                                                      rot=(0, 0, t + R90), bevel=0)
    # Three capacitor cabins between the arms (the base has two; the branch adds the third bank).
    for i in range(3):
        t = ARMS[i] + TAU / 6
        cx, cy = math.cos(t) * 1.95, math.sin(t) * 1.95
        yaw = t + R90
        c, s = math.cos(yaw), math.sin(yaw)
        W.slab(a.part('Shelter', 'Plaster'), (1.5, 1.0, 1.4), (cx, cy, PAD), caps=(False, False), rot=(0, 0, yaw))
        k.block(a.part('Roof', 'Armor'), (1.65, 1.15, .12), loc=(cx, cy, PAD + 1.46), rot=(0, 0, yaw), chamfer=.03)
        K.grille(a, (cx + s * .51, cy - c * .51, PAD + .9), .9, .3, facing=(s, -c, 0), slats=4)
        a.part('Doors', 'Armor').box((.6, .03, 1.1), loc=(cx - s * .51 + c * .3, cy + c * .51 + s * .3, PAD + .6),
                                     rot=(0, 0, yaw), bevel=0)
        a.part('Team_band', 'Team').box((1.52, 1.02, .14), loc=(cx, cy, PAD + 1.2), rot=(0, 0, yaw), bevel=0)
        k.lathe(a.part('Vents', 'Steel'), [(.1, 0), (.1, .25), (.18, .27), (0, .34)], loc=(cx, cy, PAD + 1.52), seg=8)
        for d in (-.45, -.15, .15, .45):
            a.part('Capacitor_caps', 'Steel').cyl(.07, .14, loc=(cx + c * d, cy + s * d, PAD + 1.57), seg=6, bevel=0)
        a.part('Cable_trays', 'Steel').box((.25, 1.0, .08), loc=(cx * .62, cy * .62, PAD + .9), rot=(0, 0, t + R90),
                                           bevel=0)


def _crown(a):
    """The short core, the service deck and the three ward-projector arms."""
    k.extrude(a.part('Walls_core', 'Armor'), _hexagon(.85), DECK - PAD + .9, loc=(0, 0, (DECK + PAD + .9) / 2),
              axis='Z', corner=.03, taper=(.7, .7), caps=(False, True))
    con = a.part('Conduits', 'Undercarriage')
    for i in range(6):
        t = i * TAU / 6 + .3
        con.tube([(math.cos(t) * .86, math.sin(t) * .86, PAD), (math.cos(t) * .62, math.sin(t) * .62, DECK + .8)],
                 .035, seg=4)
    glow = a.part('Emitter_rings', 'TeamGlow')
    for z, r in ((1.3, .86), (2.2, .78), (DECK + .7, .64)):
        glow.torus(r, .06, loc=(0, 0, z), seg=14, ring=4)
    k.lathe(a.part('Roof_deck', 'Steel'), [(1.4, -.08), (1.4, .04), (0, .04)], loc=(0, 0, DECK), seg=12)
    a.part('Platform_band', 'Team').cyl(1.42, .1, loc=(0, 0, DECK - .1), seg=12, bevel=0)
    rail = [(math.cos(i * TAU / 12) * 1.35, math.sin(i * TAU / 12) * 1.35, DECK) for i in range(1, 12)]
    K.railing(a.part('Railings', 'Steel'), rail, h=.9, post=.75, r=.018)
    K.ladder(a.part('Ladders', 'Steel'), (1.45, -.2, PAD), (1.45, -.2, DECK + .9), width=.45, step=.35, r=.02)
    k.lathe(a.part('Emitter_collar', 'Armor'), [(.5, 0), (.55, .1), (.55, .3), (.3, .4), (0, .4)],
            loc=(0, 0, DECK + .9), seg=10, worn=(2,))
    a.part('Emitter', 'TeamGlow').sphere(.32, loc=(0, 0, DECK + 1.45), seg=12, rings=6)
    K.whip_antenna(a.part('Antennas', 'Steel'), (.25, .25, DECK + 1.3), h=.2, r=.025)
    for i, t in enumerate(ARMS):
        c, s = math.cos(t), math.sin(t)
        # The lattice arm: two chords and zig-zag web from the core to the projector, a strut down to the plinth.
        arm = a.part('Mast', 'Steel')
        r0, r1 = .7, 3.75
        z0, z1 = DECK + .4, DECK + .75
        for dz in (0, .45):
            arm.tube([(c * r0, s * r0, z0 + dz), (c * r1, s * r1, z1 + dz * .5)], .05, seg=4)
        for j in range(6):
            f0, f1 = j / 6, (j + 1) / 6
            ra, rb = r0 + (r1 - r0) * f0, r0 + (r1 - r0) * f1
            za, zb = z0 + (z1 - z0) * f0, z0 + (z1 - z0) * f1
            arm.tube([(c * ra, s * ra, za + (.45 if j % 2 else 0) * (1 - f0 * .5)),
                      (c * rb, s * rb, zb + (0 if j % 2 else .45) * (1 - f1 * .5))], .02, seg=3)
        a.part('Arm_struts', 'Steel').tube([(c * 3.0, s * 3.0, z1), (c * 2.4, s * 2.4, PAD)], .05, seg=4)
        k.block(a.part('Footings', 'Concrete'), (.4, .4, .2), loc=(c * 2.4, s * 2.4, PAD + .1), chamfer=.03)
        a.part('Kit_cables', 'Undercarriage').tube([(c * r0, s * r0, z0 - .1), (c * r1, s * r1, z1 - .1)], .03, seg=3)
        # The ward projector: swivel, the dish of glowing segments in its rim, aimed outwards.
        px, py, pz = c * 3.95, s * 3.95, z1 + .35
        k.lathe(a.part('Swivels', 'Armor'), [(.22, -.25), (.22, .1), (.16, .18), (0, .2)], loc=(c * 3.75, s * 3.75, z1),
                seg=8)
        n = (c, s, .35)
        k.lathe(a.part('Ward_dishes', 'Armor'), [(0, 0), (.3, .05), (.55, .2), (.62, .3), (.6, .34)],
                loc=(px, py, pz), rot=K.rot_to(n), seg=12, caps=(False, False), worn=(3,))
        m = K.frame((px, py, pz), K.rot_to(n))
        segs = a.part('Ward_segments', 'TeamGlow')
        for q in range(6):
            u = q * TAU / 6
            segs.box((.28, .14, .03), loc=K._at(m, (math.cos(u) * .35, math.sin(u) * .35, .14)),
                     rot=K.rot_to(n), bevel=0)
        a.part('Ward_rims', 'Steel').torus(.61, .035, loc=K._at(m, (0, 0, .32)), rot=K.rot_to(n), seg=12, ring=3)
        a.part('Emitter_tips', 'TeamGlow').sphere(.11, loc=K._at(m, (0, 0, .2)), seg=8, rings=4)
    # Tier 3: insulators and clamps on the conduits, bolts, beacons, lamps, a junction box; the floodlight.
    ins = a.part('Insulators', 'PlasterWhite')
    for i in range(6):
        t = i * TAU / 6 + .3
        for j in (1, 3):
            z = PAD + (DECK + .4 - PAD) * j / 4
            r = .86 - .24 * j / 4 + .05
            for dz in (-.06, 0, .06):
                ins.cyl(.07, .03, loc=(math.cos(t) * r, math.sin(t) * r, z + dz), seg=6, bevel=0)
    bolts = a.part('Kit_bolts', 'Steel')
    for i in range(12):
        t = i * TAU / 12
        bolts.cyl(.035, .04, loc=(math.cos(t) * 1.05, math.sin(t) * 1.05, PAD), seg=4, bevel=0)
    K.beacon(a, (1.0, .9, DECK + .04))
    K.beacon(a, (-1.0, -.9, DECK + .04))
    k.block(a.part('Junction_box', 'Armor'), (.4, .3, .5), loc=(.0, -1.25, PAD + .25), chamfer=.02)
    a.part('Hazard_marks', 'Hazard').box((.6, .02, .1), loc=(0, -1.41, PAD + .4), bevel=0)
    K.floodlight(a, (-3.0, -1.2, PAD), facing=(.8, .2, .3), pole=2.2)


def shield_tower_b(a):
    _plinth(a)
    _crown(a)
    for i in range(6):
        u = i * TAU / 6
        K.dust(a, (math.cos(u) * 3.0, math.sin(u) * 3.0, PAD), radius=1.2, k=.28)
    P.merge_parts(a, {'Arm_struts': 'Mast', 'Cable_trays': 'Mast', 'Swivels': 'Roof'})
    k.clean(a)


BUILDERS = {'shield_tower_b': (shield_tower_b, dict(ao_distance=.8, grime_height=.5, ao_strength=.65))}
