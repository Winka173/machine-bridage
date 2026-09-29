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
| Parts with no node of their own | A place on the hull: the Iron Train's locomotive and second gun car, the Behemoth's and Iron Bird's missile and rocket racks, the Silver Bug's coilgun, bay, shield and EMP emitters, the Hive's EMP emitter, the Hive Mothership's bay, UAV bay and shield | Their own nodes (`Part_*`) in the models, so they can be hidden and replaced like the others |
| Heat haze round the fires (High) | Not drawn: the pipeline has no distortion pass | A screen-space distortion pass, or a refraction particle material |
| Electric arcs on broken energy parts | Glow points along a jagged line (`Emitters.Charge`) and blue sparks | A proper arc (line renderer with a noise texture) |
| Fire crackle | The shared fire loop, louder near a burning boss | Its own crackle for a boss's fires |
| Rail Supergun's tractors | Their broken piece is a stump on their deck | A burnt-out tractor model |

## Prompt 16 (old bosses' weapons, escorts)

| What | Uses now | Needs |
|---|---|---|
| Hover gunboat (`hover_gunboat`, the landing hovercraft's escort) | The landing hovercraft's model at 0.34 scale | The fleet's fast attack craft model (prompt 16 C) once it lands, or its own small air-cushion gunboat |
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
