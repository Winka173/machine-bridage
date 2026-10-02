# C03: zero-CP cards (prompt 29, read only)

| id | data | in a deck? | notes |
|---|---|---|---|
| supply_truck | `cp` 0, class Support, `card` not set (= true) | The AI never buys it (`ConquestAi.TryDeploy` skips `CpCost <= 0`). The deck screen's own filter is Game/UI code: check locally. | Not in `Progression.EarlyPrices`. |
| hover_gunboat | `cp` 0, class Light, boss escort ("Hộ tống boss" in the AI sheet) | as above | not in EarlyPrices |
| uav_loiter_strike | `cp` 0, class Plane, flying | as above; it is the unit of the support card below | not in EarlyPrices |
| uav_loiter_strike_support | support, kind Escort, 6 CP, `units: [uav_loiter_strike]` | a support card (MatchSettings.AllSupports) | Progression price 2500 coins |

- **"Mua sớm 300 xu"**: the 300-coin early prices are a hand-written table (`Progression.EarlyPrices`, the round-1 sheet's
  "Mua sớm"); none of the three zero-CP vehicles is in it. Any "300 xu" line on their cards would be generated from
  that table: none is.
- **UAV of the support card**: spawned by `StrikeSystem` (Escort: `SpawnVehicle`, expires after the support's
  duration, guards the called point). It is an ordinary vehicle of the side while alive: it counts in the aircraft cap
  (`EconomySystem.AircraftCount`: flying, not boss, not scripted, not `airCapFree`) and the vehicle count; it adds
  nothing to the supply (`ArmyCp` sums `ArmyCost` = its 0 CP). Not changed (read only).
