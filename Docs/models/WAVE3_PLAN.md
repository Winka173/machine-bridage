# Prompt 27 wave 3: ground vehicles (V2), split into small passes

The owner (2026-10-02): "bắt đầu prompt 27 đợt 3, nhớ chia nhỏ ra, và tiết kiệm token". 65 models, 8 passes of 8-9,
one agent at a time, each pass on its own branch `feature/p27-wave3<x>` from `lead/integration`, merged by the lead.

| pass | models |
|---|---|
| 3a | heavy_tank (+hd), light_tank (+hd), tank_destroyer (+hd), elite_heavy_tank, elite_mbt, elite_tank_destroyer, titan_tank, turtle_tank | done (builds and static gates; cards and previews still to render, DECISIONS 27 wave 3a)
| 3b | laser_tank, flame_tank, twin_tank, bmpt, ifv, elite_apc, armored_bulldozer, engineer_vehicle | done (builds and static gates; cards by the lead, DECISIONS 27 wave 3b)
| 3c | aa_vehicle (+hd), artillery (+hd), heavy_aa, elite_aa, mortar_carrier, mine_layer, smoke_carrier, shield_carrier | done (builds and static gates; cards by the lead, DECISIONS 27 wave 3c)
| 3d | mlrs, elite_mlrs, heavy_rocket_artillery, thermobaric_launcher, ballistic_launcher, long_sam, sam_launcher, iron_beam |
| 3e | counter_battery_radar, ew_jammer, bunker_vehicle, ammo_carrier, supply_truck, railgun_truck, shahed_truck, vbied |
| 3f | wheeled_gun, zu23_technical, rocket_technical, hover_gunboat, aa_gun_vehicle, airborne_vehicle, fibre_fpv_carrier, interceptor_drone_vehicle |
| 3g | microwave_vehicle, nlos_atgm_vehicle, radar_atgm_vehicle, radar_scout, recoilless_jeep, shorad_vehicle, sp_mortar, wheeled_howitzer |
| 3h | armored_car, command_vehicle, fpv_carrier, lancet_truck, scout_jeep (+hd), landing_craft, missile_boat, sea_corvette, grad_truck |

## The standing brief for every pass (the agent reads this instead of a long prompt)

Read first, by line ranges: this file; `Docs/models/PROGRESS.md` "Wave 3"; `Docs/models/art-bible.md`; the recipe in
`Docs/models/EXPERIMENT_1.md` (near line 158); `Docs/models/BUDGETS.md`; `Tools/assets/README.md`; in `Docs/DECISIONS.md`
(grep headings, never read it whole) the sections "27 experiment 1", "27 wave 1c pass A", "27 wave 1c pass B",
"27 wave 2 pass A", "27 wave 2 pass B" and every "27 wave 3" section already there (lessons of earlier passes).
Look at `Tools/blender/mb_p27_experiment.py` (the V2 main_battle_tank is the model to copy for tracked vehicles),
`mb_kit27.py`, `mb_parts27.py` and the wave 1c builders in `mb_p27_wave1c.py` for wheeled ones.

Rules:
- These are rebuilds of the SAME model: keep every runtime node name (turret, mounts, muzzles, `Part_*`, `Deploy_*`,
  rotors, every variant's keep/drop nodes: grep balance.json for defs that share the model), pivots, materials,
  proportions (within 4 % of `modelSize`), the `_hd` twin where one exists. Gates: triangles <= 1.6x (hard 2x) and
  within BUDGETS, zero-area 0, COLOR_0 >= old (use `ao_strength` per model if a rebuild dims it), card luma >= old - 1 %.
  If a model cannot pass a gate, keep the old one and say why.
- Builders go in `Tools/blender/mb_p27_wave3.py` (create it in 3a, extend it after), registered last in `build_assets.py`.
- Never use MaterialPropertyBlocks on MachineBrigade/Lit renderers. No balance.json number changes (only if a node
  field must follow a renamed node; then run CatalogCheck).
- **Owner 2026-10-02 (after 3a): agents do NOT mirror into the runner and do NOT render cards or previews** (the
  permission system refuses the robocopy /MIR there). The lead merges each pass, syncs lead -> runner with
  handoff_tools/sync.sh, renders cards + previews and checks card luma. Agents stop after the GLBs, the validator and
  the docs; list the old card luma of each model (from the current card PNGs, mean luma of pixels with alpha > 0.5)
  in the report. When rebuilding `light_tank`, revert `airborne_light_tank(_chute)` (substring filter).
- Allowed runs only: Blender rebuild; `python Tools/assets/glb_check.py --compare --only <names>` then `--accept` with a
  reason; mirror the worktree into `C:\Users\Winka\Projects\MachineBrigade-runner` with PowerShell robocopy
  (`/MIR /XD Library Logs Builds .git UserSettings /XF .git`; Git Bash robocopy fails); in the runner card renders
  (`env -u ELECTRON_RUN_AS_NODE "/c/Program Files/Unity/Hub/Editor/6000.6.3f1/Editor/Unity.exe" -batchmode
  -force-d3d11 -force-device-index 1 -quit -projectPath . -executeMethod MachineBrigade.Editor.CardRenders.RenderBatch
  -mbCardsOnly "<ids>" -logFile <log>`, no -nographics) and the preview (`-executeMethod
  MachineBrigade.Editor.ModelPreview.RenderBatch -mbPreview "<ids>"`, same flags), one batch each; CatalogCheck only if
  balance.json changed. Copy new cards (+ .meta, manifest entries for these ids only) back. No tests, fixtures, sims,
  measures. Look at no more than 3 images per pass; use the luma numbers.
- Save tokens: grep and line ranges; no sub-agents; a short report.
- Docs per pass: a DECISIONS section "## 27 wave 3<x> (lead pass, <date>)" at the end (short: lessons, exceptions);
  mark the models in PROGRESS.md and in the table above (append "done"); one line under "## Unreleased" in
  `Docs/CHANGELOG.md`. Commit every 2-4 models; messages end with the attribution line the lead gives. Do not push,
  do not merge. On a quota stop, commit sound pieces first.
- Report in ~8 lines: commits, a compact table (model: tris old -> new, card luma old -> new, pass/kept-old), problems.
