# Prompt 35 wave 7 report (lane C)

Wave 7 of prompt 35 (sections 7 and 8; plan Docs/models/WAVES_P35.md): nineteen models rebuilt from scratch on branch
`feature/p35-w7`, each in its own Blender script (`Tools/blender/mb_p35_<id>.py`; minefield / minefield_b and
mg_bunker / mg_bunker_a share a module) on the kit35 library and the lane's helper module `mb_p35c_parts.py`, with a
build spec first (`Tools/blender/specs/<id>.json`). main_battle_tank, a gold model, was only checked. Decisions:
Docs/DECISIONS.md "Prompt 35 wave 7 (lane C)". Blender and Python only: no Unity run, no test, sim or measure.

## Models

Soft score 0-100 against the gold of the class (Tốt >= 80). "Before" = the committed GLB at the start of the wave,
scored on the same gate. Every row passes every hard gate (`quality_gate.py`: parts, mounts and muzzles, size, own
geometry, zero-area, COLOR_0, colour zones, AO / dust / wear, not a single block), the spec check
(`validate_specs.py --glb`) and glb_check (accepted with `--reason "P35 wave 7"`). Before, 19 of the 20 failed a hard
gate.

| model | real reference | triangles before -> after | soft before -> after | rounds |
|---|---|---|---|---|
| `elite_aa` | Skyranger 35-style turret on the Leopard 1 hull (unit_refs), the def's twin 35 mm | 5,456 -> 11,904 | 78.9 -> 93.5 | 3 |
| `elite_heavy_tank` | Object 195 / T-95: 152 mm, 30 mm cheek gun, remote 12.7 mm | 5,754 -> 13,350 | 79.8 -> 97.7 | 3 |
| `elite_tank_destroyer` | 2S25M Sprut-SDM1 (unit_refs' 2S25, upgraded) | 4,794 -> 11,184 | 86.0 -> 97.7 | 1 |
| `elite_apc` | BMP-3 with the Epokha module (30 mm, coax, four Kornets) | 5,480 -> 11,260 | 84.7 -> 98.9 | 2 |
| `radar_atgm_vehicle` | 9P157-2 Khrizantema-S on the BMP-3 chassis | 2,672 -> 10,290 | 83.8 -> 95.0 | 2 |
| `nlos_atgm_vehicle` | Spike NLOS launcher on a Tatra-pattern armoured 6x6 | 4,918 -> 7,440 | 79.0 -> 100 | 3 |
| `ground_drone_carrier` | Milrem Type-X pattern with three docked UGVs | 4,274 -> 8,736 | 94.8 -> 95.0 | 1 |
| `armored_car` | Pandur I 6x6, M242 25 mm (unit_refs, sheet) | 2,622 -> 6,804 | 81.3 -> 85.0 | 3 |
| `scout_jeep` | M151A2 with a WMIK-style pedestal M2 (and scout_jeep_hd) | 2,422 -> 6,064 | 91.9 -> 100 | 4 |
| `rocket_technical` | 6th-generation Hilux single cab, Type 63 107 mm | 2,948 -> 6,554 | 85.7 -> 100 | 3 |
| `uav_loiter_strike` | MQ-1C Gray Eagle, four Hellfires | 1,084 -> 3,504 | 89.8 -> 98.9 | 2 |
| `aerial_tanker` | Il-78M Midas, three UPAZ pods | 4,164 -> 5,454 | 85.4 -> 90.2 | 2 |
| `command_hq` | the Siege command bunker (old mb_siege brief) | 5,982 -> 8,872 | 90.0 -> 89.3 | 3 |
| `minefield` | TM-62M field with marked perimeter | 3,198 -> 4,746 | 91.7 -> 94.7 | 2 |
| `minefield_b` | PTM-3 scatter mines and the six-tube dispenser | 4,560 -> 4,194 | 94.2 -> 93.7 | 2 |
| `gun_turret_a` | Leopard 2A6-class turret, Rh-120 L/55, on gun_turret's casemate | 6,702 -> 5,327 | 68.2 -> 83.5 | 1 |
| `mg_bunker` | cast pillbox with an NSV cupola (mg_bunker_b's style) | 3,904 -> 3,748 | 68.3 -> 80.5 | 3 |
| `mg_bunker_a` | the same pillbox with a cupola collar and twin NSV | 4,204 -> 4,996 | 70.6 -> 86.7 | 3 |
| `guard_tower_b` | the guard tower's blockhouse with a 25 mm gun nest | 2,746 -> 5,880 | 68.4 -> 71.2 | 4 (NEEDS_HUMAN) |
| `main_battle_tank` | gold model (prompt 27), not rebuilt | 7,196 (unchanged) | 93.5 | 0 |

Hard fails before: parts (mantlet, idler, sight, roof MG, smoke, stowage, glass, axles, tail, exhaust, pylons, stores,
base, walls, antenna), the triangle floor (radar_atgm_vehicle, uav_loiter_strike), the size (radar_atgm_vehicle), own
geometry (elite_heavy_tank 93 % with heavy_tank, nlos_atgm_vehicle 31 % with interceptor_drone_vehicle), the tower cap
(gun_turret_a), worn edges (both minefields), sloped faces (command_hq, rocket_technical, elite_apc).

Budgets: units seen in numbers stay under 1.5 x their class maximum (wheeled 6,064-7,440 under 7,500; towers
3,748-5,880 under 6,000). Tracked 8.7-13.4k and command_hq 8.9k are over their class maxima as information only.
Renderers under glb_check's caps (aerial_tanker 42 of 44, command_hq 52 of 58, ground units 46-70 of 76).

Towers: gun_turret_a stands on lane A's gun_turret casemate; mg_bunker and mg_bunker_a use mg_bunker_b's mound, drum,
race and cupola, so the three read as one pillbox family; guard_tower_b keeps the guard tower's blockhouse and turns its
roof into the nest. Roof guns stand on posts (MODEL_STANDARD "Roof guns"): elite_heavy_tank's and
elite_tank_destroyer's remote 12.7 mm, ground_drone_carrier's RWS and scout_jeep's pedestal M2 on `roof_gun`, the free
MGs (nlos_atgm_vehicle, rocket_technical) on `pintle_mg(post=...)`.

## Pictures

Before / after sheets (Blender Workbench, material colours: front, rear, side, top, 3/4 front, 3/4 rear, and the battle
angle at 28.4 px per metre, x2): `Docs/models/rebuild/<id>/before_after.png` for the nineteen rebuilt ids.

**For the lead to render in Unity** (cards and ModelScan sheets): the nineteen rebuilt ids. Every one has a card image
(Resources/UI/Cards) except **command_hq** (a Siege prop, no card). main_battle_tank did not change.

```
MachineBrigade.Editor.ModelScan.RenderBatch -mbScan "elite_aa,elite_heavy_tank,elite_tank_destroyer,elite_apc,radar_atgm_vehicle,nlos_atgm_vehicle,ground_drone_carrier,armored_car,scout_jeep,rocket_technical,uav_loiter_strike,aerial_tanker,command_hq,minefield,minefield_b,gun_turret_a,mg_bunker,mg_bunker_a,guard_tower_b"
```

Points to look at in Unity: elite_aa's and command_hq's `Radar` spinners; radar_atgm_vehicle's `Radar` head on its arm;
uav_loiter_strike's pusher `Propeller` and the two `Muzzle_missile` rails; aerial_tanker's flare points (wrapper) and
`Part_wing` cut; ground_drone_carrier's `Minion_1..3` on the deck; guard_tower_b's new height (4.6 m).

## The whole gate after the wave

`python Tools/assets/quality_gate.py --no-write` over all 230 scored models: 97 pass the whole gate; the twenty wave 7
ids all pass; no other model's own-geometry check names a wave 7 model (twin_tank names main_battle_tank, which did not
change; lane A's wave 5 rebuilds twin_tank).

## NEEDS_HUMAN

- `guard_tower_b`: soft 71.2 after four rounds (68.4 before; every hard gate passes). The tower gold is dense and the
  10 % size rule keeps the nest's kit inside the old 4.3 x 3.5 m footprint (a round with yard clutter outside it scored
  74.4 but broke the size). Its height also grows from 1.8 m to 4.6 m (below).

## Kit / gate requests (lane A)

1. `mb_kit35.missile` fix: wave 4's recon_drone and strike_drone pass `direction=(0, 1, 0)` to get the nose forward;
   flip them to `(0, -1, 0)` when the fix lands. Wave 7 uses lane C's `store`, so nothing here flips.
2. Gate: still the wave 4 request, roles applied only when the def has the system (elite_aa and radar_atgm_vehicle have
   no MG, uav_loiter_strike no flares: spec `"merged"` for now).
3. Gate: the asymmetry metric reads a structure on a square or octagonal slab as symmetric (command_hq, guard_tower_b:
   asym_raw 0.0 -> half marks); measure it without the base slab.
4. `mb_kit35.ladder`: a vertical ladder always spreads along X; a `facing` argument would put it flat on a side wall
   (guard_tower_b leans it 6 cm to turn it).

## Owner questions

1. The six wave 4 references kept for now (lead call): amphib_light_vehicle as an AAV-7A1 pattern, aa_gun_vehicle as
   the CV9040 AAV, shorad_vehicle as the Avenger, demolition_line_vehicle as the M1150 ABV, river_patrol_boat as a
   PBR / SURC, towed_at_gun as the 2A45M. Confirm or name others.
2. guard_tower_b: the guard tower's blockhouse with a gun nest on its roof (4.6 m) instead of the old 1.8 m sandbag
   ring, so it reads as an upgrade of the base. Keep, or go back to a low nest?
3. elite_tank_destroyer is drawn with unit_refs' long 125 mm (2S25M) while the def fires gun_105_apfsds; elite_aa draws
   the def's twin 35 mm although the real Skyranger 35 has one gun. Fine?
