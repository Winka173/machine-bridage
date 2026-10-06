"""MVA W2-B (spec parts Z3, AB, CG): merge a model's static same-material detail meshes into one mesh node, in the GLB.

    python Tools/assets/glb_merge_static.py                 # the models listed in static_merge.json
    python Tools/assets/glb_merge_static.py a b ...         # these models (still only the listed ones are merged on export)
    python Tools/assets/glb_merge_static.py --check         # report what would merge, write nothing

Why it is identical on screen: at load ModelLibrary.MergeRigidParts already combines every mesh under one moving anchor
(the root, a Turret, a Mount_, a Part_ ...) into one renderer, one sub-mesh per material. This tool does a strict subset of
that merge in the file: only sibling mesh nodes (same parent) with no children, no transform (identity: every exported
mesh node is), one primitive each, the same material and the same attribute layout, and a mesh no other node uses. Their
vertex rows are concatenated byte for byte (positions, the quantised normals and colours, UVs) and the indices offset, so
the merged triangles are the very same numbers in the very same space; the runtime's merged mesh is the same set of
triangles per material as before. Names the runtime or the data read are never merged (RUNTIME below, every string of
Resources/Data/*.json, the C# string literals that look like node names): a mesh the game finds by name keeps its node.

The merged node keeps the first member's name (canonical file order, so the result is deterministic); the merge is
idempotent (a second run finds nothing). Run by frontier_kit.export_collection after quantisation, for the listed models,
so a rebuild keeps the lower renderer count. Pure Python + numpy (runs inside Blender too).
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import glb_quantize as gq  # noqa: E402

LIST = HERE / 'static_merge.json'
MODELS = ROOT / 'Assets/MachineBrigade/Resources/Models'
DATA = ROOT / 'Assets/MachineBrigade/Resources/Data'
SCRIPTS = ROOT / 'Assets/MachineBrigade/Scripts'
UINT16, UINT32 = 5123, 5125
SIZE = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
LEGACY = re.compile(r'\.\d+$')

# The node names the runtime looks up (ModelLibrary patterns, VehicleView, EngineFlames, FxPoints, TowerArt, Loaded rounds).
RUNTIME = re.compile(
    r'^(turret|mount_|muzzle_|part_|deploy_|elevation|bombs|pump_beam|erector|searchlight|lift|blade|rotor|tail_rotor|radar|'
    r'propeller|main_cannon|muzzle_brake|mortar_tube|rocket_tubes|tubes|tube_bores|pod|atgm_pod|launcher|coax|flares|'
    r'aps_cluster|engine_flame|parachute|outline|lod1|emitter|drone_|rack|ram_rods|rams|missile_|round_?\d|rocket_?\d|'
    r'missile_?\d|cruise_missile|merged)|_(barrels|muzzles)(_\d+)?$', re.IGNORECASE)


def _protected_names():
    """Every string the data holds (a part's node, a prefix pattern) and every node-like C# string literal."""
    exact, prefixes = set(), set()

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, str) and 0 < len(o) < 80 and ' ' not in o:
            for piece in o.split('|'):
                if piece.endswith('*'):
                    if len(piece) > 1:
                        prefixes.add(piece[:-1].lower())
                elif piece:
                    exact.add(piece.lower())
    import glb_check
    for path in sorted(DATA.glob('*.json')):
        try:
            walk(glb_check.load_jsonc(path.read_text(encoding='utf-8')))
        except Exception:  # noqa: BLE001 - a file that is not JSON(C) names no node
            continue
    literal = re.compile(r'"([A-Z][A-Za-z0-9_]{2,})"')
    starts = re.compile(r'StartsWith\(\s*"([A-Za-z][A-Za-z0-9_]+)"')
    for path in sorted(SCRIPTS.rglob('*.cs')):
        text = path.read_text(encoding='utf-8', errors='ignore')
        exact.update(name.lower() for name in literal.findall(text))      # a name read by ==
        prefixes.update(name.lower() for name in starts.findall(text))    # a name read by StartsWith
    return exact, prefixes


def protected(name: str, exact, prefixes) -> bool:
    base = LEGACY.sub('', name)
    low = base.lower()
    if RUNTIME.search(base) or low in exact or name.lower() in exact:
        return True
    return any(low.startswith(p) for p in prefixes)


def _rows(doc, binary, index):
    """An accessor's elements as an (count, element bytes) uint8 array (strided views read row by row)."""
    acc = doc['accessors'][index]
    view = doc['bufferViews'][acc['bufferView']]
    width = gq.WIDTH[acc['type']] * SIZE[acc['componentType']]
    stride = view.get('byteStride', 0) or width
    start = view.get('byteOffset', 0) + acc.get('byteOffset', 0)
    count = acc['count']
    rows = np.zeros((count, stride), np.uint8)
    if count:
        # The last element may end at its own width (the view need not hold the final row's padding).
        raw = np.frombuffer(binary, np.uint8, count=stride * (count - 1) + width, offset=start)
        flat = rows.reshape(-1)
        flat[:len(raw)] = raw
    return rows, stride


def _indices(doc, binary, index):
    acc = doc['accessors'][index]
    view = doc['bufferViews'][acc['bufferView']]
    start = view.get('byteOffset', 0) + acc.get('byteOffset', 0)
    dtype = {5121: '<u1', 5123: '<u2', 5125: '<u4'}[acc['componentType']]
    return np.frombuffer(binary, dtype, count=acc['count'], offset=start).astype(np.uint32)


def _layout(doc, prim):
    return tuple(sorted((k, doc['accessors'][v]['componentType'], doc['accessors'][v]['type'],
                         bool(doc['accessors'][v].get('normalized', False))) for k, v in prim['attributes'].items()))


def plan(doc, exact, prefixes):
    """[(parent or None, [node indices])] groups to merge, in file order."""
    nodes = doc.get('nodes', [])
    parent = {}
    for i, n in enumerate(nodes):
        for c in n.get('children', []):
            parent[c] = i
    users = {}
    for i, n in enumerate(nodes):
        if 'mesh' in n:
            users[n['mesh']] = users.get(n['mesh'], 0) + 1
    groups = {}
    for i, n in enumerate(nodes):
        if 'mesh' not in n or n.get('children') or any(k in n for k in ('translation', 'rotation', 'scale', 'matrix')):
            continue
        if users[n['mesh']] != 1 or 'skin' in n or 'weights' in n or protected(n.get('name', ''), exact, prefixes):
            continue
        mesh = doc['meshes'][n['mesh']]
        prims = mesh.get('primitives', [])
        if len(prims) != 1 or prims[0].get('mode', 4) != 4 or 'targets' in prims[0] or 'indices' not in prims[0] \
                or 'extensions' in prims[0] or 'material' not in prims[0]:
            continue
        key = (parent.get(i), prims[0]['material'], _layout(doc, prims[0]))
        groups.setdefault(key, []).append(i)
    return [(k[0], members) for k, members in groups.items() if len(members) > 1]


def merge_bytes(data: bytes, exact=None, prefixes=None):
    """(new bytes, merged groups as [[names]]); the input bytes when nothing merges."""
    if exact is None:
        exact, prefixes = _protected_names()
    doc, binary = gq._read(data)
    groups = plan(doc, exact, prefixes)
    if not groups:
        return data, []
    nodes = doc['nodes']
    new_views = []   # (bytes, stride or None, target)
    report = []
    dropped = set()
    for _, members in groups:
        first = nodes[members[0]]
        prim0 = doc['meshes'][first['mesh']]['primitives'][0]
        attr_rows = {}
        index_parts, base, tri, members_out = [], 0, 0, []
        for i in members:
            prim = doc['meshes'][nodes[i]['mesh']]['primitives'][0]
            count = doc['accessors'][prim['attributes']['POSITION']]['count']
            n_tris = doc['accessors'][prim['indices']]['count'] // 3
            members_out.append([nodes[i].get('name', ''), tri, n_tris])
            tri += n_tris
            for key, acc in prim['attributes'].items():
                rows, stride = _rows(doc, binary, acc)
                attr_rows.setdefault(key, []).append((rows, stride))
            index_parts.append(_indices(doc, binary, prim['indices']) + base)
            base += count
        new_prim = {k: v for k, v in prim0.items() if k not in ('attributes', 'indices')}
        new_prim['attributes'] = {}
        for key, parts in attr_rows.items():
            stride = parts[0][1]
            if any(s != stride for _, s in parts):
                raise ValueError(f'{first.get("name")}: {key} strides differ')
            rows = np.concatenate([r for r, _ in parts])
            src = doc['accessors'][prim0['attributes'][key]]
            acc = {k: v for k, v in src.items() if k not in ('bufferView', 'byteOffset', 'count', 'min', 'max')}
            acc['count'] = int(len(rows))
            if key == 'POSITION':
                pos = np.ascontiguousarray(rows[:, :12]).view('<f4').reshape(-1, 3)
                acc['min'] = [float(x) for x in pos.min(axis=0)]
                acc['max'] = [float(x) for x in pos.max(axis=0)]
            src_view = doc['bufferViews'][src['bufferView']]
            new_views.append((rows.tobytes(), src_view.get('byteStride'), src_view.get('target')))
            acc['bufferView'] = ('new', len(new_views) - 1)
            doc['accessors'].append(acc)
            new_prim['attributes'][key] = len(doc['accessors']) - 1
        indices = np.concatenate(index_parts)
        ctype = UINT16 if base <= 65535 else UINT32
        blob = indices.astype('<u2' if ctype == UINT16 else '<u4').tobytes()
        new_views.append((blob, None, 34963))
        doc['accessors'].append({'bufferView': ('new', len(new_views) - 1), 'componentType': ctype, 'count': int(len(indices)),
                                 'type': 'SCALAR'})
        new_prim['indices'] = len(doc['accessors']) - 1
        mesh = {'name': doc['meshes'][first['mesh']].get('name', first.get('name', 'merged')), 'primitives': [new_prim]}
        doc['meshes'].append(mesh)
        first['mesh'] = len(doc['meshes']) - 1
        # The members' names and triangle ranges, for the static tools (glb_mesh, glb_analyze: the quality gate's parts
        # and body pieces read node names); glTFast ignores extras.
        first.setdefault('extras', {})['mergedFrom'] = members_out
        report.append([nodes[i].get('name', '') for i in members])
        dropped.update(members[1:])
    _compact(doc, binary, new_views, dropped)
    return gq._write(doc, doc.pop('_binary')), report


def _compact(doc, binary, new_views, dropped):
    """Drops the merged-away nodes and every mesh / accessor / bufferView nothing uses any more; rebuilds the buffer."""
    nodes = doc['nodes']
    keep = [i for i in range(len(nodes)) if i not in dropped]
    remap = {old: new for new, old in enumerate(keep)}
    for n in nodes:
        if 'children' in n:
            n['children'] = [remap[c] for c in n['children'] if c in remap]
            if not n['children']:
                del n['children']
    for scene in doc.get('scenes', []):
        scene['nodes'] = [remap[c] for c in scene.get('nodes', []) if c in remap]
    doc['nodes'] = [nodes[i] for i in keep]
    # Meshes in use.
    used_mesh = sorted({n['mesh'] for n in doc['nodes'] if 'mesh' in n})
    mesh_map = {old: new for new, old in enumerate(used_mesh)}
    for n in doc['nodes']:
        if 'mesh' in n:
            n['mesh'] = mesh_map[n['mesh']]
    doc['meshes'] = [doc['meshes'][i] for i in used_mesh]
    # Accessors in use (meshes, skins, animations: these models have no skins or animations).
    used_acc = set()
    for mesh in doc['meshes']:
        for prim in mesh['primitives']:
            used_acc.update(prim['attributes'].values())
            if 'indices' in prim:
                used_acc.add(prim['indices'])
    for skin in doc.get('skins', []):
        if 'inverseBindMatrices' in skin:
            used_acc.add(skin['inverseBindMatrices'])
    for anim in doc.get('animations', []):
        for s in anim.get('samplers', []):
            used_acc.update((s['input'], s['output']))
    acc_order = sorted(used_acc)
    acc_map = {old: new for new, old in enumerate(acc_order)}
    for mesh in doc['meshes']:
        for prim in mesh['primitives']:
            prim['attributes'] = {k: acc_map[v] for k, v in prim['attributes'].items()}
            if 'indices' in prim:
                prim['indices'] = acc_map[prim['indices']]
    for skin in doc.get('skins', []):
        if 'inverseBindMatrices' in skin:
            skin['inverseBindMatrices'] = acc_map[skin['inverseBindMatrices']]
    for anim in doc.get('animations', []):
        for s in anim.get('samplers', []):
            s['input'], s['output'] = acc_map[s['input']], acc_map[s['output']]
    accessors = [doc['accessors'][i] for i in acc_order]
    # Buffer views in use, old ones first in file order, then the new ones; images keep theirs.
    blobs, views = [], []
    view_map = {}
    old_used = sorted({a['bufferView'] for a in accessors if isinstance(a.get('bufferView'), int)} |
                      {img['bufferView'] for img in doc.get('images', []) if 'bufferView' in img})
    for old in old_used:
        v = doc['bufferViews'][old]
        start = v.get('byteOffset', 0)
        view_map[old] = len(views)
        views.append({k: val for k, val in v.items() if k not in ('byteOffset', 'byteLength')})
        blobs.append(binary[start:start + v['byteLength']])
    new_map = {}
    for k, (blob, stride, target) in enumerate(new_views):
        if not any(a.get('bufferView') == ('new', k) for a in accessors):
            continue
        new_map[k] = len(views)
        view = {'buffer': 0}
        if stride:
            view['byteStride'] = stride
        if target:
            view['target'] = target
        views.append(view)
        blobs.append(blob)
    for a in accessors:
        bv = a.get('bufferView')
        a['bufferView'] = new_map[bv[1]] if isinstance(bv, tuple) else view_map[bv]
    for img in doc.get('images', []):
        if 'bufferView' in img:
            img['bufferView'] = view_map[img['bufferView']]
    parts, cursor = [], 0
    for view, blob in zip(views, blobs):
        pad = -cursor % 4
        parts.append(b'\0' * pad)
        cursor += pad
        view['byteOffset'] = cursor
        view['byteLength'] = len(blob)
        parts.append(blob)
        cursor += len(blob)
    doc['bufferViews'] = views
    doc['accessors'] = accessors
    new_binary = b''.join(parts)
    doc['buffers'][0]['byteLength'] = len(new_binary)
    doc['_binary'] = new_binary


def listed() -> list[str]:
    return json.loads(LIST.read_text(encoding='utf-8')).get('models', []) if LIST.exists() else []


def merge_file(path, check=False, names=None):
    """Merges one GLB in place when its model is listed in static_merge.json. Returns the merged groups."""
    path = Path(path)
    if path.stem not in listed():
        return []
    exact, prefixes = names or _protected_names()
    data = path.read_bytes()
    out, report = merge_bytes(data, exact, prefixes)
    if out != data and not check:
        tmp = path.with_name(path.name + '.tmp')
        tmp.write_bytes(out)
        os.replace(tmp, path)
    return report


def main(argv):
    check = '--check' in argv
    wanted = [a for a in argv if not a.startswith('--')] or listed()
    names = _protected_names()
    total = 0
    for model in wanted:
        report = merge_file(MODELS / f'{model}.glb', check, names)
        saved = sum(len(g) - 1 for g in report)
        total += saved
        print(f'{model}: {saved} mesh nodes merged into {len(report)}' + (' (check)' if check else ''))
    print(f'STATIC MERGE: {total} renderers fewer')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
