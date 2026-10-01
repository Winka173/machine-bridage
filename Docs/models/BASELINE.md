# GLB baseline (prompt 27 step 2)

Generated 2026-10-02 by `python Tools/assets/glb_check.py` over Assets/MachineBrigade/Resources/Models (400 GLB files). Full data: Tools/assets/baseline.json. Static analysis only (no Unity run).
Rules: DECISIONS "27 step 0 + baseline". No numeric budgets yet (they come with the budgets document), so
only hard errors are flagged; warnings are listed in the JSON.

## Totals per category

| category | models | triangles | avg | largest | material slots | with errors | with warnings |
|---|---:|---:|---:|---|---:|---:|---:|
| boss | 24 | 398,064 | 16,586 | nuke_train (35,666) | 1,622 | 1 | 20 |
| structure | 72 | 316,328 | 4,393 | headquarters (14,260) | 2,647 | 8 | 20 |
| ground | 75 | 256,870 | 3,424 | main_battle_tank_hd (16,462) | 1,858 | 0 | 7 |
| prop | 115 | 238,276 | 2,071 | house_large (6,056) | 1,620 | 0 | 8 |
| unlisted | 33 | 127,724 | 3,870 | ixion (21,628) | 668 | 2 | 2 |
| air | 23 | 71,082 | 3,090 | fighter_jet_hd (13,856) | 419 | 2 | 10 |
| scenery | 29 | 26,976 | 930 | rubble_large (3,516) | 110 | 0 | 0 |
| wreck | 1 | 20,250 | 20,250 | silver_bug_wreck (20,250) | 123 | 0 | 1 |
| munition | 28 | 6,742 | 240 | fpv_drone (1,520) | 191 | 0 | 0 |

All files: 1,462,312 triangles, 13 with errors, 64 more with warnings only.

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

- silver_bug: runtime names with a Blender suffix: Mount_gun.001, Mount_gun.002, Mount_gun.003, Mount_mg.001; hyperion: length 36.32 m vs modelSize 67.2 m (fitted at runtime)

## Error reasons (count of models)

- zero-area triangles over 0.5 %: 7
- proportions off modelSize by over 25 %: 5
- boss part node missing: 1

## Flagged models (13)

- **at_gun_emplacement** (structure): at_gun_emplacement: height/length 0.22 vs modelSize 0.34 (-37%)
- **headquarters** (structure): 82 zero-area triangles (0.58%)
- **heavy_flak_tower** (structure): heavy_flak_tower: height/length 0.69 vs modelSize 0.49 (+43%)
- **helipad** (structure): 96 zero-area triangles (8.51%)
- **helipad_a** (structure): 96 zero-area triangles (7.12%)
- **helipad_b** (structure): 96 zero-area triangles (4.61%)
- **interceptor_jet** (air): interceptor_jet: height/length 0.20 vs modelSize 0.27 (-26%)
- **laser_ad_station** (structure): laser_ad_station: width/length 1.12 vs modelSize 0.67 (+67%)
- **mobile_fortress** (boss): mobile_fortress: boss part 'howitzer_2' node Mount_gun not in the model; mobile_fortress: boss part 'sam' node Mount_missile.001 not in the model; fenrir: boss part 'howitzer_2' node Mount_gun not in the model; fenrir: boss part 'sam' node Mount_missile.001 not in the model
- **sky_gunship_hd** (air): 202 zero-area triangles (5.37%)
- **strike_jet** (unlisted): 156 zero-area triangles (1.79%)
- **tank_buster** (unlisted): 163 zero-area triangles (1.82%)
- **visual_jammer** (structure): visual_jammer: width/length 1.16 vs modelSize 0.83 (+39%)
