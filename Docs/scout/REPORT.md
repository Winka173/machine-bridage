# Scout Target Designation: report (10/10)

Branch `feature/scout-designation`, worktree `MachineBrigade-art3`. Tóm tắt (vi): không có Fog of War trong source nên không xóa gì; scout đánh dấu 1 mục tiêu (+10% sát thương trực tiếp, boss +5%); toàn bộ test và đo lường chỉ được viết, chưa chạy (chủ dự án tạm dừng test).

**Test status: all tests, replays, regressions and measurements are "not run - owner paused testing".** Only `dotnet build Tools/simbuild/Sim.csproj` ran (0 errors, Temp/simbuild untracked). Game-layer C# (HUD) and the EditMode test file and the regress harness entry were checked by reading only (C# 9 syntax, no records/new target-typed beyond C# 9).

## 1. Files changed
Sim: `Combat/DesignationSystem.cs` (new), `Entities/Vehicle.Designation.cs` (new), `Content/SimTunables.ScoutDesignation.cs` (new), `Content/SimTunables.cs` (+2 lines), `Content/Catalog.Extra.cs` (+1), `Content/VehicleDef.Extra.cs` (+1 property), `SimWorld.cs` (property, ctor, 2 Step calls, public `MarkedTargets`), `Combat/DamageSystem.cs` (+2 lines in `Apply`), `Combat/CombatSystem.cs` (+2 lines in `Score`).
Data: `Resources/Data/tunables.json` (section `vehicles.scoutDesignation`), `Resources/Data/balance.json` (`designationRange` on three ids).
HUD: `Game/Hud/EventMarkers.cs` (`DesignationMarks`), `Game/Hud/BattleHud.Events.cs`, `Game/Match/MatchRunner.EventHud.cs`, `Resources/UI/Screens.uss`, `Game/Hud/Strings.cs`.
Tests/tools: `Tests/EditMode/ScoutDesignationTests.cs`, `Tools/simbuild/regress/ScoutDesignation.cs` (+ `Program.cs` mode `scout`).
Docs: `Docs/scout/AUDIT.md`, this report, DECISIONS section, CHANGELOG line.

**AI files touched (other agent is reworking the AI):** none under `Sim/AI/`. The only target-scoring hook is `Combat/CombatSystem.cs`, the `Score` method: one comment and one line, `score *= _world.Designation.PriorityFor(v, other);` right after `P5Worth` (before the distance divide). `Feasibility` (`CombatSystem.P0A.cs`) is untouched.

## 2. Existing mechanisms reused
`StatusKind`/status pattern (studied, deliberately not reused, see below), `HitInfo.Kind` (Direct/Splash/Pierce/Strike/Burn split already exists), `DamageSystem.Apply` pipeline, `Vehicle.IsVisibleTo` (the sim's stealth/vision), `CombatSystem.Score` and `Feasibility`, `SimWorld.Tick`/`VehicleList`, the tunables registry (`SimTunables` Entry + tunables.json), balance.json vehicle keys read in `Catalog.Extra`, the `GeneralTags` pooled-label pattern and the `crosshair` kit icon.
Why not `StatusKind.Mark`: it also gives artillery longer reach and tighter spread and boosts every hit kind; reusing it would break the "no artillery spread/reach change, no splash bonus" rules. It is a different function (equipment laser designator); the two can coexist.

## 3. New classes and functions
`DesignationSystem` (`Step`, `Refresh`, `Eligible`, `PickScore`, `Place`, `Release`, `IsMarkedFor`, `PriorityFor`, `Multiplier`, `Marked`), `DesignationSlot` struct, `Vehicle.DesignationSlots/DesignationTarget/DesignationNextTick`, `VehicleDef.DesignationRange`, `SimTunables.Vehicles.ScoutDesignation`, `SimWorld.Designation/MarkedTargets`, `DesignationMarks` (HUD pool).
Damage order (documented in the class): HitMultiplier (armour, penetration, face, table) -> smoke -> equipment Outgoing -> commander Outgoing -> **designation** -> weapon bonuses -> boss air -> HitVehicle (cover, domes, shield, barrier, parts, phases). Direct/Pierce only.

## 4. Data and parameters
tunables.json `vehicles.scoutDesignation`: damageBonus 0.10, bossDamageBonus 0.05, markSeconds 5 (100 ticks), retargetSeconds 2 (40 ticks), maxTargetsPerScout 1 (clamped), markedPriorityMultiplier 1.10, switchMargin 1.35, weightThreat 3, weightArtillery 2.5, weightAirDefence 3, weightHeavy 2, weightSupport 1.5, weightOther 1, rangeFalloff 0.25, flags stacking false, applyToSelf false, affectsDirectDamage true, affectsSplashDamage false, affectsDamageOverTime false. balance.json: `scout_jeep` 35, `recon_drone` 55, `scout_heli` 45 (real ids confirmed). affectsSelfDamage/friendlyFire/scripted are structural (always excluded; no attacker or same team returns 1). Weights and margin are my additions to implement the owner's priority list; they are tunable.

## 5. Fog of War removed
None: grep found no FoW code (only `RenderSettings.fog` in editor shot tools and the weather look). Sim visibility, stealth, radar, reveal kept. 3D enemies are not hidden by the game; the minimap shows every enemy (unseen ones dimmed), kept as a lock hint.

## 6. Unit tests and replay
`ScoutDesignationTests.cs` covers prompt section 14 items 1-12 and 15, 14 and 13 in 14 tests (`OneScoutMarks...`, `TwoScouts...`, `ScoutOfSideA...`, `ScoutDoesNotBenefit...`, `BossTakesFive...`, `SplashAndDamageOverTime...`, `MarkIsRecalledWhenTheTargetDies`, `MarkLapsesExactly...`, `ScoutSwitching...`, `SecondScoutKeeps...`, `TargetOutOfRange...`, `AiDoesNotFireOutOfReach...`, `StealthKeepsItsCombatBehaviour`, `SameSeedSameStateHash`, plus `RangesComeFromData`). **Not run - owner paused testing.** Replay hash: **not run**. The state hash does not mix the mark (HP carries its effect), so no existing baseline should move unless scouts are present.

## 7. Balance numbers before/after
**Not run - owner paused testing.** Harness ready: `Tools/simbuild/regress` mode `scout` (`MB_SET=all|light|heavy|artillery|air|siege|boss`, `MB_SEEDS`), variants none / jeep / drone / heli / 2x jeep / mixed against six opponent sets, columns damage, damage per CP (scout CP counted), kill time, marked ticks, scout survival, winner. The harness entry itself was not compiled (only the Sim project was built).

## 8. Open problems
- Nothing measured: bonus size, scout survival, and whether scouts dive are unknown; no scout movement/doctrine change was made (prompt 8 only if needed).
- Tests unrun; test code and the harness were not compiled. HUD code not compiled (Unity only); the tooltip texts hardcode 10 % / 5 % instead of reading the tunables.
- `maxTargetsPerScout` above 1 is not supported (clamped). Slots: 4 scouts per target; a fifth cannot mark it (no bonus lost, as it never stacks).
- Burn with `affectsDamageOverTime` true would boost only burns that carry an attacker; default is off.
- The pipeline factor is applied to the amount before shields/domes, so a marked target's shield absorbs 10 % more per hit (a design consequence of the placement).
- The mark does not reveal stealth and requires the target to be visible to the scout's side.

## 9. Proposed, not applied
- Neutral radars: `radar_station_prop` only widens sight; propose converting them into capture-bonus or counter-battery posts after the owner decides (touches capture goals and AI).
- Guard tower, radar, jammer stats unchanged; no stealth changes (no measurement evidence).
- If scouts prove too weak: raise the bonus only after the measure; or let a scout also mark during ordered attacks. If too strong: lower `markSeconds` or make drone range 50.
- A tunables-driven tooltip (format the 10 / 5 % from the data) and a minimap ring for marked targets (kept off to avoid icon clutter).
