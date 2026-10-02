# GLB baseline (prompt 27 step 2)

Generated 2026-10-02 by `python Tools/assets/glb_check.py` over Assets/MachineBrigade/Resources/Models (442 GLB files). Full data: Tools/assets/baseline.json. Static analysis only (no Unity run).
Rules: DECISIONS "27 step 0 + baseline"; budgets: Docs/models/BUDGETS.md (over the soft budget a warning, over
the hard cap an error). Warnings are listed in the JSON.

## Totals per category

| category | models | triangles | avg | largest | material slots | with errors | with warnings |
|---|---:|---:|---:|---|---:|---:|---:|
| boss | 33 | 518,460 | 15,710 | rail_supergun (36,726) | 2,208 | 0 | 27 |
| ground | 95 | 413,256 | 4,350 | main_battle_tank_hd (16,462) | 2,469 | 0 | 6 |
| structure | 78 | 352,890 | 4,524 | headquarters (14,164) | 2,770 | 0 | 9 |
| prop | 115 | 237,142 | 2,062 | command_hq (5,982) | 1,540 | 0 | 8 |
| air | 30 | 107,046 | 3,568 | fighter_jet_hd (14,216) | 596 | 0 | 14 |
| unlisted | 33 | 104,344 | 3,161 | apc_hd (14,466) | 624 | 0 | 1 |
| scenery | 29 | 27,164 | 936 | rubble_large (3,516) | 112 | 0 | 2 |
| wreck | 1 | 20,250 | 20,250 | silver_bug_wreck (20,250) | 123 | 0 | 1 |
| munition | 28 | 7,102 | 253 | fpv_drone (1,520) | 210 | 0 | 1 |

All files: 1,787,654 triangles, 0 with errors, 69 more with warnings only.

## Experiment models (DECISIONS "27 order" step 3)

| model | category | triangles | vertices | renderers | materials | slots | KiB | L x W x H (m) | COLOR_0 mean |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| main_battle_tank (MBT) | ground | 7,196 | 8,446 | 38 | 8 | 38 | 442 | 7.79 x 3.07 x 2.31 | 0.6229 |
| main_battle_tank_hd (MBT) | ground | 16,462 | 21,877 | 56 | 9 | 56 | 1090 | 7.79 x 3.07 x 2.35 | 0.5504 |
| fighter_jet (Su-27) | air | 4,308 | 5,614 | 24 | 9 | 24 | 292 | 8.64 x 5.85 x 2.15 | 0.7457 |
| fighter_jet_hd (Su-27) | air | 14,216 | 21,418 | 31 | 9 | 31 | 1036 | 8.64 x 5.85 x 2.14 | 0.7033 |
| silver_bug (Icarus) | boss | 21,760 | 29,716 | 120 | 12 | 120 | 1499 | 36.32 x 18.23 x 13.15 | 0.7421 |
| attack_helicopter (complex unit) | air | 4,722 | 5,896 | 30 | 9 | 30 | 312 | 6.35 x 4.44 x 2.02 | 0.7192 |
| attack_helicopter_hd (complex unit) | air | 6,902 | 9,300 | 38 | 9 | 38 | 479 | 6.35 x 4.44 x 2.02 | 0.6856 |

- fighter_jet_hd: triangles 14,216 over the jet hd budget 12,300; vertices 21,418 over the jet hd budget 19,200
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

