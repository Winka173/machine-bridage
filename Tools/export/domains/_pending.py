"""Leaves claimed by domain files not built yet (coverage counts them as pending, not unmapped).

(source glob, leaf pattern, the domain file that will export it, note). When a lane registers its module in
domains/__init__.py it deletes its lines here; a claim whose file is built no longer excuses a leaf. Unclassified
sources (spec 3.2) are claimed by 12_he_thong_trang_thai (sheet Khac_chua_phan_loai).
"""

BAL = "Assets/MachineBrigade/Resources/Data/balance.json"
DATA = "Assets/MachineBrigade/Resources/Data/"

CLAIMS = [
    # ---------------------------------------------------------------- balance.json blocks of later files
    (BAL, "economy.**", "05_che_do_kinh_te", "kinh tế, CP, thu nhập, trần"),
    (BAL, "matchRules.**", "05_che_do_kinh_te", "luật trận theo chế độ"),
    (BAL, "ai.**", "06_ai", "tham số AI (prompt 28 L)"),
    (BAL, "aiBehaviour.**", "06_ai", "chiến thuật, hành vi AI"),
    (BAL, "aiModeProfiles.**", "06_ai", "hồ sơ AI theo chế độ"),
    (BAL, "generals.**", "06_ai", "tướng địch: elite ưa thích, bài thêm"),
    (BAL, "props.**", "08_ban_do", "vật thể bản đồ"),
    (BAL, "neutrals.**", "08_ban_do", "trung lập"),
    (BAL, "handbook.**", "11_meta_giao_dien", "ví dụ của sổ tay đạn trên giao diện"),
    # ---------------------------------------------------------------- other data files
    (DATA + "campaign.json", "economy.**", "05_che_do_kinh_te", "kinh tế chiến dịch"),
    (DATA + "campaign.json", "generals.**", "06_ai", "tướng địch của chiến dịch (bộ bài, phong cách)"),
    (DATA + "campaign.json", "migration*.**", "12_he_thong_trang_thai", "chuyển đổi save cũ"),
    (DATA + "campaign.json", "**", "07_chien_dich_cot_truyen", "chương, nhiệm vụ, biến cố"),
    (DATA + "script/*.json", "**", "07_chien_dich_cot_truyen", "thoại, người nói, trigger"),
    (DATA + "release.json", "**", "07_chien_dich_cot_truyen", "phần chiến dịch bản phát hành mở"),
    (DATA + "operations.json", "**", "05_che_do_kinh_te", "Tác chiến: bậc, điểm, tuần, mutator"),
    (DATA + "maps/*.json", "**", "08_ban_do", "bản đồ (lưới địa hình: tóm tắt hoặc Khong_xuat do lane 08 quyết)"),
    (DATA + "map_dressing.json", "**", "08_ban_do", "trang trí, biome, địa danh"),
    ("Assets/MachineBrigade/Resources/UI/Bases/*.json", "**", "11_meta_giao_dien", "ảnh bản đồ căn cứ của màn Căn cứ"),
    ("Assets/MachineBrigade/Resources/UI/Cards/manifest.json", "**", "10_model_tai_san", "ảnh thẻ (render model)"),
    ("Assets/MachineBrigade/Resources/Models/**", "**", "10_model_tai_san", "model GLB"),
    ("Assets/MachineBrigade/Resources/Licenses/*", "**", "10_model_tai_san", "giấy phép tài sản"),
    ("Assets/MachineBrigade/Resources/Audio/**", "**", "09_hieu_ung_am_thanh", "âm thanh"),
    ("Assets/MachineBrigade/Settings/BattlefieldProfile.asset", "**", "09_hieu_ung_am_thanh", "hậu kỳ hình ảnh (bloom, màu)"),
    ("Assets/MachineBrigade/Scripts/*.cs", "**", "10_model_tai_san", "bảng chữ Việt / Anh (localization)"),
    ("Assets/MachineBrigade/Tests/**", "**", "12_he_thong_trang_thai", "kịch bản test EditMode"),
    # ---------------------------------------------------------------- Tools data
    ("Tools/assets/baseline.json", "**", "10_model_tai_san", "chuẩn kiểm model (baseline)"),
    ("Tools/models/reference_real.json", "**", "10_model_tai_san", "kích thước thật tham chiếu (cũng dùng ở 13)"),
    ("Tools/docs/unit_refs.json", "**", "13_tham_chieu_nguon", "tham chiếu ngoài đời / game theo đơn vị (spec 12.1)"),
    ("Tools/docs/unit_sheet.json", "**", "12_he_thong_trang_thai", "bảng đơn vị của tài liệu"),
    ("Tools/sfx/library.json", "**", "09_hieu_ung_am_thanh", "thư viện âm thanh"),
    ("Tools/story/script/*.txt", "**", "07_chien_dich_cot_truyen", "kịch bản thoại gốc (dựng ra script/*.json)"),
    ("Tools/campaign/unlocks_sheet.json", "**", "11_meta_giao_dien", "mở khóa"),
    ("Tools/campaign/p31_objectives_baseline.json", "**", "12_he_thong_trang_thai", "mốc đo mục tiêu (lịch sử đo)"),
    ("Tools/balance/*_before.json", "**", "12_he_thong_trang_thai", "mốc trước sửa (lịch sử đo)"),
    ("Tools/balance/*_baseline.json", "**", "12_he_thong_trang_thai", "mốc đo (lịch sử đo)"),
]
