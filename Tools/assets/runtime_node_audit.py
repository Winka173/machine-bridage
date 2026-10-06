"""MVA W1-B: runtime node and aim/pivot contract audit (spec parts W, X, BX; Docs/mapvisaudio).

Static: reads every Resources/Models/*.glb (JSON chunk only), Docs/export/game_snapshot.json (each unit's weapons in mount
order: slot, aim, arc) and balance.json (boss part nodes, barrelLimits). No Unity, no Blender.

    python Tools/assets/runtime_node_audit.py                    # audit, write the reports; exit 1 on a new hard finding
    python Tools/assets/runtime_node_audit.py --accept "reason"  # take today's hard findings as the known baseline
    python Tools/assets/runtime_node_audit.py --rename a b ...   # give these models stable names (runtime_nodes.propose),
                                                                 # recorded in runtime_node_map.json, then audit

Hard (BX): an indexed runtime node with a Blender suffix (Muzzle_mg.001), a duplicate or mixed (tag + suffix) runtime id,
a data part node the model lacks, a weapon slot with neither muzzle nor mount nor turret, a muzzle on another mount's pivot
than the one it is the k-th of (it cannot follow its pivot). Soft: count mismatch (k wraps), a tilted yaw pivot, a fixed-arc
mount on the wrong side of its arc, a hull-aimed weapon on a turning pivot. Known hard findings live in
runtime_node_baseline.json (each with its reason); only new ones fail, so the gate is a ratchet.

Outputs: Docs/models/RUNTIME_NODES.md (report) and Docs/models/aim_contract.json (per unit and mount: aimMode Free | Hull |
FixedArc, pivotNode, muzzleNodes[], yawMin / yawMax, pitchMin / pitchMax, findings).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'Tools/export'))
import runtime_nodes as rn  # noqa: E402

SNAPSHOT = ROOT / 'Docs/export/game_snapshot.json'
BASELINE = HERE / 'runtime_node_baseline.json'
REPORT = ROOT / 'Docs/models/RUNTIME_NODES.md'
CONTRACT = ROOT / 'Docs/models/aim_contract.json'
UNIT_LISTS = ('vehicles', 'bosses', 'towers', 'elites', 'itemVehicles')
AIM = {'Turret': 'Free', 'Free': 'Free', 'Hull': 'Hull', 'Left': 'FixedArc', 'Right': 'FixedArc'}


def model_info(path: Path):
    doc, _ = rn.read_doc(path)
    nodes = doc.get('nodes', [])
    names = [n.get('name', '') for n in nodes]
    mats, parent = rn.world_matrices(doc)
    return {'names': names, 'mats': mats, 'parent': parent, 'index': {n: i for i, n in reversed(list(enumerate(names)))}}


def ancestors(info, name):
    i = info['index'][name]
    while i in info['parent']:
        i = info['parent'][i]
        yield info['names'][i]


def pivot_of(info, name):
    """The nearest Mount_* (weapon) or Turret ancestor: what the node turns with."""
    for a in ancestors(info, name):
        p = rn.parse(a)
        if (p and p[0] == 'mount') or rn.SET_PATTERNS['turret'].match(a):
            return a
    return None


def node_findings(model, info):
    hard, soft = [], []
    names = info['names']
    seen = {}
    for n in names:
        p = rn.parse(n)
        if not p:
            continue
        seen[n] = seen.get(n, 0) + 1
        if p[2] and p[3] is not None:
            hard.append(('mixed', n, 'semantic tag and a Blender suffix at once'))
    for n, c in seen.items():
        if c > 1:
            hard.append(('duplicate', n, f'{c} nodes share the runtime id'))
    for (kind, slot), members in rn.groups(names).items():
        legacy = [m for m in members if rn.parse(m)[3] is not None]
        if legacy:
            hard.append(('suffix', f'{kind}:{slot}', ', '.join(legacy[:6]) + (f' (+{len(legacy) - 6})' if len(legacy) > 6 else '')))
    turrets = [n for n in names if rn.SET_PATTERNS['turret'].match(n)]
    if len(turrets) > 1:
        soft.append(('turrets', ','.join(turrets), 'more than one Turret: only the first turns'))
    return hard, soft


def pitch_limits(w, boss, main_mount, limits, bmr):
    try:
        cls, _ = bmr.weapon_class({'family': w.get('familyId') or w.get('family') or '', 'projectile': w.get('projectile'),
                                   'caliberMm': w.get('caliberMm'), 'targets': w.get('targets'),
                                   'minRange': w.get('minRange')}, boss, main_mount, limits)
        lim, _ = limits.of(cls, {'family': w.get('familyId') or ''}, {})
    except Exception:  # the barrel tables are an estimate; a weapon they cannot class keeps no pitch limits
        return None, None, None
    lo = lim.get('elevationMinDeg', -lim['depressionDeg'] if 'depressionDeg' in lim else None)
    return cls, lo, lim.get('elevationMaxDeg')


def unit_contract(unit, info, limits, bmr, part_nodes):
    """The aim contract rows of one unit and the findings against its model."""
    hard, soft, rows = [], [], []
    names = info['names'] if info else []
    grp = rn.groups(names)
    turret = next((n for n in names if rn.SET_PATTERNS['turret'].match(n)), None)
    seen = {}
    weapons = unit.get('weapons') or []
    per_slot = {}
    for w in weapons:
        per_slot[(w.get('slot') or 'main').lower()] = per_slot.get((w.get('slot') or 'main').lower(), 0) + 1
    for i, w in enumerate(weapons):
        slot = (w.get('slot') or 'main').lower()
        k = seen.get(slot, 0)
        seen[slot] = k + 1
        aim = AIM.get(w.get('aim'), 'Free')
        if (w.get('arcHalfDeg') or 0) > 0:
            aim = 'FixedArc'
        muzzles = grp.get(('muzzle', slot), [])
        mounts = grp.get(('mount', slot), [])
        muzzle = muzzles[k % len(muzzles)] if muzzles else None
        mount = mounts[k % len(mounts)] if len(mounts) > 1 else (mounts[0] if mounts else None)
        pivot = mount or (turret if w.get('aim') == 'Turret' or (slot == 'main' and turret) else None)
        if aim == 'Hull':
            pivot = None
        centre, half = float(w.get('arcCentreDeg') or 0), float(w.get('arcHalfDeg') or 0)
        if w.get('aim') == 'Left':
            centre, half = -90.0, 60.0
        yaw = (centre - half, centre + half) if aim == 'FixedArc' else ((-180.0, 180.0) if aim == 'Free' else (0.0, 0.0))
        cls, pmin, pmax = pitch_limits(w, {'frame': unit.get('frame')}, bool(w.get('mainMount')), limits, bmr)
        row = {'mount': i, 'slot': slot, 'k': k, 'weapon': w.get('id'), 'aimMode': aim, 'dataAim': w.get('aim'),
               'pivotNode': pivot, 'muzzleNodes': [muzzle] if muzzle else [], 'yawMin': yaw[0], 'yawMax': yaw[1],
               'pitchMin': pmin, 'pitchMax': pmax, 'pitchClass': cls, 'findings': []}
        rows.append(row)
        if not info:
            continue
        label = f"{unit['id']} m{i} {slot}#{k}"
        if not muzzles and not mounts and not turret and slot not in ('main', 'blade') and w.get('familyId') != 'melee':
            hard.append(('slot_missing', label, f'no Muzzle_{slot} / Mount_{slot} / Turret: fires from the hull'))
            row['findings'].append('slot_missing')
        if len(muzzles) > 1 and per_slot[slot] > len(muzzles) and k == len(muzzles):
            soft.append(('count', label, f'{per_slot[slot]} data mounts on {len(muzzles)} Muzzle_{slot} nodes (k wraps)'))
        if muzzle and len(mounts) > 1 and mount:
            own = pivot_of(info, muzzle)
            if own and own != mount and rn.parse(own) and rn.parse(own)[1] == slot:
                hard.append(('off_pivot', label, f'{muzzle} turns with {own}, not its k-th mount {mount}'))
                row['findings'].append('off_pivot')
        if pivot and pivot in info['index']:
            up = info['mats'][info['index'][pivot]][:3, 1]
            norm = math.sqrt(float(up @ up)) or 1.0
            if float(up[1]) / norm < 0.9:
                soft.append(('tilted', label, f'{pivot} local up {up[1] / norm:.2f}: its yaw is not level'))
                row['findings'].append('tilted')
        if aim == 'FixedArc' and pivot and pivot in info['index']:
            x, _, z = info['mats'][info['index'][pivot]][:3, 3]
            if math.hypot(x, z) > 0.5:
                az = math.degrees(math.atan2(-x, z))  # clockwise from the nose; glTF +X is the left
                off = abs((az - centre + 180) % 360 - 180)
                if off > half + 45:
                    soft.append(('arc_side', label, f'{pivot} sits at {az:.0f} deg, its arc is {centre:.0f} +/- {half:.0f}'))
                    row['findings'].append('arc_side')
        if aim == 'Hull' and muzzle and (own := pivot_of(info, muzzle)) and rn.parse(own):
            soft.append(('hull_on_pivot', label, f'hull-aimed but {muzzle} rides {own}'))
    for node in part_nodes:
        for pattern in node.split('|'):
            found = any(n.startswith(pattern[:-1]) for n in names) if pattern.endswith('*') else pattern in names
            if info and not found:
                hard.append(('part_missing', unit['id'], f'data part node {pattern} not in the model'))
    return rows, hard, soft


def load_units():
    snap = json.loads(SNAPSHOT.read_text(encoding='utf-8'))
    out = []
    for key in UNIT_LISTS:
        lst = snap.get(key) or []
        for u in (lst if isinstance(lst, list) else lst.values()):
            if u.get('model') and u.get('id'):
                out.append(u)
    return out


def audit():
    import boss_min_range as bmr
    import glb_check
    balance = glb_check.load_balance()
    limits = bmr.Limits(balance)
    parts = {}
    for u in glb_check.resolve(balance['vehicles']):
        parts[u['id']] = [p['node'] for p in u['parts'] if p.get('node')]
    infos = {p.stem: model_info(p) for p in sorted(rn.MODELS.glob('*.glb'))}
    findings = {}
    contract = {}
    for model, info in infos.items():
        hard, soft = node_findings(model, info)
        findings[model] = {'hard': hard, 'soft': soft}
    for unit in load_units():
        info = infos.get(unit['model'])
        rows, hard, soft = unit_contract(unit, info, limits, bmr, parts.get(unit['id'], []))
        contract[unit['id']] = {'model': unit['model'], 'mounts': rows}
        if info is None:
            continue
        f = findings[unit['model']]
        for h in hard:
            if h not in f['hard']:
                f['hard'].append(h)
        for s in soft:
            if s not in f['soft']:
                f['soft'].append(s)
    return infos, findings, contract


def key(model, finding):
    return f'{model}|{finding[0]}|{finding[1]}'


def write_reports(infos, findings, contract, baseline, renamed):
    CONTRACT.write_text(json.dumps({'about': 'MVA W1-B aim/pivot contract (Tools/assets/runtime_node_audit.py): per unit and '
                                             'mount, as data and model agree today. yaw: degrees clockwise from the nose; pitch: '
                                             'barrelLimits (estimated).', 'units': dict(sorted(contract.items()))},
                                   indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    hard_new, hard_known, soft_n = [], [], 0
    lines = []
    for model in sorted(findings):
        f = findings[model]
        soft_n += len(f['soft'])
        for h in f['hard']:
            (hard_known if key(model, h) in baseline else hard_new).append((model, h))
    by_code = {}
    for model, h in hard_known + hard_new:
        by_code.setdefault(h[0], set()).add(model)
    lines += ['# Runtime nodes and aim contract (MVA W1-B)', '',
              'Generated by `python Tools/assets/runtime_node_audit.py` (rules: Tools/assets/runtime_nodes.py; spec parts W, X, '
              'BX). Do not edit by hand.', '',
              f'- Models: {len(infos)}; units with weapons in the contract: {len(contract)} '
              f'({sum(len(c["mounts"]) for c in contract.values())} mounts) -> `Docs/models/aim_contract.json`.',
              f'- Renamed to stable names (runtime_node_map.json): {len(renamed)}: {", ".join(sorted(renamed))}.',
              f'- Hard findings: {len(hard_new)} new (fail), {len(hard_known)} known (baseline, each with its reason).',
              f'- Soft findings (review): {soft_n}.', '',
              '## Hard findings by rule', '', '| rule | models |', '| --- | --- |']
    for code in sorted(by_code):
        ms = sorted(by_code[code])
        lines.append(f'| {code} | {len(ms)}: {", ".join(ms[:40])}{" ..." if len(ms) > 40 else ""} |')
    lines += ['', '## New hard findings (fail)', '']
    lines += [f'- {m}: {h[0]} {h[1]}: {h[2]}' for m, h in hard_new] or ['- none']
    lines += ['', '## Known hard findings (baseline)', '', '| model | rule | where | detail | reason |', '| --- | --- | --- | --- | --- |']
    for m, h in hard_known:
        lines.append(f'| {m} | {h[0]} | {h[1]} | {h[2]} | {baseline[key(m, h)]} |')
    lines += ['', '## Soft findings', '', '| model | rule | where | detail |', '| --- | --- | --- | --- |']
    for model in sorted(findings):
        for s in findings[model]['soft']:
            lines.append(f'| {model} | {s[0]} | {s[1]} | {s[2]} |')
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return hard_new, hard_known, soft_n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--accept', metavar='REASON')
    ap.add_argument('--rename', nargs='+', metavar='MODEL')
    args = ap.parse_args()
    if args.rename:
        models = rn.load_map()
        for name in args.rename:
            path = rn.MODELS / f'{name}.glb'
            doc, _ = rn.read_doc(path)
            mapping = rn.propose(doc)
            if not mapping:
                print(f'{name}: nothing to rename')
                continue
            done = rn.rename_file(path, mapping)
            models[name] = {**models.get(name, {}), **mapping}
            print(f'{name}: renamed {len(done)}')
        rn.save_map(models)
    baseline = json.loads(BASELINE.read_text(encoding='utf-8')).get('known', {}) if BASELINE.exists() else {}
    infos, findings, contract = audit()
    if args.accept:
        known = {key(m, h): baseline.get(key(m, h), args.accept) for m, f in findings.items() for h in f['hard']}
        BASELINE.write_text(json.dumps({'about': 'Known hard runtime-node findings (MVA W1-B ratchet): each stays until its '
                                                 'model is renamed or fixed; a new one fails the audit.',
                                        'known': dict(sorted(known.items()))}, indent=1, ensure_ascii=False) + '\n',
                            encoding='utf-8')
        baseline = known
    hard_new, hard_known, soft_n = write_reports(infos, findings, contract, baseline, rn.load_map())
    print(f'RUNTIME NODES: {len(hard_new)} new hard, {len(hard_known)} known hard, {soft_n} soft -> {REPORT.relative_to(ROOT)}')
    for m, h in hard_new[:20]:
        print(f'  NEW {m}: {h[0]} {h[1]}: {h[2]}')
    return 1 if hard_new else 0


if __name__ == '__main__':
    sys.exit(main())
