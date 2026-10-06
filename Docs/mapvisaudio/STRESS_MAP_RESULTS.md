# Map stress results (generated)

Headless `Tools/simbuild/mapstress` (no Unity) over the spec BT scenes (`MapStressScenes.All`, lane
W2-A): the five "conquest" scenes run here as two-side layered-AI Conquest battles on the shipped
map (`AutoDeploy` off, roster topped up every 5 s, as the AI MASTER P5 48v48 harness does); the sixth,
`fortress_siege` (mode "siege"), needs `ModeSessions`' siege session and Unity play, reported skipped
here. Weather is presentation only (spec Q1): no Sim effect to measure; render/audio metrics and the
siege scene are the final part's own Unity-play pass. Never edit by hand: re-run the tool.

## 48v48 in an urban choke (`urban_choke_48v48`)

Map `metrocity_conquest`, 48 v 48 ground units, seed 7, 120 s measured after 10 s warm-up. Focus `choke` resolved to choke31 (StreetCanyon, 5.0 m) at (31.0,67.0); extras 0, wrecks seeded 0.

- whole step (AI ticks + world step): mean 1.131 ms, p99 3.525 ms, max 151.577 ms
- AiPerfCounters (per-system, lane W1-A P5 format):
  AI per-system cost over 2400 steps (ms/step, max ms, calls); total 0.858 ms/step
  Steering          0.308   10.806     2400
  PathRebuild       0.008    1.469     2400
  Tactical          0.031    1.520     4800
  Squad             0.178    4.634     4800
  Commander         0.052    1.896      240
  Procurement       0.004    1.498      218
  Targeting         0.244    5.824     2400
  Watchdog          0.019    1.172     2400
  Bosses            0.005    0.016     2400
  HealthMonitor     0.009    0.342      120
- routeFailures: SevereUnstuck 0 (0.00 per 10 unit-minutes), heavyRouteFailure 0
- spawnBlockEvents (TrafficStats.SpawnExitClears): 7
- chokeQueueSeconds: 7.0
- bossRouteReplanCount: 0
- navalCollisionEvents (MapTelemetry.NavalCloseApproachEvents): 0; naval reverse events (Health.Counters.NavalReverseAttempts): 0
- averageLosEngagementDistance: 43.5 m (62 samples)
- laneUsageShare: alt1 22.4%, boss 20.9%, main 15.7%, obj1_point_town 9.8%, alt3 9.7%
- staleChokesDropped: 0
- approach-route usage (maps.topology.telemetryApproaches forced on for this run): appr0_point_town/r0 8.4%, appr0_hq_1/r1 7.7%, appr1_point_east/r2 7.3%, appr1_point_town/r0 6.4%, appr0_point_west/r1 6.3%, appr1_point_town/r1 5.9%, appr0_point_west/r0 5.4%, appr1_hq_0/r1 4.6%
- Part K: blocked 0 (0.00), deadlocks 0, anomalies 2, stalledObjectives 3

## 48v48 open desert (`open_desert_48v48`)

Map `saltflat_conquest`, 48 v 48 ground units, seed 11, 120 s measured after 10 s warm-up. Focus `open` resolved to main lane middle at (0.0,0.0); extras 0, wrecks seeded 0.

- whole step (AI ticks + world step): mean 0.436 ms, p99 1.494 ms, max 153.079 ms
- AiPerfCounters (per-system, lane W1-A P5 format):
  AI per-system cost over 2400 steps (ms/step, max ms, calls); total 0.298 ms/step
  Steering          0.101    3.292     2400
  PathRebuild       0.001    0.590     2400
  Tactical          0.007    0.373     4800
  Squad             0.058    3.026     4800
  Commander         0.024    0.736      240
  Procurement       0.001    0.141      218
  Targeting         0.096    0.446     2400
  Watchdog          0.004    0.019     2400
  Bosses            0.003    0.027     2400
  HealthMonitor     0.004    0.174      120
- routeFailures: SevereUnstuck 0 (0.00 per 10 unit-minutes), heavyRouteFailure 0
- spawnBlockEvents (TrafficStats.SpawnExitClears): 23
- chokeQueueSeconds: 0.0
- bossRouteReplanCount: 0
- navalCollisionEvents (MapTelemetry.NavalCloseApproachEvents): 0; naval reverse events (Health.Counters.NavalReverseAttempts): 0
- averageLosEngagementDistance: 42.4 m (45 samples)
- laneUsageShare: boss 26.5%, alt1 15.1%, main 15.0%, obj1_point_east 13.7%, obj0_point_west 10.0%
- staleChokesDropped: 0
- approach-route usage (maps.topology.telemetryApproaches forced on for this run): appr1_point_east/r2 8.0%, appr1_point_town/r0 7.4%, appr1_hq_0/r0 7.4%, appr0_point_town/r0 6.6%, appr0_hq_1/r0 6.5%, appr1_point_east/r0 6.5%, appr1_point_town/r1 6.2%, appr0_point_west/r1 6.0%
- Part K: blocked 0 (0.00), deadlocks 1, anomalies 0, stalledObjectives 0

## Naval boss + escorts (`naval_boss_escorts`)

Map `lighthousebay_conquest`, 32 v 32 ground units, seed 13, 120 s measured after 10 s warm-up. Focus `naval` resolved to sea node hold_shore_near_3 at (53.7,-53.7); extras 11, wrecks seeded 0.

- whole step (AI ticks + world step): mean 1.003 ms, p99 3.973 ms, max 137.287 ms
- AiPerfCounters (per-system, lane W1-A P5 format):
  AI per-system cost over 2400 steps (ms/step, max ms, calls); total 0.433 ms/step
  Steering          0.163    5.128     2400
  PathRebuild       0.003    1.238     2400
  Tactical          0.003    0.184     4800
  Squad             0.083    8.480     4800
  Commander         0.023    4.497      240
  Procurement       0.002    0.126      218
  Targeting         0.128    0.693     2400
  Watchdog          0.006    0.892     2400
  Bosses            0.019    0.252     2400
  HealthMonitor     0.003    0.166      120
- routeFailures: SevereUnstuck 0 (0.00 per 10 unit-minutes), heavyRouteFailure 0
- spawnBlockEvents (TrafficStats.SpawnExitClears): 2
- chokeQueueSeconds: 4.0
- bossRouteReplanCount: 0
- navalCollisionEvents (MapTelemetry.NavalCloseApproachEvents): 1; naval reverse events (Health.Counters.NavalReverseAttempts): 0
- averageLosEngagementDistance: 28.8 m (2134 samples)
- laneUsageShare: alt1 35.5%, main 26.2%, boss 23.6%, alt2 10.8%, alt3 3.8%
- staleChokesDropped: 0
- approach-route usage (maps.topology.telemetryApproaches forced on for this run): appr0_point_town/r1 7.1%, appr0_hq_1/r1 7.1%, appr1_hq_0/r1 6.1%, appr1_point_east/r1 6.0%, appr1_point_town/r0 5.9%, appr1_hq_0/r0 5.5%, appr0_point_east/r1 5.4%, appr0_point_west/r0 4.8%
- Part K: blocked 0 (0.00), deadlocks 1, anomalies 1, stalledObjectives 1

## Fortress siege (`fortress_siege`)

Skipped here: mode `siege` needs `ModeSessions` and Unity play (see `STRESS_SCENES.json`'s `harness` field).

## Weather storm (`weather_storm`)

Map `junglepass_conquest`, 48 v 48 ground units, seed 19, 120 s measured after 10 s warm-up. Focus `open` resolved to main lane middle at (8.0,-4.0); extras 0, wrecks seeded 0.

- whole step (AI ticks + world step): mean 0.265 ms, p99 0.751 ms, max 52.809 ms
- AiPerfCounters (per-system, lane W1-A P5 format):
  AI per-system cost over 2400 steps (ms/step, max ms, calls); total 0.194 ms/step
  Steering          0.074    0.461     2400
  PathRebuild       0.001    0.348     2400
  Tactical          0.007    4.809     4800
  Squad             0.031    1.117     4800
  Commander         0.010    0.411      240
  Procurement       0.000    0.035      218
  Targeting         0.066    0.394     2400
  Watchdog          0.002    0.236     2400
  Bosses            0.001    0.002     2400
  HealthMonitor     0.002    0.070      120
- routeFailures: SevereUnstuck 0 (0.00 per 10 unit-minutes), heavyRouteFailure 0
- spawnBlockEvents (TrafficStats.SpawnExitClears): 35
- chokeQueueSeconds: 3.0
- bossRouteReplanCount: 0
- navalCollisionEvents (MapTelemetry.NavalCloseApproachEvents): 0; naval reverse events (Health.Counters.NavalReverseAttempts): 0
- averageLosEngagementDistance: 54.6 m (14 samples)
- laneUsageShare: alt2 24.8%, main 18.7%, obj1_point_west 14.9%, obj0_point_west 11.9%, boss 10.8%
- staleChokesDropped: 0
- approach-route usage (maps.topology.telemetryApproaches forced on for this run): appr0_point_east/r0 8.4%, appr0_point_town/r0 8.1%, appr0_hq_1/r0 8.1%, appr1_point_east/r1 7.5%, appr0_point_west/r0 7.3%, appr1_point_west/r0 6.3%, appr1_point_town/r0 5.5%, appr1_hq_0/r0 5.5%
- Part K: blocked 0 (0.00), deadlocks 3, anomalies 0, stalledObjectives 1

## Maximum wreck density (`wreck_density`)

Map `rustyard_conquest`, 48 v 48 ground units, seed 23, 120 s measured after 10 s warm-up. Focus `choke` resolved to choke21 (StreetCanyon, 7.0 m) at (-30.0,-40.0); extras 0, wrecks seeded 40.

- whole step (AI ticks + world step): mean 0.835 ms, p99 3.672 ms, max 54.528 ms
- AiPerfCounters (per-system, lane W1-A P5 format):
  AI per-system cost over 2400 steps (ms/step, max ms, calls); total 0.516 ms/step
  Steering          0.228   10.764     2400
  PathRebuild       0.014    1.753     2400
  Tactical          0.003    0.802     4800
  Squad             0.123    2.794     4800
  Commander         0.024    0.973      240
  Procurement       0.001    0.077      218
  Targeting         0.116    0.524     2400
  Watchdog          0.005    0.096     2400
  Bosses            0.001    0.004     2400
  HealthMonitor     0.002    0.091      120
- routeFailures: SevereUnstuck 0 (0.00 per 10 unit-minutes), heavyRouteFailure 0
- spawnBlockEvents (TrafficStats.SpawnExitClears): 50
- chokeQueueSeconds: 19.0
- bossRouteReplanCount: 0
- navalCollisionEvents (MapTelemetry.NavalCloseApproachEvents): 0; naval reverse events (Health.Counters.NavalReverseAttempts): 0
- averageLosEngagementDistance: 22.9 m (1875 samples)
- laneUsageShare: boss 20.1%, main 16.6%, alt2 14.9%, alt1 14.6%, alt3 11.0%
- staleChokesDropped: 0
- approach-route usage (maps.topology.telemetryApproaches forced on for this run): appr1_hq_0/r0 6.8%, appr0_hq_1/r0 6.3%, appr0_point_east/r1 6.2%, appr0_point_town/r0 6.0%, appr0_point_west/r1 5.7%, appr1_point_town/r1 5.7%, appr0_point_east/r0 5.6%, appr1_hq_0/r1 5.4%
- Part K: blocked 0 (0.00), deadlocks 1, anomalies 5, stalledObjectives 0

