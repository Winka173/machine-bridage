# Model fix backlog (pass 8)

From Docs/models/scan/visual_scores.md after the lead pass L8 (2026-10-03). The 15 models rebuilt in that pass are not
listed. Priority order inside each list: visual Kém first (box models, unreadable), then bosses, then the rest.

## Final Kém, not rebuilt

| model | class | triangles | why (static* / visual) | suggested fix |
|---|---|---|---|---|
| `garuda` | boss | 2,840 | far under budget; proportions > 25 % off (high-confidence reference); visual: flat flying-wing slab, 2840 triangles; no volume or engine detail for a boss | rebuild (box model / too little detail) |
| `moloch` | boss | 10,244 | missing parts: running_gear; LOD1 share 12%; visual: box model: stacked rectangular blocks on tracks, no bevels; weak boss silhouette | rebuild (box model / too little detail) |
| `morrigan` | boss | 1,344 | far under budget; visual: flat flying-wing slab, 1344 triangles; far too little volume and detail for a boss | rebuild (box model / too little detail) |
| `elite_apc` | tracked | 5,480 | 4 parts missing; visual: box model: one tall rectangular hull with a small turret, no glacis slope or side detail | rebuild (box model / too little detail) |
| `fibre_fpv_carrier` | wheeled | 1,324 | far under budget; visual: box cab and flat bed, spools only; too little detail to read at play distance | rebuild (box model / too little detail) |
| `hover_gunboat` | ground | 2,202 | triangles 2202 under 3000; visual: flat slab hull with a box deckhouse; no skirt, deck or bow detail for a ship | rebuild (box model / too little detail) |
| `landing_craft` | ship | 498 | far under budget; 4 parts missing; proportions > 25 % off (high-confidence reference); visual: open tub hull with a box wheelhouse, 498 triangles; no ramp hinge, deck or bow detail | rebuild (box model / too little detail) |
| `missile_boat` | ship | 630 | far under budget; visual: box model: wedge slab hull with two box launchers and a box wheelhouse, 630 triangles | rebuild (box model / too little detail) |
| `river_patrol_boat` | ground | 1,624 | triangles 1624 under 3000; visual: box deckhouse on a slab hull with box engines, 1624 triangles; reads as blocks, not a boat | rebuild (box model / too little detail) |
| `sea_corvette` | ship | 1,884 | far under budget; visual: slab hull with box deckhouses, 1884 triangles; no bow flare, CIWS or deck detail | rebuild (box model / too little detail) |
| `stealth_naval_strike` | jet | 2,124 | 4 parts missing; visual: flat triangle slab with stickers, 2124 triangles; no volume for its role | rebuild (box model / too little detail) |
| `command_airship` | boss | 22,840 | proportions > 25 % off (high-confidence reference) | check the reference (drawn shortened on purpose?) or rescale |
| `drone_mothership` | boss | 20,206 | proportions > 25 % off (high-confidence reference) | check the reference (drawn shortened on purpose?) or rescale |
| `kronos` | boss | 13,194 | proportions > 25 % off (high-confidence reference) | check the reference (drawn shortened on purpose?) or rescale |
| `leviathan` | boss | 26,744 | proportions > 25 % off (high-confidence reference) | check the reference (drawn shortened on purpose?) or rescale |
| `mega_gunship` | boss | 11,476 | proportions > 25 % off (high-confidence reference) | check the reference (drawn shortened on purpose?) or rescale |
| `mobile_fortress` | boss | 23,256 | proportions > 25 % off (high-confidence reference) | check the reference (drawn shortened on purpose?) or rescale |
| `nyx` | boss | 3,526 | far under budget | add detail (under half the triangle minimum) |
| `sky_fortress` | boss | 3,084 | far under budget | add detail (under half the triangle minimum) |
| `stymphalos` | boss | 4,186 | far under budget | add detail (under half the triangle minimum) |
| `typhon` | boss | 6,876 | proportions > 25 % off (high-confidence reference) | check the reference (drawn shortened on purpose?) or rescale |
| `aa_57mm_vehicle` | tracked | 6,028 | 4 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `aa_gun_vehicle` | tracked | 3,556 | 7 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `aa_vehicle` | tracked | 4,964 | 6 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `aerial_tanker` | jet | 4,164 | 4 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `airborne_light_tank` | tracked | 5,550 | 4 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `airborne_vehicle` | tracked | 3,260 | 7 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `amphib_light_vehicle` | tracked | 4,606 | 6 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `armored_bulldozer` | tracked | 3,244 | 8 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `artillery` | tracked | 5,326 | 4 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `bmpt` | tracked | 5,056 | 5 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `bridging_vehicle` | tracked | 5,148 | 4 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `bunker_vehicle` | tracked | 7,792 | 4 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `demolition_line_vehicle` | tracked | 6,202 | 4 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `elite_aa` | tracked | 5,456 | 6 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `elite_mbt` | tracked | 7,288 | proportions > 25 % off (high-confidence reference) | check the reference (drawn shortened on purpose?) or rescale |
| `elite_tank_destroyer` | tracked | 4,794 | 5 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `engineer_vehicle` | tracked | 3,670 | 7 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `flame_tank` | tracked | 5,258 | 7 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `glide_bomber` | jet | 1,624 | far under budget | add detail (under half the triangle minimum) |
| `ground_drone_carrier` | tracked | 4,274 | 6 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `gunship_heli` | helicopter | 4,660 | proportions > 25 % off (high-confidence reference) | check the reference (drawn shortened on purpose?) or rescale |
| `heavy_turret_a` | tower | 9,670 | far over budget; main muzzle missing | add the main Muzzle_* node |
| `heavy_turret_b` | tower | 11,958 | far over budget; main muzzle missing | add the main Muzzle_* node |
| `ifv` | tracked | 5,040 | 4 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `inflatable_decoy` | tower | 1,378 | 4 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `interceptor_jet` | jet | 1,500 | far under budget | add detail (under half the triangle minimum) |
| `laser_tank` | tracked | 3,844 | 6 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `light_tank` | tracked | 4,350 | 6 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `mine_layer` | tracked | 3,872 | 7 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `mortar_carrier` | tracked | 3,242 | 5 parts missing; proportions > 25 % off (high-confidence reference) | check the reference (drawn shortened on purpose?) or rescale |
| `next_gen_tank` | tracked | 6,620 | 4 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `radar_atgm_vehicle` | tracked | 2,672 | 8 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `recon_drone` | jet | 890 | far under budget; 5 parts missing; proportions > 25 % off (high-confidence reference) | check the reference (drawn shortened on purpose?) or rescale |
| `recon_jet` | jet | 768 | far under budget; 5 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `sam_launcher` | tracked | 4,418 | 7 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `sea_cruiser` | ship | 5,416 | proportions > 25 % off (high-confidence reference) | check the reference (drawn shortened on purpose?) or rescale |
| `shield_carrier` | wheeled | 2,476 | proportions > 25 % off (high-confidence reference) | check the reference (drawn shortened on purpose?) or rescale |
| `siege_tank` | tracked | 5,924 | 6 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `sky_gunship` | jet | 3,652 | 4 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `smoke_carrier` | tracked | 3,698 | 6 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `stealth_bomber` | jet | 2,096 | proportions > 25 % off (high-confidence reference) | check the reference (drawn shortened on purpose?) or rescale |
| `stealth_fighter` | jet | 3,336 | proportions > 25 % off (high-confidence reference) | check the reference (drawn shortened on purpose?) or rescale |
| `strike_drone` | jet | 1,968 | far under budget; 5 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `swarm_carrier` | jet | 3,464 | 5 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `tank_destroyer` | tracked | 4,702 | 5 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `thermobaric_launcher` | tracked | 4,982 | 4 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `titan_tank` | tracked | 8,384 | 4 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `towed_at_gun` | wheeled | 1,996 | 4 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `turtle_tank` | tracked | 3,938 | 9 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `uav_loiter_strike` | jet | 1,084 | far under budget; 4 parts missing | name / add the missing parts (many are modelled inside merged nodes: rename or split) |
| `wingman_drone` | jet | 1,064 | far under budget | add detail (under half the triangle minimum) |

## Visual "Cần sửa" (look faults to fix when the model is next touched)

| model | class | visual reason |
|---|---|---|
| `aa_gun_tower` | tower | single-box gun house on a sandbag ring; thin barrel, little detail |
| `at_gun_emplacement` | tower | gun is a flat shield plate and a stick barrel; low detail |
| `attack_jet` | jet | Su-25-like planform reads but fuselage is thin and flat, few stores detail |
| `auto_loader_howitzer` | tracked | big box casemate turret on a slab hull |
| `ballistic_launcher` | wheeled | missile and erector read but the cab is a plain box and the bed is a flat slab |
| `blast_wall` | obstacle | row of plain blocks; no texture or rebar detail |
| `bunker_shelter_tower` | tower | earth-sided block with flat roof and vents; low detail, 1228 triangles |
| `caspian` | boss | ekranoplan reads, but the fuselage is a long box and the wings are flat slabs |
| `cerberus` | boss | three-section wheeled boss reads; sections are stacked boxes with few bevels |
| `combat_wreck_car` | wheeled | pickup with a sandbagged bed and gun; boxy cab, few details |
| `command_vehicle` | wheeled | 8-wheel APC with antennas reads, but the hull is a plain box with flat sides |
| `dazzler_vehicle` | wheeled | 8x8 with a plain box body and a light array; few panel details |
| `drone_hijack_vehicle` | wheeled | 8x8 with a plain box body and antennas; few panel details |
| `drone_net_tower` | obstacle | net panel on two posts with lamps; simple, 1378 triangles |
| `elite_heavy_tank` | tracked | flat slab hull and a low flat turret; long gun reads |
| `elite_mlrs` | wheeled | HIMARS-like; cab and pod are plain boxes with little bevel, few details |
| `ew_jammer` | wheeled | truck with a plain box body and a dish; body has no panel detail |
| `fpv_carrier` | wheeled | 6x6 truck with a plain box body; launcher grid on the roof reads |
| `gps_jammer_vehicle` | wheeled | truck with an antenna tree and cable drum on an open bed; cab box |
| `guard_tower_b` | tower | gun on a pedestal in a sandbag ring, a thin ring for a tower |
| `heavy_aa` | wheeled | truck with an open flat bed and a small launcher; cab and bed plain boxes |
| `heavy_bomber` | jet | swept wing and T-tail read; slim tube fuselage, flat slab wings and tail |
| `heavy_tank` | tracked | flat slab hull and a low flat turret; reads as a tank, few volumes |
| `helipad` | obstacle | flat marked pad only; no lights, windsock or edge detail |
| `helipad_a` | obstacle | plain half-tube hangar over the pad; shell has no ribs or doors |
| `iron_beam` | wheeled | 8x8 truck with a plain box body and laser head; few panel details |
| `ixion` | boss | BelAZ mine truck with a 125 mm turret reads; slab body sides, small turret for a boss |
| `lancet_truck` | wheeled | 6x6 with box launcher and box cab; little bevel or detail |
| `logistics_station` | tower | containers and a forklift on a flat slab; no shed, roof or fence |
| `mine_rocket_truck` | wheeled | truck with a plain box launcher; cab box |
| `mlrs` | wheeled | HIMARS-like truck; pod and cab plain boxes, few details |
| `mobile_repair_vehicle` | wheeled | boxy 6x6 with crane and tool boxes; body plain box |
| `monster` | boss | giant twin-hull tracked gun reads; stacked slabs, few bevels |
| `one_shot_atgm_tower` | tower | box bunker with a launcher box on a timber base; boxy |
| `radar_support_vehicle` | wheeled | 6x6 with mast radar; body plain box |
| `railgun_truck` | wheeled | 8x8 with a box rail launcher; cab and body plain boxes |
| `river_gunboat` | ground | gunboat hull with turrets and deckhouse reads; slab sides |
| `rocket_technical` | wheeled | pickup with rocket pod and MG; boxy cab, few details |
| `searchlight` | tower | drum lamp on a post in a sandbag ring; simple, few details |
| `shorad_vehicle` | wheeled | boxy 4x4 with a turret and missile pods; cab and body plain |
| `vbied` | wheeled | up-armoured pickup with plates and a dozer blade; crude by intent, low detail |

Not rebuilt in L8 though early: `moloch` (chapter 6 main boss, visual Kém: stacked boxes) needs its own pass - a boss
with track and door part nodes, four twin-gun mounts and the factory doors; `morrigan` and `garuda` (flat flying-wing
slabs) likewise. `heavy_turret_a` / `_b` lack their main muzzle node (static), a node fix, not a rebuild.
