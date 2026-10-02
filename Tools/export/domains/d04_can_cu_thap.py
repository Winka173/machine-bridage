"""04_can_cu_thap, layer A: towers (cards and rank-7 branches), walls, headquarters (types x HQ level), utility modules,
base loadouts by HQ level, rebuild rules, reference defence loadouts, the AI's base building."""
from __future__ import annotations

from core.model import NEED_CODE_CHECK, chua_ap

from . import _b04, _unit_settle
from . import _balance as B
from . import _game as G
from . import _units as U

FILE_ID = "04_can_cu_thap"
TITLE = "Căn cứ và tháp"
DESC = "Tháp và nhánh, tường, nhà chính (kiểu x cấp), mô-đun tiện ích, ô căn cứ theo cấp HQ, xây lại, loadout tham chiếu, AI xây căn cứ"

TOWER_FK = ["04_can_cu_thap/Thap", "04_can_cu_thap/Mo_dun_tien_ich", "04_can_cu_thap/Tuong", "04_can_cu_thap/Nha_chinh"]
LEVEL_LISTS = {"fortress": ("scale", "airScale"), "garrison": ("every", "caps", "squads"),
               "shield": ("scale", "regen", "dome")}


def build(ctx):
    book = ctx.book(FILE_ID, TITLE, DESC)
    d = B.bal(ctx)
    base_cfg = d.get("base") or {}
    res = B.resolved_vehicles(ctx)
    base = B.base_view(ctx)
    base_res = B.resolved_vehicles(base) if base else {}
    rebuild = base_cfg.get("rebuild") or {}
    roster = set(base_cfg.get("roster") or [])

    def unit_sheet(name, title, desc, kinds, extra=None):
        sh = book.sheet(name, title, desc)
        U.declare(sh)
        if extra:
            extra(sh)
        mounts = U.mounts_child(f"{name}_vu_khi", f"{title}: bệ vũ khí phụ", book, sh)
        rows = []
        for vid, v, path in B.vehicle_entries(ctx):
            if B.classify(ctx, vid) not in kinds:
                continue
            r = sh.row(vid, B.nguon(path), raw=v)
            U.fill(ctx, r, vid, res[vid], base_record=base_res.get(vid), has_base=base is not None)
            rows.append((r, vid, v, path))
            U.raw(r, v, path, children={"secondary": U.child(mounts)})
        return sh, rows

    # ------------------------------------------------------------------ Thap
    def thap_cols(sh):
        sh.col("the_goc", meaning="thẻ tháp gốc của nhánh (branchOf)", fk=["04_can_cu_thap/Thap"])
        sh.col("nhanh_ab", meaning="nhánh bậc 7: hậu tố id (long / auto ...) hoặc noBranch")
        sh.col("co_o", meaning="cỡ ô (fort.size: Small / Medium / Large)")
        sh.col("vai_tro", meaning="vai trò tháp (towerRole)")
        sh.col("trong_roster", meaning="có trong base.roster (thẻ tháp người chơi chọn)")
        sh.col("base_rebuild_cp", unit="CP", meaning="giá xây lại riêng (rebuildCp) hoặc theo cỡ ô (base.rebuild.<cỡ>.cp)")
        sh.col("runtime_rebuild_cp", unit="CP", meaning="giá game thu khi thả lại tháp: rebuildCp > 0, còn lại CP theo cỡ ô "
               "(port Sim/Content/BaseRules.cs RebuildCost; công thức định giá ở Thap_gia_cong_thuc)",
               source_note="port Sim/Content/BaseRules.cs RebuildCost")
        sh.col("xay_lai_cho_s", unit="s", meaning="thời gian chờ xây lại theo cỡ ô (base.rebuild.<cỡ>.cooldown)")
        sh.col("xay_lai_tha_s", unit="s", meaning="thời gian thả khi xây lại theo cỡ ô (base.rebuild.<cỡ>.drop)")
        sh.col("mo_khoa", meaning="mở khóa (07 / 11)")
        sh.col("the_cu_gop_vao", meaning="thẻ cũ gộp vào (DECISIONS)")
        sh.col("co_can_bang", meaning="cờ REBALANCE_STATS / HOLD (prompt 32)")

    th, trows = unit_sheet("Thap", "Tháp", "Mỗi tháp (thẻ và nhánh bậc 7) một dòng", ("tower",), thap_cols)
    for r, vid, v, path in trows:
        rr = res[vid]
        size = ((rr.get("fort") or {}) if isinstance(rr.get("fort"), dict) else {}).get("size", "")
        r.set("the_goc", rr.get("branchOf", ""))
        r.set("nhanh_ab", "noBranch" if rr.get("noBranch") else (vid.split(".", 1)[1] if "." in vid else ""))
        r.set("co_o", size)
        r.set("vai_tro", rr.get("towerRole", ""))
        r.set("trong_roster", vid in roster)
        per_size = rebuild.get(size.lower(), {}) if size else {}
        r.set("base_rebuild_cp", rr.get("rebuildCp", per_size.get("cp", "")))
        r.set("runtime_rebuild_cp", G.rebuild_cost(rr, rebuild))
        r.set("xay_lai_cho_s", per_size.get("cooldown", ""))
        r.set("xay_lai_tha_s", per_size.get("drop", ""))
        r.set("mo_khoa", NEED_CODE_CHECK)
        r.set("the_cu_gop_vao", NEED_CODE_CHECK)
        r.set("co_can_bang", NEED_CODE_CHECK)

    # ------------------------------------------------------------------ Tuong (+ wall types)
    def tuong_cols(sh):
        sh.col("loai", meaning="loại tường (base.walls.types)")
        sh.col("do_ben_tuong_doi", meaning="độ bền tương đối (types.<loại>.durability)")
        sh.col("tuong_them", meaning="đoạn tường thêm (types.<loại>.extra)")
        sh.col("co_sung", meaning="tường gắn súng (types.<loại>.gun)")
        sh.col("trang_thai_navmesh", meaning="trạng thái navmesh (vật cản: obstacle)")

    tg, wrows = unit_sheet("Tuong", "Tường", "Mỗi loại tường một dòng (def + base.walls.types)", ("wall",), tuong_cols)
    walls = base_cfg.get("walls") or {}
    type_of = {t.get("def"): (k, t) for k, t in (walls.get("types") or {}).items() if isinstance(t, dict)}
    for r, vid, v, path in wrows:
        k, t = type_of.get(vid, ("", {}))
        r.set("loai", k)
        tp = ("base", "walls", "types", k)
        for key, col in (("durability", "do_ben_tuong_doi"), ("extra", "tuong_them"), ("gun", "co_sung")):
            if key in t:
                r.set(col, t[key], B.BALANCE, tp + (key,))
            else:
                r.set(col, "")
        if "def" in t:
            r.mark(B.BALANCE, tp + ("def",), "id")
        r.set("trang_thai_navmesh", "obstacle" if res[vid].get("obstacle") else "")
    tl = book.kv_sheet("Tuong_luat", "Tường: luật", "base.walls: xe phá tường, máu đoạn, số tuyến, mặc định, tường theo tướng")
    book.kv_rows(tl, {k: x for k, x in walls.items() if k != "types"}, B.BALANCE, ("base", "walls"), "base.walls")

    # ------------------------------------------------------------------ Nha_chinh (+ types x level)
    nc, hrows = unit_sheet("Nha_chinh", "Nhà chính", "Nhà chính và các kiểu (fortress / shield...)", ("hq",))
    hq_types = base_cfg.get("hqTypes") or {}
    kt = book.sheet("Nha_chinh_kieu", "Nhà chính: kiểu", "hqTypes.<kiểu>: trường không theo cấp")
    kt.col("nha_chinh", meaning="nhà chính của kiểu (ground / air / hq)", fk=["04_can_cu_thap/Nha_chinh"])
    kc = book.sheet("Nha_chinh_kieu_cap", "Nhà chính: kiểu x cấp HQ", "hqTypes.<kiểu>.<danh sách>[cấp-1]: sức mạnh, đồn trú, khiên theo HQ 1-5")
    kc.col("kieu", meaning="kiểu nhà chính", fk=["04_can_cu_thap/Nha_chinh_kieu"])
    kc.col("cap_hq", meaning="cấp HQ 1-5")
    for k, t in hq_types.items():
        if not isinstance(t, dict) or k == "ai":
            continue
        path = ("base", "hqTypes", k)
        r = kt.row(k, B.nguon(path), raw=t)
        r.set("nha_chinh", ";".join(x for x in (t.get("ground"), t.get("air"), t.get("hq")) if isinstance(x, str)))
        lists = LEVEL_LISTS.get(k, ())
        r.flatten({kk: x for kk, x in t.items() if kk not in lists}, B.BALANCE, path)
        n = max((len(t[x]) for x in lists if isinstance(t.get(x), list)), default=0)
        for lvl in range(n):
            cr = kc.row(f"{k}/{lvl + 1}", B.nguon(path) + f" [cấp {lvl + 1}]")
            cr.set("kieu", k)
            cr.set("cap_hq", lvl + 1)
            for x in lists:
                vals = t.get(x)
                if not isinstance(vals, list) or lvl >= len(vals):
                    continue
                val = vals[lvl]
                if isinstance(val, dict):
                    cr.flatten(val, B.BALANCE, path + (x, lvl), prefix=f"{x}_")
                else:
                    cr.set(f"{x}", val, B.BALANCE, path + (x, lvl))
    nl = book.kv_sheet("Nha_chinh_luat", "Nhà chính: luật", "base.hq, hqTypes.default / skillCooldown / radius / ai (kiểu theo tướng, độ khó)")
    book.kv_rows(nl, {"hq": base_cfg.get("hq")}, B.BALANCE, ("base",), "base")
    book.kv_rows(nl, {k: x for k, x in hq_types.items() if not (isinstance(x, dict) and k != "ai")}, B.BALANCE,
                 ("base", "hqTypes"), "base.hqTypes", prefix=("hqTypes",))

    # ------------------------------------------------------------------ Mo_dun_tien_ich
    unit_sheet("Mo_dun_tien_ich", "Mô-đun tiện ích", "Trạm sửa, kho đạn, sân bay, trạm hậu cần, radar (ô tiện ích)", ("utility",))

    # ------------------------------------------------------------------ Loadout_can_cu, Xay_lai, Dot_phong_thu
    lo = book.sheet("Loadout_can_cu", "Ô căn cứ theo cấp HQ", "base.levels (thường) và base.longLevels (bản đồ dài): số ô mỗi cỡ")
    lo.col("bang", meaning="levels / longLevels")
    lo.col("cap_hq", meaning="cấp HQ 1-5")
    for key in ("levels", "longLevels"):
        for i, slots in enumerate(base_cfg.get(key) or []):
            path = ("base", key, i)
            r = lo.row(f"{key}/{i + 1}", B.nguon(path), raw=slots)
            r.set("bang", key)
            r.set("cap_hq", i + 1)
            r.flatten(slots, B.BALANCE, path)
    xl = book.sheet("Xay_lai", "Xây lại tháp theo cỡ ô", "base.rebuild.<cỡ>: CP, thời gian chờ, thời gian thả")
    for size, cfg in rebuild.items():
        if isinstance(cfg, dict):
            r = xl.row(size, B.nguon(("base", "rebuild", size)), raw=cfg)
            r.flatten(cfg, B.BALANCE, ("base", "rebuild", size))
    cl = book.kv_sheet("Can_cu_luat", "Căn cứ: luật", "base.rebuild (chung), longForward, outpost, roles (vai trò căn cứ theo chế độ), roster")
    book.kv_rows(cl, {k: x for k, x in rebuild.items() if not isinstance(x, dict)}, B.BALANCE, ("base", "rebuild"),
                 "base.rebuild", prefix=("rebuild",))
    for key in ("longForward", "outpost", "roles", "roster"):
        if key in base_cfg:
            book.kv_rows(cl, base_cfg[key], B.BALANCE, ("base", key), f"base.{key}", prefix=(key,))
    dp = book.sheet("Dot_phong_thu", "Loadout phòng thủ tham chiếu", "base.reference: 5 loadout tham chiếu theo cấp HQ")
    for c in ("small", "medium", "large", "utilities"):
        dp.col(c, meaning=f"tháp ô {c} (ngăn ';')", fk=TOWER_FK)
    dp.col("he_so_do_kho", meaning="hệ số độ khó của đợt (05 / matchRules)")
    dp.col("duong_cong_dot", meaning="đường cong đợt (05 / matchRules)")
    for i, ref in enumerate(base_cfg.get("reference") or []):
        path = ("base", "reference", i)
        r = dp.row(f"hq{ref.get('level', i + 1)}", B.nguon(path), raw=ref)
        r.flatten(ref, B.BALANCE, path, aliases={"level": "cap_hq"})
        r.set("he_so_do_kho", chua_ap("xuat_luot3"))
        r.set("duong_cong_dot", chua_ap("xuat_luot3"))

    # ------------------------------------------------------------------ the AI's base building
    ai = book.sheet("Can_cu_AI_kieu", "AI xây căn cứ: trọng số", "base.ai.styles.<kiểu>.<tháp>: trọng số chọn tháp ('*' = mọi tháp khác)")
    ai.col("kieu", meaning="kiểu AI (default, armour, air, tướng...)")
    ai.col("thap", meaning="tháp (id hoặc '*')", fk=TOWER_FK)
    ai.col("trong_so", meaning="trọng số chọn")
    for style, weights in ((base_cfg.get("ai") or {}).get("styles") or {}).items():
        for tower, w in weights.items():
            path = ("base", "ai", "styles", style, tower)
            r = ai.row(f"{style}/{tower}", B.nguon(path), raw=w)
            r.set("kieu", style)
            r.set("thap", tower if tower != "*" else "")
            r.set("trong_so", w, B.BALANCE, path)
    _b04.build(ctx, book, d, res)
    _unit_settle.apply(book)
    # an empty weapon-mount child (no utility module / wall has a secondary[] in balance.json): one KHONG_CO marker row
    for name, what in (("Mo_dun_tien_ich_vu_khi", "mô-đun tiện ích"), ("Tuong_vu_khi", "loại tường")):
        sh = book.sheets.get(name)
        if sh is not None and not sh.rows:
            r = sh.row("KHONG_CO", f"{B.BALANCE}: vehicles[*].secondary (không {what} nào có)")
            r.set(sh.parent_col, "KHONG_CO")
            r.set("trang_thai", "KHONG_CO", meaning="KHONG_CO: dòng đánh dấu (sheet không có dữ liệu)")
            r.set("ghi_chu", f"không {what} nào có bệ phụ (secondary[]) trong balance.json; vũ khí chính ở sheet cha", meaning="lý do")
    al = book.kv_sheet("Can_cu_AI_cap", "AI xây căn cứ: cấp HQ theo độ khó", "base.ai.levels")
    book.kv_rows(al, (base_cfg.get("ai") or {}).get("levels") or {}, B.BALANCE, ("base", "ai", "levels"), "base.ai.levels")
