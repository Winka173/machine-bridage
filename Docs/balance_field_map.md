# Prompt 29 CHECK C01: Manifest field paths -> real keys

Source: `Docs/balance/manifest_v2.json` (export of `Machine_Brigade_Can_bang_dot2_v2.xlsx`, Manifest sheet). Each logical
`field_path` (R5) maps to a key in `Assets/MachineBrigade/Resources/Data/balance.json` (or code). The apply tool
(`Tools/balance/p29_apply.py`) implements exactly this table; a path not listed is CONFLICT ("no mapping").

| field_path | rows | real key | read (current) | write | status |
|---|---|---|---|---|---|
| `units.<id>.hp` | 82 | `vehicles[id].hp` x `toughness.vehicles` (2.2; bosses `toughness.bosses`) | data hp x toughness | data hp = ROUND_HALF_UP(value / toughness); values compare in data units: equal when ROUND_HALF_UP(value / toughness) == data hp | exists |
| `units.<id>.cost` | 78 | `vehicles[id].cp` (baseCP, R7/S04) | `cp` | `cp` | exists |
| `units.<id>.speed` | 4 | `vehicles[id].speed` (m/s) | `speed` | `speed` | exists |
| `units.<id>.outgoingDamageMult` | 90 | `vehicles[id].outgoingDamageMult` | absent = 1.0 | the key | **created in pass 1 (S03)**. Not the existing `weaponDamage` (prompt 25: ground targets only, already != 1 on 29 vehicles); the two multiply |
| `units.<id>.dropDelaySec` | 37 | `vehicles[id].dropDelay` | absent = 3.5 (`EconomySystem.DeliverySeconds`) | the key | **created in pass 1 (S04)**; delivery reads it |
| `units.<id>.flare.maxCharges` | 17 | `vehicles[id].flareCharges` | absent = 0 (today flares are a skill with a cooldown, no charges) | the key | **created in pass 5 (S06)** |
| `units.<id>.flare.rechargeSec` | 17 | `vehicles[id].flareRecharge`, else the cooldown of the vehicle's `Flares` skill (`skills[]`: heli_flares 20, jet_flares 16, bomber_flares 11, ...) | override, else skill cooldown, else null | the key; null new value removes the flare skill from the vehicle | **created in pass 5 (S06)**; the shared skills are not edited (R8 in spirit) |
| `units.<id>.apsCapability` | 3 | `vehicles[id].apsCapability` | absent = "—" (NONE) | the key | **created in pass 5 (S07)** |
| `units.<id>.interception.rechargeSec` | 2 | `vehicles[id].aps.recharge` | `aps.recharge` (absent aps: null) | the key | exists |
| `units.<id>.interception.maxCharges` | 1 | `vehicles[id].aps.charges` | absent aps: 0 | the key | exists |
| `units.<id>.interception.shellChance` | 1 | `vehicles[id].aps.shells` | absent: 0 | the key | exists |
| `units.<id>.interception.blocks.artilleryRocket` | 1 | `vehicles[id].aps.rockets` | absent: false | the key | exists (the "rockets" flag lets APS take artillery rockets) |
| `modes.<mode>.cpStockCap` | 7 | `economy.bankByMode[tag] = [from, to]` (new data), read by `SimWorld.EnableEconomy` | the code's bank for the mode: default 30 (`TeamEconomy`), Siege attacker 40, Boss Rush 45 (ModeSessions), Vault = mode bank + commander okoye's BankBonus 15 | `[expected_before, new_value]` per mode tag | **created in pass 4 (E1)**; mode names -> tags below |
| `economy.supplyThreshold` | 1 | `TeamEconomy.Supply` (army cap x 1.5) | HOLD (E2) | not written | HOLD |
| `aircraft.returnBecauseLowHP` | 1 | code: `TacticalAi.Refit` (`RefitBelow`) | code | code (pass 6) | code |
| `equipment.trophy_aps.rule` | 1 | code: gear trait `TrophyAps` (`VehicleBoost.cs`) | code | code (pass 5, S07) | code |
| `boss.gungnir.*` | 5 | vehicle `rail_supergun` (the Gungnir) and its big attack | data + code | pass 7 (G1) | partly code |
| `weapons.<id>.range`, `units.<id>.dps`, `balance.hpFloorCurve`, `metric.*`, `units.*.speed` | 6 | REJECT rows | - | never | REJECT |
| `—` | 9 | system bundles S01-S09 (code) | - | code | code |

Mode names of E1 -> `SimWorld.ModeTag` (GameModeKind): "Chiếm cứ điểm / Tử chiến / Vua đồi" -> Conquest, Deathmatch,
KingOfTheHill; "Công phá" -> Assault; "Công thành" -> Siege; "Phòng thủ / Vô tận" -> Defend, Endless; "Sinh tồn" ->
Survival; "Săn trùm" -> BossRush; "Chỉ huy Vault" -> derived (mode bank + 15), checked, not written.

Every unit id of the Manifest exists in balance.json (checked by the export: none missing). Gungnir's entity id
`gungnir` maps to `rail_supergun`.
