"""Prompt 35 pass 1: the parametric detail library (DECISIONS "Prompt 35").

frontier_kit has the primitives (box, cyl, sphere, loft); mb_kit27 the chamfered ones (block, extrude, lathe, ring,
sweep, inset, mirrored); mb_parts27 the prompt 27 sub-assemblies (road wheels, sprockets, tracks, hatches, barrels,
the pintle MG, smoke launchers, rotor heads, nozzles, pylons, canopies). This module adds the rest of prompt 35
section 3 as functions with real-size defaults, chamfered big edges, standard part names and variants, and the
COLOR_0 effects the bake does not do (soot, local dust, part tone). Each model is still its own script (prompt 35
section 1): a builder calls these with its own parameters, never another model's builder.

Conventions are frontier_kit's: metres, +Z up, Blender -Y is the front, +X the vehicle's left. `a` is a
frontier_kit.Asset, `part` / `shape` a frontier_kit.Shape (a.part(name, material, parent)). Functions that make
several materials take `a` and a `parent` pivot; part names are the KIT names below (the quality gate's KIT_PIECE
pattern lets them repeat across models). Small repeated pieces are plain (no chamfer: it would not show) and sink
1 cm into what they sit on; big pieces get the two-step chamfer that marks worn edges for the bake.

Tier 3 detail (bolts, rivets, hinges, handles, cables, lamps) is always built here: prompt 35 wants it at LOD0 on
every model, not only on the `_hd` twins (the runtime builds LOD1 / the impostor itself).

Index (section 3 of the prompt):
  general   chamfer_box, panel, rivet_line, bolt_ring, weld, hinge, handle, hatch_round, hatch_rect, lamp, whip_antenna,
            mesh_antenna, dish, periscope, tow_hook, tow_cable, crate, jerrycan, backpack, net_roll, grille, exhaust
  tracked   detail (context), road_wheel, sprocket, idler, return_roller, tracks, side_skirt, fender, turret_ring,
            gun_barrel, roof_mg, pintle_mg, smoke_dischargers, era_bricks, slat_cage, net_armour
  wheeled   truck_wheel, tread_wheel, axle, leaf_spring, windscreen, mirror, outrigger
  aircraft  wing, fin, intake, missile, bomb, drop_tank, flare_dispenser, blade_antenna, landing_gear, pylon
  heli      rotor_head, tail_rotor, skids, stub_wing
  ship      ship_hull, railing, ladder, vls, ciws, rhib, radar_mast
  rail      rail_track, bogie
  structure footing, sandbag_wall, wire_fence, hesco, t_wall, floodlight, door, beacon (style 'accord' / 'hegemon')
  boss      armour_plate, breakable_panel, fuel_drum, smokestack, gun_cluster
  colour    soot, dust, tone, team_band (COLOR_0 effects applied after the bake)
"""
import contextlib
import math
import random

from mathutils import Matrix, Vector

import frontier_kit as kit
import mb_detail as hd
import mb_kit27 as k
import mb_parts27 as p27

R90 = math.pi / 2
TAU = math.tau
FORWARD = (R90, 0, 0)    # local +Z -> -Y (the front)
BACKWARD = (-R90, 0, 0)  # local +Z -> +Y
UP = (0, 0, 0)

# Part names the library writes (the quality gate treats these as kit components).
KIT = dict(bolts='Kit_bolts', rivets='Kit_rivets', welds='Kit_welds', hinges='Kit_hinges', handles='Kit_handles',
           lamps='Lamps', lamp_rims='Lamp_rims', antennas='Antennas', glass='Glass', cables='Kit_cables',
           stowage='Stowage', straps='Kit_straps', grille='Grilles', exhaust='Exhaust', soot='Exhaust_soot',
           tyres='Tyres', wheels='Wheels', hubs='Hubs', nuts='Wheel_nuts', axles='Axles', skirts='Skirts',
           era='Era_bricks', slats='Slat_armour', rails='Railings', ladders='Ladders', sandbags='Sandbags',
           fence='Kit_fence', concrete='Base')


def rot_to(normal, roll=0.0):
    """Euler turning local +Z towards `normal`, local +Y towards world up (or towards +Y when `normal` is vertical),
    so a wall fitting stands upright: local X is across, local Y up the wall. `roll` turns it about the normal."""
    z = Vector(normal).normalized()
    up = Vector((0, 0, 1)) if abs(z.z) < .9 else Vector((0, 1, 0))
    y = (up - z * up.dot(z)).normalized()
    x = y.cross(z)
    m = Matrix((x, y, z)).transposed()
    if roll:
        m = m @ Matrix.Rotation(roll, 3, 'Z')
    return m.to_euler('XYZ')


def frame(loc, rot=UP):
    return hd.frame(loc, rot)


def _at(m, p):
    return tuple(m @ Vector(p))


# ============================================================================= general
def chamfer_box(shape, size, loc=(0, 0, 0), rot=UP, c=None, taper=(1, 1)):
    """A big block centred at loc, chamfered on every edge (both ends): c defaults to 6 % of its smallest side,
    1.5-12 cm. (mb_kit27.block, like this, centres the block on loc.)"""
    c = c if c is not None else max(.015, min(.12, .06 * min(size)))
    return k.block(shape, size, loc=loc, rot=rot, chamfer=c, taper=taper, ends=(True, True))


def plate(shape, size, loc=(0, 0, 0), rot=UP, chamfer=.012):
    """A thin plate centred at loc with its edges chamfered all round (mb_kit27.block leaves blocks under 12 cm
    plain; a skirt, a door leaf or an ERA brick still wants its worn rim)."""
    sx, sy, sz = size
    c = min(chamfer, sz * .35, sx * .2, sy * .2)
    return k.extrude(shape, [(-sx / 2, -sy / 2), (sx / 2, -sy / 2), (sx / 2, sy / 2), (-sx / 2, sy / 2)], sz,
                     loc=loc, rot=rot, axis='Z', chamfer=c, corner=c)


def name(base, i):
    """The i-th runtime name of a series (base, base__001, ...): written with '__' so the kit's duplicate check
    passes, renamed to base.001 after the finish (suffixed(a) is installed on first use)."""
    return base if i == 0 else f'{base}__{i:03d}'


def suffixed(a):
    """Wrap a.finish so pivots written base__NNN are renamed base.NNN after the kit's checks (idempotent)."""
    if getattr(a, '_suffixed35', False):
        return
    a._suffixed35 = True
    original = a.finish

    def finish():
        out = original()
        for o in list(a.collection.objects):
            if '__' in o.name:
                want = o.name.replace('__', '.')
                o.name = want
                if o.name != want:
                    raise ValueError(f'{a.name}: could not name {want} (got {o.name})')
        return out
    a.finish = finish


def panel(a, part, size, loc, normal, t=.03, rivet=.18, parent=None, mat_rivets='Steel', r=.016, seg=6):
    """A bolted-on plate (w x h, t thick) lying on a surface at loc facing `normal`, with a rivet row round its
    border every `rivet` metres (0: none)."""
    rot = rot_to(normal)
    m = frame(loc, rot)
    w, h = size
    plate(part, (w, h, t), loc=_at(m, (0, 0, t / 2 - .005)), rot=rot)
    if rivet:
        rv = a.part(KIT['rivets'], mat_rivets, parent)
        e = .05
        corners = [(-w / 2 + e, -h / 2 + e), (w / 2 - e, -h / 2 + e), (w / 2 - e, h / 2 - e), (-w / 2 + e, h / 2 - e)]
        for (x0, y0), (x1, y1) in zip(corners, corners[1:] + corners[:1]):
            n = max(1, int(math.hypot(x1 - x0, y1 - y0) / rivet))
            for i in range(n):
                f = i / n
                hd.bolt(rv, _at(m, (x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, t - .004)), rot=rot, r=r, h=r * 1.25,
                        seg=seg)


def rivet_line(part, p0, p1, normal, pitch=.2, r=.018, h=.022, seg=6):
    p0, p1 = Vector(p0), Vector(p1)
    n = max(1, int((p1 - p0).length / pitch))
    rot = rot_to(normal)
    for i in range(n + 1):
        hd.bolt(part, tuple(p0 + (p1 - p0) * (i / n)), rot=rot, r=r, h=h, seg=seg)


def bolt_ring(part, loc, normal, R, n, r=.02, h=.025, phase=0.0):
    hd.bolt_ring(part, frame(loc, rot_to(normal)), R, n, r=r, h=h, phase=phase)


def weld(part, points, r=.016):
    """A weld bead along a polyline (a flattened hexagon swept)."""
    prof = [(math.cos(u) * r, math.sin(u) * r * .6) for u in (i * TAU / 6 for i in range(6))]
    k.sweep(part, prof, points)


def hinge(part, p0, p1, r=.03, knuckles=3):
    hd.hinge(part, p0, p1, r=r, knuckles=knuckles, seg=8)


def handle(part, p0, p1, up, h=.07, r=.014):
    hd.handle(part, p0, p1, up, h=h, r=r)


def hatch_round(a, loc, r=.4, parent=None, mat='Armor', hinge_dir=1, periscopes=2, seg=14):
    """A round hatch with its raised coaming (vành), a domed lid, the hinge barrel, a grab handle, a bolt ring and
    `periscopes` vision blocks round the coaming."""
    x, y, z = loc
    lid = a.part('Hatches', mat, parent)
    steel = a.part('Hatch_fittings', 'Steel', parent)
    k.ring(lid, [(r * .98, -.02), (r * 1.15, -.02), (r * 1.15, .04), (r * 1.0, .06)], loc=loc, seg=seg, worn=(2,))
    k.lathe(lid, [(0, .1), (r * .7, .097), (r * .9, .087), (r * .97, .065), (r * .97, .01)], loc=loc, seg=seg,
            worn=(2,))
    k.lathe(steel, [(.036, -r * .45), (.036, r * .45)], loc=(x, y + hinge_dir * (r + .05), z + .05), rot=(0, R90, 0),
            seg=6)
    hd.bolt_ring(steel, frame((x, y, z + .09)), r * .78, 8, r=.014, h=.02, phase=.2)
    hy = y - hinge_dir * r * .3
    handle(steel, (x - r * .35, hy, z + .09), (x + r * .35, hy, z + .09), (0, 0, 1), h=.06)
    glass = a.part(KIT['glass'], 'Glass', parent)
    for i in range(periscopes):
        u = math.radians(-60 + 120 * i / max(1, periscopes - 1)) if periscopes > 1 else 0.0
        px, py = x + math.sin(u) * r * 1.3, y - math.cos(u) * r * 1.3
        k.block(lid, (.16, .12, .12), loc=(px, py, z - .02), rot=(0, 0, u), chamfer=0)
        glass.box((.13, .02, .06), loc=(px - math.sin(u) * .06, py - math.cos(u) * .06 + .0, z + .05),
                  rot=(0, 0, u), bevel=0)


def hatch_rect(a, loc, size=(.7, .9), normal=(0, 0, 1), parent=None, mat='Armor'):
    """A rectangular hatch or access door: coaming frame, lid with a raised panel, two hinges, a handle."""
    w, h = size
    rot = rot_to(normal)
    m = frame(loc, rot)
    lid = a.part('Hatches', mat, parent)
    steel = a.part('Hatch_fittings', 'Steel', parent)
    outline = [(-w / 2 - .04, -h / 2 - .04), (w / 2 + .04, -h / 2 - .04), (w / 2 + .04, h / 2 + .04),
               (-w / 2 - .04, h / 2 + .04)]
    start = len(lid.bm.verts)
    lid.shell(outline, .05, .05, floor=None)
    import bmesh
    lid.bm.verts.ensure_lookup_table()
    bmesh.ops.transform(lid.bm, matrix=m, verts=list(lid.bm.verts)[start:])
    plate(lid, (w - .02, h - .02, .04), loc=_at(m, (0, 0, .005)), rot=rot)
    k.block(lid, (w * .7, h * .7, .025), loc=_at(m, (0, 0, .04)), rot=rot, chamfer=.008)
    for s in (-1, 1):
        hinge(steel, _at(m, (s * w * .3 - .08, h / 2 + .03, .04)), _at(m, (s * w * .3 + .08, h / 2 + .03, .04)),
              r=.022, knuckles=2)
    handle(steel, _at(m, (-w * .2, -h * .32, .065)), _at(m, (w * .2, -h * .32, .065)), Vector(normal), h=.05)


def lamp(a, loc, facing=(0, -1, 0), r=.09, parent=None, guard=True, mat='Armor', glow='Lamp'):
    """A head / work lamp: a turned housing, the lit lens (Lamp, or LavaGlow for tail lamps) and a wire guard."""
    rot = rot_to(facing)
    m = frame(loc, rot)
    k.lathe(a.part(KIT['lamp_rims'], mat, parent), [(r * .7, -.06), (r * 1.08, -.03), (r * 1.15, .02), (r, .03)],
            loc=loc, rot=rot, seg=10, worn=(2,))
    a.part(KIT['lamps'], glow, parent).cyl(r * .92, .02, loc=_at(m, (0, 0, .03)), rot=rot, seg=10, bevel=0)
    if guard:
        g = a.part('Lamp_guards', 'Steel', parent)
        for dx in (-r * .45, 0, r * .45):
            g.tube([_at(m, (dx, -r * 1.05, .02)), _at(m, (dx, -r * .9, .1)), _at(m, (dx, r * .9, .1)),
                    _at(m, (dx, r * 1.05, .02))], .007, seg=4)


def whip_antenna(part, loc, h=1.6, r=.022, lean=0.0):
    """A whip antenna on its spring base: a turned base, a spring collar, a tapering mast (at least 2 cm: a thinner
    whip shimmers at RTS distance) with a ball tip; `lean` tilts it back (radians)."""
    rot = (lean, 0, 0)
    k.lathe(part, [(r * 3, -.02), (r * 3, .05), (r * 1.8, .09), (r * 1.8, .16), (r * 1.2, .18), (r * .9, h),
                   (r * 1.5, h + .02), (0, h + .05)], loc=loc, rot=rot, seg=6, worn=(1,))


def mesh_antenna(part, loc, w=.6, h=.5, normal=(0, -1, 0), bars=4):
    """A flat grid antenna: a frame and crossing bars on a mast stub."""
    rot = rot_to(normal)
    m = frame(loc, rot)
    for i in range(bars + 1):
        f = -0.5 + i / bars
        part.box((w, .025, .025), loc=_at(m, (0, f * h, 0)), rot=rot, bevel=0)
        part.box((.025, h, .025), loc=_at(m, (f * w, 0, 0)), rot=rot, bevel=0)
    part.cyl(.03, .3, loc=_at(m, (0, -h / 2 - .15, -.05)), rot=(rot[0] + R90, rot[1], rot[2]), seg=6, bevel=0)


def dish(part, feed_part, loc, r=.5, normal=(0, -1, 0), depth=None, seg=16):
    """A parabolic dish facing `normal`: the reflector (lathe), a rim, the feed horn on three struts."""
    depth = depth if depth is not None else r * .35
    rot = rot_to(normal)
    m = frame(loc, rot)
    prof = [(0, 0)] + [(r * f, depth * f * f) for f in (.35, .7, 1.0)] + [(r * 1.04, depth + .01), (r * 1.0, depth + .03)]
    k.lathe(part, prof, loc=loc, rot=rot, seg=seg, caps=(False, True), worn=(4,))
    tip = _at(m, (0, 0, depth + r * .55))
    feed_part.cyl(r * .08, r * .12, loc=tip, rot=rot, seg=8, bevel=0)
    for i in range(3):
        u = i * TAU / 3
        feed_part.tube([_at(m, (math.cos(u) * r * .92, math.sin(u) * r * .92, depth * .9)), tip], .012, seg=4)


def periscope(a, loc, facing=(0, -1, 0), parent=None, size=(.18, .16, .14), mat='Armor'):
    """A sight / periscope head: an armoured box on a turned collar, its glass face towards `facing`, a small hood."""
    w, d, h = size
    yaw = math.atan2(facing[0], -facing[1])
    rot = (0, 0, yaw)
    m = frame(loc, rot)
    k.lathe(a.part('Sight', mat, parent), [(w * .55, -.02), (w * .55, .04), (w * .45, .06)], loc=loc, seg=10)
    k.block(a.part('Sight', mat, parent), (w, d, h), loc=_at(m, (0, 0, .05 + h / 2)), rot=rot, chamfer=.02)
    a.part(KIT['glass'], 'Glass', parent).box((w * .8, .02, h * .55), loc=_at(m, (0, -d / 2 - .005, .05 + h * .5)),
                                              rot=rot, bevel=0)
    a.part('Sight', mat, parent).box((w * 1.05, .06, .02), loc=_at(m, (0, -d / 2 - .02, .05 + h * .93)), rot=rot,
                                     bevel=0)


def tow_hook(part, loc, facing=(0, -1, 0), size=.12):
    """A towing eye: a base plate and a hook loop standing out along `facing`."""
    rot = rot_to(facing)
    m = frame(loc, rot)
    part.box((size * 2, size * 1.4, .03), loc=_at(m, (0, 0, .01)), rot=rot, bevel=0)
    pts = [_at(m, (0, -size * .45, 0)), _at(m, (0, -size * .45, size * .8)), _at(m, (0, 0, size * 1.1)),
           _at(m, (0, size * .45, size * .8)), _at(m, (0, size * .45, 0))]
    part.tube(pts, size * .16, seg=6)


def tow_cable(part, points, r=.025, eyes=True):
    """A steel tow cable along a polyline with an eye loop at each end."""
    part.tube(points, r, seg=6)
    if eyes:
        for end, nxt in ((points[0], points[1]), (points[-1], points[-2])):
            e, n = Vector(end), Vector(nxt)
            d = (e - n).normalized()
            part.torus(r * 3, r * .8, loc=tuple(e + d * r * 3), rot=rot_to(d.cross(Vector((0, 0, 1))) or (1, 0, 0)),
                       seg=8, ring=4)


def crate(part, band, size, loc, rot=UP, bands=2):
    """An ammunition / stowage crate standing on loc: a chamfered box, its lid line, metal bands and rope handles."""
    w, d, h = size
    m = frame(loc, rot)
    k.block(part, size, loc=_at(m, (0, 0, h / 2)), rot=rot, chamfer=min(.02, min(size) * .12))
    band.box((w + .01, d * .98, .02), loc=_at(m, (0, 0, h * .82)), rot=rot, bevel=0)
    for i in range(bands):
        f = -0.5 + (i + 1) / (bands + 1)
        band.box((.03, d + .012, h + .01), loc=_at(m, (f * w, 0, h / 2)), rot=rot, bevel=0)
    for s in (-1, 1):
        band.box((.03, d * .3, .03), loc=_at(m, (s * (w / 2 + .012), 0, h * .6)), rot=rot, bevel=0)


def jerrycan(part, loc, rot=UP, scale=1.0):
    """A 20-litre jerrycan, 0.165 x 0.345 x 0.47 m: the body with the X pressing, the triple handle and the cap."""
    w, d, h = .165 * scale, .345 * scale, .47 * scale
    m = frame(loc, rot)
    k.block(part, (w, d, h * .9), loc=_at(m, (0, 0, h * .45)), rot=rot, chamfer=.015 * scale)
    for s in (-1, 1):
        part.box((.012, d * .9, .02 * scale), loc=_at(m, (s * w / 2, 0, h * .45)), rot=(rot[0] + s * .62, rot[1], rot[2]),
                 bevel=0)
    part.box((w * .5, d * .55, .05 * scale), loc=_at(m, (0, .03 * scale, h * .93)), rot=rot, bevel=0)
    part.cyl(.022 * scale, .04 * scale, loc=_at(m, (0, -d * .38, h * .95)), rot=(rot[0] - .6, rot[1], rot[2]), seg=6,
             bevel=0)


def backpack(part, strap, size, loc, rot=UP):
    """A kit bag / rucksack: a rounded block with a flap and two straps."""
    w, d, h = size
    m = frame(loc, rot)
    k.block(part, size, loc=_at(m, (0, 0, h / 2)), rot=rot, chamfer=min(size) * .25)
    k.block(part, (w * 1.02, d * .6, h * .3), loc=_at(m, (0, -d * .15, h * .75)), rot=rot, chamfer=min(size) * .12)
    for s in (-1, 1):
        strap.box((.04, d + .02, h * 1.02), loc=_at(m, (s * w * .28, 0, h * .5)), rot=rot, bevel=0)


def net_roll(part, strap, loc, length=1.6, r=.16, axis='X'):
    """A rolled camouflage net: a ten-sided roll with three straps round it."""
    rot = (0, R90, 0) if axis == 'X' else (R90, 0, 0)
    m = frame(loc, rot)
    k.lathe(part, [(r * .7, -length / 2), (r, -length / 2 + .04), (r * 1.03, 0), (r, length / 2 - .04),
                   (r * .7, length / 2)], loc=loc, rot=rot, seg=10)
    for f in (-.33, 0, .33):
        strap.cyl(r * 1.06, .045, loc=_at(m, (0, 0, f * length)), rot=rot, seg=10, bevel=0)


def grille(a, loc, w, h, facing=(0, -1, 0), slats=6, parent=None, frame_mat='Armor'):
    """A radiator / engine grille: a chamfered frame and angled slats in a dark recess."""
    rot = rot_to(facing)
    m = frame(loc, rot)
    fr = a.part('Grille_frames', frame_mat, parent)
    for s in (-1, 1):
        fr.box((.06, h + .06, .06), loc=_at(m, (s * (w / 2 + .03), 0, .02)), rot=rot, bevel=0)
        fr.box((w + .12, .06, .06), loc=_at(m, (0, s * (h / 2 + .03), .02)), rot=rot, bevel=0)
    g = a.part(KIT['grille'], 'Undercarriage', parent)
    g.box((w, h, .02), loc=_at(m, (0, 0, -.03)), rot=rot, bevel=0)
    for i in range(slats):
        y = -h / 2 + (i + .5) * h / slats
        sm = m @ hd.frame((0, y, 0), (math.radians(35), 0, 0))
        g.box((w * .98, h / slats * .9, .015), loc=tuple(sm.to_translation()), rot=tuple(sm.to_euler('XYZ')), bevel=0)


def exhaust(a, loc, r=.06, length=.6, direction=(0, 0, 1), parent=None, muffler=True, cap=True):
    """An exhaust stack: a muffler can with a perforated heat shield, the pipe, a rain cap (or a cut end), and soot
    on the paint round its mouth (COLOR_0)."""
    rot = rot_to(direction)
    m = frame(loc, rot)
    pipe = a.part(KIT['exhaust'], 'Steel', parent)
    k.lathe(pipe, [(r, 0), (r, length), (r * 1.15, length + .01), (r * 1.15, length + .03), (r * .8, length + .03),
                   (r * .8, length - .05), (0, length - .05)], loc=loc, rot=rot, seg=8, worn=(2,))
    if muffler:
        k.lathe(a.part('Exhaust_mufflers', 'Armor', parent), [(r * 1.4, length * .08), (r * 2.2, length * .14),
                                                              (r * 2.2, length * .5), (r * 1.4, length * .56)],
                loc=loc, rot=rot, seg=10, worn=(1, 2))
        sh = a.part('Exhaust_shields', 'MetalSheet', parent)
        for i in range(4):
            u = i * TAU / 8 - TAU / 16
            sh.box((r * 1.4, .012, length * .38), loc=_at(m, (math.cos(u) * r * 2.35, math.sin(u) * r * 2.35,
                                                             length * .32)), rot=(rot[0], rot[1], rot[2] + u + R90),
                   bevel=0)
    if cap:
        a.part('Exhaust_caps', 'Steel', parent).box((r * 2.6, r * 2.6, .012), loc=_at(m, (r * .4, 0, length + .1)),
                                                    rot=(rot[0], rot[1] + .5, rot[2]), bevel=0)
    soot(a, _at(m, (0, 0, length)), radius=max(.35, r * 6), k=.45)


# ============================================================================= tracked running gear and turret
@contextlib.contextmanager
def detail(a):
    """Turn mb_parts27's / mb_detail's high-detail extras on inside the block (prompt 35: tier 3 detail at LOD0)."""
    old = getattr(a, 'hd', False)
    a.hd = True
    try:
        yield a
    finally:
        a.hd = old


def road_wheel(a, centre, r, width, s, seg=12, disc_mat='Team'):
    with detail(a):
        p27.road_wheel(a, centre, r, width, s, seg=seg, disc_mat=disc_mat)


def sprocket(a, centre, r, teeth, width, s):
    with detail(a):
        p27.sprocket(a, centre, r, teeth, width, s)


def idler(a, centre, r, width, s, seg=12):
    with detail(a):
        p27.idler(a, centre, r, width, s, seg=seg)


def return_roller(a, centre, r, width, s):
    """A track return roller: a rubber-rimmed small wheel with a hub on a stub axle out of the hull side."""
    x, y, z = centre
    k.lathe(a.part('Rollers', 'Undercarriage'), [(r * .7, -width / 2), (r, -width / 2 + .015), (r, width / 2 - .015),
                                                  (r * .7, width / 2)], loc=centre, rot=p27.side_rot(s), seg=8)
    a.part(KIT['hubs'], 'Steel').cyl(r * .35, width + .04, loc=centre, rot=p27.side_rot(s), seg=6, bevel=0)


def tracks(a, x, length, top, wheel_r, wheels, belt_width, sprocket_end=1, cleat_pitch=.18, teeth=9, rollers=3):
    """Both track units (mb_parts27.track_unit) with the high-detail return rollers, sprocket teeth and cleats."""
    with detail(a):
        p27.track_unit(a, x, length, top, wheel_r, wheels, belt_width, sprocket_end=sprocket_end,
                       cleat_pitch=cleat_pitch, wheel_seg=12, teeth=teeth, return_rollers=rollers)


def side_skirt(a, x, y0, y1, ztop, h, s, panels=4, t=.04, mat='Team', parent=None, hinged=True, bolts=True):
    """Side skirts on side s: `panels` plates with a hinge line along the top, bolt rows, a rubber lower flap and a
    worn chamfer (each plate its own block, a little gap between). `bolts=False` (wave 2, lane B's request) leaves
    the four bolts a panel out (about 80 triangles a panel); the default keeps them."""
    part = a.part(KIT['skirts'], mat, parent)
    rub = a.part('Skirt_flaps', 'Rubber', parent)
    steel = a.part(KIT['hinges'], 'Steel', parent)
    L = (y1 - y0) / panels
    for i in range(panels):
        yc = y0 + (i + .5) * L
        plate(part, (L - .03, h, t), loc=(s * x, yc, ztop - h / 2), rot=(R90, 0, R90), chamfer=.015)
        rub.box((t * .6, L - .05, .12), loc=(s * x, yc, ztop - h - .05), bevel=0)
        if hinged:
            hinge(steel, (s * (x + t / 2 + .01), yc - L * .3, ztop - .04), (s * (x + t / 2 + .01), yc + L * .3,
                                                                           ztop - .04), r=.022, knuckles=3)
        if bolts:
            hd.bolt_line(steel, (s * (x + t / 2), yc - L * .4, ztop - h * .55), (s * (x + t / 2), yc + L * .4,
                                                                               ztop - h * .55), 4,
                         rot=hd.side_rot(s), r=.016, h=.02)


def fender(part, x, y0, y1, z, w, s, lip=.04):
    """A track / wheel fender on side s from y0 to y1 at height z, w wide, with a turned-down outer lip."""
    k.block(part, (w, y1 - y0, .03), loc=(s * x, (y0 + y1) / 2, z - .03), chamfer=0)
    part.box((.025, y1 - y0, lip + .03), loc=(s * (x + w / 2), (y0 + y1) / 2, z - lip / 2 - .015), bevel=0)


def turret_ring(part, loc, r, h=.12):
    """The turret race collar: a stepped ring round the turret base."""
    k.ring(part, [(r * .96, -.02), (r * 1.06, -.02), (r * 1.06, h * .6), (r * 1.02, h), (r * .96, h)], loc=loc,
           seg=24, worn=(3,))


def gun_barrel(a, name, parent, x, y0, z, length, r, seg=14, extractor=(.4, 1.6, .5), brake_name='Muzzle_brake',
               brake='baffle', sleeve=1.22):
    """mb_parts27.barrel: collar, thermal sleeve with clamps, fume extractor, the muzzle brake."""
    p27.barrel(a, name, parent, x, y0, z, length, r, seg=seg, sleeve=sleeve, extractor=extractor,
               brake_name=brake_name, brake=brake)


def roof_mg(a, parent, loc, length=.9, shield=True):
    """mb_parts27.mg_mount with its high-detail feed cover, rails and belt: Mount_mg + Muzzle_mg."""
    with detail(a):
        p27.mg_mount(a, parent, loc, length=length, shield=shield)


def pintle_mg(a, parent, loc, index=0, scale=1.0, slot='mg', shield=True, length=1.1, post=0.0, riser=0.0,
              ring_r=.36, cradle=None):
    """A pintle machine gun on its own yaw pivot `Mount_<slot>` (index 1, 2 ...: `Mount_<slot>.001` ...), sized by
    `scale` (1 = a 12.7 mm gun on a tank roof; a boss uses 1.6-2): a turned pintle, the receiver with its sloped feed
    cover and spade grips, the barrel with its carrying handle and flash hider, the ammunition can, a shield.
    `Muzzle_<slot>[.NNN]` at the barrel's tip. Pivots are named through name() / suffixed() (added in the pilot:
    mb_parts27.mg_mount names only one gun).
    `post` (metres; wave 1, the owner's roof-gun rule in MODEL_STANDARD): the gun stands on a fixed pintle post that
    high (a base plate with gussets, the column, a collar) with the mount pivot on its top, and gets a cradle (side
    plates, a trunnion pin) round the receiver, so it stands clear of the roof line at the battle camera's distance.
    The default 0 builds the pilot's gun unchanged.
    `riser` (metres; wave 2, lane B's request, the whole roof-gun rule in one call): a riser collar under the
    post (an M66-class ring of radius `ring_r` x scale on its collar, the rail on top, four brackets), as on a
    hatch ring; the post (or, with post 0, the mount itself) stands on its top. `cradle` builds the cradle
    round the receiver (default: whenever there is a post or a riser). Defaults keep today's geometry."""
    suffixed(a)
    sc = scale
    tag = '' if index == 0 else f'__{index:03d}'
    if cradle is None:
        cradle = post > 0 or riser > 0
    if riser > 0:
        x, y, z = loc
        rr = ring_r * sc
        rp = a.part(f'MG_riser{tag}', 'Armor', parent)
        k.ring(rp, [(rr * .8, 0), (rr * .92, 0), (rr * .92, riser * .7), (rr * .86, riser), (rr * .8, riser)],
               loc=(x, y, z), seg=12, worn=(3,))
        rs = a.part(f'MG_post{tag}', 'Steel', parent)
        k.ring(rs, [(rr * .95, riser - .015 * sc), (rr * 1.02, riser - .015 * sc), (rr * 1.02, riser + .025 * sc),
                    (rr * .95, riser + .025 * sc)], loc=(x, y, z), seg=12)
        for i in range(4):
            u = i * TAU / 4 + TAU / 8
            rs.box((.03 * sc, .05 * sc, riser * .9), loc=(x + math.cos(u) * rr * .97, y + math.sin(u) * rr * .97,
                                                     z + riser * .45), rot=(0, 0, u), bevel=0)
        # The slide arm from the ring rail to the post at the centre.
        rs.box((.08 * sc, rr * .95, .04 * sc), loc=(x, y + rr * .48, z + riser + .02 * sc), bevel=0)
        loc = (x, y, z + riser + .02 * sc)
    if post > 0:
        x, y, z = loc
        pp = a.part(f'MG_post{tag}', 'Steel', parent)
        k.block(pp, (.24 * sc, .24 * sc, .03 * sc), loc=(x, y, z + .015 * sc), chamfer=.008 * sc)
        k.lathe(pp, [(.045 * sc, 0), (.045 * sc, post - .05 * sc), (.062 * sc, post - .04 * sc), (.062 * sc, post),
                     (0, post)], loc=(x, y, z), seg=8, worn=(2,))
        for g in range(3):
            u = g * TAU / 3
            pp.box((.012 * sc, .09 * sc, .1 * sc), loc=(x + math.sin(u) * .07 * sc, y + math.cos(u) * .07 * sc,
                                                       z + .08 * sc), rot=(0, 0, -u), bevel=0)
        loc = (x, y, z + post)
    m = a.pivot(name(f'Mount_{slot}', index), loc, parent)
    if cradle:
        cr = a.part(f'MG_cradle{tag}', 'Armor', m)
        for s in (-1, 1):
            k.block(cr, (.02 * sc, .3 * sc, .14 * sc), loc=(s * .095 * sc, -.02 * sc, .17 * sc), chamfer=.006 * sc)
        k.lathe(cr, [(.018 * sc, -.12 * sc), (.018 * sc, .12 * sc)], loc=(0, .02 * sc, .17 * sc), rot=(0, R90, 0),
                seg=6)
    g = a.part(f'MG{tag}', 'Steel', m)
    k.lathe(g, [(.07 * sc, 0), (.07 * sc, .04 * sc), (.045 * sc, .07 * sc), (.04 * sc, .16 * sc)], seg=8, worn=(1,))
    k.extrude(g, [(-.2 * sc, .14 * sc), (.18 * sc, .14 * sc), (.2 * sc, .26 * sc), (.02 * sc, .3 * sc),
                  (-.2 * sc, .28 * sc)], .15 * sc, axis='X', chamfer=.012 * sc, corner=.012 * sc)
    for s in (-1, 1):
        g.limb((s * .05 * sc, .2 * sc, .2 * sc), (s * .07 * sc, .3 * sc, .14 * sc), .025 * sc, .025 * sc, bevel=0)
    front = -.2 * sc
    L = length * sc
    k.lathe(g, [(.045 * sc, 0), (.045 * sc, .2 * sc), (.03 * sc, .24 * sc), (.03 * sc, L - .12 * sc),
                (.05 * sc, L - .1 * sc), (.05 * sc, L - .01 * sc), (.035 * sc, L), (.02 * sc, L),
                (.02 * sc, L - .05 * sc), (0, L - .05 * sc)], loc=(0, front, .22 * sc), rot=FORWARD, seg=8, worn=(4,))
    handle(g, (0, front - .25 * sc, .27 * sc), (0, front - .45 * sc, .27 * sc), (0, 0, 1), h=.05 * sc, r=.01 * sc)
    ab = 1.35 if (post > 0 or riser > 0) else 1.0   # a raised gun carries the big ammunition can on a bracket
    k.block(a.part(f'MG_ammo{tag}', 'Armor', m), (.13 * sc * ab, .24 * sc * ab, .16 * sc * ab),
            loc=(.16 * sc * ab, .02 * sc, .2 * sc - (ab - 1) * .05 * sc), chamfer=.015 * sc)
    if shield:
        k.extrude(a.part(f'MG_shield{tag}', 'Armor', m), [(-.28 * sc, -.17 * sc), (.28 * sc, -.17 * sc),
                                                        (.24 * sc, .2 * sc), (-.24 * sc, .2 * sc)], .04 * sc,
                  loc=(0, -.3 * sc, .28 * sc), rot=(-.12 + R90, 0, 0), axis='Z', chamfer=.01 * sc, corner=.01 * sc)
    a.pivot(name(f'Muzzle_{slot}', index), (0, front - L + .01 * sc, .22 * sc), m)
    return m


def smoke_dischargers(a, x, y, z, s, count=4, parent=None):
    part = a.part('Smoke_launchers', 'Armor', parent)
    p27.smoke_launcher(a, part, x, y, z, s, count=count)


def era_bricks(a, origin, u, v, cols, rows, size=(.3, .22, .07), gap=.02, parent=None, mat='Armor', bolts=True):
    """A block of explosive reactive armour bricks on a plane spanned by unit u, v at origin (normal u x v), each a
    chamfered brick with two bolts (`bolts=False`, wave 2: plain bricks, half the triangles; the default keeps them)."""
    part = a.part(KIT['era'], mat, parent)
    bolt_part = a.part(KIT['bolts'], 'Steel', parent) if bolts else None
    u, v, o = Vector(u).normalized(), Vector(v).normalized(), Vector(origin)
    n = u.cross(v).normalized()
    rot = Matrix((u, v, n)).transposed().to_euler('XYZ')
    w, h, t = size
    for i in range(cols):
        for j in range(rows):
            c = o + u * ((i - (cols - 1) / 2) * (w + gap)) + v * ((j - (rows - 1) / 2) * (h + gap))
            plate(part, (w, h, t), loc=tuple(c + n * (t / 2 - .01)), rot=tuple(rot), chamfer=.015)
            for s in ((-1, 1) if bolts else ()):
                hd.bolt(bolt_part, tuple(c + u * (s * w * .32) + n * (t - .012)), rot=tuple(rot), r=.014, h=.018)


def slat_cage(a, p0, p1, z0, height, outward, pitch=.12, standoff=.35, parent=None):
    """Slat (bar) armour: a frame of tubes standing `standoff` off the hull face from p0 to p1 (at heights z0 ..
    z0 + height), vertical slats every `pitch`, stand-off brackets."""
    part = a.part(KIT['slats'], 'Steel', parent)
    p0, p1, o = Vector(p0), Vector(p1), Vector(outward).normalized() * standoff
    d = p1 - p0
    n = max(2, int(d.length / pitch))
    for zz in (z0, z0 + height):
        part.tube([tuple(p0 + o + Vector((0, 0, zz))), tuple(p1 + o + Vector((0, 0, zz)))], .02, seg=4)
    for i in range(n + 1):
        b = p0 + d * (i / n) + o
        part.box((.012, .05, height), loc=tuple(b + Vector((0, 0, z0 + height / 2))),
                 rot=(0, 0, math.atan2(d.y, d.x)), bevel=0)
    for f in (0, .5, 1):
        b = p0 + d * f
        part.tube([tuple(b + Vector((0, 0, z0 + height * .5))), tuple(b + o + Vector((0, 0, z0 + height * .5)))], .02,
                  seg=4)


def net_armour(a, p0, p1, z0, height, outward, cell=.18, standoff=.3, parent=None):
    """Net (RPG) armour: a tube frame with a diamond net of thin cords at 45 degrees standing off a hull face."""
    part = a.part('Net_armour', 'Steel', parent)
    o = Vector(outward).normalized() * standoff
    p0, p1 = Vector(p0) + o, Vector(p1) + o
    d = p1 - p0
    L, H = d.length, height
    u = d.normalized()
    corners = [p0 + Vector((0, 0, z0)), p1 + Vector((0, 0, z0)), p1 + Vector((0, 0, z0 + H)), p0 + Vector((0, 0, z0 + H))]
    part.tube([tuple(c) for c in corners + corners[:1]], .02, seg=4)

    def at(t, z):
        return tuple(p0 + u * t + Vector((0, 0, z0 + z)))
    c = -H
    while c <= L + H:
        for sgn in (1, -1):
            if sgn > 0:
                za, zb = max(0.0, -c), min(H, L - c)
            else:
                za, zb = max(0.0, c - L), min(H, c)
            if zb - za > .05:
                part.tube([at(c + sgn * za, za), at(c + sgn * zb, zb)], .006, seg=3, caps=False)
        c += cell


# ============================================================================= wheeled
def truck_wheel(a, centre, r, width, s, lugs=18, seg=18, rim_mat='Steel', parent=None, tyre='Tyres', rim='Wheels',
                lug_depth=None, nuts=8, hub_cap=True):
    """A truck / mining wheel on an axle along X, its outer face on side s: a rubber casing with rounded shoulders,
    chevron tread lugs, a dished rim with a flange, the hub with wheel nuts and a hub cap."""
    x, y, z = centre
    rot = p27.side_rot(s)
    w = width
    tr = a.part(tyre, 'Rubber', parent)
    ld = lug_depth if lug_depth is not None else r * .06
    R = r - ld
    k.lathe(tr, [(r * .62, -w / 2 + .01), (R * .9, -w / 2), (R - ld * .5, -w / 2 + w * .08), (R, -w / 2 + w * .2),
                 (R, w / 2 - w * .2), (R - ld * .5, w / 2 - w * .08), (R * .9, w / 2), (r * .62, w / 2 - .01)],
            loc=centre, rot=rot, seg=seg, worn=(3, 4))
    m = frame(centre, rot)
    for i in range(lugs):
        th = i * TAU / lugs
        for side in (-1, 1):
            tt = th + (TAU / lugs / 2 if side > 0 else 0)
            lm = m @ Matrix.Rotation(tt, 4, 'Z') @ Matrix.Translation((R + ld / 2 - .005, 0, side * w * .22)) @                 Matrix.Rotation(side * .35, 4, 'X')
            tr.box((ld + .01, w * .1 + r * .1, w * .4), loc=tuple(lm.to_translation()), rot=tuple(lm.to_euler('XYZ')),
                   bevel=0)
    rm = a.part(rim, rim_mat, parent)
    f = w / 2
    k.lathe(rm, [(r * .64, f - .02), (r * .64, f + .015), (r * .58, f + .02), (r * .55, f - .06), (r * .3, f - .08),
                 (r * .26, f), (r * .16, f + .02), (0, f + .02)], loc=centre, rot=rot, seg=seg, worn=(1, 5))
    nut = a.part(KIT['nuts'], 'Steel', parent)
    for i in range(nuts):
        u = i * TAU / nuts
        nut.cyl(r * .035 + .005, .03, loc=_at(m, (r * .21 * math.cos(u), r * .21 * math.sin(u), f + .01)), rot=rot,
                seg=6, bevel=0)
    if hub_cap:
        k.lathe(a.part(KIT['hubs'], 'Steel', parent), [(r * .12, f), (r * .12, f + .05), (r * .07, f + .08),
                                                       (0, f + .085)], loc=centre, rot=rot, seg=8)


def tread_wheel(a, centre, r, width, s, seg=14, depth=None, parent=None, tyre='Tyres', rim='Wheels', rim_mat='Steel',
                hub=True, nuts=0, dish=.6, rim_seg=8):
    """A lean military tyre (about 250 triangles against about 700 for truck_wheel; wave 2, lane B's request, after
    its mb_p35b_parts.tread_wheel) on an axle along X, outer face on side s: the casing's two tread rows alternate in
    radius vertex by vertex, so a chevron lug pattern reads in the silhouette without lug boxes; the inner face ends
    at the sidewall (never seen); a dished rim with its flange, the hub boss and (nuts > 0) wheel nuts. For trucks
    and carriers with many wheels."""
    import bmesh
    w = width
    ld = depth if depth is not None else r * .07
    R = r - ld
    prof = [(R * .9, -w / 2), (R, -w / 2 + w * .12), (r, -w / 2 + w * .3),
            (r, w / 2 - w * .3), (R, w / 2 - w * .12), (R * .9, w / 2), (r * .62, w / 2 - .012)]
    sh = a.part(tyre, 'Rubber', parent)
    bm = sh.bm
    rows = []
    for j, (rr, z) in enumerate(prof):
        row = []
        for i in range(seg):
            u = i * TAU / seg
            q = rr
            if j in (2, 3):                    # the tread: lug and groove alternate, offset between the two rows
                q = r if (i + j) % 2 == 0 else R + ld * .5
            row.append(bm.verts.new((q * math.cos(u), q * math.sin(u), z)))
        rows.append(row)
    faces = []
    for ra, rb in zip(rows, rows[1:]):
        faces += [bm.faces.new((ra[i], ra[(i + 1) % seg], rb[(i + 1) % seg], rb[i])) for i in range(seg)]
    faces.append(bm.faces.new(list(reversed(rows[0]))))
    faces.append(bm.faces.new(rows[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    k._wear(sh, rows[1] + rows[4])
    rot = (0, s * R90, 0)
    bmesh.ops.transform(bm, matrix=k._frame(centre, rot), verts=[v for row in rows for v in row])
    f = w / 2
    dk = dish / .6
    k.lathe(a.part(rim, rim_mat, parent), [(r * .64, f + .012), (r * .57, f + .016), (r * .5, f - .05 * dk),
                                           (r * .22, f - .06 * dk), (0, f - .06 * dk)], loc=centre, rot=rot,
            seg=rim_seg, worn=(0,))
    m = frame(centre, rot)
    if hub:
        k.lathe(a.part(KIT['hubs'], 'Steel', parent), [(r * .13, f), (r * .1, f + .05), (0, f + .065)], loc=centre,
                rot=rot, seg=6)
    if nuts:
        nut = a.part(KIT['nuts'], 'Steel', parent)
        for i in range(nuts):
            u = i * TAU / nuts
            nut.cyl(r * .03 + .004, .03, loc=_at(m, (r * .3 * math.cos(u), r * .3 * math.sin(u), f - .03)), rot=rot,
                    seg=5, bevel=0)


def axle(part, y, z, half_track, r=.09, diff=True):
    """A beam axle across the vehicle at (y, z), its differential housing in the middle."""
    k.lathe(part, [(r * .9, -half_track), (r, -half_track + .05), (r, half_track - .05), (r * .9, half_track)],
            loc=(0, y, z), rot=(0, R90, 0), seg=8, worn=(1, 2))
    if diff:
        k.lathe(part, [(0, -r * 1.4), (r * 2.2, -r * 1.2), (r * 2.4, 0), (r * 2.2, r * 1.2), (0, r * 1.5)],
                loc=(0, y, z), rot=FORWARD, seg=10)


def leaf_spring(part, x, y, z, length, leaves=4, w=.07):
    """A leaf spring pack along Y at (x, y, z): stacked leaves shorter downwards, the centre clamp and the eyes."""
    for i in range(leaves):
        L = length * (1 - i * .18)
        part.box((w, L, .018), loc=(x, y, z - i * .02), bevel=0)
    part.box((w * 1.3, .1, .1), loc=(x, y, z - leaves * .01), bevel=0)
    for s in (-1, 1):
        part.cyl(.025, w * 1.2, loc=(x, y + s * length / 2, z + .01), rot=(0, R90, 0), seg=6, bevel=0)


def windscreen(a, corners, frame_mat='Armor', parent=None, wipers=1, bar=.04):
    """A glass pane through four corners (clockwise seen from outside), its frame round it and wipers at the
    bottom edge. Returns the pane's centre."""
    c = [Vector(p) for p in corners]
    centre = sum(c, Vector()) / 4
    n = (c[1] - c[0]).cross(c[3] - c[0]).normalized()
    a.part(KIT['glass'], 'Glass', parent).mesh([tuple(p + n * .005) for p in c], [(0, 1, 2, 3)])
    fr = a.part('Window_frames', frame_mat, parent)
    for p, q in zip(c, c[1:] + c[:1]):
        fr.tube([tuple(p + n * .01), tuple(q + n * .01)], bar / 2, seg=4)
    st = a.part('Wipers', 'Steel', parent)
    bot = (c[0], c[1])
    for i in range(wipers):
        f = (i + .5) / wipers
        base = bot[0] + (bot[1] - bot[0]) * (f * .9) + n * .02
        up = ((c[3] - c[0]) * .55)
        st.tube([tuple(base), tuple(base + up + (bot[1] - bot[0]).normalized() * .08)], .008, seg=3)
    return tuple(centre)


def mirror(part, loc, s, arm=.25, size=(.12, .03, .2)):
    """A door mirror on side s: a tube arm out of the cab and the mirror head."""
    x, y, z = loc
    part.tube([(x, y, z), (x + s * arm, y - .05, z + .05)], .012, seg=4)
    k.block(part, size, loc=(x + s * (arm + .02), y - .05, z - .02), chamfer=.01)


def outrigger(part, pad_part, loc, s, reach=1.2, drop=.9, w=.22):
    """A stabiliser leg on side s: a box beam out of the chassis, the jack cylinder down and the foot pad."""
    x, y, z = loc
    k.block(part, (reach, w, w), loc=(x + s * reach / 2, y, z - w / 2), chamfer=.02)
    part.cyl(w * .3, drop, loc=(x + s * (reach - .1), y, z - drop / 2), seg=8, bevel=0)
    k.lathe(pad_part, [(w * 1.4, 0), (w * 1.4, .05), (w * .5, .1)], loc=(x + s * (reach - .1), y, z - drop - .05),
            seg=10, worn=(1,))


# ============================================================================= aircraft
FOIL = [(1.0, 0.0), (.6, .55), (.1, 1.0), (-.35, .8), (-1.0, 0.0), (-.35, -.6), (.1, -.75), (.6, -.4)]


def _foil_ring(lead, chord, t, x, z, dihedral=0.0, axis='x'):
    """A section of an airfoil at span position x: leading edge y = lead (front is -Y), chord along +Y."""
    pts = []
    for u, v in FOIL:
        yy = lead + chord * (1 - u) / 2
        if axis == 'x':
            pts.append((x, yy, z + v * t * chord * .5))
        else:                             # a vertical fin: span along Z, thickness along X
            pts.append((v * t * chord * .5 + x, yy, z))
    return pts


def wing(shape, root, tip, span, x0=0.0, z=0.0, t=.08, dihedral=0.0, sides=(1, -1), crank=None):
    """A wing panel per side: airfoil sections from root (lead y, chord) at x0 to tip at x0 + span, the leading edge
    sweep from the two lead positions, the taper from the chords, `t` thickness / chord, dihedral in radians.
    crank = (fraction of the span, lead y, chord) adds a mid section (cranked arrows, LERX)."""
    for s in sides:
        secs = [(0.0,) + tuple(root)]
        if crank:
            secs.append(crank)
        secs.append((1.0,) + tuple(tip))
        rings = []
        for f, lead, chord in secs:
            x = x0 + span * f
            rings.append([(s * px, py, pz) for px, py, pz in _foil_ring(lead, chord, t, x, z + math.tan(dihedral) * span * f)])
        if s < 0:
            rings = [list(reversed(r)) for r in rings]
        shape.loft(rings, bevel=0)


def fin(shape, root, tip, height, x=0.0, z0=0.0, t=.07, cant=0.0):
    """A vertical (or canted) fin: airfoil sections from the root (lead y, chord) at z0 to the tip at z0 + height."""
    rings = []
    for f, (lead, chord) in ((0.0, root), (1.0, tip)):
        zz = z0 + height * f
        xx = x + math.sin(cant) * height * f
        rings.append(_foil_ring(lead, chord, t, xx, zz, axis='z'))
    shape.loft(rings, bevel=0)


def intake(shape, dark, loc, w, h, depth, facing=(0, -1, 0), lip=.04):
    """A box intake mouth: a chamfered duct, a sharp lip ring and the dark duct inside."""
    rot = rot_to(facing)
    m = frame(loc, rot)
    k.extrude(shape, [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)], depth,
              loc=_at(m, (0, 0, -depth / 2)), rot=rot, axis='Z', chamfer=lip, corner=min(w, h) * .12)
    dark.box((w - lip * 2, h - lip * 2, .02), loc=_at(m, (0, 0, -.06)), rot=rot, bevel=0)


def missile(a, loc, r, length, direction=(0, -1, 0), fins=4, parent=None, body='Missiles', seeker='Glass', band=True):
    """A missile nose along `direction`: an ogive body, the seeker dome, a hazard band, 4 tail fins and 4 canards."""
    rot = rot_to([-c for c in direction])
    m = frame(loc, rot)
    k.lathe(a.part(body, 'Fuel', parent), [(0, 0), (r * .8, .02), (r, .08), (r, length * .82), (r * .9, length * .94),
                                           (r * .45, length), (0, length + .005)], loc=loc, rot=rot, seg=8, worn=(2,))
    k.lathe(a.part('Missile_seekers', seeker, parent), [(r * .45, length - .002), (r * .2, length + r * .3),
                                                        (0, length + r * .35)], loc=loc, rot=rot, seg=8,
            caps=(False, False))
    fp = a.part('Missile_fins', 'Steel', parent)
    for i in range(fins):
        fm = m @ Matrix.Rotation(i * TAU / fins + TAU / 8, 4, 'Z')
        for zpos, fl, fw in ((.04, r * 2.2, length * .14), (length * .75, r * 1.2, length * .06)):
            fp.box((fl, .008, fw), loc=_at(fm, (r + fl / 2 - .01, 0, zpos + fw / 2)), rot=tuple(fm.to_euler('XYZ')),
                   bevel=0)
    if band:
        a.part('Missile_bands', 'Hazard', parent).cyl(r * 1.03, .03, loc=_at(m, (0, 0, length * .7)), rot=rot, seg=8,
                                                       bevel=0)


def bomb(a, loc, r, length, parent=None):
    """A low-drag bomb nose forward: the body, the fuze, the cruciform tail with its ring."""
    k.lathe(a.part('Bombs_body', 'Armor', parent), [(0, -length * .5), (r * .6, -length * .45), (r, -length * .2),
                                                    (r, length * .2), (r * .45, length * .45), (r * .3, length * .5)],
            loc=loc, rot=BACKWARD, seg=10, worn=(2,))
    tp = a.part('Bomb_fins', 'Steel', parent)
    for i in range(4):
        u = i * R90 + TAU / 8
        tp.box((.008, r * 1.1, length * .22), loc=(loc[0] + math.cos(u) * r * .7, loc[1] + length * .42,
                                                   loc[2] + math.sin(u) * r * .7), rot=(R90, 0, u), bevel=0)
    a.part('Bomb_bands', 'Hazard', parent).cyl(r * 1.02, .03, loc=(loc[0], loc[1] - length * .25, loc[2]), rot=FORWARD,
                                               seg=10, bevel=0)


def drop_tank(part, loc, r, length):
    k.lathe(part, [(0, -length / 2), (r * .5, -length * .42), (r, -length * .15), (r, length * .2),
                   (r * .3, length * .5), (0, length * .5 + .01)], loc=loc, rot=FORWARD, seg=12, worn=(2, 3))


def flare_dispenser(a, loc, normal=(0, 0, -1), cols=3, rows=2, cell=.07, parent=None):
    """A chaff / flare dispenser: a flat box with a grid of cartridge mouths."""
    rot = rot_to(normal)
    m = frame(loc, rot)
    w, h = cols * cell + .03, rows * cell + .03
    k.block(a.part('Flares', 'Armor', parent), (w, h, .05), loc=_at(m, (0, 0, -.005)), rot=rot, chamfer=.01)
    holes = a.part('Flare_mouths', 'Undercarriage', parent)
    for i in range(cols):
        for j in range(rows):
            holes.cyl(cell * .32, .012, loc=_at(m, ((i - (cols - 1) / 2) * cell, (j - (rows - 1) / 2) * cell, .02)),
                      rot=rot, seg=6, bevel=0)


def blade_antenna(part, loc, h=.2, chord=.12, normal=(0, 0, 1)):
    rot = rot_to(normal)
    k.extrude(part, [(-chord / 2, 0), (chord / 2, 0), (chord * .1, h), (-chord * .25, h)], .015, loc=loc, rot=rot,
              axis='X')


def landing_gear(a, loc, wheel_r=.32, leg=1.2, width=.18, twin=False, parent=None):
    """A landing gear leg down from loc: the oleo strut, the torque link, the wheel(s) with hubs."""
    x, y, z = loc
    st = a.part('Gear', 'Steel', parent)
    k.lathe(st, [(.06, 0), (.06, -leg * .55), (.045, -leg * .6), (.045, -leg + wheel_r)], loc=loc, seg=8, worn=(1,))
    st.limb((x, y - .08, z - leg * .45), (x, y - .1, z - leg * .75), .03, .03, bevel=0)
    for s in ((-1, 1) if twin else (1,)):
        c = (x + (s * (width / 2 + .03) if twin else 0), y, z - leg)
        k.lathe(a.part('Gear_tyres', 'Rubber', parent), [(wheel_r * .6, -width / 2), (wheel_r, -width / 2 + .03),
                                                         (wheel_r, width / 2 - .03), (wheel_r * .6, width / 2)],
                loc=c, rot=(0, R90, 0), seg=12)
        a.part('Gear_hubs', 'Steel', parent).cyl(wheel_r * .55, width + .02, loc=c, rot=(0, R90, 0), seg=10, bevel=0)


def pylon(part, x, y0, y1, ztop, zbot, w=.08):
    p27.pylon(part, x, y0, y1, ztop, zbot, w=w, braces=True)


# ============================================================================= helicopters
def rotor_head(a, r, blades, R, chord, **kw):
    with detail(a):
        p27.rotor_head(a, r, blades, R, chord, **kw)


def tail_rotor(a, tr, blades, R, chord, **kw):
    with detail(a):
        p27.tail_rotor(a, tr, blades, R, chord, **kw)


def skids(part, x, y0, y1, z, h=.6, r=.04):
    """Landing skids both sides at |x| from y0 to y1, z the ground: tubes with upturned toes and two cross tubes."""
    for s in (-1, 1):
        part.tube([(s * x, y0 - .25, z + .18), (s * x, y0, z + r), (s * x, y1, z + r)], r, seg=6)
    for f in (.25, .75):
        y = y0 + (y1 - y0) * f
        part.tube([(-x, y, z + r), (-x * .7, y, z + h), (x * .7, y, z + h), (x, y, z + r)], r * .9, seg=6)


def stub_wing(shape, x0, span, y, chord, z, t=.12, anhedral=.08):
    wing(shape, (y, chord), (y + chord * .05, chord * .8), span, x0=x0, z=z, t=t, dihedral=-anhedral)


# ============================================================================= ships
def ship_hull(shape, length, beam, depth, flare=.25, sheer=.06, stern=.8, keel=.15, sections=9):
    """A displacement hull centred on the origin, bow at -Y: sections from stern to bow, the beam narrowing to the
    stem, flare (the deck wider than the waterline forward), sheer (the deck rising to the bow), a transom stern."""
    rings = []
    for i in range(sections + 1):
        f = i / sections                     # 0 stern .. 1 bow
        y = length / 2 - f * length
        half = beam / 2 * (stern + (1 - stern) * math.sin(min(1, f * 1.6) * R90)) if f < .6 else \
            beam / 2 * math.cos((f - .6) / .4 * R90) ** .8
        half = max(half, .02)
        top = depth * (1 + sheer * f * f * 4)
        fl = 1 + flare * f
        wl = half / fl
        bot = keel * (1 - f * .5)
        rings.append([(-half, y, top), (-wl, y, depth * .35), (-wl * .6, y, bot), (0, y, 0), (wl * .6, y, bot),
                      (wl, y, depth * .35), (half, y, top)])
    rings[-1] = [(0, rings[-1][0][1] - .01, p[2]) if i in (0, 6) else (p[0] * .2, p[1], p[2])
                 for i, p in enumerate(rings[-1])]
    shape.loft(rings, bevel=0)


def railing(part, points, h=1.0, post=1.2, r=.025):
    """A guard rail along a polyline on a deck: posts every `post` metres, a top rail and a middle rail."""
    pts = [Vector(p) for p in points]
    for z in (h, h * .5):
        part.tube([tuple(p + Vector((0, 0, z))) for p in pts], r, seg=4)
    for p, _ in k.along([tuple(p) for p in pts], pitch=post):
        part.box((r * 2, r * 2, h), loc=tuple(Vector(p) + Vector((0, 0, h / 2))), bevel=0)


def ladder(part, p0, p1, width=.45, step=.3, r=.022):
    """A ladder from p0 (bottom) to p1 (top): two stringers and rungs every `step`."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    side = d.cross(Vector((0, 0, 1)))
    side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
    for s in (-1, 1):
        part.tube([tuple(p0 + side * s * width / 2), tuple(p1 + side * s * width / 2)], r * 1.2, seg=4)
    n = max(1, int(d.length / step))
    for i in range(1, n):
        c = p0 + d * (i / n)
        part.tube([tuple(c - side * width / 2), tuple(c + side * width / 2)], r, seg=4)


def vls(a, origin, cols, rows, cell=.6, parent=None):
    """A vertical launch block: a deck plate with a grid of square hatches and their hinges."""
    x, y, z = origin
    plate(a.part('Vls', 'Armor', parent), (cols * cell + .1, rows * cell + .1, .08), loc=(x, y, z), chamfer=.02)
    lids = a.part('Vls_hatches', 'Steel', parent)
    for i in range(cols):
        for j in range(rows):
            cx, cy = x + (i - (cols - 1) / 2) * cell, y + (j - (rows - 1) / 2) * cell
            lids.box((cell * .82, cell * .82, .02), loc=(cx, cy, z + .045), bevel=0)
            lids.box((cell * .6, .03, .03), loc=(cx, cy - cell * .38, z + .055), bevel=0)


def ciws(a, mount, loc, parent=None, scale=1.0):
    """A Phalanx-class CIWS on its own Mount_<mount> pivot: the pedestal, the white radome barrel housing, the
    gatling barrels and Muzzle_<mount>."""
    k.lathe(a.part('Ciws_base', 'Armor', parent), [(.55 * scale, 0), (.5 * scale, .6 * scale), (.4 * scale, .7 * scale)],
            loc=loc, seg=12)
    m = a.pivot(f'Mount_{mount}', (loc[0], loc[1], loc[2] + .7 * scale), parent)
    body = a.part('Ciws_body', 'Plaster', m)
    k.block(body, (.7 * scale, .9 * scale, .6 * scale), loc=(0, .1 * scale, 0), chamfer=.06 * scale)
    k.lathe(body, [(.3 * scale, 0), (.38 * scale, .4 * scale), (.32 * scale, .8 * scale), (0, .95 * scale)],
            loc=(0, .1 * scale, .55 * scale), seg=12, worn=(1,))
    g = a.part('Ciws_gun', 'Steel', m)
    for i in range(6):
        u = i * TAU / 6
        g.cyl(.022 * scale, 1.2 * scale, loc=(math.cos(u) * .06 * scale, -.85 * scale, .3 * scale + math.sin(u) * .06 *
                                              scale), rot=FORWARD, seg=5, bevel=0)
    g.cyl(.11 * scale, .12 * scale, loc=(0, -1.4 * scale, .3 * scale), rot=FORWARD, seg=10, bevel=0)
    a.pivot(f'Muzzle_{mount}', (0, -1.47 * scale, .3 * scale), m)


def rhib(part, tube, loc, length=7.0, beam=2.5):
    """A rigid-hull inflatable boat: the hull wedge, the grey tubes round it, the console."""
    x, y, z = loc
    k.extrude(part, [(-beam * .4, 0), (beam * .4, 0), (beam * .45, .6), (-beam * .45, .6)], length * .9,
              loc=(x, y, z), axis='Y', chamfer=.08)
    tube.tube([(x - beam * .45, y + length * .45, z + .55), (x - beam * .45, y - length * .3, z + .55),
               (x, y - length * .5, z + .6), (x + beam * .45, y - length * .3, z + .55),
               (x + beam * .45, y + length * .45, z + .55)], .25, seg=8)
    k.block(part, (.8, .7, .9), loc=(x, y + .3, z + .55), chamfer=.06)


def radar_mast(a, loc, h=6.0, parent=None, radar_parent=None):
    """A lattice mast: four legs with cross braces, yards, a top platform, the `Radar` pivot on top (spins)."""
    x, y, z = loc
    st = a.part('Mast', 'Steel', parent)
    b = .5
    for sx in (-1, 1):
        for sy in (-1, 1):
            st.tube([(x + sx * b, y + sy * b, z), (x + sx * b * .35, y + sy * b * .35, z + h)], .05, seg=4)
    for i in range(4):
        zz = z + h * (i + .5) / 4
        w = b * (1 - .65 * (i + .5) / 4)
        st.tube([(x - w, y - w, zz), (x + w, y - w, zz), (x + w, y + w, zz), (x - w, y + w, zz), (x - w, y - w, zz)],
                .025, seg=4)
    st.box((2.4, .1, .1), loc=(x, y, z + h * .8), bevel=0)
    k.block(st, (b * 1.4, b * 1.4, .1), loc=(x, y, z + h), chamfer=.02)
    r = a.pivot('Radar', (x, y, z + h + .1), radar_parent)
    rad = a.part('Radar_array', 'Armor', r)
    k.block(rad, (2.2, .25, .7), loc=(0, 0, .2), chamfer=.04)
    a.part('Radar_face', 'Undercarriage', r).box((2.0, .02, .55), loc=(0, -.13, .55), bevel=0)


# ============================================================================= rail
def rail_track(part, sleeper_part, length, gauge=1.435, pitch=.6, y0=0.0):
    """A straight track along Y: two rails on concrete sleepers every `pitch`."""
    for s in (-1, 1):
        k.extrude(part, [(-.035, 0), (.035, 0), (.012, .03), (.012, .12), (.035, .14), (-.035, .14), (-.012, .12),
                         (-.012, .03)], length, loc=(s * gauge / 2, y0, .2), axis='Y')
    n = int(length / pitch)
    for i in range(n):
        k.block(sleeper_part, (2.6, .26, .2), loc=(0, y0 - length / 2 + (i + .5) * pitch, 0), chamfer=.02)


def bogie(a, loc, gauge=1.435, wheel_r=.46, base=2.6, parent=None):
    """A two-axle bogie: side frames with axle boxes and springs, four wheels with flanges, the bolster."""
    x, y, z = loc
    fr = a.part('Bogies', 'Undercarriage', parent)
    for s in (-1, 1):
        k.block(fr, (.18, base + .8, .35), loc=(x + s * (gauge / 2 + .15), y, z + wheel_r - .15), chamfer=.03)
        for e in (-1, 1):
            fr.box((.24, .3, .3), loc=(x + s * (gauge / 2 + .17), y + e * base / 2, z + wheel_r), bevel=0)
            a.part('Bogie_springs', 'Steel', parent).cyl(.07, .25, loc=(x + s * (gauge / 2 + .17), y + e * base * .25,
                                                                          z + wheel_r + .25), seg=8, bevel=0)
    for e in (-1, 1):
        for s in (-1, 1):
            k.lathe(a.part('Rail_wheels', 'Steel', parent), [(0, -.07), (wheel_r * .9, -.07), (wheel_r, -.04),
                                                             (wheel_r, .05), (wheel_r * 1.08, .07),
                                                             (wheel_r * .5, .09), (0, .09)],
                    loc=(x + s * gauge / 2, y + e * base / 2, z + wheel_r), rot=p27.side_rot(-s), seg=14)
        fr.cyl(.08, gauge + .1, loc=(x, y + e * base / 2, z + wheel_r), rot=(0, R90, 0), seg=8, bevel=0)
    k.block(fr, (gauge + .2, .5, .3), loc=(x, y, z + wheel_r + .1), chamfer=.03)


# ============================================================================= structures and towers
STYLES = ('accord', 'hegemon')


def footing(a, size, loc=(0, 0, 0), style='hegemon', parent=None):
    """The base a tower or structure stands on. hegemon: a cast concrete plinth with a chamfered top and form-tie
    marks; accord: a timber-framed earth pad (sleepers along the edge, staked)."""
    w, d, h = size
    x, y, z = loc
    if style == 'hegemon':
        base = a.part('Base', 'Concrete', parent)
        k.block(base, size, loc=loc, chamfer=min(.12, h * .4))
        ties = a.part('Base_ties', 'Steel', parent)
        for s in (-1, 1):
            for i in range(4):
                f = -0.375 + i * .25
                ties.cyl(.025, .03, loc=(x + f * w, y + s * d / 2, z), rot=FORWARD, seg=6, bevel=0)
                ties.cyl(.025, .03, loc=(x + s * w / 2, y + f * d, z), rot=(0, R90, 0), seg=6, bevel=0)
    else:
        base = a.part('Base', 'Dirt', parent)
        k.block(base, (w, d, h), loc=loc, chamfer=min(.2, h * .5), taper=(.94, .94))
        wood = a.part('Base_timbers', 'Wood', parent)
        for s in (-1, 1):
            k.block(wood, (w + .1, .22, .22), loc=(x, y + s * (d / 2 + .02), z), chamfer=.03)
            k.block(wood, (.22, d - .3, .22), loc=(x + s * (w / 2 + .02), y, z), chamfer=.03)
            for f in (-.4, 0, .4):
                wood.cyl(.05, .4, loc=(x + f * w, y + s * (d / 2 + .15), z + .1), seg=6, bevel=0)


def sandbag_wall(a, path, layers=3, bag=(.6, .32, .14), closed=False, parent=None, mat='Sandbag', round_both=True):
    """Sandbags laid along a polyline, `layers` courses high, each course offset by half a bag, every bag a pillow
    (a rounded block with its tied end) with slight deterministic jitter. round_both=False leaves the hidden bottom
    edges square (a cheaper bag for towers seen from above)."""
    part = a.part(KIT['sandbags'], mat, parent)
    rng = random.Random(len(path) * 7919 + layers)
    L, W, H = bag
    pts = path + path[:1] if closed else path
    for course in range(layers):
        start = L / 2 * (course % 2)
        for p, t in k.along(pts, pitch=L * .97, start=start):
            yaw = math.atan2(t.y, t.x)
            jit = rng.uniform(-.03, .03)
            loc = (p.x, p.y, p.z + H / 2 + course * H * .92)
            k.block(part, (L * (.96 + jit), W * (1 + jit), H), loc=loc, rot=(0, 0, yaw + rng.uniform(-.06, .06)),
                    chamfer=H * .42, ends=(True, True) if round_both else (False, True))


def wire_fence(a, path, h=1.6, post=2.5, strands=4, parent=None, concertina=True):
    """A wire fence: angle-iron posts every `post` metres, strands between them, a concertina coil on top."""
    part = a.part(KIT['fence'], 'Steel', parent)
    pts = [Vector(p) for p in path]
    for p, t in k.along([tuple(p) for p in pts], pitch=post):
        part.box((.05, .05, h), loc=(p.x, p.y, p.z + h / 2), rot=(0, 0, math.atan2(t.y, t.x) + .78), bevel=0)
    for i in range(strands):
        z = h * (i + .6) / strands
        part.tube([tuple(p + Vector((0, 0, z))) for p in pts], .006, seg=3, caps=False)
    if concertina:
        for p, t in k.along([tuple(p) for p in pts], pitch=.35):
            part.torus(.22, .008, loc=(p.x, p.y, p.z + h + .18), rot=(0, R90, math.atan2(t.y, t.x)), seg=8, ring=3)


def hesco(a, loc, size=(1.06, 1.06, 1.37), cells=1, yaw=0.0, parent=None):
    """HESCO bastion cells: the earth fill (Dirt) inside a wire-mesh basket (posts and rims in Steel), a canvas
    liner line at the top."""
    w, d, h = size
    m = frame(loc, (0, 0, yaw))
    fill = a.part('Hesco', 'Dirt', parent)
    mesh = a.part('Hesco_mesh', 'Steel', parent)
    liner = a.part('Hesco_liner', 'Canvas', parent)
    for c in range(cells):
        cx = (c - (cells - 1) / 2) * w
        k.block(fill, (w * .98, d * .98, h * .97), loc=_at(m, (cx, 0, h * .485)), rot=(0, 0, yaw), chamfer=.04)
        liner.box((w, d, .05), loc=_at(m, (cx, 0, h * .97)), rot=(0, 0, yaw), bevel=0)
        for sx in (-1, 1):
            for sy in (-1, 1):
                mesh.box((.03, .03, h), loc=_at(m, (cx + sx * w / 2, sy * d / 2, h / 2)), rot=(0, 0, yaw), bevel=0)
        for z in (h * .33, h * .66, h):
            for sy in (-1, 1):
                mesh.box((w, .015, .015), loc=_at(m, (cx, sy * (d / 2 + .005), z)), rot=(0, 0, yaw), bevel=0)


def t_wall(a, loc, h=3.6, w=1.5, yaw=0.0, parent=None):
    """A T-wall (cast concrete blast wall): the tall slab, the wide foot, lifting eyes on top."""
    m = frame(loc, (0, 0, yaw))
    c = a.part('Wall', 'Concrete', parent)
    k.block(c, (w, .25, h - .3), loc=_at(m, (0, 0, (h + .3) / 2)), rot=(0, 0, yaw), chamfer=.04, taper=(1, .8))
    k.block(c, (w, 1.2, .35), loc=_at(m, (0, 0, .175)), rot=(0, 0, yaw), chamfer=.06, taper=(1, .5))
    st = a.part(KIT['handles'], 'Steel', parent)
    for s in (-1, 1):
        hd.lifting_eye(st, _at(m, (s * w * .3, 0, h - .01)), yaw=yaw, size=.12)


def floodlight(a, loc, facing=(0, -1, -.3), pole=3.0, parent=None):
    """A floodlight on a pole: the mast, the yoke, a lamp box with its lit face and a cable down."""
    x, y, z = loc
    st = a.part('Light_poles', 'Steel', parent)
    st.cyl(.06, pole, loc=(x, y, z + pole / 2), seg=8, bevel=0)
    rot = rot_to(facing)
    head = (x, y - .1, z + pole + .1)
    k.block(a.part('Light_housing', 'Armor', parent), (.5, .2, .4), loc=head, rot=rot, chamfer=.03)
    m = frame(head, rot)
    a.part(KIT['lamps'], 'Lamp', parent).box((.42, .32, .02), loc=_at(m, (0, 0, .2)), rot=rot, bevel=0)
    a.part(KIT['cables'], 'Undercarriage', parent).tube([(x + .08, y, z + pole), (x + .08, y, z + .1)], .012, seg=4)


def door(a, loc, size=(1.0, 2.0), normal=(0, -1, 0), parent=None, mat='Armor'):
    """A steel door in a wall: the frame, the leaf with a vision slot, hinges and a handle."""
    w, h = size
    rot = rot_to(normal)
    m = frame(loc, rot)
    fr = a.part('Door_frames', 'Steel', parent)
    for s in (-1, 1):
        fr.box((.08, .08, h), loc=_at(m, (s * (w / 2 + .04), h / 2, .02)), rot=rot, bevel=0)
    fr.box((w + .16, .08, .08), loc=_at(m, (0, h + .04, .02)), rot=rot, bevel=0)
    # A door's local frame: +Z out of the wall, +Y up the wall after rot_to; the boxes above use (x, up, out).
    leaf = a.part('Doors', mat, parent)
    plate(leaf, (w, h, .05), loc=_at(m, (0, h / 2, -.02)), rot=rot, chamfer=.012)
    a.part('Door_slots', 'Undercarriage', parent).box((w * .4, .06, .02), loc=_at(m, (0, h * .72, .035)), rot=rot,
                                                      bevel=0)
    st = a.part(KIT['hinges'], 'Steel', parent)
    for f in (.2, .8):
        hinge(st, _at(m, (-w / 2, h * f - .1, .04)), _at(m, (-w / 2, h * f + .1, .04)), r=.02, knuckles=2)


def beacon(a, loc, parent=None, r=.1):
    """A rotating warning beacon: a base, an amber lens dome (Alloy glows) and a guard."""
    k.lathe(a.part('Beacon_base', 'Armor', parent), [(r * 1.2, 0), (r * 1.2, .05), (r, .07)], loc=loc, seg=10)
    k.lathe(a.part('Beacons', 'Alloy', parent), [(r * .9, .07), (r * .9, .18), (r * .5, .24), (0, .26)], loc=loc,
            seg=10)


# ============================================================================= bosses
def armour_plate(a, part, size, loc, rot=UP, rivet=.3, parent=None):
    """A big armour plate (w x d x t) with a chamfered edge and a rivet row round its face."""
    w, d, t = size
    m = frame(loc, rot)
    k.block(part, size, loc=loc, rot=rot, chamfer=min(.08, t * .4), ends=(True, True))
    if rivet:
        rv = a.part(KIT['rivets'], 'Steel', parent)
        e = min(.12, min(w, d) * .1)
        for (x0, y0), (x1, y1) in (((-w / 2 + e, -d / 2 + e), (w / 2 - e, -d / 2 + e)),
                                   ((w / 2 - e, -d / 2 + e), (w / 2 - e, d / 2 - e)),
                                   ((w / 2 - e, d / 2 - e), (-w / 2 + e, d / 2 - e)),
                                   ((-w / 2 + e, d / 2 - e), (-w / 2 + e, -d / 2 + e))):
            n = max(1, int(math.hypot(x1 - x0, y1 - y0) / rivet))
            for i in range(n):
                f = i / n
                hd.bolt(rv, _at(m, (x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, t / 2)), rot=rot, r=.03, h=.035)


def breakable_panel(a, node, size, loc, rot=UP, mat='Armor', tone_k=.88):
    """A boss's destructible part plate on its own `node` pivot (a Part_* node the def's parts name): a riveted
    plate one shade off the hull (COLOR_0 tone) so the player reads it as a separate target. Returns the pivot."""
    p = a.pivot(node, loc)
    armour_plate(a, a.part(f'{node.split(".")[0]}_plates', mat, p), size, (0, 0, 0), rot=rot, rivet=.35, parent=p)
    tone(a, node, k=tone_k)
    return p


def fuel_drum(part, band, loc, r=.29, h=.88, lying=False):
    """A 200-litre drum: the body with its two rolling hoops and the lid rim."""
    rot = (0, R90, 0) if lying else UP
    m = frame(loc, rot)
    k.lathe(part, [(r * .96, 0), (r, .02), (r, h - .02), (r * .96, h), (0, h)], loc=loc, rot=rot, seg=12, worn=(1, 2))
    for f in (.33, .66):
        band.cyl(r * 1.02, .025, loc=_at(m, (0, 0, h * f)), rot=rot, seg=12, bevel=0)


def smokestack(a, loc, r=.3, h=2.0, parent=None, mat='Steel'):
    """A smokestack: a stepped pipe with a band and a cap ring, soot round its mouth."""
    k.lathe(a.part('Stacks', mat, parent), [(r * 1.15, 0), (r * 1.15, .15), (r, .25), (r, h * .9), (r * 1.12, h * .92),
                                             (r * 1.12, h), (r * .85, h), (r * .85, h - .3), (0, h - .3)],
            loc=loc, seg=12, worn=(4, 5))
    soot(a, (loc[0], loc[1], loc[2] + h), radius=r * 4, k=.55)


def gun_cluster(a, mount, loc, barrels=2, spacing=.5, length=4.0, r=.12, parent=None, muzzle=None):
    """A multi-barrel gun house on its own `mount` pivot: a chamfered house, `barrels` barrels side by side, each with
    its own Muzzle_<slot> (".001" suffixes after the first), returns the pivot."""
    m = a.pivot(mount, loc, parent)
    house = a.part(f'{mount}_house', 'Armor', m)
    w = barrels * spacing + .6
    k.extrude(house, [(-w / 2, 0), (w / 2, 0), (w / 2 * .9, .9), (-w / 2 * .9, .9)], 2.0, loc=(0, .2, 0), axis='Y',
              chamfer=.06, corner=.05)
    slot = muzzle or mount.replace('Mount_', '')
    for i in range(barrels):
        x = (i - (barrels - 1) / 2) * spacing
        p27.barrel(a, f'{mount}_barrels', m, x, -.8, .45, length, r, seg=10, extractor=(.45, 1.4, .4))
        suffixed(a)
        a.pivot(name(f'Muzzle_{slot}', i), (x, -.8 - length - .05, .45), m)
    return m


# ============================================================================= COLOR_0 effects
def _fx(a):
    """The asset's effect list; installs an instance-level finish() that applies them after the bake."""
    if not hasattr(a, '_fx35'):
        a._fx35 = []
        original = a.finish

        def finish():
            out = original()
            _apply(a)
            return out
        a.finish = finish
    return a._fx35


def soot(a, point, radius=.4, k=.4):
    """Darken COLOR_0 round `point` (muzzles, exhaust mouths): smooth falloff to `radius`, a little cooler."""
    _fx(a).append(('soot', Vector(point), radius, k, None))


def dust(a, point, radius=1.0, k=.18):
    """Dust / mud round `point` (wheels, tracks): darker and browner, smooth falloff to `radius`."""
    _fx(a).append(('dust', Vector(point), radius, k, None))


def tone(a, prefix, k=.9, warm=.02):
    """Scale COLOR_0 of every mesh whose name or pivot chain starts with `prefix` by k (a breakable part one shade
    off the hull, a faction style difference)."""
    _fx(a).append(('tone', None, 0, k, (prefix, warm)))


def team_band(part, loc, size, rot=UP):
    """A faction colour band (Team material): a thin plate just proud of a surface."""
    part.box(size, loc=loc, rot=rot, bevel=0)


def _chain(ob):
    names, o = [], ob
    while o is not None:
        names.append(o.name)
        o = o.parent
    return names


def _world_offset(ob):
    v, o = Vector(), ob.parent
    while o is not None:
        v += o.location
        o = o.parent
    return v + ob.location


def _apply(a):
    fx = a._fx35
    if not fx:
        return
    for ob in a.objects:
        me = ob.data
        attr = me.color_attributes.get('Col')
        if attr is None or not me.materials or me.materials[0] is None:
            continue
        if me.materials[0].name.split('.')[0] in kit.GLOWING:
            continue
        off = _world_offset(ob)
        chain = _chain(ob)
        cols = [0.0] * (len(me.vertices) * 4)
        attr.data.foreach_get('color', cols)
        changed = False
        for kind, p, radius, kk, extra in fx:
            if kind == 'tone':
                prefix, warm = extra
                if not any(n.startswith(prefix) for n in chain):
                    continue
                for i in range(len(me.vertices)):
                    cols[i * 4] = min(1.0, cols[i * 4] * kk * (1 + warm))
                    cols[i * 4 + 1] = cols[i * 4 + 1] * kk
                    cols[i * 4 + 2] = cols[i * 4 + 2] * kk * (1 - warm)
                changed = True
                continue
            for i, v in enumerate(me.vertices):
                d = (off + v.co - p).length
                if d >= radius:
                    continue
                f = (1 - d / radius) ** 2 * kk
                if kind == 'soot':
                    mul = (1 - f, 1 - f * 1.02, 1 - f * .97)
                else:
                    mul = (1 - f * .8, 1 - f * .95, 1 - f * 1.15)
                for c in range(3):
                    cols[i * 4 + c] = max(0.0, min(1.0, cols[i * 4 + c] * mul[c]))
                changed = True
        if changed:
            attr.data.foreach_set('color', cols)
