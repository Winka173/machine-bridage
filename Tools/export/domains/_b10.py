"""10_model_tai_san, layer B (pass 5 part 2): Model_cham_diem (MODEL_STANDARD scoring per model: the static scan
Docs/models/scan/static_scores.csv, the visual scan Docs/models/scan/visual_scores.md, the backlogs of
Docs/checks/fix_validate.json item 7 and the fix backlog, as data; live: the triangle budget status on the GLB's current
triangles, the missing parts count, the final grade = the lower of static* and visual, the score, rebuilt-in-prompt-27,
the keep / restore / rebuild decision) and Dia_phuong_hoa_thong_ke (per HUD table: keys, missing English / Vietnamese,
keys defined twice, proper names in one language only, keys no code literal names) with its per-key list
Dia_phuong_hoa_van_de."""
from __future__ import annotations

import csv
import json
import re
import sys

from core.formula import lookup, q, ref as R
from core.repo import ROOT

from . import _lane_c as C
from . import _layer_b as LB

STATIC = "Docs/models/scan/static_scores.csv"
VISUAL = "Docs/models/scan/visual_scores.md"
BACKLOG = "Docs/models/scan/fix_backlog.md"
FIXV = "Docs/checks/fix_validate.json"
SB = "Tools/story/script_build.py"
GRADE = {"Tốt": "Tot", "Cần sửa": "Can_sua", "Kém": "Kem", "": ""}
G3 = ["Tot", "Can_sua", "Kem"]


def _visual(ctx):
    p = ROOT / VISUAL
    out = {}
    if not p.exists():
        ctx.issue(f"10 Model_cham_diem: {VISUAL} missing")
        return out, set()
    rebuilt = set()
    for _line, header, rows in C.md_tables(p.read_text("utf-8")):
        if header[:2] != ["model", "class"]:
            if header[:2] == ["model", "triangles before -> after"]:
                rebuilt |= {C.clean_md(r[0]).split()[0] for _l, r in rows if r}
            continue
        for line, r in rows:
            cell = C.clean_md(r[0])
            mid = cell.split()[0]
            out[mid] = {"line": line, "static_star": r[3].strip(), "visual": r[5].strip(), "visual_reason": r[6].strip(),
                        "old_new": r[7].strip(), "final": r[8].strip(), "rebuilt": "rebuilt" in cell}
    return out, rebuilt


def _backlog(ctx):
    p = ROOT / BACKLOG
    out = {}
    if not p.exists():
        return out
    for _line, header, rows in C.md_tables(p.read_text("utf-8")):
        if not header or header[0] != "model":
            continue
        fix = header.index("suggested fix") if "suggested fix" in header else None
        for line, r in rows:
            mid = C.clean_md(r[0]).split()[0]
            out.setdefault(mid, (line, C.clean_md(r[fix]) if fix is not None and fix < len(r) else ""))
    return out


def build(ctx, book):
    md = book.sheets["Model"]
    p = ROOT / STATIC
    st = list(csv.DictReader(p.open(encoding="utf-8"))) if p.exists() else []
    if not st:
        ctx.issue(f"10 Model_cham_diem: {STATIC} missing")
    vis, rebuilt = _visual(ctx)
    back = _backlog(ctx)
    fv = (json.loads((ROOT / FIXV).read_text("utf-8")).get("models") or {}) if (ROOT / FIXV).exists() else {}
    grades = fv.get("grades") or {}
    lists = {"backlog_lam_lai": set((fv.get("rebuildBacklog") or {}).keys()), "backlog_doi_ten": set((fv.get("renamingBacklog") or {}).keys()),
             "chua_quet": set(fv.get("notScanned") or []), "lod1_ngoai_dai": {s.split()[0] for s in fv.get("lod1OutsideBand") or []}}

    # ------------------------------------------------------------------ Model_cham_diem
    mc = book.sheet("Model_cham_diem", "Model: chấm điểm", "Chấm điểm theo Docs/models/MODEL_STANDARD.md: tam giác trong ngân sách, Part_* "
                    "thiếu, Mount / Muzzle thiếu, sai tỷ lệ, hình bóng (quét hình); điểm; xếp hạng Tot / Can_sua / Kem (thấp hơn của "
                    "static* và hình); làm lại ở prompt 27 (có bản cũ để so); so bản cũ / mới; quyết định giữ / khôi phục / làm lại. "
                    "Số quét là dữ liệu của báo cáo (static_scores.csv, visual_scores.md, fix_validate.json mục 7)", layer="B")
    mc.col("id", fk=["10_model_tai_san/Model"], meaning="model (Model.id, tên GLB)")
    data = [
        ("lop", "class", STATIC, "", "lớp model"), ("lop_ngan_sach", "budgetClass", STATIC, "", "lớp ngân sách"),
        ("tam_giac_bao_cao", "triangles", STATIC, "", "tam giác lúc quét"), ("ngan_sach_duoi", "budgetMin", STATIC, "", "ngân sách tam giác (dưới)"),
        ("ngan_sach_tren", "budgetMax", STATIC, "", "ngân sách tam giác (trên)"), ("ngan_sach_bao_cao", "budgetStatus", STATIC, "", "ok / under / over lúc quét"),
        ("so_phan_bat_buoc", "partsRequired", STATIC, "", "số Part_* bắt buộc của lớp"), ("phan_thieu", "partsMissing", STATIC, "", "Part_* thiếu (ngăn ';')"),
        ("muzzle_can", "muzzlesNeeded", STATIC, "", "Muzzle_* cần"), ("muzzle_co", "muzzlesFound", STATIC, "", "Muzzle_* có"),
        ("muzzle_thieu", "muzzlesMissing", STATIC, "", "Muzzle_* thiếu"), ("mount_thieu", "mountsMissing", STATIC, "", "Mount_* thiếu"),
        ("mount_flare", "flareMounts", STATIC, "", "Mount_Flare có / cần"), ("mount_aps", "apsMount", STATIC, "", "Mount_APS"),
        ("nut_bo_phan_boss_thieu", "bossPartNodesMissing", STATIC, "", "nút bộ phận boss thiếu"),
        ("mau_that", "reference", STATIC, "", "mẫu thật so tỷ lệ"), ("tin_cay_mau", "refConf", STATIC, "", "độ tin cậy mẫu"),
        ("kich_thuoc_glb", "glbSize", STATIC, "", "kích thước GLB (D x R x C, m)"), ("lech_ty_le_rong", "propW", STATIC, "", "lệch tỷ lệ rộng / dài so với mẫu"),
        ("lech_ty_le_cao", "propH", STATIC, "", "lệch tỷ lệ cao / dài so với mẫu"), ("co_ty_le", "propFlag", STATIC, "", "cờ tỷ lệ"),
        ("lod1", "lod1Share", STATIC, "", "tỷ lệ tam giác LOD1"), ("diem_tinh", "staticGrade", STATIC, "", "xếp hạng tĩnh (Tot / Can_sua / Kem)"),
        ("ly_do_kem", "poorBecause", STATIC, "", "lý do Kém"), ("ly_do_tinh", "reasons", STATIC, "", "lý do của điểm tĩnh"),
        ("diem_tinh_sao", None, VISUAL, "", "static*: điểm tĩnh bỏ vượt ngân sách (luật chủ dự án 02/10)"),
        ("diem_hinh", None, VISUAL, "", "điểm quét hình (Tot / Can_sua / Kem; trống: chưa quét)"), ("ly_do_hinh", None, VISUAL, "", "lý do điểm hình"),
        ("cu_moi", None, VISUAL, "", "bản cũ (trước prompt 27, 07444b1) so với bản mới: better / same / worse / redesign; '-' không có bản cũ"),
        ("xep_hang_bao_cao", None, VISUAL, "", "xếp hạng cuối của báo cáo"), ("lam_lai_l8", None, VISUAL, "", "làm lại ở lượt L8 sau lần quét (điểm là bản trước)"),
        ("goi_y_sua", None, BACKLOG, "", "gợi ý sửa của fix_backlog.md"),
        ("backlog_lam_lai", None, FIXV, "", "trong rebuildBacklog (fix_validate mục 7)"), ("backlog_doi_ten", None, FIXV, "", "trong renamingBacklog"),
        ("lod1_ngoai_dai", None, FIXV, "", "trong lod1OutsideBand"), ("chua_quet", None, FIXV, "", "trong notScanned"),
    ]
    for c, _k, src, unit, m in data:
        mc.col(c, unit=unit, meaning=m, source_note=src, enum=G3 if c in ("diem_tinh", "diem_tinh_sao", "diem_hinh", "xep_hang_bao_cao") else None)
    tri = lookup("Model", "tam_giac", "{id}")
    lo = lambda a, b: f"IF(OR({{{a}}}={q('Kem')},{{{b}}}={q('Kem')}),{q('Kem')},IF(OR({{{a}}}={q('Can_sua')},{{{b}}}={q('Can_sua')}),{q('Can_sua')},{q('Tot')}))"  # noqa: E731
    T = {
        "tam_giac": f"=IF(COUNTIFS({R('Model', 'id', '*')},{{id}})>0,{tri},{q('')})",
        "ngan_sach": (f"=IF(OR({{tam_giac}}={q('')},{{ngan_sach_duoi}}={q('')}),{q('')},IF({{tam_giac}}<{{ngan_sach_duoi}},{q('under')},"
                      f"IF({{tam_giac}}>{{ngan_sach_tren}},{q('over')},{q('ok')})))"),
        "so_phan_thieu": f"=IF({{phan_thieu}}={q('')},0,LEN({{phan_thieu}})-LEN(SUBSTITUTE({{phan_thieu}},{q(';')},{q('')}))+1)",
        "xep_hang": f"=IF({{diem_hinh}}={q('')},{{diem_tinh_sao}},{lo('diem_tinh_sao', 'diem_hinh')})",
        "diem": f"=IF({{xep_hang}}={q('Tot')},2,IF({{xep_hang}}={q('Can_sua')},1,0))",
        "lam_lai_p27": f"=AND({{cu_moi}}<>{q('')},{{cu_moi}}<>{q('-')})",
        "quyet_dinh": (f"=IF({{lam_lai_l8}},{q('da_lam_lai')},IF({{cu_moi}}={q('worse')},{q('khoi_phuc')},IF({{xep_hang}}={q('Kem')},"
                       f"{q('lam_lai')},{q('giu')})))"),
        "lech_bao_cao": f"=OR({{xep_hang}}<>{{xep_hang_bao_cao}},{{ngan_sach}}<>{{ngan_sach_bao_cao}})",
    }
    TM = {"tam_giac": ("tam giác hiện tại của GLB (Model.tam_giac)", None), "ngan_sach": ("ok / under / over trên tam giác hiện tại", ["ok", "under", "over"]),
          "so_phan_thieu": ("số Part_* thiếu", None), "xep_hang": ("xếp hạng cuối: thấp hơn của static* và hình (MODEL_STANDARD mục 4)", G3),
          "diem": ("điểm: Tot 2, Can_sua 1, Kem 0", None), "lam_lai_p27": ("đã làm lại ở prompt 27 (có bản cũ khác bản mới để so)", None),
          "quyet_dinh": ("da_lam_lai (L8) / khoi_phuc (bản mới kém hơn) / lam_lai (Kem) / giu", ["da_lam_lai", "khoi_phuc", "lam_lai", "giu"]),
          "lech_bao_cao": ("TRUE: xếp hạng hoặc ngân sách tính lại khác báo cáo (GLB đổi sau lần quét)", None)}
    for c, t in T.items():
        LB.declare(mc, c, t, "Docs/models/MODEL_STANDARD.md mục 4 + Docs/models/scan (luật của báo cáo)", game=False, meaning=TM[c][0], enum=TM[c][1])

    def worst(a, b):
        return "Kem" if "Kem" in (a, b) else "Can_sua" if "Can_sua" in (a, b) else "Tot"
    for row in sorted(st, key=lambda r: r["model"]):
        mid = row["model"]
        if mid not in md.rows:
            ctx.issue(f"10 Model_cham_diem: {mid} of {STATIC} has no GLB row")
            continue
        v = vis.get(mid, {})
        x = mc.row(mid, f"{STATIC} (model = {mid}); {VISUAL}" + (f":{v['line']}" if v else "") + f"; {FIXV} models")
        for c, key, src, _u, _m in data:
            if key is None:
                continue
            val = row.get(key, "")
            if c == "diem_tinh":
                val = GRADE.get(val, val)
            elif c == "phan_thieu":
                val = ";".join(val.split())
            elif c in ("tam_giac_bao_cao", "ngan_sach_duoi", "ngan_sach_tren", "so_phan_bat_buoc", "muzzle_can", "muzzle_co", "lod1"):
                try:
                    val = float(val) if val != "" else ""
                except ValueError:
                    pass
            x.set(c, val)
        x.set("diem_tinh_sao", GRADE.get(v.get("static_star", ""), v.get("static_star", "")))
        x.set("diem_hinh", GRADE.get(v.get("visual", ""), "") if v.get("visual") not in (None, "-") else "")
        x.set("ly_do_hinh", v.get("visual_reason", ""))
        x.set("cu_moi", v.get("old_new", ""))
        x.set("xep_hang_bao_cao", GRADE.get(v.get("final", ""), v.get("final", "")))
        x.set("lam_lai_l8", bool(v.get("rebuilt")) or mid in rebuilt)
        x.set("goi_y_sua", back.get(mid, (0, ""))[1])
        for c, s in lists.items():
            x.set(c, mid in s)
        if mid not in grades:
            ctx.issue(f"10 Model_cham_diem: {mid} not in {FIXV} models.grades")
        # the rules, in Python
        t_now = md.rows[mid].values.get("tam_giac")
        lo_, hi_ = x.values.get("ngan_sach_duoi"), x.values.get("ngan_sach_tren")
        budget = "" if t_now in (None, "") or lo_ == "" else "under" if t_now < lo_ else "over" if t_now > hi_ else "ok"
        pm = x.values.get("phan_thieu") or ""
        s_star, vis_g = x.values["diem_tinh_sao"], x.values["diem_hinh"]
        final = s_star if vis_g == "" else worst(s_star, vis_g)
        cu = x.values["cu_moi"]
        dec = "da_lam_lai" if x.values["lam_lai_l8"] else "khoi_phuc" if cu == "worse" else "lam_lai" if final == "Kem" else "giu"
        vals = {"tam_giac": float(t_now) if isinstance(t_now, (int, float)) else "", "ngan_sach": budget,
                "so_phan_thieu": float(len(pm.split(";"))) if pm else 0.0, "xep_hang": final,
                "diem": 2.0 if final == "Tot" else 1.0 if final == "Can_sua" else 0.0, "lam_lai_p27": cu not in ("", "-"),
                "quyet_dinh": dec, "lech_bao_cao": final.lower() != str(x.values["xep_hang_bao_cao"]).lower() or budget != x.values["ngan_sach_bao_cao"]}
        for c in T:
            LB.put(x, c, T[c], vals[c], game=False)

    # ------------------------------------------------------------------ Dia_phuong_hoa_van_de / _thong_ke
    dp = book.sheets["Dia_phuong_hoa"]
    names = []
    sys.path.insert(0, str(ROOT / "Tools" / "story"))
    try:
        import script_build as S  # noqa: WPS433
        names = list(S.NAMES)
    except Exception as e:  # noqa: BLE001
        ctx.issue(f"10 Dia_phuong_hoa_thong_ke: {SB} unreadable ({type(e).__name__}: {e})")
    finally:
        sys.path.pop(0)
    lits, prefixes = _code_literals()
    vd = book.sheet("Dia_phuong_hoa_van_de", "Địa phương hóa: khóa có vấn đề", "Mỗi khóa chữ có vấn đề một dòng: thiếu tiếng Anh / "
                    "Việt, khai hai lần, tên riêng chỉ có ở một thứ tiếng (danh sách tên của Tools/story/script_build.py: tên riêng "
                    "không dịch), không thấy literal nào trong mã nêu khóa (heuristic: khóa ghép động 'tiền_tố.' + id được tính là dùng)",
                    layer="B")
    vd.col("id", fk=["10_model_tai_san/Dia_phuong_hoa"], meaning="khóa (Dia_phuong_hoa.id)")
    vd.col("bang", meaning="file C# chứa khóa")
    for c, m in (("ten_rieng_mot_thu_tieng", "tên riêng có ở một thứ tiếng mà không có ở thứ tiếng kia (ngăn ';')"),
                 ("khong_thay_trong_ma", "không literal nào trong Assets/MachineBrigade/Scripts nêu khóa hay tiền tố của nó")):
        vd.col(c, meaning=m, source_note="python: Tools/export/domains/_b10.py (quét chữ)" if c == "khong_thay_trong_ma" else f"python: {SB} NAMES")
    VT = {"thieu_en": f"=LEN({R('Dia_phuong_hoa', 'en')})=0", "thieu_vi": f"=LEN({R('Dia_phuong_hoa', 'vi')})=0",
          "khai_hai_lan": f"=ISNUMBER(FIND({q('@')},{{id}}))"}
    for c, m in (("thieu_en", "không có tiếng Anh"), ("thieu_vi", "không có tiếng Việt"), ("khai_hai_lan", "khóa khai lần hai ở một bảng khác (id có '@')")):
        LB.declare(vd, c, VT[c], "Dia_phuong_hoa (en / vi / id)", game=False, meaning=m)
    for r in dp.sorted_rows():
        en, vi = r.values.get("en") or "", r.values.get("vi") or ""
        key = str(r.id).split("@")[0]
        one = [n for n in names if (re.search(rf"\b{re.escape(n)}", en) is None) != (re.search(rf"\b{re.escape(n)}", vi) is None)]
        unused = key not in lits and not any(key.startswith(p) for p in prefixes)
        flags = {"thieu_en": en == "", "thieu_vi": vi == "", "khai_hai_lan": "@" in str(r.id)}
        if not (any(flags.values()) or one or unused):
            continue
        x = vd.row(r.id, f"10/Dia_phuong_hoa ({r.id})")
        x.set("bang", r.values.get("bang"))
        x.set("ten_rieng_mot_thu_tieng", ";".join(one))
        x.set("khong_thay_trong_ma", unused)
        for c in VT:
            LB.put(x, c, VT[c], flags[c], game=False)
    tk = book.sheet("Dia_phuong_hoa_thong_ke", "Địa phương hóa: thống kê", "Mỗi bảng chữ C#: số khóa, khóa thiếu tiếng Anh / Việt, khai hai "
                    "lần, có tên riêng ở một thứ tiếng, không thấy trong mã (COUNTIFS trên Dia_phuong_hoa và Dia_phuong_hoa_van_de)", layer="B")
    tk.col("id", meaning="file C# (Dia_phuong_hoa.bang)")
    VD = lambda c: R("Dia_phuong_hoa_van_de", c, "*")  # noqa: E731
    KT = {"so_khoa": f"=COUNTIFS({R('Dia_phuong_hoa', 'bang', '*')},{{id}})",
          "thieu_en": f"=COUNTIFS({VD('bang')},{{id}},{VD('thieu_en')},TRUE)",
          "thieu_vi": f"=COUNTIFS({VD('bang')},{{id}},{VD('thieu_vi')},TRUE)",
          "khai_hai_lan": f"=COUNTIFS({VD('bang')},{{id}},{VD('khai_hai_lan')},TRUE)",
          "ten_rieng_bi_dich": f"=COUNTIFS({VD('bang')},{{id}},{VD('ten_rieng_mot_thu_tieng')},{q('?*')})",
          "khong_thay_trong_ma": f"=COUNTIFS({VD('bang')},{{id}},{VD('khong_thay_trong_ma')},TRUE)"}
    for c, m in (("so_khoa", "số khóa của bảng"), ("thieu_en", "khóa thiếu tiếng Anh"), ("thieu_vi", "khóa thiếu tiếng Việt"),
                 ("khai_hai_lan", "khóa đã khai ở bảng khác"), ("ten_rieng_bi_dich", "khóa có tên riêng chỉ ở một thứ tiếng (bị dịch hoặc thiếu)"),
                 ("khong_thay_trong_ma", "khóa không thấy literal trong mã (thừa?)")):
        LB.declare(tk, c, KT[c], "COUNTIFS", game=False, meaning=m)
    for b in sorted({r.values.get("bang") for r in dp.rows.values()}):
        x = tk.row(b, f"10/Dia_phuong_hoa (bang = {b})")
        rows_b = [r for r in vd.rows.values() if r.values.get("bang") == b]
        vals = {"so_khoa": float(sum(1 for r in dp.rows.values() if r.values.get("bang") == b)),
                "thieu_en": float(sum(1 for r in rows_b if LB.F_value(r.values["thieu_en"]))),
                "thieu_vi": float(sum(1 for r in rows_b if LB.F_value(r.values["thieu_vi"]))),
                "khai_hai_lan": float(sum(1 for r in rows_b if LB.F_value(r.values["khai_hai_lan"]))),
                "ten_rieng_bi_dich": float(sum(1 for r in rows_b if r.values.get("ten_rieng_mot_thu_tieng"))),
                "khong_thay_trong_ma": float(sum(1 for r in rows_b if r.values.get("khong_thay_trong_ma")))}
        for c in KT:
            LB.put(x, c, KT[c], vals[c], game=False)


def _code_literals():
    """Every string literal of the game's C# outside the text tables' own entries (["key"] = ...): the exact literals, and
    the prefixes of keys built at run time (a literal ending in '.' or '_', the head of an interpolated $"a.{x}")."""
    lits, prefixes = set(), set()
    rx = re.compile(r'"((?:[^"\\\n]|\\.)*)"')
    table_entry = re.compile(r'^\s*\["[^"]+"\]\s*=')
    for p in sorted((ROOT / "Assets" / "MachineBrigade" / "Scripts").rglob("*.cs")):
        for ln in p.read_text("utf-8-sig").splitlines():
            if table_entry.match(ln):
                continue
            for m in rx.finditer(ln):
                s = m.group(1)
                if not s or " " in s:
                    continue
                lits.add(s)
                head = s.split("{", 1)[0] if "{" in s else s
                if head != s and len(head) >= 3:
                    prefixes.add(head)  # an interpolated key: $"arc.{speaker}.{mission}"
                elif s.endswith((".", "_")) and len(s) > 2:
                    prefixes.add(s)  # a key built as "prefix." + id
    return lits, prefixes
