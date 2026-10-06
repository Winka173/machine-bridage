"""World-space triangle soup of one GLB for the prompt 35 quality gate and the rebuild inventory (no Unity, no Blender).

`load(path)` returns a `Model`: every mesh node's triangles in model space (glTF axes: +Y up, +Z front, metres), its
material name and base colour, per-vertex COLOR_0 luminance and the node's name chain. `render(model, view)` draws a
cheap orthographic picture (PIL painter's algorithm, flat shaded, base colour x COLOR_0 x a fixed sun), enough to
measure silhouettes, edge density and brightness regions the same way for every model.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

import glb_analyze as ga

LUMA = np.array([0.2126, 0.7152, 0.0722])


@dataclass
class Piece:
    node: str            # the mesh node's name
    chain: tuple         # its ancestors' names, root first
    material: str
    base: float          # base colour luminance (linear)
    pos: np.ndarray      # (n, 3) world positions
    tris: np.ndarray     # (m, 3) indices
    lum: np.ndarray      # (n,) COLOR_0 luminance (1 when absent)
    has_color: bool


@dataclass
class Model:
    name: str
    pieces: list = field(default_factory=list)
    nodes: list = field(default_factory=list)       # every node name

    @property
    def triangles(self):
        return sum(len(p.tris) for p in self.pieces)

    def soup(self, keep=None):
        """(T, 3, 3) triangle corners, (T,) shade inputs: base x mean COLOR_0, and the piece index per triangle."""
        corners, shade, owner = [], [], []
        for i, p in enumerate(self.pieces):
            if keep is not None and not keep(p):
                continue
            if not len(p.tris):
                continue
            corners.append(p.pos[p.tris])
            shade.append(p.base * p.lum[p.tris].mean(axis=1))
            owner.append(np.full(len(p.tris), i))
        if not corners:
            return np.zeros((0, 3, 3)), np.zeros(0), np.zeros(0, dtype=int)
        return np.concatenate(corners), np.concatenate(shade), np.concatenate(owner)

    def bounds(self):
        allp = [p.pos for p in self.pieces if len(p.pos)]
        if not allp:
            return np.zeros(3), np.zeros(3)
        a = np.concatenate(allp)
        return a.min(axis=0), a.max(axis=0)


def load(path: Path) -> Model:
    doc, binary = ga.read_glb(path)
    mats = doc.get('materials', [])
    m = Model(Path(path).stem)
    parents = {}
    for i, world, parent in ga.walk(doc):
        parents[i] = parent
    for i, world, parent in ga.walk(doc):
        node = doc['nodes'][i]
        name = node.get('name', f'node{i}')
        m.nodes.append(name)
        if node.get('mesh') is None:
            continue
        chain, j = [], parent
        while j is not None:
            chain.append(doc['nodes'][j].get('name', f'node{j}'))
            j = parents.get(j)
        for prim in doc['meshes'][node['mesh']].get('primitives', []):
            attrs = prim.get('attributes', {})
            if 'POSITION' not in attrs or prim.get('mode', 4) != 4:
                continue
            pos = ga.accessor(doc, binary, attrs['POSITION']).astype(np.float64)
            pos = (np.c_[pos, np.ones(len(pos))] @ world.T)[:, :3]
            if 'indices' in prim:
                idx = ga.accessor(doc, binary, prim['indices']).reshape(-1).astype(np.int64)
            else:
                idx = np.arange(len(pos), dtype=np.int64)
            tris = idx[:len(idx) - len(idx) % 3].reshape(-1, 3)
            has = 'COLOR_0' in attrs
            lum = (ga.accessor(doc, binary, attrs['COLOR_0']).astype(np.float64)[:, :3] @ LUMA) if has \
                else np.ones(len(pos))
            mat = mats[prim['material']] if 'material' in prim and prim['material'] < len(mats) else {}
            bc = mat.get('pbrMetallicRoughness', {}).get('baseColorFactor', [0.8, 0.8, 0.8, 1])
            lum = np.clip(np.nan_to_num(lum, nan=1.0), 0, 1)
            # MVA W2-B: a node glb_merge_static.py merged reads as its members again (names, triangle ranges).
            merged = (node.get('extras') or {}).get('mergedFrom')
            for piece_name, part in (((n, tris[a:a + c]) for n, a, c in merged) if merged else ((name, tris),)):
                m.pieces.append(Piece(piece_name, tuple(reversed(chain)), mat.get('name', ''), float(np.dot(bc[:3], LUMA)),
                                      pos, part, lum, has))
    return m


# ----------------------------------------------------------------------------- geometry hashes
def _tri_keys(corners, q):
    """One int64 key per triangle, independent of its corner order (corners quantized at step q)."""
    c = np.round(corners / q).astype(np.int64)
    v = (c[..., 0] * 73856093) ^ (c[..., 1] * 19349663) ^ (c[..., 2] * 83492791)
    v = np.sort(v, axis=1)
    return (v[:, 0] * 1000003) ^ (v[:, 1] * 998244353) ^ (v[:, 2] * 7919)


def triangle_hashes(model: Model, skip=None, q_abs=0.002, min_tris=12):
    """(absolute keys, normalized keys) per triangle of every piece kept: absolute = model space at 2 mm (an
    unscaled copy); normalized = each piece fitted to a unit box per axis (a copy scaled or stretched part by part).
    Pieces under min_tris triangles or named by `skip` (kit components) are left out."""
    absk, normk, counted = [], [], 0
    for p in model.pieces:
        if len(p.tris) < min_tris or (skip and skip(p)):
            continue
        c = p.pos[p.tris]
        absk.append(_tri_keys(c, q_abs))
        lo, hi = p.pos.min(axis=0), p.pos.max(axis=0)
        span = np.where(hi - lo > 1e-6, hi - lo, 1.0)
        normk.append(_tri_keys((c - lo) / span, 1e-3))
        counted += len(p.tris)
    if not absk:
        return np.zeros(0, np.int64), np.zeros(0, np.int64)
    return np.concatenate(absk), np.concatenate(normk)


# ----------------------------------------------------------------------------- views
VIEWS = {
    # name: (yaw degrees, pitch degrees): the camera looks along -forward; pitch 0 = level, 90 = straight down
    'side': (90.0, 0.0), 'front': (0.0, 0.0), 'top': (0.0, 90.0), 'rear': (180.0, 0.0),
    'battle': (-45.0, 52.0),     # the battle camera: orthographic, pitch 52, yaw -45 (MODEL_STANDARD section 3.5)
}
PX_PER_M = 28.4                  # the default zoom on a 1080 px screen


def _basis(yaw, pitch):
    """Camera right, up and forward (towards the scene) in model space (+Y up, +Z front)."""
    y, p = math.radians(yaw), math.radians(pitch)
    # The camera sits in front of the model at yaw 0 (on +Z) looking back towards -Z.
    fwd = np.array([-math.sin(y) * math.cos(p), -math.sin(p), -math.cos(y) * math.cos(p)])
    right = np.cross(fwd, [0, 1, 0])
    if np.linalg.norm(right) < 1e-6:
        right = np.array([-math.cos(y), 0, math.sin(y)])
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    return right, up, fwd


SUN = np.array([0.45, 0.8, 0.4]) / np.linalg.norm([0.45, 0.8, 0.4])


def render(model: Model, view='battle', px=PX_PER_M, max_side=1400, mask_only=False, keep=None):
    """(grey image float [0, 1] with NaN outside the model, scale px/m). Flat shading: base x COLOR_0 x
    (0.35 + 0.65 * max(0, n.sun)); painter's order by depth (fine for convex-ish hard-surface parts)."""
    from PIL import Image, ImageDraw
    corners, shade, _ = model.soup(keep)
    if not len(corners):
        return np.full((4, 4), np.nan), px
    right, up, fwd = _basis(*VIEWS[view])
    u = corners @ right
    v = corners @ up
    d = corners @ fwd
    lo_u, hi_u, lo_v, hi_v = u.min(), u.max(), v.min(), v.max()
    span = max(hi_u - lo_u, hi_v - lo_v, 1e-3)
    if span * px > max_side:
        px = max_side / span
    w = int(math.ceil((hi_u - lo_u) * px)) + 6
    h = int(math.ceil((hi_v - lo_v) * px)) + 6
    X = (u - lo_u) * px + 3
    Y = (hi_v - v) * px + 3
    if mask_only:
        img = Image.new('L', (w, h), 0)
        draw = ImageDraw.Draw(img)
        for xs, ys in zip(X, Y):
            draw.polygon(list(zip(xs.tolist(), ys.tolist())), fill=255)
        return np.asarray(img) > 0, px
    n = np.cross(corners[:, 1] - corners[:, 0], corners[:, 2] - corners[:, 0])
    ln = np.linalg.norm(n, axis=1)
    ok = ln > 1e-12
    n[ok] /= ln[ok, None]
    facing = n @ fwd
    n = np.where(facing[:, None] > 0, -n, n)          # two-sided: light the side towards the camera
    lit = 0.35 + 0.65 * np.clip(n @ SUN, 0, 1)
    g = np.clip(shade * lit, 0, 1)
    order = np.argsort(-d.mean(axis=1))                  # far first
    img = Image.new('L', (w, h), 0)
    cov = Image.new('L', (w, h), 0)
    draw, dcov = ImageDraw.Draw(img), ImageDraw.Draw(cov)
    for i in order[ok[order]]:
        pts = list(zip(X[i].tolist(), Y[i].tolist()))
        val = int(round(1 + g[i] * 254))
        draw.polygon(pts, fill=val)
        dcov.polygon(pts, fill=255)
    a = np.asarray(img).astype(np.float64)
    out = (a - 1) / 254
    out[np.asarray(cov) == 0] = np.nan
    return out, px


def _sides(m):
    """Pixel sides between the mask and the outside (the boundary length in pixels, L1)."""
    pad = np.pad(m, 1)
    return float((pad[1:, :] != pad[:-1, :]).sum() + (pad[:, 1:] != pad[:, :-1]).sum())


def silhouette_ratio(mask):
    """(silhouette boundary / its convex hull's boundary, both counted as pixel sides so the measure is the same for
    every orientation; 1 = convex, higher = more notches and protrusions; the boundary length in pixels)."""
    from PIL import Image, ImageDraw
    from scipy.spatial import ConvexHull
    m = mask.astype(bool)
    if m.sum() < 10:
        return 1.0, 0.0
    ys, xs = np.nonzero(m)
    pts = np.c_[xs, ys].astype(float)
    pts = np.concatenate([pts, pts + [1, 0], pts + [0, 1], pts + [1, 1]])
    try:
        hull = ConvexHull(pts)
    except Exception:
        return 1.0, _sides(m)
    img = Image.new('L', (m.shape[1] + 2, m.shape[0] + 2), 0)
    ImageDraw.Draw(img).polygon([tuple(p) for p in pts[hull.vertices].tolist()], fill=255)
    hm = np.asarray(img)[:m.shape[0], :m.shape[1]] > 0
    hs = _sides(hm | m)
    s = _sides(m)
    return (s / hs if hs else 1.0), s


def edge_density(img):
    """Share of the model's pixels on a visible shading edge (|gradient| > 0.06 of the grey range)."""
    inside = ~np.isnan(img)
    if inside.sum() < 10:
        return 0.0
    g = np.where(inside, img, 0.0)
    gx = np.abs(np.diff(g, axis=1))[:-1, :]
    gy = np.abs(np.diff(g, axis=0))[:, :-1]
    mag = np.maximum(gx, gy)
    both = inside[:-1, :-1] & inside[1:, :-1] & inside[:-1, 1:]
    return float(((mag > 0.06) & both).sum() / max(1, inside.sum()))


def brightness_regions(img, levels=12, min_px=6):
    """Connected regions of equal quantized brightness (12 levels) with at least min_px pixels, per 1000 model
    pixels."""
    from scipy import ndimage
    inside = ~np.isnan(img)
    if inside.sum() < 10:
        return 0.0
    q = np.where(inside, np.clip((np.nan_to_num(img) * levels).astype(int), 0, levels - 1), -1)
    total = 0
    for lv in range(levels):
        lab, n = ndimage.label(q == lv)
        if n:
            sizes = np.bincount(lab.ravel())[1:]
            total += int((sizes >= min_px).sum())
    return 1000.0 * total / inside.sum()


def file_hash(path: Path):
    return hashlib.sha1(Path(path).read_bytes()).hexdigest()[:12]
