"""Full fix prompt L3: the barrels the bosses' twin guns need (DECISIONS "Sửa lỗi tổng hợp L3").

The boss weapons now fire at their real cadence; where a boss lost more than a fifth of its DPS it was made up with more
barrels firing together (balance.json "barrels", "salvoMode": "SIMULTANEOUS"; Tools/balance/fix_boss_weapons.py MAKEUP),
and Behemoth's 2A65 and Cerberus's copy of it are the wave 1 twin. Each barrel needs a muzzle of its own (Muzzle_b<k>_<tag>,
as prompt 34 L4's mb_p34_barrels), so:

  TWIN    a gun with one barrel gets a second one: the barrel and the pieces on its axis (sleeve, brake, bore evacuator)
          are copied beside it, the pair centred on the old axis (the gap ~2.4 x the barrel's width), so the mount's
          Muzzle_<slot> stays between them;
  EXTRA   a mount that already has its barrels only gets the per-barrel muzzles;
  EMPTY   a launch point with no barrel to copy (a submarine's deck hatch) gets its per-barrel muzzles side by side.

Run last, after mb_p34_barrels.wrap (build_assets.all_builders).
"""
import bmesh

import mb_p34_barrels as P

# model -> the muzzle pivots (Blender names, before finish) whose single barrel becomes a twin
TWIN = {
    # Prompt 35 wave 8 (lane A): behemoth's rebuilt turrets model both barrels and their per-barrel muzzles.
    'typhon': ['Muzzle_gun'],
    # hydra_sub: play-test 14 wave M3's builder (mb_pt14_m3) models its twins and their per-barrel muzzles.
    'monster': ['Muzzle_gun', 'Muzzle_gun__001'],
}
# model -> muzzles that already have two barrels (only the per-barrel muzzles)
EXTRA = {
    # daedalus: play-test 14 wave M2's builder (mb_pt14_m2) models both barrels and their per-barrel muzzles.
    # fortress_bastion: play-test 14 wave M1's builder (mb_pt14_m1) models its twins' per-barrel muzzles itself.
    # Prompt 35 wave 4 (lane C): moloch's rebuilt turrets model both barrels themselves.
    'moloch': ['Muzzle_main', 'Muzzle_gun', 'Muzzle_gun__001', 'Muzzle_gun__002'],
    # Prompt 35 wave 11 (lane C): cerberus's rebuilt turret models both 152 mm barrels itself.
    'cerberus': ['Muzzle_main'],
}
# model -> {muzzle: (barrels, gap m)} with no barrel geometry
EMPTY = {
}


def _components(bm):
    """The bmesh's connected pieces, as lists of BMVerts."""
    bm.verts.index_update()
    seen = set()
    out = []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack, piece = [v], []
        seen.add(v.index)
        while stack:
            u = stack.pop()
            piece.append(u)
            for e in u.link_edges:
                w = e.other_vert(u)
                if w.index not in seen:
                    seen.add(w.index)
                    stack.append(w)
        out.append(piece)
    return out


def _box(piece):
    xs = [v.co.x for v in piece]
    ys = [v.co.y for v in piece]
    zs = [v.co.z for v in piece]
    return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))


def twin(a, wanted):
    muzzle = P._resolve(a, wanted)
    if muzzle is None:
        print(f'FIX_BARRELS {a.name}: no pivot {wanted}')
        return
    tips = P.barrels_of(a, muzzle)
    if len(tips) != 1:
        print(f'FIX_BARRELS {a.name}: {wanted}: {len(tips)} barrel(s), not a single one: left as it is')
        return
    bx, bz = tips[0]
    m = a.pivots[muzzle]
    parent = m.parent.name if m.parent is not None else None
    parent_key = next((k for k, o in a.pivots.items() if o is m.parent), parent)
    # The barrel itself: the longest thin piece on the axis.
    cands = []
    for (name, mat, par), shape in a.shapes.items():
        if par != parent_key or not shape.bm.verts:
            continue
        for piece in _components(shape.bm):
            (x0, x1), (y0, y1), (z0, z1) = _box(piece)
            w = max(x1 - x0, z1 - z0, 1e-3)
            if abs((x0 + x1) / 2 - bx) < 0.2 and abs((z0 + z1) / 2 - bz) < 0.2 and (y1 - y0) > P.THIN * w:
                cands.append(((y1 - y0), w, (y0, y1)))
    if not cands:
        print(f'FIX_BARRELS {a.name}: {wanted}: no barrel piece found')
        return
    _length, width, (by0, by1) = max(cands)
    gap = max(2.4 * width, 0.3)
    copied = 0
    for (name, mat, par), shape in list(a.shapes.items()):
        if par != parent_key or not shape.bm.verts:
            continue
        bm = shape.bm
        for piece in _components(bm):
            (x0, x1), (y0, y1), (z0, z1) = _box(piece)
            cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
            if abs(cx - bx) > 1.5 * width or abs(cz - bz) > 1.5 * width:
                continue
            if max(x1 - x0, z1 - z0) > 2.6 * width or y1 < by0 - 0.2 or y0 > by1 + 0.2:
                continue
            verts = list(piece)
            edges = list({e for v in verts for e in v.link_edges})
            faces = list({f for v in verts for f in v.link_faces})
            ret = bmesh.ops.duplicate(bm, geom=verts + edges + faces)
            new = [g for g in ret['geom'] if isinstance(g, bmesh.types.BMVert)]
            for v in verts:
                v.co.x -= gap / 2
            for v in new:
                v.co.x += gap / 2
            copied += 1
    print(f'FIX_BARRELS {a.name}: {wanted}: twin, {copied} pieces copied {gap:.2f} m apart (barrel {width:.2f} m wide)')


def empties(a, wanted, n, gap):
    muzzle = P._resolve(a, wanted)
    if muzzle is None:
        print(f'FIX_BARRELS {a.name}: no pivot {wanted}')
        return
    tag = wanted.replace('Muzzle_', '').replace('__', '_').replace('.', '_')
    for k in range(n):
        a.pivot(f'Muzzle_b{k + 1}_{tag}', ((k - (n - 1) / 2) * gap, 0.0, 0.0), parent=muzzle)
    print(f'FIX_BARRELS {a.name}: {wanted}: {n} launch points {gap} m apart')


def finish(a, name):
    for wanted in TWIN.get(name, []):
        twin(a, wanted)
    P.add_barrels(a, TWIN.get(name, []) + EXTRA.get(name, []))
    for wanted, (n, gap) in EMPTY.get(name, {}).items():
        empties(a, wanted, n, gap)


def wrap(builders):
    """The builders with the twin barrels and the per-barrel muzzles added after each listed model's own build."""
    out = dict(builders)
    for name in set(TWIN) | set(EXTRA) | set(EMPTY):
        for key in (name, f'{name}_hd'):
            if key not in out:
                continue
            build, options = out[key]

            def run(a, build=build, name=name, **kw):
                build(a, **kw)
                finish(a, name)
            run.__name__ = getattr(build, '__name__', key)
            run.__doc__ = (build.__doc__ or '') + '\n\nFull fix L3: twin barrels and a muzzle for every barrel.'
            out[key] = (run, options)
    return out
