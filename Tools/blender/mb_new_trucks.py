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
import re

from mathutils import Euler, Matrix, Vector

import mb_weapons as wpn
from frontier_kit import chamfered
from mb_support import _beacon, _light_bar, _plane, _ram, _rod, _stripes, _telescopic_mast, _whip
from mb_vehicles import (ACROSS, FORWARD, R90, _dish, _flank, _frame, _glacis, _grille_frame, _hatch,
                         _headlight, _jerrycans, _rail, _roll, _stowage_bin, _taillight, _wheel)
from mb_vehicles2 import _axis
from mb_vehicles3 import _at, _jack

TAU = math.tau
# ModelLibrary.BarrelPattern: the Turret children that the game raises on its elevating pivot.
ELEVATING = re.compile(r'^(main_cannon|muzzle_brake|mortar_tube|rocket_tubes|tubes|tube_bores|pod(?!_frame)|atgm_pod|'
                       r'launcher|coax|muzzle_main|muzzle_coax|muzzle_missile|muzzle_rocket)', re.I)


def _game_pivot(a, parent):
    """Where ModelLibrary.AddElevation will put the elevating pivot of `parent`'s barrel parts (in the parent's
    frame): the middle across, 6% of the group's length from its rear (+Y) and 30% of its height up."""
    pts = [v.co for (name, _, par), shape in a.shapes.items() if par == parent and ELEVATING.match(name)
           for v in shape.bm.verts]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    return Vector(((lo.x + hi.x) / 2, hi.y - (hi.y - lo.y) * .06, lo.z + (hi.z - lo.z) * .3))


# ----------------------------------------------------------------------------- shared truck parts
def _cab_over(a, yf, yb, zb, zs, zt, w, wt, rake, name='Body'):
    """Cab-over cab: vertical flanks, chamfered roof edges, the front plate raked back by `rake` (dy per dz).
    Returns the front plate's bottom and top (y, z) for _glacis."""
    def ring(y0, k):
        pts = [(-w, zb), (w, zb), (w, zs), (wt, zt), (-wt, zt), (-w, zs)]
        return [(x, y0 + k * (z - zb), z) for x, z in pts]
    a.part(name, 'Team').loft([ring(yf, rake), ring(yb, 0)], bevel=.06)
    return (yf, zb), (yf + rake * (zt - zb), zt)


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
    _running_gear(a, axles, 1.03, .56, .44, (-3.45, 3.46), .92)

    # Cab-over armoured crew cab: vertical flanks, chamfered roof edges, the front raked back.
    zb, zs, zt, w, wt = 1.16, 2.38, 3.0, 1.25, 1.04
    F0, F1 = _cab_over(a, -3.64, -1.5, zb, zs, zt, w, wt, .1)      # the front plate, bottom and top

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
    steel.box((2.56, .24, .3), loc=(0, -3.7, .92), bevel=.04, seg=1)
    armor.box((.62, .1, .2), loc=(0, -3.83, .92), bevel=.02, seg=1)                              # fairlead
    dark.cyl(.035, .5, loc=(0, -3.885, .92), rot=ACROSS, seg=6, bevel=0)
    for s in (-1, 1):
        steel.box((.14, .14, .14), loc=(s * .52, -3.85, .82), bevel=.02, seg=1)                # tow hooks
        _stripe_band(a, (s * .95, -3.82, .92), '-y', .6, .2)
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
        _mirror(a, s, (s * 1.22, -3.44, 2.62), out=.18)
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
    armor.box((2.5, 5.02, .12), loc=(0, 1.11, 1.32), bevel=.02, seg=1)
    for s in (-1, 1):
        body.box((.08, 4.94, .3), loc=(s * 1.21, 1.12, 1.53), bevel=.015, seg=1)
        dark.box((.2, 4.9, .2), loc=(s * .48, 1.1, 1.16), bevel=0)                               # subframe
        armor.box((.52, 2.5, .05), loc=(s * 1.03, 2.05, 1.23), bevel=0)                          # mudguards
        a.part('Mud_flaps', 'Rubber').box((.46, .04, .4), loc=(s * 1.03, 3.36, .74), bevel=0)
        for y in (-.9, .6, 2.1, 3.4):
            steel.box((.04, .1, .06), loc=(s * 1.26, y, 1.44), bevel=0)                         # tie-downs
    body.box((2.5, .08, .3), loc=(0, -1.36, 1.53), bevel=.015, seg=1)
    body.box((2.5, .08, .3), loc=(0, 3.58, 1.53), bevel=.015, seg=1)
    # Under the bed: fuel tank and locker on the left, the spare wheel on the right.
    _fuel_tank(a, .95, -.78, .9, 1.2)
    armor.box((.4, .62, .5), loc=(1.02, .3, .98), bevel=.03, seg=1)
    steel.box((.03, .06, .08), loc=(1.23, .3, 1.08), bevel=0)
    _spare_wheel(a, (-1.0, -.45, .7), .54, .4, axis='x')
    steel.box((.1, .5, .1), loc=(-.72, -.45, .7), bevel=0)                                        # carrier
    steel.box((.1, .1, .5), loc=(-.72, -.45, 1.0), bevel=0)
    # Tail: crossmember, lights, striped bumper, jerrycans, ladder.
    dark.box((2.3, .12, .22), loc=(0, 3.52, 1.14), bevel=0)
    for s in (-1, 1):
        _taillight(a, s * .95, 3.63, 1.14)
    steel.box((2.4, .16, .2), loc=(0, 3.68, .88), bevel=.03, seg=1)
    _stripe_band(a, (0, 3.76, .88), '+y', 2.3, .16)
    for x in (.4, .76):
        _jerrycans(a, (x, 3.705, .98), 1, axis='y', bracket=False)
    _ladder(a, -.72, 3.81, .3, 1.7, width=.36)
    for z in (.5, 1.62):
        steel.box((.05, .12, .05), loc=(-.72, 3.74, z), bevel=0)

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


# ----------------------------------------------------------------------------- shahed_truck
def _shahed(a, m, parent, k=1.0):
    """Shahed-136 one-way attack drone in frame m (origin on the wing plane at the drone's middle, local -Y
    the nose, local Z up), k times full size (3.3 m long, 2.5 m span): a cropped delta wing blended round a
    slim fuselage with a rounded warhead nose, wingtip fins standing above and below the tips, and the
    engine with a two-blade pusher propeller (blades level with the wing) at the tail."""
    def at(loc, rot=(0, 0, 0)):
        return _at(m, tuple(c * k for c in loc), rot)
    skin = a.part('Drone_airframe', 'Medical', parent)
    l, r = at((0, 0, 0))
    skin.prism([(-1.25 * k, .98 * k), (-.16 * k, -.78 * k), (.16 * k, -.78 * k), (1.25 * k, .98 * k),
                (1.25 * k, 1.36 * k), (-1.25 * k, 1.36 * k)], .07 * k, loc=l, rot=r, axis='Z', bevel=.02 * k, seg=1)
    l, r = at((0, 0, 0), FORWARD)                                      # lathe axis (local Z) -> the nose
    skin.lathe([(.1 * k, -1.52 * k), (.15 * k, -1.3 * k), (.17 * k, -.3 * k), (.17 * k, .95 * k), (.14 * k, 1.35 * k),
                (.08 * k, 1.58 * k), (0, 1.66 * k)], loc=l, rot=r, seg=10)
    a.part('Drone_nose', 'Armor', parent).cyl(.175 * k, .06 * k, loc=at((0, -1.1, 0))[0], rot=at((0, 0, 0), FORWARD)[1],
                                               seg=10, bevel=0)                                  # warhead joint
    for s in (-1, 1):                                                                            # wingtip fins
        l, r = at((s * 1.25, 0, 0))
        skin.prism([(.78 * k, .02 * k), (1.1 * k, .27 * k), (1.4 * k, .27 * k), (1.4 * k, -.14 * k), (1.12 * k, -.14 * k)],
                   .035 * k, loc=l, rot=r, axis='X', bevel=0)
    eng = a.part('Drone_engine', 'Steel', parent)
    l, r = at((0, 1.5, 0), FORWARD)
    eng.cyl(.12 * k, .26 * k, loc=l, rot=r, seg=8, bevel=0)
    l, r = at((0, 1.66, 0), FORWARD)
    eng.cyl(.05 * k, .08 * k, loc=l, rot=r, seg=6, bevel=0)                                      # hub
    prop = a.part('Drone_prop', 'Undercarriage', parent)
    for s in (-1, 1):
        l, r = at((s * .2, 1.67, 0), (0, s * .25, 0))
        prop.box((.36 * k, .02 * k, .07 * k), loc=l, rot=r, bevel=0)


def shahed_truck(a):
    """6x6 bonneted truck (Mercedes-Benz Zetros lineage) carrying five Shahed-136 drones: a short square
    bonnet with a big grille behind a brush guard, flared front fenders with the lamps, a two-door cab with a
    raked split windscreen, wipers, a sun visor, big mirrors, a side air intake and a roof machine gun; a
    fuel tank, a spare wheel and lockers along the frame, drop sides, rear jacks, a ladder and striped bumpers.
    The launcher on `Turret` is a stepped five-level rack inclined 20 degrees: each drone sits on its twin
    rails, each level set back from the one below it, between two side trusses on a hinged base lifted by
    rams."""
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    axles = (-2.85, 1.35, 2.75)
    _running_gear(a, axles, 1.02, .55, .42, (-3.75, 3.6), .9)
    # Short square bonnet, grille and brush guard, bumper, fenders with the lamps.
    body.prism([(-3.84, .98), (-3.88, 1.74), (-3.74, 1.86), (-2.7, 1.95), (-2.7, .98)], 1.66, bevel=.05)
    dark.grille(1.2, .56, loc=(0, -3.875, 1.36), rot=(-.05, 0, 0), slats=6, depth=.05, thickness=.045)
    for x in (-.64, .64):
        armor.box((.06, .05, .66), loc=(x, -3.89, 1.36), bevel=0)                                  # grille frame
    for z in (1.03, 1.69):
        armor.box((1.34, .05, .06), loc=(0, -3.89, z), bevel=0)
    for s in (-1, 1):
        steel.box((.04, .5, .04), loc=(s * .835, -3.2, 1.86), bevel=0)                              # bonnet latches
        dark.grille(.5, .22, loc=(s * .835, -3.05, 1.6), rot=(0, 0, s * R90), slats=3, depth=.04, thickness=.03)
    _rail(a, [(-.72, -3.9, 1.0), (-.72, -4.0, 1.12), (-.72, -4.0, 1.72), (.72, -4.0, 1.72), (.72, -4.0, 1.12),
              (.72, -3.9, 1.0)], r=.032)
    for x in (-.36, 0, .36):
        _rail(a, [(x, -4.0, 1.1), (x, -4.0, 1.72)], r=.022)
    steel.box((2.5, .22, .26), loc=(0, -3.92, .86), bevel=.04, seg=1)
    for s in (-1, 1):
        steel.box((.14, .14, .14), loc=(s * .55, -4.05, .78), bevel=.02, seg=1)                   # tow hooks
        _stripe_band(a, (s * .96, -4.03, .86), '-y', .5, .2)
        body.prism([(-3.58, 1.12), (-3.52, 1.3), (-3.3, 1.42), (-2.42, 1.42), (-2.2, 1.26), (-2.2, 1.12)], .6,
                   loc=(s * 1.0, 0, 0), bevel=.03)                                                  # fender
        _headlight(a, s * 1.0, -3.54, 1.24, guard=False)
        a.part('Marker_lights', 'Alloy').box((.12, .05, .07), loc=(s * 1.18, -3.47, 1.38), bevel=0)
    # Cab: raked split windscreen, doors, roof with the machine gun and a hatch.
    F0, F1 = (-2.74, 1.9), (-2.58, 2.66)
    body.prism([(-2.74, 1.12), F0, F1, (-2.46, 2.78), (-1.25, 2.8), (-1.25, 1.12)], 2.36, bevel=.06)
    t_ws = .52
    for s in (-1, 1):
        _plate_frame(a, F0, F1, t_ws, s * .55, .96, .62)
        _wiper(a, F0, F1, .14, .78, s * .55 - .32, s * .55 + .06)
    wr = _glacis(F0, F1, .5, 0)[2]
    vy, vz, _ = _glacis(F0, F1, 1.0, .04)
    armor.box((2.3, .3, .05), loc=(0, vy - .1, vz + .06), rot=(wr - 1.2, 0, 0), bevel=.012, seg=1)   # sun visor
    for x in (-.5, 0, .5):
        a.part('Marker_lights', 'Alloy').box((.1, .05, .05), loc=(x, -2.36, 2.805), bevel=0)
    for s in (-1, 1):
        ox = 1.18
        _side_window(a, s, ox, -2.08, 2.26, .62, .46)
        for y in (-2.6, -1.42):
            armor.box((.03, .04, 1.2), loc=(s * (ox + .006), y, 1.9), bevel=0)                     # door lines
        steel.box((.04, .16, .05), loc=(s * (ox + .02), -1.6, 1.95), bevel=0)                      # handle
        _rail(a, [(s * (ox + .01), -1.34, 1.5), (s * (ox + .06), -1.34, 1.5), (s * (ox + .06), -1.34, 2.3),
                  (s * (ox + .01), -1.34, 2.3)])
        for zz in (.78, .48):
            steel.box((.3, .3, .04), loc=(s * 1.05, -1.95, zz), bevel=0)                          # steps
        steel.box((.04, .32, .42), loc=(s * 1.2, -1.95, .72), bevel=0)
        _mirror(a, s, (s * 1.17, -2.6, 2.5), out=.2)
        a.part('Mud_flaps', 'Rubber').box((.44, .04, .4), loc=(s * 1.02, -2.22, .72), bevel=0)
    steel.cyl(.1, 1.1, loc=(1.28, -1.55, 2.2), seg=10, bevel=0)                                    # air intake
    steel.cyl(.14, .24, loc=(1.28, -1.55, 2.82), seg=10, bevel=.02, bseg=1)
    for z in (1.8, 2.5):
        steel.box((.14, .06, .05), loc=(1.22, -1.55, z), bevel=0)
    steel.cyl(.07, 1.3, loc=(-1.02, -1.12, 2.0), seg=8, bevel=0)                                  # exhaust stack
    steel.cyl(.1, .3, loc=(-1.02, -1.12, 2.3), seg=8, bevel=0)                                    # heat shield
    dark.cyl(.075, .06, loc=(-1.02, -1.12, 2.66), seg=8, bevel=0)
    armor.cyl(.33, .1, loc=(.45, -1.95, 2.82), seg=16, bevel=.02, bseg=1)                         # MG ring
    wpn.hmg(a, (.45, -1.95, 2.87), post=.12, length=.85, ammo=1)
    _hatch(a, -.45, -1.85, 2.79, .26)
    _whip(a, -.95, -1.45, 2.8, 1.4)
    armor.box((.7, .06, 1.0), loc=(.2, -1.23, 1.95), bevel=.012, seg=1)                            # rear window frame
    a.part('Windows', 'Glass').box((.56, .04, .3), loc=(.2, -1.205, 2.25), bevel=0)

    # Bed: flat deck with drop sides, lockers, fuel tank and spare wheel below, rear jacks, bumper, ladder.
    armor.box((2.5, 4.94, .14), loc=(0, 1.37, 1.31), bevel=.02, seg=1)                             # deck
    for s in (-1, 1):
        body.box((.07, 4.84, .2), loc=(s * 1.22, 1.39, 1.47), bevel=.012, seg=1)                  # drop sides
        for y in (-.4, 1.2, 2.8):
            steel.box((.03, .06, .15), loc=(s * 1.26, y, 1.47), bevel=0)                          # side latches
        dark.box((.2, 4.84, .2), loc=(s * .48, 1.37, 1.14), bevel=0)                              # subframe
        armor.box((.5, 2.5, .05), loc=(s * 1.02, 2.05, 1.215), bevel=0)                           # mudguards
        a.part('Mud_flaps', 'Rubber').box((.44, .04, .4), loc=(s * 1.02, 3.4, .72), bevel=0)
        _jack(a, s * 1.05, 3.5, 1.24, pad=.18)
        _taillight(a, s * .8, 3.83, 1.12)
    body.box((2.5, .07, .2), loc=(0, -1.07, 1.47), bevel=.012, seg=1)
    body.box((2.5, .07, .2), loc=(0, 3.81, 1.47), bevel=.012, seg=1)
    dark.box((2.2, .12, .22), loc=(0, 3.7, 1.12), bevel=0)                                          # crossmember
    steel.box((2.3, .16, .2), loc=(0, 3.84, .86), bevel=.03, seg=1)
    _stripe_band(a, (0, 3.92, .86), '+y', 2.2, .16)
    _ladder(a, .3, 3.94, .35, 1.56, width=.36)
    _fuel_tank(a, .92, -.55, .88, 1.3)
    _spare_wheel(a, (-.98, -.45, .68), .53, .38, axis='x')
    steel.box((.1, .5, .1), loc=(-.72, -.45, .68), bevel=0)
    steel.box((.1, .1, .52), loc=(-.72, -.45, .98), bevel=0)
    armor.box((.36, .5, .44), loc=(1.02, .45, .96), bevel=.03, seg=1)                              # battery box
    steel.box((.03, .06, .08), loc=(1.21, .45, 1.06), bevel=0)
    # Bed front: launch-control box with its cable to the rack, jerrycans, a tarp.
    armor.box((.9, .5, .5), loc=(-.55, -.72, 1.63), bevel=.03, seg=1)
    dark.grille(.6, .26, loc=(-.55, -.975, 1.66), slats=3, depth=.04, thickness=.03)
    a.part('Labels', 'Hazard').box((.2, .02, .1), loc=(-.2, -.98, 1.8), bevel=0)
    _jerrycans(a, (.6, -.78, 1.37), 3, axis='x')
    boost = a.part('Boosters', 'Armor')
    for y in (-.3, 0.0):
        boost.cyl(.12, 1.2, loc=(.35, y, 1.53), rot=ACROSS, seg=10, bevel=.02, bseg=1)             # spare boosters
        a.part('Booster_bands', 'Hazard').cyl(.125, .1, loc=(-.1, y, 1.53), rot=ACROSS, seg=10, bevel=0)
        steel.cyl(.09, .14, loc=(1.0, y, 1.53), rot=ACROSS, seg=8, r2=.11, bevel=0)                    # nozzles
    for x in (-.05, .75):
        armor.box((.1, .56, .12), loc=(x, -.15, 1.44), bevel=0)                                         # cradles
    a.part('Launch_cable', 'Undercarriage').tube([(-.55, -.45, 1.5), (-.4, .1, 1.42), (-.3, .45, 1.42)], .035, seg=5)
    armor.box((.2, .14, .12), loc=(-.3, .5, 1.42), bevel=0)                                       # deck socket

    # Launcher: turntable, hinged base and the stepped rack of five drones.
    t = a.pivot('Turret', (0, 1.75, 1.38))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(.95, .1, loc=(0, 0, .04), seg=20, bevel=.02, bseg=1)                               # turntable
    tarm.cyl(.86, .16, loc=(0, 0, .16), seg=20, bevel=.02, bseg=1)                                   # pedestal
    # The base clears the drop sides (top 1.57 m) as it turns.
    tarm.box((1.7, 2.3, .28), loc=(0, .0, .37), bevel=.04, seg=1, taper=(.95, .96))                  # base
    pitch = math.radians(20)
    rot = (-pitch, 0, 0)
    turn = Euler(rot, 'XYZ').to_matrix()
    back = turn @ Vector((0, 1, 0))                                  # down the rails, towards the tail
    k, hz, st, xt = .92, .47, .3, 1.28                               # drone scale, level rise, set-back, trusses
    hinge = Vector((0, .98, .66))
    rs, fs = 1.78 * k, -1.02 * k                                     # rear and front stations (drone frame y)
    c0 = hinge - turn @ Vector((0, rs + .05, -.24))

    def level(i):
        return _frame(c0 + Vector((0, 0, i * hz)) + back * st * i, rot)
    tsteel.cyl(.09, 2.0, loc=hinge, rot=ACROSS, seg=10, bevel=0)                                  # hinge pin
    for s in (-1, 1):
        tarm.box((.16, .44, .44), loc=(s * .92, hinge.y, hinge.z - .12), bevel=.02, seg=1)        # hinge cheeks
    rails = a.part('Rack_rails', 'Steel', t)
    shoes = a.part('Rack_shoes', 'Armor', t)
    cross = a.part('Rack_cross', 'Armor', t)
    truss = a.part('Rack', 'Team', t)
    for i in range(5):
        m = level(i)

        def put(part, size, loc):
            wl, wrot = _at(m, loc)
            part.box(size, loc=wl, rot=wrot, bevel=0)
        for x in (-.5 * k, .5 * k):
            put(rails, (.07, rs - fs, .1), (x, (rs + fs) / 2, -.1))                                  # twin rails
            put(shoes, (.12, .16, .06), (x, -.2, -.02))                                              # launch shoes
            put(shoes, (.12, .16, .06), (x, .9 * k, -.02))
        put(cross, (2 * xt, .1, .1), (0, rs + .05, -.1))                                              # rear cross beam
        for s in (-1, 1):
            put(cross, (xt - .5 * k + .05, .1, .1), (s * (xt + .5 * k) / 2, fs, -.1))              # front outriggers
        if i == 0:
            put(cross, (2 * xt, .12, .12), (0, fs, -.24))                                            # bottom front beam
        a.part('Rack_stops', 'Hazard', t).box((.1, .04, .1), loc=_at(m, (0, fs - .08, -.1))[0], rot=rot, bevel=0)
        _shahed(a, m, t, k=k)
    # Side trusses: stringers along the bottom and top levels, posts up the stepped rear and front ends, a
    # diagonal, and a ladder up the left truss for loading.
    for s in (-1, 1):
        x = s * xt
        pts = {(i, st_): tuple(level(i) @ Vector((x, st_, -.1))) for i in (0, 4) for st_ in (rs + .05, fs)}
        for i in (0, 4):
            _rod(truss, pts[(i, rs + .05)], pts[(i, fs)], .05, seg=6)
        for st_ in (rs + .05, fs):
            _rod(truss, pts[(0, st_)], pts[(4, st_)], .05, seg=6)
        _rod(truss, pts[(0, rs + .05)], pts[(4, fs)], .035, seg=6)
        for i in (1, 2, 3):
            for st_ in (rs + .05, fs):
                truss.box((.1, .1, .1), loc=tuple(level(i) @ Vector((x, st_, -.1))), rot=rot, bevel=0)
        _ram(a, (s * .55, -.85, .5), tuple(level(0) @ Vector((s * .55, fs, -.3))), .07, parent=t)
    for i in range(4):
        _rod(a.part('Rack_ladder', 'Steel', t), tuple(level(i) @ Vector((xt + .06, rs + .05, -.1))),
             tuple(level(i + 1) @ Vector((xt + .06, rs + .05, -.1))), .018, seg=4)
    a.part('Rack_cables', 'Undercarriage', t).tube([(-.3, -.9, .5), (-.6, .1, .55), tuple(level(0) @ Vector((-.6, rs, -.18)))],
                                                   .035, seg=5)
    a.pivot('Muzzle_main', tuple(level(4) @ Vector((0, -1.66 * k - .04, 0))), t)


# ----------------------------------------------------------------------------- iron_beam
def _fan(a, x, y, z, r=.42):
    """Radiator fan on a roof at height z: a steel shroud, a dark grille disc with spokes and a hub."""
    a.part('Fan_shrouds', 'Steel').cyl(r + .04, .12, loc=(x, y, z + .05), seg=16, bevel=.02, bseg=1)
    a.part('Fan_grilles', 'Undercarriage').cyl(r, .02, loc=(x, y, z + .11), seg=16, bevel=0)
    spokes = a.part('Fan_spokes', 'Armor')
    for k in range(4):
        spokes.box((2 * r - .02, .035, .03), loc=(x, y, z + .125), rot=(0, 0, k * math.pi / 4), bevel=0)
    spokes.cyl(.09, .05, loc=(x, y, z + .13), seg=8, bevel=0)


def iron_beam(a):
    """8x8 high-energy laser air-defence truck (Rafael Iron Beam lineage): a wide cab-over cab (MAN HX
    lineage) with a split raked windscreen, wipers, visor, mirrors, a grille panel and a lamp bumper with
    hazard stripes; a flat deck with the fuel tank, spare wheel and four stabiliser jacks on the chassis. On
    the deck behind the cab the beam director turns on `Turret`: an octagonal azimuth housing, a yoke and the
    big boxy director head (`Main_cannon_director`) with a large round optical window in a sun-hooded bezel,
    a glowing emitter ring, a tracking sensor block beside the window and a tracker pod on top; the head
    tilts on the yoke's trunnions. Behind it the power and cooling container: radiator grilles and doors on
    its sides, two roof fans, handrails, a generator exhaust stack, coolant pipes and cables running forward
    to the director, and a small flat radar panel spinning on `Radar` above the tail."""
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    axles = (-3.2, -1.85, 1.9, 3.25)
    _running_gear(a, axles, 1.16, .6, .46, (-4.2, 4.3), .98)

    # Cab-over cab.
    zb, zs, zt, w = 1.3, 2.5, 3.02, 1.25
    F0, F1 = _cab_over(a, -4.3, -2.45, zb, zs, zt, w, 1.1, .12)
    _plate_frame(a, F0, F1, (2.5 - zb) / (zt - zb), 0, 2.16, .66)                                     # panoramic pane
    for x in (-.62, .42):
        _wiper(a, F0, F1, (2.2 - zb) / (zt - zb), (2.76 - zb) / (zt - zb), x - .28, x + .14)
    # Full-width black grille band with the headlamps set in it, steel bars across the grille.
    a.part('Grille_band', 'Undercarriage').box((2.5, .14, .62), loc=(0, -4.37, 1.63), bevel=.03, seg=1)
    for z in (1.5, 1.63, 1.76):
        steel.box((1.3, .04, .04), loc=(0, -4.45, z), bevel=0)
    steel.box((2.56, .28, .32), loc=(0, -4.36, 1.1), bevel=.04, seg=1)                                # bumper
    for s in (-1, 1):
        _headlight(a, s * .98, -4.44, 1.63, guard=False)
        a.part('Marker_lights', 'Alloy').box((.14, .05, .08), loc=(s * .75, -4.52, 1.14), bevel=0)
        steel.box((.14, .16, .14), loc=(s * .45, -4.52, .98), bevel=.02, seg=1)                     # tow hooks
        _stripe_band(a, (s * 1.08, -4.5, 1.1), '-y', .38, .2)
    _light_bar(a, -.95, .95, -3.95, zt - .01, lamps=4)
    for s in (-1, 1):
        _side_window(a, s, w, -3.45, 2.28, .72, .5)
        _side_window(a, s, w, -2.78, 2.28, .36, .5)
        for y in (-4.12, -3.0):
            armor.box((.03, .04, 1.2), loc=(s * (w + .006), y, 1.92), bevel=0)                       # door lines
        steel.box((.04, .16, .05), loc=(s * (w + .02), -3.15, 2.0), bevel=0)
        for zz in (.86, .56):
            steel.box((.3, .26, .04), loc=(s * 1.1, -3.98, zz), bevel=0)                             # steps
        steel.box((.04, .28, .44), loc=(s * 1.26, -3.98, .8), bevel=0)
        _rail(a, [(s * (w + .01), -4.18, 1.55), (s * (w + .06), -4.18, 1.55), (s * (w + .06), -4.18, 2.4),
                  (s * (w + .01), -4.18, 2.4)])
        _mirror(a, s, (s * 1.22, -4.1, 2.7), out=.18)
        a.part('Mud_flaps', 'Rubber').box((.46, .04, .42), loc=(s * 1.16, -1.18, .78), bevel=0)
        armor.box((.56, 1.4, .05), loc=(s * 1.16, -1.85, 1.39), bevel=0)                             # mudguards
        armor.box((.56, 2.75, .05), loc=(s * 1.16, 2.575, 1.39), bevel=0)
        a.part('Mud_flaps', 'Rubber').box((.46, .04, .42), loc=(s * 1.16, 3.93, .78), bevel=0)
    _hatch(a, -.5, -3.4, zt, .27)
    armor.box((.8, .6, .2), loc=(.35, -2.85, zt + .08), bevel=.03, seg=1)                             # air conditioner
    dark.grille(.6, .4, loc=(.35, -2.85, zt + .185), rot=(-R90, 0, 0), slats=3, depth=.04, thickness=.03)
    a.part('Satcom', 'Fuel').sphere((.14, .14, .08), loc=(-.55, -2.75, zt), seg=10, rings=5, cut=0)
    for s in (-1, 1):
        _whip(a, s * .95, -2.62, zt, 1.2)

    # Deck, subframe, chassis lockers, jacks, tail.
    armor.box((2.5, 6.9, .12), loc=(0, 1.0, 1.5), bevel=.02, seg=1)
    for s in (-1, 1):
        dark.box((.2, 6.8, .3), loc=(s * .48, 1.0, 1.29), bevel=0)
        armor.box((.06, 6.9, .08), loc=(s * 1.24, 1.0, 1.55), bevel=0)                                # deck edges
        for y in (-2.1, -.4, 1.5, 3.2):
            steel.box((.04, .1, .06), loc=(s * 1.265, y, 1.5), bevel=0)                               # tie-downs
        _jack(a, s * 1.3, .95, 1.44, pad=.22)
        _jack(a, s * 1.1, 4.12, 1.44, pad=.2)
        _taillight(a, s * .8, 4.5, 1.3)
    _fuel_tank(a, .95, -.45, .96, 1.2, r=.28)
    _spare_wheel(a, (-1.05, -.45, .78), .58, .42, axis='x')
    steel.box((.1, .5, .1), loc=(-.74, -.45, .78), bevel=0)
    steel.box((.1, .1, .5), loc=(-.74, -.45, 1.1), bevel=0)
    dark.box((2.3, .12, .24), loc=(0, 4.36, 1.26), bevel=0)                                           # crossmember
    steel.box((2.4, .16, .2), loc=(0, 4.5, 1.0), bevel=.03, seg=1)
    _stripe_band(a, (0, 4.58, 1.0), '+y', 2.3, .16)
    _stowage_bin(a, (-.7, -2.2, 1.55), (.8, .36, .34), latch_side=0)                                  # in front of
    _stowage_bin(a, (.7, -2.2, 1.55), (.8, .36, .34), latch_side=0)                                   # the director

    # Power and cooling container behind the director.
    y0, y1, zc = .5, 4.3, 2.72
    cz0, hw = 1.56, 1.24
    body.box((2 * hw, y1 - y0, zc - cz0), loc=(0, (y0 + y1) / 2, (cz0 + zc) / 2), bevel=.05, seg=1)
    for sx in (-1, 1):
        for yy in (y0 + .04, y1 - .04):
            armor.box((.1, .1, zc - cz0 + .02), loc=(sx * (hw - .03), yy, (cz0 + zc) / 2), bevel=0)   # corner posts
            for zz in (cz0 + .07, zc - .05):
                steel.box((.14, .14, .1), loc=(sx * (hw - .02), yy, zz), bevel=0)                     # corner castings
    for s in (-1, 1):
        for yc in (1.3, 2.55):
            dark.grille(1.0, .8, loc=(s * (hw + .01), yc, 2.12), rot=(0, 0, s * R90), slats=6, depth=.05,
                        thickness=.04)
            for dy in (-.54, .54):
                armor.box((.05, .06, .9), loc=(s * (hw + .015), yc + dy, 2.12), bevel=0)             # grille frames
            for dz in (-.47, .47):
                armor.box((.05, 1.14, .06), loc=(s * (hw + .015), yc, 2.12 + dz), bevel=0)
        armor.box((.05, .7, .95), loc=(s * (hw + .015), 3.6, 2.08), bevel=.012, seg=1)               # door
        steel.box((.04, .05, .2), loc=(s * (hw + .045), 3.35, 2.1), bevel=0)
        a.part('Labels', 'Hazard').box((.03, .3, .2), loc=(s * (hw + .02), 3.6, 2.4), bevel=0)
        _rail(a, [(s * (hw - .1), y0 + .4, zc - .02), (s * (hw - .1), y0 + .4, zc + .14), (s * (hw - .1), y1 - .3, zc + .14),
                  (s * (hw - .1), y1 - .3, zc - .02)])
    for yf in (1.35, 2.45):
        _fan(a, 0, yf, zc - .01)
    _stripe_band(a, (0, y0 - .005, zc - .12), '-y', 2.2, .14)
    # Front face: coolant manifold and cable glands, pipes and cables running forward to the director.
    pipes = a.part('Coolant_pipes', 'Pipe')
    cables = a.part('Power_cables', 'Rubber')
    for x in (-.35, -.15):
        pipes.tube([(x, y0 + .02, 2.15), (x, y0 - .07, 2.15), (x, y0 - .07, 1.66)], .045, seg=6)
    armor.box((.5, .1, .2), loc=(-.25, y0 - .03, 2.15), bevel=0)                                       # manifold
    for x in (.2, .42):
        cables.tube([(x, y0 + .02, 2.0), (x, y0 - .07, 1.94), (x, y0 - .08, 1.66)], .05, seg=6)
    armor.box((1.0, .14, .16), loc=(0, y0 - .08, 1.63), bevel=.02, seg=1)                             # junction box
    # Rear: container doors with lock bars, a ladder to the roof, the generator exhaust.
    for x in (-.6, .6):
        armor.box((1.1, .05, 1.0), loc=(x, y1 + .015, 2.1), bevel=.012, seg=1)
        for dx in (-.25, .25):
            steel.box((.04, .04, 1.0), loc=(x + dx, y1 + .045, 2.1), bevel=0)                        # lock bars
    _ladder(a, .6, y1 + .1, 1.6, zc + .3, width=.4)
    ex = (-.9, 3.95)
    steel.cyl(.1, .7, loc=(ex[0], ex[1], zc + .35), seg=10, bevel=0)                                  # exhaust stack
    steel.cyl(.14, .36, loc=(ex[0], ex[1], zc + .25), seg=10, bevel=0)                                # heat shield
    armor.box((.24, .24, .03), loc=(ex[0], ex[1] + .06, zc + .74), rot=(-.5, 0, 0), bevel=0)         # rain cap
    armor.box((.5, .4, .26), loc=(ex[0] + .1, ex[1] - .45, zc + .1), bevel=.03, seg=1)                # silencer
    # Small flat radar panel on a mast above the tail, spinning on `Radar`.
    steel.cyl(.08, .5, loc=(.3, 3.55, zc + .25), seg=8, bevel=0)
    armor.box((.3, .3, .12), loc=(.3, 3.55, zc + .05), bevel=.02, seg=1)
    rp = a.pivot('Radar', (.3, 3.55, zc + .5))
    ra = a.part('Radar_panel', 'Armor', rp)
    ra.cyl(.1, .1, loc=(0, 0, .05), seg=8, bevel=0)
    pm = _frame((0, 0, .45), (-.25, 0, 0))
    ra.box((.9, .1, .62), loc=pm.to_translation(), rot=(-.25, 0, 0), bevel=.02, seg=1)
    a.part('Radar_face', 'Undercarriage', rp).box((.8, .03, .52), loc=pm @ Vector((0, -.055, 0)), rot=(-.25, 0, 0),
                                                   bevel=0)
    ra.box((.3, .14, .3), loc=pm @ Vector((0, .1, -.06)), rot=(-.25, 0, 0), bevel=0)

    # Beam director: turntable, octagonal azimuth housing, yoke, and the head that tilts on the yoke.
    t = a.pivot('Turret', (0, -.9, 1.56))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tteam = a.part('Turret_body', 'Team', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(.95, .1, loc=(0, 0, .04), seg=20, bevel=.02, bseg=1)
    tteam.prism(chamfered(1.9, 1.8, .42), .64, loc=(0, 0, .4), axis='Z', bevel=.05, taper=.92)
    for s in (-1, 1):
        tarm.box((.05, .7, .4), loc=(s * .925, 0, .38), rot=(0, -s * .12, 0), bevel=.01, seg=1)      # side panels
    a.part('Turret_vents', 'Undercarriage', t).grille(.8, .3, loc=(0, .88, .4), rot=(0, 0, math.pi), slats=3,
                                                       depth=.04, thickness=.03)
    a.part('Turret_labels', 'Hazard', t).box((.3, .03, .12), loc=(.4, -.86, .52), rot=(-.12, 0, 0), bevel=0)
    # Head: a box whose round window sits low on its face (at the game's pivot height, so the head reads as
    # level), the tracking sensor block beside it and the tracker pod on top.
    W, L, Hh, zh = 1.6, 1.35, 1.3, .86
    yf, yr = -.755, .595
    head = a.part('Main_cannon_director', 'Team', t)
    head.box((W, L, Hh), loc=(0, (yf + yr) / 2, zh + Hh / 2), bevel=.06, seg=2)
    pod_top = zh + Hh + .5
    zw = zh + .3 * (pod_top - zh)                                   # the window's centre: the pivot height
    xw = .14
    pod = a.part('Main_cannon_pod', 'Armor', t)
    pod.box((.5, .62, .44), loc=(.42, -.3, pod_top - .22), bevel=.04, seg=1)
    pod.box((.2, .3, .08), loc=(.42, -.2, zh + Hh + .02), bevel=0)                                  # pod neck
    lens = a.part('Main_cannon_lens', 'Glass', t)
    lens.box((.3, .04, .22), loc=(.42, -.62, pod_top - .2), bevel=.01, seg=1)
    fit = a.part('Main_cannon_fittings', 'Steel', t)
    for x in (-.55, .55):
        fit.box((.08, .08, .08), loc=(x, .2, zh + Hh + .02), bevel=0)                               # lifting eyes
    sens = a.part('Main_cannon_sensor', 'Armor', t)
    sens.box((.34, .16, .66), loc=(-.58, yf - .06, zw + .1), bevel=.03, seg=1)
    lens.cyl(.09, .04, loc=(-.58, yf - .15, zw + .28), rot=FORWARD, seg=10, bevel=0)
    lens.box((.2, .04, .14), loc=(-.58, yf - .15, zw - .04), bevel=0)
    fit.cyl(.05, .04, loc=(-.58, yf - .15, zw - .22), rot=FORWARD, seg=8, bevel=0)                  # rangefinder
    bez = a.part('Main_cannon_bezel', 'Armor', t)
    bl, br = _at(_frame((xw, yf + .01, zw), (0, 0, 0)), (0, 0, 0), FORWARD)
    bez.lathe([(.5, -.03), (.5, .06), (.46, .1), (.46, .16), (.42, .16), (.42, .02)], loc=bl, rot=br, seg=20)
    a.part('Main_cannon_window', 'Glass', t).cyl(.43, .03, loc=(xw, yf - .02, zw), rot=FORWARD, seg=20, bevel=0)
    glow = a.part('Main_cannon_glow', 'TeamGlow', t)
    glow.torus(.35, .016, loc=(xw, yf - .045, zw), rot=FORWARD, seg=24, ring=4)                      # emitter ring
    glow.cyl(.07, .012, loc=(xw, yf - .04, zw), rot=FORWARD, seg=10, bevel=0)
    bez.box((1.08, .3, .05), loc=(xw, yf - .12, zw + .56), rot=(-.12, 0, 0), bevel=.01, seg=1)       # sun hood
    for s in (-1, 1):
        bez.box((.05, .5, .4), loc=(s * (W / 2 + .004), -.1, zh + .62), bevel=.01, seg=1)          # side panels
        a.part('Main_cannon_labels', 'Hazard', t).box((.03, .24, .14), loc=(s * (W / 2 + .03), -.1, zh + 1.0),
                                                      bevel=0)
    fit.box((.3, .08, .2), loc=(0, yr + .03, zh + .5), bevel=0)                                      # rear connector
    P = _game_pivot(a, t)
    a.pivot('Muzzle_main', (xw, yf - .06, zw), t)
    # The yoke: arms at the head's rear rising to trunnions on the game's pivot, an elevation drive, cables.
    tz0 = .66
    for s in (-1, 1):
        xa = s * (W / 2 + .12)
        tteam.box((.16, .56, P.z + .24 - tz0), loc=(xa, P.y, (P.z + .24 + tz0) / 2), bevel=.03, seg=1)
        tsteel.cyl(.16, .1, loc=(xa + s * .1, P.y, P.z), rot=ACROSS, seg=12, bevel=.015, bseg=1)
    tarm.cyl(.26, .14, loc=(W / 2 + .3, P.y, P.z), rot=ACROSS, seg=14, bevel=.02, bseg=1)            # drive
    a.part('Turret_cables', 'Undercarriage', t).tube([(-.5, .7, .72), (-.7, .95, .9), (-(W / 2 + .12), P.y + .3,
                                                                                       P.z - .3)], .04, seg=5)


# ----------------------------------------------------------------------------- railgun_truck
def _capacitor_container(a, y0, y1, z0, z1, hw, roof='bank'):
    """Capacitor bank container on the deck from y0 to y1: ribbed Team walls, corner posts, side doors with
    high-voltage labels and status lights, a hazard band along the bottom and a roof of either capacitor
    terminals joined by copper bus bars ('bank') or louvred cooling panels ('louvres')."""
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    ym = (y0 + y1) / 2
    body.box((2 * hw, y1 - y0, z1 - z0), loc=(0, ym, (z0 + z1) / 2), bevel=.05, seg=1)
    for sx in (-1, 1):
        for yy in (y0 + .05, y1 - .05):
            armor.box((.1, .1, z1 - z0 + .02), loc=(sx * (hw - .03), yy, (z0 + z1) / 2), bevel=0)      # corner posts
        n = max(2, int((y1 - y0) / .42))
        for i in range(n):
            y = y0 + .25 + i * (y1 - y0 - .5) / (n - 1)
            if abs(y - ym) < .45:
                continue
            armor.box((.04, .06, z1 - z0 - .3), loc=(sx * (hw + .01), y, (z0 + z1) / 2), bevel=0)      # wall ribs
        armor.box((.05, .74, .95), loc=(sx * (hw + .015), ym, (z0 + z1) / 2 + .04), bevel=.012, seg=1)  # door
        steel.box((.04, .05, .22), loc=(sx * (hw + .045), ym + .26, (z0 + z1) / 2 + .04), bevel=0)
        a.part('Labels', 'Hazard').box((.03, .3, .22), loc=(sx * (hw + .03), ym - .1, (z0 + z1) / 2 + .3), bevel=0)
        a.part('Status_lights', 'Energy').box((.03, .16, .05), loc=(sx * (hw + .02), y1 - .35, z1 - .2), bevel=0)
        _stripe_band(a, (sx * (hw + .002), ym, z0 + .1), '+x' if sx > 0 else '-x', y1 - y0 - .3, .12, pitch=.36)
    if roof == 'bank':
        terms = a.part('Terminals', 'Steel')
        bus = a.part('Bus_bars', 'Rust')
        for x in (-.72, 0, .72):
            ys = [y0 + .35 + i * (y1 - y0 - .7) / 3 for i in range(4)]
            for y in ys:
                a.part('Terminal_caps', 'Armor').cyl(.17, .08, loc=(x, y, z1 + .03), seg=8, bevel=0)
                terms.cyl(.07, .1, loc=(x, y, z1 + .1), seg=6, bevel=0)
        for i in range(4):
            bus.box((1.56, .1, .04), loc=(0, y0 + .35 + i * (y1 - y0 - .7) / 3, z1 + .15), bevel=0)
    else:
        dark = a.part('Chassis', 'Undercarriage')
        for x in (-.62, .62):
            dark.grille(.9, (y1 - y0) - .7, loc=(x, ym, z1 + .02), rot=(-R90, 0, 0), slats=6, depth=.05, thickness=.04)
            _grille_frame(a, x, ym, z1, .9, (y1 - y0) - .7, t=.05)


def railgun_truck(a):
    """Heavy 8x8 electromagnetic railgun carrier (Japanese ATLA / US Navy EMRG lineage) on a wide MZKT-style
    chassis: a four-door cab with a raked split windscreen, wipers, visor, mirrors, grille and a striped lamp
    bumper; two capacitor bank containers behind it (a louvred power conditioning unit and a bank whose
    roof carries rows of terminals joined by copper bus bars), cooling pipes along their roofs and heavy
    power cables running back to the mount; fuel tank, spare wheel, lockers and four big stabiliser jacks
    on the chassis. The railgun turns on `Turret` at the rear: a turntable, a low carriage, tall trunnion
    brackets and elevation rams, an armature magazine, and the 7 m rectangular twin-rail barrel
    (`Main_cannon`) with copper bus-bar rails between Team clamp bands, a breech block, a cradle sleeve
    and a squared muzzle (`Muzzle_brake`), laid 4 degrees up over the containers and the cab."""
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    axles = (-4.2, -2.6, 2.35, 3.95)
    _running_gear(a, axles, 1.22, .66, .52, (-5.1, 5.2), 1.05)
    # Wide four-door cab, kept below the barrel's sweep (its roof at 2.97 m, everything on it under 3.1 m).
    F0, F1 = (-5.46, 2.1), (-5.24, 2.88)
    body.prism([(-5.42, 1.4), F0, F1, (-5.08, 2.97), (-3.62, 2.97), (-3.62, 1.4)], 2.9, bevel=.07)
    wr = _glacis(F0, F1, .5, 0)[2]
    sy, sz, _ = _glacis(F0, F1, 1.0, .03)
    for x in (-.9, 0, .9):
        _plate_frame(a, F0, F1, .5, x, .76, .54)
        _wiper(a, F0, F1, .14, .8, x - .26, x + .1)
        armor.box((.86, .16, .06), loc=(x, sy - .12, sz + .03), rot=(wr - 1.2, 0, 0), bevel=.012, seg=1)   # shutters
        for dx in (-.34, .34):
            steel.box((.06, .1, .1), loc=(x + dx, sy - .01, sz - .03), rot=(wr, 0, 0), bevel=0)          # hinges
    dark.grille(1.9, .44, loc=(0, -5.455, 1.74), rot=(-.06, 0, 0), slats=5, depth=.05, thickness=.045)
    for x in (-1.0, 1.0):
        armor.box((.06, .06, .54), loc=(x, -5.46, 1.74), bevel=0)
    steel.box((2.96, .28, .3), loc=(0, -5.47, 1.22), bevel=.04, seg=1)                                # bumper
    for s in (-1, 1):
        _headlight(a, s * 1.02, -5.61, 1.24, guard=False)
        a.part('Marker_lights', 'Alloy').box((.14, .05, .08), loc=(s * .7, -5.625, 1.24), bevel=0)
        steel.box((.16, .16, .14), loc=(s * .5, -5.64, 1.1), bevel=.02, seg=1)                       # tow hooks
        _stripe_band(a, (s * 1.3, -5.61, 1.22), '-y', .32, .22)
        ox = 1.45
        for y in (-4.95, -4.15):
            _side_window(a, s, ox, y, 2.42, .6, .42)
        for y in (-5.35, -4.55, -3.72):
            armor.box((.03, .04, 1.3), loc=(s * (ox + .006), y, 2.02), bevel=0)                       # door lines
        for y in (-4.7, -3.9):
            steel.box((.04, .16, .05), loc=(s * (ox + .02), y, 2.1), bevel=0)
        for y, zz in ((-5.02, .96), (-5.02, .64), (-3.4, .96), (-3.4, .64)):
            steel.box((.3, .24, .04), loc=(s * 1.3, y, zz), bevel=0)                                 # steps
        for y in (-5.02, -3.4):
            steel.box((.04, .26, .5), loc=(s * 1.46, y, .88), bevel=0)
        _mirror(a, s, (s * 1.42, -5.2, 2.72), out=.1)
        armor.box((.6, 1.5, .06), loc=(s * 1.22, -2.6, 1.47), bevel=.015, seg=1)                     # mudguard
        a.part('Mud_flaps', 'Rubber').box((.5, .04, .44), loc=(s * 1.22, -1.85, .84), bevel=0)
        _whip(a, s * 1.25, -5.15, 2.97, 1.3)                                  # beyond the barrel's reach
    for x in (-.8, -.27, .27, .8):
        a.part('Marker_lights', 'Alloy').box((.1, .05, .05), loc=(x, -5.12, 2.975), bevel=0)
    _hatch(a, .75, -4.3, 2.96, .27)
    armor.box((.9, .6, .1), loc=(-.55, -4.1, 3.0), bevel=.02, seg=1)                                # air conditioner
    dark.grille(.7, .4, loc=(-.55, -4.1, 3.055), rot=(-R90, 0, 0), slats=3, depth=.03, thickness=.025)

    # Deck, subframe, chassis equipment, jacks, tail.
    zd = 1.66
    armor.box((2.9, 9.0, .12), loc=(0, 1.0, zd - .06), bevel=.02, seg=1)
    for s in (-1, 1):
        dark.box((.22, 8.9, .3), loc=(s * .5, 1.0, zd - .27), bevel=0)
        armor.box((.06, 9.0, .08), loc=(s * 1.44, 1.0, zd), bevel=0)                                   # deck edges
        armor.box((.62, 3.0, .06), loc=(s * 1.22, 3.15, zd - .15), bevel=.015, seg=1)                 # mudguards
        a.part('Mud_flaps', 'Rubber').box((.5, .04, .44), loc=(s * 1.22, 4.75, .84), bevel=0)
        _jack(a, s * 1.36, 1.2, zd - .12, pad=.26)
        _jack(a, s * 1.2, 5.05, zd - .12, pad=.24)
        _taillight(a, s * 1.0, 5.5, 1.36)
        for y in (-1.8, .2, 2.4, 4.4):
            steel.box((.04, .1, .06), loc=(s * 1.465, y, zd - .04), bevel=0)                          # tie-downs
    _fuel_tank(a, 1.1, -1.05, 1.02, 1.4, r=.3)
    armor.box((.4, .8, .56), loc=(1.18, .25, 1.06), bevel=.03, seg=1)                                 # locker
    steel.box((.03, .06, .08), loc=(1.39, .25, 1.18), bevel=0)
    _spare_wheel(a, (-1.12, -1.0, .86), .62, .46, axis='x')
    steel.box((.1, .5, .1), loc=(-.78, -1.0, .86), bevel=0)
    steel.box((.1, .1, .6), loc=(-.78, -1.0, 1.2), bevel=0)
    armor.box((.4, .8, .56), loc=(-1.18, .25, 1.06), bevel=.03, seg=1)                                # battery box
    dark.box((2.6, .14, .26), loc=(0, 5.38, 1.3), bevel=0)                                           # crossmember
    steel.box((2.7, .18, .22), loc=(0, 5.5, 1.04), bevel=.03, seg=1)
    _stripe_band(a, (0, 5.59, 1.04), '+y', 2.6, .18)
    _ladder(a, .6, 5.64, .4, zd, width=.4)
    a.part('Extinguisher', 'BarrelRed').cyl(.09, .5, loc=(-1.2, 4.55, zd + .25), seg=8, bevel=.02, bseg=1)
    steel.box((.2, .06, .3), loc=(-1.2, 4.66, zd + .25), bevel=0)
    _stowage_bin(a, (-.9, 5.05, zd), (.9, .5, .4), latch_side=0)
    armor.box((1.1, .6, .03), loc=(.6, 4.6, zd + .005), bevel=0)                                      # tread plate
    for s in (-1, 1):                                                                                 # rear rails
        _rail(a, [(s * 1.38, 4.55, zd), (s * 1.38, 4.55, zd + .7), (s * 1.38, 5.35, zd + .7), (s * 1.38, 5.35, zd)])

    # Capacitor bank containers, cooling pipes along their roofs and down to the deck, power cables to the mount.
    zc = 2.94
    _capacitor_container(a, -3.45, -1.5, zd, zc, 1.4, roof='louvres')
    _capacitor_container(a, -1.35, .75, zd, zc, 1.4, roof='bank')
    pipes = a.part('Coolant_pipes', 'Pipe')
    cables = a.part('Power_cables', 'Rubber')
    for s in (-1, 1):
        x = s * 1.2
        pipes.tube([(x, -3.3, zc + .06), (x, .95, zc + .06), (x, .95, zd + .12), (s * .95, 1.5, zd + .12)], .05, seg=6)
        for y in (-2.4, -.3):
            steel.box((.14, .1, .08), loc=(x, y, zc + .03), bevel=0)                                  # pipe clamps
        cables.tube([(s * .45, .76, 2.3), (s * .45, 1.0, 2.2), (s * .45, 1.08, zd + .08), (s * .45, 1.5, zd + .08)],
                    .07, seg=6)
    armor.box((1.4, .2, .18), loc=(0, 1.5, zd + .08), bevel=.02, seg=1)                             # deck junction box
    armor.box((1.2, .12, .3), loc=(0, .82, 2.3), bevel=.02, seg=1)                                  # cable glands

    # The railgun mount: turntable, carriage, magazine and brackets; the barrel group on the game's pivot.
    t = a.pivot('Turret', (0, 2.95, zd))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tteam = a.part('Turret_body', 'Team', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(1.25, .1, loc=(0, 0, .04), seg=24, bevel=.02, bseg=1)
    tteam.prism(chamfered(2.3, 2.5, .6), .44, loc=(0, 0, .31), axis='Z', bevel=.04, taper=.95)       # carriage
    pitch = math.radians(4)
    T = Vector((0, -.15, 1.92))                                     # nominal trunnion
    at = _axis(T, pitch)
    brot = (-pitch, 0, 0)

    def bb(part, size, s, up=0.0, side=0.0, bevel=0.0):
        part.box(size, loc=at(s, up, side), rot=brot, bevel=bevel, seg=1)
    Lb = 6.6
    # Barrel: a dark core with the two copper rails running along its top edges, Team U-clamps round its
    # sides and belly and steel straps bolted across the top between the rails.
    core = a.part('Main_cannon', 'Armor', t)
    bb(core, (.38, Lb + .45, .46), (Lb - .45) / 2, bevel=.02)
    rails = a.part('Main_cannon_rails', 'Rust', t)
    for side in (-.19, .19):
        bb(rails, (.1, Lb - .72, .16), (Lb + .72) / 2, up=.24, side=side)                              # copper rails
    bands = a.part('Main_cannon_bands', 'Team', t)
    bolts = a.part('Main_cannon_bolts', 'Steel', t)
    for i in range(8):
        sb = 2.8 + i * .5
        bb(bands, (.56, .1, .5), sb, up=-.01, bevel=.01)
        bb(bolts, (.28, .07, .03), sb, up=.245)
        for side in (-.1, .1):
            bb(bolts, (.04, .04, .03), sb, up=.27, side=side)
    breech = a.part('Main_cannon_breech', 'Armor', t)
    bb(breech, (.76, 1.15, .74), .12, bevel=.04)                                                      # breech block
    sleeve = a.part('Main_cannon_sleeve', 'Team', t)
    bb(sleeve, (.68, 1.9, .6), 1.62, bevel=.03)                                                       # cradle sleeve
    for s_ in (.95, 2.3):
        bb(sleeve, (.72, .12, .64), s_, bevel=.01)
    bus = a.part('Main_cannon_busbars', 'Rust', t)
    for side in (-.18, .18):
        bb(bus, (.14, .06, .5), -.47, up=.02, side=side)                                             # bus-bar straps
        bb(bus, (.14, .5, .05), -.22, up=.38, side=side)
    bb(bolts, (.5, .08, .08), .66, up=.36)
    for side in (-.37, .37):
        bb(a.part('Main_cannon_fittings', 'Armor', t), (.06, 1.5, .16), 1.6, up=.08, side=side)        # cooling jackets
    for side in (-.39, .39):
        a.part('Main_cannon_glow', 'Energy', t).box((.03, .2, .06), loc=at(.3, .15, side), rot=brot, bevel=0)
    mz = a.part('Muzzle_brake', 'Armor', t)
    for side in (-.24, .24):
        bb(mz, (.26, .36, .72), Lb + .15, side=side, bevel=.02)                                        # muzzle cheeks
    for up in (-.25, .25):
        bb(mz, (.74, .36, .22), Lb + .15, up=up, bevel=.02)
    bb(a.part('Muzzle_brake_band', 'Team', t), (.78, .08, .76), Lb + .08, bevel=.01)
    bb(a.part('Muzzle_brake_bore', 'Undercarriage', t), (.24, .04, .3), Lb + .06)
    for side in (-.09, .09):
        bb(a.part('Muzzle_brake_rails', 'Rust', t), (.04, .3, .3), Lb + .18, side=side)
    a.pivot('Muzzle_main', tuple(at(Lb + .34)), t)
    P = _game_pivot(a, t)
    # Brackets and trunnion caps on the game's pivot, elevation rams, the magazine and power feeds.
    for s in (-1, 1):
        x = s * .5
        tarm.prism([(-.55, .5), (.52, .5), (.34, P.z - .12), (.17, P.z + .2), (-.2, P.z + .2), (-.42, P.z)], .16,
                   loc=(x, P.y, 0), bevel=.03)                                                        # brackets
        tteam.box((.2, .9, .3), loc=(s * .5, P.y, .62), bevel=.03, seg=1)                             # bracket feet
        tsteel.cyl(.2, .12, loc=(s * .62, P.y, P.z), rot=ACROSS, seg=14, bevel=.02, bseg=1)
        tsteel.cyl(.09, .06, loc=(s * .7, P.y, P.z), rot=ACROSS, seg=8, bevel=0)
        _ram(a, (s * .3, -1.0, .52), tuple(at(1.9, -.3, s * .22)), .08, parent=t)
    tarm.box((1.3, .8, .44), loc=(0, 1.05, .75), bevel=.04, seg=1)                                   # armature magazine
    tsteel.box((.3, .5, .12), loc=(0, .62, 1.0), rot=(.5, 0, 0), bevel=0)                             # feed chute
    a.part('Turret_labels', 'Hazard', t).box((.4, .03, .14), loc=(0, 1.46, .8), bevel=0)
    for s in (-1, 1):
        a.part('Turret_cables', 'Rubber', t).tube([(s * .35, .9, .55), (s * .3, .55, .95), (s * .2, .2, P.z - .5)],
                                                  .06, seg=6)
        a.part('Turret_pipes', 'Pipe', t).tube([(s * .8, .6, .55), (s * .75, .3, 1.0), (s * .62, .05, P.z - .25)],
                                               .04, seg=6)
    tarm.box((.5, .5, .3), loc=(.62, -.85, .6), bevel=.03, seg=1)                                    # control box
    a.part('Turret_glass', 'Glass', t).box((.3, .03, .14), loc=(.62, -1.105, .64), bevel=0)


BUILDERS = {
    'lancet_truck': (lancet_truck, dict(ao_distance=.6, grime_height=.55)),
    'shahed_truck': (shahed_truck, dict(ao_distance=.6, grime_height=.55)),
    'iron_beam': (iron_beam, dict(ao_distance=.6, grime_height=.55)),
    'railgun_truck': (railgun_truck, dict(ao_distance=.6, grime_height=.55)),
}
