# Machine Brigade: dữ liệu ném bom (2026-10-03)

Lượt 0 của bản sửa ném bom rải thảm (Docs/prompts/bomb_run_vi.txt). Sinh bởi `python Tools/export/export.py bom`; chỉ đọc, không đổi giá trị game. Bảng đủ cột trong xlsx / csv; ở đây là các cột chính.

Bom_vet_tha: đọc 132 dòng từ vet_tha_unity.csv; thẻ hỗ trợ và siêu vũ khí boss tính lại bằng python theo công thức trong mã.

## Bom_vu_khi

| id | nhom | ten_that | dau_no_kg | loai_sat_thuong | sat_thuong_moi_phat | loi_m | so_bom_moi_luot | khoang_tha_giua_bom_s | thoi_gian_nap_s | duong_tha_theo_ma | don_vi_mang | khoang_cach_giua_bom_m_toan_toc | do_dai_dai_m_toan_toc | ty_le_chong_lan_loi_tren_khoang | canh_bao_theo_luat |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bomber_payload | vu_khi_don_vi | FAB-500 (500 kg) | 500 | HighExplosive | 420 | 10 | 7 | 0.2 | 11.2 | FREE_FALL_STICK | heavy_bomber | 4.4 | 26.4 | 2.273 | TRUE |
| bunker_buster_bomb | vu_khi_don_vi | GBU-28 | 2100 | HighExplosive | 1400 | 6 | 1 |  | 90 | FREE_FALL | glide_bomber |  |  |  | TRUE |
| cluster_at_bomb | vu_khi_don_vi | CBU-97 Sensor Fuzed Weapon | 450 | ShapedCharge | 0 | 3 | 1 |  | 90 | FREE_FALL | glide_bomber |  |  |  | TRUE |
| glide_fab500 | vu_khi_don_vi | FAB-500 M-62 with UMPK glide kit | 500 | HighExplosive | 420 | 10 | 1 |  | 3 | GLIDE | glide_bomber |  |  |  | FALSE |
| guided_bomb | vu_khi_don_vi | GBU-39 SDB (110 kg) | 110 | HighExplosive | 210 | 4 | 1 |  | 6.651 | GUIDED | morrigan;stealth_fighter;strike_drone |  |  |  | FALSE |
| jet_bombs | vu_khi_don_vi | FAB-250 (250 kg) | 250 | HighExplosive | 310 | 8 | 2 | 0.25 | 10.05 | FREE_FALL_STICK | attack_jet;elite_attack_jet;stealth_naval_strike | 8.0 | 8.0 | 1.0 | FALSE |
| p26_roc_main_roc_bombs | vu_khi_don_vi | bomb-bay stick 400 kg | 400 | HighExplosive | 700 | 10 | 8 | 0.3 | 33.34 | BAY_STICK | argus;command_airship;garuda |  |  |  | TRUE |
| p26_roc_roc_bombs | vu_khi_don_vi | bomb-bay stick 400 kg | 400 | HighExplosive | 400 | 5 | 8 | 0.3 | 2.9 | BAY_STICK |  |  |  |  | TRUE |
| stealth_payload | vu_khi_don_vi | GBU-31 JDAM (907 kg) | 907 | HighExplosive | 892 | 13 | 2 | 0.3 | 14 | GUIDED | stealth_bomber |  |  |  | FALSE |
| thermobaric_bomb | vu_khi_don_vi | ODAB-500 | 500 | HighExplosive | 380 | 12 | 1 |  | 90 | FREE_FALL | glide_bomber |  |  |  | TRUE |
| air_raid | the_ho_tro | Không kích bất ngờ |  | NEED_CODE_CHECK | 200 | 8.0 | 10 | 0.267 | 0 | SUPPORT_AIRSTRIKE | (máy bay của thẻ, không là đơn vị) | 7.778 | 70.0 | 1.029 | TRUE (vòng / dải hỗ trợ) |
| airstrike | the_ho_tro | Không kích |  | NEED_CODE_CHECK | 210 | 10.0 | 4 | 0.4 | 90 | SUPPORT_AIRSTRIKE | (máy bay của thẻ, không là đơn vị) | 20.0 | 60.0 | 0.5 | TRUE (vòng / dải hỗ trợ) |
| cluster_at_strike | the_ho_tro | Bom chùm chống tăng |  | ShapedCharge | 160 | 3.0 | 10 |  | 90 | SUPPORT_HOMING | (máy bay của thẻ, không là đơn vị) |  |  |  | TRUE (vòng / dải hỗ trợ) |
| cluster_strike | the_ho_tro | Bom chùm |  | NEED_CODE_CHECK | 90 | 5.5 | 30 | 0.076 | 15 | SUPPORT_AIRSTRIKE | (máy bay của thẻ, không là đơn vị) | 2.069 | 60.0 | 2.658 | TRUE (vòng / dải hỗ trợ) |
| glide_bomb_strike | the_ho_tro | Đòn bom lượn |  | NEED_CODE_CHECK | 420 | 10.0 | 2 |  | 90 | SUPPORT_CRUISEMISSILE | (máy bay của thẻ, không là đơn vị) |  |  |  | TRUE (vòng / dải hỗ trợ) |
| napalm_strike | the_ho_tro | Bom napalm |  | Fire | 150 | 9.0 | 8 | 0.2 | 90 | SUPPORT_AIRSTRIKE | (máy bay của thẻ, không là đơn vị) | 7.857 | 55.0 | 1.145 | TRUE (vòng / dải hỗ trợ) |
| airship_carpet | sieu_vu_khi_boss |  |  | HighExplosive | 400 | 7.0 | 16 | 0.2 | 50 | BOSS_STRIP | command_airship | 5.0 | 80.0 | 1.4 | TRUE (siêu vũ khí) |
| carrier_heavy_bomb | sieu_vu_khi_boss | bomber_payload |  | HighExplosive | 1600 | 16.0 | 1 |  | 45 | BOSS_MISSILE | drone_mothership |  |  |  | TRUE (siêu vũ khí) |
| garuda_carpet | sieu_vu_khi_boss |  |  | HighExplosive | 350 | 7.0 | 20 | 0.158 | 50 | BOSS_STRIP | garuda | 5.0 | 100.0 | 1.4 | TRUE (siêu vũ khí) |
| kraken_air_raid | sieu_vu_khi_boss |  |  | HighExplosive | 400 | 9.0 | 12 | 0.273 | 50 | BOSS_STRIP | kraken | 7.5 | 90.0 | 1.2 | TRUE (siêu vũ khí) |

## Bom_don_vi

| id | loai | toc_do_m_s | xoay_than_deg_s | ban_kinh_quay_m | do_cao_tha_m | vu_khi_bom | so_bom_moi_luot | bang_dan_qua | nap_lai_s | thoi_gian_roi_s_theo_ma | khoang_dan_dau_m_theo_ma |
|---|---|---|---|---|---|---|---|---|---|---|---|
| argus | boss | 4.5 | 16.0 | 16.114 | 30.0 | p26_roc_main_roc_bombs | 8 | ∞ | NEED_CODE_CHECK | 1.225 | 5.511 |
| attack_jet | xe | 32.0 | 104.0 | 17.629 | 30.0 | jet_bombs | 2 | ∞ | 14 | 1.225 | 39.192 |
| command_airship | boss | 4.5 | 16.0 | 16.114 | 30.0 | p26_roc_main_roc_bombs | 8 | ∞ | NEED_CODE_CHECK | 1.225 | 5.511 |
| elite_attack_jet | xe | 32.0 | 104.0 | 17.629 | 30.0 | jet_bombs | 2 | ∞ | 14 | 1.225 | 39.192 |
| garuda | boss | 6.0 | 16.0 | 21.486 | 30.0 | p26_roc_main_roc_bombs | 8 | ∞ | NEED_CODE_CHECK | 1.225 | 7.348 |
| glide_bomber | xe | 30.0 | 60.0 | 28.648 | 40.0 | bunker_buster_bomb;cluster_at_bomb;glide_fab500;thermobaric_bomb | 1;1;1;1 | ∞;∞;∞;∞ | 21 | 1.414 | 42.426 |
| heavy_bomber | xe | 22.0 | 68.0 | 18.537 | 42.0 | bomber_payload | 7 | ∞ | 16 | 1.449 | 31.881 |
| morrigan | boss | 44.0 | 118.0 | 21.365 | 40.0 | guided_bomb | 1 | ∞ | NEED_CODE_CHECK | 1.414 | 62.225 |
| stealth_bomber | xe | 28.0 | 86.0 | 18.654 | 46.0 | stealth_payload | 2 | ∞ | 16 | 1.517 | 42.464 |
| stealth_fighter | xe | 44.0 | 125.0 | 20.168 | 36.0 | guided_bomb | 1 | ∞ | 11 | 1.342 | 59.032 |
| stealth_naval_strike | xe | 30.0 | 86.0 | 19.987 | 46.0 | jet_bombs | 2 | ∞ | 16 | 1.517 | 45.497 |
| strike_drone | xe | 13.9 | 81.0 | 9.832 | 30.0 | guided_bomb | 1 | ∞ | 8.5 | 1.225 | 17.024 |
| air_raid | the_ho_tro | 29.167 |  |  | NEED_CODE_CHECK | air_raid | 10 |  | 0 |  |  |
| airstrike | the_ho_tro | 50.0 |  |  | NEED_CODE_CHECK | airstrike | 4 |  | 90 |  |  |
| cluster_at_strike | the_ho_tro |  |  |  | NEED_CODE_CHECK | cluster_at_strike | 10 |  | 90 |  |  |
| cluster_strike | the_ho_tro | 27.273 |  |  | NEED_CODE_CHECK | cluster_strike | 30 |  | 15 |  |  |
| glide_bomb_strike | the_ho_tro |  |  |  | NEED_CODE_CHECK | glide_bomb_strike | 2 |  | 90 |  |  |
| napalm_strike | the_ho_tro | 39.286 |  |  | NEED_CODE_CHECK | napalm_strike | 8 |  | 90 |  |  |
| command_airship/airship_carpet | boss_sieu_vu_khi | 4.5 | 16 |  | 30 | airship_carpet | 16 |  | 50 |  |  |
| drone_mothership/carrier_heavy_bomb | boss_sieu_vu_khi | 3.5 | 20 |  | 26 | carrier_heavy_bomb | 1 |  | 45 |  |  |
| garuda/garuda_carpet | boss_sieu_vu_khi | 6 | 16 |  | 30 | garuda_carpet | 20 |  | 50 |  |  |
| kraken/kraken_air_raid | boss_sieu_vu_khi | 2.6 | 8 |  | 0 | kraken_air_raid | 12 |  | 50 |  |  |

## Bom_hanh_vi

| id | buoc | mo_ta_theo_ma | file_ham |
|---|---|---|---|
| HV01 | chon_muc_tieu | Máy bay cánh cố định có vũ khí CHÍNH là bom và burst > 1 chọn mục tiêu bằng BombTarget: xe mặt đất địch nhìn thấy trong max(tầm nhìn, 60 m), điểm = BombWorth (cụm, công trình; trừ nơi vừa ném) × √clamp(Worth, 2, 25) / (1 + d/200). Đơn vị khác (bom là vũ khí phụ, boss): kẻ địch gần nhất trong tầm. | Assets/MachineBrigade/Scripts/Sim/Movement/MovementSystem.cs:402-404 Think; Assets/MachineBrigade/Scripts/Sim/Movement/MovementSystem.cs:433 BombTarget; Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.cs:406 BombWorth |
| HV02 | huong_vao | Máy bay quay mũi vào mục tiêu (goal = target.Position). Lượt 2: dải có heading AXIS (bomber_payload) khi còn xa thì bay tới điểm vào trên trục chính của cụm mục tiêu (StickEntry: phía sau mục tiêu một khoảng dẫn đầu + nửa dải + bán kính quay; trục trong ±45° so với hướng vào, không thì giữ hướng vào), rồi mới vào mục tiêu. Hướng dải = hướng mũi lúc thả. | Assets/MachineBrigade/Scripts/Sim/Movement/MovementSystem.cs DriveAeroplane; Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.Bombs.cs StickEntry, StickDirection |
| HV03 | toc_do_luc_tha | Ga 0,8 khi cách mục tiêu < 1,1 × AttackReach (AttackReach = tầm súng thân ngắn nhất, không có thì tầm vũ khí 0); có AttackHold thì ga 0,5–1 khi vào giữ; khi kéo ra (RunExtending) ga 1. Tốc độ đổi tối đa 0,8 × tốc độ/s. | Assets/MachineBrigade/Scripts/Sim/Movement/MovementSystem.cs:960-968, Assets/MachineBrigade/Scripts/Sim/Movement/MovementSystem.cs:994, Assets/MachineBrigade/Scripts/Sim/Movement/MovementSystem.cs:1194 AttackReach |
| HV04 | dieu_kien_tha | CanFire: hết hồi, đúng loại đạn; dải STICK chỉ bị giữ lại khi MỌI quả đều rơi gần quân ta (StickAllUnsafe); trong tầm (InReach, tầm bom = tốc độ × thời gian rơi + nửa dải + lõi, dải = (n−1) × spacing), rồi StickStraddles: mục tiêu lệch ngang ≤ lõi + bán kính mục tiêu và dọc đường bay từ (rơi − blast/2) tới (rơi + nửa dải + 2 m) khi tâm dải CENTER (START: tới rơi + blast/2). Khoang bom boss (BAY): như vũ khí thường, không cần bay qua. | Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.cs CanFire; Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.Bombs.cs StickStraddles, StickAllUnsafe, BombReach; Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.cs InReach |
| HV05 | so_bom_moi_luot | Loạt = Burst; lượt 2: dải STICK có minTargets mà quanh dải (nửa dải + rìa quanh mục tiêu) có ít hơn minTargets xe / công trình địch (và < 2 công trình) thì chỉ thả max(2, ceil(n/3)) quả (StickCount); máy bay có kho bom (load) thì loạt = min(loạt, số bom còn), chỉ trừ số đã thả. | Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.cs Operate; Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.Bombs.cs StickCount, StickBombs |
| HV06 | nhip_tha | Quả đầu thả ngay khi CanFire đúng; các quả sau mỗi SalvoGap: dải STICK = stick.interval (spacing / tốc độ lúc thả), khác = BurstInterval (bộ đếm theo bước 20 Hz). Sau dải, thời gian nạp = cooldown − (n−1) × (interval − burstInterval), nên chu kỳ từ dải này tới dải sau giữ nguyên. | Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.cs Operate; Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.Bombs.cs StickCooldown; Assets/MachineBrigade/Scripts/Sim/Content/WeaponDef.Stick.cs SalvoGap |
| HV07 | diem_nham_tung_qua | Lượt 2: quả đầu cố định dải (PlanStick): đầu dải = BombImpact lúc thả (vị trí máy bay + hướng mũi × tốc độ × thời gian rơi = khoảng dẫn đầu), hướng = hướng mũi; quả i rơi tại đầu dải + hướng × i × spacing (StickPoint), không bao giờ một điểm nhắm chung. Một quả rơi tự do (POINT n 1) vẫn nhắm BombImpact. | Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.cs Launch; Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.Bombs.cs PlanStick, StickLine, StickPoint, BombImpact |
| HV08 | diem_nham_bom_boss | Lượt 2: bom khoang của boss (p26_roc_roc_bombs, p26_roc_main_roc_bombs) là Projectile Bomb, stick.drop BAY: dải 8 quả đặt quanh điểm nhắm (CENTER), hướng = trục chính của cụm mục tiêu trong ±45° so với đường boss → điểm nhắm, không thì đường đó; quả i tại đầu dải + hướng × i × spacing; rơi ít nhất BombFall (thời gian bay cũ nếu dài hơn). Khoang vẫn nhả cách 0,3 s. | Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.cs Launch; Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.Bombs.cs BayStick, StickLine, AxisAt; Assets/MachineBrigade/Resources/Data/balance.json: weapons p26_roc_roc_bombs.stick |
| HV09 | diem_nham_bom_dan_duong | Bom dẫn đường (data guided hoặc form GuidedBomb: SDB, JDAM, UMPK): aimAt = mục tiêu (dẫn trước nếu mục tiêu chạy), độ tản thường theo tầm; bom lượn bay tới bằng tốc độ riêng. | Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.cs:805-806 LeadPoint; Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.cs:829; Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.cs:875-878; Assets/MachineBrigade/Scripts/Sim/Content/Definitions.cs:224 GuidedBomb |
| HV10 | tan_xa | Lượt 2: quả của dải STICK lệch theo seed (world Random) ±jitterAlong dọc và ±jitterAcross ngang dải (không còn vòng tản), × hệ số khinh khí cầu / đèn chiếu (Works.SpreadFactor). Bom rơi tự do POINT: vòng Spread × 0,5 như cũ. | Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.cs Launch; Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.Bombs.cs FreeFallScatter |
| HV11 | thoi_gian_roi | BombFall = √(2 × max(4, độ cao) / 40) (BombGravity 40 m/s², theo tỉ lệ bản đồ); bom có cảnh báo (≥ 400 kg) rơi không sớm hơn thời gian cảnh báo. | Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.cs:874, Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.cs:883; Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.Bombs.cs:25, Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.Bombs.cs:35 |
| HV12 | ngoi_no | Không có ngòi riêng: quả bom nổ khi hết thời gian bay tại điểm aim (UpdateProjectiles → Damage.ResolveImpact); bom chùm tung bom con ở đó. | Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.cs: UpdateProjectiles; Assets/MachineBrigade/Scripts/Sim/Combat/DamageSystem (ResolveImpact) NEED_CODE_CHECK |
| HV13 | an_toan_quan_ta | Lượt 2: dải STICK xét TỪNG quả: điểm rơi (sau lệch) trong stick.safety (+ bán kính xe) quanh xe mặt đất phe ta thì quả đó không thả; các quả khác giữ điểm của mình. Cả dải chỉ bị giữ lại khi mọi quả đều không an toàn. Bom rơi tự do POINT: StickNearOwn như cũ; bom khác: OwnNear quanh mục tiêu, lõi + 3 m. | Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.cs CanFire, Launch; Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.Bombs.cs StickAllUnsafe, StickNearOwn |
| HV14 | vong_lai | Lượt 2: thả quả đầu của dải STICK thì máy bay giữ hướng, tốc độ, độ cao trong stick.straightTime (dải / tốc độ + thời gian rơi + 1 s, và ≥ 40 m sau quả cuối) (StickStraightUntil); sau đó như cũ: kéo ra (RunExtending) khi gần / đã qua mục tiêu, xa hơn max(0,85 × tầm, 2,2 × bán kính quay) thì quay lại. Glide bomber quay đi trước khi tới mục tiêu. | Assets/MachineBrigade/Scripts/Sim/Movement/MovementSystem.cs DriveAeroplane; Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.Bombs.cs PlanStick; Assets/MachineBrigade/Scripts/Sim/Movement/MovementSystem.P25A.cs GlideAway |
| HV15 | tranh_nem_lai | Loạt > 1 quả ghi điểm vừa ném (_bombed) để BombWorth chấm thấp nơi đó lần sau. | Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.cs:567; Assets/MachineBrigade/Scripts/Sim/Combat/CombatSystem.cs:406 |
| HV16 | the_ho_tro_khong_kich | Airstrike: Count quả rải đều từ Point tới Point + hướng × Length (Lerp), lệch ngang ngẫu nhiên ±Radius/2, cách nhau Duration/(Count−1) s; máy bay bay với tốc độ Length/Duration. Đã là dải (không dồn một điểm). | Assets/MachineBrigade/Scripts/Sim/Strikes/StrikeSystem.cs:250-275 |
| HV17 | sieu_vu_khi_boss_strip | Strip: n quả cách đều dọc trục (−L/2 + L(k+0,5)/n), lệch ngang ±0,35 × W (khi không có interval), rơi trải trong Duration. Đã là dải. | Assets/MachineBrigade/Scripts/Sim/Bosses/BossSystem.BigAttacks.cs:708-720 (rơi), :492-505 (vùng cảnh báo) |
| HV18 | the_12_qua | Hướng dẫn của Oanh tạc cơ chiến lược nói 'thả một hàng 12 quả', dữ liệu bomber_payload có burst 7, load 7 (một lượt 7 quả). | Assets/MachineBrigade/Scripts/Game/Hud/GuideText.cs:410, :414; Assets/MachineBrigade/Resources/Data/balance.json: weapons bomber_payload |

## Bom_vet_tha

| id | chi_so_bom | tick_tha | vi_tri_tha_z_m | tick_cham | vi_tri_roi_x_m | vi_tri_roi_z_m | thoi_gian_roi_s | loai_dong | so_diem_roi_khac_nhau | khoang_cach_xa_nhat_m | do_dai_dai_m | do_lech_ngang_m | ty_le_chong_lan |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| air_raid/(the_ho_tro)/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 10.0 | 70.011 | 70.0 | 5.086 | 1.029 |
| airship_carpet/command_airship/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 16.0 | 75.055 | 75.0 | 7.745 | 1.4 |
| airstrike/(the_ho_tro)/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 4.0 | 60.091 | 60.0 | 3.957 | 0.5 |
| bomber_payload/heavy_bomber/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 7.0 | 65.757 | 65.68 | 4.616 | 0.914 |
| bunker_buster_bomb/glide_bomber/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| cluster_at_bomb/glide_bomber/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| cluster_strike/(the_ho_tro)/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 30.0 | 60.39 | 60.0 | 9.655 | 2.658 |
| garuda_carpet/garuda/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 20.0 | 95.124 | 95.0 | 9.355 | 1.4 |
| glide_fab500/glide_bomber/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| guided_bomb/morrigan/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| guided_bomb/stealth_fighter/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| guided_bomb/strike_drone/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| jet_bombs/attack_jet/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| jet_bombs/elite_attack_jet/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| jet_bombs/stealth_naval_strike/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 2.0 | 9.27 | 8.963 | 2.321 | 0.913 |
| kraken_air_raid/kraken/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 12.0 | 82.651 | 82.5 | 8.823 | 1.2 |
| napalm_strike/(the_ho_tro)/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 8.0 | 55.091 | 55.0 | 4.061 | 1.145 |
| p26_roc_main_roc_bombs/argus/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 8.0 | 76.835 | 76.816 | 4.616 | 0.911 |
| p26_roc_main_roc_bombs/command_airship/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 8.0 | 76.835 | 76.816 | 4.616 | 0.911 |
| p26_roc_main_roc_bombs/garuda/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 8.0 | 76.835 | 76.816 | 4.616 | 0.911 |
| stealth_payload/stealth_bomber/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 2.0 | 1.839 | 1.539 | 0.758 | 14.42 |
| thermobaric_bomb/glide_bomber/TONG_KET |  |  |  |  |  |  |  | TONG_KET_TB_3_SEED | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 |

(Chỉ các dòng tổng kết và CHUA_CHAY; từng quả trong xlsx / csv.)

## Bom_canh_bao

| id | nhom | co_vong | hinh_dang | dai_m | rong_m | ban_kinh_loi_m | ban_kinh_ria_m | thoi_gian_canh_bao_s |
|---|---|---|---|---|---|---|---|---|
| bomber_payload | vu_khi_don_vi | TRUE | 2 vòng tròn đồng tâm tại điểm rơi TỪNG quả (lõi, rìa = WarnRadius); các vòng của một loạt cùng bệ được gộp |  |  | 10.0 | 10.0 | 2.722 |
| bunker_buster_bomb | vu_khi_don_vi | TRUE | 2 vòng tròn đồng tâm tại điểm rơi TỪNG quả (lõi, rìa = WarnRadius); các vòng của một loạt cùng bệ được gộp |  |  | 6.0 | 6.0 | 2.5 |
| cluster_at_bomb | vu_khi_don_vi | TRUE | 2 vòng tròn đồng tâm tại điểm rơi TỪNG quả (lõi, rìa = WarnRadius); các vòng của một loạt cùng bệ được gộp |  |  | 3.0 | 3.0 | 2.5 |
| glide_fab500 | vu_khi_don_vi | FALSE | không có vòng |  |  | 10.0 |  | 0 |
| guided_bomb | vu_khi_don_vi | FALSE | không có vòng |  |  | 4.0 |  | 0 |
| jet_bombs | vu_khi_don_vi | FALSE | không có vòng |  |  | 8.0 |  | 0 |
| p26_roc_main_roc_bombs | vu_khi_don_vi | TRUE | 2 vòng tròn đồng tâm tại điểm rơi TỪNG quả (lõi, rìa = WarnRadius); các vòng của một loạt cùng bệ được gộp |  |  | 10.0 | 20.0 | 2.722 |
| p26_roc_roc_bombs | vu_khi_don_vi | TRUE | 2 vòng tròn đồng tâm tại điểm rơi TỪNG quả (lõi, rìa = WarnRadius); các vòng của một loạt cùng bệ được gộp |  |  | 5.0 | 10.0 | 2.5 |
| stealth_payload | vu_khi_don_vi | FALSE | không có vòng |  |  | 13.0 |  | 0 |
| thermobaric_bomb | vu_khi_don_vi | TRUE | 2 vòng tròn đồng tâm tại điểm rơi TỪNG quả (lõi, rìa = WarnRadius); các vòng của một loạt cùng bệ được gộp |  |  | 12.0 | 12.0 | 3.167 |
| air_raid | the_ho_tro | TRUE | dải dọc đường bay từ điểm chọn tới điểm + hướng × length | 70 | 12.0 |  | NEED_CODE_CHECK | 4.0 |
| airstrike | the_ho_tro | TRUE | dải dọc đường bay từ điểm chọn tới điểm + hướng × length | 60 | 12.0 |  | NEED_CODE_CHECK | 2.0 |
| cluster_at_strike | the_ho_tro | TRUE | vòng tròn quanh điểm chọn |  |  | 25 | NEED_CODE_CHECK | 2.0 |
| cluster_strike | the_ho_tro | TRUE | dải dọc đường bay từ điểm chọn tới điểm + hướng × length | 60 | 20.0 |  | NEED_CODE_CHECK | 2.5 |
| glide_bomb_strike | the_ho_tro | TRUE | vòng tròn quanh điểm chọn |  |  | 10 | NEED_CODE_CHECK | 3.0 |
| napalm_strike | the_ho_tro | TRUE | dải dọc đường bay từ điểm chọn tới điểm + hướng × length | 55 | 10.0 |  | NEED_CODE_CHECK | 2.0 |
| airship_carpet | sieu_vu_khi_boss | TRUE | hình chữ nhật dài × rộng theo hướng boss (BigZone) | 80 | 12 | 7 | NEED_CODE_CHECK | 4 |
| carrier_heavy_bomb | sieu_vu_khi_boss | TRUE | vòng tại điểm rơi |  |  | 16 | NEED_CODE_CHECK | 3.5 |
| garuda_carpet | sieu_vu_khi_boss | TRUE | hình chữ nhật dài × rộng theo hướng boss (BigZone) | 100 | 14 | 7 | NEED_CODE_CHECK | 4 |
| kraken_air_raid | sieu_vu_khi_boss | TRUE | hình chữ nhật dài × rộng theo hướng boss (BigZone) | 90 | 14 | 9 | NEED_CODE_CHECK | 4 |

## Bom_ket_qua_vung

| id | giai_doan | doi_hinh | so_bom | so_xe_trung_loi | so_xe_trung_ria | so_xe_trung | so_lan_trung_loi |
|---|---|---|---|---|---|---|---|
| SAU/air_raid/(the_ho_tro)/s1/HANG_DOC_8M | SAU_KHONG_DOI | HANG_DOC_8M | 10 | 5 | 0 | 5 | 10 |
| SAU/air_raid/(the_ho_tro)/s1/HANG_NGANG_8M | SAU_KHONG_DOI | HANG_NGANG_8M | 10 | 1 | 0 | 1 | 2 |
| SAU/air_raid/(the_ho_tro)/s1/CUM_8M | SAU_KHONG_DOI | CUM_8M | 10 | 5 | 0 | 5 | 6 |
| SAU/air_raid/(the_ho_tro)/s2/HANG_DOC_8M | SAU_KHONG_DOI | HANG_DOC_8M | 10 | 5 | 0 | 5 | 10 |
| SAU/air_raid/(the_ho_tro)/s2/HANG_NGANG_8M | SAU_KHONG_DOI | HANG_NGANG_8M | 10 | 2 | 0 | 2 | 3 |
| SAU/air_raid/(the_ho_tro)/s2/CUM_8M | SAU_KHONG_DOI | CUM_8M | 10 | 5 | 0 | 5 | 7 |
| SAU/air_raid/(the_ho_tro)/s3/HANG_DOC_8M | SAU_KHONG_DOI | HANG_DOC_8M | 10 | 5 | 0 | 5 | 10 |
| SAU/air_raid/(the_ho_tro)/s3/HANG_NGANG_8M | SAU_KHONG_DOI | HANG_NGANG_8M | 10 | 3 | 0 | 3 | 4 |
| SAU/air_raid/(the_ho_tro)/s3/CUM_8M | SAU_KHONG_DOI | CUM_8M | 10 | 5 | 0 | 5 | 7 |
| SAU/airship_carpet/command_airship/s1/HANG_DOC_8M | SAU_KHONG_DOI | HANG_DOC_8M | 16 | 5 | 0 | 5 | 14 |
| SAU/airship_carpet/command_airship/s1/HANG_NGANG_8M | SAU_KHONG_DOI | HANG_NGANG_8M | 16 | 3 | 2 | 5 | 4 |
| SAU/airship_carpet/command_airship/s1/CUM_8M | SAU_KHONG_DOI | CUM_8M | 16 | 5 | 0 | 5 | 10 |
| SAU/airship_carpet/command_airship/s2/HANG_DOC_8M | SAU_KHONG_DOI | HANG_DOC_8M | 16 | 5 | 0 | 5 | 13 |
| SAU/airship_carpet/command_airship/s2/HANG_NGANG_8M | SAU_KHONG_DOI | HANG_NGANG_8M | 16 | 2 | 1 | 3 | 3 |
| SAU/airship_carpet/command_airship/s2/CUM_8M | SAU_KHONG_DOI | CUM_8M | 16 | 5 | 0 | 5 | 11 |
| SAU/airship_carpet/command_airship/s3/HANG_DOC_8M | SAU_KHONG_DOI | HANG_DOC_8M | 16 | 5 | 0 | 5 | 13 |
| SAU/airship_carpet/command_airship/s3/HANG_NGANG_8M | SAU_KHONG_DOI | HANG_NGANG_8M | 16 | 3 | 1 | 4 | 4 |
| SAU/airship_carpet/command_airship/s3/CUM_8M | SAU_KHONG_DOI | CUM_8M | 16 | 5 | 0 | 5 | 10 |
| SAU/airstrike/(the_ho_tro)/s1/HANG_DOC_8M | SAU_KHONG_DOI | HANG_DOC_8M | 4 | 4 | 0 | 4 | 4 |
| SAU/airstrike/(the_ho_tro)/s1/HANG_NGANG_8M | SAU_KHONG_DOI | HANG_NGANG_8M | 4 | 0 | 0 | 0 | 0 |
| SAU/airstrike/(the_ho_tro)/s1/CUM_8M | SAU_KHONG_DOI | CUM_8M | 4 | 4 | 0 | 4 | 4 |
| SAU/airstrike/(the_ho_tro)/s2/HANG_DOC_8M | SAU_KHONG_DOI | HANG_DOC_8M | 4 | 4 | 0 | 4 | 4 |
| SAU/airstrike/(the_ho_tro)/s2/HANG_NGANG_8M | SAU_KHONG_DOI | HANG_NGANG_8M | 4 | 0 | 0 | 0 | 0 |
| SAU/airstrike/(the_ho_tro)/s2/CUM_8M | SAU_KHONG_DOI | CUM_8M | 4 | 4 | 0 | 4 | 4 |
| SAU/airstrike/(the_ho_tro)/s3/HANG_DOC_8M | SAU_KHONG_DOI | HANG_DOC_8M | 4 | 4 | 0 | 4 | 4 |
| SAU/airstrike/(the_ho_tro)/s3/HANG_NGANG_8M | SAU_KHONG_DOI | HANG_NGANG_8M | 4 | 0 | 0 | 0 | 0 |
| SAU/airstrike/(the_ho_tro)/s3/CUM_8M | SAU_KHONG_DOI | CUM_8M | 4 | 4 | 0 | 4 | 4 |
| SAU/bomber_payload/heavy_bomber/s1/HANG_DOC_8M | SAU | HANG_DOC_8M | 7 | 5 | 0 | 5 | 9 |
| SAU/bomber_payload/heavy_bomber/s1/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 7 | 2 | 0 | 2 | 3 |
| SAU/bomber_payload/heavy_bomber/s1/CUM_8M | SAU | CUM_8M | 7 | 5 | 0 | 5 | 10 |
| SAU/bomber_payload/heavy_bomber/s2/HANG_DOC_8M | SAU | HANG_DOC_8M | 7 | 5 | 0 | 5 | 10 |
| SAU/bomber_payload/heavy_bomber/s2/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 7 | 3 | 0 | 3 | 4 |
| SAU/bomber_payload/heavy_bomber/s2/CUM_8M | SAU | CUM_8M | 7 | 5 | 0 | 5 | 8 |
| SAU/bomber_payload/heavy_bomber/s3/HANG_DOC_8M | SAU | HANG_DOC_8M | 7 | 5 | 0 | 5 | 9 |
| SAU/bomber_payload/heavy_bomber/s3/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 7 | 2 | 0 | 2 | 3 |
| SAU/bomber_payload/heavy_bomber/s3/CUM_8M | SAU | CUM_8M | 7 | 5 | 0 | 5 | 9 |
| SAU/bunker_buster_bomb/glide_bomber/s1/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/bunker_buster_bomb/glide_bomber/s1/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/bunker_buster_bomb/glide_bomber/s1/CUM_8M | SAU | CUM_8M | 1 | 3 | 0 | 3 | 3 |
| SAU/bunker_buster_bomb/glide_bomber/s2/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/bunker_buster_bomb/glide_bomber/s2/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/bunker_buster_bomb/glide_bomber/s2/CUM_8M | SAU | CUM_8M | 1 | 3 | 0 | 3 | 3 |
| SAU/bunker_buster_bomb/glide_bomber/s3/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/bunker_buster_bomb/glide_bomber/s3/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/bunker_buster_bomb/glide_bomber/s3/CUM_8M | SAU | CUM_8M | 1 | 3 | 0 | 3 | 3 |
| SAU/cluster_at_bomb/glide_bomber/s1/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/cluster_at_bomb/glide_bomber/s1/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/cluster_at_bomb/glide_bomber/s1/CUM_8M | SAU | CUM_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/cluster_at_bomb/glide_bomber/s2/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/cluster_at_bomb/glide_bomber/s2/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/cluster_at_bomb/glide_bomber/s2/CUM_8M | SAU | CUM_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/cluster_at_bomb/glide_bomber/s3/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/cluster_at_bomb/glide_bomber/s3/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/cluster_at_bomb/glide_bomber/s3/CUM_8M | SAU | CUM_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/cluster_strike/(the_ho_tro)/s1/HANG_DOC_8M | SAU_KHONG_DOI | HANG_DOC_8M | 30 | 5 | 0 | 5 | 20 |
| SAU/cluster_strike/(the_ho_tro)/s1/HANG_NGANG_8M | SAU_KHONG_DOI | HANG_NGANG_8M | 30 | 3 | 0 | 3 | 6 |
| SAU/cluster_strike/(the_ho_tro)/s1/CUM_8M | SAU_KHONG_DOI | CUM_8M | 30 | 5 | 0 | 5 | 17 |
| SAU/cluster_strike/(the_ho_tro)/s2/HANG_DOC_8M | SAU_KHONG_DOI | HANG_DOC_8M | 30 | 5 | 0 | 5 | 22 |
| SAU/cluster_strike/(the_ho_tro)/s2/HANG_NGANG_8M | SAU_KHONG_DOI | HANG_NGANG_8M | 30 | 2 | 0 | 2 | 7 |
| SAU/cluster_strike/(the_ho_tro)/s2/CUM_8M | SAU_KHONG_DOI | CUM_8M | 30 | 5 | 0 | 5 | 18 |
| SAU/cluster_strike/(the_ho_tro)/s3/HANG_DOC_8M | SAU_KHONG_DOI | HANG_DOC_8M | 30 | 5 | 0 | 5 | 23 |
| SAU/cluster_strike/(the_ho_tro)/s3/HANG_NGANG_8M | SAU_KHONG_DOI | HANG_NGANG_8M | 30 | 2 | 0 | 2 | 5 |
| SAU/cluster_strike/(the_ho_tro)/s3/CUM_8M | SAU_KHONG_DOI | CUM_8M | 30 | 5 | 0 | 5 | 17 |
| SAU/garuda_carpet/garuda/s1/HANG_DOC_8M | SAU_KHONG_DOI | HANG_DOC_8M | 20 | 5 | 0 | 5 | 13 |
| SAU/garuda_carpet/garuda/s1/HANG_NGANG_8M | SAU_KHONG_DOI | HANG_NGANG_8M | 20 | 3 | 2 | 5 | 4 |
| SAU/garuda_carpet/garuda/s1/CUM_8M | SAU_KHONG_DOI | CUM_8M | 20 | 5 | 0 | 5 | 9 |
| SAU/garuda_carpet/garuda/s2/HANG_DOC_8M | SAU_KHONG_DOI | HANG_DOC_8M | 20 | 5 | 0 | 5 | 14 |
| SAU/garuda_carpet/garuda/s2/HANG_NGANG_8M | SAU_KHONG_DOI | HANG_NGANG_8M | 20 | 1 | 2 | 3 | 2 |
| SAU/garuda_carpet/garuda/s2/CUM_8M | SAU_KHONG_DOI | CUM_8M | 20 | 5 | 0 | 5 | 9 |
| SAU/garuda_carpet/garuda/s3/HANG_DOC_8M | SAU_KHONG_DOI | HANG_DOC_8M | 20 | 5 | 0 | 5 | 12 |
| SAU/garuda_carpet/garuda/s3/HANG_NGANG_8M | SAU_KHONG_DOI | HANG_NGANG_8M | 20 | 3 | 2 | 5 | 4 |
| SAU/garuda_carpet/garuda/s3/CUM_8M | SAU_KHONG_DOI | CUM_8M | 20 | 5 | 0 | 5 | 10 |
| SAU/glide_fab500/glide_bomber/s1/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 3 | 0 | 3 | 3 |
| SAU/glide_fab500/glide_bomber/s1/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 3 | 0 | 3 | 3 |
| SAU/glide_fab500/glide_bomber/s1/CUM_8M | SAU | CUM_8M | 1 | 5 | 0 | 5 | 5 |
| SAU/glide_fab500/glide_bomber/s2/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 3 | 0 | 3 | 3 |
| SAU/glide_fab500/glide_bomber/s2/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 3 | 0 | 3 | 3 |
| SAU/glide_fab500/glide_bomber/s2/CUM_8M | SAU | CUM_8M | 1 | 5 | 0 | 5 | 5 |
| SAU/glide_fab500/glide_bomber/s3/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 3 | 0 | 3 | 3 |
| SAU/glide_fab500/glide_bomber/s3/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 3 | 0 | 3 | 3 |
| SAU/glide_fab500/glide_bomber/s3/CUM_8M | SAU | CUM_8M | 1 | 5 | 0 | 5 | 5 |
| SAU/guided_bomb/morrigan/s1/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 1 | 1 | 2 | 1 |
| SAU/guided_bomb/morrigan/s1/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/guided_bomb/morrigan/s1/CUM_8M | SAU | CUM_8M | 1 | 1 | 4 | 5 | 1 |
| SAU/guided_bomb/morrigan/s2/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 1 | 1 | 2 | 1 |
| SAU/guided_bomb/morrigan/s2/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 1 | 1 | 2 | 1 |
| SAU/guided_bomb/morrigan/s2/CUM_8M | SAU | CUM_8M | 1 | 1 | 4 | 5 | 1 |
| SAU/guided_bomb/morrigan/s3/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 1 | 1 | 2 | 1 |
| SAU/guided_bomb/morrigan/s3/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 1 | 1 | 2 | 1 |
| SAU/guided_bomb/morrigan/s3/CUM_8M | SAU | CUM_8M | 1 | 1 | 4 | 5 | 1 |
| SAU/guided_bomb/stealth_fighter/s1/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/guided_bomb/stealth_fighter/s1/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/guided_bomb/stealth_fighter/s1/CUM_8M | SAU | CUM_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/guided_bomb/stealth_fighter/s2/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/guided_bomb/stealth_fighter/s2/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/guided_bomb/stealth_fighter/s2/CUM_8M | SAU | CUM_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/guided_bomb/stealth_fighter/s3/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/guided_bomb/stealth_fighter/s3/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/guided_bomb/stealth_fighter/s3/CUM_8M | SAU | CUM_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/guided_bomb/strike_drone/s1/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/guided_bomb/strike_drone/s1/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/guided_bomb/strike_drone/s1/CUM_8M | SAU | CUM_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/guided_bomb/strike_drone/s2/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/guided_bomb/strike_drone/s2/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/guided_bomb/strike_drone/s2/CUM_8M | SAU | CUM_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/guided_bomb/strike_drone/s3/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/guided_bomb/strike_drone/s3/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/guided_bomb/strike_drone/s3/CUM_8M | SAU | CUM_8M | 1 | 1 | 0 | 1 | 1 |
| SAU/jet_bombs/attack_jet/s1/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 2 | 0 | 2 | 2 |
| SAU/jet_bombs/attack_jet/s1/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 2 | 0 | 2 | 2 |
| SAU/jet_bombs/attack_jet/s1/CUM_8M | SAU | CUM_8M | 1 | 4 | 0 | 4 | 4 |
| SAU/jet_bombs/attack_jet/s2/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 2 | 0 | 2 | 2 |
| SAU/jet_bombs/attack_jet/s2/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 2 | 0 | 2 | 2 |
| SAU/jet_bombs/attack_jet/s2/CUM_8M | SAU | CUM_8M | 1 | 5 | 0 | 5 | 5 |
| SAU/jet_bombs/attack_jet/s3/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 2 | 0 | 2 | 2 |
| SAU/jet_bombs/attack_jet/s3/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 2 | 0 | 2 | 2 |
| SAU/jet_bombs/attack_jet/s3/CUM_8M | SAU | CUM_8M | 1 | 5 | 0 | 5 | 5 |
| SAU/jet_bombs/elite_attack_jet/s1/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 2 | 0 | 2 | 2 |
| SAU/jet_bombs/elite_attack_jet/s1/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 2 | 0 | 2 | 2 |
| SAU/jet_bombs/elite_attack_jet/s1/CUM_8M | SAU | CUM_8M | 1 | 4 | 0 | 4 | 4 |
| SAU/jet_bombs/elite_attack_jet/s2/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 2 | 0 | 2 | 2 |
| SAU/jet_bombs/elite_attack_jet/s2/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 2 | 0 | 2 | 2 |
| SAU/jet_bombs/elite_attack_jet/s2/CUM_8M | SAU | CUM_8M | 1 | 5 | 0 | 5 | 5 |
| SAU/jet_bombs/elite_attack_jet/s3/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 2 | 0 | 2 | 2 |
| SAU/jet_bombs/elite_attack_jet/s3/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 2 | 0 | 2 | 2 |
| SAU/jet_bombs/elite_attack_jet/s3/CUM_8M | SAU | CUM_8M | 1 | 5 | 0 | 5 | 5 |
| SAU/jet_bombs/stealth_naval_strike/s1/HANG_DOC_8M | SAU | HANG_DOC_8M | 2 | 3 | 0 | 3 | 4 |
| SAU/jet_bombs/stealth_naval_strike/s1/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 2 | 2 | 0 | 2 | 3 |
| SAU/jet_bombs/stealth_naval_strike/s1/CUM_8M | SAU | CUM_8M | 2 | 5 | 0 | 5 | 7 |
| SAU/jet_bombs/stealth_naval_strike/s2/HANG_DOC_8M | SAU | HANG_DOC_8M | 2 | 3 | 0 | 3 | 4 |
| SAU/jet_bombs/stealth_naval_strike/s2/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 2 | 2 | 0 | 2 | 3 |
| SAU/jet_bombs/stealth_naval_strike/s2/CUM_8M | SAU | CUM_8M | 2 | 5 | 0 | 5 | 7 |
| SAU/jet_bombs/stealth_naval_strike/s3/HANG_DOC_8M | SAU | HANG_DOC_8M | 2 | 3 | 0 | 3 | 4 |
| SAU/jet_bombs/stealth_naval_strike/s3/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 2 | 2 | 0 | 2 | 3 |
| SAU/jet_bombs/stealth_naval_strike/s3/CUM_8M | SAU | CUM_8M | 2 | 5 | 0 | 5 | 6 |
| SAU/kraken_air_raid/kraken/s1/HANG_DOC_8M | SAU_KHONG_DOI | HANG_DOC_8M | 12 | 5 | 0 | 5 | 10 |
| SAU/kraken_air_raid/kraken/s1/HANG_NGANG_8M | SAU_KHONG_DOI | HANG_NGANG_8M | 12 | 3 | 2 | 5 | 4 |
| SAU/kraken_air_raid/kraken/s1/CUM_8M | SAU_KHONG_DOI | CUM_8M | 12 | 5 | 0 | 5 | 12 |
| SAU/kraken_air_raid/kraken/s2/HANG_DOC_8M | SAU_KHONG_DOI | HANG_DOC_8M | 12 | 5 | 0 | 5 | 10 |
| SAU/kraken_air_raid/kraken/s2/HANG_NGANG_8M | SAU_KHONG_DOI | HANG_NGANG_8M | 12 | 2 | 2 | 4 | 4 |
| SAU/kraken_air_raid/kraken/s2/CUM_8M | SAU_KHONG_DOI | CUM_8M | 12 | 5 | 0 | 5 | 10 |
| SAU/kraken_air_raid/kraken/s3/HANG_DOC_8M | SAU_KHONG_DOI | HANG_DOC_8M | 12 | 5 | 0 | 5 | 10 |
| SAU/kraken_air_raid/kraken/s3/HANG_NGANG_8M | SAU_KHONG_DOI | HANG_NGANG_8M | 12 | 2 | 3 | 5 | 4 |
| SAU/kraken_air_raid/kraken/s3/CUM_8M | SAU_KHONG_DOI | CUM_8M | 12 | 5 | 0 | 5 | 11 |
| SAU/napalm_strike/(the_ho_tro)/s1/HANG_DOC_8M | SAU_KHONG_DOI | HANG_DOC_8M | 8 | 5 | 0 | 5 | 10 |
| SAU/napalm_strike/(the_ho_tro)/s1/HANG_NGANG_8M | SAU_KHONG_DOI | HANG_NGANG_8M | 8 | 2 | 0 | 2 | 4 |
| SAU/napalm_strike/(the_ho_tro)/s1/CUM_8M | SAU_KHONG_DOI | CUM_8M | 8 | 5 | 0 | 5 | 11 |
| SAU/napalm_strike/(the_ho_tro)/s2/HANG_DOC_8M | SAU_KHONG_DOI | HANG_DOC_8M | 8 | 5 | 0 | 5 | 10 |
| SAU/napalm_strike/(the_ho_tro)/s2/HANG_NGANG_8M | SAU_KHONG_DOI | HANG_NGANG_8M | 8 | 3 | 0 | 3 | 4 |
| SAU/napalm_strike/(the_ho_tro)/s2/CUM_8M | SAU_KHONG_DOI | CUM_8M | 8 | 5 | 0 | 5 | 10 |
| SAU/napalm_strike/(the_ho_tro)/s3/HANG_DOC_8M | SAU_KHONG_DOI | HANG_DOC_8M | 8 | 5 | 0 | 5 | 10 |
| SAU/napalm_strike/(the_ho_tro)/s3/HANG_NGANG_8M | SAU_KHONG_DOI | HANG_NGANG_8M | 8 | 2 | 0 | 2 | 4 |
| SAU/napalm_strike/(the_ho_tro)/s3/CUM_8M | SAU_KHONG_DOI | CUM_8M | 8 | 5 | 0 | 5 | 11 |
| SAU/p26_roc_main_roc_bombs/argus/s1/HANG_DOC_8M | SAU | HANG_DOC_8M | 8 | 5 | 0 | 5 | 8 |
| SAU/p26_roc_main_roc_bombs/argus/s1/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 8 | 3 | 2 | 5 | 5 |
| SAU/p26_roc_main_roc_bombs/argus/s1/CUM_8M | SAU | CUM_8M | 8 | 5 | 0 | 5 | 8 |
| SAU/p26_roc_main_roc_bombs/argus/s2/HANG_DOC_8M | SAU | HANG_DOC_8M | 8 | 5 | 0 | 5 | 9 |
| SAU/p26_roc_main_roc_bombs/argus/s2/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 8 | 3 | 2 | 5 | 5 |
| SAU/p26_roc_main_roc_bombs/argus/s2/CUM_8M | SAU | CUM_8M | 8 | 5 | 0 | 5 | 9 |
| SAU/p26_roc_main_roc_bombs/argus/s3/HANG_DOC_8M | SAU | HANG_DOC_8M | 8 | 5 | 0 | 5 | 9 |
| SAU/p26_roc_main_roc_bombs/argus/s3/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 8 | 3 | 2 | 5 | 5 |
| SAU/p26_roc_main_roc_bombs/argus/s3/CUM_8M | SAU | CUM_8M | 8 | 5 | 0 | 5 | 7 |
| SAU/p26_roc_main_roc_bombs/command_airship/s1/HANG_DOC_8M | SAU | HANG_DOC_8M | 8 | 5 | 0 | 5 | 8 |
| SAU/p26_roc_main_roc_bombs/command_airship/s1/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 8 | 3 | 2 | 5 | 5 |
| SAU/p26_roc_main_roc_bombs/command_airship/s1/CUM_8M | SAU | CUM_8M | 8 | 5 | 0 | 5 | 8 |
| SAU/p26_roc_main_roc_bombs/command_airship/s2/HANG_DOC_8M | SAU | HANG_DOC_8M | 8 | 5 | 0 | 5 | 9 |
| SAU/p26_roc_main_roc_bombs/command_airship/s2/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 8 | 3 | 2 | 5 | 5 |
| SAU/p26_roc_main_roc_bombs/command_airship/s2/CUM_8M | SAU | CUM_8M | 8 | 5 | 0 | 5 | 9 |
| SAU/p26_roc_main_roc_bombs/command_airship/s3/HANG_DOC_8M | SAU | HANG_DOC_8M | 8 | 5 | 0 | 5 | 9 |
| SAU/p26_roc_main_roc_bombs/command_airship/s3/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 8 | 3 | 2 | 5 | 5 |
| SAU/p26_roc_main_roc_bombs/command_airship/s3/CUM_8M | SAU | CUM_8M | 8 | 5 | 0 | 5 | 7 |
| SAU/p26_roc_main_roc_bombs/garuda/s1/HANG_DOC_8M | SAU | HANG_DOC_8M | 8 | 5 | 0 | 5 | 8 |
| SAU/p26_roc_main_roc_bombs/garuda/s1/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 8 | 3 | 2 | 5 | 5 |
| SAU/p26_roc_main_roc_bombs/garuda/s1/CUM_8M | SAU | CUM_8M | 8 | 5 | 0 | 5 | 8 |
| SAU/p26_roc_main_roc_bombs/garuda/s2/HANG_DOC_8M | SAU | HANG_DOC_8M | 8 | 5 | 0 | 5 | 9 |
| SAU/p26_roc_main_roc_bombs/garuda/s2/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 8 | 3 | 2 | 5 | 5 |
| SAU/p26_roc_main_roc_bombs/garuda/s2/CUM_8M | SAU | CUM_8M | 8 | 5 | 0 | 5 | 9 |
| SAU/p26_roc_main_roc_bombs/garuda/s3/HANG_DOC_8M | SAU | HANG_DOC_8M | 8 | 5 | 0 | 5 | 9 |
| SAU/p26_roc_main_roc_bombs/garuda/s3/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 8 | 3 | 2 | 5 | 5 |
| SAU/p26_roc_main_roc_bombs/garuda/s3/CUM_8M | SAU | CUM_8M | 8 | 5 | 0 | 5 | 7 |
| SAU/stealth_payload/stealth_bomber/s1/HANG_DOC_8M | SAU | HANG_DOC_8M | 2 | 3 | 0 | 3 | 6 |
| SAU/stealth_payload/stealth_bomber/s1/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 2 | 3 | 0 | 3 | 6 |
| SAU/stealth_payload/stealth_bomber/s1/CUM_8M | SAU | CUM_8M | 2 | 5 | 0 | 5 | 10 |
| SAU/stealth_payload/stealth_bomber/s2/HANG_DOC_8M | SAU | HANG_DOC_8M | 2 | 3 | 0 | 3 | 6 |
| SAU/stealth_payload/stealth_bomber/s2/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 2 | 3 | 0 | 3 | 6 |
| SAU/stealth_payload/stealth_bomber/s2/CUM_8M | SAU | CUM_8M | 2 | 5 | 0 | 5 | 10 |
| SAU/stealth_payload/stealth_bomber/s3/HANG_DOC_8M | SAU | HANG_DOC_8M | 2 | 3 | 0 | 3 | 6 |
| SAU/stealth_payload/stealth_bomber/s3/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 2 | 3 | 0 | 3 | 6 |
| SAU/stealth_payload/stealth_bomber/s3/CUM_8M | SAU | CUM_8M | 2 | 5 | 0 | 5 | 10 |
| SAU/thermobaric_bomb/glide_bomber/s1/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 3 | 0 | 3 | 3 |
| SAU/thermobaric_bomb/glide_bomber/s1/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 3 | 0 | 3 | 3 |
| SAU/thermobaric_bomb/glide_bomber/s1/CUM_8M | SAU | CUM_8M | 1 | 5 | 0 | 5 | 5 |
| SAU/thermobaric_bomb/glide_bomber/s2/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 3 | 0 | 3 | 3 |
| SAU/thermobaric_bomb/glide_bomber/s2/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 3 | 0 | 3 | 3 |
| SAU/thermobaric_bomb/glide_bomber/s2/CUM_8M | SAU | CUM_8M | 1 | 5 | 0 | 5 | 5 |
| SAU/thermobaric_bomb/glide_bomber/s3/HANG_DOC_8M | SAU | HANG_DOC_8M | 1 | 3 | 0 | 3 | 3 |
| SAU/thermobaric_bomb/glide_bomber/s3/HANG_NGANG_8M | SAU | HANG_NGANG_8M | 1 | 3 | 0 | 3 | 3 |
| SAU/thermobaric_bomb/glide_bomber/s3/CUM_8M | SAU | CUM_8M | 1 | 5 | 0 | 5 | 5 |
| TRUOC/air_raid/(the_ho_tro)/s1/HANG_DOC_8M | TRUOC_KHONG_DOI | HANG_DOC_8M | 10 | 5 | 0 | 5 | 10 |
| TRUOC/air_raid/(the_ho_tro)/s1/HANG_NGANG_8M | TRUOC_KHONG_DOI | HANG_NGANG_8M | 10 | 1 | 0 | 1 | 2 |
| TRUOC/air_raid/(the_ho_tro)/s1/CUM_8M | TRUOC_KHONG_DOI | CUM_8M | 10 | 5 | 0 | 5 | 6 |
| TRUOC/air_raid/(the_ho_tro)/s2/HANG_DOC_8M | TRUOC_KHONG_DOI | HANG_DOC_8M | 10 | 5 | 0 | 5 | 10 |
| TRUOC/air_raid/(the_ho_tro)/s2/HANG_NGANG_8M | TRUOC_KHONG_DOI | HANG_NGANG_8M | 10 | 2 | 0 | 2 | 3 |
| TRUOC/air_raid/(the_ho_tro)/s2/CUM_8M | TRUOC_KHONG_DOI | CUM_8M | 10 | 5 | 0 | 5 | 7 |
| TRUOC/air_raid/(the_ho_tro)/s3/HANG_DOC_8M | TRUOC_KHONG_DOI | HANG_DOC_8M | 10 | 5 | 0 | 5 | 10 |
| TRUOC/air_raid/(the_ho_tro)/s3/HANG_NGANG_8M | TRUOC_KHONG_DOI | HANG_NGANG_8M | 10 | 3 | 0 | 3 | 4 |
| TRUOC/air_raid/(the_ho_tro)/s3/CUM_8M | TRUOC_KHONG_DOI | CUM_8M | 10 | 5 | 0 | 5 | 7 |
| TRUOC/airship_carpet/command_airship/s1/HANG_DOC_8M | TRUOC_KHONG_DOI | HANG_DOC_8M | 16 | 5 | 0 | 5 | 14 |
| TRUOC/airship_carpet/command_airship/s1/HANG_NGANG_8M | TRUOC_KHONG_DOI | HANG_NGANG_8M | 16 | 3 | 2 | 5 | 4 |
| TRUOC/airship_carpet/command_airship/s1/CUM_8M | TRUOC_KHONG_DOI | CUM_8M | 16 | 5 | 0 | 5 | 10 |
| TRUOC/airship_carpet/command_airship/s2/HANG_DOC_8M | TRUOC_KHONG_DOI | HANG_DOC_8M | 16 | 5 | 0 | 5 | 13 |
| TRUOC/airship_carpet/command_airship/s2/HANG_NGANG_8M | TRUOC_KHONG_DOI | HANG_NGANG_8M | 16 | 2 | 1 | 3 | 3 |
| TRUOC/airship_carpet/command_airship/s2/CUM_8M | TRUOC_KHONG_DOI | CUM_8M | 16 | 5 | 0 | 5 | 11 |
| TRUOC/airship_carpet/command_airship/s3/HANG_DOC_8M | TRUOC_KHONG_DOI | HANG_DOC_8M | 16 | 5 | 0 | 5 | 13 |
| TRUOC/airship_carpet/command_airship/s3/HANG_NGANG_8M | TRUOC_KHONG_DOI | HANG_NGANG_8M | 16 | 3 | 1 | 4 | 4 |
| TRUOC/airship_carpet/command_airship/s3/CUM_8M | TRUOC_KHONG_DOI | CUM_8M | 16 | 5 | 0 | 5 | 10 |
| TRUOC/airstrike/(the_ho_tro)/s1/HANG_DOC_8M | TRUOC_KHONG_DOI | HANG_DOC_8M | 4 | 4 | 0 | 4 | 4 |
| TRUOC/airstrike/(the_ho_tro)/s1/HANG_NGANG_8M | TRUOC_KHONG_DOI | HANG_NGANG_8M | 4 | 0 | 0 | 0 | 0 |
| TRUOC/airstrike/(the_ho_tro)/s1/CUM_8M | TRUOC_KHONG_DOI | CUM_8M | 4 | 4 | 0 | 4 | 4 |
| TRUOC/airstrike/(the_ho_tro)/s2/HANG_DOC_8M | TRUOC_KHONG_DOI | HANG_DOC_8M | 4 | 4 | 0 | 4 | 4 |
| TRUOC/airstrike/(the_ho_tro)/s2/HANG_NGANG_8M | TRUOC_KHONG_DOI | HANG_NGANG_8M | 4 | 0 | 0 | 0 | 0 |
| TRUOC/airstrike/(the_ho_tro)/s2/CUM_8M | TRUOC_KHONG_DOI | CUM_8M | 4 | 4 | 0 | 4 | 4 |
| TRUOC/airstrike/(the_ho_tro)/s3/HANG_DOC_8M | TRUOC_KHONG_DOI | HANG_DOC_8M | 4 | 4 | 0 | 4 | 4 |
| TRUOC/airstrike/(the_ho_tro)/s3/HANG_NGANG_8M | TRUOC_KHONG_DOI | HANG_NGANG_8M | 4 | 0 | 0 | 0 | 0 |
| TRUOC/airstrike/(the_ho_tro)/s3/CUM_8M | TRUOC_KHONG_DOI | CUM_8M | 4 | 4 | 0 | 4 | 4 |
| TRUOC/bomber_payload/heavy_bomber/s1/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 7 | 5 | 0 | 5 | 18 |
| TRUOC/bomber_payload/heavy_bomber/s1/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 7 | 3 | 0 | 3 | 11 |
| TRUOC/bomber_payload/heavy_bomber/s1/CUM_8M | TRUOC | CUM_8M | 7 | 5 | 0 | 5 | 24 |
| TRUOC/bomber_payload/heavy_bomber/s2/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 7 | 4 | 0 | 4 | 17 |
| TRUOC/bomber_payload/heavy_bomber/s2/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 7 | 3 | 0 | 3 | 15 |
| TRUOC/bomber_payload/heavy_bomber/s2/CUM_8M | TRUOC | CUM_8M | 7 | 5 | 0 | 5 | 27 |
| TRUOC/bomber_payload/heavy_bomber/s3/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 7 | 4 | 0 | 4 | 15 |
| TRUOC/bomber_payload/heavy_bomber/s3/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 7 | 3 | 0 | 3 | 13 |
| TRUOC/bomber_payload/heavy_bomber/s3/CUM_8M | TRUOC | CUM_8M | 7 | 5 | 0 | 5 | 28 |
| TRUOC/bunker_buster_bomb/glide_bomber/s1/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/bunker_buster_bomb/glide_bomber/s1/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/bunker_buster_bomb/glide_bomber/s1/CUM_8M | TRUOC | CUM_8M | 1 | 3 | 0 | 3 | 3 |
| TRUOC/bunker_buster_bomb/glide_bomber/s2/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/bunker_buster_bomb/glide_bomber/s2/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/bunker_buster_bomb/glide_bomber/s2/CUM_8M | TRUOC | CUM_8M | 1 | 3 | 0 | 3 | 3 |
| TRUOC/bunker_buster_bomb/glide_bomber/s3/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/bunker_buster_bomb/glide_bomber/s3/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/bunker_buster_bomb/glide_bomber/s3/CUM_8M | TRUOC | CUM_8M | 1 | 3 | 0 | 3 | 3 |
| TRUOC/cluster_at_bomb/glide_bomber/s1/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/cluster_at_bomb/glide_bomber/s1/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/cluster_at_bomb/glide_bomber/s1/CUM_8M | TRUOC | CUM_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/cluster_at_bomb/glide_bomber/s2/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/cluster_at_bomb/glide_bomber/s2/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/cluster_at_bomb/glide_bomber/s2/CUM_8M | TRUOC | CUM_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/cluster_at_bomb/glide_bomber/s3/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/cluster_at_bomb/glide_bomber/s3/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/cluster_at_bomb/glide_bomber/s3/CUM_8M | TRUOC | CUM_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/cluster_strike/(the_ho_tro)/s1/HANG_DOC_8M | TRUOC_KHONG_DOI | HANG_DOC_8M | 30 | 5 | 0 | 5 | 20 |
| TRUOC/cluster_strike/(the_ho_tro)/s1/HANG_NGANG_8M | TRUOC_KHONG_DOI | HANG_NGANG_8M | 30 | 3 | 0 | 3 | 6 |
| TRUOC/cluster_strike/(the_ho_tro)/s1/CUM_8M | TRUOC_KHONG_DOI | CUM_8M | 30 | 5 | 0 | 5 | 17 |
| TRUOC/cluster_strike/(the_ho_tro)/s2/HANG_DOC_8M | TRUOC_KHONG_DOI | HANG_DOC_8M | 30 | 5 | 0 | 5 | 22 |
| TRUOC/cluster_strike/(the_ho_tro)/s2/HANG_NGANG_8M | TRUOC_KHONG_DOI | HANG_NGANG_8M | 30 | 2 | 0 | 2 | 7 |
| TRUOC/cluster_strike/(the_ho_tro)/s2/CUM_8M | TRUOC_KHONG_DOI | CUM_8M | 30 | 5 | 0 | 5 | 18 |
| TRUOC/cluster_strike/(the_ho_tro)/s3/HANG_DOC_8M | TRUOC_KHONG_DOI | HANG_DOC_8M | 30 | 5 | 0 | 5 | 23 |
| TRUOC/cluster_strike/(the_ho_tro)/s3/HANG_NGANG_8M | TRUOC_KHONG_DOI | HANG_NGANG_8M | 30 | 2 | 0 | 2 | 5 |
| TRUOC/cluster_strike/(the_ho_tro)/s3/CUM_8M | TRUOC_KHONG_DOI | CUM_8M | 30 | 5 | 0 | 5 | 17 |
| TRUOC/garuda_carpet/garuda/s1/HANG_DOC_8M | TRUOC_KHONG_DOI | HANG_DOC_8M | 20 | 5 | 0 | 5 | 13 |
| TRUOC/garuda_carpet/garuda/s1/HANG_NGANG_8M | TRUOC_KHONG_DOI | HANG_NGANG_8M | 20 | 3 | 2 | 5 | 4 |
| TRUOC/garuda_carpet/garuda/s1/CUM_8M | TRUOC_KHONG_DOI | CUM_8M | 20 | 5 | 0 | 5 | 9 |
| TRUOC/garuda_carpet/garuda/s2/HANG_DOC_8M | TRUOC_KHONG_DOI | HANG_DOC_8M | 20 | 5 | 0 | 5 | 14 |
| TRUOC/garuda_carpet/garuda/s2/HANG_NGANG_8M | TRUOC_KHONG_DOI | HANG_NGANG_8M | 20 | 1 | 2 | 3 | 2 |
| TRUOC/garuda_carpet/garuda/s2/CUM_8M | TRUOC_KHONG_DOI | CUM_8M | 20 | 5 | 0 | 5 | 9 |
| TRUOC/garuda_carpet/garuda/s3/HANG_DOC_8M | TRUOC_KHONG_DOI | HANG_DOC_8M | 20 | 5 | 0 | 5 | 12 |
| TRUOC/garuda_carpet/garuda/s3/HANG_NGANG_8M | TRUOC_KHONG_DOI | HANG_NGANG_8M | 20 | 3 | 2 | 5 | 4 |
| TRUOC/garuda_carpet/garuda/s3/CUM_8M | TRUOC_KHONG_DOI | CUM_8M | 20 | 5 | 0 | 5 | 10 |
| TRUOC/glide_fab500/glide_bomber/s1/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 3 | 0 | 3 | 3 |
| TRUOC/glide_fab500/glide_bomber/s1/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 3 | 0 | 3 | 3 |
| TRUOC/glide_fab500/glide_bomber/s1/CUM_8M | TRUOC | CUM_8M | 1 | 5 | 0 | 5 | 5 |
| TRUOC/glide_fab500/glide_bomber/s2/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 3 | 0 | 3 | 3 |
| TRUOC/glide_fab500/glide_bomber/s2/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 3 | 0 | 3 | 3 |
| TRUOC/glide_fab500/glide_bomber/s2/CUM_8M | TRUOC | CUM_8M | 1 | 5 | 0 | 5 | 5 |
| TRUOC/glide_fab500/glide_bomber/s3/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 3 | 0 | 3 | 3 |
| TRUOC/glide_fab500/glide_bomber/s3/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 3 | 0 | 3 | 3 |
| TRUOC/glide_fab500/glide_bomber/s3/CUM_8M | TRUOC | CUM_8M | 1 | 5 | 0 | 5 | 5 |
| TRUOC/guided_bomb/morrigan/s1/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 1 | 1 | 2 | 1 |
| TRUOC/guided_bomb/morrigan/s1/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/guided_bomb/morrigan/s1/CUM_8M | TRUOC | CUM_8M | 1 | 1 | 4 | 5 | 1 |
| TRUOC/guided_bomb/morrigan/s2/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 1 | 1 | 2 | 1 |
| TRUOC/guided_bomb/morrigan/s2/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 1 | 1 | 2 | 1 |
| TRUOC/guided_bomb/morrigan/s2/CUM_8M | TRUOC | CUM_8M | 1 | 1 | 4 | 5 | 1 |
| TRUOC/guided_bomb/morrigan/s3/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 1 | 1 | 2 | 1 |
| TRUOC/guided_bomb/morrigan/s3/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 1 | 1 | 2 | 1 |
| TRUOC/guided_bomb/morrigan/s3/CUM_8M | TRUOC | CUM_8M | 1 | 1 | 4 | 5 | 1 |
| TRUOC/guided_bomb/stealth_fighter/s1/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/guided_bomb/stealth_fighter/s1/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/guided_bomb/stealth_fighter/s1/CUM_8M | TRUOC | CUM_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/guided_bomb/stealth_fighter/s2/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/guided_bomb/stealth_fighter/s2/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/guided_bomb/stealth_fighter/s2/CUM_8M | TRUOC | CUM_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/guided_bomb/stealth_fighter/s3/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/guided_bomb/stealth_fighter/s3/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/guided_bomb/stealth_fighter/s3/CUM_8M | TRUOC | CUM_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/guided_bomb/strike_drone/s1/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/guided_bomb/strike_drone/s1/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/guided_bomb/strike_drone/s1/CUM_8M | TRUOC | CUM_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/guided_bomb/strike_drone/s2/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/guided_bomb/strike_drone/s2/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/guided_bomb/strike_drone/s2/CUM_8M | TRUOC | CUM_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/guided_bomb/strike_drone/s3/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/guided_bomb/strike_drone/s3/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/guided_bomb/strike_drone/s3/CUM_8M | TRUOC | CUM_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/jet_bombs/attack_jet/s1/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 2 | 0 | 2 | 2 |
| TRUOC/jet_bombs/attack_jet/s1/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/jet_bombs/attack_jet/s1/CUM_8M | TRUOC | CUM_8M | 1 | 5 | 0 | 5 | 5 |
| TRUOC/jet_bombs/attack_jet/s2/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 2 | 0 | 2 | 2 |
| TRUOC/jet_bombs/attack_jet/s2/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/jet_bombs/attack_jet/s2/CUM_8M | TRUOC | CUM_8M | 1 | 4 | 0 | 4 | 4 |
| TRUOC/jet_bombs/attack_jet/s3/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 2 | 0 | 2 | 2 |
| TRUOC/jet_bombs/attack_jet/s3/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 2 | 0 | 2 | 2 |
| TRUOC/jet_bombs/attack_jet/s3/CUM_8M | TRUOC | CUM_8M | 1 | 5 | 0 | 5 | 5 |
| TRUOC/jet_bombs/elite_attack_jet/s1/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 2 | 0 | 2 | 2 |
| TRUOC/jet_bombs/elite_attack_jet/s1/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/jet_bombs/elite_attack_jet/s1/CUM_8M | TRUOC | CUM_8M | 1 | 5 | 0 | 5 | 5 |
| TRUOC/jet_bombs/elite_attack_jet/s2/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 2 | 0 | 2 | 2 |
| TRUOC/jet_bombs/elite_attack_jet/s2/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 1 | 0 | 1 | 1 |
| TRUOC/jet_bombs/elite_attack_jet/s2/CUM_8M | TRUOC | CUM_8M | 1 | 4 | 0 | 4 | 4 |
| TRUOC/jet_bombs/elite_attack_jet/s3/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 2 | 0 | 2 | 2 |
| TRUOC/jet_bombs/elite_attack_jet/s3/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 2 | 0 | 2 | 2 |
| TRUOC/jet_bombs/elite_attack_jet/s3/CUM_8M | TRUOC | CUM_8M | 1 | 5 | 0 | 5 | 5 |
| TRUOC/jet_bombs/stealth_naval_strike/s1/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 2 | 3 | 0 | 3 | 4 |
| TRUOC/jet_bombs/stealth_naval_strike/s1/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 2 | 1 | 0 | 1 | 2 |
| TRUOC/jet_bombs/stealth_naval_strike/s1/CUM_8M | TRUOC | CUM_8M | 2 | 5 | 0 | 5 | 6 |
| TRUOC/jet_bombs/stealth_naval_strike/s2/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 2 | 3 | 0 | 3 | 4 |
| TRUOC/jet_bombs/stealth_naval_strike/s2/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 2 | 1 | 0 | 1 | 2 |
| TRUOC/jet_bombs/stealth_naval_strike/s2/CUM_8M | TRUOC | CUM_8M | 2 | 5 | 0 | 5 | 6 |
| TRUOC/jet_bombs/stealth_naval_strike/s3/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 2 | 3 | 0 | 3 | 4 |
| TRUOC/jet_bombs/stealth_naval_strike/s3/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 2 | 1 | 0 | 1 | 2 |
| TRUOC/jet_bombs/stealth_naval_strike/s3/CUM_8M | TRUOC | CUM_8M | 2 | 5 | 0 | 5 | 6 |
| TRUOC/kraken_air_raid/kraken/s1/HANG_DOC_8M | TRUOC_KHONG_DOI | HANG_DOC_8M | 12 | 5 | 0 | 5 | 10 |
| TRUOC/kraken_air_raid/kraken/s1/HANG_NGANG_8M | TRUOC_KHONG_DOI | HANG_NGANG_8M | 12 | 3 | 2 | 5 | 4 |
| TRUOC/kraken_air_raid/kraken/s1/CUM_8M | TRUOC_KHONG_DOI | CUM_8M | 12 | 5 | 0 | 5 | 12 |
| TRUOC/kraken_air_raid/kraken/s2/HANG_DOC_8M | TRUOC_KHONG_DOI | HANG_DOC_8M | 12 | 5 | 0 | 5 | 10 |
| TRUOC/kraken_air_raid/kraken/s2/HANG_NGANG_8M | TRUOC_KHONG_DOI | HANG_NGANG_8M | 12 | 2 | 2 | 4 | 4 |
| TRUOC/kraken_air_raid/kraken/s2/CUM_8M | TRUOC_KHONG_DOI | CUM_8M | 12 | 5 | 0 | 5 | 10 |
| TRUOC/kraken_air_raid/kraken/s3/HANG_DOC_8M | TRUOC_KHONG_DOI | HANG_DOC_8M | 12 | 5 | 0 | 5 | 10 |
| TRUOC/kraken_air_raid/kraken/s3/HANG_NGANG_8M | TRUOC_KHONG_DOI | HANG_NGANG_8M | 12 | 2 | 3 | 5 | 4 |
| TRUOC/kraken_air_raid/kraken/s3/CUM_8M | TRUOC_KHONG_DOI | CUM_8M | 12 | 5 | 0 | 5 | 11 |
| TRUOC/napalm_strike/(the_ho_tro)/s1/HANG_DOC_8M | TRUOC_KHONG_DOI | HANG_DOC_8M | 8 | 5 | 0 | 5 | 10 |
| TRUOC/napalm_strike/(the_ho_tro)/s1/HANG_NGANG_8M | TRUOC_KHONG_DOI | HANG_NGANG_8M | 8 | 2 | 0 | 2 | 4 |
| TRUOC/napalm_strike/(the_ho_tro)/s1/CUM_8M | TRUOC_KHONG_DOI | CUM_8M | 8 | 5 | 0 | 5 | 11 |
| TRUOC/napalm_strike/(the_ho_tro)/s2/HANG_DOC_8M | TRUOC_KHONG_DOI | HANG_DOC_8M | 8 | 5 | 0 | 5 | 10 |
| TRUOC/napalm_strike/(the_ho_tro)/s2/HANG_NGANG_8M | TRUOC_KHONG_DOI | HANG_NGANG_8M | 8 | 3 | 0 | 3 | 4 |
| TRUOC/napalm_strike/(the_ho_tro)/s2/CUM_8M | TRUOC_KHONG_DOI | CUM_8M | 8 | 5 | 0 | 5 | 10 |
| TRUOC/napalm_strike/(the_ho_tro)/s3/HANG_DOC_8M | TRUOC_KHONG_DOI | HANG_DOC_8M | 8 | 5 | 0 | 5 | 10 |
| TRUOC/napalm_strike/(the_ho_tro)/s3/HANG_NGANG_8M | TRUOC_KHONG_DOI | HANG_NGANG_8M | 8 | 2 | 0 | 2 | 4 |
| TRUOC/napalm_strike/(the_ho_tro)/s3/CUM_8M | TRUOC_KHONG_DOI | CUM_8M | 8 | 5 | 0 | 5 | 11 |
| TRUOC/p26_roc_main_roc_bombs/argus/s1/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 8 | 3 | 2 | 5 | 22 |
| TRUOC/p26_roc_main_roc_bombs/argus/s1/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 8 | 3 | 2 | 5 | 23 |
| TRUOC/p26_roc_main_roc_bombs/argus/s1/CUM_8M | TRUOC | CUM_8M | 8 | 5 | 0 | 5 | 40 |
| TRUOC/p26_roc_main_roc_bombs/argus/s2/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 8 | 3 | 2 | 5 | 23 |
| TRUOC/p26_roc_main_roc_bombs/argus/s2/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 8 | 3 | 2 | 5 | 24 |
| TRUOC/p26_roc_main_roc_bombs/argus/s2/CUM_8M | TRUOC | CUM_8M | 8 | 5 | 0 | 5 | 40 |
| TRUOC/p26_roc_main_roc_bombs/argus/s3/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 8 | 3 | 2 | 5 | 22 |
| TRUOC/p26_roc_main_roc_bombs/argus/s3/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 8 | 3 | 2 | 5 | 23 |
| TRUOC/p26_roc_main_roc_bombs/argus/s3/CUM_8M | TRUOC | CUM_8M | 8 | 5 | 0 | 5 | 40 |
| TRUOC/p26_roc_main_roc_bombs/command_airship/s1/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 8 | 3 | 2 | 5 | 22 |
| TRUOC/p26_roc_main_roc_bombs/command_airship/s1/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 8 | 3 | 2 | 5 | 23 |
| TRUOC/p26_roc_main_roc_bombs/command_airship/s1/CUM_8M | TRUOC | CUM_8M | 8 | 5 | 0 | 5 | 40 |
| TRUOC/p26_roc_main_roc_bombs/command_airship/s2/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 8 | 3 | 2 | 5 | 23 |
| TRUOC/p26_roc_main_roc_bombs/command_airship/s2/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 8 | 3 | 2 | 5 | 24 |
| TRUOC/p26_roc_main_roc_bombs/command_airship/s2/CUM_8M | TRUOC | CUM_8M | 8 | 5 | 0 | 5 | 40 |
| TRUOC/p26_roc_main_roc_bombs/command_airship/s3/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 8 | 3 | 2 | 5 | 22 |
| TRUOC/p26_roc_main_roc_bombs/command_airship/s3/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 8 | 3 | 2 | 5 | 23 |
| TRUOC/p26_roc_main_roc_bombs/command_airship/s3/CUM_8M | TRUOC | CUM_8M | 8 | 5 | 0 | 5 | 40 |
| TRUOC/p26_roc_main_roc_bombs/garuda/s1/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 8 | 3 | 2 | 5 | 24 |
| TRUOC/p26_roc_main_roc_bombs/garuda/s1/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 8 | 3 | 2 | 5 | 23 |
| TRUOC/p26_roc_main_roc_bombs/garuda/s1/CUM_8M | TRUOC | CUM_8M | 8 | 5 | 0 | 5 | 40 |
| TRUOC/p26_roc_main_roc_bombs/garuda/s2/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 8 | 3 | 2 | 5 | 23 |
| TRUOC/p26_roc_main_roc_bombs/garuda/s2/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 8 | 3 | 2 | 5 | 24 |
| TRUOC/p26_roc_main_roc_bombs/garuda/s2/CUM_8M | TRUOC | CUM_8M | 8 | 5 | 0 | 5 | 40 |
| TRUOC/p26_roc_main_roc_bombs/garuda/s3/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 8 | 3 | 2 | 5 | 22 |
| TRUOC/p26_roc_main_roc_bombs/garuda/s3/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 8 | 3 | 2 | 5 | 24 |
| TRUOC/p26_roc_main_roc_bombs/garuda/s3/CUM_8M | TRUOC | CUM_8M | 8 | 5 | 0 | 5 | 40 |
| TRUOC/stealth_payload/stealth_bomber/s1/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 2 | 3 | 0 | 3 | 6 |
| TRUOC/stealth_payload/stealth_bomber/s1/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 2 | 3 | 0 | 3 | 6 |
| TRUOC/stealth_payload/stealth_bomber/s1/CUM_8M | TRUOC | CUM_8M | 2 | 5 | 0 | 5 | 10 |
| TRUOC/stealth_payload/stealth_bomber/s2/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 2 | 3 | 0 | 3 | 6 |
| TRUOC/stealth_payload/stealth_bomber/s2/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 2 | 3 | 0 | 3 | 6 |
| TRUOC/stealth_payload/stealth_bomber/s2/CUM_8M | TRUOC | CUM_8M | 2 | 5 | 0 | 5 | 10 |
| TRUOC/stealth_payload/stealth_bomber/s3/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 2 | 3 | 0 | 3 | 6 |
| TRUOC/stealth_payload/stealth_bomber/s3/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 2 | 3 | 0 | 3 | 6 |
| TRUOC/stealth_payload/stealth_bomber/s3/CUM_8M | TRUOC | CUM_8M | 2 | 5 | 0 | 5 | 10 |
| TRUOC/thermobaric_bomb/glide_bomber/s1/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 3 | 0 | 3 | 3 |
| TRUOC/thermobaric_bomb/glide_bomber/s1/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 3 | 0 | 3 | 3 |
| TRUOC/thermobaric_bomb/glide_bomber/s1/CUM_8M | TRUOC | CUM_8M | 1 | 5 | 0 | 5 | 5 |
| TRUOC/thermobaric_bomb/glide_bomber/s2/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 3 | 0 | 3 | 3 |
| TRUOC/thermobaric_bomb/glide_bomber/s2/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 3 | 0 | 3 | 3 |
| TRUOC/thermobaric_bomb/glide_bomber/s2/CUM_8M | TRUOC | CUM_8M | 1 | 5 | 0 | 5 | 5 |
| TRUOC/thermobaric_bomb/glide_bomber/s3/HANG_DOC_8M | TRUOC | HANG_DOC_8M | 1 | 3 | 0 | 3 | 3 |
| TRUOC/thermobaric_bomb/glide_bomber/s3/HANG_NGANG_8M | TRUOC | HANG_NGANG_8M | 1 | 3 | 0 | 3 | 3 |
| TRUOC/thermobaric_bomb/glide_bomber/s3/CUM_8M | TRUOC | CUM_8M | 1 | 5 | 0 | 5 | 5 |
