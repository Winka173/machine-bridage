"""12_he_thong_trang_thai, layer A: prompt status, every DECISIONS heading, items waiting on the owner, code checks
(C01-C16 and Docs/checks), the field map, manifest results, tests, validators and their last results, old measurements,
save migration, the unit sheet of the documents, unclassified items; the code-constant scan is pass 5."""
from __future__ import annotations

import hashlib
import re

from core import secrets
from core.model import chua_ap
from core.repo import ROOT

from . import _lane_c as C

FILE_ID = "12_he_thong_trang_thai"
TITLE = "Hệ thống và trạng thái"
DESC = "Trạng thái prompt, DECISIONS, chờ quyết, kiểm tra mã, bản đồ trường dữ liệu, kết quả áp manifest, test, validator, " \
       "lịch sử đo, chuyển đổi save, bảng đơn vị tài liệu, chưa phân loại; Hang_so_trong_ma ở lượt 5"

PROMPTS = "Docs/prompts/README.md"
DECISIONS = "Docs/DECISIONS.md"
FIELD_MAP = "Docs/balance_field_map.md"
REPORT29 = "Docs/balance/report_p29.md"
APPLY_STATE = "Docs/balance/apply_state_p29.json"
VALIDATE = "Docs/checks/fix_validate.json"
CHECKS = "Docs/checks/"
TESTS = "Assets/MachineBrigade/Tests/"
UNIT_SHEET = "Tools/docs/unit_sheet.json"
NOT_RUN = "KHONG_CHAY"  # owner rule 30/09: no test runs until the owner approves
REDACTED = "<DUONG_DAN_MAY_CA_NHAN>"
WAIT = re.compile(r"\bHOLD\b|\bDECIDE\b|waits? (?:for|on) the owner|owner'?s? (?:word|call|decision|ask)|chờ chủ dự án|"
                  r"cần chủ dự án|needs? the owner", re.I)


def _text(path: str) -> str:
    p = ROOT / path
    return p.read_text("utf-8", errors="replace") if p.exists() else ""


def _redact(s: str) -> str:
    """Docs text with absolute local paths and the local user name removed (spec 8)."""
    for name, rx in secrets.PATTERNS:
        if name in ("windows_abs_path", "unix_home_path"):
            s = re.sub(rx.pattern + r"[^\s`'\")|]*", REDACTED, s, flags=rx.flags)
    for user in secrets._local_names():
        s = re.sub(rf"(?<![A-Za-z]){re.escape(user)}(?![A-Za-z])", "<USER>", s)
    return s


def _state_of(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ("skipped", "on hold", "queued", "saved, queued", "waits")) and "done" not in t:
        return "Chua"
    if any(w in t for w in ("started", "reduced", "partly", "but the", "in progress")):
        return "Mot_phan"
    if "done" in t or "standing" in t:
        return "Da_chay"
    return "Chua"


def build(ctx):
    book = ctx.book(FILE_ID, TITLE, DESC)
    ctx.exclude(VALIDATE, "models.summary.scanDir", "bảo mật: đường dẫn tuyệt đối máy cá nhân (spec 8)", origin="domains/d12")

    # ------------------------------------------------------------------ Trang_thai_prompt
    tp = book.sheet("Trang_thai_prompt", "Trạng thái prompt", "Docs/prompts/README.md: mỗi dòng bảng prompt (chủ đề, trạng thái "
                    "nguyên văn, trạng thái suy ra Da_chay / Mot_phan / Chua), file prompt")
    tp.col("chu_de", meaning="chủ đề")
    tp.col("trang_thai_nguyen_van", meaning="cột State nguyên văn")
    tp.col("trang_thai", meaning="suy từ chữ của cột State", enum=["Da_chay", "Mot_phan", "Chua"])
    tp.col("file_prompt", meaning="file prompt trong Docs/prompts (ngăn ';')")
    tp.col("commit_dau_cuoi", meaning="commit đầu / cuối của prompt")
    tp.col("test", meaning="kết quả test (KHONG_CHAY: luật chủ dự án 30/09, không chạy test)")
    files = sorted(p.name for p in (ROOT / "Docs/prompts").glob("*") if p.is_file())
    for line, header, rows in C.md_tables(_text(PROMPTS)):
        if not header or header[0].lower() != "prompt":
            continue
        for ln, cells in rows:
            pid = C.clean_md(cells[0])
            r = tp.row(pid, f"{PROMPTS}:{ln}")
            r.set("chu_de", _redact(C.clean_md(cells[1])) if len(cells) > 1 else "")
            state = " | ".join(C.clean_md(c) for c in cells[2:])
            r.set("trang_thai_nguyen_van", _redact(state))
            r.set("trang_thai", _state_of(state))
            nums = [int(x) for x in re.findall(r"\d+", pid)]
            if " to " in pid and len(nums) == 2:
                nums = list(range(nums[0], nums[1] + 1))
            r.set("file_prompt", ";".join(f for f in files for n in nums if re.fullmatch(rf"prompt{n:02d}(_v\d+)?_\w+\.(txt|md)", f)))
            r.set("commit_dau_cuoi", chua_ap("xuat_luot8"))
            r.set("test", NOT_RUN)
    for f in files:
        if not re.fullmatch(r"prompt\d+.*", f) and f != "README.md":
            r = tp.row(f, f"Docs/prompts/{f}")
            r.set("chu_de", "spec ngoài bảng prompt")
            r.set("file_prompt", f)
            r.set("trang_thai", "Chua")
            r.set("trang_thai_nguyen_van", "")
            r.set("commit_dau_cuoi", chua_ap("xuat_luot8"))
            r.set("test", NOT_RUN)

    # ------------------------------------------------------------------ DECISIONS, Cho_quyet
    dc = book.sheet("DECISIONS", "DECISIONS", "Docs/DECISIONS.md: mọi tiêu đề mục (## và ###) một dòng (dòng, cấp, mục cha)")
    dc.col("cap", meaning="2 = ##, 3 = ###")
    dc.col("tieu_de", meaning="tiêu đề")
    dc.col("dong", meaning="số dòng trong Docs/DECISIONS.md")
    dc.col("muc_cha", meaning="mục ## chứa nó", fk=["12_he_thong_trang_thai/DECISIONS"])
    cq = book.sheet("Cho_quyet", "Chờ quyết", "Dòng của Docs/DECISIONS.md có HOLD / DECIDE / chờ chủ dự án (tìm bằng mẫu chữ)")
    cq.col("dong", meaning="số dòng")
    cq.col("muc", meaning="mục chứa dòng", fk=["12_he_thong_trang_thai/DECISIONS"])
    cq.col("noi_dung", meaning="nội dung dòng (cắt 400 ký tự)")
    cur2 = cur = ""
    n = q = 0
    for i, line in enumerate(_text(DECISIONS).splitlines(), 1):
        m = re.match(r"^(#{2,3})\s+(.*)$", line)
        if m:
            n += 1
            rid = f"D{n:04d}"
            r = dc.row(rid, f"{DECISIONS}:{i}")
            r.set("cap", len(m.group(1)))
            r.set("tieu_de", _redact(m.group(2).strip()))
            r.set("dong", i)
            if len(m.group(1)) == 2:
                cur2 = rid
                r.set("muc_cha", "")
            else:
                r.set("muc_cha", cur2)
            cur = rid
            continue
        if WAIT.search(line):
            q += 1
            r = cq.row(f"Q{q:04d}", f"{DECISIONS}:{i}")
            r.set("dong", i)
            r.set("muc", cur)
            r.set("noi_dung", _redact(line.strip())[:400])

    # ------------------------------------------------------------------ Kiem_tra_ma (C01-C16), Kiem_tra_file (Docs/checks)
    km = book.sheet("Kiem_tra_ma", "Kiểm tra mã (CHECK)", "Docs/balance/report_p29.md: kết quả CHECK C01-C16 của prompt 29 "
                    "(bảng Checks; C02 / C04 / C08 / C14 ghi 'Not done')")
    km.col("ten", meaning="tên CHECK")
    km.col("ket_qua", meaning="kết quả")
    km.col("trang_thai", meaning="xong / chua_lam", enum=["xong", "chua_lam"])
    km.col("file", meaning="file chi tiết")
    rep = _text(REPORT29)
    for line, header, rows in C.md_tables(rep):
        if not header or header[0].lower() != "check":
            continue
        for ln, cells in rows:
            m = re.match(r"(C\d+)\s*(.*)", C.clean_md(cells[0]))
            if not m:
                continue
            r = km.row(m.group(1), f"{REPORT29}:{ln}")
            r.set("ten", m.group(2))
            r.set("ket_qua", _redact(C.clean_md(cells[1])) if len(cells) > 1 else "")
            r.set("trang_thai", "xong")
            r.set("file", C.clean_md(cells[2]) if len(cells) > 2 else "")
    nd = re.search(r"Not done[^\n]*(?:\n(?!\n)[^\n]*)*", rep)
    if nd:
        ln = rep[: nd.start()].count("\n") + 1
        for cid, what in re.findall(r"\*\*(C\d+)\*\*\s*\(([^)]*)\)", nd.group(0)):
            if cid not in km.rows:
                r = km.row(cid, f"{REPORT29}:{ln}")
                r.set("ten", " ".join(what.split()))
                r.set("ket_qua", "")
                r.set("trang_thai", "chua_lam")
                r.set("file", "")
    kf = book.sheet("Kiem_tra_file", "Kiểm tra: file báo cáo", "Docs/checks/*: mỗi file báo cáo kiểm (precheck, audit) một dòng")
    for c, m in (("loai", "đuôi file"), ("kich_thuoc_byte", "cỡ file"), ("tieu_de", "tiêu đề đầu (md) / khóa gốc (json)"),
                 ("sha256", "hash nội dung (LF)")):
        kf.col(c, meaning=m)
    for p in sorted((ROOT / CHECKS).glob("*")):
        if not p.is_file():
            continue
        rel = CHECKS + p.name
        r = kf.row(p.name, rel)
        r.set("loai", p.suffix.lstrip("."))
        data = p.read_bytes().replace(b"\r\n", b"\n")
        r.set("kich_thuoc_byte", len(data))
        txt = data.decode("utf-8", "replace")
        head = next((l.lstrip("# ").strip() for l in txt.splitlines() if l.startswith("#")), "") if p.suffix == ".md" else ""
        if p.suffix == ".json":
            head = ";".join(re.findall(r'^ ?"(\w+)"\s*:', txt, re.M)[:10])
        r.set("tieu_de", _redact(head))
        r.set("sha256", hashlib.sha256(data).hexdigest())

    # ------------------------------------------------------------------ Truong_du_lieu (field map)
    tf = book.sheet("Truong_du_lieu", "Bản đồ trường dữ liệu", "Docs/balance_field_map.md: field_path logic của Manifest -> khóa "
                    "thật (đọc, ghi, trạng thái)")
    for line, header, rows in C.md_tables(_text(FIELD_MAP)):
        if not header or header[0].lower() != "field_path":
            continue
        cols = [re.sub(r"\W+", "_", h.lower()).strip("_") for h in header]
        for k, (ln, cells) in enumerate(rows):
            r = tf.row(f"F{k + 1:03d}", f"{FIELD_MAP}:{ln}")
            for c, v in zip(cols, cells):
                r.set(c, _redact(C.clean_md(v)))
        break

    # ------------------------------------------------------------------ Manifest_ap
    ma = book.sheet("Manifest_ap", "Kết quả áp manifest (prompt 29)", "Docs/balance/report_p29.md bảng Bundles: kết quả OK / "
                    "ALREADY_APPLIED / CONFLICT / BLOCKED / SKIPPED, số gói, gói")
    for line, header, rows in C.md_tables(rep):
        if not header or header[0].lower() != "outcome":
            continue
        for ln, cells in rows:
            r = ma.row(C.clean_md(cells[0]), f"{REPORT29}:{ln}")
            r.set("so_goi", C.clean_md(cells[1]) if len(cells) > 1 else "")
            r.set("goi", _redact(C.clean_md(cells[2])) if len(cells) > 2 else "")
    st = C.docs_json(ctx, APPLY_STATE)
    if st is not None:
        mg = book.sheet("Manifest_ap_goi", "Manifest: gói đã áp", "Docs/balance/apply_state_p29.json: mỗi gói đã áp (bundle id)")
        mg.col("goi", meaning="bundle id")
        for i, b in enumerate(st.data if isinstance(st.data, list) else []):
            r = mg.row(b, C.nguon(APPLY_STATE, (i,)))
            r.set("goi", b, APPLY_STATE, (i,))

    # ------------------------------------------------------------------ Test (+ the scenario JSON)
    te = book.sheet("Test", "Test", "Assets/MachineBrigade/Tests: mỗi file test một dòng (số [Test], lớp); kết quả: KHONG_CHAY "
                    "(luật chủ dự án 30/09: không chạy test tới khi chủ dự án cho)")
    for c in ("nhom", "so_test", "lop", "ket_qua"):
        te.col(c)
    for p in sorted((ROOT / TESTS).rglob("*.cs")):
        rel = p.relative_to(ROOT).as_posix()
        txt = p.read_text("utf-8-sig", errors="replace")
        r = te.row(rel[len(TESTS):], rel)
        r.set("nhom", rel[len(TESTS):].split("/")[0])
        r.set("so_test", len(re.findall(r"\[(?:Test|UnityTest|TestCase)\b", txt)))
        r.set("lop", ";".join(sorted(set(re.findall(r"\bclass\s+(\w+)", txt)))))
        r.set("ket_qua", NOT_RUN)
    tk = book.sheet("Test_kich_ban", "Test: kịch bản", "Tests/EditMode/Scenarios/*.json: kịch bản sandbox (bên, quân, điều kiện kiểm)")
    for sid in sorted(s for s in ctx.sources if s.startswith(TESTS) and s.endswith(".json")):
        rec = ctx.data(sid)
        r = tk.row(sid.rsplit("/", 1)[-1][:-5], sid, raw=rec)
        r.flatten(rec, sid, (), children={k: C.child(book.sheets.get(f"Test_kich_ban_{k}") or book.sheet(
            f"Test_kich_ban_{k}", f"Kịch bản: {k}", f"{k}[]", parent=tk)) for k, v in rec.items()
            if isinstance(v, list) and any(isinstance(x, dict) for x in v)})

    # ------------------------------------------------------------------ Validator (+ fix_validate.json)
    va = book.sheet("Validator", "Validator", "Công cụ kiểm của Tools/ (validate / check / audit): mục đích (docstring đầu), "
                    "báo cáo; kết quả gần nhất của fix_validate.py ở Validator_ket_qua / _model / _vu_khi")
    va.col("muc_dich", meaning="dòng đầu docstring")
    va.col("lan_chay", meaning="KHONG_CHAY trong lượt xuất (chỉ đọc kết quả có sẵn)")
    for p in sorted((ROOT / "Tools").rglob("*.py")):
        if not re.search(r"valid|check|audit", p.name) or "export" in p.parts:
            continue
        rel = p.relative_to(ROOT).as_posix()
        txt = p.read_text("utf-8", errors="replace")
        m = re.search(r'^\s*(?:#![^\n]*\n)?\s*(?:"""|\'\'\')\s*([^\n]*)', txt)
        r = va.row(rel, rel)
        r.set("muc_dich", _redact(m.group(1).strip()) if m else "")
        r.set("lan_chay", NOT_RUN)
    fv = C.docs_json(ctx, VALIDATE)
    if fv is not None:
        data = fv.data
        models = data.get("models") or {}
        vm = book.sheet("Validator_model", "Validator: điểm model", "fix_validate.json models.grades: ngân sách, trạng thái, lớp, "
                        "LOD1, bộ phận thiếu, điểm tĩnh / hình")
        vm.col("model", fk=["10_model_tai_san/Model"])
        for r, _x, _p in C.keyed(vm, models.get("grades"), VALIDATE, ("models", "grades")):
            r.set("model", r.id if r.id in ctx.books["10_model_tai_san"].sheets["Model"].rows else "")
        vw = book.sheet("Validator_vu_khi", "Validator: vũ khí", "fix_validate.json weapons: chu kỳ, cờ nhịp, số phát, lý do; "
                        "recordedRateFlags: lý do đã ghi")
        vw.col("vu_khi", fk=["01_vu_khi_dan/Vu_khi"])
        vw.col("ly_do_da_ghi", meaning="recordedRateFlags.<vũ khí>")
        flags = data.get("recordedRateFlags") or {}
        for r, _x, _p in C.keyed(vw, data.get("weapons"), VALIDATE, ("weapons",)):
            r.set("vu_khi", r.id)
            if r.id in flags:
                r.set("ly_do_da_ghi", flags[r.id], VALIDATE, ("recordedRateFlags", r.id))
        vk = book.kv_sheet("Validator_ket_qua", "Validator: kết quả fix_validate", "fix_validate.json: tóm tắt, danh sách lỗi, "
                           "ngoài dải LOD1, quá ngân sách, tồn đọng (trừ grades, weapons)")
        rest = {"models": {k: v for k, v in models.items() if k != "grades"}}
        rest.update({k: v for k, v in data.items() if k not in ("models", "weapons", "recordedRateFlags")})
        rest["recordedRateFlags"] = {k: v for k, v in flags.items() if k not in vw.rows}
        if not rest["recordedRateFlags"]:
            del rest["recordedRateFlags"]
        _kv_skip(book, vk, rest, VALIDATE, {("models", "summary", "scanDir")})

    # ------------------------------------------------------------------ Lich_su_do (old measurements)
    ld = book.kv_sheet("Lich_su_do", "Lịch sử đo", "Mốc đo cũ: Tools/balance/*_before.json, *_baseline.json, "
                       "Tools/campaign/p31_objectives_baseline.json; mỗi lá một dòng (id = <file>.<đường dẫn>)")
    ld.col("stale", meaning="STALE: số đo cũ hơn dữ liệu hiện tại (chưa có hash lúc đo)")
    for sid in sorted(s for s in ctx.sources if re.fullmatch(r"Tools/balance/[^/]*_(before|baseline)\.json", s)
                      or s == "Tools/campaign/p31_objectives_baseline.json"):
        stem = sid.rsplit("/", 1)[-1][:-5]
        book.kv_rows(ld, ctx.data(sid), sid, (), stem, prefix=(stem,))
    for r in ld.rows.values():
        r.set("stale", chua_ap("xuat_luot5"))

    # ------------------------------------------------------------------ Chuyen_doi_save (campaign migration)
    camp = ctx.data(C.CAMPAIGN)
    cs = book.kv_sheet("Chuyen_doi_save", "Chuyển đổi save cũ", "campaign.json migration / migration22: nhiệm vụ đổi chỗ, chương đã "
                       "xem, cấp HQ theo nhiệm vụ")
    for k in sorted(k for k in camp if k.startswith("migration")):
        book.kv_rows(cs, camp[k], C.CAMPAIGN, (k,), k, prefix=(k,))

    # ------------------------------------------------------------------ Bang_don_vi_tai_lieu (Tools/docs/unit_sheet.json)
    if UNIT_SHEET in ctx.sources:
        us = ctx.data(UNIT_SHEET)
        bu = book.sheet("Bang_don_vi_tai_lieu", "Bảng đơn vị của tài liệu", "Tools/docs/unit_sheet.json: mô tả, hình dạng, sheet, "
                        "mở khóa của mỗi đơn vị trong tài liệu cũ (Docs/balance)")
        C.keyed(bu, us.get("units"), UNIT_SHEET, ("units",))
        rest = {k: v for k, v in us.items() if k != "units"}
        if rest:
            kv = book.kv_sheet("Bang_don_vi_tai_lieu_chung", "Bảng đơn vị: ghi chú", "unit_sheet.json: khóa ngoài units")
            book.kv_rows(kv, rest, UNIT_SHEET, (), "unit_sheet")

    # ------------------------------------------------------------------ Khac_chua_phan_loai, Hang_so_trong_ma
    kc = book.sheet("Khac_chua_phan_loai", "Chưa phân loại chắc", "Nguồn / thực thể chưa rõ lĩnh vực (spec 3.2): nơi tạm đặt và lý do")
    kc.col("noi_dat", meaning="file / sheet đang chứa")
    kc.col("ly_do", meaning="vì sao chưa chắc")
    provisional = [
        ("Tests/EditMode/Scenarios/*.json", "12_he_thong_trang_thai/Test_kich_ban", "kịch bản test sandbox, không phải dữ liệu game"),
        (UNIT_SHEET, "12_he_thong_trang_thai/Bang_don_vi_tai_lieu", "bảng đơn vị của tài liệu cũ (mô tả chữ), không phải dữ liệu game"),
        ("Assets/MachineBrigade/Resources/UI/Bases/*.json", "11_meta_giao_dien/Anh_can_cu", "ảnh căn cứ của giao diện; có thể thuộc 08"),
        ("Assets/MachineBrigade/Resources/UI/Cards/manifest.json", "10_model_tai_san/Anh_the", "ảnh thẻ render từ model; có thể thuộc 11"),
        ("Assets/MachineBrigade/Settings/BattlefieldProfile.asset", "09_hieu_ung_am_thanh/Hau_ky_hinh_anh", "hậu kỳ hình ảnh"),
        ("balance.json handbook", "11_meta_giao_dien/So_tay_dan", "xe mẫu của sổ tay đạn (giao diện)"),
        ("campaign.json eventLibrary.rules.weatherSight", "08_ban_do/Thoi_tiet", "thời tiết: chiến dịch (07) hay bản đồ (08)"),
        ("campaign.json eventLibrary.rules.difficulty", "05_che_do_kinh_te/Do_kho", "biến cố theo độ khó: 05 hay 07"),
        ("Docs/checks/fix_validate.json", "12_he_thong_trang_thai/Validator_*", "kết quả validator; điểm model cũng là 10/Model_cham_diem (lớp B)"),
    ] + [(s, "?", why) for s, _p, why in ctx.unclassified]
    for i, (src, where, why) in enumerate(provisional):
        r = kc.row(f"K{i + 1:02d}", src)
        r.set("noi_dat", where)
        r.set("ly_do", why)
    C.marker_sheet(book, "Hang_so_trong_ma", "Hằng số trong mã", "Mọi hằng số và số cứng ảnh hưởng lối chơi (spec 5): tệp, dòng, "
                   "tên, giá trị, ngữ cảnh, lĩnh vực, đề xuất đưa ra dữ liệu", chua_ap("xuat_luot5"),
                   "lượt 5 quét Assets/MachineBrigade/Scripts", "Tools/export (lượt 5)")


def _kv_skip(book, sheet, obj, src, skip: set):
    """kv_rows without the leaves in skip (they sit in Khong_xuat)."""
    def prune(node, path):
        if isinstance(node, dict):
            return {k: prune(v, path + (k,)) for k, v in node.items() if path + (k,) not in skip}
        return node
    book.kv_rows(sheet, prune(obj, ()), src, (), "fix_validate")
