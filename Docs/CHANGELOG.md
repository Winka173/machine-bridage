# Changelog

Every merge into `main` is a version, numbered from the first commit (a docs-only merge bumps the patch
number). Work on `feature/visual-overhaul` that is not on `main` yet sits under Unreleased; new entries go
there, and the next merge into `main` turns it into a version. Each version keeps its prompt notes and lists
its commits.

## Unreleased (feature/visual-overhaul)

- Prompt 29 appendix: `gun_100_river` and `gun_155_crusader` hit the ground only (high explosive, no anti-air round); a target-mask check (`TargetMaskTests`, `Tools/balance/target_mask_check.py`, Docs/checks/target_mask.md: 0 masks, 17 elite-only rounds no elite carries); outgoingDamageMult confirmed on every round a gun loads (DECISIONS "Prompt 29 appendix").

- Prompt 27 stand-in sweep: coastal_battery, super_gun, bulwark_post and uav_loiter_strike get their own models (they drew heavy_turret, mg_bunker, strike_drone); stand-in audit in Docs/models/STANDIN_AUDIT.md (DECISIONS "27 stand-in sweep").

- Prompt 27 wave 8: the remaining 198 models (munitions, debris, map props, towns, themes, harbor, terrain, trees, rubble, wrecks, base pieces, unlisted units) rebuilt or edge-treated on the V2 kit with lighter AO; aim120 and aim9 kept. Prompt 27's eight waves are complete (DECISIONS "27 wave 8a1" to "27 wave 8b7").

- Prompt 27 wave 5d: leviathan, caspian, typhon, landing_hovercraft and supreme_command on the V2 kit (wave 5 complete, DECISIONS "27 wave 5d").

- Prompt 27 wave 5b: kronos, moloch, nuke_train, armored_train and earth_borer on the V2 kit (DECISIONS "27 wave 5b").

- Prompt 27 wave 5c: command_airship, drone_mothership, mega_gunship, sky_fortress, daedalus and morrigan on the V2 kit; mega_gunship's lost mount nodes restored (DECISIONS "27 wave 5c").

- Prompt 27 wave 5a: behemoth, behemoth_inferno, behemoth_tempest, fortress_bastion and fortress_hive on the V2 kit (DECISIONS "27 wave 5a").

- Prompt 27 wave 7b: nine more structures on the V2 kit, blast_wall kept (wave 7 complete, DECISIONS "27 wave 7b").

- Prompt 27 wave 7a: cp_relay, shield_tower, dragons_teeth, minefield and their branches on the V2 kit (DECISIONS "27 wave 7a").

- Prompt 27 waves 6d and 6e: drone_hangar, ew_tower, heavy_turret, missile_battery and their branches, aa_gun_tower, flare_tower, searchlight and wreck_turret on the V2 kit; atgm_tower repainted pale (wave 6 complete, DECISIONS "27 wave 6d", "27 wave 6e").

- Prompt 27 waves 4c and 6c: prompt 29 flare tubes on the other nine aircraft and APS clusters on next_gen_tank and titan_tank (wave 4 complete); atgm_tower, c_ram and their branches and gun_pit on the V2 kit (DECISIONS "27 wave 4c", "27 wave 6c").

- Prompt 27 waves 4b and 6b: the jets cleaned with flare rows and the attack_jet_hd library canopy and nozzle; gun_turret, mg_bunker, rocket_turret and their branches on the V2 kit (DECISIONS "27 wave 4b", "27 wave 6b").

- Prompt 27 wave 6a: aa_turret, artillery_emplacement, guard_tower and their branches on the V2 kit (DECISIONS "27 wave 6a").

- Prompt 27 wave 4a: eight helicopters and drones on the V2 kit, prompt 29 flare tubes on three (DECISIONS "27 wave 4a").

- Models (prompt 27 wave 3h, the last of wave 3): armoured car, command vehicle, FPV carrier, Lancet truck, scout jeep (+hd), Grad truck, missile boat, sea corvette and landing craft rebuilt on the V2 kit (V2 wheels, extruded hulls, cabs and superstructures, lofted boat hulls, revolved barrels, tubes and masts); same nodes, pivots and proportions, 1.0-1.6x triangles (the Grad truck now under its old budget), brighter vertex colours; the 3g NLOS and radar ATGM vehicles brightened (their cards came out darker). Cards rendered by the lead after the merge.
- Balance round 2 (prompt 29, cloud): manifest tool (`Tools/balance/p29_apply.py`), one rounding, per-vehicle damage factor and drop time, base CP vs call cost, measure stamps; 7 FIX regressions, CP bank by mode, ~97 cards repriced; flare charges, APS capability and modes, vehicle missile loads; no low-health aircraft retreat; Gungnir a main boss (45 s global rail shot); prompt 28's army-band upkeep removed. Not run yet; report `Docs/balance/report_p29.md`.
- Models (prompt 27 wave 3g): microwave vehicle, NLOS and radar ATGM vehicles, radar scout, recoilless jeep, SHORAD vehicle, self-propelled mortar and wheeled howitzer rebuilt on the V2 kit (V2 wheels and track units, extruded hulls and cabs, revolved barrels, framed launchers and masts); same nodes, pivots and proportions, 1.0-1.4x triangles, brighter vertex colours; the 3f AA gun vehicle brightened (its card came out 1.8 % darker). Cards rendered by the lead after the merge.
- Models (prompt 27 wave 3f): wheeled gun, ZU-23 technical, rocket technical, hover gunboat, AA gun vehicle, airborne vehicle, fibre FPV carrier and interceptor drone vehicle rebuilt on the V2 kit (V2 wheels and track units, extruded hulls and cabs, lofted turret and hull, revolved barrels, tubes, spools and fan ducts, six-barrel AK-630); same nodes, pivots and proportions, 1.0-1.6x triangles, brighter vertex colours. Cards rendered by the lead after the merge.
- Models (prompt 27 wave 3e): supply truck, ammo carrier, counter-battery radar, EW jammer, railgun truck, Shahed truck, VBIED and bunker vehicle rebuilt on the V2 kit (V2 HEMTT, truck and pickup with V2 wheels and extruded cabs, chamfered shelters, bars and plates, revolved barrels and drone fuselages); same nodes, pivots and proportions, 1.1-1.3x triangles, brighter vertex colours. Cards rendered by the lead after the merge.
- Models (prompt 27 wave 3d): MLRS, elite MLRS, heavy rocket artillery, thermobaric launcher, ballistic launcher, long SAM, SAM launcher and Iron Beam rebuilt on the V2 kit (V2 wheels and running gear, extruded cabs and hulls, chamfered pods and decks, revolved tubes, canisters and missiles); every node, pivot and size kept.
- Models (prompt 27 wave 3c): AA vehicle (+hd), artillery (+hd), heavy AA, elite AA, mortar carrier, mine layer, smoke carrier and shield carrier rebuilt on the V2 kit (V2 running gear and wheels, extruded and chamfered hulls, one-surface barrels, revolved drums and tubes); same nodes, pivots and proportions, 1.3-1.56x triangles, brighter vertex colours. Cards rendered by the lead after the merge.
- Models (prompt 27 wave 3b): laser, flame, twin, BMPT, IFV, elite APC, armored bulldozer and engineer vehicle rebuilt on the V2 kit (V2 running gear, extruded and chamfered hulls, lofted turrets, one-surface barrels); same nodes, pivots and proportions, 1.4-1.6x triangles, brighter vertex colours. Cards rendered by the lead after the merge.
- Models (prompt 27 wave 3a): eight tanks rebuilt on the V2 kit (heavy, light, tank destroyer with their `_hd`, titan, turtle and the three elites on the new bases): V2 running gear, chamfered hulls, lofted turrets, one-surface barrels; same nodes, pivots and proportions, 1.4-1.6x triangles, brighter vertex colours. Cards not re-rendered yet.
- AI UI (28 local pass): tactic picker beside deck and commander (suggested for the commander, unlock by chapter, last pick per mode), HUD tactic switch with cooldown and per-squad tactics, scouted enemy tactic, AI hint line (Settings toggle), upkeep factor on the supply line, pressure lines, tower targeting modes on the Base screen and on a tap, player AI at Normal skill, Sandbox tactic per side and the internal AI viewer sheet. Compiled only; not played.
- AI (28 extras, cloud): EN/VI text tables for tactics, hints, tower modes, fire stances, upkeep, pressure and the AI viewer; unit-level "VÌ SAO"; Sandbox scenario tests and 5-seed fingerprint/campaign sweeps (Explicit, not run); design docs AI_DESIGN, TACTICS, ECONOMY; the applied research xlsx and its exporter.
- AI and economy (28 pass 5, cloud, Sim only): income falls with vehicles out against the cap (army bands); pressure tiers on a quiet battle (points worth more, a crate, a barrage on the passive side, armies revealed); Conquest's final phase; hit-and-run spread while backing off; tactic unlock and commander suggestions; the Sandbox sets each side's tactic. Not run yet.
- AI (28 pass 4, cloud, Sim only): tower targeting modes from the sheet (with `SimWorld.SetTowerMode`), the sheet's special tower rules, towers sharing a target, point defence ordered by mode; boss behaviour types weighting targets and big-attack aims, a slow turn to the most firepower, escorts screening the enemy mass and closing in on a new phase. Not run yet.
- AI (28 pass 3, cloud, Sim only): the unit layer and anti-stuck. Target score gains squad focus, tactic targets and friends in the line of fire; armour facing; role short moves when overwhelmed (no retreat on health, aircraft refit for ammunition only); scouts at sight edge; shoot-and-scoot for every gun with marked spots avoided; aircraft approach by the least anti-air and leave dense anti-air; squads take crowded passages in turns, re-score when idle and climb a stuck ladder. Not run yet.
- AI (28 pass 2, cloud, Sim only): the layered AI. `AiCommander` (general: plan, attack window, tasks, tactic, buying by the tactic's CP shares, supports by event, hints) and `SquadLayer` (squads of 3-6: valid actions scored 0-100 with "VÌ SAO" factors, switch margin and commitment, 7 states, Emergency Reposition, formations, focus fire, bounding overwatch, fall-back lines); `TacticalAi.Layered` keeps its helpers and drops health retreats; `aiBehaviour` data generated from the sheet (states, roles, units, 16 tactics, generals, tower modes, boss types); `DecisionLog` (J.2-J.4). Not run yet.
- AI (28 pass 1, cloud, Sim only): `Tools/ai/import_ai_xlsx.py` generates balance.json `ai` (world, the 21 parameters of the research sheet, the in-battle economy frame; each with value, min, max, metric, reason) and `Catalog.Ai` reads it; `SimWorld.Intel` is the shared World Model (strength, composition, threat layers, contacts with confidence, enemy groups, front, chokepoints, warnings, the five event kinds); `SimWorld.AiRandom` gives each AI layer its own seeded stream; `WorldModelTests` and the `AiParamSweep` tool are written, not yet run.
- Models (27 wave 2 pass B): the last nine flagged models fixed - renderer merges on `command_hq`, `shield_generator`, `siege_tank`; `flak_tower` and `sea_cruiser` lose unused moving-part nodes; zero-area triangles removed from `sky_gunship_hd`, `strike_jet`, `tank_buster`; `interceptor_jet` gets taller fins to match its `modelSize` (`siege_tank` keeps its 22 deploy parts, the ground cap is wrong for it).
- Models (27 wave 2 pass A): nine validator errors fixed with the smallest change - `mobile_fortress` gets the part nodes `Mount_gun` (roof howitzer) and `Mount_missile.001` (deck SAM), `headquarters` and the three helipads lose their zero-area triangles, and the proportions of `heavy_flak_tower`, `at_gun_emplacement`, `laser_ad_station` and `visual_jammer` now match their `modelSize`.

## v0.34.0: Prompt 26 (bosses: health, weapons, two-layer blasts, sizes, Boss Hunt health), prompt 27 wave 1 (the model pipeline and 43 new models), prompt 28 saved

2026-10-02 · merged into main together with v0.33.0 (the owner: "toàn bộ"); the design review PDF was rebuilt first (316 pages)

Main merges on feature/visual-overhaul since v0.33.0 was written (newest first): 3329117 the PDF rebuild; 593d785 wave 1c
pass B; 5ae66c9 wave 1c pass A; ba5eda4 wave 1b; 66ce86a wave 1a + Monster, Nyx; 8138b9b preview, budgets, Art Bible,
wave plan; 67dc88a experiment 1; 1536eff Step 0 and the GLB baseline; e25dc0b the 318-page PDF; 4a2b4c1 prompt 26 pass 3;
4633f03 prompt 26 pass 2; 78dbf58 prompt 26 pass 1. Docs only: 34b06fa prompt 28 and Docs/ai/Machine_Brigade_AI_Research.xlsx.

### Design review PDF rebuilt (DECISIONS "27 PDF rebuild")

- 316 pages: wave 1 models and cards, a new section 10h on the prompt 27 model pipeline, the Unreleased headings

### Prompt 27, wave 1c pass B: the last sixteen batch B units get their own models (DECISIONS "27 wave 1c pass B (lead pass, 2026-10-02)"); wave 1c complete

- Own models (V2 kit, `mb_p27_wave1c.py`) and cards for twin_rotor_gunship, ground_drone_carrier, mobile_repair_vehicle, radar_support_vehicle, towed_at_gun, flare_searchlight_tower, recoilless_gun_tower, bunker_shelter_tower, dazzler_vehicle, ground_cruise_missile_vehicle, aerial_tanker, heavy_lift_helicopter, bridging_vehicle, gps_jammer_vehicle, drone_net_tower, one_shot_atgm_tower; washes dropped

### Prompt 27, wave 1c pass A: sixteen batch B units get their own models (DECISIONS "27 wave 1c pass A (lead pass, 2026-10-02)")

- Own models (V2 kit, `mb_p27_wave1c.py`) and cards for aa_57mm_vehicle, mine_rocket_truck, prop_attack_plane, light_attack_heli, next_gen_tank, demolition_line_vehicle, combat_wreck_car, drone_hijack_vehicle, manpads_tower, river_patrol_boat, river_gunboat, coastal_ashm_vehicle, auto_loader_howitzer, amphib_light_vehicle, airborne_light_tank (+ its parachute proxy) and stealth_naval_strike; the colour washes are gone, no number or behaviour changed.

### Prompt 27, wave 1b: the other six batch D bosses (DECISIONS "27 wave 1b (lead pass, 2026-10-02)")

- Real models for Kraken (an aircraft carrier with a ski-jump, island, parked jets), Garuda (a 70 m B-2-style flying wing), Hyperion (a hexagonal mirror ring station, its own model), Stymphalos (eight delta-wing drones in V formation), Cerberus (three coupled big-wheeled cars) and Hydra (a small VLS submarine carrying six FPV drones); their colour washes dropped.

### Prompt 27, wave 1a + 1b (part): Ixion, Gungnir, Monster, Nyx (DECISIONS "27 wave 1a + 1b (part)")

- Real models for four stand-in bosses on the V2 kit: Ixion (an armoured BelAZ-75710 mine truck with a T-72-class turret), Gungnir (an electromagnetic railgun train with capacitor cars and a modern diesel tractor), Monster (an 800 mm self-propelled gun on four track clusters) and Nyx (a Zumwalt-style stealth destroyer); their colour washes dropped.

### Prompt 27, step 5: preview, budgets, Art Bible, wave plan (DECISIONS "27 preview + budgets + art bible")

- A Unity contact-sheet preview for named models (`ModelPreview.RenderBatch -mbPreview`: 8 angles plus detail / LOD1 / impostor views, luma JSON), budgets per class and tier in the GLB validator (Docs/models/BUDGETS.md), the Art Bible (Docs/models/art-bible.md) and the wave plan (Docs/models/PROGRESS.md).

### Prompt 27, step 3: experiment 1, the improved kit on four models (DECISIONS "27 experiment 1")

- The main battle tank, Su-27, Icarus and the Apache (and their `_hd` twins) rebuilt with new kit primitives and a shared parts library (Tools/blender/mb_kit27.py, mb_parts27.py, mb_p27_experiment.py): crisper edges, dished road wheels, hatches, a new gun, recessed bays, canopy frames; the Su-27 high-detail model's 390 zero-area triangles fixed; report Docs/models/EXPERIMENT_1.md.

### Prompt 27, steps 1-2: Step 0 audit and the GLB baseline (DECISIONS "27 step 0 + baseline")

- Docs/models/STEP0_AUDIT.md (the short audit for the 4-model experiment) and Tools/assets/glb_check.py, a static GLB analyzer and validator: Tools/assets/baseline.json covers all 400 GLBs, Docs/models/BASELINE.md sums it up (14 flagged).

### Prompt 26, pass 3 (E): Boss Hunts with the boss health from an estimated P (DECISIONS "26E")

Reduced scope again: no tests, sweeps or measures (compile only; no data changed).

- P, the player's damage a second on a boss, is estimated once from the carried deck (card ranks, gear, commander) by a formula
  (`HuntPower`); a hunt boss's health is P x its target seconds x 0.6 x m, its damage the data's x m. Replaces the old ramp and
  `KeepPace` on bosses: no quick mode's boss keeps pace with the arsenal any more (escorts, vehicles and towers still do).
- The week: 10 bosses with the mains at 4, 7 and 10 (3-2-2 minis), 66 s / 2.8 min targets, a 15 s rest, m = 1 + 0.06 per boss,
  survivors repaired 30 %, half the CP kept, a checkpoint at each leg's end, a 30 minute clock.
- The full hunt: 2.5 min mains, 1 min minis, m from x0.8 to x1.3 in story order, every boss a fresh battle (no army, the starting CP),
  only the supports kept, saved after every boss.
- Combat supports are capped at +40 % army strength; past it only the play-changing ones (an extra drop, quicker cards) are offered.
- Hunt tiers: Normal x1 / x1, Heroic (Hard) x1.3 / x1.15, Steel (Very Hard) x1.6 / x1.3 on the existing difficulty picker. Legendary
  and the hunt mutators are left.
- The applied Excel is re-exported with the 26AB and 26CD boss numbers; the "to measure" list is gathered in DECISIONS "26E".
- Written, not run: new cases in `Prompt20HuntTests`.

### Prompt 26, pass 2 (C and D): boss sizes, Ixion, Gungnir and the post-1945 rule (DECISIONS "26CD")

Reduced scope again: no tests, sweeps or measures; no Blender rebuild, camera pull-back or shadow work.

- Boss sizes as data (`size` / `variant.size`, solved by `Tools/balance/p26_cd.py`): the twelve mains and the minis to the
  prompt's table (Bastion 40 m, Moloch 40, Roc 80, Icarus 90, Caspian 36, Atlas 16 ...); hit radius, parts and mounts follow.
- Ixion is the armoured BelAZ-75710 mine truck (stand-in model): a 125 mm turret that loads a high-explosive shell against crowds
  and an armour-piercing one against single targets, a 2 s warned crush charge every 10 s, two roof machine guns, a strip of six
  mines dropped when it turns (20 s), eight breakable parts (tyres, turret, cab).
- Gungnir is a rail electromagnetic gun: one slug every 25 s through up to five vehicles in a line, blasting at the last
  (new `bombard.pierceMax`, `pierceDamage`).
- Every pre-1945 reference is gone (Ratte, Yamato, Gustav, Tsar Tank, Snow Cruiser, Akron / Zeppelin, Maxim Gorky, Pantherturm,
  Churchill Crocodile, Flak 36/37, Pak 40, Horten ...): reference lines, profiles, Guide, campaign text, the balance sheet's
  shape and reference columns, the new-content tracker (KS-19 100 mm heavy AA tower, JLENS radar aerostat that also shows stealth
  aircraft). Leviathan's main gun is 406 mm.
- Written, not run: `Prompt26CDTests` (the era scan, Ixion, Gungnir, Leviathan); the old tests whose rules moved were updated.

### Prompt 26, pass 1 (A and B): boss health, armour, phases, weapons and two-layer blasts (DECISIONS "26AB")

Reduced scope (no tests, sweeps or measures; every number is the prompt's starting value, solved on paper by
`Tools/balance/p26_ab.py`).

- Boss health by chapter from the prompt's table (main 22,000 at chapter 1 to 150,000 at 12; mini 9,000 to 57,000; interludes and
  the eight batch D bosses interpolated). The campaign no longer scales a boss by the player's arsenal (prompt 2's edge); the
  difficulty scales it instead (health x0.75 / 1 / 1.25 / 1.5, damage x0.8 / 1 / 1.15 / 1.3).
- Phases 40 / 35 / 25 (mini 55 / 45), the last phase firing 25 % faster; breakable parts about 35 % of the body on top; armour
  front 5 / side 3 / rear 2 on the ground main bosses (a mini's front at most 4), a hit on a ground boss's side or rear x1.5.
- New weapon sets for the twelve main bosses at the chapter's target damage a second (600 to 1,600) in the 45 / 25 / 20 / 10 mix,
  the secondary weapons opening in the second phase, a close-guard ring for six of them, targets chosen by crowd (area weapons)
  or worth (guns); the super weapons on a 45-50 s cycle with 3-4 s of warning; minis and the batch D bosses scaled to the
  chapter's target.
- Two-layer blasts for every boss weapon, big attack, salvo, pod and quake: the core at full damage, an edge twice as wide
  (20 m at most) at 40 %; both rings show on the blast, a small ring warns of a big boss shell for its last 0.8 s, and the Guide
  names the core and the edge.
- Written, not run: `Prompt26ABTests`; the tests whose numbers moved were updated.

## v0.33.0: Prompt 25 (the balance spreadsheet applied: data, weapons, sizes, rebuilt models, bosses and super weapons, names, unlocks, second rounds, 92 of 93 new items), play-tests 9-11

2026-10-01 · written for the next merge into main (the design review PDF is rebuilt once before it)

Main merges on feature/visual-overhaul since v0.32.0 (newest first): 4775606 batch D, eight new bosses as stand-in
variants; be53653 batch C, 14 missiles and bombs and 11 support cards; db4ab38 batch B, 32 low-priority units on stand-in
models; 91a513e and 7e6707e play-test 10 visuals and gear menu; 8df4f41 prompt 25 G, second rounds on 66 weapons;
f0f8b8c batch A, 27 new units and structures; 78650e4 and 0ab78a5 prompt 25 B2, the models rebuilt at the sheet's sizes;
bd04bd3 prompt 25 E2, E3, F1, documents and measures; 2a6d6b9 prompt 25 D1-D2, names, unlocks and economy; a122d90
prompt 25 C1-C2, boss numbers and super weapons; fc53b1c prompt 25 B1, B3, sizes and turn rates; fb9a496 prompt 25
A1-A5, the sheet's data and weapons; b0f2329 play-test 9 models. Direct commits: play-test 11's dark-hull fix (4337993,
b22d9d5, 5874c0f), the Windows build target, every campaign mission open while TestUnlockAll is on, dx23 dropped by the
owner (f2e02c9). Tests, sweeps and measures wait for the owner (every DECISIONS 25x section lists what to measure).
The design review PDF was rebuilt with 318 pages (the lost screenshots and render pages recovered from the 30/09 PDF into Docs/doc-images; new sections 10f second rounds, 10g bosses' core/edge blasts, phases and sizes, 10h Boss Hunt).

### New content, batch D: eight new bosses (prompt 25 F2, DECISIONS "25F2-D")

- Four main bosses (Kraken carrier, Monster 800 mm gun, Garuda bomber, Hyperion mirror station) and four mini bosses
  (Stymphalos UAV swarm, Nyx stealth destroyer, Cerberus convoy, Hydra drone submarine) as stand-ins: variants of the
  nearest existing boss with a tint, the sheet's health and size, and a super weapon for each main boss. In the Guide, the
  Boss Rush kinds and the Boss Hunts; real models come in prompts 26-27.

### Dark hulls fix (play-test 11, DECISIONS "PT11 dark hulls")

- The hull's own colour and its soot reach the shader as meant: the "_Tint" multiply was written with SetColor, which
  converts gamma to linear in this linear-space project, so the soot's 0.45 became 0.17 and a stand-in's 0.55 tint with
  it about 0.05 (black). Stand-ins also wear their colour from the first frame, as on their cards, not from the first hit.
- The real cause: any MaterialPropertyBlock drew a hull at about 40 % brightness, so a vehicle went dark at its first
  hit, and tinted stand-ins and boss variants were dark from the start. Hulls are now tinted through shared tinted
  materials, and a tint shifts the hue only, so a variant is as bright as its parent (as on the detail page). Stand-in
  cards re-rendered.

### Gear menu fix (play-test 10, DECISIONS "PT10 gear menu")

- Army > Equipment: a picked piece's card, names and buttons (equip, level up, merge) stay pinned at the top of the right
  panel; its long lines and the piece list scroll together under them. A long piece no longer pushes its equip button and
  the list off the panel, so equipping works again and the list scrolls by wheel, mouse drag and touch.
- New screenshot and layout-check screen `army-gear-picked` (the Equipment tab with a piece picked).
### PT10 visuals (play-test 10, DECISIONS PT10 visuals)

- The In action preview's targets no longer crackle white, spark blue and smoke while unharmed: a range dummy was drawn as
  knocked out by an EMP because the sim holds it still as "stunned". Only a real stun (an EMP, a SEAD strike) draws the
  arcs, sparks, burnt-electronics smoke and dead radar now; hit flashes, damage smoke and fire still follow real damage.
- Flak bursts redrawn after real flak: a sharp orange flash gone in a few frames, a dense round black-to-charcoal puff that
  blooms, hangs and drifts for 3-6 s, and a quick spark spray of fragments. No ring, no Small blast or grey puffs under
  it. Sized and weighted by calibre (a small grey tuft at 20 mm, a heavy black ball at 57 mm and over), never smaller than
  before; Low draws fewer puffs and sparks. Editor: Machine Brigade > Render Flak Burst Shots.

### New content, batch A (prompt 25 F2, DECISIONS 25F2-A)

- 27 new cards from the balance spreadsheet, each sold in the shop (1,500-5,000 coins) and fielded by the enemy too:
  - anti-air: heavy flak tower, 40 mm AA gun vehicle and tower, light SAM vehicle, anti-drone microwave vehicle,
    interceptor drone vehicle, laser anti-drone station;
  - anti-tank: anti-tank gun emplacement, beyond-sight and radar-guided ATGM vehicles, recoilless rifle jeep,
    fibre-optic FPV carrier (never jammed);
  - artillery and air: shoot-and-scoot wheeled howitzer, turreted SP mortar (four bombs landing at once), long-range
    glide bomber, high-speed recon jet (one pass), interceptor;
  - scouting and drops: radar scout car, airborne fighting vehicle (tap the card, then the ground to drop it by
    parachute where your side sees);
  - structures: gabion blast wall, inflatable decoy, fire-control centre, searchlight, barrage balloon, visual jammer,
    troop shelter, flare tower. Searchlights and flare towers work at night and in fog.
- The catalog loads again: an empty weapon family no longer stops it.

### New content, batch B (prompt 25 F2, DECISIONS 25F2-B)

- 32 more cards from the balance spreadsheet (the Thấp-priority items), each sold in the shop (1,500-5,000 coins) and
  fielded by the enemy too. The owner's choice for this batch: every card is complete (mechanics, AI, texts, unlock)
  but wears another unit's model with a colour wash, its own tint, so it reads apart in the shop; the real models
  come in a later prompt. Among them: a 57 mm AA vehicle, a mine-laying rocket truck, a light prop attack plane and
  a light attack helicopter, a next-generation tank (a double-charge active protection), a demolition-line vehicle,
  a drone-hijack vehicle, a MANPADS post, river patrol and gun boats, a coastal anti-ship vehicle, an auto-loading
  howitzer, an amphibious light vehicle, an airborne light tank (parachutes in like the airborne fighting vehicle), a
  stealth carrier strike jet, a twin-rotor gunship, a mobile repair vehicle, a towed anti-tank gun, a flare tower and
  a recoilless gun post at the small slot, a bigger bunker at the medium slot, a laser dazzler and a GPS jammer
  vehicle, a ground-launched cruise missile vehicle, an aerial tanker, a heavy-lift helicopter, a bridging vehicle, a
  drone net corridor, and a one-shot ATGM battery.
- `CardRenders.RenderBatch`: a non-boss unit with a tint now gets its own card picture (keyed by its own id) instead
  of sharing its borrowed model's, the same colour wash `VehicleView` already puts on a boss variant.

### Second rounds (prompt 25 G, DECISIONS 25G)

- 66 guns get a second round from the balance sheet's suggestions (`Tools/balance/import_alt_rounds.py`, balance.json
  `secondRounds`): air-burst rounds for the autocannons, armour-piercing rounds for the flak guns, high explosive for the tank
  guns, guided shells and API rounds for elites and rank-7 branches. The sheet's numbers, no rebalance.
- A gun loads the round that suits its target on its own: the change takes its reload (at least 0.5 s) and a round stays in
  at least 2 s. Deterministic, in the checkpoint fingerprint.
- Air-burst rounds fly a new flak round model and burst in a dark puff with a spark ring and fragment streaks, sized by
  calibre; the flak guns' own rounds look the same now.
- The ammo-switch icon marks a gun of two rounds on cards and weapon rows; a glyph flashes on a unit's bar when it changes
  round; the detail page lists both rounds with their figures and what each is for.

### New content, batch C: ordnance and support cards (prompt 25 F2, DECISIONS 25F2-C)

- 9 new weapons from the balance sheet's "Tên lửa & bom mới", each fitted to an existing unit as a secondary or extra
  weapon (no equipment-purchase system exists yet, so this stands in for it): a CBU-97-class cluster bomb, a GBU-28
  bunker buster and an ODAB-500 thermobaric bomb on the glide bomber; an AGM-88 HARM anti-radar missile on the
  interceptor; an APKWS laser-guided rocket on the attack helicopter; a second Coyote Block 2 interceptor round on the
  interceptor drone vehicle; an SMArt 155/BONUS top-attack shell on the wheeled howitzer; a Switchblade 300 mini swarm
  on the fibre-optic FPV carrier. An NSM/P-800 Oniks anti-ship missile is catalogued with no host (its coastal vehicle
  does not exist yet). 4 sheet rows (a glide bomb, an R-37M, a Spike NLOS and a 155 mm guided shell) duplicate weapons
  batch A and the second-rounds pass already built; the sheet's stealth cruise missile updates the existing
  `cruise_missile` support card's numbers instead of adding a new one.
- 11 new support cards from "Thẻ hỗ trợ mới", each sold in the shop (1,500-2,500 coins) and fielded by the enemy too: a
  stand-off glide bomb strike (can still be shot down), a no-scatter guided shell, a self-seeking cluster bomb and a
  drone-interceptor strike (one new mechanism, reused for both), a loitering attack UAV, an instant ammo resupply, a
  jamming storm (downs drones, hides the area), an illumination flare, a decoy paradrop (3 fake tanks that draw fire,
  never on the enemy), an instant counter-battery strike on enemy guns that just fired, and radar chaff (built on the
  smoke screen's own zone).
- The enemy AI can now draw any new-content support card into its quick-battle deck, as it already could for units.

### Measures and documents (prompt 25 E2, E3, F1, DECISIONS 25E)

- The combat-value tool measures what support vehicles do for their side (E2): health repaired, rounds resupplied,
  missiles decoyed and shield damage blocked, and a support value per CP on the combat value's scale. Table 9b has the
  columns, "—" until the test phase runs `CombatValueMeasure`.
- Table 9b has a "vs cluster" column (E3): damage a second against five light vehicles 4 m apart, computed from each
  weapon's blast radius, falloff, penetration and damage type (and cluster bomblets), with how many times one target's.
- The design document has a new section 8b (every unit's description, shape note and unlock) and 10e (every weapon's
  DPS against armour levels 0-5, aircraft and structures; missile flight speed and time; model and round sizes from the
  data; the main bosses' super weapons). `ExportGameDoc` writes the fields they read.
- `Docs/balance/apply-report.md` is finished: rows by task and by sheet for all 28 sheets, the combat value by role
  before and after ("to measure" until the test phase runs it) and the 33 places where the game differs from the
  spreadsheet, with the reason.
- `Docs/balance/Machine_Brigade_Can_bang_applied.xlsx`: the balance spreadsheet with a "Hiện tại" column beside each
  proposed value, filled with the game's numbers after prompt 25 (`Tools/balance/export_applied_xlsx.py`).

### Unlocks and economy from the balance spreadsheet (prompt 25 D2 and E.3, DECISIONS 25D2)

- Every vehicle opens where the spreadsheet's "Phương tiện" sheet says, and costs the sheet's price to unlock early:
  300 coins in act I, 800 in act II, 1,500 in act III, 2,500 in act IV (was 300 + 150 per CP). A new player starts
  with the scout jeep, armoured car, IFV and main battle tank. The light tank, AA vehicle and SP howitzer are won in
  chapters 1 and 2 now, and a save that has already played keeps them.
- The super-heavy tank, both bombers, the ballistic launcher and the AC-130 are no longer premium: they open in
  chapters 8 to 11. The turtle tank and the shield carrier open in interludes I and II. The minefield and the
  long-range SAM site, which nothing unlocked, open in chapters 1 and 8.
- Story loot (the railgun truck, the drone mothership, the bunker vehicle, the wingman drone and Kessler's cruise
  missiles) is never sold. The shop marks it as won in its mission.
- The economy was recomputed from the data (`Docs/balance/apply-report.md`, section D2). Buying every card early now
  costs 48,250 coins, 21 % of what the campaign pays (was 70,200). The campaign's blueprint pay dropped by a third, and
  the main deck is rank 7 as act IV begins.
- Each new item planned in the spreadsheet (93) has its shop price and source in `Docs/backlog/new_content.json`.
- The campaign was checked against the spreadsheet's story sheet. It found no data slip, and the differences are listed
  for the owner.

### Names from the balance spreadsheet (prompt 25 D1, DECISIONS 25D1)

- 63 units take the full name, short name and English name of the spreadsheet's "Tên đề xuất" sheet: for example
  "Pháo hạm bay" / "Airborne gunship" (was "Pháo hạm AC-130"), "Xe phóng đạn lảng vảng" / "Loitering munition truck"
  (was "Xe phóng Lancet"), "Trạm tên lửa phòng không tầm xa" / "Long-range SAM site" (was "Tên lửa Patriot tầm xa"),
  "Siêu tăng" / "Super-heavy tank" (was "Siêu tăng Titan"), "Lựu pháo tự hành" / "SP howitzer".
- The real model a card was named after (AC-130, Patriot, Lancet, Shahed, ZU-23, BMPT Terminator, Iron Beam, TOS-1A) is
  now on the unit's reference line in the Guide tab, not in its name.
- Each unit has one name everywhere: its guide opens with it, and the guides, tips, missions and loot lines that used an
  old name use the new one.
- `Tools/balance/import_names.py` applies the sheet; `NameSheetTests` checks that no old name is left.
### Prompt 25 A1-A5

The owner's balance spreadsheet (`Docs/balance/Machine_Brigade_Can_bang.xlsx`) goes into the game data by script
(`Tools/balance/import_xlsx.py`); what was applied and what waits for a later task is in
`Docs/balance/apply-report.md` (DECISIONS 25A).

- A1 Cao: new prices (attack helicopter 9, attack jet 18, heavy tank 13, Iron Beam 6, long-range SAM 14, SAM launcher
  7, scout helicopter 5, stealth fighter 13, strike drone 9, swarm carrier 13, super-heavy tank 18); SAMs and
  air-to-air missiles fast enough to catch a fighter; the swarm carrier drops cruise missiles instead of small bombs;
  the scout jeep sees farther (55 m) and hides when it stands; the wheeled gun has less health and reloads like a
  tank; the ZU-23 fires a stream of lighter rounds farther; the self-propelled gun fires faster.
- A1 Trung: armour by face for a dozen vehicles (the main battle tank's front 4, the tank destroyer, siege mortar and
  laser tank lighter); tank turrets turn faster than their hulls; the IFV and the BMPT fire their 30 mm in bursts;
  the HIMARS moves after every salvo; the heavy turret loads armour-piercing rounds for armour; the gunship carries
  Ataka missiles and flies faster; the heavy bomber carries seven FAB-500s; the Phalanx fires a real stream.
- A1 Thấp: death blasts sized by the vehicle (the ammunition depot 14 m, the flame tank 5 m); mini bosses' front armour
  4 at most; the light tank fires its 57 mm in pairs and sees farther; the Grad turret hits harder; the Pantsir's
  guns and the gunboat's AK-630 fire long streams; the railgun truck, the Smerch and the TOS cost a CP more.
- A2: every weapon's rate, magazine or burst, rest, reach, speed and blast from the weapon sheet (sustained DPS within
  5 % of the sheet's, tested); the HIMARS, Iskander, Smerch and Buk launchers lose their machine guns; the wheeled gun
  gains a roof M2, the light tank a gun-launched missile, the Pantsir its own 57E6 missiles.
- A3: weapon families: every weapon that is the same real weapon (all Hellfires, all M2s, all Grads...) shares one
  speed, blast radius, round model and look, set once in the data (`weaponFamilies`).
- A4: every missile flies the sheet's speed (SAMs and air-to-air missiles 42-65 m/s, faster than the aircraft they
  hunt; cruise missiles and Shaheds kept slow on purpose).
- A5: one blast radius for one round on every carrier (the siege tank's 203 mm 8 m, the Grad 4.5 m everywhere), and every
  blast drawn exactly as wide as its damage reaches: its shock ring sits on the radius (bombs' rings were twice it);
  small flak and grenade bursts show a faint ring of their own.
- B.7-B.8: prices checked against the price sheets; the airstrike drops four FAB-500s (10 m each), the barrage fires six
  shells, the cruise missile hits for 600 over 10 m.

### Prompt 25 A1 review

The rows the first pass kept for a measurement, applied as the sheet has them (the owner's call; DECISIONS 25A,
`import_xlsx.py --upto A1-review`).

- Nine speeds by the sheet's real speed x the map factor (the engineer vehicle 4.4 m/s, the smoke carrier and the
  mortar carrier 5.9, the mine layer 5.5, the VBIED 6.7, the light tank 4.0, the flame tank 4.6, the HIMARS 9.4,
  the strike drone 13.9); the siege tank sees 30 m.
- Health by the sheet's class median a CP: the TOS 450, the siege tank 600, the swarm carrier 632, the AC-130 1,069
  (about half).
- The Skyranger's AHEAD gun changes magazines in 1.21 s (the sheet's formula, 102 a second sustained).

### Prompt 25 B1, B3 and turn rates

The spreadsheet's sizes (DECISIONS 25B; `import_xlsx.py --upto B1`, `--upto B3`).

- B1: every vehicle's drawn size is in the data (`modelSize`) and the game fits its model to it, so the models B2
  rebuilt (the main battle tank 7.8 m, the twin tank 9.0 m, the flame tank, the armoured car, the scout jeep, the FPV
  and Lancet trucks, the command vehicle, the Su-27 8.6 m, the Apache, the swarm carrier and the AC-130 on one C-130
  frame) and the old ones are drawn at the sheet's sizes, their hulls (collision) with them; the super tank 10.6 m,
  the Pantsir 9.6 m, the supply truck 8.2 m, the self-propelled gun, the siege tank, the Iron Beam, the radar and
  Shahed trucks resized; Daedalus ~45 m, and Icarus 60 m, now the largest thing in the sky.
- B3: rounds at the sheet's lengths (0.8 x real from the ground, 0.5 x from the air, 0.8 m at least): bombs, the
  JASSM, the Kornet and the 240 mm mortar smaller, the Buk, Patriot and 48N6 bigger; 155 mm shells 0.8 m and every
  203 mm 1.3 x that; the Kh-29L and the GBU-39 get models of their own (the Maverick and the GBU-12 stand in until
  they are built).
- C.4: the design document's turn rates in degrees a second (it printed the code's radians under a degrees label);
  the tanks' turrets turn faster than their hulls (115 deg/s, from A1).
### Prompt 25 C1: bosses and super weapons (DECISIONS 25C)

The sheet "Boss đề xuất" by script (`import_xlsx.py --upto C1`).

- Every boss's health from the sheet: Icarus 26,000 (the most of any boss), Daedalus 24,000, Roc 23,000 ... Bastion
  12,000; mini bosses 6,000-13,000 (Scylla and Bastion Mk.0 about half what they had).
- Every boss's ordinary fire comes to the sheet's damage a second against armour 3 (a boss's own `weaponDamage`, on the
  ground only), after the new weapons: the Behemoth's twin Kornet, Jötunn's anti-drone 30 mm, Roc's two twin 30 mm,
  Moloch's two ZU-23, Bastion's two NSV, Kronos's and Daedalus's two 57 mm, Leviathan's SAM, the mothership's third
  Lancet bay; Icarus trades its tank guns and flak for two coilguns (four ordinary turrets on its wreck); Scylla fires
  a twin AK-130 and an anti-ship missile every 15 s instead of a battleship's 460 mm; Typhon a short-range cruise
  missile every 12 s; Caspian an anti-ship missile each pass and two ZU-23; Ixion and the Harpy 12.7 mm guns.
- Only the twelve main bosses have a super weapon, with the sheet's numbers, cycle, warning and counter: the Behemoth's
  six shells in six rings, Jötunn's 203 mm barrage, the mothership's heavy glide bomb (it can be shot down), Nemesis's
  Doomsday missile on a 6 s clock, Icarus's seven rods (nine in phase 3), Bastion's single 420 mm bomb, Roc's sixteen
  bombs, Leviathan's nine shells along a strip, Daedalus's eight pods; each with a warning sound of its own. Mini
  bosses fight with their ordinary weapons only.

### Prompt 25 C2: the Gungnir's gun and the Kronos's bucket wheel as weapons (DECISIONS 25C)

- The Gungnir's 80 cm gun is its main weapon, in the weapons tables and the Guide: one 900 shell every 25 s with a 12 m
  blast (was 1,400 every 20 s), still at your biggest group anywhere; its shot fires the gun's numbers.
- The Kronos's bucket wheel is a weapon on its wheel (900 a second within 6 m, three times on walls and towers); its
  crusher takes the weapon's numbers.

### Prompt 25 B2: models rebuilt to the balance sheet (DECISIONS 25B2)

- Thirteen models are redrawn from the balance sheet's shape notes and drawing guide, at its sizes (ground vehicles
  0.8 x real, aircraft 0.4 x real): the main battle tank (a 7.7 m Leopard 2 / Abrams-class tank with its long gun), the
  Su-27 fighter (now clearly longer than the attack jet), the drone mothership and the AC-130 (one C-130 airframe at
  one size; the mothership drops its drones from an open ramp), the Apache (with wheels, not skids, and longer stub
  wings), Daedalus (a two-tier Acclamator-style assault ship with bigger point-defence turrets), the scout jeep (the
  smallest vehicle, with its driver and gunner), the twin-gun tank (the MBT 15 % larger with two parallel guns), the
  flame tank (a TO-55 with red fuel tanks on the back), the armoured car (a Pandur 6x6), the FPV and Lancet launchers
  (one MRAP) and the command vehicle (a Stryker with its mast folded and no tall whips).
- Each is inside the sheet's triangle budget (most were two to three times over) and keeps every weapon and part
  point, so shots, bosses' parts and the high-detail variants work as before. Their cards are re-rendered, and
  before/after shots are in `Docs/ui-screens/models/`.
- The new sizes take effect in battle when prompt 25 B1 sets the scales; Icarus is unchanged (its size is a scale
  for B1). The models not reached yet are listed in `Docs/ASSET_DEBT.md`.
- Part 2: every other vehicle is redrawn the same way, in lean builders at the sheet's sizes: the trucks the sheet
  sized (supply truck and ammunition carrier on a HEMTT, counter-battery radar, Shahed launcher, Iron Beam, Pantsir),
  the M109A7 self-propelled gun (was a CAESAR truck), the siege tank on 2S4 lines, the Buk and S-400 launchers with
  missiles at their new lengths, the four-track super tank, the IFV, light tank and Gepard, the hovercraft, engineer,
  smoke and mortar carriers, the three pickups, jammer, minelayer, HIMARS, Centauro, shield carrier, turtle tank,
  bulldozer, Sprut, TOS-1A, BMPT, heavy tank, Smerch, Iskander, railgun and laser tanks, the bunker vehicle, and the
  aircraft (Little Bird, TB2, XQ-58, MQ-9, the stealth jet resized, Hind, Su-25, B-52, B-2, the airdrop plane on the
  shared C-130). The seven elites with models of their own follow their new bases; the Sky Fortress is the shared
  C-130 painted dark; the Kh-29L and GBU-39 get round models; the logistics yard, repair bay, radar site and the
  airfield's two branches get models of their own. Most are 1,000-3,500 triangles (were 6,000-15,000). The towers
  and the other bosses were checked against the sheet and kept for prompt 27's new kit.

### Play-test 9 models (DECISIONS 23M)

- Icarus is a spaceship again, not a station: a dagger-shaped warship about as big as before on the map, with a pointed
  bow, a lit trench along each side, a keel under the bow that carries the laser ball, two long pods on its flanks
  with the coilguns and the crash turrets, a stepped superstructure, a command tower aft with a wide bridge, a bank of
  seven engines across the stern and two engine nacelles with canted fins. It borrows from Star Wars, Halo, The
  Expanse, Battlestar Galactica and Mass Effect without copying any one ship. Its wreck is the same ship crashed, with
  the tower snapped and the bridge lying beside it. Its parts, weapons and attacks are unchanged, and so is the
  prototype variant (Icarus Mk.0).
- The stealth jet is redrawn slim, half as deep as before. Seen from above it is one flat, blended shape: sharp chines
  run from the nose and flare into the wing roots, then the body tapers to the tail. It has a wide trapezoid wing, twin
  tails canted out, flat thrust-vectoring nozzles and a one-piece canopy (F-22, J-20, YF-23, Su-57 and F-35 mixed). It
  is all dark gunmetal, with your side's colour only on the tail tips, the wingtips and a panel by the canopy. Same
  size class, same weapons and bays.
- Both cards are re-rendered from the new models.

## v0.32.0: Doctrines folded into the commanders, the owner's answer on the bombs

2026-09-30 · merged into main

Main merges on feature/visual-overhaul since v0.31.0 (newest first): 2c387bb design review PDF after the fold; fd55169 the
doctrines folded into the commanders (one choice before a battle, bought doctrines refunded, DECISIONS 23D); 3043b0c the owner
keeps the bombs' fall and the heavy bomber's gap.


### Doctrines folded into commanders (DECISIONS 23D)

- The commander is now the only choice before a battle. The doctrine picker on the deck page and the doctrine tiles in
  the shop are gone, and neither your side nor the enemy takes a doctrine any more.
- Each doctrine's edge is now part of the commander whose style it suited. Where that commander already had the same
  bonus, the two are one number, not added:
  - Crown: tanks, heavy vehicles and vehicles of 9 CP or more +20 % health (was +15 % on the dear ones only); +15 %
    damage on the dear ones as before.
  - Hawk: aircraft also +20 % health, and fire support recharges 15 % faster.
  - Longshot: artillery also +25 % health, and fire support recharges 25 % faster.
  - Rush: vehicles +15 % speed (was +10 %); scouts and light vehicles +15 % health.
  - Ledger: all income +15 % (was +10 %) and supply +10 %.
- Old saves: every doctrine you bought is refunded, 1,500 coins each, once, and the menu tells you how much came back.
  The free Armoured fist refunds nothing.
- The design review PDF no longer lists a doctrine price; its commander section shows the new numbers.

## v0.31.0: Prompt 23 (mission events and in-battle text dialogue) and the 264-page design review

2026-09-30 · merged into main

Main merges on feature/visual-overhaul since v0.30.0 (newest first): the design review PDF (264 pages, new 7c on events and
dialogue); f585c2b prompt 23 E (events in all 193 missions); 0117138 the event HUD adapter; df75776 prompt 23 F (arrows, side
objectives, Accord mark, general labels); 6511dc2 prompt 23 A-D (event library, spawn points, reinforcements, event groups);
c19fbc0 prompt 23 H (text dialogue, compact notices). Balance of the events (5-seed campaign runs, FPS) waits for the testing
phase; DECISIONS 23A and 23E list what it must measure.


### Prompt 23 F: event HUD markers (DECISIONS 23F)

- Reinforcements show where they come from for as long as their warning runs: an arrow at that side of the minimap and a
  small round indicator at the screen's edge pointing towards them (red: the enemy's; sky blue: the Meridian Accord's),
  up to four at once, kept clear of the notices, the dialogue line and the card tray.
- The Accord's reinforcements (and the other allied-AI units) read apart from the player's own: a sky-blue health bar
  with the Accord's sign beside it (teal for colour-blind players), sky-blue ringed blips on the minimap; the player
  cannot select them.
- An enemy general's vehicle on the field has a small name label (VARGA, KESSLER...) above it, with a small speaking mark
  while that general's line is on show. No speech bubbles.
- A side objective has its own row on the mission bar (what to do, 2/5, a clock that turns red in the last ten seconds)
  and a short notice when it starts, is completed or fails.
### Prompt 23 E: events in the campaign (DECISIONS 23E)

- Every campaign mission now plays mission events, side missions included (534 in all): 2-4 in a mission, 5-8 in a
  chapter's operation, 2-3 in an interlude. Each chapter has its own:
  - Chapters 1-4: landing craft striking back from the sea and the Accord's second landing wave; oil convoys and
    Thorne's first support; Orlov's massed guns and snowstorms; landing ships, Kessler's trains and the families' ferries.
  - Chapters 5-8: drone swarms and Venn's electronic storms; counterattacks from every side, Brandt's lines of towers and
    the Hollow Dam's ceasefire; Veyra's militia and Thorne's turned columns; Tartarus surfacing and the held miners.
  - Chapters 9-12: landings and sea fog; Raven's raids again and again, Hawk's strikes and nightfall; drop pods and the
    satellite's test rod; reinforcements from every side and the Total Offensive.
  - Interlude II: Locust's hunting packs. Interlude III: Morrigan hunting Hawk.
- The Hollow Dam's ceasefire: Varga's column holds its fire until noon and nothing of ours shoots it unless ordered to.
  Whoever fires first loses the reward.
- Chapter 12's Total Offensive: Brandt's armour, Venn's drones, Hawk's air wing and Mara's Behemoth come in at once, as
  strong as the enemy's wave from every side.
- The satellite's test rod follows the big-attack rules at a small size: a warning, a ring on the ground, a kinetic hit
  from above.
- The ferries and the held miners come in the option of their chapter's story choice that has them.
- Every chapter with an enemy general has the general take the field in one of its missions (Brandt in chapter 1, Thorne
  when he turns in Veyra, Raven in Morrigan in interlude III).
- No two missions in a row play the same events. The campaign build checks this, the counts and each chapter's set pieces.
- Six story moments slow the battle while their lines play: Varga's word at the Hollow Dam, Venn losing her swarm,
  Thorne's betrayal, Thorne on Typhon's bridge, Varga's fall and Icarus falling.
- An intercepted convoy of files now recovers one of the dossier's intel files, won or lost; the result card lists it.

### Prompt 23 H: in-battle dialogue (DECISIONS 23H)

- Every line a character says in battle is now one subtitle just above the card tray: the speaker's short name in bold
  (ours light blue, the enemy's darker red), then the words, on a dim strip that hugs the text, at most half the screen
  wide and two lines. The radio panel with its portrait and frame is gone.
- One line at a time: story lines and warnings wait their turn (a warning cuts chatter short), other lines show only
  when the strip is free and at least 9 s after the last (20 s for a general's reactions in a boss battle). A line stays
  3-6 s by its length and fades; nothing waits for a tap.
- Pause has a Dialogue log with the battle's last 20 lines. Settings, Game: In-battle dialogue (Full, Important only,
  Off); story lines always show.
- Story moments slow the battle to half speed while their lines play (the betrayal today; replays are unaffected).
- Notices at the top edge have an icon by kind (a point, an air raid, a strike, a boss, an elite, the weather...) and
  queue one after another; an elite's arrival has a short notice of its own.
- Twenty lines that ran past two lines at Large text were shortened.
### Prompt 23 A-D: mission events, spawn points, reinforcements and the event groups (DECISIONS 23A)

- Mission events are data: a library in campaign.json (`eventLibrary`, built from `Tools/campaign/events.py`) with 18
  kinds. Each event has a trigger (a time, the mission's progress, the boss's health, the units on the field, another
  event, the player being outnumbered), a warning, lines and a reward. Missions list theirs in `missionEvents`; part E
  fills the campaign. Events follow the battle's seed and are part of its fingerprint, so a checkpoint's replay brings
  them back.
- Every battlefield has spawn points, worked out from the map. The enemy gets its edges in every direction, rail heads,
  water landings, landing zones and transport drop points; the allies get the area behind the player, the drop zone and
  the outposts. Nothing spawns within 45 m of the player's units: another point in the same direction is used instead.
  Prompt 12's stuck probe from every point on all 72 battlefields found nothing stuck.
- Reinforcements:
  - Enemy waves come from 1-4 directions by difficulty, warned 15/10/8/6 s ahead. The mission's general decides what
    comes: Varga's tanks, Orlov's guns, Kessler's landings and trains, Venn's drones, Wolff's aircraft, Thorne's turned
    columns, Aurel's drop pods.
  - Meridian Accord waves come under the allied AI, worth 70/50/30/15 % of an enemy wave's combat value by difficulty.
    They replace the losing side's free drop and never come on top of it.
  - Reinforcements have their own cap, outside the army cap.
- The event groups:
  - fire support: enemy barrages, air raids and counter-battery fire; Hawk's air strikes and Accord artillery;
  - the enemy general on the field, in an elite or their own mini boss and with their passive, breaking off at 30 %
    unless it is their last battle;
  - timed side objectives: intercept, rescue, protect;
  - economy: a neutral supply convoy, loot crates, raids on the player's supplies;
  - logistics and intelligence: supply drops, Nadia's reports, and the EW blackout with its countdown (radar and
    minimap dark);
  - a mid-battle mini boss, and Kade's change of plan;
  - the weather or night turning over 20-30 s, with sight following it.
- Every notice and line has English and Vietnamese text (`EventText`). Lines go to the in-battle dialogue with their
  priority.

## v0.30.0: Prompts 19-22 (the Silver Bug as an orbital spacecraft; twelve chapters in four acts, boss templates, Boss Hunt; the Sandbox and bilingual text; the story rewrite, Commanders, narrative mechanics, new maps and bosses), play-tests 4-8, the boss and mode balance, and the 261-page design review

2026-09-30 · merged into main

Main merges on feature/visual-overhaul since v0.29.0 (newest first): 21c00bf design review PDF (261 pages: rates, reloads and
ballistics, sizes, blast radii, reach, boss health and DPS, prices, commanders, a reference for every unit); 393cb34 play-test 8 B;
be456db play-test 8 A; 4f10422 prompt 22 D; 7904d73 prompt 22 F; 2f45a5d boss and mode balance; e5ad3c7 prompt 22 E; prompt 22
pass 1, play-tests 4-7, prompts 19-21 and the balance passes below.


### Play-test 8 B (DECISIONS 22R)

- Burning vehicles burn in three stages (catching, burning, ablaze): broad flames over the engine deck with taller
  tongues out of them, yellow-white at the base and red at the tips, a white-hot root, licks breaking off, embers and
  sparks, dark smoke lit brown just above the fire, and a flickering orange light on the hull and the ground round it.
  A vehicle on the move trails one plume of smoke instead of a row of puffs.
- Blast smoke clears about 40 % sooner (the heavy fortress's shells, a boss's death blast and every weapon that uses
  the same smoke); the fire and the blast itself are as before.
- AC-130: its guns stick out about as far as a real AC-130U's, and it no longer carries Griffin missiles.
- Icarus is redrawn as an orbital weapons platform: a white-and-gold station with a telescope nose, two blue solar
  wings on a truss, white radiators and a big drive bell. Its parts, weapons and attacks are unchanged.

### Prompt 22 D: narrative mechanics (DECISIONS 22D)

- The chapter screen opens on a map of the Meridian Coast: the brigade's ground, Hegemon's and (from Veyra) Thorne's,
  the front line moving with every win, flags on the bases taken, a pin per chapter that opens it. Varga's
  counterstrike takes ground back in chapter 6; Thorne's betrayal turns Red Rock, Hollow Dam, Iron Harbor and Beacon Bay
  until chapters 8-9 win them back.
- Three story choices (after 4-13, 8-11 and 11-10): chase Kessler or save the ferries, free the miners (+6 CP in
  chapter 9) or strike Kronos (double coins), blind the Skygate radar (the enemy sees 25% less in chapter 12) or take the
  short road (coins and rare blueprints). Each leads to its own mission, then the story goes on; kept in the save and
  listed in the dossier.
- Story loot: the railgun truck after Tempest (chapter 4), the drone mothership with Venn (5), the bunker vehicle from
  Moloch (6), the loyal wingman from Roc (10), Kessler's cruise missiles (12), each with a line saying why.
- 33 intel files from side missions and three-star wins (letters, Aurel's reports, Mara's diary, Venn's notes, the
  clues about Thorne in chapters 4-6) in the dossier's new Intel tab; comic panels after every chapter and interlude,
  skippable and replayable; the characters' arcs in the dossier; every enemy general answers on the radio to a fast win,
  heavy losses, lots of aircraft, drones or artillery, and a big attack broken.
### Play-test 8 A (DECISIONS 22Q)

- Units and towers look for a better target every half second: an anti-air gun firing at a tank turns on a helicopter
  that comes in. Each weapon goes for what it hurts most and what threatens it, without flicking between two equal
  targets. The AI's own attack orders give way to an aircraft overhead; the player's orders never do.
- The SAM launcher fires again in its In action clip.
- The siege tank's sieged mortar blast is 20 % smaller. The long-range SAM's blast is twice as wide and drawn twice as big.
- The fire support's gunship flies off the map when its time is up instead of vanishing.
- The vehicle details page frames every model by its size, so the Leviathan fits.
- Armour by face draws each unit's own outline: ships, aircraft, helicopters, turretless vehicles, structures and tanks.
- Sandbox: a test range with sea for ships and naval bosses. Buttons on the unit card no longer miss taps.
- Base screen: each tower's range is a coloured border over a clear fill, and the picked tower's range pulses.
- Bombs fall: a bomber drops its stick bomb after bomb along its path and lets go so the stick straddles the target.
  Unguided bombs land where their drop and fall put them, not on a target that drives away. Guided bombs glide onto
  their target.

### Play-test 7 (DECISIONS 22P)

- The AC-130 is an aircraft card again, "AC-130 Gunship" ("Pháo hạm AC-130"), listed with the aircraft (premium,
  4,500 coins, 22 CP). It circles what it is sent at with its 105, 40 and 25 mm firing from the left. The Gunship
  support card is gone: a bought one becomes the AC-130 card. The one-use Gunship item stays.
- Every weapon of a vehicle, tower or boss fires on its own timing; twin barrels open fire a tenth of a second apart.
- The heavy gunship's and attack jet's missiles and rockets fly 30 % slower, and so do the drone mothership's drones.
- Siege tank: the twin 105 mm pulls right into the turret when it sieges and comes back out when it packs up. The roof
  machine gun sits clear of the siege cannon.
- Artillery, launchers, SAM and support vehicles carry a short self-defence machine gun (15-21 m instead of 30).
- Towers have no extra weapons in the data or on their models. The steel fortress keeps its two MG turrets, the MG
  bunker its machine gun, the guard tower its own gun.
### Prompt 22 pass 1: names, structure, story

- Every proper name is the spec's, the same in both languages (A): the Meridian Coast, the Meridian Accord and its
  7th Mechanized Brigade ("Machine Brigade"), Veyra; Colonel Marcus Kade "Iron", Engineer Mara Lind, Lieutenant Jonah
  Reyes "Hawk", Captain Nadia Kerr, General Roland Thorne "Titan", Dr Elara Venn "Queen", Kasimir Wolff "Raven" (no more
  "Quạ Đen"); the maps (Stormbeach, Hollow Dam, Beacon Bay, Deepcut Mine, Skygate Array, Helion Launch Complex...), the
  chapters and acts. The ids stay; the tokens of prompt 21 read the new names. A scan test covers every table.
- Twelve chapters of 9 to 18 main missions and three interludes (B): 168 main and 19 side missions (was 121 and 24),
  44 new ones (and four that moved) made from the battlefields' existing missions with their set-up changed (prompt 4's rule, no two in a row
  alike). Each chapter ends on its operation with its main boss: Red Rock's Behemoth (new), Leviathan (now an operation),
  Nemesis at the end of Veyra's liberation. An interlude goes with the act before it for the act switches; on the
  screens "Interlude II", its missions "II-3". Saves of the twelve chapters of ten move on (campaign version 4).
- The story (C): the setting, the people and their motives, the flash-forward to Helion before the first mission, every
  beat of C.4 in its mission (Brandt's surrender, Thorne's first battle with us and three clues before he turns in
  Veyra, Mara's past and the Foundry, the ceasefire at the Hollow Dam, Venn's escort, Hawk's rescue and duel, Aurel's
  first words in chapter 11, Varga's end, "They still don't understand."), the ending, and the hooks for later content
  in `Docs/STORY.md`. Short radio lines (100 characters at most) in both languages, each character in his or her own
  voice; eight new officers speak with portraits of their own.
- Waiting on P22-content: the Foundry and the Veyra Old Quarter (their missions say "Battlefield in the next update"
  until the maps come), Behemoth Mk.0 and Morrigan (fought as the Behemoth and Spectre until then), Mara's Behemoth in
  the last battle.

### Prompt 22 E: new maps and bosses

- Two battlefields: Foundry (Hegemon's old tank works: solid blocks of sheds cut by narrow 10 m factory lanes, a walled
  casting hall and two walled yards) and Veyra Old Quarter (the capital's old town: bending narrow streets, the
  cathedral, market and clock squares). Conquest, Survival, Siege and long versions, labelled hardpoints, map
  pictures, Guide entries, the skirmish list; both pass the access check and the stuck probe.
- Behemoth Mk.0 · Prototype Behemoth (Varga): a mini boss made from the Behemoth's data alone (main gun, flank guns,
  rocket pod; no flak, no protection system).
- Morrigan · Raven's Fighter (Wolff): a new stealth-fighter model and mini boss; its salvo sends homing missiles at your
  aircraft and guided bombs at your anti-air (break its bays in the warning to stop it). A duel mode for a mission
  where you fly aircraft only: no escorts, and it goes dark now and then.
- Mara's Behemoth: an allied Behemoth for the campaign's last battle, never a card.
- Both new mini bosses are in the Boss Hunt and the full Boss Hunt.
### Prompt 22 F: Commanders

- Pick one of 14 commanders before a battle, beside the deck: one passive strength and one small weakness, on for the whole battle; no active skill, gauge or levels. They open with the story; a locked one says where.
- The eight enemy generals play by the same rules: a mission tied to a general carries their passive, and its briefing shows their strength and weakness.
- A commander's unit bonuses count towards the loadout's stat caps like equipment, and towards the army strength the campaign's enemies keep pace with.
- Every mode takes the player's commander; a story mission may set its own (chapter 10's duel is Hawk's); in the Sandbox each side picks one.
- Screens: the picker, a commander row on the deck screen and the briefing, a small face beside pause (tap for the strength and weakness), a radio line at the start and on the result, a Commanders tab in the dossier. New portraits are placeholders.
- Auto-buy and Support favour the cards and strikes that suit the commander; an enemy general's army favours what suits its passive.
- Balance: every commander against every deck style (DECISIONS 22F).

### Play-test 6 bugs (DECISIONS 21B)

- Start on a campaign mission works again after a Back: Back no longer takes the hidden story card out of the menu
  (it closes the topmost open dialog, and hides the story card). This was why mission 1-1's Start did nothing.
- A boss's page is its boss file: no Equipment tab, no level, gear or next-level numbers, no deck or upgrade buttons;
  its numbers, armour, parts with their armour and health, big attack, escorts and general. The campaign's mission
  page links to each boss it fights, and the Sandbox shows the same file in a dialog.
- The gunship realism test samples the orbit from its arrival (the AC-130 now kills its heavy tank in 12 s).
- `MenuWalk`: a Play-mode walk through the real menu to a campaign battle.
### Sandbox screen, lean (DECISIONS 21S)

- The Sandbox keeps the battlefield: at rest only a slim icon rail under the minimap and one thin bar along the bottom (run, pause, one tick, speed, seed, reset, overlays). At 16:9 they cover about 6% of the screen, against three standing panels before.
- The unit picker opens from the rail as an icon grid with a category, a search chip and filters; a selected unit's settings are a small card on the right; overlays are a tray of small toggles; settings, scenarios, duel, A/B, statistics and both sides open one sheet at a time.
- The battle HUD in the Sandbox drops the wave counts, the commander's switches, select-all, box select and the hint.
- Before and after shots in `Docs/art/sandbox/`.
### Boss and mode balance

- Bosses are much tougher: health x1.5-2.6 for main bosses and x1.8-3 for mini bosses, the heaviest with the new
  armour level 5 on their front (a battle tank's round is one level under it: flank them or strike the roof). They hit
  40-50 % harder from every source (their big attacks 20 %), reload a quarter faster and their air defence hits aircraft
  60 % harder. Four tanks in a column no longer beat a boss without losses (DECISIONS 21G).
- One bomber's load or one barrage no longer wipes a boss: bosses take half of strikes and bombs, and at most 10 % of
  their health (mini bosses 15 %) to them in any 10 s.
- Escorts are vehicles, never towers; every arrival wave has one more, with air cover where it had none, and more are
  alive at once (Normal 5 to 7). Tempest keeps its coilguns, Atlas has a guard when it arrives.
- Armour level 5 ("Super-heavy armour") has its icons, name and a column in every effect table and the Guide legend.
- Economy a little leaner: income -5 % everywhere; Boss Rush income 2 to 1.8 CP/s and health-step bounties 8 to 6 CP.
- The quick modes' enemies keep pace with your card ranks and equipment by difficulty, as the campaign's do, so a
  geared army no longer wins every difficulty.
- Boss Rush and the Boss Hunts: every boss can come, the trains (Nemesis, Juggernaut) and Gungnir too, on their own
  battlefields' lines; each week's hunt has bosses with air defence; after the last boss, "Endless" brings the bosses
  again, each stronger with more escorts, until your army falls (the win is kept, every boss pays).
- Your army's vehicles no longer stand idle for long while the fight goes on: an idle vehicle goes for the enemy after
  12 s, and reinforcements go forward in twos.
- The attack helicopter opens with missiles from its standoff, then comes in to use its cannon and rockets where no
  air defence covers.
- Icarus comes down from orbit at once (it spent 15 s off the top of the screen).

### Play-test 6: UI, camera, audio

- The Gunship is a deck card: the AC-130 on call for 12 CP, circling its mark for 20 s with its 105, 40 and 25 mm
  guns (120 s cooldown), with the AC-130's picture on its card. Sold in the shop for 4,500 coins like the heavy
  bomber (unlocked in test builds); the one-use Gunship item stays. The Mi-24 now reads "Heavy gunship" on its
  cards, so only the AC-130 reads Gunship (DECISIONS 21E).
- Deck: a tap on a card in the deck strip takes it out (the strip's cards carry a remove mark); cards in the deck
  have a thick accent outline, an accent name and a check on their picture.
- Battle camera: zoom buttons in the compact HUD beside select-all and box-select; a close mark over the
  selection panel's corner, and a tap on a selected unit, let the selection go; one mouse-wheel notch now zooms 15 % (it
  zoomed 0.1 %); a boss's entrance, phase change and fall keep the player's zoom and ease back to where the view
  was, and a pan or zoom during the shot hands the view back at once.
- Boss HUD (compact): the boss bar shares the top row with the goal or the bosses destroyed count, one line of call
  sign and phase over the bar, with smaller part icons; a tap still opens it at full size.
- Field tower: it lands on open ground near the mark, clear of houses, vehicles and towers, and its parachute
  canopy rides over the tower's top instead of through its middle.
- Sound: rain and wind well under the music (rain 0.15-0.18, from 0.35-0.5), softer thunder; the music ducks only
  under alerts (a boss's big attack, a fortress's alarm) for a moment.
### Play-test 6: effects and models

- The siege tank is redrawn after StarCraft 2's: a low, wide hull between four armoured track pods and a broad
  turret with twin 105 mm guns; sieging, four hydraulic legs swing out and brace, the rams lift the hull, the turret
  swings round, and the big 240 mm siege cannon runs out, locks and is laid (the 2.5 s timing is kept).
- Launchers raise their launcher to fire and lower it after, like the real systems: MLRS, Grad, Smerch and TOS lay
  their tubes, the Buk its rails, the S-300 stands its canisters upright, the Iskander erects its missiles, the
  Patriot raises its box, the Shahed and Lancet trucks their launchers, and the IFVs lift their ATGM box.
- The SEAD strike's anti-radiation missile is big and bright and dives on to the air defence it locked; its hit is
  an electronic kill (a blue-white flash, shock rings, arcing, sparks), and the air defence is visibly knocked out
  for its 8 s (arcs, sparks, smoke, its radar dead and slumped). EMP-stunned vehicles show it too.
- The gun turret's blasts are 20 % bigger; the heavy fortress's 20 % smaller.
- Aircraft are drawn 15 % smaller, every type alike.
- Burning vehicles and bosses burn like vehicles: flames licking out of the engine deck, the hatch and a breach,
  fixed to the hull and moving with it, a glow on the metal, sparks and flare-ups, and dark smoke that trails behind
  a vehicle on the move. Low graphics burn on fewer sources.
### Play-test 6: combat

- Dogfights end with one jet on the other's tail: the one worse placed out of the merge runs out, jinking, and the
  other sits behind it streaming its cannon; a jet under 30 % health breaks off and flies away (DECISIONS 21F).
- A fighter hangs on a helicopter with its cannon until it dies instead of breaking away every 4 s.
- The attack jet streams a whole magazine through each attack hold instead of circling with its cannon quiet.
- Missiles and rockets no longer jump in busy fights (the view's pool grows instead of reusing a round in flight);
  the attack jet's, rocket technical's, scout helicopter's and heavy gunship's rockets and missiles fly 20 % slower.
- The light tank fires one round at a time; every machine gun streams longer and changes faster; FPV carriers,
  Shahed launchers and the drone mothership launch drones one after another instead of in waves.
- Every unit's damage a second +5-10 % by its cost (cheap units most), on the calibre scale: rounds raised within
  their band, the rest by a quicker rhythm.
- Missiles fired at a boss, a big ship or a large aircraft or tower burst where they meet its hull (or the part they
  struck), not in its middle.
- The Lancet's blast is drawn a fifth bigger, the long-range SAM's burst is bigger (3.6 m, Huge), the drone
  mothership drops two guided bombs, the C-RAM's gun fires only at incoming rounds, never at aircraft, and the
  rocket battery, artillery emplacement, Patriot battery, SAM post and coastal turret have no machine gun.

### Play-test 5: visuals

- Every explosion is layered and grander, by calibre and tier: a white-hot core in the fireball, secondary fire
  bursts, more sparks, fragments and embers, a second dust skirt and air ring on big blasts, rising smoke, and a
  smoke column over the crater of big ones (bombs, heavy rockets, boss attacks, falling buildings and towers,
  napalm). Low keeps every layer with half the added particles and never less than before (DECISIONS 20V).
- Blasts bigger: tank rounds +20 % wide and +20 % longer, artillery and mortar shells, missiles and rockets, and
  drones +20 %, the gun turret's rounds +30 %.
- A new fire on badly damaged vehicles: one to three fire points on the hull by the damage, each a bright flame
  core, tongues of flame, embers and a dark smoke column; lighter on Low.
- Shorter flames behind the SAM launcher's, thermobaric launcher's, heavy rocket artillery's, ballistic missile's,
  long-range SAM's and Patriot batteries' missiles, still sized by the munition.
- A railgun hit leaves a burn on the target like the focused laser's: a glowing spot cooling, sparks, smoke, a
  scorch.
- In action: the targets are a jeep, an armoured car, a light tank, a battle tank and a heavy tank (armour 0 to 4)
  and none lays smoke; every fire support is framed with the sky its aircraft or rounds come from.
- Models: a finer, 20 % smaller FPV drone; the bunker vehicle dug in as an emplacement (hull-down behind a bank of
  earth, sandbags, plates as revetments, a camouflage net); the AC-130 gunship with its 25, 40 and 105 mm guns
  drawn big out of the left side and a sensor ball, now on the gunship's card and item; a gunless transport for
  airdrops; the stealth fighter's middle detailed (intakes, canopy frames, spine, panel lines, bay seams). Card
  pictures to render.
### Armour and damage balance

- Fights are 10-35 % shorter and armour costs less (DECISIONS 20X): the penetration row is 1.2 (two or more levels
  above: the round overmatches the face), 1, 0.85 (level), 0.5, 0.25, 0.1 (was 1, 0.75, 0.4, 0.15, 0.05); overmatch
  counts on a front, side or rear, never on a roof or an aircraft; the front arc is 40 degrees (was 50); vehicles'
  toughness 2.2 (was 2.5; bosses unchanged); the turtle tank's front 3 (its shed stops drones, not darts).
- A flank shot beats a front shot for every gun (battle tank on battle tank: 26 s side on, 35 s front on; were 35 and
  46); the right counter still wins (the tank destroyer 25 s on a battle tank, two armoured cars 39 s). `CounterTests`
  hold; campaign, Conquest, Siege and Defend win rates hold on a 3-seed sweep. New measure `ArmourBalanceMeasure`
  (time to kill, hits by penetration step and face); tables in `Docs/balance/*_20x_*`.
### Play-test 5: rhythm, behaviour, siege tank

- Every vehicle, helicopter and aircraft autocannon fires about 5 s at a time and changes its magazine in about 1 s
  (the Gepard, the Tunguska mount, the ZU-23, the IFV, BMPT and armoured car, the Apache's M230, the Mi-24P's
  GSh-30K, the Su-25's GSh-30-2, the F-35's GAU-22, the gunship's 25 mm and 40 mm). The damage a round stays on the
  calibre scale and the damage a second is unchanged, so the cadence over the stream is the old average; the anti-air
  vehicles' missiles fire beside their gun's stream and their rounds hit aeroplanes harder (DECISIONS 20W).
- Fighters and the stealth fighter get on an enemy jet's tail: they fly for a point behind it, then keep their nose on
  it at a little over half the cannon's reach and stream the cannon, their air-to-air missiles firing beside it.
- The TOS-1A's, the Smerch's and the rocket battery tower's rockets (both its branches) fly at the SAM's 24 m/s; the
  attack jet's rockets and missiles are 25 % slower; the drone mothership's drones 40 % slower.
- The C-RAM streams a burst at every round it takes down (0.5 s, the Centurion 0.3 s, tracers on the round as it
  flies) instead of one shot; interception rates stay near their old values.
- The siege tank is reworked into StarCraft 2's: a 105 mm tank on the move; standing with an enemy in reach, or on guard,
  it sieges in 2.5 s (braces down, turret up, 105 mm back, the 240 mm mortar raised) and shells from 16 to 70 m; it
  packs up to move or when enemies get inside 16 m with nothing further to shell. New model with the animated
  deploy, armour by face, Guide card, behaviour lines, icon; now won in the campaign (chapter 4) instead of bought.
### Boss redesigns and death smoke

- Ixion is a Tsar Tank war machine now: 10 m spiked wheels with scythe hubs, slab armour, chains, a spiked roller across
  the front, exhausts and rust (DECISIONS 20Y). Icarus is a wedge warship in the Star Destroyer and Venator mould, with a
  stepped superstructure, a command tower, an engine bank and a ventral hangar; its wreck follows; every node, the
  altitude tiers and the crash work as before.
- The boss review redrew Typhon (Typhoon-class lines), Caspian (the Lun ekranoplan) and Daedalus (an Acclamator-style
  assault ship); the others were kept.
- A boss's death fires keep their flames but smoke a third as much, lighter, and clear within seconds.

### Leviathan as a battleship

- Kessler's Leviathan is a battleship on the Yamato's lines (DECISIONS 20Y): 96 x 16 m, a flush deck with a strong bow
  sheer and flare, three triple 460 mm turrets (two forward, one superfiring, one aft), a pagoda tower with a long
  rangefinder, one raked funnel with launch cells beside it, triple 155 mm secondaries, 25 mm tubs and 127 mm mounts
  along the sides, catapults, a floatplane and a crane aft, anchors and chains forward, in Hegemon's marks.
- New breakable guns: the three main turrets (one gun each a salvo, all nine in the big attack, now the Nine-Gun
  Broadside at the base), two 155 mm secondaries, two 25 mm batteries of four mounts, two CIWS; 14 parts at 5 %,
  health unchanged. Laid turrets stay inside their arcs.
- The old model is the fleet's missile cruiser (two twin 203 mm, two CIWS) with its own name, note, dossier file and
  Guide line; the cruiser and a corvette keep station abeam on the shore side instead of inside the hull. Scylla is
  scaled to stay a 48 m destroyer and keeps its salvo and cruise missiles.

### Missile speeds, fire rates, models

- No missile flies faster than the attack helicopter's Hellfire (24 m/s): the SAMs, air-to-air and MANPADS missiles,
  the Iskander, the towers' SAMs and Iron Dome, and the bosses' big-attack missiles. Rockets keep their speed; plumes
  follow the new speeds. `CounterTests` hold (DECISIONS 19R).
- Guns fire at their real rate (up to 60 rounds a second): the Gepard 1,100 rpm, the Tunguska mount at the cap, the
  ZU-23 1,800, the minigun and the Su-25's GSh-30-2 3,000, the F-35's GAU-22 3,300, the Mi-24P's GSh-30K 2,400, the
  M2 550, the PKT 750, the AK-630 at the cap, and so on, in real bursts; the pause after a burst keeps each weapon's
  damage a second. Grad and TOS ripples at their real interval. The towers' real rates are listed for the tower pass.
- The bunker vehicle is redrawn: on the move a walled engineer hull with a dozer blade; digging in, the spades and
  blade bite, the hull sinks into a spoil bank with sandbags, the side plates fold down over it and the turret rises
  on its telescopic mount. (The old spades and plate had never moved: the spawn merged them into the hull.)
- Look-alikes redrawn: the light tank (amphibious, a 57 mm module forward, trim vane), the Titan (a second,
  superfiring turret), the laser tank (a beam director on a yoke, a power module) and the shield carrier (a tall
  emitter mast with a halo). Card pictures to render.
### Prompt 21: Sandbox

- A Sandbox with the challenges on the Operations tab (DECISIONS 20S): set up any battle on any battlefield (the 300 m, long and coastal ones) or a flat test range with a metre grid, pick Blue or Red, place units one at a time or in a line, column, cluster or arc, and turn them by 15° (or freely) with a drag.
- Seven tabs (vehicles, aircraft, towers and structures, bosses, mini bosses, elites, ships and escorts) with search and branch, armour and weapon filters. Towers go on hardpoints, anywhere on the test range and anywhere in the internal build, with their rank and their rank-7 branch.
- Each unit (or a whole selection): side, rank, equipment (none, a suggested set, yours), elite, health, ammunition, immortal, and for a boss its starting phase, parts, big attack, escorts and altitude tier; copy, move, delete, undo and redo.
- The battle: run, pause, one tick, ×0.25 to ×4, reset; full AI, fighting AI or standing still for each side; unlimited or set CP, support cooldowns on or off, a whole side immortal; orders (go to, hold, hold fire, fire at); fire support called anywhere; the seed. The same scenario, seed and controls always give the same battle.
- Boss tools on a running boss: jump to a phase, big attack now or off, break or restore each part, change altitude tier, escorts on or off, swap between main and mini boss, and the bosses' difficulty.
- Overlays, each on its own: range rings, hit numbers with ✓ ~ ✕ and the face struck, real DPS and combat value, magazines and reloads, big-attack zones and shields; internal only: hit boxes, routes, stuck vehicles, the AI's buying scores.
- Scenarios save with a format version (older files still open), share as a text code (locked units swapped for unlocked ones of the same role, with a notice), export a replay with its seed, and in the internal build save as automatic tests with pass conditions; five samples; up to 20 of your own.
- Quick duels (two units or groups, distance and facing, one seed or twenty with the win rate), A/B runs of a scenario with two equipment sets, and an after-battle table (damage dealt and taken by type, time to kill, lifetime, rounds through and bounced).
- The player version opens once the last chapter switched on is finished, offers only unlocked units and beaten bosses, and pays nothing: no coins, rewards, records, daily progress or achievements, and no items are used.
### Prompt 21: Vietnamese and English

- The language follows the device on Auto and switches at once: the menu reloads in the new language, and the pause
  menu has the switch too; the battle HUD relabels itself in place without restarting the battle.
- Every placeholder is named (`{count}`, `{seconds}`); numbers follow the language (184.172 and 0,75 in Vietnamese,
  184,172 and 0.75 in English); English counts are singular or plural ("1 coin", "2 coins").
- Every text has both languages. The map table's names are used everywhere; the English left in Vietnamese texts
  (map, laser, tungsten, rocket, sonar, English map names) and the Vietnamese left in English texts (Landing Beach, "xu")
  are gone; a boss is "boss" in Vietnamese; percentages read "25%".
- Boss subtitles are translated and match on the card and the boss bar ("Icarus · Orbital Spacecraft" / "Icarus · Phi
  thuyền quỹ đạo"). The story's Vietnamese names are tokens of one name table, ready for prompt 22.
- Tight spots in English and Large text: the tower-branch picker stacks its cards in Large text and shows short names,
  the icon legend widens, four gear pieces have shorter English names, the thermobaric launcher's short name is TOS-1A.
- New checks: `L10nTests` and `L10nSwitchTests` (both languages in every key, named placeholders, nothing left
  unfilled, one language per screen, number formats, plurals, switching on the menu and in a paused battle);
  `UiLanguageTests` covers every table and every font; the layout checks run in English and English Large as well.
- `Docs/localization-report.md` (the audit) and `Docs/glossary.md` (the terms in both languages). Screenshots of
  both languages wait for the testing phase (`UiShots -mbShotsSet l10n`). DECISIONS 20L.

### Tower art

- Every tower's two rank-7 branches have models of their own (32, named `<tower>_a` / `_b` in the spec's order): the
  gun turret's very long 120 mm with a scope or twin short 57 mm barrels with a radar, the rocket battery's open rack
  or closed pod, a counter-battery radar beside the long howitzer or a squat 240 mm mortar, the fortress's long twin
  guns or armour plates and two small turrets, a radar mast on the watchtower or a low sandbagged gun nest, and so on
  for all sixteen towers. The data picks the model by the branch's order, or by a `"model"` on the branch entry.
- Ranks 1-6 show on the tower: a bar a rank on its walls, add-on plates from rank 3, thicker ones from rank 5 (the
  player's towers by card rank, the enemy's by HQ level; lighter on Low graphics).
- A line icon for every branch in the tower icons' style, shown wherever a branch's icon is (the branch choice first).
- The branch models use the shared far level and impostors; card pictures and clips are rendered after the merge.
### Tower branches

- Every tower's two rank-7 branches now differ in what they hit, their reach or a mechanism (DECISIONS 19T): a sniper 120 mm or a 57 mm autocannon with air-burst rounds; cluster or guided long-range rockets; a counter-battery howitzer or a heavy mortar that fires over walls; the coastal battery or a steel fortress with two all-round machine guns; a PAC-3 that shoots down cruise, ballistic and boss missiles or a long-range radar that shows every aircraft; one shield dome or a shield on every tower; a steady CP relay or a loot depot paid by kills.
- The C-RAM, rocket battery and AA tower branches tuned to the balance targets (the Centurion stops 90 % of an MLRS's rockets; the flak back on the calibre scale).
- The AI picks branches by the deck it faces, and each general has favourites; every branch is picked 23 % or more.
- The branch choice shows both branches side by side from their data, with when to pick each; the Guide has a block per branch.
- Saves: remade branches move to the nearest new one, one free change per reworked tower, a one-time notice.
- The branch models and icons come from the art branch by id (`<tower>_a` / `_b`); card renders later.
### In-action and effects fixes (DECISIONS 19P)

- **In action clip:** the unit shown never runs out of ammunition; the enemy can be knocked out and a new one comes in
  (aircraft fly onto the spot, vehicles drive up); aircraft glide in and slow onto their station, and nothing fires at a
  target before it is in the picture.
- **Towers with a scene of their own:** the CP relay counts its pay over the picture and stops paying while it is raided;
  dragon's teeth turn an enemy column round their ends; the minefield and the mine layer's mines go off under enemy
  vehicles driving across; the ammunition depot's launchers reload faster at home; the logistics station shows the
  supply it adds; the shield generator's attackers stand outside its dome.
- **Jammed missiles** no longer vanish: they fly true, crackle as they lose their lock, then corkscrew and roll off to
  land (or burst) wide where the simulation scores the miss.
- **Laser beams** hum continuously while they burn, with a whine as they ignite, instead of a machine gun's clatter.
- **Shield domes** flare and ripple where a round crosses their skin; a round a dome stops bursts on the dome.
- **FPV drones** (the swarms and the drone mothership's) look and fly like quadcopters: rotors, no motor flame or smoke
  trail, weaving corrections and a spread-out swarm, a buzz as they launch and a charge-and-debris impact of their own.
- **Sky gunship:** it stays over the spot it was called to, circles lower and tighter in the battle camera's picture, and
  fires its 105, 40 and 25 mm together.

### Design document: armour, penetration and weapon forms

- Every card shows armour levels by face and the main weapon's effect on each armour level, aircraft and structures (✓ ~ ✕).
- Every weapon table has penetration, form and tags. Section 10 adds a counters table and the icon legend.
- Fixed: the combat-value table uses the current roster, Boss Rush's "{0} bosses", the HQ instead of the bastion, the map, mission and difficulty counts.

### Prompt 20 pass 1: twelve chapters in four acts, new boss and general names, act switches (DECISIONS 19A)

- **Names (A):** bosses read "Proper name · Vietnamese subtitle" (the Silver Bug is "Icarus · Phi thuyền quỹ đạo", its
  project "Dự án Icarus"); generals are Brandt, Viktor Varga "Anvil", Ilya Orlov "Winter", Magnus Kessler "Maelstrom",
  Elara Sen "Queen", Kasimir Wolff "Raven" (still "Quạ Đen" on our side's radio), Lucien Aurel "Sol", Lý Hàn "Titan";
  Diều Hâu is "Hawk" on the radio, Khải "Iron". Every id is unchanged. Brandt has a portrait and a dossier entry.
- **Structure (B):** 12 chapters of 10 main and 2 side missions in 4 acts (Landing, Counterattack, Betrayal, Silver Sky);
  each chapter has its main boss and mini bosses in data (`campaign.json` "main"/"minis"); bosses pass 2 builds are
  fought as stand-ins (`"fallback"`). New chapters 8 (Underground), 9 (Rough Seas) and 11 (The Orbital Gate): 36 new
  missions written from existing ones on the same battlefields. The old chapters 7, 8, 9 are now 10, 7, 12.
- **Save migration:** campaign version 3 moves a nine-chapter save's stars, tiers and chapter cards to the new ids and
  keeps the HQ level it had; the 23-mission save still moves in one step.
- **Act switches (C):** `Resources/Data/release.json` (or `-mb-acts=1,2`): acts and chapters on, "Coming soon" or hidden;
  "To be continued" after the last chapter on; Operations, the weekly rotation and Boss Rush drop what is off; the
  unlocks and HQ levels of chapters off come with the last operation on; a shorter release pays more (x1.42 for acts I-II).
- **Economy (D):** a new unlock route (4-6 cards a chapter), HQ levels in chapters 1, 3, 6, 9 and 11, the deck at rank 7.1
  as act IV begins and 8.1 at the end.
- **Tools:** `Tools/campaign/act4.py` (the layout), `build_campaign.py` merges into `CampaignText.cs` (hand-localised words
  kept) instead of rewriting it. Tests: `Prompt20CampaignTests` (7).

### Prompt 19: the Silver Bug rebuilt as Aurel's orbital spacecraft (DECISIONS 18A)

- The final boss keeps its id `silver_bug` (records, progress and achievements stay) and is now a big military shuttle:
  new model, its crashed form, a satellite and a drop pod (`Tools/blender/mb_orbital.py`; the saucer builder is gone).
- Altitude tiers, data any boss can opt into (`"tiers"`): 15 s in low orbit at the start (out of reach, guns held),
  then a fixed cycle per phase, never back to orbit: phase 1 high 25 s / low 10 s, phase 2 high 15 s / low 20 s,
  3.5 s per change (hit as the lower tier meanwhile). High altitude: only long-range SAMs, Patriot batteries, fighters
  and stealth fighters (`"ceiling": "high"`); low: every anti-air weapon, helicopters, and railguns (`"ceiling": "low"`).
- Parts (70 % of the body, 7 % each): the main engine (broken: it stays low), four manoeuvring thrusters (slower,
  longer changes), two point-defence lasers (its APS against SAMs and fighters' missiles), the drop-pod bay, the
  satellite uplink (its big attack) and the ventral laser turret. Armour by altitude: hull 4, belly 2 (low), 3 crashed.
- Drop pods (`"pods"`): two at a time in orbit and at high altitude, 1-2 vehicles each, low-altitude targets while they
  fall 6 s (shot down, nothing lands), at most six of their vehicles alive. Escorts come as it leaves orbit, with two
  fighters; phase marks 70 % and 30 %.
- Big attack `bug_rod_rain` replaces `bug_laser_sweep` (a new `rods` shape): five tungsten rods on the densest groups,
  heavy armour first, 1 600 kinetic, penetration 4 on the roof, 6 m, 4 s of warning, every 60 s; the first from the craft
  in orbit, the rest from its satellite; the uplink broken cancels or ends it; smoke and APS do nothing, domes absorb
  part. No boss big attack is stopped by smoke now.
- Phase 3: it falls to a set point mid-map and fights on as a ground fortress (a ground target, the wreck model, four
  guns all round awake, passable debris that blocks fire, its ground closed to routes and cleared of units). Very Hard:
  it seizes the player's drones and drone launchers for 6 s now and then; jammer and EW-tower cover keeps them.
- HUD: an altitude chip with the seconds to the next change and the phase marks on the boss bar; tapping it lists the
  deck ✓ ~ ✕ by what reaches its tier. The Guide has an altitude section; every text is new or rewritten in both
  languages (`OrbitalText`, the campaign's chapter 9, the boss files, briefings and radio lines): no saucer is left.
- Boss Rush fights it on the Launch Site (`"arena"`), as the sea boss at sea. Sandbox calls for prompt 21:
  `JumpPhase`, `ForceTier`, `TriggerBig`, `SetBigOff`, `Break`.
- Tests: `OrbitalBossTests` (10) and the boss tests it touched; the 5-seed runs, the stuck check round the crash site
  and the FPS checks wait for the testing phase.
### Prompt 20 pass 2: boss templates, main and mini bosses, four new main bosses and nine new mini bosses (DECISIONS 19E)

- Bosses are built from data templates: body frames, a shared part and weapon library, big attacks built on others,
  escort templates by general, ranks and variants (a mini boss made from a main boss by data). How to add one:
  docs/ADDING_A_BOSS.md.
- Main bosses are larger, have three phases and new weapons (Bastion's casemate and ZU-23s, Behemoth's flank guns, Jötunn's
  second howitzer and SAM, Leviathan's 127 mm guns, Matriarch's belly guns and second bay, Roc's gun pods, Nemesis's two
  new cars, Icarus's crash turrets). Mini bosses are smaller, have half the health, lighter weapons and big attacks, two
  phases and two or three escorts. The bar reads "Boss" or "Mini boss"; the camera pan follows the rank.
- New: Moloch (a factory that builds tanks), Daedalus (an orbital lander raining drop pods), Kronos (a bucket-wheel
  excavator that crushes its way to the HQ on the open-pit mine), Typhon (a missile submarine that dives), Ixion (a giant
  wheel), Caspian (an ekranoplan) and the variants Bastion Mk.0, Fenrir, Scylla, Locust, Behemoth Mk.II, Icarus Mk.0,
  Argus, each with parts, a big attack, escorts, a Guide card and radio lines. Every boss is tied to its general.
- Boss Rush takes the new bosses; Operations' "two bosses" brings a mini boss.

### Prompt 20 pass 3: Boss Hunt, the full Boss Hunt, boss and battlefield pages (DECISIONS 19N)

- Boss Hunt (was Boss Rush): each week 10 bosses from the chapters that are on, 7 mini bosses leading to 3 main bosses,
  the same draw on every device, stronger down the run, 45 minutes. A 20 s rest repairs 30 % of the army; after each
  main boss pick one of 12 combat supports and keep a checkpoint (take the run up again later, from the result screen
  or Operations). The first clear of the week pays 1 500 coins.
- Full Boss Hunt, open after the last chapter that is on: every boss in story order, a checkpoint after every boss, a
  board of the best total times, 10 000 coins and a legendary crate for the first clear. The trains stay out (no rails).
- Operations' "two bosses" is "Extra mini boss": the chapter's or the boss's mini boss.
- Boss bars: big for main bosses, small for minis. Boss Guide pages: rank, chapters, general (call sign, naming theme),
  "Variant of ..." links; the dossier's boss files link to them. New dossier tab: Battlefields (with the open-pit mine's
  and the orbital gate's guides). Chapter cards count their mini bosses.
- Six missions moved onto the new maps: c8m02, c8m07, c8m10 (Kronos walks its haul-road route) to the open-pit mine,
  c11m04, c11m07, c11m10 to the orbital gate.

### Prompt 20 L-M: towers (Iron Dome, rocket battery, SAM post) and two new battlefields

- The C-RAM's rank-7 Iron Dome branch (it replaces the Hunter; a saved Hunter choice is dropped): interceptor missiles
  for rounds lobbed at anything within 60 m (artillery rockets, half the shells, drones, long-range missiles), never
  direct fire or energy; six in the launcher, reloaded whole 12 s after the last launch; its own icon, behaviour lines
  and notes. The enemy AI picks Iron Dome or Centurion by the player's deck.
- The rocket battery's rockets arc over walls and cover (checked; a test); an AI's layered base keeps rocket batteries
  in its yard against attackers at the wall. The AA tower's SAM post reaches 60 m, between the flak and the Patriot;
  the flak branch's quad 23 mm hits harder (22 a round), so it is the drone and swarm killer.
- Open-Pit Mine (terraced pit, haul roads, a fixed route for a slow boss in the map data) and Orbital Gateway (radar
  station, side launch pads, an open drop-pod field): Conquest, Survival, Siege and long versions, camps and outposts,
  menu pictures, names, guide text; in the skirmish list.
### Balance pass after prompt 18

- The section-17 measurements ran in full: the campaign over 5 seeds, the stuck detector on 21 battlefields in 4 modes over 5 seeds (420 battles), the tick budget, every mode at every difficulty over 5 seeds (DECISIONS 19B, `Docs/balance/*p18*`, `tables_p18.md`).
- Towers on the owner's DPS targets with weapons of their own (rhythm, magazines, the AA tower's flak fuzed for aircraft); the HQ's flak halved. The C-RAM, rocket battery and AA branches wait for the lead's merge.
- Vehicles: Iron Beam 7 CP and faster, SAM launcher faster and tougher, wheeled gun +20 % and +250 HP, IFV +40 % rhythm, twin tank 96 on heavy, Lancet 100 m, thermobaric launcher 48 m (it could not reach forts), cheaper-to-tougher aircraft (fragmentation on aircraft 1.5 to 1.3, more health), attack jet and strike drone one store less and 1 CP more, flame tank 5, car bomb 3, Titan 16 CP.
- Airstrike 6 x 400 at 6 m for 9 CP. Support texts take their numbers from the data (the air raid's "fourteen" bombs were 10, the cluster strike's "forty" bomblets 30), with a test; the boss supports have names.
- Siege harder, Defend's outer line tougher and its first waves lighter, Normal's enemy income x0.7 and its deck of typical cards.
- New measures: `TowerValueMeasure`, `BalancePassMeasure`, the combat value's artillery fight.

## v0.29.0: Prompts 15-18 (armour and penetration, the sea and escorts for every boss, long maps and new units, the roster review, big attacks) and the 187-page design review

2026-09-29 · merged into main

### Prompt 15 (battle rules): armour levels, penetration, six damage types

- Every unit has armour 0-4 on its front, sides, rear and roof (towers, buildings and aircraft the same all round,
  bunkers thicker in front, boss parts their own); every weapon a penetration 0-4 from the real weapon. A round a level
  above the armour does all its damage, level three quarters, then 0.4, 0.15 and 0.05. Top-attack missiles, drones,
  bomblets, artillery, bombs and diving aeroplanes hit the roof.
- Six damage types: kinetic, shaped charge, high explosive (thermobaric harder on buildings), fire (burns on),
  fragmentation (flak and anti-air missiles), energy (lasers). Reactive armour and cages stop shaped charges, APS shoots
  down missiles, rockets and drones, flares fool missiles, smoke scatters lasers.
- Equipment reads by level (+penetration, +side armour, damage against heavy armour 3-4); old pieces keep their slot,
  rarity and level. Elites are a level thicker in front. The commander picks what pierces the armour it sees.
- Rebalanced from the combat-value re-run: IFV 6 CP, light tank 3 CP, flame tank 4 CP, scout helicopter 4 CP, car bomb
  2 CP, sturdier SAM launcher and rocket technical.

### Prompt 16 (part 1): Lighthouse Bay, Leviathan and its fleet

- New battlefield, Lighthouse Bay: a rocky coast on the sea, two coves with beaches and piers, the lighthouse on its
  headland (hold it to see the fleet), abandoned coastal batteries to take (their guns fire on ships), a fishing
  village and an old fort. Conquest, Survival and Siege, and in the skirmish list.
- New boss, Kessler's Leviathan: a battleship at sea that shells the coast (marked, sweeping along it), fires cruise
  missiles, lands tanks, launches helicopters and calls jets; its CIWS shoots down missiles and drones, its sides shrug
  off direct fire but its deck does not. Below 40 % it runs for open sea on a clock. It lists, breaks in two and sinks.
- Its fleet: escort corvettes (their CIWS covers it), fast missile boats that raid the pier heads, landing craft.
- Chapter 4 ends with "Leviathan" (4-11); it opens the heavy fortress's Long-range coastal battery. Boss Rush sails to
  Lighthouse Bay for it and back; Operations adds the Sea storm and Fleet mutators.
- Low graphics: simpler water and wakes.

### Prompt 16 (part 2): the old bosses' new weapons, escorts for every boss

- New weapons, each a part you can break: the Iron Train's mortar car (it lobs over cover), the Tempest's interceptor
  laser and the Behemoth's protection system (they shoot down missiles, drones and rockets), the Inferno's fire trail,
  the Hive's jamming aura, the Bastion's Kornet launcher, the Doomsday Train's rocket and long-range SAM cars, two AA
  mounts on the Rail Supergun, and two more CIWS and two rocket launchers on the landing hovercraft. Their health was
  retuned so the fights last about as long as before (within 10 %).
- Every boss brings escorts: a group with it and another at each phase change, at most 4-6 alive by difficulty (fewer
  in Boss Rush). Each group has a helper that repairs the boss, jams your missiles, covers it from the air or marks your
  units for its guns, so you choose between the boss and its escorts. Escorts stay near their boss, pay CP when
  destroyed, wear an orange mark, and the boss bar counts them. The old escort calls are replaced by this.

### Prompt 17 A-B: long maps and layered bases

- Siege, Defend, Endless and the weekly fortress play on long battlefields: 300 m across and 480 m along the attack, the
  map's own battlefield in front and a layered base behind it (all 20 maps; the other modes keep their 300 m maps).
- The layered base: a buffer zone of dragon's teeth, ditches, wire and firing positions, forward works with the relays,
  an outer wall with a main gate and two sally ports, a yard, an inner wall (the keep) and the HQ; the defenders land in
  the keep, the attack's reinforcements land further forward as each ring falls.
- More slots on a long base: HQ level 1 to 5 open 4/1/0/1 up to 8/5/3/4 (small/medium/large/utility), plus forward
  strongpoints. New slot places (outer gate, outer wall, yard, inner wall); one base plan fits both kinds of base, and
  the Base screen shows each map's long base as its own entry.
- The camera looks along a long map's length, zooms out further, and the minimap keeps its rectangle.

### Prompt 17 C: new units and towers

- Stealth fighter (20 CP): unseen until it fires, four AIM-120s, two small guided bombs for air defences, a 25 mm gun.
- Loyal wingman drone (6 CP): flies with your manned aircraft and may draw the missiles fired at them; outside the
  six-aircraft cap, four a side.
- Focused-laser tank (10 CP): its beam burns harder the longer it stays on one target (x0.3 to x2 in 6 s).
- Shield carrier (7 CP) and shield generator (large tower): domes that take every hit but energy for the friends inside
  until they break; domes do not add up.
- Bunker vehicle (8 CP): digs in when it stands (3 s): thicker front, 30 % more reach, turret all round.
- Drone mothership (14 CP): flies a swarm of eight FPV drones anywhere; the drones are not aircraft.
- CP relay (small tower): more CP for its side, two to a base, not on outposts, silent for a while after a hit.

### Prompt 17 D: roster review

- Merged cards: the A-10 is now part of the attack jet (30 mm cannon, rockets, bombs, two Kh-29 anti-tank missiles,
  R-60s; armoured; 15 CP); the Ka-52 is part of the attack helicopter (Hellfires in pairs from 55 m, out of short-range
  flak, and Stingers; 11 CP); the ATGM carrier is gone (FPV carriers, IFVs and ATGM towers do its job); the fortification
  sapper is part of the engineer (repairs vehicles and towers, clears mines); the hidden gun pit is gone from the towers.
- Your progress moves across: the higher rank and the blueprints, the coins of the lower rank back, a bought Ka-52
  refunded; gun pits in your bases become gun turrets and their equipment moves over (or back to the bag).
- Twin-barrel tank: two 120 mm guns fired as one volley, a long reload, quicker than the heavy tank: the tank hunter.
  Heavy tank: its 152 mm loads high explosive for buildings and light vehicles on its own; 12 CP.
- The new units' costs from the combat-value measure: stealth fighter 14 CP, swarm carrier 8, bunker vehicle 6.
- Lighthouse Bay has a long Siege map; the hovercraft's escorts ride fast missile boats; the campaign opens 5-7 cards
  a chapter.

### Prompt 18: a big attack for every boss

- Every boss has one big attack, telegraphed: its zone lights up in its exact shape (a circle, a strip, a line, a sweep,
  the points of a walking barrage, a missile's landing) with a countdown, the part that fires it glows on the boss and
  flashes on the boss bar, and its general or your command says it on the radio. About 30 s after the boss appears,
  then on its own cooldown.
- Break that part during the warning and the attack is cancelled ("Broadside cancelled"); each gun car, rocket box,
  drone rack or flamer takes its own share; with the part gone for good the boss has lost its big attack until it
  patches it. An EMP delays the Tempest's and the Silver Bug's charge.
- The Doomsday Train's tactical missile, the Leviathan's cruise missile volley and the Hive's drone swarm fly and can be
  shot down by anti-air, C-RAM, point-defence lasers and APS. Smoke cuts the Silver Bug's laser to a fifth (not the
  Tempest's railgun); shield domes take the Ice Fortress's rocket rain.
- Your ground units inside a warning get out on their own if they can make it, and go back after.
- New boss parts: the Doomsday Train's missile erector and bomb bays on the Hive Carrier and the Command Airship.
- The boss's Guide tab explains its big attack: what it does, how to get out of it, how to stop it, whom it is for.
- By difficulty: Easy hits softer, less often, with a second more warning; Hard and Very Hard come round sooner.

<details><summary>29 commits</summary>

- `5f808c8` 2026-09-29 Design document: section 20, a picture library (every vehicle, elite, boss, tower and module rendered large, in-battle shots, effect sheets, model and terrain sheets, stuck heatmaps)
- `cd90e57` 2026-09-29 Prompt 15 D: the armour and weapon icon set drawn from scratch (57 icons: 15 armour, 30 weapon forms, 6 damage and thermobaric marks, 3 extra marks, 3 verdicts), fills, holes and dashes in the icon renderer, CombatFacts and KitCombat, the row on deck, collection and tower cards, the show-numbers setting
- `46b6e33` 2026-09-29 Prompt 15 E: the icons where they show: the detail page (armour diagram, chips on the Weapons tab, the effectiveness table, generated strong/weak lines), the legend page, the Base and Outpost trays, the five-shield cover rows, the tray's hold tip, the selection strip, the enemy tap tooltip, boss parts
- `0cc2d54` 2026-09-29 Prompt 15 sim, milestone 1: armour levels, penetration and the six damage types
- `c34a8df` 2026-09-29 Prompt 15: the combat icon tests, the icon sheet, the enemy tooltip battle shot; Vietnamese words for icon and tooltip
- `b14c49a` 2026-09-29 Prompt 15: the icons read the sim's data (armour by face, forms, penetration, tags, Matchup's effect row, verdicts and strong/weak summary); +N and enemy tooltip layout fixes; the stray music metas out of the index
- `0bf1fe0` 2026-09-29 Prompt 15: detail-weapons and detail-armour screens (scrolled to the table and the diagram), the deck's shields beside its summary, a narrower enemy tooltip; UiShots takes a comma list of names
- `a4af56f` 2026-09-29 Prompt 15 screenshots: the combat icon sheet at 16:9 and on the 1280 x 720 screen at the smallest size, the deck's card row and cover, the detail page (armour, Weapons tab with the table), the legend, the enemy tooltip with a held tray card
- `4d07b15` 2026-09-29 Prompt 15 sim: counters, the gear migration, counter-picking AI, first rebalance
- `fe23bb2` 2026-09-29 Card pictures for every fixed defence (the super-gun, the spawn bastion, the fallback post share their models' renders; the targeting station rendered), and the design document's picture library finds each card's render through the manifest (the utility modules' pictures are named after their models)
- `851c62d` 2026-09-29 Prompt 15 sim: the combat-value re-run, the rebalance and DECISIONS 14A
- `2c6fcdc` 2026-09-29 PlayShots: in-battle pictures from Play mode (fixed maps, decks and seed, views from the sim, the live HUD drawn off-screen and blended over); DECISIONS 14B; the design document's icon set pages
- `4855941` 2026-09-29 PlayShots: wait for the new match's world, and close views on the towers nearest the HQ
- `080eee9` 2026-09-29 Prompt 15: the legend's counter table follows the sim's (smoke cuts beams, a jammer row), the enemy tooltip's multiplier from above for aircraft as the sim's verdict, the test checks the sim's Verdict
- `739565d` 2026-09-29 Prompt 15 screenshots after the sim's rebalance, and the in-battle pictures (battle3d-conquest, -siege, -defend with three close views of the base, -boss, -air, -barrage: 3D and the compact HUD from Play mode)
- `5e7f5aa` 2026-09-29 DECISIONS 14B: the checks as run
- `8b42d05` 2026-09-29 Prompt 16 E+F WIP: old bosses' new weapons, escorts for every boss (uncompiled)
- `497e16a` 2026-09-29 Prompt 17 C sim: stealth fighter, loyal wingman, focused-laser tank, shield carrier, bunker vehicle, swarm carrier, shield generator and CP relay (data, domes, deploying, wingman flight and decoy, laser ramp, drone swarm, relay income, AI use)
- `3ff6baa` 2026-09-29 Prompt 16 A: Lighthouse Bay (Conquest, Survival, Siege): a coast on the sea in the south-east (36 % of the square), two coves with beaches and piers, the lighthouse headland, cliffs with a coastal battery each, a fishing village, the old fort; its sea data (lanes, landings, piers, batteries) in every version
- `5a7f328` 2026-09-29 Prompt 17 A-B: long battlefields (300 x 480 m) with the layered base, for every siege map
- `d652c02` 2026-09-29 Prompt 16 E+F: old bosses' new weapons as parts, one escort system for every boss, health retuned from the kill-time lab, DECISIONS 15B
- `f0ca969` 2026-09-29 Drop a stray draft and two Unity-generated music metas from the prompt 16 commit
- `1551778` 2026-09-29 Prompt 17 C: the eight new units and towers finished: temporary models, texts, Guide cards and Behaviour lines, icons, dome and deploy views, In-action scenes, campaign unlocks, behaviour tests, DECISIONS 16C, CHANGELOG, ASSET_DEBT
- `8d6a1a3` 2026-09-29 Prompt 17 A-B: the sim, views and Base screen on long battlefields; layered-base slots, labels and plans; DECISIONS 16A
- `8833077` 2026-09-29 Prompt 16 B-D, G: Leviathan and its fleet at sea, chapter 4's epilogue, Boss Rush's sea switch, two mutators, Low water
- `f974235` 2026-09-29 Prompt 17 D: roster review, merges and save migration; C.9 costs from the measure
- `15ab08f` 2026-09-29 Prompt 18: a telegraphed, interruptible big attack for every boss, three new boss parts
- `ba24e8d` 2026-09-29 Card renders for the prompt 17 units and towers, Leviathan, and the five bosses rebuilt in prompt 16
- `e993f93` 2026-09-29 Design review PDF: section 7b (Lighthouse Bay and the fleet, escorts, long maps and layered bases, the roster review, every boss's big attack), the damage table on prompt 15's six types and penetration; 187 pages

</details>

## v0.28.4: Docs: prompt 24 saved (on hold)

2026-09-29 · `9a112f5`

## v0.28.3: Save the owner's prompts 22 (story, names, Commander system) and 23 (mission events, text dialogue), on hold

2026-09-29 13:38 · `75f10f2`

## v0.28.2: Save the owner's prompt 19 (the Silver Bug as an orbital spacecraft), on hold like 20 and 21

2026-09-29 13:11 · `9f5707f`

## v0.28.1: Save the owner's spec prompts 8-18, 20 and 21 in Docs/prompts

2026-09-29 13:02 · `bfe6f14`

## v0.28.0: Play-test rounds 2-3 (flashes on every barrel, plumes, blasts, fire rhythm, aircraft AI and sizes), prompts 11-14 (compact HUD, short names, shields, stuck vehicles, combat-value balance with stores on the field and AI by difficulty, the Base screen), the model muzzle audit

2026-09-29 09:30 · `0ce9bef`

Targeted tests and play-mode smoke runs pass; the full suite and the long sweeps wait for the testing phase.

### Prompt 11: a compact battle HUD, cards in line, short names, new shields

- A compact battle HUD, on by default (Settings > Compact battle HUD; off gives the full one): a smaller
  minimap with select-all and box-select on its corner (pinch to zoom), the objective and the clock in one
  strip at the top, Attack / Defend as one icon switch and Auto buy and Support as icon toggles (also in
  the pause menu), a card tray a third lower with the render, the CP and a short name (hold a card for
  its full name), the supply penalty as a small chip, a boss bar half as wide that opens on a tap (tap a
  part there to focus fire on it), small notices at the top that go after about 3 s one after another, the
  selected vehicles as one strip above the tray with Advance / Stop / Back, and the "your army fights on
  its own" hint only in the first three matches. In a fight the HUD covers about a quarter of the screen
  (the full HUD more than half). Every control is still a 44 pt target.
- Every vehicle, tower, structure, support and item has a short name for tight places; every card's name
  area is two lines high, so pictures, CP and levels line up in every row; cards in a row are one height.
- A tower branch's name no longer shows as a raw "support." key.
- Every shield redrawn with one shader: a hex-tile energy dome, bright at the rim and clear in the middle,
  red-orange for the enemy and blue for us, rippling where rounds hit, flickering as its generators are
  damaged and shattering when it falls; a lighter version on Low graphics. Its size and rules are
  unchanged.

### Prompt 12: stuck vehicles in bases

- A stuck detector in the internal build (`StuckWatch`, `-mb-stuck`), batch runs and a report with
  heatmaps and the ten worst spots in `Docs/stuck-report/`.
- Fixed at their causes: reachable goals and formation slots, no mutual queueing, head-on in the open,
  detours off walls, re-planning over newly closed ground, towers clearing their pad, room for the keep's
  guardian and elites.
- Fortresses: double sally ports and keep gate, clear yards and approaches, a three-cell route for the
  biggest hull everywhere (`check_access.py` checks every map); Swamp's causeways widened.
- A logged safety net for what is left. Episodes over 10 s in 76 battles: 1285 before, 265 after.

### Prompt 13: combat value, ammunition, modes and difficulty

- Every card measured by what it really does in a fight for its CP (Docs/COMBAT_VALUE.md), and the theoretical
  damage a second corrected (magazines, salvos, reloads). Prices and weapons tuned by it: tank hunters, artillery,
  helicopters, aircraft and anti-air in line with the ground units of their role.
- Damage a round by the real calibre (a 155 mm shell hits harder and comes less often), the same weapon with the same
  figures everywhere, ground SAMs a little slower with flare resistance.
- Aircraft carry bombs, missiles and rockets that run out and come back on the field: they finish their attack, fly a
  few seconds behind our line to a holding pattern, and come back; faster at the landing pad, over the HQ and (for
  helicopters) beside the new Ammunition carrier. Bombers carry fewer bombs, go in with two thirds of them and never bomb
  near our own units. The Sky gunship is no longer a card (the Gunship item still flies it).
- New: the Ammunition carrier (launchers beside it reload much faster, helicopters rearm twice as fast); the engineer
  repairs only. The landing pad's rank-7 branches: Hangar (one more aircraft up) and Fast service.
- Ammunition icons beside the health bar (low, empty, flying out, rearming, full), holding patterns on the minimap, the
  stores bar in the selection panel, and a setting for every unit or aircraft only.
- Unit details: every weapon's real name, calibre, rounds, magazine or stores and how they come back ("More"), and a
  Behaviour section, both worked out from the data; four notes corrected where they disagreed with it.
- Every mode rebalanced: Deathmatch scored in the CP destroyed (first to 480), King of the Hill to 170, a stronger
  Assault defender, a tougher Siege fortress, Defend and Endless waves scaled by the base and carrying siege breakers,
  Survival waves that keep coming, and help for the side far behind after 4 minutes (more income and a free drop).
- The AI by difficulty: Easy, Normal, Hard and the new Very Hard (it knows your deck and masses its attacks; rewards
  x1.8); decks of 8 to 12 chosen by roles and value; it buys ammunition carriers, hunts rearming aircraft and goes for
  landing pads. The campaign's Heroic and Iron tiers are now called Hard and Very hard.

### Prompt 14: the Base screen on the real camp, menus sized for a phone

- Menus are sized in the phone's own points, so they look the same size on every phone and a tablet shows
  more: a slimmer top bar and rail, smaller tabs and buttons (44 pt to tap), smaller type (13 pt text,
  18 pt titles; Large text 1.2 times) and cards in lists about a fifth smaller. The page's content now takes
  70-89 % of the screen. The battle HUD is unchanged.
- The Base screen is a picture of your camp on the chosen map from above, with red arrows where the enemy
  comes from and every slot where it really is: small, medium and large slots sized 1 / 1.4 / 2, utility
  slots as hexagons, empty ones saying what they take, closed ones the HQ level they open at. Pinch to zoom,
  drag to pan. "Show ranges" paints the whole base's cover, ground in amber and air in light blue; tap a
  tower for its range ring.
- Towers come from a tray with a tab for each size: drag one onto a slot, or tap it then a slot; only the
  slots it fits light up. Towers you do not have yet are dimmed with where they unlock.
- Tapping a tower shows its render, size and rank, its health, damage and range against the other towers
  of its size, its branch and gear, and Replace, Remove and Details. With nothing chosen, an overview.
- Along the bottom: what the base covers (light vehicles, tanks, air, rockets and missiles, stealth,
  repair and resupply; a gap in red), its strength (the same number the Defend and Endless waves grow
  with) and how many slots of each size are used.
- The HQ shows its level and what the next one adds; the map list has pictures; every change saves at
  once ("Saved").
- One base for every map: towers are placed by where they stand (gate, outer ring, inner ring, beside the
  HQ, rear), so the same base fits all 20 maps; a tower with no matching slot goes to the nearest one of
  its size, and a map where something did not fit gets a dot. A map can be set up on its own. Three base
  sets, switched on the Base screen or on the home screen. "Auto-arrange" lays the base out the way the
  enemy's AI does, with your towers. Your old base carries over: every map where it would have stood
  differently is kept exactly as it was.
- The outpost has its own tab.
- Every tower and module has its own icon.

<details><summary>77 commits</summary>

- `364688a` 2026-09-29 Troop transport: in from the map edge nearest the drop, over it, a climbing U-turn and home by the same edge, removed only past the edge (it used to vanish mid-map)
- `22dcbce` 2026-09-29 AA guns fire long streams from magazines (test feedback 2): ZU-23, flak 35, twin 30, quad flak, AHEAD, C-RAM
- `418d12c` 2026-09-29 Explosions a tenth bigger and tank rounds lingering: ExplosionEffect.Play takes a life stretch (fire, smoke, dust and embers; flash and sparks stay quick; the extra life scaled by tier like the extra particles) and a ring grow so a matched cruise missile or MOAB ring stays on its radius; BlastSizes.Bigger (x1.1) on every blast above the Small tier, ShellLife by tank class (+20/25/30 %), drones by type (FPV x1.2, Lancet x1.25, Shahed and strike drone x1.3); render rig mirrors it, Impacts sheet gains shell-landing and drone rows and later moments; tests
- `93fc1ff` 2026-09-29 Smaller fighters and helicopters next to the bombers and the transport: fighter -30 %, attack jet and three helicopters -15 %, A-10 and scout helicopter -10 % (model scale only)
- `5de961e` 2026-09-29 Detail page: the In action tab becomes a theatre, the preview fills the space under the tabs with the name, weapons and dock in a side column; small arrows beside the name, off the picture; the preview texture follows its box (shape and pixels, capped), framed as the old 4:3 crop
- `d2a8cd6` 2026-09-29 Smaller bombers, gunship (and the troop transport) by 15 %, strike drone 20 %, recon drone 10 %; flying bosses keep their size
- `2fd818c` 2026-09-29 Machine guns and helicopter guns on magazines (test feedback 2): 2.5-3.2 s streams, then a 1-1.5 s change
- `2c5f41b` 2026-09-29 Muzzle flashes on the barrel tip, the flame stream on its nozzle, vehicles over ground fires
- `9692607` 2026-09-29 Missile and rocket motor plumes, boost-then-cruise flight, sizes fitted to launchers, slower missiles
- `e986a30` 2026-09-29 Army: a Towers & modules tab beside the deck, tower and module cards (render, rank, size, upgrade mark) that open the detail page; the tower's detail page chooses its branch and fits its three gear slots in place
- `36ef496` 2026-09-29 Home setup: Boss Rush in the mode picker with its line (still on Operations); Deploy starts the picker's mode; a test taps it in
- `e7bbc98` 2026-09-29 PlaySmoke: -mbSmokePreview writes the detail page's preview texture at the end of the menu step and reports its size
- `f45d75a` 2026-09-29 Bosses stream too (test feedback 2): the mega gunship's guns, the hovercraft's CIWS, boss flak, the airship's 57 mm, the Bastion's 40 mm
- `d7726a8` 2026-09-29 Aircraft attack hold: jets hold their guns on the target, a VTOL fighter hovers, helicopters close to gun reach
- `cc9fbab` 2026-09-29 Motor plumes attached to the tail (stretched quads trail back from their particle, one frame of flight compensated), continuous cone with a glow body, smaller core; MissileFlightTests
- `536b55f` 2026-09-29 Flame streaks and tongues start where their flame shape shows; night muzzle light under the muzzle; late flash snapshots
- `b5e916d` 2026-09-29 DECISIONS 12E and the screenshots: the In action theatre (vehicle, tower, module), the Towers & modules tab, the detail pages with the arrows beside the name
- `50cfc30` 2026-09-29 DECISIONS 12A: muzzle flashes and the flame's origin, vehicles over ground fires, ground fires 20 % shorter
- `a212aff` 2026-09-29 Secondary magazine guns yield only to a gun at least as strong (test feedback 2)
- `d10c754` 2026-09-29 DECISIONS 12B: missile plumes, sizes fitted to launchers, slower missiles, boost-then-cruise flight
- `405278f` 2026-09-29 DECISIONS 12D: sustained fire for AA and guns, the before/after table, the rules changed, what is left for testing
- `6e396ba` 2026-09-29 Fire test counts the ground flame layer (ground fires moved there in 12A)
- `187baaa` 2026-09-29 Attack-hold pose and tests: the nose dips at the target, a hovering jet yaws without banking and rocks, it climbs away and dives back in
- `4c5cc0b` 2026-09-29 Each fire-support card brings its own round down: smoke shells are white canister rounds that burst open and pour white smoke (no glowing HE shell, no blast); barrage shells ride their tracer; mines come on rockets and the SEAD strike fires a missile (both with motor plumes through ProjectilePool.Launch); napalm canisters tumble; cluster dispensers split open into bomblets; the strike jet drops Mk 84s and the bombing raid is a heavy bomber with FAB-500s; the MOAB rolls out of a transport on a drogue chute; the EMP is a blue energy warhead with a flash and arcs; a repair drop is a parachuted crate; reinforcements are airlifted under canopies. All in StrikeEffects (AirDrops untouched); EffectShots.Supports sheet through a SupportRig; test
- `d0e2339` 2026-09-29 DECISIONS 12F: aircraft attack hold, helicopters at gun reach, measurements, the cannon damage change it needs
- `af44650` 2026-09-29 DECISIONS 12C: explosion size and life (factors, how the tenth combines, the matched ring stays on the radius and the fireball grows, drones by type, counts and lifetimes per tier), each fire-support card's round and arrival, sheets and tests
- `5fd7df5` 2026-09-29 Ground SAMs back to the 11C speeds (the extra 20 % cut was for aircraft missiles; SAM must still beat jets)
- `687bcdd` 2026-09-29 Missile flight test pins the ground SAMs' restored speeds
- `06ed244` 2026-09-29 Flash test pairs each flash with its own round; the Inferno's two flame projectors fire from their own nozzles
- `0fa681f` 2026-09-29 Design document: tower cards by size (render, stats, weapons, DPS, guide) with branch variants named, weapon cycles with magazines, Behaviour and Ammo blocks on every card
- `79fb42b` 2026-09-29 Flashes that read right: tank-gun cores ahead of the tip, small machine-gun and mortar flashes, a small ignition and backblast for launches; motor plumes 40 % longer and 20 % wider
- `e8f2e3a` 2026-09-29 Prompt 13 A: combat-value measurement (CombatValueMeasure), theoretical DPS over a whole load (FirePower), missile hit rates (MissileHitMeasure); ground SAMs 10 % slower with flare-resistant seekers (flareResist) so SAM still beats jets
- `79e3ecb` 2026-09-29 Prompt 13 B: damage a round by the real weapon's calibre (family, size, real name on every weapon), the same real weapon hitting the same on every carrier, the damage a second kept by cadence, magazine and salvo size; autocannon rounds get their own armour row (x0.38 on heavy); tank destroyer re-gunned to 125 mm, wheeled gun and gun pit to 120 mm; calibre tests
- `4d7640f` 2026-09-29 Prompt 11 A/B: the compact battle HUD, short names, cards in line
- `b5e6c74` 2026-09-29 Prompt 13 H.7: BaseStrength, the base strength number (HQ, towers and modules at their CP worth times their rank and equipment; 100 = the Normal enemy base at HQ level 3) for the Base screen and the Defend and Endless wave scale
- `e2acb2f` 2026-09-29 Prompt 13 A+B: decisions (13C A, B), the combat-value and theoretical DPS tables in Docs, real DPS in the measurement
- `5a148dc` 2026-09-29 Prompt 11: screenshots of the compact HUD (Conquest, boss, boss bar open, Siege, Defend, Survival, full HUD) and every screen again; the design document's UI section shows them
- `307c10a` 2026-09-29 Shields redrawn (prompt 11C): one hex-tile energy shader for every shield
- `abb0492` 2026-09-29 Tests follow the calibre cadences: the home rearm waits the mortar's own reload, the laser-warner tank holds its fire, suppression lasts past the shooter's own reload, the gatling has the least proc coefficient
- `6227cd6` 2026-09-29 Shield shots: the final sheet and in-game captures under Docs/art/shields
- `53523d4` 2026-09-29 Shields: vehicles stay covered while their item dome shatters; Low domes one tile level coarser
- `1590b0f` 2026-09-29 Prompt 14 A (work in progress): out-of-battle sizes in device points
- `f1a2fd4` 2026-09-29 Prompt 11: decisions (13A: the compact HUD, short names and their table, cards in line, raw keys, the shields), changelog, and the shields in the design document
- `999f943` 2026-09-29 Prompt 14 I: tower and structure icons of their own
- `373af99` 2026-09-29 Prompt 14 G (work in progress): one base plan for every map, by slot place; three plans; the migration from the version 2 loadout; AI loadouts can be limited to the player's towers
- `bf99e0d` 2026-09-29 Prompt 13 C, D, E: aircraft stores on the field (loads, one round at a time, slow while attacking or in danger, full at the holding pattern after 3 s safe), the holding pattern behind the nearest friendly line out of known AA reach, 2-3 s away, the landing pad, HQ and ammunition carrier as faster sites; aircraft finish their attack before leaving; bombers go in with two thirds of their bombs, pick groups and structures, never drop near friends, pause on ground just bombed; fewer bombs a run (bomber 9, stealth 2, Su-25 16 rockets, airstrike 6, air raid 10, cluster 30); roster review by combat value (tank hunters, artillery, helicopters, aircraft, anti-air); the sky gunship is no card
- `c4b32a0` 2026-09-29 Prompt 14 B.1-B.2: the Base screen's map pictures and approach arrows
- `122bd61` 2026-09-29 Base map pictures: normal-quality compression, forced reimport after a render
- `61cde0d` 2026-09-29 Prompt 13 F (sim and data): the ammunition carrier (4 CP support: launchers reload three times as fast round it, helicopters rearm twice as fast beside it; the AI parks it by its launchers and helicopters and buys one when it has three of them), the engineer repairs only (3 CP), the landing pad's rank-7 branches (hangar: one more aircraft up; fast service), the enemy base takes a landing pad and a destroyed fortress pad pays the attacker; empty launchers drive to a carrier or home when that is quicker than reloading in place
- `58080e1` 2026-09-29 Prompt 13 C-F: decisions (13C C, D, E, F), asset debt for the ammunition carrier and the landing pad branches
- `1f3c401` 2026-09-29 Prompt 14 B-H (work in progress): the Base screen rebuilt on the real camp picture, the Outpost tab, base cover and strength
- `4221022` 2026-09-29 Prompt 14: the base map framed on the camp, closed slots with their level, the cover strip in one piece, base sets on the home screen; Sprut allowed in Vietnamese texts
- `d4b824c` 2026-09-29 Prompt 14 J: every screen re-shot; Large text fits on the Base screen, home and top bar
- `d09a1ac` 2026-09-29 Prompt 14: decisions (13D: out-of-battle sizes in points, the Base screen on the camp picture, one plan for every map, the outpost tab, tower icons, camp pictures), changelog, and the Base screens in the design document
- `bf92411` 2026-09-29 Prompt 14 J: every screen re-shot after the prompt 13 C-F merge; the Base map's switches in short words
- `f3680f3` 2026-09-29 Prompt 14: decisions 13D, the map switches' short words
- `f2def11` 2026-09-29 Stuck vehicles in bases (prompt 12): stuck detector, batch runs, root-cause fixes, wide fortress gateways, map access check, safety net
- `2d1eedd` 2026-09-29 Muzzle audit from the model files; muzzles turned along their barrels, launch points on the real tube face
- `3888f21` 2026-09-29 Muzzle audit enforced (MuzzleAuditTests), the plume checked on the tail frame by frame, Docs/muzzle-audit.md
- `756152c` 2026-09-29 Muzzle audit: no regressions against the first run (95 wrong -> 54, 41 fixed, none broken)
- `52cdf9c` 2026-09-29 Prompt 12: the keep's elite reinforcements land where they have room; far formation rings may reach round a gate (a garrison spreads out instead of packing the keep's yard)
- `24e90b6` 2026-09-29 Prompt 13: the C-RAM shell test counts over enough shells (two guns; the C-RAM kept standing). Since B a 155 mm shell is one every 11 s, not 7, so one gun's four shells in 40 s at the C-RAM's 30 % share were all missed on this seed; the C-RAM itself is unchanged
- `f524ec9` 2026-09-29 PlumePlayCheck: the motor flame on the drawn tail in real Play-mode frames at 30 and 60 fps (worst 1.4 cm); MLRS rocket in the frame test
- `88b6e3d` 2026-09-29 Prompt 13 H + I: every mode balanced on a sample deck (Conquest's bleed and point CP, Deathmatch scored in CP to 480, King of the Hill to 170, a stronger Assault defender, a tougher Siege fortress, Defend's lines and waves, Survival's waves that keep coming and the overrun rule), help for the side behind, waves scaled by base strength and drawn against the base with siege breakers; the AI by difficulty: one buying profile per level, decks chosen by roles and value, Very Hard (knows the deck, masses its CP, x1.4 income, 30 % elites, rewards x1.8), hunting rearming aircraft and supply on Hard+, one ladder of difficulty names; migration tests
- `6fe4827` 2026-09-29 Twin and quad guns built as one part fire from each barrel; side guns flash along their drawn barrels (54 -> 34 wrong, 61 fixed, none broken)
- `382fca2` 2026-09-29 DECISIONS 13E: muzzle, launcher and missile-tail audit from the model files
- `175ef71` 2026-09-29 Prompt 13 H: after the merge, Conquest's point CP 0.15 and its enemy 18 % more income, the Hill's enemy 1.1, Assault's defender 32 CP and 1.3, 8 CP a sector, Survival's waves without a ceiling (elites to all of them by wave 24); decisions 13C H and I, the C-RAM test note
- `636137b` 2026-09-29 Prompt 12: the stuck report (before, after with and without the safety net: heatmaps, top-10 spots, tables), DECISIONS 13B, changelog; timing: formation walk only when a slot is out of plain line, slot untangling for groups up to 12, detours keep their side when both are closed, open-ground head-ons after 1 s
- `d8ac786` 2026-09-29 Prompt 13 G and F (UI): ammunition and behaviour lines generated from the data (UnitLines: real weapon name and calibre, type and targets, damage and salvo, magazine or stores and how they come back with the faster sites, range; movement and engagement, after firing, target priority, withdrawal, skills and auras, the landing pad's rates) on the detail screen (Behaviour in the guide tab, every figure behind More on the weapons tab, the module facts) and in the design document export (behavior, ammo, weapon name); a test that the hand-written notes agree with the data (four notes corrected: the IFV's 30 mm, the Ka-52's 23 mm, the Little Bird's 24 rockets, the TOS-1A's salvos of 9); the ammunition carrier's card picture and its In-action scene (two launchers reloading beside it)
- `79f9eb4` 2026-09-29 Model muzzles in Blender: 12 known mounts fixed at the source
- `a7dc559` 2026-09-29 Prompt 13 C.9: ammunition icons beside the health bar for aircraft, helicopters and launchers (low, empty and blinking, flying out, rearming with a ring that fills and turns dim or bright by the rate, a flash when full; enemies only empty and flying out), our holding patterns as faint rings on the minimap, the selection panel's stores bar, a setting for every unit or aircraft only, the icon table in the guide tab and a tip in c3m03 (the first mission with our own aircraft; c3m03's ammunition carrier unlock now in the campaign source too)
- `46734e6` 2026-09-29 Model muzzles in Blender: 11 more known mounts fixed at the source
- `f39bc8b` 2026-09-29 Prompt 13: decisions (13C C.9, G, F interface; Z left for the testing phase), changelog, the final combat-value tables (after F) and the mode measurements under Docs/balance
- `1920972` 2026-09-29 Design document: combat value per vehicle (9b), stores and rearming (12b), mode results and AI difficulty (2b), the testing list for prompts 12-13
- `74dd111` 2026-09-29 Cards of the re-exported models, the muzzle audit (284 mounts, 12 wrong, _hd 0) and DECISIONS 13F
- `a58ad0f` 2026-09-29 The ammo carrier drives the armed truck too (the merge kept the old prop model)
- `5df60a5` 2026-09-29 Design review PDF after prompts 11-14 and the model audit (141 pages): behaviour and ammo on every card, tower cards, combat value, stores, modes and difficulty, every new screen

</details>

## v0.27.0: Story campaign (9 chapters, 108 missions), Siege and Defend upgrades, prompt 8 content and elites, boss parts on every boss, Field Command 2.0 UI, LOD, and the play-test fixes

2026-09-29 00:48 · `2a3328b`

Phases 1-10 of the 2026-09 programme and the owner's play-test fixes (DECISIONS 11A-11D).
Targeted tests and a play-mode smoke run (menu, Conquest, Siege, Defend, Boss Rush, a boss
mission, a multi-stage mission) pass with 0 errors; the full suite and the long balance sweeps
wait for the testing phase.

### Prompt 8: new content, elites and equipment

### New vehicles and mechanisms
- **Armoured bulldozer** (Heavy, 7 CP, 3,250 health, heavy armour, 5 m/s, a roof machine gun): its
  blade rams structures for three times the damage within 4.5 m, it ploughs dragon's teeth and
  hedgehogs flat as it drives into them, and its belly plate halves mine damage. The commander sends
  it at the enemy base's obstacles and towers ahead of the line; an enemy that sees two or more
  bulldozers buys more tank killers. Unlocked in act II (mission 7), in General Varga's deck.
- **SP howitzer**: shoot-and-scoot (after three rounds it drives 15-20 m to a new spot still in
  reach, so counter-battery fire lands on an empty field) and near-zero scatter on marked targets
  (radar, UAV scan, laser designator).

### Bosses (all in Boss Rush, with guides, radio lines and parts on the health bar)
- **Rail supergun** (Kessler): a gun on its rail at the map's edge, one shell every 20 s anywhere on
  the map with a 3 s warning ring; its targeting station and guard emplacements around it; kill the
  station and its shells scatter.
- **Earth Worm** (Varga): dives underground (no one can aim at it), surfaces under the player's
  biggest group after a 2 s crack warning, stuns ground vehicles within 15 m, and takes half as much
  damage again for a few seconds after.
- **Command airship** (Quạ Đen): the general part mechanism. Four engines, two drone hangars and a
  radar, each with its own health; the hull takes damage only once two engines are down; a hangar
  down stops its drones, the radar down makes its flak miss. Only anti-air and fighters reach it.
- **Landing hovercraft**: runs its route along the coast and lands three or four enemy vehicles at
  each landing point; stop it before it has landed them all.
- **Supreme Commander** (Hùng, after the betrayal): a super-heavy command vehicle that barely
  fights, but every enemy within 40 m hits 20 % harder and fires 20 % faster; elite escorts.

### Elites
- Every elite on one footing: 1.6 times its base card's health, 1.25 times its damage, one or two
  elite skills; measured power (duel damage a second times time alive) 1.8 to 2.2 times the base
  card's. The EW carrier keeps its EMP only; the heavy tank its overdrive; the battle tank's shield is
  30 %.
- New elites: FPV carrier (barrage), attack jet (long flares), long-range SAM (overdrive), SP howitzer
  (barrage), on their base card's model in dark armour and gold trim.
- A budget instead of a chance: elites cost the enemy 1.6 times the base card; a share of its
  spending may go on them (Easy 5 %, Normal 10 %, Hard 15 %, Heroic 20 %, Iron 25 %), with at most
  1/2/3/4/5 out at once; generals favour their own kind (Varga tanks, Orlov artillery, Sen drones,
  Quạ Đen aircraft). Waves and reinforcements follow the same budget. The campaign's enemy pace
  takes the elites' edge into account.
- A kill refunds at the elite price; each elite destroyed pays 10 coins after the battle (the first
  four) and has a 6 % chance of a blueprint of its base card.
- A gold ring on the minimap, a radio line when the first elite of a wave turns up, and each base
  card's Guide tab shows its elite version.

### Equipment
- The fit matrix comes from the data: which branch each class belongs to, what every card has and
  what every piece, line, module and brand needs. Crates drop only pieces that fit a branch; the
  equipment screen only takes a piece onto a branch it fits; the branch pages list their classes.
- New base types: flanking rounds, airburst rounds (replacing the hyper-velocity charge), spare
  magazine, radar-absorbent coating, laser warning, reverse gearbox. The turbocharger and turret
  drive are now one drivetrain; the mine rollers are underbelly armour (mines and blasts); the signal
  relay adds 10 % vision.
- New unique lines: Vengeance, Suppressive Fire, Rearguard. New brands: Phoenix Recovery, Wolfpack
  Tactics, Bulwark Engineering (towers only, counted across the base).
- Twin Feed: an extra round only for bursts of three or more; one- and two-round weapons hit 15 %
  (Epic) / 20 % (Legendary) harder instead.
- A proc coefficient by weapon (its time between hits over 1.5 s, 0.15 to 2.5) on every on-hit line;
  Shredder needs more hits a stack on fast guns.
- Cluster warheads burst on the first two rounds of a salvo only.
- Fixed-effect modules scale with the card's price (CP / 7, between 0.4 and 1.3); the fuel blast is
  capped at 1,500.
- Kill refunds capped at 45 % of the victim's price, own-loss refunds at 15 %.
- Trade-off pieces drop from Rare up, their drawback growing with their rarity.
- Last stands (Unbreakable, Aegis, Phoenix) cannot chain on one killing blow.
- Save version 3: retired, merged and no-longer-fitting pieces are converted in place (same slot,
  rarity and level) or taken off.
- Retuned from the lab's measurements (Legendary): Twin Feed's salvo share 12 % to 20 %, Incendiary
  14 % to 25 %, Opening Salvo 80 % to 50 %, Momentum 4 % to 7 % a stack, Cluster Warhead 6 to 8
  bomblets; a ricochet carries the damage share of the hits that earned it (fast guns bounce seldom
  but hard). The armoured bulldozer has the turtle tank's 3,250 health, not the brief's 3,500.

### Documents
- EQUIPMENT_FIT.md and EQUIPMENT_VALUES.md (generated by `EquipmentDocsExport`), ASSET_DEBT.md,
  ROSTER_BALANCE.md (the prompt 8 DPS per CP table), DECISIONS.md section 8.

### Prompt 9: boss parts

- Every boss is a body and parts (its guns, launchers, engines, shield and EMP emitters, a locomotive,
  a drill, a ramp, an antenna...), each with its own health and a small bar in a row of icons under the
  boss bar. A broken part's weapon or skill stops for the battle, its mechanism with it (the
  supergun's shot, the Earth Worm's dives, the hovercraft's landings, the Supreme Commander's aura),
  and the body loses 30 % of the part's health. Only direct hits damage parts. Body health is lower to
  keep the fights about as long.
- Tap a part on the boss, or its icon, and every unit in reach targets it until it breaks (tap again to
  cancel); it is outlined in gold.
- The Iron Train's and the Bastion's self-repair now patches one broken part (its heaviest gun) back
  to half health, once.
- The Bastion's four autocannon turrets each cover their own quarter.
- Boss Rush pays 2 CP for each part broken.
- Fire and smoke at the breaks: hurt parts smoke and spark, broken ones burn until the end of the
  battle, the body burns under two thirds and a third of its health, flying bosses trail smoke, every
  fire flares when the boss dies and the wreck burns on. At most 8 fire points a boss (5 on Low).
- Radio lines when a main gun, a shield generator, a drone bay or a locomotive breaks; each boss's
  Guide tab lists its parts and what breaking each does.

### Prompt 10: Field Command 2.0 (the interface)

- New look everywhere, on one theme of tokens (colours, Barlow fonts, type sizes, spacing, touch
  size): flat graphite panels, square corners, 1 px borders, one amber main button a screen.
- Navigation: a top bar (title, rank and XP, coins, settings) and a rail of five: Home, Campaign,
  Operations, Army, Shop. Army has Deck, Equipment and Base.
- Home: the battle behind, the campaign card, today's challenges, the deck strip with 3D renders,
  and the match setup as four dropdowns (mode with its description, battlefield with its picture,
  difficulty, weather) beside DEPLOY.
- Campaign: chapters in three acts with pictures, progress, stars and bosses; each mission's
  briefing, stars, tiers, recommended power and rewards.
- Army: deck overview with role cover, filter chips and sort, cards with renders; equipment with gear
  cards and comparisons; the base screen at touch size.
- Detail pages for every card with the same five tabs, class averages and the gains told apart, and
  now for towers and base modules as well (from the base screen's info button).
- Shop with crate renders and coin pack pictures; "Ngụy trang" instead of "Skin".
- Results: the mission's or mode's name, the score by side, hints after a defeat with a button to the
  deck, CONTINUE or PLAY AGAIN, and doubling the coins as a Claim button.
- Battle HUD: full-name Attack / Defend, on/off switches for Auto buy and Support, cards with renders,
  names, CP, what is missing and a cooldown clock, the CP box with income and the supply penalty in
  words, the boss bar with health in numbers, phases and parts, one style for notices and radio.
- Settings: Text size (Normal / Large).
- Vietnamese: one name per battlefield (Đồng Tro, Cảng Thép, Đô Thành...), "xu" for coins, no
  English words left except the listed names.

<details><summary>72 commits</summary>

- `405a130` 2026-09-28 Siege sim: fortress data, gates, collapsing walls, super-gun, line in, swarm waves
- `fc7cef5` 2026-09-28 Campaign mission types: outpost, relief, evacuation, duel; boss health and flight; free strikes and income from stage events; reversed maps
- `bd7fa46` 2026-09-28 Vehicle detail levels: simplified one-material LOD1 per moving part, impostor atlas, level choice by screen size
- `034ff7f` 2026-09-28 Impostor cards lit with their own light loop (instanced draws get no per-renderer sun), alpha to coverage; LodShots renders cards through a camera of their own
- `09b279f` 2026-09-28 Siege maps: a fortress holding 45 % of the battlefield, towers on sized hardpoints
- `e3e2aab` 2026-09-28 Campaign structure: chapters, side missions, generals, HQ levels by chapter, rewards, save migration hooks
- `c46d79d` 2026-09-28 Campaign generator, part 1: the kit, the story (people, generals, chapters, boss files, timeline) and act I's 36 missions
- `c53a4f5` 2026-09-28 Prompt 8 groundwork: branch from data, elite price, boss part and burrow data, a damage log and reveal-all for the equipment lab, mine blasts count as mines
- `eba149f` 2026-09-28 Debug flags for big battles: -mb-crowd (two armies of fifty topped up in view), -mb-zoom=N; -mb-perf reports the detail levels and impostor draws
- `3cb56ba` 2026-09-28 Checkpoint replay in its own class, tested on a real mission session (both commanders, the player's orders and switches)
- `7d1b413` 2026-09-28 Impostor cards drawn only in the battle camera; decisions 5L (LOD and impostors) with the measurements
- `967b4fb` 2026-09-28 WIP (paused): Field Command 2.0 tokens and component files in progress, not yet verified
- `3d562a0` 2026-09-28 Siege and Defend sessions and HUD: gate goals, fortress loadouts, super-gun timer, wave preview
- `959b9cd` 2026-09-28 Campaign generator, part 2: act II (chapters 4-6, 36 missions)
- `ed93df7` 2026-09-28 Story campaign data: 108 missions (90 main, 18 side) in 9 chapters, generals, chapters, 869 texts
- `9fba490` 2026-09-28 Story systems: radio chatter, story camera pans, briefing and chapter cards, the Dossier, portraits, campaign page by chapter
- `bc4dcf4` 2026-09-28 Equipment (prompt 8 B, C, D, I): fit matrix from the data, new base types, lines and brands, proc coefficient, Twin Feed, cluster, module scaling, refund caps, trade-offs, last stands, save upgrade
- `5ce02e2` 2026-09-28 Siege and Defend: tests, first balance pass (Siege 3/5, Defend 4/5 on Normal)
- `3f08411` 2026-09-28 Leave the music folder's editor-made meta files out (not this branch's)
- `ca112f5` 2026-09-28 Fortress views: shield dome, rail line and train, runway and transport, searchlights, collapsing walls, gate doors
- `f2ccd2d` 2026-09-28 Campaign tuning rounds 1-3; duel HQs are demolition targets; the AI saves CP for a held outpost
- `75b902e` 2026-09-28 Prompt 8 A+E: armoured bulldozer, SP gun shoot-and-scoot, boss parts and five bosses
- `88a4193` 2026-09-28 Siege device checks (debug flags for the fortress set pieces); a smaller transport on the runway
- `3c8e680` 2026-09-28 Campaign tuning round 4 after the first five-seed run (80 of 87 measured missions at 5/5)
- `c1ead52` 2026-09-28 Duels are sieges of a base: the siege mix, the brigade's heavy battery, a 0.3 HQ, 30 minutes; the plaza relief at 2.2x
- `f45288d` 2026-09-28 Duels: the general's strength is his base, not his field army
- `f48561c` 2026-09-28 Campaign: radio panel clears the boss bar; briefing aside separator
- `48ed040` 2026-09-28 Prompt 8 H: elites on one footing, four new elites, an elite budget instead of a chance
- `a349b77` 2026-09-28 Campaign: DECISIONS section 4, the economy chart; test fixes
- `056f80f` 2026-09-28 Siege and Defend: stores in the walls' yard, gates on odd metres, breach-aware firing spots, balance, decisions 5S
- `aec7e88` 2026-09-28 Prompt 8 I/J: lab retune, risk lab, generated equipment docs, decisions
- `babc2a1` 2026-09-28 Field Command 2.0 foundation: token theme, Barlow fonts and licences, the UI kit, its preview screen and the UI checks
- `ea1c138` 2026-09-28 Card pictures from the 3D models: the render tool, 92 renders for 122 cards and their freshness test
- `48fccfa` 2026-09-28 UI screenshot tool and the kit preview at four screen shapes; stricter layout checks
- `c81b70d` 2026-09-28 Design document export: chapters, characters, timeline, generals, bases and tower cards, Operations, boss phases and parts, mission chapters and stages
- `ef44e5f` 2026-09-28 Hud.uss reads the accent from the tokens; decisions 10: card renders, screenshots, the checks and what the rebuild takes over
- `cae097f` 2026-09-28 Design document: the programme's sections (story campaign, multi-stage missions, Operations, bases and towers, Siege and Defend, tests still to run); stale texts updated
- `869948a` 2026-09-28 Card renders for the bulldozer, the five new bosses and the new elites
- `77f1328` 2026-09-28 Design document: card renders on the vehicle cards, generals' styles in Vietnamese
- `88263f7` 2026-09-28 Prompt 9 A+B: parts on every boss, on the general part rules
- `06e0876` 2026-09-28 Prompt 9 C+D: fire and smoke at a boss's breaks, the part row, the part order from a tap
- `8a9118a` 2026-09-28 Prompt 9 docs: DECISIONS section 9 (rules, every boss's parts, effects, interface, tests), CHANGELOG, ASSET_DEBT
- `cf82a0a` 2026-09-28 Field Command 2.0 screens on the kit: navigation, home, campaign, operations, army, vehicle detail, shop, settings
- `0934d78` 2026-09-28 LOD test: the far level may drop radio whips (under a pixel far away), so it may be up to a fifth lower, never taller
- `a98479c` 2026-09-28 Design document: prompt 9's part rules and break effects, a parts table under every boss (share of the body, what breaking it does, lock, self-repair, tip)
- `fe0e305` 2026-09-28 E6 base screen on the tokens: Screens.uss off the theme so it can restyle old classes
- `c5cdbcd` 2026-09-28 E7 match setup: the home's mode and map pickers as screens of their own in the checks and shots
- `ab1a136` 2026-09-28 The editor compiles without the UI Toolkit test framework: the screenshot tool and the UI checks sit behind MB_UI_TEST_FRAMEWORK, set when the package is present
- `3cc8e9e` 2026-09-28 Design review PDF for phases 1-9 (97 pages): the programme's chapters, boss parts, a phase 10 preview from the rebuilt screens
- `2e1fa0e` 2026-09-28 E10 result, pause and stage choice on the kit
- `05650c8` 2026-09-28 Play-mode smoke run for batch mode: the menu and a list of matches (Conquest, Siege, Defend, Boss Rush, a boss mission, a multi-stage mission), every error and exception reported
- `816bb67` 2026-09-28 Boss Rush easy to find: the weekly fortress and the boss rush head the Operations tab's right column; the card says ten bosses
- `4eb15e7` 2026-09-28 G battle HUD on the kit
- `fd77d45` 2026-09-29 Menu load and sound (test feedback 11D): the first open is built behind the curtain, one music player for the session, the lobby battle silent
- `0d82485` 2026-09-29 Towers and base structures get the vehicles' detail page (owner request)
- `b480b26` 2026-09-29 Rounds leave from the barrel as it is drawn that frame, and tracer streaks trail their round
- `cc8a967` 2026-09-29 H names: one Vietnamese name per map, no English left in the Vietnamese texts
- `fb6db92` 2026-09-29 In action clips show each vehicle's and support's special ability (test feedback 11D)
- `7c15ad5` 2026-09-29 Lobbed rounds leave down their barrel and bend onto where they land; missiles 10-20 % and drones twice as big
- `047fa03` 2026-09-29 Prompt 10 screens: decisions (10b), changelog, every screen's screenshots at the four shapes
- `8826b39` 2026-09-29 Decisions 11B: muzzles, projectile flight and projectile sizes (causes, measurements, fixes, sizes, tools)
- `2c2bd67` 2026-09-29 Play-test fixes for effects: bigger tank-round, bomb and cruise-missile blasts that stay sharp, a reworked flame stream, a held laser beam
- `477f9cf` 2026-09-29 Test feedback 11C: main guns fight the ground, missiles fly a third slower, magazine guns fire in streams
- `8e7d43c` 2026-09-29 Debris rotation renormalised each step: the drifting quaternion made TRS assert (47 errors in 40 s of Conquest)
- `7cafdaf` 2026-09-29 Effects tuning from the contact sheets: a heavier Iron Beam glow, tank-round fireballs that burn a fifth of a second, hotter and bigger flame balls, the impact sheet's own moments
- `07b47fa` 2026-09-29 In action clips checked with graphics: the jammer's view widened and its ring every second, the breacher's teeth on a slower cycle; RangeSceneTests; DECISIONS 11D
- `2ecd169` 2026-09-29 DECISIONS 11C: weapon targets, missile speeds, magazines and the measured DPS before and after
- `8865e15` 2026-09-29 DECISIONS 11A: final particle counts and beam widths
- `1559803` 2026-09-29 Combat comments: the leading magazine gun is a ground vehicle's main gun (an aeroplane's cannon takes turns)
- `290645e` 2026-09-29 DECISIONS 11D: the debris drift is fixed on lead/integration
- `1a92d6a` 2026-09-29 HUD screenshot demo: fall back to the starter supports when another test left the deck without any
- `c744f72` 2026-09-29 Design review PDF after phase 10 and the play-test fixes (100 pages): the new screens and HUD, names from the data, magazines and round speeds, section 16b on the fixes, the testing list

</details>

## v0.26.0: Bases as a loadout, roster cleanup, towers with sized slots and gear, multi-stage missions, Operations, new bosses' models and eight new maps

2026-09-28 18:30 · `14b174b`

<details><summary>33 commits</summary>

- `95b0c64` 2026-09-28 Sized hardpoints replace fortification points; tower cards and branches
- `ea76b3c` 2026-09-28 Base layout rules for the base screen: slot mapping, fitting, gaps, saving
- `28477b9` 2026-09-28 Tower roster: new towers, merges, branches, utility modules, counters
- `9bd8912` 2026-09-28 Tower equipment: Weapon, Structure and Systems slots per tower type, tower lines, fit, crates
- `92cbfec` 2026-09-28 Tests for tower equipment: slots, fit, shared loadouts, caps, the five tower lines, crates, saves
- `6ac3d76` 2026-09-28 Base loadout screen: camp diagram, drag and tap placement, branches, gear tab
- `dde1100` 2026-09-28 Decisions for tower equipment (section 3D)
- `18704f7` 2026-09-28 Map builder: plan the keep's flak branch on the old Flakturm's ground
- `cb518b2` 2026-09-28 AI weighs defences by size and by what they can hit; drones on emplacements
- `8b9d260` 2026-09-28 Base screen: device fixes at 16:9 and 18.5:9
- `cfc0887` 2026-09-28 Base screen: utility slots come alive once utility modules exist
- `7dbd145` 2026-09-28 Base screen: compact outpost row, one placed count, decisions 3F
- `1fc9178` 2026-09-28 Phase 8 models: armoured combat bulldozer (D9R lineage)
- `67a6905` 2026-09-28 Multi-stage missions: stages, events, choices, checkpoints by replay, an allied commander and its betrayal, the play area
- `de4932f` 2026-09-28 Phase 8: rail supergun, its rail tractors and targeting station
- `7a6d70d` 2026-09-28 Phase 8: earth borer boss
- `74bfd7a` 2026-09-28 Phase 8: command airship boss
- `4cb20d0` 2026-09-28 Phase 8: landing hovercraft boss
- `2d10c26` 2026-09-28 Landing hovercraft: rub rail, crew doors, bollards
- `366bca2` 2026-09-28 Phase 8: supreme command boss
- `6713e9e` 2026-09-28 Phase 8: generic boss wreck pieces
- `86d69e9` 2026-09-28 Phase 8: Unity import metas for the new models; clean rebuild
- `2df12de` 2026-09-28 mb_phase8: drop unused imports, measured sizes in the docstrings
- `6389ca3` 2026-09-28 Tick budget: path finding spread over steps, commanders on different steps, enemy ceiling 48 in the big modes; the ally's own base; the measured default base
- `ccc87fb` 2026-09-28 Rail supergun: bed runs on under its two coupled tractors
- `6b8e340` 2026-09-28 Map builder: groundwork for battlefields laid out in world metres
- `e371f13` 2026-09-28 Eight new battlefields: Landing Beach, Hydro Dam, Capital, Silver Bug Launch Site, Salt Flats, Border Bridge, Swamp, Coral Isles
- `9f48725` 2026-09-28 Register the eight new battlefields in the game
- `c06436a` 2026-09-28 Map tests: routes from every drop zone on all twenty battlefields
- `3782c3e` 2026-09-28 Multi-phase bosses: the bar stops at each phase's mark, the boss transforms untouchable, then fights on stronger
- `8194005` 2026-09-28 Decisions 4M: the eight new battlefields
- `1052669` 2026-09-28 Operations mode (prompt 6): four tiers with Legend, scores and records, 18 weekly mutators on a 26-week rotation, one weekly reward ledger
- `85d56f1` 2026-09-28 The camera keeps to the play area and follows it as it opens; decisions for Operations (6) and the growing battlefield

</details>

## v0.25.0: Merge bases as a loadout and the roster cleanup (prompts 1-2)

2026-09-28 14:47 · `d119abe`

<details><summary>2 commits</summary>

- `1d8dcda` 2026-09-28 Bases as a loadout: HQ, fortification points, hardpoints, outposts
- `a60811a` 2026-09-28 Roster cleanup: merges, new vehicles and supports, balance

</details>

## v0.24.0: Round 6 (weapon turns, barrels, round models, impacts, railgun, bosses, Ka-52/Su-25, economy and rank discount, guide tab, music, minimap, loading, PDF)

2026-09-28 11:31 · `250a465`

<details><summary>5 commits</summary>

- `39529e4` 2026-09-28 Round 6, part 1: weapons take clear turns, rounds leave from the real barrels, slower guns, AA bursts, slower missiles
- `2f323ab` 2026-09-28 Round 6, part 2: own round models, impact kinds, railgun charge, boss deaths, new bosses, Ka-52 and Su-25, economy, music, minimap, loading
- `d9871fa` 2026-09-28 Metas for the new boss models and the music director
- `2ceeaef` 2026-09-28 Round 6, part 3: Guide tab for every unit, fire-support clips, touch fix after the deferred build
- `f8f54df` 2026-09-28 Round 6: review PDF rebuilt, progress notes, m13 retune, detail debug flag

</details>

## v0.23.0: Round 5 (armament, new vehicles, campaign depth, Defend base, Endless, Field Command menus, equipment rework, traffic, 300 m maps, HD models, design-review PDF)

2026-09-28 05:45 · `44c5380`

<details><summary>25 commits</summary>

- `0bb5759` 2026-09-27 Playtest fixes: deck slots keep their places, one currency, aircraft fly in and keep their wings, crash damage, strike safety, boss stays visible, weather eases in, economy and counter-buying
- `ef3508b` 2026-09-27 Menu colours by meaning and finished buttons
- `270b07d` 2026-09-27 Real armament: side-firing gunship, stealth, fighters that hunt aircraft, air-to-air missiles, flares, corrected ranges and sizes
- `1d785e1` 2026-09-28 New vehicles (sim, data, icons, notes), bigger bosses and a flying-saucer boss, an In action tab, flight effects
- `742e968` 2026-09-28 Campaign enemy keeps pace with the arsenal and calls reinforcements; tracked models for turtle tank, BMPT, sapper
- `8fcdbcd` 2026-09-28 New mission goals (hunt, recon, protect, shoot down), six new missions, Defend as a real base, Endless mode, eight new models
- `dd9f3c0` 2026-09-28 Remove the 40 mm grenade launchers from the jeep, engineer, jammer and mine layer models
- `3fe8b1b` 2026-09-28 Traffic rules: lane map, no-park doorways, yielding and routes round parked hulls
- `5694a7a` 2026-09-28 Gear engine in the sim: stat lines, weapon copies, status effects and trait hooks
- `0a2d892` 2026-09-28 Menus restyled "Field Command" (flat, tactical) after the user found the glossy menu dated
- `3821070` 2026-09-28 Flat battle HUD shapes, square rarity frames, settings values off amber
- `46a9f9e` 2026-09-28 48 equipment pictures for the gear rework (base types and special modules)
- `ac176da` 2026-09-28 Equipment affix model: base types, sub-stats, traits, brands, Optics slot and save migration
- `9b65351` 2026-09-28 Proc words over vehicles in battle and the gear style block
- `630ef83` 2026-09-28 Checks for every remaining trait, module and set; thermal sight share; trait choice API
- `b22e5c3` 2026-09-28 Look for a missing gear picture once; expose blocks left and burning for views
- `0ef45ef` 2026-09-28 Progress: equipment rework merged, loot boxes kept, what is left to do
- `1fa84e1` 2026-09-28 WIP: Gate token, wider fortress, anchored defences, traffic scenario tests
- `f00c1fe` 2026-09-28 Traffic: a group bound for one place and units holding in the open are not sent away
- `b1d5970` 2026-09-28 Battlefields half as big again (300 m), denser, the country going on past a marked boundary, bigger houses, sharper High shadows
- `fa38ecc` 2026-09-28 m13 rebalanced for the bigger fortress map: siege buying mix, no extra waves, more time
- `e700281` 2026-09-28 Design-review document generator: game data export test and HTML/PDF builder
- `1f900f2` 2026-09-28 Progress: traffic, bigger battlefields and the review document
- `42834ff` 2026-09-28 High-detail models for High graphics: the twelve most-seen vehicles
- `31454ab` 2026-09-28 Design-review PDF: readable equipment lines, image cache, current edition in Docs

</details>

## v0.22.0: Mobile menu layout, vehicle detail page, equipment pictures

2026-09-27 22:10 · `7ac15a6`

<details><summary>1 commits</summary>

- `69e180c` 2026-09-27 Mobile menu layout, vehicle detail page, equipment pictures with rarity frames

</details>

## v0.21.0: Arsenal (card ranks, equipment 6+1 slots, crates with odds and pity, gems), device-check fixes

2026-09-27 21:17 · `829a296`

<details><summary>3 commits</summary>

- `a30df89` 2026-09-27 Arsenal: card ranks 1-10 (coins and blueprints, +5% health and damage a rank, +5% strike damage), equipment per branch (six slots and a special module, white to gold, levels, caps, always-successful merging with refunds), crates (battle, silver, gold, legendary; odds and pity shown before buying or opening), gems with a test-build store, a battle crate for each of the first five wins a day, a silver one for a mission's first clear, three ad crates a day; upgrades applied to the player's vehicles and strikes in the simulation; tests never write the real profile
- `5ca94bd` 2026-09-27 Docs: progress for the siege playtest round and the arsenal; release checklist gains the gem store switch
- `98e4868` 2026-09-27 Device check fixes: compact brand strip and dock labels on the narrow main page, arsenal dock buttons sized to fit, crates tab without the empty detail pane, parachute canopy single-sided and about 1.3 vehicle lengths across, placeholder ads in the menu (arsenal ad crates)

</details>

## v0.20.0: Menu taps and scene curtain, siege AI and fortress buildings, in-place reload with ammo gauge, stuck fix, AI waves and role-mix buying, air drops, falling shells, jet trails, audio cleanup, smaller aircraft

2026-09-27 20:51 · `4080802`

<details><summary>7 commits</summary>

- `89ce098` 2026-09-27 Menu taps that land (fire on release within a finger's slop, whoever holds the pointer; no more taps lost to scroll views), a fixed card-detail pane so deck cards stop jumping under the finger, and a black curtain with a loading screen between scenes (fade out with the sound, build behind black, fade in after warm-up); editor clicks count without Game view focus
- `f49dba3` 2026-09-27 Artillery and siege guns shell known defences from outside their reach (firing-spot solver, defences before the mission structure); fixed defences stay known once seen, siege attackers start with the fortress plans; empty magazines reload in place standing still (3x at home or a supply vehicle) with an overhead ammo gauge and reload bar; smaller aircraft (helicopters ~1.5x a tank), tougher helicopters, fortress AA toned down; bigger fortress gun impacts without screen flash
- `e4e4213` 2026-09-27 Stuck check measures progress towards the waypoint (a hull edging back and forth against a corner passed it for ever: 261 shakes a battle, now about 30); arrival contagion near a crowded goal; an unreachable guard post moves to where the hull can stand
- `f28ea93` 2026-09-27 Reinforcements are flown in: a transport passes over and the vehicle comes down under a parachute onto its landing point (landing and elite roll decided when bought; delivery 3.5 s); aircraft fly in from the map's edge. Audio: the interface beep for enemy strikes is gone, barrages and heavy shells whistle down where they land instead; points taken or lost come over the radio instead of puzzle chimes; the fortress siren fades with distance
- `574fcc8` 2026-09-27 Fire support is seen coming: every barrage round is aimed a moment ahead and falls out of the sky from its guns' side onto the spot it hits; smoke shells come down before the cloud. Jets trail vapour and a hot exhaust, with wingtip vortices in hard turns; strike jets' trails sized to the aircraft
- `49682be` 2026-09-27 Siege: 14 fortress buildings per map (barracks, stores, offices, workshops) placed clear of the attack lanes, each paying the attacker 2-6 CP when knocked down and coins at the end; the attacking AI shoots them up when nothing military is in reach; a bigger purse for the attacker (34 CP, 1.8 income, supply 40, 20 CP a stage) and a leaner defender
- `8399ac5` 2026-09-27 AI in waves: reinforcements gather at a staging point and go forward in threes instead of one by one; the line stops at the edge of known defences' reach until most of it has gathered, then goes in together; remembered defences are not contact (seen-now vs known masks); purchases follow a role mix per stance (a siege attacker brings more artillery), then counters

</details>

## v0.19.0: Editor Debug Flags window

2026-09-27 19:31 · `8eeba49`

<details><summary>1 commits</summary>

- `ac358ba` 2026-09-27 Editor: Machine Brigade > Debug Flags window, so the development switches (start straight into a mode, map or weather, test views, switch-offs) work in Play mode without a command line

</details>

## v0.18.0: Launch points, directional armour, smarter fire, night lighting, Defend mode, challenges, track marks and felled trees, screen flash, AI review, catch-up, bigger bombing blasts

2026-09-27 19:23 · `30199a8`

<details><summary>7 commits</summary>

- `38acb95` 2026-09-27 Armour by facing (side 1.25x, rear 1.6x), smarter fire (no overkill for heavy weapons, value and threat targeting, artillery bracketing), screen flash on huge blasts, heavy guns for the Doomsday Train, names for the new defences and the elite Grad
- `e646ca6` 2026-09-27 Defend mode: hold three dug-in sectors against the enemy's Breakthrough (the Assault rules with the sides swapped)
- `b39c517` 2026-09-27 Challenges: Heroic and Iron tiers for every mission, each mission's own third star (no strikes, no aircraft, kills), and a weekly fortress whose broken rings stay broken all week
- `e51ed3d` 2026-09-27 Hulls knock down trees, bushes, hedges and fences (they topple the way the vehicle drove, then sink away); track marks behind every ground vehicle, fading over half a minute
- `ec02f73` 2026-09-27 Night lighting: blasts, gun flashes and fires light the ground, illumination flares drift down over the fighting
- `1febeb1` 2026-09-27 m16 player income 1.55 after the Doomsday Train's heavy guns; campaign 17/17 at 5/5
- `f59ecc9` 2026-09-27 AI review: artillery backs off along the map's edge (EscapeRoute) and only from ground threats, crowds step aside to a random open spot, nobody targets invulnerable bastions, artillery sees 30 m; catch-up for the losing side in quick modes (underdog reinforcements up to +50%, kill bounty by the odds); bigger bombing blasts drawn to size

</details>

## v0.17.0: Rounds leave from the real launchers, twin guns fire together

2026-09-27 18:29 · `fdf975d`

<details><summary>2 commits</summary>

- `84f67b2` 2026-09-27 Rounds leave from the real launchers: pods and rails on both sides in turn, a random tube across a launcher face, only launchers round the slot's own muzzle; twin guns fire both barrels together; L/R barrels recognised and measured from their meshes; fixed defences block routes; AA ignores fixed defences when taking cover; half the hit flash on aircraft
- `d275752` 2026-09-27 Only defences a mode puts down block routes (map fortresses keep their checked lanes); campaign back to 17/17 at 5/5

</details>

## v0.16.0: Straight direct-fire shells, no roof guns on the twin turrets

2026-09-27 18:02 · `7dc3ad5`

<details><summary>1 commits</summary>

- `870dedd` 2026-09-27 Direct-fire shells fly straight down the barrel whatever their blast size (only artillery and howitzers arc); no roof gun on the camp bastion or the coastal turret

</details>

## v0.15.0: Rarer, deadlier aircraft; neutral point towers; defences that burn and stay; bombs under the bomber; ground units ignore circling aircraft

2026-09-27 17:51 · `ba93704`

<details><summary>3 commits</summary>

- `50460c6` 2026-09-27 Air power rarer and stronger: aircraft cost about 1.45x, six at most per side, aircraft and bombers hit harder, anti-air 1.4x to stay the counter; ground units no longer chase circling aircraft; bombs land under the bomber; neutral watchtowers on capture points; defences burn, cook off and stay as ruins; twin guns fire barrel by barrel; a gentler hit flash
- `2c44846` 2026-09-27 Defences do not flash white; the camp bastion's roof carries twin flak instead of SAMs launched from its roof; -mb-towerwatch and -mb-bastion device checks
- `4b61532` 2026-09-27 Balance with rarer aircraft: player-like test decks, the last point is always attacked, committed attacks press on 60 s, m10 enemy economy eased; campaign 17/17 at 5/5

</details>

## v0.14.0: Damage you can see, two-weapon vehicles, air war, 200 m maps, three-stage siege with fortress art, Attack/Defend rework, Breakthrough, recorded audio

2026-09-27 16:41 · `e508a29`

<details><summary>12 commits</summary>

- `6282482` 2026-09-27 Weapons take turns and machine guns fire in bursts; guns leave aircraft to anti-aircraft; long shots can miss
- `5634a0f` 2026-09-27 Aircraft at believable sizes, jets and bombers faster and higher, rotors that sweep instead of strobing
- `c9d9e69` 2026-09-27 Damage shows on the hull; cluster rockets for the elite MLRS and a new elite Grad; elite weapons
- `1221030` 2026-09-27 200 m battlefields filled with more to see; Siege rebuilt as a three-stage fortress assault
- `f8b9487` 2026-09-27 Capture modes protect each camp: indestructible bastions, home-zone repair and spawn grace, no strikes on a camp, a comeback behemoth
- `1c9938f` 2026-09-27 Fortress defences for the multi-stage siege: heavy turret, flak tower, missile battery, shield generator
- `10f0adf` 2026-09-27 Blasts and smoke screens stop popping over each other: a fixed draw order per effect layer, flipbook smoke screens that cover what burns inside, blasts in front drawn over them
- `f2c3c14` 2026-09-27 Fortress art in the siege: heavy coastal turrets, flak towers, missile batteries and shield generators; spawn bastions on the heavy turret; fortress interior laid out so every piece stands
- `4c3ce9b` 2026-09-27 Real recorded sound effects: 63 licensed OGGs in Resources/Audio, with credits
- `d09f638` 2026-09-27 Attack and Defend stances that play differently: Defend holds the front point, never falls back and digs in (hull-down, -20% damage); Attack goes for the weakest-held point; watchtowers on captured points; Assault rebuilt as a three-sector Breakthrough; lone artillery closes to range and kites
- `6393a5b` 2026-09-27 Recorded battle sounds (Sonniss GDC bundles and CC0, credited in Resources/Audio/CREDITS.md) with a proper mix: variants without repeats, voice limits and priorities, distance muffling, speed-of-sound delay for far blasts, ducking under big blasts, fires crackling near the view
- `f1139d5` 2026-09-27 Hit feedback (white flash, hull rock, damage trail on the health bar); hull-down only against direct fire; campaign at 17/17 missions 5/5 with the new AI, maps and fortress; -mb-smokescreen device check; progress notes

</details>

## v0.13.0: No stutter, tougher vehicles and slower economy, real artillery, Grad, ATGM carrier, APS tank, collapsing buildings, unstuck AI

2026-09-27 14:39 · `c7edbdd`

<details><summary>8 commits</summary>

- `3e446e0` 2026-09-27 No more stutter from the camera and blasts; all cards unlocked for testing; menus drag with the mouse
- `d293b44` 2026-09-27 Vehicles no longer stall against walls, the map's edge or each other; anti-aircraft follows the armour
- `4f09b89` 2026-09-27 Tougher vehicles, a slower economy, buildings that collapse in their own dust
- `d1b7425` 2026-09-27 Artillery that reads as artillery, plus grad_truck, atgm_carrier and aps_tank
- `4c6cff1` 2026-09-27 Thicker dust when a building comes down; the flattened remains sink out of sight; -mb-demolish device check
- `2385422` 2026-09-27 Artillery that reads as artillery, a Grad truck, an ATGM carrier and an active-protection tank
- `74f97be` 2026-09-27 Campaign kept at 5/5 with the new cards in players' decks (m10, m13 income); shake setting hidden while shake is off
- `6d3d57f` 2026-09-27 Progress notes for the stutter, toughness, artillery and collapse round

</details>

## v0.12.0: Smooth blasts, map outlines and minimap, phone UI, line of fire, barrel elevation, scale pass, map kit on every battlefield

2026-09-27 13:06 · `315074f`

<details><summary>14 commits</summary>

- `29f1032` 2026-09-27 Smoother battles: no blast lights, one big blast per death, calm crowds, upkeep instead of an army cap
- `2719e5f` 2026-09-27 Barrels rise to fire; direct fire no longer goes through buildings and rock
- `f3ca406` 2026-09-27 Every battlefield has its own shape; the minimap shows the real map
- `f1baab9` 2026-09-27 Battle HUD made for phones, responsive on every screen shape; Editor ready; AI goes for crates
- `6f196c4` 2026-09-27 Second visible weapon on 18 single-weapon models
- `b3f3fa4` 2026-09-27 Aircraft drawn nearer their real size, ground vehicles a little smaller, houses and buildings 15 % larger
- `22c22ed` 2026-09-27 Every combat vehicle carries at least two weapons; aircraft flights no longer hover off their rally point
- `ba12234` 2026-09-27 Scale is visual and hull only: hit radius stays as given; m03 gets 19 min, the Doomsday Train 6400 hp
- `5a2df2e` 2026-09-27 Menus for phones: Be Vietnam Pro everywhere, icon mode tiles, deck card details with weapons
- `5a0093a` 2026-09-27 Map kit: battlefield dressing props (22 models)
- `041d30e` 2026-09-27 Lighter scenery: bay dressing budgeted, shadowless and mostly rock; countryside scatter stays outside the square; lighter small-arms impacts
- `54ab427` 2026-09-27 Map kit on every battlefield: wrecks, craters, trenches, field camps, checkpoints, pylons and poles; jungle bridges
- `49d0256` 2026-09-27 Mobile Fortress 9000 hp (m09 stalled to the time limit on the dressed Frostpeak); map kit noted in the generator header
- `b395c58` 2026-09-27 Shop cards line up: two-line name box, price pinned to the bottom, taller cards; the items note no longer lingers on other tabs; progress notes

</details>

## v0.11.0: The big expansion (collisions, odds AI, abilities, elites, statics, counters, items, doctrines, events, daily challenges, Siege and Boss Rush, four maps, campaign m00 and m13-m16, optimisation)

2026-09-27 09:35 · `a0aadd6`

<details><summary>29 commits</summary>

- `9a65c86` 2026-09-27 Vehicles collide as hulls and steer round each other
- `2682d52` 2026-09-27 AI weighs the odds: outmatched armies fall back and wait for reinforcements
- `835d25e` 2026-09-27 Abilities, elites, fixed defences and a third wave of vehicles
- `e78a02f` 2026-09-27 Counter system: who beats whom, proven in skirmishes and shown on the cards
- `d41f0d0` 2026-09-27 Items bought with coins: MOAB, cluster bombs, airdropped armour and more
- `5ed79c8` 2026-09-27 Art: seven elite enemy units (refurbished, up-armoured base vehicles)
- `e2ba3a5` 2026-09-27 Battle events: supply drops, bomber raids and weather that turns
- `ab41486` 2026-09-27 Third vehicle roster: twin tank, siege tank, heavy MLRS, ballistic TEL, siege mortar, two projectiles
- `ad5a7bd` 2026-09-27 Art: support vehicles, FPV drone, mine and air-dropped crates
- `1f10d5b` 2026-09-27 Doctrines: pick an army-wide edge before each battle
- `5fd38a2` 2026-09-27 Air art: fighter jet, tank buster, recon drone, heavy attack heli; drone mothership and nuke train bosses; icbm
- `b7dda67` 2026-09-27 Siege and Boss Rush modes
- `4e24295` 2026-09-27 Maps: Ember Ridge, Jungle Pass, Skyhold Airbase, Metro City; Siege for all twelve
- `2536921` 2026-09-27 Doomsday launch countdown; animated erector, searchlights, shields, elite bars
- `db8eb10` 2026-09-27 Siege base kit: six static defences and ten fortress props
- `95d21d5` 2026-09-27 Flipbook fire, smoke and fireballs; far more debris
- `af8a771` 2026-09-27 Siege: the command HQ is a hardened fortress core (4x health); siege tests on real fortress maps
- `c0c08cb` 2026-09-27 Menu colours for the volcanic, jungle and urban battlefields
- `89a9570` 2026-09-27 Trail smoke puffs grow less: fill back near the old budget
- `730891a` 2026-09-27 Theme art: volcanic, jungle, airbase and city props (28 models)
- `88e9152` 2026-09-27 Items that do no damage pulse instead of exploding: EMP and shield-dome rings, dust on airdrops; EMP skills ring too
- `06b7437` 2026-09-27 Effects director keeps the catalog for item pulses (fix build)
- `c52a900` 2026-09-27 Campaign: boot camp and four new missions; balanced with the deck a player really has
- `ef82f9c` 2026-09-27 War drums for boss fights, vibration, colour-blind team colours
- `165eeb3` 2026-09-27 Daily challenges: three a day for coins
- `92f08e6` 2026-09-27 Lava without the grid showing through; battlefield towers cut to 62% height so they do not hide the fight
- `2d7b430` 2026-09-27 Performance: prewarm only what a battle can field; lighter city skyline; skill checks at 4 Hz
- `8dccd4f` 2026-09-27 Static batching for still map props; docs for the big expansion; hull and merge helper scripts in Tools
- `edf7083` 2026-09-27 measure_hulls: repo-relative model path, usage note

</details>

## v0.10.0: Campaign, bosses, free-to-play economy, new modes, eight battlefields

2026-09-27 01:06 · `d932007`

<details><summary>18 commits</summary>

- `1bd3d0d` 2026-09-26 WIP: game modes, campaign, economy, skins data, rewards and ads flow
- `4994bcc` 2026-09-26 Aircraft art: overhaul the strike jet, attack jet and drone
- `40646bf` 2026-09-27 Boss focus for the AI, no field repairs on bosses, campaign balance
- `56eefdf` 2026-09-27 New vehicles: howitzer, thermobaric launcher, IFV, heavy AA truck, titan tank
- `b86b767` 2026-09-27 Menu for modes, campaign and shop; procedural camo skins
- `e12871d` 2026-09-27 Five new vehicles: howitzer, thermobaric launcher, IFV, heavy air defence, Titan
- `07d8967` 2026-09-27 Premium supports: napalm strike and carpet bombing
- `5719385` 2026-09-27 Maps: Redrock Canyon, Whiteout Pass, Greenvale Farms, Rust Yard; richer Dunebreak, Frostpeak, Ironport
- `41e241d` 2026-09-27 Cinematic moments on the biggest blasts
- `caaae7c` 2026-09-27 Art: four boss models (behemoth, mobile fortress, armoured train, mega gunship)
- `97b28de` 2026-09-27 Four new battlefields on the menu: Redrock Canyon, Whiteout Pass, Greenvale, Rust Yard
- `aab2e41` 2026-09-27 Aircraft art: polish the helicopters and munitions, add the heavy and stealth bombers
- `34b1da6` 2026-09-27 Aircraft art: add the sky gunship, finish the premium aircraft
- `d9959bd` 2026-09-27 Runtime: spin Propeller_2.. pivots and load-test the premium aircraft
- `9ffa5a2` 2026-09-27 Ground vehicles: detail pass on all 14 units plus the civilian car and truck
- `9c39927` 2026-09-27 Campaign: every mission winnable again on the richer maps
- `e90854c` 2026-09-27 Premium aircraft in battle: heavy bomber, stealth bomber, sky gunship
- `b648bd3` 2026-09-27 Docs: campaign, economy, modes, eight battlefields; shorter Vietnamese name for Greenvale

</details>

## v0.9.0: UI redesign, new maps and weather, muzzle fire, settings and shadows

2026-09-26 21:20 · `8c33c9f`

<details><summary>7 commits</summary>

- `03183aa` 2026-09-26 Harbour models: containers, gantry crane, factory, rail wagons, dock and street props
- `8354413` 2026-09-26 Desert and snow map models: adobe town, oilfield, mesa, snowy village and radar station
- `8ad8086` 2026-09-26 UI redesign, graphics tiers, off-screen culling, muzzle fire and smoke
- `4092fa3` 2026-09-26 Keep the market stall's jars inside its 4 m footprint
- `eaf8544` 2026-09-26 Three new battlefields, map themes, and snow, sandstorm, fog and night weather
- `6bd5c17` 2026-09-26 Full graphics settings, shadows fitted to the view, research-driven performance
- `b1fcfe1` 2026-09-26 Docs: new maps, settings, shadows and the performance research

</details>

## v0.8.0: Air power, a real town, mountains, effects that never reset, full audit

2026-09-26 19:25 · `1b5592b`

<details><summary>9 commits</summary>

- `ebe3aa1` 2026-09-26 Add ten vehicles and aircraft; chunkier attack helicopter
- `00deeae` 2026-09-26 Town buildings, barriers, civilian vehicles and more tree species
- `54e0141` 2026-09-26 Effects that never reset, no slow motion, steadier frames
- `ecb88a4` 2026-09-26 New units, aeroplanes, a real town and a mountain range
- `b3b51a4` 2026-09-26 Crisp animated ground markings; mountains coloured and forested
- `7a82c71` 2026-09-26 Menu fixes: language applies at once, back key closes pages or pauses, readable card costs, Survival hint
- `67cbd9f` 2026-09-26 Audit fixes: simulation, AI, balance and map generator
- `f28e082` 2026-09-26 Audit fixes: effects, rendering, HUD, input and audio
- `b0fa4fb` 2026-09-26 Docs: milestone entry, perf switches, SmoothStep and fog notes, map generator

</details>

## v0.7.0: Auto-play commander, cleaner and bigger explosions

2026-09-26 17:08 · `7d2a531`

<details><summary>2 commits</summary>

- `9ed7dd2` 2026-09-26 Sparks as glowing points, and more fire: secondaries, burning debris, lingering fires
- `c57b703` 2026-09-26 Auto-play commander: the army fights on its own, the player steers intent

</details>

## v0.6.0: Visual overhaul fixes

2026-09-26 16:42 · `e0dbaa3`

<details><summary>1 commits</summary>

- `7163f16` 2026-09-26 Explosions without hard lines or claw streaks, and cheaper

</details>

## v0.5.0: Visual overhaul fixes

2026-09-26 16:23 · `5d3e449`

<details><summary>1 commits</summary>

- `d08eaeb` 2026-09-26 Notes: device test flags and headless balance check

</details>

## v0.4.0: Flicker fix, full roster with aircraft, Conquest with CP and strikes, menus, weather, terrain, explosions

2026-09-26 16:22 · `7727e7c`

<details><summary>10 commits</summary>

- `8e977f7` 2026-09-26 Fix vehicle flicker; add weapon mounts, aircraft, CP, strikes and Conquest
- `531df6f` 2026-09-26 Main menu, Conquest HUD, deck, strikes targeting and minimap
- `56feec8` 2026-09-26 Add APC, MLRS, AA, flame tank, aircraft, munitions and terrain models
- `f7fed2d` 2026-09-26 Conquest AI saves for strong units and fields a mixed army; slower ticket drain
- `3cc7066` 2026-09-26 Use the new models: muzzles per mount, new materials, model tests, waves with the full roster
- `4bb5b43` 2026-09-26 Sounds for launches, flak, flamethrowers, jets, rotors, strike alarms and objective chimes
- `23d56ec` 2026-09-26 Weather, mountains and terrain props
- `fae5970` 2026-09-26 Noise-eroded fireballs, lit smoke, burning debris; bomb-line telegraphs; tap fixes; progress log
- `35f2c9a` 2026-09-26 AI flanks from alternating sides
- `0a77f5b` 2026-09-26 Fix issues from code review

</details>

## v0.3.0: Blender art, UI Toolkit HUD, surroundings, effects, audio and tactical AI

2026-09-26 14:19 · `6d69447`

<details><summary>6 commits</summary>

- `bc14eb1` 2026-09-26 Add Blender asset pipeline and first low-poly models
- `8bf96b2` 2026-09-26 Render Blender models in the match
- `bdab35c` 2026-09-26 Paint the battlefield like the reference
- `0798250` 2026-09-26 Rebuild the HUD with UI Toolkit in the reference style
- `b65e3f2` 2026-09-26 Surround the battlefield with countryside
- `9eb19f2` 2026-09-26 Battle effects, synthesised audio and tactical AI

</details>

## v0.2.0: Add playable combat sandbox

2026-09-26 12:28 · `90807b0`

Vehicles-only battle on the Ashfield sandbox map, running on the Android
emulator.

- Simulation: fixed-step world, validated commands (move, attack,
  attack-move, stop, retreat), team vision, grid A* with formations and
  stuck detection, projectiles with travel time, damage table, splash,
  delayed explosions with terminating chain reactions
- Data-driven balance and map JSON with a comment-tolerant reader
- Sandbox mode with enemy waves and reinforcements, placeholder AI
- Voxel models drawn in code, greedy mesher, debris chunks and rubble
- Pooled effects: five explosion tiers, tracers, scorch marks, burning
  wrecks with tossed turrets, physics debris, camera shake, slow motion
- Touch controls (tap, double tap, box select, pan, pinch) and HUD
- Hand-written URP shaders; scene generated from code
- 38 EditMode tests; progress and known limitations in Docs/PROGRESS.md

## v0.1.0: Set up Machine Brigade Unity project

2026-09-26 11:44 · `ed9e2f9`

Unity 6000.6.3f1 URP project for a vehicles-only 3D mobile tactics game.

- Game plan in Docs/GAME_PLAN.md; earlier RTS plans kept as reference
- Player settings applied from code (bundle id com.winka.machinebrigade,
  landscape, IL2CPP ARM64) and command-line Android/iOS build scripts
- Pure C# simulation assembly with a fixed-step SimClock and EditMode tests
- Emulator images denied Vulkan so they fall back to GLES3
- Tools/run-android.sh installs and launches the dev APK
