"""The compact balance pack (Docs/prompts/export_pack_vi.txt, addendum): the 13 domain books domains/ builds are regrouped
into the files of Docs/export/current/ (PACK below), the sheets of section 2.3 go to bulk.zip, the process sheets of 2.1 leave, and
every cell is made free of process words and build-time markers.

restructure(ctx, game) runs before the formulas are resolved, so a formula still reads sheets of ITS file only (the sheet
a collision renames gets its placeholders renamed too). It changes no value of the game: it moves sheets, drops process
sheets, renames markers and scrubs text.
"""
from __future__ import annotations

import collections
import json
import re

from . import units_fill
from .model import KHONG_AP_DUNG, MARKER, NEED_CODE_CHECK, NEED_SOURCE, Book, Sheet
from .scrub import GAME_TEXT, scrub_str

# new file id -> (title, the old files it takes, description)
PACK = {
    "01_chien_dau": ("Chiến đấu", ("01_vu_khi_dan", "02_phuong_tien"),
                     "Vũ khí, đạn, phương tiện, thẻ hỗ trợ, trang bị, commander, đội mở màn, ném bom rải thảm"),
    "02_boss": ("Boss", ("03_boss",), "Boss, bộ phận, siêu vũ khí, hộ tống, pha, Săn trùm"),
    "03_can_cu": ("Căn cứ và tháp", ("04_can_cu_thap",), "Tháp và nhánh, tường, nhà chính, mô-đun tiện ích, xây lại, AI căn cứ"),
    "04_che_do_kinh_te_ai": ("Chế độ, kinh tế, meta, giao diện", ("05_che_do_kinh_te", "11_meta_giao_dien"),
                             "Chế độ chơi, độ khó, kinh tế, tác chiến, thăng hạng, mở khóa, cửa hàng, giao diện"),
    "05_chien_dich": ("Chiến dịch và cốt truyện", ("07_chien_dich_cot_truyen",),
                      "Chương, nhiệm vụ, biến cố, bộ bài game, nhân vật, thống kê thoại"),
    "06_ban_do": ("Bản đồ", ("08_ban_do",), "Bản đồ, bản đồ gốc, biome, thời tiết, địa danh, ray, vật thể, ngân sách thực thể"),
    "07_hinh_anh_am_thanh_model": ("Hình ảnh, âm thanh, model", ("09_hieu_ung_am_thanh", "10_model_tai_san"),
                                   "Hiệu ứng, âm thanh, hậu kỳ hình ảnh, model và số đo model, tài sản, giấy phép"),
    "08_tham_chieu": ("Tham chiếu ngoài đời và game", ("13_tham_chieu_nguon",),
                      "Nguồn ngoài đời, cơ chế lấy ý từ game, học thuyết quân sự, bản quyền tài liệu"),
    "09_ai": ("AI", ("06_ai",),
              "Chiến thuật, hồ sơ AI theo chế độ, tướng địch, tham số AI, vai trò đơn vị, trạng thái đội, hành vi tháp / "
              "boss, luồng quyết định theo lớp (tướng / đội / đơn vị), mục tiêu ưu tiên, độ khó, chống kẹt, tiếp tế "
              "máy bay, hằng số AI còn trong mã"),
    "10_trang_bi": ("Trang bị", (),
                    "Trang bị xe và trang bị tháp: loại cơ bản, mô-đun, đặc tính, dòng phụ, bộ, trần cộng dồn, bảng chỉ "
                    "số, bảng theo độ hiếm, giá nâng cấp theo cấp, luật ghép, hòm và tỷ lệ rơi, tên Anh/Việt theo id"),
}
OLD_TO_NEW = {old: new for new, (_t, olds, _d) in PACK.items() for old in olds}
GROUP_PREFIX = {"01_vu_khi_dan": "vk", "02_phuong_tien": "xe", "03_boss": "boss", "04_can_cu_thap": "cc",
                "05_che_do_kinh_te": "ce", "06_ai": "ai", "11_meta_giao_dien": "meta", "07_chien_dich_cot_truyen": "cd",
                "08_ban_do": "bd", "09_hieu_ung_am_thanh": "hu", "10_model_tai_san": "mo", "13_tham_chieu_nguon": "tc"}

# section 2.1: left out of the pack (the source stays in the repo and CI)
DROP = {"Trang_thai_prompt", "DECISIONS", "Cho_quyet", "Kiem_tra_ma", "Kiem_tra_file", "Test", "Validator",
        "Validator_ket_qua", "Validator_model", "Validator_vu_khi", "Manifest_ap", "Manifest_ap_goi", "Lich_su_do",
        "Chuyen_doi_save", "Bang_don_vi_tai_lieu", "Bang_don_vi_tai_lieu_chung", "Truong_du_lieu", "Thieu_nguon",
        "Tham_chieu_decisions", "Khac_chua_phan_loai",
        # history of the model rebuilds (dated notes with their reasons): not a value of the game
        "Model_lich_su", "Anh_chup"}
DROP_PREFIX = ("Test_kich_ban", "Validator")
# section 2.3: CSV in bulk.zip
BULK = {"Ban_do_vat_the", "Ban_do_tag_dia_hinh", "Ban_do_trang_tri", "Ban_do_can_cu_o", "Ban_do_phao_dai_o", "Ban_do_duong",
        "Ban_do_tuong_doan", "Ban_do_lien_ket_canh", "Ban_do_canh", "Ban_do_goc_canh", "Model_nut", "Dia_phuong_hoa",
        "Dia_phuong_hoa_van_de", "Anh_the", "Kich_ban_goc", "Thoai", "Thoai_thong_ke_nhom", "Nhiem_vu_radio",
        "Giay_phep_noi_dung", "Huong_dan", "Am_thanh_envelope"}
# Khac_chua_phan_loai, classified: a sheet filed under the file that owns its subject
RECLASSIFY = {"Anh_can_cu": "03_can_cu", "Anh_can_cu_mui_ten": "03_can_cu", "Anh_can_cu_vien": "03_can_cu",
              "So_tay_dan": "01_chien_dau",
              # Gear book 04/10 (lane A, owner: "đem ra 1 file riêng, đầy đủ"): every Trang_bi* sheet, wherever its old
              # domain built it (02_phuong_tien: most of them; 11_meta_giao_dien: Trang_bi_hang), moves into 10_trang_bi.
              "Trang_bi": "10_trang_bi", "Trang_bi_mo_dun": "10_trang_bi", "Trang_bi_dac_tinh": "10_trang_bi",
              "Trang_bi_dong_phu": "10_trang_bi", "Trang_bi_bo": "10_trang_bi", "Trang_bi_thap": "10_trang_bi",
              "Trang_bi_dac_tinh_thap": "10_trang_bi", "Trang_bi_tran": "10_trang_bi", "Trang_bi_chi_so": "10_trang_bi",
              "Trang_bi_hang": "10_trang_bi",
              # new layer-C sheets (domains/_c02_gear.py), built inside 02_phuong_tien same as the rest: reclassified too.
              "Trang_bi_nang_cap": "10_trang_bi", "Trang_bi_ghep": "10_trang_bi", "Trang_bi_thung": "10_trang_bi",
              "Trang_bi_thung_nguon": "10_trang_bi", "Trang_bi_ten": "10_trang_bi"}
# the file / sheet text of the classification (kept for CHANGES.md and the README)
CLASSIFIED = [
    ("Anh_can_cu, Anh_can_cu_mui_ten, Anh_can_cu_vien", "03_can_cu", "ảnh căn cứ của giao diện: hình của chính ô căn cứ"),
    ("So_tay_dan", "01_chien_dau", "xe mẫu của sổ tay đạn: thuộc vũ khí và đạn"),
    ("Trang_bi, Trang_bi_mo_dun, Trang_bi_dac_tinh, Trang_bi_dong_phu, Trang_bi_bo, Trang_bi_thap, "
     "Trang_bi_dac_tinh_thap, Trang_bi_tran, Trang_bi_chi_so, Trang_bi_hang", "10_trang_bi",
     "trang bị xe và trang bị tháp: gom thành một file riêng (owner 04/10), từ 02_phuong_tien và 11_meta_giao_dien"),
    ("Anh_the", "bulk.zip (07)", "ảnh thẻ render từ model: thuộc hình ảnh"),
    ("Hau_ky_hinh_anh", "07_hinh_anh_am_thanh_model", "hậu kỳ hình ảnh: thuộc hình ảnh"),
    ("Thoi_tiet", "06_ban_do", "thời tiết: giữ ở bản đồ (chiến dịch chỉ dùng nó)"),
    ("Do_kho", "04_che_do_kinh_te_ai", "biến cố theo độ khó: giữ ở chế độ và độ khó"),
    ("Test_kich_ban, Validator_*, Bang_don_vi_tai_lieu", "ngoài gói", "kịch bản test, kết quả validator, bảng đơn vị cũ: không phải dữ liệu game"),
]
OUT = "_ngoai_goi"  # coverage: a leaf mapped to a sheet that is not in the pack


def _dropped(name: str) -> bool:
    return name in DROP or name.startswith(DROP_PREFIX)


def _marker_row_only(s: Sheet) -> str | None:
    """The marker of a sheet that is one marker row (the sheet says 'not here' or 'to read from the code')."""
    if len(s.rows) != 1:
        return None
    r = next(iter(s.rows.values()))
    vals = [v for k, v in r.values.items() if isinstance(v, str) and k != s.id_col]
    if str(r.id) in ("chua_ap", "khong_co") or any(v == "KHONG_CO" for v in vals):
        for v in vals:
            if MARKER.match(v):
                return v
    return None


def _route(oldfid: str, name: str, s: Sheet) -> tuple:
    """('drop', why) | ('qa', name) | ('pack', file) | ('bulk', file)."""
    if oldfid == "12_he_thong_trang_thai":
        if name == "Hang_so_trong_ma":
            return ("qa", name)
        return ("drop", "sheet quy trình (mục 2.1)")
    if _dropped(name):
        return ("drop", "sheet quy trình, lịch sử hoặc kiểm tra (mục 2.1)")
    mk = _marker_row_only(s)
    if mk == "KHONG_CO":
        return ("drop", "game không có (mục 2.5)")
    if name in BULK:
        return ("bulk", RECLASSIFY.get(name) or OLD_TO_NEW[oldfid])
    return ("pack", RECLASSIFY.get(name) or OLD_TO_NEW[oldfid])


# ------------------------------------------------------------------------------------------------------- the move
def restructure(ctx, game: dict | None = None):
    old = ctx.books
    plan: dict[tuple, tuple] = {}
    for fid, book in old.items():
        for name, s in book.sheets.items():
            plan[(fid, name)] = _route(fid, name, s)
    # new names: the group prefix when two moved sheets share a name
    count = collections.Counter(name for (fid, name), p in plan.items() if p[0] in ("pack", "bulk"))
    newname = {}
    for (fid, name), p in plan.items():
        if p[0] in ("pack", "bulk"):
            newname[(fid, name)] = name if count[name] == 1 else f"{GROUP_PREFIX[fid]}_{name}"[:31]
    ctx.sheet_map = {k: (p[1], newname[k]) for k, p in plan.items() if p[0] in ("pack", "bulk")}
    ctx.dropped = []  # (old file, sheet, reason, rows)
    ctx.qa_sheets = {}
    ctx.out_sheets = {}
    new_books = {}
    for nid, (title, _olds, desc) in PACK.items():
        new_books[nid] = Book(ctx, nid, title, desc)
    for fid, book in old.items():
        for name, s in list(book.sheets.items()):
            p = plan[(fid, name)]
            if p[0] == "drop":
                ctx.dropped.append((fid, name, p[1], len(s.rows)))
                ctx.out_sheets[name] = p[1]
            elif p[0] == "qa":
                ctx.qa_sheets[name] = s
                ctx.out_sheets[name] = "hằng số trong mã: chỉ ở _qa (mục 4)"
    # keep the order of the old files inside a new file
    for nid, (_t, olds, _d) in PACK.items():
        for fid in olds:
            for name, s in list(old[fid].sheets.items() if fid in old else []):
                p = plan[(fid, name)]
                if p[0] in ("pack", "bulk") and p[1] == nid:
                    _move(new_books[nid], s, newname[(fid, name)], p[0] == "bulk")
        # a sheet reclassified into this file from another old file
    for fid, book in old.items():
        for name, s in list(book.sheets.items()):
            p = plan[(fid, name)]
            if p[0] in ("pack", "bulk") and OLD_TO_NEW.get(fid) != p[1]:
                _move(new_books[p[1]], s, newname[(fid, name)], p[0] == "bulk")
    ctx.books = new_books
    ctx.plan = plan

    def target(ref: str):
        fid, _, sname = ref.partition("/")
        q = plan.get((fid, sname))
        if q is None:
            return ref
        if q[0] not in ("pack", "bulk"):
            return None
        return f"{q[1]}/{newname[(fid, sname)]}"

    renames = collections.defaultdict(dict)  # old file -> {old sheet: new sheet}
    for (fid, name), nn in newname.items():
        if nn != name:
            renames[fid][name] = nn
    origin = {}
    for fid, book in old.items():
        for name in book.sheets:
            origin[(fid, name)] = (fid, name)
    for nid, book in new_books.items():
        for s in book.sheets.values():
            for c in s.cols.values():
                c.fk = [t for t in (target(x) for x in c.fk) if t]
    _rename_templates(ctx, plan, renames, newname)
    for cp in getattr(ctx, "copies", []):
        for kf, ks in (("file", "sheet"), ("src_file", "src_sheet")):
            q = ctx.sheet_map.get((cp[kf], cp[ks]))
            if q:
                cp[kf], cp[ks] = q
    # coverage: a leaf mapped to a moved sheet follows it; one mapped to a dropped sheet is out of the pack
    moved = {}
    for k, (f, sh, c) in ctx.cov.mapped.items():
        q = ctx.sheet_map.get((f, sh))
        moved[k] = (q[0], q[1], c) if q else (OUT, sh, c)
    ctx.cov.mapped = moved
    ctx.cov.out_reasons = dict(ctx.out_sheets)

    bal = "Assets/MachineBrigade/Resources/Data/balance.json"  # its version lands in 00_index.xlsx Phien_ban
    if bal in ctx.sources and ctx.sources[bal].readable and "version" in ctx.sources[bal].data:
        ctx.cov.mark(bal, ("version",), "00_index", "Phien_ban", "gia_tri")
    from . import tunables
    ctx.tunables = tunables.build(ctx)  # lane B's constants moved from the code into the data, in their domain sheets
    if tunables.SID in ctx.sources and ctx.sources[tunables.SID].readable and "version" in ctx.sources[tunables.SID].data:
        ctx.cov.mark(tunables.SID, ("version",), "00_index", "Phien_ban", "gia_tri")
    catch_all(ctx)
    _classify_markers(ctx)
    _scrub_cells(ctx)
    ctx.game_filled = 0
    ctx.game = game  # add_bom_sheets fills the bomb sheets' cells from it (they join file 01 after the formulas)
    if game:
        from . import gamefill
        ctx.game_filled = gamefill.fill(ctx, game)


def _move(book: Book, s: Sheet, name: str, bulk: bool):
    s.book.sheets.pop(s.name, None)
    s.book = book
    s.name = name
    s.bulk = bulk
    book.sheets[name] = s


def _rename_templates(ctx, plan, renames, newname):
    from .formula import F
    pat = re.compile(r"\{([A-Za-z][A-Za-z0-9_]*)!")
    inv = {}  # new (file, name) -> old file
    for (fid, name), nn in newname.items():
        inv[(plan[(fid, name)][1], nn)] = fid
    for nid, book in ctx.books.items():
        for name, s in book.sheets.items():
            fid = inv.get((nid, name))
            ren = renames.get(fid) if fid else None
            if not ren:
                continue
            for r in s.rows.values():
                for v in r.values.values():
                    if isinstance(v, F):
                        v.template = pat.sub(lambda m: "{" + ren.get(m.group(1), m.group(1)) + "!", v.template)
    # a renamed sheet's own formulas also name the sheets of their old file: handled above (same old file)


# ----------------------------------------------------------------------------------------------------------- markers
KAD_REASONS = {
    ("prompt_24",): "game chưa có hướng dẫn người chơi mới (chưa làm; gợi ý trong trận ở sheet nhiệm vụ)",
}


def _classify_markers(ctx):
    """CHUA_AP:prompt_N -> NEED_CODE_CHECK (or KHONG_AP_DUNG when the game has nothing there); KHONG_CO -> KHONG_AP_DUNG;
    a one-row marker sheet keeps its marker with a clear id."""
    ctx.kad = {}  # (file, sheet, column) -> reason, for Schema
    for nid, book in ctx.books.items():
        for name, s in book.sheets.items():
            for r in list(s.rows.values()):
                if r.id == "chua_ap":
                    new = "can_doc_ma"
                    s.rows.pop("chua_ap")
                    r.id = new
                    r.values[s.id_col] = new
                    s.rows[new] = r
                for col, v in list(r.values.items()):
                    if not isinstance(v, str):
                        continue
                    if v.startswith("CHUA_AP:"):
                        if "prompt_24" in v:
                            r.values[col] = KHONG_AP_DUNG
                            ctx.kad[(nid, name, col)] = KAD_REASONS[("prompt_24",)]
                        else:
                            r.values[col] = NEED_CODE_CHECK
                    elif v == "KHONG_CO":
                        r.values[col] = KHONG_AP_DUNG
                        ctx.kad[(nid, name, col)] = "game không có thứ này cho dòng đó (xem ghi_chu của dòng)"


OLD_FILE = re.compile(r"\b(0[1-9]|1[0-3])_[a-z_]+(?:/([A-Za-z][A-Za-z0-9_]*))?\b")
OLD_SHORT = re.compile(r"\b(0[1-9]|1[0-3])/([A-Z][A-Za-z0-9_]*)\b")


def make_ref_rewriter(ctx):
    """Text that names a file or sheet of the old layout ('09_hieu_ung_am_thanh/Am_thanh', '10/Model') names the pack's now."""
    plan, smap = ctx.plan, ctx.sheet_map
    num = {fid[:2]: fid for (fid, _n) in plan}
    new_of = {old: new for old, new in OLD_TO_NEW.items()}

    def one(fid: str, sheet: str | None, whole: str) -> str:
        if sheet is None:
            nf = new_of.get(fid)
            return nf if nf else whole
        q = smap.get((fid, sheet))
        if q:
            return f"{q[0]}/{q[1]}"
        if (fid, sheet) in plan:
            return f"{sheet} (ngoài gói)"
        nf = new_of.get(fid)
        return f"{nf}/{sheet}" if nf else whole

    def rewrite(s: str) -> str:
        if "/" not in s and "_" not in s:
            return s
        s = OLD_FILE.sub(lambda m: one(m.group(0).split("/")[0], m.group(2), m.group(0)) if m.group(0).split("/")[0] in new_of
                         or m.group(0).split("/")[0] in {f for f, _ in plan} else m.group(0), s)
        return OLD_SHORT.sub(lambda m: one(num.get(m.group(1), ""), m.group(2), m.group(0)) if num.get(m.group(1)) else m.group(0), s)

    return rewrite


def _scrub_cells(ctx):
    rewrite = make_ref_rewriter(ctx)
    ctx.rewrite_refs = rewrite

    def clean(v):
        return rewrite(scrub_str(v))

    for nid, book in ctx.books.items():
        for name, s in book.sheets.items():
            if s.base_name not in GAME_TEXT:  # the cells of a game-text sheet are the game's own words
                for r in s.rows.values():
                    r.nguon = clean(r.nguon) if isinstance(r.nguon, str) else r.nguon
                    for col, v in list(r.values.items()):
                        if col != s.id_col and isinstance(v, str) and v and not MARKER.match(v):
                            w = clean(v)
                            if w != v:
                                r.values[col] = w
            for c in s.cols.values():
                if isinstance(c.meaning, str):
                    c.meaning = clean(c.meaning)
                if isinstance(c.source_note, str):
                    c.source_note = clean(c.source_note)
            s.desc = clean(s.desc or "")
            s.title_vi = clean(s.title_vi or "")


# ------------------------------------------------------------------------------------------- the game's own numbers
# the cells game.json answers are filled by core/gamefill.py; what is left is listed here


def need_code_check(ctx) -> list[tuple]:
    """Every NEED_CODE_CHECK cell left: (file, sheet, id, column), in file / sheet / row order."""
    out = []
    for nid, book in ctx.books.items():
        for name, s in book.sheets.items():
            for r in s.sorted_rows():
                for col in s.column_order():
                    if r.values.get(col) == NEED_CODE_CHECK:
                        out.append((nid, name, str(r.id), col))
    return out


# --------------------------------------------------------------------------------------------- additions after FX
def add_bom_sheets(ctx):
    """The four bomb sheets (bom.py) join 01_chien_dau; built from the evaluated sheets, so after FX.run."""
    import bom
    book = ctx.books["01_chien_dau"]
    try:
        sheets = bom.static_sheets(ctx)
    except KeyError:  # a lenient build (an old tree): the bomb sheets need the whole of file 01 and 03
        return
    descs = {
        "Bom_vu_khi": "Mỗi vũ khí thả bom và mỗi đòn không kích / đòn lớn của boss một dòng: tham số dải bom (stick), "
                      "khoảng cách giữa bom, độ dài dải, cảnh báo, đường thả theo mã",
        "Bom_don_vi": "Đơn vị mang bom: tốc độ, bán kính quay, độ cao thả, vũ khí bom, số bom mỗi lượt",
        "Bom_hanh_vi": "Từng bước hành vi ném bom theo mã (chọn mục tiêu, hướng vào, thả, rơi) và file hàm",
        "Bom_canh_bao": "Vòng cảnh báo của bom theo luật (hình dạng, bán kính lõi và rìa, thời gian cảnh báo)",
    }
    titles = {"Bom_vu_khi": "Ném bom: vũ khí", "Bom_don_vi": "Ném bom: đơn vị mang", "Bom_hanh_vi": "Ném bom: hành vi theo mã",
              "Bom_canh_bao": "Ném bom: vòng cảnh báo"}
    for name, (header, rows) in sheets.items():
        s = book.sheet(name, titles[name], descs[name], layer="C")
        data_cols = [h for h in header if h not in ("id", "nguon", "raw_json")]
        for h in data_cols:
            s.col(h, auto=True)
        for line in rows:
            d = dict(zip(header, line))
            raw = None
            if d.get("raw_json"):
                try:
                    raw = json.loads(d["raw_json"])
                except ValueError:
                    raw = None
            r = s.row(str(d["id"]), scrub_str(str(d.get("nguon") or "")), raw=raw)
            for h in data_cols:
                v = d.get(h)
                r.values[h] = scrub_str(v) if isinstance(v, str) else v
    game = getattr(ctx, "game", None)
    if game:
        from . import gamefill
        ctx.game_filled = getattr(ctx, "game_filled", 0) + gamefill.fill_late(ctx, game)


def add_map_summary(ctx):
    """06_ban_do/Ban_do_tom_tat: one row a map (section 2.3): objects by kind, the share of each terrain tag, base slots,
    lanes and chokepoints. The layout rows themselves are in bulk.zip."""
    book = ctx.books["06_ban_do"]
    if not {"Ban_do", "Ban_do_vat_the", "Ban_do_tag_dia_hinh", "Ban_do_do_tinh"} <= set(book.sheets):
        return  # a lenient build of an old tree
    sh = lambda n: book.sheets[n]  # noqa: E731
    maps = sh("Ban_do")
    s = book.sheet("Ban_do_tom_tat", "Tóm tắt từng bản đồ",
                   "Một dòng một bản đồ: số vật thể theo loại, phần trăm diện tích mỗi tag địa hình (rect sau đè rect trước, "
                   "lưới terrain_cell), số ô căn cứ, số ô pháo đài, số đường, số làn độc lập và điểm nghẽn", layer="C")
    s.col("dien_tich_m2", unit="m2", meaning="diện tích bản đồ (bounds hoặc size × size)", auto=True)
    s.col("so_vat_the", meaning="số vật thể trong Ban_do_vat_the", auto=True)
    s.col("so_vat_the_theo_loai", meaning="def:số lượng, ngăn ';', giảm dần", auto=True)
    s.col("so_o_can_cu", meaning="số ô căn cứ (Ban_do_can_cu_o)", auto=True)
    s.col("so_o_phao_dai", meaning="số ô pháo đài (Ban_do_phao_dai_o)", auto=True)
    s.col("so_duong", meaning="số đường (Ban_do_duong)", auto=True)
    s.col("so_lan_doc_lap", meaning="số làn độc lập (Ban_do_do_tinh)", auto=True)
    s.col("diem_nghen_bat_buoc", meaning="số điểm nghẽn bắt buộc (Ban_do_do_tinh)", auto=True)
    s.col("diem_nghen_tuy_chon", meaning="số điểm nghẽn tùy chọn (Ban_do_do_tinh)", auto=True)
    props = collections.defaultdict(collections.Counter)
    for r in sh("Ban_do_vat_the").rows.values():
        props[r.values.get("ban_do_id")][r.values.get("def")] += 1
    count = lambda n, col: collections.Counter(r.values.get(col) for r in sh(n).rows.values())  # noqa: E731
    base_slots = collections.Counter()
    bases = {r.id: r.values.get("ban_do_id") for r in sh("Ban_do_can_cu").rows.values()}
    for r in sh("Ban_do_can_cu_o").rows.values():
        base_slots[bases.get(r.values.get("ban_do_can_cu_id"))] += 1
    fort, roads = count("Ban_do_phao_dai_o", "ban_do_id"), count("Ban_do_duong", "ban_do_id")
    tom = {str(r.id): r for r in sh("Ban_do_do_tinh").rows.values()}
    rects = collections.defaultdict(list)
    for r in sh("Ban_do_tag_dia_hinh").sorted_rows():
        v = r.values
        rects[v.get("ban_do_id")].append((v.get("thu_tu"), v.get("x0_m"), v.get("z0_m"), v.get("x1_m"), v.get("z1_m"), v.get("tag")))
    tag_pct, tags = {}, set()
    for mid, row in maps.rows.items():
        v = row.values
        bounds = [float(x) for x in str(v.get("bounds") or "").split(";") if x != ""]
        size = float(v.get("size") or 0)
        x0, z0, x1, z1 = bounds if len(bounds) == 4 else (-size / 2, -size / 2, size / 2, size / 2)
        cell = float(v.get("terrain_cell") or 2.0) or 2.0
        nx, nz = max(1, int(round((x1 - x0) / cell))), max(1, int(round((z1 - z0) / cell)))
        grid = {}
        for _i, ax, az, bx, bz, tag in rects.get(mid, []):
            if None in (ax, az, bx, bz):
                continue
            i0, i1 = sorted((int((ax - x0) // cell), int((bx - x0) // cell)))
            j0, j1 = sorted((int((az - z0) // cell), int((bz - z0) // cell)))
            for i in range(max(0, i0), min(nx - 1, i1) + 1):
                for j in range(max(0, j0), min(nz - 1, j1) + 1):
                    grid[(i, j)] = tag
        per = collections.Counter(grid.values())
        tag_pct[mid] = {t: round(100.0 * n / (nx * nz), 2) for t, n in per.items()}
        tags |= set(per)
        tag_pct[mid]["_area"] = round((x1 - x0) * (z1 - z0), 1)
    for t in sorted(tags):
        s.col(f"tag_{t.lower()}_pct", unit="%", meaning=f"phần trăm diện tích bản đồ có tag địa hình {t}", auto=True)
    for mid in sorted(maps.rows, key=lambda k: str(k)):
        r = s.row(str(mid), "Tools/export (core/pack.py) từ Ban_do, Ban_do_vat_the, Ban_do_tag_dia_hinh, Ban_do_do_tinh")
        r.values["dien_tich_m2"] = tag_pct[mid]["_area"]
        pc = props.get(mid, collections.Counter())
        r.values["so_vat_the"] = sum(pc.values())
        r.values["so_vat_the_theo_loai"] = ";".join(f"{k}:{n}" for k, n in sorted(pc.items(), key=lambda x: (-x[1], str(x[0]))))
        r.values["so_o_can_cu"] = base_slots.get(mid, 0)
        r.values["so_o_phao_dai"] = fort.get(mid, 0)
        r.values["so_duong"] = roads.get(mid, 0)
        t = tom.get(str(mid))
        for col in ("so_lan_doc_lap", "diem_nghen_bat_buoc", "diem_nghen_tuy_chon"):
            r.values[col] = t.values.get(col) if t else ""
        for tag in tags:
            r.values[f"tag_{tag.lower()}_pct"] = tag_pct[mid].get(tag, 0.0)


# ---------------------------------------------------------------------------------------------------------- units
def schema_unit(sheet: Sheet, col) -> str:
    """Schema.don_vi: the column's unit; a count, share or multiplier named; khong_ro when nobody can say."""
    if col is None:
        return ""
    if col.unit:
        return col.unit
    if sheet.kind == "kv" and col.name == "gia_tri_so":
        return "theo_cot_don_vi"  # a key / value sheet: the unit of each value is in its row's don_vi cell
    if col.kind in ("int", "number") or (col.kind or "").startswith("mixed:") and "int" in (col.kind or ""):
        if col.unit_unknown:
            return units_fill.unit_for(sheet.base_name, col.name)
        return units_fill.NO_UNIT
    return ""


def freeze_bulk_references(ctx):
    """A formula that reads a sheet which lives in bulk.zip cannot stay a formula in the xlsx (formulas read their own
    file's sheets): its evaluated value replaces it. Returns the (file, sheet, column) list changed."""
    from .formula import F, PLACEHOLDER
    changed = set()
    for nid, book in ctx.books.items():
        bulk = {n for n, s in book.sheets.items() if s.bulk}
        if not bulk:
            continue
        for name, s in book.sheets.items():
            if s.bulk:
                continue
            for r in s.rows.values():
                for col, v in list(r.values.items()):
                    if isinstance(v, F) and any(m.group(1) in bulk for m in PLACEHOLDER.finditer(v.template)):
                        r.values[col] = v.value
                        changed.add((nid, name, col))
    for nid, name, col in changed:
        s = ctx.books[nid].sheets[name]
        c = s.cols.get(col)
        if c is not None and not any(hasattr(r.values.get(col), "template") for r in s.rows.values()):
            c.source_note = (c.source_note + "; " if c.source_note else "") + "giá trị tính từ sheet nằm trong bulk.zip"
            c.formula = None
    return sorted(changed)


# ------------------------------------------------------------------------------------------- data nobody claims yet
# the file that takes the leaves of a block no domain maps (a constant block moved from the code into balance.json, a new
# data file); the first pattern that fits the block's name wins, the default is 01_chien_dau
CONST_ROUTE = [
    (re.compile(r"(?i)boss|hunt"), "02_boss"),
    (re.compile(r"(?i)tower|base|wall|fortress|siege|defen"), "03_can_cu"),
    (re.compile(r"(?i)\bai\b|ai[A-Z_]|^ai"), "09_ai"),
    (re.compile(r"(?i)econom|supply|income|mode|match|difficult|meta|menu|shop|rank|unlock|operation"),
     "04_che_do_kinh_te_ai"),
    (re.compile(r"(?i)campaign|mission|dialog|script|event|chapter"), "05_chien_dich"),
    (re.compile(r"(?i)map|terrain|biome|weather|prop|dressing"), "06_ban_do"),
    (re.compile(r"(?i)audio|sound|vfx|effect|model|camera|light|render|shake"), "07_hinh_anh_am_thanh_model"),
]


def catch_all(ctx):
    """Every leaf of a JSON data file under Assets/ that no domain mapped and no rule excludes goes into a key / value sheet
    Hang_so_<block> of the file CONST_ROUTE picks, so the pack always shows what the data holds (coverage stays whole when
    constants move from the code into the data). Returns the (file, sheet, leaves) list made; empty when nothing is loose."""
    from . import paths as P
    from .sources import get as leaf_get
    from .units import column_for, snake
    made = []
    for sid, src in sorted(ctx.sources.items()):
        if src.kind != "json" or not sid.startswith("Assets/") or not src.readable:
            continue
        ex = [r for r in ctx.excluded if r.fits_source(sid)]
        cache: dict = {}
        groups = collections.defaultdict(list)
        for path in src.leaves():
            if (sid, path) in ctx.cov.mapped:
                continue
            g = P.general(path)
            hit = cache.get(g, 0)
            if hit == 0:
                hit = cache[g] = next((r for r in ex if P.matches(r.pattern, g)), None)
            if hit is None:
                groups[str(path[0]) if path else "_"].append(path)
        stem = sid.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        for block, paths in groups.items():
            fid = next((f for rx, f in CONST_ROUTE if rx.search(block)), "01_chien_dau")
            book = ctx.books[fid]
            base = f"Hang_so_{snake(block)}" if stem == "balance" else f"Hang_so_{snake(stem)}_{snake(block)}"
            name, n = base[:31].rstrip("_"), 2
            while name in book.sheets:
                name = f"{base[:28]}_{n}"
                n += 1
            sh = book.kv_sheet(name, f"Hằng số trong dữ liệu: {block}",
                               f"Mọi lá của {sid} dưới '{block}' mà sheet lĩnh vực chưa nhận: một dòng một lá (id = đường dẫn)")
            sh.col("khoa", meaning="khóa của lá")
            for path in paths:
                node = leaf_get(src.data, path)
                r = sh.row(P.to_str(path), f"{sid}: {P.to_str(path)}", raw=node)
                last = next((x for x in reversed(path) if isinstance(x, str)), "")
                r.values["nhom"] = P.to_str(path[:1])
                r.values["khoa"] = str(path[-1]) if path else ""
                r.values["don_vi"] = column_for(last)[1] if last else ""
                if isinstance(node, bool) or isinstance(node, (int, float)):
                    r.set("gia_tri_so", node, sid, path)
                elif isinstance(node, str):
                    r.set("gia_tri_chu", node, sid, path)
                else:  # an empty list / dict / null
                    r.set("gia_tri_chu", "" if node in ([], {}, None) else str(node), sid, path)
            made.append((fid, name, len(paths)))
            ctx.issue(f"catch-all: {len(paths)} leaves of {sid} under '{block}' went to {fid}/{name} (no domain maps them)")
    ctx.catch_all = made
    return made
