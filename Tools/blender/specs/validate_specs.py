"""Prompt 35 section 4: check the build specs (Tools/blender/specs/<id>.json) against the data and, with --glb, the
built GLB.

    python Tools/blender/specs/validate_specs.py               # every spec, data only
    python Tools/blender/specs/validate_specs.py --glb ixion   # + the GLB: every node named, the size

Rules: every identifying feature names at least one node; every weapon of the def (main, secondaries; a boss's
mountWeapons) has its spec entry with a mount and as many muzzles as the weapon has barrels in balance.json; a boss's
every parts[].node is in `breakable`; Mount_Flare / Mount_APS when the def has flares / APS; with --glb every node the
spec names exists in the file (a mesh name may carry the exporter's ".NNN") and the size is within the tolerance.
Exit code 1 on any failure.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'Tools' / 'models'))
sys.path.insert(0, str(ROOT / 'Tools' / 'assets'))
import glb_analyze  # noqa: E402
import scan_prep as sp  # noqa: E402

REQUIRED = ('id', 'class', 'real', 'shape', 'confidence', 'target_size', 'features', 'weapons', 'budget',
            'team_zones', 'breakable', 'faction_style', 'details')


def check(spec, defs, glb=False):
    fails = []
    for key in REQUIRED:
        if key not in spec:
            fails.append(f'missing field {key}')
    for f in spec.get('features', []):
        if not f.get('nodes'):
            fails.append(f"feature without a node: {f.get('feature')}")
    own = defs.by_id.get(spec['id'])
    if own is not None:
        want = []
        if defs.field(own, 'boss') and isinstance(defs.field(own, 'mountWeapons'), dict):
            dropped = sp.dropped_mounts(defs, own)     # a variant boss keeps only some mounts (prompt 35 wave 1)
            want = [(w, 1) for i, w in sorted(defs.field(own, 'mountWeapons').items()) if int(i) not in dropped]
        else:
            main = defs.field(own, 'weapon')
            if defs.armed(main):
                want.append((main, defs.barrels(main)))
            for s in defs.field(own, 'secondary') or []:
                if isinstance(s, dict) and defs.armed(s.get('weapon')):
                    want.append((s['weapon'], defs.barrels(s['weapon'])))
        have = [w for w in spec.get('weapons', []) if w.get('weapon') in defs.weapons]
        for wid, barrels in want:
            match = next((w for w in have if w['weapon'] == wid), None)
            if match is None:
                fails.append(f'weapon {wid} has no spec entry')
                continue
            have.remove(match)
            if not match.get('mount'):
                fails.append(f'weapon {wid} has no mount')
            if len(match.get('muzzles', [])) != barrels:
                fails.append(f"weapon {wid}: {len(match.get('muzzles', []))} muzzles, data has {barrels} barrels")
        if defs.field(own, 'flareCharges') and not spec.get('flare'):
            fails.append('the def has flares: Mount_Flare_* points needed')
        if defs.field(own, 'aps') and not spec.get('aps'):
            fails.append('the def has APS: Mount_APS needed')
        if defs.field(own, 'boss'):
            nodes = {b['node'] for b in spec.get('breakable', [])}
            for p in defs.field(own, 'parts') or []:
                if p.get('node') and not any(n.rstrip('*') in nodes for n in p['node'].split('|')):
                    fails.append(f"boss part {p.get('id')} ({p['node']}) not in breakable")
    if glb:
        path = sp.MODELS / f"{spec['id']}.glb"
        rec = glb_analyze.analyze(path)
        names = set(rec['nodeNames'])
        plain = {re.sub(r'\.\d{3}$', '', n) for n in names}
        wanted = {n for f in spec.get('features', []) for n in f.get('nodes', [])}
        wanted |= {w['mount'] for w in spec.get('weapons', []) if w.get('mount')}
        wanted |= {m for w in spec.get('weapons', []) for m in w.get('muzzles', [])}
        wanted |= {b['node'] for b in spec.get('breakable', []) if b.get('node', '').split(' ')[0] == b.get('node')}
        for n in sorted(wanted):
            if n not in names and n not in plain:
                fails.append(f'node {n} not in the GLB')
        t = spec['target_size']
        L, W, H = rec['size']
        tol = t.get('tolerance', .1)
        for label, got, want in (('L', L, t['L']), ('W', W, t['W']), ('H', H, t['H'])):
            if abs(got / want - 1) > tol:
                fails.append(f'size {label} {got:.2f} vs {want} ({got / want - 1:+.0%})')
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--glb', nargs='*', default=None, help='ids whose GLB is checked too (none: every spec)')
    args = ap.parse_args()
    defs = sp.Defs(sp.load_balance())
    bad = 0
    for path in sorted(HERE.glob('*.json')):
        spec = json.loads(path.read_text(encoding='utf-8'))
        glb = args.glb is not None and (not args.glb or spec['id'] in args.glb)
        fails = check(spec, defs, glb)
        bad += bool(fails)
        print(f"{spec['id']:24s} {'ok' if not fails else 'FAIL: ' + '; '.join(fails)}")
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
