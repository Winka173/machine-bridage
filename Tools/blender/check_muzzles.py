"""blender -b --python Tools/blender/check_muzzles.py -- <name> [<name> ...]

Checks that rounds leave from the right place in exported models (Resources/Models/<name>.glb), against the rig
rules of ModelLibrary.cs / VehicleView.cs:
  * every `Muzzle_<slot>` empty: its world position, its parent, and the barrel it belongs to: the mesh under the
    same parent (or under the muzzle itself) whose bounding box holds the muzzle's bore axis (X/Z, 15 cm
    slack) and whose front end (-Y) is nearest, scored by the distance along Y plus the offset from the box's
    middle across it. PASS when the muzzle lies within 0.15 m of that front end;
  * a ray fired forward (-Y) from each muzzle must clear the model for 1.5 m (no muzzle buried in or behind
    another part);
  * the elevation rig AddElevation builds (Turret children matching BarrelPattern; missile muzzles only when a
    launcher rides): its trunnion and the barrel's rest pitch;
  * launcher groups AddLaunchPoints finds (Launch_tubes, Missiles, Pods, Miniguns ...: vertex groups split by X
    gaps of 0.35 m or more): each group's launch point must sit within 6 cm of a muzzle of its slot;
  * twin barrels (Main_cannon / Main_cannon_2 ...): VehicleView alternates them only if their tips stand more
    than 0.25 m apart.
Prints one line per muzzle and MUZZLES_OK / MUZZLES_FAIL at the end.
"""
import math
import re
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

MODELS = Path(__file__).resolve().parents[2] / 'Assets' / 'MachineBrigade' / 'Resources' / 'Models'
MUZZLE = re.compile(r'^Muzzle_(main|coax|mg|missile|rocket|gun|aam|door_l|door_r|ramp|agl_l|agl_r)(\.\d+)?$', re.I)
BARREL = re.compile(r'^(main_cannon|muzzle_brake|mortar_tube|rocket_tubes|tubes|tube_bores|pod(?!_frame)|atgm_pod|launcher|coax|'
                    r'muzzle_main|muzzle_coax|muzzle_missile|muzzle_rocket)\w*(\.\d+)?$', re.I)
TWIN = re.compile(r'^(?:Main_cannon|Muzzle_brake)_(\d+|L|R)(?![a-z])', re.I)
PAIRS = {'rocket': ('Pods', 'Rocket_pod', 'Rocket_pods', 'Standoff_missile', 'Ordnance_bodies', 'Bomb_bodies'),
         'missile': ('Missiles', 'Launch_tubes', 'Missile_pack', 'ATGM_pod', 'Standoff_missile', 'Missile_racks',
                     'Bomb_bodies', 'Ordnance_bodies'),
         'gun': ('Miniguns',), 'main': ('Pods',)}
TOL, CLEAR, SLACK = .15, 1.5, .15


def bounds(o):
    mw = o.matrix_world
    vs = [mw @ v.co for v in o.data.vertices]
    return (Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs))),
            Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs))), vs)


def _chain(o):
    """o and its ancestors."""
    out = []
    while o is not None:
        out.append(o)
        o = o.parent
    return out


def _hits(moving, meshes, static, centre, angle):
    """Static parts that the moving parts, turned by `angle` about the vertical through `centre`, overlap."""
    rot = Matrix.Translation(centre) @ Matrix.Rotation(angle, 4, 'Z') @ Matrix.Translation(-centre)
    verts, polys = [], []
    for o in moving:
        base = len(verts)
        verts += [rot @ v for v in meshes[o][2]]
        polys += [tuple(base + i for i in f.vertices) for f in o.data.polygons]
    tree = BVHTree.FromPolygons(verts, polys)
    return {o for o, t in static.items() if tree.overlap(t)}


def check(name):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(MODELS / f'{name}.glb'))
    scene = bpy.context.scene
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    objs = list(scene.objects)
    meshes = {o: bounds(o) for o in objs if o.type == 'MESH'}
    ok = True
    print(f'== {name}')
    lo = Vector((min(b[0].x for b in meshes.values()), min(b[0].y for b in meshes.values()), min(b[0].z for b in meshes.values())))
    hi = Vector((max(b[1].x for b in meshes.values()), max(b[1].y for b in meshes.values()), max(b[1].z for b in meshes.values())))
    size = hi - lo
    tris = 0
    for o in meshes:
        o.data.calc_loop_triangles()
        tris += len(o.data.loop_triangles)
    print(f'   bounds x {lo.x:.2f}..{hi.x:.2f}  y {lo.y:.2f}..{hi.y:.2f}  z {lo.z:.2f}..{hi.z:.2f}  '
          f'(width {size.x:.2f} x length {size.y:.2f} x height {size.z:.2f} m), {tris} triangles')
    pivots = [o for o in objs if o.type == 'EMPTY']
    for p in sorted(pivots, key=lambda o: o.name):
        if re.match(r'^(Turret|Radar|Mount_|Rotor|Searchlight|Erector)', p.name):
            w = p.matrix_world.translation
            print(f'   pivot  {p.name:<20} parent {p.parent.name if p.parent else "(root)":<16} at ({w.x:6.2f}, {w.y:6.2f}, {w.z:5.2f})')
    muzzles = sorted((o for o in pivots if MUZZLE.match(o.name)), key=lambda o: o.name)
    for mz in muzzles:
        m = mz.matrix_world.translation
        best = None
        for o, (blo, bhi, _) in meshes.items():
            if o.parent not in (mz.parent, mz):
                continue
            if not (blo.x - SLACK <= m.x <= bhi.x + SLACK and blo.z - SLACK <= m.z <= bhi.z + SLACK):
                continue
            dy = abs(m.y - blo.y)
            lateral = (Vector((m.x, m.z)) - Vector(((blo.x + bhi.x) / 2, (blo.z + bhi.z) / 2))).length
            score = dy + lateral
            if best is None or score < best[0]:
                best = (score, o, dy, lateral)
        hit, at, _, _, hobj, _ = scene.ray_cast(deps, m + Vector((0, -.01, 0)), Vector((0, -1, 0)), distance=CLEAR)
        blocked = f'  BLOCKED by {hobj.name} at {(at - m).length:.2f} m' if hit else ''
        if best is None:
            verdict, part = 'FAIL', 'no barrel mesh holds its bore axis'
        else:
            _, o, dy, lateral = best
            verdict = 'PASS' if dy <= TOL and not hit else 'FAIL'
            part = f'{o.name:<18} front end {dy:.3f} m, {lateral:.3f} m off its axis'
        ok &= verdict == 'PASS'
        print(f'   {verdict} {mz.name:<20} parent {mz.parent.name if mz.parent else "(root)":<10} '
              f'at ({m.x:6.2f}, {m.y:6.2f}, {m.z:5.2f})  {part}{blocked}')
    # Elevation rig, as ModelLibrary.AddElevation builds it.
    turret = next((o for o in pivots if re.match(r'^Turret(\.\d+)?$', o.name)), None)
    if turret:
        kids = [c for c in turret.children if BARREL.match(c.name)]
        rides = any(re.match(r'^(launcher|tubes|pod|atgm_pod)', c.name, re.I) for c in kids)
        if not rides:
            kids = [c for c in kids if not c.name.lower().startswith('muzzle_missile')]
        main = [c for c in kids if c.name.lower().startswith('muzzle_main')]
        pts = [v for c in kids for d in [c] + list(c.children_recursive) if d in meshes for v in meshes[d][2]]
        if main and pts:
            glo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
            ghi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
            piv = Vector(((glo.x + ghi.x) / 2, ghi.y - (ghi.y - glo.y) * .06, glo.z + (ghi.z - glo.z) * .3))
            aim = main[-1].matrix_world.translation - piv
            pitch = math.degrees(math.atan2(aim.z, max(.01, Vector((aim.x, aim.y)).length)))
            kinds = ', '.join(sorted({re.sub(r'[._]\d+$', '', c.name) for c in kids}))
            print(f'   elevation: {len(kids)} parts ({kinds}) about ({piv.x:.2f}, {piv.y:.2f}, {piv.z:.2f}), '
                  f'rest pitch {pitch:.1f} deg')
        else:
            print('   elevation: none (no Muzzle_main under the Turret)')
        tips = {}
        for c in turret.children:
            if re.match(r'^(main_cannon|muzzle_brake)', c.name, re.I) and c in meshes:
                t = TWIN.match(c.name)
                k = 0 if not t else {'L': 0, 'R': 1}.get(t.group(1).upper(), None)
                k = int(t.group(1)) - 1 if t and k is None else k
                if k not in tips or c.name.lower().startswith('muzzle_brake'):
                    tips[k] = c
        if len(tips) > 1:
            cs = {k: (meshes[o][0] + meshes[o][1]) / 2 for k, o in tips.items()}
            spread = max((Vector((cs[i].x - cs[j].x, cs[i].z - cs[j].z))).length for i in cs for j in cs)
            state = 'alternate' if spread > .25 else 'do NOT alternate'
            print(f'   twin barrels {sorted(o.name for o in tips.values())}: tips {spread:.2f} m apart, they {state}')
            ok &= spread > .25
    # Traverse sweeps: every Turret / Mount_* / Radar pivot turned all the way round (15-degree steps) must not
    # run into a part it clears at rest.
    for p in sorted(pivots, key=lambda o: o.name):
        if not re.match(r'^(Turret|Mount_[a-z]+|Radar)(\.\d+)?$', p.name, re.I):
            continue
        moving = [o for o in meshes if p in _chain(o)]
        others = [o for o in meshes if o not in moving and not any(q in _chain(o) for q in pivots
                                                                   if q is not p and re.match(r'^(Mount_|Radar)', q.name))]
        if not moving or not others:
            continue
        static = {o: BVHTree.FromPolygons(meshes[o][2], [tuple(f.vertices) for f in o.data.polygons]) for o in others}
        c = p.matrix_world.translation
        rest = _hits(moving, meshes, static, c, 0.0)
        clashes = {}
        for k in range(1, 24):
            for o in _hits(moving, meshes, static, c, math.radians(k * 15)) - rest:
                clashes.setdefault(o.name, []).append(k * 15)
        if clashes:
            ok = False
            for n, angles in sorted(clashes.items()):
                print(f'   FAIL sweep {p.name}: runs into {n} at {angles[0]}..{angles[-1]} deg')
        else:
            print(f'   PASS sweep {p.name}: turns all the way round clear of the model')
    # Launch points, as ModelLibrary.AddLaunchPoints finds them.
    by_name = {}
    for o in meshes:
        by_name.setdefault(re.sub(r'\.\d+$', '', o.name), []).append(o)
    for slot, names in PAIRS.items():
        slot_muzzles = [mz for mz in muzzles if mz.name.lower().startswith(f'muzzle_{slot}')]
        if not slot_muzzles:
            continue
        for part in names:
            if part not in by_name:
                continue
            pts = sorted((v for o in by_name[part] for v in meshes[o][2]), key=lambda v: v.x)
            groups, start = [], 0
            for i in range(1, len(pts) + 1):
                if i < len(pts) and pts[i].x - pts[i - 1].x < .35:
                    continue
                g = pts[start:i]
                glo = Vector((min(p.x for p in g), min(p.y for p in g), min(p.z for p in g)))
                ghi = Vector((max(p.x for p in g), max(p.y for p in g), max(p.z for p in g)))
                groups.append(Vector(((glo.x + ghi.x) / 2, glo.y, (glo.z + ghi.z) / 2)))
                start = i
            if len(groups) < 2:
                continue
            for g in groups:
                near = min(slot_muzzles, key=lambda mz: (mz.matrix_world.translation - g).length)
                d = (near.matrix_world.translation - g).length
                verdict = 'PASS' if d < .06 else 'FAIL'
                ok &= verdict == 'PASS'
                print(f'   {verdict} launch point ({slot}, {part}) at ({g.x:6.2f}, {g.y:6.2f}, {g.z:5.2f})  {d:.3f} m from {near.name}')
            break
    return ok


args = sys.argv[sys.argv.index('--') + 1:]
results = [check(n) for n in args]
print('MUZZLES_OK' if all(results) else 'MUZZLES_FAIL')
