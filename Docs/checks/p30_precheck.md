# Prompt 30 pass 0: precheck (read only)

Read from the code and data on `feature/visual-overhaul` 91c3aa2 (cloud, 2026-10-02). Nothing was run.

## 1. Acts

- `campaign.json` `chapters[]` has `act` for all 15 chapters: act 1 = 1, 2, 3, 13 (interlude 1); act 2 = 4, 5, 6, 14
  (interlude 2); act 3 = 7, 8, 9, 15 (interlude 3); act 4 = 10, 11, 12. Four acts in the data.
- Act switches (prompt 20 C) read `act` (`Progression`, `MenuScreen.Campaign`); chapter cards are `comic.<n>` panels;
  the story timeline is `Docs/STORY.md` plus `CampaignText`.
- "3 acts" text left: `Tools/docs/programme.py` line 28 ("15 chương trong 3 hồi") and the comment at the top of
  `MenuScreen.Campaign.cs` ("nine chapters in their three acts"). `Docs/STORY.md` already lists four acts.
- "phần kết (epilogue) sau chương 9": `Tools/docs/programme.py` line 66. The game's real epilogue
  (`campaign.epilogue`) shows after the last operation switched on (c12m10 when all are on).

## 2. Legendary (Operations)

- `Game/Match/Operations.cs` `LegendOpen`: open once the last entry of `Big` (the operations in data order) is won.
  Data order ends with chapter 12, so this is c12m10 today, but only by the order of the list. `operations.json` says
  "Legend opens once the last operation of the campaign is won".

## 3. Dialogue queue (prompt 23 H, Game layer)

- `Game/Match/Dialogue.cs` `DialogueDirector`: priorities Story > Warning > Event > Reaction (4 levels). Story and
  Warning queue (queue of 6; a stale warning is dropped after 12 s); Event and Reaction are "now or never".
- Gaps: `Gap` 9 s and `BossReactionGap` 20 s, applied to Event/Reaction only, as a gap since the last chatter.
- Setting Full / Important (story + warning) / Off (story only): `DialogueSetting`, `Allowed`.
- Log of 20 lines (`LogSize`).
- Story moments: `MomentScale` 0.5, at most 3 lines / 14 s; `DialogueRules.MomentKeys` holds the six beats (c6m14,
  c5m10, c7m10, c9m10, c12m10 Varga, Icarus crash).
- Line sources: `RadioDirector` (mission `radio` lines by `RadioTrigger`: Start, Time, Capture, Lost, Boss, BossHalf,
  HqHalf, Stage, Reinforce, Win, Lose) and Radio events from the Sim (`SimEventKind.Radio`, priority in `Value`).
- No P0 level: system warnings are HUD toasts and big-attack warnings, outside the dialogue.
- Mapping to L12: P0 = system warning (not dialogue), P1 = Story, P2 = Warning/Event of the mission, P3 = Event
  reaction, P4 = Reaction/atmosphere. The queue rules to add: P1 ignores the gap but waits for the line on show; P3/P4
  dropped after 8 s instead of "now or never" only.

## 4. Time scale

- One `Time.timeScale` (`MatchRunner` line 717: `min(cinematics, DialogueTimeScale)`). The runner steps the Sim at a
  fixed dt and runs more or fewer steps by the scaled time, so the Sim and VFX share the pace. The simulation's results
  do not depend on it (fixed dt), but a slow-motion of the visuals slows the battle too. For the end sequence the Sim
  gameplay is frozen at RESOLVED, so a visual slow-motion there cannot change the result; a separate view clock is still
  needed for VFX that must keep normal speed while the battle runs (L3, local).

## 5. Modes now

- **Survival** (`SurvivalSession` + `SandboxMode`): endless; first wave at 20 s, then every 30 s / intensity; wave size
  3 + 0.9 (w-1), cap 14 + 1.5 w enemies (48); elites from wave 8. No bosses, no win; lost when the army is wiped out
  for a while or the drop zone is held by the enemy.
- **Catch-up**: `SimWorld.CatchUp` (quick modes): income up to +50 % (`EconomySystem.MaxCatchUp` 0.5) below 75 % of the
  enemy's army (minimum army 14); the underdog's one-off help after 240 s (`UnderdogRules`). The sheet's "+25 % max"
  for Conquest/Deathmatch is lower than today's +50 %.
- **Operations score** (`OperationScoring.Score`): 5000 win + 3000 x time under par + 2000 x (1 - lost vehicles / 20)
  + 2000 x HQ left, x tier and mutators. Losses count vehicles.
- **Conquest**: 400 tickets, bleed 0.6/s per point difference, kills cost 0.5 ticket per CP; no time limit.
- **Deathmatch**: 480 CP worth destroyed (a kill scores its price), 12 min; tie = draw (-1).
- **King of the Hill**: 100 points at 0.75/s sole holder, 15 min; higher score at the limit.
- **Assault**: bank 300 s, +240 s per sector, max 480 s, 60 s overtime while a live point is contested.
- **Siege / Weekly**: win by levelling the fortress HQ; lose on time (`SiegeMode`).
- **Defend / Endless**: Defend = AssaultMode with `PlayerDefends`; Endless = waves until the HQ falls.
- **Boss Rush**: bosses in a row; `EndlessOffer` and `EndlessChoice` 20 s exist already (`BossHunt.cs`).
- **Campaign**: per-mission goals (`MissionGoal`), star rules `starLosses`/`starTime` per mission.

## 6. Map data

- Maps are JSON (`Resources/Data/maps/*.json`); the Sim builds its own `NavGrid` (no Unity NavMesh). Python reads the
  JSON directly (`Tools/maps/build_maps.py` already checks reachability), so the map audit can be a Python script.
