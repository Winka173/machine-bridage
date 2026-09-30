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
| Thay đổi chi tiết | 27 | 0 | 6 | 0 |
| Vũ khí đề xuất | 14 | 1 | 0 | 0 |
| Đơn vị – vũ khí | 2 | 0 | 0 | 0 |

| Sheet | id | Item | Outcome | Detail |
|---|---|---|---|---|
| Vũ khí đề xuất | tower_flak_30 | weapon | applied | damage 7, cooldown 0.0286, clip 120, clipReload 3.0286 (for aa_turret: Vũ khí và tham khảo) |
| Thay đổi chi tiết | aa_turret | Vũ khí và tham khảo | applied | reference (unit_refs.json); tower_flak_30: damage 7, cooldown 0.0286, clip 120, clipReload 3.0286; choice: the reference moves to the 2A38 (the weapon is kept); the anti-aircraft value falls through the tower flak's new rate (tower_flak_30's row) |
| Vũ khí đề xuất | howitzer | weapon | applied | cooldown 7.1429 (for artillery: Vũ khí: lựu pháo 155 mm) |
| Thay đổi chi tiết | artillery | Vũ khí: lựu pháo 155 mm | applied | howitzer: cooldown 7.1429 |
| Thay đổi chi tiết | artillery | Model và tham khảo | deferred | model and reference follow the model change: task B2 (the armour and speed are its Trung rows) |
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
