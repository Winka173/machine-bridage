# Machine Brigade: handoff for a Claude Code cloud session (prompt 28, Sim part)

Written 2026-10-02 by the local lead. Read this file first, then `Docs/prompts/prompt28_vi.txt`.

## What this project is

Machine Brigade is a Unity 6000.6.3f1 URP mobile RTS, vehicles only. Gameplay runs in a deterministic 20 Hz `SimWorld`
(C#, `Assets/MachineBrigade/Scripts/Sim`, assembly `MachineBrigade.Sim`, `noEngineReferences: true`: no UnityEngine).
The view, UI (UI Toolkit, "Field Command" kit) and editor tools live in `Scripts/Game` and `Scripts/Editor` and need
Unity. Data: `Assets/MachineBrigade/Resources/Data/balance.json` (JSON with comments; edit it with
`Tools/balance/jsonc_edit.py` style tools, keep comments) and `campaign.json`. Text tables are C# (English + Vietnamese).

## Your job in the cloud

Prompt 28 (AI redo, tactics system, in-battle economy) in the **Sim only**. Source data:
`Docs/ai/Machine_Brigade_AI_Research.xlsx` (v2, 20 sheets). The owner agreed to this split:

| Part of prompt 28 | Where |
|---|---|
| Python generator reading the xlsx into balance.json (like `Tools/balance/import_xlsx.py` of prompt 25) | **cloud** |
| A World Model, L parameter frame (values in balance.json), N determinism | **cloud** |
| B AI general, C squad layer, D unit layer, G anti-stuck / anti-idle | **cloud** |
| E tower targeting modes and F boss behaviour types: the Sim logic | **cloud** |
| H tactics and I economy: the Sim logic and data (no UI) | **cloud** |
| K difficulty: the Sim side | **cloud** |
| L.3 parameter sweep tool, O the Sandbox scenario tests: write them, **do not run them** | **cloud** |
| J AI viewer overlays, H.4/H.6/B.7/E.1 UI (tactic picker, HUD switch button, hint line, tower mode), O.6 screenshots, localization screens | local (later) |
| CatalogCheck, the EditMode suite, every sim/sweep/measure run | local, only when the owner allows |

Order: prompt 28's passes 1-5, Sim parts only (pass 1: A, L, N and the generator; pass 2: B, C; pass 3: D, G; pass 4:
E, F; pass 5: H, I, K). Pass 6's measuring waits for the owner.

## Rules (the owner's; they override prompt 28 where it asks for runs)

1. **Save tokens first.** At most one sub-agent at a time; grep and read line ranges, never whole big files
   (`Docs/DECISIONS.md` is >13k lines: grep its headings). Short replies.
2. **No tests, sims, sweeps or measurements** until the owner says so. Prompt 28's "chạy đủ test sau mỗi lượt" means:
   write the tests and a compile check, do not run them. Allowed: a compile check of the Sim (below), the Python
   generator on the xlsx.
3. **Reply to the owner in Vietnamese; write code, comments and docs in English.** Match the surrounding code style.
4. **Record every decision with its reason** in `Docs/DECISIONS.md`: append new sections at the END, headed
   `## 28 <pass> (cloud, <date>)`. Ask the owner only real choices. Prompt 28 says to work autonomously.
5. **Save every owner message** verbatim and dated at the end of `Docs/prompts/prompt28_vi.txt` under
   "YÊU CẦU LẺ GẮN VÀO PROMPT NÀY" before acting on it.
6. **CHANGELOG:** one entry per pass under `## Unreleased (feature/visual-overhaul)` in `Docs/CHANGELOG.md`.
7. **Git:** work on branch `cloud/p28-sim` made from `origin/feature/visual-overhaul`; commit and push each verified step
   to `origin cloud/p28-sim`. Never push to `main` or `feature/visual-overhaul` (the local lead merges). Commit messages
   end with the attribution line your environment gives.
8. **Stay inside** `Scripts/Sim`, `Assets/MachineBrigade/Tests/EditMode` (new tests), `Tools/` (Python, the compile
   project), `Resources/Data/balance.json` and `Docs/`. If the Sim needs a Game/UI/Editor hook, do not write Unity code
   blind: list it in `Docs/ai/LOCAL_TODO.md` (file, what, why) for the local session. Never edit `.meta` files by hand;
   a new `.cs` file needs no `.meta` (Unity makes it locally).
9. **Determinism (prompt 28 N):** all randomness and tie-breaks through the sim's seeded RNG; no `System.Random`,
   `DateTime`, `Dictionary` iteration order or float-order hazards in decisions. Read how `SimWorld` does RNG first.
10. **Do not change the existing balance numbers** outside prompt 28's new AI/tactics/economy parameters. Every
    balance.json change must keep CatalogCheck passing; you cannot run it, so list the changed keys in the pass's
    DECISIONS section so the local lead runs it.

## Setup and compile check (cloud)

- Clone without the 400 MB of LFS models: `GIT_LFS_SKIP_SMUDGE=1 git clone ...` (the Sim needs no LFS file).
- Install the .NET SDK if missing. Make a throwaway project outside `Assets` (e.g. `Tools/simbuild/Sim.csproj`,
  `netstandard2.1`, `LangVersion 9.0`, `<Compile Include="../../Assets/MachineBrigade/Scripts/Sim/**/*.cs" />`,
  `Nullable disable`, `AllowUnsafeBlocks` only if the Sim already uses it) and run `dotnet build` as the compile check.
  Commit that project (it is a tool). Unity 6 compiles C# 9: do not use newer language features.
- The EditMode tests reference Unity's NUnit; compile them only if a plain NUnit reference makes them build, else
  leave them to the local compile.

## Where things are (verify with grep; do not re-discover the whole repo)

- Sim AI today: `Scripts/Sim/AI/` (`ConquestAi*.cs`: AI buying and counters of prompt 13 + the sized-slot addition;
  `TacticalAi.cs`). Reuse them (prompt 28 "Phụ thuộc").
- Other systems prompt 28 reuses: `Scripts/Sim/Combat` (ammo and reload of prompt 13, facing armour of prompt 15,
  splash and two-layer blasts of prompt 26), `Movement` and `Navigation` (the stuck detector of prompt 12),
  `Events` + `SimWorld.Events.cs` (mission events and text dialogue of prompt 23), `SimWorld.Commanders.cs`
  (commanders and general personalities of prompt 22), `Sandbox` + `SimWorld.Sandbox.cs` (the Sandbox of prompt 21),
  `Bosses`, `Economy`, `Modes`, `Content` (the catalog and balance.json parsing).
- Earlier xlsx importers to copy the style from: `Tools/balance/import_xlsx.py`, `p26_ab.py`, `p26_cd.py`.
- Design decisions so far: `Docs/DECISIONS.md` (grep "13", "22", "23", "26AB", "26CD", "26E" for the systems above).
- Every owner prompt: `Docs/prompts/` (index `README.md`).

## Known facts that save you time

- The runtime keeps a model node as a separate part only if it is named `Part_<letters>[.NNN]` (view side; not your
  concern unless the Sim names parts).
- Stand-in models are deliberate (`Docs/ASSET_DEBT.md`); some list AI behaviour that prompt 28 owns: Stymphalos's swarm
  (`Part_drone`..`.007`), Cerberus's coupling break (`Part_tractor`/`_middle`/`_trailer`), Hydra's six FPV drones,
  Ixion's mines (`Point_mines`), the ground drone carrier's minions (`Minion_1..3`), Monster's track break
  (`Part_track`..`.003`), Gungnir's line warning. Do them in the Sim where prompt 28 F covers them, else leave them.
- Known old test failure: `EveryUnitHasArmourLevelsAndEveryWeaponAPenetrationAndAForm` fails on
  `turret_gun_120_long: a penetration 0-4` (data; not yours).

## When you stop

Push, then write a short state note at the end of this file (`## Cloud state <date>`: branch head, passes done, what
waits for the local session, the balance.json keys changed) so the local lead can merge and continue.

## Cloud state 2026-10-02

- Branch `cloud/p28-sim`, head: see `git log origin/cloud/p28-sim -1` (the commit after "Prompt 28 pass 1 (Sim)").
- Done: pass 1 Sim part (A World Model, L frame + L.3 sweep tool, N per-layer RNG, the xlsx generator). DECISIONS "28 1".
- Compile check: `dotnet build Tools/simbuild/Sim.csproj` clean (Sim only; tests are not compiled in the cloud).
- Waits for the local session: CatalogCheck and EditMode suite (new `WorldModelTests`; `AiParamSweep` is Explicit),
  the hooks in `Docs/ai/LOCAL_TODO.md`, J viewer.
- balance.json keys added: `ai.world.*`, `ai.params.*` (21), `ai.economy.*` (generated block before `"generals"`); no
  existing value changed.
- Next: pass 2 (B commander, C squads) reading `world.Intel` and `Catalog.Ai`.

## Scope widened by the owner (2026-10-02, local lead): "cái gì đưa được cứ đưa"

Merged locally after pass 1 (feature/visual-overhaul 63a34f9): pass 1 compiled in Unity with 0 errors, CatalogCheck OK
(241 vehicles, 371 weapons); the ModeSessions hook of LOCAL_TODO is done. Before pass 2, `git merge origin/feature/visual-overhaul`
into `cloud/p28-sim`. On top of the Sim passes 2-5, the cloud may now also do (still no runs):
- **Text tables:** new EN + VI strings for tactics (names, core behaviour, strong/weak when, counters, unlock hints),
  HUD hints (B.7), tactic-switch lines (H.8), tower targeting modes (E.1), fire stances (H.9), the upkeep factor and
  pressure tiers (I.2, I.6). Put them in new pure-C# files beside `Scripts/Game/Hud/CommanderText.cs` and copy its
  pattern exactly (no Unity API in them). The local compile catches mistakes.
- **Save data in the Sim:** the last tactic per mode (H.14) and per-squad tactics (H.10) as Sim/Content data, if the
  save layer is Sim-side (grep first); else list it in LOCAL_TODO.
- **AI viewer data (J.2-J.4):** the "VÌ SAO" records (chosen action + score, top 3 plus and top 2 minus factors,
  runner-up), the decision-churn counters and the replay decision log, all in the Sim; the local session draws them.
- **Sandbox scenario tests (O.4)** and the 5-seed campaign/tactic-fingerprint harness (H.3, O.5) as EditMode tests,
  marked Explicit; written, not run.
- **Design docs (O.7):** `Docs/ai/AI_DESIGN.md`, `Docs/ai/TACTICS.md`, `Docs/ai/ECONOMY.md` (English, short), and the
  exporter for `Docs/ai/Machine_Brigade_AI_Research_applied.xlsx` (run it with the initial values; tuned values come
  after the owner allows the sims).
Still local: drawing J's overlays, the tactic picker and HUD switch button (UI Toolkit), tower mode UI, screenshots,
the EditMode suite and every measure.

## Cloud state 2026-10-02 (passes 2-5 and the widened scope)

- Branch `cloud/p28-sim` (merged `origin/feature/visual-overhaul` at 212383f first); head: the commit "Cloud state after
  prompt 28 passes 2-5". Sim compile check clean (`dotnet build Tools/simbuild/Sim.csproj`); nothing was run.
- Done, Sim side: pass 2 (B general `AiCommander`, C `SquadLayer`, decision log), pass 3 (D unit layer, G anti-stuck),
  pass 4 (E tower modes and rules, F boss behaviour types), pass 5 (H tactics, I economy, K difficulty). DECISIONS
  "28 2" to "28 5" and "28 extras".
- Done, widened scope: `Game/Hud/TacticText.cs` (+ 3 lines in `Strings.cs`), Sandbox side tactic, "VÌ SAO" for
  general, squads and units, churn counters, replay log, `AiScenarioTests`, `TacticFingerprintSweep`, three design docs,
  the applied xlsx and its exporter.
- Waits for the local session: Unity compile (Game and Tests were written blind), CatalogCheck (`aiBehaviour` and new
  `ai.world` keys), the EditMode suite, then the owner's go for the Explicit runs (scenarios, sweeps, fingerprints,
  campaign); the hooks in `Docs/ai/LOCAL_TODO.md` (tactic picker, HUD switch, hint line, tower mode UI, saving, player AI
  at Normal, viewer overlays, screenshots).
- Behaviour change to check first: `ConquestAi.LayeredDefault = true` puts every ConquestAi on the new AI, and the
  army-band upkeep and pressure tiers change every mode with an economy or battle events. If a regression blocks the
  merge, `LayeredDefault = false` restores the old commander; `BattleEvents.Escalation = false` the old events.
- balance.json keys added: `ai.world.bigFight`, `ai.world.escalationPoints`, `ai.world.churnWarn`,
  `ai.world.mergeThreshold`, and the whole generated `aiBehaviour` block; no existing value changed.

## Prompt 29 (owner, 2026-10-02): balance round 2 (v2), for the cloud

Read `Docs/prompts/prompt29_vi.txt` whole (it is the task) and its source `Docs/balance/Machine_Brigade_Can_bang_dot2_v2.xlsx`.
Work on a new branch `cloud/p29-balance` from `origin/feature/visual-overhaul`; same rules as above (Vietnamese replies,
English code/docs, one sub-agent at most, save tokens, DECISIONS sections `## Prompt 29 <pass> (cloud, <date>)`).
Facts the prompt does not know:
- **The v1 file `Docs/balance/Machine_Brigade_Can_bang_dot2.xlsx` does not exist** (the owner only has v2). Use the
  numbers the prompt itself gives for 5.4 and its 5.5 descriptions; E1's cross-check against v1 is not possible: log it.
- **The owner amended prompt 28** (end of `prompt28_vi.txt`): "no new upkeep system; use supply (tiếp tế)". Prompt 28
  I.2 already added `ArmyFactor` (`Scripts/Sim/Economy/EconomySystem.P28.cs`, `economy.armyBands` in balance.json) on
  top of the supply upkeep that already existed (`EconomySystem.Upkeep`, `Supply`). Pass 0 of this prompt: remove
  ArmyFactor from `Earning` and the armyBands data (keep the supply upkeep untouched), fix the docs (`Docs/ai/ECONOMY.md`)
  and the HUD text key if it names it (list the HUD line in LOCAL_TODO). Record it.
- **B3-AI is probably already done** by prompt 28 (aircraft return only when out of ammo). Pass 6: verify against C12,
  log ALREADY_APPLIED if so, and write the two tests the prompt asks for.
- The Blender kit name in 5.5 (`frontier_kit.py`) exists, but the current kit is V2 (`mb_kit27.py`, `mb_parts27.py`,
  wave builders `mb_p27_*.py`, registered last in `build_assets.py`). The cloud has no Blender: write the builder changes
  for the flare tubes and APS clusters, do not build; list the model ids in LOCAL_TODO for the local session (it builds,
  validates and renders the cards).
- No runs (owner's rule): the prompt says "write unit tests"; write them, do not run them; the only allowed run is the
  dotnet compile check and Python tools on the xlsx (the manifest export, the apply tool in dry-run and real mode on
  balance.json/campaign.json). CatalogCheck, the Unity compile, the PDF export (pass 8) and card renders are local.

## Cloud state 2026-10-02 (prompt 29)

- Branch `cloud/p29-balance` from `origin/feature/visual-overhaul` (377052b); head: the commit "P29 L8: design doc +
  report". Sim compile check clean; nothing run but the Python tools (manifest export, apply tool, applied-xlsx export).
- Done: pass 0 (ArmyFactor removed; field map; manifest export), 1 (S01-S04, S08, S09), 2 (ten checks), 3 (B0), 4 (E1,
  B1), 5 (S05-S07, B2-FLR, B2-APS, 5.4 missiles, 5.5 Blender parts written), 6 (B3-AI), 7 (B1-sky_gunship, C11, G1),
  8 (doc section, report). 0 CONFLICT, 0 BLOCKED; HOLD and REJECT skipped. Optional checks C02, C04, C08, C14 not done.
- Waits for the local session: Unity compile, CatalogCheck, EditMode and Python tests, card renders, PDF, Blender
  (`Tools/blender/mb_p29_details.py`), UI items in `Docs/ai/LOCAL_TODO.md`.
- balance.json: ~100 vehicles' `cp`/`hp`/`outgoingDamageMult`/`dropDelay`; 7 FIX values; `economy.bankByMode`;
  `flareCharges`/`flareRecharge` (17), stealth_bomber's flare skill removed; `apsCapability`, `interceptionMode`, `aps`
  (next_gen_tank, titan_tank); `missiles` (5 vehicles); rail_supergun rank/hp/bombard; p26_gungnir_emrg flags;
  `ai.economy.armyBands` removed.

## Prompts 28 appendix, 30, 31 (owner, 2026-10-02): order and split

Read the prompts whole: the appendix at the end of `Docs/prompts/prompt28_vi.txt` ("PHỤ LỤC PROMPT 28"),
`Docs/prompts/prompt30_vi.txt`, `Docs/prompts/prompt31_vi.txt`; source `Docs/story/Machine_Brigade_Cot_truyen_Che_do_v2.xlsx`
(16 sheets). Order: **28 appendix -> 30 -> 31**, one branch each (`cloud/p28-modes`, `cloud/p30-story`, `cloud/p31-decks`),
each from the latest `origin/feature/visual-overhaul` (the lead merges in between). Same rules as above.

Facts: prompt 29 already removed ArmyFactor and did B3-AI (appendix A is mostly done: verify and record; the new part is
the spendPressure / advancePressure split). Navigation is the Sim's own (`Scripts/Sim/Navigation`: NavGrid,
PathFinder, LaneMap, UnitCostField), not Unity NavMesh, so prompt 31's "prebuilt navmesh states" are NavGrid states and
are Sim work. Maps are JSON (`Resources/Data/maps/*.json`, 100 files incl. mode versions): prompt 30 L8's map audit
can be a Python tool over them. The dialogue queue and events are Sim (`Events`, `SimWorld.Events.cs`); the HUD that
draws them is Game.

| part | cloud | local (lead, Unity) |
|---|---|---|
| 28 appendix | aiModeProfile data + loader + assignment for every mode and mission type in campaign.json, the pressure split, CEASEFIRE at the damage level (Sim), the unit tests (written, not run) | compile, CatalogCheck |
| 30 L0, L1 | the precheck by reading code; act metadata, "Kết mạch Thorne", Legendary unlock (data, docs, text keys) | the UI that shows acts |
| 30 L2 | the P0-P4 queue rules, new triggers, speakerRole/allowedTriggers data, a line-length validator by character budget | the portrait strip UI, safe areas, the real render-width check |
| 30 L3 | the RUNNING/RESOLVED/PRESENTATION/RESULTS state machine in the Sim, frozen gameplay at RESOLVED, tests | the presentation (camera, VFX, slow motion on a view clock, skip tap) |
| 30 L4, L5, L6 | match rules schema and scoring, stars, leaderboards order, the endless continuation and rewards, neutrals V1 (Sim + map JSON) | the Continue/End buttons, results screen, neutral models if new ones are needed |
| 30 L7 | the 193-mission script (text tables EN + VI), validator, `script_stats.md` | - |
| 30 L8, L9 | mode static audit and map audit (Python), report | the PDF |
| 31 | the precheck, the fixed-deck data model, loaned cards, campaign generator rule, the 13 + later missions' data and special rules, placed allies (Sim AI), events as NavGrid states, tests | the fixed-deck screen UI, event visuals and minimap marks, the PDF |

List every local item in `Docs/ai/LOCAL_TODO.md` under the prompt's name. No runs except the dotnet compile check and
Python tools; the prompts' "write automated tests" means write them.

## Cloud state 2026-10-02 (prompt 28 appendix)

- Branch `cloud/p28-modes` (from `origin/feature/visual-overhaul` 322bcc89), commit "P28: aiModeProfile": the appendix's
  cloud part is done (DECISIONS "28 appendix", LOCAL_TODO "Prompt 28 appendix"). dotnet compile: 0 errors.
- Waiting for the owner to merge it; then prompt 30 on `cloud/p30-story` from the latest `origin/feature/visual-overhaul`,
  then prompt 31 on `cloud/p31-decks`.

## Local merge notes for the cloud (2026-10-02)

Prompt 28 appendix merged (feature/visual-overhaul 592d8e2): Unity compile 0 after one fix, CatalogCheck OK. Tests
written in the cloud must compile under Unity's NUnit 3.5 and with `using UnityEngine;`: no `Is.AnyOf` (use a boolean
`Is.True`), use `Has.Member`/`Has.No.Member` for collections, and alias `EntityId = MachineBrigade.Sim.Core.EntityId`
(UnityEngine has its own `EntityId`). Waiting locally: the UI greying of tactics a profile forbids (LOCAL_TODO).

## Cloud state 2026-10-02 (prompt 30, stopped early at the owner's request)

- Branch `cloud/p30-story` (from `origin/feature/visual-overhaul` 91c3aa2); head: the commit "Cloud state after prompt 30 (partial)".
- Done and pushed: L0 (`Docs/checks/p30_precheck.md`), L1, L2, L3, L4, L5, L6, L7 (all 15 chapters, 1601 lines over 193
  missions, validator 0 errors, 238 soft-length warnings; `Docs/story/script_stats.md`), L8 (`Tools/audit/map_audit.py`
  → `Docs/checks/map_audit.md/.csv`: 9 RED, 91 YELLOW; `Tools/audit/mode_static_audit.py` → `Docs/checks/mode_static_audit.md`:
  no symmetric flags).
- Unfinished, for the local machine:
  - `Docs/DECISIONS.md` "Prompt 30": notes for L7 (script source format `trigger[:arg][@sec] | speaker | P | VI || EN`,
    speaker trigger extensions in `Tools/story/import_speakers.py`, the story guard rails in `script_build.py`) and L8
    (thresholds in the audit scripts' docstrings) are not written.
  - L9: `Docs/story/report_p30.md` is not written (L0 results, decisions, lines per chapter from script_stats.md, the 238
    warnings, RED maps: borderbridge conquest/sandbox, coralisles_siege, emberridge conquest/long/sandbox, openpit_siege,
    swamp_siege (disconnected regions), hydrodam_conquest (path delta 19 %)). Design-doc sections in
    `Tools/docs/programme.py` (match rules, endless, neutrals, dialogue, end sequence) are not updated; the PDF is local.
  - `Docs/ai/LOCAL_TODO.md` "Prompt 30" still needs: Unity compile of all edited Game/Sim files; run MatchEndTests,
    DialogueTests, MatchRulesTests, EndlessTests, NeutralTests, CatalogCheck (none were run in the cloud; only dotnet
    compile checks); fix the 9 RED maps; export the PDF.
- Prompt 31 (`cloud/p31-decks`) not started.

## Play-test 14 lane B (owner, 2026-10-03): UI, hangars, aura buildings, HQ tab, fire-support summons

Read `Docs/AGENT_RULES.md`, then `Docs/prompts/playtest14_vi.txt` (owner's words, Vietnamese) and
`Docs/fixes/playtest14_plan.md` (binding decisions, owner answers). Branch from `origin/feature/visual-overhaul`,
push to **`cloud/pt14-b`** only (never main or feature/*). No Unity in the cloud: compile the Sim with the dotnet
project of "Setup and compile check" above; review Game/UI C# by hand (C# 9). Write tests if useful, do not run them.

Running locally in parallel (do NOT do their parts): lane A = gameplay/VFX fixes and boss escorts by domain; lane C =
deletes every id in the plan's "Deletion list" (and moves their GLBs to Archive/models). So: do not delete anything,
do not reference ids from the deletion list in new code/data, do not touch boss models. Bosses are on hold.

Your work (gameplay values allowed only as listed in the plan; log each in `Docs/export/CHANGES.md`):
1. Commander + tactic get their own menu tab, showing the chosen commander's starting forces (generals +
   openingSquads in balance.json), read-only.
2. Back button (top-left) and tab switching often need two taps: find the cause by reading the UI code
   (focus / picking / pointer handlers / navigation) and fix so one tap works everywhere.
3. Base tab: cannot scroll, text hidden behind the base cover; make it scroll, readable, simpler (flat tactical style).
4. New HQ tab: pick HQ type (headquarters, .fortress_ground, .fortress_air, .shield = the gun) and the light unit the
   HQ calls (scout_jeep / armored_car / light_tank); wire into the match.
5. Hangars: keep drone_hangar; add a vehicle hangar (scout_jeep / armored_car / light_tank, player picks one) and an
   aircraft hangar (scout_heli / recon_drone). Free, one unit per cycle, max 2 alive per hangar; tap the map to set a
   rally point. New structure ids, strings EN/VI, catalog entries; reuse existing hangar models as placeholders (the
   local lead redraws the 3 hangars later).
6. Aura buildings per the plan (airfield: aircraft +10 % damage, +10 % speed; repair_bay: ground vehicles +10 % damage,
   +10 % max HP; fire_control_centre renamed "Defence Command Centre" / "Trung tâm chỉ huy phòng thủ": structures
   +15 % range, +10 % HP); global while standing, one per kind, no stacking, deterministic Sim; their old functions
   replaced; drop airfield.hangar / airfield.service.
7. laser_ad_station renamed "Laser Defence Tower" / "Tháp la-de phòng thủ"; drop the .net variant.
8. Fire-support screen: a "Units called" tab for supports that call units. reinforcements (Airdropped armour): the
   player picks the units, total unit value <= 20 cp, call price = ceil(1.5 x total) (20 -> 30, 15 -> 23).

Finish: `## Play-test 14 (lane B, cloud)` in Docs/DECISIONS.md (append at the end), one CHANGELOG line under
Unreleased, commits "Play-test 14 (lane B): ..." in logical steps, then append a short `## Cloud state <date>
(play-test 14 lane B)` note at the end of this file (what is done, what needs a Unity check locally, open questions)
and push cloud/pt14-b.
