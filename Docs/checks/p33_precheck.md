# Prompt 33 L0: precheck (2026-10-02, lead pass)

Read from the code and data on `feature/p33-b1` (after prompt 31 L6); nothing run, nothing changed by this pass.

1. **Camera.** `Game/CameraControl/RtsCamera.cs`: orthographic, pitch fixed at 52 deg, yaw fixed per map (square maps
   -45 deg, long battlefields -90 deg; `_yaw` is readonly: **no rotation** by the player). Zoom is the orthographic
   half-height: 9 m (closest) to 42 m (`DefaultMaxZoom`; only the `-mb-overview` device check raises it). The camera
   stands 130 m back along its view (`Distance`; changes nothing on screen). Focus is clamped to the map's rectangle
   (or a mission's play area + margin). Screen: landscape only (`allowedAutorotateToLandscapeLeft/Right`, no
   portrait); Android aspect 1:1 to 2.4:1 (`androidMaxAspectRatio` 2.4), so 4:3, 16:9 and 20:9 are all in range. Widest
   view: 42 m x 2 = 84 m tall on screen, 84 x 2.4 = 202 m wide at 2.4:1; on the ground the 52 deg tilt stretches the
   height to 84 / sin 52 deg = 107 m.
2. **How reinforcements, trains, ships and aircraft come in.**
   - Bought cards (`EconomySystem.Deploy`): a ground vehicle lands by parachute at the drop zone (HQ, an outpost, a
     command vehicle's zone) `DeliverySeconds` = 3.5 s after the order; an aircraft flies in from the map's edge
     straight behind the zone (`EdgeBehind`), at once.
   - Siege defender's cards with a fortress line (`fortress.arrival`, rail or runway; `SiegeModes.NextArrival` through
     `Economy.Route`): `ArrivalLead` 10 s after the first order (one run at least `ArrivalGap` 16 s after the last),
     the vehicles appear at the stop, one behind another along the platform; the train or the aircraft is only the
     view's (`FortressView.StartRun`, its own clock: in over 9 s, 7 s standing, out over 9 s). No sim object, nothing
     at the edge.
   - Mission waves (`MissionEventSystem.Deliver`): at the wave's tick (after its 8-12 s warning), at spawn points
     worked out from the map (`SpawnPoints`: edges, rail heads = the ends of map route `rail` and the fortress line's
     first point inside the map, sea beaches, water landings, landing zones): ground vehicles drive in from the spot
     itself (they appear 0-6 m inside the edge, no entry gate); paratroops and pods 3.5 s / 6 s after a warning;
     aircraft over the edge of an air path. A rescued convoy and the allies' waves use the same points.
   - Ships (`NavalSystem.Joined`): a flagship is spawned where the mode puts it (a mission's boss x/z, Boss Rush's far
     lane, the Sandbox's coast); its fleet is spawned the next step round it (escorts abeam or on its lane, attack
     boats on their lane); landing craft come out of its well deck, air waves come in at `sea.airEntry`. All at the
     tick they are created, inside the map. Leaving: the flagship's run ends at the far lane's end (`Escaped`).
   - Boss trains: spawned at the mission's boss x/z (c4m05 x 128 on Ironport's quay line, c7m05 x 128 on Metro City's,
     c7m10's stage x 140 on Capital, c11m05's Gungnir x 140 on Rust Yard's siding), i.e. inside the map at the tick the
     mission (or stage) starts.
3. **Path costs by vehicle type.** No. One 2 m `NavGrid` (walkable or not, built once with the props' clearances), one
   `PathFinder` (A*, 8-way, plain distance), shared by every ground vehicle. The only extra costs are the parked-hull
   layers of `UnitCostField` (by side, not by type) paid by a vehicle re-planning after it got stuck (`PathCosts`). No
   area cost, no per-type mask, no water class (river water is a prop/tile matter of the builder). So DEEP_FORD waits
   (prompt 33 L3, lane A, writes it down).
4. **Wrecks.** A destroyed vehicle leaves the simulation (`RemoveDead`): its hulk is the view's only (EffectsDirector,
   no collider, no cover, not in the visibility). The map's own wreck props (`wreck_tank`, `wreck_truck`, `wreck_car`,
   `artillery_wreck`, balance.json `props`) are solid props: they block routes and (but for `artillery_wreck`,
   `blocksFire: false`) direct fire, like any building. The exception: the card `combat_wreck_car` ("Xe khi hỏng
   thành công sự", the wreck turret car).
5. **Stealth and sight.** `SimWorld.RefreshVisibility`: each spotter's reach (vision x optics, weather, the storm's
   half, team vision) times a per-target factor `sight`: stealthy aircraft (`VehicleDef.StealthSight` after 2.5 s
   without firing), a still scout's `StillCamouflage`, a camouflage net standing still (gear `Camouflage`, up to
   50 %); Ghillie mode and a gun pit cut the reach to `GhillieReveal`; smoke blocks the line (`Strikes.Obscures`, but
   for thermal sights); Kerr's side, guard towers and the Patriot's radar see through some of it. A FOREST tag can
   multiply the same `sight` factor by 0.7 (lane A, 33 L3).
6. **How Juggernaut, Nemesis and Gungnir move.** On the ground grid, like a tank: frame `train` (`BossMove.Rail`) is
   only a label today. Juggernaut (`armored_train`) and Nemesis (`nuke_train`) get `Move` commands to their route's
   waypoints (the mission's `boss.route`, through `MissionMode.DriveBoss`, or the map's `routes.rail` through
   `BossSystem.FollowRoute`, which runs a train back at the end of its line in the Boss Hunt) and path to them with the
   A* like any vehicle; the route's ground is kept clear by the builder (`FIXED_ROUTES`, 7 m either side). Gungnir
   (`rail_supergun`) is static (speed 0): placed at its spot on the Rust Yard siding and never moves. Nothing keeps a
   train on a line; vehicles on its way are pushed by the ordinary separation.
