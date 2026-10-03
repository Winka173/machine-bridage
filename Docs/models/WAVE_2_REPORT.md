# Prompt 35 wave 2 report (lane A)

Wave 2 of prompt 35 (sections 7 and 8; the list in Docs/models/WAVES_P35.md), after the owner approved wave 1 with the
lead's defaults (DECISIONS "Prompt 35: owner review of wave 1 (2026-10-03)"). Branch `feature/p35-w2` from
`lead/integration`. Decisions: Docs/DECISIONS.md "Prompt 35 wave 2 (lane A)". Blender and Python only: no Unity run,
no test, sim or measure.

Gate: `Tools/assets/quality_gate.py` (hard gates + a 0-100 soft score against the class gold; Tốt >= 80). Specs:
`Tools/blender/specs/<id>.json` (`validate_specs.py --glb`: every node named, every mount and muzzle, the size within
10 % of the old file). Before / after sheets (Blender Workbench, the battle angle at 28.4 px/m x2):
`Docs/models/rebuild/<id>/before_after.png`.

## The 20 models

Towers are under the owner's 1.5 x cap (6,000 triangles). "Rounds" = build-and-gate rounds (section 7, at most 4).

| model | builder | what it is now | triangles before -> after | soft before -> after | hard gates | rounds |
|---|---|---|---|---|---|---|
| `atgm_tower` | mb_p35_wave2_atgm | Hegemon battered blockhouse, Kornet-EM twin launcher with shield and guidance box | 5,374 -> 5,408 | 58.7 -> 82.9 | pass | 3 |
| `atgm_tower_a` | same | the launcher raised 1.8 m on a guyed column, Javelin-class boxes at 15 degrees | 5,926 -> 5,744 | 56.3 -> 90.3 | pass | 3 |
| `atgm_tower_b` | same | four containers in stacked pairs, search radar turning on a post | 5,974 -> 5,788 | 59.7 -> 83.4 | pass | 3 |
| `gun_turret` | mb_p35_wave2_guns | battered casemate, Leopard-2A4-class turret, Rh-120 L/44, stowage basket | 6,430 -> 5,089 | 58.6 -> 83.0 | pass (was over the cap) | 1 |
| `gun_turret_b` | same | unmanned twin-57 mm module, feed housing, sight ball, radar mast | 7,006 -> 4,241 | 57.9 -> 85.2 | pass (was over the cap) | 1 |
| `heavy_turret` | mb_p35_wave2_heavy | octagonal barbette, AK-130-class gun house, twin 155 mm, rangefinder, roof rail, MG on riser and post | 9,514 -> 5,630 | 52.5 -> 78.0 | pass (was over the cap) | 4, NEEDS_HUMAN |
| `heavy_turret_b` | same | the same gun house plus two round corner bastions with steel cloches (HMG) | 11,958 -> 5,910 | 54.8 -> 71.6 | pass (was 2 x the cap; Muzzle_main 1/2) | 4, NEEDS_HUMAN |
| `drone_hangar` | mb_p35_wave2_hangar | earth-covered arch shelter, headwall, roller door, FPV trestle rail | 7,794 -> 4,912 | 56.2 -> 71.5 | pass (was over the cap) | 4, NEEDS_HUMAN |
| `drone_hangar_a` | same | Lancet pneumatic catapult on the berm | 6,634 -> 5,072 | 54.2 -> 71.8 | pass (was over the cap) | 4, NEEDS_HUMAN |
| `drone_hangar_b` | same | eight swarm launch cells with open lids, FPV drones | 9,770 -> 5,884 | 48.2 -> 71.5 | pass (was over the cap) | 4, NEEDS_HUMAN |
| `shield_tower` | mb_p35_wave2_shield | hex plinth, capacitor cabins, braced pylon, TeamGlow rings, platform, emitter head | 5,404 -> 4,786 | 42.9 -> 85.6 | pass (was missing walls, roof, antenna) | 2 |
| `shield_tower_a` | same | dome projector dish and three emitter arms | 7,260 -> 5,518 | 55.3 -> 81.9 | pass (was over the cap) | 2 |
| `mg_bunker_b` | mb_p35_wave2_branches | round pillbox in a mound, turning cupola with flame projector, fuel pit | 4,060 -> 3,602 | 57.6 -> 81.2 | pass (was missing base) | 3 |
| `aa_turret_b` | same | sandbag pit, Starstreak-LML-class launcher (two tube pairs), IFF antenna | 2,610 -> 2,844 | 53.0 -> 82.2 | pass | 4 |
| `artillery_emplacement_b` | same | U-shaped earth emplacement, 240 mm mortar on its carriage, loading jib | 5,878 -> 5,374 | 50.3 -> 64.1 | pass (was missing antenna, bake) | 4, NEEDS_HUMAN |
| `cp_relay_b` | same | salvage relay post: HESCO compound, container store, guyed mast, two dishes | 1,512 -> 2,852 | 48.7 -> 81.3 | pass (was missing walls, antenna) | 1 |
| `logistics_station` | mb_p35_wave2_support | supply depot: two containers, fuel bund with tanks and pump, forklift, net | 1,576 -> 5,742 | 25.9 -> 63.7 | pass (was missing walls, roof, antenna) | 4, NEEDS_HUMAN |
| `helipad` | same | flat precast pad, ring, H, stripes, flush lights (kept 0.11 m high) | 1,032 -> 2,224 | 14.0 -> 52.5 | pass (was a single block) | 3, NEEDS_HUMAN |
| `helipad_a` | same | the pad with a fabric clamshell shelter | 1,252 -> 3,614 | 15.8 -> 54.1 | pass (was a single block) | 3, NEEDS_HUMAN |
| `helipad_b` | same | the pad with a FARP: fuel bladders, pump, rocket rack, windsock | 1,988 -> 4,140 | 19.2 -> 61.8 | pass | 3, NEEDS_HUMAN |

Every one passes every hard gate (shared geometry 1.6-14 %). 11 of 20 reach Tốt; 9 are NEEDS_HUMAN on the soft score.

Branches are built together with their base (owner decision 4) where the base is in this wave: atgm, gun, heavy, drone
hangar, shield, helipad. mg_bunker_b, aa_turret_b, artillery_emplacement_b and cp_relay_b keep their base's footprint;
their base is rebuilt in waves 7-10.

### NEEDS_HUMAN (all hard gates pass)

- **drone_hangar family 71.5-71.8, logistics_station 63.7, artillery_emplacement_b 64.1**: big earth berms, container
  roofs and pads; the tower gold (seven small gun towers dense in railings and ladders) holds an edge density and
  brightness-region count per pixel that a 7-10 m earthwork does not reach at the 6,000 cap. Same as wave 1's
  structures (accepted on the owner's look, review item 1).
- **heavy_turret 78.0, heavy_turret_b 71.6**: an 8 m barbette and a 5 m gun house under the cap (the old files were
  9.5k / 12k); heavy_turret was 82.1 until the kit door fix (below) removed the door posts that stuck out.
- **helipad family 52.5-61.8**: scored against the obstacle gold (walls and dragon's teeth); a passable 10 x 10 m pad
  kept flat (the base helipad at 0.11 m) has almost no silhouette; the old files scored 14-19.
  Owner question 1.

## Trims (owner review item 2)

The 25 over-cap towers of wave 1: 19 are rebuilt by waves 2-10 (the ten of this wave are under the cap above). The six
no wave rebuilds keep their builders and are trimmed after their bake by `Tools/blender/mb_p35_trims.py` (collapse
decimation of their densest parts, zero-area and duplicate faces removed; parts, node names and pivots unchanged).
Sheets: `Docs/models/trims/<id>.png` (kept out of Docs/models/rebuild/ so the gate keeps their pass 8 visual grade).

| model | triangles before -> after | soft before -> after | hard gates |
|---|---|---|---|
| `ew_tower_a` | 6,268 -> 5,664 | 98.9 -> 98.9 | pass |
| `guard_tower` | 6,772 -> 5,796 | 98.3 -> 97.2 | pass |
| `guard_tower_a` | 7,488 -> 5,942 | 100 -> 100 | pass |
| `missile_battery` | 7,242 -> 5,842 | 80.6 -> 83.2 | pass |
| `missile_battery_a` | 8,654 -> 5,952 | 80.0 -> 85.6 | pass |
| `missile_battery_b` | 7,290 -> 5,832 | 82.7 -> 87.4 | pass |

## Kit (lane B's requests, kit35) and other items

- `tread_wheel` (lean tyre, about 250 triangles, from lane B's `mb_p35b_parts.tread_wheel`); `side_skirt(bolts=False)`;
  `era_bricks(bolts=False)`; `pintle_mg(riser=, ring_r=, cradle=)` builds the riser collar, post and cradle in one call.
  Defaults keep today's geometry: rocket_turret family and fortress_bastion rebuilt byte-identical. Tests added to
  Tools/blender/tests/test_kit35.py (not run).
- **kit35 door fix**: `K.door` built its two frame posts lying along the wall's normal (2 m out of the wall). Fixed; the
  models using it rebuilt: ixion, fortress_hive, repair_bay, radar_site, ammo_dump (triangles unchanged, soft -0.1 to
  -0.9) and the atgm family.
- **build_assets.py**: the wave 1 merge had left a stray `}` in all_builders (a syntax error); fixed in the first commit.
- **Boss!P11** "(model tạm)" removed (only sheet10.xml changed); unit_sheet.json regenerated by Tools/docs/unit_sheet.py
  (unchanged: it reads the shape column); the same note removed from Tools/docs/unit_refs.json (it copies P11).
- glb_check baseline accepts the wave's files (reason "P35 wave 2 (lane A)"); logistics_station merged small parts of
  one material to stay under the structure renderer cap (46 / 48).

## The whole gate after the wave

`python Tools/assets/quality_gate.py` (Docs/models/quality_report.xlsx / .csv): 230 models, **51 pass every gate (35
before)**. Outside this wave only the door-fix models moved (soft -0.1 to -0.9, hard gates unchanged) and
nlos_atgm_vehicle's shared share (32 % -> 31 %, still failing as before). No other model changed.

Pre-existing spec mismatches (wave 1 files, not changed here): `validate_specs --glb` still flags ammo_dump (H 3.5 vs
2.9), radar_site (merged node names, H 9.67 vs 7.9), repair_bay (merged node names), rocket_turret_a (H 3.91 vs 3.4)
and stymphalos (node names); their specs need updating by whoever owns wave 1's specs.

## For the lead to render in Unity (cards and ModelScan)

Cards (CardRenders) for the defs drawing these models: atgm_tower (+ .top, .multi), gun_turret (+ .auto), heavy_turret
(+ .bastion), drone_hangar (+ .lancet, .swarm), shield_tower (+ .bulwark), mg_bunker.flame, aa_turret.sam,
artillery_emplacement.mortar, logistics_station, airfield (+ .hangar, .service); the trimmed ew_tower.drone,
guard_tower (+ .watch), missile_battery (+ .pac3, .lrr) if their cards are re-shot. **No card**: cp_relay_b (an
orphan branch file: cp_relay has noBranch) and helipad as a prop (only the airfield cards show it). ModelScan:

```
MachineBrigade.Editor.ModelScan.RenderBatch -mbScan "atgm_tower,atgm_tower_a,atgm_tower_b,gun_turret,gun_turret_b,heavy_turret,heavy_turret_b,drone_hangar,drone_hangar_a,drone_hangar_b,shield_tower,shield_tower_a,mg_bunker_b,aa_turret_b,artillery_emplacement_b,cp_relay_b,logistics_station,helipad,helipad_a,helipad_b,ew_tower_a,guard_tower,guard_tower_a,missile_battery,missile_battery_a,missile_battery_b"
```

Points to look at in Unity: atgm_tower_b's and gun_turret_b's `Radar` spinners; heavy_turret_b's per-barrel
`Muzzle_b1/b2_main` (written by the builder) and the cloches' `Mount_gun[.001]`; the drone hangars' root muzzles; the
helipads lying flat under passing units.

## Owner questions

1. Structures and pads on the soft score: the hangars, logistics_station, artillery_emplacement_b and the helipads
   end at 52-78 after four rounds (all hard gates pass). Accept them on the look like wave 1's structures, or give
   structures / pads a gold set of their own?
2. The base helipad is kept flat (0.11 m, the 10 % size rule). A windsock or edge-light posts would read better
   but raise it to 0.3-2 m; allow it (the pad stays passable)?
3. gun_turret_b keeps two 57 mm barrels (unit_refs and the old model) although the AU-220M is single-barrelled and
   the data fires one barrel: keep, or go single-barrelled?
