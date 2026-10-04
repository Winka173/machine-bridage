# AUDIT P0-B — map topology, engagement feasibility, procurement (lane B, 04/10)

Source: `Machine_Brigade_AI_Behavior_MASTER_FINAL.md` sections 4-18, 67, 100-101, 109, 196-198, 208-209 (+ MASTER RULES 1, 2,
6, 9; Part A; Part O `PURCHASE_*`). Branch `feature/ai-p0b`. Sim builds (`dotnet build Tools/simbuild/Sim.csproj`); no Unity
run, no test run (the lead runs `AiMasterP0BTests`, category `AIMasterP0B`).

Status: **change** = new or changed code; **kept** = existing behaviour kept (Part A); **scaffold** = API in place, behaviour
partial, left for a later lane.

## Spec section -> code

| § | Spec | Before | Now | Status |
|---|---|---|---|---|
| 2.1 | Filter before score | `ConquestAi.TryDeploy` scored every legal card; no map check | Legality (existing checks) then `ProcurementDirector.Gate` (map feasibility) **before** any score; a rejected card is never scored | change |
| 3.5 | Procurement tick 0.5 Hz / event | buying ran every `Interval` (2.2 / 1.1 / 0.6 / 0.45 s by difficulty) | kept; the director observes once per buying decision; plans (§16) stop re-scoring every tick | kept |
| 4 | MapTopology: domains Ground/Naval/Amphibious/Air/Static; Ground/Naval/Amphibious graphs; Chokes; MainLanes; Regions; Objectives | none (NavGrid had one ground region labelling; LaneMap has roads/doorways) | `Sim/Navigation/MapTopology.cs`: `MobilityDomain`, `DomainGraph` per domain on the NavGrid's 2 m cells (Ground = open & not sea, Naval = sea, Amphibious = open incl. shallow water and any open sea cell), `Chokes` (clearance field + opposite closed sides, clustered), `Regions` (= components), `Objectives` (capture points, team rallies, coastal batteries, with component per domain). `MainLanes`: not duplicated — `SimWorld.Lanes` (LaneMap) already holds roads/main routes | change (MainLanes: kept as LaneMap) |
| 4 | built once per map, cached | — | `SimWorld.Topology` lazy; rebuilt only when `Grid.Version` changed and `ai.topology.rebuildSeconds` (5 s) passed (walls down, wrecks): deterministic rebuild moments | change |
| 5 | Connected components per domain; spawns and objectives know their component | `NavGrid.RegionOf` (ground only, not sea-aware) | `DomainGraph.ComponentAt/ComponentOfCell`, `ObjectiveRegion.Ground/Naval/AmphibiousComponent`, BFS distance fields `DistancesFrom(source)` (cached, 16 sources) | change |
| 6 | `EngagementFeasibility` / `InfluenceResult` (CanDeploy, CanReachObjective, CanReachEnemy, CanFireFromReachableRegion, Coverage, TravelSeconds, UsefulTargetShare, Reason) | none | `Sim/AI/EngagementFeasibility.cs`: `InfluenceResult` (+ `ObjectiveCoverage`, `NoTargets`), `Evaluate(def, ctx)`; `SimWorld.Feasibility` | change |
| 7 | "can fire" ≠ "can reach" (coastal gun vs MBT) | — | reach = component cells within target radius; fire = §8 band; both separate in the result | change |
| 8 | Reachable firing region = reachable ∩ (target ⊕ max range − target ⊕ min range); cache by (mobility, envelope, target region) | — | `WeaponEnvelope.Of(def, layer)` (min/max over damaging mounts that hit the layer; ship-only guns only on ships); band test as the combat system measures (`distance − radius ≤ range`, `distance ≥ minRange`); cache key (domain, source cell, min, max, target coarse cell 8 m, radius); a ship counts by its lane (9 samples over its patrol) → Coverage = share of the lane in reach | change |
| 9 | ProcurementDirector pipeline | additive score in `TryDeploy` (counters, role mix, value, copies, commander fit, tactic shares via `AiCommander.BuyScore`) | `Sim/AI/ProcurementDirector.cs` + `ConquestAi.Procurement.cs`; the legacy score is **kept** and the director's master score is added (`ai.procurement.blendWeight` 3 points; Easy ×0.5, Normal ×0.75) | change (integrated, not replaced) |
| 10 | Hard filter: !available, CP < price, cap, spawn unavailable, deployment impossible, zero useful targets & no utility, cannot influence → `reject("no-map-influence")` | legality only | legality kept in the loop; `Gate`: `!CanDeploy` → `deployment-unreachable`; `!Useful && !IsStrategicUtility` → `no-map-influence`. CP < price stays a "save up" decision (not a reject), as before | change |
| 10/101 | `log.Reject(card, "no-map-influence")` | — | `DecisionLog` gets `DecisionKind.Purchase`; line `REJECT <card> reason=no-map-influence (PURCHASE_NO_MAP_INFLUENCE; <influence>)`, logged when a card's verdict changes (no flood of the 4000-line ring) | change |
| 11 | Naval boss map: never "only naval"; ground valid from shore / land objective / utility | — | targets = enemies seen (clustered 16 m, ships by lane), points not held (own when contested), mission goal (`Goal`), defend point, enemy camp when it has a base; ground stays eligible with any of them reachable or in reach | change |
| 12 | FinalScore = 0.22 RoleDeficit + 0.18 CounterNeed + 0.15 ObjectiveFit + 0.12 MapInfluence + 0.10 Timing + 0.08 Survivability + 0.06 Synergy + 0.05 Cost + 0.04 Tactic − Redundancy − Congestion − LongTravel | — | `ProcurementDirector.Score`, weights in `ai.procurement.weights`; inputs 0-1 | change |
| 13 | Role budget by tactic shares (Frontline … AirCover) | `RoleMix` 5 roles (legacy) / `AiCommander.Targets` 8 force groups (layered) | `ProcurementRole` (13 roles), `RolesOf(def)` multi-role; desired shares from the layered general's force-group targets, else the legacy mix, else §13 Balanced (Flexible → AirCover/Drone) | change (both old mixes kept and still scored) |
| 14 | Counter need from observed/remembered intel; decay when stale | `CounterScore` from `KnownEnemies` (seen) | kept; plus director EMA over threats (Air, HeavyArmour, Light, Artillery, Drones, Naval; AntiAir/AntiTank for survivability) from `TacticalAi.KnownEnemies` only (fog-fair); EMA decays to 0 with nothing in sight | change |
| 15 | EMA 0.20; mismatch only with confidence ≥ threshold and ≥ 4 s | `TeamIntel` MISMATCH events (no EMA) | `ai.procurement.intelEma` 0.20, `mismatchShare` 0.2, `mismatchConfidence` 0.5 (confidence = seen CP / 24), `mismatchConfirmSeconds` 4 | change |
| 16 | PurchasePlan 3-5 cards, purpose, cancellable | none (one card per decision) | `PurchasePlan` (cards, purpose, expected power, CP, signature); made when the top card is bought (Normal 4, Hard+ 5; Easy none); next card bought first; cancelled on expiry (30 s), confirmed-need change, a card turning infeasible; illegal card skipped. Purposes: shore denial / air defence / anti-armour / counter-battery / objective capture / frontline | change |
| 17 | Congestion = density × footprint × choke dependency | none | ground army / cap × radius/3 × (narrowest passage on the shortest ground route drop zone → first objective, `MapTopology.Bottleneck`) × `congestionMax` 0.2 | change |
| 18 | Reserve CP (counter nearly affordable, boss phase soon, composition enough, air cap full, ground cap near full); bounded | saves for the best card unless thin / overflowing / Easy; Very Hard massing; all-out saving | kept; plus `Reserve`: a confirmed counter's card affordable within `reserveHorizonSeconds` 8 s of income is waited for (≤ 12 s, never at bank − 3, thin army or under fire). Air cap full = legality (kept). Boss-phase forecast and "composition enough": **scaffold** (P4 forecast) | change / scaffold |
| 67 | Boss/factory spawns through the same feasibility; scripted spawns keep their role | factory and escort waves spawn their lists blindly | `EngagementFeasibility.SpawnUseful`: workshop (`BossSystem.P20.FeasibleUnit`) takes the next feasible unit of its list (none: the list's own); escort waves (`BossSystem.Escorts.Spawn`) skip a ground escort that could do nothing where it would land; both log `REJECT … (factory/escort spawn)`. Mission-event (scripted) spawns untouched | change |
| 100 | C# feasibility skeleton (`Useful`) | — | `InfluenceResult.Useful` = CanDeploy && (NoTargets ‖ objective ‖ enemy ‖ fire ‖ share > 0); `UsefulTargetShare` is map-aware (hurt **and** engage), so a tank that could hurt a ship it cannot reach is not "useful" | change |
| 101 | C# procurement skeleton | — | `ConquestAi.TryDeploy` loop: legal → Gate → legacy score + `LegacyAdjust(Score)` → best | change |
| 109 | Tests A/B/C | — | `Tests/EditMode/AiMasterP0BTests.cs` (written, not run) | change |
| 196 | Same-match feedback: CombatTime ≥ 20 s & utilisation < 0.15 → ×≥0.55, log `low-realized-utilization` | none | per card (elite → base id): combat seconds = an enemy within 1.5 × reach or fired in 2 s; firing seconds = fired in 2 s; modifier 0.55-1 on the master score, `feedbackPoints` 4 off the legacy score; factor `low-realized-utilization` in the BUY line | change |
| 197 | Counter saturation: deficits count existing useful coverage | `CounterScore` already subtracts own answers | kept; CounterNeed subtracts own answering CP; RoleDeficit uses own role CP; a role over `saturation` 1.3 × its share adds `role-saturated` (PURCHASE_ROLE_SATURATED) | change |
| 198 | Soft floors recon/AA/AT when the threat can appear; not hard | none | `ai.procurement.floors` 0.05/0.08/0.10 raise the role's want when plausible (aircraft/drones ever seen; heavy armour or ships ever seen; recon always); AA with none fielded after aircraft were seen is "strategic utility" (passes the map filter) | change |
| 208 | Time to value = delivery + rally + travel + time to firing region; late game favours fast | none | TimingFit = 1 − (DropDelay + travel to the nearest useful cell (firing band included)) / 90 s; from 480 s timing weighs up to ×2, cost down to ×0.5 | change |
| 209 | Capability replacement: a death raises the role deficit, not the same id | copies penalty only | lost units' CP per role adds to the role's want, decaying over `capabilitySeconds` 30 s | change |

## Part A (kept)

AiCommander tactic shares (`BuyScore`), `CounterScore`/`Fit`/`EnemyMix`, `NewCardScore`, `P25CardScore`, breacher / command /
carrier / counter-battery rules, commander fit, Very Hard massing, all-out saving, tower rebuilds, support strikes, deck
picking: all unchanged and still scored. The director adds and filters; it does not replace.

## API for the other lanes (P0-A targeting, P0-C boss/naval)

- `world.Topology` (`MapTopology`): `DomainOf(def)`, `Ground/Naval/Amphibious` (`DomainGraph.ComponentAt`, `NearestPassableCell`,
  `DistancesFrom`), `IsSea`, `Chokes`, `Objectives`, `Bottleneck(source, target)`.
- `world.Feasibility` (`EngagementFeasibility`): `Evaluate(def, ctx)`, `HasReachableFiringPosition(def, from, target, radius,
  layer)` (§47 "do not chase unreachable"), `CanReach`, `TravelSeconds`, `SpawnUseful` (§67), `LayerOf(world, v)`,
  `WeaponEnvelope.Of(def, layer)`, `Observed(...)` (fog-fair context).

## Open / risks

- Behaviour change: the hard filter and the master score shift purchases on every map; `blendWeight` 3 is a first guess for
  the lead's sweeps (Part P/V). The plan (§16) makes buying less reactive for up to 30 s.
- Topology cost: three flood fills + clearance on the 2 m grid at first use and at most every 5 s after ground changes; firing
  checks cached (≤ 20 000 entries). To be measured in the 48v48 gate.
- Amphibious = open grid cells (incl. any open sea cell): on real maps the sea is outside the outline, so it equals Ground plus
  shallow water.
- Not done here: §18 boss-phase reserve and "composition enough" (needs the P4 forecast); a chokes-per-lane `MainLanes` list
  (LaneMap serves); Part K's health-monitor counter `noMapInfluencePurchases` (stays 0 by construction; `Rejections` counts
  rejects).
