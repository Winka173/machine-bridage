# Token optimisation for Machine Brigade

How to spend fewer Claude Code tokens on this project. Measured on 2026-10-03 from the session transcripts in
`~/.claude/projects/c--Users-Winka-OneDrive-Documents-Tank-arena/` (3 lead sessions, 258 agents) and from the repo.

## 0. The owner's rule comes first

**Detail work is not a place to save (owner, 03/10):** "đối với các task cần sự chi tiết cao như làm model, và các
hiệu ứng thì không cần tiết kiệm token, tôi muốn chất lượng cao nhất có thể". Building or fixing models and visual
effects (VFX, explosions, smoke, warning rings, wrecks) gets the highest quality possible: more gate rounds, looking
at renders, the strongest model, bigger agent budgets.

Everything below applies to **routine work only**: merges, docs, exports, status replies, small fixes, bookkeeping.
Where a tip touches detail work, it changes only *how* the work is packaged (fresh context, capped logs), never how
many rounds, renders or checks the work gets. Every tip marked **(routine only)** must never be applied to model or
VFX work.

## 1. Where the tokens go

How billing works here: every tool call is one API request that re-reads the whole conversation so far (mostly from
the prompt cache). So the cost is roughly **context size x number of turns**, not the size of what you read once.

| Measure | Value |
|---|---|
| Input-side tokens, all sessions | ~14.3 billion (98.7 % cache reads), output ~9.8 million |
| Agents vs lead | agents 72 %, lead sessions 28 % |
| Lead: turns, average context per turn | 8,145 turns, **492k** per turn (one session: 7,017 turns, 3.6 B tokens, 25 % of everything) |
| Agents: turns, average context per turn | 34,851 turns, **296k** per turn; median agent 116 turns, 28 M tokens |
| Agent cost after its turn 100 | **69 %** of all agent tokens (after turn 50: 85 %) |
| 13 agents with 300+ turns | 25 % of agent tokens (the 162 agents under 150 turns: also 25 %) |
| Fixed start (system prompt, tools, CLAUDE.md) | ~32k per agent turn, 11 % of agent tokens |
| Images read | 2,691 (1,806 by agents, 885 by the lead), ~1.5k tokens each, carried to the end of the session |

What fills the context (share of agent tokens, estimated as size x turns it stays in context):

| Rank | Sink | Agents | Lead (relative) |
|---|---|---|---|
| 1 | Long-lived contexts (turn count x size; the multiplier on everything below) | 69 % of cost after turn 100 | average 492k per turn |
| 2 | Bash output (paged `sed -n` reads 10 %, `grep` 4 %, `cat` 2.5 %, python 2 %, Blender logs 1.6 %) | 24 % | ~35 % |
| 3 | Fixed start per turn | 11 % | 8 % |
| 4 | Whole files written with Write (builders, reports) | 6 % | ~21 % (the lead writing files itself) |
| 5 | Commands typed (long heredocs and inline scripts) | 4 % | ~17 % |
| 6 | Images | 2 % | ~11 % |
| 7 | Read of C# / Python files | 5 % | ~7 % |
| 8 | Agent briefs and reports | < 1 % | ~2 % |
| 9 | Reading DECISIONS / CHANGELOG | 0.1 % (agents already grep) | small |

Docs agents keep touching (bytes, rough tokens = bytes / 4):

| File | Size |
|---|---|
| `Docs/DECISIONS.md` | 18,647 lines, 1.72 MB (~430k tokens), 240 `##` sections, median section 5.4 kB, largest 48 kB |
| `Docs/CHANGELOG.md` | 2,082 lines, 236 kB (~59k) |
| `Docs/prompts/` | 45 files, 824 kB; largest `prompt28_vi.txt` 45 kB, `requests_vi.md` 31 kB |
| `Docs/models/REBUILD_LIST.md` | 282 lines, 32 kB |
| `Docs/models/WAVE_*_REPORT.md` | 11 files, 116 kB |
| `Tools/blender/build_assets.py` | 445 lines, 27 kB (248 files in `Tools/blender/`) |
| `Docs/export/` (tracked) | 219 MB; three runs from 03/10, each 45-54 MB of md/json/csv text, two nearly identical |
| `Docs/models/rebuild/` (tracked) | 269 MB, 420 files |
| `CLAUDE.md` | 41 lines, 9 kB (loaded into every session and agent) |

Reading: one accidental whole read of DECISIONS costs ~430k tokens *per later turn*. A 1.5k-token image read by the
lead at 500k context is small; the 500k context each of the lead's next turns re-reads is not.

## 2. Rules for the lead

### Spawn an agent or do it inline
- Inline: you know the exact file and lines, the change is under ~20 lines, and it needs at most ~5 tool calls.
- Agent: anything that reads more than a few files, writes a builder, renders, or iterates. The agent starts at ~32k
  context instead of the lead's 300-900k, so the same 50 tool calls cost 6-20 x less there.
- Never write long files from the lead (Write was ~21 % of the lead's context). Hand them to an agent.
- One agent per task; the agent must not spawn sub-agents.

### Shared preamble instead of repeated rules
- Briefs start with **"Read Docs/AGENT_RULES.md first."** and then give only the task: branch, paths, ids, checks,
  report format. The standing rules (owner quality rule, no Unity/tests, no MaterialPropertyBlock, `Mount_Flare_*`,
  builders-dict registration plus py_compile, the substring filter, scratchpad subfolders, DECISIONS grep, decisions
  plus one CHANGELOG line, no insignia, budgets, never shrink fire) live there once.
- Saving: briefs drop from ~3.5k characters (median; p90 6.5k) to ~1.5k. Small in agents, but each brief stays in
  the lead's context for every later lead turn, and fewer rules typed means fewer missed rules.

### Short reports
- Ask for 5-15 lines: commit, counts, failures, questions. Details go into the repo (WAVE report, DECISIONS) where
  the lead can grep them later if needed.
- When an agent finishes, read its report, not its files. Spot-check by grep, not by Read.

### Renders and images
- Detail work: the model/VFX agent looks at its own renders as much as the work needs (owner rule). The lead does
  not re-look at the same renders; it trusts the gate numbers and the agent's report, and looks only at what the
  agent flags or what the owner asks about.
- Routine checks: prefer numbers (card luma from `wave_cards.sh`, `glb_analyze`, `quality_gate`) to pictures. When a
  picture is needed, one contact sheet (`Tools/models/sheet.py`, `Tools/art/model_sheet.py`) instead of N files.
- Batch card renders: one `render_wave.sh <wave> <ids...>` per wave, not per model.

### Merges (routine only)
- Merge lanes in batches with `merge_lane.sh`; let it resolve the known conflicts. Read only its last lines
  (`| tail -15`). Fix by hand only what it reports UNRESOLVED.
- Do not `git diff` whole merges into the context; use `--stat` or `--name-only`.

### Memory, handoff and fresh sessions
- Memory (`MEMORY.md` plus files) holds standing rules and the resume point; keep `MEMORY.md` an index of one-line
  pointers (it is ~3.5 kB now; keep it under ~5 kB) and put details in the linked files.
- `HANDOFF_machine_brigade.md` holds "how to work" and "state now". Update its state section before each fresh start.
- **Start a fresh session** when the lead's context passes ~200-250k, at every wave or prompt boundary, and after any
  session-limit stop. Above that size each lead tool call costs more than a whole small agent turn. The 7,017-turn
  session averaged ~500k per turn; at ~150k average the same work would have cost ~70 % less.
- Before starting fresh: commit, update memory's resume file and the handoff state (5-10 lines), then `/clear` or a
  new chat. Resuming costs ~30-50k tokens once.

### Session-limit stops
- Keep agents short (section 5), so a stop loses at most one small agent's work.
- On a stop: commit what is done (agents commit per model or per step), write the resume line, start fresh.

## 3. Rules for agents (routine reading; never a limit on detail work)

1. Grep before Read. `Grep` with `-n` and a few lines of context finds the section; then Read with offset/limit.
2. Never read `Docs/DECISIONS.md`, `Docs/CHANGELOG.md`, `Docs/export/**` or `Docs/models/REBUILD_LIST.md` whole.
3. Do not page through big files with `sed -n 1,400p` (paged reads were 10 % of agent tokens): grep for the symbol,
   then read 30-80 lines around it.
4. Cap every command's output: `| tail -20`, `| head -40`, `cut -c1-200`, `grep -c`. Blender and Unity logs: grep the
   result lines, never print the log.
5. Do not re-read a file already in context; after an Edit, trust the tool.
6. Edit, do not rewrite: change a builder with Edit; use Write only for new files.
7. Put long one-off scripts in a scratchpad file and run it, instead of pasting them inline repeatedly.
8. Batch independent tool calls in one message (one turn instead of several).
9. Use the existing tools: `merge_lane.sh`, `render_wave.sh`, `wave_cards.sh`, `sync.sh`, `compile.sh`,
   `Tools/assets/glb_analyze.py`, `Tools/assets/quality_gate.py`, `Tools/models/sheet.py`, `Tools/art/resolve_merge.py`.
10. Reply in 5-15 lines.

## 4. Repo changes that save tokens (proposals; not done here)

| Change | Saving | Risk |
|---|---|---|
| A. Split DECISIONS.md | low per turn (~1 %), removes the 430k blow-up risk and speeds greps | broken cross-references, merge tools |
| B. `Docs/STATE.md` | 20-50k per fresh session / new agent | goes stale |
| C. Archive old prompts and reports | small (fewer grep hits) | links to moved files |
| D. Keep generated output out of grep | large when it happens (a grep into 45 MB of export text) | none |
| E. Script routine steps | 5-20 tool calls per merge/wave at lead context | script bugs |
| F. Model-wave template | ~2k lead tokens per brief, fewer missed rules | none |
| G. Trim CLAUDE.md | ~1.5k per turn of every session (~0.5 %) | lose a rare note |

**A. Split DECISIONS.md.**
1. `mkdir Docs/decisions`; with a small Python script split at `## ` headings into `Docs/decisions/p01-p12.md`,
   `p13-p20.md`, `p21-p26.md`, `p27-p34.md`, `p35.md` (by the prompt number in the heading; dated sections without a
   prompt go with their date's prompt).
2. Write `Docs/decisions/INDEX.md`: one line per section (heading, file, line).
3. Replace `Docs/DECISIONS.md` with a stub: what moved where, plus a `## Current` part where new sections go.
4. Update `handoff_tools/resolve_decisions.py` and `merge_lane.sh` (they special-case `Docs/DECISIONS.md`), the
   handoff file, memory and AGENT_RULES.
5. Do it between waves with no lane branch open, or every open branch conflicts.

**B. STATE.md.** One page: current branch heads, open prompts, what waits for the owner, known stand-ins (pointer to
ASSET_DEBT), the last wave. The lead rewrites it (not appends) at each wave end. New agents and fresh sessions read it
instead of grepping the handoff, memory and DECISIONS.

**C. Archive.** Move `Docs/prompts/prompt00-30*` and finished `Docs/models/WAVE*_PLAN.md` / `WAVE_*_REPORT.md` to
`Docs/archive/` with `git mv`; leave `Docs/prompts/README.md` pointing there. Only after the PDF build
(`Tools/docs/build_doc.py`) is checked for paths it reads.

**D. Generated output.** Add a `.ignore` file (ripgrep, which the Grep tool uses, honours it) listing `Docs/export/`,
`Docs/models/rebuild/`, `Docs/doc-images/`, `Library/`. Keep only the newest export run in git (the two older 03/10
runs are 90 MB of text); older runs go to a release asset or are regenerated.

**E. Scripts.** Already good: `merge_lane.sh`, `render_wave.sh`, `wave_cards.sh`, `sync.sh`, `compile.sh`. Add:
- `wave_check.sh <ids>`: py_compile build_assets, build the ids, `git status` for unintended GLBs (substring filter),
  run quality_gate on the ids, print a 1-line-per-model table;
- `lane_status.sh`: for the three worktrees, branch, last commit and dirty count in one screen;
- every script prints at most ~15 lines and writes full logs to `handoff_tools/logs/`.

**F. Model-wave template** (`Docs/models/WAVE_BRIEF_TEMPLATE.md`): "Read Docs/AGENT_RULES.md first" + branch + ids +
spec path pattern + builder name pattern + gate command + report path + "commit per model". The lead fills the ids.

**G. CLAUDE.md.** Move emulator/device-debugging notes (about a third of it) to `Docs/DEVICE_NOTES.md` and leave a
one-line pointer. It loads into every turn of every session and agent.

## 5. Prompt-35-style mass work

Prompt 35 rebuilt ~230 models in waves of 13-21 models per agent. Those agents ran 300-680 turns at up to ~960k
context; 69 % of agent tokens were spent after turn 100, i.e. on re-reading earlier models' work that the current
model no longer needed.

- **Smaller agents, same quality.** One agent per 4-6 models (or per family: one boss, or 5 light vehicles). Each
  model keeps every gate round and render it needs (owner rule); only the context resets between groups. Expected
  saving: 40-60 % of a wave's tokens, because the average context per turn falls from ~300-500k to ~100-150k.
- **Commit per model.** A session stop or a bad model then costs one model, not a wave.
- **Cache the shared material.** The kit, MODEL_STANDARD and gold metrics are read once per agent; give the agent the
  exact sections (line ranges or a short `Docs/models/KIT_QUICKREF.md`) instead of letting it explore.
- **Specs first, cheap to read.** `Tools/blender/specs/<id>.json` already holds the research; a later fix agent reads
  the spec, not the research or web pages again.
- **Reuse builders and the kit.** Start from the closest existing `mb_p35_<id>.py` and `mb_kit35.py` parts; copy, do
  not regenerate. New shared parts go into the kit so the next wave reuses them.
- **Research in its own step.** Web research (references, dimensions) is a short separate agent that writes specs;
  the builder agents start from specs. Keeps search results out of the long builder context.
- **Lanes:** up to 3 in parallel is fine for throughput; tokens scale with turns, not with parallelism. Do not let the
  lead watch them (no polling); wait for the completion notice.

## 6. Claude Code features that help

| Feature | Use here |
|---|---|
| `CLAUDE.md` (project memory) | Loaded every turn; keep it short and stable (see 4G). |
| Auto memory (`MEMORY.md` + files) | Standing rules and the resume point; index stays short. |
| `/clear` | Start over in the same window after saving state: the cheapest reset. |
| `/compact [focus]` | Summarises the conversation to shrink the context; use when you must keep going mid-task. A summary loses detail, so commit and note state first. |
| `/context` | Shows what fills the context; check it before deciding to start fresh. |
| Agent tool `model` | `opus` for model building, VFX, kit design, visual review and hard debugging (owner rule: never downgrade these). `sonnet` for routine mechanical work: doc edits, CHANGELOG/DECISIONS bookkeeping, export reruns, merges on a known recipe. `haiku` for simple lookups or summaries; I have not measured its quality on this repo, so try it on a docs task first. |
| Custom agents (`.claude/agents/*.md`) | A `routine-docs` agent with `model: sonnet` and limited tools; a `model-builder` agent with `model: opus` that loads AGENT_RULES. |
| Background agents | The lead keeps working (or stays idle) while lanes run; do not poll them. |
| Worktrees (`isolation: "worktree"` or the existing art/art2/art3) | Parallel lanes without file clashes; already in use. |
| Prompt caching | Automatic. Cache reads are much cheaper than fresh input but still the bulk of the total here. Long idle gaps may expire the cache so the next turn re-writes it; I am not sure of the exact lifetime on this plan. |

Not sure / not claimed: a per-agent hard token cap. If none is available, enforce size by scope (models per agent).

## 7. One-page checklist

Before any task
- [ ] Detail work (model, VFX)? Then quality first: strongest model, full gate rounds, renders. Skip the saving tips.
- [ ] Routine? Then save: inline only if known file and < 5 calls, else one agent.

Lead
- [ ] Brief = "Read Docs/AGENT_RULES.md first" + task, paths, ids, checks, report format.
- [ ] Ask for a 5-15 line report; read the report, not the files.
- [ ] `opus` for models/VFX; `sonnet` only for routine bookkeeping.
- [ ] Merge in batches with `merge_lane.sh`, `| tail -15`.
- [ ] Render a wave in one `render_wave.sh` call; numbers before pictures on routine checks.
- [ ] No long Write calls from the lead.
- [ ] Context past ~200-250k, a wave ended, or a limit stop: commit, update memory + handoff state, fresh session.

Agents
- [ ] Grep, then Read with offset/limit; never DECISIONS/CHANGELOG/export whole.
- [ ] Cap output (`tail`, `head`, `cut -c1-200`); grep logs.
- [ ] Edit rather than rewrite; no re-reads; batch tool calls.
- [ ] Commit per model or per step; scratch files in your own scratchpad subfolder.
- [ ] Append DECISIONS, one CHANGELOG line, short report.

Mass work
- [ ] 4-6 models per agent; research agent writes specs first; reuse builders and kit.

Repo (when there is a quiet moment)
- [ ] `.ignore` for generated output; split DECISIONS; STATE.md; archive old prompts; `wave_check.sh`; trim CLAUDE.md.
