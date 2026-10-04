# Armour / Penetration 5, 04/10 (lane A): report

Branch `feature/pen5-splash` (worktree MachineBrigade-art). Source: `Docs/prompts/armour_pen5_vi.md` (sections 1-14).
Decisions: `Docs/DECISIONS.md` "Armour/Pen 5 and splash/overpen 04/10 (lane A)"; old -> new log: `Docs/export/CHANGES.md`
"ARMOUR PEN 5". No Unity run. Tests: skipped at the owner's word ("không cần test", 04/10); none written, none run.
Compile check: `dotnet build Tools/simbuild/Sim.csproj` OK (0 errors; bin / obj / Temp/simbuild deleted after).

## 1. Unit / weapon, old -> new

Player vehicles, armour front / side / rear / top:

| unit | old | new |
|---|---|---|
| titan_tank | 4 / 3 / 2 / 2 (data `4`) | **5** / 3 / 2 / 2 (data `[5, 3, 2, 2]`) |
| elite_heavy_tank | 4 / 3 / 2 / 2 (data `4`) | **5** / 3 / 2 / 2 (data `[5, 3, 2, 2]`) |
| mara_behemoth | 4 / 3 / 3 / 2 | **5** / 3 / 3 / 2 |

A single `5` in the data would expand to 5 / 4 / 3 / 3 (`ArmourLevels.Vehicle`), so the two scalar entries became four-value lists.
KEEP checked: main_battle_tank 4/2/1/1, heavy_tank 4/3/2/2, next_gen_tank 4/2/1/1, elite_mbt 4/2/1/1, elite_tank_destroyer 4/2/1/1. No player vehicle is 5/5/5/5.

Penetration 4 -> 5 (each id carries its own `pen`; nothing else inherits it):

| weapon | old | new | inherits |
|---|---:|---:|---|
| railgun | 4 | 5 | - |
| gun_140_twin | 4 | 5 | child gun_140_twin_he has its own pen 2 (unchanged) |
| gun_152 | 4 | 5 | - |
| gun_152_heat | 4 | 5 | child gun_152_heat_he own pen 3 |
| gun_125_elite | 4 | 5 | child gun_125_elite_he own pen 2 |
| gun_105_apfsds | 4 | 5 | child gun_105_apfsds_he own pen 2 |
| gun_125_armata_ke | 4 | 5 | - |
| gun_155_twin_ap (heavy_turret / heavy_turret.bastion) | 4 | 5 | inherits gun_155_twin_fort, own pen: set on this id only |
| boss_railgun | 4 | 5 | - |
| p26_ixion_125 | 4 | 5 | inherits gun_120mm, own pen: set on this id only (gun_120mm stays 4); child p26_ixion_125_he own pen 3 |
| train_gun | 4 | 5 | child train_gun_he own pen 2 |
| borer_drill | 4 | 5 | - |

turret_gun_120_long: 5, kept. Damage, reload and range of every weapon above: unchanged.

Existing boss pen 5, confirmed (actual value 5 for all ten, inherited from their `p26_*` parent): p26_bastion_direct_b100,
p26_behemoth_direct_be120, p26_behemoth_tiny_be120, p26_jotunn_direct_jo125, p26_leviathan_direct_lev127,
p26_matriarch_direct_ma_atgm, p26_moloch_direct_mo120ap, p26_nemesis_direct_ne125, p26_roc_direct_roc_atgm,
p26_icarus_main_ic_coil. None differed, so nothing was set.

KEEP pen 4, confirmed: gun_120mm, gun_120_twin, gun_105_long, gun_105_wheeled, atgm, hellfire_standoff, hellfire_volley,
drone_missile, kh29, cruise_missile_ground, stealth_payload, ballistic_missile, siege_mortar_240 (player);
p26_leviathan_lev406, p26_bastion_sec_b240, p26_jotunn_jo203, p26_moloch_main_mo120, locust_drones, p26_matriarch_ma_drones,
p26_roc_main_roc_bombs (boss); no boss Energy weapon touched.

Pen 5 after the change (whole catalogue): the 12 ids above, turret_gun_120_long, the 10 confirmed boss directs and their
`p26_*` parents, p26_behemoth_tiny_kornet_twin (already 5). No other 4 -> 5.

## 2. Canonical files changed

- `Assets/MachineBrigade/Resources/Data/balance.json`: the 3 vehicles and 12 weapons above (15 lines).
- `Scripts/Sim/Content/Armour.cs`: new `ArmourLevels.CapFor(boss, structure, face)`: a boss any face to 5, a vehicle's front to 5, every other face and every tower / building to 4.
- `Scripts/Sim/Content/Catalog.cs`: the load check uses it (it used to refuse any 5 on a non-boss); still refuses a 5 on a tower, a building, or a vehicle's side / rear / roof.
- `Scripts/Sim/Entities/Vehicle.cs` `ArmourOn`: the gear cap is max(4, the face's data level) for a non-boss, so armour gear never lifts a face to 5 and a data 5 front stays 5 (it would have been cut to 4).
- UI: `Game/Hud/CombatIcons.cs` (penetration names to 5), `Strings.cs` (new `pen.level.5` "Heavy anti-armour penetration" / "Xuyên giáp hạng nặng"), `Kit/KitCombat.cs` (deck cover cells 0-5), `BaseText.cs` `hb.pen.faces` (who reaches level 5).
- Exporter / doc generators: `Tools/docs/prompt32.py` (handbook text), `Tools/docs/build_doc.py` (section 10 text).
- `Tests/EditMode/ExportGameDoc.cs`: its armour-range assertion (it runs inside the Unity export) now uses `CapFor`; `ArmourTests.cs` and `PlayTest6BossTests.cs`: the same one-line range checks, so the shipped data does not trip them (no new tests).

## 3. Generated files regenerated

`python Tools/export/export.py check --game-json Docs/export/game_snapshot.json` (writes the pack, then checks): 15 / 15 PASS
(unmapped 0, foreign keys 301 OK, formulas 285 OK, NEED_CODE_CHECK 0, identical across two processes).
- `01_chien_dau.xlsx`: `Vu_khi.xuyen`, `Vu_khi_suy_ra` armour multipliers and DPS against armour 0 / 2 / 4, aircraft; `01_chien_dau.md`: the handbook prose (who reaches level 5).
- `02_boss.xlsx` / md (unit tables, regression inputs), `03_can_cu.xlsx` (boss hit factors, tower threat shots), `04_che_do_kinh_te_ai.xlsx`, `00_index.xlsx`, `README.md`, `bulk.zip` (07 localisation gains `pen.level.5`).
- `Docs/Machine_Brigade_Design_Review.html`: the ammunition handbook section regenerated by `prompt32.ammo_handbook` and spliced in (text diff: the level-5 sentence only).

Needs the lead's Unity re-export (`ExportGameDoc`, then `export.py`), because these cells come from `game_snapshot.json`
(exported before this change): the game-measured DPS / time-to-kill (`02_boss` Boss.thoi_gian_ha_muc_tieu_s, `dpsVs`), the
game's price / power figures (`02/Xe_suy_ra.he_so_gia`, `thuong_suc_manh`) for the three tanks and every pen-5 carrier,
the snapshot's own armour / pen fields, and the design review HTML / PDF outside the handbook (section 10 and the effect
rows come from game.json; `build_doc.py` after the re-export).

## 4. Validation

- only 3 player vehicles raised to Armour 5: yes (a catalogue scan finds non-boss level 5 only on titan_tank, elite_heavy_tank, mara_behemoth; kraken and monster are bosses).
- only the listed player weapons raised to Pen 5: yes (7).
- towers: only gun_155_twin_ap raised; turret_gun_120_long kept 5.
- tower armour max remains 4: yes (40 towers / structures scanned, max 4; the loader refuses 5 on a structure).
- boss armour unchanged: yes (no boss line touched).
- boss HP unchanged: yes.
- only the 4 boss weapons newly at Pen 5: yes; the 10 existing boss Pen 5 kept (all already 5).
- no accidental mass-upgrade 4 -> 5: yes (no parent changed; every child of a changed id has its own pen).

`boss armour unchanged`
`boss HP unchanged`
`tower armour max remains 4`
`player Armour 5 only on titan_tank, elite_heavy_tank, mara_behemoth`
