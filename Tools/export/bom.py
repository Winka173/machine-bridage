"""The bomb-run fix, pass 0 (Docs/prompts/bomb_run_vi.txt): a bomb-focused export.

    python Tools/export/export.py bom [--trace CSV] [--date YYYY-MM-DD] [--out DIR]

Builds the full export in memory (no files), keeps the bomb weapons and their carriers from 01_vu_khi_dan, 02_phuong_tien
and 03_boss, and writes Docs/export/bom_<date>/: Machine_Brigade_Bom_<date>.xlsx (6 sheets), csv/<sheet>.csv,
Machine_Brigade_Bom_<date>.md and BOM_REPORT.md. Bom_vet_tha reads the csv the EditMode test
MachineBrigade.Tests.BombStickTrace.WriteTheBombDropTrace writes (env MB_BOMB_TRACE; default <out>/vet_tha_unity.csv);
without it the unit weapons' rows say CHUA_CHAY. The fire supports' airstrikes and the bosses' strip attacks are laid out
by formulas with no unit flying them, so their rows are mirrored here from the code (StrikeSystem / BossSystem.BigAttacks).
Read only: no game value is changed.
"""
from __future__ import annotations

import csv
import json
import math
import os
import random
from pathlib import Path

from core import repo
from core.model import NEED_CODE_CHECK
from core.write import write_csv, write_xlsx

CHUA_CHAY = "CHUA_CHAY"
DT = 0.05
SEEDS = (1, 2, 3)
TEST = "MachineBrigade.Tests.BombStickTrace.WriteTheBombDropTrace"
ENV = "MB_BOMB_TRACE"
BALANCE = "Assets/MachineBrigade/Resources/Data/balance.json"
BOMB_GRAVITY = 40.0  # CombatSystem.Bombs.cs:25
FREE_FALL_SCATTER = 0.5  # CombatSystem.Bombs.cs:28
SAME_POINT_M = 1.0  # two impacts closer than this count as one point
FORMATIONS = {
    # 5 vehicles 8 m apart in a row along the flight line, across it, and a cluster 8 m wide (centre and 4 corners)
    "HANG_DOC_8M": [(0.0, z) for z in (-16.0, -8.0, 0.0, 8.0, 16.0)],
    "HANG_NGANG_8M": [(x, 0.0) for x in (-16.0, -8.0, 0.0, 8.0, 16.0)],
    "CUM_8M": [(0.0, 0.0), (-4.0, -4.0), (4.0, -4.0), (-4.0, 4.0), (4.0, 4.0)],
}
TRACE_COLS = ["vu_khi_id", "don_vi_id", "seed", "chi_so_bom", "tick_tha", "vi_tri_tha_x_m", "vi_tri_tha_z_m", "tick_cham",
              "vi_tri_roi_x_m", "vi_tri_roi_z_m", "thoi_gian_roi_s", "toc_do_luc_tha_m_s", "do_cao_m", "huong_bay_deg",
              "duong_tha", "dieu_kien_tha", "loi_m", "ria_m", "khoang_tha_s", "ghi_chu"]
C = "Assets/MachineBrigade/Scripts/Sim/"


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


def code_path(w: dict) -> str:
    """How CombatSystem.Launch aims it (CombatSystem.Bombs.cs:31 FreeFall; Definitions.cs:224 GuidedBomb)."""
    guided = str(w.get("guided")).upper() == "TRUE" or w.get("form") in ("GuidedBomb",)
    if w.get("dang_dan") != "Bomb":
        return "SHELL_PATH"
    if str(w.get("glides")).upper() == "TRUE":
        return "GLIDE"
    return "GUIDED" if guided else "FREE_FALL"


def current_mode(path: str) -> str:
    return {
        "FREE_FALL": "STICK_THEO_TOC_DO (mỗi quả nhắm lại lúc thả: BombImpact; cách nhau tốc độ × khoảng thả)",
        "GUIDED": "POINT (mọi quả nhắm vào mục tiêu)",
        "GLIDE": "POINT (bom lượn bay tới mục tiêu)",
        "SHELL_PATH": "POINT (bắn như đạn pháo: mọi quả nhắm vào mục tiêu, chỉ lệch theo độ tản)",
    }[path]


# ---------------------------------------------------------------------------------------------------------- sheets
def sheet_vu_khi(vk_header, vk, wids, carriers, sup, big, big_strikes, units):
    extra = ["duong_tha_theo_ma", "che_do_tha_hien_tai", "so_bom_moi_luot", "khoang_tha_giua_bom_s", "don_vi_mang",
             "toc_do_don_vi_mang_m_s", "khoang_cach_giua_bom_m_toan_toc", "khoang_cach_giua_bom_m_ga_0_8",
             "do_dai_dai_m_toan_toc", "ty_le_chong_lan_loi_tren_khoang", "canh_bao_theo_luat", "thoi_gian_canh_bao_s_theo_luat"]
    base = [c for c in vk_header if c not in ("id", "nguon", "raw_json")]
    header = ["id", "nhom"] + base + extra + ["nguon", "raw_json"]
    rows = []
    for wid in wids:
        w = vk[wid]
        path = code_path(w)
        burst = int(fnum(w.get("so_phat_moi_loat"), 1)) or 1
        gap = fnum(w.get("khoang_phat_trong_loat_s"), 0.1)
        core = fnum(w.get("loi_m"))
        mounts = carriers.get(wid, [])
        speeds = [fnum(units[u].get("toc_do_m_s")) for u in mounts if u in units]
        speed = speeds[0] if speeds else 0.0
        spacing = speed * gap if path == "FREE_FALL" else 0.0
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
                     "một lượt bay qua, không vòng lại", s.get("nguon", ""), s.get("raw_json", "")])
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
        ("huong_vao", "Không có đường vào tính trước: máy bay quay mũi thẳng vào vị trí mục tiêu (goal = target.Position) theo tốc độ quay; hướng dải bom = hướng mũi lúc thả.",
         f"{M}:944 goal; {M}:993 RotateTowards", "mọi máy bay"),
        ("toc_do_luc_tha", "Ga 0,8 khi cách mục tiêu < 1,1 × AttackReach (AttackReach = tầm súng thân ngắn nhất, không có thì tầm vũ khí 0); có AttackHold thì ga 0,5–1 khi vào giữ; khi kéo ra (RunExtending) ga 1. Tốc độ đổi tối đa 0,8 × tốc độ/s.",
         f"{M}:960-968, {M}:994, {M}:1194 AttackReach", "mọi máy bay cánh cố định"),
        ("dieu_kien_tha", "CanFire: hết hồi, đúng loại đạn, không có quân ta (StickNearOwn), trong tầm (InReach, tầm bom = tốc độ × thời gian rơi + nửa dải + lõi), rồi StickStraddles: mục tiêu lệch ngang ≤ lõi + bán kính mục tiêu và dọc đường bay từ (rơi − blast/2) tới (rơi + nửa dải + 2 m). KHÔNG có điều kiện 'chỉ thả khi đủ 2/3 số bom' trong mã.",
         f"{S}:719-737 CanFire; {B}:62-73 StickStraddles; {B}:54-55 BombReach; {S}:502 InReach", "bom rơi tự do"),
        ("so_bom_moi_luot", "Loạt = Burst; máy bay có kho bom (load) thì loạt = min(Burst, số bom còn), trừ cả loạt khỏi kho.",
         f"{S}:560-565 Operate; {B}:46-51 StickBombs", "mọi vũ khí bom"),
        ("nhip_tha", "Quả đầu thả ngay khi CanFire đúng; các quả sau mỗi BurstInterval (bộ đếm theo bước 20 Hz; interval < 0,05 s thì nhiều quả cùng một bước).",
         f"{S}:516-532 (loạt đang dở); {S}:606-612", "mọi vũ khí bom có burst > 1"),
        ("diem_nham_tung_qua", "Bom rơi tự do: MỖI quả nhắm lại lúc thả: aimAt = BombImpact = vị trí máy bay + hướng mũi × (tốc độ × thời gian rơi). Không dùng chung một điểm nhắm. Khoảng cách giữa hai quả = tốc độ lúc đó × BurstInterval (StickLength = (n−1) × BurstInterval × tốc độ).",
         f"{S}:820-821 Launch; {B}:38-39 BombImpact; {B}:42-43 StickLength", "bom rơi tự do (FREE_FALL)"),
        ("diem_nham_bom_boss", "Bom khoang của boss (p26_roc_roc_bombs, p26_roc_main_roc_bombs) kế thừa boss_howitzer nên Projectile = Shell, không phải Bomb: FreeFall = false, cả 8 quả nhắm vào CHÍNH mục tiêu (còn sống thì theo vị trí mục tiêu, không thì BurstAim = vị trí lúc bắt đầu loạt), chỉ lệch theo độ tản pháo → MỘT ĐIỂM.",
         f"{S}:529 (loạt dở nhắm t.Position); {S}:611 BurstAim; {S}:829 spread; {BALANCE}: weapons p26_roc_roc_bombs", "argus, garuda, command_airship"),
        ("diem_nham_bom_dan_duong", "Bom dẫn đường (data guided hoặc form GuidedBomb: SDB, JDAM, UMPK): aimAt = mục tiêu (dẫn trước nếu mục tiêu chạy), độ tản thường theo tầm; bom lượn bay tới bằng tốc độ riêng.",
         f"{S}:805-806 LeadPoint; {S}:829; {S}:875-878; {C}Content/Definitions.cs:224 GuidedBomb", "stealth_payload, guided_bomb, glide_fab500"),
        ("tan_xa", "Bom rơi tự do: lệch ngẫu nhiên trong vòng bán kính Spread × 0,5 (FreeFallScatter) quanh điểm của nó, × hệ số khinh khí cầu chắn (Works.SpreadFactor). Không có lệch dọc / ngang riêng theo đường bay.",
         f"{S}:829, {S}:856-858; {B}:28", "bom rơi tự do"),
        ("thoi_gian_roi", "BombFall = √(2 × max(4, độ cao) / 40) (BombGravity 40 m/s², theo tỉ lệ bản đồ); bom có cảnh báo (≥ 400 kg) rơi không sớm hơn thời gian cảnh báo.",
         f"{S}:874, {S}:883; {B}:25, {B}:35", "bom rơi tự do"),
        ("ngoi_no", "Không có ngòi riêng: quả bom nổ khi hết thời gian bay tại điểm aim (UpdateProjectiles → Damage.ResolveImpact); bom chùm tung bom con ở đó.",
         f"{S}: UpdateProjectiles; {C}Combat/DamageSystem (ResolveImpact) {NEED_CODE_CHECK}", "mọi bom"),
        ("an_toan_quan_ta", "Bom rơi tự do: StickNearOwn xét MỘT vòng quanh giữa dải (bán kính lõi + nửa dải + 3 m): có xe ta thì KHÔNG thả cả loạt (không bỏ từng quả). Bom khác: OwnNear quanh mục tiêu, lõi + 3 m.",
         f"{S}:727-729; {B}:76-82", "mọi vũ khí bom"),
        ("vong_lai", "Kéo ra (RunExtending) khi cách < max(6, 0,3 × tầm) hoặc đã qua mục tiêu và < 0,6 × tầm: bay thẳng toàn lực; xa hơn max(0,85 × tầm, 2,2 × bán kính quay) thì quay lại vào. Không có đoạn bay thẳng bắt buộc sau quả cuối. Glide bomber quay đi trước khi tới mục tiêu.",
         f"{M}:932-941; {C}Movement/MovementSystem.P25A.cs:17-23 GlideAway", "máy bay cánh cố định"),
        ("tranh_nem_lai", "Loạt > 1 quả ghi điểm vừa ném (_bombed) để BombWorth chấm thấp nơi đó lần sau.",
         f"{S}:567; {S}:406", "máy bay ném bom"),
        ("the_ho_tro_khong_kich", "Airstrike: Count quả rải đều từ Point tới Point + hướng × Length (Lerp), lệch ngang ngẫu nhiên ±Radius/2, cách nhau Duration/(Count−1) s; máy bay bay với tốc độ Length/Duration. Đã là dải (không dồn một điểm).",
         f"{C}Strikes/StrikeSystem.cs:250-275", "airstrike, napalm_strike, air_raid, cluster_strike"),
        ("sieu_vu_khi_boss_strip", "Strip: n quả cách đều dọc trục (−L/2 + L(k+0,5)/n), lệch ngang ±0,35 × W (khi không có interval), rơi trải trong Duration. Đã là dải.",
         f"{C}Bosses/BossSystem.BigAttacks.cs:708-720 (rơi), :492-505 (vùng cảnh báo)", "airship_carpet, garuda_carpet, kraken_air_raid"),
        ("the_12_qua", "Hướng dẫn của Oanh tạc cơ chiến lược nói 'thả một hàng 12 quả', dữ liệu bomber_payload có burst 7, load 7 (một lượt 7 quả).",
         "Assets/MachineBrigade/Scripts/Game/Hud/GuideText.cs:410, :414; " + BALANCE + ": weapons bomber_payload", "heavy_bomber"),
    ]
    rows = [[f"HV{i + 1:02d}", b, m, f, a, "đọc mã nhánh feature/bomb-p0"] for i, (b, m, f, a) in enumerate(items)]
    return header, rows


# ---------------------------------------------------------------------------------------------------------- trace
def read_trace(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


def mirror_rows(sup, big, big_strikes) -> list[dict]:
    """The supports' airstrikes and the bosses' strips, laid out by the code's formulas (no unit flies them): aim (0, 0),
    heading 0 (+z); a python Random per seed stands in for the world's (the lateral offsets differ from a battle's)."""
    out = []
    # heading 0: Direction = SimMath.Forward(0) = (0, 1); the lateral vector (-dir.y, dir.x) = (-1, 0)
    for sid, s in sup.items():
        if s.get("kind") != "Airstrike":
            continue
        n = int(fnum(s.get("count"), 1))
        length, dur, radius = fnum(s.get("length_m")), fnum(s.get("duration_s")), fnum(s.get("radius_m"))
        delay, blast = fnum(s.get("delay_s")), fnum(s.get("blast_m"))
        speed = length / max(0.2, dur)
        interval = dur / (n - 1) if n > 1 else 0.0
        for seed in SEEDS:
            rng = random.Random(seed)
            for k in range(n):
                along = k / (n - 1) if n > 1 else 0.5
                lat = (rng.random() - 0.5) * radius
                x, z = -lat, length * along
                lands = int(math.ceil((delay + k * interval) / DT - 1e-6))
                fall = 0.8  # the view's fall (Game/Effects/StrikeEffects.cs:23); the sim blasts at the landing time
                out.append({"vu_khi_id": sid, "don_vi_id": "(the_ho_tro)", "seed": seed, "chi_so_bom": k,
                            "tick_tha": lands - int(round(fall / DT)), "vi_tri_tha_x_m": x, "vi_tri_tha_z_m": z - speed * fall,
                            "tick_cham": lands, "vi_tri_roi_x_m": x, "vi_tri_roi_z_m": z, "thoi_gian_roi_s": fall,
                            "toc_do_luc_tha_m_s": speed, "do_cao_m": "", "huong_bay_deg": 0, "duong_tha": "SUPPORT_AIRSTRIKE",
                            "dieu_kien_tha": "theo thời gian (Start + k × interval)", "loi_m": blast, "ria_m": blast,
                            "khoang_tha_s": interval, "ghi_chu": "python mirror of StrikeSystem.cs:250-275 (no Scattered jam spread)",
                            "_nguon": "python_mirror"})
    for bid, b in big.items():
        st = big_strikes[bid]
        if st.get("shape") != "strip":
            continue
        n = int(fnum(st.get("count"), 1))
        length, width, dur = fnum(st.get("length_m")), fnum(st.get("width_m")), fnum(st.get("duration_s"))
        core = fnum(st.get("radius_m"))
        warn = fnum(b.get("warn_s"))
        for seed in SEEDS:
            rng = random.Random(seed)
            for k in range(n):
                along = -length * 0.5 + length * (k + 0.5) / n
                lat = (rng.random() - 0.5) * width * 0.7 if width > 0 else 0.0
                due = warn + (dur * k / (n - 1) if n > 1 else 0.0)
                lands = int(math.ceil(due / DT - 1e-6))
                out.append({"vu_khi_id": bid, "don_vi_id": b.get("dung_boi", ""), "seed": seed, "chi_so_bom": k,
                            "tick_tha": lands - int(round(0.9 / DT)), "vi_tri_tha_x_m": "", "vi_tri_tha_z_m": "",
                            "tick_cham": lands, "vi_tri_roi_x_m": lat, "vi_tri_roi_z_m": along, "thoi_gian_roi_s": 0.9,
                            "toc_do_luc_tha_m_s": "", "do_cao_m": "", "huong_bay_deg": 0, "duong_tha": "BOSS_STRIP",
                            "dieu_kien_tha": "sau cảnh báo warn_s", "loi_m": core, "ria_m": min(20.0, core * 2.0),
                            "khoang_tha_s": dur / (n - 1) if n > 1 else 0.0,
                            "ghi_chu": "python mirror of BossSystem.BigAttacks.cs:708-720; ria = Catalog.WithEdge 2 × lõi (NEED_CODE_CHECK cho siêu vũ khí)",
                            "_nguon": "python_mirror"})
    return out


def drops(rows: list[dict]) -> dict[tuple, list[dict]]:
    """One drop = one (weapon, carrier, seed) with its bombs (rows with a bomb index >= 0)."""
    out: dict[tuple, list[dict]] = {}
    for r in rows:
        i = num(r.get("chi_so_bom"))
        if not isinstance(i, (int, float)) or i < 0:
            continue
        out.setdefault((r["vu_khi_id"], r["don_vi_id"], int(fnum(r["seed"]))), []).append(r)
    return out


def drop_stats(bombs: list[dict]) -> dict:
    pts = [(fnum(b["vi_tri_roi_x_m"]), fnum(b["vi_tri_roi_z_m"])) for b in bombs]
    h = math.radians(fnum(bombs[0].get("huong_bay_deg")))
    fwd = (math.sin(h), math.cos(h))
    clusters: list[tuple[float, float]] = []
    for p in pts:
        if not any(math.dist(p, c) < SAME_POINT_M for c in clusters):
            clusters.append(p)
    far = max((math.dist(a, b) for i, a in enumerate(pts) for b in pts[i + 1:]), default=0.0)
    along = [p[0] * fwd[0] + p[1] * fwd[1] for p in pts]
    across = [p[0] * fwd[1] - p[1] * fwd[0] for p in pts]
    order = sorted(along)
    gaps = [b - a for a, b in zip(order, order[1:])]
    mean_gap = sum(gaps) / len(gaps) if gaps else 0.0
    core = fnum(bombs[0].get("loi_m"))
    return {"so_bom": len(pts), "so_diem_roi_khac_nhau": len(clusters), "khoang_cach_xa_nhat_m": far,
            "do_dai_dai_m": max(along) - min(along), "do_lech_ngang_m": max(across) - min(across),
            "khoang_cach_tb_giua_bom_m": mean_gap, "ty_le_chong_lan": core / mean_gap if mean_gap > 0 else ""}


def sheet_vet_tha(trace: list[dict], mirror: list[dict], unit_pairs: list[tuple[str, str]], trace_path: Path):
    stats_cols = ["loai_dong", "so_bom", "so_diem_roi_khac_nhau", "khoang_cach_xa_nhat_m", "do_dai_dai_m", "do_lech_ngang_m",
                  "khoang_cach_tb_giua_bom_m", "ty_le_chong_lan"]
    header = ["id"] + TRACE_COLS + stats_cols + ["nguon", "raw_json"]
    rows = []
    src_trace = f"Unity EditMode {TEST} ({ENV}={rel(trace_path)})"
    all_rows = [dict(r, _nguon=src_trace) for r in trace] + mirror
    groups: dict[tuple[str, str], list[dict]] = {}
    for r in all_rows:
        groups.setdefault((r["vu_khi_id"], r["don_vi_id"]), []).append(r)
    for wid, uid in unit_pairs:  # a pair the trace lacks (not run yet, or not in this csv)
        groups.setdefault((wid, uid), [])
    for key in sorted(groups):
        wid, uid = key
        group = groups[key]
        if not group:
            rows.append([f"{wid}|{uid}|{CHUA_CHAY}"] + [wid, uid] + [CHUA_CHAY] * (len(TRACE_COLS) - 2)
                        + [CHUA_CHAY] + [""] * (len(stats_cols) - 1)
                        + [f"chờ chạy Unity: {TEST} với {ENV}=<csv>", ""])
            continue
        for r in sorted(group, key=lambda x: (int(fnum(x["seed"])), fnum(x.get("chi_so_bom"), -1))):
            i = num(r.get("chi_so_bom"))
            rid = f"{wid}|{uid}|s{num(r['seed'])}|" + (f"b{int(i):02d}" if isinstance(i, (int, float)) and i >= 0 else str(r.get("dieu_kien_tha") or "x"))
            raw = {k: r.get(k, "") for k in TRACE_COLS}
            rows.append([rid] + [num(r.get(c)) if not isinstance(r.get(c), float) else r3(r[c]) for c in TRACE_COLS]
                        + ["BOM" if isinstance(i, (int, float)) and i >= 0 else "KHONG_THA"] + [""] * (len(stats_cols) - 1)
                        + [r["_nguon"], json.dumps(raw, ensure_ascii=False)])
        per = [drop_stats(b) for k, b in sorted(drops(group).items())]
        if per:
            avg = {k: (sum(p[k] for p in per if isinstance(p[k], (int, float))) / max(1, sum(isinstance(p[k], (int, float)) for p in per)))
                   for k in per[0]}
            rows.append([f"{wid}|{uid}|TONG_KET", wid, uid] + [""] * (len(TRACE_COLS) - 2)
                        + ["TONG_KET_TB_3_SEED"] + [r3(avg[k]) for k in stats_cols[1:]]
                        + [group[0]["_nguon"], json.dumps({"seeds": [p for p in per]}, ensure_ascii=False, default=float)])
    return header, rows


def sheet_ket_qua_vung(trace: list[dict], mirror: list[dict], unit_pairs):
    header = ["id", "vu_khi_id", "don_vi_id", "seed", "doi_hinh", "so_xe", "so_bom", "so_xe_trung_loi", "so_xe_trung_ria",
              "so_xe_trung", "so_lan_trung_loi", "loi_m", "ria_m", "nguon", "raw_json"]
    rows = []
    groups = drops(trace)
    groups.update(drops(mirror))
    for (wid, uid, seed), bombs in sorted(groups.items()):
        core, edge = fnum(bombs[0].get("loi_m")), fnum(bombs[0].get("ria_m"))
        edge = max(edge, core)
        h = math.radians(fnum(bombs[0].get("huong_bay_deg")))
        pts = [(fnum(b["vi_tri_roi_x_m"]), fnum(b["vi_tri_roi_z_m"])) for b in bombs]
        src = bombs[0].get("_nguon") or "Unity trace"
        support = str(bombs[0].get("duong_tha", "")).startswith("SUPPORT")
        for fname, cars in FORMATIONS.items():
            # the formation turned to the drop's heading (heading 0 leaves it as written), centred on the aim (0, 0); an
            # airstrike's Point is the START of its line (StrikeSystem.cs:252), so its formations sit on the line's middle
            cx, cz = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)) if support else (0.0, 0.0)
            placed = [(cx + x * math.cos(h) + z * math.sin(h), cz - x * math.sin(h) + z * math.cos(h)) for x, z in cars]
            in_core = in_edge = core_hits = 0
            for car in placed:
                d = [math.dist(car, p) for p in pts]
                hits_core = sum(1 for v in d if v <= core)
                core_hits += hits_core
                if hits_core:
                    in_core += 1
                elif any(v <= edge for v in d):
                    in_edge += 1
            rows.append([f"{wid}|{uid}|s{seed}|{fname}", wid, uid, seed, fname, len(cars), len(pts), in_core, in_edge,
                         in_core + in_edge, core_hits, core, edge, f"{src}; python (xe là điểm, không tính bán kính xe; tâm đội hình = "
                         + ("giữa dải" if support else "điểm nhắm (0, 0)") + ")",
                         json.dumps({"xe": placed}, ensure_ascii=False)])
    traced = {(k[0], k[1]) for k in groups}
    for wid, uid in unit_pairs:
        if (wid, uid) in traced:
            continue
        for fname, cars in FORMATIONS.items():
            rows.append([f"{wid}|{uid}|{CHUA_CHAY}|{fname}", wid, uid, CHUA_CHAY, fname, len(cars)] + [CHUA_CHAY] * 5
                        + ["", "", f"chờ Bom_vet_tha ({TEST})", ""])
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


# ---------------------------------------------------------------------------------------------------------- docs
def md_table(header, rows, cols=None, limit=400) -> str:
    cols = cols or header
    idx = [header.index(c) for c in cols if c in header]
    out = ["| " + " | ".join(header[i] for i in idx) + " |", "|" + "---|" * len(idx)]
    for r in rows[:limit]:
        out.append("| " + " | ".join(str(r[i]).replace("|", "/").replace("\n", " ") for i in idx) + " |")
    if len(rows) > limit:
        out.append(f"\n({len(rows) - limit} dòng nữa trong xlsx / csv)")
    return "\n".join(out)


def main(args, ex) -> int:
    date = args.date or repo.head_date()
    out = Path(args.out) if args.out else repo.ROOT / "Docs" / "export" / f"bom_{date}"
    if not out.is_absolute():
        out = repo.ROOT / out
    trace_path = Path(getattr(args, "trace", None) or os.environ.get(ENV) or (out / "vet_tha_unity.csv"))
    if not trace_path.is_absolute():
        trace_path = repo.ROOT / trace_path
    base = repo.resolve_ref(args.base) if args.base else None
    ctx, *_ = ex.build(args.base if base else None)

    vk_header, vk = table(ctx, "01_vu_khi_dan", "Vu_khi")
    _, xe = table(ctx, "02_phuong_tien", "Xe")
    _, boss = table(ctx, "03_boss", "Boss")
    _, the = table(ctx, "02_phuong_tien", "The_ho_tro")
    _, big_all = table(ctx, "03_boss", "Boss_sieu_vu_khi")
    _, big_strike_all = table(ctx, "03_boss", "Boss_sieu_vu_khi_don")
    units = {**{k: dict(v, _loai="xe") for k, v in xe.items()}, **{k: dict(v, _loai="boss") for k, v in boss.items()}}

    wids = bomb_weapons(vk)
    carriers = {w: [u for u in str(vk[w].get("mang_boi") or "").split(";") if u] for w in wids}
    # a weapon that inherits a bomb weapon and has no carrier of its own: its parent's carriers do not carry it
    sup = {k: v for k, v in the.items() if v.get("kind") == "Airstrike" or k in ("glide_bomb_strike", "cluster_at_strike")}
    big = {k: v for k, v in big_all.items() if v.get("icon") == "bomb"}
    big_strikes = {k: next(s for s in big_strike_all.values() if s.get("boss_sieu_vu_khi_id") == k) for k in big}

    sheets = {}
    sheets["Bom_vu_khi"] = sheet_vu_khi(vk_header, vk, wids, carriers, sup, big, big_strikes, units)
    h, rws = sheets["Bom_vu_khi"]
    bomb_rows_vk = {r[0]: dict(zip(h, r)) for r in rws if r[1] == "vu_khi_don_vi"}
    sheets["Bom_don_vi"] = sheet_don_vi(units, carriers, vk, sup, big, big_strikes)
    sheets["Bom_hanh_vi"] = sheet_hanh_vi()
    trace = read_trace(trace_path)
    mirror = mirror_rows(sup, big, big_strikes)
    unit_pairs = sorted((w, u) for w in wids for u in carriers[w])
    sheets["Bom_vet_tha"] = sheet_vet_tha(trace, mirror, unit_pairs, trace_path)
    sheets["Bom_canh_bao"] = sheet_canh_bao(vk, wids, sup, big, big_strikes, bomb_rows_vk)
    sheets["Bom_ket_qua_vung"] = sheet_ket_qua_vung(trace, mirror, unit_pairs)

    stem = f"Machine_Brigade_Bom_{date}"
    write_xlsx(out / f"{stem}.xlsx", [(n, hh, rr, set()) for n, (hh, rr) in sheets.items()])
    for n, (hh, rr) in sheets.items():
        write_csv(out / "csv" / f"{n}.csv", hh, rr)
    write_md(out / f"{stem}.md", sheets, date, trace, trace_path)
    write_report(out / "BOM_REPORT.md", sheets, date, trace, trace_path, out, stem)
    print(f"bom: {len(wids)} unit bomb weapons, {len(unit_pairs)} weapon-carrier pairs, {len(sup)} supports, {len(big)} boss attacks; "
          f"trace {'read ' + str(len(trace)) + ' rows' if trace else 'absent (CHUA_CHAY)'}")
    print(f"wrote {rel(out)}")
    return 0


MD_COLS = {
    "Bom_vu_khi": ["id", "nhom", "ten_that", "dau_no_kg", "loai_sat_thuong", "sat_thuong_moi_phat", "loi_m", "so_bom_moi_luot",
                   "khoang_tha_giua_bom_s", "thoi_gian_nap_s", "duong_tha_theo_ma", "don_vi_mang", "khoang_cach_giua_bom_m_toan_toc",
                   "do_dai_dai_m_toan_toc", "ty_le_chong_lan_loi_tren_khoang", "canh_bao_theo_luat"],
    "Bom_don_vi": ["id", "loai", "toc_do_m_s", "xoay_than_deg_s", "ban_kinh_quay_m", "do_cao_tha_m", "vu_khi_bom", "so_bom_moi_luot",
                   "bang_dan_qua", "nap_lai_s", "thoi_gian_roi_s_theo_ma", "khoang_dan_dau_m_theo_ma"],
    "Bom_hanh_vi": ["id", "buoc", "mo_ta_theo_ma", "file_ham"],
    "Bom_vet_tha": ["id", "chi_so_bom", "tick_tha", "vi_tri_tha_z_m", "tick_cham", "vi_tri_roi_x_m", "vi_tri_roi_z_m", "thoi_gian_roi_s",
                    "loai_dong", "so_diem_roi_khac_nhau", "khoang_cach_xa_nhat_m", "do_dai_dai_m", "do_lech_ngang_m", "ty_le_chong_lan"],
    "Bom_canh_bao": ["id", "nhom", "co_vong", "hinh_dang", "dai_m", "rong_m", "ban_kinh_loi_m", "ban_kinh_ria_m", "thoi_gian_canh_bao_s"],
    "Bom_ket_qua_vung": ["id", "doi_hinh", "so_bom", "so_xe_trung_loi", "so_xe_trung_ria", "so_xe_trung", "so_lan_trung_loi"],
}


def write_md(path: Path, sheets, date, trace, trace_path):
    parts = [f"# Machine Brigade: dữ liệu ném bom ({date})", "",
             "Lượt 0 của bản sửa ném bom rải thảm (Docs/prompts/bomb_run_vi.txt). Sinh bởi `python Tools/export/export.py bom`; "
             "chỉ đọc, không đổi giá trị game. Bảng đủ cột trong xlsx / csv; ở đây là các cột chính.", "",
             f"Bom_vet_tha: {'đọc ' + str(len(trace)) + ' dòng từ ' + trace_path.name if trace else 'các vũ khí của đơn vị còn CHUA_CHAY (chờ test Unity ' + TEST + ')'}; "
             "thẻ hỗ trợ và siêu vũ khí boss tính lại bằng python theo công thức trong mã.", ""]
    for n, (h, r) in sheets.items():
        body = r if n != "Bom_vet_tha" else [x for x in r if x[h.index("loai_dong")] != "BOM"]
        parts += [f"## {n}", "", md_table(h, body, MD_COLS.get(n)), ""]
        if n == "Bom_vet_tha":
            parts += ["(Chỉ các dòng tổng kết và CHUA_CHAY; từng quả trong xlsx / csv.)", ""]
    path.write_bytes("\n".join(parts).encode("utf-8"))


def write_report(path: Path, sheets, date, trace, trace_path, out, stem):
    h, rows = sheets["Bom_vet_tha"]
    summ = [dict(zip(h, r)) for r in rows if r[h.index("loai_dong")] == "TONG_KET_TB_3_SEED"]
    lines = [f"# BOM_REPORT: ném bom dồn một điểm, lượt 0 ({date})", "",
             "## Nguyên nhân quan sát được trong mã", "",
             "1. **Máy bay ném bom thường (bom rơi tự do) KHÔNG dùng chung một điểm nhắm.** Mỗi quả được nhắm lại lúc thả: "
             "`aimAt = BombImpact(shooter)` = vị trí máy bay + hướng mũi × tốc độ × thời gian rơi "
             f"({C}Combat/CombatSystem.cs:820-821; {C}Combat/CombatSystem.Bombs.cs:38-39). Nhưng khoảng cách giữa hai quả chỉ là "
             "tốc độ × BurstInterval (CombatSystem.Bombs.cs:42-43): Oanh tạc cơ chiến lược 22 m/s × 0,2 s = 4,4 m (3,5 m khi ga 0,8 trong tầm, "
             "MovementSystem.cs:968), trong khi lõi nổ 10 m và tản 3,5 m: 7 quả nằm trong dải ~21–26 m, lõi chồng lõi (lõi / khoảng ≈ 2,3–2,9), "
             "nhìn như một đống. Cường kích: 2 quả × 0,25 s × 32 m/s = 8 m (lõi 8 m).",
             "2. **Bom khoang của boss rơi đúng một điểm.** p26_roc_roc_bombs / p26_roc_main_roc_bombs (Argus, Garuda, khí cầu chỉ huy; 8 quả 400 kg) "
             "kế thừa boss_howitzer nên bay như đạn pháo (Projectile = Shell), FreeFall = false: cả loạt nhắm vào chính mục tiêu "
             f"({C}Combat/CombatSystem.cs:529 nhắm t.Position khi mục tiêu còn sống, :611 BurstAim), chỉ lệch theo độ tản (:829). Đây là chỗ 'mọi quả cùng một điểm' thật sự.",
             "3. **Bom dẫn đường là POINT theo thiết kế:** stealth_payload (B-2, 2 × 907 kg, guided), guided_bomb (SDB), glide_fab500 (UMPK) nhắm vào mục tiêu.",
             "4. **Thẻ hỗ trợ không kích và siêu vũ khí boss dạng strip đã rải dải** (StrikeSystem.cs:250-275 Lerp dọc đường; BossSystem.BigAttacks.cs:708-720): "
             "garuda_carpet 20 quả / 100 m (5 m, lõi 7 m), airship_carpet 16 / 80 m, kraken_air_raid 12 / 90 m, airstrike 4 / 60 m, napalm_strike 8 / 55 m.",
             "5. **Thẻ nói 12 quả, dữ liệu là 7:** GuideText.cs:410/414 'một hàng 12 quả' vs balance.json bomber_payload burst 7, load 7.",
             "6. An toàn quân ta xét cả loạt một lần (CombatSystem.Bombs.cs:76-82): có xe ta gần giữa dải thì bỏ cả lượt, không bỏ từng quả. "
             "Không có điều kiện 'đủ 2/3 số bom' trong mã.", "",
             "## Số đo (Bom_vet_tha)", ""]
    if trace and summ:
        lines += [md_table(list(summ[0].keys()), [list(s.values()) for s in summ],
                           ["id", "so_bom", "so_diem_roi_khac_nhau", "khoang_cach_xa_nhat_m", "do_dai_dai_m", "do_lech_ngang_m",
                            "khoang_cach_tb_giua_bom_m", "ty_le_chong_lan"]), ""]
    else:
        lines += ["Vũ khí của đơn vị: **CHUA_CHAY** (chờ test Unity). Lệnh cho người chạy Unity:", "",
                  "```",
                  f"set {ENV}=<repo>\\Docs\\export\\bom_{date}\\vet_tha_unity.csv",
                  f"Unity.exe -batchmode -projectPath <repo> -runTests -testPlatform EditMode -testFilter {TEST} -testResults <tmp>\\bom_results.xml",
                  "python Tools/export/export.py bom",
                  "```", "",
                  "Thẻ hỗ trợ và strip boss (python theo công thức trong mã):", ""]
        if summ:
            lines += [md_table(list(summ[0].keys()), [list(s.values()) for s in summ],
                               ["id", "so_bom", "so_diem_roi_khac_nhau", "khoang_cach_xa_nhat_m", "do_dai_dai_m", "do_lech_ngang_m",
                                "khoang_cach_tb_giua_bom_m", "ty_le_chong_lan"]), ""]
    where = rel(out)
    lines += ["## File", "",
              f"- {where}/{stem}.xlsx (6 sheet), {where}/csv/<sheet>.csv, {where}/{stem}.md, {where}/BOM_REPORT.md",
              f"- Vết thả từ Unity: {trace_path.name} ({'có' if trace else 'chưa có'}); test: Assets/MachineBrigade/Tests/EditMode/BombStickTrace.cs",
              "- Bộ xuất: Tools/export/bom.py (`python Tools/export/export.py bom [--trace CSV]`)",
              f"- Mã: {C}Combat/CombatSystem.Bombs.cs, {C}Combat/CombatSystem.cs (CanFire, Operate, Launch), {C}Movement/MovementSystem.cs (BombTarget, chạy vào), "
              f"{C}Strikes/StrikeSystem.cs (Airstrike), {C}Bosses/BossSystem.BigAttacks.cs (Strip)", "",
              "Lượt 0 dừng ở đây: chưa sửa gì, chờ chủ dự án nói \"tiếp tục\".", ""]
    path.write_bytes("\n".join(lines).encode("utf-8"))
