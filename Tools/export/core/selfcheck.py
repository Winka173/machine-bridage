"""Pass 8 (spec 9, 8): the self-check. `python Tools/export/export.py check [--out DIR] [--base REF]`

Exports twice (two separate processes: the export folder, then a rerun in a temp folder), reads the written csv/ back and
runs the 9 checks of spec 9 (plus the reference-layer line of 12.6), writes 00_chi_muc/SELF_CHECK.md (no clock in it: the
same data gives the same file) and adds it to MANIFEST.json. Read only: no game value is changed.

Exit 1 when a CI check fails: coverage (an unmapped leaf or a leaf mapped twice), a foreign key, determinism (the two runs
differ) or a secret in any output file. The other checks are reported (DAT / CHUA_DAT / CHUA_AP) without failing the run,
so a later pass's gap does not block a push; SELF_CHECK.md lists every gap.
"""
from __future__ import annotations

import collections
import hashlib
import json
import math
import random
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from . import jsonc, repo, secrets
from .diff import compared_cols, load_export, number

SEED = 20261003
SAMPLE = 200
SPEC = "Docs/prompts/export_full_vi.txt"
NOT_DETERMINISTIC = {"00_chi_muc/README.md", "00_chi_muc/MANIFEST.json", "00_chi_muc/SELF_CHECK.md"}
MARKER = re.compile(r"^(CHUA_AP:prompt_[\w.]+|NEED_CODE_CHECK|NEED_SOURCE|KHONG_CO|KHONG_CHAY)$")
UNIT_TEXT = re.compile(r"^\s*-?\d+(?:[.,]\d+)?\s*(?:s|ms|m|km|kg|g|mm|cm|cp|hp|%|deg|°|m/s|km/h|rpm|giây|phút)\s*$", re.I)
# columns that name a different thing in each file (kv blocks, notes, status): left out of the (id, column) test
GENERIC_COLS = {"nhom", "khoa", "gia_tri_so", "gia_tri_chu", "trang_thai", "ghi_chu", "mo_ta"}
BAL = "Assets/MachineBrigade/Resources/Data/balance.json"
CAMP = "Assets/MachineBrigade/Resources/Data/campaign.json"


# ------------------------------------------------------------------------------------------------------------- helpers
def _dicts(books, fid, sheet):
    h, rows = books.get(fid, {}).get(sheet, ([], []))
    return [dict(zip(h, r)) for r in rows]


def _json(path: str):
    p = repo.ROOT / path
    return jsonc.loads(p.read_text("utf-8-sig")) if p.exists() else None


def _hashes(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in secrets.files(root)}


def _run_export(here: Path, out: Path, base: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(here / "export.py"), "export", "--out", str(out), "--base", base],
                       cwd=repo.ROOT, capture_output=True)
    return r.returncode, r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")


def _md(v, limit: int = 100) -> str:
    s = str(v).replace("|", "\\|").replace("\n", " ")
    return s if len(s) <= limit else s[:limit - 3] + "..."


def _table(header, rows, limit=40) -> list[str]:
    if not rows:
        return ["(không có)", ""]
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(_md(v) for v in r) + " |" for r in rows[:limit]]
    if len(rows) > limit:
        out.append(f"\n{limit} / {len(rows)} dòng đầu.")
    return out + [""]


# --------------------------------------------------------------------------------------------------------------- checks
def spec_sheets() -> dict:
    """{file: [sheet names spec 4 names]} parsed from the spec (names with an underscore or 'Name:' / 'Name (')."""
    p = repo.ROOT / SPEC
    if not p.exists():
        return {}
    t = p.read_text("utf-8")
    s4 = t[t.index("## 4."):t.index("## 5.")]
    out = {}
    for sec in re.split(r"^### ", s4, flags=re.M)[1:]:
        fid = sec.split()[0]
        names = set(re.findall(r"(?<![\w/])([A-Z][A-Za-z0-9]*_[A-Za-z0-9_]*[A-Za-z0-9]|[A-Z][a-z]+(?=\s*[:(]))", sec))
        out[fid] = sorted(n for n in names if not n.isupper() and not n.startswith(("Mount_", "Machine_Brigade"))
                          and not re.fullmatch(r"[A-Z0-9_]+", n))
    return out


def check1(books, planned: dict):
    rows, gaps = [], []
    for fid in sorted(planned):
        have = fid in books
        rows.append([fid, "có" if have else "không", len(books.get(fid, {}))])
        if not have:
            gaps.append(f"file {fid} chưa xuất" + (" (lượt 10, spec 12.3)" if fid.startswith("13_") else ""))
    missing = []
    for fid, names in spec_sheets().items():
        for n in names:
            if fid in books and n not in books[fid]:
                missing.append([fid, n])
    empty, marker_only = [], 0
    for fid, sheets in sorted(books.items()):
        for s, (h, r) in sorted(sheets.items()):
            if not r and fid != "00_chi_muc":
                empty.append([fid, s])
            elif r and all(any(MARKER.match(v or "") for v in line) for line in r):
                marker_only += 1
    if missing:
        gaps.append(f"{len(missing)} sheet spec 4 nêu chưa có (lớp B / C là lượt 5)")
    if empty:
        gaps.append(f"{len(empty)} sheet rỗng không có dòng CHUA_AP")
    status = "DAT" if not gaps else "CHUA_DAT"
    body = ["Files:", ""] + _table(["file", "có", "số sheet"], rows)
    body += ["Sheet spec 4 nêu mà chưa có:", ""] + _table(["file", "sheet"], missing, 60)
    body += ["Sheet rỗng (0 dòng, không có dòng CHUA_AP):", ""] + _table(["file", "sheet"], empty)
    body += [f"Sheet chỉ có dòng đánh dấu (CHUA_AP / NEED_CODE_CHECK / KHONG_CO): {marker_only}.", ""]
    return status, gaps, body


def _src_files(schema_row: dict) -> frozenset:
    """The source files a column reads (Schema.nguon_khoa '<file>: <path>; ...')."""
    text = schema_row.get("nguon_khoa", "") if schema_row else ""
    return frozenset(p.split(":")[0].strip() for p in text.split(";") if ":" in p)


def cross_file(books):
    """(id, column) pairs holding two different values in two files. Two cells are the same datum when one sits in an
    input_<name> sheet (a copy, spec 2.2) or both columns read the same source file (Schema.nguon_khoa); a column name
    reused for another quantity (Xe.class = the unit class, Validator_model.class = the model checker's class) is not."""
    schema = {(x["file"], x["sheet"], x["cot"]): x for x in _dicts(books, "00_chi_muc", "Schema")}
    vals = collections.defaultdict(list)
    for fid, sheets in books.items():
        if fid == "00_chi_muc":
            continue
        for s, (h, rows) in sheets.items():
            cols = {c: _src_files(schema.get((fid, s, c))) for c in compared_cols(h) if c not in GENERIC_COLS}
            idx = [(i, c) for i, c in enumerate(h) if c in cols]
            for r in rows:
                for i, c in idx:
                    v = r[i] if i < len(r) else ""
                    if v != "" and not MARKER.match(v):
                        vals[(r[0], c)].append((fid, s, v, cols[c]))
    out = []
    for (rid, c), cells in sorted(vals.items()):
        if len({x[0] for x in cells}) < 2:
            continue
        bad = set()
        for i, (fa, sa, va, srca) in enumerate(cells):
            for fb, sb, vb, srcb in cells[i + 1:]:
                if fa == fb or not (sa.startswith("input_") or sb.startswith("input_") or (srca & srcb)):
                    continue
                x, y = number(va), number(vb)
                if va != vb and not (x is not None and y is not None and math.isclose(x, y, rel_tol=1e-9)):
                    bad |= {f"{fa}/{sa}={va}", f"{fb}/{sb}={vb}"}
        if bad:
            out.append([rid, c, ";".join(sorted(bad)), any("/input_" in x for x in bad)])
    return out


def check2(books, run_out: str):
    nd = _dicts(books, "00_chi_muc", "Nguon_du_lieu")
    unmapped = sum(int(x.get("so_la_chua_anh_xa") or 0) for x in nd)
    pending = sum(int(x.get("so_la_cho") or 0) for x in nd)
    leaves = sum(int(x.get("so_la") or 0) for x in nd)
    twice = [x["noi_dung"] for x in _dicts(books, "00_chi_muc", "Van_de") if "ánh xạ hai lần" in x.get("noi_dung", "")]
    fk = _dicts(books, "00_chi_muc", "Khoa_ngoai")
    fk_counts = collections.Counter(x.get("ket_qua", "") for x in fk)
    fk_fail = [[x["file"], x["sheet"], x["cot"], x["so_loi"], x["vi_du_loi"]] for x in fk if x.get("ket_qua") == "FAIL"]
    conflicts = cross_file(books)
    cov_ok = unmapped == 0 and not twice
    gaps = []
    if not cov_ok:
        gaps.append(f"độ phủ: {unmapped} lá chưa ánh xạ, {len(twice)} lá ánh xạ hai lần")
    if fk_fail:
        gaps.append(f"{len(fk_fail)} khóa ngoại FAIL")
    if conflicts:
        gaps.append(f"{len(conflicts)} cặp (id, cột) có hai giá trị khác nhau giữa các file")
    status = "DAT" if not gaps else "CHUA_DAT"
    body = [f"Nguồn {len(nd)}, lá {leaves}; chưa ánh xạ {unmapped}; ánh xạ hai lần {len(twice)}; chờ file chưa dựng {pending} "
            f"(Cho_anh_xa: file 13, lượt 10). Khóa ngoại: {dict(sorted(fk_counts.items()))}.", ""]
    body += ["Khóa ngoại FAIL:", ""] + _table(["file", "sheet", "cột", "số lỗi", "ví dụ"], fk_fail)
    body += ["Cùng (id, cột), giá trị khác nhau giữa các file (bỏ cột chung: " + ", ".join(sorted(GENERIC_COLS))
             + ", raw_json, nguon, khối _truoc / _sau):", ""]
    body += _table(["id", "cột", "giá trị theo file/sheet", "có sheet input_"], conflicts, 60)
    return status, gaps, body, cov_ok, not fk_fail


def check3(books):
    def ids(fid, s):
        h, rows = books.get(fid, {}).get(s, ([], []))
        return [r[0] for r in rows]

    bal, camp = _json(BAL) or {}, _json(CAMP) or {}
    maps = len(list((repo.ROOT / "Assets/MachineBrigade/Resources/Data/maps").glob("*.json")))
    glb = len(list((repo.ROOT / "Assets/MachineBrigade/Resources/Models").rglob("*.glb")))
    clips = len([p for p in (repo.ROOT / "Assets/MachineBrigade/Resources/Audio").rglob("*")
                 if p.suffix.lower() in (".ogg", ".wav", ".mp3")])
    vehicles_split = ["02_phuong_tien/Xe", "04_can_cu_thap/Thap", "04_can_cu_thap/Tuong", "04_can_cu_thap/Nha_chinh",
                      "04_can_cu_thap/Mo_dun_tien_ich", "03_boss/Boss"]
    split_rows = sum(len(ids(*x.split("/"))) for x in vehicles_split)
    ents = [
        ("vũ khí", "01_vu_khi_dan/Vu_khi", len(bal.get("weapons", [])) + len((bal.get("secondRounds") or {}).get("rounds", [])),
         "", "balance.json weapons + secondRounds.rounds"),
        ("xe", "02_phuong_tien/Xe", None, "", f"vehicles[] ({len(bal.get('vehicles', []))}) chia vào {len(vehicles_split)} sheet: "
         f"tổng {split_rows}"),
        ("boss", "03_boss/Boss", None, 41, ""),
        ("tháp", "04_can_cu_thap/Thap", None, "", "phần của vehicles[]"),
        ("thẻ hỗ trợ", "02_phuong_tien/The_ho_tro", len(bal.get("supports", [])), "", "balance.json supports"),
        ("nhiệm vụ", "07_chien_dich_cot_truyen/Nhiem_vu", len(camp.get("missions", [])), 193, "campaign.json missions"),
        ("chương", "07_chien_dich_cot_truyen/Chuong", len(camp.get("chapters", [])), 15, "campaign.json chapters"),
        ("bộ bài game", "07_chien_dich_cot_truyen/Bo_bai_game", None, 23, ""),
        ("bản đồ", "08_ban_do/Ban_do", maps, 50, "maps/*.json: 25 bản đồ x 4 biến thể"),
        ("commander", "02_phuong_tien/Commander", None, "", "Commanders.cs"),
        ("model", "10_model_tai_san/Model", glb, "", "Resources/Models/**/*.glb"),
        ("clip", "09_hieu_ung_am_thanh/Am_thanh", clips, "", "Resources/Audio/** ogg / wav (Am_thanh có thêm dòng bank / nhạc nếu chênh)"),
    ]
    rows, gaps = [], []
    for name, where, src_n, spec_n, note in ents:
        fid, s = where.split("/")
        got = ids(fid, s)
        dup = [k for k, n in collections.Counter(got).items() if n > 1]
        delta = "" if src_n is None else len(got) - src_n
        rows.append([name, where, len(got), "" if src_n is None else src_n, delta, spec_n, len(dup), note])
        if dup:
            gaps.append(f"{where}: {len(dup)} id trùng")
        if src_n is not None and delta not in (0, "") and name != "clip":
            gaps.append(f"{where}: {len(got)} dòng, nguồn {src_n}")
    if split_rows != len(bal.get("vehicles", [])):
        gaps.append(f"vehicles[] {len(bal.get('vehicles', []))} != tổng sheet {split_rows}")
    dup_any = []
    for fid, sheets in sorted(books.items()):
        for s, (h, r) in sorted(sheets.items()):
            c = collections.Counter(x[0] for x in r)
            n = sum(1 for v in c.values() if v > 1)
            if n:
                dup_any.append([fid, s, n])
    if dup_any:
        gaps.append(f"{len(dup_any)} sheet có id trùng")
    status = "DAT" if not gaps else "CHUA_DAT"
    body = _table(["thực thể", "sheet", "số dòng", "số trong nguồn", "chênh", "số spec nêu", "id trùng", "ghi chú"], rows)
    body += ["Bản đồ: spec nêu 50; dữ liệu có 25 bản đồ x 4 biến thể = 100 file (mỗi file một dòng).", ""]
    body += ["Sheet có id trùng (mọi file):", ""] + _table(["file", "sheet", "số id trùng"], dup_any)
    return status, gaps, body


def check4(books):
    schema = _dicts(books, "00_chi_muc", "Schema")
    formulas = [x for x in schema if x.get("cong_thuc")]
    game_cols = [x for x in schema if x.get("cot", "").endswith("_game")]
    inputs = [(fid, s) for fid, sheets in books.items() for s in sheets if s.startswith("input_")]
    conflicts = [c for c in cross_file(books) if c[3]]
    gaps = []
    if not formulas:
        gaps.append("chưa có cột công thức (lớp B: lượt 5)")
    no_game = []
    by_sheet = collections.defaultdict(set)
    for x in game_cols:
        by_sheet[(x["file"], x["sheet"])].add(x["cot"][:-5])
    for x in formulas:
        if x["cot"] not in by_sheet[(x["file"], x["sheet"])]:
            no_game.append([x["file"], x["sheet"], x["cot"]])
    if no_game:
        gaps.append(f"{len(no_game)} cột công thức không có cột _game")
    if conflicts:
        gaps.append(f"{len(conflicts)} ô input_ khác file nguồn")
    status = "CHUA_AP" if not formulas else ("DAT" if not gaps else "CHUA_DAT")
    body = [f"Cột công thức (Schema.cong_thuc): {len(formulas)}; cột _game: {len(game_cols)}; sheet input_: {len(inputs)}.",
            "So công thức với _game (sai số 1e-6) là test của lượt 5; ở đây: mỗi cột công thức có cột _game, và mọi ô "
            "input_ bằng giá trị ở file nguồn (cùng id, cùng cột).", ""]
    body += ["Cột công thức thiếu _game:", ""] + _table(["file", "sheet", "cột"], no_game)
    body += ["Ô input_ khác nguồn:", ""] + _table(["id", "cột", "giá trị", "input"], conflicts)
    return status, gaps, body


def check5(books, out: Path):
    md_dir, pdf_dir = out / "md", out / "pdf"
    if not md_dir.is_dir():
        return "CHUA_AP", ["md / pdf chưa dựng (lượt 6)"], ["md/ và pdf/ chưa có: lượt 6 dựng. Khi có, kiểm này lấy mẫu "
                                                             f"{SAMPLE} ô số (seed {SEED}) từ các bảng md có dòng "
                                                             "'Sheet: <file>/<sheet>' và so với csv.", ""]
    cells = []
    for f in sorted(md_dir.glob("*.md")):
        lines = f.read_text("utf-8").splitlines()
        where = None
        i = 0
        while i < len(lines):
            m = re.search(r"Sheet:\s*([0-9]{2}_[a-z_0-9]+)/([A-Za-z0-9_]+)", lines[i])
            if m:
                where = (m.group(1), m.group(2))
            if where and lines[i].startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1]):
                header = [x.strip() for x in lines[i].strip("|").split("|")]
                i += 2
                while i < len(lines) and lines[i].startswith("|"):
                    vals = [x.strip() for x in lines[i].strip("|").split("|")]
                    for c, v in zip(header[1:], vals[1:]):
                        if number(v) is not None:
                            cells.append((where[0], where[1], vals[0], c, v, f.name))
                    i += 1
                where = None
                continue
            i += 1
    rng = random.Random(SEED)
    sample = rng.sample(cells, min(SAMPLE, len(cells))) if cells else []
    bad = []
    for fid, s, rid, c, v, mdname in sample:
        h, rows = books.get(fid, {}).get(s, ([], []))
        rec = next((dict(zip(h, r)) for r in rows if r and r[0] == rid), None)
        x = None if rec is None else number(rec.get(c, "") or "")
        if x is None or not math.isclose(x, number(v), rel_tol=1e-6, abs_tol=1e-9):
            bad.append([mdname, f"{fid}/{s}", rid, c, v, "" if rec is None else rec.get(c, "")])
    pdf_note = "pdf: chưa có" if not pdf_dir.is_dir() else "pdf: sinh từ cùng md (spec 6), không đọc riêng"
    status = "DAT" if sample and not bad else "CHUA_DAT"
    gaps = [] if status == "DAT" else [f"{len(bad)} / {len(sample)} ô md khác csv" if sample else "md không có bảng số"]
    body = [f"Ô số trong bảng md: {len(cells)}; mẫu {len(sample)} (seed {SEED}); khác csv: {len(bad)}. {pdf_note}.", ""]
    body += _table(["md", "sheet", "id", "cột", "md", "csv"], bad)
    return status, gaps, body


def check6(books):
    schema = _dicts(books, "00_chi_muc", "Schema")
    kinds = {(x["file"], x["sheet"], x["cot"]): x for x in schema}
    unit_cells, num_text, req_empty = [], collections.Counter(), collections.Counter()
    for fid, sheets in sorted(books.items()):
        for s, (h, rows) in sorted(sheets.items()):
            meta = [kinds.get((fid, s, c), {}) for c in h]
            for r in rows:
                for c, v, m in zip(h, r, meta):
                    if c in ("raw_json", "nguon"):
                        continue
                    numeric = m.get("don_vi") or m.get("kieu", "") in ("int", "number") or m.get("kieu", "").startswith("mixed")
                    if v and numeric and UNIT_TEXT.match(v):  # a name such as Ho_vu_khi.ten "20 mm" is text, not a number
                        unit_cells.append([fid, s, r[0], c, v])
                    if m.get("kieu") in ("int", "number") and v and number(v) is None and not MARKER.match(v):
                        num_text[(fid, s, c)] += 1
                    if m.get("bat_buoc") == "TRUE" and v == "":
                        req_empty[(fid, s, c)] += 1
    gaps = []
    if unit_cells:
        gaps.append(f"{len(unit_cells)} ô ghi số kèm chữ đơn vị")
    if num_text:
        gaps.append(f"{len(num_text)} cột số có ô chữ")
    if req_empty:
        gaps.append(f"{len(req_empty)} cột bắt buộc có ô trống")
    status = "DAT" if not gaps else "CHUA_DAT"
    body = ["Ô số kèm đơn vị (cột số hoặc cột có đơn vị; cả ô là 'số đơn vị'):", ""] + _table(["file", "sheet", "id", "cột", "giá trị"], unit_cells)
    body += ["Cột kiểu số (Schema int / number) có ô chữ không phải dấu đánh dấu:", ""]
    body += _table(["file", "sheet", "cột", "số ô"], [[*k, n] for k, n in sorted(num_text.items())])
    body += ["Cột bắt buộc (Schema bat_buoc) có ô trống:", ""]
    body += _table(["file", "sheet", "cột", "số ô"], [[*k, n] for k, n in sorted(req_empty.items())])
    return status, gaps, body


def check7(out: Path, rerun: Path):
    a, b = _hashes(out), _hashes(rerun)
    keys = sorted((set(a) | set(b)) - NOT_DETERMINISTIC)
    diff = [[k, "có" if k in a else "không", "có" if k in b else "không"] for k in keys if a.get(k) != b.get(k)]
    status = "DAT" if not diff else "CHUA_DAT"
    gaps = [] if not diff else [f"{len(diff)} file khác giữa hai lần xuất"]
    body = [f"Hai lần xuất (hai tiến trình riêng) trên cùng dữ liệu: {len(keys)} file so băm sha256 (trừ README.md, "
            f"MANIFEST.json, SELF_CHECK.md); khác: {len(diff)}.", ""] + _table(["file", "lần 1", "lần 2"], diff)
    return status, gaps, body


def check8(books):
    kx = [[x["id"], x["nguon_mau"], x["mau_duong_dan"], x["ly_do"], x["so_la"]] for x in _dicts(books, "00_chi_muc", "Khong_xuat")]
    nk = [[x["id"], x.get("ly_do", "")] for x in _dicts(books, "00_chi_muc", "Nguon_khong_doc_duoc")]
    ncc = collections.Counter()
    for fid, sheets in sorted(books.items()):
        if fid == "00_chi_muc":
            continue
        for s, (h, rows) in sorted(sheets.items()):
            for r in rows:
                for c, v in zip(h, r):
                    if v == "NEED_CODE_CHECK":
                        ncc[(fid, s, c)] += 1
    body = [f"Khong_xuat: {len(kx)} luật; nguồn không đọc được: {len(nk)}; cột có NEED_CODE_CHECK: {len(ncc)} "
            f"({sum(ncc.values())} ô).", ""]
    body += ["Khong_xuat (mẫu đường dẫn, lý do, số lá):", ""] + _table(["id", "nguồn", "mẫu", "lý do", "số lá"], kx, 80)
    body += ["Nguồn không đọc được:", ""] + _table(["nguồn", "lý do"], nk)
    body += ["Cột NEED_CODE_CHECK:", ""] + _table(["file", "sheet", "cột", "số ô"], [[*k, n] for k, n in sorted(ncc.items())], 200)
    return "DAT", [], body


def check9(out: Path, extra: list[Path]):
    hits, n = [], 0
    for root in [out] + extra:
        fs = secrets.files(root)
        n += len(fs)
        for p in fs:
            label = root.name + "/" + p.relative_to(root).as_posix()
            secrets.scan_file(p, label, hits)
    status = "DAT" if not hits else "CHUA_DAT"
    gaps = [] if not hits else [f"{len(hits)} chuỗi khớp mẫu bí mật"]
    body = [f"Quét {n} file (mọi file của bộ xuất" + (" và các thư mục diff_*" if extra else "") + "; xlsx từng phần, pdf "
            "giải nén luồng, ảnh đọc thô): khóa API (Google, AWS, GitHub, Slack, sk-), khóa riêng, mật khẩu / keystore, "
            "JWT, bearer, api_key=, email, đường dẫn tuyệt đối máy cá nhân, tên người dùng máy.", ""]
    body += _table(["file", "mẫu", "chuỗi (cắt)"], [[a, b, c] for a, b, c in hits])
    return status, gaps, body


# ----------------------------------------------------------------------------------------------------------------- main
TITLES = [
    "1. Mọi file và sheet của mục 4 tồn tại; sheet rỗng chỉ khi có dòng CHUA_AP",
    "2. Độ phủ khóa, khóa ngoại, không (id, cột) nào hai giá trị giữa các file",
    "3. Mỗi id đúng một dòng; số dòng khớp dữ liệu",
    "4. Công thức khớp mã game; input chép khớp nguồn",
    f"5. Số trong Excel khớp md và pdf (mẫu {SAMPLE} ô, seed {SEED})",
    "6. Không ô số chứa chữ đơn vị; không ô trống ở cột bắt buộc",
    "7. Hai lần xuất liên tiếp cho file giống hệt",
    "8. Thứ không xuất và lý do; cột NEED_CODE_CHECK",
    "9. Không có bí mật trong bất kỳ file",
]


def main(args, ex) -> int:
    commit, date = repo.head_commit(), repo.head_date()
    out = Path(args.out) if args.out else repo.ROOT / "Docs" / "export" / f"{date}_{commit}"
    if not out.is_absolute():
        out = repo.ROOT / out
    base = args.base or ""
    here = Path(ex.__file__).resolve().parent
    print(f"check: export 1 -> {out.name}")
    code1, log1 = _run_export(here, out, base)
    print("\n".join(line for line in log1.splitlines() if line.startswith(("sources ", "foreign keys", "UNMAPPED", "SECRET"))))
    if not (out / "csv").is_dir():
        print(log1[-2000:])
        return 1
    work = Path(tempfile.mkdtemp(prefix="mb_export_check_"))
    try:
        print("check: export 2 (determinism) -> temp")
        _run_export(here, work / out.name, base)
        books, _, _ = load_export(out)
        diffs = sorted(p for p in (repo.ROOT / "Docs" / "export").glob("diff_*") if p.is_dir()) if not args.out else []
        results = [
            check1(books, ex.PLANNED),
            check2(books, log1),
            check3(books),
            check4(books),
            check5(books, out),
            check6(books),
            check7(out, work / out.name),
            check8(books),
            check9(out, diffs),
        ]
    finally:
        shutil.rmtree(work, ignore_errors=True)
    cov_ok, fk_ok = results[1][3], results[1][4]
    ci = {"coverage": cov_ok, "foreign_keys": fk_ok, "determinism": results[6][0] == "DAT", "secrets": results[8][0] == "DAT"}
    lines = ["# Tự kiểm bộ xuất (spec 9)", "",
             f"Commit {commit}, ngày {date}, bản gốc so sánh `{base or '(không)'}`. Lệnh: `python Tools/export/export.py check`.",
             "Trạng thái: DAT = đạt; CHUA_DAT = có thiếu (liệt kê); CHUA_AP = phần của lượt sau. CI (.github/workflows/"
             "export.yml) chặn khi độ phủ, khóa ngoại, đồng nhất hoặc bí mật không đạt.", "",
             "| # | Kiểm | Trạng thái | Thiếu |", "|---|---|---|---|"]
    for title, r in zip(TITLES, results):
        lines.append(f"| {title.split('.')[0]} | {_md(title.split('. ', 1)[1])} | {r[0]} | {_md('; '.join(r[1]), 600)} |")
    lines += ["", "CI: " + ", ".join(f"{k} {'DAT' if v else 'CHUA_DAT'}" for k, v in ci.items()), "",
              "Lớp tham chiếu (spec 12.6): CHUA_AP:prompt_xuat_luot10 (file 13 và sheet <tên>_tham_chieu chưa dựng; "
              "diff đã so mọi sheet nên sẽ báo thay đổi ở sheet tham chiếu).", ""]
    for title, r in zip(TITLES, results):
        lines += [f"## {title}", "", f"Trạng thái: {r[0]}.", ""] + r[2]
    text = "\n".join(lines) + "\n"
    (out / "00_chi_muc" / "SELF_CHECK.md").write_bytes(text.encode("utf-8"))
    _manifest_add(out, "00_chi_muc/SELF_CHECK.md")
    print(f"check: wrote {out.name}/00_chi_muc/SELF_CHECK.md")
    for title, r in zip(TITLES, results):
        print(f"  {title.split('.')[0]}: {r[0]}" + (f"  ({'; '.join(r[1])})" if r[1] else ""))
    print("  CI: " + ", ".join(f"{k} {'ok' if v else 'FAIL'}" for k, v in ci.items()))
    return 0 if all(ci.values()) else 1


def _manifest_add(out: Path, rel: str):
    mf = out / "00_chi_muc" / "MANIFEST.json"
    if not mf.exists():
        return
    m = json.loads(mf.read_text("utf-8"))
    p = out / rel
    files = [f for f in m.get("files", []) if f["path"] != rel]
    files.append({"path": rel, "bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    m["files"] = sorted(files, key=lambda f: f["path"])
    mf.write_bytes(json.dumps(m, ensure_ascii=False, indent=1).encode("utf-8"))
