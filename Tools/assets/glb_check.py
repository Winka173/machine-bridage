"""Prompt 27 step 2: the GLB baseline and machine validator (static: reads the exported files only).

    python Tools/assets/glb_check.py                       # analyse + validate every model, write the baseline
    python Tools/assets/glb_check.py --compare             # compare the current files with the committed baseline
    python Tools/assets/glb_check.py --only main_battle_tank fighter_jet     # print some rows, write nothing
    python Tools/assets/glb_check.py --accept main_battle_tank --reason "turret redesigned"   # intentional update

Writes Tools/assets/baseline.json (every GLB: stats, category, flags) and Docs/models/BASELINE.md (summary).
Rules: hard errors only where the prompt gives no numeric budget (DECISIONS "27 step 0 + baseline"). Budgets per
category and tier come with the budgets document (27 order step 5) and plug into BUDGETS below.
Exit code 1 when any model has an error (so a build script can stop on it).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'Tools' / 'balance'))
import glb_analyze  # noqa: E402
from jsonc_edit import loads as load_jsonc  # noqa: E402

MODELS = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Models'
BALANCE = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data' / 'balance.json'
BASELINE = HERE / 'baseline.json'
SUMMARY = ROOT / 'Docs' / 'models' / 'BASELINE.md'

# The controlled experiment's models (DECISIONS "27 order" step 3; the complex unit: STEP0_AUDIT.md).
EXPERIMENT = {'main_battle_tank': 'MBT', 'fighter_jet': 'Su-27', 'silver_bug': 'Icarus', 'attack_helicopter': 'complex unit'}

# Per-category budgets {category: {metric: max}}. Empty until the budgets document: no budget rule fires.
BUDGETS: dict[str, dict[str, float]] = {}

SIZE_TOLERANCE = 0.25        # proportions (width/length, height/length) against balance.json modelSize
LENGTH_TOLERANCE = 0.25      # absolute length: only reported (the view fits the length to modelSize at runtime)
DEGENERATE_ERROR = 0.005     # share of a model's triangles below 1e-8 m^2 that makes an error; fewer: a warning
REGRESSION = 0.10            # --compare: a change above 10 % in a counted metric is flagged
DARK, BRIGHT = 0.15, 0.95    # COLOR_0 mean luminance outside this band: suspicious
SCENERY = re.compile(r'^(birch|bush|pine|snow_pine|tree_|rock_|mountain_|debris_|rubble_|wreck_|dragons_teeth|minefield|'
                     r'mine$|supply_crate|repair_crate)')


def load_balance():
    return load_jsonc(BALANCE.read_text(encoding='utf-8'))


def resolve(vehicles):
    """Each vehicle with its model name and parts resolved through variantOf (Catalog's inheritance, simplified)."""
    by_id = {v['id']: v for v in vehicles}

    def field(v, key, depth=0):
        if key in v or depth > 8:
            return v.get(key)
        parent = by_id.get(v.get('variantOf') or v.get('inherits') or '')
        return field(parent, key, depth + 1) if parent else None

    out = []
    for v in vehicles:
        parent = by_id.get(v.get('variantOf') or '')
        model = v.get('model') or (field(parent, 'model') or parent['id'] if parent else v['id'])
        out.append({
            'id': v['id'], 'model': model, 'boss': bool(field(v, 'boss')), 'flying': bool(field(v, 'flying')),
            'speed': field(v, 'speed'), 'class': field(v, 'class'), 'modelSize': v.get('modelSize'),
            'parts': field(v, 'parts') or [], 'variant': bool(parent),
        })
    return out


def categorise(names, balance, units):
    cat = {}
    for u in units:
        m = u['model']
        if u['boss']:
            kind = 'boss'
        elif u['flying']:
            kind = 'air'
        elif u['speed'] in (0, None) or u['class'] == 'Defense':
            kind = 'structure'
        else:
            kind = 'ground'
        # A model drawn for several defs: its own def (id == model) decides, else the first def that draws it.
        if m not in cat or u['id'] == m:
            cat[m] = kind
    for p in balance.get('props', []):
        cat.setdefault(p['id'], 'prop')
    for w in balance.get('weapons', []):
        if w.get('projectileModel'):
            cat.setdefault(w['projectileModel'], 'munition')
    for s in balance.get('supports', []):
        cat.setdefault(s['id'], 'munition')
    result = {}
    for n in names:
        base = n[:-3] if n.endswith('_hd') else n
        if base in cat:
            result[n] = cat[base]
        elif base.endswith('_wreck'):
            result[n] = 'wreck'
        elif re.sub(r'_[ab]$', '', base) in cat and cat[re.sub(r'_[ab]$', '', base)] in ('structure', 'prop'):
            result[n] = 'structure'  # tower branches (<tower>_a / _b)
        elif re.search(r'_(tower|turret|bunker|battery|emplacement|hangar|relay|pad)(_[ab])?$', base) or \
                base.startswith(('helipad', 'c_ram', 'gun_pit', 'flak_tower')):
            result[n] = 'structure'
        elif SCENERY.match(base):
            result[n] = 'scenery'
        else:
            result[n] = 'unlisted'  # not named in balance.json (C#-only models, stand-ins, spares)
    return result


def validate(rec, category, units_by_model, hd_twin):
    errors, warnings = [], []
    errors += rec.get('problems', [])
    if rec['triangles'] == 0:
        errors.append('no triangles')
    if rec['nonFiniteValues']:
        errors.append(f"{rec['nonFiniteValues']} NaN/Infinity values")
    missing = rec['primitivesMissing']
    if missing['COLOR_0']:
        errors.append(f"COLOR_0 missing on {missing['COLOR_0']} of {rec['submeshes']} primitives")
    if missing['NORMAL']:
        errors.append(f"NORMAL missing on {missing['NORMAL']} primitives")
    if missing['TEXCOORD_0']:
        warnings.append(f"TEXCOORD_0 missing on {missing['TEXCOORD_0']} primitives")
    if rec['degenerateTriangles']:
        share = rec['degenerateTriangles'] / max(1, rec['triangles'])
        msg = f"{rec['degenerateTriangles']} zero-area triangles ({share:.2%})"
        (errors if share > DEGENERATE_ERROR else warnings).append(msg)
    c0 = rec.get('color0')
    if c0:
        if c0['outOfRange']:
            errors.append(f"COLOR_0 outside 0-1 on {c0['outOfRange']} vertices")
        if c0['mean'] < DARK or c0['mean'] > BRIGHT:
            warnings.append(f"COLOR_0 mean luminance {c0['mean']} (suspiciously {'dark' if c0['mean'] < DARK else 'bright'})")
    if rec['runtimeSuffixed']:
        warnings.append(f"runtime names with a Blender suffix: {', '.join(rec['runtimeSuffixed'][:4])}")
    if rec['animations'] or rec['skins']:
        warnings.append('animations or skins present (the pipeline exports none)')
    if rec['textures']:
        warnings.append(f"{rec['textures']} textures (the pipeline uses COLOR_0 + flat materials)")
    length, width, height = rec['size']
    if category in ('ground', 'structure') and height > 0 and rec['boundsMin'][1] < -0.25 * height:
        warnings.append(f"origin: {rec['boundsMin'][1]:.2f} m below the ground plane")
    names = set(rec['nodeNames'])
    base = rec['file'][:-4]
    own = base[:-3] if base.endswith('_hd') else base
    for u in units_by_model.get(own, []):
        size = u['modelSize']
        if size and length > 0.01:
            want_l, want_w, want_h = size
            for label, have, want in (('width', width, want_w), ('height', height, want_h)):
                ratio = (have / length) / (want / want_l)
                if abs(ratio - 1) > SIZE_TOLERANCE:
                    # The model's own def: an error. A def borrowing another model (a stand-in, a variant): a warning.
                    mine = u['id'] == own
                    (errors if mine else warnings).append(
                        f"{u['id']}{'' if mine else ' (borrowed model)'}: {label}/length {have / length:.2f} "
                        f"vs modelSize {want / want_l:.2f} ({ratio - 1:+.0%})")
            if abs(length / want_l - 1) > LENGTH_TOLERANCE:
                warnings.append(f"{u['id']}: length {length:.2f} m vs modelSize {want_l} m (fitted at runtime)")
        for part in u['parts']:
            node = part.get('node')
            if not node:
                continue
            found = any(any(n.startswith(p[:-1]) for n in names) if p.endswith('*') else p in names
                        for p in node.split('|'))
            if not found:
                errors.append(f"{u['id']}: boss part '{part.get('id')}' node {node} not in the model")
    if category == 'air' and any(n.startswith('Rotor') for n in names) and 'rotor' not in rec['runtimeNodes']:
        warnings.append('rotor parts but no spinning Rotor pivot')
    if hd_twin is not None:
        mine = {k: sorted(v) for k, v in rec['runtimeNodes'].items() if k != 'point'}
        theirs = {k: sorted(v) for k, v in hd_twin['runtimeNodes'].items() if k != 'point'}
        if mine != theirs:
            diff = sorted(set(sum(mine.values(), [])) ^ set(sum(theirs.values(), [])))
            errors.append(f"_hd runtime nodes differ from the normal model: {', '.join(diff[:6])}")
    for metric, cap in BUDGETS.get(category, {}).items():
        if rec.get(metric, 0) > cap:
            warnings.append(f'{metric} {rec[metric]} over the {category} budget {cap}')
    return errors, warnings


def run(names):
    balance = load_balance()
    units = resolve(balance['vehicles'])
    by_model = {}
    for u in units:
        by_model.setdefault(u['model'], []).append(u)
    categories = categorise(names, balance, units)
    records = {}
    for n in names:
        try:
            records[n] = glb_analyze.analyze(MODELS / f'{n}.glb')
        except (glb_analyze.GlbError, ValueError, KeyError, IndexError) as e:
            records[n] = {'file': f'{n}.glb', 'loadError': str(e)}
    for n, rec in records.items():
        rec['category'] = categories.get(n, 'unlisted')
        rec['hd'] = n.endswith('_hd')
        if 'loadError' in rec:
            rec['errors'], rec['warnings'] = [f"load failed: {rec['loadError']}"], []
            continue
        twin = records.get(n[:-3]) if rec['hd'] else None
        rec['errors'], rec['warnings'] = validate(rec, rec['category'], by_model, twin if twin and 'loadError' not in twin else None)
        rec['units'] = [u['id'] for u in by_model.get(n[:-3] if rec['hd'] else n, [])]
    return records


COMPARED = ('triangles', 'vertices', 'meshes', 'renderers', 'materials', 'materialSlots', 'fileBytes')


def compare(old, new):
    lines = []
    for n in sorted(set(old) | set(new)):
        if n not in new:
            lines.append(f'{n}: removed')
            continue
        if n not in old:
            lines.append(f'{n}: new ({new[n].get("triangles", "?")} triangles)')
            continue
        a, b = old[n], new[n]
        if a.get('sha1') == b.get('sha1'):
            continue
        parts, flagged = [], False
        for m in COMPARED:
            x, y = a.get(m, 0), b.get(m, 0)
            if x != y:
                pct = (y - x) / x if x else 1.0
                flagged |= abs(pct) > REGRESSION
                parts.append(f'{m} {x:,} -> {y:,} ({pct:+.1%})')
        if a.get('structureHash') != b.get('structureHash'):
            parts.append('structure changed')
        lines.append(f"{'FLAG ' if flagged else ''}{n}: {'; '.join(parts) or 'bytes only'}")
    return lines


def row(n, r):
    size = ' x '.join(f'{v:.2f}' for v in r['size']) if 'size' in r else '-'
    return (f"| {n} | {r['category']} | {r.get('triangles', 0):,} | {r.get('vertices', 0):,} | {r.get('renderers', 0)} | "
            f"{r.get('materialsUsed', 0)} | {r.get('materialSlots', 0)} | {r.get('fileBytes', 0) / 1024:.0f} | {size} | "
            f"{(r.get('color0') or {}).get('mean', '-')} |")


HEADER = ('| model | category | triangles | vertices | renderers | materials | slots | KiB | L x W x H (m) | COLOR_0 mean |\n'
          '|---|---|---:|---:|---:|---:|---:|---:|---|---:|')


REASONS = (('zero-area', 'zero-area triangles over 0.5 %'), ('boss part', 'boss part node missing'),
           ('/length', 'proportions off modelSize by over 25 %'), ('COLOR_0', 'COLOR_0 missing or out of range'),
           ('NaN', 'NaN/Infinity'), ('_hd runtime', '_hd runtime nodes differ'), ('load failed', 'load failed'),
           ('index', 'bad indices'))


def reason(error):
    return next((label for key, label in REASONS if key in error), error[:60])


def write_summary(records, stamp):
    cats = {}
    for r in records.values():
        c = cats.setdefault(r['category'], {'n': 0, 'tri': 0, 'max': (0, ''), 'slots': 0, 'err': 0, 'warn': 0})
        c['n'] += 1
        c['tri'] += r.get('triangles', 0)
        c['slots'] += r.get('materialSlots', 0)
        c['max'] = max(c['max'], (r.get('triangles', 0), r['file'][:-4]))
        c['err'] += bool(r['errors'])
        c['warn'] += bool(r['warnings'])
    flagged = [(n, r) for n, r in sorted(records.items()) if r['errors']]
    warned = [(n, r) for n, r in sorted(records.items()) if r['warnings'] and not r['errors']]
    reasons = {}
    for _, r in flagged:
        for key in {reason(e) for e in r['errors']}:
            reasons[key] = reasons.get(key, 0) + 1
    lines = [
        '# GLB baseline (prompt 27 step 2)',
        '',
        f'Generated {stamp} by `python Tools/assets/glb_check.py` over Assets/MachineBrigade/Resources/Models '
        f'({len(records)} GLB files). Full data: Tools/assets/baseline.json. Static analysis only (no Unity run).',
        'Rules: DECISIONS "27 step 0 + baseline". No numeric budgets yet (they come with the budgets document), so',
        'only hard errors are flagged; warnings are listed in the JSON.',
        '',
        '## Totals per category',
        '',
        '| category | models | triangles | avg | largest | material slots | with errors | with warnings |',
        '|---|---:|---:|---:|---|---:|---:|---:|',
    ]
    for k, c in sorted(cats.items(), key=lambda kv: -kv[1]['tri']):
        lines.append(f"| {k} | {c['n']} | {c['tri']:,} | {c['tri'] // max(1, c['n']):,} | {c['max'][1]} ({c['max'][0]:,}) | "
                     f"{c['slots']:,} | {c['err']} | {c['warn']} |")
    total = sum(r.get('triangles', 0) for r in records.values())
    lines += ['', f'All files: {total:,} triangles, {sum(1 for r in records.values() if r["errors"])} with errors, '
                  f'{len(warned)} more with warnings only.', '',
              '## Experiment models (DECISIONS "27 order" step 3)', '', HEADER]
    for n, label in EXPERIMENT.items():
        for m in (n, f'{n}_hd'):
            if m in records:
                lines.append(row(f'{m} ({label})', records[m]))
    lines += ['']
    for n in EXPERIMENT:
        for m in (n, f'{n}_hd'):
            r = records.get(m)
            if r and (r['errors'] or r['warnings']):
                lines.append(f"- {m}: " + '; '.join(r['errors'] + r['warnings']))
    lines += ['', '## Error reasons (count of models)', '']
    lines += [f'- {k}: {v}' for k, v in sorted(reasons.items(), key=lambda kv: -kv[1])] or ['- none']
    lines += ['', f'## Flagged models ({len(flagged)})', '']
    for n, r in flagged:
        lines.append(f"- **{n}** ({r['category']}): " + '; '.join(r['errors']))
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--only', nargs='*', help='print these models, write nothing')
    ap.add_argument('--compare', action='store_true', help='compare with baseline.json, write nothing')
    ap.add_argument('--accept', nargs='*', help='models whose change is intentional (needs --reason)')
    ap.add_argument('--reason', help='why the accepted change is intentional (kept in baseline.json)')
    args = ap.parse_args()
    names = sorted(p.stem for p in MODELS.glob('*.glb'))
    if args.only:
        for n, r in run([n for n in names if n in args.only]).items():
            r.pop('nodeNames', None)
            print(json.dumps({n: r}, indent=1))
        return 0
    records = run(names)
    old = json.loads(BASELINE.read_text(encoding='utf-8')) if BASELINE.exists() else None
    if args.compare:
        if not old:
            print('no baseline.json yet')
            return 1
        lines = compare(old['models'], records)
        print('\n'.join(lines) or 'no changes against the baseline')
        return 1 if any(l.startswith('FLAG') for l in lines) else 0
    stamp = dt.date.today().isoformat()
    history = old.get('history', []) if old else []
    if args.accept:
        if not args.reason:
            ap.error('--accept needs --reason')
        diff = compare({n: old['models'][n] for n in args.accept if old and n in old['models']},
                       {n: records[n] for n in args.accept if n in records})
        history.append({'date': stamp, 'models': args.accept, 'reason': args.reason, 'changes': diff})
    elif old:
        changed = [l for l in compare(old['models'], records) if l.startswith('FLAG')]
        if changed:
            print('Flagged changes against the baseline (use --accept NAME --reason TEXT to take them):')
            print('\n'.join(changed))
            return 1
    for r in records.values():
        r.pop('problems', None)
    out = {'generated': stamp, 'tool': 'Tools/assets/glb_check.py', 'count': len(records), 'budgets': BUDGETS,
           'history': history, 'models': records}
    BASELINE.write_text(json.dumps(out, indent=1, sort_keys=False) + '\n', encoding='utf-8')
    write_summary(records, stamp)
    errors = sum(1 for r in records.values() if r['errors'])
    print(f'{len(records)} GLB files, {errors} with errors -> {BASELINE.relative_to(ROOT)}, {SUMMARY.relative_to(ROOT)}')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
