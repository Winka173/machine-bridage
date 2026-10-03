# COVERAGE (độ phủ khóa, spec 3.3 và 3.5)

Commit 90337539, bản gốc so sánh origin/main (9198a675). Lá = mọi giá trị lá của mọi nguồn (Nguon_du_lieu).

| Mục | Số |
|---|---|
| Nguồn | 1003 |
| Lá | 803070 |
| Đã ánh xạ vào một cột | 801221 |
| Khong_xuat (có lý do) | 1849 |
| Chờ file lĩnh vực chưa xuất | 0 |
| Chưa ánh xạ (FAIL) | 0 |
| Lá ánh xạ hai nơi (FAIL) | 0 |

## Theo file lĩnh vực

| File | Lá đã ánh xạ | Sheet | Dòng | Ô trống | CHUA_AP | NEED_CODE_CHECK |
|---|---|---|---|---|---|---|
| 01_vu_khi_dan | 6494 | 17 | 1762 | 46669 | 0 | 490 |
| 02_phuong_tien | 5797 | 32 | 1521 | 20464 | 0 | 792 |
| 03_boss | 5372 | 44 | 1851 | 15989 | 0 | 164 |
| 04_can_cu_thap | 2013 | 28 | 676 | 10141 | 10 | 231 |
| 05_che_do_kinh_te | 424 | 13 | 192 | 1164 | 0 | 8 |
| 06_ai | 1310 | 15 | 742 | 1400 | 0 | 0 |
| 07_chien_dich_cot_truyen | 29881 | 35 | 9134 | 35455 | 2 | 3492 |
| 08_ban_do | 646558 | 41 | 151332 | 201277 | 0 | 0 |
| 09_hieu_ung_am_thanh | 1032 | 20 | 1593 | 1223 | 0 | 2 |
| 10_model_tai_san | 89732 | 23 | 22833 | 25602 | 0 | 519 |
| 11_meta_giao_dien | 1721 | 26 | 1046 | 2850 | 2 | 0 |
| 12_he_thong_trang_thai | 10885 | 23 | 15913 | 19498 | 28 | 0 |
| 13_tham_chieu_nguon | 1 | 7 | 6582 | 3706 | 0 | 0 |

## Khong_xuat

| Nguồn | Mẫu | Lá | Lý do |
|---|---|---|---|
| Assets/Settings/*.asset | `**` | 1322 | cấu hình render URP (không có trường lối chơi) |
| Assets/MachineBrigade/Settings/VulkanDeviceFilters.asset | `**` | 17 | bộ lọc thiết bị Vulkan (không có trường lối chơi) |
| Assets/MachineBrigade/Scenes/*.unity | `**` | 437 | cảnh Unity: chỉ bố cục khởi động; lối chơi đọc từ dữ liệu lúc chạy (SceneBuilder dựng cảnh) |
| Tools/music/requirements.txt | `**` | 7 | danh sách gói Python của công cụ nhạc (không phải dữ liệu game) |
| *.asset | `docs[*]._class` | 6 | mã lớp Unity của tài liệu YAML (siêu dữ liệu) |
| *.asset | `docs[*]._file_id` | 6 | mã đối tượng Unity (siêu dữ liệu) |
| *.asset | `docs[*].*.m_ObjectHideFlags` | 6 | cờ ẩn của Unity (siêu dữ liệu) |
| *.asset | `docs[*].*.m_CorrespondingSourceObject` | 6 | liên kết prefab của Unity (siêu dữ liệu) |
| *.asset | `docs[*].*.m_PrefabInstance` | 6 | liên kết prefab của Unity (siêu dữ liệu) |
| *.asset | `docs[*].*.m_PrefabAsset` | 6 | liên kết prefab của Unity (siêu dữ liệu) |
| *.asset | `docs[*].*.m_GameObject` | 6 | liên kết GameObject của Unity (siêu dữ liệu) |
| *.asset | `docs[*].*.m_Script` | 6 | guid script của Unity (siêu dữ liệu) |
| *.asset | `docs[*].*.m_EditorHideFlags` | 6 | cờ editor của Unity (siêu dữ liệu) |
| *.asset | `docs[*].*.m_EditorClassIdentifier` | 6 | định danh editor của Unity (siêu dữ liệu) |
| Assets/MachineBrigade/Settings/BattlefieldProfile.asset | `docs[*].MonoBehaviour.components._items[*].*` | 5 | VolumeProfile.components: id tài liệu Unity của các hiệu ứng (siêu dữ liệu; mỗi hiệu ứng là một dòng ở Hau_ky_hinh_anh) |
| Docs/checks/fix_validate.json | `models.summary.scanDir` | 1 | bảo mật: đường dẫn tuyệt đối máy cá nhân (spec 8) |

## Chờ file lĩnh vực chưa xuất

| Nguồn | Mẫu | File | Lá |
|---|---|---|---|

## Chưa ánh xạ

Không có.

## Nguồn không đọc được

Không có.

## Lớp tham chiếu ngoài đời và game (spec 12.6, lượt 10)

Trạng thái: DAT. Chỉ dữ liệu trong repo (không tra web); thiếu nguồn ghi NEED_SOURCE.

**1. Phủ thực thể** (mỗi xe, vũ khí, tháp, boss, nhà chính, tường có dòng tham chiếu; gia_tuong phải có ly_do):

| loại | số thực thể | có dòng | có tham chiếu | NEED_SOURCE | gia_tuong | gia_tuong thiếu ly_do |
|---|---:|---:|---:|---:|---:|---:|
| xe | 120 | 120 | 75 | 45 | 0 | 0 |
| vũ khí | 372 | 372 | 371 | 1 | 0 | 0 |
| tháp | 76 | 76 | 52 | 24 | 0 | 0 |
| boss | 41 | 41 | 35 | 6 | 2 | 0 |
| nhà chính | 4 | 4 | 1 | 3 | 0 | 0 |
| tường | 3 | 3 | 2 | 1 | 0 | 0 |

**2. Nguồn:** 179 dòng Nguon_tham_chieu; 5431 lần trỏ nguon_id; mồ côi (nguon_id không có ở Nguon_tham_chieu): 0; nguồn không có URL lẫn tiêu đề: 0; có tiêu đề in rõ nhưng không URL (repo không ghi URL): 174; nguồn không ai trỏ: 4.

**3. Cột thông số ngoài đời** (ngoai_doi_*, quoc_gia, nam_dua_vao_su_dung): 1812 ô có giá trị (mỗi ô trên dòng có nguon_id), 4353 ô NEED_SOURCE; ô có giá trị mà dòng không có nguon_id: 0.

**4. Cơ chế lấy ý từ game:** 182 dòng Tham_chieu_game_co_che; 115 lần một dòng tham chiếu nêu game; thiếu dòng cơ chế: 0.

**5. So sánh game với thật** (co_lech_lon = ngoài khoảng mà không có chủ đích):

| sheet | dòng | ngoài khoảng có chủ đích (có ly_do) | co_lech_lon | trong đó có ly_do | có dòng Cho_quyet | không ly_do, không Cho_quyet |
|---|---:|---:|---:|---:|---:|---:|
| 01_vu_khi_dan/Vu_khi_so_sanh_that | 279 | 58 | 77 | 0 | 77 | 0 |
| 02_phuong_tien/Phuong_tien_so_sanh_that | 269 | 51 | 39 | 0 | 39 | 0 |
| 03_boss/Boss_so_sanh_that | 122 | 40 | 6 | 0 | 6 | 0 |
| 04_can_cu_thap/Can_cu_so_sanh_that | 37 | 6 | 17 | 0 | 17 | 0 |
| tổng | 707 | 155 | 139 | 0 | 139 | 0 |

**6. Độ tin cậy theo lĩnh vực** (dòng của các sheet <tên>_tham_chieu):

| file | dòng | da_kiem_chung | uoc_dinh | ban_dau_doan | NEED_SOURCE | gia_tuong (loại) |
|---|---:|---:|---:|---:|---:|---:|
| 01_vu_khi_dan | 372 | 263 (71%) | 60 (16%) | 48 (13%) | 1 (0%) | 0 |
| 02_phuong_tien | 160 | 26 (16%) | 32 (20%) | 17 (11%) | 85 (53%) | 0 |
| 03_boss | 41 | 9 (22%) | 18 (44%) | 8 (20%) | 6 (15%) | 2 |
| 04_can_cu_thap | 96 | 0 (0%) | 22 (23%) | 44 (46%) | 30 (31%) | 0 |
| 05_che_do_kinh_te | 12 | 0 (0%) | 0 (0%) | 1 (8%) | 11 (92%) | 0 |
| 06_ai | 56 | 14 (25%) | 0 (0%) | 30 (54%) | 12 (21%) | 0 |
| 07_chien_dich_cot_truyen | 252 | 0 (0%) | 0 (0%) | 0 (0%) | 252 (100%) | 0 |
| 08_ban_do | 33 | 0 (0%) | 0 (0%) | 0 (0%) | 33 (100%) | 0 |
| 09_hieu_ung_am_thanh | 55 | 0 (0%) | 0 (0%) | 0 (0%) | 55 (100%) | 0 |
| 10_model_tai_san | 107 | 41 (38%) | 34 (32%) | 31 (29%) | 1 (1%) | 21 |
| 11_meta_giao_dien | 13 | 0 (0%) | 0 (0%) | 0 (0%) | 13 (100%) | 0 |
| tổng | 1197 | 353 (29%) | 166 (14%) | 179 (15%) | 499 (42%) | |

Thiếu nguồn (13/Thieu_nguon): 5840 ô NEED_SOURCE (ưu tiên 1: 4028, 2: 528, 3: 1284).


Chế độ kiểm: thường (lá chờ file chưa xuất được phép).

## Markdown, ảnh và PDF (lượt 6, spec 6)

- md/: 14 file (01_vu_khi_dan.md, 02_phuong_tien.md, 03_boss.md, 04_can_cu_thap.md, 05_che_do_kinh_te.md, 06_ai.md, 07_chien_dich_cot_truyen.md, 08_ban_do.md, 09_hieu_ung_am_thanh.md, 10_model_tai_san.md, 11_meta_giao_dien.md, 12_he_thong_trang_thai.md, 13_tham_chieu_nguon.md, Machine_Brigade_Design_FULL_2026-10-03.md).
- images/: 35 ảnh chép từ repo (Docs/doc-images, Docs/models/rebuild); ảnh hiệu ứng Unity: chờ (pending).
- pdf/: Machine_Brigade_Design_2026-10-03.pdf, 133 trang, sinh từ Machine_Brigade_Design_FULL_2026-10-03.md.
- Mục "Chưa áp": không có.
