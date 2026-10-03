# Bomb-run fix report (Docs/prompts/bomb_run_vi.txt, passes 0-4)

Done 2026-10-03 in lane B (pass 0 in lane C), merged through lead/integration. Not a new prompt: the owner's bug, "bombers
dump every bomb on one point". No battle was simulated; the drop traces come from the EditMode test
MachineBrigade.Tests.BombStickTrace (the game's own CombatSystem.Launch on an empty field). Notes: DECISIONS "Ném bom rải
thảm" (passes 0, 1, 2, 2 follow-up, 3, 4).

## 1. The cause (pass 0, read in the code)

1. **Free-falling bombs were re-aimed bomb by bomb, but packed too tight.** CombatSystem.Launch aimed each bomb at
   BombImpact (the aircraft's position plus its speed over the fall), so a stick was only speed x BurstInterval apart:
   the strategic bomber's 22 m/s x 0.2 s = 4.4 m (3.5 m at the run's 0.8 throttle) against a 10 m core. Seven bombs in
   ~20 m, core over core: on screen one pile.
2. **The boss bomb bays really did drop on one point.** p26_roc_roc_bombs / p26_roc_main_roc_bombs (argus, garuda,
   command_airship) inherited boss_howitzer and flew as shells: all eight aimed at the target itself, only the scatter
   apart.
3. Friendly safety dropped the whole stick, never a single bomb. The heavy bomber's card said "twelve bombs"; the data
   drops seven (GuideText.cs).
4. Guided bombs (JDAM, SDB, UMPK) land on one point by design; the supports' airstrikes and the bosses' strip attacks
   already laid sticks.

## 2. Before / after (Docs/export/bom_2026-10-03)

Before = the pass 0 trace (`vet_tha_truoc_luot2.csv`); after = the Unity trace after the fix (`vet_tha_unity.csv`).
Means of 3 seeds, aim (0, 0), heading 0. Distinct points: impacts closer than 1 m count as one. Stick length: along the
track. Vehicles hit: of 5 (core or edge of at least one bomb; vehicles as points), for the spec's two standard
formations: 5 vehicles 8 m apart in a row along the track, and 5 in an 8 m cluster, centred on the aim. Computed by
`Tools/export/bom.py compare_rows` (also the PDF section 22).

| weapon / carrier | bombs | distinct points | stick length (m) | hit, row 8 m | hit, cluster 8 m |
|---|---|---|---|---|---|
| bomber_payload / heavy_bomber | 7 | 7 -> 7 | 19.7 -> 65.7 | 4.3 -> 5 | 5 -> 5 |
| p26_roc_main_roc_bombs / argus | 8 | 5.7 -> 8 | 3.8 -> 76.8 | 5 -> 5 | 5 -> 5 |
| p26_roc_main_roc_bombs / command_airship | 8 | 5.7 -> 8 | 3.8 -> 76.8 | 5 -> 5 | 5 -> 5 |
| p26_roc_main_roc_bombs / garuda | 8 | 5.3 -> 8 | 3.6 -> 76.8 | 5 -> 5 | 5 -> 5 |
| jet_bombs / stealth_naval_strike | 2 | 2 -> 2 | 9.1 -> 9.0 | 3 -> 3 | 5 -> 5 |
| jet_bombs / attack_jet, elite_attack_jet | 1 | 1 -> 1 | 0 -> 0 | 2 -> 2 | 4.7 -> 4.7 |
| stealth_payload / stealth_bomber (POINT) | 2 | 2 -> 2 | 1.5 -> 1.5 | 3 -> 3 | 5 -> 5 |
| single bombs (guided_bomb, glide_fab500, cluster_at_bomb, bunker_buster_bomb, thermobaric_bomb) | 1 | 1 -> 1 | 0 -> 0 | unchanged | unchanged |

Reading it: the stick now covers 66-77 m instead of 4-20 m, so it catches a column strung along the road and the whole
of a spread position; against a tight 8 m cluster both old and new hit all five (the new stick spends its outer bombs
on empty ground, as a real stick does; on fewer than 3 targets it is cut to max(2, ceil(n/3)) bombs). The attack jets'
trace drops one bomb a pass (their two-bomb salvo is cut by the trace's stores; the stealth strike jet shows the pair
8.8 m apart): to look at in play. No balance change was made (the spec's pass 1 rule); Bom_ket_qua_vung is there for the
owner's balance look.

## 3. What changed

**Data (pass 1).** Every bomb weapon carries a `stick` block in balance.json (mode, bombs, spacing = 1.1 x core,
length, interval = spacing / release speed, release speed, fall time, lead, heading, anchor, drop, jitters, overlap,
width, min targets, safety, straight-flight time, exit, bay-open time, warning shape), checked against its formulas on
load. Damage, bombs per pass, cooldown and loads unchanged.

| weapon | carriers | mode | n | spacing | stick | interval | warning |
|---|---|---|---|---|---|---|---|
| bomber_payload (FAB-500) | heavy_bomber | STICK, overfly, axis | 7 | 11 m | 66 m | 0.625 s | STICK_RECT |
| jet_bombs (FAB-250) | attack_jet, elite_attack_jet, stealth_naval_strike | STICK, overfly, approach | 2 | 8.8 m | 8.8 m | 0.344 s | none |
| p26_roc_main_roc_bombs | argus, garuda, command_airship | STICK, bay, axis | 8 | 11 m | 77 m | 0.3 s | STICK_RECT |
| p26_roc_roc_bombs | (the small bay) | STICK, bay, axis | 8 | 5.5 m | 38.5 m | 0.3 s | STICK_RECT |
| stealth_payload, guided_bomb, glide_fab500 | guided | POINT | 1-2 | - | - | - | none |
| cluster_at_bomb, bunker_buster_bomb, thermobaric_bomb | glide_bomber | POINT (one bomb) | 1 | - | - | - | ring (bunker buster, ODAB) |

**Sim (pass 2).** Bomb i lands at the stick's start + direction x i x spacing + its seeded jitter, the line fixed when
the first bomb goes (a bomber's position plus its lead; a boss bay's line round its aim); the direction is the target
cluster's main axis (2 x 2 covariance, within 45 degrees of the approach) or the approach; friendly safety skips single
bombs; few targets drop max(2, ceil(n/3)); the bomber holds heading, speed and height for its straight-flight time and
runs in along the axis; the boss bays drop Bomb rounds, not shells; the cycle (first bomb to first bomb) is kept. Nine
EditMode tests (BombStickTests), plus the four follow-up test fixes.

**View (pass 3, no Sim change).** Bay doors open on the hinged models (heavy_bomber, command_airship; the other bombers'
doors are merged meshes without a hinge and stay shut); each bomb falls on its interval with a thin trail; the blasts
chain along the line by their tier (T4 for 400-500 kg), the far bombs of a long stick one detail level lighter inside
the tier budget; one STICK_RECT warning rectangle for the whole stick (thin edge, faint fill, darker core band, the
flight line dashed, the next bomb's countdown ring) giving up its ground as the bombs land; the blasts' sound walks
along the stick with one shared tail and one falling whistle. BombStickViewTests (written, not run).

**Docs (pass 4).** Aircraft cards say "thả N quả, cách nhau X m, dải Y m" from the data ({{stick}} in GuideText,
filled by StickLines; the stale "12 quả" / "twelve" gone, EN and VI). File 01 of the full export gains the sheet
Bom_rai_tham linking the bomb export (Docs/export/bom_2026-10-03). The design document gains section 22 "Ném bom rải
thảm" (Tools/docs/bomb_run.py: the stick parameters from the data, this before / after table, and the before / after
stick pictures from EffectShots.FxBatch, grey "shot pending" boxes until the lead renders them).

## 4. Own decisions

- The strategic bomber keeps its 7 bombs (owner item 1); the card follows the data.
- The stealth bomber's "3 very large bombs, short stick" in the spec predates the data (2 guided JDAMs): kept POINT by
  the spec's own guided rule.
- Boss bays keep their 0.3 s ripple (an airship's 4.5-6 m/s would stretch an 8-bomb stick past its whole cycle); their
  release speed is the bay's nominal walk (spacing / 0.3 s), their lead 0, their stick laid round the aim (CENTER).
- Supports and boss strip attacks keep their own code and data (airstrike overlap 0.5 noted for the balance look).
- Few targets cut the stick to max(2, ceil(n/3)) as the spec says; this lowers a lone target's damage per pass.
- The view reads the sticks from the fired events only (the Sim's stick state stays internal): a skipped or cut bomb's
  warning section is let go a moment after its release time.
- Far-bomb lightening touches only the tier overlay and the lingering smoke of sticks of 6+ bombs beyond 35 m from the
  view (12+ bombs beyond 70 m: flash and rings only); a round's own blast is never smaller.
- The bomb export stays its own folder, linked from file 01 (Bom_rai_tham), so the full export's coverage and its
  foreign keys are untouched.

## 5. To look at in play

The heavy bomber's release speed (the data assumes the run's 0.8 throttle), its axis run-in, the few-target cut, the
attack jets' pair, the bay doors' swing direction on both models, and the rectangle's readability at the Low graphics
setting. Unity command for the stick pictures: DECISIONS "Ném bom rải thảm (pass 4)".
