# Prompt 35 wave 6 report (lane B)

Wave 6 of prompt 35 (sections 7 and 8; plan: Docs/models/WAVES_P35.md): its twenty models plus the inflatable decoy
the lead asked for (wave 3 call 2), all done by lane B on branch `feature/p35-w6` (from lead/integration with wave 3
merged). Each model has its own new Blender script (`Tools/blender/mb_p35_<id>.py`; inflatable_decoy's own wave 3
script rewritten) and a build spec written first (`Tools/blender/specs/<id>.json`); the builders are registered last
in `build_assets.py`. Decisions: Docs/DECISIONS.md "Prompt 35 wave 6 (lane B)". Blender and Python only: no Unity run,
no test, sim or measure.

Gate: `Tools/assets/quality_gate.py` (hard gates + the 0-100 soft score against the gold of the class or boss frame;
Tốt >= 80). Ships have no gold of their own and borrow the whole boss gold; bosses are scored against their frame's
gold (sea: hydra_sub, nyx, kraken; air: garuda).

## Rows

"Before" = the committed GLB at the start of the wave. Every row passes every hard gate (triangle floor, parts and
roles, mounts / muzzles / Mount_APS / Mount_Flare / boss part nodes, size, own geometry, zero-area, COLOR_0, colour
zones, AO / dust / wear, not a single block), the spec check (`validate_specs.py --glb <id>`) and glb_check (accepted,
0 errors). Size = L x W x H in metres as built (target: modelSize, else the old file). "Shared" = triangles also found
in another model family (limit 30 %).

| model | class (gold) | real reference | triangles before -> after | size | soft before -> after | rounds | status | shared |
|---|---|---|---|---|---|---|---|---|
| `next_gen_tank` | tracked | T-14 Armata | 6,620 -> 11,642 | 7.88 x 3.21 x 2.34 | 88.7 -> 100 | 2 | Tốt | 15 % -> 7.5 % |
| `airborne_light_tank` | tracked | M8 AGS / M10 Booker | 5,550 -> 10,510 | 6.49 x 2.58 x 2.01 | 94.6 -> 97.4 | 2 | Tốt | 12 % -> 11.4 % |
| `airborne_vehicle` | tracked | BMD-4M (Bakhcha-U) | 3,260 -> 9,464 | 5.32 x 2.50 x 2.19 | 77.7 -> 100 | 1 | Tốt | 13 % -> 4.0 % |
| `bridging_vehicle` | tracked | MTU-72 / M60 AVLB | 5,148 -> 9,652 | 6.58 x 3.00 x 2.01 | 73.6 -> 100 | 3 | Tốt | 8 % -> 7.0 % |
| `shield_carrier` | wheeled | Boxer 8x8 + field emitter | 2,476 -> 7,436 | 6.41 x 2.64 x 2.83 | 44.0 -> 87.8 | 3 | Tốt | 3 % -> 11.2 % |
| `dazzler_vehicle` | wheeled | Peresvet on an MZKT 8x8 | 4,640 -> 7,134 | 9.18 x 2.82 x 3.88 | 58.2 -> 86.4 | 2 | Tốt | 67 % -> 11.7 % |
| `drone_hijack_vehicle` | wheeled | Krasukha / Repellent on a BAZ 8x8 | 3,446 -> 6,754 | 9.28 x 2.72 x 3.94 | 59.6 -> 85.4 | 1 | Tốt | 44 % -> 7.0 % |
| `fibre_fpv_carrier` | wheeled | armoured 4x4 pickup + FPV rack | 1,324 -> 6,364 | 4.88 x 1.99 x 2.08 | 55.3 -> 97.7 | 2 | Tốt | 16 % -> 13.0 % |
| `hover_gunboat` | ground (tracked) | air-cushion gunboat, AK-630 | 2,202 -> 4,648 | 13.70 x 3.90 x 3.53 | 69.9 -> 100 | 2 | Tốt | 0 % -> 3.4 % |
| `landing_craft` | ship (boss) | LCM-8 / LCU | 498 -> 8,592 | 16.70 x 7.49 x 4.90 | 24.0 -> 81.1 | 3 | Tốt | 16 % -> 3.2 % |
| `missile_boat` | ship (boss) | 14 m planing FAC, S-8 | 630 -> 5,752 | 14.36 x 4.05 x 4.42 | 41.6 -> 84.3 | 3 | Tốt | 16 % -> 10.0 % |
| `sea_corvette` | ship (boss) | Buyan-M / Steregushchiy, 76/62, AK-630 | 1,884 -> 7,638 | 30.00 x 6.17 x 12.29 | 47.0 -> 89.5 | 2 | Tốt | 4 % -> 4.0 % |
| `sea_cruiser` | ship (boss) | Kirov / Iowa with missiles, Mk 71 | 5,416 -> 14,150 | 64.00 x 12.15 x 20.60 | 54.4 -> 83.2 | 4 | Tốt | 3 % -> 2.7 % |
| `interceptor_jet` | jet | MiG-31BM | 1,500 -> 3,436 | 8.88 x 5.42 x 2.60 | 77.0 -> 100 | 2 | Tốt | 8 % -> 0.6 % |
| `glide_bomber` | jet | Su-34 + UMPK glide bombs | 1,624 -> 3,184 | 9.40 x 6.04 x 2.34 | 78.1 -> 100 | 2 | Tốt | 7 % -> 1.8 % |
| `stealth_naval_strike` | jet | A-12 Avenger II | 2,124 -> 3,662 | 8.39 x 20.20 x 1.46 | 50.3 -> 67.5 | 4 | NEEDS_HUMAN | 60 % -> 0.5 % |
| `hydra_sub` | boss (sea) | small SSGN, Yasen / Oscar line | 7,548 -> 7,912 | 34.45 x 7.18 x 7.93 | 61.1 -> 81.8 | 2 | Tốt | 7 % -> 1.9 % |
| `nyx` | boss (sea) | Zumwalt + railgun | 3,526 -> 7,602 | 52.95 x 8.95 x 11.47 | 42.6 -> 81.6 | 3 | Tốt | 2 % -> 7.2 % |
| `kraken` | boss (sea) | Kuznetsov / Nimitz carrier | 10,796 -> 12,638 | 110.15 x 20.09 x 23.40 | 54.0 -> 86.4 | 2 | Tốt | 10 % -> 8.5 % |
| `garuda` | boss (air) | B-2 / B-21 flying wing | 2,840 -> 8,022 | 27.80 x 70.00 x 4.19 | 39.1 -> 67.2 | 4 | NEEDS_HUMAN | 1 % -> 0.9 % |
| `inflatable_decoy` | tower | inflatable replica of gun_turret | 3,088 -> 2,580 | 7.81 x 6.74 x 3.96 | 59.8 -> 57.6 | 2 | owner's look | 6 % -> 6.5 % |

Before, 20 of the 21 failed the gate (Kém, Cần sửa or a hard fail: the ship and boss triangle floors, missing roles
such as mantlet / idler / smoke / stowage / axles / glass / boats / exhaust / pylons, missing `Mount_APS` on four APS
units, the free secondaries' missing mounts on interceptor_jet and fibre_fpv_carrier, sizes 13-27 % off, 44-67 %
shared geometry, broken COLOR_0 bakes). After: every hard gate passes; 18 Tốt, 2 NEEDS_HUMAN (the two flying wings),
the decoy on the owner's look (structures, lead call 1).

What each one is (details in its spec and builder docstring):

- **Tanks**: next_gen_tank a T-14 (flat long hull, seven wheels, ERA skirts, slat cage, the unmanned faceted turret
  set back, Afghanit radar panels and tubes, the raised 12.7 mm RWS); airborne_light_tank an M8 AGS / M10 Booker
  (bolt-on armour modules, pepper-pot brake, bustle autoloader, the commander's M2 on the cupola);
  airborne_vehicle a BMD-4M (boat hull, trim vane, bow MGs, Bakhcha-U with the 100 mm and coaxial 30 mm);
  bridging_vehicle a turretless T-72 hull with the folded two-span scissor bridge on its boom and rams, the bridge set
  behind the commander's 12.7 mm so it can turn.
- **Wheeled**: shield_carrier a Boxer 8x8 with the finned field emitter, prongs, reflector dish and the glowing Team
  ring and core; dazzler_vehicle a Peresvet-class lens housing (six glowing lenses) on a scissor lift over an
  MZKT-type 8x8 shelter; drone_hijack_vehicle a BAZ-type 8x8 with the sloped-ended body, the tilted phased panel with
  yagis and feed horn on its mast and the spinning cab-roof dish; fibre_fpv_carrier an armoured pickup with the
  four-drone launch rack, two fibre spools and the mini-swarm box on the cab roof (its free secondary). All under the
  7,500 cap of light units seen in numbers.
- **Craft and ships** (ship rules: flared bow, waterline band, multi-tier superstructure, mast and radar, CIWS, boat,
  detailed deck): hover_gunboat a teardrop air-cushion hull with fingered skirt, AK-630 and two ducted fans
  (`Propeller` / `_2` still spin); landing_craft an LCM-8 / LCU (raised bow ramp, well deck, wing walls, two-tier
  wheelhouse, tyre fenders, the M2 on the roof, a pintle M134 in a sponson tub, a Zodiac); missile_boat a deep-vee FAC
  (two S-8 pods on the trainable launcher, reload pods, the M2 behind its shield, a pintle minigun, life-raft
  canisters); sea_corvette a 30 m corvette (76 mm stealth house, 8-cell VLS, three-tier superstructure, pyramid
  mast with the spinning radar and APS faces, funnel, quad canisters, hangar with the AK-630 on its roof, RHIB in
  davits); sea_cruiser a Kirov / Iowa-line cruiser (two twin 203 mm turrets, two VLS fields, four-tier superstructure,
  pyramid mast, lattice aft mast, twin funnel, two CIWS sponsons, canisters, two RHIBs and a crane, flight deck).
- **Jets**: interceptor_jet a MiG-31BM (big side intakes, tandem canopy, twin canted fins, ventral fins, four R-37M
  under the belly, the Kh-31P on its own `Mount_aam`); glide_bomber an Su-34 (platypus nose, side-by-side canopy,
  canards, the tail stinger, two FAB-500 + UMPK on heavy pylons, R-73 on the tips, two flare rows a side);
  stealth_naval_strike an A-12 Avenger II (the triangular flying wing, intakes under the leading edge, flat exhaust
  troughs, bays with the bomb load, four standoff missiles, RAM edges and seam tape as paint).
- **Bosses** (drawn 1.3-1.5 x of the real type's features for the read; the weak points the BossText tips name are
  riveted plates one shade off on their own nodes): hydra_sub a small surfaced SSGN (sail with the SAM box, the deck
  gun, ten launch tubes under the toned hatch rows, the drone deck with six FPV, the pump-jet and cruciform planes);
  nyx a Zumwalt (tumblehome hull, wave-piercing bow, pyramid deckhouse with flush radar faces, the railgun turret with
  its glowing capacitor bank, peripheral VLS banks, two CIWS, the helicopter deck, the stern boat bay); kraken a
  carrier (ski-jump, angled deck lines, lifts and sponsons, the island with the mast radar and funnel, flush missile
  cells, VLS, SAM boxes, two CIWS and two four-mount galleries, the landing area with wires and parked jets, the boat
  bay); garuda a B-2 / B-21 wing (double-W sawtooth trailing edge, four engine humps with serrated intakes, bomb and
  drone bays, nose radar panel, twin dorsal turrets, the 105 mm pods, tail barbettes). Every old `Part_*`, `Mount_*`,
  `Muzzle_*` and `Radar` of the four bosses is kept at its old place (the def parts' `at` are tuned onto them).
- **inflatable_decoy** (lead call 2): now an inflatable replica of the wave 2 gun turret on its own dimensions (the
  battered casemate, the turret plan, mantlet, barrel, bustle, printed fittings) with the giveaways (seams, patches,
  tethers, blower, bag); the turret stands traversed 38 degrees so the replica keeps the def's modelSize proportions
  (owner question 2).

## NEEDS_HUMAN

- **stealth_naval_strike 67.5, garuda 67.2** (four rounds each, every hard gate passes). Both are flying wings: a
  triangle (A-12) and a sawtooth wing (B-2 / B-21) stay near-convex from the side, front and top (silhouette 1.07 and
  1.16 against the jet gold 1.42 and the air boss gold 1.76), their top outlines are symmetric (the asymmetry share
  stays at half), and the smooth radar-absorbent skin holds few brightness regions at the battle camera even with the
  seam tape, edge bands and panel patchwork painted on (the jet rule forbids insets and greebles). The old files
  scored 50.3 and 39.1; the owner's look decides.

## Pictures

Before / after sheets (Blender Workbench, material colours: front, rear, side, top, 3/4 front, 3/4 rear, the battle
angle at the default zoom's 28.4 px per metre, x2): `Docs/models/rebuild/<id>/before_after.png` for the 21 ids.

**For the lead to render in Unity (cards and ModelScan).** Cards (CardRenders) for the seventeen ids with a card:
next_gen_tank, airborne_light_tank, airborne_vehicle, bridging_vehicle, shield_carrier, dazzler_vehicle,
drone_hijack_vehicle, fibre_fpv_carrier, hover_gunboat, interceptor_jet, glide_bomber, stealth_naval_strike,
hydra_sub, nyx, kraken, garuda, inflatable_decoy. **No card: landing_craft, missile_boat, sea_corvette, sea_cruiser**
(balance.json `card: false`). ModelScan:

```
MachineBrigade.Editor.ModelScan.RenderBatch -mbScan "next_gen_tank,airborne_light_tank,airborne_vehicle,bridging_vehicle,shield_carrier,dazzler_vehicle,drone_hijack_vehicle,fibre_fpv_carrier,hover_gunboat,landing_craft,missile_boat,sea_corvette,sea_cruiser,interceptor_jet,glide_bomber,stealth_naval_strike,hydra_sub,nyx,kraken,garuda,inflatable_decoy"
```

Points to look at in Unity: the ships sinking whole and the bosses' parts breaking off their `Part_*` nodes; Kraken's
and the cruiser's radars spinning; the hover gunboat's fans; sea_cruiser's twin 203 mm muzzles (now 10.4 m ahead of the
mounts instead of 12.4 m, at the new barrels' ends; the wrapper still adds one muzzle a barrel); hydra_sub's twinned
deck gun (the wrapper copies its barrel as before); garuda's dorsal turrets firing from both barrels
(`Muzzle_b1_gun` / `_b2_gun` and `_gun_001`, new: the def's eight mounts want eight muzzles); interceptor_jet's
anti-radar missile from its own `Mount_aam` on the right pylon and fibre_fpv_carrier's mini-swarm box from its
`Mount_rocket` (both new, the defs' free secondaries); the bridging vehicle's commander gun turning in front of the
bridge; the inflatable decoy beside a gun turret (drawn at 0.66 x until owner question 2 is answered).

## Roof guns

Every roof gun of the wave stands on `mb_p35b_parts.raised_gun` or its own mount: next_gen_tank (the 12.7 mm RWS on a
raised ring), airborne_light_tank (the commander's M2 on a post over the cupola), bridging_vehicle (the 12.7 mm on the
cupola: its main weapon), shield_carrier and dazzler_vehicle (12.7 mm RWS on raised rings: their main weapons);
landing_craft and missile_boat carry their M2 on a ring with a shield.

## The whole gate after the wave (no old model broken)

`python Tools/assets/quality_gate.py --no-write` over all 230 scored models: 77 pass the whole gate (59 after wave 3).
Compared with the lead's quality_report.csv no model outside waves 3 and 6 changed its hard result or its soft score
by more than 0.5 (the wave 3 rows differ because the csv predates its merge), and no other model's own-geometry check
names a wave 6 model. glb_check: 0 errors, `--compare` clean after the accepts; warnings only (renderer and triangle
budgets: the owner's rule keeps over-budget models). quality_report.xlsx / .csv are not rewritten on this branch.

## Kit requests (for lane A, mb_kit35.py)

The wave 3 requests stand (`track_run`, `sandbag_run(part=, lean=)`, `camo_net`, `earth_pad(bottom=False)`,
`door(frame_mat=)`); this wave added four generic helpers to lane B's `mb_p35b_parts.py`, worth a kit home:

1. `clutter(a, name, mat, x0, x1, y0, y1, z, n, seed, ...)`: n non-overlapping boxes of varied size on a deck (lockers,
   hose boxes, fittings): what the ship and boss densities need, 12 triangles each.
2. `plane(part, x0, x1, y0, y1, z)`: a one-sided deck plate (half a box's area, which the densities divide by).
3. `portholes(a, points, normal, r=, seg=)`.
4. `merge_parts(a, mapping)`: folds static parts into fewer meshes before the finish (glb_check's renderer caps on
   ships and jets).

## Owner questions

1. stealth_naval_strike 67.5 and garuda 67.2 (flying wings, see NEEDS_HUMAN): accepted on the look?
2. inflatable_decoy: the def's modelSize 5.0 x 4.6 x 2.6 cannot hold a replica of the gun turret with its gun straight
   ahead (8.97 x 5.25 x 4.0 m), and the runtime fits the model's length to modelSize, so the decoy is drawn at
   5.0 / 7.6 = 0.66 x the real tower even with the turret traversed. Set its modelSize to its own size (about
   [7.6, 6.8, 4.0], or drop it as gun_turret has none) for a 1:1 copy? (Data: not changed here.)
3. The ship rules ask for a CIWS and a boat on every ship: landing_craft and missile_boat carry the pintle M134 /
   minigun small craft really carry (the close-in Gatling) and a Zodiac / life-raft canisters. Fine?
