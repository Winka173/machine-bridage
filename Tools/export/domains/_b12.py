"""12_he_thong_trang_thai, pass 5: Hang_so_trong_ma (spec 5) from Tools/export/scan_constants.scan(repo root): every gameplay
constant and hard-coded number of the game's C# (Sim/** and Game/**), one row each, id = <file>:<line>:<column>, rows in
natural id order (file, line, column), columns in scan_constants.COLUMNS order. Read only: no code is changed."""
from __future__ import annotations

import sys

from core.repo import ROOT

TOOL = "Tools/export/scan_constants.py"


def build(ctx, book):
    sys.path.insert(0, str(ROOT / "Tools" / "export"))
    try:
        import scan_constants as S  # noqa: WPS433
    finally:
        sys.path.pop(0)
    sh = book.sheet("Hang_so_trong_ma", "Hằng số trong mã", "Mọi hằng số và số cứng ảnh hưởng lối chơi (spec 5): tệp, dòng, tên, "
                    "giá trị, ngữ cảnh, loại, nhóm, lĩnh vực liên quan (01-11), đề xuất đưa ra dữ liệu (đề xuất của bản quét "
                    f"{TOOL}, chủ dự án duyệt); chú thích và chuỗi trong mã không được đọc")
    sh.col("id", meaning="<tệp>:<dòng>:<cột>")
    enums = {"loai": ["const", "static_readonly", "mac_dinh_thuoc_tinh", "mac_dinh_doc_du_lieu", "so_cung"],
             "nhom": ["sat_thuong", "thoi_gian", "ban_kinh", "nguong", "xac_suat", "tran", "tan_suat", "gioi_han_thuc_the", "khac"],
             "de_xuat_dua_ra_du_lieu": ["co", "khong"]}
    for name, unit, meaning in S.COLUMNS:
        sh.col(name, unit=unit, meaning=meaning, enum=enums.get(name), source_note=f"python: {TOOL} scan")
    sh.col("cot", meaning="cột trong dòng (1 = đầu dòng)", source_note=f"python: {TOOL} scan")
    rows = S.scan(ROOT)
    for r in rows:
        x = sh.row(r["id"], f"{r['tep']}:{r['dong']}")
        for name, _u, _m in S.COLUMNS:
            x.set(name, r.get(name, ""))
        x.set("cot", r.get("cot", ""))
    return len(rows)


def stale(ctx, ld):
    """Lich_su_do.stale (pass 5): STALE when the data a measurement read (balance.json; campaign.json for the p31 objectives)
    changed in a commit after the measurement file's own last commit (git), else OK; commit_do = that commit's short hash."""
    from . import _layer_b as LB
    bal = "Assets/MachineBrigade/Resources/Data/balance.json"
    camp = "Assets/MachineBrigade/Resources/Data/campaign.json"
    srcs = sorted({str(r.nguon).split(":", 1)[0] for r in ld.rows.values()})
    commits = LB.git_last_commit(srcs + [bal, camp])
    ld.col("stale", meaning="STALE: dữ liệu đo (balance.json; p31: campaign.json) đổi ở commit sau commit cuối của file số đo (git); OK: chưa đổi",
           enum=["STALE", "OK"])
    ld.col("commit_do", meaning="commit cuối của file số đo (mốc đo)")
    for r in ld.rows.values():
        f = str(r.nguon).split(":", 1)[0]
        data = camp if "p31_objectives" in f else bal
        t_m, h = commits.get(f, (0, ""))
        t_d = commits.get(data, (0, ""))[0]
        r.set("stale", "STALE" if t_d > t_m else "OK")
        r.set("commit_do", h)
