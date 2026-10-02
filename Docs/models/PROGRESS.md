# Prompt 27 progress and wave plan

Date 2026-10-02. Decisions: DECISIONS "27 checkpoint 1" and "27 preview + budgets + art bible". Rules for each model:
Docs/models/art-bible.md section 11 (the EXPERIMENT_1 recipe with the static gates); budgets: Docs/models/BUDGETS.md.
Tables generated from `balance.json`, `Tools/assets/baseline.json` and a static scan of `all_builders()` (the module
whose `BUILDERS` names the model last; `_hd` files are the same builder with `detail=True` unless round 6 or
p25_models2 own one).

## Done

| step | what | where |
|---|---|---|
| 1-2 | Step 0 audit, GLB analyzer / validator / baseline | STEP0_AUDIT.md, BASELINE.md, Tools/assets/ |
| 3-4 | Experiment 1 (V2 kit) on main_battle_tank, fighter_jet, silver_bug, attack_helicopter (+ `_hd`); checkpoint 1 approved | EXPERIMENT_1.md, `mb_p27_experiment.py` |
| 5 | Unity preview (`ModelPreview.RenderBatch -mbPreview`), budgets in the validator, Art Bible, this plan | Tools/assets/README.md, BUDGETS.md, art-bible.md |
| 6 | Benchmarks, frame time, device tests: wait for the owner's word on measuring | - |

## Rules for every wave

- **Stand-ins.** A wave that builds a stand-in's real model points that def at the new model (balance.json `model`,
  dropping its `tint` when the new model has its own colours), renders its card, and strikes its line in
  Docs/ASSET_DEBT.md in the same commit. **Never change a stand-in's pointer otherwise** (DECISIONS "27 checkpoint
  1"): not to "fix" a validator warning, not for a borrowed model's rebuild.
- A borrowed model rebuilt in a later wave (engineer_vehicle, ew_jammer, leviathan ...) changes how its stand-ins
  look until their own wave: check their cards too (CardRenders re-renders on hash change).
- One model per commit: baseline row, builder in the wave's module (merged last in `all_builders()`), rebuild normal
  and `_hd`, `glb_check.py` (no new error, gates), card render, `ModelPreview -mbPreview "<id>"` before and after,
  `glb_check.py --accept <names> --reason "..."`, commit. New builders: `Tools/blender/mb_p27_wave<N>.py`.
- Static gates only (validator, card luminance, preview luma). No EditMode suite, sims or measures until the owner
  allows them. Sonnet may run a wave on this recipe; opus reviews each wave's first model.
- Status per model: todo / built / gated / committed. All rows below are **todo** unless marked.

## Wave 1: the stand-ins (ASSET_DEBT)

Order: 1a Ixion and Gungnir, 1b the eight batch D bosses, 1c the 32 batch B units. Each new model gets its own id
(the def's id, e.g. `kraken.glb`) unless noted; the parent model is not touched. Items that need game code as well as a
model (the lead decides whether a wave may touch runtime code): Stymphalos (eight separate drone units, a swarm rule),
`ground_drone_carrier` (a minion-spawn mechanism), `combat_wreck_car` (a wreck-turret prop), Ixion's own mines,
Gungnir's line warning, `airborne_light_tank_chute` (its own parachute canopy model only).

### Wave 1a: prompt 26 pass 2 stand-ins (Ixion, Gungnir) - **committed** (DECISIONS "27 wave 1a + 1b (part)")

| def | current pointer (model) | its builder | tris now | new model / notes |
|---|---|---|---:|---|
| `ixion` (**committed**: `ixion`, 17,324 tris, mb_p27_wave1a) | `railgun_truck` (fitted to 26 x 12 x 10 m, mine-yellow tint) | mb_p25_models2 | 2,324 | new `ixion` builder: armoured BelAZ-75710 box body, welded T-72 turret, left-offset cab, six big tyres, V ram; nodes for parts `reartyre`, `hulltower`; own mine model. An unlisted `ixion.glb` already ships (21,628 tris, builder mb_redesign_20y): check it against the brief before building anew |
| `rail_supergun` (Gungnir) (**committed**: 36,726 tris, mb_p27_wave1a; `rail_tractor` 4,406) | `rail_supergun` (the old railway gun) | mb_p16_arms | 28,756 | rebuild in place: EMRG rail car, capacitor cars, a modern diesel (post-1945); keep boss part nodes; the line warning is game code (not this wave) |

### Wave 1b: prompt 25 batch D stand-in bosses - **all eight committed** (DECISIONS "27 wave 1a + 1b (part)", "27 wave 1b (lead pass, 2026-10-02)")

| def | current pointer | its builder | modelSize | the real model (ASSET_DEBT) |
|---|---|---|---|---|
| `kraken` (**committed**: `kraken`, 10,796 tris, mb_p27_wave1b) | `leviathan` (blue wash, 110 m) | mb_naval | 110 x 18.4 x 24 | a Nimitz / Kuznetsov carrier: flat deck, island to starboard, aircraft parked, lifts, arresting cable, 4 CIWS, 2 SAM mounts |
| `monster` (**committed**: `monster`, 23,066 tris, mb_p27_wave1b) | `fortress_bastion` (sand wash) | mb_p20_bosses | 40.3 x 22.1 x 13 | a Landkreuzer P. 1500: four track clusters (`Part_track_*`), one 800 mm barrel half the hull long (`Part_barrel`), 2 turrets, 4 flak |
| `garuda` (**committed**: `garuda`, 2,840 tris, mb_p27_wave1b; modelSize 27.9 x 70 x 4.5 added) | `command_airship` (violet wash) | mb_p20_bosses | (boss size) | a B-2 / Ho 229 flying wing, 70 m span, sawtooth trailing edge, opening bomb bay, 6 defensive turrets |
| `hyperion` (**committed**: `hyperion`, 7,914 tris, mb_p27_wave1b; silver_bug untouched) | `silver_bug` (amber wash) | mb_p27_experiment | 67.2 x 43.7 x 20 | a hexagonal mirror ring round a core with long solar panels, 4 point-defence lasers, 2 landing pods |
| `stymphalos` (**committed**: `stymphalos`, 4,186 tris, + `stymphalos_drone` 502, mb_p27_wave1b; modelSize 15.5 x 26 x 2.55 added) | `drone_mothership` (green wash) | mb_p20_bosses | (boss size) | eight delta-wing jet drones in V formation (separate units, 1,300 health each; a swarm rule) |
| `nyx` (**committed**: `nyx`, 3,526 tris, mb_p27_wave1b) | `leviathan` (steel wash) | mb_naval | 53 x 8.9 x 11 | a Zumwalt-style tumblehome hull, pyramid superstructure, railgun, 2 CIWS |
| `cerberus` (**committed**: `cerberus`, 11,848 tris, mb_p27_wave1b) | `behemoth` (red wash) | mb_p20_bosses | 16.3 x 8.4 x 5.5 | three big-wheeled trucks joined by couplings: 125 mm tractor, anti-air middle, rocket trailer (middle first breaks the AA) |
| `hydra` (**committed**: `hydra_sub`, 7,268 tris, mb_p27_wave1b) | `typhon` (teal wash) | mb_redesign_20y | 34.8 x 7.2 x 8 | a small submarine with vertical launch tubes along the back and six FPV drones |

### Wave 1c: prompt 25 batch B stand-in units (complete: pass A 16 rows, pass B 16 rows; 02/10)

| def | current pointer | its builder | class | the real model (ASSET_DEBT) |
|---|---|---|---|---|
| `aa_57mm_vehicle` (**committed**: `aa_57mm_vehicle`, 6,028 tris, mb_p27_wave1c) | `aa_gun_vehicle` (a green wash) | mb_p25_new | ground | a 2S38 Derivatsiya-PVO: a tracked chassis with a boxy 57 mm autoloading turret |
| `mine_rocket_truck` (**committed**: `mine_rocket_truck`, 5,012 tris, mb_p27_wave1c) | `mlrs` (a tan wash) | mb_p25_models2 | ground | a BM-27 Uragan-class wheeled rocket truck with a mine-dispensing rocket pod |
| `prop_attack_plane` (**committed**: `prop_attack_plane`, 2,634 tris, mb_p27_wave1c) | `attack_jet` (an olive wash) | mb_p25_models2 | jet | an EMB-314 Super Tucano / OV-10 Bronco: a small single-engine turboprop, a bubble canopy |
| `light_attack_heli` (**committed**: `light_attack_heli`, 3,058 tris, mb_p27_wave1c) | `scout_heli` (a tan wash) | mb_p25_models2 | helicopter | a small stub-winged attack helicopter (AH-1Z Viper light / Mi-28 class) |
| `next_gen_tank` (**committed**: `next_gen_tank`, 6,512 tris, mb_p27_wave1c) | `main_battle_tank` (a blue-grey wash) | mb_p27_experiment | ground | a T-14 Armata: an unmanned low-profile turret set well back on the hull |
| `demolition_line_vehicle` (**committed**: `demolition_line_vehicle`, 6,202 tris, mb_p27_wave1c) | `engineer_vehicle` (a violet wash) | mb_p25_models2 | ground | an M58 MICLIC: a mine-roller frame ahead of the hull and a line-charge rocket rack on the rear deck |
| `combat_wreck_car` (**committed**: `combat_wreck_car`, 2,794 tris, mb_p27_wave1c) | `armored_car` (a yellow wash) | mb_p25_models | ground | a light car whose wreck resolves into a standing gun pit (a new wreck-turret prop, not just a model) |
| `drone_hijack_vehicle` (**committed**: `drone_hijack_vehicle`, 3,446 tris, mb_p27_wave1c) | `ew_jammer` (a cyan wash) | mb_p25_models2 | ground | an EW vehicle with a directional hijack antenna array, distinct from the visual jammer and the GPS jammer |
| `manpads_tower` (**committed**: `manpads_tower`, 1,750 tris, mb_p27_wave1c) | `shield_tower` (a tan wash) | mb_p17_temp | structure | a sandbagged pit with two shoulder-launched MANPADS tubes on a low tripod |
| `river_patrol_boat` (**committed**: `river_patrol_boat`, 1,624 tris, mb_p27_wave1c) | `armored_car` (a blue wash) | mb_p25_models | ground | a Mark VI / Riverine Command Boat hull: a shallow-draft aluminium boat, a pintle MG and a grenade launcher |
| `river_gunboat` (**committed**: `river_gunboat`, 2,302 tris, mb_p27_wave1c) | `artillery` (an orange wash) | mb_p25_models2 | ground | a Buyan-class river gunboat: a low hull, a forward 100 mm turret |
| `coastal_ashm_vehicle` (**committed**: `coastal_ashm_vehicle`, 3,508 tris, mb_p27_wave1c) | `sam_launcher` (a green wash) | mb_p25_models2 | ground | an NSM Coastal Defence truck: angled missile canisters on a flatbed |
| `auto_loader_howitzer` (**committed**: `auto_loader_howitzer`, 6,520 tris, mb_p27_wave1c) | `artillery` (an olive wash) | mb_p25_models2 | ground | an XM2001 Crusader: a low-profile tracked self-propelled howitzer with an autoloader bustle |
| `amphib_light_vehicle` (**committed**: `amphib_light_vehicle`, 4,606 tris, mb_p27_wave1c) | `ifv` (a sage wash) | mb_p25_models2 | ground | an EFV / AAV-7: a boat-hulled tracked APC with a bow planing trim vane |
| `airborne_light_tank` (**committed**: `airborne_light_tank`, 5,550 tris + `airborne_light_tank_chute`, 3,514 tris, mb_p27_wave1c) | `light_tank` (a magenta wash) | mb_p25_models2 | ground | an M8 AGS / M10 Booker: a light tank hull with a low-profile 105 mm turret, and its own parachute canopy Also `airborne_light_tank_chute`. |
| `stealth_naval_strike` (**committed**: `stealth_naval_strike`, 2,124 tris, mb_p27_wave1c) | `stealth_bomber` (a steel-blue wash) | mb_p25_models2 | jet | an A-12 Avenger II: a flying-wing stealth strike aircraft, carrier folding wingtips |
| `twin_rotor_gunship` (**committed**: `twin_rotor_gunship`, 3,422 tris, mb_p27_wave1c) | `sky_gunship` (a khaki wash) | mb_p25_models | jet | an ACH-47A "Guns-A-Go-Go": a CH-47 tandem-rotor airframe with side gun mounts and a nose turret |
| `ground_drone_carrier` (**committed**: `ground_drone_carrier`, 4,274 tris, mb_p27_wave1c) | `interceptor_drone_vehicle` (a teal wash) | mb_p25_new | ground | a THeMIS / Uran-9 mothership plus three small tracked minion robots (needs a minion-spawn mechanism too) |
| `mobile_repair_vehicle` (**committed**: `mobile_repair_vehicle`, 3,668 tris, mb_p27_wave1c) | `engineer_vehicle` (a mauve wash) | mb_p25_models2 | ground | an MTO-UB: a wheeled repair truck with a crane and a welding rig |
| `radar_support_vehicle` (**committed**: `radar_support_vehicle`, 3,368 tris, mb_p27_wave1c) | `radar_scout` (a sky-blue wash) | mb_p25_new | ground | a Giraffe AMB / Kasta: a boxy radar cabin on a mast, raised when stationary |
| `towed_at_gun` (**committed**: `towed_at_gun`, 1,996 tris, mb_p27_wave1c) | `tank_destroyer` (a sand wash) | mb_p25_models2 | ground | a 2A45 Sprut-B: a long-barrelled towed gun on a split trail carriage, no armour |
| `flare_searchlight_tower` (**committed**: `flare_searchlight_tower`, 2,296 tris, mb_p27_wave1c) | `flare_tower` (a teal wash) | mb_p25_new | tower | its own small-slot flare launcher post (the medium-slot flare_tower, shrunk) |
| `recoilless_gun_tower` (**committed**: `recoilless_gun_tower`, 2,318 tris, mb_p27_wave1c) | `at_gun_emplacement` (a violet wash) | mb_p25_new | tower | an SPG-9 Kopyo emplacement: a small sandbagged pit, a short stubby recoilless tube |
| `bunker_shelter_tower` (**committed**: `bunker_shelter_tower`, 1,228 tris, mb_p27_wave1c) | `troop_shelter` (a green wash) | mb_p25_new | structure | a bigger concrete bunker (the medium-slot troop_shelter, grown) |
| `dazzler_vehicle` (**committed**: `dazzler_vehicle`, 4,640 tris, mb_p27_wave1c) | `ew_jammer` (a gold wash) | mb_p25_models2 | ground | a Peresvet-class dazzler: a boxy vehicle with a large forward-facing lens array |
| `ground_cruise_missile_vehicle` (**committed**: `ground_cruise_missile_vehicle`, 3,868 tris, mb_p27_wave1c) | `sam_launcher` (a rose wash) | mb_p25_models2 | ground | a Typhon MRC: a trailer with two long vertical missile canisters |
| `aerial_tanker` (**committed**: `aerial_tanker`, 3,220 tris, mb_p27_wave1c) | `heavy_bomber` (a periwinkle wash) | mb_p25_models2 | jet | a KC-135 / Il-78: an airliner-shaped tanker with a boom or drogue pod under the tail |
| `heavy_lift_helicopter` (**committed**: `heavy_lift_helicopter`, 3,138 tris, mb_p27_wave1c) | `gunship_heli` (a coral wash) | mb_p25_models2 | helicopter | a CH-47 / Mi-26: a big tandem or single heavy-lift rotor helicopter with a cargo hook |
| `bridging_vehicle` (**committed**: `bridging_vehicle`, 5,148 tris, mb_p27_wave1c) | `engineer_vehicle` (a mint wash) | mb_p25_models2 | ground | an AVLB / MTU-72: a tank hull carrying a folded scissor bridge span |
| `gps_jammer_vehicle` (**committed**: `gps_jammer_vehicle`, 4,396 tris, mb_p27_wave1c) | `ew_jammer` (a periwinkle wash) | mb_p25_models2 | ground | a Pole-21-class jammer: a mast-mounted antenna array on a truck bed, distinct from the visual jammer |
| `drone_net_tower` (**committed**: `drone_net_tower`, 1,378 tris, mb_p27_wave1c) | `laser_ad_station` (a pink wash) | mb_p25_new | tower | a net corridor: two poles with anti-drone netting strung wide between them, no turret |
| `one_shot_atgm_tower` (**committed**: `one_shot_atgm_tower`, 2,186 tris, mb_p27_wave1c) | `atgm_tower` (a tan wash) | mb_towers3 | tower | an automatic launcher box of eight ready-to-fire Kornet tubes, no reload magazine in view |


## Wave 2: the validator's flagged models (18 with errors: the 13 of the baseline + 5 over a budget hard cap)

**Wave 2 complete (2026-10-02):** all 18 fixed; siege_tank keeps its 22 moving parts under a per-model cap exception (`CAP_EXCEPTIONS` in glb_check.py; its 16 Deploy_* pivots are all driven by VehicleView.Deploy).

Fix the error with the smallest change (DECISIONS: proportions within 25 % of `modelSize`, zero-area via `k.clean`, boss part nodes, budget caps), then the V2 pass if the category takes it. `strike_jet` and `tank_buster` are unlisted (C#-only) models: fix the slivers only.

| model | class | builder | tris | errors |
|---|---|---|---:|---|
| `at_gun_emplacement` (**done pass A**, mb_p27_wave2 / mb_p25_new) | tower | mb_p25_new | 1,384 | at_gun_emplacement: height/length 0.22 vs modelSize 0.34 (-37%) |
| `command_hq` (**done pass B**, mb_p27_wave2 / edits) | prop | mb_siege | 5,982 | renderers 62 over the prop normal hard cap 58 |
| `flak_tower` (**done pass B**, mb_p27_wave2 / edits) | tower | mb_fortress | 9,748 | movingParts 10 over the tower normal hard cap 9 |
| `headquarters` (**done pass A**, mb_p27_wave2 / mb_p25_new) | tower | mb_phase2 | 14,260 | 82 zero-area triangles (0.58%) |
| `heavy_flak_tower` (**done pass A**, mb_p27_wave2 / mb_p25_new) | tower | mb_p25_new | 1,116 | heavy_flak_tower: height/length 0.69 vs modelSize 0.49 (+43%) |
| `helipad` (**done pass A**, mb_p27_wave2 / mb_p25_new) | structure | mb_siege | 1,128 | 96 zero-area triangles (8.51%) |
| `helipad_a` (**done pass A**, mb_p27_wave2 / mb_p25_new) | structure | mb_p25_models2 | 1,348 | 96 zero-area triangles (7.12%) |
| `helipad_b` (**done pass A**, mb_p27_wave2 / mb_p25_new) | structure | mb_p25_models2 | 2,084 | 96 zero-area triangles (4.61%) |
| `interceptor_jet` (**done pass B**, mb_p27_wave2 / edits) | jet | mb_p25_new | 1,052 | interceptor_jet: height/length 0.20 vs modelSize 0.27 (-26%) |
| `laser_ad_station` (**done pass A**, mb_p27_wave2 / mb_p25_new) | tower | mb_p25_new | 390 | laser_ad_station: width/length 1.12 vs modelSize 0.67 (+67%) |
| `mobile_fortress` (**done pass A**, mb_p27_wave2 / mb_p25_new) | boss_s | mb_bosses2 | 22,116 | mobile_fortress: boss part 'howitzer_2' node Mount_gun not in the model; mobile_fortress: boss part 'sam' node Mount_missile.001 not in the model; fenrir: boss part 'howitzer_2' node Mount_gun not in the model; fenrir: boss part 'sam' node Mount_missile.001 not in the model |
| `sea_cruiser` (**done pass B**, mb_p27_wave2 / edits) | ground | mb_naval | 5,416 | movingParts 14 over the ground normal hard cap 10 |
| `shield_generator` (**done pass B**, mb_p27_wave2 / edits) | prop | mb_fortress | 5,864 | renderers 63 over the prop normal hard cap 58 |
| `siege_tank` (**done pass B**, mb_p27_wave2 / edits) | ground | mb_p25_models2 | 5,924 | renderers 80 over the ground normal hard cap 76; movingParts 22 over the ground normal hard cap 10 |
| `sky_gunship_hd` (**done pass B**, mb_p27_wave2 / edits) | jet | mb_p25_models (detail=True) | 3,764 | 202 zero-area triangles (5.37%) |
| `strike_jet` (**done pass B**, mb_p27_wave2 / edits) | unlisted | mb_air | 8,700 | 156 zero-area triangles (1.79%) |
| `tank_buster` (**done pass B**, mb_p27_wave2 / edits) | unlisted | mb_air3 | 8,958 | 163 zero-area triangles (1.82%) |
| `visual_jammer` (**done pass A**, mb_p27_wave2 / mb_p25_new) | structure | mb_p25_new | 592 | visual_jammer: width/length 1.16 vs modelSize 0.83 (+39%) |


## Wave 3: ground vehicles (V2) - 65 models

**Pass 3a done (2026-10-02, V2 rebuild in `mb_p27_wave3`; static gates pass, cards and previews not yet rendered):** heavy_tank (+hd), light_tank (+hd), tank_destroyer (+hd), elite_heavy_tank, elite_mbt, elite_tank_destroyer, titan_tank, turtle_tank.

**Pass 3b done (2026-10-02, static gates pass; cards not rendered by the agent):** laser_tank, flame_tank, twin_tank, bmpt, ifv, elite_apc, armored_bulldozer, engineer_vehicle.

**Pass 3c done (2026-10-02, static gates pass; cards not rendered by the agent):** aa_vehicle (+hd), artillery (+hd), heavy_aa, elite_aa, mortar_carrier, mine_layer, smoke_carrier, shield_carrier.

**Pass 3d done (2026-10-02, static gates pass; cards not rendered by the agent):** mlrs, elite_mlrs, heavy_rocket_artillery, thermobaric_launcher, ballistic_launcher, long_sam, sam_launcher, iron_beam.

**Pass 3e done (2026-10-02, static gates pass; cards not rendered by the agent):** counter_battery_radar, ew_jammer, bunker_vehicle, ammo_carrier, supply_truck, railgun_truck, shahed_truck, vbied.

**Pass 3f done (2026-10-02, static gates pass; cards not rendered by the agent):** wheeled_gun, zu23_technical, rocket_technical, hover_gunboat, aa_gun_vehicle, airborne_vehicle, fibre_fpv_carrier, interceptor_drone_vehicle.

**Pass 3g done (2026-10-02, static gates pass; cards not rendered by the agent):** microwave_vehicle, nlos_atgm_vehicle, radar_atgm_vehicle, radar_scout, recoilless_jeep, shorad_vehicle, sp_mortar, wheeled_howitzer; aa_gun_vehicle brightened (3f fix).

**Pass 3h done (2026-10-02, static gates pass; cards not rendered by the agent):** armored_car, command_vehicle, fpv_carrier, lancet_truck, scout_jeep (+hd), landing_craft, missile_boat, sea_corvette, grad_truck; nlos_atgm_vehicle and radar_atgm_vehicle brightened (3g fix).

**Wave 3 complete (2026-10-02): all 8 passes (3a-3h, 65 models) built and past the static gates; the lead renders the 3g/3h cards.**

Tanks and tracked first (the 12 `_hd` models are here or done), then wheeled, then boats. grad_truck is over the ground soft budget: it may not grow.

| builder | models |
|---|---|
| mb_p25_models2 | aa_vehicle (+hd), ammo_carrier, armored_bulldozer, artillery (+hd), ballistic_launcher, bmpt, bunker_vehicle, counter_battery_radar, elite_aa, elite_apc, elite_heavy_tank, elite_mbt, elite_mlrs, elite_tank_destroyer, engineer_vehicle, ew_jammer, heavy_aa, heavy_rocket_artillery, heavy_tank (+hd), hover_gunboat, ifv, iron_beam, laser_tank, light_tank (+hd), long_sam, mine_layer, mlrs, mortar_carrier, railgun_truck, rocket_technical, sam_launcher, shahed_truck, shield_carrier, smoke_carrier, supply_truck, tank_destroyer (+hd), thermobaric_launcher, titan_tank, turtle_tank, vbied, wheeled_gun, zu23_technical |
| mb_p25_new | aa_gun_vehicle, airborne_vehicle, fibre_fpv_carrier, interceptor_drone_vehicle, microwave_vehicle, nlos_atgm_vehicle, radar_atgm_vehicle, radar_scout, recoilless_jeep, shorad_vehicle, sp_mortar, wheeled_howitzer |
| mb_p25_models | armored_car, command_vehicle, flame_tank, fpv_carrier, lancet_truck, scout_jeep (+hd), twin_tank |
| mb_naval | landing_craft, missile_boat, sea_corvette |
| mb_artillery | grad_truck |

## Wave 4: aircraft (helicopters V2; jets clean-up + `_hd` nozzle/canopy only) - 15 models

Helicopters V2; jets only `k.clean` and the library nozzle / canopy in `_hd` (checkpoint 1). attack_jet_hd and sky_gunship (wave 2) carry `_hd`.

| builder | models |
|---|---|
| mb_p25_models2 | attack_jet (+hd), elite_attack_helicopter, gunship_heli, heavy_bomber, recon_drone, scout_heli, stealth_bomber, stealth_fighter, strike_drone, wingman_drone |
| mb_p25_new | airborne_vehicle_chute, glide_bomber, recon_jet |
| mb_orbital | drop_pod |
| mb_p25_models | swarm_carrier |

## Wave 5: bosses (V2, at the prompt 26 sizes) - 21 models

At the prompt 26 sizes (`size`, `modelSize`); boss part nodes and `mountWeapons` slots kept; vary greeble seeds per ship. These are also the batch D stand-ins' parents: their rebuild does not touch the stand-ins once wave 1b is done.

| builder | models |
|---|---|
| mb_p20_bosses | behemoth, command_airship, drone_mothership, fortress_bastion, kronos, moloch, nuke_train |
| mb_bosses2 | behemoth_inferno, behemoth_tempest, fortress_hive, mega_gunship |
| mb_p16_arms | armored_train, landing_hovercraft |
| mb_redesign_20y | caspian, typhon |
| mb_phase8 | earth_borer, supreme_command |
| mb_p25_models | daedalus |
| mb_naval | leviathan |
| mb_p22_content | morrigan |
| mb_p25_models2 | sky_fortress |

## Wave 6: towers (armed statics) - 41 models

The weapon on top must read at 40 px; tower branches (`_a`, `_b`) with their base tower in one commit each.

| builder | models |
|---|---|
| mb_tower_branches | aa_turret_a, aa_turret_b, artillery_emplacement_a, artillery_emplacement_b, atgm_tower_a, atgm_tower_b, c_ram_a, c_ram_b, drone_hangar_a, drone_hangar_b, ew_tower_a, ew_tower_b, guard_tower_a, guard_tower_b, gun_turret_a, gun_turret_b, heavy_turret_a, heavy_turret_b, mg_bunker_a, mg_bunker_b, missile_battery_a, missile_battery_b, rocket_turret_a, rocket_turret_b |
| mb_siege | aa_turret, artillery_emplacement, guard_tower, gun_turret, mg_bunker, rocket_turret |
| mb_towers3 | atgm_tower, c_ram, drone_hangar, ew_tower, gun_pit |
| mb_p25_new | aa_gun_tower, flare_tower, searchlight |
| mb_fortress | heavy_turret, missile_battery |
| mb_phase8 | wreck_turret |

## Wave 7: structures (unarmed statics) - 22 models

Unarmed statics: big volumes, no new moving parts.

| builder | models |
|---|---|
| mb_tower_branches | cp_relay_a, cp_relay_b, dragons_teeth_a, dragons_teeth_b, minefield_a, minefield_b, shield_tower_a, shield_tower_b |
| mb_p25_new | barrage_balloon, blast_wall, fire_control_centre, inflatable_decoy, troop_shelter |
| mb_p25_models2 | logistics_station, radar_site, repair_bay |
| mb_p17_temp | cp_relay, shield_tower |
| mb_towers3 | dragons_teeth, minefield |
| mb_siege | ammo_dump |
| mb_phase8 | targeting_station |

## Wave 8: remaining: props, scenery, munitions, unlisted (only where the preview shows a gain) - 198 models

Low value per triangle: only where a preview shows a visible gain or the validator flags it. Unlisted models get a class when a def points at them. Builders the static scan missed are generated dicts (munitions, rounds).

| builder | models |
|---|---|
| (not found by the static scan) | aim120, aim9, apfsds, atgm_ataka, atgm_kornet, atgm_tow, bomb_fab, bomb_mk84, buk, debris_concrete, debris_leaves, debris_metal, debris_plaster, debris_roof, debris_wood, flak_round, gbu12, gbu39, gmlrs, grad, grad_cluster, griffin, heat_round, hellfire, hellfire_longbow, hydra, igla, jassm, jdam, kh29l, lancet, mam_l, maverick, mortar_bomb, patriot, r60, rail_slug, rocket_107, s8, shahed, shell_155, shorad_dart, stinger, tos_rocket |
| mb_themes2 | bamboo_clump, basalt_rock_a, basalt_rock_b, basalt_rock_c, billboard, bus, charred_tree, control_tower, fern_bush, fuel_truck, hangar, highrise_a, highrise_b, jungle_tree_a, jungle_tree_b, jungle_tree_c, lava_vent, obsidian_spire, parked_jet, parking_garage, radar_dome, revetment, runway_light, skyscraper, stilt_hut, temple_ruin, traffic_light, volcanic_cliff |
| mb_mapkit | barricade, bridge_road, camo_net, checkpoint, command_tent, crater_large, dead_tree, foxhole, fuel_bladder, power_pylon, radio_mast, ruin_house, ruin_tower, supply_pile, tank_ditch, telegraph_pole, trench_corner, trench_straight, wreck_car, wreck_tank, wreck_truck |
| mb_props | ammo_crate, barrel, birch, bush, fuel_tank, house_large, house_small, pine, rock_a, rock_b, rock_c, rubble_large, rubble_medium, rubble_small, tree, tree_broad, tree_dead, tree_round, wall |
| mb_town | apartment, barn, car, church, cottage, fence, garage, hedge, ruin, shop, silo, stone_wall, townhouse, truck, warehouse, water_tower |
| mb_themes | adobe_house, adobe_large, cactus, log_cabin, market_stall, mesa, oil_pump, palm, pipeline, radar_station, refinery_tower, snow_pine, snow_rock, storage_tank, watchtower |
| mb_harbor | container, container_stack, dock_bollards, factory, gantry_crane, jersey_barrier, lamp_post, office_block, rail_boxcar, rail_tanker |
| mb_terrain | boulders, cliff_a, cliff_b, dirt_mound, mountain_a, mountain_b, mountain_c, sandbags, tank_trap |
| mb_siege | base_gate, base_wall, floodlight_mast, fuel_depot, razor_wire, sandbag_wall, vehicle_hangar |
| mb_phase8 | rail_tractor, wreck_barrel, wreck_engine, wreck_launcher, wreck_stump |
| mb_air | bomb, cruise_missile, missile, rocket |
| mb_artillery | aps_tank, atgm_carrier, howitzer |
| mb_vehicles3 | ballistic_missile, heavy_rocket, siege_mortar |
| mb_naval | fishing_boat, lighthouse, pier |
| mb_support | mine, repair_crate, supply_crate |
| mb_vehicles | apc (+hd) |
| mb_new_trucks | armed_truck |
| mb_orbital | bug_satellite |
| mb_pt5_models | fpv_drone |
| mb_round6 | heavy_attack_heli |
| mb_air3 | icbm |
| mb_new_tracked | sapper |
| mb_p25_models2 | transport_plane |
