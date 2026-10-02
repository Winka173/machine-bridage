# Pass 8 visual scores

Scored 2026-10-02/03 (lead pass L8, DECISIONS "Sửa lỗi tổng hợp L8 (lead pass, 2026-10-02)") from the 402 sheets in
`C:\Users\Winka\Projects\MachineBrigade-runner\Builds\scan` (read as composite grids: old above new, each cell
cropped to the model). "static" is static_scores.csv; "static*" is the same with over-budget left out (the lead's
instruction of 2026-10-02: a model over its triangle budget is not graded down). Final grade = the lower of static*
and visual (MODEL_STANDARD section 4). Old vs new: the pre-prompt-27 sheet (`<id>_old.png`) against the current one.
Rows marked **rebuilt** were rebuilt in this pass after the scan: their grades are the scanned (before) state and
need the "after" sheets (see the end of this file).

| model | class | static | static* | static reasons | visual | visual reason | old vs new | final |
|---|---|---|---|---|---|---|---|---|
| `aa_57mm_vehicle` | tracked | Kém | Kém | missing parts: mantlet, idler, roof_mg, stowage | Tốt | S-60/Derivatsiya-like turret with 57 mm gun and radar box, skirts, tracks | - | Kém |
| `aa_gun_tower` | tower | Cần sửa | Cần sửa | triangles 1724 under 2000 | Cần sửa | single-box gun house on a sandbag ring; thin barrel, little detail | same | Cần sửa |
| `aa_gun_vehicle` | tracked | Kém | Kém | triangles 3556 under 4000; missing parts: mantlet, idler, skirts, sight, roof_mg, smoke, stowage | Cần sửa | slab hull and box turret, reads as a generic tank not an SPAAG; few details | better | Kém |
| `aa_turret` | tower | Kém | Cần sửa | LOD1 share 69% | Tốt | twin guns on a ring mount in a sandbag pit; clear silhouette | same | Cần sửa |
| `aa_turret_a` | tower | Kém | Cần sửa | muzzles: Muzzle_missile 0/1; LOD1 share 67% | Tốt | quad guns, sandbag pit, readable | same | Cần sửa |
| `aa_turret_b` | tower | Tốt | Tốt |  | Tốt | missile box launcher on a cast pad, readable | same | Tốt |
| `aa_vehicle` | tracked | Kém | Kém | missing parts: mantlet, idler, sight, roof_mg, smoke, stowage; mounts: Mount_missile 0/1 | Tốt | Gepard-like twin guns and radar, wheels and skirts read | better | Kém |
| `aerial_tanker` | jet | Kém | Kém | missing parts: tail, exhaust, pylons, stores; Mount_Flare 0/2; proportions vs B-52H (same frame as the heavy bomber): h/L +11% | Tốt | airliner-type tanker, swept wing, engines, boom | - | Kém |
| `airborne_light_tank` | tracked | Kém | Kém | missing parts: mantlet, idler, roof_mg, stowage | Cần sửa | slab hull with a box turret; tracks and wheels read | - | Kém |
| `airborne_light_tank_chute` | air_other | Cần sửa | Cần sửa | LOD1 share 34% | Tốt | single canopy with rigging and the tank under it | - | Cần sửa |
| `airborne_vehicle` | tracked | Kém | Kém | triangles 3260 under 4000; missing parts: mantlet, idler, skirts, sight, roof_mg, smoke, stowage | Cần sửa | slab hull and single-box turret; wheels and tracks read | better | Kém |
| `airborne_vehicle_chute` | air_other | Cần sửa | Cần sửa | LOD1 share 29% | Tốt | three canopies, rigging and pallet read; load is the airborne tank | same | Cần sửa |
| `ammo_carrier` | wheeled | Cần sửa | Cần sửa | missing parts: axles | Tốt | 8x8 truck with crate bed and crane, cab glass, wheels read | same | Cần sửa |
| `ammo_dump` | tower | Cần sửa | Cần sửa | missing parts: base, roof | Tốt | camo net over crate stacks, flags, shell rows; base slab added | better | Cần sửa |
| `amphib_light_vehicle` | tracked | Kém | Kém | missing parts: mantlet, idler, skirts, roof_mg, smoke, stowage | Cần sửa | boat-bow box hull with small turret; plain sides | - | Kém |
| `armored_bulldozer` | tracked | Kém | Kém | triangles 3244 under 4000; missing parts: turret, mantlet, idler, skirts, hatches, sight, smoke, stowage; proportions vs Caterpillar D9R (IDF kit): w/L +14%, h/L +16% | Tốt | blade, cab with glass, tracks with sprocket read as a dozer | better | Kém |
| `armored_car` | wheeled | Cần sửa | Cần sửa | triangles 2622 under 3000; missing parts: glass, stowage | Tốt | BTR-style 8-wheeler with turret, hatches, vents | better | Cần sửa |
| `armored_train` | boss | Cần sửa | Cần sửa | muzzles: muzzles 5/7; LOD1 share 9% | Tốt | loco, turret wagons and flat car read as a train; plenty of detail | same | Cần sửa |
| `artillery` | tracked | Kém | Kém | missing parts: mantlet, idler, skirts, smoke; proportions vs M109A6 Paladin: w/L +18% | Cần sửa | big single-box casemate turret with flat sides; hull and wheels fine | better | Kém |
| `artillery_emplacement` | tower | Kém | Cần sửa | missing parts: antenna | Tốt | towed howitzer in a sandbag ring on a timber pad, ammo crates | same | Cần sửa |
| `artillery_emplacement_a` | tower | Kém | Tốt |  | Tốt | long gun, radar dish, sandbag ring | same | Tốt |
| `artillery_emplacement_b` | tower | Cần sửa | Cần sửa | missing parts: antenna; LOD1 share 73% | Tốt | heavy mortar on a sandbag ring, ammo | same | Cần sửa |
| `at_gun_emplacement` | tower | Cần sửa | Cần sửa | triangles 1384 under 2000; missing parts: base, antenna | Cần sửa | gun is a flat shield plate and a stick barrel; low detail | same | Cần sửa |
| `atgm_tower` | tower | Cần sửa | Tốt |  | Tốt | cast blockhouse with stair, sandbag parapet, ATGM launcher; readable | same | Tốt |
| `atgm_tower_a` | tower | Cần sửa | Tốt |  | Tốt | mast-mounted launcher over the blockhouse; readable | same | Tốt |
| `atgm_tower_b` | tower | Cần sửa | Tốt |  | Tốt | multi-tube launcher on the blockhouse; readable | same | Tốt |
| `attack_helicopter` | helicopter | Cần sửa | Cần sửa | muzzles: Muzzle_rocket 1/2; mounts: Mount_rocket 0/1, Mount_aam 0/1; Mount_Flare 0/2; proportions vs AH-64D Apache Longbow: w/L -15%, h/L +46% | Tốt | Apache-like stepped canopy, stub wings, 4 blades, tail rotor | better | Cần sửa |
| `attack_jet` | jet | Cần sửa | Cần sửa | triangles 2732 under 4000; missing parts: tail; mounts: Mount_aam 0/1; Mount_Flare 0/2; LOD1 share 31% | Cần sửa | Su-25-like planform reads but fuselage is thin and flat, few stores detail | same | Cần sửa |
| `auto_loader_howitzer` | tracked | Cần sửa | Cần sửa | missing parts: mantlet, idler, stowage | Cần sửa | big box casemate turret on a slab hull | - | Cần sửa |
| `ballistic_launcher` | wheeled | Cần sửa | Cần sửa | triangles 2818 under 3000; missing parts: axles, stowage | Cần sửa | missile and erector read but the cab is a plain box and the bed is a flat slab | same | Cần sửa |
| `barrage_balloon` | tower | Cần sửa | Cần sửa | triangles 1748 under 2000; missing parts: walls, roof, antenna; LOD1 share 32% | Tốt | balloon with fins, tether and winch base read | same | Cần sửa |
| `behemoth` | boss | Cần sửa | Cần sửa | Mount_APS missing; LOD1 share 16% | Tốt | multi-turret super-heavy tank, many barrels, tracks and skirts read | same | Cần sửa |
| `behemoth_inferno` | boss | Cần sửa | Cần sửa | LOD1 share 21% | Tốt | flamer tanks and turrets, heavy hull detail | same | Cần sửa |
| `behemoth_tempest` | boss | Cần sửa | Cần sửa | Mount_APS missing; boss part nodes missing: railgun:Main_cannon*; LOD1 share 16% | Tốt | long gatling main gun, stepped hull, readable | same | Cần sửa |
| `blast_wall` | obstacle | Cần sửa | Cần sửa | LOD1 share 100% | Cần sửa | row of plain blocks; no texture or rebar detail | - | Cần sửa |
| `bmpt` | tracked | Kém | Kém | missing parts: mantlet, idler, roof_mg, smoke, stowage | Tốt | BMPT-style twin-cannon turret with ATGM boxes, dozer blade | better | Kém |
| `bridging_vehicle` | tracked | Kém | Kém | missing parts: mantlet, idler, smoke, stowage | Tốt | tracked AVLB with folded bridge deck, readable | - | Kém |
| `bulwark_post` | structure | Cần sửa | Cần sửa | triangles 1710 under 2000; LOD1 share 72% | Tốt | sandbag ring with MG and flag, readable | - | Cần sửa |
| `bunker_shelter_tower` | tower | Cần sửa | Cần sửa | triangles 1228 under 2000 | Cần sửa | earth-sided block with flat roof and vents; low detail, 1228 triangles | - | Cần sửa |
| `bunker_vehicle` | tracked | Kém | Kém | missing parts: mantlet, idler, skirts, stowage | Cần sửa | long flat slab hull with a small box turret; plain sides | same | Kém |
| `c_ram` | tower | Kém | Cần sửa | missing parts: walls; Mount_APS missing | Tốt | Phalanx dome on a trailer pad, radar mast, readable | same | Cần sửa |
| `c_ram_a` | tower | Kém | Cần sửa | missing parts: walls; Mount_APS missing | Tốt | dome gun, sphere radar mast, readable | same | Cần sửa |
| `c_ram_b` | tower | Kém | Cần sửa | missing parts: walls; Mount_APS missing | Tốt | box launcher on a trailer pad, readable | same | Cần sửa |
| `caspian` | boss | Cần sửa | Cần sửa | triangles 6766 under 10000; missing parts: superstructure; muzzles: muzzles 1/3; proportions vs Lun-class ekranoplan: w/L +24%, h/L +16%; LOD1 share 9% | Cần sửa | ekranoplan reads, but the fuselage is a long box and the wings are flat slabs | same | Cần sửa |
| `cerberus` | boss | Cần sửa | Cần sửa | LOD1 share 30% | Cần sửa | three-section wheeled boss reads; sections are stacked boxes with few bevels | - | Cần sửa |
| `coastal_ashm_vehicle` | wheeled | Cần sửa | Cần sửa | missing parts: axles, stowage; LOD1 share 34% | Tốt | truck with a four-canister anti-ship launcher, outriggers | - | Cần sửa |
| `coastal_battery` | structure | Cần sửa | Cần sửa | missing parts: walls | Tốt | casemate twin-gun turret on a rock-strewn emplacement | - | Cần sửa |
| `combat_wreck_car` | wheeled | Cần sửa | Cần sửa | triangles 2794 under 3000; missing parts: axles, stowage | Cần sửa | pickup with a sandbagged bed and gun; boxy cab, few details | - | Cần sửa |
| `command_airship` | boss | Kém | Kém | muzzles: muzzles 6/8; proportions vs Airlander 10: w/L +46%, h/L +25%; LOD1 share 16% | Tốt | twin-hull airship with gondola and engines, readable | same | Kém |
| `command_hq` | hq | Cần sửa | Cần sửa | missing parts: base, walls | Tốt | stepped command block, lattice mast, dish, fences | same | Cần sửa |
| `command_vehicle` | wheeled | Cần sửa | Cần sửa | missing parts: glass | Cần sửa | 8-wheel APC with antennas reads, but the hull is a plain box with flat sides | same | Cần sửa |
| `counter_battery_radar` | wheeled | Cần sửa | Cần sửa | triangles 2396 under 3000; missing parts: axles, stowage | Tốt | truck with folding radar panel, cab glass, outriggers | same | Cần sửa |
| `cp_relay` | tower | Cần sửa | Cần sửa | missing parts: walls | Tốt | lattice mast with dishes, hut and crates on a pad; new pale cast slab and hut | same | Cần sửa |
| `cp_relay_a` | tower | Cần sửa | Cần sửa | missing parts: walls | - | no sheet (the scan wrote none; branch model of an unscanned def?) | - | Cần sửa |
| `cp_relay_b` | tower | Cần sửa | Cần sửa | triangles 1512 under 2000; missing parts: walls, antenna | - | no sheet (the scan wrote none; branch model of an unscanned def?) | - | Cần sửa |
| `daedalus` | boss | Cần sửa | Cần sửa | missing parts: running_gear; Mount_APS missing; LOD1 share 21% | Tốt | wedge-hull flying fortress, dense greebles, readable | same | Cần sửa |
| `dazzler_vehicle` | wheeled | Cần sửa | Cần sửa | missing parts: axles, stowage; LOD1 share 29% | Cần sửa | 8x8 with a plain box body and a light array; few panel details | - | Cần sửa |
| `demolition_line_vehicle` | tracked | Kém | Kém | missing parts: mantlet, idler, roof_mg, smoke | Tốt | tracked mine-clearing vehicle with rocket box, roller and line charge | - | Kém |
| `dragons_teeth` | obstacle | Tốt | Tốt |  | Tốt | concrete pyramids and hedgehogs on a slab (new: pale concrete) | same | Tốt |
| `dragons_teeth_a` | obstacle | Tốt | Tốt |  | Tốt | steel hedgehogs on a slab, readable | same | Tốt |
| `dragons_teeth_b` | obstacle | Tốt | Tốt |  | Tốt | concertina wire rings on pickets, readable | same | Tốt |
| `drone_hangar` | tower | Kém | Tốt |  | Tốt | arched hangar with launch rail, generator, barrels, pad | same | Tốt |
| `drone_hangar_a` | tower | Kém | Tốt |  | Tốt | arched hangar with launch rail, readable | same | Tốt |
| `drone_hangar_b` | tower | Kém | Cần sửa | LOD1 share 28% | Tốt | arched hangar with a rooftop module, readable | same | Cần sửa |
| `drone_hijack_vehicle` | wheeled | Cần sửa | Cần sửa | missing parts: axles, stowage; LOD1 share 34% | Cần sửa | 8x8 with a plain box body and antennas; few panel details | - | Cần sửa |
| `drone_mothership` | boss | Kém | Kém | proportions vs Airlander 10: h/L +48%; LOD1 share 15% | Tốt | airship hull, fins, engine pods, gondola | same | Kém |
| `drone_net_tower` | obstacle | Tốt | Tốt |  | Cần sửa | net panel on two posts with lamps; simple, 1378 triangles | - | Cần sửa |
| `drop_pod` | air_other | Cần sửa | Cần sửa | proportions vs Soyuz descent module: h/L +90% | Tốt | capsule with heat shield, ring and vents reads | same | Cần sửa |
| `earth_borer` | boss | Cần sửa | Cần sửa | muzzles: muzzles 2/3; LOD1 share 18% | Tốt | drill head, segmented body, tracks; readable boss | same | Cần sửa |
| `elite_aa` | tracked | Kém | Kém | missing parts: mantlet, idler, sight, roof_mg, smoke, stowage | Cần sửa | slab hull with a box turret; guns and radar read, sides plain | better | Kém |
| `elite_apc` | tracked | Kém | Kém | missing parts: mantlet, idler, roof_mg, stowage | Kém | box model: one tall rectangular hull with a small turret, no glacis slope or side detail | better | Kém |
| `elite_attack_helicopter` | helicopter | Cần sửa | Cần sửa | mounts: Mount_aam 0/1; proportions vs AH-64D Apache Longbow: w/L -15%, h/L +46% | Tốt | attack helicopter with canopy, stub wings, rotors | same | Cần sửa |
| `elite_heavy_tank` | tracked | Cần sửa | Cần sửa | missing parts: mantlet, idler, stowage | Cần sửa | flat slab hull and a low flat turret; long gun reads | better | Cần sửa |
| `elite_mbt` | tracked | Kém | Kém | missing parts: mantlet, idler; proportions vs T-90: h/L +28% | Cần sửa | slab hull, angular turret with some cheeks; reads as a tank | better | Kém |
| `elite_mlrs` | wheeled | Cần sửa | Cần sửa | triangles 2692 under 3000; missing parts: axles, stowage | Cần sửa | HIMARS-like; cab and pod are plain boxes with little bevel, few details | same | Cần sửa |
| `elite_tank_destroyer` | tracked | Kém | Kém | missing parts: mantlet, idler, skirts, smoke, stowage; proportions vs 2S25 Sprut-SD: h/L -19%; LOD1 share 35% | Cần sửa | wide flat slab hull, small low turret, long gun; hull sides plain | better | Kém |
| `engineer_vehicle` | tracked | Kém | Kém | triangles 3670 under 4000; missing parts: mantlet, idler, skirts, sight, roof_mg, smoke, stowage; proportions vs M88A1 recovery vehicle: w/L +13%, h/L -17% | Cần sửa | flat slab hull with crane arm and blade; tracks read | better | Kém |
| `ew_jammer` | wheeled | Cần sửa | Cần sửa | triangles 2274 under 3000; missing parts: axles, stowage | Cần sửa | truck with a plain box body and a dish; body has no panel detail | same | Cần sửa |
| `ew_tower` | tower | Cần sửa | Cần sửa | LOD1 share 25% | Tốt | lattice tower with antenna head, shelters, generator | same | Cần sửa |
| `ew_tower_a` | tower | Kém | Cần sửa | LOD1 share 33% | Tốt | lattice tower with radome and emitter rings | same | Cần sửa |
| `ew_tower_b` | tower | Cần sửa | Cần sửa | LOD1 share 26% | Tốt | lattice tower with a panel radar, shelters | same | Cần sửa |
| `fibre_fpv_carrier` | wheeled | Kém | Kém | triangles 1324 under 3000; missing parts: axles; muzzles: Muzzle_rocket 0/1; mounts: Mount_rocket 0/1; LOD1 share 70% | Kém | box cab and flat bed, spools only; too little detail to read at play distance | better | Kém |
| `fighter_jet` | jet | Cần sửa | Cần sửa | missing parts: tail; mounts: Mount_aam 0/1; Mount_Flare 0/2; LOD1 share 18% | Tốt | Su-27-like twin fins, swept wing, canopy, missiles | better | Cần sửa |
| `fire_control_centre` **rebuilt** | tower | Kém | Kém | triangles 612 under 2000; missing parts: walls, roof | Kém | box model: two plain blocks with a mast, no roof, wall or sandbag detail | same | Kém |
| `flame_tank` | tracked | Kém | Kém | missing parts: mantlet, idler, skirts, sight, roof_mg, smoke, stowage | Tốt | T-55-like dome turret with fuel tanks on the rear deck | better | Kém |
| `flare_searchlight_tower` | tower | Cần sửa | Cần sửa | missing parts: base, walls | Tốt | timber stilt tower with ladder, flare launcher and lamp | - | Cần sửa |
| `flare_tower` **rebuilt** | tower | Kém | Kém | triangles 680 under 2000; missing parts: walls, antenna | Kém | a table on four legs with a small launcher box; no base, parapet or roof detail | same | Kém |
| `fortress_bastion` | boss | Cần sửa | Cần sửa | boss part nodes missing: mortar:Main_cannon*; LOD1 share 12% | Tốt | tracked fortress with mortar well, turrets, side sponsons | same | Cần sửa |
| `fortress_hive` | boss | Cần sửa | Cần sửa | LOD1 share 19% | Tốt | tracked fortress with radome and drone racks | same | Cần sửa |
| `fpv_carrier` | wheeled | Cần sửa | Cần sửa | triangles 2484 under 3000; missing parts: axles | Cần sửa | 6x6 truck with a plain box body; launcher grid on the roof reads | same | Cần sửa |
| `garuda` | boss | Kém | Kém | triangles 2840 under 10000; missing parts: body; muzzles: muzzles 6/8; proportions vs B-2A Spirit: h/L -35%; LOD1 share 8% | Kém | flat flying-wing slab, 2840 triangles; no volume or engine detail for a boss | - | Kém |
| `glide_bomber` | jet | Kém | Kém | triangles 1624 under 4000; missing parts: intakes, exhaust, pylons; Mount_Flare 0/2; LOD1 share 26% | Cần sửa | thin tube fuselage and flat slab wings; planform reads, little volume | better | Kém |
| `gps_jammer_vehicle` | wheeled | Cần sửa | Cần sửa | missing parts: axles, stowage; LOD1 share 31% | Cần sửa | truck with an antenna tree and cable drum on an open bed; cab box | - | Cần sửa |
| `grad_truck` | wheeled | Cần sửa | Cần sửa | missing parts: stowage; proportions vs BM-21 Grad (Ural-375D): h/L +18% | Tốt | Ural-type cab, 40-tube rocket pack, wheels and lights read (new fewer triangles, same look) | same | Cần sửa |
| `ground_cruise_missile_vehicle` | wheeled | Cần sửa | Cần sửa | missing parts: axles, stowage; LOD1 share 34% | Tốt | 8x8 TEL with canisters, cab, equipment boxes | - | Cần sửa |
| `ground_drone_carrier` | tracked | Kém | Kém | missing parts: mantlet, idler, skirts, roof_mg, smoke, stowage | Cần sửa | slab tracked hull with drone racks; plain sides | - | Kém |
| `guard_tower` | tower | Kém | Cần sửa | LOD1 share 23% | Tốt | lattice watchtower with a glazed cabin, readable | same | Cần sửa |
| `guard_tower_a` | tower | Kém | Cần sửa | LOD1 share 20% | Tốt | tall watchtower with radar head, readable | same | Cần sửa |
| `guard_tower_b` | tower | Cần sửa | Cần sửa | missing parts: antenna; LOD1 share 68% | Cần sửa | gun on a pedestal in a sandbag ring, a thin ring for a tower | same (the sheet looked worse, but the GLB only gained pad and shield detail: see "Worse than old") | Cần sửa |
| `gun_turret` | tower | Kém | Cần sửa | LOD1 share 26% | Tốt | armoured gun house on a cast ring base, hatches, hazard bands | same | Cần sửa |
| `gun_turret_a` | tower | Kém | Cần sửa | LOD1 share 21% | Tốt | long-gun turret on a cast ring base | same | Cần sửa |
| `gun_turret_b` | tower | Kém | Tốt |  | Tốt | twin-gun turret with a dish on a cast base | same | Tốt |
| `gunship_heli` | helicopter | Kém | Kém | missing parts: stub_wings; mounts: Turret (main mount); Mount_Flare 0/2; proportions vs Mi-24 Hind: w/L -13%, h/L -26%; LOD1 share 35% | Tốt | Ka-52-like coaxial rotors, stub wings, tandem canopy | better | Kém |
| `headquarters` | hq | Kém | Cần sửa | mounts: Mount_mg 1/2; LOD1 share 28% | Tốt | multi-storey HQ with rooftop turret, helipad, mast, flags | same | Cần sửa |
| `heavy_aa` | wheeled | Cần sửa | Cần sửa | missing parts: axles, stowage; LOD1 share 29% | Cần sửa | truck with an open flat bed and a small launcher; cab and bed plain boxes | better | Cần sửa |
| `heavy_bomber` | jet | Cần sửa | Cần sửa | triangles 3540 under 4000; mounts: Mount_gun 0/1; Mount_Flare 0/2; proportions vs B-52H Stratofortress: h/L +13%; LOD1 share 14% | Cần sửa | swept wing and T-tail read; slim tube fuselage, flat slab wings and tail | better | Cần sửa |
| `heavy_flak_tower` **rebuilt** | tower | Cần sửa | Cần sửa | triangles 1116 under 2000; missing parts: antenna; LOD1 share 84% | Kém | box gun house with a stick barrel on a sandbag ring; too little detail for a heavy flak tower | same | Kém |
| `heavy_lift_helicopter` | helicopter | Cần sửa | Cần sửa | triangles 3858 under 4000; missing parts: weapons; Mount_Flare 0/2 | Tốt | Mi-26-like fuselage, 8-blade rotor, gear | - | Cần sửa |
| `heavy_rocket_artillery` | wheeled | Cần sửa | Cần sửa | missing parts: axles, stowage; proportions vs 9A52-2 Smerch (MAZ-543M): h/L +21% | Tốt | 8x8 with a large tube pack, cab glass, outriggers | same | Cần sửa |
| `heavy_tank` | tracked | Cần sửa | Cần sửa | missing parts: mantlet, idler, stowage | Cần sửa | flat slab hull and a low flat turret; reads as a tank, few volumes | better | Cần sửa |
| `heavy_turret` | tower | Kém | Cần sửa | LOD1 share 33% | Tốt | twin-gun armoured turret on a cast bastion, dense detail (new: pale cast base) | same | Cần sửa |
| `heavy_turret_a` | tower | Kém | Kém | muzzles: Muzzle_main 1/2 (main); LOD1 share 28% | Tốt | twin long guns on a cast bastion | same | Kém |
| `heavy_turret_b` | tower | Kém | Kém | muzzles: Muzzle_main 1/2 (main); LOD1 share 32% | Tốt | quad-gun turret on a cast bastion | same | Kém |
| `helipad` | obstacle | Cần sửa | Cần sửa | LOD1 share 20% | Cần sửa | flat marked pad only; no lights, windsock or edge detail | same | Cần sửa |
| `helipad_a` | obstacle | Cần sửa | Cần sửa | LOD1 share 34% | Cần sửa | plain half-tube hangar over the pad; shell has no ribs or doors | same | Cần sửa |
| `helipad_b` | obstacle | Tốt | Tốt |  | Tốt | pad with fuel bowser, crates and a dish | same | Tốt |
| `hover_gunboat` | ground | Cần sửa | Cần sửa | triangles 2202 under 3000 | Kém | flat slab hull with a box deckhouse; no skirt, deck or bow detail for a ship | better | Kém |
| `hydra_sub` | boss | Cần sửa | Cần sửa | triangles 7548 under 10000; LOD1 share 12% | Tốt | submarine with VLS hatches, sail, planes | - | Cần sửa |
| `hyperion` | boss | Cần sửa | Cần sửa | triangles 7914 under 10000; Mount_APS missing; LOD1 share 16% | Tốt | hexagonal ring station with solar arrays and core | - | Cần sửa |
| `ifv` | tracked | Kém | Kém | missing parts: mantlet, idler, roof_mg, stowage | Tốt | Bradley-like hull and turret with TOW box, hatches, tracks | better | Kém |
| `inflatable_decoy` | tower | Kém | Kém | triangles 1378 under 2000; missing parts: base, walls, roof, antenna | Cần sửa | soft blob tank on pegs; reads as an inflatable but the gun and hull are crude | same | Kém |
| `interceptor_drone_vehicle` **rebuilt** | wheeled | Kém | Kém | triangles 1494 under 3000; missing parts: axles, stowage; muzzles: Muzzle_aam 0/1; mounts: Mount_aam 0/1; LOD1 share 65% | Kém | box cab and box launcher on a flat chassis; reads only as a generic truck | better | Kém |
| `interceptor_jet` | jet | Kém | Kém | triangles 1500 under 4000; missing parts: exhaust, pylons; muzzles: Muzzle_aam 0/1; mounts: Mount_aam 0/1; Mount_Flare 0/2; LOD1 share 25% | Cần sửa | stick fuselage with slab wings and box intakes; planform reads, little volume | better | Kém |
| `iron_beam` | wheeled | Cần sửa | Cần sửa | triangles 2888 under 3000; missing parts: axles, stowage; Mount_APS missing | Cần sửa | 8x8 truck with a plain box body and laser head; few panel details | same | Cần sửa |
| `ixion` | boss | Tốt | Tốt |  | Cần sửa | BelAZ mine truck with a 125 mm turret reads; slab body sides, small turret for a boss | redesign (prompt 26 D1, giant wheel -> mine truck; the old GLB lacks the 8 part nodes) | Cần sửa |
| `kraken` | boss | Cần sửa | Cần sửa | Mount_APS missing; LOD1 share 4% | Tốt | carrier deck with island and parked aircraft | - | Cần sửa |
| `kronos` | boss | Kém | Kém | muzzles: muzzles 3/5; proportions vs Bagger 288: w/L +60%, h/L -24%; LOD1 share 9% | Cần sửa | bucket-wheel excavator reads; body is stacked boxes, few bevels | better | Kém |
| `lancet_truck` | wheeled | Cần sửa | Cần sửa | triangles 2314 under 3000; missing parts: axles | Cần sửa | 6x6 with box launcher and box cab; little bevel or detail | same | Cần sửa |
| `landing_craft` | ship | Kém | Kém | triangles 498 under 8000; missing parts: mast, turrets, ciws, boats; proportions vs LCM-8: w/L +46%; LOD1 share 29% | Kém | open tub hull with a box wheelhouse, 498 triangles; no ramp hinge, deck or bow detail | same | Kém |
| `landing_hovercraft` | boss | Cần sửa | Cần sửa | Mount_APS missing; LOD1 share 13% | Tốt | LCAC-like skirt, fans, deck ramps | same | Cần sửa |
| `laser_ad_station` **rebuilt** | tower | Kém | Kém | triangles 390 under 2000; missing parts: walls; Mount_APS missing; LOD1 share 83% | Kém | box model: one block with a dome and a box sensor, 390 triangles | same | Kém |
| `laser_tank` | tracked | Kém | Kém | triangles 3844 under 4000; missing parts: mantlet, idler, skirts, roof_mg, smoke, stowage | Cần sửa | slab hull with a box housing and laser dish; no turret volume | better | Kém |
| `leviathan` | boss | Kém | Kém | Mount_APS missing; proportions vs Iowa-class battleship: w/L +55%; LOD1 share 4% | Tốt | battleship: flared hull, turrets, tiered superstructure, masts | same | Kém |
| `light_attack_heli` | helicopter | Cần sửa | Cần sửa | triangles 3418 under 4000; muzzles: Muzzle_missile 0/1; mounts: Turret (main mount); Mount_Flare 0/2; proportions vs AH-6 Little Bird (same frame as the scout): h/L +57% | Tốt | attack helicopter with tandem canopy, wings, rockets | - | Cần sửa |
| `light_tank` | tracked | Kém | Kém | missing parts: mantlet, idler, skirts, roof_mg, smoke, stowage | Tốt | BMD-like low hull with a round turret, wheels and tracks read | better | Kém |
| `logistics_station` | tower | Cần sửa | Cần sửa | triangles 1576 under 2000; missing parts: walls, roof, antenna; LOD1 share 32% | Cần sửa | containers and a forklift on a flat slab; no shed, roof or fence | better | Cần sửa |
| `long_sam` | wheeled | Cần sửa | Cần sửa | triangles 2980 under 3000; missing parts: axles, stowage | Tốt | S-300-like TEL with four tubes, cab, outriggers | same | Cần sửa |
| `main_battle_tank` | tracked | Cần sửa | Cần sửa | missing parts: mantlet, idler; proportions vs Leopard 2A4: h/L +15% | Tốt | T-90/Leopard-like angled turret, side skirts, stowage, long gun | better | Cần sửa |
| `manpads_tower` | tower | Cần sửa | Cần sửa | triangles 1750 under 2000; LOD1 share 84% | Tốt | brick ring with tripod MANPADS and flag | - | Cần sửa |
| `mega_gunship` | boss | Kém | Kém | muzzles: muzzles 7/9; proportions vs CH-47F Chinook: h/L +57%; LOD1 share 18% | Tốt | Chinook-like tandem rotors, long fuselage, stub wings | same | Kém |
| `mg_bunker` | tower | Cần sửa | Cần sửa | missing parts: base; LOD1 share 69% | Tốt | domed earth bunker with camo net, sandbag MG nest, door | same | Cần sửa |
| `mg_bunker_a` | tower | Cần sửa | Cần sửa | missing parts: base | Tốt | camo dome bunker with twin MG embrasure | same | Cần sửa |
| `mg_bunker_b` | tower | Cần sửa | Cần sửa | missing parts: base | Tốt | camo dome bunker with flamer tanks | same | Cần sửa |
| `microwave_vehicle` **rebuilt** | wheeled | Cần sửa | Cần sửa | triangles 1664 under 3000; missing parts: axles, stowage | Kém | box cab, box bed and a flat panel emitter; reads only as a generic truck | same | Kém |
| `mine_layer` | tracked | Kém | Kém | triangles 3872 under 4000; missing parts: mantlet, idler, skirts, sight, roof_mg, smoke, stowage | Cần sửa | slab hull with a mine-cassette deck and chute; tracks read | better | Kém |
| `mine_rocket_truck` | wheeled | Cần sửa | Cần sửa | missing parts: axles, stowage | Cần sửa | truck with a plain box launcher; cab box | - | Cần sửa |
| `minefield` | obstacle | Tốt | Tốt |  | Tốt | fenced plot with warning signs and mine bumps (new: pale sand ground) | same | Tốt |
| `minefield_a` | obstacle | Tốt | Tốt |  | - | no sheet (the scan wrote none; branch model of an unscanned def?) | - | Tốt |
| `minefield_b` | obstacle | Tốt | Tốt |  | - | no sheet (the scan wrote none; branch model of an unscanned def?) | - | Tốt |
| `missile_battery` | tower | Kém | Tốt |  | Tốt | Patriot-like launcher, radar mast, generator on a pad | same | Tốt |
| `missile_battery_a` | tower | Kém | Tốt |  | Tốt | launcher with phased-array radar, mast, pad | same | Tốt |
| `missile_battery_b` | tower | Kém | Tốt |  | Tốt | launcher with large dish radar, pad | same | Tốt |
| `missile_boat` | ship | Kém | Kém | triangles 630 under 8000; missing parts: turrets, ciws, boats; LOD1 share 27% | Kém | box model: wedge slab hull with two box launchers and a box wheelhouse, 630 triangles | same | Kém |
| `mlrs` | wheeled | Cần sửa | Cần sửa | triangles 2652 under 3000; missing parts: axles, stowage | Cần sửa | HIMARS-like truck; pod and cab plain boxes, few details | same | Cần sửa |
| `mobile_fortress` | boss | Kém | Kém | proportions vs NASA Crawler-Transporter: w/L -35%, h/L +238%; LOD1 share 17% | Tốt | tracked fortress, turrets, sponsons, dense detail | same | Kém |
| `mobile_repair_vehicle` | wheeled | Cần sửa | Cần sửa | missing parts: axles, stowage; proportions vs M88A1 (same frame as the engineer vehicle): w/L +11%, h/L -16% | Cần sửa | boxy 6x6 with crane and tool boxes; body plain box | - | Cần sửa |
| `moloch` | boss | Cần sửa | Cần sửa | missing parts: running_gear; LOD1 share 12% | Kém | box model: stacked rectangular blocks on tracks, no bevels; weak boss silhouette | better | Kém |
| `monster` | boss | Cần sửa | Cần sửa | boss part nodes missing: mortar:Main_cannon*; LOD1 share 12% | Cần sửa | giant twin-hull tracked gun reads; stacked slabs, few bevels | - | Cần sửa |
| `morrigan` | boss | Kém | Kém | triangles 1344 under 10000; missing parts: running_gear; proportions vs Su-57: h/L -25%; LOD1 share 20% | Kém | flat flying-wing slab, 1344 triangles; far too little volume and detail for a boss | same | Kém |
| `mortar_carrier` | tracked | Kém | Kém | triangles 3242 under 4000; missing parts: mantlet, idler, skirts, smoke, stowage; proportions vs M1064 (M113A3 hull): h/L +49% | Cần sửa | M113-like box hull (true to type) with open hatch and mortar; plain sides | better | Kém |
| `next_gen_tank` | tracked | Kém | Kém | missing parts: mantlet, idler, smoke, stowage; Mount_APS missing; proportions vs Leopard 2A4 (same frame as the MBT): h/L +14% | Tốt | modern tank with long gun, RWS, skirts, detailed | - | Kém |
| `nlos_atgm_vehicle` **rebuilt** | wheeled | Cần sửa | Cần sửa | triangles 2048 under 3000; missing parts: axles, stowage | Kém | box cab and box launcher on a flat chassis; generic truck | better | Kém |
| `nuke_train` | boss | Kém | Cần sửa | LOD1 share 5% | Tốt | loco, missile wagon and escort wagons read as an armoured train | same | Cần sửa |
| `nyx` | boss | Kém | Kém | triangles 3526 under 10000; missing parts: superstructure; muzzles: muzzles 3/7; Mount_APS missing; LOD1 share 12% | Cần sửa | Zumwalt-like tumblehome hull and deckhouse read; plain surfaces, 3526 triangles for a boss | - | Kém |
| `one_shot_atgm_tower` | tower | Cần sửa | Cần sửa | LOD1 share 66% | Cần sửa | box bunker with a launcher box on a timber base; boxy | - | Cần sửa |
| `prop_attack_plane` | jet | Cần sửa | Cần sửa | triangles 2994 under 4000; missing parts: tail, intakes, exhaust; Mount_Flare 0/2 | Tốt | Super Tucano-like prop plane, canopy, stores | - | Cần sửa |
| `radar_atgm_vehicle` | tracked | Kém | Kém | triangles 2672 under 4000; missing parts: mantlet, idler, skirts, hatches, sight, roof_mg, smoke, stowage | Cần sửa | slab tracked hull with a radar box and launch rails; plain | - | Kém |
| `radar_scout` **rebuilt** | wheeled | Kém | Kém | triangles 1192 under 3000; missing parts: axles, glass, stowage; LOD1 share 66% | Kém | box model: wedge box hull on four wheels with a mast; no glass, lights or panel detail | same | Kém |
| `radar_site` **rebuilt** | tower | Kém | Kém | triangles 900 under 2000; missing parts: walls | Kém | plain box hut and a thin lattice dish on a slab, 900 triangles; no sandbags, roof or fence | same | Kém |
| `radar_support_vehicle` | wheeled | Cần sửa | Cần sửa | missing parts: axles, stowage | Cần sửa | 6x6 with mast radar; body plain box | - | Cần sửa |
| `rail_supergun` | boss | Kém | Cần sửa | LOD1 share 3% | Tốt | railway gun on bogies with long barrel, ammo wagons added | better | Cần sửa |
| `railgun_truck` | wheeled | Cần sửa | Cần sửa | triangles 2924 under 3000; missing parts: axles, stowage | Cần sửa | 8x8 with a box rail launcher; cab and body plain boxes | same | Cần sửa |
| `recoilless_gun_tower` | tower | Cần sửa | Cần sửa | LOD1 share 69% | Tốt | brick ring with recoilless gun on tripod and ammo | - | Cần sửa |
| `recoilless_jeep` **rebuilt** | wheeled | Cần sửa | Cần sửa | triangles 1606 under 3000; missing parts: axles, stowage | Kém | box jeep with a stick gun, 1606 triangles; no windscreen frame, lights or crew detail | better | Kém |
| `recon_drone` | jet | Kém | Kém | triangles 890 under 4000; missing parts: canopy, tail, intakes, exhaust, flares; proportions vs Bayraktar TB2: h/L -46% | Cần sửa | Predator-like long wing and V-tail read; very thin, 890 triangles | better | Kém |
| `recon_jet` | jet | Kém | Kém | triangles 768 under 4000; missing parts: intakes, exhaust, pylons, stores, flares; LOD1 share 33% | Cần sửa | SR-71 planform and nacelles read; 768 triangles, flat chines, no canopy shape | same | Kém |
| `repair_bay` **rebuilt** | tower | Cần sửa | Cần sửa | triangles 1152 under 2000; missing parts: antenna | Kém | box shed with a gantry frame, 1152 triangles; no doors, roof ribs or tools | same | Kém |
| `river_gunboat` | ground | Cần sửa | Cần sửa | triangles 2302 under 3000; LOD1 share 33% | Cần sửa | gunboat hull with turrets and deckhouse reads; slab sides | - | Cần sửa |
| `river_patrol_boat` | ground | Cần sửa | Cần sửa | triangles 1624 under 3000 | Kém | box deckhouse on a slab hull with box engines, 1624 triangles; reads as blocks, not a boat | - | Kém |
| `rocket_technical` | wheeled | Cần sửa | Cần sửa | triangles 2948 under 3000; missing parts: axles, stowage; proportions vs Toyota Hilux (7th gen, double cab): h/L +25% | Cần sửa | pickup with rocket pod and MG; boxy cab, few details | better | Cần sửa |
| `rocket_turret` | tower | Cần sửa | Tốt |  | Tốt | box launcher on a cradle in a cast ring, readable | same | Tốt |
| `rocket_turret_a` | tower | Cần sửa | Tốt |  | Tốt | tube-pack launcher on a cast ring | same | Tốt |
| `rocket_turret_b` | tower | Tốt | Tốt |  | Tốt | twin-pod launcher on a cast ring | same | Tốt |
| `sam_launcher` | tracked | Kém | Kém | missing parts: mantlet, idler, skirts, hatches, sight, smoke, stowage | Tốt | tracked TEL with a six-missile rack, readable | better | Kém |
| `scout_heli` | helicopter | Cần sửa | Cần sửa | triangles 2602 under 4000; missing parts: stub_wings; mounts: Turret (main mount); Mount_Flare 0/2; proportions vs MH-6 Little Bird: h/L +58% | Tốt | MD 500-like egg cabin, skids, rotor and tail | better | Cần sửa |
| `scout_jeep` | wheeled | Cần sửa | Cần sửa | triangles 2422 under 3000; missing parts: axles | Tốt | open jeep with crew, roll bar and MG, readable | same | Cần sửa |
| `sea_corvette` | ship | Kém | Kém | triangles 1884 under 8000; missing parts: boats; Mount_APS missing; LOD1 share 16% | Kém | slab hull with box deckhouses, 1884 triangles; no bow flare, CIWS or deck detail | better | Kém |
| `sea_cruiser` | ship | Kém | Kém | triangles 5416 under 8000; missing parts: boats; Mount_APS missing; proportions vs Kirov-class battlecruiser: w/L +53%; LOD1 share 8% | Cần sửa | cruiser reads (helideck, superstructure, guns); hull is a flat slab, 5416 triangles | same | Kém |
| `searchlight` | tower | Cần sửa | Cần sửa | triangles 1292 under 2000; missing parts: base, antenna | Cần sửa | drum lamp on a post in a sandbag ring; simple, few details | same | Cần sửa |
| `shahed_truck` | wheeled | Cần sửa | Cần sửa | triangles 2616 under 3000; missing parts: axles; LOD1 share 67% | Tốt | truck with a slanted Shahed launch rack, readable | same | Cần sửa |
| `shield_carrier` | wheeled | Kém | Kém | triangles 2476 under 3000; missing parts: axles, glass, stowage; proportions vs Boxer 8x8: h/L +52% | Cần sửa | box 8-wheel hull with a dish emitter; plain flat sides | better | Kém |
| `shield_tower` | tower | Cần sửa | Cần sửa | missing parts: walls, roof, antenna | Tốt | tapered emitter tower with ring, capacitor drums, base | same | Cần sửa |
| `shield_tower_a` | tower | Kém | Cần sửa | missing parts: walls, antenna | Tốt | emitter tower inside a lattice dome cage | same | Cần sửa |
| `shield_tower_b` | tower | Kém | Cần sửa | missing parts: walls, roof, antenna; LOD1 share 33% | Tốt | emitter pylons ring with central dome (new: pale cast deck) | same | Cần sửa |
| `shorad_vehicle` | wheeled | Cần sửa | Cần sửa | triangles 2000 under 3000; missing parts: axles, stowage | Cần sửa | boxy 4x4 with a turret and missile pods; cab and body plain | better | Cần sửa |
| `siege_tank` | tracked | Kém | Kém | missing parts: hull, mantlet, idler, skirts, smoke, stowage | Tốt | heavy tracked SPG with a big mortar and twin guns, dense detail | same | Kém |
| `silver_bug` | boss | Cần sửa | Cần sửa | Mount_APS missing; LOD1 share 8% | Tốt | wedge flying carrier with engines and greebles | same | Cần sửa |
| `sky_fortress` | boss | Kém | Kém | triangles 3084 under 10000; LOD1 share 25% | Cần sửa | C-130 planform reads; tube fuselage and slab wings with little volume | better | Kém |
| `sky_gunship` | jet | Kém | Kém | triangles 3652 under 4000; missing parts: tail, intakes, exhaust, pylons; Mount_Flare 0/2; LOD1 share 26% | Cần sửa | AC-130: high wing, 4 props, side guns read; tube fuselage, flat slab wings, little panel detail | better | Kém |
| `smoke_carrier` | tracked | Kém | Kém | triangles 3698 under 4000; missing parts: mantlet, idler, skirts, sight, roof_mg, stowage; proportions vs M58 Wolf (M113 hull): h/L +21% | Cần sửa | M113-like box hull with smoke generator drum; plain sides | better | Kém |
| `sp_mortar` **rebuilt** | wheeled | Cần sửa | Cần sửa | triangles 2806 under 3000; missing parts: axles, glass, stowage | Kém | box model: plain box 8-wheel hull with a box turret; no glacis, lights or stowage | better | Kém |
| `stealth_bomber` | jet | Kém | Kém | triangles 2096 under 4000; missing parts: tail, pylons, flares; proportions vs B-2A Spirit: h/L -28% | Tốt | B-2 flying wing with sawtooth trailing edge, readable | same | Kém |
| `stealth_fighter` | jet | Kém | Kém | triangles 3336 under 4000; missing parts: tail, intakes, pylons; Mount_Flare 0/2; proportions vs F-22A Raptor: h/L -37%; LOD1 share 16% | Tốt | F-22-like planform, canted fins, intakes | same | Kém |
| `stealth_naval_strike` | jet | Kém | Kém | triangles 2124 under 4000; missing parts: fuselage, tail, pylons, flares; proportions vs B-2A Spirit (same frame as the stealth bomber): h/L -27%; LOD1 share 10% | Kém | flat triangle slab with stickers, 2124 triangles; no volume for its role | - | Kém |
| `strike_drone` | jet | Kém | Kém | triangles 1968 under 4000; missing parts: canopy, tail, intakes, exhaust, flares; proportions vs MQ-9A Reaper: h/L -14%; LOD1 share 17% | Cần sửa | MQ-9-like long wing, V-tail and stores read; thin, 1968 triangles | same | Kém |
| `stymphalos` | boss | Kém | Kém | triangles 4186 under 10000; missing parts: body, lift; muzzles: muzzles 5/9; LOD1 share 15% | Tốt | swarm formation of delta drones, readable | - | Kém |
| `super_gun` | structure | Cần sửa | Cần sửa | missing parts: walls | Tốt | twin heavy guns in a turret on a cast bastion | - | Cần sửa |
| `supply_truck` | wheeled | Cần sửa | Cần sửa | triangles 2862 under 3000; missing parts: axles | Tốt | 8x8 cargo truck with tarp hoops, cab glass, crates | same | Cần sửa |
| `supreme_command` | boss | Cần sửa | Cần sửa | LOD1 share 24% | Tốt | 8-wheel command vehicle with mast, radome and windows | same | Cần sửa |
| `swarm_carrier` | jet | Kém | Kém | triangles 3464 under 4000; missing parts: tail, intakes, exhaust, pylons, stores; Mount_Flare 0/2; LOD1 share 18% | Cần sửa | C-130 planform reads; tube fuselage, slab wings, little detail | better | Kém |
| `tank_destroyer` | tracked | Kém | Kém | missing parts: mantlet, idler, skirts, smoke, stowage; proportions vs 2S25 Sprut-SD: h/L -19% | Cần sửa | wide flat slab hull with a small low turret; long gun reads | better | Kém |
| `targeting_station` | structure | Cần sửa | Cần sửa | missing parts: roof; LOD1 share 35% | Tốt | lattice mast, dish, equipment hut on a pad | same | Cần sửa |
| `thermobaric_launcher` | tracked | Kém | Kém | missing parts: mantlet, idler, smoke, stowage; proportions vs TOS-1A Solntsepyok: w/L +25% | Cần sửa | TOS-1-like box launcher on a slab hull; launcher box plain | better | Kém |
| `titan_tank` | tracked | Kém | Kém | missing parts: mantlet, idler, smoke, stowage; Mount_APS missing; LOD1 share 30% | Tốt | twin-gun heavy tank, sponson MGs, layered turret | better | Kém |
| `towed_at_gun` | wheeled | Kém | Kém | triangles 1996 under 3000; missing parts: axles, cab, glass, lights; LOD1 share 26% | Tốt | towed AT gun with shield, split trail, wheels | - | Kém |
| `troop_shelter` **rebuilt** | tower | Kém | Kém | triangles 916 under 2000; missing parts: base, antenna; LOD1 share 78% | Kém | box model: one sloped earth block with a flat roof, 916 triangles; no entrance, sandbags or vents read | same | Kém |
| `turtle_tank` | tracked | Kém | Kém | triangles 3938 under 4000; missing parts: hull, mantlet, idler, skirts, hatches, sight, roof_mg, smoke, stowage | Tốt | domed armour shell with plates over tracks, distinctive | better | Kém |
| `twin_rotor_gunship` | helicopter | Cần sửa | Cần sửa | missing parts: tail_rotor; mounts: Mount_mg 0/1, Turret (main mount); Mount_Flare 0/2; LOD1 share 31% | Tốt | tandem-rotor gunship with gear and sponsons | - | Cần sửa |
| `twin_tank` | tracked | Cần sửa | Cần sửa | missing parts: mantlet, idler | Tốt | twin-gun tank, angled turret, skirts, stowage | better | Cần sửa |
| `typhon` | boss | Kém | Kém | triangles 6876 under 10000; proportions vs Project 941 Akula (Typhoon): w/L +58%; LOD1 share 26% | Cần sửa | submarine hull, sail and hatches read; plain long hull for a boss | same | Kém |
| `uav_loiter_strike` | jet | Kém | Kém | triangles 1084 under 4000; missing parts: canopy, tail, intakes, flares; LOD1 share 26% | Cần sửa | Predator-like long wing and pusher prop read; thin, 1084 triangles | - | Kém |
| `vbied` | wheeled | Cần sửa | Cần sửa | triangles 1574 under 3000; missing parts: axles, glass; LOD1 share 66% | Cần sửa | up-armoured pickup with plates and a dozer blade; crude by intent, low detail | better | Cần sửa |
| `visual_jammer` **rebuilt** | tower | Kém | Kém | triangles 592 under 2000; missing parts: walls, roof | Kém | box model: one green block with a post and two drums, 592 triangles | same | Kém |
| `wall_gun` | obstacle | Tốt | Tốt |  | Tốt | Hesco wall section with gun gap and wire | - | Tốt |
| `wall_hesco` | obstacle | Cần sửa | Cần sửa | LOD1 share 70% | Tốt | Hesco bastion run with wire on top | - | Cần sửa |
| `wall_t` | obstacle | Cần sửa | Cần sửa | LOD1 share 18% | Tốt | T-wall concrete panels, readable | - | Cần sửa |
| `wheeled_gun` | wheeled | Cần sửa | Cần sửa | missing parts: axles, glass, stowage; proportions vs B1 Centauro: w/L -23%, h/L -19% | Tốt | Centauro-like 8x8 with a long gun turret | better | Cần sửa |
| `wheeled_howitzer` **rebuilt** | wheeled | Cần sửa | Cần sửa | triangles 2136 under 3000; missing parts: axles, stowage | Kém | flat truck bed with a stick barrel and a box, 2136 triangles; reads as a truck, not a howitzer | better | Kém |
| `wingman_drone` | jet | Kém | Kém | triangles 1064 under 4000; missing parts: canopy, tail, flares; LOD1 share 27% | Cần sửa | delta loyal-wingman planform reads; flat slab wing, 1064 triangles | better | Kém |
| `zu23_technical` | wheeled | Cần sửa | Cần sửa | triangles 1996 under 3000; missing parts: axles | Tốt | pickup with ZU-23-2 twin cannon, cab glass, readable | better | Cần sửa |

## Counts

- Final: Tốt 22, Cần sửa 121, Kém 87 (230 models; 4 without a sheet graded on static*).
- Visual: Tốt 125, Cần sửa 75, Kém 26 (226 sheets).
- Old vs new (176 with an old sheet): better 60, same 115, worse 0, redesign 1.

## Worse than old

- `guard_tower_b` looked worse on the sheet (thinner, lower sandbag ring; 2,154 vs 2,594 triangles) but is not: the GLB
  went 2,594 -> 2,746 with identical runtime nodes and only the pad and shield changed (V2 kit, prompt 27 wave 6a). The
  new sheet draws fewer triangles than the file holds (2,154 of 2,746; `guard_tower` 6,180 of 6,772), so the
  difference comes from how ModelScan loads the current model (the game path) against the old copy, not from the GLB.
  Not restored; worth a look by whoever owns ModelScan.
- `ixion` differs completely, by design: prompt 26 D1 turned the giant wheel into the armoured BelAZ mine truck; the
  old GLB lacks the 8 boss part nodes the def now names. Not restored.
- Must-check list: `sky_gunship` better (3,652 vs 2,708 triangles, more panel and gun detail, same silhouette); every
  structure, tower and HQ with an old sheet is the same or better (several statics got the pale cast concrete of
  prompt 27 wave 7, which is the lead rule there, not a regression). No GLB was restored from 07444b14.

## Rebuilt in this pass (15)

| model | triangles before -> after | before | after |
|---|---|---|---|
| `heavy_flak_tower` | 1,116 -> 8,902 | box gun house + stick barrel on a bag ring | octagonal cast emplacement, 3-course staggered sandbag parapet, ammo niches, cruciform platform, 88 mm with carriage, shield, recuperators, baffle brake, rangefinder, aerial |
| `flare_tower` | 680 -> 5,102 | a table on four legs with a launcher box | braced steel legs on footings, plank deck, sandbag parapet, ladder, canvas roof, crates, aerial, 8-tube flare rack on a yoke |
| `laser_ad_station` | 390 -> 3,434 | one block with a dome | slab, T-wall blast panels, ribbed shelter with coolers, generator, cable trough, search panel mast, yoke + telescope beam director with fin rings; Mount_APS added |
| `visual_jammer` | 592 -> 3,672 | one block, a post, two drums | pad, ribbed shelter with railed roof, sandbag wall, lattice mast with lamp head, smoke drums on a rack, generator, camo net, aerials |
| `fire_control_centre` | 612 -> 2,874 | two plain blocks and a mast | sunken bunker under earth berms with concrete front and embrasures, roof slab with vents, sandbagged entrance, plotting shelter, generator, camo net, radar on a mast (Radar pivot kept) |
| `radar_site` | 900 -> 4,252 | box hut and a thin lattice dish | lattice tower with railed platform and ladder, truss reflector on the Radar pivot, hut with pitched roof and windows, sandbag wall, fence, generator, drums, aerials |
| `troop_shelter` | 916 -> 3,158 | one sloped earth block | earth berms round a ribbed corrugated arch roof with concrete ends, doorway, steps, sandbag entrance walls, vents, aerial, crates, camo net |
| `repair_bay` | 1,152 -> 5,214 | box shed with a gantry frame | portal-frame shed with rafters and pitched corrugated roof, clad wall and end, roller door, gantry crane with hoist, benches, tool chests, tyre stack, drums, aerial |
| `interceptor_drone_vehicle` | 1,494 -> 4,068 | box cab and box launcher | detailed 4x4 armoured truck (frame, axles, fenders, glazed cab, stowage), six-cell launcher on a turntable, radar panel mast, Coyote pod on new Mount_aam + Muzzle_aam |
| `microwave_vehicle` | 1,664 -> 4,914 | box truck with a flat panel | 6x6 truck as above, generator container, cable reels, horn-cell emitter array with ribs and electronics box |
| `nlos_atgm_vehicle` | 2,048 -> 4,918 | box cab and box launcher | 6x6 truck as above, four-canister launcher on an elevating arm with rams, reload canisters, sensor mast, cab-roof MG |
| `radar_scout` | 1,192 -> 3,362 | wedge box on four wheels with a mast | Fennek-type faceted hull, fenders, glazing, side skirts, engine grille, stowage, smoke dischargers, telescopic mast with twin-lens head, shielded ring MG |
| `recoilless_jeep` | 1,606 -> 3,386 | box jeep with a stick gun | M151-type body with flared arches, grille, framed screen, seats, roll bar, spare, jerrycans, M40 with venturi breech, spotting rifle, handwheel |
| `sp_mortar` | 2,806 -> 5,748 | plain box 8x8 with a box turret | AMV hull with raked glacis and tapered flanks, fenders, vision blocks, hatches, bins, smoke dischargers, faceted AMOS turret with bustle and side plates, sight, roof MG |
| `wheeled_howitzer` | 2,136 -> 5,026 | flat bed, stick barrel and a box | CAESAR: armoured glazed cab, crew cab, platform with lockers, travel lock, mount cheeks, cradle, recoil cylinders, baffle brake, spade on arms, ammo |

Builder: `Tools/blender/mb_fix_l8.py` (registered last in build_assets.py). Every runtime node kept at its place;
only `Part_wheel` / `Part_wheelb` (placed by the mb_p34_parts wrapper at the wheels) moved by up to 0.5 m. Sizes
within 10 % of the old GLBs and the defs' modelSize (laser_ad_station, visual_jammer and repair_bay keep their
long side on Y). `glb_check.py --accept` with 0 errors. Re-render these 15 for the cards and the scan "after" sheets.
