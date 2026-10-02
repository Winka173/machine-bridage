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
