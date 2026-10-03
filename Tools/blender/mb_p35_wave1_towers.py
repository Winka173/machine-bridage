"""Prompt 35 wave 1 (lane A): three base structures rebuilt from scratch, each from its own spec
(Tools/blender/specs/<id>.json) on the kit35 library. DECISIONS "Prompt 35 wave 1 (lane A)".

- repair_bay (the repair_bay def): an Accord field workshop, 14.5 x 10 x 8.7 m. A cast slab with ramps, an open
  steel-framed shed under a corrugated gable roof (half-height side walls, a full back wall), and in front of it a
  gantry crane on rails lifting an engine pack out of the work area; an inspection pit, workbench, tool chests,
  compressor, gas bottles, a tyre stack, drums and sandbag corners.
- radar_site (the radar_station def): a Hegemon prefabricated radar post, 8.1 x 7.9 x 7.9 m. A cast concrete pad,
  a tapering lattice tower with a ladder and a railed platform, the big parabolic dish on its `Radar` pivot (the
  runtime spins it), an equipment container with its air conditioner and cable tray, a generator skid with its
  stack, jersey barriers and a chain-link fence.
- ammo_dump (the ammo_depot def): an Accord semi-sunken ammunition store, 4.9 x 6.1 x 2.9 m. An earth berm round a
  timber-faced bunker with a steel door and a sandbagged corrugated roof, ammunition crates on pallets and shell
  cases outside under a camouflage net, a red ammunition flag (no insignia), a hazard board, an extinguisher stand.

Runtime nodes kept: `Point_fire` (repair_bay, radar_site), `Radar` (radar_site). Every structure is drawn for both
sides; a structure's materials and colours stay the kit's (Team bands). Built only from frontier_kit / mb_kit27
primitives and mb_kit35; no other model's builder or mesh. Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau


# ============================================================================= repair_bay
BAY_X, BAY_Y = 5.0, 7.25          # half extents of the footprint
SLAB = .3
SHED_Y = (-2.6, 6.3)              # shed front .. back wall
EAVE, RIDGE = 4.6, 6.3


def _bay_slab(a):
    base = a.part('Base', 'Concrete')
    k.block(base, (10.0, 13.4, SLAB), loc=(0, .3, SLAB / 2), chamfer=.05, taper=(.96, .97))
    # Round 2: expansion joints and the painted bay lines on the slab.
    joints = a.part('Slab_joints', 'Undercarriage')
    for y in (-3.0, 1.0, 5.0):
        joints.box((9.4, .05, .01), loc=(0, y, SLAB + .003), bevel=0)
    joints.box((.05, 12.8, .01), loc=(0, .3, SLAB + .003), bevel=0)
    lines = a.part('Bay_lines', 'Hazard')
    for s in (-1, 1):
        lines.box((.1, 5.2, .012), loc=(s * 2.1, -4.3, SLAB + .004), bevel=0)
    # The ramps at the front (vehicles drive in) and the back door.
    k.extrude(base, [(-BAY_Y, 0), (-6.4, 0), (-6.4, SLAB)], 7.0, loc=(0, 0, 0), axis='X', chamfer=.03)
    k.extrude(base, [(6.95, 0), (7.25, 0), (6.95, SLAB)], 3.4, loc=(-2.2, 0, 0), axis='X', chamfer=.02)
    # The inspection pit in the work area: a dark well with its hazard kerb.
    a.part('Pit', 'Undercarriage').box((1.2, 4.2, .04), loc=(0, -4.2, SLAB + .005), bevel=0)
    kerb = a.part('Pit_kerb', 'Hazard')
    for s in (-1, 1):
        kerb.box((.12, 4.4, .08), loc=(s * .66, -4.2, SLAB + .04), bevel=0)
        kerb.box((1.44, .12, .08), loc=(0, -4.2 + s * 2.16, SLAB + .04), bevel=0)
    # Crane rails along both sides of the front work area.
    rails = a.part('Crane_rails', 'Steel')
    for s in (-1, 1):
        rails.box((.12, 5.6, .08), loc=(s * 4.55, -4.2, SLAB + .04), bevel=0)
    K.dust(a, (0, -6.5, SLAB), radius=3.5, k=.25)
    K.dust(a, (0, 0, SLAB), radius=7.5, k=.12)


def _bay_shed(a):
    steel = a.part('Frame', 'Steel')
    y0, y1 = SHED_Y
    cols = [y0, y0 + (y1 - y0) / 3, y0 + 2 * (y1 - y0) / 3, y1]
    for s in (-1, 1):
        for y in cols:
            steel.box((.22, .22, EAVE), loc=(s * 4.55, y, SLAB + EAVE / 2), bevel=0)               # I-beam columns
            steel.box((.4, .4, .03), loc=(s * 4.55, y, SLAB + .015), bevel=0)                     # base plates
        steel.box((.18, y1 - y0, .25), loc=(s * 4.55, (y0 + y1) / 2, SLAB + EAVE - .1), bevel=0)    # eave beams
    # Rafters to the ridge on every column line, purlins along the slopes.
    half = 4.75
    pitch = math.atan2(RIDGE - EAVE, half)
    for y in cols:
        for s in (-1, 1):
            steel.limb((s * half, y, SLAB + EAVE), (0, y, SLAB + RIDGE), .14, .2, bevel=0)
    for f in (.3, .65):
        for s in (-1, 1):
            steel.box((.08, y1 - y0, .12), loc=(s * half * (1 - f), (y0 + y1) / 2,
                                                 SLAB + EAVE + (RIDGE - EAVE) * f + .05), rot=(0, s * pitch, 0),
                      bevel=0)
    # The corrugated roof: two sloped sheets with an overhang, the ridge cap, a Team band along the eaves.
    roof = a.part('Roof', 'Corrugated')
    slope = math.hypot(half + .35, RIDGE - EAVE + .26)
    for s in (-1, 1):
        k.block(roof, (slope, y1 - y0 + .7, .06), loc=(s * (half + .35) / 2, (y0 + y1) / 2,
                                                       SLAB + (EAVE - .26 + RIDGE) / 2 + .14), rot=(0, s * pitch, 0),
                chamfer=0)
    # Round 2: the sheets' overlap seams down each slope, two skylight panels a side, ridge ventilators.
    seams = a.part('Roof_seams', 'Steel')
    sky = a.part('Skylights', 'Glass')
    for s in (-1, 1):
        cx = s * (half + .35) / 2
        cz = SLAB + (EAVE - .26 + RIDGE) / 2 + .18
        for j in range(8):
            y = y0 - .3 + (j + .5) * (y1 - y0 + .6) / 8
            seams.box((slope - .1, .06, .03), loc=(cx, y, cz), rot=(0, s * pitch, 0), bevel=0)
        for y in (y0 + 2.0, y1 - 2.0):
            sky.box((1.3, 1.0, .02), loc=(cx, y, cz + .02), rot=(0, s * pitch, 0), bevel=0)
        # Round 3: the corrugation ribs down the slope, every 0.32 m (a triangular rib, 8 triangles each).
        ribs = a.part('Roof_ribs', 'Corrugated')
        n = int((y1 - y0 + .6) / .32)
        for j in range(n):
            y = y0 - .3 + (j + .5) * (y1 - y0 + .6) / n
            k.extrude(ribs, [(-.05, 0), (.05, 0), (0, .045)], slope - .15, loc=(cx, y, cz - .005),
                      rot=(0, s * pitch, 0), axis='X', chamfer=0)
    for y in (y0 + 2.8, y1 - 2.8):
        k.lathe(a.part('Ridge_vents', 'Steel'), [(.25, 0), (.25, .3), (.35, .34), (.3, .45), (0, .48)],
                loc=(0, y, SLAB + RIDGE + .18), seg=8, worn=(2,))
    k.extrude(a.part('Ridge', 'Steel'), [(-.25, 0), (.25, 0), (0, .16)], y1 - y0 + .7,
              loc=(0, (y0 + y1) / 2, SLAB + RIDGE + .15), axis='Y', chamfer=.01)
    team = a.part('Team_band', 'Team')
    for s in (-1, 1):
        team.box((.04, y1 - y0, .3), loc=(s * 4.68, (y0 + y1) / 2, SLAB + EAVE - .45), bevel=0)
    # The back wall (full, with its gable) and the half-height side walls of corrugated sheet.
    wall = a.part('Wall', 'Corrugated')
    k.extrude(wall, [(-4.6, 0), (4.6, 0), (4.6, EAVE), (0, RIDGE), (-4.6, EAVE)], .08,
              loc=(0, y1 + .12, SLAB), axis='Y', chamfer=0)
    for s in (-1, 1):
        k.block(wall, (.08, y1 - y0 - .3, 2.1), loc=(s * 4.7, (y0 + y1) / 2 + .1, SLAB + 1.05), chamfer=0)
    K.door(a, (-2.2, y1 + .17, SLAB), (1.4, 2.3), normal=(0, 1, 0), mat='Armor')
    sheet = a.part('Wall_seams', 'Steel')
    for z in (1.5, 3.0):
        sheet.box((9.2, .05, .05), loc=(0, y1 + .17, SLAB + z), bevel=0)
    a.part('Windows', 'Glass').box((1.6, .04, .7), loc=(1.4, y1 + .17, SLAB + 2.0), bevel=0)
    K.grille(a, (2.6, y1 + .17, SLAB + 3.6), 1.2, .8, facing=(0, 1, 0), slats=5)                  # extractor
    K.lamp(a, (0, y0 - .05, SLAB + EAVE - .4), (0, -1, -.4), r=.16, mat='Steel')
    K.whip_antenna(a.part('Antennas', 'Steel'), (1.6, y1 - .4, SLAB + RIDGE - .4), h=2.2, r=.03)


def _bay_crane(a):
    """The gantry crane over the work area: two A-frame legs on rail bogies, the box girder with its hazard band,
    the trolley and hoist, the hook on its chain carrying an engine pack."""
    y = -4.4
    top = SLAB + 7.9
    cr = a.part('Gantry', 'CraneYellow')
    st = a.part('Gantry_steel', 'Steel')
    for s in (-1, 1):
        x = s * 4.55
        if s > 0:
            K.ladder(a.part('Ladders', 'Steel'), (x + .18, y + .9, SLAB + .4), (x + .18, y + .3, top - .5),
                     width=.4, step=.35, r=.02)
        for dy in (-1.0, 1.0):
            cr.limb((x, y + dy, SLAB + .35), (x, y + dy * .2, top - .3), .2, .2, bevel=0)
        cr.box((.3, 2.4, .3), loc=(x, y, SLAB + .3), bevel=0)                                    # the bogie beam
        for dy in (-.9, .9):
            st.cyl(.15, .14, loc=(x, y + dy, SLAB + .17), rot=(0, R90, 0), seg=10, bevel=0)       # rail wheels
        cr.box((.25, .7, .25), loc=(x, y, SLAB + 2.6), bevel=0)                                  # leg tie
    k.block(cr, (9.6, .6, .7), loc=(0, y, top), chamfer=.04)
    a.part('Gantry_band', 'SafetyStripe').box((9.0, .62, .14), loc=(0, y, top - .2), bevel=0)
    K.railing(a.part('Railings', 'Steel'), [(-4.6, y - .32, top + .35), (4.6, y - .32, top + .35)], h=.8, post=1.5,
              r=.02)
    # Trolley, hoist drum, hook block and chain; the engine pack in its lifting frame.
    tx = 1.1
    k.block(a.part('Hoist', 'Armor'), (.9, .9, .55), loc=(tx, y, top - .62), chamfer=.04)
    k.lathe(st, [(.22, -.35), (.22, .35)], loc=(tx, y, top - .62), rot=(0, R90, 0), seg=10)
    chain = a.part('Hook_chain', 'Steel')
    chain.tube([(tx - .08, y, top - .9), (tx - .08, y, SLAB + 3.0)], .025, seg=4)
    chain.tube([(tx + .08, y, top - .9), (tx + .08, y, SLAB + 3.0)], .025, seg=4)
    k.block(a.part('Hook_block', 'Hazard'), (.3, .2, .4), loc=(tx, y, SLAB + 2.8), chamfer=.03)
    for dx in (-.55, .55):
        st.tube([(tx, y, SLAB + 2.6), (tx + dx, y - .4, SLAB + 1.95)], .015, seg=4)
        st.tube([(tx, y, SLAB + 2.6), (tx + dx, y + .4, SLAB + 1.95)], .015, seg=4)
    eng = a.part('Engine_pack', 'Armor')
    k.block(eng, (1.3, 1.0, .75), loc=(tx, y, SLAB + 1.55), chamfer=.06)
    k.block(eng, (.9, .7, .3), loc=(tx, y, SLAB + 2.05), chamfer=.04)
    K.grille(a, (tx, y - .52, SLAB + 1.55), .9, .45, facing=(0, -1, 0), slats=4)
    a.part('Hoses', 'Rubber').tube([(tx + .65, y + .1, SLAB + 1.7), (tx + .85, y + .3, SLAB + 1.2),
                                    (tx + .7, y + .5, SLAB + .9)], .04, seg=5)
    K.soot(a, (tx, y, SLAB + 1.2), radius=1.2, k=.25)


def _bay_floor(a):
    """The working kit: bench with its vice, tool chests, compressor, gas bottles on a cart, a tyre stack, drums,
    jerrycans, an extinguisher, the lift trolley, sandbag corners at the front (Accord), a floodlight."""
    st = a.part('Fit_steel', 'Steel')
    bench = a.part('Workbench', 'Wood')
    k.block(bench, (2.6, .8, .08), loc=(3.6, 2.0, SLAB + .9), chamfer=.01)
    for dx in (-1.2, 1.2):
        for dy in (-.32, .32):
            st.box((.06, .06, .9), loc=(3.6 + dx, 2.0 + dy, SLAB + .45), bevel=0)
    st.box((2.4, .7, .03), loc=(3.6, 2.0, SLAB + .25), bevel=0)
    k.block(a.part('Vice', 'Armor'), (.2, .3, .18), loc=(2.6, 1.75, SLAB + 1.03), chamfer=.02)
    chests = a.part('Tool_chests', 'BarrelRed')
    for i, (x, y, h) in enumerate(((3.9, 4.0, 1.1), (3.9, 4.75, .8))):
        k.block(chests, (.6, .7, h), loc=(x, y, SLAB + h / 2), chamfer=.03)
        for j in range(int(h / .22)):
            st.box((.02, .5, .02), loc=(x - .31, y, SLAB + .15 + j * .22), bevel=0)               # drawer pulls
    # Compressor: tank and motor on a skid, its hose.
    k.lathe(a.part('Compressor', 'Armor'), [(0, -.7), (.32, -.65), (.35, -.5), (.35, .5), (.32, .65), (0, .7)],
            loc=(-3.6, 4.6, SLAB + .5), rot=(R90, 0, 0), seg=12)
    k.block(a.part('Compressor', 'Armor'), (.5, .5, .4), loc=(-3.6, 4.5, SLAB + 1.05), chamfer=.03)
    st.box((.9, 1.6, .1), loc=(-3.6, 4.6, SLAB + .05), bevel=0)
    a.part('Hoses', 'Rubber').tube([(-3.3, 3.9, SLAB + .5), (-2.4, 3.0, SLAB + .03), (-1.0, 2.6, SLAB + .03)],
                                   .025, seg=4)
    # Gas bottles on their cart (oxygen and acetylene for the welder).
    for i, (mat, x) in enumerate((('Steel', -2.3), ('BarrelRed', -2.0))):
        k.lathe(a.part('Gas_bottles', mat), [(.11, 0), (.11, 1.1), (.08, 1.2), (.03, 1.25), (0, 1.27)],
                loc=(x, 5.6, SLAB + .1), seg=8, worn=(1,))
    st.box((.7, .4, .08), loc=(-2.15, 5.6, SLAB + .1), bevel=0)
    st.tube([(-2.5, 5.85, SLAB + .1), (-2.5, 5.85, SLAB + 1.0), (-1.8, 5.85, SLAB + 1.0), (-1.8, 5.85, SLAB + .1)],
            .015, seg=4)
    # A stack of road wheels / tyres, drums and jerrycans along the left wall.
    for j in range(2):
        k.lathe(a.part('Tyres', 'Rubber'), [(.35, 0), (.55, .02), (.58, .14), (.58, .26), (.55, .38), (.35, .4)],
                loc=(-3.7, 1.3, SLAB + j * .4), seg=12, caps=(False, False))
    K.fuel_drum(a.part('Fuel_drums', 'Fuel'), a.part('Drum_bands', 'Steel'), (-4.0, -1.2, SLAB), r=.3, h=.9)
    K.fuel_drum(a.part('Fuel_drums', 'Fuel'), a.part('Drum_bands', 'Steel'), (-3.4, -.9, SLAB + .3), r=.3, h=.9,
                lying=True)
    for i in range(2):
        K.jerrycan(a.part('Jerrycans', 'Fuel'), (-4.1 + i * .3, 2.6, SLAB), rot=(0, 0, R90))
    k.lathe(a.part('Extinguishers', 'BarrelRed'), [(.08, 0), (.08, .45), (.05, .52), (0, .55)],
            loc=(4.3, -1.8, SLAB), seg=8, worn=(1,))
    # The lift trolley (a trolley jack) by the pit, two axle stands.
    k.block(a.part('Trolley_jack', 'Hazard'), (.35, 1.1, .18), loc=(1.3, -2.3, SLAB + .15), chamfer=.02)
    st.tube([(1.3, -1.75, SLAB + .2), (1.3, -1.1, SLAB + .9)], .02, seg=4)
    for x in (-1.3, -1.7):
        k.lathe(st, [(.15, 0), (.04, .5), (.04, .7), (.08, .72)], loc=(x, -2.2, SLAB), seg=6)
    # Accord sandbag corners at the front, a floodlight on a pole, a sign board.
    for s in (-1, 1):
        K.sandbag_wall(a, [(s * 4.9, -6.2, SLAB), (s * 4.9, -7.0, SLAB), (s * 4.1, -7.0, SLAB)], layers=2,
                       bag=(.7, .36, .2), round_both=False)
    K.floodlight(a, (-4.75, -2.8, SLAB), facing=(.6, -1, -.5), pole=3.4)
    sign = a.part('Signs', 'PlasterWhite')
    k.block(sign, (1.4, .05, .7), loc=(3.6, -7.0, SLAB + 1.5), chamfer=0)
    a.part('Sign_marks', 'SafetyStripe').box((1.3, .06, .12), loc=(3.6, -7.0, SLAB + 1.3), bevel=0)
    for dx in (-.6, .6):
        a.part('Sign_posts', 'Wood').box((.07, .07, 1.5), loc=(3.6 + dx, -6.98, SLAB + .75), bevel=0)
    a.pivot('Point_fire', (2.6, 3.3, 2.1))


def repair_bay(a):
    """The repair bay: see the module docstring."""
    _bay_slab(a)
    _bay_shed(a)
    _bay_crane(a)
    _bay_floor(a)
    k.clean(a)


# ============================================================================= radar_site
PAD = .3


def _radar_pad(a):
    base = a.part('Base', 'Concrete')
    k.block(base, (7.4, 7.9, PAD), loc=(-.15, 0, PAD / 2), chamfer=.05, taper=(.94, .95))
    k.inset(base, lambda c, n, f: n.z > .9 and c.z > PAD - .02, width=.25, depth=-.02)
    # Round 2: the generator's annex slab (cast later, a step lower) breaks the square; a drain channel.
    k.block(base, (1.9, 3.0, PAD * .7), loc=(3.0, -2.2, PAD * .35), chamfer=.04, taper=(.92, .95))
    a.part('Drain', 'Undercarriage').box((.18, 7.4, .02), loc=(-3.5, 0, PAD + .005), bevel=0)
    ties = a.part('Base_ties', 'Steel')
    for s in (-1, 1):
        for f in (-.3, 0, .3):
            ties.cyl(.03, .03, loc=(f * 7.7, s * 3.96, PAD * .5), rot=K.FORWARD, seg=6, bevel=0)
            ties.cyl(.03, .03, loc=(s * 3.86, f * 7.9, PAD * .5), rot=(0, R90, 0), seg=6, bevel=0)
    # Hegemon cast jersey barriers along the front, a chain-link fence down the left side and the back.
    bar = a.part('Barriers', 'Concrete')
    for i in range(3):
        x = -2.2 + i * 2.0
        k.extrude(bar, [(-.3, 0), (.3, 0), (.15, .3), (.1, .8), (-.1, .8), (-.15, .3)], 1.9,
                  loc=(x, -3.6, PAD), axis='X', chamfer=.03)
        a.part('Barrier_eyes', 'Steel').torus(.05, .012, loc=(x, -3.6, PAD + .82), rot=(0, R90, 0), seg=6, ring=3)
    K.wire_fence(a, [(3.7, -3.0, PAD), (3.7, 3.75, PAD), (-3.7, 3.75, PAD)], h=1.8, post=2.2, strands=3,
                 concertina=False)
    K.dust(a, (0, 0, PAD), radius=5.5, k=.12)


def _radar_tower(a):
    """The lattice tower: four legs tapering from a 2.6 m square to 1.6 m at 4.6 m, X bracing in three bays, a
    ladder with cage hoops, the railed platform with its grating, the drive housing and the `Radar` pivot."""
    tw = a.part('Tower', 'Steel')
    cx, cy = .6, .4
    b0, b1, H = 1.3, .8, 4.6
    legs = [(sx, sy) for sx in (-1, 1) for sy in (-1, 1)]
    for sx, sy in legs:
        tw.tube([(cx + sx * b0, cy + sy * b0, PAD), (cx + sx * b1, cy + sy * b1, PAD + H)], .07, seg=6)
        k.block(a.part('Tower_footing', 'Concrete'), (.5, .5, .3), loc=(cx + sx * b0, cy + sy * b0, PAD + .15),
                chamfer=.05, taper=(.8, .8))
    bolts = a.part('Kit_bolts', 'Steel')
    for sx, sy in legs:
        for bx in (-.17, .17):
            for by in (-.17, .17):
                bolts.cyl(.025, .06, loc=(cx + sx * b0 + bx, cy + sy * b0 + by, PAD + .32), seg=6, bevel=0)
    levels = [0, 1.6, 3.1, H]
    for z0, z1 in zip(levels, levels[1:]):
        f0, f1 = z0 / H, z1 / H
        r0, r1 = b0 + (b1 - b0) * f0, b0 + (b1 - b0) * f1
        for (ax, ay), (bx, by) in (((-1, -1), (1, -1)), ((1, -1), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, -1))):
            tw.tube([(cx + ax * r0, cy + ay * r0, PAD + z0), (cx + bx * r1, cy + by * r1, PAD + z1)], .03, seg=4)
            tw.tube([(cx + bx * r0, cy + by * r0, PAD + z0), (cx + ax * r1, cy + ay * r1, PAD + z1)], .03, seg=4)
            tw.tube([(cx + ax * r1, cy + ay * r1, PAD + z1), (cx + bx * r1, cy + by * r1, PAD + z1)], .035, seg=4)
    K.ladder(a.part('Ladders', 'Steel'), (cx, cy - b0 - .15, PAD), (cx, cy - b1 - .15, PAD + H + .1), width=.45,
             step=.32, r=.02)
    for z in (1.8, 2.6, 3.4, 4.2):
        f = z / H
        a.part('Ladders', 'Steel').torus(.38, .012, loc=(cx, cy - (b0 + (b1 - b0) * f) - .4, PAD + z),
                                         rot=(0, 0, 0), seg=10, ring=3)
    plat = a.part('Platform', 'Armor')
    k.block(plat, (2.4, 2.4, .12), loc=(cx, cy, PAD + H + .06), chamfer=.02)
    k.inset(plat, lambda c, n, f: n.z > .9, width=.12, depth=-.02)
    K.railing(a.part('Railing', 'Steel'), [(cx - 1.15, cy - 1.15, PAD + H + .12), (cx + 1.15, cy - 1.15, PAD + H + .12),
                                           (cx + 1.15, cy + 1.15, PAD + H + .12), (cx - 1.15, cy + 1.15, PAD + H + .12),
                                           (cx - 1.15, cy - .4, PAD + H + .12)], h=1.0, post=1.1, r=.02)
    drive = a.part('Radar_drive', 'Team')
    k.lathe(drive, [(.55, 0), (.55, .5), (.45, .6), (.3, .62), (.3, .8)], loc=(cx, cy, PAD + H + .12), seg=14,
            worn=(1, 2))
    K.beacon(a, (cx + 1.0, cy + 1.0, PAD + H + 1.1), r=.09)
    # The cable tray from the platform down the tower to the shelter.
    a.part('Kit_cables', 'Undercarriage').tube([(cx + .3, cy + .2, PAD + H + .1), (cx + b1 + .05, cy + .2, PAD + H - .2),
                                                (cx + b0 + .05, cy + .2, PAD + .6), (-1.6, cy + .2, PAD + .5)],
                                               .05, seg=4)
    return (cx, cy, PAD + H + .92)


def _radar_dish(a, at):
    """The rotating head on `Radar`: the yoke, the big parabolic reflector tilted up 15 degrees (its back truss, the
    feed horn on struts, a counterweight), an IFF bar on top."""
    r = a.pivot('Radar', at)
    yoke = a.part('Radar_truss', 'Steel', r)
    k.block(yoke, (1.3, .5, .25), loc=(0, 0, .1), chamfer=.03)
    for s in (-1, 1):
        k.block(yoke, (.12, .3, 1.0), loc=(s * .6, -.1, .65), chamfer=.02)
    n = Vector((0, -math.cos(math.radians(15)), math.sin(math.radians(15))))
    centre = Vector((0, -.45, 1.3))
    K.dish(a.part('Radar_dish', 'Team', r), a.part('Radar_feed', 'Steel', r), tuple(centre), r=2.25,
           normal=tuple(n), depth=.55, seg=24)
    back = centre - n * .05
    for u in range(6):
        ang = u * TAU / 6
        p = back + Vector((math.cos(ang) * 1.6, math.sin(ang) * .4, math.sin(ang) * 1.5))
        yoke.tube([tuple(back + Vector((0, .5, 0))), tuple(p)], .03, seg=4)
    # Round 3: the reflector's panel seams (radial ribs on its face) and its rim bolts.
    rib = a.part('Dish_ribs', 'Steel', r)
    for u in range(8):
        ang = u * TAU / 8
        tip = centre + Vector((math.cos(ang) * 2.1, 0, math.sin(ang) * 2.1)) - n * .0
        rib.tube([tuple(centre + n * .02), tuple(tip + n * .5)], .025, seg=3)
    k.block(a.part('Counterweight', 'Armor', r), (.9, .5, .5), loc=(0, .85, .7), chamfer=.04)
    k.block(a.part('Iff_bar', 'Armor', r), (2.2, .12, .2), loc=(0, -.2, 3.75), chamfer=.02)


def _radar_kit(a):
    """The equipment container (door, air conditioner, vents), the generator skid with its stack, fuel drums, a
    floodlight, whips, the Point_fire."""
    sh = a.part('Shelter', 'MetalSheet')
    k.block(sh, (2.4, 3.6, 2.4), loc=(-2.2, .9, PAD + 1.2), chamfer=.05)
    k.inset(sh, lambda c, n, f: abs(n.x) > .9, width=.1, depth=-.03)
    K.door(a, (-.98, .2, PAD + .05), (.9, 2.0), normal=(1, 0, 0), mat='Armor')
    k.block(a.part('Ac_unit', 'Armor'), (.4, .8, .6), loc=(-2.2, 2.85, PAD + 1.4), chamfer=.03)
    K.grille(a, (-2.2, 3.26, PAD + 1.4), .7, .5, facing=(0, 1, 0), slats=4)
    a.part('Roof', 'Armor').box((2.5, 3.7, .06), loc=(-2.2, .9, PAD + 2.43), bevel=0)
    K.whip_antenna(a.part('Antenna', 'Steel'), (-3.0, -.6, PAD + 2.45), h=2.4, r=.03)
    K.whip_antenna(a.part('Antenna', 'Steel'), (-1.4, 2.4, PAD + 2.45), h=1.6, r=.025)
    sk = a.part('Generator_skid', 'Steel')
    sk.box((1.6, 2.4, .12), loc=(2.2, -2.0, PAD + .06), bevel=0)
    gen = a.part('Generator', 'Team')
    k.block(gen, (1.3, 2.1, 1.2), loc=(2.2, -2.0, PAD + .72), chamfer=.06)
    K.grille(a, (2.86, -2.0, PAD + .8), 1.2, .6, facing=(1, 0, 0), slats=5)
    K.exhaust(a, (2.5, -1.3, PAD + 1.32), r=.07, length=.8, muffler=True)
    a.pivot('Point_fire', (-2.0, -2.4, 2.5))
    for i, (x, y) in enumerate(((3.2, -.4), (3.2, .25))):
        K.fuel_drum(a.part('Fuel_drums', 'Fuel'), a.part('Drum_bands', 'Steel'), (x, y, PAD), r=.29, h=.88)
    K.floodlight(a, (3.3, 3.3, PAD), facing=(-.7, -.7, -.4), pole=3.0)
    K.lamp(a, (-.98, .2, PAD + 2.2), (1, 0, 0), r=.09, mat='Steel', guard=True)
    # Round 2: steps up to the container door, junction boxes and a warning board on the tower, a cable reel,
    # battery boxes by the generator, a sunshade over its control panel, an earthing rod.
    st = a.part('Fit_steel', 'Steel')
    for i in range(2):
        st.box((.5, .9, .04), loc=(-.75 + i * .25, .2, PAD + .12 + i * .14), bevel=0)
    jb = a.part('Junction_boxes', 'Armor')
    k.block(jb, (.35, .2, .45), loc=(1.85, -.85, PAD + 1.2), chamfer=.02)
    k.block(jb, (.3, .2, .35), loc=(-1.0, -1.0, PAD + 2.6), chamfer=.02)
    a.part('Signs', 'Hazard').box((.5, .03, .4), loc=(.6, -.9, PAD + .9), bevel=0)
    a.part('Sign_marks', 'Charred').box((.2, .04, .2), loc=(.6, -.91, PAD + .9), rot=(0, .78, 0), bevel=0)
    k.lathe(a.part('Cable_reel', 'Wood'), [(.4, -.25), (.4, -.21), (.22, -.21), (.22, .21), (.4, .21), (.4, .25)],
            loc=(-.2, -2.6, PAD + .4), rot=(0, R90, 0), seg=10)
    for i in range(2):
        k.block(a.part('Battery_boxes', 'Team'), (.4, .6, .35), loc=(3.4, -3.3 + i * .65, PAD * .7 + .17),
                chamfer=.03)
    a.part('Sunshade', 'Canvas').box((1.1, .8, .03), loc=(1.4, -2.0, PAD + 1.9), rot=(.15, 0, 0), bevel=0)
    for dx in (-.5, .5):
        st.box((.04, .04, 1.6), loc=(1.4 + dx, -2.35, PAD + 1.1), bevel=0)
    st.cyl(.015, .6, loc=(-3.4, -3.4, PAD + .3), seg=4, bevel=0)


def radar_site(a):
    """The radar site: see the module docstring."""
    _radar_pad(a)
    at = _radar_tower(a)
    _radar_dish(a, at)
    _radar_kit(a)
    k.clean(a)


# ============================================================================= ammo_dump
def _dump_ground(a):
    outline = [(-3.05, -2.3), (-2.2, -2.45), (-1.0, -2.2), (.4, -2.45), (1.6, -2.35), (3.05, -1.9), (2.8, -.6),
               (3.0, 1.2), (2.9, 2.45), (1.3, 2.3), (-.4, 2.45), (-2.9, 2.3), (-2.8, 1.4), (-3.05, .4)]
    k.extrude(a.part('Base', 'Dirt'), outline, .14, loc=(0, 0, .07), axis='Z', chamfer=.05, corner=.1,
              taper=(.97, .97))
    K.dust(a, (0, -1.2, .14), radius=2.6, k=.25)


def _dump_bunker(a):
    """The semi-sunken store at the back: the earth berm (sloped on three sides), the timber revetment framing the
    entrance, the steel door, the corrugated roof under sandbags, a vent pipe."""
    berm = a.part('Berm', 'Dirt')
    k.extrude(berm, [(-2.9, -.2), (2.9, -.2), (2.9, 2.35), (-2.9, 2.35)], 1.5, loc=(0, 0, .14 + .75), axis='Z',
              chamfer=.1, corner=.4, taper=(.72, .6))
    wood = a.part('Revetment', 'Wood')
    for i in range(6):
        wood.box((2.6, .12, .2), loc=(0, -.26, .3 + i * .21), bevel=0)                          # planked face
    for x in (-1.35, -.55, .55, 1.35):
        wood.box((.16, .16, 1.55), loc=(x, -.32, .9), bevel=0)                                  # posts
    k.block(wood, (2.9, .2, .2), loc=(0, -.32, 1.7), chamfer=.02)                              # lintel
    K.door(a, (0, -.36, .15), (1.0, 1.4), normal=(0, -1, 0), mat='Armor')
    roof = a.part('Roof', 'Corrugated')
    k.block(roof, (2.6, 2.2, .05), loc=(0, .85, 1.72), rot=(-.08, 0, 0), chamfer=0)
    K.sandbag_wall(a, [(-1.0, .5, 1.72), (1.0, .5, 1.72)], layers=1, bag=(.55, .32, .16), round_both=False)
    # Round 3: a course of sandbags along the berm's crest (left, back, right), its top line broken.
    K.sandbag_wall(a, [(-1.9, .1, 1.5), (-1.9, 1.75, 1.5), (1.9, 1.75, 1.5), (1.9, .1, 1.5)], layers=1,
                   bag=(.85, .4, .2), round_both=False)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-1.6, 1.6, 1.45), h=2.0, r=.025)
    k.lathe(a.part('Vent', 'Steel'), [(.07, 0), (.07, .6), (.12, .62), (.12, .7), (0, .74)], loc=(1.6, 1.4, 1.5),
            seg=8, worn=(2,))
    K.lamp(a, (.9, -.4, 1.5), (0, -1, -.3), r=.07, mat='Steel', guard=True)
    # Round 2: turf cut and laid on the berm (camouflage from the air), wattles of stakes holding the berm's front
    # corners, a drainage ditch along the entrance, timber steps down to the door.
    turf = a.part('Turf', 'Foliage')
    for i, (x, y, z, r) in enumerate(((-2.0, 1.2, 1.1, .2), (-1.2, 1.9, 1.2, -.3), (1.9, 1.5, 1.15, .4),
                                      (2.3, .5, .8, .1), (-2.4, .3, .75, -.2), (.2, 2.1, 1.25, .6),
                                      (1.2, 1.9, 1.3, 0))):
        turf.box((.55, .45, .06), loc=(x, y, z), rot=(.25 * math.sin(i), .3 * math.cos(i), r), bevel=0)
    stakes = a.part('Wattle', 'Wood')
    for s in (-1, 1):
        for j in range(5):
            stakes.cyl(.035, .9, loc=(s * (1.55 + j * .25), -.2 - j * .05, .5), rot=(.1, 0, 0), seg=5, bevel=0)
        stakes.box((1.3, .05, .05), loc=(s * 2.05, -.28, .75), rot=(0, 0, s * -.2), bevel=0)
    a.part('Ditch', 'Undercarriage').box((3.0, .25, .02), loc=(0, -.65, .145), bevel=0)
    for i in range(2):
        a.part('Steps', 'Wood').box((1.0, .25, .08), loc=(0, -.75 - i * .25, .17 + (1 - i) * .1), bevel=0)
    sign = a.part('Signs', 'Hazard')
    k.block(sign, (.5, .03, .5), loc=(-.95, -.42, 1.25), rot=(0, .78, 0), chamfer=0)
    a.part('Sign_marks', 'Charred').box((.18, .04, .18), loc=(-.95, -.43, 1.25), rot=(0, .78, 0), bevel=0)


def _dump_yard(a):
    """Outside the store: crates on pallets in two stacks, a row of shell cases, a camouflage net on poles over
    them, the red ammunition flag on its pole, sandbags on the open side, the extinguisher stand."""
    crates = a.part('Crates', 'Crate')
    bands = a.part('Crate_bands', 'Steel')
    pal = a.part('Pallets', 'Wood')
    for (x, y), stack in (((-1.7, -1.4), 3), ((.2, -1.6), 2)):
        k.block(pal, (1.2, 1.0, .12), loc=(x, y, .2), chamfer=.01)
        for j in range(stack):
            for i in range(2):
                K.crate(crates, bands, (1.1, .44, .3), (x, y - .23 + i * .46, .26 + j * .3),
                        rot=(0, 0, .02 * (i - j)), bands=1)
    # Round 4: a timber blast traverse between the two crate stacks (a hit on one stack does not set off the other).
    trav = a.part('Traverse', 'Wood')
    for j in range(4):
        trav.box((.12, 1.3, .2), loc=(-.75, -1.5, .26 + j * .21), bevel=0)
    for dy in (-.6, .6):
        trav.box((.14, .14, 1.0), loc=(-.75, -1.5 + dy, .64), bevel=0)
    k.block(a.part('Traverse_fill', 'Dirt'), (.4, 1.2, .8), loc=(-.55, -1.5, .54), chamfer=.08, taper=(.6, .9))
    shells = a.part('Shell_cases', 'Gilded')
    heads = a.part('Shell_heads', 'Armor')
    for i in range(5):
        x = 1.6 + i * .22
        k.lathe(shells, [(.07, 0), (.075, .02), (.075, .45), (.06, .48)], loc=(x, -1.85, .14), seg=6)
        k.lathe(heads, [(.06, .48), (.03, .68), (0, .72)], loc=(x, -1.85, .14), seg=6)
    poles = [(-2.6, -2.2), (1.2, -2.25), (1.2, -.6), (-2.6, -.6)]
    hs = (2.0, 1.9, 2.1, 2.2)
    wood = a.part('Net_poles', 'Wood')
    for (x, y), h in zip(poles, hs):
        wood.cyl(.045, h, loc=(x, y, .14 + h / 2), seg=6, bevel=0)
    pts = [(x, y, .14 + h) for (x, y), h in zip(poles, hs)]
    mid = (-.7, -1.4, 1.75)
    net = a.part('Camo_net', 'Canvas')
    tris = []
    for i in range(4):
        tris += [pts[i], pts[(i + 1) % 4], mid]
    # Round 4: the net drawn on to a fifth pole over the bunker's mouth (a sagging flap).
    far = (1.9, .1, 1.95)
    wood.cyl(.04, 1.8, loc=(far[0], far[1], .14 + .9), seg=5, bevel=0)
    tris += [pts[1], far, pts[2]]
    net.mesh(tris, [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(5)])
    net.mesh(tris, [(3 * i, 3 * i + 2, 3 * i + 1) for i in range(5)])
    garn = a.part('Camo_garnish', 'Foliage')
    for i, f in enumerate((.25, .5, .75)):
        p0, p1 = Vector(pts[0]), Vector(pts[1])
        q = p0 + (p1 - p0) * f
        garn.box((.35, .3, .04), loc=(q.x, q.y + .2, q.z - .1), rot=(.2, 0, .3 * i), bevel=0)
    rope = a.part('Guy_ropes', 'Canvas')
    for (x, y, z) in (pts[0], pts[1]):
        rope.tube([(x, y, z), (x * 1.08, y - .3, .14)], .01, seg=3)
    # Round 3: the sentry's sandbag ring at the front-left corner, with its timber roof post.
    K.sandbag_wall(a, [(-2.95, -1.45, .14), (-2.95, -2.35, .14), (-2.05, -2.4, .14)], layers=2,
                   bag=(.5, .3, .17), round_both=False)
    a.part('Net_poles', 'Wood').cyl(.04, 1.4, loc=(-2.85, -2.25, .84), seg=5, bevel=0)
    a.part('Flag_pole', 'Steel').cyl(.03, 3.0, loc=(2.75, .4, .14 + 1.5), seg=6, bevel=0)
    a.part('Flag', 'BarrelRed').box((.04, .7, .45), loc=(2.75, .05, 2.8), rot=(0, 0, .15), bevel=0)
    K.sandbag_wall(a, [(2.95, -1.2, .14), (2.95, .9, .14)], layers=1, bag=(.7, .36, .2), round_both=False)
    st = a.part('Extinguisher_stand', 'Wood')
    st.box((.5, .08, 1.2), loc=(-2.75, .15, .74), bevel=0)
    for dx in (-.12, .12):
        k.lathe(a.part('Extinguishers', 'BarrelRed'), [(.07, 0), (.07, .4), (.04, .46), (0, .48)],
                loc=(-2.75 + dx, .07, .5), seg=8, worn=(1,))
    a.part('Fire_bucket', 'BarrelRed').cyl(.12, .22, loc=(-2.75, .05, .3), seg=8, r2=.1, bevel=0)
    # Round 2: an open crate showing its rounds, a hand trolley, the sentry's field telephone on a post, a tally
    # board for the stock.
    k.block(a.part('Crates', 'Crate'), (1.0, .45, .25), loc=(1.9, -.75, .27), chamfer=.015)
    for i in range(4):
        k.lathe(a.part('Loose_rounds', 'Gilded'), [(.05, 0), (.05, .7), (0, .78)], loc=(1.5 + i * .25, -.75, .42),
                rot=(0, R90, 0), seg=6)
    tr = a.part('Trolley', 'Steel')
    tr.box((.5, .35, .03), loc=(-.6, -2.0, .2), bevel=0)
    tr.tube([(-.85, -1.82, .2), (-.85, -1.82, 1.1)], .015, seg=4)
    tr.tube([(-.35, -1.82, .2), (-.35, -1.82, 1.1)], .015, seg=4)
    for dx in (-.25, .25):
        tr.cyl(.1, .04, loc=(-.6 + dx, -1.85, .24), rot=(0, R90, 0), seg=8, bevel=0)
    a.part('Phone_post', 'Wood').cyl(.04, 1.2, loc=(2.5, -2.1, .74), seg=5, bevel=0)
    k.block(a.part('Field_phone', 'Armor'), (.22, .12, .18), loc=(2.5, -2.18, 1.15), chamfer=.015)
    k.block(a.part('Tally_board', 'PlasterWhite'), (.6, .03, .45), loc=(-1.6, -.42, 1.0), chamfer=0)


def ammo_dump(a):
    """The ammunition dump: see the module docstring."""
    _dump_ground(a)
    _dump_bunker(a)
    _dump_yard(a)
    k.clean(a)


BUILDERS = {
    'repair_bay': (repair_bay, dict(ao_distance=1.0, grime_height=.6)),
    'radar_site': (radar_site, dict(ao_distance=.9, grime_height=.5)),
    'ammo_dump': (ammo_dump, dict(ao_distance=.6, grime_height=.4)),
}
