# GLB baseline (prompt 27 step 2)

Generated 2026-10-02 by `python Tools/assets/glb_check.py` over Assets/MachineBrigade/Resources/Models (406 GLB files). Full data: Tools/assets/baseline.json. Static analysis only (no Unity run).
Rules: DECISIONS "27 step 0 + baseline"; budgets: Docs/models/BUDGETS.md (over the soft budget a warning, over
the hard cap an error). Warnings are listed in the JSON.

## Totals per category

| category | models | triangles | avg | largest | material slots | with errors | with warnings |
|---|---:|---:|---:|---|---:|---:|---:|
| boss | 30 | 473,252 | 15,775 | rail_supergun (36,726) | 1,960 | 1 | 24 |
| structure | 72 | 316,328 | 4,393 | headquarters (14,260) | 2,647 | 9 | 21 |
| ground | 75 | 256,870 | 3,424 | main_battle_tank_hd (16,462) | 1,858 | 2 | 8 |
| prop | 115 | 238,276 | 2,071 | house_large (6,056) | 1,620 | 2 | 8 |
| unlisted | 33 | 105,496 | 3,196 | apc_hd (14,466) | 615 | 2 | 2 |
| air | 23 | 71,082 | 3,090 | fighter_jet_hd (13,856) | 419 | 2 | 11 |
| scenery | 29 | 26,976 | 930 | rubble_large (3,516) | 110 | 0 | 2 |
| wreck | 1 | 20,250 | 20,250 | silver_bug_wreck (20,250) | 123 | 0 | 1 |
| munition | 28 | 6,742 | 240 | fpv_drone (1,520) | 191 | 0 | 1 |

All files: 1,515,272 triangles, 18 with errors, 73 more with warnings only.

## Experiment models (DECISIONS "27 order" step 3)

| model | category | triangles | vertices | renderers | materials | slots | KiB | L x W x H (m) | COLOR_0 mean |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| main_battle_tank (MBT) | ground | 7,196 | 8,446 | 38 | 8 | 38 | 442 | 7.79 x 3.07 x 2.31 | 0.6229 |
| main_battle_tank_hd (MBT) | ground | 16,462 | 21,877 | 56 | 9 | 56 | 1090 | 7.79 x 3.07 x 2.35 | 0.5504 |
| fighter_jet (Su-27) | air | 3,948 | 5,032 | 22 | 9 | 22 | 263 | 8.64 x 5.85 x 2.15 | 0.7127 |
| fighter_jet_hd (Su-27) | air | 13,856 | 20,836 | 29 | 9 | 29 | 1006 | 8.64 x 5.85 x 2.14 | 0.6493 |
| silver_bug (Icarus) | boss | 21,760 | 29,716 | 120 | 12 | 120 | 1499 | 36.32 x 18.23 x 13.15 | 0.7421 |
| attack_helicopter (complex unit) | air | 4,362 | 5,314 | 28 | 9 | 28 | 283 | 6.35 x 4.44 x 2.02 | 0.6933 |
| attack_helicopter_hd (complex unit) | air | 6,542 | 8,718 | 36 | 9 | 36 | 450 | 6.35 x 4.44 x 2.02 | 0.6492 |

- fighter_jet_hd: triangles 13,856 over the jet hd budget 12,300; vertices 20,836 over the jet hd budget 19,200
- silver_bug: runtime names with a Blender suffix: Mount_gun.001, Mount_gun.002, Mount_gun.003, Mount_mg.001; hyperion: length 36.32 m vs modelSize 67.2 m (fitted at runtime)

## Over budget (models per class and metric)

| class | metric | over soft (warning) | over hard (error) | over the hard cap |
|---|---|---:|---:|---|
| ground | movingParts | 1 | 2 | sea_cruiser, siege_tank |
| ground | renderers | 0 | 1 | siege_tank |
| ground | triangles | 1 | 0 | - |
| ground | vertices | 1 | 0 | - |
| jet | triangles | 1 | 0 | - |
| jet | vertices | 1 | 0 | - |
| munition | renderers | 1 | 0 | - |
| munition | triangles | 1 | 0 | - |
| munition | vertices | 1 | 0 | - |
| prop | renderers | 0 | 2 | command_hq, shield_generator |
| scenery | renderers | 2 | 0 | - |
| structure | movingParts | 1 | 0 | - |
| tower | movingParts | 0 | 1 | flak_tower |
| tower | vertices | 1 | 0 | - |

13 models over a budget, 5 of them over a hard cap.

## Error reasons (count of models)

- zero-area triangles over 0.5 %: 7
- proportions off modelSize by over 25 %: 5
- over a budget hard cap: 5
- boss part node missing: 1

## Flagged models (18)

- **at_gun_emplacement** (structure): at_gun_emplacement: height/length 0.22 vs modelSize 0.34 (-37%)
- **command_hq** (prop): renderers 62 over the prop normal hard cap 58
- **flak_tower** (structure): movingParts 10 over the tower normal hard cap 9
- **headquarters** (structure): 82 zero-area triangles (0.58%)
- **heavy_flak_tower** (structure): heavy_flak_tower: height/length 0.69 vs modelSize 0.49 (+43%)
- **helipad** (structure): 96 zero-area triangles (8.51%)
- **helipad_a** (structure): 96 zero-area triangles (7.12%)
- **helipad_b** (structure): 96 zero-area triangles (4.61%)
- **interceptor_jet** (air): interceptor_jet: height/length 0.20 vs modelSize 0.27 (-26%)
- **laser_ad_station** (structure): laser_ad_station: width/length 1.12 vs modelSize 0.67 (+67%)
- **mobile_fortress** (boss): mobile_fortress: boss part 'howitzer_2' node Mount_gun not in the model; mobile_fortress: boss part 'sam' node Mount_missile.001 not in the model
- **sea_cruiser** (ground): movingParts 14 over the ground normal hard cap 10
- **shield_generator** (prop): renderers 63 over the prop normal hard cap 58
- **siege_tank** (ground): renderers 80 over the ground normal hard cap 76; movingParts 22 over the ground normal hard cap 10
- **sky_gunship_hd** (air): 202 zero-area triangles (5.37%)
- **strike_jet** (unlisted): 156 zero-area triangles (1.79%)
- **tank_buster** (unlisted): 163 zero-area triangles (1.82%)
- **visual_jammer** (structure): visual_jammer: width/length 1.16 vs modelSize 0.83 (+39%)
