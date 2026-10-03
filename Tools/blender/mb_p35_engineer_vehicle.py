"""Prompt 35 wave 3 (lane B): the engineer vehicle rebuilt from scratch (spec: Tools/blender/specs/engineer_vehicle.json).

An armoured recovery / engineer vehicle of the BREM-1 kind on a tank chassis without a turret (unit_sheet: a folding
crane on the roof, a dozer blade in front wider than the hull; unit_refs M88A2 / BREM-1; the def's modelSize 6.45 x
3.02 x 2.02 m): the low hull with its V splash board on the glacis and the raised crew casemate at the front right; the
slewing crane on its ring at the front left with the jib folded back diagonally along the deck to its rest at the
rear right (from above the crane lies across the hull), the hook block and its cable, hazard stripes; the dozer blade
(`Blade`, the runtime rams it) on push arms with its curved mould board, cutting edge and hydraulic rams; six road
wheels, the rear sprocket and front idler, a linked track under rubber side skirts; the commander's cupola with the
M2 on its raised ring and a shield (`Turret`, the def's self-defence gun; MODEL_STANDARD "Roof guns"); the winch
fairlead in the nose, tow bars and tow cables on the sides, spare track links, crates, jerrycans; smoke grenade
launchers on the casemate; Team bands.

Its own hull: no shape is taken from the thermobaric launcher (whose triangles the old file shared).
Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Blade`, `Point_exhaust`, `Point_fire`;
old part names `Crane`, `Boom_inner`, `Boom_stripes`, `Blade_plate`, `Blade_edge`, `Blade_stripe`, `Cupola`; named
for the gate: `Cradle` (the gun's mantlet), `Idlers`, `Skirts`, `Sight`, `Smoke_launchers`, `Stowage`.
Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TX, TW = 1.05, .5
WR = .3
WHEELS = (-1.88, -1.12, -.36, .4, 1.16, 1.92)
DECK = 1.05
NOSE, TAIL = -2.72, 3.0
HALF = 1.32
CRANE = (.62, -1.2, DECK)


def _hull(a):
    hull = a.part('Hull', 'Team')
    prof = [(TAIL, .5), (TAIL + .05, .9), (TAIL - .1, DECK), (-1.35, DECK), (NOSE + .1, .62), (NOSE, .55),
            (NOSE + .35, .4)]
    k.extrude(hull, prof, HALF * 2, axis='X', chamfer=.05, corner=.02)
    k.extrude(a.part('Hull_lower', 'Armor'), [(TAIL - .05, .36), (NOSE + .5, .36), (NOSE + .35, .5), (TAIL - .05, .5)],
              1.6, axis='X', chamfer=.02)
    # The crew casemate at the front right: sloped front and sides, its roof hatches.
    cas = a.part('Casemate', 'Team')
    rings = []
    for z, f, r, xo, xi in ((DECK, -1.5, .5, -1.25, -.05), (DECK + .4, -1.27, .4, -1.15, -.12)):
        rings.append([(xo, f, z), (xi, f, z), (xi, r, z), (xo, r, z)])
    k.sharp_loft(cas, rings, chamfer=.04)
    K.hatch_round(a, (-.62, -.25, DECK + .4), r=.26, periscopes=2, seg=10)
    for dx in (-.95, -.35):
        K.periscope(a, (dx, -1.2, DECK + .4), facing=(0, -1, 0), size=(.16, .12, .1))
    for x in (1.15, .2):                              # two banks on the casemate's front corners
        K.smoke_dischargers(a, x, -1.3, DECK + .32, -1, count=3)
    # The glacis: the V splash board, headlamps, the winch fairlead in the nose, tow hooks.
    for s in (-1, 1):
        a.part('Splash_board', 'Armor').box((1.1, .05, .12), loc=(s * .5, NOSE + .62, .8),
                                            rot=(-.55, 0, -s * .35), bevel=0)
        K.lamp(a, (s * 1.1, NOSE + .3, .76), (0, -1, .1), r=.06, mat='Armor', guard=True)
        K.tow_hook(a.part('Kit_hooks', 'Steel'), (s * .65, NOSE + .05, .48), facing=(0, -1, 0), size=.08)
    fl = a.part('Fairlead', 'Steel')
    k.block(fl, (.5, .14, .26), loc=(0, NOSE + .02, .5), chamfer=.03)
    for dz in (-.08, .08):
        fl.cyl(.04, .4, loc=(0, NOSE - .05, .5 + dz), rot=(0, R90, 0), seg=8, bevel=0)
    # The engine deck: grilles, the exhaust on the left side, the spare links on the rear plate.
    K.grille(a, (0, 2.1, DECK + .02), 1.6, .9, facing=(0, 0, 1), slats=6, frame_mat='Armor')
    K.grille(a, (HALF + .01, 1.6, 1.0), .6, .22, facing=(1, 0, 0), slats=3, frame_mat='Armor')
    a.pivot('Point_exhaust', (HALF + .05, 1.6, 1.0))
    K.soot(a, (HALF + .05, 1.6, 1.0), radius=.5, k=.4)
    a.pivot('Point_fire', (0, 1.3, 1.4))
    links = a.part('Spare_links', 'Undercarriage')
    for j in range(4):
        links.box((.5, .06, .16), loc=(-.6 + j * .4, TAIL + .04, .88), bevel=0)
    for s in (-1, 1):
        a.part('Tail_lamps', 'LavaGlow').box((.1, .01, .06), loc=(s * 1.15, TAIL + .03, 1.08), bevel=0)
        a.part('Team_band', 'Team').box((.012, 2.6, .1), loc=(s * (HALF + .006), .3, 1.05), bevel=0)
    # Tow bars and a tow cable along the sides, crates and jerrycans on the fenders (the gate's stowage).
    K.fender(a.part('Fenders', 'Armor'), TX + .05, NOSE + .3, TAIL - .05, .9, .55, 1, lip=.03)
    K.fender(a.part('Fenders', 'Armor'), TX + .05, NOSE + .3, TAIL - .05, .9, .55, -1, lip=.03)
    tb = a.part('Tow_bars', 'Steel')
    for dz in (0, .12):
        tb.tube([(HALF + .05, -1.6, 1.0 + dz), (HALF + .05, .9, 1.0 + dz)], .035, seg=6)
    K.tow_cable(a.part('Tow_cable', 'Steel'), [(-(HALF + .04), -1.8, .98), (-(HALF + .05), -.2, 1.05),
                                               (-(HALF + .04), 1.2, .98)], r=.03)
    st = a.part('Stowage', 'Crate')
    K.crate(st, a.part('Kit_straps', 'Steel'), (.45, .55, .3), (-(TX + .05), 2.0, .9), bands=1)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (TX + .05, 2.1, .9), rot=(0, 0, R90))
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (TX + .05, 1.82, .9), rot=(0, 0, R90))


def _blade(a):
    """The dozer blade on its push arms: `Blade` pivots at the arms' hinges on the hull sides (the runtime rams it)."""
    b = a.pivot('Blade', (0, NOSE + .55, .62))
    by = -.75                                      # the mould board's line ahead of the hinge
    plate = a.part('Blade_plate', 'Armor', b)
    prof = [(by, -.45), (by - .05, -.45), (by - .2, -.25), (by - .26, 0), (by - .22, .2), (by - .12, .3), (by - .04, .3),
            (by - .12, .18), (by - .15, 0), (by - .1, -.22), (by, -.38)]
    k.extrude(plate, [(y, z) for y, z in prof], 3.0, axis='X', chamfer=.02)
    k.block(a.part('Blade_edge', 'Steel', b), (3.0, .08, .08), loc=(0, by - .03, -.47), chamfer=0)
    stripe = a.part('Blade_stripe', 'Hazard', b)
    for j in range(6):
        stripe.box((.2, .02, .12), loc=(-1.25 + j * .5, by - .265, 0), rot=(0, .6, 0), bevel=0)
    for s in (-1, 1):
        k.extrude(plate, [(by, -.45), (by + .25, -.4), (by + .25, .25), (by, .3)], .05, loc=(s * 1.5, 0, 0), axis='X',
                  chamfer=0)
        a.part('Push_arms', 'Armor', b).limb((s * 1.0, 0, 0), (s * 1.1, by + .1, -.2), .12, .1, bevel=0)
        a.part('Blade_rams', 'Steel', b).limb((s * .55, .3, .35), (s * .6, by + .05, .15), .07, .07, bevel=0)


def _crane(a):
    """The slewing crane at the front left, the jib folded back diagonally to its rest at the rear right."""
    k.lathe(a.part('Crane_ring', 'Steel'), [(.45, 0), (.5, 0), (.5, .1), (.45, .12)], loc=CRANE, seg=14)
    col = a.part('Crane', 'Team')
    k.lathe(col, [(.4, .1), (.4, .3), (.3, .42), (0, .44)], loc=CRANE, seg=12)
    x0, y0, z0 = CRANE
    hinge = (x0, y0 + .1, z0 + .5)
    rest = (-.85, 2.5, DECK + .5)
    d = (rest[0] - hinge[0], rest[1] - hinge[1], rest[2] - hinge[2])
    L = math.sqrt(sum(c * c for c in d))
    # The jib: the outer box section and the inner telescopic section, hazard stripes near the head.
    col.limb(hinge, (hinge[0] + d[0] * .62, hinge[1] + d[1] * .62, hinge[2] + d[2] * .62), .24, .26, bevel=0)
    a.part('Boom_inner', 'Armor').limb((hinge[0] + d[0] * .6, hinge[1] + d[1] * .6, hinge[2] + d[2] * .6), rest,
                                       .17, .19, bevel=0)
    stripes = a.part('Boom_stripes', 'Hazard')
    for f in (.85, .93):
        stripes.limb((hinge[0] + d[0] * f, hinge[1] + d[1] * f, hinge[2] + d[2] * f + .01),
                     (hinge[0] + d[0] * (f + .04), hinge[1] + d[1] * (f + .04), hinge[2] + d[2] * (f + .04) + .01),
                     .19, .21, bevel=0)
    # The luffing ram under the jib, the sheave head, the hook block and its cable, the rest post.
    a.part('Crane_ram', 'Steel').limb((x0 + .1, y0 + .3, z0 + .3), (hinge[0] + d[0] * .35, hinge[1] + d[1] * .35,
                                                                     hinge[2] + d[2] * .35 - .12), .08, .08, bevel=0)
    head = (rest[0] + d[0] / L * .1, rest[1] + d[1] / L * .1, rest[2])
    a.part('Sheave', 'Steel').cyl(.13, .12, loc=head, rot=(0, R90, 0), seg=10, bevel=0)
    a.part('Crane_cable', 'Undercarriage').tube([head, (head[0], head[1] - .05, head[2] - .3)], .015, seg=3)
    k.block(a.part('Hook_block', 'Armor'), (.16, .14, .2), loc=(head[0], head[1] - .05, head[2] - .4), chamfer=.02)
    post = a.part('Jib_rest', 'Steel')
    post.limb((rest[0] - .1, rest[1] - .15, DECK), (rest[0], rest[1] - .12, rest[2] - .14), .06, .06, bevel=0)
    post.box((.3, .1, .05), loc=(rest[0], rest[1] - .12, rest[2] - .12), bevel=0)
    a.part('Team_band', 'Team').box((.5, .5, .015), loc=(x0, y0, z0 + .445), bevel=0)


def _cupola(a):
    loc = (-.62, .35, DECK + .4)
    k.ring(a.part('Cupola', 'Armor'), [(.3, 0), (.38, 0), (.38, .1), (.33, .13), (.3, .13)], loc=loc, seg=14,
           worn=(2,))
    P.raised_gun(a, (loc[0], loc[1], loc[2] + .13), pivot='Turret', riser=.03, ring_r=.33, post=.06, length=1.0,
                 shield_k=.8)
    # Spare 12.7 mm ammunition cans strapped beside the cupola.
    for j in range(2):
        k.block(a.part('Hmg_ammo', 'Crate'), (.12, .3, .2), loc=(loc[0] - .5, loc[1] - .1 + j * .16, loc[2] - .3),
                chamfer=.012)


def engineer_vehicle(a):
    """The engineer vehicle: see the module docstring."""
    _hull(a)
    P.track_run(a, TX, TW, WHEELS, WR, sprocket=(2.66, .62, .28), idler=(-2.42, .55, .27), rollers=(),
                wheel_w=.18, hide_top=(-2.2, 2.45, .66), disc_mat='Armor', wheel_seg=9)
    sk = a.part('Skirts', 'Rubber')
    for s in (-1, 1):
        for i in range(5):
            yc = NOSE + .45 + (i + .5) * (TAIL - NOSE - .7) / 5
            sk.box((.03, (TAIL - NOSE - .7) / 5 - .03, .32), loc=(s * (TX + .3), yc, .76), bevel=0)
    _blade(a)
    _crane(a)
    _cupola(a)
    k.clean(a)


BUILDERS = {
    'engineer_vehicle': (engineer_vehicle, dict(ao_distance=.5, grime_height=.6)),
}
