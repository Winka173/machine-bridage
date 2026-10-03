# Báo cáo bộ xuất dữ liệu toàn bộ (spec 11 và 12.7)

Bản xuất `Docs/export/2026-10-03_90337539/` (commit 90337539), lệnh `python Tools/export/export.py check`. Lượt 0-10 của `Docs/prompts/export_full_vi.txt` đã chạy (lượt 9 nhập ngược: lane B). Chỉ đọc: không giá trị game nào đổi; không chạy Unity, test, mô phỏng hay đo. Lượt 10 không tra web (quyết định của chủ dự án): chỉ dữ liệu có trong repo.

## Tự kiểm

| Kiểm | Kết quả |
|---|---|
| 1 | DAT |
| 2 | DAT |
| 3 | DAT |
| 4 | DAT |
| 5 | DAT |
| 6 | DAT |
| 7 | DAT |
| 8 | DAT |
| 9 | DAT |
| 12.6 | DAT  co_lech_lon {'rows': 707, 'chu': 155, 'lech': 139, 'why': 0, 'cq': 139, 'none': 0}  NEED_SOURCE rows 499 |
| CI | coverage ok, foreign_keys ok, determinism ok, secrets ok |

## File, sheet, dòng, cột

| file | tiêu đề | sheet | dòng | cột |
|---|---|---:|---:|---:|
| 00_chi_muc | Chỉ mục | 14 | 7862 | 130 |
| 01_vu_khi_dan | Vũ khí và đạn | 17 | 1762 | 429 |
| 02_phuong_tien | Phương tiện | 32 | 1521 | 584 |
| 03_boss | Boss | 44 | 1851 | 805 |
| 04_can_cu_thap | Căn cứ và tháp | 28 | 676 | 666 |
| 05_che_do_kinh_te | Chế độ và kinh tế | 13 | 192 | 227 |
| 06_ai | AI | 15 | 742 | 192 |
| 07_chien_dich_cot_truyen | Chiến dịch và cốt truyện | 35 | 9134 | 555 |
| 08_ban_do | Bản đồ | 41 | 151332 | 511 |
| 09_hieu_ung_am_thanh | Hiệu ứng và âm thanh | 20 | 1593 | 242 |
| 10_model_tai_san | Model và tài sản | 23 | 22833 | 321 |
| 11_meta_giao_dien | Meta và giao diện | 26 | 1046 | 238 |
| 12_he_thong_trang_thai | Hệ thống và trạng thái | 23 | 15913 | 191 |
| 13_tham_chieu_nguon | Tham chiếu ngoài đời và game (nguồn) | 7 | 6582 | 74 |
| tổng | | 338 | 223039 | 5165 |

## Độ phủ khóa (spec 3.3)

1003 nguồn, 803070 lá: 801221 đã ánh xạ, 1849 trong Khong_xuat (có lý do), 0 chờ file chưa xuất, 0 chưa ánh xạ, 0 lá ánh xạ hai lần. Chi tiết theo file và danh sách Khong_xuat: `00_chi_muc/COVERAGE.md`.

Khong_xuat: 16 luật, 1849 lá (lớn nhất: Assets/Settings/*.asset `**` 1322 lá (cấu hình render URP (không có trường lối chơi)); Assets/MachineBrigade/Scenes/*.unity `**` 437 lá (cảnh Unity: chỉ bố cục khởi động; lối chơi đọc từ dữ liệu lú); Assets/MachineBrigade/Settings/VulkanDeviceFilters.asset `**` 17 lá (bộ lọc thiết bị Vulkan (không có trường lối chơi)); Tools/music/requirements.txt `**` 7 lá (danh sách gói Python của công cụ nhạc (không phải dữ liệu ga); *.asset `docs[*]._class` 6 lá (mã lớp Unity của tài liệu YAML (siêu dữ liệu))).

## Nguồn không đọc được

Không có.

## Cột suy ra và khớp mã game (spec 2.3, lớp B)

217 cột công thức sống (Schema.cong_thuc), 82 cột `_game` (port mã game), 168 cột phân tích so với bản Python của chính công cụ (không có `_game`, ví dụ so sánh với thật của lượt 10). Kiểm công thức == giá trị tham chiếu (sai số 1e-6) và input chép == file nguồn: {'OK': 279} trên 35664 ô; chi tiết `00_chi_muc/Machine_Brigade_00_Index_<ngày>.xlsx` sheet Kiem_cong_thuc.

Cột công thức theo file: 01_vu_khi_dan 29, 02_phuong_tien 38, 03_boss 23, 04_can_cu_thap 20, 05_che_do_kinh_te 32, 06_ai 13, 07_chien_dich_cot_truyen 15, 08_ban_do 13, 09_hieu_ung_am_thanh 7, 10_model_tai_san 20, 11_meta_giao_dien 7.

## Hằng số trong mã (spec 5)

7249 hằng số / số cứng ảnh hưởng lối chơi trong 12/Hang_so_trong_ma (đề xuất đưa ra dữ liệu: {'khong': 3921, 'co': 3328}).

## Lớp tham chiếu ngoài đời và game (lượt 10, spec 12)

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

Nguon_tham_chieu: 179 nguồn (bai_bao 1, nha_phat_hanh_game 1, nha_san_xuat 3, tai_lieu_quan_su_chinh_thuc 3, tai_lieu_repo 18, thu_vien_am_thanh 36, wiki_game 3, wikipedia 114); 5 có URL (chỉ các link repo ghi).

### Danh sách ưu tiên điền nguồn

Thứ tự của 13/Thieu_nguon: 1 xe, vũ khí, boss; 2 căn cứ và tháp; 3 còn lại. Trước hết là các thực thể chưa có tham chiếu nào (loai_tham_chieu NEED_SOURCE), rồi các cột thông số hay thiếu nhất.

- Xe chưa có tham chiếu (45): `aa_57mm_vehicle`, `aa_gun_vehicle`, `aerial_tanker`, `airborne_light_tank`, `airborne_light_tank_chute`, `airborne_vehicle`, `airborne_vehicle_chute`, `amphib_light_vehicle`, `auto_loader_howitzer`, `bridging_vehicle`, `coastal_ashm_vehicle`, `combat_wreck_car`, `dazzler_vehicle`, `demolition_line_vehicle`, `drone_hijack_vehicle`, `fibre_fpv_carrier`, `glide_bomber`, `gps_jammer_vehicle`, `ground_cruise_missile_vehicle`, `ground_drone_carrier`, `heavy_lift_helicopter`, `interceptor_drone_vehicle`, `interceptor_jet`, `light_attack_heli`, `mara_behemoth`, `microwave_vehicle`, `mine_rocket_truck`, `mobile_repair_vehicle`, `next_gen_tank`, `nlos_atgm_vehicle`, `prop_attack_plane`, `radar_atgm_vehicle`, `radar_scout`, `radar_support_vehicle`, `recoilless_jeep`, `recon_jet`, `river_gunboat`, `river_patrol_boat`, `shorad_vehicle`, `sp_mortar`, `stealth_naval_strike`, `towed_at_gun`, `twin_rotor_gunship`, `uav_loiter_strike`, `wheeled_howitzer`.
- Boss chưa có tham chiếu (6): `cerberus`, `hydra`, `hyperion`, `kraken`, `nyx`, `stymphalos`.
- Vũ khí chưa có tên thật (1): `none`.
- Tháp, tường, nhà chính, mô-đun chưa có tham chiếu (30): `aa_gun_tower`, `at_gun_emplacement.long`, `at_gun_emplacement.recoilless`, `blast_wall`, `bunker_shelter_tower`, `decoy_tank`, `drone_net_tower`, `fire_control_centre`, `flare_searchlight_tower`, `flare_tower`, `headquarters.fortress_air`, `headquarters.fortress_ground`, `headquarters.shield`, `heavy_flak_tower.bofors`, `heavy_flak_tower.heavy`, `inflatable_decoy`, `inflatable_decoy.balloon`, `inflatable_decoy.inflatable`, `laser_ad_station`, `laser_ad_station.laser`, `laser_ad_station.net`, `manpads_tower`, `one_shot_atgm_tower`, `recoilless_gun_tower`, `searchlight`, `searchlight.beam`, `searchlight.flare`, `troop_shelter`, `visual_jammer`, `wall_gun`.

| ưu tiên | file | cột | số ô NEED_SOURCE |
|---:|---|---|---:|
| 1 | 01_vu_khi_dan | ngoai_doi_khoi_luong_dan_kg | 372 |
| 1 | 01_vu_khi_dan | ngoai_doi_khoi_luong_thuoc_no_kg | 372 |
| 1 | 01_vu_khi_dan | ngoai_doi_so_toc_dau_nong_m_s | 372 |
| 1 | 01_vu_khi_dan | ngoai_doi_tam_hieu_qua_m | 372 |
| 1 | 01_vu_khi_dan | ngoai_doi_tam_toi_da_m | 372 |
| 1 | 01_vu_khi_dan | ngoai_doi_nap | 342 |
| 1 | 02_phuong_tien | nam_dua_vao_su_dung | 160 |
| 1 | 02_phuong_tien | quoc_gia | 160 |
| 1 | 02_phuong_tien | ngoai_doi_dong_co_cong_suat_kw | 120 |
| 1 | 02_phuong_tien | ngoai_doi_giap | 120 |
| 1 | 02_phuong_tien | ngoai_doi_khoi_luong_t | 120 |
| 1 | 02_phuong_tien | ngoai_doi_tam_hoat_dong_km | 120 |
| 1 | 02_phuong_tien | ngoai_doi_to_lai | 120 |
| 1 | 02_phuong_tien | ngoai_doi_toc_do_toi_da_km_h | 120 |
| 1 | 01_vu_khi_dan | ngoai_doi_co_mm | 112 |
| 1 | 01_vu_khi_dan | ngoai_doi_phat_phut_duy_tri | 95 |
| 1 | 02_phuong_tien | do_tin_cay | 85 |
| 1 | 02_phuong_tien | loai_tham_chieu | 85 |
| 1 | 02_phuong_tien | ngoai_doi_cao_m | 63 |
| 1 | 02_phuong_tien | ngoai_doi_dai_m | 58 |
| 1 | 02_phuong_tien | ngoai_doi_rong_m | 58 |
| 1 | 01_vu_khi_dan | ngoai_doi_phat_phut_toi_da | 38 |
| 1 | 03_boss | nam_dua_vao_su_dung | 38 |
| 1 | 03_boss | quoc_gia | 38 |
| 1 | 01_vu_khi_dan | ngoai_doi_khoi_luong_dau_dan_kg | 27 |
| 1 | 03_boss | ngoai_doi_cao_m | 27 |
| 1 | 03_boss | ngoai_doi_dai_m | 24 |
| 1 | 03_boss | ngoai_doi_rong_m | 24 |
| 1 | 03_boss | do_tin_cay | 6 |
| 1 | 03_boss | loai_tham_chieu | 6 |
| 1 | 01_vu_khi_dan | do_tin_cay | 1 |
| 1 | 01_vu_khi_dan | loai_tham_chieu | 1 |
| 2 | 04_can_cu_thap | nam_dua_vao_su_dung | 93 |
| 2 | 04_can_cu_thap | ngoai_doi_cao_m | 93 |
| 2 | 04_can_cu_thap | ngoai_doi_dai_m | 93 |
| 2 | 04_can_cu_thap | ngoai_doi_rong_m | 93 |
| 2 | 04_can_cu_thap | quoc_gia | 93 |
| 2 | 04_can_cu_thap | do_tin_cay | 30 |
| 2 | 04_can_cu_thap | loai_tham_chieu | 30 |
| 2 | 04_can_cu_thap | ngoai_doi_vat_lieu | 3 |

(69 cặp file × cột; toàn bộ 5840 ô ở 13/Thieu_nguon.)

### Dòng co_lech_lon (chưa có lý do, đã vào 12/Cho_quyet)

139 dòng; mỗi dòng mang `cho_quyet_id`. 40 dòng đầu:

- `TC0001`: 01_vu_khi_dan/Vu_khi_so_sanh_that anti_ship_missile/nhip: nhịp anti_ship_missile: ty_le 10 ngoài 0,6–2, cờ CHAM_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0002`: 01_vu_khi_dan/Vu_khi_so_sanh_that atgm_heavy/nhip: nhịp atgm_heavy: ty_le 0.375 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0003`: 01_vu_khi_dan/Vu_khi_so_sanh_that ballistic_missile/nhip: nhịp ballistic_missile: ty_le 0.404 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0004`: 01_vu_khi_dan/Vu_khi_so_sanh_that boss_howitzer/nhip: nhịp boss_howitzer: ty_le 0.275 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0005`: 01_vu_khi_dan/Vu_khi_so_sanh_that boss_missiles/nhip: nhịp boss_missiles: ty_le 0.32 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0006`: 01_vu_khi_dan/Vu_khi_so_sanh_that boss_mortar/nhip: nhịp boss_mortar: ty_le 0.114 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0007`: 01_vu_khi_dan/Vu_khi_so_sanh_that buk_launcher/nhip: nhịp buk_launcher: ty_le 0.412 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0008`: 01_vu_khi_dan/Vu_khi_so_sanh_that casemate_155/nhip: nhịp casemate_155: ty_le 0.598 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0009`: 01_vu_khi_dan/Vu_khi_so_sanh_that cruise_missile_ground/nhip: nhịp cruise_missile_ground: ty_le 7.5 ngoài 0,6–2, cờ CHAM_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0010`: 01_vu_khi_dan/Vu_khi_so_sanh_that flak_35/nhip: nhịp flak_35: ty_le 5.42 ngoài 0,6–2, cờ CHAM_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0011`: 01_vu_khi_dan/Vu_khi_so_sanh_that flak_88/nhip: nhịp flak_88: ty_le 0.5 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0012`: 01_vu_khi_dan/Vu_khi_so_sanh_that gun_100_river/nhip: nhịp gun_100_river: ty_le 2.8 ngoài 0,6–2, cờ CHAM_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0013`: 01_vu_khi_dan/Vu_khi_so_sanh_that gun_105_ags/nhip: nhịp gun_105_ags: ty_le 0.583 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0014`: 01_vu_khi_dan/Vu_khi_so_sanh_that gun_105_apfsds/nhip: nhịp gun_105_apfsds: ty_le 0.319 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0015`: 01_vu_khi_dan/Vu_khi_so_sanh_that gun_105_bunker/nhip: nhịp gun_105_bunker: ty_le 0.529 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0016`: 01_vu_khi_dan/Vu_khi_so_sanh_that gun_105_long/nhip: nhịp gun_105_long: ty_le 0.272 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0017`: 01_vu_khi_dan/Vu_khi_so_sanh_that gun_105_wheeled/nhip: nhịp gun_105_wheeled: ty_le 0.346 ngoài 0,6–2, cờ NHANH_QUA;LECH_DOT_1; chưa có lý do ở fix_weapon_reasons.json
- `TC0018`: 01_vu_khi_dan/Vu_khi_so_sanh_that gun_120_twin/nhip: nhịp gun_120_twin: ty_le 0.482 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0019`: 01_vu_khi_dan/Vu_khi_so_sanh_that gun_120mm/nhip: nhịp gun_120mm: ty_le 0.476 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0020`: 01_vu_khi_dan/Vu_khi_so_sanh_that gun_125_armata_ke/nhip: nhịp gun_125_armata_ke: ty_le 0.467 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0021`: 01_vu_khi_dan/Vu_khi_so_sanh_that gun_125_elite/nhip: nhịp gun_125_elite: ty_le 0.528 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0022`: 01_vu_khi_dan/Vu_khi_so_sanh_that gun_140_twin/nhip: nhịp gun_140_twin: ty_le 0.529 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0023`: 01_vu_khi_dan/Vu_khi_so_sanh_that gun_155_coastal/nhip: nhịp gun_155_coastal: ty_le 0.206 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0024`: 01_vu_khi_dan/Vu_khi_so_sanh_that gun_155_twin/nhip: nhịp gun_155_twin: ty_le 0.413 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0025`: 01_vu_khi_dan/Vu_khi_so_sanh_that gun_155_twin_ap/nhip: nhịp gun_155_twin_ap: ty_le 0.259 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0026`: 01_vu_khi_dan/Vu_khi_so_sanh_that gun_155_twin_coastlr/nhip: nhịp gun_155_twin_coastlr: ty_le 0.259 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0027`: 01_vu_khi_dan/Vu_khi_so_sanh_that gun_155_twin_fort/nhip: nhịp gun_155_twin_fort: ty_le 0.259 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0028`: 01_vu_khi_dan/Vu_khi_so_sanh_that gun_155_twin_long/nhip: nhịp gun_155_twin_long: ty_le 0.413 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0029`: 01_vu_khi_dan/Vu_khi_so_sanh_that gun_203_siege/nhip: nhịp gun_203_siege: ty_le 0.285 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0030`: 01_vu_khi_dan/Vu_khi_so_sanh_that gun_57mm/nhip: nhịp gun_57mm: ty_le 4.5 ngoài 0,6–2, cờ CHAM_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0031`: 01_vu_khi_dan/Vu_khi_so_sanh_that gun_pit_105/nhip: nhịp gun_pit_105: ty_le 0.432 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0032`: 01_vu_khi_dan/Vu_khi_so_sanh_that gunship_40mm/nhip: nhịp gunship_40mm: ty_le 0.413 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0033`: 01_vu_khi_dan/Vu_khi_so_sanh_that howitzer/nhip: nhịp howitzer: ty_le 0.411 ngoài 0,6–2, cờ NHANH_QUA;LECH_DOT_1; chưa có lý do ở fix_weapon_reasons.json
- `TC0034`: 01_vu_khi_dan/Vu_khi_so_sanh_that howitzer_cb/nhip: nhịp howitzer_cb: ty_le 0.212 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0035`: 01_vu_khi_dan/Vu_khi_so_sanh_that howitzer_ext/nhip: nhịp howitzer_ext: ty_le 0.296 ngoài 0,6–2, cờ NHANH_QUA;LECH_DOT_1; chưa có lý do ở fix_weapon_reasons.json
- `TC0036`: 01_vu_khi_dan/Vu_khi_so_sanh_that howitzer_fixed/nhip: nhịp howitzer_fixed: ty_le 0.212 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0037`: 01_vu_khi_dan/Vu_khi_so_sanh_that jassm/nhip: nhịp jassm: ty_le 0.2 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0038`: 01_vu_khi_dan/Vu_khi_so_sanh_that kornet_multi/nhip: nhịp kornet_multi: ty_le 0.278 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0039`: 01_vu_khi_dan/Vu_khi_so_sanh_that kornet_top/nhip: nhịp kornet_top: ty_le 0.26 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json
- `TC0040`: 01_vu_khi_dan/Vu_khi_so_sanh_that kornet_twin/nhip: nhịp kornet_twin: ty_le 0.555 ngoài 0,6–2, cờ NHANH_QUA; chưa có lý do ở fix_weapon_reasons.json

Đủ danh sách: 12_he_thong_trang_thai/Cho_quyet (id TC####).

## Chỗ tự quyết (DECISIONS, các mục "Bộ xuất dữ liệu toàn bộ")

### Bộ xuất dữ liệu toàn bộ (lane A)

- **Tool.** `python Tools/export/export.py [--out DIR] [--base REF] [--strict]`; subcommands `coverage` and `fk` run one check
- **Domains.** One module per file in `Tools/export/domains/` (FILE_ID, TITLE, DESC, build(ctx)), listed in
- **Coverage.** Concrete leaf paths, not patterns: a vehicles[] entry splits across Xe / Thap / Tuong / Nha_chinh /
- **Two column blocks.** Spec-named Vietnamese columns hold the value the game builds (Python ports of Catalog.Inherited,
- **game.json not used.** The only ExportGameDoc output found lies outside the repo, predates today's balance.json and cannot
- **_truoc / _sau.** Against `--base` (default `origin/main`, the last release 9198a675): `so_voi_ban_goc` = giong / doi /
- **Markers.** Layer B cells are `CHUA_AP:prompt_xuat_luot5`; real-world numbers only from the repo (the REAL table of
- **Units.** Suffix from `core/units.py`; a numeric column of unknown unit goes to 00/Don_vi_chua_ro (200 today) instead of a guess.
- **Kept in git.** The output is 3 MB for files 00-04, so it is committed whole. When 08 (maps) makes it heavy, add
### Bộ xuất dữ liệu toàn bộ: lead calls on lane A's open questions (2026-10-03)

### Bộ xuất dữ liệu toàn bộ (lane C, passes 3-4)

- **Coverage.** 999 sources, 802 226 leaves: 799 681 mapped, 1 849 Khong_xuat, 0 unmapped, 0 mapped twice; 210 foreign
- **Maps.** Every leaf of the 100 map files is a row or a cell, nothing summarised: props one row each (89 245), terrain
- **Split of shared sources.** campaign.json: economy and `eventLibrary.rules.difficulty` -> 05 (Do_kho), generals -> 06,
- **C# tables.** Meta tables are every `static readonly` literal array of the meta files (Arsenal, DailyMissions,
- **Docs inputs of file 12.** `Docs/checks/fix_validate.json` and `Docs/balance/apply_state_p29.json` are registered as
- **Markers.** Code-only sheets hold one marker row: NEED_CODE_CHECK (wrecks, mixer, preview, rewards) or
- **Clip facts.** Length, channels and rate come from each Ogg file's headers; author, source and licence from
- **Counts against the spec.** 193 missions, 15 chapters, 23 game decks: match. 41 bosses: file 03. Maps: 25 base maps x 4
- **Size.** The whole output is 56 MB (08_ban_do: 8 MB xlsx, 32 MB csv), so per the lead's call the dated folders' xlsx/,
### Bộ xuất dữ liệu toàn bộ (lane C, passes 7-8)

- **Diff.** `python Tools/export/export.py diff <dirA|refA> <dirB|refB> [--out DIR]` -> `Docs/export/diff_<A>_<B>/`: one
- **Refs.** A ref is exported in a temp git worktree with the current exporter overlaid (so only data differs), with
- **Demo** origin/main (v0.34.0, 9198a675) -> 382d5fb9: d01 and d09 are not buildable on v0.34.0 (a helper / source
- **Self-check.** `python Tools/export/export.py check [--out DIR]`: two exports in separate processes, the 9 checks read
- **Result at 382d5fb9.** 1 CHUA_DAT (file 13 = pass 10; 23 layer B / C sheets = pass 5; empty 04/Mo_dun_tien_ich_vu_khi
- **Fixes in lane C's own files.** 10/Model size columns are `glb_x_m` / `glb_y_m` / `glb_z_m` (were dai_m / cao_m /
- **Secrets.** The scan reads every output file: xlsx / zip parts, PDF streams inflated, other binaries as Latin-1; adds
- **CI.** `.github/workflows/export.yml`: on push, Ubuntu, Python 3.11 + openpyxl 3.1.5 + numpy, `export.py check --out
### Bộ xuất dữ liệu toàn bộ (lane B, pass 5)

- **Formulas.** `core/formula.py`: an `F` cell holds a template (`{col}`, `{Sheet!col}`, `{Sheet!col@id}`, `{Sheet!col@*}`)
- **The test.** Each formula cell carries its reference value: a `_game` column (the Python port of the C# named in
- **Ports.** FirePower (Volley, OnPaper, Sustained, SustainedAir), Definitions (RoundsPerCycle, CycleSeconds,
- **Inputs.** `input_<name>` sheets copy what a file needs from another (02, 03, 04 copy weapon numbers from 01; 03 the
- **Layer A cells settled by the ports.** 01 Vu_khi xuyen default, thoi_gian_canh_bao_s, co_vong_canh_bao,
- **Choices.** dps_may_bay at aircraft armour 0 (14 of 22 card aircraft); dps_cong_trinh at structure armour 2 (the
- **Left NEED_CODE_CHECK.** 02 Xe_suy_ra nhom_gia / he_so_gia / thuong_suc_manh / tha_du_theo_nhom_s (no price group in
- **Hang_so_trong_ma.** `Tools/export/scan_constants.py` `scan(root)` returns the rows (columns in `COLUMNS`): const,
- **TODO (lane C / lead):** wire `scan_constants.scan(repo.ROOT)` into d12 as sheet Hang_so_trong_ma (one row per item, id
### Bộ xuất dữ liệu toàn bộ (lane B, pass 5 part 2)

- **Modules.** `domains/_b05.py` .. `_b12.py`, one hook line in each lane C domain file. Evaluator (`core/formula.py`) gains
- **05.** Start CP and income are C# literals of each mode session (ModeSessions.cs, ShowdownSession.cs); the game applies
- **Findings 05.** At Normal the enemy's 0.7 income makes Deathmatch and King of the Hill RED (enemy about 35 % below the
- **06.** AI_xung_dot ports the tactic precedence (ConquestAi.P28 TickLayered + Commander.AllowedTactic) per mode / goal x
- **07.** Counts by COUNTIFS over Thoai; budget and word-for-word rule from Tools/story/script_build.py; silence = the
- **08.** Ban_do_do_tinh = Docs/checks/map_audit.csv + validate_p33.json as data (not re-measured), the status re-derived by
- **09 / 10.** Audio and model numbers are report data (metrics.json, static_scores.csv, visual_scores.md, fix_validate
- **11.** Rewards.cs literals; a reference quick battle of 20 kills and 9 minutes; rank 1 -> 10 of one card 12 850 coins,
- **12.** Hang_so_trong_ma = scan_constants.scan (7 249 rows, natural id order file / line / column). Lich_su_do.stale is
- **Lead items.** 04/Mo_dun_tien_ich_vu_khi and 04/Tuong_vu_khi get one KHONG_CO marker row (no utility module or wall has a
- **Schema.** Accepted assumptions written into the columns: aircraft armour 0 (01 dps_may_bay, 02 Hoi_quy), light / heavy
- **Self-check 4** counts a formula column with a Python reference (no `_game`, Schema.nguon_khoa "python: ...") as a gap;
### Bộ xuất dữ liệu toàn bộ (lane C, pass 6)

- **Source of the tables.** The md reads the csv/ the same run just wrote (not the domain modules), so every table prints
- **Source of the prose.** The committed design review `Docs/Machine_Brigade_Design_Review.html` (the build_doc.py
- **Section order.** PDF 1-19 (with its sub-parts: 2b, 2c, 7b, 8b in 8, 9b in 9, 10b-10h, 12b, 12c) plus 3b (game decks,
- **Status line.** Computed from the section's sheets: a sheet of only marker rows (CHUA_AP / KHONG_CO) = not done, a
- **Text fixed to the code (spec 6 list).** Checked against code / data; applied as regex fixes on the review's text,
- **Pictures.** Copied (as is, gitignored) to images/<domain>/: the review's r6 / shots pictures where they stand, the
- **PDF.** PyMuPDF Story renders FULL.md through a small md -> HTML step (no other text); A4, bookmarks from h1-h3,
- **Self-check 5.** 200 numeric cells (seed 20261003) from every md table headed "Sheet: <file>/<sheet>" must equal the
- **Open.** The pass 6 markers inside domain modules (10/Anh_chup, 10/Model.anh_3_goc, 09/Am_thanh_mau, 09/VFX_vu_khi,
### Bộ xuất dữ liệu toàn bộ (lane B, pass 9)

- **Command.** `python Tools/export/export.py import <export folder | edited xlsx> --dry-run [--out DIR]`
- **Finding an edit.** The export is rebuilt from the current tree with the export's own base ref (00_chi_muc/MANIFEST.json
- **Inverse mapping.** Row.mark is recorded per cell during the rebuild (file, sheet, row id, column -> source leaves); only
- **Manifest.** Prompt 29's columns and bundle shape (Docs/balance/manifest_v2.json): rows bundle_id (`XL<file>-<sheet>-<id>`),
- **Apply path.** The only data writer stays Tools/balance/p29_apply.py (R1-R8). It reads only manifest_v2.json + the
- **Check.** `python Tools/export/tests/test_import_demo.py [export folder]` (exports into temp when no folder is given): the
- **Apply by real key path (lead, 03/10).** `python Tools/balance/p29_apply.py --manifest <manifest_import.json> [--bundles P] --dry-run`
- **Check.** `python Tools/export/tests/test_manifest_apply.py` (run, PASS) works on a temp copy of balance.json,
- **Owner answers.** Rejecting the named (resolved) columns with a pointer to the raw column is kept; the import .md now
- **Open (closed by the follow-up below).** The pass 6 markers inside domain modules (10/Anh_chup, 10/Model.anh_3_goc,
- **Follow-up (markers filled, lead's go 03/10).** No CHUA_AP:prompt_xuat_luot6 cell is left. 10/Anh_chup = every picture the
### Bộ xuất dữ liệu toàn bộ (lane C, pass 10)

- **Sources.** `Tools/docs/unit_refs.json` (its claim left `_pending.py`; leaves now map to 02 / 03 / 04 and its `_about`
- **A cited document is a source row.** Every document a repo note names (Wikipedia 'X', US Army FM ..., a maker's
- **Reliability of a reference row.** da_kiem_chung only when the repo record carrying the figure names an outside
- **Sheet names.** `<domain>_tham_chieu` / `<domain>_so_sanh_that` with the domain's short name (02 already has
- **Real-world columns.** Calibre from the "NN mm" of the weapon's real name in balance.json; rates, practical rates
- **Comparisons (12.4).** Rate: the gap one barrel takes for one round, exactly the audit L1 measure (its ratio is
- **Unexplained deviations.** Every co_lech_lon row without a reason gets a 12/Cho_quyet line (`TC####`, 139 today) and
- **Game mechanics.** Tham_chieu_game_co_che holds every game a reference row names (aggregated by game and mechanic,
- **Edge cases.** unit_refs keys of branches that no longer exist (`minefield.at`, `minefield.scatter`,
- **Check 4.** `01/Vu_khi.thoi_gian_bay_toi_tam_s` gains its `_game` port (CombatSystem.cs Fire: range / speed, a warned
- **12.6 in the reports.** COVERAGE.md and SELF_CHECK.md gain the reference section (entity coverage, orphan nguon_id,

Toàn văn và lý do: `Docs/DECISIONS.md`, các mục trên.

## Diff (lượt 7)

`python Tools/export/export.py diff <A> <B>` so mọi file và mọi sheet theo cách chung (không danh sách sheet cứng), nên file 13 và các sheet `<tên>_tham_chieu` / `<tên>_so_sanh_that` hiện là sheet thêm khi so với một bản xuất cũ và báo dòng / ô đổi ở các bản sau.

