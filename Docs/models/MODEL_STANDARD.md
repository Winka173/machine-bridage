# Model standard (fix pass 8)

Source: Docs/prompts/fix_full_vi.txt "Lượt 8" item 1 (owner, 2026-10-02); DECISIONS "Sửa lỗi tổng hợp L8 prep".
Where this file and Docs/models/BUDGETS.md disagree, this file decides how a model is **scored**. L9 item 7 is
`python Tools/balance/fix_validate.py 7` (budget information only, the parts and LOD1 against the pass 8 scores); the
prompt 27 caps in `Tools/assets/glb_check.py` stay an error gate for draw calls, while their triangle and vertex caps
only warn (the owner's rule of 02/10).
Checked statically by `python Tools/models/scan_prep.py` (Docs/models/scan/static_scores.csv) and visually on the
sheets that `MachineBrigade.Editor.ModelScan.RenderBatch` draws (Docs/models/scan/README.md).

## 1. Triangle budgets

LOD0 = the normal GLB (every platform loads it; phones only load this one). The `_hd` twin (the PC High tiers) may
carry up to 2.4 x the class maximum (BUDGETS.md's median `_hd` / normal ratio). The scorer reports it but does not
grade on it.

**Owner rule (02/10): a model over its budget is kept.** Budgets are a guide, not a cap; the scorer reports
over-budget as information only and never grades a model down or cuts it for that (DECISIONS "Owner: over-budget
models are fine").

| class (scorer) | what | LOD0 triangles |
|---|---|---|
| light | wheeled and other light vehicles (trucks, cars, APCs on wheels) | 3,000-5,000 |
| heavy | tanks, tracked and heavy vehicles (tracked, or class Tank / Heavy) | 4,000-7,000 |
| jet, helicopter | aircraft and helicopters | 4,000-7,000 |
| air_other | drop pods, parachute loads | at most 7,000 |
| ship | ships (`naval`) | 8,000-15,000 |
| boss | bosses (every frame) | 10,000-20,000 |
| tower | towers (defs with `fort`, their branch `_a` / `_b` models) | 2,000-4,000 |
| structure, hq | other static structures; the HQs (`headquarters`, `command_hq`) | 2,000-6,000 |
| obstacle | walls, dragon's teeth, minefields (`wall`, `obstacle`, `passable`) | at most 6,000 |

- Below the minimum is a fault too (too little detail to read), not only above the maximum.
- **LOD1 ~50 %** of LOD0: the game builds it at run time (`ModelLibrary.Lod`, `MeshSimplifier`, half a pixel of
  error at the 128 px switch). ModelScan writes `triangles0` / `triangles1` per model; accepted band 35-65 %.
- **LOD2 ~20 %**: the impostor (`ImpostorAtlas`, below 24 px) takes this level for every vehicle. A model drawn large
  enough that its impostor is never used (bosses, ships) needs no mesh LOD2; if one is ever added, about 20 % of LOD0.

## 2. Minimum parts per class

A part is a named node. A role is met by a `Part_<role>` node **or** by the kit's merged-material node of that
part (the names in the table). Note: `Part_*` nodes are runtime parts (damage, boss parts): ModelLibrary keeps each as
a mesh of its own, so one draw and one shadow draw each. Do **not** add a `Part_*` node per wheel or per blade to pass
this list; "every road wheel", "every blade", "every barrel" are geometry rules, checked on the sheet (each wheel its
own disc with a hub, each blade its own blade). Roles marked (w) only apply when the def is armed; (t) only with a
turret (`turretTurnRate`).

| class | roles (accepted node names, start of the name) |
|---|---|
| tracked | hull (Hull, Body, Chassis); turret (t) (Turret, Casemate); mantlet (t) (Mantlet, Gun_mantlet, Elevation, Cradle); barrels (w) (Main_cannon, Barrel, Gun, Tubes, Launcher, Pod, Missiles, Mount_*); every road wheel (Wheels, Roadwheels, Bogies); drive sprocket (Sprockets); idler (Idlers); tracks with links / tread (Tracks, Track_links, Treads); side skirts (Skirts, Skirt_edge); hatches (Hatch, Hatches, Cupola); sights (Sight, Periscope, Optics, Sensor); roof MG (w) (MG, Mount_mg, Rws, Hmg); smoke dischargers (Smoke, Smoke_launchers, Smoke_brackets); stowage (Stowage, Tarp, Crates, Jerrycans, Bins, Racks, Straps, Ammo_boxes, Bags) |
| wheeled | every wheel (Wheels, Tyres); axles (Axles, Undercarriage, Suspension, Hubs); cab (Cab, Cabin, Hull, Body); glass (Glass, Windows, Windscreen, Lit_windows, Canopy, Visors); lights (Lamps, Lights, Headlights, Tail_lamps, Light_rims); stowage (as above); weapon (w) |
| jet | fuselage; cockpit glass (Canopy, Cockpit, Glass); wings with the reference's sweep and taper (Wing, Part_wing); horizontal and vertical tail (Tail, Fins, Tailplane, Stabilator, Rudder); intakes (Intake, Intake_lips, Inlet); exhausts (Nozzle, Exhaust); pylons (Pylons, Hardpoints, Racks); stores on them (Missiles, Bombs, Pods, Rockets, Drop_tanks); flare dispensers (Flares, Mount_flare) |
| helicopter | fuselage; glass (Canopy, Glass, Windows); rotor hub (Rotor_hub, Rotor_grips, Hub); every blade (Rotor_blades, Blades); tail rotor (Tail_rotor); landing gear (Undercarriage, Skids, Gear, Tyres); stub wings (Wing, Stub_wing, Pylons); weapons (Gun, Gun_turret, Missiles, Pods, Rockets, Launchers) |
| ship | hull with bow flare (Hull); superstructure tiers (Superstructure, Bridge, Deckhouse, Tier, Island, Funnel); radar mast (Mast, Radar, Antenna); every turret and barrel (Turret, Gun_house, Main_cannon, Barrel); CIWS (CIWS, Phalanx, AK630, Gatling, Mount_ciws); boats (Boat, RHIB, Lifeboat, Davit); deck details (Deck, Rails, Bollards, Hatches, Vents, Winch, Anchor) |
| tower, structure, hq | base (Base, Plinth, Footing, Emplacement, Pad, Foundation, Slab, Block, Race); sandbags / walls (Sandbags, Hesco, Wall, Parapet, Barriers, Blast_bags, Revetment, Berm, Coping); roof (Roof, Roof_deck, Canopy, Cupola, Tower_deck, Deck, Turret, Dome, Shelter); antennas (Antenna, Mast, Aerial, Radar, Dish, Flag_pole); faction detail differs (Accord: practical, field-built - sandbags, timber, nets; Hegemon: prefabricated - cast concrete, modular panels) - visual check |
| boss | body (Hull, Fuselage, Body, Chassis, Deck, Envelope, Gondola); weapons; by frame: running gear (ground: Tracks, Wheels, Bogies, Legs, Rail_wheels), lift (air: Rotor, Wing, Envelope, Propeller, Engine), superstructure (naval); and every `parts[].node` of its def present |
| obstacle | none (budget and look only) |

## 3. General rules

1. **Proportions within 10 %** of the real reference: width/length and height/length against
   `Docs/models/reference_dimensions.md` (data: `Tools/models/reference_real.json`). Absolute size is free (the game
   draws aircraft and ships smaller on purpose; the view fits the length to `modelSize`). Fictional designs
   (conf "inspiration") are not judged.
2. **No single-box turret or hull**: at least two stacked or angled volumes, sloped glacis / cheeks; large bevels on
   every big edge (the kit's chamfers), no 90-degree slab edge on a hull or turret read from 28 px per metre.
3. **Materials and detail colours separated**: hull paint, steel, rubber, glass, lamps, markings in their own
   materials (the kit's names), so the team colour and wear read.
4. **Mounts and muzzles**: a `Muzzle_<slot>` per barrel of every weapon (the weapon's `barrels`; a secondary on the
   main gun's slot shares its barrels); a `Mount_<slot>` per freely aimed (`aim: Free`) secondary; the main weapon on a
   `Turret` (or `Mount_<mainSlot>`) when the def turns a turret; `Mount_Flare` x 2 or more when the def has
   `flareCharges`; `Mount_APS` when it has `aps`. Bosses: as many `Muzzle_*` as `mountWeapons`, every part node.
5. **Readable silhouette at the normal camera distance**: the battle camera's default zoom (orthographic size 19 on
   a 1080 px screen = 28.4 px per metre, pitch 52). The ModelScan sheet shows exactly that; the type must be named from
   the left cell alone.

## 4. Grades

- **Kém** (poor): triangles over 1.5 x the class maximum or under half the minimum; 4 or more required parts missing;
  the main weapon's muzzle missing; proportions more than 25 % off a high-confidence reference; or the visual pass
  finds the silhouette unreadable / a box model.
- **Cần sửa** (needs fixing): any other fault above (over or under budget, 1-3 parts, a secondary muzzle or mount,
  Mount_Flare / Mount_APS, boss part node, proportions 10-25 %, LOD1 outside 35-65 %), or a visual fault.
- **Tốt** (good): nothing found, statically and on the sheet.
- Final grade = the lower of the static and the visual grade, with one exception: a "missing part" that the sheet
  shows modelled inside a merged node (an idler inside `Wheels`, a mantlet inside `Turret_body`) is cleared by the
  visual pass, which says so in its reason (the static check only sees node names). Old vs new (models rebuilt in prompt 27): the lower
  scoring version loses; when the new one scores lower, restore the old GLB or rebuild it to pass.

## 5. How the scorer assigns a class

Own def = the def whose id is the model, else the first def drawing it. HQ ids -> hq; `boss` -> boss; `naval` -> ship;
`flying` -> jet (`fixedWing`), helicopter (has a `Rotor*` node) or air_other; static or speed 0 -> obstacle (`wall`,
`obstacle`, `passable` or a wall / teeth / minefield id), tower (`fort` or `branchOf`; the `_a` / `_b` files) or
structure; otherwise tracked (Tracks / Sprockets nodes), wheeled (Tyres / Wheels nodes) or ground.
