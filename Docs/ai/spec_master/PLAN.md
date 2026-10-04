# AI MASTER spec: implementation plan (lead, 04/10)

Single source of truth: Docs/ai/spec_master/Machine_Brigade_AI_Behavior_MASTER_FINAL.md (6,395 lines). Owner (04/10):
"file AI hoàn thiện đã có, dùng nó, các file trước bỏ" — the V2 spec and its prompt are dropped (removed from the repo);
do not combine old AI prompts with it. Integrate into the existing AI (AiCommander / SquadLayer / TacticalAi /
WorldModel / DecisionLog; docs Docs/export/current/09_ai*), never rewrite blind (Part A).
Each lane: audit (spec section -> current code -> change/kept/scaffold) in Docs/ai/spec_master/AUDIT_<lane>.md, tests
for its rows of the regression matrix (Part R + sections 109-114, 224) written as EditMode tests; the lead runs the
tests and the performance runs (Part P, 48v48 gate) at the end, then the Part V report and Part W confirmations.

Order (Part Q):
- P0 correctness, 3 lanes:
  - P0-A combat: CombatActivityWatchdog + no-idle-armed-unit invariant (Part C), target hard feasibility + utility +
    overkill + stickiness + unreachable drop + accessibility cache + arcs/aim/fire-while-moving (42-47, 83, 88-91,
    105-106), breach/structure targeting and objective-aware priority (Part B breacher/siege rows, Part H).
  - P0-B procurement: MapTopology, connected components, EngagementFeasibility, reachable firing region,
    ProcurementDirector with no-map-influence REJECT before scoring + score inputs, PurchasePlan, reserve CP,
    boss/factory spawn feasibility (4-18, 67, 100-101, 109, 196-198, 208-209).
  - P0-C boss/naval: BossBrain split, NavalBossMovementController (no reverse, Rmin, look-ahead lanes, hysteresis,
    broadside from arcs, CPA, spacing, escape/phase), hull/turret separation for naval/ground/air bosses, boss
    corridor, escort rings (48-66, 96, 103-104, 110, 202-203).
- then P0-D + P1 movement/traffic: staged anti-stuck (37-38, 102), shared corridor, TrafficCoordinator, deterministic
  passing, choke queue/reservation, wreck nav invalidation, spawn clear zones, predictive congestion, deadlock
  wait-for (28-41, 84-87, 111, 185-190).
- P2 role/mode intelligence: CombatRoleDoctrine (Part B), ModeCombatDoctrine (Part I), FireSupportAnchor (Part J),
  terrain/cover (Part D), friendly firing lane (Part E), component-state adaptation (Part F), formation switching
  (Part G), squad lifecycle/size/merge/split/rendezvous/cohesion/formation slots (19-27, 68-76, 159-162).
- P3 coordination: frontline, planned action board, synchronized attacks, reserve, route diversity, counterbattery,
  pursuit (124-151, 170-173, 199-201, 205-213).
- P4 advanced planning: forecast, shallow counterfactual plans, probe/feint/fix-flank, same-match adaptation
  (Part M), SEAD/air packages, boss cadence/weakpoint (152-158, 174-181, 214-217).
- P5 monitoring/optimization: AI Health Monitor (Part K), ammo-aware tactics (Part L), tower coordination (Part N),
  reason codes (Part O), update budget (Part P), tuning + regression sweeps; docs regen; Part V report.
