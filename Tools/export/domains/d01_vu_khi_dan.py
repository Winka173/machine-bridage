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
from . import _b01

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


def real_rates():
    """The REAL table of Tools/balance/full_weapon_audit.py (pattern on the real name, max rpm, practical rpm, kind,
    mount, source), read as a literal (the module is not run)."""
    tree = ast.parse((ROOT / AUDIT).read_text("utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "REAL" for t in node.targets):
            return ast.literal_eval(node.value)
    return []


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
    vk.col("thoi_gian_bay_toi_tam_s", unit="s", meaning="tầm / tốc độ đạn (lớp B: công thức sống; CombatSystem.cs bay "
           "khoảng cách / projectileSpeed, bom và MRSI riêng)", formula="={tam_m}/{toc_do_dan_m_s}")
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
        flight = (G.f(e, "range") / G.f(e, "projectileSpeed")) if G.f(e, "projectileSpeed") > 0 else None
        r.set("thoi_gian_bay_toi_tam_s", F("={tam_m}/{toc_do_dan_m_s}", expect=flight, ref="python: tam_m / toc_do_dan_m_s")
              if flight is not None else "")
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

    # ------------------------------------------------------------------ Canh_bao_vong
    cb = book.kv_sheet("Canh_bao_vong", "Vòng cảnh báo", "warningRules: loại đòn có vòng, sàn thời gian theo bậc, số vùng tối đa")
    book.kv_rows(cb, d.get("warningRules", {}), B.BALANCE, ("warningRules",), "warningRules",
                 units={"gunMinMm": "mm", "bombMinKg": "kg", "rocketMinMm": "mm", "floorT4": "s", "floor406": "s",
                        "floorT5": "s", "base": "s", "escapeSpeed": "m/s", "cap": "s", "maxShown": "",
                        "salvoMergeSeconds": "s", "fadeIn": "s"})
    _b01.build(ctx, book, d, res, tiers, warn_rules)
    ctx.note("01_canh_bao", "Canh_bao_vong.cap đọc là giây (trần thời gian cảnh báo) và base là giây: suy từ tên khóa; "
             "công thức thời gian cảnh báo nằm trong mã (Vu_khi.thoi_gian_canh_bao_s = NEED_CODE_CHECK).")
