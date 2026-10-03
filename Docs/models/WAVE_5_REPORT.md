# Prompt 35 wave 5 report (lane A)

Wave 5 of prompt 35 (sections 7 and 8; the list in Docs/models/WAVES_P35.md). Branch `feature/p35-w5` from
`lead/integration`, with waves 3 and 4 merged in as they landed. Decisions: Docs/DECISIONS.md "Prompt 35 wave 5
(lane A)" (with the lead calls of 2026-10-03). Blender and Python only: no Unity run, no test, sim or measure.

Gate: `Tools/assets/quality_gate.py` (hard gates + a 0-100 soft score against the class gold; Tốt >= 80). Specs:
`Tools/blender/specs/<id>.json` (`validate_specs.py --glb`: every node named, every mount and muzzle, the size within
10 %). Before / after sheets (Blender Workbench, six angles and the battle view x2): `Docs/models/rebuild/<id>/before_after.png`.

## The 20 models

"Rounds" = build-and-gate rounds (section 7, at most 4). Every one passes every hard gate; shared geometry 0.6-16 %.

| model | builder | what it is now | triangles before -> after | soft before -> after | rounds |
|---|---|---|---|---|---|
| `monster` | mb_p35_wave5_bosses | 800 mm gun carriage on four tracked pods (2B1 Oka / Object 271): slab gun house, recoil cylinders, shell hoist, twin 100 mm and 40 mm turrets, casemate 155 mm, ZU-23 balconies, Kornet, engine house | 23,626 -> 39,598 | 62.1 -> 86.1 | 3 |
| `landing_hovercraft` | same | Zubr / LCAC: skirt with fingers, cargo deck with tarp-covered vehicles, side structures and wheelhouse, ramp, two ducted props, four AK-630, two A-22, APS head | 16,984 -> 18,890 | 74.8 -> 85.5 | 4 (+ a fix) |
| `typhon` | same | Typhoon: wide flat hull, worn anechoic tiles, 20 tubes ahead of the sail, sail with SAM post, bow planes, sonar dome, cruciform stern, twin shrouded screws, deck gun | 6,876 -> 13,260 | 48.6 -> 69.1 | 4, NEEDS_HUMAN |
| `caspian` | same | Lun ekranoplan: boat hull, cockpit, eight turbofans on the canard pylon, short wings with floats, T-tail, six Moskit canisters, CIWS, two ZU-23 turrets | 6,766 -> 11,042 | 69.7 -> 80.9 | 4 |
| `morrigan` | mb_p35_wave5_air | Su-57 type: lifting body, LEVCONs, spaced nacelles and tunnel, open side and main bays, 3D nozzles and sting, canted fins | 1,344 -> 7,656 | 54.8 -> 72.0 | 3, NEEDS_HUMAN |
| `sky_fortress` | same | AC-130J type, dark: chined fuselage, sensor nose, six-blade props, side guns on their mounts, Griffin ramp launcher, GBU-39 pylons, jammers | 3,084 -> 7,300 | 82.0 -> 87.3 | 1 |
| `twin_tank` | mb_p35_wave5_tanks | twin Rh-120 in two mantlets on a wide flat turret, raised 12.7 mm, bustle rack, skirts | 7,154 -> 9,870 | 87.4 -> 100 | 3 |
| `titan_tank` | same | four tracks, broad hull, twin 140 mm in one mantlet, TOW boxes, APS panels and clusters (Mount_APS added), rear MG sub-turret | 8,384 -> 10,282 | 92.8 -> 95.5 | 4 |
| `turtle_tank` | same | T-72 under a corrugated shed (patches, doors, slits), anti-drone net, KMT-7 mine roller | 3,938 -> 7,348 | 73.4 -> 96.8 | 2 |
| `laser_tank` | same | tracked chassis, beam director with the big mirror on a fork, radiator banks, power cabinet, RWS | 3,844 -> 7,266 | 71.8 -> 95.3 | 3 |
| `aa_57mm_vehicle` | same | 2S38: BMP-3 hull with trim vane and stern doors, AU-220M turret, sight drum, radar on a mast | 6,028 -> 7,096 | 91.3 -> 100 | 2 |
| `thermobaric_launcher` | same | TOS-1A: T-72 hull, dozer blade, 24-tube box on its turntable and rams, raised 12.7 mm | 4,982 -> 10,028 | 81.0 -> 97.7 | 1 |
| `bunker_vehicle` | mb_p35_wave5_deploy | engineer hull, wide blade, low L7 turret on its riser, side plates, rear spades, the emplacement it raises (bank, sandbags, net) | 7,792 -> 9,356 | 95.5 -> 97.3 | 2 |
| `siege_tank` | same | lofted hull between armoured pods, four I-section legs with rams, spades, the fat 240 mm and the sliding twin 105 mm | 5,924 -> 10,350 | 100 -> 100 (was failing 6 roles) | 3 |
| `gps_jammer_vehicle` | mb_p35_wave5_tanks | EW truck: armoured cab-over cab, 8x8, container shelter, jammer array (Radar), stowed mast sections, RWS | 4,396 -> 7,444 | 84.6 -> 93.8 | 3 |
| `stealth_bomber` | mb_p35_wave5_air | B-2: span-wise lofted flying wing, saw-tooth trailing edge, cockpit hump, dorsal intakes, drag rudders, open bays with JDAMs | 2,096 -> 3,564 | 44.1 -> 71.0 | 3, NEEDS_HUMAN |
| `wingman_drone` | same | XQ-58: chined fuselage, dorsal intake, swept wing, V-tail, EO ball, two AIM-9 | 1,064 -> 2,914 | 90.4 -> 100 | 4 |
| `recon_jet` | same | SR-71: chined fuselage, spike-inlet nacelles, canted fins, corrugated delta | 768 -> 3,068 | 38.3 -> 86.6 | 2 |
| `sky_gunship` | same | AC-130U: round fuselage, four-blade props, left gun deck (105 / 40 / 25), sensor turrets, drop tanks; `_hd` the same builder | 3,652 -> 3,562 | 100 -> 95.6 (was failing 4 roles) | 2 |
| `elite_attack_helicopter` | same | AH-64E with the Longbow radome, its own body and rotor (0.6 % shared; was 98 % the V2 Apache), elite marks | 4,398 -> 5,606 | 85.4 -> 88.5 | 1 |

17 of 20 reach Tốt; 3 are NEEDS_HUMAN on the soft score only.

### NEEDS_HUMAN (all hard gates pass)

- **typhon 69.1**: a submarine against the sea-boss gold (warships dense in masts, rails and mounts): its smooth hull
  gives little silhouette and edge density; tiles, rails and fittings already added (the old file scored 48.6).
- **stealth_bomber 71.0**: a flying wing has almost no side or front silhouette and is symmetrical (old 44.1).
- **morrigan 72.0**: a stealth fighter's clean faces against the air-boss gold (gunships and the drone carrier).

More detail on these would be padding (prompt 35 section 1). Owner question 2.

## Other items

- **Lead call 3, gun_turret_b**: gun_57_auto barrels 2, damage 35, clip 12, cooldown 0.25, clipReload 2.65: cycle
  5.40 s and DPS 78 unchanged; real name "AU-220 57 mm (tower, twin)". full_weapon_audit: flag totals unchanged
  (TOO FAST 80, TOO SLOW 8, UNIT 1, WAVE 1 33, FAMILY 0, DISPLAY 0). Muzzle_b1 / b2_main on the model.
- **Kit (lanes B and C)**: track_run, sandbag_run, camo_net, earth_pad, ring_from_half, section_loft, slab_loft,
  ellipse_half, store, door(frame_mat=); tests added (not run). **Missile fix**: stymphalos rebuilt (its drones'
  missiles pointed backwards); recon_drone, strike_drone, artillery_emplacement_b byte-identical.
- **Gate**: data-aware roles (`systems_absent`), fixed-wing bosses as air, `Bogie_*` names read as rail (noted).
- **Byte-identical builds**: a full rebuild of the twenty matches the committed files (landing_hovercraft fixed:
  overlapping parts made its AO bake depend on object order).
- glb_check baseline accepts the wave's files (518 files, 0 errors); renderer counts under every hard cap.

## The whole gate after the wave

`python Tools/assets/quality_gate.py`: 230 models, **96 pass every gate** (51 at wave 2; waves 3 and 4 merged). The
wave's gate changes only remove role requirements (no model got worse); dazzler_vehicle's shared share fell (67 % ->
40 %) now that gps_jammer_vehicle is its own. Still open from wave 1 (specs only, not changed here):
`validate_specs --glb` flags ammo_dump, radar_site, repair_bay, rocket_turret_a and stymphalos (node names and
heights of the wave 1 files).

## For the lead to render in Unity

Cards (CardRenders, by model id): monster, landing_hovercraft, typhon, caspian, morrigan, sky_fortress, twin_tank,
titan_tank, turtle_tank, laser_tank, aa_57mm_vehicle, thermobaric_launcher, bunker_vehicle, siege_tank,
gps_jammer_vehicle, stealth_bomber, wingman_drone, recon_jet, sky_gunship, elite_attack_helicopter; also stymphalos
(missiles) if re-shot. gun_turret_b's picture is unchanged (muzzles only). **No card**: none (all twenty have one).
ModelScan:

```
MachineBrigade.Editor.ModelScan.RenderBatch -mbScan "monster,landing_hovercraft,typhon,caspian,morrigan,sky_fortress,twin_tank,titan_tank,turtle_tank,laser_tank,aa_57mm_vehicle,thermobaric_launcher,bunker_vehicle,siege_tank,gps_jammer_vehicle,stealth_bomber,wingman_drone,recon_jet,sky_gunship,elite_attack_helicopter,stymphalos"
```

Points to look at in Unity: bunker_vehicle and siege_tank deploying (the rigs keep their pivots; the bunker's new
bank grows from 1 %); typhon surfacing with its silo forward; titan_tank's Mount_APS and per-barrel muzzles;
gun_turret_b alternating barrels; the gunships' left-side fire; landing_hovercraft's ramp and fans.

## Owner questions

1. Typhon: the real Typhoon's silo is ahead of the sail; the old file had it aft. Keep the real layout?
2. typhon, stealth_bomber, morrigan at 69-72 after their rounds: accept on the look, or give submarines / flying
   wings / stealth fighters gold sets of their own?
3. Rows with no sheet entry were built from their data: recon_jet as the SR-71 (its modelSize is exactly 0.4 x),
   aa_57mm_vehicle as the 2S38, gps_jammer_vehicle as a generic EW truck. Keep?
