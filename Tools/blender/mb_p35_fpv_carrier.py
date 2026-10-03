"""Play-test 13 (lane B): the FPV drone carrier redrawn (the owner: the old tall MRAP capsule with a row of
windows looked like a bus). Spec: Tools/blender/specs/fpv_carrier.json.

What an FPV strike team's vehicle really is (Ukraine war practice; Typhoon-U / KrAZ / Ural-class protected trucks
carrying a drone station): a bonneted 6x6 protected truck, the def's modelSize 7.41 x 2.04 x 2.88 m. The long
armoured bonnet with its louvred grille, heavy bumper and wings; the short armoured crew cab (the operators ride
and fly from it) with a raked two-pane windscreen, small thick door windows, steps, mirrors, the roof EW jammer with
its rod antennas (drone defence) and the M2 on a ring over the roof (the def's free `hmg_selfdef_18`); behind it
an open steel flatbed with drop sides and a tall headboard, carrying the generator, cased spare drones, the cable
reel and the telescopic relay mast with its two flat panel antennas (the control / video link) at the front, and
at the rear the drone launch station on a turntable (`Turret`): a box module on a pedestal above the drop sides,
its clamshell lids opened fore and aft, four armed quadcopters (RPG-type warheads slung under them) ready on their
pads, charging drawers in its sides, two whips. The front axle and the rear tandem with lugged tyres on leaf
springs, the fuel tank, the spare wheel, a toolbox, mud flaps, tail lamps.

Its own body: nothing taken from the Lancet truck (a cab-over Typhoon-K with a catapult rail). Runtime nodes kept:
`Turret`, `Muzzle_main` (above the pads), `Mount_mg` / `Muzzle_mg`, `Point_exhaust`, `Point_fire` (the wrapper adds
`Part_wheel` / `Part_wheelb`). No Turret part is named like a barrel (ModelLibrary.BarrelPattern), so the station
gets no elevating pivot and never tilts. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P
import mb_p35c_parts as C

R90 = math.pi / 2
WR, WW, TRACK = .52, .38, .78
AX = (-2.6, 1.3, 2.55)
HALF = .97
FZ = 1.0                         # the frame's top
CAB_Y0, CAB_Y1 = -1.98, -.55
ROOF = 2.42
DECK = 1.28                      # the flatbed's top
BED_Y0, BED_Y1 = -.35, 3.66
TY = 2.2                         # the launch station's turntable


def _whip(part, loc, h):
    """A lean whip antenna: its base and the rod (a few triangles; kit whips are ten times that)."""
    x, y, z = loc
    part.cyl(.03, .05, loc=(x, y, z + .025), seg=6, bevel=0)
    part.cyl(.008, h, loc=(x, y, z + .05 + h / 2), seg=4, r2=.005, bevel=0)


def _front(a):
    """The armoured bonnet, grille, bumper, wings and lamps."""
    hood = a.part('Body', 'Team')
    C.section_loft(hood, [(-3.6, [(0, .95), (.8, .95), (.8, 1.36), (.68, 1.47), (0, 1.49)]),
                          (-3.3, [(0, .92), (.84, .92), (.84, 1.48), (.72, 1.59), (0, 1.61)]),
                          (-2.0, [(0, .92), (.86, .92), (.86, 1.56), (.74, 1.68), (0, 1.7)])])
    K.grille(a, (0, -3.61, 1.16), 1.05, .32, facing=(0, -1, 0), slats=5, frame_mat='Armor')
    vents = a.part('Hood_vents', 'Undercarriage')
    for s in (-1, 1):
        for i in range(4):
            vents.box((.012, .3, .03), loc=(s * .853, -2.95 + i * .2, 1.3), bevel=0)
    bump = a.part('Bumper', 'Armor')
    K.chamfer_box(bump, (1.96, .22, .3), loc=(0, -3.6, .88), c=.03)
    for s in (-1, 1):
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .55, -3.72, .82), facing=(0, -1, 0), size=.08)
        # Wings over the front wheels, their front skirts, the lamps in guards on them.
        K.plate(a.part('Fenders', 'Armor'), (.4, 1.3, .04), loc=(s * TRACK, AX[0] - .05, WR * 2 + .12), chamfer=0)
        a.part('Fenders', 'Armor').box((.37, .04, .22), loc=(s * TRACK, AX[0] - .7, WR * 2 + .02), bevel=0)
        K.lamp(a, (s * .78, -3.28, 1.22), (0, -1, 0), r=.07, mat='Armor', guard=False)
    a.pivot('Point_fire', (0, -2.7, 1.5))


def _cab(a):
    """The short armoured crew cab: raked windscreen, small door windows, doors, steps, mirrors, roof kit."""
    cab = a.part('Cab', 'Team')
    low = [(0, .95), (.97, .95), (.97, 1.7), (.9, 1.78), (0, 1.79)]
    full = [(0, .95), (.97, .95), (.97, 1.75), (.86, ROOF - .02), (0, ROOF)]
    C.section_loft(cab, [(CAB_Y0, low), (CAB_Y0 + .48, full), (CAB_Y1, full)])

    def fy(z):           # the raked windscreen face, a centimetre proud of it
        return CAB_Y0 + .48 * (z - 1.79) / (ROOF - 1.79) - .01
    for s in (-1, 1):
        x0, x1 = s * .05, s * .76
        z0, z1 = 1.86, ROOF - .1
        c = [(x0, fy(z0), z0), (x1, fy(z0), z0), (x1 * .97, fy(z1), z1), (x0, fy(z1), z1)]
        if s < 0:
            c = [c[1], c[0], c[3], c[2]]
        K.windscreen(a, c, frame_mat='Undercarriage', wipers=1, bar=.05)
    glass = a.part('Glass', 'Glass')
    seams = a.part('Cab_seams', 'Undercarriage')
    fit = a.part('Kit_latches', 'Steel')
    lean = math.atan2(.11, ROOF - .02 - 1.75)
    xw = .97 - .11 * (2.02 - 1.75) / (ROOF - .02 - 1.75) + .008
    for s in (-1, 1):
        for y in (-1.45, -.9):
            # Small thick door windows on the leaning upper sides, the door seams, handles, hinges.
            glass.box((.012, .36, .28), loc=(s * xw, y, 2.02), rot=(0, -s * lean, 0), bevel=0)
            seams.box((.01, .015, .8), loc=(s * (HALF + .006), y + .27, 1.33), bevel=0)
            fit.box((.02, .1, .03), loc=(s * (HALF + .012), y + .18, 1.5), bevel=0)
        seams.box((.01, 1.12, .015), loc=(s * (HALF + .006), -1.17, .99), bevel=0)
        P.step(a, (s * (HALF - .12), -1.45, .62), w=.36)
        P.step(a, (s * (HALF - .12), -.9, .62), w=.36)
        K.mirror(fit, (s * (HALF + .02), CAB_Y0 + .15, 1.95), s, arm=.05, size=(.035, .1, .26))
        a.part('Team_band', 'Team').box((.012, 1.3, .08), loc=(s * (HALF + .006), -1.25, 1.62), bevel=0)
    # The rear wall's window, the M2 on its ring over the roof hatch (free secondary).
    glass.box((.6, .012, .2), loc=(0, CAB_Y1 + .007, 2.1), bevel=0)
    k.ring(a.part('Gun_ring', 'Armor'), [(.36, 0), (.43, 0), (.43, .1), (.38, .13)], loc=(.3, -1.0, ROOF - .01),
           seg=12, worn=(2,))
    K.pintle_mg(a, None, (.3, -1.0, ROOF + .08), post=.05, length=1.0)
    # The EW jammer on the roof: its box and the fan of rod antennas (drone defence); two whips.
    K.chamfer_box(a.part('EW_jammer', 'Armor'), (.42, .3, .14), loc=(-.48, -.85, ROOF + .07), c=.02)
    rods = a.part('EW_rods', 'Steel')
    for i in range(6):
        u = i * math.tau / 6
        rods.limb((-.48 + .1 * math.cos(u), -.85 + .08 * math.sin(u), ROOF + .13),
                  (-.48 + .15 * math.cos(u), -.85 + .15 * math.sin(u), ROOF + .46), .02, .02, bevel=0)
    for s in (-1, 1):
        _whip(a.part('Antennas', 'Steel'), (s * .8, CAB_Y1 - .1, ROOF - .03), .42)
    K.exhaust(a, (-.86, -.44, 1.2), r=.05, length=1.0, direction=(0, 0, 1), muffler=False, cap=True)
    a.pivot('Point_exhaust', (-.86, -.44, 2.25))


def _chassis(a):
    fr = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        fr.box((.14, 7.0, .22), loc=(s * .45, 0, FZ - .11), bevel=0)
    ax = a.part('Axles', 'Undercarriage')
    springs = a.part('Suspension', 'Steel')
    for y in AX:
        K.axle(ax, y, WR, TRACK - .12, r=.075, diff=y > 0)
        for s in (-1, 1):
            K.tread_wheel(a, (s * TRACK, y, WR), WR, WW, s, seg=12)
            springs.box((.07, .9, .05), loc=(s * .45, y, WR + .16), bevel=0)          # the leaf pack
            springs.box((.09, .12, .1), loc=(s * .45, y, WR + .12), bevel=0)          # its axle clamp
            K.dust(a, (s * TRACK, y, .15), radius=1.0, k=.26)
    # Under the bed: the fuel tank (left), the spare wheel and a toolbox (right), mud flaps, rear fenders.
    P.fuel_tank(a, (.78, .2, .72), .85, .2)
    K.tread_wheel(a, (-.84, .2, .64), .42, .24, -1, seg=10, tyre='Spare_wheel', rim='Spare_wheel_rim')
    P.toolbox(a, (-.78, -.5, .66), (.3, .36, .3))
    for s in (-1, 1):
        K.plate(a.part('Fenders', 'Armor'), (.42, 2.45, .04), loc=(s * TRACK, (AX[1] + AX[2]) / 2, WR * 2 + .1),
                chamfer=0)
        P.mudflap(a, (s * TRACK, AX[2] + .6, WR * 2 + .06), w=.4, h=.42)


def _bed(a):
    """The steel flatbed: deck, drop sides with stakes, headboard, tailgate; the gear at its front."""
    yc, yl = (BED_Y0 + BED_Y1) / 2, BED_Y1 - BED_Y0
    sills = a.part('Bed_frame', 'Undercarriage')
    for s in (-1, 1):
        sills.box((.12, yl - .1, .19), loc=(s * .45, yc, FZ + .095), bevel=0)
    for y in (BED_Y0 + .3, 1.0, 2.3, BED_Y1 - .25):
        sills.box((1.9, .1, .1), loc=(0, y, DECK - .13), bevel=0)
    a.part('Bed', 'Steel').box((1.96, yl, .08), loc=(0, yc, DECK - .04), bevel=0)
    side = a.part('Bed_sides', 'Team')
    stakes = a.part('Bed_stakes', 'Steel')
    for s in (-1, 1):
        K.plate(side, (.04, yl - .1, .38), loc=(s * (HALF - .01), yc + .02, DECK + .19), chamfer=0)
        for y in (BED_Y0 + .5, .9, 1.9, 2.9):
            stakes.box((.025, .07, .36), loc=(s * (HALF + .02), y, DECK + .19), bevel=0)
        a.part('Team_band', 'Team').box((.012, 1.0, .07), loc=(s * (HALF + .012), .3, DECK + .29), bevel=0)
    # The headboard with its guard bars, the tailgate with its hinges, the tail lamps and a ladder under it.
    K.plate(side, (1.93, .06, .72), loc=(0, BED_Y0 + .05, DECK + .36), chamfer=0)
    for x in (-.6, -.2, .2, .6):
        stakes.box((.04, .03, .66), loc=(x, BED_Y0 + .1, DECK + .37), bevel=0)
    K.plate(side, (1.94, .04, .38), loc=(0, BED_Y1, DECK + .19), chamfer=0)
    for x in (-.7, 0, .7):
        stakes.box((.2, .03, .04), loc=(x, BED_Y1 + .035, DECK + .01), bevel=0)
    for s in (-1, 1):
        a.part('Tail_lamps', 'Undercarriage').box((.18, .05, .1), loc=(s * .72, BED_Y1 + .01, DECK - .18), bevel=0)
        a.part('Tail_lenses', 'LavaGlow').box((.14, .01, .07), loc=(s * .72, BED_Y1 + .04, DECK - .18), bevel=0)
    K.ladder(a.part('Ladders', 'Steel'), (0, BED_Y1 + .03, .62), (0, BED_Y1 + .03, DECK - .12), width=.36, step=.2)
    # The generator (right front) with its louvres; cased spare drones; the mast's cable reel.
    K.chamfer_box(a.part('Generator', 'Armor'), (.62, .55, .5), loc=(-.55, .15, DECK + .26), c=.03)
    lv = a.part('Generator_vents', 'Undercarriage')
    for i in range(4):
        lv.box((.012, .4, .03), loc=(-.866, .15, DECK + .14 + i * .08), bevel=0)
    crates = a.part('Stowage', 'Crate')
    straps = a.part('Kit_straps', 'Steel')
    for (w, d, h), (x, y, z) in (((.55, .4, .26), (.18, .5, DECK + .01)), ((.48, .36, .22), (.18, .5, DECK + .28)),
                                 ((.5, .38, .26), (-.3, .75, DECK + .01)), ((.36, .5, .3), (.66, .62, DECK + .01))):
        # Hard drone cases: the shell, its lid seam and two latches.
        k.block(crates, (w, d, h), loc=(x, y, z + h / 2), chamfer=.02)
        straps.box((w + .012, d + .012, .015), loc=(x, y, z + h * .75), bevel=0)


def _mast(a):
    """The telescopic relay mast at the bed's front left (lowered for the road), its two flat panel antennas."""
    x, y = .66, -.08
    m = a.part('Mast', 'Steel')
    k.block(a.part('Mast_base', 'Armor'), (.24, .24, .12), loc=(x, y, DECK + .06), chamfer=.02)
    for r, z0, z1 in ((.065, DECK + .12, 2.05), (.05, 2.05, 2.5), (.036, 2.5, 2.68)):
        m.cyl(r, z1 - z0, loc=(x, y, (z0 + z1) / 2), seg=8, bevel=0)
    m.cyl(.078, .05, loc=(x, y, 2.05), seg=8, bevel=0)                 # the section collars
    m.cyl(.062, .05, loc=(x, y, 2.5), seg=8, bevel=0)
    m.box((.5, .04, .04), loc=(x, y, 2.66), bevel=0)                    # the crossbar
    pan = a.part('Mast_panels', 'Armor')
    face = a.part('Mast_panel_faces', 'Undercarriage')
    for s in (-1, 1):
        ang = s * .45
        cx, cy = x + s * .2, y - .03
        pan.box((.24, .04, .3), loc=(cx, cy, 2.7), rot=(0, 0, ang), bevel=0)
        face.box((.2, .01, .26), loc=(cx + math.sin(ang) * .025, cy - math.cos(ang) * .025, 2.7), rot=(0, 0, ang),
                 bevel=0)
    m.cyl(.012, .16, loc=(x, y, 2.76), seg=6, bevel=0)                 # the omni stub on top
    m.limb((x, y, 2.0), (x - .15, BED_Y0 + .09, DECK + .7), .025, .025, bevel=0)     # its brace to the headboard


def _station(a):
    """The drone launch station on its turntable (`Turret`): pedestal, module, lids opened fore and aft, drones."""
    k.ring(a.part('Turret_ring', 'Steel'), [(.5, 0), (.62, 0), (.62, .08), (.5, .08)], loc=(0, TY, DECK), seg=10)
    t = a.pivot('Turret', (0, TY, DECK + .08))
    k.lathe(a.part('Station_pedestal', 'Armor', t), [(.55, 0), (.55, .05), (.38, .1), (.38, .37), (0, .37)], seg=12,
            worn=(1,))
    W, L, z0, z1 = 1.5, 1.6, .37, .85                  # the module: width, length, bottom, top
    k.extrude(a.part('Station_module', 'Team', t),
              [(-W / 2, z0), (W / 2, z0), (W / 2, z1 - .06), (W / 2 - .06, z1), (-W / 2 + .06, z1), (-W / 2, z1 - .06)],
              L, axis='Y', chamfer=.02)
    # The launch deck inset in the top, the four pads with their marks.
    a.part('Station_deck', 'Undercarriage', t).box((W - .18, L - .3, .02), loc=(0, 0, z1 + .005), bevel=0)
    pads = a.part('Station_pads', 'Hazard', t)
    spots = [(-.35, -.36), (.35, -.36), (-.35, .36), (.35, .36)]
    for px, py in spots:
        pads.box((.5, .5, .012), loc=(px, py, z1 + .021), bevel=0)
    # Charging drawers along each side, louvres, handles, a Team band; the rear control panel.
    dr = a.part('Station_drawers', 'Undercarriage', t)
    hd = a.part('Station_fit', 'Steel', t)
    for s in (-1, 1):
        for i in range(3):
            y = (i - 1) * .5
            dr.box((.012, .44, .18), loc=(s * (W / 2 + .006), y, z0 + .14), bevel=0)
            hd.box((.03, .14, .025), loc=(s * (W / 2 + .02), y, z0 + .14), bevel=0)
        for i in range(4):
            dr.box((.012, .3, .025), loc=(s * (W / 2 + .006), -.35, z0 + .29 + i * .04), bevel=0)
        a.part('Station_band', 'Team', t).box((.012, .5, .06), loc=(s * (W / 2 + .01), .45, z0 + .36), bevel=0)
    K.chamfer_box(a.part('Station_panel', 'Armor', t), (.5, .1, .26), loc=(0, L / 2 + .06, z0 + .2), c=.015)
    a.part('Station_panel_lit', 'Glass', t).box((.3, .01, .1), loc=(0, L / 2 + .115, z0 + .22), bevel=0)
    # The clamshell lids, hinged across the top's front and rear edges and swung open 130 degrees, up and out.
    lid = a.part('Station_lids', 'Team', t)
    ribs = a.part('Station_lid_ribs', 'Steel', t)
    op = math.radians(130)
    lw = L / 2 - .02
    for e in (-1, 1):                                   # e = -1 the front lid, +1 the rear lid
        hy, hz = e * L / 2, z1 + .03
        d = (-e * math.cos(op), math.sin(op))           # (y, z): from the hinge to the lid's free edge
        n = (-e * d[1], e * d[0])                       # the lid's inner face (towards the pads)
        tilt = e * (math.pi - op)
        my, mz = hy + d[0] * lw / 2, hz + d[1] * lw / 2
        lid.box((W - .04, lw, .03), loc=(0, my, mz), rot=(tilt, 0, 0), bevel=0)
        for x in (-.45, 0, .45):
            ribs.box((.04, lw * .9, .035), loc=(x, my + n[0] * .03, mz + n[1] * .03), rot=(tilt, 0, 0), bevel=0)
        hd.cyl(.025, W - .1, loc=(0, hy, z1 + .02), rot=(0, R90, 0), seg=6, bevel=0)
    # Four armed quadcopters on their pads: body, X arms, motors and props, the slung warhead with its fuze nose.
    dbody = a.part('Drones', 'Undercarriage', t)
    props = a.part('Drone_props', 'Steel', t)
    war = a.part('Drone_warheads', 'Fuel', t)
    for px, py in spots:
        z = z1 + .13
        dbody.box((.1, .17, .05), loc=(px, py, z), bevel=0)
        for ang in (math.pi / 4, -math.pi / 4):
            dbody.box((.34, .025, .02), loc=(px, py, z + .01), rot=(0, 0, ang), bevel=0)
        for ox, oy in ((-.12, -.12), (.12, -.12), (-.12, .12), (.12, .12)):
            props.cyl(.085, .006, loc=(px + ox, py + oy, z + .035), seg=6, bevel=0)
        war.cyl(.035, .26, loc=(px, py - .05, z - .06), rot=K.FORWARD, seg=6, r2=.02, bevel=0)
    a.pivot('Muzzle_main', (0, 0, z1 + .35), t)
    for s in (-1, 1):
        _whip(a.part('Station_whips', 'Steel', t), (s * (W / 2 - .08), L / 2 - .08, z1 + .01), .32)


def fpv_carrier(a, detail=False):
    """The FPV drone carrier: see the module docstring."""
    _front(a)
    _cab(a)
    _chassis(a)
    _bed(a)
    _mast(a)
    _station(a)
    K.dust(a, (0, 0, .3), radius=3.6, k=.15)
    k.clean(a)


BUILDERS = {
    'fpv_carrier': (fpv_carrier, dict(ao_distance=.5, grime_height=.6)),
}
