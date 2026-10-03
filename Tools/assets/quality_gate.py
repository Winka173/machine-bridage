"""Prompt 35 section 5: the model quality gate (hard gates + a 0-100 soft score against the gold standard).

    python Tools/assets/quality_gate.py                     # every scored model -> Docs/models/quality_report.xlsx/.csv
    python Tools/assets/quality_gate.py --ids ixion,apc     # only these (printed; the report keeps the other rows)
    python Tools/assets/quality_gate.py --gold              # recompute the gold metrics -> Docs/models/GOLD_METRICS.md

Static only (numpy + PIL + scipy; no Unity, no Blender). Pictures are drawn by glb_mesh.render (flat shaded,
orthographic, the battle camera's 28.4 px per metre), so every model is measured the same way; the in-game sheets
(ModelScan) stay the reviewer's pictures. Rules: Docs/models/MODEL_STANDARD.md (budgets, parts, mounts) and
Docs/prompts/prompt35_vi.txt section 5; decisions in Docs/DECISIONS.md "Prompt 35".

Hard gates (a fail = not passed): triangle floor (70 % of the class minimum; over the maximum is information only,
the owner's rule), required parts, muzzles / mounts / Mount_Flare / Mount_APS / boss part nodes, size against
modelSize within 10 %, own geometry (at most 30 % of triangles shared with another model family), no zero-area
triangles, materials and COLOR_0 on every mesh, colour zones (materials) >= N, AO + dust + wear in COLOR_0, body not a
single block (>= 3 sloped face directions on the hull / turret).
Soft score: silhouette complexity, edge density, brightness regions, own parts per m2, detail tiers, asymmetry, each
against the gold mean of the model's class (thresholds 85 / 80 / 80 / 80 / 100 % of gold), weighted to 0-100.
"""
from __future__ import annotations

import sys as _sys
try:
    _sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'Tools' / 'models'))
import glb_analyze  # noqa: E402
import glb_mesh as gm  # noqa: E402
import scan_prep as sp  # noqa: E402

MODELS = sp.MODELS
DOCS = ROOT / 'Docs' / 'models'
REPORT_CSV = DOCS / 'quality_report.csv'
REPORT_XLSX = DOCS / 'quality_report.xlsx'
GOLD_JSON = HERE / 'gold_metrics.json'
GOLD_MD = DOCS / 'GOLD_METRICS.md'
VISUAL = DOCS / 'scan' / 'visual_scores.md'

GOLD_V2 = {'main_battle_tank': 'tracked', 'fighter_jet': 'jet', 'attack_helicopter': 'helicopter', 'silver_bug': 'boss'}
FLOOR = 0.70                     # the triangle floor: 70 % of the class minimum
SIZE_TOL = 0.10
SHARED_MAX = 0.30
ZONES = {'tracked': 4, 'wheeled': 4, 'ground': 4, 'jet': 4, 'helicopter': 4, 'air_other': 3, 'ship': 5, 'boss': 6,
         'tower': 3, 'structure': 3, 'hq': 3, 'obstacle': 2}
# A class without gold models of its own borrows the nearest class's (DECISIONS "Prompt 35").
NEAREST = {'wheeled': 'tracked', 'ground': 'tracked', 'air_other': 'helicopter', 'ship': 'boss', 'hq': 'structure',
           'obstacle': 'structure', 'structure': 'tower', 'tower': 'structure'}
SOFT = (  # (metric, weight, share of the gold mean that scores full marks)
    ('silhouette', 25, 0.85), ('edges', 15, 0.80), ('regions', 15, 0.80), ('parts_m2', 20, 0.80),
    ('tiers', 15, 1.00), ('asymmetry', 10, 1.00))
TOP_SHARE = 0.10
# Owner decision 5 (prompt 35 pilot review): each boss frame has its own gold set (a ground boss is not scored against
# trains). The class key is 'boss_<frame>'; a frame without a gold model uses the whole boss gold.
BOSS_FRAMES = ('ground', 'rail', 'air', 'sea')
RAIL_NODE = re.compile(r'^(Bogies?|Wheel_flanges|Sleepers|Rail_wheels)(?:$|[._0-9])', re.I)
for _f in BOSS_FRAMES:
    NEAREST[f'boss_{_f}'] = 'boss'
# Owner decision 6: units seen in numbers (technicals, light vehicles, towers) stay under 1.5 x the class maximum; a
# hard gate for these budget classes only (over-budget stays information for the others).
NUMBERS_CAP = {'light': 1.5, 'tower': 1.5}
# Owner decision 8: a role, muzzle or mount the kit merged into another node counts when that node is there
# (MODEL_STANDARD section 4: a part the sheet shows inside a merged node is cleared). {model: {item: host node}};
# the four V2 gold models here, a rebuilt model in its spec ("merged": {...}, Tools/blender/specs/<id>.json).
MERGED = {
    'main_battle_tank': {'mantlet': 'Turret_body', 'idler': 'Wheels'},
    'fighter_jet': {'tail': 'Fuselage', 'Mount_aam': 'Wingtip_missiles'},
    'attack_helicopter': {'Muzzle_rocket': 'Pods', 'Mount_rocket': 'Pods', 'Mount_aam': 'Stinger_tubes'},
    'silver_bug': {'Mount_APS': 'Pd_base'},
}
SPECS = ROOT / 'Tools' / 'blender' / 'specs'


def merged_for(model):
    out = dict(MERGED.get(model, {}))
    spec = SPECS / f'{model}.json'
    if spec.exists():
        try:
            out.update(json.loads(spec.read_text(encoding='utf-8')).get('merged') or {})
        except ValueError:
            pass
    return out


def boss_frame(defs, own, names):
    """ground / rail / air / sea (decision 5): air and sea from the def, rail from the running gear's nodes."""
    f = sp.boss_frame(defs, own)
    if f == 'ship':
        return 'sea'
    if f == 'ground' and any(RAIL_NODE.match(n) for n in names):
        return 'rail'
    return f


def gold_class(defs, model, own, cls, names):
    """The key of the gold set a model is scored against."""
    return f'boss_{boss_frame(defs, own, names)}' if cls == 'boss' and own is not None else cls
FLARE = re.compile(r'^Mount_flare(_[a-z]+)?(\.\d+)?$', re.I)
FAMILY_SUFFIX = re.compile(r'(_hd|_a|_b|_chute|_wreck|_deployed|_dug|_dugin|_open|_mk\d|_old|_lod\d)$')
# Kit component pieces (frontier_kit, mb_parts27, mb_kit35 names): allowed to repeat across models.
KIT_PIECE = re.compile(r'^(Tyres?|Wheels?|Hubs?|Wheel_bolts|Wheel_nuts|Sprockets?|Idlers?|Tracks?|Track_links|Hatch(es)?|'
                       r'Hatch_fittings|MG|MG_\w+|Smoke\w*|Antennas?|Rotor_\w+|Tail_rotor\w*|Nozzle\w*|Exhaust\w*|'
                       r'Missiles?|Missile_\w+|Pods?|Pod_\w+|Bolts|Rivets|Welds|Lamps|Lamp_\w+|Grilles?|Handles|Hinges|'
                       r'Kit_\w+|Rails?|Railings|Ladders?|Sandbags?|Glass|Cab_glass)(\.\d+)?$', re.I)


def family(name):
    prev = None
    while prev != name:
        prev, name = name, FAMILY_SUFFIX.sub('', name)
    return name


# ----------------------------------------------------------------------------- shared geometry
def geometry_overlap(names, pool=None, ubiquitous=6):
    """{model: (share_all, share_body, partner)}: the share of each model's triangles whose key (absolute or
    normalized, see glb_mesh.triangle_hashes) is also in another model family's file; share_body leaves the kit's
    component pieces out. Keys found in more than `ubiquitous` families are generic primitives and do not count."""
    pool = pool or sorted(p.stem for p in MODELS.glob('*.glb'))
    keys_all, keys_body = {}, {}
    for n in pool:
        try:
            m = gm.load(MODELS / f'{n}.glb')
        except Exception:
            continue
        a1, n1 = gm.triangle_hashes(m)
        a2, n2 = gm.triangle_hashes(m, skip=lambda p: KIT_PIECE.match(p.node))
        keys_all[n] = (np.unique(a1), np.unique(n1), len(a1))
        keys_body[n] = (a2, n2, a1, n1)
    fams = {n: family(n) for n in keys_all}
    out = {}
    counts_abs = _counts([keys_all[n][0] for n in keys_all], [fams[n] for n in keys_all])
    counts_norm = _counts([keys_all[n][1] for n in keys_all], [fams[n] for n in keys_all])
    for n in names:
        if n not in keys_body:
            continue
        ab, nbk, aa, na = keys_body[n]
        res = []
        for ak, nk in ((aa, na), (ab, nbk)):
            if not len(ak):
                res.append(0.0)
                continue
            ca = _lookup(counts_abs, ak)
            cn = _lookup(counts_norm, nk)
            shared = ((ca >= 2) & (ca <= ubiquitous)) | ((cn >= 2) & (cn <= ubiquitous))
            res.append(float(shared.mean()))
        partner = _partner(n, keys_all, fams) if max(res) >= 0.1 else ''
        out[n] = (round(res[0], 3), round(res[1], 3), partner)
    return out


def _counts(key_lists, fam_list):
    ks, fs = [], []
    fam_ids = {f: i for i, f in enumerate(sorted(set(fam_list)))}
    for k, f in zip(key_lists, fam_list):
        ks.append(k)
        fs.append(np.full(len(k), fam_ids[f], dtype=np.int64))
    if not ks:
        return np.zeros(0, np.int64), np.zeros(0, np.int64)
    pair = np.unique(np.c_[np.concatenate(ks), np.concatenate(fs)], axis=0)
    return np.unique(pair[:, 0], return_counts=True)


def _lookup(table, keys):
    k, c = table
    i = np.searchsorted(k, keys)
    i = np.clip(i, 0, len(k) - 1)
    return np.where(k[i] == keys, c[i], 0)


def _partner(n, keys_all, fams):
    """The other model family sharing most triangle keys with n."""
    a, b, _ = keys_all[n]
    best, who = 0, ''
    for m, (a2, b2, _) in keys_all.items():
        if fams[m] == fams[n]:
            continue
        s = len(np.intersect1d(a, a2, assume_unique=True)) + len(np.intersect1d(b, b2, assume_unique=True))
        if s > best:
            best, who = s, m
    return who


_ADDED = {}


def first_added(model):
    """Unix time the model's GLB first entered git (None when unknown)."""
    if model not in _ADDED:
        import subprocess
        rel = f'Assets/MachineBrigade/Resources/Models/{model}.glb'
        try:
            outp = subprocess.run(['git', '-C', str(ROOT), 'log', '--diff-filter=A', '--format=%at', '--', rel],
                                  capture_output=True, text=True, timeout=60).stdout.split()
            _ADDED[model] = int(outp[-1]) if outp else None
        except Exception:
            _ADDED[model] = None
    return _ADDED[model]


def is_original(model, partner):
    """True when `model` is the source of the shared geometry: a gold model, or its GLB is older than the
    partner's (the partner was built from it)."""
    if model in GOLD_V2:
        return True
    if partner in GOLD_V2:
        return False
    a, b = first_added(model), first_added(partner)
    return a is not None and b is not None and a < b


# ----------------------------------------------------------------------------- per-model metrics
def _components(piece):
    """Connected pieces of one mesh (welded at 0.1 mm): [(triangle count, sorted bbox dims)]."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    if not len(piece.tris):
        return []
    q = np.round(piece.pos / 1e-4).astype(np.int64)
    _, weld = np.unique(q, axis=0, return_inverse=True)
    weld = weld.reshape(-1)
    t = weld[piece.tris]
    n = int(weld.max()) + 1
    rows = np.concatenate([t[:, 0], t[:, 1]])
    cols = np.concatenate([t[:, 1], t[:, 2]])
    g = coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n))
    nc, lab = connected_components(g, directed=False)
    tl = lab[t[:, 0]]
    out = []
    wpos = np.zeros((n, 3))
    wpos[weld] = piece.pos
    for c in np.unique(tl):
        sel = t[tl == c]
        p = wpos[np.unique(sel)]
        dims = np.sort(p.max(axis=0) - p.min(axis=0))[::-1]
        out.append((len(sel), dims))
    return out


def _area(model):
    total = 0.0
    for p in model.pieces:
        if len(p.tris):
            c = p.pos[p.tris]
            total += 0.5 * np.linalg.norm(np.cross(c[:, 1] - c[:, 0], c[:, 2] - c[:, 0]), axis=1).sum()
    return total


BODY = re.compile(r'^(Hull|Body|Chassis|Turret|Turret_body|Casemate|Fuselage|Superstructure|Deck|Cab|Base|Block|Team)',
                  re.I)
# A structure's main volumes are its roof, walls, berm and shelter, not only its base (wave 1: a shed with a gable roof
# read as "0 sloped directions" because only the slab was looked at).
BODY_STRUCTURE = re.compile(BODY.pattern + r'|^(Roof|Walls?|Berm|Shelter|Bunker|Revetment)', re.I)


def _sloped_directions(model, structure=False):
    """Distinct sloped face directions (not within 15 degrees of an axis, at least 0.5 % of the body's area) on the
    hull / turret / body pieces (or the two largest pieces when none is named so); a structure's roof, walls and berm
    count as its body."""
    rx = BODY_STRUCTURE if structure else BODY
    body = [p for p in model.pieces if rx.match(p.node) and len(p.tris)]
    if not body:
        body = sorted((p for p in model.pieces if len(p.tris)), key=lambda p: -len(p.tris))[:2]
    dirs, areas = [], []
    for p in body:
        c = p.pos[p.tris]
        n = np.cross(c[:, 1] - c[:, 0], c[:, 2] - c[:, 0])
        a = np.linalg.norm(n, axis=1)
        ok = a > 1e-9
        dirs.append(n[ok] / a[ok, None])
        areas.append(a[ok] / 2)
    if not dirs:
        return 0
    d = np.concatenate(dirs)
    a = np.concatenate(areas)
    sloped = np.abs(d).max(axis=1) < math.cos(math.radians(15))
    if not sloped.any():
        return 0
    d, a = d[sloped], a[sloped]
    q = np.round(d * 4).astype(int)              # ~15-degree bins
    keys, inv = np.unique(q, axis=0, return_inverse=True)
    sums = np.bincount(inv.reshape(-1), weights=a)
    return int((sums >= 0.005 * sum(x.sum() for x in areas)).sum())


def metrics(model, length_ref=7.0, structure=False):
    """The soft metrics of one model (see the module notes)."""
    out = {}
    sil = []
    for v in ('side', 'front', 'top'):
        lo, hi = model.bounds()
        span = float(max(hi - lo))
        mask, _ = gm.render(model, v, px=256 / max(span, 1e-3), mask_only=True)
        sil.append(gm.silhouette_ratio(mask)[0])
    out['silhouette'] = float(np.mean(sil))
    img, _ = gm.render(model, 'battle')
    out['edges'] = gm.edge_density(img)
    out['regions'] = gm.brightness_regions(img)
    top, _ = gm.render(model, 'top', px=256 / max(float(max(model.bounds()[1] - model.bounds()[0])), 1e-3),
                       mask_only=True)
    inter = (top & top[:, ::-1]).sum()
    union = (top | top[:, ::-1]).sum()
    out['asym_raw'] = float(1 - inter / union) if union else 0.0
    lo, hi = model.bounds()
    L = float(max(hi - lo))
    scale = max(1.0, L / length_ref)
    area = _area(model) / scale ** 2
    comps = []
    for p in model.pieces:
        comps += _components(p)
    t3, t1 = 0.3 * scale, 0.25 * L
    tiers = [sum(1 for _, d in comps if d[0] >= t1), sum(1 for _, d in comps if t3 <= d[0] < t1),
             sum(1 for _, d in comps if d[0] < t3)]
    sigs = {(n, tuple(np.round(d / (0.02 * scale)).astype(int))) for n, d in comps}
    out['pieces'] = len(comps)
    out['unique_pieces'] = len(sigs)
    out['parts_m2'] = len(sigs) / max(area, 1e-3)
    out['tier1'], out['tier2'], out['tier3'] = tiers
    out['tier2_m2'] = tiers[1] / max(area, 1e-3)
    out['tier3_m2'] = tiers[2] / max(area, 1e-3)
    out['area_scaled'] = area
    # A structure takes the better of the two readings (its base and fittings, or its roof / walls / berm too), so a
    # tower that passed on its base alone still passes.
    out['sloped_dirs'] = max(_sloped_directions(model), _sloped_directions(model, True)) if structure else         _sloped_directions(model)
    out['zones'] = len({p.material for p in model.pieces if len(p.tris)})
    lum = np.concatenate([p.lum for p in model.pieces if p.has_color]) if any(p.has_color for p in model.pieces) \
        else np.zeros(0)
    if len(lum):
        out['c0_p05'], out['c0_p95'] = float(np.percentile(lum, 5)), float(np.percentile(lum, 95))
        out['c0_wear'] = float((lum > 0.83).mean())
        ys = np.concatenate([p.pos[:, 1] for p in model.pieces if p.has_color])
        low = ys < lo[1] + 0.15 * (hi[1] - lo[1])
        highm = ys > lo[1] + 0.5 * (hi[1] - lo[1])
        out['c0_dust'] = float(lum[highm].mean() - lum[low].mean()) if low.any() and highm.any() else 0.0
    out['no_color'] = sum(1 for p in model.pieces if not p.has_color and len(p.tris))
    return out


def soft_score(m, gold):
    """(0-100, per-metric shares)."""
    shares = {}
    total = 0.0
    for key, weight, need in SOFT:
        if key == 'asymmetry':
            a = m['asym_raw']
            s = 1.0 if min(0.01, 0.8 * (gold.get('asym_raw') or 0)) <= a <= 0.35 else 0.5
        elif key == 'tiers':
            parts = []
            for t in ('tier2_m2', 'tier3_m2'):
                g = gold.get(t) or 0
                parts.append(min(1.0, m[t] / g) if g > 0 else 1.0)
            s = float(np.mean(parts))
        else:
            g = gold.get(key) or 0
            if key == 'silhouette':      # complexity above convex (1.0): compare the excess
                s = min(1.0, max(0.0, (m[key] - 1) / ((g - 1) * need))) if g > 1 else 1.0
            else:
                s = min(1.0, m[key] / (g * need)) if g > 0 else 1.0
        shares[key] = round(s, 3)
        total += weight * s
    return round(total * 100 / sum(w for _, w, _ in SOFT), 1), shares


def grade(score):
    return 'Tốt' if score >= 80 else 'Cần sửa' if score >= 60 else 'Kém'


# ----------------------------------------------------------------------------- static (hard) checks
def hard_checks(defs, model, own, cls, rec, m, overlap):
    """[(gate, ok, note)] for one model."""
    names = rec['nodeNames']
    bcls = sp.budget_class(defs, cls, own)
    lo, hi = sp.BUDGET[bcls]
    tris = rec['triangles']
    cap = NUMBERS_CAP.get(bcls)
    out = [('triangles_floor', tris >= FLOOR * lo, f'{tris} (floor {int(FLOOR * lo)}, class {lo}-{hi}'
            + (f'; over max +{tris / hi - 1:.0%}' + ('' if cap else ', information only') if tris > hi else '')
            + ')')]
    if cap:
        out.append(('triangles_cap', tris <= cap * hi, f'{tris} (seen in numbers: at most {cap:g} x {hi} = '
                    f'{int(cap * hi)})'))
    merged = merged_for(model)
    have = set(names)

    def cleared(item):
        host = merged.get(item)
        return bool(host) and any(n == host or re.sub(r'\.\d{3}$', '', n) == host for n in have)
    if cls == 'boss':
        frame = sp.boss_frame(defs, own)
        roles = [sp.BOSS_ROLES['body'], sp.BOSS_ROLES['weapons'], sp.BOSS_ROLES[frame]]
    else:
        roles = list(sp.ROLES.get(cls, []))
        if cls == 'tracked' and own is not None and not defs.field(own, 'turretTurnRate'):
            roles = [r for r in roles if r[0] not in ('turret', 'mantlet')]
        if cls in ('wheeled', 'ground', 'tracked') and own is not None and not defs.armed(defs.field(own, 'weapon')):
            roles = [r for r in roles if r[0] not in ('weapon', 'barrel', 'roof_mg')]
    missing = [n for n, pat in roles if not any(sp.role(pat).match(x) for x in names)]
    inside = [n for n in missing if cleared(n)]
    missing = [n for n in missing if n not in inside]
    out.append(('parts', not missing, ('missing ' + ', '.join(missing) if missing else f'{len(roles)} roles') +
                (f" (merged: {', '.join(f'{n} in {merged[n]}' for n in inside)})" if inside else '')))
    if own is not None and cls != 'obstacle':
        need, found, mz, mounts, flare, aps = sp.weapon_checks(defs, own, cls, names)
        # The flare points are Mount_Flare_L / _R / _TL / _TR (a bare Mount_Flare reads as a weapon pivot).
        flare = (sum(1 for x in names if FLARE.match(x)), flare[1])
        bad = mz + mounts + ([f'Mount_Flare {flare[0]}/{flare[1]}'] if flare[0] < flare[1] else []) + \
            (['Mount_APS'] if aps[0] < aps[1] else [])
        if cls == 'boss':
            bad += ['part ' + p for p in sp.boss_part_nodes(defs, own, names)]
        inside = [b for b in bad if cleared(b.split(' ')[0])]
        bad = [b for b in bad if b not in inside]
        out.append(('mounts', not bad, ('; '.join(bad) if bad else f'muzzles {found}/{need}') +
                    (f" (merged: {', '.join(inside)})" if inside else '')))
    size = rec['size']
    want = defs.field(own, 'modelSize') if own is not None else None
    if want and size[0] > 0.01:
        k = want[0] / size[0]
        errs = [abs(size[i] * k / want[i] - 1) for i in (1, 2) if want[i]]
        ok = max(errs or [0]) <= SIZE_TOL
        out.append(('size', ok, f"{'x'.join(f'{x:.1f}' for x in size)} vs modelSize {want} "
                    f"(w/h off {max(errs or [0]):.0%})"))
    sa, sb, partner = overlap.get(model, (0.0, 0.0, ''))
    original = bool(partner) and sa > SHARED_MAX and is_original(model, partner)
    out.append(('own_geometry', sa <= SHARED_MAX or original, f'{sa:.0%} of triangles shared' +
                (f' (most with {partner}' + (', which was made later from this one)' if original else ')')
                 if partner else '')))
    deg = rec['degenerateTriangles']
    out.append(('zero_area', deg == 0, f'{deg} zero-area triangles'))
    out.append(('color0', m['no_color'] == 0 and rec['color0'] is not None, f"{m['no_color']} meshes without COLOR_0"))
    zn = ZONES.get(cls, 3)
    out.append(('colour_zones', m['zones'] >= zn, f"{m['zones']} materials (need {zn})"))
    bake = m.get('c0_p95', 0) - m.get('c0_p05', 0) >= 0.15 and m.get('c0_wear', 0) >= 0.005
    if cls not in ('jet', 'helicopter', 'air_other') and not (cls == 'boss' and defs.field(own, 'flying')):
        bake = bake and m.get('c0_dust', 0) > 0.0
    out.append(('ao_dust_wear', bake, f"COLOR_0 p05 {m.get('c0_p05', 0):.2f} p95 {m.get('c0_p95', 0):.2f}, worn "
                f"{m.get('c0_wear', 0):.1%}, dust {m.get('c0_dust', 0):+.2f}"))
    out.append(('not_single_block', m['sloped_dirs'] >= 3, f"{m['sloped_dirs']} sloped face directions"))
    return out


# ----------------------------------------------------------------------------- the visual grades of pass 8
REBUILT = DOCS / 'rebuild'


def rebuilt():
    """Models rebuilt in prompt 35 (a folder in Docs/models/rebuild/): the pass 8 grades were of the old file."""
    return {p.name for p in REBUILT.iterdir() if p.is_dir()} if REBUILT.exists() else set()


def visual_grades():
    """{model: (visual grade, final grade)} from Docs/models/scan/visual_scores.md (not for a rebuilt model)."""
    out = {}
    if not VISUAL.exists():
        return out
    for line in VISUAL.read_text(encoding='utf-8').splitlines():
        cells = [c.strip() for c in line.split('|')]
        if len(cells) > 10 and cells[1].startswith('`'):
            out[cells[1].strip('`')] = (cells[6], cells[9])
    for m in rebuilt():
        out.pop(m, None)
    return out


# ----------------------------------------------------------------------------- driver
def scored_models(defs):
    return sp.model_owners(defs, MODELS)


def evaluate(ids=None, overlap=None, gold=None, quiet=False):
    balance = sp.load_balance()
    defs = sp.Defs(balance)
    owners = scored_models(defs)
    ids = ids or list(owners)
    for i in ids:
        owners.setdefault(i, [])
    overlap = overlap if overlap is not None else geometry_overlap(ids)
    gold = gold if gold is not None else load_gold()
    vis = visual_grades()
    rows = []
    for model in ids:
        path = MODELS / f'{model}.glb'
        if not path.exists():
            continue
        vs = owners.get(model, [])
        own = vs[0] if vs else None
        rec = glb_analyze.analyze(path)
        cls = sp.classify(defs, model, own, rec['nodeNames'])
        mesh = gm.load(path)
        m = metrics(mesh, structure=cls in ('tower', 'structure', 'hq'))
        hard = hard_checks(defs, model, own, cls, rec, m, overlap)
        gcls = gold_class(defs, model, own, cls, rec['nodeNames'])
        g = gold_for(gold, gcls)
        score, shares = soft_score(m, g) if g else (None, {})
        hard_ok = all(ok for _, ok, _ in hard)
        sg = grade(score) if score is not None else 'NA'
        v, final8 = vis.get(model, ('', ''))
        rows.append({
            'model': model, 'class': cls, 'gold_set': gold_key(gold, gcls), 'units': ' '.join(x['id'] for x in vs[:3]), 'triangles': rec['triangles'],
            'hard_pass': hard_ok, 'hard_fails': ' | '.join(f'{k}: {n}' for k, ok, n in hard if not ok),
            'soft_score': score, 'soft_grade': sg, 'gate': 'PASS' if hard_ok and sg == 'Tốt' else 'FAIL',
            'l8_visual': v, 'l8_final': final8, 'agent_visual': 'NA',
            'shared_all': overlap.get(model, (0, 0, ''))[0], 'shared_body': overlap.get(model, (0, 0, ''))[1],
            'shared_with': overlap.get(model, (0, 0, ''))[2],
            **{k: (round(x, 4) if isinstance(x, float) else x) for k, x in m.items()},
            **{f's_{k}': x for k, x in shares.items()},
        })
        if not quiet:
            r = rows[-1]
            print(f"{model:28s} {cls:10s} tris {r['triangles']:6d} soft {score} {sg:8s} hard "
                  f"{'ok' if hard_ok else 'FAIL: ' + r['hard_fails']}")
    return rows


def gold_key(gold, cls):
    """The gold set a class is scored against (its own, else the nearest class's; '' when none)."""
    seen = set()
    while cls and cls not in gold.get('classes', {}) and cls not in seen:
        seen.add(cls)
        cls = NEAREST.get(cls)
    return cls if cls in gold.get('classes', {}) else ''


def gold_for(gold, cls):
    return gold.get('classes', {}).get(gold_key(gold, cls))


def load_gold():
    return json.loads(GOLD_JSON.read_text(encoding='utf-8')) if GOLD_JSON.exists() else {}


KEYS = ('silhouette', 'edges', 'regions', 'parts_m2', 'tier2_m2', 'tier3_m2', 'asym_raw', 'sloped_dirs', 'zones')


def compute_gold(quiet=False):
    """Gold = the four V2 models + the top 10 % of each class: models the pass 8 scan graded Tốt visually
    ranked by the mean percentile of their soft metrics within the class (the soft score needs a gold to exist)."""
    balance = sp.load_balance()
    defs = sp.Defs(balance)
    owners = scored_models(defs)
    vis = visual_grades()
    raw = {}
    frames = {}
    # A borrowed model (REBUILD_LIST stand_in) is never gold: its density is another model's (wave 1 found the
    # ground boss gold made of fortress_bastion and behemoth_tempest, both stand-ins being rebuilt).
    borrowed = set()
    if (DOCS / 'rebuild_list.csv').exists():
        with (DOCS / 'rebuild_list.csv').open(encoding='utf-8') as fh:
            borrowed = {r['model'] for r in csv.DictReader(fh) if r.get('stand_in') == 'yes'}
    for model, vs in owners.items():
        rec = glb_analyze.analyze(MODELS / f'{model}.glb')
        own = vs[0] if vs else None
        cls = sp.classify(defs, model, own, rec['nodeNames'])
        raw[model] = (cls, metrics(gm.load(MODELS / f'{model}.glb')))
        if cls == 'boss' and own is not None:
            frames[model] = gold_class(defs, model, own, cls, rec['nodeNames'])
    classes = {}
    members = {}
    for cls in sorted({c for c, _ in raw.values()}):
        in_cls = [n for n, (c, _) in raw.items() if c == cls]
        good = [n for n in in_cls if vis.get(n, ('', ''))[0] == 'Tốt' and n not in borrowed]
        ranks = {}
        for key in ('silhouette', 'edges', 'regions', 'parts_m2', 'tier2_m2', 'tier3_m2'):
            vals = sorted(raw[n][1][key] for n in in_cls)
            for n in in_cls:
                ranks.setdefault(n, []).append(np.searchsorted(vals, raw[n][1][key]) / max(1, len(vals) - 1))
        top_n = max(1, int(math.ceil(TOP_SHARE * len(in_cls))))
        top = sorted(good, key=lambda n: -np.mean(ranks[n]))[:top_n]
        gold_set = sorted(set(top) | {n for n, c in GOLD_V2.items() if c == cls and n in raw})
        if not gold_set:
            continue
        members[cls] = gold_set
        classes[cls] = {k: round(float(np.mean([raw[n][1][k] for n in gold_set])), 4) for k in KEYS}
        classes[cls]['count'] = len(in_cls)
        if cls != 'boss':
            continue
        # Decision 5: the same rule inside each boss frame (a frame with no visual Tốt model and no V2 model uses the
        # whole boss gold through NEAREST).
        for fk in sorted(set(frames.values())):
            in_f = [n for n in in_cls if frames.get(n) == fk]
            good_f = [n for n in in_f if n in good]
            top_f = sorted(good_f, key=lambda n: -np.mean(ranks[n]))[:max(1, int(math.ceil(TOP_SHARE * len(in_f))))]
            set_f = sorted(set(top_f) | {n for n, c in GOLD_V2.items() if c == 'boss' and frames.get(n) == fk})
            if set_f:
                members[fk] = set_f
                classes[fk] = {k: round(float(np.mean([raw[n][1][k] for n in set_f])), 4) for k in KEYS}
                classes[fk]['count'] = len(in_f)
    gold = {'about': 'prompt 35 section 5.3: class means of the gold set (quality_gate.compute_gold)',
            'members': members, 'classes': classes,
            'v2': {n: {k: round(float(raw[n][1][k]), 4) for k in KEYS} for n in GOLD_V2 if n in raw}}
    GOLD_JSON.write_text(json.dumps(gold, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    write_gold_md(gold)
    return gold


def write_gold_md(gold):
    lines = ['# Gold metrics (prompt 35 section 5.3)', '',
             'Generated by `python Tools/assets/quality_gate.py --gold` (data: `Tools/assets/gold_metrics.json`). Gold =',
             'the four V2 models the owner approved in prompt 27 EXPERIMENT_1 (main_battle_tank, fighter_jet,',
             'attack_helicopter, silver_bug) plus the top 10 % of each class: models the pass 8 scan graded Tốt visually,',
             'ranked by the mean percentile of their soft metrics in the class. A class with no gold uses the nearest',
             "class's (`NEAREST` in quality_gate.py: " + ', '.join(f'{a} -> {b}' for a, b in NEAREST.items()) + ').',
             '', 'Metrics (glb_mesh pictures, every model drawn the same way):', '',
             '- silhouette: silhouette boundary / convex hull boundary, mean of side, front, top (256 px on the long side; 1 = convex);',
             '- edges: share of model pixels on a shading edge, battle view (28.4 px/m, pitch 52, yaw -45);',
             '- regions: brightness regions (12 levels, >= 6 px) per 1000 model pixels, battle view;',
             '- parts_m2: distinct connected pieces (repeats of one kit piece counted once) per m2 of surface (scaled to a 7 m vehicle);',
             '- tier2_m2 / tier3_m2: pieces 0.3 m .. 25 % of the length / under 0.3 m (scaled the same way) per m2;',
             '- asym_raw: 1 - IoU of the top view and its mirror (0 = perfectly symmetric);',
             '- sloped_dirs: sloped face directions on the hull / turret; zones: materials.', '',
             '| class | models in class | gold set | ' + ' | '.join(KEYS) + ' |',
             '|---|---|---|' + '---|' * len(KEYS)]
    for cls, g in gold['classes'].items():
        lines.append(f"| {cls} | {g['count']} | {', '.join(gold['members'][cls])} | " +
                     ' | '.join(f'{g[k]:.3f}' if isinstance(g[k], float) else str(g[k]) for k in KEYS) + ' |')
    lines += ['', '## The four V2 models', '', '| model | ' + ' | '.join(KEYS) + ' |', '|---|' + '---|' * len(KEYS)]
    for n, g in gold['v2'].items():
        lines.append(f'| {n} | ' + ' | '.join(f'{g[k]:.3f}' for k in KEYS) + ' |')
    GOLD_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def write_report(rows, merge=True):
    old = {}
    if merge and REPORT_CSV.exists():
        with REPORT_CSV.open(encoding='utf-8') as fh:
            old = {r['model']: r for r in csv.DictReader(fh)}
    for r in rows:
        old[r['model']] = r
    allrows = [old[k] for k in sorted(old)]
    fields = []
    for r in allrows:
        for k in r:
            if k not in fields:
                fields.append(k)
    with REPORT_CSV.open('w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(allrows)
    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = 'quality'
        ws.append(fields)
        for r in allrows:
            ws.append([r.get(k, '') if not isinstance(r.get(k), bool) else str(r.get(k)) for k in fields])
        ws.freeze_panes = 'B2'
        wb.save(REPORT_XLSX)
    except ImportError:
        pass


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--ids', help='comma-separated model ids (default: every scored model)')
    ap.add_argument('--gold', action='store_true', help='recompute the gold metrics first')
    ap.add_argument('--no-write', action='store_true')
    args = ap.parse_args()
    if args.gold or not GOLD_JSON.exists():
        compute_gold()
    ids = [x for x in (args.ids or '').split(',') if x] or None
    rows = evaluate(ids)
    if not args.no_write:
        write_report(rows, merge=bool(ids))
    fails = sum(1 for r in rows if r['gate'] != 'PASS')
    print(f'{len(rows)} models, {len(rows) - fails} pass, {fails} not yet')


if __name__ == '__main__':
    main()
