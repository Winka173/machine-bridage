# Balance spreadsheet: apply report (prompt 25)

What `Tools/balance/import_xlsx.py` applied from `Docs/balance/Machine_Brigade_Can_bang.xlsx`, sheet by sheet, and
what it left and why. Outcomes: **applied** (the data now holds the sheet's number), **already** (the data already
held it), **deferred** (the row belongs to a later task of the sheet "Việc cho agent": names D1, model sizes B1,
models B2, bosses C1, boss weapons C2), **skipped** (no id in the data, a contradiction, or a measurement that did not
confirm it). Decisions and their reasons: `Docs/DECISIONS.md`, section 25A. Each step's section is rewritten when the
script runs it again.

<!-- step:A1-Cao -->
## A1 Cao: sheet Thay đổi chi tiết

| Sheet | Applied | Already so | Deferred | Skipped |
|---|---|---|---|---|
| Thay đổi chi tiết | 1 | 26 | 6 | 0 |
| Vũ khí đề xuất | 0 | 15 | 0 | 0 |
| Đơn vị – vũ khí | 0 | 2 | 0 | 0 |

| Sheet | id | Item | Outcome | Detail |
|---|---|---|---|---|
| Vũ khí đề xuất | tower_flak_30 | weapon | already | as the sheet (for aa_turret: Vũ khí và tham khảo) |
| Thay đổi chi tiết | aa_turret | Vũ khí và tham khảo | applied | choice: the reference moves to the 2A38 (the weapon is kept); the anti-aircraft value falls through the tower flak's new rate (tower_flak_30's row) |
| Vũ khí đề xuất | howitzer | weapon | already | as the sheet (for artillery: Vũ khí: lựu pháo 155 mm) |
| Thay đổi chi tiết | artillery | Vũ khí: lựu pháo 155 mm | already | the data already holds it |
| Thay đổi chi tiết | artillery | Model và tham khảo | deferred | model and reference follow the model change: task B2 (the armour and speed are its Trung rows) |
| Thay đổi chi tiết | attack_helicopter | Giá | already | the data already holds it |
| Vũ khí đề xuất | jet_bombs | weapon | already | as the sheet (for attack_jet: Vũ khí: FAB-250) |
| Thay đổi chi tiết | attack_jet | Vũ khí: FAB-250 | already | the data already holds it |
| Vũ khí đề xuất | kh29 | weapon | already | as the sheet (for attack_jet: Vũ khí: Kh-29L, R-60) |
| Vũ khí đề xuất | r60 | weapon | already | as the sheet (for attack_jet: Vũ khí: Kh-29L, R-60) |
| Thay đổi chi tiết | attack_jet | Vũ khí: Kh-29L, R-60 | already | the data already holds it |
| Thay đổi chi tiết | attack_jet | Giá | already | the data already holds it |
| Thay đổi chi tiết | caspian | Vũ khí | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | daedalus | Máu, vũ khí | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Vũ khí đề xuất | air_to_air | weapon | already | as the sheet (for fighter_jet: Vũ khí: AIM-120, AIM-9X) |
| Vũ khí đề xuất | wvr_aam | weapon | already | as the sheet (for fighter_jet: Vũ khí: AIM-120, AIM-9X) |
| Thay đổi chi tiết | fighter_jet | Vũ khí: AIM-120, AIM-9X | already | the data already holds it |
| Thay đổi chi tiết | heavy_tank | Giá (CP) | already | the data already holds it |
| Thay đổi chi tiết | iron_beam | Giá | already | the data already holds it |
| Vũ khí đề xuất | hel_beam | weapon | already | as the sheet (for iron_beam: Vũ khí: laser 100 kW) |
| Thay đổi chi tiết | iron_beam | Vũ khí: laser 100 kW | already | the data already holds it |
| Thay đổi chi tiết | long_sam | Giá | already | the data already holds it |
| Vũ khí đề xuất | patriot | weapon | already | as the sheet (for missile_battery: Vũ khí: Patriot PAC-2) |
| Thay đổi chi tiết | missile_battery | Vũ khí: Patriot PAC-2 | already | the data already holds it |
| Vũ khí đề xuất | turret_gmlrs | weapon | already | as the sheet (for rocket_turret.guided: Vũ khí: GMLRS dẫn đường) |
| Thay đổi chi tiết | rocket_turret.guided | Vũ khí: GMLRS dẫn đường | already | the data already holds it |
| Thay đổi chi tiết | sam_launcher | Giá | already | the data already holds it |
| Vũ khí đề xuất | buk_launcher | weapon | already | as the sheet (for sam_launcher: Vũ khí: 9M317 Buk) |
| Thay đổi chi tiết | sam_launcher | Vũ khí: 9M317 Buk | already | the data already holds it |
| Thay đổi chi tiết | scout_heli | Giá | already | the data already holds it |
| Vũ khí đề xuất | scout_rockets | weapon | already | as the sheet (for scout_heli: Vũ khí: Hydra 70) |
| Thay đổi chi tiết | scout_heli | Vũ khí: Hydra 70 | already | the data already holds it |
| Thay đổi chi tiết | scout_jeep | Tầm nhìn | already | the data already holds it |
| Thay đổi chi tiết | scout_jeep | Hành vi | already | the data already holds it |
| Thay đổi chi tiết | scylla | Vũ khí, máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | silver_bug | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | silver_bug | Vũ khí | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | stealth_fighter | Giá (CP) | already | the data already holds it |
| Thay đổi chi tiết | strike_drone | Giá | already | the data already holds it |
| Vũ khí đề xuất | jassm | weapon | already | as the sheet (for swarm_carrier: Vũ khí: thêm Rapid Dragon) |
| Đơn vị – vũ khí | swarm_carrier | guided_bomb | already | not mounted |
| Đơn vị – vũ khí | swarm_carrier | jassm | already | mounted |
| Thay đổi chi tiết | swarm_carrier | Vũ khí: thêm Rapid Dragon | already | the data already holds it |
| Thay đổi chi tiết | swarm_carrier | Giá | already | the data already holds it |
| Thay đổi chi tiết | titan_tank | Giá (CP) | already | the data already holds it |
| Thay đổi chi tiết | wheeled_gun | Máu | already | the data already holds it |
| Vũ khí đề xuất | gun_105_wheeled | weapon | already | as the sheet (for wheeled_gun: Vũ khí: 120 mm) |
| Thay đổi chi tiết | wheeled_gun | Vũ khí: 120 mm | already | the data already holds it |
| Vũ khí đề xuất | zu23 | weapon | already | as the sheet (for zu23_technical: Vũ khí: ZU-23-2) |
| Thay đổi chi tiết | zu23_technical | Vũ khí: ZU-23-2 | already | the data already holds it |

<!-- /step:A1-Cao -->

<!-- step:A1-Trung -->
## A1 Trung: sheet Thay đổi chi tiết

| Sheet | Applied | Already so | Deferred | Skipped |
|---|---|---|---|---|
| Thay đổi chi tiết | 1 | 59 | 27 | 1 |
| Vũ khí đề xuất | 0 | 24 | 0 | 0 |
| Đơn vị – vũ khí | 0 | 1 | 0 | 0 |

| Sheet | id | Item | Outcome | Detail |
|---|---|---|---|---|
| Thay đổi chi tiết | aa_turret.sam | Tham khảo | already | the data already holds it |
| Vũ khí đề xuất | sam | weapon | already | as the sheet (for aa_vehicle: Vũ khí: Stinger) |
| Thay đổi chi tiết | aa_vehicle | Vũ khí: Stinger | already | the data already holds it |
| Thay đổi chi tiết | aa_vehicle | Giáp (T/H/S/N) | already | the data already holds it |
| Thay đổi chi tiết | argus | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | armored_bulldozer | Tốc độ | already | the data already holds it |
| Thay đổi chi tiết | armored_train | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | artillery | Giáp (T/H/S/N) | already | the data already holds it |
| Vũ khí đề xuất | mortar_240_fixed | weapon | already | as the sheet (for artillery_emplacement.mortar: Vũ khí: cối 240 mm) |
| Thay đổi chi tiết | artillery_emplacement.mortar | Vũ khí: cối 240 mm | already | the data already holds it |
| Vũ khí đề xuất | hellfire_standoff | weapon | already | as the sheet (for attack_helicopter: Vũ khí: Hellfire, Stinger ATAS) |
| Vũ khí đề xuất | stinger_atas | weapon | already | as the sheet (for attack_helicopter: Vũ khí: Hellfire, Stinger ATAS) |
| Thay đổi chi tiết | attack_helicopter | Vũ khí: Hellfire, Stinger ATAS | already | the data already holds it |
| Vũ khí đề xuất | jet_cannon | weapon | already | as the sheet (for attack_jet: Vũ khí: GSh-30-2) |
| Thay đổi chi tiết | attack_jet | Vũ khí: GSh-30-2 | already | the data already holds it |
| Vũ khí đề xuất | ballistic_missile | weapon | already | as the sheet (for ballistic_launcher: Vũ khí: Iskander) |
| Thay đổi chi tiết | ballistic_launcher | Vũ khí: Iskander | already | the data already holds it |
| Thay đổi chi tiết | bastion_mk0 | Máu, giáp | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | behemoth | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | behemoth_mk2 | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | behemoth_tempest | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Vũ khí đề xuất | twin_30_bmpt | weapon | already | as the sheet (for bmpt: Vũ khí: 2A42 đôi) |
| Thay đổi chi tiết | bmpt | Vũ khí: 2A42 đôi | already | the data already holds it |
| Vũ khí đề xuất | agl_40 | weapon | already | as the sheet (for bmpt: Vũ khí: Mk 19 40 mm) |
| Thay đổi chi tiết | bmpt | Vũ khí: Mk 19 40 mm | already | the data already holds it |
| Vũ khí đề xuất | c_ram_gatling | weapon | already | as the sheet (for c_ram: Vũ khí: Phalanx 20 mm) |
| Thay đổi chi tiết | c_ram | Vũ khí: Phalanx 20 mm | already | the data already holds it |
| Thay đổi chi tiết | caspian | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | command_airship | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | command_vehicle | Giáp (T/H/S/N) | already | the data already holds it |
| Thay đổi chi tiết | daedalus | Kích thước | deferred | model size: task B1 |
| Thay đổi chi tiết | engineer_vehicle | Giáp (T/H/S/N) | already | the data already holds it |
| Thay đổi chi tiết | flame_tank | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | fortress_bastion | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | fortress_hive | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Vũ khí đề xuất | turret_gun_120_long | weapon | already | as the sheet (for gun_turret.long: Vũ khí: 120 mm L/55) |
| Thay đổi chi tiết | gun_turret.long | Vũ khí: 120 mm L/55 | applied | choice: penetration +1 (the weapon row's 'xuyên đề xuất' 5), not a first-shot bonus |
| Thay đổi chi tiết | gunship_heli | Giáp, máu | already | the data already holds it |
| Vũ khí đề xuất | heli_atgm | weapon | already | as the sheet (for gunship_heli: Vũ khí: tên lửa chống tăng) |
| Đơn vị – vũ khí | gunship_heli | heli_atgm | already | Hellfire -> 9M120 Ataka |
| Thay đổi chi tiết | gunship_heli | Vũ khí: tên lửa chống tăng | already | the data already holds it |
| Thay đổi chi tiết | gunship_heli | Tốc độ | already | the data already holds it |
| Thay đổi chi tiết | heavy_aa | Giá | already | the data already holds it |
| Vũ khí đề xuất | air_cruise_missile | weapon | already | as the sheet (for heavy_bomber: Vũ khí: Kh-101) |
| Thay đổi chi tiết | heavy_bomber | Vũ khí: Kh-101 | already | the data already holds it |
| Vũ khí đề xuất | bomber_payload | weapon | already | as the sheet (for heavy_bomber: Vũ khí: FAB-500) |
| Thay đổi chi tiết | heavy_bomber | Vũ khí: FAB-500 | already | the data already holds it |
| Thay đổi chi tiết | heavy_tank | Tham khảo, giá | already | the data already holds it |
| Thay đổi chi tiết | heavy_tank | Tốc độ xoay thân / tháp | already | the data already holds it |
| Thay đổi chi tiết | heavy_turret | Vũ khí: 155 mm đôi | skipped | gun_155_twin_fort is not on heavy_turret |
| Thay đổi chi tiết | heavy_turret | Vũ khí: 155 mm đôi | already | the data already holds it |
| Thay đổi chi tiết | icarus_mk0 | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Vũ khí đề xuất | ifv_30 | weapon | already | as the sheet (for ifv: Vũ khí: 2A42 30 mm) |
| Thay đổi chi tiết | ifv | Vũ khí: 2A42 30 mm | already | the data already holds it |
| Vũ khí đề xuất | atgm | weapon | already | as the sheet (for ifv: Vũ khí: TOW-2) |
| Thay đổi chi tiết | ifv | Vũ khí: TOW-2 | already | the data already holds it |
| Thay đổi chi tiết | ifv | Tốc độ | already | the data already holds it |
| Thay đổi chi tiết | ixion | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | kronos | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | landing_hovercraft | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | laser_tank | Giá, tăng dần | already | the data already holds it |
| Thay đổi chi tiết | laser_tank | Giáp (T/H/S/N) | already | the data already holds it |
| Vũ khí đề xuất | leviathan_460 | weapon | already | as the sheet (for leviathan: Vũ khí: 460 mm) |
| Thay đổi chi tiết | leviathan | Vũ khí: 460 mm | already | the data already holds it |
| Thay đổi chi tiết | locust | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Vũ khí đề xuất | sam_48n6 | weapon | already | as the sheet (for long_sam: Vũ khí: 48N6) |
| Thay đổi chi tiết | long_sam | Vũ khí: 48N6 | already | the data already holds it |
| Thay đổi chi tiết | main_battle_tank | Giáp (T/H/S/N) | already | the data already holds it |
| Thay đổi chi tiết | main_battle_tank | Tốc độ | already | the data already holds it |
| Thay đổi chi tiết | main_battle_tank | Tốc độ xoay thân / tháp | already | the data already holds it |
| Thay đổi chi tiết | mine_layer | Giáp (T/H/S/N) | already | the data already holds it |
| Vũ khí đề xuất | sam_battery_lrr | weapon | already | as the sheet (for missile_battery.lrr: Vũ khí) |
| Thay đổi chi tiết | missile_battery.lrr | Vũ khí | already | the data already holds it |
| Vũ khí đề xuất | sam_pac3 | weapon | already | as the sheet (for missile_battery.pac3: Vũ khí: PAC-3) |
| Thay đổi chi tiết | missile_battery.pac3 | Vũ khí: PAC-3 | already | the data already holds it |
| Thay đổi chi tiết | mlrs | Hành vi | already | the data already holds it |
| Thay đổi chi tiết | mlrs | Giá | already | the data already holds it |
| Thay đổi chi tiết | mortar_carrier | Giáp (T/H/S/N) | already | the data already holds it |
| Thay đổi chi tiết | nuke_train | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | rail_supergun | Dữ liệu vũ khí | deferred | a boss's main weapon as data: task C2 |
| Thay đổi chi tiết | rail_supergun | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | recon_drone | Tốc độ | already | the data already holds it |
| Thay đổi chi tiết | sam_launcher | Máu | already | the data already holds it |
| Thay đổi chi tiết | sam_launcher | Giáp (T/H/S/N) | already | the data already holds it |
| Thay đổi chi tiết | scout_jeep | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | siege_tank | Giáp (T/H/S/N) | already | the data already holds it |
| Thay đổi chi tiết | silver_bug | Kích thước | deferred | model size: task B1 |
| Thay đổi chi tiết | sky_fortress | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | smoke_carrier | Vũ khí: M2 12,7 mm | already | it carries hmg_selfdef_15 (15 m, the engineer's) already; the sheet's 22 m is out of date |
| Thay đổi chi tiết | smoke_carrier | Giáp (T/H/S/N) | already | the data already holds it |
| Thay đổi chi tiết | stealth_bomber | Giá | already | the data already holds it |
| Vũ khí đề xuất | jassm | weapon | already | as the sheet (for stealth_bomber: Vũ khí: JASSM) |
| Thay đổi chi tiết | stealth_bomber | Vũ khí: JASSM | already | the data already holds it |
| Vũ khí đề xuất | air_to_air | weapon | already | as the sheet (for stealth_fighter: Vũ khí và giá) |
| Thay đổi chi tiết | stealth_fighter | Vũ khí và giá | already | the data already holds it |
| Thay đổi chi tiết | stealth_fighter | Tốc độ | already | the data already holds it |
| Thay đổi chi tiết | supply_truck | Tốc độ | already | the data already holds it |
| Thay đổi chi tiết | supreme_command | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | swarm_carrier | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | tank_destroyer | Giáp | already | the data already holds it |
| Vũ khí đề xuất | gun_105_long | weapon | already | as the sheet (for tank_destroyer: Tầm, nhịp, giá) |
| Thay đổi chi tiết | tank_destroyer | Tầm, nhịp, giá | already | the data already holds it |
| Thay đổi chi tiết | titan_tank | Tốc độ, giá | already | the data already holds it |
| Thay đổi chi tiết | titan_tank | Tốc độ xoay thân / tháp | already | the data already holds it |
| Thay đổi chi tiết | turtle_tank | Giáp (T/H/S/N) | already | the data already holds it |
| Thay đổi chi tiết | twin_tank | Tốc độ xoay thân / tháp | already | the data already holds it |
| Thay đổi chi tiết | typhon | Vũ khí | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | typhon | Máu | deferred | boss health and weapons: task C1 (sheet Boss đề xuất) |
| Thay đổi chi tiết | vbied | Giáp | already | the data already holds it |
| Vũ khí đề xuất | detonator | weapon | already | as the sheet (for vbied: Máu, nổ lan) |
| Thay đổi chi tiết | vbied | Máu, nổ lan | already | the data already holds it |
| Vũ khí đề xuất | aim9 | weapon | already | as the sheet (for wingman_drone: Vũ khí: AIM-9) |
| Thay đổi chi tiết | wingman_drone | Vũ khí: AIM-9 | already | the data already holds it |

<!-- /step:A1-Trung -->

<!-- step:A1-Thap -->
## A1 Thấp: sheet Thay đổi chi tiết

| Sheet | Applied | Already so | Deferred | Skipped |
|---|---|---|---|---|
| Thay đổi chi tiết | 1 | 33 | 58 | 0 |
| Vũ khí đề xuất | 0 | 9 | 0 | 0 |

| Sheet | id | Item | Outcome | Detail |
|---|---|---|---|---|
| Thay đổi chi tiết | aa_vehicle | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | ammo_depot | Nổ khi bị phá | already | the data already holds it |
| Thay đổi chi tiết | armored_car | Tầm nhìn | already | the data already holds it |
| Thay đổi chi tiết | armored_car | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | armored_car | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | armored_train | Giáp | already | the data already holds it |
| Thay đổi chi tiết | armored_train | Giáp | already | the data already holds it |
| Thay đổi chi tiết | artillery | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | artillery | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | artillery | Nổ khi bị phá (bán kính) | already | the data already holds it |
| Thay đổi chi tiết | attack_helicopter | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | ballistic_launcher | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | bastion_mk0 | Giáp | already | the data already holds it |
| Thay đổi chi tiết | behemoth_inferno | Giáp | already | the data already holds it |
| Thay đổi chi tiết | behemoth_mk2 | Giáp | already | the data already holds it |
| Thay đổi chi tiết | behemoth_tempest | Giáp | already | the data already holds it |
| Vũ khí đề xuất | ataka | weapon | already | as the sheet (for bmpt: Vũ khí: 9M120 Ataka) |
| Thay đổi chi tiết | bmpt | Vũ khí: 9M120 Ataka | already | the data already holds it |
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
| Thay đổi chi tiết | fenrir | Giáp | already | the data already holds it |
| Thay đổi chi tiết | fenrir | Giáp | already | the data already holds it |
| Thay đổi chi tiết | fighter_jet | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Vũ khí đề xuất | flamethrower | weapon | already | as the sheet (for flame_tank: Vũ khí: súng phun lửa) |
| Thay đổi chi tiết | flame_tank | Vũ khí: súng phun lửa | already | the data already holds it |
| Thay đổi chi tiết | flame_tank | Nổ khi bị phá (bán kính) | already | the data already holds it |
| Thay đổi chi tiết | fpv_carrier | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | gunship_heli | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Vũ khí đề xuất | twin_30_flak | weapon | already | as the sheet (for heavy_aa: Vũ khí: 2A38 30 mm đôi) |
| Thay đổi chi tiết | heavy_aa | Vũ khí: 2A38 30 mm đôi | already | the data already holds it |
| Thay đổi chi tiết | heavy_aa | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | heavy_aa | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | heavy_bomber | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Vũ khí đề xuất | rockets_300mm | weapon | already | as the sheet (for heavy_rocket_artillery: Vũ khí: Smerch 300 mm) |
| Thay đổi chi tiết | heavy_rocket_artillery | Vũ khí: Smerch 300 mm | already | the data already holds it |
| Thay đổi chi tiết | heavy_rocket_artillery | Giá | already | the data already holds it |
| Thay đổi chi tiết | heavy_turret | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Vũ khí đề xuất | hover_ciws | weapon | already | as the sheet (for hover_gunboat: Vũ khí: AK-630 30 mm) |
| Thay đổi chi tiết | hover_gunboat | Vũ khí: AK-630 30 mm | already | the data already holds it |
| Thay đổi chi tiết | hover_gunboat | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | hover_gunboat | Nổ khi bị phá (bán kính) | already | the data already holds it |
| Thay đổi chi tiết | iron_beam | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | iron_beam | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | kronos | Dữ liệu vũ khí | deferred | a boss's main weapon as data: task C2 |
| Thay đổi chi tiết | lancet_truck | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | lancet_truck | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | lancet_truck | Nổ khi bị phá (bán kính) | already | the data already holds it |
| Thay đổi chi tiết | laser_tank | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Vũ khí đề xuất | gun_57mm | weapon | already | as the sheet (for light_tank: Vũ khí: 57 mm) |
| Thay đổi chi tiết | light_tank | Vũ khí: 57 mm | already | the data already holds it |
| Thay đổi chi tiết | light_tank | Tầm nhìn | already | the data already holds it |
| Thay đổi chi tiết | light_tank | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | long_sam | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | missile_battery | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | mlrs | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | morrigan | Tham khảo | already | the data already holds it |
| Vũ khí đề xuất | mortar_120 | weapon | already | as the sheet (for mortar_carrier: Vũ khí: cối 120 mm) |
| Thay đổi chi tiết | mortar_carrier | Vũ khí: cối 120 mm | already | the data already holds it |
| Thay đổi chi tiết | mortar_carrier | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | mortar_carrier | Nổ khi bị phá (bán kính) | already | the data already holds it |
| Thay đổi chi tiết | railgun_truck | Giá | already | the data already holds it |
| Thay đổi chi tiết | railgun_truck | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Vũ khí đề xuất | turret_rockets | weapon | already | as the sheet (for rocket_turret: Vũ khí: Grad) |
| Thay đổi chi tiết | rocket_turret | Vũ khí: Grad | applied | choice: +15 % damage (the weapon row's 66 a rocket), not the shorter reload |
| Thay đổi chi tiết | sam_launcher | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | scout_heli | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | scout_jeep | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | scylla | Giáp | already | the data already holds it |
| Vũ khí đề xuất | shahed | weapon | already | as the sheet (for shahed_truck: Vũ khí: Shahed-136) |
| Thay đổi chi tiết | shahed_truck | Vũ khí: Shahed-136 | already | the data already holds it |
| Thay đổi chi tiết | shahed_truck | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | shahed_truck | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | siege_tank | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | siege_tank | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | sky_gunship | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | smoke_carrier | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | spawn_bastion | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | stealth_bomber | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | stealth_fighter | Nổ khi bị phá (bán kính) | already | the data already holds it |
| Thay đổi chi tiết | supply_truck | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | supply_truck | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | supreme_command | Giáp | already | the data already holds it |
| Thay đổi chi tiết | tank_destroyer | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | thermobaric_launcher | Giá | already | the data already holds it |
| Thay đổi chi tiết | thermobaric_launcher | Nổ khi bị phá (bán kính) | already | the data already holds it |
| Thay đổi chi tiết | titan_tank | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | titan_tank | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | titan_tank | Nổ khi bị phá (bán kính) | already | the data already holds it |
| Thay đổi chi tiết | turtle_tank | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | twin_tank | Kích thước model (dài × rộng × cao) | deferred | model size: task B1 |
| Thay đổi chi tiết | vbied | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | wheeled_gun | Tên | deferred | name: task D1 (sheet Tên đề xuất) |
| Thay đổi chi tiết | zu23_technical | Tên | deferred | name: task D1 (sheet Tên đề xuất) |

<!-- /step:A1-Thap -->
