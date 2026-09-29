"""Machine Brigade boss vehicles built with frontier_kit: one showpiece per battlefield.

  * behemoth (Dunebreak): super-heavy "land battleship" on four separate track units, twin-gun
    main `Turret`, a forward secondary turret on `Mount_gun`, a twin AA gun on `Mount_mg` on the
    turret roof and hull-side missile racks.
  * mobile_fortress (Frostpeak): tracked land crawler on four big track pods carrying a
    multi-deck armoured superstructure with a glazed command bridge, a superfiring howitzer
    `Turret`, a rocket battery on `Mount_rocket`, an MG sponson on `Mount_mg`, a missile silo
    and a spinning `Radar` dish.
  * armored_train (Ironport): armoured diesel locomotive coupled to a gun wagon as one rigid
    model on 1.435 m gauge wheelsets (no rails: the map paints them). The wagon carries the
    cannon `Turret`, an MG cupola on `Mount_mg` and a rocket launcher on `Mount_rocket`.
  * mega_gunship (Ashfield): tandem-rotor heavy gunship (`Rotor` front, `Rotor_rear` rear), a
    chin cannon on `Mount_gun`, a door gun on `Mount_mg`, stub wings with rocket pods and
    missile rails.

Conventions follow mb_vehicles / mb_air: metres, +Z up, Blender -Y is the front, origin on the
ground at the footprint centre (the gunship's wheels stand on z = 0, like gunship_heli). Parts
named Main_cannon* / Muzzle_brake* under `Turret` recoil; `Muzzle_<slot>` empties sit at the
weapon openings, at most one per slot (twin barrels share one between the tips). Touching parts
overlap or stand at least 1 cm apart so no two visible faces are coplanar.

Each main gun is the highest thing inside its sweep, so the `Turret` can turn all the way round
without its barrel passing through the rest of the model (the fortress radar mast pole is the one
thin exception, straight behind the turret). Secondary mounts have blind arcs: the behemoth's
forward gun and the fortress MG sponson can reach into the superstructure behind them, and the
gunship's door gun into the fuselage.
"""
import math

from mathutils import Euler, Vector

from frontier_kit import chamfered

from mb_air import _fin
from mb_themes import ladder
from mb_town import fbox
from mb_vehicles import _antenna, _barrel, _dish, _flank, _frame, _glacis, _smoke, _tube_mouth

R90 = math.pi / 2
FORWARD = (R90, 0, 0)    # cylinder axis along Y (local +Z -> -Y)
BACKWARD = (-R90, 0, 0)  # local +Z -> +Y
ACROSS = (0, R90, 0)     # cylinder axis along X


# ----------------------------------------------------------------------------- shared helpers
def _hull2d(points):
    """Convex hull (Andrew's monotone chain) of 2D points, counter-clockwise."""
    pts = sorted({(round(p[0], 5), round(p[1], 5)) for p in points})

    def cross(o, p, q):
        return (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 1e-7:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 1e-7:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def track_outline(length, top, end_r, ground_r, ground_in, samples=20):
    """Counter-clockwise (y, z) outline of a track belt wrapped round an end wheel at each end
    (radius end_r, its top at `top`) and a ground wheel `ground_in` in from each end, with the
    belt's ground run 1 cm below the ground."""
    pts = []
    for s in (-1, 1):
        for cy, cz, r in ((s * (length / 2 - end_r), top - end_r, end_r),
                          (s * (length / 2 - ground_in), ground_r - .01, ground_r)):
            pts += [(cy + r * math.cos(u), cz + r * math.sin(u))
                    for u in (i * math.tau / samples for i in range(samples))]
    return _hull2d(pts)


def track_shoes(part, x, y0, outline, width, pitch, zmin=.12, skip=None, size=(.13, .07), embed=.025):
    """Track shoes (grousers) every `pitch` metres round a belt outline, half sunk into it. Shoes on
    the ground run (below zmin) are left out; skip(y, z, nz) drops more (hidden under a deck)."""
    segs, total = [], 0.0
    n = len(outline)
    for i in range(n):
        p, q = outline[i], outline[(i + 1) % n]
        L = math.hypot(q[0] - p[0], q[1] - p[1])
        segs.append((p, q, L, total))
        total += L
    count = max(1, int(total / pitch))
    off = size[1] / 2 - embed
    for k in range(count):
        d = (k + .5) * total / count
        p, q, L, s0 = next(s for s in segs if s[3] <= d < s[3] + s[2])
        t = (d - s0) / L
        py, pz = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
        ty, tz = (q[0] - p[0]) / L, (q[1] - p[1]) / L
        ny, nz = tz, -ty  # outward normal of a counter-clockwise outline
        if pz < zmin or (skip and skip(py, pz, nz)):
            continue
        part.box((width, size[0], size[1]), loc=(x, y0 + py + ny * off, pz + nz * off), rot=(math.atan2(tz, ty), 0, 0),
                 bevel=0)


def track_unit(a, x, y, length, width, top, end_r, ground_r, ground_in, wheel_r, wheels, side, pitch=.3,
               sprocket=-1, skip=None, wheel_seg=14):
    """One track unit centred at (x, y): a belt round two end wheels, shoes, rubber-rimmed road
    wheels and a toothed drive sprocket at the `sprocket` end (-1 front, +1 back) on the outer side
    (`side` = +1 for +X). Returns the belt outline for fenders and skirts."""
    outline = track_outline(length, top, end_r, ground_r, ground_in)
    a.part('Tracks', 'Undercarriage').prism([(y + p, z) for p, z in outline], width, loc=(x, 0, 0), axis='X',
                                            bevel=.035, seg=1)
    track_shoes(a.part('Track_shoes', 'Armor'), x, y, outline, width + .05, pitch, skip=skip)
    tyre, disc, hub = a.part('Road_wheels', 'Rubber'), a.part('Wheels', 'Steel'), a.part('Hubs', 'Undercarriage')
    ox = x + side * (width / 2 + .03)
    zc = ground_r - .01
    span = length / 2 - ground_in
    for i in range(wheels):
        wy = y - span + i * 2 * span / max(1, wheels - 1)
        tyre.cyl(wheel_r, .1, loc=(ox, wy, zc), rot=ACROSS, seg=wheel_seg, bevel=.025, bseg=1)
        disc.cyl(wheel_r * .76, .13, loc=(ox, wy, zc), rot=ACROSS, seg=wheel_seg - 2, bevel=0)
        hub.cyl(wheel_r * .26, .19, loc=(ox, wy, zc), rot=ACROSS, seg=6, bevel=0)
    ez = top - end_r
    for end in (-1, 1):
        ey = y + end * (length / 2 - end_r)
        r = end_r * .8
        disc.cyl(r, .12, loc=(ox, ey, ez), rot=ACROSS, seg=12, bevel=0)
        hub.cyl(r * .36, .2, loc=(ox, ey, ez), rot=ACROSS, seg=8, bevel=0)
        if end == sprocket:
            teeth = a.part('Sprockets', 'Steel')
            for k in range(10):
                u = k * math.tau / 10
                teeth.box((.1, .12, .12), loc=(ox, ey + math.cos(u) * r, ez + math.sin(u) * r), rot=(u, 0, 0), bevel=0)
    return outline


def _plate_bolts(part, x, ys, z, r=.035, h=.04):
    part.bolts([(x, y, z) for y in ys], r=r, h=h, rot=ACROSS, seg=6, bevel=0)


def _periscopes(part, cx, cy, z, r, count, start=0.0, arc=math.tau):
    for k in range(count):
        ang = start + (k + .5) * arc / count
        part.box((.12, .05, .08), loc=(cx + math.cos(ang) * r, cy + math.sin(ang) * r, z), rot=(0, 0, ang + R90),
                 bevel=0)


def _headlamp(a, loc, r=.14, hood=True):
    """Round headlamp facing -Y in an armoured hood."""
    x, y, z = loc
    a.part('Lamps', 'Lamp').cyl(r, .06, loc=(x, y - .02, z), rot=FORWARD, seg=10, bevel=0)
    body = a.part('Lamp_hoods', 'Armor')
    body.cyl(r + .05, .22, loc=(x, y + .1, z), rot=FORWARD, seg=10, bevel=.02, bseg=1)
    if hood:
        body.box((r * 2 + .16, .3, .05), loc=(x, y + .03, z + r + .06), bevel=.01, seg=1)


# ----------------------------------------------------------------------------- behemoth
def _sec6(y, wb, zb, ws, zs, wt, zt):
    """Six-point hull section: belly half-width wb at zb, side up to (ws, zs), chamfer to the roof."""
    return [(-wb, y, zb), (wb, y, zb), (ws, y, zs), (wt, y, zt), (-wt, y, zt), (-ws, y, zs)]


def behemoth(a):
    """Super-heavy "land battleship": four separate track units on their own fenders flank a
    tall stepped hull with a ship-like prow, a huge twin-gun turret with battleship rangefinder
    ears, a forward secondary turret, a twin AA gun on the turret roof and missile racks on the
    hull sides over the rear track units."""
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    glass = a.part('Vision_blocks', 'Glass')
    # Four track units, two per side, with an open waist between the front and rear pairs.
    TX, TY, TW, TL, TOP = 2.62, 3.0, 1.0, 5.2, 1.5
    fender = a.part('Fenders', 'Team')
    for sx in (-1, 1):
        for sy in (-1, 1):
            y0 = sy * TY
            track_unit(a, sx * TX, y0, TL, TW, TOP, .52, .42, 1.05, .34, 4, sx, pitch=.3, sprocket=sy,
                       skip=lambda py, pz, nz: nz > .8, wheel_seg=12)
            fender.box((1.2, TL + .2, .1), loc=(sx * TX, y0, 1.61), bevel=.03, seg=1)             # z 1.56 .. 1.66
            for end in (-1, 1):                                                                  # raked mudguards
                c = Vector((sx * TX, y0 + end * (TL / 2 + .15), 1.43))
                fender.box((1.2, .5, .08), loc=c, rot=(end * .75, 0, 0), bevel=.02, seg=1)
            armor.box((.07, TL - .5, .42), loc=(sx * 3.19, y0, 1.37), bevel=.015, seg=1)          # skirt lip
            _plate_bolts(steel, sx * 3.23, [y0 + d for d in (-1.8, 0, 1.8)], 1.3, r=.03)
        # Final-drive housing and cross shaft in the waist between the two units.
        armor.box((.85, .66, .9), loc=(sx * 2.58, 0, 1.05), bevel=.05, taper=(.9, .85))
        steel.cyl(.24, .2, loc=(sx * 3.05, 0, .95), rot=ACROSS, seg=12, bevel=.02, bseg=1)
    # Central hull with a prow, stepped up to a casemate that carries the main turret.
    full = (1.95, .45, 2.05, 2.3, 1.9, 2.55)
    hull.loft([_sec6(-6.3, .95, 1.05, 1.25, 1.45, 1.1, 1.62), _sec6(-5.3, 1.55, .5, 1.95, 1.75, 1.75, 2.22),
               _sec6(-4.35, *full), _sec6(5.35, *full), _sec6(5.95, 1.85, .7, 2.05, 2.2, 1.85, 2.45)], bevel=.07, seg=2)

    def sec(y, z1, w1, z0=2.53, w0=1.84):
        return [(-w0, y, z0), (w0, y, z0), (w1, y, z1), (-w1, y, z1)]
    hull.loft([sec(-2.2, 2.66, 1.8), sec(-1.45, 3.35, 1.6), sec(3.6, 3.35, 1.6), sec(4.2, 2.92, 1.72)], bevel=.06,
              seg=2)
    # Bolt-on plates on the hull sides (above the fenders) and the casemate flanks.
    for s in (-1, 1):
        for y in (-3.3, -1.25, .8, 4.85):
            armor.box((.06, 1.9, .5), loc=(s * 2.075, y, 2.0), bevel=.015, seg=1)
            _plate_bolts(steel, s * 2.11, (y - .75, y, y + .75), 2.17, r=.028)
        fx, fz, lean = _flank((1.84, 2.53), (1.6, 3.35), .52, .025)
        for y in (-.7, .7, 2.1):
            armor.box((.06, 1.25, .5), loc=(s * fx, y, fz), rot=(0, -s * lean, 0), bevel=.015, seg=1)
    # Prow: spare track links on the lower glacis, reactive armour on the upper; headlamps.
    links = a.part('Spare_links', 'Undercarriage')
    lower, upper = ((-6.3, 1.62), (-5.3, 2.22)), ((-5.3, 2.22), (-4.35, 2.55))
    gy, gz, grot = _glacis(*lower, .5, .03)
    for x in (-.95, -.32, .32, .95):
        links.box((.56, .3, .06), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=.012, seg=1)
        steel.box((.46, .06, .05), loc=(x, gy + .1, gz + .05), rot=(grot, 0, 0), bevel=0)
    gy, gz, grot = _glacis(*upper, .5, .045)
    for x in (-1.4, -.7, 0, .7, 1.4):
        armor.box((.64, .46, .12), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=.02, seg=1)
    for s in (-1, 1):
        _headlamp(a, (s * .7, -6.33, 1.34), r=.12)
        _headlamp(a, (s * 2.62, -5.6, 1.86), r=.11)
        armor.box((.36, .3, .2), loc=(s * 2.62, -5.45, 1.72), bevel=.03, seg=1)                  # lamp plinth
        steel.box((.18, .24, .16), loc=(s * .45, -6.3, 1.0), bevel=.02, seg=1)                   # tow hooks
        a.part('Tail_lights', 'Alloy').box((.18, .05, .1), loc=(s * 1.7, 5.975, 2.12), bevel=.01, seg=1)
        # Front fenders: stowage bin and jerrycans; rear fenders carry the missile racks.
        armor.box((.78, 1.25, .38), loc=(s * 2.62, -2.55, 1.84), bevel=.04, seg=1)
        steel.box((.8, .06, .06), loc=(s * 2.62, -2.55, 2.04), bevel=0)
        for dy in (-1.25, -1.03):
            a.part('Jerrycans', 'Hazard').box((.3, .18, .44), loc=(s * 2.62, dy, 1.87), bevel=.03, seg=1)
    # Front deck: driver's and radio operator's hatches, the forward turret ring.
    for s in (-1, 1):
        armor.cyl(.3, .07, loc=(s * 1.4, -3.95, 2.58), seg=14, bevel=.02, bseg=1)
        for dx in (-.18, 0, .18):
            glass.box((.13, .06, .08), loc=(s * 1.4 + dx, -4.33, 2.59), bevel=0)
    steel.cyl(.98, .12, loc=(0, -3.45, 2.57), seg=24, bevel=.03, bseg=1)                       # z 2.51 .. 2.63
    # Casemate roof: crew hatches and periscopes behind the barbette of the main turret.
    for s in (-1, 1):
        armor.cyl(.3, .07, loc=(s * 1.05, 2.75, 3.37), seg=14, bevel=.02, bseg=1)
        _periscopes(glass, s * 1.05, 2.75, 3.4, .36, 3, start=R90 - .8, arc=1.6)
    steel.cyl(1.58, .26, loc=(0, .4, 3.44), seg=28, bevel=.03)                                # z 3.31 .. 3.57
    # Missile racks on the hull sides, over the rear track units, raised 12 degrees. The one
    # Muzzle_missile sits at the left rack's mouths.
    rot = (-math.radians(12), 0, 0)
    for s in (-1, 1):
        x = s * 2.62
        armor.box((.6, 1.6, .16), loc=(x, 3.0, 1.73), bevel=.03, seg=1)                          # rack base
        armor.box((.1, 1.2, .5), loc=(s * 2.2, 3.1, 1.95), bevel=.02, seg=1)                      # side bracket
        centre = Vector((x, 2.9, 2.12))
        rack = _frame(centre, rot)
        a.part('Missile_racks', 'Team').box((.62, 1.9, .56), loc=centre, rot=rot, bevel=.04)
        frame = a.part('Rack_frames', 'Armor')
        for yy in (-.82, .82):
            frame.box((.67, .12, .61), loc=rack @ Vector((0, yy, 0)), rot=rot, bevel=.015, seg=1)
        for cz in (-.13, .13):
            for cx in (-.19, 0, .19):
                _tube_mouth(a, None, rack @ _frame((cx, -.95, cz), FORWARD), .085, protrude=.05, seg=8)
        steel.limb((x, 2.2, 1.8), tuple(rack @ Vector((0, -.55, -.28))), .1, .1, bevel=0)       # elevation ram
        if s < 0:
            a.pivot('Muzzle_missile', tuple(rack @ Vector((0, -1.0, 0))))
    # Rear deck: engine grilles, four exhaust stacks with heat shields, rear plate.
    for s in (-1, 1):
        deck.grille(1.1, 1.0, loc=(s * .75, 4.95, 2.56), rot=(-R90, 0, 0), slats=6, depth=.09, thickness=.04)
        for dy in (4.65, 5.2):
            x = s * 1.55
            steel.cyl(.15, 1.2, loc=(x, dy, 3.13), seg=10, bevel=0)                               # z 2.53 .. 3.73
            armor.cyl(.19, .6, loc=(x, dy, 3.08), seg=10, bevel=.02, bseg=1)                      # heat shield
            a.part('Soot', 'Charred').cyl(.165, .06, loc=(x, dy, 3.72), seg=10, bevel=0)
        steel.box((.08, .9, .08), loc=(s * 1.55, 4.925, 3.3), bevel=0)                            # stack bracket
    armor.box((3.6, .1, .5), loc=(0, 5.99, 1.6), bevel=.02, seg=1)                                 # rear plate
    for x in (-1.1, 1.1):
        steel.box((.2, .22, .18), loc=(x, 6.03, 1.2), bevel=.02, seg=1)
    _antenna(a, None, -1.6, 5.75, 2.47, 1.2)

    # Forward secondary turret on its own yaw mount.
    g = a.pivot('Mount_gun', (0, -3.45, 2.63))
    ft = a.part('Gun_turret', 'Team', g)
    ft.prism([(-.6, .76), (.6, .76), (.84, .3), (.84, -.3), (.5, -.8), (-.5, -.8), (-.84, -.3), (-.84, .3)], .56,
             loc=(0, 0, .3), axis='Z', bevel=.05, taper=.84)
    garm = a.part('Gun_armor', 'Armor', g)
    garm.box((.62, .34, .44), loc=(0, -.84, .3), bevel=.04)                                       # mantlet
    garm.box((1.0, .26, .32), loc=(0, .76, .26), bevel=.03, taper=(.95, .9))                      # bustle
    gs = a.part('Gun_steel', 'Steel', g)
    gs.cyl(.07, 2.3, loc=(0, -2.15, .3), rot=FORWARD, seg=10, bevel=0)                           # barrel
    gs.cyl(.11, .5, loc=(0, -1.2, .3), rot=FORWARD, seg=10, bevel=.02, bseg=1)                    # sleeve
    a.part('Gun_brake', 'Undercarriage', g).box((.2, .3, .18), loc=(0, -3.35, .3), bevel=.025)
    gs.cyl(.18, .1, loc=(.3, .2, .6), seg=10, bevel=.02, bseg=1)                                 # hatch
    gs.box((.22, .22, .16), loc=(-.35, -.2, .62), bevel=.03)                                      # sight
    a.part('Gun_sight', 'Glass', g).box((.16, .04, .09), loc=(-.35, -.32, .63), bevel=.01, seg=1)
    a.pivot('Muzzle_gun', (0, -3.52, .3), g)

    # Main turret.
    t = a.pivot('Turret', (0, .4, 3.57))
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-1.55, 2.25), (1.55, 2.25), (1.95, 1.35), (1.95, -.85), (1.25, -1.85), (-1.25, -1.85), (-1.95, -.85),
               (-1.95, 1.35)]
    turret.prism(outline, 1.0, loc=(0, 0, .51), axis='Z', bevel=.07, taper=.88)
    turret.box((3.3, 1.2, .82), loc=(0, 2.75, .47), bevel=.06, taper=(.93, .9))                   # bustle
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    for s in (-1, 1):
        # Spaced armour on the angled front faces, bins on the bustle, smoke dischargers.
        p0, p1 = Vector((s * 1.25, -1.85)), Vector((s * 1.95, -.85))
        mid, d = (p0 + p1) / 2, (p1 - p0).normalized()
        c = mid + Vector((d.y, -d.x)) * s * .06
        tarm.box((1.1, .14, .74), loc=(c.x, c.y, .44), rot=(0, 0, math.atan2(d.y, d.x)), bevel=.03, seg=1)
        tarm.box((.18, 1.5, .5), loc=(s * 1.72, 2.65, .5), bevel=.03, seg=1)
        _smoke(a, tsteel, 1.3, -.95, .92, s, count=4, gap=.1, r=.055, depth=.18)
    tarm.box((1.9, .7, .82), loc=(0, -1.95, .5), bevel=.06, taper=(.95, .9))                      # mantlet
    for s in (-1, 1):
        tarm.cyl(.3, .45, loc=(s * .52, -2.36, .5), rot=FORWARD, seg=14, bevel=.04)              # gun sleeves
    tips = []
    for s, suffix in ((-1, ''), (1, '_2')):
        tip = _barrel(a, t, start_y=-2.3, length=5.3, radius=.15, height=.5, brake=(.44, .5, .42),
                      sleeve=(.3, .9, .22), x=s * .52, suffix=suffix, seg=14)
        a.part(f'Muzzle_brake{suffix}', 'Undercarriage', t).box((.4, .16, .36), loc=(s * .52, tip[1] + .62, .5),
                                                                 bevel=.04)
        tips.append(tip)
    a.pivot('Muzzle_main', (0, tips[0][1], tips[0][2]), t)
    # Battleship rangefinder across the turret roof, lenses facing forward.
    tsteel.cyl(.15, 4.3, loc=(0, 1.7, .94), rot=ACROSS, seg=12, bevel=.02, bseg=1)
    for s in (-1, 1):
        tarm.box((.34, .46, .44), loc=(s * 2.12, 1.7, .94), bevel=.05)
        glass.box((.2, .04, .2), loc=(s * 2.12, 1.46, .96), bevel=.01, seg=1)
    # Commander's cupola with a searchlight, gunner's sight, vents, hatch, antennas.
    tsteel.cyl(.36, .26, loc=(1.0, .1, 1.0), seg=16, bevel=.04)
    a.part('Cupola_top', 'Armor', t).cyl(.3, .08, loc=(1.0, .1, 1.16), seg=16, bevel=.02, bseg=1)
    _periscopes(a.part('Periscope', 'Glass', t), 1.0, .1, 1.02, .37, 5)
    a.part('Searchlight', 'Lamp', t).cyl(.12, .05, loc=(1.45, -.35, 1.06), rot=FORWARD, seg=10, bevel=.01, bseg=1)
    tarm.cyl(.16, .24, loc=(1.45, -.22, 1.06), rot=FORWARD, seg=10, bevel=.02, bseg=1)
    tsteel.box((.44, .4, .28), loc=(-.95, -1.05, 1.0), bevel=.04)                                # gunner sight
    a.part('Sight', 'Glass', t).box((.32, .04, .15), loc=(-.95, -1.26, 1.02), bevel=.01, seg=1)
    a.part('Vents', 'Undercarriage', t).grille(1.3, .6, loc=(0, 2.85, .885), rot=(-R90, 0, 0), slats=5, depth=.07,
                                               thickness=.04)
    a.part('Hatch', 'Armor', t).cyl(.3, .07, loc=(.35, 1.05, 1.02), seg=14, bevel=.02, bseg=1)
    _antenna(a, t, -1.45, 3.1, .88, 1.0)
    _antenna(a, t, 1.45, 3.1, .88, .8)
    # Twin AA gun on the turret roof, on its own yaw mount.
    tsteel.cyl(.46, .1, loc=(-.9, .75, .98), seg=16, bevel=.02, bseg=1)
    m = a.pivot('Mount_mg', (-.9, .75, 1.03), t)
    base = a.part('AA_mount', 'Armor', m)
    base.cyl(.42, .16, loc=(0, 0, .09), seg=16, bevel=.03, bseg=1)
    base.box((.5, .6, .3), loc=(0, .05, .3), bevel=.04)                                           # cradle
    base.box((.66, .06, .36), loc=(0, -.34, .4), rot=(-.15, 0, 0), bevel=.012, seg=1, taper=(.85, 1))  # shield
    gun = a.part('AA_guns', 'Steel', m)
    for dx in (-.16, .16):
        gun.box((.12, .5, .14), loc=(dx, -.05, .42), bevel=.02, seg=1)                            # receivers
        gun.cyl(.035, 1.25, loc=(dx, -.925, .42), rot=FORWARD, seg=8, bevel=0)
        gun.cyl(.055, .16, loc=(dx, -1.52, .42), rot=FORWARD, seg=8, bevel=0)                     # flash hiders
        a.part('AA_ammo', 'Hazard', m).box((.14, .3, .22), loc=(dx * 2.4, .15, .34), bevel=.03, seg=1)
    a.pivot('Muzzle_mg', (0, -1.6, .42), m)


# ----------------------------------------------------------------------------- mobile fortress
def _snow(a, size, loc, parent=None, drifts=True):
    """Snow lying on a flat top whose surface is at loc's z: a soft slab half sunk into it, with two
    thicker drifts off-centre so the patch has a ragged outline (their tops stand 1-2 cm apart)."""
    part = a.part('Snow', 'SnowCap', parent)
    w, d, h = size
    x, y, z = loc
    b = min(.05, h * .45)
    if not drifts:
        part.box(size, loc=loc, bevel=b, seg=1)
        return
    # A core inset from the edges and two drifts reaching out to them: the outline is stepped.
    # Edges of the three slabs stay >= 2 % of the patch apart, so no two side faces coincide.
    part.box((w * .76, d * .7, h), loc=(x + w * .02, y - d * .05, z), bevel=b, seg=1)
    part.box((w * .44, d * .91, h + .03), loc=(x - w * .27, y - d * .015, z), bevel=b, seg=1)
    part.box((w * .88, d * .34, h + .05), loc=(x, y + d * .31, z), bevel=b, seg=1)


def _railing(part, points, h=.95, post=.05, rail=.03, every=1.4):
    """Handrail on posts along a polyline standing on the deck (two rails)."""
    pts = [Vector(p) for p in points]
    for p, q in zip(pts, pts[1:]):
        n = max(1, round((q - p).length / every))
        for i in range(n + (1 if q is pts[-1] else 0)):
            c = p + (q - p) * (i / n)
            part.box((post, post, h), loc=(c.x, c.y, c.z + h / 2), bevel=0)
    for z in (h * .55, h):
        part.tube([(p.x, p.y, p.z + z) for p in pts], rail, seg=4, caps=False)


def mobile_fortress(a):
    """Tracked land-crawler fortress: four big track pods with snow ploughs on hydraulic struts
    carry a chassis deck, a superstructure deck with lit portholes and a glazed command bridge. A
    howitzer turret on a tall barbette fires over the bridge; a rocket battery and a missile silo
    share the rear deck, an MG sponson guards the front corner, a search radar spins between the
    two smokestacks. Snow lies on the top edges."""
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Deck', 'Undercarriage')
    glass = a.part('Windows', 'Glass')
    lamp = a.part('Lamps', 'Lamp')
    # Track pods: a belt unit inside an armoured housing on a levelling strut.
    PX, PY, PL = 3.4, 5.2, 4.8
    pods = a.part('Pods', 'Team')
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * PX, sy * PY
            track_unit(a, x, y, PL, 1.9, 1.8, .62, .46, 1.1, .38, 4, sx, pitch=.34, sprocket=sy,
                       skip=lambda py, pz, nz: pz > 1.36, wheel_seg=12)
            pods.prism([(y + p, z) for p, z in ((-2.62, 1.35), (-2.62, 1.85), (-2.25, 2.3), (2.25, 2.3), (2.62, 1.85),
                                                 (2.62, 1.35))], 2.14, loc=(x, 0, 0), axis='X', bevel=.05)
            for dy in (-1.55, 0, 1.55):                                                            # side plates
                armor.box((.06, 1.35, .36), loc=(x + sx * 1.085, y + dy, 1.62), bevel=.015, seg=1)
            _snow(a, (1.9, 4.2, .07), (x, y, 2.31))
            steel.cyl(.4, 1.0, loc=(x, y, 2.75), seg=14, bevel=.02, bseg=1)                         # z 2.25 .. 3.25
            armor.box((1.05, 1.05, .22), loc=(x, y, 2.4), bevel=.04, seg=1)                          # lower collar
            armor.box((1.1, 1.1, .24), loc=(x, y, 2.93), bevel=.04, seg=1)                           # upper collar
            steel.limb((x, y - .95, 2.33), (x - sx * .55, y - .35, 2.98), .12, .12, bevel=0)          # steering ram
            armor.box((.5, .8, .4), loc=(x + sx * .72, y + 1.2, 2.47), bevel=.04, seg=1)             # drive motor
            steel.cyl(.1, .14, loc=(x + sx * .98, y + 1.2, 2.47), rot=ACROSS, seg=8, bevel=0)
            if sy < 0:
                # Snow plough ahead of each front pod, striped along its top edge.
                rot = (-.3, 0, 0)
                blade = _frame((x, -8.02, .74), rot)
                armor.box((2.3, .14, 1.05), loc=blade.to_translation(), rot=rot, bevel=.03, seg=1)
                for i in range(6):
                    mat = 'SafetyStripe' if i % 2 == 0 else 'Charred'
                    a.part('Plough_stripes', mat).box((.38, .03, .2), loc=blade @ Vector((-.95 + i * .38, -.075, .36)),
                                                      rot=rot, bevel=0)
                for dx in (-.7, .7):
                    steel.limb(tuple(blade @ Vector((dx, .07, .1))), (x + dx, -7.7, 1.55), .12, .12, bevel=0)
                _headlamp(a, (x - .55, -7.845, 2.0), r=.13)
                _headlamp(a, (x + .55, -7.845, 2.0), r=.13)
            else:
                a.part('Tail_lights', 'Alloy').box((.2, .05, .12), loc=(x + sx * .7, 7.835, 1.6), bevel=.01, seg=1)
    # Chassis deck on the four struts, an engine-room belly between the pods with fuel tanks.
    hull.prism([(-6.7, 3.0), (-7.3, 3.45), (-6.6, 4.3), (6.6, 4.3), (7.3, 3.5), (6.8, 3.0)], 7.2, bevel=.07)
    armor.box((4.4, 4.9, 1.8), loc=(0, 0, 2.15), bevel=.06)
    fuel = a.part('Fuel_tanks', 'Fuel')
    for s in (-1, 1):
        fuel.cyl(.42, 4.3, loc=(s * 2.55, 0, 2.42), rot=FORWARD, seg=14, bevel=.12)
        for yy in (-1.4, 0, 1.4):
            armor.cyl(.445, .14, loc=(s * 2.55, yy, 2.42), rot=FORWARD, seg=14, bevel=0)             # straps
        a.part('Hazard_bands', 'Hazard').cyl(.435, .3, loc=(s * 2.55, -1.95, 2.42), rot=FORWARD, seg=14, bevel=0)
        dark.grille(1.4, .6, loc=(s * 2.22, 1.2, 1.65), rot=(0, 0, s * R90), slats=4, depth=.06, thickness=.04)
        # Chassis sides: bolted plates, vents and a ladder from the ground at the waist.
        for yy in (-5.3, -3.2, 3.2, 5.3):
            armor.box((.06, 1.8, .9), loc=(s * 3.615, yy, 3.62), bevel=.02, seg=1)
        dark.grille(1.3, .6, loc=(s * 3.62, 0, 3.7), rot=(0, 0, s * R90), slats=4, depth=.06, thickness=.04)
        ladder(steel, (s * 3.66, -1.2, .35), 4.3, R90, width=.46, step=.4, rung=.03)
    # Front of the chassis: a raked bumper, spare track links and lamps on the glacis.
    front, back = (-7.3, 3.45), (-6.6, 4.3)
    gy, gz, grot = _glacis(front, back, .45, .03)
    for x in (-1.8, -1.2, -.6, 0, .6, 1.2, 1.8):
        a.part('Spare_links', 'Undercarriage').box((.52, .34, .06), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=.012,
                                                   seg=1)
    armor.box((6.2, .3, .45), loc=(0, -7.35, 3.2), bevel=.04, seg=1)
    armor.box((6.2, .3, .45), loc=(0, 7.15, 3.25), bevel=.04, seg=1)                              # rear bumper
    steel.box((.5, .4, .3), loc=(0, 7.35, 3.1), bevel=.03, seg=1)                                 # tow hitch
    gy, gz, grot = _glacis((7.3, 3.5), (6.6, 4.3), .55, .02)
    for s in (-1, 1):
        dark.grille(1.8, .55, loc=(s * 1.4, gy, gz), rot=(grot + R90, 0, 0), slats=4, depth=.06, thickness=.04)
    fbox(armor, '+y', (-1.3, 4.75, 4.72), (.9, .06, .8), out=.02, bevel=.015)                     # rear door
    fbox(steel, '+y', (-.95, 4.75, 4.72), (.06, .05, .2), out=.06)
    dark.grille(1.1, .45, loc=(1.3, 4.79, 4.75), rot=(0, 0, math.pi), slats=3, depth=.06, thickness=.04)
    for s in (-1, 1):
        _headlamp(a, (s * 2.6, -7.52, 3.2), r=.12, hood=False)
        a.part('Tail_lights', 'Alloy').box((.24, .05, .12), loc=(s * 2.8, 7.2, 3.62), rot=(-.96, 0, 0), bevel=.01,
                                           seg=1)
    # Superstructure deck with lit portholes along its sloped sides.
    def sec(y, z1, w1, z0=4.28, w0=2.9):
        return [(-w0, y, z0), (w0, y, z0), (w1, y, z1), (-w1, y, z1)]
    hull.loft([sec(-5.2, 4.62, 2.85), sec(-4.55, 5.5, 2.62), sec(4.35, 5.5, 2.62), sec(4.75, 5.1, 2.75)], bevel=.06,
              seg=2)
    px, pz, plean = _flank((2.9, 4.28), (2.62, 5.5), .55, .012)
    for s in (-1, 1):
        for i, yy in enumerate((-3.3, -2.2, -1.1, 0, 1.1, 2.2, 3.3)):
            part = lamp if (i + (s > 0)) % 3 else glass
            part.box((.04, .42, .3), loc=(s * px, yy, pz), rot=(0, -s * plean, 0), bevel=0)
        fx, fz, flean = _flank((2.9, 4.28), (2.62, 5.5), .2, .015)
        armor.box((.06, 8.4, .2), loc=(s * fx, -.1, fz), rot=(0, -s * flean, 0), bevel=.015, seg=1)   # rub strake
        _snow(a, (.4, 2.9, .07), (s * 2.38, .15, 5.51), drifts=False)
    # Walkways round the superstructure: railings, a ladder up to its roof on each side.
    rail = a.part('Railings', 'Steel')
    for s in (-1, 1):
        _railing(rail, [(s * 3.5, -5.1, 4.3), (s * 3.5, 6.4, 4.3)])
        ladder(steel, (s * 2.97, 2.8, 4.3), 5.5, R90, width=.42, step=.38, rung=.03)
    # Command bridge on the front of the superstructure: sloped glazing under a snowy visor roof.
    def bsec(y, z1, w1):
        return [(-2.3, y, 5.48), (2.3, y, 5.48), (w1, y, z1), (-w1, y, z1)]
    hull.loft([bsec(-4.3, 5.55, 2.28), bsec(-3.85, 6.45, 2.05), bsec(-1.75, 6.45, 2.05), bsec(-1.5, 6.1, 2.12)],
              bevel=.05, seg=2)
    gy, gz, grot = _glacis((-4.3, 5.55), (-3.85, 6.45), .5, .012)
    frames = a.part('Window_frames', 'Armor')
    for x in (-1.64, -.82, 0, .82, 1.64):
        glass.box((.72, .66, .04), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=0)
    gy2, gz2, _ = _glacis((-4.3, 5.55), (-3.85, 6.45), .5, .03)
    for x in (-2.05, -1.23, -.41, .41, 1.23, 2.05):
        frames.box((.08, .8, .05), loc=(x, gy2, gz2), rot=(grot, 0, 0), bevel=0)                   # mullions
    bx, bz, blean = _flank((2.3, 5.48), (2.05, 6.45), .55, .012)
    for s in (-1, 1):
        for yy in (-3.25, -2.35):
            glass.box((.04, .78, .5), loc=(s * bx, yy, bz), rot=(0, -s * blean, 0), bevel=0)
    armor.box((4.45, 2.8, .12), loc=(0, -2.75, 6.5), bevel=.03, seg=1)                           # visor roof
    _snow(a, (4.05, 2.4, .08), (0, -2.72, 6.57))
    for s in (-1, 1):
        # Searchlights on brackets at the bridge's front corners, below the gun line.
        steel.box((.3, .3, .12), loc=(s * 2.28, -4.05, 6.0), bevel=0)
        _headlamp(a, (s * 2.42, -4.2, 6.12), r=.13)
    _antenna(a, None, -3.3, 6.2, 4.3, 1.8)
    # Front deck corners: the MG sponson right, a searchlight tower left.
    for s in (-1, 1):
        armor.cyl(.72, .86, loc=(s * 3.2, -6.0, 3.93), seg=18, bevel=.04)                          # tub z 3.5 .. 4.36
        armor.cyl(.76, .08, loc=(s * 3.2, -6.0, 4.2), seg=18, bevel=0)                             # band
    steel.cyl(.25, .5, loc=(-3.2, -6.0, 4.6), seg=10, bevel=0)
    armor.box((.6, .5, .5), loc=(-3.2, -6.0, 5.05), bevel=.04)
    _headlamp(a, (-3.2, -6.26, 5.05), r=.18, hood=False)
    m = a.pivot('Mount_mg', (-(-3.2), -6.0, 4.37))
    cup = a.part('MG_cupola', 'Team', m)
    cup.cyl(.56, .4, loc=(0, 0, .21), seg=16, bevel=.04)
    cup.sphere((.5, .5, .22), loc=(0, 0, .4), seg=16, rings=8, cut=0)
    marm = a.part('MG_armor', 'Armor', m)
    marm.box((.5, .3, .3), loc=(0, -.5, .24), bevel=.04, seg=1)                                  # gun mantlet
    a.part('MG_glass', 'Glass', m).box((.2, .05, .08), loc=(.25, -.5, .45), rot=(0, 0, .45), bevel=0)
    mg = a.part('MG_guns', 'Steel', m)
    for dx in (-.11, .11):
        mg.cyl(.035, .95, loc=(dx, -1.1, .24), rot=FORWARD, seg=8, bevel=0)
        mg.cyl(.05, .14, loc=(dx, -1.55, .24), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_mg', (0, -1.63, .24), m)
    # Superstructure roof: two smokestacks, the radar mast between them, hatches and vents.
    for s in (-1, 1):
        x = s * 2.1
        steel.lathe([(.4, 5.46), (.4, 6.2), (.34, 6.35), (.34, 6.62)], loc=(x, 3.75, 0), seg=14)
        armor.cyl(.425, .12, loc=(x, 3.75, 5.9), seg=14, bevel=0)
        a.part('Soot', 'Charred').cyl(.28, .05, loc=(x, 3.75, 6.63), seg=12, bevel=0)
        armor.cyl(.26, .07, loc=(s * 1.35, -1.1, 5.52), seg=12, bevel=.02, bseg=1)                 # roof hatches
        dark.grille(.9, .7, loc=(s * 2.0, 2.3, 5.51), rot=(-R90, 0, 0), slats=4, depth=.07, thickness=.04)
    steel.cyl(.16, 2.0, loc=(0, 4.2, 6.48), r2=.1, seg=10, bevel=0)                               # mast z 5.48 .. 7.48
    armor.cyl(.3, .12, loc=(0, 4.2, 5.54), seg=12, bevel=.02, bseg=1)
    for zz in (6.1, 6.9):
        steel.box((.9, .06, .06), loc=(0, 4.2, zz), bevel=0)                                      # yard arms
    a.part('Beacon', 'Alloy').sphere(.06, loc=(.45, 4.2, 6.96), seg=6, rings=4)
    r = a.pivot('Radar', (0, 4.2, 7.48))
    rm = a.part('Radar_mast', 'Steel', r)
    rm.cyl(.2, .12, loc=(0, 0, .06), seg=12, bevel=.02, bseg=1)
    rm.box((.2, .3, .42), loc=(0, .08, .3), bevel=.03, seg=1)
    rm.limb((0, -.2, .45), (0, -.62, .5), .05, .05, bevel=0)                                     # feed horn
    _dish(a.part('Radar_dish', 'Armor', r), (0, -.12, .45), .85, .34, depth=.2, seg=14, tilt=.2)
    # Rear deck: rocket battery on its own mount, missile silo with its doors open.
    rk = a.pivot('Mount_rocket', (1.0, 6.0, 4.3))
    a.part('Launcher_base', 'Steel', rk).cyl(.72, .1, loc=(0, 0, .06), seg=16, bevel=.02, bseg=1)
    lbase = a.part('Launcher_armor', 'Armor', rk)
    lbase.box((.8, .8, .45), loc=(0, .1, .33), bevel=.04)
    for s in (-1, 1):
        lbase.box((.1, .5, .5), loc=(s * .7, .1, .72), bevel=.02, seg=1)                          # yoke arms
    pitch = math.radians(25)
    lrot = (-pitch, 0, 0)
    centre = Vector((0, 0, .98))
    pod = _frame(centre, lrot)
    a.part('Rocket_pod', 'Team', rk).box((1.3, 1.6, .9), loc=centre, rot=lrot, bevel=.05)
    band = a.part('Pod_bands', 'Armor', rk)
    for yy in (-.66, .66):
        band.box((1.35, .12, .95), loc=pod @ Vector((0, yy, 0)), rot=lrot, bevel=.015, seg=1)
    a.part('Launcher_steel', 'Steel', rk).cyl(.08, 1.56, loc=(0, .1, .72), rot=ACROSS, seg=8, bevel=0)
    for row in (-.25, 0, .25):
        for col in (-.45, -.15, .15, .45):
            _tube_mouth(a, rk, pod @ _frame((col, -.8, row), FORWARD), .1, protrude=.04, seg=8)
    a.pivot('Muzzle_rocket', tuple(pod @ Vector((0, -.86, 0))), rk)
    sx_, sy_ = -2.3, 6.0
    armor.shell(chamfered(1.3, 1.4, .15), .22, .08, loc=(sx_, sy_, 4.28), bevel=.015)
    dark.prism(chamfered(1.16, 1.26, .12), .02, loc=(sx_, sy_, 4.32), axis='Z', bevel=0)
    for dx in (-.28, .28):
        a.part('Silo_missiles', 'Fuel').lathe([(.2, 4.2), (.2, 4.36), (.14, 4.47), (.05, 4.55), (0, 4.57)],
                                              loc=(sx_ + dx, sy_, 0), seg=10)
        a.part('Hazard_bands', 'Hazard').cyl(.205, .06, loc=(sx_ + dx, sy_, 4.35), seg=10, bevel=0)
    lean = math.radians(30)
    for s in (-1, 1):
        armor.box((.06, 1.3, .66), loc=(sx_ + s * (.66 + .33 * math.sin(lean)), sy_, 4.5 + .33 * math.cos(lean)),
                  rot=(0, s * lean, 0), bevel=.015, seg=1)                                         # open doors
    a.pivot('Muzzle_missile', (sx_, sy_, 4.62))
    _snow(a, (1.2, .4, .07), (-2.6, 5.05, 4.31))

    # Howitzer turret on a tall barbette, firing over the bridge.
    armor.cyl(1.75, .76, loc=(0, 1.0, 5.86), seg=28, bevel=.04)                                   # z 5.48 .. 6.24
    steel.cyl(1.8, .1, loc=(0, 1.0, 6.28), seg=28, bevel=0)                                       # ring
    t = a.pivot('Turret', (0, 1.0, 6.33))
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-1.2, 2.05), (1.2, 2.05), (1.75, 1.2), (1.75, -.85), (1.05, -1.6), (-1.05, -1.6), (-1.75, -.85),
               (-1.75, 1.2)]
    turret.prism(outline, 1.18, loc=(0, 0, .6), axis='Z', bevel=.07, taper=.88)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm.box((1.3, .6, .95), loc=(0, -1.72, .72), bevel=.06, taper=(.94, .9))                     # mantlet
    tarm.cyl(.34, .4, loc=(0, -2.1, .75), rot=FORWARD, seg=14, bevel=.04)                        # gun collar
    tip = _barrel(a, t, start_y=-2.05, length=4.4, radius=.17, height=.75, brake=(.52, .6, .48),
                  sleeve=(.3, 1.1, .26), seg=14)
    a.part('Muzzle_brake', 'Undercarriage', t).box((.48, .18, .44), loc=(0, tip[1] + .74, .75), bevel=.04)
    a.pivot('Muzzle_main', tip, t)
    for s in (-1, 1):
        tsteel.cyl(.09, .6, loc=(s * .26, -2.5, 1.02), rot=FORWARD, seg=8, bevel=0)               # recoil cylinders
        tarm.box((.16, 1.6, .5), loc=(s * 1.6, .5, .55), bevel=.03, seg=1)                        # side bins
        _smoke(a, tsteel, 1.1, -.75, 1.25, s, count=3, gap=.1, r=.055, depth=.18)
    tsteel.cyl(.34, .24, loc=(.85, .3, 1.28), seg=16, bevel=.04)                                  # cupola
    a.part('Cupola_top', 'Armor', t).cyl(.28, .08, loc=(.85, .3, 1.43), seg=16, bevel=.02, bseg=1)
    _periscopes(a.part('Periscope', 'Glass', t), .85, .3, 1.3, .35, 5)
    a.part('Hatch', 'Armor', t).cyl(.28, .07, loc=(-.7, .9, 1.2), seg=14, bevel=.02, bseg=1)
    tsteel.box((.4, .36, .26), loc=(-.85, -.8, 1.28), bevel=.04)                                 # gunner sight
    a.part('Sight', 'Glass', t).box((.3, .04, .14), loc=(-.85, -.99, 1.3), bevel=0)
    a.part('Vents', 'Undercarriage', t).grille(1.0, .5, loc=(.55, 1.4, 1.2), rot=(-R90, 0, 0), slats=4, depth=.07,
                                               thickness=.04)
    tarm.box((1.4, .1, .6), loc=(0, 2.06, .6), bevel=.02, seg=1)                                 # loading door
    _snow(a, (.9, .5, .06), (-.55, 1.5, 1.2), t)


# ----------------------------------------------------------------------------- armoured train
GAUGE = 1.435          # standard gauge between the rail heads' inner faces
TREAD = .7525          # wheel tread centre line: over the rail head centres (gauge + 70 mm rail head)


def _bogie(a, y, axles, pitch, r, frame_len):
    """Railway bogie centred at y: flanged wheelsets on 1.435 m gauge (treads at x = +-0.7525), axle
    boxes, side frames with springs and a bolster. Wheels touch z = 0."""
    wheel, flange = a.part('Wheels', 'Steel'), a.part('Wheel_flanges', 'Armor')
    under = a.part('Bogies', 'Undercarriage')
    steel = a.part('Steel', 'Steel')
    for i in range(axles):
        ay = y + (i - (axles - 1) / 2) * pitch
        steel.cyl(.08, 1.9, loc=(0, ay, r), rot=ACROSS, seg=8, bevel=0)                            # axle
        for s in (-1, 1):
            wheel.cyl(r, .13, loc=(s * TREAD, ay, r), rot=ACROSS, seg=14, bevel=.015, bseg=1)
            flange.cyl(r + .035, .03, loc=(s * (TREAD - .08), ay, r), rot=ACROSS, seg=14, bevel=0)
            under.cyl(r * .4, .16, loc=(s * (TREAD + .05), ay, r), rot=ACROSS, seg=8, bevel=0)      # hub
            under.box((.2, .3, .3), loc=(s * .98, ay, r), bevel=.02, seg=1)                        # axle box
    for s in (-1, 1):
        under.box((.14, frame_len, .42), loc=(s * 1.1, y, r + .12), bevel=.03, seg=1)             # side frame
        for dy in (-.35, .35):
            steel.cyl(.08, .3, loc=(s * 1.1, y + dy, r + .48), seg=8, bevel=0)                     # springs
    under.box((2.1, .55, .26), loc=(0, y, r + .5), bevel=.03, seg=1)                                # bolster


def _underframe(a, y0, y1, front=True, back=True):
    """Sole bars between the headstocks at y0 and y1 (outer faces), striped headstocks, buffers
    reaching 0.38 m out and screw couplers."""
    under = a.part('Underframe', 'Undercarriage')
    steel = a.part('Buffers', 'Steel')
    for s in (-1, 1):
        under.box((.24, y1 - y0 - .3, .36), loc=(s * 1.28, (y0 + y1) / 2, 1.18), bevel=.02, seg=1)
    for end, face in ((-1, y0), (1, y1)):
        c = face - end * .1
        a.part('Headstocks', 'SafetyStripe').box((3.0, .2, .5), loc=(0, c, 1.15), bevel=.02, seg=1)
        bars = a.part('Headstock_bars', 'Charred')
        for k in range(7):
            bars.box((.13, .02, .56), loc=(-1.2 + k * .4, face + end * .005, 1.15), rot=(0, .6, 0), bevel=0)
        for s in (-1, 1):
            steel.cyl(.1, .34, loc=(s * .85, face + end * .15, 1.15), rot=FORWARD, seg=8, bevel=0)
            steel.cyl(.22, .06, loc=(s * .85, face + end * .345, 1.15), rot=FORWARD, seg=12, bevel=.015, bseg=1)
        a.part('Couplers', 'Armor').box((.26, .3, .2), loc=(0, face + end * .12, 1.1), bevel=.03, seg=1)
        for s in (-1, 1):
            steel.box((.3, .22, .05), loc=(s * 1.25, face - end * .3, .62), bevel=0)                 # steps
            steel.box((.04, .04, .5), loc=(s * 1.39, face - end * .3, .86), bevel=0)


def armored_train(a):
    """Armoured diesel locomotive (front) coupled to a gun wagon as one rigid model, 20 m over the
    buffers. The locomotive has a V plough, a headlamp, an armoured cab with vision slits and a long
    hood whose roof stays under the wagon gun's line of fire. The wagon carries the cannon turret on
    a barbette, an MG cupola and a rocket launcher, both lower than the gun."""
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Deck', 'Undercarriage')
    glass = a.part('Vision_slits', 'Glass')
    # ---- locomotive: y -9.55 .. -0.38 over the headstocks (the coupled buffer heads stand 1 cm apart)
    for y in (-7.35, -2.65):
        _bogie(a, y, 3, 1.1, .5, 3.2)
    _underframe(a, -9.55, -.38)
    hull.loft([_sec6(-9.4, 1.5, 1.34, 1.5, 1.9, 1.0, 2.3), _sec6(-8.75, 1.6, 1.34, 1.6, 2.05, 1.25, 2.85),
               _sec6(-8.2, 1.6, 1.34, 1.6, 2.2, 1.2, 3.35), _sec6(-6.5, 1.6, 1.34, 1.6, 2.2, 1.2, 3.35),
               _sec6(-6.2, 1.6, 1.34, 1.6, 2.05, 1.15, 2.95), _sec6(-1.1, 1.6, 1.34, 1.6, 2.05, 1.15, 2.95),
               _sec6(-.6, 1.55, 1.34, 1.55, 2.0, 1.1, 2.7)], bevel=.06, seg=2)
    # V plough ahead of the front bogie.
    armor.loft([[(-.35, -9.92, .15), (.35, -9.92, .15), (1.3, -9.62, .15), (1.4, -9.35, .15), (-1.4, -9.35, .15),
                 (-1.3, -9.62, .15)],
                [(-.3, -9.6, .95), (.3, -9.6, .95), (1.2, -9.45, .95), (1.35, -9.3, .95), (-1.35, -9.3, .95),
                 (-1.2, -9.45, .95)]], bevel=.03, seg=1)
    # Headlamp and marker lamps on the nose; vision slits in the cab's front and side plates.
    _headlamp(a, (0, -9.42, 2.0), r=.2)
    for s in (-1, 1):
        a.part('Lamps', 'Lamp').box((.16, .04, .12), loc=(s * 1.15, -9.415, 1.55), bevel=0)
    gy, gz, grot = _glacis((-8.75, 2.85), (-8.2, 3.35), .55, .012)
    for x in (-.7, 0, .7):
        glass.box((.5, .1, .04), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=0)
    gy, gz, grot = _glacis((-8.75, 2.85), (-8.2, 3.35), .8, .03)
    armor.box((2.2, .2, .05), loc=(0, gy, gz), rot=(grot, 0, 0), bevel=.01, seg=1)                 # slit brow
    fx, fz, flean = _flank((1.6, 2.2), (1.2, 3.35), .62, .012)
    gy, gz, grot = _glacis((-9.4, 2.3), (-8.75, 2.85), .5, .012)
    glass.box((.6, .1, .04), loc=(0, gy, gz), rot=(grot, 0, 0), bevel=0)                           # driver slit
    for s in (-1, 1):
        for y in (-7.85, -7.05):
            glass.box((.03, .5, .1), loc=(s * fx, y, fz), rot=(0, -s * flean, 0), bevel=0)
        # Cab door, steps and grab rails; bolted skirts over both bogies.
        fbox(armor, '+x' if s > 0 else '-x', (s * 1.6, -6.9, 1.75), (.62, .05, .76), out=.02, bevel=.01)
        steel.box((.04, .04, .5), loc=(s * 1.66, -6.5, 1.82), bevel=0)
        for y in (-7.35, -2.65):
            armor.box((.06, 3.3, .8), loc=(s * 1.645, y, 1.1), bevel=.015, seg=1)                   # z .7 .. 1.5
            _plate_bolts(steel, s * 1.68, [y + d for d in (-1.4, -.7, 0, .7, 1.4)], 1.4, r=.028)
        # Hood side: plate seams, louvres, a handrail on stanchions.
        for y in (-5.5, -3.75, -2.7, -.95):
            armor.box((.04, .07, .64), loc=(s * 1.615, y, 1.7), bevel=0)
        dark.grille(1.1, .5, loc=(s * 1.62, -4.65, 1.72), rot=(0, 0, s * R90), slats=4, depth=.05, thickness=.035)
        dark.grille(1.1, .5, loc=(s * 1.62, -1.8, 1.72), rot=(0, 0, s * R90), slats=4, depth=.05, thickness=.035)
        px, pz, plean = _flank((1.6, 2.05), (1.15, 2.95), .64, .025)
        for y in (-5.45, -4.1, -2.75, -1.4):                                                     # hood plates
            armor.box((.06, 1.22, .5), loc=(s * px, y, pz), rot=(0, -s * plean, 0), bevel=.015, seg=1)
            _plate_bolts(steel, s * (px + .03), (y - .5, y + .5), pz + .2, r=.025, h=.03)
        hx, hz, _ = _flank((1.6, 2.05), (1.15, 2.95), .3, .09)
        steel.tube([(s * hx, -6.0, hz), (s * hx, -.9, hz)], .025, seg=5)
        for y in (-5.8, -3.5, -1.1):
            steel.box((.03, .03, .1), loc=(s * (hx - .04), y, hz - .03), bevel=0)
    # Hood roof: radiator grilles over fans, exhaust stacks, horn; all below the gun line (3.4 m).
    for y in (-4.9, -2.9):
        a.part('Fans', 'Rubber').cyl(.42, .04, loc=(0, y, 2.97), seg=14, bevel=0)
        dark.grille(1.3, 1.2, loc=(0, y, 3.0), rot=(-R90, 0, 0), slats=6, depth=.07, thickness=.035)
    for s in (-1, 1):
        steel.cyl(.12, .45, loc=(s * .55, -5.95, 3.12), seg=10, bevel=0)                          # z 2.9 .. 3.35
        a.part('Soot', 'Charred').cyl(.135, .05, loc=(s * .55, -5.95, 3.34), seg=10, bevel=0)
        armor.box((.8, .5, .08), loc=(s * .4, -1.5, 2.97), bevel=.015, seg=1)                     # roof hatches
    steel.box((.06, .06, .1), loc=(.5, -7.2, 3.39), bevel=0)
    steel.cyl(.05, .3, loc=(.5, -7.2, 3.46), rot=FORWARD, r2=.09, seg=8, bevel=0)                  # horn
    armor.box((.9, .7, .1), loc=(-.3, -7.35, 3.38), bevel=.02, seg=1)                             # cab roof hatch
    _antenna(a, None, -.8, -6.8, 3.35, 1.5)

    # ---- gun wagon: y 0.38 .. 9.55
    for y in (2.4, 7.6):
        _bogie(a, y, 2, 1.8, .46, 2.7)
    _underframe(a, .38, 9.55)
    # Screw coupling bridging the two couplers.
    steel.box((.1, .5, .08), loc=(0, 0, 1.1), bevel=0)
    wagon = (1.6, 1.34, 1.6, 2.0, 1.3, 2.62)
    hull.loft([_sec6(.6, 1.55, 1.34, 1.55, 1.95, 1.2, 2.45), _sec6(1.1, *wagon), _sec6(8.9, *wagon),
               _sec6(9.4, 1.55, 1.34, 1.55, 1.95, 1.2, 2.45)], bevel=.06, seg=2)
    fx, fz, flean = _flank((1.6, 2.0), (1.3, 2.62), .5, .012)
    for s in (-1, 1):
        for y in (2.4, 7.6):
            armor.box((.06, 2.9, .8), loc=(s * 1.645, y, 1.1), bevel=.015, seg=1)                   # skirts
            _plate_bolts(steel, s * 1.68, [y + d for d in (-1.2, -.4, .4, 1.2)], 1.4, r=.028)
        for y in (1.6, 4.6, 5.8, 8.4):                                                          # vision slits
            glass.box((.03, .45, .09), loc=(s * fx, y, fz), rot=(0, -s * flean, 0), bevel=0)
        px, pz, plean = _flank((1.6, 2.0), (1.3, 2.62), .5, .025)
        for y, L in ((3.1, 2.4), (7.1, 1.9)):                                                     # chamfer plates
            armor.box((.06, L, .5), loc=(s * px, y, pz), rot=(0, -s * plean, 0), bevel=.015, seg=1)
        armor.box((.5, .4, .07), loc=(s * .75, .92, 2.62), bevel=.015, seg=1)                     # roof hatches
        for y in (3.4, 6.9):                                                                     # firing ports
            fbox(armor, '+x' if s > 0 else '-x', (s * 1.6, y, 1.72), (.34, .06, .26), out=.03, bevel=.01)
            fbox(dark, '+x' if s > 0 else '-x', (s * 1.6, y, 1.72), (.14, .04, .1), out=.06)
        fbox(armor, '+x' if s > 0 else '-x', (s * 1.6, 5.2, 1.7), (.8, .05, .66), out=.02, bevel=.01)  # door
        steel.box((.04, .04, .5), loc=(s * 1.66, 5.7, 1.7), bevel=0)
        for y in (1.1, 8.9):
            armor.box((.04, .07, .6), loc=(s * 1.615, y + (-.5 if y > 5 else .5), 1.7), bevel=0)  # plate seams
        a.part('Tail_lights', 'Alloy').box((.14, .04, .1), loc=(s * 1.0, 9.415, 2.2), bevel=0)
    fbox(armor, '+y', (0, 9.4, 1.9), (.9, .05, .8), out=.02, bevel=.01)                            # rear door
    a.part('Ammo_boxes', 'Crate').box((.5, .4, .3), loc=(1.0, 1.0, 2.6), bevel=.03, seg=1)
    a.part('Ammo_boxes', 'Crate').box((.5, .4, .3), loc=(-1.0, 9.0, 2.6), bevel=.03, seg=1)
    _antenna(a, None, 1.05, 9.05, 2.6, .9)
    # Barbette and turret ring; the turret yaws at 3.18 m, the gun axis at 3.8 m.
    armor.cyl(1.45, .92, loc=(0, 3.2, 2.66), seg=26, bevel=.04)                                  # z 2.2 .. 3.12
    steel.cyl(1.5, .1, loc=(0, 3.2, 3.13), seg=26, bevel=0)                                      # z 3.08 .. 3.18
    t = a.pivot('Turret', (0, 3.2, 3.18))
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-1.2, 1.7), (1.2, 1.7), (1.5, .9), (1.5, -.7), (.9, -1.45), (-.9, -1.45), (-1.5, -.7), (-1.5, .9)]
    turret.prism(outline, 1.0, loc=(0, 0, .51), axis='Z', bevel=.06, taper=.86)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm.box((1.0, .5, .75), loc=(0, -1.5, .58), bevel=.05, taper=(.94, .9))                      # mantlet
    tarm.cyl(.26, .36, loc=(0, -1.85, .62), rot=FORWARD, seg=14, bevel=.03)
    tip = _barrel(a, t, start_y=-1.7, length=5.6, radius=.14, height=.62, brake=(.42, .46, .38),
                  sleeve=(.3, .8, .2), seg=14)
    a.part('Muzzle_brake', 'Undercarriage', t).box((.38, .15, .34), loc=(0, tip[1] + .58, .62), bevel=.035)
    a.pivot('Muzzle_main', tip, t)
    for s in (-1, 1):
        tarm.box((.16, 1.3, .44), loc=(s * 1.37, .5, .48), bevel=.03, seg=1)                     # side bins
        _smoke(a, tsteel, .95, -.8, 1.02, s, count=3, gap=.09, r=.05, depth=.16)
    tsteel.cyl(.3, .22, loc=(.7, .35, 1.08), seg=16, bevel=.03)                                  # cupola
    a.part('Cupola_top', 'Armor', t).cyl(.25, .07, loc=(.7, .35, 1.21), seg=16, bevel=.02, bseg=1)
    _periscopes(a.part('Periscope', 'Glass', t), .7, .35, 1.1, .31, 5)
    a.part('Hatch', 'Armor', t).cyl(.26, .06, loc=(-.6, .75, 1.02), seg=14, bevel=.02, bseg=1)
    tsteel.box((.34, .32, .24), loc=(-.7, -.7, 1.1), bevel=.03)                                  # gunner sight
    a.part('Sight', 'Glass', t).box((.26, .04, .12), loc=(-.7, -.87, 1.12), bevel=0)
    a.part('Searchlight', 'Lamp', t).cyl(.11, .05, loc=(1.15, -.45, 1.08), rot=FORWARD, seg=10, bevel=0)
    tarm.cyl(.15, .22, loc=(1.15, -.33, 1.08), rot=FORWARD, seg=10, bevel=.02, bseg=1)
    a.part('Vents', 'Undercarriage', t).grille(.9, .4, loc=(0, 1.15, 1.01), rot=(-R90, 0, 0), slats=3, depth=.06,
                                               thickness=.035)
    _antenna(a, t, -.9, 1.25, 1.0, .5)
    # MG cupola on its own mount behind the turret (top 3.2 m).
    armor.cyl(.62, .1, loc=(0, 6.35, 2.64), seg=16, bevel=.02, bseg=1)                           # z 2.59 .. 2.69
    m = a.pivot('Mount_mg', (0, 6.35, 2.7))
    cup = a.part('MG_cupola', 'Team', m)
    cup.cyl(.52, .3, loc=(0, 0, .16), seg=16, bevel=.04)
    cup.sphere((.46, .46, .2), loc=(0, 0, .3), seg=16, rings=8, cut=0)
    marm = a.part('MG_armor', 'Armor', m)
    marm.box((.36, .26, .24), loc=(0, -.46, .18), bevel=.03, seg=1)
    a.part('MG_glass', 'Glass', m).box((.18, .05, .07), loc=(.22, -.44, .36), rot=(0, 0, .45), bevel=0)
    mg = a.part('MG_gun', 'Steel', m)
    mg.cyl(.035, .78, loc=(0, -.95, .18), rot=FORWARD, seg=8, bevel=0)
    mg.cyl(.05, .12, loc=(0, -1.3, .18), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_mg', (0, -1.37, .18), m)
    # Rocket launcher on its own mount at the rear (top 3.5 m, under the gun).
    rk = a.pivot('Mount_rocket', (0, 8.3, 2.64))
    a.part('Launcher_base', 'Steel', rk).cyl(.68, .08, loc=(0, 0, .05), seg=16, bevel=.015, bseg=1)
    lbase = a.part('Launcher_armor', 'Armor', rk)
    lbase.box((.5, .6, .2), loc=(0, .3, .18), bevel=.03, seg=1)
    pitch, L, H, W = math.radians(8), 1.4, .42, 1.3
    lrot = (-pitch, 0, 0)
    hinge = Vector((0, .5, .27))
    turn = Euler(lrot, 'XYZ').to_matrix()
    centre = hinge - turn @ Vector((0, L / 2, -H / 2))
    pod = _frame(centre, lrot)
    a.part('Rocket_box', 'Team', rk).box((W, L, H), loc=centre, rot=lrot, bevel=.04)   # launches from its tube face
    band = a.part('Pod_bands', 'Armor', rk)
    for yy in (-L / 2 + .1, L / 2 - .1):
        band.box((W + .05, .1, H + .05), loc=pod @ Vector((0, yy, 0)), rot=lrot, bevel=.012, seg=1)
    a.part('Launcher_steel', 'Steel', rk).cyl(.07, W + .1, loc=hinge, rot=ACROSS, seg=8, bevel=0)
    for row in (-.1, .1):
        for col in (-.45, -.15, .15, .45):
            _tube_mouth(a, rk, pod @ _frame((col, -L / 2, row), FORWARD), .085, protrude=.04, seg=8)
    a.pivot('Muzzle_rocket', tuple(pod @ Vector((0, -L / 2 - .05, 0))), rk)


# ----------------------------------------------------------------------------- mega gunship
def _squircle(y, w, zc, h, n=20, p=3.0, a0=None, a1=None):
    """Rounded-box fuselage section at y (half-width w, half-height h about zc; p = 2 is an ellipse,
    larger is boxier). With a0/a1 only that arc (radians, 0 = +X, counter-clockwise) is returned."""
    if a0 is None:
        us = [-R90 + i * math.tau / n for i in range(n)]
    else:
        us = [a0 + (a1 - a0) * i / max(1, n - 1) for i in range(n)]
    pts = []
    for u in us:
        c, s = math.cos(u), math.sin(u)
        pts.append((w * math.copysign(abs(c) ** (2 / p), c), y, zc + h * math.copysign(abs(s) ** (2 / p), s)))
    return pts


def _rotor(a, name, loc, phase, blades=3, radius=7.5, chord=.64):
    """Tandem-rotor head on its own pivot (spins about local Z): hub, blade grips with pitch links,
    wide blades from 0.5 m out to `radius` with yellow tips."""
    def side_of(d):
        return Vector((-d.y, d.x, 0))
    r = a.pivot(name, loc)
    hub = a.part(f'{name}_hub', 'Steel', r)
    hub.cyl(.4, .22, loc=(0, 0, .02), seg=14, bevel=.03, bseg=1)
    hub.cyl(.2, .3, loc=(0, 0, .25), seg=10, bevel=.04, bseg=1)
    blade = a.part(f'{name}_blades', 'Armor', r)
    tips = a.part(f'{name}_tips', 'Hazard', r)
    span = radius - .5
    for k in range(blades):
        ang = phase + k * math.tau / blades
        d = Vector((math.cos(ang), math.sin(ang), 0))
        rot = (0, 0, ang - R90)
        blade.box((chord, span, .075), loc=tuple(d * (.5 + span / 2) + Vector((0, 0, .04))), rot=rot, bevel=.025, seg=1,
                  taper=(.82, 1))
        tips.box((chord + .02, .42, .095), loc=tuple(d * (radius - .22) + Vector((0, 0, .04))), rot=rot, bevel=0)
        hub.box((.3, .75, .16), loc=tuple(d * .6 + Vector((0, 0, .04))), rot=rot, bevel=.03, seg=1)     # grips
        blade.box((chord * .8, .5, .12), loc=tuple(d * 1.0 + Vector((0, 0, .04))), rot=rot, bevel=.03, seg=1)  # cuff
        hub.limb(tuple(d * .35 - side_of(d) * .18 + Vector((0, 0, .06))), tuple(d * .85 - side_of(d) * .18 +
                 Vector((0, 0, .06))), .06, .06, bevel=0)                                         # lead-lag damper
        side = Vector((-d.y, d.x, 0))
        hub.limb(tuple(d * .5 + side * .12 + Vector((0, 0, .1))), tuple(d * .3 + side * .12 + Vector((0, 0, -.2))), .04,
                 .04, bevel=0)                                                                       # pitch links
    return r


def mega_gunship(a):
    """Tandem-rotor heavy gunship (Chinook-sized, 17 m fuselage): front `Rotor` on a pylon over the
    armoured cockpit, `Rotor_rear` on the tall aft pylon between two engine nacelles, long side
    sponsons on four-wheel gear, stub wings with rocket pods and missile rails, a chin cannon and
    a door gun. Origin on the ground under the fuselage centre (wheels at z = 0)."""
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    glass = a.part('Canopy', 'Glass')
    frames = a.part('Canopy_frames', 'Armor')
    body.loft([_squircle(-8.45, .45, 2.15, .42), _squircle(-8.1, .95, 2.2, .85), _squircle(-7.4, 1.22, 2.3, 1.15),
               _squircle(-6.5, 1.3, 2.35, 1.28), _squircle(5.6, 1.3, 2.35, 1.28), _squircle(7.3, 1.24, 2.62, 1.0),
               _squircle(8.45, 1.1, 3.05, .55)], bevel=0)
    # Armoured cockpit: glazing over the nose 2.5 cm proud of it, thick frames, side windows.
    arc = dict(n=13, a0=.22, a1=math.pi - .22)
    # Glass stations match the fuselage's (-8.1, -7.4) or lie on one of its straight spans (-7.1),
    # so the 3 cm offset holds everywhere and the fuselage never shows through.
    canopy = ((-8.1, .98, 2.2, .88), (-7.4, 1.25, 2.3, 1.18), (-7.1, 1.277, 2.317, 1.223))
    glass.loft([_squircle(y, w, zc, h, **arc) for y, w, zc, h in canopy])
    for y, w, zc, h in canopy:
        frames.tube(_squircle(y, w + .015, zc, h + .015, n=11, a0=.15, a1=math.pi - .15), .055, seg=6)
    for u in (R90, R90 - .7, R90 + .7):
        frames.tube([_squircle(y, w + .02, zc, h + .02, n=1, a0=u, a1=u)[0] for y, w, zc, h in canopy], .04, seg=5)
    for s in (-1, 1):                                                                             # chin windows
        glass.box((.5, .5, .03), loc=(s * .45, -7.95, 1.4), rot=(.9, 0, 0), bevel=0)
    for s in (-1, 1):
        glass.box((.04, .75, .45), loc=(s * 1.29, -6.65, 2.52), bevel=0)
        frames.box((.05, .82, .07), loc=(s * 1.29, -6.65, 2.78), bevel=0)
        armor.box((.05, 1.3, .5), loc=(s * 1.268, -6.35, 1.78), bevel=.015, seg=1)                   # cockpit armour
        for y in (-3.4, -2.2, -1.0, 1.4, 2.6, 3.8):                                                  # cabin windows
            glass.box((.03, .3, .3), loc=(s * 1.3, y, 2.55), bevel=0)
        for y in (-2.8, 2.0):                                                                        # cabin armour
            armor.box((.05, 1.6, .42), loc=(s * 1.268, y, 1.8), bevel=.015, seg=1)
            _plate_bolts(steel, s * 1.3, (y - .65, y, y + .65), 1.96, r=.025, h=.03)
    # Drive-shaft tunnel along the roof between the pylons, with access-panel ribs.
    body.box((.76, 8.4, .3), loc=(0, -.35, 3.68), bevel=.1, seg=2)                                 # z 3.53 .. 3.83
    for y in (-3.1, -.6, 1.4, 3.3):
        armor.box((.8, .08, .32), loc=(0, y, 3.69), bevel=.02, seg=1)
    # Frame bands round the fuselage (a rib every 2.8 m), 2 cm proud.
    bands = a.part('Frame_bands', 'Armor')
    for y in (-5.2, -1.6, 2.0, 4.6):
        bands.loft([_squircle(y - .05, 1.32, 2.35, 1.3, n=20), _squircle(y + .05, 1.32, 2.35, 1.3, n=20)])
    # Front rotor pylon over the cockpit and the tall aft pylon; engine nacelles on its flanks.
    body.box((1.4, 2.8, .8), loc=(0, -5.85, 3.8), bevel=.22, seg=2, taper=(.72, .82))              # z 3.4 .. 4.2
    steel.cyl(.17, .45, loc=(0, -5.8, 4.33), seg=10, bevel=0)                                      # mast
    steel.cyl(.34, .06, loc=(0, -5.8, 4.28), seg=12, bevel=0)                                      # swashplate
    body.prism([(3.6, 3.45), (8.4, 3.3), (8.4, 4.2), (7.9, 5.2), (5.7, 5.3), (4.5, 4.35)], 1.5, bevel=.14, seg=2)
    steel.cyl(.18, .4, loc=(0, 6.7, 5.43), seg=10, bevel=0)                                        # aft mast
    steel.cyl(.36, .06, loc=(0, 6.7, 5.36), seg=12, bevel=0)
    for s in (-1, 1):
        x = s * 1.38
        body.lathe([(.34, -1.65), (.46, -1.4), (.5, -.2), (.47, 1.1), (.36, 1.62)], loc=(x, 5.6, 4.3), rot=BACKWARD,
                   seg=14)
        dark.cyl(.35, .06, loc=(x, 3.95, 4.3), rot=FORWARD, seg=14, bevel=0)                         # intake
        a.part('Intake_screens', 'Steel').torus(.36, .035, loc=(x, 3.9, 4.3), rot=FORWARD, seg=14, ring=4)
        for k in range(3):
            a.part('Intake_screens', 'Steel').box((.7, .03, .03), loc=(x, 3.88 - k * .012, 4.3),
                                                  rot=(0, k * math.pi / 3, 0), bevel=0)
        steel.cyl(.13, .14, loc=(x, 3.9, 4.3), rot=FORWARD, r2=.04, seg=8, bevel=0)                  # bullet
        armor.box((.6, 1.5, .28), loc=(s * .95, 5.5, 4.25), bevel=.04, seg=1)                        # nacelle strut
        # IR-suppressing exhaust: an upturned duct with a sooty mouth.
        m = _frame((x + s * .08, 7.45, 4.42), (-R90 + .5, 0, s * -.35))
        dark.cyl(.3, .6, loc=m.to_translation(), rot=m.to_euler('XYZ'), seg=12, bevel=.02, bseg=1)
        a.part('Soot', 'Charred').cyl(.24, .04, loc=m @ Vector((0, 0, .29)), rot=m.to_euler('XYZ'), seg=12, bevel=0)
        dark.grille(.9, .45, loc=(s * .76, 6.6, 4.75), rot=(0, 0, s * R90), slats=4, depth=.05, thickness=.035)
    # Sponsons along the lower sides with the landing gear under them.
    def sponson(y, w, h, s):
        return [(s * 1.45 + px, y, pz) for px, _, pz in _squircle(y, w, 1.3, h, n=12, p=2.6)]
    for s in (-1, 1):
        body.loft([sponson(-3.95, .22, .2, s), sponson(-3.3, .44, .4, s), sponson(3.9, .46, .42, s),
                   sponson(4.65, .24, .22, s)], bevel=0)
        for y in (-2.4, -.6, 1.2, 3.0):
            armor.box((.05, 1.5, .34), loc=(s * 1.905, y, 1.3), bevel=.012, seg=1)                  # sponson panels
        a.part('Flares', 'Armor').box((.12, .5, .3), loc=(s * 1.9, 4.05, 1.72), bevel=.02, seg=1)
        dark.box((.04, .42, .22), loc=(s * 1.97, 4.05, 1.72), bevel=0)
    tyres, gear = a.part('Tyres', 'Rubber'), a.part('Gear', 'Steel')
    for s in (-1, 1):
        for dx in (-.16, .16):                                                                # twin front wheels
            tyres.cyl(.38, .2, loc=(s * 1.45 + dx, -3.25, .38), rot=ACROSS, seg=12, bevel=.06, bseg=1)
        gear.cyl(.06, .6, loc=(s * 1.45, -3.25, .38), rot=ACROSS, seg=6, bevel=0)
        gear.limb((s * 1.45, -3.25, .38), (s * 1.45, -3.1, 1.0), .12, .12, bevel=.02, seg=1)           # oleo
        gear.limb((s * 1.45, -3.2, .5), (s * 1.3, -2.4, 1.05), .07, .07, bevel=0)                     # drag brace
        tyres.cyl(.42, .24, loc=(s * 1.62, 4.1, .42), rot=ACROSS, seg=12, bevel=.07, bseg=1)          # aft wheels
        gear.limb((s * 1.5, 4.1, .42), (s * 1.45, 4.0, 1.0), .13, .13, bevel=.02, seg=1)
        gear.limb((s * 1.5, 4.05, .55), (s * 1.3, 3.2, 1.0), .07, .07, bevel=0)
    # Stub wings: two rocket pods and two missile rails on each; lights at the tips.
    pods = a.part('Pods', 'Armor')
    missiles, noses = a.part('Missiles', 'Fuel'), a.part('Missile_noses', 'Armor')
    fins = a.part('Missile_fins', 'Armor')
    for s in (-1, 1):
        body.prism([(s * 1.2, -.95), (s * 4.3, -.62), (s * 4.3, .5), (s * 1.2, .78)], .2, loc=(0, 0, 2.05), axis='Z',
                   bevel=.05)
        armor.box((.12, 1.0, .5), loc=(s * 4.33, -.05, 2.0), bevel=.02, seg=1)                       # tip plate
        a.part('Wing_lights', 'TeamGlow').box((.06, .14, .07), loc=(s * 4.41, .2, 2.18), bevel=0)
        for x in (2.33, 3.02):
            x *= s
            armor.box((.12, .7, .28), loc=(x, -.1, 1.83), bevel=.02, seg=1)                         # pylons
            pods.lathe([(.23, -1.0), (.32, -.8), (.32, .85), (.28, 1.0)], loc=(x, -.25, 1.4), rot=FORWARD, seg=12)
            dark.cyl(.26, .03, loc=(x, -1.255, 1.4), rot=FORWARD, seg=12, bevel=0)
            for k in range(7):
                ox, oz = (0, 0) if k == 6 else (math.cos(k * math.tau / 6) * .15, math.sin(k * math.tau / 6) * .15)
                a.part('Pod_tubes', 'Steel').cyl(.045, .04, loc=(x + ox, -1.27, 1.4 + oz), rot=FORWARD, seg=6, bevel=0)
        x = s * 3.72
        armor.box((.1, 1.5, .16), loc=(x, -.1, 1.87), bevel=.02, seg=1)                              # missile rail
        for dx in (-.19, .19):
            mx = x + dx
            for mz in (1.66, 1.4):                                                                   # 2 x 2 per wing
                missiles.cyl(.1, 1.5, loc=(mx, -.2, mz), rot=FORWARD, seg=10, bevel=0)
                noses.cyl(.1, .28, r2=.03, loc=(mx, -1.09, mz), rot=FORWARD, seg=10, bevel=0)
                for k in range(4):
                    _fin(fins, (mx, .42, mz), math.pi / 4 + k * R90, .08, .22, .02, .09)
            armor.box((.05, .5, .1), loc=(mx, -.2, 1.79), bevel=0)                                   # shoe
        armor.box((.08, 1.3, .3), loc=(x, -.2, 1.53), bevel=.015, seg=1)                             # lower rail
    a.pivot('Muzzle_rocket', (0, -1.3, 1.4))
    a.pivot('Muzzle_missile', (0, -1.25, 1.53))
    # Side door with the door gun on its own mount (right), a rescue hoist over the left door.
    fbox(a.part('Door', 'Charred'), '+x', (1.29, -4.6, 2.3), (.9, .03, 1.3), out=.01)
    fbox(armor, '+x', (1.29, -3.95, 2.3), (.08, .05, 1.4), out=.02)
    fbox(a.part('Door', 'Charred'), '-x', (-1.29, -4.6, 2.3), (.9, .03, 1.3), out=.01)
    armor.box((.5, .4, .3), loc=(-1.35, -4.6, 3.35), bevel=.04, seg=1)                             # hoist
    steel.limb((-1.35, -4.6, 3.35), (-1.7, -4.6, 3.3), .08, .08, bevel=0)
    steel.box((.3, .3, .06), loc=(1.43, -4.6, 1.62), bevel=0)                                     # gun sill
    m = a.pivot('Mount_mg', (1.52, -4.6, 1.7))
    mgp = a.part('Door_gun_mount', 'Steel', m)
    mgp.cyl(.05, .5, loc=(0, 0, .25), seg=8, bevel=0)                                             # pintle
    mgun = a.part('Door_gun', 'Armor', m)
    mgun.box((.16, .5, .18), loc=(0, .05, .55), bevel=.03, seg=1)                                 # receiver
    mgun.box((.16, .22, .2), loc=(.17, .15, .5), bevel=.02, seg=1)                                # ammo can
    barrels = a.part('Door_gun_barrels', 'Steel', m)
    barrels.cyl(.07, .8, loc=(0, -.6, .56), rot=FORWARD, seg=8, bevel=0)
    barrels.cyl(.085, .06, loc=(0, -.96, .56), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_mg', (0, -1.02, .56), m)
    # Chin cannon on its own mount; a sensor ball and landing lamp beside it.
    g = a.pivot('Mount_gun', (0, -7.35, 1.08))
    a.part('Gun_turret', 'Armor', g).sphere(.32, loc=(0, 0, -.12), seg=14, rings=8)
    gun = a.part('Gun', 'Steel', g)
    gun.cyl(.13, .3, loc=(0, -.38, -.2), rot=FORWARD, seg=10, bevel=.02, bseg=1)
    for k in range(3):
        ang = R90 + k * math.tau / 3
        gun.cyl(.035, 1.1, loc=(math.cos(ang) * .06, -1.05, -.2 + math.sin(ang) * .06), rot=FORWARD, seg=6, bevel=0)
    gun.cyl(.11, .08, loc=(0, -1.45, -.2), rot=FORWARD, seg=10, bevel=0)
    a.pivot('Muzzle_gun', (0, -1.62, -.2), g)
    armor.sphere(.19, loc=(.62, -7.75, 1.25), seg=12, rings=8)
    a.part('Sensor', 'Glass').cyl(.08, .04, loc=(.62, -7.93, 1.25), rot=FORWARD, seg=10, bevel=0)
    a.part('Lamps', 'Lamp').box((.3, .2, .05), loc=(-.5, -6.2, 1.06), bevel=0)
    # Refuelling probe along the right of the nose, antennas, rear ramp, beacons.
    steel.tube([(1.2, -6.4, 2.95), (1.14, -7.8, 2.93), (1.08, -9.6, 2.9)], .065, seg=8)
    steel.cyl(.09, .22, loc=(1.08, -9.68, 2.9), rot=FORWARD, r2=.05, seg=8, bevel=0)
    for y in (-2.5, 2.0):
        steel.box((.04, .6, .3), loc=(0, y, 3.72), rot=(-.4, 0, 0), bevel=0)                       # blade aerials
    steel.cyl(.015, .8, loc=(.6, 1.0, 1.0), seg=5, bevel=0)
    fbox(armor, '+y', (0, 8.45, 3.0), (1.9, .05, .9), out=.02, bevel=.015)                          # rear ramp door
    for x in (-.6, .6):
        steel.box((.12, .08, .08), loc=(x, 8.51, 2.56), bevel=0)                                   # ramp hinges
    a.part('Beacon', 'TeamGlow').sphere(.09, loc=(0, 7.4, 5.28), seg=8, rings=5)
    steel.cyl(.2, .3, loc=(0, 8.2, 4.05), rot=BACKWARD, seg=10, bevel=.02, bseg=1)                 # IR jammer
    a.part('Sensor', 'Glass').cyl(.16, .04, loc=(0, 8.37, 4.05), rot=BACKWARD, seg=10, bevel=0)
    for s in (-1, 1):
        a.part('Nav_lights', 'TeamGlow').box((.05, .12, .08), loc=(s * .77, 7.6, 4.7), bevel=0)
        for y in (-3.0, 3.5):
            steel.box((.28, .22, .04), loc=(s * 1.98, y, 1.05), bevel=0)                          # sponson steps
        dark.box((.05, .5, .3), loc=(s * .77, 4.8, 3.95), bevel=0)                                 # pylon vents
    a.part('Beacon', 'TeamGlow').sphere(.07, loc=(0, 1.0, 1.05), seg=8, rings=5)
    steel.cyl(.12, .2, loc=(0, -.6, 1.0), seg=8, bevel=0)                                          # cargo hook
    # Rotors: counter-phased so the blades interleave in the overlap.
    _rotor(a, 'Rotor', (0, -5.8, 4.6), R90)
    _rotor(a, 'Rotor_rear', (0, 6.7, 5.66), R90 + math.pi / 3)


BUILDERS = {
    'behemoth': (behemoth, dict(ao_distance=.9, grime_height=.8)),
    'mobile_fortress': (mobile_fortress, dict(ao_distance=1.1, grime_height=1.0)),
    'armored_train': (armored_train, dict(ao_distance=.8, grime_height=.7)),
    'mega_gunship': (mega_gunship, dict(ao_distance=.8, grime_height=.5)),
}
