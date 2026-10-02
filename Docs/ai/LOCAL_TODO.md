# Prompt 28: hooks for the local session (Game, UI, Editor)

The cloud session writes the Sim only. Each line: file, what, why.

- DONE 2026-10-02 (local, bf234c3+1): `Scripts/Game/Match/ModeSessions.cs` (every session with an `IObjectiveMode`): set `world.Intel.Objectives = mode`
  after `mode.Setup(world)`. Why: the World Model's OBJECTIVE_PRESSURE events need the capture points (28 A.4).
- CatalogCheck DONE 2026-10-02 after pass 1 (OK: 241 vehicles, 371 weapons); the EditMode suite waits for the owner. Run them after merging pass 1 (`WorldModelTests` is new; balance.json gained `ai`).
- J (AI viewer overlays in the Sandbox) reads `world.Intel.For(team)`: `Own`/`Enemy`/`Threat[k]` grids
  (`Columns` x `Rows`, `CellCentre`), `Contacts` (confidence via `Confidence(now, ConfidenceDecay)`), `EnemyGroups`,
  `Front`, `Contested`, `Chokepoints`, `Warnings`, `Events`.
- Pass 2 hooks: the tactic picker sets `ConquestAi.Tactic` (player Auto-buy/Support AI and the Sandbox's two sides)
  before the first tick; the HUD switch button calls `ai.Commander.RequestTactic(world, id)` (shows `TacticReadyAt`,
  `InTransition`); the player's AI gets `Skill = AiSkill.For(AiDifficulty.Normal, catalog.Ai)` (K.2); the hint line
  calls `ai.Hints.Next(world, team, ai.Commander?.Squads)` about once a second (a side without an AI: `new AiHints()`).
  Boss Rush: set `Commander.FreeSwitch` during a break. Run CatalogCheck (`aiBehaviour` added) and the EditMode suite;
  `ConquestAi.LayeredDefault = false` gives the old AI for comparison.
- Pass 4 hooks: the Base screen (prompt 14) and a tap on a tower in battle call `world.SetTowerMode(team, id, mode)`;
  the allowed list is `catalog.AiData.Towers[defId]` (`Mode` + `Modes`); the Base loadout should save the chosen
  mode per hardpoint and apply it when the tower is placed. Text keys `tower.mode.*` are in the new text table.
- Pass 5 hooks: `PlayerProfile` saves the last tactic per mode (H.14) and per-squad choices (H.10, after chapter 6:
  `Commander.SquadTactics = true`, `RequestSquadTactic`); the HUD shows the supply upkeep `TeamEconomy.Upkeep` when below 1 (I.2; ArmyFactor was removed in prompt 29) and
  `world.PressureTier` (I.6) and Conquest's `InFinalPhase` (I.7); the tactic picker lists `catalog.AiData.Tactics`
  filtered by `AiBehaviour.Unlocked` and highlights `SuitedTo(commander)`; the briefing shows the general's tactic
  (`GeneralTactic`); a line when the enemy switches tactic while `enemy.TacticSeenBy(world, player)` (H.8); the
  Sandbox's side panel gets a tactic picker (`SandboxSide.Tactic`) and a switch button (H.13).
- Text tables: `Scripts/Game/Hud/TacticText.cs` (EN + VI: tactics, hints `aihint.*`, tower modes, fire stances, upkeep,
  pressure tiers, AI viewer words incl. `why.<factor>`), registered in `Strings.Get/Entries/Has`. Written blind:
  the local compile and L10nTests check them.

## Local UI pass (2026-10-02, feature/p28-ui; DECISIONS "28 local UI pass")

- DONE: tactic picker beside deck and commander (H.4, H.11, H.12) and the general's tactic in the mission panel (H.7):
  `Scripts/Game/Hud/MenuScreen.Tactics.cs`, `Scripts/Game/Match/TacticPick.cs`.
- DONE: player AI start tactic, Normal skill (K.2), squad presets, hint polling, tower modes, Boss Hunt free switch:
  `Scripts/Game/Match/ModeSession.Tactics.cs` (+ journal inputs in `MatchJournal.cs`, `MatchRunner.cs`).
- DONE: HUD tactic switch, per-squad tactics, scouted enemy tactic, hint line + Settings toggle, upkeep factor,
  pressure and final-phase lines, tower mode on a tap: `Scripts/Game/Hud/BattleHud.Tactics.cs`,
  `Scripts/Game/Match/MatchRunner.Tactics.cs`, `PlayerCommander.cs`, `SelectionController.cs`.
- DONE: tower targeting chips on the Base screen (`BaseScreen.TowerModeRow`), saved per tower type (not per hardpoint).
- DONE: PlayerProfile: last tactic per mode, per-squad tactics, tower modes (`PlayerProfile.Tactics.cs`).
- DONE: Sandbox tactic per side + live switch (H.13), AI viewer sheet (J) `SandboxScreen.AiView.cs`; Sim gained
  `WorldModel.Peek` (read-only).
- WAITS FOR THE OWNER: O.6 screenshots of the picker, HUD switch, Base chips and AI viewer; the EditMode suite
  (L10nTests covers the new keys) and a play check of the HUD rail layout on a phone (the rail gained one tool).
- Prompt 29 (lead 2026-10-02: cards are model renders hashed by the GLB, no data printed: no re-render needed; Unity compile 0 and CatalogCheck OK after the merge; tests wait for the owner; PDF after the waves): re-render the cards (prices, health, drop times changed for ~100 vehicles), run CatalogCheck (new keys
  `outgoingDamageMult`, `dropDelay`, `economy.bankByMode`, later `flareCharges`, `flareRecharge`, `apsCapability`,
  `interceptionMode`, `missiles`) and `BalanceRound2Tests`, `Tools/balance/test_p29.py`; rebuild the design PDF
  (`Tools/docs/build_doc.py`, pass 8 sections).
- DONE 2026-10-02 (feature/p29-local-ui; DECISIONS "Prompt 29 local UI"): Prompt 29 L5: the equipment screen must not offer the heat-decoy module to vehicles without flares
  (`VehicleDef.FlareCharges == 0`) nor Trophy to `ApsCapability.None` (Game `GearCatalog`/`VehicleFit`); HUD and card show
  missiles left (`Weapons[i].Ammo` of the `missiles` mount) and flare charges (`FlareChargesLeft`/`FlareChargesMax`);
  check that equipment tuning a missile mount keeps the vehicle's own load (VehicleDef.ArmOf).
- Prompt 29 5.5 (Blender, local; the two Game effects DONE 2026-10-02 on feature/p29-local-ui, the models by wave 4c): `Tools/blender/mb_p29_details.py` has `flare_tubes` and `aps_cluster` (V2 kit) and the
  model lists (`FLARE_MODELS`: 16 aircraft; `APS_MODELS`: next_gen_tank, titan_tank; main_battle_tank's Trophy only
  as gear art). Call them from each model's builder with hull positions, rebuild with build_assets.py, validate,
  render cards; add the two effects (`FLARE_EFFECT`, `APS_EFFECT` descriptions) in the Game's effects.
- DONE 2026-10-02 (feature/p29-local-ui): Prompt 29 G1: the view draws the Gungnir's aiming line (origin to aim) for the 3 s warning from its `FiredWith` event
  (ASSET_DEBT "Gungnir's line warning"); check the Boss Hunt lists and the hunt UI with 17 mains.

## Prompt 28 appendix (aiModeProfile, cloud/p28-modes)

- Unity compile, then run `AiModeProfileTests` (5 tests, written only) and the existing AI suites (AiTests, AiReviewTests).
- CatalogCheck with the new balance.json `aiModeProfiles` block.
- Tactic picker UI: `RequestTactic` can return `NotAllowed`; grey out tactics the mode's profile forbids
  (`world.AiProfile.Allows`).
- Recon HUD: optional "Báo động" indicator from `world.Alarm`.

## Prompt 30

- DONE 2026-10-02 (lead pass, feature/p30-local; not compiled yet): L1, L2 (strip), L3 (presentation), L5 (buttons, pay),
  L6 (field + minimap); DECISIONS "Prompt 30 local". Still open below: the Unity compile of every edited Game/Sim file
  (incl. `MatchRunner.Ending.cs`, `NeutralSiteView.cs`, `DialogueViews.cs`, `Overlays.cs`, `BattleHud.cs`, `Minimap.cs`,
  `MusicDirector.cs`, `Neutrals.cs`), the test runs (when the owner allows), the strip measure and `RENDER_CHARS`,
  L3's proxies retreating / turrets turning (not done), L5's leaderboard sort (no board screen yet), the owner's look
  at the radar dome / garage / ammo dump as capturable sites, and the PDF.
- L1 (DONE): show the "Kết mạch Thorne" card (`campaign.thorneArc.title`, `campaign.thorneArc`) after c9m10, before chapter 15
  (once, like the chapter cards); the act switch UI reads `act` (4 acts).
- L2 (DONE but the measure and the test run): the portrait strip (small portrait + compact 2-line strip above the card tray; existing portraits: generals,
  briefing cards; a placeholder portrait by side for anyone missing, list them); never over the superweapon warning,
  the key boss UI or the objective timer; safe areas at 16:9, 20:9, 4:3. Measure the real render width: every script
  line in 2 lines at the smallest supported screen with the portrait at Large font, and set
  `RENDER_CHARS` in `Tools/story/script_build.py` from it. Route the HUD's system warnings as `DialoguePriority.System`
  if they should share the strip. Run `DialogueTests` (rewritten for the P0-P4 rules). Unity compile of
  `Dialogue.cs`, `RadioDirector.cs`, `ScriptText.cs`, `Strings.cs`.
- L3 (DONE but proxies / turrets and the test runs): drive the presentation in `MatchRunner`: when `_world.Ending.Phase == Resolved`, pick the `EndKind` (first win of
  a main boss / big operation, first win, replay, loss), `BeginPresentation`, call `Ending.Advance(Time.unscaledDeltaTime)`
  each frame, `Skip` on a tap after 0.75 s, show the results at `Results` (and `ShowResults` from `CheckResult`). Hide
  the card tray and command buttons, keep the boss bar and notices; camera to the last target (0-1.5 s); visual slow
  motion x0.3 from 1.5 s on the effects/animation clock only; the boss's part-by-part death chain (0.3-0.5 s each,
  then the hull; wrecks burn, ships sink, aircraft fall); enemy proxies retreat to the edge, our turrets turn to the
  target (visual only); the last lines (general's defeat line, then the closing line; chapter line for big
  operations). A skipped story line goes to the results panel and the log. Loss: camera to our HQ or last vehicle,
  explosion, the general's gloating line, 3-4 s, no slow motion. Run `MatchEndTests` and the existing suites (some
  tests may have stepped a world after `IsOver`; they now see it frozen).
- L5 (DONE but the leaderboard sort and the test runs): the results panel's two buttons for Defend, Survival and Boss Rush when `session.CanContinue`: "Đánh tiếp (vô hạn)"
  (`result.continueEndless`, calls `session.ContinueEndless(world)`, hides the panel, resumes) and "Kết thúc"
  (`result.endRun`), with `result.endlessKept`. Call `session.PayEndless(modeId)` each frame (or each wave) and toast
  the coins and badges. Boss Rush's in-battle endless pick no longer opens (EndlessAtResults). Endless's menu entry
  unchanged. Leaderboards: sort with `world.Catalog.MatchRules.Board(id)`. Run `EndlessTests`, `MatchRulesTests`.
- L6 (DONE but the owner's look and the test run): show the neutral sites (`world.Neutrals.Sites`: kind, place, holder) on the field and the minimap (holder colour,
  capture ring), the abandoned AA site's marker (no building until taken), the supply drop's 15 s marker. The radar
  dome, garage and ammo dump props are existing models; check they read as capturable sites. Run `NeutralTests`.

## Prompt 31 (lane B, feature/p31-b1)

- Compile the Sim and Game edits (FixedDeckDef.cs new, MissionDef, MissionMode, MissionDecks, MatchRunner,
  ModeSessions, MenuScreen.Campaign, Strings) and the new FixedDeckTests; run CatalogCheck (campaign.json gains
  `fixedDeck` on 13 missions and an `enemy_barrage` event on c1m01).
- Look at the mission page's "Mission deck" panel in Unity (10 compact cards in a wrapping row, the "Loaned" tag under a
  card, the rule lines); it uses existing classes plus `fc-campaign__fixed-deck`, `fc-campaign__fixed-card`,
  `fc-tag--loaned`, which have no USS rules yet.
- When the owner allows test runs: FixedDeckTests, and the dialogue validator is already green (script_build.py).
## Prompt 32 L1 (lead pass, 2026-10-02): tower roster 22

- Art (Blender): the merged cards' branch models and icons `<tower>_a` / `_b` for `at_gun_emplacement`, `searchlight`,
  `inflatable_decoy`, `heavy_flak_tower`, `laser_ad_station` (until then a branch wears its absorbed tower's model, or the
  card's: `TowerArt.ModelFor`); `TowerBranchArtTests` skips these five until then. The AA tower's B branch is now the
  Stinger post (its `aa_turret_b` SAM-pair model may want a Stinger launcher); the 57 mm branch lost its air role.
- Unity: compile, `CatalogCheck`, card renders of the ten new branch ids; run `TowerRosterP32Tests`, `TargetMaskTests`,
  `TowerRosterTests`, `TowerBranchTests`, `TowerCardTests`, `Prompt20TowersMapsTests`, `Prompt25NewContentTests`,
  `Prompt25NewContentBTests`, `TowerBranchArtTests`, `TowerGearTests`, `BaseLayoutTests`, `BaseTests`.

## Prompt 32 L2 (lead pass, 2026-10-02): rebuilds and prices

- Unity: compile, CatalogCheck (balance.json: 60 rebuildCp, 5 outgoingDamageMult cuts, base.rebuild drop/enemyRadius/showdownCutoff/hqRescue); run TowerRebuildP32Tests, BaseTests, TowerGearTests, DefendLinesTests, BaseDefenceTests.
- Play: the REBALANCE_STATS cuts (MG bunker x0.32, twin x0.27, flame x0.17, AA tower x0.58, flak x0.41) and the tap on a fallen slot with Auto-buy off; the steel fortress verdict (HOLD) for the owner.

## Prompt 34 L5/L6/L7 (lead pass, 2026-10-02)

- Unity: compile; run `Prompt34ViewTests` (L5 tiers, budget, shake; L6 sounds; L7 wrecks and the crash plan) with `Prompt34Tests`, `BlastSizeTests`, `EffectsTests`.
- docs/vfx (the lead renders): before/after shots of each tier's shot and blast, T0-T5 (`EffectShots` or the In action range: a 12.7 mm, 30 mm, 100 mm, 152 mm, 203 mm and the 406 mm salvo), saved as `Docs/vfx/p34_t<k>_{fire,blast}_{before,after}.png`; before = the commit before "Prompt 34 L5" (`TierImpact` and `TierShot` off).
- Unity import: 83 new clips in `Resources/Audio/p34` (their import settings come from `Editor/P34AudioImport`; commit the generated metas) and 39 rebuilt GLBs (Part_wheel / Part_wheelb / Part_wing); `glb_check` already accepts them.
- Look (play or the lead's shots): a wheeled wreck's wheels and roll, a fighter's lost wing and spiral, a helicopter's spin, a bomber's slant, each crash landing on its blast; wreck lives 30-45 s and the 12 near the camera; the T4+ shake and the screen shake setting; the effects / dialogue volume rows.
