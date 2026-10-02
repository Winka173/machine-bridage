# C10: anti-air multipliers against aircraft (prompt 29, read only)

`DamageTable.Effective` = penetration step x damage type. Against an aircraft there is no overmatch, so the step is at
most 1.0 (`Penetration(pen, armour 0, overmatch false)` = table[1] = 1.0 for pen >= 1). Damage type
Fragmentation vs Air = **1.3**.

| weapon | damage | type | pen | x aircraft (armour 0) |
|---|---|---|---|---|
| buk_launcher (inherits sam_long) | 320 | Fragmentation | 3 | **1.3** |
| sam (light SAM) | 170 | Fragmentation | 2 | 1.3 |
| stinger_atas | 178 | Fragmentation | 2 | 1.3 |
| air_to_air | 294 | Fragmentation | 3 | 1.3 |

The sheet's assumed 1.3 holds. Aircraft with armour above 0 (none among the B1 aircraft rows) would take less.
