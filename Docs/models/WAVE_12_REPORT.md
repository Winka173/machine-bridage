# Prompt 35 wave 12 report (lane C)

Wave 12 (owner, DECISIONS "Prompt 35: owner answers on REBUILD_REPORT section 8", item 5): the eight P3 models left
as they were after wave 11 rebuilt from scratch, and the three helipads lifted with real heliport furniture. Branch
`feature/p35-w12` from `lead/integration` (eec98c34). Each model has its own Blender script
(`Tools/blender/mb_p35_<id>.py`; the helipads share `mb_p35_helipads.py`) and a build spec first
(`Tools/blender/specs/<id>.json`). Decisions: Docs/DECISIONS.md "Prompt 35 wave 12 (lane C)". Blender and Python only:
no Unity run, no test, sim or measure.

## Models

Soft score 0-100 against the gold of the class (bosses against their frame's set: boss_air, boss_rail). "Before" =
the committed GLB at the start of the wave, on the same gate. Every row passes every hard gate (`quality_gate.py`),
the spec check (`validate_specs.py --glb`) and glb_check (0 errors; accepted with `--reason "P35 wave 12"`). Each
took 3-6 build / look rounds (sheets read at full size, the train in 2,400 px crops).

| model | real reference | triangles before -> after | soft before -> after |
|---|---|---|---|
| `minefield_a` | M21 heavy AT mines with M607 tilt rods, a TM-83 off-route mine with its seismic sensor, a taped crossing lane, an opened mine crate; on the wave 7 minefield's patch and perimeter, the glowing Team rims kept | 3,780 -> 6,730 | 92.4 -> 94.2 |
| `dragons_teeth_b` | FM 5-34 triple-standard concertina fence (two base coils, top coil, U pickets, barbed strands, anchor pickets, tin-can rattles, wire spool) on lane A's wave 8 footing and marker stakes; repeats every 5 m | 4,232 -> 8,378 | 83.2 -> 100 |
| `drone_mothership` | USS Akron / Macon (hangar, trapeze) with an X tail and vectoring ducted fans: chin twin 30 mm, gondola with bomb bay and cannon ball, gun pods, drone hangar with six FPV drones, rotary drop launcher, UAV on the trapeze, two quad flak turrets, the shield belt | 20,206 -> 18,880 | 94.1 -> 98.6 |
| `ew_tower` | Pole-21 / R-934-style sector jammer head on a galvanised four-legged lattice mast; equipment shelter, skid generator, drums, reel (the old family layout, so the trimmed ew_tower_a still matches) | 5,936 -> 5,998 | 95.0 -> 95.0 |
| `ew_tower_b` | the same site with a DRFM radar-spoofer planar array on a trunnion yoke (framed radome tiles, sun shade, side horns, back box with fans, elevation jack) | 5,376 -> 5,740 | 94.4 -> 95.0 |
| `nuke_train` | BZhRK Molodets launcher car (roof doors open, catenary diverter, erector, the icbm projectile's scheme), BP-43-style armoured locomotive with the twin turret, rocket / SAM (Roland pattern) / 152 mm / twin 35 mm flatcars; car layout and lengths kept | 36,310 -> 28,910 | 100 -> 100 |
| `recoilless_jeep` | M38A1C with the M40A1 106 mm on the M79 pedestal (perforated chamber, venturi breech, M8C spotting rifle, M92F sight); round-nosed body so it is not the scout jeep's M151 | 3,386 -> 7,328 | 94.8 -> 95.0 |
| `airborne_light_tank_chute` | lane B's wave 6 airborne_light_tank (its builder, unchanged) on a Type V platform with honeycomb and chain tie-downs, four slings to the M-2 release, four G-11 canopies | 3,514 -> 16,310 | 100 -> 100 |
| `helipad` | lane A's pad (paint now over the stains: the H clear), elevated green FATO lights, tie-down cups, ICAO windsock, two floodlight posts, a hose-reel fuel cabinet and an extinguisher trolley | 2,224 -> 4,370 | 52.5 -> 72.5 |
| `helipad_a` | the same with lane A's clamshell shelter and a towed fuel bowser (windsock on the free left edge) | 3,614 -> 6,422 | 54.1 -> 74.5 |
| `helipad_b` | the same with lane A's FARP (its old windsock replaced by the common one) | 4,140 -> 5,582 | 61.8 -> 70.2 |

Budgets: the towers 5,998 / 5,740 and the jeep 7,328 under their "seen in numbers" caps (6,000 / 7,500). Over the
guide on non-capped classes (owner rule: kept): dragons_teeth_b 8,378 and minefield_a 6,730 (obstacle 6,000: the
coils and the mines), airborne_light_tank_chute 16,310 (air_other 7,000: the ground tank's 10,510 plus the rig; its
static parts merged by material to 38 renderers under the air cap of 44), nuke_train 28,910 (boss 10-20k; 7,400 under
the old file). GLBs of the eleven: 5.9 -> 7.9 MiB.

Footprints: the helipads' bounds are the old files' to the centimetre (10 x 10 m, lane A's shelter and FARP overhangs
unchanged); only the height grows with the windsock and posts (3.39 / 3.54 m; the specs' targets updated).

Runtime nodes: every old pivot kept at its place (checked against the old files node by node; the train's loads at
13.40 / 18.22 / 23.00 / 27.80 exactly). Added: drone_mothership `Mount_Flare_L2` / `_R2` (the flare wrapper reads
the dispensers as two rows), nuke_train `Point_exhaust` / `Point_fire`. airborne_light_tank_chute now carries the
wave 6 tank's own nodes (`Mantlet`, `Mount_mg`, `Muzzle_mg`; `Muzzle_main` at the new gun's tip, -3.25 m) instead of
the old tank's.

## Pictures

Before / after sheets (Blender Workbench, material colours; seven angles): `Docs/models/rebuild/<id>/before_after.png`
for the eleven ids.

**For the lead to render in Unity** (cards and ModelScan sheets): the eleven ids below. **No card** in
Resources/UI/Cards/manifest.json for `minefield_a` (an orphan branch file) and `airborne_light_tank_chute` (the
paradrop proxy, card: false).

```
MachineBrigade.Editor.ModelScan.RenderBatch -mbScan "minefield_a,dragons_teeth_b,drone_mothership,ew_tower,ew_tower_b,nuke_train,recoilless_jeep,airborne_light_tank_chute,helipad,helipad_a,helipad_b"
```

Points to look at in Unity: the train's 152 mm barrel over the SAM car (the pivots put it through the SAM turret's
sweep, as in the old file), the erector raising the ICBM clear of the open roof doors; the mothership's aft flak
barrels over the shield belt (the belt is kept low for them), the fans spinning; the chute tank falling (canopies
8.3-10.2 m up); the windsock streaming into each pad.

## The whole gate after the wave

`python Tools/assets/quality_gate.py --no-write` over all 230 scored models: 199 pass the whole gate, hard gates 230
of 230 (no model fails a hard gate, so no own-geometry check names a wave 12 model). The eleven wave 12 ids all pass
every hard gate; the three helipads stay under 80 (below).

## NEEDS_HUMAN

None new. The helipads (wave 2 NEEDS_HUMAN, accepted on the look) rise from 52.5 / 54.1 / 61.8 to 72.5 / 74.5 / 70.2
and stay under 80: a flat 10 x 10 m pad has little silhouette against the obstacle gold however many thin props
stand on it.

## Owner questions

1. **nuke_train's `locomotive` hit point**: `at` (0, -8.5, 2.5) lies at Blender y +8.5, on the launcher car's rear
   (the def's frame is (-x, -y, z)); the locomotive is at y -10.6 .. -1.6. Move it to (0, 6.1, 2.5)? (data only; not
   changed here.)
