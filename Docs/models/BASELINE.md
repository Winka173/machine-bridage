# GLB baseline (prompt 27 step 2)

Generated 2026-10-04 by `python Tools/assets/glb_check.py` over Assets/MachineBrigade/Resources/Models (456 GLB files). Full data: Tools/assets/baseline.json. Static analysis only (no Unity run).
Rules: DECISIONS "27 step 0 + baseline"; budgets: Docs/models/BUDGETS.md (over the soft budget a warning, over
the hard cap an error). Warnings are listed in the JSON.

## Totals per category

| category | models | triangles | avg | largest | material slots | with errors | with warnings |
|---|---:|---:|---:|---|---:|---:|---:|
| boss | 29 | 1,141,989 | 39,378 | leviathan (86,412) | 3,979 | 1 | 29 |
| ground | 66 | 569,046 | 8,621 | main_battle_tank_hd (16,462) | 3,735 | 2 | 40 |
| structure | 71 | 412,111 | 5,804 | headquarters (21,052) | 3,809 | 2 | 18 |
| prop | 115 | 258,170 | 2,244 | command_hq (8,872) | 1,568 | 0 | 3 |
| unlisted | 34 | 108,062 | 3,178 | apc_hd (14,968) | 668 | 0 | 0 |
| air | 19 | 101,328 | 5,333 | fighter_jet_hd (14,216) | 711 | 0 | 14 |
| wreck | 1 | 69,462 | 69,462 | silver_bug_wreck (69,462) | 205 | 0 | 1 |
| scenery | 96 | 40,708 | 424 | rubble_large (3,516) | 294 | 0 | 2 |
| munition | 25 | 5,154 | 206 | bomb (404) | 175 | 0 | 0 |

All files: 2,706,030 triangles, 5 with errors, 102 more with warnings only.

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
- silver_bug: runtime names with a Blender suffix: Mount_gun.001, Mount_gun.002, Mount_gun.003, Mount_gun.004; triangles 67,592 over the boss_m normal hard cap 55,000 (info: kept, owner rule); vertices 76,991 over the boss_m normal hard cap 70,000 (info: kept, owner rule); renderers 207 over the boss_m normal budget 178

## Over budget (models per class and metric)

| class | metric | over soft (warning) | over hard (error) | over the hard cap |
|---|---|---:|---:|---|
| boss_l | triangles | 3 | 0 | - |
| boss_l | vertices | 2 | 0 | - |
| boss_m | renderers | 4 | 0 | - |
| boss_m | triangles | 4 | 0 | - |
| boss_m | vertices | 3 | 0 | - |
| boss_s | renderers | 3 | 1 | ixion |
| boss_s | triangles | 5 | 0 | - |
| boss_s | vertices | 6 | 0 | - |
| ground | movingParts | 3 | 0 | - |
| ground | renderers | 14 | 2 | fpv_carrier, heavy_aa |
| ground | triangles | 26 | 0 | - |
| ground | vertices | 33 | 0 | - |
| helicopter | renderers | 1 | 0 | - |
| helicopter | triangles | 1 | 0 | - |
| helicopter | vertices | 1 | 0 | - |
| jet | renderers | 8 | 0 | - |
| jet | triangles | 4 | 0 | - |
| jet | vertices | 4 | 0 | - |
| prop | renderers | 1 | 0 | - |
| prop | triangles | 1 | 0 | - |
| prop | vertices | 1 | 0 | - |
| scenery | renderers | 2 | 0 | - |
| structure | movingParts | 1 | 0 | - |
| structure | renderers | 7 | 2 | aircraft_hangar, vehicle_hangar_base |
| structure | triangles | 2 | 0 | - |
| structure | vertices | 2 | 0 | - |
| tower | movingParts | 1 | 0 | - |
| tower | triangles | 1 | 0 | - |
| tower | vertices | 1 | 0 | - |

79 models over a budget, 5 of them over a hard cap.

## Error reasons (count of models)

- over a budget hard cap: 5

## Flagged models (5)

- **aircraft_hangar** (structure): renderers 93 over the structure normal hard cap 48
- **fpv_carrier** (ground): renderers 78 over the ground normal hard cap 76
- **heavy_aa** (ground): renderers 77 over the ground normal hard cap 76
- **ixion** (boss): renderers 175 over the boss_s normal hard cap 162
- **vehicle_hangar_base** (structure): renderers 129 over the structure normal hard cap 48
