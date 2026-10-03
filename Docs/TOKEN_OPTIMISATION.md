# Token optimisation for Machine Brigade

How to spend fewer Claude Code tokens on this project. First version (lane C) measured on 2026-10-03 from the session
transcripts in `~/.claude/projects/c--Users-Winka-OneDrive-Documents-Tank-arena/` (3 lead sessions, 258 agents) and
from the repo. Version 2 (lane A, same day) adds the small savings (section 4), prompt caching (section 2), which
model for which job (section 5) and outside sources (section 9). Numbers marked *measured* come from a static scan of
the 263 transcript files (1.3 GB) and of the repo; nothing was run in Unity.

## 0. The owner's rule comes first

**Detail work is not a place to save (owner, 03/10):** "đối với các task cần sự chi tiết cao như làm model, và các
hiệu ứng thì không cần tiết kiệm token, tôi muốn chất lượng cao nhất có thể". Building or fixing models and visual
effects (VFX, explosions, smoke, warning rings, wrecks) gets the highest quality possible: more gate rounds, looking
at renders, the most capable model, bigger agent budgets.

Everything below applies to **routine work only**: merges, docs, exports, status replies, small fixes, bookkeeping.
Where a tip touches detail work, it changes only *how* the work is packaged (fresh context, capped logs, quiet
flags), never how many rounds, renders or checks the work gets, and never which model does it.

## 1. Where the tokens go

How billing works: every tool call is one API request that re-sends the whole conversation so far (mostly from the
prompt cache, section 2). So the cost is roughly **context size x number of turns**, not the size of what you read
once. Anything printed into the context is paid again on every later turn of that session.

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

Files agents keep touching (rough tokens = bytes / 4):

| File | Size |
|---|---|
| `Docs/DECISIONS.md` | 18,647 lines, 1.72 MB (~430k tokens), 240 `##` sections, median section 5.4 kB |
| `Docs/CHANGELOG.md` | 2,082 lines, 236 kB (~59k) |
| `Assets/MachineBrigade/Resources/Data/balance.json` | 490 kB (~120k); `campaign.json` 264 kB; `maps/swamp_long.json` 193 kB |
| `Docs/balance/manifest_v2.json`, `Docs/stuck-report/data/**.csv` | 262 kB; CSVs up to 435 kB |
| `Docs/prompts/` | 45 files, 824 kB; largest `prompt28_vi.txt` 45 kB, `requests_vi.md` 31 kB |
| `Assets/MachineBrigade/Resources/Models/` | 1,036 entries (518 GLBs + metas); a bare `ls` prints ~21 kB (~5k tokens) |
| `Tools/blender/build_assets.py` | 445 lines, 27 kB (248 files in `Tools/blender/`) |
| `Docs/models/rebuild/` (tracked) | 273 MB; `Docs/export/` now 28 tracked files, 2.8 MB |
| Unity logs (`MachineBrigade-runner/Builds/*.log`, 18 files) | 45 kB to 2.1 MB each; `effect_shots.log` 7,375 lines / 583 kB; `scan*.log` ~85 kB |
| `handoff_tools/compile.log`, `logs/build_win.log` | 1,595 lines / 336 kB (~84k); 13,567 lines / 873 kB (~218k) |
| `CLAUDE.md` | 41 lines, 9 kB (loaded into every session and agent) |

### Small sinks found in the transcripts (measured, v2)

| Habit | Measured | What it costs |
|---|---|---|
| Git CRLF warnings ("LF will be replaced by CRLF") | 6,243 lines in 196 of 263 transcripts, 568 kB (~142k tokens) | each line then rides along every later turn |
| Bash vs the Grep tool | 36,001 Bash calls, 273 Grep calls; only 79 Grep calls used `output_mode` or `head_limit` | raw `grep -rn` prints every hit |
| Read with `offset`/`limit` | 1,010 of ~1,500 text Reads (68 %) | the rest read whole files |
| Parallel tool calls | 3,217 of 42,459 tool-calling messages (7.6 %) had more than one call | each extra message = one more full-context turn |
| Re-read right after an Edit/Write | 224 Reads of a file within 3 calls of editing it | pure waste: the tool already confirms |
| `cat` of a JSON/CSV without a pipe | 168 calls | balance.json alone is ~120k tokens |
| `ls` of the Models folder | 123 calls; 7 printed 100+ GLB names | ~5k tokens each |
| Bash results over 20 kB | 236 calls, 5.5 MB together (6.4 % of all Bash output) | most were logs or whole files |
| Blender runs | 789 runs: 788 used `--background`, 717 piped to grep/tail, 131 logged to a file, 92 used `--factory-startup`; median output 394 chars, p90 1.9 kB, max 27 kB | already good; finish the job (rule S6) |
| Agent resumes | 157 SendMessage calls vs 262 Agent spawns | resuming beats re-briefing (rule S20) |
| Web research | 505 WebSearch + 323 WebFetch calls, 1.8 MB of results | broad fetch prompts return whole pages |
| Bash result size | median 1.0 kB, p90 6.2 kB, p99 18 kB | the long tail is what matters |

## 2. Prompt caching: how it works here

Facts from the official docs (sources [1], [2], [3]):
- Each request is matched against recently processed content **from the start (the prefix)**. The match is exact: a
  change anywhere in the prefix reprocesses everything after it. There is no per-file caching. Claude Code orders the
  request as system prompt + tools, then project context (CLAUDE.md, memory), then the conversation.
- Price (API reference [3]): cache reads ~0.1 x the normal input price (the page lists lower read multipliers for the
  newest models; not re-checked); cache writes 1.25 x for the 5-minute TTL, 2 x for the 1-hour TTL. A cache hit
  refreshes the TTL for free.
- TTL in Claude Code [2]: on a subscription within plan usage the **main conversation gets 1 hour**; subagents,
  compaction and other side requests get **5 minutes**. On usage credits or an API key the main conversation drops to
  5 minutes. Settings `promptCacheTtl` / `subagentPromptCacheTtl` (env `CLAUDE_CODE_PROMPT_CACHE_TTL`,
  `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL`) choose `5m` or `1h` (needs v2.1.242+).
- What breaks the cache [2]: switching models (`/model`, or a skill whose frontmatter names another model), changing
  effort on most models (Opus 5.5, Sonnet 5.5 and Fable 5.1 keep it on a subscription/API key), turning on fast mode,
  connecting/removing an MCP server when tools are not deferred, enabling a plugin with MCP servers, denying a whole
  tool without tool search, `/compact`, Claude Code dropping a batch of old images when a request has too many, and a
  Claude Code upgrade (first turn after restart).
- What keeps it [2]: editing repo files (a reminder is appended, earlier reads are not changed), editing CLAUDE.md
  mid-session (it also does **not apply** until `/clear`, `/compact` or a restart), permission-mode changes, skills,
  `/recap`, `/rewind`, and spawning a subagent (the parent prefix is untouched).
- A subagent builds its own cache from scratch (different system prompt and tools); a resumed subagent can read the
  cache its first run warmed, if still alive [2]. `/usage` shows a `Prompt cache (main)` line with hit rate and misses
  (v2.1.251+) [1].

What it means for the lead and the lanes:
1. **Idle gaps are expensive at large context.** A 500k lead left idle over an hour (or 5 minutes on usage credits)
   pays one full cache write on its next turn: 500k x 1.25-2 instead of 500k x 0.1, i.e. ~12-20 normal turns. When the
   owner comes back after a long break to a big lead, a fresh session from the handoff (30-50k) is cheaper.
2. **Agents live on a 5-minute TTL.** Any single tool call longer than 5 minutes (a long Blender batch, a render
   wave) means the agent's next turn re-writes its whole context. Run the long steps early, while the context is
   small; put several long steps in one call rather than many calls that each cross 5 minutes.
3. **Never switch `/model` or effort in the lead mid-session** (on models that split the cache). Pick at session
   start. To use another model, spawn an agent with the `model` option: its cache is separate anyway.
4. **Do not edit CLAUDE.md or MEMORY.md expecting the lead to see it**; it loads at the next `/clear` or session. It
   costs no cache, it just does not apply.
5. **Abandoned path: `/rewind`, not `/compact`.** Rewinding truncates to a prefix that is already cached; compaction
   builds a new one and its summary request reads the whole history [2].
6. **Images:** a lead that keeps reading renders eventually hits the per-request image limit; Claude Code then drops
   the oldest batch and the conversation from that point is reprocessed [2]. Another reason the lead looks at few
   pictures.
7. MCP tools are deferred by default, so the claude.ai connectors in this setup (Asana, Notion, Figma, Stitch...) cost
   only their names and server instructions; disable unused ones in `/mcp` at session start, not mid-session [1].

## 3. Rules for the lead

### Spawn an agent or do it inline
- Inline: you know the exact file and lines, the change is under ~20 lines, and it needs at most ~5 tool calls.
- Agent: anything that reads more than a few files, writes a builder, renders, or iterates. The agent starts at ~32k
  context instead of the lead's 300-900k, so the same 50 tool calls cost 6-20 x less there.
- Never write long files from the lead (Write was ~21 % of the lead's context). Hand them to an agent.
- One agent per task; agents do not spawn sub-agents. (Claude Code allows nesting up to 3 levels by default [4];
  `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` in settings would enforce our rule.)

### Briefs and reports
- Briefs start with **"Read Docs/AGENT_RULES.md first."** and then give only the task: branch, paths, ids, checks,
  report format (~1.5k characters instead of the old median 3.5k). Pass inputs **by path**, never pasted.
- Always pass `model` explicitly on the Agent call (section 5); do not rely on the inherited default.
- Ask for 5-10 lines for routine work, 10-15 for model/VFX waves. Details go into the repo (WAVE report, DECISIONS)
  where they can be grepped later.
- Read the handback, not the files behind it. Do not open a report the handback already summarised; spot-check by
  grep, not by Read.

### Renders and images
- Detail work: the model/VFX agent looks at its own renders as much as the work needs (owner rule). The lead does not
  re-look at the same renders; it trusts the gate numbers and the agent's report, and looks only at what the agent
  flags or what the owner asks about.
- Routine checks: numbers first (card luma from `wave_cards.sh`, `glb_analyze`, `quality_gate`). When a picture is
  needed, one contact sheet (`Tools/models/sheet.py`, `Tools/art/model_sheet.py`) at small size (about 256 px tiles,
  sheet at most ~1024 px wide) instead of N full-size files. Image tokens grow with pixel area (~w x h / 750 per the
  vision docs [6]; not re-checked 03/10).
- Batch card renders: one `render_wave.sh <wave> <ids...>` per wave, not per model.

### Merges (routine only; merges and renders stay with the lead)
- Merge lanes in batches with `merge_lane.sh ... 2>&1 | tail -15`. It already silences the merge, resolves the known
  conflicts and prints only UNRESOLVED / MARKERS LEFT / 1 compile line / 10 error lines / 2 CatalogCheck lines. Fix
  by hand only what it reports. Do not follow it with `git log -p` or a full `git diff`; use `--stat | tail -3`.

### Memory, handoff and fresh sessions
- `MEMORY.md` stays an index of one-line pointers (under ~5 kB); details live in the linked files.
- `HANDOFF_machine_brigade.md` holds "how to work" and "state now"; update the state before each fresh start.
- **Start a fresh session** when the lead's context passes ~200-250k, at every wave or prompt boundary, after a
  session-limit stop, after an idle gap longer than the cache TTL at large context (section 2), and after two failed
  corrections on the same problem (the best-practice guide [5]: a clean session with a better prompt beats a long one).
- Before starting fresh: commit, update memory's resume file and the handoff state (5-10 lines), then `/clear`
  (`/clear` itself costs nothing [1]).
- Side questions from the owner that need no follow-up: `/btw` keeps the answer out of the history [5].

### Session-limit stops
- Keep agents short (section 7), so a stop loses at most one small agent's work; agents commit per model or step.
- After the reset, **resume the stopped agent with SendMessage** ("continue from where you stopped"): it keeps its full
  history [4]. A fresh brief re-reads AGENT_RULES, the specs and the files it already had. Only if the agent was an
  Explore/Plan agent (they cannot be resumed [4]) or its context was already huge, start a new small one.

## 4. Rules for agents

### Big rules (v1)
1. Grep before Read; then Read with offset/limit.
2. Never read `Docs/DECISIONS.md`, `Docs/CHANGELOG.md`, `Docs/export/**` or `Docs/models/REBUILD_LIST.md` whole.
3. No paging with `sed -n 1,400p` (10 % of agent tokens): grep the symbol, read 30-80 lines around it.
4. Cap every command's output; grep logs, never print them.
5. No re-reads of a file already in context.
6. Edit, do not rewrite; Write only for new files.
7. Long one-off scripts go in a scratchpad file, not pasted inline again and again.
8. Batch independent tool calls in one message.
9. Use the existing tools: `merge_lane.sh`, `render_wave.sh`, `wave_cards.sh`, `sync.sh`, `compile.sh`,
   `Tools/assets/glb_analyze.py`, `Tools/assets/quality_gate.py`, `Tools/models/sheet.py`, `Tools/art/resolve_merge.py`.
10. Short replies.

### Small rules (v2): 24 habits, each cheap, together large
Searching and reading
- **S1 Grep tool modes.** Use the Grep tool, not `grep -rn` in Bash. Start with `output_mode: "files_with_matches"`
  (where?) or `"count"` (how many?), then `"content"` with `-n`, `-C 2` and `head_limit: 30` on one file or glob.
- **S2 Size before reading.** `wc -l file` or `grep -c pattern file` first; anything over ~300 lines is read with
  `offset`/`limit` (`build_assets.py` 445 lines, `mb_p35_*.py` builders, C# systems).
- **S3 No whole JSON/CSV.** `balance.json` is JSON with `//` comments and one entry per line, so plain `json.load`
  fails; the cheapest look-up is `grep -n '"id": *"light_tank"' Assets/MachineBrigade/Resources/Data/balance.json |
  cut -c1-400`. For structure use the project's loader:
  `python -c "import sys,json;sys.path.insert(0,'Tools/balance');import jsonc_edit as j;d=json.loads(j.strip_comments(open('Assets/MachineBrigade/Resources/Data/balance.json',encoding='utf-8').read()));print(list(d))"`
  (top level: `vehicles`, `weapons`, `supports` arrays with `id`, plus `economy`, `ai`, ...). Plain JSON files:
  `json.load` then print one key, `[:1500]`. CSV: `python -c "import csv;r=list(csv.reader(open(p)));print(len(r),r[0])"`.
- **S4 No listing of big folders.** Not `ls Resources/Models` (1,036 entries). Use `ls ... | wc -l`,
  `ls ... | grep light_tank`, or Glob with a pattern (`**/Models/*airborne*.glb`).
- **S5 Unity logs: grep, then tail.** `grep -E "error CS|Exception|\[CatalogCheck\]|\[Tag\]" Builds/x.log | tail -20`.
  Even `tail -100` of a Unity log is ~10 kB of shader and import noise. Never `cat` one (up to 2.1 MB).
- **S6 Blender quiet.** `blender.exe --background --factory-startup --python-exit-code 1 --python x.py -- args
  > scratchpad/<lane>/x.log 2>&1; grep -E "Traceback|Error|saved|tris" scratchpad/<lane>/x.log | tail -15`.
  `--factory-startup` skips user prefs and add-ons (bundled default add-ons such as the glTF exporter stay on; check
  once that a build still exports before relying on it). Exit code 1 on a Python error lets `&&` chains stop.
- **S7 No CRLF warning floods.** `git -c core.safecrlf=false add ...` (or `... 2>&1 | grep -v "will be replaced by"`).
  6,243 warning lines were printed in these sessions. `merge_lane.sh` already uses `-c core.autocrlf=false`.
- **S8 Quiet git.** `git commit -q`, `checkout -q`, `fetch -q`, `push -q`, `merge -q`; `git status --short | head -20`;
  `git log --oneline -5`; `git diff --stat | tail -3`; `git show --stat HEAD | tail -5`. Use
  `GIT_LFS_SKIP_SMUDGE=1` when switching branches whose GLBs you do not need; `git lfs checkout >/dev/null 2>&1`.
- **S9 Quiet copies.** robocopy with `/NFL /NDL /NJH /NJS /NP` and `> /dev/null`, checking only the exit code (as
  `sync.sh` does; codes 8+ are failures). `cp -r` and `mv` without `-v`.
- **S10 Long lines.** `cut -c1-200` on anything that may hold minified JSON or long paths.
- **S11 Narrow web fetches.** WebFetch returns an answer to its `prompt`, so ask a narrow question ("only the TTL and
  prices") rather than "summarise the page"; a broad prompt returns most of the page.

Writing and passing results
- **S12 Results by path.** Write tables, logs and long findings to a file (repo report or `scratchpad/<lane>/`) and
  reply with the path and 1-3 numbers. Never paste a file's content into a reply or a brief.
- **S13 Tools print summaries.** New Python tools print at most ~15 lines (counts, failures) and write details to a
  file. Prefer `--quiet` modes where tools have them.
- **S14 Short commit messages.** Subject under ~72 characters ("Prompt 35 wave 12 (lane C): ..."), body at most 3
  lines plus the Co-Authored-By line. Long bodies come back in every later `git log`.
- **S15 Short replies.** Routine agents: 5-10 lines (commit, counts, failures, questions). Model/VFX: up to 15.

Fewer turns
- **S16 One call, several steps.** Chain dependent shell steps in one Bash call:
  `git add -A Docs && git -c core.safecrlf=false commit -qm "..." && git log --oneline -1`. Each extra call
  re-sends the whole context.
- **S17 Parallel calls.** Independent reads, greps and checks go in one message (only 7.6 % of messages did this).
- **S18 No verify reads.** After Edit/Write, do not Read the file back (224 times in these sessions); the tool fails
  loudly if the edit did not apply. Re-read only when a later step really needs other lines.
- **S19 No re-reading what the brief summarised.** If the brief already gives the lines, numbers or decisions, do not
  open the report or DECISIONS section again to "confirm".
- **S20 Resume, do not re-brief.** (Lead) After a session-limit stop or a follow-up question, SendMessage the same
  agent; it keeps its context [4].
- **S21 Load deferred tools in one go.** `ToolSearch` with `select:A,B,C` instead of one call per tool.
- **S22 Do not poll.** Background agents and long commands notify on completion; no `sleep` loops or repeated
  Monitor/status checks (160 Monitor calls in these sessions).
- **S23 Long steps early.** Run the slow Blender batch or render while the context is small (5-minute agent cache,
  section 2), and put several slow steps in one call.
- **S24 Pictures small and few.** Agents doing routine checks read one contact sheet, not N renders; model/VFX
  agents look as much as the work needs (owner rule) but still prefer sheets for overviews.

## 5. Which model for which job

The Agent tool's `model` option takes `opus`, `sonnet`, `haiku` or `fable`. What the official docs say ([7], [4]):
- `fable`: "for your hardest and longest-running tasks"; holds long sessions without losing the thread; give it the
  outcome, not the steps; verifies its own work. The `best` alias resolves to Fable where available, otherwise Opus,
  so **Fable is the most capable model in this setup, Opus the fallback**.
- `opus`: "complex reasoning tasks", architecture decisions.
- `sonnet`: "daily coding tasks"; the cost guide [1] says it handles most coding well and costs less than Opus.
- `haiku`: "fast and efficient ... for simple tasks"; the cost guide suggests `model: haiku` for simple subagents.
- Opus 5.5, Sonnet 5.5 and the Fable models always use extended thinking (billed as output) [1]; lower effort is
  the lever there, not turning thinking off.
- Precedence: the per-call `model` beats the agent definition, then `CLAUDE_CODE_SUBAGENT_MODEL`, then the session
  model [4]. Built-in Explore and Plan agents inherit the session model unless told otherwise.

**The owner's rule comes first:** models (Blender building, rebuilds, specs), visual effects and everything that
decides how they look use the most capable model (`fable`, else `opus`) with no token saving.

| Job in this project | Model | Why |
|---|---|---|
| Model rebuild waves, new builders, kit parts, spec writing/research for models | `fable` (else `opus`) | Owner rule; long multi-model runs with many gate rounds are exactly Fable's "long-running" case |
| VFX / effects (explosions, smoke, rings, wrecks), card/render look | `fable` (else `opus`) | Owner rule; visual judgement on renders |
| Gameplay / Sim bug fixes, AI and tactics, balance design | `fable` or `opus` | Root-cause work across systems; a wrong fix costs more than the tokens |
| Code-reading audits, export passes (`Docs/export`), doc generators, PDF build fixes | `sonnet` | Mechanical but needs reading code correctly |
| Writing tests (not running them) | `sonnet` | Follows existing test patterns; the lead or a reviewer checks |
| Routine docs, CHANGELOG/DECISIONS bookkeeping, log summaries, report formatting | `haiku` | Simple text work; spot-check its first runs (not yet tried on this repo) |
| File moves, archive passes, simple greps and counts | `haiku` | Deterministic steps; mistakes show in `git status` |
| Broad read-only searches ("where is X used") | Explore agent, `model: haiku` or `sonnet` | Read-only, skips CLAUDE.md and git status so it starts cheaper [4]; cannot be resumed |
| Merges, renders, owner-facing image checks | the lead itself | `merge_lane.sh` / `render_wave.sh` are one call each; the lead needs the outcome in its own context |
| The lead session | `opus` (owner picks at session start) | Judgement, owner dialogue, reviewing reports; `fable` for a long detail-heavy push if the owner wants it; never switch mid-session (cache) |

Notes:
- Do not set `CLAUDE_CODE_SUBAGENT_MODEL` to a cheap model globally: one forgotten override would put a model wave on
  a weaker model. Pass `model` on every Agent call instead.
- When a cheap model fails twice on a task, move it up one step rather than re-trying (a failed run costs more).
- Fable and Opus prices differ from Sonnet and Haiku; check the `/model` picker or the pricing page before assuming
  a ratio (not recorded here).

## 6. Repo changes that save tokens (proposals; not done here)

| Change | Saving | Risk |
|---|---|---|
| A. Split DECISIONS.md into `Docs/decisions/` + INDEX | removes the 430k blow-up risk, faster greps | merge tools special-case the file |
| B. `Docs/STATE.md` (one page, rewritten each wave) | 20-50k per fresh session / new agent | goes stale |
| C. Archive old prompts and wave reports (`git mv`) | fewer grep hits | links; check `Tools/docs/build_doc.py` paths |
| D. `.ignore` for `Docs/models/rebuild/`, `Docs/doc-images/`, `Library/`, old export runs | large when a grep hits them | none |
| E. Scripts: `wave_check.sh <ids>`, `lane_status.sh`; every script prints at most ~15 lines, full logs to `handoff_tools/logs/` | 5-20 tool calls per wave at lead context | script bugs |
| F. `Docs/models/WAVE_BRIEF_TEMPLATE.md` | ~2k lead tokens per brief, fewer missed rules | none |
| G. Trim CLAUDE.md (device notes to `Docs/DEVICE_NOTES.md`) | ~1.5k per turn of every session; the guide [5] says prune what Claude would not get wrong without it | lose a rare note |
| H. A PreToolUse hook that appends `2>&1 \| grep -v "will be replaced by"` to git commands (pattern from [1]) | removes CRLF floods for everyone | a hook bug blocks git; test on one lane first |
| I. Custom agents in `.claude/agents/` (`model-builder` with `model: fable`, `routine-docs` with `model: haiku`) | the model choice is written once | needs the lead to use them |

Details for A-G are unchanged from v1: split DECISIONS between waves with no lane branch open and update
`resolve_decisions.py` / `merge_lane.sh`; STATE.md lists branch heads, open prompts, owner waits, stand-ins, last
wave; archive only after the PDF build is checked; `wave_check.sh` = py_compile + build ids + `git status` for
unintended GLBs + quality_gate, one line per model.

## 7. Prompt-35-style mass work

Prompt 35 rebuilt ~230 models in waves of 13-21 models per agent. Those agents ran 300-680 turns at up to ~960k
context; 69 % of agent tokens were spent after turn 100, re-reading earlier models' work the current model no longer
needed.

- **Smaller agents, same quality.** One agent per 4-6 models (or per family). Each model keeps every gate round and
  render it needs (owner rule); only the context resets between groups. Expected saving 40-60 % of a wave's tokens.
- **Commit per model.** A stop or a bad model then costs one model, not a wave.
- **Give exact sections** of the kit, MODEL_STANDARD and gold metrics (line ranges or a `KIT_QUICKREF.md`).
- **Specs first.** `Tools/blender/specs/<id>.json` (213 files) holds the research; fix agents read the spec, not the
  web again. Research is its own short agent that writes specs.
- **Reuse builders and the kit.** Start from the closest `mb_p35_<id>.py` and `mb_kit35.py` parts.
- **Lanes:** up to 3 in parallel; tokens scale with turns, not parallelism. The lead does not watch them.

## 8. Claude Code features that help

| Feature | Use here |
|---|---|
| `CLAUDE.md` | Loaded every turn; short and stable; edits apply only after `/clear` or a new session [2]. The guide [5] suggests keeping it under ~200 lines and moving rarely needed workflows into skills [1]. |
| Auto memory (`MEMORY.md` + files) | Standing rules and the resume point; the index stays short. |
| `/clear` | The cheapest reset (costs nothing [1]); save state first. |
| `/compact [focus]` | Mid-task shrink; its summary request reads the whole history, cheap only while the cache is warm [2]. Commit first. |
| `/rewind` | Drop an abandoned path while keeping the cached prefix [2]. |
| `/btw` | A side question whose answer never enters the history [5]. |
| `/context`, `/usage` | What fills the context; `/usage` shows cache hit rate and misses [1]. |
| Agent `model` option | See section 5. |
| `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` | Enforces "agents do not spawn agents" [4]. |
| Hooks (PreToolUse) | Filter verbose output before it reaches the context, e.g. only failing lines [1]. |
| Background agents, worktrees | Lanes in parallel without polling; already in use. |

Not sure / not claimed: a per-agent hard token cap. Enforce size by scope (models per agent).

## 9. Sources

1. Manage costs effectively (Claude Code docs): https://code.claude.com/docs/en/costs
2. How Claude Code uses prompt caching: https://code.claude.com/docs/en/prompt-caching
3. Prompt caching (Claude API docs; prices, TTL refresh): https://platform.claude.com/docs/en/build-with-claude/prompt-caching
4. Subagents (built-ins, model precedence, resume, nesting): https://code.claude.com/docs/en/sub-agents
5. Best practices for Claude Code: https://code.claude.com/docs/en/best-practices
6. Vision (image token estimate; cited from memory, not fetched 03/10): https://platform.claude.com/docs/en/build-with-claude/vision
7. Model configuration (aliases opus, sonnet, haiku, fable, best): https://code.claude.com/docs/en/model-config

All fetched 2026-10-03 except [6]. Version numbers (v2.1.xxx) are as the pages state.

## 10. One-page checklist

Before any task
- [ ] Model or VFX work? Quality first: `fable` (else `opus`), full gate rounds, renders. Skip the saving tips.
- [ ] Routine? Inline only if known file and < 5 calls; otherwise one agent with an explicit `model`.

Lead
- [ ] Brief = "Read Docs/AGENT_RULES.md first" + task, paths, ids, checks, report format; inputs by path.
- [ ] Model per section 5: fable/opus for models, VFX, Sim fixes, balance; sonnet for audits, exports, tests;
      haiku for routine docs, moves, greps; Explore (haiku/sonnet) for broad searches.
- [ ] Read the handback, not the files; no re-reading what it summarised.
- [ ] Merge in batches: `merge_lane.sh ... 2>&1 | tail -15`; `--stat` only.
- [ ] One `render_wave.sh` per wave; numbers before pictures; small contact sheets; images only owner-facing.
- [ ] No long Write calls from the lead. No `/model` or effort switch mid-session.
- [ ] Session-limit stop: SendMessage the same agent to continue; do not re-brief.
- [ ] Fresh session at ~200-250k, at a wave end, after a limit stop, after a long idle gap, after two failed fixes.

Agents
- [ ] Grep tool with files_with_matches / count first, then content with head_limit; Read with offset/limit.
- [ ] Never DECISIONS / CHANGELOG / export / balance.json whole; JSON and CSV through a Python one-liner.
- [ ] No `ls` of Models; Unity logs `grep | tail -20`; Blender `--background --factory-startup`, log to file, grep.
- [ ] Quiet git (`-q`, `--short`, `--oneline`, `--stat | tail`), `-c core.safecrlf=false`; quiet robocopy.
- [ ] One Bash call for chained steps; parallel calls for independent ones; no verify reads after edits.
- [ ] Results to files, reply with paths; commit subject < 72 chars; reply 5-10 lines (15 for model/VFX).
- [ ] Long steps early; do not poll; commit per model or step; scratch files in your own scratchpad subfolder.
- [ ] Append DECISIONS, one CHANGELOG line.

Repo (quiet moment)
- [ ] `.ignore`; split DECISIONS; STATE.md; archive; `wave_check.sh`; trim CLAUDE.md; CRLF hook; custom agents.
