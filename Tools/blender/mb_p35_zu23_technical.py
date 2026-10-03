"""Prompt 35 pilot 2: the ZU-23 technical rebuilt from scratch (spec: Tools/blender/specs/zu23_technical.json).

A double-cab pickup of the Hilux class (0.83 x real: 4.39 x 1.5 x 1.56 m, the def's modelSize) with a ZU-23-2 on a
pedestal in its load bed: two long 23 mm barrels pointing forward over the cab, their box magazines on the outer
sides, the two crew seats, the sight and the handwheels; four mud-tyred wheels on beam axles and leaf springs, a bull
bar, lamps, mirrors, wipers, door handles, ammunition boxes, a spare wheel, a jerrycan, a short whip.

Runtime nodes (kept from the old model): `Turret` (the gun's yaw pivot on the pedestal), `Main_cannon` /
`Main_cannon_2` (the barrels, recoil rig), `Muzzle_brake` / `Muzzle_brake_2` (the flash hiders), `Muzzle_main`
(one muzzle: zu23 has no `barrels` in data), `Point_exhaust`, `Point_fire`. mb_p34_parts adds the wreck wheels
(`Part_wheel`, `Part_wheelb`) from the Tyres / Wheels / Hubs / Wheel_nuts meshes after this builder.
Built only from frontier_kit / mb_kit27 primitives and the mb_kit35 library. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
WHEEL_R, WHEEL_W, TRACK = .31, .2, .62
AXLES = (-1.3, 1.26)
BELT = 1.0         # waist line (bonnet and bed sides' top)
ROOF = 1.47
FLOOR = .64        # the load bed's floor
HALF = .73         # half the body width
GUN = (0.0, 1.22, FLOOR + .02)


def _running_gear(a):
    for y in AXLES:
        for s in (-1, 1):
            K.truck_wheel(a, (s * TRACK, y, WHEEL_R), WHEEL_R, WHEEL_W, s, lugs=8, seg=12, rim_mat='Steel',
                          lug_depth=.035, nuts=4)
            K.dust(a, (s * TRACK, y, .1), radius=.7, k=.25)
        K.axle(a.part('Axles', 'Undercarriage'), y, WHEEL_R, TRACK - .05, r=.045, diff=True)
    frame = a.part('Chassis', 'Undercarriage')
    with k.mirrored(frame):
        K.chamfer_box(frame, (.08, 3.9, .14), loc=(.36, 0, .44), c=.015)
    for y in (-1.75, -.4, .7, 1.9):
        frame.box((.72, .07, .07), loc=(0, y, .43), bevel=0)
    susp = a.part('Suspension', 'Steel')
    for s in (-1, 1):
        K.leaf_spring(susp, s * .36, AXLES[1], WHEEL_R + .08, .9, leaves=4, w=.06)
        susp.cyl(.03, .3, loc=(s * .42, AXLES[0], WHEEL_R + .16), seg=6, bevel=0)             # front shock
    K.exhaust(a, (-.45, 2.0, .32), r=.025, length=.14, direction=(0, 1, 0), muffler=False, cap=False)
    a.pivot('Point_exhaust', (-.45, 2.16, .32))
    a.pivot('Point_fire', (0, -1.6, .85))


def _body(a):
    team = a.part('Cab', 'Team')
    dark = a.part('Body_dark', 'Undercarriage')
    # The lower body: bonnet and doors in one side profile (the bonnet slopes to the grille).
    prof = [(-2.17, .5), (.47, .5), (.47, BELT), (.45, BELT - .02), (-1.02, BELT + .02), (-2.0, BELT - .05),
            (-2.17, BELT - .12)]
    k.extrude(team, prof, HALF * 2, axis='X', chamfer=.03, corner=.035)
    # The greenhouse: windscreen raked back, the roof, the rear window; a little narrower than the body.
    start = len(team.bm.verts)
    k.extrude(team, [(-1.02, BELT), (.45, BELT), (.4, ROOF - .03), (.33, ROOF), (-.42, ROOF), (-.5, ROOF - .03)],
              HALF * 2 - .1, axis='X', chamfer=.03, corner=.03)
    team.bm.verts.ensure_lookup_table()
    for v in list(team.bm.verts)[start:]:          # tumblehome: the greenhouse sides lean in towards the roof
        v.co.x *= 1 - .24 * max(0.0, v.co.z - BELT) / (ROOF - BELT)
    # The load bed, open: the tub under the floor, the drop sides, the front wall and the tailgate, the rails.
    bed = a.part('Bed', 'Team')
    K.chamfer_box(bed, (HALF * 2, 1.7, FLOOR - .5), loc=(0, 1.32, (FLOOR + .5) / 2), c=.02)
    a.part('Bed_floor', 'Armor').box((HALF * 2 - .1, 1.62, .02), loc=(0, 1.32, FLOOR + .01), bevel=0)
    for s in (-1, 1):
        k.block(bed, (.05, 1.7, BELT - FLOOR), loc=(s * (HALF - .025), 1.32, (BELT + FLOOR) / 2), chamfer=0)
        bed.box((.06, 1.72, .05), loc=(s * (HALF - .02), 1.32, BELT + .02), bevel=0)               # bed rails
    k.block(bed, (HALF * 2, .05, BELT - FLOOR), loc=(0, .5, (BELT + FLOOR) / 2), chamfer=0)
    k.block(bed, (HALF * 2 - .1, .05, BELT - FLOOR - .04), loc=(0, 2.14, (BELT + FLOOR) / 2 - .02), chamfer=0)
    K.hinge(a.part('Kit_hinges', 'Steel'), (-.5, 2.18, .56), (.5, 2.18, .56), r=.018, knuckles=3)
    # Seams and wheel arches: the door gaps, the arch flares, the sill, the team band along the doors.
    for s in (-1, 1):
        x = s * (HALF + .003)
        for y in (-1.0, -.27, .45):
            dark.box((.01, .015, BELT - .55), loc=(x, y, (BELT + .55) / 2), bevel=0)
        for y in AXLES:
            k.sweep(a.part('Fender_flares', 'Undercarriage'), [(-.03, -.02), (.03, -.02), (.03, .02), (-.03, .02)],
                    [(s * (HALF + .01), y + .42 * math.cos(u), WHEEL_R + .38 * math.sin(u))
                     for u in [math.radians(d) for d in range(10, 175, 20)]])
        dark.box((.04, 1.4, .06), loc=(s * (HALF - .01), -.27, .52), bevel=0)                     # sill
        a.part('Team_band', 'Team').box((.012, 1.5, .07), loc=(s * (HALF + .006), -.25, .8), bevel=0)
    # Glass: the windscreen with frame and wipers, the side windows (front and rear doors), the rear window.
    K.windscreen(a, [(-.6, -1.0, BELT + .03), (.6, -1.0, BELT + .03), (.56, -.52, ROOF - .05),
                     (-.56, -.52, ROOF - .05)], frame_mat='Undercarriage', wipers=2, bar=.025)
    glass = a.part('Glass', 'Glass')
    for s in (-1, 1):
        glass.box((.01, .6, .36), loc=(s * (HALF - .065), -.62, BELT + .23), bevel=0)
        glass.box((.01, .58, .34), loc=(s * (HALF - .065), .08, BELT + .23), bevel=0)
    glass.box((1.0, .01, .3), loc=(0, .44, BELT + .24), bevel=0)
    # Bonnet scoop, grille, lamps, bumpers, bull bar, tow hook, mirrors, handles, a whip on the cab corner.
    K.chamfer_box(team, (.4, .3, .05), loc=(0, -1.55, BELT + .01), c=.012)
    K.grille(a, (0, -2.18, .78), .8, .22, facing=(0, -1, 0), slats=4, frame_mat='Steel')
    for s in (-1, 1):
        K.lamp(a, (s * .55, -2.18, .8), (0, -1, 0), r=.07, mat='Steel', guard=False)
        K.lamp(a, (s * .62, 2.18, .82), (0, 1, 0), r=.05, glow='LavaGlow', guard=False)
    steel = a.part('Bull_bar', 'Steel')
    steel.tube([(-.62, -2.18, .5), (-.62, -2.25, .55), (-.55, -2.27, .96), (.55, -2.27, .96), (.62, -2.25, .55),
                (.62, -2.18, .5)], .028, seg=6)
    steel.tube([(-.3, -2.22, .5), (-.3, -2.27, .94)], .022, seg=6)
    steel.tube([(.3, -2.22, .5), (.3, -2.27, .94)], .022, seg=6)
    K.chamfer_box(a.part('Bumpers', 'Steel'), (1.4, .1, .12), loc=(0, -2.22, .52), c=.02)
    K.chamfer_box(a.part('Bumpers', 'Steel'), (1.36, .08, .1), loc=(0, 2.21, .5), c=.02)
    K.tow_hook(a.part('Kit_hooks', 'Steel'), (0, -2.27, .44), facing=(0, -1, 0), size=.05)
    fit = a.part('Cab_fit', 'Steel')
    for s in (-1, 1):
        K.mirror(fit, (s * (HALF - .04), -.9, BELT + .12), s, arm=.05, size=(.03, .05, .1))
        for y in (-.5, .2):
            K.handle(fit, (s * (HALF + .005), y - .04, BELT - .08), (s * (HALF + .005), y + .04, BELT - .08), (s, 0, 0),
                     h=.015, r=.008)
    K.whip_antenna(a.part('Antennas', 'Steel'), (.5, .3, ROOF - .03), h=.12, r=.025)


def _bed_stowage(a):
    crates = a.part('Ammo_boxes', 'Crate')
    straps = a.part('Kit_straps', 'Steel')
    K.crate(crates, straps, (.42, .26, .2), (-.42, .7, FLOOR + .02))
    K.crate(crates, straps, (.42, .26, .2), (-.42, .7, FLOOR + .22))
    K.crate(crates, straps, (.36, .24, .18), (.45, 2.0, FLOOR + .02), rot=(0, 0, R90))
    K.truck_wheel(a, (.42, .68, FLOOR + .13), .26, .17, 1, lugs=6, seg=12, tyre='Spare_wheel', rim='Spare_rim',
                  lug_depth=.03, nuts=0, hub_cap=False)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (-.5, 2.0, FLOOR + .02), rot=(0, 0, 0), scale=.83)


def _gun(a):
    """The ZU-23-2 on its pedestal: a turntable ring, the carriage with the two seats, the cradle carrying the two
    barrels (jackets, flash hiders), the box magazines outside each breech, the sight in the middle, the elevating and
    traversing handwheels."""
    steel = a.part('Gun_pedestal', 'Steel')
    # Wave 1 (the owner's roof-gun rule): the pedestal stands 5 cm taller with a collar and gussets, the box
    # magazines stand upright over the breeches and the AA ring sight rises on its post, so the gun reads tall over
    # the cab roof (the height stays within 10 % of modelSize).
    k.lathe(steel, [(.3, 0), (.3, .06), (.12, .1), (.1, .44), (.14, .45), (.14, .48), (.18, .51)], loc=GUN, seg=12,
            worn=(1, 4))
    for g in range(2):
        u = g * math.pi + R90
        steel.box((.02, .16, .2), loc=(GUN[0] + math.sin(u) * .14, GUN[1] + math.cos(u) * .14, GUN[2] + .16),
                  rot=(0, 0, -u), bevel=0)
    t = a.pivot('Turret', (GUN[0], GUN[1], GUN[2] + .51))
    car = a.part('Turret_armor', 'Armor', t)
    K.chamfer_box(car, (.62, .7, .1), loc=(0, .05, .05), c=.02)
    for s in (-1, 1):
        K.chamfer_box(car, (.08, .5, .36), loc=(s * .2, -.05, .26), c=.015)                    # cradle cheeks
    seats = a.part('Gun_seats', 'Canvas', t)
    sf = a.part('Gun_fit', 'Steel', t)
    for s in (-1, 1):
        sf.tube([(s * .2, .3, .1), (s * .42, .42, .2), (s * .42, .5, .2)], .015, seg=4)
        K.chamfer_box(seats, (.2, .18, .05), loc=(s * .42, .5, .23), c=.012)
        K.chamfer_box(seats, (.2, .04, .18), loc=(s * .42, .6, .32), c=.012)
        k.ring(sf, [(.07, -.008), (.08, -.008), (.08, .008), (.07, .008)], loc=(s * .32, .25, .3),
               rot=(0, R90, 0), seg=10)                                                              # handwheels
    z = .42                                                       # barrel axis over the pivot (world ~1.54)
    for x, rig, brake in ((.11, 'Main_cannon', 'Muzzle_brake'), (-.11, 'Main_cannon_2', 'Muzzle_brake_2')):
        part = a.part(rig, 'Steel', t)
        L = 1.75
        k.lathe(part, [(.07, -.15), (.07, .25), (.055, .3), (.05, .55), (.042, .62), (.042, L - .14), (0, L - .14)],
                loc=(x, .15, z), rot=K.FORWARD, seg=8, worn=(1, 3))
        k.lathe(a.part(brake, 'Undercarriage', t), [(.045, L - .16), (.055, L - .12), (.055, L), (.035, L),
                                                    (.035, L - .03), (0, L - .03)], loc=(x, .15, z), rot=K.FORWARD,
                seg=8, worn=(1,))
        side = 1 if x > 0 else -1
        K.chamfer_box(a.part('Magazines', 'Armor', t), (.09, .3, .22), loc=(x + side * .1, .05, z), c=.015)
        sf.box((.012, .26, .02), loc=(x + side * .147, .05, z + .06), bevel=0)                      # magazine latch
    K.periscope(a, (0, -.15, z - .06), facing=(0, -1, 0), parent='Turret', size=(.09, .1, .1), mat='Armor')
    sight = a.part('Gun_sight', 'Steel', t)
    sight.cyl(.012, .05, loc=(0, -.3, z + .0), seg=5, bevel=0)
    sight.torus(.05, .007, loc=(0, -.3, z + .05), rot=(R90, 0, 0), seg=10, ring=3)
    # Owner decision 2: the data fires both barrels (barrels 2): a muzzle for each under the slot's Muzzle_main.
    a.pivot('Muzzle_main', (0, .15 - 1.75 - .01, z), 'Turret')
    for i, x in enumerate((.11, -.11)):
        a.pivot(f'Muzzle_b{i + 1}_main', (x, 0, 0), 'Muzzle_main')
    K.soot(a, (0, GUN[1] + .15 - 1.75, GUN[2] + .51 + z), radius=.25, k=.3)


def zu23_technical(a):
    """The ZU-23 technical: see the module docstring."""
    _running_gear(a)
    _body(a)
    _bed_stowage(a)
    _gun(a)
    k.clean(a)


BUILDERS = {
    'zu23_technical': (zu23_technical, dict(ao_distance=.4, grime_height=.45)),
}
