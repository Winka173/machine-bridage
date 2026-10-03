"""Pass 7 (spec 7, 12.6): compare two exports, sheet by sheet, generically (any file, any sheet, so file 13 and the
<name>_tham_chieu sheets of pass 10 are covered without code here).

    python Tools/export/export.py diff <dirA> <dirB>        two export folders (Docs/export/<date>_<commit>)
    python Tools/export/export.py diff <refA> <refB>        two commits / tags / branches: each is exported in a temp git
                                                            worktree with THIS exporter (so only the data differs), then diffed

Output Docs/export/diff_<A>_<B>/: <file>.xlsx + <file>.md for every file of either export (same names 00-13) and
00_tom_tat.xlsx (+ .md). Read from csv/ when the folder has it (the exact strings written), else from the xlsx files.
Rows are matched by the first column (the stable id). Not compared: raw_json (it repeats the row), nguon (provenance; a C#
line shift is not a data change) and the <col>_truoc / <col>_sau / so_voi_ban_goc block (it depends on --base, not on the
data). A column only one side has is listed in Cot_doi, not as a change of every cell. Deterministic: no clock, sorted.
"""
from __future__ import annotations

import csv
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from . import repo
from .write import csv_value, write_xlsx

SKIP_COLS = {"raw_json", "nguon", "so_voi_ban_goc"}
DEFAULT_PACK_QA = "current/_qa"
XLSX_MAX_ROWS = 1_000_000
MD_ALL_ROWS = 40     # spec 6: a table over 40 rows prints its first 15 + "xem sheet"
MD_HEAD_ROWS = 15
TOP_N = 50
BIG_PCT = 20.0
NUM = re.compile(r"^-?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?$")
PATH_IN_NGUON = re.compile(r"(?:Assets|Tools|Docs)/[^\s;,()#:\"']+")
csv.field_size_limit(2**31 - 1)


# ---------------------------------------------------------------------------------------------------------------- load
def load_export(folder: Path) -> tuple[dict, dict, str]:
    """({file id: {sheet: (header, rows)}}, {"commit", "ngay"} of 00_index.xlsx, 'xlsx'): the pack's xlsx files and the CSVs
    of bulk.zip (as sheets of their file). 00_index.xlsx itself is not compared (its hashes always move)."""
    import io
    import openpyxl
    import zipfile
    books: dict = {}
    manifest: dict = {}
    for f in sorted(folder.glob("*.xlsx")):
        wb = openpyxl.load_workbook(f, read_only=True, data_only=False)
        if f.stem == "00_index":
            if "Phien_ban" in wb.sheetnames:
                for r in wb["Phien_ban"].iter_rows(min_row=2, values_only=True):
                    if r and r[0] in ("commit", "ngay"):
                        manifest[r[0]] = str(r[1])
            wb.close()
            continue
        for ws in wb.worksheets:
            it = ws.iter_rows(values_only=True)
            header = [csv_value(v) for v in next(it, ())]
            rows = [[csv_value(v) for v in r] for r in it]
            books.setdefault(f.stem, {})[ws.title] = (header, rows)
        wb.close()
    z = folder / "bulk.zip"
    if z.is_file():
        with zipfile.ZipFile(z) as zf:
            for name in zf.namelist():
                fid, _, sheet = name[:-4].partition("__")
                lines = list(csv.reader(io.StringIO(zf.read(name).decode("utf-8"))))
                books.setdefault(fid, {})[sheet] = (lines[0] if lines else [], lines[1:])
    return books, manifest, "xlsx"


# ------------------------------------------------------------------------------------------------------------- compare
def number(s: str):
    s = s.strip()
    if NUM.match(s):
        try:
            return float(s)
        except ValueError:
            return None
    return None


def same(a: str, b: str) -> bool:
    if a == b:
        return True
    x, y = number(a), number(b)
    return x is not None and y is not None and math.isclose(x, y, rel_tol=1e-12, abs_tol=0.0)


def pct(a: str, b: str):
    x, y = number(a), number(b)
    if x is None or y is None or x == 0:
        return None
    return round((y - x) / abs(x) * 100.0, 4)


def compared_cols(header: list[str]) -> list[str]:
    hs = set(header)
    base_block = set()
    for h in header:
        if h.endswith("_truoc") and h[:-6] in hs and h[:-6] + "_sau" in hs:
            base_block |= {h, h[:-6] + "_sau"}
    return [h for h in header[1:] if h not in SKIP_COLS and h not in base_block]


def keyed(header: list[str], rows: list[list]) -> dict:
    out, seen = {}, {}
    for r in rows:
        rid = r[0] if r else ""
        n = seen.get(rid, 0) + 1
        seen[rid] = n
        out[rid if n == 1 else f"{rid}#{n}"] = dict(zip(header, r))
    return out


def metric(col: str, row: dict) -> str:
    """dps / hp / gia / chu_ky when a column (or a kv sheet's khoa) names one of the spec's watched numbers, else ''."""
    name = str(row.get("khoa") or col) if col in ("gia_tri_so", "gia_tri_chu") else col
    t = re.split(r"[_.\s]+", re.sub(r"([a-z])([A-Z])", r"\1_\2", name).lower())
    ts = set(t)
    if "dps" in ts:
        return "dps"
    if "hp" in ts:
        return "hp"
    if ts & {"cp", "cost", "price", "xu", "coins"} or any(a == "gia" and b != "tri" for a, b in zip(t, t[1:] + [""])):
        return "gia"
    if ts & {"cooldown", "reload", "cycle"} or "chu_ky" in name or name.startswith(("thoi_gian_nap", "nap_lai", "nap_bang")):
        return "chu_ky"
    return ""


def diff_sheet(fid: str, sname: str, a, b, commit_of) -> dict:
    ha, ra = a if a else ([], [])
    hb, rb = b if b else ([], [])
    out = {"file": fid, "sheet": sname, "status": "chung" if a and b else ("them" if b else "xoa"),
           "rows_a": len(ra), "rows_b": len(rb), "added": [], "removed": [], "cells": [], "cols": []}
    ka, kb = keyed(ha, ra), keyed(hb, rb)
    ca, cb = compared_cols(ha) if ha else [], compared_cols(hb) if hb else []
    if a and b:
        out["cols"] = [(c, "them") for c in cb if c not in set(ca)] + [(c, "xoa") for c in ca if c not in set(cb)]
    common = [c for c in cb if c in set(ca)]
    for rid in sorted(set(kb) - set(ka), key=_nat):
        out["added"].append((rid, kb[rid].get("nguon", ""), sum(1 for c in cb if kb[rid].get(c, "") != "")))
    for rid in sorted(set(ka) - set(kb), key=_nat):
        out["removed"].append((rid, ka[rid].get("nguon", ""), sum(1 for c in ca if ka[rid].get(c, "") != "")))
    for rid in sorted(set(ka) & set(kb), key=_nat):
        x, y = ka[rid], kb[rid]
        for c in common:
            old, new = x.get(c, ""), y.get(c, "")
            if not same(old, new):
                nguon = y.get("nguon", "") or x.get("nguon", "")
                out["cells"].append({"row": rid, "col": c, "old": old, "new": new, "pct": pct(old, new),
                                     "commit": commit_of(nguon), "nguon": nguon, "metric": metric(c, y)})
    return out


def _nat(s):
    return [(0, int(t), "") if t.isdigit() else (1, 0, t) for t in re.split(r"(\d+)", str(s)) if t != ""]


# ------------------------------------------------------------------------------------------------------- source commit
class Commits:
    """The newest commit in (A, B] that touched the row's source file (from nguon), or '' when none did / unknown."""

    def __init__(self, a: str | None, b: str | None):
        self.latest: dict[str, str] = {}
        self.ok = bool(a and b)
        if self.ok:
            log = repo.git("log", "--format=@%h", "--name-only", f"{a}..{b}", check=False)
            cur = ""
            for line in log.splitlines():
                if line.startswith("@"):
                    cur = line[1:]
                elif line.strip() and line not in self.latest:
                    self.latest[line.strip()] = cur
        self.cache: dict[str, str] = {}

    def __call__(self, nguon: str) -> str:
        if not self.ok or not nguon:
            return ""
        if nguon not in self.cache:
            hit = ""
            for p in PATH_IN_NGUON.findall(nguon):
                p = p.rstrip(".")
                if p in self.latest:
                    hit = self.latest[p]
                    break
            self.cache[nguon] = hit
        return self.cache[nguon]


# --------------------------------------------------------------------------------------------------------------- write
def _cell(v):
    if isinstance(v, str):
        n = number(v)
        if n is not None:
            return int(n) if re.fullmatch(r"-?\d+", v.strip()) and abs(n) < 2**53 else n
        if v in ("TRUE", "FALSE"):
            return v == "TRUE"
    return v


def _split(name: str, header: list[str], rows: list[list]) -> list[tuple]:
    if len(rows) <= XLSX_MAX_ROWS:
        return [(name, header, rows, set())]
    return [(f"{name}_{i // XLSX_MAX_ROWS + 1}", header, rows[i:i + XLSX_MAX_ROWS], set())
            for i in range(0, len(rows), XLSX_MAX_ROWS)]


def file_sheets(fid: str, results: list[dict]) -> list[tuple]:
    tom = [[r["sheet"], r["status"], r["rows_a"], r["rows_b"], len(r["added"]), len(r["removed"]),
            len({c["row"] for c in r["cells"]}), len(r["cells"]), sum(1 for _, s in r["cols"] if s == "them"),
            sum(1 for _, s in r["cols"] if s == "xoa")] for r in results]
    h_tom = ["id", "trang_thai", "so_dong_a", "so_dong_b", "dong_them", "dong_xoa", "dong_doi", "o_doi", "cot_them", "cot_xoa"]
    add = [[f"{r['sheet']}/{rid}", r["sheet"], rid, n, ng] for r in results for rid, ng, n in r["added"]]
    rem = [[f"{r['sheet']}/{rid}", r["sheet"], rid, n, ng] for r in results for rid, ng, n in r["removed"]]
    h_row = ["id", "sheet", "id_dong", "so_o_co_gia_tri", "nguon"]
    cells = [[f"{r['sheet']}/{c['row']}/{c['col']}", r["sheet"], c["row"], c["col"], _cell(c["old"]), _cell(c["new"]),
              c["pct"], c["commit"], c["metric"], c["nguon"]] for r in results for c in r["cells"]]
    h_cell = ["id", "sheet", "id_dong", "cot", "gia_tri_cu", "gia_tri_moi", "chenh_lech_pct", "commit_nguon", "nhom_theo_doi",
              "nguon"]
    cols = [[f"{r['sheet']}/{c}", r["sheet"], c, s] for r in results for c, s in r["cols"]]
    return ([("Tom_tat", h_tom, tom, set())] + _split("Dong_them", h_row, add) + _split("Dong_xoa", h_row, rem)
            + _split("O_doi", h_cell, cells) + [("Cot_doi", ["id", "sheet", "cot", "trang_thai"], cols, set())])


def _md_table(header: list[str], rows: list[list], where: str) -> list[str]:
    if not rows:
        return ["(không có)", ""]
    shown = rows if len(rows) <= MD_ALL_ROWS else rows[:MD_HEAD_ROWS]
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for r in shown:
        out.append("| " + " | ".join(_md(v) for v in r) + " |")
    if len(rows) > len(shown):
        out.append(f"\n{len(shown)} / {len(rows)} dòng đầu; xem sheet {where}.")
    return out + [""]


def _md(v) -> str:
    s = "" if v is None else csv_value(v)
    s = s.replace("|", "\\|").replace("\n", " ")
    return s if len(s) <= 80 else s[:77] + "..."


def file_md(fid: str, results: list[dict], la: str, lb: str) -> str:
    lines = [f"# So sánh {fid}: {la} → {lb}", "",
             f"Sheet: diff_{la}_{lb}/{fid}.xlsx. Dòng ghép theo cột đầu (id). Không so: raw_json, nguon, khối _truoc / _sau.", ""]
    lines += ["## Theo sheet", ""]
    lines += _md_table(["sheet", "trạng thái", "dòng A", "dòng B", "thêm", "xóa", "dòng đổi", "ô đổi"],
                       [[r["sheet"], r["status"], r["rows_a"], r["rows_b"], len(r["added"]), len(r["removed"]),
                         len({c["row"] for c in r["cells"]}), len(r["cells"])] for r in results], "Tom_tat")
    for r in results:
        if not (r["added"] or r["removed"] or r["cells"] or r["cols"]):
            continue
        lines += [f"## {r['sheet']}", ""]
        if r["cols"]:
            lines += ["Cột thêm / xóa: " + "; ".join(f"{c} ({s})" for c, s in r["cols"]), ""]
        if r["added"]:
            lines += ["Dòng thêm:", ""] + _md_table(["id"], [[x[0]] for x in r["added"]], "Dong_them")
        if r["removed"]:
            lines += ["Dòng xóa:", ""] + _md_table(["id"], [[x[0]] for x in r["removed"]], "Dong_xoa")
        if r["cells"]:
            lines += ["Ô đổi:", ""] + _md_table(["id", "cột", "cũ", "mới", "%", "commit"],
                                                [[c["row"], c["col"], c["old"], c["new"], c["pct"], c["commit"]]
                                                 for c in r["cells"]], "O_doi")
    return "\n".join(lines) + "\n"


def summary_sheets(all_results: dict, meta: dict) -> list[tuple]:
    readme = [[k, v] for k, v in meta.items()]
    per_file, per_sheet, every = [], [], []
    for fid, results in sorted(all_results.items()):
        st = {"them": 0, "xoa": 0, "chung": 0}
        for r in results:
            st[r["status"]] += 1
        per_file.append([fid, len(results), st["them"], st["xoa"], sum(len(r["added"]) for r in results),
                         sum(len(r["removed"]) for r in results), sum(len(r["cells"]) for r in results),
                         sum(len(r["cols"]) for r in results)])
        for r in results:
            per_sheet.append([f"{fid}/{r['sheet']}", fid, r["sheet"], r["status"], r["rows_a"], r["rows_b"], len(r["added"]),
                              len(r["removed"]), len(r["cells"]), len(r["cols"])])
            if fid != "00_chi_muc":  # the index's counts are not game values: kept out of the top 50 and the 20 % list
                every.extend((fid, r["sheet"], c) for c in r["cells"])
    ranked = sorted((e for e in every if e[2]["pct"] is not None),
                    key=lambda e: (-abs(e[2]["pct"]), e[0], e[1], _nat(e[2]["row"]), e[2]["col"]))
    top = [[f"{f}/{s}/{c['row']}/{c['col']}", f, s, c["row"], c["col"], _cell(c["old"]), _cell(c["new"]), c["pct"],
            c["commit"]] for f, s, c in ranked[:TOP_N]]
    big = [[f"{f}/{s}/{c['row']}/{c['col']}", f, s, c["row"], c["metric"], c["col"], _cell(c["old"]), _cell(c["new"]),
            c["pct"], c["commit"]]
           for f, s, c in every if c["metric"] and c["pct"] is not None and abs(c["pct"]) > BIG_PCT]
    big += [[f"{f}/{s}/{c['row']}/{c['col']}", f, s, c["row"], c["metric"], c["col"], _cell(c["old"]), _cell(c["new"]),
             "", c["commit"]]
            for f, s, c in every if c["metric"] and c["pct"] is None and number(c["old"]) == 0 and number(c["new"])]
    big.sort(key=lambda r: (r[1], r[2], _nat(r[3]), r[5]))
    h_cnt = ["so_dong_them", "so_dong_xoa", "so_o_doi", "so_cot_doi"]
    return [
        ("README", ["id", "gia_tri"], readme, set()),
        ("Theo_file", ["id", "so_sheet", "sheet_them", "sheet_xoa"] + h_cnt, per_file, set()),
        ("Theo_sheet", ["id", "file", "sheet", "trang_thai", "so_dong_a", "so_dong_b"] + h_cnt, per_sheet, set()),
        ("Top_50_pct", ["id", "file", "sheet", "id_dong", "cot", "gia_tri_cu", "gia_tri_moi", "chenh_lech_pct",
                        "commit_nguon"], top, set()),
        ("Doi_tren_20pct", ["id", "file", "sheet", "thuc_the", "nhom", "cot", "gia_tri_cu", "gia_tri_moi",
                            "chenh_lech_pct", "commit_nguon"], big, set()),
    ]


def summary_md(sheets: list[tuple], la: str, lb: str) -> str:
    lines = [f"# So sánh bộ xuất: {la} → {lb}", "", "Sheet: 00_tom_tat.xlsx. Nhóm theo dõi (spec 7): dps, hp (máu), gia "
             "(giá: cp / cost / price), chu_ky (cooldown / reload / nạp); đổi quá 20 % hoặc từ 0.", ""]
    for name, header, rows, _ in sheets:
        lines += [f"## {name}", ""] + _md_table(header, rows, f"00_tom_tat/{name}")
    return "\n".join(lines) + "\n"


def diff_dirs(a: Path, b: Path, out: Path, la: str, lb: str, ca: str | None = None, cb: str | None = None) -> dict:
    books_a, man_a, fmt_a = load_export(a)
    books_b, man_b, fmt_b = load_export(b)
    ca = ca or (repo.resolve_ref(man_a["commit"]) if man_a.get("commit") else None)
    cb = cb or (repo.resolve_ref(man_b["commit"]) if man_b.get("commit") else None)
    commit_of = Commits(ca, cb)
    all_results = {}
    for fid in sorted(set(books_a) | set(books_b)):
        sa, sb = books_a.get(fid, {}), books_b.get(fid, {})
        all_results[fid] = [diff_sheet(fid, s, sa.get(s), sb.get(s), commit_of) for s in sorted(set(sa) | set(sb))]
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for fid, results in all_results.items():
        write_xlsx(out / f"{fid}.xlsx", file_sheets(fid, results))
        (out / f"{fid}.md").write_bytes(file_md(fid, results, la, lb).encode("utf-8"))
    meta = {"ban_a": la, "ban_b": lb, "commit_a": ca or man_a.get("commit", ""), "commit_b": cb or man_b.get("commit", ""),
            "doc_tu_a": fmt_a, "doc_tu_b": fmt_b, "commit_nguon": "có" if commit_of.ok else "không (thiếu commit trong git)",
            "lenh": f"python Tools/export/export.py diff {la} {lb}"}
    sheets = summary_sheets(all_results, meta)
    write_xlsx(out / "00_tom_tat.xlsx", sheets)
    (out / "00_tom_tat.md").write_bytes(summary_md(sheets, la, lb).encode("utf-8"))
    return {"files": len(all_results), "cells": sum(len(r["cells"]) for rs in all_results.values() for r in rs),
            "added": sum(len(r["added"]) for rs in all_results.values() for r in rs),
            "removed": sum(len(r["removed"]) for rs in all_results.values() for r in rs),
            "big": len(sheets[4][2])}


# ------------------------------------------------------------------------------------------------------- commit form
def _label(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", s).strip("-") or "x"


def export_ref(ref: str, commit: str, work: Path) -> Path:
    """Exports `ref` with this exporter in a temp worktree (lenient: a domain whose sources the old tree lacks is left out)."""
    wt = work / f"wt_{commit}"
    repo.git("worktree", "add", "--detach", str(wt), commit)
    try:
        here = Path(__file__).resolve().parents[1]
        dst = wt / "Tools" / "export"
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(here, dst, ignore=shutil.ignore_patterns("__pycache__"))
        out = work / f"out_{commit}"
        r = subprocess.run([sys.executable, str(dst / "export.py"), "--base", "", "--lenient", "--out", str(out)],
                           cwd=wt, capture_output=True)
        text = r.stdout.decode("utf-8", "replace")
        for line in text.splitlines():
            if line.startswith(("lenient:", "sources ", "foreign keys")):
                print(f"  [{commit}] {line}")
        if not (out / "00_index.xlsx").is_file():
            raise RuntimeError(f"export of {ref} ({commit}) wrote nothing: {r.stderr.decode('utf-8', 'replace')[-400:]}")
        return out
    finally:
        repo.git("worktree", "remove", "--force", str(wt), check=False)


def main(a: str, b: str, out: str | None) -> int:
    def as_dir(x: str):
        for p in (Path(x), repo.ROOT / x, repo.ROOT / "Docs" / "export" / x):
            if p.is_dir() and (p / "00_index.xlsx").is_file():
                return p
        return None

    da, db = as_dir(a), as_dir(b)
    work = None
    try:
        ca = cb = None
        if da is None or db is None:
            work = Path(tempfile.mkdtemp(prefix="mb_export_diff_"))
            if da is None:
                ca = repo.resolve_ref(a)
                if not ca:
                    print(f"diff: {a} is neither an export folder nor a git ref")
                    return 1
                print(f"exporting {a} ({ca}) in a temp worktree")
                da = export_ref(a, ca, work)
            if db is None:
                cb = repo.resolve_ref(b)
                if not cb:
                    print(f"diff: {b} is neither an export folder nor a git ref")
                    return 1
                print(f"exporting {b} ({cb}) in a temp worktree")
                db = export_ref(b, cb, work)
        la = ca or _label(da.name)
        lb = cb or _label(db.name)
        target = Path(out) if out else repo.ROOT / "Docs" / "export" / DEFAULT_PACK_QA / "diff"
        if not target.is_absolute():
            target = repo.ROOT / target
        st = diff_dirs(da, db, target, la, lb, ca, cb)
        try:
            shown = target.relative_to(repo.ROOT).as_posix()
        except ValueError:
            shown = target.name
        print(f"diff {la} -> {lb}: {st['files']} files, rows +{st['added']} -{st['removed']}, {st['cells']} cells changed, "
              f"{st['big']} watched values moved > {BIG_PCT:g} %; wrote {shown}")
        return 0
    finally:
        if work is not None:
            shutil.rmtree(work, ignore_errors=True)
            repo.git("worktree", "prune", check=False)
