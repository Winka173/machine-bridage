"""The bomb sheets of 01_chien_dau (Bom_vu_khi, Bom_don_vi, Bom_hanh_vi, Bom_canh_bao): per bomb weapon its stick
parameters (weapons[*].stick), the carriers, the warning rings the rules draw, the code path of the drop.

Built from the export's own sheets once the formulas are evaluated (core/pack.py add_bom_sheets); read only. The drop
traces a Unity test writes are measurements, not data, and are not part of the pack.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from core import repo
from core.model import NEED_CODE_CHECK

BALANCE = "Assets/MachineBrigade/Resources/Data/balance.json"
BOMB_GRAVITY = 40.0  # CombatSystem.Bombs.cs:25
FREE_FALL_SCATTER = 0.5  # CombatSystem.Bombs.cs:28
C = "Assets/MachineBrigade/Scripts/Sim/"
# The bomb-run fix, pass 1: the stick parameters of the spec, one column each (balance.json weapons[*].stick key; the
# supports' and the bosses' strips have no "stick" block: their columns are worked out from their own data).
STICK_COLS = [
    ("che_do_tha", "mode", "POINT / STICK / PATTERN"),
    ("cach_tha", "drop", "OVERFLY (máy bay bay qua, bom rơi tự do) / BAY (khoang bom boss: dải đặt quanh điểm nhắm)"),
    ("so_bom_dai_n", "bombs", "số bom một lần thả (n; = burst)"),
    ("khoang_cach_giua_bom_m", "spacing", "spacing = 1,1 × lõi (0,8–1,5 × lõi)"),
    ("do_dai_dai_m", "length", "(n − 1) × spacing; trần 120 m (boss 140 m)"),
    ("chu_ky_tha_giua_bom_s", "interval", "spacing / tốc độ lúc thả"),
    ("toc_do_bay_luc_tha_m_s", "releaseSpeed", "tốc độ máy bay lúc thả (ga 0,8 khi vào; boss: tốc độ danh nghĩa của khoang = spacing / chu kỳ)"),
    ("thoi_gian_roi_s", "fallTime", "√(2 × độ cao / 40)"),
    ("khoang_dan_dau_m", "lead", "tốc độ × thời gian rơi (thả trước để quả đầu rơi đầu dải); BAY và dẫn đường: 0"),
    ("huong_ra_tham", "heading", "APPROACH / AXIS (trục chính cụm mục tiêu trong ±45°)"),
    ("tam_dai", "anchor", "START / CENTER"),
    ("lech_ngang_m", "jitterAcross", "± theo seed, 0,25 × lõi"),
    ("lech_doc_m", "jitterAlong", "± theo seed, 0,15 × spacing"),
    ("ty_le_chong_lan", "overlap", "lõi / spacing (mục tiêu 0,8–1,2)"),
    ("do_rong_dai_m", "width", "2 × rìa + 2 × lệch ngang"),
    ("so_muc_tieu_toi_thieu", "minTargets", "ít hơn thì thả max(2, ceil(n/3)) quả (0: không áp)"),
    ("so_bom_khi_it_muc_tieu", None, "max(2, ceil(n/3)) (dải STICK có minTargets)"),
    ("khoang_cach_an_toan_m", "safety", "max(lõi, 8): mỗi quả tự kiểm tra, quả rơi gần quân ta bị bỏ"),
    ("thoi_gian_bay_thang_s", "straightTime", "độ dài / tốc độ + thời gian rơi + 1 s (và ≥ 40 m sau quả cuối); 0: không giữ"),
    ("khoang_thoat_m", "exit", "bay thẳng ≥ 40 m sau quả cuối rồi mới vòng"),
    ("thoi_gian_mo_khoang_bom_s", "bayOpen", "hình ảnh"),
    ("canh_bao_dang", "warnShape", "STICK_RECT (≥ 400 kg và boss) / RING / NONE"),
]


def stick_of(w: dict, vk: dict) -> dict:
    """The weapon's "stick" block from its raw json (or its parent's through inherits), {} without one."""
    seen = set()
    while w and id(w) not in seen:
        seen.add(id(w))
        try:
            raw = json.loads(w.get("raw_json") or "{}")
        except (TypeError, ValueError):
            raw = {}
        if isinstance(raw.get("stick"), dict):
            return raw["stick"]
        w = vk.get(str(w.get("ke_thua_tu") or ""), {})
    return {}


def stick_values(st: dict) -> dict:
    out = {}
    for col, key, _m in STICK_COLS:
        if key is None:
            continue
        v = st.get(key, "")
        out[col] = v if v != "" else ""
    n = int(fnum(st.get("bombs"), 1)) if st else 0
    out["so_bom_khi_it_muc_tieu"] = (min(n, max(2, -(-n // 3))) if st.get("mode") == "STICK" and fnum(st.get("minTargets")) > 0
                                     and n > 1 else "")
    return out


def strip_stick(n: int, length: float, core: float, edge: float, dur: float, lateral: float, centre: bool) -> dict:
    """A support's airstrike or a boss strip as stick columns (their code lays the line; nothing here is data)."""
    spacing = (length / (n - 1) if centre is False else length / n) if n > 1 and length else 0.0
    interval = dur / (n - 1) if n > 1 else 0.0
    speed = spacing / interval if interval else 0.0
    return {"che_do_tha": "STICK", "cach_tha": "OVERFLY" if not centre else "BAY", "so_bom_dai_n": n,
            "khoang_cach_giua_bom_m": r3(spacing), "do_dai_dai_m": r3(spacing * (n - 1)), "chu_ky_tha_giua_bom_s": r3(interval),
            "toc_do_bay_luc_tha_m_s": r3(speed), "thoi_gian_roi_s": "", "khoang_dan_dau_m": "",
            "huong_ra_tham": "APPROACH (hướng người chơi kéo)" if not centre else "APPROACH (hướng boss)",
            "tam_dai": "START (Point = đầu dải)" if not centre else "CENTER", "lech_ngang_m": r3(lateral), "lech_doc_m": 0,
            "ty_le_chong_lan": r3(core / spacing) if spacing else "", "do_rong_dai_m": r3(2 * max(edge, core) + 2 * lateral),
            "so_muc_tieu_toi_thieu": 0, "so_bom_khi_it_muc_tieu": "", "khoang_cach_an_toan_m": "",
            "thoi_gian_bay_thang_s": "", "khoang_thoat_m": "", "thoi_gian_mo_khoang_bom_s": "",
            "canh_bao_dang": "STICK_RECT"}


# ---------------------------------------------------------------------------------------------------------- helpers
def rel(p: Path) -> str:
    try:
        return repo.rel(p)
    except ValueError:
        return p.as_posix()


def num(v):
    """A csv cell as a number when it is one (numbers stay numbers), else the text ('' for empty)."""
    if v is None:
        return ""
    if isinstance(v, (int, float)):
        return v
    s = str(v).strip()
    if s == "":
        return ""
    try:
        f = float(s)
    except ValueError:
        return s
    return int(f) if f.is_integer() and "." not in s and "e" not in s.lower() else f


def fnum(v, default=0.0) -> float:
    v = num(v)
    return float(v) if isinstance(v, (int, float)) else default


def r3(x: float) -> float:
    return round(float(x), 3)


def table(ctx, fid: str, sheet: str) -> tuple[list[str], dict[str, dict]]:
    fid, sheet = getattr(ctx, "sheet_map", {}).get((fid, sheet), (fid, sheet))
    header, rows = ctx.books[fid].sheets[sheet].table(values=True)
    return header, {str(r[0]): dict(zip(header, r)) for r in rows}


def warn_seconds(core: float, tier: int) -> float:
    """WarningRules.Seconds for a T4 / T5 round (Content/WeaponDef.P34.cs:56-64, data warningRules): max(floor, 0.5 + core / 4.5), at most 6."""
    floor = 4.0 if tier >= 5 else 2.5
    return min(6.0, max(floor, 0.5 + core / 4.5))


# ---------------------------------------------------------------------------------------------------------- weapons
def bomb_weapons(vk: dict[str, dict]) -> list[str]:
    """The unit weapons that drop bombs: fired as bombs, or data family "bomb" (a boss's bomb-bay stick flies as a shell),
    and what inherits from one; not the car bomb's charge (form CarBomb)."""
    out = []
    for wid, w in vk.items():
        fam = w.get("family") or ""
        parent = vk.get(str(w.get("ke_thua_tu") or w.get("inherits") or ""), {})
        is_bomb = w.get("dang_dan") == "Bomb" or fam == "bomb" or (not fam and parent.get("family") == "bomb")
        if is_bomb and w.get("form") != "CarBomb":
            out.append(wid)
    return sorted(out)


def code_path(w: dict, stick: dict | None = None) -> str:
    """How CombatSystem.Launch aims it (CombatSystem.Bombs.cs FreeFall, BayStick, Sticks; Definitions.cs GuidedBomb)."""
    guided = str(w.get("guided")).upper() == "TRUE" or w.get("form") in ("GuidedBomb",)
    stick = stick or {}
    laid = stick.get("mode") == "STICK" and fnum(stick.get("bombs"), 1) > 1
    if w.get("dang_dan") != "Bomb":
        return "SHELL_PATH"
    if str(w.get("glides")).upper() == "TRUE":
        return "GLIDE"
    if guided:
        return "GUIDED"
    if laid and stick.get("drop") == "BAY":
        return "BAY_STICK"
    return "FREE_FALL_STICK" if laid else "FREE_FALL"


def current_mode(path: str) -> str:
    return {
        "FREE_FALL": "POINT (một quả rơi tự do: BombImpact + tản 0,5 × spread)",
        "FREE_FALL_STICK": "STICK (quả i = đầu dải + hướng × i × spacing + lệch seed; đầu dải = máy bay lúc thả + khoảng dẫn đầu)",
        "BAY_STICK": "STICK (khoang bom boss, dải đặt quanh điểm nhắm theo trục cụm mục tiêu; mỗi quả một điểm riêng)",
        "GUIDED": "POINT (mọi quả nhắm vào mục tiêu)",
        "GLIDE": "POINT (bom lượn bay tới mục tiêu)",
        "SHELL_PATH": "POINT (bắn như đạn pháo: mọi quả nhắm vào mục tiêu, chỉ lệch theo độ tản)",
    }[path]


# ---------------------------------------------------------------------------------------------------------- sheets
def sheet_vu_khi(vk_header, vk, wids, carriers, sup, big, big_strikes, units):
    extra = ["duong_tha_theo_ma", "che_do_tha_hien_tai", "so_bom_moi_luot", "khoang_tha_giua_bom_s", "don_vi_mang",
             "toc_do_don_vi_mang_m_s", "khoang_cach_giua_bom_m_toan_toc", "khoang_cach_giua_bom_m_ga_0_8",
             "do_dai_dai_m_toan_toc", "ty_le_chong_lan_loi_tren_khoang", "canh_bao_theo_luat", "thoi_gian_canh_bao_s_theo_luat"]
    extra += [c for c, _k, _m in STICK_COLS]
    base = [c for c in vk_header if c not in ("id", "nguon", "raw_json")]
    header = ["id", "nhom"] + base + extra + ["nguon", "raw_json"]
    rows = []
    for wid in wids:
        w = vk[wid]
        path = code_path(w, stick_of(w, vk))
        burst = int(fnum(w.get("so_phat_moi_loat"), 1)) or 1
        gap = fnum(w.get("khoang_phat_trong_loat_s"), 0.1)
        core = fnum(w.get("loi_m"))
        mounts = carriers.get(wid, [])
        speeds = [fnum(units[u].get("toc_do_m_s")) for u in mounts if u in units]
        speed = speeds[0] if speeds else 0.0
        spacing = speed * gap if path.startswith("FREE_FALL") else 0.0  # pass 0's speed x burstInterval (before the fix)
        size = fnum(w.get("dau_no_kg")) or fnum(w.get("co_mm"))
        guided = path in ("GUIDED", "GLIDE")
        tier = int(fnum(w.get("bac_co"), -1)) if isinstance(num(w.get("bac_co")), (int, float)) else -1
        warns = (not guided and core > 0 and (tier >= 4 if tier >= 0 else
                 (size >= 400 if w.get("dang_dan") == "Bomb" else size >= 203)))
        vals = {c: num(w.get(c)) for c in base}
        vals.update({
            "id": wid, "nhom": "vu_khi_don_vi", "duong_tha_theo_ma": path, "che_do_tha_hien_tai": current_mode(path),
            "so_bom_moi_luot": burst, "khoang_tha_giua_bom_s": gap if burst > 1 else "",
            "don_vi_mang": ";".join(mounts), "toc_do_don_vi_mang_m_s": ";".join(f"{s:g}" for s in speeds),
            "khoang_cach_giua_bom_m_toan_toc": r3(spacing) if burst > 1 and spacing else "",
            "khoang_cach_giua_bom_m_ga_0_8": r3(spacing * 0.8) if burst > 1 and spacing else "",
            "do_dai_dai_m_toan_toc": r3((burst - 1) * spacing) if burst > 1 and spacing else "",
            "ty_le_chong_lan_loi_tren_khoang": r3(core / spacing) if burst > 1 and spacing else "",
            "canh_bao_theo_luat": "TRUE" if warns else "FALSE",
            "thoi_gian_canh_bao_s_theo_luat": r3(warn_seconds(core, tier)) if warns else 0,
            "nguon": w.get("nguon", ""), "raw_json": w.get("raw_json", ""),
        })
        vals.update(stick_values(stick_of(w, vk)))
        rows.append([vals.get(c, "") for c in header])
    for sid, s in sup.items():
        count = int(fnum(s.get("count"), 1))
        dur = fnum(s.get("duration_s"))
        length = fnum(s.get("length_m"))
        core = fnum(s.get("blast_m"))
        gap = dur / (count - 1) if count > 1 else 0.0
        spacing = length / (count - 1) if count > 1 and length else 0.0
        kind = s.get("kind")
        mode = ("STICK (rải đều Point → Point + hướng × length; StrikeSystem.cs:250-275)" if kind == "Airstrike" else
                "POINT (bom lượn tầm xa, mỗi quả lệch ít; StrikeSystem.cs:278-300)" if kind == "CruiseMissile" else
                "HOMING (bom con tự tìm xe trong bán kính)")
        vals = {"id": sid, "nhom": "the_ho_tro", "ten_that": s.get("ten_vi") or s.get("ten_en"),
                "loai_sat_thuong": s.get("damage_type") or NEED_CODE_CHECK, "sat_thuong_moi_phat": num(s.get("damage")),
                "loi_m": core, "ria_m": NEED_CODE_CHECK, "so_phat_moi_loat": count,
                "khoang_phat_trong_loat_s": r3(gap) if gap else "", "thoi_gian_nap_s": num(s.get("cooldown_s")),
                "xuyen": num(s.get("pen")), "bac_no": s.get("tier", ""),
                "duong_tha_theo_ma": "SUPPORT_" + str(kind).upper(), "che_do_tha_hien_tai": mode, "so_bom_moi_luot": count,
                "khoang_tha_giua_bom_s": r3(gap) if gap else "", "don_vi_mang": "(máy bay của thẻ, không là đơn vị)",
                "toc_do_don_vi_mang_m_s": r3(length / max(0.2, dur)) if kind == "Airstrike" and length else "",
                "khoang_cach_giua_bom_m_toan_toc": r3(spacing) if spacing else "",
                "do_dai_dai_m_toan_toc": length if length else "",
                "ty_le_chong_lan_loi_tren_khoang": r3(core / spacing) if spacing else "",
                "canh_bao_theo_luat": "TRUE (vòng / dải hỗ trợ)", "thoi_gian_canh_bao_s_theo_luat": num(s.get("delay_s")),
                "nguon": s.get("nguon", ""), "raw_json": s.get("raw_json", "")}
        if kind == "Airstrike" and count > 1:
            vals.update(strip_stick(count, length, core, core, dur, 0.5 * fnum(s.get("radius_m")), False))
        rows.append([vals.get(c, "") for c in header])
    for bid, b in big.items():
        st = big_strikes[bid]
        count = int(fnum(st.get("count"), 1))
        length = fnum(st.get("length_m"))
        core = fnum(st.get("radius_m"))
        dur = fnum(st.get("duration_s"))
        spacing = length / count if count and length else 0.0
        strip = st.get("shape") == "strip"
        vals = {"id": bid, "nhom": "sieu_vu_khi_boss", "ten_that": st.get("weapon") or "",
                "loai_sat_thuong": st.get("type", ""), "sat_thuong_moi_phat": num(st.get("damage")), "loi_m": core,
                "ria_m": NEED_CODE_CHECK, "so_phat_moi_loat": count, "thoi_gian_nap_s": num(b.get("cooldown_s")),
                "xuyen": num(st.get("pen")),
                "duong_tha_theo_ma": "BOSS_" + str(st.get("shape")).upper(),
                "che_do_tha_hien_tai": ("STICK (n quả cách đều L/n dọc hướng boss; BossSystem.BigAttacks.cs:708-720)" if strip
                                        else "POINT (một quả lớn bay như tên lửa)"),
                "so_bom_moi_luot": count, "khoang_tha_giua_bom_s": r3(dur / (count - 1)) if strip and count > 1 else "",
                "don_vi_mang": b.get("dung_boi", ""), "khoang_cach_giua_bom_m_toan_toc": r3(spacing) if strip else "",
                "do_dai_dai_m_toan_toc": length if strip else "",
                "ty_le_chong_lan_loi_tren_khoang": r3(core / spacing) if strip and spacing else "",
                "canh_bao_theo_luat": "TRUE (siêu vũ khí)", "thoi_gian_canh_bao_s_theo_luat": num(b.get("warn_s")),
                "nguon": f"{b.get('nguon', '')}; {st.get('nguon', '')}", "raw_json": st.get("raw_json", "")}
        if strip and count > 1:
            vals.update(strip_stick(count, length, core, min(20.0, core * 2.0), dur,
                                    0.35 * fnum(st.get("width_m")), True))
        rows.append([vals.get(c, "") for c in header])
    return header, rows


def sheet_don_vi(units, carriers, vk, sup, big, big_strikes):
    header = ["id", "loai", "lop", "toc_do_m_s", "xoay_than_deg_s", "ban_kinh_quay_m", "do_cao_tha_m", "canh_co_dinh",
              "vu_khi_bom", "so_bom_moi_luot", "bang_dan_qua", "nap_lai_s", "cach_nap", "thoi_gian_roi_s_theo_ma",
              "khoang_dan_dau_m_theo_ma", "cach_chon_muc_tieu", "cach_vong_cho", "nguon", "raw_json"]
    by_unit: dict[str, list[str]] = {}
    for wid, us in carriers.items():
        for u in us:
            by_unit.setdefault(u, []).append(wid)
    rows = []
    for uid in sorted(by_unit):
        u = units.get(uid)
        wids = sorted(by_unit[uid])
        if u is None:
            rows.append([uid, "KHONG_CO", "", "", "", "", "", "", ";".join(wids)] + [""] * (len(header) - 11) + ["", ""])
            continue
        speed = fnum(u.get("toc_do_m_s"))
        turn = fnum(u.get("xoay_than_deg_s"))
        alt = fnum(u.get("do_cao_m"))
        flying = str(u.get("bay")).upper() == "TRUE" or alt > 0
        fall = math.sqrt(2 * max(4.0, alt) / BOMB_GRAVITY) if flying else 0.0
        main = u.get("vu_khi_chinh") or ""
        main_stick = main in wids and fnum(vk.get(main, {}).get("so_phat_moi_loat"), 1) > 1
        fixed = str(u.get("fixed_wing")).upper() == "TRUE"
        loads = [str(int(fnum(vk[w].get("bang_dan")))) if fnum(vk[w].get("bang_dan")) else "∞" for w in wids]
        rows.append([
            uid, u.get("_loai", "xe"), u.get("lop") or u.get("class") or "", speed, turn,
            r3(speed / math.radians(turn)) if turn else "", alt, "TRUE" if fixed else "FALSE", ";".join(wids),
            ";".join(str(num(vk[w].get("so_phat_moi_loat"))) for w in wids), ";".join(loads),
            num(u.get("rearm_time_s")) if u.get("rearm_time_s") not in (None, "") else NEED_CODE_CHECK,
            ("kho bom (load) tiêu theo loạt, hết thì về nạp ở vùng nạp (rearm; Catalog.cs:106-113)" if any(l != "∞" for l in loads)
             else "theo thời gian nạp của vũ khí (cooldown)"),
            r3(fall) if flying else "", r3(speed * fall) if flying else "",
            ("BombTarget: nhóm / công trình đáng ném nhất trong max(tầm nhìn, 60 m) (MovementSystem.cs:402-404, 433)"
             if fixed and main_stick else "kẻ địch gần nhất trong tầm (MovementSystem.cs:404-405)"),
            ("bay thẳng vào mục tiêu; qua mục tiêu thì kéo thẳng toàn lực (RunExtending), xa quá max(0,85×tầm, 2,2×bán kính quay) thì quay lại (MovementSystem.cs:932-941)"
             + ("; glide bomber quay đi trước khi tới mục tiêu (MovementSystem.P25A.cs:17-23)" if str(u.get("glide_release")).upper() == "TRUE" else "")
             if fixed else "boss / trực thăng: đi theo đường của nó, bắn khi trong tầm"),
            u.get("nguon", ""), u.get("raw_json", ""),
        ])
    for sid, s in sup.items():
        length, dur = fnum(s.get("length_m")), fnum(s.get("duration_s"))
        rows.append([sid, "the_ho_tro", s.get("kind", ""), r3(length / max(0.2, dur)) if length else "", "", "", NEED_CODE_CHECK,
                     "TRUE", sid, num(s.get("count")), "", num(s.get("cooldown_s")), "thẻ: hồi chiêu (cooldown) sau mỗi lần gọi",
                     "", "", "điểm người chơi chọn (Point) và hướng kéo (Point2) (StrikeSystem.cs:150-167)",
                     "một lần bay qua, không vòng lại", s.get("nguon", ""), s.get("raw_json", "")])
    for bid, b in big.items():
        st = big_strikes[bid]
        for uid in str(b.get("dung_boi", "")).split(";"):
            u = units.get(uid, {})
            rows.append([f"{uid}|{bid}", "boss_sieu_vu_khi", st.get("shape", ""), num(u.get("toc_do_m_s")), num(u.get("xoay_than_deg_s")),
                         "", num(u.get("do_cao_m")), "", bid, num(st.get("count")), "", num(b.get("cooldown_s")),
                         "siêu vũ khí theo chu kỳ (cooldown); phá bộ phận mang thì mất / giảm", "", "",
                         f"aim {b.get('aim', '')}, target {b.get('target', '')}, reach {b.get('reach_m', '')} m (BossSystem.BigAttacks.cs)",
                         "boss dừng khi cảnh báo nếu halt" if b.get("halt_s") not in (None, "") else "boss giữ đường đi",
                         b.get("nguon", ""), b.get("raw_json", "")])
    return header, rows


def sheet_hanh_vi():
    header = ["id", "buoc", "mo_ta_theo_ma", "file_ham", "ap_dung_cho", "nguon"]
    B = C + "Combat/CombatSystem.Bombs.cs"
    S = C + "Combat/CombatSystem.cs"
    M = C + "Movement/MovementSystem.cs"
    items = [
        ("chon_muc_tieu", "Máy bay cánh cố định có vũ khí CHÍNH là bom và burst > 1 chọn mục tiêu bằng BombTarget: xe mặt đất địch nhìn thấy trong max(tầm nhìn, 60 m), điểm = BombWorth (cụm, công trình; trừ nơi vừa ném) × √clamp(Worth, 2, 25) / (1 + d/200). Đơn vị khác (bom là vũ khí phụ, boss): kẻ địch gần nhất trong tầm.",
         f"{M}:402-404 Think; {M}:433 BombTarget; {S}:406 BombWorth", "heavy_bomber (bomber_payload); các đơn vị khác theo luật thường"),
        ("huong_vao", "Máy bay quay mũi vào mục tiêu (goal = target.Position). Lượt 2: dải có heading AXIS (bomber_payload) khi còn xa thì bay tới điểm vào trên trục chính của cụm mục tiêu (StickEntry: phía sau mục tiêu một khoảng dẫn đầu + nửa dải + bán kính quay; trục trong ±45° so với hướng vào, không thì giữ hướng vào), rồi mới vào mục tiêu. Hướng dải = hướng mũi lúc thả.",
         f"{M} DriveAeroplane; {B} StickEntry, StickDirection", "mọi máy bay; AXIS: bomber_payload"),
        ("toc_do_luc_tha", "Ga 0,8 khi cách mục tiêu < 1,1 × AttackReach (AttackReach = tầm súng thân ngắn nhất, không có thì tầm vũ khí 0); có AttackHold thì ga 0,5–1 khi vào giữ; khi kéo ra (RunExtending) ga 1. Tốc độ đổi tối đa 0,8 × tốc độ/s.",
         f"{M}:960-968, {M}:994, {M}:1194 AttackReach", "mọi máy bay cánh cố định"),
        ("dieu_kien_tha", "CanFire: hết hồi, đúng loại đạn; dải STICK chỉ bị giữ lại khi MỌI quả đều rơi gần quân ta (StickAllUnsafe); trong tầm (InReach, tầm bom = tốc độ × thời gian rơi + nửa dải + lõi, dải = (n−1) × spacing), rồi StickStraddles: mục tiêu lệch ngang ≤ lõi + bán kính mục tiêu và dọc đường bay từ (rơi − blast/2) tới (rơi + nửa dải + 2 m) khi tâm dải CENTER (START: tới rơi + blast/2). Khoang bom boss (BAY): như vũ khí thường, không cần bay qua.",
         f"{S} CanFire; {B} StickStraddles, StickAllUnsafe, BombReach; {S} InReach", "bom rơi tự do, khoang bom boss"),
        ("so_bom_moi_luot", "Loạt = Burst; dải STICK có minTargets mà quanh dải (nửa dải + rìa quanh mục tiêu) có ít hơn minTargets xe / công trình địch (và < 2 công trình) thì chỉ thả max(2, ceil(n/3)) quả (StickCount); máy bay có kho bom (load) thì loạt = min(loạt, số bom còn), chỉ trừ số đã thả.",
         f"{S} Operate; {B} StickCount, StickBombs", "mọi vũ khí bom"),
        ("nhip_tha", "Quả đầu thả ngay khi CanFire đúng; các quả sau mỗi SalvoGap: dải STICK = stick.interval (spacing / tốc độ lúc thả), khác = BurstInterval (bộ đếm theo bước 20 Hz). Sau dải, thời gian nạp = cooldown − (n−1) × (interval − burstInterval), nên chu kỳ từ dải này tới dải sau giữ nguyên.",
         f"{S} Operate; {B} StickCooldown; {C}Content/WeaponDef.Stick.cs SalvoGap", "mọi vũ khí bom có burst > 1"),
        ("diem_nham_tung_qua", "Lượt 2: quả đầu cố định dải (PlanStick): đầu dải = BombImpact lúc thả (vị trí máy bay + hướng mũi × tốc độ × thời gian rơi = khoảng dẫn đầu), hướng = hướng mũi; quả i rơi tại đầu dải + hướng × i × spacing (StickPoint), không bao giờ một điểm nhắm chung. Một quả rơi tự do (POINT n 1) vẫn nhắm BombImpact.",
         f"{S} Launch; {B} PlanStick, StickLine, StickPoint, BombImpact", "bom rơi tự do (FREE_FALL_STICK)"),
        ("diem_nham_bom_boss", "Lượt 2: bom khoang của boss (p26_roc_roc_bombs, p26_roc_main_roc_bombs) là Projectile Bomb, stick.drop BAY: dải 8 quả đặt quanh điểm nhắm (CENTER), hướng = trục chính của cụm mục tiêu trong ±45° so với đường boss → điểm nhắm, không thì đường đó; quả i tại đầu dải + hướng × i × spacing; rơi ít nhất BombFall (thời gian bay cũ nếu dài hơn). Khoang vẫn nhả cách 0,3 s.",
         f"{S} Launch; {B} BayStick, StickLine, AxisAt; {BALANCE}: weapons p26_roc_roc_bombs.stick", "argus, garuda, command_airship"),
        ("diem_nham_bom_dan_duong", "Bom dẫn đường (data guided hoặc form GuidedBomb: SDB, JDAM, UMPK): aimAt = mục tiêu (dẫn trước nếu mục tiêu chạy), độ tản thường theo tầm; bom lượn bay tới bằng tốc độ riêng.",
         f"{S}:805-806 LeadPoint; {S}:829; {S}:875-878; {C}Content/Definitions.cs:224 GuidedBomb", "stealth_payload, guided_bomb, glide_fab500"),
        ("tan_xa", "Lượt 2: quả của dải STICK lệch theo seed (world Random) ±jitterAlong dọc và ±jitterAcross ngang dải (không còn vòng tản), × hệ số khinh khí cầu / đèn chiếu (Works.SpreadFactor). Bom rơi tự do POINT: vòng Spread × 0,5 như cũ.",
         f"{S} Launch; {B} FreeFallScatter", "bom rơi tự do, khoang bom boss"),
        ("thoi_gian_roi", "BombFall = √(2 × max(4, độ cao) / 40) (BombGravity 40 m/s², theo tỉ lệ bản đồ); bom có cảnh báo (≥ 400 kg) rơi không sớm hơn thời gian cảnh báo.",
         f"{S}:874, {S}:883; {B}:25, {B}:35", "bom rơi tự do"),
        ("ngoi_no", "Không có ngòi riêng: quả bom nổ khi hết thời gian bay tại điểm aim (UpdateProjectiles → Damage.ResolveImpact); bom chùm tung bom con ở đó.",
         f"{S}: UpdateProjectiles; {C}Combat/DamageSystem (ResolveImpact) {NEED_CODE_CHECK}", "mọi bom"),
        ("an_toan_quan_ta", "Lượt 2: dải STICK xét TỪNG quả: điểm rơi (sau lệch) trong stick.safety (+ bán kính xe) quanh xe mặt đất phe ta thì quả đó không thả; các quả khác giữ điểm của mình. Cả dải chỉ bị giữ lại khi mọi quả đều không an toàn. Bom rơi tự do POINT: StickNearOwn như cũ; bom khác: OwnNear quanh mục tiêu, lõi + 3 m.",
         f"{S} CanFire, Launch; {B} StickAllUnsafe, StickNearOwn", "mọi vũ khí bom"),
        ("vong_lai", "Lượt 2: thả quả đầu của dải STICK thì máy bay giữ hướng, tốc độ, độ cao trong stick.straightTime (dải / tốc độ + thời gian rơi + 1 s, và ≥ 40 m sau quả cuối) (StickStraightUntil); sau đó như cũ: kéo ra (RunExtending) khi gần / đã qua mục tiêu, xa hơn max(0,85 × tầm, 2,2 × bán kính quay) thì quay lại. Glide bomber quay đi trước khi tới mục tiêu.",
         f"{M} DriveAeroplane; {B} PlanStick; {C}Movement/MovementSystem.P25A.cs GlideAway", "máy bay cánh cố định"),
        ("tranh_nem_lai", "Loạt > 1 quả ghi điểm vừa ném (_bombed) để BombWorth chấm thấp nơi đó lần sau.",
         f"{S}:567; {S}:406", "máy bay ném bom"),
        ("the_ho_tro_khong_kich", "Airstrike: Count quả rải đều từ Point tới Point + hướng × Length (Lerp), lệch ngang ngẫu nhiên ±Radius/2, cách nhau Duration/(Count−1) s; máy bay bay với tốc độ Length/Duration. Đã là dải (không dồn một điểm).",
         f"{C}Strikes/StrikeSystem.cs:250-275", "airstrike, napalm_strike, air_raid, cluster_strike"),
        ("sieu_vu_khi_boss_strip", "Strip: n quả cách đều dọc trục (−L/2 + L(k+0,5)/n), lệch ngang ±0,35 × W (khi không có interval), rơi trải trong Duration. Đã là dải.",
         f"{C}Bosses/BossSystem.BigAttacks.cs:708-720 (rơi), :492-505 (vùng cảnh báo)", "airship_carpet, garuda_carpet, kraken_air_raid"),
        ("the_12_qua", "Hướng dẫn của Oanh tạc cơ chiến lược nói 'thả một hàng 12 quả', dữ liệu bomber_payload có burst 7, load 7 (một lần thả 7 quả).",
         "Assets/MachineBrigade/Scripts/Game/Hud/GuideText.cs:410, :414; " + BALANCE + ": weapons bomber_payload", "heavy_bomber"),
    ]
    rows = [[f"HV{i + 1:02d}", b, m, f, a, "đọc mã"] for i, (b, m, f, a) in enumerate(items)]
    return header, rows




def sheet_canh_bao(vk, wids, sup, big, big_strikes, bomb_rows_vk):
    header = ["id", "nhom", "co_vong", "luat", "hinh_dang", "dai_m", "rong_m", "ban_kinh_loi_m", "ban_kinh_ria_m",
              "thoi_gian_canh_bao_s", "file_ham", "nguon", "raw_json"]
    rows = []
    for wid in wids:
        w = vk[wid]
        info = bomb_rows_vk[wid]
        warns = info["canh_bao_theo_luat"] == "TRUE"
        core = fnum(w.get("loi_m"))
        edge = fnum(w.get("edge_m")) or fnum(w.get("ria_m"))
        rows.append([wid, "vu_khi_don_vi", "TRUE" if warns else "FALSE",
                     "FixRules.Warns: không dẫn đường, có lõi; bom ≥ 400 kg, đạn pháo ≥ 203 mm, rốc-két ≥ 300 mm (hoặc bậc ≥ T4)",
                     ("2 vòng tròn đồng tâm tại điểm rơi TỪNG quả (lõi, rìa = WarnRadius); các vòng của một loạt cùng bệ được gộp"
                      if warns else "không có vòng"),
                     "", "", core, (edge if edge > core else core) if warns else "",
                     info["thoi_gian_canh_bao_s_theo_luat"],
                     f"{C}Content/FixRules.cs:134-145 Warns; Assets/MachineBrigade/Scripts/Game/Effects/EffectsDirector.Warnings.cs:57-68 EscapeRing; {C}Content/WeaponDef.P34.cs:64-67",
                     w.get("nguon", ""), ""])
    for sid, s in sup.items():
        line = s.get("kind") == "Airstrike"
        rows.append([sid, "the_ho_tro", "TRUE",
                     "mọi hỏa lực hỗ trợ có vùng báo trước (StrikeWarning, delay)",
                     "dải dọc đường bay từ điểm chọn tới điểm + hướng × length" if line else "vòng tròn quanh điểm chọn",
                     num(s.get("length_m")) if line else "", r3(2 * fnum(s.get("radius_m"))) if line else "",
                     num(s.get("radius_m")) if not line else "", NEED_CODE_CHECK, num(s.get("delay_s")),
                     f"{C}Strikes/StrikeSystem.cs:165-166 StrikeWarning; :111 Incoming (bán kính max(radius, length/2)); Game/Effects/StrikeEffects.cs (vẽ) {NEED_CODE_CHECK}",
                     s.get("nguon", ""), ""])
    for bid, b in big.items():
        st = big_strikes[bid]
        strip = st.get("shape") == "strip"
        rows.append([bid, "sieu_vu_khi_boss", "TRUE", "siêu vũ khí luôn hiện vòng",
                     "hình chữ nhật dài × rộng theo hướng boss (BigZone)" if strip else "vòng tại điểm rơi",
                     num(st.get("length_m")) if strip else "", num(st.get("width_m")) if strip else "",
                     num(st.get("radius_m")), NEED_CODE_CHECK, num(b.get("warn_s")),
                     f"{C}Bosses/BossSystem.BigAttacks.cs:492-505 (Strip zone)",
                     b.get("nguon", ""), ""])
    return header, rows




def static_sheets(ctx) -> dict[str, tuple[list[str], list[list]]]:
    """{sheet name: (header, rows)} of the four bomb sheets."""
    vk_header, vk = table(ctx, "01_vu_khi_dan", "Vu_khi")
    _, xe = table(ctx, "02_phuong_tien", "Xe")
    _, boss = table(ctx, "03_boss", "Boss")
    _, the = table(ctx, "02_phuong_tien", "The_ho_tro")
    _, big_all = table(ctx, "03_boss", "Boss_sieu_vu_khi")
    _, big_strike_all = table(ctx, "03_boss", "Boss_sieu_vu_khi_don")
    units = {**{k: dict(v, _loai="xe") for k, v in xe.items()}, **{k: dict(v, _loai="boss") for k, v in boss.items()}}
    wids = bomb_weapons(vk)
    carriers = {w: [u for u in str(vk[w].get("mang_boi") or "").split(";") if u] for w in wids}
    sup = {k: v for k, v in the.items() if v.get("kind") == "Airstrike" or k in ("glide_bomb_strike", "cluster_at_strike")}
    big = {k: v for k, v in big_all.items() if v.get("icon") == "bomb"}
    big_strikes = {k: next(s for s in big_strike_all.values() if s.get("boss_sieu_vu_khi_id") == k) for k in big}
    sheets = {}
    sheets["Bom_vu_khi"] = sheet_vu_khi(vk_header, vk, wids, carriers, sup, big, big_strikes, units)
    h, rws = sheets["Bom_vu_khi"]
    bomb_rows_vk = {r[0]: dict(zip(h, r)) for r in rws if r[1] == "vu_khi_don_vi"}
    sheets["Bom_don_vi"] = sheet_don_vi(units, carriers, vk, sup, big, big_strikes)
    sheets["Bom_hanh_vi"] = sheet_hanh_vi()
    sheets["Bom_canh_bao"] = sheet_canh_bao(vk, wids, sup, big, big_strikes, bomb_rows_vk)
    return sheets
