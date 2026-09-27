"""New Machine Brigade vehicles (round 5): wheeled drone, laser and railgun carriers, built with frontier_kit
and the mb_vehicles* / mb_support helpers.

  * lancet_truck: 6x6 armoured truck (KamAZ Typhoon-K lineage) carrying loitering munitions (Lancet /
    Switchblade 600 style). A cab-over armoured crew cab, and on the bed a six-cell canister box (2 rows of
    3 square tubes with lids, one cell open) raised 25 degrees on a trainable launcher (`Turret`),
    `Muzzle_main` at the centre of the tube mouths; the dark `Box_face` plate behind the mouths is the
    launch face. A telescopic sensor mast with a stabilised camera ball and a ground-control station
    (tracking dish, sector panels, whips) stand at the front of the bed; a machine gun rides the cab roof
    (`Mount_mg` / `Muzzle_mg`).
  * shahed_truck: 6x6 bonneted truck carrying five Shahed-136 delta-wing drones on a stepped five-rail rack
    inclined 20 degrees on `Turret`; `Muzzle_main` at the front top of the rack, centred. Cab roof machine gun
    (`Mount_mg` / `Muzzle_mg`).
  * iron_beam: 8x8 truck carrying a high-energy laser air-defence system (Rafael Iron Beam lineage): a big
    boxy beam director on `Turret` whose head (`Main_cannon_director` and its Main_cannon_* fittings) tilts
    on a yoke, with a large round optical window and a tracking sensor pod; `Muzzle_main` at the centre of
    the window. Behind it a power and cooling container with radiator grilles, fans, a generator exhaust and
    a small flat radar panel spinning on `Radar`; four stabiliser jacks.
  * railgun_truck: heavy 8x8 truck carrying an electromagnetic railgun (ATLA / EMRG lineage): a 7 m
    rectangular twin-rail barrel (`Main_cannon`, copper bus-bar rails between clamp bands, a squared
    `Muzzle_brake`) on an elevating mount on `Turret`, `Muzzle_main` at its tip; two capacitor bank
    containers with cooling pipes and power cables running back to the mount, and four stabiliser jacks.

Rig (ModelLibrary.cs): `Turret` yaws. The game puts the Turret's children named main_cannon*, muzzle_brake*,
launcher*, tubes*, pod*, coax* or muzzle_main* on an elevating pivot at the back of their bounds (6% of their
length from the rear, 30% of their height from the bottom), so the director head and the railgun are shaped
to put that point on their trunnions. The two drone launchers use other names (Cells, Rack...), so like
fpv_carrier's rack they keep their modelled angle. Main_cannon* parts also recoil.

Conventions are those of mb_vehicles.py: metres, +Z up, Blender -Y is the front, the vehicle's left is +X,
origin on the ground under the hull centre, wheels touching z = 0. Each launcher or gun is the highest thing
inside its sweep, so the Turret turns all the way round; the machine guns have clear circles too. Touching
parts overlap or stand at least 1 cm apart, never face to face (coplanar faces z-fight).
"""
import math

from mathutils import Euler, Matrix, Vector

import mb_weapons as wpn
from mb_support import _beacon, _plane, _ram, _rod, _stripes, _telescopic_mast, _whip
from mb_vehicles import (ACROSS, FORWARD, R90, _antenna, _dish, _flank, _frame, _glacis, _grille_frame, _hatch,
                         _headlight, _jerrycans, _rail, _roll, _stowage_bin, _taillight, _wheel)
from mb_vehicles2 import _axis
from mb_vehicles3 import _at, _jack

TAU = math.tau
BACKWARD = (-R90, 0, 0)  # cylinder axis along +Y


# ----------------------------------------------------------------------------- shared truck parts
def _running_gear(a, axles, track, r, width, rails, rail_z, seg=14):
    """Wheels on `axles` (y) at +-track, axle beams at hub height with differentials, and the two frame
    rails from rails[0] to rails[1] at rail_z."""
    dark = a.part('Chassis', 'Undercarriage')
    for y in axles:
        for s in (-1, 1):
            _wheel(a, s * track, y, r, width, seg=seg)
        dark.box((2 * track - .3, .22, .17), loc=(0, y, r), bevel=.02, seg=1)                 # axle beam
        dark.box((.36, .42, .32), loc=(0, y, r + .1), bevel=.03, seg=1)                       # differential
    y0, y1 = rails
    for s in (-1, 1):
        dark.box((.2, y1 - y0, .3), loc=(s * .48, (y0 + y1) / 2, rail_z), bevel=.03, seg=1)   # frame rails
    for y in (y0 + .3, (y0 + y1) / 2, y1 - .3):
        dark.box((.8, .12, .16), loc=(0, y, rail_z), bevel=0)                                  # cross members


def _fuel_tank(a, x, y, z, length, r=.26):
    """Fuel tank along Y on the chassis side at x: steel drum, dark straps, a filler cap and brackets to the
    frame rail."""
    s = 1 if x > 0 else -1
    a.part('Fuel_tanks', 'Steel').cyl(r, length, loc=(x, y, z), rot=FORWARD, seg=12, bevel=.04, bseg=1)
    dark = a.part('Chassis', 'Undercarriage')
    for k in (-.32, .32):
        dark.box((2 * r + .04, .05, 2 * r + .04), loc=(x, y + k * length, z), bevel=0)
        dark.box((abs(x) - .5, .08, .1), loc=(s * (abs(x) + .5) / 2, y + k * length, z + r * .5), bevel=0)
    a.part('Fuel_caps', 'Armor').cyl(.07, .07, loc=(x + s * r * .4, y - length * .3, z + r * .9), seg=8, bevel=0)


def _spare_wheel(a, loc, r, width, axis='x'):
    """Spare wheel on a carrier: axis 'x' (standing along the side), 'y' (facing the tail) or 'z' (flat)."""
    rot = {'x': ACROSS, 'y': FORWARD, 'z': (0, 0, 0)}[axis]
    a.part('Tyres', 'Rubber').cyl(r, width, loc=loc, rot=rot, seg=14, bevel=r * .16, bseg=1)
    hubs = a.part('Hubs', 'Steel')
    hubs.cyl(r * .52, width + .04, loc=loc, rot=rot, seg=10, bevel=.02, bseg=1)
    hubs.cyl(r * .2, width + .1, loc=loc, rot=rot, seg=6, bevel=0)


def _ladder(a, x, y, z0, z1, width=.4, axis='x', parent=None, step=.3):
    """Ladder from z0 to z1 at (x, y): two stiles and rungs running along axis ('x' or 'y')."""
    steel = a.part('Ladder', 'Steel', parent)
    for k in (-1, 1):
        dx, dy = (k * width / 2, 0) if axis == 'x' else (0, k * width / 2)
        steel.box((.05, .05, z1 - z0), loc=(x + dx, y + dy, (z0 + z1) / 2), bevel=0)
    n = max(2, round((z1 - z0) / step))
    for i in range(n):
        z = z0 + (i + .6) * (z1 - z0) / (n + .2)
        steel.box((width, .03, .035) if axis == 'x' else (.03, width, .035), loc=(x, y, z), bevel=0)


def _mirror(a, s, base, out=.24, back=-.1, up=.06):
    """Big truck mirror on side s: a tube arm from base out to a tall housing whose glass looks back."""
    x, y, z = base
    tip = (x + s * out, y + back, z + up)
    a.part('Mirror_arms', 'Steel').tube([base, (x + s * out * .6, y + back * .5, z + up + .04), tip], .016, seg=4)
    a.part('Mirrors', 'Armor').box((.2, .07, .34), loc=(tip[0] + s * .06, tip[1], tip[2] - .1), bevel=.015, seg=1)
    a.part('Mirror_glass', 'Glass').box((.16, .02, .28), loc=(tip[0] + s * .06, tip[1] + .036, tip[2] - .1), bevel=0)


def _plate_frame(a, front, top, t, x, w, h, out=.012, pane=True, bar=.08, name='Window_frames'):
    """A framed pane on a sloped front plate (front -> top in (y, z), see _glacis): glass w x h centred t
    along the plate at x, and an Armor frame round it."""
    wy, wz, wr = _glacis(front, top, t, out)
    if pane:
        a.part('Windows', 'Glass').box((w, h, .04), loc=(x, wy, wz), rot=(wr, 0, 0), bevel=.01, seg=1)
    L = math.hypot(top[0] - front[0], top[1] - front[1])
    fr = a.part(name, 'Armor')
    for dt in (-(h + bar) / 2, (h + bar) / 2):
        fy, fz, _ = _glacis(front, top, t + dt / L, out + .015)
        fr.box((w + 2 * bar, bar, .06), loc=(x, fy, fz), rot=(wr, 0, 0), bevel=0)
    fy, fz, _ = _glacis(front, top, t, out + .015)
    for dx in (-(w + bar) / 2, (w + bar) / 2):
        fr.box((bar, h, .06), loc=(x + dx, fy, fz), rot=(wr, 0, 0), bevel=0)


def _wiper(a, front, top, t0, t1, x0, x1, out=.035):
    """Wiper arm lying on a sloped windscreen from (x0, t0) to (x1, t1), with its spindle."""
    y0, z0, _ = _glacis(front, top, t0, out)
    y1, z1, _ = _glacis(front, top, t1, out)
    steel = a.part('Wipers', 'Steel')
    steel.tube([(x0, y0, z0), (x1, y1, z1)], .013, seg=4)
    y2, z2, wr = _glacis(front, top, t0, out - .02)
    steel.cyl(.03, .04, loc=(x0, y2, z2), rot=(wr - R90, 0, 0), seg=6, bevel=0)


def _side_window(a, s, x, y, z, w, h):
    """Framed window on a vertical cab side at |x| (side s)."""
    a.part('Window_frames', 'Armor').box((.05, w + .12, h + .12), loc=(s * (x + .01), y, z), bevel=.01, seg=1)
    a.part('Windows', 'Glass').box((.04, w, h), loc=(s * (x + .03), y, z), bevel=.008, seg=1)


def _stripe_band(a, origin, facing, width, height, pitch=.26, parent=None):
    """Hazard stripes on a vertical face looking along `facing` ('-y', '+y', '-x', '+x')."""
    ax = {'-y': (1, 0, 0), '+y': (-1, 0, 0), '-x': (0, -1, 0), '+x': (0, 1, 0)}[facing]
    _stripes(a, _plane(origin, ax, (0, 0, 1)), width, height, pitch=pitch, parent=parent)


def _helix(a, x, y, z0, z1, r, turns, parent=None, name='Mast_cable', rr=.016):
    """Coiled cable wound round a mast."""
    n = int(turns * 10)
    pts = [(x + r * math.cos(k * TAU / 10), y + r * math.sin(k * TAU / 10), z0 + (z1 - z0) * k / n) for k in range(n + 1)]
    a.part(name, 'Undercarriage', parent).tube(pts, rr, seg=4, caps=False)


def _camera_ball(a, x, y, z, parent=None, r=.17):
    """Gyro-stabilised electro-optical turret on a pan unit at z (its foot): yoke, ball and lenses facing -Y."""
    steel = a.part('Sensor_steel', 'Steel', parent)
    arm = a.part('Sensor_yoke', 'Armor', parent)
    steel.cyl(.1, .1, loc=(x, y, z + .05), seg=10, bevel=0)                                       # pan unit
    arm.box((.2, .16, .08), loc=(x, y, z + .13), bevel=.02, seg=1)
    ball = a.part('Sensor_ball', 'Armor', parent)
    ball.sphere(r, loc=(x, y, z + .2 + r), seg=14, rings=9)
    lens = a.part('Sensor_glass', 'Glass', parent)
    lens.box((.13, .06, .11), loc=(x - .05, y - r + .02, z + .2 + r + .02), bevel=.01, seg=1)
    lens.box((.07, .05, .07), loc=(x + .08, y - r + .035, z + .2 + r - .05), bevel=0)
    steel.box((.08, .06, .06), loc=(x + .08, y - r + .02, z + .2 + r + .07), bevel=0)             # rangefinder


# ----------------------------------------------------------------------------- lancet_truck
def lancet_truck(a):
    """6x6 armoured truck (KamAZ-63968 Typhoon-K lineage) carrying loitering munitions (Lancet / Switchblade
    600 style): a cab-over armoured crew cab with framed armoured windscreens, a visor, wipers, big mirrors,
    add-on side armour, four doors and steps, guarded headlights, a winch bumper with hazard stripes and a
    roof machine gun; a fuel tank, a locker and a spare wheel under the bed. On the bed: a telescopic sensor
    mast with a camera ball and a coiled cable, a ground-control station with a tracking dish, sector
    panels and whips, stowage and jerrycans, and at the rear the trainable launcher: a six-cell canister box
    (2 x 3 square tubes with lids, one open showing the munition) raised 25 degrees on a rear hinge and two
    rams."""
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    axles = (-2.45, 1.35, 2.75)
    _running_gear(a, axles, 1.03, .56, .44, (-3.45, 3.62), .92)

    # Cab-over armoured crew cab: vertical flanks, chamfered roof edges, the front raked back.
    zb, zs, zt, w, wt = 1.16, 2.38, 3.0, 1.25, 1.04

    def ring(yb, rake):
        pts = [(-w, zb), (w, zb), (w, zs), (wt, zt), (-wt, zt), (-w, zs)]
        return [(x, yb + rake * (z - zb), z) for x, z in pts]
    rake = .1
    body.loft([ring(-3.64, rake), ring(-1.5, 0)], bevel=.06)
    F0, F1 = (-3.64, zb), (-3.64 + rake * (zt - zb), zt)            # the front plate, bottom and top

    def on_front(z, out):
        return _glacis(F0, F1, (z - zb) / (zt - zb), out)
    wr = on_front(2.0, 0)[2]
    for s in (-1, 1):
        _plate_frame(a, F0, F1, (2.42 - zb) / (zt - zb), s * .54, .9, .68)
        _wiper(a, F0, F1, (2.1 - zb) / (zt - zb), (2.66 - zb) / (zt - zb), s * .54 - .3, s * .54 + .08)
    vy, vz, _ = on_front(zt, .04)
    armor.box((2.36, .32, .05), loc=(0, vy - .1, vz - .03), rot=(wr - 1.25, 0, 0), bevel=.012, seg=1)   # visor
    gy, gz, _ = on_front(1.56, .015)
    dark.grille(1.3, .4, loc=(0, gy, gz), rot=(-(R90 - wr), 0, 0), slats=5, depth=.05, thickness=.04)
    for s in (-1, 1):
        hy = on_front(1.52, 0)[0]
        _headlight(a, s * .93, hy, 1.52, guard=True)
        a.part('Marker_lights', 'Alloy').box((.14, .05, .08), loc=(s * .93, on_front(1.3, 0)[0] - .01, 1.3), bevel=0)
    for x in (-.55, 0, .55):
        a.part('Marker_lights', 'Alloy').box((.1, .05, .05), loc=(x, -3.3, zt + .005), bevel=0)
    # Lower nose, bumper with a winch fairlead, tow hooks and striped ends.
    dark.box((2.1, .5, .32), loc=(0, -3.42, 1.02), bevel=.02, seg=1)
    steel.box((2.56, .26, .3), loc=(0, -3.74, .92), bevel=.04, seg=1)
    armor.box((.62, .12, .2), loc=(0, -3.9, .92), bevel=.02, seg=1)                              # fairlead
    dark.cyl(.04, .5, loc=(0, -3.965, .92), rot=ACROSS, seg=6, bevel=0)
    for s in (-1, 1):
        steel.box((.14, .2, .14), loc=(s * .52, -3.92, .82), bevel=.02, seg=1)                 # tow hooks
        _stripe_band(a, (s * .95, -3.87, .92), '-y', .6, .2)
    # Flanks: framed door windows, shut lines, handles, bolted add-on armour, steps, mirrors, mud flaps.
    for s in (-1, 1):
        for y in (-3.02, -2.06):
            _side_window(a, s, w, y, 2.12, .52, .34)
        for y in (-3.52, -2.56, -1.6):
            armor.box((.03, .04, 1.14), loc=(s * (w + .006), y, 1.8), bevel=0)                  # shut lines
        for y in (-2.72, -1.76):
            steel.box((.04, .16, .05), loc=(s * (w + .02), y, 1.9), bevel=0)                    # handles
        for y, ln in ((-3.05, .85), (-2.08, .85)):
            armor.box((.05, ln, .42), loc=(s * (w + .02), y, 1.5), bevel=.012, seg=1)            # add-on armour
            steel.bolts([(s * (w + .05), y + d * (ln / 2 - .07), 1.5 + e) for d in (-1, 1) for e in (-.14, .14)],
                        r=.02, h=.02, rot=(0, R90, 0), bevel=0)
        xu, zu, lean = _flank((w, zs), (wt, zt), .5, .02)
        for y in (-3.0, -2.05):
            armor.box((.05, .8, .36), loc=(s * xu, y, zu), rot=(0, -s * lean, 0), bevel=.012, seg=1)
        for y, zz in ((-3.3, .8), (-3.3, .5), (-1.72, .8), (-1.72, .5)):
            steel.box((.3, .28, .04), loc=(s * 1.1, y, zz), bevel=0)                            # steps
        for y in (-3.3, -1.72):
            steel.box((.04, .3, .44), loc=(s * 1.26, y, .74), bevel=0)
        _mirror(a, s, (s * 1.22, -3.44, 2.62))
        a.part('Mud_flaps', 'Rubber').box((.46, .04, .4), loc=(s * 1.03, -1.84, .74), bevel=0)
        _rail(a, [(s * .9, -3.0, zt - .02), (s * .9, -3.0, zt + .08), (s * .9, -1.8, zt + .08), (s * .9, -1.8, zt - .02)])
    # Cab back: a door out onto the bed.
    armor.box((.72, .05, 1.1), loc=(.35, -1.49, 1.95), bevel=.012, seg=1)
    steel.box((.05, .04, .2), loc=(.06, -1.46, 1.95), bevel=0)
    # Roof: the machine gun ring, a hatch, a SATCOM dome, whips.
    armor.cyl(.34, .1, loc=(-.5, -2.8, zt + .02), seg=16, bevel=.02, bseg=1)
    wpn.hmg(a, (-.5, -2.8, zt + .07), post=.12, length=.85, ammo=-1)
    _hatch(a, .5, -2.35, zt, .27)
    a.part('Satcom', 'Fuel').sphere((.15, .15, .08), loc=(.55, -1.8, zt), seg=10, rings=5, cut=0)
    for s in (-1, 1):
        _whip(a, s * .85, -1.72, zt, 1.4 if s > 0 else 1.1)

    # Bed: deck, low walls, a bulkhead at the front, a tailgate.
    armor.box((2.5, 5.18, .12), loc=(0, 1.19, 1.32), bevel=.02, seg=1)
    for s in (-1, 1):
        body.box((.08, 5.1, .3), loc=(s * 1.21, 1.2, 1.53), bevel=.015, seg=1)
        dark.box((.2, 5.1, .2), loc=(s * .48, 1.2, 1.16), bevel=0)                               # subframe
        armor.box((.52, 2.5, .05), loc=(s * 1.03, 2.05, 1.23), bevel=0)                          # mudguards
        a.part('Mud_flaps', 'Rubber').box((.46, .04, .4), loc=(s * 1.03, 3.4, .74), bevel=0)
        for y in (-.9, .6, 2.1, 3.4):
            steel.box((.04, .1, .06), loc=(s * 1.26, y, 1.44), bevel=0)                         # tie-downs
    body.box((2.5, .08, .3), loc=(0, -1.36, 1.53), bevel=.015, seg=1)
    body.box((2.5, .08, .3), loc=(0, 3.74, 1.53), bevel=.015, seg=1)
    # Under the bed: fuel tank and locker on the left, the spare wheel on the right.
    _fuel_tank(a, .95, -.78, .9, 1.2)
    armor.box((.4, .62, .5), loc=(1.02, .3, .98), bevel=.03, seg=1)
    steel.box((.03, .06, .08), loc=(1.23, .3, 1.08), bevel=0)
    _spare_wheel(a, (-1.0, -.45, .7), .54, .4, axis='x')
    steel.box((.1, .5, .1), loc=(-.72, -.45, .7), bevel=0)                                        # carrier
    steel.box((.1, .1, .5), loc=(-.72, -.45, 1.0), bevel=0)
    # Tail: crossmember, lights, striped bumper, jerrycans, ladder.
    dark.box((2.3, .12, .22), loc=(0, 3.68, 1.14), bevel=0)
    for s in (-1, 1):
        _taillight(a, s * .95, 3.79, 1.14)
    steel.box((2.4, .16, .2), loc=(0, 3.84, .88), bevel=.03, seg=1)
    _stripe_band(a, (0, 3.92, .88), '+y', 2.3, .16)
    _jerrycans(a, (.55, 3.885, .98), 2, axis='x', bracket=False)
    _ladder(a, -.72, 3.97, .3, 1.7, width=.36)
    for z in (.5, 1.62):
        steel.box((.05, .12, .05), loc=(-.72, 3.9, z), bevel=0)

    # Front of the bed: the ground-control station on the left, the sensor mast on the right (clear of the
    # canister faces seen from the front left).
    mx, my = -.62, -.85
    armor.box((.52, .52, .64), loc=(mx, my, 1.69), bevel=.03, seg=1)                             # mast housing
    dark.grille(.36, .3, loc=(mx - .265, my, 1.7), rot=(0, 0, -R90), slats=3, depth=.04, thickness=.03)
    top = _telescopic_mast(a, mx, my, 1.99, ((.11, 1.0), (.09, .9), (.07, .8)))
    _camera_ball(a, mx, my, top)
    _helix(a, mx, my, 2.3, top - .2, .16, 6)
    _ram(a, (mx + .2, my + .2, 1.9), (mx + .1, my + .1, 2.9), .045)                               # mast brace ram
    gx = .62
    armor.box((.8, .9, .72), loc=(gx, my, 1.73), bevel=.03, seg=1)                               # GCS cabinet
    dark.grille(.6, .36, loc=(gx + .405, my, 1.78), rot=(0, 0, R90), slats=4, depth=.04, thickness=.03)
    armor.box((.56, .04, .56), loc=(gx, my - .46, 1.72), bevel=.01, seg=1)                       # door
    steel.box((.04, .04, .16), loc=(gx - .22, my - .49, 1.72), bevel=0)
    a.part('Labels', 'Hazard').box((.22, .02, .12), loc=(gx + .15, my - .485, 1.92), bevel=0)
    steel.cyl(.09, .22, loc=(gx - .12, my + .05, 2.18), seg=10, bevel=0)                         # dish pedestal
    steel.box((.1, .16, .26), loc=(gx - .12, my + .12, 2.4), bevel=0)                            # yoke
    dish = a.part('Link_dish', 'Armor')
    _dish(dish, (gx - .12, my + .08, 2.52), .34, .34, depth=.13, seg=12, tilt=.55)
    feed = Vector((gx - .12, my + .08, 2.52)) + Vector((0, -.36, .21))
    _rod(steel, (gx - .12, my - .03, 2.58), tuple(feed), .012, seg=4)
    armor.box((.06, .06, .06), loc=feed, bevel=0)
    steel.cyl(.03, .7, loc=(gx + .25, my + .3, 2.42), seg=6, bevel=0)                           # panel mast
    panels = a.part('Link_panels', 'Fuel')
    for k in (-1, 1):
        panels.box((.22, .05, .36), loc=(gx + .25 + k * .12, my + .26, 2.72), rot=(-.15, 0, k * .6), bevel=.015,
                   seg=1)
    _whip(a, gx - .3, my + .38, 2.09, 1.5)
    _beacon(a, gx + .32, my - .35, 2.09)
    a.part('Link_cable', 'Undercarriage').tube([(gx - .4, my + .3, 1.42), (mx + .26, my + .3, 1.42)], .03, seg=5)
    # Stowage between the station and the launcher (low: the canister box turns over it).
    for x in (-.72, .72):
        _stowage_bin(a, (x, -.05, 1.37), (.62, .6, .34), latch_side=0)
    _roll(a, (0, -.05, 1.5), .7, r=.12)

    # Launcher: turntable, base, hinge cheeks and rams under the six-cell canister box.
    t = a.pivot('Turret', (0, 2.0, 1.38))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(.88, .1, loc=(0, 0, .04), seg=20, bevel=.02, bseg=1)                               # turntable
    tarm.box((1.5, 1.7, .3), loc=(0, .05, .24), bevel=.04, seg=1, taper=(.94, .95))                  # base
    tarm.box((.46, .4, .3), loc=(-.4, -.45, .52), bevel=.03, seg=1)                                  # hydraulic pack
    a.part('Turret_labels', 'Hazard', t).box((.2, .02, .1), loc=(-.4, -.655, .56), bevel=0)
    pitch = math.radians(25)
    L, cw, rows, cols = 2.3, .56, 2, 3
    W, H = cols * cw + .06, rows * cw + .04
    hinge = Vector((0, .8, .66))
    rot = (-pitch, 0, 0)
    turn = Euler(rot, 'XYZ').to_matrix()
    box = _frame(hinge - turn @ Vector((0, L / 2, -H / 2)), rot)

    def bx(part, size, loc, rr=(0, 0, 0), bevel=0.0, seg=1):
        wl, wrot = _at(box, loc, rr)
        part.box(size, loc=wl, rot=wrot, bevel=bevel, seg=seg)
    tsteel.cyl(.08, W + .34, loc=hinge, rot=ACROSS, seg=10, bevel=0)                             # hinge pin
    for s in (-1, 1):
        tarm.box((.16, .46, .5), loc=(s * (W / 2 + .12), hinge.y, hinge.z - .16), bevel=.02, seg=1)  # cheeks
        tsteel.cyl(.12, .06, loc=(s * (W / 2 + .21), hinge.y, hinge.z), rot=ACROSS, seg=10, bevel=0)
        _ram(a, (s * .5, -.55, .38), tuple(box @ Vector((s * .5, -.35, -H / 2 - .03))), .065, parent=t)
    cells = a.part('Cells', 'Team', t)
    bx(cells, (W, L - .12, H), (0, .06, 0), bevel=.03)
    fr = a.part('Cell_frame', 'Armor', t)
    y0 = -L / 2
    for z in (-H / 2 + .02, H / 2 - .02):                                                             # rim
        bx(fr, (W + .04, .16, .07), (0, y0 + .07, z))
    for x in (-W / 2 + .02, W / 2 - .02):
        bx(fr, (.07, .16, H + .04), (x, y0 + .07, 0))
    bx(fr, (W, .14, .05), (0, y0 + .08, 0))                                                           # dividers
    for x in (-cw / 2, cw / 2):
        bx(fr, (.05, .14, H), (x, y0 + .08, 0))
    for y in (-.25, .62):                                                                             # bands
        bx(fr, (W + .06, .1, H + .06), (0, y, 0), bevel=.012)
    a.part('Box_face', 'Undercarriage', t).box((W - .04, .02, H - .04), loc=tuple(box @ Vector((0, y0 + .125, 0))),
                                                rot=rot, bevel=0)
    lids = a.part('Cell_lids', 'Fuel', t)
    fit = a.part('Cell_fittings', 'Steel', t)
    open_cell = (2, 1)
    for i in range(cols):
        for j in range(rows):
            cx, cz = (i - 1) * cw, (j - .5) * cw
            hz = cz + cw / 2 - .04
            bx(fit, (.36, .05, .05), (cx, y0 + .035, hz))                                          # lid hinge
            if (i, j) == open_cell:
                # Lid swung up on its hinge, the munition's nose and folded wings in the mouth.
                theta = -1.75
                lc = Vector((cx, y0 + .02, hz)) + Matrix.Rotation(theta, 3, 'X') @ Vector((0, 0, -.235))
                bx(lids, (.46, .03, .46), tuple(lc), (theta, 0, 0))
                nose = a.part('Munition', 'Medical', t)
                ml, mr = _at(box, (cx, y0 + .125, cz), (R90, 0, 0))
                nose.lathe([(.15, 0), (.15, .03), (.12, .08), (.05, .12), (0, .13)], loc=ml, rot=mr, seg=10)
                wing = a.part('Munition_wings', 'Armor', t)
                for k in range(4):
                    ang = math.pi / 4 + k * R90
                    bx(wing, (.03, .06, .08), (cx + math.cos(ang) * .18, y0 + .1, cz + math.sin(ang) * .18),
                       (0, -ang, 0))
                continue
            bx(lids, (.47, .03, .47), (cx, y0 + .045, cz))
            bx(fit, (.1, .03, .05), (cx, y0 + .025, cz - cw / 2 + .08))                            # pull tab
    # Top: seams between the canisters, lifting lugs, a cable conduit and a hazard band at the front.
    seam = a.part('Cell_seams', 'Undercarriage', t)
    for x in (-cw / 2, cw / 2):
        bx(seam, (.025, L - .5, .02), (x, .18, H / 2 + .002))
    for x in (-W / 2 + .12, W / 2 - .12):
        for y in (y0 + .35, L / 2 - .3):
            bx(fit, (.08, .1, .08), (x, y, H / 2 + .03))
    bx(a.part('Cell_conduit', 'Undercarriage', t), (.1, L - .6, .06), (W / 2 - .3, .25, H / 2 + .02))
    sm = box @ _frame((0, y0 + .32, H / 2 - .002), (0, 0, 0))
    _stripes(a, _plane(sm.to_translation(), box.to_3x3() @ Vector((1, 0, 0)), box.to_3x3() @ Vector((0, 1, 0))),
             W - .5, .2, pitch=.24, parent=t)
    for s in (-1, 1):                                                                                  # grab handles
        bx(fit, (.04, .5, .04), (s * (W / 2 + .03), .3, .1))
    # Rear face: a connector per canister and the umbilical down to the turntable.
    for i in range(cols):
        for j in range(rows):
            bx(fit, (.14, .06, .14), ((i - 1) * cw, L / 2 + .01, (j - .5) * cw))
    p0 = box @ Vector((0, L / 2 + .04, -.1))
    a.part('Box_cables', 'Undercarriage', t).tube([tuple(p0), tuple(p0 + Vector((0, .25, -.3))), (0, 1.05, .45),
                                                   (0, .75, .3)], .045, seg=6)
    a.pivot('Muzzle_main', tuple(box @ Vector((0, y0 - .02, 0))), t)


BUILDERS = {
    'lancet_truck': (lancet_truck, dict(ao_distance=.6, grime_height=.55)),
}
