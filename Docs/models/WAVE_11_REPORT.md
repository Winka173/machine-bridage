# Prompt 35 wave 11 report (lane C)

Wave 11, the last wave of prompt 35 (plan Docs/models/WAVES_P35.md): thirteen models rebuilt from scratch on branch
`feature/p35-w11` (from `lead/integration` after wave 9's merge; waves 8 and 10 merged in before the report), each in
its own Blender script (`Tools/blender/mb_p35_<id>.py`) on the kit35 library and lane C's helpers, with a build spec
first (`Tools/blender/specs/<id>.json`). Decisions: Docs/DECISIONS.md "Prompt 35 wave 11 (lane C)". The prompt's final
report: Docs/models/REBUILD_REPORT.md. Blender and Python only: no Unity run, no test, sim or measure.

## Models

Soft score 0-100 against the gold of the class (bosses against their frame's set). "Before" = the committed GLB at the
start of the wave, on the same gate. Every row passes every hard gate (`quality_gate.py`), the spec check
(`validate_specs.py --glb`) and glb_check (0 errors; accepted with `--reason "P35 wave 11"`). Before, 9 of the 13
failed a hard gate.

| model | real reference | triangles before -> after | soft before -> after |
|---|---|---|---|
| `drop_pod` | Soyuz descent module (retro-rocket landing), ODST / 40k pods: eight-sided capsule, retro ring, legs, fins | 2,612 -> 6,090 | 66.6 -> 83.5 |
| `hyperion` | Znamya 2 orbital mirror, ISS truss: hex lattice ring with mirror facets, core, sun-beam emitter, solar wings | 7,914 -> 19,014 | 77.1 -> 100 |
| `mine_rocket_truck` | ISDM Zemledeliye (two 25-tube packages) on a KamAZ-5350-family 6x6 cab-over | 5,012 -> 7,340 | 69.1 -> 100 |
| `cerberus` | LeTourneau Overland Train cars: three armoured cars on giant hub-motor wheels, twin 152 mm turret | 12,434 -> 16,026 | 89.1 -> 91.2 |
| `bulwark_post` | NSV 12.7 mm on its 6T7 tripod in a sandbag ring under a mushroom roof, a fallen-tower slab | 1,710 -> 5,140 | 75.1 -> 100 |
| `drone_net_tower` | anti-drone net tunnel over a road: pole pairs, arches, net, zap emitters, generator | 1,378 -> 5,802 | 76.2 -> 97.9 |
| `airborne_vehicle_chute` | lane B's BMD-4M on a P-7 platform under an MKS-350-9 three-canopy cluster | 3,262 -> 13,056 | 76.6 -> 95.0 |
| `flare_searchlight_tower` | 60 cm searchlight with a six-tube flare pack on a four-legged steel tower | 2,296 -> 4,162 | 77.0 -> 93.3 |
| `wheeled_howitzer` | CAESAR 6x6, 52-calibre 155 mm (fix L8's layout kept) | 5,026 -> 7,342 | 82.7 -> 94.3 |
| `prop_attack_plane` | EMB-314 Super Tucano: turboprop, tandem canopy, Hydra pods, wing 12.7 mm | 2,994 -> 4,068 | 88.6 -> 100 |
| `auto_loader_howitzer` | XM2001 Crusader: front crew compartment, unmanned turret, 56-calibre gun | 6,520 -> 9,464 | 92.8 -> 100 |
| `light_attack_heli` | OH-58D Kiowa Warrior / ARH-70: mast sight, stub wings, M134 pods, Ataka tubes | 3,418 -> 4,390 | 100 -> 100 |
| `targeting_station` | Würzburg-Riese radar, coastal rangefinder blockhouse, guyed lattice mast | 4,446 -> 6,486 | 100 -> 95.0 |

Hard fails before: Mount_APS (hyperion), parts (mine_rocket_truck axles / stowage, flare_searchlight_tower base /
walls, prop_attack_plane tail / intakes / exhaust, auto_loader_howitzer mantlet / idler / stowage, targeting_station
roof), size (cerberus 17 %, wheeled_howitzer 14 %), single block (drone_net_tower, airborne_vehicle_chute,
flare_searchlight_tower, targeting_station), light_attack_heli's Muzzle_missile and main mount.

Budgets: light wheeled 7,340 / 7,342 under the 7,500 cap; tower 4,162 under 6,000; structures 5,140 / 6,486 and the
obstacle 5,802 inside 6,000; the jet 4,068 and the helicopter 4,390 in their 4,000-7,000 band; bosses 16.0k / 19.0k in
the 10-20k band. Over the guide (owner rule: kept): auto_loader_howitzer 9,464 (tracked 7,000) and
airborne_vehicle_chute 13,056 (air_other 7,000: the ground model's 9,464 plus the rig). Renderers under glb_check's
caps (the chute variant merges the vehicle's static parts by material: 43 of 44).

Runtime nodes: every old pivot kept at its place, the bosses' checked node by node against the old files. Added:
hyperion `Mount_APS`; light_attack_heli `Mount_gun` / `.001` (the pods' pivots, now carrying the old `Muzzle_gun` /
`.001`) and `Muzzle_missile` / `.001`. Plain pivots without a drawn weapon where the data has none:
light_attack_heli `Muzzle_rocket` / `.001`, auto_loader_howitzer `Mount_mg` / `Muzzle_mg`, cerberus `Mount_gun` /
`Muzzle_gun` and `Muzzle_missile` / `.001` (parts its variant drops). cerberus's per-barrel muzzles come from
`mb_fix_barrels` (now under EXTRA: the builder models both barrels).

## Pictures

Before / after sheets (Blender Workbench, material colours; seven angles): `Docs/models/rebuild/<id>/before_after.png`
for the thirteen ids.

**For the lead to render in Unity** (cards and ModelScan sheets): the thirteen ids below. **No card** in
Resources/UI/Cards/manifest.json for `drop_pod` and `airborne_vehicle_chute` (as before: they are not deck units).

```
MachineBrigade.Editor.ModelScan.RenderBatch -mbScan "drop_pod,hyperion,mine_rocket_truck,cerberus,bulwark_post,drone_net_tower,airborne_vehicle_chute,flare_searchlight_tower,wheeled_howitzer,prop_attack_plane,auto_loader_howitzer,light_attack_heli,targeting_station"
```

Points to look at in Unity: hyperion's size and the sun-beam emitter's aim (Muzzle_main forward and down from the
yoke); cerberus's three Part_* cars breaking apart and the twin muzzles; light_attack_heli's pods turning on their
Mount_gun pivots; the chute variant falling (canopies 8-10 m up); targeting_station's `Radar` head turning clear of the
blockhouse (1.7 m dish, 0.75 m clearance); prop_attack_plane's Part_wing cut and the flare points (wrappers).

## The whole gate after the wave

`python Tools/assets/quality_gate.py` (report written: quality_report.csv / .xlsx) over all 230 scored models, after
the merge of waves 8 and 10: 199 pass the whole gate; the thirteen wave 11 ids all pass (shared geometry 0.3-10 %).
No other model's own-geometry check fails on a wave 11 model; the largest share naming one is gun_turret_b's 21 %
with auto_loader_howitzer (common kit pieces; limit 30 %).

## NEEDS_HUMAN

None: every model passes every hard gate with soft >= 80 (drop_pod the lowest at 83.5).

## Owner questions

None new from this wave; the open ones are collected in REBUILD_REPORT.md.
