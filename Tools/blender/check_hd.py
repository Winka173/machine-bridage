"""blender -b --python check_hd.py -- <normal_dir> <hd_dir> <name> [<name> ...]

Compares <hd_dir>/<name>_hd.glb with <normal_dir>/<name>.glb against the runtime contract of ModelLibrary.cs:
  * every pivot / empty: same name, same parent, same world position;
  * every normal mesh part still present (same parent);
  * hull footprint (measure_hulls.py rules) unchanged, HD inside the normal overall bounds;
  * the elevation group (Turret children matching BarrelPattern), the recoil parts and the launcher parts
    (AddLaunchPoints names) have identical bounds, so trunnion, muzzle and launch points are unchanged;
  * spinning pivots (rotor blur radius) keep their bounds;
  * no new part name matches a runtime pattern.
Prints one line per model and CHECK_OK / CHECK_FAIL at the end.
"""
import json
import re
import sys
from pathlib import Path

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:]
normal_dir, hd_dir, names = Path(args[0]), Path(args[1]), args[2:]

BARREL = re.compile(r'^(main_cannon|muzzle_brake|mortar_tube|rocket_tubes|tubes|tube_bores|pod(?!_frame)|atgm_pod|launcher|coax|'
                    r'muzzle_main|muzzle_coax|muzzle_missile|muzzle_rocket)\w*(\.\d+)?$', re.I)
RECOIL = re.compile(r'^(main_cannon|muzzle_brake)', re.I)
MUZZLE = re.compile(r'^Muzzle_(main|coax|mg|missile|rocket|gun|aam|door_l|door_r|ramp|agl_l|agl_r)(\.\d+)?$', re.I)
MOUNT = re.compile(r'^Mount_([a-z]+)(\.\d+)?$', re.I)
SPIN = [re.compile(p) for p in (r'^Rotor(_rear|_front|_\d+)?(\.\d+)?$', r'^Tail_rotor(\.\d+)?$',
                                r'^Radar(_search|_\d+)?(\.\d+)?$', r'^Propeller(_\d+)?(\.\d+)?$')]
LOOSE = re.compile(r'^(Bombs|Pump_beam|Erector|Searchlight)(\.\d+)?$')
TURRET = re.compile(r'^Turret(\.\d+)?$')
LAUNCH = {'Pods', 'Rocket_pod', 'Rocket_pods', 'Pod_face', 'Tubes_bore', 'Rocket_tubes_face', 'Box_face', 'Launcher_face',
          'Launcher_tubes_bore', 'Tubes', 'Missiles', 'Launch_tubes', 'Missile_pack', 'ATGM_pod', 'Standoff_missile',
          'Missile_racks', 'Launcher_covers', 'Miniguns'}
HULL_SKIP = ('Turret', 'Mount_', 'Rotor', 'Tail_rotor', 'Propeller', 'Radar', 'Bombs', 'Erector', 'Searchlight')
RIG = re.compile(r'^(main_cannon|muzzle_brake|barrel|cannon|muzzle|turret_head)(?![a-z])', re.I)
TOL = 1e-3


def load(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(path))
    bpy.context.view_layer.update()
    objs = {}
    for o in bpy.context.scene.objects:
        rec = {'type': o.type, 'parent': o.parent.name if o.parent else None,
               'pos': tuple(o.matrix_world.translation), 'obj': o}
        if o.type == 'MESH':
            mw = o.matrix_world
            vs = [mw @ v.co for v in o.data.vertices]
            rec['verts'] = len(vs)
            rec['lo'] = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
            rec['hi'] = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
            o.data.calc_loop_triangles()
            rec['tris'] = len(o.data.loop_triangles)
            rec['mats'] = [m.name for m in o.data.materials if m]
        objs[o.name] = rec
    # snapshot: plain data only (objects die on the next factory reset)
    out = {}
    for n, r in objs.items():
        o = r.pop('obj')
        chain = []
        p = o
        while p is not None:
            chain.append(p.name)
            p = p.parent
        r['chain'] = chain
        out[n] = r
    return out


def union(recs):
    recs = [r for r in recs if 'lo' in r]
    if not recs:
        return None
    lo = Vector((min(r['lo'].x for r in recs), min(r['lo'].y for r in recs), min(r['lo'].z for r in recs)))
    hi = Vector((max(r['hi'].x for r in recs), max(r['hi'].y for r in recs), max(r['hi'].z for r in recs)))
    return lo, hi


def fmt(b):
    return 'none' if b is None else f'({b[0].x:.3f},{b[0].y:.3f},{b[0].z:.3f})..({b[1].x:.3f},{b[1].y:.3f},{b[1].z:.3f})'


def same(b1, b2, tol=TOL):
    if b1 is None or b2 is None:
        return b1 is None and b2 is None
    return all(abs(a - b) <= tol for a, b in zip(list(b1[0]) + list(b1[1]), list(b2[0]) + list(b2[1])))


def inside(inner, outer, tol=2e-3):
    return all(inner[0][i] >= outer[0][i] - tol and inner[1][i] <= outer[1][i] + tol for i in range(3))


def hull(objs):
    return union([r for r in objs.values() if r['type'] == 'MESH' and not any(c.startswith(HULL_SKIP) for c in r['chain'])])


def barrel_group(objs):
    turret = next((n for n in objs if TURRET.match(n)), None)
    if not turret:
        return None, None
    tp = Vector(objs[turret]['pos'])
    kids = [n for n, r in objs.items() if r['parent'] == turret and BARREL.match(n)]
    recs = []
    for n in kids:  # the part itself and anything under it
        recs += [r for r in objs.values() if r['type'] == 'MESH' and n in r['chain']]
    b = union(recs)
    if b:
        b = (b[0] - tp, b[1] - tp)
    return b, sorted(kids)


def recoil(objs):
    turret = next((n for n in objs if TURRET.match(n)), None)
    if not turret:
        return None
    return union([r for n, r in objs.items() if r['parent'] == turret and RECOIL.match(n) and r['type'] == 'MESH'])


def spinners(objs):
    out = {}
    for n in objs:
        if any(p.match(n) for p in SPIN):
            out[n] = union([r for r in objs.values() if r['type'] == 'MESH' and n in r['chain']])
    return out


def base(n):
    return re.sub(r'\.\d+$', '', n)


results, failed = {}, False
for name in names:
    A = load(normal_dir / f'{name}.glb')
    B = load(hd_dir / f'{name}_hd.glb')
    problems = []
    # 1. empties
    ea = {n: r for n, r in A.items() if r['type'] != 'MESH'}
    eb = {n: r for n, r in B.items() if r['type'] != 'MESH'}
    for n, r in ea.items():
        if n not in eb:
            problems.append(f'pivot {n} missing')
            continue
        d = (Vector(r['pos']) - Vector(eb[n]['pos'])).length
        if d > 1e-4:
            problems.append(f'pivot {n} moved {d:.4f} m')
        if r['parent'] != eb[n]['parent']:
            problems.append(f'pivot {n} parent {r["parent"]} -> {eb[n]["parent"]}')
    for n in eb:
        if n not in ea:
            problems.append(f'extra pivot {n}')
    # 2. mesh parts
    ma = {n: r for n, r in A.items() if r['type'] == 'MESH'}
    mb = {n: r for n, r in B.items() if r['type'] == 'MESH'}
    for n, r in ma.items():
        if n not in mb:
            problems.append(f'part {n} missing')
        elif r['parent'] != mb[n]['parent']:
            problems.append(f'part {n} parent {r["parent"]} -> {mb[n]["parent"]}')
    new = sorted(set(mb) - set(ma))
    for n in new:
        bn = base(n)
        if (MUZZLE.match(bn) or MOUNT.match(bn) or LOOSE.match(bn) or TURRET.match(bn) or RIG.match(bn)
                or any(p.match(n) for p in SPIN) or bn in LAUNCH):
            problems.append(f'new part {n} matches a runtime pattern')
        if mb[n]['parent'] and TURRET.match(mb[n]['parent']) and BARREL.match(n):
            problems.append(f'new turret part {n} joins the elevation group')
    # 3. hull footprint and overall bounds
    ha, hb = hull(A), hull(B)
    # The footprint (x, y) must match exactly; the ground line may shift a few millimetres (tread lugs).
    if not (same((ha[0].xy.to_3d(), ha[1].xy.to_3d()), (hb[0].xy.to_3d(), hb[1].xy.to_3d()))
            and abs(ha[0].z - hb[0].z) <= 5e-3 and abs(ha[1].z - hb[1].z) <= TOL):
        problems.append(f'hull bounds {fmt(ha)} -> {fmt(hb)}')
    oa, ob = union(list(ma.values())), union(list(mb.values()))
    if not inside(ob, oa):
        problems.append(f'overall bounds grow {fmt(oa)} -> {fmt(ob)}')
    # 4. elevation group, recoil, launchers, spinners
    ga, ka = barrel_group(A)
    gb, kb = barrel_group(B)
    if ka != kb:
        problems.append(f'elevation parts {ka} -> {kb}')
    if not same(ga, gb, 5e-4):
        problems.append(f'elevation bounds {fmt(ga)} -> {fmt(gb)}')
    if not same(recoil(A), recoil(B), 5e-4):
        problems.append(f'recoil bounds {fmt(recoil(A))} -> {fmt(recoil(B))}')
    for n in sorted(set(base(k) for k in ma) & LAUNCH):
        ra = union([r for k, r in ma.items() if base(k) == n])
        rb = union([r for k, r in mb.items() if base(k) == n])
        va = sum(r['verts'] for k, r in ma.items() if base(k) == n)
        vb = sum(r['verts'] for k, r in mb.items() if base(k) == n)
        if not same(ra, rb, 5e-4) or va != vb:
            problems.append(f'launcher part {n} changed ({va} -> {vb} verts)')
    sa, sb = spinners(A), spinners(B)
    for n in sa:
        if n in sb and not same(sa[n], sb[n], 2e-3):
            problems.append(f'spinner {n} bounds {fmt(sa[n])} -> {fmt(sb[n])}')
    ta = sum(r['tris'] for r in ma.values())
    tb = sum(r['tris'] for r in mb.values())
    mats_a = sorted({m for r in ma.values() for m in r['mats']})
    mats_b = sorted({m for r in mb.values() for m in r['mats']})
    results[name] = {'tris': [ta, tb, round(tb / ta, 2)], 'pivots': len(ea), 'parts': [len(ma), len(mb)],
                     'new_materials': sorted(set(mats_b) - set(mats_a)), 'problems': problems}
    failed |= bool(problems)
    print(f'CHECK {name}: tris {ta} -> {tb} (x{tb / ta:.2f}), pivots {len(ea)} ok={not any("pivot" in p for p in problems)}, '
          f'parts {len(ma)} -> {len(mb)}, hull {fmt(hb)}; ' + ('OK' if not problems else 'PROBLEMS: ' + '; '.join(problems)))
print('CHECK_JSON ' + json.dumps(results))
print('CHECK_FAIL' if failed else 'CHECK_OK')
