"""02_phuong_tien, layer A: vehicles (and elites), their weapon mounts, support cards, skills, equipment (GearCatalog.cs,
GearCatalog.Tower.cs, Gear.Model.cs, Gear.Tower.cs), commanders and enemy generals' passives (Commanders.cs), opening
squads, reference vehicles, global toughness."""
from __future__ import annotations

import re

from core.model import NEED_CODE_CHECK, child_rows
from core.repo import ROOT
from core.units import snake

from . import _b02, _c02_gear, _lane_c as C, _unit_settle
from . import _balance as B
from . import _game as G
from . import _units as U

FILE_ID = "02_phuong_tien"
TITLE = "Phương tiện"
DESC = "Xe, bệ vũ khí, thẻ hỗ trợ, kỹ năng, trang bị, commander, đội mở màn, xe tham chiếu, hệ số độ bền"

COMMANDERS = "Assets/MachineBrigade/Scripts/Sim/Content/Commanders.cs"
COMMANDER_DEFS = "Assets/MachineBrigade/Scripts/Sim/Content/CommanderDefs.cs"
GEAR = "Assets/MachineBrigade/Scripts/Game/Match/GearCatalog.cs"
GEAR_TOWER = "Assets/MachineBrigade/Scripts/Game/Match/GearCatalog.Tower.cs"
GEAR_MODEL = "Assets/MachineBrigade/Scripts/Game/Match/Gear.Model.cs"
GEAR_TOWER_GEAR = "Assets/MachineBrigade/Scripts/Game/Match/Gear.Tower.cs"
STATID_ENUM = "Assets/MachineBrigade/Scripts/Sim/Content/VehicleBoost.cs"
VEHICLE_FK = ["02_phuong_tien/Xe"]
FAMILY_OF = {"Combat": "Combat", "Econ": "Economy", "Gen": "General"}
# spec 03 B (Boss_hieu_qua) and the warning formula's slow vehicle (warningRules.escapeSpeed)
REFERENCE = [
    ("main_battle_tank", "Tăng chủ lực"), ("heavy_tank", "Tăng hạng nặng"), ("ifv", "Xe chiến đấu bộ binh"),
    ("armored_car", "Xe bọc thép bánh lốp"), ("gun_turret", "Tháp vừa (pháo)"),
]


def build(ctx):
    book = ctx.book(FILE_ID, TITLE, DESC)
    d = B.bal(ctx)
    res = B.resolved_vehicles(ctx)
    base = B.base_view(ctx)
    base_res = B.resolved_vehicles(base) if base else {}
    elites = d.get("elites") or {}

    # ------------------------------------------------------------------ Xe (+ mounts, missiles, parts)
    xe = book.sheet("Xe", "Xe", "Mỗi xe / máy bay / tàu của người chơi và địch, cả tinh nhuệ (elite): giá trị game và trường gốc")
    xe.col("loai_thuc_the", meaning="xe / tinh_nhue / vat_pham (card false: chỉ thả qua thẻ hỗ trợ, sự kiện)",
           enum=["xe", "tinh_nhue", "vat_pham"])
    U.declare(xe)
    xe.col("gia_quan_cp", unit="CP", meaning="giá tính quân (elite: max(1, round(cp gốc x elites.costScale)), Catalog.EliteCost)")
    xe.col("nhom_gia", meaning="nhóm giá (tính trong mã)")
    xe.col("tinh_nhue_cua", meaning="xe gốc của bản tinh nhuệ (eliteOf)", fk=VEHICLE_FK)
    xe.col("ban_tinh_nhue", meaning="bản tinh nhuệ của xe này", fk=VEHICLE_FK)
    xe.col("vai_tro_mo_man", meaning="vai trò đội mở màn có xe này (openingSquads.roles)")
    xe.col("mo_khoa", meaning="mở khóa (chiến dịch / xu: đọc ở 11 và 07)")
    mounts = U.mounts_child("Xe_vu_khi", "Xe: bệ vũ khí phụ", book, xe)
    missiles = book.sheet("Xe_ten_lua", "Xe: tên lửa mang", "missiles[]", parent=xe)
    parts = book.sheet("Xe_bo_phan", "Xe: bộ phận", "parts[] của xe không phải boss", parent=xe)
    roles = (d.get("openingSquads") or {}).get("roles") or {}
    role_of = {}
    for role, cands in roles.items():
        if isinstance(cands, list):
            for c in cands:
                role_of.setdefault(c, []).append(role)
    elite_of = {v.get("eliteOf"): vid for vid, v, _ in B.vehicle_entries(ctx) if v.get("eliteOf")}
    for vid, v, path in B.vehicle_entries(ctx):
        kind = B.classify(ctx, vid)
        if kind not in ("vehicle", "elite"):
            continue
        r = xe.row(vid, B.nguon(path), raw=v)
        rr = res[vid]
        r.set("loai_thuc_the", "tinh_nhue" if kind == "elite" else "vat_pham" if rr.get("card") is False else "xe")
        eff = U.fill(ctx, r, vid, rr, base_record=base_res.get(vid), has_base=base is not None)
        if kind == "elite":
            r.values["mau_trong_tran_hp"] = NEED_CODE_CHECK  # an elite's health scale is applied on the field (Vehicle.HpScale)
            orig = res.get(v.get("eliteOf"), {})
            r.set("gia_quan_cp", max(1, round(orig.get("cp", 0) * elites.get("costScale", 1.6))))
        else:
            r.set("gia_quan_cp", eff["base_cp"])
        r.set("nhom_gia", NEED_CODE_CHECK)
        r.set("tinh_nhue_cua", v.get("eliteOf", ""))
        r.set("ban_tinh_nhue", elite_of.get(vid, ""))
        r.set("vai_tro_mo_man", ";".join(sorted(role_of.get(vid, []))))
        r.set("mo_khoa", NEED_CODE_CHECK)
        U.raw(r, v, path, children={
            "secondary": U.child(mounts),
            "missiles": lambda row, items, src, p: child_rows(missiles, row, items, src, p),
            "parts": lambda row, items, src, p: child_rows(parts, row, items, src, p, vectors={"at": ["x_m", "y_m", "z_m"]}),
        })

    # ------------------------------------------------------------------ The_ho_tro
    th = book.sheet("The_ho_tro", "Thẻ hỗ trợ", "supports[]: pháo kích, không kích, khói, thả hộ tống...")
    th.col("ten_en", meaning="tên tiếng Anh (HUD support.<id>)")
    th.col("ten_vi", meaning="tên tiếng Việt (HUD support.<id>)")
    th.col("units", meaning="đơn vị được thả", fk=VEHICLE_FK + ["03_boss/Boss", "04_can_cu_thap/Thap", "04_can_cu_thap/Tuong",
                                                         "04_can_cu_thap/Mo_dun_tien_ich"])
    B.declare_changes(th, ["cp", "cooldown_s", "damage", "radius_m", "count"])
    base_sup = {s["id"]: s for s in base.data(B.BALANCE).get("supports", [])} if base else {}
    for i, s in enumerate(d.get("supports", [])):
        path = ("supports", i)
        r = th.row(s["id"], B.nguon(path), raw=s)
        en, vi = B.name_of(ctx, f"support.{s['id']}")
        r.set("ten_en", en)
        r.set("ten_vi", vi)
        keyed = lambda x: {"cp": x.get("cp", 0), "cooldown_s": x.get("cooldown"), "damage": x.get("damage"),  # noqa: E731
                           "radius_m": x.get("radius"), "count": x.get("count")}
        b = base_sup.get(s["id"])
        B.set_changes(r, ["cp", "cooldown_s", "damage", "radius_m", "count"], keyed(s), keyed(b) if b else None,
                      base is not None)
        r.flatten(s, B.BALANCE, path)

    # ------------------------------------------------------------------ Ky_nang (skills)
    kn = book.sheet("Ky_nang", "Kỹ năng nội tại", "skills[]: khiên, khói, sửa... của xe, elite, boss")
    kn.col("dung_boi", meaning="đơn vị có kỹ năng này (vehicles[*].skills sau inherits)")
    users = {}
    for vid, rr in res.items():
        for sk in rr.get("skills", []) if isinstance(rr.get("skills"), list) else []:
            users.setdefault(sk, set()).add(vid)
    for vid, b in B.boss_built(ctx).items():
        for sk in b.get("skills", []) if isinstance(b.get("skills"), list) else []:
            users.setdefault(sk, set()).add(vid)
    for i, s in enumerate(d.get("skills", [])):
        path = ("skills", i)
        r = kn.row(s["id"], B.nguon(path), raw=s)
        r.set("dung_boi", ";".join(sorted(users.get(s["id"], []))))
        r.flatten(s, B.BALANCE, path)

    # ------------------------------------------------------------------ Tinh_nhue (elite rules) / Nhanh / Do_ben
    tn = book.kv_sheet("Tinh_nhue_luat", "Luật tinh nhuệ", "elites: hệ số giá / máu / sát thương, ngân sách và trần theo độ khó")
    book.kv_rows(tn, elites, B.BALANCE, ("elites",), "elites")
    nh = book.sheet("Nhanh_xe", "Nhánh quân", "branches: nhánh -> các lớp xe")
    nh.col("lop", meaning="các lớp thuộc nhánh")
    for k, classes in (d.get("branches") or {}).items():
        r = nh.row(k, B.nguon(("branches", k)), raw=classes)
        r.set("lop", ";".join(classes))
        for j in range(len(classes)):
            r.mark(B.BALANCE, ("branches", k, j), "lop")
    db = book.kv_sheet("Do_ben", "Hệ số độ bền", "toughness: máu trong trận = hp x hệ số (xe, boss)")
    book.kv_rows(db, d.get("toughness") or {}, B.BALANCE, ("toughness",), "toughness")

    # ------------------------------------------------------------------ Trang_bi (GearCatalog.cs)
    tables = [
        ("Bases", "Trang_bi", "Trang bị: loại cơ bản", "40 loại trang bị (ô, chỉ số ngầm, giá trị đỉnh 5 hạng, đánh đổi)", "id", "gear.base."),
        # Gear book 04/10 (lane A): name_prefix fixed to the HUD key GearText.cs actually reads (was "gear.module." /
        # "gear.sub." / "gear.brand.", none of which ever matched; ten_vi had been None for every Module/Sub/Brand row).
        ("Modules", "Trang_bi_mo_dun", "Trang bị: mô-đun đặc biệt", "14 mô-đun (Sử thi / Huyền thoại); FlareDispenser, TrophyAps chỉ nâng cấp hệ có sẵn", "module", "special."),
        ("Traits", "Trang_bi_dac_tinh", "Trang bị: đặc tính", "45 đặc tính (giá trị Sử thi / Huyền thoại)", "id", "trait."),
        ("Subs", "Trang_bi_dong_phu", "Trang bị: dòng phụ", "dòng phụ: giá trị theo hạng, ô được ra, trọng số", "stat", "stat.line."),
        ("Brands", "Trang_bi_bo", "Trang bị: bộ (brand)", "bộ trang bị: thưởng 2 món / 4 món", "id", "set."),
    ]
    for array, sname, title, desc, key, name_prefix in tables:
        sid, rows, lines = ctx.cs_table(GEAR, array)
        sh = book.sheet(sname, title, desc)
        sh.col("ten_vi", meaning=f"tên tiếng Việt (HUD {name_prefix}<id>)")
        for i, rowd in enumerate(rows):
            rid = str(rowd.get(key, i))
            r = sh.row(rid, f"{GEAR}:{lines[i] if i < len(lines) else ''} ({array}[{i}])", raw=rowd)
            sn = snake(rid)
            r.set("ten_vi", B.name_of(ctx, name_prefix + rid, name_prefix + sn, f"trait.{sn}", f"stat.line.{sn}", f"special.{sn}")[1])
            r.flatten({k: x for k, x in rowd.items() if k != key or k == "id"}, sid, (i,))
            if key != "id":
                r.mark(sid, (i, key), "id")

    # ------------------------------------------------------------------ Trang_bi_thap / Trang_bi_dac_tinh_thap
    # (GearCatalog.Tower.cs: 13 tower base types over 3 tower slots, 10 tower traits; owner 04/10 "chưa export hết
    # trang bị" — tower gear carried no sheet at all before this). BaseTypeDef / TraitDef are declared in GearCatalog.cs
    # (extra=[GEAR] gives the constructor signatures cs_table needs to name the positional args).
    tower_tables = [
        (GEAR_TOWER, "TowerBases", "Trang_bi_thap", "Trang bị tháp: loại cơ bản",
         "14 loại trang bị tháp, 3 ô (Weapon/Structure/Systems); numbers ở mức đỉnh 5 hạng như trang bị xe", "id", "gear.base."),
    ]
    for path, array, sname, title, desc, key, name_prefix in tower_tables:
        sid, rows, lines = ctx.cs_table(path, array, extra=[GEAR])
        sh = book.sheet(sname, title, desc)
        sh.col("ten_vi", meaning=f"tên tiếng Việt (HUD {name_prefix}<id>)")
        for i, rowd in enumerate(rows):
            rid = str(rowd.get(key, i))
            r = sh.row(rid, f"{path}:{lines[i] if i < len(lines) else ''} ({array}[{i}])", raw=rowd)
            sn = snake(rid)
            r.set("ten_vi", B.name_of(ctx, name_prefix + rid, name_prefix + sn, f"trait.{sn}", f"stat.line.{sn}", f"special.{sn}")[1])
            r.flatten({k: x for k, x in rowd.items() if k != key or k == "id"}, sid, (i,))
            if key != "id":
                r.mark(sid, (i, key), "id")

    # Tower traits: a separate sheet (5 of the 10 ids repeat a vehicle Trang_bi_dac_tinh row, e.g. Executioner on
    # GearSlot.Weapon vs GearSlot.TowerWeapon, with their own numbers) — "@thap" keeps row ids unique across sheets.
    sid, rows, lines = ctx.cs_table(GEAR_TOWER, "TowerTraits", extra=[GEAR])
    tt = book.sheet("Trang_bi_dac_tinh_thap", "Trang bị tháp: đặc tính",
                     "10 đặc tính tháp (giá trị Sử thi / Huyền thoại); 5 khóa trùng Trang_bi_dac_tinh (ô tháp riêng, số có thể khác)")
    tt.col("ten_vi", meaning="tên tiếng Việt (HUD trait.<id>)")
    for i, rowd in enumerate(rows):
        base_id = str(rowd.get("id", i))
        r = tt.row(f"{base_id}@thap", f"{GEAR_TOWER}:{lines[i] if i < len(lines) else ''} (TowerTraits[{i}])", raw=rowd)
        sn = snake(base_id)
        r.set("ten_vi", B.name_of(ctx, "trait." + sn, "trait." + base_id)[1])
        r.flatten({k: x for k, x in rowd.items() if k != "id"}, sid, (i,))
        r.mark(sid, (i, "id"), "id")

    # ------------------------------------------------------------------ Trang_bi_tran (loadout stat caps)
    # GearCatalog.cs BuildCaps() / GearCatalog.Tower.cs BuildTowerCaps(): what a whole 6-slot (vehicle) or 3-slot
    # (tower) loadout may add to a stat; built by Set(...) calls (one a range loop), not a literal array, so a small
    # regex over the method text reads it (ctx.cs_custom; see _cap_extractor / _tower_override_extractor above).
    order = _statid_order()
    base_sid, cap_rows, cap_lines = ctx.cs_custom(f"{GEAR}#StatCap", GEAR, _cap_extractor(order))
    over_sid, over_rows, _over_lines = ctx.cs_custom(f"{GEAR_TOWER}#TowerStatCapOverride", GEAR_TOWER, _tower_override_extractor)
    over_map = {r["stat"]: r["tran"] for r in over_rows}
    tr = book.sheet("Trang_bi_tran", "Trang bị: trần cộng dồn",
                     "Trần tối đa cả loadout có thể cộng vào một chỉ số (StatId không liệt kê: GearCatalog không đặt trần riêng, "
                     "chỉ số đó không rơi làm trang bị hoặc không giới hạn)")
    tr.col("tran_xe", meaning="trần cho xe, 6 ô (GearCatalog.StatCap)")
    tr.col("tran_thap", meaning="trần cho tháp, 3 ô (GearCatalog.TowerStatCap = trần xe, trừ Range 0.1 và Regen 0.01)")
    for i, row in enumerate(cap_rows):
        stat = row["stat"]
        r = tr.row(stat, f"{GEAR}:{cap_lines[i]} (BuildCaps)", raw=row)
        r.set("tran_xe", row["tran"], base_sid, (i, "tran"))
        r.mark(base_sid, (i, "stat"), "id")
        r.set("tran_thap", over_map.get(stat, row["tran"]))
    for i, row in enumerate(over_rows):
        rr = tr.rows.get(row["stat"])
        if rr is not None:
            rr.mark(over_sid, (i, "stat"), "id")
            rr.mark(over_sid, (i, "tran"), "tran_thap")

    # ------------------------------------------------------------------ Trang_bi_chi_so (Gear.Model.cs / Gear.Tower.cs)
    # The rarity- or index-keyed literal tables left over the two files that build a piece's numbers (sub-stat count
    # and growth-bump levels by rarity, the plating / tower main-stat tops by rarity, the tower slot order): everything
    # cs_table reads as a plain scalar array (no constructor, so no dict), one row an element (as d11's Trang_bi_hang).
    cs_sh = book.sheet("Trang_bi_chi_so", "Trang bị: bảng chỉ số",
                        "Gear.Model.cs / Gear.Tower.cs: bảng hằng còn lại theo độ hiếm hoặc theo chỉ số (mỗi phần tử một dòng)")
    cs_sh.col("bang", meaning="<file>#<mảng>")
    cs_sh.col("chi_so", meaning="chỉ số trong bảng (độ hiếm Common=0..Legendary=4, trừ SubBumpLevels và TowerSlots)")
    for path, array in ((GEAR_MODEL, "SubCount"), (GEAR_MODEL, "SubBumpLevels"), (GEAR_MODEL, "PlatingTop"),
                        (GEAR_TOWER_GEAR, "TowerSlots"), (GEAR_TOWER_GEAR, "StandardTop"), (GEAR_TOWER_GEAR, "RepairTop")):
        sid, rows, lines = ctx.cs_table(path, array)
        fname = path.rsplit("/", 1)[-1][:-3]
        for i, v in enumerate(rows):
            r = cs_sh.row(f"{fname}#{array}/{i}", f"{path}:{lines[i] if i < len(lines) else ''} ({array}[{i}])", raw=v)
            r.set("bang", f"{fname}#{array}")
            r.set("chi_so", i)
            C.cs_element_row(r, v, sid, (i,))

    # ------------------------------------------------------------------ Commander (+ passives, prices)
    cm = book.sheet("Commander", "Commander và nội tại tướng", "Commanders.cs: 14 commander của người chơi + nội tại 8 tướng địch")
    cm.col("ho", meaning="Combat / Economy / General")
    cm.col("ten_vi", meaning="tên tiếng Việt (HUD cmdr.<id>.name)")
    cm.col("khai_bao_qua", meaning="hàm dựng trong Commanders.cs (Combat / Econ / Gen) hoặc new CommanderDef")
    lines_sh = book.sheet("Commander_noi_tai", "Commander: dòng nội tại", "Lines: chỉ số, giá trị, phạm vi", parent=cm)
    price_sh = book.sheet("Commander_gia", "Commander: hệ số giá", "Prices: phạm vi giá, hệ số", parent=cm)
    for array in ("All", "Generals"):
        sid, rows, lines = ctx.cs_table(COMMANDERS, array, extra=[COMMANDER_DEFS])
        for i, rowd in enumerate(rows):
            norm = {_lower(k): x for k, x in rowd.items()}
            cid = norm.get("id") or ("gen." + str(norm.get("general", i)))
            r = cm.row(cid, f"{COMMANDERS}:{lines[i] if i < len(lines) else ''} ({array}[{i}])", raw=rowd)
            via = rowd.get("_via", "")
            r.set("ho", norm.get("family") or FAMILY_OF.get(via, ""))
            r.set("ten_vi", B.name_of(ctx, f"cmdr.{cid}.name", f"cmdr.{cid}")[1])
            r.set("khai_bao_qua", via or "new CommanderDef")
            if via:
                r.mark(sid, (i, "_via"), "khai_bao_qua")
            for k, x in rowd.items():
                if k == "_via":
                    continue
                lk = _lower(k)
                if lk == "lines":
                    r.children.add(k)
                    _cs_children(lines_sh, r, x, sid, (i, k))
                elif lk == "prices":
                    r.children.add(k)
                    _cs_children(price_sh, r, x, sid, (i, k))
                else:
                    r.flatten({k: x}, sid, (i,))

    # ------------------------------------------------------------------ Doi_mo_man (opening squads)
    os_ = d.get("openingSquads") or {}
    dm = book.sheet("Doi_mo_man", "Đội mở màn", "openingSquads.commanders / generals: vai trò của đội mở màn")
    dm.col("ben", meaning="commander (người chơi) / general (địch)")
    dm.col("vai_tro", meaning="vai trò (Doi_mo_man_vai_tro)", fk=["02_phuong_tien/Doi_mo_man_vai_tro"])
    dm.col("base_cp_uoc_tinh", unit="CP", meaning="tổng baseCP đội với bộ bài trống: thẻ rẻ nhất đủ điều kiện mỗi vai trò "
           "(port Sim/Modes/OpeningSquads.cs Pick, không trần ngân sách)")
    dm.col("thieu_vai_tro_hoan_cp", meaning="thiếu vai trò: bo_vai_tro_giu_cp (vai trò không có thẻ bị bỏ, CP của nó giữ lại; "
           "OpeningSquads.cs Pick)", enum=["bo_vai_tro_giu_cp"])
    for side, sname in (("commanders", "commander"), ("generals", "general")):
        for k, role_list in (os_.get(side) or {}).items():
            path = ("openingSquads", side, k)
            r = dm.row(f"{sname}.{k}", B.nguon(path), raw=role_list)
            r.set("ben", sname)
            r.set("vai_tro", ";".join(role_list))
            for j in range(len(role_list)):
                r.mark(B.BALANCE, path + (j,), "vai_tro")
            if not role_list:
                r.mark(B.BALANCE, path, "vai_tro")
            picks = [G.opening_cheapest(roles[x], res) for x in role_list if x in roles]
            r.set("base_cp_uoc_tinh", sum(p[1] for p in picks if p))
            r.set("thieu_vai_tro_hoan_cp", "bo_vai_tro_giu_cp")
    vt = book.sheet("Doi_mo_man_vai_tro", "Đội mở màn: vai trò", "openingSquads.roles: thẻ chọn được cho mỗi vai trò")
    vt.col("ung_vien", meaning="các thẻ chọn được (theo thứ tự ưu tiên của dữ liệu)", fk=VEHICLE_FK)
    vt.col("cp_toi_da", unit="CP", meaning="trần CP thay cho danh sách (maxCp)")
    vt.col("re_nhat", meaning="thẻ rẻ nhất đủ điều kiện (cp > 0, không công trình / boss / tinh nhuệ / tàu; cp rồi id; "
           "port OpeningSquads.cs Pick, bộ bài trống)", fk=VEHICLE_FK)
    vt.col("re_nhat_cp", unit="CP", meaning="cp của ứng viên rẻ nhất")
    for role, cands in roles.items():
        path = ("openingSquads", "roles", role)
        r = vt.row(role, B.nguon(path), raw=cands)
        if isinstance(cands, list):
            r.set("ung_vien", ";".join(cands))
            for j in range(len(cands)):
                r.mark(B.BALANCE, path + (j,), "ung_vien")
        elif isinstance(cands, dict):
            r.flatten(cands, B.BALANCE, path, aliases={"maxCp": "cp_toi_da"})
        best = G.opening_cheapest(cands, res)  # OpeningSquads.cs Pick: eligible cards only (baseCP, then id)
        r.set("re_nhat", best[0] if best else "")
        r.set("re_nhat_cp", best[1] if best else "")
    luat = book.kv_sheet("Doi_mo_man_luat", "Đội mở màn: luật", "openingSquads.share / modes / enemyModes")
    book.kv_rows(luat, {k: x for k, x in os_.items() if k not in ("commanders", "generals", "roles")}, B.BALANCE,
                 ("openingSquads",), "openingSquads")

    # ------------------------------------------------------------------ Xe_tham_chieu
    tc = book.sheet("Xe_tham_chieu", "Xe tham chiếu", "Xe tham chiếu của Boss_hieu_qua (spec 03 B) và xe chậm tham chiếu của vòng cảnh báo")
    tc.col("ten_vi_spec", meaning="tên trong spec")
    tc.col("don_vi_id", meaning="id đơn vị", fk=VEHICLE_FK + ["04_can_cu_thap/Thap"])
    tc.col("toc_do_m_s", unit="m/s", meaning="tốc độ (giá trị game)")
    tc.col("mau_trong_tran_hp", unit="hp", meaning="máu trong trận (giá trị game)")
    tc.col("giap_truoc", meaning="giáp trước (giá trị game)")
    tc.col("giap_noc", meaning="giáp nóc (giá trị game)")
    tc.col("cong_trinh", meaning="là công trình (giáp đều, hệ số Structure)")
    for vid, name in REFERENCE:
        r = tc.row(vid, "Docs/prompts/export_full_vi.txt (spec 03 B)")
        r.set("ten_vi_spec", name)
        r.set("don_vi_id", vid)
        if vid in res:
            e = U.effective(ctx, vid, res[vid])
            r.set("toc_do_m_s", e["toc_do_m_s"])
            r.set("mau_trong_tran_hp", e["mau_trong_tran_hp"])
            r.set("giap_truoc", e["giap_truoc"])
            r.set("giap_noc", e["giap_noc"])
            r.set("cong_trinh", e["cong_trinh"])
    esc = (d.get("warningRules") or {}).get("escapeSpeed")
    r = tc.row("xe_cham_tham_chieu", f"{B.BALANCE}: warningRules.escapeSpeed (xem 01/Canh_bao_vong)")
    r.set("ten_vi_spec", "xe chậm tham chiếu của vòng cảnh báo")
    r.set("toc_do_m_s", esc if esc is not None else 4.5)  # FixRules.cs WarningRules.EscapeSpeed default 4.5

    _b02.build(ctx, book, d, res)
    _unit_settle.apply(book)

    # ------------------------------------------------------------------ layer C (gear book, 04/10): code-sourced sheets
    _c02_gear.build(ctx, book)


def _lower(k: str) -> str:
    return k[:1].lower() + k[1:] if k else k


def _cs_children(sheet, parent, items, sid, path):
    if not isinstance(items, list):
        return
    for j, it in enumerate(items):
        r = sheet.row(f"{parent.id}/{j}", f"{sid} ({'.'.join(str(p) for p in path)}[{j}])", raw=it)
        r.set(sheet.parent_col, parent.id)
        r.set("thu_tu", j)
        if isinstance(it, dict):
            r.flatten(it, sid, path + (j,))
        else:
            r.set("value", it, sid, path + (j,))
    if not items:
        parent.set(sheet.name.lower(), "", sid, path)


# ---------------------------------------------------------------------- Trần cộng dồn (BuildCaps() / BuildTowerCaps())
# StatCap and TowerStatCap (GearCatalog.cs / GearCatalog.Tower.cs) are built by a method (Set(stat, value) calls, one a
# range loop), not a literal array, so cs_table cannot read them; a small regex over the method's own text does.
_ENUM_BODY = re.compile(r"public enum StatId\s*\{(.*?)\n\s*\}", re.S)
_SET_OR_LOOP = re.compile(
    r"Set\(StatId\.(?P<one>\w+),\s*(?P<v1>-?[\d.]+)f?\)"
    r"|for\s*\(var r = StatId\.(?P<lo>\w+); r <= StatId\.(?P<hi>\w+); r\+\+\) Set\(r,\s*(?P<v2>-?[\d.]+)f?\);")
_TOWER_OVERRIDE = re.compile(r"caps\[\(int\)StatId\.(?P<stat>\w+)\]\s*=\s*(?P<v>-?[\d.]+)f;")


def _statid_order() -> list[str]:
    """StatId's members, in declaration order (doc comments and line comments stripped)."""
    text = (ROOT / STATID_ENUM).read_text("utf-8-sig")
    m = _ENUM_BODY.search(text)
    body = re.sub(r"///[^\n]*|//[^\n]*", "", m.group(1))
    return [n.strip() for n in body.split(",") if re.fullmatch(r"[A-Za-z_]\w*", n.strip())]


def _cap_extractor(order: list[str]):
    def extractor(text: str):
        rows, lines = [], []
        for m in _SET_OR_LOOP.finditer(text):
            line_no = text.count("\n", 0, m.start()) + 1
            if m.group("one"):
                rows.append({"stat": m.group("one"), "tran": float(m.group("v1"))})
                lines.append(line_no)
            else:
                i0, i1, val = order.index(m.group("lo")), order.index(m.group("hi")), float(m.group("v2"))
                for name in order[i0:i1 + 1]:
                    rows.append({"stat": name, "tran": val})
                    lines.append(line_no)
        return rows, lines
    return extractor


def _tower_override_extractor(text: str):
    rows, lines = [], []
    for m in _TOWER_OVERRIDE.finditer(text):
        rows.append({"stat": m.group("stat"), "tran": float(m.group("v"))})
        lines.append(text.count("\n", 0, m.start()) + 1)
    return rows, lines
