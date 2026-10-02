# Prompt 30 report: in-battle story, match end, match rules, endless, neutrals, static audits

Passes 0-8 were done Sim-side by the cloud session (`cloud/p30-story`, merged at 6aa9542); the Unity side of L1, L2, L3,
L5 and L6 and these docs were done in the lead pass on `feature/p30-local`. Nothing was run: no match, no test, no
measure (the owner's rule); the tests were written. Details and reasons are in `Docs/DECISIONS.md` under "Prompt 30
(cloud, 2026-10-02, cloud/p30-story)" and "Prompt 30 local (lead pass, 2026-10-02)".

## 1. Pass 0 results (`Docs/checks/p30_precheck.md`)

1. **Acts.** `campaign.json` has `act` on all 15 chapters, four acts: I = 1, 2, 3, 13; II = 4, 5, 6, 14; III = 7, 8,
   9, 15; IV = 10, 11, 12. The chapter list and the chapter cards read it. Only text was wrong ("15 chapters in 3
   acts" in the design doc generator and a code comment); the "epilogue after chapter 9" is now "Kết mạch Thorne".
2. **Legendary** opened after the last entry of the operations list (c12m10 by data order only); it now opens on
   winning c12m10 by id.
3. **Dialogue queue** (prompt 23 H, Game layer): four priorities, gaps 9 s / 20 s, Full / Important / Off, a log of
   20 lines, six story moments at x0.5. Extended in place to P0-P4 (L12), no second system.
4. **Time scale.** One `Time.timeScale` for the Sim and the effects (the runner runs more or fewer fixed steps). With
   the battle frozen at RESOLVED, the end's slow motion only reaches the pictures.
5. **Modes** (before the pass): Survival endless with no win; catch-up up to +50 % income; Operations' score counted
   lost vehicles; Conquest 400 tickets, no clock; Deathmatch 480 CP worth, 12 min; King of the Hill 100 points, 15 min;
   Assault 300 s bank; Siege/Weekly by levelling the HQ; Defend/Endless waves; Boss Rush with an in-battle endless pick.
6. **Map data** is JSON with the Sim's own grid (no Unity NavMesh), so the map audit is a Python script.

## 2. Decisions taken without the owner

- Four acts kept from the data; "Kết mạch Thorne" is an interlude card after c9m10, before chapter 15, shown once (and
  in the Dossier timeline); the real epilogue stays after c12m10. Legendary opens on c12m10 by id.
- Dialogue: P0 System (whatever the setting, cuts any line), P1 Story/Warning (ignore the gap, wait for the line on
  show), P2 Event (kept 12 s), P3 Reaction and P4 Ambient (dropped after 8 s). System warnings stay HUD toasts.
- The subtitle became a portrait strip (portrait or side placeholder, two lines) at the bottom centre; everything it
  must not cover (objective timer, boss bar, big-attack warning) is in the top strip. Only "recon" has no portrait
  (all 21 script speakers have one).
- Match end: the world freezes on the resolving tick; the runner steps nothing after it; the presentation's clock is
  unscaled; durations are the middle of the sheet's ranges (7 / 4.5 / 3 s, loss 3.5 s); slow motion x0.3 from 1.5 s
  only for first and big wins; a tap skips after 0.75 s; a cut story line goes to the results and the log. Proxies
  retreating and turrets turning were left out (they need a view-side pose override).
- Match rules from the sheet into data (`matchRules`), no general "army gone = lost" rule; Deathmatch kills score
  min(baseCP, 18); Operations' losses part counts base CP lost; campaign stars ★1 win, ★2 the type's mastery, ★3 the
  mission's own side goal; leaderboards by keys in order, never a merged formula.
- Endless: Continue/End on the results of a won Defend, Survival, Boss Rush, the reward claimed first; stats-only
  growth; Survival finite at 10 waves with mini/main bosses; coins 18 (60) x 0.9^k within 600 a day; badges.
  CHECK left: Boss Rush's roster and limit do not match the sheet's "10 bosses, 30 minutes".
- Neutrals: the eight V1 rows; 0-2 kinds a battlefield, mirrored pairs on symmetric maps; on the field as ground rings
  with the capture sweep and on the minimap as squares; the supply drop announced 15 s ahead with a landing ring.
- Script: 193 missions in play order, one commit a chapter; speaker trigger extensions where the trigger sheet names a
  speaker the voice sheet leaves out (DECISIONS "L7").

## 3. Script lines per chapter (`Docs/story/script_stats.md`)

| Order | Chapter | Act | Missions | Lines |
|---|---|---|---|---|
| 1 | 1 | I | 10 | 81 |
| 2 | 2 | I | 13 | 106 |
| 3 | 3 | I | 14 | 110 |
| 4 | 13 (interlude) | I | 4 | 35 |
| 5 | 4 | II | 20 | 162 |
| 6 | 5 | II | 15 | 120 |
| 7 | 6 | II | 18 | 153 |
| 8 | 14 (interlude) | II | 4 | 44 |
| 9 | 7 | III | 19 | 148 |
| 10 | 8 | III | 16 | 128 |
| 11 | 9 | III | 16 | 130 |
| 12 | 15 (interlude) | III | 4 | 38 |
| 13 | 10 | IV | 16 | 134 |
| 14 | 11 | IV | 14 | 119 |
| 15 | 12 | IV | 10 | 93 |
| | **Total** | | **193** | **1601** |

The 23 game-deck missions are scripted on their original objectives (prompt 31 adds their own rules' lines).

## 4. Validator results left

- **0 errors** (budget, hard length, render estimate, word-for-word repeats, triggers outside allowedTriggers,
  missing language, translated proper names, the Icarus / Ellis / Thorne guard rails).
- **238 warnings, all "over the soft length"** (Vietnamese over 90 or English over 75 characters, under the hard
  limits of 110 / 90): 204 in chapter missions, 21 in interlude missions, 13 in side missions. Listed at the end of
  `script_stats.md`; left as written (they fit the two-line estimate).
- **Open:** the render check uses an estimate of 2 lines of 58 characters. The real strip width at the smallest
  supported screen, with the portrait and Large text, is to be measured in Unity and `RENDER_CHARS` set from it
  (LOCAL_TODO L2); lines over it would then show as errors.

## 5. Maps and modes flagged

### Maps (`Docs/checks/map_audit.md`, 100 map files, every mode version)

9 RED, 91 YELLOW, 0 GREEN. Prompt 30 L8 forbids changing maps, so the RED files are **reported, not fixed**; fixing
them is for the owner to decide.

| RED file | Why |
|---|---|
| borderbridge_conquest | disconnected navigation regions |
| borderbridge_sandbox | disconnected navigation regions |
| coralisles_siege | disconnected navigation regions |
| emberridge_conquest | disconnected navigation regions (also YELLOW exits) |
| emberridge_long | disconnected navigation regions |
| emberridge_sandbox | disconnected navigation regions (also YELLOW exits) |
| openpit_siege | disconnected navigation regions |
| swamp_siege | disconnected navigation regions |
| hydrodam_conquest | median path delta to the objectives 19 % (over 15 %) |

YELLOW: every file has "sightline" (P95 over the tank gun's 32 m; information only, the battlefields are open ground);
12 files have "exits" (a drop zone with fewer than 2 ways out): emberridge conquest and sandbox (above) and frostpeak,
landingbeach, redrock, rustyard, skyhold, each conquest and sandbox. No path-delta or neutral-value YELLOW.

Limits: a static measure shows no win rate, traffic jam, flow, real artillery value, AI lane choice, fight length or
performance; asymmetric files (siege, long) are reported by role, never 1:1.

### Modes (`Docs/checks/mode_static_audit.md`)

No RED or YELLOW: no symmetric mode (Conquest, Deathmatch, King of the Hill) is more than 20 % apart at 25/50/75/100 %
of its length (Conquest's band 1.13-1.14 from the enemy's x1.18 income; Deathmatch 0.90, King of the Hill 0.93). The asymmetric modes
(Assault, Siege, Weekly, Defend, Survival, Boss Rush) are reported by role. Theory only: no win rate is predicted.

## 6. Still for the local machine (LOCAL_TODO "Prompt 30")

Unity compile of the edited Sim and Game files; run DialogueTests, MatchEndTests, MatchRulesTests, EndlessTests,
NeutralTests, CatalogCheck once the owner allows test runs; measure the strip and set `RENDER_CHARS`; the owner's look
at the portrait strip, the match end and the neutral sites; export the design PDF.
