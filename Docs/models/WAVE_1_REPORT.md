# Prompt 35 wave 1 report

Wave 1 of prompt 35 (sections 7 and 8), after the owner approved the pilot (DECISIONS "Prompt 35: owner review of
the pilot (2026-10-03)"). Two lanes: lane A (bosses, towers, the kit and the gate) below; lane B (the ten wave 1
vehicles) fills its own section. **STOP: the owner reviews this wave before wave 2.**

Gate: `Tools/assets/quality_gate.py` (hard gates + a 0-100 soft score against the gold of the class; Tốt >= 80).
Specs: `Tools/blender/specs/<id>.json` (`validate_specs.py --glb`: every node named, every mount and muzzle, the size).
Decisions: Docs/DECISIONS.md "Prompt 35 wave 1 (lane A)".

## Lane A (feature/p35-w1a)

### Models

"Before" = the committed GLB at the start of wave 1: its pass 0 score (old gold) / its score on the wave 1 gate (per-frame
boss gold, decision 5). "Shared" = the share of triangles also found in another model family (gate limit 30 %).

| model | class / gold set | triangles before -> after | soft before -> after | hard gates | shared |
|---|---|---|---|---|---|
| `fortress_bastion` | boss / boss_ground | 25,064 -> 34,218 | 77.3 / 91.8 -> 88.7 | pass | 4.6 % (was 55 % with fortress_hive) |
| `fortress_hive` | boss / boss_ground | 19,334 -> 19,476 | 70.4 / 92.2 -> 96.9 | pass | 2.5 % (was 75 % with fortress_bastion) |
| `behemoth_inferno` | boss / boss_ground | 20,046 -> 23,648 | 74.6 / 92.5 -> 90.7 | pass | 3.2 % (was 69 % with behemoth) |
| `behemoth_tempest` | boss / boss_ground | 17,418 -> 16,670 | 78.9 / 96.9 -> 91.7 | pass | 7.2 % (was 79 % with behemoth) |
| `stymphalos` | boss / boss_air | 4,186 -> 10,794 | 79.5 / 85.7 -> 94.4 | pass | 1.0 % (was 84 % with stymphalos_drone) |
| `ixion` (touch-up) | boss / boss_ground | 35,714 -> 36,022 | 79.7 / 87.5 -> 90.1 | pass | 3.7 % |
| `rocket_turret` | tower | 9,052 -> 5,638 | 79.6 -> 83.5 | pass (was over the new cap) | 11.7 % (its own branches) |
| `rocket_turret_a` | tower | 5,554 -> 5,366 | 74.4 -> 83.9 | pass | 12.3 % (family) |
| `rocket_turret_b` | tower | 3,526 -> 5,520 | 52.5 -> 86.3 | pass | 12.1 % (family) |
| `repair_bay` | tower | 5,214 -> 5,970 | 32.5 -> 66.9 | pass (was: single block) | 0.7 % |
| `radar_site` | tower | 4,252 -> 5,830 | 54.2 -> 71.2 | pass (was: single block) | 4.7 % |
| `ammo_dump` | tower | 5,276 -> 5,284 | 56.5 -> 57.8 | pass (was: no base, no roof) | 0.9 % |
| `zu23_technical` (touch-up) | wheeled / tracked gold | 7,436 -> 7,368 | 93.9 -> 95.0 | pass (was: Muzzle_main 1/2) | 1.8 % |

What each one is (section 7's identifying features, from its spec):

- **fortress_bastion**: a Sandcrawler-like riveted casemate on two long tracks under thick hinged skirts; the
  2B8-class 240 mm mortar raised on a citadel; four deck turrets (twin 100 mm forward, Bofors 40 mm aft); the 155 mm
  bow casemate gun; the twin Kornet; two ZU-23-2 on raised pedestals; a repair crane with welding bottles (it patches
  itself up once).
- **fortress_hive**: a crawler-transporter platform on four double-track trucks with levelling rams, two corner
  operator cabs, generator houses; the vaulted drone hangar with bays and parked drones; the EMP dome (glowing, in a
  hazard ring) and the jammer array, the card's two weak points; Lancet rails, the SAM box, twin flak.
- **behemoth_inferno**: an Object 279 elliptical shell over four narrow tracks (stiffener ribs, shoulder stowage);
  twin flame projectors with jackets, fuel hoses, nozzles and pilot flames; a TOS-1A box on the glacis; the red fuel
  tanks strapped on the rear deck (its fuel part).
- **behemoth_tempest**: its own slab hull with rhomboid track guards; the EMRG twin-rail barrel with glowing coils;
  two coilguns on the front deck; the interceptor laser on the turret roof (Mount_APS, which the old file lacked);
  the shield emitter turning on its mast (Radar); capacitor banks and cooling fins.
- **stymphalos**: eight Loyal-Wingman jet drones of its own design in the V (chined fuselage, dorsal intake, swept
  wings, canted tails, flat exhaust, wing missiles); the lead's flak pod and bay, the first pair's gun pods, the tail
  drone's bay.
- **rocket_turret_a / _b**: the base's emplacement with a launcher of their own: a 16-tube Uragan-class pack (cluster)
  and two GMLRS pod boxes with a guidance mast (guided); the three read apart at the default zoom.
- **repair_bay** (Accord): a corrugated shed on a steel frame (ribbed roof, skylights, ridge vents), a gantry crane on
  rails lifting an engine pack, the inspection pit, bench, tool chests, compressor, gas bottles, tyres.
- **radar_site** (Hegemon): a cast pad, a tapering lattice tower with a caged ladder and a railed platform, the big
  dish on `Radar`, the equipment container, a generator skid, jersey barriers and a fence.
- **ammo_dump** (Accord): a semi-sunken bunker in an earth berm (turf, sandbagged crest, timber revetment, steel door),
  crate stacks on pallets with a blast traverse under a camouflage net, shell cases, the red ammunition flag.
- **Roof guns** (the owner's rule): Ixion's two MGs on 0.9 m pintle posts, the rocket turret family's crew MG on a
  0.5 m post, bastion's ZU-23 on 0.95 m pedestals, zu23_technical's gun taller on its pedestal (upright magazines,
  ring sight) within the 10 % size limit.

Rounds (section 7, at most 4): bosses 1-2 (blockout and tier 2 / 3 in one pass, a fix round for sizes, plates and
the inferno's shell); the rocket turret family 3 (cap trims); repair_bay, radar_site, ammo_dump 4.

### Pictures

Before / after sheets (Blender Workbench: front, rear, side, top, 3/4 front, 3/4 rear, the battle angle at 28.4 px/m x2):
`Docs/models/rebuild/<id>/before_after.png` for the eleven rebuilt models; for the three pilots touched again
`Docs/models/rebuild/<id>/wave1_before_after.png` (ixion, zu23_technical, rocket_turret; the pilot's sheet kept).

### NEEDS_HUMAN

- **repair_bay 66.9, radar_site 71.2, ammo_dump 57.8** (4 rounds each; every hard gate passes; the old files scored
  32.5 / 54.2 / 56.5). They are scored against the tower gold (seven small gun towers dense in railings and ladders);
  at the 6,000-triangle cap (decision 6) a 6-15 m building's roofs and berms cannot reach that edge density and
  brightness-region count per pixel. The owner's look decides, or a structure gold set (question 1).

### The whole gate after the wave (no old model broken)

`python Tools/assets/quality_gate.py` over all 230 scored models (Docs/models/quality_report.xlsx / .csv): 25 pass the
whole gate (16 before). Changes on models outside the wave:

- **Now pass the hard gates (5):** main_battle_tank, fighter_jet, attack_helicopter, silver_bug (merged nodes,
  decision 8), monster (its `Main_cannon*` part read as a prefix, as the runtime does).
- **Now fail only the new cap (decision 6), 25 towers over 6,000 triangles:** aa_turret, aa_turret_a,
  artillery_emplacement, artillery_emplacement_a, c_ram, c_ram_a, c_ram_b, drone_hangar, drone_hangar_a,
  drone_hangar_b, ew_tower_a, guard_tower, guard_tower_a, gun_turret, gun_turret_a, gun_turret_b, heavy_flak_tower,
  heavy_turret, heavy_turret_a, heavy_turret_b, missile_battery, missile_battery_a, missile_battery_b, shield_tower_a,
  shield_tower_b (10 of them failed something else already). No light vehicle is over 7,500. These need trimming in
  a later wave (question 2).
- **Boss soft scores moved with the per-frame gold (decision 5):** ground bosses mostly up (behemoth 76.5 -> 99.6,
  mobile_fortress 70.6 -> 94.6), rail bosses down against nuke_train (armored_train 92.9 -> 81.8, rail_supergun
  90.5 -> 76.4), sea up against leviathan. No hard gate changed by it.
- **The structure body rule** (roof / walls / berm count, the better reading kept) clears the old "single block"
  fail of bunker_shelter_tower, fire_control_centre, troop_shelter and heavy_flak_tower (their other fails stay).
- No other score or hard gate changed. Hard gates passed: 44 models (46 before: +5 above and the wave's models, -15
  newly over the cap).

### Decision items (owner's pilot review)

| # | done |
|---|---|
| 2 | zu23 `barrels: 2`, 2 x 50 rounds at half the damage a round (a magazine fires its barrels in turn); the bosses' ZU-23 copies follow; `full_weapon_audit.py`: DPS 70 / 70.6 unchanged, flag totals unchanged |
| 4 | rocket_turret_a / _b rebuilt on the new base |
| 5 | a gold set per boss frame (ground, rail, air, sea); stand-ins never gold |
| 6 | hard gate `triangles_cap`: light and tower under 1.5 x the class maximum |
| 7 | mara_behemoth's own id noted in REBUILD_LIST (no copy, no pointer yet) |
| 8 | merged nodes accepted for the four gold models (and by a spec's `"merged"`) |
| 9 | canonical mesh order before the glTF export: rocket_turret_a x3 and ixion x2 built byte-identical (md5) |
| 10 | Ixion's "(model tạm)" removed from the Boss sheet's shape cell, unit_sheet.json regenerated by its tool |
| roof guns | kit35 `pintle_mg(post=)`; Ixion, the pilots, bastion's ZU-23 |

### For the lead to render in Unity (cards and ModelScan)

Cards (CardRenders) for the defs drawing these models: fortress_bastion, bastion_mk0, fortress_hive, behemoth_inferno,
behemoth_tempest, stymphalos, ixion, zu23_technical, rocket_turret (and its branches), repair_bay, radar_station,
ammo_depot. ModelScan:

```
MachineBrigade.Editor.ModelScan.RenderBatch -mbScan "fortress_bastion,fortress_hive,behemoth_inferno,behemoth_tempest,stymphalos,ixion,zu23_technical,rocket_turret,rocket_turret_a,rocket_turret_b,repair_bay,radar_site,ammo_dump"
```

### Owner questions

1. Structures (repair_bay, radar_site, ammo_dump) against the tower gold under the 6,000 cap: a structure gold set
   like decision 5, or judge them on the look?
2. 25 old towers are over the new cap: trim them in wave 2 (they are P1 / P2 in REBUILD_LIST anyway)?
3. zu23: twice the rounds (2 x 50) at half the damage keeps the DPS; the card now shows a 100-round magazine at 3.5
   damage. Fine, or keep the old single-barrel data and only the two muzzles?

## Lane B (the ten wave 1 vehicles)

(Joined from WAVE_1_REPORT_B.md by the lead.)

Ten vehicles rebuilt from scratch on branch `feature/p35-w1b`, each in its own new Blender script on the kit35 library
with a build spec first (prompt 35 sections 4 and 7). Lane A reports the bosses and towers in `WAVE_1_REPORT.md`; the
lead joins the two. Decisions: Docs/DECISIONS.md "Prompt 35 wave 1 (lane B)". Blender and Python only: no Unity run, no
test, sim or measure.

## Rows

Soft score 0-100 against the gold mean of the class (Tốt >= 80); before = the committed GLB at the start of the wave.
Light (wheeled) class 3,000-5,000 triangles, kept under 1.5 x (7,500, owner decision 6); heavy class 4,000-7,000; jet
4,000-7,000. Every row passes every hard gate (`python Tools/assets/quality_gate.py --ids <id>`: parts, mounts and
muzzles, size, own geometry, zero-area, COLOR_0, colour zones, AO / dust / wear, not a single block), the spec check
(`Tools/blender/specs/validate_specs.py --glb <id>`) and glb_check (accepted with `--reason "P35 wave 1"`).

| model | real reference | script | triangles before -> after | size L x W x H (target) | soft before -> after | gate | rounds |
|---|---|---|---|---|---|---|---|
| `supply_truck` | KamAZ-6350 8x8 cab-over, tarp, crates, M2 on a cab ring | `mb_p35_supply_truck.py` | 2,862 -> 7,494 | 8.48 x 2.12 x 2.62 (8.37 x 2.02 x 2.42) | 72.1 -> 87.8 | pass | 4 |
| `ammo_carrier` | M977 HEMTT, flat racks, palletised ammunition, rear crane | `mb_p35_ammo_carrier.py` | 3,388 -> 7,492 | 8.74 x 2.17 x 2.69 (8.36 x 2.02 x 2.46) | 70.1 -> 92.0 | pass | 3 |
| `vbied` | Mosul "Iron Coffin" armoured pickup | `mb_p35_vbied.py` | 1,574 -> 4,698 | 4.89 x 1.73 x 1.71 (4.58 x 1.68 x 1.6) | 59.7 -> 86.2 | pass | 4 |
| `elite_mlrs` | HIMARS armoured-cab truck + M270 twin-pod module | `mb_p35_elite_mlrs.py` | 2,692 -> 7,446 | 7.09 x 2.44 x 3.22 (7.01 x 2.3 x 2.99) | 68.0 -> 87.7 | pass | 4 |
| `counter_battery_radar` | AN/TPQ-53 on an FMTV 6x6 | `mb_p35_counter_battery_radar.py` | 2,396 -> 6,956 | 6.71 x 2.36 x 3.12 (6.65 x 2.3 x 2.89) | 73.0 -> 87.0 | pass | 2 |
| `lancet_truck` | KamAZ Typhoon-K 6x6 + Lancet catapult rail | `mb_p35_lancet_truck.py` | 2,314 -> 7,300 | 7.52 x 2.20 x 2.84 (7.41 x 2.02 x 2.7) | 62.9 -> 94.3 | pass | 3 |
| `microwave_vehicle` | Leonidas-class HPM array on a JLTV-class 4x4 | `mb_p35_microwave_vehicle.py` | 4,914 -> 6,314 | 5.91 x 2.16 x 3.11 (5.8 x 2.1 x 2.9) | 79.7 -> 80.6 | pass | 2 |
| `smoke_carrier` | M58 Wolf (M113A3 + smoke generator) | `mb_p35_smoke_carrier.py` | 3,698 -> 8,458 | 4.55 x 2.35 x 2.72 (4.21 x 2.24 x 2.64) | 84.9 -> 100 | pass | 2 |
| `elite_mbt` | T-90M | `mb_p35_elite_mbt.py` | 7,288 -> 10,002 | 9.23 x 3.57 x 2.87 (8.96 x 3.53 x 2.64) | 94.3 -> 89.6 | pass | 3 |
| `swarm_carrier` | C-130J, ramp open, drone rack | `mb_p35_swarm_carrier.py` | 3,464 -> 4,918 | 11.96 x 16.32 x 4.91 (11.93 x 16.3 x 4.79) | 95.0 -> 85.1 | pass | 3 |

Before, every one of the ten failed a hard gate (shared geometry 41-87 % with the model it borrowed from, missing
parts such as axles, mantlet / idler, the jet's tail / intakes / pylons, or the triangle floor). After: shared
geometry 0-15 % (the shared part is the lane helpers' small pieces: wheels, gun ring), no other model's own-geometry check names one of the ten (full gate, `--no-write`: 230 models).

elite_mbt and swarm_carrier score lower than the files they replace: those were copies that failed hard gates; the new
ones are their own and pass every gate (DECISIONS "Prompt 35 wave 1 (lane B)", old vs new).

**NEEDS_HUMAN: none** (every model passed within four rounds).

## Pictures

Before / after sheets (Blender Workbench, material colours: front, rear, side, top, 3/4 front, 3/4 rear, and the battle
angle at the default zoom's 28.4 px per metre, x2): `Docs/models/rebuild/<id>/before_after.png` for the ten ids.

**In-game shots (the game's preview scene) are for the lead to render in Unity:**

```
MachineBrigade.Editor.ModelScan.RenderBatch -mbScan "supply_truck,ammo_carrier,vbied,elite_mlrs,counter_battery_radar,lancet_truck,microwave_vehicle,smoke_carrier,elite_mbt,swarm_carrier"
```

Points to look at in Unity: the Radar spinner on the counter-battery radar (the whole array turns, as before), the
swarm carrier's four Propeller spinners and its Part_wing / Mount_Flare points, the vbied's Turret (its roof hatch:
kamikaze, mainAim Hull), the elite_mlrs launch points (`Pods` pair and `Tubes_bore`), the lancet truck's `Box_face`.

## Roof guns

Every roof-mounted gun of the ten (supply_truck, ammo_carrier, elite_mlrs, counter_battery_radar, lancet_truck,
smoke_carrier, elite_mbt's remote station) stands on `mb_p35b_parts.raised_gun`: a riser ring (or a post for the remote
station), the pintle, the cradle, the receiver with spade grips, the barrel with carrying handle and flash hider, the
ammunition can on its tray and the shield (none on the remote station), so it clears the roof line at the battle
camera (MODEL_STANDARD "Roof guns").

## Kit requests (for lane A, mb_kit35.py)

1. A lean wheel: `truck_wheel` costs about 700 triangles a wheel, so a 6x6 or 8x8 cannot stay under 1.5 x the light
   maximum with it. Lane B used its own `mb_p35b_parts.tread_wheel` (tread rows alternating in radius, about 250
   triangles, seg / rim_seg parameters); worth moving into the kit.
2. `side_skirt(..., hinged=False)` still writes four bolts per panel into `Kit_hinges` (800 triangles on a tank's ten
   panels): a `bolts=False` switch.
3. `era_bricks`: bolts optional (two per brick doubles a glacis block's cost).
4. `pintle_mg`: the owner's roof-gun rule would like the riser ring / post and the cradle in the kit function itself
   (lane B's `raised_gun` is a candidate).

## Owner questions

1. `microwave_vehicle` has no unit_refs row: built as a Leonidas-class flat microwave array on a JLTV-class utility
   4x4. Confirm, or name the reference.
2. `elite_mlrs` pairs the HIMARS truck (its modelSize) with the M270's two-pod launcher-loader module so it reads apart
   from the plain mlrs (one HIMARS pod). Fine?
3. The gate scores dark paint low (it measures brightness regions and shading edges on base colour): an all-EliteBlack
   tank fell to 79.7. The elites are therefore team-painted with black armour parts, as DECISIONS 25B2 did. If the
   owner wants all-black elites, the gate needs a paint-independent measure for them.

## Lead: Unity check (2026-10-03)
Cards re-rendered for every wave 1 model with a card (supply_truck has none) and ModelScan sheets at the battle
camera's scale in Docs/models/rebuild/<id>/unity_scan.png (23 models). Full gate after both merges: 230 models, 35 pass
every hard gate, 195 not yet (most old models fail the new part-name and floor rules; the waves rebuild them).
