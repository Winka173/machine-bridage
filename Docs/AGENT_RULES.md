# Agent rules (read this first)

Briefs say "read Docs/AGENT_RULES.md first" instead of repeating these rules. A brief may override a rule by name.

**Quality before tokens on detail work (owner, 03/10).** Building or fixing models and visual effects (VFX,
explosions, smoke, warning rings, wrecks) gets the best quality possible: run as many gate rounds as needed, look at
the renders, use the strongest model. Token saving applies only to routine work: merges, docs, exports, status, small
fixes. Nothing below asks you to cut a corner on a model or an effect.

**Models (owner, 03/10): the strongest model is `opus`. Never use `fable`, at any cost** (any Agent call you make
names `opus`, `sonnet` or `haiku` explicitly; never the `best` alias).

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
- Prefer the existing tools (`Tools/assets/glb_analyze.py`, `Tools/assets/quality_gate.py`, `Tools/models/sheet.py`,
  `Tools/art/model_sheet.py`) to new one-off scripts.

## Token hygiene (every agent; details and reasons in Docs/TOKEN_OPTIMISATION.md section 4)
- Grep tool: `files_with_matches` or `count` first, then `content` with `-C 2` and `head_limit: 30`. `wc -l` before a
  Read; files over ~300 lines are read with offset/limit. No re-reads, and no Read-back after Edit/Write.
- Never print whole: DECISIONS, CHANGELOG, `balance.json` (grep `'"id": *"<id>"'` + `cut -c1-400`), other JSON/CSV
  (Python one-liner), Unity logs (`grep -E "error CS|Exception|\[Tag\]" | tail -20`), `ls` of `Resources/Models`.
- Blender: `--background --factory-startup --python-exit-code 1`, log to `scratchpad/<lane>/x.log`, grep it.
- Git: `-q`, `status --short`, `log --oneline -5`, `diff --stat | tail -3`; `git -c core.safecrlf=false add` (no CRLF
  warning floods). robocopy `/NFL /NDL /NJH /NJS /NP`. `cut -c1-200` on long lines. Every output capped.
- Fewer turns: chain dependent shell steps in one call (`&&`); put independent calls in one message; do not poll.
- Run slow builds/renders early while the context is small, several in one call (agent cache lives 5 minutes).
- Results go to files; replies and briefs carry paths, never pasted content. Do not re-read what the brief summarised.
- Commit subject under ~72 characters, body at most 3 lines. Routine reply 5-10 lines; model/VFX up to 15.
- None of this limits model or VFX quality: gate rounds, renders and the most capable model stay (owner rule).

## Finish
- Append your decisions to `Docs/DECISIONS.md` as a new `## <prompt/wave> (lane X)` section at the end; add one line
  under `## Unreleased` in `Docs/CHANGELOG.md`.
- Commit with a short subject ("Prompt 35 wave 12 (lane C): ...") and the Co-Authored-By line from your brief. Do not
  push or merge unless told; the lead merges.
- Report in 5-10 lines (model/VFX work up to 15): commit, what changed, what failed, open questions. No file dumps.
