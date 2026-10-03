"""Play-test 14 (cloud session 3): takes the deleted ids out of the source spreadsheets the importers read.

The ids are every first-column id of Docs/fixes/playtest14_deleted.md's tables. The workbooks are edited in their XML, cell
by cell, so the sheets keep their layout, styles, formulas and the computed values the importers read (openpyxl would
drop the cached results of ~6,000 formulas on saving):

  * a row whose key (column A: the id, or a manifest key "B<n>-<id>") is a deleted id is emptied: its cells keep their
    place and style, their values and formulas go;
  * a cell listing ids ("a, b, c") loses the deleted ones;
  * a deleted id inside prose (a note, a log line) is left and reported.

calcChain.xml goes when a formula is removed (Excel rebuilds it). Writes Docs/fixes/playtest14_xlsx.md (what changed).

    python Tools/balance/pt14_xlsx_prune.py [--dry]
"""

import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LIST = os.path.join(ROOT, 'Docs', 'fixes', 'playtest14_deleted.md')
REPORT = os.path.join(ROOT, 'Docs', 'fixes', 'playtest14_xlsx.md')
BOOKS = [
    'Docs/balance/Machine_Brigade_Can_bang.xlsx',
    'Docs/balance/Machine_Brigade_Can_bang_dot2_v2.xlsx',
    'Docs/ai/Machine_Brigade_AI_Research.xlsx',
    'Docs/story/Machine_Brigade_Cot_truyen_Che_do_v2.xlsx',
]
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
CELL = re.compile(r'<c r="([A-Z]+)(\d+)"([^>]*?)(/>|>(.*?)</c>)', re.S)
LIST_CELL = re.compile(r'^[a-z0-9_.]+(\s*,\s*[a-z0-9_.]+)+$')


def deleted_ids():
    text = open(LIST, encoding='utf-8').read()
    return set(re.findall(r'^\| `([a-z0-9_.]+)` \|', text, re.M))


def shared_strings(z):
    if 'xl/sharedStrings.xml' not in z.namelist():
        return []
    root = ET.fromstring(z.read('xl/sharedStrings.xml'))
    return [''.join(t.text or '' for t in si.iter(NS + 't')) for si in root.findall(NS + 'si')]


def sheet_names(z):
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    target = {r.get('Id'): r.get('Target') for r in rels}
    rid = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
    out = {}
    for s in wb.iter(NS + 'sheet'):
        t = target[s.get(rid)].lstrip('/')
        out['xl/' + t if not t.startswith('xl/') else t] = s.get('name')
    return out


def value(attrs, body, strings):
    t = re.search(r'\bt="([^"]+)"', attrs)
    kind = t.group(1) if t else 'n'
    if body is None:
        return None
    if kind == 's':
        v = re.search(r'<v>(\d+)</v>', body)
        return strings[int(v.group(1))] if v else None
    if kind == 'inlineStr':
        return ''.join(re.findall(r'<t[^>]*>(.*?)</t>', body, re.S))
    if kind == 'str':
        v = re.search(r'<v>(.*?)</v>', body, re.S)
        return v.group(1) if v else None
    return None


def style_only(attrs):
    s = re.search(r'\bs="\d+"', attrs)
    return ' ' + s.group(0) if s else ''


def prune(path, ids, dry, report):
    full = os.path.join(ROOT, path)
    key = re.compile(r'^(?:[A-Z][A-Z0-9]*-)*(' + '|'.join(sorted(map(re.escape, ids), key=len, reverse=True)) + r')$')
    code = re.compile(r'^[A-Z][A-Za-z0-9]*(-[A-Za-z0-9]+)+$')
    word = re.compile(r'(?<![a-z0-9_])(' + '|'.join(sorted(map(re.escape, ids), key=len, reverse=True)) + r')(?![a-z0-9_.])')
    with zipfile.ZipFile(full) as z:
        strings = shared_strings(z)
        names = sheet_names(z)
        items = [(i, z.read(i.filename)) for i in z.infolist()]
    changed = {}
    formulas_gone = False
    for name, sheet in names.items():
        xml = dict((i.filename, d) for i, d in items)[name].decode('utf-8')
        rows_cleared, lists, prose, masters = [], [], [], []
        # The rows whose key is gone.
        gone_rows = set()
        codes = {}
        for m in CELL.finditer(xml):
            if m.group(1) not in ('A', 'B'):
                continue
            v = value(m.group(3), m.group(5), strings)
            if not isinstance(v, str):
                continue
            v = v.strip()
            if m.group(1) == 'A':
                if key.match(v):
                    gone_rows.add(m.group(2))
                    rows_cleared.append((m.group(2), v))
                elif code.match(v):
                    codes[m.group(2)] = v
            # A manifest row ("R-radar", "B2-FLR-x" in A) names its unit in B.
            elif m.group(2) in codes and v in ids and m.group(2) not in gone_rows:
                gone_rows.add(m.group(2))
                rows_cleared.append((m.group(2), codes[m.group(2)] + ' / ' + v))

        def edit(m):
            nonlocal formulas_gone
            col, row, attrs, body = m.group(1), m.group(2), m.group(3), m.group(5)
            if row in gone_rows:
                # The master of a shared formula other rows use keeps its formula (they would lose theirs).
                if body is not None and re.search(r'<f[^>]*t="shared"[^>]*ref="', body):
                    masters.append(f'{col}{row}')
                    return m.group(0)
                if body is not None and '<f' in body:
                    formulas_gone = True
                return f'<c r="{col}{row}"{style_only(attrs)}/>'
            v = value(attrs, body, strings)
            if not isinstance(v, str) or not word.search(v):
                return m.group(0)
            if LIST_CELL.match(v.strip()):
                kept = [p.strip() for p in v.split(',') if p.strip() not in ids]
                lists.append((f'{col}{row}', v.strip(), ', '.join(kept)))
                if not kept:
                    return f'<c r="{col}{row}"{style_only(attrs)}/>'
                return f'<c r="{col}{row}"{style_only(attrs)} t="inlineStr"><is><t>{escape(", ".join(kept))}</t></is></c>'
            prose.append((f'{col}{row}', v.strip()))
            return m.group(0)

        new = CELL.sub(edit, xml)
        if rows_cleared or lists or prose:
            report.append((path, names[name], rows_cleared, lists, prose, masters))
        if new != xml:
            changed[name] = new.encode('utf-8')
    if dry or not changed:
        return bool(changed)
    tmp = full + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as out:
        for info, data in items:
            n = info.filename
            if formulas_gone and n == 'xl/calcChain.xml':
                continue
            if n in changed:
                data = changed[n]
            elif formulas_gone and n == '[Content_Types].xml':
                data = re.sub(rb'<Override[^>]*calcChain[^>]*/>', b'', data)
            elif formulas_gone and n == 'xl/_rels/workbook.xml.rels':
                data = re.sub(rb'<Relationship[^>]*calcChain[^>]*/>', b'', data)
            out.writestr(info, data)
    os.replace(tmp, full)
    return True


def main():
    dry = '--dry' in sys.argv
    ids = deleted_ids()
    report = []
    for book in BOOKS:
        prune(book, ids, dry, report)
    lines = ['# Play-test 14: deleted ids out of the source spreadsheets', '',
             'Written by `Tools/balance/pt14_xlsx_prune.py` from the ids of `Docs/fixes/playtest14_deleted.md` '
             f'({len(ids)} ids). Rows keyed by a deleted id are emptied (layout and styles kept); lists lose the id; prose '
             'mentions are left (history, notes) and listed.', '']
    for path, sheet, rows, lists, prose, masters in report:
        lines.append(f'## {os.path.basename(path)} / {sheet}')
        lines.append('')
        if rows:
            lines.append('Rows emptied: ' + ', '.join(f'{r} `{v}`' for r, v in rows) + '.')
        for cell, before, after in lists:
            lines.append(f'- {cell}: `{before}` -> `{after}`')
        if masters:
            lines.append('Kept (shared-formula masters other rows use): ' + ', '.join(masters) + '.')
        for cell, text in prose:
            lines.append(f'- left (prose) {cell}: {text[:160]}')
        lines.append('')
    if not dry:
        open(REPORT, 'w', encoding='utf-8').write('\n'.join(lines))
    print('\n'.join(lines[:3]))
    print(sum(len(r[2]) for r in report), 'rows emptied,', sum(len(r[3]) for r in report), 'lists,',
          sum(len(r[4]) for r in report), 'prose left')


if __name__ == '__main__':
    main()
