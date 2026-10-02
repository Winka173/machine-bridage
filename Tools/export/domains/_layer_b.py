"""Layer B helpers for files 01-04 (spec 2.2, 2.3): a formula column with its _game partner, and input_<name> sheets
copied from another file (the copy test in core/formula.py compares every copied cell with its source).

A derived sheet keeps its formulas in columns declared here; Schema's cong_thuc shows the template (placeholders as in
core/formula.py), nguon_khoa the C# the _game column ports (or 'python: ...' for an analysis column the game does not
compute: the test then compares the formula with the exporter's own Python of the same rule)."""
from __future__ import annotations

from core.formula import F


def declare(sheet, col: str, template: str, ref: str, unit: str = "", meaning: str = "", game: bool = True, enum=None):
    """A formula column (and <col>_game when game is True). ref: the C# 'file method' (game) or the Python rule."""
    sheet.col(col, unit=unit, meaning=meaning + (" [công thức sống]" if meaning else "công thức sống"),
              formula=template, source_note=("game: " if game else "python: ") + ref, enum=enum)
    if game:
        sheet.col(col + "_game", unit=unit, meaning=f"{col}: giá trị mã game tính (port Python của {ref})",
                  source_note=f"port Python của {ref}", enum=enum)


def put(row, col: str, template: str, value, game: bool = True):
    """The formula cell (its reference value = value) and, for a game column, <col>_game = value."""
    c = row.sheet.cols[col]
    row.set(col, F(template, expect=value, ref=c.source_note))
    if game:
        row.set(col + "_game", value)


def input_sheet(ctx, book, name: str, title: str, src_file: str, src_sheet: str, cols: list[tuple], rows: dict):
    """input_<name>: values copied from <src_file>/<src_sheet> (spec 2.2). cols: [(column, source column, unit, meaning)];
    rows: {id: {column: value}}. The copy test checks every cell against the source file's cell."""
    sh = book.sheet(name, title, f"Chép từ {src_file}/{src_sheet} (spec 2.2: công thức chỉ tham chiếu sheet cùng file); "
                                 f"test: giá trị chép == giá trị ở file nguồn", layer="B")
    sh.col("id", fk=[f"{src_file}/{src_sheet}"], meaning=f"id ở {src_file}/{src_sheet}")
    for col, src_col, unit, meaning in cols:
        sh.col(col, unit=unit, meaning=f"{meaning} (chép từ {src_file}/{src_sheet}.{src_col})",
               source_note=f"{src_file}/{src_sheet}.{src_col}")
    for rid in sorted(rows):
        r = sh.row(rid, f"{src_file}/{src_sheet} (id {rid})")
        for col, _src, _u, _m in cols:
            r.set(col, rows[rid].get(col, ""))
    ctx.__dict__.setdefault("copies", []).append(
        {"file": book.file_id, "sheet": name, "src_file": src_file, "src_sheet": src_sheet,
         "cols": {col: src for col, src, _u, _m in cols}})
    return sh


def source_value(ctx, file_id: str, sheet: str, rid, col: str):
    """A cell of an already built file (a formula: its reference value, the port's)."""
    v = ctx.books[file_id].sheets[sheet].rows[rid].values.get(col)
    return v.expect if isinstance(v, F) else v
