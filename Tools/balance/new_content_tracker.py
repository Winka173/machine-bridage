"""Prompt 25 F2: the progress tracker of every new item in the balance spreadsheet (Docs/backlog/new_content.json).

Reads the five new-content sheets of Docs/balance/Machine_Brigade_Can_bang.xlsx and writes one entry per item, keeping
the status, game id and notes already in the tracker, so it can be re-run as work lands. An item that is both in "Đề
xuất thêm" and "Công trình mới" (same name) is one entry, with both sheets listed.

    python Tools/balance/new_content_tracker.py                      # refresh from the spreadsheet
    python Tools/balance/new_content_tracker.py --set KEY STATUS [ID]  # mark one item (chưa làm / đang làm / xong / bỏ: dropped by the owner)

Tools/balance/import_unlocks.py (prompt 25 D2) writes each item's planned shop price and source into its notes (set_notes).
"""
import json
import sys
import unicodedata
from datetime import date
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]
XLSX = ROOT / 'Docs' / 'balance' / 'Machine_Brigade_Can_bang.xlsx'
OUT = ROOT / 'Docs' / 'backlog' / 'new_content.json'
STATUSES = ('chưa làm', 'đang làm', 'xong', 'bỏ')

# sheet: (tracker prefix, kind, name column, group column, priority column, unlock column)
SHEETS = {
    'Đề xuất thêm': ('dx', 'unit', 'Tên đề xuất', 'Nhóm', 'Ưu tiên', 'Mở khóa đề xuất'),
    'Công trình mới': ('ct', 'structure', 'Tên', 'Ô', 'Ưu tiên', 'Mở khóa đề xuất'),
    'Tên lửa & bom mới': ('tl', 'ordnance', 'Tên', 'Dạng', None, 'Mở khóa đề xuất'),
    'Thẻ hỗ trợ mới': ('ht', 'support', 'Thẻ', None, None, 'Mở khóa đề xuất'),
    'Boss mới': ('bs', 'boss', 'Tên · dòng phụ', 'Cấp', None, 'Ra mắt đề xuất'),
}


def norm(name):
    return unicodedata.normalize('NFC', str(name or '')).strip().lower()


def read_items():
    wb = openpyxl.load_workbook(XLSX, data_only=True, read_only=True)
    items, by_name = [], {}
    for sheet, (prefix, kind, name_col, group_col, prio_col, unlock_col) in SHEETS.items():
        rows = list(wb[sheet].iter_rows(values_only=True))
        head = [str(h or '').strip() for h in rows[0]]
        col = {h: i for i, h in enumerate(head)}
        n = 0
        for r in rows[1:]:
            if not any(c is not None for c in r):
                continue
            name = str(r[col[name_col]] or '').strip()
            if not name:
                continue
            n += 1
            key = norm(name)
            if key in by_name:  # the same item in two sheets
                by_name[key]['sheets'].append(sheet)
                continue
            item = {
                'key': f'{prefix}{n:02d}',
                'name': name,
                'kind': kind,
                'sheets': [sheet],
                'group': str(r[col[group_col]]).strip() if group_col and r[col[group_col]] is not None else '',
                'priority': str(r[col[prio_col]]).strip() if prio_col and r[col[prio_col]] is not None else '',
                'unlock': str(r[col[unlock_col]]).strip() if unlock_col in col and r[col[unlock_col]] is not None else '',
                'status': 'chưa làm',
                'id': None,
                'notes': '',
            }
            by_name[key] = item
            items.append(item)
    return items


def load():
    if OUT.exists():
        return json.loads(OUT.read_text(encoding='utf-8'))
    return {'items': []}


def save(items):
    counts = {s: sum(1 for i in items if i['status'] == s) for s in STATUSES}
    by_kind = {}
    for i in items:
        k = by_kind.setdefault(i['kind'], {s: 0 for s in STATUSES})
        k[i['status']] += 1
    data = {
        '_about': 'Prompt 25 F2: every new item of Docs/balance/Machine_Brigade_Can_bang.xlsx and how far it is. '
                  'status: chưa làm / đang làm / xong / bỏ (dropped by the owner); id: the game id once it exists. Refreshed by '
                  'Tools/balance/new_content_tracker.py.',
        'updated': date.today().isoformat(),
        'total': len(items),
        'counts': counts,
        'byKind': by_kind,
        'items': items,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    return data


def set_notes(notes):
    """Prompt 25 D2: writes the notes of the items named (key -> text), keeping every status and id as it is."""
    items = load().get('items', [])
    for i in items:
        if i['key'] in notes:
            i['notes'] = notes[i['key']]
    return save(items)


def main():
    old = {i['key']: i for i in load().get('items', [])}
    if len(sys.argv) >= 4 and sys.argv[1] == '--set':
        key, status = sys.argv[2], sys.argv[3]
        if status not in STATUSES or key not in old:
            raise SystemExit(f'unknown key or status: {key} {status}')
        old[key]['status'] = status
        if len(sys.argv) > 4:
            old[key]['id'] = sys.argv[4]
        data = save(list(old.values()))
    else:
        items = read_items()
        for i in items:
            prev = old.get(i['key'])
            if prev and norm(prev['name']) == norm(i['name']):
                i['status'], i['id'], i['notes'] = prev['status'], prev['id'], prev.get('notes', '')
        data = save(items)
    print(data['total'], 'items', data['counts'])


if __name__ == '__main__':
    main()
