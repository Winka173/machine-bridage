"""Machine Brigade play-test 5 (DECISIONS 20V): the owner's model list.

Conventions as everywhere: metres, +Z up, Blender -Y is the front (Unity +Z), +X the left side. Team / TeamGlow
parts are recoloured per army at runtime. Touching parts overlap or stand at least 1 cm apart (no coplanar faces).

  * fpv_drone: the FPV quadcopter a carrier (and the hangars, the airship) launches, drawn finer: a true-X carbon
    frame (bottom plate, tapered arms, top plate on standoffs), four motor bells with tri-blade props at the same
    places as before (0.16 m out on each diagonal, where ProjectilePool's rotor discs spin), a camera pod in a
    printed mount tilted up at the nose, a strapped battery with its lead, a video antenna and receiver whips, and
    the RPG-7 warhead slung under the nose (piezo fuse, ogive, band, booster). It flies a fifth smaller than before
    (WeaponEffects.QuadScale).
  * bunker_vehicle: the play-test 4 hull and its Deploy_* parts, dug in anew as an emplacement. Its spoil bank is
    one lofted horseshoe of earth round the scrape (a steep revetted inner face, a crest, a long outer slope, open
    at the rear for the ramp), crowned with two courses of sandbags across the front and one down the front of each
    side, grass on the slopes, clods, a camouflage net on poles over the engine deck and ammunition boxes by the
    ramp. The runtime sinks the hull deeper (hull-down: the hull top just above the ground), lifts the turret less
    and leans the side plates out only a little, so they line the pit's sides as armoured revetments under the
    bank's crest (VehicleView.Deploy: HullSink, MountLift, PlateFold). Dug in, only the turret and its gun show
    over the parapet.
  * sky_gunship: the AC-130 redrawn to read as a gunship at battle zoom (the owner took it for a bomber): the same
    airframe (high wing, four turboprops, upswept tail) with the left-side battery drawn big and sticking well out:
    the 25 mm GAU-12 gatling in a blister behind the crew door, the 40 mm Bofors behind its mantlet just aft of the
    wing, the 105 mm howitzer in a long bulged fairing further aft with its recoil sleeve and muzzle brake (the
    AC-130U's layout); a big sensor ball under the nose and a second one behind the crew door, and gun-deck windows. Muzzle_mg, Muzzle_gun and
    Muzzle_main sit at the three muzzles on the left side, Muzzle_ramp at the ramp launcher.
  * transport_plane: the same airframe without the battery, the sensors or the ramp launcher: the airlifter that
    flies airdrops and the MOAB (AirDrops, StrikeEffects), so it no longer carries a gunship's guns.
  * stealth_fighter: the faceted fighter with the middle of its body filled in: caret intakes with lips, a bump on
    the fuselage ahead of each mouth and dark ducts, a framed canopy (bow frame and sills), a dorsal spine with a
    sawtooth access panel, the refuelling door, blade antennas, sensor windows, sawtooth panel lines along the
    body, the bay doors' seams on the belly and hinge lines on the wings and tails.
"""
import functools
import math

from mathutils import Matrix, Vector

import mb_air2
import mb_detail as hd
import mb_p17_temp
import mb_p21_models
from mb_air import ACROSS, BACKWARD, FORWARD, R90, _dome, _sec
from mb_p17_temp import SF, _hex_top
from mb_vehicles import _frame

TAU = math.tau


def _along(p0, p1):
    """Location, rotation and length of a cylinder from p0 to p1."""
    a, b = Vector(p0), Vector(p1)
    v = b - a
    return tuple((a + b) / 2), Vector((0, 0, 1)).rotation_difference(v.normalized()).to_euler('XYZ'), v.length


# ----------------------------------------------------------------------------- FPV quadcopter
def fpv_drone(a):
    """FPV kamikaze quadcopter (flies along -Y, origin at its centre), 0.69 m prop tip to prop tip across the
    diagonal (see the module notes)."""
    carbon = a.part('Drone_frame', 'Undercarriage')
    steel = a.part('Drone_motors', 'Steel')
    bells = a.part('Drone_bells', 'Armor')
    props = a.part('Drone_props', 'BarrelRed')
    alloy = a.part('Drone_standoffs', 'Alloy')
    # Bottom plate and four tapered arms (true X), motor mounts at their tips.
    carbon.box((.1, .15, .006), loc=(0, 0, .006), bevel=0)
    for i, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        ang = math.atan2(sy, sx)
        mid = Vector((sx * .08, sy * .08, .007))
        carbon.box((.2, .036, .007), loc=tuple(mid), rot=(0, 0, ang), bevel=0, taper=(1, .75))
        carbon.cyl(.022, .007, loc=(sx * .16, sy * .16, .007), seg=8, bevel=0)                   # motor mount
        # Motor: stator base, bell, shaft and prop nut.
        bells.cyl(.023, .012, loc=(sx * .16, sy * .16, .017), seg=8, bevel=0)
        steel.cyl(.024, .02, loc=(sx * .16, sy * .16, .033), seg=10, bevel=0)
        steel.cyl(.005, .016, loc=(sx * .16, sy * .16, .05), seg=6, bevel=0)
        bells.cyl(.008, .008, loc=(sx * .16, sy * .16, .058), seg=6, bevel=0)
        # Tri-blade prop, each blade tapered and pitched, spun a little differently on each motor.
        props.cyl(.012, .008, loc=(sx * .16, sy * .16, .052), seg=6, bevel=0)
        for k in range(3):
            phi = i * .7 + k * TAU / 3
            c = Vector((sx * .16, sy * .16, .053)) + Vector((math.cos(phi), math.sin(phi), 0)) * .066
            props.box((.12, .024, .004), loc=tuple(c), rot=(.22 * (1 if (sx * sy) > 0 else -1), 0, phi), bevel=0,
                      taper=(.55, .7))
    # Top plate on four alloy standoffs; the flight stack between the plates.
    for sx in (-1, 1):
        for sy in (-1, 1):
            alloy.cyl(.005, .03, loc=(sx * .032, sy * .045, .025), seg=6, bevel=0)
    carbon.box((.078, .118, .005), loc=(0, 0, .042), bevel=0)
    a.part('Drone_stack', 'Rubber').box((.05, .05, .018), loc=(0, .01, .022), bevel=0)
    # Battery strapped on top, its lead and plug hanging off the back.
    a.part('Drone_battery', 'Team').box((.066, .12, .034), loc=(0, .01, .063), bevel=.005, seg=1)
    straps = a.part('Drone_straps', 'Rubber')
    for y in (-.02, .045):
        straps.box((.072, .014, .042), loc=(0, y, .063), bevel=0)
    a.part('Drone_plug', 'Hazard').box((.018, .02, .012), loc=(0, .082, .05), bevel=0)
    # Camera pod at the nose: a printed mount with side plates, the camera tilted 25 degrees up, its lens.
    pod = a.part('Drone_pod', 'Armor')
    tilt = (-.44, 0, 0)
    pod.box((.044, .04, .036), loc=(0, -.078, .03), rot=tilt, bevel=.004, seg=1)
    for sx in (-1, 1):
        carbon.box((.004, .05, .04), loc=(sx * .026, -.07, .028), bevel=0)
    lens_at = Vector((0, -.078, .03)) + Matrix.Rotation(-.44, 3, 'X') @ Vector((0, -.027, 0))
    pod.cyl(.013, .016, loc=tuple(lens_at), rot=(R90 - .44, 0, 0), seg=10, bevel=0)
    a.part('Drone_lens', 'Glass').cyl(.009, .006, loc=tuple(lens_at + Matrix.Rotation(-.44, 3, 'X') @ Vector((0, -.009, 0))),
                                      rot=(R90 - .44, 0, 0), seg=10, bevel=0)
    # Video antenna (a stubby pagoda on a mast) at the back, two receiver whips in a V.
    loc, rot, length = _along((0, .07, .046), (0, .1, .1))
    steel.cyl(.003, length, loc=loc, rot=rot, seg=5, bevel=0)
    a.part('Drone_antenna', 'Rubber').cyl(.012, .016, loc=(0, .103, .106), rot=(-.5, 0, 0), seg=8, bevel=0)
    for sx in (-1, 1):
        loc, rot, length = _along((sx * .03, .06, .045), (sx * .07, .12, .07))
        a.part('Drone_whips', 'Undercarriage').cyl(.002, length, loc=loc, rot=rot, seg=4, bevel=0)
    a.part('Drone_led', 'TeamGlow').box((.04, .006, .008), loc=(0, .077, .012), bevel=0)
    # The RPG-7 warhead slung under the nose along -Y: booster, band, body, ogive and piezo fuse, zip-tied on.
    charge = a.part('Drone_charge', 'Armor')
    profile = [(.022, .16), (.03, .12), (.03, .06), (.044, .03), (.046, -.03), (.04, -.08), (.028, -.12), (.012, -.15),
               (.004, -.16)]
    charge.lathe([(r, -z) for r, z in reversed(profile)], loc=(0, -.035, -.03), rot=FORWARD, seg=10)
    a.part('Drone_band', 'Hazard').cyl(.047, .018, loc=(0, -.055, -.03), rot=FORWARD, seg=10, bevel=0)
    steel.cyl(.007, .03, loc=(0, -.2, -.03), rot=FORWARD, seg=6, bevel=0)                          # fuse
    fins = a.part('Drone_fins', 'Undercarriage')
    for k in range(4):
        phi = k * R90 + math.pi / 4
        fins.box((.003, .03, .02), loc=(math.cos(phi) * .026, .12, -.03 + math.sin(phi) * .026), rot=(0, -phi, 0), bevel=0)
    for y in (-.02, .04):
        straps.box((.06, .008, .03), loc=(0, y, -.008), bevel=0)


# ----------------------------------------------------------------------------- bunker emplacement
def _heap(dirt, path, profile, heights, seed=0.0):
    """One lofted bank of earth along `path` [(x, y, nx, ny)...] (a point and its outward normal): the cross
    profile [(d, z)...] (d outward from the path), each z but the first and last scaled by `heights` [h...]."""
    verts, faces = [], []
    n = len(profile)
    for i, ((x, y, nx, ny), h) in enumerate(zip(path, heights)):
        for j, (d, z) in enumerate(profile):
            zz = z if j in (0, n - 1) else z * h
            wob = .05 * math.sin(i * 1.7 + j * 2.3 + seed) if 0 < j < n - 1 else 0.0
            verts.append((x + nx * (d + wob), y + ny * (d + wob), zz + wob * .5 * (1 if j > 1 else 0)))
    for i in range(len(path) - 1):
        for j in range(n - 1):
            q = [i * n + j, i * n + j + 1, (i + 1) * n + j + 1, (i + 1) * n + j]
            p0, p1, p3 = (Vector(verts[q[0]]), Vector(verts[q[1]]), Vector(verts[q[3]]))
            if (p1 - p0).cross(p3 - p0).z < 0:
                q.reverse()
            faces.append(tuple(q))
    dirt.mesh(verts, faces)


def _horseshoe(xi, yf, yr, r, tail, step=.3):
    """The bank's inner line: up the right side from the rear (y = yr + tail) to the front corner, across the
    front at y = yf, round the left corner and back down the left side; corners of radius r. Returns
    [(x, y, nx, ny)...] with outward normals, and each point's share along the path."""
    pts = []

    def run(p0, p1, normal):
        k = max(1, int((p1 - p0).length / step))
        for i in range(k):
            p = p0 + (p1 - p0) * (i / k)
            pts.append((p.x, p.y, normal.x, normal.y))

    def arc(c, a0, a1):
        k = max(3, int(abs(a1 - a0) * r / step))
        for i in range(k):
            t = a0 + (a1 - a0) * i / k
            pts.append((c.x + math.cos(t) * r, c.y + math.sin(t) * r, math.cos(t), math.sin(t)))
    run(Vector((-xi, yr + tail)), Vector((-xi, yf + r)), Vector((-1, 0)))
    arc(Vector((-xi + r, yf + r)), math.pi, 1.5 * math.pi)
    run(Vector((-xi + r, yf)), Vector((xi - r, yf)), Vector((0, -1)))
    arc(Vector((xi - r, yf + r)), 1.5 * math.pi, 2 * math.pi)
    run(Vector((xi, yf + r)), Vector((xi, yr + tail)), Vector((1, 0)))
    pts.append((xi, yr + tail, 1, 0))
    return pts


def _emplacement(a):
    """The dug-in bunker vehicle's emplacement, in ground space round the scrape (see the module notes). The
    view shows it (grown from 1 % to full height) as the hull sinks into the scrape."""
    p = a.pivot('Deploy_berm', (0, 0, 0))
    dirt = a.part('Berm_dirt', 'Dirt', p)
    grass = a.part('Berm_grass', 'Grass', p)
    bags = a.part('Berm_bags', 'Sandbag', p)
    wood = a.part('Berm_posts', 'Wood', p)
    net = a.part('Berm_net', 'Canvas', p)
    leaves = a.part('Berm_leaves', 'Foliage', p)
    crates = a.part('Berm_crates', 'Crate', p)
    xi, yf, yr, tail = 2.35, -4.95, 3.2, 1.9
    path = _horseshoe(xi, yf, yr, 1.3, tail)
    # Crest height along the path: 0.85 m across the front (two courses of sandbags on it bring it to 1.2 m, under
    # the gun), 1.0 m down the sides, sloping away to nothing over the last 2.6 m of each side (the rear ramp).
    heights = []
    for x, y, nx, ny in path:
        h = .85 if ny < -.5 else 1.0 if y < yr - .7 else max(0.0, 1.0 - (y - (yr - .7)) / 2.6)
        if -.5 <= ny < 0 and abs(nx) < .9:
            h = .92
        heights.append(max(h, .02))
    profile = [(-.4, -.35), (0, .96), (.38, 1.0), (1.1, .7), (2.0, .3), (2.9, -.03)]
    _heap(dirt, path, profile, heights, seed=1.3)
    # Grass patches on the outer slopes, clods and stones.
    for k, (x, y, nx, ny) in enumerate(path[2::5]):
        h = heights[2 + 5 * k]
        if h < .2:
            continue
        d = 1.55 + .35 * math.sin(k * 2.1)
        grass.ico(.34 + .1 * math.sin(k), loc=(x + nx * d, y + ny * d, .42 * h), sub=1, jitter=.3, seed=k * .7)
    for k, (x, y, z, r) in enumerate([(-3.9, -2.0, .18, .3), (4.1, 1.2, .14, .28), (-1.5, -7.2, .1, .32),
                                      (1.9, -7.0, .12, .36), (4.3, -3.3, .14, .26), (-4.1, 2.6, .1, .3)]):
        dirt.ico(r, loc=(x, y, z), sub=1, jitter=.25, seed=k * 1.7)
    # Sandbags: two courses along the front crest (staggered), one down the front of each side.
    for row, z in enumerate((.86, 1.02)):
        n = 9 - row                                                   # the upper course sits over the joints
        for i in range(n):
            x = (i - (n - 1) / 2) * .54
            bags.box((.52, .3, .17), loc=(x, yf - .22, z), rot=(0, 0, .04 * ((i % 3) - 1)), bevel=.07, seg=1)
    for s in (-1, 1):
        for i in range(3):                                            # round the front corners
            ang = 1.5 * math.pi + s * (.45 + i * .38)
            c = Vector((s * (xi - 1.3), yf + 1.3))
            q = c + Vector((math.cos(ang), math.sin(ang))) * 1.5
            bags.box((.52, .3, .17), loc=(q.x, q.y, .95), rot=(0, 0, ang + R90), bevel=.07, seg=1)
        for i in range(5):                                            # down the sides
            bags.box((.3, .52, .17), loc=(s * (xi + .22), -3.1 + i * .56, 1.08), rot=(0, 0, .04 * ((i % 3) - 1)),
                     bevel=.07, seg=1)
    # Camouflage net over the engine deck on four poles, sagging between them, foliage tied into it.
    x0, x1, y0, y1 = 2.7, 2.7, 2.2, 4.9
    wood_posts = [(-x0, y0), (x1, y0), (-x0, y1), (x1, y1)]
    for x, y in wood_posts:
        wood.cyl(.05, 1.55, loc=(x, y, .7), seg=6, bevel=0)
    verts, faces = [], []
    nx_, ny_ = 7, 5
    for j in range(ny_ + 1):
        for i in range(nx_ + 1):
            u, v = i / nx_, j / ny_
            x = -x0 + (x0 + x1) * u
            y = y0 + (y1 - y0) * v
            sag = .28 * math.sin(math.pi * u) * math.sin(math.pi * v)
            verts.append((x, y, 1.45 - sag + .04 * math.sin(i * 1.9 + j * 1.3)))
    for j in range(ny_):
        for i in range(nx_):
            q = (j * (nx_ + 1) + i, j * (nx_ + 1) + i + 1, (j + 1) * (nx_ + 1) + i + 1, (j + 1) * (nx_ + 1) + i)
            faces.append(q)
    net.mesh(verts, faces)
    # Its underside, a centimetre lower (seen from inside the pit and from a low camera).
    net.mesh([(x, y, z - .01) for x, y, z in verts], [tuple(reversed(q)) for q in faces])
    for k in range(9):
        u, v = (k % 3 + .5) / 3, (k // 3 + .5) / 3
        x = -x0 + (x0 + x1) * u + .2 * math.sin(k * 3.1)
        y = y0 + (y1 - y0) * v
        z = 1.45 - .28 * math.sin(math.pi * u) * math.sin(math.pi * v) + .05
        leaves.ico(.26 + .06 * math.sin(k), loc=(x, y, z), sub=1, jitter=.35, seed=k * 2.3)
    # Ammunition boxes and a jerrycan by the ramp.
    for k, (x, y, z, rz) in enumerate(((-3.2, 4.3, .16, .2), (-3.25, 4.95, .16, -.1), (-3.2, 4.6, .48, .05))):
        crates.box((.62, .38, .32), loc=(x, y, z), rot=(0, 0, rz), bevel=.03, seg=1)
    a.part('Berm_can', 'Team', p).box((.2, .36, .46), loc=(3.25, 4.5, .23), rot=(0, 0, .3), bevel=.04, seg=1)


def bunker_vehicle(a):
    """Deployable bunker vehicle: play-test 4's hull, blade, plates, spades and riser, with the emplacement of
    play-test 5 as its Deploy_berm (see the module notes)."""
    original = mb_p21_models._bunker_berm
    mb_p21_models._bunker_berm = _emplacement
    try:
        mb_p21_models.bunker_vehicle(a)
    finally:
        mb_p21_models._bunker_berm = original


# ----------------------------------------------------------------------------- AC-130 gunship
def _battery(a):
    """The left-side battery, drawn big enough to read from the battle camera: a barrel out of the left side (+X),
    tilted down. Returns nothing; sets Muzzle_mg, Muzzle_gun and Muzzle_main."""
    guns = a.part('Guns', 'Steel')
    ports = a.part('Gun_ports', 'Armor')
    dark = a.part('Gun_bores', 'Undercarriage')
    # 25 mm GAU-12 in a blister behind the crew door: five barrels in a clamp, a muzzle clamp.
    at, rot = mb_air2._side_gun((.9, -3.3, -.05), tilt=.16)
    ports.sphere((.36, .62, .42), loc=(.84, -3.3, -.05), seg=14, rings=8)
    guns.cyl(.13, .22, loc=at(.3), rot=rot, seg=12, bevel=.01, bseg=1)
    for k in range(5):
        ang = k * TAU / 5
        off = Vector((0, math.cos(ang) * .07, math.sin(ang) * .07))
        guns.cyl(.026, 1.25, loc=tuple(Vector(at(.95)) + off), rot=rot, seg=6, bevel=0)
    guns.cyl(.11, .08, loc=at(.9), rot=rot, seg=12, bevel=0)
    guns.cyl(.105, .07, loc=at(1.52), rot=rot, seg=12, bevel=0)
    dark.cyl(.05, .02, loc=at(1.565), rot=rot, seg=8, bevel=0)
    a.pivot('Muzzle_mg', at(1.6))
    # 40 mm Bofors behind a mantlet just aft of the wing: breech housing, recuperator over the barrel, flash hider.
    at, rot = mb_air2._side_gun((.9, 1.75, .02), tilt=.14)
    ports.box((.36, 1.0, .8), loc=(.9, 1.75, .04), bevel=.06, seg=1)
    ports.box((.12, .7, .6), loc=(1.1, 1.75, .03), bevel=.03, seg=1)                                 # mantlet
    guns.cyl(.14, .42, loc=at(.35), rot=rot, seg=12, bevel=.02, bseg=1)
    guns.cyl(.075, 1.95, loc=at(1.3), rot=rot, seg=12, bevel=0)
    top = Vector((0, 0, .15))
    guns.cyl(.05, 1.0, loc=tuple(Vector(at(.85)) + top), rot=rot, seg=8, bevel=0)                   # recuperator
    guns.cyl(.12, .42, r2=.085, loc=at(2.42), rot=rot, seg=12, bevel=0)                             # flash hider
    dark.cyl(.05, .02, loc=at(2.64), rot=rot, seg=8, bevel=0)
    a.pivot('Muzzle_gun', at(2.66))
    # 105 mm howitzer in a long bulged fairing aft: recoil sleeve, long barrel, double-baffle muzzle brake.
    at, rot = mb_air2._side_gun((.9, 3.45, .0), tilt=.12)
    ports.sphere((.42, 1.1, .62), loc=(.8, 3.45, .02), seg=16, rings=9)
    ports.box((.14, .9, .82), loc=(1.18, 3.45, .0), bevel=.04, seg=1)                                # gun shield
    guns.cyl(.2, .7, loc=at(.55), rot=rot, seg=14, bevel=.02, bseg=1)                               # recoil sleeve
    guns.cyl(.115, 2.6, loc=at(1.9), rot=rot, seg=14, bevel=0)
    brake = a.part('Howitzer_brake', 'Armor')
    brake.box((.34, .4, .36), loc=at(3.3), rot=(0, .12, 0), bevel=.04, seg=1)
    for dy in (-.21, .21):
        dark.box((.2, .02, .2), loc=tuple(Vector(at(3.3)) + Vector((0, dy, 0))), rot=(0, .12, 0), bevel=0)
    dark.cyl(.07, .02, loc=at(3.48), rot=rot, seg=10, bevel=0)
    a.pivot('Muzzle_main', at(3.5))
    # Gun-deck window strip along the left side over the battery.
    glass = a.part('Gun_deck_windows', 'Glass')
    for y in (-2.6, -2.0, 2.45, 2.85):
        glass.box((.03, .3, .2), loc=(.975, y, .5), bevel=0)
    if hd.on(a):  # bolts round the three gun ports' faces
        for yc, zc, face, dy, dz in ((-3.3, -.05, 1.2, .2, .16), (1.75, .03, 1.165, .3, .26), (3.45, 0, 1.255, .38, .34)):
            for sy in (-1, 1):
                for sz in (-1, 1):
                    hd.bolt(guns, (face, yc + sy * dy, zc + sz * dz), hd.RIGHT_X, r=.018, h=.026)


def _sensors(a):
    """Sensor turrets: a big ball under the nose (the targeting FLIR), a second behind the gear, both looking
    left; each on a neck with a window, a small lens and a housing plate."""
    armor = a.part('Sensor_turrets', 'Armor')
    glass = a.part('Sensor', 'Glass')
    for (x, y, z), rr in (((.5, -4.7, -1.05), .36), ((.74, -1.9, -.88), .27)):
        armor.cyl(rr * .5, .26, loc=(x, y, z + rr * .95), seg=12, bevel=0)
        armor.sphere(rr, loc=(x, y, z), seg=16, rings=10)
        glass.cyl(rr * .45, .05, loc=(x + rr - .015, y, z - rr * .12), rot=ACROSS, seg=12, bevel=0)
        glass.cyl(rr * .2, .05, loc=(x + rr * .82 - .01, y - rr * .5, z + rr * .12), rot=(0, R90, -.6), seg=8, bevel=0)
        armor.box((.03, rr * 1.2, rr * 1.4), loc=(x - rr * .9, y, z), bevel=0)


def sky_gunship(a, detail=False, armed=True):
    """AC-130 gunship (see the module notes), span about 17 m. With armed=False, the transport_plane: the same
    airframe without the battery, the sensors and the ramp launcher."""
    # The airframe is mb_air2's; its battery, sensors and ramp launcher are drawn afresh here (or left off).
    original = (mb_air2._side_gun, a.part, a.pivot)
    skip = {'Guns', 'Gun_ports', 'Howitzer_brake', 'Sensor'}
    dropped = []

    def part(name, mat, parent=None, flat=False):
        if name in skip:
            dropped.append(name)
            return _Sink()
        return original[1](name, mat, parent, flat)

    def pivot(name, loc, parent=None):
        if name in ('Muzzle_mg', 'Muzzle_gun', 'Muzzle_main', 'Muzzle_ramp'):
            return None
        return original[2](name, loc, parent)
    bolt = mb_air2.hd.bolt

    def no_port_bolts(part_, p, rot=None, **kw):
        # The old gun ports' bolts (on their faces, outside the skin) go with the old ports.
        if p[0] < 1.0:
            bolt(part_, p, rot, **kw) if rot is not None else bolt(part_, p, **kw)
    a.part, a.pivot = part, pivot
    mb_air2.hd.bolt = no_port_bolts
    try:
        mb_air2.sky_gunship(a, detail=detail)
    finally:
        a.part, a.pivot = original[1], original[2]
        mb_air2.hd.bolt = bolt
    if armed:
        _battery(a)
        _sensors(a)
        a.pivot('Muzzle_ramp', (0, 4.95, -.42))
    else:
        # The ramp launcher is Armor and Steel on the shared parts; the transport keeps it as a cargo-door fairing.
        pass


class _Sink:
    """A part that swallows everything drawn on it (the old battery, left off)."""

    def __getattr__(self, name):
        return lambda *args, **kwargs: self


# ----------------------------------------------------------------------------- stealth fighter
def _skin(y, x, lift=.012):
    """A point on the chined body's upper skin at (x, y), `lift` above it."""
    return (x, y, _hex_top(SF, y, x) + lift)


def _panel_line(part, pts, r=.012, step=.35):
    """A panel line over the upper skin through [(x, y)...], subdivided so it follows the facets."""
    path = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        for i in range(n):
            t = i / n
            path.append(_skin(y0 + (y1 - y0) * t, x0 + (x1 - x0) * t))
    path.append(_skin(pts[-1][1], pts[-1][0]))
    part.tube(path, r, seg=4)


def _saw(x0, x1, y, teeth, depth):
    """A sawtooth edge across the body from x0 to x1 at y, `teeth` teeth `depth` deep (towards +Y)."""
    pts = []
    for k in range(teeth * 2 + 1):
        pts.append((x0 + (x1 - x0) * k / (teeth * 2), y + (depth if k % 2 else 0.0)))
    return pts


def _wing_top(s, u):
    """A point on the diamond wing's upper face at span s (from the root, x = s) and chord share u."""
    stations = [(2.0, -2.4, 6.6, .26), (6.3, 1.47, 1.3, .07)]
    (s0, le0, c0, t0), (s1, le1, c1, t1) = stations
    k = max(0.0, min(1.0, (s - s0) / (s1 - s0)))
    le, c, t = le0 + (le1 - le0) * k, c0 + (c1 - c0) * k, t0 + (t1 - t0) * k
    n = t / 2 * (u / .42 if u <= .42 else (1 - u) / .58)
    return (s, le + c * u, -.12 - (s - 2.0) * .02 + n + .01)


def stealth_fighter(a):
    """Faceted stealth fighter (F-22 / Su-57 lineage), 19 x 12.7 m: prompt 17's airframe, bays and cannon, with
    the middle of the body detailed (see the module notes)."""
    mb_p17_temp.stealth_fighter(a)
    lines = a.part('Panel_lines', 'Undercarriage')
    edges = a.part('Detail_edges', 'Armor', flat=True)
    dark = a.part('Detail_dark', 'Undercarriage')
    glass = a.part('Detail_glass', 'Glass')
    steel = a.part('Detail_steel', 'Steel')
    # Canopy: sill frames along both sides, a bow frame behind the windscreen, the aft frame, a HUD inside.
    st = [(-7.7, .1), (-7.0, .36), (-6.0, .44), (-5.0, .4), (-4.1, .24), (-3.6, .1)]
    for sg in (-1, 1):
        a.part('Canopy_frames', 'Armor').tube([_skin(y, sg * w, .02) for y, w in st], .03, seg=5)
    zc = lambda y: _hex_top(SF, y, 0) - .06
    bow = [(math.cos(t) * .43, -6.55, zc(-6.55) + .44 * math.sin(t) ** 1.15 + .05) for t in
           [k * math.pi / 8 for k in range(9)]]
    a.part('Canopy_frames', 'Armor').tube(bow, .035, seg=5)
    aft = [(math.cos(t) * .26, -4.05, zc(-4.05) + .72 * math.sin(t) ** 1.2 - .02) for t in
           [k * math.pi / 8 for k in range(9)]]
    a.part('Canopy_frames', 'Armor').tube(aft, .03, seg=5)
    glass.box((.16, .02, .12), loc=(0, -6.35, zc(-6.35) + .52), rot=(-.5, 0, 0), bevel=0)
    a.part('Seat', 'Rubber').box((.34, .3, .5), loc=(0, -5.2, zc(-5.2) + .48), rot=(.25, 0, 0), bevel=.04, seg=1)
    # Caret intake lips: a thin frame round each mouth, the bump ahead of it on the body, a deep dark duct.
    for sg in (-1, 1):
        y = -4.83
        edges.box((.06, .06, .52), loc=(sg * .69, y, -.39), bevel=0)                                  # inner lip
        edges.box((.06, .06, .5), loc=(sg * 1.52, y, -.39), rot=(0, sg * -.2, 0), bevel=0)             # outer lip
        edges.box((.86, .06, .05), loc=(sg * 1.11, y, -.14), bevel=0)                                 # top lip
        edges.box((.86, .06, .05), loc=(sg * 1.11, y, -.64), bevel=0)                                 # bottom lip
        dark.box((.7, .5, .38), loc=(sg * 1.11, -4.55, -.39), bevel=0)                                # duct
        edges.sphere((.16, .9, .2), loc=(sg * .62, -5.4, -.36), seg=10, rings=6)                     # bump
    # Dorsal spine between the intakes and the fins: a raised panel with a sawtooth access door, the
    # refuelling receptacle, the APU vent, blade antennas and sensor windows.
    spine = a.part('Spine', 'Armor', flat=True)
    y0, y1 = -3.4, 3.6
    rings = []
    for y in (y0, -2.0, 1.5, y1):
        w = .5 if y in (-2.0, 1.5) else .3
        z = _hex_top(SF, y, 0)
        h = .1 if y in (-2.0, 1.5) else .01
        rings.append([(-w, y, z - .01), (-w * .7, y, z + h), (w * .7, y, z + h), (w, y, z - .01)])
    spine.loft(rings, bevel=0)
    _panel_line(lines, _saw(-.55, .55, -1.2, 3, .22) + [(.55, .9)] + list(reversed(_saw(-.55, .55, .9, 3, -.22))) +
                [(-.55, -1.2)], r=.011)
    dark.box((.34, .5, .02), loc=(0, -2.6, _hex_top(SF, -2.6, 0) + .1), bevel=0)                     # refuel door
    steel.box((.26, .12, .03), loc=(.6, 2.4, _hex_top(SF, 2.4, .6) + .02), bevel=0)                  # APU vent
    for y, z in ((-1.6, 1), (3.0, 1), (-.8, -1)):
        zz = (_hex_top(SF, y, 0) + .08) if z > 0 else -.62
        a.part('Antennas', 'Armor').box((.02, .34, .14), loc=(0, y, zz), rot=(-.3 * z, 0, 0), bevel=0, taper=(1, .45))
    for sg in (-1, 1):
        glass.box((.02, .22, .12), loc=(sg * 1.02, -6.4, -.02), rot=(0, 0, sg * -.35), bevel=0)      # EODAS cheeks
        steel.cyl(.012, .5, loc=(sg * .26, -8.3, -.12), rot=(R90 + .05, 0, sg * .08), seg=5, bevel=0)  # air data
    glass.box((.16, .16, .02), loc=(0, -2.3, -.62), bevel=0)                                          # belly window
    # Sawtooth panel lines along the body: the nose join, the chine seams, the wing roots and the tail.
    _panel_line(lines, _saw(-.95, .95, -6.9, 4, .25))
    _panel_line(lines, _saw(-1.9, 1.9, -3.3, 6, .3))
    _panel_line(lines, _saw(-1.6, 1.6, 5.2, 5, -.3))
    for sg in (-1, 1):
        _panel_line(lines, [(sg * .3, -8.6), (sg * .5, -7.0), (sg * .75, -5.2), (sg * .9, -3.4), (sg * .95, 4.8)])
        _panel_line(lines, [(sg * 1.5, -3.0), (sg * 2.0, -1.0), (sg * 2.05, 2.8)])
        _panel_line(lines, [(sg * 1.2, 5.2), (sg * 1.05, 7.4)])
    # The bays' seams on the belly: door outlines round the two main bays and the centre bay.
    for (x, y, w, l) in ((.35, -1.2, .56, 3.7), (-.35, -1.2, .56, 3.7), (0, 2.1, .74, 2.5)):
        for dy in (-l / 2, l / 2):
            lines.box((w, .03, .02), loc=(x, y + dy, -.585), bevel=0)
        for dx in (-w / 2, w / 2):
            lines.box((.03, l, .02), loc=(x + dx, y, -.585), bevel=0)
    # Hinge lines on the wings (flaperons and ailerons) and on the stabilisers.
    for sg in (-1, 1):
        for u, s0, s1 in ((.8, 2.4, 4.5), (.7, 4.6, 6.0)):
            pts = [_wing_top(s, u + (s - s0) * .015) for s in (s0, (s0 + s1) / 2, s1)]
            lines.tube([(sg * x, y, z) for x, y, z in pts], .012, seg=4)
        pts = [_wing_top(s, .5) for s in (2.4, 3.5, 4.6, 5.8)]
        lines.tube([(sg * x, y, z + .005) for x, y, z in pts], .01, seg=4)                            # spar line


# name: (builder, Asset options).
BUILDERS = {
    'fpv_drone': (fpv_drone, dict(ao_distance=.08, ground=False)),
    'bunker_vehicle': (bunker_vehicle, dict(ao_distance=.7, grime_height=.6)),
    'sky_gunship': (sky_gunship, dict(ao_distance=.9, ground=False)),
    'transport_plane': (functools.partial(sky_gunship, armed=False), dict(ao_distance=.9, ground=False)),
    'stealth_fighter': (stealth_fighter, dict(ao_distance=.7, ground=False)),
}
