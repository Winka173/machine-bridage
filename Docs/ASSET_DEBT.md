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
