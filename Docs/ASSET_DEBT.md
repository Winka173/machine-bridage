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

