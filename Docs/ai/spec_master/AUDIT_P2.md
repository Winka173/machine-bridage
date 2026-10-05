# AUDIT P2 — role / mode intelligence and squad management (lane C, 05/10)

Branch `feature/ai-p2` (worktree MachineBrigade-art3). Source of truth: `Machine_Brigade_AI_Behavior_MASTER_FINAL.md` (MASTER
RULES, Part A kept). Lane scope: Part B (all roles), Part I (every mode), Part J, Part D, Part E, Part F, Part G, sections 19-27,
68-76, 86 (as far as no traffic is needed), 97, 159-162, Part O codes of this lane, regression rows R4-R7 (+ the ladder side of
R2/R3) and section 112. Not run here (no Unity, no tests, no sims): the Sim builds (`dotnet build Tools/simbuild/Sim.csproj`,
0 errors), the new test file compiles against the Sim + NUnit 3.13 with stubs for `GameContent` / `TestWorlds` (scratch).

Legend: **changed** = new or altered behaviour; **kept** = the existing code already does it (Part A); **scaffold** = API /
data in place, behaviour belongs to a later lane; **deviation** = differs from the letter of the spec, why given.

## Section -> code -> status

| Spec | What it asks | Code | Status |
|---|---|---|---|
| B1 | Generic product score, infeasible removed first | Existing `CombatSystem.Score` (P0-A's hard filter first) x `P0AWorth` x `DoctrineWorth` x `P2ModeWorth` | **kept** (P0-A) |
| B2 / B3 | Breacher / siege | P0-A's `DoctrineWorth`; P2 ladders return 1 for these roles | **kept** (P0-A) |
| B4 | TD / rail: Armour5 > Armour4 > heavy > boss > MBT > medium > light last | `CombatRoleDoctrine.Worth` (TankDestroyer), main weapon only (`CombatSystem.P2RoleWorth`) | **changed** |
| B5 | MBT / heavy: threat to self / squad, heavy, TD on our heavies, objective, structure, light | MainBattle ladder; "squad" = an enemy aiming at one of ours within 15 m (`ThreatensNear`) | **changed** |
| B6 | IFV / light: light, recon, drone / low air, fragile support, medium; heavy only last | LightCombat ladder | **changed** |
| B7 | AA: aircraft on a protected asset, bomber / strike, gunship, fighter, drone; no ground chase | AntiAir ladder (asset = Part H's ThreatToObjective > 0); ground x lastResort unless self-defence | **changed** |
| B8 | Artillery: counter-battery, tower, dense cluster, static heavy, objective defenders, isolated light last; heavy salvo min value | FireSupport ladder; cluster = 2+ enemies within 8 m (per-step cache); salvo (burst > 1, indirect) under 4 CP -> lastResort | **changed** |
| B9 / B10 | Recon opportunity fire; support coverage | Ladder factor 1 (no chase is the squads' / tactical AI's: recon edge-of-sight move kept) | **kept** |
| B11 / B12 / B13 | Bomber, fighter, loitering (anti-armour, Lancet-like) | Bomber / Fighter / LoiterAntiArmour / LoiterAntiArtillery ladders ("lancet" in the id = anti-artillery) | **changed** |
| B (role map) | Role from data | `CombatRoleDoctrine.BaseRole`: aiBehaviour.units role id, then flags (breacher, siege deploy), then UnitClass | **changed** |
| Part D1 | PositionScore with role weights | `FiringPositionScorer.Score` (11 terms, `ai.position.weights`, role factors) | **changed** |
| D2 | Hull-down for TD / MBT / heavy, LOS kept, not when timing critical | Flat ground: low cover (blocks movement, not fire: sandbags, tank traps, low walls, pipelines) 1.5-7 m in a 35° cone towards the threat, target line clear; used for TD / MBT slots in Hold, not in an urgent primary attack | **changed / deviation** (no terrain height in the sim) |
| D3 | Ridge / observation | Observation = clear 30 m lines round the spot (recon x1.5, TD x1) | **changed / deviation** (flat) |
| D4 | Dead ground for indirect fire | `FiringPositionScorer.DirectExposure` added to `TacticalAi.FiringSpot` (+6 per known direct-fire enemy that sees the spot) | **changed** |
| D5 | Cover reservation | `PositionReservations` (4 m, 10 s, one owner) used by `Best` | **changed** |
| E1 | Firing-lane check | Existing `FriendInLine` (score x0.6) + watchdog `BlockedByFriend` | **kept** |
| E2 | Wait / sidestep / alternate slot / other target / move blocker; no oscillation | `FiringLaneResolver` (rungs, 4 s cooldown, rear-of-pair acts, yielding blocker held), driven from the watchdog's BlockedByFriend branch | **changed** |
| E3 | Boss multi-mount lanes | Per-mount targeting (CombatSystem) and P0-C's BossWeaponDirector | **kept** |
| F1 | Main gun disabled -> screen | `ComponentState.MainGunLost` (main mount's part out for good) -> `DoctrineRole.Screen`, off the front row | **changed** |
| F2 | Engine crippled | Speed left (parts, slow) < 0.6: flank -15 points, hold +8 when most of the squad, off the front row | **changed** |
| F3 | Radar destroyed | `RadarLost` logged (SUPPORT_AA_COVERAGE_HANDOFF); such AA no longer counts as AA cover for fire-support anchors | **changed / scaffold** (coverage optimiser is P3 169) |
| F4 | APS lost | Off the front row; no retreat | **changed** |
| F5 | Boss broadside recompute | P0-C samples working mounts; P2 drops the held broadside the tick the mount set changes (`ComponentWatch.MountsChanged`) | **changed** (on top of P0-C) |
| Part G | Splash -> Spread, choke -> Travel, static -> Hold, flank -> Flank, low cohesion -> Regroup; hysteresis | `SquadLayer.ChooseFormation` (commit 3 s, choke / splash override), reason codes FORMATION_* | **changed** |
| I (all) | ModeDoctrine per mode: frontline, fire support, support, pursuit, reserve, triggers, target weights | `ModeCombatDoctrine` table (25 doctrines, inheritance I15), `ModeDoctrineState` (per-step, phase generation, per-side `For(team)`) | **changed** |
| I1 | Assault bands 55-75 / 65-85 / 75-90 / 85-95 %; towers first | `ai.modeDoctrine.*Band`; TowerWeight 1.4 | **changed** |
| I2 / I18 | Defend: launchers do not meet the enemy, no chase, deeper | DefenceLine policy, NoChase, BandBias 0.8; Hold / Protect / Outpost / Relieve inherit | **changed**; mine-layer pre-placement **scaffold** |
| I3 | Conquest: cover objective + approaches outside the circle; fast reserve | ObjectiveCover, FastReserve | **changed** |
| I4 / I19 | Escort / Evacuate: convoy-relative, leapfrog, leash wins | ConvoyLeapfrog anchor, Leash (escort profile's maxAdvanceDistance); sectors themselves kept (prompt 33 escort rules) | **changed** |
| I5 / I17 | Siege / Weekly: layers, shoot and scoot | SiegeLayers (reference = nearest seen enemy defence), ShootAndScoot, Tower x1.5, counter-battery x1.3 | **changed** |
| I6 / I16 | Survival / Endless: 2-3 pockets, rotate by wave direction; Endless reserve only for HQ emergencies | PreparedPockets (3), rotate 60 s, wave-direction trigger, ReserveEmergencyOnly | **changed** |
| I7 / I25 | BossRush: parts, adds, predicted region | BossPredict (6 s look-ahead), Boss x1.3, escorts x1.1; telegraph dodge = squads' existing warning dodge | **changed** |
| I8 / I24 | Deathmatch / Duel: logical front anchor | FrontLogical with front-moved / band-lost / pocket-compromised triggers | **changed** |
| I9 / I20 | Hunt / Intercept: launchers never chase, predict with intel | InterceptPredict (group confidence >= 0.5); slow-unit ETA filter **scaffold** (P3 207) | **changed** |
| I10 / I21 | Recon quiet | Quiet anchor (deep), fire support / bombers x lastResort under 12 CP unless the target threatens the mission | **changed** |
| I11 | Operation phase rebuild | `ModeDoctrineState.PhaseKey` (AiPhase, alarm, operation stage, showdown stage, boss phase, profile) -> Generation -> anchors / commitments rebuilt | **changed** |
| I12 | Showdown early / mid / final | Stage from ShowdownRules (escalation, rebuild cut-off, sudden death): band bias 1 / 0.5 / 0; final reserve 0-5 % | **changed** |
| I13 / I22 | ShootDown | AirFirst: unrelated ground x0.5; NoChase | **changed**; coverage optimiser **scaffold** |
| I14 | Fixed deck | Base doctrine inside the scenario's rules (flags untouched) | **kept** |
| I26 | Every profile / goal resolves; fallback BalancedObjectiveDoctrine | `ModeCombatDoctrine.Validate` + MODE_DOCTRINE_FALLBACK at first use; optional data key aiModeProfiles.*.doctrine | **changed** |
| Part J | FireSupportAnchor, AnchorScore, triggers | `FireSupportDirector` per tactical AI side, per fire class; replaces the old standoff in `TacticalAi.DirectArtillery` (old standoff only when no valid spot) | **changed** |
| 19 | Lifecycle Forming..Dissolving | `Squad.Lifecycle`, SQUAD_LIFECYCLE lines | **changed** |
| 20 | Size 3-9, desired 5-7, exceptions | Enlist fills to 7, merges to 9 (`ai.squadLayer.maxSquad` 6 -> 9), split over 9. Artillery batteries, aircraft, naval escorts, drones are not in squads (tactical AI / boss escorts own them) | **changed** (exceptions **kept**) |
| 21 | Merge (< 45 %, compatible, < 35 m, no combat; not reserve / opposite flank / other domain / over max) | `CanMerge`, `MergeP2`; Join merges inside 35 m | **changed** |
| 22 | Split over max; choke packets 2-4 s apart; two objectives | `Split` (alternate column members); packets in `SlotsP2`; two simultaneous objectives **scaffold** (P3) | **changed** |
| 23 | Reinforcement rendezvous 12-20 m | `EnlistOne` / `Rendezvous` / `ServePending` (receive radius 16 m; reachable, low threat, no doorway, off routes) | **changed** |
| 24 | Reserve 15-25 % | `AiCommander.PickReserve` / `ReserveTrigger` (threat near home / a squad, a losing squad); mode doctrine decides | **changed** |
| 25 | Cohesion 0.45 / 0.30 / 0.25, regroup < 0.55 for 2 s | `CohesionOf`; Regroup option from cohesion (recover at 0.7), not in an immediate survival fight | **changed** |
| 26 / 27 | Formalised slots, role placement | `FormationSlots` (front / middle / outer / rear rows), `PlacementOf` | **changed** |
| 68 | CombatPower | `PowerOf` (DPS vs nearest seen enemy x survivability x availability x range x mobility access, normalised) for debug / squad view | **changed** (odds still from intel strength, 69) |
| 69 | Odds thresholds from tactic data | Existing tactic AttackThreshold | **kept** |
| 70 | Urgency | `UpdateUrgency` (HQ threat, points lost, Showdown clock, enemy boss phase 2+), threshold x lerp(1, 0.75, U), floor = tactic x 0.75 | **changed** |
| 71 / 72 / 73 | Objective demand, assignment utility, commitment | `Demand`, `AssignmentScore` (role fit, distance, current task, domain, reassignment cost), commit = AI minCommit except emergency / phase change | **changed** |
| 74 | Join with rendezvous / intercept | `Intercept` (velocity x clamp(travel, 0, 6)) | **changed** |
| 75 | Regroup point | `RegroupPoint` (behind the line, one component, no splash / choke / route / doorway) | **changed** |
| 76 | Flank route score; no flank too narrow | `FlankRouteFits` (MapTopology.Bottleneck vs column width); threat factor kept; congestion / exposure cost **scaffold** (P1 traffic) | **changed / partial** |
| 86 | Travel before choke, restore after | Part G choke trigger (MapTopology chokes within 40 m); restore when the choke is behind (after the commit window) | **changed** |
| 97 | Squad debug | Squad `Why.Context`: task, state, formation (+ reason), lifecycle, cohesion, power, members + pending | **changed** |
| 159 / 160 / 161 / 162 | Morph, stable slots, stable column, splash spacing | Halfway slot for 1.5 s; slot kept per placement; column rebuilt only on member / component change; spread capped at 8 m against direct AT only, packets of 3 under splash | **changed** |
| Part O | Reason codes | `P2Reasons` (MODE_*, ARTILLERY_*, POSITION_*, FORMATION_*, TARGET_*, BOSS_*, SUPPORT_*, SQUAD_*, ROLE_*) | **changed** |

## Regression rows (tests written, not run)

`Assets/MachineBrigade/Tests/EditMode/AiMasterP2Tests.cs` (32 tests)

| Row | Tests |
|---|---|
| R2 / R3 (ladder side) | `R2_R3_TheBreacherAndSiegeRowsStayP0AsAndTheLaddersLeaveThemAlone` (P0-A's R2/R3 tests stay the behaviour check) |
| R4 Assault, Defend, Conquest, Escort, Siege, Survival, BossRush, Deathmatch, Hunt, Operation phase, Showdown | `R4_*` (11 tests: anchor policy and band, pursuit, reposition trigger) |
| R5 boss broadside, MBT main gun | `R5_ABossThatLosesABatteryDropsItsHeldBroadsideAndRecomputes`, `R5_AnMbtThatLosesItsMainGunBecomesAScreenWithoutAHealthRetreat` |
| R6 | `R6_TheRearTankSidestepsThenTakesAnEquivalentSlotInsteadOfIdling`, `R6_InARunTheBlockedRearTankFiresOrMovesAndNeverIdlesUnexplained` |
| R7 | `R7_ATankDestroyerPrefersTheHullDownSpotToOpenGroundWithTheSameTiming` (+ D5 reservation) |
| 112 reinforcement / understrength / oversize / narrow route | `S112_*` (5 tests: rendezvous and join, merge, merge rules, split, choke -> Travel + packets) |
| 160 / 161 / 25 / 24 | `S160_S161_SlotsAndColumnOrderAreStable`, `S25_CohesionIsLowWhenScatteredAndHighWhenGathered`, `S24_TheCommanderKeepsAReserveWhereTheModeAllowsIt` |
| I26 / I15 / I23 / B | `I26_*` (2), `I15_*`, `I23_*`, `B4_*` (2), `B6_B7_B8_*` |

## Risks for the lead's runs

1. Every fight changes: role ladders (x0.35-1.6) on the main weapon, mode target weights, new squad sizes (7 desired, 9 max
   instead of 6), cohesion-based regroup instead of spread, the reserve (15-25 % of squads held back in Conquest-like modes),
   artillery on anchors. Tests that pin exact squad counts, targets or artillery spots (AiScenarioTests, PlayTest8A) may move.
2. Reserve: a 2-squad army holds one squad back only if it is under 25 % of the strength; with squads of 7 a reserve appears
   from about 4 squads. Watch that Conquest attacks do not stall (the reserve commits on threats / losing squads).
3. Rendezvous: a reinforcement up to 150 m away drives to its squad's rendezvous instead of forming a squad at the base;
   pending units time out after 45 s (they join where they are).
4. Fire-support anchors: on cramped maps no band candidate may be valid (walkable, off doorways, outside known guns): the
   old standoff is used then. Check that mortars do not park on the far side of walls (no path check on the anchor).
5. Per-side doctrine: the attacker in Defend / Survival / Hold plays Assault, the defender in Assault / Siege plays Defend.
6. Cost (Part P): the ladders are cached per step; cohesion O(n^2) per squad (n <= 9); anchors scored only when set.

## For the lead / other lanes

- P1 (traffic): `SquadLayer.ChokeAhead`, `RequiredWidth` and the packet release times (`Squad.ReleaseAt`) are the squad side
  of section 86 / 22; a TrafficCoordinator choke queue can replace the fixed 3 s packet delay. `PositionReservations` and the
  firing-spot booking are the Firing reservations P1's Transit / Hold reservations sit beside.
- P3: `ModeDoctrine` (policies, triggers), `FireSupportDirector.AnchorOf`, `AiCommander.Urgency`, the reserve's
  `ReserveTrigger` and `Demand` are the hooks for the frontline model, planned action board and coverage optimiser.
- P5 Health Monitor: lifecycle / cohesion / power per squad (`Squad.Lifecycle`, `Cohesion`, `Power`), anchor reasons, lane rungs
  (`FiringLaneResolver.RungOf`).
