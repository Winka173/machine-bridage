# Prompt 27 Step 0 audit (short: what the 4-model experiment needs)

Date: 2026-10-01. Scope: DECISIONS "27 scope (v2)" and "27 order" step 1 (they override the prompt where they
differ). Static reading of the repository plus the GLB baseline (Docs/models/BASELINE.md); nothing was run in Unity,
nothing measured. The full prompt audit (sections 3.1-3.7 in depth, FPS, memory) waits for the owner's word on
measuring.

## 1. Where models are built

- `Tools/blender/build_assets.py`: headless Blender (`blender --background --python Tools/blender/build_assets.py
  -- <filter>`) builds every model into `Assets/MachineBrigade/Resources/Models/<name>.glb` and records triangle counts
  in `Docs/art/models.json`. The exporter is Blender I/O 4.5.51 (the GLBs' generator string).
- `all_builders()` merges ~45 modules' `BUILDERS` dicts; **the last dict that names a model wins** (later prompts
  override earlier ones). `HIGH_DETAIL` (12 names) adds `<name>_hd` = the same builder with `detail=True`
  (`Tools/blender/mb_detail.py` adds the extra detail); round 6 and p25_models2 own variants override the generic one.
- The kit is `Tools/blender/frontier_kit.py` (719 lines):
  - `Shape` primitives: `box`, `limb`, `cyl`, `prism` (profile extrusion), `shell`, `loft`, `mesh`, `lathe`,
    `sphere`, `ico`, `tier`, `torus`, `tube` (sweep along points), `grille`, `bolts`; helpers `mirror_x`,
    `chamfered`, `arc`. Several of the "improved kit" primitives already exist in a basic form (lathe, loft, tube,
    prism): the experiment improves them rather than adding duplicates.
  - `Asset`: `pivot()` (empties: Turret, Mount_*, Rotor ...), `part(name, mat, parent)` (one Shape per
    name/material/parent), `finish()` (smoothing by a 50 degree sharp angle, duplicate-runtime-name guard,
    `_shade` = baked AO / grime / wear into `COLOR_0`, box UVs, weighted normals), `export()`.
  - Regexes `RIG`, `MOVING`, `RUNTIME` mirror the C# names; `MATERIALS` / `GLOWING` the flat material set.
- No textures: flat PBR factors per material + `COLOR_0` (baked light, AO, wear, grime). One material per part.

## 2. How GLBs reach Unity

- Import: glTFast (`com.unity.cloud.gltfast` 6.20.0), files under `Resources/Models`, loaded by
  `ModelLibrary` (`Resources.Load<GameObject>("Models/" + id)`, ModelLibrary.cs:1284).
- `ModelLibrary.HighDetail` (static, ModelLibrary.cs:311) swaps in `<id>_hd` (`HighDetailSuffix`, :284) when the file
  exists; the high graphics tiers set it; card renders use the `_hd` files.
- `ModelLibrary.Template()` (:533) merges every rigid mesh into one per part that moves on its own (hull, turret,
  each recoiling barrel, mount, rotor, propeller), built once per model: **GLB renderers / material slots are not
  the runtime draw count**; the budget work must count both (GLB: authoring cost; template: draw calls).
- Runtime names (ModelLibrary.cs:134-169): `TurretPattern ^Turret(\.\d+)?$`, `RecoilPattern ^(main_cannon|
  muzzle_brake)`, `MuzzlePattern ^Muzzle_(main|coax|mg|missile|rocket|gun|aam|door_l|door_r|ramp|agl_l|agl_r|mortar)`,
  `MountPattern ^Mount_([a-z]+)`, spinners `Rotor`, `Tail_rotor`, `Radar`, `Propeller`, `LoosePattern`,
  `PartPattern ^Part_`, `DeployPattern ^Deploy_`; `VehicleView` uses `Muzzle_brake`, `Main_cannon_tube`; boss parts
  name nodes in balance.json (`"node": "Main_cannon|Muzzle_brake"`, `*` = prefix; VehicleView.BossParts.cs:67).
- LOD: `VehicleLod.Choose` by on-screen pixels (DetailPixels 128, ImpostorPixels 24, Band 0.12 hysteresis);
  LOD1 = `MeshSimplifier.Simplify` (quadric edge collapse on welded positions, surface groups kept) per moving part,
  cached per model (ModelLibrary.Lod.cs:245); drawn with one `MaterialLibrary.LodSurface(team)` material (palette
  column per kit surface in UV); LOD2 = `ImpostorAtlas` cells (16 headings). No Unity LODGroup.
- Materials: `MachineBrigade/Lit` shared materials from `MaterialLibrary`; team/variant tints are shared copies from
  `MaterialLibrary.Tinted(source, tint)` (MaterialLibrary.cs:310).
- Visual paths to reuse: `CardRenders` (Editor, its private `Stage` class, CardRenders.cs:297) and `UnitPreview`
  (Game/Rendering/UnitPreview.cs). Tower rank details: `TowerRankDetails` in Game/Rendering/TowerArt.cs (kept).
- The runtime fits each def's model **length** to balance.json `modelSize` (VehicleView.DrawScaleOf): width and
  height follow the model's proportions, so a rebuilt model must keep length:width:height close to `modelSize`.

## 3. Repository facts from "27 scope (v2)" (each verified with one grep, 2026-10-01)

| fact | evidence | status |
|---|---|---|
| No MaterialPropertyBlock on MachineBrigade/Lit; tints via `MaterialLibrary.Tinted` | `Tinted(Material source, Vector4 tint)` MaterialLibrary.cs:310; property blocks only in ShieldVisual, GroundMark, ImpostorAtlas (not Lit hulls) | holds |
| GPU Resident Drawer ON for PC, off for mobile | PC_RPAsset.asset:85 `m_GPUResidentDrawerMode: 1`; Mobile_RPAsset.asset:85 `0` | holds (record, do not change) |
| SSAO active on PC on top of baked AO | PC_Renderer.asset: `ScreenSpaceAmbientOcclusion`, `m_Active: 1` | holds: double darkening check applies to PC |
| LOD by screen size, MeshSimplifier per moving part, LodSurface, ImpostorAtlas, no LODGroup | VehicleLod.cs:24/27/30/85; no `LODGroup` in Scripts | holds |
| 12 `_hd` GLBs, loaded when `ModelLibrary.HighDetail` | build_assets.py:75 `HIGH_DETAIL`; 12 `*_hd.glb` in Resources/Models | holds |
| Card stage + UnitPreview are the render paths | CardRenders.cs:297 `class Stage`; UnitPreview.cs:15 | holds |
| Structures, towers, bosses share the pipeline; `TowerRankDetails` kept | TowerArt.cs | holds |

## 4. The 4 experiment models

| label | GLB (Resources/Models) | builder that wins | tris | verts | renderers | materials | size L x W x H (m) | modelSize |
|---|---|---|---:|---:|---:|---:|---|---|
| MBT | main_battle_tank.glb | mb_p25_models.py:97 `main_battle_tank` | 4,700 | 6,490 | 36 | 8 | 7.79 x 3.07 x 2.30 | 7.79 x 3.07 x 2.3 |
| MBT HD | main_battle_tank_hd.glb | same, detail=True | 12,106 | 18,883 | 55 | 9 | 7.79 x 3.07 x 2.35 | |
| Su-27 | fighter_jet.glb | mb_p25_models.py:223 `fighter_jet` | 3,580 | 4,524 | 22 | 9 | 8.64 x 5.85 x 2.15 | 8.64 x 5.85 x 2.15 |
| Su-27 HD | fighter_jet_hd.glb | same, detail=True | 14,528 | 21,806 | 31 | 9 | 8.64 x 5.85 x 2.15 | |
| Icarus | silver_bug.glb (+ silver_bug_wreck.glb) | mb_pt9_models.py:580 `silver_bug` | 19,136 | 26,450 | 118 | 12 | 36.32 x 18.23 x 13.12 | (boss "size") |
| complex unit | attack_helicopter.glb | mb_p25_models.py:514 `attack_helicopter` | 3,482 | 4,722 | 27 | 9 | 6.35 x 4.44 x 2.02 | 6.35 x 4.44 x 2.02 |
| complex HD | attack_helicopter_hd.glb | same, detail=True | 5,694 | 8,238 | 34 | 9 | 6.35 x 4.44 x 2.02 | |

Triangle counts match `Docs/art/models.json` (4,700 / 3,580 / 19,136). All have COLOR_0, normals and UVs on every
primitive, no NaN, no textures, one extension (`KHR_materials_emissive_strength`).

**Complex unit: attack_helicopter (AH-64 class).** Chosen because it covers the contracts the other three do not:
two spinners (`Rotor`, `Tail_rotor`, which the merge and LOD1 must keep as separate moving parts), a chin gun on
`Mount_gun`, four muzzle kinds (`Muzzle_aam`, `Muzzle_gun`, `Muzzle_missile`, `Muzzle_rocket`), an `_hd` twin
(check_hd.py's rotor-blur bounds rule), a low-flying unit seen closer than jets, and it is already in the
MuzzleShots set. A tracked tank (MBT), a fast jet (Su-27) and a boss (Icarus) are the other three; a wheeled or
deployable unit would repeat the MBT's turret contract.

Runtime nodes now (analyzer): MBT `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main/coax/mg`, `Mount_mg`;
Su-27 `Muzzle_aam/gun/missile`; Icarus `Turret`, `Main_cannon*`, `Mount_gun` + `Mount_gun.001-.003`,
`Mount_mg(.001)` (boss mounts, `mountWeapons` 0-6) and parts' nodes; Apache as listed above.

## 5. Risks for the experiment

1. **Builder precedence.** A new builder only takes effect if its module's `BUILDERS` comes last in
   `all_builders()` (or the winning function is edited in place). Put experiment builders in one new module merged
   last, so reverting is one line.
2. **Naming contract.** Keep every pivot and runtime part name, parent and position (check_hd.py rules, the boss
   parts' `node` patterns in balance.json, `mountWeapons` slots). The validator compares the `_hd` runtime nodes with
   the normal model's and checks boss part nodes; run it after each build.
3. **Proportions.** The view fits length only; keep width/length and height/length within the validator's 25 %
   (better within 4 %, the 25B2 tolerance). Icarus is shared by variants (hyperion at 67.2 m, icarus_mk0).
4. **Draw cost is the merged template, not the GLB.** More separate parts in Blender are cheap only if they are rigid
   (merged); every new moving part or material adds a draw per LOD0 instance and a shadow draw.
5. **COLOR_0 and SSAO.** AO is baked into COLOR_0 and PC adds SSAO; `_hd` files are already darker (mean luminance
   MBT 0.51 vs 0.56, Su-27 0.64 vs 0.70). Cards render from `_hd`, and card mean luminance is the regression signal:
   compare before/after on the same tier.
6. **Degenerate triangles.** fighter_jet_hd has 390 zero-area triangles (2.7 %), sky_gunship_hd 5.4 %: the detail
   kit leaves slivers. The improved kit must not add more (validator error above 0.5 %).
7. **LOD1 behaviour.** MeshSimplifier keeps surface boundaries and open edges; many small separate pieces
   (MBT 171 loose pieces, Icarus 522) limit how far LOD1 can drop. Greebles should be few, large-ish, or rigid
   with the hull.
8. **No property blocks** in any preview or experiment variation (PT11): use `MaterialLibrary.Tinted`.
9. **Runs.** Rebuilding needs Blender 4.5 headless; the card renders are allowed; EditMode tests, FPS, draw-call and
   memory measures wait for the owner.
