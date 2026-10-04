"""Resources/Data/tunables.json: the gameplay constants that lived in the C# code and now live in the data (lane B, rule B).

One key-value row per constant, in the sheet of its domain (no 99_ file): weapons and vehicles in 01_chien_dau, bosses in
02_boss, bases in 03_can_cu, modes and AI in 04_che_do_kinh_te_ai, campaign in 05_chien_dich, maps in 06_ban_do. Layout of
the source: group -> owner class -> name -> {value, unit, kind, linh_vuc, code}. Every leaf is mapped, so the coverage test
sees the file whole; `gia_tri_so` / `gia_tri_chu` is the value the game reads (editable: the import maps it to its leaf).
"""
from __future__ import annotations

from . import paths as P
from .model import _leaf_paths, join_list

SID = "Assets/MachineBrigade/Resources/Data/tunables.json"
# group -> (file, sheet, Vietnamese title)
GROUPS = {
    "weapons": ("01_chien_dau", "Hang_so_vu_khi", "Hằng số vũ khí, đạn, sát thương và nổ"),
    "vehicles": ("01_chien_dau", "Hang_so_phuong_tien", "Hằng số phương tiện: giá, thả dù, hồi đạn, tiếp tế, kỹ năng"),
    "bosses": ("02_boss", "Hang_so_boss", "Hằng số boss: đòn lớn, pha, hộ tống"),
    "bases": ("03_can_cu", "Hang_so_can_cu", "Hằng số căn cứ và tháp"),
    "modes": ("04_che_do_kinh_te_ai", "Hang_so_che_do", "Hằng số chế độ, tiếp tế và cờ chế độ"),
    "ai": ("09_ai", "Hang_so_ai", "Hằng số AI"),
    "campaign": ("05_chien_dich", "Hang_so_chien_dich", "Hằng số chiến dịch, biến cố, thoại"),
    "maps": ("06_ban_do", "Hang_so_ban_do", "Hằng số bản đồ và đường đi"),
}
EXTRA_COLS = (("nhom_quet", "kind", "nhóm của bản quét hằng số (thời gian, bán kính, sát thương, ngưỡng, trần, xác suất…)"),
              ("linh_vuc_ma_cu", "linh_vuc", "mã lĩnh vực của bản quét (01–11 là mã file cũ)"),
              ("ma_nguon", "code", "tên C# đọc giá trị này (SimTunables)"))


def build(ctx):
    """Adds the Hang_so_* sheets (one a group of GROUPS) to the pack's books; returns the number of constants. Call after
    restructure."""
    src = ctx.sources.get(SID)
    if src is None or not src.readable:
        return 0
    data = src.data
    sheets = {}
    n = 0
    for group, (fid, name, title) in GROUPS.items():
        block = data.get(group)
        if not isinstance(block, dict) or fid not in ctx.books:
            continue
        sh = ctx.books[fid].kv_sheet(name, title, f"{SID}: '{group}' (lớp chủ → tên): một dòng một hằng số; mã game đọc qua "
                                     "SimTunables, giữ nguyên giá trị khi chuyển từ mã ra dữ liệu")
        sh.cols["nhom"].meaning = "lớp chủ (lớp C# sở hữu hằng số)"
        sh.cols["khoa"].meaning = "tên hằng số"
        sh.cols["don_vi"].meaning = "đơn vị khai báo trong dữ liệu (s, m, x, share 0-1, CP, count, ticks 20/s…)"
        for col, _key, meaning in EXTRA_COLS:
            sh.col(col, meaning=meaning)
        sheets[group] = sh
        for cls, items in block.items():
            for key, entry in items.items():
                base = (group, cls, key)
                r = sh.row(f"{group}.{cls}.{key}", f"{SID}: {P.to_str(base)}", raw=entry)
                r.values["nhom"] = cls
                r.values["khoa"] = key
                value = entry.get("value")
                vpath = base + ("value",)
                if isinstance(value, list):
                    r.set("gia_tri_chu", join_list(value))
                    for leaf in _leaf_paths(value, vpath):
                        r.mark(SID, leaf, "gia_tri_chu")
                elif isinstance(value, (bool, int, float)):
                    r.set("gia_tri_so", value, SID, vpath)
                else:
                    r.set("gia_tri_chu", "" if value is None else str(value), SID, vpath)
                r.set("don_vi", entry.get("unit", ""), SID, base + ("unit",))
                for col, field, _m in EXTRA_COLS:
                    r.set(col, entry.get(field, ""), SID, base + (field,))
                n += 1
    return n
