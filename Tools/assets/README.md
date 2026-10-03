# Tools/assets: GLB baseline and validator (prompt 27)

Static: reads `Assets/MachineBrigade/Resources/Models/*.glb` (Python 3.11 + numpy; no Unity, no Blender).

- `python Tools/assets/glb_check.py` - analyse and validate every GLB; writes `baseline.json` and `Docs/models/BASELINE.md`. Refuses (exit 1) when a counted metric moved over 10 % against the committed baseline.
- `python Tools/assets/glb_check.py --compare` - list changes against `baseline.json` (FLAG = over 10 %), write nothing.
- `python Tools/assets/glb_check.py --accept NAME ... --reason "why"` - take an intentional change; the reason goes in `baseline.json` history.
- `python Tools/assets/glb_check.py --only NAME ...` - print full rows for some models, write nothing.
- `glb_analyze.py` = per-file stats (triangles, vertices, renderers, slots, bounds, COLOR_0, topology, runtime nodes); `glb_check.py` = categories, rules, outputs.
- Rules and thresholds: Docs/DECISIONS.md "27 step 0 + baseline"; budgets per class and tier: Docs/models/BUDGETS.md (`BUDGETS` in glb_check.py: over soft = warning, over hard = error). Exit code 1 when any model has an error.
- Run it after every `build_assets.py` run, before committing new GLBs.
- `python Tools/assets/glb_quantize.py [files]` - KHR_mesh_quantization (int8 normals, uint16 COLOR_0) over every GLB or the files named; `frontier_kit.export_collection` already runs it after each export (DECISIONS "Prompt 35: GLB size (lane A)").

## Unity preview (`--preview`, prompt 27 step 5)

Contact sheets rendered in Unity for the models named on the command line only (flagged or changed models, never all):

```
env -u ELECTRON_RUN_AS_NODE "/c/Program Files/Unity/Hub/Editor/6000.6.3f1/Editor/Unity.exe" -batchmode -force-d3d11 \
  -force-device-index 1 -quit -projectPath . -executeMethod MachineBrigade.Editor.ModelPreview.RenderBatch \
  -mbPreview "main_battle_tank,fighter_jet" [-mbPreviewOut Builds/preview] -logFile preview.log
```

- Needs a graphics device: no `-nographics`. Run it in the runner tree (mirror the worktree first), ~25 s for 4 models.
- Writes `Builds/preview/<id>.png` + `<id>.json`, and `<id>_hd.png/.json` when `<id>_hd.glb` ships (git-ignored).
- Sheet (2048 x 1536, 512 px cells): rows 1-2 = 8 angles through the card stage (card lights, orthographic, pitch 26):
  front, front-right, right, rear-right / rear, rear-left, left, front-left. Row 3 = the battle camera (orthographic,
  pitch 52, yaw -45, LodShots' sun, ground and post-processing): detail (the size at the closest zoom 9 on a 1080 px
  screen, clamped to 144-300 px), LOD1 (103 px, just under VehicleLod's 128 px switch) and impostor (20 px, just under
  24 px), each enlarged by whole pixels. The 4th cell of row 3 is empty.
- JSON per view: `luma` (mean Rec. 709 luma of the stored sRGB values over the model's own pixels; angles before the
  ground shadow, gameplay views with the battle lighting), `pixels`, `level`, `zoomPc` / `zoomPhone` (the battle
  camera's orthographic size where the model is that big: 1080 px at 100 %, 720 px at the Low tier's 70 %), `inPlay*`
  (inside the camera's 9-50 range), plus the active pipeline asset (PC_RPAsset in the editor).
- Compare a model's luma before/after on the same tier; a drop over 1 % is the same gate as the card luminance.
- No property blocks, no tints (stand-in washes are def-level and not drawn); bosses and elites in the enemy colours.
- Code: `Assets/MachineBrigade/Scripts/Editor/ModelPreview.cs` (reuses `CardRenders.Stage` and LodShots' battle stage).
