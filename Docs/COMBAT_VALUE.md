# Machine Brigade: combat value and damage tables (prompt 13)

Generated from the measurements (`CombatValueMeasure`, `MB_BALANCE=1`, one fixed seed, 13): "pre13" is the data before prompt 13, "after B" the data now. Decisions are in DECISIONS.md 13C. Raw files: `Docs/balance/*.tsv`.

## 1. Theoretical damage a second, corrected (A.1)

All mounts added up, against each armour (damage table and plain armour bonuses included). "Old" is the old way: every weapon firing its salvo or magazine over and over with no reload. "Now" counts a launcher's rounds per load and its reload in place, and an aircraft's stores per full load and their rearm at the holding pattern's full rate (prompt 13 C). It is still a weapon firing whenever it can: the real figure is in section 2.

| Vehicle | Class | CP | Old light / heavy / air / structure | Now light / heavy / air / structure | Heavy per CP |
|---|---|---|---|---|---|
| scout_jeep | Scout | 2 | 49 / 12 / 15 / 15 | 49 / 12 / 15 / 15 | 6.1 |
| vbied | Scout | 3 | 700 / 420 / 0 / 525 | 700 / 420 / 0 / 525 | 140.0 |
| armored_car | Light | 3 | 91 / 23 / 13 / 27 | 91 / 29 / 13 / 32 | 9.7 |
| ifv | Light | 5 | 115 / 41 / 13 / 40 | 115 / 49 / 13 / 46 | 9.7 |
| light_tank | Tank | 4 | 63 / 38 / 13 / 29 | 63 / 38 / 13 / 29 | 9.6 |
| turtle_tank | Tank | 8 | 75 / 54 / 13 / 39 | 75 / 54 / 13 / 39 | 6.8 |
| bmpt | Tank | 9 | 178 / 84 / 13 / 87 | 178 / 95 / 13 / 96 | 10.6 |
| flame_tank | Heavy | 5 | 152 / 55 / 13 / 101 | 152 / 55 / 13 / 101 | 10.9 |
| armored_bulldozer | Heavy | 7 | 77 / 40 / 14 / 138 | 76 / 40 / 14 / 138 | 5.7 |
| main_battle_tank | Heavy | 7 | 123 / 66 / 27 / 53 | 123 / 66 / 27 / 53 | 9.5 |
| twin_tank | Heavy | 9 | 143 / 92 / 27 / 69 | 143 / 92 / 27 / 69 | 10.3 |
| heavy_tank | Heavy | 10 | 150 / 81 / 14 / 65 | 150 / 89 / 14 / 71 | 8.9 |
| siege_tank | Heavy | 12 | 91 / 38 / 14 / 169 | 83 / 33 / 14 / 138 | 2.7 |
| titan_tank | Heavy | 14 | 193 / 159 / 27 / 109 | 193 / 159 / 27 / 109 | 11.3 |
| atgm_carrier | TankHunter | 6 | 83 / 58 / 14 / 42 | 83 / 58 / 14 / 42 | 9.7 |
| fpv_carrier | TankHunter | 6 | 86 / 63 / 14 / 60 | 76 / 49 / 14 / 48 | 8.2 |
| tank_destroyer | TankHunter | 6 | 96 / 76 / 14 / 53 | 96 / 76 / 14 / 53 | 12.7 |
| lancet_truck | TankHunter | 7 | 63 / 32 / 14 / 32 | 59 / 26 / 14 / 27 | 3.8 |
| wheeled_gun | TankHunter | 7 | 91 / 76 / 13 / 52 | 91 / 76 / 13 / 52 | 10.8 |
| railgun_truck | TankHunter | 9 | 51 / 68 / 0 / 41 | 51 / 68 / 0 / 41 | 7.5 |
| rocket_technical | Artillery | 3 | 75 / 28 / 15 / 53 | 68 / 24 / 15 / 43 | 7.9 |
| mortar_carrier | Artillery | 4 | 72 / 26 / 14 / 50 | 66 / 23 / 14 / 41 | 5.6 |
| mlrs | Artillery | 5 | 90 / 37 / 14 / 77 | 79 / 31 / 14 / 61 | 6.1 |
| artillery | Artillery | 6 | 72 / 26 / 14 / 50 | 68 / 24 / 14 / 44 | 4.0 |
| shahed_truck | Artillery | 8 | 95 / 40 / 14 / 85 | 83 / 33 / 14 / 67 | 4.1 |
| heavy_rocket_artillery | Artillery | 9 | 131 / 62 / 14 / 139 | 110 / 49 / 14 / 107 | 5.5 |
| thermobaric_launcher | Artillery | 9 | 102 / 44 / 14 / 96 | 88 / 36 / 14 / 74 | 4.0 |
| ballistic_launcher | Artillery | 11 | 101 / 44 / 14 / 94 | 87 / 35 / 14 / 72 | 3.2 |
| zu23_technical | AntiAir | 3 | 52 / 13 / 196 / 13 | 52 / 13 / 196 / 13 | 4.4 |
| aa_vehicle | AntiAir | 4 | 35 / 9 / 184 / 9 | 35 / 9 / 184 / 9 | 2.2 |
| sam_launcher | AntiAir | 5 | 48 / 12 / 168 / 14 | 48 / 12 / 169 / 14 | 2.4 |
| heavy_aa | AntiAir | 7 | 94 / 23 / 403 / 23 | 94 / 23 / 403 / 23 | 3.3 |
| iron_beam | AntiAir | 9 | 0 / 0 / 105 / 0 | 0 / 0 / 105 / 0 | 0.0 |
| long_sam | AntiAir | 11 | 0 / 0 / 112 / 0 | 0 / 0 / 112 / 0 | 0.0 |
| supply_truck | Support | 0 | 49 / 12 / 15 / 15 | 49 / 12 / 15 / 15 |  |
| smoke_carrier | Support | 3 | 48 / 12 / 14 / 14 | 48 / 12 / 14 / 14 | 4.0 |
| engineer_vehicle | Support | 4 | 48 / 12 / 14 / 14 | 48 / 12 / 14 / 14 | 3.0 |
| counter_battery_radar | Support | 5 | 48 / 12 / 14 / 14 | 48 / 12 / 14 / 14 | 2.4 |
| ew_jammer | Support | 5 | 48 / 12 / 14 / 14 | 48 / 12 / 14 / 14 | 2.4 |
| mine_layer | Support | 5 | 48 / 12 / 14 / 14 | 48 / 12 / 14 / 14 | 2.4 |
| sapper | Support | 5 | 48 / 12 / 14 / 14 | 48 / 12 / 14 / 14 | 2.4 |
| command_vehicle | Support | 6 | 48 / 12 / 14 / 14 | 48 / 12 / 14 / 14 | 2.0 |
| scout_heli | Helicopter | 6 | 90 / 36 / 16 / 73 | 90 / 36 / 16 / 73 | 6.0 |
| attack_helicopter | Helicopter | 9 | 148 / 91 / 50 / 107 | 148 / 101 / 39 / 114 | 11.2 |
| gunship_heli | Helicopter | 14 | 305 / 245 / 35 / 221 | 305 / 245 / 35 / 221 | 17.5 |
| heavy_attack_heli | Helicopter | 14 | 201 / 124 / 56 / 152 | 201 / 136 / 47 / 161 | 9.7 |
| recon_drone | Plane | 6 | 11 / 15 / 0 / 9 | 11 / 15 / 0 / 9 | 2.5 |
| strike_drone | Plane | 7 | 80 / 85 / 0 / 105 | 72 / 80 / 0 / 93 | 11.5 |
| fighter_jet | Plane | 10 | 50 / 13 / 450 / 13 | 50 / 13 / 311 / 13 | 1.3 |
| attack_jet | Plane | 13 | 372 / 414 / 38 / 377 | 372 / 414 / 23 / 377 | 31.8 |
| tank_buster | Plane | 18 | 497 / 616 / 41 / 443 | 497 / 616 / 25 / 443 | 34.2 |
| heavy_bomber | Plane | 20 | 422 / 253 / 21 / 633 | 413 / 248 / 21 / 619 | 12.4 |
| stealth_bomber | Plane | 20 | 254 / 152 / 0 / 381 | 232 / 139 / 0 / 348 | 7.0 |
| sky_gunship | Plane | 22 | 389 / 203 / 0 / 383 | 381 / 211 / 0 / 391 | 9.6 |
| aa_turret | Defense | 0 | 94 / 23 / 403 / 23 | 94 / 23 / 403 / 23 |  |
| aa_turret.flak | Defense | 0 | 60 / 15 / 224 / 15 | 60 / 15 / 224 / 15 |  |
| aa_turret.sam | Defense | 0 | 48 / 12 / 168 / 14 | 48 / 12 / 169 / 14 |  |
| airfield | Defense | 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |  |
| ammo_depot | Defense | 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |  |
| artillery_emplacement | Defense | 0 | 66 / 25 / 13 / 49 | 62 / 23 / 13 / 43 |  |
| artillery_emplacement.cb | Defense | 0 | 66 / 25 / 13 / 49 | 62 / 23 / 13 / 43 |  |
| artillery_emplacement.ext | Defense | 0 | 64 / 24 / 13 / 45 | 60 / 21 / 13 / 40 |  |
| atgm_tower | Defense | 0 | 33 / 44 / 0 / 26 | 33 / 44 / 0 / 26 |  |
| atgm_tower.multi | Defense | 0 | 33 / 35 / 13 / 26 | 33 / 35 / 13 / 26 |  |
| atgm_tower.top | Defense | 0 | 33 / 61 / 0 / 26 | 33 / 61 / 0 / 26 |  |
| bulwark_post | Defense | 0 | 87 / 22 / 26 / 26 | 87 / 22 / 26 / 26 |  |
| c_ram | Defense | 0 | 0 / 0 / 122 / 0 | 0 / 0 / 122 / 0 |  |
| c_ram.centurion | Defense | 0 | 0 / 0 / 122 / 0 | 0 / 0 / 122 / 0 |  |
| c_ram.hunter | Defense | 0 | 0 / 0 / 122 / 0 | 0 / 0 / 122 / 0 |  |
| dragons_teeth | Defense | 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |  |
| dragons_teeth.hedgehog | Defense | 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |  |
| dragons_teeth.wire | Defense | 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |  |
| drone_hangar | Defense | 0 | 10 / 13 / 0 / 12 | 10 / 13 / 0 / 12 |  |
| drone_hangar.lancet | Defense | 0 | 9 / 12 / 0 / 11 | 9 / 12 / 0 / 11 |  |
| drone_hangar.swarm | Defense | 0 | 16 / 21 / 0 / 19 | 16 / 21 / 0 / 19 |  |
| ew_tower | Defense | 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |  |
| ew_tower.drone | Defense | 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |  |
| ew_tower.spoof | Defense | 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |  |
| guard_tower | Defense | 0 | 56 / 17 / 14 / 26 | 56 / 17 / 14 / 26 |  |
| guard_tower.nest | Defense | 0 | 56 / 17 / 0 / 26 | 57 / 23 / 0 / 31 |  |
| guard_tower.watch | Defense | 0 | 56 / 17 / 14 / 26 | 56 / 17 / 14 / 26 |  |
| gun_pit | Defense | 0 | 81 / 62 / 0 / 44 | 81 / 62 / 0 / 44 |  |
| gun_pit.ambush | Defense | 0 | 81 / 62 / 0 / 44 | 81 / 62 / 0 / 44 |  |
| gun_pit.deep | Defense | 0 | 81 / 62 / 0 / 44 | 81 / 62 / 0 / 44 |  |
| gun_turret | Defense | 0 | 67 / 44 / 0 / 33 | 67 / 44 / 0 / 33 |  |
| gun_turret.auto | Defense | 0 | 71 / 49 / 0 / 36 | 71 / 49 / 0 / 36 |  |
| gun_turret.long | Defense | 0 | 64 / 40 / 0 / 30 | 64 / 40 / 0 / 30 |  |
| headquarters | Defense | 0 | 367 / 192 / 882 / 144 | 367 / 191 / 883 / 144 |  |
| heavy_turret | Defense | 0 | 115 / 54 / 0 / 121 | 115 / 54 / 0 / 121 |  |
| heavy_turret.bastion | Defense | 0 | 115 / 54 / 0 / 121 | 115 / 54 / 0 / 121 |  |
| heavy_turret.coastal | Defense | 0 | 115 / 54 / 0 / 121 | 115 / 54 / 0 / 121 |  |
| logistics_station | Defense | 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |  |
| mg_bunker | Defense | 0 | 93 / 30 / 26 / 31 | 93 / 30 / 26 / 31 |  |
| mg_bunker.flame | Defense | 0 | 130 / 52 / 0 / 104 | 130 / 52 / 0 / 104 |  |
| mg_bunker.twin | Defense | 0 | 112 / 34 / 32 / 36 | 112 / 34 / 32 / 36 |  |
| minefield | Defense | 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |  |
| minefield.at | Defense | 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |  |
| minefield.scatter | Defense | 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |  |
| missile_battery | Defense | 0 | 48 / 12 / 111 / 14 | 48 / 12 / 111 / 14 |  |
| missile_battery.lrr | Defense | 0 | 48 / 12 / 111 / 14 | 48 / 12 / 111 / 14 |  |
| missile_battery.pac3 | Defense | 0 | 48 / 12 / 150 / 14 | 48 / 12 / 150 / 14 |  |
| radar_station | Defense | 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |  |
| repair_bay | Defense | 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |  |
| rocket_turret | Defense | 0 | 83 / 35 / 13 / 74 | 83 / 35 / 13 / 74 |  |
| rocket_turret.cluster | Defense | 0 | 75 / 30 / 13 / 62 | 86 / 37 / 13 / 78 |  |
| rocket_turret.thermo | Defense | 0 | 93 / 41 / 13 / 112 | 93 / 41 / 13 / 112 |  |
| spawn_bastion | Defense | 0 | 135 / 134 / 13 / 86 | 135 / 133 / 13 / 86 |  |
| super_gun | Defense | 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |  |
| targeting_station | Defense | 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |  |

## 2. Combat value per CP (A.2-A.4)

Each vehicle, rank 1 with no equipment, in a group of about 14 CP of its kind led by the tactical AI, attacks a reference group for 90 s (a destroyed group comes back as another wave): light (3 armoured cars and a jeep), tanks (2 battle tanks), fort (a gun turret and an MG bunker), air (an attack helicopter and an attack jet), and the three ground groups with anti-air (an AA vehicle; an AA tower at the fort). Aircraft and launchers also fight a mixed group with anti-air for 4 minutes (long). Value = real damage (never more than the victim had left) x (1 + share of the time alive) / 2 / CP. "Ground" is the mean over the six ground groups, the like-for-like figure for anything that fights the ground; "real DPS" is what one vehicle delivered a second while it lived (against the tanks, and the fort).

| Vehicle | Class | CP | Ground (pre13) | Ground (after B) | Change | Light | Tanks | Fort | Air | +AA (L/T/F) | Long | On target | Survival s | Real DPS tanks / fort |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| scout_jeep | Scout | 2 | 20 | 21 | +1 % | 45 | 14 | 20 | 5 | 16 / 24 / 6 |  | 23 % | 22 | 3 / 6 |
| vbied | Scout | 3 | 100 | 95 | -6 % | 129 | 83 | 132 | 0 | 113 / 26 / 85 |  | 2 % | 10 | 54 / 67 |
| armored_car | Light | 3 | 73 | 84 | +15 % | 147 | 61 | 55 | 7 | 129 / 78 / 31 |  | 58 % | 19 | 14 / 13 |
| ifv | Light | 5 | 81 | 90 | +12 % | 144 | 78 | 43 | 6 | 156 / 109 / 12 |  | 44 % | 32 | 27 / 6 |
| light_tank | Tank | 4 | 213 | 166 | -22 % | 294 | 98 | 91 | 17 | 383 / 68 / 60 |  | 53 % | 52 | 16 / 13 |
| turtle_tank | Tank | 8 | 257 | 252 | -2 % | 392 | 290 | 191 | 0 | 358 / 172 / 106 |  | 59 % | 73 | 32 / 22 |
| bmpt | Tank | 9 | 383 | 416 | +8 % | 784 | 309 | 344 | 8 | 801 / 257 / 0 |  | 63 % | 65 | 58 / 51 |
| flame_tank | Heavy | 5 | 289 | 223 | -23 % | 598 | 80 | 0 | 15 | 585 / 78 / 0 |  | 35 % | 56 | 14 / 0 |
| armored_bulldozer | Heavy | 7 | 237 | 203 | -14 % | 507 | 98 | 0 | 18 | 521 / 92 / 0 |  | 52 % | 64 | 20 / 0 |
| main_battle_tank | Heavy | 7 | 414 | 390 | -6 % | 689 | 295 | 198 | 15 | 695 / 247 / 215 |  | 64 % | 65 | 46 / 16 |
| twin_tank | Heavy | 9 | 464 | 443 | -4 % | 686 | 342 | 300 | 17 | 782 / 392 / 157 |  | 65 % | 68 | 55 / 46 |
| heavy_tank | Heavy | 10 | 297 | 293 | -1 % | 728 | 446 | 0 | 12 | 585 / 0 / 0 |  | 42 % | 79 | 65 / 0 |
| siege_tank | Heavy | 12 | 449 | 454 | +1 % | 257 | 204 | 917 | 13 | 260 / 219 / 865 | 491 | 84 % | 82 | 27 / 122 |
| titan_tank | Heavy | 14 | 493 | 490 | -1 % | 600 | 728 | 393 | 15 | 611 / 607 / 0 |  | 68 % | 82 | 113 / 61 |
| atgm_carrier | TankHunter | 6 | 172 | 188 | +9 % | 191 | 188 | 368 | 5 | 226 / 126 / 28 |  | 60 % | 52 | 12 / 25 |
| fpv_carrier | TankHunter | 6 | 477 | 477 | +0 % | 338 | 562 | 567 | 7 | 330 / 530 / 536 | 1083 | 88 % | 79 | 37 / 38 |
| tank_destroyer | TankHunter | 6 | 495 | 435 | -12 % | 665 | 308 | 525 | 10 | 723 / 389 / 0 |  | 66 % | 61 | 61 / 35 |
| lancet_truck | TankHunter | 7 | 212 | 212 | +0 % | 161 | 321 | 170 | 4 | 161 / 292 / 170 | 851 | 91 % | 78 | 25 / 13 |
| wheeled_gun | TankHunter | 7 | 113 | 86 | -24 % | 122 | 141 | 71 | 1 | 67 / 82 / 30 |  | 68 % | 24 | 34 / 33 |
| railgun_truck | TankHunter | 9 | 392 | 392 | +0 % | 323 | 553 | 348 | 0 | 299 / 499 / 335 |  | 83 % | 79 | 55 / 35 |
| rocket_technical | Artillery | 3 | 234 | 236 | +1 % | 81 | 23 | 717 | 1 | 48 / 39 / 509 | 163 | 44 % | 40 | 6 / 24 |
| mortar_carrier | Artillery | 4 | 350 | 336 | -4 % | 246 | 248 | 525 | 7 | 279 / 142 / 573 | 194 | 81 % | 76 | 11 / 23 |
| mlrs | Artillery | 5 | 599 | 530 | -12 % | 320 | 360 | 846 | 0 | 417 / 358 / 878 | 995 | 82 % | 90 | 20 / 47 |
| artillery | Artillery | 6 | 276 | 293 | +6 % | 212 | 220 | 448 | 0 | 260 / 237 / 378 | 563 | 84 % | 90 | 15 / 30 |
| shahed_truck | Artillery | 8 | 378 | 378 | +0 % | 178 | 267 | 606 | 0 | 215 / 315 / 688 | 531 | 84 % | 90 | 24 / 54 |
| heavy_rocket_artillery | Artillery | 9 | 522 | 558 | +7 % | 388 | 431 | 814 | 0 | 468 / 411 / 834 | 1238 | 82 % | 90 | 43 / 81 |
| thermobaric_launcher | Artillery | 9 | 229 | 228 | -1 % | 313 | 107 | 211 | 7 | 310 / 93 / 331 | 119 | 42 % | 69 | 17 / 21 |
| ballistic_launcher | Artillery | 11 | 540 | 490 | -9 % | 464 | 325 | 619 | 0 | 464 / 341 / 724 | 967 | 84 % | 90 | 40 / 76 |
| zu23_technical | AntiAir | 3 | 42 | 43 | +2 % | 87 | 30 | 23 | 87 | 60 / 49 / 10 |  | 45 % | 16 | 8 / 8 |
| aa_vehicle | AntiAir | 4 | 81 | 83 | +3 % | 140 | 46 | 81 | 232 | 144 / 82 / 9 |  | 59 % | 38 | 7 / 8 |
| sam_launcher | AntiAir | 5 | 8 | 7 | -12 % | 0 | 0 | 0 | 201 | 0 / 42 / 0 |  | 9 % | 74 | 0 / 0 |
| heavy_aa | AntiAir | 7 | 140 | 135 | -4 % | 177 | 72 | 275 | 150 | 186 / 71 / 29 |  | 68 % | 36 | 17 / 21 |
| iron_beam | AntiAir | 9 | 0 | 0 |  | 0 | 0 | 0 | 26 | 0 / 0 / 0 |  | 7 % | 68 | 0 / 0 |
| long_sam | AntiAir | 11 | 0 | 0 |  | 0 | 0 | 0 | 632 | 0 / 0 / 0 |  | 12 % | 90 | 0 / 0 |
| smoke_carrier | Support | 3 | 83 | 81 | -3 % | 171 | 48 | 11 | 17 | 179 / 68 / 9 |  | 43 % | 34 | 8 / 1 |
| engineer_vehicle | Support | 4 | 0 | 0 |  | 0 | 0 | 0 | 0 | 0 / 0 / 0 |  | 0 % | 90 | 0 / 0 |
| counter_battery_radar | Support | 5 | 0 | 0 |  | 0 | 0 | 0 | 0 | 0 / 0 / 0 |  | 0 % | 90 | 0 / 0 |
| ew_jammer | Support | 5 | 0 | 0 |  | 0 | 0 | 0 | 0 | 0 / 0 / 0 |  | 0 % | 90 | 0 / 0 |
| mine_layer | Support | 5 | 40 | 55 | +37 % | 95 | 114 | 7 | 11 | 67 / 44 / 3 |  | 30 % | 35 | 20 / 1 |
| sapper | Support | 5 | 251 | 208 | -17 % | 499 | 55 | 21 | 17 | 524 / 96 / 50 |  | 49 % | 63 | 7 / 2 |
| command_vehicle | Support | 6 | 0 | 0 |  | 0 | 0 | 0 | 0 | 0 / 0 / 0 |  | 0 % | 90 | 0 / 0 |
| scout_heli | Helicopter | 6 | 155 | 149 | -4 % | 358 | 176 | 290 | 18 | 25 / 20 / 24 | 0 | 44 % | 31 | 21 / 56 |
| attack_helicopter | Helicopter | 9 | 380 | 392 | +3 % | 729 | 685 | 642 | 138 | 54 / 206 / 35 | 38 | 62 % | 51 | 84 / 92 |
| gunship_heli | Helicopter | 14 | 465 | 395 | -15 % | 679 | 766 | 722 | 26 | 66 / 99 / 39 | 0 | 62 % | 57 | 119 / 112 |
| heavy_attack_heli | Helicopter | 14 | 215 | 238 | +11 % | 222 | 321 | 193 | 68 | 223 / 277 / 193 | 768 | 89 % | 86 | 50 / 30 |
| recon_drone | Plane | 6 | 47 | 47 | -1 % | 97 | 91 | 72 | 0 | 6 / 8 / 5 | 12 | 52 % | 35 | 12 / 8 |
| strike_drone | Plane | 7 | 335 | 339 | +1 % | 546 | 630 | 782 | 0 | 35 / 30 / 9 | 25 | 55 % | 44 | 64 / 65 |
| fighter_jet | Plane | 10 | 0 | 0 |  | 0 | 0 | 0 | 192 | 0 / 0 / 0 | 0 | 10 % | 43 | 0 / 0 |
| attack_jet | Plane | 13 | 483 | 521 | +8 % | 975 | 902 | 1143 | 12 | 46 / 7 / 54 | 10 | 53 % | 44 | 130 / 189 |
| tank_buster | Plane | 18 | 589 | 489 | -17 % | 785 | 1125 | 915 | 39 | 42 / 26 / 39 | 38 | 60 % | 50 | 225 / 183 |
| heavy_bomber | Plane | 20 | 557 | 542 | -3 % | 435 | 876 | 1474 | 33 | 103 / 184 / 181 | 177 | 40 % | 58 | 195 / 328 |
| stealth_bomber | Plane | 20 | 504 | 459 | -9 % | 420 | 675 | 1156 | 0 | 156 / 192 / 153 | 246 | 35 % | 69 | 150 / 257 |

