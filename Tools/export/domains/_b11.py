"""11_meta_giao_dien, layer B (pass 5 part 2): Meta_kinh_te_nguon (every source and sink of coins with its amount, unit
and cap: the reward formulas of Game/Match/Rewards.cs, daily crates and missions, Endless, crates, the shop; rank-ups,
crate prices, skins), Meta_kinh_te_tran (the coins a quick battle pays by difficulty and result, port of
Rewards.Quick, at the reference kills and minutes stated in the row) and Meta_kinh_te (rank 1 -> 10 of one card: coins
and blueprints to the next rank and in all, ports of CardRanks.CoinsSpent / BlueprintsSpent; battles and hours of play to
pay for it at a Normal win; the caps).

The reward literals are read from the C# (cited file:line; NEED_CODE_CHECK when a pattern no longer matches)."""
from __future__ import annotations

from core.formula import q, ref as R
from core.model import NEED_CODE_CHECK

from . import _layer_b as LB

RW = LB.SCRIPTS + "Game/Match/Rewards.cs"
ARS = LB.SCRIPTS + "Game/Match/Arsenal.cs"
DAILY = LB.SCRIPTS + "Game/Match/DailyMissions.cs"
END = LB.SCRIPTS + "Sim/Modes/Endless.cs"
DIFFS = ["Easy", "Normal", "Hard", "VeryHard"]
OUTCOMES = [("thang", 1), ("hoa", 0), ("thua", -1)]
REF_KILLS, REF_MINUTES = 20.0, 9.0   # a reference quick battle (stated in Schema; Conquest / Deathmatch run 6-10 minutes)


def _round_to_int(x: float) -> int:
    """UnityEngine.Mathf.RoundToInt: to the nearest integer, a .5 to the even one (System.Math.Round's default)."""
    return int(round(x))


def build(ctx, book):
    n = lambda path, pat, what, g=0, after=None: LB.cs_num(ctx, path, pat, after=after, what=what, group=g)  # noqa: E731
    F_ = r"([\d.]+)f"
    win, c_w = n(RW, r"var coins = outcome > 0 \? " + F_ + " : outcome == 0 \\? " + F_ + " : " + F_, "Quick base", 0)
    draw, _ = n(RW, r"var coins = outcome > 0 \? " + F_ + " : outcome == 0 \\? " + F_ + " : " + F_, "Quick base", 1)
    loss, _ = n(RW, r"var coins = outcome > 0 \? " + F_ + " : outcome == 0 \\? " + F_ + " : " + F_, "Quick base", 2)
    kcap, c_k = n(RW, r"coins \+= Mathf\.Min\(kills, (\d+)\) \* " + F_, "Quick kills cap", 0)
    kpay, _ = n(RW, r"coins \+= Mathf\.Min\(kills, (\d+)\) \* " + F_, "Quick per kill", 1)
    mcap, c_m = n(RW, r"coins \+= Mathf\.Clamp\(minutes, 0f, " + F_ + r"\) \* " + F_, "Quick minutes cap", 0)
    mpay, _ = n(RW, r"coins \+= Mathf\.Clamp\(minutes, 0f, " + F_ + r"\) \* " + F_, "Quick per minute", 1)
    fac = {}
    for d, pat in (("Easy", r"AiDifficulty\.Easy => " + F_), ("Hard", r"AiDifficulty\.Hard => " + F_),
                   ("VeryHard", r"AiDifficulty\.VeryHard => " + F_), ("Normal", r"_ => " + F_)):
        fac[d] = n(RW, pat, f"DifficultyFactor {d}", after="DifficultyFactor")
    sv = [n(RW, r"var coins = \(" + F_ + r" \+ waves \* " + F_ + r" \+ Mathf\.Min\(kills, (\d+)\) \* " + F_, "Survival", g) for g in range(4)]
    mloss, c_ml = n(RW, r"reward\.Coins = (\d+);", "Mission loss coins", after="if (!won)")
    share = [n(RW, r"var share = first \? " + F_ + " : " + F_, "Mission share", g) for g in range(2)]
    star, c_s = n(RW, r"mission\.RewardCoins \* share \+ (\d+) \* stars", "Mission coins per star")
    tier = [n(RW, r"tier switch \{ 1 => " + F_ + ", 2 => " + F_, "TierPay", g) for g in range(2)]
    wcr, c_wc = n(ARS, r"public const int WinCrates = (\d+);", "DailyCrates.WinCrates")
    acr, c_ac = n(ARS, r"public const int AdCrates = (\d+);", "DailyCrates.AdCrates")
    rmax, c_rm = n(ARS, r"public const int Max = (\d+);", "CardRanks.Max", after="class CardRanks")
    dpd, c_dpd = n(DAILY, r"for \(var n = 0; n < (\d+); n\+\+\)", "daily missions a day")
    ew, c_ew = n(END, r"WaveCoins = (\d+), BossCoins = (\d+), DailyCap = (\d+)", "Endless", 0)
    eb, _ = n(END, r"WaveCoins = (\d+), BossCoins = (\d+), DailyCap = (\d+)", "Endless", 1)
    ec, _ = n(END, r"WaveCoins = (\d+), BossCoins = (\d+), DailyCap = (\d+)", "Endless", 2)

    # ------------------------------------------------------------------ Meta_kinh_te_nguon
    ng = book.sheet("Meta_kinh_te_nguon", "Meta: nguồn và chỗ tiêu xu", "Mỗi nguồn xu (thưởng trận, nhiệm vụ, hòm, nhiệm vụ ngày, Vô "
                    "tận, cửa hàng) và chỗ tiêu xu (nâng hạng, hòm, skin): số xu, đơn vị, trần; số trong mã (Rewards.cs, Arsenal.cs, "
                    "DailyMissions.cs, Endless.cs) hoặc tổng sống của sheet cùng file", layer="B")
    ng.col("loai", meaning="nguon (vào) / tieu (ra)", enum=["nguon", "tieu"])
    ng.col("don_vi_tinh", meaning="mỗi gì (tran / ha_xe / phut / dot / sao / ngay / goi / hang / hom / skin)")
    ng.col("xu", meaning="số xu (hoặc hệ số) mỗi đơn vị; dòng có nguồn là sheet cùng file: công thức sống AVERAGE / MAX / SUM",
           source_note="C# (nguon_ma) / sheet cùng file")
    ng.col("tran", meaning="trần (số đơn vị tối đa, hoặc xu tối đa mỗi ngày)")
    ng.col("ghi_chu", meaning="ghi chú")
    ng.col("nguon_ma", meaning="file:dòng")
    items = [
        ("tran_nhanh_thang", "nguon", "tran", win, "", "Rewards.Quick: thắng", c_w),
        ("tran_nhanh_hoa", "nguon", "tran", draw, "", "Rewards.Quick: hòa", c_w),
        ("tran_nhanh_thua", "nguon", "tran", loss, "", "Rewards.Quick: thua", c_w),
        ("tran_nhanh_ha_xe", "nguon", "ha_xe", kpay, kcap, "Rewards.Quick: mỗi xe hạ, tối đa", c_k),
        ("tran_nhanh_phut", "nguon", "phut", mpay, mcap, "Rewards.Quick: mỗi phút, tối đa (phút)", c_m),
        ("song_sot_co_ban", "nguon", "tran", sv[0][0], "", "Rewards.Survival: cơ bản", sv[0][1]),
        ("song_sot_dot", "nguon", "dot", sv[1][0], "", "Rewards.Survival: mỗi đợt", sv[0][1]),
        ("song_sot_ha_xe", "nguon", "ha_xe", sv[3][0], sv[2][0], "Rewards.Survival: mỗi xe hạ, tối đa", sv[0][1]),
        ("nhiem_vu_thua", "nguon", "tran", mloss, "", "Rewards.Mission: thua", c_ml),
        ("nhiem_vu_sao", "nguon", "sao", star, 3.0, "Rewards.Mission: mỗi sao (x TierPay), tối đa 3 sao", c_s),
        ("nhiem_vu_lan_dau", "nguon", "he_so", share[0][0], "", "Rewards.Mission: phần RewardCoins lần thắng đầu", share[0][1]),
        ("nhiem_vu_choi_lai", "nguon", "he_so", share[1][0], "", "Rewards.Mission: phần RewardCoins khi chơi lại", share[0][1]),
        ("bac_anh_hung", "nguon", "he_so", tier[0][0], "", "Rewards.TierPay: Anh hùng", tier[0][1]),
        ("bac_sat", "nguon", "he_so", tier[1][0], "", "Rewards.TierPay: Sắt", tier[0][1]),
        ("hom_thang_ngay", "nguon", "hom", "", wcr, "DailyCrates.WinCrates: hòm cho các trận thắng đầu mỗi ngày", c_wc),
        ("hom_quang_cao_ngay", "nguon", "hom", "", acr, "DailyCrates.AdCrates: hòm xem quảng cáo mỗi ngày", c_ac),
        ("nhiem_vu_ngay", "nguon", "ngay", None, dpd, "DailyMissions: số nhiệm vụ mỗi ngày (trần); xu: trung bình thưởng của Pool", c_dpd),
        ("vo_tan_dot", "nguon", "dot", ew, ec, "Endless: mỗi đợt; trần xu mỗi ngày", c_ew),
        ("vo_tan_boss", "nguon", "boss", eb, ec, "Endless: mỗi boss; trần xu mỗi ngày", c_ew),
        ("cua_hang_goi_lon_nhat", "nguon", "goi", None, "", "gói xu lớn nhất (Cua_hang)", "Cua_hang"),
        ("nang_hang_tong", "tieu", "the", None, rmax, "xu nâng một thẻ hạng 1 -> tối đa (Nang_hang); trần: hạng tối đa", c_rm),
        ("hom_gia_cao_nhat", "tieu", "hom", None, "", "giá xu của hòm đắt nhất (Hom_do.coin_price)", "Hom_do"),
        ("skin_tong", "tieu", "skin", None, "", "tổng giá mọi skin (Skin.price)", "Skin"),
    ]
    live = {"nhiem_vu_ngay": (f"=AVERAGE({R('Nhiem_vu_ngay', 'thuong_xu', '*')})", "thuong_xu", "Nhiem_vu_ngay", "avg"),
            "cua_hang_goi_lon_nhat": (f"=MAX({R('Cua_hang', 'xu', '*')})", "xu", "Cua_hang", "max"),
            "nang_hang_tong": (f"=SUM({R('Nang_hang', 'xu', '*')})", "xu", "Nang_hang", "sum"),
            "hom_gia_cao_nhat": (f"=MAX({R('Hom_do', 'coin_price', '*')})", "coin_price", "Hom_do", "max"),
            "skin_tong": (f"=SUM({R('Skin', 'price', '*')})", "price", "Skin", "sum")}
    for rid, kind, unit, xu, cap, note, cite in items:
        x = ng.row(rid, f"C#: {cite}")
        for c, v in (("loai", kind), ("don_vi_tinh", unit), ("tran", cap), ("ghi_chu", note), ("nguon_ma", cite)):
            x.set(c, v)
        if rid in live:
            t, col, sheet, how = live[rid]
            vals = [v for v in (r.values.get(col) for r in book.sheets[sheet].rows.values()) if isinstance(v, (int, float))]
            exp = (sum(vals) / len(vals) if how == "avg" else max(vals) if how == "max" else float(sum(vals))) if vals else ""
            LB.put(x, "xu", t, float(exp) if exp != "" else "", game=False)
        else:
            x.set("xu", xu)

    # ------------------------------------------------------------------ Meta_kinh_te_tran
    mt = book.sheet("Meta_kinh_te_tran", "Meta: xu mỗi trận nhanh", "Xu một trận nhanh theo độ khó x kết quả (Rewards.Quick: cơ bản + "
                    f"min(hạ, trần) x xu + min(phút, trần) x xu, x hệ số độ khó), ở trận tham chiếu {REF_KILLS:g} xe hạ, {REF_MINUTES:g} phút",
                    layer="B")
    mt.col("do_kho", fk=["05_che_do_kinh_te/Do_kho"], meaning="độ khó")
    mt.col("ket_qua", meaning="thang / hoa / thua", enum=["thang", "hoa", "thua"])
    mt.col("he_so_do_kho", meaning="Rewards.DifficultyFactor (số trong mã)", source_note=f"C#: {LB.short(RW)} DifficultyFactor")
    mt.col("so_xe_ha", meaning="xe hạ của trận tham chiếu (giả định)")
    mt.col("so_phut", meaning="phút của trận tham chiếu (giả định)")
    NG = lambda rid: R("Meta_kinh_te_nguon", "xu", rid)  # noqa: E731
    TG = lambda rid: R("Meta_kinh_te_nguon", "tran", rid)  # noqa: E731
    base = lambda res: NG(f"tran_nhanh_{res}")  # noqa: E731
    t_mt = lambda res: (f"=ROUND(({base(res)}+MIN({{so_xe_ha}},{TG('tran_nhanh_ha_xe')})*{NG('tran_nhanh_ha_xe')}+MIN(MAX({{so_phut}},0),"  # noqa: E731
                        f"{TG('tran_nhanh_phut')})*{NG('tran_nhanh_phut')})*{{he_so_do_kho}},0)")
    LB.declare(mt, "xu", t_mt("<ket_qua>"), "Game/Match/Rewards.cs Rewards.Quick (Mathf.RoundToInt: .5 về số chẵn; Excel ROUND: .5 ra xa 0)",
               meaning="xu của trận")
    ok_all = all(isinstance(v, float) for v in (win, draw, loss, kcap, kpay, mcap, mpay)) and all(isinstance(fac[d][0], float) for d in DIFFS)
    for d in DIFFS:
        for res, outc in OUTCOMES:
            x = mt.row(f"{d}/{res}", f"{LB.short(RW)} Quick ({fac[d][1]})")
            x.set("do_kho", d)
            x.set("ket_qua", res)
            x.set("he_so_do_kho", fac[d][0])
            x.set("so_xe_ha", REF_KILLS)
            x.set("so_phut", REF_MINUTES)
            b = win if outc > 0 else draw if outc == 0 else loss
            v = float(_round_to_int((b + min(REF_KILLS, kcap) * kpay + min(max(REF_MINUTES, 0.0), mcap) * mpay) * fac[d][0])) if ok_all else NEED_CODE_CHECK
            LB.put(x, "xu", t_mt(res), v)

    # ------------------------------------------------------------------ Meta_kinh_te (rank-ups)
    mk = book.sheet("Meta_kinh_te", "Meta: kinh tế nâng hạng", "Một thẻ từ hạng 1 lên hạng h: xu và bản thiết kế cho lần nâng, tổng từ hạng 1 "
                    "(CardRanks.CoinsSpent / BlueprintsSpent), số trận thắng nhanh Bình thường và giờ chơi để trả đủ xu (trận tham "
                    "chiếu của Meta_kinh_te_tran; bản thiết kế đến từ hòm, không tính giờ); trần: hạng tối đa (CardRanks.Max)", layer="B")
    mk.col("id", fk=["11_meta_giao_dien/Nang_hang"], meaning="hạng h (Nang_hang.id)")
    MK = {
        "xu_len_hang": f"={R('Nang_hang', 'xu')}",
        "xu_tich_luy": f"=SUMIFS({R('Nang_hang', 'xu', '*')},{R('Nang_hang', 'hang', '*')},{q('<=')}&{R('Nang_hang', 'hang')})",
        "ban_thiet_ke_tich_luy": f"=SUMIFS({R('Nang_hang', 'ban_thiet_ke', '*')},{R('Nang_hang', 'hang', '*')},{q('<=')}&{R('Nang_hang', 'hang')})",
        "so_tran_thang": f"=CEILING({{xu_tich_luy}}/{R('Meta_kinh_te_tran', 'xu', 'Normal/thang')},1)",
        "gio_choi": f"={{so_tran_thang}}*{R('Meta_kinh_te_tran', 'so_phut', 'Normal/thang')}/60",
        "trong_tran": f"={R('Nang_hang', 'hang')}<={R('Meta_kinh_te_nguon', 'tran', 'nang_hang_tong')}",
    }
    MM = {"xu_len_hang": ("xu", "xu cho lần nâng lên hạng h (Nang_hang.xu)", False, "Nang_hang.xu"),
          "xu_tich_luy": ("xu", "xu từ hạng 1 tới hạng h", True, "Game/Match/Arsenal.cs CardRanks.CoinsSpent"),
          "ban_thiet_ke_tich_luy": ("", "bản thiết kế từ hạng 1 tới hạng h", True, "Game/Match/Arsenal.cs CardRanks.BlueprintsSpent"),
          "so_tran_thang": ("", "số trận thắng nhanh Bình thường để có đủ xu (chỉ xu thưởng trận)", False, "ceil(xu / xu một trận)"),
          "gio_choi": ("h", "giờ chơi tương ứng (số trận x phút của trận tham chiếu)", False, "số trận x phút / 60"),
          "trong_tran": ("", "hạng h không vượt hạng tối đa (CardRanks.Max)", False, "hang <= Max")}
    for c, (unit, m, game, ref_) in MM.items():
        LB.declare(mk, c, MK[c], ref_, unit=unit, meaning=m, game=game)
    nh = book.sheets["Nang_hang"]
    win_n = LB.F_value(mt.rows["Normal/thang"].values.get("xu"))
    coins = {r.values.get("hang"): r.values.get("xu") for r in nh.rows.values()}
    prints = {r.values.get("hang"): r.values.get("ban_thiet_ke") for r in nh.rows.values()}
    for r in nh.sorted_rows():
        h = r.values.get("hang")
        x = mk.row(r.id, f"11/Nang_hang ({r.id}); {LB.short(ARS)} CardRanks")
        # CardRanks.CoinsSpent(h): sum Coins[1 .. h-1] = the Nang_hang rows 2..h (row k holds Coins[k-1])
        spent = float(sum(v for k, v in coins.items() if isinstance(k, int) and k <= h and isinstance(v, (int, float))))
        bp = float(sum(v for k, v in prints.items() if isinstance(k, int) and k <= h and isinstance(v, (int, float))))
        battles = float(-(-spent // win_n)) if isinstance(win_n, float) and win_n > 0 else NEED_CODE_CHECK
        vals = {"xu_len_hang": coins.get(h), "xu_tich_luy": spent, "ban_thiet_ke_tich_luy": bp, "so_tran_thang": battles,
                "gio_choi": battles * REF_MINUTES / 60 if isinstance(battles, float) else NEED_CODE_CHECK,
                "trong_tran": h <= rmax if isinstance(rmax, float) else NEED_CODE_CHECK}
        for c, (_u, _m, game, _r) in MM.items():
            LB.put(x, c, MK[c], vals[c], game=game)
