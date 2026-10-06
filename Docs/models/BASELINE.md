# GLB baseline (prompt 27 step 2)

Generated 2026-10-06 by `python Tools/assets/glb_check.py` over Assets/MachineBrigade/Resources/Models (465 GLB files). Full data: Tools/assets/baseline.json. Static analysis only (no Unity run).
Rules: DECISIONS "27 step 0 + baseline"; budgets: Docs/models/BUDGETS.md (over the soft budget a warning, over
the hard cap an error). Warnings are listed in the JSON.

## Totals per category

| category | models | triangles | avg | largest | material slots | with errors | with warnings |
|---|---:|---:|---:|---|---:|---:|---:|
| boss | 29 | 1,141,989 | 39,378 | leviathan (86,412) | 3,905 | 0 | 14 |
| ground | 75 | 662,194 | 8,829 | main_battle_tank_hd (16,462) | 4,000 | 0 | 48 |
| structure | 71 | 412,111 | 5,804 | headquarters (21,052) | 3,618 | 0 | 10 |
| prop | 115 | 258,170 | 2,244 | command_hq (8,872) | 1,568 | 0 | 3 |
| unlisted | 34 | 108,062 | 3,178 | apc_hd (14,968) | 668 | 0 | 0 |
| air | 19 | 101,328 | 5,333 | fighter_jet_hd (14,216) | 685 | 0 | 9 |
| wreck | 1 | 69,462 | 69,462 | silver_bug_wreck (69,462) | 205 | 0 | 1 |
| scenery | 96 | 40,708 | 424 | rubble_large (3,516) | 294 | 0 | 2 |
| munition | 25 | 5,154 | 206 | bomb (404) | 175 | 0 | 0 |

All files: 2,799,178 triangles, 0 with errors, 87 more with warnings only.

## Experiment models (DECISIONS "27 order" step 3)

| model | category | triangles | vertices | renderers | materials | slots | KiB | L x W x H (m) | COLOR_0 mean |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| main_battle_tank (MBT) | ground | 7,196 | 8,446 | 38 | 8 | 38 | 345 | 7.79 x 3.07 x 2.31 | 0.6229 |
| main_battle_tank_hd (MBT) | ground | 16,462 | 21,877 | 56 | 9 | 56 | 837 | 7.79 x 3.07 x 2.35 | 0.5504 |
| fighter_jet (Su-27) | air | 4,308 | 5,571 | 40 | 9 | 40 | 243 | 8.64 x 5.85 x 2.15 | 0.7461 |
| fighter_jet_hd (Su-27) | air | 14,216 | 21,233 | 51 | 9 | 51 | 802 | 8.64 x 5.85 x 2.14 | 0.7036 |
| silver_bug (Icarus) | boss | 67,592 | 76,991 | 207 | 20 | 207 | 2931 | 36.67 x 18.56 x 15.00 | 0.6246 |
| attack_helicopter (complex unit) | air | 4,722 | 5,896 | 30 | 9 | 30 | 245 | 6.35 x 4.44 x 2.02 | 0.7192 |
| attack_helicopter_hd (complex unit) | air | 6,902 | 9,300 | 38 | 9 | 38 | 372 | 6.35 x 4.44 x 2.02 | 0.6856 |

- fighter_jet: renderers 40 over the jet normal budget 36
- fighter_jet_hd: triangles 14,216 over the jet hd budget 12,300; vertices 21,233 over the jet hd budget 19,200; renderers 51 over the jet hd budget 49
- silver_bug: triangles 67,592 over the boss_m normal hard cap 55,000 (info: kept, owner rule); vertices 76,991 over the boss_m normal hard cap 70,000 (info: kept, owner rule); renderers 207 over the boss_m normal budget 178

## Over budget (models per class and metric)

| class | metric | over soft (warning) | over hard (error) | over the hard cap |
|---|---|---:|---:|---|
| boss_l | triangles | 3 | 0 | - |
| boss_l | vertices | 2 | 0 | - |
| boss_m | renderers | 4 | 0 | - |
| boss_m | triangles | 4 | 0 | - |
| boss_m | vertices | 3 | 0 | - |
| boss_s | renderers | 3 | 0 | - |
| boss_s | triangles | 5 | 0 | - |
| boss_s | vertices | 6 | 0 | - |
| ground | movingParts | 3 | 0 | - |
| ground | renderers | 14 | 0 | - |
| ground | triangles | 34 | 0 | - |
| ground | vertices | 41 | 0 | - |
| helicopter | renderers | 1 | 0 | - |
| helicopter | triangles | 1 | 0 | - |
| helicopter | vertices | 1 | 0 | - |
| jet | renderers | 7 | 0 | - |
| jet | triangles | 4 | 0 | - |
| jet | vertices | 4 | 0 | - |
| prop | renderers | 1 | 0 | - |
| prop | triangles | 1 | 0 | - |
| prop | vertices | 1 | 0 | - |
| scenery | renderers | 2 | 0 | - |
| structure | movingParts | 1 | 0 | - |
| structure | renderers | 6 | 0 | - |
| structure | triangles | 2 | 0 | - |
| structure | vertices | 2 | 0 | - |
| tower | movingParts | 1 | 0 | - |
| tower | triangles | 1 | 0 | - |
| tower | vertices | 1 | 0 | - |

85 models over a budget, 0 of them over a hard cap.

## Error reasons (count of models)

- none

## Flagged models (0)

