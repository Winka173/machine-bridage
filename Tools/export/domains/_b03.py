"""03_boss, layer B (pass 5): Boss_vu_khi's cycle and sustained DPS per mount, Boss_dps (a boss's total sustained DPS now
and at the base version), Boss_hieu_qua (each boss's main weapon against the five reference units of spec 03 B: hits and
time to kill, vehicles caught in the core / edge, warning against the time to get out of the core). Weapon numbers come
from 01 (input_vu_khi, input_vu_khi_suy_ra, input_bang_xuyen_giap), the reference units from 02 (input_xe_tham_chieu)."""
from __future__ import annotations

import math

from core.formula import lookup, q, ref as R
from core.model import NEED_CODE_CHECK

from . import _balance as B
from . import _game as G
from . import _layer_b as LB

W01, X02 = "01_vu_khi_dan", "02_phuong_tien"
FP = "Sim/Combat/FirePower.cs"
DT = "Sim/Content/DamageTable.cs"
SPACING = 8.0  # spec 03 B: five vehicles 8 m apart (a row; a cluster = the centre and four at 8 m)

V_COLS = [("sat_thuong_moi_phat", "sat_thuong_moi_phat", "hp", "sát thương mỗi phát"), ("xuyen", "xuyen", "", "mức xuyên"),
          ("dat_boi_boss", "dat_boi_boss", "", "do hệ boss đặt bắn (laid)"), ("loi_m", "loi_m", "m", "lõi nổ")]
S_COLS = [("dps_duy_tri_mot_muc_tieu", "dps_duy_tri_mot_muc_tieu", "hp/s", "DPS duy trì (FirePower.Sustained, không carrier)"),
          ("chu_ky_day_du_s", "chu_ky_day_du_s", "s", "chu kỳ đầy đủ"), ("danh_tu_tren", "danh_tu_tren", "", "đánh từ trên"),
          ("ban_mat_dat", "ban_mat_dat", "", "nhắm mặt đất"), ("he_so_mat_dat", "he_so_mat_dat", "", "hệ số lên mặt đất"),
          ("he_so_cong_trinh", "he_so_cong_trinh", "", "hệ số lên công trình"),
          ("thoi_gian_canh_bao_s", "thoi_gian_canh_bao_s", "s", "thời gian cảnh báo")]
X_COLS = [("ten_vi_spec", "ten_vi_spec", "", "tên trong spec"), ("mau_trong_tran_hp", "mau_trong_tran_hp", "hp", "máu trong trận"),
          ("giap_truoc", "giap_truoc", "", "giáp trước"), ("giap_noc", "giap_noc", "", "giáp nóc"),
          ("cong_trinh", "cong_trinh", "", "là công trình"), ("toc_do_m_s", "toc_do_m_s", "m/s", "tốc độ")]


def build(ctx, book, d, built, base_built, base_w):
    table = d.get("damageTable") or {}
    ranks = d.get("bossRanks") or {}
    W = B.resolved_weapons(ctx)
    wids = sorted({w for b in built.values() for w in [b.get("weapon")] + [m.get("weapon") for m in b.get("secondary") or []]
                   if w in W})
    pick = lambda sheet, cols: {w: {c: LB.source_value(ctx, W01, sheet, w, s) for c, s, _u, _m in cols} for w in wids}  # noqa: E731
    LB.input_sheet(ctx, book, "input_vu_khi", "Input: vũ khí (từ 01)", W01, "Vu_khi", V_COLS, pick("Vu_khi", V_COLS))
    LB.input_sheet(ctx, book, "input_vu_khi_suy_ra", "Input: vũ khí suy ra (từ 01)", W01, "Vu_khi_suy_ra", S_COLS,
                   pick("Vu_khi_suy_ra", S_COLS))
    bx = ctx.books[W01].sheets["Bang_xuyen_giap"]
    LB.input_sheet(ctx, book, "input_bang_xuyen_giap", "Input: bảng xuyên giáp (từ 01)", W01, "Bang_xuyen_giap",
                   [("he_so", "he_so", "", "hệ số xuyên của bước")], {rid: {"he_so": r.values.get("he_so")} for rid, r in bx.rows.items()})
    tc = ctx.books[X02].sheets["Xe_tham_chieu"]
    refs = [rid for rid in tc.rows if tc.rows[rid].values.get("don_vi_id")]
    LB.input_sheet(ctx, book, "input_xe_tham_chieu", "Input: xe tham chiếu (từ 02)", X02, "Xe_tham_chieu", X_COLS,
                   {rid: {c: tc.rows[rid].values.get(s) for c, s, _u, _m in X_COLS} for rid in refs})

    # ------------------------------------------------------------------ Boss_dps (per boss), Boss_vu_khi formulas
    bd = book.sheet("Boss_dps", "Boss: DPS duy trì", "Tổng DPS duy trì của boss (FirePower.Sustained mọi bệ, trên mặt đất, trước "
                    "bảng sát thương; chưa nhân hạng / pha / fireRate) bây giờ và ở bản gốc", layer="B")
    bd.col("id", fk=["03_boss/Boss"])
    bd.col("he_so_vu_khi", meaning="weaponDamage của boss (kẹp 0,1-10; không áp cho vũ khí laid)",
           source_note="port Sim/Content/Catalog.Extra.cs ParseExtras")
    bd.col("he_so_sat_thuong_ra", meaning="outgoingDamageMult của boss (kẹp 0,1-10)", source_note="port Catalog.Extra.cs ParseExtras")
    bd.col("he_so_hang", meaning="damageScale: của boss, hoặc của hạng (bossRanks); kẹp 0,1-5 (CombatSystem nhân mỗi phát)",
           source_note="port Sim/Content/BossTemplates.cs Rank + Catalog.Extra.cs")
    bd.col("so_be", meaning="số bệ (Boss_vu_khi)")
    bd.col("tong_dps_duy_tri_truoc", unit="hp/s", meaning="tổng DPS duy trì ở bản gốc (Phien_ban.ban_goc; port như cột _game)")
    bv = book.sheets["Boss_vu_khi"]
    LB.declare(bv, "chu_ky_day_du_s", "=" + lookup("input_vu_khi_suy_ra", "chu_ky_day_du_s", "{vu_khi}"),
               "Sim/Content/Definitions.cs CycleSeconds", unit="s", meaning="chu kỳ đầy đủ của vũ khí trên bệ")
    tmpl_mount = (f"=IF({{vu_khi}}={q('')},0,{lookup('input_vu_khi_suy_ra', 'dps_duy_tri_mot_muc_tieu', '{vu_khi}')}*"
                  f"IF({lookup('input_vu_khi', 'dat_boi_boss', '{vu_khi}')},1,{R('Boss_dps', 'he_so_vu_khi', '@BOSS@')})*"
                  f"{R('Boss_dps', 'he_so_sat_thuong_ra', '@BOSS@')})")
    LB.declare(bv, "dps_duy_tri", tmpl_mount, f"{FP} Sustained(w, boss)", unit="hp/s",
               meaning="DPS duy trì của bệ trên mặt đất (weaponDamage trừ vũ khí laid, outgoingDamageMult)")
    LB.declare(bd, "tong_dps_duy_tri", "=SUM(Boss_vu_khi.dps_duy_tri của các bệ)", f"{FP} Sustained(w, boss) cộng mọi bệ",
               unit="hp/s", meaning="tổng DPS duy trì mọi bệ")
    LB.declare(bd, "ty_le_sau_truoc", f"=IF(ISNUMBER({{tong_dps_duy_tri_truoc}}),IF({{tong_dps_duy_tri_truoc}}>0,"
               f"{{tong_dps_duy_tri}}/{{tong_dps_duy_tri_truoc}},{q('')}),{q('')})", "tong / truoc", game=False,
               meaning="tổng DPS bây giờ / ở bản gốc")
    bd.col("cach_bu", meaning="cách bù khi DPS giảm (thêm nòng / thêm bệ / gộp bệ): quyết định thiết kế, không suy được từ "
           "dữ liệu; chờ chủ dự án")

    def boss_total(b, wres):
        car = G.carrier(b, None, boss=True)
        tot, per = 0.0, []
        for wid in [b.get("weapon")] + [m.get("weapon") for m in b.get("secondary") or []]:
            w = wres.get(wid)
            v = G.sustained(w, car) if w else 0.0
            per.append(v)
            tot += v
        return tot, per, car

    for bid in sorted(built):
        b = built[bid]
        tot, per, car = boss_total(b, W)
        x = bd.row(bid, f"{B.BALANCE}: vehicles[id={bid}] dựng bởi Tools/balance/p26_ab.expand")
        x.set("he_so_vu_khi", car["weapon_damage"])
        x.set("he_so_sat_thuong_ra", car["outgoing"])
        x.set("he_so_hang", G.boss_damage_scale(b, ranks))
        x.set("so_be", len(per))
        bb = base_built.get(bid) if base_built else None
        truoc = boss_total(bb, base_w)[0] if bb is not None else ""
        x.set("tong_dps_duy_tri_truoc", truoc)
        terms = []
        for k, v in enumerate(per):
            rid = f"{bid}/{k}"
            if rid in bv.rows:
                r = bv.rows[rid]
                wid = r.values.get("vu_khi")
                w = W.get(wid)
                r.set("ria_tren_boss_m", G.boss_edge(w) if w else "")
                r.set("canh_bao_s", LB.source_value(ctx, W01, "Vu_khi_suy_ra", wid, "thoi_gian_canh_bao_s") if w else "")
                if w:
                    LB.put(r, "chu_ky_day_du_s", bv.cols["chu_ky_day_du_s"].formula, G.cycle_seconds(w))
                    LB.put(r, "dps_duy_tri", tmpl_mount.replace("@BOSS@", bid), v)
                    terms.append(R("Boss_vu_khi", "dps_duy_tri", rid))
                else:
                    r.set("chu_ky_day_du_s", "")
                    r.set("dps_duy_tri", "")
        LB.put(x, "tong_dps_duy_tri", "=SUM(" + ",".join(terms) + ")" if terms else "=0", tot)
        LB.put(x, "ty_le_sau_truoc", bd.cols["ty_le_sau_truoc"].formula,
               (tot / truoc if truoc > 0 else "") if isinstance(truoc, float) else "", game=False)
        x.set("cach_bu", NEED_CODE_CHECK)

    # ------------------------------------------------------------------ Boss_hieu_qua
    bh = book.sheet("Boss_hieu_qua", "Boss: hiệu quả vũ khí chính", "Mỗi boss x vũ khí chính (bệ 0) x xe tham chiếu (spec 03 B): "
                    "số đòn để hạ, thời gian hạ khi dồn hỏa lực, số xe trúng lõi / rìa (5 xe cách 8 m: hàng và cụm), cảnh báo "
                    "so với thời gian thoát lõi, kết luận DU / THIEU", layer="B")
    bh.col("boss_id", fk=["03_boss/Boss"], meaning="boss")
    bh.col("vu_khi", fk=["01_vu_khi_dan/Vu_khi"], meaning="vũ khí chính (bệ 0)")
    bh.col("xe_tham_chieu", fk=["03_boss/input_xe_tham_chieu"], meaning="xe tham chiếu")
    Vi = lambda c: lookup("input_vu_khi", c, "{vu_khi}")  # noqa: E731
    Si = lambda c: lookup("input_vu_khi_suy_ra", c, "{vu_khi}")  # noqa: E731
    Xi = lambda c: lookup("input_xe_tham_chieu", c, "{xe_tham_chieu}")  # noqa: E731
    D = lambda c: lookup("Boss_dps", c, "{boss_id}")  # noqa: E731
    pen_step = f"2-({Vi('xuyen')}-{{giap_mat_trung}})"
    pen_step = f"IF({Si('danh_tu_tren')},MAX(1,{pen_step}),{pen_step})"
    T = {
        "giap_mat_trung": f"=IF({Si('danh_tu_tren')},{Xi('giap_noc')},{Xi('giap_truoc')})",
        "he_so_trung": (f"=IF({Si('ban_mat_dat')},INDEX({R('input_bang_xuyen_giap', 'he_so', '*')},MIN(6,MAX(1,{pen_step}+1)))*"
                        f"IF({Xi('cong_trinh')},{Si('he_so_cong_trinh')},{Si('he_so_mat_dat')}),0)"),
        "sat_thuong_moi_don": (f"={Vi('sat_thuong_moi_phat')}*{D('he_so_hang')}*IF({Vi('dat_boi_boss')},1,{D('he_so_vu_khi')})*"
                               f"{D('he_so_sat_thuong_ra')}*{{he_so_trung}}"),
        "so_don_de_ha": f"=IF({{sat_thuong_moi_don}}>0,CEILING({Xi('mau_trong_tran_hp')}/{{sat_thuong_moi_don}},1),{q('')})",
        "thoi_gian_ha_s": (f"=IF({R('Boss_vu_khi', 'dps_duy_tri', 'BOSSID/0')}*{{he_so_trung}}>0,{Xi('mau_trong_tran_hp')}/"
                           f"({R('Boss_vu_khi', 'dps_duy_tri', 'BOSSID/0')}*{D('he_so_hang')}*{{he_so_trung}}),{q('')})"),
        "so_xe_trung_loi_hang": f"=1+2*MIN(2,FLOOR({Vi('loi_m')}/{SPACING:g},1))",
        "so_xe_trung_ria_hang": f"=1+2*MIN(2,FLOOR(MAX({Vi('loi_m')},{R('Boss_vu_khi', 'ria_tren_boss_m', 'BOSSID/0')})/{SPACING:g},1))",
        "so_xe_trung_loi_cum": f"=IF({Vi('loi_m')}>={SPACING:g},5,1)",
        "so_xe_trung_ria_cum": f"=IF(MAX({Vi('loi_m')},{R('Boss_vu_khi', 'ria_tren_boss_m', 'BOSSID/0')})>={SPACING:g},5,1)",
        "thoi_gian_canh_bao_s": f"={Si('thoi_gian_canh_bao_s')}",
        "thoi_gian_thoat_loi_s": f"=IF(AND({Xi('toc_do_m_s')}>0,{Vi('loi_m')}>0),{Vi('loi_m')}/{Xi('toc_do_m_s')},{q('')})",
        "ket_luan": (f"=IF(ISNUMBER({{thoi_gian_thoat_loi_s}}),IF({{thoi_gian_canh_bao_s}}>={{thoi_gian_thoat_loi_s}},{q('DU')},"
                     f"{q('THIEU')}),{q('')})"),
    }
    META = {
        "giap_mat_trung": ("", "mặt giáp bị trúng: nóc nếu đạn đánh từ trên, còn lại trước", "Sim/Content/Armour.cs StrikesTop", False),
        "he_so_trung": ("", "hệ số một phát lên xe tham chiếu (xuyên x loại; công trình: hệ số công trình)",
                        f"{DT} Effective(w, armour, Ground / Structure)", True),
        "sat_thuong_moi_don": ("hp", "sát thương một phát: damage x damageScale x weaponDamage (trừ laid) x outgoingDamageMult x hệ "
                               "số (CombatSystem.cs; DamageBoost, CommandDamage, LinkDamage = 1)",
                               "Sim/Combat/CombatSystem.cs damageScale x DamageSystem.cs Apply", True),
        "so_don_de_ha": ("", "số phát để hạ (máu trong trận / sát thương một phát, làm tròn lên)", "ceil", False),
        "thoi_gian_ha_s": ("s", "thời gian hạ khi chỉ bệ 0 bắn liên tục (DPS duy trì x damageScale x hệ số); giả định (lead chấp nhận 03/10): vũ khí chính "
                           "(bệ 0), không nhân fireRate của hạng và pha", "máu / DPS", False),
        "so_xe_trung_loi_hang": ("", "xe trúng lõi: 5 xe một hàng cách 8 m, nổ ở xe giữa", "1 + 2 x min(2, floor(lõi / 8))", False),
        "so_xe_trung_ria_hang": ("", "xe trong rìa (rìa trên boss: Boss_vu_khi.ria_tren_boss_m), hàng 5 xe cách 8 m",
                                 "1 + 2 x min(2, floor(max(lõi, rìa) / 8))", False),
        "so_xe_trung_loi_cum": ("", "xe trúng lõi: cụm 5 xe (giữa và 4 xe cách 8 m)", "5 nếu lõi >= 8 m, còn lại 1", False),
        "so_xe_trung_ria_cum": ("", "xe trong rìa, cụm 5 xe", "5 nếu max(lõi, rìa) >= 8 m, còn lại 1", False),
        "thoi_gian_canh_bao_s": ("s", "thời gian cảnh báo của vũ khí (WarnSeconds)", "Sim/Content/FixRules.cs WarningRules.Seconds", False),
        "thoi_gian_thoat_loi_s": ("s", "thời gian xe tham chiếu chạy từ tâm ra khỏi lõi (lõi / tốc độ); trống: đứng yên hoặc không lõi",
                                  "lõi / tốc độ", False),
        "ket_luan": ("", "DU: cảnh báo >= thời gian thoát lõi; THIEU: ngắn hơn; trống: không áp dụng", "so sánh", False),
    }
    for c, t in T.items():
        unit, meaning, ref, game = META[c]
        LB.declare(bh, c, t, ref, unit=unit, meaning=meaning, game=game,
                   enum=["DU", "THIEU"] if c == "ket_luan" else None)
    xv = {rid: {c: tc.rows[rid].values.get(s) for c, s, _u, _m in X_COLS} for rid in refs}
    for bid in sorted(built):
        b = built[bid]
        wid = b.get("weapon")
        w = W.get(wid)
        if w is None:
            continue
        car = G.carrier(b, None, boss=True)
        ds = G.boss_damage_scale(b, ranks)
        dps0 = G.sustained(w, car)
        warn = LB.source_value(ctx, W01, "Vu_khi_suy_ra", wid, "thoi_gian_canh_bao_s")
        core, edge = G.f(w, "splash"), G.boss_edge(w)
        for rid in refs:
            t = xv[rid]
            x = bh.row(f"{bid}/{rid}", f"{B.BALANCE}: vehicles[id={bid}].weapon x {X02}/Xe_tham_chieu[{rid}]")
            x.set("boss_id", bid)
            x.set("vu_khi", wid)
            x.set("xe_tham_chieu", rid)
            top = G.strikes_top(w)
            arm = t["giap_noc"] if top else t["giap_truoc"]
            kind = "Structure" if t["cong_trinh"] else "Ground"
            mult = G.effective(table, w, arm, kind) if G.can_target(w, False) else 0.0
            hit = G.f(w, "damage") * ds * (1.0 if w.get("laid") else car["weapon_damage"]) * car["outgoing"] * mult
            hp = t["mau_trong_tran_hp"]
            escape = core / t["toc_do_m_s"] if t["toc_do_m_s"] and t["toc_do_m_s"] > 0 and core > 0 else ""
            vals = {
                "giap_mat_trung": arm, "he_so_trung": mult, "sat_thuong_moi_don": hit,
                "so_don_de_ha": float(math.ceil(hp / hit - 1e-12)) if hit > 0 else "",
                "thoi_gian_ha_s": hp / (dps0 * ds * mult) if dps0 * mult > 0 else "",
                "so_xe_trung_loi_hang": 1 + 2 * min(2, math.floor(core / SPACING + 1e-12)),
                "so_xe_trung_ria_hang": 1 + 2 * min(2, math.floor(max(core, edge) / SPACING + 1e-12)),
                "so_xe_trung_loi_cum": 5 if core >= SPACING else 1,
                "so_xe_trung_ria_cum": 5 if max(core, edge) >= SPACING else 1,
                "thoi_gian_canh_bao_s": warn, "thoi_gian_thoat_loi_s": escape,
                "ket_luan": ("DU" if warn >= escape else "THIEU") if escape != "" else "",
            }
            for c, tt in T.items():
                LB.put(x, c, tt.replace("BOSSID", bid), vals[c], game=META[c][3])
    return bh
