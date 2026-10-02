# GLB baseline (prompt 27 step 2)

Generated 2026-10-02 by `python Tools/assets/glb_check.py` over Assets/MachineBrigade/Resources/Models (442 GLB files). Full data: Tools/assets/baseline.json. Static analysis only (no Unity run).
Rules: DECISIONS "27 step 0 + baseline"; budgets: Docs/models/BUDGETS.md (over the soft budget a warning, over
the hard cap an error). Warnings are listed in the JSON.

## Totals per category

| category | models | triangles | avg | largest | material slots | with errors | with warnings |
|---|---:|---:|---:|---|---:|---:|---:|
| boss | 33 | 495,942 | 15,028 | rail_supergun (36,726) | 2,197 | 0 | 27 |
| ground | 95 | 413,562 | 4,353 | main_battle_tank_hd (16,462) | 2,472 | 0 | 6 |
| structure | 78 | 327,100 | 4,193 | headquarters (14,164) | 2,745 | 0 | 20 |
| prop | 115 | 238,276 | 2,071 | house_large (6,056) | 1,540 | 0 | 8 |
| unlisted | 33 | 105,160 | 3,186 | apc_hd (14,466) | 615 | 0 | 2 |
| air | 30 | 92,064 | 3,068 | fighter_jet_hd (13,856) | 542 | 0 | 15 |
| scenery | 29 | 26,976 | 930 | rubble_large (3,516) | 110 | 0 | 2 |
| wreck | 1 | 20,250 | 20,250 | silver_bug_wreck (20,250) | 123 | 0 | 1 |
| munition | 28 | 6,742 | 240 | fpv_drone (1,520) | 191 | 0 | 1 |

All files: 1,726,072 triangles, 0 with errors, 82 more with warnings only.

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
- silver_bug: runtime names with a Blender suffix: Mount_gun.001, Mount_gun.002, Mount_gun.003, Mount_mg.001

## Over budget (models per class and metric)

| class | metric | over soft (warning) | over hard (error) | over the hard cap |
|---|---|---:|---:|---|
| ground | movingParts | 2 | 0 | - |
| ground | renderers | 1 | 0 | - |
| ground | triangles | 1 | 0 | - |
| jet | triangles | 1 | 0 | - |
| jet | vertices | 1 | 0 | - |
| munition | renderers | 1 | 0 | - |
| munition | triangles | 1 | 0 | - |
| munition | vertices | 1 | 0 | - |
| scenery | renderers | 2 | 0 | - |
| structure | movingParts | 1 | 0 | - |
| tower | vertices | 1 | 0 | - |

10 models over a budget, 0 of them over a hard cap.

## Error reasons (count of models)

- none

## Flagged models (0)

