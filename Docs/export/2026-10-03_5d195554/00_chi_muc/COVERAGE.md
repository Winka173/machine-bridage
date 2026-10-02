# COVERAGE (độ phủ khóa, spec 3.3 và 3.5)

Commit 5d195554, bản gốc so sánh origin/main (9198a675). Lá = mọi giá trị lá của mọi nguồn (Nguon_du_lieu).

| Mục | Số |
|---|---|
| Nguồn | 1003 |
| Lá | 803070 |
| Đã ánh xạ vào một cột | 800525 |
| Khong_xuat (có lý do) | 1849 |
| Chờ file lĩnh vực chưa xuất | 696 |
| Chưa ánh xạ (FAIL) | 0 |
| Lá ánh xạ hai nơi (FAIL) | 0 |

## Theo file lĩnh vực

| File | Lá đã ánh xạ | Sheet | Dòng | Ô trống | CHUA_AP | NEED_CODE_CHECK |
|---|---|---|---|---|---|---|
| 01_vu_khi_dan | 6494 | 15 | 1111 | 42076 | 0 | 482 |
| 02_phuong_tien | 5486 | 29 | 1014 | 17342 | 0 | 792 |
| 03_boss | 5223 | 39 | 1523 | 15269 | 0 | 164 |
| 04_can_cu_thap | 1778 | 24 | 473 | 8593 | 10 | 231 |
| 05_che_do_kinh_te | 424 | 11 | 179 | 1024 | 0 | 8 |
| 06_ai | 1310 | 13 | 685 | 870 | 0 | 0 |
| 07_chien_dich_cot_truyen | 29881 | 32 | 8881 | 32914 | 2 | 3492 |
| 08_ban_do | 646558 | 39 | 151298 | 200898 | 0 | 0 |
| 09_hieu_ung_am_thanh | 1032 | 16 | 858 | 606 | 2 | 2 |
| 10_model_tai_san | 89732 | 20 | 22609 | 24302 | 519 | 519 |
| 11_meta_giao_dien | 1721 | 24 | 630 | 358 | 2 | 0 |
| 12_he_thong_trang_thai | 10885 | 23 | 15765 | 19217 | 28 | 0 |

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

## Markdown, ảnh và PDF (lượt 6, spec 6)

- md/: 13 file (01_vu_khi_dan.md, 02_phuong_tien.md, 03_boss.md, 04_can_cu_thap.md, 05_che_do_kinh_te.md, 06_ai.md, 07_chien_dich_cot_truyen.md, 08_ban_do.md, 09_hieu_ung_am_thanh.md, 10_model_tai_san.md, 11_meta_giao_dien.md, 12_he_thong_trang_thai.md, Machine_Brigade_Design_FULL_2026-10-03.md).
- images/: 34 ảnh chép từ repo (Docs/doc-images, Docs/models/rebuild); ảnh hiệu ứng Unity: chờ (pending).
- pdf/: Machine_Brigade_Design_2026-10-03.pdf, 118 trang, sinh từ Machine_Brigade_Design_FULL_2026-10-03.md.
- Mục "Chưa áp": không có.
