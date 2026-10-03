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

_Lane B fills this section: supply_truck, vbied, elite_mlrs, ammo_carrier, counter_battery_radar, smoke_carrier,
lancet_truck, microwave_vehicle, elite_mbt, swarm_carrier: before / after table, pictures, NEEDS_HUMAN, its ids to
render._
