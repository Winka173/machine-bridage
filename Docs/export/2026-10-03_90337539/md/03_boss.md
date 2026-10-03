# 03_boss — Boss

Bộ xuất dữ liệu Machine Brigade, commit 90337539, ngày 2026-10-03. Sinh bởi `python Tools/export/export.py` (lượt 6): bảng in đúng ô của csv / xlsx; văn bản lấy từ tài liệu thiết kế (Tools/docs) và chuỗi trong game. Toàn văn: Machine_Brigade_Design_FULL_2026-10-03.md.

Boss chủ lực / mini và biến thể, bệ vũ khí (đã dựng), bộ phận, pha, khung, hạng, siêu vũ khí, hộ tống, Săn trùm

Mục trong file này: 10d. Tổng hợp boss; 10g. Boss: vụ nổ hai lớp, pha, giáp và cỡ; 10h. Săn trùm (Boss Hunt); 11. Tháp canh, xe tinh nhuệ và boss.

### 10d. Tổng hợp boss

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_dps; 03_boss/Boss_hieu_qua. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §10d.

Mọi boss và mini boss cạnh nhau, đọc từ dữ liệu hiện tại: máu thân (trước hệ số độ khó), giáp trước/hông/sau/nóc, số bộ phận và phần máu của chúng, DPS duy trì lên xe nhẹ, xe nặng, máy bay và công trình (trước giáp), đòn lớn đầu tiên và số hộ tống trong mọi đợt.

Sheet: 03_boss/Boss_dps — Boss: DPS duy trì (41 dòng, 12 cột)

| id | he_so_vu_khi | he_so_sat_thuong_ra | he_so_hang | so_be | tong_dps_duy_tri | tong_dps_duy_tri_game | cach_bu |
|---|---|---|---|---|---|---|---|
| argus | 1.44 | 1.7892 | 1.2 | 2 | 814.2273589164784 | 814.2273589164784 | NEED_CODE_CHECK |
| armored_train | 1.859 | 0.8319 | 1.2 | 6 | 1472.785778546959 | 1472.785778546959 | NEED_CODE_CHECK |
| bastion_mk0 | 1.51 | 1.4708 | 1.2 | 3 | 288.6319582945737 | 288.6319582945737 | NEED_CODE_CHECK |
| behemoth | 1.0 | 1.0 | 1.4 | 10 | 1098.635326362491 | 1098.635326362491 | NEED_CODE_CHECK |
| behemoth_inferno | 1.962 | 1.0 | 1.2 | 3 | 552.3849250535332 | 552.3849250535332 | NEED_CODE_CHECK |
| behemoth_mk0 | 0.884 | 1.0 | 1.2 | 4 | 563.0441464722239 | 563.0441464722239 | NEED_CODE_CHECK |
| behemoth_mk2 | 1.928 | 1.0 | 1.2 | 3 | 992.2860383669616 | 992.2860383669616 | NEED_CODE_CHECK |
| behemoth_tempest | 1.74 | 1.0 | 1.2 | 3 | 519.8567849686848 | 519.8567849686848 | NEED_CODE_CHECK |
| caspian | 6.0 | 1.0 | 1.2 | 3 | 1559.7600799733423 | 1559.7600799733423 | NEED_CODE_CHECK |
| cerberus | 1.326 | 1.0 | 1.2 | 4 | 1165.954442756663 | 1165.954442756663 | NEED_CODE_CHECK |
| command_airship | 1.0 | 1.7892 | 1.4 | 8 | 1225.8887184265823 | 1225.8887184265823 | NEED_CODE_CHECK |
| daedalus | 1.0 | 1.0 | 1.4 | 4 | 777.5524475524476 | 777.5524475524476 | NEED_CODE_CHECK |
| drone_mothership | 1.0 | 1.0 | 1.4 | 9 | 1187.8241562511437 | 1187.8241562511437 | NEED_CODE_CHECK |
| earth_borer | 2.874 | 1.0854 | 1.2 | 3 | 665.4804479999999 | 665.4804479999999 | NEED_CODE_CHECK |
| fenrir | 2.222 | 0.9508 | 1.2 | 3 | 803.3324875060612 | 803.3324875060612 | NEED_CODE_CHECK |

*15 / 41 dòng đầu: xem sheet 03_boss/Boss_dps.*

Sheet: 03_boss/Boss_hieu_qua — Boss: hiệu quả vũ khí chính (205 dòng, 20 cột)

| id | boss_id | vu_khi | xe_tham_chieu | giap_mat_trung | he_so_trung | he_so_trung_game | sat_thuong_moi_don | sat_thuong_moi_don_game | so_don_de_ha |
|---|---|---|---|---|---|---|---|---|---|
| argus/armored_car | argus | p26_roc_main_roc_bombs | armored_car | 0 | 1.0 | 1.0 | 2164.2163199999995 | 2164.2163199999995 | 1.0 |
| argus/gun_turret | argus | p26_roc_main_roc_bombs | gun_turret | 3 | 1.5 | 1.5 | 3246.3244799999993 | 3246.3244799999993 | 2.0 |
| argus/heavy_tank | argus | p26_roc_main_roc_bombs | heavy_tank | 2 | 1.0 | 1.0 | 2164.2163199999995 | 2164.2163199999995 | 3.0 |
| argus/ifv | argus | p26_roc_main_roc_bombs | ifv | 0 | 1.0 | 1.0 | 2164.2163199999995 | 2164.2163199999995 | 1.0 |
| argus/main_battle_tank | argus | p26_roc_main_roc_bombs | main_battle_tank | 1 | 1.0 | 1.0 | 2164.2163199999995 | 2164.2163199999995 | 2.0 |
| armored_train/armored_car | armored_train | train_gun | armored_car | 1 | 1.2 | 1.2 | 1336.1778144 | 1336.1778144 | 1.0 |
| armored_train/gun_turret | armored_train | train_gun | gun_turret | 3 | 0.6 | 0.6 | 668.0889072 | 668.0889072 | 6.0 |
| armored_train/heavy_tank | armored_train | train_gun | heavy_tank | 4 | 0.85 | 0.85 | 946.4592852000001 | 946.4592852000001 | 5.0 |
| armored_train/ifv | armored_train | train_gun | ifv | 2 | 1.2 | 1.2 | 1336.1778144 | 1336.1778144 | 2.0 |
| armored_train/main_battle_tank | armored_train | train_gun | main_battle_tank | 4 | 0.85 | 0.85 | 946.4592852000001 | 946.4592852000001 | 3.0 |
| bastion_mk0/armored_car | bastion_mk0 | p26_bastion_sec_b240 | armored_car | 0 | 1.0 | 1.0 | 2931.5985600000004 | 2931.5985600000004 | 1.0 |
| bastion_mk0/gun_turret | bastion_mk0 | p26_bastion_sec_b240 | gun_turret | 3 | 1.5 | 1.5 | 4397.3978400000005 | 4397.3978400000005 | 1.0 |
| bastion_mk0/heavy_tank | bastion_mk0 | p26_bastion_sec_b240 | heavy_tank | 2 | 1.0 | 1.0 | 2931.5985600000004 | 2931.5985600000004 | 2.0 |
| bastion_mk0/ifv | bastion_mk0 | p26_bastion_sec_b240 | ifv | 0 | 1.0 | 1.0 | 2931.5985600000004 | 2931.5985600000004 | 1.0 |
| bastion_mk0/main_battle_tank | bastion_mk0 | p26_bastion_sec_b240 | main_battle_tank | 1 | 1.0 | 1.0 | 2931.5985600000004 | 2931.5985600000004 | 1.0 |

*15 / 205 dòng đầu: xem sheet 03_boss/Boss_hieu_qua; in 10 / 20 cột; 8 cột khác (và raw_json, nguon): xem sheet.*

### 10g. Boss: vụ nổ hai lớp, pha, giáp và cỡ

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_phase; 03_boss/Boss_be_goc. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §10g.

Prompt 26: vũ khí nổ của boss có hai lớp. **Lõi** (bán kính nổ của vũ khí) nhận đủ sát thương; **rìa** (gấp đôi lõi, tối đa 20 m) nhận 40% sát thương. Vũ khí không có rìa nổ một lớp, giảm dần theo khoảng cách. Máu, vũ khí và cỡ của boss được làm lại theo chương (mục tiêu hạ boss chủ lực từ 2,5 phút ở chương 1 tới 4 phút ở chương 12, mini boss 60 đến 90 giây); Ixion và Gungnir được làm lại; mỗi boss có mốc thời đại ở dòng Tham khảo của thẻ. Pha: hệ số nhân vào từ mốc máu đó trở đi.

#### Pha, giáp và cỡ model (41 boss)

| Boss | Cấp | Máu | Giáp T/H/S/N | Cỡ model (m) | Pha |
|---|---|---|---|---|---|
| **Bastion Mk.0 · Pháo đài nguyên mẫu** | mini | 8.999 | 4/4/4/3 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Inferno · Behemoth phun lửa** | mini | 11.500 | 4/3/2/2 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Harpy · Trực thăng khổng lồ** | mini | 14.002 | 2/2/2/2 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Fenrir · Xe tiên phong** | mini | 14.002 | 4/4/3/2 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Behemoth Mk.0 · Behemoth nguyên mẫu** | mini | 15.848 | 3/3/2/1 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Juggernaut · Đoàn tàu bọc thép** | mini | 17.648 | 4/3/3/2 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Tempest · Behemoth pháo điện từ** | mini | 17.648 | 4/3/2/2 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Scylla · Tàu khu trục** | mini | 17.648 | 4/4/3/2 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Nyx · Tàu khu trục tàng hình** | mini | 17.648 | 4/4/3/2 | 53 × 9 × 11 | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Hive · Pháo đài drone** | mini | 21.341 | 4/3/2/2 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Locust · Tàu con drone** | mini | 21.341 | 1/1/1/1 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Stymphalos · Bầy UAV phản lực** | mini | 21.341 | 1/1/1/1 | 16 × 26 × 3 | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Bastion · Pháo đài** | chủ lực | 22.015 | 5/3/2/3 | — | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.2, tốc độ ×1.1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Charybdis · Tàu đệm khí đổ bộ** | mini | 25.011 | 3/2/1/1 | — | 45%: sát thương ×1, tốc độ ×1.2, nhận sát thương ×1, nhịp bắn ×1 |
| **Behemoth Mk.II · Behemoth nâng cấp** | mini | 25.011 | 4/3/2/2 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Cerberus · Đoàn xe ba khung** | mini | 25.011 | 3/3/2/2 | 16 × 8 × 6 | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Behemoth · Quái vật thép** | chủ lực | 28.518 | 5/3/2/2 | — | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.2, tốc độ ×1.1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Atlas · Xe chỉ huy siêu nặng** | mini | 29.359 | 4/3/2/2 | — | 45%: sát thương ×1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1, hồi 8% máu |
| **Tartarus · Máy khoan** | mini | 33.660 | 4/3/2/2 | — | 45%: sát thương ×1, tốc độ ×1.15, nhận sát thương ×1, nhịp bắn ×1 |
| **Ixion · Xe tải mỏ bọc thép** | mini | 33.660 | 4/3/2/2 | 26 × 12 × 10 | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Jötunn · Pháo đài di động** | chủ lực | 35.020 | 5/3/2/2 | — | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.2, tốc độ ×1.1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Caspian · Tàu bay sát mặt nước** | mini | 38.008 | 2/2/2/1 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Hydra · Tàu ngầm mang drone** | mini | 38.008 | 4/3/2/2 | 35 × 7 × 8 | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Morrigan · Tiêm kích của Raven** | mini | 41.140 | 1/1/1/1 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Spectre · Máy bay pháo** | mini | 44.342 | 2/2/2/2 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Icarus Mk.0 · Phi thuyền nguyên mẫu** | mini | 44.342 | 4/4/4/4 | — | — |
| **Argus · Khí cầu trinh sát** | mini | 44.342 | 2/2/2/2 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Leviathan · Thiết giáp hạm** | chủ lực | 44.370 | 5/3/2/2 | — | 60%: sát thương ×1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Matriarch · Tàu mẹ drone** | chủ lực | 53.635 | 2/2/2/2 | — | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.2, tốc độ ×1.1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Moloch · Nhà máy di động** | chủ lực | 62.985 | 5/3/2/2 | — | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.2, tốc độ ×1.1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Nemesis · Đoàn tàu tên lửa** | chủ lực | 75.352 | 5/3/2/2 | — | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.2, tốc độ ×1.1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Kronos · Máy xúc mỏ** | chủ lực | 87.635 | 5/3/2/2 | — | 60%: sát thương ×1, tốc độ ×1.45, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.3, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Monster · Pháo tự hành 800 mm** | chủ lực | 87.635 | 5/3/2/3 | 40 × 22 × 13 | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.2, tốc độ ×1.1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Typhon · Tàu ngầm tên lửa** | chủ lực | 100.002 | 5/3/2/2 | — | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.2, tốc độ ×1.1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Kraken · Tàu sân bay** | chủ lực | 100.002 | 5/3/2/2 | 110 × 18 × 24 | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.2, tốc độ ×1.1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Roc · Khí cầu chỉ huy** | chủ lực | 116.662 | 2/2/2/2 | — | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.25, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Garuda · Cánh bay ném bom khổng lồ** | chủ lực | 116.662 | 2/2/2/2 | 28 × 70 × 4 | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.2, tốc độ ×1.1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Gungnir · Pháo điện từ đường ray** | chủ lực | 133.365 | 3/2/1/1 | — | 45%: sát thương ×1.2, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Daedalus · Tàu đổ bộ quỹ đạo** | chủ lực | 133.365 | 3/3/3/3 | — | — |
| **Icarus · Phi thuyền quỹ đạo** | chủ lực | 149.982 | 4/4/4/4 | — | — |
| **Hyperion · Trạm gương quỹ đạo** | chủ lực | 149.982 | 4/4/4/4 | 67 × 44 × 20 | — |

Sheet: 03_boss/Boss_phase — Boss: pha (10 dòng, 12 cột)

| id | boss_id | thu_tu | at | damage | fire_rate | heal | radio | speed_m_s | transform |
|---|---|---|---|---|---|---|---|---|---|
| command_airship/0 | command_airship | 0 | 0.6 | 1.1 |  |  | radio.quaden.airship.phase2 |  | 2.5 |
| command_airship/1 | command_airship | 1 | 0.25 | 1.25 | 1.25 |  | radio.quaden.airship.half |  | 3 |
| earth_borer/0 | earth_borer | 0 | 0.45 |  |  |  | radio.hung.borer.half | 1.15 | 2.5 |
| kronos/0 | kronos | 0 | 0.6 |  |  |  | radio.hung.kronos.phase2 | 1.45 | 2.5 |
| kronos/1 | kronos | 1 | 0.25 | 1.3 | 1.25 |  | radio.hung.kronos.phase3 |  | 3 |
| landing_hovercraft/0 | landing_hovercraft | 0 | 0.45 |  |  |  | radio.kessler.hovercraft.half | 1.2 | 2.5 |
| leviathan/0 | leviathan | 0 | 0.6 |  |  |  | radio.kessler.leviathan.phase2 |  | 2.5 |
| leviathan/1 | leviathan | 1 | 0.25 |  | 1.25 |  | radio.kessler.leviathan.phase3 |  | 3 |
| rail_supergun/0 | rail_supergun | 0 | 0.45 | 1.2 |  |  | radio.orlov.supergun.half |  | 3 |
| supreme_command/0 | supreme_command | 0 | 0.45 |  |  | 0.08 | radio.hung.supreme.half |  | 3 |

Sheet: 03_boss/Boss_be_goc — Boss: bệ phụ gốc (107 dòng, 11 cột)

| id | boss_id | thu_tu | weapon | aim | slot |
|---|---|---|---|---|---|
| armored_train/0 | armored_train | 0 | boss_rockets | Free | rocket |
| armored_train/1 | armored_train | 1 | boss_hmg | Free | mg |
| armored_train/2 | armored_train | 2 | boss_flak | Free | mg |
| armored_train/3 | armored_train | 3 | train_gun | Free | main |
| armored_train/4 | armored_train | 4 | train_mortar | Free | mortar |
| armored_train/5 | armored_train | 5 | boss_flak | Free | mg |
| behemoth/0 | behemoth | 0 | gun_120mm | Free | gun |
| behemoth/1 | behemoth | 1 | boss_flak | Free | mg |
| behemoth/2 | behemoth | 2 | boss_flak | Free | mg |
| behemoth/3 | behemoth | 3 | boss_missiles | Hull | missile |
| behemoth/4 | behemoth | 4 | boss_missiles | Hull | missile |
| behemoth/5 | behemoth | 5 | kornet_twin | Free | missile |
| behemoth_inferno/0 | behemoth_inferno | 0 | boss_thermo | Free | rocket |
| behemoth_inferno/1 | behemoth_inferno | 1 | boss_flak | Free | mg |
| behemoth_inferno/2 | behemoth_inferno | 2 | boss_flamer | Turret | main |

*15 / 107 dòng đầu: xem sheet 03_boss/Boss_be_goc.*

### 10h. Săn trùm (Boss Hunt)

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Sanhunt; 03_boss/Sanhunt_ho_tro; 03_boss/Sanhunt_chua_xep. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §10h. Săn trùm.

Prompt 26 E: máu boss theo sức mạnh bộ bài; mọi số dưới đây là giá trị khởi đầu, chờ đo ở phase kiểm tra.

- **Sức mạnh P:** đo một lần lúc bắt đầu từ bộ bài mang theo (sát thương giấy mỗi giây của các thẻ chiến đấu, tính cả hạng thẻ, trang bị và chỉ huy) × 10 xe ra trận × 0,3 trúng boss, tối thiểu 60. Máu boss = P × thời gian mục tiêu × 0,6 × hệ số m × hệ số bậc; sát thương boss là của dữ liệu × m × hệ số bậc.
- **Tuần:** 10 boss (3 chủ lực, 7 mini; nhóm 3, 2, 2 mini dẫn tới mỗi boss chủ lực), mục tiêu mini 66 s, chủ lực 2.8 phút; m = 1 + 0.06 × số thứ tự (×1 tới ×1,54); nghỉ 15 s giữa các boss, quân sống sót được sửa 30% và chỉ giữ 50% CP; điểm hồi sinh sau mỗi boss chủ lực; đồng hồ 30 phút.
- **Toàn bộ:** 41 boss (17 chủ lực) theo thứ tự cốt truyện, chủ lực 2,5 phút, mini 1 phút; m từ ×0.8 tới ×1.3; điểm hồi sinh và lưu sau mỗi boss; mỗi boss là một trận mới (không giữ quân, CP khởi đầu như nhau), chỉ hỗ trợ tác chiến được giữ.
- **Hỗ trợ tác chiến:** sau mỗi boss chủ lực chọn 1 trong 3; tổng sức mạnh quân từ hỗ trợ tối đa +40%; khi đã chạm trần chỉ còn các hỗ trợ đổi cách chơi (thẻ bắn nhanh hơn, thả xe).
- **Bậc:** bốn độ khó của bảng chọn là bốn bậc (bảng dưới). Chưa làm: bậc Huyền thoại và các biến thể (mutator) cho Săn trùm.

#### Lời trong game

Tuần: 10 boss tuần này: 7 mini boss dẫn tới 3 boss chủ lực, boss sau mạnh hơn boss trước. Máu boss theo sức mạnh bộ bài bạn mang. Nghỉ 15 giây giữa các boss, xe còn sống được sửa 30% và giữ 50% CP; sau mỗi boss chủ lực (tối đa +40% sức mạnh đội quân từ hỗ trợ), chọn một trong ba hỗ trợ tác chiến và lưu điểm hồi sinh. Đồng hồ 30 phút.

Toàn bộ: Toàn bộ 41 boss chủ lực và mini boss của các chương đang mở, theo đúng thứ tự cốt truyện. Có điểm hồi sinh sau mỗi boss: chơi dần qua bao nhiêu lần cũng được. Mỗi boss là một trận mới: quân không được giữ và bạn bắt đầu với cùng lượng CP; chỉ hỗ trợ tác chiến được giữ (chọn sau mỗi boss chủ lực, tối đa +40% sức mạnh đội quân, sau đó chỉ còn các hỗ trợ đổi cách chơi). Xếp hạng theo tổng thời gian.

#### Hỗ trợ tác chiến (12)

| Hỗ trợ | Id | Tác dụng | Sức mạnh quân |
|---|---|---|---|
| Gia cố thân xe | `hull` | Máu toàn quân +15%, cả xe tới sau. | +15% |
| Huấn luyện pháo thủ | `gunnery` | Sát thương toàn quân +10%. | +10% |
| Nạp đạn nhanh | `loaders` | Toàn quân bắn nhanh hơn 12%. | +12% |
| Tinh chỉnh động cơ | `engines` | Toàn quân chạy nhanh hơn 12%. | +6% |
| Sửa chữa dã chiến | `regen` | Khi không trúng đạn, mỗi xe tự hồi 1% máu mỗi giây. | +8% |
| Điều phối nhanh | `rapid` | Hồi chiêu thẻ hỗ trợ ngắn hơn 25%. | đổi cách chơi, không tính vào trần |
| Đoàn tiếp tế | `logistics` | Thu nhập CP +20%. | +10% |
| Quỹ chiến tranh | `warchest` | Nhận ngay 35 CP. | +5% |
| Thêm kíp lái | `supply` | Giới hạn quân +6. | +8% |
| Xưởng lưu động | `workshop` | Giờ nghỉ sửa quân gấp đôi. | +5% |
| Hợp đồng săn thưởng | `bounty` | Tiền thưởng CP khi hạ boss +50%. | +5% |
| Tiếp viện miễn phí | `airdrop` | Ba xe đắt nhất trong bộ bài được thả xuống ngay, miễn phí. | đổi cách chơi, không tính vào trần |

Sheet: 03_boss/Sanhunt — Săn trùm (41 dòng, 9 cột)

| id | thu_tu | chu_luc | chuong | cach_xep | phong_khong | tuan |
|---|---|---|---|---|---|---|
| argus | 36 | FALSE | 10 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| armored_train | 9 | FALSE | 4 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| bastion_mk0 | 1 | FALSE | 1 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| behemoth | 4 | TRUE | 2 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| behemoth_inferno | 3 | FALSE | 2 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| behemoth_mk0 | 8 | FALSE | 13 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| behemoth_mk2 | 18 | FALSE | 6 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| behemoth_tempest | 10 | FALSE | 4 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| caspian | 28 | FALSE | 9 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| cerberus | 21 | FALSE | 6 | unslotted | NEED_CODE_CHECK | NEED_CODE_CHECK |
| command_airship | 35 | TRUE | 10 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| daedalus | 39 | TRUE | 11 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| drone_mothership | 16 | TRUE | 5 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| earth_borer | 24 | FALSE | 8 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| fenrir | 7 | FALSE | 3 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |

*15 / 41 dòng đầu: xem sheet 03_boss/Sanhunt.*

Sheet: 03_boss/Sanhunt_ho_tro — Săn trùm: hỗ trợ tác chiến (12 dòng, 8 cột)

| id | ten_vi | icon | kind | strength | value |
|---|---|---|---|---|---|
| airdrop | Tiếp viện miễn phí | reinforce | Airdrop |  | 3 |
| bounty | Hợp đồng săn thưởng | trophy | Bounty | 0.05 | 0.5 |
| engines | Tinh chỉnh động cơ | move | Engines | 0.06 | 0.12 |
| gunnery | Huấn luyện pháo thủ | crosshair | Gunnery | 0.1 | 0.1 |
| hull | Gia cố thân xe | shield | Hull | 0.15 | 0.15 |
| loaders | Nạp đạn nhanh | ammo | Loaders | 0.12 | 0.12 |
| logistics | Đoàn tiếp tế | cp | Logistics | 0.1 | 0.2 |
| rapid | Điều phối nhanh | airstrike | Rapid |  | 0.25 |
| regen | Sửa chữa dã chiến | repair | Regen | 0.08 | 0.01 |
| supply | Thêm kíp lái | people | Supply | 0.08 | 6 |
| warchest | Quỹ chiến tranh | coin | WarChest | 0.05 | 35 |
| workshop | Xưởng lưu động | gear | Workshop | 0.05 | 1 |

Sheet: 03_boss/Sanhunt_chua_xep — Săn trùm: boss chưa có ô chương (10 dòng, 4 cột)

| id | sau_chuong |
|---|---|
| behemoth_mk0 | 3 |
| cerberus | 6 |
| garuda | 10 |
| hydra | 9 |
| hyperion | 12 |
| kraken | 9 |
| monster | 8 |
| morrigan | 9 |
| nyx | 4 |
| stymphalos | 5 |

## 11. Tháp canh, xe tinh nhuệ và boss

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss; 03_boss/Boss_vu_khi; 03_boss/Boss_bo_phan; 03_boss/Boss_sieu_vu_khi; 03_boss/Boss_ho_tong; 03_boss/Boss_hang; 04_can_cu_thap/Thap (lời hướng dẫn: 10_model_tai_san/Dia_phuong_hoa guide.<id>). Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §11. Tháp canh.

#### Tháp và công sự

Tháp cố định chặn lưới đường đi khi xuất hiện; trong Chiếm cứ điểm mỗi cứ điểm có tháp trung lập bắn mọi phe và dựng lại sau một thời gian; mỗi phe có sở chỉ huy (HQ) có máu (phá được hay không tùy chế độ, phần 6). Tháp của căn cứ người chơi xếp theo cỡ ô (phần 6), có hạng, nhánh ở hạng 7 và 3 ô đồ.

#### Xe tinh nhuệ

Phiên bản tân trang: +60% máu, +25% sát thương, 1–2 kỹ năng tinh nhuệ, thanh máu vàng và vòng vàng trên bản đồ nhỏ; sức mạnh thực đo được 1,8–2,2 lần bản thường. Địch không còn nhận tinh nhuệ theo xác suất mà theo **ngân sách**: tinh nhuệ giá 1,6 lần, phần chi tiêu theo độ khó (Dễ 5%, Thường 10%, Khó 15%, Anh hùng 20%, Thép 25%), trần 1–5 xe cùng lúc; tướng ưu tiên loại xe của mình. Hạ tinh nhuệ hoàn CP theo giá thật và thưởng một ít xu, có tỷ lệ nhỏ rơi bản thiết kế.

| Tên | Giá | Giáp | Máu | Tốc độ | Vũ khí | DPS nhẹ/nặng/bay | Kỹ năng | Tham khảo |
|---|---|---|---|---|---|---|---|---|
| **Phòng không tinh nhuệ** | 6 CP (địch) | Trước 2 (Vừa) · Hông 0 (Không giáp) · Sau 0 (Không giáp) · Nóc 0 (Không giáp) | 1.041 | 8.5 | twin_35_ahead, sam | 102 / 51 / 182 | elite_overdrive | Rheinmetall Skyranger 35 (đạn AHEAD), Gepard (khung gốc) — Phòng không tinh nhuệ, đạn nổ trên không AHEAD |
| **Xe bọc thép tinh nhuệ** | 11 CP (địch) | Trước 3 (Dày) · Hông 1 (Mỏng) · Sau 0 (Không giáp) · Nóc 0 (Không giáp) | 1.544 | 9 | autocannon_30, mg_coax, atgm | 125 / 62 / 11 | elite_emp | M2 Bradley / BMP-3 (khung gốc), 2A42 30 mm — Xe chiến đấu bộ binh tinh nhuệ |
| **Pháo tự hành tinh nhuệ** | 11 CP (địch) | Trước 2 (Vừa) · Hông 0 (Không giáp) · Sau 0 (Không giáp) · Nóc 0 (Không giáp) | 891 | 6 | howitzer, hmg_selfdef_15 | 101 / 60 / 21 | elite_barrage | CAESAR 155 mm — Lựu pháo tự hành tinh nhuệ |
| **Trực thăng tinh nhuệ** | 18 CP (địch) | cấp 2 (Vừa) | 1.485 | 15 | hellfire_volley, heli_gun, heli_rockets, stinger_atas | 164 / 98 / 136 | elite_flares, elite_barrage | AH-64 Apache, AGM-114L Hellfire Longbow — Apache tinh nhuệ, bắn loạt Hellfire |
| **Cường kích tinh nhuệ** | 37 CP (địch) | cấp 2 (Vừa) | 1.366 | 32 | jet_cannon, s8_pods, jet_bombs, kh29, r60 | 553 / 301 / 25 | elite_flares | Su-25 Frogfoot, A-10 Thunderbolt II — Cường kích tinh nhuệ |
| **Xe phóng drone FPV tinh nhuệ** | 11 CP (địch) | Trước 2 (Vừa) · Hông 0 (Không giáp) · Sau 0 (Không giáp) · Nóc 0 (Không giáp) | 1.247 | 9 | fpv_swarm, hmg_selfdef_18 | 107 / 66 / 21 | elite_barrage | KamAZ Typhoon-K, RG-33 MRAP, drone FPV — Xe phóng drone FPV tinh nhuệ |
| **Grad tinh nhuệ** | 13 CP (địch) | Trước 2 (Vừa) · Hông 0 (Không giáp) · Sau 0 (Không giáp) · Nóc 0 (Không giáp) | 950 | 8.5 | grad_cluster, hmg_selfdef_15 | 86 / 50 / 18 | elite_barrage | BM-21 Grad (khung Ural-375D) — Xe tải Grad 122 mm tinh nhuệ, đầu đạn chùm |
| **Tăng hạng nặng tinh nhuệ** | 26 CP (địch) | Trước 4 (Rất dày) · Hông 3 (Dày) · Sau 2 (Vừa) · Nóc 2 (Vừa) | 5.632 | 4.6 | gun_152_heat, autocannon_30, hmg_roof | 198 / 110 / 18 | elite_overdrive | Object 195 / T-95 (2A83 152 mm, đạn HEAT) — Siêu tăng tinh nhuệ, đạn nổ lõm 152 mm |
| **Tên lửa phòng không tầm xa tinh nhuệ** | 29 CP (địch) | Trước 2 (Vừa) · Hông 0 (Không giáp) · Sau 0 (Không giáp) · Nóc 0 (Không giáp) | 1.307 | 6 | sam_48n6 | 0 / 0 / 165 | elite_overdrive | S-400 (48N6), S-300PMU (5P85) — Tên lửa phòng không tầm xa tinh nhuệ |
| **Tăng chủ lực tinh nhuệ** | 13 CP (địch) | Trước 4 (Rất dày) · Hông 2 (Vừa) · Sau 1 (Mỏng) · Nóc 1 (Mỏng) | 2.673 | 6.2 | gun_125_elite, mg_coax, hmg_roof | 118 / 65 / 29 | elite_shield | T-90M (2A46M-5 125 mm), Leopard 2A4 / M1 Abrams (khung gốc) — Xe tăng chủ lực tinh nhuệ, giáp tăng cường sơn đen |
| **Pháo phản lực tinh nhuệ** | 13 CP (địch) | Trước 2 (Vừa) · Hông 0 (Không giáp) · Sau 0 (Không giáp) · Nóc 0 (Không giáp) | 950 | 6.5 | mlrs_elite, hmg_selfdef_15 | 89 / 53 / 18 | elite_barrage | M142 HIMARS / M270, M30 GMLRS 227 mm (đầu đạn chùm) — Xe phóng rốc-két tinh nhuệ, đầu đạn chùm |
| **Pháo chống tăng tinh nhuệ** | 11 CP (địch) | Trước 4 (Rất dày) · Hông 2 (Vừa) · Sau 1 (Mỏng) · Nóc 1 (Mỏng) | 1.841 | 7.5 | gun_105_apfsds, hmg_roof | 117 / 81 / 18 | elite_barrage, elite_smoke | 2S25 Sprut-SD (2A75 125 mm APFSDS) — Pháo chống tăng tinh nhuệ, đạn xuyên dưới cỡ |

#### Boss

Mọi boss có bộ phận theo cùng một bộ luật (phase 9); boss cuối chương còn có thanh máu nhiều pha.

- **Máu bộ phận** là một phần máu thân (đọc trực tiếp, nên tăng theo cấp chiến dịch, độ khó và bản mạnh của nhiệm vụ): mỗi bộ phận 8–15%; boss từ 5 súng trở lên có tổng 50–70%, boss chỉ có 3–4 thứ phá được có tổng 35–47%.
- **Máu thân** giảm còn ×0,76 đến ×0,90 (1,125 / (1 + 0,7 × tổng phần bộ phận)) để trận dài hơn khoảng 12% (ước tính theo mô hình, đo ở phase kiểm tra).
- **Vỡ một bộ phận:** súng trên đó im cả trận; kỹ năng dừng khi mọi bộ phận mang nó đều vỡ; cơ chế dừng (phát bắn của siêu pháo, đào hầm của Giun Đất, đổ quân của tàu đệm khí, hào quang của Tổng Tư Lệnh); áp dụng phạt tốc độ, quay, nhịp bắn, độ tản; thân mất thêm 30% máu của bộ phận đó.
- **Chỉ phát trúng trực tiếp** làm hại bộ phận; nổ lan, lửa và hỏa lực hỗ trợ rơi vào thân. Đạn trúng bộ phận nhô ra ngoài thân (quạt, đầu máy, đầu kéo) nay tính là trúng.
- **Tự sửa:** Tàu Thép và Bastion một lần mỗi trận hồi bộ phận đã vỡ có phát bắn mặt đất nặng nhất lên 50%.
- **Nhắm bắn:** mỗi xe nhắm bộ phận nguy hiểm nhất với nó trong tầm (phòng không nhắm bộ phận bắn máy bay, diệt tăng nhắm bộ phận dày nhất); 2 trên 5 phát vẫn vào thân.
- **Lệnh bắn bộ phận:** chạm vào biểu tượng bộ phận dưới thanh máu boss hoặc chạm thẳng vào bộ phận trên mô hình: mọi xe trong tầm dồn hỏa lực vào đó tới khi vỡ; chạm lại để hủy.
- **Săn trùm** thưởng 2 CP cho mỗi bộ phận vỡ.

##### Lửa và khói ở chỗ vỡ

- Dưới 50% máu bộ phận bốc khói và tóe lửa điện, dưới 25% bắt cháy.
- Lúc vỡ: súng và kho đạn nổ lớn (có mảnh văng ở đồ họa Cao), bộ phận năng lượng lóe sáng với vòng xanh và tia điện, động cơ bùng cầu lửa; bộ phận biến mất, thay bằng mảnh xác.
- Sau khi vỡ, lửa và cột khói đen ở lại tới hết trận; thân boss cháy thêm ở 66% và 33% máu; boss bay hoặc chạy nhanh kéo vệt khói từ động cơ vỡ.
- Tối đa 8 điểm lửa mỗi boss (5 ở đồ họa Thấp, khói và tia lửa giảm một nửa). Khi boss chết mọi đám cháy bùng lên, xác cháy 25–35 giây.
- Chỉ là hình ảnh: mô phỏng không thấy khói, tầm nhìn qua boss đang cháy không đổi.

giáp thân trước 4 / hông 4 / sau 4 / nóc 3; Tổng 35% máu thân trong 3 bộ phận; tự sửa một bộ phận một lần mỗi trận; pha ở 45%.

**Mẹo:** phá **khẩu cối** trước; hai tháp pháo chỉ bắn gần.

Pháo đài biết đi đầu tiên của Brandt, bản nguyên mẫu của Bastion: ít pháo hơn, giáp mỏng hơn, vẫn kíp lái lì lợm ấy.

giáp thân trước 4 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 4 bộ phận; pha ở 45%.

**Mẹo:** mỗi **súng phun lửa** bị phá là lửa giảm một nửa; phá cả hai thì nó chỉ còn bắn rốc-két nhiệt áp. Trong lúc đó hãy giữ ngoài 20 m và tránh vệt lửa phía sau nó: **thùng nhiên liệu** nuôi vệt lửa đó.

Một chiếc Behemoth dựng lại quanh hai súng phun lửa lớn và một hộp rốc-két nhiệt áp. Nó đốt cháy cả mặt đất. Tránh xa tầm với của nó và cứ thế mà nện.

giáp thân trước 2 / hông 2 / sau 2 / nóc 2; Tổng 35% máu thân trong 6 bộ phận; pha ở 45%.

**Mẹo:** phá **cánh quạt sau** là nó xoay chậm một nửa và khó ngắm; hộp rốc-két và pháo dưới mũi là thứ làm hại quân mặt đất.

Pháo hạm bay của Orlov, to như con tàu và chậm như vậy: ổ rốc-két, pháo sáng mồi bẫy và một tốp trực thăng hộ tống. Chỉ phòng không và tiêm kích với tới nó. Mang theo mọi bệ phóng có được.

giáp thân trước 4 / hông 4 / sau 3 / nóc 2; Tổng 35% máu thân trong 3 bộ phận; pha ở 45%.

**Mẹo:** mỗi **hộp rốc-két** bị phá là rốc-két của nó giảm một nửa; cao xạ là thứ duy nhất chống máy bay.

Xe tiên phong mùa đông của Orlov: một thợ săn hạng nặng chạy trước các trận địa pháo qua tuyết và đánh dấu mục tiêu cho chúng.

giáp thân trước 3 / hông 3 / sau 2 / nóc 1; Tổng 35% máu thân trong 4 bộ phận; pha ở 45%.

**Mẹo: pháo chính** là khẩu mạnh nhất; phá cả hai **pháo sườn** thì nó chỉ còn bắn được phía trước.

Chiếc Behemoth đầu tiên từng được chế tạo, do một kỹ sư trẻ tên Mara Lind vẽ và Varga hoàn thiện. Chậm hơn, mỏng hơn và già hơn những đứa con của nó, và vẫn canh giữ Foundry nơi nó ra đời.

giáp thân trước 4 / hông 3 / sau 3 / nóc 2; Tổng 35% máu thân trong 5 bộ phận; tự sửa một bộ phận một lần mỗi trận; pha ở 45%.

**Mẹo:** phá **đầu máy** trước để nó chậm một nửa, rồi tới các toa pháo. Nó tự vá một bộ phận một lần, ưu tiên pháo nặng, nên hãy phá toa đó lần nữa.

Đoàn tàu bọc thép của Kessler: toa pháo và toa giáp chạy đúng giờ. Bị bắn là nó tự thả khói, vừa chạy vừa tự vá. Phải chặn nó trước khi tới bến cảng.

giáp thân trước 4 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 5 bộ phận; pha ở 45%.

**Mẹo:** phá **máy phát khiên** trước khi nó xuống máu, không thì khiên sẽ nuốt đợt dồn hỏa lực của bạn; **bộ phát la-de** bắn hạ tên lửa, drone và rốc-két, nên hãy dùng pháo, đạn hoặc khói cho tới khi phá được nó.

Một chiếc Behemoth dựng quanh khẩu súng điện từ: nạp điện, phát sáng rồi xuyên thủng mọi thứ trên một đường thẳng. Hai pháo điện từ và một tấm khiên. Dàn quân ra và áp sát.

giáp thân trước 4 / hông 4 / sau 3 / nóc 2; Tổng 35% máu thân trong 3 bộ phận; pha ở 45%.

**Mẹo:** phá **ống phóng tên lửa** để chặn tên lửa hành trình, phá **CIWS** trước khi dùng tên lửa.

Tàu khu trục chỉ huy của Kessler: nhanh, nhiều vũ khí, và luôn là chiếc đầu tiên vào cảng.

giáp thân trước 4 / hông 4 / sau 3 / nóc 2; Tổng 35% máu thân trong 4 bộ phận; pha ở 45%.

**Mẹo: CIWS** chặn tên lửa của bạn; ống phóng mang tên lửa chống hạm của nó.

Tàu khu trục kiểu Zumwalt mà hạm đội không bao giờ ghi tên: nó chỉ hiện trên radar khi nó muốn.

giáp thân trước 4 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 6 bộ phận; pha ở 45%.

**Mẹo:** hai **giàn phóng drone** nuôi bầy drone của nó: phá cả hai là hết phóng. **Cột gây nhiễu** làm tên lửa dẫn đường trong 30 m bay lệch: phá nó bằng pháo trước khi trông vào tên lửa. Nên phá bộ phát EMP trước khi áp sát.

Pháo đài drone của Venn: không có pháo chính, chỉ có các giàn phóng hết bầy này tới bầy khác, một dàn tên lửa phòng không và pháo cao xạ. Cực nguy hiểm với máy bay; xe tăng và pháo binh mới hạ được nó.

giáp thân trước 1 / hông 1 / sau 1 / nóc 1; Tổng 35% máu thân trong 2 bộ phận; pha ở 45%.

**Mẹo: khoang drone** là tất cả những gì nó có.

Một tàu mang drone cỡ nhỏ trong chương trình drone của Venn. Aurel vẫn cho đóng tiếp sau khi bà bỏ đi.

giáp thân trước 1 / hông 1 / sau 1 / nóc 1; Tổng 35% máu thân trong 3 bộ phận; pha ở 45%.

**Mẹo: khoang drone** là vũ khí của nó; phá cả hai thì chỉ còn cao xạ.

Tám drone phản lực nhỏ bay như một, theo kiểu Loyal Wingman; câu trả lời của Matriarch khi mất tàu mẹ.

giáp thân trước 5 / hông 3 / sau 2 / nóc 3; Tổng 35% máu thân trong 9 bộ phận; tự sửa một bộ phận một lần mỗi trận; pha ở 60%, 25%.

**Mẹo:** mỗi **tháp pháo tự động** chỉ phủ một góc: phá các tháp ở một phía rồi đánh từ phía đó. Khi tự vá nó ưu tiên khẩu cối.

Pháo đài biết đi đầu tiên của Hegemon: bốn tháp pháo tự động, một khẩu cối hạng nặng và kíp lái biết tự vá giáp dưới làn đạn. Chiếc ở Ashfield là mẫu đời đầu, chậm hơn và mỏng hơn những chiếc về sau.

giáp thân trước 3 / hông 2 / sau 1 / nóc 1; Tổng 35% máu thân trong 8 bộ phận; pha ở 45%.

**Mẹo:** phá **cửa đổ bộ** là nó hết đổ quân; mỗi **quạt đẩy** bị phá làm nó chậm 30%. Hai **pháo phòng thủ tầm gần** bắn hạ tên lửa và rốc-két: phá chúng trước khi tấn công bằng tên lửa.

Tàu đệm khí đổ bộ của Hegemon, chở cả một đại đội thiết giáp lên bãi biển với tốc độ sáu mươi hải lý và tự yểm trợ cuộc đổ bộ bằng pháo của mình. Phải đánh nó trước khi nó kịp dỡ quân.

giáp thân trước 4 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 4 bộ phận; pha ở 45%.

**Mẹo: pháo chính** là đòn mạnh nhất; **hệ thống bảo vệ** bắn hạ hai tên lửa mỗi loạt.

Chiếc Behemoth của Varga dựng lại sau lần bại trận đầu tiên: nặng hơn, lắp hệ sưởi cho mùa đông, và hung hãn hơn.

giáp thân trước 3 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 4 bộ phận; pha ở 45%.

**Mẹo:** cao xạ đuổi máy bay; **pháo chính** là vũ khí mạnh nhất.

Đoàn xe tải quân sự nối rơ-moóc, mỗi xe mang một vũ khí: toán lính hoang mạc trên đường.

giáp thân trước 5 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 10 bộ phận; pha ở 60%, 25%.

**Mẹo:** cho xe tăng dồn bắn **pháo chính**: mất cặp nòng đó nó chỉ còn là khối thép chậm chạp với cao xạ và tên lửa. **Hệ thống bảo vệ chủ động** bắn hạ hai tên lửa chống tăng mỗi lượt: phá nó, hoặc dùng pháo. Phòng không nên phá cao xạ trước nếu máy bay ta ở gần.

Chiến hạm mặt đất của Varga: pháo chính mỗi phát hạ một xe tăng, đội hộ tống bám theo vào trận và lớp vỏ chịu được gần hết hỏa lực của lữ đoàn. Mara nói các tấm giáp phía sau là điểm yếu của nó.

giáp thân trước 4 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 3 bộ phận; pha ở 45%.

**Mẹo:** phá **ăng-ten chỉ huy** trước tiên: quân của nó mất ngay hào quang chỉ huy.

Xe chỉ huy riêng của Aurel, Atlas: lớp giáp nặng nhất Hegemon từng đúc, bao quanh hệ thống liên lạc điều hành toàn bộ bãi phóng.

giáp thân trước 4 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 4 bộ phận; pha ở 45%.

**Mẹo:** đánh vào **mũi khoan** trong vài giây ngay sau khi nó trồi lên: vỡ rồi là nó không bao giờ chui xuống đất được nữa.

Cỗ máy khoan cũ của Varga, Tartarus: nó nghiến xuyên dưới tường thành và thân đập rồi trồi lên đúng chỗ không ai canh. Phải tiêu diệt nó trước khi nó tới trạm phát điện.

giáp thân trước 4 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 8 bộ phận; pha ở 45%.

**Mẹo:** phá **tháp pháo trên thùng** là mất pháo 125 mm; phá một **lốp trước** thì cú lao lệch và dừng; **lốp sau** giáp cấp 1; phá **ca-bin** là súng máy ngừng bắn.

Xe tải mỏ bọc thép của Thorne ở Deepcut Mine: một chiếc BelAZ-75710 hàn tháp pháo xe tăng lên thùng, lưỡi húc ở mũi và súng máy trên nóc ca-bin.

giáp thân trước 5 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 9 bộ phận; pha ở 60%, 25%.

**Mẹo:** phá **lựu pháo** để chấm dứt các loạt pháo dồn, và phá bộ phát EMP trước khi thiết giáp ta áp sát.

Mỏ neo của tuyến Frostpeak: một pháo đài di động với lựu pháo, đội hộ tống và xung EMP làm tê liệt mọi thứ xung quanh.

giáp thân trước 2 / hông 2 / sau 2 / nóc 1; Tổng 35% máu thân trong 4 bộ phận; pha ở 45%.

**Mẹo:** phá **bệ tên lửa** trên lưng để chặn tên lửa của nó; phá **cụm động cơ** ở mũi để các lượt lao chậm lại.

Một con tàu bay sát mặt sóng với tốc độ của máy bay và đổ quân lên bất cứ bãi biển nào.

giáp thân trước 4 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 4 bộ phận; pha ở 45%.

**Mẹo: cửa ống phóng** mang tên lửa của nó; pháo boong chỉ bắn khi nổi.

Tàu ngầm mang drone theo khái niệm: nhỏ hơn Typhon, nhanh hơn, và im lặng cho tới khi nắp ống mở.

giáp thân trước 1 / hông 1 / sau 1 / nóc 1; Tổng 35% máu thân trong 4 bộ phận; pha ở 45%.

**Mẹo:** phá cả hai **khoang tên lửa** là hết tên lửa; phá **động cơ** thì nó chậm lại.

Chiếc tiêm kích riêng của Wolff, làm cho một mình hắn: nhanh, khó thấy trên radar, mang tên lửa không đối không và bom dẫn đường.

giáp thân trước 2 / hông 2 / sau 2 / nóc 2; Tổng 35% máu thân trong 8 bộ phận; pha ở 45%.

**Mẹo:** mỗi **động cơ** bị phá làm vòng bay chậm 15%: bay chậm hơn là phòng không ta có thêm thời gian. Khẩu 105 mm là thứ giết xe tăng.

Pháo hạm bay vòng trên cao quanh con mồi với khẩu 105 mm và hai khẩu 40 mm dọc sườn. Nó không bao giờ hạ thấp. Hoặc phòng không và tiêm kích, hoặc chẳng gì cả.

giáp thân trước 4 / hông 4 / sau 4 / nóc 4; Tổng 35% máu thân trong 3 bộ phận.

**Mẹo: la-de phòng thủ điểm** là lớp bảo vệ, **khoang đổ bộ** mang các đợt thả.

Chiếc Icarus đầu tiên chưa hoàn thiện, bay trên Skyhold như một cuộc thử nghiệm thực địa. Đánh nó đủ đau, nó sẽ bỏ chạy.

giáp thân trước 2 / hông 2 / sau 2 / nóc 2; Tổng 35% máu thân trong 3 bộ phận; pha ở 45%.

**Mẹo: radar** chỉ điểm cho pháo địch.

Khí cầu trinh sát bọc giáp của Wolff: thấy hết mọi thứ và chỉ đường cho máy bay của hắn.

giáp thân trước 5 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 14 bộ phận; pha ở 60%, 25%.

**Mẹo:** chiếm **hải đăng** để thấy hạm đội; phá cả hai **CIWS** (hoặc đánh chìm tuần dương hạm và tàu hộ vệ bên cạnh) trước khi dùng tên lửa và drone; mỗi **pháo chính** bị phá bớt một phần ba loạt pháo và loạt bắn mạn; phá **radar** thì đạn pháo rơi lệch; phá **buồng máy** thì nó chạy chậm lại.

Soái hạm của Kessler: thiết giáp hạm lớn nhất từng được đóng, ba tháp pháo ba nòng 406 mm, tháp chỉ huy kiểu chùa trên cả một rừng súng, ống phóng cạnh ống khói và khoang chở tàu đổ bộ. Hông tàu chặn được đạn xe tăng; boong thì không. Nó không bao giờ đánh ở nơi nó không rút được.

giáp thân trước 2 / hông 2 / sau 2 / nóc 2; Tổng 35% máu thân trong 11 bộ phận; pha ở 60%, 25%.

**Mẹo:** phá **cửa thả drone** và **khoang phóng UAV** để chặn drone, và phá **máy phát khiên** trước khi nó xuống máu.

Tàu sân bay biết bay của Hive: phóng drone từ bụng, bắn pháo sáng mồi bẫy và dựng khiên khi bị thương. Chỉ những gì bắn được lên trời mới kết liễu được nó.

giáp thân trước 5 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 9 bộ phận; pha ở 60%, 25%.

**Mẹo:** vòng ra sau đánh **cửa xưởng** (giáp cấp 2): phá một cửa là sinh xe giảm một nửa, phá cả hai là ngừng hẳn; phá **cụm xích** để làm chậm.

Nhà máy di động của Varga: vừa lăn bánh vừa đóng xe tăng, rồi tung chúng ra trận qua các cửa thả.

giáp thân trước 5 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 9 bộ phận; pha ở 60%, 25%.

**Mẹo: đầu máy** là bộ phận quan trọng nhất: phá nó là tàu chỉ bò nửa tốc độ trong khi bạn đánh toa tên lửa.

Một đoàn tàu tên lửa đang băng qua Metro City tới bãi phóng. Tới nơi là đếm ngược bắt đầu. Đừng để nó tới nơi.

giáp thân trước 5 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 10 bộ phận; pha ở 60%, 25%.

**Mẹo:** mỗi **cụm xích** (giáp cấp 2) bị phá là nó chậm lại; **cần gầu** mang đòn quét; **bánh gầu** (giáp cấp 4) là thứ nghiền.

Một máy xúc bánh gầu to bằng cả tòa nhà, được Thorne bọc thép và chĩa thẳng vào lữ đoàn.

giáp thân trước 5 / hông 3 / sau 2 / nóc 3; Tổng 35% máu thân trong 9 bộ phận; tự sửa một bộ phận một lần mỗi trận; pha ở 60%, 25%.

**Mẹo: khẩu cối** là nòng dài có máu riêng; phá nó là hết quả đạn 800 mm. Bốn tháp pháo chỉ để tự vệ.

Một khẩu pháo cỡ 2B1 Oka thay Gungnir làm mối đe dọa lớn của quân đội: chậm, to và tự tin.

giáp thân trước 5 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 7 bộ phận; pha ở 60%, 25%.

**Mẹo: cửa ống phóng** mang tên lửa (lộ trên mặt nước lúc cảnh báo); **tháp chỉ huy** ngắm tên lửa phòng không; **sô-na** là hệ điều khiển hỏa lực.

Tàu ngầm tên lửa của Kessler, giờ trong tay Thorne: nổi lên, phóng một loạt rồi lại lặn.

giáp thân trước 5 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 14 bộ phận; pha ở 60%, 25%.

**Mẹo: boong cất cánh** nuôi máy bay và mang đòn không kích; phá nó trước. **CIWS** bắn hạ tên lửa trước khi chúng trúng.

Soái hạm của hạm đội mới của Kessler: tàu sân bay đánh bằng máy bay, không bằng pháo.

giáp thân trước 2 / hông 2 / sau 2 / nóc 2; Tổng 35% máu thân trong 10 bộ phận; thân không nhận sát thương tới khi vỡ động cơ ×2; pha ở 60%, 25%.

**Mẹo:** phá hai **động cơ** để mở thân; sau đó tới các nhà chứa drone và radar ngắm cao xạ.

Sở chỉ huy bay của Wolff trên Skyhold: radar, tên lửa và một khoang chứa drone. Nó điều khiển mọi máy bay Hegemon trên Meridian Coast.

giáp thân trước 2 / hông 2 / sau 2 / nóc 2; Tổng 35% máu thân trong 10 bộ phận; thân không nhận sát thương tới khi vỡ động cơ ×2; pha ở 60%, 25%.

**Mẹo:** phá khoang bom là hết thảm bom; phá động cơ thì nó chậm lại.

Người kế nhiệm máy bay ném bom của Wolff: một cánh bay to bằng nhà chứa máy bay, có tiêm kích hộ tống.

giáp thân trước 3 / hông 2 / sau 1 / nóc 1; Tổng 35% máu thân trong 8 bộ phận; pha ở 45%.

**Mẹo:** phá **trạm chỉ thị mục tiêu** là đạn rơi lệch; mỗi **đầu máy kéo** bị phá làm nó bắn thưa hơn; phá **pháo chính** là nó hết bắn.

Một khẩu pháo điện từ trên đoàn tàu: toa pháo ray điện từ, các toa tụ điện và đầu máy diesel hiện đại. Kessler dùng nó bắn một phát xuyên cả đội hình từ cách bốn mươi cây số.

giáp thân trước 3 / hông 3 / sau 3 / nóc 3; Tổng 35% máu thân trong 8 bộ phận.

**Mẹo:** phá **cửa thả khoang** (mỗi cửa mất là thả chậm hơn; mất một cửa thì đòn đổ bộ lớn chỉ còn ba khoang) và **tháp la-de phòng thủ** trước khi dùng tên lửa.

Con tàu đưa quân của Aurel từ quỹ đạo xuống Skygate Array, từng khoang một.

giáp thân trước 4 / hông 4 / sau 4 / nóc 4; Tổng 35% máu thân trong 12 bộ phận.

**Mẹo:** phá **động cơ đẩy chính** để nhốt nó ở tầng thấp, và phá **ăng-ten liên kết vệ tinh** để chặn thanh vonfram; nên dọn hai **tháp la-de phòng thủ điểm** trước khi trông vào tên lửa.

Chiến hạm quỹ đạo của Aurel: thân tàu hình mũi dao, thượng tầng bậc thang dưới tháp chỉ huy và cả một dãy động cơ ở đuôi, được chế tạo để tấn công từ quỹ đạo và đưa Aurel ra ngoài tầm với của mọi người. Chiếc đầu tiên xuất hiện sẽ bỏ chạy khi bị thương đủ nặng. Chiếc trên bệ phóng đã hoàn chỉnh.

giáp thân trước 4 / hông 4 / sau 4 / nóc 4; Tổng 35% máu thân trong 9 bộ phận.

**Mẹo:** tia **la-de chính** mang đòn tia mặt trời; phá nó là hết tia. **Tháp la-de phòng thủ** bắn hạ tên lửa của bạn.

Một trong những chấm sáng cuối cùng còn trên quỹ đạo sau phần kết: trạm gương kiểu Znamya.

Sheet: 03_boss/Boss — Boss (41 dòng, 329 cột)

| id | phan_loai | ten_en | ten_vi | ten_ngan_vi | base_cp | mau_hp | mau_trong_tran_hp | giap_hong | giap_noc |
|---|---|---|---|---|---|---|---|---|---|
| argus | mini | Argus · Scout Airship | Argus · Khí cầu trinh sát | Argus | 0 | 94850 | 80622.5 | 2 | 2 |
| armored_train | mini | Juggernaut · Armoured Train | Juggernaut · Đoàn tàu bọc thép | Juggernaut | 0 | 37750 | 32087.5 | 3 | 2 |
| bastion_mk0 | mini | Bastion Mk.0 · Prototype Fortress | Bastion Mk.0 · Pháo đài nguyên mẫu | Bastion Mk.0 | 0 | 19250 | 16362.5 | 4 | 3 |
| behemoth | main | Behemoth · Steel Monster | Behemoth · Quái vật thép | Behemoth | 0 | 33550 | 28517.5 | 3 | 2 |
| behemoth_inferno | mini | Inferno · Flame Behemoth | Inferno · Behemoth phun lửa | Inferno | 0 | 24600 | 20910.0 | 3 | 2 |
| behemoth_mk0 | mini | Behemoth Mk.0 · Prototype Behemoth | Behemoth Mk.0 · Behemoth nguyên mẫu | Behemoth Mk.0 | 0 | 33900 | 28815.0 | 3 | 1 |
| behemoth_mk2 | mini | Behemoth Mk.II · Upgraded Behemoth | Behemoth Mk.II · Behemoth nâng cấp | Behemoth Mk.II | 0 | 53500 | 45475.0 | 3 | 2 |
| behemoth_tempest | mini | Tempest · Railgun Behemoth | Tempest · Behemoth pháo điện từ | Tempest | 0 | 37750 | 32087.5 | 3 | 2 |
| caspian | mini | Caspian · Ekranoplan | Caspian · Tàu bay sát mặt nước | Caspian | 0 | 81300 | 69105.0 | 2 | 1 |
| cerberus | mini | Cerberus · Three-Car Convoy | Cerberus · Đoàn xe ba khung | Cerberus | 0 | 53500 | 45475.0 | 3 | 2 |
| command_airship | main | Roc · Flying Headquarters | Roc · Khí cầu chỉ huy | Roc | 0 | 137250 | 116662.5 | 2 | 2 |
| daedalus | main | Daedalus · Orbital Lander | Daedalus · Tàu đổ bộ quỹ đạo | Daedalus | 0 | 156900 | 133365.0 | 2 | 1 |
| drone_mothership | main | Matriarch · Drone Mothership | Matriarch · Tàu mẹ drone | Matriarch | 0 | 63100 | 53635.0 | 2 | 2 |
| earth_borer | mini | Tartarus · Tunnelling Machine | Tartarus · Máy khoan | Tartarus | 0 | 72000 | 61200.0 | 3 | 2 |
| fenrir | mini | Fenrir · Vanguard | Fenrir · Xe tiên phong | Fenrir | 0 | 29950 | 25457.5 | 4 | 2 |

*15 / 41 dòng đầu: xem sheet 03_boss/Boss; in 10 / 329 cột; 163 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 03_boss/Boss_vu_khi — Boss: vũ khí theo bệ (223 dòng, 22 cột)

| id | boss_id | chi_so_be | vu_khi | slot | aim | bo_phan | so_nong | sat_thuong_moi_phat | thoi_gian_nap_s |
|---|---|---|---|---|---|---|---|---|---|
| argus/0 | argus | 0 | p26_roc_main_roc_bombs | gun | Free |  | 1 | 700 | 33.34 |
| argus/1 | argus | 1 | p26_roc_main_roc_bombs | gun | Free |  | 1 | 700 | 33.34 |
| armored_train/0 | armored_train | 0 | train_gun | main |  | gun_car_front | 1 | 600 | 8 |
| armored_train/1 | armored_train | 1 | boss_rockets | rocket | Free | rocket_car | 1 | 200 | 2.44 |
| armored_train/2 | armored_train | 2 | boss_hmg | mg | Free |  | 1 | 15 | 0.0833 |
| armored_train/3 | armored_train | 3 | boss_flak | mg | Free | flak_car | 1 | 25 | 0.05 |
| armored_train/4 | armored_train | 4 | train_gun | main | Free | gun_car_rear | 1 | 600 | 8 |
| armored_train/5 | armored_train | 5 | boss_flak | mg | Free |  | 1 | 25 | 0.05 |
| bastion_mk0/0 | bastion_mk0 | 0 | p26_bastion_sec_b240 | main |  | mortar | 1 | 1100 | 60 |
| bastion_mk0/1 | bastion_mk0 | 1 | p26_bastion_direct_b100 | gun | Free | turret_fl | 2 | 240 | 8.6 |
| bastion_mk0/2 | bastion_mk0 | 2 | p26_bastion_direct_b100 | gun | Free | turret_fr | 2 | 240 | 8.6 |
| behemoth/0 | behemoth | 0 | p26_behemoth_main_be152 | main |  | main_gun | 2 | 600 | 8.98 |
| behemoth/1 | behemoth | 1 | p26_behemoth_tiny_be120 | gun | Free | gun_120 | 1 | 260 | 7.5 |
| behemoth/2 | behemoth | 2 | p26_behemoth_close_boss_flak | mg | Free | flak_r | 1 | 25 | 0.05 |
| behemoth/3 | behemoth | 3 | p26_behemoth_close_boss_flak | mg | Free | flak_l | 1 | 25 | 0.05 |

*15 / 223 dòng đầu: xem sheet 03_boss/Boss_vu_khi; in 10 / 22 cột; 8 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 03_boss/Boss_bo_phan — Boss: bộ phận (198 dòng, 29 cột)

| id | boss_id | thu_tu | use | armour | at_x_m | at_y_m | at_z_m | hp | id_goc |
|---|---|---|---|---|---|---|---|---|---|
| armored_train/flak_car | armored_train | 4 |  | 2 | 0 | -6.35 | 3.2 | 0.1 | flak_car |
| armored_train/gun_car_front | armored_train | 1 |  | 3 | 0 | -3.2 | 3.7 | 0.12 | gun_car_front |
| armored_train/gun_car_rear | armored_train | 2 |  | 3 | 0 | 2.0 | 3.0 | 0.12 | gun_car_rear |
| armored_train/locomotive | armored_train | 0 |  | 4 | 0 | 7.5 | 2.5 | 0.12 | locomotive |
| armored_train/mortar_car | armored_train | 5 |  | 2 | 0 | -12.5 | 2.6 | 0.1 | mortar_car |
| armored_train/rocket_car | armored_train | 3 |  | 2 | 0 | -8.3 | 3.0 | 0.1 | rocket_car |
| behemoth/aps | behemoth | 6 |  | 1 | 0 | 0.6 | 5.2 | 0.07 | aps |
| behemoth/flak_l | behemoth | 3 |  | 2 | -0.9 | -1.15 | 4.8 | 0.07 | flak_l |
| behemoth/flak_r | behemoth | 2 |  | 2 | 0.9 | -1.15 | 4.8 | 0.07 | flak_r |
| behemoth/gun_120 | behemoth | 1 |  | 3 | 0 | 3.45 | 2.8 | 0.07 | gun_120 |
| behemoth/main_gun | behemoth | 0 |  | 3 | 0 | 3.5 | 4.1 | 0.07 | main_gun |
| behemoth/missiles_l | behemoth | 5 |  | 2 | -2.6 | -2.5 | 2.3 | 0.07 | missiles_l |
| behemoth/missiles_r | behemoth | 4 |  | 2 | 2.6 | -2.5 | 2.3 | 0.07 | missiles_r |
| behemoth/rocket_pod | behemoth | 9 | rocket_pod |  | 0 | -3.8 | 4.4 |  | rocket_pod |
| behemoth/side_gun_l | behemoth | 7 | side_gun_120 |  | -3.4 | 1.0 | 2.6 |  | side_gun_l |

*15 / 198 dòng đầu: xem sheet 03_boss/Boss_bo_phan; in 10 / 29 cột; 8 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 03_boss/Boss_sieu_vu_khi — Siêu vũ khí (17 dòng, 18 cột)

| id | dung_boi | aim | cooldown_s | exposed_s | first | halt_s | hold | icon | late_cooldown_s |
|---|---|---|---|---|---|---|---|---|---|
| airship_carpet | command_airship | group | 50 |  |  |  |  | bomb |  |
| bastion_420_shell | fortress_bastion | group | 45 |  |  |  |  | mortar |  |
| behemoth_barrage | behemoth | group | 45 |  |  |  |  | artillery |  |
| bug_rod_rain | silver_bug | group | 45 |  | 5 |  |  | ballistic | 45 |
| carrier_heavy_bomb | drone_mothership | group | 45 | 1.3 |  | TRUE |  | bomb |  |
| daedalus_mass_drop | daedalus | group | 50 |  |  |  |  | reinforce |  |
| doomsday_missile | nuke_train | hq | 50 |  |  |  |  | ballistic |  |
| fortress_203_barrage | mobile_fortress | group | 50 |  |  |  |  | artillery |  |
| garuda_carpet | garuda | group | 50 |  |  |  |  | bomb |  |
| hyperion_sun_beam | hyperion | group | 50 |  |  |  |  | ballistic |  |
| ixion_crush_charge | ixion | group | 10 |  | 6 |  |  | barrage |  |
| kraken_air_raid | kraken | group | 50 |  |  |  |  | bomb |  |
| kronos_bucket_sweep | kronos | self | 45 |  |  |  |  | dune |  |
| leviathan_volley | leviathan | base | 50 |  |  |  | cruise | artillery |  |
| moloch_factory_dump | moloch | group | 50 |  |  |  |  | reinforce |  |
| monster_800_shell | monster | group | 50 |  |  |  |  | mortar |  |
| typhon_underwater_launch | typhon | base | 50 |  |  |  | cruise | missile |  |

*in 10 / 18 cột; 6 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 03_boss/Boss_ho_tong — Hộ tống boss (17 dòng, 9 cột)

| id | boss | marks | on | phase_drop | phase_halt_s | phase_refill |
|---|---|---|---|---|---|---|
| armored_train | armored_train |  |  |  | 6 |  |
| behemoth | behemoth |  |  |  |  |  |
| behemoth_inferno | behemoth_inferno |  |  |  |  |  |
| behemoth_tempest | behemoth_tempest |  |  |  |  | TRUE |
| command_airship | command_airship |  |  |  |  |  |
| drone_mothership | drone_mothership |  |  |  |  |  |
| earth_borer | earth_borer |  | surface | para |  |  |
| fortress_bastion | fortress_bastion |  |  |  |  |  |
| fortress_hive | fortress_hive |  |  |  |  |  |
| landing_hovercraft | landing_hovercraft |  |  |  |  |  |
| mega_gunship | mega_gunship |  |  |  |  |  |
| mobile_fortress | mobile_fortress |  |  |  |  |  |
| nuke_train | nuke_train |  |  |  |  |  |
| rail_supergun | rail_supergun |  |  |  |  |  |
| silver_bug | silver_bug | 0.6;0.25 |  |  |  |  |
| sky_fortress | sky_fortress |  |  |  |  |  |
| supreme_command | supreme_command | 0.6 |  |  |  |  |

Sheet: 03_boss/Boss_hang — Hạng boss (42 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so | gia_tri_chu | don_vi |
|---|---|---|---|---|---|
| main.airDamage | bossRanks | airDamage | 1.6 |  |  |
| main.bigAttackScale.cooldown | bossRanks | cooldown | 0.85 |  | s |
| main.bigAttackScale.damage | bossRanks | damage | 0.857 |  |  |
| main.bigAttackScale.warn | bossRanks | warn | 0 |  | s |
| main.damageScale | bossRanks | damageScale | 1.4 |  |  |
| main.fireRate | bossRanks | fireRate | 1.25 |  |  |
| main.intro | bossRanks | intro | 6 |  | s |
| main.music | bossRanks | music |  | boss |  |
| main.partsShare | bossRanks | partsShare | 0.35 |  |  |
| main.phases[0].at | bossRanks | at | 0.6 |  |  |
| main.phases[0].damage | bossRanks | damage | 1.1 |  |  |
| main.phases[0].transform | bossRanks | transform | 2.5 |  |  |
| main.phases[1].at | bossRanks | at | 0.25 |  |  |
| main.phases[1].damage | bossRanks | damage | 1.2 |  |  |
| main.phases[1].fireRate | bossRanks | fireRate | 1.25 |  |  |

*15 / 42 dòng đầu: xem sheet 03_boss/Boss_hang.*

#### Lời hướng dẫn trong game theo đơn vị (04_can_cu_thap/Thap; chuỗi guide.<id> của GuideText.cs)

- **Pháo PK 40 mm** (`aa_gun_tower`): Cách đánh: bốn phát ngòi cận đích mỗi giây, tầm 48 m, bắn cả máy bay lẫn xe nhẹ. · Mạnh / yếu: thắng trực thăng, drone và xe nhẹ; xe tăng gần như miễn nhiễm. · Mẹo: khẩu ở giữa, giữa cao xạ bắn nhanh và cao xạ hạng nặng.
- **Tháp PK** (`aa_turret`): Cách đánh: pháo đôi 30 mm cao xạ tới 42 m và tên lửa phòng không (44 m); cũng bắn mặt đất nhưng chẳng mấy tác dụng. · Mạnh / yếu: xé nát trực thăng và máy bay; lực lượng mặt đất phá nó dễ dàng. · Mẹo: dọn nó bằng xe tăng hoặc pháo binh trước khi máy bay ta bay vào.
- **Trận địa pháo** (`artillery_emplacement`): Cách đánh: lựu pháo nã vào mục tiêu mặt đất cách 25–90 m mỗi khi phe thủ nhìn thấy; không có gì tự vệ ở gần. · Mạnh / yếu: gây đau cho mọi thứ dừng lại trong tầm; không bắn được gần hơn 25 m, và khá mỏng manh. · Mẹo: dùng xe nhanh lao vào: trong vòng 25 m pháo của nó chịu thua. Diệt tai mắt của nó trước.
- **Ụ chống tăng** (`at_gun_emplacement`): Cách đánh: 5 giây một phát xuyên giáp, tầm 38 m, chỉ trong 45° hai bên phía trước; pháo xoay chậm. · Mạnh / yếu: chặn xe tăng lao thẳng tới; pháo binh và xe vòng sườn diệt được nó. · Mẹo: quay mặt nó về con đường thiết giáp địch đi.
- **Tháp ATGM** (`atgm_tower`): Cách đánh: bệ phóng Kornet đôi bắn tên lửa chống tăng theo cặp xa tới 50 m. · Mạnh / yếu: chặn xe tăng và giáp dày từ xa; APS và xe la-de phòng không bắn hạ được tên lửa của nó, pháo binh bắn xa hơn nó. · Mẹo: nã pháo từ ngoài 50 m, hoặc cho tăng có APS hay xe la-de phòng không đi cùng đợt tấn công.
- **Khí cầu radar** (`barrage_balloon`): Cách đánh: bom địch ném trong 40 m quanh nó tản mát thêm 50%; trực thăng địch tránh vùng; nó còn làm lộ máy bay trong 45 m, cả máy bay tàng hình. · Mạnh / yếu: phá các lượt ném bom vào căn cứ; bom dẫn đường không bị ảnh hưởng. · Mẹo: đặt trên những tháp cần giữ nhất.
- **Tường chắn đạn** (`blast_wall`): Cách đánh: không súng, không chặn đường; tháp trong 10 m sau nó nhận ít hơn 30% sát thương bắn thẳng. · Mạnh / yếu: giữ tháp tuyến đầu trước xe tăng; đạn cầu vồng và bom vẫn vượt qua. · Mẹo: đặt trước tháp mạnh nhất.
- **Hầm ngầm** (`bunker_shelter_tower`): Xe phe ta gần đó nhận ít hơn một nửa sát thương từ pháo, cối, bom, không kích.
- **C-RAM** (`c_ram`): Cách đánh: bắn hạ rốc-két, tên lửa, drone và khoảng một phần ba đạn pháo nhắm vào trong 35 m, hai quả đánh chặn cùng lúc; pháo nhiều nòng 20 mm chỉ bắn đạn bay tới, không bắn máy bay. · Mạnh / yếu: che căn cứ khỏi pháo binh, rốc-két và drone; không có gì đánh xe mặt đất. · Mẹo: đặt nơi pháo địch sẽ gây hại nhất, giữa các tháp của ta. Ở hạng 7, Vòm Sắt đổi súng nhiều nòng lấy tên lửa đánh chặn (60 m, sáu quả một lượt, không chặn đạn bắn thẳng); Centurion giữ vai trò che chắn tầm gần bắn nhanh.
- **Trạm CP** (`cp_relay`): Cách đánh: không có súng; +0,1 CP mỗi giây cho phe mình, trạm thứ hai +0,06, trạm thứ ba không thêm gì; bị bắn thì ngừng trả 5 giây. · Mạnh / yếu: thêm CP cho căn cứ yên ổn; chiếm một ô phòng thủ nhỏ, và quân địch tấn công căn cứ sẽ nhắm nó trước. · Mẹo: tối đa hai trạm mỗi căn cứ, không đặt ở tiền đồn; cân nhắc với tòa tháp mà nó thay chỗ.
- **Răng rồng** (`dragons_teeth`): Cách đánh: các hàng khối bê tông không xe nào đi qua được; không đánh gì và bị bắn sau cùng. · Mạnh / yếu: biến lối vào thành đường vòng dưới họng súng của ta; công binh phá nhanh gấp ba. · Mẹo: bịt lỗ hổng địch sẽ đi qua; nhánh rào thép gai thì làm chậm thay vì chặn.
- **Nhà chứa drone** (`drone_hangar`): Cách đánh: cứ 20 giây phóng hai drone FPV cảm tử vào địch xa tới 70 m, mạnh lên giáp và công trình. · Mạnh / yếu: bào mòn thứ gì đứng ngoài tầm các tháp khác; APS, la-de và máy gây nhiễu chặn được drone. · Mẹo: nhánh Lancet bắn tới 85 m và săn pháo binh; nhánh Bầy đàn phóng bốn chiếc một lần.
- **Lưới drone** (`drone_net_tower`): Drone bay qua bị hạ; xe đi qua bình thường.
- **Tháp EW** (`ew_tower`): Cách đánh: tên lửa điều khiển, drone và hỏa lực yểm trợ nhắm vào trong vòng 30 m quanh nó bị lệch; không có súng. · Mạnh / yếu: làm cùn tên lửa chống tăng, Lancet và các đòn không kích vào căn cứ; thứ gì chỉ cần lái tới bắn là hạ được nó. · Mẹo: đặt cạnh các tháp mà tên lửa địch hay nhắm; nhánh: máy gây nhiễu drone 45 m, hoặc máy đánh lừa radar tìm pháo.
- **Tháp pháo sáng** (`flare_searchlight_tower`): Mỗi 15 giây ban đêm, một quả pháo sáng trên đầu địch gần nhất.
- **Tháp pháo sáng** (`flare_tower`): Cách đánh: ban đêm và trong sương mù, 15 giây một quả pháo sáng trên địch gần nhất trong 40 m, làm lộ mọi thứ trong 30 m. · Mạnh / yếu: tìm quân đột kích đêm, cả tàng hình; ban ngày vô dụng. · Mẹo: đi cặp với đèn pha ở map đêm.
- **Tháp canh** (`guard_tower`): Cách đánh: súng máy nặng (30 m, bắn cả máy bay); tầm nhìn 60 m giúp soi quân ta cho pháo địch. · Mạnh / yếu: chặn trinh sát và xe nhẹ; là tháp yếu nhất, gục nhanh trước xe tăng và đạn nổ mạnh. · Mẹo: hạ nó sớm bằng xe tăng hoặc pháo binh để địch mất tai mắt.
- **Tháp pháo** (`gun_turret`): Cách đánh: pháo 120 mm xuyên giáp của tăng chủ lực đặt trên bệ cố định. · Mạnh / yếu: thắng xe tăng và xe nhẹ lọt vào tầm 32 m; bị xe diệt tăng và pháo binh bắn xa hơn. · Mẹo: đứng ngoài 32 m, để xe diệt tăng (40 m) hoặc pháo binh phá nó.
- **Cao xạ nặng** (`heavy_flak_tower`): Cách đánh: 2 giây một phát lớn, nổ trên không rộng 6 m, tầm 70 m; hạ nòng bắn xe tăng trong 50 m. · Mạnh / yếu: bẻ gãy oanh tạc cơ và tốp máy bay dày; quá chậm với tiêm kích lẻ và drone. · Mẹo: đặt cạnh pháo phòng không bắn nhanh để lo trực thăng.
- **Pháo hạng nặng** (`heavy_turret`): Cách đánh: tháp pháo đôi 155 mm xoay chậm, bắn loạt đôi đạn nổ mạnh tới 50 m. · Mạnh / yếu: phá nát xe nhẹ, cụm quân và xe tăng trong góc bắn; là công trình nên ăn 1,5× sát thương nổ mạnh, sợ ít đạn súng máy. · Mẹo: pháo cối công thành, lựu pháo và pháo phản lực bắn xa hơn nó; tháp xoay chậm nên hãy đánh từ hai hướng.
- **Mồi nhử** (`inflatable_decoy`): Cách đánh: trông như tháp pháo; địch bắn vào nó cho tới khi trinh sát, radar, drone hoặc UAV quét lật tẩy. · Mạnh / yếu: làm địch phí đạn pháo và tên lửa; gần như không có máu. · Mẹo: đặt nơi loạt pháo đầu tiên sẽ rơi.
- **Trạm laser** (`laser_ad_station`): Cách đánh: laser chỉ bắn drone, tầm 40 m, cùng bộ đánh chặn rốc-két và đạn cối; khói làm tia yếu 80%. · Mạnh / yếu: dập bầy drone và mưa rốc-két; vô dụng trước máy bay và xe tăng. · Mẹo: giữ khói của ta tránh xa nó.
- **Tổ vác vai** (`manpads_tower`): Tên lửa Stinger tầm ngắn, chỉ bắn máy bay và trực thăng.
- **Lô cốt** (`mg_bunker`): Cách đánh: súng máy nặng bắn nhanh (32 m, bắn cả máy bay). · Mạnh / yếu: quét sạch trinh sát và xe nhẹ; gần như không làm xước xe tăng. · Mẹo: đưa xe tăng vào, đừng dùng xe nhẹ; tăng phun lửa hoặc pháo binh phá nó rất nhanh.
- **Bãi mìn** (`minefield`): Cách đánh: tám quả mìn chống tăng trong vòng 5 m, rải lại mỗi 45 giây; bãi mìn không phải mục tiêu. · Mạnh / yếu: trừng phạt xe lao vào ồ ạt; trinh sát, công binh và UAV quét thấy mìn, công binh gỡ được. · Mẹo: đặt trên đường vào căn cứ, sau các họng súng buộc địch phải chậm lại.
- **Trạm PK tầm xa** (`missile_battery`): Cách đánh: radar nhìn xa 85 m, phóng tên lửa từng cặp vào máy bay cách tới 62 m; không có gì để đánh mặt đất. · Mạnh / yếu: bắn xa hơn gần như mọi máy bay; nhưng bất kỳ lực lượng mặt đất nào cũng áp sát và phá được nó. · Mẹo: dùng xe tăng hoặc pháo binh diệt nó trước; máy bay tránh xa cho tới khi nó bị hạ.
- **TL một lần** (`one_shot_atgm_tower`): Tám tên lửa Kornet chặn đợt tấn công lớn, rồi hết đạn.
- **Súng không giật** (`recoilless_gun_tower`): Yếu hơn ụ pháo chống tăng nhưng rẻ hơn.
- **Dàn rốc-két** (`rocket_turret`): Cách đánh: phóng loạt sáu rốc-két theo đường cầu vồng vào mục tiêu mặt đất cách 8–55 m, vượt qua tường và vật che (từ sân trong vào quân địch đã áp sát tường). · Mạnh / yếu: trừng phạt cụm xe nhẹ và pháo binh; xe tăng chịu rốc-két khá tốt, đạn nổ mạnh phá nó nhanh. · Mẹo: dàn quân khi tiến vào và dùng xe tăng lao tới: trong vòng 8 m nó không bắn được gì.
- **Đèn pha** (`searchlight`): Cách đánh: ban đêm và trong sương mù, phe ta thấy mọi thứ trong 35 m quanh nó; địch trong vùng bắn kém 20%. · Mạnh / yếu: biến trận đêm thành bất lợi cho kẻ tấn công; ban ngày vô dụng. · Mẹo: mang theo cho trận đêm và sương mù.
- **Máy phát khiên** (`shield_tower`): Cách đánh: không có súng; vòm khiên 25 m hấp thụ 3.000 sát thương từ đạn pháo, bom, đạn súng và tên lửa cho mọi thứ phe ta bên dưới, rồi vỡ; hồi lại 30 giây sau đòn cuối. · Mạnh / yếu: giữ các tháp quanh nó đứng vững qua trận pháo kích; vũ khí năng lượng xuyên qua, nhiều vòm không cộng dồn, và máy phát là mục tiêu đầu tiên của địch. · Mẹo: đặt giữa những tháp mạnh nhất; nhánh hạng 7 cho vòm nhỏ mà bền hơn, hoặc hồi lại nhanh hơn.
- **Tháp căn cứ** (`spawn_bastion`): Cách đánh: đứng yên; pháo nặng hai nòng bắn loạt đôi tới 40 m. · Mạnh / yếu: cực lì, giáp dày như xe tăng chứ không phải giáp công trình nên đạn xuyên giáp hiệu quả nhất; thắng xe nhẹ và xe tăng. · Mẹo: đừng đánh trực diện; dùng pháo binh, pháo nặng từ ngoài 40 m, hoặc máy bay để bào dần.
- **Siêu pháo** (`super_gun`): Cách đánh: theo đồng hồ đếm ngược ở đầu màn hình, nó bắn một quả đạn cực lớn vào chỗ quân tấn công đông nhất (vào trại nếu không ai ở ngoài), 4 giây sau khi vòng cảnh báo hiện ra. · Mạnh / yếu: một phát xóa sổ cả đoàn xe nhẹ; nó không có súng bắn gần. · Mẹo: tản quân khi đồng hồ sắp hết; phá được nó là nhiệm vụ phụ, thưởng CP ngay và xu cuối trận.
- **Hầm che quân** (`troop_shelter`): Cách đánh: xe ta trong 15 m nhận một nửa sát thương pháo, cối, bom và không kích; không che đạn bắn thẳng. · Mạnh / yếu: giữ quân phòng thủ sống qua trận pháo kích; vô dụng trước xe tăng. · Mẹo: kéo quân phòng thủ về quanh nó khi đạn pháo tới.

*34 / 76 đơn vị có lời hướng dẫn.*

#### Lời hướng dẫn trong game theo đơn vị (03_boss/Boss; chuỗi guide.<id> của GuideText.cs)

- **Argus** (`argus`): Cách đánh: khi nó còn, pháo binh địch tản mát chỉ khoảng một nửa. Cao xạ và radar. · Mạnh / yếu: chậm và to; chỉ phòng không và tiêm kích bắn tới. · Mẹo: phá radar là pháo binh địch lại bắn tản mát.
- **Juggernaut** (`armored_train`): Cách đánh: hai pháo nặng (42 m), hộp rốc-két, hai pháo cao xạ và súng máy; bị bắn thì núp trong khói, còn nửa máu thì tự vá 20% một lần. · Mạnh / yếu: pháo của nó diệt xe tăng và xe nhẹ gần đường ray; nó không thể rời đường ray. · Mẹo: bố trí xe diệt tăng và pháo binh dọc tuyến đường phía trước nó, cách đường ray hơn 45 m.
- **Bastion Mk.0** (`bastion_mk0`): Cách đánh: chiếc Bastion đầu tiên của Brandt: một khẩu cối hạng nặng và hai tháp pháo 40 mm trên xích, bò chậm về phía căn cứ ta. · Mạnh / yếu: mặt trước dày, chậm; hai tháp pháo là thứ phòng thủ gần duy nhất. · Mẹo: phá khẩu cối là nó hết nguy hiểm từ xa.
- **Behemoth** (`behemoth`): Cách đánh: pháo chính hai nòng (40 m), pháo 120 mm, pháo cao xạ, tên lửa bắn cả đất lẫn trời (45 m) và bệ Kornet đôi sau tháp chính; còn 70% máu gọi 2 tăng tinh nhuệ. · Mạnh / yếu: nghiền nát xe nhẹ và xe tăng; khắc tinh là xe diệt tăng, giáp dày khiến đạn súng máy vô dụng. · Mẹo: đánh từ ngoài 45 m; còn nửa máu nó nổi điên (bắn nhanh hơn), dưới 35% thỉnh thoảng bật khiên.
- **Inferno** (`behemoth_inferno`): Cách đánh: hai súng phun lửa lớn (20 m) đốt cháy mặt đất; hộp rốc-két nhiệt áp đánh tầm 10–46 m; còn 70% máu gọi 2 tăng tinh nhuệ. · Mạnh / yếu: thiêu chảy xe nhẹ và xe tăng tới gần; yếu trước máy bay vì chỉ có một khẩu pháo cao xạ. · Mẹo: giữ khoảng cách: xe diệt tăng và pháo binh bắn từ ngoài 46 m, trực thăng tấn công và cường kích đánh từ trên cao.
- **Behemoth Mk.0** (`behemoth_mk0`): Cách đánh: bản lắp đầu tiên của Behemoth, chậm hơn bản hoàn chỉnh: pháo chính, hai pháo sườn và một giàn rốc-két trên cùng thân xe. · Mạnh / yếu: mặt trước giáp cấp 3; không có pháo cao xạ và hệ thống bảo vệ chủ động, nên máy bay và tên lửa không gặp cản trở nào. · Mẹo: mang máy bay và tên lửa; phá pháo chính, khẩu mạnh nhất của nó.
- **Behemoth Mk.II** (`behemoth_mk2`): Cách đánh: bản nâng cấp của Varga sau khi Behemoth gục: pháo chính, hai cao xạ và hệ thống bảo vệ chủ động bắn hạ tên lửa. · Mạnh / yếu: mặt trước giáp cấp 4 dưới lớp băng; hông và sau mỏng hơn nhiều. · Mẹo: đánh vào hông; phá hệ thống bảo vệ trước khi dùng tên lửa.
- **Tempest** (`behemoth_tempest`): Cách đánh: pháo điện từ nạp năng lượng một giây (cuộn dây sáng lên) rồi xuyên thủng cả hàng tới 80 m; hai pháo điện từ bắn đất lẫn trời (55 m). · Mạnh / yếu: trừng phạt xe đi thành hàng dọc; ở gần, EMP (22 m) làm choáng xe mặt đất, và nó bật khiên khi bị thương. · Mẹo: dàn quân và áp sát từ nhiều hướng; khi cuộn dây sáng lên, hãy tránh khỏi đường ngắm của nó.
- **Caspian** (`caspian`): Cách đánh: lao dọc bờ khoảng 6 giây mỗi lượt rồi vòng ra xa khoảng 20 giây; là mục tiêu trên mặt nước. Mỗi lượt lao nó phóng một tên lửa chống hạm vào cụm quân lớn nhất (có đánh dấu trước); hai pháo 23 mm đôi và một AK-630 che chắn. · Mạnh / yếu: giáp mỏng; phá cụm động cơ ở mũi thì nó chậm lại. · Mẹo: để sẵn pháo bắn nhanh trên bờ đón lượt lao, và phòng không hoặc C-RAM cho tên lửa.
- **Cerberus** (`cerberus`): Cách đánh: tạm dùng thân Behemoth (pháo, cao xạ, ổ rốc-két). Pháo đầu bắn xe mặt đất, cao xạ giữa đuổi máy bay, ổ rốc-két sau phủ một vùng. · Mạnh / yếu: mỗi bộ phận là một vũ khí riêng; chậm. · Mẹo: phá cao xạ trước thì không kích thoải mái; phá pháo chính thì đoàn xe không làm hại xe tăng nữa.
- **Roc** (`command_airship`): Cách đánh: hai tháp pháo phòng không 57 mm, hai tháp 30 mm đôi dưới bụng, drone từ hai nhà chứa và thỉnh thoảng mỗi nhà chứa thả một UAV tấn công. Mỗi bộ phận có máu riêng: thân không nhận sát thương cho tới khi hai động cơ bị phá. · Mạnh / yếu: chỉ phòng không và tiêm kích với tới; phá nhà chứa thì ngừng thả drone, phá radar thì pháo phòng không của nó bắn lệch. · Mẹo: bắn động cơ trước để mở thân, rồi tới radar; mang pháo cao xạ và tên lửa phòng không, thêm tiêm kích để diệt UAV.
- **Daedalus** (`daedalus`): Cách đánh: khoảng 10 giây trên quỹ đạo (không bắn tới được), sau đó đổi tầng cao và thấp theo lịch cố định, không lên lại quỹ đạo. Ba cửa thả khoang thả liên tục khoang chở 1–2 xe (tối đa tám xe còn sống); khoang đang rơi bắn hạ được. Pha 3 nó dừng hẳn ở tầng thấp, mở toàn bộ khoang. Hai pháo 30 mm và hai pháo 57 mm bắn từ dưới bụng. · Mạnh / yếu: tự nó bắn yếu hơn Icarus; thân trên cấp 3, bụng 2. Tháp la-de phòng thủ chặn tên lửa bắn vào nó. · Mẹo: bắn hạ khoang đang rơi và phá cửa thả: mỗi cửa mất là thả chậm hơn, đòn đổ bộ lớn cũng hụt đi.
- **Matriarch** (`drone_mothership`): Cách đánh: pháo và bầy drone cảm tử từ ba khoang phóng (70 m) đánh mặt đất, pháo cao xạ chống máy bay; cứ 30 giây phóng ra 3 UAV tấn công. · Mạnh / yếu: nhấn chìm mặt đất bằng drone; chỉ phòng không và tiêm kích gây sát thương được, còn nửa máu thì bật khiên. · Mẹo: dồn pháo cao xạ và tên lửa phòng không bên dưới, tăng APS hoặc la-de chặn drone, tiêm kích dọn UAV tấn công.
- **Tartarus** (`earth_borer`): Cách đánh: chui xuống đất, khoan ngầm không bị nhắm tới dưới cụm xe mặt đất đông nhất của bạn, mặt đất nứt 2 giây rồi nó trồi lên gây rung chấn làm choáng mọi xe mặt đất trong 15 m. Mũi khoan và hai khẩu pháo kết liễu nốt. · Mạnh / yếu: cực nguy hiểm với cụm xe tăng dày; ngay sau khi trồi lên nó nhận thêm 50% sát thương trong 6 giây, và máy bay không bao giờ nằm dưới nó. · Mẹo: rời khỏi vết nứt ngay, rồi dồn hỏa lực vào nó lúc nó lộ thân.
- **Fenrir** (`fenrir`): Cách đánh: nhanh: lao vào, xả hai hộp rốc-két rồi rút; cao xạ đuổi trực thăng. · Mạnh / yếu: nhẹ hơn Jötunn nhiều; không giữ trận địa được. · Mẹo: đón nó lúc rút, đặt xe diệt tăng trên đường rút.
- **Bastion** (`fortress_bastion`): Cách đánh: khẩu cối hạng nặng bắn tầm 12–80 m, bốn tháp pháo tự động 40 mm (28 m) phủ mọi hướng, hai súng máy NSV giữ hai bên hông, còn nửa máu nó tự vá giáp một lần. · Mạnh / yếu: pháo tự động xé nát xe nhẹ tới gần; giáp dày chặn đạn súng máy, cối không bắn được trong vòng 12 m. · Mẹo: mang xe diệt tăng và pháo hạng nặng, để dành hỏa lực dồn cho sau lần tự vá duy nhất của nó.
- **Hive** (`fortress_hive`): Cách đánh: không có pháo lớn: hai giàn phóng bầy drone tới 70 m, dàn tên lửa (62 m) và pháo cao xạ giữ bầu trời, còn thả thêm UAV tấn công. · Mạnh / yếu: xé nát máy bay; drone của nó hại được xe tăng, nhưng xe tăng và pháo binh mới là thứ hạ được nó. · Mẹo: để máy bay ở nhà; mang tăng APS hoặc xe la-de phòng không chặn drone, rồi dùng xe tăng và pháo binh bào dần.
- **Garuda** (`garuda`): Cách đánh: tạm dùng thân khí cầu chỉ huy (tháp súng và drone). Tháp phòng thủ và tên lửa đuổi máy bay; cứ 70 giây nó rải thảm 20 quả bom. · Mạnh / yếu: mục tiêu rộng, nhiều súng; chỉ phòng không tầng thấp mới trúng tốt. · Mẹo: dàn quân ra và để ý dải dài; phá khoang bom để chặn thảm bom.
- **Hydra** (`hydra`): Cách đánh: tạm dùng thân Typhon (pháo boong và cửa ống phóng, nhỏ và nhanh hơn). Nó lặn rồi nổi theo lịch ngắn, chỉ bắn khi nổi, và phóng tên lửa hành trình mỗi 16 giây. · Mạnh / yếu: lúc lặn không đánh tới được; thân mỏng. · Mẹo: chờ bong bóng; phá cửa ống phóng để chặn tên lửa.
- **Hyperion** (`hyperion`): Cách đánh: tạm dùng thân Silver Bug (chỉ ở tầng cao). Tháp la-de phòng thủ điểm che chắn, mỗi phút thả hai khoang đổ bộ, cứ 65 giây một tia mặt trời đốt dải 70 × 6 m trong 4 giây. · Mạnh / yếu: không bao giờ xuống tầng thấp, chỉ tên lửa tầm xa và pháo điện từ với tới. · Mẹo: giữ sẵn tên lửa tầm xa và pháo ray; rời dải ngay khi có cảnh báo.
- **Icarus Mk.0** (`icarus_mk0`): Cách đánh: không lên quỹ đạo: đổi tầng cao và thấp theo lịch cố định. Một tháp la-de, một khoang đổ bộ và một la-de phòng thủ điểm bắn hạ tên lửa. · Mạnh / yếu: ở tầng cao chỉ phòng không tầm xa và tiêm kích bắn tới; ở tầng thấp mọi vũ khí phòng không đều tới. · Mẹo: chờ lúc nó xuống thấp; phá la-de phòng thủ điểm trước khi dùng tên lửa.
- **Ixion** (`ixion`): Cách đánh: xe tải mỏ bọc thép (BelAZ-75710) chạy thẳng khoảng 7 m/s và xoay rất chậm. Tháp pháo 125 mm hàn trên thùng xoay 360°, nạp đạn nổ mạnh với đám đông (nổ lõi 5 m, rìa 10 m) và đạn xuyên với mục tiêu đơn lẻ, khoảng 780 mỗi 2 giây; cứ khoảng 10 giây nó lao theo đường thẳng báo trước 2 giây, khoảng 900 và choáng 1 giây, tháp pháo vẫn bắn trong lúc lao; hai súng máy 12,7 mm trên nóc; khi rẽ n… · Mạnh / yếu: giáp trước 4, hông 3, sau và nóc 2; bốn lốp sau giáp cấp 1 là điểm yếu; phá một lốp trước thì cú lao lệch và dừng, phá cả hai thì nó quay vòng rất chậm; phá tháp pháo trên thùng là mất pháo, phá ca-bin là súng máy ngừng bắn. · Mẹo: tránh khỏi đường lao, đánh vào hông và đuôi khi nó xoay, và tránh dải mìn.
- **Kraken** (`kraken`): Cách đánh: tạm dùng thân tàu Leviathan (pháo, ống phóng tên lửa và CIWS). Boong cất cánh phóng tiêm kích và drone, và cứ 75 giây nó gọi một đợt không kích. · Mạnh / yếu: thân tàu dài và dày nhất mặt nước; boong thang máy mỏng (giáp 2). · Mẹo: phá boong cất cánh là máy bay hết xuất kích; trong 4 giây cảnh báo hãy ra khỏi dải đỏ dài.
- **Kronos** (`kronos`): Cách đánh: chạy rất chậm theo đường cố định về căn cứ ta; bánh gầu nghiền mọi thứ phía trước (900 mỗi giây trong 6 m), cả tường lẫn tháp (gấp ba). Tới được HQ là thua nhiệm vụ. Hai tháp 30 mm, hai tháp pháo 57 mm tự động và một giàn rốc-két che chắn. Pha 2 nó đi nhanh hơn; pha 3 bánh gầu quay nhanh và hất đá vụn ra xung quanh. · Mạnh / yếu: bánh gầu giáp cấp 4, thân 3, cụm xích 2. Mỗi cụm xích bị phá là nó chậm lại. · Mẹo: phá cụm xích để câu giờ, phá cần gầu để chặn đòn quét; đừng xây tường chắn đường nó.
- **Charybdis** (`landing_hovercraft`): Cách đánh: chạy theo lộ trình dọc bờ biển; cứ 35 giây dừng lại, hạ cửa đổ bộ và thả 3–4 xe lên bờ, tối đa năm lần. Bốn pháo CIWS sáu nòng che chắn cả đất lẫn trời (hai khẩu bắn hạ tên lửa và rốc-két) và hai dàn rốc-két 140 mm bắn phá bờ. · Mạnh / yếu: mỗi lần đổ bộ là địch thêm quân; nó to và xoay chậm, đánh trúng nó trên đường tới là cắt bớt số lần đổ bộ. · Mẹo: đón đầu nó trước lần đổ bộ đầu tiên bằng xe diệt tăng và pháo binh, và giữ lực lượng dự bị cho số quân đã lên bờ.
- **Leviathan** (`leviathan`): Cách đánh: ba tháp pháo ba nòng 406 mm bắn loạt vào bờ, mỗi tháp một nòng, có cảnh báo trước và quét dần dọc bờ, và bắn cả chín nòng theo dải qua căn cứ khi tung siêu vũ khí; hai tháp ba nòng 155 mm tự bắn, tám bệ 25 mm và một bệ tên lửa phòng không tầm trung bắn máy bay; tên lửa hành trình đánh vào cụm quân và căn cứ; CIWS bắn hạ tên lửa, rốc-két và drone (không chặn đạn pháo, đạn súng hay Năng… · Mạnh / yếu: hông tàu giáp cấp 4, boong chỉ cấp 2: pháo binh, bom, pháo phản lực và đòn đánh nóc đánh vào boong; pháo xe tăng chỉ với tới khi nó áp sát, đứng ở đầu cầu tàu. · Mẹo: giữ ngọn hải đăng và trận địa pháo bờ biển; mang pháo binh và máy bay; phá CIWS (hoặc tuần dương hạm và tàu hộ vệ) trước khi dùng tên lửa, phá một tháp pháo chính khi loạt bắn mạn được đánh dấu, và phá buồng máy trước khi nó bỏ chạy.
- **Locust** (`locust`): Cách đánh: khoang drone thả drone liên tục; cao xạ trên lưng. · Mạnh / yếu: thân rất mỏng (giáp cấp 1): phòng không hạ nó nhanh. · Mẹo: phá khoang drone là nó hết đòn.
- **Harpy** (`mega_gunship`): Cách đánh: hai giàn rốc-két, hai pháo 30 mm, một súng máy nhiều nòng và mỗi bên cửa một súng máy 12,7 mm; thả mồi nhiệt liên tục, hộ tống là 2 trực thăng tấn công và 1 trực thăng trinh sát vũ trang đánh dấu mục tiêu, 50% thì nổi điên. · Mạnh / yếu: pháo xe tăng và pháo binh không chạm được nó: chỉ phòng không và tiêm kích gây sát thương. · Mẹo: dồn pháo cao xạ (xe phòng không, Tunguska) vì đạn pháo không bị mồi nhiệt lừa, thêm tiêm kích để diệt trực thăng hộ tống.
- **Jötunn** (`mobile_fortress`): Cách đánh: hai lựu pháo 203 mm (60 m), hộp rốc-két, pháo cao xạ, tháp 30 mm đôi chống drone và tên lửa; EMP làm choáng xe mặt đất trong 22 m; hộ tống là 2 tăng nặng và 1 xe công binh sửa cho nó, còn nửa máu thêm 1 xe công binh. · Mạnh / yếu: xé nát xe nhẹ và xe tăng dồn quanh nó; xe diệt tăng và pháo hạng nặng bào dần được nó. · Mẹo: đánh từ ngoài 22 m để né EMP, và coi chừng dưới 40% máu nó bắn nhanh gấp đôi.
- **Moloch** (`moloch`): Cách đánh: bò chậm theo đường của nhiệm vụ; hai cửa xưởng cứ 20 giây thả 1–2 xe (xe tăng nhẹ và xe bộ binh, từ pha 2 thêm tăng chủ lực), mỗi phút thêm một xe mỗi lượt, tối đa sáu xe còn sống. Bốn tháp pháo 120 mm, cao xạ và hai ZU-23 trên nóc che chắn. · Mạnh / yếu: giáp trước cấp 4, hông 3, sau 2: cửa xưởng ở phía sau, giáp mỏng cũng ở đó. Phá cụm xích thì nó chậm lại. · Mẹo: vòng ra sau, phá cả hai cửa trước: nó ngừng sinh xe, siêu vũ khí chỉ còn loạt pháo.
- **Monster** (`monster`): Cách đánh: tạm dùng thân Bastion (tháp pháo và khẩu cối, to hơn). Nó bò rất chậm, cứ 80 giây nòng 800 mm nâng lên bắn một quả 4.000 sát thương, nổ lan 20 m. · Mạnh / yếu: giáp và máu khổng lồ, nhưng chậm hơn mọi boss. · Mẹo: ra khỏi vòng đỏ trong 6 giây nó hiện; phá khẩu cối (nòng dài) là mất đòn này.
- **Morrigan** (`morrigan`): Cách đánh: nhanh hơn mọi tiêm kích của ta và tàng hình: chỉ bị phát hiện ở cự ly gần, hoặc trong chốc lát sau khi khai hỏa. Tên lửa không đối không từ hai khoang săn máy bay của bạn; bom dẫn đường săn xe phòng không. · Mạnh / yếu: rất nhanh và khó thấy; giáp mỏng, các khoang và động cơ phá được. · Mẹo: giữ ra-đa và phòng không gần máy bay để thấy được nó; bắn ngay lúc nó khai hỏa; phá các khoang tên lửa để chặn tên lửa của nó.
- **Nemesis** (`nuke_train`): Cách đánh: pháo nặng hai nòng (40 m), toa pháo 152 mm và ba pháo cao xạ; bị bắn thì núp trong khói; phía sau có toa rốc-két và toa SAM tầm xa, xe bọc thép hộ tống chạy dọc đường ray. · Mạnh / yếu: pháo của nó phá nát mọi thứ gần đường ray; nó không rời được đường ray và không có tên lửa để đánh. · Mẹo: dùng pháo binh và xe diệt tăng đánh mạnh và sớm; phải chặn nó trước khi tới bãi phóng.
- **Nyx** (`nyx`): Cách đánh: tạm dùng thân Leviathan thu nhỏ. Pháo điện từ bắn mỗi 8 giây, hai CIWS chặn tên lửa và drone, rồi tới tên lửa chống hạm. Nó tàng hình: chỉ thấy ở gần hoặc ngay sau khi bắn. · Mạnh / yếu: khó thấy; mỏng so với kích cỡ. · Mẹo: giữ radar hoặc drone trên mặt nước để thấy nó; phá CIWS trước khi dùng tên lửa.
- **Gungnir** (`rail_supergun`): Cách đánh: cứ 25 giây một phát điện từ vào cụm xe mặt đất đông nhất của bạn, ở bất cứ đâu trên bản đồ: nó xuyên qua tối đa năm xe trên một đường thẳng (1.000 mỗi xe) rồi nổ ở xe cuối (2.000 trong lõi 12 m, còn 40% tới rìa 20 m); vòng đỏ báo điểm ngắm trước 3 giây. Tường, tháp pháo, tháp phòng không và trạm chỉ thị mục tiêu bảo vệ nền pháo; hai khẩu 40 mm che chắn. · Mạnh / yếu: trừng phạt đội quân dồn cục; không di chuyển được, và mất trạm chỉ thị thì đạn rơi lệch xa. · Mẹo: luôn di chuyển và tản ra khi thấy vòng đỏ; phá trạm chỉ thị trước, rồi cho xe tăng tiến vào sau pháo binh.
- **Scylla** (`scylla`): Cách đánh: nhanh hơn Leviathan, chạy tuyến gần bờ: pháo AK-130 130 mm đôi nã vào bờ, ống phóng bắn tên lửa chống hạm mỗi 15 giây, CIWS chặn tên lửa và drone. · Mạnh / yếu: đủ gần để pháo xe tăng ở đầu cầu tàu bắn tới. · Mẹo: giữ cầu tàu bằng xe tăng, phá CIWS trước khi dùng tên lửa.
- **Icarus** (`silver_bug`): Cách đánh: tháp la-de chính và hai pháo coilgun bắn xuống mặt đất ở cả tầng cao lẫn tầng thấp; khoang đổ bộ thả xe xuống; cứ 60 giây có 7 thanh vonfram rơi từ vệ tinh của nó (khi đã rơi xuống đất: 9 thanh mỗi 50 giây). · Tầng độ cao: mở màn ở quỹ đạo thấp, ngoài tầm bắn; sau đó lặp cố định tầng cao (chỉ PK tầm xa, trạm PK tầm xa và tiêm kích bắn tới) và tầng thấp (mọi vũ khí bắn được máy bay, cộng pháo điện từ); dưới 30% máu nó rơi xuống thành pháo đài mặt đất, bốn tháp pháo thường trên xác. · Mạnh / yếu: bụng nó (giáp cấp 2) lộ ra ở tầng thấp; hai tháp la-de phòng thủ điểm của nó bắn hạ bớt SAM và tên lửa của ta. · Mẹo: giữ phòng không tầm xa sẵn sàng cho các đợt tầng cao, dồn mọi vũ khí khác vào các đợt tầng thấp, bắn hạ khoang đổ bộ trước khi chúng chạm đất, và phá ăng-ten liên kết vệ tinh để hủy một đợt mưa thanh vonfram.
- **Spectre** (`sky_fortress`): Cách đánh: bay vòng quanh mục tiêu, pháo 105 mm, hai 40 mm và một 25 mm bắn từ bên trái (50–58 m), kèm Griffin; không bắn được máy bay. · Mạnh / yếu: hủy diệt quân mặt đất nằm dưới vòng bay; chỉ phòng không và tiêm kích với tới nó. · Mẹo: xây cao xạ và tên lửa phòng không sớm, thêm tiêm kích vì pháo của nó không bắn được máy bay; bay kèm là 2 tiêm kích và 1 UAV đánh dấu quân ta (hạ UAV thì pháo của nó bắn lệch hơn), còn nửa máu thêm 2 tiêm kích.
- **Stymphalos** (`stymphalos`): Cách đánh: tạm là một thân với khoang drone và cao xạ của tàu mẹ, nhanh. Nó bắn tên lửa nhỏ và thả drone liên tục. · Mạnh / yếu: rất nhanh; giáp mỏng, phòng không hạ nó nhanh. · Mẹo: phá khoang drone và cao xạ; phòng không diện rộng và đạn nổ trên không là tốt nhất.
- **Atlas** (`supreme_command`): Cách đánh: chỉ có hai súng máy nhẹ; mọi quân địch trong 40 m quanh nó tăng 20% sát thương và 20% tốc độ bắn. Có cận vệ tinh nhuệ đi kèm, còn 60% máu thì gọi thêm. · Mạnh / yếu: quân địch gần nó nguy hiểm hơn nhiều; bản thân nó gần như không đánh lại được và không chạy thoát được thứ gì. · Mẹo: kéo trận đánh ra xa nó, hoặc đánh nó từ xa bằng pháo binh và máy bay; hạ nó là cả đạo quân yếu đi ngay.
- **Typhon** (`typhon`): Cách đánh: lặn (không bắn tới được) và nổi (mục tiêu trên mặt nước) theo lịch từng pha, mỗi lần nổi ở một chỗ khác; bong bóng báo trước chỗ nổi. Khi nổi nó phóng tên lửa hành trình tầm ngắn mỗi 12 giây và tự vệ bằng tên lửa phòng không. Pha 3 nổi hẳn, thêm pháo boong 100 mm. · Mạnh / yếu: thân giáp cấp 4, tháp chỉ huy và boong 2: pháo binh, bom và đòn đánh nóc đánh vào boong. · Mẹo: chờ sẵn pháo binh và máy bay chỗ bong bóng; phá cửa ống phóng lúc cảnh báo (cửa mở trên mặt nước) hoặc bắn hạ tên lửa.

*41 / 41 đơn vị có lời hướng dẫn.*

## Tham khảo ngoài đời và game

Trạng thái: Đã áp (lượt 10; chỉ dữ liệu trong repo, thiếu nguồn ghi NEED_SOURCE).

Nguồn dữ liệu: 03_boss/Boss_tham_chieu; 03_boss/Boss_so_sanh_that; 13_tham_chieu_nguon/Nguon_tham_chieu.

### Boss_tham_chieu

41 dòng. Độ tin cậy: da_kiem_chung 9, uoc_dinh 18, ban_dau_doan 8, NEED_SOURCE 6. Loại: NEED_SOURCE 6, doi_that 32, game 1, gia_tuong 2.

- `argus` (Argus · Khí cầu trinh sát): mẫu thật: JLENS (khí cầu radar neo); game: Red Alert 2; giống: biến thể của khí cầu chỉ huy, khí cầu radar neo; độ tin: uoc_dinh; nguồn: R_unit_refs, R_machine_brigade_can_bang, R_unit_sheet.
- `armored_train` (Juggernaut · Đoàn tàu bọc thép): mẫu thật: tàu bọc thép Liên Xô BP-35;B-38 152 mm;2B11 120 mm; giống: đầu máy diesel bọc thép kéo toa pháo; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, R_machine_brigade_can_bang, R_unit_sheet.
- `bastion_mk0` (Bastion Mk.0 · Pháo đài nguyên mẫu): mẫu thật: 2B8 240 mm;Bofors 40 mm; phim / truyện: Star Wars; giống: bản đầu, nhỏ của Bastion; độ tin: uoc_dinh; nguồn: R_unit_refs, R_machine_brigade_can_bang, R_unit_sheet.
- `behemoth` (Behemoth · Quái vật thép): mẫu thật: Object 279 (1959: bốn dải xích, thân dẹt);giáp composite, APS và cảm biến hiện đại;2A65 1…; game: Warhammer 40,000; giống: 'thiết giáp hạm trên cạn' bốn cụm xích; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_object_279, R_machine_brigade_can_bang, R_unit_sheet.
- `behemoth_inferno` (Inferno · Behemoth phun lửa): mẫu thật: TOS-1A;Object 279 (1959); game: Warhammer 40,000; giống: Behemoth phun lửa, thùng nhiên liệu đỏ; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, R_machine_brigade_can_bang, R_unit_sheet.
- `behemoth_mk0` (Behemoth Mk.0 · Behemoth nguyên mẫu): mẫu thật: Object 279 (1959);giáp composite, APS và cảm biến hiện đại; game: Warhammer 40,000; giống: Behemoth đời đầu, nhỏ hơn; độ tin: uoc_dinh; nguồn: R_unit_refs, R_machine_brigade_can_bang, R_unit_sheet.
- `behemoth_mk2` (Behemoth Mk.II · Behemoth nâng cấp): mẫu thật: Object 279 (1959);giáp composite, APS và cảm biến hiện đại; game: Warhammer 40,000; giống: Behemoth đời hai; độ tin: uoc_dinh; nguồn: R_unit_refs, R_machine_brigade_can_bang, R_unit_sheet.
- `behemoth_tempest` (Tempest · Behemoth pháo điện từ): mẫu thật: US Navy EMRG (pháo điện từ);Object 279 (1959); game: Warhammer 40,000; giống: Behemoth hai tháp pháo điện từ; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, R_machine_brigade_can_bang, R_unit_sheet.
- `caspian` (Caspian · Tàu bay sát mặt nước): mẫu thật: ekranoplan lớp Lun MD-160 ('Quái vật biển Caspi'); giống: Thủy phi cơ hiệu ứng mặt đất; độ tin: da_kiem_chung; nguồn: R_unit_refs, R_reference_real, W_wikipedia_lun_class_ekranoplan, R_machine_brigade_can_bang, R_mb_p20_bosses, R_unit_sheet.
- `command_airship` (Roc · Khí cầu chỉ huy): mẫu thật: Airlander 10;Lockheed P-791 (khí cầu lai hiện đại); game: Red Alert 2; giống: 'Sky Admiral', thiết giáp hạm bay hai túi khí; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_hybrid_air_vehicles_airlander_10, R_machine_brigade_can_bang, R_unit_sheet.
- `daedalus` (Daedalus · Tàu đổ bộ quỹ đạo): phim / truyện: Star Wars: Attack of the Clones; giống: Tàu đổ bộ tấn công của Aurel; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_reference_real, R_machine_brigade_can_bang, R_mb_p20_bosses, R_unit_sheet.
- `drone_mothership` (Matriarch · Tàu mẹ drone): mẫu thật: Airlander 10 (khí cầu mẹ hiện đại);drone FPV; game: Red Alert 2; giống: khí cầu bọc thép phóng drone; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_hybrid_air_vehicles_airlander_10, R_machine_brigade_can_bang, R_unit_sheet.
- `earth_borer` (Tartarus · Máy khoan): mẫu thật: 'Battle Mole' của Liên Xô;máy khoan hầm TBM;2A70 100 mm; giống: 'Earth Worm': máy khoan đất bọc thép ba đốt; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_reference_real, R_machine_brigade_can_bang, R_unit_sheet.
- `fenrir` (Fenrir · Xe tiên phong): mẫu thật: NASA Crawler-Transporter;Kharkovchanka (1959); phim / truyện: Star Wars; giống: biến thể của pháo đài di động; độ tin: uoc_dinh; nguồn: R_unit_refs, R_machine_brigade_can_bang, R_unit_sheet.
- `fortress_bastion` (Bastion · Pháo đài): mẫu thật: 2B8 240 mm;Bofors 40 mm;9M133 Kornet; phim / truyện: Star Wars; giống: pháo đài bánh xích bọc giáp tấm dày; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, R_machine_brigade_can_bang, R_unit_sheet.
- … 20 dòng có tham chiếu nữa: xem sheet 03_boss/Boss_tham_chieu.

Nguồn được dùng (tiêu đề như repo ghi; link khi repo có):

- `R_ixion`: spec dựng lại ixion (prompt 35) (độ tin 3)
- `R_machine_brigade_can_bang`: Rà soát cân bằng (Machine_Brigade_Can_bang.xlsx) (độ tin 3)
- `R_mb_p20_bosses`: script Blender mb_p20_bosses.py (docstring) (độ tin 3)
- `R_mb_p22_content`: script Blender mb_p22_content.py (docstring) (độ tin 3)
- `R_mb_redesign_20y`: script Blender mb_redesign_20y.py (docstring) (độ tin 3)
- `R_reference_real`: reference_real.json (kích thước thật, độ tin conf) (độ tin 3)
- `R_unit_refs`: unit_refs.json (tham chiếu ngoài đời / phim / game theo đơn vị) (độ tin 3)
- `R_unit_sheet`: unit_sheet.json (hình dạng, mô tả từ bảng cân bằng) (độ tin 3)
- `W_wikipedia_bagger_288`: Wikipedia 'Bagger 288' (độ tin 2)
- `W_wikipedia_belaz_75710`: Wikipedia 'BelAZ 75710' (độ tin 2)
- `W_wikipedia_boeing_ch_47_chinook`: Wikipedia 'Boeing CH-47 Chinook' (độ tin 2)
- `W_wikipedia_crawler_transporter`: Wikipedia 'Crawler-transporter' (độ tin 2)
- `W_wikipedia_hybrid_air_vehicles_airlander_10`: Wikipedia 'Hybrid Air Vehicles Airlander 10' (độ tin 2)
- `W_wikipedia_iowa_class_battleship`: Wikipedia 'Iowa-class battleship' (độ tin 2)
- `W_wikipedia_landing_craft_air_cushion`: Wikipedia 'Landing Craft Air Cushion' (độ tin 2)
- `W_wikipedia_lockheed_ac_130`: Wikipedia 'Lockheed AC-130' (độ tin 2)
- `W_wikipedia_lun_class_ekranoplan`: Wikipedia 'Lun-class ekranoplan' (độ tin 2)
- `W_wikipedia_northrop_b_2_spirit`: Wikipedia 'Northrop B-2 Spirit' (độ tin 2)
- `W_wikipedia_object_279`: Wikipedia 'Object 279' (độ tin 2)
- `W_wikipedia_sukhoi_su_57`: Wikipedia 'Sukhoi Su-57' (độ tin 2)
- `W_wikipedia_typhoon_class_submarine`: Wikipedia 'Typhoon-class submarine' (độ tin 2)

Sheet: 03_boss/Boss_so_sanh_that — Boss: so sánh với thật (122 dòng, 18 cột)

| id | entity_id | thong_so | don_vi | gia_tri_game | gia_tri_that | ty_le | khoang_min | khoang_max | co_chu_dich |
|---|---|---|---|---|---|---|---|---|---|
| argus/p26_roc_main_roc_bombs/nhip | argus | khe_mot_nong_mot_vien | s | 0.3 | 0.1 | 2.9999999999999996 | 0.6 | 2.0 | TRUE |
| armored_train/boss_flak/nhip | armored_train | khe_mot_nong_mot_vien | s | 0.262439018 | 0.10909090909090909 | 2.4056909983333337 | 0.6 | 2.0 | TRUE |
| armored_train/boss_hmg/nhip | armored_train | khe_mot_nong_mot_vien | s | 0.132467025 | 0.075 | 1.766227 | 0.6 | 2.0 | FALSE |
| armored_train/boss_rockets/nhip | armored_train | khe_mot_nong_mot_vien | s | 0.5 | 0.5 | 1.0 | 0.6 | 2.0 | FALSE |
| armored_train/train_gun/nhip | armored_train | khe_mot_nong_mot_vien | s | 8.0 | 11.428571428571429 | 0.7 | 0.6 | 2.0 | FALSE |
| bastion_mk0/p26_bastion_direct_b100/nhip | bastion_mk0 | khe_mot_nong_mot_vien | s | 8.599995918 | 12.244897959183675 | 0.7023329999699999 | 0.6 | 2.0 | FALSE |
| bastion_mk0/p26_bastion_sec_b240/nhip | bastion_mk0 | khe_mot_nong_mot_vien | s | 60.0 | 85.71428571428572 | 0.7 | 0.6 | 2.0 | FALSE |
| behemoth/p26_behemoth_close_boss_flak/nhip | behemoth | khe_mot_nong_mot_vien | s | 0.262439018 | 0.10909090909090909 | 2.4056909983333337 | 0.6 | 2.0 | TRUE |
| behemoth/p26_behemoth_direct_be120/nhip | behemoth | khe_mot_nong_mot_vien | s | 7.5 | 10.714285714285715 | 0.7 | 0.6 | 2.0 | FALSE |
| behemoth/p26_behemoth_main_be152/nhip | behemoth | khe_mot_nong_mot_vien | s | 8.979996429 | 10.714285714285715 | 0.8381330000399999 | 0.6 | 2.0 | FALSE |
| behemoth/p26_behemoth_sec_be_rockets/nhip | behemoth | khe_mot_nong_mot_vien | s | 0.5 | 0.5 | 1.0 | 0.6 | 2.0 | FALSE |
| behemoth/p26_behemoth_tiny_be120/nhip | behemoth | khe_mot_nong_mot_vien | s | 7.5 | 10.714285714285715 | 0.7 | 0.6 | 2.0 | FALSE |
| behemoth/p26_behemoth_tiny_boss_missiles/nhip | behemoth | khe_mot_nong_mot_vien | s | 20.0 | 20.0 | 1.0 | 0.6 | 2.0 | FALSE |
| behemoth/p26_behemoth_tiny_kornet_twin/nhip | behemoth | khe_mot_nong_mot_vien | s | 20.0 | 20.0 | 1.0 | 0.6 | 2.0 | FALSE |
| behemoth_inferno/boss_thermo/nhip | behemoth_inferno | khe_mot_nong_mot_vien | s | 0.3 | 0.25 | 1.2 | 0.6 | 2.0 | FALSE |

*15 / 122 dòng đầu: xem sheet 03_boss/Boss_so_sanh_that; in 10 / 18 cột; 5 cột khác (và raw_json, nguon): xem sheet.*

## Các sheet khác của file

Mọi sheet chưa in ở mục trên (sheet input_<tên> là bản chép từ file khác, không in lại).

### Boss_air

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_air.

Sheet: 03_boss/Boss_air — Boss: air (1 dòng, 7 cột)

| id | boss_id | thu_tu | phase | units |
|---|---|---|---|---|
| leviathan/0 | leviathan | 0 | 1 | attack_jet;attack_jet |

### Boss_attach

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_attach.

Sheet: 03_boss/Boss_attach — Boss: attach (2 dòng, 7 cột)

| id | boss_id | thu_tu | at | model |
|---|---|---|---|---|
| rail_supergun/0 | rail_supergun | 0 | 2.5;19.26;0.36 | rail_tractor |
| rail_supergun/1 | rail_supergun | 1 | -2.5;19.26;0.36 | rail_tractor |

### Boss_bien_the_chinh

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_bien_the_chinh.

Sheet: 03_boss/Boss_bien_the_chinh — Boss: chỉnh bộ phận của biến thể (73 dòng, 13 cột)

| id | boss_id | thu_tu | bo_phan | break_damage | hp | radio | stops |
|---|---|---|---|---|---|---|---|
| argus/engine_fl | argus | 1 | engine_fl | 0.3 | 0.1 |  |  |
| argus/engine_fr | argus | 2 | engine_fr | 0.3 | 0.1 |  |  |
| argus/radar | argus | 0 | radar | 0.3 | 0.14 | radio.part.radar | spotaura |
| bastion_mk0/mortar | bastion_mk0 | 0 | mortar |  | 0.15 |  |  |
| bastion_mk0/turret_fl | bastion_mk0 | 1 | turret_fl |  | 0.1 |  |  |
| bastion_mk0/turret_fr | bastion_mk0 | 2 | turret_fr |  | 0.1 |  |  |
| behemoth_mk0/main_gun | behemoth_mk0 | 0 | main_gun |  | 0.14 |  |  |
| behemoth_mk0/rocket_pod | behemoth_mk0 | 3 | rocket_pod |  | 0.12 |  |  |
| behemoth_mk0/side_gun_l | behemoth_mk0 | 1 | side_gun_l |  | 0.12 |  |  |
| behemoth_mk0/side_gun_r | behemoth_mk0 | 2 | side_gun_r |  | 0.12 |  |  |
| behemoth_mk2/aps | behemoth_mk2 | 3 | aps |  | 0.08 |  |  |
| behemoth_mk2/flak_l | behemoth_mk2 | 2 | flak_l |  | 0.09 |  |  |
| behemoth_mk2/flak_r | behemoth_mk2 | 1 | flak_r |  | 0.09 |  |  |
| behemoth_mk2/main_gun | behemoth_mk2 | 0 | main_gun |  | 0.13 |  |  |
| cerberus/flak_l | cerberus | 2 | flak_l |  | 0.11 |  |  |

*15 / 73 dòng đầu: xem sheet 03_boss/Boss_bien_the_chinh.*

### Boss_bo_phan_thu_vien

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_bo_phan_thu_vien.

Sheet: 03_boss/Boss_bo_phan_thu_vien — Thư viện bộ phận boss (19 dòng, 17 cột)

| id | weapon | aim | arc_deg_center_deg | arc_deg_half_deg | armour | fx | hp | kind | radio |
|---|---|---|---|---|---|---|---|---|---|
| casemate_155 | casemate_155 | Free | 0 | 60 | 4 |  | 0.09 | casemate |  |
| deck_gun_100 | naval_100 | Free |  |  | 2 |  | 0.08 | gun |  |
| drone_bay | mothership_drones | Free |  |  | 2 |  | 0.06 | bay | radio.part.bay |
| flak_35 | boss_flak | Free |  |  | 2 |  | 0.07 | flak |  |
| gun_30 | autocannon_30 | Free |  |  | 2 |  | 0.06 | gun |  |
| gun_40 | autocannon_40 | Free |  |  | 3 |  | 0.05 | turret |  |
| gun_152_car | gun_152_he | Free |  |  | 3 |  | 0.07 | maingun |  |
| howitzer_203 | boss_howitzer | Free |  |  | 3 |  | 0.08 | howitzer |  |
| naval_127 | naval_127 | Free |  |  | 3 |  | 0.06 | gun |  |
| pd_laser |  |  |  |  | 2 | energy | 0.08 | pdlaser |  |
| pod_105 | gunship_105 | Free |  |  | 2 |  | 0.07 | gun |  |
| pod_bay |  |  |  |  | 2 |  | 0.08 | podbay | radio.part.podbay |
| rocket_pod | boss_rockets | Free |  |  | 2 |  | 0.07 | rockets |  |
| sam_medium | sam_post | Free |  |  | 2 |  | 0.07 | sam |  |
| side_gun_120 | gun_120mm | Free |  |  | 3 |  | 0.07 | gun |  |
| tracks |  |  |  |  | 2 |  | 0.07 | tracks |  |
| turret_120 | gun_120mm | Free |  |  | 3 |  | 0.07 | gun |  |
| workshop_door |  |  |  |  | 2 |  | 0.07 | door | radio.part.door |
| zu23 | zu23 | Free |  |  | 1 |  | 0.07 | flak |  |

*in 10 / 17 cột; 5 cột khác (và raw_json, nguon): xem sheet.*

### Boss_guards

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_guards.

Sheet: 03_boss/Boss_guards — Boss: guards (9 dòng, 7 cột)

| id | boss_id | thu_tu | at | def |
|---|---|---|---|---|
| rail_supergun/0 | rail_supergun | 0 | -16;20 | gun_turret |
| rail_supergun/1 | rail_supergun | 1 | 16;20 | gun_turret |
| rail_supergun/2 | rail_supergun | 2 | -13;-2 | aa_turret |
| rail_supergun/3 | rail_supergun | 3 | 13;-2 | aa_turret |
| rail_supergun/4 | rail_supergun | 4 | -8;27 | mg_bunker |
| rail_supergun/5 | rail_supergun | 5 | 8;27 | mg_bunker |
| rail_supergun/6 | rail_supergun | 6 | -12;36 | dragons_teeth |
| rail_supergun/7 | rail_supergun | 7 | 0;38 | dragons_teeth |
| rail_supergun/8 | rail_supergun | 8 | 12;36 | dragons_teeth |

### Boss_ham_doi

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_ham_doi.

Sheet: 03_boss/Boss_ham_doi — Boss: hạm đội đi kèm (8 dòng, 9 cột)

| id | boss_id | thu_tu | unit | abeam | at | count |
|---|---|---|---|---|---|---|
| hydra/0 | hydra | 0 | missile_boat |  |  | 1 |
| leviathan/0 | leviathan | 0 | sea_cruiser | -17 | 22 | 1 |
| leviathan/1 | leviathan | 1 | sea_corvette | -16 | -27 | 1 |
| leviathan/2 | leviathan | 2 | missile_boat |  |  | 3 |
| nyx/0 | nyx | 0 | missile_boat |  |  | 1 |
| scylla/0 | scylla | 0 | missile_boat |  |  | 2 |
| typhon/0 | typhon | 0 | sea_corvette |  | 26 | 1 |
| typhon/1 | typhon | 1 | missile_boat |  |  | 2 |

### Boss_ho_tong_den

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_ho_tong_den.

Sheet: 03_boss/Boss_ho_tong_den — Hộ tống: đến cùng boss (62 dòng, 8 cột)

| id | boss_ho_tong_id | thu_tu | unit | role |
|---|---|---|---|---|
| armored_train/0 | armored_train | 0 | armored_car |  |
| armored_train/1 | armored_train | 1 | armored_car |  |
| armored_train/2 | armored_train | 2 | aa_vehicle | cover |
| armored_train/3 | armored_train | 3 | armored_car | spot |
| behemoth/0 | behemoth | 0 | main_battle_tank |  |
| behemoth/1 | behemoth | 1 | main_battle_tank |  |
| behemoth/2 | behemoth | 2 | heavy_tank |  |
| behemoth/3 | behemoth | 3 | aa_vehicle | cover |
| behemoth_inferno/0 | behemoth_inferno | 0 | flame_tank |  |
| behemoth_inferno/1 | behemoth_inferno | 1 | flame_tank |  |
| behemoth_inferno/2 | behemoth_inferno | 2 | aa_vehicle | cover |
| behemoth_inferno/3 | behemoth_inferno | 3 | smoke_carrier | smoke |
| behemoth_tempest/0 | behemoth_tempest | 0 | main_battle_tank |  |
| behemoth_tempest/1 | behemoth_tempest | 1 | ew_jammer | jam |
| behemoth_tempest/2 | behemoth_tempest | 2 | ew_jammer | jam |

*15 / 62 dòng đầu: xem sheet 03_boss/Boss_ho_tong_den.*

### Boss_ho_tong_luat

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_ho_tong_luat.

Sheet: 03_boss/Boss_ho_tong_luat — Hộ tống: luật (18 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so | gia_tri_chu | don_vi |
|---|---|---|---|---|---|
| bossRushCut | escortRules | bossRushCut | 2 |  |  |
| bossRushGuards | escortRules | bossRushGuards | 0.7 |  |  |
| bossRushMin | escortRules | bossRushMin | 4 |  |  |
| bounty | escortRules | bounty | 3 |  |  |
| cap.Easy | escortRules | Easy | 5 |  |  |
| cap.Hard | escortRules | Hard | 8 |  |  |
| cap.Heroic | escortRules | Heroic | 9 |  |  |
| cap.Iron | escortRules | Iron | 9 |  |  |
| cap.Normal | escortRules | Normal | 7 |  |  |
| cap.VeryHard | escortRules | VeryHard | 9 |  |  |
| dropWarn | escortRules | dropWarn | 3 |  | s |
| helperBounty | escortRules | helperBounty | 4 |  |  |
| leash | escortRules | leash | 28 |  | m |
| marks | escortRules | marks |  | 0.5 |  |
| repair | escortRules | repair | 0.003 |  |  |
| repairReach | escortRules | repairReach | 12 |  | m |
| spotBonus | escortRules | spotBonus | 0.15 |  |  |
| spotSpread | escortRules | spotSpread | 0.6 |  |  |

### Boss_ho_tong_mau

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_ho_tong_mau.

Sheet: 03_boss/Boss_ho_tong_mau — Hộ tống mẫu theo tướng (8 dòng, 3 cột)

| id |
|---|
| aurel |
| brandt |
| hung |
| kessler |
| orlov |
| quaden |
| sen |
| varga |

### Boss_ho_tong_mau_den

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_ho_tong_mau_den.

Sheet: 03_boss/Boss_ho_tong_mau_den — Hộ tống mẫu: đến (32 dòng, 7 cột)

| id | boss_ho_tong_mau_id | thu_tu | unit | role |
|---|---|---|---|---|
| aurel/0 | aurel | 0 | elite_heavy_tank |  |
| aurel/1 | aurel | 1 | railgun_truck |  |
| aurel/2 | aurel | 2 | sam_launcher | cover |
| aurel/3 | aurel | 3 | fighter_jet | cover |
| brandt/0 | brandt | 0 | tank_destroyer |  |
| brandt/1 | brandt | 1 | main_battle_tank |  |
| brandt/2 | brandt | 2 | heavy_aa | cover |
| brandt/3 | brandt | 3 | engineer_vehicle | repair |
| hung/0 | hung | 0 | heavy_tank |  |
| hung/1 | hung | 1 | bmpt |  |
| hung/2 | hung | 2 | sam_launcher | cover |
| hung/3 | hung | 3 | engineer_vehicle | repair |
| kessler/0 | kessler | 0 | wheeled_gun |  |
| kessler/1 | kessler | 1 | ifv |  |
| kessler/2 | kessler | 2 | main_battle_tank |  |
| kessler/3 | kessler | 3 | sam_launcher | cover |
| orlov/0 | orlov | 0 | mortar_carrier |  |
| orlov/1 | orlov | 1 | main_battle_tank |  |
| orlov/2 | orlov | 2 | sam_launcher | cover |
| orlov/3 | orlov | 3 | counter_battery_radar | spot |
| quaden/0 | quaden | 0 | attack_helicopter |  |
| quaden/1 | quaden | 1 | fighter_jet | cover |
| quaden/2 | quaden | 2 | fighter_jet | cover |
| quaden/3 | quaden | 3 | scout_heli | spot |
| sen/0 | sen | 0 | fpv_carrier |  |
| sen/1 | sen | 1 | strike_drone |  |
| sen/2 | sen | 2 | heavy_aa | cover |
| sen/3 | sen | 3 | ew_jammer | jam |
| varga/0 | varga | 0 | main_battle_tank |  |
| varga/1 | varga | 1 | main_battle_tank |  |
| varga/2 | varga | 2 | heavy_tank |  |
| varga/3 | varga | 3 | aa_vehicle | cover |

### Boss_ho_tong_mau_pha

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_ho_tong_mau_pha.

Sheet: 03_boss/Boss_ho_tong_mau_pha — Hộ tống mẫu: pha sau (14 dòng, 8 cột)

| id | boss_ho_tong_mau_id | thu_tu | unit | elite | role |
|---|---|---|---|---|---|
| brandt/0 | brandt | 0 | heavy_tank |  |  |
| brandt/1 | brandt | 1 | sam_launcher |  | cover |
| hung/0 | hung | 0 | heavy_tank | TRUE |  |
| hung/1 | hung | 1 | aa_vehicle |  | cover |
| kessler/0 | kessler | 0 | main_battle_tank |  |  |
| kessler/1 | kessler | 1 | smoke_carrier |  | smoke |
| orlov/0 | orlov | 0 | mlrs |  |  |
| orlov/1 | orlov | 1 | engineer_vehicle |  | repair |
| quaden/0 | quaden | 0 | attack_helicopter |  |  |
| quaden/1 | quaden | 1 | scout_heli |  | spot |
| sen/0 | sen | 0 | lancet_truck |  |  |
| sen/1 | sen | 1 | recon_drone |  | spot |
| varga/0 | varga | 0 | heavy_tank | TRUE |  |
| varga/1 | varga | 1 | engineer_vehicle |  | repair |

### Boss_ho_tong_mau_phases

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_ho_tong_mau_phases.

Sheet: 03_boss/Boss_ho_tong_mau_phases — Hộ tống mẫu theo tướng: phases (2 dòng, 5 cột)

| id | boss_ho_tong_mau_id | thu_tu |
|---|---|---|
| aurel/0 | aurel | 0 |
| aurel/1 | aurel | 1 |

### Boss_ho_tong_mau_phases_units

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_ho_tong_mau_phases_units.

Sheet: 03_boss/Boss_ho_tong_mau_phases_units — Hộ tống mẫu theo tướng: phases: units (4 dòng, 7 cột)

| id | boss_ho_tong_mau_phases_id | thu_tu | role | unit |
|---|---|---|---|---|
| aurel/0/0 | aurel/0 | 0 |  | bmpt |
| aurel/0/1 | aurel/0 | 1 | jam | ew_jammer |
| aurel/1/0 | aurel/1 | 0 |  | elite_attack_helicopter |
| aurel/1/1 | aurel/1 | 1 | repair | engineer_vehicle |

### Boss_ho_tong_pha

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_ho_tong_pha.

Sheet: 03_boss/Boss_ho_tong_pha — Hộ tống: gọi ở pha sau (8 dòng, 7 cột)

| id | boss_ho_tong_id | thu_tu | unit | role |
|---|---|---|---|---|
| armored_train/0 | armored_train | 0 | light_tank |  |
| armored_train/1 | armored_train | 1 | light_tank |  |
| armored_train/2 | armored_train | 2 | engineer_vehicle | repair |
| behemoth_tempest/0 | behemoth_tempest | 0 | ew_jammer | jam |
| behemoth_tempest/1 | behemoth_tempest | 1 | ew_jammer | jam |
| earth_borer/0 | earth_borer | 0 | ifv |  |
| earth_borer/1 | earth_borer | 1 | aa_vehicle | cover |
| earth_borer/2 | earth_borer | 2 | engineer_vehicle | repair |

### Boss_ho_tong_phase

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_ho_tong_phase.

Sheet: 03_boss/Boss_ho_tong_phase — Hộ tống boss: phase (28 dòng, 8 cột)

| id | boss_ho_tong_id | thu_tu | elite | role | unit |
|---|---|---|---|---|---|
| behemoth/0 | behemoth | 0 | TRUE |  | heavy_tank |
| behemoth/1 | behemoth | 1 |  | repair | engineer_vehicle |
| behemoth_inferno/0 | behemoth_inferno | 0 |  |  | flame_tank |
| behemoth_inferno/1 | behemoth_inferno | 1 |  |  | flame_tank |
| behemoth_inferno/2 | behemoth_inferno | 2 |  | repair | engineer_vehicle |
| command_airship/0 | command_airship | 0 |  |  | attack_helicopter |
| command_airship/1 | command_airship | 1 |  | spot | scout_heli |
| drone_mothership/0 | drone_mothership | 0 |  | spot | scout_heli |
| fortress_bastion/0 | fortress_bastion | 0 |  |  | heavy_tank |
| fortress_bastion/1 | fortress_bastion | 1 |  | cover | sam_launcher |
| fortress_bastion/2 | fortress_bastion | 2 |  | repair | engineer_vehicle |
| fortress_hive/0 | fortress_hive | 0 |  |  | fpv_carrier |
| fortress_hive/1 | fortress_hive | 1 |  |  | fpv_carrier |
| fortress_hive/2 | fortress_hive | 2 |  | spot | recon_drone |
| landing_hovercraft/0 | landing_hovercraft | 0 |  | spot | hover_gunboat |
| mega_gunship/0 | mega_gunship | 0 |  | spot | scout_heli |
| mobile_fortress/0 | mobile_fortress | 0 |  | repair | engineer_vehicle |
| nuke_train/0 | nuke_train | 0 |  |  | ifv |
| nuke_train/1 | nuke_train | 1 |  |  | ifv |
| nuke_train/2 | nuke_train | 2 |  | smoke | smoke_carrier |
| rail_supergun/0 | rail_supergun | 0 |  |  | main_battle_tank |
| rail_supergun/1 | rail_supergun | 1 |  |  | main_battle_tank |
| rail_supergun/2 | rail_supergun | 2 |  | repair | engineer_vehicle |
| sky_fortress/0 | sky_fortress | 0 |  | cover | fighter_jet |
| sky_fortress/1 | sky_fortress | 1 |  | cover | fighter_jet |
| supreme_command/0 | supreme_command | 0 | TRUE |  | main_battle_tank |
| supreme_command/1 | supreme_command | 1 | TRUE |  | main_battle_tank |
| supreme_command/2 | supreme_command | 2 |  | cover | aa_vehicle |

### Boss_ho_tong_phases

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_ho_tong_phases.

Sheet: 03_boss/Boss_ho_tong_phases — Hộ tống boss: phases (2 dòng, 5 cột)

| id | boss_ho_tong_id | thu_tu |
|---|---|---|
| silver_bug/0 | silver_bug | 0 |
| silver_bug/1 | silver_bug | 1 |

### Boss_ho_tong_phases_units

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_ho_tong_phases_units.

Sheet: 03_boss/Boss_ho_tong_phases_units — Hộ tống boss: phases: units (4 dòng, 7 cột)

| id | boss_ho_tong_phases_id | thu_tu | role | unit |
|---|---|---|---|---|
| silver_bug/0/0 | silver_bug/0 | 0 |  | elite_fpv_carrier |
| silver_bug/0/1 | silver_bug/0 | 1 | jam | ew_jammer |
| silver_bug/1/0 | silver_bug/1 | 0 |  | elite_attack_helicopter |
| silver_bug/1/1 | silver_bug/1 | 1 | repair | engineer_vehicle |

### Boss_khung

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_khung.

Sheet: 03_boss/Boss_khung — Khung boss (8 dòng, 25 cột)

| id | defaults_altitude_m | defaults_burrow_damage | defaults_burrow_dive_s | defaults_burrow_exposed_s | defaults_burrow_exposed_taken | defaults_burrow_radius_m | defaults_burrow_sea | defaults_burrow_speed_m_s | defaults_burrow_stun_s |
|---|---|---|---|---|---|---|---|---|---|
| aircraft |  |  |  |  |  |  |  |  |  |
| hovercraft |  |  |  |  |  |  |  |  |  |
| ship |  |  |  |  |  |  |  |  |  |
| spacecraft | 22 |  |  |  |  |  |  |  |  |
| submarine |  | 0 | 2 | 0 | 1 | 0 | TRUE | 9 | 0 |
| tracked |  |  |  |  |  |  |  |  |  |
| train |  |  |  |  |  |  |  |  |  |
| wheeled |  |  |  |  |  |  |  |  |  |

*in 10 / 25 cột; 13 cột khác (và raw_json, nguon): xem sheet.*

### Boss_sieu_vu_khi_don

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_sieu_vu_khi_don.

Sheet: 03_boss/Boss_sieu_vu_khi_don — Siêu vũ khí: đòn (18 dòng, 34 cột)

| id | boss_sieu_vu_khi_id | thu_tu | weapon | area_m | at | axis | count | cut | damage |
|---|---|---|---|---|---|---|---|---|---|
| airship_carpet/0 | airship_carpet | 0 |  |  |  | heading | 16 |  | 400 |
| bastion_420_shell/0 | bastion_420_shell | 0 | boss_mortar |  |  |  | 1 |  | 2000 |
| behemoth_barrage/0 | behemoth_barrage | 0 |  | 14 |  |  | 6 |  | 600 |
| bug_rod_rain/0 | bug_rod_rain | 0 |  |  |  |  | 7 |  | 1800 |
| carrier_heavy_bomb/0 | carrier_heavy_bomb | 0 | bomber_payload |  |  |  | 1 |  | 1600 |
| daedalus_mass_drop/0 | daedalus_mass_drop | 0 |  | 12 |  |  | 8 | 0.5 | 600 |
| doomsday_missile/0 | doomsday_missile | 0 | ballistic_missile |  |  |  | 1 |  | 3500 |
| fortress_203_barrage/0 | fortress_203_barrage | 0 | boss_howitzer | 14 |  |  |  |  | 900 |
| garuda_carpet/0 | garuda_carpet | 0 |  |  |  | heading | 20 |  | 350 |
| hyperion_sun_beam/0 | hyperion_sun_beam | 0 |  |  |  | toward | 4 |  | 500 |
| ixion_crush_charge/0 | ixion_crush_charge | 0 |  |  |  |  |  | 0 | 900 |
| kraken_air_raid/0 | kraken_air_raid | 0 |  |  |  | heading | 12 |  | 400 |
| kronos_bucket_sweep/0 | kronos_bucket_sweep | 0 |  |  |  |  |  |  | 2500 |
| leviathan_volley/0 | leviathan_volley | 0 |  |  |  | toward |  |  | 950 |
| moloch_factory_dump/0 | moloch_factory_dump | 0 |  |  | 0;-16 |  |  |  |  |
| moloch_factory_dump/1 | moloch_factory_dump | 1 | gun_152_he | 12 |  |  | 8 |  | 350 |
| monster_800_shell/0 | monster_800_shell | 0 | boss_mortar |  |  |  | 1 |  | 4000 |
| typhon_underwater_launch/0 | typhon_underwater_launch | 0 | leviathan_cruise |  |  |  | 6 |  | 700 |

*in 10 / 34 cột; 22 cột khác (và raw_json, nguon): xem sheet.*

### Boss_sieu_vu_khi_luat

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_sieu_vu_khi_luat.

Sheet: 03_boss/Boss_sieu_vu_khi_luat — Siêu vũ khí: luật (34 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so | don_vi |
|---|---|---|---|---|
| aaHit | bigAttackRules | aaHit | 0.5 |  |
| difficulty.Easy.bossDamage | bigAttackRules | bossDamage | 0.8 |  |
| difficulty.Easy.bossHp | bigAttackRules | bossHp | 0.75 |  |
| difficulty.Easy.cooldown | bigAttackRules | cooldown | 1.2 | s |
| difficulty.Easy.damage | bigAttackRules | damage | 1 |  |
| difficulty.Easy.warn | bigAttackRules | warn | 1 | s |
| difficulty.Hard.bossDamage | bigAttackRules | bossDamage | 1.15 |  |
| difficulty.Hard.bossHp | bigAttackRules | bossHp | 1.25 |  |
| difficulty.Hard.cooldown | bigAttackRules | cooldown | 0.9 | s |
| difficulty.Hard.damage | bigAttackRules | damage | 1 |  |
| difficulty.Hard.warn | bigAttackRules | warn | 0 | s |
| difficulty.Heroic.bossDamage | bigAttackRules | bossDamage | 1.3 |  |
| difficulty.Heroic.bossHp | bigAttackRules | bossHp | 1.5 |  |
| difficulty.Heroic.cooldown | bigAttackRules | cooldown | 0.8 | s |
| difficulty.Heroic.damage | bigAttackRules | damage | 1 |  |
| difficulty.Heroic.warn | bigAttackRules | warn | 0 | s |
| difficulty.Iron.bossDamage | bigAttackRules | bossDamage | 1.3 |  |
| difficulty.Iron.bossHp | bigAttackRules | bossHp | 1.5 |  |
| difficulty.Iron.cooldown | bigAttackRules | cooldown | 0.8 | s |
| difficulty.Iron.damage | bigAttackRules | damage | 1 |  |
| difficulty.Iron.warn | bigAttackRules | warn | 0 | s |
| difficulty.Normal.bossDamage | bigAttackRules | bossDamage | 1 |  |
| difficulty.Normal.bossHp | bigAttackRules | bossHp | 1 |  |
| difficulty.Normal.cooldown | bigAttackRules | cooldown | 1 | s |
| difficulty.Normal.damage | bigAttackRules | damage | 1 |  |
| difficulty.Normal.warn | bigAttackRules | warn | 0 | s |
| difficulty.VeryHard.bossDamage | bigAttackRules | bossDamage | 1.3 |  |
| difficulty.VeryHard.bossHp | bigAttackRules | bossHp | 1.5 |  |
| difficulty.VeryHard.cooldown | bigAttackRules | cooldown | 0.8 | s |
| difficulty.VeryHard.damage | bigAttackRules | damage | 1 |  |
| difficulty.VeryHard.warn | bigAttackRules | warn | 0 | s |
| dodge | bigAttackRules | dodge | 3 |  |
| first | bigAttackRules | first | 30 |  |
| intercept | bigAttackRules | intercept | 150 |  |

### Boss_tiers_schedule

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_tiers_schedule.

Sheet: 03_boss/Boss_tiers_schedule — Boss: tiers_schedule (10 dòng, 5 cột)

| id | boss_id | thu_tu |
|---|---|---|
| daedalus/0 | daedalus | 0 |
| daedalus/1 | daedalus | 1 |
| daedalus/2 | daedalus | 2 |
| hyperion/0 | hyperion | 0 |
| hyperion/1 | hyperion | 1 |
| hyperion/2 | hyperion | 2 |
| icarus_mk0/0 | icarus_mk0 | 0 |
| icarus_mk0/1 | icarus_mk0 | 1 |
| silver_bug/0 | silver_bug | 0 |
| silver_bug/1 | silver_bug | 1 |

### Boss_tiers_schedule_steps

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_tiers_schedule_steps.

Sheet: 03_boss/Boss_tiers_schedule_steps — Boss: tiers_schedule: steps (16 dòng, 7 cột)

| id | boss_tiers_schedule_id | thu_tu | seconds_s | tier |
|---|---|---|---|---|
| daedalus/0/0 | daedalus/0 | 0 | 20 | high |
| daedalus/0/1 | daedalus/0 | 1 | 14 | low |
| daedalus/1/0 | daedalus/1 | 0 | 14 | high |
| daedalus/1/1 | daedalus/1 | 1 | 20 | low |
| daedalus/2/0 | daedalus/2 | 0 | 60 | low |
| hyperion/0/0 | hyperion/0 | 0 | 60 | high |
| hyperion/1/0 | hyperion/1 | 0 | 60 | high |
| hyperion/2/0 | hyperion/2 | 0 | 60 | high |
| icarus_mk0/0/0 | icarus_mk0/0 | 0 | 18 | high |
| icarus_mk0/0/1 | icarus_mk0/0 | 1 | 12 | low |
| icarus_mk0/1/0 | icarus_mk0/1 | 0 | 12 | high |
| icarus_mk0/1/1 | icarus_mk0/1 | 1 | 18 | low |
| silver_bug/0/0 | silver_bug/0 | 0 | 25 | high |
| silver_bug/0/1 | silver_bug/0 | 1 | 10 | low |
| silver_bug/1/0 | silver_bug/1 | 0 | 15 | high |
| silver_bug/1/1 | silver_bug/1 | 1 | 20 | low |
