# Agent rules (read this first)

Briefs say "read Docs/AGENT_RULES.md first" instead of repeating these rules. A brief may override a rule by name.

**Quality before tokens on detail work (owner, 03/10).** Building or fixing models and visual effects (VFX,
explosions, smoke, warning rings, wrecks) gets the best quality possible: run as many gate rounds as needed, look at
the renders, use the strongest model. Token saving applies only to routine work: merges, docs, exports, status, small
fixes. Nothing below asks you to cut a corner on a model or an effect.

## Never, unless the owner's word is in your brief
- No Unity runs, EditMode/PlayMode tests, sims, sweeps or measurements. Write tests if asked; do not run them.
  Allowed: compile checks the brief names, Blender builds, static Python tools over files (glb_analyze, quality_gate).
- No gameplay value changes (balance.json, campaign.json, weapons, health, costs) unless the brief asks for them.
- Never shrink fire or explosions.
- No real-world national insignia or unit markings; use the factions' own marks.

## Code and assets
- Never put a `MaterialPropertyBlock` on a `MachineBrigade/Lit` renderer (draws at ~40 % brightness, PT11). Tint
  through `MaterialLibrary.Tinted` shared copies.
- Flare points are `Mount_Flare_L` / `_R` (plus `_L2` / `_R2`, `_TL` / `_TR`); never a bare `Mount_Flare` (the
  runtime reads `Mount_<letters>` as a weapon pivot).
- New builders are registered **inside** the builders dict of `Tools/blender/build_assets.py`, never after it; then
  `python -m py_compile Tools/blender/build_assets.py`.
- The build filter is a **substring** match (`-- light_tank` also builds `airborne_light_tank`). After a build,
  `git status` the GLBs and `git checkout` any you did not mean to change.
- Triangle budgets are information only; keep over-budget models, except units seen in numbers (technicals, light
  vehicles, towers) stay at or under 1.5 x the class maximum.
- Keep parts at least 1 cm apart (coplanar faces z-fight).

## Files and tokens (routine work)
- Scratch files go in your own subfolder of the scratchpad (e.g. `scratchpad/lane_c_w12/`) with distinctive names.
- `Docs/DECISIONS.md` (1.7 MB) and `Docs/CHANGELOG.md`: grep, then read line ranges. Never read them whole.
- Grep before Read; read big files with offset/limit; do not re-read a file you already have.
- Cap command output: `| tail -20`, `| head -40`, `cut -c1-200`, quiet flags. Blender logs: grep the lines you need.
- Batch independent tool calls in one message. Prefer the existing tools (`Tools/assets/glb_analyze.py`,
  `Tools/assets/quality_gate.py`, `Tools/models/sheet.py`, `Tools/art/model_sheet.py`) to new one-off scripts.

## Finish
- Append your decisions to `Docs/DECISIONS.md` as a new `## <prompt/wave> (lane X)` section at the end; add one line
  under `## Unreleased` in `Docs/CHANGELOG.md`.
- Commit with a short subject ("Prompt 35 wave 12 (lane C): ...") and the Co-Authored-By line from your brief. Do not
  push or merge unless told; the lead merges.
- Report in 5-15 lines: commit, what changed, what failed, open questions. No file dumps.
