"""Leaves claimed by domain files not built yet (coverage counts them as pending, not unmapped).

(source glob, leaf pattern, the domain file that will export it, note). When a lane registers its module in
domains/__init__.py it deletes its lines here; a claim whose file is built no longer excuses a leaf. Unclassified
sources (spec 3.2) are claimed by 12_he_thong_trang_thai (sheet Khac_chua_phan_loai).
"""

BAL = "Assets/MachineBrigade/Resources/Data/balance.json"
DATA = "Assets/MachineBrigade/Resources/Data/"

CLAIMS = [
    # ---------------------------------------------------------------- balance.json blocks of later files
    # ---------------------------------------------------------------- other data files
    # ---------------------------------------------------------------- Tools data
    ("Tools/docs/unit_refs.json", "**", "13_tham_chieu_nguon", "tham chiếu ngoài đời / game theo đơn vị (spec 12.1)"),
]
