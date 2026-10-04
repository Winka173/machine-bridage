# AUDIT P0-A — combat correctness (lane A, 04/10)

Branch `feature/ai-p0a`. Source of truth: `Machine_Brigade_AI_Behavior_MASTER_FINAL.md` (MASTER RULES, Part A kept). Lane scope:
Part C (watchdog + no-idle invariant), sections 42-47, 83, 88-91, 105-106, Part B B2/B3, Part H, Part O codes of this lane,
tests R1-R3, 113, 224 (opportunity fire). Not run here (no Unity, no tests, no sims): the Sim builds
(`dotnet build Tools/simbuild/Sim.csproj`), the new test file compiles against the Sim + NUnit (scratch check).

Legend: **changed** = new or altered behaviour; **kept** = the existing code already does it (Part A: integrate, not rewrite);
**scaffold** = API / data in place, behaviour belongs to a later lane; **deviation** = differs from the letter of the spec, why given.

## Section -> code -> status

| Spec | What it asks | Code | Status |
|---|---|---|---|
| 42 / 105 | Hard feasibility before any score: targetable, mask, line/arc, reachable firing solution, min-range trap -> -inf | `CombatSystem.P0A.Feasibility` (returns a `TargetReject`); `IsValidAutoTarget` now = `Feasibility == None`, so every candidate list (BestInRange, Retarget, BetterThanOrder, secondaries, coax AA) is filtered before Score | **changed**: adds the mount's bearing (`CanBear`: traverse-limited turret / fixed hull that cannot turn) and the aim-time cut (`maxAimSeconds` 10 s, mobile shooters only). Old checks (alive, truce, ceasefire, coastal battery, fog, tier/layer, reach, min reach, ground dead zone, line of fire) kept in the same order |
| 42 | "Not inside min range trap without escape" | `Feasibility` -> `TargetReject.MinRange`; escape = existing `CloseIn` / `DirectArtillery` EscapeRoute | **kept** + reason code `COMBAT_IDLE_WAITING_MIN_RANGE` |
| 43 | Utility = DPS x HitProb x Value x RangeAccess x AngleAccess x TimeOnTarget | Existing `Score` (Estimate = damage type x armour x pen x facing; bonuses; worth; distance divisor) + `P0AWorth` (AngleAccess = aim penalty) | **kept / partial**: HitProbability and TimeOnTarget are not modelled in the score (the sim has no per-shot hit roll in targeting; time in reach needs the forecast of P4, spec 152). Noted for P4 |
| 44 / 106 | Overkill: committed > 1.15 x EffectiveHp -> another target if any; exceptions boss part focus, Executioner/kill objective, extremely dangerous | `Overkilled`, `OverkillExempt`, applied in `P0AWorth` for every weapon | **changed**: replaces the old rule (cooldown >= 2 s weapons, 1.1 x hp, x0.05). Exceptions: boss part focus (prompt 9), Executioner trait under 30 %, the player's attack order, a boss or a target worth >= 20 CP. **Deviation**: -1000 is a factor 0.001 (`overkillFloor`) so an overkilled target is still taken when it is the only one ("chọn target khác nếu có"); the -1000 would leave the gun idle |
| 45 | Current target +15 % for 1.5 s after acquire; break on invalid / unreachable / leaves domain / commander override | `WeaponState.AcquiredAt` stamped by `Acquire` when a mount's target changes; bonus in `P0AWorth` | **changed**. Breaks: invalid/unreachable/domain fail the hard filter first; the squad focus (P28Worth) and orders outrank it. The old hysteresis (`SwitchMargin` 1.3, `RetargetSeconds`) is **kept** (Part A) |
| 46 | TargetScore weights 0.20 / 0.22 / 0.18 / 0.12 / 0.12 / 0.08 / 0.08 | Existing Score is Part B B1's product form (ThreatToSelf = aiming-at-us x1.2 and can-shoot-back x1.15; WeaponSuitability = Estimate; KillOpportunity = hp share + finishing x1.5; StrategicValue = Worth; FocusFire = x1.3 / squad focus; DistanceEfficiency = divisor). New: ThreatToObjective as `1 + T x 0.22/0.20` | **changed / deviation**: the weighted sum is not substituted (it would flatten every tuned worth of prompts 8A-28 untested); the missing term (ThreatToObjective) enters at its weight relative to ThreatToSelf; weights in tunables `threatToSelfWeight` / `threatToObjectiveWeight`. Role modifier after (B2/B3 here, the rest P2) |
| 47 | Drop a target that leaves the connected firing-access region | `MovementSystem.Unreachable` -> `TargetAccessCache.CanInfluence`; used by the AI's Attack orders (dropped to Idle), attack-move engagement (not broken off for it), guard threats (not gone out to) | **changed**; logged `TARGET_UNREACHABLE_DROPPED` once per unit and target (`CombatWatch.Dropped`). The player's orders are kept (his choice; the unit shows `COMBAT_IDLE_NO_REACHABLE_TARGET`) |
| 83 | Target accessibility cache, invalidated on gate / bridge / hardpoint / wreck / terrain change | `AI/TargetAccessCache.cs`: key (unit region, 8 m target cell, reach band, min-reach band), cleared on `NavGrid.Version` change (every blocker change bumps it) or at 8192 entries | **changed**. `Resolver` hook: P0-B's reachable firing region can answer instead (see "For the lead") |
| 88 | Mount yaw/pitch limits, hull-dependent; score 0 if it cannot bear in acceptable aim time | `CanBear` + `AimTooLong` in `Feasibility` | **changed** (yaw only: the sim has no pitch limits beyond min reach / ground dead zone / tiers, which are kept) |
| 89 | AimPenalty = exp(-AimSeconds / 4) | `CombatSystem.AimSeconds` (turret: turret + hull rate; hull mount: hull rate; side/arc mounts: their mount, hull outside the arc; aircraft 0) and the factor in `P0AWorth` | **changed**; `aimTimeConstant` 4 s |
| 90 | Fire while moving; non-FWM picks a firing stop; no stop on a choke | `SelectTarget` Move/Retreat (FWM only), `CanFire` (non-FWM main stops), `CloseIn` (InTheWay / NoPark: step aside, never park in a gate) | **kept**; test A224 |
| 91 | Transit / Firing / Hold reservations; no firing spot on a transit route | `TacticalAi.FiringSpot`: pass 1 skips `LaneFlags.Route` cells; pass 2 (only if none) uses the old scoring and logs `POSITION_TRANSIT_FALLBACK` | **changed** (firing). Transit and Hold reservations: **scaffold for P0-D** (TrafficCoordinator / choke reservation, spec 30-31) |
| Part C record | lastTargetAcquireTime ... explicitHoldReason | `CombatActivityWatchdog.Record` (all fields), `RecordOf(id)` | **changed** |
| Part C1 | COMBAT_ANOMALY after 1.5-2.5 s beyond readiness; 8-step recovery | `CombatActivityWatchdog.Evaluate/RecoverAnomaly`: window = aim time expected at start + `anomalyGraceSeconds` 2 s, and no aim progress for 2 s. Steps 1/3/6 `CombatSystem.ResetAim` (second time: target suppressed 3 s), 2 hull-laid weapons turn the hull (FaceHeading), 4 line/friend recomputed by `Check`, 5/7 an AI unit's sidestep via the side's TacticalAi, 8 `WATCHDOG_COMBAT_ANOMALY` + `WATCHDOG_RECOVERY_ESCALATED` | **changed** |
| Part C2 | No idle armed unit without a reason code | `Classify` gives every armed unit one of 25 `CombatIdleReason`s; `Unexplained` (the forbidden state) is counted, logged `WATCHDOG_IDLE_UNEXPLAINED`, its aim reset, and (AI side) a push at the reachable enemy requested. Explicit reasons from the AI: `SquadLayer.ExplainHolds` (Hold/Overwatch -> OBJECTIVE_HOLD, Regroup -> WAITING_FORMATION), `TacticalAi` (held point, fall-back, reinforcements, idle guns -> WAITING_FIRE_MISSION), AiHoldFire -> HOLD_FIRE_AMBUSH | **changed**. The existing StaleIdle 12 s push is **kept** as the severe fail-safe (spec 108) |
| Part B B2 | Breacher priority; must not abandon a mission-blocking wall for a random light unit | `DoctrineWorth` (blocking structure in the mission corridor x25, a non-threat unit x0.5) and `BreachHeld` in `BetterThanOrder` (an ordered breach gives way only to an immediate survival threat, or an AA weapon to an aircraft as before) | **changed**. The breach choice itself (route cost / threat / breach time) is the **kept** prompt 32 L3 `SquadLayer.BreachChoice`; FriendlyUnitsUnblocked / ChokeRelief terms: P0-D / P3 |
| Part B B3 | Siege: tower damaging the assault > defensive tower > ... > light targets only without structures | `DoctrineWorth`: siege platform (role Siege or a siege-deploying vehicle) x2 on armed structures (x1.5 more when shooting at our side), x1.3 unarmed structures, x0.2 light targets while a valuable structure is in reach (not in self-defence) | **changed** |
| Part H | ThreatToObjective mode-aware | `ThreatToObjective`: Conquest capture (our point 1, other 0.7), Escort (shooting the convoy 1, convoy in reach 0.5), Defend (enemy breacher within 30 m of our walls 1), Siege (defence shooting at our assault on a structure 1, covering our breach 0.8), shooting at our structures 0.6 | **changed**. BossRush "exposed dangerous part": the prompt-9 part focus x4 is **kept**; per-part scoring is P0-C (boss target director, 65 / 179) |
| Part O | TARGET_* / COMBAT_IDLE_* / WATCHDOG_* codes | `AI/CombatReasons.cs` (`Code(...)`, `Log(...)`) writing `DecisionEntry` lines (Unit layer) | **changed**; DecisionLog class itself untouched (other lanes add their namespaces the same way) |
| 99 | Determinism | Vehicle-list order, sim clock, `SortedDictionary` for requests, id-parity sidestep side, no `System.Random` | **kept** |
| 107 | Tunables `targeting` | `SimTunables.AiP0A.cs` + `tunables.json` ai.targeting (17 keys) and ai.combatWatchdog (7 keys) | **changed**: spec values 1.5 / 0.15 / 1.15 / 4 / 0.20 / 0.22; the rest are lane choices (DECISIONS) |

## Regression rows (tests written, not run)

`Assets/MachineBrigade/Tests/EditMode/AiMasterP0ATests.cs`

| Row | Test |
|---|---|
| R1 valid target + clear LOS | `R1_AValidTargetWithAClearLineIsShot` |
| R1 friend blocks | `R1_AFriendInTheLineGivesAReasonOrTheTankStillFights` |
| R1 inside min range | `R1_ATargetInsideTheMinimumRangeIsWaitingMinRange` |
| R1 outside mount arc | `R1_ATargetOutsideAFixedMountsBearingIsFiltered` |
| R1 stale target entity | `R1_AStaleTargetEntityIsDroppedAndTheTankFightsOn` |
| R1 reloaded but aim stuck | `R1_AStuckAimIsACombatAnomalyWithAReasonAndARecovery` |
| R1 formation waiting incorrectly | `R1_AnAiUnitStandingWithAReachableEnemyInSightIsRecovered`, `R1_AFormationWaitIsAnExplicitReasonAndExpires` |
| R2 breacher | `R2_ABreacherKeepsOnTheBlockingWallBesideARandomJeep`, `R2_AnImmediateSurvivalThreatMayTakeTheBreacherOffTheWall` |
| R3 siege | `R3_ASiegePlatformShellsTheTowerBeforeTheScout` |
| 113 unreachable / cache | `T113_AnUnreachableTargetIsFilteredAndTheAiOrderDropped`, `T113_TheAccessCacheIsDroppedWhenTheGroundChanges` |
| 113 behind wall (direct vs indirect) | `T113_ATargetBehindAWallIsFilteredForDirectFireButNotForIndirect` |
| 113 mount bearing / min range | `T113_AMountThatCannotBearIsFiltered`, `T113_TheMinimumRangeIsRespected` |
| 113 overkill spreads / exceptions | `T113_OverkillSpreadsTheFire`, `T113_OverkillLeavesTheExceptionsAlone` |
| 113 stickiness | `T113_TheCurrentTargetIsStickyForASecondAndAHalf` (+ existing PlayTest8A `ATargetIsHeldBetweenTwoOfTheSameWorth`) |
| 89 aim penalty | `T113_AimTimeCostsATargetBehindTheTurret` |
| 113 boss part focus | `T113_TheBossPartFocusStillOverridesOverkill` |
| 224 opportunity fire | `A224_ATurretFiresOnTheMoveAndTheRouteDoesNotChange` |
| Part H escort | `H_TheUnitShootingAtTheConvoyOutranksADistantHeavy` |
| Tunables | existing `TunablesTests` cover the 24 new keys (file = code defaults) |

Not this lane's rows: R4 (fire support by mode, P2 Part J), R5 (component damage, P2 Part F), R6 (friendly lane sidestep: the
watchdog's BlockedByFriend sidestep covers the "never silently idle" half; the alternate-slot choice is P2 Part E), R7 (cover,
P2 Part D), R8 (health monitor, P5 Part K: it can read `CombatWatch.Anomalies / Unexplained / Escalations / Dropped`).

## Risks for the lead's runs

1. Behaviour now differs in every fight (aim penalty, stickiness, overkill for all weapons, objective factor). Tests that pin an
   exact target choice between near-equal candidates may move; PlayTest8A's AA-turns-on-helicopter keeps a 50x margin.
2. Spec 47 drops: an AI Attack order on a target sealed off from the unit's ground region is dropped every time it is issued
   (the commander re-issues; the unit stands with `COMBAT_IDLE_NO_REACHABLE_TARGET`). Watch walled-base maps whose gate is a
   grid blocker: the squad breach (prompt 32 L3, walls are reachable) opens them, which bumps the grid version.
3. Watchdog cost (Part P): looks at each armed unit 4 times a second, cheap exits for firing / moving / reloading; the
   no-target branch scans the vehicle list once (`NearestEngageable`). Measure in the 48v48 gate.
4. `maxAimSeconds` 10 s: mobile units only, turret + hull rate; a unit whose turret and hull are both crippled leaves targets it
   cannot bear on (reason `COMBAT_IDLE_BLOCKED_BY_ARC`).

## For the lead / other lanes

- P0-B: plug the reachable firing region into `world.TargetAccess.Resolver` (unit region, target point, reach, min reach ->
  bool); the cache and the domain rules (air, ships, fixed defences) stay here.
- P0-C: `CombatIdleReason.BossControlled` is what a boss's laid mounts report; per-part target scoring (Part H BossRush) is yours.
- P0-D: `CombatReasons.PositionTransitFallback` marks the firing spots that still sit on a route (map data to fix or a
  TrafficCoordinator Transit/Hold reservation to add).
- P5 Health Monitor: `world.CombatWatch` counters and `RecordOf(id)`; reason per unit `ReasonOf / CodeOf`.
