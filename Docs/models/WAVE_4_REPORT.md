# Prompt 35 wave 4 report (lane C)

Wave 4 of prompt 35 (sections 7 and 8; plan Docs/models/WAVES_P35.md): twenty models rebuilt from scratch on branch
`feature/p35-w4`, each in its own new Blender script (`Tools/blender/mb_p35_<id>.py`) on the kit35 library and the
lane's helper module `Tools/blender/mb_p35c_parts.py`, with a build spec first (`Tools/blender/specs/<id>.json`).
Decisions: Docs/DECISIONS.md "Prompt 35 wave 4 (lane C)". Blender and Python only: no Unity run, no test, sim or
measure.

## Models

Soft score 0-100 against the gold of the class (Tốt >= 80). "Before" = the committed GLB at the start of the wave,
scored on the same gate. Every row passes every hard gate (`quality_gate.py`: parts, mounts and muzzles, size, own
geometry, zero-area, COLOR_0, colour zones, AO / dust / wear, not a single block), the spec check
(`validate_specs.py --glb`) and glb_check (accepted with `--reason "P35 wave 4"`). Before, all twenty failed a hard
gate (missing mantlet / idler / skirts / roof MG / smoke / stowage, the triangle floor, a missing mount, the size).

| model | real reference | triangles before -> after | soft before -> after | shared | rounds |
|---|---|---|---|---|---|
| `amphib_light_vehicle` | AAV-7A1-pattern amphibian, 25 mm one-man turret | 4,606 -> 9,256 | 78.2 -> 85.8 | 12 % | 2 |
| `aa_gun_vehicle` | CV9040 AAV (Bofors 40 mm L/70, search radar) | 3,556 -> 8,256 | 69.2 -> 91.4 | 8 % | 2 |
| `aa_vehicle` | Flakpanzer Gepard (+ twin Stinger box on `Mount_missile`) | 4,964 -> 9,586 | 78.0 -> 98.8 | 13 % | 3 |
| `shorad_vehicle` | Avenger on the HMMWV | 2,000 -> 5,620 | 79.7 -> 93.2 | 4 % | 2 |
| `sam_launcher` | 9A310 Buk TELAR | 4,418 -> 8,446 | 83.0 -> 95.0 | 11 % | 2 |
| `flame_tank` | TO-55 on the T-55, M67-style projector | 5,258 -> 10,726 | 83.3 -> 100 | 3 % | 4 |
| `artillery` | M109A7 Paladin PIM | 5,326 -> 9,958 | 89.1 -> 100 | 13 % | 2 |
| `tank_destroyer` | 2S25 Sprut-SD | 4,702 -> 10,558 | 89.1 -> 100 | 10 % | 3 |
| `demolition_line_vehicle` | M1150 Assault Breacher Vehicle (MICLIC) | 6,202 -> 8,546 | 90.5 -> 100 | 20 % | 1 |
| `scout_heli` | AH-6 / MH-6 Little Bird (five blades, after the sheet) | 2,602 -> 3,898 | 100 -> 95.0 | 2 % | 2 |
| `mine_layer` | GMZ-3 | 3,872 -> 9,902 | 71.7 -> 100 | 12 % | 1 |
| `recon_drone` | Bayraktar TB2 | 890 -> 2,936 | 93.9 -> 95.0 | 2 % | 3 |
| `fpv_carrier` | RG-33L 6x6 MRAP with an FPV launcher | 2,484 -> 7,310 | 59.9 -> 83.6 | 9 % | 3 |
| `armored_bulldozer` | IDF Caterpillar D9R | 3,244 -> 9,246 | 79.0 -> 97.2 | 11 % | 2 |
| `river_patrol_boat` | PBR Mk II / SURC-pattern patrol boat | 1,624 -> 4,374 | 83.6 -> 100 | 9 % | 3 |
| `bmpt` | BMPT Terminator (T-72) | 5,056 -> 8,706 | 86.3 -> 95.0 | 10 % | 2 |
| `towed_at_gun` | 2A45M Sprut-B | 1,996 -> 4,166 | 98.6 -> 100 | 12 % | 3 |
| `attack_jet` | Su-25 Frogfoot (and attack_jet_hd) | 2,732 -> 4,914 | 99.8 -> 100 | 1 % | 2 |
| `strike_drone` | MQ-9 Reaper | 1,968 -> 3,672 | 94.7 -> 100 | 1 % | 2 |
| `moloch` (boss, chapter 6) | tracked mobile factory (Fatboy / C&C war factory look) | 10,244 -> 27,426 | 54.5 -> 85.7 | 0 % | 4 |

"Shared" = the share of triangles also found in another model family (gate limit 30 %); the shared part is the
lane's small repeated pieces (road wheels, hatches). `scout_heli` scores 95 against 100 for the old file: the old
one failed three hard gates (floor, stub wings, main mount) and is replaced (old vs new, DECISIONS).

Budgets: over the class maximum is information only (owner 02/10). The units seen in numbers stay under 1.5 x their
class maximum: the light / wheeled ones 4,166-7,310 (cap 7,500). Tracked vehicles 8.3-10.7k (heavy class 4-7k, not a
gated cap); `moloch` 27.4k (boss 10-20k; the wave 1 bosses are 17-36k). Renderers under glb_check's caps (attack_jet
40 of 44, moloch 115).

## Pictures

Before / after sheets (Blender Workbench, material colours: front, rear, side, top, 3/4 front, 3/4 rear, and the battle
angle at 28.4 px per metre, x2): `Docs/models/rebuild/<id>/before_after.png` for the twenty ids.

**For the lead to render in Unity** (cards and ModelScan sheets): all twenty ids have a card image already
(CardRenders, `moloch` a boss card); none is without one. ModelScan:

```
MachineBrigade.Editor.ModelScan.RenderBatch -mbScan "amphib_light_vehicle,aa_gun_vehicle,aa_vehicle,shorad_vehicle,sam_launcher,flame_tank,artillery,tank_destroyer,demolition_line_vehicle,scout_heli,mine_layer,recon_drone,fpv_carrier,armored_bulldozer,river_patrol_boat,bmpt,towed_at_gun,attack_jet,strike_drone,moloch"
```

Points to look at in Unity: aa_vehicle's and aa_gun_vehicle's `Radar` spinners (only the array turns); the bulldozer's
`Blade` stroke (it pivots at the push-arm trunnions); the drones' `Propeller` (pusher, axis along the fuselage);
moloch's per-barrel muzzles (`Muzzle_b1/b2_*`, now from mb_fix_barrels' EXTRA list), its doors and track parts; the
flare points on scout_heli and attack_jet (wrapper, at the `Flares` dispensers); attack_jet's `Part_wing` cut.

## Roof guns

Every roof gun stands clear of the roof line (MODEL_STANDARD "Roof guns"): main-weapon roof guns on
`mb_p35c_parts.roof_gun` (post, yaw pivot, cradle, receiver with grips, ribbed barrel, flash hider, ammunition can on
its bracket, shield: mine_layer, river_patrol_boat's bow gun, armored_bulldozer); free secondaries on
`mb_kit35.pintle_mg(post=...)` (tank_destroyer, artillery, sam_launcher, fpv_carrier, the boat's 40 mm); the flame
tank's DShK on its ring and cradle post; the ABV's remote station on a turned base.

## The whole gate after the wave

`python Tools/assets/quality_gate.py --no-write` over all 230 scored models (after merging wave 2): 71 pass the whole
gate; the twenty wave 4 models all pass; no other model's own-geometry check names a wave 4 model.

## NEEDS_HUMAN

None (every model passed within four rounds).

## Kit / gate requests (lane A)

1. `mb_kit35.missile`: its docstring says the nose points along `direction`, but the nose (and seeker) is built
   towards `-direction` (`rot_to(-direction)` with the nose at the profile's far end). Wave 1's bosses pass
   `direction=(0, -1, 0)`, so their missiles may point backwards. Lane C used `direction=(0, 1, 0)` or its own lean
   store.
2. Gate: the jet roles ask `flares` and `canopy` of drones (recon_drone, strike_drone have neither); the tracked roles
   ask `roof_mg` / `smoke` of vehicles that have none (Gepard, Buk, GMZ-3) and `turret` / `mantlet` of a hull-aimed
   bulldozer whose def has a turretTurnRate. Lane C used honest names where the real vehicle has the part (the coax
   PKT as `MG_coax`, the TDA smoke vent, the gun cradle) and spec `"merged"` with a note otherwise; asked: apply those
   roles only when the def has the system (flareCharges, an MG secondary, mainAim Turret).
3. A lean missile / bomb in the kit (lane C's `store`: two parts, under the jet renderer cap) and the `section_loft`
   / `slab_loft` / `ellipse_half` body helpers.

## Owner questions

1. No unit_refs / unit_sheet row for six ids, built after the old builders: amphib_light_vehicle (AAV-7A1 pattern; note
   reference_real.json says M2A3 Bradley), aa_gun_vehicle (CV9040 AAV), shorad_vehicle (Avenger),
   demolition_line_vehicle (M1150 ABV), river_patrol_boat (PBR / SURC pattern), towed_at_gun (2A45M). Confirm or
   name the references.
2. fpv_carrier is an RG-33L (unit_refs' second vehicle) because the lancet truck already is the Typhoon-K. Fine?
