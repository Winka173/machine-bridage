"""New Machine Brigade vehicles (round 5), built with frontier_kit.

Conventions are those of mb_vehicles.py: metres, +Z up, Blender -Y is the front and +X the vehicle's
left, origin on the ground under the hull centre, wheels and tracks touching z = 0. Touching parts
overlap or stand at least 1 cm apart, never face to face (coplanar faces z-fight).

  * vbied: "Iron Coffin", an up-armoured suicide pickup (Mosul 2016-17 SVBIED): welded slab plates
    bolted over the whole body, vision slits instead of glass, a V-wedge ram at the front and skirts
    over the wheels. The caged bed holds the charge: oil drums and gas cylinders strapped together
    with detonator wiring. `Turret` is the small roof camera; `Muzzle_main` sits at the tip of the
    ram, where the charge is delivered.
  * zu23_technical: Hilux-style pickup with a ZU-23-2 twin 23 mm anti-aircraft gun on the bed. The
    gun turns on `Turret`; its two barrels are `Main_cannon` (left) and `Main_cannon_2` (right) with
    slotted flash hiders (`Muzzle_brake`, `Muzzle_brake_2`), and `Muzzle_main` sits between the two
    tips. Gunner's seat and ZAP-23 sight, ammunition boxes on both sides, a gun shield; roll bar,
    spare tyre on the bonnet, canvas and jerrycans.
  * smoke_carrier: M58 Wolf smoke generator carrier on the M113 hull: the rear deck carries the
    generator module (turbine housing, fog-oil tanks and two tall exhaust stacks leaning back),
    smoke-grenade dischargers sit on the front corners, and the commander's cupola is the `Turret`
    with an M2 .50 heavy machine gun behind an ACAV shield (`Main_cannon`, `Muzzle_main`).
"""
import math

from mathutils import Euler, Matrix, Vector

from frontier_kit import chamfered
from mb_support import _along, _plane
from mb_vehicles import (ACROSS, FORWARD, R90, _antenna, _barrel, _cable, _flank, _frame, _glacis, _grille_frame,
                         _hatch, _headlight, _jerrycans, _periscopes, _rail, _roll, _skirt, _taillight, tracks)

TAU = math.tau


# ----------------------------------------------------------------------------- helpers
def _in(m, euler=(0, 0, 0)):
    """Euler rotation of a primitive rotated by `euler` inside frame m."""
    return (m.to_3x3() @ Euler(euler, 'XYZ').to_matrix()).to_euler('XYZ')


def _tyre(a, m, r, width, lugs=16, seg=16, rim='Armor', nuts=6, parent=None):
    """Off-road tyre in frame m (axle along local X, outer face towards local +X, centre at the
    origin): a rubber carcass, staggered tread lugs whose outer faces lie on radius r (one of them
    straight down, so a road wheel centred at z = r touches the ground), a painted rim, a steel hub
    and lug nuts."""
    centre = m @ Vector((0, 0, 0))
    axle = _in(m, ACROSS)
    carcass = r - .03
    a.part('Tyres', 'Rubber', parent).cyl(carcass, width, loc=centre, rot=axle, seg=seg, bevel=carcass * .14, bseg=1)
    tread = a.part('Tread', 'Rubber', parent)
    for k in range(lugs):
        ang = -R90 + k * TAU / lugs
        off = (-1 if k % 2 == 0 else 1) * width * .2
        rr = r - .02
        tread.box((width * .54, .085, .04), loc=m @ Vector((off, math.cos(ang) * rr, math.sin(ang) * rr)),
                  rot=_in(m, (ang - R90, 0, 0)), bevel=0)
    a.part('Rims', rim, parent).cyl(r * .52, width + .03, loc=centre, rot=axle, seg=12, bevel=.015, bseg=1)
    steel = a.part('Hubs', 'Steel', parent)
    steel.cyl(r * .19, width + .09, loc=centre, rot=axle, seg=8, bevel=0)
    for k in range(nuts):
        ang = k * TAU / nuts
        steel.cyl(.022, .03, loc=m @ Vector((width / 2 + .025, math.cos(ang) * r * .3, math.sin(ang) * r * .3)),
                  rot=axle, seg=6, bevel=0)


def _road_tyre(a, s, x, y, r, width, **kw):
    """Tyre on side s (+1 left, -1 right) touching the ground, outer face outwards."""
    _tyre(a, _frame((s * x, y, r), (0, 0, 0 if s > 0 else math.pi)), r, width, **kw)


def _box_ring(x, z, y0, y1):
    """Horizontal rectangle (loft section) at height z: x half-width, y from y0 to y1."""
    return [(-x, y0, z), (x, y0, z), (x, y1, z), (-x, y1, z)]


def _weld(a, points, parent=None, r=.013):
    """Weld bead along a polyline (a dark square-section run)."""
    a.part('Welds', 'Charred', parent).tube(points, r, seg=4)


def _frame_bolts(a, f, points, r=.024, h=.03, parent=None):
    """Bolt heads on the plane of frame f at local (u, v, w) points, their axes along local Z."""
    rot = f.to_euler('XYZ')
    a.part('Bolts', 'Steel', parent).bolts([f @ Vector(p) for p in points], r=r, h=h, rot=rot, seg=5, bevel=0)


def _drum(a, x, y, z, mat, r=.27, h=.86):
    """Standing 200-litre oil drum: rolling hoops, rims top and bottom, two bungs in the lid."""
    a.part('Drums_' + mat, mat).lathe([(r * .95, 0), (r, .025), (r, h * .32), (r + .014, h * .33), (r, h * .345),
                                       (r, h * .655), (r + .014, h * .67), (r, h * .685), (r, h - .025),
                                       (r * .95, h)], loc=(x, y, z), seg=14)
    steel = a.part('Drum_bungs', 'Steel')
    steel.cyl(.035, .03, loc=(x + r * .55, y - r * .25, z + h + .005), seg=6, bevel=0)
    steel.cyl(.022, .03, loc=(x - r * .55, y + r * .2, z + h + .005), seg=6, bevel=0)


def _gas_cylinder(a, loc, s, mat, r=.15, length=.62):
    """LPG cylinder lying across the bed with its base at loc: domed ends, a foot ring and a valve
    inside its guard collar, the valve end pointing towards -s * X (the middle of the bed). Returns
    the point where a wire meets the valve."""
    x, y, z = loc
    a.part('Gas_cylinders_' + mat, mat).lathe(
        [(r * .35, 0), (r * .8, .025), (r, .08), (r, length - .08), (r * .8, length - .03), (r * .35, length)],
        loc=(x, y, z), rot=(0, -s * R90, 0), seg=12)          # lathe axis (local Z) -> -s * X
    tip = Vector((x - s * length, y, z))
    a.part('Gas_valves', 'Steel').cyl(.035, .08, loc=tip + Vector((-s * .03, 0, 0)), rot=ACROSS, seg=6, bevel=0)
    a.part('Gas_collars', 'Steel').cyl(r * .62, .05, loc=tip + Vector((-s * .015, 0, 0)), rot=ACROSS, seg=10,
                                       bevel=0)
    a.part('Gas_rings', 'Armor').cyl(r * .8, .03, loc=(x - s * .005, y, z), rot=ACROSS, seg=10, bevel=0)
    return tip + Vector((-s * .07, 0, 0))


def _discharger(a, s, x, y, z, count=4, gap=.085, r=.045, depth=.2):
    """Smoke-grenade discharger bank on side s standing on a roof at height z: a bracket block and
    `count` tubes angled up, forwards and outwards, each with a dark bore."""
    a.part('Discharger_mounts', 'Armor').box((count * gap + .08, .18, .08),
                                             loc=(s * (x + (count - 1) * gap / 2), y, z + .03), bevel=.01, seg=1)
    tube = a.part('Dischargers', 'Armor')
    bore = a.part('Discharger_bores', 'Undercarriage')
    rot = (.6, 0, s * .4)
    axis = Euler(rot, 'XYZ').to_matrix() @ Vector((0, 0, 1))
    for i in range(count):
        c = Vector((s * (x + i * gap), y, z + .1))
        tube.cyl(r, depth, loc=c, rot=rot, seg=8, bevel=0)
        bore.cyl(r * .72, .02, loc=c + axis * (depth / 2 + .002), rot=rot, seg=8, bevel=0)


# ----------------------------------------------------------------------------- VBIED
def vbied(a):
    """Up-armoured suicide pickup ("Iron Coffin", Mosul 2016-17): a truncated-wedge cab of welded slab
    plates with bolted door and bonnet plates, vision slits under visor lips, a V ram at the front,
    three-panel skirts over the tyres, and a bed walled in steel under a welded bar cage holding
    the charge (four oil drums and six gas cylinders strapped together, a detonator box with its
    wiring and a command wire into the cab). A camera on the roof (`Turret`), a short whip antenna
    and rust patches."""
    body = a.part('Body', 'Team')
    plates = a.part('Plates', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    chassis = a.part('Chassis', 'Undercarriage')
    rust = a.part('Rust', 'Rust')
    # Running gear: the ladder frame, axles and four tyres behind the skirts.
    chassis.box((1.3, 4.4, .22), loc=(0, .05, .55), bevel=.04)
    for y in (-1.5, 1.55):
        chassis.box((1.5, .16, .14), loc=(0, y, .4), bevel=.02, seg=1)
        for s in (-1, 1):
            _road_tyre(a, s, .82, y, .4, .3, lugs=12, seg=14, nuts=5)
    # Lower hull (bonnet and cab tub) and the cab: a truncated wedge of slab plates.
    body.prism([(-2.34, .56), (-2.42, .98), (-1.36, 1.17), (.44, 1.17), (.44, .56)], 1.94, bevel=.05)
    lo, hi = (.97, 1.12), (.74, 1.9)
    face = ((-1.4, 1.12), (-.8, 1.9))
    body.loft([_box_ring(lo[0], lo[1], face[0][0], .44), _box_ring(hi[0], hi[1], face[1][0], .3)], bevel=.04)
    # Front plate over the windscreen with two vision slits under visor lips.
    gy, gz, grot = _glacis(*face, .48, .015)
    armor.prism([(-.93, -.44), (.93, -.44), (.75, .44), (-.75, .44)], .05, loc=(0, gy, gz), rot=(grot, 0, 0),
                axis='Z', bevel=.012)
    front = _plane((0, gy, gz), (1, 0, 0), (0, face[1][0] - face[0][0], face[1][1] - face[0][1]))
    frot = front.to_euler('XYZ')
    slits = a.part('Slits', 'Glass')
    recess = a.part('Slit_recess', 'Undercarriage')
    for x in (-.31, .31):
        recess.box((.52, .15, .02), loc=front @ Vector((x, .16, .03)), rot=frot, bevel=0)
        slits.box((.44, .06, .02), loc=front @ Vector((x, .16, .04)), rot=frot, bevel=0)
        steel.box((.58, .04, .07), loc=front @ Vector((x, .25, .055)), rot=frot, bevel=0)      # visor lip
    _frame_bolts(a, front, [(u, -.38, .025) for u in (-.84, -.3, .3, .84)] + [(u, .38, .025) for u in (-.68, .68)] +
                 [(u, 0, .025) for u in (-.8, .8)])
    # Side plates over the doors, a slit above each; bolts round the plates.
    lean = math.atan2(lo[0] - hi[0], hi[1] - lo[1])

    def flank_frame(s, t, y, out):
        x, z, _ = _flank(lo, hi, t, out)
        return _plane((s * x, y, z), (0, s, 0), (-s * math.sin(lean), 0, math.cos(lean)))
    for s in (-1, 1):
        side = flank_frame(s, .34, -.46, .02)
        plates.box((.96, .5, .05), loc=side @ Vector((0, 0, 0)), rot=side.to_euler('XYZ'), bevel=.012, seg=1)
        _frame_bolts(a, side, [(u, v, .025) for u in (-.43, -.14, .14, .43) for v in (-.2, .2)])
        slit = flank_frame(s, .66, -.46, 0)
        srot = slit.to_euler('XYZ')
        recess.box((.5, .14, .02), loc=slit @ Vector((0, 0, .005)), rot=srot, bevel=0)
        slits.box((.42, .055, .02), loc=slit @ Vector((0, 0, .015)), rot=srot, bevel=0)
        steel.box((.56, .04, .06), loc=slit @ Vector((0, .1, .025)), rot=srot, bevel=0)
        # Rear quarter: a rusty patch plate.
        rq = flank_frame(s, .3, .16, .02)
        rust.box((.34, .42, .03), loc=rq @ Vector((0, 0, 0)), rot=rq.to_euler('XYZ'), bevel=.008, seg=1)
        _frame_bolts(a, rq, [(u, v, .015) for u in (-.13, .13) for v in (-.16, .16)], r=.02)
        # Welds: A and C pillars, roof edges, the cab's foot along the hull.
        _weld(a, [(s * lo[0], face[0][0], lo[1]), (s * hi[0], face[1][0], hi[1])])
        _weld(a, [(s * lo[0], .44, lo[1]), (s * hi[0], .3, hi[1])])
        _weld(a, [(s * hi[0], face[1][0], hi[1]), (s * hi[0], .3, hi[1])])
        _weld(a, [(s * .975, -2.3, 1.15), (s * .975, .42, 1.15)])
        # Mirrors on stubby welded arms, caged headlights on the bonnet, tail lights on the tail plate.
        steel.tube([(s * .95, -1.28, 1.3), (s * 1.0, -1.33, 1.35)], .016, seg=4)
        armor.box((.13, .045, .16), loc=(s * 1.03, -1.34, 1.37), bevel=.01, seg=1)
        a.part('Mirror_glass', 'Glass').box((.1, .02, .12), loc=(s * 1.03, -1.315, 1.37), bevel=0)
        _headlight(a, s * .66, -2.3, 1.09)
        _taillight(a, s * .7, 2.435, 1.2)
        # Skirts over the tyres on brackets from the hull.
        _skirt(a, s, 1.06, -2.12, 2.32, .3, 1.02, 3, mat='Team', thick=.07, gap=.04)
        for y in (-1.05, .3, 1.0, 2.1):
            steel.box((.1, .08, .07), loc=(s * .99, y, .96), bevel=0)
    _weld(a, [(-hi[0], face[1][0], hi[1]), (hi[0], face[1][0], hi[1])])
    rust.box((.02, .5, .28), loc=(1.1, .72, .6), bevel=0)                                   # skirt rust
    rust.box((.02, .36, .2), loc=(-1.1, -1.6, .8), bevel=0)
    # Bonnet plate with bolts and a welded air scoop.
    hood = ((-2.42, .98), (-1.36, 1.17))
    hy, hz, hrot = _glacis(*hood, .5, .02)
    armor.box((1.86, 1.02, .05), loc=(0, hy, hz), rot=(hrot, 0, 0), bevel=.012, seg=1)
    bonnet = _plane((0, hy, hz), (1, 0, 0), (0, hood[1][0] - hood[0][0], hood[1][1] - hood[0][1]))
    brot = bonnet.to_euler('XYZ')
    _frame_bolts(a, bonnet, [(u, v, .025) for u in (-.88, .88) for v in (-.42, -.14, .14, .42)] +
                 [(u, -.46, .025) for u in (-.5, 0, .5)])
    plates.box((.56, .42, .14), loc=bonnet @ Vector((0, .14, .08)), rot=brot, bevel=.02, seg=1)
    chassis.grille(.44, .1, loc=bonnet @ Vector((0, -.075, .08)), rot=brot, slats=2, depth=.03, thickness=.03)
    rust.box((.4, .3, .02), loc=bonnet @ Vector((-.58, -.28, .03)), rot=brot, bevel=0)
    # V ram: two raked plates meeting at a steel prow, a cutting edge and a top cap on each.
    ram = a.part('Ram', 'Armor')
    tip_y, cx, cy = -2.47, 1.02, -2.27
    zr, hr, tilt = .6, .8, -.32
    length = math.hypot(cx, cy - tip_y)
    yaw = math.atan2(cy - tip_y, cx)
    for s in (-1, 1):
        p = _frame((s * cx / 2, (tip_y + cy) / 2, zr), (tilt, 0, s * yaw))
        rot = p.to_euler('XYZ')
        ram.box((length + .1, .07, hr), loc=p @ Vector((0, 0, 0)), rot=rot, bevel=.015, seg=1)
        steel.box((length + .1, .1, .06), loc=p @ Vector((0, -.015, -hr / 2 + .03)), rot=rot, bevel=0)
        steel.box((length + .06, .1, .05), loc=p @ Vector((0, .01, hr / 2)), rot=rot, bevel=0)
        _frame_bolts(a, p @ _frame((0, -.035, 0), (R90, 0, 0)), [(u, v, 0) for u in (-.3, .1, .4) for v in (-.18, .2)],
                     r=.026)
        if s > 0:
            rust.box((.3, .02, .2), loc=p @ Vector((.12, -.04, .1)), rot=rot, bevel=0)
        chassis.box((.1, .24, .1), loc=(s * .45, -2.24, .5), bevel=0)                         # ram braces
    prow = (Matrix.Rotation(tilt, 3, 'X') @ Matrix.Rotation(math.pi / 4, 3, 'Z')).to_euler('XYZ')
    steel.box((.15, .15, hr + .06), loc=(0, tip_y - .01, zr), rot=prow, bevel=0)
    # Bed walled in steel, a welded bar cage over it, the tail plate and the rear.
    body.shell(chamfered(1.94, 1.9, .06), .94, .07, loc=(0, 1.45, .56), floor=.36, bevel=.02)
    cage = a.part('Cage', 'Armor')
    bars = a.part('Cage_bars', 'Rust')
    zc = 1.92
    for x in (-.93, .93):
        for y in (.56, 1.45, 2.34):
            cage.box((.07, .07, zc - 1.46), loc=(x, y, (zc + 1.46) / 2), bevel=0)
        cage.box((.07, 1.85, .07), loc=(x, 1.45, zc), bevel=0)
    for y in (.56, 2.34):
        cage.box((1.93, .07, .07), loc=(0, y, zc), bevel=0)
    for x in (-.71, 0, .71):
        bars.box((.045, 1.74, .045), loc=(x, 1.45, zc + .005), bevel=0)
    for y in (1.2, 1.76):
        bars.box((1.8, .045, .045), loc=(0, y, zc + .04), bevel=0)
    for s in (-1, 1):
        _weld(a, [(s * .98, .52, 1.5), (s * .98, 2.38, 1.5)])
        plates.box((.05, .8, .4), loc=(s * .98, 1.0, 1.1), bevel=.012, seg=1)                 # bed side plates
        _frame_bolts(a, _plane((s * 1.005, 1.0, 1.1), (0, s, 0), (0, 0, 1)),
                     [(u, v, 0) for u in (-.34, 0, .34) for v in (-.15, .15)], r=.022)
    rust.box((.02, .6, .3), loc=(.975, 1.95, 1.2), bevel=0)
    plates.box((1.5, .05, .5), loc=(0, 2.41, 1.05), bevel=.012, seg=1)                        # tail plate
    _frame_bolts(a, _plane((0, 2.435, 1.05), (-1, 0, 0), (0, 0, 1)),
                 [(u, v, 0) for u in (-.68, -.23, .23, .68) for v in (-.2, .2)], r=.022)
    steel.box((.2, .1, .12), loc=(0, 2.44, .6), bevel=.02, seg=1)                             # tow hook
    steel.cyl(.045, .4, loc=(-.55, 2.28, .42), rot=FORWARD, seg=8, bevel=0)                  # exhaust
    # The charge: oil drums strapped in a block at the back, gas cylinders stacked across the front.
    for (x, y), mat in (((.43, 1.48), 'BarrelRed'), ((-.43, 1.48), 'ContainerBlue'), ((.43, 2.04), 'Charred'),
                        ((-.43, 2.04), 'BarrelRed')):
        _drum(a, x, y, .92, mat)
    straps = a.part('Straps', 'Charred')
    for z in (1.12, 1.52):
        straps.tube([(-.6, 1.195, z), (.6, 1.195, z), (.715, 1.3, z), (.715, 2.22, z), (.6, 2.318, z),
                     (-.6, 2.318, z), (-.715, 2.22, z), (-.715, 1.3, z), (-.6, 1.195, z)], .014, seg=4)
    valves = []
    for y, z, mats in ((.75, 1.06, ('Fuel', 'Hazard')), (1.03, 1.06, ('Hazard', 'Fuel')),
                       (.89, 1.32, ('Fuel', 'Fuel'))):
        for s, mat in zip((-1, 1), mats):
            valves.append(_gas_cylinder(a, (s * .84, y, z), s, mat))
    for x in (-.5, .5):
        straps.tube([(x, .585, .93), (x, .585, 1.2), (x, .7, 1.49), (x, 1.08, 1.49), (x, 1.19, 1.2), (x, 1.19, .93)],
                    .014, seg=4)
    straps.box((.08, .06, .05), loc=(.5, .89, 1.5), bevel=0)                                  # ratchet buckle
    a.part('Sacks', 'Sandbag').box((.46, .3, .1), loc=(-.43, 1.96, 1.83), rot=(0, 0, .2), bevel=.04, seg=1)
    a.part('Sacks', 'Sandbag').box((.42, .28, .09), loc=(-.4, 2.12, 1.9), rot=(0, .1, -.3), bevel=.035, seg=1)
    # Detonator box on the front-left drum, red and yellow wiring to every drum and cylinder, and the
    # command wire into the cab.
    det = Vector((.43, 1.44, 1.825))
    armor.box((.22, .15, .1), loc=det, bevel=.015, seg=1)
    a.part('Detonator_led', 'LavaGlow').box((.04, .02, .03), loc=det + Vector((-.05, -.08, .02)), bevel=0)
    steel.box((.03, .03, .03), loc=det + Vector((.06, -.08, .02)), bevel=0)
    red = a.part('Wires', 'BarrelRed')
    yellow = a.part('Wires_yellow', 'Hazard')
    for i, (x, y) in enumerate(((-.43, 1.48), (.43, 2.04), (-.43, 2.04))):
        end = Vector((x + .27 * .55, y - .27 * .25, 1.81))
        mid = (det + end) / 2 + Vector((0, 0, .05))
        (red if i % 2 == 0 else yellow).tube([det + Vector((0, .07, 0)), mid, end], .011, seg=4)
    for i, v in enumerate(valves):
        start = det + Vector((-.06 + .02 * i, -.07, -.02))
        mid = Vector(((v.x + start.x) / 2, (v.y + start.y) / 2, max(v.z, 1.3) + .2))
        (yellow if i % 2 == 0 else red).tube([start, mid, v], .01, seg=4)
    red.tube([det + Vector((-.1, 0, 0)), Vector((.36, 1.0, 1.62)), Vector((.32, .62, 1.52)), Vector((.3, .46, 1.4))],
             .013, seg=4)
    # Roof: a patch plate and welds, a small hatch, the whip antenna, the receiver and the camera.
    plates.box((1.2, .5, .04), loc=(0, .02, 1.9), bevel=.01, seg=1)
    _weld(a, [(-.6, -.23, 1.915), (.6, -.23, 1.915)])
    armor.box((.44, .4, .05), loc=(.3, .0, 1.935), bevel=.01, seg=1)                          # roof hatch
    steel.box((.36, .06, .05), loc=(.3, .22, 1.95), bevel=0)
    steel.tube([(.2, -.12, 1.955), (.2, -.12, 2.0), (.4, -.12, 2.0), (.4, -.12, 1.955)], .012, seg=4)
    _antenna(a, None, -.52, .14, 1.9, .9)
    steel.box((.09, .09, .06), loc=(-.52, .14, 1.93), bevel=0)
    armor.box((.18, .12, .08), loc=(-.3, .16, 1.93), bevel=.01, seg=1)                        # receiver box
    red.tube([(-.3, .1, 1.95), (-.3, -.1, 1.925), (-.1, -.32, 1.925)], .01, seg=4)

    t = a.pivot('Turret', (0, -.5, 1.9))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(.12, .06, loc=(0, 0, .02), seg=10, bevel=0)                                      # pan base
    tsteel.cyl(.03, .14, loc=(0, 0, .12), seg=6, bevel=0)                                       # post
    tarm.box((.18, .3, .15), loc=(0, -.02, .25), bevel=.02, seg=1)                             # housing
    tarm.box((.22, .16, .02), loc=(0, -.13, .335), bevel=0)                                    # sun hood
    tarm.box((.08, .1, .08), loc=(.13, .02, .22), bevel=0)                                      # IR lamp
    a.part('Camera_lens', 'Glass', t).cyl(.05, .03, loc=(0, -.175, .25), rot=FORWARD, seg=10, bevel=0)
    a.part('Camera_lamp', 'Lamp', t).box((.06, .02, .06), loc=(.13, -.035, .22), bevel=0)
    # The charge goes off at the ram's tip, ahead of the camera.
    a.pivot('Muzzle_main', (0, -2.66 + .5, .6 - 1.9), t)


# ----------------------------------------------------------------------------- ZU-23-2 technical
# Fender flare (y offset, z) over a 0.4 m tyre: outer edge forwards, inner edge back.
FLARE = [(-.54, .7), (-.46, .88), (-.26, .99), (.26, .99), (.46, .88), (.54, .7), (.46, .7), (.39, .85), (.22, .94),
         (-.22, .94), (-.39, .85), (-.46, .7)]


def _zu23(a, loc):
    """ZU-23-2 twin 23 mm anti-aircraft gun on `Turret` at loc (the bed floor): traverse ring and
    platform, two side frames, the trunnion, two receivers with barrels (`Main_cannon`,
    `Main_cannon_2`) and slotted flash hiders, ammunition boxes outboard of both guns, a gun shield
    with ears and side wings, two seats, the ZAP-23 sight, handwheels and a firing pedal."""
    t = a.pivot('Turret', loc)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    frame = a.part('Gun_carriage', 'Team', t)
    tsteel.cyl(.6, .08, loc=(0, 0, .03), seg=20, bevel=.015, bseg=1)                          # traverse ring
    tarm.prism(chamfered(1.14, 1.3, .28), .08, loc=(0, .06, .1), axis='Z', bevel=.015)          # platform
    zb = 1.24                                                                                # bore axis
    for s in (-1, 1):
        frame.prism([(-.42, .12), (.36, .12), (.3, .62), (.14, 1.18), (-.16, 1.18), (-.32, .62)], .06,
                    loc=(s * .31, 0, 0), bevel=.015)                                          # side frames
        tsteel.bolts([(s * .345, y, z) for y, z in ((-.3, .3), (.24, .3), (0, .9))], r=.022, h=.02,
                     rot=(0, R90, 0), bevel=0)
    tsteel.cyl(.055, .76, loc=(0, 0, 1.1), rot=ACROSS, seg=10, bevel=0)                       # trunnion
    tarm.box((.3, .2, .5), loc=(0, .15, .4), bevel=.02, seg=1)                                 # centre column
    tips = []
    for s, suffix in ((1, ''), (-1, '_2')):
        x = s * .19
        tarm.box((.15, .9, .2), loc=(x, .12, zb), bevel=.02, seg=1)                            # receiver
        tsteel.box((.11, .5, .03), loc=(x, .2, zb + .11), bevel=0)                            # top cover
        tsteel.box((.03, .1, .06), loc=(x - s * .06, .45, zb + .12), bevel=0)                 # cocking lever
        a.part('Case_chutes', 'Undercarriage', t).box((.1, .16, .18), loc=(x, .22, zb - .16), rot=(.35, 0, 0),
                                                      bevel=0)
        tips.append(_barrel(a, t, start_y=-.33, length=1.8, radius=.034, height=zb, x=x, suffix=suffix, seg=10,
                            brake=(.1, .22, .1), style='flash', sleeve=(.07, .3, .05)))
        cannon = a.part(f'Main_cannon{suffix}', 'Steel', t)
        cannon.box((.025, .16, .025), loc=(x, -.95, zb + .075), bevel=0)                      # carrying handle
        for y in (-1.02, -.88):
            cannon.box((.02, .02, .05), loc=(x, y, zb + .045), bevel=0)
    a.pivot('Muzzle_main', (0, tips[0][1], tips[0][2]), t)
    # Ammunition boxes outboard of both guns, with lids, handles and feed chutes.
    for s in (-1, 1):
        a.part('Ammo_boxes', 'Crate', t).box((.2, .5, .32), loc=(s * .455, .08, 1.16), bevel=.02, seg=1)
        tarm.box((.22, .52, .04), loc=(s * .455, .08, 1.33), bevel=.01, seg=1)
        tsteel.box((.05, .16, .03), loc=(s * .455, .08, 1.36), bevel=0)
        tarm.box((.12, .2, .03), loc=(s * .315, .02, 1.3), rot=(0, s * .5, 0), bevel=0)
    # Gun shield: a lower plate under the barrels, ears beside them and wings folded back, all in one
    # plane leaning back 0.12 rad.
    shield = a.part('Gun_shield', 'Team', t)
    tilt = -.12

    def sy(z):
        return -.52 + (z - .66) * math.tan(-tilt)
    shield.box((1.16, .04, .64), loc=(0, sy(.84), .84), rot=(tilt, 0, 0), bevel=.012, seg=1)
    for s in (-1, 1):
        shield.box((.26, .04, .26), loc=(s * .46, sy(1.28), 1.28), rot=(tilt, 0, 0), bevel=.012, seg=1)
        shield.box((.035, .3, .64), loc=(s * .64, -.38, .84), rot=(0, 0, -s * .4), bevel=.01, seg=1)
        tsteel.box((.04, .3, .04), loc=(s * .31, -.38, .9), bevel=0)                          # shield struts
        tsteel.bolts([(s * u, sy(z) - .02, z) for u in (.2, .45) for z in (.6, 1.08)], r=.022, h=.02,
                     rot=(R90 + tilt, 0, 0), bevel=0)
    # Seats (gunner on the left with the ZAP-23 sight and handwheels, loader on the right).
    seats = a.part('Seats', 'Canvas', t)
    for s in (-1, 1):
        x = s * .44
        tsteel.cyl(.03, .44, loc=(x, .62, .35), seg=6, bevel=0)
        seats.box((.32, .3, .09), loc=(x, .62, .6), bevel=.03, seg=1)
        seats.box((.32, .08, .32), loc=(x, .76, .8), rot=(-.18, 0, 0), bevel=.03, seg=1)
        tsteel.box((.04, .04, .3), loc=(x, .74, .58), rot=(-.18, 0, 0), bevel=0)
        tsteel.box((.3, .04, .03), loc=(x, .3, .24), bevel=0)                                 # footrest
    tarm.box((.13, .22, .2), loc=(.46, .31, 1.5), bevel=.02, seg=1)                             # ZAP-23 sight
    tsteel.box((.04, .04, .08), loc=(.46, .31, 1.38), bevel=0)                                 # sight post
    sight = a.part('Sight', 'Glass', t)
    sight.box((.1, .02, .12), loc=(.46, .195, 1.51), bevel=0)
    sight.box((.1, .08, .02), loc=(.46, .28, 1.61), rot=(.5, 0, 0), bevel=0)                    # collimator
    tsteel.cyl(.03, .07, loc=(.46, .44, 1.52), rot=FORWARD, seg=8, bevel=0)                     # eyepiece
    tsteel.torus(.085, .012, loc=(.44, .37, .93), rot=(R90, 0, 0), seg=14, ring=4)            # traverse wheel
    tsteel.torus(.075, .012, loc=(.3, .5, .8), rot=(0, R90, 0), seg=14, ring=4)               # elevation wheel
    tsteel.cyl(.015, .12, loc=(.44, .31, .93), rot=FORWARD, seg=5, bevel=0)
    tsteel.cyl(.015, .12, loc=(.36, .5, .8), rot=ACROSS, seg=5, bevel=0)
    tsteel.box((.08, .12, .03), loc=(.44, .3, .17), rot=(.3, 0, 0), bevel=0)                    # firing pedal
    return t


def zu23_technical(a):
    """Hilux-style single-cab pickup carrying a ZU-23-2 twin 23 mm anti-aircraft gun on the bed: fender
    flares over tread tyres, a sloped greenhouse with glass, door lines, mirrors and steps, a bull bar,
    headlights and indicators, a braced roll bar with spot lamps, a spare tyre strapped on the bonnet,
    a canvas tarp on the cab roof and over the tailgate, jerrycans, ammunition crates and a whip antenna
    on the front bumper (outside the barrels' sweep)."""
    body = a.part('Body', 'Team')
    steel = a.part('Steel', 'Steel')
    armor = a.part('Armor', 'Armor')
    chassis = a.part('Chassis', 'Undercarriage')
    glass = a.part('Windows', 'Glass')
    trim = a.part('Trim', 'Armor')
    tarp = a.part('Tarp', 'Canvas')
    chassis.box((1.16, 4.6, .2), loc=(0, .02, .55), bevel=.04)
    for y in (-1.62, 1.46):
        chassis.box((1.44, .15, .13), loc=(0, y, .4), bevel=.02, seg=1)
        for s in (-1, 1):
            _road_tyre(a, s, .8, y, .4, .28)
            body.prism([(y + dy, z) for dy, z in FLARE], .2, loc=(s * .9, 0, 0), bevel=0)
            a.part('Mud_flaps', 'Rubber').box((.3, .03, .28), loc=(s * .8, y + .5, .62), bevel=0)
    # Body: bonnet and cab tub, a greenhouse tapering to the roof, the bed.
    body.prism([(-2.46, .64), (-2.52, .95), (-2.44, 1.08), (-1.3, 1.2), (.22, 1.2), (.22, .64)], 1.74, bevel=.05)
    lo, hi = (.86, 1.16), (.74, 1.84)
    ws = ((-1.3, 1.16), (-.64, 1.84))
    body.loft([_box_ring(lo[0], lo[1], ws[0][0], .22), _box_ring(hi[0], hi[1], ws[1][0], .14)], bevel=.04)
    body.shell(chamfered(1.74, 2.2, .04), .6, .06, loc=(0, 1.38, .72), floor=.12, bevel=.02)
    # Glass: windscreen, door windows, rear window; wipers.
    gy, gz, grot = _glacis(*ws, .52, .012)
    glass.box((1.38, .62, .03), loc=(0, gy, gz), rot=(grot, 0, 0), bevel=.01, seg=1)
    wy, wz, _ = _glacis(*ws, .14, .03)
    for x in (-.3, .3):
        steel.box((.5, .025, .02), loc=(x, wy, wz), rot=(grot, 0, .15), bevel=0)
    for s in (-1, 1):
        x, z, lean = _flank(lo, hi, .55, .012)
        glass.box((.03, .74, .32), loc=(s * x, -.38, z), rot=(0, -s * lean, 0), bevel=.01, seg=1)
    glass.box((1.2, .03, .34), loc=(0, .186, 1.55), rot=(.117, 0, 0), bevel=.01, seg=1)
    # Front: grille, headlights, indicators, bumper, bull bar with lamps, tow hooks.
    chassis.grille(.66, .2, loc=(0, -2.515, .86), rot=(.19, 0, 0), slats=3, depth=.05, thickness=.04)
    for s in (-1, 1):
        a.part('Light_housing', 'Armor').box((.34, .06, .16), loc=(s * .56, -2.49, .87), rot=(.19, 0, 0), bevel=.01,
                                             seg=1)
        a.part('Lamps', 'Lamp').box((.28, .03, .1), loc=(s * .56, -2.52, .87), rot=(.19, 0, 0), bevel=0)
        a.part('Indicators', 'Alloy').box((.08, .03, .08), loc=(s * .8, -2.51, .87), rot=(.19, 0, 0), bevel=0)
        steel.box((.12, .12, .1), loc=(s * .4, -2.58, .52), bevel=0)                          # tow hooks
        a.part('Lamps', 'Lamp').cyl(.06, .05, loc=(s * .42, -2.66, 1.14), rot=FORWARD, seg=10, bevel=0)
        a.part('Light_housing', 'Armor').cyl(.075, .08, loc=(s * .42, -2.62, 1.14), rot=FORWARD, seg=10, bevel=0)
    steel.box((1.84, .14, .18), loc=(0, -2.56, .66), bevel=.03)                               # bumper
    _rail(a, [(-.66, -2.58, .75), (-.66, -2.62, .84), (-.66, -2.62, 1.08), (.66, -2.62, 1.08), (.66, -2.62, .84),
              (.66, -2.58, .75)], r=.03)
    _rail(a, [(-.66, -2.62, .96), (.66, -2.62, .96)], r=.022)
    for x in (-.22, .22):
        _rail(a, [(x, -2.62, .75), (x, -2.62, 1.08)], r=.022)
    # Sides: door shut lines, handles, a body crease, steps, mirrors, a fuel filler.
    for s in (-1, 1):
        for y in (-1.02, .16):
            trim.box((.02, .025, .5), loc=(s * .872, y, .93), bevel=0)
        trim.box((.02, 4.9, .025), loc=(s * .872, -.03, 1.0), bevel=0)
        steel.box((.03, .14, .04), loc=(s * .885, .0, 1.08), bevel=0)
        steel.box((.14, 1.0, .04), loc=(s * .92, -.42, .58), bevel=0)
        for y in (-.8, -.05):
            steel.box((.1, .04, .08), loc=(s * .86, y, .6), bevel=0)
        steel.tube([(s * .84, -1.1, 1.28), (s * .98, -1.16, 1.32)], .016, seg=4)
        armor.box((.16, .05, .2), loc=(s * 1.0, -1.18, 1.34), bevel=.01, seg=1)
        a.part('Mirror_glass', 'Glass').box((.13, .02, .16), loc=(s * 1.0, -1.152, 1.34), bevel=0)
    steel.cyl(.05, .03, loc=(.875, 2.0, 1.1), rot=ACROSS, seg=10, bevel=0)                  # fuel filler
    # Bed: rail caps, stake pockets, tailgate, tail lights, bumper, exhaust.
    for s in (-1, 1):
        armor.box((.09, 2.2, .04), loc=(s * .845, 1.38, 1.33), bevel=0)
        for y in (.5, 1.38, 2.26):
            trim.box((.1, .1, .05), loc=(s * .845, y, 1.345), bevel=0)
        _taillight(a, s * .72, 2.48, 1.05)
    armor.box((1.74, .04, .04), loc=(0, 2.475, 1.33), bevel=0)
    trim.box((1.3, .02, .02), loc=(0, 2.487, 1.18), bevel=0)
    trim.box((1.3, .02, .02), loc=(0, 2.487, .88), bevel=0)
    steel.box((.3, .04, .05), loc=(0, 2.5, 1.23), bevel=0)                                     # tailgate handle
    steel.box((1.8, .12, .14), loc=(0, 2.52, .66), bevel=.03)                                 # rear bumper
    steel.box((.1, .1, .1), loc=(0, 2.58, .6), bevel=0)                                        # tow ball
    steel.cyl(.04, .5, loc=(-.45, 2.32, .48), rot=FORWARD, seg=8, bevel=0)                    # exhaust
    # Roll bar behind the cab, braced to the bed, with two spot lamps below the barrels' sweep.
    steel.tube([(-.8, .38, 1.3), (-.8, .38, 1.96), (.8, .38, 1.96), (.8, .38, 1.3)], .045, seg=8)
    for s in (-1, 1):
        steel.tube([(s * .8, .4, 1.88), (s * .8, .92, 1.31)], .032, seg=6)
        a.part('Light_housing', 'Armor').box((.16, .08, .13), loc=(s * .36, .31, 1.86), bevel=.01, seg=1)
        a.part('Lamps', 'Lamp').box((.12, .02, .09), loc=(s * .36, .265, 1.86), bevel=0)
    # Spare tyre strapped flat on the bonnet.
    hood = ((-2.44, 1.08), (-1.3, 1.2))
    hy, hz, hrot = _glacis(*hood, .44, .11)
    top = _frame((0, hy, hz), (hrot, 0, 0))
    _tyre(a, top @ _frame((0, 0, 0), (0, -R90, 0)), .38, .24, lugs=16, nuts=5)
    for x in (-.22, .22):
        steel.box((.06, .82, .02), loc=top @ Vector((x, 0, .125)), rot=(hrot, 0, 0), bevel=0)   # straps
        for d in (-1, 1):
            steel.box((.06, .02, .25), loc=top @ Vector((x, d * .4, .0)), rot=(hrot, 0, 0), bevel=0)
    # Canvas: a folded tarp and its roll on the cab roof, a sheet over the tailgate, a roll in the bed.
    tarp.box((1.3, .52, .06), loc=(0, -.28, 1.855), bevel=.025, seg=1)
    _roll(a, (0, .02, 1.9), 1.3, r=.07)
    for x in (-.35, .35):
        a.part('Straps', 'Undercarriage').box((.05, .56, .07), loc=(x, -.28, 1.86), bevel=0)
    tarp.box((.9, .3, .04), loc=(.2, 2.36, 1.345), rot=(0, 0, .03), bevel=.015, seg=1)
    tarp.box((.9, .04, .3), loc=(.2, 2.52, 1.2), rot=(-.12, 0, .03), bevel=.015, seg=1)
    _roll(a, (0, .5, .94), .6, r=.11)
    # Bed stowage low under the gun's sweep: 23 mm ammunition crates at the front, jerrycans at the back.
    for x in (.55, -.55):
        a.part('Crates', 'Crate').box((.3, .44, .24), loc=(x, .6, .95), bevel=.02, seg=1)
        steel.box((.32, .05, .03), loc=(x, .6, 1.085), bevel=0)
    a.part('Crates', 'Crate').box((.28, .4, .2), loc=(.55, .62, 1.17), rot=(0, 0, .12), bevel=.02, seg=1)
    _jerrycans(a, (.55, 2.22, .84), 2, axis='x', mat='Crate')
    _jerrycans(a, (-.55, 2.22, .84), 2, axis='x', mat='Hazard')
    # Whip antenna on the front bumper corner, clear of the barrels.
    _antenna(a, None, -.8, -2.56, .75, 1.5)
    steel.box((.08, .08, .08), loc=(-.8, -2.56, .77), bevel=0)
    _zu23(a, (0, 1.45, .84))


# ----------------------------------------------------------------------------- M58 Wolf
def smoke_carrier(a):
    """M58 Wolf smoke generator carrier (M113 hull): front sprockets, a trim vane on the glacis,
    headlights in guards, smoke-grenade dischargers on the front corners, the driver's hatch with
    vision blocks, the engine grille and side exhaust; the generator module on the rear deck (a
    housing with access panels and a louvred rear, a turbine with a bell-mouth intake, two tall
    exhaust stacks leaning back with sooty outlets, and fog-oil tanks with hazard bands on cradles),
    jerrycans, tow cables, antennas and the rear ramp. The commander's cupola is the `Turret`, with an
    M2 behind an ACAV shield."""
    tracks(a, 1.02, 4.4, .72, .25, 5, .42, belt_width=.48, wheel_seg=12, lean=True, sprocket=-1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Deck', 'Undercarriage')
    hull.prism([(-2.2, .44), (-2.36, .95), (2.26, .95), (2.26, .44)], 1.62, bevel=.05)     # belly
    nose, brow = (-2.48, 1.2), (-1.9, 1.82)
    hull.prism([(-2.38, .88), nose, brow, (2.3, 1.82), (2.3, .88)], 2.62, bevel=.06)
    gy, gz, grot = _glacis(nose, brow, .42, .02)
    armor.box((1.8, .5, .05), loc=(0, gy, gz), rot=(grot, 0, 0), bevel=.015, seg=1)       # trim vane
    vane = _plane((0, gy, gz), (1, 0, 0), (0, brow[0] - nose[0], brow[1] - nose[1]))
    _frame_bolts(a, vane, [(u, v, .025) for u in (-.8, -.4, 0, .4, .8) for v in (-.2, .2)], r=.022)
    for s in (-1, 1):
        _headlight(a, s * 1.02, -2.14, 1.66)
        steel.box((.12, .12, .12), loc=(s * .6, -2.43, .95), bevel=.02, seg=1)            # tow hooks
        _taillight(a, s * 1.12, 2.3, 1.62)
        steel.box((.1, .12, .08), loc=(s * .8, 2.35, 1.7), bevel=.01, seg=1)             # ramp hinges
        armor.box((.03, 4.2, .06), loc=(s * 1.315, -.05, 1.76), bevel=0)                  # top edge strip
        armor.box((.08, 4.2, .05), loc=(s * 1.32, -.05, .895), bevel=0)                   # lip over the tracks
        _discharger(a, s, .9, -1.78, 1.82)
        _cable(a, [(s * 1.315, -1.55, 1.25), (s * 1.315, .3, 1.25), (s * 1.315, 1.9, 1.25)])
        steel.box((.1, .1, .06), loc=(s * 1.2, 2.2, 1.84), bevel=0)                       # lifting eyes
        steel.bolts([(s * 1.312, y, 1.68) for y in (-1.5, -.9, -.3, .3, .9, 1.5, 2.1)], r=.022, h=.02,
                    rot=(0, R90, 0), seg=5, bevel=0)                                      # side plate bolts
        for y in (-1.75, -1.35):                                                           # footholds
            steel.box((.05, .16, .03), loc=(s * 1.32, y, 1.05), bevel=0)
    steel.cyl(.07, .03, loc=(1.315, 1.95, 1.45), rot=ACROSS, seg=10, bevel=0)             # fuel filler
    armor.box((.03, .36, .26), loc=(-1.318, 1.7, 1.42), bevel=.008, seg=1)               # access plate
    # Driver's hatch and vision blocks on the left, the engine grille and exhaust on the right.
    _hatch(a, .62, -1.3, 1.82, .27)
    _periscopes(a, [(.62 + math.cos(ang) * .36, -1.3 + math.sin(ang) * .36, 1.82, ang + R90)
                    for ang in (-R90 - .55, -R90, -R90 + .55, 0)])
    dark.grille(.66, .46, loc=(-.6, -1.58, 1.845), rot=(-R90, 0, 0), slats=5, depth=.06, thickness=.04)
    _grille_frame(a, -.6, -1.58, 1.83, .66, .46, t=.05)
    armor.box((.05, .56, .34), loc=(-1.33, -1.0, 1.5), bevel=.012, seg=1)
    dark.grille(.44, .24, loc=(-1.35, -1.0, 1.5), rot=(0, 0, -R90), slats=3, depth=.025, thickness=.025)
    a.part('Soot', 'Charred').box((.02, .5, .16), loc=(-1.317, -1.0, 1.73), bevel=0)
    _rail(a, [(1.05, -1.0, 1.81), (1.05, -1.0, 1.88), (1.05, -.5, 1.88), (1.05, -.5, 1.81)])
    _jerrycans(a, (.95, -.05, 1.82), 2, axis='x', mat='Hazard')
    # Rear ramp with its door, the towing pintle and hooks, antennas at the rear corners.
    armor.box((1.9, .06, .96), loc=(0, 2.32, 1.3), bevel=.02, seg=1)
    armor.box((.7, .03, .72), loc=(.4, 2.355, 1.3), bevel=0)
    steel.box((.05, .05, .2), loc=(.12, 2.38, 1.32), bevel=0)
    steel.box((.2, .12, .14), loc=(0, 2.35, .95), bevel=0)
    for s in (-1, 1):
        steel.box((.12, .12, .12), loc=(s * .7, 2.35, .8), bevel=0)
        _antenna(a, None, s * 1.1, 2.16, 1.82, 1.3)
        steel.box((.09, .09, .06), loc=(s * 1.1, 2.16, 1.84), bevel=0)

    # Smoke generator module on the rear deck. The housing and tanks stay below the cupola gun's bore
    # (2.48 m); the turbine and stacks stand further back than the gun reaches.
    gen = a.part('Generator', 'Team')
    fuel = a.part('Fog_oil_tanks', 'Fuel')
    hazard = a.part('Hazard_bands', 'Hazard')
    pipe = a.part('Turbine', 'Pipe')
    armor.box((1.62, 1.92, .08), loc=(0, 1.22, 1.84), bevel=.02, seg=1)                     # skid
    gen.box((1.44, 1.7, .46), loc=(0, 1.2, 2.1), bevel=.05)                                  # housing
    for x in (-.34, .34):                                                                    # access panels
        armor.box((.6, .56, .03), loc=(x, .72, 2.335), bevel=.008, seg=1)
        steel.box((.2, .03, .02), loc=(x, .5, 2.355), bevel=0)
        steel.box((.12, .05, .03), loc=(x - .18, .98, 2.35), bevel=0)
        steel.box((.12, .05, .03), loc=(x + .18, .98, 2.35), bevel=0)
    dark.box((1.1, .02, .32), loc=(0, 2.055, 2.1), bevel=0)                                   # rear louvres
    dark.grille(1.02, .28, loc=(0, 2.075, 2.1), rot=(0, 0, math.pi), slats=5, depth=.04, thickness=.03)
    for z in (1.92, 2.28):
        armor.box((1.16, .04, .04), loc=(0, 2.07, z), bevel=0)
    for s in (-1, 1):
        steel.box((.03, .08, .05), loc=(s * .73, .45, 2.0), bevel=0)                          # latches
        steel.box((.03, .08, .05), loc=(s * .73, 1.9, 2.0), bevel=0)
    a.part('Labels', 'Hazard').box((.3, .02, .1), loc=(-.3, .345, 2.25), bevel=0)
    # Turbine intake (bell mouth with a guard) and the control panel on the housing front.
    steel.lathe([(.14, -.03), (.14, .06), (.17, .1), (.19, .12)], loc=(.36, .36, 2.08), rot=FORWARD, seg=14)
    dark.cyl(.13, .02, loc=(.36, .3, 2.08), rot=FORWARD, seg=14, bevel=0)
    steel.box((.36, .02, .02), loc=(.36, .25, 2.08), bevel=0)
    steel.box((.02, .02, .36), loc=(.36, .25, 2.08), bevel=0)
    armor.box((.36, .06, .24), loc=(-.34, .33, 2.07), bevel=.01, seg=1)
    a.part('Gauges', 'Glass').box((.2, .02, .08), loc=(-.34, .295, 2.1), bevel=0)
    a.part('Panel_lamp', 'Alloy').box((.04, .02, .04), loc=(-.46, .295, 2.0), bevel=0)
    # Turbine on cradles along the top, its duct feeding the two exhaust stacks.
    tz = 2.6
    pipe.cyl(.26, .78, loc=(0, 1.62, tz), rot=FORWARD, seg=16, bevel=.03, bseg=1)
    for y in (1.36, 1.62, 1.88):
        armor.cyl(.275, .05, loc=(0, y, tz), rot=FORWARD, seg=16, bevel=0)
    pipe.lathe([(.2, -.03), (.2, .05), (.26, .1), (.29, .13)], loc=(0, 1.24, tz), rot=FORWARD, seg=16)
    dark.cyl(.19, .02, loc=(0, 1.17, tz), rot=FORWARD, seg=16, bevel=0)
    steel.box((.4, .02, .02), loc=(0, 1.12, tz), bevel=0)
    for y in (1.4, 1.85):
        armor.box((.5, .12, .14), loc=(0, y, 2.37), bevel=0)
    pipe.box((.8, .22, .32), loc=(0, 2.02, 2.52), bevel=.04)
    stacks = a.part('Stacks', 'Steel')
    for s in (-1, 1):
        base, bend, top = Vector((s * .26, 1.96, 2.48)), Vector((s * .3, 2.06, 2.74)), Vector((s * .36, 2.22, 3.2))
        stacks.tube([base, bend, top], .105, seg=12)
        d = (top - bend).normalized()
        loc, rot, length = _along(top - d * .04, top + d * .16)
        stacks.cyl(.11, length, r2=.15, loc=loc, rot=rot, seg=12, bevel=0)                  # flared outlet
        a.part('Soot', 'Charred').cyl(.135, .02, loc=top + d * .165, rot=rot, seg=12, bevel=0)
        for k in (.25, .65):
            armor.cyl(.12, .05, loc=bend.lerp(top, k), rot=rot, seg=12, bevel=0)             # clamp bands
        steel.limb(tuple(bend.lerp(top, .45)), (s * .5, 1.98, 2.32), .04, .04, bevel=0)      # stay
    # Fog-oil tanks lying along the deck edges on cradles, with hazard bands, fillers and feed pipes.
    for s in (-1, 1):
        x = s * 1.02
        fuel.lathe([(.12, 0), (.19, .04), (.22, .1), (.22, 1.6), (.19, 1.66), (.12, 1.7)], loc=(x, 2.05, 2.07),
                   rot=FORWARD, seg=14)
        hazard.cyl(.226, .08, loc=(x, 1.2, 2.07), rot=FORWARD, seg=14, bevel=0)
        for y in (.6, 1.8):
            armor.box((.5, .12, .22), loc=(x, y, 1.9), bevel=0)
            steel.cyl(.228, .04, loc=(x, y, 2.07), rot=FORWARD, seg=14, bevel=0)
        steel.cyl(.06, .06, loc=(x, .52, 2.28), seg=8, bevel=0)                              # filler cap
        for y in (1.0, 1.5):
            steel.tube([(s * .86, y, 1.98), (s * .79, y, 1.98), (s * .7, y, 2.0)], .03, seg=6)   # feed pipes
        _rail(a, [(s * .66, .5, 2.3), (s * .66, .5, 2.36), (s * .66, 1.1, 2.36), (s * .66, 1.1, 2.3)])

    # Commander's cupola (Turret): vision blocks, the hatch standing open behind, an M2 on a pintle
    # behind the ACAV front shield and side wings, its ammunition can on the left.
    cx, cy = -.05, -.62
    steel.cyl(.46, .08, loc=(cx, cy, 1.84), seg=18, bevel=.015, bseg=1)                    # cupola ring
    t = a.pivot('Turret', (cx, cy, 1.86))
    tarm = a.part('Cupola', 'Armor', t)
    tsteel = a.part('Cupola_steel', 'Steel', t)
    tarm.cyl(.4, .26, loc=(0, 0, .13), seg=16, bevel=.03, bseg=1)
    _periscopes(a, [(math.cos(ang) * .38, math.sin(ang) * .38, .2, ang + R90)
                    for ang in (-R90 - 1.2, -R90 - .6, -R90 + .6, -R90 + 1.2, 0, math.pi)], parent=t,
                size=(.09, .06, .07))
    lid = -2.05                                                        # hatch opened 117 degrees
    lc = Vector((0, .3 - .3 * math.cos(lid), .27 - .3 * math.sin(lid)))
    ln = Vector((0, -math.sin(lid), math.cos(lid)))                     # its outer face, facing back
    a.part('Cupola_hatch', 'Team', t).cyl(.3, .05, loc=lc, rot=(lid, 0, 0), seg=14, bevel=.012, bseg=1)
    tsteel.box((.3, .08, .07), loc=(0, .3, .28), bevel=0)
    h0 = lc + ln * .02
    tsteel.tube([h0 + Vector((-.12, 0, 0)), h0 + ln * .05 + Vector((-.12, 0, 0)), h0 + ln * .05 + Vector((.12, 0, 0)),
                 h0 + Vector((.12, 0, 0))], .012, seg=4)
    zb = .62
    tsteel.cyl(.04, .3, loc=(0, -.2, .39), seg=8, bevel=0)                                   # pintle
    tarm.box((.18, .3, .06), loc=(0, -.16, .54), bevel=0)                                    # cradle
    tsteel.box((.14, .5, .16), loc=(0, -.12, zb), bevel=.02, seg=1)                         # receiver
    tarm.box((.12, .26, .03), loc=(0, -.16, zb + .09), bevel=0)                              # feed cover
    tsteel.box((.12, .03, .1), loc=(0, .14, zb), bevel=0)
    for s in (-1, 1):
        tsteel.box((.03, .03, .13), loc=(s * .035, .17, zb - .02), rot=(.25, 0, 0), bevel=0)  # spade grips
    tsteel.cyl(.05, .22, loc=(0, -.47, zb), rot=FORWARD, seg=10, bevel=0)                  # barrel support
    tip = _barrel(a, t, start_y=-.37, length=1.02, radius=.037, height=zb, brake=(.09, .13, .09), style='flash',
                  seg=8)
    cannon = a.part('Main_cannon', 'Steel', t)
    cannon.box((.025, .16, .025), loc=(0, -.8, zb + .085), bevel=0)                          # carrying handle
    for y in (-.87, -.73):
        cannon.box((.02, .02, .06), loc=(0, y, zb + .05), bevel=0)
    a.pivot('Muzzle_main', tip, t)
    a.part('Ammo_can', 'Crate', t).box((.13, .28, .2), loc=(.17, -.1, zb - .05), bevel=.015, seg=1)
    tarm.box((.08, .08, .02), loc=(.1, -.12, zb + .06), rot=(0, .5, 0), bevel=0)
    # ACAV shield: front plates above and below a slot for the gun, and side wings, in a plane leaning
    # back 0.08 rad.
    shield = a.part('Gun_shield', 'Team', t)
    tilt = -.08

    def sy(z):
        return -.54 + (z - .5) * math.tan(-tilt)
    shield.box((.76, .035, .48), loc=(0, sy(.28), .28), rot=(tilt, 0, 0), bevel=.01, seg=1)
    shield.box((.76, .035, .24), loc=(0, sy(.85), .85), rot=(tilt, 0, 0), bevel=.01, seg=1)
    for s in (-1, 1):
        shield.box((.035, .44, .88), loc=(s * .486, -.346, .54), rot=(0, 0, -s * .5), bevel=.01, seg=1)
        shield.box((.12, .035, .22), loc=(s * .32, sy(.62), .62), rot=(tilt, 0, 0), bevel=0)   # slot sides
        tsteel.limb((s * .2, -.3, .27), (s * .3, sy(.45) + .02, .45), .03, .03, bevel=0)     # shield struts
    tsteel.bolts([(u, sy(z) - .018, z) for u in (-.3, -.1, .1, .3) for z in (.14, .86)], r=.02, h=.02,
                 rot=(R90 + tilt, 0, 0), bevel=0)


BUILDERS = {
    'vbied': (vbied, dict(ao_distance=.55, grime_height=.5)),
    'zu23_technical': (zu23_technical, dict(ao_distance=.55, grime_height=.5)),
    'smoke_carrier': (smoke_carrier, dict(ao_distance=.55, grime_height=.5)),
}
