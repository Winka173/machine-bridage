"""Pass 10 (spec 12.2, 12.4): the columns every <name>_tham_chieu sheet shares, the row writer, the reliability rule and the
<name>_so_sanh_that sheet (live formulas: ratio game / real, the allowed band, co_lech_lon).

Reliability (do_tin_cay, spec 12.2): da_kiem_chung only when the repo record carrying the figure names an outside document
for it (and is not marked as an estimate); a note labelled "ước đoán" (unit_refs.json), "est." (the REAL table) or approx
(reference_real.json) stays uoc_dinh; a name or note the repo gives with no document behind it is ban_dau_doan; nothing in
the repo: NEED_SOURCE. Never upgraded without a source.
"""
from __future__ import annotations

from core.formula import F, lookup
from core.model import NEED_SOURCE

REF_FILE = "13_tham_chieu_nguon"
NGUON_FK = [f"{REF_FILE}/Nguon_tham_chieu"]
LOAI = ["doi_that", "game", "phim_truyen", "lich_su", "hoc_thuyet_quan_su", "gia_tuong"]
TIN = ["da_kiem_chung", "uoc_dinh", "ban_dau_doan", NEED_SOURCE]
LY_DO = ["gameplay", "hieu_nang", "ban_quyen", "gia_tuong"]
BAN_QUYEN = ("chỉ ở mức ý tưởng và thông số (sự kiện); không dùng tên, logo, văn bản, ảnh hay mô hình có bản quyền; "
             "tên và phù hiệu quốc gia thật không hiện cho người chơi")
SPEED_SIZE = (0.7, 1.4)   # spec 12.4 starting bands
RATE = (0.6, 2.0)
SHAPE = (0.9, 1.1)        # proportions W/L, H/L: MODEL_STANDARD rule 3.1 (10 %)

COMMON = [
    ("ten_hien_thi", "tên hiển thị của thực thể (trong game)", None),
    ("loai_tham_chieu", "doi_that | game | phim_truyen | lich_su | hoc_thuyet_quan_su | gia_tuong; NEED_SOURCE: repo không "
                        "có tham chiếu", LOAI),
    ("ten_mau_that", "mẫu thật (ký hiệu như nguồn repo ghi; nhiều mẫu ngăn ';')", None),
    ("quoc_gia", "quốc gia của mẫu thật (chỉ khi nguồn repo ghi; không hiện cho người chơi)", None),
    ("nam_dua_vao_su_dung", "năm đưa vào sử dụng (chỉ khi nguồn repo ghi)", None),
    ("ten_game", "game lấy ý (ngăn ';')", None),
    ("co_che_game", "cơ chế / hình dáng lấy ý từ game (ngắn; ngăn ';' theo ten_game)", None),
    ("ten_phim_truyen", "phim / truyện lấy ý (ngăn ';')", None),
    ("diem_giong", "điểm giống (tóm tắt của ta từ nguồn repo)", None),
    ("diem_khac_co_chu_dich", "điểm khác có chủ đích (khi nguồn repo ghi)", None),
    ("ly_do_khac", "gameplay | hieu_nang | ban_quyen | gia_tuong (khi nguồn repo cho biết)", LY_DO),
    ("cam_giac_khac_khi_choi", "cảm giác khác khi chơi so với bản gốc (khi nguồn repo ghi)", None),
    ("do_tin_cay", "da_kiem_chung | uoc_dinh | ban_dau_doan | NEED_SOURCE (luật ở đầu _ref_common.py)", TIN),
    ("nguon_id", "nguồn (13_tham_chieu_nguon/Nguon_tham_chieu; ngăn ';')", None),
    ("ly_do", "lý do (bắt buộc khi gia_tuong hoặc NEED_SOURCE: vì sao chưa có mẫu thật)", None),
    ("ghi_chu_ban_quyen", "quy tắc bản quyền (spec 12.5)", None),
]


def ref_sheet(book, name: str, title: str, desc: str, entity_fk: list, extra: list):
    """<name>_tham_chieu: entity_id + the common columns + the domain's extra [(col, unit, meaning)]."""
    sh = book.sheet(name, title, desc + " (spec 12.2; lượt 10; chỉ dữ liệu có trong repo)", layer="C")
    sh.col("entity_id", meaning="thực thể (khóa ngoại)", fk=entity_fk, required=True)
    for col, meaning, enum in COMMON:
        sh.col(col, meaning=meaning, enum=enum,
               fk=NGUON_FK if col == "nguon_id" else None)
    for col, unit, meaning in extra:
        sh.col(col, unit=unit, meaning=meaning)
    return sh


def real_blank(loai: str):
    """A real-world value nobody gave: NEED_SOURCE when the row has (or should have) a real model, empty for a game,
    film or fictional reference (not applicable)."""
    return NEED_SOURCE if loai in ("doi_that", NEED_SOURCE, "lich_su") else ""


def reliability(loai: str, label_guess: bool, number_tins: list[str]) -> str:
    if loai == NEED_SOURCE:
        return NEED_SOURCE
    if label_guess:
        return "uoc_dinh"
    if "uoc_dinh" in number_tins:
        return "uoc_dinh"
    if "da_kiem_chung" in number_tins:
        return "da_kiem_chung"
    return "ban_dau_doan"


def put_row(sh, rid, entity, nguon_text: str, vals: dict, raw=None):
    r = sh.row(rid, nguon_text, raw=raw)
    r.set("entity_id", entity)
    for k, v in vals.items():
        r.set(k, v)
    if r.values.get("ghi_chu_ban_quyen") in (None, ""):
        r.set("ghi_chu_ban_quyen", BAN_QUYEN)
    for col, _m, _e in COMMON:
        r.values.setdefault(col, "")
    return r


def join(items) -> str:
    return ";".join(dict.fromkeys(x for x in items if x not in (None, "")))


# ---------------------------------------------------------------------------------------------------------- so_sanh_that
def compare_sheet(book, name: str, title: str, entity_fk: list):
    sh = book.sheet(name, title, "So sánh game với thật (spec 12.4): mỗi thông số có đối chiếu một dòng; ty_le = game / "
                    "thật, khoảng cho phép, co_lech_lon = ngoài khoảng mà không có chủ đích (công thức sống)", layer="B")
    sh.col("entity_id", meaning="thực thể", fk=entity_fk, required=True)
    sh.col("thong_so", meaning="thông số đối chiếu")
    sh.col("don_vi", meaning="đơn vị của gia_tri_game và gia_tri_that")
    sh.col("gia_tri_game", meaning="giá trị trong game (tra sống sheet gốc cùng file, hoặc số bản kiểm tính)",
           formula="INDEX/MATCH sheet gốc (xem ô)", source_note="python: giá trị ô nguồn cùng file / Tools/balance/full_weapon_audit.py")
    sh.col("gia_tri_that", meaning="giá trị ngoài đời (tra sống sheet tham chiếu / input cùng file; nguồn ở nguon_id)",
           formula="INDEX/MATCH sheet tham chiếu (xem ô)", source_note="python: giá trị ô nguồn cùng file")
    sh.col("ty_le", meaning="game / thật [công thức sống]", formula="={gia_tri_game}/{gia_tri_that}",
           source_note="python: gia_tri_game / gia_tri_that")
    sh.col("khoang_min", meaning="cận dưới khoảng cho phép (trống: không bắt buộc, chỉ ghi ty_le)")
    sh.col("khoang_max", meaning="cận trên khoảng cho phép")
    sh.col("co_chu_dich", meaning="lệch có chủ đích (true khi nguồn repo ghi lý do)")
    sh.col("ly_do", meaning="lý do lệch có chủ đích (trích nguồn repo)")
    sh.col("co_lech_lon", meaning="true nếu ty_le ngoài khoảng và co_chu_dich = false [công thức sống]",
           formula="=IF(ISNUMBER({khoang_min}),AND(NOT({co_chu_dich}),OR({ty_le}<{khoang_min},{ty_le}>{khoang_max})),FALSE)",
           source_note="python: spec 12.4 co_lech_lon")
    sh.col("cho_quyet_id", meaning="dòng 12_he_thong_trang_thai/Cho_quyet khi co_lech_lon mà chưa có lý do",
           fk=["12_he_thong_trang_thai/Cho_quyet"])
    sh.col("nguon_id", meaning="nguồn của giá trị thật", fk=NGUON_FK)
    sh.col("ghi_chu", meaning="ghi chú (định nghĩa thông số)")
    return sh


LECH = "=IF(ISNUMBER({khoang_min}),AND(NOT({co_chu_dich}),OR({ty_le}<{khoang_min},{ty_le}>{khoang_max})),FALSE)"


def compare_row(sh, rid, entity, thong_so, unit, game, real, band, chu_dich: bool, ly_do: str, nguon_ids, note: str,
                nguon_text: str):
    """game / real: (template, python value) for a live lookup, or a plain number. Returns (row, co_lech_lon python)."""
    r = sh.row(rid, nguon_text)
    r.set("entity_id", entity)
    r.set("thong_so", thong_so)
    r.set("don_vi", unit)
    gv = _cell(r, "gia_tri_game", game)
    tv = _cell(r, "gia_tri_that", real)
    ratio = gv / tv if isinstance(gv, (int, float)) and isinstance(tv, (int, float)) and tv else None
    r.set("ty_le", F("={gia_tri_game}/{gia_tri_that}", expect=ratio, ref="python: gia_tri_game / gia_tri_that"))
    lo, hi = band if band else ("", "")
    r.set("khoang_min", lo)
    r.set("khoang_max", hi)
    r.set("co_chu_dich", bool(chu_dich))
    r.set("ly_do", ly_do if chu_dich else "")
    lech = bool(band) and ratio is not None and not chu_dich and (ratio < lo or ratio > hi)
    r.set("co_lech_lon", F(LECH, expect=lech, ref="python: spec 12.4 co_lech_lon"))
    r.set("cho_quyet_id", "")
    r.set("nguon_id", join(nguon_ids))
    r.set("ghi_chu", note)
    return r, lech


def _cell(r, col, spec):
    if isinstance(spec, tuple):
        tpl, val = spec
        r.set(col, F(tpl, expect=val, ref="python: giá trị ô nguồn cùng file"))
        return val
    r.set(col, spec)
    return spec


def look(sheet: str, col: str, key_col: str = "entity_id") -> str:
    return "=" + lookup(sheet, col, "{" + key_col + "}")


def marker_compare(book, name: str, title: str, note: str):
    sh = book.sheet(name, title, "So sánh game với thật (spec 12.4)", layer="B")
    sh.col("trang_thai", meaning="KHONG_CO: lĩnh vực không có thông số ngoài đời để đối chiếu")
    sh.col("ghi_chu", meaning="lý do")
    r = sh.row("khong_co", "spec 12.4 (lượt 10)")
    r.set("trang_thai", "KHONG_CO")
    r.set("ghi_chu", note)
    return sh
