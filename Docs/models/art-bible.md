# Machine Brigade Art Bible (models)

The production rules for procedural models (Blender Python -> GLB -> Unity), prompt 27 step 5. Sources: the
experiment (EXPERIMENT_1.md), the budgets (BUDGETS.md), the audit (STEP0_AUDIT.md) and DECISIONS "27 ..." sections.
Where this file and a DECISIONS line differ, DECISIONS wins.

## 1. Style: readable from the battle camera first

- The battle camera is orthographic, pitch 52, yaw -45, zoom 9 (closest) to 42 (50 on long maps). A 7.8 m tank is
  468 px across at the closest zoom on a 1080 px screen, 100 px at the widest, ~40 px on a phone at the widest. Design
  for 100 px; reward the 300 px view; the card (512 px, from `_hd`) is the only close-up.
- Detail priority, in this order: silhouette, major proportions, turret / gun / rotor readability, team colour, material
  separation, major surface forms, medium detail (wheels, hatches, racks), tiny detail only where a 300 px view shows it.
- Hard-surface military realism, post-1945 equipment (prompt 26's rule). Clean, slightly chunky shapes; no noise.
- Look at the preview's LOD1 cell (103 px): if the vehicle's role cannot be read there, fix the silhouette before adding
  any detail.

## 2. Silhouette and proportions

- Length:width:height must stay within 4 % of the def's `modelSize` (validator error over 25 %): the view fits the
  length only, width and height follow the model. Keep the GLB bounds the baseline's within 1 % in a rebuild.
- Guns read long and straight (the real calibre-length ratio of the reference), never thinner than 10 cm at normal detail.
- Turrets sit visibly on top; a low-profile design (T-14, M8) still needs a turret step the LOD1 cell shows.
- Aircraft: wings and tail planes read from above (the camera is high). Swept edges, not thick slabs.
- Helicopters: rotor discs at rest are drawn as blades; blades must be visible at 103 px (wide chord, not slivers).
- Bosses: one dominant read (deck, hull, wheels, ring) plus 2-4 large secondary masses; small greebles never carry the
  identity. Size class from BUDGETS.md (small < 30 m, medium < 60 m, large).
- Antennas and masts short (they grow the bounds: the first V2 MBT went from 2.30 to 2.47 m).

## 3. Bevels and chamfers

- Large plates: `k.extrude` / `k.block` with a two-step chamfer on the top edges only; the worn middle row gives the
  bright edge line that reads at gameplay distance.
- Nothing under 12 cm gets a chamfer (`k.block` leaves it plain): a chamfered box costs ~90 triangles against 12.
- Chined hulls and flat-panel airframes: `k.sharp_loft` (chamfered vertical corners, sharp roof edge).
- Round parts: `k.lathe` (one surface, no stacked cylinders). Tubes and rails: `k.sweep`.
- Smoothing: the kit's 50 degree sharp angle; weighted normals. Do not add smooth-shaded bevels on lofted jet skins.

## 4. Kit and part library

- Primitives (`Tools/blender/mb_kit27.py`): extrude, block, lathe, ring, sweep, along / place (arrays), mirrored, inset
  (raised plates on big flat faces only), sharp_loft, cut (MANIFOLD boolean, at most one recess per closed solid),
  greebles (3-6 seeded per surface, vary the seed per model), clean (end every builder with it: zero-area 0).
- Parts (`Tools/blender/mb_parts27.py`): road_wheel, sprocket, idler, track_unit (sagging upper run), hatch, barrel
  (collar or baffle brake), mg_mount, smoke_launcher, antenna, rotor_head, tail_rotor, jet_nozzle, engine_bell,
  engine_nacelle, pylon, launch_rail, hellfire_rack, rocket_pod, canopy. Use them before writing new geometry.
- Use per category (checkpoint 1): ground vehicles, bosses, structures: V2 (kit + parts). Helicopters: V2. Jets: only
  `k.clean` plus the library nozzle and canopy in `_hd`; panel insets on jets cost triangles for nothing visible.
- Builders go in the wave's module, merged last in `all_builders()`; keep every name, pivot, material and `_hd` branch.

## 5. Materials

- Flat PBR factors per kit material (`frontier_kit.MATERIALS`), no textures, no decals, one material per part.
- Team colour: the `Team` (and `TeamGlow`) surfaces are recoloured per faction at runtime; keep a large share of the visible
  top area on `Team`, so the side reads at 40 px. Armor, Steel, Undercarriage, Rubber, Glass for the rest.
- Glowing materials (`GLOWING`): lamps, energy, alloy; small areas only (bloom).
- **Never a MaterialPropertyBlock on a MachineBrigade/Lit renderer** (draws at ~40 % brightness, PT11). Variant and
  stand-in washes go through shared copies from `MaterialLibrary.Tinted`. Previews draw untinted shared materials.
- No new material on a moving part: the merged template draws one mesh per material per moving part.

## 6. COLOR_0, AO and brightness

- COLOR_0 carries baked light, AO, wear and grime (`_shade` in `Asset.finish()`). Its vertex-weighted mean must not
  fall in a rebuild (gate: >= baseline; validator warning outside 0.15-0.95).
- PC adds SSAO (PC_Renderer, active) on top of the baked AO: double darkening. So keep baked AO soft: no deep recess
  that ends in a lathe pole (a muzzle bore, a pod face weighs ~10 dark vertices), shallow cuts, worn bright rims on lips
  and petal tips. `_hd` files are already 5-10 % darker in COLOR_0 than their normal twin; do not widen the gap.
- Brightness gate: card luminance and the preview's luma per view (ModelPreview JSON) within -1 % of the baseline on
  the same tier. PT11's dark-hull bug was caught this way.

## 7. Moving parts and naming (gameplay contracts)

- Runtime names are a contract (ModelLibrary.cs): `Turret`, `Main_cannon*`, `Muzzle_brake`, `Muzzle_<kind>`
  (main, coax, mg, missile, rocket, gun, aam, door_l/r, ramp, agl_l/r, mortar), `Mount_<kind>`, `Rotor`, `Tail_rotor`,
  `Radar`, `Propeller`, `Part_*`, `Deploy_*`, loose pieces. Boss parts name nodes in balance.json (`"node"`, `*` =
  prefix) and `mountWeapons` count mount slots: `Mount_gun.001`-style suffixes are kept where a boss needs them.
- `_hd` runtime node names must equal the normal file's (validator error otherwise).
- Every moving part is a draw per LOD0 instance plus a shadow draw: add one only for gameplay (it turns, recoils,
  spins, breaks, deploys). Budgets per class in BUDGETS.md.
- Pivots: turrets rotate about their ring centre; barrels recoil along their own axis from `Main_cannon`.

## 8. LOD and tiers

- LOD0: the GLB (normal on phones and PC without `_hd`; `_hd` on the PC high tiers). LOD1: `MeshSimplifier` per moving
  part below 128 px across, one `LodSurface` material. Impostor: `ImpostorAtlas` (16 headings) below 24 px. Choice by
  on-screen size with a 12 % band (`VehicleLod`). No Unity LODGroup, no baked Blender LODs.
- LOD1 keeps open edges and loose pieces: fewer, larger greebles; rigid details joined to the hull where possible.
- `_hd` is optional and PC-only; the normal file must look complete on its own.

## 9. Briefs: era and shape

- The shape of each model comes from the balance spreadsheet (`Docs/balance/Machine_Brigade_Can_bang.xlsx`), column
  "Hình dạng (cho AI vẽ)" on the Phương tiện, Công trình and Boss sheets (with "Dựa trên" and "Kích thước hiện"), and
  its drawing guide sheet "Hướng dẫn vẽ" (DECISIONS 25B2).
- Prompt 26's post-1945 rule (DECISIONS 26CD, "D3-D12"): every reference is 1945 or later; reference lines per unit in
  `Tools/docs/unit_refs.json`. Boss sizes: prompt 26 C (`size`, `modelSize` in balance.json).
- Stand-ins: ASSET_DEBT.md says what each real model must be (the "Needs" / "The real model" columns).

## 10. Per category: do / don't

| category | do | don't |
|---|---|---|
| tanks, tracked | V2 running gear (road wheels, sprocket, idler, sagging track), hatches, library barrel, smoke launchers | skirts that hide every wheel; antennas over 0.3 m; more than one recess per solid |
| wheeled, trucks | big library wheels with hubs, readable cab vs bed, the payload (launcher, crane, radar) as the silhouette | thin chassis rails at normal detail; payload parts as new moving parts unless they move |
| helicopters | wide-chord blades, library rotor head and tail rotor, stub wings, rocket pods / racks | new spinners; canopy frames at normal detail (only `_hd`) |
| jets | `k.clean`, clean lofted skin, library nozzle and canopy in `_hd`, readable wing planform from above | insets and greebles on the skin; zero-area slivers at lofted tips |
| bosses | one dominant mass, seeded greebles varied per ship, boss part nodes and mount slots kept | regular grids of identical greebles; growing the bounds; renaming `Mount_*.00N` |
| towers | the weapon on top reads at 40 px, sandbags / pad as a plain base | tall thin masts; detail on the base that the camera never sees |
| structures | big readable volumes, roof shapes, a few large openings | interior detail; window grids as separate parts |
| props, scenery | low counts, merged parts, natural silhouettes | moving parts; glow |

## 11. The static gates (each model in a wave, EXPERIMENT_1 recipe)

1. Record the baseline row (`glb_check.py --only <name>`), the card luminance and a preview
   (`ModelPreview.RenderBatch -mbPreview "<name>"`, Tools/assets/README.md).
2. Copy the winning builder into the wave's module (merged last); keep every name, pivot, material, `_hd` branch.
3. Swap helpers for `mb_parts27` parts; plates with `k.extrude` / `k.block`; `k.sharp_loft` for chined hulls;
   `k.inset` on big flat faces only; `k.cut` at most once per solid; 3-6 seeded greebles per surface.
4. No deep recess poles; nothing thinner than 10 cm at normal detail; keep the bounds.
5. End with `k.clean(a)`; rebuild normal and `_hd`.
6. Gates: triangles <= 1.6x (hard 2x) and inside the class budget (BUDGETS.md), zero-area 0, COLOR_0 mean >= baseline,
   size within 1 %, runtime names identical, no new moving part or material on a moving part, card luminance and
   preview luma within -1 %.
7. Render the card and the preview, `glb_check.py --accept <names> --reason "..."`, one model per commit.

## 12. Regression

- `glb_check.py` writes `baseline.json` and refuses when a counted metric moved over 10 % (`--compare` lists,
  `--accept NAME --reason TEXT` takes an intentional change into the history with its reason).
- A large change (over 1.6x, a new moving part, a darker card) needs a DECISIONS line before `--accept`.
- Unity is the visual ground truth: card PNG and preview sheet before and after, same tier.
