# Tactics (prompt 28 H)

A tactic is a set of shared behaviour modules, never its own AI: attack readiness, cohesion, flank weight, pincer,
focus, main effort, spread, fire stance and hold distance, engagement band and kiting, artillery prep, fall-back and
counter-attack lines, pace and bounding overwatch, holding (points, base), waiting for air, saving CP, all together,
target groups, tower mode. The generator reads them from the sheet "Chiến thuật" ("Tác động lên AI": numbers by
pattern, flags by keyword); `aiBehaviour.tactics` in balance.json. Balanced has none: the standard thresholds.

## The 16 tactics (initial data)

| id | sheet name | CP % (armour, light, AT, artillery, AA, heli, air, support) | modules | opens | suits |
|---|---|---|---|---|---|
| `balanced` | Cân bằng | 25, 20, 12, 12, 10, 8, 5, 8 | (standard) | start | kade |
| `blitz` | Tấn công chớp nhoáng | 25, 30, 10, 5, 8, 10, 4, 8 | attackThreshold 0.9; cohesion 0 | chapter 2 | mendez |
| `firepower` | Hỏa lực áp đảo | 20, 12, 8, 30, 12, 5, 5, 8 | artilleryPrep 1.0 | chapter 3 | dahl |
| `depth` | Phòng thủ chiều sâu | 25, 15, 18, 15, 12, 5, 2, 8 | fallback 0.6; counterattack 1.3; hold 1 | start | brandt |
| `encircle` | Bao vây | 22, 28, 15, 8, 10, 10, 2, 5 | flank 1.6; pincer 1 | chapter 4 | adler |
| `bounding` | Yểm hộ luân phiên | 30, 25, 12, 10, 10, 5, 0, 8 | pace 0.7; bounding 1 | chapter 3 | kade |
| `ambush` | Phục kích | 15, 15, 30, 10, 12, 8, 2, 8 | holdFire 0.6; stance HoldFire | interlude 1 | kerr |
| `hit_and_run` | Bắn và chạy | 10, 25, 25, 10, 10, 12, 3, 5 | engage [0.9, 1.0]; kite 0.7 | chapter 5 | mendez |
| `breakthrough` | Tập trung đột phá | 40, 15, 8, 12, 10, 5, 2, 8 | mainEffort 0.7; heavyLead 1; dropSecondary 1 | chapter 6 | reyn |
| `dispersal` | Phân tán | 15, 25, 15, 15, 10, 10, 3, 7 | focus 0.5; spread 2.0 | chapter 6 | venn |
| `air_superiority` | Ưu thế trên không | 15, 12, 8, 8, 20, 10, 22, 5 | waitAir 1 | chapter 3 | reyes |
| `sead` | Chế áp phòng không trước | 15, 12, 10, 15, 10, 10, 20, 8 | targets ['AntiAir']; seadCards 1 | chapter 7 | reyes |
| `attrition` | Tiêu hao | 10, 10, 20, 30, 10, 5, 5, 10 | attackThreshold 1.5; engage [0.9, 1.0]; standoff 1 | chapter 8 | quist |
| `decapitation` | Săn đầu | 12, 28, 15, 10, 8, 15, 7, 5 | flank 1.6; targets ['Support', 'Artillery'] | chapter 9 | kerr |
| `base_defence` | Bảo vệ căn cứ | 25, 15, 20, 15, 15, 2, 0, 8 | hold 1; holdBase 1; towerMode Lead | start | brandt |
| `all_out` | Tổng tấn công | 30, 20, 10, 10, 10, 8, 7, 5 | cpSaving 1; together 1; massSupport 1 | chapter 10 | okoye |

Generals: varga -> `breakthrough`, orlov -> `firepower`, kessler -> `attrition`, venn -> `dispersal`, wolff -> `air_superiority`, thorne -> `balanced`, aurel -> `all_out`, brandt -> `depth`, default -> `balanced`

## Rules

- **Choosing (H.4).** One tactic before the battle (`ConquestAi.Tactic`); a general without one uses its preference
  (sheet; Brandt and generals without a row: depth or balanced).
- **Force shares (H.5).** By CP spent, not vehicles. Soft target: MISMATCH events move a group's target up to 15
  points; groups the deck lacks give their share to the rest; the tactic's preferred cards first within a group.
- **Switching (H.6).** Cooldown `params.tacticCooldown` (50 s, sweep 45-60), free in Boss Rush breaks; a transition
  of `params.tacticTransition` (5 s): no new attack, squads regroup, attacking squads lose their momentum. New shares
  apply to later purchases only.
- **Knowing the enemy's tactic (H.8).** Only while a recon, UAV or scout helicopter sees the other side.
- **Fire stance (H.9).** Free, confirmed targets, hold fire; Ambush holds until the enemy is inside 60 % of reach or the
  squad is hit.
- **Per squad (H.10).** After chapter 6, `SquadTactics`: a squad may play its own tactic with its own cooldown.
- **Merging (H.3).** `TacticFingerprintSweep` measures 8 fingerprint numbers over 5 seeds; pairs closer than
  `world.mergeThreshold` (0.15) merge (`MergedInto`) or get a more distinct core behaviour. Not run yet; no merge yet.
- **Difficulty (K).** Easy never switches; Hard switches when clearly losing; Very Hard counters the tactic its scouts see.
