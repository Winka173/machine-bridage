# Tools/assets: GLB baseline and validator (prompt 27)

Static: reads `Assets/MachineBrigade/Resources/Models/*.glb` (Python 3.11 + numpy; no Unity, no Blender).

- `python Tools/assets/glb_check.py` - analyse and validate every GLB; writes `baseline.json` and `Docs/models/BASELINE.md`. Refuses (exit 1) when a counted metric moved over 10 % against the committed baseline.
- `python Tools/assets/glb_check.py --compare` - list changes against `baseline.json` (FLAG = over 10 %), write nothing.
- `python Tools/assets/glb_check.py --accept NAME ... --reason "why"` - take an intentional change; the reason goes in `baseline.json` history.
- `python Tools/assets/glb_check.py --only NAME ...` - print full rows for some models, write nothing.
- `glb_analyze.py` = per-file stats (triangles, vertices, renderers, slots, bounds, COLOR_0, topology, runtime nodes); `glb_check.py` = categories, rules, outputs.
- Rules and thresholds: Docs/DECISIONS.md "27 step 0 + baseline". Exit code 1 when any model has an error.
- Run it after every `build_assets.py` run, before committing new GLBs.
