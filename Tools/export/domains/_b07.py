"""07_chien_dich_cot_truyen, layer B (pass 5 part 2): Thoai_thong_ke (per mission: lines against the budget of its kind,
the longest known silence, lines over the hard length, lines said word for word in another mission), its child
Thoai_thong_ke_nhom (lines by speaker / trigger / priority), Thoai_moc_thoi_gian (the timed marks the silence is read
from) and Nhiem_vu_thong_ke (lines with Vietnamese / English text, lines by priority P0-P4).

Counts are live COUNTIFS over Thoai; the budget (by mission kind) and the word-for-word rule are Tools/story/script_build.py's
(BUDGET, kind_of, the L8 check), copied as data with that source."""
from __future__ import annotations

import sys

from core.formula import F, q, ref as R
from core.repo import ROOT

from . import _layer_b as LB

SB = "Tools/story/script_build.py"
VI_HARD, EN_HARD = 110, 90


def _script_build(ctx):
    sys.path.insert(0, str(ROOT / "Tools" / "story"))
    try:
        import script_build as S  # noqa: WPS433
        return S
    except Exception as e:  # noqa: BLE001
        ctx.issue(f"07 Thoai_thong_ke: {SB} unreadable ({type(e).__name__}: {e})")
        return None
    finally:
        sys.path.pop(0)


def build(ctx, book, camp):
    th = book.sheets["Thoai"]
    nv = book.sheets["Nhiem_vu"]
    S = _script_build(ctx)
    budget = getattr(S, "BUDGET", {}) if S else {}
    vi_hard = getattr(S, "VI_HARD", VI_HARD) if S else VI_HARD
    en_hard = getattr(S, "EN_HARD", EN_HARD) if S else EN_HARD
    by_id = {m["id"]: m for m in camp.get("missions") or [] if isinstance(m, dict)}
    lines = th.sorted_rows()
    per = {}
    for r in sorted(th.rows.values(), key=lambda r: (str(r.values.get("tep")), r.values.get("thu_tu", 0))):
        per.setdefault(r.values.get("nhiem_vu_id"), []).append(r)
    # the word-for-word rule (script_build L8): a text said in another mission
    where = {}
    for r in lines:
        for lang in ("van_ban_vi", "van_ban_en"):
            t = (r.values.get(lang) or "").lower()
            if t:
                where.setdefault((lang, t), set()).add(r.values.get("nhiem_vu_id"))

    def dup(r):
        return any(len(where.get((lang, (r.values.get(lang) or "").lower()), ())) > 1
                   for lang in ("van_ban_vi", "van_ban_en") if r.values.get(lang))

    TH = lambda col: R("Thoai", col, "*")  # noqa: E731

    # ------------------------------------------------------------------ Thoai_moc_thoi_gian
    mk = book.sheet("Thoai_moc_thoi_gian", "Thoại: mốc thời gian", "Câu có thời điểm biết trước của mỗi nhiệm vụ (mission_start = 0 s, "
                    "trigger time = at), theo thời gian; khoảng = mốc này - mốc trước (mốc đầu: từ 0 s)", layer="B")
    mk.col("id", fk=["07_chien_dich_cot_truyen/Thoai"], meaning="câu thoại (Thoai.id)")
    mk.col("nhiem_vu_id", fk=["07_chien_dich_cot_truyen/Nhiem_vu"], meaning="nhiệm vụ")
    mk.col("thu_tu_moc", meaning="thứ tự mốc trong nhiệm vụ (0 = sớm nhất)")
    mk.col("moc_truoc", fk=["07_chien_dich_cot_truyen/Thoai_moc_thoi_gian"], meaning="mốc trước (trống: mốc đầu)")
    LB.declare(mk, "moc_s", f"=IF({R('Thoai', 'trigger')}={q('mission_start')},0,{R('Thoai', 'dieu_kien_at_s')})",
               "Thoai.trigger / Thoai.dieu_kien_at_s", unit="s", game=False, meaning="thời điểm câu (s từ đầu nhiệm vụ)")
    mk.col("khoang_s")
    marks = {}
    for mid, rs in per.items():
        timed = [r for r in rs if r.values.get("trigger") == "mission_start" or
                 (r.values.get("trigger") == "time" and isinstance(r.values.get("dieu_kien_at_s"), (int, float)))]
        timed.sort(key=lambda r: (0.0 if r.values.get("trigger") == "mission_start" else float(r.values["dieu_kien_at_s"]),
                                  r.values.get("thu_tu", 0)))
        prev = None
        for k, r in enumerate(timed):
            at = 0.0 if r.values.get("trigger") == "mission_start" else float(r.values["dieu_kien_at_s"])
            x = mk.row(r.id, f"07/Thoai ({r.id})")
            x.set("nhiem_vu_id", mid)
            x.set("thu_tu_moc", k)
            x.set("moc_truoc", prev[0] if prev else "")
            LB.put(x, "moc_s", mk.cols["moc_s"].formula, at, game=False)
            gap = at - (prev[1] if prev else 0.0)
            t = f"={{moc_s}}-{R('', 'moc_s', prev[0])}" if prev else "={moc_s}"
            x.set("khoang_s", F(t, expect=gap, ref="python: mốc - mốc trước"))
            marks.setdefault(mid, []).append(r.id)
            prev = (r.id, at)
    LB.declare(mk, "khoang_s", "={moc_s}-{moc_s@<mốc trước>}", "mốc - mốc trước", unit="s", game=False,
               meaning="khoảng im lặng trước câu này (giữa hai mốc biết trước)")

    # ------------------------------------------------------------------ Thoai_thong_ke
    tk = book.sheet("Thoai_thong_ke", "Thoại: thống kê theo nhiệm vụ", "Mỗi nhiệm vụ: số câu so với ngân sách theo kiểu nhiệm vụ "
                    "(Tools/story/script_build.py L1: ngắn / phụ 4-8, thường 6-10, boss / chiến dịch lớn 10-16), khoảng im lặng dài "
                    "nhất giữa các mốc biết trước, câu quá độ dài cứng (Việt 110, Anh 90 ký tự), câu trùng nguyên văn ở nhiệm vụ khác "
                    "(L8); theo người nói / trigger / ưu tiên: Thoai_thong_ke_nhom", layer="B")
    tk.col("id", fk=["07_chien_dich_cot_truyen/Nhiem_vu"], meaning="nhiệm vụ")
    for c, m in (("kieu_nhiem_vu", "kiểu theo script_build.kind_of: short (phụ) / normal / boss (boss, chiến dịch lớn)"),
                 ("ngan_sach_duoi", "ngân sách câu, dưới (script_build.BUDGET)"), ("ngan_sach_tren", "ngân sách câu, trên"),
                 ("so_cau_trung_nguyen_van", "câu có văn bản Việt hoặc Anh trùng nguyên văn một câu của nhiệm vụ khác (script_build L8)")):
        tk.col(c, meaning=m, source_note=f"python: {SB}")
    TT = {
        "so_cau": f"=COUNTIFS({TH('nhiem_vu_id')},{{id}})",
        "vuot_ngan_sach": (f"=IF({{ngan_sach_duoi}}={q('')},{q('')},IF({{so_cau}}<{{ngan_sach_duoi}},{q('THIEU')},"
                           f"IF({{so_cau}}>{{ngan_sach_tren}},{q('THUA')},{q('ok')})))"),
        "so_cau_vi_qua_dai": f"=COUNTIFS({TH('nhiem_vu_id')},{{id}},{TH('so_ky_tu_vi')},{q('>' + str(vi_hard))})",
        "so_cau_en_qua_dai": f"=COUNTIFS({TH('nhiem_vu_id')},{{id}},{TH('so_ky_tu_en')},{q('>' + str(en_hard))})",
    }
    TM = {"so_cau": ("", "số câu thoại của nhiệm vụ"), "vuot_ngan_sach": ("", "THIEU / THUA / ok so với ngân sách (trống: không có kiểu)"),
          "so_cau_vi_qua_dai": ("", f"câu tiếng Việt quá {vi_hard} ký tự"), "so_cau_en_qua_dai": ("", f"câu tiếng Anh quá {en_hard} ký tự")}
    for c, t in TT.items():
        LB.declare(tk, c, t, f"COUNTIFS trên Thoai ({SB} L1 / L3)", unit=TM[c][0], meaning=TM[c][1], game=False,
                   enum=["THIEU", "THUA", "ok"] if c == "vuot_ngan_sach" else None)
    LB.declare(tk, "khoang_im_lang_dai_nhat_s", "=MAX({Thoai_moc_thoi_gian!khoang_s@<mỗi mốc của nhiệm vụ>})",
               "Thoai_moc_thoi_gian.khoang_s", unit="s", game=False,
               meaning="khoảng im lặng dài nhất giữa hai mốc biết trước (trống: nhiệm vụ không có câu có thời điểm)")
    for nr in nv.sorted_rows():
        mid = nr.id
        rs = per.get(mid, [])
        x = tk.row(mid, f"07/Thoai (nhiem_vu_id = {mid}); {SB}")
        m = by_id.get(mid)
        kind = S.kind_of(m) if S and m else ""
        lo, hi = budget.get(kind, ("", ""))
        x.set("kieu_nhiem_vu", kind)
        x.set("ngan_sach_duoi", lo)
        x.set("ngan_sach_tren", hi)
        x.set("so_cau_trung_nguyen_van", sum(1 for r in rs if dup(r)))
        n = len(rs)
        LB.put(x, "so_cau", TT["so_cau"], float(n), game=False)
        LB.put(x, "vuot_ngan_sach", TT["vuot_ngan_sach"], "" if lo == "" else "THIEU" if n < lo else "THUA" if n > hi else "ok", game=False)
        LB.put(x, "so_cau_vi_qua_dai", TT["so_cau_vi_qua_dai"], float(sum(1 for r in rs if (r.values.get("so_ky_tu_vi") or 0) > vi_hard)), game=False)
        LB.put(x, "so_cau_en_qua_dai", TT["so_cau_en_qua_dai"], float(sum(1 for r in rs if (r.values.get("so_ky_tu_en") or 0) > en_hard)), game=False)
        ids = marks.get(mid, [])
        if ids:
            gaps = [LB.F_value(mk.rows[i].values["khoang_s"]) for i in ids]
            LB.put(x, "khoang_im_lang_dai_nhat_s", "=MAX(" + ",".join(R("Thoai_moc_thoi_gian", "khoang_s", i) for i in ids) + ")",
                   max(gaps), game=False)
        else:
            LB.put(x, "khoang_im_lang_dai_nhat_s", f"={q('')}", "", game=False)

    # ------------------------------------------------------------------ Thoai_thong_ke_nhom
    tn = book.sheet("Thoai_thong_ke_nhom", "Thoại: số câu theo nhóm", "Mỗi nhiệm vụ x (người nói / trigger / ưu tiên) x giá trị có mặt: "
                    "số câu (COUNTIFS trên Thoai)", layer="B", parent=tk)
    tn.col("chieu", meaning="nguoi_noi / trigger / uu_tien", enum=["nguoi_noi", "trigger", "uu_tien"])
    tn.col("gia_tri", meaning="người nói / trigger / ưu tiên (1-4)")
    LB.declare(tn, "so_cau", f"=COUNTIFS({TH('nhiem_vu_id')},{{thoai_thong_ke_id}},{TH('<chieu>')},{{gia_tri}})",
               "COUNTIFS trên Thoai", game=False, meaning="số câu của nhiệm vụ có giá trị này")
    for mid in sorted(per, key=str):
        if mid not in tk.rows:
            continue
        for dim in ("nguoi_noi", "trigger", "uu_tien"):
            counts = {}
            for r in per[mid]:
                v = r.values.get(dim)
                if v not in (None, ""):
                    counts[v] = counts.get(v, 0) + 1
            for j, v in enumerate(sorted(counts, key=str)):
                x = tn.row(f"{mid}/{dim}/{v}", f"07/Thoai (nhiem_vu_id = {mid}, {dim} = {v})")
                x.set(tn.parent_col, mid)
                x.set("thu_tu", j)
                x.set("chieu", dim)
                x.set("gia_tri", v)
                LB.put(x, "so_cau", f"=COUNTIFS({TH('nhiem_vu_id')},{{thoai_thong_ke_id}},{TH(dim)},{{gia_tri}})", float(counts[v]), game=False)

    # ------------------------------------------------------------------ Nhiem_vu_thong_ke
    ns = book.sheet("Nhiem_vu_thong_ke", "Nhiệm vụ: thống kê thoại", "Mỗi nhiệm vụ: số câu có văn bản tiếng Việt / tiếng Anh, số câu "
                    "theo ưu tiên P0-P4 (COUNTIFS trên Thoai)", layer="B")
    ns.col("id", fk=["07_chien_dich_cot_truyen/Nhiem_vu"], meaning="nhiệm vụ")
    NT = {"so_cau_vi": f"=COUNTIFS({TH('nhiem_vu_id')},{{id}},{TH('so_ky_tu_vi')},{q('>0')})",
          "so_cau_en": f"=COUNTIFS({TH('nhiem_vu_id')},{{id}},{TH('so_ky_tu_en')},{q('>0')})"}
    for p in range(5):
        NT[f"so_cau_p{p}"] = f"=COUNTIFS({TH('nhiem_vu_id')},{{id}},{TH('uu_tien')},{p})"
    for c, t in NT.items():
        LB.declare(ns, c, t, "COUNTIFS trên Thoai", game=False,
                   meaning={"so_cau_vi": "câu có văn bản tiếng Việt", "so_cau_en": "câu có văn bản tiếng Anh"}.get(c, f"câu ưu tiên P{c[-1]}"))
    for nr in nv.sorted_rows():
        rs = per.get(nr.id, [])
        x = ns.row(nr.id, f"07/Thoai (nhiem_vu_id = {nr.id})")
        LB.put(x, "so_cau_vi", NT["so_cau_vi"], float(sum(1 for r in rs if (r.values.get("so_ky_tu_vi") or 0) > 0)), game=False)
        LB.put(x, "so_cau_en", NT["so_cau_en"], float(sum(1 for r in rs if (r.values.get("so_ky_tu_en") or 0) > 0)), game=False)
        for p in range(5):
            LB.put(x, f"so_cau_p{p}", NT[f"so_cau_p{p}"], float(sum(1 for r in rs if r.values.get("uu_tien") == p)), game=False)
