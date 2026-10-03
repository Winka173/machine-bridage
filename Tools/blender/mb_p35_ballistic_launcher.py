"""Prompt 35 wave 9 (lane C): the ballistic missile launcher rebuilt from scratch (spec:
Tools/blender/specs/ballistic_launcher.json).

The Iskander-M 9P78-1 on the MZKT-7930 8x8 (unit_refs: 9K720 Iskander, 9M723; the def's modelSize 10.7 x 2.53 x
4.18 m, its height the opened cover): the full-width four-seat cab with its raked split windscreen, side windows,
doors, the grille and bumper below, lamps and mirrors; the long chassis on four evenly spaced axles on big lugged
tyres with their wings; the launcher bay with its clamshell cover opened up on both sides (ribbed panels on their
hinges and rams), inside it the two 9M723 missiles side by side on the launch beam (`Turret`: their ogive noses,
the dark seeker windows, the four tail fins and the rocket nozzles) with the erector's rams at the rear; the
rear stabilising jacks, toolboxes, jerrycans, the spare wheel, the cab's roof rack and whips.

Runtime nodes kept: `Turret`, `Muzzle_main`, the old file's `Mount_mg` / `Muzzle_mg` (plain pivots on the cab
roof; the def has no secondary), `Point_exhaust`, `Point_fire`. Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Matrix

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WR = .6
AXLES = (-3.45, -1.75, 1.3, 3.0)
TX = .88
FZ = 1.05
NOSE, TAIL = -5.35, 5.35
BAY_Z = 1.25        # the bay's floor
BAY_TOP = 2.35      # the bay's sill (the cover's hinge line)


def _cab(a):
    cab = a.part('Cab', 'Team')
    C.section_loft(cab, [
        (NOSE, [(0, FZ - .25), (1.16, FZ - .25), (1.18, 1.6), (1.12, 1.66), (0, 1.66)]),
        (NOSE + .5, [(0, FZ - .25), (1.2, FZ - .25), (1.22, 1.62), (.9, 2.55), (0, 2.6)]),
        (NOSE + 2.3, [(0, FZ - .25), (1.2, FZ - .25), (1.22, 1.62), (.92, 2.6), (0, 2.62)]),
    ])
    for s in (-1, 1):
        K.windscreen(a, [(s * .05 if s < 0 else .05, NOSE + .05, 1.72), (s * 1.0, NOSE + .05, 1.72),
                         (s * .8, NOSE + .42, 2.5), (s * .05, NOSE + .42, 2.5)][::s], frame_mat='Team', wipers=1)
        gl = a.part('Glass', 'Glass')
        for y in (NOSE + .85, NOSE + 1.75):
            gl.box((.01, .6, .4), loc=(s * 1.09, y, 2.08), rot=(0, s * .34, 0), bevel=0)
        dr = a.part('Doors', 'Team')
        for y in (NOSE + .85, NOSE + 1.75):
            dr.box((.012, .8, .02), loc=(s * 1.225, y, 1.75), bevel=0)
            dr.box((.012, .02, .8), loc=(s * 1.225, y + .4, 1.35), bevel=0)
            K.handle(a.part('Kit_steel', 'Steel'), (s * 1.23, y + .2, 1.6), (s * 1.23, y + .3, 1.6), (s, 0, 0), h=.025,
                     r=.01)
        K.mirror(a.part('Kit_steel', 'Steel'), (s * 1.1, NOSE + .15, 2.0), s, arm=.08, size=(.05, .02, .18))
        K.lamp(a, (s * .85, NOSE - .01, 1.3), (0, -1, 0), r=.08, guard=True)
        st = a.part('Steps', 'Steel')
        for y in (NOSE + .85, NOSE + 1.75):
            st.box((.08, .45, .03), loc=(s * 1.2, y, .75), bevel=0)
    K.grille(a, (0, NOSE - .01, 1.3), 1.1, .4, facing=(0, -1, 0), slats=5, frame_mat='Steel')
    bp = a.part('Bumper', 'Steel')
    K.chamfer_box(bp, (2.4, .14, .22), loc=(0, NOSE - .02, FZ - .3), c=.03)
    for s in (-1, 1):
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .5, NOSE - .08, FZ - .35), facing=(0, -1, 0), size=.08)
    rk = a.part('Racks', 'Steel')
    sq = [(-.02, -.02), (.02, -.02), (.02, .02), (-.02, .02)]
    k.sweep(rk, sq, [(-.9, NOSE + .7, 2.62), (-.9, NOSE + 2.1, 2.62), (.9, NOSE + 2.1, 2.62), (.9, NOSE + .7, 2.62),
                     (-.9, NOSE + .7, 2.62)])
    a.part('Stowage', 'Canvas').box((1.4, .9, .25), loc=(0, NOSE + 1.4, 2.75), bevel=0)
    for s in (-1, 1):
        K.whip_antenna(a.part('Antennas', 'Steel'), (s * .85, NOSE + 2.15, 2.62), h=1.2, r=.015)
    m = a.pivot('Mount_mg', (.5, NOSE + 1.0, 2.62))
    a.pivot('Muzzle_mg', (0, -.5, .2), m)


def _chassis(a):
    fr = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        fr.box((.18, 10.2, .32), loc=(s * .45, .2, FZ - .16), bevel=0)
    ax = a.part('Axles', 'Undercarriage')
    for y in AXLES:
        K.axle(ax, y, WR, TX - .1, r=.07)
        for s in (-1, 1):
            K.tread_wheel(a, (s * TX, y, WR), WR, .44, s, seg=12)
    wing = a.part('Mud_wings', 'Team')
    for y in AXLES[1:]:
        for s in (-1, 1):
            K.plate(wing, (.5, 1.45, .04), loc=(s * (TX + .03), y, WR * 2 + .12), chamfer=0)
    for s in (-1, 1):
        C.stowage_box(a, (.32, 1.2, .32), (s * 1.02, -.25, FZ - .55), mat='Team', latches=2)
    C.jerry_rack(a, (-1.1, 2.15, FZ - .55), count=2, axis='Y')
    K.tread_wheel(a, (1.02, 2.15, FZ - .2), .45, .3, 1, seg=10, tyre='Spare_wheel', rim='Spare_wheel_rim')
    K.exhaust(a, (1.1, NOSE + 2.4, FZ + .3), r=.07, length=.9, direction=(0, 0, 1))
    a.pivot('Point_exhaust', (1.1, NOSE + 2.4, FZ + 1.25))
    a.pivot('Point_fire', (0, .5, BAY_TOP))
    for s in (-1, 1):
        a.part('Tail_lamps', 'Lamp').box((.12, .02, .08), loc=(s * 1.0, TAIL - .02, FZ), bevel=0)
    jk = a.part('Outriggers', 'Steel')
    pads = a.part('Outrigger_pads', 'Steel')
    for s in (-1, 1):
        for y in (-2.55, TAIL - .4):
            K.outrigger(jk, pads, (s * .5, y, FZ - .05), s, reach=.6, drop=.35, w=.15)


def _bay(a):
    """The launcher bay: walls, floor, the clamshell cover opened up, the missiles on their beam (`Turret`)."""
    y0, y1 = NOSE + 2.4, TAIL - .25
    bay = a.part('Hull', 'Team')
    for s in (-1, 1):
        xa, xb = sorted((s * 1.0, s * 1.2))
        xc, xd = sorted((s * 1.0, s * 1.1))
        C.slab_loft(bay, [(xa, y0), (xb, y0), (xb, y1), (xa, y1)], [(xc, y0 + .05), (xd, y0 + .05), (xd, y1 - .05),
                                                                    (xc, y1 - .05)], BAY_Z - .2, BAY_TOP)
    k.block(bay, (2.4, .2, .33), loc=(0, y1 - .1, BAY_Z - .035), chamfer=.02)      # a low sill under the boom
    k.block(bay, (2.4, .25, BAY_TOP - BAY_Z + .45), loc=(0, y0 + .12, BAY_Z - .2 + (BAY_TOP - BAY_Z + .45) / 2),
            chamfer=.02)
    a.part('Floor', 'Undercarriage').box((2.0, y1 - y0, .05), loc=(0, (y0 + y1) / 2, BAY_Z), bevel=0)
    # The cover: two ribbed halves swung open about the sills and hanging down along the bay's sides.
    cov = a.part('Cover', 'Team')
    ribs = a.part('Cover_ribs', 'Steel')
    pw = 1.0                           # each half's width (its height as it hangs)
    for s in (-1, 1):
        hx = s * 1.22
        cz = BAY_TOP - pw / 2 + .04
        K.plate(cov, (.04, y1 - y0 - .3, pw), loc=(hx + s * .02, (y0 + y1) / 2, cz), rot=(0, s * .06, 0),
                chamfer=.01)
        for j in range(7):
            yy = y0 + .4 + j * (y1 - y0 - .8) / 6
            ribs.box((.03, .06, pw * .95), loc=(hx + s * .055, yy, cz), rot=(0, s * .06, 0), bevel=0)
        a.part('Cover_hinges', 'Steel').cyl(.05, y1 - y0 - .4, loc=(hx, (y0 + y1) / 2, BAY_TOP + .02), rot=K.FORWARD,
                                            seg=6, bevel=0)
        a.part('Team_band', 'Team').box((.02, 3.0, .15), loc=(hx + s * .05, (y0 + y1) / 2, cz - .25),
                                        rot=(0, s * .06, 0), bevel=0)
        for yy in (y0 + 1.0, y1 - 1.0):
            a.part('Cover_rams', 'Steel').limb((s * 1.0, yy, BAY_TOP - .1), (s * 1.24, yy, BAY_TOP - .5), .03, .035,
                                               bevel=0)
    _erector(a)


ERECTOR = '^(erector|missile_)'     # ModelLibrary.ErectorParts["ballistic_launcher"]: what rides the Elevation pivot


def _erector(a):
    """Play-test 13 (lane B): the erector and both 9M723 missiles drawn lying on it (travel pose, `Turret`).

    Everything that rises is named Erector_* / Missile_* (or Muzzle_main), so ModelLibrary puts all of it on the
    runtime `Elevation` pivot: the boom's rails and cross members, the spine, the saddles and clamps, the ram body,
    the missiles with their fins, nozzles, seekers and bands, the hinge shaft. The pivot lands 6 % in from the
    group's rear end and 30 % up it (C.elevation_pivot); the hinge shaft and its brackets on the bay floor are built
    exactly there, so the boom turns about its own rear hinge and the missiles ride up with it (VehicleView
    Erectors: raised 86 degrees from this flat pose)."""
    t = a.pivot('Turret', (0, 1.0, BAY_Z + .2))
    floor = (BAY_Z + .025) - (BAY_Z + .2)       # the bay floor's top in the Turret's coordinates
    R, L = .36, 6.0
    tail = 3.6                                  # the missiles' base (their nozzles reach back over the hinge)
    y_front, y_rear = tail - 5.45, tail + .5    # the boom rails
    rail_h, axis_z = .24, .24 + .1 + R
    # The boom: two box rails, cross members, the spine between the missiles, the erecting ram's body under it.
    boom = a.part('Erector_beam', 'Armor', t)
    for s in (-1, 1):
        k.block(boom, (.14, y_rear - y_front, rail_h), loc=(s * .62, (y_front + y_rear) / 2, rail_h / 2), chamfer=.02)
    for y in (y_front + .3, -.2, 1.2, 2.5, y_rear - .25):
        boom.box((1.1, .12, .14), loc=(0, y, .12), bevel=0)
    k.block(a.part('Erector_arm', 'Armor', t), (.12, 4.8, .15), loc=(0, 1.0, rail_h + .075), chamfer=.02)
    ram = a.part('Erector_ram', 'Steel', t)
    ram.cyl(.075, 2.4, loc=(0, 2.0, .11), rot=K.FORWARD, seg=10, bevel=0)
    ram.cyl(.04, 1.1, loc=(0, .3, .11), rot=K.FORWARD, seg=8, bevel=0)
    ram.box((.2, .14, .2), loc=(0, 3.25, .11), bevel=0)
    # The saddles under each missile, the clamp bands over them.
    sad = a.part('Erector_saddles', 'Steel', t)
    clamps = a.part('Erector_clamps', 'Steel', t)
    for x in (-.42, .42):
        for f in (.15, .5, .85):
            yy = tail - L * f
            if yy < y_front + .1:
                continue
            k.extrude(sad, [(x - .3, rail_h), (x + .3, rail_h), (x + .3, axis_z - R * .55), (x + .18, axis_z - R - .005),
                            (x - .18, axis_z - R - .005), (x - .3, axis_z - R * .55)], .16, loc=(0, yy, 0), axis='Y')
        for f in (.3, .7):
            clamps.cyl(R + .018, .07, loc=(x, tail - L * f, axis_z), rot=K.FORWARD, seg=8, bevel=0)
    # The two 9M723 missiles side by side, noses forward: ogive, body, the tail skirt with four small fins, nozzle.
    for x in (-.42, .42):
        base = (x, tail, axis_z)
        k.lathe(a.part('Missile_bodies', 'Fuel', t), [(R * .9, 0), (R, .12), (R, L * .7), (R * .88, L * .82),
                                                      (R * .55, L * .93), (R * .12, L * .995), (0, L)],
                loc=base, rot=(R90, 0, 0), seg=12, worn=(2, 4))
        a.part('Missile_seekers', 'Glass', t).cyl(R * .3, .02, loc=(x, tail - L * .9, axis_z + R * .5),
                                                  rot=(R90 - .55, 0, 0), seg=8, bevel=0)
        a.part('Missile_bands', 'Hazard', t).cyl(R + .008, .09, loc=(x, tail - L * .56, axis_z), rot=K.FORWARD,
                                                 seg=10, bevel=0)
        fins = a.part('Missile_fins', 'Steel', t)
        for j in range(4):
            u = j * R90 + math.pi / 4
            rr = R + .13
            fins.box((.025, .55, .26), loc=(x + math.cos(u) * rr, tail - .4, axis_z + math.sin(u) * rr),
                     rot=(0, R90 - u, 0), bevel=0)
        k.lathe(a.part('Missile_nozzles', 'Undercarriage', t), [(R * .55, 0), (R * .72, .14), (R * .5, .22)],
                loc=(x, tail + .01, axis_z), rot=(-R90, 0, 0), seg=10)
    a.pivot('Muzzle_main', (.42, tail - L - .03, axis_z), t)
    # The hinge: where the runtime turns the group, a shaft through lugs on the rails, brackets on the bay floor.
    hx, hy, hz = C.elevation_pivot(a, 'Turret', ERECTOR)
    lug = a.part('Erector_lugs', 'Armor', t)
    for s in (-1, 1):
        lh = hz + .13 - (rail_h - .04)
        k.block(lug, (.07, .36, lh), loc=(s * .62, hy, rail_h - .04 + lh / 2), chamfer=.02)
    a.part('Erector_hinge', 'Steel', t).cyl(.07, 1.56, loc=(hx, hy, hz), rot=(0, R90, 0), seg=10, bevel=0)
    br = a.part('Bay_hinge_brackets', 'Armor', t)
    for s in (-1, 1):
        k.extrude(br, [(hy - .3, floor), (hy + .3, floor), (hy + .14, hz + .1), (hy - .14, hz + .1)], .05,
                  loc=(s * .745, 0, 0), axis='X')
    # The boom's rests on the bay floor (it lies on them for travel), the ram's foot.
    rests = a.part('Bay_rests', 'Steel', t)
    for y in (y_front + .5, 1.6):
        for s in (-1, 1):
            rests.box((.22, .3, -.012 - floor), loc=(s * .62, y, (floor - .012) / 2), bevel=0)
    a.part('Bay_ram_foot', 'Steel', t).box((.3, .3, -.03 - floor), loc=(0, 3.25, (floor - .03) / 2), bevel=0)


def ballistic_launcher(a, detail=False):
    """The Iskander-M 9P78-1: see the module docstring."""
    _cab(a)
    _chassis(a)
    _bay(a)
    K.dust(a, (0, 0, .3), radius=4.8, k=.14)
    k.clean(a)


BUILDERS = {
    'ballistic_launcher': (ballistic_launcher, dict(ao_distance=.45, grime_height=.5)),
}
