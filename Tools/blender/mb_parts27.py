"""Prompt 27 experiment 1, variable V2: the shared parts library (DECISIONS "27 scope (v2)", "27 experiment 1").

Only the parts the four experiment models need: road wheels, sprockets, idlers, tracks with sag, hatches, gun barrels
with muzzle collars / brakes, the pintle MG mount, smoke launchers, antennas, rotor heads, jet nozzles and engine
bells, engine nacelles, pylons, missile rails and racks, canopies. Every part is built from the V1 primitives
(mb_kit27) and takes the same arguments as the helper it replaces where there is one (mb_p25_models._lean_tracks,
mb_vehicles._hatch / _roof_mg / _smoke, mb_air._rotor_head / _tail_rotor / _nozzle / _pylon), so a builder swaps a
helper for a part without moving anything. Part names, pivots and muzzles are the replaced helpers' own (Mount_mg,
Muzzle_mg, Rotor_*, Tail_rotor_*, Nozzles, Missiles ...): nothing the runtime looks up changes.
"""
import math

import bmesh
from mathutils import Matrix, Vector

import mb_detail as hd
import mb_kit27 as k
import mb_vehicles as mv

R90 = math.pi / 2
TAU = math.tau
FORWARD = (R90, 0, 0)    # local +Z -> -Y
BACKWARD = (-R90, 0, 0)  # local +Z -> +Y


def side_rot(s):
    """Rotation turning local +Z out of the +X (s = 1) or -X (s = -1) side."""
    return (0, s * R90, 0)


# ----------------------------------------------------------------------------- running gear
def road_wheel(a, centre, r, width, s, seg=10, tyre='Tyres', disc='Wheels', hub='Hubs', disc_mat='Team'):
    """Road wheel on an axle along X at centre, its outer face towards side s: a rubber tyre with rounded shoulders, a
    dished disc with a raised rim and a hub boss (the bake darkens the dish), hub bolts at high detail."""
    x, y, z = centre
    w = width
    k.lathe(a.part(tyre, 'Undercarriage'), [(r * .8, -w / 2), (r * .96, -w / 2), (r, -w / 2 + .02), (r, w / 2 - .02),
                                            (r * .96, w / 2), (r * .8, w / 2)],
            loc=(x, y, z), rot=side_rot(s), seg=seg, worn=(2, 3))
    k.lathe(a.part(disc, disc_mat), [(0, w / 2 + .03), (r * .24, w / 2 + .03), (r * .3, w / 2 + .008),
                                     (r * .6, w / 2 - .004), (r * .72, w / 2 + .02), (r * .8, w / 2 + .012),
                                     (r * .8, w / 2 - .03)],
            loc=(x, y, z), rot=side_rot(s), seg=seg, worn=(4,))
    if hd.on(a):
        m = hd.frame((x + s * (w / 2 + .03), y, z), side_rot(s))
        hd.bolt_ring(a.part('Wheel_bolts', 'Steel'), m, r * .17, 6, r=.014, h=.02)
        a.part(hub, 'Steel').cyl(r * .12, .03, loc=(x + s * (w / 2 + .04), y, z), rot=side_rot(s), seg=6, bevel=0)


def sprocket(a, centre, r, teeth, width, s, part='Sprockets', mat='Armor'):
    """Toothed drive sprocket (axle along X): a gear outline extruded, a dished hub over it."""
    x, y, z = centre
    p = TAU / teeth
    outline = []
    for i in range(teeth):
        u = i * p
        for du, rr in ((-.42 * p, r * .86), (-.18 * p, r * 1.04), (.18 * p, r * 1.04), (.42 * p, r * .86)):
            outline.append((math.cos(u + du) * rr, math.sin(u + du) * rr))
    k.extrude(a.part(part, mat), outline, width, loc=(x, y, z), axis='X', chamfer=.012 if hd.on(a) else 0)
    k.lathe(a.part('Hubs', 'Steel'), [(0, width / 2 + .05), (r * .3, width / 2 + .05), (r * .38, width / 2 + .02),
                                      (r * .55, width / 2), (r * .55, -width / 2 + .01)],
            loc=(x, y, z), rot=side_rot(s), seg=8)


def idler(a, centre, r, width, s, seg=10):
    """Idler wheel: a tyre and a spoked-looking dished disc (the road wheel's, larger hub)."""
    road_wheel(a, centre, r, width, s, seg=seg)


def track_unit(a, x, length, top, wheel_r, wheels, belt_width, sprocket_end=1, cleat_pitch=.21, wheel_seg=8, teeth=7,
               return_rollers=3, sag=.035):
    """Both track units, a drop-in for mb_p25_models._lean_tracks: the belt round idler, sprocket and the first and
    last road wheels, its upper run sagging `sag` between `return_rollers` supports (the rollers themselves only at
    high detail, under the skirts), cleats arrayed along the curved ends, dished road wheels, a toothed sprocket at
    the `sprocket_end` end and an idler at the other. x is the belt's centre line; the belt runs from `top` to 1 cm
    below the ground."""
    belt = a.part('Tracks', 'Undercarriage')
    bottom = -.01
    rb = min(.25, (top - bottom) * .3)
    first = length / 2 - wheel_r - .12
    circles = [(e * (length / 2 - rb), top - rb, rb) for e in (-1, 1)] + \
              [(e * first, bottom + wheel_r, wheel_r) for e in (-1, 1)]
    hull = mv._hull2d([(cy + r * math.cos(i * TAU / 16), cz + r * math.sin(i * TAU / 16))
                       for cy, cz, r in circles for i in range(16)])
    # Replace the straight top run (the hull's edge at z = top) by a sagging one over the return rollers.
    e = length / 2 - rb
    keep = [p for p in hull if not (p[1] > top - 1e-3 and -e + 1e-3 < p[0] < e - 1e-3)]
    i_end = next(i for i, p in enumerate(keep) if abs(p[1] - top) < 1e-3 and p[0] > 0)
    supports = [e - j * 2 * e / (return_rollers + 1) for j in range(return_rollers + 2)]
    run = []
    for y0, y1 in zip(supports, supports[1:]):
        for t in (.25, .5, .75, 1.0):
            yy = y0 + (y1 - y0) * t
            run.append((yy, top - (sag * 4 * t * (1 - t) if t < 1 else 0)))
    run = run[:-1]
    outline = keep[:i_end + 1] + run + keep[i_end + 1:]
    detail = hd.on(a)
    seg = 14 if detail else wheel_seg
    for s in (-1, 1):
        cx = s * x
        face = cx + s * belt_width / 2
        k.extrude(belt, outline, belt_width, loc=(cx, 0, 0), axis='X', chamfer=.015 if detail else 0)
        # Cleats along the curved ends only (the runs are under the skirts and the hull).
        for (py, pz), (ty, tz) in mv._perimeter(outline, cleat_pitch, .05):
            if abs(py) < first - .02:
                continue
            ny, nz = tz, -ty
            k.block(belt, (belt_width + .04, .07, .05), loc=(cx, py + ny * .012, pz + nz * .012),
                    rot=(math.atan2(tz, ty), 0, 0), chamfer=0)
        for i in range(wheels):
            y = -first + i * 2 * first / (wheels - 1)
            road_wheel(a, (face - s * .03, y, bottom + wheel_r), wheel_r, .12, s, seg=seg)
        if detail:
            for y in supports[1:-1]:
                a.part('Hubs', 'Steel').cyl(.07, .1, loc=(face - s * .05, y, top - .08), rot=side_rot(s), seg=8, bevel=0)
        for end in (-1, 1):
            cy, cz = end * (length / 2 - rb), top - rb
            if end == sprocket_end:
                sprocket(a, (face - s * .02, cy, cz), rb * .96, max(9, teeth + 2), .1, s)
            else:
                idler(a, (face - s * .03, cy, cz), rb * .92, .12, s, seg=seg)


# ----------------------------------------------------------------------------- hull and turret fittings
def hatch(a, x, y, z, r, parent=None, mat='Armor', handle=True, hinge=1, seg=12):
    """Round hatch on a roof at height z, a drop-in for mb_vehicles._hatch: a coaming ring, a domed lid with a worn
    rim, a hinge barrel (towards +Y if hinge=1); the grab handle and a periscope boss at high detail."""
    lid = a.part('Hatches', mat, parent)
    steel = a.part('Hatch_fittings', 'Steel', parent)
    k.ring(lid, [(r * .98, -.02), (r * 1.13, -.02), (r * 1.13, .03), (r * 1.0, .045)], loc=(x, y, z), seg=seg, worn=(2,))
    k.lathe(lid, [(0, .085), (r * .7, .082), (r * .9, .072), (r * .97, .05), (r * .97, .0)], loc=(x, y, z), seg=seg,
            worn=(2,))
    k.lathe(steel, [(.034, -r * .45), (.034, r * .45)], loc=(x, y + hinge * (r + .04), z + .04), rot=(0, R90, 0), seg=6)
    if hd.on(a):
        hd.bolt_ring(steel, hd.frame((x, y, z + .075)), r * .78, 8, r=.013, h=.02, phase=.2)
        lid.cyl(r * .22, .03, loc=(x - r * .35, y + hinge * r * .2, z + .09), seg=8, bevel=0)
        if handle:
            hy = y - hinge * r * .3
            k.sweep(steel, [(-.01, -.01), (.01, -.01), (.01, .01), (-.01, .01)],
                    [(x - r * .4, hy, z + .07), (x - r * .4, hy, z + .13), (x + r * .4, hy, z + .13),
                     (x + r * .4, hy, z + .07)])


def barrel(a, name, parent, x, y0, z, length, r, seg=12, sleeve=1.22, extractor=(.4, 1.65, .42), brake_name=None,
           brake='collar', brake_mat='Undercarriage', rot=FORWARD):
    """A gun barrel from the mantlet face at y0 forward (-Y) as one revolved surface: root collar, thermal sleeve with
    clamp steps, a fume extractor with tapered ends at `extractor` = (position along the barrel, radius factor,
    length), a slightly tapered muzzle end with a dark bore. brake_name adds the recoiling muzzle part: 'collar' (a
    reference collar ring, smooth bores) or 'baffle' (a double-baffle brake with side ports)."""
    L = length
    u, rf, el = extractor
    e0, e1 = L * u - el / 2, L * u + el / 2
    s1 = L * .67
    prof = [(r * 1.32, -.06), (r * 1.32, .08), (r * sleeve, .13),
            (r * sleeve, e0 - .05), (r * rf, e0 + .03), (r * rf, e1 - .05), (r * sleeve, e1 + .03),
            (r * sleeve, s1 * .82), (r * (sleeve + .06), s1 * .82 + .02), (r * (sleeve + .06), s1 * .82 + .06),
            (r * sleeve, s1 * .82 + .08), (r * sleeve, s1), (r, s1 + .03),
            (r * .95, L), (r * .58, L), (r * .58, L - .12), (0, L - .12)]
    k.lathe(a.part(name, 'Steel', parent), prof, loc=(x, y0, z), rot=rot, seg=seg, worn=(5, 9))
    if brake_name:
        part = a.part(brake_name, brake_mat, parent)
        if brake == 'baffle':
            k.lathe(part, [(r * 1.5, L - .02), (r * 1.5, L + .3), (r * .62, L + .3), (r * .62, L + .26), (0, L + .26)],
                    loc=(x, y0, z), rot=rot, seg=seg, worn=(1,))
            m = hd.frame((x, y0, z), rot)
            for dz in (.08, .2):
                k.block(part, (r * 3.4, r * 1.4, .05), loc=tuple(m @ Vector((0, 0, L + dz))), rot=rot, chamfer=.008)
        else:
            k.ring(part, [(r * .6, L - .02), (r * 1.3, L - .02), (r * 1.3, L + .12), (r * 1.18, L + .14),
                          (r * .6, L + .14)], loc=(x, y0, z), rot=rot, seg=seg, worn=(2,))


def mg_mount(a, parent, loc, length=.8, shield=True):
    """Pintle heavy machine gun on its own `Mount_mg` yaw pivot, a drop-in for mb_vehicles._roof_mg: a turned pintle,
    a chamfered receiver with a sloped feed cover, a barrel with a jacket and a flash-hider cone, an ammunition box,
    the shield. `Muzzle_mg` sits where the helper put it."""
    m = a.pivot('Mount_mg', loc, parent)
    mg = a.part('MG', 'Steel', m)
    k.lathe(mg, [(.075, 0), (.075, .03), (.05, .05), (.045, .14)], seg=8, worn=(1,))
    k.extrude(mg, [(-.16, .13), (.2, .13), (.2, .25), (.02, .28), (-.16, .27)], .14, axis='X', chamfer=.012, corner=.015)
    k.block(mg, (.05, .16, .08), loc=(0, .24, .17), rot=(.3, 0, 0), chamfer=.01)          # grips
    front = .02 - .18
    k.lathe(mg, [(.04, 0), (.04, .22), (.03, .25), (.028, length - .1), (.045, length - .08), (.045, length - .01),
                 (.03, length), (.02, length), (.02, length - .04), (0, length - .04)],
            loc=(0, front + .04, .21), rot=FORWARD, seg=8, worn=(4,))
    k.block(a.part('MG_ammo', 'Armor', m), (.12, .2, .14), loc=(.14, .04, .19), chamfer=.015)
    if shield:
        k.extrude(a.part('MG_shield', 'Armor', m), [(-.24, -.15), (.24, -.15), (.2, .15), (-.2, .15)], .04,
                  loc=(0, -.24, .25), rot=(-.12 + R90, 0, 0), axis='Z', chamfer=.01)
    if hd.on(a):
        det = a.part('MG_detail', 'Steel', m)
        det.box((.025, .03, .06), loc=(0, -.14, .29), bevel=0)
        det.box((.05, .03, .05), loc=(0, .17, .285), bevel=0)
        k.sweep(det, [(-.008, -.008), (.008, -.008), (.008, .008), (-.008, .008)],
                [(-.035, -.08, .26), (-.035, -.08, .31), (-.035, .1, .31), (-.035, .1, .26)])
        belt = a.part('MG_belt', 'Crate', m)
        for j in range(3):
            belt.box((.03, .06, .035), loc=(.1 - j * .025, .03, .215 + j * .012), rot=(0, -.5, 0), bevel=0)
    a.pivot('Muzzle_mg', (0, front - length + .02, .21), m)


def smoke_launcher(a, part, x, y, z, s, count=3, gap=.07, r=.04, depth=.14):
    """Smoke-grenade dischargers on side s, a drop-in for mb_vehicles._smoke: a bracket block under the row, each tube
    revolved with a lip round its mouth and a dark recessed bore (no separate bore part)."""
    parent = next((key[2] for key, v in a.shapes.items() if v is part), None)
    rot = (.6, 0, s * .4)
    span = (count - 1) * gap
    k.block(a.part('Smoke_brackets', 'Armor', parent), (span + r * 2.6, r * 2.2, .05),
            loc=(s * (x + span / 2), y + .02, z - r * 1.1), chamfer=.012)
    h = depth / 2
    for i in range(count):
        k.lathe(part, [(r * .9, -h), (r, -h + .012), (r, h - .016), (r * 1.18, h - .012), (r * 1.18, h),
                       (r * .74, h), (r * .74, h - .045), (0, h - .045)],
                loc=(s * (x + i * gap), y, z), rot=rot, seg=8, worn=(4,))


def antenna(part, loc, h=.45, r=.05, seg=8):
    """Antenna on its base: a turned base boss and a tapered mast at least 10 cm thick (no shimmering whips), a
    ball at the tip."""
    k.lathe(part, [(r * 2.3, -.02), (r * 2.3, .03), (r * 1.5, .07), (r * 1.1, .09), (r * 1.0, h), (r * 1.25, h + .02),
                   (r * 1.25, h + .07), (0, h + .09)], loc=loc, seg=seg, worn=(1, 5))


# ----------------------------------------------------------------------------- rotors
def rotor_head(a, r, blades, R, chord, hub=.3, phase=0.0, t=.05, cap=.25, stripe=.28, droop=.06):
    """Main rotor under pivot r (spins about local Z), a drop-in for mb_air._rotor_head: one turned hub (plates, hub
    body and cap in a single revolved surface), a swashplate ring, chamfered blade grips, turned dampers and pitch
    links, the airfoil blades with their tip stripes (mb_air._blade)."""
    from mb_air import _blade
    steel = a.part('Rotor_hub', 'Steel', r)
    grips = a.part('Rotor_grips', 'Armor', r)
    blades_p = a.part('Rotor_blades', 'Armor', r)
    tips = a.part('Rotor_tips', 'Hazard', r)
    k.lathe(steel, [(hub * .7, -.06), (hub, -.05), (hub, .05), (hub * .8, .07), (hub * .78, .17), (hub * .55, .19),
                    (hub * .45, .14 + cap * .5), (hub * .22, .14 + cap), (0, .17 + cap)], seg=14, worn=(2, 4))
    k.ring(steel, [(hub * .35, -.26), (hub * .82, -.26), (hub * .82, -.21), (hub * .35, -.21)], seg=14, worn=(2,))
    grip = .5 + hub * .4
    for j in range(blades):
        ang = phase + j * TAU / blades
        d = Vector((math.cos(ang), math.sin(ang), 0))
        e = Vector((-math.sin(ang), math.cos(ang), 0))
        k.block(grips, (grip, chord * .55, .1), loc=tuple(d * (hub * .6 + grip / 2) + Vector((0, 0, .012))),
                rot=(0, 0, ang), chamfer=.02)
        p = d * (hub * .75 + grip * .38) + e * chord * .36 + Vector((0, 0, .02))
        k.lathe(steel, [(.04, -grip * .35), (.04, grip * .35)], loc=tuple(p), rot=(0, R90, ang), seg=6)
        q = d * hub * .72 - e * (chord * .275 + .04) + Vector((0, 0, -.12))
        k.lathe(steel, [(.022, -.13), (.022, .13)], loc=tuple(q), seg=5)
        _blade(blades_p, tips, d, e, (0, 0, 1), hub * .6 + grip - .06, R, chord, t, stripe=stripe, droop=droop)
    if hd.on(a):
        bolts = a.part('Rotor_bolts', 'Steel', r)
        hd.bolt_ring(bolts, hd.frame((0, 0, .06)), hub * .89, 8, r=.018, h=.024)
        for j in range(blades):
            ang = phase + j * TAU / blades
            d = Vector((math.cos(ang), math.sin(ang), 0))
            for f in (.3, .72):
                hd.bolt(bolts, tuple(d * (hub * .6 + grip * f) + Vector((0, 0, .062))), r=.016, h=.022)
        for sx in (-1, 1):
            bolts.limb((sx * hub * .52, 0, -.2), (sx * hub * .3, 0, -.06), .03, .03, bevel=0)


def tail_rotor(a, tr, blades, R, chord, t=.028, phase=0.0, side=-1):
    """Tail rotor under pivot tr (spins about local X), a drop-in for mb_air._tail_rotor: one turned hub with its
    pitch-spider cap, airfoil blades with tip stripes."""
    from mb_air import _blade
    hub = a.part('Tail_rotor_hub', 'Steel', tr)
    k.lathe(hub, [(R * .1 + .02, -.05), (R * .1 + .02, .04), (R * .08, .06), (R * .06, .1), (0, .14)],
            rot=(0, side * R90, 0), seg=10, worn=(1,))
    bl = a.part('Tail_rotor_blades', 'Armor', tr)
    tips = a.part('Tail_rotor_tips', 'Hazard', tr)
    for j in range(blades):
        ang = phase + j * TAU / blades
        d = (0, -math.sin(ang), math.cos(ang))
        e = (0, math.cos(ang), math.sin(ang))
        _blade(bl, tips, d, e, (side, 0, 0), R * .12, R, chord, t, pitch=.2, stripe=R * .16, tip=R * .08, droop=0)
    if hd.on(a):
        links = a.part('Tail_rotor_links', 'Steel', tr)
        for j in range(blades):
            ang = phase + j * TAU / blades + .35
            tipv = Vector((side * .03, -math.sin(ang) * R * .15, math.cos(ang) * R * .15))
            links.limb((side * .09, 0, 0), tuple(tipv), .016, .016, bevel=0)


# ----------------------------------------------------------------------------- engines
def jet_nozzle(a, x, y, z, r, length, seg=12, glow=True):
    """Afterburning nozzle from y (root buried) rearwards, a drop-in for mb_air._nozzle: a turned shroud with a worn
    lip, a ring of overlapping converging petals whose pointed tips give the serrated rim, a deep dark liner and the
    glowing flame holder."""
    L = length
    k.lathe(a.part('Nozzles', 'Steel'), [(r * 1.04, -.15), (r, L * .3), (r * .95, L * .45), (r * .9, L * .45),
                                         (r * .9, L * .3)], loc=(x, y, z), rot=BACKWARD, seg=seg, worn=(2,),
            caps=(True, False))
    petals = a.part('Nozzle_petals', 'Armor')
    n = seg
    for i in range(n):
        u = (i + .5) * TAU / n
        c, s = math.cos(u), math.sin(u)
        w = TAU * r * .94 / n * .62
        # A tapered petal from radius .96 r at L*.42 to .84 r at L, standing out of the shroud.
        p0 = Vector((x + c * r * .955, y + L * .42, z + s * r * .955))
        p1 = Vector((x + c * r * .85, y + L, z + s * r * .85))
        tang = (p1 - p0).normalized()
        nrm = Vector((c, 0, s))
        side = tang.cross(nrm).normalized()
        L1 = (p1 - p0).length
        prof = [(-w, 0), (w, 0), (w * .75, L1 * .92), (0, L1 + .02), (-w * .75, L1 * .92)]
        start = len(petals.bm.verts)
        k.extrude(petals, prof, .014, axis='Z')
        petals.bm.verts.ensure_lookup_table()
        m = Matrix((side, tang, nrm)).transposed().to_4x4()
        m.translation = p0
        bmesh.ops.transform(petals.bm, matrix=m, verts=list(petals.bm.verts)[start:])
    k.lathe(a.part('Nozzle_liners', 'Undercarriage'), [(r * .84, L - .02), (r * .74, L * .55), (r * .5, L * .5),
                                                       (0, L * .5)], loc=(x, y, z), rot=BACKWARD, seg=seg,
            caps=(False, False))
    if glow:
        g = a.part('Exhaust_glow', 'Alloy')
        g.torus(r * .45, r * .07, loc=(x, y + L * .5 + .02, z), rot=FORWARD, seg=seg, ring=4)
        g.cyl(r * .16, .04, loc=(x, y + L * .5 + .03, z), rot=FORWARD, seg=8, bevel=0)


def engine_bell(shell, bands, glow, loc, r, length, rot=BACKWARD, seg=18, bell=1.0, throat=.86):
    """A spacecraft engine: a turned bell or round ion engine from loc along local +Z (default rearwards): the shroud
    with a cooling band step and a worn lip, the glowing face set deep in a dark-lined throat (bands)."""
    L = length
    k.lathe(shell, [(r * bell, 0), (r * bell, L * .62), (r * bell * 1.04, L * .66), (r * bell * 1.04, L * .74),
                    (r * bell, L * .78), (r * bell, L), (r * throat, L), (r * throat, L * .7)],
            loc=loc, rot=rot, seg=seg, worn=(2, 5), caps=(True, False))
    k.lathe(bands, [(r * throat, L * .7), (r * throat * .92, L * .35), (0, L * .35)], loc=loc, rot=rot, seg=seg,
            caps=(False, False))
    m = hd.frame(loc, rot)
    glow.cyl(r * throat * .8, .03, loc=tuple(m @ Vector((0, 0, L * .36 + .02))), rot=rot, seg=seg, bevel=0)


def engine_nacelle(body, dark, loc, r, length, rot=FORWARD, seg=10):
    """A turboshaft nacelle along local +Z from its exhaust end at loc to the intake: a turned cowling with a worn
    seam ring and an intake lip round a dark recessed face."""
    L = length
    k.lathe(body, [(r * .8, 0), (r * .96, .04), (r, .12), (r, L * .55), (r * 1.03, L * .57), (r * 1.03, L * .61),
                   (r, L * .63), (r, L - .06), (r * .9, L), (r * .72, L)], loc=loc, rot=rot, seg=seg, worn=(4, 8),
            caps=(True, False))
    k.lathe(dark, [(r * .72, L), (r * .7, L - .06), (r * .3, L - .08), (0, L - .06)], loc=loc, rot=rot, seg=seg,
            caps=(False, False))


# ----------------------------------------------------------------------------- stores
def pylon(part, x, y0, y1, ztop, zbot, w=.08):
    """Store pylon from the skin (ztop, buried) down to zbot, chord y0..y1, a drop-in for mb_air._pylon: the same
    streamlined profile with rounded corners and chamfered faces, and sway-brace pads at its foot."""
    prof = [(y0 + .12, ztop), (y0, zbot + .04), (y0 + .1, zbot), (y1 - .15, zbot), (y1, ztop)]
    k.extrude(part, prof, w, loc=(x, 0, 0), axis='X', chamfer=min(.012, w * .2), corner=.015)
    span = y1 - y0
    for f in (.3, .65):
        k.block(part, (w * 2.2, .05, .04), loc=(x, y0 + span * f, zbot + .01), chamfer=.008)


def launch_rail(part, x, y0, y1, z, w=.1, h=.08):
    """Missile launch rail under a pylon or a wingtip, y0..y1, its top at z: a chamfered profile with a tapered
    nose."""
    k.extrude(part, [(y0 + .1, z), (y0, z - h * .6), (y0 + .05, z - h), (y1 - .02, z - h), (y1, z)], w,
              loc=(x, 0, 0), axis='X', chamfer=min(.01, w * .2), corner=.012)


def hellfire_rack(a, x, y, z, s, rows=(.66, .52), cols=(1.02, 1.14), length=.66, r=.045, detail=False):
    """Four-round Hellfire launcher (M299 class) on side s: a rack beam with the rails, the missiles (seekers, bands
    and fins at high detail)."""
    from mb_air import _hellfire
    rack = a.part('Armor', 'Armor')
    k.block(rack, (.05, .56, .3), loc=(s * (cols[0] + cols[1]) / 2, y + .3, (rows[0] + rows[1]) / 2), chamfer=.012)
    for cx in cols:
        k.block(rack, (.045, .6, .03), loc=(s * cx, y + .3, rows[0] + r + .012), chamfer=.006)
    for cx in cols:
        for cz in rows:
            if detail:
                _hellfire(a, s * cx, y, cz, length=length, r=r, fins=cx > 1.1)
            else:
                k.lathe(a.part('Missiles', 'Fuel'), [(r * .9, .06), (r, .1), (r, length * .97), (r * .8, length)],
                        loc=(s * cx, y, cz), rot=BACKWARD, seg=6, caps=(False, True))
                k.lathe(a.part('Missile_seekers', 'Glass'), [(0, 0), (r * .6, .03), (r * .9, .07)],
                        loc=(s * cx, y, cz), rot=BACKWARD, seg=6, caps=(False, False))


def rocket_pod(a, x, y, z, r, length, s, seg=10):
    """A 19-shot rocket pod nose forward at y (body along +Y): one turned body with a worn nose ring, the tube face
    recessed into it (dark, its tube mouths drawn as a ring of bores) and the hazard band."""
    k.lathe(a.part('Pods', 'Armor'), [(r * .56, .0), (r * .82, .02), (r * .95, .06), (r, .2), (r, length * .62),
                                      (r * .83, length * .9), (r * .55, length)],
            loc=(x, y, z), rot=BACKWARD, seg=seg, worn=(2,), caps=(False, True))
    k.lathe(a.part('Pod_face', 'Undercarriage'), [(r * .56, .0), (r * .5, .04), (0, .04)], loc=(x, y, z), rot=BACKWARD,
            seg=seg, caps=(False, False))
    a.part('Pod_bands', 'Hazard').cyl(r * 1.05, .04, loc=(x, y + .14, z), rot=FORWARD, seg=seg, bevel=0)


# ----------------------------------------------------------------------------- canopies
def canopy(glass, frame, sections, sill=.04, bows=(), bow_r=.022, sills=(0, -1), arch=None):
    """Glass loft through `sections` (rings over the crown from sill to sill: mb_air._dome, or _bubble with
    sills=(1, 0) and arch=(1, 2, 3, 4, 5, 0)), with a sill frame swept round its base (`sill` wide, 0 for none) and
    frame bows swept over the sections listed in `bows` (indices). sills: the right and left sill points' indices
    in a section; arch: the order of a section's points from one sill over the crown to the other."""
    glass.loft(sections, bevel=0)
    if sill > 0:
        right = [Vector(sc[sills[0]]) for sc in sections]
        left = [Vector(sc[sills[1]]) for sc in sections]
        k.sweep(frame, [(-sill / 2, -.012), (sill / 2, -.012), (sill / 2, .022), (-sill / 2, .022)],
                [tuple(p) for p in right + left[::-1]], closed=True, up=(0, 0, 1))
    for i in bows:
        sc = sections[i]
        order = arch or range(len(sc))
        k.sweep(frame, [(-bow_r, -bow_r * .5), (bow_r, -bow_r * .5), (bow_r, bow_r), (-bow_r, bow_r)],
                [tuple(sc[j]) for j in order])
