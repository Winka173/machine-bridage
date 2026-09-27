"""Machine Brigade support vehicles, drops and battlefield devices, built with frontier_kit.

Vehicles (origin on the ground at the footprint centre, Blender -Y is the front):
  * engineer_vehicle: tracked armoured recovery and engineering vehicle (BREM-1 / M88 lineage)
    with a hazard-striped dozer blade, a crane boom folded along the right of the deck, a rear
    winch, tool boxes, spare track links, tow cables and a work light bar. `Turret` is a small
    remote weapon station on the cab roof; `Muzzle_main` is its machine gun.
  * ew_jammer: 6x6 electronic-warfare jamming truck: a boxy shelter body with a generator, two
    raised telescopic masts carrying antenna arrays, whip antennas and a dish on the `Radar`
    pivot (spins about Z). `Turret` is a roof remote weapon station with `Muzzle_main` (machine
    gun).
  * fpv_carrier: armoured 6x6 MRAP truck launching FPV kamikaze drones. `Turret` carries the rear
    launcher rack of drone cells, facing up and back, with quadcopters sitting in the open cells;
    `Muzzle_main` is at the top centre of the rack's open face. A roof `Mount_mg` holds a
    remote-weapon machine gun with `Muzzle_mg`.
  * mine_layer: tracked mine layer (GMZ-3 / MT-LB lineage): mine hoppers and racks of mines on the
    deck, a rear dispensing chute and ploughshare lowered to the ground. `Turret` is a small roof
    machine-gun turret with `Muzzle_main`.
Small models:
  * mine: anti-tank mine half-buried in a scuffed dirt ring, a TeamGlow light on top (prop).
  * fpv_drone: FPV kamikaze quadcopter projectile with an RPG-style charge; flies along -Y,
    origin at its centre. Propellers are plain parts (no spin pivots).
  * supply_crate / repair_crate: air-dropped crates on pallets. The canopy and its lines sit
    under a `Parachute` empty that the game hides on landing; like Bombs, those parts receive
    ambient occlusion but never cast it onto the crate.

The machine guns on the vehicles' `Turret` are not named Main_cannon, so they do not recoil (the
runtime recoil is sized for tank guns). Conventions
and helpers are those of mb_vehicles.py; touching parts overlap or stand at least 1 cm apart, never
face to face (coplanar faces z-fight).
"""
import math

from mathutils import Matrix, Vector, noise

import mb_weapons as wpn
from frontier_kit import chamfered

from mb_vehicles import (ACROSS, FORWARD, R90, _antenna, _cable, _dish, _exhaust, _flank, _frame, _glacis,
                         _grille_frame, _hatch, _headlight, _jerrycans, _periscopes, _pick, _rail, _rws, _shovel,
                         _stowage_bin, _taillight, _track_links, _wheel, tracks)

TAU = math.tau


# ----------------------------------------------------------------------------- helpers
def _plane(origin, ax, ay):
    """Frame at origin with local X along ax and local Y along ay (made orthogonal); local Z = X x Y
    points out of the face."""
    ax = Vector(ax).normalized()
    ay = Vector(ay)
    ay = (ay - ax * ay.dot(ax)).normalized()
    az = ax.cross(ay)
    o = Vector(origin)
    return Matrix(((ax.x, ay.x, az.x, o.x), (ax.y, ay.y, az.y, o.y), (ax.z, ay.z, az.z, o.z), (0, 0, 0, 1)))


def _clip_x(poly, x0, x1):
    """Clip a convex polygon [(x, y)...] to x0 <= x <= x1."""
    def cut(pts, keep, edge):
        out = []
        for i, p in enumerate(pts):
            q = pts[(i + 1) % len(pts)]
            pin, qin = keep(p), keep(q)
            if pin:
                out.append(p)
            if pin != qin:
                t = (edge - p[0]) / (q[0] - p[0])
                out.append((edge, p[1] + (q[1] - p[1]) * t))
        return out
    poly = cut(poly, lambda p: p[0] >= x0, x0)
    return cut(poly, lambda p: p[0] <= x1, x1) if poly else poly


def _stripes(a, m, width, height, pitch=.3, parent=None, lean=.7, t=.02, sink=.01,
             mats=('SafetyStripe', 'Charred'), names=('Stripes', 'Stripes_dark')):
    """Painted hazard band on the face frame m (local X along the band, Y up it, Z out of the
    face): alternating diagonal stripes pitch / 2 wide, each a tile t thick whose back sinks
    `sink` into the face, so the band reads as paint standing proud of the surface. A None
    material skips that colour (dark stripes laid over a yellow strap)."""
    rot = m.to_euler('XYZ')
    loc = m @ Vector((0, 0, t / 2 - sink))
    s = height * math.tan(lean)
    half = pitch / 2
    x = -width / 2 - s
    k = 0
    while x < width / 2:
        tile = [(x, -height / 2), (x + half, -height / 2), (x + half + s, height / 2), (x + s, height / 2)]
        tile = _clip_x(tile, -width / 2, width / 2)
        if len(tile) >= 3 and mats[k % 2]:
            area = .5 * abs(sum(tile[i][0] * tile[i - 1][1] - tile[i - 1][0] * tile[i][1] for i in range(len(tile))))
            if area > 4e-4:
                a.part(names[k % 2], mats[k % 2], parent).prism(tile, t, loc=loc, rot=rot, axis='Z', bevel=0)
        x += half
        k += 1


def _along(p0, p1):
    """Location (midpoint), rotation and length of a cylinder spanning p0 -> p1."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    rot = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_euler('XYZ')
    return (p0 + p1) / 2, rot, d.length


def _rod(part, p0, p1, r, seg=8, bevel=0.0):
    loc, rot, length = _along(p0, p1)
    part.cyl(r, length, loc=loc, rot=rot, seg=seg, bevel=bevel, bseg=1)


def _ram(a, p0, p1, r, parent=None, split=.6, seg=8):
    """Hydraulic ram from p0 (barrel end) to p1 (rod end): a painted barrel, a thinner steel rod."""
    p0, p1 = Vector(p0), Vector(p1)
    mid = p0.lerp(p1, split)
    _rod(a.part('Rams', 'Armor', parent), p0, mid, r, seg=seg)
    _rod(a.part('Ram_rods', 'Steel', parent), mid - (p1 - p0).normalized() * .05, p1, r * .55, seg=seg)


def _beacon(a, x, y, z, parent=None, mat='Alloy', r=.075):
    """Rotating warning beacon: steel base and a glowing dome."""
    a.part('Beacon_base', 'Steel', parent).cyl(r * .9, .05, loc=(x, y, z + .015), seg=8, bevel=0)
    a.part('Beacons', mat, parent).sphere((r, r, r * 1.2), loc=(x, y, z + .04), seg=8, rings=6, cut=0)


def _whip(a, x, y, z, height, parent=None, r=.011):
    """Whip antenna on a spring base (no glowing tip)."""
    steel = a.part('Whips', 'Steel', parent)
    steel.cyl(.035, .12, loc=(x, y, z + .05), seg=6, bevel=0)
    steel.cyl(r, height, loc=(x, y, z + .1 + height / 2), seg=4, bevel=0)


def _rws_turret(a, loc, parent=None, length=.8, sensor=True, shield=False):
    """Small remote weapon station on the `Turret` pivot: base ring, armoured cradle, sensor head,
    ammunition box and a machine gun whose opening is `Muzzle_main`."""
    t = a.pivot('Turret', loc, parent)
    body = a.part('RWS_body', 'Armor', t)
    a.part('RWS_ring', 'Steel', t).cyl(.27, .08, loc=(0, 0, .03), seg=14, bevel=.015, bseg=1)
    body.box((.38, .5, .26), loc=(0, .05, .2), bevel=.035, seg=1)                 # cradle
    body.box((.14, .26, .2), loc=(.27, .12, .22), bevel=.02, seg=1)               # ammunition box
    if sensor:
        body.box((.2, .26, .22), loc=(-.28, .0, .3), bevel=.03, seg=1)            # sensor head
        a.part('RWS_sensor', 'Glass', t).box((.14, .03, .12), loc=(-.28, -.135, .31), bevel=0)
    if shield:
        body.box((.5, .04, .26), loc=(.02, -.24, .31), rot=(-.15, 0, 0), bevel=.01, seg=1, taper=(.85, 1))
    gun = a.part('RWS_gun', 'Steel', t)
    gun.box((.12, .4, .12), loc=(.06, -.22, .31), bevel=.015, seg=1)             # receiver
    front = -.42
    gun.cyl(.026, length, loc=(.06, front - length / 2 + .02, .31), rot=FORWARD, seg=8, bevel=0)
    gun.cyl(.04, .11, loc=(.06, front - length + .055, .31), rot=FORWARD, seg=8, bevel=0)   # flash hider
    a.pivot('Muzzle_main', (.06, front - length, .31), t)
    return t


def _light_bar(a, x0, x1, y, z, lamps=4, parent=None, facing=-1):
    """Work light bar on two posts at height z: a steel bar with `lamps` flood lights facing
    `facing` (-1 front) and an amber beacon at each end."""
    steel = a.part('Light_bar', 'Steel', parent)
    steel.box((x1 - x0, .06, .06), loc=((x0 + x1) / 2, y, z + .14), bevel=0)
    for x in (x0 + .12, x1 - .12):
        steel.box((.05, .04, .15), loc=(x, y, z + .06), bevel=0)
    for i in range(lamps):
        x = x0 + .3 + i * (x1 - x0 - .6) / max(1, lamps - 1)
        a.part('Light_housing', 'Armor', parent).box((.17, .1, .13), loc=(x, y + facing * .06, z + .15), bevel=0)
        a.part('Lamps', 'Lamp', parent).box((.13, .02, .09), loc=(x, y + facing * .115, z + .15), bevel=0)
    for x in (x0 - .02, x1 + .02):
        _beacon(a, x, y, z + .16, parent)


# ----------------------------------------------------------------------------- engineer vehicle
def engineer_vehicle(a):
    """Armoured recovery and engineering vehicle (BREM-1 / M88 lineage) on a tank chassis: a
    hazard-striped dozer blade on push arms and rams, a crew cab on the left front with a work light
    bar, vision blocks and a small remote weapon station, a telescopic crane boom folded along the
    right of the deck on a slewing base with a hook block, a recovery winch and fairlead at the
    rear, tool boxes and tools on the fenders, spare track links, tow cables and a stowed tow bar."""
    F, B = -.12, .12                                       # front and rear overhang shifts
    tracks(a, 1.26, 6.3 + B - F, .9, .3, 6, .48, belt_width=.58, wheel_seg=10, lean=True, sprocket=1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    nose, brow = (-3.35 + F, 1.0), (-2.78, 1.5)
    rear = 3.2 + B
    hull.prism([(-3.08 + F, .56), nose, brow, (rear - .2, 1.5), (rear, 1.32), (rear, .56)], 2.3, bevel=.06)
    # Crew cab on the left front: sloped front plate, flat roof.
    cab_x, cab_w = -.38, 1.48
    cab_front = ((-2.74, 1.45), (-2.46, 2.3))
    a.part('Cab', 'Team').prism([cab_front[0], cab_front[1], (-.5, 2.34), (-.42, 2.22), (-.42, 1.45)], cab_w,
                                loc=(cab_x, 0, 0), bevel=.05)

    def roof(y):
        return 2.3 + .04 * (y + 2.46) / 1.96
    # Front plate: driver's vision blocks up top, spare track links below them.
    gy, gz, grot = _glacis(*cab_front, .86, .012)
    for dx in (-.16, 0, .16):
        a.part('Vision_blocks', 'Glass').box((.12, .07, .05), loc=(-.78 + dx, gy, gz), rot=(grot, 0, 0), bevel=0)
    gy, gz, grot = _glacis(*cab_front, .36, 0)
    _track_links(a, _frame((-.2, gy, gz), (grot, 0, 0)), 3, width=.42)
    _track_links(a, _frame((-.85, gy, gz), (grot, 0, 0)), 2, width=.42)
    # Roof: work light bar along the front edge, hatches, periscopes, the RWS and an antenna.
    _light_bar(a, -1.0, .24, -2.3, roof(-2.3) - .01)
    _hatch(a, -.84, -1.9, roof(-1.9), .23)
    _hatch(a, -.02, -.85, roof(-.85), .24, hinge=-1)
    _periscopes(a, [(x, -2.06, roof(-2.06), 0) for x in (-.42, -.22)] +
                [(-1.1, y, roof(y), -R90) for y in (-1.5, -1.0)] + [(.3, -1.35, roof(-1.35), R90)])
    # Left side: crew door with a vision block and handle, a grab rail behind it.
    armor.box((.05, .7, .62), loc=(-1.135, -1.65, 1.88), bevel=0)
    steel.box((.04, .16, .04), loc=(-1.17, -1.45, 1.86), bevel=0)
    a.part('Vision_blocks', 'Glass').box((.04, .16, .07), loc=(-1.165, -1.8, 2.08), bevel=0)
    _rail(a, [(-1.1, -1.12, 2.0), (-1.17, -1.12, 2.0), (-1.17, -.62, 2.0), (-1.1, -.62, 2.0)])
    # Welding gas bottles in a rack against the cab's rear wall.
    for x, mat in ((-1.0, 'Fuel'), (-.76, 'Fuel'), (-.52, 'BarrelRed')):
        a.part(f'Gas_bottles_{mat}', mat).lathe([(.1, 1.49), (.1, 2.2), (.07, 2.29), (.035, 2.33), (.035, 2.37)],
                                                loc=(x, -.28, 0), seg=8)
        steel.cyl(.045, .06, loc=(x, -.28, 2.39), seg=6, bevel=0)                         # valve caps
    for z in (1.72, 2.06):
        steel.box((.78, .03, .05), loc=(-.76, -.175, z), bevel=0)                         # straps
    for x in (-1.14, -.38):
        steel.box((.04, .26, .6), loc=(x, -.3, 1.8), bevel=0)                             # rack posts
    _antenna(a, None, -.95, 2.95 + B, 1.5, 1.3)
    steel.box((.09, .09, .06), loc=(-.95, 2.95 + B, 1.51), bevel=0)
    # Lower hull front: headlights, tow hooks.
    for s in (-1, 1):
        steel.box((.16, .2, .14), loc=(s * .45, -3.18 + F, .74), bevel=0)
    gy, gz, grot = _glacis(nose, brow, .7, .02)
    _headlight(a, -.95, gy - .02, gz + .1, guard=False)
    _headlight(a, 1.0, gy - .02, gz + .1, guard=False)
    gy, gz, grot = _glacis(nose, brow, .92, 0)
    steel.bolts([(x, gy, gz) for x in (-.9, -.6, -.3, 0, .3, .6)], r=.03, h=.03, rot=(grot, 0, 0), bevel=0)

    # Dozer blade raised for travel: a concave moldboard with a steel cutting edge and top lip, end
    # plates, back ribs, push arms into the lower hull and two lift rams; hazard band across its face.
    def fy(pts):
        return [(y + F, z) for y, z in pts]
    front = fy([(-3.74, .3), (-3.64, .48), (-3.6, .66), (-3.6, .92), (-3.64, 1.1)])
    back = [(y + .08, z) for y, z in reversed(front)]
    a.part('Blade', 'Team').prism(front + back, 3.24, bevel=.015)
    steel.box((3.26, .1, .07), loc=(0, -3.73 + F, .31), rot=(.5, 0, 0), bevel=0)         # cutting edge
    steel.box((3.26, .12, .05), loc=(0, -3.6 + F, 1.115), bevel=0)                        # top lip
    for s in (-1, 1):
        armor.prism(fy([(-3.77, .28), (-3.68, 1.14), (-3.5, 1.1), (-3.5, .34)]), .05, loc=(s * 1.64, 0, 0), bevel=0)
        armor.box((.1, .26, .1), loc=(s * .8, -3.45 + F, .55), bevel=0)                  # arm lugs
        armor.limb((s * .8, -3.5 + F, .52), (s * .8, -3.02 + F, .66), .14, .16, bevel=0)          # push arms
        _ram(a, (s * .45, -3.05 + F, 1.18), (s * .45, -3.55 + F, .97), .06)
    for x in (-1.25, -.4, .4, 1.25):                                                      # back ribs
        armor.prism(fy([(-3.64, .36), (-3.57, .5), (-3.54, .66), (-3.54, .92), (-3.565, 1.06), (-3.44, 1.0),
                        (-3.41, .44)]), .06, loc=(x, 0, 0), bevel=0)
    _stripes(a, _plane((0, -3.6 + F, .79), (1, 0, 0), (0, 0, 1)), 3.2, .24, pitch=.34)

    # Crane: slewing base at the right rear, telescopic box boom folded forward on a travel rest,
    # luffing ram under it, sheave head with a striped tip, hook block hanging off the head.
    cx = .68
    crane = a.part('Crane', 'Team')
    steel.cyl(.5, .12, loc=(cx, 2.3, 1.54), seg=16, bevel=.02, bseg=1)
    crane.box((.86, .92, .5), loc=(cx, 2.32, 1.85), bevel=.05, taper=(.9, .92))
    for s in (-1, 1):
        armor.box((.07, .36, .34), loc=(cx + s * .21, 2.02, 2.12), bevel=0)                # pivot cheeks
    steel.cyl(.07, .52, loc=(cx, 2.02, 2.16), rot=ACROSS, seg=10, bevel=0)             # pivot pin
    armor.box((.5, .3, .28), loc=(cx, 2.72, 2.0), bevel=.03, seg=1)                     # hydraulic pack
    a.part('Lamps', 'Lamp').box((.12, .02, .09), loc=(cx - .31, 1.855, 2.0), bevel=0)  # boom spotlight
    a.part('Light_housing', 'Armor').box((.16, .08, .13), loc=(cx - .31, 1.9, 2.0), bevel=0)
    tip = Vector((cx, -2.2, 1.98))
    crane.limb((cx, 2.12, 2.16), tuple(tip), .34, .42, bevel=.03, seg=1)                # boom
    a.part('Boom_inner', 'Armor').limb(tuple(tip + Vector((0, .2, 0))), (cx, -2.42, 1.97), .26, .32, bevel=.02,
                                       seg=1)
    head = Vector((cx, -2.5, 1.99))
    armor.box((.3, .2, .3), loc=head, bevel=0)
    for s in (-1, 1):
        armor.box((.03, .24, .26), loc=head + Vector((s * .11, -.04, -.16)), bevel=0)      # sheave cheeks
        _stripes(a, _plane(head + Vector((s * .15, 0, 0)), (0, s, 0), (0, 0, 1)), .18, .26, pitch=.16, lean=.6)
    steel.cyl(.11, .18, loc=head + Vector((0, -.06, -.19)), rot=ACROSS, seg=12, bevel=0)  # sheave
    for dx in (-.05, .05):
        _rod(steel, head + Vector((dx, -.15, -.24)), head + Vector((dx, -.15, -.37)), .01, seg=4)
    a.part('Hook_block', 'Hazard').box((.18, .12, .16), loc=head + Vector((0, -.15, -.42)), bevel=0)
    steel.torus(.05, .015, loc=head + Vector((0, -.27, -.4)), rot=(0, R90, 0), seg=8, ring=4)
    for s in (-1, 1):                                                                      # travel rest
        armor.box((.07, .07, .3), loc=(cx + s * .15, -1.6, 1.64), bevel=0)
    armor.box((.44, .12, .06), loc=(cx, -1.6, 1.79), bevel=0)
    _ram(a, (cx, 1.9, 1.72), (cx, .5, 1.86), .075)

    def boom_z(y):
        return 2.16 + (1.98 - 2.16) * (2.12 - y) / 4.32
    y0, y1 = -2.15, -1.35                                     # hazard band across the top of the boom tip
    top = Vector((cx, (y0 + y1) / 2, boom_z((y0 + y1) / 2) + .21))
    _stripes(a, _plane(top, (0, -4.32, -.18), (1, 0, 0)), y1 - y0, .28, pitch=.2, lean=.6)
    for y in (-1.2, -.2, .8):                                                              # side stiffeners
        for s in (-1, 1):
            armor.box((.03, .08, .34), loc=(cx + s * .18, y, boom_z(y)), bevel=0)
    a.part('Hoses', 'Undercarriage').tube([(cx + .2, 1.95, 1.9), (cx + .2, 1.2, boom_z(1.2) - .1),
                                           (cx + .2, -2.1, boom_z(-2.1) - .1), (cx + .16, -2.38, 1.9)], .02, seg=4)
    # Rear deck left: engine grille and the recovery winch with its cable to the rear fairlead.
    deck.grille(.8, 1.0, loc=(-.62, 1.25, 1.52), rot=(-R90, 0, 0), slats=6, depth=.08, thickness=.04)
    _grille_frame(a, -.62, 1.25, 1.5, .8, 1.0, t=.05)
    a.part('Tyres', 'Undercarriage').cyl(.3, .1, loc=(.1, .3, 1.54), seg=10, bevel=0)     # spare road wheel
    a.part('Wheels', 'Team').cyl(.22, .03, loc=(.1, .3, 1.6), seg=10, bevel=0)
    a.part('Hubs', 'Steel').cyl(.08, .03, loc=(.1, .3, 1.62), seg=6, bevel=0)
    wx, wy = -.45, 2.45 + B
    armor.box((1.14, .72, .1), loc=(wx, wy, 1.54), bevel=0)
    for s in (-1, 1):
        armor.box((.08, .56, .52), loc=(wx + s * .5, wy, 1.82), bevel=0)
    a.part('Winch_drum', 'Steel').cyl(.24, .9, loc=(wx, wy, 1.86), rot=ACROSS, seg=14, bevel=0)
    steel.cyl(.06, 1.1, loc=(wx, wy, 1.86), rot=ACROSS, seg=8, bevel=0)                  # axle
    for dx in (-.44, .44):
        a.part('Winch_flanges', 'Armor').cyl(.29, .04, loc=(wx + dx, wy, 1.86), rot=ACROSS, seg=14, bevel=0)
    steel.box((.5, .16, .14), loc=(wx, rear - .04, 1.46), bevel=0)                      # fairlead
    steel.cyl(.05, .44, loc=(wx, rear, 1.52), rot=ACROSS, seg=8, bevel=0)
    _cable(a, [(wx, wy + .15, 1.66), (wx, rear - .15, 1.56), (wx, rear + .02, 1.45), (wx, rear + .1, 1.28)], r=.028)
    # Fenders: tool boxes, tools and jerrycans; tow cables along the hull sides.
    _stowage_bin(a, (1.39, -2.2, 1.0), (.4, 1.0, .3), latch_side=1)
    _stowage_bin(a, (1.39, -.6, 1.0), (.4, 1.4, .3), latch_side=1)
    _jerrycans(a, (1.39, 1.3, 1.0), 3)
    _stowage_bin(a, (1.39, 2.4, 1.0), (.4, .9, .3), latch_side=1)
    _shovel(a, (-1.39, -2.1, 1.02), length=1.0)
    _pick(a, (-1.41, -.85, 1.028), length=.9)
    _stowage_bin(a, (-1.39, .55, 1.0), (.4, 1.2, .3), latch_side=-1)
    _stowage_bin(a, (-1.39, 2.15, 1.0), (.4, 1.3, .3), latch_side=-1)
    for s in (-1, 1):
        _cable(a, [(s * 1.175, -2.6, 1.42), (s * 1.175, -.6, 1.42), (s * 1.175, 1.6, 1.42), (s * 1.175, 2.85, 1.38)])
        _taillight(a, s * 1.0, rear, 1.24)
        steel.box((.16, .2, .14), loc=(s * .3, rear + .06, .74), bevel=0)                 # rear tow hooks
    # Rear plate: exhaust, towing pintle and the tow bar stowed flat on it.
    _exhaust(a, .45, rear, .98, .5, .22)
    steel.box((.2, .2, .16), loc=(0, rear + .08, .78), bevel=0)
    tow = a.part('Tow_bar', 'Hazard')
    for x in (-1.02, -.52):
        _rod(tow, (x, rear + .05, .7), (-.77, rear + .05, 1.14), .04, seg=6)
    steel.torus(.07, .02, loc=(-.77, rear + .05, 1.22), rot=(R90, 0, 0), seg=8, ring=4)
    steel.cyl(.22, .08, loc=(-.45, -1.3, roof(-1.3) + .02), seg=14, bevel=.015, bseg=1)  # RWS pedestal
    _rws_turret(a, (-.45, -1.3, roof(-1.3) + .05), length=.8)


# ----------------------------------------------------------------------------- electronic warfare truck
def _panel_array(a, x, y, z, parent=None, r=.24, size=(.34, .07, .72)):
    """Four radome panels round a mast top at (x, y, z) (their centre), turned 45 degrees."""
    fit = a.part('Mast_fittings', 'Armor', parent)
    for k in range(4):
        ang = math.pi / 4 + k * R90
        a.part('Radomes', 'Fuel', parent).box(size, loc=(x + math.cos(ang) * r, y + math.sin(ang) * r, z),
                                              rot=(0, 0, ang + R90), bevel=.02, seg=1)
        fit.box((.05, r - .05, .05), loc=(x + math.cos(ang) * (r + .05) / 2, y + math.sin(ang) * (r + .05) / 2,
                                          z + .2), rot=(0, 0, ang + R90), bevel=0)
    fit.cyl(.09, .1, loc=(x, y, z + size[2] / 2 + .04), seg=8, bevel=0)


def _lpda(a, x, y, z, parent=None, length=1.3, elements=7):
    """Log-periodic dipole antenna: a boom along Y with horizontal dipoles shrinking towards -Y."""
    steel = a.part('Array_elements', 'Steel', parent)
    a.part('Mast_fittings', 'Armor', parent).box((.07, length, .07), loc=(x, y, z), bevel=0)
    for i in range(elements):
        k = i / (elements - 1)
        w = .38 + (1.3 - .38) * k
        steel.box((w, .025, .025), loc=(x, y - length / 2 + .06 + k * (length - .12), z + .035), bevel=0)


def _telescopic_mast(a, x, y, z0, sections, parent=None):
    """Telescopic mast from a base box at z0: (radius, length) sections, each with a collar.
    Returns the height of the top."""
    steel = a.part('Mast', 'Steel', parent)
    fit = a.part('Mast_fittings', 'Armor', parent)
    fit.box((.34, .34, .26), loc=(x, y, z0 + .11), bevel=.03, seg=1)
    z = z0 + .2
    for r, length in sections:
        steel.cyl(r, length + .04, loc=(x, y, z + length / 2), seg=8, bevel=0)
        fit.cyl(r + .025, .07, loc=(x, y, z + length - .045), seg=8, bevel=0)
        z += length
    return z


def ew_jammer(a):
    """6x6 electronic-warfare jamming truck (Krasukha / Leer-3 lineage): a cab-over cab with a
    split windscreen, mirrors and a snorkel, a generator set behind it, and a tall shelter body with
    ribs, air-conditioning units, a side door, a rear door and ladder, roof handrails, two raised
    telescopic masts (a radome panel array and a log-periodic antenna), whips, a spinning dish on
    `Radar` and a roof remote weapon station on `Turret`; stabiliser jacks down at the rear."""
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    glass = a.part('Windows', 'Glass')
    for y in (-3.0, 1.55, 2.95):
        for s in (-1, 1):
            _wheel(a, s * 1.02, y, .56, .42)
        dark.box((1.66, .2, .16), loc=(0, y, .56), bevel=.02, seg=1)                        # axles
    for s in (-1, 1):
        dark.box((.2, 8.3, .3), loc=(s * .5, 0, .86), bevel=.03, seg=1)                     # frame rails
    # Cab over the front axle.
    front, top = (-4.46, 1.95), (-4.36, 2.86)
    body.prism([(-4.42, 1.2), front, top, (-4.2, 3.0), (-2.56, 3.0), (-2.56, 1.2)], 2.46, bevel=.07)
    wy, wz, wrot = _glacis(front, top, .52, .012)
    for s in (-1, 1):
        glass.box((1.0, .62, .04), loc=(s * .54, wy, wz), rot=(wrot, 0, 0), bevel=.01, seg=1)
        glass.box((.04, .78, .5), loc=(s * 1.235, -3.55, 2.42), bevel=.01, seg=1)          # door windows
        for y in (-4.12, -2.95):
            armor.box((.03, .03, 1.5), loc=(s * 1.23, y, 2.02), bevel=0)                    # door shut lines
        steel.box((.04, .16, .05), loc=(s * 1.245, -3.15, 2.1), bevel=0)                     # door handles
        steel.box((.32, .34, .04), loc=(s * 1.1, -3.82, .78), bevel=0)                       # steps
        steel.box((.32, .34, .04), loc=(s * 1.1, -3.82, .46), bevel=0)
        steel.box((.04, .36, .4), loc=(s * 1.25, -3.82, .8), bevel=0)
        steel.tube([(s * 1.2, -4.28, 2.45), (s * 1.42, -4.34, 2.5)], .018, seg=4)           # mirror arms
        armor.box((.06, .16, .3), loc=(s * 1.45, -4.36, 2.42), bevel=.01, seg=1)            # mirrors
        a.part('Lamps', 'Lamp').box((.26, .04, .14), loc=(s * .88, -4.62, 1.02), bevel=0)   # headlights
        armor.box((.5, 1.25, .06), loc=(s * 1.02, -3.0, 1.18), bevel=.02, seg=1)            # front fenders
        a.part('Mud_flaps', 'Rubber').box((.44, .04, .42), loc=(s * 1.02, -2.32, .92), bevel=0)
    dark.grille(1.5, .44, loc=(0, -4.44, 1.58), rot=(-.05, 0, 0), slats=4, depth=.06, thickness=.04)
    steel.box((2.5, .24, .3), loc=(0, -4.5, 1.02), bevel=.04)                               # bumper
    for x in (-.5, 0, .5):
        a.part('Roof_lights', 'Alloy').box((.12, .06, .05), loc=(x, -4.19, 3.01), bevel=0)
    armor.cyl(.24, .06, loc=(-.45, -3.4, 3.0), seg=12, bevel=.02, bseg=1)                  # cab hatch
    steel.cyl(.1, 1.3, loc=(1.12, -2.45, 2.35), seg=10, bevel=0)                          # air intake snorkel
    steel.cyl(.14, .22, loc=(1.12, -2.45, 3.1), seg=10, bevel=.02, bseg=1)
    _antenna(a, None, -1.05, -2.75, 3.0, 1.6)
    # Generator set behind the cab: louvred sides, a fan grille on top and an exhaust stack.
    gen = a.part('Generator', 'Armor')
    gen.box((2.3, .86, 1.3), loc=(0, -1.98, 1.85), bevel=.05)
    for s in (-1, 1):
        dark.grille(.62, .7, loc=(s * 1.16, -1.98, 1.9), rot=(0, 0, s * R90), slats=5, depth=.05, thickness=.04)
    dark.grille(.7, .5, loc=(-.4, -1.98, 2.51), rot=(-R90, 0, 0), slats=4, depth=.05, thickness=.035)
    steel.cyl(.07, .7, loc=(.6, -1.98, 2.8), seg=8, bevel=0)                               # exhaust stack
    steel.cyl(.1, .1, loc=(.6, -1.98, 3.15), seg=8, bevel=0)
    a.part('Labels', 'Hazard').box((.3, .02, .2), loc=(.62, -2.42, 2.1), bevel=0)
    # Under the body: fuel tank, battery box and air tanks between the axles.
    steel.cyl(.26, 1.2, loc=(.82, -.6, .92), rot=FORWARD, seg=12, bevel=.03, bseg=1)
    armor.box((.5, .8, .45), loc=(-.85, -.6, .95), bevel=.03, seg=1)
    steel.cyl(.14, .9, loc=(-.8, .55, .9), rot=FORWARD, seg=10, bevel=0)
    # Shelter body: ribs, a gutter, a bottom rail, air conditioners, a side door and a rear door.
    L0, L1, zb, zt, hw = -1.4, 4.45, 1.28, 3.5, 1.4
    body.box((2 * hw, L1 - L0, zt - zb), loc=(0, (L0 + L1) / 2, (zb + zt) / 2), bevel=.05)
    dark.box((2 * hw + .04, L1 - L0 + .04, .12), loc=(0, (L0 + L1) / 2, zb + .05), bevel=0)   # bottom rail
    for s in (-1, 1):
        armor.box((.05, L1 - L0 - .1, .06), loc=(s * (hw + .01), (L0 + L1) / 2, zt - .1), bevel=0)  # gutter
        for y in (-.35, 1.0, 2.25, 3.5):
            if s > 0 and y < 0:
                continue
            armor.box((.04, .08, zt - zb - .3), loc=(s * (hw + .01), y, (zb + zt) / 2), bevel=0)     # ribs
        a.part('Mud_flaps', 'Rubber').box((.44, .04, .42), loc=(s * 1.02, 3.56, .9), bevel=0)
        armor.box((.5, 2.4, .06), loc=(s * 1.02, 2.25, 1.2), bevel=.02, seg=1)             # rear mudguards
    for y in (.4, 2.9):                                                                      # air conditioners
        armor.box((.28, .9, .62), loc=(-hw - .12, y, 2.85), bevel=.03, seg=1)
        dark.grille(.7, .44, loc=(-hw - .265, y, 2.87), rot=(0, 0, -R90), slats=4, depth=.04, thickness=.03)
    armor.box((.05, .82, 1.7), loc=(hw + .015, -.7, 2.2), bevel=.012, seg=1)               # side door
    steel.box((.04, .06, .22), loc=(hw + .05, -.4, 2.2), bevel=0)
    steel.box((.36, .5, .04), loc=(hw + .12, -.7, 1.1), bevel=0)                            # door step
    for dy in (-.22, .22):
        steel.box((.3, .04, .22), loc=(hw + .11, -.7 + dy, 1.2), bevel=0)
    armor.box((.3, .5, .22), loc=(hw + .12, 1.75, 2.95), bevel=.02, seg=1)                 # cable entry box
    for dz in (-.05, .05):
        steel.cyl(.035, .06, loc=(hw + .27, 1.75, 2.95 + dz), rot=ACROSS, seg=6, bevel=0)
    armor.box((1.0, .05, 1.8), loc=(.55, L1 + .015, 2.25), bevel=.012, seg=1)                # rear door
    steel.box((.06, .04, .24), loc=(.18, L1 + .05, 2.2), bevel=0)
    ladder = a.part('Ladder', 'Steel')
    for x in (-.95, -.55):
        ladder.box((.05, .05, 2.4), loc=(x, L1 + .08, 2.3), bevel=0)
    for i in range(6):
        ladder.box((.4, .03, .035), loc=(-.75, L1 + .08, 1.35 + i * .38), bevel=0)
    for x in (-.95, -.55):
        ladder.box((.03, .1, .05), loc=(x, L1 + .03, 3.2), bevel=0)
    steel.box((2.5, .16, .18), loc=(0, 4.42, .9), bevel=.03, seg=1)                         # rear bumper
    for s in (-1, 1):
        a.part('Tail_lights', 'Alloy').box((.16, .05, .1), loc=(s * 1.0, 4.52, .92), bevel=0)
        armor.box((.26, .26, .5), loc=(s * 1.18, 4.15, 1.02), bevel=.03, seg=1)             # stabiliser jacks
        steel.cyl(.07, .78, loc=(s * 1.18, 4.15, .45), seg=10, bevel=0)
        steel.cyl(.2, .07, loc=(s * 1.18, 4.15, .04), seg=12, bevel=.02, bseg=1)
    # Roof: handrails, whips, masts with their arrays, the dish on its pedestal and the RWS.
    for s in (-1, 1):
        _rail(a, [(s * 1.3, -.1, zt - .02), (s * 1.3, -.1, zt + .12), (s * 1.3, 3.3, zt + .12),
                  (s * 1.3, 3.3, zt - .02)])
        _whip(a, s * 1.25, 2.6, zt, 1.7)
        _whip(a, s * 1.25, .45, zt, 1.2)
        armor.box((.05, .3, .34), loc=(s * 1.2, -1.2, zt + .15), bevel=.015, seg=1)          # blade antennas
        armor.box((.1, .12, .06), loc=(s * 1.2, -1.2, zt), bevel=0)
    for y in (.3, 2.5):                                                                      # roof seams
        armor.box((2.7, .05, .03), loc=(0, y, zt), bevel=0)
    dark.box((.14, 3.2, .05), loc=(-.45, 2.05, zt + .01), bevel=0)                         # cable tray
    for x, y in ((-.45, 3.55), (.45, 3.55), (.55, 2.2)):                                     # junction boxes
        armor.box((.3, .24, .2), loc=(x, y, zt + .08), bevel=.02, seg=1)
    for x in (-.9, .9):
        top = _telescopic_mast(a, x, 3.95, zt, ((.1, .8), (.08, .7), (.06, .55)))
        if x < 0:
            _panel_array(a, x, 3.95, top - .25)
        else:
            _lpda(a, x, 3.95, top + .03)
    steel.cyl(.15, .3, loc=(0, 1.45, zt + .14), seg=12, bevel=.02, bseg=1)                  # dish pedestal
    r = a.pivot('Radar', (0, 1.45, zt + .29))
    rm = a.part('Radar_mast', 'Steel', r)
    rm.cyl(.08, .3, loc=(0, 0, .15), seg=8, bevel=0)
    rm.box((.12, .22, .16), loc=(0, .04, .38), bevel=.02, seg=1)                            # yoke
    rm.limb((0, -.1, .42), (0, -.5, .44), .03, .03, bevel=0)                                 # feed horn
    a.part('Radar_feed', 'Armor', r).box((.09, .09, .09), loc=(0, -.52, .44), bevel=0)
    _dish(a.part('Radar_dish', 'Armor', r), (0, -.06, .42), .56, .56, depth=.15, seg=12, tilt=.3)
    steel.cyl(.22, .08, loc=(0, -.75, zt + .03), seg=14, bevel=.015, bseg=1)                # RWS pedestal
    _rws_turret(a, (0, -.75, zt + .06), length=.85)


# ----------------------------------------------------------------------------- FPV drones and their carrier
def _quadcopter(a, m, k=1.0, parent=None, full=True):
    """FPV kamikaze quadcopter in frame m (local Z up, local -Y forward), k times the 0.69 m
    reference size (prop tip to prop tip across the diagonal): an X frame of carbon arms, a stack
    and a Team-painted battery, four motors with red two-blade props and an RPG-style shaped
    charge slung under the body, nose forward. full adds the camera, antennas, a TeamGlow LED
    and the charge's warning band (the projectile); the launcher rack's drones skip them."""
    turn = m.to_3x3()

    def at(x, y, z):
        return m @ Vector((x * k, y * k, z * k))

    def spin(ang):
        return (turn @ Matrix.Rotation(ang, 3, 'Z')).to_euler('XYZ')
    frame = a.part('Drone_frame', 'Undercarriage', parent)
    for i in range(4):
        ang = math.pi / 4 + i * R90
        frame.box((.2 * k, .035 * k, .018 * k), loc=at(math.cos(ang) * .13, math.sin(ang) * .13, .009),
                  rot=spin(ang), bevel=0)
    frame.box((.09 * k, .17 * k, .04 * k), loc=at(0, 0, .036), rot=spin(0), bevel=0)
    a.part('Drone_battery', 'Team', parent).box((.064 * k, .13 * k, .036 * k), loc=at(0, .012, .072), rot=spin(0),
                                                bevel=0)
    motors = a.part('Drone_motors', 'Steel', parent)
    props = a.part('Drone_props', 'BarrelRed', parent)
    for i, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        mx, my = sx * .16, sy * .16
        motors.cyl(.026 * k, .048 * k, loc=at(mx, my, .04), rot=spin(0), seg=6, bevel=0)
        props.box((.26 * k, .028 * k, .006 * k), loc=at(mx, my, .0495), rot=spin(.35 + i * 1.1), bevel=0)
    charge = a.part('Drone_charge', 'Armor', parent)
    rot = (turn @ Matrix.Rotation(R90, 3, 'X')).to_euler('XYZ')           # lathe axis -> local -Y (the nose)
    charge.lathe([(r * k, z * k) for r, z in ((.028, -.13), (.045, -.1), (.045, .07), (.036, .13), (.016, .19),
                                                (.004, .205))], loc=at(0, -.02, -.038), rot=rot, seg=8 if full else 6)
    if full:
        a.part('Drone_band', 'Hazard', parent).cyl(.058 * k, .03 * k, loc=at(0, -.075, -.038), rot=rot, seg=8,
                                                   bevel=0)
        frame.box((.038 * k, .034 * k, .03 * k), loc=at(0, -.105, .03), rot=spin(0), bevel=0)     # camera
        a.part('Drone_lens', 'Glass', parent).box((.022 * k, .01 * k, .02 * k), loc=at(0, -.127, .03), rot=spin(0),
                                                   bevel=0)
        for sx in (-1, 1):
            loc, r, length = _along(at(sx * .03, .08, .06), at(sx * .055, .17, .13))
            motors.cyl(.005 * k, length, loc=loc, rot=r, seg=4, bevel=0)                          # antennas
        a.part('Drone_led', 'TeamGlow', parent).box((.03 * k, .012 * k, .014 * k), loc=at(0, .09, .036),
                                                    rot=spin(0), bevel=0)
        for y in (-.035, .035):                                                                    # straps
            a.part('Drone_straps', 'Rubber', parent).box((.11 * k, .016 * k, .155 * k), loc=at(0, y, -.0125),
                                                         rot=spin(0), bevel=0)


def fpv_drone(a):
    """FPV kamikaze drone projectile (flies along -Y, origin at its centre): see _quadcopter."""
    _quadcopter(a, _frame((0, .0, .0), (0, 0, 0)), k=1.0)


def fpv_carrier(a):
    """Armoured 6x6 MRAP truck (Typhoon-K / RG-33 lineage) launching FPV kamikaze drones: a V-hull
    under an angular crew capsule with framed armoured windscreens, small side windows, doors,
    steps and big mirrors; a narrow bonnet with a grille guard, a winch and fenders over the front
    wheels; drone-link panel antennas and a remote weapon station on `Mount_mg` on the roof. The
    rear bed carries the launcher on `Turret`: a tilted rack of nine drone cells facing up and
    back, six of them still holding a quadcopter, on a turntable with lift rams."""
    body = a.part('Body', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    glass = a.part('Windows', 'Glass')
    for y in (-2.55, 1.35, 2.75):
        for s in (-1, 1):
            _wheel(a, s * 1.05, y, .6, .46)
        dark.box((1.66, .22, .16), loc=(0, y, .6), bevel=.02, seg=1)                         # axles

    def vee(y, w, zk, zt=1.34):
        return [(-w, y, zt), (-w * .38, y, zk), (w * .38, y, zk), (w, y, zt)]
    body.loft([vee(-3.0, .6, 1.0), vee(-2.35, .8, .74), vee(3.3, .8, .74), vee(3.72, .66, 1.0)], bevel=.03)
    # Crew capsule: vertical lower flanks, sloped upper flanks, a flat roof.
    low, high = (1.22, 1.28), (1.3, 2.3)
    body.prism([(-1.22, 1.28), (1.22, 1.28), (1.3, 2.3), (1.08, 2.95), (-1.08, 2.95), (-1.3, 2.3)], 3.2,
               loc=(0, -1.0, 0), axis='Y', bevel=.06)
    # Bonnet, grille, grille guard, winch, bumper, headlights and fenders over the front wheels.
    f = .15                                                   # bonnet shortened by f
    body.prism([(-3.98 + f, .98), (-4.04 + f, 1.55), (-3.86 + f, 1.74), (-2.55, 1.92), (-2.55, .98)], 1.6, bevel=.06)
    dark.grille(1.1, .36, loc=(0, -4.035 + f, 1.28), rot=(.1, 0, 0), slats=4, depth=.05, thickness=.04)
    dark.grille(.8, .5, loc=(0, -3.18, 1.842), rot=(-R90 + .154, 0, 0), slats=5, depth=.05, thickness=.035)
    steel.box((2.3, .26, .3), loc=(0, -4.14 + f, .94), bevel=.04)
    steel.cyl(.1, .56, loc=(0, -4.33 + f, .94), rot=ACROSS, seg=10, bevel=0)                 # winch drum
    for x in (-.34, .34):
        armor.box((.08, .2, .26), loc=(x, -4.3 + f, .94), bevel=0)
    _rail(a, [(-.72, -4.1 + f, 1.1), (-.72, -4.24 + f, 1.22), (-.72, -4.24 + f, 1.66), (.72, -4.24 + f, 1.66),
              (.72, -4.24 + f, 1.22), (.72, -4.1 + f, 1.1)], r=.035)
    for x in (-.3, .3):
        _rail(a, [(x, -4.24 + f, 1.2), (x, -4.24 + f, 1.66)], r=.025)
    for s in (-1, 1):
        _headlight(a, s * .58, -3.96 + f, 1.62, guard=False)
        steel.box((.14, .2, .14), loc=(s * .95, -4.2 + f, .82), bevel=.02, seg=1)            # tow hooks
        armor.box((.58, 1.34, .07), loc=(s * 1.05, -2.62, 1.3), bevel=.02, seg=1)            # front fenders
        armor.box((.56, .07, .32), loc=(s * 1.05, -3.27, 1.16), rot=(-.35, 0, 0), bevel=.015, seg=1)
        a.part('Mud_flaps', 'Rubber').box((.46, .04, .4), loc=(s * 1.05, -1.88, .95), bevel=0)
    # Windscreens in thick frames, a visor, marker lights; big mirrors on arms.
    frame = a.part('Window_frames', 'Armor')
    for s in (-1, 1):
        x = s * .55
        glass.box((.8, .06, .6), loc=(x, -2.61, 2.37), bevel=0)
        for z in (2.03, 2.71):
            frame.box((.96, .12, .08), loc=(x, -2.62, z), bevel=0)
        for dx in (-.44, .44):
            frame.box((.08, .12, .6), loc=(x + dx, -2.62, 2.37), bevel=0)
        steel.tube([(s * 1.2, -2.5, 2.5), (s * 1.48, -2.62, 2.55)], .02, seg=4)
        armor.box((.07, .18, .34), loc=(s * 1.51, -2.64, 2.46), bevel=.01, seg=1)
    armor.box((2.2, .3, .04), loc=(0, -2.72, 2.87), rot=(.12, 0, 0), bevel=.01, seg=1)       # visor
    for x in (-.6, 0, .6):
        a.part('Roof_lights', 'Alloy').box((.12, .06, .05), loc=(x, -2.52, 2.96), bevel=0)
    # Flanks: framed side windows, door shut lines and handles, a step, a fuel tank and a locker.
    for s in (-1, 1):
        for y in (-1.95, -.65):
            xw, zw, lean = _flank(low, high, .7, .03)
            frame.box((.06, .62, .42), loc=(s * (xw - .02), y, zw), rot=(0, -s * lean, 0), bevel=0)
            xg, zg, _ = _flank(low, high, .7, .055)
            glass.box((.03, .5, .3), loc=(s * xg, y, zg), rot=(0, -s * lean, 0), bevel=0)
        for y in (-2.5, -1.35, -.05):
            xs, zs, lean = _flank(low, high, .46, .005)
            armor.box((.03, .04, 1.0), loc=(s * xs, y, zs), rot=(0, -s * lean, 0), bevel=0)
        xh, zh, lean = _flank(low, high, .38, .02)
        for y in (-1.5, -.2):
            steel.box((.04, .18, .05), loc=(s * xh, y, zh), rot=(0, -s * lean, 0), bevel=0)
        for z in (.66, .98):
            steel.box((.34, .34, .04), loc=(s * 1.2, -1.55, z), bevel=0)
        steel.box((.04, .36, .42), loc=(s * 1.36, -1.55, .92), bevel=0)
        xa, za, lean = _flank(low, high, .2, .025)                                          # add-on armour
        for y, w in ((-1.98, .95), (-.7, 1.2), (.2, .5)):
            armor.box((.05, w, .34), loc=(s * xa, y, za), rot=(0, -s * lean, 0), bevel=.012, seg=1)
            xb, zb, _ = _flank(low, high, .2, .055)
            steel.bolts([(s * xb, y + d * (w / 2 - .08), zb + e) for d in (-1, 1) for e in (-.1, .1)], r=.022,
                        h=.02, rot=(0, s * R90, 0), bevel=0)
        up0, up1 = (1.3, 2.3), (1.08, 2.95)
        xu, zu, lean = _flank(up0, up1, .45, .025)
        for y in (-1.95, -.65):
            armor.box((.05, 1.1, .4), loc=(s * xu, y, zu), rot=(0, -s * lean, 0), bevel=.012, seg=1)
    steel.cyl(.26, 1.0, loc=(-1.0, -.5, .98), rot=FORWARD, seg=12, bevel=.03, bseg=1)       # fuel tank
    armor.box((.34, .9, .5), loc=(1.12, -.5, 1.02), bevel=.03, seg=1)                       # locker
    steel.box((.03, .06, .08), loc=(1.3, -.5, 1.12), bevel=0)
    # Roof: hatch, rails, drone-link panel antennas, a GPS puck, whips and the RWS.
    _hatch(a, -.45, -.55, 2.95, .28)
    for s in (-1, 1):
        _rail(a, [(s * .98, -1.9, 2.93), (s * .98, -1.9, 3.03), (s * .98, .3, 3.03), (s * .98, .3, 2.93)])
        steel.cyl(.03, .5, loc=(s * .75, .35, 3.18), seg=6, bevel=0)                          # link masts
        a.part('Link_panels', 'Fuel').box((.26, .05, .34), loc=(s * .75, .41, 3.48), rot=(-.35, 0, s * .5),
                                          bevel=.015, seg=1)
    a.part('Link_panels', 'Fuel').sphere((.09, .09, .05), loc=(.25, .2, 2.95), seg=10, rings=5, cut=0)
    _antenna(a, None, -.95, .45, 2.95, 1.2)
    _whip(a, .95, -.05, 2.95, 1.0)
    _rws(a, None, (.35, -1.45, 2.95), length=.85)
    # Capsule rear wall: a door out onto the bed.
    armor.box((.8, .05, 1.2), loc=(-.35, .615, 2.0), bevel=.012, seg=1)
    steel.box((.05, .04, .2), loc=(-.05, .65, 2.0), bevel=0)
    # Rear bed: deck, low side walls and tailgate, lights, bumper, mud flaps, corner stowage.
    r = -.2                                                   # rear bed shortened by -r
    armor.box((2.62, 3.36 + r, .1), loc=(0, 2.27 + r / 2, 1.38), bevel=.02, seg=1)
    for s in (-1, 1):
        body.box((.08, 3.3 + r, .24), loc=(s * 1.27, 2.29 + r / 2, 1.53), bevel=.015, seg=1)
        a.part('Mud_flaps', 'Rubber').box((.46, .04, .4), loc=(s * 1.05, 3.45, .95), bevel=0)
        a.part('Tail_lights', 'Alloy').box((.16, .05, .1), loc=(s * 1.02, 3.99 + r, 1.2), bevel=0)
        steel.box((.14, .2, .14), loc=(s * .6, 3.95 + r, .98), bevel=.02, seg=1)             # rear tow hooks
        for x in (.26, .64):                                                                 # on the tailgate
            _jerrycans(a, (s * x, 4.055 + r, 1.2), 1, axis='y', bracket=False)
        armor.box((.42, .36, .34), loc=(s * .98, .95, 1.6), bevel=.02, seg=1)               # charger boxes
        a.part('Labels', 'Hazard').box((.2, .02, .12), loc=(s * .98, .76, 1.63), bevel=0)
    body.box((2.5, .08, .24), loc=(0, 3.93 + r, 1.53), bevel=.015, seg=1)                   # tailgate
    steel.box((2.3, .16, .16), loc=(0, 3.96 + r, 1.12), bevel=.03, seg=1)                   # rear bumper
    steel.box((1.6, .03, .05), loc=(0, 4.14 + r, 1.45), bevel=0)                           # jerrycan strap

    # Launcher on the Turret: turntable, base, hinge brackets and lift rams under a rack of 3 x 3
    # drone cells tilted 22 degrees back; its open face looks up and back.
    t = a.pivot('Turret', (0, 2.35, 1.43))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(.9, .1, loc=(0, 0, .04), seg=20, bevel=.02, bseg=1)                           # turntable
    tarm.box((1.4, 1.1, .28), loc=(0, -.1, .19), bevel=.03, seg=1)                          # base
    p, depth = .62, .16
    tilt = math.radians(22)
    rot = (-tilt, 0, 0)
    rack = _frame((0, .2, 1.0), rot)
    normal = rack.to_3x3() @ Vector((0, 0, 1))
    half = 1.5 * p
    walls = a.part('Rack', 'Team', t)
    for s in (-1, 1):
        walls.box((.05, 2 * half + .1, depth + .06), loc=rack @ Vector((s * (half + .025), 0, -(depth + .06) / 2)),
                  rot=rot, bevel=.012, seg=1)
        walls.box((2 * half, .05, depth + .06), loc=rack @ Vector((0, s * (half + .025), -(depth + .06) / 2)),
                  rot=rot, bevel=.012, seg=1)
    a.part('Rack_floor', 'Armor', t).box((2 * half + .02, 2 * half + .02, .06), loc=rack @ Vector((0, 0, -depth - .03)),
                                         rot=rot, bevel=0)
    grid = a.part('Rack_grid', 'Undercarriage', t)
    for c in (-p / 2, p / 2):
        grid.box((.03, 2 * half, depth + .02), loc=rack @ Vector((c, 0, -depth / 2 - .01)), rot=rot, bevel=0)
        grid.box((2 * half, .03, depth + .01), loc=rack @ Vector((0, c, -depth / 2 - .015)), rot=rot, bevel=0)
    band = a.part('Rack_bands', 'Armor', t)
    for c in (-half + .25, half - .25):                                                      # outer bands
        for s in (-1, 1):
            band.box((.04, .1, depth + .02), loc=rack @ Vector((s * (half + .065), c, -depth / 2 - .02)), rot=rot,
                     bevel=0)
    for s in (-1, 1):                                                                        # lifting lugs
        for c in (-half, half):
            tsteel.box((.08, .08, .08), loc=rack @ Vector((s * (half - .1), c + (.06 if c > 0 else -.06), .0)),
                       rot=rot, bevel=0)
    for s in (-1, 1):
        tarm.box((.12, .3, .5), loc=(s * .75, .72, .3), bevel=.015, seg=1)                   # hinge brackets
        _ram(a, (s * .45, -.5, .3), tuple(rack @ Vector((s * .45, -.55, -depth - .04))), .06, parent=t)
        tarm.limb((s * .75, .72, .3), tuple(rack @ Vector((s * .75, .75, -depth - .04))), .1, .16, bevel=.01,
                  seg=1)                                                                     # hinge arms
    empty = {(1, 1), (-1, 0), (0, -1)}
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            if (i, j) in empty:
                continue
            cell = rack @ _frame((i * p, j * p, -depth + .055), (0, 0, 0))
            _quadcopter(a, cell, k=.8, parent=t, full=False)
    a.pivot('Muzzle_main', tuple(rack.to_translation() + normal * .08), t)


# ----------------------------------------------------------------------------- mines and the mine layer
def _mine_disc(a, m, parent=None, r=.15, h=.08, seg=8, plate=True):
    """Anti-tank mine (TM-62 style) in frame m, its axis along local Z from the bottom face at the
    origin: an olive disc with a steel pressure plate on top."""
    rot = m.to_euler('XYZ')
    a.part('Mines', 'Crate', parent).cyl(r, h, loc=m @ Vector((0, 0, h / 2)), rot=rot, seg=seg, bevel=0)
    if plate:
        a.part('Mine_fuzes', 'Steel', parent).cyl(r * .5, .025, loc=m @ Vector((0, 0, h + .005)), rot=rot, seg=6,
                                                  bevel=0)


def mine_layer(a):
    """Tracked mine layer (GMZ-3 / MT-LB lineage): a front cab with a small machine-gun `Turret`,
    two open mine hoppers with their lids thrown open, racks of mines on the fenders, a conveyor to
    the rear, and the dispensing chute running down into a ploughshare lowered to the ground, with
    a hazard-striped plough beam, furrow-closing discs and ploughed earth."""
    tracks(a, 1.16, 5.9, .8, .27, 7, .44, belt_width=.52, wheel_seg=10, lean=True, sprocket=-1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    nose, brow = (-3.25, .95), (-2.66, 1.35)
    hull.prism([(-2.95, .52), nose, brow, (3.0, 1.35), (3.0, .52)], 2.3, bevel=.06)
    cab_front = ((-2.68, 1.3), (-2.38, 2.05))
    a.part('Cab', 'Team').prism([cab_front[0], cab_front[1], (-1.15, 2.05), (-1.15, 1.3)], 2.3, bevel=.05)
    # Nose: spare track links, tow hooks, guarded headlights, vision blocks in the cab front.
    gy, gz, grot = _glacis(nose, brow, .5, 0)
    _track_links(a, _frame((-.55, gy, gz), (grot, 0, 0)), 3, width=.44)
    _track_links(a, _frame((.55, gy, gz), (grot, 0, 0)), 3, width=.44)
    for s in (-1, 1):
        steel.box((.16, .2, .14), loc=(s * .6, -3.2, .72), bevel=.02, seg=1)
        _headlight(a, s * .88, -2.64, 1.5, guard=True)
        gy, gz, grot = _glacis(*cab_front, .78, .012)
        for dx in (-.14, 0, .14):
            a.part('Vision_blocks', 'Glass').box((.11, .07, .05), loc=(s * .45 + dx, gy, gz), rot=(grot, 0, 0),
                                                 bevel=0)
    for s in (-1, 1):                                                                        # cab side doors
        armor.box((.04, .6, .52), loc=(s * 1.165, -1.62, 1.7), bevel=.01, seg=1)
        steel.box((.03, .14, .04), loc=(s * 1.195, -1.45, 1.7), bevel=0)
        a.part('Vision_blocks', 'Glass').box((.04, .16, .07), loc=(s * 1.17, -2.15, 1.88), bevel=0)
    _hatch(a, .45, -1.72, 2.05, .26)
    _periscopes(a, [(.45, -2.2, 2.05, 0), (1.05, -1.7, 2.05, R90)])
    _antenna(a, None, .95, -1.3, 2.05, 1.3)
    steel.box((.09, .09, .06), loc=(.95, -1.3, 2.06), bevel=0)
    # Mine hoppers: two open bins, their lids thrown open outwards, a top layer of mines in each.
    hy, hl, hz0, hz1 = .45, 2.6, 1.34, 2.1
    for s in (-1, 1):
        cx = s * .53
        hull.shell(chamfered(.96, hl, .06), hz1 - hz0, .05, loc=(cx, hy, hz0), floor=.05, bevel=.015)
        deck.box((.86, hl - .1, .03), loc=(cx, hy, 1.86), bevel=0)                          # fill level
        for i in range(4):
            for j in (-1, 1):
                _mine_disc(a, _frame((cx + j * .22, hy - .93 + i * .62 + j * .05, 1.87), (0, 0, 0)))
        lean = math.radians(70)
        lid = _frame((s * 1.01, hy, hz1), (0, -s * lean, 0))
        a.part('Hopper_lids', 'Team').box((.96, hl - .02, .05), loc=lid @ Vector((s * .48, 0, .03)),
                                          rot=(0, -s * lean, 0), bevel=.015, seg=1)
        for y in (-.9, 0, .9):
            steel.box((.06, .14, .08), loc=(s * 1.02, hy + y, hz1 - .02), bevel=0)             # lid hinges
            armor.box((.5, .05, .05), loc=lid @ Vector((s * .5, y, .07)), rot=(0, -s * lean, 0), bevel=0)
    # Fender racks of mines standing on edge, and stowage bins.
    for s in (-1, 1):
        rack = a.part('Mine_racks', 'Steel')
        for z in (.97, 1.2):
            rack.box((.03, 2.5, .04), loc=(s * 1.44, .45, z), bevel=0)
        for y in (-.8, 1.7):
            rack.box((.28, .04, .36), loc=(s * 1.29, y, 1.1), bevel=0)
        for i in range(6):
            _mine_disc(a, _frame((s * 1.25, -.55 + i * .4, 1.07), (0, s * R90, 0)), h=.1)
        _stowage_bin(a, (s * 1.32, -2.0, .91), (.3, 1.0, .3), latch_side=s)
        _stowage_bin(a, (s * 1.32, 2.4, .91), (.3, .9, .3), latch_side=s)
        _cable(a, [(s * 1.175, -1.1, 1.24), (s * 1.175, 1.6, 1.24), (s * 1.175, 2.9, 1.2)])
        _taillight(a, s * .95, 3.0, 1.2)
        steel.box((.16, .2, .14), loc=(s * .85, 3.06, .66), bevel=.02, seg=1)                 # rear tow hooks
        deck.grille(.5, .8, loc=(s * .75, 2.4, 1.365), rot=(-R90, 0, 0), slats=5, depth=.06, thickness=.035)
        _grille_frame(a, s * .75, 2.4, 1.35, .5, .8, t=.04)
    # Conveyor from under the hoppers to the rear, then the chute down into the plough.
    armor.box((.62, 1.2, .5), loc=(0, 2.4, 1.58), bevel=.03, seg=1)
    armor.box((.7, .2, .6), loc=(0, 1.86, 1.6), bevel=.02, seg=1)
    top, low = Vector((0, 2.95, 1.62)), Vector((0, 3.8, .42))
    chute = _plane((top + low) / 2, (1, 0, 0), low - top)
    length = (low - top).length
    crot = chute.to_euler('XYZ')
    trough = a.part('Chute', 'Armor')
    trough.box((.5, length, .04), loc=chute @ Vector((0, 0, -.02)), rot=crot, bevel=0)
    for s in (-1, 1):
        trough.box((.04, length, .18), loc=chute @ Vector((s * .27, 0, .07)), rot=crot, bevel=0)
    for u in (-.45, .05, .5):
        _mine_disc(a, chute @ _frame((0, u * length / 1.2, 0), (0, 0, 0)))
    for s in (-1, 1):                                                                        # chute stays
        _rod(steel, (s * .3, 3.0, 1.2), tuple(chute @ Vector((s * .27, .1, -.02))), .025, seg=6)
    # Plough: arms from the rear plate, lift rams, a striped beam, the share, discs and earth.
    beam = Vector((0, 3.62, .56))
    armor.box((1.2, .16, .18), loc=beam, bevel=.02, seg=1)
    _stripes(a, _plane(beam + Vector((0, .08, 0)), (-1, 0, 0), (0, 0, 1)), 1.14, .14, pitch=.2)
    for s in (-1, 1):
        armor.limb((s * .55, 3.0, .72), (s * .5, 3.62, .56), .1, .12, bevel=.01, seg=1)
        _ram(a, (s * .32, 3.02, 1.18), (s * .32, 3.58, .62), .05)
    share = a.part('Share', 'Steel')
    share.prism([(3.5, .5), (3.44, .15), (3.56, -.04), (3.86, -.04), (3.8, .5)], .12, bevel=0)
    for s in (-1, 1):
        share.box((.3, .34, .03), loc=(s * .2, 3.74, .04 + (s + 1) * .008), rot=(0, 0, s * .5), bevel=0)
        share.cyl(.2, .04, loc=(s * .32, 4.0, .18), rot=(0, R90 + s * .35, s * .35), seg=10, bevel=0)
        steel.limb((s * .5, 3.64, .5), (s * .32, 3.98, .24), .05, .05, bevel=0)
    dirt = a.part('Earth', 'Dirt', flat=True)
    for x, y, r, h, seed in ((-.24, 3.62, .26, .1, 1.0), (.26, 3.66, .24, .09, 2.0), (0, 4.12, .3, .07, 3.0),
                             (-.42, 4.0, .18, .06, 4.0), (.44, 4.02, .2, .06, 5.0)):
        dirt.ico((r, r * 1.2, h), loc=(x, y, 0), sub=1, jitter=.25, seed=seed)
    _exhaust(a, -.55, 3.0, .95, .36, .16)

    # Small machine-gun turret on the cab roof.
    t = a.pivot('Turret', (-.5, -1.95, 2.04))
    a.part('Turret_body', 'Team', t).cyl(.4, .36, r2=.3, loc=(0, 0, .18), seg=12, bevel=.03, bseg=1)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.cyl(.2, .06, loc=(.06, .08, .38), seg=10, bevel=.015, bseg=1)                      # hatch
    tarm.box((.2, .16, .2), loc=(0, -.34, .19), bevel=.02, seg=1)                           # mantlet
    gun = a.part('MG_gun', 'Steel', t)
    gun.box((.1, .3, .1), loc=(0, -.38, .19), bevel=0)
    gun.cyl(.022, .62, loc=(0, -.8, .19), rot=FORWARD, seg=8, bevel=0)
    gun.cyl(.034, .08, loc=(0, -1.08, .19), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_main', (0, -1.12, .19), t)
    _periscopes(a, [(.18, -.18, .35, 0), (-.2, -.1, .34, -.6)], parent=t, size=(.1, .06, .07))


def mine(a):
    """Anti-tank mine prop: a 0.5 m disc half-buried in a scuffed ring of earth, its pressure plate
    and fuze standing proud and a small TeamGlow light on top showing the owner."""
    seg = 12
    verts, faces = [], []
    rings = ((.2, .058), (.3, .07), (.42, .03), (.54, -.01))
    for r, z in rings:
        for i in range(seg):
            ang = i * TAU / seg
            n = noise.noise(Vector((math.cos(ang) * 1.7, math.sin(ang) * 1.7, r * 3)))
            rr = r * (1 + .12 * n) if r > .25 else r
            verts.append((rr * math.cos(ang), rr * math.sin(ang), z + (.015 * n if 0 < z < .06 else 0)))
    for k in range(len(rings) - 1):
        for i in range(seg):
            j = (i + 1) % seg
            faces.append((k * seg + i, (k + 1) * seg + i, (k + 1) * seg + j, k * seg + j))
    a.part('Earth', 'Dirt', flat=True).mesh(verts, faces)
    for x, y, r in ((.38, .12, .05), (-.3, -.3, .04)):
        a.part('Earth', 'Dirt', flat=True).ico((r, r, r * .6), loc=(x, y, .015), sub=0, jitter=.3, seed=x)
    a.part('Mine_body', 'Crate').cyl(.25, .115, loc=(0, 0, .0275), seg=seg, bevel=.012, bseg=1)
    a.part('Mine_plate', 'Steel').cyl(.15, .025, loc=(0, 0, .0925), seg=10, bevel=0)
    a.part('Mine_fuze', 'Armor').cyl(.055, .025, loc=(0, 0, .115), seg=8, bevel=0)
    a.part('Mine_light', 'TeamGlow').sphere((.03, .03, .025), loc=(0, 0, .125), seg=8, rings=4, cut=0)


# ----------------------------------------------------------------------------- air-dropped crates
def _pallet(a, w, d, h=.15):
    """Wooden pallet w x d, h tall: bottom boards, three stringers and five gapped deck boards."""
    wood = a.part('Pallet', 'Wood')
    for x in (-w / 2 + .07, 0, w / 2 - .07):
        wood.box((.14, d, .03), loc=(x, 0, .015), bevel=0)
    for y in (-d / 2 + .06, 0, d / 2 - .06):
        wood.box((w, .12, h - .06), loc=(0, y, h / 2), bevel=0)
    bw = w / 5 - .05
    for i in range(5):
        wood.box((bw, d, .03), loc=(-w / 2 + w / 10 + i * w / 5, 0, h - .015), bevel=0)


def _stencil_star(a, f, r=.22, name='Stencils', mat='Medical'):
    """Five-point star painted on the face frame f (1 cm proud of the face)."""
    pts = [((r if i % 2 == 0 else r * .4) * math.cos(R90 + i * math.pi / 5),
            (r if i % 2 == 0 else r * .4) * math.sin(R90 + i * math.pi / 5)) for i in range(10)]
    a.part(name, mat).prism(pts, .02, loc=f @ Vector((0, 0, 0)), rot=f.to_euler('XYZ'), axis='Z', bevel=0)


def _flat_boxes(a, f, boxes, t, sink, name, mat, turn=0.0, parent=None):
    """Boxes (cx, cy, w, h) laid in the plane of face frame f, turned `turn` in that plane, each t
    thick with its back `sink` into the face. Neighbouring boxes should abut, not overlap."""
    m3 = f.to_3x3() @ Matrix.Rotation(turn, 3, 'Z')
    rot = m3.to_euler('XYZ')
    for cx, cy, w, h in boxes:
        a.part(name, mat, parent).box((w, h, t), loc=f @ (Matrix.Rotation(turn, 3, 'Z') @ Vector((cx, cy, 0)) +
                                                            Vector((0, 0, t / 2 - sink))), rot=rot, bevel=0)


def _canopy(a, parent, base, radius, height, gores, mats, confluence, risers, line_mat='Canvas',
            names=('Canopy', 'Canopy_b')):
    """Cargo parachute under the `parent` pivot (coordinates are relative to it): a scalloped dome
    of `gores` panels alternating mats, a thin double skin open at the apex vent and the skirt,
    suspension lines from every seam to the confluence ring and risers down to the load."""
    rings = ((.1, 1.0), (.45, .93), (.75, .74), (.93, .44), (1.0, .12), (.97, 0.0))
    n = gores * 2
    bx, by, bz = base
    outer, inner = [], []
    for i, (rk, hk) in enumerate(rings):
        o_ring, i_ring = [], []
        for c in range(n):
            ang = c * TAU / n
            mid = c % 2 == 1
            r = radius * rk * (1.03 if mid and 0 < i < len(rings) - 1 else 1.0)
            z = bz + height * hk + (height * .07 if mid and i == len(rings) - 1 else 0)
            o_ring.append((bx + r * math.cos(ang), by + r * math.sin(ang), z))
            ri = r - .035
            i_ring.append((bx + ri * math.cos(ang), by + ri * math.sin(ang), z - .03))
        outer.append(o_ring)
        inner.append(i_ring)
    for g in range(gores):
        verts, faces = [], []

        def v(p):
            verts.append(p)
            return len(verts) - 1
        for c in (2 * g, 2 * g + 1):
            d = (c + 1) % n
            for i in range(len(rings) - 1):
                faces.append((v(outer[i][c]), v(outer[i + 1][c]), v(outer[i + 1][d]), v(outer[i][d])))
                faces.append((v(inner[i][d]), v(inner[i + 1][d]), v(inner[i + 1][c]), v(inner[i][c])))
            faces.append((v(outer[0][c]), v(outer[0][d]), v(inner[0][d]), v(inner[0][c])))       # vent lip
            faces.append((v(outer[-1][c]), v(inner[-1][c]), v(inner[-1][d]), v(outer[-1][d])))   # skirt lip
        a.part(names[g % 2], mats[g % 2], parent).mesh(verts, faces)
    lines = a.part('Shroud_lines', line_mat, parent)
    cf = Vector(confluence)
    for g in range(gores):
        rim = Vector(outer[-1][2 * g])
        lines.tube([rim + (cf - rim).normalized() * .02, cf], .014, seg=3)
    for p in risers:
        a.part('Risers', 'Undercarriage', parent).tube([cf, Vector(p)], .02, seg=4)
    a.part('Confluence', 'Steel', parent).torus(.07, .02, loc=cf, seg=8, ring=4)


def supply_crate(a):
    """Air-dropped supply crate: a reinforced 2 x 2 m crate on a pallet, corner posts, crossed
    yellow-and-black hazard straps with buckles, stencilled stars, lifting eyes and a TeamGlow
    beacon; its olive-and-white cargo parachute, lines and risers hang under the `Parachute`
    empty, which the game hides on landing."""
    _pallet(a, 2.1, 2.1, .15)
    half, z0, z1 = .95, .145, 1.35
    a.part('Crate', 'Crate').box((2 * half, 2 * half, z1 - z0), loc=(0, 0, (z0 + z1) / 2), bevel=.04)
    armor = a.part('Corners', 'Armor')
    steel = a.part('Steel', 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            armor.box((.1, .1, z1 + .035 - z0), loc=(sx * .935, sy * .935, (z0 + z1 + .035) / 2), bevel=.01,
                      seg=1)
            armor.box((.3, .3, .03), loc=(sx * .82, sy * .82, z1 + .005), bevel=0)           # corner plates
            steel.box((.1, .03, .1), loc=(sx * .82, sy * .82, z1 + .05), rot=(0, 0, sx * sy * math.pi / 4),
                      bevel=0)                                                                 # lifting eyes
    # Straps: along X over the top and down the +-X faces, along Y (thicker, on top where they cross).
    top = Vector((0, 0, z1))
    sides = (z1 - z0 - .06)
    zc = (z0 + z1) / 2
    yel = a.part('Straps', 'SafetyStripe')
    dark = dict(mats=(None, 'Charred'), names=('Straps', 'Strap_stripes'), pitch=.3, lean=.6)
    yel.box((2 * half - .04, .16, .02), loc=top, bevel=0)
    _stripes(a, _plane(top, (1, 0, 0), (0, 1, 0)), 2 * half - .04, .14, t=.045, sink=.02, **dark)
    yel.box((.16, 2 * half - .04, .05), loc=top + Vector((0, 0, .015)), bevel=0)
    _stripes(a, _plane(top, (0, 1, 0), (-1, 0, 0)), 2 * half - .04, .14, t=.07, sink=.02, **dark)
    for s in (-1, 1):
        yel.box((.02, .16, sides), loc=(s * half, 0, zc), bevel=0)
        _stripes(a, _plane((s * half, 0, zc), (0, 0, -1), (0, s, 0)), sides, .14, t=.045, sink=.02, **dark)
        yel.box((.16, .02, sides), loc=(0, s * half, zc), bevel=0)
        _stripes(a, _plane((0, s * half, zc), (0, 0, -1), (-s, 0, 0)), sides, .14, t=.045, sink=.02, **dark)
        steel.box((.048, .22, .12), loc=(s * (half + .026), 0, .5), bevel=0)                   # buckles
        steel.box((.22, .048, .12), loc=(0, s * (half + .026), .5), bevel=0)
        _stencil_star(a, _plane((s * half, s * .5, .8), (0, s, 0), (0, 0, 1)))
        _stencil_star(a, _plane((-s * .5, s * half, .8), (-s, 0, 0), (0, 0, 1)))
    _beacon(a, .55, -.55, z1 + .01, mat='TeamGlow', r=.1)
    p = a.pivot('Parachute', (0, 0, z1 + .05))
    base = z1 + .05
    _canopy(a, p, (0, 0, 5.45 - base), 2.3, 1.6, 12, ('Canvas', 'Fuel'), (0, 0, 2.95 - base),
            [(sx * .82, sy * .82, z1 + .08 - base) for sx in (-1, 1) for sy in (-1, 1)])


def repair_crate(a):
    """Consumable repair drop: a green crate on a pallet with a red cross on a white field on its top
    and front and back, a wrench stencil on its sides, corner guards and rope handles; a red-and-
    white parachute with its lines under its own `Parachute` empty."""
    _pallet(a, 1.3, 1.3, .12)
    half, z0, z1 = .6, .115, .98
    a.part('Crate', 'RoofGreen').box((2 * half, 2 * half, z1 - z0), loc=(0, 0, (z0 + z1) / 2), bevel=.035)
    armor = a.part('Corners', 'Armor')
    for sx in (-1, 1):
        for sy in (-1, 1):
            armor.box((.08, .08, z1 - z0 + .01), loc=(sx * (half - .015), sy * (half - .015), (z0 + z1) / 2),
                      bevel=.008, seg=1)
            a.part('Steel', 'Steel').box((.08, .025, .08), loc=(sx * .5, sy * .5, z1 + .03),
                                         rot=(0, 0, sx * sy * math.pi / 4), bevel=0)             # lifting eyes

    def cross(f):
        _flat_boxes(a, f, [(0, 0, .62, .62)], .02, .01, 'Cross_field', 'Medical')
        _flat_boxes(a, f, [(0, 0, .15, .48), (-.165, 0, .18, .15), (.165, 0, .18, .15)], .045, .02, 'Cross',
                    'BarrelRed')
    cross(_plane((0, 0, z1), (1, 0, 0), (0, 1, 0)))
    wrench = [(x * 1.35, y * 1.35, w * 1.35, h * 1.35) for x, y, w, h in
              ((0, -.06, .07, .4), (0, -.3, .11, .08), (0, .19, .2, .1), (-.065, .285, .07, .09),
               (.065, .285, .07, .09))]
    zc = (z0 + z1) / 2
    for s in (-1, 1):
        cross(_plane((0, s * half, zc), (-s, 0, 0), (0, 0, 1)))
        _flat_boxes(a, _plane((s * half, 0, zc - .06), (0, s, 0), (0, 0, 1)), wrench, .02, .01, 'Stencils',
                    'Medical', turn=math.pi / 4)
        a.part('Handles', 'Canvas').tube([(s * (half - .01), -.2, z1 - .06), (s * (half + .05), -.16, z1 - .12),
                                          (s * (half + .05), .16, z1 - .12), (s * (half - .01), .2, z1 - .06)], .018,
                                         seg=4)
    p = a.pivot('Parachute', (0, 0, z1 + .04))
    base = z1 + .04
    _canopy(a, p, (0, 0, 3.75 - base), 1.55, 1.1, 8, ('Medical', 'BarrelRed'), (0, 0, 2.05 - base),
            [(sx * .5, sy * .5, z1 + .06 - base) for sx in (-1, 1) for sy in (-1, 1)])


BUILDERS = {
    'engineer_vehicle': (engineer_vehicle, dict(ao_distance=.6, grime_height=.55)),
    'ew_jammer': (ew_jammer, dict(ao_distance=.6, grime_height=.55)),
    'fpv_carrier': (fpv_carrier, dict(ao_distance=.6, grime_height=.55)),
    'fpv_drone': (fpv_drone, dict(ao_distance=.08, ground=False)),
    'mine_layer': (mine_layer, dict(ao_distance=.55, grime_height=.5)),
    'mine': (mine, dict(ao_distance=.15, grime_height=.1)),
    'supply_crate': (supply_crate, dict(ao_distance=.4, grime_height=.3)),
    'repair_crate': (repair_crate, dict(ao_distance=.35, grime_height=.25)),
}
