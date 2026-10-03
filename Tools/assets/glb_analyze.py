"""Static analysis of one exported model (.glb): counts, bounds, vertex colour, topology, gameplay node names.

No Unity, no Blender: the glTF binary is read directly (numpy for the arrays). Used by glb_check.py, which runs it
over every file in Assets/MachineBrigade/Resources/Models and applies the validation rules.

Axes: glTF is +Y up with the front along Z, as Unity imports it, so a size reads (x, y, z) = (width, height, length)
(the order Tools/balance/glb_bounds.py and balance.json's modelSize use: length, width, height).
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
from pathlib import Path

import numpy as np

# The node names the runtime looks up (ModelLibrary.cs patterns, VehicleView, MuzzleFx, BossParts).
RUNTIME_PATTERNS = {
    'turret': re.compile(r'^Turret(\.\d+)?$'),
    'main_cannon': re.compile(r'^Main_cannon', re.I),
    'muzzle_brake': re.compile(r'^Muzzle_brake', re.I),
    'muzzle': re.compile(r'^Muzzle_(main|coax|mg|missile|rocket|gun|aam|door_l|door_r|ramp|agl_l|agl_r|mortar)(\.\d+)?$', re.I),
    'mount': re.compile(r'^Mount_([a-z]+)(\.\d+)?$', re.I),
    'rotor': re.compile(r'^Rotor(_rear|_front|_\d+)?(\.\d+)?$'),
    'tail_rotor': re.compile(r'^Tail_rotor(\.\d+)?$'),
    'radar': re.compile(r'^Radar(_search|_\d+)?(\.\d+)?$'),
    'propeller': re.compile(r'^Propeller(_\d+)?(\.\d+)?$'),
    'loose': re.compile(r'^(Bombs|Pump_beam|Erector|Searchlight|Lift|Blade)(\.\d+)?$'),
    'part': re.compile(r'^Part_[a-z]+(\.\d+)?$', re.I),
    'deploy': re.compile(r'^Deploy_[a-z]+(_[lr])?(\.\d+)?$', re.I),
    'point': re.compile(r'^Point_', re.I),
    'launch': re.compile(r'^Launch_', re.I),
}
# Names Blender suffixed (".001") that the runtime would look up: the build refuses these (frontier_kit.finish).
RUNTIME_PREFIX = re.compile(r'^(turret|main_cannon|muzzle|bombs|parachute|rotor|tail_rotor|propeller|radar|mount_|erector|'
                            r'icbm_payload|deploy_)', re.I)

COMPONENTS = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
WIDTH = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}
NORMALIZED_MAX = {5121: 255.0, 5123: 65535.0}
# Signed normalized (KHR_mesh_quantization normals, glb_quantize.py): decoded max(c / max, -1) as the glTF spec says.
SIGNED_NORMALIZED_MAX = {5120: 127.0, 5122: 32767.0}
DEGENERATE_AREA = 1e-8  # m^2 in the mesh's own space: 0.1 mm x 0.1 mm


class GlbError(Exception):
    pass


def read_glb(path: Path):
    data = path.read_bytes()
    if len(data) < 20:
        raise GlbError('file too short')
    magic, version, length = struct.unpack_from('<III', data, 0)
    if magic != 0x46546C67:
        raise GlbError('not a glTF binary (bad magic)')
    if version != 2:
        raise GlbError(f'glTF version {version}, expected 2')
    if length != len(data):
        raise GlbError(f'header length {length} != file size {len(data)}')
    offset, doc, binary = 12, None, b''
    while offset < len(data):
        chunk_len, kind = struct.unpack_from('<II', data, offset)
        body = data[offset + 8:offset + 8 + chunk_len]
        if kind == 0x4E4F534A:
            doc = json.loads(body.decode('utf-8'))
        elif kind == 0x004E4942:
            binary = body
        offset += 8 + chunk_len
    if doc is None:
        raise GlbError('no JSON chunk')
    return doc, binary


def accessor(doc, binary, index):
    acc = doc['accessors'][index]
    if 'bufferView' not in acc:
        raise GlbError(f'accessor {index} has no bufferView (sparse/empty not supported)')
    view = doc['bufferViews'][acc['bufferView']]
    if view.get('buffer', 0) != 0:
        raise GlbError('external buffers are not supported')
    dtype = np.dtype(COMPONENTS[acc['componentType']])
    width = WIDTH[acc['type']]
    count = acc['count']
    start = view.get('byteOffset', 0) + acc.get('byteOffset', 0)
    stride = view.get('byteStride', 0) or dtype.itemsize * width
    end = start + stride * (count - 1) + dtype.itemsize * width if count else start
    if end > len(binary) or end > view.get('byteOffset', 0) + view['byteLength']:
        raise GlbError(f'accessor {index} reads past its buffer view')
    if stride == dtype.itemsize * width:
        arr = np.frombuffer(binary, dtype=dtype, count=count * width, offset=start).reshape(count, width)
    else:
        rows = np.frombuffer(binary, dtype=np.uint8, count=stride * count, offset=start)
        rows = np.lib.stride_tricks.as_strided(rows, shape=(count, dtype.itemsize * width), strides=(stride, 1))
        arr = np.ascontiguousarray(rows).view(dtype).reshape(count, width)
    if acc.get('normalized') and acc['componentType'] in NORMALIZED_MAX:
        arr = arr.astype(np.float32) / NORMALIZED_MAX[acc['componentType']]
    elif acc.get('normalized') and acc['componentType'] in SIGNED_NORMALIZED_MAX:
        arr = np.maximum(arr.astype(np.float32) / SIGNED_NORMALIZED_MAX[acc['componentType']], -1.0)
    return arr


def local_matrix(node):
    if 'matrix' in node:
        return np.array(node['matrix'], dtype=np.float64).reshape(4, 4).T  # column-major
    tx, ty, tz = node.get('translation', [0, 0, 0])
    qx, qy, qz, qw = node.get('rotation', [0, 0, 0, 1])
    sx, sy, sz = node.get('scale', [1, 1, 1])
    r = np.array([
        [1 - 2 * (qy * qy + qz * qz), 2 * (qx * qy - qz * qw), 2 * (qx * qz + qy * qw)],
        [2 * (qx * qy + qz * qw), 1 - 2 * (qx * qx + qz * qz), 2 * (qy * qz - qx * qw)],
        [2 * (qx * qz - qy * qw), 2 * (qy * qz + qx * qw), 1 - 2 * (qx * qx + qy * qy)]])
    m = np.eye(4)
    m[:3, :3] = r * np.array([sx, sy, sz])
    m[:3, 3] = (tx, ty, tz)
    return m


def walk(doc):
    """(node index, world matrix, parent index) for every node reachable from the scene's roots."""
    scene = doc['scenes'][doc.get('scene', 0)]
    out, stack = [], [(i, np.eye(4), None) for i in scene.get('nodes', [])]
    seen = set()
    while stack:
        i, parent_m, parent = stack.pop()
        if i in seen:
            raise GlbError(f'node {i} reached twice (cycle or shared child)')
        seen.add(i)
        node = doc['nodes'][i]
        m = parent_m @ local_matrix(node)
        out.append((i, m, parent))
        stack.extend((c, m, i) for c in node.get('children', []))
    return out


def _components(tris, n):
    """Connected pieces of a welded triangle list (union-find over its edges)."""
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b, c in tris.tolist():
        ra = find(a)
        for v in (b, c):
            rv = find(v)
            if rv != ra:
                parent[rv] = ra
    used = np.unique(tris)
    return len({find(int(v)) for v in used})


def _topology(pos, tris):
    """Weld by position (1e-5 m), then count loose pieces, open edges and edges shared by 3+ triangles."""
    if len(tris) == 0:
        return 0, 0, 0
    q = np.round(pos / 1e-5).astype(np.int64)
    _, weld = np.unique(q, axis=0, return_inverse=True)
    weld = weld.reshape(-1)
    t = weld[tris]
    t = t[(t[:, 0] != t[:, 1]) & (t[:, 1] != t[:, 2]) & (t[:, 0] != t[:, 2])]
    if len(t) == 0:
        return 0, 0, 0
    edges = np.sort(np.concatenate([t[:, [0, 1]], t[:, [1, 2]], t[:, [2, 0]]]), axis=1)
    _, counts = np.unique(edges, axis=0, return_counts=True)
    return _components(t, int(weld.max()) + 1), int((counts == 1).sum()), int((counts > 2).sum())


def analyze(path: Path) -> dict:
    """Every number the baseline records for one file. Raises GlbError when the file cannot be read."""
    doc, binary = read_glb(path)
    rec = {
        'file': path.name,
        'fileBytes': path.stat().st_size,
        'sha1': hashlib.sha1(path.read_bytes()).hexdigest()[:16],
        'generator': doc.get('asset', {}).get('generator', ''),
        'extensions': sorted(doc.get('extensionsUsed', [])),
        'nodes': len(doc.get('nodes', [])),
        'meshes': len(doc.get('meshes', [])),
        'materials': len(doc.get('materials', [])),
        'animations': len(doc.get('animations', [])),
        'skins': len(doc.get('skins', [])),
        'textures': len(doc.get('textures', [])),
    }
    problems = []  # hard read problems found while analysing (NaN, bad indices, ...)
    renderers = submeshes = triangles = vertices = degenerate = 0
    loose = open_edges = nonmanifold = 0
    missing = {'COLOR_0': 0, 'NORMAL': 0, 'TEXCOORD_0': 0}
    used_materials = set()
    lo = np.full(3, np.inf)
    hi = np.full(3, -np.inf)
    colours = []
    colour_weights = []
    colour_out_of_range = 0
    nonfinite = 0
    names, structure = [], []
    for i, world, parent in walk(doc):
        node = doc['nodes'][i]
        name = node.get('name', f'node{i}')
        names.append(name)
        mesh_index = node.get('mesh')
        tri_count = 0
        if mesh_index is not None:
            renderers += 1
            mesh = doc['meshes'][mesh_index]
            for prim in mesh.get('primitives', []):
                submeshes += 1
                attrs = prim.get('attributes', {})
                if 'material' in prim:
                    used_materials.add(prim['material'])
                for key in missing:
                    if key not in attrs:
                        missing[key] += 1
                if 'POSITION' not in attrs:
                    problems.append(f'{name}: primitive without POSITION')
                    continue
                mode = prim.get('mode', 4)
                if mode != 4:
                    problems.append(f'{name}: primitive mode {mode} (not triangles)')
                pos = accessor(doc, binary, attrs['POSITION']).astype(np.float64)
                vertices += len(pos)
                bad = ~np.isfinite(pos).all(axis=1)
                if bad.any():
                    nonfinite += int(bad.sum())
                    pos = np.where(np.isfinite(pos), pos, 0.0)
                for key in ('NORMAL', 'TEXCOORD_0'):
                    if key in attrs:
                        a = accessor(doc, binary, attrs[key])
                        nonfinite += int((~np.isfinite(a.astype(np.float64))).any(axis=1).sum())
                if 'COLOR_0' in attrs:
                    col = accessor(doc, binary, attrs['COLOR_0']).astype(np.float64)
                    nonfinite += int((~np.isfinite(col)).any(axis=1).sum())
                    col = np.nan_to_num(col)
                    colour_out_of_range += int(((col < -1e-4) | (col > 1 + 1e-4)).any(axis=1).sum())
                    rgb = col[:, :3]
                    lum = rgb @ np.array([0.2126, 0.7152, 0.0722])
                    colours.append(lum)
                if 'indices' in prim:
                    idx = accessor(doc, binary, prim['indices']).reshape(-1).astype(np.int64)
                else:
                    idx = np.arange(len(pos), dtype=np.int64)
                if len(idx) % 3 and mode == 4:
                    problems.append(f'{name}: index count {len(idx)} not a multiple of 3')
                    idx = idx[:len(idx) - len(idx) % 3]
                if len(idx) and (idx.min() < 0 or idx.max() >= len(pos)):
                    problems.append(f'{name}: index out of range (max {int(idx.max())}, {len(pos)} vertices)')
                    idx = np.clip(idx, 0, len(pos) - 1)
                tris = idx.reshape(-1, 3)
                tri_count += len(tris)
                if len(tris):
                    a, b, c = pos[tris[:, 0]], pos[tris[:, 1]], pos[tris[:, 2]]
                    area = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
                    degenerate += int((area < DEGENERATE_AREA).sum())
                    if 'COLOR_0' in attrs:
                        colour_weights.append(np.bincount(tris.reshape(-1), minlength=len(pos))[:len(pos)])
                    pc, oe, nm = _topology(pos, tris)
                    loose += pc
                    open_edges += oe
                    nonmanifold += nm
                if len(pos):
                    w = (np.c_[pos, np.ones(len(pos))] @ world.T)[:, :3]
                    lo = np.minimum(lo, w.min(axis=0))
                    hi = np.maximum(hi, w.max(axis=0))
            triangles += tri_count
        parent_name = doc['nodes'][parent].get('name', f'node{parent}') if parent is not None else ''
        structure.append(f'{name}<{parent_name}#{tri_count}')
    if not np.isfinite(lo).all():
        lo = hi = np.zeros(3)
    size = hi - lo
    rec.update({
        'renderers': renderers,
        'submeshes': submeshes,
        'materialSlots': submeshes,
        'materialsUsed': len(used_materials),
        'triangles': triangles,
        'vertices': vertices,
        'degenerateTriangles': degenerate,
        'nonFiniteValues': nonfinite,
        'primitivesMissing': missing,
        'loosePieces': loose,
        'openEdges': open_edges,
        'nonManifoldEdges': nonmanifold,
        'boundsMin': [round(float(v), 4) for v in lo],
        'boundsMax': [round(float(v), 4) for v in hi],
        # length, width, height (balance.json modelSize order)
        'size': [round(float(size[2]), 3), round(float(size[0]), 3), round(float(size[1]), 3)],
        'center': [round(float(v), 3) for v in (lo + hi) / 2],
        'structureHash': hashlib.sha1('|'.join(sorted(structure)).encode('utf-8')).hexdigest()[:16],
    })
    if colours:
        lum = np.concatenate(colours)
        weights = np.concatenate(colour_weights) if len(colour_weights) == len(colours) else None
        rec['color0'] = {
            'mean': round(float(np.average(lum, weights=weights) if weights is not None and weights.sum() else lum.mean()), 4),
            'min': round(float(lum.min()), 4),
            'max': round(float(lum.max()), 4),
            'p05': round(float(np.percentile(lum, 5)), 4),
            'p95': round(float(np.percentile(lum, 95)), 4),
            'outOfRange': colour_out_of_range,
        }
    else:
        rec['color0'] = None
    runtime = {}
    for key, pattern in RUNTIME_PATTERNS.items():
        hits = sorted(n for n in names if pattern.match(n))
        if hits:
            runtime[key] = hits
    rec['runtimeNodes'] = runtime
    rec['runtimeSuffixed'] = sorted(n for n in names if re.search(r'\.\d+$', n) and RUNTIME_PREFIX.match(n))
    rec['nodeNames'] = sorted(set(names))
    rec['problems'] = problems
    return rec
