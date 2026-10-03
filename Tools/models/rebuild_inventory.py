"""Prompt 35 pass 0: inventory of every model and the rebuild list (no building).

    python Tools/models/rebuild_inventory.py        # -> Docs/models/REBUILD_LIST.md, Docs/models/rebuild_list.csv,
                                                    #    Docs/models/quality_report.xlsx/.csv, Docs/models/GOLD_METRICS.md

Finds the borrowed ("stand-in") models four ways (prompt 35 section 2.1):
  (a) geometry: >= 30 % of the model's own (non-kit) triangles are also in another model family's GLB and this model
      is the later one (quality_gate.geometry_overlap; a scaled or stretched copy is caught by the per-piece
      normalized keys);
  (b) notes: "model tạm" / "stand-in" / "temporary" in Tools/docs/unit_refs.json, unit_sheet.json or the winning
      builder's docstring; a def whose `model` is another id (Docs/models/STANDIN_AUDIT.md keeps the intentional ones);
  (c) scripts: the winning builder (the last BUILDERS entry for the id in build_assets.all_builders' order) calls
      another id's builder function;
  (d) quality: the prompt 35 gate (Tools/assets/quality_gate.py) and the pass 8 visual grades.
Priorities: P1 = borrowed or Kém, P2 = Cần sửa, P3 = Đạt (Tốt). Order: (1) borrowed bosses, (2) borrowed vehicles,
ships and aircraft in the starter deck and chapters 1-5, (3) towers, structures, HQs, walls, (4) other P1, (5) P2.
"""
from __future__ import annotations

import ast
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'Tools' / 'assets'))
sys.path.insert(0, str(HERE))
import quality_gate as qg  # noqa: E402
import scan_prep as sp  # noqa: E402

BLENDER = ROOT / 'Tools' / 'blender'
DOCS = ROOT / 'Docs' / 'models'
LIST_MD = DOCS / 'REBUILD_LIST.md'
LIST_CSV = DOCS / 'rebuild_list.csv'
CAMPAIGN = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data' / 'campaign.json'
PROGRESSION = ROOT / 'Assets' / 'MachineBrigade' / 'Scripts' / 'Game' / 'Match' / 'Progression.cs'
NOTE = re.compile(r'(model tạm|stand-?ins?|stand in|dùng tạm|temporary|placeholder)', re.I)
DOC_NOTE = re.compile(r'(model tạm|stand-in model|placeholder|temporary model)', re.I)
# The defs drawing another model on purpose (Docs/models/STANDIN_AUDIT.md (b), "INTENTIONAL").
INTENTIONAL = {'elite_grad', 'spawn_bastion', 'airfield', 'airfield.hangar', 'airfield.service',
               'shield_tower.ward', 'cp_relay.loot', 'hydra'}
GROUND_AIR_SEA = ('tracked', 'wheeled', 'ground', 'jet', 'helicopter', 'air_other', 'ship')
STATIC = ('tower', 'structure', 'hq', 'obstacle')
RANK = {'Kém': 0, 'Cần sửa': 1, 'Tốt': 2}


# ----------------------------------------------------------------------------- (c) builder scripts
def builder_order():
    text = (BLENDER / 'build_assets.py').read_text(encoding='utf-8')
    body = text[text.index('def all_builders'):text.index('def build_all')]
    return re.findall(r'\*\*(mb_\w+)\.BUILDERS', body)


def _first_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f'{_first_name(node.value)}.{node.attr}' if _first_name(node.value) else node.attr
    if isinstance(node, ast.Call):
        for arg in node.args:
            n = _first_name(arg)
            if n:
                return n
        return _first_name(node.func)
    if isinstance(node, ast.Lambda):
        for sub in ast.walk(node.body):
            if isinstance(sub, ast.Call):
                return _first_name(sub.func)
    return None


class Module:
    def __init__(self, name):
        self.name = name
        self.path = BLENDER / f'{name}.py'
        self.tree = ast.parse(self.path.read_text(encoding='utf-8'))
        self.funcs = {n.name: n for n in self.tree.body if isinstance(n, ast.FunctionDef)}
        self.aliases = {}       # local name -> (module, attr or None)
        for n in ast.walk(self.tree):
            if isinstance(n, ast.Import):
                for a in n.names:
                    self.aliases[a.asname or a.name] = (a.name, None)
            elif isinstance(n, ast.ImportFrom) and n.module:
                for a in n.names:
                    self.aliases[a.asname or a.name] = (n.module, a.name)
        self.builders = {}
        for n in self.tree.body:
            if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'BUILDERS' for t in n.targets) \
                    and isinstance(n.value, ast.Dict):
                for k, v in zip(n.value.keys, n.value.values):
                    if isinstance(k, ast.Constant) and isinstance(k.value, str):
                        first = v.elts[0] if isinstance(v, ast.Tuple) and v.elts else v
                        self.builders[k.value] = self.resolve(_first_name(first))

    def resolve(self, dotted):
        """(module, function) for a local name or alias.attr."""
        if not dotted:
            return None
        head, _, attr = dotted.partition('.')
        if attr and head in self.aliases and self.aliases[head][1] is None:
            return (self.aliases[head][0], attr.split('.')[0])
        if head in self.aliases and self.aliases[head][1]:
            return self.aliases[head]
        return (self.name, head)


def script_borrowing():
    """{id: (module, function, [other ids whose builder it calls], docstring note)} for each winning builder."""
    mods = {}
    order = builder_order()
    for name in order:
        if (BLENDER / f'{name}.py').exists():
            mods[name] = Module(name)
    winner = {}
    owners = {}             # (module, func) -> {ids}
    for name in order:
        m = mods.get(name)
        if not m:
            continue
        for bid, target in m.builders.items():
            if target:
                winner[bid] = target
                owners.setdefault(target, set()).add(bid)
    out = {}
    for bid, (mod, func) in winner.items():
        m = mods.get(mod) or (Module(mod) if (BLENDER / f'{mod}.py').exists() else None)
        if m is None or func not in m.funcs:
            out[bid] = (mod, func, [], '')
            continue
        fn = m.funcs[func]
        calls = set()
        for n in ast.walk(fn):
            if isinstance(n, ast.Call):
                t = m.resolve(_first_name(n.func) if not isinstance(n.func, ast.Call) else None)
                if t and t != (mod, func):
                    calls.add(t)
        borrowed = sorted({o for t in calls for o in owners.get(t, ()) if o != bid and qg.family(o) != qg.family(bid)})
        doc = ast.get_docstring(fn) or ''
        note = NOTE.search(doc)
        out[bid] = (mod, func, borrowed, note.group(0) if note else '')
    return out


# ----------------------------------------------------------------------------- chapters
def earliest_chapter():
    """{def id: earliest chapter (0 = the starter deck)} from campaign.json's missions and Progression.StarterVehicles."""
    camp = sp.load_jsonc(CAMPAIGN.read_text(encoding='utf-8'))
    found = {}

    def strings(x):
        if isinstance(x, str):
            yield x
        elif isinstance(x, dict):
            for v in x.values():
                yield from strings(v)
        elif isinstance(x, list):
            for v in x:
                yield from strings(v)
    missions = camp.get('missions') if isinstance(camp, dict) else None
    for ms in (missions or []):
        ch = ms.get('chapter')
        if not isinstance(ch, int):
            continue
        for s in strings(ms):
            if s not in found or ch < found[s]:
                found[s] = ch
    text = PROGRESSION.read_text(encoding='utf-8')
    m = re.search(r'StarterVehicles\s*=\s*\{([^}]*)\}', text)
    for s in re.findall(r'"(\w+)"', m.group(1) if m else ''):
        found[s] = 0
    return found


# ----------------------------------------------------------------------------- the list
def notes_for(model, units, refs, sheet):
    hits = []
    for uid in [model] + [u['id'] for u in units]:
        r = refs.get(uid) or {}
        if isinstance(r, dict) and DOC_NOTE.search(r.get('note', '') or ''):
            hits.append(f'unit_refs[{uid}]')
        s = sheet.get(uid) or {}
        if DOC_NOTE.search(s.get('shape', '') or ''):
            hits.append(f'unit_sheet[{uid}]')
    return sorted(set(hits))


def build():
    balance = sp.load_balance()
    defs = sp.Defs(balance)
    owners = sp.model_owners(defs, sp.MODELS)
    ids = list(owners)
    gold = qg.compute_gold()
    overlap = qg.geometry_overlap(ids)
    rows = qg.evaluate(ids, overlap=overlap, gold=gold, quiet=True)
    qg.write_report(rows, merge=False)
    scripts = script_borrowing()
    chapters = earliest_chapter()
    refs = json.loads((ROOT / 'Tools' / 'docs' / 'unit_refs.json').read_text(encoding='utf-8'))
    sheet = json.loads((ROOT / 'Tools' / 'docs' / 'unit_sheet.json').read_text(encoding='utf-8'))['units']
    out = []
    for r in rows:
        model = r['model']
        units = owners.get(model, [])
        reasons, borrowed = [], ''
        sa, sb, partner = overlap.get(model, (0, 0, ''))
        if sb >= qg.SHARED_MAX and partner and not qg.is_original(model, partner):
            reasons.append(f'(a) {sb:.0%} of its own triangles shared with {partner}')
            borrowed = partner
        notes = notes_for(model, units, refs, sheet)
        if notes:
            reasons.append('(b) note "model tạm/stand-in" in ' + ', '.join(notes))
        mod, func, calls, doc = scripts.get(model, ('', '', [], ''))
        if doc:
            reasons.append(f'(b) builder {mod}.{func} docstring says "{doc}"')
        if calls:
            reasons.append(f'(c) builder {mod}.{func} calls the builder of ' + ', '.join(calls[:4]))
            borrowed = borrowed or calls[0]
        soft, vis = r['soft_grade'], r['l8_visual'] or 'Tốt'
        hard = r['hard_fails']
        missing = len(re.findall(r'parts: missing ([^|]*)', hard)[0].split(',')) if 'parts: missing' in hard else 0
        hard_grade = 'Kém' if (missing >= sp.MISSING_POOR or 'triangles_floor' in hard) else \
            'Cần sửa' if hard else 'Tốt'
        cands = [g for g in (soft, vis, hard_grade) if g in RANK]
        grade = min(cands, key=lambda g: RANK[g]) if cands else 'NA'
        stand_in = bool(reasons)
        prio = 'P1' if stand_in or grade == 'Kém' else 'P2' if grade == 'Cần sửa' else 'P3'
        ch = min([chapters[u['id']] for u in units if u['id'] in chapters] + ([chapters[model]] if model in chapters
                                                                            else []), default=None)
        cls = r['class']
        if stand_in and cls == 'boss':
            group = 1
        elif stand_in and cls in GROUND_AIR_SEA and ch is not None and ch <= 5:
            group = 2
        elif cls in STATIC and prio == 'P1':
            group = 3
        elif prio == 'P1':
            group = 4
        elif prio == 'P2':
            group = 5
        else:
            group = 6
        out.append({
            'model': model, 'class': cls, 'units': r['units'], 'priority': prio, 'group': group,
            'grade': grade, 'soft_score': r['soft_score'], 'soft_grade': soft, 'l8_visual': r['l8_visual'],
            'l8_final': r['l8_final'], 'triangles': r['triangles'], 'borrowed_from': borrowed,
            'stand_in': 'yes' if stand_in else '', 'reasons': ' ; '.join(reasons),
            'hard_fails': hard, 'chapter': '' if ch is None else ('starter' if ch == 0 else ch),
        })
    out.sort(key=lambda x: (x['group'], x['chapter'] if isinstance(x['chapter'], int) else
                            (0 if x['chapter'] == 'starter' else 99), x['soft_score'] or 0, x['model']))
    for i, x in enumerate(out, 1):
        x['order'] = i
    pointers = []
    for v in defs.by_id.values():
        m = defs.model_of(v)
        if m != v['id'] and v['id'] not in INTENTIONAL and not v.get('variantOf') and v.get('model'):
            pointers.append((v['id'], m))
    write(out, pointers, gold)
    return out


def write(rows, pointers, gold):
    fields = ['order', 'model', 'class', 'priority', 'group', 'grade', 'soft_score', 'soft_grade', 'l8_visual',
              'l8_final', 'triangles', 'borrowed_from', 'stand_in', 'chapter', 'units', 'reasons', 'hard_fails']
    with LIST_CSV.open('w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)
    count = lambda p: sum(1 for r in rows if r['priority'] == p)  # noqa: E731
    si = [r for r in rows if r['stand_in']]
    how = {k: sum(1 for r in si if f'({k})' in r['reasons']) for k in 'abc'}
    groups = {1: 'borrowed bosses', 2: 'borrowed vehicles / ships / aircraft, starter deck and chapters 1-5',
              3: 'towers, structures, HQs, walls (P1)', 4: 'other P1', 5: 'P2 (Cần sửa)', 6: 'P3 (Đạt)'}
    lines = ['# Rebuild list (prompt 35 pass 0)', '',
             'Generated by `python Tools/models/rebuild_inventory.py` (data: `rebuild_list.csv`; every number in',
             '`quality_report.xlsx`). Gold: `GOLD_METRICS.md`. Decisions: Docs/DECISIONS.md "Prompt 35".', '',
             f'{len(rows)} models scored (every GLB a def, a tower branch or an HQ draws; props and scenery are',
             'decoration and not scored). '
             f'**P1 {count("P1")}, P2 {count("P2")}, P3 {count("P3")}.** Borrowed (stand-in) models: {len(si)} '
             f'(found by (a) geometry {how["a"]}, (b) notes {how["b"]}, (c) builder calls {how["c"]}; one model can '
             'have several).', '',
             'Grade = the lowest of the gate\'s soft grade, the pass 8 visual grade and the hard checks (4+ parts missing',
             'or under the triangle floor = Kém, any other hard fail = Cần sửa). "chapter" = the earliest campaign',
             'chapter a def drawing the model appears in (starter = the starter deck). Columns: order, model, class,',
             'priority, grade (soft score), triangles, borrowed from, chapter, why.', '']
    for g, title in groups.items():
        sub = [r for r in rows if r['group'] == g]
        lines += [f'## {g}. {title} ({len(sub)})', '',
                  '| # | model | class | prio | grade (score) | tris | borrowed from | ch. | why |',
                  '|---|---|---|---|---|---|---|---|---|']
        for r in sub:
            why = r['reasons'] or r['hard_fails'] or (f"L8 visual {r['l8_visual']}" if r['l8_visual'] else '')
            why = why.replace('|', '/')
            if len(why) > 160:
                why = why[:157] + '...'
            lines.append(f"| {r['order']} | `{r['model']}` | {r['class']} | {r['priority']} | {r['grade']} "
                         f"({r['soft_score']}) | {r['triangles']} | {r['borrowed_from']} | {r['chapter']} | {why} |")
        lines.append('')
    lines += ['## Defs that draw another model (data pointers)', '',
              'Not GLBs of their own: giving them a model changes the def\'s `model` (gameplay data), which prompt 35',
              'forbids, so they are listed for the owner (QUESTIONS.md). The intentional ones of STANDIN_AUDIT.md (b)',
              'are left out; elites without a model wear their base model repainted by design (DECISIONS 25B2).', '',
              '| def | draws |', '|---|---|']
    # Owner decision 7 (prompt 35 pilot review): these defs get a model id of their own, built in a later wave; the
    # data pointer changes in the commit that adds the model (no copy in between: nothing reads the id before that).
    later = {'mara_behemoth': 'own id `mara_behemoth` (owner decision 7), its model built in a later wave'}
    lines[-2:] = ['| def | draws | plan |', '|---|---|---|']
    lines += [f'| `{a}` | `{b}` | {later.get(a, "")} |' for a, b in sorted(pointers)]
    LIST_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'{len(rows)} models: P1 {count("P1")}, P2 {count("P2")}, P3 {count("P3")}; stand-ins {len(si)} {how}; '
          f'pointers {len(pointers)}')


if __name__ == '__main__':
    build()
