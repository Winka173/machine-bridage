# AUDIT P5 — monitoring / optimisation (lane A, 05/10)

Branch `feature/ai-p5` (worktree MachineBrigade-art), on top of P0-A/B/C, P0-D + P1, P2, P3 and P4. Source of truth:
`Machine_Brigade_AI_Behavior_MASTER_FINAL.md` Parts K, L, N, O, P, sections 3, 94, 98-99, 114, 185, 215, Part R R8, Part V.
Not run here (no Unity, no tests, no sims): the Sim builds (`dotnet build Tools/simbuild/Sim.csproj`, 0 errors, no new warnings);
`AiMasterP5Tests.cs` and `AiMasterP5PerfHarness.cs` compile against the Sim + NUnit 3.13.3 (scratch project, `GameContent` /
`MatchSettings` / `UnityEngine.Debug` stubbed); the Game edits checked by reading (C# 9).

Legend: **changed** = new or altered behaviour; **kept** = the existing code already does it (Part A); **scaffold** = API in
place, behaviour partial; **deviation** = differs from the letter of the spec, why given.

Switches for the lead's sweeps: `ai.health.enabled` (false = counters only, no recovery), `ai.ammo.enabled`, `ai.towers.enabled`,
`ai.budget.squadBuckets` (1 = the old 4 Hz think for every squad). 33 new keys under `ai.health / ammo / towers / budget`
(`SimTunables.AiMasterP5.cs`, registered in `SimTunables.Pack2.cs`, same values in `Resources/Data/tunables.json`).

## Architecture

- `world.Health` (`AI/P5/AiHealthMonitor.cs`, stepped by `SimWorld.StepP5` right after the combat watchdog, own 1 Hz clock,
  phase 0.5 s): reads every lane's counters, judges the AI sides' squads (`HealthRules`, pure), recovers through existing paths.
- `world.AiPerf` (`AI/P5/AiBudget.cs` `AiPerfCounters`): Stopwatch counters per `AiPerfSection`, off by default.
- `world.Spatial` (`AiSpatialIndex`): uniform grid, rebuilt at most once a step, invalidated after the movement step.
- `AiCadence` (pure): the squad think buckets.
- `AmmoTactics` / `MagazineReading` (pure rules + a reader), used by `SquadLayer.P5` (holds), `CombatSystem.P5` (target keeping)
  and `Commander.P3` (reload scoot).
- `TowerCoordination` (pure) used by `CombatSystem.P5.P5Worth` after `P3Worth` in the target score.
- `ReasonCodes` (one registry, `ReasonCodes.All`, 235 entries) + `P5Reasons`; `SimWorld.CuesOf` + `MatchRunner.Cues` (spec 215).

## Section -> code -> status

| Spec | What it asks | Code | Status |
|---|---|---|---|
| K (track) | 13 aggregate metrics | `HealthCounters`: armedIdleWithoutReason (`CombatWatch.Unexplained`), squadsNoDamage, blockedUnits + ratio, severeUnstuck (`Traffic.Stats`), orders / unit / min (`SimWorld.OrdersOf`, counted in `Submit`), target and action switches / min (`DecisionLog.Totals`), noMapInfluencePurchases (0 by construction, P0-B), lowUtilizationUnitClasses (`AdaptationTracker.LowClasses`, new), stalledObjectiveAssignments, combatAnomalies, deadlockCycles, navalReverseAttempts (events + refused) | **changed** |
| K1 idle | audit, refresh, top reasons | share of armed AI units idle without a reason >= `idleTripShare` (or a fresh unexplained one): their unit and mount retarget clocks reset (the next combat step re-solves), `WATCHDOG_IDLE_AUDIT` + `WATCHDOG_IDLE_TOP_REASONS` (top 3 codes) | **changed** |
| K1 squad no damage | anchor, route, mission re-evaluated after 10-20 s | in contact (enemy within reach + 15 m, seen < 5 s), no member shot for 15 s, not holding / dodging / defending: `HealthReassess` (taken as the squad's idle reassessment: re-score, may keep the action), goal re-issued (new route), the side's fire-support anchors picked afresh (`FireSupportDirector.Refresh`, served by TacticalAi), `WATCHDOG_SQUAD_ZERO_UTILIZATION`; one recovery per squad per 20 s | **changed** |
| K stalled objective | (metric) | objective not 5 m closer for 20 s out of contact: same re-evaluation without the anchor, `WATCHDOG_SQUAD_STALLED_OBJECTIVE` | **changed** |
| K1 blocked | traffic escalation, re-route packets | >= 25 % (and >= 4) of a side's moving ground units at jam stage 3+: squads with half their members jammed re-issue their goal (P1's corridor replan / predictive congestion choose the way) and re-score, `WATCHDOG_TRAFFIC_ESCALATION` | **changed** (packet split stays P1's) |
| K1 low utilisation | same-match purchase modifier | P4's `PurchaseModifier` already acts; the monitor counts classes and logs `WATCHDOG_LOW_UTILIZATION_CLASSES` on change | **kept** + log |
| K1 churn | longer commitment for a while | `DecisionLog.Churning` -> commitment x1.5 for 30 s (`CommitScale` in `Squads.Think`), `WATCHDOG_CHURN_DAMPED` | **changed** |
| K1 naval reverse | hard error in debug; turn / slow / other lane | the controller already clamps to 0 (P0-C); now `NAVAL_REVERSE_FORBIDDEN` at the clamp and from the monitor (error count), `ai.health.strictAssertions` throws (tests / debug) | **changed** |
| K "never cheat" | only valid re-evaluation | recoveries only set the squad's reassessment flag, NaN its issued goal, clear anchors, reset retarget clocks, lengthen commitment; no position / health / vision change | **changed** |
| L1 | no exposed charge on an empty / near-empty magazine unless emergency | `AmmoTactics.MayCharge` (rule); in squads (`UnitsP5`): a member advancing (Attack / Flank) whose meaningful (>= 2 s) magazine is reloading stops (`POSITION_RELOAD_HOLD`) and rejoins the squad's goal when loaded or in an emergency (urgency >= 0.75, overwhelmed, dodge: `POSITION_RELOAD_RESUME`) | **changed**; **deviation**: a near-empty in-place magazine that is not yet reloading is not held (the game reloads it only once empty or at home; holding would idle it) |
| L2 | long reload windows for short reposition | `RepositionWindow`: clip reloads and on-the-move reloads only; an in-place magazine reload pauses while moving (prompt "reload standing still"), so no free window there | **scaffold** (rule + test; the P2 firing-lane resolver can call it) |
| L3 | artillery may scoot during reload | `ScootDuringReload` added to P3's scoot trigger (known enemy guns, no immediate threat, >= 4 s of a reload that runs on the move), `ARTILLERY_SCOOT_DURING_RELOAD` | **changed** |
| L4 | support weapons avoid exposure while unable to fire | `HoldBack(..., supportRole)`: FireSupport / AntiAir / Support roles hold while reloading even when the reload runs on the move | **changed** |
| L5 | do not cancel reload on target churn | reloads never restart on a target change here (**kept**); a reloading mount of an AI side keeps its valid target without re-scoring (`Retarget`, counted `TargetsKeptReloading`) | **changed** |
| N overkill | towers avoid overkilling one weak unit | P3's planned-damage board already covers AI sides' towers (**kept**); `TowerCoordination.Overkill` adds the cross-tower check (other towers' cycle damage >= 1.15 x hp -> x0.35 unless already on it or critical) | **changed** |
| N SAM / AA | aircraft threatening the protected zone first | AA tower x1.6 on an aircraft within 45 m of the HQ or shooting a friendly structure | **changed** |
| N AT | values heavy | anti-armour direct tower x1.3 on SuperHeavy / Armour4 / Heavy / MBT | **changed** |
| N artillery / hangar | enemy artillery / support | indirect towers and the drone hangar x1.4 on artillery / support / SAM-radar | **changed** |
| N shield / PD | interceptable threats | intercept-only mounts are skipped (their interception system targets rounds) | **kept** |
| N critical override | critical objective threat overrides the mode | ground enemy within 20 m of the HQ or shooting it: x4 (above AirFirst / ArtilleryFirst's x3), never spread off by overkill | **changed** |
| N static | no pathing, board deconfliction | towers never path (kept); the board (P3) and the cross-tower cache | **kept** |
| O | full namespace set, every rejection explainable, one registry | `ReasonCodes.All` (all 16 Part O namespaces + SQUAD / ROLE / COMBAT), every lane constant, enum code, jam stage and hull reason registered (test); Part O's 12 examples registered and written; new boss lines `BOSS_HULL_*` / `NAVAL_*` / `BOSS_PHASE_ROUTE`, escort / factory REJECT lines carry `BOSS_ESCORT_SPAWN_REJECT`; section 94's BUY / REJECT / PLAN / RESERVE verbs kept as registered aliases (P0-B tests read them); `ReasonCodes.Unregistered(log)` for the lead's runs | **changed** |
| P cadences | steering 10, tactical 4, squad 2, commander 1, procurement 0.5 Hz | steering 10 Hz ORCA (P1, kept); watchdog 4 Hz (P0-A, kept); squad layer 4 Hz with each squad thinking at 2 Hz in staggered buckets (`AiCadence`, new; dodges every tick); commander 1 Hz with teams 0.5 s apart (kept); health monitor 1 Hz (new) | **changed**; **deviation**: procurement keeps the difficulty's interval (2.2 / 1.1 / 0.6 / 0.45 s) — it is the difficulty's reaction lever; the expensive full-deck scoring is already skipped while a purchase plan (spec 16) runs |
| P / 98 | spatial hash 8-12 m, bounded neighbour queries | `AiSpatialIndex` 10 m; role-ladder clusters and tower crowds use it (same counts, tested against a scan); ORCA keeps P1's sorted window (nearest <= 10) | **changed** (other O(n) scans listed for the lead under Risks) |
| P counters | per-system timing the lead can read in a 48v48 run | `AiPerfCounters`: Steering, PathRebuild, Tactical, Squad, Commander, Procurement, Targeting, Watchdog, Bosses, HealthMonitor; `Report()`; harness `AiMasterP5PerfHarness` | **changed** |
| 99 | determinism | review below; test `Determinism_TheSameSeedGivesTheSameDecisionLogAndBattle` | **kept** |
| 114 | performance tests | 48v48 harness (Conquest, Ashfield): per-system ms, whole step mean / p99, SevereUnstuckCount + rate, NavalReverseEvents, Part K counters, codes by namespace | **changed** (not run) |
| 185 | anomaly detection, no command spam | the monitor's per-squad cooldown; P0-A / P1 kept | **kept** + **changed** |
| 215 | radio cue / gesture, no gameplay bonus | `SimWorld.CuesOf(team)` (public) and `MatchRunner.Cues`: an allied AI's cues all shown as notices; of an enemy AI only "attack_go" (never probe / feint / flank: that would give its plan away); strings en / vi | **changed** (gesture / escort animation: not done) |

## Tick / determinism review across lanes

- No `System.Random` in any AI MASTER lane (P0-A .. P5): grep of `AI/P2..P5`, `Bosses/Brain`, `Movement/JamTracker|Traffic*`,
  `ProcurementDirector`, `EngagementFeasibility`, `CombatActivityWatchdog`: none. Seeded legacy RNGs stay (prompt-era, not AI
  MASTER): `ConquestAi._random` (buy noise / Easy skips, seeded per side), `TacticalAi` flank side (seeded), deck drawing, the
  world's combat dispersion (`SimWorld.Random`); all seeded, so replays hold; replacing them would change balance (not in scope).
- Dictionary iterations in the lanes that could order a decision: `ComponentState` prune, `PlannedActionBoard.Covering` (count),
  `CombatActivityWatchdog` prune, `TrafficCoordinator.SweepPassing` (collect then remove): all order-independent. Every decision
  loop walks `VehicleList` (spawn order) or squad lists; ties by id; the monitor walks teams 0..2.
- Timing counters (Stopwatch) never feed a decision; the spatial index sorts `Near` by id and only counts in `CountSameSide`.

## Regression rows (tests written, not run)

`Assets/MachineBrigade/Tests/EditMode/AiMasterP5Tests.cs` (category `AIMasterP5`, 21 tests) and
`AiMasterP5PerfHarness.cs` (category `AIMasterP5Perf`, Explicit).

| Row | Test |
|---|---|
| R8 health monitor (inject stalled squad -> detect, valid re-evaluation, log) | `R8_InjectedStalledSquad_IsDetectedReEvaluatedAndLogged` (world), `R8_HealthRules_AStalledSquadIsDetectedOnceAndNotSpammed`, `R8_HealthRules_SystemThresholds`, `R8_TheMonitorCountsEveryPartKMetric` |
| L1-L5 | `L1_*`, `L2_*`, `L3_*`, `L4_*`, `L5_*`, `L_ReadingAVehicle_AnEmptyMagazineIsReloading` |
| N1-N5 | `N1_TowersAvoidOverkillOnOneWeakUnit`, `N2_SamTowersFirst...`, `N3_..._N4_...`, `N5_ACriticalObjectiveThreatOverridesTheTowerMode` |
| O registry | `O_EveryLanesCodeIsRegistered`, `O_TheRegistryIsConsistent`, `O_ABattlesLogHasOnlyRegisteredCodes` |
| P / 98 / 99 | `P_SquadBucketsSpread...`, `P_TheSpatialIndexCountsTheSameAsAScan`, `P_PerfCountersStayOff...`, `Determinism_TheSameSeed...` |
| 114 / Part S perf | `Perf48v48_ReportsPerSystemMsSevereUnstuckAndNavalReverse` (writes `Temp/ai_p5_perf_48v48.txt`; `MB_P5_SECONDS`) |

## Risks for the lead's runs

1. Squads think at 2 Hz (was 4 Hz): reaction to a new threat can be up to 0.25 s later (dodges stay at 4 Hz). Tests that time
   squad switches tightly may move; `ai.budget.squadBuckets` 1 restores the old cadence exactly.
2. Reload holds stop an advancing member while its in-place magazine reloads (MLRS, missile carriers): Attack packages may arrive
   more spread out; `ai.ammo.enabled` false restores.
3. AI towers: a ground enemy within 20 m of the HQ now beats AirFirst / ArtilleryFirst modes (x4); cross-tower overkill spreads
   tower fire. Player towers unchanged.
4. Monitor recoveries re-issue goals (new paths) at most once per squad per 20 s; watch path-queue load in the 48v48 run.
5. Remaining O(n) scans per call (candidates for the grid if the counters show them): `CombatSystem.FriendInLine` (per score),
   `TowerWorth` E.2 focus, P3 / P4 squad and contact loops. The 48v48 counters will say which matter.
6. Boss / naval log lines changed text (`BOSS_HULL_*`, `BOSS_PHASE_ROUTE` first); no test read the old text (grep).

## Not done / for later

- Leader gestures / escort animations for spec 215 (cues shown as notices only).
- Procurement at 0.5 Hz (kept by difficulty, see deviation); flow-field tiles (P1's phase 2).
- L2 reposition window is a rule only (no caller yet beyond the tests).
