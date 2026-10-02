# COVERAGE (độ phủ khóa, spec 3.3 và 3.5)

Commit dc121318, bản gốc so sánh origin/main (9198a675). Lá = mọi giá trị lá của mọi nguồn (Nguon_du_lieu).

| Mục | Số |
|---|---|
| Nguồn | 917 |
| Lá | 796955 |
| Đã ánh xạ vào một cột | 18982 |
| Khong_xuat (có lý do) | 1843 |
| Chờ file lĩnh vực chưa xuất | 776130 |
| Chưa ánh xạ (FAIL) | 0 |
| Lá ánh xạ hai nơi (FAIL) | 0 |

## Theo file lĩnh vực

| File | Lá đã ánh xạ | Sheet | Dòng | Ô trống | CHUA_AP | NEED_CODE_CHECK |
|---|---|---|---|---|---|---|
| 01_vu_khi_dan | 6494 | 14 | 739 | 41590 | 372 | 1226 |
| 02_phuong_tien | 5486 | 21 | 576 | 17342 | 0 | 309 |
| 03_boss | 5223 | 33 | 1098 | 15269 | 223 | 569 |
| 04_can_cu_thap | 1778 | 18 | 303 | 8296 | 10 | 307 |

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

## Chờ file lĩnh vực chưa xuất

| Nguồn | Mẫu | File | Lá |
|---|---|---|---|
| Assets/MachineBrigade/Resources/Data/balance.json | `economy.**` | 05_che_do_kinh_te | 47 |
| Assets/MachineBrigade/Resources/Data/balance.json | `matchRules.**` | 05_che_do_kinh_te | 231 |
| Assets/MachineBrigade/Resources/Data/balance.json | `ai.**` | 06_ai | 245 |
| Assets/MachineBrigade/Resources/Data/balance.json | `aiBehaviour.**` | 06_ai | 602 |
| Assets/MachineBrigade/Resources/Data/balance.json | `aiModeProfiles.**` | 06_ai | 358 |
| Assets/MachineBrigade/Resources/Data/balance.json | `generals.**` | 06_ai | 6 |
| Assets/MachineBrigade/Resources/Data/balance.json | `props.**` | 08_ban_do | 860 |
| Assets/MachineBrigade/Resources/Data/balance.json | `neutrals.**` | 08_ban_do | 20 |
| Assets/MachineBrigade/Resources/Data/balance.json | `handbook.**` | 11_meta_giao_dien | 2 |
| Assets/MachineBrigade/Resources/Data/campaign.json | `economy.**` | 05_che_do_kinh_te | 2 |
| Assets/MachineBrigade/Resources/Data/campaign.json | `generals.**` | 06_ai | 99 |
| Assets/MachineBrigade/Resources/Data/campaign.json | `migration*.**` | 12_he_thong_trang_thai | 55 |
| Assets/MachineBrigade/Resources/Data/campaign.json | `**` | 07_chien_dich_cot_truyen | 14372 |
| Assets/MachineBrigade/Resources/Data/script/*.json | `**` | 07_chien_dich_cot_truyen | 13693 |
| Assets/MachineBrigade/Resources/Data/release.json | `**` | 07_chien_dich_cot_truyen | 6 |
| Assets/MachineBrigade/Resources/Data/operations.json | `**` | 05_che_do_kinh_te | 108 |
| Assets/MachineBrigade/Resources/Data/maps/*.json | `**` | 08_ban_do | 644473 |
| Assets/MachineBrigade/Resources/Data/map_dressing.json | `**` | 08_ban_do | 1197 |
| Assets/MachineBrigade/Resources/UI/Bases/*.json | `**` | 11_meta_giao_dien | 964 |
| Assets/MachineBrigade/Resources/UI/Cards/manifest.json | `**` | 10_model_tai_san | 1208 |
| Assets/MachineBrigade/Resources/Models/** | `**` | 10_model_tai_san | 29156 |
| Assets/MachineBrigade/Resources/Licenses/* | `**` | 10_model_tai_san | 374 |
| Assets/MachineBrigade/Resources/Audio/** | `**` | 09_hieu_ung_am_thanh | 365 |
| Assets/MachineBrigade/Settings/BattlefieldProfile.asset | `**` | 09_hieu_ung_am_thanh | 93 |
| Assets/MachineBrigade/Scripts/*.cs | `**` | 10_model_tai_san | 13070 |
| Assets/MachineBrigade/Tests/** | `**` | 12_he_thong_trang_thai | 54 |
| Tools/assets/baseline.json | `**` | 10_model_tai_san | 44506 |
| Tools/models/reference_real.json | `**` | 10_model_tai_san | 574 |
| Tools/docs/unit_refs.json | `**` | 13_tham_chieu_nguon | 696 |
| Tools/docs/unit_sheet.json | `**` | 12_he_thong_trang_thai | 478 |
| Tools/sfx/library.json | `**` | 09_hieu_ung_am_thanh | 301 |
| Tools/story/script/*.txt | `**` | 07_chien_dich_cot_truyen | 1854 |
| Tools/campaign/unlocks_sheet.json | `**` | 11_meta_giao_dien | 111 |
| Tools/campaign/p31_objectives_baseline.json | `**` | 12_he_thong_trang_thai | 96 |
| Tools/balance/*_before.json | `**` | 12_he_thong_trang_thai | 3550 |
| Tools/balance/*_baseline.json | `**` | 12_he_thong_trang_thai | 2304 |

## Chưa ánh xạ

Không có.

## Nguồn không đọc được

Không có.

Chế độ kiểm: thường (lá chờ file chưa xuất được phép).
