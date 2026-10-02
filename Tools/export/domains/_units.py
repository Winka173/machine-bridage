"""The columns every vehicles[] sheet shares (Xe, Thap, Tuong, Nha_chinh, Mo_dun_tien_ich, Boss): the game's value
(Vietnamese names, ported from Catalog.cs: inherits, toughness, the armour faces rule, the loader's defaults) and the raw
fields (snake_case, one column a source key)."""
from __future__ import annotations

from core.model import NEED_CODE_CHECK, child_rows

from . import _balance as B

# keys of a vehicles[] record that file 01 exports (Khac_che, Phao_sang)
IN_01 = ("aps", "apsCapability", "interceptionMode", "flares", "flareCharges", "flareRecharge")
VECTORS = {"armour": ["front", "side", "rear", "top"], "modelSize": ["length_m", "width_m", "height_m"]}

# (column, unit, meaning)
COMMON = [
    ("ten_en", "", "tên tiếng Anh (HUD unit.<id>)"),
    ("ten_vi", "", "tên tiếng Việt (HUD unit.<id>)"),
    ("ten_ngan_vi", "", "tên ngắn tiếng Việt (HUD short.<id>)"),
    ("lop", "", "lớp (class) sau inherits"),
    ("nhanh", "", "nhánh quân (balance.branches theo lớp)"),
    ("ke_thua_tu", "", "bản ghi cha (inherits)"),
    ("base_cp", "CP", "giá thẻ (cp) sau inherits; 0 = không bán"),
    ("mau_hp", "hp", "máu trong dữ liệu (hp) sau inherits"),
    ("mau_trong_tran_hp", "hp", "máu trong trận = hp x toughness.vehicles (boss: toughness.bosses; trước hệ số hạng boss, độ khó, chiến dịch)"),
    ("giap_truoc", "", "giáp mặt trước 0-5 (Armour.cs: một số = trước, hông -1, sau / nóc -2; bay / công trình: đều)"),
    ("giap_hong", "", "giáp hông"),
    ("giap_sau", "", "giáp sau"),
    ("giap_noc", "", "giáp nóc"),
    ("cong_trinh", "", "là công trình (structure): giáp đều, hệ số Structure"),
    ("toc_do_m_s", "m/s", "tốc độ"),
    ("xoay_than_deg_s", "deg/s", "tốc độ xoay thân (turnRate)"),
    ("xoay_thap_deg_s", "deg/s", "tốc độ xoay tháp pháo (turretTurnRate)"),
    ("tam_nhin_m", "m", "tầm nhìn"),
    ("ban_kinh_m", "m", "bán kính va chạm / trúng đạn"),
    ("dai_m", "m", "dài thân = length x scale"),
    ("rong_m", "m", "rộng thân = width x scale"),
    ("bay", "", "bay (flying)"),
    ("do_cao_m", "m", "độ cao bay (altitude, mặc định 0)"),
    ("dung_yen", "", "đứng yên (static)"),
    ("ban_khi_chay", "", "bắn khi chạy (firesWhileMoving, mặc định true)"),
    ("toc_do_chiem", "", "hệ số tốc độ chiếm cứ điểm (captureRate, mặc định 1)"),
    ("tha_du_s", "s", "thời gian thả dù (dropDelay, mặc định 3,5, kẹp 0,5-30)"),
    ("he_so_sat_thuong_ra", "", "outgoingDamageMult (mặc định 1, kẹp 0,1-10)"),
    ("vu_khi_chinh", "", "vũ khí chính (weapon)"),
    ("vu_khi_phu", "", "vũ khí phụ (secondary[*].weapon)"),
    ("noi_tai", "", "kỹ năng nội tại (skills)"),
    ("tu_ve", "", "tự vệ: none / flare / aps"),
    ("so_lan_tu_ve", "", "số lần tự vệ (aps.charges hoặc flareCharges)"),
    ("hoi_tu_ve_s", "s", "hồi tự vệ (aps.recharge hoặc flareRecharge)"),
    ("mo_hinh", "", "model GLB (model, mặc định cha hoặc id)"),
]
WEAPON_FK = ["01_vu_khi_dan/Vu_khi"]
TRACKED = ["base_cp", "mau_hp", "giap_truoc", "giap_hong", "giap_sau", "giap_noc", "toc_do_m_s", "tam_nhin_m",
           "vu_khi_chinh", "vu_khi_phu", "he_so_sat_thuong_ra"]


def declare(sheet, tracked=True):
    for col, unit, meaning in COMMON:
        fk = WEAPON_FK if col in ("vu_khi_chinh", "vu_khi_phu") else ["02_phuong_tien/Ky_nang"] if col == "noi_tai" else None
        sheet.col(col, unit=unit, meaning=meaning, fk=fk,
                  source_note="" if col.startswith("ten") else f"{B.BALANCE}: vehicles[*] sau inherits (Catalog.cs)")
    if tracked:
        B.declare_changes(sheet, TRACKED)


def armour_faces(r: dict, structure: bool):
    a = r.get("armour")
    if isinstance(a, list):
        f = list(a) + [None] * (4 - len(a))
        return f[:4]
    if isinstance(a, (int, float)):
        a = int(a)
        if r.get("flying") or structure:
            return [a, a, a, a]
        return [a, max(0, a - 1), max(0, a - 2), max(0, a - 2)]
    if structure:
        return [2, 2, 2, 2]
    return [NEED_CODE_CHECK] * 4


def effective(ctx, vid: str, r: dict, boss: bool = False, view=None) -> dict:
    """The game's values of a resolved record (view: an earlier version, for _truoc)."""
    src = view or ctx
    d = B.bal(src)
    tough = d.get("toughness") or {}
    branches = {c: b for b, classes in (d.get("branches") or {}).items() for c in classes}
    static = bool(r.get("static", False))
    structure = bool(r.get("structure")) if "structure" in r else (static and not boss) or r.get("armor") == "Structure"
    faces = armour_faces(r, structure)
    scale = r.get("scale", 1)
    hp = r.get("hp")
    mult = tough.get("bosses" if boss else "vehicles", 1)
    aps = r.get("aps") if isinstance(r.get("aps"), dict) else None
    flares = "flareCharges" in r or "flares" in r
    en, vi = B.name_of(ctx, f"unit.{vid}", f"boss.{vid}") if view is None else ("", "")
    out = {
        "ten_en": en, "ten_vi": vi,
        "ten_ngan_vi": B.name_of(ctx, f"short.{vid}")[1] if view is None else "",
        "lop": r.get("class", ""),
        "nhanh": branches.get(r.get("class"), ""),
        "ke_thua_tu": r.get("inherits", ""),
        "base_cp": r.get("cp", 0),
        "mau_hp": hp if hp is not None else "",
        "mau_trong_tran_hp": round(hp * mult, 6) if isinstance(hp, (int, float)) else "",
        "giap_truoc": faces[0], "giap_hong": faces[1], "giap_sau": faces[2], "giap_noc": faces[3],
        "cong_trinh": structure,
        "toc_do_m_s": r.get("speed", ""),
        "xoay_than_deg_s": r.get("turnRate", ""),
        "xoay_thap_deg_s": r.get("turretTurnRate", ""),
        "tam_nhin_m": r.get("vision", ""),
        "ban_kinh_m": r.get("radius", ""),
        "dai_m": round(r["length"] * scale, 6) if isinstance(r.get("length"), (int, float)) else "",
        "rong_m": round(r["width"] * scale, 6) if isinstance(r.get("width"), (int, float)) else "",
        "bay": bool(r.get("flying", False)),
        "do_cao_m": r.get("altitude", 0),
        "dung_yen": static,
        "ban_khi_chay": r.get("firesWhileMoving", True),
        "toc_do_chiem": r.get("captureRate", 1),
        # Catalog.Extra.ParseExtras: dropDelay default EconomySystem.DeliverySeconds (3.5) clamped 0.5-30,
        # outgoingDamageMult default 1 clamped 0.1-10
        "tha_du_s": min(30.0, max(0.5, r.get("dropDelay", 3.5))),
        "he_so_sat_thuong_ra": min(10.0, max(0.1, r.get("outgoingDamageMult", 1))),
        "vu_khi_chinh": r.get("weapon", ""),
        "vu_khi_phu": ";".join(m.get("weapon", "") for m in (r.get("secondary") or []) if isinstance(m, dict)),
        "noi_tai": ";".join(r.get("skills", [])) if isinstance(r.get("skills"), list) else "",
        "tu_ve": "aps" if aps else "flare" if flares else "none",
        "so_lan_tu_ve": aps.get("charges", "") if aps else max(0, int(r.get("flareCharges", 0))) if flares else "",
        "hoi_tu_ve_s": aps.get("recharge", "") if aps else r.get("flareRecharge", NEED_CODE_CHECK) if flares else "",
        "mo_hinh": r.get("model") or vid,
    }
    return out


def fill(ctx, row, vid: str, r: dict, boss: bool = False, base_record: dict | None = None, has_base: bool = False,
         tracked=True):
    eff = effective(ctx, vid, r, boss)
    for k, v in eff.items():
        row.set(k, v)
    if tracked:
        base_eff = effective(ctx, vid, base_record, boss, view=B.base_view(ctx)) if base_record is not None else None
        B.set_changes(row, TRACKED, eff, base_eff, has_base)
    return eff


def raw(row, v: dict, path: tuple, children: dict, extra_skip=()):
    """The record's own fields (not the ones 01 exports)."""
    row.flatten(v, B.BALANCE, path, skip=IN_01 + tuple(extra_skip), children=children, vectors=VECTORS)


def mounts_child(sheet_name: str, title: str, book, parent):
    """A child sheet of weapon mounts (secondary[]): vehicle / tower / boss - weapon - slot."""
    ch = book.sheet(sheet_name, title, "secondary[]: bệ phụ (chỉ số bệ = thu_tu + 1; bệ 0 là vũ khí chính)", parent=parent)
    ch.col("weapon", meaning="vũ khí trên bệ", fk=WEAPON_FK)
    return ch


def child(ch):
    return lambda row, items, src, p: child_rows(ch, row, items, src, p, vectors={"arc": ["center_deg", "half_deg"]})
