"""The size of a model in Assets/MachineBrigade/Resources/Models, read from its .glb (no Unity, no Blender).

    python Tools/balance/glb_bounds.py main_battle_tank aim9     # length x width x height, metres

A glTF binary holds each mesh's POSITION accessor with its min and max; the model's box is those corners through
every node's transform, from the scene's roots. glTF is +Y up with the front along Z, as Unity imports it, so the
box reads (x, y, z) = (width, height, length), the order ExportGameDoc.ModelSizes and the design document use.
"""
from __future__ import annotations

import json
import os
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODELS = os.path.join(ROOT, "Assets", "MachineBrigade", "Resources", "Models")


def _gltf(path):
    with open(path, "rb") as f:
        data = f.read()
    magic, _version, _length = struct.unpack_from("<III", data, 0)
    if magic != 0x46546C67:
        raise ValueError(f"{path}: not a glTF binary")
    length, kind = struct.unpack_from("<II", data, 12)
    if kind != 0x4E4F534A:
        raise ValueError(f"{path}: the first chunk is not JSON")
    return json.loads(data[20:20 + length].decode("utf-8"))


def _mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def _local(node):
    if "matrix" in node:
        m = node["matrix"]  # column-major
        return [[m[c * 4 + r] for c in range(4)] for r in range(4)]
    tx, ty, tz = node.get("translation", [0, 0, 0])
    qx, qy, qz, qw = node.get("rotation", [0, 0, 0, 1])
    sx, sy, sz = node.get("scale", [1, 1, 1])
    r = [[1 - 2 * (qy * qy + qz * qz), 2 * (qx * qy - qz * qw), 2 * (qx * qz + qy * qw)],
         [2 * (qx * qy + qz * qw), 1 - 2 * (qx * qx + qz * qz), 2 * (qy * qz - qx * qw)],
         [2 * (qx * qz - qy * qw), 2 * (qy * qz + qx * qw), 1 - 2 * (qx * qx + qy * qy)]]
    return [[r[0][0] * sx, r[0][1] * sy, r[0][2] * sz, tx],
            [r[1][0] * sx, r[1][1] * sy, r[1][2] * sz, ty],
            [r[2][0] * sx, r[2][1] * sy, r[2][2] * sz, tz],
            [0, 0, 0, 1]]


def bounds(model_id, models=MODELS):
    """(width, height, length) of the model's box in metres, or None when there is no such model."""
    path = os.path.join(models, model_id + ".glb")
    if not os.path.exists(path):
        return None
    g = _gltf(path)
    nodes, meshes, accessors = g.get("nodes", []), g.get("meshes", []), g.get("accessors", [])
    lo, hi = [float("inf")] * 3, [float("-inf")] * 3

    def walk(index, parent):
        node = nodes[index]
        m = _mul(parent, _local(node))
        if "mesh" in node:
            for prim in meshes[node["mesh"]].get("primitives", []):
                acc = accessors[prim["attributes"]["POSITION"]]
                a, b = acc["min"], acc["max"]
                for cx in (a[0], b[0]):
                    for cy in (a[1], b[1]):
                        for cz in (a[2], b[2]):
                            p = [m[r][0] * cx + m[r][1] * cy + m[r][2] * cz + m[r][3] for r in range(3)]
                            for k in range(3):
                                lo[k] = min(lo[k], p[k])
                                hi[k] = max(hi[k], p[k])
        for child in node.get("children", []):
            walk(child, m)

    identity = [[1 if i == j else 0 for j in range(4)] for i in range(4)]
    scene = g.get("scenes", [{}])[g.get("scene", 0)]
    for root in scene.get("nodes", range(len(nodes))):
        walk(root, identity)
    if lo[0] == float("inf"):
        return None
    return tuple(hi[k] - lo[k] for k in range(3))


def length_width_height(model_id, models=MODELS):
    b = bounds(model_id, models)
    return None if b is None else (b[2], b[0], b[1])


if __name__ == "__main__":
    for name in sys.argv[1:]:
        s = length_width_height(name)
        print(name, "missing" if s is None else " x ".join(f"{v:.2f}" for v in s))
