"""Prompt 25 B2 part 2: put the rebuilt models' sizes into balance.json.

Reads the "Part 2" table of DECISIONS 25B2 (each rebuilt model's built box and hull) and, for every vehicle drawn with
that model, sets "scale": 1.0, "modelSize" to the built box and "length" / "width" to the hull. Then it applies the
table's model notes: the borrowed "model" lines are dropped, radar_station draws radar_site, and the Sky Fortress draws
at 1.3 x the AC-130. Re-runnable: a second run changes nothing.

    python Tools/balance/apply_model_sizes.py
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from jsonc_edit import Doc  # noqa: E402

ROOT = HERE.parents[1]
BALANCE = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data' / 'balance.json'
DECISIONS = ROOT / 'Docs' / 'DECISIONS.md'
NUM = r'(\d+(?:\.\d+)?)'


def table_rows():
    text = DECISIONS.read_text(encoding='utf-8')
    part = text[text.index('Part 2'):]
    rows = []
    for line in part.splitlines():
        if not line.startswith('|'):
            if rows:
                break
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) < 4 or cells[0] in ('Model', '') or set(cells[0]) <= set('-'):
            continue
        model = cells[0].split()[0].strip('`')
        if '(round)' in cells[0]:
            continue
        box = re.match(NUM + r'\s*x\s*' + NUM + r'\s*x\s*' + NUM, cells[2])
        hull = re.match(NUM + r'\s*x\s*' + NUM, cells[3])
        rows.append((model, [float(v) for v in box.groups()] if box else None,
                     [float(v) for v in hull.groups()] if hull else None, line))
    return rows


def main():
    doc = Doc(str(BALANCE))
    data = doc.data()
    by_model = {}
    for v in data['vehicles']:
        by_model.setdefault(v.get('model', v['id']), []).append(v['id'])
    changed = 0
    for model, box, hull, line in table_rows():
        ids = set(by_model.get(model, [])) | ({model} if model in doc.ids('vehicles') else set())
        for vid in sorted(ids):
            e = doc.entry('vehicles', vid)
            if e is None or e.has('variantOf') or e.get('boss'):
                continue
            if box:
                changed += e.set('scale', 1.0)
                changed += e.set('modelSize', [round(x, 2) for x in box])
            if hull:
                changed += e.set('length', round(hull[0], 2))
                changed += e.set('width', round(hull[1], 2))
            doc.put('vehicles', vid, e, note='B2 part 2 size')
    # The table's model notes.
    for vid in ('supply_truck', 'ammo_carrier', 'hover_gunboat', 'logistics_station', 'repair_bay'):
        e = doc.entry('vehicles', vid)
        if e is not None and e.has('model'):
            e.remove('model')
            doc.put('vehicles', vid, e, note='own model now')
            changed += 1
    e = doc.entry('vehicles', 'radar_station')
    if e is not None and e.get('model') != 'radar_site':
        e.set('model', 'radar_site')
        doc.put('vehicles', 'radar_station', e, note='own model now')
        changed += 1
    e = doc.entry('vehicles', 'sky_fortress')
    if e is not None and abs((e.get('scale') or 1) * (e.get('size') or 1) - 0.88) > 0.01:
        # 1.3 x the AC-130 on the shared C-130 airframe (DECISIONS 25B2 part 2).
        e.set('scale', 1.035)
        e.set('size', 0.85)
        doc.put('vehicles', 'sky_fortress', e, note='1.3 x the AC-130')
        changed += 1
    doc.save()
    print('changes:', changed)


if __name__ == '__main__':
    main()
