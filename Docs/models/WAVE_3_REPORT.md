# Prompt 35 wave 3 report (lane B)

Wave 3 of prompt 35 (sections 7 and 8; plan: Docs/models/WAVES_P35.md): the twenty models of the wave, all done by
lane B on branch `feature/p35-w3` (from lead/integration, lead/integration with wave 2 merged in on the way). Each
model has its own new Blender script (`Tools/blender/mb_p35_<id>.py`) and a build spec written first
(`Tools/blender/specs/<id>.json`); the builders are registered last in `build_assets.py`. Decisions: Docs/DECISIONS.md
"Prompt 35 wave 3 (lane B)". Blender and Python only: no Unity run, no test, sim or measure.

Gate: `Tools/assets/quality_gate.py` (hard gates + the 0-100 soft score against the gold of the class; Tốt >= 80).
Owner review of wave 1: structures are judged on the owner's look; over-cap towers are trimmed when rebuilt (towers at
most 1.5 x 4,000 = 6,000 triangles); elites keep team bodies (none in this wave); roof guns on raised mounts.

## Rows

"Before" = the committed GLB at the start of the wave (its row in quality_report.csv). Every row passes every hard gate
(parts, mounts and muzzles, size, own geometry, zero-area, COLOR_0, colour zones, AO / dust / wear, not a single
block), the spec check (`validate_specs.py --glb <id>`: every named node, the size within 10 %) and glb_check
(accepted, 0 errors). Size = L x W x H in metres (target: modelSize, or the old file where the data has none).
"Shared" = triangles also found in another model family (limit 30 %).

| model | class | real reference | triangles before -> after | size (target) | soft before -> after | rounds | status | shared |
|---|---|---|---|---|---|---|---|---|
| `wall_hesco` | obstacle | HESCO MIL 7-class cells, concertina on pickets | 3,276 -> 4,444 | 2.0 x 12.0 x 2.76 (2.0 x 12.02 x 2.75) | 58.8 -> 69.9 | 3 | owner's look | 0.3 % (was 47 %) |
| `wall_gun` | obstacle | MIL 1 breastwork with fire step + timber crib firing platform | 2,672 -> 5,440 | 2.16 x 12.0 x 2.76 (2.16 x 12.02 x 2.75) | 57.3 -> 63.5 | 2 | owner's look | 0.3 % (was 40 %) |
| `wall_t` | obstacle | eight Bremer-class T-wall panels | 1,798 -> 4,722 | 1.9 x 12.0 x 3.92 (same) | 31.2 -> 57.1 | 2 | owner's look | 1.4 % |
| `blast_wall` | obstacle | stepped stone-filled gabions, sandbag crest | 792 -> 3,500 | 1.91 x 4.75 x 2.40 (1.9 x 4.8 x 2.4) | 35.6 -> 61.6 | 3 | owner's look | 0.1 % |
| `aa_gun_tower` | tower | Bofors 40 mm L/70 on its cruciform carriage, FC radar | 1,724 -> 5,924 | 5.13 x 5.41 x 3.18 (5.5 x 5.5 x 3.2) | 28.6 -> 80.1 | 2 | Tốt | 5.8 % |
| `at_gun_emplacement` | tower | MT-12 Rapira 100 mm on split trails | 1,384 -> 4,974 | 5.83 x 4.36 x 1.99 (5.8 x 4.2 x 2.0) | 42.3 -> 77.9 | 4 | NEEDS_HUMAN | 2.8 % |
| `heavy_flak_tower` | tower | KS-19 100 mm in a log-revetted pit, rangefinder | 8,902 -> 5,880 | 7.05 x 6.09 x 3.19 (7.0 x 6.0 x 3.4) | 45.6 -> 66.6 | 4 | NEEDS_HUMAN | 3.0 % |
| `searchlight` | tower | Sperry 60-inch searchlight on its trailer, generator | 1,292 -> 4,946 | 3.49 x 3.11 x 2.78 (3.6 x 3.0 x 2.8) | 42.7 -> 87.7 | 2 | Tốt | 9.3 % |
| `one_shot_atgm_tower` | tower | eight-round Kornet-class remote launcher on a sleeper crib | 2,186 -> 5,966 | 4.40 x 4.54 x 3.57 (4.8 x 4.8 x 3.6) | 38.0 -> 74.6 | 4 | NEEDS_HUMAN | 2.3 % |
| `laser_ad_station` | tower | Iron Beam / DragonFire director on a power shelter | 3,434 -> 5,592 | 5.90 x 4.27 x 4.69 (6.0 x 4.0 x 4.6) | 42.7 -> 73.0 | 4 | NEEDS_HUMAN | 4.2 % |
| `fire_control_centre` | tower | field FDC: log dug-out, ops tent, guyed radar mast | 2,874 -> 4,990 | 5.89 x 6.24 x 5.25 (6.0 x 6.0 x 5.5) | 43.2 -> 63.1 | 4 | owner's look | 2.2 % |
| `troop_shelter` | tower | half-buried cast concrete bunker, blast baffle | 3,158 -> 3,914 | 6.08 x 4.95 x 2.26 (6.0 x 5.0 x 2.2) | 33.1 -> 51.3 | 2 | owner's look | 5.6 % |
| `bunker_shelter_tower` | tower | earthed corrugated steel arch (Elephant / Nissen) | 1,228 -> 5,034 | 6.16 x 5.15 x 2.31 (6.0 x 5.0 x 2.2) | 24.5 -> 51.5 | 1 | owner's look | 6.6 % |
| `inflatable_decoy` | tower | inflatable gun-turret decoy on a blower | 1,378 -> 3,088 | 5.33 x 4.84 x 2.54 (5.0 x 4.6 x 2.6) | 34.1 -> 59.8 | 3 | owner's look | 5.7 % |
| `barrage_balloon` | tower | JLENS aerostat on its mobile mooring station | 1,748 -> 3,930 | 8.89 x 4.12 x 16.16 (9.0 x 4.0 x 16.0) | 33.7 -> 91.6 | 1 | Tốt | 3.2 % (was 39 %) |
| `super_gun` | structure | twin heavy coastal turret on a concrete citadel, shell hoist | 4,266 -> 7,132 | 9.96 x 7.33 x 5.10 (10.4 x 8.0 x 5.2) | 59.0 -> 82.6 | 3 | Tốt | 2.0 % |
| `ifv` | tracked | M2A2 Bradley (30 mm, coax, side TOW) | 5,040 -> 9,466 | 5.75 x 2.99 x 2.62 (5.48 x 3.02 x 2.5) | 85.4 -> 96.5 | 2 | Tốt | 6.7 % |
| `light_tank` | tracked | PT-76 / ZBD-05 boat hull, long 57 mm | 4,350 -> 8,054 (_hd 9,118) | 6.52 x 2.50 x 2.02 (6.39 x 2.61 x 1.89) | 74.7 -> 85.1 | 3 | Tốt | 8.9 % |
| `engineer_vehicle` | tracked | BREM-1 / M88A2: crane, dozer blade | 3,670 -> 8,144 | 6.26 x 3.05 x 2.07 (6.45 x 3.02 x 2.02) | 75.3 -> 100 | 3 | Tốt | 11.9 % (was 51 %) |
| `mortar_carrier` | tracked | M1064 (M113 + 120 mm mortar) | 3,242 -> 8,422 | 4.54 x 2.28 x 3.29 (4.21 x 2.3 x 3.2) | 77.1 -> 100 | 2 | Tốt | 8.3 % |

Before, all twenty failed the gate (Kém or a hard fail: the triangle floor, missing roles such as walls / roof /
antenna / mantlet / idler / roof_mg, sizes 12-23 % off, 40-51 % shared geometry, no wear in COLOR_0, single blocks).
After: every hard gate passes; 10 Tốt, 4 NEEDS_HUMAN (towers with a gun), 6 structures and walls on the owner's look.

What each one is (section 7's identifying features; details in its spec):

- **Walls** (the wall system tiles them: each box kept to the centimetre, centred, along X, front to -Y, as before;
  WallRules / BaseSystem place a segment by its centre and stand the gun wall's tower at the same deck height):
  wall_hesco eight MIL 7-class cells in beige geotextile behind welded mesh, coil pins, heaped tops, concertina on
  pickets; wall_gun 1 m cells two tiers high at the front and one at the back (a fire step with duckboards) either
  side of a 4 m timber crib platform at the old 1.28 m deck, sandbag parapet, revetment, ladder; wall_t eight T-wall
  panels in two casting shades on a gravel bed, lifting loops, forklift slots, streaks, sandbagged joints; blast_wall
  stone-filled gabions stepped back, the stones against the mesh, a sandbag crest.
- **Gun towers** (Accord field-built: earth pads, sandbags, timber, nets): aa_gun_tower the L/70 on its outriggers in a
  sandbag pit, clip racks, the fire-control dish on a tripod; at_gun_emplacement the MT-12 with spades dug in, a
  three-course sandbag horseshoe, a net over the crew corner, an ammunition niche; heavy_flak_tower a KS-19-class gun on
  a pedestal in an octagonal pit of stacked logs (each cut differently) with a sandbag crest, the rangefinder on a
  tripod, shell racks; one_shot_atgm_tower eight Kornet-class containers on a remote turning mount on a sleeper crib,
  the operator's foxhole under a net; laser_ad_station the beam director on a power and cooling shelter with chiller,
  radar mast and APS sensor, generator; searchlight the 60-inch light with its louvred lens door on a levelled trailer.
- **Structures**: fire_control_centre a log-and-earth dug-out, the canvas plotting tent, a guyed mast with the radar
  still spinning (`Radar`), 5.25 m tall (the old file was 6.8 m against the data's 5.5 m); troop_shelter a cast
  concrete bunker under earth and sandbags, turned to its modelSize (the old file lay across); bunker_shelter_tower an
  earthed steel arch with a sandbag front wall and a plank porch (its body differs from troop_shelter's);
  inflatable_decoy an inflatable turret in a printed lobe ring, sagging barrel, tethers, blower (it copies the gun
  turret's outline, not its geometry; no Turret pivot: the def is unarmed); barrage_balloon the JLENS envelope with
  inverted-Y fins and belly radome over its mooring station (the old file was 39 % c_ram_a); super_gun the fortress's
  twin turret on a concrete citadel with rangefinder arms, shell hoist, trolley rails and gantry crane.
- **Vehicles**: ifv an M2A2 Bradley (box hull, bolted skirts, offset turret, side TOW box that the runtime raises,
  the commander's pintle M240); light_tank a PT-76 / ZBD-05-line boat hull with trim vane and water jets, a compact
  turret with the long 57 mm (light_tank_hd from the same builder with more segments); engineer_vehicle a BREM-1-class
  hull with casemate, a slewing crane folded diagonally across the deck, the dozer blade on its `Blade` pivot (the
  runtime rams it), the M2 on a raised cupola ring; mortar_carrier an M1064 on its own M113 hull, the three-leaf hatch
  open and the 120 mm raised 70 degrees.

## NEEDS_HUMAN

Four towers with a gun stayed under 80 after four rounds (every hard gate passes; the old files scored 38-46):

- **at_gun_emplacement 77.9, heavy_flak_tower 66.6, one_shot_atgm_tower 74.6, laser_ad_station 73.0.** Open gun pits
  and a container site against the tower gold (seven dense gun towers): their edges and brightness regions per pixel
  stay low over earth, logs and a flat shelter at the battle camera's 28 px per metre, and the 6,000-triangle cap
  leaves no room for more small parts (heavy_flak_tower was trimmed from 8,902). The owner's look decides.

Structures and walls under 80 (fire_control_centre 63.1, troop_shelter 51.3, bunker_shelter_tower 51.5,
inflatable_decoy 59.8, the four walls 57.1-69.9) are judged on the owner's look (review of wave 1, item 1). Walls cannot
score asymmetry (their top view is the full segment rectangle, which the wall system needs).

## Pictures

Before / after sheets (Blender Workbench, material colours: front, rear, side, top, 3/4 front, 3/4 rear, and the battle
angle at the default zoom's 28.4 px per metre, x2): `Docs/models/rebuild/<id>/before_after.png` for the twenty ids.

**For the lead to render in Unity (cards and ModelScan).** Cards (CardRenders) for the seventeen ids with a card:
blast_wall, aa_gun_tower, at_gun_emplacement, heavy_flak_tower, searchlight, one_shot_atgm_tower, laser_ad_station,
fire_control_centre, troop_shelter, bunker_shelter_tower, inflatable_decoy, barrage_balloon, super_gun, ifv, light_tank,
engineer_vehicle, mortar_carrier. **No card: wall_hesco, wall_gun, wall_t** (balance.json `card: false`). ModelScan:

```
MachineBrigade.Editor.ModelScan.RenderBatch -mbScan "wall_hesco,wall_gun,wall_t,blast_wall,aa_gun_tower,at_gun_emplacement,heavy_flak_tower,searchlight,one_shot_atgm_tower,laser_ad_station,fire_control_centre,troop_shelter,bunker_shelter_tower,inflatable_decoy,barrage_balloon,super_gun,ifv,light_tank,engineer_vehicle,mortar_carrier"
```

Points to look at in Unity: the three wall segments tiling end to end (boxes unchanged) and the gun wall's tower on
its deck; the ifv's TOW box raising (Launcher_arm / Launcher_box / Tubes / Muzzle_missile stay direct children of
Turret); the engineer vehicle's blade ram (`Blade` now pivots at the push arms' hinge); the fire-control radar
spinning; the light tank's _hd on PC High; the super-gun's two barrels firing in turn.

## Roof guns

Every roof gun of the wave stands on `mb_p35b_parts.raised_gun` (riser ring or post, cradle, receiver, ammunition can,
shield where the real one has it): ifv (the commander's pintle M240), light_tank (cupola 7.62 mm), engineer_vehicle
(M2 on the cupola ring: its main weapon), mortar_carrier (M2 on the cupola ring), and the AA / AT / flak guns stand on
their own carriages.

## The whole gate after the wave (no old model broken)

`python Tools/assets/quality_gate.py --no-write` over all 230 scored models: 59 pass the whole gate. Compared with the
lead's quality_report.csv (after wave 2) no model outside the wave changed its hard result or its soft score by more
than 0.5, and no other model's own-geometry check names a wave 3 model. glb_check: 0 errors; warnings only for the four
vehicles over the ground budget (triangles 8,054-9,466 against 7,800; ifv's vertices 12,809 over the 12,600 hard cap,
kept by the owner's rule) and fire_control_centre's renderers (42 against 39). quality_report.xlsx / .csv are not
rewritten on this branch (the lead's run after the merge refreshes them).

## Kit requests (for lane A, mb_kit35.py)

1. `track_run` (lane B's `mb_p35b_parts.track_run`: belt outline round sprocket, idler and wheels, links all round with
   the skirt-hidden top run left out, wheels, sprocket, spoked idler on its arm, return rollers) is generic; worth a
   kit function, since `K.tracks` builds the prompt 27 unit.
2. `sandbag_run(part=, lean=)`: kit `sandbag_wall` writes a fixed part name and always rounds the bags; structures
   want the name (Parapet, Walls, Porch) for their gate roles and a square-cornered bag (36 against 60 triangles) for
   long runs under the tower cap.
3. `camo_net` (poles, a sagging two-sided net, scrim tufts) and `earth_pad(bottom=False)` (an irregular dug pad without
   the face on the ground, which only inflates the area the densities divide by).
4. `door(mat=)` is used with 'Wood'; a `frame_mat` switch would let timber walls get timber frames.

## Owner questions

1. The four gun towers above (77.9, 74.6, 73.0, 66.6): accepted on the look like the structures, or another round?
2. inflatable_decoy copies the gun turret's outline (sandbag ring, drum, dome, long barrel) as an inflatable; the gun
   turret itself was rebuilt in wave 2 in parallel. Should the decoy follow the new gun turret's outline more closely?
3. super_gun is the fortress's own (cast concrete and armour with the garrison's sandbags) rather than the Accord's
   field-built style the other structures follow. Fine?
