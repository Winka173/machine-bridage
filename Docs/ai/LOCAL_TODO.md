# Prompt 28: hooks for the local session (Game, UI, Editor)

The cloud session writes the Sim only. Each line: file, what, why.

- `Scripts/Game/Match/ModeSessions.cs` (every session with an `IObjectiveMode`): set `world.Intel.Objectives = mode`
  after `mode.Setup(world)`. Why: the World Model's OBJECTIVE_PRESSURE events need the capture points (28 A.4).
- Run CatalogCheck and the EditMode suite after merging pass 1 (`WorldModelTests` is new; balance.json gained `ai`).
- J (AI viewer overlays in the Sandbox) reads `world.Intel.For(team)`: `Own`/`Enemy`/`Threat[k]` grids
  (`Columns` x `Rows`, `CellCentre`), `Contacts` (confidence via `Confidence(now, ConfidenceDecay)`), `EnemyGroups`,
  `Front`, `Contested`, `Chokepoints`, `Warnings`, `Events`.
