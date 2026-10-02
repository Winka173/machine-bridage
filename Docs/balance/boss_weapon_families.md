# Boss weapon families: before and after (full fix prompt L3)

Written by `Tools/balance/fix_boss_weapons.py` (it replaces prompt 34 L2's `p34_boss_families.py`, retired). Before =
the data after prompt 34 (stored in `Tools/balance/fix_boss_before.json`): each weapon's cadence solved from the old
prompt 26 DPS. After = the real cadence family by family (wave 1 where it passes the real rate, else the real rate),
the family's round unchanged; the DPS is the result. DPS on paper: a cycle's rounds over the cycle, every barrel,
before the boss's own factors (weaponDamage, rank, phases). Ground = every mount that can fire at the ground; air =
the anti-air-only mounts. No battle was run. Health: unchanged (the formula P x t x 0.6 is not recalculated).

## The family table (boss scale) and the cadence

| family | weapons | cadence | why |
|---|---|---|---|
| 2a65 | `p26_behemoth_main_be152` | 2 barrels together every 8.98 s | wave 1 gun_behemoth: the twin 2A65, 2 rounds every 8.98 s (real 7-8 rpm a gun, Msta-B): passes (b) |
| rh120 | `p26_behemoth_tiny_be120`, `p26_behemoth_direct_be120`, `p26_moloch_direct_mo120ap`, `p26_moloch_main_mo120` | one round every 7.5 s | real Rh-120 with a loader, 8 rpm (7.5 s); wave 1's 5.1 s is too fast after the 30 % rule |
| 2a46 | `p26_jotunn_direct_jo125`, `p26_nemesis_direct_ne125`, `p26_ixion_125` | one round every 7.5 s | real 2A46 with its autoloader, 8 rpm (7.5 s); wave 1's 5.56 s is too fast after the 30 % rule |
| 2a44 | `p26_jotunn_jo203` | one round every 24 s | real 2S7M Malka 2.5 rpm (24 s); wave 1's 9.44 s is too fast |
| 2b8 | `p26_bastion_sec_b240` | one round every 60 s | real 2S4 Tyulpan ~1 rpm (60 s); wave 1's 10 s is too fast |
| m284 | `p26_bastion_main_b155` | one round every 15 s | real M109A7 4 rpm (15 s) at its maximum; wave 1's 12.5 s is too fast after the 30 % rule |
| d10 | `p26_bastion_direct_b100` | one round every 8.6 s | real D-10 4-7 rpm (8.6 s at 7) |
| 152rail | `p26_nemesis_main_ne152` | one round every 7.5 s | a 152 mm railway gun of the 2A65 class, 8 rpm (7.5 s); the 4-round 0.5 s salvo was 6 x too fast |
| b38 | `train_gun` | one round every 8 s | real B-38 5-7.5 rpm (8 s at 7.5); wave 1's 5.11 s is too fast |
| 155_60 | `p26_leviathan_sec_lev155` | 3 barrels together every 10.5 s | wave 1 naval_155_triple: the triple turret, 3 rounds every 10.5 s (real ~5 rpm a gun): passes (b) |
| ak130 | `naval_130_twin` | 2 barrels together every 3.0 s | real AK-130 10-40 rpm a barrel: 20 rpm (3 s), practical; 4.75 s was too slow |
| a192 | `p26_leviathan_direct_lev127` | one round every 3.0 s | an A-192 class 130 mm, 30 rpm max: 20 rpm practical (3 s) |
| ak100 | `p26_typhon_direct_ty100` | 2 rounds 1.0 s apart, 2.5 s after | wave 1 naval_100's pair every 3.5 s, the rounds 1 s apart (AK-100 60 rpm; wave 1's 0.5 s is twice the real rate) |
| au220 | `p26_typhon_sec_ty57`, `p26_daedalus_sec_dae57`, `p26_kronos_direct_kr57`, `p26_matriarch_tiny_mothership_cannon` | 4 rounds 0.5 s apart, 2.79 s after | wave 1 mothership_cannon: 4 rounds 0.5 s apart every 4.29 s (AU-220M 120 rpm) |
| 2a42 | `p26_matriarch_sec_autocannon_30`, `p26_kronos_close_autocannon_30` | 10 rounds 0.1111 s apart, 1.5 s after | wave 1 autocannon_30: 10 rounds at 540 rpm every 2.5 s (2A42 550-800 rpm) |
| 2a42x2 | `p26_roc_close_twin_30_bmpt` | 12 rounds 0.0833 s apart, 1.45 s after | wave 1 twin_30_bmpt: 12 rounds at 720 rpm, 1.45 s after (wave 1's 1.5 s is a hair over 2 x the practical rate) |
| patriot | `sam_battery` | 2 rounds 3.0 s apart, 8.0 s after | MIM-104 Patriot: the pair ~3 s apart (est.; 0.45 s was too fast), the 11 s cycle kept |
| grad | `p26_behemoth_sec_be_rockets`, `p26_nemesis_sec_boss_rockets`, `p26_kronos_close_boss_rockets`, `boss_rockets` | ripple 0.5 s apart, 2.44 s after | wave 1 boss_rockets: rockets 0.5 s apart (BM-21: 40 in 20 s), 2.44 s after the ripple; each pod keeps its rockets |
| smerch | `p26_jotunn_sec_jo_rockets` | ripple 3.17 s apart, 15.76 s after | real BM-30 Smerch 12 rockets in 38 s (3.17 s apart), wave 1 rockets_300mm's 15.76 s after the ripple |
| kornet | `p26_behemoth_tiny_boss_missiles`, `p26_matriarch_direct_ma_atgm` | one round every 20 s | real 9M133 Kornet 3 rpm (20 s); wave 1's 6.39 s is too fast |
| kornet2 | `p26_behemoth_tiny_kornet_twin`, `p26_bastion_tiny_kornet_twin`, `p26_roc_direct_roc_atgm` | 2 rounds 0.6 s apart, 19.4 s after | a twin Kornet launcher: the pair 0.6 s apart, every 20 s (3 rpm a rail); 55.6 s was too slow |
| bofors | `p26_bastion_tiny_autocannon_40`, `p26_icarus_close_autocannon_40` | 10 rounds 0.2 s apart, changed in 1.52 s | wave 1 autocannon_40: 10 rounds at 300 rpm, changed in 1.52 s (Bofors L/70 240-330 rpm) |
| nsv | `p26_bastion_close_boss_hmg`, `p26_ixion_mg`, `boss_hmg` | 100 rounds 0.0833 s apart, changed in 5.0 s | wave 1 boss_hmg: 100 rounds at 720 rpm, changed in 5 s (NSV 700-800 rpm) |
| zu23 | `p26_bastion_tiny_zu23`, `p26_moloch_tiny_zu23` | 50 rounds 0.04 s apart, changed in 3.0 s | wave 1 zu23: 50 rounds at 1,500 rpm, changed in 3 s (ZU-23-2 2 x 800-1,000 rpm) |
| gdf | `p26_behemoth_close_boss_flak`, `p26_jotunn_close_boss_flak`, `p26_matriarch_close_boss_flak`, `p26_nemesis_close_boss_flak`, `p26_moloch_close_boss_flak` | 41 rounds 0.05 s apart, changed in 3.38 s | wave 1 boss_flak: 41 rounds at 1,200 rpm, changed in 3.38 s (twin Oerlikon GDF 2 x 550 rpm) |
| 2a38 | `p26_jotunn_tiny_twin_30_flak` | 160 rounds 0.025 s apart, changed in 3.0 s | wave 1 twin_30_flak: 160 rounds at 2,400 rpm, changed in 3 s (2A38M 4,060-5,000 rpm the pair) |
| m102 | `p26_roc_roc105` | one round every 6 s | real M102 10 rpm (6 s); wave 1's 2.74 s is too fast after the 30 % rule |
| 2a70 | `borer_cannon` | one round every 6 s | real 2A70 10 rpm (6 s); 2.08 s was too fast |
| ogon | `hover_rockets` | ripple 0.5 s apart, own s after | A-22 Ogon 140 mm: est. 0.5 s a rocket (0.1 s was too fast), the 22 s pause kept |

## Per boss

### behemoth

Ground DPS **1012 -> 1099** (109 %); anti-air only 0 -> 0. Made up: `p26_behemoth_direct_be120` 2 barrels together, `p26_behemoth_sec_be_rockets` 40 tubes.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_behemoth_main_be152` | cal_152_155 | 600 x 1 / 1.85 s = 325 | 600 x 2 (2 together) / 8.98 s = 134 | 7 / 14 |
| 1 | `p26_behemoth_tiny_be120` | cal_120_ap | 260 x 1 / 20.00 s = 13 | 260 x 1 / 7.50 s = 35 | 0 / 0 |
| 2 | `p26_behemoth_close_boss_flak` | cal_35 | 25 x 41 / 8.41 s = 122 | 25 x 41 / 5.38 s = 191 | 2.5 / 0 |
| 3 | `p26_behemoth_close_boss_flak` | cal_35 | 25 x 41 / 8.41 s = 122 | 25 x 41 / 5.38 s = 191 | 2.5 / 0 |
| 4 | `p26_behemoth_tiny_boss_missiles` | atgm_kornet | 230 x 1 / 31.95 s = 7 | 230 x 1 / 20.00 s = 12 | 0 / 0 |
| 5 | `p26_behemoth_tiny_boss_missiles` | atgm_kornet | 230 x 1 / 31.95 s = 7 | 230 x 1 / 20.00 s = 12 | 0 / 0 |
| 6 | `p26_behemoth_tiny_kornet_twin` | atgm_kornet | 230 x 2 / 55.55 s = 8 | 230 x 2 / 20.00 s = 23 | 0 / 0 |
| 7 | `p26_behemoth_direct_be120` | cal_120_ap | 260 x 1 / 5.10 s = 51 | 260 x 2 (2 together) / 7.50 s = 69 | 0 / 0 |
| 8 | `p26_behemoth_direct_be120` | cal_120_ap | 260 x 1 / 5.10 s = 51 | 260 x 2 (2 together) / 7.50 s = 69 | 0 / 0 |
| 9 | `p26_behemoth_sec_be_rockets` | rkt_grad_122 | 200 x 8 / 5.23 s = 306 | 200 x 40 / 21.94 s = 365 | 4.5 / 9 |

### mobile_fortress

Ground DPS **954 -> 1204** (126 %); anti-air only 145 -> 145.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_jotunn_jo203` | cal_203 | 900 x 1 / 5.70 s = 158 | 900 x 1 / 24.00 s = 38 | 8.5 / 17 |
| 1 | `p26_jotunn_sec_jo_rockets` | rkt_smerch_300 | 450 x 8 / 33.78 s = 107 | 450 x 8 / 37.95 s = 95 | 8 / 16 |
| 2 | `p26_jotunn_sec_jo_rockets` | rkt_smerch_300 | 450 x 8 / 33.78 s = 107 | 450 x 8 / 37.95 s = 95 | 8 / 16 |
| 3 | `p26_jotunn_close_boss_flak` | cal_35 | 25 x 41 / 7.47 s = 137 | 25 x 41 / 5.38 s = 191 | 2.5 / 0 |
| 4 | `p26_jotunn_close_boss_flak` | cal_35 | 25 x 41 / 7.47 s = 137 | 25 x 41 / 5.38 s = 191 | 2.5 / 0 |
| 5 | `p26_jotunn_direct_jo125` | cal_125_ap | 400 x 1 / 3.45 s = 116 | 400 x 1 / 7.50 s = 53 | 0 / 0 |
| 6 | `p26_jotunn_tiny_twin_30_flak` | cal_30 | 22 x 160 / 102.66 s = 34 | 22 x 160 / 6.97 s = 505 | 2.5 / 0 |
| 7 | `p26_jotunn_jo203` | cal_203 | 900 x 1 / 5.70 s = 158 | 900 x 1 / 24.00 s = 38 | 8.5 / 17 |
| 8 | `sam_post` | sam_9m317_buk | 320 x 2 / 4.40 s = 145 | 320 x 2 / 4.40 s = 145 | 2 / 0 |

### armored_train

Ground DPS **660 -> 952** (144 %); anti-air only 0 -> 0.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `train_gun` | cal_152_155 | 600 x 1 / 9.58 s = 63 | 600 x 1 / 8.00 s = 75 | 2.5 / 0 |
| 1 | `boss_rockets` | rkt_grad_122 | 200 x 13 / 31.37 s = 83 | 200 x 13 / 8.44 s = 308 | 4.5 / 9 |
| 2 | `boss_hmg` | cal_12_7 | 15 x 100 / 21.05 s = 71 | 15 x 100 / 13.25 s = 113 | 0 / 0 |
| 3 | `boss_flak` | cal_35 | 25 x 41 / 5.38 s = 191 | 25 x 41 / 5.38 s = 191 | 2.5 / 0 |
| 4 | `train_gun` | cal_152_155 | 600 x 1 / 9.58 s = 63 | 600 x 1 / 8.00 s = 75 | 2.5 / 0 |
| 5 | `boss_flak` | cal_35 | 25 x 41 / 5.38 s = 191 | 25 x 41 / 5.38 s = 191 | 2.5 / 0 |

### mega_gunship

Ground DPS **462 -> 546** (118 %); anti-air only 0 -> 0.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `gunship_rockets` | rkt_70_80 | 32 x 16 / 9.77 s = 52 | 32 x 16 / 9.77 s = 52 | 3 / 0 |
| 1 | `boss_heli_gun` | cal_30 | 22 x 40 / 9.67 s = 91 | 22 x 40 / 9.67 s = 91 | 0 / 0 |
| 2 | `boss_heli_gun` | cal_30 | 22 x 40 / 9.67 s = 91 | 22 x 40 / 9.67 s = 91 | 0 / 0 |
| 3 | `boss_minigun` | cal_7_62 | 5.5 x 40 / 6.76 s = 33 | 5.5 x 40 / 6.76 s = 33 | 0 / 0 |
| 4 | `gunship_rockets` | rkt_70_80 | 32 x 16 / 9.77 s = 52 | 32 x 16 / 9.77 s = 52 | 3 / 0 |
| 5 | `boss_hmg` | cal_12_7 | 15 x 100 / 21.05 s = 71 | 15 x 100 / 13.25 s = 113 | 0 / 0 |
| 6 | `boss_hmg` | cal_12_7 | 15 x 100 / 21.05 s = 71 | 15 x 100 / 13.25 s = 113 | 0 / 0 |

### drone_mothership

Ground DPS **1304 -> 1188** (91 %); anti-air only 0 -> 0.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_matriarch_tiny_mothership_cannon` | cal_57 | 120 x 4 / 41.06 s = 12 | 120 x 4 / 4.29 s = 112 | 3 / 6 |
| 1 | `p26_matriarch_ma_drones` | drone_zala_lancet_3_swarm | 320 x 6 / 5.00 s = 384 | 320 x 6 / 5.00 s = 384 | 3 / 6 |
| 2 | `p26_matriarch_close_boss_flak` | cal_35 | 25 x 41 / 6.11 s = 168 | 25 x 41 / 5.38 s = 191 | 2.5 / 0 |
| 3 | `p26_matriarch_close_boss_flak` | cal_35 | 25 x 41 / 6.11 s = 168 | 25 x 41 / 5.38 s = 191 | 2.5 / 0 |
| 4 | `p26_matriarch_tiny_mothership_cannon` | cal_57 | 120 x 4 / 41.06 s = 12 | 120 x 4 / 4.29 s = 112 | 3 / 6 |
| 5 | `p26_matriarch_direct_ma_atgm` | atgm_kornet | 230 x 1 / 3.29 s = 70 | 230 x 1 / 20.00 s = 12 | 0 / 0 |
| 6 | `p26_matriarch_sec_autocannon_30` | cal_30 | 22 x 10 / 1.04 s = 211 | 22 x 10 / 2.50 s = 88 | 0 / 0 |
| 7 | `p26_matriarch_sec_autocannon_30` | cal_30 | 22 x 10 / 1.04 s = 211 | 22 x 10 / 2.50 s = 88 | 0 / 0 |
| 8 | `p26_matriarch_direct_ma_atgm` | atgm_kornet | 230 x 1 / 3.29 s = 70 | 230 x 1 / 20.00 s = 12 | 0 / 0 |

### nuke_train

Ground DPS **1751 -> 1070** (61 %); anti-air only 62 -> 62. Made up: `p26_nemesis_sec_boss_rockets` 40 tubes. **Not made up within 20 %** (see below).

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_nemesis_main_ne152` | cal_152_155 | 600 x 4 / 4.12 s = 582 | 600 x 1 / 7.50 s = 80 | 7 / 14 |
| 1 | `p26_nemesis_close_boss_flak` | cal_35 | 25 x 41 / 7.08 s = 145 | 25 x 41 / 5.38 s = 191 | 2.5 / 0 |
| 2 | `p26_nemesis_close_boss_flak` | cal_35 | 25 x 41 / 7.08 s = 145 | 25 x 41 / 5.38 s = 191 | 2.5 / 0 |
| 3 | `p26_nemesis_sec_boss_rockets` | rkt_grad_122 | 200 x 13 / 4.72 s = 551 | 200 x 40 / 21.94 s = 365 | 4.5 / 9 |
| 4 | `sam_battery` | sam_mim_104_patriot_pac_2 | 340 x 2 / 11.00 s = 62 | 340 x 2 / 11.00 s = 62 | 2.5 / 0 |
| 5 | `p26_nemesis_direct_ne125` | cal_125_ap | 400 x 1 / 2.18 s = 183 | 400 x 1 / 7.50 s = 53 | 0 / 0 |
| 6 | `p26_nemesis_close_boss_flak` | cal_35 | 25 x 41 / 7.08 s = 145 | 25 x 41 / 5.38 s = 191 | 2.5 / 0 |

### silver_bug

Ground DPS **1638 -> 1501** (92 %); anti-air only 0 -> 0.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_icarus_sec_orbital_laser` | laser_laser | 40 x 1 / 0.10 s = 400 | 40 x 1 / 0.10 s = 400 | 1.5 / 0 |
| 1 | `p26_icarus_main_ic_coil` | rail_heavy_coilgun | 1500 x 1 / 5.00 s = 300 | 1500 x 1 / 5.00 s = 300 | 0 / 0 |
| 2 | `p26_icarus_main_ic_coil` | rail_heavy_coilgun | 1500 x 1 / 5.00 s = 300 | 1500 x 1 / 5.00 s = 300 | 0 / 0 |
| 3 | `p26_icarus_direct_ic_laser` | laser_tower | 16 x 1 / 0.10 s = 160 | 16 x 1 / 0.10 s = 160 | 1.5 / 0 |
| 4 | `p26_icarus_direct_ic_laser` | laser_tower | 16 x 1 / 0.10 s = 160 | 16 x 1 / 0.10 s = 160 | 1.5 / 0 |
| 5 | `p26_icarus_close_autocannon_40` | cal_40 | 30 x 10 / 1.89 s = 159 | 30 x 10 / 3.32 s = 90 | 0 / 0 |
| 6 | `p26_icarus_close_autocannon_40` | cal_40 | 30 x 10 / 1.89 s = 159 | 30 x 10 / 3.32 s = 90 | 0 / 0 |

### behemoth_inferno

Ground DPS **282 -> 282** (100 %); anti-air only 0 -> 0.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `boss_flamer` | flame_flamethrower | 30 x 1 / 0.25 s = 120 | 30 x 1 / 0.25 s = 120 | 3.5 / 0 |
| 1 | `boss_thermo` | rkt_tos_220 | 97 x 6 / 14.01 s = 42 | 97 x 6 / 14.01 s = 42 | 7 / 0 |
| 2 | `boss_flamer` | flame_flamethrower | 30 x 1 / 0.25 s = 120 | 30 x 1 / 0.25 s = 120 | 3.5 / 0 |

### behemoth_tempest

Ground DPS **299 -> 299** (100 %); anti-air only 0 -> 0.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `boss_railgun` | rail_railgun | 720 x 1 / 8.00 s = 90 | 720 x 1 / 8.00 s = 90 | 0 / 0 |
| 1 | `coilgun` | rail_coilgun | 250 x 2 / 4.79 s = 104 | 250 x 2 / 4.79 s = 104 | 0 / 0 |
| 2 | `coilgun` | rail_coilgun | 250 x 2 / 4.79 s = 104 | 250 x 2 / 4.79 s = 104 | 0 / 0 |

### fortress_hive

Ground DPS **586 -> 586** (100 %); anti-air only 0 -> 0.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `mothership_drones` | drone_zala_lancet_3 | 240 x 4 / 9.37 s = 102 | 240 x 4 / 9.37 s = 102 | 3 / 0 |
| 1 | `mothership_drones` | drone_zala_lancet_3 | 240 x 4 / 9.37 s = 102 | 240 x 4 / 9.37 s = 102 | 3 / 0 |
| 2 | `boss_flak` | cal_35 | 25 x 41 / 5.38 s = 191 | 25 x 41 / 5.38 s = 191 | 2.5 / 0 |
| 3 | `boss_flak` | cal_35 | 25 x 41 / 5.38 s = 191 | 25 x 41 / 5.38 s = 191 | 2.5 / 0 |

### fortress_bastion

Ground DPS **792 -> 741** (94 %); anti-air only 0 -> 0. Made up: `p26_bastion_direct_b100` 2 barrels together.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_bastion_sec_b240` | cal_240 | 1100 x 1 / 7.69 s = 143 | 1100 x 1 / 60.00 s = 18 | 10 / 20 |
| 1 | `p26_bastion_direct_b100` | cal_100_105_ap | 240 x 1 / 5.00 s = 48 | 240 x 2 (2 together) / 8.60 s = 56 | 0 / 0 |
| 2 | `p26_bastion_direct_b100` | cal_100_105_ap | 240 x 1 / 5.00 s = 48 | 240 x 2 (2 together) / 8.60 s = 56 | 0 / 0 |
| 3 | `p26_bastion_tiny_autocannon_40` | cal_40 | 30 x 10 / 17.60 s = 17 | 30 x 10 / 3.32 s = 90 | 0 / 0 |
| 4 | `p26_bastion_tiny_autocannon_40` | cal_40 | 30 x 10 / 17.60 s = 17 | 30 x 10 / 3.32 s = 90 | 0 / 0 |
| 5 | `p26_bastion_tiny_kornet_twin` | atgm_kornet | 230 x 2 / 55.55 s = 8 | 230 x 2 / 20.00 s = 23 | 0 / 0 |
| 6 | `p26_bastion_close_boss_hmg` | cal_12_7 | 15 x 100 / 13.33 s = 113 | 15 x 100 / 13.25 s = 113 | 0 / 0 |
| 7 | `p26_bastion_close_boss_hmg` | cal_12_7 | 15 x 100 / 13.33 s = 113 | 15 x 100 / 13.25 s = 113 | 0 / 0 |
| 8 | `p26_bastion_main_b155` | cal_152_155 | 600 x 1 / 2.33 s = 258 | 600 x 1 / 15.00 s = 40 | 7 / 14 |
| 9 | `p26_bastion_tiny_zu23` | cal_23 | 7 x 50 / 25.00 s = 14 | 7 x 50 / 4.96 s = 71 | 0 / 0 |
| 10 | `p26_bastion_tiny_zu23` | cal_23 | 7 x 50 / 25.00 s = 14 | 7 x 50 / 4.96 s = 71 | 0 / 0 |

### rail_supergun

Ground DPS **170 -> 170** (100 %); anti-air only 240 -> 240.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `supergun_800` | cal_800 | 900 x 1 / 25.00 s = 0 (laid) | 900 x 1 / 25.00 s = 0 (laid) | 12 / 0 |
| 1 | `autocannon_40` | cal_40 | 30 x 10 / 3.52 s = 85 | 30 x 10 / 3.52 s = 85 | 1 / 0 |
| 2 | `autocannon_40` | cal_40 | 30 x 10 / 3.52 s = 85 | 30 x 10 / 3.52 s = 85 | 1 / 0 |
| 3 | `ciws_aa` | cal_30 | 12 x 60 / 6.00 s = 120 | 12 x 60 / 6.00 s = 120 | 0 / 0 |
| 4 | `ciws_aa` | cal_30 | 12 x 60 / 6.00 s = 120 | 12 x 60 / 6.00 s = 120 | 0 / 0 |

### earth_borer

Ground DPS **289 -> 213** (74 %); anti-air only 0 -> 0. **Not made up within 20 %** (see below).

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `borer_drill` | melee_drill_head | 260 x 1 / 1.50 s = 173 | 260 x 1 / 1.50 s = 173 | 0 / 0 |
| 1 | `borer_cannon` | cal_76 | 120 x 1 / 2.08 s = 58 | 120 x 1 / 6.00 s = 20 | 1.5 / 0 |
| 2 | `borer_cannon` | cal_76 | 120 x 1 / 2.08 s = 58 | 120 x 1 / 6.00 s = 20 | 1.5 / 0 |

### command_airship

Ground DPS **1532 -> 685** (45 %); anti-air only 0 -> 0. **Not made up within 20 %** (see below).

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_roc_main_roc_bombs` | bomb_400 | 700 x 8 / 35.44 s = 158 | 700 x 8 / 35.44 s = 158 | 10 / 20 |
| 1 | `p26_roc_main_roc_bombs` | bomb_400 | 700 x 8 / 35.44 s = 158 | 700 x 8 / 35.44 s = 158 | 10 / 20 |
| 2 | `p26_roc_direct_roc_atgm` | atgm_kornet | 230 x 1 / 1.98 s = 116 | 230 x 2 / 20.00 s = 23 | 0 / 0 |
| 3 | `p26_roc_direct_roc_atgm` | atgm_kornet | 230 x 1 / 1.98 s = 116 | 230 x 2 / 20.00 s = 23 | 0 / 0 |
| 4 | `p26_roc_close_twin_30_bmpt` | cal_30 | 22 x 12 / 1.86 s = 142 | 22 x 12 / 2.37 s = 112 | 0 / 0 |
| 5 | `p26_roc_close_twin_30_bmpt` | cal_30 | 22 x 12 / 1.86 s = 142 | 22 x 12 / 2.37 s = 112 | 0 / 0 |
| 6 | `p26_roc_roc105` | cal_100_105_he | 300 x 1 / 0.86 s = 350 | 300 x 1 / 6.00 s = 50 | 5 / 10 |
| 7 | `p26_roc_roc105` | cal_100_105_he | 300 x 1 / 0.86 s = 350 | 300 x 1 / 6.00 s = 50 | 5 / 10 |

### landing_hovercraft

Ground DPS **302 -> 293** (97 %); anti-air only 120 -> 120.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `hover_ciws` | cal_30 | 12 x 60 / 6.00 s = 120 | 12 x 60 / 6.00 s = 120 | 0 / 0 |
| 1 | `hover_ciws` | cal_30 | 12 x 60 / 6.00 s = 120 | 12 x 60 / 6.00 s = 120 | 0 / 0 |
| 2 | `ciws_aa` | cal_30 | 12 x 60 / 6.00 s = 120 | 12 x 60 / 6.00 s = 120 | 0 / 0 |
| 3 | `hover_rockets` | rkt_140 | 65 x 11 / 23.00 s = 31 | 65 x 11 / 27.00 s = 26 | 4 / 0 |
| 4 | `hover_rockets` | rkt_140 | 65 x 11 / 23.00 s = 31 | 65 x 11 / 27.00 s = 26 | 4 / 0 |

### supreme_command

Ground DPS **143 -> 226** (159 %); anti-air only 0 -> 0.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `boss_hmg` | cal_12_7 | 15 x 100 / 21.05 s = 71 | 15 x 100 / 13.25 s = 113 | 0 / 0 |
| 1 | `boss_hmg` | cal_12_7 | 15 x 100 / 21.05 s = 71 | 15 x 100 / 13.25 s = 113 | 0 / 0 |

### sky_fortress

Ground DPS **418 -> 418** (100 %); anti-air only 0 -> 0.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `gunship_105` | cal_100_105_he | 200 x 1 / 2.74 s = 73 | 200 x 1 / 2.74 s = 73 | 5.5 / 0 |
| 1 | `gunship_40mm` | cal_40 | 30 x 29 / 5.99 s = 145 | 30 x 29 / 5.99 s = 145 | 3 / 0 |
| 2 | `gunship_25mm` | cal_25 | 17 x 56 / 6.01 s = 158 | 17 x 56 / 6.01 s = 158 | 0 / 0 |
| 3 | `griffin` | atgm_agm_176_griffin | 180 x 1 / 4.29 s = 42 | 180 x 1 / 4.29 s = 42 | 0 / 0 |

### leviathan

Ground DPS **771 -> 956** (124 %); anti-air only 804 -> 804.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_leviathan_lev406` | cal_406 | 2400 x 3 / 60.00 s = 0 (laid) | 2400 x 3 (3 together) / 60.00 s = 0 (laid) | 14 / 24 |
| 1 | `p26_leviathan_lev406` | cal_406 | 2400 x 3 / 60.00 s = 0 (laid) | 2400 x 3 (3 together) / 60.00 s = 0 (laid) | 14 / 24 |
| 2 | `p26_leviathan_lev406` | cal_406 | 2400 x 3 / 60.00 s = 0 (laid) | 2400 x 3 (3 together) / 60.00 s = 0 (laid) | 14 / 24 |
| 3 | `p26_leviathan_sec_lev155` | cal_152_155 | 600 x 3 / 13.71 s = 131 | 600 x 3 (3 together) / 10.50 s = 171 | 7 / 14 |
| 4 | `p26_leviathan_sec_lev155` | cal_152_155 | 600 x 3 / 13.71 s = 131 | 600 x 3 (3 together) / 10.50 s = 171 | 7 / 14 |
| 5 | `p26_leviathan_direct_lev127` | cal_127_130 | 380 x 1 / 5.10 s = 74 | 380 x 1 / 3.00 s = 127 | 0 / 0 |
| 6 | `p26_leviathan_direct_lev127` | cal_127_130 | 380 x 1 / 5.10 s = 74 | 380 x 1 / 3.00 s = 127 | 0 / 0 |
| 7 | `aa_25_triple` | cal_25 | 17 x 15 / 3.10 s = 82 | 17 x 15 / 3.10 s = 82 | 0 / 0 |
| 8 | `aa_25_triple` | cal_25 | 17 x 15 / 3.10 s = 82 | 17 x 15 / 3.10 s = 82 | 0 / 0 |
| 9 | `aa_25_triple` | cal_25 | 17 x 15 / 3.10 s = 82 | 17 x 15 / 3.10 s = 82 | 0 / 0 |
| 10 | `aa_25_triple` | cal_25 | 17 x 15 / 3.10 s = 82 | 17 x 15 / 3.10 s = 82 | 0 / 0 |
| 11 | `aa_25_triple` | cal_25 | 17 x 15 / 3.10 s = 82 | 17 x 15 / 3.10 s = 82 | 0 / 0 |
| 12 | `aa_25_triple` | cal_25 | 17 x 15 / 3.10 s = 82 | 17 x 15 / 3.10 s = 82 | 0 / 0 |
| 13 | `aa_25_triple` | cal_25 | 17 x 15 / 3.10 s = 82 | 17 x 15 / 3.10 s = 82 | 0 / 0 |
| 14 | `aa_25_triple` | cal_25 | 17 x 15 / 3.10 s = 82 | 17 x 15 / 3.10 s = 82 | 0 / 0 |
| 15 | `sam_post` | sam_9m317_buk | 320 x 2 / 4.40 s = 145 | 320 x 2 / 4.40 s = 145 | 2 / 0 |
| salvo | `p26_leviathan_lev406` | cal_406 | 2400 x 9 / 60.00 s = 360 | 2400 x 9 (3 together) / 60.00 s = 360 | 14 / 24 |

### moloch

Ground DPS **1382 -> 652** (47 %); anti-air only 0 -> 0. Made up: `p26_moloch_direct_mo120ap` 2 barrels together, `p26_moloch_main_mo120` 2 barrels together. **Not made up within 20 %** (see below).

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_moloch_main_mo120` | cal_120_he | 340 x 1 / 1.13 s = 300 | 340 x 2 (2 together) / 7.50 s = 91 | 5 / 10 |
| 1 | `p26_moloch_tiny_zu23` | cal_23 | 7 x 50 / 25.00 s = 14 | 7 x 50 / 4.96 s = 71 | 0 / 0 |
| 2 | `p26_moloch_tiny_zu23` | cal_23 | 7 x 50 / 25.00 s = 14 | 7 x 50 / 4.96 s = 71 | 0 / 0 |
| 3 | `p26_moloch_main_mo120` | cal_120_he | 340 x 1 / 1.13 s = 300 | 340 x 2 (2 together) / 7.50 s = 91 | 5 / 10 |
| 4 | `p26_moloch_direct_mo120ap` | cal_120_ap | 260 x 1 / 2.36 s = 110 | 260 x 2 (2 together) / 7.50 s = 69 | 0 / 0 |
| 5 | `p26_moloch_direct_mo120ap` | cal_120_ap | 260 x 1 / 2.36 s = 110 | 260 x 2 (2 together) / 7.50 s = 69 | 0 / 0 |
| 6 | `p26_moloch_close_boss_flak` | cal_35 | 25 x 41 / 1.92 s = 534 | 25 x 41 / 5.38 s = 191 | 2.5 / 0 |

### daedalus

Ground DPS **745 -> 778** (104 %); anti-air only 0 -> 0. Made up: `p26_daedalus_sec_dae57` 2 barrels together.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_daedalus_direct_dae_laser` | laser_targeting_laser | 16.5 x 1 / 0.10 s = 165 | 16.5 x 1 / 0.10 s = 165 | 1.5 / 0 |
| 1 | `p26_daedalus_sec_dae57` | cal_57 | 120 x 2 / 1.16 s = 208 | 120 x 8 (2 together) / 4.29 s = 224 | 3 / 6 |
| 2 | `p26_daedalus_sec_dae57` | cal_57 | 120 x 2 / 1.16 s = 208 | 120 x 8 (2 together) / 4.29 s = 224 | 3 / 6 |
| 3 | `p26_daedalus_direct_dae_laser` | laser_targeting_laser | 16.5 x 1 / 0.10 s = 165 | 16.5 x 1 / 0.10 s = 165 | 1.5 / 0 |

### kronos

Ground DPS **439 -> 708** (161 %); anti-air only 0 -> 0.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_kronos_close_autocannon_30` | cal_30 | 22 x 10 / 2.73 s = 80 | 22 x 10 / 2.50 s = 88 | 0 / 0 |
| 1 | `p26_kronos_direct_kr57` | cal_57 | 120 x 2 / 2.40 s = 100 | 120 x 4 / 4.29 s = 112 | 0 / 0 |
| 2 | `p26_kronos_direct_kr57` | cal_57 | 120 x 2 / 2.40 s = 100 | 120 x 4 / 4.29 s = 112 | 0 / 0 |
| 3 | `bucket_wheel` | melee_bucket_wheel | 1080 x 1 / 2.00 s = 0 (laid) | 1080 x 1 / 2.00 s = 0 (laid) | 0 / 0 |
| 4 | `p26_kronos_close_autocannon_30` | cal_30 | 22 x 10 / 2.73 s = 80 | 22 x 10 / 2.50 s = 88 | 0 / 0 |
| 5 | `p26_kronos_close_boss_rockets` | rkt_grad_122 | 200 x 13 / 33.11 s = 79 | 200 x 13 / 8.44 s = 308 | 4.5 / 9 |

### typhon

Ground DPS **707 -> 619** (88 %); anti-air only 145 -> 145. Made up: `p26_typhon_sec_ty57` 2 barrels together.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `sam_post` | sam_9m317_buk | 320 x 2 / 4.40 s = 145 | 320 x 2 / 4.40 s = 145 | 2 / 0 |
| 1 | `p26_typhon_sec_ty57` | cal_57 | 120 x 2 / 1.15 s = 208 | 120 x 8 (2 together) / 4.29 s = 224 | 3 / 6 |
| 2 | `p26_typhon_sec_ty57` | cal_57 | 120 x 2 / 1.15 s = 208 | 120 x 8 (2 together) / 4.29 s = 224 | 3 / 6 |
| 3 | `p26_typhon_direct_ty100` | cal_100_105_he | 300 x 1 / 1.03 s = 290 | 300 x 2 / 3.50 s = 171 | 5 / 10 |

### ixion

Ground DPS **615 -> 280** (46 %); anti-air only 0 -> 0. **Not made up within 20 %** (see below).

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_ixion_125` | cal_125_ap | 400 x 1 / 1.03 s = 390 | 400 x 1 / 7.50 s = 53 | 0 / 0 |
| 1 | `p26_ixion_mg` | cal_12_7 | 15 x 100 / 13.33 s = 113 | 15 x 100 / 13.25 s = 113 | 0 / 0 |
| 2 | `p26_ixion_mg` | cal_12_7 | 15 x 100 / 13.33 s = 113 | 15 x 100 / 13.25 s = 113 | 0 / 0 |

### caspian

Ground DPS **260 -> 260** (100 %); anti-air only 0 -> 0.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `hover_ciws` | cal_30 | 12 x 60 / 6.00 s = 120 | 12 x 60 / 6.00 s = 120 | 0 / 0 |
| 1 | `zu23` | cal_23 | 7 x 50 / 5.00 s = 70 | 7 x 50 / 5.00 s = 70 | 0 / 0 |
| 2 | `zu23` | cal_23 | 7 x 50 / 5.00 s = 70 | 7 x 50 / 5.00 s = 70 | 0 / 0 |

### morrigan

Ground DPS **165 -> 165** (100 %); anti-air only 147 -> 147.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `air_to_air` | sam_aim_120_amraam | 294 x 1 / 3.99 s = 74 | 294 x 1 / 3.99 s = 74 | 2 / 0 |
| 1 | `air_to_air` | sam_aim_120_amraam | 294 x 1 / 3.99 s = 74 | 294 x 1 / 3.99 s = 74 | 2 / 0 |
| 2 | `guided_bomb` | bomb_gbu_39_sdb | 210 x 1 / 6.65 s = 32 | 210 x 1 / 6.65 s = 32 | 4 / 0 |
| 3 | `fighter_cannon` | cal_25 | 18 x 44 / 5.95 s = 133 | 18 x 44 / 5.95 s = 133 | 0 / 0 |

### bastion_mk0

Ground DPS **239 -> 130** (54 %); anti-air only 0 -> 0. Made up: `p26_bastion_direct_b100` 2 barrels together. **Not made up within 20 %** (see below).

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_bastion_sec_b240` | cal_240 | 1100 x 1 / 7.69 s = 143 | 1100 x 1 / 60.00 s = 18 | 10 / 20 |
| 1 | `p26_bastion_direct_b100` | cal_100_105_ap | 240 x 1 / 5.00 s = 48 | 240 x 2 (2 together) / 8.60 s = 56 | 0 / 0 |
| 2 | `p26_bastion_direct_b100` | cal_100_105_ap | 240 x 1 / 5.00 s = 48 | 240 x 2 (2 together) / 8.60 s = 56 | 0 / 0 |

### fenrir

Ground DPS **350 -> 380** (109 %); anti-air only 0 -> 0.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_jotunn_sec_jo_rockets` | rkt_smerch_300 | 450 x 8 / 33.78 s = 107 | 450 x 8 / 37.95 s = 95 | 8 / 16 |
| 1 | `p26_jotunn_sec_jo_rockets` | rkt_smerch_300 | 450 x 8 / 33.78 s = 107 | 450 x 8 / 37.95 s = 95 | 8 / 16 |
| 2 | `p26_jotunn_close_boss_flak` | cal_35 | 25 x 41 / 7.47 s = 137 | 25 x 41 / 5.38 s = 191 | 2.5 / 0 |

### scylla

Ground DPS **234 -> 380** (162 %); anti-air only 0 -> 0.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `naval_130_twin` | cal_127_130 | 380 x 2 / 4.75 s = 160 | 380 x 2 (2 together) / 3.00 s = 253 | 5 / 10 |
| 1 | `p26_leviathan_direct_lev127` | cal_127_130 | 380 x 1 / 5.10 s = 74 | 380 x 1 / 3.00 s = 127 | 0 / 0 |

### locust

Ground DPS **552 -> 575** (104 %); anti-air only 0 -> 0.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_matriarch_ma_drones` | drone_zala_lancet_3_swarm | 320 x 6 / 5.00 s = 384 | 320 x 6 / 5.00 s = 384 | 3 / 6 |
| 1 | `p26_matriarch_close_boss_flak` | cal_35 | 25 x 41 / 6.11 s = 168 | 25 x 41 / 5.38 s = 191 | 2.5 / 0 |

### behemoth_mk2

Ground DPS **569 -> 515** (90 %); anti-air only 0 -> 0.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_behemoth_main_be152` | cal_152_155 | 600 x 1 / 1.85 s = 325 | 600 x 2 (2 together) / 8.98 s = 134 | 7 / 14 |
| 1 | `p26_behemoth_close_boss_flak` | cal_35 | 25 x 41 / 8.41 s = 122 | 25 x 41 / 5.38 s = 191 | 2.5 / 0 |
| 2 | `p26_behemoth_close_boss_flak` | cal_35 | 25 x 41 / 8.41 s = 122 | 25 x 41 / 5.38 s = 191 | 2.5 / 0 |

### icarus_mk0

Ground DPS **400 -> 400** (100 %); anti-air only 0 -> 0.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_icarus_sec_orbital_laser` | laser_laser | 40 x 1 / 0.10 s = 400 | 40 x 1 / 0.10 s = 400 | 1.5 / 0 |

### argus

Ground DPS **316 -> 316** (100 %); anti-air only 0 -> 0.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_roc_main_roc_bombs` | bomb_400 | 700 x 8 / 35.44 s = 158 | 700 x 8 / 35.44 s = 158 | 10 / 20 |
| 1 | `p26_roc_main_roc_bombs` | bomb_400 | 700 x 8 / 35.44 s = 158 | 700 x 8 / 35.44 s = 158 | 10 / 20 |

### behemoth_mk0

Ground DPS **733 -> 637** (87 %); anti-air only 0 -> 0. Made up: `p26_behemoth_direct_be120` 2 barrels together, `p26_behemoth_sec_be_rockets` 40 tubes.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_behemoth_main_be152` | cal_152_155 | 600 x 1 / 1.85 s = 325 | 600 x 2 (2 together) / 8.98 s = 134 | 7 / 14 |
| 1 | `p26_behemoth_direct_be120` | cal_120_ap | 260 x 1 / 5.10 s = 51 | 260 x 2 (2 together) / 7.50 s = 69 | 0 / 0 |
| 2 | `p26_behemoth_direct_be120` | cal_120_ap | 260 x 1 / 5.10 s = 51 | 260 x 2 (2 together) / 7.50 s = 69 | 0 / 0 |
| 3 | `p26_behemoth_sec_be_rockets` | rkt_grad_122 | 200 x 8 / 5.23 s = 306 | 200 x 40 / 21.94 s = 365 | 4.5 / 9 |

### kraken

Ground DPS **771 -> 956** (124 %); anti-air only 804 -> 804.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_leviathan_lev406` | cal_406 | 2400 x 3 / 60.00 s = 0 (laid) | 2400 x 3 (3 together) / 60.00 s = 0 (laid) | 14 / 24 |
| 1 | `p26_leviathan_lev406` | cal_406 | 2400 x 3 / 60.00 s = 0 (laid) | 2400 x 3 (3 together) / 60.00 s = 0 (laid) | 14 / 24 |
| 2 | `p26_leviathan_lev406` | cal_406 | 2400 x 3 / 60.00 s = 0 (laid) | 2400 x 3 (3 together) / 60.00 s = 0 (laid) | 14 / 24 |
| 3 | `p26_leviathan_sec_lev155` | cal_152_155 | 600 x 3 / 13.71 s = 131 | 600 x 3 (3 together) / 10.50 s = 171 | 7 / 14 |
| 4 | `p26_leviathan_sec_lev155` | cal_152_155 | 600 x 3 / 13.71 s = 131 | 600 x 3 (3 together) / 10.50 s = 171 | 7 / 14 |
| 5 | `p26_leviathan_direct_lev127` | cal_127_130 | 380 x 1 / 5.10 s = 74 | 380 x 1 / 3.00 s = 127 | 0 / 0 |
| 6 | `p26_leviathan_direct_lev127` | cal_127_130 | 380 x 1 / 5.10 s = 74 | 380 x 1 / 3.00 s = 127 | 0 / 0 |
| 7 | `aa_25_triple` | cal_25 | 17 x 15 / 3.10 s = 82 | 17 x 15 / 3.10 s = 82 | 0 / 0 |
| 8 | `aa_25_triple` | cal_25 | 17 x 15 / 3.10 s = 82 | 17 x 15 / 3.10 s = 82 | 0 / 0 |
| 9 | `aa_25_triple` | cal_25 | 17 x 15 / 3.10 s = 82 | 17 x 15 / 3.10 s = 82 | 0 / 0 |
| 10 | `aa_25_triple` | cal_25 | 17 x 15 / 3.10 s = 82 | 17 x 15 / 3.10 s = 82 | 0 / 0 |
| 11 | `aa_25_triple` | cal_25 | 17 x 15 / 3.10 s = 82 | 17 x 15 / 3.10 s = 82 | 0 / 0 |
| 12 | `aa_25_triple` | cal_25 | 17 x 15 / 3.10 s = 82 | 17 x 15 / 3.10 s = 82 | 0 / 0 |
| 13 | `aa_25_triple` | cal_25 | 17 x 15 / 3.10 s = 82 | 17 x 15 / 3.10 s = 82 | 0 / 0 |
| 14 | `aa_25_triple` | cal_25 | 17 x 15 / 3.10 s = 82 | 17 x 15 / 3.10 s = 82 | 0 / 0 |
| 15 | `sam_post` | sam_9m317_buk | 320 x 2 / 4.40 s = 145 | 320 x 2 / 4.40 s = 145 | 2 / 0 |
| salvo | `p26_leviathan_lev406` | cal_406 | 2400 x 9 / 60.00 s = 360 | 2400 x 9 (3 together) / 60.00 s = 360 | 14 / 24 |

### monster

Ground DPS **792 -> 741** (94 %); anti-air only 0 -> 0. Made up: `p26_bastion_direct_b100` 2 barrels together.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_bastion_sec_b240` | cal_240 | 1100 x 1 / 7.69 s = 143 | 1100 x 1 / 60.00 s = 18 | 10 / 20 |
| 1 | `p26_bastion_direct_b100` | cal_100_105_ap | 240 x 1 / 5.00 s = 48 | 240 x 2 (2 together) / 8.60 s = 56 | 0 / 0 |
| 2 | `p26_bastion_direct_b100` | cal_100_105_ap | 240 x 1 / 5.00 s = 48 | 240 x 2 (2 together) / 8.60 s = 56 | 0 / 0 |
| 3 | `p26_bastion_tiny_autocannon_40` | cal_40 | 30 x 10 / 17.60 s = 17 | 30 x 10 / 3.32 s = 90 | 0 / 0 |
| 4 | `p26_bastion_tiny_autocannon_40` | cal_40 | 30 x 10 / 17.60 s = 17 | 30 x 10 / 3.32 s = 90 | 0 / 0 |
| 5 | `p26_bastion_tiny_kornet_twin` | atgm_kornet | 230 x 2 / 55.55 s = 8 | 230 x 2 / 20.00 s = 23 | 0 / 0 |
| 6 | `p26_bastion_close_boss_hmg` | cal_12_7 | 15 x 100 / 13.33 s = 113 | 15 x 100 / 13.25 s = 113 | 0 / 0 |
| 7 | `p26_bastion_close_boss_hmg` | cal_12_7 | 15 x 100 / 13.33 s = 113 | 15 x 100 / 13.25 s = 113 | 0 / 0 |
| 8 | `p26_bastion_main_b155` | cal_152_155 | 600 x 1 / 2.33 s = 258 | 600 x 1 / 15.00 s = 40 | 7 / 14 |
| 9 | `p26_bastion_tiny_zu23` | cal_23 | 7 x 50 / 25.00 s = 14 | 7 x 50 / 4.96 s = 71 | 0 / 0 |
| 10 | `p26_bastion_tiny_zu23` | cal_23 | 7 x 50 / 25.00 s = 14 | 7 x 50 / 4.96 s = 71 | 0 / 0 |

### garuda

Ground DPS **1532 -> 685** (45 %); anti-air only 0 -> 0. **Not made up within 20 %** (see below).

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_roc_main_roc_bombs` | bomb_400 | 700 x 8 / 35.44 s = 158 | 700 x 8 / 35.44 s = 158 | 10 / 20 |
| 1 | `p26_roc_main_roc_bombs` | bomb_400 | 700 x 8 / 35.44 s = 158 | 700 x 8 / 35.44 s = 158 | 10 / 20 |
| 2 | `p26_roc_direct_roc_atgm` | atgm_kornet | 230 x 1 / 1.98 s = 116 | 230 x 2 / 20.00 s = 23 | 0 / 0 |
| 3 | `p26_roc_direct_roc_atgm` | atgm_kornet | 230 x 1 / 1.98 s = 116 | 230 x 2 / 20.00 s = 23 | 0 / 0 |
| 4 | `p26_roc_close_twin_30_bmpt` | cal_30 | 22 x 12 / 1.86 s = 142 | 22 x 12 / 2.37 s = 112 | 0 / 0 |
| 5 | `p26_roc_close_twin_30_bmpt` | cal_30 | 22 x 12 / 1.86 s = 142 | 22 x 12 / 2.37 s = 112 | 0 / 0 |
| 6 | `p26_roc_roc105` | cal_100_105_he | 300 x 1 / 0.86 s = 350 | 300 x 1 / 6.00 s = 50 | 5 / 10 |
| 7 | `p26_roc_roc105` | cal_100_105_he | 300 x 1 / 0.86 s = 350 | 300 x 1 / 6.00 s = 50 | 5 / 10 |

### hyperion

Ground DPS **1320 -> 1320** (100 %); anti-air only 0 -> 0.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_icarus_sec_orbital_laser` | laser_laser | 40 x 1 / 0.10 s = 400 | 40 x 1 / 0.10 s = 400 | 1.5 / 0 |
| 1 | `p26_icarus_main_ic_coil` | rail_heavy_coilgun | 1500 x 1 / 5.00 s = 300 | 1500 x 1 / 5.00 s = 300 | 0 / 0 |
| 2 | `p26_icarus_main_ic_coil` | rail_heavy_coilgun | 1500 x 1 / 5.00 s = 300 | 1500 x 1 / 5.00 s = 300 | 0 / 0 |
| 3 | `p26_icarus_direct_ic_laser` | laser_tower | 16 x 1 / 0.10 s = 160 | 16 x 1 / 0.10 s = 160 | 1.5 / 0 |
| 4 | `p26_icarus_direct_ic_laser` | laser_tower | 16 x 1 / 0.10 s = 160 | 16 x 1 / 0.10 s = 160 | 1.5 / 0 |

### stymphalos

Ground DPS **622 -> 586** (94 %); anti-air only 0 -> 0.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_matriarch_ma_drones` | drone_zala_lancet_3_swarm | 320 x 6 / 5.00 s = 384 | 320 x 6 / 5.00 s = 384 | 3 / 6 |
| 1 | `p26_matriarch_close_boss_flak` | cal_35 | 25 x 41 / 6.11 s = 168 | 25 x 41 / 5.38 s = 191 | 2.5 / 0 |
| 2 | `p26_matriarch_direct_ma_atgm` | atgm_kornet | 230 x 1 / 3.29 s = 70 | 230 x 1 / 20.00 s = 12 | 0 / 0 |

### nyx

Ground DPS **239 -> 343** (144 %); anti-air only 0 -> 0.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `boss_railgun` | rail_railgun | 720 x 1 / 8.00 s = 90 | 720 x 1 / 8.00 s = 90 | 0 / 0 |
| 1 | `p26_leviathan_direct_lev127` | cal_127_130 | 380 x 1 / 5.10 s = 74 | 380 x 1 / 3.00 s = 127 | 0 / 0 |
| 2 | `p26_leviathan_direct_lev127` | cal_127_130 | 380 x 1 / 5.10 s = 74 | 380 x 1 / 3.00 s = 127 | 0 / 0 |

### cerberus

Ground DPS **875 -> 879** (101 %); anti-air only 0 -> 0. Made up: `p26_behemoth_sec_be_rockets` 40 tubes.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_behemoth_main_be152` | cal_152_155 | 600 x 1 / 1.85 s = 325 | 600 x 2 (2 together) / 8.98 s = 134 | 7 / 14 |
| 1 | `p26_behemoth_close_boss_flak` | cal_35 | 25 x 41 / 8.41 s = 122 | 25 x 41 / 5.38 s = 191 | 2.5 / 0 |
| 2 | `p26_behemoth_close_boss_flak` | cal_35 | 25 x 41 / 8.41 s = 122 | 25 x 41 / 5.38 s = 191 | 2.5 / 0 |
| 3 | `p26_behemoth_sec_be_rockets` | rkt_grad_122 | 200 x 8 / 5.23 s = 306 | 200 x 40 / 21.94 s = 365 | 4.5 / 9 |

### hydra

Ground DPS **707 -> 619** (88 %); anti-air only 0 -> 0. Made up: `p26_typhon_sec_ty57` 2 barrels together.

| mount | weapon | family | before: round x n / cycle = DPS | after: round x n (barrels) / cycle = DPS | core / edge |
|---|---|---|---|---|---|
| 0 | `p26_typhon_sec_ty57` | cal_57 | 120 x 2 / 1.15 s = 208 | 120 x 8 (2 together) / 4.29 s = 224 | 3 / 6 |
| 1 | `p26_typhon_sec_ty57` | cal_57 | 120 x 2 / 1.15 s = 208 | 120 x 8 (2 together) / 4.29 s = 224 | 3 / 6 |
| 2 | `p26_typhon_direct_ty100` | cal_100_105_he | 300 x 1 / 1.03 s = 290 | 300 x 2 / 3.50 s = 171 | 5 / 10 |

## Totals

| boss | ground before | ground after | after / before | anti-air before -> after | make-up |
|---|---|---|---|---|---|
| behemoth | 1012 | 1099 | 109 % | 0 -> 0 | `p26_behemoth_direct_be120` 2 barrels together, `p26_behemoth_sec_be_rockets` 40 tubes |
| mobile_fortress | 954 | 1204 | 126 % | 145 -> 145 | - |
| armored_train | 660 | 952 | 144 % | 0 -> 0 | - |
| mega_gunship | 462 | 546 | 118 % | 0 -> 0 | - |
| drone_mothership | 1304 | 1188 | 91 % | 0 -> 0 | - |
| nuke_train | 1751 | 1070 | 61 % **(< 80 %)** | 62 -> 62 | `p26_nemesis_sec_boss_rockets` 40 tubes |
| silver_bug | 1638 | 1501 | 92 % | 0 -> 0 | - |
| behemoth_inferno | 282 | 282 | 100 % | 0 -> 0 | - |
| behemoth_tempest | 299 | 299 | 100 % | 0 -> 0 | - |
| fortress_hive | 586 | 586 | 100 % | 0 -> 0 | - |
| fortress_bastion | 792 | 741 | 94 % | 0 -> 0 | `p26_bastion_direct_b100` 2 barrels together |
| rail_supergun | 170 | 170 | 100 % | 240 -> 240 | - |
| earth_borer | 289 | 213 | 74 % **(< 80 %)** | 0 -> 0 | - |
| command_airship | 1532 | 685 | 45 % **(< 80 %)** | 0 -> 0 | - |
| landing_hovercraft | 302 | 293 | 97 % | 120 -> 120 | - |
| supreme_command | 143 | 226 | 159 % | 0 -> 0 | - |
| sky_fortress | 418 | 418 | 100 % | 0 -> 0 | - |
| leviathan | 771 | 956 | 124 % | 804 -> 804 | - |
| moloch | 1382 | 652 | 47 % **(< 80 %)** | 0 -> 0 | `p26_moloch_direct_mo120ap` 2 barrels together, `p26_moloch_main_mo120` 2 barrels together |
| daedalus | 745 | 778 | 104 % | 0 -> 0 | `p26_daedalus_sec_dae57` 2 barrels together |
| kronos | 439 | 708 | 161 % | 0 -> 0 | - |
| typhon | 707 | 619 | 88 % | 145 -> 145 | `p26_typhon_sec_ty57` 2 barrels together |
| ixion | 615 | 280 | 46 % **(< 80 %)** | 0 -> 0 | - |
| caspian | 260 | 260 | 100 % | 0 -> 0 | - |
| morrigan | 165 | 165 | 100 % | 147 -> 147 | - |
| bastion_mk0 | 239 | 130 | 54 % **(< 80 %)** | 0 -> 0 | `p26_bastion_direct_b100` 2 barrels together |
| fenrir | 350 | 380 | 109 % | 0 -> 0 | - |
| scylla | 234 | 380 | 162 % | 0 -> 0 | - |
| locust | 552 | 575 | 104 % | 0 -> 0 | - |
| behemoth_mk2 | 569 | 515 | 90 % | 0 -> 0 | - |
| icarus_mk0 | 400 | 400 | 100 % | 0 -> 0 | - |
| argus | 316 | 316 | 100 % | 0 -> 0 | - |
| behemoth_mk0 | 733 | 637 | 87 % | 0 -> 0 | `p26_behemoth_direct_be120` 2 barrels together, `p26_behemoth_sec_be_rockets` 40 tubes |
| kraken | 771 | 956 | 124 % | 804 -> 804 | - |
| monster | 792 | 741 | 94 % | 0 -> 0 | `p26_bastion_direct_b100` 2 barrels together |
| garuda | 1532 | 685 | 45 % **(< 80 %)** | 0 -> 0 | - |
| hyperion | 1320 | 1320 | 100 % | 0 -> 0 | - |
| stymphalos | 622 | 586 | 94 % | 0 -> 0 | - |
| nyx | 239 | 343 | 144 % | 0 -> 0 | - |
| cerberus | 875 | 879 | 101 % | 0 -> 0 | `p26_behemoth_sec_be_rockets` 40 tubes |
| hydra | 707 | 619 | 88 % | 0 -> 0 | `p26_typhon_sec_ty57` 2 barrels together |

## Kept as they are

- `p26_roc_main_roc_bombs`: a 400 kg bomb stick from an airship's bay: no real rate for the bay's reload; the 35.4 s cycle kept.
- `p26_matriarch_ma_drones`: a six-drone swarm: no real rate and no wave 1 row (wave 1's mothership_drones is a 4-drone salvo).
- `p26_icarus_main_ic_coil`: a 64 MJ coilgun, its own family (rail_heavy_coilgun): no real rate.
- `p26_leviathan_lev406`: the 406 mm salvo every 60 s (prompt 34's trial table; 1.4 x the real gap after the 30 % rule).
- `p26_daedalus_direct_dae_laser`: a laser: no real rate.
- `p26_icarus_direct_ic_laser`: a laser: no real rate.
- `p26_icarus_sec_orbital_laser`: a laser: no real rate.
- `autocannon_40`: Gungnir's 40 mm guns: frozen (fix rule 8); their 1 m burst is Gungnir's own.
- `gunship_105`: shared with the player's AC-130: the player rule (Docs/balance/player_weapon_waitlist.md).
