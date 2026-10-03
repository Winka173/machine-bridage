"""Prompt 35 wave 1 (lane B): the supply truck rebuilt from scratch (spec: Tools/blender/specs/supply_truck.json).

A KamAZ-6350-class 8x8 cab-over cargo truck (the def's modelSize 8.37 x 2.02 x 2.42 m): the flat-fronted tilt cab
over the first axle with its two-piece windscreen, the bumper with lamps and steps, the grille panel, big mirrors;
behind the cab the air-intake snorkel, the exhaust stack and the spare wheel; a ladder frame on four axles (two
steered at the front, a tandem at the rear) with single tyres, the side fuel tank and the battery / tool boxes; a
dropside cargo bed with a canvas cover on bows over its front two thirds and wooden crates and ammunition boxes in
the open rear third; the M2 on a raised ring over the cab's roof hatch (the main weapon: `Turret`).

Its own body: no shape is shared with the ammunition carrier (a HEMTT with an engine housing behind a fibreglass
cab and an open flat-rack bed, mb_p35_ammo_carrier.py).

Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Point_exhaust`, `Point_fire`.
Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
WR, WW, TRACK = .5, .34, .8             # tyre radius, width, wheel centre off the middle
AXLES = (-2.95, -1.75, 1.95, 3.15)
FRONT, REAR = -4.18, 4.18
HALF = .98                               # half the cab / bed width
CAB_Y0, CAB_Y1 = -4.06, -2.42            # cab front face and back wall
CAB_Z0, ROOF = 1.02, 1.98
BELT = CAB_Z0 + .55                      # the cab's belt line: the windscreen's foot
BED_Y0, BED_Y1, BED_FLOOR = -2.2, 4.1, 1.24
SIDE_TOP = 1.72
TARP_END = 1.75


def _chassis(a):
    frame = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        K.chamfer_box(frame, (.1, 7.9, .26), loc=(s * .44, 0, .86), c=.02)
    for y in (-3.6, -2.35, -.6, .9, 2.5, 3.95):
        frame.box((.8, .08, .14), loc=(0, y, .86), bevel=0)
    for y in AXLES:
        for s in (-1, 1):
            P.tread_wheel(a, (s * TRACK, y, WR), WR, WW, s, seg=10, rim_seg=6)
            K.dust(a, (s * TRACK, y, .15), radius=.9, k=.25)
        K.axle(a.part('Axles', 'Undercarriage'), y, WR, TRACK - .1, r=.07, diff=False)
    susp = a.part('Suspension', 'Steel')
    for s in (-1, 1):
        for y in AXLES[:2]:
            P.leaf_pack(susp, s * .44, y, WR + .16, 1.1, leaves=2, w=.08)
        # The rear tandem's balancer: one long spring pack pivoting between the two axles.
        P.leaf_pack(susp, s * .44, (AXLES[2] + AXLES[3]) / 2, WR + .14, 1.5, leaves=3, w=.09)
        # Front shock absorbers and steering drag link.
    # Fenders over every wheel pair (front pair on the cab, the rest under the bed).
    fen = a.part('Fenders', 'Undercarriage')
    for s in (-1, 1):
        for y0, y1 in ((AXLES[1] - .62, AXLES[1] + .55), (AXLES[2] - .62, AXLES[3] + .62)):
            k.sweep(fen, [(-.19, -.012), (.19, -.012), (.19, .012), (-.19, .012)],
                    [(s * TRACK, y0, WR + .3), (s * TRACK, y0 + .14, WR + .56), (s * TRACK, y1 - .14, WR + .56),
                     (s * TRACK, y1, WR + .3)])
        P.mudflap(a, (s * TRACK, AXLES[3] + .66, WR + .45), w=.4, h=.42)
        P.mudflap(a, (s * TRACK, AXLES[1] + .58, WR + .45), w=.4, h=.38)
    # Side furniture between the axles: the fuel tank (left), the battery box and tool box (right).
    P.fuel_tank(a, (.78, .1, .95), 1.4, .24, straps=1)
    P.toolbox(a, (-.78, -.25, .92), (.32, .7, .42))
    a.pivot('Point_fire', (0, .3, 1.6))


def _cab(a):
    team = a.part('Cab', 'Team')
    dark = a.part('Cab_dark', 'Undercarriage')
    # Horizontal sections bottom to roof: the front corners wrap round at an angle (the Mustang cab's corner
    # panels), the face is upright below the belt and raked above it, the roof edge rounds over.
    rings = []
    for z, yf, c, inset in ((CAB_Z0, CAB_Y0 + .01, .26, 0), (BELT, CAB_Y0, .26, 0), (ROOF - .1, CAB_Y0 + .2, .28, .03),
                            (ROOF, CAB_Y0 + .32, .3, .06)):
        h = HALF - inset
        rings.append([(-h, CAB_Y1, z), (-h, yf + c, z), (-h + c, yf, z), (h - c, yf, z), (h, yf + c, z), (h, CAB_Y1, z)])
    k.sharp_loft(team, rings, chamfer=.04)
    # The roof cap with its sun visor and marker lamps.
    K.chamfer_box(team, (HALF * 2 - .14, 1.2, .07), loc=(0, CAB_Y1 - .62, ROOF + .03), c=.02)
    a.part('Window_frames', 'Undercarriage').box((HALF * 2 - .1, .2, .03), loc=(0, CAB_Y0 + .22, ROOF - .04),
                                              rot=(-.2, 0, 0), bevel=0)
    for x in (-.5, 0, .5):
        a.part('Marker_lamps', 'Alloy').box((.09, .05, .04), loc=(x, CAB_Y0 + .34, ROOF + .02), bevel=0)
    # Windscreen in two panes (the centre pillar) on the raked face, with frame and a wiper each.
    def face_y(z):
        return CAB_Y0 + .2 * (z - BELT) / (ROOF - .1 - BELT)
    zb, zt = BELT + .04, ROOF - .14
    for s in (-1, 1):
        x0, x1 = s * .05, s * (HALF - .3)
        c = [(x0, face_y(zb) - .005, zb), (x1, face_y(zb) - .005, zb), (x1, face_y(zt) - .005, zt),
             (x0, face_y(zt) - .005, zt)]
        if s < 0:
            c = [c[1], c[0], c[3], c[2]]
        K.windscreen(a, c, frame_mat='Undercarriage', wipers=1, bar=.03)
    # Corner windows in the angled panels.
    glass = a.part('Glass', 'Glass')
    for s in (-1, 1):
        x, y = s * (HALF - .12), CAB_Y0 + .14
        glass.box((.2, .012, .36), loc=(x + s * .01, y + .005, BELT + .26), rot=(-.2, 0, s * -.785), bevel=0)
    # The grille panel, the cab-tilt badge plate (blank), headlamps in the bumper, fog lamps.
    K.grille(a, (0, CAB_Y0 - .01, CAB_Z0 + .27), 1.1, .36, facing=(0, -1, 0), slats=5, frame_mat='Undercarriage')
    bump = a.part('Bumper', 'Steel')
    K.chamfer_box(bump, (HALF * 2 + .04, .22, .34), loc=(0, FRONT + .11, .9), c=.03)
    bump.box((.5, .1, .1), loc=(0, FRONT + .02, .7), bevel=0)                           # tow pin housing
    for s in (-1, 1):
        K.lamp(a, (s * .72, FRONT - .005, .95), (0, -1, 0), r=.08, mat='Undercarriage', guard=False)
    # Doors: seams, the door window, handles, the boarding steps under the door and grab rails.
    fit = a.part('Cab_fit', 'Steel')
    for s in (-1, 1):
        x = s * (HALF + .004)
        for y in (CAB_Y0 + .48, CAB_Y1 - .18):
            dark.box((.01, .015, ROOF - CAB_Z0 - .25), loc=(x, y, (ROOF + CAB_Z0) / 2 - .05), bevel=0)
        dark.box((.01, CAB_Y1 - .18 - CAB_Y0 - .48, .015), loc=(x, (CAB_Y0 + CAB_Y1) / 2 + .15, CAB_Z0 + .1),
                 bevel=0)
        glass.box((.012, .7, .42), loc=(s * (HALF + .002), -3.3, ROOF - .38), bevel=0)
        dark.box((.014, .74, .03), loc=(s * (HALF + .004), -3.3, ROOF - .6), bevel=0)
        K.handle(fit, (x, -2.95, CAB_Z0 + .55), (x, -2.85, CAB_Z0 + .55), (s, 0, 0), h=.02, r=.01)
        fit.tube([(x + s * .02, CAB_Y0 + .42, CAB_Z0 + .15), (x + s * .05, CAB_Y0 + .42, CAB_Z0 + .25),
                  (x + s * .05, CAB_Y0 + .42, ROOF - .3), (x + s * .02, CAB_Y0 + .42, ROOF - .2)], .015, seg=4)
        P.step(a, (s * (HALF - .1), -3.6, .62), w=.36)
        P.step(a, (s * (HALF - .1), -3.6, .87), w=.36)
        K.mirror(fit, (s * (HALF - .04), CAB_Y0 + .15, ROOF - .25), s, arm=.06, size=(.04, .1, .3))
        a.part('Team_band', 'Team').box((.012, 1.2, .1), loc=(s * (HALF + .008), -3.25, CAB_Z0 + .32), bevel=0)
        # The front wheel arch flare on the cab's lower edge.
        k.sweep(a.part('Fender_flares', 'Undercarriage'), [(-.04, -.015), (.04, -.015), (.04, .015), (-.04, .015)],
                [(s * (HALF + .01), AXLES[0] + .62 * math.cos(u), WR + .58 * math.sin(u))
                 for u in [math.radians(d) for d in range(20, 165, 24)]])
    glass.box((1.0, .012, .32), loc=(0, CAB_Y1 + .005, ROOF - .32), bevel=0)             # rear window
    # Roof hatch under the gun ring (the ring's riser sits on it) and a whip antenna on the rear corner.
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.8, CAB_Y1 + .12, ROOF + .02), h=.4, r=.02)


def _behind_cab(a):
    # Air-intake snorkel (right) with its filter can, the exhaust stack (left), the spare wheel carrier.
    st = a.part('Air_intake', 'Armor')
    k.lathe(st, [(.12, 0), (.12, .55), (.1, .6), (.06, .62)], loc=(-.78, CAB_Y1 + .2, 1.2), seg=10, worn=(1,))
    st.tube([(-.78, CAB_Y1 + .2, 1.8), (-.78, CAB_Y1 + .2, ROOF + .05), (-.78, CAB_Y1 + .05, ROOF + .14)], .06, seg=8)
    a.part('Grilles', 'Undercarriage').cyl(.09, .1, loc=(-.78, CAB_Y1 - .02, ROOF + .14), rot=K.FORWARD,
                                                  seg=8, bevel=0)
    K.exhaust(a, (.82, CAB_Y1 + .18, 1.05), r=.05, length=1.12, direction=(0, 0, 1), muffler=False, cap=True)
    a.pivot('Point_exhaust', (.82, CAB_Y1 + .18, 2.25))
    carrier = a.part('Cab_fit', 'Steel')
    carrier.box((.9, .05, .05), loc=(0, CAB_Y1 + .28, 1.1), bevel=0)
    for s in (-1, 1):
        carrier.box((.05, .05, .7), loc=(s * .4, CAB_Y1 + .28, 1.45), bevel=0)
    P.tread_wheel(a, (0, CAB_Y1 + .42, 1.55), .46, .3, 1, seg=10, rim_seg=6, tyre='Spare_wheel', rim='Spare_rim', hub=False)
    # Can't spin: the spare's axis is along Y (it stands behind the cab, face to the rear).
    a.part('Chassis', 'Undercarriage').tube([(.3, CAB_Y1 + .05, 1.2), (.3, CAB_Y1 + .3, 1.15),
                                               (.3, BED_Y0 - .05, 1.1)], .015, seg=4)


def _bed(a):
    bed = a.part('Bed', 'Armor')
    floor = a.part('Bed_floor', 'Wood')
    K.chamfer_box(bed, (HALF * 2, BED_Y1 - BED_Y0, .14), loc=(0, (BED_Y0 + BED_Y1) / 2, BED_FLOOR - .07), c=.02)
    floor.box((HALF * 2 - .08, BED_Y1 - BED_Y0 - .08, .02), loc=(0, (BED_Y0 + BED_Y1) / 2, BED_FLOOR + .01), bevel=0)
    # Cross members under the floor and the long sills.
    under = a.part('Bed_frame', 'Undercarriage')
    for i in range(5):
        y = BED_Y0 + .3 + i * (BED_Y1 - BED_Y0 - .6) / 4
        under.box((HALF * 2 - .04, .07, .1), loc=(0, y, BED_FLOOR - .19), bevel=0)
    # Drop sides (two leaves a side, hinged at the floor), the headboard with its window guard, the tailgate.
    side = a.part('Bed_sides', 'Armor')
    hing = a.part('Kit_hinges', 'Steel')
    hh = SIDE_TOP - BED_FLOOR
    L = (BED_Y1 - BED_Y0) / 2
    for s in (-1, 1):
        for i in range(2):
            yc = BED_Y0 + (i + .5) * L
            side.box((.05, L - .04, hh), loc=(s * (HALF - .025), yc, BED_FLOOR + hh / 2), bevel=0)
            side.box((.02, L - .06, .03), loc=(s * (HALF + .005), yc, BED_FLOOR + hh * .5), bevel=0)      # rib
            side.box((.03, L - .04, .04), loc=(s * (HALF + .005), yc, SIDE_TOP - .02), bevel=0)        # top rail
            if i == 0 and s > 0:
                K.hinge(hing, (s * (HALF + .01), yc - .1, BED_FLOOR + .02),
                        (s * (HALF + .01), yc + .1, BED_FLOOR + .02), r=.018, knuckles=2)
            hing.box((.03, .04, .08), loc=(s * (HALF + .01), yc + L * .48, SIDE_TOP - .08), bevel=0)        # latch
        a.part('Team_band', 'Team').box((.012, BED_Y1 - BED_Y0 - .2, .1), loc=(s * (HALF + .012),
                                                                                (BED_Y0 + BED_Y1) / 2, SIDE_TOP - .2),
                                        bevel=0)
    K.chamfer_box(side, (HALF * 2, .06, .95), loc=(0, BED_Y0 + .03, BED_FLOOR + .47), c=.015)       # headboard
    side.box((HALF * 2 - .06, .05, hh), loc=(0, BED_Y1 - .025, BED_FLOOR + hh / 2), bevel=0)           # tailgate
    for x in (-.6, -.2, .2, .6):
        side.box((.03, .02, hh - .06), loc=(x, BED_Y1 + .005, BED_FLOOR + hh / 2), bevel=0)
    # Rear: bumper, tail lamps, reflectors, the tow pintle, the rear steps.
    rb = a.part('Bumper', 'Steel')
    K.chamfer_box(rb, (HALF * 2 - .1, .12, .14), loc=(0, REAR - .06, .78), c=.02)
    for s in (-1, 1):
        a.part('Tail_lamps', 'Undercarriage').box((.24, .05, .1), loc=(s * .74, REAR - .02, .8), bevel=0)
        a.part('Tail_lenses', 'LavaGlow').box((.2, .01, .07), loc=(s * .74, REAR + .006, .8), bevel=0)
        a.part('Reflectors', 'LavaGlow').box((.08, .01, .05), loc=(s * .55, REAR + .001, .8), bevel=0)
    K.tow_hook(a.part('Kit_hooks', 'Steel'), (0, REAR - .02, .68), facing=(0, 1, 0), size=.08)


def _cargo(a):
    P.tarp_bows(a, BED_Y0 + .06, TARP_END, HALF + .01, SIDE_TOP - .05, ROOF + .02, bows=4, hoops=False, steps=2)
    # The cover's rear edge rolled up on itself; two bare bows over the open load.
    P.canvas_roll(a, (0, TARP_END + .08, ROOF - .06), HALF * 2 - .1, r=.1)
    bows = a.part('Bows', 'Undercarriage')
    for y in (2.75, 3.75):
        bows.tube([(-HALF + .02, y, SIDE_TOP - .05), (-HALF + .02, y, ROOF - .2), (-HALF + .2, y, ROOF - .02),
                   (HALF - .2, y, ROOF - .02), (HALF - .02, y, ROOF - .2), (HALF - .02, y, SIDE_TOP - .05)], .025,
                   seg=5)
    bows.tube([(0, TARP_END + .1, ROOF - .02), (0, 3.95, ROOF - .02)], .02, seg=4)                 # ridge pole
    # The open load: wooden crates (stencilled lids), olive ammunition boxes stacked two high, a tied-down drum.
    wood = a.part('Crates', 'Wood')
    straps = a.part('Kit_straps', 'Steel')
    z = BED_FLOOR + .02
    K.crate(wood, straps, (.8, .55, .5), (.45, 2.2, z), bands=1)
    K.crate(wood, straps, (.8, .55, .5), (.45, 2.8, z), bands=1)
    K.crate(wood, straps, (.75, .5, .42), (.45, 2.5, z + .5), rot=(0, 0, .05))
    for j, y in enumerate((2.25, 2.75)):
        P.ammo_box(a, (-.42, y, z))
        if j < 1:
            P.ammo_box(a, (-.42, y + .1, z + .26))
    P.ammo_box(a, (.4, 3.55, z), rot=(0, 0, R90))
    # Ratchet straps over the load.
    for y in (2.5,):
        straps.tube([(HALF - .03, y, SIDE_TOP - .02), (.45, y, z + .95), (-.4, y, z + .56),
                     (-HALF + .03, y, SIDE_TOP - .02)], .012, seg=3)


def _gun(a):
    """The M2 on a raised ring over the cab roof hatch: the main weapon (`Turret`, mg_jeep)."""
    P.raised_gun(a, (.25, -2.95, ROOF + .06), pivot='Turret', riser=.1, ring_r=.4, post=.16, length=1.0,
                 shield_k=.75)


def supply_truck(a):
    """The supply truck: see the module docstring."""
    _chassis(a)
    _cab(a)
    _behind_cab(a)
    _bed(a)
    _cargo(a)
    _gun(a)
    k.clean(a)


BUILDERS = {
    'supply_truck': (supply_truck, dict(ao_distance=.55, grime_height=.7)),
}
