# COVERAGE (độ phủ khóa, spec 3.3 và 3.5)

Commit 382d5fb9, bản gốc so sánh origin/main (9198a675). Lá = mọi giá trị lá của mọi nguồn (Nguon_du_lieu).

| Mục | Số |
|---|---|
| Nguồn | 999 |
| Lá | 802226 |
| Đã ánh xạ vào một cột | 799681 |
| Khong_xuat (có lý do) | 1849 |
| Chờ file lĩnh vực chưa xuất | 696 |
| Chưa ánh xạ (FAIL) | 0 |
| Lá ánh xạ hai nơi (FAIL) | 0 |

## Theo file lĩnh vực

| File | Lá đã ánh xạ | Sheet | Dòng | Ô trống | CHUA_AP | NEED_CODE_CHECK |
|---|---|---|---|---|---|---|
| 01_vu_khi_dan | 6494 | 14 | 739 | 41590 | 372 | 1226 |
| 02_phuong_tien | 5486 | 21 | 576 | 17342 | 0 | 309 |
| 03_boss | 5223 | 33 | 1098 | 15269 | 223 | 569 |
| 04_can_cu_thap | 1778 | 18 | 303 | 8296 | 10 | 307 |
| 05_che_do_kinh_te | 424 | 8 | 87 | 895 | 0 | 8 |
| 06_ai | 1310 | 12 | 258 | 870 | 1 | 0 |
| 07_chien_dich_cot_truyen | 29881 | 28 | 5594 | 32721 | 2 | 3492 |
| 08_ban_do | 646558 | 35 | 151147 | 200157 | 0 | 0 |
| 09_hieu_ung_am_thanh | 1032 | 12 | 605 | 570 | 2 | 8 |
| 10_model_tai_san | 88888 | 15 | 21650 | 20745 | 519 | 519 |
| 11_meta_giao_dien | 1721 | 21 | 585 | 343 | 2 | 1 |
| 12_he_thong_trang_thai | 10885 | 23 | 8508 | 19212 | 5768 | 0 |

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
| Tools/docs/unit_refs.json | `**` | 13_tham_chieu_nguon | 696 |

## Chưa ánh xạ

Không có.

## Nguồn không đọc được

Không có.

Chế độ kiểm: thường (lá chờ file chưa xuất được phép).
