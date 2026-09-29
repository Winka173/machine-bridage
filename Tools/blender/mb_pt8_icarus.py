"""Machine Brigade play-test 8 (DECISIONS 22R): Icarus (silver_bug / silver_bug_wreck) redesigned from scratch.

The owner found DECISIONS 20Y's Icarus too close to a Star Wars ship (a Star Destroyer wedge with a Venator's doors).
Only the idea is kept, an orbital boss; everything else is new, drawn from real orbital platforms and from other
science fiction's ship language (see DECISIONS 22R for the list):

  * The layout is an armed space station's, not a warship's: a long round pressure hull along the thrust axis (the
    Soviet Polyus / Skif-DM orbital weapons platform, Almaz), a square lattice truss across its middle carrying two big
    solar-array wings (the ISS's main truss and arrays, Ace Combat 5's SOLG), white radiator panels over the service
    module aft (the ISS's heat radiators), a single big drive bell at the stern on a gimbal ring with vernier nozzles
    round it (The Expanse's thrust-axis ships, the MCRN Donnager's drive cone), and a telescope nose with a sunshade
    tube and an open aperture door (Hubble, KH-11): the eye that aims its laser.
  * Colours: satin white hull and radiators, gold foil (multi-layer insulation) on the telescope, the equipment racks
    and the service module's flanks, deep blue solar cells on steel frames, the side's colour only in bands round the
    modules, the drive's glow and the verniers. No grey wedge, no trench, no command tower, no stripes down a deck.
  * Seen from the battle camera it reads as a cross: a white-and-gold spine with two broad blue wings and white fins
    aft, the drive bell behind: a satellite gone to war.

Every node keeps its name and place (mb_orbital.NODES), so the parts, muzzles and big attacks play as before: `Turret`
(the ventral laser ball, `Muzzle_main`), `Mount_gun` / `.001` (coilguns, on barbettes on the truss), `Mount_mg` /
`.001` (flak, on the forward module and the service module), `Pd_laser_l` / `_r` (on the forward equipment racks),
`Thruster_main` (the drive), `Thruster_fl` / `_fr` (RCS pods on booms off the forward module), `Thruster_rl` / `_rr`
(RCS pods at the radiator tips), `Pod_bay` (`Muzzle_missile`, under the service module), `Uplink` (a dish on a mast),
and the crash turrets `Mount_gun.002` / `.003` (40 mm, on sponsons off the service module, woken on the ground).
The wreck is the same platform crashed, raised by mb_orbital.LIFT: one solar wing torn off and lying beside it, the
other bent to the ground, a radiator snapped off, the telescope's door gone, scorched, in its crater and debris.

Conventions are mb_vehicles'/mb_orbital's: metres, +Z up, Blender -Y is the front, +X the vehicle's left.
"""
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import mb_orbital as orb  # noqa: E402
from mb_phase2 import _suffixed  # noqa: E402
from mb_phase8 import autocannon  # noqa: E402
from mb_vehicles import FORWARD, R90  # noqa: E402

ALONG_Y = (R90, 0, 0)    # a cylinder's axis along Y
ALONG_X = (0, R90, 0)    # a cylinder's axis along X

HULL = 'Fuel'            # satin white paint
FOIL = 'Gilded'          # gold multi-layer insulation
CELLS = 'ContainerBlue'  # solar cells

# The pressure hull, stern (+y) to nose (-y): (y, radius, axis z). Forward module, neck, service module.
CORE_Z = 0.1
FWD = (-13.0, -3.0, 2.85)     # y from, y to, radius (top at CORE_Z + r = 2.95)
AFT = (2.6, 12.4, 2.9)        # the service module (top 3.35, its belly clear of the pod bay)
AFT_Z = 0.45                  # its axis, a little above the forward module's
TRUSS_Z = 0.45                # the main truss's centre height
WING_X = (6.4, 12.2)          # the solar wings' span out from the centreline
WING_Y = (0.7, 4.6)           # each blanket's chord, fore and aft of the truss
RAD_Y = (8.2, 12.2)           # the radiators' chord
RAD_X = (3.9, 8.7)            # and span


def _ring_band(part, y, r, width=.36, z=CORE_Z, seg=24):
    """A band round a module (the side's colour or a joint ring), a little proud of the hull."""
    part.cyl(r + .04, width, loc=(0, y, z), rot=ALONG_Y, seg=seg, bevel=.02, bseg=1)


def _hull(a, lift, wreck, rng):
    """The pressure hull: the forward module, the neck, the service module and the boat-tail, with bands, foil,
    handrails and small gear."""
    white = a.part('Hull', 'Armor' if wreck else HULL)
    y0, y1, r = FWD
    z = CORE_Z + lift
    white.cyl(r, y1 - y0, loc=(0, (y0 + y1) / 2, z), rot=ALONG_Y, seg=24, bevel=.06, bseg=1)
    # The neck between the modules (under the truss) and the service module.
    white.cyl(2.3, AFT[0] - y1 + .1, loc=(0, (y1 + AFT[0]) / 2, z), rot=ALONG_Y, seg=20, bevel=.03, bseg=1)
    a0, a1, ra = AFT
    za = AFT_Z + lift
    white.cyl(ra, a1 - a0, loc=(0, (a0 + a1) / 2, za), rot=ALONG_Y, seg=24, bevel=.06, bseg=1)
    # End domes: the forward module's front bulkhead (behind the telescope) and the boat-tail down to the drive.
    white.cyl(r, .5, r2=2.2, loc=(0, y0 - .25, z), rot=(R90, 0, 0), seg=24, bevel=.03, bseg=1)

    def circle(y, rr, zc):
        return [(rr * math.sin(k * math.tau / 24), y, zc + rr * math.cos(k * math.tau / 24)) for k in range(24)]
    white.loft([circle(a1 - .02, ra, za), circle(a1 + .6, 2.4, (za + z) / 2), circle(a1 + 1.2, 1.7, z)], bevel=0)
    # The side's colour in bands, and steel joint rings where the modules meet.
    team = a.part('Bands', 'Charred' if wreck else 'Team')
    joints = a.part('Joint_rings', 'Steel')
    for y in (-12.2, -3.6):
        _ring_band(team, y, r, z=z)
    for y in (3.3, 11.7):
        _ring_band(team, y, ra, z=za)
    for y in (y0 + .05, y1 - .05):
        _ring_band(joints, y, r + .02, width=.16, z=z)
    for y in (a0 + .05, a1 - .05):
        _ring_band(joints, y, ra + .02, width=.16, z=za)
    # Gold foil on the service module's flanks (between the bands), in panels, a centimetre proud.
    foil = a.part('Foil_panels', 'Charred' if wreck else FOIL, flat=True)
    for side in (-1, 1):
        for yc in (5.2, 7.3, 9.6):
            ang = side * math.radians(62)
            x, zz = math.sin(ang) * (ra + .02), math.cos(ang) * (ra + .02)
            foil.box((.05, 1.9, 1.5), loc=(x, yc, za + zz), rot=(0, ang, 0), bevel=0, seg=1)
            ang2 = side * math.radians(112)
            x2, z2 = math.sin(ang2) * (ra + .02), math.cos(ang2) * (ra + .02)
            foil.box((.05, 1.9, 1.3), loc=(x2, yc, za + z2), rot=(0, ang2, 0), bevel=0, seg=1)
    # Handrails (yellow, as on the ISS) along the forward module's top and small gear: star trackers, antennas.
    rails = a.part('Handrails', 'Hazard')
    for side in (-1, 1):
        x = side * .9
        top = z + math.sqrt(r * r - x * x) + .08
        rails.tube([(x, y, top) for y in (-11.5, -7.5, -4.2)], .035, seg=5)
        for y in (-11.5, -9.5, -7.5, -5.8, -4.2):
            rails.cyl(.03, .1, loc=(x, y, top - .05), seg=5, bevel=0)
    gear = a.part('Small_gear', 'Steel')
    dark = a.part('Small_gear_dark', 'Undercarriage')
    for (x, y) in ((1.4, -12.0), (-1.5, -8.2), (1.2, 10.4), (-1.3, 6.0)):
        rr, zc = (r, z) if y < 0 else (ra, za)
        top = zc + math.sqrt(max(0.0, rr * rr - x * x))
        gear.box((.5, .6, .35), loc=(x, y, top + .1), bevel=.03, seg=1)
        dark.cyl(.12, .06, loc=(x, y - .3, top + .15), rot=ALONG_Y, seg=8, bevel=0)
    # Status lights along the flanks of the forward module (lit ports), fewer on the wreck.
    lamps = a.part('Status_lights', 'Lamp')
    for side in (-1, 1):
        for y in (-11.0, -9.4, -7.8, -6.2, -4.6):
            if wreck and rng.random() < .6:
                continue
            lamps.box((.05, .3, .14), loc=(side * (r + .015), y, z), bevel=0, seg=1)
    # The belly: a keel plate under the forward module and dark service hatches.
    keel = a.part('Keel', 'Armor')
    keel.box((1.6, 4.0, .12), loc=(0, -11.0, z - r + .02), bevel=.02, seg=1)
    keel.box((1.6, 3.4, .12), loc=(0, -3.9, z - r + .02), bevel=.02, seg=1)
    for y in (-11.0, -3.9):
        dark.box((1.0, .9, .03), loc=(0, y, z - r - .05), bevel=0)
    if wreck:
        scorch = a.part('Scorch', 'Charred', flat=True)
        for i in range(14):
            y = rng.uniform(-12.0, 12.0)
            rr, zc = (r, z) if y < 0 else (ra, za)
            ang = rng.uniform(-1.2, 1.2)
            scorch.ico((1.1, 1.3, .25), loc=(math.sin(ang) * rr, y, zc + math.cos(ang) * rr), rot=(0, ang, 0), sub=1, jitter=.3,
                       seed=i * 2.3)


def _telescope(a, lift, wreck):
    """The nose: a telescope's sunshade tube in gold foil, its open aperture door (gone on the wreck), the dark
    aperture with the secondary mirror's spider, and a ring of sensor blisters round its base."""
    z = CORE_Z + lift
    y0 = FWD[0] - .45
    length = 3.5
    tube = a.part('Telescope_tube', 'Charred' if wreck else FOIL)
    tube.cyl(1.95, length, loc=(0, y0 - length / 2, z), rot=ALONG_Y, seg=24, bevel=.03, bseg=1)
    white = a.part('Telescope_rings', 'Armor' if wreck else HULL)
    for y in (y0 - .15, y0 - length + .15):
        white.cyl(2.02, .3, loc=(0, y, z), rot=ALONG_Y, seg=24, bevel=.02, bseg=1)
    mouth = y0 - length
    a.part('Telescope_aperture', 'Obsidian').cyl(1.78, .04, loc=(0, mouth - .03, z), rot=ALONG_Y, seg=24, bevel=0)
    spider = a.part('Telescope_spider', 'Steel')
    spider.box((3.5, .05, .07), loc=(0, mouth - .06, z), bevel=0)
    spider.box((.07, .05, 3.5), loc=(0, mouth - .06, z), bevel=0)
    spider.cyl(.35, .2, loc=(0, mouth - .12, z), rot=ALONG_Y, seg=12, bevel=0)
    if not wreck:
        # The aperture door, hinged at the top of the mouth and swung 130 degrees open, forward and over (Hubble's).
        swing = math.radians(130)
        tilt = R90 - swing
        hinge = (0, mouth, z + 2.0)
        centre = (0, mouth - 1.95 * math.sin(swing), z + 2.0 - 1.95 * math.cos(swing))
        normal = (0, -math.sin(tilt), math.cos(tilt))
        a.part('Aperture_door', HULL).cyl(1.95, .08, loc=centre, rot=(tilt, 0, 0), seg=24, bevel=.02, bseg=1)
        a.part('Door_foil', FOIL).cyl(1.7, .02, loc=tuple(c + n * .05 for c, n in zip(centre, normal)), rot=(tilt, 0, 0), seg=24,
                                      bevel=0)
        a.part('Door_hinge', 'Steel').cyl(.09, 1.2, loc=hinge, rot=ALONG_X, seg=8, bevel=0)
    blister = a.part('Sensor_blisters', 'Glass')
    for k in range(6):
        ang = k * math.tau / 6 + math.pi / 6
        blister.sphere(.28, loc=(math.sin(ang) * 2.2, y0 + .3, z + math.cos(ang) * 2.2), seg=10, rings=6)


def _racks(a, lift, wreck):
    """Equipment racks along the forward module's shoulders on brackets, carrying the point-defence lasers and
    gold-foiled boxes (the ISS's external payload racks)."""
    z = CORE_Z + lift
    r = FWD[2]
    rack = a.part('Racks', 'Steel')
    brackets = a.part('Rack_brackets', 'Armor')
    boxes = a.part('Rack_boxes', 'Charred' if wreck else FOIL)
    top = 3.17 + lift            # the point-defence lasers' base rests on it
    for side in (-1, 1):
        x = side * 3.2
        rack.box((.8, 8.8, .3), loc=(x, -5.4, top - .15), bevel=.03, seg=1)
        ang = math.radians(38)
        hx, hz = side * math.sin(ang) * r, z + math.cos(ang) * r
        for y in (-9.2, -6.6, -4.0, -1.6):
            brackets.limb((hx * .96, y, hz - .05), (x * .92, y, top - .28), .22, .3, bevel=.02, seg=1)
        for y, w in ((-8.4, 1.0), (-7.1, .8), (-3.2, 1.1), (-2.0, .7)):
            boxes.box((.62, w, .44), loc=(x, y, top + .22), bevel=.03, seg=1)


def _truss(a, lift, wreck):
    """The main truss across the middle: a square lattice beam from wing to wing, the rotary joints, the coilguns'
    barbettes (Mount_gun / .001 sit on them), and the solar wings (the right one torn off on the wreck, the left bent
    to the ground)."""
    z = TRUSS_Z + lift
    chords = a.part('Truss_chords', 'Steel')
    lace = a.part('Truss_lacing', 'Armor')
    half = WING_X[0] - .3
    w = .95
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                x0, x1 = (2.2, half) if sx > 0 else (-half, -2.2)
                chords.box((x1 - x0, .12, .12), loc=((x0 + x1) / 2, sy * w / 2, z + sz * w / 2), bevel=0, seg=1)
        # Lacing: diagonals on the top, the bottom and the two faces, bay by bay.
        n = 4
        for i in range(n):
            xa = sx * (2.2 + (half - 2.2) * i / n)
            xb = sx * (2.2 + (half - 2.2) * (i + 1) / n)
            for sy in (-1, 1):
                lace.limb((xa, sy * w / 2, z - w / 2), (xb, sy * w / 2, z + w / 2), .07, .07, bevel=0, seg=1)
            for sz in (-1, 1):
                lace.limb((xa, -w / 2, z + sz * w / 2), (xb, w / 2, z + sz * w / 2), .07, .07, bevel=0, seg=1)
            for sy in (-1, 1):
                lace.box((.08, .08, w), loc=(xb, sy * w / 2, z), bevel=0, seg=1)
                lace.box((.08, w, .08), loc=(xb, 0, z + sy * w / 2), bevel=0, seg=1)
    # Rotary joints at the truss ends and the coilgun barbettes (tall blocks up to the mounts' rings).
    joint = a.part('Rotary_joints', 'Armor')
    barbette = a.part('Barbettes', 'Armor' if wreck else HULL)
    team = a.part('Barbette_bands', 'Charred' if wreck else 'Team')
    for sx in (-1, 1):
        joint.cyl(.72, .5, loc=(sx * (half + .2), 0, z), rot=ALONG_X, seg=16, bevel=.03, bseg=1)
        gx, gy, gz = orb._node('Mount_gun' if sx > 0 else 'Mount_gun.001', lift)
        base = z + w / 2
        top = gz - .34
        barbette.box((1.3, 1.3, top - base), loc=(gx, gy, (top + base) / 2), bevel=.06, seg=1, taper=(.86, .86))
        team.box((1.32, 1.32, .16), loc=(gx, gy, top - .35), bevel=.02, seg=1, taper=(.99, .99))
    # The wings: a boom out to the tip and two blankets per side (fore and aft of the boom).
    for sx in (-1, 1):
        if wreck and sx < 0:
            _torn_wing(a, lift)
            continue
        droop = math.radians(28) if wreck else 0.0
        _wing(a, sx, z, droop)


def _wing(a, sx, z, droop):
    """A solar wing on the +X (sx 1) or -X side: a boom and two blankets of deep blue cells on steel frames with
    their cell grid, from WING_X out, turned down about the rotary joint by `droop` (the wreck's bent wing)."""
    x0, x1 = WING_X
    boom = a.part('Wing_booms', 'Steel')
    frame = a.part('Wing_frames', 'Steel')
    cells = a.part('Wing_cells', CELLS)
    grid = a.part('Wing_grid', 'Undercarriage')
    c, s = math.cos(droop), math.sin(droop)

    def at(x, y, dz=0.0):
        """A point x out along the wing (from the joint at x0 - .3), y fore/aft, dz over its face, drooped."""
        d = x - (x0 - .3)
        return (sx * ((x0 - .3) + d * c + dz * s), y, z - d * s + dz * c)
    rot = (0, sx * droop, 0)
    mid = (x0 + x1) / 2
    boom.cyl(.13, x1 - x0 + .6, loc=at(mid, 0), rot=(0, R90 + sx * droop, 0), seg=8, bevel=0)
    for sy in (-1, 1):
        yc = sy * (WING_Y[0] + WING_Y[1]) / 2
        chord = WING_Y[1] - WING_Y[0]
        frame.box((x1 - x0, chord, .07), loc=at(mid, yc), rot=rot, bevel=.01, seg=1)
        cells.box((x1 - x0 - .12, chord - .12, .03), loc=at(mid, yc, .045), rot=rot, bevel=0, seg=1)
        for k in range(1, 8):
            x = x0 + (x1 - x0) * k / 8
            grid.box((.03, chord - .14, .012), loc=at(x, yc, .066), rot=rot, bevel=0)
        grid.box((x1 - x0 - .14, .03, .012), loc=at(mid, yc, .066), rot=rot, bevel=0)
        # Spreader bars from the boom to the blanket's outer corners.
        boom.limb(at(x1, 0, .05), at(x1, sy * WING_Y[1], .05), .06, .06, bevel=0, seg=1)


def _torn_wing(a, lift):
    """The wreck's torn-off wing: its two blankets lying broken on the ground beside the hull, a stub of boom."""
    x0, x1 = WING_X
    frame = a.part('Wing_frames', 'Steel')
    cells = a.part('Wing_cells', CELLS)
    boom = a.part('Wing_booms', 'Steel')
    boom.cyl(.13, 1.4, loc=(-(x0 + .4), 0, TRUSS_Z + lift), rot=(0, R90, .25), seg=8, bevel=0)
    for (x, y, tilt, turn) in ((-12.6, 3.4, .22, .35), (-11.8, -2.6, -.3, -.2)):
        frame.box((4.4, 3.2, .07), loc=(x, y, .7), rot=(tilt, .12, turn), bevel=.01, seg=1)
        cells.box((4.3, 3.1, .03), loc=(x, y, .76), rot=(tilt, .12, turn), bevel=0, seg=1)


def _radiators(a, lift, wreck):
    """White heat radiators over the service module's aft end, on arms, ribbed; the right one snapped off on the
    wreck (a stub); the rear RCS pods sit at their tips."""
    z = TRUSS_Z + lift - .05
    panel = a.part('Radiators', 'Charred' if wreck else 'Medical')
    ribs = a.part('Radiator_ribs', 'Steel')
    arms = a.part('Radiator_arms', 'Armor')
    x0, x1 = RAD_X
    y0, y1 = RAD_Y
    for sx in (-1, 1):
        arms.limb((sx * 2.6, (y0 + y1) / 2, z), (sx * (x0 + .2), (y0 + y1) / 2, z), .3, .3, bevel=.02, seg=1)
        if wreck and sx < 0:
            panel.box((1.2, y1 - y0, .08), loc=(sx * (x0 + .6), (y0 + y1) / 2, z - .2), rot=(0, -.4, 0), bevel=.01, seg=1)
            continue
        panel.box((x1 - x0, y1 - y0, .08), loc=(sx * (x0 + x1) / 2, (y0 + y1) / 2, z), bevel=.01, seg=1)
        for k in range(1, 7):
            y = y0 + (y1 - y0) * k / 7
            ribs.box((x1 - x0 - .1, .05, .03), loc=(sx * (x0 + x1) / 2, y, z + .055), bevel=0)


def _drive(a, lift, wreck):
    """The drive on its node (`Thruster_main`): a thrust frame, a gimbal ring, the big bell with its glow, and four
    vernier nozzles round it."""
    right, forward, up = orb.NODES['Thruster_main']
    t = a.pivot('Thruster_main', orb._pos(right, forward, up + lift))
    ax = CORE_Z - up   # the drive's axis in the node's frame (on the hull's axis)
    frame = a.part('Drive_frame', 'Armor', t)
    frame.cyl(1.7, .9, r2=1.35, loc=(0, -2.0, ax), rot=(-R90, 0, 0), seg=20, bevel=.03, bseg=1)
    a.part('Gimbal_ring', 'Steel', t).torus(1.3, .16, loc=(0, -1.45, ax), rot=ALONG_Y, seg=24, ring=6)
    bell = a.part('Drive_bell', 'Charred' if wreck else 'Steel', t)
    bell.lathe([(.9, 0.0), (.82, .5), (1.2, 1.4), (1.85, 2.4), (2.3, 3.0), (2.25, 3.05), (1.78, 2.4), (1.15, 1.4), (.78, .5),
                (.85, .02)], loc=(0, -1.5, ax), rot=(-R90, 0, 0), seg=28)
    a.part('Drive_throat', 'Undercarriage', t).cyl(.8, .05, loc=(0, -1.0, ax), rot=ALONG_Y, seg=20, bevel=0)
    glow = a.part('Drive_glow', 'Charred' if wreck else 'TeamGlow', t)
    glow.cyl(1.4, .04, loc=(0, .4, ax), rot=ALONG_Y, seg=24, bevel=0)
    verniers = a.part('Verniers', 'Steel', t)
    vglow = a.part('Vernier_glow', 'Charred' if wreck else 'TeamGlow', t)
    for k in range(4):
        ang = k * math.tau / 4 + math.pi / 4
        x, zz = math.sin(ang) * 2.35, ax + math.cos(ang) * 2.35
        verniers.cyl(.3, .8, r2=.45, loc=(x, -1.9, zz), rot=ALONG_Y, seg=10, bevel=0)
        vglow.cyl(.3, .03, loc=(x, -1.48, zz), rot=ALONG_Y, seg=10, bevel=0)
        frame.limb((x * .6, -2.2, ax + (zz - ax) * .6), (x, -2.1, zz), .22, .22, bevel=0, seg=1)


def _rcs_pod(a, name, lift, boom_from):
    """An RCS pod on its node: a pod with a quad of thruster nozzles, on a boom from `boom_from` (in the node's frame)."""
    right, forward, up = orb.NODES[name]
    p = a.pivot(name, orb._pos(right, forward, up + lift))
    a.part('Rcs_pod', HULL, p).cyl(.5, 1.5, loc=(0, 0, 0), rot=ALONG_Y, seg=12, bevel=.08, bseg=1)
    a.part('Rcs_caps', 'Armor', p).sphere(.5, loc=(0, -.75, 0), rot=(R90, 0, 0), seg=12, rings=6, cut=0)
    nozzles = a.part('Rcs_nozzles', 'Steel', p)
    glow = a.part('Rcs_glow', 'TeamGlow', p)
    for dx, dz, rot in ((.55, 0, ALONG_X), (-.55, 0, ALONG_X), (0, .55, (0, 0, 0)), (0, -.55, (0, 0, 0))):
        nozzles.cyl(.12, .22, r2=.17, loc=(dx, .35, dz), rot=rot, seg=8, bevel=0)
    glow.cyl(.3, .03, loc=(0, .77, 0), rot=ALONG_Y, seg=10, bevel=0)
    a.part('Rcs_booms', 'Steel', p).limb(boom_from, (0, 0, 0), .26, .26, bevel=.02, seg=1)


def _plinth(a, name, lift, below, width=.45):
    """A short column under a mount, from the surface at `below` up to just under the mount's own base."""
    x, y, z = orb._node(name, lift)
    top = z - .02
    if top - below > .02:
        a.part('Plinths', 'Armor').cyl(width, top - below, loc=(x, y, (top + below) / 2), seg=12, bevel=.02, bseg=1)


def _crash_sponsons(a, lift):
    """The two 40 mm turrets that wake on the ground (prompt 20 F.3), on sponsons off the service module."""
    arm = a.part('Sponsons', 'Armor')
    z = AFT_Z + lift
    for s, mount in ((1, 'Mount_gun.002'), (-1, 'Mount_gun.003')):
        loc = (s * 6.5, 6.0, 2.2 + lift)
        arm.limb((s * 2.4, 6.0, z + 1.15), (s * 6.5, 6.0, z + 1.15), .9, .6, bevel=.04, seg=1)
        arm.limb((s * 2.6, 6.0, z - .4), (s * 6.2, 6.0, z + .9), .3, .3, bevel=.02, seg=1)
        base = z + 1.45
        a.part(f'Crash_pylon_{mount[-3:]}', 'Armor').cyl(.5, loc[2] - base, loc=(loc[0], loc[1], (loc[2] + base) / 2), seg=10, bevel=.03, bseg=1)
        autocannon(a, mount, loc, length=2.4, size=(1.3, 1.5, .62))


def _platform(a, lift, wreck):
    _suffixed(a)
    rng = random.Random(2208)
    _hull(a, lift, wreck, rng)
    _telescope(a, lift, wreck)
    _racks(a, lift, wreck)
    _truss(a, lift, wreck)
    _radiators(a, lift, wreck)
    _drive(a, lift, wreck)
    r = FWD[2]
    for name in ('Thruster_fl', 'Thruster_fr'):
        sx = 1 if orb.NODES[name][0] < 0 else -1          # right < 0 is Blender +X
        _rcs_pod(a, name, lift, (-sx * (4.5 - r + .2), 0, 0))
    for name in ('Thruster_rl', 'Thruster_rr'):
        sx = 1 if orb.NODES[name][0] < 0 else -1
        _rcs_pod(a, name, lift, (-sx * .7, 0, 0))
    orb._build_main_turret(a, orb._node('Turret', lift))
    orb._build_coilgun(a, 'Mount_gun', 'Muzzle_gun', '', orb._node('Mount_gun', lift), deployed=wreck)
    orb._build_coilgun(a, 'Mount_gun.001', 'Muzzle_gun.001', '_001', orb._node('Mount_gun.001', lift), deployed=wreck)
    orb._build_flak(a, 'Mount_mg', 'Muzzle_mg', '', orb._node('Mount_mg', lift), deployed=wreck)
    orb._build_flak(a, 'Mount_mg.001', 'Muzzle_mg.001', '_001', orb._node('Mount_mg.001', lift), deployed=wreck)
    orb._build_pd_laser(a, 'Pd_laser_l', orb._node('Pd_laser_l', lift))
    orb._build_pd_laser(a, 'Pd_laser_r', orb._node('Pd_laser_r', lift))
    orb._build_pod_bay(a, orb._node('Pod_bay', lift))
    orb._build_uplink(a, orb._node('Uplink', lift))
    # Columns under the mounts that stand proud of the hull: the flak on each module, the uplink's mast.
    _plinth(a, 'Mount_mg', lift, CORE_Z + FWD[2] + lift - .03)
    _plinth(a, 'Mount_mg.001', lift, AFT_Z + AFT[2] + lift - .03, width=.5)
    ux, uy, uz = orb._node('Uplink', lift)
    mast = a.part('Uplink_mast', 'Armor')
    mast.cyl(.32, uz - .6 - (AFT_Z + AFT[2] + lift - .03), loc=(ux, uy, (uz - .6 + AFT_Z + AFT[2] + lift - .03) / 2), seg=10,
             bevel=.02, bseg=1)
    _crash_sponsons(a, lift)
    if wreck:
        orb._crater_ring(a)
        for i, (right, forward, w, d) in enumerate(orb.DEBRIS):
            x, y, _z = orb._pos(right, forward)
            orb._debris_pile(a, x, y, w, d, 1.8, seed=300 + i)


def silver_bug(a):
    """Icarus, the orbital weapons platform: see the module docstring."""
    _platform(a, 0.0, False)


def silver_bug_wreck(a):
    """Icarus crashed, for its ground phase: see the module docstring."""
    _platform(a, orb.LIFT, True)


BUILDERS = {
    'silver_bug': (silver_bug, dict(ao_distance=.6, ground=False)),
    'silver_bug_wreck': (silver_bug_wreck, dict(ao_distance=1.1, grime_height=1.2)),
}
