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
