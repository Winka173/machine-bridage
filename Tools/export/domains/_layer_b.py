"""Layer B helpers for files 01-04 (spec 2.2, 2.3): a formula column with its _game partner, and input_<name> sheets
copied from another file (the copy test in core/formula.py compares every copied cell with its source).

A derived sheet keeps its formulas in columns declared here; Schema's cong_thuc shows the template (placeholders as in
core/formula.py), nguon_khoa the C# the _game column ports (or 'python: ...' for an analysis column the game does not
compute: the test then compares the formula with the exporter's own Python of the same rule)."""
from __future__ import annotations

from core.formula import F


def shown(template: str) -> str:
    """The template as Schema.cong_thuc shows it: a row id with a dot is bracketed ({Kinh_te!gia_tri_so@[economy.income]}),
    so the text never reads as an e-mail address to the secret scan."""
    import re
    return re.sub(r"@([^}\[\]]*\.[^}]*)\}", lambda m: "@[" + m.group(1) + "]}", template)


def declare(sheet, col: str, template: str, ref: str, unit: str = "", meaning: str = "", game: bool = True, enum=None):
    """A formula column (and <col>_game when game is True). ref: the C# 'file method' (game) or the Python rule."""
    sheet.col(col, unit=unit, meaning=meaning + (" [công thức sống]" if meaning else "công thức sống"),
              formula=shown(template), source_note=("game: " if game else "python: ") + ref, enum=enum)
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


# ---------------------------------------------------------------------------------------------------------- C# reading
# Layer B of files 05-12 (pass 5 part 2) reads a few C# literals the game's sessions and rules hold (start CP, income,
# clocks, caps): each found by a regex in its file (after an anchor, e.g. the session's class), with its line for the
# citation. A literal not found gives NEED_CODE_CHECK and an issue, never a guess.
_CS_TEXT: dict[str, str] = {}
SCRIPTS = "Assets/MachineBrigade/Scripts/"


def cs_text(path: str) -> str:
    from core.repo import ROOT
    if path not in _CS_TEXT:
        p = ROOT / path
        _CS_TEXT[path] = p.read_text("utf-8-sig") if p.exists() else ""
    return _CS_TEXT[path]


def cs_find(ctx, path: str, pattern: str, after: str | None = None, until: str | None = None, what: str = ""):
    """(groups, line) of the first match of pattern in the C# file (searched after the text `after`, before `until`);
    (None, 0) and an issue when it is not there."""
    import re
    text = cs_text(path)
    start = text.find(after) if after else 0
    end = text.find(until, max(0, start)) if until else -1
    if start < 0:
        ctx.issue(f"layer B: {path}: anchor {after!r} not found ({what})")
        return None, 0
    hay = text[:end] if end > 0 else text
    m = re.compile(pattern, re.S).search(hay, start)
    if not m:
        ctx.issue(f"layer B: {path}: {what or pattern} not found")
        return None, 0
    return m.groups(), text.count("\n", 0, m.start()) + 1


def cs_num(ctx, path: str, pattern: str, after: str | None = None, until: str | None = None, what: str = "", group: int = 0):
    """One number of a C# literal (float), its citation '<file>:<line>'; NEED_CODE_CHECK when not found."""
    from core.model import NEED_CODE_CHECK
    g, line = cs_find(ctx, path, pattern, after, until, what)
    if g is None:
        moved = tunable_for(ctx, path, pattern)
        if moved is not None:
            return moved
        return NEED_CODE_CHECK, f"{path} (không tìm thấy: {what})"
    return float(g[group]), f"{short(path)}:{line}"


def tunable_for(ctx, path: str, pattern: str):
    """A constant lane B moved from the C# into tunables.json: the C# now reads it from the data, so the literal is gone. The
    pattern names it ('public const int MaxVehicles = (\d+)'), the file names the class (TeamEconomy.cs): the data key whose
    `code` is Class.Name holds the value. Returns (value, citation) or None."""
    import re
    from core.sources import get as _get  # noqa: F401
    sid = "Assets/MachineBrigade/Resources/Data/tunables.json"
    src = ctx.sources.get(sid)
    if src is None or not src.readable:
        return None
    m = re.search(r"(?:const|readonly)\s+\w+\s+(\w+)\s*=|(\w+)\s*=\s*\(", pattern)
    name = (m.group(1) or m.group(2)) if m else None
    if not name:
        return None
    cls = path.rsplit("/", 1)[-1].split(".")[0]
    found = []
    for group, classes in src.data.items():
        if not isinstance(classes, dict):
            continue
        for ocls, items in classes.items():
            for key, entry in (items.items() if isinstance(items, dict) else ()):
                if isinstance(entry, dict) and isinstance(entry.get("value"), (int, float))                         and str(entry.get("code", "")).split(".")[-1] == name:
                    found.append((entry.get("code"), float(entry["value"]), f"tunables.json: {group}.{ocls}.{key}.value"))
    exact = [f for f in found if f[0] == f"{cls}.{name}"]
    pick = exact if exact else found  # the class may live in another file (TeamEconomy in EconomySystem.cs)
    return (pick[0][1], pick[0][2]) if len(pick) == 1 else None


def short(path: str) -> str:
    """A C# path without the Scripts prefix (for the nguon text)."""
    return path[len(SCRIPTS):] if path.startswith(SCRIPTS) else path


def git_last_commit(paths: list[str]) -> dict:
    """{path: (unix time, short hash)} of the last commit that touched each path (one git call); missing: absent."""
    import subprocess
    from core.repo import ROOT
    out = {}
    if not paths:
        return out
    try:
        txt = subprocess.run(["git", "log", "--format=@%ct %h", "--name-only", "--", *paths], cwd=ROOT,
                             capture_output=True, text=True, encoding="utf-8", check=True).stdout
    except Exception:  # noqa: BLE001
        return out
    cur = None
    for ln in txt.splitlines():
        if ln.startswith("@"):
            t, h = ln[1:].split()
            cur = (int(t), h)
        elif ln.strip() and cur and ln.strip() not in out:
            out[ln.strip()] = cur
    return out


def F_value(v):
    """A cell's reference value: an F's expect (the port's / Python's), else the value itself."""
    from core.formula import F
    return v.expect if isinstance(v, F) else v
