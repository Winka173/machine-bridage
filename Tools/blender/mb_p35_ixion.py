"""Prompt 35 pilot 1: Ixion rebuilt from scratch (spec: Tools/blender/specs/ixion.json; DECISIONS "Prompt 35").

Ixion is Thorne's armoured BelAZ-75710 mine truck (Hung's mini boss): the giant dump truck read first (six mining
tyres, the front upper deck with the cab offset left and the diagonal stair across the radiator, the dump body with
its canopy over the cab), then the war fit (a V ram, bolted appliqué on the body, a welded T-72-class 125 mm turret
on the armoured roof, two 12.7 mm guns over the cab, the mine dispenser under the tail). 26 x 12 x 10 m, the def's
modelSize (x1.26 of the real truck's length).

Gameplay nodes (balance.json `ixion.parts` and `mountWeapons`, unchanged): `Part_wheel` / `Part_wheel.001` (front
tyres, left / right), `Part_tyre` .. `.003` (rear tyres l1, r1, l2, r2), `Turret` (part gun: Main_cannon,
Muzzle_brake, Muzzle_main), `Part_cab` (the cab, carrying Mount_mg / Mount_mg.001 with Muzzle_mg / .001),
`Point_mines` (the dispenser mouth), `Point_exhaust`, `Point_fire`. Weak points the player must see (the card's "how
to fight"): the four rear tyres (armour 1) stand bare behind the body with hazard-yellow rims; the front tyres stand
outside the ram's ends.

Built only from frontier_kit / mb_kit27 primitives and the mb_kit35 library; no other model's builder or mesh.
Conventions: metres, +Z up, Blender -Y is the front, +X the truck's left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau

TYRE_R, TYRE_W, TYRE_X = 2.45, 1.9, 5.0
TYRES = (('Part_wheel', 1, -8.5), ('Part_wheel__001', -1, -8.5),      # front left, front right
         ('Part_tyre', 1, 3.0), ('Part_tyre__001', -1, 3.0),           # rear l1, r1
         ('Part_tyre__002', 1, 9.0), ('Part_tyre__003', -1, 9.0))      # rear l2, r2
DECK = 5.7            # top of the front upper deck
FLOOR = 5.05          # the dump body's floor (above the rear tyres' tops at 4.9)
ROOF = 8.45           # the armoured roof over the body and the canopy
BODY_Y = (-6.3, 12.6)  # body front wall .. tail
TURRET = (0.0, 1.5, ROOF + .28)
CAB = (3.75, -9.55, DECK)


def _tyre(a, node, s, y):
    """One mining tyre on its part node: the casing with chevron lugs, the rim (rear: hazard yellow, the weak point),
    nuts, hub cap, a valve stem; mud round it (COLOR_0)."""
    p = a.pivot(node, (s * TYRE_X, y, TYRE_R))
    rear = y > 0
    K.truck_wheel(a, (0, 0, 0), TYRE_R, TYRE_W, s, lugs=20, seg=20, rim_mat='Hazard' if rear else 'Steel', parent=p,
                  lug_depth=.16, nuts=8)
    K.dust(a, (s * TYRE_X, y, .6), radius=3.2, k=.22)


def _running_gear(a):
    frame = a.part('Chassis', 'Undercarriage')
    steel = a.part('Chassis_steel', 'Steel')
    for node, s, y in TYRES:
        _tyre(a, node, s, y)
    # Two frame rails, cross members, the rear axles with their differentials and final-drive hubs.
    with k.mirrored(frame):
        K.chamfer_box(frame, (.75, 24.0, 1.1), loc=(1.7, -.2, 2.9), c=.06)
    for y in (-11.7, -6.0, -1.0, 6.0, 11.6):
        K.chamfer_box(frame, (2.7, .55, .7), loc=(0, y, 2.9), c=.04)
    for y in (3.0, 9.0):
        K.axle(frame, y, TYRE_R, TYRE_X - .7, r=.42)
        with k.mirrored(steel):
            k.lathe(steel, [(.75, 0), (.8, .1), (.8, .45), (.6, .55)], loc=(TYRE_X - 1.3, y, TYRE_R), rot=(0, R90, 0),
                    seg=12, worn=(2,))
    # Front: hydro-pneumatic suspension struts from the frame to each front hub, the steering tie rod.
    for s in (-1, 1):
        k.lathe(steel, [(.32, 0), (.32, 1.7), (.26, 1.78), (.26, 2.9), (.36, 3.0), (.36, 3.25)],
                loc=(s * 3.05, -8.5, 1.9), seg=12, worn=(1, 4))
        frame.limb((s * 3.1, -8.5, 2.2), (s * (TYRE_X - .9), -8.5, TYRE_R), .45, .5, bevel=0)
    steel.tube([(-3.0, -9.3, 2.0), (3.0, -9.3, 2.0)], .09, seg=8)
    # Rear: the oscillating suspension cylinders over the rear axles.
    for s in (-1, 1):
        for y in (3.0, 9.0):
            k.lathe(steel, [(.28, 0), (.28, 1.0), (.22, 1.05), (.22, 1.7)], loc=(s * 2.6, y - .9, TYRE_R + .45),
                    seg=10, worn=(1,))
    # Mud flaps behind the rear tyres (rubber hung from the body floor).
    flap = a.part('Mud_flaps', 'Rubber')
    for s in (-1, 1):
        flap.box((TYRE_W + .2, .06, 1.6), loc=(s * TYRE_X, 11.8, FLOOR - .9), bevel=0)


def _front(a):
    yel = a.part('Hood', 'Hazard')
    arm = a.part('Front_armour', 'Armor')
    steel = a.part('Front_steel', 'Steel')
    # The engine hood between the front tyres, its radiator grille behind a bar guard.
    K.chamfer_box(yel, (5.2, 6.3, 3.0), loc=(0, -9.15, 4.1), c=.12)
    k.inset(yel, lambda c, n, f: abs(n.x) > .9 and abs(c.x) > 2.5, width=.18, depth=-.04)
    K.grille(a, (0, -12.32, 4.05), 4.2, 2.3, facing=(0, -1, 0), slats=9, frame_mat='Armor')
    guard = a.part('Grille_guard', 'Armor')
    for x in (-1.95, -1.0, 0.0, 1.0, 1.95):
        K.chamfer_box(guard, (.22, .24, 2.7), loc=(x, -12.62, 4.05), c=.04)
    for z in (2.85, 5.25):
        K.chamfer_box(guard, (4.6, .26, .22), loc=(0, -12.62, z), c=.04)
    # The upper deck across the whole width: a chequer plate on beams, its toe board and railings.
    deck = a.part('Deck', 'Hazard')
    K.chamfer_box(deck, (12.0, 6.9, .32), loc=(0, -9.15, DECK - .16), c=.06)
    k.inset(deck, lambda c, n, f: n.z > .9 and c.z > DECK - .05, width=.22, depth=-.025)
    for x in (-5.4, -2.6, 2.6, 5.4):
        K.chamfer_box(arm, (.3, 6.6, .45), loc=(x, -9.15, DECK - .55), c=.04)                  # deck beams
    rails = a.part('Railings', 'Steel')
    K.railing(rails, [(-5.9, -5.9, DECK), (-5.9, -12.5, DECK), (.3, -12.5, DECK)], h=1.05, post=1.3, r=.045)
    K.railing(rails, [(5.9, -12.5, DECK), (5.9, -7.2, DECK)], h=1.05, post=1.3, r=.045)
    # The BelAZ's diagonal stair across the radiator: stringers, treads and a handrail, from the ram's right end up
    # to the deck's front edge.
    stair = a.part('Stair', 'Steel')
    p0, p1 = Vector((-4.9, -12.95, 1.25)), Vector((.9, -12.95, DECK))
    d = p1 - p0
    for off in (-.32, .32):
        stair.tube([tuple(p0 + Vector((0, off, 0))), tuple(p1 + Vector((0, off, 0)))], .07, seg=6)
    for i in range(9):
        c = p0 + d * ((i + .5) / 9)
        stair.box((.5, .7, .07), loc=tuple(c), bevel=0)
    stair.tube([tuple(p0 + Vector((0, -.38, 1.0))), tuple(p1 + Vector((0, -.38, 1.0)))], .04, seg=6)
    for f in (.05, .5, .95):
        c = p0 + d * f
        stair.tube([tuple(c + Vector((0, -.38, 0))), tuple(c + Vector((0, -.38, 1.0)))], .035, seg=4)
    # Right of the deck: two air cleaners, an equipment box, the exhaust stacks (the engine's), lamps along the edge.
    for y in (-7.4, -9.0):
        k.lathe(steel, [(.6, 0), (.6, 1.3), (.5, 1.42), (.16, 1.46), (.16, 1.62), (0, 1.62)], loc=(-4.85, y, DECK),
                seg=14, worn=(1, 2))
        steel.tube([(-4.3, y, DECK + .8), (-3.4, y + .4, DECK + .8), (-3.0, y + .4, DECK - .3)], .14, seg=8)
    K.chamfer_box(arm, (2.8, 2.6, 1.3), loc=(-3.9, -11.4, DECK + .65), c=.08)
    K.hatch_rect(a, (-3.9, -12.72, DECK + .65), (1.4, .8), normal=(0, -1, 0), mat='Armor')
    for x in (-2.0, -2.8):
        K.exhaust(a, (x, -7.0, DECK), r=.2, length=1.8, muffler=True)
    a.pivot('Point_exhaust', (-2.4, -7.0, DECK + 2.0))
    a.pivot('Point_fire', (0, -9.2, DECK + .2))
    for x in (-4.9, -3.9, 3.9, 4.9):
        K.lamp(a, (x, -12.7, DECK - .5), (0, -1, 0), r=.2, mat='Armor')
    for s in (-1, 1):
        K.tow_hook(steel, (s * 1.4, -12.3, 1.8), facing=(0, -1, 0), size=.3)


def _ram(a):
    """The V ram, 0.4 .. 3.4 m up, nose 13 m ahead of the centre: a chamfered plough with vertical ribs behind it, a
    steel cutting edge, push arms to the frame, hazard chevrons along its top."""
    ram = a.part('Ram', 'Armor')
    steel = a.part('Ram_steel', 'Steel')
    prof = [(0, -13.0), (5.6, -11.5), (5.6, -11.05), (0, -12.55), (-5.6, -11.05), (-5.6, -11.5)]
    k.extrude(ram, prof, 3.0, loc=(0, 0, 1.9), axis='Z', chamfer=.1, corner=.07)
    k.sweep(steel, [(-.1, -.14), (.1, -.14), (.1, .14), (-.1, .14)], [(-5.5, -11.55, .48), (0, -13.03, .48),
                                                                    (5.5, -11.55, .48)])
    for s in (-1, 1):
        for f in (.2, .45, .7, .92):
            x = s * 5.4 * f
            y = -12.55 + 1.5 * f
            K.chamfer_box(ram, (.18, .5, 2.6), loc=(x, y + .35, 1.9), rot=(0, 0, s * .26), c=.04)
        ram.limb((s * 1.5, -12.0, 2.0), (s * 1.75, -10.9, 2.7), .5, .5, bevel=0)
        ram.limb((s * 4.3, -11.3, 2.3), (s * 2.0, -10.6, 2.8), .38, .38, bevel=0)
        steel.cyl(.18, .8, loc=(s * 2.9, -11.0, 2.6), rot=(R90, 0, s * .4), seg=10, bevel=0)      # push rams
    stripe = a.part('Ram_stripes', 'SafetyStripe')
    for s in (-1, 1):
        for i in range(6):
            t = (i + .5) / 6
            stripe.box((.55, .2, .05), loc=(s * 5.4 * t, -12.92 + 1.45 * t + .22, 3.42), rot=(0, 0, s * .27), bevel=0)
    K.rivet_line(a.part('Kit_rivets', 'Steel'), (-5.4, -11.45, 3.1), (0, -12.98, 3.1), (0, -1, 0), pitch=.7, r=.07,
                 h=.07, seg=4)
    K.rivet_line(a.part('Kit_rivets', 'Steel'), (0, -12.98, 3.1), (5.4, -11.45, 3.1), (0, -1, 0), pitch=.7, r=.07,
                 h=.07, seg=4)


def _cab(a):
    """The cab on the deck's left (Part_cab): a sloped-front cab with glass behind armoured louvres, a door, mirrors,
    a grab rail, a riveted shade one tone off the deck; the two roof MGs stand on the canopy above it."""
    pc = a.pivot('Part_cab', CAB)
    cab = a.part('Cab', 'Hazard', pc)
    w, dpt, h = 4.0, 4.3, 2.35
    k.extrude(cab, [(-dpt / 2, 0), (dpt / 2, 0), (dpt / 2, h), (-dpt / 2 + .55, h), (-dpt / 2, h - .9)], w,
              axis='X', chamfer=.08, corner=.06)
    K.windscreen(a, [(-1.75, -2.17, 1.47), (1.75, -2.17, 1.47), (1.75, -1.67, 2.27), (-1.75, -1.67, 2.27)],
                 frame_mat='Armor', parent=pc, wipers=2, bar=.07)
    glass = a.part('Glass', 'Glass', pc)
    glass.box((.04, 1.6, .8), loc=(w / 2 + .01, -.8, 1.6), bevel=0)
    glass.box((.04, 2.4, .8), loc=(-w / 2 - .01, -.2, 1.6), bevel=0)
    arm = a.part('Cab_armour', 'Armor', pc)
    for z in (1.62, 1.88, 2.14):
        arm.box((3.7, .14, .1), loc=(0, -2.17 + (z - 1.47) * .62 - .08, z), rot=(-.56, 0, 0), bevel=0)
        arm.box((.14, 1.8, .1), loc=(w / 2 + .07, -.8, z - .1), bevel=0)
    K.panel(a, arm, (2.4, .9), (-w / 2 - .02, -.2, .65), (-1, 0, 0), t=.08, rivet=.4, parent=pc, r=.05, seg=4)
    K.door(a, (w / 2 + .01, 1.0, .1), (1.1, 2.0), normal=(1, 0, 0), parent=pc, mat='Hazard')
    st = a.part('Cab_steel', 'Steel', pc)
    K.mirror(st, (w / 2, -1.9, 1.9), 1, arm=.6, size=(.3, .06, .5))
    K.handle(st, (-w / 2 - .02, -.4, .4), (-w / 2 - .02, -.4, 1.6), (-1, 0, 0), h=.1, r=.025)
    K.whip_antenna(a.part('Antennas', 'Steel', pc), (1.4, 1.6, h), h=.6, r=.06)
    for i, x in enumerate((-.9, 1.1)):
        k.lathe(arm, [(.5, 0), (.5, .14), (.36, .2)], loc=(x, -.6, ROOF - DECK + .02), seg=12, worn=(1,))
        # Wave 1 (the owner's roof-gun rule): each gun on a 0.9 m pintle post with its cradle and big ammunition can,
        # so the pair stands clear of the canopy at the battle camera's distance.
        K.pintle_mg(a, 'Part_cab', (x, -.6, ROOF - DECK + .2), index=i, scale=2.0, slot='mg', post=.9)
    K.tone(a, 'Part_cab', k=.93, warm=.03)


def _body(a):
    """The armoured dump body: a side profile with the tail rising, the canopy over the cab, ribs and appliqué
    plates bolted between them, the roof with its insets, hatches and vents, the general's stripe, the V keel, the
    fuel and hydraulic tanks and the hoist rams under it."""
    team = a.part('Body', 'Team')
    arm = a.part('Body_armour', 'Armor')
    steel = a.part('Body_steel', 'Steel')
    rivets = a.part('Kit_rivets', 'Steel')
    y0, y1 = BODY_Y
    prof = [(y0, FLOOR), (11.0, FLOOR), (y1, 6.6), (y1, 9.05), (y1 - .9, 9.05), (y1 - 1.6, ROOF), (y0 - .2, ROOF),
            (y0 - .2, ROOF - .9)]
    k.extrude(team, prof, 11.7, axis='X', chamfer=.14, corner=.1)
    k.inset(team, lambda c, n, f: n.z > .9 and c.z > ROOF - .05, width=.4, depth=-.04)
    # Canopy over the cab and the deck, with its beams under it and two posts (the war fit).
    canopy = a.part('Canopy', 'Team')
    K.chamfer_box(canopy, (11.9, 6.8, .38), loc=(0, -9.55, ROOF - .19), c=.08)
    for x in (-4.6, -1.6, 1.6, 4.6):
        K.chamfer_box(arm, (.32, 6.6, .55), loc=(x, -9.4, ROOF - .62), c=.04)
    for s in (-1, 1):
        K.chamfer_box(arm, (.38, .38, ROOF - DECK - .4), loc=(s * 5.7, -12.6, (ROOF + DECK) / 2 - .2), c=.05)
    a.part('Canopy_band', 'SafetyStripe').box((11.9, .08, .3), loc=(0, -12.97, ROOF - .2), bevel=0)
    # Ribs (the BelAZ body's vertical stiffeners), the top rails with the general's stripe, appliqué between ribs.
    ribs = [-5.4, -1.6, 2.2, 6.0, 9.6]
    for s in (-1, 1):
        x = s * 5.85
        for y in ribs:
            K.chamfer_box(team, (.3, .45, ROOF - FLOOR - .1), loc=(x + s * .1, y, (ROOF + FLOOR) / 2), c=.05)
        K.chamfer_box(team, (.45, y1 - y0 + .2, .34), loc=(x + s * .12, (y0 + y1) / 2 - .4, ROOF + .02), c=.06)
        a.part('Team_band', 'Team').box((.06, y1 - y0 - 1.0, .32), loc=(x + s * .37, (y0 + y1) / 2 - .5, ROOF - .5),
                                        bevel=0)
        for ya, yb in zip(ribs, ribs[1:]):
            K.panel(a, arm, (yb - ya - .55, 2.2), (x + s * .02, (ya + yb) / 2, 6.6), (s, 0, 0), t=.12, rivet=.85,
                    r=.07, seg=4)
        K.rivet_line(rivets, (x + s * .06, y0 + .2, FLOOR + .25), (x + s * .06, 11.0, FLOOR + .25), (s, 0, 0),
                     pitch=1.0, r=.07, h=.07, seg=4)
    # The V keel under the body between the rear tyres and the body's subframe.
    k.extrude(a.part('Body_keel', 'Undercarriage'), [(-3.2, FLOOR + .02), (3.2, FLOOR + .02), (2.2, FLOOR - 1.0),
                                                     (-2.2, FLOOR - 1.0)], 17.0, loc=(0, 3.0, 0), axis='Y',
              chamfer=.08)
    # Roof fittings: hatches, vents, a ladder up the tail, the welded adapter under the turret.
    K.hatch_rect(a, (3.6, 8.6, ROOF), (1.3, 1.3), mat='Armor')
    K.hatch_rect(a, (-3.6, 9.6, ROOF), (1.3, 1.3), mat='Armor')
    K.grille(a, (-3.6, -2.9, ROOF + .02), 2.2, 1.4, facing=(0, 0, 1), slats=6)
    K.grille(a, (3.6, -2.9, ROOF + .02), 2.2, 1.4, facing=(0, 0, 1), slats=6)
    k.extrude(arm, k.round_corners([(-3.7, -3.7), (3.7, -3.7), (3.7, 3.7), (-3.7, 3.7)], 1.2, steps=2), .3,
              loc=(TURRET[0], TURRET[1], ROOF + .13), axis='Z', chamfer=.08)
    K.weld(a.part('Kit_welds', 'Charred'), [(x, TURRET[1] + y, ROOF + .02) for x, y in
                                            ((-3.55, -3.55), (3.55, -3.55), (3.55, 3.55), (-3.55, 3.55), (-3.55, -3.55))],
           r=.06)
    K.ladder(a.part('Ladders', 'Steel'), (-4.2, y1 + .25, FLOOR - 1.6), (-4.2, y1 + .25, 9.0), width=.6, step=.38,
             r=.04)
    # The mine hopper on the rear roof (the mines' magazine), its feed trunk down the tail to the dispenser; roof
    # stowage ahead of the turret: ammunition bins and a rolled net.
    hop = a.part('Mine_hopper', 'Armor')
    k.extrude(hop, [(-2.6, 0), (2.6, 0), (2.2, 1.6), (-2.2, 1.6)], 3.0, loc=(0, 9.6, ROOF), axis='Y', chamfer=.1,
              corner=.08, taper=(1, 1))
    k.extrude(hop, [(-2.2, 1.6), (2.2, 1.6), (2.0, 1.9), (-2.0, 1.9)], 2.8, loc=(0, 9.6, ROOF), axis='Y', chamfer=.06)
    K.panel(a, hop, (4.0, 1.0), (0, 8.08, ROOF + .8), (0, -1, 0), t=.06, rivet=.6, r=.05, seg=4)
    a.part('Hopper_hazard', 'SafetyStripe').box((4.4, .05, .22), loc=(0, 8.07, ROOF + 1.45), bevel=0)
    K.chamfer_box(hop, (1.2, 1.2, 4.6), loc=(0, y1 + .45, ROOF - 1.6), c=.08)
    for x in (-3.6, 3.6):
        K.crate(a.part('Stowage', 'Crate'), a.part('Kit_straps', 'Steel'), (1.6, 1.0, .7), (x, -4.6, ROOF))
    K.net_roll(a.part('Tarp', 'Canvas'), a.part('Kit_straps', 'Undercarriage'), (0, -5.4, ROOF + .3), length=5.0,
               r=.3)
    # Under the body: the fuel tank (right) and hydraulic tank (left), the hoist rams, steps.
    K.chamfer_box(arm, (1.2, 3.2, 1.6), loc=(-4.6, -3.6, 3.3), c=.12)
    k.lathe(steel, [(.2, 0), (.2, .25), (0, .3)], loc=(-4.6, -3.6, 4.1), seg=8)
    K.chamfer_box(arm, (1.1, 2.6, 1.4), loc=(4.6, -3.6, 3.3), c=.12)
    for s in (-1, 1):
        k.lathe(steel, [(.36, 0), (.36, 1.8), (.28, 1.86), (.28, 2.6)], loc=(s * 2.4, -5.6, 2.9),
                rot=(-.25, 0, 0), seg=12, worn=(1,))
        for y in (-4.2, -2.9):
            steel.box((.7, .3, .06), loc=(s * 5.4, y, 2.2 + (y + 4.2) * .6), bevel=0)
    # The tail: the mine dispenser box and chute, tail lamps, the tow pintle.
    disp = a.part('Mine_dispenser', 'Armor')
    K.chamfer_box(disp, (3.4, 1.7, 1.7), loc=(0, 11.9, 3.4), c=.1)
    k.extrude(disp, [(-.9, 0), (.9, 0), (.7, -1.3), (-.7, -1.3)], .9, loc=(0, 12.5, 2.6), axis='Y', chamfer=.04)
    K.panel(a, disp, (2.6, 1.2), (0, 12.76, 3.5), (0, 1, 0), t=.06, rivet=.5, r=.05, seg=4)
    a.part('Mine_hazard', 'SafetyStripe').box((3.4, .05, .25), loc=(0, 12.77, 4.15), bevel=0)
    a.pivot('Point_mines', (0, 12.95, 1.3))
    for s in (-1, 1):
        K.lamp(a, (s * 4.7, y1 + .02, 7.6), (0, 1, 0), r=.22, glow='LavaGlow', guard=True)
        K.lamp(a, (s * 4.7, y1 + .02, 7.0), (0, 1, 0), r=.18, glow='Lamp', guard=False)
    K.tow_hook(steel, (0, 12.75, 2.4), facing=(0, 1, 0), size=.35)


def _turret(a):
    """A T-72-class turret blown up to read on a 26 m truck: a cast dome, two rows of Kontakt-style ERA wedges round
    the front arc, the mantlet and the 2A46 125 mm gun (thermal sleeve, fume extractor), the commander's cupola, the
    gunner's hatch, the IR searchlight, smoke dischargers, rear stowage bins, the snorkel, a short antenna."""
    H, V = 1.38, 1.1
    t = a.pivot('Turret', TURRET)
    body = a.part('Turret_body', 'Team', t)
    k.lathe(body, [(2.05 * H, 0), (2.25 * H, .14 * V), (2.32 * H, .34 * V), (2.14 * H, .7 * V), (1.62 * H, .96 * V),
                   (.9 * H, 1.07 * V), (0, 1.1 * V)], seg=30, worn=(2, 3))
    steel = a.part('Turret_steel', 'Steel', t)
    K.turret_ring(steel, (0, 0, -.05), 2.05 * H, h=.14)
    era = a.part('Era_bricks', 'Armor', t)
    bolts = a.part('Kit_bolts', 'Steel', t)
    for row, (rr, z, tilt) in enumerate(((2.25 * H, .42 * V, .3), (1.98 * H, .8 * V, .75))):
        for i in range(9):
            u = math.radians(-60 + i * 15 + row * 7.5)
            d = Vector((math.sin(u), -math.cos(u), 0))
            rot = (-tilt * math.cos(u), tilt * math.sin(u), u)
            K.plate(era, (.66 * H, .34, .38 * V), loc=(d.x * rr, d.y * rr, z), rot=rot, chamfer=.02)
            bolts.cyl(.04, .05, loc=(d.x * (rr + .17), d.y * (rr + .17), z + .05), rot=(R90 - tilt, 0, u), seg=6,
                      bevel=0)
    mant = a.part('Turret_armor', 'Armor', t)
    K.chamfer_box(mant, (1.55, .8, 1.0), loc=(0, -2.18 * H, .56 * V), c=.08)
    y0, length, z = -2.2 * H - .35, 8.6, .57 * V
    K.gun_barrel(a, 'Main_cannon', 'Turret', 0, y0, z, length, .18, seg=16, extractor=(.42, 1.55, .65),
                 brake_name='Muzzle_brake', brake='collar', sleeve=1.25)
    a.pivot('Muzzle_main', (0, y0 - length - .18, z), 'Turret')
    K.hatch_round(a, (.95 * H, .45 * H, 1.03 * V), r=.58, parent='Turret', periscopes=4)
    K.hatch_round(a, (-.95 * H, .55 * H, 1.0 * V), r=.5, parent='Turret', periscopes=1)
    k.lathe(steel, [(.38, 0), (.38, .62), (.33, .64), (0, .65)], loc=(-.95 * H, -1.5 * H, .94 * V), rot=K.FORWARD,
            seg=12, worn=(1,))
    K.lamp(a, (-.95 * H, -1.5 * H - .66, .94 * V), (0, -1, 0), r=.3, parent='Turret', guard=True)
    for s in (-1, 1):
        K.smoke_dischargers(a, 1.55 * H, -.6 * H, .72 * V, s, count=4, parent='Turret')
        K.chamfer_box(mant, (.7, 2.1, .65), loc=(s * 1.98 * H, 1.05 * H, .5 * V), rot=(0, 0, -s * .5), c=.05)
    for i, x in enumerate((-1.2, 0, 1.2)):
        K.crate(a.part('Stowage', 'Crate', t), a.part('Kit_straps', 'Steel', t), (1.05, .65, .6),
                (x, 2.25 * H, .25 * V))
    k.lathe(steel, [(.24, -1.9), (.24, 1.9)], loc=(0, 2.25 * H + .55, .85 * V), rot=(0, R90, 0), seg=10)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (1.4 * H, 1.55 * H, .8 * V), h=.5, r=.06)
    K.soot(a, (0, TURRET[1] + y0 - length, z + TURRET[2]), radius=.8, k=.35)


def _field_fit(a):
    """Tier 2 / 3 gear with a job (round 2 of the pilot, against the gold's detail density): hydraulic hoses from the
    hoist and suspension cylinders to the frame, tool boxes and jerrycan racks under the body, fire extinguishers and
    a cable reel on the deck, grab rails and lifting eyes on the turret, side marker lamps, a tow cable on the roof,
    ram lamps."""
    hose = a.part('Hoses', 'Rubber')
    paths = [[(2.4, -5.6, 2.9), (2.0, -5.9, 2.4), (1.75, -6.6, 2.4)], [(-2.4, -5.6, 2.9), (-2.1, -6.2, 2.3), (-1.75, -7.2, 2.5)],
             [(3.05, -8.5, 4.7), (2.6, -8.0, 4.4), (2.0, -7.4, 3.5)], [(-3.05, -8.5, 4.7), (-2.5, -7.8, 4.2), (-2.0, -6.9, 3.3)],
             [(2.6, 2.1, 4.6), (2.2, 1.0, 3.9), (1.9, -.4, 3.6)], [(-2.6, 8.1, 4.6), (-2.2, 6.8, 3.8), (-1.9, 5.2, 3.6)]]
    for i, pts in enumerate(paths):
        hose.tube(pts, .06 + .01 * (i % 3), seg=6)
    box = a.part('Toolboxes', 'Armor')
    steel = a.part('Fit_steel', 'Steel')
    for s, (y, w) in ((1, (-1.2, 1.5)), (-1, (-1.0, 1.9)), (1, (6.0, 1.1)), (-1, (6.0, 1.3))):
        K.chamfer_box(box, (.7, w, .8), loc=(s * 5.1, y, FLOOR - .55), c=.05)
        K.handle(steel, (s * 5.46, y - w * .25, FLOOR - .4), (s * 5.46, y + w * .25, FLOOR - .4), (s, 0, 0), h=.06,
                 r=.02)
    for s in (-1, 1):
        for j in range(3):
            K.jerrycan(a.part('Jerrycans', 'Fuel'), (s * (2.2 + j * .45), BODY_Y[1] + .25, 6.7), rot=(0, 0, R90),
                       scale=1.6)
        steel.box((1.6, .08, .06), loc=(s * 2.65, BODY_Y[1] + .55, 7.3), bevel=0)
    for x, y in ((-5.5, -6.4), (5.5, -6.5)):
        k.lathe(a.part('Extinguishers', 'BarrelRed'), [(.16, 0), (.16, .7), (.1, .8), (.05, .9), (0, .9)],
                loc=(x, y, DECK), seg=8, worn=(1,))
    k.lathe(a.part('Cable_reel', 'Steel'), [(.5, -.35), (.5, -.3), (.32, -.3), (.32, .3), (.5, .3), (.5, .35)],
            loc=(-1.4, -11.9, DECK + .55), rot=(0, R90, 0), seg=12)
    K.tow_cable(a.part('Kit_cables', 'Steel'), [(-5.2, 4.0, ROOF + .08), (-5.2, 11.2, ROOF + .08), (-4.4, 11.6, ROOF + .08)],
                r=.07)
    t = 'Turret'
    eye = a.part('Turret_fit', 'Steel', t)
    for x, y in ((1.9, -1.0), (-1.9, -1.0), (1.6, 1.9), (-1.6, 1.9)):
        K.hd.lifting_eye(eye, (x, y, 1.05), yaw=math.atan2(y, x), size=.24)
    K.handle(eye, (-2.4, -.4, .95), (-2.2, 1.2, .95), (0, 0, 1), h=.1, r=.03)
    K.handle(eye, (2.5, .2, .9), (2.3, 1.0, .9), (0, 0, 1), h=.1, r=.03)
    for s in (-1, 1):
        for y in (-3.0, 1.2, 5.4, 9.2):
            K.lamp(a, (s * 6.13, y, ROOF - .3), (s, 0, 0), r=.12, glow='Alloy', guard=False)
        K.lamp(a, (s * 3.6, -12.5, 3.55), (0, -1, .2), r=.16, mat='Armor')
    # Round 3: the left access ladder to the deck, floodlights on the canopy corners for night shifts, the cab's air
    # conditioner, the ram's tilt cylinders, two external fuel drums on the turret's bustle rack.
    K.ladder(a.part('Ladders', 'Steel'), (6.05, -6.2, .6), (6.05, -6.9, DECK), width=.6, step=.4, r=.04)
    for s in (-1, 1):
        K.floodlight(a, (s * 5.3, -12.4, ROOF), facing=(0, -1, -.35), pole=1.1)
        k.lathe(steel, [(.2, 0), (.2, 1.2), (.15, 1.25), (.15, 1.9)], loc=(s * 3.9, -11.0, 1.6),
                rot=(-(R90 - .45), 0, 0), seg=10, worn=(1,))
        K.beacon(a, (s * 4.2, -10.5, ROOF), r=.16)
    K.chamfer_box(a.part('Cab_fit', 'Steel', 'Part_cab'), (1.6, 1.0, .5), loc=(-.4, 1.0, 2.6), c=.05)
    K.grille(a, (-.4, .48, 2.6), 1.3, .36, facing=(0, -1, 0), slats=3, parent='Part_cab')
    rack = a.part('Turret_rack', 'Steel', t)
    rack.tube([(-1.9, 2.9, .2), (-1.9, 3.95, .2), (1.9, 3.95, .2), (1.9, 2.9, .2)], .045, seg=6)
    for x in (-1.0, 1.0):
        K.fuel_drum(a.part('Drums', 'Armor', t), a.part('Drum_bands', 'Steel', t), (x - .45, 4.25, .7), r=.42,
                    h=1.3, lying=True)


def ixion(a):
    """Ixion, the armoured BelAZ-75710 mine truck: see the module docstring."""
    K.suffixed(a)
    _running_gear(a)
    _front(a)
    _ram(a)
    _cab(a)
    _body(a)
    _turret(a)
    _field_fit(a)
    k.clean(a)


BUILDERS = {
    'ixion': (ixion, dict(ao_distance=1.1, grime_height=1.6)),
}
