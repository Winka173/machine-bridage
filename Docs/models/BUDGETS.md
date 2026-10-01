# Model budgets per class and tier (prompt 27 step 5)

Date 2026-10-02. Decisions: DECISIONS "27 preview + budgets + art bible". Derived from the static baseline
(`Tools/assets/baseline.json`, 400 GLBs, 2026-10-02) and the experiment's gates (EXPERIMENT_1.md: a rebuilt model's
triangles within 1.6x of its own baseline, hard 2x). Nothing was measured on a device: these are authoring budgets,
not frame-time budgets. When the owner allows measuring, checkpoint 2's benchmark may move them.

## How the numbers are made

- **Soft budget** (validator warning) = the class's 90th percentile x 1.6; **hard cap** (validator error) = p90 x 2.
  Rounded up to 100 (triangles, vertices) or to a whole count. Bosses evened out so a bigger class never gets less.
- **Tiers.** `normal` = the GLB every platform loads: phones (Mobile Low 720p at 70 % render scale, Mobile High 1080p
  at 85-100 %) and PC wherever no `_hd` ships. `hd` = the `_hd` twin the PC high tiers load (`ModelLibrary.HighDetail`),
  today only 12 ground and air models: normal budget x the median `_hd`/normal ratio of those 12 (triangles 2.4,
  vertices 2.7, renderers 1.35). Moving parts are identical in both tiers (the validator requires the same runtime
  nodes). A class without `_hd` files uses its normal budget on PC too (one source asset, prompt section 13).
- **Metrics.** Triangles and vertices of the file; renderers = GLB mesh nodes (authoring cost; `ModelLibrary.Template`
  merges the rigid ones, so the runtime LOD0 draw count is the moving parts x material slots on them, not this number);
  moving parts = the runtime nodes the template keeps separate (Turret, Main_cannon, Mount_*, Rotor, Tail_rotor,
  Radar, Propeller, Part_*, loose and Deploy_* pieces), each one a draw per LOD0 instance plus a shadow draw.
- **Classes** (`budget_class` in glb_check.py): the baseline category, with air split into helicopter (a `Rotor` node
  or "heli" in the name) and jet (everything else that flies: jets, bombers, drones, gunships), bosses by the GLB's
  longest side (small < 30 m, medium < 60 m, large), statics into tower (a Turret, Mount or Muzzle node) and structure
  (no weapon node), wrecks into their parent's class. The 33 unlisted GLBs (no def names them: strike_jet, ixion,
  spares) have no class and no budget until a def points at them.

## The table

`soft / hard` per metric. Baseline p50 and p90 of the normal files in brackets (triangles).

| class | models | tier | triangles | vertices | renderers | moving parts | baseline tris p50 / p90 |
|---|---:|---|---|---|---|---|---|
| ground | 68 + 7 hd | normal | 7,800 / 9,700 | 10,100 / 12,600 | 61 / 76 | 8 / 10 | 2,546 / 4,841 |
| | | hd | 18,800 / 23,300 | 27,300 / 34,100 | 83 / 103 | 8 / 10 | 8,074 / 12,046 (hd) |
| helicopter | 4 + 1 hd | normal | 6,600 / 8,300 | 8,300 / 10,400 | 45 / 56 | 5 / 6 | 3,315 / 4,109 |
| | | hd | 15,900 / 20,000 | 22,500 / 28,100 | 61 / 76 | 5 / 6 | 6,542 (one file) |
| jet | 15 + 3 hd | normal | 5,100 / 6,400 | 7,100 / 8,900 | 36 / 44 | 6 / 7 | 2,376 / 3,159 |
| | | hd | 12,300 / 15,400 | 19,200 / 24,100 | 49 / 60 | 6 / 7 | 3,764 / 11,838 (hd) |
| boss small (< 30 m) | 15 | both | 36,000 / 45,000 | 43,000 / 54,000 | 130 / 162 | 22 / 28 | 18,866 / 22,400 |
| boss medium (30-60 m) | 7 + wreck | both | 44,000 / 55,000 | 56,000 / 70,000 | 178 / 222 | 25 / 31 | 11,472 / 27,574 |
| boss large (>= 60 m) | 2 | both | 56,000 / 70,000 | 72,000 / 90,000 | 240 / 299 | 41 / 52 | 27,374 / 28,480 |
| tower (armed static) | 46 | both | 14,700 / 18,400 | 20,100 / 25,100 | 144 / 180 | 8 / 9 | 5,664 / 9,168 |
| structure (unarmed static) | 26 | both | 7,900 / 9,900 | 9,800 / 12,200 | 39 / 48 | 2 / 3 | 1,744 / 4,928 |
| prop | 115 | both | 6,900 / 8,600 | 9,900 / 12,300 | 46 / 58 | 2 / 3 | 1,752 / 4,295 |
| scenery | 29 | both | 3,700 / 4,600 | 9,700 / 12,100 | 12 / 14 | 2 / 3 | 436 / 2,288 |
| munition | 28 | both | 500 / 1,600 | 600 / 2,400 | 14 / 17 | 2 / 3 | 203 / 255 |

Munitions' hard cap is raised above p90 x 2 (600) so the FPV drone (1,520 triangles, a munition that is a small
aircraft) warns instead of failing. The tower class holds the headquarters (14,260 triangles, a Turret node).

## Per-model gates in a wave (stricter than the class budget)

A rebuilt model is held to its own baseline row, not only to its class: triangles <= 1.6x (hard 2x), zero-area 0,
COLOR_0 mean >= baseline, size within 1 %, runtime names identical, no new moving part and no new material on a moving
part, card and preview luma within -1 % (EXPERIMENT_1.md recipe; art-bible.md). A model that starts small may grow to
1.6x even if the class budget would allow more; a model already over the class's soft budget may not grow at all
without a DECISIONS line.

## Not budgeted yet (needs a measure or the owner)

- Shadow casters: every LOD0 renderer casts; the shadow cost equals the moving-part count. No separate budget until
  frame time is measured.
- File size (KiB): follows triangles (~60 bytes a triangle with COLOR_0, normals, UVs); `--compare` flags > 10 %.
- Runtime memory, draw calls, LOD1 triangles (MeshSimplifier keeps open edges and many loose pieces: Icarus 561) and
  impostor counts: checkpoint 2, when measuring is allowed.
- Material slots: one material per part is the kit's rule, so slots = renderers today; a budget would duplicate it.

## Where the baseline stands (glb_check.py, 2026-10-02)

13 models are over a budget (8 over a soft budget only, 5 over a hard cap); with them the validator reports 18 models
with errors (the 13 of the baseline plus the 5 hard caps):

| model | class | over |
|---|---|---|
| siege_tank | ground | renderers 80 (cap 76), moving parts 22 (cap 10) - hard |
| sea_cruiser | ground | moving parts 14 (cap 10) - hard |
| flak_tower | tower | moving parts 10 (cap 9) - hard |
| command_hq | prop | renderers 62 (cap 58) - hard |
| shield_generator | prop | renderers 63 (cap 58) - hard |
| grad_truck | ground | triangles 8,092, vertices 10,240 - soft |
| bunker_vehicle | ground | moving parts 9 - soft |
| fighter_jet_hd | jet hd | triangles 13,856, vertices 20,836 - soft |
| headquarters | tower | vertices 20,274 - soft |
| targeting_station | structure | moving parts 3 - soft |
| fpv_drone | munition | triangles, vertices, renderers - soft |
| repair_crate, supply_crate | scenery | renderers 13 / 14 - soft |

The full list per model is in `Docs/models/BASELINE.md` ("Over budget") and in each record of `baseline.json`
(`budgetClass`, `movingParts`, warnings, errors).
