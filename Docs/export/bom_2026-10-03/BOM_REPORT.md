# BOM_REPORT: ném bom dồn một điểm, lượt 0 (nguyên nhân) và lượt 2 (trước / sau) (2026-10-03)

## Nguyên nhân quan sát được trong mã

1. **Máy bay ném bom thường (bom rơi tự do) KHÔNG dùng chung một điểm nhắm.** Mỗi quả được nhắm lại lúc thả: `aimAt = BombImpact(shooter)` = vị trí máy bay + hướng mũi × tốc độ × thời gian rơi (Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.cs:820-821; Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.Bombs.cs:38-39). Nhưng khoảng cách giữa hai quả chỉ là tốc độ × BurstInterval (CombatSystem.Bombs.cs:42-43): Oanh tạc cơ chiến lược 22 m/s × 0,2 s = 4,4 m (3,5 m khi ga 0,8 trong tầm, MovementSystem.cs:968), trong khi lõi nổ 10 m và tản 3,5 m: 7 quả nằm trong dải ~21–26 m, lõi chồng lõi (lõi / khoảng ≈ 2,3–2,9), nhìn như một đống. Cường kích: 2 quả × 0,25 s × 32 m/s = 8 m (lõi 8 m).
2. **Bom khoang của boss rơi đúng một điểm.** p26_roc_roc_bombs / p26_roc_main_roc_bombs (Argus, Garuda, khí cầu chỉ huy; 8 quả 400 kg) kế thừa boss_howitzer nên bay như đạn pháo (Projectile = Shell), FreeFall = false: cả loạt nhắm vào chính mục tiêu (Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.cs:529 nhắm t.Position khi mục tiêu còn sống, :611 BurstAim), chỉ lệch theo độ tản (:829). Đây là chỗ 'mọi quả cùng một điểm' thật sự.
3. **Bom dẫn đường là POINT theo thiết kế:** stealth_payload (B-2, 2 × 907 kg, guided), guided_bomb (SDB), glide_fab500 (UMPK) nhắm vào mục tiêu.
4. **Thẻ hỗ trợ không kích và siêu vũ khí boss dạng strip đã rải dải** (StrikeSystem.cs:250-275 Lerp dọc đường; BossSystem.BigAttacks.cs:708-720): garuda_carpet 20 quả / 100 m (5 m, lõi 7 m), airship_carpet 16 / 80 m, kraken_air_raid 12 / 90 m, airstrike 4 / 60 m, napalm_strike 8 / 55 m.
5. **Thẻ nói 12 quả, dữ liệu là 7:** GuideText.cs:410/414 'một hàng 12 quả' vs balance.json bomber_payload burst 7, load 7.
6. An toàn quân ta xét cả loạt một lần (CombatSystem.Bombs.cs:76-82): có xe ta gần giữa dải thì bỏ cả lượt, không bỏ từng quả. Không có điều kiện 'đủ 2/3 số bom' trong mã.

## Số đo (Bom_vet_tha)

| id | so_bom | so_diem_roi_khac_nhau | khoang_cach_xa_nhat_m | do_dai_dai_m | do_lech_ngang_m | khoang_cach_tb_giua_bom_m | ty_le_chong_lan |
|---|---|---|---|---|---|---|---|
| air_raid/(the_ho_tro)/TONG_KET | 10.0 | 10.0 | 70.011 | 70.0 | 5.086 | 7.778 | 1.029 |
| airship_carpet/command_airship/TONG_KET | 16.0 | 16.0 | 75.055 | 75.0 | 7.745 | 5.0 | 1.4 |
| airstrike/(the_ho_tro)/TONG_KET | 4.0 | 4.0 | 60.091 | 60.0 | 3.957 | 20.0 | 0.5 |
| bomber_payload/heavy_bomber/TONG_KET | 7.0 | 7.0 | 65.757 | 65.68 | 4.616 | 10.947 | 0.914 |
| bunker_buster_bomb/glide_bomber/TONG_KET | 1.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| cluster_at_bomb/glide_bomber/TONG_KET | 1.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| cluster_strike/(the_ho_tro)/TONG_KET | 30.0 | 30.0 | 60.39 | 60.0 | 9.655 | 2.069 | 2.658 |
| garuda_carpet/garuda/TONG_KET | 20.0 | 20.0 | 95.124 | 95.0 | 9.355 | 5.0 | 1.4 |
| glide_fab500/glide_bomber/TONG_KET | 1.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| guided_bomb/morrigan/TONG_KET | 1.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| guided_bomb/stealth_fighter/TONG_KET | 1.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| guided_bomb/strike_drone/TONG_KET | 1.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| jet_bombs/attack_jet/TONG_KET | 1.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| jet_bombs/elite_attack_jet/TONG_KET | 1.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| jet_bombs/stealth_naval_strike/TONG_KET | 2.0 | 2.0 | 9.27 | 8.963 | 2.321 | 8.963 | 0.913 |
| kraken_air_raid/kraken/TONG_KET | 12.0 | 12.0 | 82.651 | 82.5 | 8.823 | 7.5 | 1.2 |
| napalm_strike/(the_ho_tro)/TONG_KET | 8.0 | 8.0 | 55.091 | 55.0 | 4.061 | 7.857 | 1.145 |
| p26_roc_main_roc_bombs/argus/TONG_KET | 8.0 | 8.0 | 76.835 | 76.816 | 4.616 | 10.974 | 0.911 |
| p26_roc_main_roc_bombs/command_airship/TONG_KET | 8.0 | 8.0 | 76.835 | 76.816 | 4.616 | 10.974 | 0.911 |
| p26_roc_main_roc_bombs/garuda/TONG_KET | 8.0 | 8.0 | 76.835 | 76.816 | 4.616 | 10.974 | 0.911 |
| stealth_payload/stealth_bomber/TONG_KET | 2.0 | 2.0 | 1.839 | 1.539 | 0.758 | 1.539 | 14.42 |
| thermobaric_bomb/glide_bomber/TONG_KET | 1.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## File

- Docs/export/bom_2026-10-03/Machine_Brigade_Bom_2026-10-03.xlsx (6 sheet), Docs/export/bom_2026-10-03/csv/<sheet>.csv, Docs/export/bom_2026-10-03/Machine_Brigade_Bom_2026-10-03.md, Docs/export/bom_2026-10-03/BOM_REPORT.md
- Vết thả từ Unity: vet_tha_unity.csv (có); test: Assets/MachineBrigade/Tests/EditMode/BombStickTrace.cs
- Bộ xuất: Tools/export/bom.py (`python Tools/export/export.py bom [--trace CSV]`)
- Mã: Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.Bombs.cs, Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.cs (CanFire, Operate, Launch), Assets/MachineBrigade/Scripts/Sim/Movement/MovementSystem.cs (BombTarget, chạy vào), Assets/MachineBrigade/Scripts/Sim/Strikes/StrikeSystem.cs (Airstrike), Assets/MachineBrigade/Scripts/Sim/Bosses/BossSystem.BigAttacks.cs (Strip)


## Lượt 2: trước / sau (Bom_ket_qua_vung, trung bình 3 seed)

TRƯỚC = vết thả lượt 0 (Docs/export/bom_2026-10-03/vet_tha_truoc_luot2.csv, mục tiêu một xe tăng); SAU = vết thả mới (vet_tha_unity.csv, mục tiêu là xe giữa hàng 5 xe dọc đường bay). 

| id | doi_hinh | so_bom_truoc | so_bom_sau | trung_loi_truoc | trung_loi_sau | trung_truoc | trung_sau |
|---|---|---|---|---|---|---|---|
| air_raid/(the_ho_tro) | CUM_8M | 10.0 | 10.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| air_raid/(the_ho_tro) | HANG_DOC_8M | 10.0 | 10.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| air_raid/(the_ho_tro) | HANG_NGANG_8M | 10.0 | 10.0 | 2.0 | 2.0 | 2.0 | 2.0 |
| airship_carpet/command_airship | CUM_8M | 16.0 | 16.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| airship_carpet/command_airship | HANG_DOC_8M | 16.0 | 16.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| airship_carpet/command_airship | HANG_NGANG_8M | 16.0 | 16.0 | 2.667 | 2.667 | 4.0 | 4.0 |
| airstrike/(the_ho_tro) | CUM_8M | 4.0 | 4.0 | 4.0 | 4.0 | 4.0 | 4.0 |
| airstrike/(the_ho_tro) | HANG_DOC_8M | 4.0 | 4.0 | 4.0 | 4.0 | 4.0 | 4.0 |
| airstrike/(the_ho_tro) | HANG_NGANG_8M | 4.0 | 4.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| bomber_payload/heavy_bomber | CUM_8M | 7.0 | 7.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| bomber_payload/heavy_bomber | HANG_DOC_8M | 7.0 | 7.0 | 4.333 | 5.0 | 4.333 | 5.0 |
| bomber_payload/heavy_bomber | HANG_NGANG_8M | 7.0 | 7.0 | 3.0 | 2.333 | 3.0 | 2.333 |
| bunker_buster_bomb/glide_bomber | CUM_8M | 1.0 | 1.0 | 3.0 | 3.0 | 3.0 | 3.0 |
| bunker_buster_bomb/glide_bomber | HANG_DOC_8M | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| bunker_buster_bomb/glide_bomber | HANG_NGANG_8M | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| cluster_at_bomb/glide_bomber | CUM_8M | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| cluster_at_bomb/glide_bomber | HANG_DOC_8M | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| cluster_at_bomb/glide_bomber | HANG_NGANG_8M | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| cluster_strike/(the_ho_tro) | CUM_8M | 30.0 | 30.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| cluster_strike/(the_ho_tro) | HANG_DOC_8M | 30.0 | 30.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| cluster_strike/(the_ho_tro) | HANG_NGANG_8M | 30.0 | 30.0 | 2.333 | 2.333 | 2.333 | 2.333 |
| garuda_carpet/garuda | CUM_8M | 20.0 | 20.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| garuda_carpet/garuda | HANG_DOC_8M | 20.0 | 20.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| garuda_carpet/garuda | HANG_NGANG_8M | 20.0 | 20.0 | 2.333 | 2.333 | 4.333 | 4.333 |
| glide_fab500/glide_bomber | CUM_8M | 1.0 | 1.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| glide_fab500/glide_bomber | HANG_DOC_8M | 1.0 | 1.0 | 3.0 | 3.0 | 3.0 | 3.0 |
| glide_fab500/glide_bomber | HANG_NGANG_8M | 1.0 | 1.0 | 3.0 | 3.0 | 3.0 | 3.0 |
| guided_bomb/morrigan | CUM_8M | 1.0 | 1.0 | 1.0 | 1.0 | 5.0 | 5.0 |
| guided_bomb/morrigan | HANG_DOC_8M | 1.0 | 1.0 | 1.0 | 1.0 | 2.0 | 2.0 |
| guided_bomb/morrigan | HANG_NGANG_8M | 1.0 | 1.0 | 1.0 | 1.0 | 1.667 | 1.667 |
| guided_bomb/stealth_fighter | CUM_8M | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| guided_bomb/stealth_fighter | HANG_DOC_8M | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| guided_bomb/stealth_fighter | HANG_NGANG_8M | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| guided_bomb/strike_drone | CUM_8M | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| guided_bomb/strike_drone | HANG_DOC_8M | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| guided_bomb/strike_drone | HANG_NGANG_8M | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| jet_bombs/attack_jet | CUM_8M | 1.0 | 1.0 | 4.667 | 4.667 | 4.667 | 4.667 |
| jet_bombs/attack_jet | HANG_DOC_8M | 1.0 | 1.0 | 2.0 | 2.0 | 2.0 | 2.0 |
| jet_bombs/attack_jet | HANG_NGANG_8M | 1.0 | 1.0 | 1.333 | 2.0 | 1.333 | 2.0 |
| jet_bombs/elite_attack_jet | CUM_8M | 1.0 | 1.0 | 4.667 | 4.667 | 4.667 | 4.667 |
| jet_bombs/elite_attack_jet | HANG_DOC_8M | 1.0 | 1.0 | 2.0 | 2.0 | 2.0 | 2.0 |
| jet_bombs/elite_attack_jet | HANG_NGANG_8M | 1.0 | 1.0 | 1.333 | 2.0 | 1.333 | 2.0 |
| jet_bombs/stealth_naval_strike | CUM_8M | 2.0 | 2.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| jet_bombs/stealth_naval_strike | HANG_DOC_8M | 2.0 | 2.0 | 3.0 | 3.0 | 3.0 | 3.0 |
| jet_bombs/stealth_naval_strike | HANG_NGANG_8M | 2.0 | 2.0 | 1.0 | 2.0 | 1.0 | 2.0 |
| kraken_air_raid/kraken | CUM_8M | 12.0 | 12.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| kraken_air_raid/kraken | HANG_DOC_8M | 12.0 | 12.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| kraken_air_raid/kraken | HANG_NGANG_8M | 12.0 | 12.0 | 2.333 | 2.333 | 4.667 | 4.667 |
| napalm_strike/(the_ho_tro) | CUM_8M | 8.0 | 8.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| napalm_strike/(the_ho_tro) | HANG_DOC_8M | 8.0 | 8.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| napalm_strike/(the_ho_tro) | HANG_NGANG_8M | 8.0 | 8.0 | 2.333 | 2.333 | 2.333 | 2.333 |
| p26_roc_main_roc_bombs/argus | CUM_8M | 8.0 | 8.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| p26_roc_main_roc_bombs/argus | HANG_DOC_8M | 8.0 | 8.0 | 3.0 | 5.0 | 5.0 | 5.0 |
| p26_roc_main_roc_bombs/argus | HANG_NGANG_8M | 8.0 | 8.0 | 3.0 | 3.0 | 5.0 | 5.0 |
| p26_roc_main_roc_bombs/command_airship | CUM_8M | 8.0 | 8.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| p26_roc_main_roc_bombs/command_airship | HANG_DOC_8M | 8.0 | 8.0 | 3.0 | 5.0 | 5.0 | 5.0 |
| p26_roc_main_roc_bombs/command_airship | HANG_NGANG_8M | 8.0 | 8.0 | 3.0 | 3.0 | 5.0 | 5.0 |
| p26_roc_main_roc_bombs/garuda | CUM_8M | 8.0 | 8.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| p26_roc_main_roc_bombs/garuda | HANG_DOC_8M | 8.0 | 8.0 | 3.0 | 5.0 | 5.0 | 5.0 |
| p26_roc_main_roc_bombs/garuda | HANG_NGANG_8M | 8.0 | 8.0 | 3.0 | 3.0 | 5.0 | 5.0 |
| stealth_payload/stealth_bomber | CUM_8M | 2.0 | 2.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| stealth_payload/stealth_bomber | HANG_DOC_8M | 2.0 | 2.0 | 3.0 | 3.0 | 3.0 | 3.0 |
| stealth_payload/stealth_bomber | HANG_NGANG_8M | 2.0 | 2.0 | 3.0 | 3.0 | 3.0 | 3.0 |
| thermobaric_bomb/glide_bomber | CUM_8M | 1.0 | 1.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| thermobaric_bomb/glide_bomber | HANG_DOC_8M | 1.0 | 1.0 | 3.0 | 3.0 | 3.0 | 3.0 |
| thermobaric_bomb/glide_bomber | HANG_NGANG_8M | 1.0 | 1.0 | 3.0 | 3.0 | 3.0 | 3.0 |
