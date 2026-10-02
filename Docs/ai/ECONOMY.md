# In-battle economy (prompt 28 I)

Soft pressure so neither side piles up an army and no battle stands still, while every tactic still has to fight.
Numbers: balance.json `ai.economy` (generated from the sheet "Cân bằng kinh tế"); they are starting values for the sweeps.

## Pieces

| Rule | Where | Starting values |
|---|---|---|
| Hard caps (I.1) | existing vehicle and aircraft caps | 32 ground, 6 aircraft a side; no tactic loosens them |
| Upkeep (I.2) | the existing supply upkeep, `TeamEconomy.Upkeep` (prompt 7) | by army CP against the supply line; unchanged. The owner amended prompt 28: no second upkeep system (the army bands of pass 5 were removed in prompt 29 pass 0) |
| CP bank (I.3) | existing bank | unchanged (Vault higher) |
| Use it or lose it (I.4) | `AiCommander.AttackThreshold` | at the cap with a full bank the attack threshold falls to 0.9 over 30 s |
| Victory points (I.5) | Conquest's ticket bleed | already there: nothing added |
| Pressure tiers (I.6) | `BattleEvents` (prompt 23) | quiet 30/50/70/90 s: points x1.5, crate in the middle, barrage on the passive side, armies revealed; a big fight (600 health lost in 5 s) resets |
| Final phase (I.7) | `ConquestMode.FinalPhase` | when the losing side would run out within 120 s, points count x2 |
| Defensive tactics' cost (I.8) | behaviour, plus hit-and-run spread x1.3 while backing off | dispersal focuses half |

## Targets (O.2) and what to tune

Average army 60-80 % of the cap; at the cap under 30 % of the time; fighting over 60 % of the battle; the loser can
still turn it. If armies are too big: tighten the supply line (`economy.supply`, the existing upkeep) or shorten the use-or-lose ramp. Too little fighting: shorten the
tiers. A tactic pair that stalls: raise the cost of the defensive tactic in that pair first. None of this has been
measured yet (owner's rule); `AiParamSweep` with `MB_SWEEP_KEYS=economy.` sweeps these.
