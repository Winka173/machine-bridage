# Prompt 35: final report (rebuild of the stand-in and low-quality models)

Prompt 35 section 10 (Docs/prompts/prompt35_vi.txt), written by lane C after wave 11, on branch `feature/p35-w11`
with `lead/integration` merged in (waves 8 and 10 and the owner fixes included). Sources: REBUILD_LIST.md and
rebuild_list.csv (pass 0, the "before"), PILOT_REPORT.md and WAVE_1..11_REPORT.md, quality_report.csv after a full
gate run (`python Tools/assets/quality_gate.py`, 2026-10-03, the pre-rebuild gold kept: DECISIONS "Prompt 35: gold
recompute dropped"), the DECISIONS "Prompt 35" sections, and git (sizes, times). No Unity run, no test, sim or measure.

## 1. Numbers

| | count | notes |
|---|---|---|
| models reviewed (scored) | **230** | every GLB a def, a tower branch or an HQ draws (REBUILD_LIST: P1 129, P2 86, P3 15; 29 stand-ins found) |
| models rebuilt | **218** | P1 129 of 129, P2 82 of 86, P3 7 of 15 (zu23_technical, guard_tower / _a, ew_tower_a, missile_battery / _a / _b: bases rebuilt with their branches) |
| P2 not rebuilt | 4 | the owner-approved V2 gold models main_battle_tank, fighter_jet, attack_helicopter, silver_bug: they pass every gate as they are (merged-node names, decision 8) |
| P3 not rebuilt | 8 -> 0 | minefield_a, dragons_teeth_b, drone_mothership, ew_tower, ew_tower_b, nuke_train, recoilless_jeep, airborne_light_tank_chute: rebuilt in wave 12 (section 9) |
| NEEDS_HUMAN raised | **25** | pilot 2, wave 1 3, wave 2 10, wave 3 4, wave 5 3, wave 6 2, wave 7 1; waves 4, 8, 9, 10, 11: none |
| NEEDS_HUMAN still under 80 | 23 | ixion (89.8) and rocket_turret (83.5) now pass; the other 23 pass every hard gate (the 3 wave 1 structures accepted on the owner's look still score 57.6-70.9; list in section 5) |
| whole gate now | **202 of 230** | gold recomputed with the rebuilt models and recalibrated (owner answer 1, section 2 end): hard gates 230 of 230; soft Tốt 202, Cần sửa 21, Kém 7. Pre-rebuild gold: 199 (Tốt 199, Cần sửa 24, Kém 7); first recompute: 105; pass 0: Tốt 78, Cần sửa 89, Kém 63 |

Every rebuilt model is its own script and spec (`Tools/blender/mb_p35_<id>.py` or a wave module,
`Tools/blender/specs/<id>.json`), with a before / after sheet in `Docs/models/rebuild/<id>/` and the lead's Unity
ModelScan sheet where rendered. Every one keeps its id, runtime node names (Part_*, Mount_*, Muzzle_*), materials and
size within 10 % of its modelSize (or, without one, of its old file); added nodes are listed in each wave report.

## 2. Scores before / after by class (the 218 rebuilt models)

"Before" = pass 0's soft score (rebuild_list.csv); "after" = quality_report.csv now, same gate and gold.

| class | rebuilt | soft before (mean) | soft after (mean) | Tốt / Cần sửa / Kém before | after | hard gates pass before | after | triangles before -> after (mean) |
|---|---|---|---|---|---|---|---|---|
| tower | 60 | 59.3 | 80.7 | 7 / 21 / 32 | 41 / 15 / 4 | 26 | 60 | 5,232 -> 5,165 |
| wheeled | 42 | 74.2 | 93.1 | 13 / 23 / 6 | 42 / 0 / 0 | 3 | 42 | 3,417 -> 6,663 |
| tracked | 37 | 83.8 | 97.0 | 23 / 14 / 0 | 37 / 0 / 0 | 0 | 37 | 5,074 -> 9,569 |
| boss | 30 | 66.6 | 87.9 | 4 / 16 / 10 | 27 / 3 / 0 | 3 | 30 | 15,389 -> 17,655 |
| jet | 16 | 79.8 | 91.8 | 9 / 4 / 3 | 14 / 2 / 0 | 0 | 16 | 2,312 -> 3,832 |
| obstacle | 12 | 52.8 | 74.2 | 2 / 3 / 7 | 5 / 4 / 3 | 3 | 12 | 2,136 -> 4,230 |
| helicopter | 6 | 81.8 | 90.7 | 4 / 2 / 0 | 6 / 0 / 0 | 0 | 6 | 3,884 -> 5,550 |
| structure | 4 | 74.8 | 90.4 | 1 / 2 / 1 | 4 / 0 / 0 | 1 | 4 | 3,704 -> 6,141 |
| ship | 4 | 41.8 | 84.5 | 0 / 0 / 4 | 4 / 0 / 0 | 0 | 4 | 2,107 -> 9,033 |
| ground | 3 | 78.4 | 99.8 | 2 / 1 / 0 | 3 / 0 / 0 | 1 | 3 | 2,043 -> 4,749 |
| air_other | 2 | 71.6 | 89.2 | 0 / 2 / 0 | 2 / 0 / 0 | 1 | 2 | 2,937 -> 9,573 |
| hq | 2 | 95.0 | 96.2 | 2 / 0 / 0 | 2 / 0 / 0 | 0 | 2 | 10,073 -> 14,962 |
| **all** | **218** | **69.8** | **88.3** | 67 / 88 / 63 | 187 / 24 / 7 | 38 | 218 | |

Towers dropped in triangles on average (5,232 -> 5,165) while gaining score: the 25 old towers over the 1.5 x cap
(owner decision 6) were rebuilt under 6,000.

### Gold vs the new average (soft metrics, class means)

Gold = the four V2 models and the top 10 % of each class at pass 0 (section 5.3; GOLD_METRICS.md). "new" = the mean
of the rebuilt models scored against that set. A soft metric earns full marks at 80-100 % of the gold mean.

| gold set | gold members | rebuilt on it | silhouette gold / new | edges gold / new | regions gold / new | parts_m2 gold / new | tier2_m2 gold / new | tier3_m2 gold / new |
|---|---|---|---|---|---|---|---|---|
| tower | 7 | 60 | 2.47 / 2.22 | 0.30 / 0.20 | 12.37 / 8.58 | 0.95 / 0.74 | 1.42 / 0.83 | 0.66 / 0.49 |
| wheeled | 5 | 42 | 1.62 / 1.65 | 0.33 / 0.28 | 14.92 / 9.83 | 0.70 / 0.85 | 0.63 / 0.93 | 0.48 / 1.17 |
| tracked | 4 | 40 | 1.46 / 1.49 | 0.27 / 0.26 | 9.51 / 8.11 | 0.40 / 0.59 | 0.73 / 1.09 | 0.30 / 0.72 |
| jet | 2 | 16 | 1.42 / 1.43 | 0.18 / 0.21 | 6.32 / 9.29 | 0.88 / 1.62 | 0.65 / 1.34 | 1.36 / 2.82 |
| boss_ground | 2 | 15 | 1.76 / 1.86 | 0.25 / 0.16 | 7.53 / 4.33 | 0.52 / 0.72 | 1.02 / 1.45 | 0.95 / 2.60 |
| obstacle | 2 | 12 | 2.86 / 2.13 | 0.27 / 0.24 | 10.83 / 11.57 | 0.64 / 0.70 | 0.75 / 1.18 | 1.23 / 1.40 |
| boss_air | 2 | 7 | 1.76 / 1.85 | 0.15 / 0.12 | 3.99 / 3.22 | 1.63 / 1.95 | 1.10 / 2.40 | 4.11 / 10.07 |
| boss_sea | 1 | 6 | 1.48 / 1.37 | 0.12 / 0.09 | 2.82 / 1.84 | 1.90 / 1.56 | 1.50 / 1.24 | 7.96 / 6.48 |
| helicopter | 2 | 6 | 2.12 / 2.01 | 0.32 / 0.30 | 23.01 / 16.65 | 2.43 / 2.14 | 1.76 / 1.78 | 2.48 / 4.01 |
| structure | 1 | 4 | 2.21 / 2.10 | 0.17 / 0.17 | 5.85 / 6.73 | 0.62 / 0.92 | 1.00 / 0.93 | 0.26 / 0.67 |
| boss | 5 | 4 | 1.60 / 1.70 | 0.17 / 0.16 | 4.65 / 5.04 | 2.16 / 1.49 | 1.78 / 1.03 | 10.08 / 4.13 |
| air_other | 1 | 2 | 2.79 / 2.42 | 0.10 / 0.20 | 2.18 / 8.78 | 0.23 / 0.73 | 0.29 / 0.61 | 0.18 / 1.47 |
| boss_rail | 1 | 2 | 1.52 / 1.69 | 0.22 / 0.20 | 6.31 / 5.64 | 3.54 / 2.15 | 3.03 / 2.78 | 19.96 / 11.67 |
| hq | 1 | 2 | 1.80 / 1.93 | 0.16 / 0.14 | 4.63 / 4.21 | 0.44 / 0.52 | 0.77 / 0.74 | 0.48 / 0.69 |

Reading: the vehicles, jets, air bosses and ground bosses now pass their gold on detail density (parts, tier 2 and
tier 3 per m2: 1.2-2.5 x the gold) and match it on silhouette; they stay a little under it on brightness regions and
shading edges at the battle camera (the gold models are older, darker-painted and noisier). Towers and obstacles stay
under the gold on every density and on edges / regions: the seven-member tower gold is dense small gun towers with
railings and ladders, while the class also holds open gun pits, shelters, depots, hangars and helipads under the
6,000-triangle cap. Sea and rail bosses are near or under their single gold member (Leviathan rebuilt; the trains'
rails and sleepers count as thousands of small parts).

The gold sets were not recomputed (lead, 2026-10-03): rebuilt models carry no pass 8 visual grade, so a recompute
would shrink the sets to the old models left and drop 24 passes (lane A's run: 163 of 230).

### Gold recomputed with the rebuilt models (owner answer 1, lane A, 2026-10-03)

The owner allowed a rebuilt model that passes every hard gate with soft >= 80 to stand for gold (section 8 item 1).
Gate passes: **199** of 230 with the pre-rebuild gold, **105** after lane A's first recompute (one set per class,
top 10 %; the lead held it back because three of the four owner-approved V2 models failed it), **202** after the
recalibration now in `gold_metrics.json` (DECISIONS "Prompt 35: gold recompute with rebuilt models (lane A)"):

- mixed classes split into sets of like models: wheeled light / heavy, tracked light / heavy, jet drone / fighter /
  heavy, helicopter light / heavy, obstacle flat / wall / pad / tall, tower mast / small / big (boss frames as before);
- anchor: every gold member and every V2 model scores >= 80 against its own set leave-one-out, else the set widens
  (top 20 %, 25 %, down to the candidates' median); dense outliers never stand for gold; set value = median of members;
- a set without gold, or a sole member, borrows a similar set (sea boss <-> ship, HQ / structure -> big towers,
  river boats -> ship, air boss -> heavy jets), then its parent class.

V2 models against their own sets: main_battle_tank 82.8, fighter_jet 81.6, attack_helicopter 98.3, silver_bug 81.5.
Grades against the pre-rebuild gold: 33 change; Tốt -> Cần sửa 11, Cần sửa -> Tốt 14, Kém -> Cần sửa 4, Cần sửa -> Kém
4; soft Tốt 202, Cần sửa 21, Kém 7. "scored on it" counts each model under the set it is scored against now.

| gold set | members | how chosen | scored on it | pass old gold | first recompute | now |
|---|---|---|---|---|---|---|
| tower_big | c_ram_b, gun_turret, gun_turret_b, visual_jammer | top 10 % of 28 candidates; outliers left out: artillery_emplacement, barrage_balloon, c_ram, c_ram_a, gun_turret_a | 34 | 17 | 5 | 28 |
| wheeled_heavy | lancet_truck, long_sam, railgun_truck, wheeled_howitzer | top 10 % of 29 candidates; outliers left out: command_vehicle, heavy_rocket_artillery, towed_at_gun, wheeled_gun | 31 | 31 | 4 | 29 |
| tracked_heavy | airborne_light_tank, artillery, elite_mbt, heavy_tank, main_battle_tank, next_gen_tank, twin_tank | top 20 % of 29 candidates; outliers left out: bridging_vehicle, elite_tank_destroyer, mine_layer, sam_launcher, tank_destroyer | 30 | 30 | 29 | 30 |
| tower_small | mg_bunker_a, searchlight | top 10 % of 20 candidates; outliers left out: flare_tower, manpads_tower, recoilless_gun_tower | 20 | 18 | 4 | 20 |
| boss_ground | fortress_hive, supreme_command | top 10 % of 15 candidates; outliers left out: kronos, monster | 15 | 15 | 8 | 15 |
| obstacle_flat | dragons_teeth_a, minefield_a | top 10 % of 6 candidates; outliers left out: dragons_teeth_b | 13 | 6 | 1 | 6 |
| wheeled_light | recoilless_jeep, rocket_technical, zu23_technical | top 20 % of 11 candidates; outliers left out: scout_jeep | 12 | 12 | 6 | 9 |
| boss_air | drone_mothership, mega_gunship, silver_bug, stymphalos | top 25 % of 6 candidates; outliers left out: hyperion | 9 | 7 | 4 | 7 |
| tower_mast | ew_tower_a, ew_tower_b | top 10 % of 8 candidates; outliers left out: ew_tower | 9 | 9 | 9 | 9 |
| tracked_light | airborne_vehicle, ground_drone_carrier | top 10 % of 8 candidates | 8 | 8 | 8 | 8 |
| jet_heavy | heavy_bomber, swarm_carrier | top 10 % of 4 candidates; outliers left out: sky_gunship | 7 | 5 | 0 | 4 |
| boss_sea | leviathan, nyx | top 10 % of 6 candidates | 7 | 6 | 4 | 7 |
| jet_fighter | fighter_jet, prop_attack_plane | top 10 % of 4 candidates | 6 | 6 | 2 | 5 |
| helicopter_heavy | attack_helicopter, elite_attack_helicopter | top 10 % of 4 candidates | 5 | 5 | 4 | 5 |
| structure | bulwark_post, targeting_station | top 10 % of 2 candidates | 4 | 4 | 2 | 2 |
| jet_drone | recon_drone, strike_drone | top 10 % of 4 candidates | 4 | 4 | 4 | 4 |
| air_other | airborne_light_tank_chute, airborne_vehicle_chute | top 10 % of 2 candidates | 3 | 3 | 1 | 2 |
| boss_rail | armored_train, rail_supergun | top 10 % of 3 candidates; outliers left out: nuke_train | 3 | 3 | 2 | 3 |
| ground | hover_gunboat, river_patrol_boat | top 10 % of 3 candidates | 3 | 3 | 3 | 3 |
| ship | missile_boat | down to the median of 4 candidates; under the anchor, left out: sea_cruiser; sole member | 3 | 3 | 2 | 2 |
| hq | command_hq, headquarters | top 10 % of 2 candidates | 2 | 2 | 1 | 2 |
| helicopter_light | light_attack_heli, scout_heli | top 10 % of 2 candidates | 2 | 2 | 2 | 2 |

Reading: big towers gain most (17 -> 28: hangars, emplacements, flak, shelters no longer measured against slim masts).
Down: wheeled light (armored_car, radar_scout, interceptor_drone_vehicle under the jeep / technical gold), wheeled heavy
(fpv_carrier, microwave_vehicle), structure (coastal_battery 61.0, super_gun 64.3 against bulwark_post and
targeting_station, the only two candidates), drop_pod (against the two chutes), recon_jet and stealth_fighter, sea_cruiser
(left out of the ship gold by the anchor). Walls (no candidate of their own) and helipads borrow the flat set and fall to
Kém (helipad_b 57.8, wall_gun 55.9, wall_hesco 58.0, blast_wall 46.7); they failed the old gold too. Per-model scores:
quality_report.csv; per-set rules and metrics: GOLD_METRICS.md.

## 3. Kit components added

`Tools/blender/mb_kit35.py` is new in prompt 35 (pass 1): the parametric detail library with real-size defaults,
two-step chamfers and the standard part names the gate treats as kit pieces:

- **general**: chamfer_box, plate, panel, rivet_line, bolt_ring, weld, hinge, handle, hatch_round, hatch_rect, lamp,
  whip_antenna, mesh_antenna, dish, periscope, tow_hook, tow_cable, crate, jerrycan, backpack, net_roll, grille,
  exhaust; `rot_to` keeps wall fittings upright (pilot fix).
- **tracked**: road_wheel, sprocket, idler, return_roller, tracks, side_skirt (`bolts=False`, wave 2), fender,
  turret_ring, gun_barrel, roof_mg, pintle_mg (indexed mounts, `post=`, `riser=`, `ring_r=`, `cradle=`: the owner's
  roof-gun rule), smoke_dischargers, era_bricks (`bolts=False`), slat_cage, net_armour, `track_run` (lane B, wave 5).
- **wheeled**: truck_wheel, `tread_wheel` (the lean tyre, about 250 triangles; lane B, wave 2), axle, leaf_spring,
  windscreen, mirror, outrigger.
- **aircraft / heli**: wing, fin, intake, missile (nose direction fixed in wave 5), bomb, drop_tank, flare_dispenser,
  blade_antenna, landing_gear, pylon, rotor_head, tail_rotor, skids, stub_wing.
- **ship / rail**: ship_hull, railing, ladder (`facing=`, HQ pass), vls, ciws, rhib, radar_mast, rail_track, bogie;
  `clutter`, `plane`, `portholes`, `merge_parts` (lane B's, moved into the kit in the HQ pass).
- **structure**: footing, sandbag_wall (`round_both=`), wire_fence, hesco, t_wall, floodlight, door (frame posts
  fixed in wave 2, `frame_mat=` in wave 5), beacon, `sandbag_run(part=, lean=)`, `earth_pad(bottom=)`, `camo_net`.
- **bodies** (lane C, wave 5): ring_from_half, section_loft, slab_loft, ellipse_half, store (a lean missile / bomb).
- **boss**: armour_plate, breakable_panel, fuel_drum, smokestack, gun_cluster.
- **colour** (COLOR_0 after the bake): soot, dust, tone, team_band.
- `mb_kit27.sweep(v_up=)` (the profile's v follows `up`; HQ pass).

Lane helper modules (generic sub-assemblies, not models): `mb_p35b_parts.py` (lane B) and `mb_p35c_parts.py`
(lane C: running_gear, lugged_tyre, plain_wheel, roof_gun, gun_tube, stowage_box, jerry_rack, cable_reel, ammo_tins,
hatch, casings, duckboard, entrenching_tools, helmets, pickets, octagon, wheel_arm).

Gate and tools: `Tools/assets/quality_gate.py` (hard + soft gate, gold sets per boss frame, merged nodes from the spec,
the 1.5 x cap for units seen in numbers, roles only when the def has the system, kit wheels never shared geometry,
structure asymmetry read without the base slab, helicopter roles for tandems and unarmed transports),
`Tools/blender/specs/validate_specs.py`, `Tools/models/rebuild_inventory.py`, `Tools/models/sheet.py` and
`Tools/blender/render_angles.py` (the before / after sheets).

## 4. Average time per model

| | minutes per model |
|---|---|
| pilot (ixion, zu23_technical, rocket_turret, with the kit fixes they found) | 25-70 (PILOT_REPORT) |
| waves 2-11, cadence between "P35: <id>" commits in a lane (git) | 1.8-4.3 per wave, median **3.5** |
| a whole lane wave including set-up, specs, before renders, report (lane C, measured from its branch) | about **4**: wave 9 20 models in 82 min, wave 11 13 models in 52 min |

The waves ran three lanes in parallel, so the 218 models took about one working day of wall time after the pilot
(the pilot's estimate was 25-45 min a model, 110-150 agent hours). The one-off cost before the waves (inventory,
kit35, gate, specs) was about 3 hours.

## 5. Models still Kém, and the rest under 80

Kém (< 60), all rebuilt, every hard gate passes:

| model | score | why it stays low |
|---|---|---|
| troop_shelter | 51.3 | a low earth-covered shelter: a smooth berm and a flat roof against the tower gold's dense small gun towers; little silhouette and few brightness regions at the battle camera |
| bunker_shelter_tower | 51.5 | the same: a buried shelter, most of it under its berm |
| helipad | 52.5 | a flat pad kept 0.11 m high (the 10 % size rule): no silhouette, a symmetric top view; the lead allows a windsock and light posts (not built yet) |
| helipad_a | 54.1 | the same pad with its upgrade |
| wall_t | 57.1 | a wall segment: its top view is the full rectangle the wall system needs, so asymmetry stays at half marks; long plain faces |
| ammo_dump | 57.6 | a 6-15 m depot under the 6,000-triangle cap (decision 6): roofs and berms cannot reach the tower gold's edge density (accepted on the owner's look, wave 1 review) |
| inflatable_decoy | 57.6 | a smooth inflatable replica of the gun turret (it must read as the real tower, not as kit); its modelSize now draws it 1:1 (owner fix 4) |

Cần sửa (60-79), all rebuilt and accepted on the owner's look by the lead's calls (wave 1-6 reviews): towers and
structures (blast_wall 61.6, helipad_b 61.8, fire_control_centre 63.1, wall_gun 63.5, logistics_station 63.7,
artillery_emplacement_b 64.1, repair_bay 66.0, heavy_flak_tower 66.6, wall_hesco 69.9, radar_site 70.9,
guard_tower_b 71.2, drone_hangar 71.5, drone_hangar_b 71.5, heavy_turret_b 71.6, drone_hangar_a 71.8,
laser_ad_station 73.0, one_shot_atgm_tower 74.6, at_gun_emplacement 77.9, heavy_turret 78.0), the flying wings and
stealth airframes (garuda 67.2, stealth_naval_strike 67.5, stealth_bomber 71.0, morrigan 72.0: near-convex outlines,
symmetric top views, smooth skins with few brightness regions, and the jet rule forbids greebles) and typhon 69.1 (a
smooth submarine against the warship gold).

## 6. Integration (section 9)

- **GLB size: over the limit (fixed by quantisation, now +6.6 %: section 9).** Total of `Assets/MachineBrigade/Resources/Models/*.glb` (git LFS sizes; 518 files in
  both trees): pre-prompt-35 tree `01f7312b` 123.1 MiB -> now 168.4 MiB, **+36.7 %, over the 25 % limit**. All of the
  growth is in the 226 rebuilt files (218 models and their `_hd` twins: 80.4 -> 125.6 MiB, +56 %); no other file
  changed. (Against `07444b14`, 99.6 MiB with 400 files, the growth reads +69 %, but 118 files were added between the
  two trees by prompts 27-34, so `01f7312b` is the fair baseline.) The largest growth: monster +1.26 MiB, moloch +1.23,
  ixion +1.20, hyperion +0.89, sea_cruiser +0.71; wave 11 3.6 -> 7.5 MiB.
  Where the bytes are (all 518 files): POSITION 38.1 MiB, NORMAL 38.1, COLOR_0 38.1, TEXCOORD_0 25.4, indices 13.8;
  every attribute is stored as 32-bit floats. **Proposal (no model changed for it):** quantise at export
  (KHR_mesh_quantization, which glTFast reads): normals as normalized int8, COLOR_0 as normalized unsigned bytes, UVs
  as int16 (or dropped if MachineBrigade/Lit does not sample them). Estimated vertex data 153.6 -> about 90 MiB, total
  about 105 MiB: about -15 % against the pre-prompt-35 tree, with no visible change. LOD would not help the files
  (the runtime builds LOD1 and the impostor itself); merging meshes by material saves draw calls, not bytes.
  Second choice if quantisation is not wanted: the `_hd` twins of the rebuilt models (12 files) and the largest boss
  files could go through meshoptimizer's simplifier to the class maximum.
- **Draw calls / materials.** Every rebuilt model passes glb_check's renderer caps (merging by material where needed:
  logistics_station, the ships, stealth_fighter, airborne_vehicle_chute); the material separation (11-17 per model)
  is kept by the owner's call (pilot review 11).
- **Unity load check and preview pictures** for every rebuilt model: the lead's ModelScan / card passes after each
  merge (waves 1-10 done; wave 11's ids are listed in WAVE_11_REPORT.md: 13 to render, `drop_pod` and
  `airborne_vehicle_chute` have no card).
- **Gameplay data**: unchanged by the model work; the size rule was held everywhere. The data changes the owner asked
  for went through their own passes (zu23 / gun_turret_b barrels, the decoy's modelSize, kronos's gun_r node).
- **Export sheets** Model and Model_cham_diem: for the export pass (the lead's), not touched here.

## 7. Own decisions (chỗ tự quyết)

The main calls the lanes and the lead made without the owner (DECISIONS "Prompt 35 ..." for each):
1. Score classes: a class without gold borrows the nearest one (wheeled -> tracked, structure <-> tower, air_other ->
   helicopter, ship -> boss); each boss frame (ground, rail, air, sea) has its own gold (owner decision 5); the gold
   is not recomputed after the rebuild (rebuilt models have no visual grade).
2. Over-budget models are kept (owner rule 02/10) except units seen in numbers: light wheeled and towers under 1.5 x
   the class maximum (owner decision 6), a hard gate.
3. Visible weapons follow the data: a model draws the weapons its def fires; old pivots for weapons the def lacks stay
   as plain pivots (never removed, never drawn); a missing mount the gate asks for is added (Mount_APS, Mount_gun,
   Muzzle_missile ...), never a data change.
4. A role, mount or muzzle the kit merges into another node counts when the spec names the host (`merged`, owner
   decision 8); gate roles apply only when the def has the system (flares, MG, smoke, turret).
5. Towers drop the slab under the whole post (the ground is the floor); tower branches are rebuilt with their base in
   one module.
6. Size: the 10 % rule guards the footprint and the main body against modelSize (or the old file); a tower may grow
   taller (guard_tower_b); thin props above a flat pad are allowed.
7. References: unit_refs first; where a row was missing the lanes chose a real vehicle that fits the def's frame and
   size, and listed it for the owner (wave 4, wave 5); prompt 24's reserved list is respected (amphib_light_vehicle
   moved off AAV-7 in the owner fixes).
8. Variants keep their relationship: airborne_vehicle_chute calls the ground model's builder; the wreck / chute
   suffixes share a family for the own-geometry rule.
9. Builds that differ only by bake noise keep the gated file (hyperion after wave 11's merge, the HQ, two jets).
10. The thirteen GLBs of a wave are committed one per model ("P35: <id>") with the spec, the sheet and the baseline
    accept; the full gate is refreshed after each wave.

## 8. Owner questions

Status after DECISIONS "Prompt 35: owner review of the pilot", "owner review of wave 1", "Prompt 35: owner answers",
"Owner: open questions settled by the lead's proposals (2026-10-03)", "Owner fixes 2026-10-03" and the lead's calls
in each wave's DECISIONS.

**Still open**

1. **GLB size** was 36.7 % over the pre-prompt-35 tree (limit 25 %); lane A quantised the vertex attributes, now +6.6 % (section 9). Was: quantise vertex attributes at export (proposal
   in section 6), or simplify the largest files?
2. **Gold for rebuilt models**: allow a rebuilt model with every hard gate and soft >= 80 to stand for gold (lane A's
   question after its recompute), so the gold sets refill, or keep the pre-rebuild gold?
3. **The owner's look on the 31 rebuilt models under 80** (section 5): the lead accepted them on the look pending
   the owner's review of their sheets; the NEEDS_HUMAN among them: heavy_turret, heavy_turret_b, the drone_hangar
   family, artillery_emplacement_b, logistics_station, the helipad family (wave 2), at_gun_emplacement,
   heavy_flak_tower, one_shot_atgm_tower, laser_ad_station (wave 3), typhon, morrigan, stealth_bomber (wave 5),
   stealth_naval_strike, garuda (wave 6), guard_tower_b (wave 7, also grown from 1.8 to 4.6 m).
4. **headquarters.fortress_air's Bofors**: the HQ model draws one gun (the ground fortress's 120 mm); drawing the
   40 mm needs a data change (a model id of its own or hidden nodes).
5. **kronos gun_r's `at`**: the node now points at Mount_gun.002 (owner fix 6) but the hit point stays at the old
   Mount_gun place (4, -2, 9.4); move it to (3, -7, 9.6)?
6. **The P3 models left as they are** (answered: wave 12 rebuilt them, section 9) (minefield_a, dragons_teeth_b, drone_mothership, ew_tower, ew_tower_b,
   nuke_train, recoilless_jeep, airborne_light_tank_chute): leave, or a wave 12? airborne_light_tank_chute in
   particular is the air_other gold, and its ground model airborne_light_tank was rebuilt in wave 6.
7. **Over-guide triangles on non-capped classes** (kept by the 02/10 rule): e.g. airborne_vehicle_chute 13,056
   (air_other 7,000), auto_loader_howitzer 9,464 and the tracked average 9,569 (7,000), the bosses up to 39.6k (monster):
   fine on phones, or wait for the FPS measure?
8. **Helipads** (answered: built in wave 12, section 9): the lead allows a windsock and light posts above the flat pad; build them (it would lift the three
   pads' scores)?

**Answered** (kept for the record)

9. The pilot's eleven questions (QUESTIONS.md: Ixion's size and tyres, zu23 barrels, Hegemon tower twins later, tower
   branches with their base, the two pilots under 80, triangles, mara_behemoth's own id, merged node names,
   byte-identical builds, Ixion's stand-in note, materials per model): settled in the pilot review.
10. Wave 1: microwave_vehicle as a Leonidas-type emitter on a JLTV-type 4x4, elite_mlrs with M270 pods on the HIMARS
    truck, elites in team colours with black armour parts: kept (owner review of wave 1).
11. Wave 2: the low structures and pads accepted on the look (lead), helipad props allowed, gun_turret_b keeps two
    barrels with `barrels: 2` and the DPS unchanged.
12. Wave 3: the four gun towers and the walls / shelters accepted on the look; inflatable_decoy follows the new gun
    turret's outline (rebuilt in wave 6); super_gun in the fortress concrete style.
13. **References** (waves 4, 5, 7, 8, 9): aa_gun_vehicle CV9040 AAV, shorad_vehicle Avenger, demolition_line_vehicle
    M1150 ABV, river_patrol_boat PBR / SURC, towed_at_gun 2A45M, recon_jet SR-71, aa_57mm_vehicle 2S38,
    gps_jammer_vehicle EW truck: kept; fpv_carrier as an RG-33L: fine.
14. **amphib_light_vehicle on AAV-7** (prompt 24's reserved list): moved off it; rebuilt by lane A as an AMX-10P-pattern
    amphibious IFV (owner fix 2; 95.0 Tốt).
15. Wave 5: typhon's silo ahead of the sail (the real layout); typhon, stealth_bomber, morrigan accepted on the look.
16. Wave 6: the flying wings accepted on the look; the small craft's pintle Gatling and Zodiac / raft canisters fine.
17. **inflatable_decoy's modelSize**: set to its own box, 7.81 x 6.74 x 3.96, so it draws at the real gun turret's size
    (owner fix 4).
18. Wave 7: guard_tower_b as a gun nest on the blockhouse (lead, pending the look: open question 3);
    elite_tank_destroyer now draws its def's 105 mm; elite_aa keeps the def's twin 35 mm.
19. Wave 8: railgun_truck as its own heavy 8x8 with Tempest's twin rails: approved; the fortress HQ types get a
    visible gun: approved and built (the 120 mm L/55 tower; open question 4 for the Bofors).
20. **iron_beam truck vs tower**: stays a truck (the data has it mobile).
21. **kronos's Mount_gun pointer**: gun_r's node now `Mount_gun.002` (owner fix 6; open question 5 for its `at`).
22. **ballistic_launcher's raised missile**: one missile raised 22 degrees, kept.
23. **supreme_command's wheels vs a tracked frame**: keeps its wheels (MZKT-7930) and the 11 m mast.
24. Wave 10: rail_supergun's lighter 11.9k file is fine; the gold recompute was tried and dropped by the lead (open
    question 2).
25. Wave 11: no new question; the GLB size (open question 1) comes from section 9.

## 9. GLB size (section 9, lane A)

The over-limit size of section 6 is fixed by vertex quantisation; no model's look, geometry, nodes or materials changed.

- **Importer**: `com.unity.cloud.gltfast` 6.20.0 (Packages/manifest.json). It reads `KHR_mesh_quantization` out of
  the box (Documentation~/features.md; `GltfImport.k_SupportedExtensions`; int8 normalized normals and uint16 colours
  have their own Burst jobs, strided views included). Draco and `EXT_meshopt_compression` need the
  `com.unity.cloud.draco` / meshopt packages, which the project does not have: not used.
- **What is written** (`Tools/assets/glb_quantize.py`, pure Python + numpy, run by `frontier_kit.export_collection`
  right after Blender's glTF export, and once over all 518 committed files): NORMAL float32 -> normalized int8 (unit
  length first, worst error 0.33 degree; glTFast renormalises on import); COLOR_0 float32 -> normalized uint16, still
  VEC3 (error under 8e-6). Kept as float32: POSITION (an int16 position needs a scale on the node, which would change
  the hierarchy's transforms) and TEXCOORD_0 (the box-projected UVs run past 0-1, and unnormalized int16 needs
  KHR_texture_transform on a texture these flat materials do not have). Node names, hierarchy, materials, extras and
  indices are untouched; `KHR_mesh_quantization` is added to extensionsUsed and extensionsRequired. Deterministic
  and idempotent (a second pass changes 0 files).
- **Size** (518 files, git LFS sizes): pre-prompt-35 tree `01f7312b` 123.1 MiB (129,124,680 bytes); before this
  change 168.4 MiB (+36.7 %); **now 131.3 MiB (137,671,980 bytes), +6.6 %**, under the 25 % limit (-22.0 % on the
  files). NORMAL 38.1 -> 12.7 MiB, COLOR_0 38.1 -> 25.4 MiB.
- **Checks** (readers dequantise: `glb_analyze.accessor` now decodes signed normalized as max(c / 127, -1)):
  glb_check: 518 files, 0 errors; every record identical except fileBytes, sha1, extensions, and COLOR_0 statistics
  on 34 files that move by one step in the 4th decimal (rounding); baseline accepted with a reason. Full gate: 230
  models, 199 pass (as before); triangles, parts, hard gates, soft scores and grades identical for every model; 16
  raw metric cells moved in the 4th decimal (c0_p05 x 11, c0_dust x 2, c0_p95 x 2, recoilless_jeep edges 0.3986 ->
  0.3983), no score moved.
- Not taken: COLOR_0 as 8-bit (total about 112 MiB, -9 % against `01f7312b`) shifts the COLOR_0 numbers by up to
  0.002 in linear light, so the gate would not read the same; it stays an option.
- **Unity check (lead)**: reimport the GLBs, CatalogCheck, then render the cards / ModelPreview sheets of
  main_battle_tank, monster and ammo_crate and compare them with the previous renders (luma within the 1 % card
  gate, no "unsupported extension" or ColorFormatUnsupported errors in the import log).
## 9. Wave 12 (lane C)

The owner's answers on section 8 (DECISIONS "Prompt 35: owner answers on REBUILD_REPORT section 8") added a wave 12:
the eight P3 models rebuilt from scratch and the three helipads lifted with a windsock, light posts and real heliport
furniture (report: Docs/models/WAVE_12_REPORT.md). All eleven pass every hard gate; the P3 eight score 94.2-100
(dragons_teeth_b 83.2 -> 100, drone_mothership 94.1 -> 98.6, the rest held or up); the helipads rise from
52.5 / 54.1 / 61.8 to 72.5 / 74.5 / 70.2 (still under 80: a flat pad), so helipad and helipad_a leave the Kém list of
section 5. With wave 12, models rebuilt: 226 of 230 (P3 15 of 15); the 4 not rebuilt are the owner-approved V2 gold
models. Whole gate after the wave (`--no-write`): 199 of 230 pass, hard gates 230 of 230. GLB total: 170.4 MiB
(+38.4 % on the pre-prompt-35 tree; the eleven files 5.9 -> 7.9 MiB). New open question: nuke_train's `locomotive`
hit point sits on the launcher car (WAVE_12_REPORT, owner questions). The gold recompute the owner asked for after
wave 12 is the lead's step (`quality_gate.py --gold`), not run here.
