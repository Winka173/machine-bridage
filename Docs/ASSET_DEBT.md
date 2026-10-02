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

## Prompt 25 B1 and B3: sizes (DECISIONS 25B)

| What | Uses now | Needs |
|---|---|---|
| Supply truck, counter-battery radar, Shahed truck, Iron Beam (the sheet: trucks 2.0 m wide, 2.1-2.8 m high) | Their old models fitted to the sheet's length (`modelSize`): 2.3-2.9 m wide, 3.5-3.9 m high | Models at the sheet's box (0.8 x real) for `"scale": 1`; the data fits any model's length, so nothing else changes |
| Self-propelled gun (M109A7, 7.8 x 3.1 x 2.9 m), siege tank (6.8 x 2.6 x 2.6 m), Pantsir (9.6 x 2.6 x 2.8 m) | The old models at the sheet's length: the gun 2.2 m wide, the siege tank 3.0 m wide, the Pantsir 3.4 m wide and 4.5 m high | Models at the sheet's box (the M109A7 is on B2's own list) |
| Kh-29L (`kh29l`) and GBU-39 SDB (`gbu39`) round models (Tools/blender/mb_munitions.py) | The Maverick and the GBU-12 (`WeaponEffects.RoundStandIns`), fitted to the new lengths, 1.95 and 0.9 m | Their own models: the Kh-29L a long, fat body with big cruciform wings (3.9 m real), the GBU-39 a slim body with folded wings (1.8 m real); any length, the data fits it |
| SAM launcher's Buk box, Patriot and 48N6 canisters | Boxes sized for the old rounds (the SAM launcher's 2.45 m); the rounds are 4.44, 4.24 and 6.0 m now | Launchers (sam_launcher, missile_battery, long_sam) whose boxes and tubes hold the sheet's rounds |
| Icarus at 60 m | The play-test 9 dagger hull, 30 m wide at that length | A planform nearer the sheet's ~60 x 40 m, if the owner wants its width too (its nodes kept where the boss data puts them) |
## Prompt 25 B2 (DECISIONS 25B2)

Part 2 rebuilt every vehicle left from part 1 (and the seven elites with models of their own) to the balance sheet's
shape notes and sizes, redrew the Sky Fortress, gave four structures that borrowed another model their own, and
reviewed the towers and the bosses against the sheet (DECISIONS 25B2 Part 2). The owner's rule for this pass was a
low effort: prompt 27 redoes every model with an upgraded kit. What is left is below.

### Vehicles

None left. The data changes they need are the lead's (DECISIONS 25B2 Part 2: `scale` 1.0 and `modelSize` = the built
box for every rebuilt model; the supply truck, ammunition carrier and escort hovercraft drop their borrowed `"model"`).

### Structures

The towers and their rank-7 branches match their notes (the branches differ in their weapon modules) and keep their
sizes; most are over the guide's tower budget of 1,500-3,500 triangles, left for prompt 27 (base / branch A / B):

| Tower | Triangles |
|---|---|
| aa_turret | 6,126 / 6,554 / 2,382 |
| cp_relay | 2,192 / 2,220 / 1,328 |
| dragons_teeth | 1,508 / 1,980 / 4,088 |
| ew_tower | 5,104 / 5,436 / 4,544 |
| guard_tower | 4,656 / 5,372 / 2,594 |
| mg_bunker | 3,404 / 3,704 / 3,560 |
| minefield | 3,150 / 3,732 / 4,512 |
| atgm_tower | 4,958 / 5,510 / 5,558 |
| c_ram | 5,806 / 6,254 / 7,150 |
| gun_turret | 6,112 / 6,384 / 6,688 |
| rocket_turret | 3,894 / 5,102 / 3,010 |
| artillery_emplacement | 7,334 / 7,766 / 5,770 |
| drone_hangar | 7,138 / 5,978 / 9,114 |
| heavy_turret | 9,222 / 9,378 / 11,666 |
| missile_battery | 6,926 / 8,338 / 6,974 |
| shield_tower | 5,344 / 7,200 / 6,176 |

Also kept: headquarters (14,260; its note: a multi-block concrete command building, antennas, sandbags),
ammo_depot (on ammo_dump: the berm-covered store with crates outside, as its note), bulwark_post (on mg_bunker at 0.8),
coastal_battery, spawn_bastion and super_gun (on heavy_turret; coastal_battery could wear the coastal branch's
heavy_turret_a instead, a data choice), targeting_station (no note). The Patriot's box (missile_battery) is 4.6 m long
along its tubes, so B3's 4.24 m round fits it.

### Bosses

Reviewed against the sheet's boss rules in part 2 and kept (DECISIONS 25B2 Part 2: their parts are nodes with wrecks,
the side's colour is on each, the mini bosses are smaller than their mains; Sky Fortress was redrawn on the shared
C-130, Daedalus in part 1, Icarus kept). What is left is detail for prompt 27's kit, the bosses under the guide's
15,000-triangle floor:

| Boss | Triangles | Needs |
|---|---|---|
| caspian | 5,054 | detail over its 52.9 m hull (Lun-class: the eight nose engines, the missile tubes on the back) |
| typhon | 6,348 | detail over its 59 m hull (the Typhoon's twin pressure hulls under the deck, the anechoic tiles) |
| moloch | 7,180 | the factory's doors and cranes in more detail |
| kronos | 8,404 | the Bagger 288's wheel, boom and conveyors in more detail |
| supreme_command | 9,118 | the MZKT-7930's cabs and the command module |
| mega_gunship | 11,304 | the Chinook frame's rotors and gun fit |
| morrigan | 1,312 | none if it counts as an aircraft (2,000-4,000); a stealth-fighter boss at 12.9 m |

## Prompt 25 batch B stand-ins (DECISIONS 25F2-B)

The owner's choice: every item below is complete (data, mechanics, AI, texts, unlock, card) but wears a borrowed
model with a tint (`"tint"` in balance.json, applied as VehicleView's own variant-tint multiply and by
`CardRenders.RenderBatch` on its card). Real models are prompt 26-27's.

| What | Uses now (borrowed model, tint) | Needs (the sheet's shape) |
|---|---|---|
| ~~`aa_57mm_vehicle`~~ | done in prompt 27 wave 1c pass A: its own `aa_57mm_vehicle` model (a 2S38 Derivatsiya-PVO: tracked chassis with skirts, boxy faceted turret with autoloader boxes, 57 mm barrel (baffle brake), spinning roof search radar `Radar`), wash dropped | - |
| ~~`mine_rocket_truck`~~ | done in prompt 27 wave 1c pass A: its own `mine_rocket_truck` model (a BM-27 Uragan-class 8x8 truck: forward cab, mine-dispensing 16-tube pod with a hazard band on a turntable (`Turret`, `Muzzle_main`)), wash dropped | - |
| ~~`prop_attack_plane`~~ | done in prompt 27 wave 1c pass A: its own `prop_attack_plane` model (a Super Tucano-class turboprop: lofted fuselage, straight wing, bubble canopy, spinning `Propeller`, two underwing rocket pods (`Muzzle_rocket`, `.001`), wing guns (`Muzzle_gun`)), wash dropped | - |
| ~~`light_attack_heli`~~ | done in prompt 27 wave 1c pass A: its own `light_attack_heli` model (a small stub-winged attack helicopter: tandem canopy, tail boom with fin, 4-blade `Rotor`, `Tail_rotor`, gun and rocket pods (`Muzzle_gun`, `Muzzle_rocket`, each with `.001`)), wash dropped | - |
| ~~`next_gen_tank`~~ | done in prompt 27 wave 1c pass A: its own `next_gen_tank` model (a T-14 Armata: low flat unmanned turret set back, ERA blocks, APS panels, remote MG (`Mount_mg`), 125 mm gun, side skirts, rear cage), wash dropped | - |
| ~~`demolition_line_vehicle`~~ | done in prompt 27 wave 1c pass A: its own `demolition_line_vehicle` model (an M58 MICLIC: tracked hull, two pushing arms with five-disc mine rollers ahead, line-charge rack with the rocket and cable box on the rear deck, remote MG turret), wash dropped | - |
| ~~`combat_wreck_car`~~ | done in prompt 27 wave 1c pass A: its own `combat_wreck_car` model (a light armoured pickup car with a roof gun post; the `Wreck_turret` node (a sandbag ring round the gun post) is built, the wreck-resolves-into-a-gun-pit rule is still game work), wash dropped | - |
| ~~`drone_hijack_vehicle`~~ | done in prompt 27 wave 1c pass A: its own `drone_hijack_vehicle` model (an 8x8 EW truck: cab, equipment shelter, phased-array hijack panel with yagi elements and a feed horn on the turning `Turret` (`Muzzle_main`), spinning sensor dish `Radar`), wash dropped | - |
| ~~`manpads_tower`~~ | done in prompt 27 wave 1c pass A: its own `manpads_tower` model (a sandbagged round pit with two shoulder-launched MANPADS tubes on a tripod head (`Turret`, `Muzzle_main`, `Muzzle_missile`, `.001`), crates, radio mast), wash dropped | - |
| ~~`river_patrol_boat`~~ | done in prompt 27 wave 1c pass A: its own `river_patrol_boat` model (a riverine command boat: V hull with chines, wheelhouse, twin outboards, pintle MG on the bow (`Turret`) and a grenade launcher aft (`Mount_mg` > `Muzzle_mg`)), wash dropped | - |
| ~~`river_gunboat`~~ | done in prompt 27 wave 1c pass A: its own `river_gunboat` model (a Buyan-class gunboat: flared low hull, faceted deckhouse with mast and radar, forward 100 mm turret, eight VLS cells, stern CIWS (`Mount_mg`)), wash dropped | - |
| ~~`coastal_ashm_vehicle`~~ | done in prompt 27 wave 1c pass A: its own `coastal_ashm_vehicle` model (an NSM Coastal Defence 6x6 truck: cab, flatbed, turntable (`Turret`) with four angled missile canisters (`Muzzle_main`), jacks), wash dropped | - |
| ~~`auto_loader_howitzer`~~ | done in prompt 27 wave 1c pass A: its own `auto_loader_howitzer` model (an XM2001 Crusader: wide tracked hull with skirts, faceted turret with a big autoloader bustle, cradle (`Main_cannon_cradle`), 155 mm barrel with baffle brake, roof MG), wash dropped | - |
| ~~`amphib_light_vehicle`~~ | done in prompt 27 wave 1c pass A: its own `amphib_light_vehicle` model (an EFV / AAV-7: slab-sided boat hull on narrow tracks, sloped planing bow with a folded trim vane, rear ramp, small right-front turret (25 mm, coax)), wash dropped | - |
| ~~`airborne_light_tank`~~ (+ `airborne_light_tank_chute`) | done in prompt 27 wave 1c pass A: its own `airborne_light_tank` model (an M10 Booker: light hull on six road wheels, low flat turret with a big mantlet and bustle, 105 mm barrel with baffle brake; its `airborne_light_tank_chute` proxy is the same tank under a 9 m 12-gore canopy with rigging (9 x 9 x 11 m, a leaner tank body)), wash dropped | - |
| ~~`stealth_naval_strike`~~ | done in prompt 27 wave 1c pass A: its own `stealth_naval_strike` model (an A-12 Avenger II: flat-iron flying wing (one loft, 35 degree leading edge, clipped tips with fold seams), flush canopy, dorsal intakes, exhaust troughs, weapon bays (`Muzzle_rocket`, `.001`), `Bombs` rack (`Muzzle_missile`)), wash dropped | - |
| ~~`twin_rotor_gunship`~~ | done in prompt 27 wave 1c pass B: its own `twin_rotor_gunship` model (an ACH-47A Guns-A-Go-Go: a boxy fuselage with a three-blade `Rotor` forward and `Rotor_rear` on a tall aft pylon between two nacelles, side gun sponsons (`Muzzle_mg`, `.001`), chin turret (`Muzzle_gun`); modelSize width 16.3 -> 5.7), wash dropped | - |
| ~~`ground_drone_carrier`~~ | done in prompt 27 wave 1c pass B: its own `ground_drone_carrier` model (a THeMIS / Uran-9 tracked carrier with a remote turret (`Turret`, `Muzzle_main`) and three docked minion robots (`Minion_1` .. `Minion_3`, nodes only; the spawn mechanism is still open)), wash dropped | - |
| ~~`mobile_repair_vehicle`~~ | done in prompt 27 wave 1c pass B: its own `mobile_repair_vehicle` model (an MTO-UB 6x6 repair truck: workshop box, slewing crane (`Crane`), welding rig, outriggers, roof RWS (`Turret`, `Muzzle_main`)), wash dropped | - |
| ~~`radar_support_vehicle`~~ | done in prompt 27 wave 1c pass B: its own `radar_support_vehicle` model (a Giraffe AMB 4x4 radar truck: equipment box, raised telescopic mast with a turning array (`Radar`), jacks, roof RWS), wash dropped | - |
| ~~`towed_at_gun`~~ | done in prompt 27 wave 1c pass B: its own `towed_at_gun` model (a 2A45 Sprut-B: long smoothbore barrel with baffle brake (`Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`), gun shield, two wheels, split trails), wash dropped | - |
| ~~`flare_searchlight_tower`~~ | done in prompt 27 wave 1c pass B: its own `flare_searchlight_tower` model (a braced steel lattice post with deck, ladder, flare launcher on a turntable (`Turret`, `Launcher`, `Tubes`, `Muzzle_main`), floodlight, flare drums), wash dropped | - |
| ~~`recoilless_gun_tower`~~ | done in prompt 27 wave 1c pass B: its own `recoilless_gun_tower` model (an SPG-9 emplacement: round sandbagged pit, tripod head, short recoilless tube (`Turret`, `Cradle`, `Main_cannon`, `Muzzle_main`), shield, rounds), wash dropped | - |
| ~~`bunker_shelter_tower`~~ | done in prompt 27 wave 1c pass B: its own `bunker_shelter_tower` model (a concrete bunker: Team roof slab, earth berms, entrance porch with steel door, sandbag piles, roof vents (no weapon node)), wash dropped | - |
| ~~`dazzler_vehicle`~~ | done in prompt 27 wave 1c pass B: its own `dazzler_vehicle` model (a Peresvet-class 8x8 EW truck with a lift-frame housing of six glowing lenses, roof RWS (`Turret`, `Muzzle_main`)), wash dropped | - |
| ~~`ground_cruise_missile_vehicle`~~ | done in prompt 27 wave 1c pass B: its own `ground_cruise_missile_vehicle` model (a Typhon MRC tractor and trailer with two long vertical canisters on a turntable (`Turret`, `Muzzle_main` at the tops)), wash dropped | - |
| ~~`aerial_tanker`~~ | done in prompt 27 wave 1c pass B: its own `aerial_tanker` model (a KC-135 / Il-78 tanker: glazed nose, swept wings, four turbofans, wingtip hose pods, refuelling boom under the tail (`Muzzle_gun`)), wash dropped | - |
| ~~`heavy_lift_helicopter`~~ | done in prompt 27 wave 1c pass B: its own `heavy_lift_helicopter` model (a Mi-26 class heavy-lift helicopter: six-blade `Rotor`, nose glazing, roof engines, `Tail_rotor`, sponsons with wheels, cargo hook), wash dropped | - |
| ~~`bridging_vehicle`~~ | done in prompt 27 wave 1c pass B: its own `bridging_vehicle` model (an MTU-72 bridgelayer: tracked hull with skirts, folded two-half scissor bridge on rams, driver hatch, fender RWS (`Turret`, `Muzzle_main`)), wash dropped | - |
| ~~`gps_jammer_vehicle`~~ | done in prompt 27 wave 1c pass B: its own `gps_jammer_vehicle` model (a Pole-21 class 8x8 truck: shelter, flatbed with stowed antenna sections, tall mast with a turning three-tier dipole array (`Radar`), roof RWS), wash dropped | - |
| ~~`drone_net_tower`~~ | done in prompt 27 wave 1c pass B: its own `drone_net_tower` model (two poles on concrete bases with splayed A-frame legs, netting between them, a zap emitter ball on each pole top (`Turret`, `Muzzle_main` on the first)), wash dropped | - |
| ~~`one_shot_atgm_tower`~~ | done in prompt 27 wave 1c pass B: its own `one_shot_atgm_tower` model (a concrete pedestal with sandbag apron, Team roof deck, turntable with a box of eight ready-to-fire Kornet tubes (`Turret`, `Launcher`, `Tubes`, `Muzzle_main`, `Muzzle_missile`, `.001`), no spare missiles), wash dropped | - |

## Prompt 25 batch D stand-in bosses (DECISIONS 25F2-D)

All eight have their own models since prompt 27 wave 1b (no tint; cards of their own). What stays open is game work for prompt 28.

| Boss | Stand-in (parent, tint) | The real model |
|---|---|---|
| ~~`kraken`~~ | done in prompt 27 wave 1b: its own `kraken` model (a Kuznetsov / Nimitz-style carrier: ski-jump, island, lifts, parked jets, arresting wires on `Part_deck`, 4 CIWS, 2 SAM box launchers), wash dropped. Still open: the runway / arresting-cable rule and the air wing as units (game work, prompt 28); the weapon list is still Leviathan's (see the last row) | - |
| ~~`monster`~~ | done in prompt 27 wave 1b: its own `monster` model (an 800 mm SPG after 2B1 Oka / Object 271 on the four-cluster layout; nodes `Part_track` .. `.003`, `Part_barrel`), wash dropped. Still open: no part names the track or barrel nodes (a track-break rule is game data, prompt 28) | - |
| ~~`garuda`~~ | done in prompt 27 wave 1b: its own `garuda` model (a 70 m flying wing, sawtooth trailing edge, 6 turrets), wash dropped; bomb bay doors built as `Part_bay` / `.001` (closed). Still open: the opening bay view and the circling course (prompt 28) | - |
| ~~`hyperion`~~ | done in prompt 27 wave 1b: its own `hyperion` model (hexagonal mirror ring, core, solar booms, 4 PD lasers, 2 landing pods on `Pod_bay`), wash dropped; silver_bug / icarus untouched | - |
| `stymphalos` | model done in prompt 27 wave 1b: `stymphalos` (eight delta-wing jet drones in V formation, each on `Part_drone` .. `.007`) and `stymphalos_drone` (one drone, unlisted), wash dropped | the swarm rule: eight separate units of 1,300 health each, spawned from those nodes (game work, prompt 28) |
| ~~`nyx`~~ | done in prompt 27 wave 1b: its own `nyx` model (Zumwalt-style), wash dropped | - |
| `cerberus` | model done in prompt 27 wave 1b: `cerberus` (three big-wheeled cars on `Part_tractor` / `Part_middle` / `Part_trailer`), wash dropped | the coupling rule (the middle car breaks first and takes the AA with it; parts naming those nodes) is game work (prompt 28) |
| `hydra` | model done in prompt 27 wave 1b: `hydra_sub` (a small VLS submarine, six FPV drones on `Part_drone` .. `.005`), wash dropped | the drones' launch from those nodes (game work, prompt 28) |
| Weapon lists | the parent's | each sheet weapon list on its own mounts (see 25F2-D); the sun beam's smoke cut; the In-action clips of the four super weapons |


## Prompt 26 pass 2 stand-ins (DECISIONS 26CD)

| What | Stand-in now | The real thing |
|---|---|---|
| ~~Ixion, the armoured BelAZ-75710 mine truck~~ | done in prompt 27 wave 1a: its own `ixion` model (26 x 12 x 10 m, mb_p27_wave1a), tint dropped | - |
| Boss sizes | the old models scaled by `size` (Roc and Garuda stay 56-62 m wide, Icarus 45 m wide, Moloch and Bastion keep their proportions) | models rebuilt at the sheet's sizes (prompt 27) |
| Gungnir's electromagnetic gun | model done in prompt 27 wave 1a (`rail_supergun`: EMRG launcher, two capacitor cars; `rail_tractor`: a modern Bo-Bo diesel); the slug is still the existing rail slug projectile | the line warning along the slug's path (game code, prompt 28) |
| ~~Ixion's parts: `reartyre`, `hulltower`~~ | done in wave 1a: every tyre (`Part_wheel`, `.001`, `Part_tyre` .. `.003`), the cab (`Part_cab`) and the turret (`Turret`) are nodes the parts name, hidden when broken | - |
| Ixion's mine strip | the ordinary mine model (MineViews spawns `mine` for every layer); the model has `Point_mines` at the dispenser's mouth, unused | a mine truck's own mine model and the view lookup per layer (game code, prompt 28) |
