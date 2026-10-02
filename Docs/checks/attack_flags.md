# C13: attack capability flags (prompt 29, read only)

| flag (S05) | existing equivalent | where |
|---|---|---|
| canHitGround / canHitAir | `WeaponDef.Targets` (TargetLayers Ground/Air/both) and `CanTarget(flying)` | Definitions.cs, `targets` in balance.json |
| interceptable | implied by the round: `DamageSystem.GunTakes`/`TryIntercept` (missile, drone, direct rocket; lobbed shells by share; beams and Energy never) | DamageSystem.cs |
| flareEligible | `WeaponDef.FlareResist` (0 = fully decoyed, 1 = ignores flares) on guided air-to-air and SAMs | `flareResist` |
| apsEligible | same as interceptable for vehicle APS (`ApsDef.Direct`, `Rockets`, `Shells`) | ApsDef |
| ciwsEligible | point-defence guns (`ApsDef.Burst`) through `GunTakes` | ApsDef |
| (interceptor only) | `WeaponDef.InterceptOnly` | Definitions.cs |

No field named interceptable/flareEligible/apsEligible/ciwsEligible exists; their meaning is computed from the round. S05
therefore adds them as optional overrides (`interceptable`, `flareEligible`, `apsEligible`, `ciwsEligible`, default:
what the round rules say) instead of duplicate stored fields, and canHitGround/canHitAir read `targets`.
