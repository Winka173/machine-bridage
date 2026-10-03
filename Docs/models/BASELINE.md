# GLB baseline (prompt 27 step 2)

Generated 2026-10-03 by `python Tools/assets/glb_check.py` over Assets/MachineBrigade/Resources/Models (517 GLB files). Full data: Tools/assets/baseline.json. Static analysis only (no Unity run).
Rules: DECISIONS "27 step 0 + baseline"; budgets: Docs/models/BUDGETS.md (over the soft budget a warning, over
the hard cap an error). Warnings are listed in the JSON.

## Totals per category

| category | models | triangles | avg | largest | material slots | with errors | with warnings |
|---|---:|---:|---:|---|---:|---:|---:|
| ground | 94 | 767,706 | 8,167 | main_battle_tank_hd (16,462) | 5,252 | 1 | 47 |
| boss | 33 | 601,248 | 18,219 | monster (39,598) | 3,017 | 0 | 30 |
| structure | 86 | 458,614 | 5,332 | headquarters (21,052) | 4,018 | 0 | 18 |
| prop | 114 | 252,886 | 2,218 | command_hq (8,872) | 1,527 | 0 | 3 |
| air | 31 | 168,682 | 5,441 | airborne_light_tank_chute (16,310) | 1,169 | 0 | 24 |
| unlisted | 34 | 111,176 | 3,269 | apc_hd (14,968) | 666 | 0 | 0 |
| scenery | 96 | 40,708 | 424 | rubble_large (3,516) | 294 | 0 | 2 |
| wreck | 1 | 20,250 | 20,250 | silver_bug_wreck (20,250) | 123 | 0 | 1 |
| munition | 28 | 7,146 | 255 | fpv_drone (1,564) | 210 | 0 | 1 |

All files: 2,428,416 triangles, 1 with errors, 125 more with warnings only.

## Experiment models (DECISIONS "27 order" step 3)

| model | category | triangles | vertices | renderers | materials | slots | KiB | L x W x H (m) | COLOR_0 mean |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| main_battle_tank (MBT) | ground | 7,196 | 8,446 | 38 | 8 | 38 | 345 | 7.79 x 3.07 x 2.31 | 0.6229 |
| main_battle_tank_hd (MBT) | ground | 16,462 | 21,877 | 56 | 9 | 56 | 837 | 7.79 x 3.07 x 2.35 | 0.5504 |
| fighter_jet (Su-27) | air | 4,308 | 5,571 | 40 | 9 | 40 | 243 | 8.64 x 5.85 x 2.15 | 0.7461 |
| fighter_jet_hd (Su-27) | air | 14,216 | 21,233 | 51 | 9 | 51 | 802 | 8.64 x 5.85 x 2.14 | 0.7036 |
| silver_bug (Icarus) | boss | 21,760 | 29,716 | 120 | 12 | 120 | 1158 | 36.32 x 18.23 x 13.15 | 0.7421 |
| attack_helicopter (complex unit) | air | 4,722 | 5,896 | 30 | 9 | 30 | 245 | 6.35 x 4.44 x 2.02 | 0.7192 |
| attack_helicopter_hd (complex unit) | air | 6,902 | 9,300 | 38 | 9 | 38 | 372 | 6.35 x 4.44 x 2.02 | 0.6856 |

- fighter_jet: renderers 40 over the jet normal budget 36
- fighter_jet_hd: triangles 14,216 over the jet hd budget 12,300; vertices 21,233 over the jet hd budget 19,200; renderers 51 over the jet hd budget 49
- silver_bug: runtime names with a Blender suffix: Mount_gun.001, Mount_gun.002, Mount_gun.003, Mount_mg.001

## Over budget (models per class and metric)

| class | metric | over soft (warning) | over hard (error) | over the hard cap |
|---|---|---:|---:|---|
| boss_s | triangles | 1 | 0 | - |
| boss_s | vertices | 2 | 0 | - |
| ground | movingParts | 2 | 0 | - |
| ground | renderers | 15 | 1 | fpv_carrier |
| ground | triangles | 35 | 0 | - |
| ground | vertices | 42 | 0 | - |
| helicopter | renderers | 3 | 0 | - |
| helicopter | triangles | 1 | 0 | - |
| helicopter | vertices | 1 | 0 | - |
| jet | renderers | 14 | 0 | - |
| jet | triangles | 6 | 0 | - |
| jet | vertices | 5 | 0 | - |
| munition | renderers | 1 | 0 | - |
| munition | triangles | 1 | 0 | - |
| munition | vertices | 1 | 0 | - |
| prop | renderers | 1 | 0 | - |
| prop | triangles | 1 | 0 | - |
| prop | vertices | 1 | 0 | - |
| scenery | renderers | 2 | 0 | - |
| structure | movingParts | 1 | 0 | - |
| structure | renderers | 10 | 0 | - |
| structure | triangles | 1 | 0 | - |
| structure | vertices | 1 | 0 | - |
| tower | triangles | 1 | 0 | - |
| tower | vertices | 1 | 0 | - |

83 models over a budget, 1 of them over a hard cap.

## Error reasons (count of models)

- over a budget hard cap: 1

## Flagged models (1)

- **fpv_carrier** (ground): renderers 78 over the ground normal hard cap 76
