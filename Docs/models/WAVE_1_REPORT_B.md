# Prompt 35 wave 1 report, lane B (vehicles, 2026-10-03)

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
