# AUDIT P4 — advanced planning (lane A, 05/10)

Branch `feature/ai-p4` (worktree MachineBrigade-art), on top of P0-A/B/C, P0-D + P1, P2 and P3. Source of truth:
`Machine_Brigade_AI_Behavior_MASTER_FINAL.md` sections 132-133, 152-158, 174-184, 204, 214-217 and Part M, plus two P3 leftovers
(one owner per gun; P0-B section 18's boss-phase reserve and "composition enough"). Not run here (no Unity, no tests, no sims):
the Sim builds (`dotnet build Tools/simbuild/Sim.csproj`, 0 errors, 0 new warnings); `AiMasterP4Tests.cs` compiles against the
Sim + NUnit 3.13.3 (scratch project, `GameContent` stubbed).

Legend: **changed** = new or altered behaviour; **kept** = the existing code already does it (Part A); **scaffold** = API in
place, behaviour partial or for a later lane.

Switch for the lead's sweeps: `ai.planning.enabled` (false = P3 behaviour exactly: every P4 hook returns early or returns the
P3 value; the boss pacing and weakpoint utility are off too). It also needs `ai.coordination.enabled` (the P4 state lives on
P3's `TeamCoordination`). 109 new keys under `ai.planning / forecast / packageAbort / commitment / opportunity / probe / feint /
adaptation / airOps / bossTactics / stagger / gating / ownership / cues` (`SimTunables.AiMasterP4.cs`, registered in
`SimTunables.Pack2.cs`; the same values in `Resources/Data/tunables.json`).

## Architecture

- `TeamCoordination.Planning` (`AI/P4/Planning.cs`): one `TeamPlanning` per AI side, made by its commander: forecast cache, plan
  `RepetitionMemory`, `AdaptationTracker`, boss `PatternMemory`, `IntentOwnership`, opportunity windows, probe lane memory,
  bomb-drop reservations, cues, `PlanningMetrics`. Fed by observations only: P3's event hook now also forwards deaths (own /
  seen) and `PartBroken` (seen bosses); telegraphs from `TeamIntel.Warnings` (`WarningZone` got `Source` / `Origin`: the boss and
  where it stood, both public).
- Commander (`AI/P4/Commander.P4.cs`): `PlanP4` runs right after P3's `CoordinateP3` (1 Hz) and works on P3's attack package.
  Air (`AI/P4/Air.P4.cs`): `AirP4` before the old `Aircraft` logic for every aircraft outside squads. Ownership
  (`AI/P4/Ownership.P4.cs`): guns (P3 fire missions / scoots vs `TacticalAi.DirectArtillery`) and aircraft (`Vehicle.P4Held`,
  read by `TacticalAi.Ready` / `DirectFlankers`).
- Squads (`AI/P4/SquadLayer.P4.cs`): `AdjustP4` after `AdjustP3` in `Score`; `EnvelopeP4` after `FixP3` in `Execute`; escape
  sectors and stagger inside `Dodge`.
- Bosses (`Bosses/BossSystem.P4.cs`): weakpoint utility in `ChoosePart` for AI sides; pressure budget in big-attack `TryBegin`.
- Procurement (`ConquestAi.Procurement.cs`, `ConquestAi.cs`): `HoldPurchaseP4` before buying; `PurchaseAdjustP4` in the card score.
- Pure rules (`AI/P4/PlanningRules.cs`): forecaster, planner, dependencies, abort, repetition, probe / feint, escape sectors,
  pattern memory, pressure budget, weakpoint, commitment, stagger, gating, air rules, ownership — what the tests exercise.

## Section -> code -> status

| § | Spec | Code | Status |
|---|---|---|---|
| 152 / 222 | Short-horizon forecast 4-8 s: DPS by target class, armour / penetration, range uptime, AoE, support, local threat -> losses, powers after, breakthrough; no projectile sim | `CombatForecaster.Forecast`: two half-steps of attrition (each side's DPS shrinks with its losses), DPS vs the other side's hp-weighted front-armour mix through `DamageTable.Effective`, air / ground mix, range uptime (closing to reach), splash x cluster size, guns in reach as support DPS, repair auras, unknown-ground margin x1.25; inputs from own units + known contacts (def armour / weapons are public; hp from the seen strength). Horizon 6 s, cache 0.75 s (`TeamPlanning.TryForecast`) | **changed** |
| 153 | Forecast usage: frontal vs flank, wait artillery vs attack now, release reserve, support need; never a health-retreat rule | plans (154); reserve candidate rank 3 "forecast collapse" in P3's ranked release; `SupportWantedP4` asks a barrage for a wait-artillery plan without guns in reach; P0-B "force enough" (below). The hold (plan D) is pre-contact only and never under an emergency objective | **changed** |
| 154 | 2-4 plans A attack now / B wait artillery / C flank / D split-hold; PlanUtility = ObjectiveGain + EnemyLoss - FriendlyLoss - Delay - Congestion - Uncertainty; depth 1-2 | `EvaluatePlans` + `ShallowPlanner`: one forecast per plan (flank: x1.25 own DPS, 0.6 enemy uptime, detour delay, both sides tried; B: guns' prep loss over 4 s; D: no contact, delay cost); depth 2 on Hard+ adds known enemy groups within 80 m (`Deepen`); objective gain 30 x breakthrough, losses x1 / x1.2 by strength, delay 0.6 pt/s x (1 + urgency), congestion = P3 route bookings, uncertainty = unknown share on the way, + opportunity windows; switch margin 10 %; an attack leaving < 35 % own power loses to a valid hold. Applied to P3's package: A = frontal (no fix / flank), C = fix-and-flank on the chosen side (one squad: its own flank side), B = execute later + restaged members, D = package aborted, primary squads hold for the commitment window (`OBJECTIVE_PLAN_*`) | **changed** |
| 155 | Abort before contact: route invalidated, primary lost, flank blocked, objective changed, enemy estimate up, support failed; not for one unit's HP | `AbortRules.Check` (no health input) on `PlanDependencies.Broken` + main lost + flank squad gone / lane blocked + plan-B guns lost; only before contact (`OBJECTIVE_PACKAGE_ABORT_*`) | **changed** |
| 156 | Opportunity windows: AA destroyed, boss APS / shield / radar part destroyed, artillery exposed, defenders redeploy, gate opens, main force far; location, confidence, expiry, roles | `OpportunityWindow` + `TeamPlanning.Update` / `ObserveDeath` / `ObservePartBroken`: seen AA kill (air, 15 s), seen utility part break (12 s), gun in sight with no known escort within 35 m (8 s), seen strength at the watched objective -40 % without seen losses (10 s), new seen rubble in a wall (10 s), largest enemy group > 120 m from the objective (10 s); plus probe exploit / feint success. Used by plans (+10 x confidence), squads (Attack +10), bombers / SEAD (AA down), reserve rank 4 (`OBJECTIVE_OPPORTUNITY_WINDOW`) | **changed** |
| 157 | Same-match adaptation: EMA route success, class utilization, kill efficiency, support effectiveness; reset per match; no ML | `AdaptationTracker` (alpha 0.2) in the side's planning state (dies with the world): lane success from packages / probes, utilization sampled at 1 Hz (legal target in reach, fired within 2.5 s), kills by seen group; Hard+ only (216). Support effectiveness: API (`SupportResult`) not yet fed | **changed / scaffold (support EMA)** |
| 158 | Anti-repetition 25-50 %, decay 30-60 s, no randomness | `RepetitionMemory`: plan kind x target cell, penalty 0.25-0.5 by failure severity (losses / 60 %), half-life 45 s; a failed package (executed, not taken, heavy losses) and a light 0.2 on enemy-rise / flank-blocked aborts (`OBJECTIVE_PLAN_FAILED_REMEMBERED`) | **changed** |
| Part M | Bait chase, artillery camping, air-heavy, fixed-route ambush, tower defence -> shorter leash, more recon, alternate route, counter-battery / SEAD, procurement, smoke | bait: a chasing squad losing 25 % marks the cell; 2 marks -> P3 pursuit leash x0.6 there; camping (6 shells from one battery estimate) -> barrage on the estimate at 0.8 x P3's confidence; air share >= 35 % -> AA cards +1.5; repeated losses at one cell twice (> 20 s apart) -> scout-before-commit unknown share +0.15; >= 3 towers seen -> guns / breachers +1; alternate route = P3's failed-route penalty (kept). Observed data only, no cross-match | **changed** |
| 132 | Probe 8-15 % power; low resistance -> ExploitWindow + main shift; AT / ambush -> threat, artillery / flank / SEAD; blocked -> no main army; not suicide | Hard+: the most unknown lane (direct / left / right of the main effort) not yet probed; a squad of 8-15 % power (fast first); `ProbeRules.Judge` on seen strength, AT threat, losses, progress (8 s no progress = blocked), 20 s limit; exploit -> window + lane Exploit (plans and flank options +10) and the plan's commitment is cut; threat -> lane Hot (plans +0.5 uncertainty, plan B gain); blocked -> lane Blocked (flank options -50, plans invalid, route version up -> flank packages abort). Envelope 0.9 x reach from the nearest known enemy (`OBJECTIVE_PROBE_*`, `ROUTE_PROBE_LANE_BLOCKED`) | **changed** |
| 133 | Feint only Hard / VH or fitting tactic; own utility (secondary, spotting, flank, turret arc); success only on observed redeploy | `FeintRules`: utility 0.4 secondary + 0.3 x unknown + 0.3 flank threat + 0.2 pins a seen static defence's arc, >= 0.5; Hard+ or a pincer / flank-heavy tactic on Normal; never Easy or under urgency >= 0.75; a small squad (<= 20 % power) while the package waits; success = the watched objective's seen strength -25 % and more seen at the feint -> window + the package goes now; ends at 25 s (`OBJECTIVE_FEINT_*`) | **changed** |
| 174 | SEAD package: suppression -> ingress -> egress; failed -> delay or reroute | Hard+: strike aircraft (bombers / attack) whose goal's known AA threat / strength >= 1 and a SEAD card in the deck: hold at an ingress point 50 m outside the SAM's reach, `SupportWanted` asks SEAD on it; go (staggered 150-400 ms) on an AA-down window or a SEAD used near within 15 s; after 12 s: reroute by the lowest-risk approach (risk ok), else one more 12 s delay, then as before (`AIR_SEAD_*`) | **changed** |
| 175 | AirRiskMap: low-risk ingress, egress, no repeated pass through the strongest SAM | `AirRules.LegRisk` (mean + half max of the AA threat layer over 6 samples); five approaches (0, +-60, +-100 deg) on Hard+ when 30 % less risky; a second pass through the strongest known SAM's reach forces a detour; egress after firing inside AA >= half its strength: lowest-risk of five ways away from the SAM (`AIR_RISK_ROUTE`, `AIR_EGRESS_LOW_RISK`) | **changed** |
| 176 | CAP zones: boss, main force, objective, approach corridor; no chase to the edge | zones (merged within 40 m): own boss, strongest squad, objective, midway to the nearest enemy air group; fighters round-robin by id; outside 1.5 x 60 m -> back; patrol point turns every 8 s (`AIR_CAP_*`). Normal+ | **changed** |
| 177 | TTK; 1-2 attackers, never 6 on a weak target | seen aircraft by strength: attackers = ceil(hp / (dps x 4 s)) clamped 1-2, nearest free fighters whose zone it is in; an unneeded chaser returns to CAP (`AIR_TARGET_HANDOFF`) | **changed** |
| 178 | Bomber waits for value, route, blast deconfliction, SEAD window; not on trivial targets unless urgent | `BomberP4`: seen ground strength under blast + 4 m >= 8, route risk / strength <= 1.5, no friend within blast + 8 m and no other drop reserved there (6 s), SEAD ready; else retarget to the best seen cluster passing all, else loiter at the own centre up to 30 s then go as before (`AIR_BOMBER_*`) | **changed** |
| air | Predictive air interception | an assigned fighter out of reach of a moving aircraft attack-moves to P3's `PursuitDiscipline.Intercept` point (6 s horizon, fades with age) (`AIR_INTERCEPT_PREDICT`) | **changed** |
| 179 | Boss part score: disabled DPS, disabled APS / shield / radar, phase utility, kill progress; functions are game rules | `BossSystem.ChoosePart` for AI sides: 50 x silenced DPS share + 25 utility part (kind / skill named aps, shield, radar, jammer, sensor, dome) + 40 x phase (charging big attack 1, its part 0.3, lock part 0.6, skill part 0.2) + 30 x (1 - part health share) + 0.25 x the old shooter danger (so AA still hunts AA parts) - distance; lock / player focus rules unchanged; the commander logs its top part (`BOSS_WEAKPOINT_UTILITY`). Players keep the old choice | **changed** |
| 180 | React to warnings the player sees; difficulty = delay / quality only | P2's dodge on the public `Warnings` kept; quality by difficulty = sector count 3 / 3 / 4 / 5 and pattern learning (Hard+); delay = the skill's reaction delay + stagger | **kept / changed** |
| 181 | 3-5 safe sectors, squad spread, not one point | `EscapeSectors.Assign`: sectors oriented on the boss-to-ring axis, exit 6 m outside the ring, blocked = off map / unwalkable / inside another warning, capacity ceil(n / open), 4 m side by side; planned once per squad and warning; fallback radial (`BOSS_TELEGRAPH_ESCAPE_SECTOR`) | **changed** |
| 182 | Replan on target dead, route blocked, lethal warning, support lost, objective version; not on small changes | `TriggerP4` (cluster gone, guns lost, a new big / strike warning on the staging or a member: the execute time waits for it to land); route / objective changes go through 183 / 155; otherwise only at the end of the commitment window (`OBJECTIVE_PLAN_INTERRUPT_REPLAN`) | **changed** |
| 183 | Package stores route / objective / cluster version, support; invalidate only on important change | `PlanDependencies` (route = lane version + nav grid version; objective = 15 m cell + owner; cluster centre / strength; guns / air); `Broken`: route, objective, strength x1.5, centre > 25 m, plan-B guns | **changed** |
| 184 | Commitment: turret 1-1.5 s, spot 2-3 s, route 4-6 s, package 6-12 s; emergency breaks | package 6-12 s (hash of main squad and package), route 4-6 s (+5 points to the current flank side); turret 1.5 s (P0-A `targetStickSeconds`) and firing spot (P2 commit) kept; dodge / overwhelmed run before scoring (break them) | **changed / kept** |
| 204 | Pressure budget: delay non-critical ability while bomb / volley / strike active; pacing, not a nerf | `BossSystem.PressureDeferP4`: >= 2 of the boss side's big attacks charging / strikes incoming -> wait 1.5 s (3 s max per cast), the wait comes off the next cooldown; scripted bosses never wait (`BOSS_PRESSURE_BUDGET_DEFER`). Applies to big attacks (skills / bombard keep their own cadence) | **changed** |
| 214 | Improve escape choice after the first repeated telegraphed pattern; no hidden future | `PatternMemory`: a big zone of the same boss within 8 s of its first zone (seen, not inside it) counts its bearing (8 bins, boss frame); next time escape sectors that way cost +25 m x frequency. Hard+ (`BOSS_PATTERN_LEARNT`) | **changed** |
| 215 | Radio cue / gesture / escort animation; no gameplay bonus | `TeamPlanning.Cues` (attack_go, flank, probe, feint, escape; 10 s per kind, 32 kept) + `SQUAD_CUE` lines; the Game presentation does not read them yet | **scaffold** (presentation hookup for the lead / UI lane) |
| 216 | Easy no feint, 1 plan, simple diversity; Normal sync / fix-flank / CB / 2 plans; Hard probe, feint, adaptation, SEAD, 3 plans; VH all, still fog-fair | `DifficultyGate` from `AiSkill.Level` (new, set by `AiSkill.For`): plans 1-4, depth 1/1/2/2, probe / adaptation / SEAD / patterns Hard+, CAP / bombers Normal+, feint Hard+ (or a fitting tactic on Normal). Easy's single plan is "attack now", so P3's fix-and-flank is undone on Easy; P3 route diversity stays at every level | **changed** |
| 217 | 150-400 ms deterministic stagger, hash(unit, event) | `HumanStagger.Delay` on the dodge (per member) and the SEAD go (per aircraft); commitment lengths from the same hash | **changed** |
| P3 a | One owner per gun (P3 fire missions vs `TacticalAi.DirectArtillery`) | `IntentOwnership` (priority Emergency > FireMission / Scoot / AirPackage > Tactical): fire missions claim 10 s, scoots 8 s; `DirectArtillery` per gun (`DirectGun`) runs only its safety branches (threat inside minimum range, siege self-defence, kiting) while a mission owns the gun, and claims the guns it orders for 2 s; P3's stale-target drop leaves a gun another owner holds (`ARTILLERY_ORDER_OWNER`) | **changed** |
| P0-B 18 | CP back before an expected boss phase; stop buying when the forecast says enough | `HoldPurchaseP4` in `TryPlanned` / `BuyThroughDirector`: whole army vs all known enemies (x1.25), own >= 2 x known, enemy <= 30 % after the forecast, >= 3 known -> hold (30 s on / 10 s off), never with < 4 units, under fire or at the bank cap; a seen boss within 8 % above its next phase mark -> keep 30 % of the bank (25 s max) (`PURCHASE_HOLD_FORCE_ENOUGH`, `PURCHASE_RESERVE_BOSS_PHASE`) | **changed** |
| 225 | Metrics | `PlanningMetrics` (plans, switches, holds, replans, cache hits, probes / success, feints / success, windows, aborts, repeat penalties, SEAD / reroutes, egress, CAP returns, handoffs, intercepts, bomber waits / retargets, escape plans, pattern follow-ups, gun ownership blocks, buy holds, cues); `unitClassUtilization` = `AdaptationTracker.Utilization` | **changed** |
| Part O | Reason codes | `P4Reasons`: OBJECTIVE_PLAN_*, OBJECTIVE_PACKAGE_ABORT_*, OBJECTIVE_PROBE_*, OBJECTIVE_FEINT_*, OBJECTIVE_OPPORTUNITY_WINDOW, OBJECTIVE_RESERVE_FORECAST_COLLAPSE, ROUTE_PROBE_LANE_BLOCKED, AIR_*, BOSS_*, ARTILLERY_ORDER_OWNER / ADAPT_CAMPING_COUNTERBATTERY, PURCHASE_HOLD / RESERVE / ADAPT_*, TARGET_ADAPT_BAIT_LEASH, SQUAD_CUE | **changed** |
| Part P | Budget | commander pass 1 Hz; forecasts are closed-form (two half-steps), cached 0.75 s, built once per evaluation (O(units x mounts x 6 armour levels)); plans re-scored only at commitment ends / triggers; utilization O(units x seen contacts) at 1 Hz; air preparation once per pass; escape plan once per squad and warning; no per-step search | **changed** (the lead measures in the 48v48 gate) |

## Regression rows (tests written, not run)

`Assets/MachineBrigade/Tests/EditMode/AiMasterP4Tests.cs` (category `AIMasterP4`, 15 tests)

| Row | Test |
|---|---|
| 224 forecast (frontal bad, flank good -> flank) | `S224_Forecast_FrontalBadFlankGood_TheFlankPlanWins` |
| 154 plans / gating / hold | `S154_ShallowPlans_DifficultyGatesTheCandidatesAndAHoldBeatsASuicide`, `S153_Forecast_EnoughStopsBuyingOnlyOnAKnownWeakEnemy` |
| 155 forecast abort | `S155_ForecastAbort_AnEnemyEstimateRiseAbortsBeforeContactOnly_NeverAUnitsHealth` |
| 158 anti-repetition | `S158_AntiRepetition_AFailedPlanLosesTwentyFiveToFiftyPercentAndTheMemoryFades` |
| 132 probe utility | `S132_ProbeAndExploit_ASmallForceJudgesTheLaneAndNeverSuicides` |
| 133 feint utility | `S133_ConditionalFeint_NeedsItsOwnUtilityAndOnlyASeenRedeployIsASuccess` |
| 181 boss telegraph escape sectors | `S181_BossTelegraph_EscapeSectorsSpreadTheSquadAndSkipBlockedOnes` |
| 214 pattern learning | `S214_PatternLearning_AFollowUpSeenOnceMakesThatSectorCostMoreNextTime` |
| 224 utilization / Part M bait | `S224_Utilization_AClassThatCannotHitWhatIsInReachBuysLessAfterTwentySeconds` |
| 204, 217, 184, P3 a, 179, 216, 174-178 | `S204_*`, `S217_*`, `P3Leftover_OneOwnerOrdersAGunAtATime`, `S179_*`, `S216_DifficultyGating_AndAirRules` |

The rows are unit tests on the rule classes; whole-battle checks (a probe really shifting the main effort, a SEAD package
holding strikers, escape sectors under a boss salvo) are the lead's sweeps with `ai.planning.enabled` on / off.

## Risks for the lead's runs

1. Package shape changes: Easy now always attacks frontally (one plan); Normal+ may undo P3's fix-and-flank (plan A) or add one
   (plan C); Hard+ may delay execution 4 s for the guns (plan B); Very Hard may hold the primary squads (plan D, pre-contact,
   never under urgency >= 0.75). Watch first-contact timing in AiScenarioTests.
2. Air: fighters now patrol CAP zones and are handed out 1-2 per enemy aircraft (they no longer follow the ground army's attack
   moves); bombers may loiter up to 30 s for a worthwhile target; strike aircraft may hold 12-24 s for SEAD when the deck has a
   SEAD card. Air-attack tests that time the first strike may move.
3. Boss pacing shifts big-attack timing by up to 3 s when the boss side has two dangerous actions active (cooldown compensated);
   scripted bosses unchanged. AI shooters aim at boss parts by the weakpoint utility (players unchanged).
4. Procurement: Hard+ AI may hold CP while the forecast says its force is enough (30 s on / 10 s off) or while a seen boss is
   near a phase; utilization lowers scores of classes that never fire at what is in reach.
5. `DirectArtillery` was split into a per-gun method (`continue` -> `return`, same branches) to snapshot orders; behaviour is
   unchanged except while a P3 fire mission / scoot owns the gun.
6. Dodge: members inside a ring go to sector exits (spread, 3-5 sectors) instead of the nearest radial point, each after its own
   150-400 ms stagger on top of the reaction delay.

## Not done / for later lanes

- Cue presentation (215): the cues are recorded; no radio line / gesture is shown yet.
- Support effectiveness EMA (157): API only. Opportunity "gate opens" uses seen wall rubble (no gate state exists).
- Pressure budget on boss skills / bombard / cruise mechanisms (only big attacks wait).
- CAP and air packages for aircraft inside squads (none today: squads are ground-only).
