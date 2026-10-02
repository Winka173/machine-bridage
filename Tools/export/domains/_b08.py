"""08_ban_do, layer B (pass 5 part 2): Ban_do_do_tinh (the static map audit per map file: Docs/checks/map_audit.csv of
Tools/audit/map_audit.py and the warnings of Tools/maps/validate_p33.py, Docs/maps/validate_p33.json, as data; the
GREEN / YELLOW / RED status re-derived by a live formula from those numbers with the audit's thresholds; live counts of
each map's entities) and Ngan_sach_thuc_the (every entity source, long- or short-lived, its cap in the code or none, the
estimated most at once; and per mode x side the vehicle cap the game sets).

The audit numbers are not re-measured here (owner rule 30/09: no measures without the owner's word): bao_cao_cu marks a
map file changed after the report's commit."""
from __future__ import annotations

import csv
import json

from core.formula import F, lookup, q, ref as R
from core.model import NEED_CODE_CHECK
from core.repo import ROOT

from . import _layer_b as LB

AUDIT_CSV = "Docs/checks/map_audit.csv"
AUDIT = "Tools/audit/map_audit.py"
P33 = "Docs/maps/validate_p33.json"
MAPS = "Assets/MachineBrigade/Resources/Data/maps"
W05 = "05_che_do_kinh_te"
ECO = LB.SCRIPTS + "Sim/Economy/EconomySystem.cs"
TANK_RANGE, THREAT, DELTA_RED, DELTA_YELLOW, NEUTRAL_RED, NEUTRAL_YELLOW = 32.0, 40.0, 0.15, 0.10, 0.20, 0.10
MODES = ["Assault", "BossRush", "Campaign", "Conquest", "Deathmatch", "Defend", "Endless", "KingOfTheHill", "Operation",
         "Showdown", "Siege", "Survival", "Weekly"]


def _num(s):
    s = (s or "").strip()
    if s in ("", "-", "by role"):
        return ""
    try:
        return float(s[:-1]) / 100 if s.endswith("%") else float(s)
    except ValueError:
        return ""


def _pair(s, i):
    parts = (s or "").split("/")
    return _num(parts[i]) if i < len(parts) else ""


def _status(flags: str) -> str:
    return "RED" if "RED" in flags else "YELLOW" if "YELLOW" in flags else "GREEN"


def build(ctx, book):
    bd = book.sheets["Ban_do"]
    p = ROOT / AUDIT_CSV
    rows = {r["map"]: r for r in csv.DictReader(p.open(encoding="utf-8"))} if p.exists() else {}
    if not rows:
        ctx.issue(f"08 Ban_do_do_tinh: {AUDIT_CSV} missing")
    p33 = json.loads((ROOT / P33).read_text("utf-8")) if (ROOT / P33).exists() else []
    commits = LB.git_last_commit([MAPS, AUDIT_CSV])
    report_t = commits.get(AUDIT_CSV, (0, ""))

    # ------------------------------------------------------------------ Ban_do_do_tinh
    dt = book.sheet("Ban_do_do_tinh", "Bản đồ: đo tĩnh", "Mỗi file bản đồ x chỉ số đo tĩnh (Tools/audit/map_audit.py -> "
                    "Docs/checks/map_audit.csv: quãng đường bãi thả -> mục tiêu, chênh trung vị, số làn độc lập, điểm nghẽn bắt buộc / "
                    "tùy chọn, sightlineP95, vùng phủ pháo, vùng thả, khoảng lớp phòng thủ, kết nối nav) và cảnh báo của "
                    "Tools/maps/validate_p33.py; trang_thai tính lại bằng công thức từ các số đó (ngưỡng của bản kiểm); đếm thực thể "
                    "của bản đồ (COUNTIFS)", layer="B")
    dt.col("id", fk=["08_ban_do/Ban_do"], meaning="file bản đồ (Ban_do.id)")
    src = f"{AUDIT_CSV} ({AUDIT})"
    data_cols = [
        ("doi_xung", "", "symmetric (conquest / sandbox: so hai bên) / asymmetric (siege / long: theo vai)", "kind"),
        ("co_bao_cao", "", "cờ của bản kiểm (flags, nguyên văn)", "flags"),
        ("vung_nav_roi", "", "số vùng nav rời (disconnectedNavRegions)", "disconnectedNavRegions"),
        ("tiep_can_muc_tieu", "", "ok hoặc mục tiêu không tới được (objectiveReachability)", "objectiveReachability"),
        ("duong_toi_muc_tieu_0_m", "m", "trung vị đường bãi thả đội 0 -> mục tiêu (pathToObjective0)", "pathToObjective0"),
        ("duong_toi_muc_tieu_1_m", "m", "trung vị đường bãi thả đội 1 -> mục tiêu", "pathToObjective1"),
        ("chenh_trung_vi", "", "chênh trung vị đường hai bên (medianPathDelta, tỷ lệ; trống: theo vai)", "medianPathDelta"),
        ("khoang_cach_cham_tran_m", "m", "nửa đường bãi thả -> bãi thả (firstContactDistance)", "firstContactDistance"),
        ("muc_tieu_toi_muc_tieu_m", "m", "đường ngắn nhất giữa hai mục tiêu", "objectiveToObjectiveDistance"),
        ("so_lan_doc_lap", "", "số làn độc lập (independentLaneCount)", "independentLaneCount"),
        ("diem_nghen_bat_buoc", "", "điểm nghẽn bắt buộc (mandatoryChokeCount)", "mandatoryChokeCount"),
        ("diem_nghen_tuy_chon", "", "điểm nghẽn tùy chọn (optionalChokeCount)", "optionalChokeCount"),
        ("rong_hanh_lang_p10_m", "m", "bề rộng hành lang P10 (corridorWidthP10)", "corridorWidthP10"),
        ("tam_nhin_p95_m", "m", "sightlineP95", "sightlineP95"),
        ("lo_muc_tieu_p95_m", "m", "objectiveExposureP95", "objectiveExposureP95"),
        ("vung_lo_xa", "", "tỷ lệ tia dài hơn 2 x tầm pháo tăng (longRangeExposureArea)", "longRangeExposureArea"),
        ("ban_thang_toi_muc_tieu", "", "exposed: mục tiêu trong tầm pháo tăng + 40 m của một bãi thả (directFireCoverage)", "directFireCoverage"),
        ("phu_phao_0", "", "tỷ lệ nền đi được trong 120 m của bãi thả 0 (indirectFireGeometricEnvelope)", None),
        ("phu_phao_1", "", "như trên, bãi thả 1", None),
        ("vung_tha_0_m2", "m2", "diện tích đi được trong 20 m của bãi thả 0 (usableDropArea)", None),
        ("vung_tha_1_m2", "m2", "như trên, bãi thả 1", None),
        ("loi_ra_0", "", "số lối ra vòng 30 m quanh bãi thả 0 (trống: mở mọi phía)", None),
        ("loi_ra_1", "", "như trên, bãi thả 1", None),
        ("phong_thu_gan_0_m", "m", "khoảng cách phòng thủ cố định địch gần nhất tới bãi thả 0 (staticThreatDistance)", None),
        ("phong_thu_gan_1_m", "m", "như trên, bãi thả 1", None),
        ("khoang_lop_phong_thu_m", "m", "khoảng giữa hai vòng phòng thủ (defensiveLayerSpacing)", "defensiveLayerSpacing"),
        ("duong_rut_m", "m", "đường rút của bên thủ tới nhà chính (fallbackRouteLength)", "fallbackRouteLength"),
        ("tiep_vien_s", "s", "đường tiếp viện / 6,5 m/s (reinforcementTravelProxy)", None),
        ("chenh_trung_lap", "", "chênh giá trị trung lập hai bên (neutralValueDelta, tỷ lệ)", "neutralValueDelta"),
        ("canh_bao_p33", "", "số cảnh báo của validate_p33 nêu file này (Docs/maps/validate_p33.json)", None),
        ("loi_p33", "", "số lỗi của validate_p33 nêu file này", None),
        ("ket_noi_trang_thai_nav", "", "kết nối nav ở mọi trạng thái dựng sẵn: CHUA_DO (có trạng thái, chưa có báo cáo đo theo bản đồ; "
                                       "Tools/campaign/nav_states.py chạy lúc dựng chiến dịch) / KHONG_CO_TRANG_THAI", None),
        ("bao_cao_cu", "", "file bản đồ đổi sau commit của báo cáo (git): số đo có thể cũ", None),
    ]
    for c, unit, m, _k in data_cols:
        dt.col(c, unit=unit, meaning=m, source_note=src if c not in ("canh_bao_p33", "loi_p33") else P33,
               enum=["CHUA_DO", "KHONG_CO_TRANG_THAI"] if c == "ket_noi_trang_thai_nav" else None)
    sym = f"{{doi_xung}}={q('symmetric')}"
    isn = lambda e: f"ISNUMBER({e})"  # noqa: E731
    red = (f"OR({{vung_nav_roi}}>0,{{tiep_can_muc_tieu}}<>{q('ok')},AND({sym},{isn('{chenh_trung_vi}')},{{chenh_trung_vi}}>{DELTA_RED}),"
           f"AND({sym},{{so_lan_doc_lap}}<2),AND({isn('{phong_thu_gan_0_m}')},{{phong_thu_gan_0_m}}<{THREAT}),"
           f"AND({isn('{phong_thu_gan_1_m}')},{{phong_thu_gan_1_m}}<{THREAT}),AND({sym},{isn('{chenh_trung_lap}')},{{chenh_trung_lap}}>{NEUTRAL_RED}))")
    yellow = (f"OR(AND({sym},{isn('{chenh_trung_vi}')},{{chenh_trung_vi}}>{DELTA_YELLOW}),{{tam_nhin_p95_m}}>{TANK_RANGE},"
              f"AND({sym},{isn('{loi_ra_0}')},{{loi_ra_0}}<2),AND({sym},{isn('{loi_ra_1}')},{{loi_ra_1}}<2),"
              f"AND({sym},{isn('{chenh_trung_lap}')},{{chenh_trung_lap}}>{NEUTRAL_YELLOW}))")
    T = {"trang_thai": f"=IF({red},{q('RED')},IF({yellow},{q('YELLOW')},{q('GREEN')}))",
         "lech_bao_cao": f"={{trang_thai}}<>{{trang_thai_bao_cao}}"}
    dt.col("trang_thai_bao_cao", meaning="GREEN / YELLOW / RED theo cờ của bản kiểm", source_note=src, enum=["GREEN", "YELLOW", "RED"])
    LB.declare(dt, "trang_thai", T["trang_thai"], f"{AUDIT} audit() ngưỡng: chênh > 15 % RED / > 10 % YELLOW (đối xứng), < 2 làn RED, "
               f"phòng thủ < 40 m RED, tầm nhìn P95 > 32 m YELLOW, lối ra < 2 YELLOW, chênh trung lập > 20 % RED / > 10 % YELLOW",
               game=False, meaning="trạng thái tính lại từ các số đo (công thức)", enum=["GREEN", "YELLOW", "RED"])
    LB.declare(dt, "lech_bao_cao", T["lech_bao_cao"], "trang_thai <> trang_thai_bao_cao", game=False,
               meaning="TRUE: trạng thái tính lại khác cờ của báo cáo (số trong CSV đã làm tròn)")
    # counts of the map's entities (live)
    counts = {"so_quan_dat_san": ("Ban_do_quan", "ban_do_id", False, "quân đặt sẵn (units[])"),
              "so_o_can_cu": ("Ban_do_can_cu_o", "ban_do_can_cu_id", True, "ô xây của mọi căn cứ (bases[].slots[])"),
              "so_doan_tuong": ("Ban_do_tuong_doan", "ban_do_tuong_id", True, "đoạn tường (walls[].segments[])"),
              "so_o_phao_dai": ("Ban_do_phao_dai_o", "ban_do_id", False, "ô pháo đài (fortress.slots[])"),
              "so_trung_lap": ("Ban_do_trung_lap", "ban_do_id", False, "điểm trung lập (neutrals[])"),
              "so_vat_the": ("Ban_do_vat_the", "ban_do_id", False, "vật thể (props[])")}
    CT = {}
    for c, (sheet, col, nested, m) in counts.items():
        crit = f"{{id}}&{q('/*')}" if nested else "{id}"
        CT[c] = f"=COUNTIFS({R(sheet, col, '*')},{crit})"
        LB.declare(dt, c, CT[c], f"COUNTIFS trên {sheet}", game=False, meaning=f"số {m} của file bản đồ")
    nav_maps = {}
    nsh = ctx.books["07_chien_dich_cot_truyen"].sheets.get("Nhiem_vu_nav_state") if "07_chien_dich_cot_truyen" in ctx.books else None
    nvs = ctx.books["07_chien_dich_cot_truyen"].sheets.get("Nhiem_vu") if nsh is not None else None
    if nsh is not None:
        for r in nsh.rows.values():
            mr = nvs.rows.get(r.values.get(nsh.parent_col))
            if mr is not None:
                nav_maps[mr.values.get("map")] = nav_maps.get(mr.values.get("map"), 0) + 1
    child_n = {}
    for c, (sheet, col, nested, _m) in counts.items():
        n = {}
        for r in book.sheets[sheet].rows.values():
            k = str(r.values.get(col))
            k = k.split("/")[0] if nested else k
            n[k] = n.get(k, 0) + 1
        child_n[c] = n
    for mid in sorted(bd.rows, key=str):
        a = rows.get(mid)
        x = dt.row(mid, f"{AUDIT_CSV} (map = {mid}); {P33}" if a else f"{P33} (không có trong {AUDIT_CSV})")
        if a:
            for c, _u, _m, key in data_cols:
                if key is None:
                    continue
                v = a.get(key, "")
                if c in ("doi_xung", "co_bao_cao", "tiep_can_muc_tieu", "ban_thang_toi_muc_tieu"):
                    x.set(c, v)
                else:
                    x.set(c, _num(v))
            ind, area, ex, th = (a.get("indirectFireGeometricEnvelope", ""), a.get("usableDropArea", ""), a.get("exitCount", ""),
                                 a.get("staticThreatDistance", ""))
            for i in (0, 1):
                x.set(f"phu_phao_{i}", _pair(ind, i))
                x.set(f"vung_tha_{i}_m2", _pair(area, i))
                x.set(f"loi_ra_{i}", _pair(ex, i))
                x.set(f"phong_thu_gan_{i}_m", _pair(th, i))
            x.set("tiep_vien_s", _num((a.get("reinforcementTravelProxy") or "").replace(" s", "")))
            x.set("trang_thai_bao_cao", _status(a.get("flags", "")))
        stem = f"{mid}:"
        x.set("canh_bao_p33", sum(1 for c in p33 for w in c.get("warnings") or [] if w.startswith(stem)))
        x.set("loi_p33", sum(1 for c in p33 for w in c.get("errors") or [] if w.startswith(stem)))
        base = bd.rows[mid].values.get("ban_do_goc")
        x.set("ket_noi_trang_thai_nav", "CHUA_DO" if nav_maps.get(base) else "KHONG_CO_TRANG_THAI")
        mt = commits.get(f"{MAPS}/{mid}.json", (0, ""))
        x.set("bao_cao_cu", bool(a) and mt[0] > report_t[0])
        if a:
            v = {k: x.values.get(k) for k in x.values}
            s_ = v.get("doi_xung") == "symmetric"
            n_ = lambda k: v.get(k) if isinstance(v.get(k), float) else None  # noqa: E731
            is_red = ((n_("vung_nav_roi") or 0) > 0 or v.get("tiep_can_muc_tieu") != "ok" or
                      (s_ and n_("chenh_trung_vi") is not None and n_("chenh_trung_vi") > DELTA_RED) or
                      (s_ and (n_("so_lan_doc_lap") or 0) < 2) or
                      any(n_(f"phong_thu_gan_{i}_m") is not None and n_(f"phong_thu_gan_{i}_m") < THREAT for i in (0, 1)) or
                      (s_ and n_("chenh_trung_lap") is not None and n_("chenh_trung_lap") > NEUTRAL_RED))
            is_yel = ((s_ and n_("chenh_trung_vi") is not None and n_("chenh_trung_vi") > DELTA_YELLOW) or
                      (n_("tam_nhin_p95_m") or 0) > TANK_RANGE or
                      any(s_ and n_(f"loi_ra_{i}") is not None and n_(f"loi_ra_{i}") < 2 for i in (0, 1)) or
                      (s_ and n_("chenh_trung_lap") is not None and n_("chenh_trung_lap") > NEUTRAL_YELLOW))
            st = "RED" if is_red else "YELLOW" if is_yel else "GREEN"
            LB.put(x, "trang_thai", T["trang_thai"], st, game=False)
            LB.put(x, "lech_bao_cao", T["lech_bao_cao"], st != _status(a.get("flags", "")), game=False)
        for c in counts:
            LB.put(x, c, CT[c], float(child_n[c].get(str(mid), 0)), game=False)

    # ------------------------------------------------------------------ input_kinh_te (05)
    kt = ctx.books[W05].sheets["Kinh_te"]
    caps = {rid: {"gia_tri_so": r.values.get("gia_tri_so")} for rid, r in kt.rows.items() if str(rid).startswith("economy.vehicleCap.")}
    LB.input_sheet(ctx, book, "input_kinh_te", "Input: trần xe (từ 05)", W05, "Kinh_te",
                   [("gia_tri_so", "gia_tri_so", "", "economy.vehicleCap.<chế độ>: số xe tối đa của địch")], caps)

    # ------------------------------------------------------------------ Ngan_sach_thuc_the
    ns = book.sheet("Ngan_sach_thuc_the", "Ngân sách thực thể", "Mỗi nguồn thực thể: sống lâu (xe, máy bay, tháp, tường, vật thể) / ngắn "
                    "hạn (lửa, khói, tia, vòm); mô phỏng hay chỉ hình; đã có giới hạn trong mã hay chưa; ước tính tối đa cùng lúc "
                    "(giới hạn, hoặc nhiều nhất trên một file bản đồ)", layer="B")
    for c, m, en in (("loai_song", "song_lau / ngan_han", ["song_lau", "ngan_han"]),
                     ("lop", "mo_phong (Sim, ảnh hưởng lối chơi) / hien_thi (chỉ hình)", ["mo_phong", "hien_thi"]),
                     ("pham_vi", "moi_phe / toan_tran / moi_ban_do", ["moi_phe", "toan_tran", "moi_ban_do"]),
                     ("gioi_han_ma", "giới hạn trong mã (trống: chưa có giới hạn)", None),
                     ("dem_ban_do", "cột đếm của Ban_do_do_tinh dùng khi chưa có giới hạn", None),
                     ("ghi_chu", "ghi chú", None), ("nguon_ma", "file:dòng của giới hạn", None)):
        ns.col(c, meaning=m, enum=en, source_note="C#" if c in ("gioi_han_ma", "nguon_ma") else "")
    NT = {"co_gioi_han": "=ISNUMBER({gioi_han_ma})"}
    sources = [
        ("xe_nguoi_choi", "song_lau", "mo_phong", "moi_phe", (ECO, r"public const int MaxVehicles = (\d+)"), "", "TeamEconomy.MaxVehicles (người chơi giữ mức này)"),
        ("xe_dich", "song_lau", "mo_phong", "moi_phe", None, "", "economy.vehicleCap (input_kinh_te): lớn nhất của các chế độ; theo chế độ ở Ngan_sach_thuc_the_che_do"),
        ("may_bay", "song_lau", "mo_phong", "moi_phe", (ECO, r"public const int MaxAircraft = (\d+)"), "", "TeamEconomy.MaxAircraft, + 1 mỗi bãi đáp nhánh hangar, + commander (nằm trong trần xe)"),
        ("xe_sandbox", "song_lau", "mo_phong", "moi_phe", (LB.SCRIPTS + "Sim/Sandbox/SandboxRules.cs", r"public const int VehicleCap = (\d+)"), "", "Sandbox"),
        ("may_bay_sandbox", "song_lau", "mo_phong", "moi_phe", (LB.SCRIPTS + "Sim/Sandbox/SandboxRules.cs", r"AircraftCap = (\d+)"), "", "Sandbox"),
        ("quan_dat_san", "song_lau", "mo_phong", "moi_ban_do", None, "so_quan_dat_san", "quân đặt sẵn của file bản đồ (không có trần riêng)"),
        ("o_can_cu", "song_lau", "mo_phong", "moi_ban_do", None, "so_o_can_cu", "tháp / công trình: ô xây của các căn cứ (mỗi ô tối đa một)"),
        ("doan_tuong", "song_lau", "mo_phong", "moi_ban_do", None, "so_doan_tuong", "đoạn tường của các tuyến tường"),
        ("o_phao_dai", "song_lau", "mo_phong", "moi_ban_do", None, "so_o_phao_dai", "ô pháo đài nhiều lớp"),
        ("trung_lap", "song_lau", "mo_phong", "moi_ban_do", None, "so_trung_lap", "điểm trung lập"),
        ("vat_the", "song_lau", "mo_phong", "moi_ban_do", None, "so_vat_the", "vật thể phá được / chặn đường"),
        ("dan_bay", "ngan_han", "mo_phong", "toan_tran", None, "", "đạn đang bay: không tìm thấy giới hạn trong Sim/Combat (theo số xe và nhịp bắn)"),
        ("nhat_ky_ai", "ngan_han", "mo_phong", "toan_tran", (LB.SCRIPTS + "Sim/AI/DecisionLog.cs", r"public const int Capacity = (\d+)"), "", "mục nhật ký quyết định AI giữ lại"),
        ("lua_chay", "ngan_han", "hien_thi", "toan_tran", (LB.SCRIPTS + "Game/Effects/FireSpots.cs", r"const int MaxFires = (\d+)"), "", "đốm lửa trên nền"),
        ("lua_ngan_sach", "ngan_han", "hien_thi", "toan_tran", (LB.SCRIPTS + "Game/Effects/FireBudget.cs", r"public const int Cap = (\d+)"), "", "lửa lớn cùng lúc (máy yếu LowCap)"),
        ("khoi_lon", "ngan_han", "hien_thi", "toan_tran", (LB.SCRIPTS + "Game/Effects/ImpactSmoke.cs", r"public const int BigColumns = (\d+)"), "", "cột khói lớn cùng lúc (spec 09: tối đa 3)"),
        ("tia_laser", "ngan_han", "hien_thi", "toan_tran", (LB.SCRIPTS + "Game/Effects/LaserBeams.cs", r"const int Capacity = (\d+)"), "", "tia laser cùng lúc"),
        ("duong_ngam", "ngan_han", "hien_thi", "toan_tran", (LB.SCRIPTS + "Game/Effects/AimLines.cs", r"const int Count = (\d+)"), "", "đường ngắm"),
        ("den_nhiet", "ngan_han", "hien_thi", "toan_tran", (LB.SCRIPTS + "Game/Effects/HeatLights.cs", r"public const int Max = (\d+)"), "", "đèn nhiệt (máy yếu LowMax)"),
        ("vom_khien_vat_pham", "ngan_han", "hien_thi", "toan_tran", (LB.SCRIPTS + "Game/Effects/EffectsDirector.Shields.cs", r"const int MaxItemDomes = (\d+)"), "", "vòm khiên vật phẩm"),
    ]
    rows_out = []
    for rid, life, layer, scope, cs, count_col, note in sources:
        x = ns.row(rid, "C#: " + (LB.short(cs[0]) if cs else "") + (f"; 08/Ban_do_do_tinh.{count_col}" if count_col else ""))
        for c, v in (("loai_song", life), ("lop", layer), ("pham_vi", scope), ("dem_ban_do", count_col), ("ghi_chu", note)):
            x.set(c, v)
        cap, cite = "", ""
        if cs:
            cap, cite = LB.cs_num(ctx, cs[0], cs[1], what=rid)
        if rid == "xe_dich":
            vals = [v["gia_tri_so"] for v in caps.values() if isinstance(v["gia_tri_so"], (int, float))]
            cap = float(max(vals)) if vals else ""
            x.set("gioi_han_ma", F("=MAX(" + R("input_kinh_te", "gia_tri_so", "*") + ")", expect=cap, ref="python: max(vehicleCap)"))
        else:
            x.set("gioi_han_ma", cap)
        x.set("nguon_ma", cite)
        rows_out.append((x, cap, count_col))
    LB.declare(ns, "co_gioi_han", NT["co_gioi_han"], "ISNUMBER(gioi_han_ma)", game=False, meaning="đã có giới hạn trong mã")
    LB.declare(ns, "uoc_tinh_toi_da", "=IF({co_gioi_han},{gioi_han_ma},MAX(<Ban_do_do_tinh.cột đếm>))", "giới hạn hoặc nhiều nhất trên một file bản đồ",
               game=False, meaning="ước tính tối đa cùng lúc (theo phạm vi)")
    for x, cap, count_col in rows_out:
        has = isinstance(cap, float)
        LB.put(x, "co_gioi_han", NT["co_gioi_han"], has, game=False)
        if has:
            est = cap
            t = "={gioi_han_ma}"
        elif count_col:
            vals = [LB.F_value(r.values.get(count_col)) for r in dt.rows.values()]
            est = max(v for v in vals if isinstance(v, float)) if vals else ""
            t = f"=MAX({R('Ban_do_do_tinh', count_col, '*')})"
        else:
            est, t = "", f"={q('')}"
        LB.put(x, "uoc_tinh_toi_da", t, est, game=False)

    # ------------------------------------------------------------------ Ngan_sach_thuc_the_che_do
    nc = book.sheet("Ngan_sach_thuc_the_che_do", "Ngân sách thực thể theo chế độ", "Mỗi chế độ x phe: số xe tối đa game đặt "
                    "(SimWorld.EnableEconomy: phe địch Catalog.VehicleCapFor(chế độ), người chơi TeamEconomy.MaxVehicles), máy bay "
                    "tối đa (trong trần xe), ước tính thực thể sống lâu (xe + ô căn cứ + quân đặt sẵn nhiều nhất trên một bản đồ)", layer="B")
    nc.col("che_do", meaning="chế độ (GameModeKind)")
    nc.col("phe", meaning="nguoi_choi (đội 0) / dich (đội 1)", enum=["nguoi_choi", "dich"])
    inp = R("input_kinh_te", "id", "*")
    NC = {
        "xe_toi_da": (f"=IF({{phe}}={q('nguoi_choi')},{R('Ngan_sach_thuc_the', 'gioi_han_ma', 'xe_nguoi_choi')},"
                      f"IF(COUNTIFS({inp},{q('economy.vehicleCap.')}&{{che_do}})>0,{lookup('input_kinh_te', 'gia_tri_so', q('economy.vehicleCap.') + '&{che_do}')},"
                      f"IF(COUNTIFS({inp},{q('economy.vehicleCap.default')})>0,{lookup('input_kinh_te', 'gia_tri_so', q('economy.vehicleCap.default'))},"
                      f"{R('Ngan_sach_thuc_the', 'gioi_han_ma', 'xe_nguoi_choi')})))"),
        "may_bay_toi_da": f"=MIN({{xe_toi_da}},{R('Ngan_sach_thuc_the', 'gioi_han_ma', 'may_bay')})",
        "uoc_tinh_song_lau": (f"={{xe_toi_da}}+{R('Ngan_sach_thuc_the', 'uoc_tinh_toi_da', 'o_can_cu')}+"
                              f"{R('Ngan_sach_thuc_the', 'uoc_tinh_toi_da', 'quan_dat_san')}"),
    }
    LB.declare(nc, "xe_toi_da", NC["xe_toi_da"], "Sim/SimWorld.cs EnableEconomy + Sim/Content/Catalog.cs VehicleCapFor", meaning="số xe tối đa của phe (trên sân + đang tới)")
    LB.declare(nc, "may_bay_toi_da", NC["may_bay_toi_da"], "TeamEconomy.MaxAircraft (không tính bãi đáp hangar, commander)", game=False,
               meaning="máy bay tối đa (nằm trong trần xe)")
    LB.declare(nc, "uoc_tinh_song_lau", NC["uoc_tinh_song_lau"], "xe + ô căn cứ + quân đặt sẵn (nhiều nhất trên một bản đồ)", game=False,
               meaning="ước tính thực thể sống lâu tối đa của phe (thô: ô căn cứ và quân đặt sẵn của cả bản đồ)")
    vc = {k[len("economy.vehicleCap."):]: v["gia_tri_so"] for k, v in caps.items()}
    pc = LB.F_value(ns.rows["xe_nguoi_choi"].values.get("gioi_han_ma"))
    ac = LB.F_value(ns.rows["may_bay"].values.get("gioi_han_ma"))
    oc = LB.F_value(ns.rows["o_can_cu"].values.get("uoc_tinh_toi_da"))
    qc = LB.F_value(ns.rows["quan_dat_san"].values.get("uoc_tinh_toi_da"))
    for m in MODES:
        for side in ("nguoi_choi", "dich"):
            x = nc.row(f"{m}/{side}", f"{LB.short(LB.SCRIPTS + 'Sim/SimWorld.cs')} EnableEconomy; input_kinh_te")
            x.set("che_do", m)
            x.set("phe", side)
            if not isinstance(pc, float):
                cap = NEED_CODE_CHECK
            elif side == "nguoi_choi":
                cap = pc
            else:
                cap = float(vc.get(m, vc.get("default", pc)))
            LB.put(x, "xe_toi_da", NC["xe_toi_da"], cap)
            LB.put(x, "may_bay_toi_da", NC["may_bay_toi_da"], min(cap, ac) if isinstance(cap, float) and isinstance(ac, float) else "", game=False)
            tot = cap + oc + qc if all(isinstance(v, float) for v in (cap, oc, qc)) else ""
            LB.put(x, "uoc_tinh_song_lau", NC["uoc_tinh_song_lau"], tot, game=False)
