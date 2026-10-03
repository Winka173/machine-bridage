# Prompt 35 wave 8 report (lane A)

Wave 8 of prompt 35 (the list in Docs/models/WAVES_P35.md). Branch `feature/p35-w8` from `lead/integration` (wave 5
merged there). Decisions: Docs/DECISIONS.md "Prompt 35 wave 8 (lane A)" (with the lead calls of 2026-10-03 on the
wave 5 questions). Blender and Python only: no Unity run, no test, sim or measure.

Gate: `Tools/assets/quality_gate.py` (hard gates + a 0-100 soft score against the class gold; Tốt >= 80). Specs:
`Tools/blender/specs/<id>.json` (`validate_specs.py --glb`: every node named, every mount and muzzle, the size within
10 %). Before / after sheets (Blender Workbench, six angles and the battle view x2): `Docs/models/rebuild/<id>/before_after.png`.

## The 20 models

18 rebuilt from scratch, each on its own builder; the two gold models checked only. Every one passes every hard gate.

| model | builder | what it is now | triangles before -> after | soft before -> after |
|---|---|---|---|---|
| `behemoth` | mb_p35_wave8_bosses | land battleship: two track units a side, twin 152 mm turret with roof flak and Mount_APS, hull and sponson twin-120 turrets, rocket box, missile racks, one-sided field kit | 21,610 -> 25,692 | 99.6 -> 99.6 (was failing Mount_APS) |
| `mobile_fortress` | same | crawler-transporter: four twin-track corner trucks on jacks, the platform, glazed command bridge, 203 mm turret with the roof gun, rocket pods, silo, SAM box, EMP dish, crane | 23,256 -> 25,402 | 94.6 -> 93.4 |
| `leviathan` | same | Iowa-modernised battleship: every part node and mount kept, triple 406 / 155 mm with their own per-barrel muzzles, pagoda tower, radar, Mount_APS, ABL boxes, Harpoons, mainmast, funnel, flight deck, stern gate | 26,744 -> 24,358 | 100 -> 98.8 (was failing Mount_APS) |
| `armored_train` | same | BP-35 locomotive, gun wagon and mortar flatcar on the old car layout and lengths; rear gun casemate and two flak mounts give the data's 7 muzzles; riveted seams, sandbags | 21,954 -> 26,470 | 81.8 -> 89.5 (was failing muzzles 5/7) |
| `mega_gunship` | mb_p35_wave8_air | ACH-47 on the Chinook airframe: fuel pods, ramp, two three-blade rotors, chin turrets, miniguns, stub pods, belly missile rack, door guns for the two HMGs | 11,476 -> 9,284 | 99.3 -> 100 (was failing muzzles 7/9) |
| `gunship_heli` | same | Mi-24P: double-bubble canopies, cabin door guns, five-blade rotor, anhedral stubs with pods and ATGM tip rails, chin gun turret | 4,660 -> 5,624 | 81.4 -> 91.5 (was failing stub_wings, main mount) |
| `headquarters` | mb_p35_wave8_fort | the same 14 x 12 m plinth and pivots: battered cast block, portal and blast door, bastion tower flak, gun drum and twin heavy turret, second flak nest (Mount_mg.001), helipad wing, radar yard | 14,164 -> 18,228 | 100 -> 97.8 (was failing Mount_mg 1/2) |
| `dragons_teeth` | same | Westwall teeth on plinths over a ragged earth bed, lift lines, a broken tooth with rebar, a hedgehog, stakes (tiles every 5 m) | 1,556 -> 3,592 | 73.2 -> 84.2 |
| `dragons_teeth_a` | same | hedgehog branch: three big and two small Czech hedgehogs of chamfered L-angles on bolted shoes, chained | 2,124 -> 4,340 | 65.9 -> 98.8 (was failing ao_dust_wear) |
| `mlrs` | mb_p35_wave8_trucks | M142 HIMARS: LSAC cab, one six-round pod on its module, cab-roof gun on a post | 2,652 -> 7,472 | 74.8 -> 96.5 (was failing axles, stowage, sloped faces) |
| `grad_truck` | same | BM-21 on the Ural-375: long bonnet, canvas-top cab, 40-tube pack, pedestal gun, jacks | 6,342 -> 7,408 | 87.5 -> 95.8 (was failing stowage, sloped faces) |
| `command_vehicle` | same | Stryker CV: faceted 8x8 hull, folded mast, dish, whips, rolled tent, cupola gun on its riser | 3,084 -> 6,096 | 73.5 -> 94.9 (was failing glass) |
| `railgun_truck` | same | its own vehicle: heavy 8x8, low cab under the rails, twin rails in insulator bands, capacitor bank, glowing radiators | 2,924 -> 7,482 | 80.6 -> 97.3 (was failing axles, stowage, sloped faces) |
| `radar_scout` | same | Fennek-class 4x4: wedge hull, telescopic sensor mast, remote 12.7 mm | 3,362 -> 5,352 | 78.5 -> 93.0 |
| `heavy_aa` | same | Pantsir-S1 on the KamAZ 8x8: twin 30 mm and six-tube packs either side, search and tracking radars | 4,524 -> 7,278 | 81.4 -> 94.8 (was failing axles, stowage, sloped faces) |
| `wheeled_gun` | same | Centauro II: faceted 8x8 hull, Hitfact II turret, 120 mm with baffle brake, roof gun on its post | 3,058 -> 7,178 | 70.6 -> 96.1 (was failing axles, glass, stowage) |
| `heavy_tank` | mb_p35_wave8_ground | Object 195: seven wheels under skirts, crew-capsule hatches, unmanned turret, 152 mm, the 30 mm beside it; `_hd` the same builder with bolt rows | 5,662 -> 9,296 | 81.2 -> 99.1 (was failing mantlet, idler, stowage) |
| `river_gunboat` | same | Shmel-type river monitor: hard-chine hull, tank turret with the 100 mm, armoured wheelhouse, aft gun tub | 2,302 -> 5,224 | 81.7 -> 99.3 |
| `attack_helicopter` | (gold, prompt 27 V2) | unchanged: passes every gate on its names and nodes | 4,722 -> 4,722 | 92.7 -> 92.7 |
| `fighter_jet` | (gold, prompt 27 V2) | unchanged: passes every gate on its names and nodes | 4,308 -> 4,308 | 99.2 -> 99.2 |

20 of 20 reach Tốt and pass every hard gate. NEEDS_HUMAN: none.

## Other items

- **Exceptions handled.** headquarters keeps its footprint and pivots exactly (the prompt 32 HQ types swap the def,
  not the model). leviathan keeps every part node, mount and muzzle place (the PreviewSalvo of play-test 12 lays its
  maingun parts by Part_gun and their first mount); its triple turrets carry Muzzle_b1-b3 from the builder.
  armored_train keeps its car ends, lengths and couplings. railgun_truck no longer shares anything with ixion.
- **Wrappers.** mb_fix_barrels no longer twins behemoth (its builder models the barrels and writes the per-barrel
  muzzles, same names and places); mb_p34_barrels no longer lists leviathan. headquarters keeps the wrapper.
- **Wave 1 specs.** ammo_dump, radar_site, repair_bay, rocket_turret_a and stymphalos now pass `validate_specs --glb`
  (node names after the wave 1 renderer-cap merge; the approved wave 1 heights; the validator skips a variant boss's
  dropped parts).
- **Builds.** sixteen of the eighteen rebuild byte-identically; heavy_tank and wheeled_gun differ in two COLOR_0
  vertices of the roof gun when built together with the other ids (the kit pintle's coincident post cap): the
  committed files are the single-model builds.
- glb_check baseline accepts the wave's files (518 files, 0 errors; renderer counts under every hard cap).

## The whole gate after the wave

`python Tools/assets/quality_gate.py`: 230 models, **112 pass every gate** (96 after wave 5). No model outside the wave
changed. Still failing nearby (other lanes' waves): elite_heavy_tank (wave 7, lane C).

## For the lead to render in Unity

Cards (CardRenders, by model id; every one has a card): behemoth, mobile_fortress, leviathan, armored_train,
mega_gunship, gunship_heli, headquarters, dragons_teeth, dragons_teeth_a, mlrs, grad_truck, command_vehicle,
railgun_truck, radar_scout, heavy_aa, wheeled_gun, heavy_tank, river_gunboat. **No card**: none. attack_helicopter and
fighter_jet: nothing to re-render (unchanged). ModelScan:

```
MachineBrigade.Editor.ModelScan.RenderBatch -mbScan "behemoth,mobile_fortress,leviathan,armored_train,mega_gunship,gunship_heli,headquarters,dragons_teeth,dragons_teeth_a,mlrs,grad_truck,command_vehicle,railgun_truck,radar_scout,heavy_aa,wheeled_gun,heavy_tank,river_gunboat"
```

Points to look at in Unity: leviathan's PreviewSalvo (the three main turrets, each barrel's flash) and the aft turret
turned to its rest arc; behemoth_mk0 / fenrir / scylla hiding their dropped parts; the HQ's second flak nest firing;
armored_train on a rail run (the rear casemate's shots, the two flak mounts turning); mega_gunship's door guns;
gunship_heli's flare points (mb_flare_mounts found its dispensers: L / R / TL / TR only).

## Owner questions

1. railgun_truck is its own vehicle now (a heavy 8x8 with the twin-rail gun salvaged from Tempest); keep this read?
2. The HQ's fortress types add a `gun` weapon (turret_gun_120_long / bofors_l70) that has no mount of its own on the
   model (as before): add a visible gun for them in a later pass?
3. From wave 5 (lead call 3): recon_jet as the SR-71, aa_57mm_vehicle as the 2S38, gps_jammer_vehicle as a generic EW
   truck: keep?
