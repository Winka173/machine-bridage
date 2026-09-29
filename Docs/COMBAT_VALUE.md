# Machine Brigade: combat value and damage tables (prompt 13)

Generated from the measurements (`CombatValueMeasure`, `MB_BALANCE=1`, one fixed seed, 13): "pre13x3" is the data before prompt 13, "after F (final)" the data now. Decisions are in DECISIONS.md 13C. Raw files: `Docs/balance/*.tsv`.

## 1. Theoretical damage a second, corrected (A.1)

All mounts added up, against each armour (damage table and plain armour bonuses included). "Old" is the old way: every weapon firing its salvo or magazine over and over with no reload. "Now" counts a launcher's rounds per load and its reload in place, and an aircraft's stores per full load and their rearm at the holding pattern's full rate (prompt 13 C). It is still a weapon firing whenever it can: the real figure is in section 2.

| Vehicle | Class | CP | Old light / heavy / air / structure | Now light / heavy / air / structure | Heavy per CP |
|---|---|---|---|---|---|
| scout_jeep | Scout | 2 | 49 / 12 / 15 / 15 | 49 / 12 / 15 / 15 | 6.1 |
| vbied | Scout | 3 | 700 / 420 / 0 / 525 | 700 / 420 / 0 / 525 | 140.0 |
| armored_car | Light | 3 | 91 / 23 / 13 / 27 | 91 / 29 / 13 / 32 | 9.7 |
| ifv | Light | 5 | 115 / 41 / 13 / 40 | 115 / 49 / 13 / 46 | 9.7 |
| light_tank | Tank | 4 | 63 / 38 / 13 / 29 | 63 / 38 / 13 / 29 | 9.6 |
| turtle_tank | Tank | 7 | 75 / 54 / 13 / 39 | 75 / 54 / 13 / 39 | 7.8 |
| bmpt | Tank | 9 | 178 / 84 / 13 / 87 | 178 / 95 / 13 / 96 | 10.6 |
| flame_tank | Heavy | 5 | 152 / 55 / 13 / 101 | 152 / 55 / 13 / 101 | 10.9 |
| armored_bulldozer | Heavy | 7 | 77 / 40 / 14 / 138 | 76 / 40 / 14 / 138 | 5.7 |
| main_battle_tank | Heavy | 7 | 123 / 66 / 27 / 53 | 123 / 66 / 27 / 53 | 9.5 |
| twin_tank | Heavy | 9 | 143 / 92 / 27 / 69 | 143 / 92 / 27 / 69 | 10.3 |
| heavy_tank | Heavy | 10 | 150 / 81 / 14 / 65 | 150 / 89 / 14 / 71 | 8.9 |
| siege_tank | Heavy | 12 | 91 / 38 / 14 / 169 | 83 / 33 / 14 / 138 | 2.7 |
| titan_tank | Heavy | 14 | 193 / 159 / 27 / 109 | 193 / 159 / 27 / 109 | 11.3 |
| atgm_carrier | TankHunter | 5 | 83 / 58 / 14 / 42 | 94 / 73 / 14 / 51 | 14.7 |
| fpv_carrier | TankHunter | 6 | 86 / 63 / 14 / 60 | 76 / 49 / 14 / 48 | 8.2 |
| lancet_truck | TankHunter | 6 | 63 / 32 / 14 / 32 | 59 / 26 / 14 / 27 | 4.4 |
| wheeled_gun | TankHunter | 6 | 91 / 76 / 13 / 52 | 97 / 83 / 13 / 56 | 13.9 |
| tank_destroyer | TankHunter | 7 | 96 / 76 / 14 / 53 | 96 / 76 / 14 / 53 | 10.9 |
| railgun_truck | TankHunter | 9 | 51 / 68 / 0 / 41 | 51 / 68 / 0 / 41 | 7.5 |
| rocket_technical | Artillery | 3 | 75 / 28 / 15 / 53 | 70 / 25 / 15 / 46 | 8.2 |
| mortar_carrier | Artillery | 4 | 72 / 26 / 14 / 50 | 66 / 23 / 14 / 41 | 5.6 |
| artillery | Artillery | 6 | 72 / 26 / 14 / 50 | 73 / 27 / 14 / 52 | 4.5 |
| mlrs | Artillery | 6 | 90 / 37 / 14 / 77 | 79 / 31 / 14 / 61 | 5.1 |
| thermobaric_launcher | Artillery | 7 | 102 / 44 / 14 / 96 | 92 / 39 / 14 / 81 | 5.5 |
| shahed_truck | Artillery | 8 | 95 / 40 / 14 / 85 | 83 / 33 / 14 / 67 | 4.1 |
| ballistic_launcher | Artillery | 11 | 101 / 44 / 14 / 94 | 87 / 35 / 14 / 72 | 3.2 |
| heavy_rocket_artillery | Artillery | 11 | 131 / 62 / 14 / 139 | 110 / 49 / 14 / 107 | 4.5 |
| zu23_technical | AntiAir | 3 | 52 / 13 / 196 / 13 | 52 / 13 / 196 / 13 | 4.4 |
| aa_vehicle | AntiAir | 4 | 35 / 9 / 184 / 9 | 35 / 9 / 184 / 9 | 2.2 |
| sam_launcher | AntiAir | 5 | 48 / 12 / 168 / 14 | 48 / 12 / 169 / 14 | 2.4 |
| heavy_aa | AntiAir | 6 | 94 / 23 / 403 / 23 | 94 / 23 / 403 / 23 | 3.9 |
| iron_beam | AntiAir | 9 | 0 / 0 / 105 / 0 | 0 / 0 / 105 / 0 | 0.0 |
| long_sam | AntiAir | 11 | 0 / 0 / 112 / 0 | 0 / 0 / 112 / 0 | 0.0 |
| supply_truck | Support | 0 | 49 / 12 / 15 / 15 | 49 / 12 / 15 / 15 |  |
| engineer_vehicle | Support | 3 | 48 / 12 / 14 / 14 | 48 / 12 / 14 / 14 | 4.0 |
| smoke_carrier | Support | 3 | 48 / 12 / 14 / 14 | 48 / 12 / 14 / 14 | 4.0 |
| ammo_carrier | Support | 4 |  | 48 / 12 / 14 / 14 | 3.0 |
| counter_battery_radar | Support | 5 | 48 / 12 / 14 / 14 | 48 / 12 / 14 / 14 | 2.4 |
| ew_jammer | Support | 5 | 48 / 12 / 14 / 14 | 48 / 12 / 14 / 14 | 2.4 |
| mine_layer | Support | 5 | 48 / 12 / 14 / 14 | 48 / 12 / 14 / 14 | 2.4 |
| sapper | Support | 5 | 48 / 12 / 14 / 14 | 48 / 12 / 14 / 14 | 2.4 |
| command_vehicle | Support | 6 | 48 / 12 / 14 / 14 | 48 / 12 / 14 / 14 | 2.0 |
| scout_heli | Helicopter | 5 | 90 / 36 / 16 / 73 | 78 / 29 / 16 / 55 | 5.7 |
| attack_helicopter | Helicopter | 9 | 148 / 91 / 50 / 107 | 124 / 78 / 41 / 87 | 8.7 |
| heavy_attack_heli | Helicopter | 13 | 201 / 124 / 56 / 152 | 168 / 108 / 46 / 120 | 8.3 |
| gunship_heli | Helicopter | 15 | 305 / 245 / 35 / 221 | 278 / 219 / 35 / 189 | 14.6 |
| recon_drone | Plane | 6 | 11 / 15 / 0 / 9 | 10 / 13 / 0 / 8 | 2.1 |
| strike_drone | Plane | 7 | 80 / 85 / 0 / 105 | 50 / 54 / 0 / 66 | 7.7 |
| fighter_jet | Plane | 12 | 50 / 13 / 450 / 13 | 50 / 13 / 294 / 13 | 1.1 |
| attack_jet | Plane | 13 | 372 / 414 / 38 / 377 | 316 / 380 / 19 / 292 | 29.2 |
| tank_buster | Plane | 16 | 497 / 616 / 41 / 443 | 435 / 567 / 21 / 361 | 35.4 |
| stealth_bomber | Plane | 18 | 254 / 152 / 0 / 381 | 100 / 60 / 0 / 150 | 3.3 |
| heavy_bomber | Plane | 22 | 422 / 253 / 21 / 633 | 148 / 88 / 21 / 221 | 4.0 |
| sky_gunship | Plane | 22 | 389 / 203 / 0 / 383 | 381 / 211 / 0 / 391 | 9.6 |
| aa_turret | Defense | 0 | 94 / 23 / 403 / 23 | 94 / 23 / 403 / 23 |  |
| aa_turret.flak | Defense | 0 | 60 / 15 / 224 / 15 | 60 / 15 / 224 / 15 |  |
| aa_turret.sam | Defense | 0 | 48 / 12 / 168 / 14 | 48 / 12 / 169 / 14 |  |
| airfield | Defense | 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |  |
| airfield.hangar | Defense | 0 |  | 0 / 0 / 0 / 0 |  |
| airfield.service | Defense | 0 |  | 0 / 0 / 0 / 0 |  |
| ammo_depot | Defense | 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |  |
| artillery_emplacement | Defense | 0 | 66 / 25 / 13 / 49 | 67 / 26 / 13 / 50 |  |
| artillery_emplacement.cb | Defense | 0 | 66 / 25 / 13 / 49 | 67 / 26 / 13 / 50 |  |
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

| Vehicle | Class | CP | Ground (pre13x3) | Ground (after F (final)) | Change | Light | Tanks | Fort | Air | +AA (L/T/F) | Long | On target | Survival s | Real DPS tanks / fort |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| scout_jeep | Scout | 2 | 40 | 38 | -6 % | 91 | 14 | 25 | 10 | 50 / 32 / 14 |  | 31 % | 14 | 3 / 7 |
| vbied | Scout | 3 | 95 | 91 | -5 % | 107 | 84 | 140 | 0 | 96 / 60 / 57 |  | 3 % | 10 | 46 / 60 |
| armored_car | Light | 3 | 86 | 92 | +7 % | 198 | 50 | 71 | 10 | 141 / 65 / 28 |  | 56 % | 20 | 11 / 14 |
| ifv | Light | 5 | 111 | 123 | +11 % | 202 | 91 | 105 | 11 | 219 / 101 / 23 |  | 54 % | 31 | 24 / 26 |
| light_tank | Tank | 4 | 209 | 159 | -24 % | 317 | 96 | 103 | 15 | 338 / 64 / 37 |  | 52 % | 51 | 16 / 13 |
| turtle_tank | Tank | 7 | 262 | 360 | +38 % | 477 | 404 | 288 | 0 | 453 / 304 / 235 |  | 66 % | 78 | 38 / 22 |
| bmpt | Tank | 9 | 388 | 411 | +6 % | 764 | 288 | 351 | 8 | 810 / 252 / 0 |  | 63 % | 65 | 55 / 51 |
| flame_tank | Heavy | 5 | 407 | 356 | -13 % | 677 | 162 | 490 | 17 | 670 / 133 / 0 |  | 52 % | 54 | 26 / 55 |
| armored_bulldozer | Heavy | 7 | 446 | 422 | -5 % | 567 | 201 | 637 | 23 | 548 / 213 / 364 |  | 75 % | 69 | 24 / 53 |
| main_battle_tank | Heavy | 7 | 454 | 430 | -5 % | 626 | 305 | 284 | 24 | 703 / 380 / 284 |  | 73 % | 66 | 43 / 32 |
| twin_tank | Heavy | 9 | 468 | 451 | -4 % | 686 | 363 | 310 | 16 | 771 / 405 / 169 |  | 66 % | 68 | 56 / 47 |
| heavy_tank | Heavy | 10 | 459 | 475 | +3 % | 644 | 434 | 364 | 16 | 683 / 531 / 193 |  | 69 % | 78 | 60 / 46 |
| siege_tank | Heavy | 12 | 405 | 405 | +0 % | 215 | 180 | 820 | 20 | 227 / 183 / 806 | 474 | 81 % | 84 | 24 / 109 |
| titan_tank | Heavy | 14 | 490 | 494 | +1 % | 613 | 737 | 393 | 14 | 612 / 607 / 0 |  | 67 % | 81 | 115 / 61 |
| atgm_carrier | TankHunter | 5 | 165 | 307 | +86 % | 334 | 289 | 550 | 17 | 328 / 252 / 88 |  | 70 % | 46 | 51 / 32 |
| fpv_carrier | TankHunter | 6 | 428 | 428 | +0 % | 277 | 500 | 500 | 7 | 292 / 451 / 547 | 1107 | 87 % | 79 | 33 / 33 |
| lancet_truck | TankHunter | 6 | 204 | 238 | +17 % | 196 | 384 | 180 | 7 | 177 / 308 / 180 | 829 | 91 % | 79 | 26 / 12 |
| wheeled_gun | TankHunter | 6 | 146 | 234 | +61 % | 254 | 296 | 276 | 6 | 265 / 249 / 63 |  | 72 % | 35 | 55 / 39 |
| tank_destroyer | TankHunter | 7 | 554 | 492 | -11 % | 679 | 351 | 469 | 11 | 677 / 370 / 407 |  | 74 % | 66 | 49 / 36 |
| railgun_truck | TankHunter | 9 | 403 | 403 | +0 % | 324 | 570 | 348 | 0 | 325 / 516 / 335 |  | 83 % | 79 | 57 / 35 |
| rocket_technical | Artillery | 3 | 235 | 244 | +4 % | 105 | 68 | 812 | 3 | 54 / 20 / 407 | 40 | 44 % | 41 | 7 / 27 |
| mortar_carrier | Artillery | 4 | 345 | 335 | -3 % | 270 | 237 | 523 | 9 | 280 / 123 / 576 | 164 | 76 % | 76 | 11 / 23 |
| artillery | Artillery | 6 | 284 | 314 | +11 % | 269 | 209 | 445 | 0 | 277 / 235 / 447 | 636 | 84 % | 90 | 14 / 30 |
| mlrs | Artillery | 6 | 551 | 441 | -20 % | 267 | 299 | 704 | 0 | 347 / 299 / 731 | 830 | 82 % | 90 | 20 / 47 |
| thermobaric_launcher | Artillery | 7 | 243 | 267 | +10 % | 421 | 175 | 98 | 19 | 467 / 143 / 297 | 161 | 41 % | 75 | 19 / 8 |
| shahed_truck | Artillery | 8 | 374 | 374 | +0 % | 178 | 259 | 606 | 0 | 215 / 311 / 676 | 533 | 84 % | 90 | 23 / 54 |
| ballistic_launcher | Artillery | 11 | 412 | 382 | -7 % | 332 | 286 | 545 | 0 | 284 / 343 / 500 | 867 | 82 % | 90 | 35 / 67 |
| heavy_rocket_artillery | Artillery | 11 | 527 | 456 | -13 % | 315 | 351 | 673 | 0 | 348 / 364 / 683 | 1008 | 82 % | 90 | 43 / 82 |
| zu23_technical | AntiAir | 3 | 50 | 62 | +25 % | 114 | 39 | 34 | 85 | 115 / 57 / 16 |  | 56 % | 17 | 9 / 9 |
| aa_vehicle | AntiAir | 4 | 79 | 81 | +3 % | 133 | 44 | 82 | 233 | 141 / 79 / 9 |  | 59 % | 37 | 7 / 8 |
| sam_launcher | AntiAir | 5 | 9 | 7 | -22 % | 0 | 0 | 42 | 183 | 0 / 0 / 0 |  | 13 % | 66 | 0 / 9 |
| heavy_aa | AntiAir | 6 | 147 | 180 | +22 % | 253 | 98 | 319 | 193 | 258 / 100 / 52 |  | 64 % | 44 | 14 / 21 |
| iron_beam | AntiAir | 9 | 0 | 0 |  | 0 | 0 | 0 | 33 | 0 / 0 / 0 |  | 8 % | 69 | 0 / 0 |
| long_sam | AntiAir | 11 | 0 | 0 |  | 0 | 0 | 0 | 410 | 0 / 0 / 0 |  | 11 % | 88 | 0 / 0 |
| engineer_vehicle | Support | 3 | 0 | 0 |  | 0 | 0 | 0 | 0 | 0 / 0 / 0 |  | 0 % | 90 | 0 / 0 |
| smoke_carrier | Support | 3 | 104 | 102 | -2 % | 229 | 47 | 78 | 19 | 168 / 75 / 14 |  | 54 % | 30 | 7 / 10 |
| ammo_carrier | Support | 4 |  | 0 |  | 0 | 0 | 0 | 0 | 0 / 0 / 0 |  | 0 % | 90 | 0 / 0 |
| counter_battery_radar | Support | 5 | 0 | 0 |  | 0 | 0 | 0 | 0 | 0 / 0 / 0 |  | 0 % | 90 | 0 / 0 |
| ew_jammer | Support | 5 | 0 | 0 |  | 0 | 0 | 0 | 0 | 0 / 0 / 0 |  | 0 % | 90 | 0 / 0 |
| mine_layer | Support | 5 | 62 | 72 | +17 % | 102 | 83 | 35 | 8 | 104 / 103 / 6 |  | 45 % | 28 | 16 / 10 |
| sapper | Support | 5 | 280 | 266 | -5 % | 581 | 74 | 162 | 31 | 608 / 108 / 61 |  | 65 % | 66 | 9 / 12 |
| command_vehicle | Support | 6 | 0 | 0 |  | 0 | 0 | 0 | 0 | 0 / 0 / 0 |  | 0 % | 90 | 0 / 0 |
| scout_heli | Helicopter | 5 | 249 | 318 | +27 % | 677 | 373 | 639 | 48 | 50 / 126 / 41 | 24 | 60 % | 44 | 30 / 58 |
| attack_helicopter | Helicopter | 9 | 383 | 392 | +2 % | 717 | 683 | 645 | 104 | 67 / 206 / 35 | 48 | 63 % | 49 | 83 / 90 |
| heavy_attack_heli | Helicopter | 13 | 229 | 264 | +15 % | 239 | 353 | 215 | 54 | 240 / 324 / 215 | 548 | 89 % | 84 | 51 / 31 |
| gunship_heli | Helicopter | 15 | 469 | 384 | -18 % | 659 | 738 | 699 | 27 | 62 / 108 / 36 | 131 | 62 % | 58 | 123 / 117 |
| recon_drone | Plane | 6 | 76 | 58 | -24 % | 86 | 143 | 82 | 0 | 12 / 14 / 8 | 12 | 54 % | 39 | 12 / 7 |
| strike_drone | Plane | 7 | 329 | 343 | +4 % | 452 | 730 | 790 | 0 | 29 / 42 / 14 | 23 | 55 % | 46 | 58 / 66 |
| fighter_jet | Plane | 12 | 1 | 0 | -48 % | 0 | 1 | 0 | 284 | 0 / 1 / 1 | 0 | 10 % | 49 | 0 / 0 |
| attack_jet | Plane | 13 | 442 | 438 | -1 % | 628 | 729 | 1156 | 21 | 47 / 24 / 47 | 7 | 50 % | 43 | 120 / 173 |
| tank_buster | Plane | 16 | 559 | 383 | -32 % | 676 | 844 | 631 | 49 | 56 / 59 / 30 | 24 | 55 % | 50 | 150 / 112 |
| stealth_bomber | Plane | 18 | 535 | 390 | -27 % | 336 | 448 | 855 | 0 | 248 / 163 / 288 | 219 | 20 % | 72 | 90 / 171 |
| heavy_bomber | Plane | 22 | 598 | 438 | -27 % | 398 | 469 | 1070 | 30 | 235 / 205 / 248 | 198 | 32 % | 71 | 115 / 262 |


## 4. Prompt 15: armour levels, penetration, six damage types

The same measure, one seed (13), after prompt 15's rules (DECISIONS 14A.R). Value per CP on the ground, "(air)" in the air group. "Prompt 13" is the F3 file, "first" the new rules on prompt 13's roster, "shipped" after the rebalance. Raw files: `Docs/balance/combat_value_p15*.tsv`.

| Vehicle | Class | CP (was) | Prompt 13 | Prompt 15 first | Prompt 15 shipped | Change |
|---|---|---|---|---|---|---|
| scout_jeep | Scout | 2 | 38 | 28 | 28 | -26 % |
| vbied | Scout | 2 (3) | 91 | 48 | 87 | -4 % |
| armored_car | Light | 3 | 92 | 105 | 105 | +14 % |
| ifv | Light | 6 (5) | 123 | 188 | 118 | -4 % |
| light_tank | Tank | 3 (4) | 159 | 62 | 150 | -6 % |
| turtle_tank | Tank | 7 | 360 | 414 | 414 | +15 % |
| bmpt | Tank | 9 | 411 | 371 | 371 | -10 % |
| flame_tank | Heavy | 4 (5) | 356 | 190 | 289 | -19 % |
| armored_bulldozer | Heavy | 7 | 422 | 395 | 395 | -6 % |
| main_battle_tank | Heavy | 7 | 430 | 362 | 362 | -16 % |
| twin_tank | Heavy | 9 | 451 | 381 | 381 | -15 % |
| heavy_tank | Heavy | 10 | 475 | 497 | 497 | +5 % |
| siege_tank | Heavy | 12 | 405 | 413 | 413 | +2 % |
| titan_tank | Heavy | 14 | 494 | 525 | 525 | +6 % |
| atgm_carrier | TankHunter | 5 | 307 | 305 | 305 | -1 % |
| fpv_carrier | TankHunter | 6 | 428 | 428 | 428 | +0 % |
| lancet_truck | TankHunter | 6 | 238 | 278 | 278 | +17 % |
| wheeled_gun | TankHunter | 6 | 234 | 297 | 297 | +27 % |
| tank_destroyer | TankHunter | 7 | 492 | 426 | 426 | -14 % |
| railgun_truck | TankHunter | 9 | 403 | 461 | 461 | +14 % |
| rocket_technical | Artillery | 3 | 244 | 192 | 209 | -15 % |
| mortar_carrier | Artillery | 4 | 335 | 300 | 300 | -10 % |
| artillery | Artillery | 6 | 314 | 280 | 280 | -11 % |
| mlrs | Artillery | 6 | 441 | 446 | 446 | +1 % |
| thermobaric_launcher | Artillery | 7 | 267 | 265 | 265 | -1 % |
| shahed_truck | Artillery | 8 | 374 | 383 | 383 | +2 % |
| ballistic_launcher | Artillery | 11 | 382 | 402 | 402 | +5 % |
| heavy_rocket_artillery | Artillery | 11 | 456 | 432 | 432 | -5 % |
| zu23_technical (air) | AntiAir | 3 | 85 | 89 | 101 | +18 % |
| aa_vehicle (air) | AntiAir | 4 | 233 | 189 | 252 | +8 % |
| sam_launcher (air) | AntiAir | 5 | 183 | 150 | 155 | -15 % |
| heavy_aa (air) | AntiAir | 6 | 193 | 187 | 217 | +12 % |
| iron_beam (air) | AntiAir | 9 | 33 | 26 | 34 | +5 % |
| long_sam (air) | AntiAir | 11 | 410 | 545 | 545 | +33 % |
| smoke_carrier | Support | 3 | 102 | 96 | 96 | -6 % |
| mine_layer | Support | 5 | 72 | 63 | 63 | -13 % |
| sapper | Support | 5 | 266 | 132 | 132 | -50 % |
| scout_heli | Helicopter | 4 (5) | 318 | 197 | 243 | -23 % |
| attack_helicopter | Helicopter | 9 | 392 | 415 | 415 | +6 % |
| heavy_attack_heli | Helicopter | 13 | 264 | 278 | 272 | +3 % |
| gunship_heli | Helicopter | 15 | 384 | 355 | 302 | -21 % |
| recon_drone | Plane | 6 | 58 | 48 | 48 | -17 % |
| strike_drone | Plane | 7 | 343 | 325 | 325 | -5 % |
| fighter_jet (air) | Plane | 12 | 284 | 300 | 354 | +25 % |
| attack_jet | Plane | 13 | 438 | 480 | 439 | +0 % |
| tank_buster | Plane | 16 | 383 | 401 | 401 | +5 % |
| stealth_bomber | Plane | 18 | 390 | 402 | 402 | +3 % |
| heavy_bomber | Plane | 22 | 438 | 412 | 412 | -6 % |
