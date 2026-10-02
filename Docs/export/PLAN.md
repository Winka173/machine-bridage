# Bộ xuất dữ liệu toàn bộ: kế hoạch (lượt 0)

Spec: `Docs/prompts/export_full_vi.txt` (cả phần bổ sung mục 12, lượt 10). Công cụ: `Tools/export/` (Python 3.11,
openpyxl 3.1.5). Một lệnh: `python Tools/export/export.py [--out DIR] [--base REF] [--strict]`. Bộ xuất chỉ đọc,
không đổi giá trị game nào.

Số liệu dưới đây đếm bằng chính bộ xuất (commit 331065ab, 03/10): sheet `00_chi_muc/Nguon_du_lieu` liệt kê từng
nguồn, số lá, số lá đã ánh xạ / Khong_xuat / chờ.

## 1. Nguồn (tự quét Assets/ và Tools/; bỏ .meta, Library, Temp, Logs, Docs/export)

| Nguồn | Loại | File | Lá | File lĩnh vực |
|---|---|---|---|---|
| Resources/Data/balance.json | JSONC | 1 | 20 013 | 01, 02, 03, 04 (đã xuất); 05, 06, 08, 11 (chờ); `version` vào 00 |
| Resources/Data/campaign.json | JSON | 1 | 14 528 | 07 (chương, nhiệm vụ, biến cố); 05 (economy); 06 (generals); 12 (migration) |
| Resources/Data/script/ch01-15.json, speakers.json | JSON | 16 | 13 693 | 07 (thoại, người nói, trigger) |
| Resources/Data/maps/*.json (25 bản đồ x 4 biến thể) | JSON | 100 | 644 473 | 08 (lưới / vật thể: lane 08 quyết tóm tắt hay Khong_xuat) |
| Resources/Data/map_dressing.json | JSON | 1 | 1 197 | 08 |
| Resources/Data/operations.json | JSON | 1 | 108 | 05 (Tác chiến, mutator) |
| Resources/Data/release.json | JSONC | 1 | 6 | 07 |
| Resources/UI/Bases/*.json | JSON | 20 | 964 | 11 (ảnh bản đồ căn cứ) |
| Resources/UI/Cards/manifest.json | JSON | 1 | 1 208 | 10 (ảnh thẻ) |
| Resources/Models/*.glb | GLB (đọc bằng Tools/assets/glb_analyze.read_glb) | 518 | 29 156 (tên nút, vật liệu, mesh, số tam giác) | 10 |
| Resources/Audio/** (wav / ogg) | audio | 189 | 189 | 09 |
| Resources/Audio/sfx/envelopes.txt | TXT | 1 | 176 | 09 |
| Resources/Licenses/*.txt | TXT | 5 | 374 | 10 |
| Scripts/Game/Hud/*.cs bảng chữ Việt / Anh | C# (bảng `["key"] = ("en", "vi")`) | 15 | 13 070 | 10 (Dia_phuong_hoa); 01-04 chỉ đọc tên |
| Scripts: GearCatalog.cs (Bases, Modules, Traits, Subs, Brands) | C# bảng hằng | 5 bảng | 945 | 02 |
| Scripts: Commanders.cs (All, Generals) | C# bảng hằng | 2 bảng | 254 | 02 |
| Scripts: BossHunt.cs (HuntSupports.All), BossHunts.cs (Unslotted) | C# bảng hằng | 2 bảng | 78 | 03 |
| Settings/BattlefieldProfile.asset | Unity YAML | 1 | 153 | 09 (hậu kỳ hình ảnh) |
| Assets/Settings/*.asset, VulkanDeviceFilters.asset, Scenes/Sandbox.unity | Unity YAML | 8 | 2 556 | Khong_xuat (render, thiết bị, bố cục cảnh: không có trường lối chơi) |
| Tests/EditMode/Scenarios/*.json | JSON | 1 | 54 | 12 (Test) |
| Tools/assets/baseline.json | JSON | 1 | 44 506 | 10 (chuẩn kiểm model) |
| Tools/models/reference_real.json | JSON | 1 | 574 | 10 (kích thước thật), 13 |
| Tools/docs/unit_refs.json | JSON | 1 | 696 | 13 (tham chiếu ngoài đời / game, spec 12.1) |
| Tools/docs/unit_sheet.json | JSON | 1 | 478 | 12 (Khac_chua_phan_loai) |
| Tools/balance/fix_weapon_reasons.json | JSON | 1 | 63 | 01 (Vu_khi.ly_do_sua) |
| Tools/balance/*_before.json, *_baseline.json, Tools/campaign/p31_objectives_baseline.json | JSON | 5 | 5 670 | 12 (Lich_su_do) |
| Tools/campaign/unlocks_sheet.json | JSON | 1 | 111 | 11 |
| Tools/sfx/library.json | JSON | 1 | 301 | 09 |
| Tools/story/script/ch*.txt | TXT | 15 | 1 854 | 07 (kịch bản gốc dựng ra script/*.json) |
| Tools/music/requirements.txt | TXT | 1 | 7 | Khong_xuat (gói Python) |

Tổng 917 nguồn, 796 955 lá. Không có prefab; 8 ScriptableObject (.asset) đều là cài đặt render / hậu kỳ.
Bảng hằng C# khác (TowerRoster, EscortDefs, EventDefs, BossTemplates...) và số cứng trong mã: lượt 5 (Hang_so_trong_ma);
đọc chúng dùng `ctx.cs_table(path, array)` (Tools/export/core/cs.py đọc mảng hằng C# không cần biên dịch).

Giá trị chỉ mã C# tính: ghi `NEED_CODE_CHECK`. Không dùng `game.json` của ExportGameDoc: bản duy nhất tìm thấy nằm ngoài
repo (thư mục Projects, 02/10 08:22), cũ hơn balance.json hiện tại, và CI không chạy lại được. Chỗ nào luật C# là phép
gộp đơn giản thì bộ xuất port sang Python và ghi nguồn: Catalog.Inherited (inherits), WeaponFamilies (weaponFamily),
SecondRounds.StripRoundLinks, mặt giáp (Armour.cs), toughness, mặc định của ParseExtras (dropDelay 3,5, outgoingDamageMult 1),
Catalog.EliteCost, BossTemplates.Expand (qua Tools/balance/p26_ab.expand có sẵn), BossHunts.Story.

## 2. Ước lượng sheet / cột mỗi file lĩnh vực

| File | Sheet (ước lượng) | Cột / sheet chính | Ghi chú |
|---|---|---|---|
| 01_vu_khi_dan | 14 (đã xuất) | Vu_khi 165 | + Vu_khi_suy_ra (lớp B) |
| 02_phuong_tien | 21 (đã xuất) | Xe 193 | + Xe_suy_ra, Hoi_quy, May_bay_so_phat, Doi_mo_man_suy_ra |
| 03_boss | 34 (đã xuất) | Boss 328 | + Boss_hieu_qua, Boss_dps, input_xe_tham_chieu |
| 04_can_cu_thap | 18 (đã xuất) | Thap 153 | + Thap_gia_cong_thuc, Tuong_duong_xe_cong_trinh, Nha_chinh_so_sanh, input_xe |
| 05_che_do_kinh_te | ~12 | Che_do ~40 | matchRules (231 lá), economy (47), operations.json (108), campaign economy |
| 06_ai | ~8 | AI_ho_so_che_do ~60 | ai (245), aiBehaviour (602), aiModeProfiles (358), generals |
| 07_chien_dich_cot_truyen | ~12 | Nhiem_vu ~120, Thoai ~15 | 15 chương, 193 nhiệm vụ, ~1 900 câu thoại, 23 bộ bài game |
| 08_ban_do | ~14 | Ban_do ~30, Ban_do_vat_the ~12 | 100 file bản đồ: vật thể ~100 nghìn dòng; lưới địa hình nên tóm tắt (hash) hoặc Khong_xuat |
| 09_hieu_ung_am_thanh | ~8 | Am_thanh ~12 | 189 clip, sfx/library.json, envelopes.txt, BattlefieldProfile |
| 10_model_tai_san | ~8 | Model ~25, Dia_phuong_hoa 4 | 518 GLB, ~6 500 khóa chữ, baseline.json, reference_real.json, giấy phép |
| 11_meta_giao_dien | ~12 | tùy bảng | UI/Bases, unlocks_sheet.json, handbook; meta (xu, hòm, cửa hàng) phần lớn trong C# |
| 12_he_thong_trang_thai | ~11 | tùy bảng | Docs/prompts, DECISIONS, test, validator, lịch sử đo, Hang_so_trong_ma |
| 13_tham_chieu_nguon | 5 + <file>_tham_chieu / _so_sanh_that ở 01-11 | ~20 | lượt 10 (spec 12) |

## 3. Thực thể chưa phân loại chắc (vào 12/Khac_chua_phan_loai nếu lane sau không nhận)

- Tests/EditMode/Scenarios/platoon_beats_light_tank.json: kịch bản test, tạm cho 12 (Test).
- Tools/docs/unit_sheet.json: bảng đơn vị của tài liệu cũ, tạm cho 12.
- Resources/UI/Bases/*.json (ảnh bản đồ căn cứ): tạm 11, có thể là 08.
- Resources/UI/Cards/manifest.json (camera render thẻ): tạm 10.
- Settings/BattlefieldProfile.asset (bloom, màu): tạm 09.
- balance.json `handbook` (xe mẫu của sổ tay đạn): tạm 11.
- Lá phải ánh xạ của lượt sau nằm trong `Tools/export/domains/_pending.py` (sheet 00/Cho_anh_xa).

## 4. Dữ liệu tham chiếu đã có trong repo (cho lượt 10, spec 12.1)

- Tools/docs/unit_refs.json (tham chiếu theo đơn vị, nhãn "ước đoán" giữ là uoc_dinh).
- Tools/models/reference_real.json (kích thước thật của mẫu).
- Bảng REAL trong Tools/balance/full_weapon_audit.py (nhịp bắn thật, mỗi dòng có nguồn): đã xuất ở 01/Vu_khi.ngoai_doi_*.
- Ghi chú tham chiếu trong script Blender (Tools/blender/build_assets.py, mb_p20_bosses.py, mb_p22_content.py, mb_parts27.py,
  mb_gear_icons2.py có chữ "reference").
- Cột "Ngoài đời" / "Tham khảo" / "Tham khảo game" / "Cảm giác khác" trong file Excel cũ (Docs không nằm trong vùng quét của
  spec 3.1, lane 10 đọc riêng): Docs/balance/Machine_Brigade_Can_bang.xlsx và _applied (Boss, Boss mới, Công trình,
  Công trình mới, Giá CP: "Giá ngoài đời (USD, ước lượng)"), Docs/ai/Machine_Brigade_AI_Research.xlsx và _applied
  (Chiến thuật, Vai trò, Boss, Công trình), Docs/story/Machine_Brigade_Cot_truyen_Che_do_v2.xlsx (Kết trận).
- Không có số ngoài đời nào được điền từ trí nhớ; thiếu nguồn ghi NEED_SOURCE.

## 5. Khung cho lane sau

- Một file lĩnh vực = một module `Tools/export/domains/dNN_<tên>.py` (FILE_ID, TITLE, DESC, build(ctx)) + một dòng trong
  `domains/__init__.py` DOMAINS; xóa các claim của nó trong `domains/_pending.py`.
- Sheet: `book.sheet(name, title_vi, desc, parent=...)`, `row = sheet.row(id, nguon, raw=record)`,
  `row.flatten(record, source_id, path)` (mọi trường thành cột, đánh dấu độ phủ), `row.set(col, value, source_id, path)`;
  khối cài đặt: `book.kv_sheet` + `book.kv_rows`. Khóa ngoại: `sheet.col(name, fk=["02_phuong_tien/Xe"])`.
- Sheet tham chiếu (lượt 10): `<tên>_tham_chieu`, `<tên>_so_sanh_that` là sheet thường trong cùng module; file 13 là một
  domain như các file khác; cột `nguon_id` khai báo `fk=["13_tham_chieu_nguon/Nguon_tham_chieu"]`.
