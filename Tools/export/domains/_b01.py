"""01_vu_khi_dan, layer B (pass 5): Vu_khi_suy_ra. Live formulas on Vu_khi / Bang_sat_thuong / Bang_xuyen_giap /
He_so_toan_cuc / Canh_bao_vong, each with its _game value (the Python port in _game.py of the C# named in Schema);
the real-rate ratio and the audit flags come from Tools/balance/full_weapon_audit.py (values, not formulas: they depend
on its REAL table's name patterns and the wave 1 sheet)."""
from __future__ import annotations

import copy
import sys

from core.formula import ref as R
from core.model import NEED_CODE_CHECK
from core.repo import ROOT

from . import _balance as B
from . import _game as G
from . import _layer_b as LB

AUDIT_FLAGS = {"TOO FAST": "NHANH_QUA", "TOO SLOW": "CHAM_QUA", "UNIT": "LOI_DON_VI", "FAMILY": "LECH_HO",
               "DISPLAY": "HIEN_THI_SAI", "WAVE 1": "LECH_DOT_1"}
FP = "Sim/Combat/FirePower.cs"
DEF = "Sim/Content/Definitions.cs"
DT = "Sim/Content/DamageTable.cs"
Q = '"'


def audit_rows(ctx, d):
    """Tools/balance/full_weapon_audit.audit (report only; reads the wave 1 sheet in Docs/balance): {weapon: row}."""
    sys.path.insert(0, str(ROOT / "Tools" / "balance"))
    try:
        import full_weapon_audit as FWA  # noqa: WPS433
        rows, _built, _ws = FWA.audit(copy.deepcopy(d))
    except Exception as e:  # noqa: BLE001
        ctx.issue(f"01/Vu_khi_suy_ra: full_weapon_audit unreadable ({type(e).__name__}: {e}); ghi_chu_lech NEED_CODE_CHECK")
        return None
    finally:
        sys.path.pop(0)
    return {r["id"]: r for r in rows}


FF_SRC = "python: Tools/balance/flight_feel_audit.py analyse (flight feel 05/10: class-based effective flight-time validator)"
FF_COLS = [
    ("toc_do_dan_hieu_dung_m_s", "effectiveProjectileSpeedMps", "m/s", "tốc độ đạn hiệu dụng trong game (họ vũ khí đè dòng riêng; không có hệ số boss)"),
    ("toc_do_dan_tran_trang_bi_m_s", "effectiveSpeedAtGearCapMps", "m/s", "tốc độ hiệu dụng khi trang bị ProjectileSpeed đạt trần +30 % (súng chính, vũ khí 0)"),
    ("thoi_gian_bay_tam_toi_thieu_s", "flightTimeMinRangeS", "s", "thời gian bay tại tầm tối thiểu (minRange; không có: 25 % tầm)"),
    ("thoi_gian_bay_nua_tam_s", "flightTimeHalfRangeS", "s", "thời gian bay tại 50 % tầm"),
    ("thoi_gian_bay_tam_toi_da_s", "flightTimeMaxRangeS", "s", "thời gian bay tại tầm tối đa (tầm / tốc độ: Sim không có quỹ đạo cong, đường cong chỉ là hình ảnh)"),
    ("thoi_gian_bay_tam_toi_da_tran_s", "flightTimeMaxRangeAtGearCapS", "s", "thời gian bay tại tầm tối đa khi trang bị ở trần +30 %"),
    ("lop_cam_giac_dan", "projectileFeelClass", "", "lớp cảm giác đạn (DIRECT_FAST / TACTICAL_MISSILE / AIR_DEFENCE_MISSILE / ROCKET_ARTILLERY / MORTAR / HOWITZER / CRUISE / DRONE / BOMB + AIRCRAFT_ROCKET / NAVAL_DIRECT / ANTI_SHIP_MISSILE / BALLISTIC_MISSILE)"),
    ("ket_qua_kiem_dan", "validationBucket", "", "bản kiểm v2 (06/10, owner answer 3): HARD_FAIL / YELLOW_FEEL / PASS_INTENTIONAL_SHORT_RANGE / ok; thay vai trò đọc tốc độ của NHANH_QUA / CHAM_QUA, vốn là cờ chu kỳ bắn, không phải cờ tốc độ đạn"),
    ("ly_do_kiem_dan", "reasonCode", "", "mã lý do của ket_qua_kiem_dan: CANONICAL_SHORT_RANGE / INHERITANCE_MISMATCH / TOO_FAST_FOR_CLASS / TOO_SLOW_FOR_CLASS / INTENTIONAL_BOSS_OVERRIDE / trống (ok)"),
    ("canh_bao_toc_do_dan", "projectileSpeedWarning", "", "[CŨ, giữ để tương thích] bí danh của ket_qua_kiem_dan: HARD_FAIL / YELLOW_FEEL / PASS_INTENTIONAL_SHORT_RANGE / ok"),
    ("nguon_ke_thua_toc_do", "speedInheritanceSource", "", "tốc độ lấy từ đâu: họ vũ khí (weaponFamilies) / dòng riêng / kế thừa từ vũ khí cha"),
    ("khoang_cach_loat_m", "salvoSpacingM", "m", "khoảng cách giữa hai quả trong loạt = tốc độ x burstInterval (tên lửa / rocket nhiều quả)"),
]


def kv_id(sheet, khoa: str):
    return next((rid for rid, r in sheet.rows.items() if r.values.get("khoa") == khoa), None)


def s(text: str) -> str:
    return Q + text + Q


def templates(book):
    hs, cb = book.sheets["He_so_toan_cuc"], book.sheets["Canh_bao_vong"]
    thermo = kv_id(hs, "thermobaric")

    def V(c):
        return R("Vu_khi", c)

    def kv(khoa, default):
        rid = kv_id(cb, khoa)
        return R("Canh_bao_vong", "gia_tri_so", rid) if rid is not None else repr(float(default))

    def type_idx(col):
        return f"INDEX({R('Bang_sat_thuong', col, '*')},MATCH({V('loai_sat_thuong')},{R('Bang_sat_thuong', 'id', '*')},0))"

    def pen_idx(armour, air=False):
        # Combat final 04/10: a topAttack weapon reads Bang_danh_noc only, the rest Bang_xuyen_giap (DamageTable.ArmourMultiplier).
        # Overpenetration 04/10: a Kinetic weapon that is no top attack also reads Bang_xuyen_qua (DamageTable.Overpenetration).
        return LB.armour_index(R('Bang_xuyen_giap', 'he_so', '*'), R('Bang_danh_noc', 'he_so', '*'), V('xuyen'), armour,
                               roof_expr="{danh_tu_tren}", top_expr=V('danh_noc'), air=air,
                               over=R('Bang_xuyen_qua', 'he_so', '*'), over_expr="{xuyen_qua}")

    struct = type_idx("cong_trinh")
    if thermo is not None:
        struct = (f"IF(AND({V('nhiet_ap')},{V('loai_sat_thuong')}={s('HighExplosive')}),"
                  f"MAX({R('He_so_toan_cuc', 'gia_tri_so', thermo)},{struct}),{struct})")
    shot = V("dang_dan")
    return {
        "vien_moi_lan_bop": f"=IF({V('che_do_nong')}={s('SIMULTANEOUS')},MAX(1,{V('so_nong')}),1)",
        "vien_moi_chu_ky": f"=IF({V('bang_dan')}>0,{V('bang_dan')},{V('so_phat_moi_loat')}*{{vien_moi_lan_bop}})",
        "chu_ky_day_du_s": f"=IF({V('bang_dan')}>0,({V('bang_dan')}-1)*{V('thoi_gian_nap_s')}+{V('nap_bang_s')},"
                           f"{V('thoi_gian_nap_s')}+({V('so_phat_moi_loat')}-1)*{V('khoang_phat_trong_loat_s')})",
        "sat_thuong_moi_loat": f"={V('sat_thuong_moi_phat')}*MAX(1,{{vien_moi_chu_ky}})",
        "nap_lai_kho_hieu_dung_s": f"=IF({V('nap_lai_kho_s')}>0,{V('nap_lai_kho_s')},"
                                   f"MIN(28,MAX(10,{V('so_loat_mang')}*{V('thoi_gian_nap_s')}*0.4)))",
        "dps_duy_tri_mot_muc_tieu": f"=IF({V('sat_thuong_moi_phat')}<=0,0,IF({V('so_loat_mang')}>0,"
                                    f"{{sat_thuong_moi_loat}}*{V('so_loat_mang')}/(MAX(0.05,{{chu_ky_day_du_s}})*{V('so_loat_mang')}"
                                    f"+{{nap_lai_kho_hieu_dung_s}}),{{sat_thuong_moi_loat}}/MAX(0.05,{{chu_ky_day_du_s}})))",
        "danh_tu_tren": f"=OR({V('danh_noc')},{V('tam_toi_thieu_m')}>0,{V('bay_cong')},{shot}={s('Bomb')},{shot}={s('Drone')})",
        "ban_mat_dat": f"=AND(NOT({V('chi_danh_chan')}),OR({V('muc_tieu')}={s('Ground')},{V('muc_tieu')}={s('All')}))",
        "ban_may_bay": f"=AND(NOT({V('chi_danh_chan')}),OR({V('muc_tieu')}={s('Air')},{V('muc_tieu')}={s('All')}))",
        "he_so_mat_dat": "=" + type_idx("mat_dat"),
        "he_so_may_bay": "=" + type_idx("may_bay"),
        "he_so_cong_trinh": "=" + struct,
        "xuyen_qua": f"=AND({V('loai_sat_thuong')}={s('Kinetic')},NOT({V('danh_noc')}))",
        "he_so_xuyen_giap_0": "=" + pen_idx(0),
        "he_so_xuyen_giap_2": "=" + pen_idx(2),
        "he_so_xuyen_giap_4": "=" + pen_idx(4),
        "he_so_xuyen_may_bay": "=" + pen_idx(0, air=True),
        "dps_giap_0": "=IF({ban_mat_dat},{dps_duy_tri_mot_muc_tieu}*{he_so_xuyen_giap_0}*{he_so_mat_dat},0)",
        "dps_giap_2": "=IF({ban_mat_dat},{dps_duy_tri_mot_muc_tieu}*{he_so_xuyen_giap_2}*{he_so_mat_dat},0)",
        "dps_giap_4": "=IF({ban_mat_dat},{dps_duy_tri_mot_muc_tieu}*{he_so_xuyen_giap_4}*{he_so_mat_dat},0)",
        "dps_cong_trinh": "=IF({ban_mat_dat},{dps_duy_tri_mot_muc_tieu}*{he_so_xuyen_giap_2}*{he_so_cong_trinh},0)",
        "dps_may_bay": "=IF({ban_may_bay},{dps_duy_tri_mot_muc_tieu}*{he_so_xuyen_may_bay}*{he_so_may_bay},0)",
        "co_vong_canh_bao": (
            f"=IF(OR({shot}={s('Missile')},{shot}={s('Drone')},AND({shot}={s('Rocket')},OR({V('dan_huong')},"
            f"{V('bien_the_id')}={s('guided')})),{V('tia')},{V('dat_boi_boss')},{V('loi_m')}<=0),FALSE,IF({{bac_so}}>=0,"
            f"{{bac_so}}>=4,IF({shot}={s('Shell')},{V('kich_co')}>={kv('gunMinMm', 203)},IF({shot}={s('Bomb')},"
            f"{V('kich_co')}>={kv('bombMinKg', 400)},IF({shot}={s('Rocket')},{V('kich_co')}>={kv('rocketMinMm', 300)},FALSE)))))"),
        "bac_canh_bao": "=IF(AND({bac_so}<0,{co_vong_canh_bao}),4,{bac_so})",
        "thoi_gian_canh_bao_s": (
            f"=IF({{bac_canh_bao}}<4,0,MIN(MAX(0.5,{kv('cap', 6)}),MAX(IF({V('ho_id')}={s('cal_406')},{kv('floor406', 3.5)},"
            f"IF({{bac_canh_bao}}>=5,{kv('floorT5', 4)},{kv('floorT4', 2.5)})),{kv('base', 0.5)}+MAX(0,{V('loi_m')})/"
            f"MAX(0.1,{kv('escapeSpeed', 4.5)}))))"),
    }


REF = {
    "vien_moi_lan_bop": "Sim/Content/WeaponDef.P34.cs RoundsPerPull", "vien_moi_chu_ky": f"{DEF} RoundsPerCycle",
    "chu_ky_day_du_s": f"{DEF} CycleSeconds", "sat_thuong_moi_loat": f"{FP} Volley",
    "nap_lai_kho_hieu_dung_s": f"{DEF} MagazineReload", "dps_duy_tri_mot_muc_tieu": f"{FP} Sustained (carrier null)",
    "danh_tu_tren": "Sim/Content/Armour.cs StrikesTop", "ban_mat_dat": f"{DEF} CanTarget(false)",
    "ban_may_bay": f"{DEF} CanTarget(true)", "he_so_mat_dat": f"{DT} TypeOf(Ground)", "he_so_may_bay": f"{DT} TypeOf(Air)",
    "he_so_cong_trinh": f"{DT} TypeOf(Structure)", "xuyen_qua": f"{DT} Overpenetrates",
    "he_so_xuyen_giap_0": f"{DT} ArmourMultiplier(pen, 0, Ground) x Overpenetration",
    "he_so_xuyen_giap_2": f"{DT} ArmourMultiplier(pen, 2, Ground) x Overpenetration",
    "he_so_xuyen_giap_4": f"{DT} ArmourMultiplier(pen, 4, Ground) x Overpenetration",
    "he_so_xuyen_may_bay": f"{DT} ArmourMultiplier(pen, 0, Air) x Overpenetration",
    "dps_giap_0": f"{FP} Sustained x {DT} Effective(armour 0, Ground)",
    "dps_giap_2": f"{FP} Sustained x {DT} Effective(armour 2, Ground)",
    "dps_giap_4": f"{FP} Sustained x {DT} Effective(armour 4, Ground)",
    "dps_cong_trinh": f"{FP} Sustained x {DT} Effective(armour 2, Structure)",
    "dps_may_bay": f"{FP} SustainedAir x {DT} Effective(armour 0, Air)",
    "co_vong_canh_bao": "Sim/Content/FixRules.cs WarningRules.Warns",
    "bac_canh_bao": "Sim/Content/WeaponDef.P34.cs WarnSeconds (tier)",
    "thoi_gian_canh_bao_s": "Sim/Content/FixRules.cs WarningRules.Seconds",
}
UNIT = {"chu_ky_day_du_s": "s", "nap_lai_kho_hieu_dung_s": "s", "sat_thuong_moi_loat": "hp",
        "dps_duy_tri_mot_muc_tieu": "hp/s", "dps_giap_0": "hp/s", "dps_giap_2": "hp/s", "dps_giap_4": "hp/s",
        "dps_cong_trinh": "hp/s", "dps_may_bay": "hp/s", "thoi_gian_canh_bao_s": "s"}
MEAN = {
    "vien_moi_lan_bop": "viên một lần bóp cò (mọi nòng của súng SIMULTANEOUS, còn lại 1)",
    "vien_moi_chu_ky": "viên một chu kỳ (băng, hoặc loạt x viên một lần bóp)",
    "chu_ky_day_du_s": "chu kỳ đầy đủ: từ viên đầu loạt / băng này tới viên đầu loạt / băng sau",
    "sat_thuong_moi_loat": "sát thương một loạt (cả băng), trước bảng sát thương",
    "nap_lai_kho_hieu_dung_s": "thời gian nạp lại kho dùng thật (reload, hoặc 0,4 x ammo x cooldown kẹp 10-28)",
    "dps_duy_tri_mot_muc_tieu": "DPS duy trì một mục tiêu, trước bảng sát thương và thưởng (cả nạp kho)",
    "danh_tu_tren": "đạn rơi lên nóc (topAttack, cầu vồng, có tầm tối thiểu, bom, drone): không vượt cấp",
    "ban_mat_dat": "nhắm được mục tiêu mặt đất", "ban_may_bay": "nhắm được máy bay",
    "he_so_mat_dat": "hệ số loại sát thương lên mặt đất", "he_so_may_bay": "hệ số loại sát thương lên máy bay",
    "he_so_cong_trinh": "hệ số loại sát thương lên công trình (nhiệt áp: max(thermobaric, hệ số))",
    "xuyen_qua": "đạn động năng bắn thẳng, không đánh nóc: nhân thêm bảng xuyên quá (Bang_xuyen_qua) sau bảng xuyên",
    "he_so_xuyen_giap_0": "hệ số xuyên lên giáp 0 (gồm xuyên quá)", "he_so_xuyen_giap_2": "hệ số xuyên lên giáp 2 (công trình mặc định 2; gồm xuyên quá)",
    "he_so_xuyen_giap_4": "hệ số xuyên lên giáp 4 (gồm xuyên quá)", "he_so_xuyen_may_bay": "hệ số xuyên lên máy bay giáp 0 (không vượt cấp; gồm xuyên quá)",
    "dps_giap_0": "DPS duy trì lên xe giáp 0 (mặt trước, hoặc nóc khi đánh từ trên)",
    "dps_giap_2": "DPS duy trì lên xe giáp 2", "dps_giap_4": "DPS duy trì lên xe giáp 4",
    "dps_cong_trinh": "DPS duy trì lên công trình giáp 2 (giáp mặc định của công trình)",
    "dps_may_bay": "DPS duy trì lên máy bay; giả định (lead chấp nhận 03/10): máy bay giáp 0 (14 / 22 máy bay thẻ)",
    "co_vong_canh_bao": "đạn có vòng cảnh báo", "bac_canh_bao": "bậc dùng cho cảnh báo (không họ mà có cảnh báo: 4)",
    "thoi_gian_canh_bao_s": "thời gian cảnh báo trước khi rơi (0 dưới T4)",
}


def values(table: dict, w: dict, tier: int, rules: dict) -> dict:
    dps = G.sustained(w)
    top = G.strikes_top(w)
    ta = bool(w.get("topAttack"))   # combat final 04/10: the top attack table instead of the direct one
    g, a = G.can_target(w, False), G.can_target(w, True)
    p = G.pen(w)
    warns = G.warns(w, tier, rules)
    return {
        "vien_moi_lan_bop": G.rounds_per_pull(w), "vien_moi_chu_ky": G.rounds_per_cycle(w),
        "chu_ky_day_du_s": G.cycle_seconds(w), "sat_thuong_moi_loat": G.volley(w),
        "nap_lai_kho_hieu_dung_s": G.magazine_reload(w), "dps_duy_tri_mot_muc_tieu": dps, "danh_tu_tren": top,
        "ban_mat_dat": g, "ban_may_bay": a, "he_so_mat_dat": G.type_of(table, w, "Ground"),
        "he_so_may_bay": G.type_of(table, w, "Air"), "he_so_cong_trinh": G.type_of(table, w, "Structure"),
        "xuyen_qua": G.overpenetrates(w),
        "he_so_xuyen_giap_0": G.armour_mult(table, p, 0, "Ground", top, ta) * G.over_mult(table, w, p, 0),
        "he_so_xuyen_giap_2": G.armour_mult(table, p, 2, "Ground", top, ta) * G.over_mult(table, w, p, 2),
        "he_so_xuyen_giap_4": G.armour_mult(table, p, 4, "Ground", top, ta) * G.over_mult(table, w, p, 4),
        "he_so_xuyen_may_bay": G.armour_mult(table, p, 0, "Air", top, ta) * G.over_mult(table, w, p, 0),
        "dps_giap_0": dps * G.effective(table, w, 0, "Ground") if g else 0.0,
        "dps_giap_2": dps * G.effective(table, w, 2, "Ground") if g else 0.0,
        "dps_giap_4": dps * G.effective(table, w, 4, "Ground") if g else 0.0,
        "dps_cong_trinh": dps * G.effective(table, w, 2, "Structure") if g else 0.0,
        "dps_may_bay": G.sustained(w, None, ground=False) * G.effective(table, w, 0, "Air") if a else 0.0,
        "co_vong_canh_bao": warns, "bac_canh_bao": 4 if tier < 0 and warns else tier,
        "thoi_gian_canh_bao_s": G.warn_seconds(w, tier, rules),
    }


def tier_of(w, tiers) -> int:
    t = tiers.get(w.get("weaponFamilyId")) if w.get("weaponFamilyId") else None
    return -1 if t is None else int(t)


def build(ctx, book, d, res, tiers, warn_rules):
    table = d.get("damageTable") or {}
    T = templates(book)
    sh = book.sheet("Vu_khi_suy_ra", "Vũ khí: suy ra", "Lớp B: chu kỳ, sát thương loạt, DPS duy trì theo giáp / công trình / "
                    "máy bay, cảnh báo: công thức sống trên Vu_khi và các bảng hệ số, kèm cột _game (port mã game)", layer="B")
    sh.col("id", fk=["01_vu_khi_dan/Vu_khi"], meaning="vũ khí (Vu_khi.id)")
    sh.col("bac_so", meaning="bậc cỡ của họ 0-5 (weaponFamilyTable[ho_id].tier); -1: không họ (WeaponDef.Tier)",
           source_note="Sim/Content/Catalog.P34.cs ApplyFamilyTable")
    for c in T:
        LB.declare(sh, c, T[c], REF[c], unit=UNIT.get(c, ""), meaning=MEAN[c])
    sh.col("ty_le_chu_ky_so_voi_ngoai_doi", meaning="thời gian một nòng cho một viên (game) / khe tham chiếu ngoài đời "
           "(nhịp tối đa; súng: chậm hơn 30 %); < 0,6 nhanh quá, > 2 chậm quá; trống: không có nhịp thật",
           source_note="python: Tools/balance/full_weapon_audit.py flags_rate")
    sh.col("ghi_chu_lech", meaning="cờ của bản kiểm vũ khí: NHANH_QUA / CHAM_QUA / LOI_DON_VI / LECH_HO / HIEN_THI_SAI / "
           "LECH_DOT_1 (lệch đề xuất đợt 1 không ghi lý do) / ok; trống: đạn thứ hai (bản kiểm chỉ đọc weapons[])",
           enum=["NHANH_QUA", "CHAM_QUA", "LOI_DON_VI", "LECH_HO", "HIEN_THI_SAI", "LECH_DOT_1", "ok"],
           source_note="python: Tools/balance/full_weapon_audit.py audit")
    sh.col("cung_ho_nhat_quan", meaning="cùng một vũ khí thật trên các boss có cùng sát thương / lõi / rìa / tốc độ / loại "
           "(không cờ FAMILY); trống: không phải vũ khí boss", source_note="python: Tools/balance/full_weapon_audit.py audit")
    for c, _k, u, m in FF_COLS:
        sh.col(c, unit=u, meaning=m, source_note=FF_SRC)
    try:
        sys.path.insert(0, str(ROOT / "Tools" / "balance"))
        import flight_feel_audit as FFA  # noqa: WPS433
        _fr, _fi = FFA.resolve_all(copy.deepcopy(d))
        feel = FFA.analyse(_fr, _fi)
    except Exception as e:  # noqa: BLE001
        ctx.issue(f"01/Vu_khi_suy_ra: flight_feel_audit unreadable ({type(e).__name__}: {e})")
        feel = {}
    finally:
        sys.path.pop(0)
    audit = audit_rows(ctx, d)
    for wid in sorted(res):
        w = res[wid]
        tier = tier_of(w, tiers)
        r = sh.row(wid, f"{B.BALANCE}: weapons[id={wid}] (lớp B trên 01_vu_khi_dan/Vu_khi)")
        r.set("bac_so", tier)
        vals = values(table, w, tier, warn_rules)
        for c in T:
            LB.put(r, c, T[c], vals[c])
        for c, k, _u, _m in FF_COLS:
            v = feel.get(wid, {}).get(k)
            r.set(c, "" if v is None else v)
        a_row = audit.get(wid) if audit is not None else None
        if audit is None:
            r.set("ghi_chu_lech", NEED_CODE_CHECK)
        elif a_row is not None:
            flags = [AUDIT_FLAGS.get(x, x) for x in a_row["flags"]]
            r.set("ghi_chu_lech", ";".join(dict.fromkeys(flags)) or "ok")
            r.set("ty_le_chu_ky_so_voi_ngoai_doi", round(a_row["ratio"], 6) if a_row.get("ratio") is not None else "")
            boss_user = any(gr == "boss" for gr, _u, _m in a_row["users"]) and float(a_row["w"].get("damage", 0) or 0) > 0
            r.set("cung_ho_nhat_quan", ("FAMILY" not in a_row["flags"]) if boss_user else "")
    return sh
