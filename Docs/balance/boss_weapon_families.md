# Boss weapon families: before and after (prompt 34 L2)

Written by `Tools/balance/p34_boss_families.py` from `Tools/balance/p34_boss_baseline.json` (the numbers before).
The DPS is on paper: a weapon's sustained DPS on one target (a cycle's rounds over the cycle), before the boss's own
factors (weaponDamage, rank, phases), which this pass does not change. Each changed weapon keeps its DPS, except
where the family's core grew more than 1.25 times, which lengthens the cycle by the same ratio (the "bonus" column).
No battle was run.

## The family table (boss scale)

| family | tier | damage a round | core / edge (m) |
|---|---|---|---|
| 12.7 mm heavy machine gun (`cal_12_7`) | T0 | 15 | - |
| 23 mm (`cal_23`) | T1 | 7 | - |
| 30 mm (`cal_30`) | T1 | 22 | - |
| 35 mm Oerlikon (`cal_35`) | T1 | 25 | 2.5 (one layer) |
| 40 mm Bofors (`cal_40`) | T1 | 30 | - |
| 57 mm (`cal_57`) | T2 | 120 | 3 / 6 |
| 100-105 mm HE (`cal_100_105_he`) | T2 | 300 | 5 / 10 |
| 120 mm HE (`cal_120_he`) | T3 | 340 | 5 / 10 |
| 120 mm AP (`cal_120_ap`) | T3 | 260 | - |
| 125 mm AP (`cal_125_ap`) | T3 | 400 | - |
| 127-130 mm (`cal_127_130`) | T3 | 380 | 5 / 10 |
| 152-155 mm (`cal_152_155`) | T3 | 600 | 7 / 14 |
| 203 mm (`cal_203`) | T4 | 900 | 8.5 / 17 |
| 240 mm (`cal_240`) | T4 | 1100 | 10 / 20 |
| 406 mm (`cal_406`) | T5 | 2400 | 14 / 24 |
| Grad 122 mm rockets (`rkt_grad_122`) | T3 | 200 | 4.5 / 9 |
| Smerch 300 mm rockets (`rkt_smerch_300`) | T4 | 450 | 8 / 16 |
| 400 kg bomb (`bomb_400`) | T4 | 700 | 10 / 20 |
| 9M133 Kornet (`atgm_kornet`) | T2 | 230 | - |

## Per boss

### behemoth

Ground DPS on paper (anti-air mounts left out): **1012 -> 1012** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_behemoth_main_be152` | cal_152_155 | 650 x 1 / 2.00 s = 325 | 8.5 / 17 | 600 x 1 / 1.85 s = 325 | 7 / 14 |  |  |
| 1 | `p26_behemoth_tiny_be120` | cal_120_ap | 52 x 1 / 4.00 s = 13 | 0 / 0 | 260 x 1 / 20.00 s = 13 | 0 / 0 |  |  |
| 2 | `p26_behemoth_close_boss_flak` | cal_35 | 16 x 41 / 5.38 s = 122 | 2.5 / 0 | 25 x 41 / 8.41 s = 122 | 2.5 / 0 |  |  |
| 3 | `p26_behemoth_close_boss_flak` | cal_35 | 16 x 41 / 5.38 s = 122 | 2.5 / 0 | 25 x 41 / 8.41 s = 122 | 2.5 / 0 |  |  |
| 4 | `p26_behemoth_tiny_boss_missiles` | atgm_kornet | 46 x 1 / 6.39 s = 7 | 0 / 0 | 230 x 1 / 31.95 s = 7 | 0 / 0 |  |  |
| 5 | `p26_behemoth_tiny_boss_missiles` | atgm_kornet | 46 x 1 / 6.39 s = 7 | 0 / 0 | 230 x 1 / 31.95 s = 7 | 0 / 0 |  |  |
| 6 | `p26_behemoth_tiny_kornet_twin` | atgm_kornet | 46 x 2 / 11.11 s = 8 | 0 / 0 | 230 x 2 / 55.55 s = 8 | 0 / 0 |  |  |
| 7 | `p26_behemoth_direct_be120` | cal_120_ap | 255 x 1 / 5.00 s = 51 | 0 / 0 | 260 x 1 / 5.10 s = 51 | 0 / 0 |  |  |
| 8 | `p26_behemoth_direct_be120` | cal_120_ap | 255 x 1 / 5.00 s = 51 | 0 / 0 | 260 x 1 / 5.10 s = 51 | 0 / 0 |  |  |
| 9 | `p26_behemoth_sec_be_rockets` | rkt_grad_122 | 195 x 8 / 5.10 s = 306 | 5 / 10 | 200 x 8 / 5.23 s = 306 | 4.5 / 9 |  |  |

### mobile_fortress

Ground DPS on paper (anti-air mounts left out): **1082 -> 954** (88 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_jotunn_jo203` | cal_203 | 790 x 1 / 5.00 s = 158 | 10 / 20 | 900 x 1 / 5.70 s = 158 | 8.5 / 17 |  |  |
| 1 | `p26_jotunn_sec_jo_rockets` | rkt_smerch_300 | 130 x 8 / 6.10 s = 170 | 5 / 10 | 450 x 8 / 33.78 s = 107 | 8 / 16 | x1.60 |  |
| 2 | `p26_jotunn_sec_jo_rockets` | rkt_smerch_300 | 130 x 8 / 6.10 s = 170 | 5 / 10 | 450 x 8 / 33.78 s = 107 | 8 / 16 | x1.60 |  |
| 3 | `p26_jotunn_close_boss_flak` | cal_35 | 18 x 41 / 5.38 s = 137 | 2.5 / 0 | 25 x 41 / 7.47 s = 137 | 2.5 / 0 |  |  |
| 4 | `p26_jotunn_close_boss_flak` | cal_35 | 18 x 41 / 5.38 s = 137 | 2.5 / 0 | 25 x 41 / 7.47 s = 137 | 2.5 / 0 |  |  |
| 5 | `p26_jotunn_direct_jo125` | cal_125_ap | 290 x 1 / 2.50 s = 116 | 0 / 0 | 400 x 1 / 3.45 s = 116 | 0 / 0 |  |  |
| 6 | `p26_jotunn_tiny_twin_30_flak` | cal_30/flak | 1.5 x 160 / 7.00 s = 34 | 2.5 / 0 | 22 x 160 / 102.66 s = 34 | 2.5 / 0 |  |  |
| 7 | `p26_jotunn_jo203` | cal_203 | 790 x 1 / 5.00 s = 158 | 10 / 20 | 900 x 1 / 5.70 s = 158 | 8.5 / 17 |  |  |
| 8 | `sam_post` | sam_9m317_buk | 145 | | unchanged | | | not in the table |

### armored_train

Ground DPS on paper (anti-air mounts left out): **660 -> 660** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `train_gun` | cal_152_155/ap | 320 x 1 / 5.11 s = 63 | 2.5 / 0 | 600 x 1 / 9.58 s = 63 | 2.5 / 0 |  |  |
| 1 | `boss_rockets` | rkt_grad_122 | 57 x 13 / 8.94 s = 83 | 4.5 / 0 | 200 x 13 / 31.37 s = 83 | 4.5 / 9 |  |  |
| 2 | `boss_hmg` | cal_12_7 | 9.5 x 100 / 13.33 s = 71 | 0 / 0 | 15 x 100 / 21.05 s = 71 | 0 / 0 |  |  |
| 3 | `boss_flak` | cal_35 | 191 | | unchanged | | | a player vehicle carries it too (player weapons do not change) |
| 4 | `train_gun` | cal_152_155/ap | 320 x 1 / 5.11 s = 63 | 2.5 / 0 | 600 x 1 / 9.58 s = 63 | 2.5 / 0 |  |  |
| 5 | `boss_flak` | cal_35 | 191 | | unchanged | | | a player vehicle carries it too (player weapons do not change) |

### mega_gunship

Ground DPS on paper (anti-air mounts left out): **462 -> 462** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `gunship_rockets` | rkt_70_80 | 52 | | unchanged | | | not in the table |
| 1 | `boss_heli_gun` | cal_30 | 22 x 40 / 9.67 s = 91 | 0 / 0 | 22 x 40 / 9.67 s = 91 | 0 / 0 |  |  |
| 2 | `boss_heli_gun` | cal_30 | 22 x 40 / 9.67 s = 91 | 0 / 0 | 22 x 40 / 9.67 s = 91 | 0 / 0 |  |  |
| 3 | `boss_minigun` | cal_7_62 | 33 | | unchanged | | | not in the table |
| 4 | `gunship_rockets` | rkt_70_80 | 52 | | unchanged | | | not in the table |
| 5 | `boss_hmg` | cal_12_7 | 9.5 x 100 / 13.33 s = 71 | 0 / 0 | 15 x 100 / 21.05 s = 71 | 0 / 0 |  |  |
| 6 | `boss_hmg` | cal_12_7 | 9.5 x 100 / 13.33 s = 71 | 0 / 0 | 15 x 100 / 21.05 s = 71 | 0 / 0 |  |  |

### drone_mothership

Ground DPS on paper (anti-air mounts left out): **1303 -> 1304** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_matriarch_tiny_mothership_cannon` | cal_57 | 14 x 4 / 4.79 s = 12 | 3.5 / 0 | 120 x 4 / 41.06 s = 12 | 3 / 6 |  |  |
| 1 | `p26_matriarch_ma_drones` | drone_zala_lancet_3_swarm | 384 | | unchanged | | | not in the table |
| 2 | `p26_matriarch_close_boss_flak` | cal_35 | 22 x 41 / 5.38 s = 168 | 2.5 / 0 | 25 x 41 / 6.11 s = 168 | 2.5 / 0 |  |  |
| 3 | `p26_matriarch_close_boss_flak` | cal_35 | 22 x 41 / 5.38 s = 168 | 2.5 / 0 | 25 x 41 / 6.11 s = 168 | 2.5 / 0 |  |  |
| 4 | `p26_matriarch_tiny_mothership_cannon` | cal_57 | 14 x 4 / 4.79 s = 12 | 3.5 / 0 | 120 x 4 / 41.06 s = 12 | 3 / 6 |  |  |
| 5 | `p26_matriarch_direct_ma_atgm` | atgm_kornet | 350 x 1 / 5.00 s = 70 | 0 / 0 | 230 x 1 / 3.29 s = 70 | 0 / 0 |  |  |
| 6 | `p26_matriarch_sec_autocannon_30` | cal_30 | 42 x 10 / 2.00 s = 210 | 0 / 0 | 22 x 10 / 1.04 s = 211 | 0 / 0 |  | salvo interval 0.1111 -> 0.105 s |
| 7 | `p26_matriarch_sec_autocannon_30` | cal_30 | 42 x 10 / 2.00 s = 210 | 0 / 0 | 22 x 10 / 1.04 s = 211 | 0 / 0 |  | salvo interval 0.1111 -> 0.105 s |
| 8 | `p26_matriarch_direct_ma_atgm` | atgm_kornet | 350 x 1 / 5.00 s = 70 | 0 / 0 | 230 x 1 / 3.29 s = 70 | 0 / 0 |  |  |

### nuke_train

Ground DPS on paper (anti-air mounts left out): **1751 -> 1751** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_nemesis_main_ne152` | cal_152_155 | 655 x 4 / 4.50 s = 582 | 8.5 / 17 | 600 x 4 / 4.12 s = 582 | 7 / 14 |  |  |
| 1 | `p26_nemesis_close_boss_flak` | cal_35 | 19 x 41 / 5.38 s = 145 | 2.5 / 0 | 25 x 41 / 7.08 s = 145 | 2.5 / 0 |  |  |
| 2 | `p26_nemesis_close_boss_flak` | cal_35 | 19 x 41 / 5.38 s = 145 | 2.5 / 0 | 25 x 41 / 7.08 s = 145 | 2.5 / 0 |  |  |
| 3 | `p26_nemesis_sec_boss_rockets` | rkt_grad_122 | 305 x 13 / 7.20 s = 551 | 4.5 / 0 | 200 x 13 / 4.72 s = 551 | 4.5 / 9 |  | salvo interval 0.5 -> 0.385 s |
| 4 | `sam_battery` | sam_mim_104_patriot_pac_2 | 62 | | unchanged | | | not in the table |
| 5 | `p26_nemesis_direct_ne125` | cal_125_ap | 275 x 1 / 1.50 s = 183 | 0 / 0 | 400 x 1 / 2.18 s = 183 | 0 / 0 |  |  |
| 6 | `p26_nemesis_close_boss_flak` | cal_35 | 19 x 41 / 5.38 s = 145 | 2.5 / 0 | 25 x 41 / 7.08 s = 145 | 2.5 / 0 |  |  |

### silver_bug

Ground DPS on paper (anti-air mounts left out): **1638 -> 1638** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_icarus_sec_orbital_laser` | laser_laser | 400 | | unchanged | | | not in the table |
| 1 | `p26_icarus_main_ic_coil` | rail_coilgun | 300 | | unchanged | | | not in the table |
| 2 | `p26_icarus_main_ic_coil` | rail_coilgun | 300 | | unchanged | | | not in the table |
| 3 | `p26_icarus_direct_ic_laser` | laser_tower | 160 | | unchanged | | | not in the table |
| 4 | `p26_icarus_direct_ic_laser` | laser_tower | 160 | | unchanged | | | not in the table |
| 5 | `p26_icarus_close_autocannon_40` | cal_40 | 56 x 10 / 3.52 s = 159 | 1 / 0 | 30 x 10 / 1.89 s = 159 | 0 / 0 |  | cadence 0.2 -> 0.154 s (the magazine's change alone could not keep the DPS) |
| 6 | `p26_icarus_close_autocannon_40` | cal_40 | 56 x 10 / 3.52 s = 159 | 1 / 0 | 30 x 10 / 1.89 s = 159 | 0 / 0 |  | cadence 0.2 -> 0.154 s (the magazine's change alone could not keep the DPS) |

### behemoth_inferno

Ground DPS on paper (anti-air mounts left out): **282 -> 282** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `boss_flamer` | flame_flamethrower | 120 | | unchanged | | | not in the table |
| 1 | `boss_thermo` | rkt_tos_220 | 42 | | unchanged | | | not in the table |
| 2 | `boss_flamer` | flame_flamethrower | 120 | | unchanged | | | not in the table |

### behemoth_tempest

Ground DPS on paper (anti-air mounts left out): **299 -> 299** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `boss_railgun` | rail_railgun | 90 | | unchanged | | | not in the table |
| 1 | `coilgun` | rail_coilgun | 104 | | unchanged | | | not in the table |
| 2 | `coilgun` | rail_coilgun | 104 | | unchanged | | | not in the table |

### fortress_hive

Ground DPS on paper (anti-air mounts left out): **586 -> 586** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `mothership_drones` | drone_zala_lancet_3 | 102 | | unchanged | | | not in the table |
| 1 | `mothership_drones` | drone_zala_lancet_3 | 102 | | unchanged | | | not in the table |
| 2 | `boss_flak` | cal_35 | 191 | | unchanged | | | a player vehicle carries it too (player weapons do not change) |
| 3 | `boss_flak` | cal_35 | 191 | | unchanged | | | a player vehicle carries it too (player weapons do not change) |

### fortress_bastion

Ground DPS on paper (anti-air mounts left out): **792 -> 792** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_bastion_sec_b240` | cal_240 | 715 x 1 / 5.00 s = 143 | 10 / 20 | 1100 x 1 / 7.69 s = 143 | 10 / 20 |  |  |
| 1 | `p26_bastion_direct_b100` | cal_100_105_ap | 48 | | unchanged | | | not in the table |
| 2 | `p26_bastion_direct_b100` | cal_100_105_ap | 48 | | unchanged | | | not in the table |
| 3 | `p26_bastion_tiny_autocannon_40` | cal_40 | 6 x 10 / 3.52 s = 17 | 1 / 0 | 30 x 10 / 17.60 s = 17 | 0 / 0 |  |  |
| 4 | `p26_bastion_tiny_autocannon_40` | cal_40 | 6 x 10 / 3.52 s = 17 | 1 / 0 | 30 x 10 / 17.60 s = 17 | 0 / 0 |  |  |
| 5 | `p26_bastion_tiny_kornet_twin` | atgm_kornet | 46 x 2 / 11.11 s = 8 | 0 / 0 | 230 x 2 / 55.55 s = 8 | 0 / 0 |  |  |
| 6 | `p26_bastion_close_boss_hmg` | cal_12_7 | 15 x 100 / 13.33 s = 113 | 0 / 0 | 15 x 100 / 13.33 s = 113 | 0 / 0 |  |  |
| 7 | `p26_bastion_close_boss_hmg` | cal_12_7 | 15 x 100 / 13.33 s = 113 | 0 / 0 | 15 x 100 / 13.33 s = 113 | 0 / 0 |  |  |
| 8 | `p26_bastion_main_b155` | cal_152_155 | 515 x 1 / 2.00 s = 258 | 8.5 / 17 | 600 x 1 / 2.33 s = 258 | 7 / 14 |  |  |
| 9 | `p26_bastion_tiny_zu23` | cal_23 | 1.4 x 50 / 5.00 s = 14 | 0 / 0 | 7 x 50 / 25.00 s = 14 | 0 / 0 |  |  |
| 10 | `p26_bastion_tiny_zu23` | cal_23 | 1.4 x 50 / 5.00 s = 14 | 0 / 0 | 7 x 50 / 25.00 s = 14 | 0 / 0 |  |  |

### rail_supergun

Ground DPS on paper (anti-air mounts left out): **170 -> 170** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 1 | `autocannon_40` | cal_40 | 85 | | unchanged | | | Gungnir carries it (rail_supergun: family and tier only) |
| 2 | `autocannon_40` | cal_40 | 85 | | unchanged | | | Gungnir carries it (rail_supergun: family and tier only) |
| 3 | `ciws_aa` | cal_30 | 120 | | unchanged | | | Gungnir carries it (rail_supergun: family and tier only) |
| 4 | `ciws_aa` | cal_30 | 120 | | unchanged | | | Gungnir carries it (rail_supergun: family and tier only) |

### earth_borer

Ground DPS on paper (anti-air mounts left out): **289 -> 289** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `borer_drill` | melee_drill_head | 173 | | unchanged | | | not in the table |
| 1 | `borer_cannon` | cal_76 | 58 | | unchanged | | | not in the table |
| 2 | `borer_cannon` | cal_76 | 58 | | unchanged | | | not in the table |

### command_airship

Ground DPS on paper (anti-air mounts left out): **1848 -> 1532** (83 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_roc_main_roc_bombs` | bomb_400 | 320 x 8 / 8.10 s = 316 | 5 / 10 | 700 x 8 / 35.44 s = 158 | 10 / 20 | x2.00 |  |
| 1 | `p26_roc_main_roc_bombs` | bomb_400 | 320 x 8 / 8.10 s = 316 | 5 / 10 | 700 x 8 / 35.44 s = 158 | 10 / 20 | x2.00 |  |
| 2 | `p26_roc_direct_roc_atgm` | atgm_kornet | 290 x 1 / 2.50 s = 116 | 0 / 0 | 230 x 1 / 1.98 s = 116 | 0 / 0 |  |  |
| 3 | `p26_roc_direct_roc_atgm` | atgm_kornet | 290 x 1 / 2.50 s = 116 | 0 / 0 | 230 x 1 / 1.98 s = 116 | 0 / 0 |  |  |
| 4 | `p26_roc_close_twin_30_bmpt` | cal_30 | 25 x 12 / 2.12 s = 142 | 0 / 0 | 22 x 12 / 1.86 s = 142 | 0 / 0 |  |  |
| 5 | `p26_roc_close_twin_30_bmpt` | cal_30 | 25 x 12 / 2.12 s = 142 | 0 / 0 | 22 x 12 / 1.86 s = 142 | 0 / 0 |  |  |
| 6 | `p26_roc_roc105` | cal_100_105_he | 700 x 1 / 2.00 s = 350 | 6 / 12 | 300 x 1 / 0.86 s = 350 | 5 / 10 |  |  |
| 7 | `p26_roc_roc105` | cal_100_105_he | 700 x 1 / 2.00 s = 350 | 6 / 12 | 300 x 1 / 0.86 s = 350 | 5 / 10 |  |  |

### landing_hovercraft

Ground DPS on paper (anti-air mounts left out): **302 -> 302** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `hover_ciws` | cal_30 | 120 | | unchanged | | | a player vehicle carries it too (player weapons do not change) |
| 1 | `hover_ciws` | cal_30 | 120 | | unchanged | | | a player vehicle carries it too (player weapons do not change) |
| 2 | `ciws_aa` | cal_30 | 120 | | unchanged | | | Gungnir carries it (rail_supergun: family and tier only) |
| 3 | `hover_rockets` | rkt_140 | 31 | | unchanged | | | not in the table |
| 4 | `hover_rockets` | rkt_140 | 31 | | unchanged | | | not in the table |

### supreme_command

Ground DPS on paper (anti-air mounts left out): **143 -> 143** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `boss_hmg` | cal_12_7 | 9.5 x 100 / 13.33 s = 71 | 0 / 0 | 15 x 100 / 21.05 s = 71 | 0 / 0 |  |  |
| 1 | `boss_hmg` | cal_12_7 | 9.5 x 100 / 13.33 s = 71 | 0 / 0 | 15 x 100 / 21.05 s = 71 | 0 / 0 |  |  |

### sky_fortress

Ground DPS on paper (anti-air mounts left out): **418 -> 418** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `gunship_105` | cal_100_105_he | 73 | | unchanged | | | a player vehicle carries it too (player weapons do not change) |
| 1 | `gunship_40mm` | cal_40/he | 145 | | unchanged | | | a player vehicle carries it too (player weapons do not change) |
| 2 | `gunship_25mm` | cal_25 | 158 | | unchanged | | | not in the table |
| 3 | `griffin` | atgm_agm_176_griffin | 42 | | unchanged | | | not in the table |

### leviathan

Ground DPS on paper (anti-air mounts left out): **771 -> 771** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 3 | `p26_leviathan_sec_lev155` | cal_152_155 | 175 x 3 / 4.00 s = 131 | 8.5 / 17 | 600 x 3 / 13.71 s = 131 | 7 / 14 |  |  |
| 4 | `p26_leviathan_sec_lev155` | cal_152_155 | 175 x 3 / 4.00 s = 131 | 8.5 / 17 | 600 x 3 / 13.71 s = 131 | 7 / 14 |  |  |
| 5 | `p26_leviathan_direct_lev127` | cal_127_130/ap | 335 x 1 / 4.50 s = 74 | 0 / 0 | 380 x 1 / 5.10 s = 74 | 0 / 0 |  |  |
| 6 | `p26_leviathan_direct_lev127` | cal_127_130/ap | 335 x 1 / 4.50 s = 74 | 0 / 0 | 380 x 1 / 5.10 s = 74 | 0 / 0 |  |  |
| 7 | `aa_25_triple` | cal_25/flak | 82 | | unchanged | | | not in the table |
| 8 | `aa_25_triple` | cal_25/flak | 82 | | unchanged | | | not in the table |
| 9 | `aa_25_triple` | cal_25/flak | 82 | | unchanged | | | not in the table |
| 10 | `aa_25_triple` | cal_25/flak | 82 | | unchanged | | | not in the table |
| 11 | `aa_25_triple` | cal_25/flak | 82 | | unchanged | | | not in the table |
| 12 | `aa_25_triple` | cal_25/flak | 82 | | unchanged | | | not in the table |
| 13 | `aa_25_triple` | cal_25/flak | 82 | | unchanged | | | not in the table |
| 14 | `aa_25_triple` | cal_25/flak | 82 | | unchanged | | | not in the table |
| 15 | `sam_post` | sam_9m317_buk | 145 | | unchanged | | | not in the table |
| salvo | `p26_leviathan_lev406` | cal_406 | 3 x 1 x 1200 / 10 s = 360 | 12 / 20 | 3 x 3 x 2400 / 60.0 s = 360 | 14 / 24 | | barrels together |

### moloch

Ground DPS on paper (anti-air mounts left out): **1381 -> 1382** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_moloch_main_mo120` | cal_120_he | 300 x 1 / 1.00 s = 300 | 5 / 10 | 340 x 1 / 1.13 s = 300 | 5 / 10 |  |  |
| 1 | `p26_moloch_tiny_zu23` | cal_23 | 1.4 x 50 / 5.00 s = 14 | 0 / 0 | 7 x 50 / 25.00 s = 14 | 0 / 0 |  |  |
| 2 | `p26_moloch_tiny_zu23` | cal_23 | 1.4 x 50 / 5.00 s = 14 | 0 / 0 | 7 x 50 / 25.00 s = 14 | 0 / 0 |  |  |
| 3 | `p26_moloch_main_mo120` | cal_120_he | 300 x 1 / 1.00 s = 300 | 5 / 10 | 340 x 1 / 1.13 s = 300 | 5 / 10 |  |  |
| 4 | `p26_moloch_direct_mo120ap` | cal_120_ap | 220 x 1 / 2.00 s = 110 | 0 / 0 | 260 x 1 / 2.36 s = 110 | 0 / 0 |  |  |
| 5 | `p26_moloch_direct_mo120ap` | cal_120_ap | 220 x 1 / 2.00 s = 110 | 0 / 0 | 260 x 1 / 2.36 s = 110 | 0 / 0 |  |  |
| 6 | `p26_moloch_close_boss_flak` | cal_35 | 70 x 41 / 5.38 s = 533 | 2.5 / 0 | 25 x 41 / 1.92 s = 534 | 2.5 / 0 |  | cadence 0.05 -> 0.0355 s (the magazine's change alone could not keep the DPS) |

### daedalus

Ground DPS on paper (anti-air mounts left out): **745 -> 745** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_daedalus_direct_dae_laser` | laser_targeting_laser | 165 | | unchanged | | | not in the table |
| 1 | `p26_daedalus_sec_dae57` | cal_57 | 135 x 2 / 1.30 s = 208 | 3.5 / 7 | 120 x 2 / 1.16 s = 208 | 3 / 6 |  |  |
| 2 | `p26_daedalus_sec_dae57` | cal_57 | 135 x 2 / 1.30 s = 208 | 3.5 / 7 | 120 x 2 / 1.16 s = 208 | 3 / 6 |  |  |
| 3 | `p26_daedalus_direct_dae_laser` | laser_targeting_laser | 165 | | unchanged | | | not in the table |

### kronos

Ground DPS on paper (anti-air mounts left out): **439 -> 439** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_kronos_close_autocannon_30` | cal_30 | 21 x 10 / 2.61 s = 80 | 0 / 0 | 22 x 10 / 2.73 s = 80 | 0 / 0 |  |  |
| 1 | `p26_kronos_direct_kr57` | cal_57/ap | 100 x 2 / 2.00 s = 100 | 0 / 0 | 120 x 2 / 2.40 s = 100 | 0 / 0 |  |  |
| 2 | `p26_kronos_direct_kr57` | cal_57/ap | 100 x 2 / 2.00 s = 100 | 0 / 0 | 120 x 2 / 2.40 s = 100 | 0 / 0 |  |  |
| 4 | `p26_kronos_close_autocannon_30` | cal_30 | 21 x 10 / 2.61 s = 80 | 0 / 0 | 22 x 10 / 2.73 s = 80 | 0 / 0 |  |  |
| 5 | `p26_kronos_close_boss_rockets` | rkt_grad_122 | 54 x 13 / 8.94 s = 79 | 4.5 / 0 | 200 x 13 / 33.11 s = 79 | 4.5 / 9 |  |  |

### typhon

Ground DPS on paper (anti-air mounts left out): **707 -> 707** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `sam_post` | sam_9m317_buk | 145 | | unchanged | | | not in the table |
| 1 | `p26_typhon_sec_ty57` | cal_57 | 125 x 2 / 1.20 s = 208 | 3 / 6 | 120 x 2 / 1.15 s = 208 | 3 / 6 |  |  |
| 2 | `p26_typhon_sec_ty57` | cal_57 | 125 x 2 / 1.20 s = 208 | 3 / 6 | 120 x 2 / 1.15 s = 208 | 3 / 6 |  |  |
| 3 | `p26_typhon_direct_ty100` | cal_100_105_he | 580 x 1 / 2.00 s = 290 | 5 / 10 | 300 x 1 / 1.03 s = 290 | 5 / 10 |  |  |

### ixion

Ground DPS on paper (anti-air mounts left out): **615 -> 615** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_ixion_125` | cal_125_ap | 780 x 1 / 2.00 s = 390 | 0 / 0 | 400 x 1 / 1.03 s = 390 | 0 / 0 |  |  |
| 1 | `p26_ixion_mg` | cal_12_7 | 15 x 100 / 13.33 s = 113 | 0 / 0 | 15 x 100 / 13.33 s = 113 | 0 / 0 |  |  |
| 2 | `p26_ixion_mg` | cal_12_7 | 15 x 100 / 13.33 s = 113 | 0 / 0 | 15 x 100 / 13.33 s = 113 | 0 / 0 |  |  |

### caspian

Ground DPS on paper (anti-air mounts left out): **260 -> 260** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `hover_ciws` | cal_30 | 120 | | unchanged | | | a player vehicle carries it too (player weapons do not change) |
| 1 | `zu23` | cal_23 | 70 | | unchanged | | | a player vehicle carries it too (player weapons do not change) |
| 2 | `zu23` | cal_23 | 70 | | unchanged | | | a player vehicle carries it too (player weapons do not change) |

### morrigan

Ground DPS on paper (anti-air mounts left out): **165 -> 165** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `air_to_air` | sam_aim_120_amraam | 74 | | unchanged | | | not in the table |
| 1 | `air_to_air` | sam_aim_120_amraam | 74 | | unchanged | | | not in the table |
| 2 | `guided_bomb` | bomb_gbu_39_sdb | 32 | | unchanged | | | not in the table |
| 3 | `fighter_cannon` | cal_25/flak | 133 | | unchanged | | | not in the table |

### bastion_mk0

Ground DPS on paper (anti-air mounts left out): **239 -> 239** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_bastion_sec_b240` | cal_240 | 715 x 1 / 5.00 s = 143 | 10 / 20 | 1100 x 1 / 7.69 s = 143 | 10 / 20 |  |  |
| 1 | `p26_bastion_direct_b100` | cal_100_105_ap | 48 | | unchanged | | | not in the table |
| 2 | `p26_bastion_direct_b100` | cal_100_105_ap | 48 | | unchanged | | | not in the table |

### fenrir

Ground DPS on paper (anti-air mounts left out): **478 -> 350** (73 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_jotunn_sec_jo_rockets` | rkt_smerch_300 | 130 x 8 / 6.10 s = 170 | 5 / 10 | 450 x 8 / 33.78 s = 107 | 8 / 16 | x1.60 |  |
| 1 | `p26_jotunn_sec_jo_rockets` | rkt_smerch_300 | 130 x 8 / 6.10 s = 170 | 5 / 10 | 450 x 8 / 33.78 s = 107 | 8 / 16 | x1.60 |  |
| 2 | `p26_jotunn_close_boss_flak` | cal_35 | 18 x 41 / 5.38 s = 137 | 2.5 / 0 | 25 x 41 / 7.47 s = 137 | 2.5 / 0 |  |  |

### scylla

Ground DPS on paper (anti-air mounts left out): **234 -> 234** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `naval_130_twin` | cal_127_130 | 160 x 2 / 2.00 s = 160 | 5 / 0 | 380 x 2 / 4.75 s = 160 | 5 / 10 |  |  |
| 1 | `p26_leviathan_direct_lev127` | cal_127_130/ap | 335 x 1 / 4.50 s = 74 | 0 / 0 | 380 x 1 / 5.10 s = 74 | 0 / 0 |  |  |

### locust

Ground DPS on paper (anti-air mounts left out): **552 -> 552** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_matriarch_ma_drones` | drone_zala_lancet_3_swarm | 384 | | unchanged | | | not in the table |
| 1 | `p26_matriarch_close_boss_flak` | cal_35 | 22 x 41 / 5.38 s = 168 | 2.5 / 0 | 25 x 41 / 6.11 s = 168 | 2.5 / 0 |  |  |

### behemoth_mk2

Ground DPS on paper (anti-air mounts left out): **569 -> 569** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_behemoth_main_be152` | cal_152_155 | 650 x 1 / 2.00 s = 325 | 8.5 / 17 | 600 x 1 / 1.85 s = 325 | 7 / 14 |  |  |
| 1 | `p26_behemoth_close_boss_flak` | cal_35 | 16 x 41 / 5.38 s = 122 | 2.5 / 0 | 25 x 41 / 8.41 s = 122 | 2.5 / 0 |  |  |
| 2 | `p26_behemoth_close_boss_flak` | cal_35 | 16 x 41 / 5.38 s = 122 | 2.5 / 0 | 25 x 41 / 8.41 s = 122 | 2.5 / 0 |  |  |

### icarus_mk0

Ground DPS on paper (anti-air mounts left out): **400 -> 400** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_icarus_sec_orbital_laser` | laser_laser | 400 | | unchanged | | | not in the table |

### argus

Ground DPS on paper (anti-air mounts left out): **632 -> 316** (50 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_roc_main_roc_bombs` | bomb_400 | 320 x 8 / 8.10 s = 316 | 5 / 10 | 700 x 8 / 35.44 s = 158 | 10 / 20 | x2.00 |  |
| 1 | `p26_roc_main_roc_bombs` | bomb_400 | 320 x 8 / 8.10 s = 316 | 5 / 10 | 700 x 8 / 35.44 s = 158 | 10 / 20 | x2.00 |  |

### behemoth_mk0

Ground DPS on paper (anti-air mounts left out): **733 -> 733** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_behemoth_main_be152` | cal_152_155 | 650 x 1 / 2.00 s = 325 | 8.5 / 17 | 600 x 1 / 1.85 s = 325 | 7 / 14 |  |  |
| 1 | `p26_behemoth_direct_be120` | cal_120_ap | 255 x 1 / 5.00 s = 51 | 0 / 0 | 260 x 1 / 5.10 s = 51 | 0 / 0 |  |  |
| 2 | `p26_behemoth_direct_be120` | cal_120_ap | 255 x 1 / 5.00 s = 51 | 0 / 0 | 260 x 1 / 5.10 s = 51 | 0 / 0 |  |  |
| 3 | `p26_behemoth_sec_be_rockets` | rkt_grad_122 | 195 x 8 / 5.10 s = 306 | 5 / 10 | 200 x 8 / 5.23 s = 306 | 4.5 / 9 |  |  |

### kraken

Ground DPS on paper (anti-air mounts left out): **771 -> 771** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 3 | `p26_leviathan_sec_lev155` | cal_152_155 | 175 x 3 / 4.00 s = 131 | 8.5 / 17 | 600 x 3 / 13.71 s = 131 | 7 / 14 |  |  |
| 4 | `p26_leviathan_sec_lev155` | cal_152_155 | 175 x 3 / 4.00 s = 131 | 8.5 / 17 | 600 x 3 / 13.71 s = 131 | 7 / 14 |  |  |
| 5 | `p26_leviathan_direct_lev127` | cal_127_130/ap | 335 x 1 / 4.50 s = 74 | 0 / 0 | 380 x 1 / 5.10 s = 74 | 0 / 0 |  |  |
| 6 | `p26_leviathan_direct_lev127` | cal_127_130/ap | 335 x 1 / 4.50 s = 74 | 0 / 0 | 380 x 1 / 5.10 s = 74 | 0 / 0 |  |  |
| 7 | `aa_25_triple` | cal_25/flak | 82 | | unchanged | | | not in the table |
| 8 | `aa_25_triple` | cal_25/flak | 82 | | unchanged | | | not in the table |
| 9 | `aa_25_triple` | cal_25/flak | 82 | | unchanged | | | not in the table |
| 10 | `aa_25_triple` | cal_25/flak | 82 | | unchanged | | | not in the table |
| 11 | `aa_25_triple` | cal_25/flak | 82 | | unchanged | | | not in the table |
| 12 | `aa_25_triple` | cal_25/flak | 82 | | unchanged | | | not in the table |
| 13 | `aa_25_triple` | cal_25/flak | 82 | | unchanged | | | not in the table |
| 14 | `aa_25_triple` | cal_25/flak | 82 | | unchanged | | | not in the table |
| 15 | `sam_post` | sam_9m317_buk | 145 | | unchanged | | | not in the table |
| salvo | `p26_leviathan_lev406` | cal_406 | 3 x 1 x 1200 / 10 s = 360 | 12 / 20 | 3 x 3 x 2400 / 60.0 s = 360 | 14 / 24 | | barrels together |

### monster

Ground DPS on paper (anti-air mounts left out): **792 -> 792** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_bastion_sec_b240` | cal_240 | 715 x 1 / 5.00 s = 143 | 10 / 20 | 1100 x 1 / 7.69 s = 143 | 10 / 20 |  |  |
| 1 | `p26_bastion_direct_b100` | cal_100_105_ap | 48 | | unchanged | | | not in the table |
| 2 | `p26_bastion_direct_b100` | cal_100_105_ap | 48 | | unchanged | | | not in the table |
| 3 | `p26_bastion_tiny_autocannon_40` | cal_40 | 6 x 10 / 3.52 s = 17 | 1 / 0 | 30 x 10 / 17.60 s = 17 | 0 / 0 |  |  |
| 4 | `p26_bastion_tiny_autocannon_40` | cal_40 | 6 x 10 / 3.52 s = 17 | 1 / 0 | 30 x 10 / 17.60 s = 17 | 0 / 0 |  |  |
| 5 | `p26_bastion_tiny_kornet_twin` | atgm_kornet | 46 x 2 / 11.11 s = 8 | 0 / 0 | 230 x 2 / 55.55 s = 8 | 0 / 0 |  |  |
| 6 | `p26_bastion_close_boss_hmg` | cal_12_7 | 15 x 100 / 13.33 s = 113 | 0 / 0 | 15 x 100 / 13.33 s = 113 | 0 / 0 |  |  |
| 7 | `p26_bastion_close_boss_hmg` | cal_12_7 | 15 x 100 / 13.33 s = 113 | 0 / 0 | 15 x 100 / 13.33 s = 113 | 0 / 0 |  |  |
| 8 | `p26_bastion_main_b155` | cal_152_155 | 515 x 1 / 2.00 s = 258 | 8.5 / 17 | 600 x 1 / 2.33 s = 258 | 7 / 14 |  |  |
| 9 | `p26_bastion_tiny_zu23` | cal_23 | 1.4 x 50 / 5.00 s = 14 | 0 / 0 | 7 x 50 / 25.00 s = 14 | 0 / 0 |  |  |
| 10 | `p26_bastion_tiny_zu23` | cal_23 | 1.4 x 50 / 5.00 s = 14 | 0 / 0 | 7 x 50 / 25.00 s = 14 | 0 / 0 |  |  |

### garuda

Ground DPS on paper (anti-air mounts left out): **1848 -> 1532** (83 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_roc_main_roc_bombs` | bomb_400 | 320 x 8 / 8.10 s = 316 | 5 / 10 | 700 x 8 / 35.44 s = 158 | 10 / 20 | x2.00 |  |
| 1 | `p26_roc_main_roc_bombs` | bomb_400 | 320 x 8 / 8.10 s = 316 | 5 / 10 | 700 x 8 / 35.44 s = 158 | 10 / 20 | x2.00 |  |
| 2 | `p26_roc_direct_roc_atgm` | atgm_kornet | 290 x 1 / 2.50 s = 116 | 0 / 0 | 230 x 1 / 1.98 s = 116 | 0 / 0 |  |  |
| 3 | `p26_roc_direct_roc_atgm` | atgm_kornet | 290 x 1 / 2.50 s = 116 | 0 / 0 | 230 x 1 / 1.98 s = 116 | 0 / 0 |  |  |
| 4 | `p26_roc_close_twin_30_bmpt` | cal_30 | 25 x 12 / 2.12 s = 142 | 0 / 0 | 22 x 12 / 1.86 s = 142 | 0 / 0 |  |  |
| 5 | `p26_roc_close_twin_30_bmpt` | cal_30 | 25 x 12 / 2.12 s = 142 | 0 / 0 | 22 x 12 / 1.86 s = 142 | 0 / 0 |  |  |
| 6 | `p26_roc_roc105` | cal_100_105_he | 700 x 1 / 2.00 s = 350 | 6 / 12 | 300 x 1 / 0.86 s = 350 | 5 / 10 |  |  |
| 7 | `p26_roc_roc105` | cal_100_105_he | 700 x 1 / 2.00 s = 350 | 6 / 12 | 300 x 1 / 0.86 s = 350 | 5 / 10 |  |  |

### hyperion

Ground DPS on paper (anti-air mounts left out): **1320 -> 1320** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_icarus_sec_orbital_laser` | laser_laser | 400 | | unchanged | | | not in the table |
| 1 | `p26_icarus_main_ic_coil` | rail_coilgun | 300 | | unchanged | | | not in the table |
| 2 | `p26_icarus_main_ic_coil` | rail_coilgun | 300 | | unchanged | | | not in the table |
| 3 | `p26_icarus_direct_ic_laser` | laser_tower | 160 | | unchanged | | | not in the table |
| 4 | `p26_icarus_direct_ic_laser` | laser_tower | 160 | | unchanged | | | not in the table |

### stymphalos

Ground DPS on paper (anti-air mounts left out): **622 -> 622** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_matriarch_ma_drones` | drone_zala_lancet_3_swarm | 384 | | unchanged | | | not in the table |
| 1 | `p26_matriarch_close_boss_flak` | cal_35 | 22 x 41 / 5.38 s = 168 | 2.5 / 0 | 25 x 41 / 6.11 s = 168 | 2.5 / 0 |  |  |
| 2 | `p26_matriarch_direct_ma_atgm` | atgm_kornet | 350 x 1 / 5.00 s = 70 | 0 / 0 | 230 x 1 / 3.29 s = 70 | 0 / 0 |  |  |

### nyx

Ground DPS on paper (anti-air mounts left out): **239 -> 239** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `boss_railgun` | rail_railgun | 90 | | unchanged | | | not in the table |
| 1 | `p26_leviathan_direct_lev127` | cal_127_130/ap | 335 x 1 / 4.50 s = 74 | 0 / 0 | 380 x 1 / 5.10 s = 74 | 0 / 0 |  |  |
| 2 | `p26_leviathan_direct_lev127` | cal_127_130/ap | 335 x 1 / 4.50 s = 74 | 0 / 0 | 380 x 1 / 5.10 s = 74 | 0 / 0 |  |  |

### cerberus

Ground DPS on paper (anti-air mounts left out): **875 -> 875** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_behemoth_main_be152` | cal_152_155 | 650 x 1 / 2.00 s = 325 | 8.5 / 17 | 600 x 1 / 1.85 s = 325 | 7 / 14 |  |  |
| 1 | `p26_behemoth_close_boss_flak` | cal_35 | 16 x 41 / 5.38 s = 122 | 2.5 / 0 | 25 x 41 / 8.41 s = 122 | 2.5 / 0 |  |  |
| 2 | `p26_behemoth_close_boss_flak` | cal_35 | 16 x 41 / 5.38 s = 122 | 2.5 / 0 | 25 x 41 / 8.41 s = 122 | 2.5 / 0 |  |  |
| 3 | `p26_behemoth_sec_be_rockets` | rkt_grad_122 | 195 x 8 / 5.10 s = 306 | 5 / 10 | 200 x 8 / 5.23 s = 306 | 4.5 / 9 |  |  |

### hydra

Ground DPS on paper (anti-air mounts left out): **707 -> 707** (100 %).

| mount | weapon | family | before: round x n / cycle = DPS | core / edge | after | core / edge | bonus | note |
|---|---|---|---|---|---|---|---|---|
| 0 | `p26_typhon_sec_ty57` | cal_57 | 125 x 2 / 1.20 s = 208 | 3 / 6 | 120 x 2 / 1.15 s = 208 | 3 / 6 |  |  |
| 1 | `p26_typhon_sec_ty57` | cal_57 | 125 x 2 / 1.20 s = 208 | 3 / 6 | 120 x 2 / 1.15 s = 208 | 3 / 6 |  |  |
| 2 | `p26_typhon_direct_ty100` | cal_100_105_he | 580 x 1 / 2.00 s = 290 | 5 / 10 | 300 x 1 / 1.03 s = 290 | 5 / 10 |  |  |

## Totals

| boss | before | after | after / before |
|---|---|---|---|
| behemoth | 1012 | 1012 | 100 % |
| mobile_fortress | 1082 | 954 | 88 % |
| armored_train | 660 | 660 | 100 % |
| mega_gunship | 462 | 462 | 100 % |
| drone_mothership | 1303 | 1304 | 100 % |
| nuke_train | 1751 | 1751 | 100 % |
| silver_bug | 1638 | 1638 | 100 % |
| behemoth_inferno | 282 | 282 | 100 % |
| behemoth_tempest | 299 | 299 | 100 % |
| fortress_hive | 586 | 586 | 100 % |
| fortress_bastion | 792 | 792 | 100 % |
| rail_supergun | 170 | 170 | 100 % |
| earth_borer | 289 | 289 | 100 % |
| command_airship | 1848 | 1532 | 83 % |
| landing_hovercraft | 302 | 302 | 100 % |
| supreme_command | 143 | 143 | 100 % |
| sky_fortress | 418 | 418 | 100 % |
| leviathan | 771 | 771 | 100 % |
| moloch | 1381 | 1382 | 100 % |
| daedalus | 745 | 745 | 100 % |
| kronos | 439 | 439 | 100 % |
| typhon | 707 | 707 | 100 % |
| ixion | 615 | 615 | 100 % |
| caspian | 260 | 260 | 100 % |
| morrigan | 165 | 165 | 100 % |
| bastion_mk0 | 239 | 239 | 100 % |
| fenrir | 478 | 350 | 73 % |
| scylla | 234 | 234 | 100 % |
| locust | 552 | 552 | 100 % |
| behemoth_mk2 | 569 | 569 | 100 % |
| icarus_mk0 | 400 | 400 | 100 % |
| argus | 632 | 316 | 50 % |
| behemoth_mk0 | 733 | 733 | 100 % |
| kraken | 771 | 771 | 100 % |
| monster | 792 | 792 | 100 % |
| garuda | 1848 | 1532 | 83 % |
| hyperion | 1320 | 1320 | 100 % |
| stymphalos | 622 | 622 | 100 % |
| nyx | 239 | 239 | 100 % |
| cerberus | 875 | 875 | 100 % |
| hydra | 707 | 707 | 100 % |

## Left alone

- `autocannon_40`: Gungnir carries it (rail_supergun: family and tier only).
- `boss_flak`: a player vehicle carries it too (player weapons do not change).
- `ciws_aa`: Gungnir carries it (rail_supergun: family and tier only).
- `gunship_105`: a player vehicle carries it too (player weapons do not change).
- `gunship_40mm`: a player vehicle carries it too (player weapons do not change).
- `hover_ciws`: a player vehicle carries it too (player weapons do not change).
- `zu23`: a player vehicle carries it too (player weapons do not change).
