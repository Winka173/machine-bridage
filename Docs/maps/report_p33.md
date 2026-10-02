# Prompt 33 report: maps (four zones, edges, terrain, sea routes, rails)

Done locally on 2026-10-02 in five passes (DECISIONS "Prompt 33 L0/L4/L5", "L1/L6", "L2/L3", "L2 view / L7"). No Unity
runs, tests or sims; Python tools, Blender and the map tools only. Unity compile 0 errors after each merge.

## Pass 0 results (Docs/checks/p33_precheck.md)
1. Camera: orthographic, zoom 9-42 m (long maps 50), pitch fixed 52°, yaw fixed per map (no rotation), landscape only,
   aspect 1:1 to 2.4:1.
2. Arrivals: bought cards parachute in after 3.5 s; aircraft cross the map edge; Siege rail and runway arrivals were
   view-only; mission waves appeared at their spawn points with no entry gate; ships and boss trains spawned inside.
3. Pathfinding has no per-vehicle-type area cost, so DEEP_FORD is deferred.
4. Wrecks of destroyed vehicles are view-only; placed wreck props block movement and fire (combat_wreck_car excepted).
5. Sight is a per-target factor (stealth, still camouflage, camo nets), plus ghillie, gun pits and smoke.
6. Juggernaut and Nemesis drove by ground A*; Gungnir is static.

## What was built
- **Four zones** (play, edge band 12-20 m, outer ring, horizon): the ring covers the widest camera frame + 15 %:
  square maps 120 m, long maps 73 m (sides) / 128 m (ends); fixed seed per map. Data: `map_dressing.json`.
- **Edges**: `edges` on all 100 map files (SEA: Stormbeach, Beacon Bay/Lighthouse Bay, Coral Keys, Ironport,
  Rust Yard square; RIVER: Border Crossing, Capital, Hollow Dam, Mirewood; URBAN: the four city maps; CLIFF stretches on
  seven maps); the view follows each edge type (sea to the horizon, shores, cliffs, harbour/industrial sets) with 10
  prebuilt corner pieces; Rust Yard's sea-side scenery removed.
- **Ingress contract**: 3,200 entry gates; scripted waves enter at a gate four abreast, rows 20 ticks apart; view-only
  stand-ins outside the map.
- **Terrain tags** on the NavGrid: ROAD 13.9 %, ROUGH 8.0 %, FOREST 5.1 % (enemy sight x0.7), SHALLOW_WATER 0.9 %
  (amphibious and hover units not slowed); versus files keep a tag only where its mirror cell has it.
- **Landmarks**: 75 (3 per battlefield) with EN/VI names matching the dialogue; 7 new landmark models.
- **Sea routes**: SeaRouteGraph on the three Lighthouse Bay files (29 nodes, 8 holding nodes, 36 segments).
- **Rails**: RailSpline on 21 files (Ironport, Metro City, Capital, Rust Yard, Foundry and 11 Siege maps), level
  crossings OPEN -> WARNING -> CLOSED -> TRAIN_PASSING; Juggernaut and Nemesis now ride rails.
- **Biome dressing**: 38 decoration models for 8 biomes; densities per biome in DECISIONS (about +20 % triangles on
  a square temperate map before culling).
- **Validators**: `Tools/maps/validate_p33.py`, 12 checks: 0 errors, 26 warnings.

## Validator warnings left (judged, not fixed)
- 13 prop models drawn as landmark looks.
- 6 rail gates on blocked ground (Siege line on Metro City, Orbital Gate, Whiteout; Rust Yard siding on conquest,
  sandbox, siege).
- The 2 old check_access failures (swamp_conquest, veyra_old_quarter_conquest).
- Ironport crossing x2 warns only (a drop zone stands on it).
- 10 m passages hold 46 % of Capital's ground and 49 % of Swamp Siege's.

## Maps whose outer ring was fixed
Rust Yard's three square files (houses/forest on the sea side removed); every SEA map now draws water to the horizon.

## Map audit
After the RED fixes (owner's call, DECISIONS "RED map fixes"): 0 RED / 100 YELLOW (was 9 RED / 91 YELLOW before
prompt 33; terrain travel time took Hollow Dam out of RED).

## Own decisions worth a look
- DEEP_FORD deferred (no per-type path cost).
- Spawn points snap to the nearest gate within 30 m (else a gate is made where they stand).
- The path finder's heuristic is scaled x0.83 for terrain costs: more nodes per search (needs a CPU measure).
- Landmarks are decoration only; three stand far from their dialogue place (Capital's palace 138 m, Ember Ridge's
  cooling tower 123 m, Red Rock's church 120 m) because the capture circles leave no room nearer.
- Waiting for the owner: far-zoom edge shots per biome (Unity renders), FPS with the denser dressing.
