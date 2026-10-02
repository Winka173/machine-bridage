<!--
Owner's revised prompt 27, given 2026-10-01 (in English), verbatim below. It REPLACES prompt27_vi.txt (kept for history).
Read the lead's notes in Docs/DECISIONS.md section "27 scope (v2)" before starting: they record repository facts this
prompt does not know (property blocks, the GPU Resident Drawer, the runtime LOD's screen-size rule, the owner's
no-test rule) and where the original prompt's dropped parts went.
-->

# Prompt 27 — Upgrade Machine Brigade Asset Pipeline for Mobile + Lightweight PC

## Objective

Upgrade the existing Machine Brigade asset pipeline without a large rewrite.

The game currently targets mobile and will later expand to PC.

The PC version is intended to remain a lightweight RTS game, so **1080p is the primary PC visual and performance target**. Do NOT design the asset pipeline around 4K.

The goal is to make the current procedural Blender → GLB → Unity pipeline more robust, measurable, scalable, and suitable for both mobile and lightweight PC while preserving the existing working architecture.

The guiding principle is:

> One high-quality source asset → multiple platform/quality runtime tiers.

Do not create separate mobile/PC assets unless benchmarking proves that a separate asset is actually necessary.

---

# 0. IMPORTANT: Understand the Existing Pipeline First

Before changing code, inspect the repository and document the actual current pipeline.

There are currently approximately 361 `.glb` assets generated through Blender Python.

The assets are generated procedurally and are NOT hand-modeled.

There are approximately 51 Blender scripts under:

`Tools/blender/`

Example:

`Tools/blender/mb_p25_models.py`

The models are assembled from the shared procedural Blender kit:

`frontier_kit.py`

The current kit provides procedural primitives such as:

* boxes
* cylinders
* spheres
* loft/cross-section extrusion
* bevels
* weighted normals

The existing visual philosophy is intended for an RTS/gameplay camera:

* readable silhouettes
* hard-surface forms
* simplified geometry
* controlled bevels
* gameplay readability over microscopic realism

## Current material approach

Materials are primarily surface descriptions.

There are approximately 50 material categories, including examples such as:

* Team
* Armor
* Steel
* Undercarriage
* Rubber
* Glass
* Lamp
* Concrete
* Sandbag
* etc.

There are currently no texture maps as part of the core asset workflow.

Do NOT introduce a texture atlas / UV / texture baking pipeline in this prompt.

## Current vertex-color workflow

Lighting/AO/wear/grime information is baked into `COLOR_0`.

This currently includes concepts such as:

* ambient occlusion
* contact darkening
* edge/wear information
* dirt near ground
* subtle mottling

Base vertex color is generally gray so that the game can apply faction/team tint at runtime.

Do not replace this system unless an experiment proves that it is necessary.

## Current Unity rendering

Unity contains:

`MaterialLibrary`

which maps material names to game materials.

The main shader is:

`MachineBrigade/Lit`

The approximate rendering concept is:

`Material Color × Vertex Color × Runtime Tint × URP Lighting`

The Team material/tint system is an important gameplay contract.

Do not casually replace this material architecture.

## Naming is a gameplay contract

Existing names such as:

* `Turret`
* `Main_cannon`
* `Muzzle_*`
* `Mount_*`
* `Rotor`

are consumed by gameplay/runtime code.

Examples include:

* turret rotation
* cannon recoil
* firing effects
* rotor animation

Do NOT rename these nodes casually.

Before changing any naming convention, search the repository for consumers.

## Current export pipeline

Blender runs headless/batch Python scripts and exports `.glb` assets into Unity.

Preserve this basic pipeline.

## Current LOD / impostor system

The project currently uses:

* runtime `MeshSimplifier`
* runtime LOD
* far-distance 2D impostors
* approximately 12 `_hd` versions for higher-quality rendering

Do not immediately replace this architecture.

First inspect how it actually works.

## Current rendering/preview tools

There are existing tools such as:

`model_shots.py`

for top-down/shadow/gameplay-style renders.

There is also:

`preview_assets.py`

for asset comparison boards.

Unity contains:

`CardRenders`

for card image rendering.

---

# 1. HARD CONSTRAINTS

These constraints apply throughout the task.

## Keep

Keep the following unless a benchmark proves they are technically insufficient:

* Blender Python procedural generation
* `frontier_kit.py`
* GLB export
* Unity import pipeline
* `MaterialLibrary`
* `MachineBrigade/Lit`
* `COLOR_0`
* Team/faction tint
* gameplay node naming contracts
* existing tower-detail code
* runtime LOD
* impostor system
* existing gameplay integration

## Do NOT introduce in this prompt

Do NOT introduce:

* texture atlas
* UV overhaul
* texture baking pipeline
* PBR texture workflow
* mass material renaming
* manual Blender modeling workflow
* mass baked LOD generation
* `_mobile.glb` for every asset
* `_pc.glb` for every asset
* `_hd` versions for every asset
* AI scoring of all 361 assets
* large rewrite of the asset pipeline
* migration of working Unity tower-detail logic into Blender
* PC-only rendering technology without measurement

These may become separate experiments later if evidence shows they are necessary.

---

# 2. TARGET PLATFORM

Define platform/quality tiers around actual project needs.

Primary target:

### Mobile Low

* approximately 720p gameplay target
* aggressive performance budget

### Mobile High

* approximately 1080p gameplay target
* higher visual quality while remaining mobile-safe

### PC

* **1080p primary target**
* lightweight RTS
* higher unit counts and stronger hardware than mobile

Do NOT use 4K as an art-quality requirement.

4K may be tested later if the game eventually needs it, but it is explicitly NOT a target for this asset-pipeline upgrade.

Do not define "PC" as a specific GPU yet.

If benchmarking hardware is required, document concrete test hardware separately.

---

# 3. STEP 0 — AUDIT THE EXISTING SYSTEM

Before modifying production code, inspect the current implementation.

Produce a short report covering:

## 3.1 LOD

Determine:

* How LOD is selected.
* Whether it is based on distance, screen size, or another metric.
* Whether Unity `LODGroup` is used.
* Whether runtime `MeshSimplifier` is applied dynamically.
* How expensive runtime simplification is.
* Whether simplification happens once and caches the result.
* Whether LOD switching causes visible popping.
* Whether vertex colors survive simplification.
* Whether material slots/submeshes are merged.
* Whether gameplay node contracts survive.

Because this is an RTS with an orthographic-style gameplay camera, prefer **screen-space / visible-on-screen size** as the conceptual basis for LOD.

Do not blindly replace the current system.

Unity's LOD system uses screen-relative transition thresholds, so determine whether the current implementation can use the same principle or an equivalent.

---

# 3.2 Impostors

Inspect:

* impostor resolution
* number of angles
* atlas size
* memory usage
* generation time
* transition distance/screen size
* whether mobile and PC need different impostor settings

Determine whether the current impostor is already sufficient.

Do not redesign it without measurements.

---

# 3.3 MeshSimplifier

Inspect:

* vertex count changes
* triangle count changes
* submesh/material behavior
* vertex color preservation
* normals/tangents
* bounds
* node hierarchy
* moving-part compatibility
* collider compatibility if applicable

Pay particular attention to assets containing:

* turret
* cannon
* rotor
* wheels
* animated/moving parts

A simplification process must not silently break gameplay contracts.

---

# 3.4 Materials / Rendering

Inspect actual runtime data:

* renderer count
* material slots
* submesh count
* material count
* draw-call implications
* batching behavior
* SRP Batcher compatibility
* GPU instancing compatibility
* shader variants
* shadow caster complexity

Do NOT assume:

"SRP Batcher is disabled on GLES."

Inspect the actual Unity version/platform/project configuration.

Do not blindly enable GPU instancing either.

Benchmark actual rendering paths.

---

# 3.5 COLOR_0

Inspect:

* color-space handling
* import behavior
* shader interpretation
* average brightness
* contrast range
* whether simplification changes vertex-color appearance
* whether AO is being multiplied by runtime SSAO

Important:

Because AO is already baked into `COLOR_0`, check whether Unity's runtime SSAO or other occlusion systems create double-darkening.

Only change this if the audit confirms an actual visual problem.

---

# 3.6 AO / Wear / Dirt

Check for known failure cases:

* rotating parts receiving inappropriate AO
* aircraft appearing to have ground-contact shadows where they should not
* large sparse plates receiving unwanted mottling
* excessive darkening under overlapping parts
* AO becoming too strong after LOD
* aircraft/rotor geometry producing incorrect occlusion

Do not rewrite the AO system unless these issues are confirmed.

---

# 3.7 URP / Platform

Inspect:

* URP version
* mobile renderer path
* PC renderer path
* shader keywords
* quality settings
* shadows
* post-processing
* MSAA
* dynamic resolution if used
* batching
* GPU instancing
* platform-specific shader branches

Do not introduce platform-specific shader complexity unless necessary.

---

# 4. P0-A — CREATE AN ASSET BASELINE / REGRESSION SYSTEM

Treat the asset pipeline similarly to a software build pipeline.

Create a deterministic analyzer for the exported GLBs.

For every asset record at minimum:

* asset name
* file size
* triangle count
* vertex count
* mesh count
* renderer/node count if available
* material count
* material-slot count
* submesh count
* bounds
* dimensions
* center
* required gameplay node names
* `COLOR_0` statistics
* mesh hash / structural hash

Also record relevant animation/bone data if present.

The baseline must cover all existing assets, approximately 361.

Example:

```text
MBT:
triangles: 18,200
vertices: 11,400
materials: 5
materialSlots: 7
meshes: 9
fileSize: 1.8 MB
```

Future changes should report:

```text
MBT

triangles:
18,200 → 19,100 (+4.9%)

vertices:
11,400 → 11,950 (+4.8%)

materials:
5 → 5

materialSlots:
7 → 7

fileSize:
1.8 MB → 1.9 MB
```

Large unexpected changes must be flagged.

Do not automatically reject intentional changes.

Allow a baseline to be updated explicitly with a reason.

Example:

```text
MBT:
triangle increase accepted because turret geometry was redesigned.
```

The baseline system must support:

* current baseline
* comparison
* intentional update
* reason
* regression flag

---

# 5. P0-B — 100% MACHINE VALIDATION

Every exported asset should go through automated validation.

Do NOT require every mesh to be mathematically "non-manifold free".

Some valid game meshes can intentionally contain open surfaces.

Instead detect actual problematic topology/geometry appropriate to the asset.

Checks should include:

## Geometry

* file loads successfully
* valid GLB structure
* no NaN
* no Infinity
* no invalid indices
* no zero-area/degenerate triangles
* no obviously corrupted geometry
* reasonable bounds
* reasonable scale
* reasonable origin
* reasonable dimensions

## Complexity

Check:

* triangles
* vertices
* meshes
* renderers
* materials
* material slots
* submeshes
* bones where applicable
* file size

## Gameplay contracts

Check required nodes where applicable:

* `Turret`
* `Main_cannon`
* `Muzzle_*`
* `Mount_*`
* `Rotor`
* etc.

Do not enforce every node on every model.

Define requirements by asset category.

## Vertex color

Check:

* `COLOR_0` exists where required
* valid range
* brightness statistics
* suspiciously black/white assets
* unexpected missing vertex color

## Budget

Compare against type-specific budget.

## Regression

Compare against baseline.

Output machine-readable JSON.

---

# 6. P0-C — UNITY IS THE VISUAL GROUND TRUTH

Blender previews are NOT the final visual quality authority.

Blender is responsible for:

* geometry
* silhouette
* naming
* procedural construction
* vertex colors
* AO generation
* export correctness

Unity is responsible for evaluating the final appearance.

Create or extend a deterministic Unity preview/validation scene.

---

# 7. UNITY VISUAL VALIDATION

For representative assets, render:

## Angles

At minimum:

* front
* rear
* left
* right
* front-left
* front-right
* rear-left
* rear-right

Also render gameplay-camera views:

* Close
* Gameplay
* Far

The gameplay camera is the most important view.

---

# 8. QUALITY MATRIX

Use:

| Platform | Quality | Target |
| -------- | ------- | ------ |
| Mobile   | Low     | ~720p  |
| Mobile   | High    | 1080p  |
| PC       | Low     | 1080p  |
| PC       | High    | 1080p  |

Do not add 4K as a required validation target.

All four tiers should use the same source asset whenever possible.

Differences should primarily come from:

* LOD
* material/shader quality
* shadow settings
* impostor resolution
* rendering settings
* runtime quality settings

not separate asset copies.

---

# 9. VISUAL REGRESSION

Do NOT use strict pixel-perfect equality as the only pass/fail criterion.

Rendering can legitimately differ because of:

* anti-aliasing
* GPU
* driver
* color management
* resolution
* lighting
* dynamic rendering behavior

Use a combination of:

* perceptual similarity / SSIM where useful
* silhouette difference
* bounding-box difference
* contrast
* Team-color separation
* major feature visibility

The objective is to catch meaningful visual regressions rather than harmless GPU noise.

Golden images should be deterministic where possible.

---

# 10. ART QUALITY PRINCIPLE

The asset does NOT need to be "high detail" simply because it will run on PC.

For an RTS:

> Gameplay readability at the actual camera scale is more important than microscopic geometry.

Before adding geometry ask:

> Is this feature visibly readable at the intended gameplay resolution?

If a bolt, weld, panel seam, internal mechanism, underside detail, or tiny mechanical feature cannot be perceived at gameplay scale, it should generally not consume expensive geometry.

Prioritize:

1. silhouette
2. major proportions
3. turret/cannon/rotor readability
4. faction readability
5. material separation
6. major surface forms
7. medium-scale detail
8. tiny detail only where actually visible

---

# 11. P0-D — PLATFORM / QUALITY BUDGETS

Create explicit budgets by:

* asset category
* platform
* quality tier

Do not use one universal triangle limit.

At minimum budget:

* triangles
* vertices
* meshes
* renderers
* materials
* material slots
* submeshes
* shadow caster complexity
* bones if applicable
* file size
* runtime memory where measurable
* LOD level
* impostor usage

Material slots and renderers must be treated as important performance metrics.

A model with fewer triangles but many material slots may still be expensive.

Where safe:

* merge static geometry using the same material
* reduce unnecessary renderers
* reduce unnecessary material slots

But keep separate objects when gameplay requires:

* turret rotation
* cannon recoil
* rotor movement
* muzzle/fire effects
* destruction/animation
* other runtime manipulation

Never optimize away a gameplay contract without checking its consumers.

---

# 12. LOD POLICY

Keep runtime LOD as the primary system.

Prefer LOD transitions based on visible screen size rather than blindly using world distance.

This is particularly important for an RTS camera.

Use the following conceptual tiers:

```text
LOD0
High visual quality
Close gameplay view

LOD1
Reduced geometry
Normal gameplay view

LOD2
Strongly simplified
Far gameplay view

Impostor
Very far distance
```

Do not automatically bake Blender LODs for all 361 assets.

Baked/prebuilt LOD may be considered for:

* Boss
* Hero
* exceptionally complex vehicles
* highly repeated expensive assets

only if benchmark data demonstrates a benefit.

---

# 13. ONE SOURCE ASSET

Prefer:

```text
one high-quality source
        ↓
Unity import/runtime optimization
        ↓
Mobile Low
Mobile High
PC Low
PC High
```

Do NOT create:

```text
tank_mobile.glb
tank_mobile_hd.glb
tank_pc.glb
tank_pc_hd.glb
```

for every asset.

Separate platform-specific assets should only be introduced when measured evidence proves the single-source approach is insufficient.

If a PC-only asset is eventually required, it must be explicitly tagged and excluded from mobile builds.

---

# 14. `_hd` POLICY

Do not proliferate `_hd` versions.

The existing approximately 12 `_hd` assets should be audited.

Determine why they exist.

If their purpose can be replaced by:

* higher source quality
* runtime LOD
* quality settings
* import settings

prefer that approach.

Keep `_hd` only where there is a demonstrated reason.

---

# 15. IMPOSTOR POLICY

Keep the current impostor approach unless measurement shows a problem.

Evaluate:

* memory
* resolution
* angle count
* transition quality
* mobile performance
* PC performance

Mobile and PC may use different impostor settings while still using the same source asset.

---

# 16. MATERIAL STRATEGY

Keep the existing material vocabulary.

Do NOT:

* rename 50 material categories
* introduce texture atlases
* introduce UV mapping
* introduce PBR texture sets

in this prompt.

Continue using:

```text
Material
×
COLOR_0
×
Team Tint
×
URP Lighting
```

as the core visual architecture.

If future PC testing at 1080p demonstrates a clear material-quality limitation, create a separate experiment rather than changing the entire pipeline here.

---

# 17. BATCHING / GPU OPTIMIZATION

Do not assume one rendering optimization is universally better.

Measure:

* SRP Batcher
* GPU instancing
* existing batching paths
* renderer count
* material slots
* draw calls

Use the configuration that actually improves the target scene on target hardware.

Do not hard-code statements such as:

```text
SRP Batcher is disabled on GLES
```

without verifying the actual Unity/project/platform configuration.

If Unity 6 GPU Resident Drawer or another newer rendering system becomes relevant later, treat it as a separate rendering-performance experiment.

Do not introduce it into this asset-pipeline upgrade without benchmark evidence.

---

# 18. AO / COLOR_0 POLICY

Keep the current AO/wear/grime approach unless the audit finds a concrete problem.

Pay special attention to:

* double-darkening from baked AO + runtime SSAO
* rotating part AO
* aircraft ground contact
* large sparse surfaces
* LOD color changes
* vertex density affecting AO quality

If a problem exists:

1. reproduce it
2. identify the cause
3. make the smallest possible fix
4. compare before/after in Unity
5. update the baseline if intentional

Do not rewrite the whole AO system preemptively.

---

# 19. P0-E — CONTROLLED EXPERIMENT

Before changing the entire pipeline, run a small controlled experiment.

Use:

1. MBT
2. Su-27
3. Icarus
4. one common high-count/complex unit

Recreate these using the proposed improved procedural kit/configuration.

The control condition must preserve the original design.

Do not simultaneously change:

* geometry style
* material architecture
* LOD architecture
* shader
* AO system
* naming
* gameplay integration

Change one major variable at a time.

Measure:

## Geometry

* triangle count
* vertex count
* mesh count
* material slots
* renderers
* file size

## Visual

* silhouette
* readability
* COLOR_0
* Team tint
* AO
* gameplay-camera appearance
* LOD appearance

## Runtime

* CPU
* GPU
* draw calls
* memory
* loading time
* LOD distribution

Define thresholds BEFORE the experiment.

Do not claim an improvement without measured evidence.

If the improvement is unclear, stop and report the result rather than expanding the change to all 361 assets.

---

# 20. BENCHMARK SCENE

Create a deterministic benchmark scene.

It should contain a representative mix of:

* tanks
* aircraft
* buildings
* terrain
* effects where relevant

Use a fixed/seeded scene so that comparisons are repeatable.

Create at least:

## Mobile benchmark

Representative unit count for the target mobile hardware.

## PC benchmark

A larger unit count appropriate for a lightweight PC RTS.

Do not artificially target extreme PC hardware.

The purpose is to verify that the asset architecture scales comfortably to the intended game.

Measure:

* FPS
* frame time
* CPU frame time
* GPU frame time
* draw calls
* triangles
* vertices
* memory
* loading time
* LOD distribution
* impostor count
* spikes/hitches

Prefer frame-time percentiles and worst-case spikes over average FPS alone.

---

# 21. REAL DEVICE VALIDATION

Emulators are useful for functionality but are NOT sufficient for performance conclusions.

At the relevant checkpoint:

* test on at least one real mobile device
* record actual frame time
* record thermal/performance behavior where practical
* record memory
* record visible LOD behavior

For PC, test on concrete representative hardware once the PC benchmark configuration is established.

---

# 22. ART BIBLE

Create/update an English Art Bible describing the actual production rules.

It should include:

## Style

* RTS readability
* hard-surface procedural style
* silhouette-first philosophy
* appropriate bevel usage

## Materials

* material vocabulary
* Team tint
* COLOR_0
* AO/wear/grime principles

## Geometry

* detail priorities
* pixel/readability rule
* when geometry should NOT be added

## Naming

Gameplay node contracts.

## Performance

Budgets by:

* Mobile Low
* Mobile High
* PC Low
* PC High

Include:

* triangles
* vertices
* renderers
* materials
* material slots
* shadows
* file size
* LOD

## LOD

Document:

* LOD0
* LOD1
* LOD2
* impostor
* screen-space principle

## Regression

Document:

* baseline creation
* comparison
* intentional baseline updates
* required reason for large changes

---

# 23. PRODUCTION WORKFLOW AFTER P0

Once the experiment is validated, the production workflow should become:

```text
Modify Blender Python
        ↓
Generate asset
        ↓
Export GLB
        ↓
Machine validation
        ↓
CatalogCheck
        ↓
Baseline comparison
        ↓
Unity import
        ↓
Unity visual preview
        ↓
Flagged assets reviewed
        ↓
Fix if necessary
        ↓
Update baseline when intentional
        ↓
Commit
```

Do not require a full test suite for every asset-generation iteration unless `CLAUDE.md` or project policy explicitly requires it.

Follow the existing repository rules.

---

# 24. VISUAL REVIEW STRATEGY FOR 361 ASSETS

Do NOT manually inspect all 361 assets at maximum detail every time.

Do NOT ask AI to assign every model a 1–5 visual score.

Instead:

## 100% automated

All assets:

* GLB validity
* geometry validity
* complexity
* material slots
* renderers
* names
* COLOR_0
* bounds
* baseline regression

## Selective visual review

Prioritize:

* tanks
* aircraft
* boss
* hero
* large buildings
* newly created assets
* modified assets
* assets that fail regression
* assets with unusual complexity
* representative assets from each category

For small/common props, review category-level batches and flagged assets.

---

# 25. PRODUCTION WAVES

After P0 is validated, process assets in waves.

Suggested approach:

### Wave 1

Representative combat vehicles

### Wave 2

Aircraft

### Wave 3

Buildings

### Wave 4

Defensive structures

### Wave 5

Terrain/props

### Wave 6

Special units

### Wave 7

Boss/Hero

### Wave 8

Remaining assets

For each wave:

```text
Generate
→ Machine Check
→ CatalogCheck
→ Baseline Comparison
→ Unity Preview
→ Review flagged assets
→ Fix
→ Commit
```

Do not blindly regenerate all 361 assets before validating the pipeline.

---

# 26. CHECKPOINTS

## Checkpoint 1

Before large-scale production:

Confirm:

* baseline system works
* machine validation works
* Unity preview works
* visual regression works
* budgets are measurable
* LOD behavior is understood
* experiment results are documented

Stop here and report findings before large-scale changes if the evidence does not clearly support the proposed architecture.

## Checkpoint 2

After representative production assets:

Confirm:

* mobile benchmark
* PC 1080p benchmark
* visual quality
* memory
* draw calls
* LOD
* impostors
* material slots
* actual device performance

Only then expand to the remaining asset waves.

---

# 27. OUT OF SCOPE

Do NOT implement these as part of Prompt 27:

* texture atlas
* UV overhaul
* texture baking
* PBR texture pipeline
* biome-specific building architecture
* landmarks
* two-faction architecture redesign
* color-blind mode
* roof fade
* UI/control redesign
* Play Asset Delivery
* PC store/distribution
* full PC build/distribution pipeline

PC asset compatibility and PC 1080p performance ARE in scope because they directly affect the asset architecture.

---

# 28. IMPORTANT FUTURE EXPERIMENTS — DO NOT IMPLEMENT NOW

Potential future experiments may include:

* texture/UV workflow
* PC-specific higher-detail materials
* triplanar mapping
* GPU Resident Drawer
* more advanced instancing
* dedicated baked LODs for selected complex units
* PC-only assets
* 1440p/4K validation
* texture streaming
* additional shader features

These should be separate experiments with measurable goals.

Do not mix them into Prompt 27.

---

# 29. REQUIRED DELIVERABLES

At the end of this work, provide:

1. `STEP0_AUDIT.md`

   * current pipeline findings
   * LOD findings
   * impostor findings
   * material/rendering findings
   * COLOR_0/AO findings
   * platform findings

2. Asset baseline dataset

   * approximately 361 assets

3. Asset analyzer

   * machine-readable JSON output

4. Asset validation tool

   * geometry
   * naming
   * complexity
   * COLOR_0
   * bounds
   * budgets
   * regression

5. Unity visual validation scene/tool

6. Unity preview images for representative assets

7. Visual regression system

8. Platform/quality budget document

9. Controlled experiment report

   * MBT
   * Su-27
   * Icarus
   * one representative complex unit

10. Benchmark scene

11. Benchmark measurements

12. Art Bible

13. `PROGRESS.md`

---

# 30. CODING / DOCUMENTATION RULE

All:

* code
* comments
* documentation
* reports
* generated config

must be written in English.

Communicate with the user in Vietnamese.

---

# 31. FINAL PRINCIPLES

The implementation must follow these principles:

1. **Do not rewrite a working system without evidence.**

2. **Unity is the final visual ground truth.**

3. **1080p is the primary visual target for PC.**

4. **The PC version is lightweight; do not optimize the art pipeline for 4K unnecessarily.**

5. **One high-quality source asset should serve multiple platform/quality tiers whenever possible.**

6. **Runtime LOD remains the primary LOD system.**

7. **Do not bake LODs for all 361 assets.**

8. **Do not create `_hd` versions for everything.**

9. **Do not create separate mobile/PC GLBs without benchmark evidence.**

10. **Material slots and renderers matter in addition to triangle count.**

11. **Gameplay node names are contracts.**

12. **Keep `MaterialLibrary`, `MachineBrigade/Lit`, `COLOR_0`, Team tint, and existing tower-detail logic.**

13. **Do not introduce texture/UV/atlas changes in this prompt.**

14. **Do not assume a batching strategy is better; measure it.**

15. **Do not hard-code incorrect platform assumptions such as SRP Batcher being disabled on GLES.**

16. **Do not require mathematically manifold meshes when open game geometry is valid.**

17. **Do not use pixel-perfect image comparison as the only visual regression method.**

18. **Do not require every model to be highly detailed; prioritize gameplay-scale readability.**

19. **Machine-check 100% of assets.**

20. **Use selective visual review instead of manually scoring all 361 assets.**

21. **Benchmark on real mobile hardware.**

22. **Benchmark PC at 1080p.**

23. **Use deterministic experiments and explicit baselines.**

24. **Do not expand the new pipeline to all assets until the controlled experiment and benchmarks justify it.**

25. **If the evidence does not show a meaningful improvement, stop and report instead of forcing the migration.**

The desired end state is:

```text
Procedural Blender Python
        ↓
One high-quality source asset
        ↓
Deterministic GLB export
        ↓
100% automated validation
        ↓
Unity import
        ↓
Runtime LOD / impostor / quality settings
        ↓
┌─────────────────────────────┐
│ Mobile Low   ~720p          │
│ Mobile High  1080p          │
│ PC Low       1080p          │
│ PC High      1080p          │
└─────────────────────────────┘
        ↓
Benchmark + Visual Validation
```

Do not optimize for theoretical future requirements.

Optimize for the actual game:

**Machine Brigade — lightweight RTS, mobile + PC, with 1080p as the primary target.**
