# Prompt 27 experiment 1: the improved kit on four models

Step 3 of DECISIONS "27 order" (decisions: DECISIONS "27 experiment 1"). Date 2026-10-01/02, branch
`feature/p27-experiment`. Four models rebuilt with the improved procedural kit, one variable at a time, checked with
the static GLB validator (`Tools/assets/glb_check.py`) and the existing Unity card renders. **Nothing else ran**: no
EditMode suite, no sims, no benchmark, no FPS / draw-call / memory measure (they wait for the owner).

## Variables and thresholds

| variant | what changes | how to rebuild it |
|---|---|---|
| baseline (V0) | the original builders (the control) | `MB_P27_VARIANT=v0` |
| V1 | new kit primitives (`Tools/blender/mb_kit27.py`) in the builders' own geometry | `MB_P27_VARIANT=v1` |
| V2 | V1 + the shared parts library (`Tools/blender/mb_parts27.py`) for the sub-assemblies | `MB_P27_VARIANT=v2` (default, shipped) |

`blender --background --python Tools/blender/build_assets.py -- main_battle_tank fighter_jet attack_helicopter
silver_bug` builds the four and their `_hd` twins (it also rebuilds elite_attack_helicopter and silver_bug_wreck,
whose builders did not change: restore them with git). The builders are in `Tools/blender/mb_p27_experiment.py`,
merged last in `all_builders()`.

Thresholds, set before the builds from the brief: triangles of the normal file within 2x the baseline; zero-area
triangles 0 (validator error over 0.5 %); mean COLOR_0 brightness at or above the baseline; runtime node names
identical (pivots, muzzles, moving parts, Icarus' Mount_gun.001-.003); size within 1 % of the baseline bounds (the
view fits only the length); no new material on a moving part (the merged template's draw count); card mean
luminance (alpha-weighted Rec. 709 luma of the PNG) not darker than 1 % below the baseline.

## Results

Triangles / vertices / GLB renderers / zero-area / COLOR_0 mean (vertex-weighted, the validator's) / card mean
luminance. Cards render from the `_hd` file (Icarus from `silver_bug`), so the card column is on the `_hd` row.
Moving parts are the same in all three variants (validator: runtime node names identical).

### Main battle tank (main_battle_tank) - moving: Turret, Main_cannon, Muzzle_brake, Mount_mg

| file | variant | tris | verts | renderers | zero-area | COLOR_0 | card lum | validator |
|---|---|---:|---:|---:|---:|---:|---:|---|
| main_battle_tank | V0 | 4,700 | 6,490 | 36 | 0 % | 0.5643 | | pass |
| | V1 | 5,036 (1.07x) | 6,774 | 36 | 0 % | 0.5968 | | pass |
| | V2 | 7,196 (1.53x) | 8,446 | 38 | 0 % | 0.6229 | | pass |
| main_battle_tank_hd | V0 | 12,106 | 18,883 | 55 | 0 % | 0.5073 | 0.3546 | pass |
| | V1 | 12,442 | 19,167 | 55 | 0 % | 0.5214 | 0.3527 | pass |
| | V2 | 16,462 | 21,877 | 56 | 0 % | 0.5504 | 0.3562 | pass |

Size 7.79 x 3.07 x 2.30 m in every variant (V2 2.307 m high: the antenna stubs). LOD1 input (loose pieces) 171 -> 161.

### Su-27 (fighter_jet) - moving: none (Muzzle_aam / _gun / _missile)

| file | variant | tris | verts | renderers | zero-area | COLOR_0 | card lum | validator |
|---|---|---:|---:|---:|---:|---:|---:|---|
| fighter_jet | V0 | 3,580 | 4,524 | 22 | 0 % | 0.7004 | | pass |
| | V1 | 3,644 (1.02x) | 4,570 | 22 | 0 % | 0.7049 | | pass |
| | V2 | 3,948 (1.10x) | 5,032 | 22 | 0 % | 0.7127 | | pass |
| fighter_jet_hd | V0 | 14,528 | 21,806 | 31 | **2.68 % (390)** | 0.6448 | 0.3883 | **error** |
| | V1 | 14,204 | 21,456 | 31 | 0 % | 0.6442 | 0.3883 | pass |
| | V2 | 13,856 | 20,836 | 29 | 0 % | 0.6493 | 0.3880 | pass |

### Icarus (silver_bug; also hyperion and icarus_mk0) - moving: Turret, Mount_gun, Mount_gun.001-.003, Mount_mg(.001)

| file | variant | tris | verts | renderers | zero-area | COLOR_0 | card lum | validator |
|---|---|---:|---:|---:|---:|---:|---:|---|
| silver_bug | V0 | 19,136 | 26,450 | 118 | 0.01 % (2) | 0.7274 | 0.4165 | pass (warnings) |
| | V1 | 20,152 (1.05x) | 28,308 | 118 | 0 % | 0.7327 | 0.4155 | pass (warnings) |
| | V2 | 21,760 (1.14x) | 29,716 | 120 | 0 % | 0.7421 | 0.4158 | pass (warnings) |

Warnings are the baseline's (the `.001` runtime names, which the boss parts need, and hyperion's fitted length).
Size 36.32 x 18.23 x 13.15 m (13.12 before: the bridge antennas). silver_bug_wreck keeps the original builder.

### Attack helicopter (attack_helicopter, the complex unit) - moving: Rotor, Tail_rotor, Mount_gun

| file | variant | tris | verts | renderers | zero-area | COLOR_0 | card lum | validator |
|---|---|---:|---:|---:|---:|---:|---:|---|
| attack_helicopter | V0 | 3,482 | 4,722 | 27 | 0 % | 0.6801 | | pass |
| | V1 | 4,064 (1.17x) | 5,159 | 27 | 0 % | 0.6911 | | pass |
| | V2 | 4,362 (1.25x) | 5,314 | 28 | 0 % | 0.6933 | | pass |
| attack_helicopter_hd | V0 | 5,694 | 8,238 | 34 | 0 % | 0.6271 | 0.3213 | pass |
| | V1 | 6,276 | 8,675 | 34 | 0 % | 0.6387 | 0.3253 | pass |
| | V2 | 6,542 | 8,718 | 36 | 0 % | 0.6492 | 0.3247 | pass |

All 7 files keep their size, materials (8 / 9 / 12 per model) and runtime names. Validator over all 400 files: 13
with errors (14 before; fighter_jet_hd fixed), the other 13 untouched.

### Card pictures (256 px copies; the shipped 512 px cards are in Assets/MachineBrigade/Resources/UI/Cards)

| model | baseline | V1 | V2 (shipped) |
|---|---|---|---|
| MBT | experiment1/main_battle_tank_before.png | experiment1/main_battle_tank_v1.png | experiment1/main_battle_tank_v2.png |
| Su-27 | experiment1/fighter_jet_before.png | experiment1/fighter_jet_v1.png | experiment1/fighter_jet_v2.png |
| Icarus | experiment1/silver_bug_before.png | experiment1/silver_bug_v1.png | experiment1/silver_bug_v2.png |
| Apache | experiment1/attack_helicopter_before.png | experiment1/attack_helicopter_v1.png | experiment1/attack_helicopter_v2.png |

The baseline cards were rendered again in the runner from the committed GLBs: identical to the committed PNGs to four
decimals, so the card stage is deterministic and the comparison fair. next_gen_tank's card (the MBT's model, tinted)
was rendered too; manifest.json only changed the hashes of the cards drawing these four models.

## What each variable changed

**V1 (primitives).**
- MBT: hull plates as chamfered extrusions (two-step chamfer, worn middle row: brighter edges), a raised plate inset on
  the glacis and rear plate, the engine-deck grille sunk into a recess cut by a boolean, the turret as a sharp-edged
  loft (chamfered vertical corners and roof edge) with a raised roof plate, a lathed gun (one surface instead of three
  cylinders), four seeded stowage greebles on the bustle, mirrored fittings. Visible on the card: crisper turret and
  hull edges, the glacis plate, the grille recess. +7 % triangles, COLOR_0 +5.8 %.
- Su-27: the clean-up pass (`k.clean`) takes fighter_jet_hd from 390 zero-area triangles to 0 (bevel T-junctions on
  lofted tips); chamfered blocks and lathes for the small fittings. Panel insets on the lofted spine were tried and
  dropped: +400 triangles, COLOR_0 -0.7 %, nothing visible at card size. No visible change on the card.
- Icarus: raised deck and step plates (insets on every flat top facet), seeded greebles with slatted vents on the steps,
  the flank pods' bay mouths cut as real recesses (boolean), slivers cleaned. Visible: busier, more regular deck
  gear, the recessed bay mouths. +5 % triangles.
- Apache: the flat-panel fuselage and boom as sharp-edged lofts, avionics-bay doors inset, stub wings as extruded
  airfoils, lathed nacelles, chin gun and tyres, three greebles behind the mast. Visible: brighter chines. +17 %.

**V2 (parts library on top).**
- MBT: dished road wheels with rims and hub bosses, toothed sprockets, track belt with a sagging upper run (under the
  skirts), domed hatches with coamings, a one-surface barrel (sleeve clamp, tapered fume extractor, dark bore) with
  an open reference collar, the pintle MG, smoke launchers on brackets, two antenna stubs. Visible: the wheels (the
  biggest gain), hatches, gun. +43 % over V1.
- Su-27: serrated nozzle petals (worn rims; at high detail they replace the old petal seams and actuator rods, two
  parts fewer), plain pylons, shaped wingtip rails, the library canopy with a sill frame and windscreen bow at high
  detail. Not visible at card size; +8 % over V1.
- Icarus: library ion engines (cooling band, deep throat), antennas on the bridge and upper step, flak barrels with
  double-baffle brakes (Steel, so no new material on the Mount_mg parts). Barely visible (the stern faces away from
  the card camera). +8 % over V1.
- Apache: one turned rotor hub, the tail-rotor hub, rocket pods with recessed tube faces, the Hellfire rack, shaped
  nacelles with intake lips, canopy frames at high detail, two antennas on the boom. Visible: canopy frames on the
  card, antennas. +7 % over V1.

## Problems met (fixed in this pass)

1. Blender 4.5's EXACT boolean turned the kit's closed solids inside out (signed volume < 0; the MBT's deck vanished
   on the first card). `k.cut` uses the MANIFOLD solver and only applies a result that is a smaller positive solid.
2. Chamfers are expensive on small parts (a two-step chamfered box: ~90 triangles vs 12): the first V2 MBT was 2.09x
   and the Apache 2.04x. `k.block` now chamfers only the top edges and leaves anything under 12 cm plain.
3. COLOR_0's mean is vertex-weighted, so a recess that ends in a lathe pole (a muzzle bore, a pod face) weighs ~10
   dark vertices; the first V2 jet and Apache fell below the baseline. Recesses were made shallow, the poles dropped
   where they do not show, worn rims added to lips and petal tips. fighter_jet_hd V1 stays 0.1 % under the baseline
   (the removed slivers sat on worn bevel rows); V2 is above it.
4. The first MBT antennas raised the bounds 7 % (2.30 -> 2.47 m); they are short stubs now (2.307 m).

## Risks

- Draw cost: no new moving part and no new material on a moving part, so the merged template's draw count should not
  change (Smoke_brackets, Antennas, Canopy_frames, Flak_brakes merge into existing materials) - not measured yet.
- LOD1: loose pieces fall for the MBT (171 -> 161) but rise for Icarus (522 -> 561, greebles and vents): the
  simplifier keeps them, so its LOD1 may keep more triangles.
- Triangles on phones: the MBT normal file is 1.53x (7,196); the 25B2 tank budget was 3,000-5,000. Fine for the
  hero units, not for every tank of a large battle without the LOD measure.
- The insets and greebles on Icarus read slightly regular; a wave should vary seeds and counts per ship.
- The SSAO double-darkening check (PC) is still unmeasured: COLOR_0 went up, so the risk did not grow.

## Recommendation for checkpoint 1

Adopt **V2** for ground vehicles and large hard-surface models (tanks, trucks, bosses, structures): the MBT is the
clear win (wheels, edges, hatches, gun) at 1.5x triangles with brighter COLOR_0 and the same card luminance. For jets
use only the V1 clean-up (zero-area fixes) and the library nozzle / canopy at high detail: the kit adds nothing visible
on a jet at card size. Helicopters: V2 is a small gain at 1.25x. Measure draw calls, LOD1 sizes and frame time on one
battle before a wave goes wide.

Draft wave recipe (one model per commit, sonnet on this recipe after approval):
1. Record the model's baseline row (`glb_check.py --only <name>`) and card luminance.
2. Copy the winning builder into the wave's module, merged last; keep every name, pivot, material, `_hd` branch.
3. Swap helpers for `mb_parts27` parts where the model has them (running gear, hatches, barrels, MG, smoke, antennas,
   rotors, nozzles, pylons, racks, canopy frames at high detail only).
4. Large plates: `k.extrude` / `k.block` (top chamfer), chined hulls `k.sharp_loft`; `k.inset` raised plates on big flat
   faces only (not lofted skins); `k.cut` at most one recess per closed solid; 3-6 seeded greebles per surface.
5. No deep recess poles; nothing thinner than 10 cm at normal detail; keep the bounds (short antennas).
6. End the builder with `k.clean(a)`; rebuild normal and `_hd`.
7. Gates: tris <= 1.6x (hard 2x), zero-area 0, COLOR_0 >= baseline, size within 1 %, runtime names identical, no new
   material on a moving part, card luminance within -1 %.
8. Render the card, `glb_check.py --accept <names> --reason ...`, commit.
