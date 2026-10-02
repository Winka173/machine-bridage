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
