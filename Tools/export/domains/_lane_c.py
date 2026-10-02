"""Shared helpers of files 05-12 (lane C): list rows, marker rows, C# meta tables, Markdown tables, Docs sources.

Read only: nothing here changes a game value.
"""
from __future__ import annotations

import re

from core import paths as P
from core.model import child_rows
from core.repo import ROOT
from core.sources import Source

CAMPAIGN = "Assets/MachineBrigade/Resources/Data/campaign.json"
DATA = "Assets/MachineBrigade/Resources/Data/"

# every sheet of a unit (FK target of a deck, a roster, a unit list)
UNIT_FK = ["02_phuong_tien/Xe", "02_phuong_tien/The_ho_tro", "03_boss/Boss", "04_can_cu_thap/Thap",
           "04_can_cu_thap/Tuong", "04_can_cu_thap/Nha_chinh", "04_can_cu_thap/Mo_dun_tien_ich"]
VEHICLE_FK = ["02_phuong_tien/Xe", "03_boss/Boss", "04_can_cu_thap/Thap", "04_can_cu_thap/Tuong",
              "04_can_cu_thap/Nha_chinh", "04_can_cu_thap/Mo_dun_tien_ich"]
SUPPORT_FK = ["02_phuong_tien/The_ho_tro"]


def nguon(src: str, path: tuple) -> str:
    return f"{src}: {P.to_str(path)}" if path else src


def records(sheet, items, src: str, base: tuple, id_key: str | None = "id", id_prefix: str = "", **flatten_args):
    """One row per record of a list (id = the record's id_key, else its index); every field flattened."""
    out = []
    for i, item in enumerate(items or []):
        if isinstance(item, dict) and id_key and isinstance(item.get(id_key), (str, int)):
            rid = f"{id_prefix}{item[id_key]}"
        else:
            rid = f"{id_prefix}{i}"
        r = sheet.row(rid, nguon(src, base + (i,)), raw=item)
        if isinstance(item, dict):
            r.flatten(item, src, base + (i,), **flatten_args)
        else:
            r.set("value", item, src, base + (i,))
        out.append((r, item, base + (i,)))
    return out


def keyed(sheet, obj: dict, src: str, base: tuple, id_prefix: str = "", key_col: str | None = None, **flatten_args):
    """One row per key of a dict of records (id = the key)."""
    out = []
    for k, item in (obj or {}).items():
        r = sheet.row(f"{id_prefix}{k}", nguon(src, base + (k,)), raw=item)
        if key_col:
            r.set(key_col, k)
        if isinstance(item, dict) and item:
            r.flatten(item, src, base + (k,), **flatten_args)
        elif isinstance(item, list):
            scalar_or_list(r, "value", item, src, base + (k,))
        elif isinstance(item, dict):
            r.set("value", "", src, base + (k,))
        else:
            r.set("value", item, src, base + (k,))
        out.append((r, item, base + (k,)))
    return out


def scalar_or_list(row, col: str, value, src: str, path: tuple):
    """A scalar into col, or a list of scalars joined by ';' with every item marked."""
    from core.model import join_list
    if isinstance(value, list):
        row.set(col, join_list(value))
        if not value:
            row.mark(src, path, col)
        for i, x in enumerate(value):
            if isinstance(x, (list, dict)):
                for leaf in _leaves(x, path + (i,)):
                    row.mark(src, leaf, col)
            else:
                row.mark(src, path + (i,), col)
    elif isinstance(value, dict) and not value:
        row.set(col, "", src, path)
    else:
        row.set(col, value, src, path)


def _leaves(x, path):
    if isinstance(x, list):
        if not x:
            yield path
        for i, y in enumerate(x):
            yield from _leaves(y, path + (i,))
    elif isinstance(x, dict):
        if not x:
            yield path
        for k, y in x.items():
            yield from _leaves(y, path + (k,))
    else:
        yield path


def child(sheet, id_key: str = "id", **flatten_args):
    """A flatten() children callback: one row of sheet per item."""
    return lambda row, items, src, path: child_rows(sheet, row, items, src, path, id_key=id_key, **flatten_args)


def marker_sheet(book, name: str, title: str, desc: str, marker: str, note: str, nguon_text: str, extra: dict | None = None):
    """A sheet whose content a later pass fills: one row holding the marker (spec 9.1)."""
    sh = book.sheet(name, title, desc)
    sh.col("trang_thai", meaning="CHUA_AP:prompt_N (lượt sau điền) / NEED_CODE_CHECK")
    sh.col("ghi_chu", meaning="phần còn thiếu và nơi đọc")
    r = sh.row("chua_ap", nguon_text)
    r.set("trang_thai", marker)
    r.set("ghi_chu", note)
    for k, v in (extra or {}).items():
        r.set(k, v)
    return sh


# ---------------------------------------------------------------------- C# tables
_ARRAY = re.compile(r"static\s+readonly\s+(?P<type>[^=;{}]*?(?:\[\]|IReadOnlyList<[^=;{}]*?>))\s+(?P<name>[A-Z]\w*)\s*=\s*"
                    r"(?P<init>\{|new\s*\[\s*\]\s*\{|new\s+[\w.<>, ()]*?\[\s*\]\s*\{|new\s*\[\s*\]|new\s+[\w.<>]+\[\]\s*$)",
                    re.M)


def cs_arrays(path: str) -> list[str]:
    """The static readonly literal arrays of a C# file (names, file order): `T[] Name = { ... }` / `new[] { ... }`."""
    text = (ROOT / path).read_text("utf-8-sig")
    out = []
    for m in _ARRAY.finditer(text):
        if m.group("name") not in out:
            out.append(m.group("name"))
    return out


def cs_element_row(row, value, src: str, path: tuple, max_cols: int = 12):
    """One C# table element into columns: a scalar -> gia_tri; a tuple / list -> gia_tri_0..n (a nested list joined)."""
    if isinstance(value, dict):
        row.flatten(value, src, path)
    elif isinstance(value, list):
        if not value:
            row.set("gia_tri", "", src, path)
        for j, x in enumerate(value):
            col = f"gia_tri_{j}" if j < max_cols else f"gia_tri_{max_cols}"
            if isinstance(x, (list, dict)):
                scalar_or_list(row, col, x, src, path + (j,)) if isinstance(x, list) else row.flatten(x, src, path + (j,), prefix=f"{col}_")
            else:
                row.set(col, x, src, path + (j,))
    else:
        row.set("gia_tri", value, src, path)


# ---------------------------------------------------------------------- Docs (outside the scanned roots)
def docs_json(ctx, path: str):
    """A JSON file under Docs/ registered as a source (so the coverage test walks it too); None when missing."""
    if path in ctx.sources:
        return ctx.sources[path]
    p = ROOT / path
    if not p.exists():
        return None
    s = Source(path, "json", p, note="Docs (đăng ký bởi file 12)")
    ctx.sources[path] = s
    if s.data is None:
        ctx.unreadable.append((path, s.error or "unreadable"))
        return None
    return s


def md_tables(text: str) -> list[tuple[int, list[str], list[tuple[int, list[str]]]]]:
    """Markdown tables: [(line of the header, header cells, [(line, cells)])]."""
    out = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            header = _cells(ln)
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                rows.append((j + 1, _cells(lines[j])))
                j += 1
            out.append((i + 1, header, rows))
            i = j
        else:
            i += 1
    return out


def _cells(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", s)]


def clean_md(s: str) -> str:
    return re.sub(r"\*\*|`", "", s).strip()
