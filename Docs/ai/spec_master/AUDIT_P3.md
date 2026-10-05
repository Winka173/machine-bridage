# AUDIT P3 — coordination (lane A, 05/10)

Branch `feature/ai-p3` (worktree MachineBrigade-art), on top of P0-A/B/C, P0-D + P1 and P2. Source of truth:
`Machine_Brigade_AI_Behavior_MASTER_FINAL.md` sections 123-151, 169-173, 199-201, 205-213, 218-227, Part O / P, plus the items P2
left (AA coverage optimiser, intercept arrival filter, two-objective splits, traffic-aware flank costs). Not run here (no Unity,
no tests, no sims): the Sim builds (`dotnet build Tools/simbuild/Sim.csproj`, 0 errors); `AiMasterP3Tests.cs` compiles against
the Sim + NUnit 3.13 (scratch project, `GameContent` stubbed).

Legend: **changed** = new or altered behaviour; **kept** = the existing code already does it (Part A); **scaffold** = API in
place, behaviour partial or for a later lane; **P4** = probe / feint / forecast lane.

Switch for the lead's sweeps: `ai.coordination.enabled` (false = P2 behaviour exactly: every hook returns early). 116 new keys
under `ai.coordination / memory / confidence / routes / attackSync / board / fireMissions / pursuit / rangeMargin /
reserveRelease / objectives / coverage / stance` (`SimTunables.AiMasterP3.cs`, registered in `SimTunables.Pack2.cs`).

## Architecture

- `world.Coordination` (`SimWorld.P3.cs`, `AI/P3/Coordination.cs`): created by the first AI commander; one `TeamCoordination`
  per AI side (memory, frontline, planned action board, counter-battery tracker, route book, counterattack windows, metrics).
  `SimWorld.Emit` feeds it two event kinds only (own / seen-enemy deaths; indirect rounds fired, queued until they land and
  observed only by a side that had sight of the impact area). Player sides never get one, so their units are untouched.
- Commander (`AI/P3/Commander.P3.cs`): `CoordinateP3` runs right after P2's `AssignP2` (1 Hz) and adjusts the tasks it gave.
- Squads (`AI/P3/SquadLayer.P3.cs`): factors appended to `Score`'s options, small overrides in `Execute` (staging, pursuit,
  fix envelope), `Focus`, `Stance`, `Units`, `ChooseFormation` (2-4 Hz, existing cadence).
- Targeting (`Combat/CombatSystem.P3.cs`): `P3Worth` on the existing score (after P28Worth); `Acquire` reserves planned damage.
- Pure rules (`AI/P3/CoordinationRules.cs`): confidence, route cost, sync planner, scout / fix-and-flank / pursuit / reserve /
  objective / range / stance / scoot / focus rules — what the tests exercise.

## Section -> code -> status

| § | Spec | Code | Status |
|---|---|---|---|
| 124 | FrontlineModel / FrontSegment (centre, normal, pressures, stability, width, confidence); no hidden enemies | `FrontlineModel.Rebuild` from the World Model's front cells (connected runs), own/enemy weight round each (remembered threat counts for the enemy = recent combat), width narrowed by MapTopology chokes, stability = seconds in place / 10, confidence = contact confidence; no front cells: provisional segment between own centre and objective (0.3). `Depth`, `Behind`, `Weakest`, `PositionalAdvantage` | **changed** |
| 124 uses | support behind the line, reserve to the breaking point, flank not just longer | scoot spots and AA coverage spots stay behind (`Behind`); reserve rank 2 "breakthrough" from segments; flank option +5 "frontWeak" | **changed** |
| 125 / 219 | TacticalConfidence 0.35/0.20/0.15/0.10/0.10/0.10, not morale; bands 0.70 / 0.45 / 0.30 | `TacticalConfidence.Compute`; inputs in `SquadLayer.ConfidenceOf` (local own/enemy ratio, AT/AA coverage vs the enemy mix at the goal, guns reaching the goal / AA / repair near, frontline positional advantage, commander urgency, unknown share x contact confidence). Used: Attack (+-points, "noCommit" under 0.30 unless urgent), Flank (-points under 0.45), Hold (+ under 0.45). No health input anywhere | **changed** |
| 126 | Dynamic frontage: required > usable -> other route, reserve, stagger, fire support, no more through one choke | `FrontageP3`: primary attackers by strength, usable = nearest segment width / default 60 m / MapTopology bottleneck on the way; overflow squads get a flank side if one fits (`ROUTE_FRONTAGE_SECOND_ROUTE`), else a staggered wave (6 s per wave, `ROUTE_FRONTAGE_STAGGER_WAVE`); the reserve stays P2's; fire support = the package's prep | **changed** |
| 127 | PathCost = Distance + Threat + Congestion x0.8 + Occupancy x0.5 + RecentLosses x0.7 + UnknownRisk | `RouteDiversity.Cost` for the squad's three corridors (direct, left, right flank); occupancy from `RouteBook` (bookings 8 s, 25 m); repeat penalty 0.35 / half-life 45 s on a route that cost the squad 40 % of its strength (`ROUTE_FAILED_REMEMBERED`); cost difference -> option points | **changed** |
| P2 76 | Traffic-aware flank costs (congestion / exposure) | `CongestionAlong`: P1 passages near the way by arrivals per lane, crowded narrow cells (World Model chokepoints) | **changed** |
| 128 | Temporal influence, half-lives 8-12 / 15-25 / 30-60 s, ConfirmedAbsent decays fast | `TacticalMemory` threat cells (10 / 20 / 45 s by kind), x0.25 per refresh when the cell is seen empty; decay on read | **changed** |
| 129 | Recent-death danger: value x exp decay; scout / artillery / avoid kill zone; no panic | `AddDeath` from own losses (CP value), half-life 18 s, 20 m; route cost, scout demand, bait leash; never a state change | **changed** |
| 130 | Unknown != safe, tactic modifier | `UnknownShare / UnknownAlong` (not seen 20 s, no known AT); modifier blitz 0.3 / balanced 0.6 / attrition 1 / ambush-recon 1 | **changed** |
| 131 | Scout before commit 2-6 s; timeout commits | at package build: unknown >= 50 % or death danger >= 1 round the objective -> a fast squad (not main / flank) or a free recon vehicle goes to look; the package waits clamp(scout ETA, 2, 5 s); urgency >= 0.75 or a Showdown timer < 60 s skips it (226); `OBJECTIVE_SCOUT_BEFORE_COMMIT`, `OBJECTIVE_SCOUT_TIMEOUT_COMMIT` | **changed** |
| 132 / 133 | Probe-and-exploit, feint | — | **P4** (PLAN: probe / feint / fix-flank planning lane); route memory and windows are its inputs |
| 134 | Fix-and-flank: stable cluster, >= 2 routes, enough power; Fix inside its envelope | `FixAndFlank.Viable` at package build; the flank squad gets the flank side (P2's pincer factor + "packageFlank" 15), the main becomes Fix and never goes closer than 0.85 x reach (`FixP3`) | **changed** |
| 135 / 220 | Synchronized ETA; tolerances 3 / 4 s, artillery 1-3 s before | `SyncPlanner`: ETA = distance-to-contact x 1.25 / slowest speed; execute delay = latest ETA, prep +2 s, air within 4 s; a squad early by more than 3 s stages (capped 15 s) | **changed** |
| 136 | AttackPackage (main, fix, flank, reserve, prep, air, target, executeAt) | `AttackPackage` built by the commander when the window is open on a fixed objective; ends 25 s after execute, aborted on window shut / target moved / main gone (`OBJECTIVE_PACKAGE_*`) | **changed** |
| 137 | Staging: reachable, wide, outside known direct fire, no choke / spawn, near the split; sub-zones | `StagingP3`: outside the known reach round the target + 12 m, 5 bearings, same ground component, off chokes / passages / lanes / spawn exit boxes, least AT + artillery threat; sub-zones 14 m apart; squads stage there (watchdog reason WaitingFormation), `OBJECTIVE_SYNC_STAGE / GO` | **changed** |
| 138 / 221 | PlannedActionBoard | `PlannedActionBoard`: damage, repair, coverage, smoke, fire-mission guns, committed power per objective. Choke movement reservations stay P1's passages | **changed** |
| 139 | Planned damage > 1.15 x hp: a unit that has not fired picks another | `Acquire` reserves one cycle of expected damage (released on change, timeout cycle + 1.5 s); `P3Worth` x OverkillFloor when planned (others) + in flight > 1.15 x hp, except P0-A's exemptions and a strong squad focus. AI sides only | **changed** (P0-A's in-flight rule kept) |
| 140 | Repair reservation | `TacticalAi.RepairTargetP3`: engineer to the largest unreserved need within 60 m of the front; reserves rate x 8 s | **changed** |
| 141 | AA coverage assignment Boss / MainForce / Artillery / Objective | `CoverageP3` (every 2 s, only with enemy air known): one AA per asset first, then by worth / cover count; `v.P3CoverAt` makes aircraft over its asset x1.4, others x0.8; radar-lost AA excluded (P2 F3) | **changed** |
| 142 | Smoke deconfliction (area, start, end, purpose) | `SupportWanted` skips a smoke where a mission / cloud covers it; accepted cards become missions (`NoteSupportP3`); new purpose AssaultObjective smoke on the approach while a package goes in against known AT | **changed** |
| 143 | Fire mission scheduler (Prep, Suppress, CounterBattery, AreaDenial, Finish); not all guns on one weak target; no stale barrage | `FireMissionP3` per gun outside squads: CounterBattery on a seen battery, Finish on a near-dead seen target, max 2 guns a target, preferred range band; an Attack on a target unseen > 4 s is dropped (`ARTILLERY_STALE_TARGET_DROPPED`). Prep = package timing; Suppress / AreaDenial: TacticalAi's cluster / defence shelling kept | **changed / kept** |
| 144 | Counter-battery: estimated origin with confidence, error, timestamp; more shots -> more confidence; no magic reveal; unseen -> area fire if allowed | `CounterBatteryTracker`: per observed shell an estimate off by a hashed offset within 20 % of the flight (>= 8 m); merged per battery (precision mean, error / sqrt(shots), confidence 1 - e^(-n/2), half-life 20 s). Guns cannot fire at ground, so unseen batteries get a support Barrage (area fire) at >= 0.7 confidence and <= 25 m error (`ARTILLERY_COUNTERBATTERY_AREA_FIRE`) | **changed** |
| 145 | Shoot-and-scoot after 2-4 salvos or CB threat, 12-30 m, not into choke / frontline / other reservation | `ArtilleryP3` + `ScootP3`: salvos 2-4 and distance 12-30 m by gun id; threat = observed enemy impacts within 25 m (8 s) or an enemy counter-battery radar in reach; spot off chokes / passages, 15 m behind the front, not booked (P2 positions, P1 `CanPark`) | **changed** (old 3-shot rule kept with P3 off) |
| 146 | Predictive interception, clamped horizon, uncertainty with age | `PursuitDiscipline.Intercept` (6 s horizon, fades over 4 s unseen) for a moving target out of reach | **changed** |
| 147 | Cutoff instead of chase | fast squads: a MapTopology choke on the enemy group's way (confidence >= 0.6, 20 s ahead) reached first and sooner than the intercept | **changed** |
| 148 / 223 | Max seconds / distance / objective leash; AA no chase | `PursuitP3` with `PursuitDiscipline.Check` (20 s / 60 m; AA squads 10 s / 40 m; urgency > 0.75 drops non-threats); back to the anchor, no retry for 10 s. P2's doctrine leash stays underneath | **changed** |
| 149 | Stances HoldFire / ReturnFire / Defend / AttackAnything | `StanceRules.For` per member each look (ambush HoldFire = P2's AiHoldFire; recon ReturnFire; support Defend; assault AttackAnything); ReturnFire = score 0 unless the target shoots at the side or the unit was hit within 3 s (watchdog reason HoldFireOrder) | **changed** |
| 150 | Opportunity fire, hull route unchanged; boss turrets | P0-A (A224 test) and P0-C's boss weapon director; HoldFire beats it (AiHoldFire) | **kept** |
| 151 | Range margin 3-6 / 5-10 / ~5 / 5-8 % | `RangeBands` (4.5 / 7.5 / 5 / 6.5 %): scoot spots and fire missions | **changed** (squad standoff bands stay the role data's 0.x shares) |
| 169 | Coverage optimiser (AA, EW, repair, radar) | `CoverageSpot`: 8 spots round the asset + here, value covered - exposure - congestion - redundancy, behind the front; moves free (non-squad, idle) AA. EW / repair aura / radar placement stay TacticalAi's DirectSupport | **changed (AA) / scaffold (EW, radar)** |
| 170 | Reserve 15-25 %; release 1 HQ/boss, 2 breakthrough, 3 primary collapse, 4 exploit, 5 secondary; never into a won fight | P2's `ReserveTrigger` -> `ReserveReleaseP3` when P3 is on: ranked candidates, `ReserveLogic.Pick` skips own/enemy >= 2 (`OBJECTIVE_RESERVE_RELEASE`, `OBJECTIVE_RESERVE_KEPT_FIGHT_WON`); Endless keeps HQ only (I16) | **changed** (share kept P2) |
| 171 | Economy of force | `EconomyOfForceP3`: with the primary decisive, secondaries keep enemy-there x 0.8 (<= 30 % of the army, at least one squad); the rest goes primary | **changed** |
| P2 22 | Two simultaneous objectives | a primary squad of 6+ splits (P2 `Split`) when a threatened secondary has nobody (30 s cooldown, `SQUAD_SPLIT_TWO_OBJECTIVES`) | **changed** |
| 172 | Sunk-cost reset | losses near the objective (half-life 90 s) x clamp(enemy / own, 0.5, 3) > 60 CP x (1 + urgency) -> no reinforcement there for 30 s; its squads take the secondary or hold 20 m back; never under urgency >= 0.75 | **changed** |
| 173 | Threat-specific posture | artillery: dispersion (213) + scoot + counter-battery; AT: heavy squads -0.5 pts frontal / +0.3 flank; air: -0.5 pts outside an AA umbrella (40 m); splash: P2 packets / spread; stealth: unknown-ground cost raises scouting | **changed** |
| 199 | Focus-fire coordinator | `FocusShareP3`: the squad focus weight full only on a high threat / boss part / near kill (< 30 %) / strategic (high-value) target, else x0.3 (`TARGET_FOCUS_FIRE / TARGET_SPREAD_FIRE`) | **changed** |
| 200 | Target handoff by suitability, lock window | `UnitsP3`: a mate 1.6x better suited (DamageSystem.Estimate) and free takes the target (x1.5), the old owner avoids it (x0.4), 2.5 s lock (`TARGET_HANDOFF_SUITABILITY`) | **changed** |
| 201 | Multi-weapon platform director | `MountFit` on secondary mounts: light guns x0.4 on heavy / boss, x1.3 on light / recon / drones / air; area launchers x1.3 on groups / structures; AA mounts x1.3 on air. Hull bearing per mount: P0-A / P0-C | **changed** |
| 205 | Ambush: hold fire, open at 55-70 % range, when detected or a high-value target passes; synchronized volley with anti-overkill | `StanceP3` (share clamped to 0.55-0.70, high-value inside 85 % reach, hit = detected; every holding ambush squad within 60 m opens the same look); the board spreads the opening volley | **changed** |
| 206 | Bait resistance without cheating | death memory round the chase shrinks the pursuit leash (x(1 - 0.5 x danger), >= 0.4), route cost and scout demand rise | **changed** |
| 207 | Deadline-aware assignment (+ P2 I9 intercept arrival filter) | `DeadlinesP3`: deadline = Showdown time left / enemy capture time at the observed rate of the public capture bar / an enemy group's ETA there for intercept doctrines; a slow squad whose ETA > deadline x 1.1 takes the next objective or holds, a fast squad takes it (`OBJECTIVE_DEADLINE_*`) | **changed** |
| 208 / 209 | Time-to-value, capability replacement | — | P0-B (procurement), not this lane |
| 210 | Objective ownership prediction / early rotation | capture-rate sampling is in `DeadlinesP3`; rotation not done | **scaffold** |
| 211 | Defence in depth 2-3 lines, next line on objective lost | `DefenseInDepthP3`: 3 lines at 0 / 30 / 60 % towards home; next line after the point is lost or its line is held by the enemy for 5 s; back when retaken; hold tasks follow (`OBJECTIVE_DEPTH_*`). Never a health trigger | **changed** |
| 212 | Counterattack window | observed enemy losses (seen dying) within 40 m / 6 s >= 35 % of the local power -> 8 s window: attack option +12, reserve rank 4 | **changed** |
| 213 | Anti-artillery dispersion timing | observed enemy impacts near the squad (8 s) or a live warning: Spread kept, Regroup option -40 (`FORMATION_DISPERSE_HOLD`); P2's warning dodge kept | **changed** |
| 218 | Advanced tunables | all spec values used where given (frontline 1 s, half-lives 10 / 45 / 18, scout 5 s, sync 3 / 4 / 2, repeat 0.35 / 45, 1.15, scoot 2-4 / 12-30, reserve share stays P2's 0.15-0.25); forecast / probe / utilisation keys are P4 / P5 | **changed** |
| 225 | Metrics | `TeamCoordination.Metrics` (packages created / aborted, sync stages, max contact delta, fix-flank, scouts, overkill prevented, duplicate repair prevented, smoke deconflicted, CB missions / strikes, scoots, stale drops, pursuit aborts, intercepts, cutoffs, handoffs, reserve releases / kept, missed-deadline orders, sunk resets, depth changes, windows, route repeats, economy moves, splits) | **changed** |
| 226 | Conflict rules | feasibility first (P3 factors sit after the hard filter); traffic over formation (P1 untouched); HoldFire over opportunity fire; emergency objective over scout; short timer drops scout; boss no-reverse untouched; public telegraphs only | **kept / changed** |
| Part O | Reason codes | `P3Reasons`: OBJECTIVE_*, ROUTE_*, ARTILLERY_*, TARGET_*, SUPPORT_*, FORMATION_*, SQUAD_* lines in `world.AiLog` | **changed** |
| Part P | Budget | commander pass 1 Hz (frontline 1 Hz, coverage 0.5 Hz), squads at their interval, memory decays on read, board / book bounded, P3Worth = dictionary lookups; no per-step deep search | **changed** (the lead measures in the 48v48 gate) |

## Regression rows (tests written, not run)

`Assets/MachineBrigade/Tests/EditMode/AiMasterP3Tests.cs` (category `AIMasterP3`, 18 tests)

| Row | Test |
|---|---|
| 224 death memory | `S224_DeathMemory_ASquadKilledAtTheChokeMakesTheNextScoutOrTakeTheOtherRoute` |
| 131 scout-before-commit | `S131_ScoutBeforeCommit_UnknownGroundAsksAScoutAndTheWaitIsCapped` |
| 134 fix-and-flank | `S134_FixAndFlank_NeedsAStableClusterTwoRoutesAndPowerAndTheFixDoesNotCloseIn` |
| 224 counterbattery confidence | `S224_Counterbattery_ShotsFromOneAreaRaiseConfidenceShrinkTheErrorAndMakeAMission` |
| 145 shoot-and-scoot | `S145_ShootAndScoot_AfterTwoToFourSalvosOrAtOnceUnderCounterBatteryThreat` |
| 224 pursuit leash | `S224_PursuitLeash_ADefendingSquadReturnsToItsObjectiveWhenTheLeashRunsOut`, `S146_S147_InterceptLeadsTheTargetAndCutoffOnlyWhenItIsSooner` |
| 207 objective deadline | `S207_ObjectiveDeadline_ASlowSquadIsNotSentInVainAFastOneIs` |
| 212 counterattack opportunity | `S212_CounterattackOpportunity_OpensOnlyAfterObservedHeavyEnemyLosses` |
| 224 sync flank | `S224_SynchronizedEta_MainStagesAboutFourSecondsAndContactIsWithinThree` |
| 224 route diversity / reserve | `S224_RouteDiversity_TwoEqualSquadsOnTwoEqualCorridorsSplit`, `S224_Reserve_PrimaryCollapseReleasesItAnEasySecondaryFightDoesNot` |
| 139-142, 125, 149, 151, 171, 172, 199, 211 | `S139_*`, `S140_S142_*`, `S125_*`, `S149_S199_*`, `S151_*`, `S171_S172_S211_*` |

The rows are unit tests on the rule classes the commander / squads call; whole-battle checks (e.g. a squad really staging in a
48v48 run) are the lead's sweeps with `ai.coordination.enabled` on / off.

## Risks for the lead's runs

1. Attack timing changes: with two or more primary squads and an open window on a fixed objective, early squads stage up to
   15 s (sync), + up to 5 s for a scout. Watch AiScenarioTests / play tests that time first contact.
2. Planned damage spreads AI fire more (x OverkillFloor on reserved targets): kill times on single heavy targets may grow;
   the squad focus (strong only on threats / near kills / bosses / high value) is exempt.
3. ReturnFire recon units no longer start fights (score 0 on non-hostile targets).
4. Reserve now commits on rank 1-5 reasons and never into a won fight; Opportunity events no longer commit it (P2 did via
   threats only, so close to before).
5. Artillery: fire missions issue Attack orders on seen batteries / near-dead targets and drop stale Attack orders; TacticalAi's
   DirectArtillery still runs for the same guns (both obey "no order change while attacking").
6. Sunk cost (60 CP value) and deadlines reassign squads away from the main objective; check Conquest / Showdown win rates.
7. Counter-battery estimates use the shell's true origin only through a bounded deterministic error (no reveal); a support
   Barrage is the only unseen area fire (guns have no ground-attack order).

## Not done / for later lanes

- Probe-and-exploit, feint (132-133), combat forecast (152 / 222), counterfactual plans: P4.
- Objective ownership prediction with early rotation (210): only the capture-rate sampling.
- Coverage optimiser for EW / repair aura / radar: AA only.
- Squad standoff bands with range margin (151): kept on the role data shares (already 0.x of reach).
