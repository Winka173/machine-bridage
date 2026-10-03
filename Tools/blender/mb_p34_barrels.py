"""Prompt 34 L4: a muzzle for every barrel of the guns that fire their barrels together (DECISIONS "Prompt 34 L4").

The ships' triple and twin turrets, the heavy turret, the headquarters' twin 152 mm and the super tank's twin 140 mm fire
every barrel in one volley (balance.json "barrels", "salvoMode": "SIMULTANEOUS"). Each barrel gets an empty of its own,
`Muzzle_b<k>_<tag>`, a child of the mount's `Muzzle_<slot>` at the same depth, beside it on the barrel's axis (k from left
to right). ModelLibrary.AddBarrelPoints turns these into the barrels' launch points, so each round and flash leaves from
its own barrel. The names never match the runtime's `Muzzle_<slot>` pattern, so the k-th mount of a slot is still the k-th
`Muzzle_<slot>`.

The barrels are found in the builder's own meshes, before finish: the connected pieces of the meshes beside the muzzle (the
same parent pivot) that are long and thin along the model's front (-Y), whose front end is level with the muzzle. Pieces
on one axis (a barrel and its sleeve, its bore) count as one barrel. A mount with fewer than two barrels gets nothing (a
bare pivot, such as Kraken's launch cells).
"""
import bmesh  # noqa: F401  (the shapes are bmesh)
from mathutils import Vector

# model -> the muzzle pivots (Blender names, before finish turns "__001" into ".001") of the guns that fire together
TARGETS = {
    # Prompt 35 wave 8 (lane A): leviathan's rebuilt turrets write their own per-barrel muzzles.
    # kraken: play-test 14 wave M3's builder (mb_pt14_m3) models its turrets' per-barrel muzzles itself.
    'sea_cruiser': ['Muzzle_gun', 'Muzzle_gun__001'],
    'heavy_turret': ['Muzzle_main'],
    'headquarters': ['Muzzle_main'],
    'titan_tank': ['Muzzle_main'],
}

MIN_LENGTH = 1.0      # m: shorter pieces are not barrels
THIN = 5.0            # a barrel is at least this many times longer than it is wide
LEVEL = 0.6           # m: a barrel's front end lies within this of the muzzle's depth (or 8 % of its length)
ACROSS = 3.0          # m: a barrel lies within this of the muzzle, across
SAME_AXIS = 0.2       # m: pieces closer than this across are one barrel


def _pieces(bm):
    """The bmesh's connected pieces, as lists of vertex coordinates."""
    seen = set()
    out = []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack, piece = [v], []
        seen.add(v.index)
        while stack:
            u = stack.pop()
            piece.append(u.co.copy())
            for e in u.link_edges:
                w = e.other_vert(u)
                if w.index not in seen:
                    seen.add(w.index)
                    stack.append(w)
        out.append(piece)
    return out


def _resolve(a, name):
    """The pivot's name as the builder registered it (with or without the "__" suffix)."""
    if name in a.pivots:
        return name
    alt = name.replace('__', '.')
    return alt if alt in a.pivots else None


def barrels_of(a, muzzle):
    """[(x, z)] of each barrel beside `muzzle`, in its parent's frame, left to right."""
    m = a.pivots[muzzle]
    parent = m.parent.name if m.parent is not None else None
    parent_key = next((k for k, o in a.pivots.items() if o is m.parent), parent)
    mx, my, mz = m.location
    tips = []
    for (name, mat, par), shape in a.shapes.items():
        if par != parent_key or not shape.bm.verts:
            continue
        shape.bm.verts.index_update()
        for piece in _pieces(shape.bm):
            xs = [p.x for p in piece]
            ys = [p.y for p in piece]
            zs = [p.z for p in piece]
            ly, lx, lz = max(ys) - min(ys), max(xs) - min(xs), max(zs) - min(zs)
            if ly < MIN_LENGTH or ly < THIN * max(lx, lz, 1e-3):
                continue
            front = min(ys)
            if abs(front - my) > max(LEVEL, 0.08 * ly):
                continue
            near = [p for p in piece if p.y <= front + 0.12 * ly]
            cx = sum(p.x for p in near) / len(near)
            cz = sum(p.z for p in near) / len(near)
            if (Vector((cx, cz)) - Vector((mx, mz))).length > ACROSS:
                continue
            tips.append((cx, cz))
    merged = []
    for cx, cz in sorted(tips):
        for i, (x, z, n) in enumerate(merged):
            if abs(x - cx) < SAME_AXIS and abs(z - cz) < SAME_AXIS:
                merged[i] = ((x * n + cx) / (n + 1), (z * n + cz) / (n + 1), n + 1)
                break
        else:
            merged.append((cx, cz, 1))
    return sorted(((x, z) for x, z, _ in merged), key=lambda t: (round(t[0], 2), t[1]))


def add_barrels(a, muzzles):
    for wanted in muzzles:
        muzzle = _resolve(a, wanted)
        if muzzle is None:
            print(f'P34_BARRELS {a.name}: no pivot {wanted}')
            continue
        found = barrels_of(a, muzzle)
        if len(found) < 2:
            print(f'P34_BARRELS {a.name}: {wanted}: {len(found)} barrel(s), no per-barrel muzzles')
            continue
        m = a.pivots[muzzle]
        tag = wanted.replace('Muzzle_', '').replace('__', '_').replace('.', '_')
        for k, (x, z) in enumerate(found, start=1):
            a.pivot(f'Muzzle_b{k}_{tag}', (x - m.location.x, 0.0, z - m.location.z), parent=muzzle)
        print(f'P34_BARRELS {a.name}: {wanted}: {len(found)} barrels at x ' + ', '.join(f'{x:.2f}' for x, _ in found))


def wrap(builders):
    """The builders with the per-barrel muzzles added after each target's own build (and its high-detail twin's)."""
    out = dict(builders)
    for name, muzzles in TARGETS.items():
        for key in (name, f'{name}_hd'):
            if key not in out:
                continue
            build, options = out[key]

            def run(a, build=build, muzzles=muzzles, **kw):
                build(a, **kw)
                add_barrels(a, muzzles)
            run.__name__ = getattr(build, '__name__', key)
            run.__doc__ = (build.__doc__ or '') + '\n\nPrompt 34 L4: a muzzle for every barrel.'
            out[key] = (run, options)
    return out
