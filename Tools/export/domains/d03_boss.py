"""03_boss, layer A: bosses (main and mini, variants), their mounts as built, parts, phases, the parts library, frames,
ranks, super weapons, escorts, Boss Hunt (order and combat supports)."""
from __future__ import annotations

from core.model import NEED_CODE_CHECK, chua_ap, child_rows

from . import _b03, _unit_settle
from . import _balance as B
from . import _units as U

FILE_ID = "03_boss"
TITLE = "Boss"
DESC = "Boss chủ lực / mini và biến thể, bệ vũ khí (đã dựng), bộ phận, pha, khung, hạng, siêu vũ khí, hộ tống, Săn trùm"

HUNT = "Assets/MachineBrigade/Scripts/Sim/Modes/BossHunt.cs"
HUNTS = "Assets/MachineBrigade/Scripts/Game/Match/BossHunts.cs"
BOSS_FK = ["03_boss/Boss"]
VEHICLE_FK = ["02_phuong_tien/Xe"]
LAYER_B = chua_ap("xuat_luot5")


def _chapters(ctx):
    camp = ctx.data(B.CAMPAIGN) if B.CAMPAIGN in ctx.sources else {}
    of, order = {}, []
    for ch in camp.get("chapters", []):
        for bid in list(ch.get("minis", [])) + ([ch["main"]] if ch.get("main") else []):
            of.setdefault(bid, []).append(ch.get("number"))
            if bid not in order:
                order.append(bid)
    missions = {}
    for m in camp.get("missions", []):
        b = m.get("boss")
        if isinstance(b, dict) and b.get("def"):
            missions.setdefault(b["def"], []).append(m["id"])
    return of, order, missions


# Boss_tam_toi_thieu (balance pack 2, section 5.1 + addendum item 1c): column, unit, meaning
MIN_RANGE_COLS = (
    ("boss_id", "", "boss"), ("vu_khi_id", "", "vũ khí trên bệ"),
    ("bo_phan_id", "", "bộ phận mang bệ (parts[].mounts; trống: bệ không thuộc bộ phận nào)"),
    ("chi_so_be", "", "0 = vũ khí chính, k = secondary[k-1]"), ("slot", "", "loại bệ"), ("aim", "", "cách nhắm của bệ"),
    ("lop_vu_khi", "", "lớp để lấy góc nòng mặc định (balance.json barrelLimits.classes, sheet Boss_goc_nong): phao_boss, "
     "phao_ham, sung_phu, phao_nho_ciws, sung_may, phun_lua, be_rocket (không hạ), ban_cau (bắn cầu), may_bay; ten_lua, drone, "
     "bom, can_chien, phong_khong (chỉ bắn máy bay) không dùng góc nòng"),
    ("nhom", "", "chinh (nòng chính, định vùng chết) / phong_thu_gan (không áp tầm tối thiểu) / dan_dan (tên lửa, drone, bom: "
     "lái hoặc rơi xuống chân) / phong_khong"),
    ("nut_glb", "", "nút Muzzle_* / Mount_* của bệ trong GLB (VehicleView: bệ thứ k của một slot = nút thứ k theo tên)"),
    ("cach_tim_nut", "", "muzzle / mount (nút GLB) / bo_phan (không có nút: độ cao bộ phận trong dữ liệu) / thay_the "
     "(Muzzle_main hoặc Turret) / hop_bao (0,75 x chiều cao)"),
    ("model", "", "model GLB (Resources/Models, sau vẽ lại)"),
    ("ti_le_ve", "", "tỉ lệ vẽ (VehicleView.DrawScaleOf: modelSize hoặc scale sau BossTemplates.Resize)"),
    ("he_so_size", "", "hệ số size của boss (BossTemplates.Resize: nhân scale, bán kính, vị trí bộ phận; biến thể: size cha x variant.size)"),
    ("do_cao_nong_m", "m", "độ cao đầu nòng so với mặt đất: nút GLB x tỉ lệ vẽ (máy bay cộng độ cao bay); không có nút: độ cao "
     "bộ phận trong dữ liệu"),
    ("do_cao_be_du_lieu_m", "m", "độ cao bộ phận mang bệ trong dữ liệu = at_z_m ở Boss_bo_phan (at = [phải, trước, cao] trong "
     "khung boss, BossDefs.At / Height: at_y_m là phía trước, không phải độ cao) + độ cao gốc (0 trên đất / nước, máy bay "
     "cộng độ cao bay)"),
    ("lech_glb_du_lieu_m", "m", "do_cao_nong_m - do_cao_be_du_lieu_m (kiểm: điểm trúng của bộ phận so với nòng đã vẽ lại)"),
    ("do_cao_boss_m", "m", "độ cao boss (đỉnh model, máy bay cộng độ cao bay)"),
    ("khoang_cach_ngang_tu_tam_boss_den_nong_m", "m", "khoảng cách ngang từ tâm boss tới đầu nòng (tư thế nghỉ)"),
    ("nut_be_xoay", "", "trục xoay của bệ (Mount_* / Turret tổ tiên gần nhất của nòng; trống: gắn cố định)"),
    ("khoang_cach_ngang_tu_tam_boss_den_be_m", "m", "khoảng cách ngang từ tâm boss tới trục xoay"),
    ("khoang_cach_ngang_theo_huong_ngam_m", "m", "phần khoảng cách nằm theo hướng ngắm: trục xoay -> đầu nòng (bệ Hull: phần "
     "về phía trước); phần lệch của trục xoay đổi dấu theo hướng nên lấy trung bình 0"),
    ("ban_kinh_than_boss_m", "m", "bán kính thân boss (radius trong mô phỏng)"), ("do_cao_bay_m", "m", "độ cao bay (máy bay)"),
    ("goc_ha_nong_toi_da_deg", "deg", "góc hạ nòng tối đa (barrelLimits)"),
    ("goc_nang_toi_da_deg", "deg", "góc nâng nòng tối đa (barrelLimits)"),
    ("goc_nang_toi_thieu_deg", "deg", "góc nâng tối thiểu (bắn cầu; barrelLimits)"),
    ("goc_quay_ngang_deg", "deg", "góc quay ngang (360: quay tròn; bệ có arc: 2 x nửa cung)"),
    ("nguon_goc_nong", "", "nguồn góc nòng: lop:<lớp> / ho:<họ vũ khí> / vu_khi / be (barrel riêng) / missileArmingM / khong_ap"),
    ("uoc_dinh", "", "true: góc nòng (hoặc khoảng vũ trang) là mặc định ước định, chưa có số thật (mục 5.2)"),
    ("tam_toi_thieu_m_hien_tai", "m", "tầm tối thiểu đang ghi ở Vu_khi cho trường dùng (minRange với vũ khí bắn cầu, "
     "groundMinReach với bắn thẳng)"),
    ("tam_toi_thieu_m", "m", "minRange hiện có (đo tới tâm mục tiêu; > 0 làm vũ khí thành bắn cầu)"),
    ("tam_toi_thieu_mep_m", "m", "tầm tối thiểu đo tới mép mục tiêu, chỉ mục tiêu mặt đất (groundMinReach; minReach nếu lớn hơn)"),
    ("tam_toi_da_m", "m", "tầm tối đa"),
    ("toc_do_dau_nong_m_s", "m/s", "tốc độ đạn trong dữ liệu (projectileSpeed: nhịp bay của game, không phải sơ tốc đạn đạo)"),
    ("toc_do_dan_dao_game_m_s", "m/s", "tốc độ đạn đạo dùng trong công thức: sqrt(g x tầm tối đa)"),
    ("khoang_cach_vu_trang_m", "m", "khoảng cách vũ trang tên lửa (barrelLimits.missileArmingM, ước định)"),
    ("do_cao_tam_muc_tieu_m", "m", "độ cao tâm mục tiêu tham chiếu (xe tăng 1,3 m; barrelLimits.targetCentreHeightM)"),
    ("cong_thuc", "", "ban_thang / roi_tu_do_be_co_dinh / v2_sin2theta_g / max(vu_trang, khoa) / ban_thang_may_bay / khong_ap"),
    ("tam_toi_thieu_hinh_hoc_tu_nong_m", "m", "công thức bổ sung 1c tính từ đầu nòng: max(0, (do_cao_nong_m - "
     "do_cao_tam_muc_tieu_m) / tan(goc_ha_nong_toi_da_deg))"),
    ("tam_toi_thieu_hinh_hoc_m", "m", "tầm tối thiểu theo hình học từ tâm boss (công thức trên + phần theo hướng ngắm; mục tiêu xe tăng)"),
    ("tam_toi_thieu_hinh_hoc_xe_nhe_m", "m", "như trên, mục tiêu xe nhẹ (1,0 m)"),
    ("tam_toi_thieu_hinh_hoc_hang_nang_m", "m", "như trên, mục tiêu hạng nặng (1,6 m)"),
    ("tam_toi_thieu_de_xuat_m", "m", "đề xuất = max(hiện tại, hình học), làm tròn nửa lên 1 m; cắt còn capShare (80 %) tầm nếu "
     "chạm tầm; vũ khí không áp: giữ hiện tại"),
    ("ap_dung", "", "true: đề xuất ghi vào vũ khí; false: phòng thủ gần (súng máy, phun lửa, cao xạ nhỏ / CIWS, cận chiến), "
     "chỉ bắn máy bay hoặc bom"),
    ("truong_ghi", "", "trường ghi vào vũ khí: groundMinReach (bắn thẳng: đo tới mép, chỉ mục tiêu mặt đất, không đổi vai pháo "
     "binh) / minRange (vũ khí đã bắn cầu) / khong_ap"),
    ("cat_theo_tam", "", "true: hình học vượt tầm, đã cắt còn 80 % tầm"),
    ("tam_toi_thieu_ghi_m", "m", "giá trị game dùng (một vũ khí dùng ở nhiều bệ lấy đề xuất nhỏ nhất)"),
    ("vung_chet_ban_kinh_m", "m", "bán kính vùng chết của boss: nhỏ nhất của tầm tối thiểu các nòng chính (từ tâm boss)"),
    ("vu_khi_che_vung_chet", "", "vũ khí bắn được vào vùng chết"),
    ("phan_tram_vung_chet_duoc_phu", "%", "phần dải chết (từ mép thân tới bán kính vùng chết) có vũ khí phủ"),
    ("co_che_vung_chet", "", "true: phủ ít nhất coverShare (90 %) dải chết (hoặc dải chết dưới negligibleBandM, 2 m)"),
)

BARREL_UNITS = {"depressionDeg": "deg", "elevationMinDeg": "deg", "elevationMaxDeg": "deg", "secondaryGunBelowMm": "mm",
                "navalSecondaryGunBelowMm": "mm", "smallAutocannonMaxMm": "mm", "xe_nhe": "m", "xe_tang": "m", "hang_nang": "m",
                "missileArmingM": "m", "largeBandM": "m", "negligibleBandM": "m", "capShare": "", "coverShare": "",
                "estimated": ""}


def _min_range_sheet(book, d, built, wres):
    """Boss_tam_toi_thieu: section 5 and addendum item 1 of Docs/prompts/export_pack2_vi.txt, computed by
    Tools/export/boss_min_range.py; Boss_goc_nong: the barrel limits it reads (balance.json barrelLimits)."""
    import boss_min_range as BMR
    res = BMR.compute(d, built, wres)
    sh = book.sheet("Boss_tam_toi_thieu", "Boss: tầm tối thiểu", "Mỗi bệ của mỗi boss một dòng: độ cao nòng từ GLB (vẽ lại) và "
                    "dữ liệu, góc nòng (barrelLimits), tầm tối thiểu theo hình học, đề xuất, vùng chết và vũ khí phủ "
                    "(Tools/export/boss_min_range.py)")
    fks = {"boss_id": BOSS_FK, "vu_khi_id": ["01_vu_khi_dan/Vu_khi"]}
    for c, unit, m in MIN_RANGE_COLS:
        sh.col(c, unit=unit, meaning=m, fk=fks.get(c))
    for r in res["rows"]:
        row = sh.row(f"{r['boss_id']}/{r['chi_so_be']}", f"{B.BALANCE}: vehicles[id={r['boss_id']}] x Resources/Models/{r['model']}.glb")
        for c, _unit, _m in MIN_RANGE_COLS:
            row.set(c, r.get(c, ""))
    gn = book.kv_sheet("Boss_goc_nong", "Boss: góc nòng", "barrelLimits: góc hạ / nâng nòng theo lớp và họ vũ khí (estimated = "
                       "uoc_dinh), luật xếp lớp, độ cao mục tiêu tham chiếu; đọc bởi Tools/export/boss_min_range.py")
    book.kv_rows(gn, d.get("barrelLimits") or {}, B.BALANCE, ("barrelLimits",), "barrelLimits", units=BARREL_UNITS)


def build(ctx):
    book = ctx.book(FILE_ID, TITLE, DESC)
    d = B.bal(ctx)
    built = B.boss_built(ctx)
    base = B.base_view(ctx)
    base_built = B.boss_built(base) if base else {}
    wres = B.resolved_weapons(ctx)
    base_w = B.resolved_weapons(base) if base else {}
    attacks = {a["id"]: a for a in d.get("bigAttacks", [])}
    frames = d.get("bossFrames") or {}
    escorts = {e.get("boss") for e in d.get("escorts", [])}
    ch_of, _order, missions = _chapters(ctx)

    # ------------------------------------------------------------------ Boss (+ raw children)
    bs = book.sheet("Boss", "Boss", "Mỗi boss (41: chủ lực, mini, biến thể) một dòng: giá trị game (đã dựng) và trường gốc")
    bs.col("phan_loai", meaning="main (chủ lực) / mini", enum=["main", "mini"])
    U.declare(bs)
    for c, m, fk in (("khung", "khung di chuyển (frame)", ["03_boss/Boss_khung"]),
                     ("kieu_duong_di", "kiểu đường đi: đất / biển / ray / không (bossFrames[frame].move)", None),
                     ("tuong", "tướng địch sở hữu (general)", None),
                     ("bien_the_cua", "boss gốc của biến thể (variantOf)", BOSS_FK),
                     ("so_be", "số bệ vũ khí khi dựng (1 + secondary)", None),
                     ("so_nong", "tổng số nòng trên mọi bệ (barrels của vũ khí)", None),
                     ("sieu_vu_khi", "siêu vũ khí (bigAttack)", ["03_boss/Boss_sieu_vu_khi"]),
                     ("sieu_vu_khi_chu_ky_s", "chu kỳ siêu vũ khí (bigAttacks.cooldown)", None),
                     ("sieu_vu_khi_cach_nham", "cách nhắm siêu vũ khí (bigAttacks.aim)", None),
                     ("ho_tong", "có đội hộ tống riêng (escorts[].boss)", None),
                     ("chuong", "chương có boss (campaign chapters main / minis)", None),
                     ("nhiem_vu", "nhiệm vụ có boss (campaign missions[].boss.def)", None),
                     ("thoi_gian_ha_muc_tieu_s", "thời gian hạ mục tiêu thiết kế (tính trong mã / bảng cân bằng)", None)):
        bs.col(c, meaning=m, fk=fk, unit="s" if c.endswith("_s") else "")
    raw_mounts = U.mounts_child("Boss_be_goc", "Boss: bệ phụ gốc", book, bs)
    parts = book.sheet("Boss_bo_phan", "Boss: bộ phận", "parts[]: bộ phận phá được (use = mẫu ở Boss_bo_phan_thu_vien)", parent=bs)
    parts.col("use", meaning="mẫu bộ phận", fk=["03_boss/Boss_bo_phan_thu_vien"])
    phases = book.sheet("Boss_phase", "Boss: pha", "phases[]: ngưỡng máu, biến hình, đổi vũ khí / sát thương", parent=bs)
    tune = book.sheet("Boss_bien_the_chinh", "Boss: chỉnh bộ phận của biến thể", "variant.tune: bộ phận -> trường đổi", parent=bs)
    fleet = book.sheet("Boss_ham_doi", "Boss: hạm đội đi kèm", "fleet[]", parent=bs)
    fleet.col("unit", meaning="đơn vị", fk=VEHICLE_FK)
    for vid, v, path in B.vehicle_entries(ctx):
        if B.classify(ctx, vid) != "boss":
            continue
        b = built.get(vid, v)
        r = bs.row(vid, B.nguon(path), raw=v)
        r.set("phan_loai", b.get("rank", "main"))
        U.fill(ctx, r, vid, b, boss=True, base_record=base_built.get(vid), has_base=base is not None)
        frame = b.get("frame", "")
        r.set("khung", frame)
        r.set("kieu_duong_di", (frames.get(frame) or {}).get("move", ""))
        r.set("tuong", b.get("general", ""))
        r.set("bien_the_cua", v.get("variantOf", ""))
        mounts = [b.get("weapon")] + [m.get("weapon") for m in b.get("secondary") or []]
        r.set("so_be", len(mounts))
        r.set("so_nong", sum(int(wres.get(w, {}).get("barrels", 1) or 1) for w in mounts if w))
        att = attacks.get(b.get("bigAttack"))
        r.set("sieu_vu_khi", b.get("bigAttack", ""))
        r.set("sieu_vu_khi_chu_ky_s", att.get("cooldown", "") if att else "")
        r.set("sieu_vu_khi_cach_nham", att.get("aim", "") if att else "")
        r.set("ho_tong", vid in escorts)
        r.set("chuong", ";".join(str(c) for c in ch_of.get(vid, [])))
        r.set("nhiem_vu", ";".join(sorted(missions.get(vid, []))))
        r.set("thoi_gian_ha_muc_tieu_s", NEED_CODE_CHECK)

        def variant_cb(row, val, src, p):
            row.flatten({k: x for k, x in val.items() if k != "tune"}, src, p, prefix="variant_",
                        vectors={"tint": ["r", "g", "b"]})
            for j, (part_id, fields) in enumerate((val.get("tune") or {}).items()):
                tr = tune.row(f"{row.id}/{part_id}", f"{src}: {'.'.join(str(x) for x in p)}.tune.{part_id}", raw=fields)
                tr.set(tune.parent_col, row.id)
                tr.set("thu_tu", j)
                tr.set("bo_phan", part_id)
                tr.flatten(fields, src, p + ("tune", part_id), vectors={"at": ["x_m", "y_m", "z_m"]})
            if "tune" in val and not val["tune"]:
                row.set("variant_tune", "", src, p + ("tune",))

        U.raw(r, v, path, children={
            "secondary": U.child(raw_mounts),
            "parts": lambda row, items, src, p: child_rows(parts, row, items, src, p, vectors={"at": ["x_m", "y_m", "z_m"]}),
            "phases": lambda row, items, src, p: child_rows(phases, row, items, src, p),
            "fleet": lambda row, items, src, p: child_rows(fleet, row, items, src, p),
            "variant": variant_cb,
        }, extra_skip=())

    # ------------------------------------------------------------------ Boss_vu_khi (mounts as built)
    bv = book.sheet("Boss_vu_khi", "Boss: vũ khí theo bệ", "Mỗi bệ của boss khi dựng (thư viện bộ phận, mountWeapons, biến thể): "
                    "một dòng; số lấy từ 01/Vu_khi (giá trị game)")
    for c, unit, m, fk in (
            ("boss_id", "", "boss", BOSS_FK), ("chi_so_be", "", "0 = vũ khí chính, k = secondary[k-1]", None),
            ("vu_khi", "", "vũ khí trên bệ", ["01_vu_khi_dan/Vu_khi"]), ("slot", "", "loại bệ (gun / mg / missile...)", None),
            ("aim", "", "cách nhắm của bệ (Free / Hull...)", None), ("bo_phan", "", "bộ phận mang bệ (parts[].mounts)", None),
            ("so_nong", "", "số nòng của vũ khí", None), ("sat_thuong_moi_phat", "hp", "sát thương mỗi phát (vũ khí, trước hệ số boss)", None),
            ("thoi_gian_nap_s", "s", "thời gian nạp", None), ("loi_m", "m", "lõi nổ", None),
            ("ria_tren_boss_m", "m", "rìa nổ trên boss (port Catalog.cs WithEdge: rìa = min(20, 2 x lõi) trừ khi đã có rìa, "
             "lõi < 2 m, tia, flak, chỉ bắn máy bay)", None),
            ("canh_bao_s", "s", "thời gian cảnh báo (port WeaponDef.WarnSeconds; WithEdge không đổi lõi)", None),
            ("chu_ky_day_du_s", "s", "chu kỳ đầy đủ (lớp B)", None)):
        bv.col(c, unit=unit, meaning=m, fk=fk)
    B.declare_changes(bv, ["vu_khi"])
    for bid in sorted(built):
        b = built[bid]
        mounts = [(b.get("weapon"), {"slot": b.get("mainSlot", "main"), "aim": b.get("mainAim", "")})] + \
                 [(m.get("weapon"), m) for m in b.get("secondary") or []]
        part_of = {}
        for p in b.get("parts") or []:
            for m in p.get("mounts", []) or []:
                part_of.setdefault(int(m), []).append(p.get("id", ""))
        bb = base_built.get(bid)
        base_mounts = ([bb.get("weapon")] + [m.get("weapon") for m in bb.get("secondary") or []]) if bb else None
        for k, (wid, m) in enumerate(mounts):
            w = wres.get(wid, {})
            r = bv.row(f"{bid}/{k}", f"{B.BALANCE}: vehicles[id={bid}] dựng bởi Tools/balance/p26_ab.expand")
            r.set("boss_id", bid)
            r.set("chi_so_be", k)
            r.set("vu_khi", wid or "")
            r.set("slot", m.get("slot", ""))
            r.set("aim", m.get("aim", ""))
            r.set("bo_phan", ";".join(part_of.get(k, [])))
            r.set("so_nong", w.get("barrels", 1) if w else "")
            r.set("sat_thuong_moi_phat", w.get("damage", "") if w else "")
            r.set("thoi_gian_nap_s", w.get("cooldown", "") if w else "")
            r.set("loi_m", w.get("splash", 0.0) if w else "")
            # ria_tren_boss_m, canh_bao_s, chu_ky_day_du_s, dps_duy_tri: layer B (_b03, pass 5)
            if base is not None:
                if base_mounts is None:
                    r.set("so_voi_ban_goc", "moi")
                else:
                    old = base_mounts[k] if k < len(base_mounts) else None
                    B.set_changes(r, ["vu_khi"], {"vu_khi": wid or ""}, {"vu_khi": old or ""} if k < len(base_mounts) else None, True)

    _min_range_sheet(book, d, built, wres)

    # ------------------------------------------------------------------ library parts, frames, ranks
    lib = book.sheet("Boss_bo_phan_thu_vien", "Thư viện bộ phận boss", "bossParts: mẫu bộ phận (máu theo phần, giáp, vũ khí, xác)")
    lib.col("weapon", meaning="vũ khí của bộ phận", fk=["01_vu_khi_dan/Vu_khi"])
    for pid, p in (d.get("bossParts") or {}).items():
        path = ("bossParts", pid)
        r = lib.row(pid, B.nguon(path), raw=p)
        r.flatten(p, B.BALANCE, path, vectors={"arc": ["center_deg", "half_deg"]})
    fr = book.sheet("Boss_khung", "Khung boss", "bossFrames: kiểu di chuyển và trường mặc định theo khung")
    for fid, f in frames.items():
        path = ("bossFrames", fid)
        r = fr.row(fid, B.nguon(path), raw=f)
        r.flatten(f, B.BALANCE, path)
    rk = book.kv_sheet("Boss_hang", "Hạng boss", "bossRanks: main / mini: hệ số sát thương, nhịp, máu, pha, thưởng")
    book.kv_rows(rk, d.get("bossRanks") or {}, B.BALANCE, ("bossRanks",), "bossRanks")

    # ------------------------------------------------------------------ super weapons
    sv = book.sheet("Boss_sieu_vu_khi", "Siêu vũ khí", "bigAttacks: cảnh báo, chu kỳ, cách nhắm, tầm, mục tiêu")
    sv.col("dung_boi", meaning="boss / công trình dùng (bigAttack)")
    strikes = book.sheet("Boss_sieu_vu_khi_don", "Siêu vũ khí: đòn", "strikes[]: hình, số lượng, sát thương, bán kính", parent=sv)
    strikes.col("weapon", meaning="vũ khí bắn đòn", fk=["01_vu_khi_dan/Vu_khi"])
    who = {}
    for vid, rr in B.resolved_vehicles(ctx).items():
        rec = built.get(vid, rr)
        if rec.get("bigAttack"):
            who.setdefault(rec["bigAttack"], set()).add(vid)
    hq_types = ((d.get("base") or {}).get("hqTypes") or {})
    for k, t in hq_types.items():
        if isinstance(t, dict) and t.get("barrage"):
            who.setdefault(t["barrage"], set()).add(f"hqTypes.{k}")
    for i, a in enumerate(d.get("bigAttacks", [])):
        path = ("bigAttacks", i)
        r = sv.row(a["id"], B.nguon(path), raw=a)
        r.set("dung_boi", ";".join(sorted(who.get(a["id"], []))))
        r.flatten(a, B.BALANCE, path, children={
            "strikes": lambda row, items, src, p: child_rows(strikes, row, items, src, p)})
    sl = book.kv_sheet("Boss_sieu_vu_khi_luat", "Siêu vũ khí: luật", "bigAttackRules: lần đầu, chặn, né, theo độ khó")
    book.kv_rows(sl, d.get("bigAttackRules") or {}, B.BALANCE, ("bigAttackRules",), "bigAttackRules")

    # ------------------------------------------------------------------ escorts
    ht = book.sheet("Boss_ho_tong", "Hộ tống boss", "escorts[]: đội đến cùng boss và đội gọi thêm ở pha sau")
    ht.col("boss", meaning="boss", fk=BOSS_FK)
    arrive = book.sheet("Boss_ho_tong_den", "Hộ tống: đến cùng boss", "escorts[].arrive[]", parent=ht)
    arrive.col("unit", meaning="đơn vị", fk=VEHICLE_FK)
    phase_u = book.sheet("Boss_ho_tong_pha", "Hộ tống: gọi ở pha sau", "escorts[].phase.units[]", parent=ht)
    phase_u.col("unit", meaning="đơn vị", fk=VEHICLE_FK)
    for i, e in enumerate(d.get("escorts", [])):
        path = ("escorts", i)
        r = ht.row(e.get("boss", str(i)), B.nguon(path), raw=e)
        r.flatten(e, B.BALANCE, path, children={
            "arrive": lambda row, items, src, p: child_rows(arrive, row, items, src, p),
            "phase.units": lambda row, items, src, p: child_rows(phase_u, row, items, src, p)})
    hm = book.sheet("Boss_ho_tong_mau", "Hộ tống mẫu theo tướng", "escortTemplates: đội hộ tống mặc định của mỗi tướng")
    hm_a = book.sheet("Boss_ho_tong_mau_den", "Hộ tống mẫu: đến", "escortTemplates.*.arrive[]", parent=hm)
    hm_a.col("unit", meaning="đơn vị", fk=VEHICLE_FK)
    hm_p = book.sheet("Boss_ho_tong_mau_pha", "Hộ tống mẫu: pha sau", "escortTemplates.*.phase[]", parent=hm)
    hm_p.col("unit", meaning="đơn vị", fk=VEHICLE_FK)
    for gen, t in (d.get("escortTemplates") or {}).items():
        path = ("escortTemplates", gen)
        r = hm.row(gen, B.nguon(path), raw=t)
        r.flatten(t, B.BALANCE, path, children={
            "arrive": lambda row, items, src, p: child_rows(hm_a, row, items, src, p),
            "phase": lambda row, items, src, p: child_rows(hm_p, row, items, src, p)})
    hl = book.kv_sheet("Boss_ho_tong_luat", "Hộ tống: luật", "escortRules: trần theo độ khó, Săn trùm, dây buộc, thưởng")
    book.kv_rows(hl, d.get("escortRules") or {}, B.BALANCE, ("escortRules",), "escortRules")

    # ------------------------------------------------------------------ Sanhunt (Boss Hunt): port of BossHunts.Story
    sid_u, unslotted, u_lines = ctx.cs_table(HUNTS, "Unslotted")
    camp = ctx.data(B.CAMPAIGN) if B.CAMPAIGN in ctx.sources else {}
    listed = {x for ch in camp.get("chapters", []) for x in list(ch.get("minis", [])) + [ch.get("main")]}
    story, seen = [], set()
    for ch in camp.get("chapters", []):  # data order: the story order with the interludes (Campaign.Chapters)
        slots = list(ch.get("minis", [])) + ([ch["main"]] if ch.get("main") else [])

        def add(bid, chapter=ch):
            b = built.get(bid)
            if bid not in slots or b is None or bid in seen:
                return
            if (frames.get(b.get("frame", "")) or {}).get("move") == "rail" and not b.get("arena"):
                return  # OnRails without an arena (its line's battlefield)
            seen.add(bid)
            story.append((bid, bid == chapter.get("main") or b.get("rank") == "main", chapter.get("number"), "slot"))

        for m in camp.get("missions", []):
            if m.get("chapter") != ch.get("number"):
                continue
            for bdef in [m.get("boss")] + [st.get("boss") for st in m.get("stages", []) or [] if isinstance(st, dict)]:
                if isinstance(bdef, dict) and bdef.get("def"):
                    add(bdef["def"])
        for bid in slots:
            add(bid)
        for pair in unslotted:
            bid, after = (pair[0], pair[1]) if isinstance(pair, list) else (pair.get("arg0"), pair.get("arg1"))
            if after == ch.get("number") and bid not in seen and bid not in listed and bid in built:
                seen.add(bid)
                story.append((bid, built[bid].get("rank") == "main", ch.get("number"), "unslotted"))
    sh = book.sheet("Sanhunt", "Săn trùm", "Boss của Săn trùm theo thứ tự cốt truyện (port BossHunts.Story: chương theo thứ tự "
                    "dữ liệu, boss theo nhiệm vụ đầu tiên đánh nó, rồi ô chương, rồi Unslotted)")
    for c, m in (("thu_tu", "thứ tự cốt truyện (BossHunts.Story)"), ("chu_luc", "tính là boss chủ lực trong Săn trùm"),
                 ("chuong", "chương"), ("cach_xep", "slot (ô chương) / unslotted (BossHunts.Unslotted)"),
                 ("phong_khong", "boss tự chống máy bay (AirDefence: 2 bệ phòng không trở lên)"),
                 ("tuan", "có trong 10 boss tuần nào (BossHunt.Weekly theo hạt giống tuần)")):
        sh.col(c, meaning=m)
    sh.col("id", fk=BOSS_FK)
    for k, (bid, main, chapter, how) in enumerate(story):
        r = sh.row(bid, f"{B.CAMPAIGN}: chapters / missions (port Assets/MachineBrigade/Scripts/Game/Match/BossHunts.cs Story)")
        r.set("thu_tu", k + 1)
        r.set("chu_luc", bool(main))
        r.set("chuong", chapter)
        r.set("cach_xep", how)
        r.set("phong_khong", NEED_CODE_CHECK)
        r.set("tuan", NEED_CODE_CHECK)
    _b03.build(ctx, book, d, built, base_built, base_w)
    _unit_settle.apply(book)
    ctx.note("03_sanhunt", f"Sanhunt: {len(story)} boss theo port của BossHunts.Story (spec ghi 41; boss trên ray không có arena "
             "bị loại như trong mã).")
    us = book.sheet("Sanhunt_chua_xep", "Săn trùm: boss chưa có ô chương", "BossHunts.Unslotted: boss mới và chương nó đứng sau")
    us.col("sau_chuong", meaning="đứng sau chương")
    us.col("id", fk=BOSS_FK)
    for i, pair in enumerate(unslotted):
        bid, after = (pair[0], pair[1]) if isinstance(pair, list) else (pair.get("arg0"), pair.get("arg1"))
        r = us.row(bid, f"{HUNTS}:{u_lines[i] if i < len(u_lines) else ''} (Unslotted[{i}])", raw=pair)
        r.mark(sid_u, (i, 0), "id")
        r.set("sau_chuong", after, sid_u, (i, 1))
    sid, rows, lines = ctx.cs_table(HUNT, "All")
    hs = book.sheet("Sanhunt_ho_tro", "Săn trùm: hỗ trợ tác chiến", "HuntSupports.All (BossHunt.cs): 12 hỗ trợ chọn sau boss chủ lực")
    hs.col("ten_vi", meaning="tên tiếng Việt (HUD hunt.support.<id>)")
    for i, rowd in enumerate(rows):
        r = hs.row(rowd.get("id", str(i)), f"{HUNT}:{lines[i] if i < len(lines) else ''} (HuntSupports.All[{i}])", raw=rowd)
        r.set("ten_vi", B.name_of(ctx, f"hunt.support.{rowd.get('id')}")[1])
        r.flatten(rowd, sid, (i,))
