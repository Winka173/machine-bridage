# GLB baseline (prompt 27 step 2)

Generated 2026-10-03 by `python Tools/assets/glb_check.py` over Assets/MachineBrigade/Resources/Models (518 GLB files). Full data: Tools/assets/baseline.json. Static analysis only (no Unity run).
Rules: DECISIONS "27 step 0 + baseline"; budgets: Docs/models/BUDGETS.md (over the soft budget a warning, over
the hard cap an error). Warnings are listed in the JSON.

## Totals per category

| category | models | triangles | avg | largest | material slots | with errors | with warnings |
|---|---:|---:|---:|---|---:|---:|---:|
| boss | 33 | 539,936 | 16,361 | rail_supergun (36,726) | 2,291 | 0 | 27 |
| ground | 95 | 431,732 | 4,544 | main_battle_tank_hd (16,462) | 2,664 | 0 | 7 |
| structure | 86 | 402,328 | 4,678 | headquarters (14,164) | 2,997 | 0 | 9 |
| prop | 115 | 253,918 | 2,207 | apartment (6,128) | 1,540 | 0 | 2 |
| air | 31 | 108,130 | 3,488 | fighter_jet_hd (14,216) | 755 | 0 | 16 |
| unlisted | 33 | 107,254 | 3,250 | apc_hd (14,968) | 628 | 0 | 0 |
| scenery | 96 | 40,708 | 424 | rubble_large (3,516) | 294 | 0 | 2 |
| wreck | 1 | 20,250 | 20,250 | silver_bug_wreck (20,250) | 123 | 0 | 1 |
| munition | 28 | 7,146 | 255 | fpv_drone (1,564) | 210 | 0 | 1 |

All files: 1,911,402 triangles, 0 with errors, 65 more with warnings only.

## Experiment models (DECISIONS "27 order" step 3)

| model | category | triangles | vertices | renderers | materials | slots | KiB | L x W x H (m) | COLOR_0 mean |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| main_battle_tank (MBT) | ground | 7,196 | 8,446 | 38 | 8 | 38 | 442 | 7.79 x 3.07 x 2.31 | 0.6229 |
| main_battle_tank_hd (MBT) | ground | 16,462 | 21,877 | 56 | 9 | 56 | 1090 | 7.79 x 3.07 x 2.35 | 0.5504 |
| fighter_jet (Su-27) | air | 4,308 | 5,571 | 40 | 9 | 40 | 305 | 8.64 x 5.85 x 2.15 | 0.7461 |
| fighter_jet_hd (Su-27) | air | 14,216 | 21,233 | 51 | 9 | 51 | 1047 | 8.64 x 5.85 x 2.14 | 0.7036 |
| silver_bug (Icarus) | boss | 21,760 | 29,716 | 120 | 12 | 120 | 1499 | 36.32 x 18.23 x 13.15 | 0.7421 |
| attack_helicopter (complex unit) | air | 4,722 | 5,896 | 30 | 9 | 30 | 312 | 6.35 x 4.44 x 2.02 | 0.7192 |
| attack_helicopter_hd (complex unit) | air | 6,902 | 9,300 | 38 | 9 | 38 | 479 | 6.35 x 4.44 x 2.02 | 0.6856 |

- fighter_jet: renderers 40 over the jet normal budget 36
- fighter_jet_hd: triangles 14,216 over the jet hd budget 12,300; vertices 21,233 over the jet hd budget 19,200; renderers 51 over the jet hd budget 49
- silver_bug: runtime names with a Blender suffix: Mount_gun.001, Mount_gun.002, Mount_gun.003, Mount_mg.001

## Over budget (models per class and metric)

| class | metric | over soft (warning) | over hard (error) | over the hard cap |
|---|---|---:|---:|---|
| boss_s | vertices | 1 | 0 | - |
| ground | movingParts | 3 | 0 | - |
| ground | renderers | 1 | 0 | - |
| ground | triangles | 1 | 0 | - |
| jet | renderers | 4 | 0 | - |
| jet | triangles | 1 | 0 | - |
| jet | vertices | 1 | 0 | - |
| munition | renderers | 1 | 0 | - |
| munition | triangles | 1 | 0 | - |
| munition | vertices | 1 | 0 | - |
| scenery | renderers | 2 | 0 | - |
| structure | movingParts | 1 | 0 | - |
| tower | vertices | 1 | 0 | - |

15 models over a budget, 0 of them over a hard cap.

## Error reasons (count of models)

- none

## Flagged models (0)

