"""01_vu_khi_dan, layer A: weapons, families, real weapon lines, second rounds, the damage table, counters (APS),
round behaviour, flares, warning rings, global firepower factors.

Vu_khi has two blocks of columns: the spec's Vietnamese names hold the value the game builds (inherits + weapon family
+ the loader's defaults, ported from Catalog.cs), the snake_case names hold each field exactly as balance.json writes
it (one column a source key: the coverage test maps those)."""
from __future__ import annotations

import ast
import re

from core.formula import F
from core.model import NEED_CODE_CHECK, NEED_SOURCE, chua_ap, child_rows
from core.repo import ROOT

from . import _balance as B
from . import _game as G
from . import _b01, _unit_settle

FILE_ID = "01_vu_khi_dan"
TITLE = "Vũ khí và đạn"
DESC = "Vũ khí, họ, dòng vũ khí thật, đạn thay thế, bảng sát thương, khắc chế (APS), hành vi đạn, pháo sáng, vòng cảnh báo"

REASONS = "Tools/balance/fix_weapon_reasons.json"
AUDIT = "Tools/balance/full_weapon_audit.py"
LAYER_B = chua_ap("xuat_luot5")  # kept for the cells pass 5 still leaves (none in 01 after pass 5)

# (column, source key, default when absent, unit, meaning); default NEED_CODE_CHECK: the C# default is not a literal
EFFECTIVE = [
    ("ten_that", "real", "", "", "tên hệ thống thật"),
    ("ho_id", "weaponFamilyId", "", "", "họ vũ khí (Ho_vu_khi)"),
    ("bien_the_id", "weaponVariantId", "", "", "biến thể trong họ"),
    ("dong_vu_khi_id", "weaponFamily", "", "", "dòng vũ khí thật (Dong_vu_khi): tốc độ đạn, cỡ nổ, mẫu đạn chung"),
    ("nhom", "family", "", "", "nhóm vũ khí (mg, tank_gun, rocket...)"),
    ("co_mm", "caliberMm", "", "mm", "cỡ nòng hiển thị"),
    ("dau_no_kg", "warheadKg", "", "kg", "khối lượng đầu nổ hiển thị"),
    ("cong_suat_kw", "powerKw", "", "kW", "công suất (la-de)"),
    ("nang_luong_mj", "energyMj", "", "MJ", "năng lượng (pháo điện từ)"),
    ("loai_sat_thuong", "damageType", "", "", "loại sát thương (Bang_sat_thuong)"),
    ("xuyen", "pen", "Armour.DefaultPenetration", "", "mức xuyên 0-5 (Bang_xuyen_giap); thiếu: theo họ và cỡ (port Armour.cs DefaultPenetration)"),
    ("dang_dan", "projectile", "Shell", "", "dạng đạn (ProjectileKind)"),
    ("so_nong", "barrels", 1, "", "số nòng"),
    ("che_do_nong", "salvoMode", "RIPPLE", "", "SIMULTANEOUS / RIPPLE"),
    ("so_phat_moi_loat", "burst", 1, "", "số phát mỗi loạt"),
    ("khoang_phat_trong_loat_s", "burstInterval", 0.1, "s", "khoảng giữa hai phát trong loạt"),
    ("thoi_gian_nap_s", "cooldown", "", "s", "thời gian nạp giữa hai loạt / phát"),
    ("bang_dan", "clip", 0, "", "số viên một băng (0: không băng)"),
    ("nap_bang_s", "clipReload", 0.0, "s", "thời gian thay băng"),
    ("so_loat_mang", "ammo", 0, "", "số loạt mang theo (0: không giới hạn)"),
    ("nap_lai_kho_s", "reload", 0.0, "s", "thời gian nạp lại kho đạn"),
    ("sat_thuong_moi_phat", "damage", "", "hp", "sát thương mỗi phát"),
    ("loi_m", "splash", 0.0, "m", "bán kính lõi nổ"),
    ("ria_m", "edge", 0.0, "m", "bán kính rìa nổ (0: không rìa)"),
    ("toc_do_dan_m_s", "projectileSpeed", "", "m/s", "tốc độ đạn"),
    ("tam_m", "range", "", "m", "tầm bắn"),
    ("tam_toi_thieu_m", "minRange", 0.0, "m", "tầm tối thiểu"),
    ("muc_tieu", "targets", "Ground", "", "lớp mục tiêu (Ground / Air / All...)"),
    ("tran_ban_m", "ceiling", "", "m", "trần bắn máy bay"),
    ("do_tan", "spread", 0.0, "", "độ tản (đơn vị trong mã: xem Don_vi_chua_ro)"),
    ("bac_no", "impactTier", "", "", "bậc hình ảnh vụ nổ (ExplosionTier)"),
    # pass 5: the flags the layer B formulas read (game values: Catalog.cs FromJson defaults)
    ("danh_noc", "topAttack", False, "", "đánh nóc (topAttack)"),
    ("bay_cong", "lofted", False, "", "bắn cầu vồng qua vật cản (lofted)"),
    ("nhiet_ap", "thermobaric", False, "", "nhiệt áp: HE lên công trình dùng damageTable.thermobaric (thermobaric)"),
    ("chi_danh_chan", "interceptOnly", False, "", "chỉ bắn chặn đạn, không nhắm xe / máy bay (interceptOnly)"),
    ("dat_boi_boss", "laid", False, "", "do hệ boss đặt bắn, không qua CombatSystem (laid)"),
    ("tia", "beam", False, "", "tia (beam)"),
    ("dan_huong", "guided", False, "", "có dẫn (guided: rocket / đạn có dẫn)"),
    ("kich_co", "size", 0.0, "", "cỡ của Sim (size): mm cho súng / rocket, kg cho bom, khác theo họ (Armour.cs DefaultPenetration)"),
    ("so_vien_mang_may_bay", "load", 0, "", "số viên một lần nạp của máy bay (load; Definitions.cs Load)"),
]
TRACKED = ["sat_thuong_moi_phat", "thoi_gian_nap_s", "tam_m", "loi_m", "ria_m", "toc_do_dan_m_s", "so_phat_moi_loat",
           "khoang_phat_trong_loat_s", "so_nong", "che_do_nong", "xuyen", "loai_sat_thuong", "bang_dan", "nap_bang_s",
           "dang_dan", "muc_tieu"]
OWNERS = ["02_phuong_tien/Xe", "03_boss/Boss", "04_can_cu_thap/Thap", "04_can_cu_thap/Tuong", "04_can_cu_thap/Nha_chinh",
          "04_can_cu_thap/Mo_dun_tien_ich"]
PEN_STEPS = ["+2", "+1", "0", "-1", "-2", "-3"]
MUNITIONS = ["directMissile", "drone", "directRocket", "artilleryRocket", "mortarShell", "artilleryShell", "tankShell",
             "bullet", "energy"]
VEHICLE_KEYS = ("aps", "apsCapability", "interceptionMode", "flares", "flareCharges", "flareRecharge")


def effective(w: dict, tiers: dict) -> dict:
    out = {}
    for col, key, default, _u, _m in EFFECTIVE:
        out[col] = w.get(key, default)
    out["xuyen"] = G.pen(w)  # Definitions.cs Penetration: data "pen", else Armour.DefaultPenetration
    out["bac_co"] = f"T{tiers[w['weaponFamilyId']]}" if w.get("weaponFamilyId") in tiers else ""
    return out


FLIGHT = ("=IF(AND({co_vong_canh_bao},{thoi_gian_canh_bao_s}>{tam_m}/{toc_do_dan_m_s}),{thoi_gian_canh_bao_s},"
          "{tam_m}/{toc_do_dan_m_s})")
FLIGHT_REF = "game: Sim/Combat/CombatSystem.cs Fire (travel)"


def flight_time(e, tier, warn_rules):
    """CombatSystem.cs Fire, the first round at full range from a ground shooter: travel = range / ProjectileSpeed; a warned
    round (Warns and WarnSeconds > travel) lands at WarnSeconds. None without a projectile speed."""
    speed = G.f(e, "projectileSpeed")
    if speed <= 0:
        return None
    travel = G.f(e, "range") / speed
    if G.warns(e, tier, warn_rules):
        ws = G.warn_seconds(e, tier, warn_rules)
        if ws > travel:
            travel = ws
    return travel


def real_rates():
    """The REAL table of Tools/balance/full_weapon_audit.py (pattern on the real name, max rpm, practical rpm, kind,
    mount, source), read as a literal (the module is not run)."""
    tree = ast.parse((ROOT / AUDIT).read_text("utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "REAL" for t in node.targets):
            return ast.literal_eval(node.value)
    return []


BOM_STICK_COLS = [
    # (column, stick key, unit, meaning): the bomb-run fix's stick parameters (weapons[*].stick); the full set is in the bomb export
    ("che_do_tha", "mode", "", "POINT / STICK / PATTERN"),
    ("cach_tha", "drop", "", "OVERFLY (bay qua, bom rơi tự do) / BAY (khoang bom boss, dải đặt quanh điểm nhắm)"),
    ("so_bom_dai_n", "bombs", "", "số bom một lượt (n)"),
    ("khoang_cach_giua_bom_m", "spacing", "m", "spacing = 1,1 × lõi"),
    ("do_dai_dai_m", "length", "m", "(n − 1) × spacing"),
    ("chu_ky_tha_giua_bom_s", "interval", "s", "spacing / tốc độ lúc thả"),
    ("ty_le_chong_lan", "overlap", "", "lõi / spacing (0,8–1,2)"),
    ("do_rong_dai_m", "width", "m", "2 × rìa + 2 × lệch ngang"),
    ("canh_bao_dang", "warnShape", "", "NONE / RING / STICK_RECT"),
]


def _bom_link(ctx, book, res, users):
    """The bomb-run fix, pass 4: file 01 links the bomb export (Docs/export/bom_<date>/, `export.py bom`: the six Bom_* sheets,
    the drop trace before / after) with one row per bomb weapon: its main stick numbers and the card's words. The values are
    the stick block's (already mapped by the Vu_khi columns: nothing is marked twice here)."""
    folders = sorted(p for p in (ROOT / "Docs" / "export").glob("bom_*") if p.is_dir())
    where = folders[-1].relative_to(ROOT).as_posix() if folders else "Docs/export/bom_<ngay>"
    stem = f"Machine_Brigade_Bom_{where.rsplit('bom_', 1)[-1]}"
    sh = book.sheet("Bom_rai_tham", "Ném bom rải thảm (liên kết)",
                    f"Mỗi vũ khí thả bom một dòng: tham số dải chính (weapons[*].stick) và câu thẻ; bảng đủ (Bom_vu_khi, Bom_don_vi, "
                    f"Bom_hanh_vi, Bom_vet_tha, Bom_canh_bao, Bom_ket_qua_vung) ở {where}/{stem}.xlsx và .md")
    sh.col("vu_khi_id", meaning="vũ khí (Vu_khi)", fk=["01_vu_khi_dan/Vu_khi"])
    for col, _key, unit, meaning in BOM_STICK_COLS:
        sh.col(col, unit=unit, meaning=meaning)
    sh.col("mang_boi", meaning="id đơn vị mang (ngăn ';')", kind="text")
    sh.col("the_vi", meaning="câu thẻ máy bay sinh từ dữ liệu (StickLines.Words, tiếng Việt)", kind="text")
    sh.col("the_en", meaning="câu thẻ máy bay sinh từ dữ liệu (StickLines.Words, tiếng Anh)", kind="text")
    sh.col("bang_day_du", meaning="file của bản xuất ném bom (đủ cột, vết thả trước / sau)", kind="text")
    for wid in sorted(res):
        stick = res[wid].get("stick")
        if not isinstance(stick, dict):
            continue
        r = sh.row(wid, f"{B.BALANCE}: weapons[{wid}].stick (giá trị game sau inherits); bản đủ: {where}/")
        r.set("vu_khi_id", wid)
        for col, key, _unit, _meaning in BOM_STICK_COLS:
            r.set(col, stick.get(key, ""))
        r.set("mang_boi", ";".join(sorted({u[1] for u in users.get(wid, [])})))
        n, spacing = int(stick.get("bombs") or 0), float(stick.get("spacing") or 0)
        laid = stick.get("mode") == "STICK" and n > 1
        r.set("the_vi", _card(n, spacing, True) if laid else "")
        r.set("the_en", _card(n, spacing, False) if laid else "")
        r.set("bang_day_du", f"{where}/{stem}.xlsx; {where}/{stem}.md; {where}/BOM_REPORT.md")


def _card(n: int, spacing: float, vietnamese: bool) -> str:
    """StickLines.Words (Game/Hud/StickLines.cs): "thả N quả, cách nhau X m, dải Y m" / "N bombs X m apart, a Y m stick"."""
    def f(v: float) -> str:
        t = f"{v:.0f}" if v >= 10 or abs(v - round(v)) < 0.05 else f"{v:.1f}"
        return t.replace(".", ",") if vietnamese else t
    length = max(0, n - 1) * spacing
    return f"thả {n} quả, cách nhau {f(spacing)} m, dải {f(length)} m" if vietnamese else f"{n} bombs {f(spacing)} m apart, a {f(length)} m stick"


def _drone_sheet(book, d, res, users):
    """Drone (play-test 13): one table of every drone: the drone rounds vehicles send (FPV, Lancet, Shahed...) and the drone
    aircraft. Data values here; the values the game builds or draws (speed, blast, flight, drawn size) come from game.json
    balancePack.drones (core/gamefill.py)."""
    sh = book.sheet("Drone", "Drone: tốc độ, đầu nổ, cỡ, vụ nổ",
                    "Mọi drone của game một dòng: drone đạn (FPV, Lancet, Shahed do xe phóng) và máy bay drone; tốc độ bay, "
                    "đầu nổ (kg), sát thương, bán kính nổ lõi / rìa, tầm, thời gian bay, cỡ (dài) và cỡ vụ nổ khi vẽ")
    for c, unit, m in (("loai", "", "dan_drone (drone vũ khí, bay tới mục tiêu và nổ) / may_bay_drone (máy bay không người lái)"),
                       ("ten_that", "", "hệ thống thật"), ("mang_boi", "", "đơn vị phóng / mang (ngăn ';')"),
                       ("toc_do_m_s", "m/s", "tốc độ bay (drone đạn: tốc độ đạn game dựng; máy bay: speed)"),
                       ("do_cao_m", "m", "độ cao bay (máy bay drone)"),
                       ("dau_no_kg", "kg", "khối lượng đầu nổ / bom (warheadKg; máy bay: của vũ khí, ngăn ';')"),
                       ("sat_thuong", "hp", "sát thương mỗi drone (game dựng)"),
                       ("loi_m", "m", "bán kính lõi nổ (SplashRadius)"), ("ria_m", "m", "bán kính rìa nổ (0: một lớp)"),
                       ("tam_m", "m", "tầm phóng"), ("thoi_gian_bay_toi_tam_s", "s", "thời gian bay tới tầm tối đa"),
                       ("mau_hp", "hp", "máu (máy bay drone)"), ("vu_khi", "", "vũ khí của máy bay drone (ngăn ';')"),
                       ("mo_hinh", "", "mô hình vẽ drone đạn"),
                       ("kich_thuoc_m", "m", "cỡ: drone đạn = chiều dài khi vẽ; máy bay drone = dài x rộng x cao (modelSize)"),
                       ("no_hinh_x", "x", "vụ nổ khi vẽ lớn hơn vụ nổ chung bao nhiêu lần (BlastSizes.Drone)")):
        sh.col(c, unit=unit, meaning=m)
    for wid in sorted(w for w, e in res.items() if e.get("projectile") == "Drone"):
        e = res[wid]
        r = sh.row(wid, f"{B.BALANCE}: weapons[{wid}] (giá trị game từ game.json balancePack.drones)")
        r.set("loai", "dan_drone")
        r.set("ten_that", e.get("real", ""))
        r.set("mang_boi", ";".join(sorted({u for _k, u, _m in users.get(wid, [])})))
        r.set("dau_no_kg", e.get("warheadKg", 0))
        for c in ("toc_do_m_s", "sat_thuong", "loi_m", "ria_m", "tam_m", "thoi_gian_bay_toi_tam_s", "mo_hinh", "kich_thuoc_m", "no_hinh_x"):
            r.set(c, NEED_CODE_CHECK)
    weapons = {w: e for w, e in res.items()}
    for v in d.get("vehicles", []):
        if not v.get("drone"):
            continue
        vid = v["id"]
        arms = [v.get("weapon")] + [x.get("weapon") for x in v.get("secondary") or [] if isinstance(x, dict)]
        arms = [a for a in arms if isinstance(a, str) and a and a != "none"]
        r = sh.row(vid, f"{B.BALANCE}: vehicles[{vid}]")
        r.set("loai", "may_bay_drone")
        r.set("ten_that", v.get("real", ""))
        r.set("toc_do_m_s", v.get("speed", ""))
        r.set("do_cao_m", v.get("altitude", ""))
        r.set("mau_hp", v.get("hp", ""))
        r.set("vu_khi", ";".join(arms))
        r.set("dau_no_kg", ";".join(f"{a}:{weapons.get(a, {}).get('warheadKg', 0)}" for a in arms))
        size = v.get("modelSize")
        r.set("kich_thuoc_m", " x ".join(f"{x:g}" for x in size) if isinstance(size, list) else "")


TEN_LUA_COLS = [
    # (column, unit, meaning). "EXISTS": already a per-weapon data field (named). "KHONG_CO": no mechanism in the
    # Sim reads this (reason in the meaning). Balance pack 2 addendum item 2.
    ("ten_that", "", "tên hệ thống thật"),
    ("kieu_dan", "", "suy từ dữ liệu: khong_dan (không guided) / bam_radar (weaponFamilyId trong munitionRules."
     "radarGuided) / tam_nhin_SACLOS (trong sightGuided: dây, chùm, laser dẫn bởi tầm nhìn bên bắn) / bam_nhiet "
     "(guided, không radarGuided, flareEligible != false: hồng ngoại, bị pháo sáng kéo đi). Mã không phân biệt "
     "laser / ảnh nhiệt / GPS-quán tính riêng: chỉ ba nhóm trên (NEED_CODE_CHECK nếu cần phân biệt thêm để chủ dự "
     "án quyết)."),
    ("co_can_tam_nhin", "", "EXISTS (suy ra): true khi kieu_dan = tam_nhin_SACLOS (CombatSystem.Munitions.cs LostSight: "
     "bên bắn chết, bên bắn hoặc mục tiêu trong khói, hoặc có vật cản chắn tầm nhìn hai xe mặt đất)"),
    ("toc_do_quay_deg_s", "deg/s", "KHONG_CO: không có mô phỏng động học quay đạn (đạn dẫn 'homing' luôn trúng vị trí "
     "mục tiêu lúc hết thời gian bay trừ khi bị chệch bởi APS / gây nhiễu / mất dấu / pháo sáng / ra ngoài tầm)"),
    ("gia_toc_ngang_m_s2", "m/s2", "KHONG_CO: không mô phỏng gia tốc ngang (không có vật lý bay chi tiết)"),
    ("ban_kinh_quay_m", "m", "KHONG_CO: không có mô phỏng bán kính lượn"),
    ("he_so_bam", "", "KHONG_CO: không có hệ số dẫn đường tỉ lệ (proportional navigation); dẫn là nhị phân (trúng / "
     "chệch theo luật, xem ty_le_trung_co_ban)"),
    ("thoi_gian_khoa_s", "s", "KHONG_CO: không có thời gian khóa mục tiêu trước khi bắn"),
    ("quy_dao", "", "EXISTS: flight_profile (Direct / Loft / Ballistic; cột Vu_khi.bay_cong + flight_profile); "
     "danh_noc (topAttack) cũng đẩy về Loft khi không khai báo flight_profile riêng (WeaponDef.P34.cs)"),
    ("ngoi_can_dich_m", "m", "MOVED (addendum 2): tham số nhóm cũ munitionRules.proximityFuze = 7 m; nay có cờ dữ liệu "
     "riêng từng vũ khí WeaponDef.ProximityFuze (null = theo nhóm). Giá trị dưới đây bằng giá trị nhóm cho mọi vũ khí "
     "(chưa vũ khí nào ghi đè). CHÚ Ý: chưa cơ chế nào trong mã đọc proximityFuze để quyết nổ cận đích (xem mục báo "
     "cáo CHANGES.md) — cờ đã sẵn, hành vi game không đổi."),
    ("ty_le_trung", "", "EXISTS (nhóm, không theo từng vũ khí): 1 − (weapons.guidance.baseFailChance + "
     "weapons.guidance.rangeFailCoeff × tầm_phần_trăm² + mountFail của bệ); tầm_phần_trăm = khoảng_cách / tầm, trần 1,2 "
     "(CombatSystem.cs Fire)"),
    ("jam_miss_min_m", "m", "MOVED (addendum 2): tham số nhóm cũ weapons.jamRules.guidedMissMin; nay WeaponDef."
     "JamMissMin riêng từng vũ khí (null = theo nhóm); giá trị dưới đây = giá trị nhóm (chưa vũ khí nào ghi đè)"),
    ("jam_miss_spread_m", "m", "MOVED (addendum 2): như trên, weapons.jamRules.guidedMissSpread / WeaponDef."
     "JamMissSpread"),
    ("thoi_gian_giua_hai_qua_s", "s", "EXISTS: khoang_phat_trong_loat_s (burstInterval)"),
    ("so_qua_moi_bang", "", "EXISTS: bang_dan (clip)"),
    ("vertical_launch", "", "KHONG_CO: không có cờ phóng thẳng đứng riêng; mọi bệ bắn từ điểm Mount_ của nó bất kể "
     "kiểu bệ"),
]


def _ten_lua_sheet(book, d, res, users, tiers):
    """Balance pack 2 addendum item 2: Ten_lua_tham_so, one row per missile weapon (projectile == Missile). The
    guidance-kind, jam-miss and proximity-fuze columns are derived from the per-weapon override fields added this
    addendum (WeaponDef.ProximityFuze / JamMissMin / JamMissSpread; FixRules.cs MunitionRules.RadarGuided /
    SightGuided); everything else not listed in TEN_LUA_COLS already has its own Vu_khi column (sat_thuong_moi_phat,
    loi_m, ria_m, tam_m, tam_toi_thieu_m, toc_do_dan_m_s, dan_huong, flare_resist, flare_eligible, aps_eligible,
    ciws_eligible, interceptable, jam_proof, bang_dan, nap_bang_s, thoi_gian_nap_s): look those up by vu_khi_id."""
    mr = d.get("munitionRules") or {}
    radar_guided = set(mr.get("radarGuided") or [])
    sight_guided = set(mr.get("sightGuided") or [])
    sh = book.sheet("Ten_lua_tham_so", "Tên lửa: tham số",
                    "Mỗi vũ khí tên lửa (projectile = Missile) một dòng: kiểu dẫn, cận đích, trúng / chệch, jam; mọi cột "
                    "khác (sát thương, tầm, tốc độ đạn, pháo sáng, APS...) đã có ở Vu_khi — tra theo vu_khi_id")
    sh.col("vu_khi_id", meaning="vũ khí (Vu_khi)", fk=["01_vu_khi_dan/Vu_khi"])
    for col, unit, meaning in TEN_LUA_COLS:
        sh.col(col, unit=unit, meaning=meaning)
    sh.col("mang_boi", meaning="id đơn vị mang (ngăn ';')", fk=OWNERS + ["03_boss/Boss_bo_phan_thu_vien"])
    for wid in sorted(w for w, e in res.items() if e.get("projectile") == "Missile"):
        e = res[wid]
        fam = e.get("weaponFamilyId")
        guided = bool(e.get("guided"))
        sight = guided and fam in sight_guided
        radar = guided and fam in radar_guided
        flare_eligible = e.get("flareEligible")
        heat = guided and not sight and not radar and flare_eligible is not False
        kieu_dan = "tam_nhin_SACLOS" if sight else "bam_radar" if radar else "bam_nhiet" if heat else \
            "khong_dan" if not guided else "khac (NEED_CODE_CHECK)"
        r = sh.row(wid, f"{B.BALANCE}: weapons[{wid}] (guided/weaponFamilyId) + munitionRules.radarGuided/sightGuided")
        r.set("vu_khi_id", wid)
        r.set("ten_that", e.get("real", ""))
        r.set("kieu_dan", kieu_dan)
        r.set("co_can_tam_nhin", sight)
        for c in ("toc_do_quay_deg_s", "gia_toc_ngang_m_s2", "ban_kinh_quay_m", "he_so_bam", "thoi_gian_khoa_s",
                  "vertical_launch"):
            r.set(c, "KHONG_CO")
        r.set("quy_dao", e.get("flightProfile") or ("Loft" if e.get("topAttack") else "Direct"))
        r.set("ngoi_can_dich_m", e.get("proximityFuze", mr.get("proximityFuze", 7)))
        r.set("ty_le_trung", "xem mô tả cột (phụ thuộc tầm bắn, không phụ thuộc tốc độ mục tiêu)")
        r.set("jam_miss_min_m", e.get("jamMissMin", 5))
        r.set("jam_miss_spread_m", e.get("jamMissSpread", 6))
        r.set("thoi_gian_giua_hai_qua_s", e.get("burstInterval", 0.1))
        r.set("so_qua_moi_bang", e.get("clip", 0))
        us = users.get(wid, [])
        r.set("mang_boi", ";".join(sorted({u[1] for u in us})))


def build(ctx):
    book = ctx.book(FILE_ID, TITLE, DESC)
    d = B.bal(ctx)
    res = B.resolved_weapons(ctx)
    tiers = {f["id"]: f.get("tier") for f in d.get("weaponFamilyTable", [])}
    users = B.weapon_users(ctx)
    base = B.base_view(ctx)
    base_res = B.resolved_weapons(base) if base else {}
    base_tiers = {f["id"]: f.get("tier") for f in base.data(B.BALANCE).get("weaponFamilyTable", [])} if base else {}
    real = real_rates()
    warn_rules = d.get("warningRules") or {}
    reasons = ctx.data(REASONS) if REASONS in ctx.sources else {}

    # ------------------------------------------------------------------ Vu_khi
    vk = book.sheet("Vu_khi", "Vũ khí", "Mỗi vũ khí (cả đạn thứ hai) một dòng: giá trị game (cột tiếng Việt) và trường gốc")
    for col, key, default, unit, meaning in EFFECTIVE:
        fk = ["01_vu_khi_dan/Ho_vu_khi"] if col == "ho_id" else ["01_vu_khi_dan/Dong_vu_khi"] if col == "dong_vu_khi_id" else None
        vk.col(col, unit=unit, meaning=f"{meaning} [giá trị game: {key}, mặc định {default!r}]", fk=fk,
               source_note=f"{B.BALANCE}: weapons[*].{key} sau inherits + weaponFamily (Catalog.Inherited, WeaponFamilies)")
    vk.col("bac_co", meaning="bậc cỡ T0-T5 (weaponFamilyTable[ho_id].tier)", enum=[f"T{i}" for i in range(6)])
    vk.col("ke_thua_tu", meaning="vũ khí cha (inherits)", fk=["01_vu_khi_dan/Vu_khi"])
    vk.col("dan_thay_the", meaning="đạn thay thế: he; air; đạn thứ hai có roundOf = vũ khí này (Dan_thay_the)",
           fk=["01_vu_khi_dan/Vu_khi"])
    vk.col("cua_ai", meaning="loại đơn vị mang: xe / thap / boss / cong_trinh / boss_part", kind="text")
    vk.col("mang_boi", meaning="id đơn vị mang (ngăn ';')", fk=OWNERS + ["03_boss/Boss_bo_phan_thu_vien"])
    vk.col("so_don_vi_mang", meaning="số đơn vị mang")
    vk.col("ten_be", meaning="bệ: <đơn vị>:<chỉ số bệ> (0 = vũ khí chính, k = secondary[k-1]; other = nhắc ở trường khác)")
    vk.col("thoi_gian_canh_bao_s", unit="s", meaning="thời gian cảnh báo vòng: WeaponDef.WarnSeconds (port FixRules.cs "
           "WarningRules.Seconds; công thức sống ở Vu_khi_suy_ra)", source_note="port Sim/Content/WeaponDef.P34.cs WarnSeconds")
    vk.col("co_vong_canh_bao", meaning="có vòng cảnh báo: WarningRules.Warns (port FixRules.cs; công thức sống ở Vu_khi_suy_ra)",
           source_note="port Sim/Content/FixRules.cs WarningRules.Warns")
    vk.col("lech_nong_s", unit="s", meaning="lệch giữa các nòng RIPPLE (hằng số trong mã)")
    vk.col("thoi_gian_bay_toi_tam_s", unit="s", meaning="thời gian bay tới tầm tối đa, phát đầu: tầm / tốc độ đạn, kéo dài tới "
           "thời gian cảnh báo khi vũ khí có vòng (lớp B: công thức sống; port CombatSystem.cs Fire: travel = distance / "
           "ProjectileSpeed, WarnSeconds > travel và Warns -> WarnSeconds; bom thả từ máy bay phụ thuộc tốc độ máy bay: "
           "_game NEED_CODE_CHECK)", formula=FLIGHT, source_note=FLIGHT_REF)
    vk.col("thoi_gian_bay_toi_tam_s_game", unit="s", meaning="thoi_gian_bay_toi_tam_s: giá trị mã game tính (port Python của "
           + FLIGHT_REF + ")", source_note="port Python của " + FLIGHT_REF)
    vk.col("ngoai_doi_phat_phut_toi_da", unit="phát/phút",
           meaning="nhịp tối đa ngoài đời (bảng REAL của Tools/balance/full_weapon_audit.py)")
    vk.col("ngoai_doi_phat_phut_duy_tri", unit="phát/phút", meaning="nhịp thực tế / duy trì ngoài đời (bảng REAL)")
    vk.col("ngoai_doi_loai", meaning="loại trong bảng REAL (mg, ac, aa, gun, rocket, missile, bomb, drone)")
    vk.col("ngoai_doi_nguon", meaning="nguồn của nhịp ngoài đời (bảng REAL); NEED_SOURCE nếu không có")
    vk.col("ly_do_sua", meaning="lý do sửa nhịp / số (Tools/balance/fix_weapon_reasons.json)")
    B.declare_changes(vk, TRACKED)
    bonus = book.sheet("Vu_khi_he_so_thuong", "Vũ khí: hệ số thưởng", "bonuses[]: hệ số sát thương theo lớp / giáp / điều kiện",
                       parent=vk)

    round_of = {}
    for wid, w in res.items():
        if w.get("roundOf"):
            round_of.setdefault(w["roundOf"], []).append(wid)
    for wid, w, path in B.weapon_entries(ctx):
        r = vk.row(wid, B.nguon(path), raw=w)
        e = res[wid]
        eff = effective(e, tiers)
        for col, val in eff.items():
            r.set(col, val)
        r.set("ke_thua_tu", w.get("inherits", ""))
        alts = [x for x in (e.get("he"), e.get("air")) if isinstance(x, str)] + sorted(round_of.get(wid, []))
        r.set("dan_thay_the", ";".join(alts))
        us = users.get(wid, [])
        r.set("cua_ai", ";".join(sorted({u[0] for u in us})))
        r.set("mang_boi", ";".join(sorted({u[1] for u in us})))
        r.set("so_don_vi_mang", len({u[1] for u in us}))
        r.set("ten_be", ";".join(f"{u[1]}:{u[2]}" for u in sorted(us, key=lambda x: (x[1], str(x[2])))))
        tier = tiers.get(e.get("weaponFamilyId"), -1) if e.get("weaponFamilyId") else -1
        tier = -1 if tier is None else int(tier)
        r.set("thoi_gian_canh_bao_s", G.warn_seconds(e, tier, warn_rules))
        r.set("co_vong_canh_bao", G.warns(e, tier, warn_rules))
        r.set("lech_nong_s", NEED_CODE_CHECK if (eff["so_nong"] or 1) > 1 and eff["che_do_nong"] == "RIPPLE" else "")
        flight = flight_time(e, tier, warn_rules)
        bomb = G.projectile(e) == "Bomb"
        r.set("thoi_gian_bay_toi_tam_s", F(FLIGHT, expect=None if bomb else flight, ref=FLIGHT_REF) if flight is not None else "")
        r.set("thoi_gian_bay_toi_tam_s_game", NEED_CODE_CHECK if bomb and flight is not None else
              (flight if flight is not None else ""))
        name = (e.get("real") or "").lower()
        hit = next((x for x in real if re.search(x[0], name)), None) if name else None
        if hit:
            r.set("ngoai_doi_phat_phut_toi_da", hit[1])
            r.set("ngoai_doi_phat_phut_duy_tri", hit[2] if hit[2] is not None else "")
            r.set("ngoai_doi_loai", hit[3])
            r.set("ngoai_doi_nguon", hit[5])
        else:
            for c in ("ngoai_doi_phat_phut_toi_da", "ngoai_doi_phat_phut_duy_tri", "ngoai_doi_nguon"):
                r.set(c, NEED_SOURCE)
        if wid in reasons:
            r.set("ly_do_sua", reasons[wid], REASONS, (wid,))
        b = base_res.get(wid)
        B.set_changes(r, TRACKED, eff, effective(b, base_tiers) if b else None, base is not None)
        r.flatten(w, B.BALANCE, path, children={
            "bonuses": lambda row, items, src, p: child_rows(bonus, row, items, src, p)})
    for k in sorted(set(reasons) - set(res)):
        ctx.issue(f"{REASONS}: '{k}' is not a weapon id (left unmapped)")

    # ------------------------------------------------------------------ Ho_vu_khi (+ variants)
    ho = book.sheet("Ho_vu_khi", "Họ vũ khí", "weaponFamilyTable: họ, bậc cỡ, số boss chung, biến thể và lý do")
    ho.col("ten", meaning="tên họ")
    ho.col("bac", meaning="bậc cỡ 0-5 (T0-T5)")
    ho.col("boss_sat_thuong", unit="hp", meaning="sát thương chung của họ trên boss")
    ho.col("boss_loi_m", unit="m", meaning="lõi nổ chung trên boss")
    ho.col("boss_ria_m", unit="m", meaning="rìa nổ chung trên boss")
    ho.col("bien_the", meaning="các biến thể (Ho_vu_khi_bien_the)")
    ho.col("so_vu_khi", meaning="số vũ khí thuộc họ (Vu_khi.ho_id)")
    ho.col("vu_khi", meaning="id vũ khí thuộc họ", fk=["01_vu_khi_dan/Vu_khi"])
    var = book.sheet("Ho_vu_khi_bien_the", "Họ vũ khí: biến thể", "variants{}: biến thể của họ và lý do", parent=ho)
    var.col("bien_the", meaning="mã biến thể")
    var.col("ly_do", meaning="lý do biến thể khác họ")
    members = {}
    for wid, e in res.items():
        if e.get("weaponFamilyId"):
            members.setdefault(e["weaponFamilyId"], []).append(wid)
    for i, f in enumerate(d.get("weaponFamilyTable", [])):
        path = ("weaponFamilyTable", i)
        r = ho.row(f["id"], B.nguon(path), raw=f)
        r.set("bien_the", ";".join(sorted((f.get("variants") or {}).keys())))
        ms = sorted(members.get(f["id"], []))
        r.set("so_vu_khi", len(ms))
        r.set("vu_khi", ";".join(ms))
        r.flatten(f, B.BALANCE, path, skip=("variants",),
                  aliases={"name": "ten", "tier": "bac", "boss.damage": "boss_sat_thuong", "boss.core": "boss_loi_m",
                           "boss.edge": "boss_ria_m"})
        for vk_, why in (f.get("variants") or {}).items():
            vr = var.row(f"{f['id']}/{vk_}", B.nguon(path + ("variants", vk_)), raw={vk_: why})
            vr.set(var.parent_col, f["id"])
            vr.set("thu_tu", sorted(f["variants"]).index(vk_))
            vr.set("bien_the", vk_)
            vr.set("ly_do", why, B.BALANCE, path + ("variants", vk_))

    # ------------------------------------------------------------------ Dong_vu_khi (real weapon lines)
    dong = book.sheet("Dong_vu_khi", "Dòng vũ khí thật", "weaponFamilies + secondRounds.families: số chung của một hệ thống thật")
    dong.col("ten_that", meaning="tên hệ thống thật")
    dong.col("khoi_nguon", meaning="weaponFamilies hoặc secondRounds.families")
    dong.col("so_vu_khi", meaning="số vũ khí dùng dòng này")
    users_line = {}
    for wid, e in res.items():
        if isinstance(e.get("weaponFamily"), str) and e["weaponFamily"]:
            users_line.setdefault(e["weaponFamily"], []).append(wid)
    blocks = [(("weaponFamilies",), d.get("weaponFamilies", []), "weaponFamilies"),
              (("secondRounds", "families"), (d.get("secondRounds") or {}).get("families", []), "secondRounds.families")]
    for base_path, items, origin in blocks:
        for i, f in enumerate(items):
            path = base_path + (i,)
            r = dong.row(f["id"], B.nguon(path), raw=f)
            r.set("khoi_nguon", origin)
            r.set("so_vu_khi", len(users_line.get(f["id"], [])))
            r.flatten(f, B.BALANCE, path, aliases={"real": "ten_that"})

    # ------------------------------------------------------------------ Dan_thay_the (links; values read from Vu_khi)
    alt = book.sheet("Dan_thay_the", "Đạn thay thế", "Liên kết vũ khí -> đạn thay thế (he, air, đạn thứ hai roundOf)")
    alt.col("vu_khi_goc", meaning="vũ khí gốc", fk=["01_vu_khi_dan/Vu_khi"])
    alt.col("dan_id", meaning="đạn thay thế (một dòng ở Vu_khi)", fk=["01_vu_khi_dan/Vu_khi"])
    alt.col("lien_ket", meaning="he / air / roundOf", enum=["he", "air", "roundOf"])
    alt.col("loai_dan", meaning="round của đạn thứ hai (ap, he, air...)")
    alt.col("dung_cho", meaning="for: mục tiêu đạn được chọn")
    alt.col("loai_sat_thuong", meaning="loại sát thương của đạn")
    alt.col("xuyen", meaning="mức xuyên của đạn")
    alt.col("sat_thuong_moi_phat", unit="hp", meaning="sát thương mỗi phát của đạn")
    alt.col("loi_m", unit="m", meaning="lõi nổ của đạn")
    alt.col("dieu_kien_tu_doi", meaning="khi nào AI tự đổi đạn (mã)")
    alt.col("thoi_gian_doi_s", unit="s", meaning="thời gian đổi đạn (mã)")
    alt.col("thoi_gian_giu_s", unit="s", meaning="thời gian giữ đạn đã đổi (mã)")
    links = []
    for wid, e in res.items():
        for kind in ("he", "air"):
            if isinstance(e.get(kind), str):
                links.append((wid, e[kind], kind))
        if e.get("roundOf"):
            links.append((e["roundOf"], wid, "roundOf"))
    for gun, rnd, kind in sorted(set(links)):
        e = res.get(rnd, {})
        r = alt.row(f"{gun}/{rnd}", f"{B.BALANCE}: {'secondRounds.rounds' if kind == 'roundOf' else 'weapons'} ({kind})")
        r.set("vu_khi_goc", gun)
        r.set("dan_id", rnd)
        r.set("lien_ket", kind)
        r.set("loai_dan", e.get("round", ""))
        r.set("dung_cho", ";".join(e.get("for", [])) if isinstance(e.get("for"), list) else e.get("for", ""))
        r.set("loai_sat_thuong", e.get("damageType", ""))
        r.set("xuyen", G.pen(e) if e else "")
        r.set("sat_thuong_moi_phat", e.get("damage", ""))
        r.set("loi_m", e.get("splash", 0.0))
        for c in ("dieu_kien_tu_doi", "thoi_gian_doi_s", "thoi_gian_giu_s"):
            r.set(c, NEED_CODE_CHECK)

    # ------------------------------------------------------------------ Bang_sat_thuong / Bang_xuyen_giap
    bst = book.sheet("Bang_sat_thuong", "Bảng sát thương", "damageTable: hệ số theo loại sát thương x mặt đất / máy bay / công trình")
    for c, m in (("mat_dat", "hệ số lên mục tiêu mặt đất"), ("may_bay", "hệ số lên máy bay"), ("cong_trinh", "hệ số lên công trình")):
        bst.col(c, meaning=m)
    dt = d.get("damageTable", {})
    for k, v in dt.items():
        if isinstance(v, dict):
            r = bst.row(k, B.nguon(("damageTable", k)), raw=v)
            r.flatten(v, B.BALANCE, ("damageTable", k), aliases={"Ground": "mat_dat", "Air": "may_bay", "Structure": "cong_trinh"})
    bx = book.sheet("Bang_xuyen_giap", "Bảng xuyên giáp", "damageTable.penetration: hệ số theo chênh xuyên - giáp (DamageTable.cs)")
    bx.col("chenh_xuyen_giap", meaning="mức xuyên trừ mức giáp mặt bị bắn (+2 = vượt hai mức trở lên, -3 = kém ba mức trở lên)")
    bx.col("he_so", meaning="hệ số sát thương")
    for i, v in enumerate(dt.get("penetration", [])):
        r = bx.row(f"buoc_{i}", B.nguon(("damageTable", "penetration", i)), raw=v)
        r.set("chenh_xuyen_giap", PEN_STEPS[i] if i < len(PEN_STEPS) else "")
        r.set("he_so", v, B.BALANCE, ("damageTable", "penetration", i))

    # ------------------------------------------------------------------ He_so_toan_cuc (firepower, thermobaric)
    hs = book.kv_sheet("He_so_toan_cuc", "Hệ số toàn cục", "firepower.* và damageTable.thermobaric: hệ số nhân chung")
    book.kv_rows(hs, d.get("firepower", {}), B.BALANCE, ("firepower",), "firepower", prefix=("firepower",))
    if "thermobaric" in dt:
        book.kv_rows(hs, {"thermobaric": dt["thermobaric"]}, B.BALANCE, ("damageTable",), "damageTable", prefix=("damageTable",))

    # ------------------------------------------------------------------ Khac_che (APS / point defence on units)
    kc = book.sheet("Khac_che", "Khắc chế (APS, phòng thủ điểm)", "Mỗi đơn vị có hệ chặn: số lần, hồi, bán kính, loại đạn chặn")
    kc.col("id", fk=OWNERS)
    kc.col("loai_don_vi", meaning="xe / thap / boss / cong_trinh")
    kc.col("he_phong_ve", meaning="SELF_APS (tự vệ) / POINT_DEFENSE (che vùng); trống: aps = null (biến thể tắt APS)",
           enum=["SELF_APS", "POINT_DEFENSE"])
    for m in MUNITIONS:
        kc.col(f"chan_{m}", meaning=f"chặn được {m}: tỷ lệ / có-không (luật trong mã)")
    # ------------------------------------------------------------------ Phao_sang (flares)
    ps = book.sheet("Phao_sang", "Pháo sáng", "Mỗi đơn vị có pháo sáng: số lần, hồi, điểm phát Mount_Flare")
    ps.col("id", fk=OWNERS)
    ps.col("loai_don_vi", meaning="xe / thap / boss / cong_trinh")
    ps.col("mo_hinh", meaning="model GLB của đơn vị (Resources/Models)")
    ps.col("so_mount_flare", meaning="số nút Mount_Flare trong GLB (đọc từ model, chỉ để xem)")
    ps.col("so_qua_moi_lan", meaning="số quả hình ảnh mỗi lần thả (munitionRules.flareRelease theo lớp; lớp chọn trong mã)")
    ps.col("do_nang_cap", meaning="đồ nâng cấp liên quan (02/Trang_bi_mo_dun)")
    B.declare_changes(ps, ["flare_charges", "flare_recharge_s"])
    res_v = B.resolved_vehicles(ctx)
    base_v = B.resolved_vehicles(base) if base else {}
    for vid, v, path in B.vehicle_entries(ctx):
        kind = B.KIND_VI[B.classify(ctx, vid)]
        if any(k in v for k in ("aps", "apsCapability", "interceptionMode")):
            r = kc.row(vid, B.nguon(path), raw={k: v[k] for k in ("aps", "apsCapability", "interceptionMode") if k in v})
            r.set("loai_don_vi", kind)
            ra = res_v[vid].get("aps", False)
            r.set("he_phong_ve", "" if ra is None else "POINT_DEFENSE" if res_v[vid].get("interceptionMode") == "PointDefense" or
                  (isinstance(ra, dict) and ra.get("rockets") and kind != "xe") else "SELF_APS")
            for m in MUNITIONS:
                r.set(f"chan_{m}", NEED_CODE_CHECK)
            r.flatten({k: v[k] for k in ("aps", "apsCapability", "interceptionMode") if k in v}, B.BALANCE, path)
        if any(k in v for k in ("flares", "flareCharges", "flareRecharge")):
            sub = {k: v[k] for k in ("flares", "flareCharges", "flareRecharge") if k in v}
            r = ps.row(vid, B.nguon(path), raw=sub)
            r.set("loai_don_vi", kind)
            model = res_v[vid].get("model") or vid
            r.set("mo_hinh", model)
            glb = ctx.sources.get(f"Assets/MachineBrigade/Resources/Models/{model}.glb")
            if glb is not None and glb.readable:
                r.set("so_mount_flare", sum(1 for n in glb.data["nodes"] if re.match(r"^Mount_Flare(\.\d+)?$", n, re.I)))
            else:
                r.set("so_mount_flare", "")
            r.set("so_qua_moi_lan", NEED_CODE_CHECK)
            r.set("do_nang_cap", "FlareDispenser (02_phuong_tien/Trang_bi_mo_dun)")
            cur = {"flare_charges": res_v[vid].get("flareCharges"), "flare_recharge_s": res_v[vid].get("flareRecharge")}
            bv = base_v.get(vid)
            B.set_changes(r, ["flare_charges", "flare_recharge_s"], cur,
                          {"flare_charges": bv.get("flareCharges"), "flare_recharge_s": bv.get("flareRecharge")} if bv else None,
                          base is not None)
            r.flatten(sub, B.BALANCE, path)

    # ------------------------------------------------------------------ Hanh_vi_dan (rules + per projectile kind)
    hv = book.kv_sheet("Hanh_vi_dan", "Hành vi đạn: luật chung", "munitionRules: pháo sáng mồi, ngòi cận đích, dẫn đường")
    book.kv_rows(hv, d.get("munitionRules", {}), B.BALANCE, ("munitionRules",), "munitionRules",
                 units={"flareOffset": "m", "proximityFuze": "m", "flareBurn": "s"})
    hn = book.sheet("Hanh_vi_dan_nhom", "Hành vi đạn theo nhóm", "Mỗi dạng đạn (projectile): cách nhắm, khi nổ, cảnh báo (luật trong mã)")
    for c, m in (("so_vu_khi", "số vũ khí dùng dạng đạn này (giá trị game)"), ("cach_nham", "cách nhắm"),
                 ("khi_no", "khi nào nổ"), ("khi_truot", "khi nào trượt"), ("co_canh_bao", "có cảnh báo không"),
                 ("thoi_gian_bay_toi_da_s", "thời gian bay tối đa"), ("tuong_tac_phao_sang", "tương tác pháo sáng"),
                 ("tuong_tac_aps", "tương tác APS"), ("tuong_tac_gay_nhieu", "tương tác gây nhiễu")):
        hn.col(c, meaning=m, unit="s" if c.endswith("_s") else "")
    kinds = {}
    for wid, e in res.items():
        kinds.setdefault(e.get("projectile", "Shell"), []).append(wid)
    for k in sorted(kinds):
        r = hn.row(k, f"{B.BALANCE}: weapons[*].projectile (giá trị game, mặc định Shell)")
        r.set("so_vu_khi", len(kinds[k]))
        for c in ("cach_nham", "khi_no", "khi_truot", "co_canh_bao", "thoi_gian_bay_toi_da_s", "tuong_tac_phao_sang",
                  "tuong_tac_aps", "tuong_tac_gay_nhieu"):
            r.set(c, NEED_CODE_CHECK)

    _drone_sheet(book, d, res, users)
    _ten_lua_sheet(book, d, res, users, tiers)

    # ------------------------------------------------------------------ Canh_bao_vong
    cb = book.kv_sheet("Canh_bao_vong", "Vòng cảnh báo", "warningRules: loại đòn có vòng, sàn thời gian theo bậc, số vùng tối đa")
    book.kv_rows(cb, d.get("warningRules", {}), B.BALANCE, ("warningRules",), "warningRules",
                 units={"gunMinMm": "mm", "bombMinKg": "kg", "rocketMinMm": "mm", "floorT4": "s", "floor406": "s",
                        "floorT5": "s", "base": "s", "escapeSpeed": "m/s", "cap": "s", "maxShown": "",
                        "salvoMergeSeconds": "s", "fadeIn": "s"})
    _bom_link(ctx, book, res, users)
    _b01.build(ctx, book, d, res, tiers, warn_rules)
    _unit_settle.apply(book)
    ctx.note("01_canh_bao", "Canh_bao_vong.cap đọc là giây (trần thời gian cảnh báo) và base là giây: suy từ tên khóa; "
             "công thức thời gian cảnh báo nằm trong mã (Vu_khi.thoi_gian_canh_bao_s = NEED_CODE_CHECK).")
