"""Prompt 35 wave 4, lane C: small parametric helpers for the lane's builders (DECISIONS "Prompt 35 wave 4 (lane C)").

Not a model: generic sub-assemblies only (prompt 35 section 1 allows a component library), each called with the
model's own sizes. Hulls, turrets, cabs, wings and fuselages stay in each model's own script (mb_p35_<id>.py).

* section_loft: a body skinned through cross-sections given as half outlines (mirrored about X = 0), so hulls get
  sloped glacis, cheeks and tumblehome as real faces instead of a box.
* slab_loft: a two-level prism (bottom polygon at z0, top polygon at z1, same point count) for turrets and casemates
  with sloped faces all round.
* running_gear: a track run on one side (belt outline round sprocket, idler and the road wheels, a link every
  `pitch` metres, the road wheels with their tyres and hubs, the toothed sprocket, a spoked idler, return rollers).
* lugged_tyre: a lean wheel (about 230 triangles): a casing with shoulders, tread lugs in two staggered rows, the
  dished rim and the hub with nuts.
* roof_gun: a roof machine gun for a MAIN weapon (Turret / Main_cannon / Muzzle_brake / Muzzle_main kept by the
  caller) that stands clear of the roof line on its post, with cradle, receiver, ammunition can and shield (owner's
  roof-gun rule, MODEL_STANDARD "Roof guns"); a FREE secondary uses mb_kit35.pintle_mg(post=...) instead.
* stowage_box, jerry_rack, cable_reel, ammo_tins: stowage with real sizes.

Conventions: frontier_kit's (metres, +Z up, -Y the front, +X the vehicle's left).
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_parts27 as p27
import mb_vehicles as mv

R90 = math.pi / 2
TAU = math.tau


# ----------------------------------------------------------------------------- bodies
def ring_from_half(y, half):
    """A full closed ring at station y from a half outline [(x, z), ...] running from the bottom centre (x = 0) up the
    +X side to the top centre (x = 0); the -X side is the mirror. Points with x = 0 are not doubled."""
    right = [(x, y, z) for x, z in half]
    left = [(-x, y, z) for x, z in reversed(half) if x > 1e-6]
    pts = right + left
    return pts


def section_loft(part, stations):
    """Skin a body through stations [(y, half_outline), ...] from front to rear (every half outline the same number
    of points, see ring_from_half)."""
    rings = [ring_from_half(y, half) for y, half in stations]
    n = {len(r) for r in rings}
    if len(n) != 1:
        raise ValueError(f'section_loft: rings differ in size {sorted(n)}')
    part.loft(rings, bevel=0)
    return part


def slab_loft(part, bottom, top, z0, z1, loc=(0, 0, 0), mid=None):
    """A prism with sloped sides: polygon `bottom` [(x, y), ...] at z0, `top` (same count) at z1, optional `mid`
    (polygon, z) as a waist between them. Translated by loc."""
    ox, oy, oz = loc
    rings = [[(x + ox, y + oy, z0 + oz) for x, y in bottom]]
    if mid:
        poly, zm = mid
        rings.append([(x + ox, y + oy, zm + oz) for x, y in poly])
    rings.append([(x + ox, y + oy, z1 + oz) for x, y in top])
    part.loft(rings, bevel=0)
    return part


def octagon(w, l, cut, y0=0.0, front_cut=None, rear_cut=None):
    """An eight-sided outline w wide and l long centred at y0, corners cut by `cut` (front / rear cuts optional)."""
    fc = front_cut if front_cut is not None else cut
    rc = rear_cut if rear_cut is not None else cut
    hw, hl = w / 2, l / 2
    return [(-hw + fc, y0 - hl), (hw - fc, y0 - hl), (hw, y0 - hl + fc), (hw, y0 + hl - rc), (hw - rc, y0 + hl),
            (-hw + rc, y0 + hl), (-hw, y0 + hl - rc), (-hw, y0 - hl + fc)]


# ----------------------------------------------------------------------------- tracked
def running_gear(a, s, tx, tw, wheels, wr, sprocket, idler, rollers=(), pitch=.2, hide_top=None, disc_mat='Armor',
                 wheel_w=.2, seg=10, teeth=11, link_h=.04, idler_spokes=5, dust=.3):
    """One side's track run (s = 1 left, -1 right). sprocket / idler = (y, z, r); wheels = road wheel y list at wheel
    radius wr; rollers = [(y, z)] return rollers; hide_top = (y0, y1, z) skips links above z between y0 and y1 (a
    skirt covers them). Names: Tracks, Track_links, Wheels / Tyres / Hubs, Sprockets, Idlers, Rollers."""
    belt = a.part('Tracks', 'Undercarriage')
    links = a.part('Track_links', 'Undercarriage')
    pts = []
    circles = [(sprocket[0], sprocket[1], sprocket[2] + .035), (idler[0], idler[1], idler[2] + .035)]
    circles += [(y, wr, wr + .035) for y in wheels]
    for cy, cz, r in circles:
        for i in range(24):
            u = i * TAU / 24
            pts.append((cy + r * math.cos(u), cz + r * math.sin(u)))
    outline = mv._hull2d(pts)
    k.extrude(belt, outline, tw, loc=(s * tx, 0, 0), axis='X', chamfer=0)
    for (py, pz), (ty, tz) in mv._perimeter(outline, pitch, 0.0):
        if hide_top and hide_top[0] < py < hide_top[1] and pz > hide_top[2]:
            continue
        ny, nz = tz, -ty
        k.block(links, (tw + .03, pitch * .38, link_h), loc=(s * tx, py + ny * .012, pz + nz * .012),
                rot=(math.atan2(tz, ty), 0, 0), chamfer=0)
    xo = s * (tx + tw / 2 - wheel_w * .62)
    for y in wheels:
        p27.road_wheel(a, (xo, y, wr), wr, wheel_w, s, seg=seg, disc_mat=disc_mat)
        a.part('Hubs', 'Steel').cyl(wr * .14, .035, loc=(xo + s * (wheel_w / 2 + .04), y, wr), rot=p27.side_rot(s),
                                    seg=6, bevel=0)
    sy, sz, sr = sprocket
    p27.sprocket(a, (xo, sy, sz), sr, teeth, wheel_w * .7, s)
    iy, iz, ir = idler
    idl = a.part('Idlers', disc_mat)
    k.lathe(idl, [(0, wheel_w * .5), (ir * .3, wheel_w * .5), (ir * .42, wheel_w * .38), (ir * .86, wheel_w * .38),
                  (ir, wheel_w * .22), (ir, -wheel_w * .4), (ir * .8, -wheel_w * .45), (0, -wheel_w * .45)],
            loc=(xo, iy, iz), rot=p27.side_rot(s), seg=seg + 2, worn=(4,))
    for j in range(idler_spokes):
        u = j * TAU / idler_spokes
        idl.box((.035, ir * .5, .04), loc=(xo + s * wheel_w * .42, iy + math.cos(u) * ir * .6,
                                          iz + math.sin(u) * ir * .6), rot=(u + R90, 0, 0), bevel=0)
    for y, z in rollers:
        K.return_roller(a, (xo - s * .02, y, z), .085, wheel_w * .6, s)
    if dust:
        K.dust(a, (s * tx, (sy + iy) / 2, .1), radius=abs(sy - iy) * .45, k=dust)
    return outline


def wheel_arm(part, s, x, y, z, length=.45, back=1, r=.05):
    """A torsion-bar swing arm from the hull side to the road wheel hub (seen between the wheels)."""
    part.limb((s * x, y + back * length * .9, z + .12), (s * x, y, z), r, r * 1.3, bevel=0)


# ----------------------------------------------------------------------------- wheeled
def lugged_tyre(a, centre, r, width, s, lugs=12, seg=14, rim_mat='Steel', nuts=6, parent=None, tyre='Tyres',
                rim='Wheels'):
    """A lean wheel on an axle along X, outer face on side s: casing with shoulders, two staggered rows of tread lugs
    (bigger than the casing so the silhouette shows them), the dished rim with its flange, the hub and nuts."""
    rot = p27.side_rot(s)
    w = width
    ld = r * .07
    R = r - ld
    k.lathe(a.part(tyre, 'Rubber', parent), [(r * .6, -w / 2), (R * .92, -w / 2), (R, -w * .3), (R, w * .3),
                                             (R * .92, w / 2), (r * .6, w / 2)],
            loc=centre, rot=rot, seg=seg, worn=(2, 3))
    m = K.frame(centre, rot)
    tp = a.part(tyre, 'Rubber', parent)
    for i in range(lugs):
        for row in (-1, 1):
            u = (i + (.5 if row > 0 else 0)) * TAU / lugs
            p = m @ Vector((math.cos(u) * (R + ld * .45), math.sin(u) * (R + ld * .45), row * w * .2))
            e = (m.to_3x3() @ Vector((0, 0, 1)))
            tp.box((ld * 1.4, TAU * R / lugs * .5, w * .38), loc=tuple(p),
                   rot=tuple((m.to_3x3() @ _rz(u)).to_euler('XYZ')), bevel=0)
            del e
    f = w / 2
    k.lathe(a.part(rim, rim_mat, parent), [(r * .62, f - .02), (r * .62, f + .012), (r * .56, f + .015),
                                           (r * .5, f - .05), (r * .28, f - .06), (r * .22, f + .01), (0, f + .01)],
            loc=centre, rot=rot, seg=seg, worn=(1, 4))
    nut = a.part(K.KIT['nuts'], 'Steel', parent)
    for i in range(nuts):
        u = i * TAU / nuts
        nut.cyl(r * .03 + .006, .025, loc=tuple(m @ Vector((r * .17 * math.cos(u), r * .17 * math.sin(u), f + .012))),
                rot=rot, seg=5, bevel=0)
    a.part(K.KIT['hubs'], 'Steel', parent).cyl(r * .1, .05, loc=tuple(m @ Vector((0, 0, f + .02))), rot=rot, seg=8,
                                               bevel=0)


def _rz(u):
    from mathutils import Matrix
    return Matrix.Rotation(u, 3, 'Z')


# ----------------------------------------------------------------------------- weapons
def roof_gun(a, loc, parent=None, pivot='Turret', barrel='Main_cannon', brake='Muzzle_brake', muzzle='Muzzle_main',
             post=.35, length=1.3, scale=1.0, shield=True, mat='Armor', tag='', can=True, base_r=.2):
    """A 12.7 mm (scale 1) main-weapon machine gun standing on a roof post: base plate with gussets, the post, the yaw
    pivot `pivot` on its top, a yoke cradle, the receiver with feed cover and spade grips, a ribbed barrel with
    carrying handle and a flash hider, the ammunition can on its bracket, a bent shield. Returns the pivot."""
    x, y, z = loc
    sc = scale
    base = a.part(f'Gun_post{tag}', 'Steel', parent)
    k.lathe(base, [(base_r * sc, 0), (base_r * sc, .03 * sc), (.06 * sc, .06 * sc), (.05 * sc, post),
                   (.075 * sc, post), (0, post)], loc=loc, seg=10, worn=(1, 3))
    for g in range(4):
        u = g * TAU / 4 + TAU / 8
        base.box((.012 * sc, base_r * .7 * sc, .14 * sc), loc=(x + math.cos(u) * base_r * .5 * sc,
                                                             y + math.sin(u) * base_r * .5 * sc, z + .09 * sc),
                 rot=(0, 0, u + R90), bevel=0)
    p = a.pivot(pivot, (x, y, z + post), parent)
    cr = a.part(f'Cradle{tag}', mat, p)
    for s in (-1, 1):
        k.block(cr, (.025 * sc, .22 * sc, .16 * sc), loc=(s * .09 * sc, 0, .02 * sc), chamfer=.006)
    cr.box((.2 * sc, .1 * sc, .03 * sc), loc=(0, 0, .02 * sc), bevel=0)
    zg = .15 * sc
    rc = a.part(f'Gun_receiver{tag}', 'Undercarriage', p)
    k.extrude(rc, [(-.25 * sc, -.065 * sc), (.2 * sc, -.065 * sc), (.22 * sc, .045 * sc), (.06 * sc, .075 * sc),
                   (-.25 * sc, .065 * sc)], .14 * sc, loc=(0, 0, zg), axis='X', chamfer=.01, corner=.01)
    for s in (-1, 1):
        rc.limb((s * .045 * sc, .2 * sc, zg + .02 * sc), (s * .06 * sc, .31 * sc, zg - .05 * sc), .024 * sc,
                .024 * sc, bevel=0)
    bp = a.part(barrel, 'Steel', p)
    front = -.25 * sc
    L = length * sc
    k.lathe(bp, [(.045 * sc, 0), (.045 * sc, .24 * sc), (.03 * sc, .28 * sc), (.024 * sc, L - .1 * sc),
                 (0, L - .1 * sc)], loc=(0, front, zg), rot=K.FORWARD, seg=8, worn=(1,))
    for j in range(3):
        bp.cyl(.034 * sc, .025 * sc, loc=(0, front - (.36 + j * .12) * sc, zg), rot=K.FORWARD, seg=8, bevel=0)
    K.handle(bp, (0, front - .3 * sc, zg + .04 * sc), (0, front - .5 * sc, zg + .04 * sc), (0, 0, 1), h=.05 * sc,
             r=.01 * sc)
    k.lathe(a.part(brake, 'Undercarriage', p), [(.024 * sc, L - .12 * sc), (.038 * sc, L - .1 * sc),
                                               (.038 * sc, L - .01 * sc), (.027 * sc, L), (0, L)],
            loc=(0, front, zg), rot=K.FORWARD, seg=8, worn=(1,))
    if can:
        am = a.part(f'Ammo_boxes{tag}', 'Crate', p)
        k.block(am, (.13 * sc, .32 * sc, .21 * sc), loc=(.17 * sc, .02 * sc, zg - .15 * sc), chamfer=.012)
        a.part(f'Gun_bracket{tag}', 'Steel', p).box((.18 * sc, .34 * sc, .02 * sc), loc=(.17 * sc, .02 * sc,
                                                                                         zg - .16 * sc), bevel=0)
        a.part(f'Gun_belt{tag}', 'Crate', p).tube([(.11 * sc, .02 * sc, zg + .05 * sc), (.07 * sc, 0, zg + .07 * sc),
                                                   (.05 * sc, -.02 * sc, zg + .04 * sc)], .014 * sc, seg=4)
    if shield:
        sh = a.part(f'Gun_shield{tag}', mat, p)
        k.extrude(sh, [(-.34 * sc, -.16 * sc), (.34 * sc, -.16 * sc), (.3 * sc, .24 * sc), (.1 * sc, .28 * sc),
                       (-.1 * sc, .28 * sc), (-.3 * sc, .24 * sc)], .025 * sc, loc=(0, -.4 * sc, zg),
                  rot=(R90 - .12, 0, 0), axis='Z', chamfer=.008, corner=.01)
        for s in (-1, 1):
            k.extrude(sh, [(-.13 * sc, -.15 * sc), (.13 * sc, -.15 * sc), (.11 * sc, .19 * sc), (-.11 * sc, .19 * sc)],
                      .02 * sc, loc=(s * .44 * sc, -.31 * sc, zg), rot=(R90, 0, s * .55), axis='Z', chamfer=.006)
    K.periscope(a, (-.13 * sc, -.05 * sc, zg + .1 * sc), facing=(0, -1, 0), parent=p,
                size=(.06 * sc, .08 * sc, .06 * sc))
    a.pivot(muzzle, (0, front - L - .005, zg), p)
    return p


def gun_tube(a, name, parent, loc, length, r, seg=12, mat='Steel', sleeve=None, brake=None, brake_name=None,
             extractor=None, taper=.85):
    """A gun barrel along -Y from loc (its breech end at the mantlet): the tube tapering towards the muzzle, optional
    thermal sleeve bands (count), fume extractor (y fraction, radius k), and a muzzle brake ('baffle', 'double',
    'pepper', None) as its own part `brake_name`."""
    x, y, z = loc
    L = length
    k.lathe(a.part(name, mat, parent), [(r * 1.25, 0), (r * 1.25, L * .06), (r, L * .08), (r * taper, L),
                                        (0, L)], loc=loc, rot=K.FORWARD, seg=seg, worn=(1,))
    if sleeve:
        sl = a.part(f'{name}_sleeve', 'Armor', parent)
        for j in range(sleeve):
            f = .14 + j * (.7 / max(1, sleeve))
            sl.cyl(r * 1.12, .05, loc=(x, y - L * f, z), rot=K.FORWARD, seg=seg, bevel=0)
    if extractor:
        f, kk = extractor
        k.lathe(a.part(f'{name}_evacuator', 'Steel', parent),
                [(r * .98, -.18), (r * kk, -.12), (r * kk, .12), (r * .98, .18)], loc=(x, y - L * f, z),
                rot=K.FORWARD, seg=seg, worn=(1, 2))
    if brake and brake_name:
        bp = a.part(brake_name, 'Steel', parent)
        y1 = y - L
        if brake == 'baffle':
            k.extrude(bp, [(-r * 1.5, -r * 1.2), (r * 1.5, -r * 1.2), (r * 1.5, r * 1.2), (-r * 1.5, r * 1.2)],
                      r * 4.5, loc=(x, y1 - r * 2.1, z), axis='Y', chamfer=r * .3, corner=r * .3)
            a.part(f'{brake_name}_ports', 'Undercarriage', parent).box((r * 3.06, r * 1.2, r * 1.4),
                                                                       loc=(x, y1 - r * 2.1, z), bevel=0)
        elif brake == 'double':
            for j, yy in enumerate((y1 - r * 1.2, y1 - r * 3.6)):
                k.lathe(bp, [(r * .9, -r * .8), (r * 1.55, -r * .7), (r * 1.55, r * .7), (r * .9, r * .8)],
                        loc=(x, yy, z), rot=K.FORWARD, seg=seg, worn=(1, 2))
            bp.cyl(r * .95, r * 4.8, loc=(x, y1 - r * 2.4, z), rot=K.FORWARD, seg=seg, bevel=0)
        elif brake == 'pepper':
            k.lathe(bp, [(r * .95, 0), (r * 1.25, r * .3), (r * 1.25, r * 4), (r * 1.05, r * 4.4), (0, r * 4.4)],
                    loc=(x, y1 + r * .2, z), rot=K.FORWARD, seg=seg, worn=(2,))
        else:   # a plain muzzle collar
            k.lathe(bp, [(r * .95, 0), (r * 1.15, r * .2), (r * 1.15, r * 1.6), (0, r * 1.6)],
                    loc=(x, y1 + r * .4, z), rot=K.FORWARD, seg=seg, worn=(1,))
    return (x, y - L, z)


# ----------------------------------------------------------------------------- stowage
def stowage_box(a, size, loc, rot=(0, 0, 0), mat='Armor', name='Stowage', latches=2, parent=None):
    """A stowage bin with a lid lip, hinges along its back and latches on its face."""
    sx, sy, sz = size
    x, y, z = loc
    k.block(a.part(name, mat, parent), size, loc=loc, rot=rot, chamfer=.02)
    a.part(name, mat, parent).box((sx + .02, sy + .02, .025), loc=(x, y, z + sz - .02), rot=rot, bevel=0)
    st = a.part('Kit_latches', 'Steel', parent)
    for i in range(latches):
        f = (i + .5) / latches - .5
        c = Vector((f * sx * .8, -sy / 2 - .008, sz * .75))
        if rot != (0, 0, 0):
            from mathutils import Euler
            c = Euler(rot).to_matrix() @ c
        st.box((.05, .015, .06), loc=(x + c.x, y + c.y, z + c.z), rot=rot, bevel=0)


def jerry_rack(a, loc, count=2, axis='X', rot=(0, 0, 0), parent=None):
    """Jerrycans in a frame (frame bars and strap)."""
    x, y, z = loc
    for i in range(count):
        d = (i - (count - 1) / 2) * .19
        p = (x + d, y, z) if axis == 'X' else (x, y + d, z)
        K.jerrycan(a.part('Jerrycans', 'Fuel', parent), p, rot=rot)
    fr = a.part('Kit_racks', 'Steel', parent)
    span = count * .19 + .04
    if axis == 'X':
        fr.box((span, .04, .03), loc=(x, y - .2, z + .3), bevel=0)
        fr.box((span, .04, .03), loc=(x, y - .2, z + .04), bevel=0)
    else:
        fr.box((.04, span, .03), loc=(x - .2, y, z + .3), bevel=0)
        fr.box((.04, span, .03), loc=(x - .2, y, z + .04), bevel=0)


def cable_reel(a, loc, r=.22, w=.3, axis='X', parent=None):
    """A tow cable on a drum: the two flanges, the coiled cable, the hub."""
    rot = (0, R90, 0) if axis == 'X' else K.FORWARD
    k.lathe(a.part('Tow_cable', 'Undercarriage', parent), [(r * .45, -w / 2), (r * .88, -w / 2 + .02),
                                                            (r * .88, w / 2 - .02), (r * .45, w / 2)], loc=loc,
            rot=rot, seg=12)
    fl = a.part('Kit_reel', 'Steel', parent)
    for s in (-1, 1):
        off = (s * w / 2, 0, 0) if axis == 'X' else (0, s * w / 2, 0)
        fl.cyl(r, .02, loc=tuple(Vector(loc) + Vector(off)), rot=rot, seg=12, bevel=0)


def ammo_tins(a, loc, n=3, size=(.12, .3, .2), parent=None, axis='X'):
    """A row of ammunition cans with their lid handles."""
    x, y, z = loc
    for i in range(n):
        d = (i - (n - 1) / 2) * (size[0] + .02)
        p = (x + d, y, z) if axis == 'X' else (x, y + d, z)
        k.block(a.part('Ammo_boxes', 'Crate', parent), size, loc=p, chamfer=.01)
        a.part('Kit_handles', 'Steel', parent).box((.02, size[1] * .4, .02), loc=(p[0], p[1], p[2] + size[2] + .01),
                                                   bevel=0)


def hatch(a, loc, r=.25, parent=None, mat='Armor', periscope=False, facing=(0, -1, 0), seg=10):
    """A lean round hatch: the coaming ring, the domed lid, a hinge block and a grab handle (about 90 triangles)."""
    x, y, z = loc
    hp = a.part('Hatches', mat, parent)
    k.ring(hp, [(r * .92, 0), (r * 1.06, 0), (r * 1.06, .04), (r * .92, .04)], loc=loc, seg=seg)
    k.lathe(hp, [(0, .085), (r * .7, .075), (r * .9, .05), (r * .9, .03)], loc=loc, seg=seg, worn=(2,))
    st = a.part('Kit_steel', 'Steel', parent)
    st.box((r * .5, .06, .05), loc=(x, y + r * .95, z + .05), bevel=0)
    st.box((r * .6, .025, .025), loc=(x, y - r * .45, z + .1), bevel=0)
    if periscope:
        K.periscope(a, (x + facing[0] * r * 1.2, y + facing[1] * r * 1.2, z), facing=facing, parent=parent,
                    size=(.12, .07, .06))
