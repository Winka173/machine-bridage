# 07_hinh_anh_am_thanh_model — Hình ảnh, âm thanh, model

Hiệu ứng, âm thanh, hậu kỳ hình ảnh, model và số đo model, tài sản, giấy phép.

Gói cân bằng Machine Brigade, commit 31e5cc2e, ngày 2026-10-10. Số liệu đầy đủ ở 07_hinh_anh_am_thanh_model.xlsx; file này chỉ nêu luật, giải thích, lý do thiết kế, tham khảo và bảng nhỏ (tối đa 20 dòng, bảng lớn: xem sheet).

## Hình ảnh

![Mô hình đạn: tên lửa chống tăng và phòng không vác vai.](images/07_hinh_anh_am_thanh_model_r6_munitions_1.png)

*Hình: Mô hình đạn: tên lửa chống tăng và phòng không vác vai. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

![Tên lửa không đối không, phòng không, không đối đất.](images/07_hinh_anh_am_thanh_model_r6_munitions_2.png)

*Hình: Tên lửa không đối không, phòng không, không đối đất. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

![Rocket.](images/07_hinh_anh_am_thanh_model_r6_munitions_3.png)

*Hình: Rocket. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

![Bom và drone.](images/07_hinh_anh_am_thanh_model_r6_munitions_4.png)

*Hình: Bom và drone. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

![Đạn pháo, đạn cối, đạn xuyên, đạn railgun.](images/07_hinh_anh_am_thanh_model_r6_munitions_5.png)

*Hình: Đạn pháo, đạn cối, đạn xuyên, đạn railgun. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

![Mô hình mới: Ka-52, Su-25, pháo công thành, Inferno, Tempest, Hive, Bastion, Spectre.](images/07_hinh_anh_am_thanh_model_r6_new_models.png)

*Hình: Mô hình mới: Ka-52, Su-25, pháo công thành, Inferno, Tempest, Hive, Bastion, Spectre. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

![Súng phun lửa làm lại: luồng nhiên liệu cong, cầu lửa cuộn, khói đen.](images/07_hinh_anh_am_thanh_model_r6_flame.png)

*Hình: Súng phun lửa làm lại: luồng nhiên liệu cong, cầu lửa cuộn, khói đen. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

![Railgun: nạp năng lượng, tia sáng lưu lại.](images/07_hinh_anh_am_thanh_model_r6_railgun.png)

*Hình: Railgun: nạp năng lượng, tia sáng lưu lại. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

![Boss chết: nổ nhiều đợt, lóe trắng, sóng xung kích.](images/07_hinh_anh_am_thanh_model_r6_boss_death.png)

*Hình: Boss chết: nổ nhiều đợt, lóe trắng, sóng xung kích. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

![Kiểm tra đầu nòng: mỗi chấm màu là nơi một vũ khí bắn ra.](images/07_hinh_anh_am_thanh_model_r6_muzzle_audit.png)

*Hình: Kiểm tra đầu nòng: mỗi chấm màu là nơi một vũ khí bắn ra. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

### Thư viện hình ảnh

Ảnh render từ mô hình 3D của game (cùng ảnh dùng cho thẻ), ảnh chụp trong trận, các bảng hiệu ứng và bản đồ nhiệt.

![Docs/doc-images/r6/supports.png](images/07_hinh_anh_am_thanh_model_r6_supports.png)

*Hình: Docs/doc-images/r6/supports.png. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

![Docs/doc-images/shots/battle1.png](images/07_hinh_anh_am_thanh_model_shots_battle1.png)

*Hình: Docs/doc-images/shots/battle1.png. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

![Docs/doc-images/shots/battle2.png](images/07_hinh_anh_am_thanh_model_shots_battle2.png)

*Hình: Docs/doc-images/shots/battle2.png. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

![Docs/doc-images/shots/boss.png](images/07_hinh_anh_am_thanh_model_shots_boss.png)

*Hình: Docs/doc-images/shots/boss.png. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

![Docs/doc-images/shots/defend.png](images/07_hinh_anh_am_thanh_model_shots_defend.png)

*Hình: Docs/doc-images/shots/defend.png. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

![Docs/doc-images/shots/edge.png](images/07_hinh_anh_am_thanh_model_shots_edge.png)

*Hình: Docs/doc-images/shots/edge.png. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

![Docs/doc-images/shots/hd.png](images/07_hinh_anh_am_thanh_model_shots_hd.png)

*Hình: Docs/doc-images/shots/hd.png. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

![Docs/doc-images/shots/hunt.png](images/07_hinh_anh_am_thanh_model_shots_hunt.png)

*Hình: Docs/doc-images/shots/hunt.png. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

![Docs/doc-images/shots/siege.png](images/07_hinh_anh_am_thanh_model_shots_siege.png)

*Hình: Docs/doc-images/shots/siege.png. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

Bảng đầy đủ: xem sheet `Anh_the` (194 dòng, bulk.zip).

## Âm thanh

### Hiệu ứng, âm thanh theo bậc, xác vỡ, màn xem trước

Hình và tiếng chỉ là hiển thị, không đổi kết quả mô phỏng. Hiệu ứng bậc được **vẽ lại** và chồng lên vụ nổ sẵn có của viên đạn (không vụ nổ nào nhỏ đi). Giới hạn chi tiết đầy đủ cùng lúc: T5 1, T4 3, T3 6; xa camera thì rút gọn (dưới 70 m đầy đủ, dưới 140 m 45%). Âm thanh tổng hợp bằng script (Tools/sfx/build_sfx.py, không dùng AI), mỗi phát ba lớp trộn sẵn: cơ cấu, tiếng nổ, đuôi vang. 32 kênh, từ 24 kênh bận thì tiếng mới dưới ưu tiên 60 chỉ chiếm kênh kém quan trọng nhất. Số liệu cảnh thử tải: Docs/balance/p34_stress_counts.json (cảnh `-mb-play -mb-lighthousebay -mb-p34stress`; FPS: NEED PROFILE).

### Bắn, nổ và tiếng theo bậc

| Bậc | Phát bắn | Vụ nổ | Camera | Tiếng |
|---|---|---|---|---|
| T0 | Chớp mảnh của vũ khí | Nổ nhỏ (công thức Small) | — | shot_t0: tiếng giòn 35 ms, đuôi 0,08 s; súng nhỏ thành cụm đấu súng |
| T1 | Khói mỏng | Nổ nhỏ, đạn nổ trên không giữ chùm mảnh | — | shot_t1; cụm đấu súng từ khẩu thứ ba trong 20 m |
| T2 | Chớp vừa, khói ngắn | Cầu lửa nhỏ nóng, bụi và đất | — | shot_t2, blast_he_t2; ưu tiên 25-30 |
| T3 | Chớp lớn cháy lâu, cầu lửa đầu nòng, khói dài, vòng bụi, thân xe giật lùi | Cầu lửa vừa, cột bụi 5 cuộn, hố sáng nhỏ | — | shot_t3, blast_he_t3; ưu tiên 40 gần |
| T4 | Chớp rất lớn, hai cầu lửa, khói cuộn, vòng áp suất, mặt đất sáng; tàu: vòng nước và bụi nước | Cầu lửa cuộn lớn, cột 8 cuộn, mảnh văng, hai váy bụi; sóng xung kích trên rìa | Rung 0,22 (chỉ trên màn hình, trong 90 m) | shot_t4, blast_he_t4, tiếng rền dưới; ưu tiên 50 gần |
| T5 | Chớp sáng cả cảnh, khói rất dài, vòng áp suất đôi, hai vòng nước | Cầu lửa rất lớn, cột 10 cuộn thành mũ nấm nhỏ, mảnh xa, ba váy bụi, hố sáng 12 s; vòng trên lõi rồi rìa | Rung 0,6 | shot_t5, blast_he_t5; ưu tiên 60 (giữ 8 kênh cuối cho cảnh báo và T5 / boss) |

### Xác vỡ theo lớp xe

Xác sống 30-45 s (boss 90 s), cháy 40% thời gian đó; tối đa khoảng 12 xác đầy đủ gần camera (Trung bình 9, Thấp 6), để lại vết cháy. Mảnh vỡ chỉ là hình: không có collider, không chặn đường hay tầm nhìn.

| Lớp | Cách vỡ |
|---|---|
| Xích (tăng; cả tàu hỏa) | Tháp pháo văng, thân cháy |
| Bánh lốp | Hai bánh văng xoáy, khung lật nghiêng hoặc ngửa trong 0,9 s |
| Xe tải | Hàng nổ dây chuyền 4-6 tiếng dọc thùng, thùng cháy |
| Pháo | Đạn trong xe nổ 6-9 tiếng, cột lửa 2-3,5 s, tháp văng một nửa số lần |
| Tiêm kích | Mất một cánh kéo lửa, xoáy ốc rơi |
| Trực thăng | Rotor đuôi văng, rotor chính bay mất, xoay ngày càng nhanh |
| Máy bay lớn | Mất cánh, động cơ cháy, rơi dài và nghiêng |
| Tàu | Nghiêng, gãy đôi (từ 24 m) và chìm; xuồng lật |
| Drone | Một tiếng nổ nhỏ, không còn gì |

### Màn xem trước theo môi trường

Xem bắn, chi tiết xe / boss / tháp: đơn vị đứng đúng chỗ của nó. Bắn thử dùng đúng hiệu ứng và tiếng theo bậc; mỗi viên nổ hiện vòng rìa và lõi đúng cỡ vùng sát thương.

| Môi trường | Cảnh | Đơn vị |
|---|---|---|
| Mặt đất | Đất theo biome của bản đồ đang chọn (mặc định ôn đới) | Xe mặt đất, boss mặt đất |
| Biển | Mặt biển có sóng, mục tiêu đứng trên bờ phía trước | Tàu, xuồng, boss biển |
| Mép nước | Nửa sau trên nước, nửa trước trên bờ | Xe lội nước, đệm khí |
| Đường ray | Đoạn ray (đá ballast, tà vẹt, hai ray, ụ chặn) | Tàu hỏa, Juggernaut, Nemesis, Gungnir |
| Trên không | Bay vòng / lơ lửng, đất ở phía dưới | Máy bay, trực thăng, boss bay |
| Ô căn cứ | Bệ bê tông, viền tối, dấu góc | Tháp |
| Bờ biển | Pháo bờ biển trên bệ ở bờ, một tàu ngoài biển làm mục tiêu | Khẩu đội bờ biển |

Sheet 07_hinh_anh_am_thanh_model/Am_thanh_loat — Âm thanh: loạt bắn nhanh (7 dòng, 7 cột)

| id | bank | co | nhip_phat_s | so_phat |
|---|---|---|---|---|
| burst_s0_10 | burst_s0_10 | S0 | 10 | 3 |
| burst_s0_16 | burst_s0_16 | S0 | 16 | 5 |
| burst_s0_55 | burst_s0_55 | S0 | 55 | 18 |
| burst_s1_10 | burst_s1_10 | S1 | 10 | 3 |
| burst_s1_22 | burst_s1_22 | S1 | 22 | 7 |
| burst_s1_35 | burst_s1_35 | S1 | 35 | 12 |
| burst_s1_55 | burst_s1_55 | S1 | 55 | 18 |

Sheet 07_hinh_anh_am_thanh_model/Am_thanh_mixer — Âm thanh: mixer (9 dòng, 5 cột)

| id | loai | gia_tri |
|---|---|---|
| am_luong.dialogue | am_luong_mac_dinh | 1 |
| am_luong.effects | am_luong_mac_dinh | 1 |
| am_luong.master | am_luong_mac_dinh | 0.8 |
| am_luong.music | am_luong_mac_dinh | 0.7 |
| nhom.Dialogue | nhom_kenh |  |
| nhom.Effects | nhom_kenh |  |
| nhom.Music | nhom_kenh |  |
| nhom.UI | nhom_kenh |  |
| nhom.Warnings | nhom_kenh |  |

Sheet 07_hinh_anh_am_thanh_model/Am_thanh_thu_vien — Âm thanh: thư viện (1 dòng, 8 cột)

| id | khoa | gia_tri_chu |
|---|---|---|
| note | note | Fix pass L7: the sound library (Tools/sfx/build_sfx.py); si… |

Sheet 07_hinh_anh_am_thanh_model/Am_thanh_mau — Âm thanh: bản ghi mẫu (3 dòng, 29 cột)

| id | tep | do_dai_s | kenh | tan_so_mau_hz | lufs_mmax_tinh | so_moc | events | played | cooldown |
|---|---|---|---|---|---|---|---|---|---|
| boss_battle | Docs/audio/samples/boss_battle.ogg | 48.0 | 2 | 44100 | -13.9 | 8 | 1288 | 972 | 261 |
| crowded_battle | Docs/audio/samples/crowded_battle.ogg | 43.0 | 2 | 44100 | -15.0 | 8 | 5930 | 1830 | 2802 |
| normal_battle | Docs/audio/samples/normal_battle.ogg | 43.0 | 2 | 44100 | -15.6 | 8 | 1150 | 739 | 251 |

*In 10 / 29 cột; 17 cột khác: xem sheet.*

Bảng đầy đủ: xem sheet `Am_thanh` (256 dòng), `Am_thanh_bank` (90 dòng).

## Hiệu ứng theo bậc và xác vỡ

Sheet 07_hinh_anh_am_thanh_model/VFX_bac — VFX theo bậc (6 dòng, 21 cột)

| id | bac | rung_camera_dong_thoi | ban_dust_ring | ban_flash | ban_flash_life | ban_light | ban_pressure | ban_puff_life | ban_puff_life_arg0 |
|---|---|---|---|---|---|---|---|---|---|
| T0 | 0 | XEM_VFX_ngan_sach | 0 | 0 | 0 | 0 | 0 | zero |  |
| T1 | 1 | XEM_VFX_ngan_sach | 0 | 0 | 0 | 0 | 0 |  | 1.2 |
| T2 | 2 | XEM_VFX_ngan_sach | 0 | 1.2 | 0.1 | 0 | 0 |  | 1.8 |
| T3 | 3 | XEM_VFX_ngan_sach | 8 | 2.4 | 0.16 | 9 | 0 |  | 3.5 |
| T4 | 4 | XEM_VFX_ngan_sach | 16 | 3.6 | 0.24 | 16 | 7 |  | 5 |
| T5 | 5 | XEM_VFX_ngan_sach | 26 | 5 | 0.34 | 28 | 12 |  | 7 |

*In 10 / 21 cột; 9 cột khác: xem sheet.*

Sheet 07_hinh_anh_am_thanh_model/VFX_chay_than_xe — VFX: lửa thân xe (3 dòng, 14 cột)

| id | bodies | embers | low_tongues | power | reach_m | size | smoke_alpha | smoke_shade | smoke_size |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 1 | 0.5 | 1 | 2.8 | 4.5 | 1 | 0.6 | 0.34 | 1 |
| 1 | 1 | 1.1 | 1 | 4 | 6 | 1.2 | 0.74 | 0.16 | 1.15 |
| 2 | 2 | 1.8 | 2 | 5.2 | 7.5 | 1.45 | 0.8 | 0.06 | 1.35 |

*In 10 / 14 cột; 2 cột khác: xem sheet.*

Sheet 07_hinh_anh_am_thanh_model/Xac_vo — Xác vỡ (3 dòng, 7 cột)

| id | tran_day_du | song_toi_thieu_s | song_toi_da_s | song_boss_s |
|---|---|---|---|---|
| High | 12 | 30 | 45 | 90 |
| Low | 6 | 20.1 | 30.15 | 60.3 |
| Medium | 9 | 30 | 45 | 90 |

Bảng đầy đủ: xem sheet `VFX_vu_khi` (77 dòng), `Hau_ky_hinh_anh` (52 dòng).

## Model

### quy trình dựng model và đợt 1

Quy trình: **STEP0_AUDIT** kiểm kê mọi model và thẻ; **BASELINE** chạy bộ kiểm tra GLB (`Tools/assets/glb_check.py`: tỉ lệ so với `modelSize`, tam giác diện tích 0, màu đỉnh COLOR_0, nút bộ phận boss) và ghi mốc; **EXPERIMENT_1** thử bộ dựng V2 trên bốn model (xe tăng chủ lực, máy bay tiêm kích, silver_bug, trực thăng tấn công) và được chủ dự án duyệt; **BUDGETS** đặt trần số tam giác, renderer và bộ phận động theo loại; **art-bible** ghi luật tạo hình, bảng màu và công thức V2. Mỗi model một commit: dựng lại, kiểm tĩnh, render thẻ, xem trước trong Unity, chấp nhận mốc mới kèm lý do. Không chạy test, mô phỏng hay đo hiệu năng cho đến khi chủ dự án cho phép.

**Đợt 1** (42 model có tên riêng; đợt 1a: 2, đợt 1b: 8, đợt 1c: 32): Ixion và Gungnir, tám boss lô D (Kraken, Monster, Garuda, Hyperion, Stymphalos, Nyx, Cerberus, Hydra) và 32 đơn vị lô B; mọi lớp màu sơn tạm đã bỏ, không số liệu nào đổi.

![bộ chi tiết kit35: 70 chi tiết dựng model (Tools/blender/mb_kit35.py; số đo ở 10_model_tai_san/Kit_chi_tiet)](images/07_hinh_anh_am_thanh_model_kit_catalog_kit35_catalog.png)

*Hình: bộ chi tiết kit35: 70 chi tiết dựng model (Tools/blender/mb_kit35.py; số đo ở 10_model_tai_san/Kit_chi_tiet). Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

Sheet 07_hinh_anh_am_thanh_model/Model_tieu_chuan — Model: tiêu chuẩn (14 dòng, 13 cột)

| id | lop | bac | moving_parts_muc | moving_parts_tran | renderers_muc | renderers_tran | triangles_muc | triangles_tran | vertices_muc |
|---|---|---|---|---|---|---|---|---|---|
| boss_l/normal | boss_l | normal | 41 | 52 | 240 | 299 | 56000 | 70000 | 72000 |
| boss_m/normal | boss_m | normal | 25 | 31 | 178 | 222 | 44000 | 55000 | 56000 |
| boss_s/normal | boss_s | normal | 22 | 28 | 130 | 162 | 36000 | 45000 | 43000 |
| ground/hd | ground | hd | 8 | 10 | 83 | 103 | 18800 | 23300 | 27300 |
| ground/normal | ground | normal | 8 | 10 | 61 | 76 | 7800 | 9700 | 10100 |
| helicopter/hd | helicopter | hd | 5 | 6 | 61 | 76 | 15900 | 20000 | 22500 |
| helicopter/normal | helicopter | normal | 5 | 6 | 45 | 56 | 6600 | 8300 | 8300 |
| jet/hd | jet | hd | 6 | 7 | 49 | 60 | 12300 | 15400 | 19200 |
| jet/normal | jet | normal | 6 | 7 | 36 | 44 | 5100 | 6400 | 7100 |
| munition/normal | munition | normal | 2 | 3 | 14 | 17 | 500 | 1600 | 600 |
| prop/normal | prop | normal | 2 | 3 | 46 | 58 | 6900 | 8600 | 9900 |
| scenery/normal | scenery | normal | 2 | 3 | 12 | 14 | 3700 | 4600 | 9700 |
| structure/normal | structure | normal | 2 | 3 | 39 | 48 | 7900 | 9900 | 9800 |
| tower/normal | tower | normal | 8 | 9 | 144 | 180 | 14700 | 18400 | 20100 |

*In 10 / 13 cột; 1 cột khác: xem sheet.*

Sheet 07_hinh_anh_am_thanh_model/Giay_phep_tai_san — Giấy phép tài sản (5 dòng, 7 cột)

| id | tep | tai_san | giay_phep | so_dong |
|---|---|---|---|---|
| OFL-Barlow | OFL-Barlow.txt | Barlow | SIL Open Font License | 75 |
| OFL-BarlowCondensed | OFL-BarlowCondensed.txt | BarlowCondensed | SIL Open Font License | 75 |
| OFL-BeVietnamPro | OFL-BeVietnamPro.txt | BeVietnamPro | SIL Open Font License | 75 |
| OFL-Inter | OFL-Inter.txt | Inter | SIL Open Font License | 75 |
| OFL-JetBrainsMono | OFL-JetBrainsMono.txt | JetBrainsMono | SIL Open Font License | 74 |

Bảng đầy đủ: xem sheet `Model` (473 dòng), `Model_kiem_chuan` (473 dòng), `Kich_thuoc_that` (84 dòng), `Kit_chi_tiet` (70 dòng), `Xem_truoc` (203 dòng).

### Model standard (fix pass 8)

Where this file and Docs/models/BUDGETS.md disagree, this file decides how a model is **scored**. L9 item 7 is
`python Tools/balance/fix_validate.py 7` (budget information only, the parts and LOD1 against the pass 8 scores); the

only warn (the owner's rule of 02/10).
Checked statically by `python Tools/models/scan_prep.py` (Docs/models/scan/static_scores.csv) and visually on the
sheets that `MachineBrigade.Editor.ModelScan.RenderBatch` draws (Docs/models/scan/README.md).

#### Triangle budgets

LOD0 = the normal GLB (every platform loads it; phones only load this one). The `_hd` twin (the PC High tiers) may
carry up to 2.4 x the class maximum (BUDGETS.md's median `_hd` / normal ratio). The scorer reports it but does not
grade on it.

**Owner rule (02/10): a model over its budget is kept.** Budgets are a guide, not a cap; the scorer reports

models are fine").

| class (scorer) | what | LOD0 triangles |
|---|---|---|
| light | wheeled and other light vehicles (trucks, cars, APCs on wheels) | 3,000-5,000 |
| heavy | tanks, tracked and heavy vehicles (tracked, or class Tank / Heavy) | 4,000-7,000 |
| jet, helicopter | aircraft and helicopters | 4,000-7,000 |
| air_other | drop pods, parachute loads | at most 7,000 |
| ship | ships (`naval`) | 8,000-15,000 |
| boss | bosses (every frame) | 10,000-20,000 |
| tower | towers (defs with `fort`, their branch `_a` / `_b` models) | 2,000-4,000 |
| structure, hq | other static structures; the HQs (`headquarters`, `command_hq`) | 2,000-6,000 |
| obstacle | walls, dragon's teeth, minefields (`wall`, `obstacle`, `passable`) | at most 6,000 |

- Below the minimum is a fault too (too little detail to read), not only above the maximum.
- **LOD1 ~50 %** of LOD0: the game builds it at run time (`ModelLibrary.Lod`, `MeshSimplifier`, half a pixel of

  error at the 128 px switch). ModelScan writes `triangles0` / `triangles1` per model; accepted band 35-65 %.
- **LOD2 ~20 %**: the impostor (`ImpostorAtlas`, below 24 px) takes this level for every vehicle. A model drawn large

  enough that its impostor is never used (bosses, ships) needs no mesh LOD2; if one is ever added, about 20 % of LOD0.

#### Minimum parts per class

A part is a named node. A role is met by a `Part_<role>` node **or** by the kit's merged-material node of that
part (the names in the table). Note: `Part_*` nodes are runtime parts (damage, boss parts): ModelLibrary keeps each as
a mesh of its own, so one draw and one shadow draw each. Do **not** add a `Part_*` node per wheel or per blade to pass
this list; "every road wheel", "every blade", "every barrel" are geometry rules, checked on the sheet (each wheel its
own disc with a hub, each blade its own blade). Roles marked (w) only apply when the def is armed; (t) only with a
turret (`turretTurnRate`).

| class | roles (accepted node names, start of the name) |
|---|---|
| tracked | hull (Hull, Body, Chassis); turret (t) (Turret, Casemate); mantlet (t) (Mantlet, Gun_mantlet, Elevation, Cradle); barrels (w) (Main_cannon, Barrel, Gun, Tubes, Launcher, Pod, Missiles, Mount_*); every road wheel (Wheels, Roadwheels, Bogies); drive sprocket (Sprockets); idler (Idlers); tracks with links / tread (Tracks, Track_links, Treads); side skirts (Skirts, Skirt_edge); hatches (Hatch, Hatches, Cupola); sights (Sight, Periscope, Optics, Sensor); roof MG (w) (MG, Mount_mg, Rws, Hmg); smoke dischargers (Smoke, Smoke_launchers, Smoke_brackets); stowage (Stowage, Tarp, Crates, Jerrycans, Bins, Racks, Straps, Ammo_boxes, Bags) |
| wheeled | every wheel (Wheels, Tyres); axles (Axles, Undercarriage, Suspension, Hubs); cab (Cab, Cabin, Hull, Body); glass (Glass, Windows, Windscreen, Lit_windows, Canopy, Visors); lights (Lamps, Lights, Headlights, Tail_lamps, Light_rims); stowage (as above); weapon (w) |
| jet | fuselage; cockpit glass (Canopy, Cockpit, Glass); wings with the reference's sweep and taper (Wing, Part_wing); horizontal and vertical tail (Tail, Fins, Tailplane, Stabilator, Rudder); intakes (Intake, Intake_lips, Inlet); exhausts (Nozzle, Exhaust); pylons (Pylons, Hardpoints, Racks); stores on them (Missiles, Bombs, Pods, Rockets, Drop_tanks); flare dispensers (Flares, Mount_flare) |
| helicopter | fuselage; glass (Canopy, Glass, Windows); rotor hub (Rotor_hub, Rotor_grips, Hub); every blade (Rotor_blades, Blades); tail rotor (Tail_rotor); landing gear (Undercarriage, Skids, Gear, Tyres); stub wings (Wing, Stub_wing, Pylons); weapons (Gun, Gun_turret, Missiles, Pods, Rockets, Launchers) |
| ship | hull with bow flare (Hull); superstructure tiers (Superstructure, Bridge, Deckhouse, Tier, Island, Funnel); radar mast (Mast, Radar, Antenna); every turret and barrel (Turret, Gun_house, Main_cannon, Barrel); CIWS (CIWS, Phalanx, AK630, Gatling, Mount_ciws); boats (Boat, RHIB, Lifeboat, Davit); deck details (Deck, Rails, Bollards, Hatches, Vents, Winch, Anchor) |
| tower, structure, hq | base (Base, Plinth, Footing, Emplacement, Pad, Foundation, Slab, Block, Race); sandbags / walls (Sandbags, Hesco, Wall, Parapet, Barriers, Blast_bags, Revetment, Berm, Coping); roof (Roof, Roof_deck, Canopy, Cupola, Tower_deck, Deck, Turret, Dome, Shelter); antennas (Antenna, Mast, Aerial, Radar, Dish, Flag_pole); faction detail differs (Accord: practical, field-built - sandbags, timber, nets; Hegemon: prefabricated - cast concrete, modular panels) - visual check |
| boss | body (Hull, Fuselage, Body, Chassis, Deck, Envelope, Gondola); weapons; by frame: running gear (ground: Tracks, Wheels, Bogies, Legs, Rail_wheels), lift (air: Rotor, Wing, Envelope, Propeller, Engine), superstructure (naval); and every `parts[].node` of its def present |
| obstacle | none (budget and look only) |

#### General rules

1. **Proportions within 10 %** of the real reference: width/length and height/length against
   `Docs/models/reference_dimensions.md` (data: `Tools/models/reference_real.json`). Absolute size is free (the game
   draws aircraft and ships smaller on purpose; the view fits the length to `modelSize`). Fictional designs
   (conf "inspiration") are not judged.
2. **No single-box turret or hull**: at least two stacked or angled volumes, sloped glacis / cheeks; large bevels on
   every big edge (the kit's chamfers), no 90-degree slab edge on a hull or turret read from 28 px per metre.
3. **Materials and detail colours separated**: hull paint, steel, rubber, glass, lamps, markings in their own
   materials (the kit's names), so the team colour and wear read.
4. **Mounts and muzzles**: a `Muzzle_<slot>` per barrel of every weapon (the weapon's `barrels`; a secondary on the
   main gun's slot shares its barrels); a `Mount_<slot>` per freely aimed (`aim: Free`) secondary; the main weapon on a
   `Turret` (or `Mount_<mainSlot>`) when the def turns a turret; `Mount_Flare` x 2 or more when the def has
   `flareCharges`; `Mount_APS` when it has `aps`. Bosses: as many `Muzzle_*` as `mountWeapons`, every part node.
5. **Readable silhouette at the normal camera distance**: the battle camera's default zoom (orthographic size 19 on
   a 1080 px screen = 28.4 px per metre, pitch 52). The ModelScan sheet shows exactly that; the type must be named from
   the left cell alone.

#### Grades

- **Kém** (poor): triangles over 1.5 x the class maximum or under half the minimum; 4 or more required parts missing;

  the main weapon's muzzle missing; proportions more than 25 % off a high-confidence reference; or the visual pass
  finds the silhouette unreadable / a box model.
- **Cần sửa** (needs fixing): any other fault above (over or under budget, 1-3 parts, a secondary muzzle or mount,

  Mount_Flare / Mount_APS, boss part node, proportions 10-25 %, LOD1 outside 35-65 %), or a visual fault.
- **Tốt** (good): nothing found, statically and on the sheet.
- Final grade = the lower of the static and the visual grade, with one exception: a "missing part" that the sheet

  shows modelled inside a merged node (an idler inside `Wheels`, a mantlet inside `Turret_body`) is cleared by the
visual pass, which says so in its reason (the static check only sees node names).
  scoring version loses; when the new one scores lower, restore the old GLB or rebuild it to pass.

#### How the scorer assigns a class

Own def = the def whose id is the model, else the first def drawing it. HQ ids -> hq; `boss` -> boss; `naval` -> ship;
`flying` -> jet (`fixedWing`), helicopter (has a `Rotor*` node) or air_other; static or speed 0 -> obstacle (`wall`,
`obstacle`, `passable` or a wall / teeth / minefield id), tower (`fort` or `branchOf`; the `_a` / `_b` files) or
structure; otherwise tracked (Tracks / Sprockets nodes), wheeled (Tyres / Wheels nodes) or ground.

#### Roof guns
Roof-mounted guns (pintle MGs, remote weapon stations, small roof turrets) must not look flat: build the raised mount
or pintle post, the cradle, the ammo box and the gun shield where the real one has them, so the gun stands clear of the
roof line at the battle camera's distance.
Kit (wave 1): `mb_kit35.pintle_mg(..., post=<metres>)` builds the post (base plate, gussets, column, collar), the
cradle and the big ammunition can; `post=0` (the default) is the pilot's low gun.

## Tham khảo ngoài đời và game

Thông số ngoài đời lấy từ nguồn trong repo (sheet Nguon_tham_chieu của 08_tham_chieu); chỗ chưa có nguồn ghi NEED_SOURCE, không điền từ trí nhớ.

### Hieu_ung_tham_chieu

58 dòng. Độ tin cậy: da_kiem_chung 0, uoc_dinh 0, ban_dau_doan 0, NEED_SOURCE 58. Loại: NEED_SOURCE 58.

- Chưa dòng nào có tham chiếu trong repo.

### Model_tham_chieu

162 dòng. Độ tin cậy: da_kiem_chung 34, uoc_dinh 26, ban_dau_doan 99, NEED_SOURCE 3. Loại: NEED_SOURCE 3, doi_that 142, gia_tuong 17.

- `aa_gun_tower` (aa_gun_tower): mẫu thật: Bofors 40 mm L/70 (towed carriage emplaced on its four outriggers);a small fire-control r…; độ tin: ban_dau_doan; nguồn: R_aa_gun_tower.
- `aa_gun_vehicle` (aa_gun_vehicle): mẫu thật: CV9040 AAV (CV90 hull, Bofors 40 mm L/70 turret, PS-70 search radar);Bofors 40 mm L/70; độ tin: ban_dau_doan; nguồn: R_aa_gun_vehicle.
- `aa_turret` (aa_turret): mẫu thật: 2A38 30 mm twin-barrel gun (the Tunguska's; balance.json tower_flak_30);Stinger twin laun…; độ tin: ban_dau_doan; nguồn: R_aa_turret.
- `aa_turret_a` (aa_turret_a): mẫu thật: ZSU-23-4 Shilka turret, four 2A7 23 mm (balance.json flak_quad);the base post's emplaceme…; độ tin: ban_dau_doan; nguồn: R_aa_turret_a.
- `aa_turret_b` (aa_turret_b): mẫu thật: Starstreak LML;Mistral ATLAS;RBS-70; độ tin: ban_dau_doan; nguồn: R_aa_turret_b.
- `aa_vehicle` (aa_vehicle): mẫu thật: Flakpanzer Gepard 1A2; độ tin: uoc_dinh; nguồn: R_reference_real, W_wikipedia_flakpanzer_gepard, R_aa_vehicle.
- `ammo_carrier` (ammo_carrier): mẫu thật: M977 / M985 HEMTT; độ tin: uoc_dinh; nguồn: R_reference_real, W_wikipedia_heavy_expanded_mobility_tactical_t, R_ammo_carrier.
- `ammo_dump` (ammo_dump): mẫu thật: a field ammunition supply point: a semi-sunken bunker behind an earth berm, crates on pal…; độ tin: ban_dau_doan; nguồn: R_ammo_dump.
- `armored_bulldozer` (armored_bulldozer): mẫu thật: Caterpillar D9R (IDF kit); độ tin: uoc_dinh; nguồn: R_reference_real, D_caterpillar_d9r_specifications, R_armored_bulldozer.
- `armored_car` (armored_car): mẫu thật: Pandur I 6x6; độ tin: uoc_dinh; nguồn: R_reference_real, W_wikipedia_steyr_pandur, R_armored_car.
- `armored_train` (armored_train): mẫu thật: BP-35 armoured train; độ tin: ban_dau_doan; nguồn: R_reference_real, R_armored_train.
- `artillery` (artillery): mẫu thật: M109A6 Paladin; độ tin: da_kiem_chung; nguồn: R_reference_real, W_wikipedia_m109_howitzer, R_artillery.
- `atgm_tower` (atgm_tower): mẫu thật: 9M133 Kornet (Kornet-EM twin launcher);1P163-class guidance unit; độ tin: ban_dau_doan; nguồn: R_atgm_tower.
- `atgm_tower_a` (atgm_tower_a): mẫu thật: 9M133 Kornet;FGM-148 Javelin (top attack, command launch unit); độ tin: ban_dau_doan; nguồn: R_atgm_tower_a.
- `atgm_tower_b` (atgm_tower_b): mẫu thật: 9M133 Kornet;Kornet-EM (multi-tube launcher with a small radar); độ tin: ban_dau_doan; nguồn: R_atgm_tower_b.
- … 144 dòng có tham chiếu nữa: xem sheet Model_tham_chieu.

Nguồn được dùng (tiêu đề như repo ghi; link khi repo có):

- `D_army_recognition_buk_m1_2`: Army Recognition 'Buk-M1-2' (độ tin 2)
- `D_caterpillar_d9r_specifications`: Caterpillar D9R specifications (độ tin 1)
- `D_toyota_hilux_an10_an20_specifications`: Toyota Hilux AN10/AN20 specifications (độ tin 1)
- `R_aa_gun_tower`: spec dựng lại aa_gun_tower (độ tin 3)
- `R_aa_gun_vehicle`: spec dựng lại aa_gun_vehicle (độ tin 3)
- `R_aa_turret`: spec dựng lại aa_turret (độ tin 3)
- `R_aa_turret_a`: spec dựng lại aa_turret_a (độ tin 3)
- `R_aa_turret_b`: spec dựng lại aa_turret_b (độ tin 3)
- `R_aa_vehicle`: spec dựng lại aa_vehicle (độ tin 3)
- `R_ammo_carrier`: spec dựng lại ammo_carrier (độ tin 3)
- `R_ammo_dump`: spec dựng lại ammo_dump (độ tin 3)
- `R_armored_bulldozer`: spec dựng lại armored_bulldozer (độ tin 3)
- `R_armored_car`: spec dựng lại armored_car (độ tin 3)
- `R_armored_train`: spec dựng lại armored_train (độ tin 3)
- `R_artillery`: spec dựng lại artillery (độ tin 3)
- `R_atgm_tower`: spec dựng lại atgm_tower (độ tin 3)
- `R_atgm_tower_a`: spec dựng lại atgm_tower_a (độ tin 3)
- `R_atgm_tower_b`: spec dựng lại atgm_tower_b (độ tin 3)
- `R_attack_jet`: spec dựng lại attack_jet (độ tin 3)
- `R_ballistic_launcher`: spec dựng lại ballistic_launcher (độ tin 3)
- `R_barrage_balloon`: spec dựng lại barrage_balloon (độ tin 3)
- `R_behemoth`: spec dựng lại behemoth (độ tin 3)
- `R_behemoth_inferno`: spec dựng lại behemoth_inferno (độ tin 3)
- `R_behemoth_tempest`: spec dựng lại behemoth_tempest (độ tin 3)
- `R_blast_wall`: spec dựng lại blast_wall (độ tin 3)
- `R_bulwark_post`: spec dựng lại bulwark_post (độ tin 3)
- `R_bunker_shelter_tower`: spec dựng lại bunker_shelter_tower (độ tin 3)
- `R_c_ram`: spec dựng lại c_ram (độ tin 3)
- `R_c_ram_a`: spec dựng lại c_ram_a (độ tin 3)
- `R_c_ram_b`: spec dựng lại c_ram_b (độ tin 3)
- … 173 nguồn nữa: xem sheet Nguon_tham_chieu của 08_tham_chieu.

## Các sheet của file

Mọi sheet, số dòng và ý nghĩa cột nằm trong 00_index.xlsx (Muc_luc_sheet, Schema). Sheet `input_<tên>` là bản chép của một sheet nguồn để công thức Excel đọc cùng file; sửa ở sheet nguồn, không sửa bản chép.

- `Am_thanh` (256 dòng): Âm thanh: clip — Mỗi clip trong Resources/Audio một dòng: nhóm, bậc cỡ, đường dẫn, độ dài, nén, nguồn, giấy phép (Audio/CREDITS.md, Music/MUSIC_CREDITS.md)
- `Am_thanh_bank` (90 dòng): Âm thanh: bank — Tools/sfx/library.json banks: nhóm, bậc cỡ, hàng, số biến thể
- `Am_thanh_thu_vien` (1 dòng): Âm thanh: thư viện — Tools/sfx/library.json: ghi chú (bậc cỡ theo cỡ nòng)
- `Am_thanh_envelope` [bulk.zip] (226 dòng): Âm thanh: envelope — Audio/sfx/envelopes.txt: RMS mỗi 20 ms (50 Hz, x1000) của từng clip cho compressor của Effects; dòng '#' là ghi chú
- `Am_thanh_loat` (7 dòng): Âm thanh: loạt bắn nhanh — SoundLibrary.Bursts: bank loạt, cỡ, nhịp (phát/s), số phát mỗi đoạn
- `VFX_bac` (6 dòng): VFX theo bậc — Bậc T0-T5: chớp đầu nòng, khói, vòng bụi, sóng nước, ánh sáng, giật (TierFx.Fire) và thời gian cầu lửa, khói, hố (EffectLife.Bands); rung camera, hạt…
- `VFX_chay_than_xe` (3 dòng): VFX: lửa thân xe — HullFire.Looks: 3 mức lửa (thân, lưỡi lửa, khói, tàn, tia)
- `Hau_ky_hinh_anh` (52 dòng): Hậu kỳ hình ảnh — Settings/BattlefieldProfile.asset: mỗi thiết lập của mỗi hiệu ứng (Bloom, Tonemapping, Color Adjustments...) một dòng: ghi đè, giá trị; trường Unity…
- `Xac_vo` (3 dòng): Xác vỡ — Xác vỡ theo bậc đồ họa: trần đầy đủ và thời gian sống
- `Am_thanh_mixer` (9 dòng): Âm thanh: mixer — Mixer âm thanh: nhóm kênh và âm lượng mặc định
- `Am_thanh_mau` (3 dòng): Âm thanh: bản ghi mẫu — Docs/audio/samples: 3 bản trộn trận mẫu (Tools/sfx/render_mix.py): file, độ dài, số sự kiện / phát / cắt, limiter, compressor, độ to (mixes.json); mố…
- `Am_thanh_mau_moc` (24 dòng): Âm thanh mẫu: mốc tiếng lớn — Mỗi bản trộn: các cửa sổ 400 ms to nhất (bước 100 ms, K-weighting BS.1770 của Tools/sfx/analyze_sfx.py trên kênh trộn mono) không dưới 6 LU so với cử…
- `VFX_vu_khi` (77 dòng): VFX theo vũ khí — EffectShots.FxBatch: mỗi bậc T0-T5 (vũ khí đại diện chọn lúc chụp) và mỗi vũ khí >= 120 mm có đơn vị mang: bậc, cỡ, số nòng, thư mục ảnh, số ảnh có /…
- `VFX_vu_khi_anh` (646 dòng): VFX theo vũ khí: ảnh — Mỗi ảnh của mỗi chủ đề: khung (fire / impact / salvo), giây sau phát bắn / lúc chạm, đường dẫn tương đối Builds/effect_shots/<key>/<ảnh>, present / p…
- `Am_thanh_so_do` (221 dòng): Âm thanh: số đo — Mỗi clip trận (không gồm nhạc): LUFS, đỉnh dB, tỷ lệ năng lượng dưới 150 Hz, đuôi, phát hiện 'keng' (Docs/audio/metrics.json của Tools/sfx/analyze_sf…
- `Am_thanh_so_do_bac` (15 dòng): Âm thanh: bảng theo bậc cỡ — Mỗi bậc cỡ x vai (bắn / nổ): trung bình M-max, LUFS, tỷ lệ dưới 150 Hz, đuôi của các bank hàng đó (metrics.json sizes); phải tăng đều từ <= 14,5 mm t…
- `VFX_ngan_sach` (8 dòng): VFX: ngân sách — Ngân sách hiệu ứng: theo bậc T0-T5 (TierFx.cs: số vụ nổ chi tiết đầy đủ cùng lúc FullCap, trọng số với trần WeightCap, thời gian tính là đang chạy Bu…
- `VFX_ngan_sach_hat` (9 dòng): VFX: trần hạt mỗi bộ phát — Mọi chỗ Game/Effects đặt maxParticles bằng một số cố định (file:dòng); bộ phát đặt theo biến (max) không có số cố định
- `Hieu_ung_tham_chieu` (58 dòng): Hiệu ứng và âm thanh: nguồn và tham chiếu — Mỗi bậc VFX và mỗi nhóm âm thanh (nhóm × bậc cỡ) một dòng: nguồn ghi âm / tổng hợp, giấy phép, đặc điểm tiếng thật, game tham chiếu cảm giác (spec 12…
- `Model` (473 dòng): Model — Mỗi GLB một dòng (đọc bằng Tools/assets/glb_analyze.read_glb): tam giác, nút, vật liệu, mesh, số Part_* / Mount_* / Muzzle_*, Mount_Flare / Mount_APS…
- `Model_nut` [bulk.zip] (17604 dòng): Model: nút — nodes[].name: mọi nút của mọi GLB một dòng
- `Model_kiem_chuan` (473 dòng): Model: kiểm chuẩn (baseline) — Tools/assets/baseline.json models: số liệu kiểm máy của mỗi model (tam giác, đỉnh, renderer, bộ phận chạy, lỗi, cảnh báo, nút runtime, kích thước, ha…
- `Model_tieu_chuan` (14 dòng): Model: tiêu chuẩn — baseline.json budgets: ngân sách theo lớp x bậc (normal / hd): tam giác, đỉnh, renderer, bộ phận chạy [mức, trần]; ngân sách là hướng dẫn, không phải…
- `Model_kiem_chuan_chung` (3 dòng): Model: kiểm chuẩn (chung) — baseline.json: số model, ngày sinh
- `Model_ten_nut_on_dinh` (308 dòng): Model: tên nút runtime ổn định — Tools/assets/runtime_node_map.json: mỗi model đã đổi tên nút có hậu tố Blender (.001) sang tên ngữ nghĩa ổn định (cũ -> mới, giữ thứ tự); frontier_ki…
- `Model_nut_ton_dong` (5 dòng): Model: lỗi nút runtime đã biết — Tools/assets/runtime_node_baseline.json: lỗi cứng đã biết (model/luật/vị trí) và lý do; lỗi mới làm runtime_node_audit.py thất bại
- `Model_ngan_sach_mien` (17 dòng): Model: miễn trừ ngân sách — Tools/assets/budget_waivers.json: miễn trừ chính thức (ai, ngày, lý do, việc tiếp) cho lỗi ngân sách cứng và ghi chú duyệt cho mức mềm. Báo cáo: Docs…
- `Model_gop_luoi_tinh` (2 dòng): Model: gộp lưới tĩnh — Tools/assets/static_merge.json: model có các lưới chi tiết tĩnh cùng vật liệu được gộp trong GLB (Tools/assets/glb_merge_static.py; hình trên màn hìn…
- `Kich_thuoc_that` (84 dòng): Kích thước thật tham chiếu — Tools/models/reference_real.json: mẫu thật, kích thước dài / rộng / cao (m), nguồn, độ tin (conf); dùng ở 13
- `Kich_thuoc_that_chung` (1 dòng): Kích thước thật: ghi chú — reference_real.json: khóa ngoài units
- `Model_chuan_vang` (925 dòng): Model: số đo bộ mẫu vàng — Tools/assets/gold_metrics.json: trung bình theo lớp của bộ model mẫu (quality_gate.compute_gold,)
- `Model_spec_dung` (11798 dòng): Model: spec dựng lại — Tools/blender/specs/<model>.json: spec dựng lại model (mẫu thật, kích thước đích, bộ phận, vũ khí, ngân sách, vùng màu;); id = <model>.<đường dẫn>
- `Anh_the` [bulk.zip] (194 dòng): Ảnh thẻ — Resources/UI/Cards/manifest.json entries: ảnh thẻ render từ model (loại, model, nguồn, hash)
- `Anh_the_chung` (3 dòng): Ảnh thẻ: cài đặt render — manifest.json: camera, cỡ ảnh, phiên bản
- `Dia_phuong_hoa` [bulk.zip] (6317 dòng): Địa phương hóa — Mọi khóa chữ của các bảng C# ["key"] = ("en", "vi") một dòng
- `Giay_phep_tai_san` (5 dòng): Giấy phép tài sản — Resources/Licenses/*.txt: mỗi file giấy phép một dòng (phông chữ OFL); nội dung từng dòng ở Giay_phep_noi_dung; âm thanh: 07_hinh_anh_am_thanh_model/…
- `Giay_phep_noi_dung` [bulk.zip] (374 dòng): Giấy phép: nội dung — mỗi dòng không trống của file giấy phép
- `Xem_truoc` (203 dòng): Màn xem trước — Màn xem trước của từng đơn vị: cảnh nền
- `Kit_chi_tiet` (70 dòng): Bộ chi tiết kit35 — Docs/models/kit_catalog/kit35_components.json: 70 chi tiết của Tools/blender/mb_kit35.py (tam giác, kích thước, lỗi kiểm); ảnh: kit35_catalog.png (An…
- `Model_cham_diem` (163 dòng): Model: chấm điểm — Chấm điểm theo Docs/models/MODEL_STANDARD.md: tam giác trong ngân sách, Part_* thiếu, Mount / Muzzle thiếu, sai tỷ lệ, hình bóng (quét hình); điểm; x…
- `Dia_phuong_hoa_van_de` [bulk.zip] (271 dòng): Địa phương hóa: khóa có vấn đề — Mỗi khóa chữ có vấn đề một dòng: thiếu tiếng Anh / Việt, khai hai lần, tên riêng chỉ có ở một thứ tiếng (danh sách tên của Tools/story/script_build.p…
- `Dia_phuong_hoa_thong_ke` (15 dòng): Địa phương hóa: thống kê — Mỗi bảng chữ C#: số khóa, khóa thiếu tiếng Anh / Việt, khai hai lần, có tên riêng ở một thứ tiếng, không thấy trong mã (COUNTIFS trên Dia_phuong_hoa…
- `Model_tham_chieu` (162 dòng): Model: tài liệu tham chiếu hình dạng và kích thước — Mỗi model có mẫu thật một dòng: tài liệu hình dạng / kích thước (chỉ nguồn và URL, không nhúng ảnh), kích thước thật (tra sống Kich_thuoc_that), ghi…
