"""Prompt 35 wave 1 (lane B): the ammunition carrier rebuilt from scratch (spec: Tools/blender/specs/ammo_carrier.json).

An M977 HEMTT-class 8x8 cargo truck with its loading crane (0.82 x real: the def's modelSize 8.36 x 2.02 x 2.46 m):
the boxy two-door cab with the raked lower grille panel, the flat two-pane windscreen and the black front fenders
with square lamps; the engine housing behind the cab with the air cleaner and the vertical exhaust on its right
corner; fat single tyres on four axles (two close together at the front, a tandem at the rear); a flat bed with low
drop sides and stake posts, flat-rack frames at both ends, palletised olive ammunition boxes stacked in tiers in a
grid; the knuckle-boom crane on its platform at the rear, folded over the load; the M2 on a raised ring over the
cab's right seat (the main weapon: `Turret`).

Its own body: nothing is shared with the supply truck (a KamAZ cab-over with a tarpaulin, mb_p35_supply_truck.py).
Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Point_exhaust`, `Point_fire`.
Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
WR, WW, TRACK = .51, .42, .78
AXLES = (-3.05, -1.8, 1.85, 3.1)
FRONT, REAR = -4.18, 4.18
HALF = .99
CAB_Y0, CAB_Y1, CAB_Z0, ROOF = -4.02, -2.78, 1.1, 2.05
GRILLE_TOP = 1.55
BED_Y0, BED_Y1, FLOOR = -1.9, 3.5, 1.28


def _running_gear(a):
    frame = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        K.chamfer_box(frame, (.12, 7.8, .3), loc=(s * .42, 0, .84), c=.02)
    for y in (-3.5, -.9, 2.4):
        frame.box((.74, .08, .16), loc=(0, y, .84), bevel=0)
    susp = a.part('Suspension', 'Steel')
    for y in AXLES:
        for s in (-1, 1):
            P.tread_wheel(a, (s * TRACK, y, WR), WR, WW, s, seg=10, rim_seg=6, depth=.045)
            K.dust(a, (s * TRACK, y, .15), radius=.95, k=.27)
        K.axle(a.part('Axles', 'Undercarriage'), y, WR, TRACK - .12, r=.08, diff=False)
    for s in (-1, 1):
        # Front: taper-leaf springs; rear: the walking-beam tandem on its trunnion.
        for y in AXLES[:2]:
            P.leaf_pack(susp, s * .42, y, WR + .18, 1.0, leaves=2, w=.09)
        susp.box((.12, AXLES[3] - AXLES[2] + .3, .16), loc=(s * .42, (AXLES[2] + AXLES[3]) / 2, WR + .08), bevel=0)
        susp.cyl(.11, .2, loc=(s * .42, (AXLES[2] + AXLES[3]) / 2, WR + .14), rot=(0, R90, 0), seg=8, bevel=0)
    fen = a.part('Fenders', 'Undercarriage')
    for s in (-1, 1):
        # Black front fenders round both front wheels, the rear fenders over the tandem.
        k.extrude(fen, [(-.62, WR + .2), (-.5, WR + .5), (.45, WR + .55), (1.85, WR + .5), (1.95, WR + .2),
                        (1.85, WR + .45), (.45, WR + .5), (-.5, WR + .45)], .46, loc=(s * TRACK, AXLES[0] - .4, 0),
                  axis='X', chamfer=.012)
        k.sweep(fen, [(-.22, -.012), (.22, -.012), (.22, .012), (-.22, .012)],
                [(s * TRACK, AXLES[2] - .65, WR + .32), (s * TRACK, AXLES[2] - .5, WR + .58),
                 (s * TRACK, AXLES[3] + .5, WR + .58), (s * TRACK, AXLES[3] + .65, WR + .32)])
        P.mudflap(a, (s * TRACK, AXLES[3] + .67, WR + .48), w=.44, h=.42)
    # Side boxes between the axles: the fuel tank (left, D-shaped), the battery box (right) and air tanks.
    tank = a.part('Fuel_tanks', 'Armor')
    k.extrude(tank, [(-.18, -.22), (.12, -.22), (.18, -.12), (.18, .16), (.1, .22), (-.18, .22)], 1.3,
              loc=(.8, -.05, .98), rot=(0, 0, R90), axis='X', chamfer=.02, corner=.03)
    a.part('Kit_straps', 'Steel').box((.4, .05, .48), loc=(.8, -.05, .98), bevel=0)
    a.part('Kit_straps', 'Steel').box((.08, .08, .05), loc=(.84, -.5, 1.22), bevel=0)               # filler cap
    P.toolbox(a, (-.8, -.3, .95), (.32, .8, .44))
    a.pivot('Point_fire', (0, 1.0, 1.7))


def _cab(a):
    team = a.part('Cab', 'Team')
    dark = a.part('Cab_dark', 'Undercarriage')
    # Side profile: the grille panel raked back from the bumper, the near-upright windscreen, a flat roof, the back.
    prof = [(CAB_Y1, CAB_Z0), (CAB_Y0 - .02, CAB_Z0), (CAB_Y0 + .12, GRILLE_TOP), (CAB_Y0 + .14, GRILLE_TOP + .04),
            (CAB_Y0 + .24, ROOF - .03), (CAB_Y0 + .27, ROOF), (CAB_Y1, ROOF)]
    k.extrude(team, prof, HALF * 2, axis='X', chamfer=.035, corner=.03)
    # The roof's raised centre (the HEMTT's air-conditioner hump) and roof marker lamps.
    K.chamfer_box(team, (1.0, .7, .1), loc=(-.25, CAB_Y1 - .45, ROOF + .04), c=.03, taper=(.9, .85))
    for x in (-.55, .7):
        a.part('Marker_lamps', 'Alloy').box((.08, .05, .04), loc=(x, CAB_Y0 + .3, ROOF + .02), bevel=0)
    # The big grille on the raked panel, the bumper with the winch fairlead, tow eyes.
    K.grille(a, (0, CAB_Y0 + .055, (CAB_Z0 + GRILLE_TOP) / 2 + .02), 1.2, .36,
             facing=(0, -.966, .259), slats=6, frame_mat='Undercarriage')
    bump = a.part('Bumper', 'Steel')
    K.chamfer_box(bump, (HALF * 2 + .02, .24, .3), loc=(0, FRONT + .12, .86), c=.03)
    bump.box((.36, .06, .14), loc=(0, FRONT - .02, .86), bevel=0)                                # winch fairlead
    for s in (-1, 1):
        bump.box((.1, .06, .1), loc=(s * .55, FRONT - .02, .76), bevel=0)                            # tow eyes
    # Square headlamps in the fender fronts, indicators above them.
    for s in (-1, 1):
        x = s * TRACK
        a.part('Lamp_rims', 'Undercarriage').box((.24, .06, .18), loc=(x, AXLES[0] - 1.0, WR + .42), bevel=0)
        a.part('Lamps', 'Lamp').box((.18, .01, .12), loc=(x, AXLES[0] - 1.035, WR + .42), bevel=0)
        a.part('Lamps', 'Alloy').box((.1, .01, .05), loc=(x + s * .03, AXLES[0] - 1.035, WR + .57), bevel=0)
    # Windscreen: two flat panes with a centre bar, two wipers each side.
    z0, z1 = GRILLE_TOP + .08, ROOF - .1

    def fy(z):
        return CAB_Y0 + .14 + .1 * (z - GRILLE_TOP - .04) / (ROOF - .03 - GRILLE_TOP - .04) - .006
    for s in (-1, 1):
        x0, x1 = s * .04, s * (HALF - .08)
        c = [(x0, fy(z0), z0), (x1, fy(z0), z0), (x1, fy(z1), z1), (x0, fy(z1), z1)]
        if s < 0:
            c = [c[1], c[0], c[3], c[2]]
        K.windscreen(a, c, frame_mat='Undercarriage', wipers=1, bar=.035)
    # Doors with windows, the handles, steps and grab handles; the mirrors on their tube frames.
    glass = a.part('Glass', 'Glass')
    fit = a.part('Cab_fit', 'Steel')
    for s in (-1, 1):
        x = s * (HALF + .004)
        for y in (CAB_Y0 + .3, CAB_Y1 - .12):
            dark.box((.01, .015, ROOF - CAB_Z0 - .15), loc=(x, y, (ROOF + CAB_Z0) / 2), bevel=0)
        glass.box((.012, .62, .36), loc=(s * (HALF + .002), (CAB_Y0 + CAB_Y1) / 2 + .1, ROOF - .3), bevel=0)
        K.handle(fit, (x, CAB_Y1 - .3, CAB_Z0 + .48), (x, CAB_Y1 - .2, CAB_Z0 + .48), (s, 0, 0), h=.02, r=.01)
        P.step(a, (s * (HALF - .12), CAB_Y1 - .5, .8), w=.36)
        fit.tube([(x, CAB_Y0 + .25, ROOF - .15), (x + s * .06, CAB_Y0 + .2, ROOF - .12), (x + s * .06, CAB_Y0 + .2, GRILLE_TOP)],
                 .014, seg=4)
        a.part('Mirrors', 'Undercarriage').box((.035, .12, .28), loc=(x + s * .075, CAB_Y0 + .2, ROOF - .4), bevel=0)
        a.part('Team_band', 'Team').box((.012, 1.0, .09), loc=(s * (HALF + .008), (CAB_Y0 + CAB_Y1) / 2 + .1,
                                                               CAB_Z0 + .22), bevel=0)
    glass.box((1.2, .012, .3), loc=(0, CAB_Y1 + .005, ROOF - .3), bevel=0)


def _engine(a):
    """The engine housing behind the cab: louvred side panels, the air cleaner and exhaust on its right rear."""
    eng = a.part('Engine_housing', 'Armor')
    K.chamfer_box(eng, (HALF * 2 - .1, .8, .72), loc=(0, CAB_Y1 + .42, 1.12 + .36), c=.05)
    for s in (-1, 1):
        K.grille(a, (s * (HALF - .045), CAB_Y1 + .42, 1.5), .55, .36, facing=(s, 0, 0), slats=3,
                 frame_mat='Armor')
    k.lathe(a.part('Air_cleaner', 'Armor'), [(.16, 0), (.16, .5), (.12, .56), (0, .57)],
            loc=(-.72, CAB_Y1 + .62, 1.84), seg=10, worn=(1,))
    K.exhaust(a, (.72, CAB_Y1 + .7, 1.84), r=.05, length=.55, direction=(0, 0, 1), muffler=False, cap=True)
    a.pivot('Point_exhaust', (.72, CAB_Y1 + .7, 2.42))
    K.plate(eng, (.6, .5, .03), loc=(0, CAB_Y1 + .42, 1.85))                                     # access panel


def _bed(a):
    bed = a.part('Bed', 'Armor')
    K.chamfer_box(bed, (HALF * 2, BED_Y1 - BED_Y0, .16), loc=(0, (BED_Y0 + BED_Y1) / 2, FLOOR - .08), c=.02)
    a.part('Bed_floor', 'MetalSheet').box((HALF * 2 - .06, BED_Y1 - BED_Y0 - .06, .02),
                                          loc=(0, (BED_Y0 + BED_Y1) / 2, FLOOR + .01), bevel=0)
    side = a.part('Bed_sides', 'Armor')
    posts = a.part('Rack', 'Steel')
    hh = .32
    for s in (-1, 1):
        side.box((.05, BED_Y1 - BED_Y0, hh), loc=(s * (HALF - .025), (BED_Y0 + BED_Y1) / 2, FLOOR + hh / 2), bevel=0)
        side.box((.02, BED_Y1 - BED_Y0 - .1, .04), loc=(s * (HALF + .005), (BED_Y0 + BED_Y1) / 2, FLOOR + hh - .06),
                 bevel=0)
        for i in range(5):                                            # stake posts with their pockets
            y = BED_Y0 + .25 + i * (BED_Y1 - BED_Y0 - .5) / 4
            posts.box((.05, .06, .62), loc=(s * (HALF - .02), y, FLOOR + .31), bevel=0)
        posts.tube([(s * (HALF - .02), BED_Y0 + .25, FLOOR + .6), (s * (HALF - .02), BED_Y1 - .25, FLOOR + .6)],
                   .022, seg=4)
        a.part('Team_band', 'Team').box((.012, BED_Y1 - BED_Y0 - .3, .08),
                                        loc=(s * (HALF + .012), (BED_Y0 + BED_Y1) / 2, FLOOR + .14), bevel=0)
    # Flat-rack A-frame end walls at both ends of the load.
    for y in (BED_Y0 + .08, BED_Y1 - .1):
        posts.tube([(-HALF + .05, y, FLOOR), (-HALF + .05, y, FLOOR + 1.0), (HALF - .05, y, FLOOR + 1.0),
                    (HALF - .05, y, FLOOR)], .03, seg=4)
        posts.tube([(-HALF + .05, y, FLOOR + .5), (HALF - .05, y, FLOOR + .5)], .025, seg=4)
        posts.tube([(-HALF + .05, y, FLOOR + .05), (0, y, FLOOR + .98), (HALF - .05, y, FLOOR + .05)], .022, seg=4)
    # Rear: the crane platform, tail lamps, the tow pintle.
    plat = a.part('Crane_platform', 'Armor')
    K.chamfer_box(plat, (HALF * 2, REAR - BED_Y1, .2), loc=(0, (BED_Y1 + REAR) / 2, FLOOR - .1), c=.02)
    for s in (-1, 1):
        a.part('Tail_lamps', 'Undercarriage').box((.22, .05, .1), loc=(s * .74, REAR - .02, 1.0), bevel=0)
        a.part('Tail_lenses', 'LavaGlow').box((.18, .01, .07), loc=(s * .74, REAR + .006, 1.0), bevel=0)
    K.chamfer_box(a.part('Bumper', 'Steel'), (HALF * 2 - .2, .1, .14), loc=(0, REAR - .05, .82), c=.02)
    K.tow_hook(a.part('Kit_hooks', 'Steel'), (0, REAR - .01, .72), facing=(0, 1, 0), size=.08)


def _load(a):
    """Palletised ammunition: 2 x 4 pallets, each a stack of olive boxes in tiers, banded, on a wooden pallet."""
    pal = a.part('Pallets', 'Wood')
    band = a.part('Kit_straps', 'Steel')
    for i in range(4):
        y = BED_Y0 + .62 + i * 1.18
        for s in (-1, 1):
            if i == 3 and s > 0:
                continue                                              # one pallet already unloaded
            x = s * .46
            tiers = 3 if (i + (s > 0)) % 2 == 0 else 2
            pal.box((.84, 1.0, .1), loc=(x, y, FLOOR + .05), bevel=0)
            h = .24 * tiers
            P.ammo_box(a, (x, y, FLOOR + .1), size=(.8, .96, h - .02))
            for t in range(1, tiers):                                 # the tier and box seams
                band.box((.81, .97, .012), loc=(x, y, FLOOR + .1 + t * .24 - .01), bevel=0)
            for dy in (0,):
                band.box((.82, .025, h + .01), loc=(x, y + dy, FLOOR + .1 + h / 2), bevel=0)
    # A loose box by the empty pallet place.
    P.ammo_box(a, (.45, BED_Y0 + .62 + 3 * 1.18, FLOOR), size=(.5, .3, .26), rot=(0, 0, .4))


def _crane(a):
    """The knuckle-boom loading crane on the rear platform, folded forward over the load."""
    x0, y0, z0 = -.45, 3.85, FLOOR
    base = a.part('Crane', 'Armor')
    k.lathe(base, [(.3, 0), (.3, .12), (.22, .16), (.18, .62), (.2, .68)], loc=(x0, y0, z0), seg=10, worn=(1, 4))
    K.chamfer_box(base, (.34, .4, .3), loc=(x0, y0, z0 + .82), c=.04)
    boom = a.part('Crane_boom', 'Armor')
    # Main boom from the column top forward and up, then the jib folded back down along it.
    p0, p1 = (x0, y0 - .05, z0 + .9), (x0, 1.4, z0 + 1.12)
    boom.limb(p0, p1, .18, .2, bevel=.015)
    boom.limb((x0, 1.5, z0 + 1.0), (x0, 3.4, z0 + .86), .14, .14, bevel=.012)
    k.lathe(a.part('Crane_rams', 'Steel'), [(.05, 0), (.05, .7), (.035, .72), (.035, 1.25)],
            loc=(x0, y0 - .02, z0 + .55), rot=(math.atan2(y0 - 2.9, 1.0) + .2, 0, 0), seg=8)
    a.part('Crane_hazard', 'Hazard').box((.15, .3, .21), loc=(x0, 1.55, z0 + 1.12), bevel=0)
    st = a.part('Kit_cables', 'Steel')
    st.tube([(x0, 3.4, z0 + .8), (x0, 3.45, z0 + .55)], .012, seg=4)
    st.box((.05, .02, .1), loc=(x0, 3.45, z0 + .5), bevel=0)                                  # hook
    # Crane controls and the outrigger legs folded at the platform corners.
    a.part('Crane_controls', 'Undercarriage').box((.2, .1, .3), loc=(.55, REAR - .1, z0 + .3), bevel=0)


def _gun(a):
    """The M2 on a raised ring over the cab's right seat: the main weapon (`Turret`, hmg_selfdef_15)."""
    P.raised_gun(a, (-.4, CAB_Y1 - .45, ROOF + .02), pivot='Turret', riser=.12, ring_r=.42, post=.16, length=1.0,
                 shield_k=.8)


def ammo_carrier(a):
    """The ammunition carrier: see the module docstring."""
    _running_gear(a)
    _cab(a)
    _engine(a)
    _bed(a)
    _load(a)
    _crane(a)
    _gun(a)
    k.clean(a)


BUILDERS = {
    'ammo_carrier': (ammo_carrier, dict(ao_distance=.55, grime_height=.7)),
}
