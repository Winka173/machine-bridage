# Machine Brigade AI (prompt 28)

The AI of every vehicle, tower and boss, in three layers over one shared picture of the battlefield. It only needs to
look smart to the player: readable, stable decisions that commit, no clumping, no standing about without a reason.
Decisions and their reasons: `Docs/DECISIONS.md`, sections "28 1" to "28 5". Source research:
`Docs/ai/Machine_Brigade_AI_Research.xlsx` (generated into balance.json by `Tools/ai/import_ai_xlsx.py`).

## Layers and rhythm

| Layer | Where | Rate | Decides |
|---|---|---|---|
| World Model | `Sim/AI/WorldModel.cs` (`SimWorld.Intel`) | ~2/s per side, on demand | strength, composition, threat layers, contacts with confidence, enemy groups, front, chokepoints, warnings, events |
| General | `Sim/AI/Commander.cs` (`AiCommander`, in `ConquestAi`) | 1/s | objective, effort, secondary task, attack window, squad tasks, tactic, buying shares, supports, hints |
| Squads | `Sim/AI/Squads.cs` (`SquadLayer`) | 4/s | one of 9 actions by score, 7 states, formation, focus, emergencies |
| Units | CombatSystem target score (every tick); `SquadLayer.Units.cs`, `Commander.Units.cs` | tick / 4/s / 1/s | target, facing, short moves, scouts, artillery scoot, aircraft approach |
| Towers, bosses | `CombatSystem.P28Structures.cs`, `Bosses/BossSystem.P28.cs` | tick / 1/s | targeting modes, boss behaviour types, big-attack aim, facing, escorts |

`TacticalAi` (prompt 13) keeps its helpers (rearming, crates, breaching, support placement, artillery standoff, boss
focus, demolition) and the aircraft; with `Layered` on it no longer moves ground vehicles. `ConquestAi.LayeredDefault`
switches every commander back to the old AI for comparison.

## World Model

A grid of `ai.world.cell` (10 m) per side. Own strength is the catalog's Power times health share; enemy strength comes
from contacts, each with last seen, age and confidence (1 - age x decay). A contact whose last cell is seen empty is
"displaced" (known, not placed); "not seen" (Unknown) differs from "seen lately and none" (ConfirmedAbsent). Threat
layers: anti-air, anti-tank, artillery, splash, each painted over the contact's reach. Events (sheet "Sự kiện"):
THREAT, OPPORTUNITY, WINDOW, MISMATCH, OBJECTIVE_PRESSURE, each with reason, priority, confidence, expiry and area.
No AI reads the raw map: the general and squads read events and the shared tables.

## General

Plans are committed for `params.minCommit` unless an emergency (THREAT >= 90, a boss phase). The attack window opens
on own/enemy strength over the tactic's threshold (lowered by use-or-lose) or a WINDOW/OPPORTUNITY near the objective,
and is committed too. The main effort's share of strength goes to the primary objective; the rest holds the secondary
(own artillery, a pressured point). Difficulty (`AiSkill`) changes reaction delay, memory, spreading, flanking, focus
and when the general switches tactics.

## Squads

Valid actions only (filtered before scoring): ATTACK, HOLD, FLANK_LEFT/RIGHT, OVERWATCH, REPOSITION, SUPPORT, JOIN,
REGROUP. A score 0-100 is a base plus named factors (the sheet's plus and minus columns, weighted by the tactic and the
task). Anti-churn: change only when the current action is invalid, an urgent event happens, an idle reassessment runs,
or the new score beats the current by `params.switchMargin` after the commitment. Emergency Reposition is not a state:
dodging a warning ring resumes the same action; gathering on friends when overwhelmed has a cooldown. Nothing looks at
health: no retreat for a squad or a vehicle.

## Determinism and the viewer

Squads, members and contacts are walked in id order; options in a fixed order; ties keep the first; no unseeded random
draw (`SimWorld.AiRandom(team, layer)` is the per-layer stream for later tie-breaks). `SimWorld.AiLog` keeps the latest
"VÌ SAO" per decision maker (choice, score, top 3 plus, top 2 minus, runner-up), per-squad switch counters with a
warning above `world.churnWarn` a minute, and a replay log of plans, tactic switches, emergencies and actions. The
viewer overlays (J.1) are drawn by the Game side.

## Tests and tools

`WorldModelTests` (pass 1), `AiScenarioTests` (O.4, Explicit), `AiParamSweep` (L.3), `TacticFingerprintSweep` (H.3,
O.5). None has been run yet: they wait for the owner's go.
