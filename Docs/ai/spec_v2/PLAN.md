# AI spec v2: implementation plan (lead, 04/10)

Sources: Machine_Brigade_AI_Behavior_Full_Spec_v2.md (5,020 lines, sections 0-200+) and the owner's prompt
PROMPT_owner_vi.md (priorities, overrides, tests, report format). Integrate into the existing AI
(AiCommander / SquadLayer / TacticalAi / WorldModel / DecisionLog, docs Docs/export/current/09_ai*), never rewrite blind.
Each lane writes its audit (spec section -> current code -> change) to Docs/ai/spec_v2/AUDIT_<lane>.md and its tests
(EditMode, deterministic) — the owner requires tests for this task; the lead runs them and the benchmarks at the end.

Wave 1 (Priority 0):
- W1-A procurement + targeting: MapTopology (domains, connected components, chokes, regions), EngagementFeasibility
  (reachable firing region, cache), ProcurementDirector hard filter (no-map-influence REJECT logged) + score inputs
  (role deficit, counter need from observed intel EMA, objective fit, timing, congestion, same-match utilization),
  PurchasePlan batches, reserve CP; target hard feasibility (mask, arc, reachable firing, min-range trap), utility,
  overkill, stickiness, drop unreachable. Spec 4-18, 42-47, 83, 88-91, 100-101, 105-106, 109, 113, 196-198.
- W1-B boss/naval: BossBrain split (mission/movement/weapon/phase/escort/target directors) on the existing boss code;
  NavalBossMovementController (allowReverse=false, Rmin, look-ahead on lanes, heading hysteresis, broadside from mount
  arcs, smoothing, CPA prediction, spacing, escape/phase lanes); hull/turret decoupling for naval, ground and flying
  bosses; boss corridor reservation; escort rings. Spec 48-67, 96, 103-104, 110, 166-167, 179-181.
- (after the gear-targets lane frees MachineBrigade-art) W1-C traffic/anti-stuck: staged jam detector (1.5/3/5/8/12 s),
  deterministic passing side, ORCA-lite, TrafficCoordinator (gate/choke/bridge/spawn exit/boss corridor/parking
  reservations, right-of-way, queue), wreck nav invalidation, spawn clear zone, artillery parking lease, predictive
  congestion, wait-for deadlock. Spec 30-41, 84-87, 95, 102, 111, 185-190.
- Gear correction (prompt sections 15-21): lane gear-targets (running).
Wave 2 (Priority 1): squad lifecycle, size 3-9, merge/split, choke packets, rendezvous, reserve 15-25 %, cohesion,
  formation slots/roles, shared path/corridor, join/regroup, assignment/commit. Spec 19-29, 68-76, 159-162, 170-172.
Wave 3 (Priority 2): frontline, confidence (not morale), temporal/death memory, route diversity, unknown-risk, scout,
  synchronized ETA, AttackPackage, staging, PlannedActionBoard + reservations, fire missions, counterbattery from
  observed fire, shoot-and-scoot, pursuit leash, stances. Spec 77-82, 124-151.
Wave 4 (Priority 3): forecast + shallow counterfactual plans, probe/feint, abort, exploit windows, same-match
  adaptation, anti-repetition, air (CAP, SEAD, risk routing, bomber, handoff), boss telegraph/escape/pressure, the
  rest of 152-200.
Final: tick staggering + performance budget (98), DecisionLog/debug (94-97), difficulty (92-93), tunables (107-108),
  docs regen (09_ai, 04, 02, 06, 00_index, README, CHANGES), Unity test run + benchmarks (32v32, 48v48,
  boss+escorts+army, wrecks/chokes, many squads), quality gates (115), report in prompt section 23 format.
