# Progress

Short record of what each milestone delivered and what is still missing. Newest first.

## 2026-09-27: Smooth blasts, map outlines, phone UI, line of fire, scale pass, map kit

The user asked for:
- smooth explosions, with a small shockwave and one big blast plus small ones;
- no hard army cap;
- a minimap with each map's own shape and its terrain;
- a phone-friendly UI with less text, redone menus, centred labels and better fonts;
- AI that cannot shoot through buildings or rock;
- richer maps;
- no jitter when vehicles touch;
- barrels that elevate when they fire high;
- at least two weapons per vehicle, listed in its description;
- wrecks that clear sooner;
- no doubled explosions;
- a project ready to play in the Unity editor, responsive on every device;
- sensible sizes: aircraft larger, tanks smaller, houses larger.

### Done

**Explosions**
- Point lights are gone from blasts. A fake ground light (an additive disc) replaces them, which removed most hitches.
  - Emulator hitches in the same battle: 203 → 68. This is a relative figure, not phone performance.
- Blasts from Medium up get a small air shockwave ring.
- A vehicle death plays one quick kill pop, then its own big blast.
  - Large wrecks cook off in a chain of small pops, not repeated big blasts.
  - This fixed the doubled or "reset" explosion: the old code played a Medium blast, then the delayed death blast, then a full cook-off chain.
- Wrecks burn for 12 s, stay 17 s and sink in 3 s.

**Economy**
- The hard cap is replaced by upkeep. Past the supply line (1.5 × the old cap), income falls, to half at twice supply (never below 25 %).
- Only a safety limit of 44 vehicles remains.
- The deck bar shows the income and the upkeep cut.

**Movement and combat**
- Contacts are calmer:
  - avoidance fades in and out;
  - there is a heading dead band while cruising;
  - braking is shared by push;
  - scripted units and bosses have right of way;
  - tanks settle at their final point.
- Ground vehicles are drawn through a velocity-predicting filter.
- Heading swings in a whole AI battle: 1426 → about 150.
- Line of fire:
  - buildings, rock, wrecks and walls that block fire are rasterised into a 1 m `CoverGrid`;
  - direct-fire weapons check it before targeting and firing;
  - a shot that is blocked anyway hits the wall;
  - vehicles close in until they are clear;
  - indirect weapons (mortars, artillery, bombs, drones) fire over.
- Barrels elevate: every model has an `Elevation` pivot on its gun, mortar or launcher group, which pitches to the ballistic angle for the current target.
- Every combat vehicle has at least two weapons. There are 18 new secondaries, with new models where needed (grenade launcher, guided bomb, drone gun, ATGM post).
- The tactical AI remembers each enemy it has seen, with a half-life of 45 s, and picks up nearby crates.

**Maps**
- Each map has its own outline, carved per map by `Tools/maps/boundary.py` inside the 160 m square: valleys, bays, a canyon rim.
  - Nothing drives or builds past it.
  - The outside is terrain with sparse, shadowless rock and trees.
- The minimap is the painted terrain, cut to the outline and turned to match the camera, with haloed blips.
- The map kit (22 new models) dresses every battlefield (`warzone` in `build_maps.py`):
  - wrecks with their craters in no man's land;
  - foxholes, trench lines, barricades, a wreck and a road checkpoint at every objective;
  - a field camp (command tent, camouflage nets, supply piles, a fuel bladder, a radio mast) beside each camp;
  - per theme: telegraph poles, pylons, ruins, dead trees and anti-tank ditches;
  - low road bridges across the Jungle Pass fords.
  - Cover comes in equal numbers on both halves. Campaign spawns and routes stay clear, and reachability is still proven.
  - Craters and wrecks scorch the ground beneath them.
- Props may turn in 45° steps; a diagonal prop keeps its bounding square as its footprint.

**Scale**
- `VehicleDef.Scale` resizes the model and the hull length and width; the hit radius is deliberately left alone, because scaling it upset the balance.
  - Aircraft are 1.05–2.0× larger.
  - Non-boss ground vehicles are 0.85×.
- `PropDef.Scale`: 25 buildings are 1.15× larger. The command HQ and the vehicle hangar are unscaled, so the fortress still fits.

**UI**
- Be Vietnam Pro for text (full Vietnamese coverage); Barlow Condensed stays for numbers.
- Battle HUD:
  - glass panels and icon-only tools;
  - a commander rail;
  - a selection card only when something is selected;
  - weapon chips and short names.
- It adapts to the screen shape (`MatchFor` from 4:3 to 16:9 and wider).
- Menus: icon mode tiles with one line for the chosen mode. Deck cards open a detail panel with every weapon (kind, calibre, targets, ammo).
- Button labels no longer end in an ellipsis.

**Editor**
- `EditorStartup` makes Play always start from the game scene (`Sandbox.unity`). It also opens that scene in a fresh session and adds the menu item *Machine Brigade → Open Game Scene*.
- Batch test and build runs use a mirrored worktree (`MachineBrigade-runner`), so the project can stay open in the editor.

**Balance** (five seeds per mission, auto-commander)
14 of 17 missions win 5/5; m02, m09 and m10 win 4/5. Before this round, 12 were 5/5 and m03 and m16 only 3/5.
The map kit first dropped m09 (the Mobile Fortress on Frostpeak) to 2/5, with stalls at the time limit, so the boss went from 10,500 to 9,000 hp.

### Known limitations
- **Ads:** still the placeholder; a real SDK needs the user's AdMob account.
- **Real phones:** nothing has been measured on one. On the emulator, Ashfield runs at about 23 fps with 15–24 vehicles (26.6 before the bigger buildings and the outside scenery). Use it only to compare builds.
- **Bridges:** they are visual. Vehicles cross at the ford underneath, and the deck is level with the ground.

## 2026-09-27: The big expansion (everything from the suggestion list, plus more)

The user asked for all of the earlier suggestions, and more:
- more vehicle variety: twin-barrel and longer tanks, artillery, long-range missiles with limited ammo that fall back to a machine gun;
- more aircraft;
- more debris and more realistic fire;
- units no longer driving through each other;
- an AI that holds its position instead of charging when outmatched;
- elite enemy units, a counter system and a rebalance;
- items bought with coins;
- a siege mode against a lit fortress, by day and by night;
- an optimisation pass once all of that was in.

### Done

**Collisions and AI**
- Hulls collide as capsules sized from each model's measured hull.
  - Drivers look ahead: they follow a friend going the same way, steer round anything parked or hostile, and pass oncoming traffic on the right.
  - New vehicles spawn on free ground.
  - Deep overlaps in a whole AI battle fell from 35 to 2 of about 200 contacts.
- The tactical AI weighs the odds (CP value × health, mobile units only).
  - Below 0.6 it falls back to a point it holds and waits for reinforcements. It attacks again at 0.95, or commits after 40 s so that dug-in defenders cannot stall it.
  - Buying is balanced: anti-air is matched to the enemy's aircraft, a core of ground units that can capture is kept, and high explosive is bought against demolition targets.
  - The main body no longer waits forever on vehicles that never finish a move.

**Abilities** (`AbilitySystem`)
- Limited ammunition: re-arm at home, or near an engineer; the AI sends empty launchers to re-arm.
- Engineers repair and re-arm the vehicles around them.
- EW jammers scramble missiles, drones and fire support aimed into their area.
- Mine layers lay mines, which the enemy sees only up close.
- Automatic skills: shield, repair, smoke, overdrive, barrage, flares, summon and EMP.

**Units**
- New ground vehicles:
  - twin-barrel tank, siege tank (203 mm), 300 mm rocket artillery, ballistic missile launcher, 240 mm siege mortar;
  - engineer, EW jammer, FPV drone carrier, mine layer.
- New aircraft: fighter jet, tank buster, recon drone, assault gunship.
- Seven elite enemy variants: refurbished models about 1.15× the base, black and gold with a red glow, gold health bars and skills. Deliveries turn elite at 10% on Normal and 25% on Hard.
- Six fixed defences: gun, AA and rocket turrets, bunker, howitzer pit, guard tower with a sweeping searchlight.
- Two bosses:
  - Hive Carrier: an airship that launches drone swarms.
  - Doomsday Train: raises its missile during a launch countdown.
- Boss phases on every boss: escorts called in, rage, bulwark shields and EMP pulses.

**Counters**
- Every vehicle has a class.
- `CounterTests` requires the counter to win twelve equal-CP skirmishes.
- Cards and the selection panel show "strong vs / weak vs".
- Defences are structures, so high explosive breaks them.

**Items, doctrines, events and daily challenges**
- **Items:** seven, bought in pairs for coins and carried into any battle: MOAB, cluster bombs, airdropped tanks, field repair, EMP, shield dome and a gunship on call.
- **Doctrines:** five, picked on the deck page.
- **Battle events:** supply crates to fight over, neutral bomber raids, and weather that changes mid-battle.
- **Daily challenges:** three a day, paid in coins.

**Modes**
- **Siege:** walls, gates, defences, a command HQ hardened 4×, floodlights, and fuel and ammo dumps that chain-explode. It works on all twelve maps' `_siege` variants.
- **Boss Rush:** four bosses in a row, with elite escorts.

**Maps**
- Four new battlefields:
  - Ember Ridge: volcanic, with lava rivers and a geothermal plant.
  - Jungle Pass: jungle, with a river, fords and a temple.
  - Skyhold Airbase: parked jets that chain-explode.
  - Metro City: urban, with a street grid, high-rises and lit windows at night.
- Three new themes.
- Every map has a Siege version.

**Campaign**
- An optional Boot Camp (m00) with timed tips, and m13–m16 built on the new content.
- Balanced with the deck a player really has at each point: 15 of 17 missions won in all five seeds, m06 and m11 in four of five.

**Effects**
- Flipbook fire, blasts and smoke: a Mantaflow fire loop, and procedural blast and smoke sheets.
- Mesh debris that bounces and burns, turret tosses, cook-off chains and textured scorch marks.
- Items with no damage (EMP, shield dome, airdrops) show pulses instead of blasts.

**Polish**
- War drums while a boss is on the field.
- Vibration on boss kills and cinematic blasts.
- Colour-blind team colours: blue and orange.

**Optimisation**
- Only the vehicles a battle can field are prewarmed.
- Metro City's skyline is limited to the ring the camera can see; before, it was 1M instanced triangles in 1631 batches.
- Static batching for map props that never move.
- Skill checks run at 4 Hz.
- Emulator measurements are relative only; see `PERFORMANCE.md`.

### Known limitations
- **Ads:** still the placeholder. A real SDK needs the user's AdMob account.
- **Real phones:** nothing has been measured on one. The emulator figures are for comparison between maps only.
- **Balance:** the counter targets and the campaign are tuned for the auto-commander; human play may need adjustments.

## 2026-09-27: Campaign, bosses, free-to-play economy, new modes, eight battlefields

The user asked for:
- a campaign with vehicles unlocked gradually, and bosses with cinematic moments (no veteran units carried between missions);
- a free game: coins after every match, a rewarded ad for double coins, skins and premium equipment bought with coins;
- more vehicles, aircraft and artillery, better bomber models and a detail pass on every model;
- more modes against the AI with difficulty levels (Deathmatch and others);
- more maps, with scenery that fits the terrain (rocks and scrub in the desert, forest in the snow).

### Done
- **Campaign "Operation Steel Fire".** Twelve missions over four battlefields, defined in `Resources/Data/campaign.json` and run by `MissionMode`.
  - Goals: capture, hold, destroy, escort a convoy, survive, kill a boss, intercept a train.
  - Missions can add waves, scripted convoys and boss routes, placed units, hardened demolition targets and their own army cap.
  - Each mission awards up to three stars, for winning, for speed and for losses.
  - Vehicles unlock as the campaign advances. Any card can be bought early with coins.
- **Bosses:**
  - behemoth (land battleship), in m06;
  - mobile fortress, in m09;
  - armoured train, in m12;
  - mega gunship (tandem rotors), in m03.

  Each boss has its own model, a boss health bar and a forced cinematic when it dies. The AI focuses its fire on the boss, and repair drops do not heal it.
- **Cinematic moments.** The biggest blasts trigger a short slow-motion moment with letterbox bars and the camera leaning in. There is at most one every 25 s, a boss death always gets one, and it can be switched off in Settings.
- **Free-to-play economy.** `PlayerProfile` is stored as JSON in PlayerPrefs `mb.profile`.
  - Coins and XP are paid after every match, and the result card offers a rewarded ad for double coins. `IRewardedAds` currently shows a 5 s placeholder in place of a real ad.
  - The shop has three tabs:
    - **Skins:** ten procedural camouflage patterns in the lit shader, previewed live on the menu battle.
    - **Premium:** coin-only cards.
    - **Unlocks:** campaign cards bought early.
- **Premium equipment:**
  - Titan super tank.
  - Heavy bomber: carpets twelve bombs.
  - Stealth bomber: three precision bombs with ultimate-tier blasts.
  - Sky gunship: side-firing 105 mm, 40 mm and 25 mm guns.
  - Napalm strike: leaves the ground burning.
  - Carpet bombing: flown by the heavy bomber model.
- **New vehicles:** IFV, 155 mm howitzer, thermobaric launcher (sets the impact area burning) and a twin-30 mm flak vehicle.
- **Quick modes against the AI**, each at Easy, Normal or Hard:
  - Conquest.
  - Deathmatch: first to 100 kills, or 12 minutes.
  - King of the Hill: hold the centre to 100 points.
  - Assault: take every point from a dug-in defender within 14 minutes.
  - Survival.
- **Eight battlefields.** New ones:
  - Redrock Canyon: desert canyon lanes, rock walls and an oasis market.
  - Whiteout Pass: a snow forest pass with a frozen lake.
  - Greenvale: hedgerowed farmland round a crossroads village.
  - Rust Yard: ruined industry and a marshalling yard.

  Dunebreak, Frostpeak and Ironport were re-dressed to fit their terrain: more boulders and cactus in the desert, more forest and snow rocks in the snow, a denser harbour.
- **Art (Blender agents):**
  - four boss models;
  - the strike jet, attack jet, drone, helicopters and munitions rebuilt with a fixed-wing kit;
  - three premium aircraft;
  - a detail pass on all 14 ground vehicles plus the car and truck: real track runs with sprockets and idlers, skirts, stowage, hatches and muzzle devices.
- **AI fixes found by measuring the campaign over eight seeds per mission** (94 of 96 won, up from 77):
  - The army now shoots demolition targets. Before, shells only splashed them, so a target with no enemy beside it never fell.
  - The main body no longer waits forever on vehicles that never finish a move: vehicles jostling for a slot, and anti-aircraft vehicles that hold short near tanks.
  - Hold missions leash the army to the point.
  - Missions raise the player's army cap to 30, because units placed at the start used to fill Conquest's 24 and no reinforcements ever came.

### Known limitations
- Ads are a placeholder. A real SDK (AdMob with test IDs, then the user's account) is still to be wired to `IRewardedAds`.
- There is no screenshot or clip sharing yet. It needs a native share plugin.
- Campaign balance is measured with a late-campaign deck (`CampaignTests`). A player still on the starter deck will find missions 5 to 12 longer.
- m06 and m12 are each lost once in eight seeds by the auto-commander, so the player may need to step in.
- Nothing new is measured on a real phone yet. The emulator checks were functional only.

## 2026-09-26: Command-console UI, three new battlefields, weather, settings, shadows

The user asked for:
- smoothness taken from how other games optimise;
- a full UI redesign with solid colours instead of see-through panels with outlines;
- more maps and weather;
- then muzzle fire and smoke for vehicles and aircraft;
- then more shadows, re-run performance research and proper settings.

### Done
- **UI redesign** (Stitch design system, Barlow Condensed and Inter):
  - Every panel is solid with a header strip, and buttons are tactile.
  - Selected states are solid amber; disabled states are solid greys.
  - The menu has numbered sections (mode, battlefield, difficulty, weather).
  - The result and pause cards have coloured heads, and the hint sits on a pill.
- **Maps.** Generated by `Tools/maps/build_maps.py`, each checked for reachability and played AI-versus-AI in the tests.
  - Dunebreak (desert): a refinery with exploding tanks and towers, an oasis market town and a pumpjack oil field.
  - Frostpeak (snow): a log-cabin village, a radar station and a lumber camp in pine forest.
  - Ironport (harbour): quays with gantry cranes and container yards, factories and a rail yard of tank wagons.
- **Art.** 25 new models from two Blender agents.
- **Map themes** (`MapTheme`):
  - ground palette, trees and clutter;
  - mountain colours;
  - water: river, frozen river or sea;
  - scenery houses and clear-day haze;
  - model grass colour and minimap colour.
- **Animated props:** radar dishes spin and pumpjacks rock.
- **Weather:**
  - Snow: drifting flakes.
  - Sandstorm: dust clouds, grit and an orange haze.
  - Fog: dense fog with low wisps.
  - Night: moonlight, lit windows and fires lighting the field.
- **Muzzle fire and smoke** (`MuzzleFx`) for vehicles and aircraft:
  - an orange core and a flame tongue on the barrel, with muzzle-brake side jets;
  - sparks and light gunsmoke that bursts out and hangs;
  - ground dust from cannons, back-blast from launchers, and a flicker for every machine-gun round.
- **Settings page** (scrolling, segmented), in the style of large mobile games:
  - **Graphics:**
    - preset: Auto, Low, Medium or High, becoming Custom when changed;
    - shadows, resolution, anti-aliasing;
    - frame-rate cap: 30, 60, 90 or 120, display-paced;
    - battery saver, glow level, brightness;
    - scenery density and effect detail.
  - **Gameplay:** screen shake, camera speed, interface size, FPS counter.
  - **Sound and language.**
- **Shadows:**
  - The single shadow map is refitted to the view every frame, so shadows are sharper zoomed in and cover the whole screen zoomed out.
  - Soft 4-tap filtering from Medium.
  - Tree shadows from Medium; clutter shadows on High.
  - Blob shadows when shadows are off.
- **Performance:**
  - Effects skip their particles off screen.
  - Particle screen size is capped.
  - Low bloom uses quarter resolution, four passes and the dual filter.
  - FSR 1 below full resolution.
  - Menus and pause draw every other frame until touched.
  - Swappy on release builds.
  - The frame-rate governor steps between 30, 60, 90 and 120.
- **Tools:** `EffectShots` renders effects frozen at chosen moments for tuning.

### Known limitations
- The emulator cannot judge performance. Real-device testing is still needed; see `Docs/PERFORMANCE.md` for Firebase Test Lab and Samsung Remote Test Lab.
- Not done yet from the research:
  - thermal scaling (Adaptive Performance);
  - pipeline-state warm-up;
  - a half-resolution particle pass;
  - tree shadow proxies;
  - a static shadow cache;
  - colour-blind mode.
- The refinery flare stack has a static flame model, not a live fire.

## 2026-09-26: Air power, a real town, mountains, effects that never reset, full audit

This milestone follows playtest feedback on four points:
- explosions and fires "reset" after a while;
- rings looked crude;
- unexplained stutter;
- buildings were illogical and repetitive, and the surroundings sparse.

The feedback also asked for:
- wrecks that stay (and later vanish);
- aircraft that fight as units and can be shot down;
- more vehicles;
- a full scan of the app for problems.

### Done

- **Effects that never reset:**
  - Explosions emit into a dozen shared particle systems. Before, pooled per-blast instances were cut short when a new blast needed the slot.
  - Fires burn in shared systems with no slot limit: they flare, die down and smoulder.
  - Wrecks burn for 45 s, stay about 75 s, then sink away.
  - Shot-down aircraft blow up in the air, fall with their momentum and explode on impact.
- **Stutter:**
  - The slow-motion dip on huge blasts was removed. It froze the game whenever one went off anywhere.
  - PhysX is no longer stepped; debris and turrets move on their own kinematics. It had spiked to 15 ms.
  - Rigid model parts are merged: a tank went from ~19 renderers to ~4.
  - Scenery is culled in cells and particle noise is a texture.
  - A frame-rate governor settles at a steady 30 fps when a device cannot hold 60.
  - `PerfProbe` (`-mb-perf`) logs frame times, hitches, engine markers and a scene census.
- **Ground markings:**
  - The `GroundMark` shader draws signed-distance, anti-aliased rings: objective rims with turning dashes and a capture arc, and strike telegraphs with a sweep to impact.
  - It also draws selection brackets, move markers and a ring under every aircraft.
- **Roster:**
  - Ten new vehicles: armoured car, tank destroyer, heavy tank, SAM launcher, mortar carrier, rocket technical, heavy gunship, scout helicopter, attack jet and strike drone.
  - Aeroplanes circle and fly strafing runs.
  - The commander keeps about a fifth of its army in the air.
  - Decks hold 8 vehicles.
- **Ashfield** is generated by `Tools/maps/build_ashfield.py`:
  - A paved square with a ring road, an outer lane, and streets lined with houses facing them.
  - Shops, apartments, a church, fuel depots, farmsteads, ruins, rock cover and forests.
  - The script proves every objective is reachable and reports anything it cannot place.
  - It uses 21 new building, barrier, civilian-vehicle and tree models.
- **Surroundings:** a faceted mountain range with snow and crags, forests climbing it, a river valley, and ground to the horizon.
- **Audit** by four reviewers (simulation, presentation, HUD/input/audio, data/balance). The fixes are in the last two commits:
  - Aeroplanes obey orders.
  - Artillery no longer freezes on close targets.
  - The commander defends drained points.
  - Kill rewards go to the right team.
  - Fog works with the orthographic camera on GLES.
  - Survival defeat is fair.
  - Audio pauses.
  - HUD updates only on change.
  - Balance was rebalanced from a DPS/EHP-per-CP audit.

### Known limitations

- The Android emulator tops out at about 30 fps even with nothing drawn, so smoothness can only be judged on a real phone.
- The back button is handled (Escape), but on the emulator GameActivity's text input consumes KEYCODE_BACK before Unity sees it; not verified on a device.
- Assault mode and further maps are still not started; there is still no background music (by request).

## 2026-09-26: Auto-play commander, cleaner and bigger explosions

Playtest feedback: explosions still showed claw-like streaks, the fire felt reduced, and most of the game should play itself rather than be micro-managed unit by unit.

### Done

- **The army plays itself.**
  - The player's side is run by the same commander AI as the enemy (Hard in Conquest). It buys vehicles, calls fire support, picks objectives and fights.
  - In Survival it holds a line between the base and the threat.
- **The player steers intent** from a commander panel:
  - Attack or Defend stance.
  - Auto buy and Auto support toggles, which are remembered between matches.
  - Tapping an objective chip (A, B, C) sends the whole army there. Tapping it again clears the focus.
- **Hand control is optional.** A vehicle given an order by hand is left alone until 20 s after that order finishes, then the commander takes it back.
- **The camera follows the fight** after 8 s without a touch.
- **Explosions:**
  - Sparks are round glowing points instead of stretched streaks.
  - There are more fireballs, sparks and burning debris, plus secondary pops for large and huge blasts.
  - Fire is brighter, more wrecks and heavy hits start fires, and wrecks burn for 40 s.
- **Tests:** 66 EditMode tests. The new `CommanderTests` cover focus points, the hand-control hold, auto buy and holding a line.

## 2026-09-26: Flicker fix, full roster, Conquest, strikes, weather and menus

### Done

- **Vehicle flicker fixed.** On OpenGL ES the URP SRP Batcher drew vehicles with stale transforms: turrets flashed back to an old pose and moving tanks stuttered. It was bisected on the emulator with screen recordings (single-frame brightness spikes per region, counted with OpenCV) and command-line debug switches (`Match.DebugFlags`). Before the fix there were 42–63 flashes per 14 s; after it, 0–1. The SRP Batcher is now off on GLES only. Specular anti-aliasing, a cap on reflected light and a bloom clamp remove sun glints on thin parts.
- **Weapons:**
  - Vehicles carry several mounts: coaxial guns, free roof guns and chin turrets, and hull-fixed pods. Each mount has its own target, cooldown and muzzle.
  - Salvos (MLRS, helicopter rockets), guided missiles that home in, flamethrowers and airburst flak.
- **Aircraft:**
  - The attack helicopter flies straight over obstacles and only anti-air weapons reach it; ground blasts cannot.
  - It banks, bobs, spins its rotors and crashes when shot down.
- **Roster:** jeep, APC, light tank, MBT, flame tank, self-propelled artillery, MLRS, anti-air vehicle and attack helicopter. There are 15 weapons in `balance.json`.
- **Models:** 19 new Blender models: the new vehicles, a strike jet, munitions, mountains, cliffs, boulders, sandbags, tank traps and dirt mounds. The existing tanks gained machine guns. Model tests check that every weapon mount has its muzzle.
- **Economy:**
  - Command Points with a bank cap and a unit cap, deployments with delivery, and kill rewards.
  - The player buys from a deck of 6 vehicles and 2 supports in both modes.
- **Fire support:** barrage, airstrike (jet flyover, falling bombs, one telegraph ring per bomb), cruise missile, smoke screen (blocks sight) and repair drop. All are telegraphed and friendly-safe.
- **Conquest mode:**
  - Three objectives on `ashfield_conquest`, capture rates (jeep ×2, APC ×3, aircraft cannot capture), contested points, ticket bleed and ticket loss per vehicle lost.
  - Results, and a Conquest AI that counter-picks, saves for strong units, strikes clusters, repairs groups and chooses objectives by value (Easy, Normal, Hard).
- **Menu and HUD:**
  - The main menu runs over a live AI-versus-AI battle. It offers mode, difficulty, weather, a deck editor and settings (volume, effects quality, reduced motion, FPS, language).
  - The in-match HUD has ticket bars and objective chips, the deck bar with CP meter and cooldowns, strike targeting, a rotated minimap (tap to jump), a mission banner, pause and results.
- **Environment:**
  - Weather: clear, overcast, rain and storm. Mood lighting and fog, rain streaks and splashes, wet ground, gusting foliage, lightning and thunder.
  - A ring of mountains and outcrops around the map. Terrain props inside it shape lanes and fortify the objectives.
- **Explosions:**
  - A new particle shader gives noise-eroded fireballs with hot cores and lit, billowing smoke. Every puff has its own seed and evolves over its life.
  - Burning debris flies on arcs, trailing smoke.
- **Audio:** synthesised launches, flak, flamethrowers, jet passes, a helicopter rotor loop, strike alarms, objective chimes, rain and thunder.
- **Tests:** 60 EditMode tests. They include headless AI-versus-AI Conquest matches with the shipped content and headless Survival waves.

### Known limitations

- Performance on a real phone is still unmeasured; the emulator runs on the desktop GPU.
- The terrain is flat inside the battlefield; the relief is the mountain ring outside it.
- There is no fog of war yet: the AI sees what its units see, but the player's view shows everything.
- Assault mode and further maps are not started.
- There is no background music (by request).

## 2026-09-26: Visual overhaul, battle effects, audio and tactical AI

The voxel look was replaced after playtest feedback ("stiff and crude", poor font and UI). Quality target: [3d_astra](https://github.com/buicongnguyen/3d_astra), whose Blender kit is reused with the owner's permission.

### Done

- **Art pipeline:** low-poly models generated by Blender scripts (`Tools/blender`, based on 3d_astra's `frontier_kit.py`): bevelled parts, weighted normals, baked vertex AO and named PBR materials, exported as GLB and loaded with glTFast. There are 24 models (4 vehicles, buildings, props, trees, rocks, rubble and debris).
- **Rendering:**
  - A `MachineBrigade/Lit` PBR shader with vertex AO, team tint and wind sway.
  - An orthographic 3/4 camera.
  - A procedural terrain texture with roads and footprints.
  - Hemisphere ambient, a reflection cubemap and fog.
  - ACES post-processing with bloom.
- **Surroundings:** the map no longer ends in a void. Fields, a river, forest belts, farmhouses and rocks extend 230 m out, drawn with GPU instancing (about 9,000 instances in 12 batches).
- **UI:** the HUD was rebuilt in UI Toolkit with the 3d_astra palette, the Inter font, vector icons and en/vi strings.
- **Jitter fixes:**
  - Hull overlap is resolved gradually instead of in one step.
  - Heading is held while rolling into the final waypoint.
  - Shadow bias and distance were tuned, and MSAA added.
- **Effects:**
  - Bigger explosion tiers with extra dirt, ember and dust-ring layers.
  - Machine-gun bursts of three staggered tracers.
  - Smoke trails behind tank and artillery shells, and muzzle smoke.
  - Lingering fires where fuel exploded or buildings collapsed.
  - Ammunition cook-offs in burning wrecks.
  - Tread dust behind moving vehicles.
  - Smoke columns darken at the source, thin into grey haze and drift with the wind, so they no longer hide the fight.
- **Audio:** every sound is synthesised at startup (`SoundSynth`): cannon, heavy gun, howitzer, machine gun, three explosion sizes, building collapse, a wind loop and a UI click. `AudioDirector` plays them from simulation events, panned by screen position and faded by distance from the camera, with per-sound cooldowns and a 20-voice pool.
- **AI:**
  - **Target choice (both sides):** vehicles prefer targets their weapon counters, badly damaged ones and ones that can be finished with this shot, and they focus fire with teammates.
  - **Guarding (both sides):** idle vehicles no longer stand still while being shot. They close in on visible enemies, and on whoever just hit them, within a 16 m leash, then drive back to their post. Artillery and unarmed vehicles hold position.
  - **Tactical opponent (`TacticalAi`, replaces the placeholder):**
    - The main body advances in bounds anchored on its lead vehicle and waits for stragglers.
    - Fast vehicles swing round a flank.
    - Artillery keeps a standoff distance, shells clusters of three or more, and backs away from anything inside its minimum range.
    - Badly damaged heavy vehicles pull back behind the line.
- **Tests:** 43 EditMode tests. New ones cover the AI (guarding, returning to post, target choice, artillery standoff, pulling back) and a headless 90 s sandbox battle that must reach contact.

### Known limitations

- Pulled-back vehicles stay in the rear; there is no repair yet.
- The flank side is fixed per match (chosen by seed).
- Audio has no music, and there is no volume setting yet.
- The Blender models cover only the four sandbox vehicles. APCs, MLRS, AA and helicopters come with Phase 3.

## 2026-09-26: Combat sandbox (Phase 1 and the start of Phase 2)

A playable test battle on the Ashfield sandbox map. It runs on the Android emulator (functional check only; no phone measurements yet).

### Done

- **Simulation** (`Scripts/Sim`, no engine references):
  - 20 Hz fixed step.
  - Stable entity ids.
  - Commands validated on submit: Move, Attack, Attack-move, Stop and Retreat.
  - Team vision.
  - Grid navigation: A* with corner-safe line-of-sight smoothing, formation slots, and stuck detection.
  - Turret aiming, projectiles with travel time, the damage table and splash.
  - Delayed explosions, with chain reactions that terminate.
  - Destroyed buildings unblock the grid.
- **Data:** `Resources/Data/balance.json` (4 weapons, 4 vehicles, 7 props) and `maps/ashfield_sandbox.json`. Both accept `//` comments. Load errors name the offending field.
- **Sandbox mode and placeholder AI:**
  - Starting forces for both sides.
  - Escalating enemy waves every 30 s.
  - A reinforcement call (+2 vehicles, 12 s cooldown).
  - Enemy groups attack-move towards the nearest player vehicle.
- **Voxel art generated in code:**
  - Jeep, light tank, main battle tank and artillery, in team colours.
  - Two house sizes, wall, fuel tank, barrel, ammo crate and tree.
  - A greedy mesher, pre-split debris chunks and rubble.
- **Effects:**
  - Five explosion tiers built from particle layers: flash, fireball, smoke, sparks, debris, shockwave and a light.
  - Muzzle flashes.
  - Tracers timed to the simulation, with arcing artillery shells.
  - Scorch decals in a ring buffer.
  - Burning wrecks, and turrets blown off by cook-offs.
  - Physics debris from destroyed props.
  - Camera shake, and brief slow motion on huge blasts.
  - All pooled, with Eco and High budgets.
- **Controls:**
  - Tap to select, move or attack; tapping a barrel or building attacks it.
  - Double-tap selects all vehicles of that type.
  - Long-press and drag box-selects.
  - One-finger pan and pinch zoom.
  - HUD buttons: All, Stop, Retreat, Attack-move, Reinforce and Restart.
  - Mouse wheel and right-drag in the editor.
- **Rendering:** three hand-written URP shaders (VoxelLit, Unlit, Particle). Vertex colours are linearised for the Linear colour space.
- **Tests:** 38 EditMode tests. They cover content parsing, navigation, commands (including R04 retreat), combat (T01 single damage, T05 chain termination, death explosions, building unblocking), determinism and the voxel mesher.

### Known limitations

- Vehicles drive through wrecks and each other's wrecks. The plan's "large wrecks block" rule is not implemented yet.
- Shots pass through buildings; there is no line-of-fire check.
- Explosions read small at the default zoom. Fireball size, lifetime and bloom need tuning.
- The pace is very lethal: most of the starting force is lost in under a minute. TTK and HP need tuning.
- The deck/CP economy, helicopters, fog-of-war visuals, Conquest tickets and the real AI are not started. These are Phase 3 onwards.
- HUD text is English only and uses the built-in font. Be Vietnam Pro and the localisation tables come with the menus.
- There are no haptics yet: `Handheld.Vibrate` is too long and a short Android vibration plugin is needed.
- The emulator runs on the desktop GPU, so its FPS says nothing about phone performance.
