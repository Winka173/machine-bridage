"""Barrel audit (owner 06/10, DECISIONS "## Barrels: battleship triple turrets + audit"): for every unit, tower and boss
mount in balance.json, the data's barrels (resolved through "inherits", the boss "mountWeapons" swaps and variants) against
the barrels the model shows at that mount.

Static: balance.json, Resources/Models/*.glb. No Unity, no Blender.

    python Tools/assets/barrel_audit.py              # print the mismatches, write Docs/models/barrel_audit.json
    python Tools/assets/barrel_audit.py --all        # print every gun mount

Per mount (the k-th mount of a slot is the k-th Muzzle_<slot> in canonical order, as the runtime and
runtime_node_audit.py read it):
  - data: "barrels" (1 by default) and "salvoMode" of the mount's weapon;
  - model, authored: the Muzzle_b<k>_<tag> children of the mount's Muzzle_<slot> (the builder's per-barrel muzzles);
  - model, seen: the barrels found in the meshes: long thin connected pieces whose front end lies at that muzzle (level
    with it along the piece's axis, beside it across), each closer to this muzzle than to any other Muzzle_ node,
    pieces on one axis (a barrel and its sleeve, brake, bore evacuator) counted once. A rotary gun's tubes sit on one
    axis within its cluster and count as one barrel (one stream of fire).
The model's count is the authored one when the muzzle has them, else the seen one.

Kinds left out of the match (listed, never a mismatch): launchers (missile, rocket, drone, bomb, torpedo, cruise and
ballistic families and the missile / rocket / aam slots: their Muzzle_b points are launch cells, not barrels), rotary
guns (CIWS, M134, GAU-8, M61: one muzzle stream), flame, laser, melee, special, mortars and howitzer batteries fired as a
ripple salvo (owner 06/10: they keep their firing), railguns and coilguns (their rails are one bore), and mounts with no
muzzle node.

Status: ok | mismatch (data barrels != model barrels) | not_simultaneous (a gun with 2+ barrels that fires them as a
ripple; owner 06/10: every multi-barrel gun turret fires its barrels together) | skip (a kind above) | no_muzzle.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'Tools/balance'))

import glb_analyze as ga  # noqa: E402
import glb_check  # noqa: E402
import glb_mesh  # noqa: E402
import runtime_nodes as rn  # noqa: E402

MODELS = ROOT / 'Assets/MachineBrigade/Resources/Models'
OUT = ROOT / 'Docs/models/barrel_audit.json'
BARREL_CHILD = re.compile(r'^Muzzle_b(\d+)_')
LAUNCH_FAMILIES = {'rocket', 'atgm', 'aa_missile', 'drone', 'missile', 'bomb', 'cruise', 'cruise_missile', 'ballistic',
                   'torpedo', 'grenade'}
LAUNCH_SLOTS = {'missile', 'rocket', 'aam', 'bomb', 'drone'}
OTHER_FAMILIES = {'flame', 'laser', 'melee', 'special', 'railgun'}   # a railgun's or coilgun's rails are one bore
ROTARY = re.compile(r'gatling|rotary|minigun|M134|GAU|M61|Vulcan|Phalanx|CIWS|AK-630|Type 1130|Goalkeeper|six-barrel|'
                    r'6-barrel|GSh-6|GSh-30|XM214|Dillon|multi-barrel', re.I)
RIPPLE_SALVO = {'mortar'}   # a mortar battery's salvo keeps its ripple (owner 06/10)

# Thresholds of a barrel (metres): long and thin, its front end at the muzzle.
MIN_LEN = 0.25
THIN = 4.5
LEVEL = 0.35         # along the axis: the tip within this (or 7 % of the length) of the muzzle's depth
ACROSS_MIN = 0.45    # across: within max(this, 22 % of the length), at most ACROSS_MAX
ACROSS_MAX = 3.2
SAME_AXIS = 0.16
SAME_LENGTH = 0.7    # a mount's barrels are at least this share of its longest one
COS_MOUNT = float(np.cos(np.radians(30)))
COS_HULL = float(np.cos(np.radians(12)))     # tips closer than this across are one barrel (a sleeve, a brake, a rotary cluster)


# ------------------------------------------------------------------------------------------------ data
def units(data):
    """[(unit id, model, [(mount index, slot, weapon id)])]: every vehicle, tower and boss as the loader builds it."""
    import p26_ab as A
    bosses = A.expand(copy.deepcopy(data))
    by_id = {v['id']: v for v in data['vehicles']}

    def field(v, key, depth=0):
        if key in v or depth > 8:
            return v.get(key)
        parent = by_id.get(v.get('inherits') or v.get('variantOf') or v.get('eliteOf') or '')
        return field(parent, key, depth + 1) if parent else None

    resolved = {u['id']: u for u in glb_check.resolve(data['vehicles'])}
    out = []
    for v in data['vehicles']:
        d = bosses.get(v['id'], v)
        model = d.get('model') or field(v, 'model') or resolved[v['id']]['model']
        # An elite or a copy with no model of its own wears its parent's (the first in its chain that ships).
        chain, p = [resolved[v['id']]['model']], v
        while p is not None and len(chain) < 10:
            p = by_id.get(p.get('eliteOf') or p.get('inherits') or p.get('variantOf') or '')
            if p is not None:
                chain.append(p.get('model') or p['id'])
        if not (MODELS / f'{model}.glb').exists():
            model = next((c for c in chain if (MODELS / f'{c}.glb').exists()), model)
        # A tower branch wears its letter's model when it ships (TowerArt.ModelFor; balance.json "art").
        if v.get('branchOf') and v.get('art') and (MODELS / f"{v['art']}.glb").exists():
            model = v['art']
        weapon = d.get('weapon') if v['id'] in bosses else field(v, 'weapon')
        secondary = d.get('secondary') if v['id'] in bosses else field(v, 'secondary')
        main_slot = (d.get('mainSlot') if v['id'] in bosses else field(v, 'mainSlot')) or 'main'
        mounts = []
        if weapon:
            mounts.append((0, main_slot.lower(), weapon))
        for i, s in enumerate(secondary or []):
            if s.get('weapon'):
                mounts.append((i + 1, (s.get('slot') or 'main').lower(), s['weapon']))
        if mounts:
            out.append((v['id'], model, mounts))
    return out


def kind_of(w, slot):
    """'gun' (matched) or why the mount is left out."""
    fam = (w.get('family') or '').lower()
    real = w.get('real') or ''
    if slot in LAUNCH_SLOTS or fam in LAUNCH_FAMILIES or w.get('projectile') in ('Missile', 'Rocket', 'Drone', 'Bomb'):
        return 'launcher'
    if fam in OTHER_FAMILIES or w.get('melee'):
        return fam or 'melee'
    if ROTARY.search(real) or ROTARY.search(w['id']):
        return 'rotary'
    if fam in RIPPLE_SALVO and int(w.get('burst', 1)) > 1:
        return 'mortar_salvo'
    return 'gun'


# ------------------------------------------------------------------------------------------------ model
class ModelBarrels:
    def __init__(self, path: Path):
        self.path = path
        doc, _ = rn.read_doc(path)
        nodes = doc.get('nodes', [])
        self.names = [n.get('name', '') for n in nodes]
        mats, parent = rn.world_matrices(doc)
        self.groups = rn.groups(self.names)
        self.children = {i: [self.names[c] for c in n.get('children', [])] for i, n in enumerate(nodes)}
        self.index = {n: i for i, n in reversed(list(enumerate(self.names)))}
        self.pos = {n: mats[i][:3, 3] for n, i in self.index.items()}
        self.muzzles = [n for n in self.names if (p := rn.parse(n)) and p[0] == 'muzzle']
        # Each muzzle's pivot (the nearest Mount_* or Turret above it) and its front (the node's +Z).
        self.pivot = {}
        self.front = {}
        for m in self.muzzles:
            i = self.index[m]
            self.pivot[m] = None
            while i in parent:
                i = parent[i]
                a = self.names[i]
                if (p := rn.parse(a)) and p[0] == 'mount' or rn.SET_PATTERNS['turret'].match(a):
                    self.pivot[m] = a
                    break
            f = mats[self.index[m]][:3, 2]
            self.front[m] = f / (np.linalg.norm(f) or 1.0)
        self._seen = None

    def authored(self, muzzle):
        return sorted(c for c in self.children.get(self.index[muzzle], []) if BARREL_CHILD.match(c))

    def seen(self, muzzle):
        if self._seen is None:
            self._seen = self._find()
        return self._seen.get(muzzle, [])

    def _find(self):
        """{muzzle: [tip points]} of the barrels in the meshes."""
        if not self.muzzles:
            return {}
        model = glb_mesh.load(self.path)
        mpos = np.array([self.pos[m] for m in self.muzzles])
        mfront = np.array([self.front[m] for m in self.muzzles])
        found = {m: [] for m in self.muzzles}
        for piece in model.pieces:
            if not len(piece.tris):
                continue
            used = np.unique(piece.tris)
            remap = np.zeros(len(piece.pos), dtype=np.int64)
            remap[used] = np.arange(len(used))
            tris = remap[piece.tris]
            pts = piece.pos[used]
            chain = set(piece.chain) | {piece.node}
            # A turret's barrels ride its pivot; a hull gun's (no pivot) may be any mesh.
            allowed = np.array([self.pivot[m] is None or self.pivot[m] in chain for m in self.muzzles])
            if not allowed.any():
                continue
            labels = _components(pts, tris)
            for lab in np.unique(labels):
                p = pts[labels == lab]
                if len(p) < 6:
                    continue
                hit = _barrel(p, mpos, mfront, allowed,
                              np.array([self.pivot[m] is None for m in self.muzzles]))
                if hit is None:
                    continue
                j, tip, length = hit
                found[self.muzzles[j]].append((tip, length))
        out = {}
        for m, tips in found.items():
            # One mount's barrels are as long as each other: a shorter rod beside the barrel (a gas tube, a sight, an
            # aerial) is not one.
            longest = max((n for _, n in tips), default=0.0)
            merged = []
            for t, n in sorted(tips, key=lambda x: -x[1]):
                if n >= SAME_LENGTH * longest and not any(np.linalg.norm(t - u) < SAME_AXIS for u in merged):
                    merged.append(t)
            out[m] = merged
        return out


def _components(pts, tris):
    """Connected pieces, vertices welded by position (1 mm)."""
    q = np.round(pts / 0.001).astype(np.int64)
    _, weld = np.unique(q, axis=0, return_inverse=True)
    weld = weld.reshape(-1)
    n = weld.max() + 1
    parent = np.arange(n)

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for a, b, c in weld[tris]:
        ra, rb, rc = find(a), find(b), find(c)
        parent[rb] = ra
        parent[find(rc)] = ra
    roots = np.array([find(i) for i in range(n)])
    return roots[weld]


def _barrel(p, mpos, mfront, allowed, hull):
    """(muzzle index, tip) when the piece is a barrel whose front end is at one of the muzzles, else None."""
    mean = p.mean(axis=0)
    c = p - mean
    w, v = np.linalg.eigh(c.T @ c / len(p))
    axis = v[:, 2]
    along = c @ axis
    length = along.max() - along.min()
    across = np.linalg.norm(c - np.outer(along, axis), axis=1)
    width = 2 * across.max()
    if length < MIN_LEN or length < THIN * max(width, 1e-3):
        return None
    ends = (mean + axis * along.max(), mean + axis * along.min())
    best = None
    for tip, sign in ((ends[0], 1), (ends[1], -1)):
        ax = axis * sign
        d = mpos - tip
        lev = d @ ax
        acr = np.linalg.norm(d - np.outer(lev, ax), axis=1)
        # Along the muzzle's front: 30 degrees on a turning mount (an elevated barrel), 12 on the hull.
        cos = mfront @ ax
        ok = allowed & (cos >= np.where(hull, COS_HULL, COS_MOUNT)) & (np.abs(lev) <= max(LEVEL, 0.07 * length)) &             (acr <= min(ACROSS_MAX, max(ACROSS_MIN, 0.22 * length)))
        if not ok.any():
            continue
        dist = np.where(ok, np.linalg.norm(d, axis=1), np.inf)
        j = int(np.argmin(dist))
        if best is None or dist[j] < best[2]:
            best = (j, tip, dist[j])
    return None if best is None else (best[0], best[1], length)


# ------------------------------------------------------------------------------------------------ audit
def audit(data=None):
    import p34_families as F
    data = data or glb_check.load_balance()
    ws = F.Weapons(data)
    models = {}
    rows = []
    for uid, model, mounts in units(data):
        per_slot = {}
        for idx, slot, wid in mounts:
            k = per_slot.get(slot, 0)
            per_slot[slot] = k + 1
            if wid not in ws.raw:
                rows.append(dict(unit=uid, model=model, mount=idx, slot=slot, weapon=wid, status='no_weapon'))
                continue
            w = ws.resolve(wid)
            barrels = int(w.get('barrels', 1))
            simul = w.get('salvoMode') == 'SIMULTANEOUS'
            kind = kind_of(w, slot)
            row = dict(unit=uid, model=model, mount=idx, slot=slot, k=k, weapon=wid, real=w.get('real', ''),
                       kind=kind, barrels=barrels, simultaneous=simul, burst=int(w.get('burst', 1)),
                       clip=int(w.get('clip', 0) or 0))
            for name in (model, model + '_hd'):
                path = MODELS / f'{name}.glb'
                if not path.exists():
                    continue
                if name not in models:
                    models[name] = ModelBarrels(path)
                mb = models[name]
                muz = mb.groups.get(('muzzle', slot), [])
                if not muz:
                    if name == model:
                        row['muzzle'] = None
                    continue
                m = muz[k % len(muz)]
                auth = mb.authored(m)
                seen = mb.seen(m) if kind == 'gun' else []
                n_model = len(auth) if auth else max(1, len(seen))
                pre = '' if name == model else 'hd_'
                row[pre + 'muzzle'] = m
                row[pre + 'authored'] = len(auth)
                row[pre + 'seen'] = len(seen)
                row[pre + 'model_barrels'] = n_model
            if kind != 'gun':
                row['status'] = 'skip'
            elif not row.get('muzzle'):
                row['status'] = 'no_muzzle'
            elif row['model_barrels'] != barrels or ('hd_model_barrels' in row and row['hd_model_barrels'] != barrels):
                row['status'] = 'mismatch'
            elif barrels > 1 and not simul:
                row['status'] = 'not_simultaneous'
            else:
                row['status'] = 'ok'
            rows.append(row)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--out', default=str(OUT))
    args = ap.parse_args()
    rows = audit()
    Path(args.out).write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding='utf-8')
    counts = {}
    for r in rows:
        counts[r['status']] = counts.get(r['status'], 0) + 1
    for r in rows:
        if args.all and r.get('kind') == 'gun' or r['status'] in ('mismatch', 'not_simultaneous', 'no_weapon'):
            hd = f" hd {r['hd_model_barrels']}" if 'hd_model_barrels' in r else ''
            print(f"{r['status']:16s} {r['unit']:28s} m{r['mount']} {r['slot']:5s} {r['weapon']:34s} data {r.get('barrels')}"
                  f"{' SIM' if r.get('simultaneous') else ''} b{r.get('burst')} | {r.get('muzzle')} auth {r.get('authored')}"
                  f" seen {r.get('seen')}{hd}")
    print('totals:', ', '.join(f'{k} {v}' for k, v in sorted(counts.items())))
    return 1 if counts.get('mismatch') or counts.get('not_simultaneous') else 0


if __name__ == '__main__':
    sys.exit(main())
