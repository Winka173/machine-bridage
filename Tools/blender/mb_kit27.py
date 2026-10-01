"""Prompt 27 experiment 1, variable V1: the improved kit primitives (DECISIONS "27 scope (v2)", "27 experiment 1").

Free functions over frontier_kit.Shape (they add to `shape.bm` like the Shape methods do, so every part keeps one
mesh per name / material / parent, the COLOR_0 bake and the runtime names). They build their edges explicitly
instead of calling bmesh's bevel, so they leave no zero-area slivers, and a two-step chamfer marks its middle row as
worn (the bake brightens it 24 %, like a two-segment bevel), which keeps edges catching light at RTS distance.

  * extrude      - profile extrusion with chamfered ends and rounded profile corners (prism without bmesh bevel)
  * lathe        - revolve a (radius, z) profile; radius 0 rows become poles (no collapsed quads)
  * ring         - revolve a closed (radius, z) loop with no caps (collars, lips, coamings)
  * sweep        - a 2D profile along a 3D polyline with mitred joints (fender lips, rails, frames, hoses)
  * along        - frames (point, tangent) at even spacing along a polyline: arrays along a path
  * mirrored     - context: geometry added inside is duplicated mirrored in X (faces re-wound)
  * inset        - panel insets on chosen faces (a recessed or raised panel inside a frame)
  * sharp_loft   - loft whose chosen corners carry a two-step chamfer along the whole hull (crisp chines)
  * cut          - boolean difference (MANIFOLD solver) of a cutter built in a scratch Shape; used only where cheap
  * greebles     - deterministic small gear scattered over a rectangle on a surface
  * clean        - dissolves zero-length edges and zero-area faces in every part of an asset (run before finish)

Conventions are frontier_kit's: metres, +Z up, Blender -Y is the front.
"""
import contextlib
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

import frontier_kit as kit

TAU = math.tau


def _frame(loc, rot):
    return kit._matrix(loc, rot)


def _signed_area(poly):
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(poly, poly[1:] + poly[:1])) / 2


def offset2d(poly, d):
    """Mitred offset of a closed 2D polygon by d (positive: inwards, either winding)."""
    sign = 1.0 if _signed_area(poly) > 0 else -1.0
    pts = [Vector(p) for p in poly]
    n = len(pts)
    out = []
    for i in range(n):
        p = pts[i]
        e1 = (p - pts[i - 1])
        e2 = (pts[(i + 1) % n] - p)
        if e1.length < 1e-9 or e2.length < 1e-9:
            out.append((p.x, p.y))
            continue
        e1.normalize()
        e2.normalize()
        n1, n2 = Vector((-e1.y, e1.x)) * sign, Vector((-e2.y, e2.x)) * sign
        k = 1 + n1.dot(n2)
        q = p + (n1 + n2) * (d / max(k, .35))
        out.append((q.x, q.y))
    return out


def round_corners(poly, r, steps=1, min_turn=math.radians(25)):
    """Cut every corner of a closed 2D polygon that turns more than min_turn by a chamfer of size r (steps=1) or a
    rounded run of steps + 1 points. Corners on edges shorter than 2.5 r are left sharp."""
    pts = [Vector(p) for p in poly]
    n = len(pts)
    out = []
    for i in range(n):
        p, a, b = pts[i], pts[i - 1], pts[(i + 1) % n]
        da, db = (a - p), (b - p)
        if da.length < 2.5 * r or db.length < 2.5 * r:
            out.append((p.x, p.y))
            continue
        turn = math.pi - da.angle(db)
        if turn < min_turn:
            out.append((p.x, p.y))
            continue
        pa, pb = p + da.normalized() * r, p + db.normalized() * r
        if steps <= 1:
            out += [(pa.x, pa.y), (pb.x, pb.y)]
        else:
            for k in range(steps + 1):
                t = k / steps
                q = (pa * (1 - t) + p * t) * (1 - t) + (p * (1 - t) + pb * t) * t   # quadratic Bezier
                out.append((q.x, q.y))
    return out


def _wear(shape, verts):
    for v in verts:
        v[shape.wear] = 1.0


def _faces(shape, rings, cap_start=True, cap_end=True):
    return shape._faces(rings, cap_start, cap_end)


# ----------------------------------------------------------------------------- extrusion
def extrude(shape, profile, depth, loc=(0, 0, 0), rot=(0, 0, 0), axis='X', chamfer=0.0, corner=0.0, taper=1.0,
            caps=(True, True), ends=(True, True)):
    """Extrude a 2D outline over `depth` centred on the origin (axis X: profile is (y, z); Y: (x, z); Z: (x, y)).
    chamfer cuts the end edges listed in `ends` (negative, positive end) in two steps (the middle row worn); corner
    rounds the profile's own corners (one chamfer each); taper (a number, or one per profile axis) scales the
    positive end (sloped walls). caps=False leaves that end open."""
    prof = round_corners(profile, corner) if corner > 0 else list(profile)
    c = min(chamfer, depth * .3)
    h = depth / 2
    rows = []   # (offset inwards, position along the axis, worn)
    if c > 0 and caps[0] and ends[0]:
        rows += [(c, -h, False), (c * .3, -h + c * .3, True), (0, -h + c, False)]
    else:
        rows.append((0, -h, False))
    if c > 0 and caps[1] and ends[1]:
        rows += [(0, h - c, False), (c * .3, h - c * .3, True), (c, h, False)]
    else:
        rows.append((0, h, False))
    ta, tb = (taper, taper) if isinstance(taper, (int, float)) else taper
    rings, worn = [], []
    for off, side, w in rows:
        f = (side + h) / depth
        ka, kb = 1 + (ta - 1) * f, 1 + (tb - 1) * f
        pts = offset2d(prof, off) if off else prof
        ring = []
        for a, b in pts:
            a, b = a * ka, b * kb
            co = {'X': (side, a, b), 'Y': (a, side, b), 'Z': (a, b, side)}[axis]
            ring.append(shape.bm.verts.new(co))
        rings.append(ring)
        if w:
            worn += ring
    _faces(shape, rings, caps[0], caps[1])
    _wear(shape, worn)
    bmesh.ops.transform(shape.bm, matrix=_frame(loc, rot), verts=[v for r in rings for v in r])
    return shape


SMALL = .12   # a block thinner than this in any direction stays a plain box (its chamfer would not show)


def block(shape, size, loc=(0, 0, 0), rot=(0, 0, 0), chamfer=.03, taper=(1, 1), ends=(False, True)):
    """Box on its base (extrude of a rectangle along Z) with its vertical corners cut and the edges round the
    chamfered `ends` (default: the top only, a block stands on something) in two steps, without bmesh bevel: plates,
    bins, blocks. Blocks under SMALL in any size are plain boxes (12 triangles): the chamfer's cost is wasted there."""
    sx, sy, sz = size
    c = 0.0 if min(size) < SMALL else min(chamfer, sx * .3, sy * .3, sz * .3)
    prof = [(-sx / 2, -sy / 2), (sx / 2, -sy / 2), (sx / 2, sy / 2), (-sx / 2, sy / 2)]
    extrude(shape, prof, sz, loc=loc, rot=rot, axis='Z', chamfer=c, corner=c, taper=tuple(taper), ends=ends)
    return shape


# ----------------------------------------------------------------------------- revolution
def lathe(shape, profile, loc=(0, 0, 0), rot=(0, 0, 0), seg=16, caps=(True, True), worn=()):
    """Revolve [(radius, z)...] about local Z, first row to last. A row with radius 0 is a pole (a fan of
    triangles); an end row with a radius is capped (caps). worn lists row indices to mark worn."""
    bm = shape.bm
    rows = []
    for r, z in profile:
        if r <= 1e-5:
            rows.append([bm.verts.new((0, 0, z))])
        else:
            rows.append([bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for a in (k * TAU / seg for k in range(seg))])
    faces = []
    for a, b in zip(rows, rows[1:]):
        if len(a) == 1 and len(b) == 1:
            continue
        if len(a) == 1:
            faces += [bm.faces.new((a[0], b[(i + 1) % seg], b[i])) for i in range(seg)]
        elif len(b) == 1:
            faces += [bm.faces.new((a[i], a[(i + 1) % seg], b[0])) for i in range(seg)]
        else:
            faces += [bm.faces.new((a[i], a[(i + 1) % seg], b[(i + 1) % seg], b[i])) for i in range(seg)]
    if caps[0] and len(rows[0]) > 1:
        faces.append(bm.faces.new(list(reversed(rows[0]))))
    if caps[1] and len(rows[-1]) > 1:
        faces.append(bm.faces.new(rows[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    for i in worn:
        _wear(shape, rows[i])
    bmesh.ops.transform(bm, matrix=_frame(loc, rot), verts=[v for r in rows for v in r])
    return shape


def ring(shape, loop, loc=(0, 0, 0), rot=(0, 0, 0), seg=16, worn=()):
    """Revolve a closed (radius, z) loop about local Z with no caps: collars, lips, hatch coamings, bands."""
    bm = shape.bm
    rows = [[bm.verts.new((r * math.cos(u), r * math.sin(u), z)) for r, z in loop]
            for u in (i * TAU / seg for i in range(seg))]
    n, faces = len(loop), []
    for i in range(seg):
        a, b = rows[i], rows[(i + 1) % seg]
        faces += [bm.faces.new((a[j], b[j], b[(j + 1) % n], a[(j + 1) % n])) for j in range(n)]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    _wear(shape, [r[j] for r in rows for j in worn])
    bmesh.ops.transform(bm, matrix=_frame(loc, rot), verts=[v for r in rows for v in r])
    return shape


# ----------------------------------------------------------------------------- paths
def _tangents(pts, closed):
    n = len(pts)
    out = []
    for i in range(n):
        if closed:
            a, b = pts[i - 1], pts[(i + 1) % n]
        else:
            a, b = pts[max(0, i - 1)], pts[min(n - 1, i + 1)]
        out.append((b - a).normalized())
    return out


def sweep(shape, profile, path, closed=False, caps=True, up=None, worn=()):
    """Sweep a 2D profile [(u, v)...] (u along the path's side normal, v along its binormal) along a 3D polyline,
    with parallel-transported frames and mitred joints. up fixes the first frame's v direction."""
    pts = [Vector(p) for p in path]
    tans = _tangents(pts, closed)
    t0 = tans[0]
    upv = Vector(up) if up else (Vector((0, 0, 1)) if abs(t0.z) < .9 else Vector((1, 0, 0)))
    side = t0.cross(upv).normalized()
    rings, worn_v = [], []
    bm = shape.bm
    seg_dirs = [(pts[(i + 1) % len(pts)] - pts[i]).normalized() for i in range(len(pts) - (0 if closed else 1))]
    for i, (p, t) in enumerate(zip(pts, tans)):
        if i:
            axis = tans[i - 1].cross(t)
            if axis.length > 1e-7:
                side = Matrix.Rotation(tans[i - 1].angle(t), 3, axis.normalized()) @ side
        side = (side - t * side.dot(t)).normalized()
        binorm = t.cross(side).normalized()
        k, bend = 1.0, None
        if closed or 0 < i < len(pts) - 1:
            d0, d1 = seg_dirs[i - 1], seg_dirs[i % len(seg_dirs)]
            cosang = max(-1.0, min(1.0, d0.dot(d1)))
            half = math.acos(cosang) / 2
            if half > 1e-4:
                k = 1 / max(.4, math.cos(half))
                bend = (d1 - d0)
                bend = (bend - t * bend.dot(t)).normalized()
        row = []
        for j, (u, v) in enumerate(profile):
            q = side * u + binorm * v
            if bend is not None:
                q = q + bend * q.dot(bend) * (k - 1)
            row.append(bm.verts.new(p + q))
            if j in worn:
                worn_v.append(row[-1])
        rings.append(row)
    if closed:
        rings.append(rings[0])
    n = len(profile)
    faces = []
    for a, b in zip(rings, rings[1:]):
        faces += [bm.faces.new((a[j], a[(j + 1) % n], b[(j + 1) % n], b[j])) for j in range(n)]
    if caps and not closed:
        faces.append(bm.faces.new(list(reversed(rings[0]))))
        faces.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    _wear(shape, worn_v)
    return shape


def along(path, count=None, pitch=None, closed=False, start=0.0):
    """Frames (point, unit tangent) spaced evenly along a polyline: `count` of them end to end, or one every
    `pitch` metres from `start`."""
    pts = [Vector(p) for p in path]
    if closed:
        pts = pts + [pts[0]]
    segs = [(a, b, (b - a).length) for a, b in zip(pts, pts[1:]) if (b - a).length > 1e-9]
    total = sum(s[2] for s in segs)
    if count is not None:
        if closed:
            ds = [total * i / count for i in range(count)]
        else:
            ds = [total * (i / (count - 1) if count > 1 else .5) for i in range(count)]
    else:
        ds, d = [], start
        while d <= total + 1e-9:
            ds.append(d)
            d += pitch
    out = []
    for d in ds:
        for a, b, L in segs:
            if d <= L + 1e-9:
                t = (b - a) / L
                out.append((a + t * min(d, L), t))
                break
            d -= L
    return out


def place(shape, frame_pt, tangent, fn, normal=(0, 0, 1)):
    """Call fn(matrix) with a frame at frame_pt whose local Y follows tangent and local Z lies towards normal."""
    t = Vector(tangent).normalized()
    nz = Vector(normal)
    nz = (nz - t * nz.dot(t))
    if nz.length < 1e-6:
        nz = Vector((1, 0, 0))
    nz.normalize()
    nx = t.cross(nz)
    m = Matrix((nx, t, nz)).transposed().to_4x4()
    m.translation = Vector(frame_pt)
    fn(m)


# ----------------------------------------------------------------------------- mirror, insets, lofts
@contextlib.contextmanager
def mirrored(shape, axis=0):
    """Everything added to `shape` inside the block is duplicated mirrored across the plane axis = 0 (X default)."""
    before = set(shape.bm.faces)
    yield shape
    new = [f for f in shape.bm.faces if f not in before]
    if not new:
        return
    verts = list({v for f in new for v in f.verts})
    edges = list({e for f in new for e in f.edges})
    dup = bmesh.ops.duplicate(shape.bm, geom=verts + edges + new)
    dverts = [g for g in dup['geom'] if isinstance(g, bmesh.types.BMVert)]
    dfaces = [g for g in dup['geom'] if isinstance(g, bmesh.types.BMFace)]
    s = [1, 1, 1]
    s[axis] = -1
    bmesh.ops.scale(shape.bm, vec=s, verts=dverts)
    bmesh.ops.reverse_faces(shape.bm, faces=dfaces)


def snapshot(shape):
    """Faces present now: pass to inset(..., since=) to touch only geometry built afterwards."""
    return set(shape.bm.faces)


def _inradius(f):
    """Smallest distance from a face's centre to the lines of its edges (a convex face's room for an inset)."""
    c = f.calc_center_median()
    best = math.inf
    for e in f.edges:
        a, b = e.verts[0].co, e.verts[1].co
        d = b - a
        if d.length < 1e-9:
            continue
        best = min(best, (c - a).cross(d).length / d.length)
    return best


def inset(shape, select, width=.03, depth=-.012, since=None, room=2.2):
    """Panel insets: every face built after `since` for which select(centre, normal, face) is true gets an inset
    frame `width` wide and its panel moved `depth` along the normal (negative: recessed). Faces without room for
    it (centre closer than room x width to an edge line) are skipped, so no frame collapses into slivers."""
    faces = []
    for f in shape.bm.faces:
        if since is not None and f in since:
            continue
        if not select(f.calc_center_median(), f.normal, f):
            continue
        if _inradius(f) < width * room:
            continue
        faces.append(f)
    if faces:
        bmesh.ops.inset_individual(shape.bm, faces=faces, thickness=width, depth=depth, use_even_offset=True)
    return len(faces)


def sharp_loft(shape, rings, chamfer=.04, corners=None, loc=(0, 0, 0), rot=(0, 0, 0), min_turn=math.radians(30)):
    """Loft equal-count 3D rings (as Shape.loft) whose corners carry a two-step chamfer `chamfer` wide along the
    whole length, the chamfer's middle line worn. corners: indices to chamfer (default: every corner of the first
    multi-point ring turning more than min_turn). One-point rings stay pointed tips."""
    multi = next(r for r in rings if len(r) > 1)
    n = len(multi)
    if corners is None:
        corners = []
        for i in range(n):
            p, a, b = Vector(multi[i]), Vector(multi[i - 1]), Vector(multi[(i + 1) % n])
            if (a - p).length > 1e-6 and (b - p).length > 1e-6 and math.pi - (a - p).angle(b - p) > min_turn:
                corners.append(i)
    corners = set(corners)
    new_rings, worn_idx = [], []
    for r in rings:
        if len(r) == 1:
            new_rings.append(list(r))
            continue
        out, idx = [], []
        m = len(r)
        for i in range(m):
            p = Vector(r[i])
            if i not in corners:
                out.append(tuple(p))
                continue
            a, b = Vector(r[i - 1]), Vector(r[(i + 1) % m])
            la, lb = (a - p).length, (b - p).length
            c = min(chamfer, la * .3, lb * .3)
            pa, pb = p + (a - p).normalized() * c, p + (b - p).normalized() * c
            mid = (pa + pb) / 2 + (p - (pa + pb) / 2) * .45
            out += [tuple(pa), tuple(mid), tuple(pb)]
            idx.append(len(out) - 2)
        new_rings.append(out)
        worn_idx.append(idx)
    bm = shape.bm
    shape.loft(new_rings, bevel=0)
    bm.verts.ensure_lookup_table()
    total = sum(len(r) for r in new_rings)
    verts = list(bm.verts)[-total:]
    k, wi = 0, 0
    for r in new_rings:
        if len(r) > 1:
            for j in worn_idx[wi]:
                verts[k + j][shape.wear] = 1.0
            wi += 1
        k += len(r)
    if any(loc) or any(rot):
        bmesh.ops.transform(bm, matrix=_frame(loc, rot), verts=verts)
    return shape


# ----------------------------------------------------------------------------- boolean cut-outs
def cut(shape, build):
    """Boolean difference: build(tool) fills a scratch Shape with the cutter (closed solids); the MANIFOLD solver cuts
    it out of everything in `shape`. Only for parts that are one closed solid (a hull plate, a pod), where the cut
    is cheap and clean; returns False (shape unchanged) when the solver gives nothing back."""
    tool = kit.Shape()
    build(tool)
    scene = bpy.context.scene
    me_a, me_b = bpy.data.meshes.new('_mb27_cut_a'), bpy.data.meshes.new('_mb27_cut_b')
    shape.bm.to_mesh(me_a)
    tool.bm.to_mesh(me_b)
    tool.bm.free()
    oa, ob = bpy.data.objects.new('_mb27_cut_a', me_a), bpy.data.objects.new('_mb27_cut_b', me_b)
    scene.collection.objects.link(oa)
    scene.collection.objects.link(ob)
    ok = False
    before = shape.bm.calc_volume(signed=True)
    try:
        mod = oa.modifiers.new('cut', 'BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.solver = 'MANIFOLD'   # EXACT turned this kit's closed solids inside out (volume < 0) in Blender 4.5
        mod.object = ob
        dg = bpy.context.evaluated_depsgraph_get()
        dg.update()
        res = bpy.data.meshes.new_from_object(oa.evaluated_get(dg))
        check = bmesh.new()
        check.from_mesh(res)
        after = check.calc_volume(signed=True) if check.faces else 0.0
        check.free()
        if 0 < after < before:   # a real cut: still a positive solid, smaller than before
            shape.bm.clear()
            shape.bm.from_mesh(res)
            shape.wear = shape.bm.verts.layers.float.get('wear') or shape.bm.verts.layers.float.new('wear')
            ok = True
        bpy.data.meshes.remove(res)
    finally:
        bpy.data.objects.remove(oa)
        bpy.data.objects.remove(ob)
        bpy.data.meshes.remove(me_a)
        bpy.data.meshes.remove(me_b)
    return ok


# ----------------------------------------------------------------------------- greebles
def greebles(shape, origin, u, v, size, count, seed, height=(.04, .14), fill=.7, chamfer=.015, vents=None,
             avoid=()):
    """Scatter `count` small blocks over the size = (su, sv) rectangle centred at origin on a surface spanned by unit
    vectors u, v (normal u x v): a jittered grid, one block per chosen cell, `fill` of the cell at most, heights in
    `height`. vents (a Shape) gets every third one as a flat slatted vent instead. avoid: (point, radius) pairs to
    keep clear. Deterministic for a seed."""
    rng = random.Random(seed)
    u, v, o = Vector(u).normalized(), Vector(v).normalized(), Vector(origin)
    n = u.cross(v).normalized()
    su, sv = size
    cols = max(1, int(round(math.sqrt(count * su / sv))))
    rows = max(1, int(math.ceil(count / cols)))
    cells = [(i, j) for i in range(cols) for j in range(rows)]
    rng.shuffle(cells)
    rot = Matrix((u, v, n)).transposed().to_euler('XYZ')
    made = 0
    for i, j in cells[:count]:
        cw, ch = su / cols, sv / rows
        w, d = cw * rng.uniform(.35, fill), ch * rng.uniform(.35, fill)
        cu = -su / 2 + (i + .5) * cw + rng.uniform(-1, 1) * (cw - w) / 2
        cv = -sv / 2 + (j + .5) * ch + rng.uniform(-1, 1) * (ch - d) / 2
        p = o + u * cu + v * cv
        if any((p - Vector(q)).length < r for q, r in avoid):
            continue
        h = rng.uniform(*height)
        if vents is not None and made % 3 == 2:
            for k in range(3):
                vu = cu - w / 2 + (k + .5) * w / 3
                q = o + u * vu + v * cv + n * .012
                block(vents, (w / 3 * .6, d, .025), loc=tuple(q), rot=tuple(rot), chamfer=0)
        else:
            block(shape, (w, d, h), loc=tuple(p + n * (h / 2 - .01)), rot=tuple(rot), chamfer=min(chamfer, h * .3))
        made += 1
    return made


# ----------------------------------------------------------------------------- clean-up
def clean(asset, dist=2e-4):
    """Dissolve zero-length edges and zero-area faces in every part (bmesh bevels on lofted tips leave them), then
    drop loose vertices. Run after the builder, before asset.finish()."""
    removed = 0
    for sh in asset.shapes.values():
        bm = sh.bm
        if not bm.faces:
            continue
        before = len(bm.faces)
        bmesh.ops.dissolve_degenerate(bm, dist=dist, edges=list(bm.edges))
        loose = [v for v in bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context='VERTS')
        # A polygon with a straight corner (a T-junction left by a bevel) can triangulate into a zero-area
        # triangle in the exporter: triangulate those few here the 'beauty' way, which never makes a triangle of
        # three points in a line.
        straight = [f for f in bm.faces if len(f.verts) > 3 and any(lp.calc_angle() > math.radians(179.0)
                                                                     for lp in f.loops)]
        if straight:
            bmesh.ops.triangulate(bm, faces=straight, quad_method='BEAUTY', ngon_method='BEAUTY')
            bmesh.ops.dissolve_degenerate(bm, dist=dist, edges=list(bm.edges))
        removed += before - len(bm.faces)
    return removed


def degenerate_triangles(asset, area=1e-8):
    """Triangles under `area` (m^2) the exporter's triangulation would produce, counted over all parts (a check)."""
    count = 0
    for sh in asset.shapes.values():
        for f in sh.bm.faces:
            if len(f.verts) == 3 and f.calc_area() < area:
                count += 1
    return count
