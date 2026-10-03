"""Prompt 35 section 9 (GLB size, lane A): rewrite a GLB's vertex attributes compactly with KHR_mesh_quantization.

    python Tools/assets/glb_quantize.py                     # every Assets/MachineBrigade/Resources/Models/*.glb
    python Tools/assets/glb_quantize.py path/a.glb ...      # some files
    python Tools/assets/glb_quantize.py --check             # report what would change, write nothing

The importer is glTFast 6.20 (Packages/manifest.json), which reads KHR_mesh_quantization out of the box (its
k_SupportedExtensions; Draco and meshopt need extra packages the project does not have). What is rewritten:
- NORMAL: float32 VEC3 -> normalized int8 VEC3 (byteStride 4), unit length first; glTFast renormalises on import.
- COLOR_0: float32 -> normalized uint16, same type (VEC3 stays VEC3, byteStride 8); error under 1e-5, so the baked
  AO reads the same everywhere (the gate's COLOR_0 numbers do not move; 8-bit would shift them by up to 0.002).
Kept as they are: POSITION (float32: an int16 position needs a node scale, which would change the hierarchy's
transforms), TEXCOORD_0 (float32: the box-projected UVs run past 0-1, and unnormalized int16 needs
KHR_texture_transform on a texture these flat materials do not have), indices, nodes, names, materials, extras.

Pure Python + numpy, so frontier_kit.export_collection runs it inside Blender right after the glTF export. Deterministic
(same input bytes -> same output bytes) and idempotent (an attribute already quantised is left alone).
"""
from __future__ import annotations

import json
import os
import struct
import sys
from pathlib import Path

import numpy as np

EXTENSION = 'KHR_mesh_quantization'
FLOAT, INT8, UINT16 = 5126, 5120, 5123
ARRAY_BUFFER = 34962
WIDTH = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}
MODELS = Path(__file__).resolve().parents[2] / 'Assets' / 'MachineBrigade' / 'Resources' / 'Models'


def _read(data: bytes):
    magic, version, length = struct.unpack_from('<III', data, 0)
    if magic != 0x46546C67 or version != 2 or length != len(data):
        raise ValueError('not a glTF 2.0 binary')
    offset, doc, binary = 12, None, b''
    while offset < len(data):
        chunk_len, kind = struct.unpack_from('<II', data, offset)
        body = data[offset + 8:offset + 8 + chunk_len]
        if kind == 0x4E4F534A:
            doc = json.loads(body.decode('utf-8'))
        elif kind == 0x004E4942:
            binary = bytes(body)
        offset += 8 + chunk_len
    if doc is None:
        raise ValueError('no JSON chunk')
    return doc, binary


def _write(doc, binary: bytes) -> bytes:
    text = json.dumps(doc, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    text += b' ' * (-len(text) % 4)
    binary += b'\0' * (-len(binary) % 4)
    out = [struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(text) + (8 + len(binary) if binary else 0)),
           struct.pack('<II', len(text), 0x4E4F534A), text]
    if binary:
        out += [struct.pack('<II', len(binary), 0x004E4942), binary]
    return b''.join(out)


def _float_rows(doc, binary, acc):
    view = doc['bufferViews'][acc['bufferView']]
    width = WIDTH[acc['type']]
    start = view.get('byteOffset', 0) + acc.get('byteOffset', 0)
    stride = view.get('byteStride', 0) or 4 * width
    rows = np.frombuffer(binary, dtype=np.uint8, count=stride * acc['count'], offset=start) if acc['count'] else \
        np.zeros(0, np.uint8)
    rows = rows.reshape(acc['count'], stride)[:, :4 * width]
    return np.ascontiguousarray(rows).view('<f4').reshape(acc['count'], width).astype(np.float64)


def quantize_normals(v: np.ndarray) -> bytes:
    """(n, 3) float -> n x 4 bytes: int8 x, y, z (decoded max(c / 127, -1)) and a zero pad byte."""
    length = np.linalg.norm(v, axis=1, keepdims=True)
    unit = np.divide(v, length, out=np.zeros_like(v), where=length > 1e-12)
    q = np.clip(np.rint(unit * 127.0), -127, 127).astype(np.int8)
    out = np.zeros((len(v), 4), np.int8)
    out[:, :3] = q
    return out.tobytes()


def quantize_colours(v: np.ndarray) -> bytes:
    """(n, w) float in 0-1 -> uint16 rows (decoded c / 65535), padded to a 4-byte multiple."""
    width = v.shape[1]
    padded = width + (width % 2)
    out = np.zeros((len(v), padded), '<u2')
    out[:, :width] = np.clip(np.rint(np.clip(v, 0.0, 1.0) * 65535.0), 0, 65535).astype('<u2')
    return out.tobytes(), padded * 2


def quantize_bytes(data: bytes) -> bytes:
    """The quantised GLB for one GLB's bytes (unchanged bytes when there is nothing left to quantise)."""
    doc, binary = _read(data)
    plan = {}   # accessor index -> (new bytes, componentType, byteStride)
    for mesh in doc.get('meshes', []):
        for prim in mesh.get('primitives', []):
            for key, index in prim.get('attributes', {}).items():
                acc = doc['accessors'][index]
                if index in plan or acc.get('componentType') != FLOAT or 'bufferView' not in acc or 'sparse' in acc:
                    continue
                if key == 'NORMAL' and acc['type'] == 'VEC3':
                    plan[index] = (quantize_normals(_float_rows(doc, binary, acc)), INT8, 4)
                elif key == 'COLOR_0' and acc['type'] in ('VEC3', 'VEC4'):
                    blob, stride = quantize_colours(_float_rows(doc, binary, acc))
                    plan[index] = (blob, UINT16, stride)
    if not plan:
        return data
    users = {}
    for i, acc in enumerate(doc['accessors']):
        users.setdefault(acc.get('bufferView'), []).append(i)
    replaced = {}   # bufferView index -> new bytes
    for index, (blob, ctype, stride) in plan.items():
        acc = doc['accessors'][index]
        view_index = acc['bufferView']
        if len(users[view_index]) != 1:   # a shared view (interleaved): give the accessor a view of its own
            doc['bufferViews'].append({'buffer': 0, 'byteLength': 0})
            view_index = len(doc['bufferViews']) - 1
            acc['bufferView'] = view_index
        view = doc['bufferViews'][view_index]
        view['byteStride'] = stride
        view['target'] = ARRAY_BUFFER
        replaced[view_index] = blob
        acc.pop('byteOffset', None)
        acc['componentType'] = ctype
        acc['normalized'] = True
        acc.pop('min', None)
        acc.pop('max', None)
    parts, cursor = [], 0
    for i, view in enumerate(doc['bufferViews']):
        if view.get('buffer', 0) != 0:
            raise ValueError('external buffers are not supported')
        if i in replaced:
            blob = replaced[i]
        else:
            start = view.get('byteOffset', 0)
            blob = binary[start:start + view['byteLength']]
        pad = -cursor % 4
        parts.append(b'\0' * pad)
        cursor += pad
        view['byteOffset'] = cursor
        view['byteLength'] = len(blob)
        parts.append(blob)
        cursor += len(blob)
    new_binary = b''.join(parts)
    doc['buffers'][0]['byteLength'] = len(new_binary)
    for key in ('extensionsUsed', 'extensionsRequired'):
        names = doc.setdefault(key, [])
        if EXTENSION not in names:
            names.append(EXTENSION)
    return _write(doc, new_binary)


def quantize_file(path, check=False):
    """Quantise one GLB in place (atomic replace). Returns (bytes before, bytes after)."""
    path = Path(path)
    data = path.read_bytes()
    out = quantize_bytes(data)
    if out != data and not check:
        tmp = path.with_name(path.name + '.tmp')
        tmp.write_bytes(out)
        os.replace(tmp, path)
    return len(data), len(out)


def main(argv):
    check = '--check' in argv
    paths = [Path(a) for a in argv if not a.startswith('--')] or sorted(MODELS.glob('*.glb'))
    before = after = changed = 0
    for p in paths:
        a, b = quantize_file(p, check)
        before += a
        after += b
        changed += a != b
    print(f'{len(paths)} files, {changed} {"would change" if check else "changed"}: '
          f'{before / 2**20:.1f} -> {after / 2**20:.1f} MiB')


if __name__ == '__main__':
    main(sys.argv[1:])
