# Prompt 35 wave 10 report (lane B)

Wave 10 of prompt 35 (plan: Docs/models/WAVES_P35.md): its twenty models, done by lane B on branch `feature/p35-w10`
(from lead/integration with wave 6 merged). Nineteen are rebuilt from scratch, each with its own builder
(`Tools/blender/mb_p35_<id>.py`; cp_relay and cp_relay_a share `mb_p35_cp_relay.py`) and a build spec written first
(`Tools/blender/specs/<id>.json`), registered inside the builders dict of `build_assets.py`; silver_bug (the
owner-approved gold, prompt 27 V2) is untouched. Decisions: Docs/DECISIONS.md "Prompt 35 wave 10 (lane B)". Blender
and Python only: no Unity run, no test, sim or measure.

Gate: `Tools/assets/quality_gate.py` (hard gates + the 0-100 soft score against the gold of the class or boss frame;
Tốt >= 80). Bosses are scored against their frame's gold (air: command_airship; ground: daedalus; rail:
rail_supergun); the wheeled class borrows the tracked gold, towers and structures each other's.

## Rows

"Before" = the committed GLB at the start of the wave. Every "after" row passes every hard gate (triangle floor and
the towers' / light units' caps, parts and roles, mounts / muzzles / Mount_Flare / Mount_APS / boss part nodes, size,
own geometry, zero-area, COLOR_0, colour zones, AO / dust / wear, not a single block), the spec check
(`validate_specs.py --glb <id>`) and glb_check (0 errors). Size = L x W x H in metres as built (target: modelSize,
else the old file). "Shared" = triangles also found in another model family (limit 30 %).

| model | class (gold) | real reference | triangles before -> after | size | soft before -> after | status | shared |
|---|---|---|---|---|---|---|---|
| `command_airship` | boss (air) | Airlander 10 / P-791, Kirov (media) | 22,840 -> 18,808 | 42.80 x 32.91 x 15.39 | 76.0 -> 91.5 | Tốt | 6.1 % |
| `daedalus` | boss (ground) | Acclamator class (media) | 14,772 -> 13,190 | 36.00 x 20.33 x 13.53 | 68.4 -> 85.2 | Tốt | 4.1 % |
| `rail_supergun` | boss (rail) | EMRG scaled up, Barguzin rail car | 36,726 -> 11,894 | 58.98 x 8.04 x 16.50 | 76.4 -> 85.0 | Tốt | 4.5 % |
| `silver_bug` | boss (air) | gold, prompt 27 V2 | 21,760 (unchanged) | 36.32 x 18.23 x 13.15 | 86.3 (unchanged) | Tốt | 4.4 % |
| `heavy_bomber` | jet | B-52 Stratofortress | 3,540 -> 5,472 | 20.22 x 22.60 x 5.72 | 78.6 -> 91.1 | Tốt | 0.4 % |
| `heavy_lift_helicopter` | helicopter | Mi-26 | 3,858 -> 5,388 | 8.03 x 6.58 x 2.05 | 60.1 -> 84.4 | Tốt | 1.7 % |
| `twin_rotor_gunship` | helicopter | ACH-47A "Guns-A-Go-Go" | 4,366 -> 8,392 | 11.27 x 5.70 x 4.73 | 64.0 -> 84.8 | Tốt | 1.4 % |
| `coastal_ashm_vehicle` | wheeled | NSM Coastal Defence System | 3,508 -> 6,758 | 7.22 x 2.75 x 3.02 | 73.6 -> 90.7 | Tốt | 12.5 % |
| `radar_support_vehicle` | wheeled | Giraffe AMB / Kasta 4x4 | 3,368 -> 6,540 | 4.76 x 2.11 x 4.06 | 77.6 -> 98.3 | Tốt | 13.6 % |
| `sp_mortar` | wheeled | Patria AMV + AMOS (L8 layout) | 5,748 -> 7,226 | 6.39 x 2.35 x 2.69 | 64.0 -> 90.3 | Tốt | 8.0 % |
| `heavy_turret_a` | tower | A-222 Bereg / AK-130 ashore (coastal branch) | 9,670 -> 5,980 | 12.79 x 8.31 x 6.47 | 60.4 -> 80.5 | Tốt | 14.8 % |
| `shield_tower_b` | tower | Shield Battery (media; ward branch) | 6,236 -> 5,438 | 7.78 x 8.11 x 4.71 | 60.8 -> 84.2 | Tốt | 3.1 % |
| `artillery_emplacement_a` | tower | M198 / M777 + AN/TPQ-50 (CB branch) | 8,426 -> 5,919 | 10.16 x 7.10 x 3.95 | 78.2 -> 80.2 | Tốt | 7.8 % |
| `cp_relay` | tower | field radio relay, lattice mast | 2,434 -> 4,912 | 4.00 x 4.02 x 7.80 | 80.0 -> 98.4 | Tốt | 7.4 % |
| `cp_relay_a` | tower | relay + comms container | 2,462 -> 4,858 | 4.00 x 4.02 x 7.80 | 79.0 -> 97.1 | Tốt | 7.5 % |
| `manpads_tower` | tower | Djigit twin Igla mount | 1,750 -> 3,072 | 3.24 x 3.22 x 2.28 | 60.7 -> 90.8 | Tốt | 4.6 % |
| `recoilless_gun_tower` | tower | SPG-9 Kopyo | 2,318 -> 3,818 | 4.24 x 4.13 x 2.92 | 64.5 -> 89.3 | Tốt | 3.7 % |
| `flare_tower` | tower | flare-mortar post (L8 layout) | 5,102 -> 5,534 | 3.72 x 3.62 x 5.17 | 62.9 -> 85.1 | Tốt | 2.8 % |
| `visual_jammer` | tower | dazzler / decoy-light post (L8 layout) | 3,672 -> 5,750 | 6.25 x 5.11 x 6.68 | 64.2 -> 85.4 | Tốt | 1.7 % |
| `coastal_battery` | structure | A-222 / AK-130 / M284 shore battery | 4,394 -> 5,806 | 10.74 x 8.30 x 4.47 | 64.9 -> 84.0 | Tốt | 10.3 % |

Before, 18 of the 20 failed the gate (Cần sửa or a hard fail: missing axles / stowage on the trucks, walls on the
relays and the coastal battery, weapons / tail rotor / stub wings on the helicopters, the free secondaries' mounts on
heavy_bomber and twin_rotor_gunship, the command airship's 6/8 muzzles, daedalus' running gear and Mount_APS, three
single-block bodies, three towers over the 6,000 cap, heavy_turret_a's second muzzle). After: all twenty pass.

What each one is (details in its spec and builder docstring):

- **Bosses**: command_airship two long envelopes (gore seams, ballonet bands, X tail fins, solar arrays on the left,
  the observation blister and antenna farm on the right) joined by the armoured spine deck with the two dual-purpose
  turrets (57 mm + twin 30 mm) and the radar mast, the keel gondola with the bridge, the bomb bay doors on hinge
  pivots, the two drone hangars, the 105 mm ball pods and four riveted engine nacelles with propellers; daedalus the
  arrowhead Acclamator-type hull with the serrated chine, the stepped superstructure and bridge tower (APS emitter),
  turbolasers, the point-defence lasers, twin ball guns, three drop-pod bays, folded landing legs, the six-nozzle
  thruster block; rail_supergun the gun car on four bogies and its track bed, outrigger jacks, the gun house with the
  cradle shroud and the 40 m segmented railgun barrel (glowing rail gap, collars, coolant pipes, truss), capacitor
  banks, the fire-control cabin, the 40 mm turrets and CIWS.
- **Aircraft**: heavy_bomber a B-52 (shoulder wing, four twin-engine pods, tall fin, quad tail turret on its new
  `Mount_gun`, Kh-101 under the inner wing, the bomb bay doors on hinge pivots over the FAB-500 load); the Mi-26
  (eight-blade rotor, glazed nose, roof engines, sponsons, clamshell doors, UV-26 launchers); the ACH-47A (tandem
  rotors, swept aft pylon with the engine pods, chin turret on a new `Turret`, 40 mm pods on new `Mount_mg` / `.001`,
  door guns, armour plates).
- **Vehicles**: the NSM launcher on a 6x6 (forward cab, fire-control box, 2 x 2 canister pack on its turntable,
  jacks); the Giraffe / Kasta radar 4x4 (bonneted cab, RWS on a raised ring, shelter, telescopic mast, array); the
  Patria AMOS (AMV hull, twin 120 mm turret, roof MG on a raised ring with its shield).
- **Towers and structures**: the branches as upgrades of their wave 2 bases (see DECISIONS): coastal heavy turret on
  the shared barbette with long barrels and a search radar, the ward shield tower with three projector arms on the
  base's plinth and cabins, the counter-battery emplacement in the _b berm with a towed 155 mm and its radar, the two
  relays in the cp_relay_b compound; the MANPADS and SPG-9 pits, the flare post and the visual jammer (L8 layouts
  brought to the standard), the sunken coastal battery with its fire-control post and ready magazines.

## NEEDS_HUMAN

None: every model scores Tốt. Points for the owner's look: rail_supergun was a boss gold member and now carries 11.9k
triangles instead of 36.7k (it scores higher: 85.0 against 76.4); shield_tower_b keeps the old low outline (4.7 m)
instead of the base's 9.5 m pylon (the size rule).

## Pictures

Before / after sheets (Blender Workbench, material colours: front, rear, side, top, 3/4 front, 3/4 rear, the battle
angle at the default zoom's 28.4 px per metre, x2): `Docs/models/rebuild/<id>/before_after.png` for the 19 rebuilt
ids.

**For the lead to render in Unity (cards and ModelScan).** Cards (CardRenders) for all nineteen rebuilt ids (every one
has a card in Resources/UI/Cards): coastal_ashm_vehicle, artillery_emplacement_a, heavy_bomber, command_airship,
radar_support_vehicle, heavy_turret_a, daedalus, cp_relay_a, cp_relay, rail_supergun, shield_tower_b,
heavy_lift_helicopter, manpads_tower, flare_tower, sp_mortar, twin_rotor_gunship, visual_jammer, recoilless_gun_tower,
coastal_battery. **No card: none.** silver_bug did not change (no re-shot). The variants drawing these models
(argus from command_airship; heavy_turret.coastal, shield_tower.ward, artillery_emplacement.cb) if their cards are
re-shot. ModelScan:

```
MachineBrigade.Editor.ModelScan.RenderBatch -mbScan "coastal_ashm_vehicle,artillery_emplacement_a,heavy_bomber,command_airship,radar_support_vehicle,heavy_turret_a,daedalus,cp_relay_a,cp_relay,rail_supergun,shield_tower_b,heavy_lift_helicopter,manpads_tower,flare_tower,sp_mortar,twin_rotor_gunship,visual_jammer,recoilless_gun_tower,coastal_battery"
```

Points to look at in Unity: the bay doors (`Part_bay_door_L` / `_R`) on heavy_bomber and command_airship staying shut
until the bomb-run pass animates them; the airship's propellers and radar spinning, argus (0.4375 x, radar and front
engines kept); daedalus' twin ball-gun muzzles and its APS from the bridge tower; the rail supergun's barrel breaking
off as main_gun; the ACH-47A's chin `Turret` and pod mounts, its two rotors; heavy_turret_a's coastal radar spinning
and its two muzzles; the radar truck's and the CB emplacement's `Radar`.

## Roof guns

sp_mortar's 12.7 mm on a raised ring with a small shield, radar_support_vehicle's RWS on a raised ring over the cab
(`mb_p35b_parts.raised_gun`); heavy_turret_a, coastal_battery and artillery_emplacement_a carry their MGs on
`mb_kit35.pintle_mg` posts.

## The whole gate after the wave (no old model broken)

`python Tools/assets/quality_gate.py --no-write` over all 230 scored models: 151 pass. Compared with the lead's
quality_report.csv no model outside waves 6, 7 and 10 changed its hard result or its soft score by more than 0.5 (the
csv predates the wave 6 and 7 merges). glb_check: 0 errors over 518 files, `--compare` clean after the accepts;
warnings only (renderer and triangle budgets: the owner's rule keeps over-budget models). quality_report.xlsx / .csv
are not rewritten on this branch.

## Kit requests (for lane A, mb_kit35.py)

Lane B's generic helpers in `mb_p35b_parts.py`, used again this wave, for a kit home (the kit was not edited):

1. `clutter(a, name, mat, x0, x1, y0, y1, z, n, seed, size=, height=)`: n non-overlapping boxes of varied size on a
   deck (the boss and ship densities; daedalus, command_airship, rail_supergun this wave).
2. `plane(part, x0, x1, y0, y1, z)`: a one-sided deck plate.
3. `portholes(a, points, normal, r=, seg=)`: rim + glass per window (the helicopters, the airship gondola).
4. `merge_parts(a, mapping)`: folds static parts into fewer meshes before the finish (glb_check's renderer caps).

The wave 3 requests stand (`track_run`, `sandbag_run(part=, lean=)`, `camo_net`, `earth_pad(bottom=False)`,
`door(frame_mat=)` are in the kit since wave 5). Gate request (lead): skip the `tail_rotor` role for tandem
helicopters and `weapons` / `stub_wings` for unarmed transports (handled here by spec "merged").

## Owner questions

1. inflatable_decoy's modelSize (lead call b, wave 6 question 2): set it to the replica's own size (about
   [7.6, 6.8, 4.0], or drop it as gun_turret has none) so the decoy is drawn 1:1 beside a gun turret? (Data
   unchanged.)
2. rail_supergun (a boss gold member) now 11.9k triangles, scoring higher than the old 36.7k file: fine, and should
   the gold set be recomputed (`quality_gate.py --gold`) after the merge?
