# Prompt 35 wave 9 report (lane C)

Wave 9 of prompt 35 (plan Docs/models/WAVES_P35.md): twenty models rebuilt from scratch on branch `feature/p35-w9`
(from `feature/p35-w7` with `lead/integration` merged in), each in its own Blender script
(`Tools/blender/mb_p35_<id>.py`; aa_turret / aa_turret_a and c_ram / c_ram_a / c_ram_b share a module so base and
branches are built together) on the kit35 library and lane C's helper module `mb_p35c_parts.py` (new this wave:
`casings`, `duckboard`, `entrenching_tools`, `helmets`, `pickets`, `plain_wheel`), with a build spec first
(`Tools/blender/specs/<id>.json`). Plus the lead's wave 7 calls: elite_tank_destroyer now draws a 105 mm, and the
drones were checked. Decisions: Docs/DECISIONS.md "Prompt 35 wave 9 (lane C)". Blender and Python only: no Unity
run, no test, sim or measure.

## Models

Soft score 0-100 against the gold of the class (bosses against the boss_ground set). "Before" = the committed GLB
at the start of the wave, on the same gate. Every row passes every hard gate (`quality_gate.py`), the spec check
(`validate_specs.py --glb`) and glb_check (0 errors; accepted with `--reason "P35 wave 9"`). Before, 19 of the 20
failed a hard gate.

| model | real reference | triangles before -> after | soft before -> after |
|---|---|---|---|
| `aa_turret` | 2A38 twin 30 mm gun house + twin Stinger tubes, field post (berm, sandbags, rear bay, net) | 6,306 -> 5,202 | 67.7 -> 80.8 |
| `aa_turret_a` | ZSU-23-4 Shilka turret (four 23 mm, RPK-2 dish) on the base's post | 6,670 -> 5,952 | 68.8 -> 84.0 |
| `c_ram` | Centurion C-RAM (Phalanx 1B on a trailer), LCMR mast, HESCO / T-wall FOB site | 6,246 -> 5,930 | 65.9 -> 91.7 |
| `c_ram_a` | the same Centurion with the Block 1B EO box and the radome-ball mast | 6,694 -> 5,972 | 69.3 -> 91.6 |
| `c_ram_b` | Iron Dome's 20-cell Tamir launcher on the site's trailer, EL/M-2084 array | 7,590 -> 5,704 | 66.3 -> 90.1 |
| `artillery_emplacement` | M198-class split-trail 155 mm in a round earth gun pit | 7,946 -> 4,992 | 65.5 -> 91.9 |
| `iron_beam` | truck-mounted Iron Beam (Iron Beam-M pattern): beam director, radar, no gun | 2,888 -> 6,718 | 76.4 -> 97.1 |
| `ew_jammer` | Krasukha-4 on the BAZ-6910 (reflector on a turning pedestal, roof 12.7 mm) | 2,274 -> 7,428 | 68.8 -> 89.8 |
| `shahed_truck` | 6x6 truck with the five-rail Shahed-136 launch box | 2,616 -> 6,228 | 83.4 -> 99.6 |
| `interceptor_drone_vehicle` | JLTV-class 4x4, six-cell interceptor box + two-tube Coyote roof mount | 4,068 -> 4,298 | 84.7 -> 91.2 |
| `mobile_repair_vehicle` | BREM-K-class armoured repair vehicle (BTR-80 hull, crane, winch, spade) | 3,668 -> 5,920 | 67.8 -> 89.3 |
| `long_sam` | S-300PMU 5P85S on the MAZ-543 | 2,980 -> 7,456 | 78.9 -> 98.8 |
| `heavy_rocket_artillery` | 9A52-2 Smerch on the MAZ-543M | 3,668 -> 7,152 | 80.9 -> 100 |
| `ballistic_launcher` | Iskander-M 9P78-1 on the MZKT-7930, one 9M723 raised | 2,818 -> 7,414 | 74.5 -> 95.0 |
| `ground_cruise_missile_vehicle` | Typhon-class four-cell Mk 41 box on an FMTV-class 6x6 | 3,868 -> 5,606 | 67.3 -> 92.7 |
| `combat_wreck_car` | improvised up-armoured sedan, shielded 12.7 mm roof ring (footprint kept) | 2,794 -> 4,010 | 63.8 -> 89.3 |
| `stealth_fighter` | F-22 / J-20 / F-35 pattern, two-tone grey, open bays (AIM-9X, GBU-39, AIM-120) | 3,336 -> 2,976 | 73.2 -> 87.3 |
| `supreme_command` | super-heavy four-axle armoured command post (MZKT-7930 pattern), mast | 10,214 -> 14,610 | 95.4 -> 95.6 |
| `kronos` | Bagger 288 war machine (crawlers, boom, bucket wheel, pylon, five guns) | 13,194 -> 11,350 | 80.0 -> 89.0 |
| `earth_borer` | three-segment armoured boring machine, spinning drill, two 100 mm | 23,130 -> 11,364 | 83.9 -> 81.4 |
| `elite_tank_destroyer` | wave 7 model: gun changed to a long 105 mm (the def's gun_105_apfsds) | 11,184 -> 11,140 | 97.7 -> 97.2 |

Hard fails before: the tower cap (aa_turret x2, c_ram x3, artillery_emplacement), parts (axles, stowage, walls,
antenna, tail, intakes, pylons), Mount_APS (iron_beam, c_ram x3), Muzzle_missile (aa_turret_a), the size
(interceptor_drone_vehicle 25 % off), sloped faces (ew_jammer, long_sam, heavy_rocket_artillery,
ballistic_launcher, kronos), boss muzzles (kronos 3/5, earth_borer 2/3).

Budgets: towers 4,992-5,972 under the 6,000 cap; light wheeled 4,010-7,456 under 7,500; the jet 2,976 (floor
2,800); bosses 11.4-14.6k in the 10-20k band. Moving parts and renderers under glb_check's caps (the stealth
fighter's fittings merged to 38 of 44 renderers; aa_turret_a's barrel sleeves are one part, 8 of 9 moving parts).

Runtime nodes: every old node kept at its place (the bosses' part pivots checked against the old files to the
centimetre). Added: `Mount_APS` (iron_beam, c_ram, c_ram_a, c_ram_b), kronos `Mount_gun.001` / `.002` with their
muzzles, earth_borer `Muzzle_main` at the drill tip. Plain pivots kept without a drawn weapon where the old file
had them and the def has no such weapon: aa_turret_a `Muzzle_missile` (the gate reads the base def's sam),
artillery_emplacement / heavy_rocket_artillery / ballistic_launcher `Mount_mg` / `Muzzle_mg`.

Drones (lead's question 4): recon_drone and strike_drone already pass `direction=(0, -1, 0)` since lane A's kit fix
(d0a05f04); rebuilt here, both GLBs came out byte-identical to the committed ones, so their missiles point forward
and nothing changed.

## Pictures

Before / after sheets (Blender Workbench, material colours; front, rear, side, top, 3/4 front, 3/4 rear, battle
angle): `Docs/models/rebuild/<id>/before_after.png` for the twenty ids and elite_tank_destroyer.

**For the lead to render in Unity** (cards and ModelScan sheets): the twenty-one ids below. Every one has a card
in Resources/UI/Cards/manifest.json; **no id is without a card** this wave.

```
MachineBrigade.Editor.ModelScan.RenderBatch -mbScan "aa_turret,aa_turret_a,c_ram,c_ram_a,c_ram_b,artillery_emplacement,iron_beam,ew_jammer,shahed_truck,interceptor_drone_vehicle,mobile_repair_vehicle,long_sam,heavy_rocket_artillery,ballistic_launcher,ground_cruise_missile_vehicle,combat_wreck_car,stealth_fighter,supreme_command,kronos,earth_borer,elite_tank_destroyer"
```

Points to look at in Unity: the `Radar` spinners (aa pair, c_ram family, iron_beam, ew_jammer's reflector);
earth_borer's `Propeller` drill; kronos's five muzzles and the bucket wheel part; iron_beam's `Energy` aperture
glow; ballistic_launcher's raised missile (Muzzle_main at its nose); the stealth fighter's `Part_wing` cut and
flare points (wrappers).

## The whole gate after the wave

`python Tools/assets/quality_gate.py --no-write` over all 230 scored models: 133 pass the whole gate; the twenty
wave 9 ids and elite_tank_destroyer all pass; no other model's own-geometry check names a wave 9 model.

## NEEDS_HUMAN

None: every model passes every hard gate with soft >= 80 (aa_turret the lowest at 80.8, earth_borer 81.4).

## Kit / gate requests (lane A)

1. `mb_kit35.ladder`: a `facing` argument (still open from wave 7).
2. Gate: measure the asymmetry metric without the base slab (still open from wave 7).
3. `k.sweep` along a horizontal closed path turns its profile's v axis downward (berms came out underground);
   lane C passes the profile turned 180 degrees. An `up` that takes effect, or a note in the docstring.
4. Own geometry: `mb_p35c_parts.lugged_tyre` with the same arguments in two models counts as shared (a small car
   hit 34 %); combat_wreck_car moved to the kit's `tread_wheel`, which is common enough to be ignored. A rule that
   kit wheels never count (as `KIT_PIECE` does for the body share) would help small vehicles.

## Owner questions

1. The six wave 4 references (the lead sends them to the owner): amphib_light_vehicle AAV-7A1, aa_gun_vehicle
   CV9040 AAV, shorad_vehicle Avenger, demolition_line_vehicle M1150 ABV, river_patrol_boat PBR / SURC, towed_at_gun
   2A45M.
2. iron_beam: the def is a mobile unit (speed 7, modelSize 8.2 x 2.05 x 2.86 m), so it is drawn as a truck-mounted
   Iron Beam (Iron Beam-M pattern), laser only. Keep, or should it become a fixed tower?
3. kronos: part gun_r (a 30 mm) names `Mount_gun`, which the runtime gives to the def's first 57 mm; the model draws
   a 57 mm there and the second 30 mm on `Mount_gun.002`. Point gun_r's node at `Mount_gun.002` in the data?
4. ballistic_launcher is drawn with one missile raised 22 degrees (the def's 4.18 m height). Fine?
5. supreme_command keeps its old 11 m mast (the boss part antenna) and its wheels; the def's frame says tracked,
   the reference (MZKT-7930) is wheeled.
