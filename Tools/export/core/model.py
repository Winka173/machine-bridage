"""Books (one xlsx a domain file), sheets, columns and rows; the flattener that turns a record into columns.

Rules kept here (spec 2.1): the first column is the stable id, then the declared columns, then the columns found in the
data (sorted), then nguon and raw_json; rows sorted by id (natural order); one row per id.
"""
from __future__ import annotations

import json
import re

from . import paths as P
from .units import column_for, known_unitless, snake

NEED_CODE_CHECK = "NEED_CODE_CHECK"
NEED_SOURCE = "NEED_SOURCE"


def chua_ap(prompt) -> str:
    """The marker of a cell a later prompt fills: CHUA_AP:prompt_N."""
    return f"CHUA_AP:prompt_{prompt}"


MARKER = re.compile(r"^(CHUA_AP:prompt_[\w.]+|NEED_CODE_CHECK|NEED_SOURCE)$")
SHEET_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,30}$")
RAW_LIMIT = 32000  # an Excel cell holds 32,767 characters


def natural_key(s: str):
    return [(0, int(t), "") if t.isdigit() else (1, 0, t) for t in re.split(r"(\d+)", str(s)) if t != ""]


class Column:
    def __init__(self, name: str, unit: str = "", meaning: str = "", enum=None, fk=None, required: bool = False,
                 kind: str | None = None, formula: str | None = None, auto: bool = False, source_note: str = ""):
        self.name = name
        self.unit = unit
        self.meaning = meaning
        self.enum = enum
        self.fk = list(fk) if fk else []
        self.required = required
        self.kind = kind
        self.formula = formula
        self.auto = auto
        self.source_note = source_note
        self.sources: set[tuple[str, str]] = set()
        self.unit_unknown = False


class Row:
    __slots__ = ("sheet", "id", "values", "raw", "nguon", "children")

    def __init__(self, sheet: "Sheet", rid, nguon: str, raw=None):
        self.sheet = sheet
        self.id = rid
        self.values: dict[str, object] = {}
        self.raw = raw
        self.nguon = nguon
        self.children: set[str] = set()

    # ------------------------------------------------------------------ cells
    def set(self, col: str, value, src: str | None = None, path: tuple | None = None, **meta):
        """Sets a cell; with (src, path) the leaf counts as exported into this column (coverage)."""
        c = self.sheet.col(col, **meta) if meta or col not in self.sheet.cols else self.sheet.cols[col]
        if col in self.values and self.values[col] != value and self.values[col] not in (None, ""):
            self.sheet.book.ctx.issue(f"{self.sheet.book.file_id}/{self.sheet.name}: id {self.id} column {col} set twice "
                                      f"({self.values[col]!r} then {value!r})")
        self.values[col] = value
        if src is not None and path is not None:
            self.mark(src, path, col)
        return c

    def mark(self, src: str, path: tuple, col: str):
        self.sheet.book.ctx.cov.mark(src, path, self.sheet.book.file_id, self.sheet.name, col)
        self.sheet.cols[col].sources.add((src, P.general_str(path)))

    # ------------------------------------------------------------------ records
    def flatten(self, obj: dict, src: str, base: tuple, prefix: str = "", aliases: dict | None = None,
                skip=(), children: dict | None = None, vectors: dict | None = None, units: dict | None = None,
                rel: tuple = ()):
        """Every field of obj into columns.

        aliases   {"key" or "a.b": column} names a column (the spec's name) instead of the snake_case key;
        skip      keys handled elsewhere (their leaves must be exported by the caller, the coverage test checks);
        children  {"key": callback(row, items, src, path)} for lists of records (a child sheet);
        vectors   {"key": [component names]} splits a fixed-length list of numbers into columns;
        units     {"key": unit label} for a key whose unit the sheet knows better than units.py.
        """
        aliases = aliases or {}
        children = children or {}
        vectors = vectors or {}
        units = units or {}
        for k, v in obj.items():
            key_path = rel + (k,)
            dotted = ".".join(str(x) for x in key_path)
            if k in skip or dotted in skip:
                continue
            path = base + (k,)
            if dotted in children or k in children:
                cb = children.get(dotted) or children.get(k)
                self.children.add(k)
                if isinstance(v, (list, dict)) and not v:
                    # an empty list of records: the parent row says so (the leaf is the empty list itself)
                    col = (aliases.get(dotted) or column_for(k, prefix)[0])
                    self.set(col, "", src, path, **self._meta(col, "", k, kind="list"))
                else:
                    cb(self, v, src, path)
                continue
            col, unit = column_for(k, prefix)
            if dotted in aliases:
                col = aliases[dotted]
            unit = units.get(dotted, units.get(k, unit))
            if isinstance(v, dict):
                if not v:
                    self.set(col, "", src, path, **self._meta(col, unit, k))
                else:
                    sub_prefix = (aliases[dotted] + "_") if dotted in aliases else col + "_"
                    self.flatten(v, src, path, sub_prefix, aliases, skip, children, vectors, units, key_path)
                continue
            if isinstance(v, list):
                if any(isinstance(x, dict) for x in v):
                    # a list of records with no child sheet named: an automatic child sheet
                    self.children.add(k)
                    self.sheet.book.ctx.issue(f"{self.sheet.book.file_id}/{self.sheet.name}: list of records '{dotted}' "
                                              f"went to an automatic child sheet", once=True)
                    auto_child(self, col, v, src, path)
                    continue
                names = vectors.get(dotted) or vectors.get(k)
                if names and len(v) <= len(names) and all(_scalar(x) for x in v):
                    for i, x in enumerate(v):
                        name = names[i]
                        vunit = "m" if name.endswith("_m") else "deg" if name.endswith("_deg") else unit
                        self.set(f"{col}_{name}", x, src, path + (i,), **self._meta(f"{col}_{name}", vunit, k))
                    continue
                if not v:
                    self.set(col, "", src, path, **self._meta(col, unit, k, kind="list"))
                    continue
                self.set(col, join_list(v), None, None, **self._meta(col, unit, k, kind="list"))
                for i, x in enumerate(v):
                    for leaf in _leaf_paths(x, path + (i,)):
                        self.mark(src, leaf, col)
                continue
            self.set(col, v, src, path, **self._meta(col, unit, k))

    def _meta(self, col: str, unit: str, key, kind: str | None = None) -> dict:
        c = self.sheet.cols.get(col)
        if c is not None:
            return {}
        meta = {"unit": unit, "auto": True}
        if kind:
            meta["kind"] = kind
        if not unit:
            meta["_unit_check"] = (not known_unitless(key))
        return meta


def _scalar(x) -> bool:
    return x is None or isinstance(x, (str, int, float, bool))


def _leaf_paths(x, path):
    if isinstance(x, list):
        if not x:
            yield path
        for i, y in enumerate(x):
            yield from _leaf_paths(y, path + (i,))
    elif isinstance(x, dict):
        if not x:
            yield path
        for k, y in x.items():
            yield from _leaf_paths(y, path + (k,))
    else:
        yield path


def fmt_scalar(x) -> str:
    if isinstance(x, bool):
        return "true" if x else "false"
    if x is None:
        return ""
    if isinstance(x, float) and x.is_integer() and abs(x) < 1e15:
        return repr(x)
    return str(x)


def join_list(v) -> str:
    """A simple list in one cell: items joined by ';' (a list of lists: inner items by ',')."""
    out = []
    for x in v:
        if isinstance(x, list):
            out.append(",".join(fmt_scalar(y) if _scalar(y) else json.dumps(y, ensure_ascii=False) for y in x))
        else:
            out.append(fmt_scalar(x))
    return ";".join(out)


def auto_child(row: Row, col: str, items: list, src: str, path: tuple):
    """A list of records with no declared child sheet: <Sheet>_<key> (truncated to 31 characters)."""
    name = f"{row.sheet.name}_{col}"[:31].rstrip("_")
    child = row.sheet.book.sheets.get(name) or row.sheet.book.sheet(
        name, f"{row.sheet.title_vi}: {col}", f"Danh sách con '{col}' của {row.sheet.name} (tự sinh).", parent=row.sheet)
    child_rows(child, row, items, src, path)


def child_rows(child: "Sheet", parent: Row, items: list, src: str, path: tuple, id_key: str = "id", **flatten_args):
    """One child row per item: id = <parent id>/<item id or index>, column <parent sheet>_id links back."""
    pcol = child.parent_col
    for i, item in enumerate(items):
        scalar = not isinstance(item, dict)
        tag = item.get(id_key) if not scalar and isinstance(item.get(id_key), (str, int)) else i
        r = child.row(f"{parent.id}/{tag}", f"{src}: {P.to_str(path + (i,))}", raw=item)
        r.set(pcol, parent.id)
        r.set("thu_tu", i)
        if scalar:
            r.set("value", item, src, path + (i,))
        else:
            args = dict(flatten_args)
            args["aliases"] = {**(args.get("aliases") or {}), id_key: "id_goc"}  # the item's own id; the row id is <parent>/<id>
            r.flatten(item, src, path + (i,), **args)
    return child


class Sheet:
    def __init__(self, book: "Book", name: str, title_vi: str, desc: str = "", id_col: str = "id", layer: str = "A",
                 parent: "Sheet | None" = None, kind: str = "table"):
        if not SHEET_NAME.match(name):
            raise ValueError(f"sheet name {name!r}: ASCII letters, digits and _ only, 31 characters at most")
        self.book = book
        self.name = name
        self.title_vi = title_vi
        self.desc = desc
        self.id_col = id_col
        self.layer = layer
        self.kind = kind
        self.parent = parent
        self.parent_col = f"{snake(parent.name)}_id" if parent is not None else None
        self.cols: dict[str, Column] = {}
        self.rows: dict[object, Row] = {}
        self.col(id_col, meaning="id ổn định (khóa chính)", required=True)
        if parent is not None:
            self.col(self.parent_col, meaning=f"id dòng cha ở {parent.name}", fk=[f"{book.file_id}/{parent.name}"],
                     required=True)
            self.col("thu_tu", meaning="thứ tự trong danh sách nguồn (0 = đầu)")

    def col(self, name: str, **meta) -> Column:
        unit_check = meta.pop("_unit_check", False)
        c = self.cols.get(name)
        if c is None:
            c = Column(name, **meta)
            c.unit_unknown = unit_check
            self.cols[name] = c
        else:
            for k, v in meta.items():
                if k == "auto":
                    continue
                if v not in (None, "", [], False) or k == "required":
                    setattr(c, k, list(v) if k == "fk" else v)
        return c

    def row(self, rid, nguon: str, raw=None) -> Row:
        if rid in self.rows:
            self.book.ctx.issue(f"{self.book.file_id}/{self.name}: duplicate id {rid!r} (second row dropped)")
            return Row(self, rid, nguon, raw)  # detached
        r = Row(self, rid, nguon, raw)
        r.values[self.id_col] = rid
        self.rows[rid] = r
        return r

    # ------------------------------------------------------------------ output order
    def column_order(self) -> list[str]:
        fixed = [n for n, c in self.cols.items() if not c.auto and n not in ("nguon", "raw_json")]
        auto = sorted(n for n, c in self.cols.items() if c.auto and n not in fixed)
        return fixed + auto + ["nguon", "raw_json"]

    def sorted_rows(self) -> list[Row]:
        return [self.rows[k] for k in sorted(self.rows, key=natural_key)]

    def table(self) -> tuple[list[str], list[list]]:
        """(header, rows) as written."""
        cols = self.column_order()
        out = []
        for r in self.sorted_rows():
            line = []
            for c in cols:
                if c == "nguon":
                    line.append(r.nguon)
                elif c == "raw_json":
                    line.append(raw_json(r))
                else:
                    line.append(r.values.get(c))
            out.append(line)
        return cols, out

    def infer_kinds(self):
        for name, c in self.cols.items():
            if c.kind:
                continue
            kinds = set()
            for r in self.rows.values():
                v = r.values.get(name)
                if v is None or v == "":
                    continue
                if isinstance(v, str) and MARKER.match(v):
                    continue
                kinds.add("bool" if isinstance(v, bool) else "int" if isinstance(v, int) else
                          "float" if isinstance(v, float) else "text")
            if kinds <= {"int"}:
                c.kind = "int" if kinds else "empty"
            elif kinds <= {"int", "float"}:
                c.kind = "number"
            elif kinds == {"bool"}:
                c.kind = "bool"
            elif kinds == {"text"}:
                c.kind = "text"
            else:
                c.kind = "mixed:" + "+".join(sorted(kinds))


def raw_json(r: Row) -> str:
    if r.raw is None:
        return ""
    text = json.dumps(r.raw, ensure_ascii=False, separators=(",", ":"))
    if len(text) > RAW_LIMIT and isinstance(r.raw, dict) and r.children:
        slim = {k: (f"<sheet con: {k}>" if k in r.children else v) for k, v in r.raw.items()}
        text = json.dumps(slim, ensure_ascii=False, separators=(",", ":"))
    if len(text) > RAW_LIMIT:
        text = "RAW_JSON_TOO_LONG: xem file nguồn ở cột nguon"
    return text


class Book:
    def __init__(self, ctx, file_id: str, title_vi: str, desc: str = ""):
        self.ctx = ctx
        self.file_id = file_id
        self.title_vi = title_vi
        self.desc = desc
        self.sheets: dict[str, Sheet] = {}

    def sheet(self, name: str, title_vi: str, desc: str = "", **kw) -> Sheet:
        if name in self.sheets:
            raise ValueError(f"{self.file_id}: sheet {name} twice")
        s = Sheet(self, name, title_vi, desc, **kw)
        self.sheets[name] = s
        return s

    def kv_sheet(self, name: str, title_vi: str, desc: str = "") -> Sheet:
        """A key / value sheet for a block of settings: one row a leaf (id = the leaf's path under the block)."""
        s = self.sheet(name, title_vi, desc, kind="kv")
        s.col("nhom", meaning="khối nguồn (đường dẫn của khối trong file nguồn)")
        s.col("khoa", meaning="khóa của lá trong khối")
        s.col("gia_tri_so", meaning="giá trị nếu là số / true-false")
        s.col("gia_tri_chu", meaning="giá trị nếu là chữ (danh sách ngăn ';')")
        s.col("don_vi", meaning="đơn vị của giá trị (trống: không đơn vị hoặc chưa rõ; xem Don_vi_chua_ro)")
        return s

    def kv_rows(self, sheet: Sheet, obj, src: str, base: tuple, group: str, units: dict | None = None,
                nguon_file: str | None = None, prefix: tuple = ()):
        """Every leaf of obj as a row of a kv sheet (lists of scalars stay in one row, joined by ';')."""
        units = units or {}
        nguon_file = nguon_file or src

        def walk(node, rel):
            if isinstance(node, dict) and node:
                for k, v in node.items():
                    walk(v, rel + (k,))
                return
            if isinstance(node, list) and node and any(isinstance(x, (dict, list)) for x in node):
                for i, v in enumerate(node):
                    walk(v, rel + (i,))
                return
            rid = P.to_str(prefix + rel) if rel else group
            r = sheet.row(rid, f"{nguon_file}: {P.to_str(base + rel)}", raw=node)
            r.values["nhom"] = P.to_str(base) if base else ""
            r.values["khoa"] = str(rel[-1]) if rel else ""
            last = next((x for x in reversed(rel) if isinstance(x, str)), "")
            unit = units.get(P.to_str(rel), units.get(last))
            if unit is None:
                unit = column_for(last)[1] if last else ""
            r.values["don_vi"] = unit
            if isinstance(node, list):
                r.set("gia_tri_chu", join_list(node))
                if node:
                    for i in range(len(node)):
                        r.mark(src, base + rel + (i,), "gia_tri_chu")
                else:
                    r.mark(src, base + rel, "gia_tri_chu")
            elif isinstance(node, dict):
                r.set("gia_tri_chu", "", src, base + rel)
            elif isinstance(node, (int, float)) or isinstance(node, bool):
                r.set("gia_tri_so", node, src, base + rel)
            else:
                r.set("gia_tri_chu", node, src, base + rel)

        walk(obj, ())
        return sheet
