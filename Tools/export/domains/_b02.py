"""02_phuong_tien, layer B (pass 5): Xe_suy_ra (the detail screen's DPS: UnitStats.Dps = FirePower.Sustained of the main
weapon on its carrier; health and DPS per CP; the ratio to the fleet's health curve), Hoi_quy_du_lieu + Hoi_quy (health
and DPS exponents on CP, medians by price band), May_bay_so_phat (hits of the reference SAMs / air-to-air missile to
down each aircraft), Doi_mo_man_suy_ra (the opening squad's baseCP, OpeningSquads.Pick with an empty deck).
Weapon numbers come from file 01 through input_vu_khi / input_vu_khi_suy_ra / input_bang_xuyen_giap (spec 2.2)."""
from __future__ import annotations

import math
import statistics

from core.formula import lookup, q, ref as R
from core.model import NEED_CODE_CHECK

from . import _balance as B
from . import _game as G
from . import _layer_b as LB

W01 = "01_vu_khi_dan"
FP = "Sim/Combat/FirePower.cs"
DT = "Sim/Content/DamageTable.cs"
# spec 02 B: May_bay_so_phat (Stinger / Buk / a fighter's missile)
AA_REF = [("stinger", "stinger_post", "FIM-92 Stinger"), ("buk", "buk_launcher", "9M317 Buk"),
          ("ten_lua_tiem_kich", "air_to_air", "AIM-120 AMRAAM (tên lửa tiêm kích)")]
NOT_IN_FIT = ("Support", "Scout")  # spec: the standard filter drops CP 0, Support and Scout
LIGHT, HEAVY = 1, 3                # the regression's light / heavy target armour (front)
HQ_MEAN = {"dps_nhe": "DPS vũ khí chính lên mục tiêu nhẹ; giả định (lead chấp nhận 03/10): nhẹ = giáp 1", "dps_nang": "DPS vũ khí chính lên mục tiêu nặng; giả định (lead chấp nhận 03/10): nặng = giáp 3",
           "dps_may_bay": "DPS vũ khí chính lên máy bay; giả định (lead chấp nhận 03/10): máy bay giáp 0"}
BANDS = [("le8", "<=8", lambda cp: cp <= 8), ("9_15", "9-15", lambda cp: 9 <= cp <= 15), ("ge16", ">=16", lambda cp: cp >= 16)]

V_COLS = [("sat_thuong_moi_phat", "sat_thuong_moi_phat", "hp", "sát thương mỗi phát"),
          ("so_phat_moi_loat", "so_phat_moi_loat", "", "số phát mỗi loạt"),
          ("so_loat_mang", "so_loat_mang", "", "số loạt mang (0: không giới hạn)"),
          ("dat_boi_boss", "dat_boi_boss", "", "do hệ boss đặt bắn (laid)"),
          ("xuyen", "xuyen", "", "mức xuyên"), ("loai_sat_thuong", "loai_sat_thuong", "", "loại sát thương"),
          ("danh_noc", "danh_noc", "", "đánh nóc (topAttack): bảng đánh nóc")]
S_COLS = [("chu_ky_day_du_s", "chu_ky_day_du_s", "s", "chu kỳ đầy đủ"),
          ("sat_thuong_moi_loat", "sat_thuong_moi_loat", "hp", "sát thương một loạt"),
          ("nap_lai_kho_hieu_dung_s", "nap_lai_kho_hieu_dung_s", "s", "nạp lại kho dùng thật"),
          ("danh_tu_tren", "danh_tu_tren", "", "đánh từ trên"), ("ban_mat_dat", "ban_mat_dat", "", "nhắm mặt đất"),
          ("ban_may_bay", "ban_may_bay", "", "nhắm máy bay"), ("he_so_mat_dat", "he_so_mat_dat", "", "hệ số lên mặt đất"),
          ("he_so_may_bay", "he_so_may_bay", "", "hệ số lên máy bay"), ("xuyen_qua", "xuyen_qua", "", "đạn động năng bắn thẳng không đánh nóc: bảng xuyên quá")]


def inputs(ctx, book, wids):
    vk = ctx.books[W01].sheets["Vu_khi"]
    rows_v = {w: {c: LB.source_value(ctx, W01, "Vu_khi", w, src) for c, src, _u, _m in V_COLS} for w in wids if w in vk.rows}
    rows_s = {w: {c: LB.source_value(ctx, W01, "Vu_khi_suy_ra", w, src) for c, src, _u, _m in S_COLS} for w in wids
              if w in vk.rows}
    LB.input_sheet(ctx, book, "input_vu_khi", "Input: vũ khí (từ 01)", W01, "Vu_khi", V_COLS, rows_v)
    LB.input_sheet(ctx, book, "input_vu_khi_suy_ra", "Input: vũ khí suy ra (từ 01)", W01, "Vu_khi_suy_ra", S_COLS, rows_s)
    bx = ctx.books[W01].sheets["Bang_xuyen_giap"]
    LB.input_sheet(ctx, book, "input_bang_xuyen_giap", "Input: bảng xuyên giáp (từ 01)", W01, "Bang_xuyen_giap",
                   [("he_so", "he_so", "", "hệ số xuyên của bước")],
                   {rid: {"he_so": r.values.get("he_so")} for rid, r in bx.rows.items()})
    bn = ctx.books[W01].sheets["Bang_danh_noc"]
    LB.input_sheet(ctx, book, "input_bang_danh_noc", "Input: bảng đánh nóc (từ 01)", W01, "Bang_danh_noc",
                   [("he_so", "he_so", "", "hệ số đánh nóc của bước")],
                   {rid: {"he_so": r.values.get("he_so")} for rid, r in bn.rows.items()})
    bo = ctx.books[W01].sheets["Bang_xuyen_qua"]
    LB.input_sheet(ctx, book, "input_bang_xuyen_qua", "Input: bảng xuyên quá (từ 01)", W01, "Bang_xuyen_qua",
                   [("he_so", "he_so", "", "hệ số xuyên quá của bước")], {rid: {"he_so": r.values.get("he_so")} for rid, r in bo.rows.items()})


def pen_idx(pen_expr: str, top_expr: str | None, armour, ta_expr: str | None = None, xq_expr: str | None = None) -> str:
    """DamageTable.ArmourMultiplier for whole levels (top_expr None: an aircraft, the direct table with no overmatch;
    ta_expr: a topAttack weapon reads the top attack table), x the overpenetration row when xq_expr (04/10)."""
    return LB.armour_index(R('input_bang_xuyen_giap', 'he_so', '*'), R('input_bang_danh_noc', 'he_so', '*'), pen_expr, armour,
                           roof_expr=top_expr, top_expr=ta_expr, air=top_expr is None,
                           over=R('input_bang_xuyen_qua', 'he_so', '*') if xq_expr else None, over_expr=xq_expr)


def build(ctx, book, d, res):
    table = d.get("damageTable") or {}
    W = B.resolved_weapons(ctx)
    xe = book.sheets["Xe"]
    xrows = xe.sorted_rows()
    mains = {r.values.get("vu_khi_chinh") for r in xrows} - {"", None}
    inputs(ctx, book, sorted((mains | {w for _k, w, _n in AA_REF}) & set(W)))

    # ------------------------------------------------------------------ Xe_suy_ra
    sh = book.sheet("Xe_suy_ra", "Xe: suy ra", "Lớp B: DPS vũ khí chính trên xe (màn chi tiết), máu / CP, DPS / CP, tỷ lệ "
                    "so với đường cong máu của đội hình (Hoi_quy)", layer="B")
    sh.col("id", fk=["02_phuong_tien/Xe"], meaning="xe (Xe.id)")
    sh.col("nap_dan_may_bay", meaning="viên mang một lần nạp của vũ khí chính (máy bay: loads[vũ khí] hoặc load; còn lại 0)",
           source_note="port Sim/Content/Definitions.cs VehicleDef.LoadOf")
    sh.col("nap_lai_may_bay_s", unit="s", meaning="thời gian nạp lại cả tải ở vòng chờ (rearmTime, mặc định theo loại)",
           source_note="port Sim/Content/Catalog.cs DefaultRearm")
    sh.col("he_so_vu_khi", meaning="weaponDamage (kẹp 0,1-10): hệ số sát thương mặt đất của vũ khí (không áp cho vũ khí laid)",
           source_note="port Sim/Content/Catalog.Extra.cs ParseExtras")
    k = R("Xe", "vu_khi_chinh")

    def Wv(c):
        return lookup("input_vu_khi", c, k)

    def Ws(c):
        return lookup("input_vu_khi_suy_ra", c, k)

    paper = (f"IF({Wv('sat_thuong_moi_phat')}<=0,0,IF({{nap_dan_may_bay}}>0,{Wv('sat_thuong_moi_phat')}*{{nap_dan_may_bay}}/"
             f"(MAX(0.05,{Ws('chu_ky_day_du_s')})*MAX(1,CEILING({{nap_dan_may_bay}}/MAX(1,{Wv('so_phat_moi_loat')}),1))"
             f"+MAX(0,{{nap_lai_may_bay_s}})),IF({Wv('so_loat_mang')}>0,{Ws('sat_thuong_moi_loat')}*{Wv('so_loat_mang')}/"
             f"(MAX(0.05,{Ws('chu_ky_day_du_s')})*{Wv('so_loat_mang')}+{Ws('nap_lai_kho_hieu_dung_s')}),"
             f"{Ws('sat_thuong_moi_loat')}/MAX(0.05,{Ws('chu_ky_day_du_s')}))))")
    T = {
        "dps_vu_khi_chinh": f"={paper}*IF({Wv('dat_boi_boss')},1,{{he_so_vu_khi}})*{R('Xe', 'he_so_sat_thuong_ra')}",
        "dps_vu_khi_chinh_may_bay": f"={paper}*{R('Xe', 'he_so_sat_thuong_ra')}",
        "mau_tren_cp": f"=IF(AND({R('Xe', 'base_cp')}>0,ISNUMBER({R('Xe', 'mau_trong_tran_hp')})),"
                       f"{R('Xe', 'mau_trong_tran_hp')}/{R('Xe', 'base_cp')},{q('')})",
        "dps_tren_cp": f"=IF({R('Xe', 'base_cp')}>0,{{dps_vu_khi_chinh}}/{R('Xe', 'base_cp')},{q('')})",
        "ty_le_so_voi_duong_cong": (f"=IF(AND({R('Xe', 'base_cp')}>0,ISNUMBER({R('Xe', 'mau_trong_tran_hp')})),"
                                    f"{R('Xe', 'mau_trong_tran_hp')}/({R('Hoi_quy', 'gia_tri', 'mau_he_so')}*"
                                    f"{R('Xe', 'base_cp')}^{R('Hoi_quy', 'gia_tri', 'mau_so_mu')}),{q('')})"),
    }
    LB.declare(sh, "dps_vu_khi_chinh", T["dps_vu_khi_chinh"], f"Game/Match/UnitStats.cs Dps -> {FP} Sustained(w, carrier)",
               unit="hp/s", meaning="DPS duy trì của vũ khí chính trên xe (màn chi tiết; trước bảng sát thương)")
    LB.declare(sh, "dps_vu_khi_chinh_may_bay", T["dps_vu_khi_chinh_may_bay"], f"{FP} SustainedAir(w, carrier)", unit="hp/s",
               meaning="DPS duy trì của vũ khí chính lên máy bay (không weaponDamage)")
    LB.declare(sh, "mau_tren_cp", T["mau_tren_cp"], "mau_trong_tran_hp / base_cp", unit="hp/CP", game=False,
               meaning="máu trong trận mỗi CP (trống: CP 0 hoặc máu chưa rõ)")
    LB.declare(sh, "dps_tren_cp", T["dps_tren_cp"], "dps_vu_khi_chinh / base_cp", unit="hp/s/CP", game=False,
               meaning="DPS vũ khí chính mỗi CP")
    LB.declare(sh, "ty_le_so_voi_duong_cong", T["ty_le_so_voi_duong_cong"], "hp / (a x cp^b) với a, b ở Hoi_quy", game=False,
               meaning="máu / máu của đường cong hồi quy (Hoi_quy.mau_he_so x CP^mau_so_mu) cùng CP")
    for c in ("nhom_gia", "he_so_gia", "thuong_suc_manh", "tha_du_theo_nhom_s"):
        sh.col(c, unit="s" if c.endswith("_s") else "", meaning=f"{c.replace('_', ' ')}: không tìm thấy hàm trong mã C# "
               "(không có nhóm giá trong Sim / Game); chờ chủ dự án định nghĩa")
    per = {}
    for r in xrows:
        vid = r.id
        v = res.get(vid, {})
        wid = r.values.get("vu_khi_chinh")
        x = sh.row(vid, f"{B.BALANCE}: vehicles[id={vid}] (lớp B trên 02_phuong_tien/Xe)")
        for c in ("nhom_gia", "he_so_gia", "thuong_suc_manh", "tha_du_theo_nhom_s"):
            x.set(c, NEED_CODE_CHECK)
        w = W.get(wid)
        if w is None:
            continue
        car = G.carrier(v, w)
        x.set("nap_dan_may_bay", car["load"])
        x.set("nap_lai_may_bay_s", car["rearm"])
        x.set("he_so_vu_khi", car["weapon_damage"])
        dps = G.sustained(w, car)
        dps_air = G.sustained(w, car, ground=False)
        LB.put(x, "dps_vu_khi_chinh", T["dps_vu_khi_chinh"], dps)
        LB.put(x, "dps_vu_khi_chinh_may_bay", T["dps_vu_khi_chinh_may_bay"], dps_air)
        cp = r.values.get("base_cp") or 0
        hp = r.values.get("mau_trong_tran_hp")
        hp_ok = isinstance(hp, (int, float)) and not isinstance(hp, bool)
        LB.put(x, "mau_tren_cp", T["mau_tren_cp"], hp / cp if cp > 0 and hp_ok else "", game=False)
        LB.put(x, "dps_tren_cp", T["dps_tren_cp"], dps / cp if cp > 0 else "", game=False)
        per[vid] = (v, w, cp, hp if hp_ok else None, dps, dps_air)

    # ------------------------------------------------------------------ Hoi_quy_du_lieu / Hoi_quy
    hd = book.sheet("Hoi_quy_du_lieu", "Hồi quy: dữ liệu", "Xe vào hồi quy (bộ lọc chuẩn: bỏ CP 0, Support, Scout; chỉ xe thẻ, "
                    "không tinh nhuệ, có máu): ln CP, ln máu, ln DPS = max(nhẹ giáp 1, nặng giáp 3, máy bay)", layer="B")
    hd.col("id", fk=["02_phuong_tien/Xe"])
    T2 = {
        "cp": f"={R('Xe', 'base_cp')}", "mau_hp": f"={R('Xe', 'mau_trong_tran_hp')}",
        "dps_nhe": None, "dps_nang": None, "dps_may_bay": None,
        "dps_max": "=MAX({dps_nhe},{dps_nang},{dps_may_bay})",
        "ln_cp": "=LN({cp})", "ln_mau": "=LN({mau_hp})",
        "ln_dps": f"=IF({{dps_max}}>0,LN({{dps_max}}),{q('')})",
        "dai_cp": f"=IF({{cp}}<=8,{q('<=8')},IF({{cp}}<=15,{q('9-15')},{q('>=16')}))",
    }
    for tag, label, _f in BANDS:
        T2[f"mau_tren_cp_{tag}"] = f"=IF({{dai_cp}}={q(label)},{{mau_hp}}/{{cp}},{q('')})"
        T2[f"dps_tren_cp_{tag}"] = f"=IF({{dai_cp}}={q(label)},{{dps_max}}/{{cp}},{q('')})"
    kk = R("Xe", "vu_khi_chinh")
    pe, top = lookup("input_vu_khi", "xuyen", kk), lookup("input_vu_khi_suy_ra", "danh_tu_tren", kk)
    tak = lookup("input_vu_khi", "danh_noc", kk)
    xq = lookup("input_vu_khi_suy_ra", "xuyen_qua", kk)
    tg, ta = lookup("input_vu_khi_suy_ra", "he_so_mat_dat", kk), lookup("input_vu_khi_suy_ra", "he_so_may_bay", kk)
    cg, ca = lookup("input_vu_khi_suy_ra", "ban_mat_dat", kk), lookup("input_vu_khi_suy_ra", "ban_may_bay", kk)
    dps_ref = R("Xe_suy_ra", "dps_vu_khi_chinh")
    T2["dps_nhe"] = f"=IF({cg},{dps_ref}*{pen_idx(pe, top, LIGHT, tak, xq)}*{tg},0)"
    T2["dps_nang"] = f"=IF({cg},{dps_ref}*{pen_idx(pe, top, HEAVY, tak, xq)}*{tg},0)"
    T2["dps_may_bay"] = f"=IF({ca},{R('Xe_suy_ra', 'dps_vu_khi_chinh_may_bay')}*{pen_idx(pe, None, 0, None, xq)}*{ta},0)"
    units = {"cp": "CP", "mau_hp": "hp", "dps_nhe": "hp/s", "dps_nang": "hp/s", "dps_may_bay": "hp/s", "dps_max": "hp/s"}
    for c, t in T2.items():
        LB.declare(hd, c, t, "hồi quy (bộ xuất)", unit=units.get(c, "hp/CP" if c.startswith("mau_tren") else
                   "hp/s/CP" if c.startswith("dps_tren") else ""), game=False, meaning=HQ_MEAN.get(c, c.replace("_", " ")))
    pts = []
    for r in xrows:
        if r.id not in per:
            continue
        v, w, cp, hp, dps, dps_air = per[r.id]
        if cp <= 0 or v.get("class") in NOT_IN_FIT or r.values.get("loai_thuc_the") != "xe" or hp is None:
            continue
        p, t_, ta = G.pen(w), G.strikes_top(w), bool(w.get("topAttack"))
        nhe = dps * G.armour_mult(table, p, LIGHT, "Ground", t_, ta) * G.over_mult(table, w, p, LIGHT) * G.type_of(table, w, "Ground") if G.can_target(w, False) else 0.0
        nang = dps * G.armour_mult(table, p, HEAVY, "Ground", t_, ta) * G.over_mult(table, w, p, HEAVY) * G.type_of(table, w, "Ground") if G.can_target(w, False) else 0.0
        bay = dps_air * G.armour_mult(table, p, 0, "Air", t_, ta) * G.over_mult(table, w, p, 0) * G.type_of(table, w, "Air") if G.can_target(w, True) else 0.0
        mx = max(nhe, nang, bay)
        band = "<=8" if cp <= 8 else "9-15" if cp <= 15 else ">=16"
        vals = {"cp": cp, "mau_hp": hp, "dps_nhe": nhe, "dps_nang": nang, "dps_may_bay": bay, "dps_max": mx,
                "ln_cp": math.log(cp), "ln_mau": math.log(hp), "ln_dps": math.log(mx) if mx > 0 else "", "dai_cp": band}
        for tag, label, _f in BANDS:
            vals[f"mau_tren_cp_{tag}"] = hp / cp if band == label else ""
            vals[f"dps_tren_cp_{tag}"] = mx / cp if band == label else ""
        x = hd.row(r.id, f"{B.BALANCE}: vehicles[id={r.id}] (lọc hồi quy)")
        for c, t in T2.items():
            LB.put(x, c, t, vals[c], game=False)
        pts.append(vals)

    hq = book.sheet("Hoi_quy", "Hồi quy theo CP", "Số mũ và hệ số của máu và DPS theo CP (máu = a x CP^b, bình phương nhỏ nhất "
                    "trên ln), N, trung vị máu / CP và DPS / CP theo dải CP (<= 8, 9-15, >= 16)", layer="B")
    LB.declare(hq, "gia_tri", "theo dòng (SLOPE / INTERCEPT / COUNT / MEDIAN trên Hoi_quy_du_lieu)", "hồi quy (bộ xuất)",
               game=False, meaning="giá trị của chỉ số")
    hq.col("y_nghia", meaning="chỉ số")

    def fit(ys, xs):
        pairs = [(x_, y_) for x_, y_ in zip(xs, ys) if isinstance(y_, float) and isinstance(x_, float)]
        mx_, my_ = statistics.fmean(p[0] for p in pairs), statistics.fmean(p[1] for p in pairs)
        b = sum((p[0] - mx_) * (p[1] - my_) for p in pairs) / sum((p[0] - mx_) ** 2 for p in pairs)
        return b, my_ - b * mx_

    D = "Hoi_quy_du_lieu"
    rng = lambda c: R(D, c, "*")  # noqa: E731
    xs = [p["ln_cp"] for p in pts]
    hb, ha = fit([p["ln_mau"] for p in pts], xs)
    db, da = fit([p["ln_dps"] for p in pts], xs)
    rows = [
        ("mau_so_mu", "số mũ b của máu theo CP", f"=SLOPE({rng('ln_mau')},{rng('ln_cp')})", hb),
        ("mau_he_so", "hệ số a của máu theo CP", f"=EXP(INTERCEPT({rng('ln_mau')},{rng('ln_cp')}))", math.exp(ha)),
        ("dps_so_mu", "số mũ b của DPS theo CP", f"=SLOPE({rng('ln_dps')},{rng('ln_cp')})", db),
        ("dps_he_so", "hệ số a của DPS theo CP", f"=EXP(INTERCEPT({rng('ln_dps')},{rng('ln_cp')}))", math.exp(da)),
        ("n_mau", "số xe trong hồi quy máu", f"=COUNT({rng('ln_mau')})", float(len(pts))),
        ("n_dps", "số xe có DPS > 0", f"=COUNT({rng('ln_dps')})", float(sum(1 for p in pts if p["ln_dps"] != ""))),
    ]
    for tag, label, _f in BANDS:
        hp_l = [p[f"mau_tren_cp_{tag}"] for p in pts if p[f"mau_tren_cp_{tag}"] != ""]
        dp_l = [p[f"dps_tren_cp_{tag}"] for p in pts if p[f"dps_tren_cp_{tag}"] != ""]
        rows.append((f"trung_vi_mau_tren_cp_{tag}", f"trung vị máu / CP, dải {label}", f"=MEDIAN({rng(f'mau_tren_cp_{tag}')})",
                     statistics.median(hp_l) if hp_l else None))
        rows.append((f"trung_vi_dps_tren_cp_{tag}", f"trung vị DPS / CP, dải {label}", f"=MEDIAN({rng(f'dps_tren_cp_{tag}')})",
                     statistics.median(dp_l) if dp_l else None))
    for rid, meaning, t, val in rows:
        x = hq.row(rid, "Tools/export (hồi quy trên Hoi_quy_du_lieu)")
        x.set("y_nghia", meaning)
        LB.put(x, "gia_tri", t, val, game=False)
    curve = (math.exp(ha), hb)
    for vid, (v, w, cp, hp, dps, dps_air) in per.items():
        x = sh.rows[vid]
        LB.put(x, "ty_le_so_voi_duong_cong", T["ty_le_so_voi_duong_cong"],
               hp / (curve[0] * cp ** curve[1]) if cp > 0 and hp is not None else "", game=False)

    # ------------------------------------------------------------------ May_bay_so_phat
    mb = book.sheet("May_bay_so_phat", "Máy bay: số phát để hạ", "Mỗi máy bay: máu trong trận, giáp, sát thương một phát và số "
                    "phát của tên lửa tham chiếu (Stinger, Buk, AMRAAM) để hạ (DamageTable.Effective, Air)", layer="B")
    mb.col("id", fk=["02_phuong_tien/Xe"])
    LB.declare(mb, "mau_hp", f"={R('Xe', 'mau_trong_tran_hp')}", "Xe.mau_trong_tran_hp", unit="hp", game=False,
               meaning="máu trong trận")
    LB.declare(mb, "giap", f"={R('Xe', 'giap_truoc')}", "Xe.giap_truoc", game=False, meaning="giáp (mặt trước; máy bay đều)")
    for tag, wid, name in AA_REF:
        per_hit = (f"=IF({lookup('input_vu_khi_suy_ra', 'ban_may_bay', q(wid))},{lookup('input_vu_khi', 'sat_thuong_moi_phat', q(wid))}*"
                   f"{pen_idx(lookup('input_vu_khi', 'xuyen', q(wid)), None, '{giap}', None, lookup('input_vu_khi_suy_ra', 'xuyen_qua', q(wid)))}*"
                   f"{lookup('input_vu_khi_suy_ra', 'he_so_may_bay', q(wid))},0)")
        LB.declare(mb, f"sat_thuong_phat_{tag}", per_hit, f"{DT} Effective(w, armour, Air) x damage", unit="hp",
                   meaning=f"sát thương một phát {name} ({wid}) lên máy bay")
        LB.declare(mb, f"so_phat_{tag}", f"=IF({{sat_thuong_phat_{tag}}}>0,CEILING({{mau_hp}}/{{sat_thuong_phat_{tag}}},1),{q('')})",
                   "ceil(máu / sát thương một phát)", game=False, meaning=f"số phát {name} để hạ")
    mb.col("dai_muc_tieu", meaning="dải số phát mục tiêu: không có nguồn trong repo (spec 02 B); chờ chủ dự án")
    for r in xrows:
        if not r.values.get("bay") or r.values.get("loai_thuc_the") == "tinh_nhue":
            continue
        hp = r.values.get("mau_trong_tran_hp")
        arm = r.values.get("giap_truoc")
        if not isinstance(hp, (int, float)) or not isinstance(arm, (int, float)):
            continue
        x = mb.row(r.id, f"{B.BALANCE}: vehicles[id={r.id}] (máy bay)")
        LB.put(x, "mau_hp", f"={R('Xe', 'mau_trong_tran_hp')}", hp, game=False)
        LB.put(x, "giap", f"={R('Xe', 'giap_truoc')}", arm, game=False)
        for tag, wid, _n in AA_REF:
            w = W.get(wid)
            hit = (G.f(w, "damage") * G.effective(table, w, arm, "Air")) if w and G.can_target(w, True) else 0.0
            LB.put(x, f"sat_thuong_phat_{tag}", mb.cols[f"sat_thuong_phat_{tag}"].formula, hit)
            LB.put(x, f"so_phat_{tag}", mb.cols[f"so_phat_{tag}"].formula, float(math.ceil(hp / hit - 1e-12)) if hit > 0 else "",
                   game=False)
        x.set("dai_muc_tieu", NEED_CODE_CHECK)

    # ------------------------------------------------------------------ Doi_mo_man_suy_ra
    os_ = d.get("openingSquads") or {}
    roles = os_.get("roles") or {}
    dm, vt = book.sheets["Doi_mo_man"], book.sheets["Doi_mo_man_vai_tro"]
    ds = book.sheet("Doi_mo_man_suy_ra", "Đội mở màn: suy ra", "baseCP ước tính của đội mở màn (bộ bài trống: thẻ rẻ nhất mỗi vai "
                    "trò, Doi_mo_man_vai_tro.re_nhat_cp); % CP khởi đầu theo chế độ cần CP khởi đầu của chế độ (mã C#)", layer="B")
    ds.col("id", fk=["02_phuong_tien/Doi_mo_man"])
    LB.declare(ds, "base_cp_uoc_tinh", "=SUM(Doi_mo_man_vai_tro.re_nhat_cp của các vai trò)",
               "Sim/Modes/OpeningSquads.cs Pick (bộ bài trống, không trần ngân sách)", unit="CP",
               meaning="tổng baseCP của đội (thẻ rẻ nhất đủ điều kiện mỗi vai trò; vai trò không có thẻ: bỏ, giữ CP)")
    ds.col("tran_ngan_sach_ty_le", meaning="đội lấy tối đa tỷ lệ này của CP khởi đầu (openingSquads.share)",
           source_note="Sim/Content/OpeningRules.cs Share")
    ds.col("phan_tram_cp_khoi_dau", meaning="% CP khởi đầu mỗi chế độ: CP khởi đầu là số trong mã từng chế độ "
           "(Game/Match/ModeSessions.cs PlayerSide / EnemySide, xem 12/Hang_so_trong_ma); file 05 xuất chế độ")
    share_id = next((rid for rid, r in book.sheets["Doi_mo_man_luat"].rows.items() if r.values.get("khoa") == "share"), None)
    for rid in sorted(dm.rows):
        row = dm.rows[rid]
        side, key = rid.split(".", 1)
        rl = (os_.get("commanders" if side == "commander" else "generals") or {}).get(key) or []
        total = 0
        terms = []
        for role in rl:
            best = G.opening_cheapest(roles[role], res) if role in roles else None
            if best is not None:
                total += best[1]
                terms.append(R("Doi_mo_man_vai_tro", "re_nhat_cp", role))
        x = ds.row(rid, f"{B.BALANCE}: openingSquads.{side}s.{key}")
        LB.put(x, "base_cp_uoc_tinh", "=SUM(" + ",".join(terms) + ")" if terms else "=0", total)
        x.set("tran_ngan_sach_ty_le", F_share(share_id, os_.get("share", 0.6)))
        x.set("phan_tram_cp_khoi_dau", NEED_CODE_CHECK)
    return sh


def F_share(share_id, value):
    from core.formula import F
    if share_id is None:
        return value
    return F("=" + R("Doi_mo_man_luat", "gia_tri_so", share_id), expect=value, ref="python: openingSquads.share")
