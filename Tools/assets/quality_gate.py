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
# Prompt 35 gold recalibration (lane A, the lead's review of the first recompute): mixed classes are split into gold
# sets of like models (gold_class), the key is '<class>_<set>'. A set without gold, or a sole member scored
# leave-one-out, borrows a SIMILAR set first, then its parent class, then NEAREST.
SIMILAR = {
    'wheeled_light': 'wheeled_heavy', 'wheeled_heavy': 'tracked_heavy',
    'tracked_light': 'tracked_heavy', 'tracked_heavy': 'tracked_light',
    'jet_drone': 'jet_fighter', 'jet_fighter': 'jet_heavy', 'jet_heavy': 'jet_fighter',
    'helicopter_light': 'helicopter_heavy', 'helicopter_heavy': 'helicopter_light', 'air_other': 'helicopter_heavy',
    'obstacle_flat': 'obstacle_wall', 'obstacle_wall': 'obstacle_flat', 'obstacle_pad': 'obstacle_flat',
    'obstacle_tall': 'tower_mast',
    'tower_mast': 'tower_small', 'tower_small': 'tower_big', 'tower_big': 'structure',
    'structure': 'tower_big', 'hq': 'tower_big',
    'ground': 'ship', 'ship': 'boss_sea', 'boss_sea': 'ship', 'boss_air': 'jet_heavy',
}
GOLD_PARENT = {k: k.split('_')[0] for k in SIMILAR if k.split('_')[0] in ('wheeled', 'tracked', 'jet', 'helicopter',
                                                                            'obstacle', 'tower')}
GOLD_PARENT.update({f'boss_{f}': 'boss' for f in BOSS_FRAMES})
# Widening (the anchor rule): top 10 % of the set, then 20 %, 25 %, then down to the candidates' median.
WIDEN = (0.10, 0.20, 0.25, 'median')
ANCHOR = 80.0
# Owner decision 6: units seen in numbers (technicals, light vehicles, towers) stay under 1.5 x the class maximum; a
# hard gate for these budget classes only (over-budget stays information for the others).
NUMBERS_CAP = {'light': 1.5, 'tower': 1.5}
# Play-test 14 wave M6: the hangars (drone, vehicle, aircraft and their branches) stand once in a base, never in
# numbers, so the towers' numbers cap does not apply to them (the class budget stays information, as for structures).
NOT_IN_NUMBERS = re.compile(r'hangar', re.I)
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


def def_frame(defs, own):
    """scan_prep's frame (air / ship / ground), with a fixed-wing boss read as air even when the def leaves
    'flying' out (wave 5: Morrigan has fixedWing but no flying field, so it was asked for tracks)."""
    f = sp.boss_frame(defs, own)
    return 'air' if f == 'ground' and defs.field(own, 'fixedWing') else f


def boss_frame(defs, own, names):
    """ground / rail / air / sea (decision 5): air and sea from the def, rail from the running gear's nodes."""
    f = def_frame(defs, own)
    if f == 'ship':
        return 'sea'
    if f == 'ground' and any(RAIL_NODE.match(n) for n in names):
        return 'rail'
    return f


def gold_class(defs, model, own, cls, names, dims=None):
    """The key of the gold set a model is scored against. dims = (length, height) in m (the longer of x / z, y).
    Splits (prompt 35 gold recalibration): wheeled light (< 5.5 m: jeeps, technicals, cars, scouts) / heavy (trucks,
    launchers, howitzers); tracked light (< 6 m: carriers, IFVs) / heavy; jet drone (drone / uav) / fighter (< 12 m) /
    heavy (bombers, gunships, tanker); helicopter light (< 5 m) / heavy; obstacle wall / pad (helipads) / tall (3 m and
    up: nets) / flat (minefields, dragon's teeth); tower mast (<= 5.5 m long and 1.4 x as tall) / small (<= 5.5 m:
    bunkers, turrets) / big (emplacements, shelters, hangars, batteries)."""
    if cls == 'boss':
        return f'boss_{boss_frame(defs, own, names)}' if own is not None else cls
    if dims is None:
        return cls
    length, height = dims
    if cls == 'wheeled':
        return 'wheeled_light' if length < 5.5 else 'wheeled_heavy'
    if cls == 'tracked':
        return 'tracked_light' if length < 6.0 else 'tracked_heavy'
    if cls == 'jet':
        drone = re.search(r'drone|uav', model) or (own is not None and defs.field(own, 'drone'))
        return 'jet_drone' if drone else 'jet_fighter' if length < 12 else 'jet_heavy'
    if cls == 'helicopter':
        return 'helicopter_light' if length < 5 else 'helicopter_heavy'
    if cls == 'obstacle':
        if re.match(r'(wall_|blast_wall)', model) or (own is not None and defs.field(own, 'wall')):
            return 'obstacle_wall'
        if 'helipad' in model:
            return 'obstacle_pad'
        return 'obstacle_tall' if height >= 3.0 else 'obstacle_flat'
    if cls == 'tower':
        if length <= 5.5:
            return 'tower_mast' if height >= 1.4 * length else 'tower_small'
        return 'tower_big'
    return cls


def mesh_dims(mesh):
    lo, hi = mesh.bounds()
    d = hi - lo
    return float(max(d[0], d[2])), float(d[1])
FLARE = re.compile(r'^Mount_flare(_[a-z]+)?(\.\d+)?$', re.I)
FAMILY_SUFFIX = re.compile(r'(_hd|_a|_b|_chute|_wreck|_deployed|_dug|_dugin|_open|_mk\d|_old|_lod\d)$')
# Kit component pieces (frontier_kit, mb_parts27, mb_kit35 names): allowed to repeat across models.
KIT_PIECE = re.compile(r'^(Tyres?|Wheels?|Hubs?|Wheel_bolts|Wheel_nuts|Sprockets?|Idlers?|Tracks?|Track_links|Hatch(es)?|'
                       r'Hatch_fittings|MG|MG_\w+|Smoke\w*|Antennas?|Rotor_\w+|Tail_rotor\w*|Nozzle\w*|Exhaust\w*|'
                       r'Missiles?|Missile_\w+|Pods?|Pod_\w+|Bolts|Rivets|Welds|Lamps|Lamp_\w+|Grilles?|Handles|Hinges|'
                       r'Kit_\w+|Rails?|Railings|Ladders?|Sandbags?|Glass|Cab_glass)(\.\d+)?$', re.I)
# Prompt 35 (lane A, wave 9's request): wheels never count as shared geometry, in the whole-model share either (the
# gate's own_geometry): a kit tyre (tread_wheel, lugged_tyre) with the same arguments in two small vehicles is not a
# copied model. Their triangles stay in the model's total as its own.
KIT_WHEEL = re.compile(r'^(Tyres?|Tires?|Wheels?|Wheel_\w+|Hubs?|Rims?|Road_?wheels?|Lug_nuts|Tyre_\w+)(\.\d+)?$', re.I)


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
        a1, n1 = gm.triangle_hashes(m, skip=lambda p: KIT_WHEEL.match(p.node))
        a2, n2 = gm.triangle_hashes(m, skip=lambda p: KIT_PIECE.match(p.node))
        wheels = sum(len(p.tris) for p in m.pieces if len(p.tris) >= 12 and KIT_WHEEL.match(p.node))
        keys_all[n] = (np.unique(a1), np.unique(n1), len(a1))
        keys_body[n] = (a2, n2, a1, n1, wheels)
    fams = {n: family(n) for n in keys_all}
    out = {}
    counts_abs = _counts([keys_all[n][0] for n in keys_all], [fams[n] for n in keys_all])
    counts_norm = _counts([keys_all[n][1] for n in keys_all], [fams[n] for n in keys_all])
    for n in names:
        if n not in keys_body:
            continue
        ab, nbk, aa, na, wheels = keys_body[n]
        res = []
        for ak, nk, own in ((aa, na, wheels), (ab, nbk, 0)):
            if not len(ak):
                res.append(0.0)
                continue
            ca = _lookup(counts_abs, ak)
            cn = _lookup(counts_norm, nk)
            shared = ((ca >= 2) & (ca <= ubiquitous)) | ((cn >= 2) & (cn <= ubiquitous))
            res.append(float(shared.sum()) / (len(shared) + own))
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


def _base_slab(model):
    """ids of the pieces that make a structure's base slab (prompt 35 lane A, wave 7's request): flat (at most
    0.6 m or 8 % of the model's height thick), on the model's floor (bottom within 0.15 m of it) and covering at
    least half the model's top-view bounding box. Empty when the model has none."""
    lo, hi = model.bounds()
    height = hi[1] - lo[1]
    box = (hi[0] - lo[0]) * (hi[2] - lo[2])
    out = set()
    for p in model.pieces:
        if not len(p.tris):
            continue
        a, b = p.pos.min(axis=0), p.pos.max(axis=0)
        if b[1] - a[1] <= max(0.6, 0.08 * height) and a[1] - lo[1] <= 0.15 and (b[0] - a[0]) * (b[2] - a[2]) >= 0.5 * box:
            out.add(id(p))
    return out


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
    px_top = 256 / max(float(max(model.bounds()[1] - model.bounds()[0])), 1e-3)

    def _asym(keep=None):
        top, _ = gm.render(model, 'top', px=px_top, mask_only=True, keep=keep)
        inter = (top & top[:, ::-1]).sum()
        union = (top | top[:, ::-1]).sum()
        return float(1 - inter / union) if union else 0.0
    out['asym_raw'] = _asym()
    # Prompt 35 (lane A, wave 7's request): a structure is also read without its base slab (a square or octagonal
    # slab made a post read as symmetric); the score takes the better of the two readings, as sloped_dirs does.
    slab = _base_slab(model) if structure else set()
    if slab and any(len(p.tris) and id(p) not in slab for p in model.pieces):
        out['asym_noslab'] = _asym(lambda p: id(p) not in slab)
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
            lo_a = min(0.01, 0.8 * (gold.get('asym_raw') or 0))
            s = 1.0 if any(lo_a <= a <= 0.35 for a in (m['asym_raw'], m.get('asym_noslab', m['asym_raw']))) else 0.5
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
def systems_absent(defs, own):
    """Part roles the unit's def has no system for (wave 5, the lead's call on lane C's request): flare dispensers
    without flareCharges, a canopy on a drone, a roof machine gun without an 'mg' weapon, smoke launchers without a
    smoke system in the data, a turret and mantlet when the main gun is laid by the hull (mainAim Hull). A model may
    still carry the part; the gate just does not ask for it."""
    f = defs.field
    out = set()
    if not (f(own, 'flareCharges') or f(own, 'flares')):
        out.add('flares')
    if f(own, 'drone'):
        out.add('canopy')
    slots = [s.get('slot') for s in (f(own, 'secondary') or []) if isinstance(s, dict) and defs.armed(s.get('weapon'))]
    if 'mg' not in slots and (f(own, 'mainSlot') or 'main') != 'mg':
        out.add('roof_mg')
    if not any(f(own, k) for k in ('smoke', 'smokeCharges', 'smokeScreen')):
        out.add('smoke')
    if f(own, 'mainAim') == 'Hull':
        out.update(('turret', 'mantlet'))
    return out


def hard_checks(defs, model, own, cls, rec, m, overlap):
    """[(gate, ok, note)] for one model."""
    names = rec['nodeNames']
    bcls = sp.budget_class(defs, cls, own)
    lo, hi = sp.BUDGET[bcls]
    tris = rec['triangles']
    cap = NUMBERS_CAP.get(bcls)
    if cap and (NOT_IN_NUMBERS.search(model) or (own is not None and NOT_IN_NUMBERS.search(own.get('id', '')))):
        cap = None
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
        frame = def_frame(defs, own)
        roles = [sp.BOSS_ROLES['body'], sp.BOSS_ROLES['weapons'], sp.BOSS_ROLES[frame]]
    else:
        roles = list(sp.ROLES.get(cls, []))
        if cls == 'tracked' and own is not None and not defs.field(own, 'turretTurnRate'):
            roles = [r for r in roles if r[0] not in ('turret', 'mantlet')]
        if own is not None:
            absent = systems_absent(defs, own)
            roles = [r for r in roles if r[0] not in absent]
        if cls in ('wheeled', 'ground', 'tracked') and own is not None and not defs.armed(defs.field(own, 'weapon')):
            roles = [r for r in roles if r[0] not in ('weapon', 'barrel', 'roof_mg')]
        if cls == 'helicopter':
            # Prompt 35 (lane A, lane B's request): a tandem (Rotor_rear aft) has no tail rotor; an unarmed transport
            # (no armed main or secondary weapon) has no weapons and needs no stub wings to carry them.
            if any(re.match(r'^Rotor_rear(?:$|[._0-9])', x, re.I) for x in names):
                roles = [r for r in roles if r[0] != 'tail_rotor']
            if own is not None and not defs.armed(defs.field(own, 'weapon')) and not any(
                    isinstance(x, dict) and defs.armed(x.get('weapon')) for x in (defs.field(own, 'secondary') or [])):
                roles = [r for r in roles if r[0] not in ('weapons', 'stub_wings')]
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
    if cls not in ('jet', 'helicopter', 'air_other') and not (cls == 'boss' and def_frame(defs, own) == 'air'):
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
        gcls = gold_class(defs, model, own, cls, rec['nodeNames'], mesh_dims(mesh))
        gset, g = gold_for_model(gold, gcls, model)
        score, shares = soft_score(m, g) if g else (None, {})
        hard_ok = all(ok for _, ok, _ in hard)
        sg = grade(score) if score is not None else 'NA'
        v, final8 = vis.get(model, ('', ''))
        rows.append({
            'model': model, 'class': cls, 'gold_set': gset, '_gold_class': gcls, 'units': ' '.join(x['id'] for x in vs[:3]), 'triangles': rec['triangles'],
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


def fallback_chain(key):
    """The sets a gold key is scored against, in order: its own, a SIMILAR set, the parent class, then NEAREST."""
    out = [key]
    if SIMILAR.get(key):
        out.append(SIMILAR[key])
    nxt = GOLD_PARENT.get(key, key)
    while nxt and nxt not in out[2:]:
        out.append(nxt)
        nxt = NEAREST.get(nxt)
    return list(dict.fromkeys(k for k in out if k))


def gold_key(gold, cls):
    """The gold set a class is scored against (the first of fallback_chain with a gold; '' when none)."""
    return next((k for k in fallback_chain(cls) if k in gold.get('classes', {})), '') if cls else ''


def gold_for(gold, cls):
    return gold.get('classes', {}).get(gold_key(gold, cls))


def gold_for_model(gold, cls, model):
    """(set label, gold means) a model is scored against. Leave-one-out (prompt 35, lane A): a gold member is scored
    against the mean of the other members of its set; a sole member against the next class's gold (NEAREST)."""
    mm = gold.get('member_metrics', {})
    for key in fallback_chain(cls) if cls else []:
        if key not in gold.get('classes', {}):
            continue
        mem = gold.get('members', {}).get(key, [])
        if model not in mem or not mm:
            return key, gold['classes'][key]
        others = [n for n in mem if n != model and n in mm]
        if others:
            return f'{key} (LOO)', {k: float(np.median([mm[n][k] for n in others])) for k in KEYS}
    key = gold_key(gold, cls)       # no other gold anywhere: the own set, self included
    return key, gold.get('classes', {}).get(key)


def load_gold():
    return json.loads(GOLD_JSON.read_text(encoding='utf-8')) if GOLD_JSON.exists() else {}


KEYS = ('silhouette', 'edges', 'regions', 'parts_m2', 'tier2_m2', 'tier3_m2', 'asym_raw', 'sloped_dirs', 'zones')


GOLD_ROUNDS = 8


def compute_gold(quiet=False, overlap=None):
    """Gold per gold set (gold_class: split classes and boss frames; _gold_set has the rule): the V2 models in the
    set + the top 10 % of its candidates, dense outliers left out, widened to 20 / 25 % / the candidates' median until
    every member and V2 model scores ANCHOR leave-one-out; the set value is the median of its members. Candidates
    (owner, prompt 35 section 8 item 1): pass 8 visual Tốt models (not rebuilt since) and rebuilt models that pass
    every hard gate with soft >= 80 against the previous gold. No circularity: candidacy is judged against the previous
    gold, every gold member is scored leave-one-out (gold_for_model), and the recompute repeats until the gold
    reproduces itself (a two-round swap is settled by the union of the swapping rounds' candidates); a second `--gold`
    run gives the same members."""
    if overlap is None:
        overlap = geometry_overlap(list(scored_models(sp.Defs(sp.load_balance()))))
    prev = load_gold()
    seen = []                       # (members, gate candidates) of each round
    settled = 'fixed point'
    for rnd in range(1, GOLD_ROUNDS + 1):
        rows = evaluate(None, overlap=overlap, gold=prev, quiet=True)
        gold = _select_gold(rows)
        done = gold['members'] == prev.get('members')
        if not quiet:
            print(f"gold round {rnd}: {sum(len(v) for v in gold['members'].values())} places in "
                  f"{len(gold['members'])} sets; candidates {gold['candidates']['count']}"
                  f"{' (fixed point)' if done else ''}")
        if done:
            break
        past = [m for m, _ in seen]
        if gold['members'] in past:
            # A cycle: a sole member of a small class is scored against the nearest class (leave-one-out) and drops
            # out, its rival wins, and the two swap each round. Settle it with the union of the cycle's gate
            # candidates: each passed against a gold without itself in some round; the class ranking then picks.
            first = past.index(gold['members'])
            union = set(gold['candidates']['gate'])
            for _, c in seen[first:]:
                union |= set(c)
            gold = _select_gold(rows, extra=union)
            settled = f'cycle settled by the union of the candidates of rounds {first + 1}-{rnd}'
            if not quiet:
                print(f'gold: {settled}')
            break
        seen.append((gold['members'], gold['candidates']['gate']))
        prev = gold
    else:
        settled = f'stopped after {GOLD_ROUNDS} rounds'
    gold['rounds'] = rnd
    gold['settled'] = settled
    GOLD_JSON.write_text(json.dumps(gold, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    write_gold_md(gold)
    return gold


DENSE = ('edges', 'regions', 'parts_m2', 'tier2_m2', 'tier3_m2')


def _outliers(names, raw):
    """Candidates far denser than the rest on some metric (never allowed to define a set alone): above Q3 + 1.5 IQR
    with four or more candidates, above 2 x the median of the other two with three (two cannot tell which is odd)."""
    out = set()
    if len(names) < 3:
        return out
    for k in DENSE:
        vals = {n: raw[n][1][k] for n in names}
        if len(names) >= 4:
            q1, q3 = np.percentile(list(vals.values()), [25, 75])
            out |= {n for n, v in vals.items() if v > q3 + 1.5 * (q3 - q1)}
        else:
            for n, v in vals.items():
                rest = [x for m, x in vals.items() if m != n]
                if v > 2 * float(np.median(rest)) > 0:
                    out.add(n)
    return out


def _anchor_fails(mem, raw, full):
    """Members (V2 included) that score under ANCHOR against the median of the other members (leave-one-out)."""
    if len(mem) < 2:
        return []
    bad = []
    for n in mem:
        g = {k: float(np.median([raw[o][1][k] for o in mem if o != n])) for k in KEYS}
        if soft_score(full[n], g)[0] < ANCHOR:
            bad.append(n)
    return bad


def _gold_set(key, names, candidates, raw, full):
    """(members, note) of one gold set: the V2 models in it plus the top share of its candidates by mean density
    percentile (at least two when two exist), widened (WIDEN) until every member and V2 model scores ANCHOR
    leave-one-out; dense outliers are left out. None when the set has no candidate and no V2 model."""
    v2 = sorted(n for n in names if n in GOLD_V2)
    cands = [n for n in names if n in candidates and n not in v2]
    odd = _outliers(cands, raw)
    pool = [n for n in cands if n not in odd]
    if not pool and not v2:
        return None
    ranks = {}
    for k in ('silhouette',) + DENSE:
        vals = sorted(raw[n][1][k] for n in names)
        for n in names:
            ranks.setdefault(n, []).append(np.searchsorted(vals, raw[n][1][k]) / max(1, len(vals) - 1))
    ranked = sorted(pool, key=lambda n: (-np.mean(ranks[n]), n))
    mem, bad, rung, prev_n = [], [], None, 0
    for rung in WIDEN:
        n_top = int(math.ceil(len(ranked) / 2)) if rung == 'median' else int(math.ceil(rung * len(names)))
        n_top = max(n_top, min(len(ranked), 2 - len(v2)), 1 if ranked else 0, prev_n)
        prev_n = n_top
        mem = sorted(set(ranked[:n_top]) | set(v2))
        bad = _anchor_fails(mem, raw, full)
        if not bad:
            break
    dropped = []
    while bad and any(n not in v2 for n in bad):
        # Widest rung and still under: a candidate that cannot meet its own set's bar does not stand for it (the
        # weakest goes first); a V2 model always stays.
        worst = min((n for n in bad if n not in v2), key=lambda n: (np.mean(ranks[n]), n))
        dropped.append(worst)
        mem = [n for n in mem if n != worst]
        bad = _anchor_fails(mem, raw, full)
    note = f"{'top ' + str(int(rung * 100)) + ' %' if rung != 'median' else 'down to the median'} of {len(cands)} candidates"
    if odd:
        note += '; outliers left out: ' + ', '.join(sorted(odd))
    if dropped:
        note += '; under the anchor, left out: ' + ', '.join(dropped)
    if len(mem) == 1:
        note += '; sole member'
    if bad:
        note += '; under the anchor at the widest: ' + ', '.join(bad)
    return mem, note


def _select_gold(rows, extra=()):
    """One gold from one gate run (rows scored against the previous gold); `extra`: more gate candidates."""
    vis = visual_grades()
    reb = rebuilt()
    # A borrowed model (REBUILD_LIST stand_in) is never gold: its density is another model's (wave 1 found the
    # ground boss gold made of fortress_bastion and behemoth_tempest, both stand-ins being rebuilt). A stand-in that
    # was rebuilt has its own geometry now (the own_geometry hard gate checks it) and is a candidate like any other.
    borrowed = set()
    if (DOCS / 'rebuild_list.csv').exists():
        with (DOCS / 'rebuild_list.csv').open(encoding='utf-8') as fh:
            borrowed = {r['model'] for r in csv.DictReader(fh) if r.get('stand_in') == 'yes'} - reb
    raw = {r['model']: (r['class'], {k: float(r[k]) for k in KEYS}) for r in rows}
    full = {r['model']: r for r in rows}
    by_visual = {n for n in raw if vis.get(n, ('', ''))[0] == 'Tốt'}
    by_gate = {r['model'] for r in rows if r['model'] in reb and r['hard_pass'] and r['soft_score'] is not None
               and r['soft_score'] >= 80} | set(extra)
    candidates = (by_visual | by_gate) - borrowed
    sets = {}
    for r in rows:
        sets.setdefault(r['_gold_class'], []).append(r['model'])
        if r['_gold_class'] != r['class']:
            sets.setdefault(r['class'], []).append(r['model'])      # the parent class: the last fallback
    classes, members, notes = {}, {}, {}
    for key in sorted(sets):
        got = _gold_set(key, sets[key], candidates, raw, full)
        if got is None:
            continue
        members[key], notes[key] = got
        classes[key] = {k: round(float(np.median([raw[n][1][k] for n in members[key]])), 4) for k in KEYS}
        classes[key]['count'] = len(sets[key])
    in_gold = sorted({n for v in members.values() for n in v})
    gold = {'about': 'prompt 35 section 5.3: class means of the gold set (quality_gate.compute_gold)',
            'rule': 'V2 + top 10 % per gold set (split classes, boss frames) of: visual Tốt (pass 8, not rebuilt) or '
                    'rebuilt with every hard gate and soft >= 80 against the previous gold; outliers out; widened '
                    '20 / 25 % / median until every member and V2 scores 80 leave-one-out; set value = median of '
                    'the members; repeated to a fixed point',
            'members': members, 'classes': classes, 'notes': notes,
            'member_metrics': {n: {k: round(raw[n][1][k], 4) for k in KEYS} for n in in_gold},
            'candidates': {'count': len(candidates), 'visual': sorted(by_visual - borrowed),
                           'gate': sorted(by_gate - borrowed)},
            'v2': {n: {k: round(float(raw[n][1][k]), 4) for k in KEYS} for n in GOLD_V2 if n in raw}}
    return gold


def write_gold_md(gold):
    lines = ['# Gold metrics (prompt 35 section 5.3)', '',
             'Generated by `python Tools/assets/quality_gate.py --gold` (data: `Tools/assets/gold_metrics.json`). Gold =',
             'the four V2 models the owner approved in prompt 27 EXPERIMENT_1 (main_battle_tank, fighter_jet,',
             'attack_helicopter, silver_bug) plus, per gold set, the top 10 % of its candidates ranked by the mean',
             'percentile of their soft metrics in the set. Candidates (owner, prompt 35 section 8 item 1): models the pass 8',
             'scan graded Tốt visually (not rebuilt since), and rebuilt models that pass every hard gate with soft >= 80',
             'against the previous gold. The set value of each metric is the median of its members.', '',
             'Gold sets (prompt 35 recalibration, `gold_class`): boss by frame (ground, rail, air, sea); wheeled light',
             '(< 5.5 m) / heavy; tracked light (< 6 m) / heavy; jet drone / fighter (< 12 m) / heavy; helicopter light',
             '(< 5 m) / heavy; obstacle wall / pad (helipads) / tall (>= 3 m: nets) / flat (minefields, dragon teeth);',
             'tower mast (<= 5.5 m long, 1.4 x as tall) / small (<= 5.5 m) / big; the parent classes are computed too, as',
             'the last fallback. Anchor: every member and every V2 model must score >= 80 against its own set',
             'leave-one-out; a set that fails is widened to the top 20 %, 25 %, then down to the candidates median; at',
             'the widest a non-V2 member still under 80 is left out. Dense outliers (above Q3 + 1.5 IQR of the set',
             'candidates on edges, regions, parts or tiers; above 2 x the other two with three candidates) never stand',
             'for gold. A set without gold, or a sole member, borrows a similar set, then its parent, then NEAREST:',
             ', '.join(f'{a} -> {b}' for a, b in SIMILAR.items()) + '.',
             '', 'No circularity: a gold member is scored leave-one-out (the median of the other members of its set; a',
             "sole member against the next set with gold; the report's gold_set column says `(LOO)`). The recompute",
             'repeats until the gold reproduces itself; a two-round swap is settled by the union of the swapping rounds',
             'candidates, the set ranking then picks.',
             f"This gold: {sum(len(v) for v in gold['members'].values())} places in {len(gold['members'])} sets, "
             f"{len(gold.get('candidates', {}).get('gate', []))} gate candidates and "
             f"{len(gold.get('candidates', {}).get('visual', []))} visual ones; {gold.get('rounds', '?')} rounds, "
             f"{gold.get('settled', '')}.",
             '', 'Metrics (glb_mesh pictures, every model drawn the same way):', '',
             '- silhouette: silhouette boundary / convex hull boundary, mean of side, front, top (256 px on the long side; 1 = convex);',
             '- edges: share of model pixels on a shading edge, battle view (28.4 px/m, pitch 52, yaw -45);',
             '- regions: brightness regions (12 levels, >= 6 px) per 1000 model pixels, battle view;',
             '- parts_m2: distinct connected pieces (repeats of one kit piece counted once) per m2 of surface (scaled to a 7 m vehicle);',
             '- tier2_m2 / tier3_m2: pieces 0.3 m .. 25 % of the length / under 0.3 m (scaled the same way) per m2;',
             '- asym_raw: 1 - IoU of the top view and its mirror (0 = perfectly symmetric);',
             '- sloped_dirs: sloped face directions on the hull / turret; zones: materials.', '',
             '| set | models in set | gold set | how chosen | ' + ' | '.join(KEYS) + ' |',
             '|---|---|---|---|' + '---|' * len(KEYS)]
    for cls, g in gold['classes'].items():
        lines.append(f"| {cls} | {g['count']} | {', '.join(gold['members'][cls])} | {gold.get('notes', {}).get(cls, '')} | " +
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
        old[r['model']] = {k: x for k, x in r.items() if not k.startswith('_')}
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
    ids = [x for x in (args.ids or '').split(',') if x] or None
    overlap = None
    if args.gold or not GOLD_JSON.exists():
        overlap = geometry_overlap(list(scored_models(sp.Defs(sp.load_balance()))))
        compute_gold(overlap=overlap)
    rows = evaluate(ids, overlap=overlap if ids is None else None)
    if not args.no_write:
        write_report(rows, merge=bool(ids))
    fails = sum(1 for r in rows if r['gate'] != 'PASS')
    print(f'{len(rows)} models, {len(rows) - fails} pass, {fails} not yet')


if __name__ == '__main__':
    main()
