# Balance spreadsheet: apply report (prompt 25)

What `Tools/balance/import_xlsx.py` applied from `Docs/balance/Machine_Brigade_Can_bang.xlsx`, sheet by sheet, and
what it left and why. Outcomes: **applied** (the data now holds the sheet's number), **already** (the data already
held it), **deferred** (the row belongs to a later task of the sheet "Việc cho agent": names D1, model sizes B1,
models B2, bosses C1, boss weapons C2), **skipped** (no id in the data, a contradiction, or a measurement that did not
confirm it). Decisions and their reasons: `Docs/DECISIONS.md`, section 25A. Each step's section is rewritten when the
script runs it again.

<!-- summary -->
## Summary

Rows by step and sheet (each step's section below lists them).

| Step | Sheet | Applied | Already so | Deferred | Skipped |
|---|---|---|---|---|---|
| A1-Cao | Thay đổi chi tiết | 28 | 0 | 5 | 0 |
| A1-Cao | Vũ khí đề xuất | 14 | 1 | 0 | 0 |
| A1-Cao | Đơn vị – vũ khí | 2 | 0 | 0 | 0 |
| A1-Trung | Thay đổi chi tiết | 58 | 2 | 27 | 0 |
| A1-Trung | Vũ khí đề xuất | 23 | 2 | 0 | 0 |
| A1-Trung | Đơn vị – vũ khí | 1 | 0 | 0 | 0 |
| A1-Thap | Thay đổi chi tiết | 32 | 2 | 58 | 0 |
| A1-Thap | Vũ khí đề xuất | 9 | 0 | 0 | 0 |
| A2 | Vũ khí đề xuất | 62 | 92 | 0 | 35 |
| A2 | Đơn vị – vũ khí | 7 | 281 | 0 | 0 |
| A3 | Tốc độ tên lửa, Vũ khí đề xuất | 25 | 10 | 0 | 0 |
| A4 | Tốc độ tên lửa | 0 | 58 | 0 | 0 |
| A5 | Tổng quan, Vũ khí đề xuất | 5 | 68 | 2 | 0 |
| B7 | Giá CP | 0 | 58 | 0 | 0 |
| B8 | Thẻ hỗ trợ | 3 | 6 | 0 | 0 |
| review | Cân bằng lần 2 | 0 | 0 | 4 | 0 |
| review | Kiểm tra từng mục | 0 | 0 | 14 | 0 |
| review | Vũ khí đề xuất / Thay đổi chi tiết | 0 | 0 | 6 | 0 |

<!-- /summary -->

<!-- step:A1-Cao -->
## A1 Cao: sheet Thay đổi chi tiết

| Sheet | Applied | Already so | Deferred | Skipped |
|---|---|---|---|---|
| Thay đổi chi tiết | 28 | 0 | 5 | 0 |
| Vũ khí đề xuất | 14 | 1 | 0 | 0 |
| Đơn vị – vũ khí | 2 | 0 | 0 | 0 |

| Sheet | id | Item | Outcome | Detail |
|---|---|---|---|---|
| Vũ khí đề xuất | tower_flak_30 | weapon | applied | damage 7, cooldown 0.0286, clip 120, clipReload 3.0286 (for aa_turret: Vũ khí và tham khảo) |
| Thay đổi chi tiết | aa_turret | Vũ khí và tham khảo | applied | reference (unit_refs.json); tower_flak_30: damage 7, cooldown 0.0286, clip 120, clipReload 3.0286; choice: the reference moves to the 2A38 (the weapon is kept); the anti-aircraft value falls through the tower flak's new rate (tower_flak_30's row) |
| Vũ khí đề xuất | howitzer | weapon | applied | cooldown 7.1429 (for artillery: Vũ khí: lựu pháo 155 mm) |
| Thay đổi chi tiết | artillery | Vũ khí: lựu pháo 155 mm | applied | howitzer: cooldown 7.1429 |
| Thay đổi chi tiết | artillery | Model và tham khảo | applied | speed 6; front armour 2; the model and its reference wait for the model (task B2) |
| Thay đổi chi tiết | attack_helicopter | Giá | applied | cp 9 |
| Vũ khí đề xuất | jet_bombs | weapon | already | as the sheet (for attack_jet: Vũ khí: FAB-250) |
| Thay đổi chi tiết | attack_jet | Vũ khí: FAB-250 | applied | jet_bombs 1 a load |
| Vũ khí đề xuất | kh29 | weapon | applied | projectileSpeed 32 (for attack_jet: Vũ khí: Kh-29L, R-60) |
| Vũ khí đề xuất | r60 | weapon | applied | projectileSpeed 42 (for attack_jet: Vũ khí: Kh-29L, R-60) |
| Thay đổi chi tiết | attack_jet | Vũ khí: Kh-29L, R-60 | applied | kh29: projectileSpeed 32; r60: projectileSpeed 42 |
| Thay đổi chi tiết | attack_jet | Giá | applied | cp 18 |
| Thay đổi chi tiết | caspian | Vũ khí | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | daedalus | Máu, vũ khí | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Vũ khí đề xuất | air_to_air | weapon | applied | projectileSpeed 60 (for fighter_jet: Vũ khí: AIM-120, AIM-9X) |
| Vũ khí đề xuất | wvr_aam | weapon | applied | projectileSpeed 55 (for fighter_jet: Vũ khí: AIM-120, AIM-9X) |
| Thay đổi chi tiết | fighter_jet | Vũ khí: AIM-120, AIM-9X | applied | air_to_air: projectileSpeed 60; wvr_aam: projectileSpeed 55 |
| Thay đổi chi tiết | heavy_tank | Giá (CP) | applied | cp 13 |
| Thay đổi chi tiết | iron_beam | Giá | applied | cp 6 |
| Vũ khí đề xuất | hel_beam | weapon | applied | damage 10 (for iron_beam: Vũ khí: laser 100 kW) |
| Thay đổi chi tiết | iron_beam | Vũ khí: laser 100 kW | applied | hel_beam: damage 10; aps shells 0.3 (the C-RAM's share of mortar bombs and shells) |
| Thay đổi chi tiết | long_sam | Giá | applied | cp 14 |
| Vũ khí đề xuất | patriot | weapon | applied | projectileSpeed 60, cooldown 2.75 (for missile_battery: Vũ khí: Patriot PAC-2) |
| Thay đổi chi tiết | missile_battery | Vũ khí: Patriot PAC-2 | applied | patriot: projectileSpeed 60, cooldown 2.75 |
| Vũ khí đề xuất | turret_gmlrs | weapon | applied | damage 160, projectileSpeed 50, splash 4.5, cooldown 7.5 (for rocket_turret.guided: Vũ khí: GMLRS dẫn đường) |
| Thay đổi chi tiết | rocket_turret.guided | Vũ khí: GMLRS dẫn đường | applied | turret_gmlrs: damage 160, projectileSpeed 50, splash 4.5, cooldown 7.5 |
| Thay đổi chi tiết | sam_launcher | Giá | applied | cp 7 |
| Vũ khí đề xuất | buk_launcher | weapon | applied | projectileSpeed 50, cooldown 2.8 (for sam_launcher: Vũ khí: 9M317 Buk) |
| Thay đổi chi tiết | sam_launcher | Vũ khí: 9M317 Buk | applied | buk_launcher: projectileSpeed 50, cooldown 2.8 |
| Thay đổi chi tiết | scout_heli | Giá | applied | cp 5 |
| Vũ khí đề xuất | scout_rockets | weapon | applied | projectileSpeed 40 (for scout_heli: Vũ khí: Hydra 70) |
| Thay đổi chi tiết | scout_heli | Vũ khí: Hydra 70 | applied | scout_rockets: projectileSpeed 40; scout_rockets 6 a load |
| Thay đổi chi tiết | scout_jeep | Tầm nhìn | applied | vision 55 |
| Thay đổi chi tiết | scout_jeep | Hành vi | applied | stillCamo 0.4 (seen at 60 % of a spotter's sight when still) |
| Thay đổi chi tiết | scylla | Vũ khí, máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | silver_bug | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | silver_bug | Vũ khí | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | stealth_fighter | Giá (CP) | applied | cp 13 |
| Thay đổi chi tiết | strike_drone | Giá | applied | cp 9 |
| Vũ khí đề xuất | jassm | weapon | applied | projectileSpeed 20, splash 9, cooldown 9.84 (for swarm_carrier: Vũ khí: thêm Rapid Dragon) |
| Đơn vị – vũ khí | swarm_carrier | guided_bomb | applied | dropped (kept 0) |
| Đơn vị – vũ khí | swarm_carrier | jassm | applied | added on slot drone |
| Thay đổi chi tiết | swarm_carrier | Vũ khí: thêm Rapid Dragon | applied | jassm: projectileSpeed 20, splash 9, cooldown 9.84; guided_bomb dropped; jassm added; jassm 2 a sortie |
| Thay đổi chi tiết | swarm_carrier | Giá | applied | cp 13 |
| Thay đổi chi tiết | titan_tank | Giá (CP) | applied | cp 18 |
| Thay đổi chi tiết | wheeled_gun | Máu | applied | hp 682 (the sheet's 1500 over toughness 2.2) |
| Vũ khí đề xuất | gun_105_wheeled | weapon | applied | cooldown 3.7037 (for wheeled_gun: Vũ khí: 120 mm) |
| Thay đổi chi tiết | wheeled_gun | Vũ khí: 120 mm | applied | gun_105_wheeled: cooldown 3.7037 |
| Vũ khí đề xuất | zu23 | weapon | applied | damage 7, range 38, cooldown 0.04, clip 50, clipReload 3.04 (for zu23_technical: Vũ khí: ZU-23-2) |
| Thay đổi chi tiết | zu23_technical | Vũ khí: ZU-23-2 | applied | zu23: damage 7, range 38, cooldown 0.04, clip 50, clipReload 3.04 |

<!-- /step:A1-Cao -->

<!-- step:A1-Trung -->
## A1 Trung: sheet Thay đổi chi tiết

| Sheet | Applied | Already so | Deferred | Skipped |
|---|---|---|---|---|
| Thay đổi chi tiết | 58 | 2 | 27 | 0 |
| Vũ khí đề xuất | 23 | 2 | 0 | 0 |
| Đơn vị – vũ khí | 1 | 0 | 0 | 0 |

| Sheet | id | Item | Outcome | Detail |
|---|---|---|---|---|
| Thay đổi chi tiết | aa_turret.sam | Tham khảo | applied | reference (unit_refs.json) |
| Vũ khí đề xuất | sam | weapon | applied | projectileSpeed 42 (for aa_vehicle: Vũ khí: Stinger) |
| Thay đổi chi tiết | aa_vehicle | Vũ khí: Stinger | applied | sam: projectileSpeed 42 |
| Thay đổi chi tiết | aa_vehicle | Giáp (T/H/S/N) | applied | armour [2, 1, 1, 0] |
| Thay đổi chi tiết | argus | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | armored_bulldozer | Tốc độ | applied | speed 4 |
| Thay đổi chi tiết | armored_train | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | artillery | Giáp (T/H/S/N) | applied | armour [2, 1, 1, 0] |
| Vũ khí đề xuất | mortar_240_fixed | weapon | applied | cooldown 5 (for artillery_emplacement.mortar: Vũ khí: cối 240 mm) |
| Thay đổi chi tiết | artillery_emplacement.mortar | Vũ khí: cối 240 mm | applied | mortar_240_fixed: cooldown 5 |
| Vũ khí đề xuất | hellfire_standoff | weapon | applied | projectileSpeed 26, cooldown 7.55 (for attack_helicopter: Vũ khí: Hellfire, Stinger ATAS) |
| Vũ khí đề xuất | stinger_atas | weapon | applied | projectileSpeed 42 (for attack_helicopter: Vũ khí: Hellfire, Stinger ATAS) |
| Thay đổi chi tiết | attack_helicopter | Vũ khí: Hellfire, Stinger ATAS | applied | hellfire_standoff: projectileSpeed 26, cooldown 7.55; stinger_atas: projectileSpeed 42 |
| Vũ khí đề xuất | jet_cannon | weapon | applied | cooldown 0.0526, clip 70, clipReload 1.5526 (for attack_jet: Vũ khí: GSh-30-2) |
| Thay đổi chi tiết | attack_jet | Vũ khí: GSh-30-2 | applied | jet_cannon: cooldown 0.0526, clip 70, clipReload 1.5526 |
| Vũ khí đề xuất | ballistic_missile | weapon | applied | projectileSpeed 50, splash 10, cooldown 22.71 (for ballistic_launcher: Vũ khí: Iskander) |
| Thay đổi chi tiết | ballistic_launcher | Vũ khí: Iskander | applied | ballistic_missile: projectileSpeed 50, splash 10, cooldown 22.71 |
| Thay đổi chi tiết | bastion_mk0 | Máu, giáp | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | behemoth | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | behemoth_mk2 | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | behemoth_tempest | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Vũ khí đề xuất | twin_30_bmpt | weapon | applied | burst 12, burstInterval 0.0833, cooldown 1.5833, clip removed (for bmpt: Vũ khí: 2A42 đôi) |
| Thay đổi chi tiết | bmpt | Vũ khí: 2A42 đôi | applied | twin_30_bmpt: burst 12, burstInterval 0.0833, cooldown 1.5833, clip removed |
| Vũ khí đề xuất | agl_40 | weapon | applied | burst 6, cooldown 3.2 (for bmpt: Vũ khí: Mk 19 40 mm) |
| Thay đổi chi tiết | bmpt | Vũ khí: Mk 19 40 mm | applied | agl_40: burst 6, cooldown 3.2 |
| Vũ khí đề xuất | c_ram_gatling | weapon | applied | damage 2, cooldown 0.02, clip 200, clipReload 3.02 (for c_ram: Vũ khí: Phalanx 20 mm) |
| Thay đổi chi tiết | c_ram | Vũ khí: Phalanx 20 mm | applied | c_ram_gatling: damage 2, cooldown 0.02, clip 200, clipReload 3.02 |
| Thay đổi chi tiết | caspian | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | command_airship | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | command_vehicle | Giáp (T/H/S/N) | applied | armour [1, 1, 0, 0] |
| Thay đổi chi tiết | daedalus | Kích thước | deferred | model size: task B1 |
| Thay đổi chi tiết | engineer_vehicle | Giáp (T/H/S/N) | applied | armour [2, 1, 1, 0] |
| Thay đổi chi tiết | flame_tank | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | fortress_bastion | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | fortress_hive | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Vũ khí đề xuất | turret_gun_120_long | weapon | applied | pen 5 (for gun_turret.long: Vũ khí: 120 mm L/55) |
| Thay đổi chi tiết | gun_turret.long | Vũ khí: 120 mm L/55 | applied | turret_gun_120_long: pen 5; choice: penetration +1 (the weapon row's 'xuyên đề xuất' 5), not a first-shot bonus |
| Thay đổi chi tiết | gunship_heli | Giáp, máu | applied | hp 1182 (the sheet's 2600 over toughness 2.2); armour [2, 1, 0, 0] |
| Vũ khí đề xuất | heli_atgm | weapon | applied | range 45, projectileSpeed 26 (for gunship_heli: Vũ khí: tên lửa chống tăng) |
| Đơn vị – vũ khí | gunship_heli | heli_atgm | applied | Hellfire -> 9M120 Ataka |
| Thay đổi chi tiết | gunship_heli | Vũ khí: tên lửa chống tăng | applied | heli_atgm: range 45, projectileSpeed 26; heli_ataka (9M120 Ataka at the Hellfire mount's rate and load); heli_atgm -> heli_ataka |
| Thay đổi chi tiết | gunship_heli | Tốc độ | applied | speed 14 |
| Thay đổi chi tiết | heavy_aa | Giá | applied | cp 7 |
| Vũ khí đề xuất | air_cruise_missile | weapon | applied | projectileSpeed 22, splash 9 (for heavy_bomber: Vũ khí: Kh-101) |
| Thay đổi chi tiết | heavy_bomber | Vũ khí: Kh-101 | applied | air_cruise_missile: projectileSpeed 22, splash 9 |
| Vũ khí đề xuất | bomber_payload | weapon | applied | burst 7, cooldown 11.2 (for heavy_bomber: Vũ khí: FAB-500) |
| Thay đổi chi tiết | heavy_bomber | Vũ khí: FAB-500 | applied | bomber_payload: burst 7, cooldown 11.2; bomber_payload 7 a sortie |
| Thay đổi chi tiết | heavy_tank | Tham khảo, giá | applied | reference (unit_refs.json) |
| Thay đổi chi tiết | heavy_tank | Tốc độ xoay thân / tháp | applied | turretTurnRate 115 (2 rad/s) |
| Vũ khí đề xuất | gun_155_twin_fort | weapon | applied | splash 7 (for heavy_turret: Vũ khí: 155 mm đôi) |
| Thay đổi chi tiết | heavy_turret | Vũ khí: 155 mm đôi | applied | gun_155_twin_fort: splash 7; gun_155_twin_ap (AP, pen 4, 300 a round); heavy_turret fires gun_155_twin_ap, its HE round gun_155_twin_fort for structures and light armour |
| Thay đổi chi tiết | icarus_mk0 | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Vũ khí đề xuất | ifv_30 | weapon | applied | burst 10, burstInterval 0.1111, cooldown 1.6111, clip removed (for ifv: Vũ khí: 2A42 30 mm) |
| Thay đổi chi tiết | ifv | Vũ khí: 2A42 30 mm | applied | ifv_30: burst 10, burstInterval 0.1111, cooldown 1.6111, clip removed |
| Vũ khí đề xuất | atgm | weapon | applied | range 40, projectileSpeed 20 (for ifv: Vũ khí: TOW-2) |
| Thay đổi chi tiết | ifv | Vũ khí: TOW-2 | applied | atgm: range 40, projectileSpeed 20 |
| Thay đổi chi tiết | ifv | Tốc độ | applied | speed 8 |
| Thay đổi chi tiết | ixion | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | kronos | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | landing_hovercraft | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | laser_tank | Giá, tăng dần | applied | cp 9; focus_laser ramp to x2 in 4 s |
| Thay đổi chi tiết | laser_tank | Giáp (T/H/S/N) | applied | armour [2, 1, 1, 1] |
| Vũ khí đề xuất | leviathan_460 | weapon | applied | splash 13 (for leviathan: Vũ khí: 460 mm) |
| Thay đổi chi tiết | leviathan | Vũ khí: 460 mm | applied | leviathan_460: splash 13 |
| Thay đổi chi tiết | locust | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Vũ khí đề xuất | sam_48n6 | weapon | applied | projectileSpeed 65 (for long_sam: Vũ khí: 48N6) |
| Thay đổi chi tiết | long_sam | Vũ khí: 48N6 | applied | sam_48n6: projectileSpeed 65 |
| Thay đổi chi tiết | main_battle_tank | Giáp (T/H/S/N) | applied | armour [4, 2, 1, 1] |
| Thay đổi chi tiết | main_battle_tank | Tốc độ | applied | speed 6.5 |
| Thay đổi chi tiết | main_battle_tank | Tốc độ xoay thân / tháp | applied | turretTurnRate 115 (2 rad/s) |
| Thay đổi chi tiết | mine_layer | Giáp (T/H/S/N) | applied | armour [1, 1, 0, 0] |
| Vũ khí đề xuất | sam_battery_lrr | weapon | applied | cooldown 3.45 (for missile_battery.lrr: Vũ khí) |
| Thay đổi chi tiết | missile_battery.lrr | Vũ khí | applied | sam_battery_lrr: cooldown 3.45 |
| Vũ khí đề xuất | sam_pac3 | weapon | applied | projectileSpeed 65, cooldown 6.25 (for missile_battery.pac3: Vũ khí: PAC-3) |
| Thay đổi chi tiết | missile_battery.pac3 | Vũ khí: PAC-3 | applied | sam_pac3: projectileSpeed 65, cooldown 6.25 |
| Thay đổi chi tiết | mlrs | Hành vi | applied | scoot after every salvo, 15-20 m |
| Thay đổi chi tiết | mlrs | Giá | applied | cp 7 |
| Thay đổi chi tiết | mortar_carrier | Giáp (T/H/S/N) | applied | armour [1, 1, 0, 0] |
| Thay đổi chi tiết | nuke_train | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | rail_supergun | Dữ liệu vũ khí | deferred | a boss's main weapon as data: task C2 |
| Thay đổi chi tiết | rail_supergun | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | recon_drone | Tốc độ | applied | speed 13 |
| Thay đổi chi tiết | sam_launcher | Máu | applied | hp 591 (the sheet's 1300 over toughness 2.2) |
| Thay đổi chi tiết | sam_launcher | Giáp (T/H/S/N) | applied | armour [1, 1, 0, 0] |
| Thay đổi chi tiết | scout_jeep | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | siege_tank | Giáp (T/H/S/N) | applied | armour [2, 1, 1, 0] |
| Thay đổi chi tiết | silver_bug | Kích thước | deferred | model size: task B1 |
| Thay đổi chi tiết | sky_fortress | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | smoke_carrier | Vũ khí: M2 12,7 mm | already | it carries hmg_selfdef_15 (15 m, the engineer's) already; the sheet's 22 m is out of date |
| Thay đổi chi tiết | smoke_carrier | Giáp (T/H/S/N) | applied | armour [1, 1, 0, 0] |
| Thay đổi chi tiết | stealth_bomber | Giá | applied | cp 21 |
| Vũ khí đề xuất | jassm | weapon | already | as the sheet (for stealth_bomber: Vũ khí: JASSM) |
| Thay đổi chi tiết | stealth_bomber | Vũ khí: JASSM | already | the data already holds it |
| Vũ khí đề xuất | air_to_air | weapon | already | as the sheet (for stealth_fighter: Vũ khí và giá) |
| Thay đổi chi tiết | stealth_fighter | Vũ khí và giá | applied | air_to_air 5 a load |
| Thay đổi chi tiết | stealth_fighter | Tốc độ | applied | speed 44 |
| Thay đổi chi tiết | supply_truck | Tốc độ | applied | speed 6 |
| Thay đổi chi tiết | supreme_command | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | swarm_carrier | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | tank_destroyer | Giáp | applied | armour [2, 1, 1, 0] |
| Vũ khí đề xuất | gun_105_long | weapon | applied | range 46, cooldown 3.3333 (for tank_destroyer: Tầm, nhịp, giá) |
| Thay đổi chi tiết | tank_destroyer | Tầm, nhịp, giá | applied | cp 6; gun_105_long: range 46, cooldown 3.3333 |
| Thay đổi chi tiết | titan_tank | Tốc độ, giá | applied | speed 4 |
| Thay đổi chi tiết | titan_tank | Tốc độ xoay thân / tháp | applied | turretTurnRate 115 (2 rad/s) |
| Thay đổi chi tiết | turtle_tank | Giáp (T/H/S/N) | applied | armour [3, 2, 2, 3] |
| Thay đổi chi tiết | twin_tank | Tốc độ xoay thân / tháp | applied | turretTurnRate 115 (2 rad/s) |
| Thay đổi chi tiết | typhon | Vũ khí | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | typhon | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | vbied | Giáp | applied | armour [2, 1, 0, 0] |
| Vũ khí đề xuất | detonator | weapon | applied | splash 10 (for vbied: Máu, nổ lan) |
| Thay đổi chi tiết | vbied | Máu, nổ lan | applied | hp 364 (the sheet's 800 over toughness 2.2); detonator: splash 10 |
| Vũ khí đề xuất | aim9 | weapon | applied | projectileSpeed 55 (for wingman_drone: Vũ khí: AIM-9) |
| Thay đổi chi tiết | wingman_drone | Vũ khí: AIM-9 | applied | aim9: projectileSpeed 55 |

<!-- /step:A1-Trung -->

<!-- step:A1-Thap -->
## A1 Thấp: sheet Thay đổi chi tiết

| Sheet | Applied | Already so | Deferred | Skipped |
|---|---|---|---|---|
| Thay đổi chi tiết | 32 | 2 | 58 | 0 |
| Vũ khí đề xuất | 9 | 0 | 0 | 0 |

| Sheet | id | Item | Outcome | Detail |
|---|---|---|---|---|
| Thay đổi chi tiết | aa_vehicle | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | ammo_depot | Nổ khi bị phá | applied | deathExplosion.radius 14 |
| Thay đổi chi tiết | armored_car | Tầm nhìn | applied | vision 42 |
| Thay đổi chi tiết | armored_car | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | armored_car | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | armored_train | Giáp | applied | armour [4, 3, 3, 2] |
| Thay đổi chi tiết | armored_train | Giáp | already | the data already holds it |
| Thay đổi chi tiết | artillery | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | artillery | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | artillery | Nổ khi bị phá (bán kính) | applied | deathExplosion.radius 10 |
| Thay đổi chi tiết | attack_helicopter | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | ballistic_launcher | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | bastion_mk0 | Giáp | applied | armour [4, 4, 4, 3] |
| Thay đổi chi tiết | behemoth_inferno | Giáp | applied | armour [4, 3, 2, 2] |
| Thay đổi chi tiết | behemoth_mk2 | Giáp | applied | armour [4, 3, 2, 2] |
| Thay đổi chi tiết | behemoth_tempest | Giáp | applied | armour [4, 3, 2, 2] |
| Vũ khí đề xuất | ataka | weapon | applied | projectileSpeed 26, cooldown 10.92 (for bmpt: Vũ khí: 9M120 Ataka) |
| Thay đổi chi tiết | bmpt | Vũ khí: 9M120 Ataka | applied | ataka: projectileSpeed 26, cooldown 10.92 |
| Thay đổi chi tiết | bmpt | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | bulwark_post | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | bunker_vehicle | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | c_ram | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | command_vehicle | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | counter_battery_radar | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | counter_battery_radar | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | drone_hangar | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | earth_borer | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | ew_jammer | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | fenrir | Giáp | applied | armour [4, 4, 3, 2] |
| Thay đổi chi tiết | fenrir | Giáp | already | the data already holds it |
| Thay đổi chi tiết | fighter_jet | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Vũ khí đề xuất | flamethrower | weapon | applied | damage 21 (for flame_tank: Vũ khí: súng phun lửa) |
| Thay đổi chi tiết | flame_tank | Vũ khí: súng phun lửa | applied | flamethrower: damage 21 |
| Thay đổi chi tiết | flame_tank | Nổ khi bị phá (bán kính) | applied | deathExplosion.radius 5 |
| Thay đổi chi tiết | fpv_carrier | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | gunship_heli | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Vũ khí đề xuất | twin_30_flak | weapon | applied | damage 7.5, cooldown 0.025, clip 160, clipReload 3.025 (for heavy_aa: Vũ khí: 2A38 30 mm đôi) |
| Thay đổi chi tiết | heavy_aa | Vũ khí: 2A38 30 mm đôi | applied | twin_30_flak: damage 7.5, cooldown 0.025, clip 160, clipReload 3.025 |
| Thay đổi chi tiết | heavy_aa | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | heavy_aa | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | heavy_bomber | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Vũ khí đề xuất | rockets_300mm | weapon | applied | projectileSpeed 55 (for heavy_rocket_artillery: Vũ khí: Smerch 300 mm) |
| Thay đổi chi tiết | heavy_rocket_artillery | Vũ khí: Smerch 300 mm | applied | rockets_300mm: projectileSpeed 55 |
| Thay đổi chi tiết | heavy_rocket_artillery | Giá | applied | cp 12 |
| Thay đổi chi tiết | heavy_turret | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Vũ khí đề xuất | hover_ciws | weapon | applied | damage 12, clip 60, clipReload 5.0167 (for hover_gunboat: Vũ khí: AK-630 30 mm) |
| Thay đổi chi tiết | hover_gunboat | Vũ khí: AK-630 30 mm | applied | hover_ciws: damage 12, clip 60, clipReload 5.0167 |
| Thay đổi chi tiết | hover_gunboat | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | hover_gunboat | Nổ khi bị phá (bán kính) | applied | deathExplosion.radius 9 |
| Thay đổi chi tiết | iron_beam | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | iron_beam | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | kronos | Dữ liệu vũ khí | deferred | a boss's main weapon as data: task C2 |
| Thay đổi chi tiết | lancet_truck | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | lancet_truck | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | lancet_truck | Nổ khi bị phá (bán kính) | applied | deathExplosion.radius 9 |
| Thay đổi chi tiết | laser_tank | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Vũ khí đề xuất | gun_57mm | weapon | applied | burst 2, burstInterval 0.5, cooldown 4 (for light_tank: Vũ khí: 57 mm) |
| Thay đổi chi tiết | light_tank | Vũ khí: 57 mm | applied | gun_57mm: burst 2, burstInterval 0.5, cooldown 4 |
| Thay đổi chi tiết | light_tank | Tầm nhìn | applied | vision 36 |
| Thay đổi chi tiết | light_tank | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | long_sam | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | missile_battery | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | mlrs | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | morrigan | Tham khảo | applied | reference (unit_refs.json) |
| Vũ khí đề xuất | mortar_120 | weapon | applied | cooldown 5 (for mortar_carrier: Vũ khí: cối 120 mm) |
| Thay đổi chi tiết | mortar_carrier | Vũ khí: cối 120 mm | applied | mortar_120: cooldown 5 |
| Thay đổi chi tiết | mortar_carrier | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | mortar_carrier | Nổ khi bị phá (bán kính) | applied | deathExplosion.radius 8 |
| Thay đổi chi tiết | railgun_truck | Giá | applied | cp 10 |
| Thay đổi chi tiết | railgun_truck | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Vũ khí đề xuất | turret_rockets | weapon | applied | damage 66, projectileSpeed 45, cooldown 3.47 (for rocket_turret: Vũ khí: Grad) |
| Thay đổi chi tiết | rocket_turret | Vũ khí: Grad | applied | turret_rockets: damage 66, projectileSpeed 45, cooldown 3.47; choice: +15 % damage (the weapon row's 66 a rocket), not the shorter reload |
| Thay đổi chi tiết | sam_launcher | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | scout_heli | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | scout_jeep | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | scylla | Giáp | applied | armour [4, 4, 3, 2] |
| Vũ khí đề xuất | shahed | weapon | applied | splash 4.5 (for shahed_truck: Vũ khí: Shahed-136) |
| Thay đổi chi tiết | shahed_truck | Vũ khí: Shahed-136 | applied | shahed: splash 4.5 |
| Thay đổi chi tiết | shahed_truck | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | shahed_truck | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | siege_tank | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | siege_tank | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | sky_gunship | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | smoke_carrier | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | spawn_bastion | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | stealth_bomber | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | stealth_fighter | Nổ khi bị phá (bán kính) | applied | deathExplosion.radius 5 |
| Thay đổi chi tiết | supply_truck | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | supply_truck | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | supreme_command | Giáp | applied | armour [4, 3, 2, 2] |
| Thay đổi chi tiết | tank_destroyer | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | thermobaric_launcher | Giá | applied | cp 9 |
| Thay đổi chi tiết | thermobaric_launcher | Nổ khi bị phá (bán kính) | applied | deathExplosion.radius 9 |
| Thay đổi chi tiết | titan_tank | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | titan_tank | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | titan_tank | Nổ khi bị phá (bán kính) | applied | deathExplosion.radius 8 |
| Thay đổi chi tiết | turtle_tank | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | twin_tank | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | vbied | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | wheeled_gun | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | zu23_technical | Tên | deferred | name: task D1 (sheet Tên đề xuất) |

<!-- /step:A1-Thap -->

<!-- step:A2 -->
## A2: sheets Vũ khí đề xuất and Đơn vị – vũ khí

Every row of "Vũ khí đề xuất" (the proposal columns: damage, fire mode, rate, rounds a burst or magazine, rest, reach, speed, blast, penetration), then the loadouts of "Đơn vị – vũ khí" (mounts kept 0 dropped, the new weapons). A cadence the game already fires within 3 % of the sheet's sustained DPS, in the same mode and rounds, stays as it is. Rows of "Đơn vị – vũ khí" that keep a mount without a note are counted, not listed.

| Sheet | Applied | Already so | Deferred | Skipped |
|---|---|---|---|---|
| Vũ khí đề xuất | 62 | 92 | 0 | 35 |
| Đơn vị – vũ khí | 7 | 281 | 0 | 0 |

| Sheet | id | Item | Outcome | Detail |
|---|---|---|---|---|
| Vũ khí đề xuất | aa_25_triple | weapon | already | as the sheet |
| Vũ khí đề xuất | agl_40 | weapon | already | as the sheet |
| Vũ khí đề xuất | aim9 | weapon | already | as the sheet |
| Vũ khí đề xuất | air_cruise_missile | weapon | already | as the sheet |
| Vũ khí đề xuất | air_to_air | weapon | already | as the sheet |
| Vũ khí đề xuất | airship_drones | weapon | applied | cooldown 8.35 |
| Vũ khí đề xuất | airship_flak | weapon | applied | clipReload 1.38 |
| Vũ khí đề xuất | ataka | weapon | already | as the sheet |
| Vũ khí đề xuất | atgm | weapon | already | as the sheet |
| Vũ khí đề xuất | autocannon_25 | weapon | applied | burst 8, burstInterval 0.1667, cooldown 1.4667, clip removed |
| Vũ khí đề xuất | autocannon_30 | weapon | applied | burst 10, burstInterval 0.1111, cooldown 1.6111, clip removed |
| Vũ khí đề xuất | autocannon_40 | weapon | applied | clipReload 1.72 |
| Vũ khí đề xuất | ballistic_missile | weapon | already | as the sheet |
| Vũ khí đề xuất | bastion_gun | weapon | already | as the sheet |
| Vũ khí đề xuất | boat_rockets | weapon | applied | projectileSpeed 40 |
| Vũ khí đề xuất | bomber_payload | weapon | already | as the sheet |
| Vũ khí đề xuất | bomber_tail_guns | weapon | already | as the sheet |
| Vũ khí đề xuất | borer_cannon | weapon | already | as the sheet |
| Vũ khí đề xuất | borer_drill | weapon | already | as the sheet |
| Vũ khí đề xuất | boss_flak | weapon | already | as the sheet |
| Vũ khí đề xuất | boss_flamer | weapon | already | as the sheet |
| Vũ khí đề xuất | boss_heli_gun | weapon | applied | cooldown 0.1667, clip 40, clipReload 3.1667 |
| Vũ khí đề xuất | boss_hmg | weapon | applied | cooldown 0.0833, clip 100, clipReload 5.0833 |
| Vũ khí đề xuất | boss_howitzer | weapon | applied | splash 8 |
| Vũ khí đề xuất | boss_minigun | weapon | already | as the sheet |
| Vũ khí đề xuất | boss_missiles | weapon | applied | projectileSpeed 22 |
| Vũ khí đề xuất | boss_mortar | weapon | already | as the sheet |
| Vũ khí đề xuất | boss_railgun | weapon | already | as the sheet |
| Vũ khí đề xuất | boss_rockets | weapon | applied | projectileSpeed 45, cooldown 2.94 |
| Vũ khí đề xuất | boss_thermo | weapon | applied | projectileSpeed 35 |
| Vũ khí đề xuất | buk_launcher | weapon | already | as the sheet |
| Vũ khí đề xuất | bunker_flame | weapon | already | as the sheet |
| Vũ khí đề xuất | bunker_hmg | weapon | applied | clip 150, clipReload 4.062 |
| Vũ khí đề xuất | bunker_hmg_twin | weapon | applied | clip 150, clipReload 4.05 |
| Vũ khí đề xuất | c_ram_gatling | weapon | already | as the sheet |
| Vũ khí đề xuất | casemate_155 | weapon | applied | splash 7 |
| Vũ khí đề xuất | ciws_aa | weapon | already | as the sheet |
| Vũ khí đề xuất | coilgun | weapon | applied | cooldown 4.54 |
| Vũ khí đề xuất | cruiser_203 | weapon | applied | splash 8, cooldown 11.4 |
| Vũ khí đề xuất | detonator | weapon | already | as the sheet |
| Vũ khí đề xuất | door_gun | weapon | applied | cooldown 0.0833, clip 100, clipReload 4.0833 |
| Vũ khí đề xuất | dozer_blade | weapon | applied | range 4 |
| Vũ khí đề xuất | drone_missile | weapon | applied | projectileSpeed 26 |
| Vũ khí đề xuất | fighter_cannon | weapon | already | as the sheet |
| Vũ khí đề xuất | flak_35 | weapon | applied | cooldown 0.25, clipReload 1.25 |
| Vũ khí đề xuất | flak_quad | weapon | already | as the sheet |
| Vũ khí đề xuất | flamethrower | weapon | already | as the sheet |
| Vũ khí đề xuất | focus_laser | weapon | already | as the sheet |
| Vũ khí đề xuất | fpv_hangar | weapon | applied | cooldown 7.5 |
| Vũ khí đề xuất | fpv_hangar_swarm | weapon | applied | cooldown 6.1 |
| Vũ khí đề xuất | fpv_swarm | weapon | already | as the sheet |
| Vũ khí đề xuất | grad_cluster | weapon | applied | projectileSpeed 45, splash 4, cooldown 8 |
| Vũ khí đề xuất | griffin | weapon | applied | projectileSpeed 22 |
| Vũ khí đề xuất | gsh30k | weapon | applied | cooldown 0.1429, clipReload 1.1429 |
| Vũ khí đề xuất | guided_bomb | weapon | applied | splash 4 |
| Vũ khí đề xuất | gun_105_apfsds | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_105_bunker | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_105_long | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_105_wheeled | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_120_twin | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_120mm | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_125_elite | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_140_twin | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_152 | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_152_he | weapon | applied | splash 6.5 |
| Vũ khí đề xuất | gun_152_heat | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_155_coastal | weapon | applied | splash 7 |
| Vũ khí đề xuất | gun_155_twin_coastlr | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_155_twin_fort | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_57_auto | weapon | applied | clipReload 2.9 |
| Vũ khí đề xuất | gun_57mm | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_behemoth | weapon | applied | splash 6.5 |
| Vũ khí đề xuất | gunship_105 | weapon | applied | splash 5.5 |
| Vũ khí đề xuất | gunship_25mm | weapon | already | as the sheet |
| Vũ khí đề xuất | gunship_40mm | weapon | already | as the sheet |
| Vũ khí đề xuất | gunship_rockets | weapon | applied | projectileSpeed 40 |
| Vũ khí đề xuất | hel_beam | weapon | already | as the sheet |
| Vũ khí đề xuất | heli_atgm | weapon | already | as the sheet |
| Vũ khí đề xuất | heli_gun | weapon | applied | cooldown 0.1667, clip 40, clipReload 3.1667 |
| Vũ khí đề xuất | heli_rockets | weapon | applied | projectileSpeed 40 |
| Vũ khí đề xuất | hellfire_standoff | weapon | already | as the sheet |
| Vũ khí đề xuất | hellfire_volley | weapon | applied | range 45, projectileSpeed 26, cooldown 10.64 |
| Vũ khí đề xuất | hmg_roof | weapon | applied | cooldown 0.1111, clip 100, clipReload 5.1111 |
| Vũ khí đề xuất | hmg_selfdef_15 | weapon | already | as the sheet |
| Vũ khí đề xuất | hmg_selfdef_18 | weapon | already | as the sheet |
| Vũ khí đề xuất | hmg_selfdef_21 | weapon | already | as the sheet |
| Vũ khí đề xuất | hover_ciws | weapon | already | as the sheet |
| Vũ khí đề xuất | hover_rockets | weapon | already | as the sheet |
| Vũ khí đề xuất | howitzer | weapon | already | as the sheet |
| Vũ khí đề xuất | howitzer_cb | weapon | already | as the sheet |
| Vũ khí đề xuất | howitzer_fixed | weapon | already | as the sheet |
| Vũ khí đề xuất | hq_flak | weapon | applied | cooldown 0.0286, clip 120, clipReload 3.0286 |
| Vũ khí đề xuất | ifv_30 | weapon | already | as the sheet |
| Vũ khí đề xuất | jassm | weapon | already | as the sheet |
| Vũ khí đề xuất | jet_bombs | weapon | already | as the sheet |
| Vũ khí đề xuất | jet_cannon | weapon | already | as the sheet |
| Vũ khí đề xuất | kh29 | weapon | already | as the sheet |
| Vũ khí đề xuất | kornet_multi | weapon | applied | projectileSpeed 22, cooldown 4.95 |
| Vũ khí đề xuất | kornet_top | weapon | applied | projectileSpeed 22, cooldown 4.6 |
| Vũ khí đề xuất | kornet_twin | weapon | applied | projectileSpeed 22, cooldown 10.51 |
| Vũ khí đề xuất | lancet | weapon | already | as the sheet |
| Vũ khí đề xuất | lancet_hangar | weapon | already | as the sheet |
| Vũ khí đề xuất | leviathan_460 | weapon | already | as the sheet |
| Vũ khí đề xuất | mg_coax | weapon | applied | cooldown 0.0833, clip 100, clipReload 4.0833 |
| Vũ khí đề xuất | mg_jeep | weapon | applied | cooldown 0.1111, clip 100, clipReload 5.1111 |
| Vũ khí đề xuất | mg_jeep_selfdef | weapon | already | as the sheet |
| Vũ khí đề xuất | minigun | weapon | applied | clip 200, clipReload 4.02 |
| Vũ khí đề xuất | mlrs_elite | weapon | applied | projectileSpeed 50 |
| Vũ khí đề xuất | mlrs_rockets | weapon | applied | projectileSpeed 50 |
| Vũ khí đề xuất | mortar_120 | weapon | already | as the sheet |
| Vũ khí đề xuất | mortar_240_fixed | weapon | already | as the sheet |
| Vũ khí đề xuất | mothership_cannon | weapon | applied | cooldown 3.29 |
| Vũ khí đề xuất | mothership_drones | weapon | applied | projectileSpeed 28, cooldown 8.47 |
| Vũ khí đề xuất | naval_100 | weapon | applied | cooldown 3.5 |
| Vũ khí đề xuất | naval_155_triple | weapon | already | as the sheet |
| Vũ khí đề xuất | naval_76 | weapon | applied | cooldown 3.1 |
| Vũ khí đề xuất | orbital_laser | weapon | already | as the sheet |
| Vũ khí đề xuất | patriot | weapon | already | as the sheet |
| Vũ khí đề xuất | r60 | weapon | already | as the sheet |
| Vũ khí đề xuất | railgun | weapon | already | as the sheet |
| Vũ khí đề xuất | recon_missile | weapon | applied | projectileSpeed 22 |
| Vũ khí đề xuất | rockets_300mm | weapon | already | as the sheet |
| Vũ khí đề xuất | s8_pods | weapon | applied | projectileSpeed 40 |
| Vũ khí đề xuất | sam | weapon | already | as the sheet |
| Vũ khí đề xuất | sam_48n6 | weapon | already | as the sheet |
| Vũ khí đề xuất | sam_battery | weapon | applied | projectileSpeed 60, cooldown 10.55 |
| Vũ khí đề xuất | sam_battery_lrr | weapon | already | as the sheet |
| Vũ khí đề xuất | sam_pac3 | weapon | already | as the sheet |
| Vũ khí đề xuất | sam_post | weapon | applied | projectileSpeed 50, cooldown 3.9 |
| Vũ khí đề xuất | scout_rockets | weapon | already | as the sheet |
| Vũ khí đề xuất | shahed | weapon | already | as the sheet |
| Vũ khí đề xuất | siege_gun_105 | weapon | already | as the sheet |
| Vũ khí đề xuất | siege_mortar_240 | weapon | already | as the sheet |
| Vũ khí đề xuất | stealth_payload | weapon | already | as the sheet |
| Vũ khí đề xuất | stinger_atas | weapon | already | as the sheet |
| Vũ khí đề xuất | swarm_drones | weapon | applied | projectileSpeed 26 |
| Vũ khí đề xuất | tamir | weapon | applied | projectileSpeed 50 |
| Vũ khí đề xuất | technical_rockets | weapon | applied | projectileSpeed 38, cooldown 5.6 |
| Vũ khí đề xuất | thermobaric_rockets | weapon | applied | projectileSpeed 35 |
| Vũ khí đề xuất | tower_ac25 | weapon | applied | burst 1, cooldown 0.125, clipReload 1.425 |
| Vũ khí đề xuất | tower_flak_30 | weapon | already | as the sheet |
| Vũ khí đề xuất | tower_hmg | weapon | applied | clip 100, clipReload 4.085 |
| Vũ khí đề xuất | tower_kornet | weapon | applied | cooldown 4.95 |
| Vũ khí đề xuất | train_gun | weapon | already | as the sheet |
| Vũ khí đề xuất | turret_gmlrs | weapon | already | as the sheet |
| Vũ khí đề xuất | turret_gun_120 | weapon | already | as the sheet |
| Vũ khí đề xuất | turret_gun_120_long | weapon | already | as the sheet |
| Vũ khí đề xuất | turret_rockets | weapon | already | as the sheet |
| Vũ khí đề xuất | turret_rockets_cluster | weapon | applied | damage 57, splash 4, cooldown 3.32 |
| Vũ khí đề xuất | twin_30_bmpt | weapon | already | as the sheet |
| Vũ khí đề xuất | twin_30_flak | weapon | already | as the sheet |
| Vũ khí đề xuất | twin_35_ahead | cadence | skipped | the sheet's mode, rate, rounds or rest cell is empty |
| Vũ khí đề xuất | twin_35_ahead | weapon | already | as the sheet |
| Vũ khí đề xuất | wvr_aam | weapon | already | as the sheet |
| Vũ khí đề xuất | zu23 | weapon | already | as the sheet |
| Đơn vị – vũ khí | light_tank | gun_launched_atgm | applied | Thêm tên lửa bắn qua nòng (1 quả × 200, xuyên 3, mỗi 20 s, tầm 34) |
| Đơn vị – vũ khí | mlrs | hmg_selfdef_15 | applied | dropped (kept 0) |
| Đơn vị – vũ khí | ballistic_launcher | hmg_selfdef_15 | applied | dropped (kept 0) |
| Đơn vị – vũ khí | heavy_rocket_artillery | hmg_selfdef_15 | applied | dropped (kept 0) |
| Đơn vị – vũ khí | aa_vehicle | sam | already | the Stinger stays (Giữ Stinger phụ — Gepard bản nâng cấp có thể mang Stinger.) |
| Đơn vị – vũ khí | sam_launcher | hmg_selfdef_18 | applied | dropped (kept 0) |
| Đơn vị – vũ khí | heavy_aa | sam | applied | Stinger -> 57E6: Đổi Stinger → tên lửa 57E6 (Pantsir): 1 × 220, Mảnh xuyên 3, tầm 55, tốc độ 55 |
| Đơn vị – vũ khí | scout_heli | loadout | already | its A1 row applied it (Hydra: 12 → 6 quả mỗi lần đầy đạn) |
| Đơn vị – vũ khí | swarm_carrier | loadout | already | its A1 row applied it (Vũ khí thêm theo đề xuất; Bỏ bom SDB; thêm 2 tên lửa hành trình Rapid Dragon mỗi lượt) |
| Đơn vị – vũ khí | stealth_fighter | loadout | already | its A1 row applied it (Thêm 1 AIM-120 mỗi lần đầy đạn) |
| Đơn vị – vũ khí | gunship_heli | loadout | already | its A1 row applied it (Đổi Hellfire → 9M120 Ataka) |
| Đơn vị – vũ khí | attack_jet | loadout | already | its A1 row applied it (FAB-250: 2 → 1 quả mỗi lần đầy đạn) |
| Đơn vị – vũ khí | wheeled_gun | hmg_roof | applied | added on slot mg |
| Vũ khí đề xuất | twin_35_ahead | DPS check | skipped | the sheet's DPS is None: a cadence cell is empty |
| Vũ khí đề xuất | gun_launched_atgm | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | missile_57e6 | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | sam_long | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | grad_rockets | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | atgm_heavy | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | jet_rockets | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | gun_155_sph | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | gun_105_twin | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | gun_203_siege | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | mortar_240 | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | igla_v | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | gsh_23v | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | heli_ataka | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | vikhr | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | gau_gatling | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | maverick | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | hind_rockets | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | gun_155_twin | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | gun_155_twin_ap | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | mg_coax_ground | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | gun_pit_105 | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | turret_gun_120_auto | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | gun_57_air | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | turret_thermobaric | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | howitzer_ext | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | gun_155_twin_long | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | tower_agl | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | atgm_post | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | drone_gun | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | supergun_800 | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | leviathan_cruise | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | train_mortar | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |
| Vũ khí đề xuất | naval_127 | weapon | skipped | not in the sheet: left as it is (families and the blast rule still apply) |

<!-- /step:A2 -->

<!-- step:A3 -->
## A3: weapon families (sheets Tốc độ tên lửa, Vũ khí đề xuất)

Weapons that are the same real weapon (the same real name once a mount's qualifier in brackets is dropped, the same damage type, round, size, and lobbed or direct) form a family in `weaponFamilies`: its speed, blast radius, round model and round weight (the tracer's and the report's) are written once there and every member takes them. A family's value is the sheet's most common proposal among its members (the current one where the sheet has none); where members disagreed, the report says which moved.

| Sheet | Applied | Already so | Deferred | Skipped |
|---|---|---|---|---|
| Tốc độ tên lửa, Vũ khí đề xuất | 25 | 10 | 0 | 0 |

| Sheet | id | Item | Outcome | Detail |
|---|---|---|---|---|
| Tốc độ tên lửa, Vũ khí đề xuất | 2a38_30_mm | family | applied | twin_30_flak, tower_flak_30, hq_flak: speed 280, blast 2.5; moved: tower_flak_30 roundWeight 7 -> 7.5 |
| Tốc độ tên lửa, Vũ khí đề xuất | 2a42_30_mm | family | applied | autocannon_30, ifv_30, twin_30_bmpt: speed 200, blast 0; moved: twin_30_bmpt projectileSpeed 210 -> 200; twin_30_bmpt roundWeight 30 -> 32 |
| Tốc độ tên lửa, Vũ khí đề xuất | 2a83_152_mm | family | applied | gun_152, bastion_gun: speed 160, blast 2.5; moved: bastion_gun projectileSpeed 200 -> 160; bastion_gun roundWeight 320 -> 343 |
| Tốc độ tên lửa, Vũ khí đề xuất | 2b11_120_mm | family | already | mortar_120, train_mortar: speed 32, blast 5, model mortar_bomb |
| Tốc độ tên lửa, Vũ khí đề xuất | 2b8_240_mm | family | applied | siege_mortar_240, mortar_240, mortar_240_fixed, boss_mortar: speed 38, blast 9, model mortar_bomb; moved: siege_mortar_240 splash 7.2 -> 9; mortar_240 splash 10 -> 9; mortar_240_fixed projectileSpeed 30 -> 38; mortar_240_fixed roundWeight 450 -> 543; boss_mortar projectileSpeed 36 -> 38; boss_mortar roundWeight 460 -> 543 |
| Tốc độ tên lửa, Vũ khí đề xuất | 9m120_ataka | family | already | ataka, heli_ataka: speed 26, blast 0, model atgm_ataka |
| Tốc độ tên lửa, Vũ khí đề xuất | 9m133_kornet | family | applied | atgm_heavy, kornet_twin, tower_kornet, kornet_top, kornet_multi, boss_missiles: speed 22, blast 0, model atgm_kornet; moved: atgm_heavy projectileSpeed 19 -> 22; atgm_heavy projectileModel "atgm_tow" -> "atgm_kornet" |
| Tốc độ tên lửa, Vũ khí đề xuất | 9m317_buk | family | applied | sam_long, buk_launcher, sam_post: speed 50, blast 2, model buk; moved: sam_long projectileSpeed 24 -> 50 |
| Tốc độ tên lửa, Vũ khí đề xuất | agm_114_hellfire | family | applied | heli_atgm, drone_missile, hellfire_volley, hellfire_standoff: speed 26, blast 0, model hellfire_longbow; moved: heli_atgm projectileModel "hellfire" -> "hellfire_longbow"; heli_atgm roundWeight 256 -> 270; drone_missile projectileModel "hellfire" -> "hellfire_longbow"; hellfire_volley roundWeight 260 -> 270; hellfire_standoff roundWeight 256 -> 270 |
| Tốc độ tên lửa, Vũ khí đề xuất | aim_9_sidewinder | family | applied | wvr_aam, aim9: speed 55, blast 1.5, model aim9; moved: aim9 roundWeight 236 -> 260 |
| Tốc độ tên lửa, Vũ khí đề xuất | ak_630_30_mm | family | already | hover_ciws, ciws_aa: speed 300, blast 0 |
| Tốc độ tên lửa, Vũ khí đề xuất | bm_21_grad_122_mm | family | applied | grad_rockets, turret_rockets: speed 45, blast 4.5, model grad; moved: grad_rockets projectileSpeed 52 -> 45; grad_rockets splash 3.5 -> 4.5; grad_rockets roundWeight 57 -> 66 |
| Tốc độ tên lửa, Vũ khí đề xuất | bm_21_grad_122_mm_2 | family | applied | grad_cluster, turret_rockets_cluster: speed 45, blast 4, model grad_cluster; moved: turret_rockets_cluster projectileModel "grad" -> "grad_cluster" |
| Tốc độ tên lửa, Vũ khí đề xuất | fpv_drone | family | applied | fpv_swarm, fpv_hangar, fpv_hangar_swarm, airship_drones, swarm_drones: speed 26, blast 2.5, model fpv_drone; moved: fpv_swarm projectileModel null -> "fpv_drone"; fpv_hangar projectileModel null -> "fpv_drone"; fpv_hangar_swarm projectileModel null -> "fpv_drone"; airship_drones projectileModel null -> "fpv_drone" |
| Tốc độ tên lửa, Vũ khí đề xuất | hydra_70_mm | family | applied | heli_rockets, scout_rockets, jet_rockets: speed 40, blast 3, model hydra; moved: heli_rockets roundWeight 40 -> 61; scout_rockets roundWeight 47 -> 61; jet_rockets projectileSpeed 48 -> 40; jet_rockets splash 3.5 -> 3 |
| Tốc độ tên lửa, Vũ khí đề xuất | l7_105_mm | family | already | gun_105_twin, siege_gun_105, gun_105_bunker: speed 190, blast 1.5 |
| Tốc độ tên lửa, Vũ khí đề xuất | m2_browning_12_7_mm | family | applied | mg_jeep, hmg_roof, hmg_selfdef_21, hmg_selfdef_18, hmg_selfdef_15, mg_jeep_selfdef, tower_hmg: speed 230, blast 0; moved: mg_jeep projectileSpeed 220 -> 230; mg_jeep roundWeight 9.5 -> 11; mg_jeep_selfdef projectileSpeed 220 -> 230; mg_jeep_selfdef roundWeight 9.5 -> 11 |
| Tốc độ tên lửa, Vũ khí đề xuất | m230_30_mm | family | already | heli_gun, boss_heli_gun: speed 220, blast 0 |
| Tốc độ tên lửa, Vũ khí đề xuất | m242_bushmaster_25_mm | family | already | autocannon_25, tower_ac25: speed 210, blast 0 |
| Tốc độ tên lửa, Vũ khí đề xuất | m284_155_mm | family | applied | gun_155_twin, gun_155_twin_fort, gun_155_twin_long, gun_155_coastal, gun_155_twin_coastlr: speed 150, blast 7, model shell_155; moved: gun_155_twin splash 4.5 -> 7; gun_155_twin_long splash 4.5 -> 7 |
| Tốc độ tên lửa, Vũ khí đề xuất | m284_155_mm_2 | family | applied | howitzer, howitzer_fixed, gun_155_sph, howitzer_cb, howitzer_ext, casemate_155: speed 45, blast 7, model shell_155; moved: gun_155_sph projectileSpeed 50 -> 45; gun_155_sph splash 8 -> 7; casemate_155 projectileSpeed 50 -> 45 |
| Tốc độ tên lửa, Vũ khí đề xuất | m31_gmlrs_227_mm | family | applied | mlrs_rockets, turret_gmlrs: speed 50, blast 4.5, model gmlrs; moved: mlrs_rockets roundWeight 100 -> 160 |
| Tốc độ tên lửa, Vũ khí đề xuất | mim_104_patriot_pac_2 | family | already | sam_battery, patriot, sam_battery_lrr: speed 60, blast 2.5, model patriot |
| Tốc độ tên lửa, Vũ khí đề xuất | mk_19_40_mm | family | already | agl_40, tower_agl: speed 70, blast 2 |
| Tốc độ tên lửa, Vũ khí đề xuất | nsv_12_7_mm | family | applied | bunker_hmg_twin, bunker_hmg, boss_hmg: speed 240, blast 0; moved: boss_hmg projectileSpeed 230 -> 240; boss_hmg roundWeight 11 -> 14 |
| Tốc độ tên lửa, Vũ khí đề xuất | oerlikon_35_mm | family | applied | flak_35, boss_flak: speed 260, blast 2.5; moved: boss_flak roundWeight 25 -> 26 |
| Tốc độ tên lửa, Vũ khí đề xuất | pkt_m240_7_62_mm | family | already | mg_coax, mg_coax_ground: speed 240, blast 0 |
| Tốc độ tên lửa, Vũ khí đề xuất | rh_120_l_44_120_mm | family | applied | gun_120mm, turret_gun_120, gun_pit_105, turret_gun_120_auto, gun_120_twin: speed 170, blast 1.5; moved: gun_120mm roundWeight 240 -> 290; turret_gun_120 roundWeight 240 -> 290; gun_pit_105 projectileSpeed 220 -> 170; gun_pit_105 splash 0 -> 1.5; turret_gun_120_auto roundWeight 240 -> 290; gun_120_twin roundWeight 240 -> 290 |
| Tốc độ tên lửa, Vũ khí đề xuất | s_8_80_mm | family | applied | gunship_rockets, s8_pods, hind_rockets, boat_rockets: speed 40, blast 3, model s8; moved: gunship_rockets splash 3.2 -> 3; gunship_rockets roundWeight 42 -> 60; s8_pods roundWeight 32 -> 60; hind_rockets projectileSpeed 48 -> 40; hind_rockets splash 3.5 -> 3; boat_rockets roundWeight 32 -> 60 |
| Tốc độ tên lửa, Vũ khí đề xuất | tos_1a_220_mm_thermobaric | family | already | thermobaric_rockets, boss_thermo: speed 35, blast 7, model tos_rocket |
| Tốc độ tên lửa, Vũ khí đề xuất | zala_lancet_3 | family | applied | lancet, lancet_hangar, mothership_drones: speed 28, blast 3, model lancet; moved: lancet splash 0 -> 3; lancet_hangar splash 0 -> 3; mothership_drones projectileModel null -> "lancet" |
| Tốc độ tên lửa, Vũ khí đề xuất | gun_155_twin_ap | family | applied | inherits gun_155_twin_fort but is another weapon: kept out of its family |
| Tốc độ tên lửa, Vũ khí đề xuất | turret_gun_120_long | family | applied | inherits turret_gun_120 but is another weapon: kept out of its family |
| Tốc độ tên lửa, Vũ khí đề xuất | turret_thermobaric | family | applied | inherits turret_rockets but is another weapon: kept out of its family |
| Tốc độ tên lửa, Vũ khí đề xuất | sam_pac3 | family | applied | inherits sam_battery but is another weapon: kept out of its family |

<!-- /step:A3 -->

<!-- step:A4 -->
## A4: sheet Tốc độ tên lửa

The sheet's proposed speed for every missile, rocket and drone it lists. A family member's speed is its family's (A3); where the sheet's row for one member differs from its family, the report says so. The sheet's ranges are checked against the weapon sheet's (A2 applied those).

| Sheet | Applied | Already so | Deferred | Skipped |
|---|---|---|---|---|
| Tốc độ tên lửa | 0 | 58 | 0 | 0 |

| Sheet | id | Item | Outcome | Detail |
|---|---|---|---|---|
| Tốc độ tên lửa | aim9 | speed | already | 55 m/s; 1.20 x its fastest target (46 m/s), below the sheet's 1.2-1.5 |
| Tốc độ tên lửa | air_cruise_missile | speed | already | 22 m/s |
| Tốc độ tên lửa | air_to_air | speed | already | 60 m/s |
| Tốc độ tên lửa | airship_drones | speed | already | 26 m/s |
| Tốc độ tên lửa | ataka | speed | already | 26 m/s |
| Tốc độ tên lửa | atgm | speed | already | 20 m/s; the sheet's range 34 differs from the weapon sheet's 40 (A2 kept) |
| Tốc độ tên lửa | ballistic_missile | speed | already | 50 m/s |
| Tốc độ tên lửa | boat_rockets | speed | already | 40 m/s |
| Tốc độ tên lửa | boss_missiles | speed | already | 22 m/s |
| Tốc độ tên lửa | boss_rockets | speed | already | 45 m/s |
| Tốc độ tên lửa | boss_thermo | speed | already | 35 m/s |
| Tốc độ tên lửa | buk_launcher | speed | already | 50 m/s |
| Tốc độ tên lửa | drone_missile | speed | already | 26 m/s |
| Tốc độ tên lửa | fpv_hangar | speed | already | 26 m/s |
| Tốc độ tên lửa | fpv_hangar_swarm | speed | already | 26 m/s |
| Tốc độ tên lửa | fpv_swarm | speed | already | 26 m/s |
| Tốc độ tên lửa | grad_cluster | speed | already | 45 m/s |
| Tốc độ tên lửa | griffin | speed | already | 22 m/s |
| Tốc độ tên lửa | guided_bomb | speed | already | 40 m/s |
| Tốc độ tên lửa | gunship_rockets | speed | already | 40 m/s |
| Tốc độ tên lửa | heli_atgm | speed | already | 26 m/s; the sheet's range 34 differs from the weapon sheet's 45 (A2 kept) |
| Tốc độ tên lửa | heli_rockets | speed | already | 40 m/s |
| Tốc độ tên lửa | hellfire_standoff | speed | already | 26 m/s |
| Tốc độ tên lửa | hellfire_volley | speed | already | 26 m/s; the sheet's range 34 differs from the weapon sheet's 45 (A2 kept) |
| Tốc độ tên lửa | hover_rockets | speed | already | 50 m/s |
| Tốc độ tên lửa | jassm | speed | already | 20 m/s |
| Tốc độ tên lửa | kh29 | speed | already | 32 m/s |
| Tốc độ tên lửa | kornet_multi | speed | already | 22 m/s |
| Tốc độ tên lửa | kornet_top | speed | already | 22 m/s |
| Tốc độ tên lửa | kornet_twin | speed | already | 22 m/s |
| Tốc độ tên lửa | lancet | speed | already | 28 m/s |
| Tốc độ tên lửa | lancet_hangar | speed | already | 28 m/s |
| Tốc độ tên lửa | mlrs_elite | speed | already | 50 m/s |
| Tốc độ tên lửa | mlrs_rockets | speed | already | 50 m/s |
| Tốc độ tên lửa | mothership_drones | speed | already | 28 m/s |
| Tốc độ tên lửa | patriot | speed | already | 60 m/s |
| Tốc độ tên lửa | r60 | speed | already | 42 m/s; 1.05 x its fastest target (40 m/s), below the sheet's 1.2-1.5 |
| Tốc độ tên lửa | recon_missile | speed | already | 22 m/s |
| Tốc độ tên lửa | rockets_300mm | speed | already | 55 m/s |
| Tốc độ tên lửa | s8_pods | speed | already | 40 m/s |
| Tốc độ tên lửa | sam | speed | already | 42 m/s |
| Tốc độ tên lửa | sam_48n6 | speed | already | 65 m/s |
| Tốc độ tên lửa | sam_battery | speed | already | 60 m/s |
| Tốc độ tên lửa | sam_battery_lrr | speed | already | 60 m/s |
| Tốc độ tên lửa | sam_pac3 | speed | already | 65 m/s; 1.18 x its fastest target (55 m/s), below the sheet's 1.2-1.5 |
| Tốc độ tên lửa | sam_post | speed | already | 50 m/s |
| Tốc độ tên lửa | scout_rockets | speed | already | 40 m/s |
| Tốc độ tên lửa | shahed | speed | already | 20 m/s |
| Tốc độ tên lửa | stinger_atas | speed | already | 42 m/s |
| Tốc độ tên lửa | swarm_drones | speed | already | 26 m/s |
| Tốc độ tên lửa | tamir | speed | already | 50 m/s; 0.91 x its fastest target (55 m/s), below the sheet's 1.2-1.5 |
| Tốc độ tên lửa | technical_rockets | speed | already | 38 m/s |
| Tốc độ tên lửa | thermobaric_rockets | speed | already | 35 m/s |
| Tốc độ tên lửa | tower_kornet | speed | already | 22 m/s |
| Tốc độ tên lửa | turret_gmlrs | speed | already | 50 m/s |
| Tốc độ tên lửa | turret_rockets | speed | already | 45 m/s |
| Tốc độ tên lửa | turret_rockets_cluster | speed | already | 45 m/s |
| Tốc độ tên lửa | wvr_aam | speed | already | 55 m/s; 1.20 x its fastest target (46 m/s), below the sheet's 1.2-1.5 |

<!-- /step:A4 -->

<!-- step:A5 -->
## A5: blast radius (sheets Tổng quan, Vũ khí đề xuất)

One blast radius for one round (its real name without the mount, damage type, size, a cluster or not) on every weapon that fires it: the weapon sheet's number where it gives one, else the rule of "Tổng quan" (10 m x (mass / 500 kg)^(1/3)) for rounds weighed in kilograms, else the calibre scale of the sheet's own numbers for the round's family (a shell's radius goes with its calibre). A family's radius is written on the family (A3).

| Sheet | Applied | Already so | Deferred | Skipped |
|---|---|---|---|---|
| Tổng quan, Vũ khí đề xuất | 5 | 68 | 2 | 0 |

| Sheet | id | Item | Outcome | Detail |
|---|---|---|---|---|
| Tổng quan, Vũ khí đề xuất | 122 mm thermobaric (HighExplosive, 122) | blast | applied | 4 m from the sheet's 7 m at 220 mm, scaled by calibre: turret_thermobaric; moved: turret_thermobaric 5.2 -> 4 |
| Tổng quan, Vũ khí đề xuất | 155 mm/60 (HighExplosive, 155) | blast | already | 4.5 m from the weapon sheet: naval_155_triple |
| Tổng quan, Vũ khí đề xuất | 2A38 30 mm (Fragmentation, 30) | blast | already | 2.5 m from the weapon sheet: twin_30_flak, tower_flak_30, hq_flak |
| Tổng quan, Vũ khí đề xuất | 2A44 203 mm (HighExplosive, 203) | blast | already | 8 m from the weapon sheet: boss_howitzer |
| Tổng quan, Vũ khí đề xuất | 2A46M-5 125 mm (Kinetic, 125) | blast | already | 1.5 m from the weapon sheet: gun_125_elite |
| Tổng quan, Vũ khí đề xuất | 2A65 152 mm (HighExplosive, 152) | blast | already | 6.5 m from the weapon sheet: gun_behemoth |
| Tổng quan, Vũ khí đề xuất | 2A70 100/76 mm (Kinetic, 76) | blast | already | 1.5 m from the weapon sheet: borer_cannon |
| Tổng quan, Vũ khí đề xuất | 2A83 152 mm (Kinetic, 152) | blast | already | 2.5 m from the weapon sheet: gun_152, bastion_gun |
| Tổng quan, Vũ khí đề xuất | 2A83 152 mm HE-FRAG (HighExplosive, 152) | blast | already | 6.5 m from the weapon sheet: gun_152_he |
| Tổng quan, Vũ khí đề xuất | 2A83 152 mm HEAT (ShapedCharge, 152) | blast | already | 3.5 m from the weapon sheet: gun_152_heat |
| Tổng quan, Vũ khí đề xuất | 2B11 120 mm (HighExplosive, 120) | blast | already | 5 m from the weapon sheet: mortar_120, train_mortar |
| Tổng quan, Vũ khí đề xuất | 2B8 240 mm (HighExplosive, 240) | blast | already | 9 m from the weapon sheet: siege_mortar_240, mortar_240, mortar_240_fixed, boss_mortar |
| Tổng quan, Vũ khí đề xuất | leviathan_cruise | blast | deferred | a boss system's own round the sheet gives no number for: task C1 |
| Tổng quan, Vũ khí đề xuất | 57E6 (Fragmentation, 7) | blast | applied | 2.5 m from the rule: 7 kg: missile_57e6; moved: missile_57e6 2 -> 2.5 |
| Tổng quan, Vũ khí đề xuất | 9K38 Igla-V (Fragmentation, 1.2) | blast | already | 1.5 m from the rule: 1.2 kg: igla_v |
| Tổng quan, Vũ khí đề xuất | 9M317 Buk (Fragmentation, 70) | blast | already | 2 m from the weapon sheet: sam_long, buk_launcher, sam_post |
| Tổng quan, Vũ khí đề xuất | 9M55 Smerch 300 mm (HighExplosive, 300) | blast | already | 8 m from the weapon sheet: rockets_300mm |
| Tổng quan, Vũ khí đề xuất | 9M723 Iskander (HighExplosive, 700) | blast | already | 10 m from the weapon sheet: ballistic_missile |
| Tổng quan, Vũ khí đề xuất | A-22 Ogon 140 mm (HighExplosive, 140) | blast | already | 4 m from the weapon sheet: hover_rockets |
| Tổng quan, Vũ khí đề xuất | AGM-158 JASSM (HighExplosive, 450) | blast | already | 9 m from the weapon sheet: jassm |
| Tổng quan, Vũ khí đề xuất | AIM-120 AMRAAM (Fragmentation, 20) | blast | already | 2 m from the weapon sheet: air_to_air |
| Tổng quan, Vũ khí đề xuất | AIM-9 Sidewinder (Fragmentation, 9.4) | blast | already | 1.5 m from the weapon sheet: wvr_aam, aim9 |
| Tổng quan, Vũ khí đề xuất | AK-100 100 mm (HighExplosive, 100) | blast | already | 3.5 m from the weapon sheet: naval_100 |
| Tổng quan, Vũ khí đề xuất | AU-220 57 mm (Fragmentation, 57) | blast | already | 3 m from the sheet's 3 m at 57 mm: gun_57_air |
| Tổng quan, Vũ khí đề xuất | AU-220 57 mm (HighExplosive, 57) | blast | already | 3.5 m from the weapon sheet: mothership_cannon |
| Tổng quan, Vũ khí đề xuất | AU-220 57 mm (Kinetic, 57) | blast | already | 1.5 m from the weapon sheet: gun_57_auto |
| Tổng quan, Vũ khí đề xuất | B-38 152 mm (Kinetic, 152) | blast | already | 2.5 m from the weapon sheet: train_gun |
| Tổng quan, Vũ khí đề xuất | BM-21 Grad 122 mm (HighExplosive, 122) | blast | applied | 4.5 m from the weapon sheet: grad_rockets, turret_rockets, boss_rockets; moved: boss_rockets 4 -> 4.5 |
| Tổng quan, Vũ khí đề xuất | BM-21 Grad 122 mm (HighExplosive, 122, cluster) | blast | already | 4 m from the weapon sheet: grad_cluster, turret_rockets_cluster |
| Tổng quan, Vũ khí đề xuất | Bofors 40 mm (Kinetic, 40) | blast | already | 1 m from the weapon sheet: autocannon_40 |
| Tổng quan, Vũ khí đề xuất | Bofors L/60 40 mm (HighExplosive, 40) | blast | already | 3 m from the weapon sheet: gunship_40mm |
| Tổng quan, Vũ khí đề xuất | FAB-250 (HighExplosive, 250) | blast | already | 8 m from the weapon sheet: jet_bombs |
| Tổng quan, Vũ khí đề xuất | FAB-500 (HighExplosive, 500) | blast | already | 10 m from the weapon sheet: bomber_payload |
| Tổng quan, Vũ khí đề xuất | FIM-92 Stinger (Fragmentation, 3) | blast | already | 1.5 m from the weapon sheet: stinger_atas |
| Tổng quan, Vũ khí đề xuất | FPV drone (ShapedCharge, 1.5) | blast | already | 2.5 m from the weapon sheet: fpv_swarm, fpv_hangar, fpv_hangar_swarm, airship_drones, swarm_drones |
| Tổng quan, Vũ khí đề xuất | GBU-31 JDAM (HighExplosive, 907) | blast | already | 13 m from the weapon sheet: stealth_payload |
| Tổng quan, Vũ khí đề xuất | GBU-39 SDB (HighExplosive, 110) | blast | already | 4 m from the weapon sheet: guided_bomb |
| Tổng quan, Vũ khí đề xuất | Hydra 70 mm (HighExplosive, 70) | blast | already | 3 m from the weapon sheet: heli_rockets, scout_rockets, jet_rockets |
| Tổng quan, Vũ khí đề xuất | Kh-101 (HighExplosive, 400) | blast | already | 9 m from the weapon sheet: air_cruise_missile |
| Tổng quan, Vũ khí đề xuất | L7 105 mm (Kinetic, 105) | blast | already | 1.5 m from the weapon sheet: gun_105_twin, siege_gun_105, gun_105_bunker |
| Tổng quan, Vũ khí đề xuất | M102 105 mm (HighExplosive, 105) | blast | already | 5.5 m from the weapon sheet: gunship_105 |
| Tổng quan, Vũ khí đề xuất | M110 203 mm (HighExplosive, 203) | blast | applied | 8 m from the sheet's 8 m at 203 mm: gun_203_siege; moved: gun_203_siege 6 -> 8 |
| Tổng quan, Vũ khí đề xuất | M284 155 mm (HighExplosive, 155) | blast | already | 7 m from the weapon sheet: howitzer, howitzer_fixed, gun_155_sph, gun_155_twin, gun_155_twin_fort, howitzer_cb, howitzer_ext, gun_155_twin_long, gun_155_coastal, gun_155_twin_coastlr, casemate_155 |
| Tổng quan, Vũ khí đề xuất | M30 GMLRS 227 mm (HighExplosive, 227, cluster) | blast | already | 5 m from the weapon sheet: mlrs_elite |
| Tổng quan, Vũ khí đề xuất | M31 GMLRS 227 mm (HighExplosive, 227) | blast | already | 4.5 m from the weapon sheet: mlrs_rockets, turret_gmlrs |
| Tổng quan, Vũ khí đề xuất | MIM-104 Patriot PAC-2 (Fragmentation, 90) | blast | already | 2.5 m from the weapon sheet: sam_battery, patriot, sam_battery_lrr |
| Tổng quan, Vũ khí đề xuất | Mk 19 40 mm (HighExplosive, 40) | blast | already | 2 m from the weapon sheet: agl_40, tower_agl |
| Tổng quan, Vũ khí đề xuất | Mk 45 127 mm (HighExplosive, 127) | blast | applied | 6 m from between the sheet's 5.5 m at 105 mm and 6.5 m at 152 mm: naval_127; moved: naval_127 4 -> 6 |
| Tổng quan, Vũ khí đề xuất | Mk 71 203 mm (HighExplosive, 203) | blast | already | 8 m from the weapon sheet: cruiser_203 |
| Tổng quan, Vũ khí đề xuất | NPzK 140 mm (Kinetic, 140) | blast | already | 2 m from the weapon sheet: gun_140_twin |
| Tổng quan, Vũ khí đề xuất | OTO Melara 76/62 (HighExplosive, 76) | blast | already | 3 m from the weapon sheet: naval_76 |
| Tổng quan, Vũ khí đề xuất | Oerlikon 35 mm (Fragmentation, 35) | blast | already | 2.5 m from the weapon sheet: flak_35, boss_flak |
| Tổng quan, Vũ khí đề xuất | Patriot PAC-3 MSE (Fragmentation, 100) | blast | already | 2.5 m from the weapon sheet: sam_pac3 |
| Tổng quan, Vũ khí đề xuất | Phalanx M61 20 mm (Fragmentation, 20) | blast | already | 1.2 m from the weapon sheet: c_ram_gatling |
| Tổng quan, Vũ khí đề xuất | R-60 (Fragmentation, 3.5) | blast | already | 1.5 m from the weapon sheet: r60 |
| Tổng quan, Vũ khí đề xuất | Rh-120 L/44 120 mm (Kinetic, 120) | blast | already | 1.5 m from the weapon sheet: gun_120mm, turret_gun_120, gun_pit_105, turret_gun_120_auto, gun_120_twin |
| Tổng quan, Vũ khí đề xuất | Rh-120 L/55 120 mm (Kinetic, 120) | blast | already | 1.5 m from the weapon sheet: turret_gun_120_long |
| Tổng quan, Vũ khí đề xuất | S-400 48N6 (Fragmentation, 180) | blast | already | 7.2 m from the weapon sheet: sam_48n6 |
| Tổng quan, Vũ khí đề xuất | S-60 57 mm (Fragmentation, 57) | blast | already | 3 m from the weapon sheet: airship_flak |
| Tổng quan, Vũ khí đề xuất | S-8 80 mm (HighExplosive, 80) | blast | already | 3 m from the weapon sheet: gunship_rockets, s8_pods, hind_rockets, boat_rockets |
| Tổng quan, Vũ khí đề xuất | Shahed-136 (HighExplosive, 50) | blast | already | 4.5 m from the weapon sheet: shahed |
| Tổng quan, Vũ khí đề xuất | Skyranger 35 mm AHEAD (Fragmentation, 35) | blast | already | 4 m from the weapon sheet: twin_35_ahead |
| Tổng quan, Vũ khí đề xuất | Starstreak / Stinger SHORAD (Fragmentation, 3) | blast | already | 2 m from the weapon sheet: sam |
| Tổng quan, Vũ khí đề xuất | TOS-1A 220 mm thermobaric (HighExplosive, 220) | blast | already | 7 m from the weapon sheet: thermobaric_rockets, boss_thermo |
| Tổng quan, Vũ khí đề xuất | Tamir interceptor (Fragmentation, 1) | blast | already | 2.5 m from the weapon sheet: tamir |
| Tổng quan, Vũ khí đề xuất | Type 63 107 mm (HighExplosive, 107) | blast | already | 3.5 m from the weapon sheet: technical_rockets |
| Tổng quan, Vũ khí đề xuất | Type 94 460 mm/45 (HighExplosive, 460) | blast | already | 13 m from the weapon sheet: leviathan_460 |
| Tổng quan, Vũ khí đề xuất | ZALA Lancet-3 (ShapedCharge, 3) | blast | already | 3 m from the weapon sheet: lancet, lancet_hangar, mothership_drones |
| Tổng quan, Vũ khí đề xuất | ZSU-23-4 23 mm (Fragmentation, 23) | blast | already | 3.5 m from the weapon sheet: flak_quad |
| Tổng quan, Vũ khí đề xuất | car bomb (HighExplosive, 900) | blast | already | 10 m from the weapon sheet: detonator |
| Tổng quan, Vũ khí đề xuất | flamethrower (Fire, 1) | blast | already | 2.5 m from the weapon sheet: flamethrower |
| Tổng quan, Vũ khí đề xuất | flamethrower (Fire, 2) | blast | already | 4.5 m from the weapon sheet: bunker_flame |
| Tổng quan, Vũ khí đề xuất | flamethrower (Fire, 3) | blast | already | 3.5 m from the weapon sheet: boss_flamer |
| Tổng quan, Vũ khí đề xuất | laser (Energy, 150) | blast | already | 1.5 m from the weapon sheet: orbital_laser |
| Tổng quan, Vũ khí đề xuất | supergun_800 | blast | deferred | a boss system's own round the sheet gives no number for: task C1 |

<!-- /step:A5 -->

<!-- step:B7 -->
## B.7: CP prices (sheets Giá CP, Kích thước – giá)

The column "CP đề xuất" of "Giá CP", checked against "CP sau đề xuất" of "Kích thước – giá". Most were applied by their A1 rows; a sheet whose two price columns disagree keeps the price sheet's.

| Sheet | Applied | Already so | Deferred | Skipped |
|---|---|---|---|---|
| Giá CP | 0 | 58 | 0 | 0 |

| Sheet | id | Item | Outcome | Detail |
|---|---|---|---|---|
| Giá CP | hover_gunboat | cp | already | 0 CP |
| Giá CP | armored_car | cp | already | 3 CP |
| Giá CP | ifv | cp | already | 6 CP |
| Giá CP | supply_truck | cp | already | 0 CP |
| Giá CP | engineer_vehicle | cp | already | 3 CP |
| Giá CP | smoke_carrier | cp | already | 3 CP |
| Giá CP | ammo_carrier | cp | already | 4 CP |
| Giá CP | counter_battery_radar | cp | already | 5 CP |
| Giá CP | ew_jammer | cp | already | 5 CP |
| Giá CP | mine_layer | cp | already | 5 CP |
| Giá CP | command_vehicle | cp | already | 6 CP |
| Giá CP | shield_carrier | cp | already | 7 CP |
| Giá CP | scout_jeep | cp | already | 2 CP |
| Giá CP | vbied | cp | already | 3 CP |
| Giá CP | light_tank | cp | already | 3 CP |
| Giá CP | flame_tank | cp | already | 5 CP |
| Giá CP | turtle_tank | cp | already | 7 CP |
| Giá CP | bmpt | cp | already | 9 CP |
| Giá CP | rocket_technical | cp | already | 3 CP |
| Giá CP | mortar_carrier | cp | already | 4 CP |
| Giá CP | artillery | cp | already | 6 CP |
| Giá CP | mlrs | cp | already | 7 CP |
| Giá CP | shahed_truck | cp | already | 8 CP |
| Giá CP | thermobaric_launcher | cp | already | 9 CP |
| Giá CP | ballistic_launcher | cp | already | 11 CP |
| Giá CP | heavy_rocket_artillery | cp | already | 12 CP |
| Giá CP | siege_tank | cp | already | 12 CP |
| Giá CP | zu23_technical | cp | already | 3 CP |
| Giá CP | aa_vehicle | cp | already | 4 CP |
| Giá CP | sam_launcher | cp | already | 7 CP |
| Giá CP | heavy_aa | cp | already | 7 CP |
| Giá CP | iron_beam | cp | already | 6 CP |
| Giá CP | long_sam | cp | already | 14 CP |
| Giá CP | scout_heli | cp | already | 5 CP |
| Giá CP | recon_drone | cp | already | 6 CP |
| Giá CP | wingman_drone | cp | already | 6 CP |
| Giá CP | strike_drone | cp | already | 9 CP |
| Giá CP | swarm_carrier | cp | already | 13 CP |
| Giá CP | attack_helicopter | cp | already | 9 CP |
| Giá CP | fighter_jet | cp | already | 12 CP |
| Giá CP | stealth_fighter | cp | already | 13 CP |
| Giá CP | gunship_heli | cp | already | 15 CP |
| Giá CP | attack_jet | cp | already | 18 CP |
| Giá CP | stealth_bomber | cp | already | 21 CP |
| Giá CP | heavy_bomber | cp | already | 22 CP |
| Giá CP | sky_gunship | cp | already | 22 CP |
| Giá CP | bunker_vehicle | cp | already | 6 CP |
| Giá CP | armored_bulldozer | cp | already | 7 CP |
| Giá CP | main_battle_tank | cp | already | 7 CP |
| Giá CP | twin_tank | cp | already | 9 CP |
| Giá CP | heavy_tank | cp | already | 13 CP |
| Giá CP | titan_tank | cp | already | 18 CP |
| Giá CP | fpv_carrier | cp | already | 6 CP |
| Giá CP | lancet_truck | cp | already | 6 CP |
| Giá CP | wheeled_gun | cp | already | 6 CP |
| Giá CP | tank_destroyer | cp | already | 6 CP |
| Giá CP | railgun_truck | cp | already | 10 CP |
| Giá CP | laser_tank | cp | already | 9 CP |

<!-- /step:B7 -->

<!-- step:B8 -->
## B.8: support cards (sheet Thẻ hỗ trợ)

The sheet names cards by their Vietnamese titles; the table below maps them to the supports' ids (checked against the sheet's "Hiện tại"). Damage in the sheet is what lands (after the strikes' firepower, x2): the data holds half. Where a row offers two options, the one taken is in the detail (DECISIONS 25A).

| Sheet | Applied | Already so | Deferred | Skipped |
|---|---|---|---|---|
| Thẻ hỗ trợ | 3 | 6 | 0 | 0 |

| Sheet | id | Item | Outcome | Detail |
|---|---|---|---|---|
| Thẻ hỗ trợ | airstrike | card | applied | option 1: 4 FAB-500s of 420 (the bomber's), each blast 10 m by the bomb scale, 9 CP; the bomb line's half-width stays 6 m; count 6 -> 4, damage 400 -> 210, blast 8 -> 10 |
| Thẻ hỗ trợ | artillery_barrage | card | applied | option 2: 6 shells (was 8): the card was strong for its price; each shell's blast 7 m, the 155 mm howitzer round's (one round, one radius); the circle they fall in stays 10 m; count 8 -> 6, blast 6 -> 7 |
| Thẻ hỗ trợ | cruise_missile | card | applied | option 1: 600 (a Tomahawk's ~450 kg), a 10 m blast, the circle shown on the map the same 10 m (it was 15 round an 18 m blast); damage 520 -> 300, blast 18 -> 10, radius 15 -> 10 |
| Thẻ hỗ trợ | napalm_strike | card | already | Bom napalm: kept (9 CP · 8 × 300 · bán kính 5) |
| Thẻ hỗ trợ | sead_strike | card | already | Đòn SEAD: kept (7 CP · 500) |
| Thẻ hỗ trợ | smoke_screen | card | already | Màn khói: kept (—) |
| Thẻ hỗ trợ | uav_scan | card | already | UAV quét: kept (—) |
| Thẻ hỗ trợ | repair_drop | card | already | Sửa chữa: kept (—) |
| Thẻ hỗ trợ | field_tower | card | already | Tháp dã chiến: kept (—) |

<!-- /step:B8 -->

<!-- step:review -->
## To measure in the test phase: "Xem lại", "Theo dõi" and the rows a measurement should judge

The owner's rule of 30/09: no test or measurement runs until a test phase is approved. The rows below need a measurement (prompt 13's combat value, CombatValueMeasure with MB_BALANCE=1, 3-5 seeds, the cards named) before they change: each keeps the game's value for now. "Xem lại" rows are judged by the measurement; "Theo dõi" rows change only if it confirms; the others are changes applied from the sheet whose words and numbers disagree, or that the sheet's own "Cân bằng lần 2" asks to re-measure.

| Sheet | Applied | Already so | Deferred | Skipped |
|---|---|---|---|---|
| Cân bằng lần 2 | 0 | 0 | 4 | 0 |
| Kiểm tra từng mục | 0 | 0 | 14 | 0 |
| Vũ khí đề xuất / Thay đổi chi tiết | 0 | 0 | 6 | 0 |

| Sheet | id | Item | Outcome | Detail |
|---|---|---|---|---|
| Kiểm tra từng mục | engineer_vehicle | Tốc độ | deferred | Xem lại: kept 7 (the sheet: Mẫu thật × hệ số map ≈ 4.4 m/s); to measure in the test phase |
| Kiểm tra từng mục | smoke_carrier | Tốc độ | deferred | Xem lại: kept 8 (the sheet: Mẫu thật × hệ số map ≈ 5.9 m/s); to measure in the test phase |
| Kiểm tra từng mục | mine_layer | Tốc độ | deferred | Xem lại: kept 8 (the sheet: Mẫu thật × hệ số map ≈ 5.5 m/s); to measure in the test phase |
| Kiểm tra từng mục | vbied | Tốc độ | deferred | Xem lại: kept 13 (the sheet: Mẫu thật × hệ số map ≈ 6.7 m/s); to measure in the test phase |
| Kiểm tra từng mục | light_tank | Tốc độ | deferred | Xem lại: kept 9 (the sheet: Mẫu thật × hệ số map ≈ 4.0 m/s); to measure in the test phase |
| Kiểm tra từng mục | flame_tank | Tốc độ | deferred | Xem lại: kept 6.5 (the sheet: Mẫu thật × hệ số map ≈ 4.6 m/s); to measure in the test phase |
| Kiểm tra từng mục | mortar_carrier | Tốc độ | deferred | Xem lại: kept 8 (the sheet: Mẫu thật × hệ số map ≈ 5.9 m/s); to measure in the test phase |
| Kiểm tra từng mục | mlrs | Tốc độ | deferred | Xem lại: kept 6 (the sheet: Mẫu thật × hệ số map ≈ 9.4 m/s); to measure in the test phase |
| Kiểm tra từng mục | thermobaric_launcher | Máu | deferred | Xem lại: kept 1980 (the sheet: Máu/CP gấp 2.1 lần trung vị lớp; giữ nếu đó là bản sắc (xe chịu đòn)); to measure in the test phase |
| Kiểm tra từng mục | siege_tank | Máu | deferred | Xem lại: kept 3300 (the sheet: Máu/CP gấp 2.3 lần trung vị lớp; giữ nếu đó là bản sắc (xe chịu đòn)); to measure in the test phase |
| Kiểm tra từng mục | siege_tank | Tầm nhìn | deferred | Xem lại: kept 38 (the sheet: ~30 m); to measure in the test phase |
| Kiểm tra từng mục | strike_drone | Tốc độ | deferred | Xem lại: kept 19 (the sheet: Mẫu thật × hệ số map ≈ 13.9 m/s); to measure in the test phase |
| Kiểm tra từng mục | swarm_carrier | Máu | deferred | Xem lại: kept 3080 (the sheet: Máu/CP gấp 3.3 lần trung vị lớp; giữ nếu đó là bản sắc (xe chịu đòn)); to measure in the test phase |
| Kiểm tra từng mục | sky_gunship | Máu | deferred | Xem lại: kept 4400 (the sheet: Máu/CP gấp 1.7 lần trung vị lớp; giữ nếu đó là bản sắc (xe chịu đòn)); to measure in the test phase |
| Cân bằng lần 2 | rocket_technical | Theo dõi | deferred | Theo dõi: kept (CP 3); Hai phép đo lệch nhau (DPS lý thuyết khác giá trị thực chiến): nguyên nhân thường là thời gian sống, thời gian bắn hoặc tầm; chạy mô phỏng trước khi đổi.; to measure in the test phase |
| Cân bằng lần 2 | long_sam | Theo dõi | deferred | Theo dõi: kept (CP 14); Hai phép đo lệch nhau (DPS lý thuyết khác giá trị thực chiến): nguyên nhân thường là thời gian sống, thời gian bắn hoặc tầm; chạy mô phỏng trước khi đổi.; to measure in the test phase |
| Cân bằng lần 2 | attack_jet | Đã giảm ở đợt 2 | deferred | Đã giảm ở đợt 2: kept (CP 18); Đã giảm thêm ở đợt 2 (xem Thay đổi chi tiết). Cột giá trị thực chiến là số đo mô phỏng cũ, cần chạy lại mô phỏng để xác nhận.; to measure in the test phase |
| Cân bằng lần 2 | heavy_bomber | Đã giảm ở đợt 2 | deferred | Đã giảm ở đợt 2: kept (CP 22); Đã giảm thêm ở đợt 2 (xem Thay đổi chi tiết). Cột giá trị thực chiến là số đo mô phỏng cũ, cần chạy lại mô phỏng để xác nhận.; to measure in the test phase |
| Vũ khí đề xuất / Thay đổi chi tiết | zu23_technical | zu23 | deferred | the row says "giữ DPS"; its numbers give 70 a second (was 143) on a card already at 0.24 of the AA median; to measure in the test phase |
| Vũ khí đề xuất / Thay đổi chi tiết | heavy_aa | twin_30_flak | deferred | "giữ DPS"; its numbers give 171 (was 252); to measure in the test phase |
| Vũ khí đề xuất / Thay đổi chi tiết | aa_turret | tower_flak_30 | deferred | the sheet wanted its anti-aircraft value 300 -> 240; the weapon row gives 131 a second (was 193); to measure in the test phase |
| Vũ khí đề xuất / Thay đổi chi tiết | headquarters | hq_flak | deferred | the HQ's flak at 140 (was 157), the 2A38 family's stream; to measure in the test phase |
| Vũ khí đề xuất / Thay đổi chi tiết | scout_heli | scout_rockets | deferred | six Hydras a load (was 24; the sheet read 12, the salvo) and 5 CP; to measure in the test phase |
| Vũ khí đề xuất / Thay đổi chi tiết | flame_tank | flamethrower | deferred | 21 a tick on every target (the row meant -10 % on light vehicles only); to measure in the test phase |

<!-- /step:review -->

<!-- import_names:begin -->
## Tên đề xuất

Applied by `Tools/balance/import_names.py` (prompt 25 D1, DECISIONS 25D1): 63 rows applied, 1 skipped. A row applies its full name, its short name and its English name to `unit.<id>` and `short.<id>`, the head of `guide.<id>`, and every text that named the unit by its old name.

| id | full name (vi) | short (vi) | English | English short | before |
|---|---|---|---|---|---|
| `hover_gunboat` | Xuồng đệm khí hộ tống | Xuồng hộ tống | Escort hovercraft | Hovercraft | Xuồng cao tốc đệm khí / Hover gunboat |
| `armored_car` | Xe bọc thép bánh lốp | Bánh lốp | Armoured car | Armoured car | Xe bọc thép / Armored car |
| `ifv` | Xe chiến đấu bộ binh | Xe bộ binh | Infantry fighting vehicle | IFV | Xe chiến đấu bộ binh / Infantry fighting vehicle |
| `supply_truck` | Xe tải tiếp tế | Tiếp tế | Supply truck | Supply truck | Xe tiếp tế / Supply truck |
| `engineer_vehicle` | Xe công binh | Công binh | Engineering vehicle | Engineer | Xe công binh / Engineer vehicle |
| `smoke_carrier` | Xe thả khói | Xe khói | Smoke carrier | Smoke carrier | Xe tạo khói / Smoke generator carrier |
| `ammo_carrier` | Xe tiếp đạn | Tiếp đạn | Ammo carrier | Ammo carrier | Xe tiếp đạn / Ammunition carrier |
| `counter_battery_radar` | Xe radar phản pháo | Radar phản pháo | Counter-battery radar | CB radar | Radar phản pháo / Counter-battery radar |
| `ew_jammer` | Xe gây nhiễu điện tử | Gây nhiễu | EW jammer | Jammer | Xe tác chiến điện tử / EW jammer |
| `mine_layer` | Xe rải mìn | Rải mìn | Minelayer | Minelayer | Xe rải mìn / Mine layer |
| `command_vehicle` | Xe chỉ huy | Chỉ huy | Command vehicle | Command | Xe chỉ huy / Command vehicle |
| `shield_carrier` | Xe phát khiên | Phát khiên | Shield carrier | Shield carrier | Xe phát khiên / Shield carrier |
| `scout_jeep` | Xe trinh sát hạng nhẹ | Trinh sát | Scout jeep | Scout | Xe trinh sát / Scout jeep |
| `vbied` | Xe bom bọc thép | Xe bom | Armoured car bomb | Car bomb | Xe bom tự sát bọc thép / Armoured car bomb |
| `light_tank` | Tăng nhẹ lội nước | Tăng nhẹ | Amphibious light tank | Light tank | Tăng hạng nhẹ / Light tank |
| `flame_tank` | Tăng phun lửa | Phun lửa | Flame tank | Flame tank | Tăng phun lửa / Flame tank |
| `turtle_tank` | Tăng mái che | Tăng rùa | Turtle tank | Turtle tank | Xe tăng rùa / Turtle tank |
| `bmpt` | Xe hỗ trợ tăng | Hỗ trợ tăng | Tank support vehicle | Tank support | BMPT Terminator / BMPT Terminator |
| `rocket_technical` | Bán tải rốc-két | Bán tải rốc-két | Rocket technical | Rocket pickup | Bán tải rốc-két / Rocket technical |
| `mortar_carrier` | Xe cối tự hành | Xe cối | Mortar carrier | Mortar | Xe súng cối / Mortar carrier |
| `artillery` | Lựu pháo tự hành | Lựu pháo | SP howitzer | SP howitzer | Pháo tự hành / Artillery |
| `mlrs` | Pháo phản lực dẫn đường | Phản lực | Guided MLRS | Guided MLRS | Pháo phản lực / Rocket launcher |
| `shahed_truck` | Xe phóng drone cảm tử tầm xa | Drone cảm tử | Long-range drone launcher | Kamikaze drones | Xe phóng Shahed / Shahed launcher truck |
| `thermobaric_launcher` | Pháo phản lực nhiệt áp | Nhiệt áp | Thermobaric launcher | Thermobaric | Pháo phản lực nhiệt áp / Thermobaric launcher |
| `ballistic_launcher` | Xe phóng tên lửa chiến thuật | TL chiến thuật | Tactical ballistic launcher | Ballistic | Xe phóng tên lửa đạn đạo / Ballistic missile launcher |
| `heavy_rocket_artillery` | Pháo phản lực hạng nặng | Phản lực nặng | Heavy MLRS | Heavy MLRS | Pháo phản lực hạng nặng / Heavy rocket artillery |
| `siege_tank` | Pháo cối công thành | Công thành | Siege mortar | Siege mortar | Tăng công thành / Siege tank |
| `zu23_technical` | Bán tải cao xạ | Cao xạ bán tải | Flak technical | Flak technical | Bán tải ZU-23 / ZU-23 technical |
| `aa_vehicle` | Pháo cao xạ tự hành | Cao xạ | Self-propelled AA gun | AA gun | Xe phòng không / Anti-air |
| `sam_launcher` | Xe tên lửa phòng không tầm trung | PK tầm trung | Medium-range SAM | Medium SAM | Tên lửa phòng không / SAM launcher |
| `heavy_aa` | Xe phòng không pháo – tên lửa | PK hỗn hợp | Gun–missile AA | Gun–missile AA | Pháo tên lửa phòng không / Gun-missile air defence |
| `iron_beam` | Xe la-de phòng không | La-de PK | Laser AA | Laser AA | La-de phòng không / Iron Beam laser |
| `long_sam` | Xe tên lửa phòng không tầm xa | PK tầm xa | Long-range SAM | Long-range SAM | Tên lửa phòng không tầm xa / Long-range SAM |
| `scout_heli` | Trực thăng trinh sát vũ trang | TT trinh sát | Armed scout helicopter | Scout heli | Trực thăng trinh sát / Scout helicopter |
| `recon_drone` | UAV trinh sát | UAV trinh sát | Recon UAV | Recon UAV | UAV trinh sát / Recon drone |
| `wingman_drone` | Drone hộ vệ | Drone hộ vệ | Wingman drone | Wingman | Drone hộ vệ / Loyal wingman |
| `strike_drone` | UAV tấn công | UAV tấn công | Strike UAV | Strike UAV | UAV tấn công / Strike drone |
| `swarm_carrier` | Máy bay mẹ thả drone | Máy bay mẹ | Drone mothership aircraft | Mothership | Máy bay mẹ thả drone / Drone mothership |
| `attack_helicopter` | Trực thăng tấn công | TT tấn công | Attack helicopter | Attack heli | Trực thăng tấn công / Attack helicopter |
| `fighter_jet` | Tiêm kích | Tiêm kích | Fighter | Fighter | Tiêm kích / Fighter jet |
| `stealth_fighter` | Tiêm kích tàng hình | TK tàng hình | Stealth fighter | Stealth fighter | Tiêm kích tàng hình / Stealth fighter |
| `gunship_heli` | Trực thăng vũ trang bọc giáp | TT vũ trang | Armoured gunship helicopter | Gunship heli | Trực thăng hạng nặng / Heavy gunship |
| `attack_jet` | Máy bay cường kích | Cường kích | Attack jet | Attack jet | Máy bay cường kích / Attack jet |
| `stealth_bomber` | Oanh tạc cơ tàng hình | OTC tàng hình | Stealth bomber | Stealth bomber | Máy bay ném bom tàng hình / Stealth bomber |
| `heavy_bomber` | Oanh tạc cơ chiến lược | Oanh tạc cơ | Strategic bomber | Bomber | Oanh tạc cơ hạng nặng / Heavy bomber |
| `sky_gunship` | Pháo hạm bay | Pháo hạm | Airborne gunship | Gunship | Pháo hạm AC-130 / AC-130 Gunship |
| `bunker_vehicle` | Xe công sự triển khai | Công sự | Deployable bunker | Bunker | Xe công sự / Bunker vehicle |
| `armored_bulldozer` | Xe ủi bọc thép | Xe ủi | Armoured bulldozer | Bulldozer | Xe ủi bọc thép / Armoured bulldozer |
| `main_battle_tank` | Tăng chủ lực | Tăng chủ lực | Main battle tank | Battle tank | Tăng chủ lực / Main battle tank |
| `twin_tank` | Tăng hai nòng | Hai nòng | Twin-gun tank | Twin-gun tank | Tăng hai nòng / Twin-barrel tank |
| `heavy_tank` | Tăng hạng nặng | Tăng nặng | Heavy tank | Heavy tank | Tăng hạng nặng / Heavy tank |
| `titan_tank` | Siêu tăng | Siêu tăng | Super-heavy tank | Super tank | Siêu tăng Titan / Titan super tank |
| `fpv_carrier` | Xe phóng drone FPV | Drone FPV | FPV drone carrier | FPV drones | Xe phóng drone FPV / FPV drone carrier |
| `lancet_truck` | Xe phóng đạn lảng vảng | Đạn lảng vảng | Loitering munition truck | Loiter munition | Xe phóng Lancet / Loitering munition truck |
| `wheeled_gun` | Pháo xung kích bánh lốp | Pháo xung kích | Wheeled tank destroyer | Wheeled gun | Pháo bánh lốp diệt tăng / Wheeled tank hunter |
| `tank_destroyer` | Pháo chống tăng tự hành | Chống tăng | Tank destroyer | Tank destroyer | Pháo chống tăng / Tank destroyer |
| `railgun_truck` | Xe pháo điện từ | Pháo điện từ | Railgun truck | Railgun | Xe súng điện từ / Railgun truck |
| `laser_tank` | Xe la-de diệt tăng | La-de diệt tăng | Laser tank destroyer | Laser tank | Xe la-de tập trung / Focused-laser tank |
| `c_ram` | Trạm đánh chặn C-RAM | C-RAM | C-RAM interceptor | C-RAM | Trạm C-RAM / C-RAM |
| `drone_hangar` | Nhà chứa drone | Nhà chứa drone | Drone hangar | Drone hangar | Nhà chứa drone / Drone hangar |
| `heavy_turret` | Tháp pháo hạng nặng | Pháo hạng nặng | Heavy gun turret | Heavy gun | Pháo đài hạng nặng / Heavy fortress |
| `missile_battery` | Trạm tên lửa phòng không tầm xa | Trạm PK tầm xa | Long-range SAM site | SAM site | Tên lửa Patriot tầm xa / Patriot battery |
| `bulwark_post` | Ụ súng dã chiến | Ụ súng | Field gun post | Gun post | Ụ súng tạm / Fallback post |

Changed from the sheet:

- `ballistic_launcher` short name "TL chiến thuật": "Tên lửa chiến thuật" is 19 letters, over the 15 of one card line; "TL" is the short names' abbreviation of "tên lửa".
- `wheeled_gun` short name "Pháo xung kích": "Bánh lốp diệt tăng" is 18 letters; the first words of the full name instead.
- `missile_battery` short name "Trạm PK tầm xa": "PK tầm xa" is the long-range SAM vehicle's short name too; the tower keeps the "Trạm" of its full name.
- English names in sentence case and British spelling (the glossary): "Armored Car" is "Armoured car". English short names are the script's (the sheet has none).

Skipped:

- `spawn_bastion` (Tháp căn cứ): the sheet proposes no name ("kiểm tra còn dùng không"): the bastion is only the fallback of ModeSupport.Build when the catalogue has no HQ, which the shipped content always has; its old name stays until the base system drops it.

<!-- import_names:end -->
