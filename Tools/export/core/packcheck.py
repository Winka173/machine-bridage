"""The tests of the pack (Docs/prompts/export_pack_vi.txt section 7 and addendum 8): `python Tools/export/export.py check`.

Exports in this process (the tests need the build: coverage, foreign keys, formulas), then reads the written pack back and
checks it as a reader sees it: the 19 files and images/ and nothing else, every image linked and every link real, no sheet of
sections 2.1-2.3 in an xlsx, no process word or build-time marker in any cell, the cells still NEED_CODE_CHECK listed, 200
numbers of the md tables equal to the xlsx cells (fixed seed), no secret. A second export in a temp folder (another process) must
give the same bytes. Writes <pack>/_qa/SELF_CHECK.md (no clock in it).

Exit 1: a structure, token, coverage, foreign-key, formula, md, determinism or secret failure. Exit 2 (--strict): a
NEED_CODE_CHECK cell is left. The cells the game's own code computes are listed, not failed, until ExportGameDoc fills them
(--game-json).
"""
from __future__ import annotations

import collections
import csv
import hashlib
import io
import random
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from . import index as IX
from . import pack, repo, secrets
from .diff import number

csv.field_size_limit(2**31 - 1)
SEED = 20261003
SAMPLE = 200
EXPECT_FILES = {"README.md", "00_index.xlsx", "bulk.zip"} | {f"{fid}.{ext}" for fid in pack.PACK for ext in ("xlsx", "md")}
FORBIDDEN_CELL = re.compile(r"prompt_|CHUA_AP|xuat_luot|\bluot\d|lượt \d+\b|\bHOLD:|^HOLD$")
# HOLD is the game's own name of an AI state (and of a weapons-control posture): allowed in these sheets
HOLD_OK = {"AI_trang_thai", "AI_xung_dot", "AI_xung_dot_do_kho", "AI_ho_so_che_do", "AI_ho_so_anh_xa", "AI_ho_so_pha",
           "AI_tham_chieu", "AI_thap", "Chien_thuat", "Nguon_tham_chieu", "Tham_chieu_game_co_che"}
# NEED_SOURCE belongs to real-world columns: the reference sheets and the real-world columns the game sheets carry
REAL_WORLD = re.compile(r"(_tham_chieu|_so_sanh_that|^Schema$|^Muc_luc)")
FORBIDDEN_NAMES = pack.DROP | pack.BULK | {"Van_de", "Kiem_cong_thuc", "Khoa_ngoai", "Khong_xuat", "Nguon_du_lieu", "Phu",
                                           "Nguon_khong_doc_duoc", "Cho_anh_xa", "Don_vi_chua_ro", "Hang_so_trong_ma"}
LINK = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def _row(name: str, ok: bool, detail: str = "") -> dict:
    return {"name": name, "ok": ok, "detail": detail}


# --------------------------------------------------------------------------------------------------------- structure
def structure(out: Path) -> list[dict]:
    res = []
    top = {p.name for p in out.iterdir() if p.name not in ("_qa", "images")}
    missing, extra = sorted(EXPECT_FILES - top), sorted(top - EXPECT_FILES)
    res.append(_row("19 file đúng danh sách (không thừa, không thiếu)", not missing and not extra,
                    f"thiếu {missing}; thừa {extra}" if missing or extra else f"{len(EXPECT_FILES)} file"))
    images = {p.name for p in (out / "images").glob("*")} if (out / "images").is_dir() else set()
    sub = [p.name for p in (out / "images").iterdir() if p.is_dir()] if (out / "images").is_dir() else []
    res.append(_row("images/ phẳng (không thư mục con)", not sub, f"thư mục con {sub}" if sub else f"{len(images)} ảnh"))
    linked, broken = set(), []
    for md in sorted(out.glob("*.md")):
        for rel in LINK.findall(md.read_text("utf-8")):
            p = (out / rel).resolve()
            if p.exists():
                linked.add(Path(rel).name)
            else:
                broken.append(f"{md.name}: {rel}")
    unused = sorted(images - linked)
    res.append(_row("mọi ảnh trong images/ được một md dẫn tới", not unused, f"không md nào dẫn: {unused[:5]}" if unused else ""))
    res.append(_row("mọi md dẫn tới ảnh tồn tại", not broken, "; ".join(broken[:5]) if broken else f"{len(linked)} ảnh"))
    prefix = [n for n in images if not re.match(r"\d\d_", n)]
    res.append(_row("tên ảnh có tiền tố lĩnh vực", not prefix, f"{prefix[:5]}" if prefix else ""))
    return res


# ----------------------------------------------------------------------------------------------------------- content
def read_pack(out: Path) -> dict:
    """{file: {sheet: (header, rows)}} of the 9 xlsx (values as the cells hold them)."""
    import openpyxl
    books = {}
    for f in sorted(out.glob("*.xlsx")):
        wb = openpyxl.load_workbook(f, read_only=True, data_only=False)
        sheets = {}
        for ws in wb.worksheets:
            it = ws.iter_rows(values_only=True)
            header = list(next(it, ()) or ())
            sheets[ws.title] = (header, [list(r) for r in it])
        wb.close()
        books[f.stem] = sheets
    return books


def content(out: Path, books: dict) -> tuple[list[dict], dict]:
    res = []
    names = [(f, s) for f, sh in books.items() for s in sh if s in FORBIDDEN_NAMES]
    res.append(_row("không sheet nào của mục 2.1–2.3 trong xlsx", not names, str(names[:5]) if names else ""))
    bad = collections.Counter()
    marks = collections.Counter()
    ncc = []
    ns_bad = collections.Counter()
    for f, sheets in books.items():
        for s, (header, rows) in sheets.items():
            for h in header:
                if isinstance(h, str) and FORBIDDEN_CELL.search(h):
                    bad[f"{f}/{s}!{h} (tiêu đề)"] += 1
            for r in rows:
                for i, v in enumerate(r):
                    if not isinstance(v, str) or not v:
                        continue
                    if v == "NEED_CODE_CHECK":
                        if f != "00_index":
                            ncc.append((f, s, str(r[0]), header[i]))
                        marks[v] += 1
                    elif v == "NEED_SOURCE":
                        marks[v] += 1
                        if f != "00_index" and not REAL_WORLD.search(s) and not _real_world_col(header[i]):
                            ns_bad[f"{f}/{s}.{header[i]}"] += 1
                    elif v == "KHONG_AP_DUNG":
                        marks[v] += 1
                    m = FORBIDDEN_CELL.search(v)
                    if m:
                        if v == "HOLD" and s in HOLD_OK:
                            continue
                        bad[f"{f}/{s}.{header[i]}: {m.group(0)}"] += 1
    res.append(_row('không ô nào chứa "prompt_", "luot", "CHUA_AP", "HOLD" (dấu hiệu)', not bad,
                    "; ".join(f"{k} x{n}" for k, n in list(bad.items())[:8]) if bad else
                    f"HOLD là tên trạng thái AI của game, cho phép ở: {', '.join(sorted(HOLD_OK))[:60]}…"))
    res.append(_row("NEED_SOURCE chỉ ở cột thông số ngoài đời", not ns_bad,
                    "; ".join(f"{k} x{n}" for k, n in list(ns_bad.items())[:8]) if ns_bad else f"{marks['NEED_SOURCE']} ô"))
    # bulk.zip and md: the same words; the NEED_CODE_CHECK cells of the CSVs are listed too
    words = collections.Counter()
    with zipfile.ZipFile(out / "bulk.zip") as z:
        for name in z.namelist():
            text = z.read(name).decode("utf-8")
            if "NEED_CODE_CHECK" in text:
                rows = list(csv.reader(io.StringIO(text)))
                for r in rows[1:]:
                    for i, v in enumerate(r):
                        if v == "NEED_CODE_CHECK":
                            fid, _, sheet = name[:-4].partition("__")
                            ncc.append((fid, sheet + " (bulk.zip)", r[0], rows[0][i]))
            for w in ("prompt_", "CHUA_AP", "xuat_luot"):
                if w in text:
                    words[f"bulk.zip:{name}:{w}"] += 1
    for md in out.glob("*.md"):
        text = md.read_text("utf-8")
        for w in ("prompt_", "CHUA_AP", "xuat_luot", "Trạng thái:", "lượt 1", "lượt 2", "lượt 3", "lượt 4", "lượt 5", "lượt 6",
                  "lượt 7", "lượt 8", "lượt 9"):
            if w in text:
                words[f"{md.name}:{w}"] += 1
        for m in re.finditer(r"(?i)\bprompt \d+", text):
            words[f"{md.name}:{m.group(0)}"] += 1
    res.append(_row("md và bulk.zip không có từ quy trình (prompt N, lượt N, CHUA_AP, dòng Trạng thái)", not words,
                    "; ".join(list(words)[:6]) if words else ""))
    return res, {"ncc": ncc, "marks": marks}


def _real_world_col(name) -> bool:
    """The real-world columns a game sheet carries (Vu_khi.ngoai_doi_*): NEED_SOURCE is allowed there."""
    return isinstance(name, str) and bool(re.match(r"ngoai_doi_", name))


# --------------------------------------------------------------------------------------------------------- md numbers
def md_cells(path: Path) -> list:
    """Numeric cells of the md tables headed 'Sheet <file>/<sheet>': (file, sheet, id, column, text, md name)."""
    out, lines = [], path.read_text("utf-8").splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"^Sheet (\d\d_\w+)/(\w+)(?: — .*)? \(\d+ dòng, \d+ cột\)$", lines[i])
        if not m:
            i += 1
            continue
        fid, sheet = m.group(1), m.group(2)
        j = i + 1
        while j < len(lines) and not lines[j].startswith("|"):
            j += 1
        if j + 1 >= len(lines):
            break
        header = [c.strip() for c in lines[j].strip().strip("|").split(" | ")]
        j += 2
        while j < len(lines) and lines[j].startswith("|"):
            cells = [c.strip() for c in lines[j].strip().strip("|").split(" | ")]
            if len(cells) == len(header):
                for h, c in zip(header[1:], cells[1:]):
                    if number(c) is not None:
                        out.append((fid, sheet, cells[0].replace("\\|", "|"), h, c, path.name))
            j += 1
        i = j
    return out


def md_check(out: Path, books: dict, ctx=None) -> dict:
    cells = []
    for md in sorted(out.glob("*.md")):
        cells += md_cells(md)
    random.Random(SEED).shuffle(cells)
    bad, checked = [], 0
    for fid, sheet, rid, col, text, md in cells:  # until SAMPLE cells are compared (a live formula without the build is skipped)
        if checked >= SAMPLE:
            break
        h, rows = books.get(fid, {}).get(sheet, ([], []))
        if col not in h:
            bad.append(f"{md} {fid}/{sheet}: cột {col} không có")
            continue
        ci = h.index(col)
        row = next((r for r in rows if str(r[0]).replace("\|", "|").replace("|", "/") == rid.replace("|", "/")), None)
        if row is None:
            bad.append(f"{md} {fid}/{sheet}: id {rid} không có")
            continue
        v = row[ci]
        if isinstance(v, str) and v.startswith("="):  # a live formula: the md prints the value the exporter evaluated
            v = _evaluated(ctx, fid, sheet).get(str(row[0]), {}).get(col) if ctx is not None else None
            if v is None:
                continue
        checked += 1
        a, b = number(text), (float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else number(str(v)))
        if a is None or b is None or abs(a - b) > 1e-9 * max(1.0, abs(b)):
            bad.append(f"{md} {fid}/{sheet} id {rid} {col}: md {text} xlsx {v}")
    return _row(f"{SAMPLE} ô số trong md bằng ô trong xlsx (seed {SEED}; {len(cells)} ô số in trong md)",
                not bad and checked >= min(SAMPLE, len(cells)), "; ".join(bad[:5]) if bad else f"{checked} ô khớp")


_EVAL: dict = {}


def _evaluated(ctx, fid: str, sheet: str) -> dict:
    key = (id(ctx), fid, sheet)
    if key not in _EVAL:
        h, rows = ctx.books[fid].sheets[sheet].table(values=True)
        _EVAL[key] = {str(r[0]): dict(zip(h, r)) for r in rows}
    return _EVAL[key]


# ----------------------------------------------------------------------------------------------------------- the run
def hashes(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*"))
            if p.is_file() and not p.relative_to(root).as_posix().startswith("_qa/")}


def determinism(here: Path, out: Path, args) -> dict:
    tmp = Path(tempfile.mkdtemp(prefix="mb_pack_"))
    try:
        cmd = [sys.executable, str(here / "export.py"), "export", "--out", str(tmp / "current"), "--base", args.base]
        if args.game_json:
            cmd += ["--game-json", args.game_json]
        if args.date:
            cmd += ["--date", args.date]
        r = subprocess.run(cmd, cwd=repo.ROOT, capture_output=True)
        if r.returncode not in (0, 2):
            return _row("hai lần xuất cho file giống hệt", False, "lần xuất thứ hai lỗi: " + r.stdout.decode("utf-8", "replace")[-200:])
        a, b = hashes(out), hashes(tmp / "current")
        diff = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
        return _row("hai lần xuất cho file giống hệt (hai tiến trình)", not diff,
                    f"khác: {diff[:5]}" if diff else f"{len(a)} file cùng băm")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def report(out: Path, meta: dict, results: list[dict], ncc: list, extra: list[str]) -> Path:
    lines = ["# SELF_CHECK (gói cân bằng)", "", f"Commit {meta.get('commit', '')}, ngày {meta.get('ngay', '')}.", "",
             "| Kiểm tra | Kết quả | Chi tiết |", "|---|---|---|"]
    for r in results:
        lines.append(f"| {r['name']} | {'ĐẠT' if r['ok'] else 'HỎNG'} | {str(r['detail']).replace('|', '/')[:240]} |")
    by = collections.Counter(f"{f}/{s}" for f, s, *_ in ncc)
    lines += ["", f"## NEED_CODE_CHECK còn lại: {len(ncc)} ô, {len(by)} sheet", "",
              "Giá trị chỉ mã C# tính ra; ExportGameDoc điền khi chạy với `--game-json`. Danh sách từng ô: `_qa/qa.xlsx` sheet "
              "Need_code_check.", "", "| Sheet | Số ô | Cột |", "|---|---|---|"]
    cols = collections.defaultdict(set)
    for f, s, _r, c in ncc:
        cols[f"{f}/{s}"].add(c)
    for k, n in sorted(by.items()):
        lines.append(f"| {k} | {n} | {', '.join(sorted(cols[k]))[:160]} |")
    lines += [""] + extra
    p = out / "_qa" / "SELF_CHECK.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
    return p


def main(args, ex) -> int:
    out = args.out_dir
    results = []
    extra: list[str] = []
    meta: dict = {}
    code = 0
    if args.structure_only:
        results += structure(out)
        books = read_pack(out)
        r, info = content(out, books)
        results += r
        results.append(md_check(out, books))
        ncc = info["ncc"]
    else:
        from . import repo as _repo
        base = _repo.resolve_ref(args.base) if args.base else None
        game = ex.load_game(args.game_json)
        ctx, per_source, unmapped, per_file, fk_results = ex.build(args.base if base else None, False, game)
        ex.summary(ctx, per_source, unmapped, fk_results, False)
        meta = ex.meta_of(args, ctx, base)
        hits = ex.write_all(ctx, per_source, unmapped, per_file, fk_results, out, meta, args.strict)
        tot = collections.Counter()
        for st in per_source.values():
            tot.update(st)
        results.append(_row("độ phủ khóa: không lá chưa ánh xạ, không lá ánh xạ hai nơi (lá trong bulk.zip tính là đã ánh xạ)",
                            not unmapped and not ctx.cov.duplicates,
                            f"{tot['leaves']} lá: {tot['mapped']} ánh xạ, {tot['khong_xuat']} Khong_xuat, "
                            f"{sum(unmapped.values())} chưa, {len(ctx.cov.duplicates)} hai nơi"))
        fkc = collections.Counter(r["status"] for r in fk_results)
        results.append(_row("khóa ngoại hợp lệ (gồm các khóa nay nằm cùng file)", set(fkc) <= {"OK"}, str(dict(sorted(fkc.items())))))
        fx = ctx.formula_checks
        fxc = collections.Counter(r["status"] for r in fx)
        results.append(_row("công thức Excel khớp giá trị mã game (_game) và bản chép input_ khớp nguồn", set(fxc) <= {"OK"},
                            f"{dict(sorted(fxc.items()))}, {sum(r['rows'] for r in fx)} ô"))
        results.append(_row("không bí mật trong file xuất", not hits, f"{len(hits)} chuỗi khớp mẫu" if hits else ""))
        results += structure(out)
        books = read_pack(out)
        r, info = content(out, books)
        results += r
        results.append(md_check(out, books, ctx))
        results.append(determinism(Path(ex.__file__).resolve().parent, out, args))
        ncc = info["ncc"]
        if ncc != ctx.ncc and not args.game_json:
            extra.append(f"Ghi chú: danh sách NEED_CODE_CHECK đọc từ xlsx ({len(ncc)}) và từ bộ dựng ({len(ctx.ncc)}) khác nhau.")
        extra.append(f"Ô điền từ game.json: {getattr(ctx, 'game_filled', 0)}.")
    p = report(out, meta, results, ncc, extra)
    for r in results:
        print(("PASS " if r["ok"] else "FAIL ") + r["name"] + (f": {r['detail']}" if not r["ok"] else ""))
    print(f"NEED_CODE_CHECK cells left: {len(ncc)}")
    print(f"wrote {p.relative_to(repo.ROOT).as_posix() if p.is_relative_to(repo.ROOT) else p.name}")
    if any(not r["ok"] for r in results):
        code = 1
    elif args.strict and ncc:
        code = 2
    return code
