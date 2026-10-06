"""Pass 10 for files 01-04 (spec 12.2-12.4): weapons, vehicles, bosses, towers / walls / HQ: <name>_tham_chieu and
<name>_so_sanh_that. Only repo data (see _refsrc.py). Tools/docs/unit_refs.json is exported here (its leaves map to the
tham_chieu sheets of 02 / 03 / 04, the stale branch keys to 04 under their base tower, _about to 13/Nguon_tham_chieu)."""
from __future__ import annotations

import re

from core.formula import F, lookup
from core.model import NEED_SOURCE

from . import _layer_b as LB
from . import _ref_common as C
from . import _refsrc as S

AUDIT_RULE = ("bản kiểm L1 (Tools/balance/full_weapon_audit.py) không cờ nhịp này: súng máy, pháo tự động, cao xạ so khe chậm "
              "với nhịp thực tế; rốc-két, bom và đồ treo máy bay chỉ so khoảng trong loạt")
GUIDE = "Docs/balance/Machine_Brigade_Can_bang.xlsx, sheet Hướng dẫn vẽ"
# 06/10 owner answer 3: NHANH_QUA / CHAM_QUA (full_weapon_audit.py TOO FAST / TOO SLOW, fire-cycle rate -- a different
# audit from the projectile flight validator) must carry a class-aware reason, never a stale flag with none. "Class"
# here is the real-world weapon kind (ngoai_doi_loai: mg/ac/aa/gun/rocket/missile/atgm/bomb) the rate was checked
# against; same reason-code names as Tools/balance/flight_feel_audit.py (TOO_FAST_FOR_CLASS / TOO_SLOW_FOR_CLASS).
KIND_LABEL = {"mg": "súng máy", "ac": "pháo tự động", "aa": "cao xạ", "gun": "pháo nòng dài (khe thật x1/0,7)",
              "rocket": "rốc-két (khoảng trong loạt)", "missile": "tên lửa", "atgm": "ATGM", "bomb": "bom/đồ treo máy bay"}


def name_of(row) -> str:
    for c in ("ten_vi", "ten", "name", "ten_en", "ten_that"):
        v = row.values.get(c)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return str(row.id)


def num(v):
    v = LB.F_value(v)
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


class Ctx:
    """What every builder of pass 10 reads once."""

    def __init__(self, ctx, reg: S.Registry):
        self.ctx, self.reg = ctx, reg
        self.refs = ctx.data(S.UNIT_REFS) if S.UNIT_REFS in ctx.sources else {}
        self.sizes = (ctx.data(S.REAL_SIZES) or {}).get("units", {}) if S.REAL_SIZES in ctx.sources else {}
        self.usheet = (ctx.data(S.UNIT_SHEET) or {}).get("units", {}) if S.UNIT_SHEET in ctx.sources else {}
        self.real, self.warhead, self.warhead_note, self.slower = S.audit_literals()
        self.reasons = ctx.data(S.REASONS) if S.REASONS in ctx.sources else {}
        self.cb = {}
        for sheet, key in (("Phương tiện", "Tham khảo (ngoài đời / game)"), ("Công trình", "Tham khảo (ngoài đời / game)"),
                           ("Boss", "Tham khảo (ngoài đời / game)"), ("Vũ khí đề xuất", "Ngoài đời")):
            for r in S.xlsx_rows(S.CAN_BANG, sheet):
                t = S.text(r.get(key))
                if r.get("id") and t:
                    self.cb[str(r["id"]).strip()] = t
        self.cb_changes = {}
        for r in S.xlsx_rows(S.CAN_BANG, "Thay đổi chi tiết"):
            t = S.text(r.get("Tham khảo (ngoài đời / game)"))
            if r.get("id") and t:
                self.cb_changes.setdefault(str(r["id"]).strip(), []).append(t)
        self.guide_rows = {S.text(r.get("Mục")): S.text(r.get(list(r)[1])) for r in S.xlsx_rows(S.CAN_BANG, "Hướng dẫn vẽ")}
        self.builders = {}
        for b in S.builder_notes():
            for i in b["ids"]:
                self.builders.setdefault(i, []).append(b)
        self.specs = {}
        for sid in sorted(s for s in ctx.sources if s.startswith(S.SPECS) and s.endswith(".json")):
            d = ctx.data(sid) or {}
            self.specs[d.get("id") or sid.rsplit("/", 1)[-1][:-5]] = (sid, d)
        self.dec = S.decisions_lines()
        self.used_refs: set[str] = set()
        self.cho_quyet: list[tuple] = []   # (file, sheet, row id, text) of co_lech_lon rows with no reason
        # repo documents
        R = reg.repo
        self.N_REFS = R(S.UNIT_REFS, "unit_refs.json (tham chiếu ngoài đời / phim / game theo đơn vị)",
                        note=(self.refs.get("_about") or "") if isinstance(self.refs, dict) else "")
        self.N_SIZES = R(S.REAL_SIZES, "reference_real.json (kích thước thật, độ tin conf)",
                         note="bản người đọc: Docs/models/reference_dimensions.md")
        self.N_USHEET = R(S.UNIT_SHEET, "unit_sheet.json (hình dạng, mô tả từ bảng cân bằng)")
        self.N_AUDIT = R(S.AUDIT, "full_weapon_audit.py: bảng REAL (nhịp bắn thật, mỗi dòng kèm nguồn) và WARHEAD",
                         note="đầu bảng ghi: số của nhà sản xuất và quân đội theo Jane's và các bài Wikipedia nêu tên (đọc "
                              "2026-10-02); 'est.' khi không có số công bố")
        self.N_CB = R(S.CAN_BANG, "Rà soát cân bằng (Machine_Brigade_Can_bang.xlsx)",
                      note="sheet Tổng quan: giá và thông số ngoài đời là ước lượng từ thông tin công khai, chỉ để so thứ tự")
        self.N_BAL = R("Assets/MachineBrigade/Resources/Data/balance.json", "balance.json: tên thật của vũ khí (weapons[].real)")
        self.N_REASONS = R(S.REASONS, "fix_weapon_reasons.json (lý do sửa nhịp / số của từng vũ khí)")
        self.N_DEC = R(S.DECISIONS, "Docs/DECISIONS.md (nhật ký quyết định)")
        self.N_DIMS = R(S.REF_DIMS, "reference_dimensions.md (kích thước thật so với model)")
        self.N_WARHEAD = reg.add("wikipedia", f"Wikipedia (bài của từng tên lửa; bảng WARHEAD: {self.warhead_note})",
                                 ngay_truy_cap="2026-10-02", trich_tu=S.AUDIT,
                                 ghi_chu="bảng WARHEAD ghi nguồn chung, không ghi tên từng bài") if self.warhead else ""

    # ------------------------------------------------------------------ unit_refs
    def unit_ref(self, sh, row, key: str, col_real="ten_mau_that"):
        """Writes (and marks) the unit_refs record of key into the tham_chieu row. Returns (real names, games, films, note,
        mechanics)."""
        rec = self.refs.get(key) if isinstance(self.refs, dict) else None
        if not isinstance(rec, dict):
            return [], [], [], "", []
        self.used_refs.add(key)
        src = S.UNIT_REFS
        real = [x for x in rec.get("real", []) if isinstance(x, str)]
        row.set(col_real, C.join(real))
        if real:
            for i in range(len(rec["real"])):
                row.mark(src, (key, "real", i), col_real)
        else:
            row.mark(src, (key, "real"), col_real)
        games, films, mech = [], [], []
        for i, m in enumerate(rec.get("media", [])):
            mm = re.match(r"^(.*?)\s*\(([^()]*)\)\s*(?::\s*(.*))?$", m)
            thing, work, detail = (mm.group(1), mm.group(2), mm.group(3) or "") if mm else (m, m, "")
            if re.fullmatch(r"\d{4}", work.strip()):
                work = thing
            elif S.known_game(thing) and not S.known_game(work):
                thing, work = work, thing  # 'Red Alert 2 (Flak Cannon)': the game outside, the thing inside
            target = "ten_phim_truyen" if S.is_film(m) else "ten_game"
            (films if target == "ten_phim_truyen" else games).append(work.strip())
            if target == "ten_game":
                mech.append(f"hình dáng: {thing.strip()}" + (f" ({detail.strip()})" if detail else ""))
            row.mark(src, (key, "media", i), target)
        if not rec.get("media"):
            row.mark(src, (key, "media"), "ten_game")
        note = rec.get("note", "")
        row.set("ghi_chu_unit_refs", note, src, (key, "note"))
        return real, games, films, note, mech


# ---------------------------------------------------------------------------------------------------------- 01 weapons
W_EXTRA = [
    ("ngoai_doi_co_mm", "mm", "cỡ nòng thật (số 'NN mm' trong tên thật của balance.json; NEED_SOURCE nếu tên không ghi)"),
    ("ngoai_doi_khoi_luong_dan_kg", "kg", "khối lượng viên đạn thật"),
    ("ngoai_doi_so_toc_dau_nong_m_s", "m/s", "sơ tốc đầu nòng thật"),
    ("ngoai_doi_tam_hieu_qua_m", "m", "tầm hiệu quả thật"),
    ("ngoai_doi_tam_toi_da_m", "m", "tầm tối đa thật"),
    ("ngoai_doi_phat_phut_toi_da", "phát/phút", "nhịp tối đa thật (bảng REAL)"),
    ("ngoai_doi_phat_phut_duy_tri", "phát/phút", "nhịp duy trì / thực tế thật (bảng REAL)"),
    ("ngoai_doi_nap", "", "nạp tay / tự động (chỉ khi nguồn bảng REAL ghi 'loader' / 'autoloader' / 'manual')"),
    ("ngoai_doi_khoi_luong_thuoc_no_kg", "kg", "khối lượng thuốc nổ thật"),
    ("ngoai_doi_khoi_luong_dau_dan_kg", "kg", "khối lượng đầu đạn tên lửa (bảng WARHEAD; không phải thuốc nổ)"),
    ("ngoai_doi_loai_nhip", "", "loại trong bảng REAL (mg, ac, aa, gun, rocket, atgm, missile, bomb)"),
    ("ngoai_doi_nguon_ghi", "", "nguồn như bảng REAL ghi (văn bản gốc của repo)"),
    ("ngoai_doi_bang_can_bang", "", "cột 'Ngoài đời' của sheet Vũ khí đề xuất (Machine_Brigade_Can_bang.xlsx)"),
]
WARHEAD_FAMS = {"atgm", "aa_missile", "missile", "cruise", "cruise_missile", "ballistic"}


def build_01(R: Ctx, book):
    ctx = R.ctx
    vk = book.sheets["Vu_khi"]
    sr = book.sheets.get("Vu_khi_suy_ra")
    sh = C.ref_sheet(book, "Vu_khi_tham_chieu", "Vũ khí: tham chiếu ngoài đời", "Mỗi vũ khí một dòng: mẫu thật (tên thật "
                     "balance.json), nhịp thật (bảng REAL), đầu đạn (WARHEAD), ghi chú bảng cân bằng", ["01_vu_khi_dan/Vu_khi"],
                     W_EXTRA)
    for wid, w in sorted(vk.rows.items(), key=lambda x: str(x[0])):
        real_name = (w.values.get("ten_that") or "").strip()
        hit = S.real_hit(R.real, real_name)
        nguon, tins = [], []
        loai = "doi_that" if real_name else NEED_SOURCE
        vals = {"ten_hien_thi": real_name or str(wid), "loai_tham_chieu": loai, "ten_mau_that": real_name}
        if real_name:
            nguon.append(R.N_BAL)
        m = re.search(r"(\d+(?:[.,]\d+)?)\s*mm\b", real_name)
        vals["ngoai_doi_co_mm"] = float(m.group(1).replace(",", ".")) if m else C.real_blank(loai)
        for c in ("ngoai_doi_khoi_luong_dan_kg", "ngoai_doi_so_toc_dau_nong_m_s", "ngoai_doi_tam_hieu_qua_m",
                  "ngoai_doi_tam_toi_da_m", "ngoai_doi_khoi_luong_thuoc_no_kg"):
            vals[c] = C.real_blank(loai)
        if hit:
            pat, rpm, prac, kind, _mount, src = hit
            ids, external = R.reg.cite(src, S.AUDIT, accessed="2026-10-02")
            nguon += [R.N_AUDIT] + ids
            tin = "uoc_dinh" if S.is_estimate(src) else ("da_kiem_chung" if external else "ban_dau_doan")
            tins.append(tin)
            vals.update(ngoai_doi_phat_phut_toi_da=rpm, ngoai_doi_phat_phut_duy_tri=prac if prac is not None else NEED_SOURCE,
                        ngoai_doi_loai_nhip=kind, ngoai_doi_nguon_ghi=src)
            low = src.lower()
            vals["ngoai_doi_nap"] = ("tu_dong" if "autoloader" in low else "tay" if ("with a loader" in low or "manual" in low)
                                     else C.real_blank(loai))
            if kind == "gun":
                vals["diem_khac_co_chu_dich"] = "nhịp chậm hơn 30 % và mạnh hơn tương ứng (luật súng của game)"
                vals["ly_do_khac"] = "gameplay"
        else:
            vals.update(ngoai_doi_phat_phut_toi_da=C.real_blank(loai), ngoai_doi_phat_phut_duy_tri=C.real_blank(loai),
                        ngoai_doi_nap=C.real_blank(loai), ngoai_doi_loai_nhip="", ngoai_doi_nguon_ghi="")
        wh = R.warhead.get(real_name.lower()) if real_name else None
        fam = (w.values.get("nhom") or "")
        if wh is not None:
            vals["ngoai_doi_khoi_luong_dau_dan_kg"] = wh
            nguon += [R.N_AUDIT, R.N_WARHEAD] if R.N_WARHEAD else [R.N_AUDIT]
            tins.append("da_kiem_chung" if R.N_WARHEAD else "ban_dau_doan")
        else:
            vals["ngoai_doi_khoi_luong_dau_dan_kg"] = C.real_blank(loai) if fam in WARHEAD_FAMS else ""
        cbt = R.cb.get(str(wid), "")
        vals["ngoai_doi_bang_can_bang"] = cbt
        if cbt:
            nguon.append(R.N_CB)
            if S.is_estimate(cbt):
                tins.append("uoc_dinh")
        if loai == NEED_SOURCE:
            vals["ly_do"] = "balance.json không ghi tên thật cho vũ khí này"
        vals["do_tin_cay"] = C.reliability(loai, False, tins)
        vals["nguon_id"] = C.join(nguon)
        C.put_row(sh, wid, wid, f"{S.AUDIT}: REAL / WARHEAD; balance.json weapons[id={wid}].real", vals)

    # ------------------------------------------------------------------ Vu_khi_so_sanh_that
    cs = C.compare_sheet(book, "Vu_khi_so_sanh_that", "Vũ khí: so sánh với thật", ["01_vu_khi_dan/Vu_khi"])
    for wid in sorted(vk.rows, key=str):
        w = vk.rows[wid]
        t = sh.rows[wid]
        rpm, kind = num(w.values.get("ngoai_doi_phat_phut_toi_da")), w.values.get("ngoai_doi_loai")
        ratio = num(sr.rows[wid].values.get("ty_le_chu_ky_so_voi_ngoai_doi")) if sr is not None and wid in sr.rows else None
        if rpm and ratio is not None:
            ref = 60.0 / rpm / (R.slower if kind == "gun" else 1.0)
            flags = str(sr.rows[wid].values.get("ghi_chu_lech") or "")
            chu, why = _rate_reason(R, wid, ratio, flags, kind)
            tpl = ("=60/" + lookup("Vu_khi", "ngoai_doi_phat_phut_toi_da", "{entity_id}") + "/IF("
                   + lookup("Vu_khi", "ngoai_doi_loai", "{entity_id}") + f'="gun",{R.slower},1)')
            _r, lech = C.compare_row(cs, f"{wid}/nhip", wid, "khe_mot_nong_mot_vien", "s", round(ref * ratio, 9), (tpl, ref),
                                     C.RATE, chu, why, t.values["nguon_id"].split(";"),
                                     "game: chu kỳ × số nòng / số viên của bản kiểm L1 (rốc-két, đồ treo: khoảng trong loạt); "
                                     "thật: 60 / nhịp tối đa (súng: chia 0,7, luật chậm hơn 30 %); ty_le = "
                                     "Vu_khi_suy_ra.ty_le_chu_ky_so_voi_ngoai_doi", f"{S.AUDIT} (bảng REAL) và 01/Vu_khi_suy_ra")
            if lech:
                R.cho_quyet.append(("01_vu_khi_dan", cs.name, f"{wid}/nhip", f"nhịp {wid}: ty_le {ratio:.3g} ngoài 0,6–2, "
                                    f"cờ {flags or 'không'}; chưa có lý do ở fix_weapon_reasons.json"))
        kg = num(t.values.get("ngoai_doi_khoi_luong_dau_dan_kg"))
        dmg, core = num(w.values.get("sat_thuong_moi_phat")), num(w.values.get("loi_m"))
        if kg and dmg:
            C.compare_row(cs, f"{wid}/sat_thuong", wid, "sat_thuong_tren_kg_dau_dan", "hp/kg",
                          (C.look("Vu_khi", "sat_thuong_moi_phat"), dmg), (C.look("Vu_khi_tham_chieu", "ngoai_doi_khoi_luong_dau_dan_kg"), kg),
                          None, False, "", [R.N_AUDIT], "sát thương một phát / khối lượng đầu đạn (không bắt buộc 1:1, chỉ ghi ty_le)",
                          f"{S.AUDIT} WARHEAD")
        if kg and core:
            C.compare_row(cs, f"{wid}/loi_no", wid, "loi_m_tren_can_bac_ba_kg_dau_dan", "m/kg^(1/3)",
                          (C.look("Vu_khi", "loi_m"), core),
                          ("=POWER(" + lookup("Vu_khi_tham_chieu", "ngoai_doi_khoi_luong_dau_dan_kg", "{entity_id}") + ",1/3)",
                           kg ** (1 / 3)), None, False, "", [R.N_AUDIT],
                          "lõi nổ / căn bậc ba khối lượng đầu đạn (đầu đạn thay cho thuốc nổ: repo không có khối lượng thuốc nổ)",
                          f"{S.AUDIT} WARHEAD")
    return sh, cs


def _rate_reason(R: Ctx, wid, ratio, flags: str, kind: str = ""):
    lo, hi = C.RATE
    if lo <= ratio <= hi:
        return False, ""
    if wid in R.reasons:
        return True, f"fix_weapon_reasons.json: {str(R.reasons[wid])[:300]}"
    if "NHANH_QUA" not in flags and "CHAM_QUA" not in flags:
        return True, AUDIT_RULE
    # 06/10 owner answer 3: this flag (NHANH_QUA/CHAM_QUA) has no fix_weapon_reasons.json entry -- give it a
    # class-aware reason instead of leaving it stale (the old `return False, ""` here dropped it silently).
    code = "TOO_FAST_FOR_CLASS" if ratio < lo else "TOO_SLOW_FOR_CLASS"
    label = KIND_LABEL.get(kind, kind or "không rõ loại")
    return True, (f"{code} ({label}): tỷ lệ khe {ratio:.3g} ngoài ngưỡng [{lo:g};{hi:g}] của bản kiểm nhịp bắn; "
                  "chưa có lý do riêng trong fix_weapon_reasons.json")


# ---------------------------------------------------------------------------------------------------------- units
U_EXTRA = [
    ("ngoai_doi_dai_m", "m", "dài thật (reference_real.json qua input_kich_thuoc_that, tra sống)"),
    ("ngoai_doi_rong_m", "m", "rộng thật (như trên)"),
    ("ngoai_doi_cao_m", "m", "cao thật (như trên)"),
    ("ngoai_doi_mau_kich_thuoc", "", "mẫu thật lấy kích thước (reference_real.json ref)"),
    ("do_tin_cay_kich_thuoc", "", "conf của reference_real.json: high / approx / inspiration / none"),
    ("tham_chieu_kich_thuoc", "", "tỷ lệ vẽ so với mẫu thật như nguồn ghi (vd. '0,8 × Flakpanzer Gepard')"),
    ("ghi_chu_unit_refs", "", "ghi chú nguyên văn của unit_refs.json (nhãn 'ước đoán' giữ nguyên)"),
    ("tham_khao_bang_can_bang", "", "cột 'Tham khảo (ngoài đời / game)' của bảng cân bằng (Machine_Brigade_Can_bang.xlsx)"),
    ("tham_khao_bang_thay_doi", "", "cột tham khảo của sheet Thay đổi chi tiết (ngăn ' | ')"),
    ("nam_ghi_trong_nguon", "", "năm trong ngoặc ở văn bản tham khảo của bảng cân bằng (năm thiết kế / ra mắt như nguồn ghi; "
                                "không phải chắc chắn năm đưa vào sử dụng)"),
    ("ghi_chu_dung_model", "", "ghi chú tham chiếu trong docstring script Blender / spec prompt 35"),
]
V_EXTRA = [
    ("ngoai_doi_khoi_luong_t", "t", "khối lượng thật"),
    ("ngoai_doi_toc_do_toi_da_km_h", "km/h", "tốc độ tối đa thật"),
    ("ngoai_doi_giap", "", "giáp thật (mô tả)"),
    ("ngoai_doi_to_lai", "", "số người tổ lái"),
    ("ngoai_doi_dong_co_cong_suat_kw", "kW", "công suất động cơ"),
    ("ngoai_doi_tam_hoat_dong_km", "km", "tầm hoạt động"),
]
B_EXTRA = [
    ("phan_lay_tu_mau", "", "phần nào của boss lấy từ mẫu nào (hình dạng 'Dựa trên: ...' của bảng cân bằng)"),
    ("he_so_phong_to", "", "hệ số phóng to so với mẫu thật như nguồn ghi"),
    ("phan_gia_tuong", "", "phần giả tưởng (nguồn ghi)"),
]
T_EXTRA = [
    ("loai_cong_trinh", "", "Thap / Tuong / Nha_chinh / Mo_dun_tien_ich"),
    ("nhanh", "", "nhánh (phần sau dấu chấm của id)"),
    ("ngoai_doi_vat_lieu", "", "vật liệu thật (tường)"),
]
WALLS = {  # entity: (real name as the repo line writes it, the DECISIONS phrase that must exist, model note)
    "wall_hesco": ("HESCO", "`segmentHp` 2400 (HESCO)", "model: ba khoang rọ đá 4 m trên ụ đất, dây thép gai (DECISIONS, "
                                                         "Models của mb_p32_walls.py)"),
    "wall_t": ("T-wall", "five precast T-wall panels", "model: năm tấm T-wall đúc sẵn (DECISIONS, Models của mb_p32_walls.py)"),
}
YEAR = re.compile(r"\((1[89]\d\d|20[0-2]\d)\)")


def _size_input(R: Ctx, book, ids):
    kt = R.ctx.books.get("10_model_tai_san", None)
    kt = kt.sheets.get("Kich_thuoc_that") if kt else None
    if kt is None:
        return None
    rows = {}
    for e in ids:
        if e in kt.rows:
            v = kt.rows[e].values
            rows[e] = {"dai_m": v.get("size_dai_m", ""), "rong_m": v.get("size_rong_m", ""), "cao_m": v.get("size_cao_m", ""),
                       "mau": v.get("ref", ""), "conf": v.get("conf", ""), "nguon_ghi": v.get("source", "")}
    if not rows:
        return None
    return LB.input_sheet(R.ctx, book, "input_kich_thuoc_that", "Kích thước thật (chép từ 10)", "10_model_tai_san",
                          "Kich_thuoc_that", [("dai_m", "size_dai_m", "m", "dài thật"), ("rong_m", "size_rong_m", "m", "rộng thật"),
                                              ("cao_m", "size_cao_m", "m", "cao thật"), ("mau", "ref", "", "mẫu thật"),
                                              ("conf", "conf", "", "độ tin"), ("nguon_ghi", "source", "", "nguồn ghi")], rows)


def unit_rows(R: Ctx, book, sh, entities, kind: str, inp):
    """entities: [(row id, entity id, display name, unit_refs key, flags dict)]"""
    for col in ("ngoai_doi_dai_m", "ngoai_doi_rong_m", "ngoai_doi_cao_m"):
        sh.col(col, formula="INDEX/MATCH input_kich_thuoc_that", source_note="python: chép sống từ input_kich_thuoc_that")
    for rid, ent, disp, key, flags in entities:
        r = sh.row(rid, f"{S.UNIT_REFS}: {key}; {S.REAL_SIZES}: units.{ent}", raw=None)
        r.set("entity_id", ent)
        real, games, films, note, mech = R.unit_ref(sh, r, key)
        size = R.sizes.get(ent) if isinstance(R.sizes, dict) else None
        nguon = [R.N_REFS] if key in R.used_refs else []
        tins = []
        vals = {"ten_hien_thi": disp, "ten_game": C.join(games), "ten_phim_truyen": C.join(films), "co_che_game": C.join(mech)}
        wall = WALLS.get(ent)
        wall_hit = S.decisions_find(R.dec, wall[1]) if wall else None
        if wall_hit and not real:
            real = [wall[0]]
            r.set("ten_mau_that", wall[0])
            vals["diem_giong"] = wall[2]
            nguon.append(R.N_DEC)
        conf = (size or {}).get("conf", "")
        if real:
            loai = "doi_that"
        elif conf == "inspiration":
            loai = "gia_tuong"
        elif games:
            loai = "game"
        elif films:
            loai = "phim_truyen"
        else:
            loai = NEED_SOURCE
        vals["loai_tham_chieu"] = loai
        if note and "diem_giong" not in vals:
            vals["diem_giong"] = re.sub(r"^ước đoán:\s*", "", note)
        # sizes
        if size:
            nguon.append(R.N_SIZES)
            ids, external = R.reg.cite(size.get("source", ""), S.REAL_SIZES)
            nguon += ids
            vals["ngoai_doi_mau_kich_thuoc"] = size.get("ref", "")
            vals["do_tin_cay_kich_thuoc"] = conf
            if conf == "high" and external:
                tins.append("da_kiem_chung")
            elif conf == "approx":
                tins.append("uoc_dinh")
            if conf == "inspiration":
                vals["ly_do"] = f"reference_real.json: {size.get('source', '')} (mẫu '{size.get('ref', '')}', thiết kế giả tưởng)"
                vals["ly_do_khac"] = "gia_tuong"
            mm = re.search(r"\(drawn ([\d.]+) x\)", size.get("ref", ""))
            if mm:
                vals["tham_chieu_kich_thuoc"] = f"{mm.group(1).replace('.', ',')} × {size['ref'].split(' (')[0]}"
        if inp is not None and ent in inp.rows:
            for col, src in (("ngoai_doi_dai_m", "dai_m"), ("ngoai_doi_rong_m", "rong_m"), ("ngoai_doi_cao_m", "cao_m")):
                v = num(inp.rows[ent].values.get(src))
                vals[col] = F(C.look("input_kich_thuoc_that", src), expect=v, ref="python: input_kich_thuoc_that") \
                    if v is not None else C.real_blank(loai)
        else:
            for col in ("ngoai_doi_dai_m", "ngoai_doi_rong_m", "ngoai_doi_cao_m"):
                vals[col] = C.real_blank(loai)
        us = R.usheet.get(ent) or {}
        shape = us.get("shape", "") if isinstance(us, dict) else ""
        mm = re.search(r"([\d]+,[\d]+) × mẫu thật ([^)]+)\)", shape)
        if mm and not vals.get("tham_chieu_kich_thuoc"):
            vals["tham_chieu_kich_thuoc"] = f"{mm.group(1)} × {mm.group(2).strip()}"
            nguon.append(R.N_USHEET)
        cbt = R.cb.get(ent, "")
        vals["tham_khao_bang_can_bang"] = cbt
        ch = R.cb_changes.get(ent, [])
        vals["tham_khao_bang_thay_doi"] = " | ".join(ch)
        if cbt or ch:
            nguon.append(R.N_CB)
        years = sorted(set(YEAR.findall(cbt)))
        vals["nam_ghi_trong_nguon"] = ";".join(years)
        notes = [f"{b['file']}: {b['text']}" for b in R.builders.get(ent, [])]
        if ent in R.specs:
            sid, d = R.specs[ent]
            notes.append(f"{sid}: real = {'; '.join(d.get('real', []))}; confidence = {d.get('confidence', '')}")
            nguon.append(R.reg.repo(sid, f"spec dựng lại {ent} (prompt 35)"))
        for b in R.builders.get(ent, []):
            nguon.append(R.reg.repo(b["file"], f"script Blender {b['file'].rsplit('/', 1)[-1]} (docstring)"))
        vals["ghi_chu_dung_model"] = " || ".join(notes)[:1500]
        card = flags.get("sheet") == "The_ho_tro"
        for c in ("quoc_gia", "nam_dua_vao_su_dung"):
            vals[c] = C.real_blank(loai)
        for col, _u, _m in V_EXTRA if kind == "xe" else []:
            vals[col] = "" if card else C.real_blank(loai)
        if card:
            for col in ("ngoai_doi_dai_m", "ngoai_doi_rong_m", "ngoai_doi_cao_m"):
                if vals.get(col) == NEED_SOURCE:
                    vals[col] = ""
        if kind == "boss":
            mm = re.search(r"Dựa trên:\s*(.+?)(?:\.\s|$)", shape)
            vals["phan_lay_tu_mau"] = mm.group(1).strip()[:400] if mm else ""
            if mm:
                nguon.append(R.N_USHEET)
            vals["he_so_phong_to"] = vals.get("tham_chieu_kich_thuoc", "") or ("boss ×1,3–1,5 so với mẫu gốc (" + GUIDE + ")"
                                                                              if real else "")
            fict = []
            if size and conf == "inspiration":
                fict.append(f"reference_real.json: {size.get('source', '')}")
            if note.startswith("ước đoán"):
                fict.append("unit_refs.json ghi ước đoán")
            vals["phan_gia_tuong"] = "; ".join(fict)
        if kind == "can_cu":
            vals["loai_cong_trinh"] = flags.get("sheet", "")
            vals["nhanh"] = ent.split(".", 1)[1] if "." in ent else ""
            vals["ngoai_doi_vat_lieu"] = C.real_blank(loai) if flags.get("sheet") == "Tuong" else ""
            if flags.get("orphan"):
                vals["ly_do"] = (f"khóa '{key}' của unit_refs.json không còn là thực thể (nhánh cũ; {ent} giờ noBranch): "
                                 "giữ để không mất ghi chú")
        if loai == NEED_SOURCE and not vals.get("ly_do"):
            vals["ly_do"] = "repo không có tham chiếu cho thực thể này (unit_refs.json, reference_real.json, bảng cân bằng)"
        vals["do_tin_cay"] = C.reliability(loai, note.startswith("ước đoán"), tins)
        vals["nguon_id"] = C.join(nguon)
        for k, v in vals.items():
            r.set(k, v)
        r.set("ghi_chu_ban_quyen", C.BAN_QUYEN)
        for col, _m, _e in C.COMMON:
            r.values.setdefault(col, "")


def compare_units(R: Ctx, book, ref_sh, main_sheet: str, entities, name: str, title: str, boss: bool = False):
    """Size rows (dài / rộng / cao, band 0.7-1.4) and proportion rows (W/L, H/L, band 0.9-1.1) of every entity with both a
    modelSize in its sheet and a real size."""
    fid = book.file_id
    cs = C.compare_sheet(book, name, title, ref_sh.cols["entity_id"].fk)
    ms = book.sheets[main_sheet]
    air_rule = R.guide_rows.get("Tỷ lệ", "") or next((v for v in R.guide_rows.values() if "0,4" in v), "")
    for rid, ent, _disp, _key, flags in entities:
        if rid not in ref_sh.rows or ent not in ms.rows:
            continue
        mv = ms.rows[ent].values
        rv = ref_sh.rows[rid].values
        game = {k: num(mv.get(f"model_size_{k}_m")) for k in ("length", "width", "height")}
        real = {k: LB.F_value(rv.get(f"ngoai_doi_{c}_m")) for k, c in (("length", "dai"), ("width", "rong"), ("height", "cao"))}
        real = {k: (v if isinstance(v, (int, float)) and not isinstance(v, bool) else None) for k, v in real.items()}
        nguon = [x for x in rv.get("nguon_id", "").split(";") if x]
        size = R.sizes.get(ent, {})
        flying = bool(mv.get("bay")) and str(mv.get("bay")).lower() not in ("false", "0", "")
        naval = bool(str(mv.get("naval_role") or "").strip())
        if boss:
            why = (f"{GUIDE}: boss ×1,3–1,5 so với mẫu gốc; {S.REF_DIMS}: game vẽ máy bay và tàu nhỏ hơn thật có chủ đích "
                   "(chỉ chấm tỷ lệ W/L, H/L)")
        elif flying:
            why = f"{GUIDE}: máy bay, trực thăng 0,4 × thật" + (f" ({air_rule[:160]})" if air_rule and "0,4" in air_rule else "")
        elif naval:
            why = f"{S.REF_DIMS}: game vẽ máy bay và tàu nhỏ hơn thật có chủ đích (chỉ chấm tỷ lệ W/L, H/L)"
        else:
            why = ""
        for k, c, label in (("length", "dai", "dai_m"), ("width", "rong", "rong_m"), ("height", "cao", "cao_m")):
            if game[k] is None or real[k] is None:
                continue
            ratio = game[k] / real[k]
            lo, hi = C.SPEED_SIZE
            chu = bool(why) and not (lo <= ratio <= hi)
            _r, lech = C.compare_row(cs, f"{rid}/{label}", ent, label, "m",
                                     (C.look(main_sheet, f"model_size_{k}_m"), game[k]),
                                     ("=" + lookup(ref_sh.name, f"ngoai_doi_{c}_m", f'"{rid}"'), real[k]), C.SPEED_SIZE, chu,
                                     why, nguon, "modelSize của dữ liệu / kích thước thật (reference_real.json)",
                                     f"{fid}/{main_sheet}.model_size_{k}_m; {S.REAL_SIZES}")
            if lech:
                R.cho_quyet.append((fid, cs.name, f"{rid}/{label}", f"{ent} {label}: ty_le {ratio:.3g} ngoài 0,7–1,4, chưa có lý do"))
        for k, c, label in (("width", "rong", "rong_tren_dai"), ("height", "cao", "cao_tren_dai")):
            if None in (game[k], game["length"], real[k], real["length"]) or not game["length"] or not real["length"]:
                continue
            g, t = game[k] / game["length"], real[k] / real["length"]
            ratio = g / t
            judge = size.get("judge")
            chu = bool(judge) and label[0] != judge[0] and not (C.SHAPE[0] <= ratio <= C.SHAPE[1])
            why2 = (f"reference_real.json: judge = '{judge}' (chỉ chấm chiều này); {size.get('source', '')}" if chu else "")
            _r, lech = C.compare_row(
                cs, f"{rid}/{label}", ent, label, "",
                ("=" + lookup(main_sheet, f"model_size_{k}_m", "{entity_id}") + "/" + lookup(main_sheet, "model_size_length_m",
                                                                                            "{entity_id}"), g),
                ("=" + lookup(ref_sh.name, f"ngoai_doi_{c}_m", f'"{rid}"') + "/" + lookup(ref_sh.name, "ngoai_doi_dai_m", f'"{rid}"'),
                 t), C.SHAPE, chu, why2, nguon, "tỷ lệ hình (MODEL_STANDARD 3.1: lệch quá 10 % là cờ)",
                f"{fid}/{main_sheet}; {S.REAL_SIZES}")
            if lech:
                R.cho_quyet.append((fid, cs.name, f"{rid}/{label}", f"{ent} {label}: tỷ lệ hình lệch {ratio:.3g} (ngoài 0,9–1,1, "
                                    "MODEL_STANDARD 3.1), chưa có lý do"))
    return cs


def rate_inputs(R: Ctx, book, weapons: set):
    """input_nhip_that (01/Vu_khi) and input_ty_le_nhip (01/Vu_khi_suy_ra) for the weapons with a real rate."""
    vk = R.ctx.books["01_vu_khi_dan"].sheets["Vu_khi"]
    sr = R.ctx.books["01_vu_khi_dan"].sheets["Vu_khi_suy_ra"]
    keep = sorted(w for w in weapons if w in vk.rows and w in sr.rows and num(vk.rows[w].values.get("ngoai_doi_phat_phut_toi_da"))
                  and num(sr.rows[w].values.get("ty_le_chu_ky_so_voi_ngoai_doi")) is not None)
    a = LB.input_sheet(R.ctx, book, "input_nhip_that", "Nhịp thật (chép từ 01)", "01_vu_khi_dan", "Vu_khi",
                       [("ngoai_doi_phat_phut_toi_da", "ngoai_doi_phat_phut_toi_da", "phát/phút", "nhịp tối đa thật"),
                        ("ngoai_doi_loai", "ngoai_doi_loai", "", "loại bảng REAL"),
                        ("ngoai_doi_nguon", "ngoai_doi_nguon", "", "nguồn bảng REAL")],
                       {w: {c: LB.source_value(R.ctx, "01_vu_khi_dan", "Vu_khi", w, c)
                            for c in ("ngoai_doi_phat_phut_toi_da", "ngoai_doi_loai", "ngoai_doi_nguon")} for w in keep})
    b = LB.input_sheet(R.ctx, book, "input_ty_le_nhip", "Tỷ lệ nhịp của bản kiểm (chép từ 01)", "01_vu_khi_dan", "Vu_khi_suy_ra",
                       [("ty_le_chu_ky_so_voi_ngoai_doi", "ty_le_chu_ky_so_voi_ngoai_doi", "", "tỷ lệ khe game / khe thật"),
                        ("ghi_chu_lech", "ghi_chu_lech", "", "cờ bản kiểm")],
                       {w: {c: LB.source_value(R.ctx, "01_vu_khi_dan", "Vu_khi_suy_ra", w, c)
                            for c in ("ty_le_chu_ky_so_voi_ngoai_doi", "ghi_chu_lech")} for w in keep})
    return a, b, set(keep)


def rate_rows(R: Ctx, book, cs, pairs, a, b, keep, who: str):
    """One rate row per (entity, weapon) with a real rate (live: the real gap from input_nhip_that)."""
    cs.col("vu_khi_id", meaning="vũ khí (01_vu_khi_dan/Vu_khi)", fk=["01_vu_khi_dan/Vu_khi"])
    t01 = R.ctx.books["01_vu_khi_dan"].sheets.get("Vu_khi_tham_chieu")
    for ent, wid in sorted(set(pairs)):
        if wid not in keep:
            continue
        rpm = num(a.rows[wid].values["ngoai_doi_phat_phut_toi_da"])
        kind = a.rows[wid].values["ngoai_doi_loai"]
        ratio = num(b.rows[wid].values["ty_le_chu_ky_so_voi_ngoai_doi"])
        flags = str(b.rows[wid].values.get("ghi_chu_lech") or "")
        ref = 60.0 / rpm / (R.slower if kind == "gun" else 1.0)
        chu, why = _rate_reason(R, wid, ratio, flags, kind)
        tpl = ("=60/" + lookup("input_nhip_that", "ngoai_doi_phat_phut_toi_da", "{vu_khi_id}") + "/IF("
               + lookup("input_nhip_that", "ngoai_doi_loai", "{vu_khi_id}") + f'="gun",{R.slower},1)')
        nguon = t01.rows[wid].values.get("nguon_id", "").split(";") if t01 is not None and wid in t01.rows else [R.N_AUDIT]
        r, lech = C.compare_row(cs, f"{ent}/{wid}/nhip", ent, "khe_mot_nong_mot_vien", "s", round(ref * ratio, 9), (tpl, ref),
                                C.RATE, chu, why, nguon, f"nhịp {who} so với hệ thống thật (định nghĩa như 01/Vu_khi_so_sanh_that)",
                                f"{S.AUDIT} (bảng REAL) qua input_nhip_that / input_ty_le_nhip")
        r.set("vu_khi_id", wid)
        if lech:
            R.cho_quyet.append((book.file_id, cs.name, f"{ent}/{wid}/nhip", f"nhịp {wid} trên {ent}: ty_le {ratio:.3g} ngoài "
                                f"0,6–2, cờ {flags or 'không'}; chưa có lý do"))
    for rid, r in cs.rows.items():
        r.values.setdefault("vu_khi_id", "")


def build_02_04(R: Ctx):
    books = R.ctx.books
    # ------------------------------------------------------------------ 02
    b2 = books["02_phuong_tien"]
    xe, th = b2.sheets["Xe"], b2.sheets["The_ho_tro"]
    ents2 = [(e, e, name_of(xe.rows[e]), e, {"sheet": "Xe"}) for e in sorted(xe.rows, key=str)]
    ents2 += [(e, e, name_of(th.rows[e]), e, {"sheet": "The_ho_tro"}) for e in sorted(th.rows, key=str)]
    inp2 = _size_input(R, b2, [e for _r, e, *_ in ents2])
    sh2 = C.ref_sheet(b2, "Phuong_tien_tham_chieu", "Phương tiện: tham chiếu ngoài đời", "Mỗi xe và thẻ hỗ trợ một dòng: mẫu "
                      "thật, phim / game (unit_refs.json), kích thước thật (reference_real.json), bảng cân bằng",
                      ["02_phuong_tien/Xe", "02_phuong_tien/The_ho_tro"], U_EXTRA + V_EXTRA)
    unit_rows(R, b2, sh2, ents2, "xe", inp2)
    cs2 = compare_units(R, b2, sh2, "Xe", [x for x in ents2 if x[4]["sheet"] == "Xe"], "Phuong_tien_so_sanh_that",
                        "Phương tiện: so sánh với thật")
    # ------------------------------------------------------------------ 03
    b3 = books["03_boss"]
    bo = b3.sheets["Boss"]
    ents3 = [(e, e, name_of(bo.rows[e]), e, {"sheet": "Boss"}) for e in sorted(bo.rows, key=str)]
    inp3 = _size_input(R, b3, [e for _r, e, *_ in ents3])
    sh3 = C.ref_sheet(b3, "Boss_tham_chieu", "Boss: tham chiếu ngoài đời", "Mỗi boss một dòng: nguồn cảm hứng, phần lấy từ "
                      "mẫu nào, hệ số phóng to, phần giả tưởng", ["03_boss/Boss"], U_EXTRA + B_EXTRA)
    unit_rows(R, b3, sh3, ents3, "boss", inp3)
    cs3 = compare_units(R, b3, sh3, "Boss", ents3, "Boss_so_sanh_that", "Boss: so sánh với thật", boss=True)
    bv = b3.sheets.get("Boss_vu_khi")
    pairs3 = [(r.values.get("boss_id"), r.values.get("vu_khi")) for r in bv.rows.values()] if bv else []
    pairs3 = [(e, w) for e, w in pairs3 if e and w]
    a3, bb3, keep3 = rate_inputs(R, b3, {w for _e, w in pairs3})
    rate_rows(R, b3, cs3, pairs3, a3, bb3, keep3, "pháo boss")
    # ------------------------------------------------------------------ 04
    b4 = books["04_can_cu_thap"]
    ents4 = []
    for sname in ("Thap", "Tuong", "Nha_chinh", "Mo_dun_tien_ich"):
        s = b4.sheets[sname]
        ents4 += [(e, e, name_of(s.rows[e]), e, {"sheet": sname}) for e in sorted(s.rows, key=str)]
    known = {e for _r, e, *_ in ents4} | {e for _r, e, *_ in ents2} | {e for _r, e, *_ in ents3}
    orphans = sorted(k for k in (R.refs if isinstance(R.refs, dict) else {}) if k != "_about" and k not in known)
    for k in orphans:
        base = k.split(".", 1)[0]
        if base in b4.sheets["Thap"].rows:
            ents4.append((k, base, name_of(b4.sheets["Thap"].rows[base]) + f" ({k})", k, {"sheet": "Thap", "orphan": True}))
        else:
            R.ctx.issue(f"{S.UNIT_REFS}: key {k} matches no unit (left unmapped)")
    inp4 = _size_input(R, b4, sorted({e for _r, e, *_ in ents4}))
    tfk = ["04_can_cu_thap/Thap", "04_can_cu_thap/Tuong", "04_can_cu_thap/Nha_chinh", "04_can_cu_thap/Mo_dun_tien_ich"]
    sh4 = C.ref_sheet(b4, "Can_cu_tham_chieu", "Căn cứ và tháp: tham chiếu ngoài đời", "Mỗi tháp / nhánh, tường, nhà chính, "
                      "mô-đun một dòng: mẫu thật, game tham khảo cơ chế, kích thước thật", tfk, U_EXTRA + T_EXTRA)
    unit_rows(R, b4, sh4, ents4, "can_cu", inp4)
    _tower_mechanics(R, sh4, b4)
    cs4 = compare_units(R, b4, sh4, "Thap", [x for x in ents4 if x[4]["sheet"] == "Thap" and not x[4].get("orphan")],
                        "Can_cu_so_sanh_that", "Căn cứ và tháp: so sánh với thật")
    tv = b4.sheets.get("Thap_vu_khi")
    pairs4 = [(r.values.get("thap_id"), r.values.get("weapon")) for r in tv.rows.values()] if tv else []
    for e, row in b4.sheets["Thap"].rows.items():
        w = row.raw.get("weapon") if isinstance(row.raw, dict) else None
        if isinstance(w, str) and w != "none":
            pairs4.append((e, w))
    pairs4 = [(e, w) for e, w in pairs4 if e and w]
    a4, bb4, keep4 = rate_inputs(R, b4, {w for _e, w in pairs4})
    rate_rows(R, b4, cs4, pairs4, a4, bb4, keep4, "tháp")
    if "_about" in (R.refs or {}):
        R.used_refs.add("_about")
    return (sh2, cs2), (sh3, cs3), (sh4, cs4)


def _tower_mechanics(R: Ctx, sh, b4):
    """The AI research workbook's 'Công trình' sheet (targeting modes, 'Tham khảo' games) on the towers whose Vietnamese
    name matches its 'Loại' cell."""
    rows = S.xlsx_rows(S.AI_RESEARCH, "Công trình")
    if not rows:
        return
    nid = R.reg.repo(S.AI_RESEARCH, "Nghiên cứu AI (Machine_Brigade_AI_Research.xlsx)")
    by_name = {}
    for sname in ("Thap", "Mo_dun_tien_ich"):
        for e, r in b4.sheets[sname].rows.items():
            by_name.setdefault((r.values.get("ten_vi") or "").strip().lower(), []).append(e)
    R.tower_research = []
    for row in rows:
        kind = S.text(row.get("Loại"))
        ref = S.text(row.get("Tham khảo"))
        R.tower_research.append((kind, ref, S.text(row.get("Hành vi đặc biệt"))))
        for e in by_name.get(kind.lower(), []):
            r = sh.rows.get(e)
            if r is None or not ref:
                continue
            items, _other = S.games_only(S.split_items(ref))
            if not items:
                continue
            games = [g for g, _m in items]
            mech = [m or "chọn mục tiêu (chế độ bắn của tháp)" for _g, m in items]
            r.values["ten_game"] = C.join([r.values.get("ten_game", "")] + games)
            r.values["co_che_game"] = C.join([r.values.get("co_che_game", "")] + mech)
            r.values["nguon_id"] = C.join(r.values.get("nguon_id", "").split(";") + [nid])
            if r.values.get("loai_tham_chieu") == NEED_SOURCE:
                r.values["loai_tham_chieu"] = "game"
                r.values["do_tin_cay"] = "ban_dau_doan"
                r.values["ly_do"] = ""
