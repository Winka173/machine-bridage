# AUDIT P0-D + P1 — staged anti-stuck, traffic, shared corridors (lane B, 05/10)

Source: `Machine_Brigade_AI_Behavior_MASTER_FINAL.md` sections 28-41, 84-87, 95, 102, 111, 185-190 (+ MASTER RULES 7, 9;
Part A "anti-stuck fallback", "firing-spot booking"; Part O `TRAFFIC_*` / `JAM_*`; Part P budgets). Branch `feature/ai-p1`
(includes P0-A, P0-B, P0-C via `lead/integration`). Sim builds (`dotnet build Tools/simbuild/Sim.csproj`); the tests compile
against the Sim; no Unity run, no test run (the lead runs `AiMasterP1Tests`, category `AIMasterP1`).

Status: **change** = new or changed code; **kept** = existing behaviour kept (Part A); **scaffold** = API in place, behaviour
partial or for a later lane.

Every new behaviour has a switch for the lead's sweeps: `ai.navigation.jamStages` (false = the old ladder exactly as before),
`ai.navigation.orcaLite`, `ai.traffic.enabled` (corridors, passages, exits, parking rules).

## Spec section -> code

| § | Spec | Before | Now | Status |
|---|---|---|---|---|
| 28 | Shared squad path | every member's own A* from `IssueGroupMove` / `Slots` | `SquadCorridors` (Sim/Movement/SquadCorridor.cs): one costed A* per squad order (squads of 3+, goal 30 m+); each member joins it at the furthest of the first 4 points in plain line, leaves at the last point that sees its slot (`SimWorld.IssueAlongCorridor`, no route search of its own); fallback = the plain command | change |
| 29 | Flow field / corridor phase 1 | — | phase 1 as specified: shared waypoint corridor + local avoidance; cached per owner 8 s / goal within 10 m; replanned when dirty (wreck, jam stage 4, overload); 2 builds per step, 6000-cell budget. Phase 2 flow-field tiles: not done | change / scaffold (phase 2) |
| 30 | TrafficCoordinator (gate, choke, bridge, spawn exit, narrow road, boss corridor, firing parking) | doorway one-way rule per vehicle (`GateCheck` / `ResolveGates`), firing-spot booking | `TrafficCoordinator` (`world.Traffic`): passages built from the lane map's doorways (Gate / NarrowRoad) and MapTopology's ground chokes (Choke / Bridge when beside water), rebuilt when lanes or topology change; spawn exits; boss corridors (`IBossCorridors`, default = P0-C `BossBrains.Corridors`); parking rules; dynamic costs; stats | change (the per-vehicle doorway rule is kept underneath) |
| 31 | PassageReservation, same way batched, opposite ways alternate | doorways: one-way per step claims, turn after `GateTurnSeconds` | `Passage.Holder` per side: Owner, EnterTime, ExpireTime, Direction, Priority, PriorityHeldUntil, Members, Riders; same way = batched riders; other way queued; after `alternateSeconds` 8 s with the other way waiting the turn goes over; waiters ordered priority > time > owner | change |
| 32 | Right of way 100..30, held ≥ 2 s | `TrafficPriority` (mover vs parked: 100/80/65/60/50/45/40/30/20/15/10) | kept for asking parked friends to make way; new `RightOfWay`: 100 boss/convoy, 90 in a passage, 80 heavy, 75 just spawned (3 s), 70 main effort, 60 artillery moving, 50, 40 reinforcement, 30 scout; cached 2 s; used by stage 3, head-on ties, ORCA responsibility, passage requests, deadlocks | change |
| 33 | Boss corridor radius + 2.5 m; friends avoid within 25-35 m | P0-C: friends parked in it make way (`ClearBossCorridors`) | kept (P0-C); P1 adds the traffic side through `IBossCorridors`: corridor cells cost 200 for routes planned round hulls, no parking / firing spot in it (`CanPark`), boss right of way 100 in ORCA (others take 85 %) | change (wired to P0-C) |
| 34-35 | ORCA-lite, horizon 1.5 s, responsibility by priority | blocker probe + avoid side; separation pushes | `MovementSystem.OrcaTurn` + `TrafficSteering.Avoid`: nearest ≤ 10 moving hulls (sorted window, ties by id), closest approach within 1.5 s, lateral avoidance × responsibility (85 % / 15 % / 50 %) × urgency × depth, clamped to the existing avoid angle, only towards open ground; 10 Hz (every other step, staggered); followers the same way and doorways left to the traffic rules | change |
| 36 | Passing side by pair hash, kept until 2× radius apart | oncoming: both keep right; crossing: away from the blocker's side | `TrafficSteering.PassingSide` (FNV hash of min/max id) cached per pair in the coordinator, released beyond `passingRelease` × radii; oncoming pairs keep right (the existing rule, consistent for both) | change |
| 37 | Jam detector (distance/path progress, desired/actual speed, density, blocker) | `DetectStuck` per 1.5 s window (progress to waypoint) | `JamTracker` per vehicle (4 Hz, staggered): low = actual < 25 % desired and route progress < 0.25 m/s; drains ×2 on progress; frozen while waiting on purpose (yield, doorway turn, queue, path queued); reset on a new order or when engaging | change |
| 38 | Stages 1.5 / 3 / 5 / 8 / 12 s | ladder: ask ×2, costed route ×2, back off, give up (~6-9 s); safety net at 10 s (ghost, then hop) | stage 1: loosen formation 4 s + deterministic side-step when crowded; 2: local waypoint 3-6 m off the line round occupied cells (else costed route); 3: friend in the way: higher right of way keeps the road, the other yields (forced request) or steps aside, parked friends always yield, bosses never; 4: congestion stamp (60, 6 m, 12 s) + corridor replan accepted only under 1.5× (`CostedKind.Corridor`), squad corridors through it dirty; 5: formation break 8 s, 3 m reverse only if `JamPolicy.AllowsReverse` and room, else pivot to an alternate local target. The ladder's asks and costed routes run inside stages 1-2; its back-off waits for stage 5; the give-up comes 3 s into stage 5 (or after 10 windows) | change (old ladder folded, kept when `jamStages` false) |
| 38 | Naval never reverses | — | `JamPolicy.Emergency(naval)` = `WidenTurnAlternate`; ships are not in the ground loop (P0-C's naval controller owns them; its no-reverse rule stays) | change (policy) |
| 38 | No teleport; relocation = last fail-safe, `SEVERE_UNSTUCK` | rescue at 10 s: place / ghost / hop, logged in `RescueLog` | rescue waits `failSafeS` 14 s (after stage 5); ghost = `JAM_FAILSAFE_GHOST`; place / hop (relocations) = `SEVERE_UNSTUCK` line + `Traffic.Stats.SevereUnstuck` (`SeverePlace`, `SevereHop`), `world.SevereUnstuckCount` for the lead | change |
| 39 | Wreck: dirty nav at once on spawn / removal; dear before a wall | wreck cost stamped at the next refresh (0.5 s), routes only replanned when stuck | `WreckField.Version` + change list; next movement step: cost layers invalidated, every ground route through a new wreck within 40 m replanned at once (`CostedKind.Wreck`, `ROUTE_WRECK_REPLAN`), corridors near it dirty; a wreck younger than 1.5 s costs 120, then 250; stamp widened by 1.5 m (a hull must not take a gap it cannot pass) | change |
| 40 | Spawn ExitBox / ClearZone / RallyRing; blocked > 2 s: outsiders yield, new units priority 3 s | — | `SpawnExit` per side at the drop zone (10 / 16 / 24 m); `CanPark` (no firing spot in the exit box), `OutOfExit` (squad hold / regroup points moved to the ring); exit blocked 2 s: idle parked friends (not just spawned) driven to rally-ring slots (`TRAFFIC_SPAWN_EXIT_CLEAR`); right of way 75 for 3 s after spawning in the clear zone. Mission spawn points (`SpawnPoints`): not added (they are edge entries) | change |
| 41 | Artillery parking lease; expire > 5 m; 1.5× splash spacing; not on main route | booking 3×3 cells, in use within 6 m | kept; lease = 5 m (`parkingLeaveM`); `CanPark`: a gun never on a main route nor within 1.5 × max(6 m, enemy splash) of another friendly gun's booked spot (one-line check in `TacticalAi.FiringSpot`) | change |
| 84 | Dynamic obstacle cost categories | parked friend 40, enemy 80, stunned / wreck 250, ring 10 | kept; added: congestion 60, boss corridor 200 (own side), booked firing spot 120 (own side), fresh wreck 120; traffic lane low move / high parking cost = the lane map's `StandCost` (kept); walls INF (grid) | change |
| 85 | Choke queue Q1, Q2... | doorway wait spot beside the mouth (per vehicle) | kept; squads: `Passage.QueuePoint(dir, slot)` back along the way in, two abreast off the line (`queueStart` 8, `queueSpacing` 8 m); queued squads wait there (`JAM_CHOKE_QUEUE`), explained to the P0-A watchdog as WaitingFormation | change |
| 86 | Formation → column through a choke, packets 2-4 s apart, restore after | G.2: back half waits 3 s | with a reserved passage: members `InColumn` (separation × 0.85), packets of lanes × 2 (1 lane when overloaded, 1-4 hulls) released `chokeBatchGapS` 2.5 s apart (clamped 2-4); the requested formation is kept for the slots at the goal; column flag cleared and passage released once every member is 6 m past. G.2 kept when there is no reserved passage | change |
| 87 | Minimum separation r+r+0.5, ×1.3-1.8 splash, ×0.85 column | separation of capsules (no overlap) | kept for collisions; `TrafficSteering.MinSeparation` (×1.5 under a known enemy blast ≥ 3 m, ×0.85 in a column) is ORCA-lite's clearance | change |
| 95 | Movement debug fields | — | `world.Traffic.DebugOf(v)` → `MovementDebug` (DesiredVelocity, SafeVelocity, FormationSlot, SharedPathId, TrafficPriority, JamStage, BlockerId, LocalTarget, StrategicTask, Reason, NextPassage); `DecisionKind.Traffic` lines in `world.AiLog` | change |
| 102 | C# JamTracker | — | `Sim/Movement/JamTracker.cs` as specified (+ Handled, Episodes, Worst, Reason, Waiting) | change |
| 108 | Old anti-stuck only as fallback; StaleIdle 12 s as severe fail-safe | see 38 | folded under the stages; the squad layer's own unstick (G.3) leaves members alone while traffic owns them (queued, packet, jam stages 1-4) | change |
| 111 | Congestion tests | — | `Tests/EditMode/AiMasterP1Tests.cs` (written, compiled against the Sim with stubs, not run): 20 vehicles one objective (squads, shared corridors, gate reserved, no shared slot, 0 severe), two squads opposite one gate (API: one granted, other queued, batching, next turn; sim: both groups through, 0 severe), heavy + scout (scout yields, heavy keeps the road), wreck in a choke (replanned within 3 steps, route keeps off the hulk, through the other gate, never 10 s still); plus spawn exit, deadlock cycle, dedup, parking lease, SEVERE_UNSTUCK counter, jam stage times, naval no-reverse, passing side, ORCA responsibility, debug fields | change |
| 185 | Unit state anomaly | — | move orders: no acceleration within 0.5 s (`ANOMALY_NO_ACCEL`) or no route found (`ANOMALY_NO_PATH`), logged once per order; recovery = the jam stages (no re-issue). Attack (aim progress) and Join (rendezvous distance): P0-A watchdog / P2 squads | change / scaffold |
| 186 | Command deduplication | squads issue only on change; TacticalAi checks its own | `IssueGroupMove`: an AI (non-manual) order equal to the current one (kind, point ±0.5 m, still on its way) is skipped (`Stats.CommandsDeduplicated`); player orders always go through | change |
| 187 | Intent ownership | — | not in this lane (P2/P5 arbiter) | — |
| 188 | Predictive congestion (arrivals in 5 s) | — | `PredictArrivals` (2 Hz): each ground vehicle's first passage within speed × 5 s (`v.Traffic.NextPassage`); overloaded = arrivals > throughput × 5 s: the squad takes a way round under 1.5× (`ROUTE_ALT_CONGESTION`), else smaller packets (delay = queue) | change |
| 189 | Choke throughput | — | `Passage.Lanes` = width / (hull width + 1), `Throughput` = lanes × speed / (length + 4); `QueueDelay` for ETAs | change |
| 190 | Deadlock wait-for graph | head-on pairs only (`ServeHeadOns`), queue-behind loops guarded pairwise | `ResolveDeadlocks` (1 Hz, before driving): edges = queued behind / jammed against a friend; functional-graph cycle walk; lowest right of way (ties: higher id; never a boss) yields to the one waiting on it or takes a local waypoint (`TRAFFIC_DEADLOCK_CYCLE`); bosses only: local waypoints, no reverse. Naval (low-priority ship slows / turns aside): P0-C controller | change |

## Part A (kept)

`TrafficPriority` and the ask-to-make-way protocol (two-phase requests), head-on back-out in doorways, doorway one-way turns
and wait spots, costed routes round parked hulls with the cell budget, queue-behind, arrival contagion, the safety net
(`RescueLog`, ghost / place / hop) and the stuck report (`StuckWatch`), firing-spot booking, the squad layer's G.2 stagger and
G.3 unstick (now skipped for members the traffic layer owns), P0-C's boss corridor yields.

## Determinism and budget

No `Random` in any new decision (passing side by pair hash, local waypoints by fixed candidate order, ties by id); lists in
build / vehicle order; the coordinator's parts are staggered over the second (passages 1 Hz, reservations / exits / arrivals
2 Hz, passing sweep 0.5 Hz); jam looks 4 Hz staggered by id; ORCA 10 Hz staggered; corridor builds ≤ 2 per step with a cell
budget; wreck replans go through the existing costed-path queue and its per-step cell budget.

## Open / risks (for the lead's runs)

- Behaviour change on every map: give-up and back-off now come later (stage 5, 12-15 s) and the safety net at 14 s instead of
  10 s; existing `TrafficTests` / `StuckTests` timing expectations may need the lead's look (`ai.navigation.jamStages` false
  restores the old ladder).
- ORCA-lite adds a steering term near moving hulls; tune `orcaHighShare` / `orcaLowShare` / `orcaNeighbours` or switch it off.
- Shared corridors change how AI squads drive (one line, then slots); stragglers without line of sight use their own route.
- `world.Topology` is now touched by the movement system once a second (rebuild rules unchanged).
- Not done: flow-field tiles (29 phase 2), mission spawn points as exits, naval wiring of the jam policy (P0-C owns ships),
  intent ownership (187).
