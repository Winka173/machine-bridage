# Asset debt

Art that stands in for its own until it is made. Each line: what, what it uses now, what it needs.

## Prompt 8

| What | Uses now | Needs |
|---|---|---|
| Elite FPV carrier, elite attack jet, elite long-range SAM, elite SP howitzer | Their base card's model, repainted at spawn (`VehicleView.EliteRepaint`): the armour in the elites' EliteBlack, hazard stripes in Gilded gold, lamps in the red EliteGlow; the gold health bar and the minimap's gold ring as for every elite | Bolt-on armour plates or a turret cage like the other elites' own models (elite_mbt, elite_heavy_tank...) if a closer look is wanted |
| Rail supergun's tractors | `rail_tractor` model attached at two points of the gun (`attach` in balance.json) | Animated couplings (they stand still) |
| Boss parts broken off | The part's node hidden and a generic wreck piece put at its origin (`VehicleView.BossParts`) | Per-part broken meshes (a burnt engine pod, a gutted hangar) |
| Earth Worm's dive | The model sinks 9 m into the ground (`BurrowDepth`); the crack warning is a toast and a warning ring on the minimap | A ground-crack decal on the field, and debris for the surfacing |
| Armoured bulldozer blade stroke | The Blade node pitched up and slammed down in code | Nothing essential (a scraping sound would help) |

## Prompt 9

| What | Uses now | Needs |
|---|---|---|
| Broken boss parts | The part's nodes hidden and a shared stand-in put in: `wreck_barrel` (guns), `wreck_turret` (mounts), `wreck_launcher` (pods, racks), `wreck_engine` (engines, fans, propellers), `wreck_stump` (the rest) | Per-part broken models: bent barrels, turrets with their hatch blown, twisted racks, burnt-out engine pods |
| Parts with no node of their own | A place on the hull: the Iron Train's locomotive and second gun car, the Behemoth's and Iron Bird's missile and rocket racks, the Hive's EMP emitter, the Hive Mothership's bay, UAV bay and shield | Their own nodes (`Part_*`) in the models, so they can be hidden and replaced like the others |
| Heat haze round the fires (High) | Not drawn: the pipeline has no distortion pass | A screen-space distortion pass, or a refraction particle material |
| Electric arcs on broken energy parts | Glow points along a jagged line (`Emitters.Charge`) and blue sparks | A proper arc (line renderer with a noise texture) |
| Fire crackle | The shared fire loop, louder near a burning boss | Its own crackle for a boss's fires |
| Rail Supergun's tractors | Their broken piece is a stump on their deck | A burnt-out tractor model |

## Prompt 16 (old bosses' weapons, escorts)

| What | Uses now | Needs |
|---|---|---|
| Hover gunboat (`hover_gunboat`, the landing hovercraft's escort) | The fleet's fast missile boat model (`missile_boat`, prompt 17 D follow-up; it drives over land too) | Its own small air-cushion gunboat, if a boat on land reads wrong |
| The Behemoth's protection system, the Hive's jamming mast | Places on the hull (no node) | Their own nodes (`Part_aps`, `Part_ew`) with a broken piece |
| The trains' new cars | Rigid with the train, like its other cars (as the models always were) | Articulated cars that follow the rails' curves |

## Prompt 13

| What | Uses now | Needs |
|---|---|---|
| Ammunition carrier (`ammo_carrier`) | The supply truck's model (`truck`), at 0.9 scale, with its hull measurements | Its own model: a cargo truck with ammunition crates and a loading crane in the bed (a Kamaz-style resupply truck), muzzle `Muzzle_mg` for its roof HMG |
| Landing pad branches (`airfield.hangar`, `airfield.service`) | The landing pad's model (`helipad`) | A hangar beside the pad; a fuel and ammunition point on the service branch |

## Prompt 16

| What | Uses now | Needs |
|---|---|---|
| Leviathan (`leviathan`) | A first model (`mb_naval.py`, 5.4 k triangles): hull, turrets, cells, superstructure, mast, funnel, CIWS, decks | Detail passes: hull plating and weld lines, railings, boats and davits, deck gear, a proper phased-array island |
| Leviathan's broken parts | The shared wreck pieces (prompt 9) | A burnt turret, gutted launch cells, a toppled mast, a burning flight deck |
| Leviathan breaking in two | A second copy of the model as the stern half (`ShipSinking`) | A split model (bow and stern halves with a torn middle) |
| Corvette, missile boat, landing craft | First models (`mb_naval.py`) | Detail passes; the missile boat's rocket pods as launch points |
| The sea and wakes | The river tiles' surface as the sea (lit, or unlit on Low); foam patches for wakes (`WakeView`) | Waves on the open water, a shoreline foam line, bow spray particles |
| Lighthouse, pier, fishing boat | Simple models (`mb_naval.py`) | The lamp's turning beam at night, a stone jetty, net racks |
| Coastal battery | The heavy fortress's model | A casemated coastal gun |
| Lighthouse Bay's Base-screen picture | None (the map is left out of the Base screen's list until it exists) | `BaseMapShots.RenderAll -mbBaseMaps lighthousebay` |
## Prompt 17 C

| What | Uses now | Needs |
|---|---|---|
| Stealth fighter, loyal wingman, laser tank, shield carrier, bunker vehicle, drone mothership, shield generator, CP relay | Simple temporary models (`Tools/blender/mb_p17_temp.py`): faceted airframes, kit tracks and wheels, emitter and mast parts | Detailed models to the 3d_astra bar (panel lines, decals, HD variants) |
| Their card pictures | Not rendered yet (needs `CardRenders.RenderBatch` in a batch run with graphics) | The renders |
| Bunker vehicle's coaxial MG | A fixed `MG_port` mesh that turns with the turret but does not elevate | A `Mount_mg` pivot if it should elevate |
| Shield domes' emitters | Static glowing `Emitter` parts | A slow spin and a pulse on hits |
| Laser tank's beam | The Iron Beam's red beam look | Its own colour and a ramping glow as the damage rises |

## Prompt 18 (big attacks)

| What | Uses now | Needs |
|---|---|---|
| Doomsday Train's missile erector, the Hive Carrier's and the Command Airship's bomb bays | No model node: a hit volume on the hull at the part's place, the generic wreck piece, blast and smoke when it breaks | Model nodes (an erector that rises with a missile on it, bomb bay doors that open), named in `balance.json` "node" |
| The charge on the part (coils brightening, launcher lids opening, bomb doors opening) | A hot pulse ring at the part twice a second (`EffectsDirector.BigAttacks`) | Animations on the models |
| Each boss's big-attack sound | One alarm (the fortress siren) and the shell whistle for every boss | A sound per boss (the railgun's whine, the erector's hydraulics, the drone swarm's buzz...) |
| Missiles and drones shot down in flight | The sim's intercept pop where it died; the round's own flight on screen runs on to its target | The projectile pool cancelling that round |
| Enemy units boosted by the Supreme Commander's offensive | No mark on them | A small icon over each boosted unit |
| The Spectre's tight, low orbit during its attack | The sim's own orbit (only the damage it takes changes) | A lower, tighter circle in its flight |
| The "In action" clip of a boss (Guide) | Its ordinary weapons only | A clip of its big attack |

## Prompt 19 (the Silver Bug as an orbital spacecraft)

Built in `Tools/blender/mb_orbital.py` (replaces `mb_boss_saucer.py`): `silver_bug` (the shuttle, 25.7k triangles, every part
node), `silver_bug_wreck` (its crashed form for phase 3, 27.8k, with the six debris piles where the sim puts its cover),
`bug_satellite` (1.7k), `drop_pod` (3.0k). LODs are the runtime's (`ModelLibrary.EnsureLod`). Not seen in Unity yet.

| What | Uses now | Needs |
|---|---|---|
| Card renders of the Silver Bug, the drop pod (and the wreck for the Guide) | The old saucer's card | The lead's graphics run after the merge (`CardRenders`) |
| The "In action" clip (Guide) | The saucer's clip | A clip of the shuttle: its laser, a rod rain from the satellite, pods falling, the crash |
| The opening in low orbit: the huge shadow sweeping the map, the craft a bright dot | The model drawn 150 m up (its shadow is the sun's) | A bright point sprite on the sky and a shadow decal the size of the ship |
| Leaving orbit: re-entry glow, engine flame; the satellite left up there | Nothing but the model coming down (`TierChanged` "descend" event is emitted) | A glowing hull shader pass, a flame at `Thruster_main`, the `bug_satellite` model as a small bright dot in the sky |
| Changing altitude (3-4 s) | The model eases between the tiers' heights (`VehicleView`) | Engine flame and a smoke trail on each `TierChanged` "shift" |
| The crash (phase 3): a long smoke trail, the impact crater | A slope down to the crash site, the warning ring (`bug_crash`), an Ultimate blast, the wreck model | A smoke trail on the fall, a crater decal; the prompt 9 fires and smoke at the breaks come from the parts |
| The tungsten rods: light columns as the warning, the streak from the sky | The shared red warning rings and an Ultimate blast per rod | A light column per ring (about 4 s) and a fast bright streak from above, a sonic crack |
| Drop pods: the fall and the landing | The pod model falling straight down, the warning ring (`pod_drop`), a dust blast | Retro-rocket flame before touchdown, doors opening, a scorch mark |
| The point-defence lasers taking SAMs | The APS intercept flash | A short beam from `Pd_laser_l/r` to the missile |
| The drone seizure (Very Hard) | The drones change colour (the ordinary side change) | A hacked-glitch shader and a sound while they are seized |
| Boss bar: altitude chip icons | `cbradar`, `sam`, `aa` from the HUD set | Icons of their own for orbit, high and low |

## Prompt 20 pass 2 (boss templates, new bosses)

| What | Uses now | Needs |
|---|---|---|
| Card renders: leviathan, sea_cruiser, silver_bug (pose `Mount_gun.002` / `.004` aft on Leviathan), moloch, daedalus, kronos, typhon, ixion, caspian, bastion_mk0, fenrir, scylla, locust, behemoth_mk2, icarus_mk0, argus; the resized and re-armed old bosses | None (new) / the old cards | The lead's graphics run after the merge (`CardRenders`) |
| "In action" clips (Guide) of the thirteen new bosses | None | Clips: Moloch's doors, Daedalus's mass drop, Kronos's sweep, Typhon surfacing and launching, Ixion's charge, Caspian's pass, each variant's attack |
| Models of the six new bosses | Ixion, Typhon, Caspian and Daedalus redrawn from references (DECISIONS 20Y, `mb_redesign_20y.py`); Moloch and Kronos first passes (`mb_p20_bosses.py`) | A detail pass to the 3d_astra bar: Moloch's workshop, Kronos's girders and buckets |
| The variants' marks (Mk.0, Mk.II, frost, ice) | A hull tint only | A decal or emblem per `mark` |
| The old bosses' new weapons | Kit turrets and pods bolted on (the models rebuilt) | Fitting them into each hull's design |
| Music: each main boss's own track, the mini bosses' shared `boss_mini` | `boss` for all | Tracks named by `music` / `bossRanks` |
| Typhon's bubbles and wake before it surfaces, its dive | The Earth Worm's ground cracks on the water | A bubble and foam effect on `Burrow` stage 1 at sea, a dive wash |
| Kronos's bucket wheel turning, debris thrown; Ixion's wheels rolling and the charge's dust | Static wheels; blasts only | Spinning `Part_wheel` / `Part_wheel_l/r` by speed, a dust trail on the charge |
| Moloch's doors opening as vehicles drive out | The `Landed` event only | A door animation on `Part_door_l/r` |
| Daedalus's mass-drop pods falling | Landing blasts only | The pod model falling on each ring |
| Kronos's 120-degree swing warning | Three rings | A sector decal |
## Tower branches (tower-branch prompt C, DECISIONS 19U)

Built in `Tools/blender/mb_tower_branches.py`: 32 branch models `<tower>_a` / `_b` (1.3k to 11.7k triangles), each on
its tower's builder with the branch's module swapped or added; 31 new branch icons (`t_<tower>_a` / `_b`, the Iron
Dome's renamed `t_cram_b`); rank details made at run time (`TowerRankDetails`). LODs are the runtime's.

| What | Uses now | Needs | Priority |
|---|---|---|---|
| Card pictures of the 32 branches and of the rank milestones (C.5) | The tower's card picture (`CardRenderTests` lists the 32 until they are rendered) | The lead's graphics run after the merge (`CardRenders.RenderBatch`) | High |
| "In action" clips of every branch | The tower's clip | A clip a branch (the lead) | High |
| Screenshots of every tower at every branch and at ranks 1, 3, 5, 7 (F), the image comparison at the default zoom and on Low | None | A graphics run into `Docs/ui-screens/`; the tower icon sheet shot again (`IconSheet.Towers` shows the branch icons) | High |
| Branches that are the tower's model plus one module (C.7): `aa_turret_a` (two more barrels), `c_ram_a` (ball radome), `atgm_tower_a` (raised launcher), `mg_bunker_a` (twin barrels and mantlet), `rocket_turret_b` (covered box), `missile_battery_b` (bigger radar), `shield_tower_a` (glowing dome cage), `cp_relay_a` (comms container) | The tower's model with that module; readable at the default zoom | A fuller rebuild of each where a closer look is wanted | High |
| Rank details (C.2) | Plain boxes laid on the tower's walls at run time (Hazard bars, Armor plates) | Per-tower rank kits modelled in Blender (stencilled bars, bolted appliqué fitted to each body) | Medium |
| Branch firing effects and sounds (C.3): the mortar's arc, the tower shields' beams to each tower, the autocannon's bursts, the flame arc | The branch's weapon effect as the sim gives it | Effects and sounds of their own (not part of this art pass) | Medium |
| Steel fortress's two small turrets | Stand on `Mount_gun` / `Mount_gun.001` but turn and fire only once the balance pass gives them MG mounts | The mounts (section B) | Medium |

## Tower branches (DECISIONS 19T), high priority

| Missing | Stand-in | Needed |
|---|---|---|
| Models and icons of all 32 branches (`<tower>_a` / `<tower>_b`) | The tower's own model and icon (`BranchArt` falls back) | The art branch (feature/tower-art, DECISIONS 19U) |
| Card renders of the branches, four of them new ids (`rocket_turret.guided`, `artillery_emplacement.mortar`, `shield_tower.ward`, `cp_relay.loot`) | The tower's render in the picker | `CardRenders.RenderBatch` with graphics, after the art merge (the lead) |
| The steel fortress's two machine-gun turrets | Both fire from the heavy turret's one `mg` muzzle | `Mount_mg` / `Mount_mg2` on `heavy_turret_b` |
| Tower shields' beams to each tower, the loot depot's pay-out, the radar's air picture | None (the rules work) | Effects on `Vehicle.WardHp` / `WardFrom`, `EconomySystem.LootPaid`, `VehicleDef.RevealAir` |
| Screenshots of every branch and rank in Docs/ui-screens | None | The lead, after the art merge |
## Play-test 4 (DECISIONS 19R)

| What | Uses now | Needs |
|---|---|---|
| Card pictures of bunker_vehicle, light_tank (from light_tank_hd), titan_tank, laser_tank, shield_carrier (and the elites that wear them) | The old pictures (`CardRenderTests` lists the five) | The lead's graphics run (`CardRenders.RenderBatch`) |
| "In action" clips of the five | The old models' clips | New clips; the bunker vehicle's should show it digging in |
| The bunker vehicle digging in | Parts swing, sink and grow (VehicleView.Deploy); no dust | Earth spray from the blade and spades, dust as the hull sinks, a dig sound |
| The bunker's spoil bank | One shared shape round the hull | A few shapes for variety, snow and sand tints on those battlefields |
| Laser tank, shield carrier | Redrawn silhouettes on the prompt-17 hulls (still simple parts) | The full 3d_astra detail pass (panel lines, bolts) |

### Play-test 5 sim half (DECISIONS 20W)

| What | Uses now | Needs |
|---|---|---|
| The siege tank's card picture and "in action" clip | The old M110-style pictures | The lead's graphics run (`CardRenders.RenderBatch`); the clip should show it sieging |
| The siege tank sieging | Braces, spades, gun, column and mortar move (VehicleView.Deploy); no dust or sound | Dust as the braces and spades bite, a hydraulic whine, a heavier mortar report |
| The C-RAM's stream at a round | Tracers and a muzzle flash each step at the round's estimated place | Tracers that meet the drawn round exactly (the view has no link from a sim round to its drawn rocket) |

## Prompt 22 E (new maps and bosses, DECISIONS 22E)

| What | Uses now | Needs |
|---|---|---|
| Morrigan's model | A first pass from references (YF-23 planform and tails, Su-57 bays, feathered trailing edge; `mb_p22_content.py`, 1 312 triangles) | A detail pass to the 3d_astra bar: panel lines, the bay doors' saw-tooth edges, a raven emblem |
| Card renders and "in action" clips: behemoth_mk0, morrigan (the salvo, the duel's dark spell) | None | The lead's graphics run (`CardRenders`) |
| Mara's Behemoth's Accord mark, Behemoth Mk.0's primer look | A hull tint (`mark` "accord", "mk0" in the data) | A decal or emblem per `mark` |
| Foundry's roofs and hall walls | Walls of the plain `wall` prop (low, fire passes over) round open floors | A factory-hall wall and a roof-truss prop (tall, blocks fire), glass skylights, furnaces with glow |
| Veyra Old Quarter's old town | The kit's townhouses, cottages, offices and shops; a church as the cathedral | Old-town facades, a cathedral, a clock tower, cobbles, fountains and awnings |
| Base map pictures of both maps (`BaseMapShots`) | None | A run with graphics |
## Prompt 22 F: commanders (DECISIONS 22F)

| What | Uses now | Needs |
|---|---|---|
| Portraits of the eight new commanders: Kaia Mendez (Rush), Piet Dahl (Longshot), Otto Brenn (Ledger), Tomas Adler (Flag), Ines Varro (Tide), August Reyn (Crown), Lena Quist (Magpie), Selma Okoye (Vault) | The HQ's placeholder portrait (`UI/Portraits/hq`: `Portraits.Get` falls back to it for `UI/Portraits/<id>`) | A portrait each, `Resources/UI/Portraits/<id>.png` (mendez, dahl, brenn, adler, varro, reyn, quist, okoye), in the story portraits' style |
| Portraits of the six story commanders (Kade, Lind, Reyes, Kerr, Venn, Brandt) and the eight generals | The story's portraits (`khai`, `mai`, `dieuhau`, `linh`, `sen`, `brandt`, the generals' own) | New ones only if the story's renames (prompt 22 A) change a character's look |
| The commander's face in the HUD | The portrait, cropped into the 44 px face | A small, high-contrast icon version of each portrait if the face reads poorly at 44 px |
| The commanders' radio lines | Text only (the radio panel, the result card's note) | Voice lines, if the game gets voice |
| Screenshots of the picker, the briefing with its general and the dossier's commander pages in `Docs/ui-screens/` | None (`UiShots` has the screens: `commanders`, `dossier-commanders`, `briefing`, `hud-commander`) | The lead's graphics run (`-mbShotsOnly commanders,dossier-commanders,briefing,hud-commander`), both languages |
### Prompt 22 D (DECISIONS 22D)

| What | Uses now | Needs |
|---|---|---|
| The front map of the Meridian Coast | Drawn in code (FrontMapView): a coast polygon, grid cells coloured by side, a front line, dots, flag icons, round pins | An illustrated map (terrain, towns, roads, the sea) with the regions as shapes, and a softer front line |
| The comic panels after each chapter (48) | A battlefield's shot and a card render, the speaker's portrait and a speech box in a black frame (ComicPage) | Drawn panels (the moment itself: the landing, the ceasefire, the turn in Veyra, Icarus falling), speech balloons |
| Interlude I's panels | The Rust Yard's shot (the Foundry has no picture yet) | The Foundry's map shot once P22-content's map lands, then the drawn panels |

## Prompt 25 B2 (DECISIONS 25B2)

The models prompt 25 B2 did not reach, with the shape note ("Hình dạng (cho AI vẽ)") of the balance sheet's
Phương tiện, Công trình and Boss sheets, in English. Sizes are length x width x height at the map scale (ground
0.8 x real, aircraft 0.4 x real); "change" marks a model whose "Kích thước model" row in "Kiểm tra từng mục" says
its size must change. Every one also needs: the side's stripe on the roof and flanks, no real insignia, the
guide's triangle budget (light 1,500-3,000, tanks 3,000-5,000, aircraft 2,000-4,000, towers 1,500-3,500, bosses
15,000-40,000), nothing thinner than 0.1 m, its mounts kept, and before/after shots in `Docs/ui-screens/models/`.
Almost all of today's models are over those budgets (6,000-15,000 triangles for most vehicles).

### Vehicles

| Model | Size now (in battle) → sheet | Shape note |
|---|---|---|
| hover_gunboat | 14.0 x 3.9 x 4.4, keep | Low hovercraft hull with a black rubber skirt, two big ducted fans aft in guard rings, a small six-barrel turret forward. From above: a teardrop with two round fan rings at the tail. |
| ifv | 6.2 x 2.7 x 3.1, keep (note: 5.2 x 2.9 x 2.4, M2 Bradley) | Tracked, six road wheels, taller hull than a tank, turret offset left with a short 30 mm gun and a TOW box on the turret side, big rear door. From above: a rectangle with the square missile box beside the turret. |
| engineer_vehicle | 6.3 x 2.8 x 2.4, keep (note: 6.9 x 3.0 x 2.6) | Turretless tank chassis (BREM-1 / M88), a folding crane on the roof, a dozer blade in front. From above: the crane lying diagonally along the hull, the blade wider than the hull. |
| smoke_carrier | 4.2 x 2.3 x 2.9, keep (note: 3.9 x 2.2 x 2.0) | Low box M113 hull, a cylindrical smoke generator and exhaust on the rear roof, smoke grenade launchers on both sides. From above: a plain box, the generator drum at the back. |
| ew_jammer | 7.9 x 2.9 x 5.1, keep (note: 8.8 x 2.4 x 3.2) | 8-wheel truck with a large dish antenna or a tall lattice antenna mast, flat body (Krasukha-4). From above: a big round dish. |
| mine_layer | 6.6 x 2.6 x 3.0, keep (note: 7.4 x 2.6 x 2.0) | Low tracked chassis, an inclined mine chute at the tail, mine boxes stacked on the roof (GMZ-3). From above: the long chute at the back. |
| shield_carrier | 7.4 x 2.5 x 5.3, keep (note: 6.3 x 2.4 x 1.9) | 8-wheel vehicle (Boxer chassis) with a domed metal shield emitter ringed in the side's glow; when active a translucent 12 m dome. From above: a glowing round disc mid-hull. |
| vbied | 4.4 x 1.9 x 2.4, keep (note: 4.2 x 1.5 x 1.8) | Civilian pickup welded over with patched steel plates, small vision slits, thicker front plate, no visible weapon. From above: a rough steel box with uneven plate edges. |
| light_tank | 6.2 x 2.3 x 2.2, keep (note: 6.1 x 2.6 x 1.8) | Low boat-shaped (amphibious) hull, small turret set forward, long thin 57 mm gun (PT-76 / ZBD-05). From above: a boat-like bow. |
| turtle_tank | 8.1 x 3.3 x 3.9, keep (note: 7.6 x 2.9 x 2.8) | T-72 covered by a big sheet-metal shell like a turtle's, over hull and turret, only the gun poking out, the edge hanging close to the ground, anti-drone netting. From above: one big oval roof. |
| bmpt | 6.3 x 3.1 x 2.9, keep (note: 5.8 x 2.8 x 2.7) | T-72 chassis, a low wide turret with twin 30 mm guns either side and two box missile launchers, two grenade launchers on the front fenders. From above: a wide turret with many short barrels. |
| rocket_technical | 4.6 x 1.8 x 2.8, keep (note: 4.2 x 1.4 x 1.6) | Civilian pickup with a 12-tube rocket launcher on the bed (Type 63). From above: a grid of small round tubes on the bed. |
| mortar_carrier | 4.4 x 2.5 x 3.2, keep (note: 3.9 x 2.2 x 2.0) | M113 chassis, the rear roof hatch open wide, a 120 mm mortar pointing up through it. From above: the big roof opening and the mortar tube. |
| mlrs | 6.4 x 2.3 x 3.6, keep (note: 5.6 x 1.9 x 2.6) | 6-wheel truck, a large six-tube box launcher at the rear that lifts and turns (HIMARS). From above: the rectangular pod covering the rear half. |
| thermobaric_launcher | 6.3 x 3.1 x 2.9, keep (note: 7.6 x 2.9 x 1.8) | T-72 chassis, a big 24-tube box launcher on a lifting mount mid-hull (TOS-1A). From above: a big square block of tubes. |
| ballistic_launcher | 10.9 x 2.6 x 4.7, keep (note: 10.5 x 2.5 x 2.6) | Long 8-wheel vehicle, one big missile in a casing on the deck, raised upright to fire (Iskander). From above: the long missile down the middle. |
| heavy_rocket_artillery | 10.5 x 2.7 x 4.2, keep (note: 9.7 x 2.4 x 2.4) | Long 8-wheel vehicle, a block of 12 large (300 mm) tubes at the rear (BM-30 Smerch). From above: 12 big round tubes in 3 rows. |
| zu23_technical | 4.5 x 1.8 x 2.1, keep (note: 4.2 x 1.4 x 1.8) | Civilian pickup with a twin-barrel ZU-23 on the bed. From above: two long parallel barrels. |
| aa_vehicle | 5.6 x 2.7 x 3.0, keep (note: 6.2 x 3.0 x 2.4) | Tracked chassis, a square turret with a 35 mm gun on each side, a round radar dish spinning behind the turret (Gepard). From above: two barrels either side, the dish. |
| scout_heli | 4.3 x 3.9 x 1.4, keep (note: 4.0 x 3.3 x 1.0) | Small egg-shaped helicopter, five-blade rotor, skids, two small weapon pylons (MH-6 Little Bird). From above: a rotor disc large for the small body. |
| recon_drone | 2.9 x 5.0 x 0.7, keep (note: 2.6 x 4.8 x 0.9) | Straight-wing UAV, long wing, slim body, inverted V tail, pusher propeller (TB2). From above: a cross with a very long wing. |
| wingman_drone | 4.2 x 3.6 x 0.8, keep (note: 3.5 x 3.3 x 0.8) | Small fighter-like jet drone, no cockpit, dorsal intake, V tail (XQ-58 Valkyrie). From above: a small arrowhead. |
| strike_drone | 4.5 x 7.4 x 1.1, keep (note: 4.4 x 8.0 x 1.5) | Large straight-wing UAV, very long wing, bulged nose (radar), Y tail, missiles under the wings (MQ-9). From above: a wing twice as long as the body. |
| stealth_fighter | 6.1 x 4.2 x 1.2, keep (note: 7.6 x 5.4 x 2.0) | Faceted stealth fighter, two tails canted out, angled intakes, no external stores (F-22 / Su-57). From above: a flat diamond. Play-test 9 redrew it slim; only its size is open. |
| gunship_heli | 7.1 x 5.8 x 2.0, keep (note: 7.0 x 6.9 x 2.6) | Large armed helicopter, two stepped bubble cockpits, a troop cabin in the middle, drooping stub wings with rocket pods, about 15 % bigger than the attack helicopter (Mi-24). From above: a big body, stub wings with many pylons. After this pass the Apache is 6.0 m long: the Hind must stay 15 % larger. |
| attack_jet | 6.4 x 6.0 x 1.5, keep (note: 6.2 x 5.8 x 1.9) | Straight-wing attack jet, two engines at the wing roots, many pylons under the wings, shorter than the fighter (Su-25). From above: a wide straight wing. It must stay shorter than the new 8.6 m fighter at B1's scales. |
| stealth_bomber | 7.0 x 17.6 x 2.0, keep (note: 8.4 x 21.0 x 2.1) | Flying wing with a sawtooth W trailing edge, no tail, very wide for its length (B-2). From above: a sawtooth boomerang. |
| heavy_bomber | 17.9 x 18.7 x 6.1, keep (note: 19.4 x 22.6 x 5.0) | Eight engines in four pairs under a long swept wing, a long fuselage, a tall tail; the biggest of the player's aircraft (B-52). From above: the swept wing with four engine pairs. |
| bunker_vehicle | 8.5 x 3.5 x 3.1, keep | Tracked chassis with a big dozer blade and a low 105 mm turret; deployed, the hull drops and armour plates and sandbags rise round it. From above: the wide blade, the low turret. |
| armored_bulldozer | 6.7 x 3.7 x 4.8, keep (note: 6.5 x 3.7 x 3.2) | Armoured box-shaped tracked dozer, a very large blade, a caged armoured-glass cab (D9R). From above: a blade wider than the hull. |
| heavy_tank | 8.8 x 3.2 x 3.5, keep (note: 8.0 x 2.9 x 2.4) | Very heavy tank, long hull, a small angular unmanned turret, a big long 152 mm gun, seven road wheels (Object 195). From above: the very big gun. Must stay longer than the new 7.7 m MBT. |
| titan_tank | 10.4 x 3.6 x 3.5 → length 10.6 or more, change | Super tank on four tracks (two a side), a big turret with twin 140 mm guns, machine-gun sub-turrets, at least 20 % bigger than the heavy tank. From above: as wide as two tanks. At scale 1.0 today's model is already 12.2 m long; the four tracks and the width are open. |
| wheeled_gun | 9.4 x 2.6 x 3.1, keep (note: 7.9 x 2.4 x 2.2) | 8-wheel vehicle with a full tank turret and a long 120 mm gun (Centauro II). From above: like a tank but with four pairs of wheels. |
| tank_destroyer | 9.2 x 2.7 x 2.2, keep (note: 7.8 x 2.5 x 2.4) | Low tank destroyer, a small turret with a very long 125 mm gun (nearly the hull's length; 2S25 Sprut-SD). From above: a very long gun for a small hull. |
| railgun_truck | 9.7 x 2.9 x 3.7, keep | 8-wheel vehicle with two long parallel guide rails, capacitor coils and blue-glowing radiator panels. From above: two long parallel rails. |
| laser_tank | 6.3 x 2.7 x 2.6, keep | Tracked chassis with a laser emitter on a fork mount, a big round mirror, radiator panels on both sides. From above: the round mirror disc on its fork. |

Related to the rebuilt models: `elite_mbt`, `elite_attack_helicopter` and the other elites of rebuilt units keep the old
designs (they are their own models); `transport_plane` (airdrops, the MOAB) still flies play-test 5's airframe, not
the new shared C-130 (`mb_p25_models._c130`); Icarus's scale for "the largest thing in the sky" is B1's (DECISIONS
25B2).

### Structures

| Model | Size now | Shape note |
|---|---|---|
| aa_turret | 5.4 x 4.5 x 3.2 | Round sandbag emplacement with a twin-barrel anti-aircraft gun on a turntable and two small missile tubes. Branch flak: a four-barrel gun with a small radar. Branch sam: a four-tube missile box instead of the guns. |
| cp_relay | 4.0 x 4.0 x 7.8 | Steel lattice mast with two dish antennas and an equipment box. Branch hardened: thick concrete cladding. Branch loot: a crane and a pile of containers. |
| dragons_teeth | 2.5 x 5.2 x 1.3 | A row of truncated concrete pyramids. Branch hedgehog: cross-shaped steel hedgehogs. Branch wire: barbed-wire coils on stakes. |
| ew_tower | 4.0 x 4.0 x 10.1 | Tall antenna mast (about 10 m) with panels and small dishes. Branch drone: an antenna dome with wave rings. Branch spoof: a flat phased-array panel. |
| guard_tower | 3.5 x 3.8 x 11.6 | Tall wood-and-steel tower (about 11 m), a roofed hut with a machine gun and a searchlight. Branch watch: a radar mast and a turning searchlight on the hut. Branch nest: a low sandbagged hut with a 25 mm gun. |
| headquarters | 12.7 x 14.1 x 9.4 | Multi-block concrete command building, antennas, the side's flag, sandbags round it. |
| mg_bunker | 4.4 x 4.4 x 3.3 | Low round or hexagonal concrete pillbox, loopholes, a barrel sticking out. Branch twin: two machine-gun barrels through the loopholes. Branch flame: a flame nozzle and fuel tanks behind. |
| minefield | 4.9 x 4.9 x 1.1 | Churned ground with warning signs; the mines show only to their own side. Branch at: a few big mines. Branch scatter: many small mines and dispenser canisters. |
| airfield | 10.0 x 10.0 x 0.1 | Flat concrete pad with painted markings and lights. Branch hangar: an aircraft hangar. Branch service: a fuel bowser and ammunition crates. |
| ammo_depot | 4.9 x 6.1 x 2.9 | Half-buried store with an earth berm, ammunition crates stacked outside. |
| atgm_tower | 5.2 x 5.2 x 5.0 | Twin missile launcher on a low steel tower with a shield. Branch top: a tall launcher, missiles arcing up. Branch multi: a four-tube turntable with an anti-air sensor. |
| c_ram | 5.6 x 5.6 x 5.4 | White multi-barrel gun turret with a cylindrical radar dome on top. Branch centurion: the gatling with a spherical radar. Branch dome: an inclined interceptor launcher. |
| gun_turret | 8.9 x 5.0 x 4.0 | A tank turret on a square concrete base, a long 120 mm gun. Branch long: one very long barrel with a sight tube. Branch auto: a small turret with two short barrels and a radar. |
| logistics_station | 8.0 x 10.0 x 3.8 | Container yard and a forklift. |
| radar_station | 8.1 x 7.9 x 7.8 | Radar tower with a big turning dish. |
| repair_bay | 10.1 x 14.2 x 6.4 | Corrugated-roof workshop with a gantry crane. |
| rocket_turret | 4.7 x 4.7 x 3.4 | A 40-tube rocket launcher on a low turntable. Branch cluster: an open rail rack with many tubes. Branch guided: a closed launch box. |
| artillery_emplacement | 8.5 x 6.8 x 3.4 | Towed howitzer in a U-shaped earth and sandbag emplacement. Branch cb: a long-barrel howitzer beside a radar dish. Branch mortar: a low mortar with a very big tube. |
| drone_hangar | 8.0 x 8.0 x 5.0 | Low domed hangar with a roller door and a drone launch rail. Branch lancet: a Lancet launch rail. Branch swarm: a rack of many small drone bays. |
| heavy_turret | 10.3 x 8.0 x 6.1 | Big twin 155 mm turret on a concrete base, armour-plated. Branch coastal: a long-barrel twin turret turned seawards. Branch bastion: thick armour and two small secondary gun turrets. |
| missile_battery | 7.0 x 9.1 x 7.3 | Launcher with four big inclined missile boxes beside a phased-array radar truck. Branch pac3: a box of many small tubes. Branch lrr: a big turning radar dish. |
| shield_tower | 7.2 x 7.2 x 9.2 | Tall shield emitter tower with a ring glowing in the side's colour, a translucent dome when active. Branch bulwark: a central emitter and dome. Branch ward: many small emitter posts joined by light beams to each tower. |
| bulwark_post | 3.5 x 3.5 x 2.7 | Small sandbag gun post. |
| coastal_battery | 10.3 x 8.0 x 6.1 | Coastal gun turret on a concrete base by the rocks. |
| spawn_bastion, super_gun, targeting_station | 10.3 x 8.0 x 6.1; 18.5 x 14.4 x 11.0; 6.5 x 8.2 x 11.0 | No shape note in the sheet (size only). |

The towers' two tier-7 branches must differ in their weapon module's shape at the default zoom; tiers 1-6 add
small rank details (rank stripes, armour cladding at tiers 3 and 5).

### Bosses

Common to every boss (the sheet): a main boss 1.3-1.5 x its reference, a mini boss smaller than the main boss of its
line; each destructible part (turrets, tracks, engines) its own readable block with an intact and a broken version;
the owning general's stripe; the important parts (main turret, engines, factory doors) big and easy to aim at.
Daedalus was redrawn in this pass; Icarus (`silver_bug`) was reviewed and kept (DECISIONS 25B2).

| Boss | Rank | Size now | References in the note |
|---|---|---|---|
| rail_supergun | Mini | 54.3 x 7.5 x 14.0 | Schwerer Gustav (80 cm), Krupp K5, V 36 / D 311 armoured locomotives: an 80 cm railway super-gun. |
| behemoth_mk0 | Mini | (none given) | Landkreuzer P. 1000 Ratte, Object 279 (four tracks), 2A65 152 mm, Baneblade (Warhammer 40,000): a land battleship. |
| armored_train | Mini | 24.5 x 3.3 x 4.8 | Soviet BP-35 armoured train, B-38 152 mm, 2B11 120 mm: an armoured diesel locomotive pulling gun wagons. |
| behemoth_tempest | Mini | 16.2 x 6.6 x 6.4 | US Navy EMRG railgun, Ratte, Baneblade: a two-turret Behemoth. |
| locust | Mini | 25.4 x 12.6 x 10.6 | USS Akron / Macon, FPV drones, Kirov Airship (Red Alert 2): a small variant of the drone airship. |
| morrigan | Mini | 12.9 x 8.4 x 2.2 | (no reference given) |
| behemoth_mk2 | Mini | 16.1 x 9.6 (height not given) | Ratte, Object 279, Baneblade: the second-generation Behemoth. |
| landing_hovercraft | Mini | 24.9 x 13.5 x 7.7 | LCAC, Zubr (Project 1232.2), A-22 Ogon 140 mm, AK-630: a landing hovercraft. |
| argus | Mini | 29.6 x 20.5 x 10.5 | USS Akron / Macon, Zeppelin, Kirov Airship: a variant of the command airship. |
| ixion | Mini | 21.7 x 19.0 x 11.9 | Tsar Tank (Lebedenko, 1915), Ork deff rolla, the Locust machines (Gears of War), Shagohod (MGS3). |
| fortress_hive | Mini | 16.4 x 9.3 x 8.5 | NASA Crawler-Transporter, Lancet-3, Patriot, Sandcrawler: a tracked fortress carrying a drone hive. |
| caspian | Mini | 52.9 x 39.0 x 16.0 | Lun-class ekranoplan MD-160 ("Caspian Sea Monster"): a ground-effect craft. |
| supreme_command | Mini | 12.4 x 4.3 x 9.5 | MZKT-7930 chassis, an armoured mobile headquarters: a super-heavy four-axle command vehicle. |
| sky_fortress | Mini | 19.4 x 24.6 x 7.7 | AC-130 Spectre: the AC-130 scaled 1.3 and painted dark. The AC-130 is now the shared C-130 airframe (11.9 x 16.3 m): this boss should become that airframe x 1.3. |
| icarus_mk0 | Mini | 24.1 x 16.2 x 5.8 | Polyus / Skif-DM, ISS, Hubble, SOLG (Ace Combat 5), The Expanse: Icarus's first version (it is Icarus at 0.65). |
| behemoth_inferno | Mini | 12.8 x 6.6 x 5.6 | TOS-1A, Ratte, Baneblade: a flame Behemoth with red fuel tanks. |
| fenrir | Mini | 16.2 x 9.1 x 8.3 | Antarctic Snow Cruiser (1939), Crawler-Transporter, Sandcrawler: a variant of the mobile fortress. |
| mega_gunship | Mini | 23.6 x 15.3 x 7.0 | CH-47 Chinook frame, ACH-47A "Guns-A-Go-Go": a heavy armed tandem-rotor helicopter. |
| behemoth | Main | 22.3 x 13.3 x 9.6 | Ratte, Object 279 (four tracks), 2A65 152 mm, Baneblade: a land battleship. |
| earth_borer | Mini | 19.9 x 4.9 x 5.9 | Soviet "Battle Mole", tunnel-boring machines, 2A70 100 mm: a three-segment armoured "Earth Worm". |
| bastion_mk0 | Mini | 25.0 x 10.3 x 10.1 | 2B8 240 mm, Bofors 40 mm, Sandcrawler: the first, smaller Bastion. |
| nuke_train | Main | 61.6 x 5.1 x 7.4 | RT-23 Molodets (BZhRK missile train), Patriot: an armoured train carrying a ballistic missile. |
| scylla | Mini | 48.8 x 9.2 x 14.2 | IJN Yamato, Kirov class: a smaller Leviathan. |
| mobile_fortress | Main | 26.1 x 14.7 x 13.5 | Antarctic Snow Cruiser, Crawler-Transporter, 2A44 203 mm (2S7 Pion), Sandcrawler: a mobile fortress. |
| command_airship | Main | 59.2 x 41.0 x 20.9 | USS Akron / Macon, Zeppelin, Kirov Airship: "Sky Admiral", a flying battleship on two gas bags. At 59 m it is bigger than Icarus (see DECISIONS 25B2). |
| moloch | Main | 26.5 x 14.4 x 12.0 | A tracked mobile factory; Fatboy (Supreme Commander), MCV / War Factory (Command & Conquer). |
| fortress_bastion | Main | 35.8 x 14.7 x 14.4 | 2B8 240 mm, Bofors 40 mm, Kornet, Sandcrawler: a tracked fortress in thick plate armour. |
| typhon | Main | 59.0 x 12.2 x 14.1 | Project 941 Akula (Typhoon), The Hunt for Red October: a missile submarine. |
| kronos | Main | 48.5 x 16.2 x 16.0 | Bagger 288: a giant bucket-wheel excavator. |
| leviathan | Main | 97.6 x 18.5 x 28.5 | IJN Yamato (1945 fit), Kirov class, Iowa class (1980s missile refit): a battleship on Yamato's lines. |
| drone_mothership | Main | 42.3 x 21.0 x 17.7 | USS Akron / Macon (the mother airship), FPV drones, Kirov Airship: an armoured airship launching drones. |
