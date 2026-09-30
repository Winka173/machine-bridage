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

<!-- step:A2 -->
## A2: sheets Vũ khí đề xuất and Đơn vị – vũ khí

Every row of "Vũ khí đề xuất" (the proposal columns: damage, fire mode, rate, rounds a burst or magazine, rest, reach, speed, blast, penetration), then the loadouts of "Đơn vị – vũ khí" (mounts kept 0 dropped, the new weapons). A cadence the game already fires within 3 % of the sheet's sustained DPS, in the same mode and rounds, stays as it is. Rows of "Đơn vị – vũ khí" that keep a mount without a note are counted, not listed.

| Sheet | Applied | Already so | Deferred | Skipped |
|---|---|---|---|---|
| Vũ khí đề xuất | 0 | 154 | 0 | 35 |
| Đơn vị – vũ khí | 0 | 288 | 0 | 0 |

| Sheet | id | Item | Outcome | Detail |
|---|---|---|---|---|
| Vũ khí đề xuất | aa_25_triple | weapon | already | as the sheet |
| Vũ khí đề xuất | agl_40 | weapon | already | as the sheet |
| Vũ khí đề xuất | aim9 | weapon | already | as the sheet |
| Vũ khí đề xuất | air_cruise_missile | weapon | already | as the sheet |
| Vũ khí đề xuất | air_to_air | weapon | already | as the sheet |
| Vũ khí đề xuất | airship_drones | weapon | already | as the sheet |
| Vũ khí đề xuất | airship_flak | weapon | already | as the sheet |
| Vũ khí đề xuất | ataka | weapon | already | as the sheet |
| Vũ khí đề xuất | atgm | weapon | already | as the sheet |
| Vũ khí đề xuất | autocannon_25 | weapon | already | as the sheet |
| Vũ khí đề xuất | autocannon_30 | weapon | already | as the sheet |
| Vũ khí đề xuất | autocannon_40 | weapon | already | as the sheet |
| Vũ khí đề xuất | ballistic_missile | weapon | already | as the sheet |
| Vũ khí đề xuất | bastion_gun | weapon | already | as the sheet |
| Vũ khí đề xuất | boat_rockets | weapon | already | as the sheet |
| Vũ khí đề xuất | bomber_payload | weapon | already | as the sheet |
| Vũ khí đề xuất | bomber_tail_guns | weapon | already | as the sheet |
| Vũ khí đề xuất | borer_cannon | weapon | already | as the sheet |
| Vũ khí đề xuất | borer_drill | weapon | already | as the sheet |
| Vũ khí đề xuất | boss_flak | weapon | already | as the sheet |
| Vũ khí đề xuất | boss_flamer | weapon | already | as the sheet |
| Vũ khí đề xuất | boss_heli_gun | weapon | already | as the sheet |
| Vũ khí đề xuất | boss_hmg | weapon | already | as the sheet |
| Vũ khí đề xuất | boss_howitzer | weapon | already | as the sheet |
| Vũ khí đề xuất | boss_minigun | weapon | already | as the sheet |
| Vũ khí đề xuất | boss_missiles | weapon | already | as the sheet |
| Vũ khí đề xuất | boss_mortar | weapon | already | as the sheet |
| Vũ khí đề xuất | boss_railgun | weapon | already | as the sheet |
| Vũ khí đề xuất | boss_rockets | weapon | already | as the sheet |
| Vũ khí đề xuất | boss_thermo | weapon | already | as the sheet |
| Vũ khí đề xuất | buk_launcher | weapon | already | as the sheet |
| Vũ khí đề xuất | bunker_flame | weapon | already | as the sheet |
| Vũ khí đề xuất | bunker_hmg | weapon | already | as the sheet |
| Vũ khí đề xuất | bunker_hmg_twin | weapon | already | as the sheet |
| Vũ khí đề xuất | c_ram_gatling | weapon | already | as the sheet |
| Vũ khí đề xuất | casemate_155 | weapon | already | as the sheet |
| Vũ khí đề xuất | ciws_aa | weapon | already | as the sheet |
| Vũ khí đề xuất | coilgun | weapon | already | as the sheet |
| Vũ khí đề xuất | cruiser_203 | weapon | already | as the sheet |
| Vũ khí đề xuất | detonator | weapon | already | as the sheet |
| Vũ khí đề xuất | door_gun | weapon | already | as the sheet |
| Vũ khí đề xuất | dozer_blade | weapon | already | as the sheet |
| Vũ khí đề xuất | drone_missile | weapon | already | as the sheet |
| Vũ khí đề xuất | fighter_cannon | weapon | already | as the sheet |
| Vũ khí đề xuất | flak_35 | weapon | already | as the sheet |
| Vũ khí đề xuất | flak_quad | weapon | already | as the sheet |
| Vũ khí đề xuất | flamethrower | weapon | already | as the sheet |
| Vũ khí đề xuất | focus_laser | weapon | already | as the sheet |
| Vũ khí đề xuất | fpv_hangar | weapon | already | as the sheet |
| Vũ khí đề xuất | fpv_hangar_swarm | weapon | already | as the sheet |
| Vũ khí đề xuất | fpv_swarm | weapon | already | as the sheet |
| Vũ khí đề xuất | grad_cluster | weapon | already | as the sheet |
| Vũ khí đề xuất | griffin | weapon | already | as the sheet |
| Vũ khí đề xuất | gsh30k | weapon | already | as the sheet |
| Vũ khí đề xuất | guided_bomb | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_105_apfsds | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_105_bunker | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_105_long | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_105_wheeled | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_120_twin | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_120mm | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_125_elite | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_140_twin | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_152 | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_152_he | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_152_heat | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_155_coastal | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_155_twin_coastlr | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_155_twin_fort | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_57_auto | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_57mm | weapon | already | as the sheet |
| Vũ khí đề xuất | gun_behemoth | weapon | already | as the sheet |
| Vũ khí đề xuất | gunship_105 | weapon | already | as the sheet |
| Vũ khí đề xuất | gunship_25mm | weapon | already | as the sheet |
| Vũ khí đề xuất | gunship_40mm | weapon | already | as the sheet |
| Vũ khí đề xuất | gunship_rockets | weapon | already | as the sheet |
| Vũ khí đề xuất | hel_beam | weapon | already | as the sheet |
| Vũ khí đề xuất | heli_atgm | weapon | already | as the sheet |
| Vũ khí đề xuất | heli_gun | weapon | already | as the sheet |
| Vũ khí đề xuất | heli_rockets | weapon | already | as the sheet |
| Vũ khí đề xuất | hellfire_standoff | weapon | already | as the sheet |
| Vũ khí đề xuất | hellfire_volley | weapon | already | as the sheet |
| Vũ khí đề xuất | hmg_roof | weapon | already | as the sheet |
| Vũ khí đề xuất | hmg_selfdef_15 | weapon | already | as the sheet |
| Vũ khí đề xuất | hmg_selfdef_18 | weapon | already | as the sheet |
| Vũ khí đề xuất | hmg_selfdef_21 | weapon | already | as the sheet |
| Vũ khí đề xuất | hover_ciws | weapon | already | as the sheet |
| Vũ khí đề xuất | hover_rockets | weapon | already | as the sheet |
| Vũ khí đề xuất | howitzer | weapon | already | as the sheet |
| Vũ khí đề xuất | howitzer_cb | weapon | already | as the sheet |
| Vũ khí đề xuất | howitzer_fixed | weapon | already | as the sheet |
| Vũ khí đề xuất | hq_flak | weapon | already | as the sheet |
| Vũ khí đề xuất | ifv_30 | weapon | already | as the sheet |
| Vũ khí đề xuất | jassm | weapon | already | as the sheet |
| Vũ khí đề xuất | jet_bombs | weapon | already | as the sheet |
| Vũ khí đề xuất | jet_cannon | weapon | already | as the sheet |
| Vũ khí đề xuất | kh29 | weapon | already | as the sheet |
| Vũ khí đề xuất | kornet_multi | weapon | already | as the sheet |
| Vũ khí đề xuất | kornet_top | weapon | already | as the sheet |
| Vũ khí đề xuất | kornet_twin | weapon | already | as the sheet |
| Vũ khí đề xuất | lancet | weapon | already | as the sheet |
| Vũ khí đề xuất | lancet_hangar | weapon | already | as the sheet |
| Vũ khí đề xuất | leviathan_460 | weapon | already | as the sheet |
| Vũ khí đề xuất | mg_coax | weapon | already | as the sheet |
| Vũ khí đề xuất | mg_jeep | weapon | already | as the sheet |
| Vũ khí đề xuất | mg_jeep_selfdef | weapon | already | as the sheet |
| Vũ khí đề xuất | minigun | weapon | already | as the sheet |
| Vũ khí đề xuất | mlrs_elite | weapon | already | as the sheet |
| Vũ khí đề xuất | mlrs_rockets | weapon | already | as the sheet |
| Vũ khí đề xuất | mortar_120 | weapon | already | as the sheet |
| Vũ khí đề xuất | mortar_240_fixed | weapon | already | as the sheet |
| Vũ khí đề xuất | mothership_cannon | weapon | already | as the sheet |
| Vũ khí đề xuất | mothership_drones | weapon | already | as the sheet |
| Vũ khí đề xuất | naval_100 | weapon | already | as the sheet |
| Vũ khí đề xuất | naval_155_triple | weapon | already | as the sheet |
| Vũ khí đề xuất | naval_76 | weapon | already | as the sheet |
| Vũ khí đề xuất | orbital_laser | weapon | already | as the sheet |
| Vũ khí đề xuất | patriot | weapon | already | as the sheet |
| Vũ khí đề xuất | r60 | weapon | already | as the sheet |
| Vũ khí đề xuất | railgun | weapon | already | as the sheet |
| Vũ khí đề xuất | recon_missile | weapon | already | as the sheet |
| Vũ khí đề xuất | rockets_300mm | weapon | already | as the sheet |
| Vũ khí đề xuất | s8_pods | weapon | already | as the sheet |
| Vũ khí đề xuất | sam | weapon | already | as the sheet |
| Vũ khí đề xuất | sam_48n6 | weapon | already | as the sheet |
| Vũ khí đề xuất | sam_battery | weapon | already | as the sheet |
| Vũ khí đề xuất | sam_battery_lrr | weapon | already | as the sheet |
| Vũ khí đề xuất | sam_pac3 | weapon | already | as the sheet |
| Vũ khí đề xuất | sam_post | weapon | already | as the sheet |
| Vũ khí đề xuất | scout_rockets | weapon | already | as the sheet |
| Vũ khí đề xuất | shahed | weapon | already | as the sheet |
| Vũ khí đề xuất | siege_gun_105 | weapon | already | as the sheet |
| Vũ khí đề xuất | siege_mortar_240 | weapon | already | as the sheet |
| Vũ khí đề xuất | stealth_payload | weapon | already | as the sheet |
| Vũ khí đề xuất | stinger_atas | weapon | already | as the sheet |
| Vũ khí đề xuất | swarm_drones | weapon | already | as the sheet |
| Vũ khí đề xuất | tamir | weapon | already | as the sheet |
| Vũ khí đề xuất | technical_rockets | weapon | already | as the sheet |
| Vũ khí đề xuất | thermobaric_rockets | weapon | already | as the sheet |
| Vũ khí đề xuất | tower_ac25 | weapon | already | as the sheet |
| Vũ khí đề xuất | tower_flak_30 | weapon | already | as the sheet |
| Vũ khí đề xuất | tower_hmg | weapon | already | as the sheet |
| Vũ khí đề xuất | tower_kornet | weapon | already | as the sheet |
| Vũ khí đề xuất | train_gun | weapon | already | as the sheet |
| Vũ khí đề xuất | turret_gmlrs | weapon | already | as the sheet |
| Vũ khí đề xuất | turret_gun_120 | weapon | already | as the sheet |
| Vũ khí đề xuất | turret_gun_120_long | weapon | already | as the sheet |
| Vũ khí đề xuất | turret_rockets | weapon | already | as the sheet |
| Vũ khí đề xuất | turret_rockets_cluster | weapon | already | as the sheet |
| Vũ khí đề xuất | twin_30_bmpt | weapon | already | as the sheet |
| Vũ khí đề xuất | twin_30_flak | weapon | already | as the sheet |
| Vũ khí đề xuất | twin_35_ahead | cadence | skipped | the sheet's mode, rate, rounds or rest cell is empty |
| Vũ khí đề xuất | twin_35_ahead | weapon | already | as the sheet |
| Vũ khí đề xuất | wvr_aam | weapon | already | as the sheet |
| Vũ khí đề xuất | zu23 | weapon | already | as the sheet |
| Đơn vị – vũ khí | light_tank | gun_launched_atgm | already | Thêm tên lửa bắn qua nòng (1 quả × 200, xuyên 3, mỗi 20 s, tầm 34) |
| Đơn vị – vũ khí | mlrs | hmg_selfdef_15 | already | not mounted |
| Đơn vị – vũ khí | ballistic_launcher | hmg_selfdef_15 | already | not mounted |
| Đơn vị – vũ khí | heavy_rocket_artillery | hmg_selfdef_15 | already | not mounted |
| Đơn vị – vũ khí | aa_vehicle | sam | already | the Stinger stays (Giữ Stinger phụ — Gepard bản nâng cấp có thể mang Stinger.) |
| Đơn vị – vũ khí | sam_launcher | hmg_selfdef_18 | already | not mounted |
| Đơn vị – vũ khí | heavy_aa | sam | already | Stinger -> 57E6: Đổi Stinger → tên lửa 57E6 (Pantsir): 1 × 220, Mảnh xuyên 3, tầm 55, tốc độ 55 |
| Đơn vị – vũ khí | scout_heli | loadout | already | its A1 row applied it (Hydra: 12 → 6 quả mỗi lần đầy đạn) |
| Đơn vị – vũ khí | swarm_carrier | loadout | already | its A1 row applied it (Bỏ bom SDB; thêm 2 tên lửa hành trình Rapid Dragon mỗi lượt; Vũ khí thêm theo đề xuất) |
| Đơn vị – vũ khí | stealth_fighter | loadout | already | its A1 row applied it (Thêm 1 AIM-120 mỗi lần đầy đạn) |
| Đơn vị – vũ khí | gunship_heli | loadout | already | its A1 row applied it (Đổi Hellfire → 9M120 Ataka) |
| Đơn vị – vũ khí | attack_jet | loadout | already | its A1 row applied it (FAB-250: 2 → 1 quả mỗi lần đầy đạn) |
| Đơn vị – vũ khí | wheeled_gun | hmg_roof | already | mounted |
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
