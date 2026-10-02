# Prompt 28: hooks for the local session (Game, UI, Editor)

The cloud session writes the Sim only. Each line: file, what, why.

- DONE 2026-10-02 (local, bf234c3+1): `Scripts/Game/Match/ModeSessions.cs` (every session with an `IObjectiveMode`): set `world.Intel.Objectives = mode`
  after `mode.Setup(world)`. Why: the World Model's OBJECTIVE_PRESSURE events need the capture points (28 A.4).
- CatalogCheck DONE 2026-10-02 after pass 1 (OK: 241 vehicles, 371 weapons); the EditMode suite waits for the owner. Run them after merging pass 1 (`WorldModelTests` is new; balance.json gained `ai`).
- J (AI viewer overlays in the Sandbox) reads `world.Intel.For(team)`: `Own`/`Enemy`/`Threat[k]` grids
  (`Columns` x `Rows`, `CellCentre`), `Contacts` (confidence via `Confidence(now, ConfidenceDecay)`), `EnemyGroups`,
  `Front`, `Contested`, `Chokepoints`, `Warnings`, `Events`.
