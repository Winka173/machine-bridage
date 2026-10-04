"""04_can_cu_thap, layer B (pass 5): Thap_gia_cong_thuc (the rebuild price formula of Tools/balance/p32_tower_prices.py
step by step: effectiveHP, roleDPS, equivalentCP, the standing factor, x 1.25, the size clamp; against the game's
RebuildCost), Tuong_duong_xe_cong_trinh (vehicle-equivalent value, its ratio to the price, the shots of each reference
threat to bring the tower down), Nha_chinh_so_sanh (Tools/balance/p32_hq_types.py: defensive value a minute under attack,
3 HQ types (Fortress ground / air) x HQ 1-5).

The rebuild price is not computed by the game: the game reads "rebuildCp" (BaseRules.RebuildCost) that p32_tower_prices
wrote. So the medians (threats, vehicles per CP) are inputs from that tool, the steps after them are live formulas checked
against it, and lech_voi_game compares the formula price with what the game charges."""
from __future__ import annotations

import math
import sys

from core.formula import lookup, q, ref as R
from core.model import NEED_CODE_CHECK
from core.repo import ROOT

from . import _balance as B
from . import _game as G
from . import _layer_b as LB

W01 = "01_vu_khi_dan"
P32 = "Tools/balance/p32_tower_prices.py"
HQ = "Tools/balance/p32_hq_types.py"
THREATS = ("kinetic", "he", "shaped", "artillery")
V_COLS = [("sat_thuong_moi_phat", "sat_thuong_moi_phat", "hp", "sát thương mỗi phát"), ("xuyen", "xuyen", "", "mức xuyên"),
          ("danh_noc", "danh_noc", "", "đánh nóc (topAttack): bảng đánh nóc, giáp nóc")]
S_COLS = [("danh_tu_tren", "danh_tu_tren", "", "đánh từ trên"), ("ban_mat_dat", "ban_mat_dat", "", "nhắm mặt đất"),
          ("he_so_cong_trinh", "he_so_cong_trinh", "", "hệ số lên công trình")]


def _p32(ctx):
    sys.path.insert(0, str(ROOT / "Tools" / "balance"))
    try:
        import p32_hq_types as H  # noqa: WPS433
        import p32_tower_prices as P  # noqa: WPS433
        return P, H, H.HqModel()
    except Exception as e:  # noqa: BLE001
        ctx.issue(f"04 layer B: {P32} unreadable ({type(e).__name__}: {e})")
        return None, None, None
    finally:
        sys.path.pop(0)


def build(ctx, book, d, res):
    table = d.get("damageTable") or {}
    th = book.sheets["Thap"]
    P, H, m = _p32(ctx)
    if m is None:
        return
    W = B.resolved_weapons(ctx)
    defs = [t for t in P.defs_of_roster(m) if t in th.rows]
    prices = {t: m.price(t) for t in defs}
    picks = {size: m.threats(size) for size in ("Small", "Medium", "Large")}
    wids = sorted({w["id"] for p in picks.values() for w in p.values() if w and w["id"] in W})
    pick = lambda sheet, cols: {w: {c: LB.source_value(ctx, W01, sheet, w, s) for c, s, _u, _m in cols} for w in wids}  # noqa: E731
    LB.input_sheet(ctx, book, "input_vu_khi", "Input: vũ khí (từ 01)", W01, "Vu_khi", V_COLS, pick("Vu_khi", V_COLS))
    LB.input_sheet(ctx, book, "input_vu_khi_suy_ra", "Input: vũ khí suy ra (từ 01)", W01, "Vu_khi_suy_ra", S_COLS,
                   pick("Vu_khi_suy_ra", S_COLS))
    bx = ctx.books[W01].sheets["Bang_xuyen_giap"]
    LB.input_sheet(ctx, book, "input_bang_xuyen_giap", "Input: bảng xuyên giáp (từ 01)", W01, "Bang_xuyen_giap",
                   [("he_so", "he_so", "", "hệ số xuyên của bước")], {rid: {"he_so": r.values.get("he_so")} for rid, r in bx.rows.items()})
    bn = ctx.books[W01].sheets["Bang_danh_noc"]
    LB.input_sheet(ctx, book, "input_bang_danh_noc", "Input: bảng đánh nóc (từ 01)", W01, "Bang_danh_noc",
                   [("he_so", "he_so", "", "hệ số đánh nóc của bước")], {rid: {"he_so": r.values.get("he_so")} for rid, r in bn.rows.items()})

    # ------------------------------------------------------------------ Thap_gia_cong_thuc
    tg = book.sheet("Thap_gia_cong_thuc", "Tháp: công thức giá xây lại", "Từng bước giá xây lại (Tools/balance/p32_tower_prices.py): "
                    "effectiveHP, roleDPS, equivalentCP, hệ số đứng yên, x 1,25, cận cỡ; so với giá game (BaseRules.RebuildCost)",
                    layer="B")
    tg.col("id", fk=["04_can_cu_thap/Thap"])
    for c, unit, meaning in (
            ("co_o", "", "cỡ ô (fort.size)"), ("vai_tro_gia", "", "vai trò định giá (p32 ROLE: light / at / air / ground / multi / util:*)"),
            ("cach_tinh", "", "chien_dau / san (sàn cỡ) / relay / intercept / protect"),
            ("he_so_trung_vi_doa", "", "trung vị hệ số của 4 mối đe dọa tham chiếu lên mặt trước tháp (p32 eff_hp)"),
            ("role_dps", "hp/s", "DPS duy trì lên mục tiêu của vai trò (p32 role_dps)"),
            ("mau_tren_cp_nhom", "hp/CP", "trung vị máu hiệu dụng / CP của xe cùng vai trò (p32 equivalent)"),
            ("dps_tren_cp_nhom", "hp/s/CP", "trung vị DPS vai trò / CP của xe cùng vai trò"),
            ("so_xe_nhom", "", "số xe trong nhóm so sánh"),
            ("he_so_dung_yen", "", "hệ số đứng yên theo tầm (<= 30 m 0,575; <= 50 m 0,625; xa hơn / gián tiếp 0,725)"),
            ("gia_tri_tien_ich", "", "giá trị tiện ích (intercept / protect: p32 utility_value; relay: CP trong 120 s)"),
            ("gia_tri_moc", "", "giá trị tiện ích của tháp mốc (c_ram / shield_tower)"),
            ("gia_moc_cp", "CP", "giá tạm của tháp mốc"),
            ("can_duoi_cp", "CP", "cận dưới theo cỡ (Small 3, Medium 5, Large 9)"),
            ("can_tren_cp", "CP", "cận trên theo cỡ (Small 6, Medium 11, Large 18)")):
        tg.col(c, unit=unit, meaning=meaning, source_note=f"python: {P32}")
    T = {
        "effective_hp": f"=IF({{cach_tinh}}={q('chien_dau')},{R('Thap', 'mau_trong_tran_hp')}/MAX(0.000001,{{he_so_trung_vi_doa}}),{q('')})",
        "equivalent_cp": (f"=IF({{cach_tinh}}={q('chien_dau')},SQRT(MAX(0,({{effective_hp}}/{{mau_tren_cp_nhom}})*"
                          f"({{role_dps}}/{{dps_tren_cp_nhom}}))),{q('')})"),
        "gia_tho": (f"=IF({{cach_tinh}}={q('chien_dau')},{{equivalent_cp}}*{{he_so_dung_yen}}*1.25,IF({{cach_tinh}}={q('san')},"
                    f"{{can_duoi_cp}},IF({{cach_tinh}}={q('relay')},{{gia_tri_tien_ich}},IF({{gia_tri_moc}}>0,"
                    f"{{gia_moc_cp}}*SQRT({{gia_tri_tien_ich}}/{{gia_tri_moc}}),{{can_duoi_cp}}))))"),
        "gia_cong_thuc_cp": "=MAX({can_duoi_cp},MIN({can_tren_cp},ROUND({gia_tho},0)))",
        "lech_voi_game": f"={{gia_cong_thuc_cp}}-{R('Thap', 'runtime_rebuild_cp')}",
    }
    META = {
        "effective_hp": ("hp", "máu hiệu dụng: máu trong trận / trung vị hệ số đe dọa"),
        "equivalent_cp": ("CP", "CP tương đương: sqrt((effHP / effHP mỗi CP) x (roleDPS / DPS mỗi CP))"),
        "gia_tho": ("CP", "giá thô: equivalentCP x hệ số đứng yên x 1,25 (tiện ích: theo cách tính)"),
        "gia_cong_thuc_cp": ("CP", "giá theo công thức: ROUND_HALF_UP(giá thô), kẹp theo cỡ"),
        "lech_voi_game": ("CP", "giá công thức - giá game (Thap.runtime_rebuild_cp); khác 0: dữ liệu đã chỉnh sau công thức "
                                "(REBALANCE_STATS, HOLD) hoặc dữ liệu đổi từ lần --apply"),
    }
    for c, t in T.items():
        LB.declare(tg, c, t, P32 if c != "lech_voi_game" else "gia_cong_thuc_cp - Thap.runtime_rebuild_cp", unit=META[c][0],
                   meaning=META[c][1], game=False)
    for tid in defs:
        p = prices[tid]
        role = p["role"]
        how = "chien_dau" if not role.startswith("util:") else {"floor": "san"}.get(role[5:], role[5:])
        lo, hi = P.CAPS[p["size"]]
        x = tg.row(tid, f"{P32} Model.price('{tid}')")
        x.set("co_o", p["size"])
        x.set("vai_tro_gia", role)
        x.set("cach_tinh", how)
        x.set("can_duoi_cp", lo)
        x.set("can_tren_cp", hi)
        eff = gt = ""
        if how == "chien_dau":
            import statistics
            ms = [m.mult(w, P.front(m.V[tid]), "Structure") for w in p["picks"].values() if w]
            med = statistics.median(ms) if ms else 1.0
            x.set("he_so_trung_vi_doa", med)
            x.set("role_dps", p["dps"])
            x.set("mau_tren_cp_nhom", p["hp_cp"])
            x.set("dps_tren_cp_nhom", p["dps_cp"])
            x.set("so_xe_nhom", p["n"])
            x.set("he_so_dung_yen", p["factor"])
            hp_here = th.rows[tid].values.get("mau_trong_tran_hp")
            eff = hp_here / max(1e-6, med)
            gt = p["eq"]
        elif how in ("intercept", "protect"):
            anchor, anchor_price = P.ANCHORS[how]
            x.set("gia_tri_tien_ich", p["eq"])
            x.set("gia_tri_moc", m.utility_value(how, m.V[anchor]))
            x.set("gia_moc_cp", anchor_price)
        elif how == "relay":
            x.set("gia_tri_tien_ich", p["eq"])
        LB.put(x, "effective_hp", T["effective_hp"], eff if how == "chien_dau" else "", game=False)
        LB.put(x, "equivalent_cp", T["equivalent_cp"], gt if how == "chien_dau" else "", game=False)
        LB.put(x, "gia_tho", T["gia_tho"], p["raw"], game=False)
        LB.put(x, "gia_cong_thuc_cp", T["gia_cong_thuc_cp"], float(p["price"]), game=False)
        LB.put(x, "lech_voi_game", T["lech_voi_game"], float(p["price"] - th.rows[tid].values.get("runtime_rebuild_cp")), game=False)

    # ------------------------------------------------------------------ Tuong_duong_xe_cong_trinh
    td = book.sheet("Tuong_duong_xe_cong_trinh", "Tháp: tương đương xe", "Giá trị tương đương xe (equivalentCP), tỷ lệ so với giá "
                    "game, số phát của từng mối đe dọa tham chiếu theo cỡ ô để hạ tháp (DamageTable.Effective, Structure)", layer="B")
    td.col("id", fk=["04_can_cu_thap/Thap"])
    LB.declare(td, "gia_tri_tuong_duong_xe_cp", f"={R('Thap_gia_cong_thuc', 'equivalent_cp')}", "Thap_gia_cong_thuc.equivalent_cp",
               unit="CP", game=False, meaning="giá trị tương đương xe (CP)")
    LB.declare(td, "ty_le_so_voi_gia", f"=IF(ISNUMBER({{gia_tri_tuong_duong_xe_cp}}),{{gia_tri_tuong_duong_xe_cp}}/"
               f"{R('Thap', 'runtime_rebuild_cp')},{q('')})", "equivalent_cp / runtime_rebuild_cp", game=False,
               meaning="giá trị tương đương / giá xây lại game")
    for k in THREATS:
        td.col(f"doa_{k}", meaning=f"vũ khí đe dọa {k} của cỡ ô (p32 threats: vũ khí trung vị của xe thẻ trong dải giá)",
               fk=["04_can_cu_thap/input_vu_khi"], source_note=f"python: {P32} Model.threats")
        ta = lookup('input_vu_khi', 'danh_noc', f'{{doa_{k}}}')
        # Combat final 04/10: a topAttack threat strikes the tower's roof through the top attack table (DamageTable.ArmourMultiplier).
        idx = LB.armour_index(R('input_bang_xuyen_giap', 'he_so', '*'), R('input_bang_danh_noc', 'he_so', '*'),
                              lookup('input_vu_khi', 'xuyen', f'{{doa_{k}}}'),
                              f"IF({ta},{R('Thap', 'giap_noc')},{R('Thap', 'giap_truoc')})",
                              roof_expr=lookup('input_vu_khi_suy_ra', 'danh_tu_tren', f'{{doa_{k}}}'), top_expr=ta)
        hit = (f"{lookup('input_vu_khi', 'sat_thuong_moi_phat', f'{{doa_{k}}}')}*{idx}*"
               f"{lookup('input_vu_khi_suy_ra', 'he_so_cong_trinh', f'{{doa_{k}}}')}")
        LB.declare(td, f"so_phat_{k}", f"=IF({{doa_{k}}}={q('')},{q('')},IF({hit}>0,CEILING({R('Thap', 'mau_trong_tran_hp')}/({hit}),1),{q('')}))",
                   f"ceil(máu / (damage x {'Sim/Content/DamageTable.cs'} Effective(w, giáp trước, Structure)))", game=False,
                   meaning=f"số phát của mối đe dọa {k} để hạ tháp")
    for tid in defs:
        p = prices[tid]
        x = td.row(tid, f"{P32} Model.price('{tid}') + threats('{p['size']}')")
        eq = p["eq"] if not p["role"].startswith("util:") else ""
        LB.put(x, "gia_tri_tuong_duong_xe_cp", f"={R('Thap_gia_cong_thuc', 'equivalent_cp')}", eq, game=False)
        price = th.rows[tid].values.get("runtime_rebuild_cp")
        LB.put(x, "ty_le_so_voi_gia", td.cols["ty_le_so_voi_gia"].formula, eq / price if eq != "" and price else "", game=False)
        hp = th.rows[tid].values.get("mau_trong_tran_hp")
        arm = th.rows[tid].values.get("giap_truoc")
        for k in THREATS:
            w = picks[p["size"]].get(k)
            if w is None or w["id"] not in W:
                x.set(f"doa_{k}", "")
                LB.put(x, f"so_phat_{k}", td.cols[f"so_phat_{k}"].formula, "", game=False)
                continue
            ww = W[w["id"]]
            x.set(f"doa_{k}", w["id"])
            roof = th.rows[tid].values.get("giap_noc", arm) if ww.get("topAttack") else arm
            per = G.f(ww, "damage") * G.effective(table, ww, roof, "Structure")
            LB.put(x, f"so_phat_{k}", td.cols[f"so_phat_{k}"].formula,
                   float(math.ceil(hp / per - 1e-12)) if per > 0 else "", game=False)

    # ------------------------------------------------------------------ Nha_chinh_so_sanh
    ns = book.sheet("Nha_chinh_so_sanh", "Nhà chính: so sánh kiểu", "Giá trị phòng thủ tương đương mỗi phút căn cứ bị đánh (CP), "
                    "3 kiểu (Pháo đài mặt đất / phòng không, Đồn trú, Khiên) x HQ 1-5 (Tools/balance/p32_hq_types.py)", layer="B")
    for c, unit, meaning in (("kieu", "", "fortress / fortress_air / garrison / shield"), ("cap_hq", "", "cấp HQ 1-5"),
                             ("muc_tieu_duoi_cp", "CP", "dải mục tiêu của prompt 32 (dưới)"),
                             ("muc_tieu_tren_cp", "CP", "dải mục tiêu (trên)"),
                             ("thanh_phan_1", "CP", "fortress: súng thêm; garrison: đội có sẵn (CP); shield: đòn chặn"),
                             ("thanh_phan_2", "CP", "fortress: pháo kích; garrison: đội ra sau (CP trong cả trận đánh); shield: sửa tháp"),
                             ("thanh_phan_3", "CP", "shield: vòm khẩn cấp; còn lại 0"),
                             ("chia_cho", "", "garrison: số phút trận đánh (ATTACK_MINUTES); còn lại 1")):
        ns.col(c, unit=unit, meaning=meaning, source_note=f"python: {HQ}")
    LB.declare(ns, "gia_tri_moi_phut_cp", "=({thanh_phan_1}+{thanh_phan_2}+{thanh_phan_3})/{chia_cho}", HQ, unit="CP",
               game=False, meaning="giá trị phòng thủ tương đương mỗi phút bị đánh")
    LB.declare(ns, "dai", f"=IF({{gia_tri_moi_phut_cp}}<{{muc_tieu_duoi_cp}},{q('low')},IF({{gia_tri_moi_phut_cp}}>"
               f"{{muc_tieu_tren_cp}},{q('high')},{q('in')}))", f"{HQ} band", game=False, meaning="trong dải / thấp / cao",
               enum=["in", "low", "high"])
    try:
        rows = H.run(m)
    except Exception as e:  # noqa: BLE001
        ctx.issue(f"04/Nha_chinh_so_sanh: {HQ} run failed ({type(e).__name__}: {e})")
        rows = {}
    for kind, items in rows.items():
        for lvl, (value, parts) in enumerate(items, start=1):
            x = ns.row(f"{kind}/{lvl}", f"{HQ} HqModel.{kind.split('_')[0]}({lvl})")
            lo, hi = H.TARGETS[lvl]
            x.set("kieu", kind)
            x.set("cap_hq", lvl)
            x.set("muc_tieu_duoi_cp", lo)
            x.set("muc_tieu_tren_cp", hi)
            if kind.startswith("fortress"):
                a, b_, c_, div = parts["gun"], parts["barrage"], 0.0, 1.0
            elif kind == "garrison":
                stocked = value * H.ATTACK_MINUTES - parts["squad_cp"] * H.ATTACK_MINUTES * 60.0 / parts["every"]
                a, b_, c_, div = stocked, parts["squad_cp"] * H.ATTACK_MINUTES * 60.0 / parts["every"], 0.0, H.ATTACK_MINUTES
            else:
                a, b_, c_, div = parts["prevented"], parts["mend"], parts["dome"], 1.0
            x.set("thanh_phan_1", a)
            x.set("thanh_phan_2", b_)
            x.set("thanh_phan_3", c_)
            x.set("chia_cho", div)
            LB.put(x, "gia_tri_moi_phut_cp", ns.cols["gia_tri_moi_phut_cp"].formula, value, game=False)
            LB.put(x, "dai", ns.cols["dai"].formula, H.band(lvl, value), game=False)


def runtime_rebuild(tower: dict, rebuild: dict):
    """Thap.runtime_rebuild_cp: the game's charge (port of BaseRules.RebuildCost)."""
    try:
        return G.rebuild_cost(tower, rebuild)
    except Exception:  # noqa: BLE001
        return NEED_CODE_CHECK
