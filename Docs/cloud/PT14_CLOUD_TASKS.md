# Play-test 14: task file for Claude cloud sessions

Written 2026-10-03 by the local lead. **This file is the single source for cloud work on play-test 14.** It replaces
the play-test 14 sections of `Docs/CLOUD_HANDOFF.md` (those stay for history only).

## 1. Repo, branches, what to read

| What | Value |
|---|---|
| Repo | `github.com/Winka173/machine-bridage` |
| Start from | `origin/feature/visual-overhaul` (the local lead pushes there; never commit to it) |
| Push to | Session 1: **`cloud/pt14-c`** · Session 2: **`cloud/pt14-a`** (only these; never `main`, `feature/*`, `lead/*`) |
| Read first, in order | `Docs/AGENT_RULES.md` → this file → `Docs/fixes/playtest14_plan.md` (binding decisions + deletion list) → `Docs/prompts/playtest14_vi.txt` (owner's words, Vietnamese) |
| Grep only, never read whole | `Docs/DECISIONS.md` (1.7 MB), `Docs/CHANGELOG.md`, `Resources/Data/balance.json` (JSONC, ~3k lines) |

## 2. What the cloud can and cannot do

| Can | Cannot |
|---|---|
| Edit any file, git commit/push to its `cloud/pt14-*` branch | Run Unity: no editor, no import, no play, no renders, no screenshots |
| **Compile the Sim**: `dotnet build Tools/simbuild/Sim.csproj` (engine-free assembly `MachineBrigade.Sim`, C# 9) | Compile `Scripts/Game`, `Scripts/Editor` or the UI (they need UnityEngine / UI Toolkit) |
| Compile Sim + a few Game files: `dotnet build Tools/simbuild/gamecheck/GameCheck.csproj` (add more engine-free Game files to it if useful) | Run EditMode/PlayMode tests, sims, sweeps, measures (owner rule; also impossible without Unity) |
| Python tools in `Tools/` (export, balance, jsonc edits), `python -m py_compile` | Blender builds, model edits, GLB checks (GLBs are LFS pointers in a skip-smudge clone) |
| Write tests (EditMode C#) | Run them |

Consequences:
- **Do not force it (owner, 03/10): "cái gì cloud không làm được thì đem về local làm, không cần phải ráng".** If an
  item needs Unity to find or check (visual bugs you cannot locate by reading code, look/feel, sound, sea shader,
  preview staging), Blender or real GLBs, skip it or do only the part you can do safely, and list it under
  "For local" in your Cloud state note with what you found (files, likely cause). Do not guess blind fixes.
- Game/UI C# is checked **by hand** only: C# 9 (no `required`, no file-scoped namespaces, no raw strings, no
  collection expressions), check every type/member you call exists (grep it), keep Unity APIs you already see in the
  file. Put new logic in the Sim where it belongs (deterministic, engine-free) so dotnet checks it.
- The local lead merges your branch, compiles in Unity, fixes compile errors, renders, and lets the owner play-test.
  List in your "Cloud state" note anything that needs a look in Unity.

## 3. Setup

```
GIT_LFS_SKIP_SMUDGE=1 git clone git@github.com:Winka173/machine-bridage.git   # or https; models are not needed
git checkout -b cloud/pt14-c origin/feature/visual-overhaul                   # session 2: cloud/pt14-a
dotnet --version || <install the .NET SDK 8 or 9>
dotnet build Tools/simbuild/Sim.csproj -nologo -v q    # must say "Build succeeded" before and after your work
```
`*.csproj` is git-ignored (Unity generates them): `Tools/simbuild/Sim.csproj` and `gamecheck/GameCheck.csproj` are
force-added; use `git add -f` if you change them.

## 4. Rules (owner)

- No tests, sims or measures. No `fable` model, ever; "sonnet" means Sonnet 5.0 only.
- Gameplay value changes only where this file or the plan says so; log **every** value change (data or code) in
  `Docs/export/CHANGES.md`.
- Bosses are on hold: no boss model, removal or size change (the +20-30 % size was cancelled).
- Never a `MaterialPropertyBlock` on a `MachineBrigade/Lit` renderer (tint via `MaterialLibrary.Tinted`). Never
  shrink fire or explosions.
- Strings are bilingual (English, Vietnamese) in the C# text tables under `Scripts/Game/Hud` (`Strings.cs`,
  `GuideText.cs`, ...): every new or renamed name needs both.
- balance.json is JSONC with comments: edit it textually (or with the jsonc helpers in `Tools/balance/`), keep
  comments and layout.
- Commits: short subject `Play-test 14 (lane X): ...`, body at most 3 lines, trailer
  `Co-Authored-By: Claude <noreply@anthropic.com>`. Push after each finished part.

## 5. Session 1: deletions (part 1), then UI + base systems (part 2) → `cloud/pt14-c`

### Part 1: delete (lane C)
Delete every id in the plan's "Deletion list" (units, supports, structures **with all variants**), the skill
`apc_smoke` (remove it from `ifv`; the ifv stays), and weapons/skills used only by deleted entries. Everywhere:
balance.json, default decks, generals' `openingSquads`, AI lists, `campaign.json`, `operations.json`, `maps/`,
`script/`, strings EN/VI, guide text, icon maps (`MenuScreen`), `MatchSettings`, `Progression`, `GearText`, name
sheets and other test data, export sources (`Tools/export`, `Docs/export/current`).
- Replacements where referenced: `gunship_heli` → `attack_helicopter`, `bmpt` → `ifv`, `interceptor_jet` →
  `fighter_jet`; any other deleted unit → nearest-role surviving unit (list each in DECISIONS).
- Old saves owning a deleted entry get a refund: add a migration in the save/progression code.
- **Keep the models**: `git mv` each deleted entry's GLB(s) from `Assets/MachineBrigade/Resources/Models/` to
  `Archive/models/` and delete their `.meta`. In a skip-smudge clone the GLB is an LFS pointer; `git mv` keeps the
  same LFS object (`*.glb` is LFS in `.gitattributes`), so this is safe. Keep their builders in
  `Tools/blender/build_assets.py` with a `# archived (play-test 14)` comment; `python -m py_compile` it.
- Final check: grep every deleted id → zero hits outside `Archive/`, `CHANGES.md`, `DECISIONS.md`, `CHANGELOG.md`,
  `Docs/prompts`, `Docs/fixes`. Sim builds. Write the removed-id list to `Docs/fixes/playtest14_deleted.md`.

### Part 2: UI and base systems (lane B), same branch, after part 1
1. Commander + tactic get their own menu tab; it shows the chosen commander's starting forces (generals +
   `openingSquads`), read-only.
2. Back button (top-left) and tab switching often need two taps: find the cause by reading the UI code (focus,
   picking, pointer handlers, navigation events, debounce) and fix so one tap works everywhere.
3. Base tab: cannot scroll; text hidden behind the base cover. Make it scroll, readable, simpler (modern flat
   tactical "Field Command" style).
4. New HQ tab: pick the HQ type (`headquarters`, `.fortress_ground`, `.fortress_air`, `.shield` = the gun) and the
   light unit the HQ calls (`scout_jeep` / `armored_car` / `light_tank`); wire it into the match.
5. Hangars: keep `drone_hangar`; add a vehicle hangar (`scout_jeep` / `armored_car` / `light_tank`, player picks one)
   and an aircraft hangar (`scout_heli` / `recon_drone`). Free, one unit per cycle, max 2 alive per hangar; the
   player taps the map to set a rally point. New structure ids, strings EN/VI, catalog entries; reuse an existing
   hangar model as a placeholder (the local lead redraws all 3 hangars).
6. Aura buildings: `airfield` = aircraft +10 % damage, +10 % speed; `repair_bay` = ground vehicles +10 % damage,
   +10 % max HP; `fire_control_centre` renamed "Defence Command Centre" / "Trung tâm chỉ huy phòng thủ" = structures
   +15 % range, +10 % HP. Global while the building stands, one per kind, no stacking, deterministic Sim; their old
   functions are replaced; drop `airfield.hangar` / `airfield.service`.
7. `laser_ad_station` renamed "Laser Defence Tower" / "Tháp la-de phòng thủ"; drop its `.net` variant.
8. Fire-support screen: a "Units called" tab for supports that call units. `reinforcements` (Airdropped armour): the
   player picks the units, total unit value ≤ 20 cp, call price = ceil(1.5 × total) (20 → 30, 15 → 23).

## 6. Session 2: gameplay + VFX fixes (lane A) → `cloud/pt14-a`

Items 1-2 (impact smoke ×0.4, no ground zones for bombs/shells) are merged already (caff29c). Do 3-14. Do not delete
anything (session 1 does). Think about the real-world logic first.
3. `armored_car` fires its two guns at the same time (in-game and in the in-action preview).
4. Missile smoke trail cut off near the target (`rocket_technical`, `mlrs`, `aa_vehicle`, `sam_launcher`,
   `strike_drone`, probably every missile): the trail must last to detonation and the visual missile must reach the
   impact point on the Sim hit frame.
5. `light_tank` (Amphibious light tank): in-action preview on land; its missile must visibly fire.
6. `sky_gunship` firing sounds are weak: make them punchy (105 / 40 / 25 mm), procedural or existing clips.
7. All launcher vehicles: raising the launcher is super fast, lowering is normal; raise at the normal speed.
8. Bosses with howitzers: their shots look like tank rounds; restore the artillery look (muzzle blast, arcing shell,
   artillery impact).
9. Leviathan: fires before the gun finishes traversing (wait until aligned); barrel recoil on firing; secondary
   turrets rotate to their targets (runtime pivots only, no model edits).
10. `armored_train` (Juggernaut) and `nuke_train` (Nemesis): the body yaws off the rail when firing; lock it to the
    track.
11. `armored_bulldozer` in-action preview: it breaks a wall and a watchtower.
12. Sea: some tiles have no water and waves run bottom-to-top; water covers every sea tile, waves follow the wind.
13. `napalm_strike` and `airstrike`: an aircraft flies over and drops bombs (napalm = fire canisters) on the existing
    bomb-run system; damage unchanged.
14. Boss escorts by domain: ground boss → ground vehicles, sea boss → boats, air boss → aircraft (Nyx gets tanks at
    sea today). Data/rules: `escortRules` / `escortTemplates` in balance.json.

Sessions 1 and 2 run in parallel; they touch different things. If both must edit the same balance.json line, keep
the change minimal; the lead resolves conflicts.

## 7. Finish (each session)

1. `dotnet build Tools/simbuild/Sim.csproj` succeeds.
2. Append `## Play-test 14 (lane X, cloud)` to the end of `Docs/DECISIONS.md` (decisions, replacements, anything
   not done) and one line under `## Unreleased` in `Docs/CHANGELOG.md`.
3. Append to the end of **this file** a `## Cloud state <date> (session N)`: last commit, done items, items not
   done and why, what needs a Unity look, questions for the owner.
4. Push. The owner tells the local lead, who merges, compiles in Unity, checks LFS, renders, and updates the
   owner's test copy.

## Cloud state 2026-10-03 (session 1)

Branch `cloud/pt14-c`; commits on top of feature/visual-overhaul 4ff17fba: part 1 8f1354f1 (deletions), part 2
0cb69985, 523e4117 and the docs commit after them (`git log --oneline origin/feature/visual-overhaul..cloud/pt14-c`).
`dotnet build Tools/simbuild/Sim.csproj` succeeds. No tests written or run (owner: "không cần viết test").

Done: part 1 entirely (list: Docs/fixes/playtest14_deleted.md; refunds = roster v9); part 2 items 1-8 (DECISIONS
"Play-test 14 (lane C + lane B, cloud session 1)"; values in Docs/export/CHANGES.md PT14 and PT14-B).

For local (Unity / LFS / owner):
- Compile in Unity: Game/UI code was only syntax-checked. New files: MenuScreen.Command.cs, MenuScreen.Calls.cs,
  Sim/Modes/BaseSystem.Hangars.cs, Sim/Abilities/FieldWorksSystem.Auras.cs (metas written by hand).
- EditMode tests: part 1 tests were updated; part 2 changed behaviour that existing tests still assert (repair bay
  repair, airfield pads and branches, fire-control link, laser_ad_station.net, Army tab order, Base strip/walls). They
  were not updated (owner said no tests): expect failures there.
- Look on device: one tap on Back / tabs (Tap.cs, MenuScreen.Back); the Base tab layout (strip now in the right panel,
  bar on one row); the new Commander and HQ tabs; the support "Units called" tab; the hangar rally button in the deck bar.
- Re-export Docs/export/current (needs the local Docs/Machine_Brigade_Design_Review.html; on the cloud 9 pictures drop).
- Card renders for vehicle_hangar / aircraft_hangar (manifest entries not added) and the 3 hangar models (placeholder
  drone_hangar model). Archived GLBs: check `git lfs` sees Archive/models/*.glb after the merge.
- Regenerating CampaignText.cs with build_campaign.py reorders boss lines and undoes hand edits: kept the committed file.
- The xlsx sources (Machine_Brigade_Can_bang.xlsx -> unlocks_sheet.json / NameSheetData; the AI sheet) still list the
  deleted ids; re-importing them would bring them back.

Questions for the owner:
- Airdropped armour: implemented as "item use + ceil(1.5 × total) CP". Should it stop being a coin item instead?
- Opening-squad role "radar_scout" lost all its units (Kerr, Orlov now open with one squad less): give them another role?
- Hangars are Medium (fit from HQ level 1) and unlock at c3m04 / c7m02: OK, or another route/price?

## Session 3 (queued, after session 2 is merged) → `cloud/pt14-d`
Lead decisions on session 1's questions are in DECISIONS "Play-test 14: cloud session 1 questions". To do:
1. `reinforcements` (Airdropped armour) stops being a coin item: a plain fire-support card paid in CP only
   (player picks units, value cap 20 cp, price ceil(1.5 x value)); owned items refunded as coins (roster migration);
   strings EN/VI; CHANGES.md.
2. Update the stale EditMode tests session 1 listed (repair bay, airfield, fire-control link, Army tab order, base
   cover strip) to the new behaviour; do not run them.
3. Remove the deleted ids from the source xlsx files the importers read (list them; keep sheet layout).
4. Delete the 10 bosses the owner dropped: stymphalos, fortress_hive (Hive), cerberus, supreme_command (Atlas),
   kronos, caspian, morrigan, sky_fortress (Spectre), garuda, rail_supergun (Gungnir), with their big attacks /
   supports / weapons used only by them (garuda_carpet, kronos_bucket_sweep, leviathan_cruise_mark_7 "Caspian's
   cruise missile", supergun_shell, ...), same clean-delete rules as part 1 (GLBs git mv to Archive/models, builders
   kept). Story replacements (rewrite the lines so they fit): Hive (c5m05) -> Matriarch (drone_mothership); Atlas
   (general's elite form) -> Behemoth Mk.II; Kronos (c8m10, also 3 map files) -> Tartarus (earth_borer); Caspian
   (c9m05) -> Charybdis (landing_hovercraft); Morrigan (morrigan_hunt mini-boss, c10m12, i3m02) -> Harpy
   (mega_gunship); Spectre (c10m08, c10m10, c10m12, i3m02) -> Roc (command_airship); Gungnir (c11m05) -> Monster.
   Campaign generator rerun if it owns those fields. List all in Docs/fixes/playtest14_deleted.md.
5. Locust (variant of drone_mothership): launches one drone every 2 s, no faster (give Locust its own drone weapon if
   it shares Matriarch's; burst/cooldown so the rate is 1 per 2 s); CHANGES.md.

## Session 4: model waves in the cloud (trial) → `cloud/pt14-models`

The owner wants the cloud to do as much as possible. Models need Blender: try it, and **if Blender cannot run, stop
and write that in Cloud state** (the local lead then builds them; do not force it).
- Setup: `GIT_LFS_SKIP_SMUDGE=1` clone is not enough here: run `git lfs install && git lfs pull --include
  "Assets/MachineBrigade/Resources/Models/*.glb"` (the builders and gates read existing GLBs). Download Blender 4.5
  LTS for Linux (`https://download.blender.org/release/Blender4.5/`, the latest 4.5.x linux-x64 tar.xz), run it
  `--background --factory-startup --python-exit-code 1`. The kit (`Tools/blender/frontier_kit.py`, bmesh only) works
  headless. For gate/look renders use what works headless (Cycles CPU or Workbench if Eevee has no GPU).
- Read `Docs/models/MODEL_STANDARD.md`, `Docs/models/BUDGETS.md`, `Docs/TOKEN_OPTIMISATION.md` (model waves).
  Quality before tokens: as many gate rounds as needed, look at every render. Build with
  `Tools/blender/build_assets.py` (register builders inside its dict; the build filter is a substring match:
  `git status` the GLBs after a build and restore any you did not mean to change); `python
  Tools/assets/glb_quantize.py` on the GLBs you built; `Tools/assets/quality_gate.py`.
- Triangle budget = N x the class maximum in BUDGETS.md (boss small 45k, medium 55k, large 70k): owner's N per boss
  below; bosses without a number get 3.5x. No size change (cancelled). Keep every Mount_* / Muzzle_* / Elevation /
  flare-point convention the runtime reads (grep `ModelLibrary` for the names) and keep data mounts in sync.
- Run **one wave per sub-agent** (Agent tool, model `opus`, never fable; 4-6 models each), commit + push after each
  wave. Owner's notes per model are in Docs/prompts/playtest14_vi.txt (list + "Bổ sung 03/10").

| Wave | Models |
|---|---|
| M1 ground bosses | mobile_fortress (Jötunn: exactly 2 symmetric rear launchers), fortress_bastion + bastion_mk0 (own model, detailed; guns placed sensibly, also on the sides, not only the roof), fenrir (own model), behemoth_inferno (from the behemoth model, smaller, secondary guns removed, thinner main barrel, flame projectors; not an oval) |
| M2 trains, Ixion, air | armored_train + nuke_train (2-4 more cars each; data length/HP only if the Sim needs it, log CHANGES), ixion (4-5 guns/missile launchers, models + data weapons, CHANGES), mega_gunship (Harpy: stub wings like an attack helicopter carrying its launchers and guns), daedalus (5x) |
| M3 sea bosses | leviathan (5x; keep turret/recoil pivots for the runtime), scylla (4x, own model), kraken (5x), nyx (4x), hydra (4x) |
| M4 base | drone_hangar, vehicle_hangar, aircraft_hangar (three distinct hangars), mg_bunker (several MG ports with guns + data mounts), guard_tower |
| M5 vehicles | ew_jammer, iron_beam (Laser AA), command_vehicle, wheeled_gun (smaller turret) |
| M6 vehicles | stealth_naval_strike, aa_vehicle + heavy_aa (twin autocannons spaced like the real designs), laser_ad_station (Laser Defence Tower) |

Units seen in numbers (M4-M6) stay at or under 1.5x their class maximum. Push GLBs as LFS objects. The local lead
then checks LFS, quantises, renders cards and Unity scans, and merges.
## Cloud state 2026-10-03 (session 2)
Branch `cloud/pt14-a` (from feature/visual-overhaul 4ff17fba); last commit: the one adding this note. Sim builds
(`dotnet build Tools/simbuild/Sim.csproj`: 0 errors); the catalog loads (FromJson). No tests written or run. Game/UI
files only syntax-checked (C# 9); they need a compile in Unity. Details per item: Docs/DECISIONS.md
"Play-test 14 (lane A, cloud)"; values: Docs/export/CHANGES.md "Play-test 14 lane A".

Done:
- 3 armored_car coax at 30 m (`mg_coax_long`), so both guns fire on the turret's target.
- 4 smoke trails laid to the impact (ProjectilePool.FinishTrail); every rocket burns to the end.
- 5 light_tank clip on land; its gun-launched ATGM and the gun share the barrel (1 s apart).
- 6 sky_gunship shots louder, farther, single shots a size class up.
- 7 launchers: the Sim waits for the erector (`erectSeconds`) before the first round.
- 8 boss howitzers drawn as artillery (`"lobs"` on boss_howitzer, inherited).
- 9 Leviathan trains its main turrets before each salvo (battle and preview); barrels on mount pivots recoil.
- 10 rail bosses never turn their hull off the track.
- 11 bulldozer clip: a HESCO wall and a watchtower.
- 12 sea swells and ripples run downwind.
- 14 escorts filtered by the boss's domain (`escortRules.domains`).

For local (needs Unity):
- Compile Game: VehicleView.MountKick.cs (new), VehicleView.Aim.cs, VehicleView.cs, WeaponEffects.cs, ModelLibrary.cs /
  .Lod.cs, FiringRange.Bosses.cs / .Abilities.cs, PreviewSettings.cs, AudioDirector.P34.cs, EffectsDirector.cs,
  WeaponInfo.cs, ProjectilePool.cs, MotorPlumes.cs; shader Water.shader.
- 9: check the Leviathan's barrels kick (Gun_barrels / Sec_barrels are now kept unmerged on their Mount_gun pivots) and
  the turrets traverse before the salvo (menu preview and a sea battle). Secondary turrets (mounts 3, 4) sleep until
  phase 1 by design (`wake`); if the owner meant they never turn even awake, look in a phase-1 battle.
- 5: whether the ATGM is now visible in the clip (it flies ~0.3 s from the gun's muzzle).
- 6: listen to the gunship; tune GunshipGain / GunshipCarry if needed.
- 7: the side ATGM box (VehicleView AtgmSeconds 0.6) still snaps up when fired; not handled.
- 11: watch the clip (the dozer drives to the wall, then the tower).
- 12: sea tiles without water not found by reading; check a sea map. Wave direction needs a look.
- 13 not done: StrikeEffects already flies the jet / bomber and drops bombs or napalm canisters; no cause found by
  reading. Check in a match which part is missing.
- 14: Nyx's tanks at sea: no sea boss has escort tables; the source (a mode's or mission's waves?) not found.
- Replay hashes change (Sim: A1-A6 in CHANGES).

Questions for the owner: none.

## Cloud state 2026-10-03 (session 3)
Branch `cloud/pt14-d` (from feature/visual-overhaul ece66216); last commit: the one adding this note. Sim builds
(`dotnet build Tools/simbuild/Sim.csproj`: 0 errors); the catalog loads (31 bosses: 14 main, 17 mini). No tests run. Game,
Editor and test C# only syntax-checked (C# 9). Details: Docs/DECISIONS.md "Play-test 14 (lane D, cloud)"; values:
Docs/export/CHANGES.md "Play-test 14 lane D"; deletions: Docs/fixes/playtest14_deleted.md (bosses section) and
Docs/fixes/playtest14_xlsx.md.

Done:
- 1 `reinforcements` is a CP fire-support card (call price on the deck card, AI default drop, chapter 4 unlock, roster v10
  refund 450 coins an item).
- 2 Stale EditMode tests rewritten (repair bay / airfield / defence command centre auras, airfield lines, Army tab order,
  Base cover in the panel scroll, Airdropped armour); Commander and HQ screens in MenuScreen.ScreenNames.
- 3 Deleted ids out of the four source workbooks (`Tools/balance/pt14_xlsx_prune.py`, XML-level edits).
- 4 Ten bosses deleted with their own big attacks, supports and weapons; story swaps as listed; models in Archive/models.
- 5 Locust: own `locust_drones`, one drone every 2 s.

For local (needs Unity):
- Compile Game, Editor and tests; run the EditMode suite (many tests touched: BossParts, Prompt20Boss/Hunt/TowersMaps,
  Prompt22Content/Story, Prompt23CampaignEvent, Prompt25Boss, Prompt26AB/CD, Prompt33SeaRoute, Prompt34/Preview,
  Prompt8Content, TowerIcon, BossEscort, FireRhythm, FixValidator, FixedDeck, Model, BalancePackRule, Item, TowerRoster,
  Prompt25NewContent, UnitLines, BaseBalance, CampaignStart). Replay hashes change.
- Play the swapped missions: c5m05 (Matriarch breaks off), c7m10, c8m10 (Tartarus at 2.6x), c9m05, i3m02 / c10m12
  (Harpy at 2.9x; the duel), c10m08 (Roc at 2.7x breaks off), c11m05 (Monster at the rail yard). Health multipliers are
  arithmetic, not measured.
- Airdropped armour in battle: the card's price follows the Units called tab; check the tab and the card after a change.
- `git lfs` sees the archived GLBs (git mv kept their pointers); card renders for the removed bosses are gone.
- Docs/export/current still lists the deleted bosses (re-export with ExportGameDoc, owner's word first); the pack2
  move tables (Tools/export/pack2/*.csv) still quote old code lines.
- `Tools/balance/import_names.py` fails (AttributeError in insert_after) on the committed sheet, before and after this
  session's edit.

Questions for the owner: none.
- Follow-up (owner): c8m10's last stage is Moloch (x1.4) with Tartarus tunnelling up at Moloch's 60 %; chapter 8 main
  Moloch, minis Ixion and Tartarus (CHANGES PT14-D12). Play it: the surfacing spot and the two bosses together.
