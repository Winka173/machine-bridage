"""Full fix pass 8, lead pass (DECISIONS "Sửa lỗi tổng hợp L8 (lead pass, 2026-10-02)"): the worst "Kém" models of the
model scan (Docs/models/scan/visual_scores.md) rebuilt on the V2 kit (mb_kit27 + mb_parts27), merged last in
build_assets.all_builders() so these builders win. The wrappers that run after every builder (mb_p34_barrels,
mb_fix_barrels, mb_p34_parts, mb_flare_mounts) still apply.

Every runtime node of the model it replaces is kept at the same place (Turret, Radar, Muzzle_*, Mount_*, Point_*,
the recoiling Main_cannon / Muzzle_brake meshes and the turret part names); new: Mount_aam + Muzzle_aam on
interceptor_drone_vehicle (its free-aimed Coyote secondary) and Mount_APS on laser_ad_station (its def has `aps`).
The scan's named roles are covered (axles, glass, stowage on the trucks; base, walls, roof, antenna on the statics).

Statics: fire_control_centre, flare_tower, laser_ad_station, visual_jammer, radar_site, troop_shelter, repair_bay,
heavy_flak_tower. Vehicles: sp_mortar, wheeled_howitzer, recoilless_jeep, radar_scout, interceptor_drone_vehicle,
microwave_vehicle, nlos_atgm_vehicle.

Conventions are frontier_kit's: metres, +Z up, Blender -Y is the front.
"""
import math
import random

import mb_detail as hd
import mb_kit27 as k
import mb_parts27 as parts
import mb_siege
from frontier_kit import chamfered
from mb_p25_models2 import _lights
from mb_towers3 import _dish_at, _runtime_names

R90 = math.pi / 2
TAU = math.tau
FORWARD = (R90, 0, 0)


# ============================================================================= shared statics
def _slab(a, name, mat, w, d, h, z=0.0, cut=.3, c=.03, loc=(0, 0)):
    """A chamfered-corner slab standing on z."""
    k.extrude(a.part(name, mat), chamfered(w, d, cut), h, loc=(loc[0], loc[1], z + h / 2), axis='Z', chamfer=c,
              corner=.02)


def _panels(shape, sel=None, width=.09, depth=-.014):
    """Recessed panels on the upright faces of a block (not its chamfer facets)."""
    k.inset(shape, lambda c, n, f: (abs(n.x) > .95 or abs(n.y) > .95) and (sel is None or sel(c, n)),
            width=width, depth=depth)


def _bag_line(part, p0, p1, z0, courses=2, bag=(.62, .34, .17), rng=None):
    """A straight sandbag wall from p0 to p1 (x, y), `courses` high, every other course staggered by half a bag;
    each bag a chamfered block slightly turned and squashed so the wall does not read as one slab."""
    rng = rng or random.Random(7)
    x0, y0 = p0
    x1, y1 = p1
    L = math.hypot(x1 - x0, y1 - y0)
    yaw = math.atan2(y1 - y0, x1 - x0)
    n = max(1, round(L / (bag[0] * .95)))
    step = L / n
    for c in range(courses):
        off = .5 * step if c % 2 else 0.0
        count = n if c % 2 == 0 else n - 1
        for i in range(count):
            t = (i + .5) * step + off
            x, y = x0 + math.cos(yaw) * t, y0 + math.sin(yaw) * t
            sq = rng.uniform(.9, 1.0)
            k.block(part, (step * .98, bag[1] * (1.06 - .06 * c), bag[2] * sq),
                    loc=(x, y, z0 + c * bag[2] * .92), rot=(0, 0, yaw + rng.uniform(-.05, .05)), chamfer=.055,
                    taper=(.9, .86), ends=(True, True))


def _bag_ring(part, centre, r, z0, courses=2, gap=None, n=None, bag_h=.17, depth=.36):
    """A ring of sandbags round centre (open to the rear, +Y, over `gap` radians when given)."""
    cx, cy = centre
    n = n or max(8, round(TAU * r / .6))
    rng = random.Random(int(r * 100))
    for c in range(courses):
        off = (.5 if c % 2 else 0.0) * TAU / n
        for i in range(n):
            ang = i * TAU / n + off
            if gap and abs(math.atan2(math.sin(ang - R90), math.cos(ang - R90))) < gap / 2:
                continue
            x, y = cx + r * math.cos(ang), cy + r * math.sin(ang)
            k.block(part, (depth * (1.04 - .05 * c), TAU * r / n * .97, bag_h * rng.uniform(.9, 1.0)),
                    loc=(x, y, z0 + c * bag_h * .92), rot=(0, 0, ang), chamfer=.05, taper=(.86, .92),
                    ends=(True, True))


def _crate(a, loc, size=(.9, .5, .4), yaw=0.0, name='Ammo_boxes', mat='Crate'):
    w, d, h = size
    b = a.part(name, mat)
    k.block(b, (w, d, h), loc=(loc[0], loc[1], loc[2] + 0), rot=(0, 0, yaw), chamfer=.035, ends=(True, True))
    c, s = math.cos(yaw), math.sin(yaw)
    band = a.part('Crate_bands', 'Hazard')
    band.box((w * .2, d + .02, .05), loc=(loc[0] + c * w * .28, loc[1] + s * w * .28, loc[2] + h * .65),
             rot=(0, 0, yaw), bevel=0)


def _drum(a, loc, r=.29, h=.88, name='Fuel_drums', mat='BarrelRed'):
    k.lathe(a.part(name, mat), [(0, 0), (r * .96, 0), (r, .03), (r, h * .3), (r * 1.03, h * .32), (r, h * .34),
                                (r, h * .66), (r * 1.03, h * .68), (r, h * .7), (r, h - .03), (r * .96, h), (0, h)],
            loc=loc, seg=12, worn=(3, 7))


def _generator(a, loc, yaw=0.0, size=(1.5, .9, .95)):
    """A skid-mounted generator set: a chamfered canopy with louvre panels on a dark skid, an exhaust stub."""
    x, y, z = loc
    w, d, h = size
    c, s = math.cos(yaw), math.sin(yaw)
    k.block(a.part('Generator_skid', 'Undercarriage'), (w + .1, d + .1, .12), loc=(x, y, z), rot=(0, 0, yaw),
            chamfer=.02)
    g = a.part('Generator', 'Armor')
    k.block(g, (w, d, h), loc=(x, y, z + .12), rot=(0, 0, yaw), chamfer=.06, ends=(False, True))
    _panels(g, width=.07, depth=-.012)
    a.part('Generator_vents', 'Undercarriage').grille(w * .5, h * .45, loc=(x + s * (d / 2 + .01), y - c * (d / 2 + .01),
                                                                        z + .12 + h * .5),
                                                     rot=(0, 0, yaw), slats=4, depth=.04, thickness=.035)
    k.lathe(a.part('Generator_stack', 'Steel'), [(.06, 0), (.06, .3), (.08, .32), (.08, .36)],
            loc=(x + c * w * .3, y + s * w * .3, z + .12 + h), seg=8)


def _container(a, name, mat, loc, size, yaw=0.0, doors=True, ribs=True):
    """An ISO-style shelter: a chamfered box with corrugation ribs on the long sides and a door pair on one end."""
    x, y, z = loc
    w, d, h = size
    box = a.part(name, mat)
    k.block(box, (w, d, h), loc=(x, y, z), rot=(0, 0, yaw), chamfer=.05, ends=(True, True))
    c, s = math.cos(yaw), math.sin(yaw)
    if ribs:
        rib = a.part(f'{name}_ribs', mat)
        n = max(3, int(w / .45))
        for side in (-1, 1):
            for i in range(n):
                u = -w / 2 + (i + .5) * w / n
                px, py = x + c * u - s * side * (d / 2 + .02), y + s * u + c * side * (d / 2 + .02)
                rib.box((.12, .04, h * .84), loc=(px, py, z + h / 2), rot=(0, 0, yaw), bevel=0)
    if doors:
        dr = a.part(f'{name}_doors', 'Armor')
        px, py = x + c * (w / 2 + .02), y + s * (w / 2 + .02)
        dr.box((.04, d * .86, h * .86), loc=(px, py, z + h / 2), rot=(0, 0, yaw), bevel=0)
        st = a.part('Steel', 'Steel')
        for u in (-.2, .2):
            st.box((.06, .05, h * .8), loc=(px + c * .03 - s * u * d, py + s * .03 + c * u * d, z + h / 2),
                   rot=(0, 0, yaw), bevel=0)


def _ladder(part, x, y, z0, z1, along=0.0, width=.44, step=.32):
    c, s = math.cos(along), math.sin(along)
    for side in (-1, 1):
        part.box((.05, .05, z1 - z0), loc=(x + side * c * width / 2, y + side * s * width / 2, (z0 + z1) / 2),
                 rot=(0, 0, along), bevel=0)
    n = max(1, int((z1 - z0 - .2) / step))
    for i in range(n):
        part.box((width, .035, .035), loc=(x, y, z0 + .25 + i * step), rot=(0, 0, along), bevel=0)


def _railing(part, pts, h=.9, post=.05, every=1.2):
    from mathutils import Vector
    P = [Vector(p) for p in pts]
    for p, q in zip(P, P[1:]):
        n = max(1, round((q - p).length / every))
        for i in range(n + (1 if q is P[-1] else 0)):
            c = p + (q - p) * (i / n)
            part.box((post, post, h), loc=(c.x, c.y, c.z + h / 2), bevel=0)
    for z in (h * .5, h):
        part.tube([(p.x, p.y, p.z + z) for p in P], .025, seg=4, caps=False)


def _camo(a, x0, x1, y0, y1, z, sag=.25, seed=1.0, cells=(10, 8)):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hx, hy = (x1 - x0) / 2, (y1 - y0) / 2

    def height(x, y):
        u, v = (x - cx) / hx, (y - cy) / hy
        return z - sag * max(abs(u), abs(v)) ** 2
    mb_siege.camo_net(a, random.Random(int(seed * 10)), x0, x1, y0, y1, height, cells=cells, garnish=14,
                      keep=lambda x, y: (x - cx) ** 2 / hx ** 2 + (y - cy) ** 2 / hy ** 2 < 1.15, seed=seed)


def _box_front(loc, size, pitch):
    """A k.block standing at loc, tilted up by pitch (rot (-pitch, 0, 0)): its front-face centre, the face's up and its
    outward normal."""
    w, d, h = size
    c, s = math.cos(pitch), math.sin(pitch)
    up = (0, s, c)
    out = (0, -c, s)
    centre = (loc[0], loc[1] + up[1] * h / 2, loc[2] + up[2] * h / 2)
    front = (centre[0], centre[1] + out[1] * d / 2, centre[2] + out[2] * d / 2)
    return front, up, out


def _cells(a, parent, loc, size, pitch, grid, pitch_xy, r, rim_name, cap_name, rim_mat='Steel', cap_mat='Undercarriage'):
    """Ringed cell mouths (a rim and a dark cap each) in a grid on the front of a tilted launcher box."""
    front, up, out = _box_front(loc, size, pitch)
    rims = a.part(rim_name, rim_mat, parent)
    caps = a.part(cap_name, cap_mat, parent)
    nx, nu = grid
    px, pu = pitch_xy
    for i in range(nx):
        for j in range(nu):
            x = (i - (nx - 1) / 2) * px
            u = (j - (nu - 1) / 2) * pu
            c = (front[0] + x, front[1] + up[1] * u + out[1] * .005, front[2] + up[2] * u + out[2] * .005)
            k.lathe(rims, [(r, 0), (r * 1.25, 0), (r * 1.25, .04), (r, .04)], loc=c, rot=(R90 - pitch, 0, 0), seg=10)
            caps.cyl(r, .02, loc=c, rot=(R90 - pitch, 0, 0), seg=10, bevel=0)
    return front


# ============================================================================= heavy flak tower (8.8 cm FlaK)
def heavy_flak_tower(a):
    """A dug-in 88 mm flak position: an octagonal cast-concrete emplacement with a staggered sandbag parapet, ammunition
    niches and a cruciform platform; the gun on its pedestal with a cradle, recuperator cylinders, a sloped shield and
    the long barrel with its brake (`Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main` as before), a rangefinder
    and an aerial."""
    _slab(a, 'Base', 'Concrete', 7.0, 6.0, .28, cut=1.3, c=.05)
    k.extrude(a.part('Emplacement', 'Plaster'), chamfered(5.6, 5.2, 1.4), .22, loc=(0, 0, .39), axis='Z', chamfer=.04,
              corner=.03)
    bags = a.part('Sandbags', 'Sandbag')
    _bag_ring(bags, (0, 0), 2.75, .3, courses=3, gap=1.0, n=26)
    revet = a.part('Revetment', 'Wood')
    for i in range(10):
        ang = (i + .5) * TAU / 12 + R90 + .45
        revet.box((.1, .1, .62), loc=(2.48 * math.cos(ang), 2.48 * math.sin(ang), .6), rot=(0, 0, ang), bevel=0)
    for ang in (.5, 1.35, 3.6, 4.4):
        _crate(a, (2.1 * math.cos(ang), 2.1 * math.sin(ang), .5), size=(.7, .38, .32), yaw=ang + R90)
    shells = a.part('Shells', 'Alloy')
    for j in range(5):
        k.lathe(shells, [(0, 0), (.05, 0), (.05, .5), (.03, .62), (0, .66)], loc=(-1.9 + j * .13, 1.5, .5), seg=8)
    plat = a.part('Platform', 'Armor')
    for yaw in (0, R90):
        k.block(plat, (3.6, .34, .2), loc=(0, 0, .5), rot=(0, 0, yaw), chamfer=.03)
        for s in (-1, 1):
            k.lathe(a.part('Jacks', 'Steel'), [(.16, 0), (.16, .06), (.06, .1), (.06, .3)],
                    loc=(s * 1.75 * math.cos(yaw), s * 1.75 * math.sin(yaw), .3), seg=8)
    t = a.pivot('Turret', (0, 0, .45))
    k.lathe(a.part('Pedestal', 'Armor', t), [(.62, .25), (.62, .32), (.46, .38), (.4, .75), (.5, .8), (.5, .88)],
            seg=14, worn=(1, 4))
    car = a.part('Carriage', 'Team', t)
    for s in (-1, 1):
        k.extrude(car, [(-.55, .85), (.75, .85), (.55, 1.25), (-.15, 1.35), (-.55, 1.1)], .12,
                  loc=(s * .32, 0, 0), axis='X', chamfer=.02, corner=.02)
    k.lathe(a.part('Trunnions', 'Steel', t), [(0, -.42), (.1, -.42), (.1, .42), (0, .42)], loc=(0, 0, 1.12),
            rot=(0, R90, 0), seg=10)
    shield = a.part('Gun_shield', 'Team', t)
    k.extrude(shield, [(-.95, 0), (.95, 0), (.82, 1.05), (-.82, 1.05)], .06, loc=(0, -.75, .82), rot=(-.25 + R90, 0, 0),
              axis='Z', chamfer=.015, corner=.03)
    for s in (-1, 1):
        k.extrude(shield, [(0, 0), (.55, 0), (.45, .9), (0, .9)], .05, loc=(s * .96, -.55, .82),
                  rot=(R90 - .25, 0, s * (R90 - .35)), axis='Z', chamfer=.012)
    pitch = math.atan2(3.21 - .9, 3.7)
    L = math.hypot(3.7, 3.21 - .9) - .3
    parts.barrel(a, 'Main_cannon', t, 0, 0, .9, L, .085, seg=12, sleeve=1.3, extractor=(.1, 1.9, .9),
                 brake_name='Muzzle_brake', brake='baffle', rot=(R90 - pitch, 0, 0))
    cyl = a.part('Recuperators', 'Steel', t)
    for dz in (.2, ):
        c, s = math.cos(pitch), math.sin(pitch)
        k.lathe(cyl, [(0, 0), (.09, 0), (.09, 1.6), (.07, 1.66), (0, 1.66)], loc=(0, .35 * c - 0, .9 + dz),
                rot=(R90 - pitch, 0, 0), seg=10)
    a.part('Breech', 'Armor', t).box((.36, .8, .36), loc=(0, .4 * math.cos(pitch), .9 - .4 * math.sin(pitch)),
                                      rot=(-pitch, 0, 0), bevel=.03, seg=1)
    k.block(a.part('Sight_box', 'Armor', t), (.22, .3, .26), loc=(-.5, -.35, 1.3), chamfer=.03)
    a.pivot('Muzzle_main', (0, -3.7, 3.21), t)
    ant = a.part('Antenna', 'Steel')
    parts.antenna(ant, (2.3, 1.9, .5), h=1.6, r=.05)
    k.lathe(ant, [(.06, 0), (.06, .9)], loc=(-2.0, 2.0, .5), seg=6)
    k.lathe(a.part('Rangefinder', 'Armor'), [(0, -.7), (.07, -.7), (.07, .7), (0, .7)], loc=(-2.0, 2.0, 1.45),
            rot=(0, R90, 0), seg=8)
    k.clean(a)


# ============================================================================= flare tower
def flare_tower(a):
    """An illumination-flare post: four braced steel legs on concrete footings, a plank deck with a sandbag parapet and
    a ladder, a canvas sun roof on posts, ready-use flare crates and an aerial; the flare-mortar rack (eight tubes on a
    trunnion yoke) turns as `Turret` with `Muzzle_main` where it was."""
    feet = a.part('Footing', 'Concrete')
    legs = a.part('Legs', 'Armor')
    braces = a.part('Braces', 'Steel')
    h0, h1, hw0, hw1 = .25, 2.9, 1.45, 1.15
    for sx in (-1, 1):
        for sy in (-1, 1):
            k.block(feet, (.55, .55, .25), loc=(sx * hw0, sy * hw0, 0), chamfer=.04)
            legs.limb((sx * hw0, sy * hw0, h0), (sx * hw1, sy * hw1, h1), .16, .16, bevel=.02)
    for z0, z1 in ((h0 + .1, 1.6), (1.6, h1 - .1)):
        f0 = hw0 + (hw1 - hw0) * (z0 - h0) / (h1 - h0)
        f1 = hw0 + (hw1 - hw0) * (z1 - h0) / (h1 - h0)
        for s in (-1, 1):
            braces.limb((-f0, s * f0, z0), (f1, s * f1, z1), .06, .06, bevel=0)
            braces.limb((s * f0, -f0, z0), (s * f1, f1, z1), .06, .06, bevel=0)
        for s in (-1, 1):
            braces.limb((-f1, s * f1, z1), (f1, s * f1, z1), .08, .08, bevel=0)
            braces.limb((s * f1, -f1, z1), (s * f1, f1, z1), .08, .08, bevel=0)
    deck = a.part('Deck', 'Wood')
    k.block(a.part('Deck_frame', 'Armor'), (3.0, 3.0, .14), loc=(0, 0, h1), chamfer=.03)
    for i in range(9):
        deck.box((3.1, .31, .05), loc=(0, -1.4 + i * .35, h1 + .165), bevel=.01, seg=1)
    bags = a.part('Sandbags', 'Sandbag')
    z = h1 + .19
    _bag_line(bags, (-1.4, 1.35), (1.4, 1.35), z, courses=2, bag=(.58, .3, .16))
    for s in (-1, 1):
        _bag_line(bags, (s * 1.35, 1.0), (s * 1.35, -.9), z, courses=2, bag=(.58, .3, .16))
    _bag_line(bags, (-1.4, -1.35), (-.55, -1.35), z, courses=2, bag=(.58, .3, .16))
    _bag_line(bags, (.55, -1.35), (1.4, -1.35), z, courses=2, bag=(.58, .3, .16))
    rail = a.part('Railing', 'Steel')
    _ladder(rail, 1.15, -1.5, 0, h1 + .2, along=0.0)
    posts = a.part('Roof_posts', 'Wood')
    for sx in (-1, 1):
        for sy in (-1, 1):
            posts.box((.09, .09, 1.6), loc=(sx * 1.3, sy * 1.3, h1 + 1.0), bevel=0)
    k.extrude(a.part('Roof', 'Canvas'), [(-1.55, 0), (1.55, 0), (1.55, .06), (0, .32), (-1.55, .06)], 3.1,
              loc=(0, 0, h1 + 1.78), axis='Y', chamfer=0, corner=.02)
    for x in (-1.0, -.45):
        _crate(a, (x, .85, z), size=(.48, .34, .3), yaw=0.0)
    parts.antenna(a.part('Antenna', 'Steel'), (-1.25, -1.25, h1 + .2), h=1.5, r=.045)
    t = a.pivot('Turret', (0, 0, 3.2))
    k.lathe(a.part('Ring', 'Steel', t), [(.42, 0), (.42, .06), (.3, .09), (.16, .12), (.16, .42)], seg=12, worn=(1,))
    yoke = a.part('Yoke', 'Armor', t)
    for s in (-1, 1):
        k.block(yoke, (.08, .34, .5), loc=(s * .42, 0, .42), chamfer=.02)
    pitch = math.radians(55)
    rack = a.part('Launcher', 'Team', t)
    c, s = math.cos(pitch), math.sin(pitch)
    base = (0, -.2 + .55 * c, 1.0 - .55 * s)
    k.block(rack, (.72, .4, .5), loc=base, rot=(R90 - pitch, 0, 0), chamfer=.04, ends=(True, True))
    tubes = a.part('Tubes', 'Undercarriage', t)
    for i in range(4):
        for j in range(2):
            x = -.27 + i * .18
            u = -.1 + j * .2
            k.lathe(tubes, [(.06, -.5), (.065, 0), (.08, .02), (.08, .06), (.05, .06), (.05, .04), (0, .04)],
                    loc=(x, -.2 + u * s, 1.0 + u * c), rot=(R90 - pitch, 0, 0), seg=8)
    a.pivot('Muzzle_main', (0, -.24, 1.09), t)
    k.clean(a)


# ============================================================================= laser air-defence station
def laser_ad_station(a):
    """An Iron Beam-type laser battery (6 m long, 4 m wide, as the def's modelSize): a cast slab with T-wall blast
    panels down the right flank and across the rear, a ribbed equipment shelter with cooling units, a generator and a
    cable trough, a search-radar panel on a mast; the beam director (yoke, a long cylindrical telescope with a large
    glazed aperture and fin rings) turns as `Turret` with `Muzzle_main` where it was; `Mount_APS` on the shelter roof
    (its def has `aps`)."""
    _slab(a, 'Base', 'Concrete', 4.0, 6.0, .22, cut=.4, c=.04)
    _slab(a, 'Pad', 'Plaster', 2.2, 2.2, .2, z=.22, cut=.5, c=.03, loc=(0, -1.0))
    wall = a.part('Wall', 'Concrete')
    for i in range(6):
        y = -2.4 + i * .8
        k.extrude(wall, [(-.16, 0), (.16, 0), (.1, 1.5), (-.1, 1.5)], .76, loc=(1.8, y, .22), axis='Y',
                  chamfer=.02, corner=.01)
    for i in range(4):
        x = -1.2 + i * .8
        k.extrude(wall, [(-.18, 0), (.18, 0), (.12, 1.7), (.06, 2.0), (-.06, 2.0), (-.12, 1.7)], .76,
                  loc=(x, 2.78, .22), axis='Y', rot=(0, 0, R90), chamfer=.02, corner=.01)
    _container(a, 'Shelter', 'Team', (.6, 1.5, .22), (2.5, 1.9, 2.0), yaw=R90)
    k.block(a.part('Roof', 'Medical'), (2.0, 2.6, .08), loc=(.6, 1.5, 2.22), chamfer=.02)
    cool = a.part('Coolers', 'Armor')
    for y in (2.2, 1.3):
        k.block(cool, (.8, .7, .35), loc=(.75, y, 2.3), chamfer=.04)
        a.part('Cooler_fans', 'Undercarriage').cyl(.26, .03, loc=(.75, y, 2.66), seg=12, bevel=0)
    a.pivot('Mount_APS', (1.2, .55, 2.55))
    k.lathe(a.part('APS_sensor', 'Glass'), [(0, 0), (.16, 0), (.16, .12), (.1, .22), (0, .24)], loc=(1.2, .55, 2.3),
            seg=10)
    _generator(a, (-1.0, 1.6, .22), yaw=R90, size=(1.4, .8, .9))
    a.part('Cable_trough', 'Undercarriage').box((.25, 1.6, .1), loc=(.45, -.3, .27), bevel=0)
    mast = a.part('Mast', 'Steel')
    k.lathe(mast, [(.1, 0), (.1, 2.8), (.07, 2.85), (.07, 3.4)], loc=(1.4, -2.5, .22), seg=8)
    pan = a.part('Search_panel', 'Armor')
    pan.box((1.0, .14, .8), loc=(1.4, -2.56, 3.72), rot=(-.3, 0, 0), bevel=.03, seg=1)
    a.part('Panel_face', 'Undercarriage').box((.88, .02, .68), loc=(1.4, -2.65, 3.75), rot=(-.3, 0, 0), bevel=0)
    t = a.pivot('Turret', (0, -1.0, 2.42))
    k.lathe(a.part('Pedestal', 'Armor'), [(.7, 0), (.7, .1), (.5, .16), (.42, 1.8), (.55, 1.86), (.55, 2.0)],
            loc=(0, -1.0, .42), seg=14, worn=(1, 4))
    yoke = a.part('Yoke', 'Team', t)
    k.lathe(yoke, [(.6, 0), (.6, .1), (.5, .16), (0, .16)], seg=14)
    for s in (-1, 1):
        k.extrude(yoke, [(-.35, .1), (.35, .1), (.25, 1.0), (-.25, 1.0)], .14, loc=(s * .62, 0, 0), axis='X',
                  chamfer=.02, corner=.03)
    d = a.part('Director', 'Armor', t)
    k.lathe(d, [(0, -.75), (.34, -.75), (.42, -.6), (.42, .55), (.48, .62), (.48, .9), (.4, .98), (0, .98)],
            loc=(0, 0, .75), rot=FORWARD, seg=16, worn=(2, 5))
    fins = a.part('Fins', 'Steel', t)
    for yy in (.1, .25, .4):
        k.lathe(fins, [(.42, -.03), (.52, -.03), (.52, .03), (.42, .03)], loc=(0, yy, .75), rot=FORWARD, seg=16)
    a.part('Aperture', 'Energy', t).cyl(.36, .03, loc=(0, -.99, .75), rot=FORWARD, seg=16, bevel=0)
    k.block(a.part('Sensor_pod', 'Armor', t), (.3, .4, .3), loc=(.62, -.2, 1.15), chamfer=.04)
    a.part('Sensor_lens', 'Glass', t).box((.2, .03, .18), loc=(.62, -.41, 1.15), bevel=0)
    a.pivot('Muzzle_main', (0, -.98, .75), t)
    k.clean(a)


# ============================================================================= visual jammer
def visual_jammer(a):
    """A dazzler / decoy-light post (6 m long, 5 m wide, as the def's modelSize): a cast pad, a ribbed control shelter
    with a railed roof deck and a sandbag blast wall in front, a tall braced mast carrying a floodlight head (lamp
    panels round a drum), smoke-generator drums on a rack, a generator, a camouflage net over the shelter's rear and
    aerials."""
    _slab(a, 'Base', 'Concrete', 5.0, 6.0, .2, cut=.5, c=.04)
    _container(a, 'Shelter', 'Team', (.9, 1.0, .2), (3.2, 2.0, 2.1), yaw=R90)
    k.block(a.part('Roof', 'Medical'), (2.1, 3.3, .1), loc=(.9, 1.0, 2.3), chamfer=.03)
    _railing(a.part('Railing', 'Steel'), [(1.85, -.55, 2.4), (-.05, -.55, 2.4), (-.05, 2.55, 2.4)], h=.6, every=1.0)
    _bag_line(a.part('Sandbags', 'Sandbag'), (-.3, -1.1), (2.3, -1.1), .2, courses=3, bag=(.62, .34, .17))
    mast = a.part('Mast', 'Armor')
    mb_siege.lattice(mast, -1.5, .9, .2, 5.4, .45, .2, 4, leg=.12, brace=.04)
    k.block(a.part('Mast_deck', 'Steel'), (.7, .7, .08), loc=(-1.5, .9, 5.4), chamfer=.02)
    k.lathe(a.part('Lamp_head', 'Armor'), [(0, 0), (.38, 0), (.38, .55), (.3, .62), (0, .62)], loc=(-1.5, .9, 5.5),
            seg=12, worn=(2,))
    lamps = a.part('Lamp_panels', 'Lamp')
    for i in range(6):
        ang = i * TAU / 6
        lamps.box((.03, .24, .32), loc=(-1.5 + .39 * math.cos(ang), .9 + .39 * math.sin(ang), 5.78),
                  rot=(0, 0, ang), bevel=0)
    for i in range(3):
        _drum(a, (-1.9 + i * .65, -2.3, .2), r=.27, h=.85, name='Smoke_drums', mat='Fuel')
    k.block(a.part('Drum_rack', 'Steel'), (2.1, .7, .06), loc=(-1.25, -2.3, .2), chamfer=0)
    _generator(a, (1.3, -2.3, .2), yaw=0.0, size=(1.3, .8, .85))
    ant = a.part('Antenna', 'Steel')
    parts.antenna(ant, (1.6, 2.4, 2.35), h=1.4, r=.04)
    parts.antenna(ant, (1.6, -.3, 2.35), h=1.0, r=.04)
    _camo(a, -.3, 2.3, 1.0, 3.0, 2.75, sag=.35, seed=3.0, cells=(7, 6))
    k.clean(a)


# ============================================================================= fire control centre
def fire_control_centre(a):
    """A dug-in fire-direction post: a cast pad, a sunken command bunker under sloped earth berms with a concrete front
    wall, embrasures and a roof slab with vents, a sandbagged entrance, a plotting shelter with antennas and a generator,
    a camouflage net; the search radar on its mast turns as `Radar` where it was."""
    _slab(a, 'Base', 'Concrete', 6.0, 6.0, .18, cut=.6, c=.03)
    k.extrude(a.part('Berm', 'Dirt'), [(-2.6, 0), (-1.6, 1.5), (1.6, 1.5), (2.6, 0)], 3.6, loc=(-.9, .5, .18),
              axis='X', chamfer=.1, corner=.15)
    bunker = a.part('Bunker', 'Concrete')
    k.block(bunker, (3.4, .4, 1.5), loc=(-.9, -1.75, .18), chamfer=.05)
    k.block(bunker, (.35, 1.0, 1.0), loc=(.95, -1.55, .18), chamfer=.04)
    _panels(bunker, lambda c, n: n.y < -.9, width=.12)
    a.part('Embrasures', 'Undercarriage').box((2.0, .05, .2), loc=(-1.0, -1.97, 1.25), bevel=0)
    k.block(a.part('Roof', 'Plaster'), (3.8, 3.75, .22), loc=(-.9, .2, 1.68), chamfer=.06)
    vents = a.part('Vents', 'Steel')
    for x in (-2.0, -.2):
        k.lathe(vents, [(.1, 0), (.1, .5), (.17, .52), (.17, .6), (0, .66)], loc=(x, 1.2, 1.9), seg=8)
    bags = a.part('Sandbags', 'Sandbag')
    _bag_line(bags, (1.25, -2.4), (2.7, -2.4), .18, courses=3)
    _bag_line(bags, (2.7, -2.2), (2.7, -.3), .18, courses=3)
    _container(a, 'Shelter', 'Team', (1.85, 1.35, .18), (2.0, 1.7, 1.9), yaw=R90)
    k.block(a.part('Roof_deck', 'Medical'), (1.8, 2.1, .08), loc=(1.85, 1.35, 2.08), chamfer=.02)
    ant = a.part('Antenna', 'Steel')
    parts.antenna(ant, (2.5, 2.1, 2.16), h=1.6, r=.045)
    parts.antenna(ant, (1.3, 2.1, 2.16), h=1.1, r=.04)
    _generator(a, (1.9, -1.2, .18), yaw=R90, size=(1.1, .7, .75))
    mast = a.part('Mast', 'Steel')
    k.lathe(mast, [(.18, 0), (.18, .1), (.1, .14), (.1, 2.95), (.14, 3.0), (.14, 3.1)], loc=(-1.3, -1.5, 1.9),
            seg=10, worn=(1, 4))
    r = a.pivot('Radar', (-1.3, -1.5, 5.2))
    k.lathe(a.part('Radar_drive', 'Armor', r), [(.2, -.2), (.2, .05), (.12, .1), (0, .1)], seg=10)
    arr = a.part('Radar_array', 'Team', r)
    arr.box((1.8, .16, .7), loc=(0, -.02, .45), rot=(-.25, 0, 0), bevel=.03, seg=1)
    a.part('Radar_face', 'Undercarriage', r).box((1.6, .02, .55), loc=(0, -.12, .47), rot=(-.25, 0, 0), bevel=0)
    _camo(a, -2.9, .9, -1.0, 2.5, 2.2, sag=.25, seed=5.0, cells=(10, 8))
    k.clean(a)


# ============================================================================= radar site
def radar_site(a):
    """A surveillance-radar post: a cast pad, a braced lattice tower with a railed platform carrying the rotating truss
    reflector (`Radar` where it was), an operations hut with a pitched roof, a sandbag blast wall, a fence run, a
    generator, fuel drums and aerials; `Point_fire` kept."""
    _slab(a, 'Base', 'Concrete', 7.9, 8.1, .2, cut=.8, c=.04)
    tower = a.part('Tower', 'Armor')
    mb_siege.lattice(tower, 1.4, .6, .2, 5.2, 1.0, .55, 4, leg=.14, brace=.05)
    k.block(a.part('Platform', 'Steel'), (1.7, 1.7, .12), loc=(1.4, .6, 5.2), chamfer=.03)
    rail = a.part('Railing', 'Steel')
    _railing(rail, [(.6, -.2, 5.32), (2.2, -.2, 5.32), (2.2, 1.4, 5.32), (.6, 1.4, 5.32), (.6, -.2, 5.32)], h=.7,
             every=.8)
    _ladder(rail, 1.4, -.45, .2, 5.2, along=0.0)
    r = a.pivot('Radar', (1.4, .6, 5.86))
    k.lathe(a.part('Radar_drive', 'Armor', r), [(.3, -.55), (.3, -.35), (.18, -.3), (.18, 0), (0, 0)], seg=12)
    dish = a.part('Radar_dish', 'Team', r)
    _dish_at(dish, (0, 0, .5), 0.0, 1.6, .7, depth=.35, seg=14, tilt=.2)
    truss = a.part('Radar_truss', 'Steel', r)
    for x in (-1.2, 0, 1.2):
        truss.limb((x, .25, .2), (0, .05, -.05), .05, .05, bevel=0)
    k.lathe(truss, [(.05, 0), (.05, .9), (.1, .92), (0, 1.0)], loc=(0, -.7, .5), rot=FORWARD, seg=6)
    hut = a.part('Shelter', 'Team')
    k.block(hut, (2.8, 2.2, 2.0), loc=(-2.0, -2.2, .2), chamfer=.05)
    _panels(hut, width=.1)
    k.extrude(a.part('Roof', 'RoofSlate'), [(-1.3, 0), (1.3, 0), (0, .55)], 3.1, loc=(-2.0, -2.2, 2.2), axis='X',
              chamfer=.03, corner=.02)
    win = a.part('Windows', 'Glass')
    for x in (-2.6, -1.4):
        win.box((.6, .04, .45), loc=(x, -3.31, 1.4), bevel=0)
    a.part('Door', 'Armor').box((.04, .9, 1.6), loc=(-.59, -2.2, 1.0), bevel=0)
    bags = a.part('Sandbags', 'Sandbag')
    _bag_line(bags, (-3.6, -.6), (-.4, -.6), .2, courses=3)
    fence = a.part('Fence', 'Steel')
    for i in range(7):
        y = -3.5 + i * 1.15
        fence.box((.07, .07, 1.3), loc=(3.7, y, .85), bevel=0)
    for z in (.7, 1.1, 1.45):
        fence.tube([(3.7, -3.5, z), (3.7, 3.4, z)], .015, seg=4, caps=False)
    _generator(a, (-2.4, 2.3, .2), yaw=0.0, size=(1.4, .85, .9))
    for i, (x, y) in enumerate(((-.6, 3.1), (-.05, 3.3), (-.4, 2.6))):
        _drum(a, (x, y, .2))
    ant = a.part('Antenna', 'Steel')
    parts.antenna(ant, (-3.2, -1.3, 2.2), h=1.8, r=.05)
    parts.antenna(ant, (-.8, -3.0, 2.2), h=1.2, r=.04)
    a.pivot('Point_fire', (-2, -2.4, 2.5))
    k.clean(a)


# ============================================================================= troop shelter
def troop_shelter(a):
    """A dug-in troop shelter: a cast footing ring, sloped earth berms round a corrugated arched roof (ribbed half
    tube, its ends in concrete), sandbagged entrance walls with steps down, vent pipes, a radio aerial, stowage and a
    camouflage net over one end."""
    _slab(a, 'Base', 'Concrete', 6.0, 5.0, .14, cut=.5, c=.03)
    k.extrude(a.part('Berm', 'Dirt'), [(-2.45, 0), (-1.5, 1.05), (1.5, 1.05), (2.45, 0)], 5.2, loc=(0, .1, .14),
              axis='X', chamfer=.12, corner=.15)
    roof = a.part('Roof', 'MetalSheet')
    n = 9
    prof = [(1.55 * math.cos(math.pi * i / n), .95 * math.sin(math.pi * i / n)) for i in range(n + 1)]
    outer = [(x, z + 1.0) for x, z in prof]
    inner = [(x * .93, z * .9 + 1.0) for x, z in reversed(prof)]
    k.extrude(roof, outer + inner, 4.2, loc=(0, .1, 0), axis='Y', chamfer=0)
    ribs = a.part('Roof_ribs', 'Steel')
    for i in range(7):
        y = -1.9 + i * .66
        ribs.tube([(1.57 * math.cos(math.pi * j / 8), y, 1.0 + .97 * math.sin(math.pi * j / 8)) for j in range(9)],
                  .035, seg=4, caps=False)
    ends = a.part('Coping', 'Concrete')
    for y in (-2.05, 2.25):
        k.extrude(ends, [(-1.75, 0), (1.75, 0), (1.75, 1.05), (0, 2.05), (-1.75, 1.05)], .22, loc=(0, y, .14),
                  axis='Y', chamfer=.03, corner=.02)
    a.part('Doorway', 'Undercarriage').box((.9, .05, 1.2), loc=(0, -2.17, .85), bevel=0)
    steps = a.part('Ramp', 'Concrete')
    for i in range(3):
        k.block(steps, (1.0, .32, .12 + i * .12), loc=(0, -2.85 + i * .3, .14), chamfer=.02)
    bags = a.part('Sandbags', 'Sandbag')
    for s in (-1, 1):
        _bag_line(bags, (s * .75, -2.4), (s * .75, -3.0), .14, courses=3, bag=(.6, .32, .17))
        _bag_line(bags, (s * .75, -2.3), (s * 2.6, -2.3), .14, courses=2, bag=(.6, .32, .17))
    vents = a.part('Vents', 'Steel')
    for x, y in ((-.7, .9), (.8, -.6)):
        k.lathe(vents, [(.08, 0), (.08, .55), (.14, .57), (.14, .65), (0, .7)], loc=(x, y, 1.85), seg=8)
    parts.antenna(a.part('Antenna', 'Steel'), (1.9, 1.9, .14), h=1.9, r=.04)
    for x, y, yaw in ((2.2, -1.5, .2), (-2.3, -1.1, -.3), (2.3, .6, 1.4)):
        _crate(a, (x, y, .14), size=(.7, .4, .32), yaw=yaw)
    _camo(a, -1.9, 1.9, .6, 2.7, 2.1, sag=.25, seed=7.0, cells=(8, 5))
    k.clean(a)


# ============================================================================= repair bay
def repair_bay(a):
    """A field workshop (14.5 m long, as before): a cast slab with a hazard-striped bay, a portal-frame shed down its
    length (steel columns, rafters, a pitched corrugated roof, a clad right wall and rear end with a roller door), an
    overhead gantry crane with a hoist over the open left bay, workbenches, tool chests, a wheel stack, fuel drums and
    an aerial; `Point_fire` kept."""
    _slab(a, 'Base', 'Concrete', 10.0, 14.5, .2, cut=.6, c=.04)
    haz = a.part('Hazard_stripes', 'Hazard')
    for i in range(8):
        haz.box((.5, .08, .02), loc=(-3.8, 1.0 - i * 1.0, .21), rot=(0, 0, .6 + R90), bevel=0)
    frame = a.part('Frame', 'Armor')
    ys = [6.6 - i * 2.2 for i in range(7)]
    for y in ys:
        for x in (-3.4, 3.4):
            k.block(frame, (.26, .26, 4.6), loc=(x, y, .2), chamfer=.03)
        frame.limb((-3.4, y, 4.8), (0, y, 6.0), .3, .22, bevel=.02)
        frame.limb((3.4, y, 4.8), (0, y, 6.0), .3, .22, bevel=.02)
    for x in (-3.4, 3.4):
        frame.box((.2, 13.4, .3), loc=(x, 0, 4.75), bevel=.02, seg=1)
    roof = a.part('Roof', 'MetalSheet')
    ang = math.atan2(1.2, 3.6)
    for s in (-1, 1):
        k.block(roof, (3.95, 14.0, .08), loc=(s * 1.85, 0, 5.43), rot=(0, s * ang, 0), chamfer=.02, ends=(True, True))
    k.block(a.part('Ridge', 'Steel'), (.3, 14.1, .1), loc=(0, 0, 6.02), chamfer=.02)
    clad = a.part('Wall', 'Team')
    k.block(clad, (.12, 13.4, 4.4), loc=(3.5, 0, .2), chamfer=.02)
    k.inset(clad, lambda c, n, f: n.x < -.9, width=.14, depth=-.014)
    k.block(clad, (6.9, .12, 4.4), loc=(0, 6.75, .2), chamfer=.02)
    k.inset(clad, lambda c, n, f: n.y < -.9 and c.y > 6.0, width=.14, depth=-.014)
    door = a.part('Roller_door', 'Steel')
    for i in range(10):
        door.box((3.2, .06, .3), loc=(-.2, -6.75, .5 + i * .38), bevel=.01, seg=1)
    k.block(a.part('Door_box', 'Armor'), (3.6, .4, .45), loc=(-.2, -6.75, 4.2), chamfer=.03)
    crane = a.part('Gantry', 'Hazard')
    for y in (-3.0, 3.0):
        for x in (-4.5, 2.6):
            k.block(crane, (.24, .24, 4.0), loc=(x, y, .2), chamfer=.02)
        crane.box((7.4, .26, .4), loc=(-.95, y, 4.35), bevel=.02, seg=1)
    crane.box((.34, 6.3, .45), loc=(-2.0, 0, 4.0), bevel=.02, seg=1)
    k.block(a.part('Hoist', 'Armor'), (.5, .5, .45), loc=(-2.0, -.8, 3.3), chamfer=.04)
    hook = a.part('Hook_chain', 'Steel')
    hook.tube([(-2.0, -.8, 3.3), (-2.0, -.8, 1.8)], .03, seg=4)
    hook.torus(.12, .03, loc=(-2.0, -.8, 1.7), rot=(0, R90, 0), seg=10, ring=4)
    bench = a.part('Workbench', 'Wood')
    for y in (4.6, -4.4):
        k.block(bench, (.7, 1.8, .1), loc=(2.8, y, .95), chamfer=.02)
        for dy in (-.8, .8):
            a.part('Steel', 'Steel').box((.6, .06, .8), loc=(2.8, y + dy, .6), bevel=0)
    chests = a.part('Tool_chests', 'BarrelRed')
    for y in (2.2, -1.6):
        k.block(chests, (.5, .8, 1.0), loc=(3.05, y, .2), chamfer=.04)
        k.inset(chests, lambda c, n, f, y=y: n.x < -.9 and abs(c.y - y) < .5, width=.05, depth=-.01)
    tyres = a.part('Tyres', 'Rubber')
    for j in range(3):
        k.lathe(tyres, [(.25, -.14), (.42, -.12), (.45, 0), (.42, .12), (.25, .14)], loc=(1.8, -5.6, .34 + j * .28),
                seg=12, caps=(False, False))
    for x, y in ((-3.0, -5.6), (-2.4, -6.0), (-2.5, -5.2)):
        _drum(a, (x, y, .2))
    parts.antenna(a.part('Antenna', 'Steel'), (3.4, -6.6, 4.9), h=1.6, r=.05)
    a.pivot('Point_fire', (2.6, 3.3, 2.1))
    k.clean(a)


# ============================================================================= wheeled chassis
def _chassis(a, L, W, axles, r, ys=None, frame_z=None):
    """Ladder frame, axle beams with differential housings, V2 wheels with hubs; returns the wheel y positions."""
    frame_z = frame_z or r + .08
    if ys is None:
        span = L - 1.9
        ys = [-L / 2 + 1.0 + span * i / max(1, axles - 1) for i in range(axles)]
    fr = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        fr.box((.16, L * .9, .26), loc=(s * W * .28, .1, frame_z), bevel=.02, seg=1)
    for y in ys:
        fr.box((W * .62, .12, .12), loc=(0, y, frame_z), bevel=0)
    ax = a.part('Axles', 'Undercarriage')
    for y in ys:
        ax.cyl(.07, W - .5, loc=(0, y, r), rot=(0, R90, 0), seg=8, bevel=0)
        k.lathe(ax, [(0, -.16), (.16, -.16), (.2, 0), (.16, .16), (0, .16)], loc=(0, y, r), rot=(0, R90, 0), seg=8)
    for s in (-1, 1):
        for y in ys:
            parts.road_wheel(a, (s * (W / 2 - .17), y, r), r, .34, s, seg=12)
    return ys


def _fenders(a, W, ys, r, z_top=None, mat='Armor'):
    """Wheel-arch fenders over each wheel (or wheel pair closer than 1.4 m): a top plate with sloped ends."""
    groups = []
    for y in sorted(ys):
        if groups and y - groups[-1][-1] < 1.4:
            groups[-1].append(y)
        else:
            groups.append([y])
    f = a.part('Fenders', mat)
    zt = z_top or r * 2 + .12
    for g in groups:
        y0, y1 = g[0] - r - .1, g[-1] + r + .1
        for s in (-1, 1):
            x = s * (W / 2 - .15)
            k.block(f, (.42, y1 - y0 - .3, .05), loc=(x, (y0 + y1) / 2, zt), chamfer=.015)
            for e, yy in ((-1, y0 + .08), (1, y1 - .08)):
                f.box((.42, .32, .05), loc=(x, yy, zt - .12), rot=(e * -.75, 0, 0), bevel=.01, seg=1)


def _cab(a, W, y_front, cab, r, cab_h, armoured=True, mat='Team', roof_hatch=True):
    """A forward-control cab: an extruded body with a raked windscreen and a rounded roof, door insets, the glazing
    (screen, side windows), screen frame bars, mirrors, steps, bumper, grille and lamps; returns the cab's rear y."""
    y0 = y_front
    y1 = y0 + cab
    body = a.part('Cab', mat)
    base = r + .2
    k.extrude(body, [(y0, base), (y0, cab_h - .75), (y0 + .12, cab_h - .62), (y0 + .42, cab_h - .05),
                     (y0 + .55, cab_h), (y1 - .1, cab_h), (y1, cab_h - .08), (y1, base)], W,
              axis='X', chamfer=.06, corner=.05)
    k.inset(body, lambda c, n, f: abs(n.x) > .9 and c.y > y0 + .55 and c.z < cab_h - .55 and c.z > base + .25,
            width=.07, depth=.014)
    glass = a.part('Glass', 'Glass')
    ang = math.atan2(.3, .57)
    glass.box((W * .84, .03, .58), loc=(0, y0 + .27 - .02 * math.cos(ang), cab_h - .335 + .02 * math.sin(ang)),
              rot=(-ang, 0, 0), bevel=0)
    for s in (-1, 1):
        glass.box((.03, cab * .42, .38), loc=(s * (W / 2 + .006), y0 + cab * .52, cab_h - .38), bevel=0)
    st = a.part('Steel', 'Steel')
    st.box((.05, .05, .66), loc=(0, y0 + .25, cab_h - .33), rot=(-ang, 0, 0), bevel=0)
    for s in (-1, 1):
        st.limb((s * (W / 2 + .01), y0 + .15, cab_h - .5), (s * (W / 2 + .09), y0 + .1, cab_h - .45), .03, .03, bevel=0)
        k.block(st, (.05, .14, .26), loc=(s * (W / 2 + .1), y0 + .1, cab_h - .6), chamfer=0)
        st.box((.18, .32, .04), loc=(s * (W / 2 - .02), y0 + cab * .55, base - .05), bevel=0)
        st.box((.18, .32, .04), loc=(s * (W / 2 - .02), y0 + cab * .55, base + .3), bevel=0)
    k.block(st, (W + .08, .18, .22), loc=(0, y0 - .06, r + .02), chamfer=.03)
    a.part('Grille', 'Undercarriage').grille(W * .45, .32, loc=(0, y0 - .02, base + .45), slats=4, depth=.05,
                                             thickness=.04)
    _lights(a, (-(W / 2 - .25), W / 2 - .25), y0 - .02, base + .4, size=(.2, .04, .14))
    if armoured:
        vis = a.part('Visor', 'Armor')
        vis.box((W * .9, .26, .05), loc=(0, y0 + .32, cab_h + .02), rot=(-.2, 0, 0), bevel=.01, seg=1)
    if roof_hatch:
        parts.hatch(a, W * .2, y0 + cab * .65, cab_h, .24, handle=False, seg=10)
    return y1


def _stowage(a, W, y, z, side=1):
    """Jerrycans in a rack and a tool box on one flank of the bed."""
    st = a.part('Stowage', 'Crate')
    x = side * (W / 2 + .06)
    for i in range(3):
        k.block(st, (.14, .32, .44), loc=(x, y + i * .36, z), chamfer=.03, ends=(True, True))
    k.block(a.part('Racks', 'Steel'), (.05, 1.15, .06), loc=(x + side * .05, y + .36, z + .3), chamfer=0)


def _tank_box(a, W, y, z, side=-1):
    k.lathe(a.part('Fuel_tank', 'Steel'), [(0, -.5), (.22, -.5), (.25, -.46), (.25, .46), (.22, .5), (0, .5)],
            loc=(side * (W / 2 - .15), y, z), rot=FORWARD, seg=10)
    k.block(a.part('Tool_box', 'Armor'), (.3, .7, .38), loc=(side * (W / 2 - .12), y + .9, z - .2), chamfer=.03)


def _truck(a, L, W, cab, axles, r, bed_h, cab_h, armoured=True, mat='Team', exhaust=(.85, -1.1, 2.0),
           fire=(0, 0, 1.4)):
    """The six-wheel (or four) truck the drone, microwave and NLOS carriers share: chassis, fenders, cab, a chamfered
    bed with a deck plate and rub rails, flank stowage, fuel tank, tail lamps, exhaust stack; returns (bed top, cab
    rear y)."""
    hd.mark(a, False)
    y0 = -L / 2
    ys = _chassis(a, L, W, axles, r)
    _fenders(a, W, ys, r)
    y1 = _cab(a, W, y0, cab, r, cab_h, armoured=armoured, mat=mat)
    bed = a.part('Bed', mat)
    bl = L - cab - .1
    k.block(bed, (W, bl, bed_h - r - .2), loc=(0, y1 + .05 + bl / 2, r + .2), chamfer=.05)
    _panels(bed, lambda c, n: abs(n.x) > .9, width=.1)
    k.block(a.part('Deck_plate', 'Armor'), (W - .16, bl - .2, .05), loc=(0, y1 + .05 + bl / 2, bed_h), chamfer=.02)
    rub = a.part('Rub_rails', 'Steel')
    for s in (-1, 1):
        rub.box((.05, bl, .06), loc=(s * (W / 2 + .02), y1 + .05 + bl / 2, bed_h - .12), bevel=0)
    _stowage(a, W, y1 + .3, r + .45, side=1)
    _tank_box(a, W, y1 + .55, r + .3, side=-1)
    _lights(a, (-(W / 2 - .2), W / 2 - .2), L / 2 + .02, r + .55, facing=1, size=(.16, .04, .1), lamp='Alloy')
    ex = exhaust
    k.lathe(a.part('Exhaust', 'Steel'), [(.06, -.9), (.06, 0), (.075, .02), (.075, .2)], loc=(ex[0], y1 + .05, cab_h - .2),
            seg=8)
    a.pivot('Point_exhaust', exhaust)
    a.pivot('Point_fire', fire)
    return bed_h, y1


def _bands(a, W, y, z, length=1.6):
    team = a.part('Team_bands', 'Team')
    for s in (-1, 1):
        team.box((.02, length, .2), loc=(s * (W / 2 + .012), y, z), bevel=0)


# ============================================================================= interceptor drone vehicle
def interceptor_drone_vehicle(a):
    """A counter-drone truck: the shared 4x4 armoured truck, a turntable carrying a six-cell interceptor-drone launcher
    with ringed cell doors (`Turret`, `Muzzle_main` where they were), a Ku-band radar panel on a folding mast, and the
    Coyote interceptor pod on its own free-aiming `Mount_aam` (`Muzzle_aam`) behind the cab."""
    top, y1 = _truck(a, 5.0, 2.1, 1.75, 2, .45, 1.15, 2.0, exhaust=(.8, 2.4, .8), fire=(0, 0, 1.7))
    t = a.pivot('Turret', (0, 1.2, 1.15))
    k.lathe(a.part('Turntable', 'Steel', t), [(.75, 0), (.75, .08), (.6, .12), (0, .12)], seg=14)
    k.block(a.part('Cradle', 'Armor', t), (1.2, .9, .3), loc=(0, .3, .1), chamfer=.04)
    pitch = math.radians(28)
    box = a.part('Launcher', 'Team', t)
    size, at = (1.5, 1.6, .9), (0, .05, .25)
    k.block(box, size, loc=at, rot=(-pitch, 0, 0), chamfer=.06, ends=(True, True))
    k.inset(box, lambda c, n, f: abs(n.x) > .9, width=.08, depth=-.012)
    _cells(a, t, at, size, pitch, (3, 2), (.46, .4), .15, 'Cell_rims', 'Cell_doors')
    a.pivot('Muzzle_main', (0, -.72, 1.14), t)
    mast = a.part('Mast', 'Steel')
    k.lathe(mast, [(.08, 0), (.08, 1.1), (.06, 1.12), (.06, 1.5)], loc=(-.75, y1 + .25, 1.15), seg=8)
    pan = a.part('Search_panel', 'Armor')
    pan.box((.7, .12, .55), loc=(-.75, y1 + .2, 2.85), rot=(-.25, 0, 0), bevel=.02, seg=1)
    a.part('Panel_face', 'Undercarriage').box((.6, .02, .45), loc=(-.75, y1 + .13, 2.87), rot=(-.25, 0, 0), bevel=0)
    m = a.pivot('Mount_aam', (.55, y1 + .35, 1.15))
    k.lathe(a.part('AAM_pedestal', 'Steel', m), [(.18, 0), (.18, .06), (.08, .1), (.08, .35)], seg=8)
    pod = a.part('AAM_pod', 'Team', m)
    k.block(pod, (.5, .9, .32), loc=(0, -.05, .35), rot=(-.3, 0, 0), chamfer=.04, ends=(True, True))
    tubes = a.part('AAM_tubes', 'Undercarriage', m)
    for x in (-.12, .12):
        tubes.cyl(.09, .03, loc=(x, -.5, .5), rot=(R90 - .3, 0, 0), seg=8, bevel=0)
    a.pivot('Muzzle_aam', (0, -.52, .5), m)
    _bands(a, 2.1, -1.4, 1.5)
    k.clean(a)


# ============================================================================= microwave vehicle
def microwave_vehicle(a):
    """A high-power-microwave counter-swarm truck: the shared 6x6 truck, a generator container with louvres, cable reels
    and a cooling unit, the emitter on its pedestal (`Turret`, `Muzzle_main` where they were): a framed flat array of
    horn cells with stiffening ribs, a rear electronics box as a counterweight and side handles."""
    top, y1 = _truck(a, 5.8, 2.1, 1.8, 3, .45, 1.2, 2.0, exhaust=(.85, -1.1, 2.0), fire=(0, 0, 1.4))
    _container(a, 'Generators', 'Armor', (0, y1 + .85, top + .05), (1.6, 1.8, .95), yaw=R90, doors=False)
    a.part('Generator_vents', 'Undercarriage').grille(.9, .45, loc=(1.07, y1 + .85, top + .55), rot=(0, 0, R90),
                                                     slats=4, depth=.05, thickness=.04)
    reels = a.part('Cable_reels', 'Hazard')
    for x in (-.65, .65):
        k.lathe(reels, [(.1, -.15), (.32, -.15), (.32, -.12), (.2, -.1), (.2, .1), (.32, .12), (.32, .15), (.1, .15)],
                loc=(x, y1 + 1.95, top + .35), rot=(0, R90, 0), seg=12)
    t = a.pivot('Turret', (0, 1.8, 1.2))
    k.lathe(a.part('Pedestal', 'Armor', t), [(.55, 0), (.55, .08), (.38, .14), (.32, .62), (.42, .68), (.42, .74)],
            seg=14, worn=(1, 4))
    pitch = .18
    em = a.part('Emitter', 'Team', t)
    size, at = (1.9, .3, 1.45), (0, -.1, .55)
    k.block(em, size, loc=at, rot=(-pitch, 0, 0), chamfer=.06, ends=(True, True))
    front, up, out = _box_front(at, size, pitch)
    face = a.part('Emitter_face', 'Undercarriage', t)
    cells = a.part('Horn_cells', 'Steel', t)
    for i in range(5):
        for j in range(4):
            x = (i - 2) * .36
            u = (j - 1.5) * .3
            loc = (x, front[1] + up[1] * u + out[1] * .015, front[2] + up[2] * u + out[2] * .015)
            face.box((.32, .03, .27), loc=loc, rot=(-pitch, 0, 0), bevel=0)
            cells.box((.2, .05, .16), loc=(x, loc[1] + out[1] * .03, loc[2] + out[2] * .03), rot=(-pitch, 0, 0),
                      bevel=0)
    rib = a.part('Emitter_ribs', 'Steel', t)
    for sx in (-1, 1):
        k.block(rib, (.08, .45, 1.5), loc=(sx * .98, -.1, .5), rot=(-pitch, 0, 0), chamfer=.01)
        rib.box((.06, .3, .06), loc=(sx * 1.05, .1, 1.2), bevel=0)
    k.block(a.part('Electronics', 'Armor', t), (1.3, .6, .7), loc=(0, .45, .62), chamfer=.05)
    a.pivot('Muzzle_main', (0, -.35, 1.2), t)
    _bands(a, 2.1, -2.0, 1.6)
    k.clean(a)


# ============================================================================= NLOS ATGM vehicle
def nlos_atgm_vehicle(a):
    """A Spike NLOS launcher truck: the shared 6x6 armoured truck, a turntable with an elevating arm carrying the
    four-cell canister box (`Turret`, `Muzzle_missile` where they were), a datalink mast with an optic head, reload
    canisters on the bed and the cab-roof machine gun (`Mount_mg`, `Muzzle_mg`)."""
    top, y1 = _truck(a, 6.0, 2.1, 1.9, 3, .45, 1.2, 2.0, exhaust=(.85, -1.1, 2.0), fire=(0, 0, 1.4))
    t = a.pivot('Turret', (0, 1.4, 1.2))
    k.lathe(a.part('Turntable', 'Steel', t), [(.7, 0), (.7, .08), (.55, .12), (0, .12)], seg=14)
    k.block(a.part('Hinge', 'Armor', t), (1.3, .8, .4), loc=(0, .4, .1), chamfer=.04)
    pitch = math.radians(30)
    box = a.part('Launcher', 'Team', t)
    size, at = (1.55, 1.9, .9), (0, .1, .25)
    k.block(box, size, loc=at, rot=(-pitch, 0, 0), chamfer=.06, ends=(True, True))
    k.inset(box, lambda c, n, f: abs(n.x) > .9, width=.08, depth=-.012)
    _cells(a, t, at, size, pitch, (2, 2), (.74, .42), .17, 'Canister_rims', 'Canister_caps')
    for sx in (-1, 1):
        a.part('Rams', 'Steel', t).limb((sx * .6, .5, .2), (sx * .6, -.2, .6), .08, .08, bevel=0)
    a.pivot('Muzzle_missile', (0, -.8, 1.16), t)
    reload = a.part('Reloads', 'Team')
    for x in (-.5, .5):
        k.lathe(reload, [(0, -.75), (.17, -.75), (.19, -.7), (.19, .7), (.17, .75), (0, .75)],
                loc=(x, 2.55, top + .2), rot=FORWARD, seg=10)
    mast = a.part('Mast', 'Steel')
    k.lathe(mast, [(.08, 0), (.08, 1.0), (.06, 1.02), (.06, 1.4)], loc=(-.75, y1 + .25, top), seg=8)
    k.block(a.part('Sensor_body', 'Armor'), (.36, .36, .3), loc=(-.75, y1 + .25, top + 1.4), chamfer=.04)
    a.part('Sensor', 'Glass').box((.22, .03, .18), loc=(-.75, y1 + .06, top + 1.55), bevel=0)
    parts.mg_mount(a, None, (.5, -2.3, 2.0), length=.6, shield=True)
    _bands(a, 2.1, -1.0, 1.55)
    k.clean(a)


# ============================================================================= radar scout
def radar_scout(a):
    """A Fennek-type 4x4 reconnaissance car: a low faceted hull with a long raked glacis, side armour skirts over the
    fenders, glazed crew cab windows, a rear engine deck with grilles, stowage bins, the telescopic sensor mast with its
    radar / optics head, and the ring-mounted machine gun (`Turret`, `Muzzle_mg` where they were)."""
    hd.mark(a, False)
    W = 2.0
    ys = _chassis(a, 4.6, W, 2, .45, ys=[-1.4, 1.35])
    hull = a.part('Hull', 'Team')
    k.extrude(hull, [(-2.3, .55), (-2.32, .78), (-1.25, 1.32), (-.35, 1.48), (1.9, 1.48), (2.3, 1.25), (2.3, .55)],
              W, axis='X', chamfer=.07, corner=.05, taper=(.92, 1.0))
    k.inset(hull, lambda c, n, f: abs(n.x) > .9 and c.z > .8 and c.y > -1.0, width=.08, depth=.014)
    _fenders(a, W, ys, .45, z_top=1.02)
    glass = a.part('Glass', 'Glass')
    glass.box((1.3, .03, .32), loc=(0, -.85, 1.35), rot=(-1.0, 0, 0), bevel=0)
    for s in (-1, 1):
        glass.box((.03, .7, .24), loc=(s * (W / 2 * .95 + .01), -.25, 1.25), bevel=0)
    armor = a.part('Armor', 'Armor')
    for s in (-1, 1):
        k.block(armor, (.06, 2.0, .3), loc=(s * (W / 2 + .02), 0, .72), chamfer=.015)
    a.part('Engine_deck', 'Undercarriage').grille(1.2, .9, loc=(0, 1.55, 1.49), rot=(-R90, 0, 0), slats=5, depth=.05,
                                                  thickness=.04)
    st = a.part('Stowage', 'Crate')
    for s in (-1, 1):
        k.block(st, (.3, .9, .3), loc=(s * .75, 1.95, 1.48), chamfer=.03)
    k.block(a.part('Steel', 'Steel'), (W + .06, .14, .2), loc=(0, -2.33, .62), chamfer=.03)
    _lights(a, (-.7, .7), -2.33, .82, size=(.18, .04, .1))
    _lights(a, (-.8, .8), 2.32, .9, facing=1, size=(.12, .04, .08), lamp='Alloy')
    parts.hatch(a, .45, .2, 1.48, .24, handle=False, seg=10)
    parts.smoke_launcher(a, a.part('Smoke_launchers', 'Undercarriage'), .62, -1.1, 1.42, 1, count=3)
    parts.smoke_launcher(a, a.part('Smoke_launchers', 'Undercarriage'), .62, -1.1, 1.42, -1, count=3)
    mast = a.part('Mast', 'Steel')
    k.lathe(mast, [(.13, 0), (.13, .7), (.11, .72), (.11, 1.5), (.09, 1.52), (.09, 2.35)], loc=(0, .85, 1.48), seg=10,
            worn=(1, 3))
    head = a.part('Sensor_head', 'Armor')
    k.block(head, (.6, .44, .48), loc=(0, .85, 3.82), chamfer=.06, ends=(True, True))
    k.block(head, (.9, .14, .34), loc=(0, 1.0, 3.9), chamfer=.03, ends=(True, True))
    lens = a.part('Sensor_lens', 'Glass')
    lens.box((.2, .03, .18), loc=(-.14, .62, 4.08), bevel=0)
    lens.box((.2, .03, .18), loc=(.14, .62, 4.08), bevel=0)
    parts.antenna(a.part('Antenna', 'Steel'), (-.8, 1.9, 1.48), h=1.0, r=.04)
    t = a.pivot('Turret', (0, -.3, 1.45))
    k.lathe(a.part('Ring', 'Armor', t), [(.38, 0), (.38, .1), (.32, .12), (0, .12)], seg=12, worn=(1,))
    gun = a.part('MG', 'Steel', t)
    k.extrude(gun, [(-.2, .22), (.2, .22), (.2, .36), (.02, .4), (-.2, .38)], .15, axis='X', chamfer=.012, corner=.015)
    k.lathe(gun, [(.045, 0), (.045, .5), (.035, .52), (.035, .72), (.055, .74), (.055, .8)], loc=(0, -.15, .3),
            rot=FORWARD, seg=8, worn=(4,))
    k.block(a.part('MG_ammo', 'Armor', t), (.14, .22, .16), loc=(.16, .05, .2), chamfer=.015)
    k.extrude(a.part('MG_shield', 'Armor', t), [(-.28, -.14), (.28, -.14), (.24, .16), (-.24, .16)], .04,
              loc=(0, -.22, .32), rot=(R90 - .1, 0, 0), axis='Z', chamfer=.01)
    a.pivot('Muzzle_mg', (0, -.95, .3), t)
    a.pivot('Point_exhaust', (.8, 2.2, 1.0))
    a.pivot('Point_fire', (0, 0, 1.6))
    _bands(a, W * .96, .6, 1.2, length=1.4)
    k.clean(a)


# ============================================================================= recoilless jeep
def recoilless_jeep(a):
    """An M151-type jeep with the M40 106 mm recoilless rifle: chassis with axles, a body with a long bonnet, flared
    wheel arches and an open tub, a folding framed windscreen, seats, a roll bar, a spare wheel and jerrycans; the rifle
    on its pedestal (`Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main` where they were) with the venturi breech,
    the spotting rifle on top and the elevation handwheel."""
    hd.mark(a, False)
    W = 1.4
    ys = _chassis(a, 3.2, W, 2, .33, ys=[-1.05, .95], frame_z=.42)
    body = a.part('Body', 'Team')
    k.extrude(body, [(-1.55, .5), (-1.58, .78), (-1.45, .9), (-.35, .95), (-.3, .88), (1.35, .88), (1.45, .8),
                     (1.45, .5)], W - .1, axis='X', chamfer=.05, corner=.04)
    k.inset(body, lambda c, n, f: abs(n.x) > .9 and c.y > -.2 and c.z > .6, width=.06, depth=.012)
    arches = a.part('Fenders', 'Team')
    for y in ys:
        for s in (-1, 1):
            k.extrude(arches, [(y - .45, .55), (y - .35, .82), (y + .35, .82), (y + .45, .55), (y + .35, .6),
                               (y - .35, .6)], .2, loc=(s * (W / 2 - .02), 0, 0), axis='X', chamfer=.02, corner=.02)
    a.part('Grille', 'Undercarriage').grille(.75, .28, loc=(0, -1.585, .66), slats=6, depth=.04, thickness=.035)
    _lights(a, (-.5, .5), -1.59, .68, size=(.14, .04, .14))
    st = a.part('Steel', 'Steel')
    k.block(st, (W + .1, .12, .14), loc=(0, -1.65, .48), chamfer=.02)
    frame = a.part('Screen_frame', 'Armor')
    frame.box((W - .05, .05, .05), loc=(0, -.3, 1.38), bevel=0)
    for s in (-1, 1):
        frame.box((.05, .05, .46), loc=(s * (W / 2 - .05), -.3, 1.15), bevel=0)
    a.part('Glass', 'Glass').box((W - .2, .03, .36), loc=(0, -.3, 1.15), bevel=0)
    seats = a.part('Seats', 'Canvas')
    for s in (-1, 1):
        k.block(seats, (.42, .42, .12), loc=(s * .33, .15, .9), chamfer=.03)
        k.block(seats, (.42, .1, .4), loc=(s * .33, .38, .95), rot=(.15, 0, 0), chamfer=.03)
    roll = a.part('Roll_bar', 'Steel')
    roll.tube([(-.62, .6, .88), (-.62, .6, 1.5), (.62, .6, 1.5), (.62, .6, .88)], .03, seg=6)
    k.lathe(a.part('Spare', 'Rubber'), [(.14, -.11), (.3, -.1), (.33, 0), (.3, .1), (.14, .11)],
            loc=(0, 1.55, .78), rot=(R90, 0, 0), seg=12)
    k.lathe(a.part('Hubs', 'Steel'), [(0, -.07), (.15, -.07), (.15, .07), (0, .07)], loc=(0, 1.55, .78), rot=(R90, 0, 0),
            seg=10)
    stw = a.part('Stowage', 'Crate')
    for i in range(2):
        k.block(stw, (.14, .3, .4), loc=(-.78, .9 + i * .34, .55), chamfer=.03, ends=(True, True))
    k.block(a.part('Ammo_boxes', 'Crate'), (.5, .32, .24), loc=(.35, 1.05, .88), chamfer=.03)
    t = a.pivot('Turret', (0, .6, 1.05))
    k.lathe(a.part('Pedestal', 'Steel', t), [(.18, -.15), (.18, -.1), (.08, -.06), (.08, .28), (.12, .3), (.12, .36)],
            seg=10)
    k.block(a.part('Cradle', 'Armor', t), (.22, .7, .16), loc=(0, .05, .3), chamfer=.03)
    parts.barrel(a, 'Main_cannon', t, 0, 1.2, .4, 3.0, .075, seg=10, sleeve=1.25, extractor=(.45, 1.35, .4),
                 brake_name='Muzzle_brake', brake='collar')
    a.pivot('Muzzle_main', (0, 1.2 - 3.23, .4), t)
    k.lathe(a.part('Breech', 'Steel', t), [(.1, -.2), (.14, -.15), (.14, .25), (.17, .32), (.17, .4), (.12, .42)],
            loc=(0, 1.35, .4), rot=FORWARD, seg=10)
    k.lathe(a.part('Spotting_rifle', 'Armor', t), [(0, 0), (.03, 0), (.03, 1.6), (.04, 1.62), (.04, 1.7), (0, 1.7)],
            loc=(0, 1.15, .56), rot=FORWARD, seg=6)
    a.part('Handwheel', 'Steel', t).torus(.1, .02, loc=(.2, .4, .3), rot=(0, R90, 0), seg=10, ring=4)
    a.pivot('Point_exhaust', (.5, 1.4, .5))
    a.pivot('Point_fire', (0, 0, 1.2))
    k.clean(a)


# ============================================================================= self-propelled mortar (AMOS)
def sp_mortar(a):
    """Patria AMV with the AMOS twin 120 mm mortar turret: an 8x8 hull with a raked glacis, tapered flanks and wheel
    arches, axles, driver's hatch with vision blocks, stowage bins, smoke dischargers, the faceted twin-mortar turret
    (`Turret`, `Turret_body`, `Turret_armor`, `Main_cannon` / `_2`, `Muzzle_brake` / `_2`, `Muzzle_main`) and the roof MG
    (`Mount_mg`, `Muzzle_mg`) where they were."""
    hd.mark(a, False)
    W = 2.3
    ys = _chassis(a, 6.0, W, 4, .45, ys=[-2.3, -1.05, .45, 1.7], frame_z=.6)
    hull = a.part('Hull', 'Team')
    k.extrude(hull, [(-2.85, .62), (-3.15, .95), (-3.05, 1.12), (-2.15, 1.72), (2.95, 1.75), (3.15, 1.5),
                     (3.15, .62)], W, axis='X', chamfer=.07, corner=.05, taper=(.9, 1.0))
    k.inset(hull, lambda c, n, f: abs(n.x) > .85 and c.z > 1.0, width=.1, depth=.014)
    _fenders(a, W - .05, ys, .45, z_top=1.0)
    glass = a.part('Glass', 'Glass')
    for x in (-.85, -.6, -.35):
        glass.box((.16, .03, .08), loc=(x, -2.25, 1.74), rot=(-.6, 0, 0), bevel=0)
    parts.hatch(a, -.6, -1.75, 1.74, .26, handle=True, seg=10)
    parts.hatch(a, .6, 2.3, 1.75, .24, handle=False, seg=10)
    a.part('Engine_deck', 'Undercarriage').grille(1.0, .8, loc=(.25, -1.3, 1.76), rot=(-R90, 0, 0), slats=4,
                                                  depth=.05, thickness=.04)
    st = a.part('Stowage', 'Crate')
    for s in (-1, 1):
        k.block(st, (.32, 1.4, .34), loc=(s * (W / 2 - .12), 2.1, 1.73), chamfer=.03)
    k.block(a.part('Bins', 'Armor'), (W - .3, .4, .4), loc=(0, 3.0, 1.2), chamfer=.04)
    for s in (-1, 1):
        _lights(a, (s * .85,), -3.12, 1.0, size=(.16, .04, .1))
        _lights(a, (s * .9,), 3.16, 1.0, facing=1, size=(.12, .04, .08), lamp='Alloy')
        parts.smoke_launcher(a, a.part('Smoke_launchers', 'Undercarriage'), .7, .9, 2.3, s, count=4)
    a.part('Steel', 'Steel').cyl(.9, .08, loc=(0, .5, 1.79), seg=16, bevel=0)
    t = a.pivot('Turret', (0, .5, 1.75))
    tb = a.part('Turret_body', 'Armor', t)

    def ring(z, sx, yf, yr, off=0.0):
        pts = [(-sx * .75, yf), (sx * .75, yf), (sx, yf + .35), (sx, yr), (-sx, yr), (-sx, yf + .35)]
        return [(x, y, z) for x, y in pts]
    k.sharp_loft(tb, [ring(.04, 1.0, -1.05, 1.15), ring(.42, 1.05, -1.15, 1.2), ring(.78, .9, -.95, 1.05)],
                 chamfer=.04)
    k.block(a.part('Turret_bustle', 'Armor', t), (1.6, .6, .55), loc=(0, 1.35, .15), chamfer=.05)
    pitch = math.radians(12)
    for x, suffix in ((-.3, ''), (.3, '_2')):
        parts.barrel(a, f'Main_cannon{suffix}', t, x, -.9, .45, 1.4, .1, seg=12, sleeve=1.25, extractor=(.5, 1.3, .2),
                     brake_name=f'Muzzle_brake{suffix}', brake='collar', rot=(R90 - pitch, 0, 0))
    ta = a.part('Turret_armor', 'Armor', t)
    k.block(ta, (1.0, .32, .48), loc=(0, -1.05, .2), chamfer=.04, taper=(.9, .9))
    for s in (-1, 1):
        k.block(ta, (.08, 1.3, .5), loc=(s * 1.08, .1, .1), rot=(0, s * .12, 0), chamfer=.015)
    k.block(a.part('Sight', 'Armor', t), (.25, .3, .28), loc=(-.65, -.6, .78), chamfer=.03)
    a.part('Sight_lens', 'Glass', t).box((.16, .03, .14), loc=(-.65, -.76, .9), bevel=0)
    parts.hatch(a, .55, .45, .78, .24, parent=t, handle=False, seg=10)
    a.pivot('Muzzle_main', (0, -2.35, .75), t)
    parts.mg_mount(a, t, (.7, .6, .7), length=.6, shield=False)
    a.pivot('Point_exhaust', (1.0, 2.6, 1.4))
    a.pivot('Point_fire', (0, 0, 1.9))
    _bands(a, W * .9, -1.0, 1.3, length=1.6)
    k.clean(a)


# ============================================================================= wheeled howitzer (CAESAR)
def wheeled_howitzer(a):
    """CAESAR 155 mm on a 6x6 truck: chassis with axles and fenders, an armoured forward cab with glazing, a crew
    compartment, a long gun platform with ammunition lockers and side lockers, the travel lock A-frame behind the cab,
    the gun mount with trunnion cheeks, recoil cylinders and the cradle, the 52-calibre barrel with its baffle brake
    (`Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main` where they were), the firing spade on its arms, stowage."""
    hd.mark(a, False)
    W, L, r = 2.1, 7.6, .48
    y0 = -L / 2
    ys = _chassis(a, L, W, 3, r, ys=[-2.75, 1.1, 2.55], frame_z=r + .1)
    _fenders(a, W, ys, r)
    y1 = _cab(a, W, y0, 1.9, r, 2.15, armoured=True, mat='Team')
    crew = a.part('Crew_cab', 'Team')
    k.block(crew, (W, 1.0, 1.15), loc=(0, y1 + .5, r + .2 + .0), chamfer=.06)
    _panels(crew, lambda c, n: abs(n.x) > .9, width=.08)
    plat = a.part('Bed', 'Armor')
    pl = L - 1.9 - 1.0
    k.block(plat, (W, pl, .55), loc=(0, y1 + 1.0 + pl / 2, r + .2), chamfer=.05)
    k.block(a.part('Deck_plate', 'Steel'), (W - .2, pl - .2, .05), loc=(0, y1 + 1.0 + pl / 2, r + .75), chamfer=.02)
    lock = a.part('Lockers', 'Team')
    for s in (-1, 1):
        k.block(lock, (.45, 2.2, .7), loc=(s * (W / 2 - .25), y1 + 1.0 + 1.2, r + .8), chamfer=.04)
        k.inset(lock, lambda c, n, f: abs(n.x) > .9, width=.06, depth=-.01)
    tl = a.part('Travel_lock', 'Steel')
    for s in (-1, 1):
        tl.limb((s * .55, y1 + .1, r + 1.35), (s * .05, y1 + .1, 2.55), .07, .07, bevel=0)
    k.block(tl, (.4, .2, .16), loc=(0, y1 + .1, 2.5), chamfer=.02)
    _stowage(a, W, y1 + 1.2, r + .55, side=1)
    _tank_box(a, W, y1 + 1.2, r + .35, side=-1)
    t = a.pivot('Turret', (0, 2.3, 1.2))
    k.block(a.part('Mount', 'Team', t), (1.6, 1.4, .45), loc=(0, .1, 0), chamfer=.06)
    cheeks = a.part('Cheeks', 'Armor', t)
    for s in (-1, 1):
        k.extrude(cheeks, [(-.6, .4), (.6, .4), (.45, 1.15), (-.2, 1.2), (-.6, .8)], .12, loc=(s * .45, 0, 0),
                  axis='X', chamfer=.02, corner=.02)
    pitch = math.radians(4)
    k.block(a.part('Cradle', 'Armor', t), (.5, 1.6, .34), loc=(0, -.3, .78), chamfer=.04, ends=(True, True))
    parts.barrel(a, 'Main_cannon', t, 0, -.4, .9, 5.6, .09, seg=12, sleeve=1.25, extractor=(.38, 1.5, .5),
                 brake_name='Muzzle_brake', brake='baffle', rot=(R90 - pitch, 0, 0))
    d = 5.875
    a.pivot('Muzzle_main', (0, -.4 - d * math.cos(pitch), .9 + d * math.sin(pitch)), t)
    rec = a.part('Recoil_cylinders', 'Steel', t)
    for s in (-1, 1):
        k.lathe(rec, [(0, 0), (.06, 0), (.06, 1.5), (0, 1.5)], loc=(s * .18, .3, 1.08), rot=(R90 - pitch, 0, 0), seg=8)
    k.block(a.part('Breech', 'Steel', t), (.4, .5, .4), loc=(0, .55, .72), chamfer=.04, ends=(True, True))
    _crate(a, (.45, y1 + 3.3, r + .75), size=(.6, .45, .35), yaw=0.0)
    _crate(a, (-.4, y1 + 3.5, r + .75), size=(.6, .45, .35), yaw=.2)
    sp = a.part('Spade', 'Armor')
    k.extrude(sp, [(-1.0, 0), (1.0, 0), (.85, .9), (-.85, .9)], .14, loc=(0, 3.85, .25), rot=(R90 + .35, 0, 0),
              axis='Z', chamfer=.02, corner=.03)
    for s in (-1, 1):
        a.part('Spade_arms', 'Steel').limb((s * .6, 3.2, .9), (s * .6, 3.75, .55), .12, .12, bevel=0)
    a.pivot('Point_exhaust', (.85, -1.9, 2.0))
    a.pivot('Point_fire', (0, 0, 1.4))
    _bands(a, W, -2.8, 1.5, length=1.2)
    k.clean(a)


def _o(ao=.65, dist=.5, grime=.4):
    return dict(ao_distance=dist, ao_strength=ao, grime_height=grime)


BUILDERS = {
    'heavy_flak_tower': (_runtime_names(heavy_flak_tower), _o(.7, .6, .4)),
    'flare_tower': (_runtime_names(flare_tower), _o(.65, .5, .3)),
    'laser_ad_station': (_runtime_names(laser_ad_station), _o(.7, .6, .4)),
    'visual_jammer': (_runtime_names(visual_jammer), _o(.7, .6, .4)),
    'fire_control_centre': (_runtime_names(fire_control_centre), _o(.65, .6, .4)),
    'radar_site': (_runtime_names(radar_site), _o(.75, .6, .4)),
    'troop_shelter': (_runtime_names(troop_shelter), _o(.65, .6, .5)),
    'repair_bay': (_runtime_names(repair_bay), _o(.8, .8, .4)),
    'interceptor_drone_vehicle': (interceptor_drone_vehicle, _o(.65, .5, .5)),
    'microwave_vehicle': (microwave_vehicle, _o(.65, .5, .5)),
    'nlos_atgm_vehicle': (nlos_atgm_vehicle, _o(.65, .5, .5)),
    'radar_scout': (radar_scout, _o(.65, .4, .4)),
    'recoilless_jeep': (recoilless_jeep, _o(.65, .4, .4)),
    'sp_mortar': (sp_mortar, _o(.65, .5, .5)),
    'wheeled_howitzer': (wheeled_howitzer, _o(.65, .5, .5)),
}
