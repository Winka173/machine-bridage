# Design decisions

Choices made while building the base, roster, tower, campaign, mission and Operations work
(prompts 1–6), where the brief left room or where a stand-in is used for now. Newest at the
bottom of each section.

## 1. Bases as a loadout

- **The HQ replaces both camp bastions.** It is one `headquarters` vehicle (9000 hp,
  Structure armour) with the bastion's twin heavy gun, twin 30 mm flak on the roof and a
  coaxial MG. It uses the `command_hq` model for now; a dedicated HQ model comes with the
  tower models in prompt 3.
- **Fortification points, not counts.** Every tower carries `"fort": {"points", "weight"}` in
  balance.json: light 1–2, medium 3, heavy 4–5. HQ levels 1–5 give 6/8/10/12/14 points and
  1/1/2/2/3 utility slots (`base.levels`). All levels are open until the campaign gates them
  (prompt 4).
- **Hardpoints live in the map data** (`bases[].slots`, per team, with a size and a facing). A
  tower goes only into a slot at least as big as its footprint (`max(length, width)`). The
  loadout fills slots front first (nearest the enemy HQ), heaviest towers first.
- **Flying a tower back in.** A destroyed tower's slot can be re-called for
  `ceil(points × cpPerPoint)` CP (`cpPerPoint` 1.0, the brief's 50% × points × 2 CP), 45 s
  after it fell or was last called, landing 4 s later. The HUD shows a rail button only while a
  slot can be called; the commander AI rebuilds the front slot when its army is at least 12 CP
  and it keeps 4 CP spare.
- **Roles by mode** (`base.roles`): Conquest, King of the Hill and Deathmatch are *Anchor*
  (the HQ cannot fall); Assault and Siege are *Target* (the defender's base is the objective,
  the attacker's an anchor); Defend and Endless are *Defend* (losing the HQ loses the battle);
  Survival, Boss Rush and the campaign default to *None*. A campaign mission opts in with
  `playerBase` / `enemyBase`.
- **Fire rule.** Strikes into an enemy home zone stay refused, except on a *Target* or
  *Defend* base (Siege, Assault, marked campaign missions), which can be shelled.
- **Outposts.** A mission marks points with `"outposts"`; the map gives such a point up to two
  `outpost` slots. Once the point is owned, the side can set it up for 6 CP; it then takes
  towers flown in for CP and becomes a secondary drop zone (the most forward one wins). Losing
  the point destroys its towers. Marked for now: m10 Ironport (town) and m14 Jungle Pass (west);
  the new campaign (prompt 4) will mark more.
- **The enemy's loadout** is drawn by `BaseLoadout.ForAi(difficulty, style, seed)`: HQ level
  by difficulty (Easy 2, Normal 3, Hard 5), towers by weighted draw from a style
  (`default`, `armour`, `artillery`, `air`) within the budget, at least one anti-air tower once
  half the budget is spent. The style is the hook for the commander personalities of prompt 4.
- **Tower sense in the AI.** Towers weigh in the odds of going into their reach (1.4× needed);
  the line stops at the edge of their guns until together and strong enough, giving its
  artillery 35 s on them first, or goes in after 70 s if it is at least a match. Flankers and
  crate runners keep out of tower reach. `TacticalAi.TowerSense` can be turned off only to
  measure the difference.
- **Towers kept as they are.** The existing towers carry points now; `point_tower` is kept only
  as a capture-point watchtower and is left out of loadouts (it merges into `guard_tower` in
  prompt 3). `FortDef.Tier` and the utility kind are in place for prompt 3.

## 2. Roster cleanup and balance

- **Merges.** APC → IFV, APS tank → battle tank, Grad → MLRS, howitzer → SP artillery,
  240 mm mortar → siege tank, carpet bombing → airstrike. The merged vehicle defs and the
  carpet bombing support are gone from the catalog; `CardMerges` keeps the old ids so saved
  progress and decks move across. The sky gunship stays in the catalog only as the Gunship
  item's aircraft; it is no longer a card.
- **What the target card took over.** The IFV now takes points 3× as fast and pops smoke when
  hit (the APC's job), and replaces the APC as a starter card. The MBT keeps its stats; APS
  tank owners get an Epic Trophy APS module instead. Elite APC now pairs with the IFV; the
  elite Grad keeps its own model and is paired with the MLRS only for its army cost (the elite
  MLRS stays the MLRS's elite).
- **Save migration** (`PlayerProfile.MigrateRoster`, once per save): the card it became gets the
  unlock, the blueprints and the higher rank; the coins and blueprints spent on the lower rank
  come back (the blueprints as the new card's). A retired card's coins come back and its
  blueprints turn universal. Cards bought with coins that no longer exist (sky gunship 4,500,
  carpet bombing 3,000) are refunded in full. Saved decks swap old ids for the new card.
- **Siege tank stays premium.** Players who had unlocked the 240 mm mortar get the siege tank.
  New players buy it as before. The campaign unlock slots freed by the merges went to the
  new cards (command vehicle m10, wheeled gun and counter-battery radar m11, long-range SAM m13,
  UAV scan m06, field tower m12, remote mines m16, SEAD m15).
- **Early missions get no harder.** In m00–m05 the enemy's APC became an armoured car. Later
  missions use the IFV. The player's placed unit in m02 is an IFV.
- **Shop.** The shop now lists every premium card (siege tank, ballistic launcher and heavy
  attack heli were buyable only from their locked card before).
- **Lancet.** ×2 damage on the artillery class and on vehicles that have stood still 3 s
  (the bonuses never stack). Fixed defences do not count as parked.
- **Iron Beam.** Point defence: 1 interceptor that reloads in 1.2 s, 30 m around it, taking
  missiles, drones and every rocket (artillery rockets too). Measured over 5 seeds, a 4-tank group
  under ATGMs, a Lancet, an MLRS and a helicopter lost 5,528 HP in 30 s with the beam against
  7,136 HP with two AA vehicles (8 CP), with 28 intercepts a minute. It is worth more than 8 CP,
  so it stays at 9 CP.
- **Ka-52.** Vikhr 55 m, and `standoff`: it holds at 60–97 % of that range, on the side of the
  target furthest from any known anti-air it outranges (anti-air that reaches as far is not
  avoided: there is no standing outside it).
- **New vehicles** (HP in data is the in-game figure ÷ 2.5 toughness):
  - Command vehicle: 6 CP, 560 (1,400) HP, light armour, 8 m/s, roof HMG. Friendly vehicles
    within 25 m fire 10 % faster (the best aura counts; auras do not add up). After 5 s standing
    still it is a drop zone, landing deliveries 7 m behind it. One per side; the AI buys it once
    it has 5 vehicles and keeps it with the support group behind the line.
  - Wheeled gun: 7 CP, 440 (1,100) HP, 12 m/s, 105 mm 300 AP / 4.6 s (65 DPS on heavy), 38 m,
    ×1.25 on a side or rear hit (on top of the usual side and rear factors).
  - Counter-battery radar: 5 CP, 360 (900) HP, HMG only. Enemy artillery that fires within
    120 m shows for 8 s, and our artillery does +15 % to it. This reuses the equipment trait's
    reveal status (the better of the two counts when both are present). The AI buys it only
    against enemy guns.
  - Long-range SAM: 11 CP, 440 (1,100) HP, 6 m/s, one 600-damage missile every 8 s, air only,
    95 m, minimum range 20 m, sight 80 m.
  - The models were built for all four and for the HQ (`Tools/blender/mb_phase2.py`), with a
    Blender muzzle check (`check_muzzles.py`). The HQ's flak is listed twice so both barrels fire.
- **Supports:**
  - UAV scan: 2 CP, 45 s. A drone circles the mark and shows everything within 30 m for 10 s,
    stealth, hidden units and mines too.
  - Remote mines: 5 CP, 60 s. 8 mines within 12 m, 600 damage each; they clear after 60 s.
  - Field tower: 6 CP, 90 s. A guard tower, or an ATGM tower from card rank 5, dropped for
    60 s. It is refused in the enemy camp whatever the mode.
  - SEAD: 7 CP, 90 s. 500 HE damage on the enemy air defence nearest the mark within 20 m,
    knocked out 8 s. Air defence is the anti-air class, or a fixed defence with an air-only
    weapon or missile.
  - The commander AI calls:
    - SEAD on known air defence when it flies aircraft or can soon;
    - the field tower on a point it holds with 2+ enemies within 45 m;
    - mines across the way of an enemy group 22+ m from its line;
    - the scan where something unseen is hitting it, or over an objective it is closing on
      with no enemy seen.
- **Airstrike from card rank 7.** The line is 40 % longer with 40 % more bombs (84 m, 11 bombs).
  The rank reaches the sim through `SetBoosts(strikeRank:)`.
- **Balance:**
  - VBIED ×0.5 on structures (a stream of 12 at an HQ with three towers left it untouched).
  - Siege tank 12 CP with ×2.4 on structures, about 155 DPS on them.
  - Tank buster 18 CP.
  - Gunship helicopter 14 CP (the CP option rather than −15 % against heavy armour: one number,
    same effect on value).
  - Stealth bomber 20 CP.
  - Railgun: measured 1.22 vehicles a shot (574 shots over 15 battles), below 2, so it drops to
    9 CP (rather than +25 % damage: a cheaper card suits its long-range, low-DPS role).
- **Supply.** The "24 × 1.05" was the army supply in CP: upkeep starts at 1.5× it, about 37 CP
  (5 mid-tier vehicles). It is now data per mode (`economy.armyCap`, default 40, so about 63 CP
  before upkeep, 8–10 mid-tier vehicles). Modes that set their own (Siege, Defend, campaign
  missions) keep theirs. `TeamEconomy.SupplyBonus` is the hook for the logistics module.
- **Campaign enemy scaling** is data (`economy.enemyScaling`), now 0.55 (was 0.8).
- **Recommended power** on the mission panel is the deck power expected by then. Rank 1 cards
  with no equipment give 100; the campaign climbs to rank 7 by the last mission. Hard missions
  add 6 % and the Heroic and Iron tiers add 8 % and 16 %. The deck's own power is the average
  over its vehicles of √(toughness × firepower).
- **Texts.** The Monolith Plate's line and the module descriptions no longer print raw keys or
  `{1}`. `LocalisationScanTests` checks:
  - both languages carry the same placeholders;
  - every card has a name and a guide entry;
  - all equipment, modules, traits and brands read as words at every rarity.
- **Firing spots are never shared.** A gun used to take another gun's booked firing spot when it was the
  only safe one left (a +1000 penalty, not a ban). Siege tanks (62 m reach) round a fortress have few such
  spots, so two often stood on one (TrafficTests: 66–331 shared bookings per ~1,000 checks on four maps).
  A booked spot is now out; two closer rings (65 % and 55 % of range) are tried when the outer three are all
  exposed or booked, and a gun that finds nothing holds back instead.
  - The price: m13 (the Ember Ridge fortress) is 1/5 (round 6: 2/5). With shared spots allowed it was 3/5,
    and a finer 7.5° bearing search dropped it to 0/5.
  - m13's weakness is the army not breaking into the fortress, and prompt 4 rebuilds that mission as a
    multi-stage grand campaign, so it is left there.
- **m12** has a 20-minute clock (it had none, and a stuck train could keep it open forever). A route boss
  that makes no headway for 12 s is sent on again to its waypoint (the train steered round tanks parked on
  its line and never found it back). Now 5/5.
- **Defend.** The attacking waves get no camp base of their own: an attacker camp is built only when the
  player attacks (Siege).

## 5. Multi-stage missions and big battles

- **Stages run in one battle** (`OperationMode`).
  - Each stage is a `MissionMode` of its own on the same world. Its JSON fields are laid over
    the mission's. What a stage fights (units, boss, hunted vehicles, convoy, waves, tips) is its
    own; the mission's units are placed once.
  - A stage's clocks (time limit, survive time, the wiped check, reinforcements) count from its
    start.
  - Finishing a stage pays its CP, fires its end events, keeps a checkpoint and leads on: to
    `next`, the next in the list, or a choice.
  - Losing a stage loses the mission.
  - Capture points keep their owners from stage to stage.
- **Events** at a stage's start, its end, or a number of seconds in:
  - reinforcements for a side (airlifted, as bought vehicles come);
  - the ally's reinforcements;
  - expansion of the play area;
  - betrayal;
  - a radio line;
  - CP.
  The commanders are set up for each stage's goal (hold leash, defend point, siege mix,
  demolition) in the same step the stage begins, so a replay does the same.
- **Choices.**
  - At a branching stage the battle goes on and a dialog offers the two objectives. Nobody
    choosing takes the first after 15 s.
  - The auto commander does not choose: the player's pick is the one thing the game waits for,
    and it is short.
- **Checkpoints by replay, not by snapshot.**
  - The world records the player's own commands with their step (`SimWorld.Journal`,
    `SubmitPlayer`). The game layer records the player's switches: stance, auto deploy, auto
    strike, focus point, branch picks.
  - A checkpoint keeps the step and a fingerprint of the state (`StateHash`: every vehicle's id,
    side, place and health, both sides' CP). It is taken at the start of the step after the
    stage ended, before that step's commands.
  - To go back, the battle is rebuilt from the same seed and the journal is fed in step for step
    behind the loading screen. The simulation is deterministic, so it lands on the same state.
  - Why not a snapshot: a deep copy of every system's state (paths, lanes, AI memories, pending
    strikes, projectiles) would be a second copy of the whole simulation to maintain and keep
    right as systems change. The replay needs nothing but determinism, which the tests already
    guard.
  - Tests:
    - a replay reaches the checkpoint with the same hash;
    - the restored battle and the uninterrupted one stay identical for six more seconds,
      through a choice and a betrayal.
  - The cost of a restore is replaying the battle so far: about 12,000 steps for ten minutes,
    a few seconds on a phone.
  - The journal is kept in memory only: a checkpoint lasts until the app closes. The result
    screen offers "Chơi lại từ điểm lưu" after a lost staged mission.
- **The allied commander.**
  - Its own HQ, towers and units at its site, on the player's side (team 0) but tagged `Ally`.
  - It is commanded by its own `TacticalAi` (`Allies = true`), and the player's commander
    leaves those units alone. It goes for the player's goal.
  - Its reinforcements land at its own site, so it never competes for the player's drop zone.
  - The ally's vehicles are not the player's army: no upkeep, army cap or unit limits, not
    selectable, not counted in the player's losses.
  - Betrayal (`Defect`) turns every ally vehicle and structure over to the enemy. Each drops its
    orders, path and targets, and its view is rebuilt in the new colours. Nothing of the
    player's changes sides.
  - It reuses the tactical AI rather than the Conquest commander, because the ally has no
    economy of its own (team 0's CP is the player's).
- **The play area.**
  - A rectangle the player's side (team 0) cannot move out of: its routes stop at the edge. The
    enemy is not held by it.
  - It is drawn on the ground as a dashed amber line, and an event opens it.
  - Growing a map past its old edge into the decor ring needs the map to be larger than its
    first play area. The new operation maps set their outer ground up that way (the map agents'
    part).
- **Growing the battlefield mid-battle.**
  - A big operation starts on part of its 300 m battlefield and opens the rest stage by stage
    (the `Expand` event). The camera keeps to the open area (with a 12 m margin, so the edge
    shows) and follows it as it opens.
  - The navigation grid and the traffic lanes already cover the whole battlefield, so an opened
    area needs no new navigation data.
  - The ring outside the 300 m square was not opened. It is scenery: mountains, forest and city
    blocks placed for their silhouette from the camera, with no roads, cover or objectives, and
    the map builder's reachability, traffic and base checks all work inside the square. Making
    it playable would mean a second, larger generator per map. If an operation ever needs more
    room, the way is a larger `_operation` version of its map from the builder, with the old
    square as its first play area.
- **The enemy's vehicle ceiling.**
  - The existing 32 vehicles a side stays for the player and the ordinary modes. The enemy in
    Siege, Defend, Endless and the big operations may field 48 (balance.json
    `economy.vehicleCap`; an operation's own `enemyCap` overrides it).
  - Big numbers come as swarms of cheap vehicles (the siege/defend waves).
- **Tick budget**
  - Setup: `TickBudgetTests`. A battle on Ashfield with both level-5 bases, the player's army of
    28, and N enemies in cheap swarms, with both commanders running. The fallen are replaced so
    the count holds. 60 s after a 10 s warm-up, three seeds a size; the median of the 99th
    percentiles is used.
  - Machine: a Ryzen 7 9700X, in the editor's Mono.
  - The low-end phone is taken as 6 times slower. That covers a Cortex-A55 / A73 class CPU at
    7–8 times slower in single-thread scores, less the IL2CPP build's gain over Mono.
  - The budget per 20 Hz step on that phone is 8 ms on average and 16 ms (half a 30 fps frame)
    at the 99th percentile.
  - Two fixes came first:
    - **Ground routes are found at most 6 a step** (`SimWorld.PathsPerStep`). A commander
      ordering a whole group, and their re-plans half a second later, made the worst steps three
      to five times the mean. The rest wait their turn, first come first served, and keep the
      route they had; a stop cancels a waiting route. At 48 enemies at most 18 routes wait, which
      is 3 steps (150 ms).
    - **The two sides' commanders think on different steps**: the enemy's half a decision
      interval later, the ally's a quarter.
  - Results, desktop ms (phone-scaled mean / p99):

    | enemies | vehicles alive | mean | p99 | phone mean | phone p99 |
    |---|---|---|---|---|---|
    | 24 | 74 | 0.56 | 2.67 | 3.4 | 16.0 |
    | 32 | 82 | 0.62 | 3.38 | 3.7 | 20.3 |
    | 40 | 90 | 0.71 | 2.69 | 4.3 | 16.1 |
    | **48** | 98 | 0.73 | 2.56 | 4.4 | **15.3** |
    | 56 | 106 | 0.89 | 3.90 | 5.4 | 23.4 |
    | 64 | 114 | 0.97 | 3.88 | 5.8 | 23.3 |
    | 80 | 130 | 1.31 | 6.23 | 7.8 | 37.4 |

  - The mean grows with the count and stays well inside the budget.
  - The 99th percentile is mostly a floor that does not follow the count: about 2.5–3.5 ms of
    worst steps, the path budget's and the commanders' steps plus the machine's own noise. Five
    agents were running Unity on it at the same time, so any one run is within about ±20 %.
  - The ceiling is 48, the highest count at or under the budget. It is to be measured again on
    a quiet machine and on a real low-end phone.
  - The step profiler (`SimWorld.Profile`, off in play) shows movement at about half of a
    step's time and combat at about a third.

## 6. Operations and the menu groups

- **Where it lives.**
  - The old Events tab is now **Tác chiến**. It holds this week's operation, the battles opened
    for replay, the weekly fortress, the boss rush and the daily challenges.
  - The skirmishes (Giữ cứ điểm, Vua đồi, Tử chiến, Công phá, Công thành, Phòng thủ) and the
    challenges (Sinh tồn, Vô tận) stay on the battle setup's mode list.
  - This is the navigation prompt 10 asks for: five items, with skirmishes and challenges
    chosen from the home screen's mode picker. So the four-group menu of prompt 6 was built
    straight into that shape rather than twice.
  - A test checks that every mode is still reachable.
- **What can be replayed.** The campaign's missions flagged `"operation": true` (each chapter's
  big operation) and `"replay": true` (the notable sieges, defences and duels with a general),
  once won in the campaign.
- **Tiers** (operations.json):

  | tier | enemy CP and income | player income | fire support | score |
  |---|---|---|---|---|
  | Normal | ×1 | ×1 | yes | ×1 |
  | Heroic | ×1.3 | ×1 | yes | ×1.3 |
  | Iron | ×1.3 | ×0.8 | no | ×1.6 |
  | Legend | ×1.6 | ×0.75 | no | ×2 |

  - Legend opens once the campaign's last big operation is won.
  - Heroic and Iron are the campaign's own tiers, unchanged.
  - A Legend win pays the Iron reward: its reward is the score and the record.
- **Score** of a won battle, out of about 12,000 before multipliers:
  - 5,000 for the win;
  - up to 3,000 for time under a 25-minute par;
  - up to 2,000 for losses, with 20 losses scoring 0 on this part;
  - up to 2,000 for the HQ's health (full marks where there is no HQ).
  - All of it is multiplied by the tier's multiplier plus each mutator's share.
  - A loss scores 0, so it never sets a record.
  - The best score and the fastest win are kept per battle and tier.
- **Mutators.** 18, all data, combinable, each adding 5–30 % to the score multiplier:
  - Stormy night and Night operation, which change only the weather;
  - All-air enemy;
  - No fire support;
  - Two bosses;
  - Enemy towers ×2 (double health, 50 % more fire);
  - No repairs;
  - Reinforced general;
  - Under 8 CP;
  - Armour only;
  - Grounded (no aircraft on either side);
  - Glass cannons;
  - Veteran enemy;
  - Against the clock;
  - Lean logistics;
  - Iron rain (bomber raids on both sides);
  - Swarm;
  - Empty base.

  A mutator that empties the player's deck (Under 8 CP, Armour only, Grounded) tops it up
  from the vehicles the player owns, so there is always something to field. The weather
  mutators are cosmetic by design: nothing is tied to weather (prompt 8's rule).
- **The weekly rotation.**
  - 26 weeks, each an operation (round the list) and a pair of mutators. The pairs are a fixed
    shuffle of all the allowed pairs (no excluded pair, no two weather mutators), taken so that
    every mutator comes up before any comes up a third time.
  - The week number (ISO week, UTC) picks the entry, so everyone gets the same week and the
    same data always gives the same table.
  - A test covers determinism, coverage, exclusions and no repeated pair. A 5-seed balance test
    plays every entry of the table; it runs once the campaign data flags its operations.
- **One weekly reward system.** The weekly fortress and the weekly operation share one ledger
  (`PlayerProfile.ClaimWeekly(week, key)`): each first win of the week pays once, 600 and 800
  coins, both read from operations.json. The fortress's old "claimed" flag is honoured, so
  nothing is paid twice after the update.
- **Result screen** of an Operations battle: the mission and the tier as its title, the score,
  the record (or "Kỷ lục mới!"), the mutators, and the week's reward when it paid.
- **A bug found on the way:** `MissionDef.Harder` (Heroic and Iron) rebuilt a mission's waves
  without their roster and spawn points, so a harder tier's waves never came. It keeps them now,
  with a test.

## 7. Sized slots (the supplementary prompt; replaces fortification points)

- **Why.** With both a slot count and a point budget, the slots were the scarce thing, so each
  was filled with the strongest tower and the light ones were never picked.
- **Slots by size.** Small takes light towers, medium light or medium, large any. HQ levels 1–5
  open 3/1/0, 4/2/0, 4/2/1, 5/3/1 and 6/3/2 (small/medium/large), with 1/1/2/2/3 utility slots.
  Every map camp has 6/3/2 tower slots and 3 utility slots, the most important of each size listed
  first, so a lower level opens the best ones. Outposts have 1 small and 1 medium slot.
- **Tower sizes.**
  - Small: guard tower, MG bunker, AA tower, EW tower, dragon's teeth, minefield.
  - Medium: gun tower, ATGM tower, rocket battery, C-RAM, hidden gun pit.
  - Large: artillery emplacement, Patriot, drone hangar, heavy fortress.
  - A tower's rank-7 branch keeps its size.
- **A loadout is three lists by slot size** (`BaseLoadout.Small/Medium/Large`), not tied to a map:
  the i-th small slot of any camp takes `Small[i]`. `Fitted` keeps only towers that fit a list's
  size and only as many as the level opens.
- **Rebuilding by size.** Small 2 CP / 25 s, medium 4 CP / 40 s, large 7 CP / 60 s (the 4 s
  flight stays).
- **Migration.** A saved point loadout (one list) goes into the level-5 lists largest first: large
  towers into large slots; medium ones into medium, then large; light ones into small, then medium,
  then large. What finds no slot is left out of the loadout: its rank and equipment live on the
  tower's card, so nothing is lost.
- **New profiles** get 6 small (guard, AA, MG ×2 each), 3 medium (gun, rockets, gun) and 2 large
  (artillery emplacement, Patriot).
- **The AI's base** fills every open slot by the style's weights among towers of the slot's own
  size, and among smaller ones only when the style has none of that size. So a base mixes all three
  sizes. Anti-air is always in it (the last small slot turns into one). Styles for the generals:
  - Varga: anti-tank towers;
  - Orlov: artillery emplacements;
  - Kessler: an even spread;
  - Dr Sen: drone hangars;
  - Quạ Đen: anti-air;
  - Aurel: the strongest of everything.

## 3. Towers: cards, branches

- **Tower cards** use the card ranks (1–10, +5 % a rank) and blueprints like vehicles. A loadout
  tower now carries its card's rank; other fixed defences (a fortress, a point's watchtower) still
  do not, unless the side boosts everything.
- **Branches are defs that inherit their tower** (`"inherits"`, `"branchOf"` in balance.json): the
  tower's data with the branch's changes on top, its model too. From rank 7 a tower card picks one
  of its two branches. The first pick is free and a change costs 800 coins. The loadout carries the
  pick into battle (`BaseLoadout.Branches`), and the tower is raised as its branch in its own slot.
  A branch shows as "tower · branch" (`branch.<id>` texts).
- **Roster** (size): guard tower, MG bunker, AA tower, EW tower, dragon's teeth, minefield (small);
  gun tower, ATGM tower, rocket battery, C-RAM, hidden gun pit (medium); artillery emplacement,
  Patriot, drone hangar, heavy fortress (large).
- **Merges.**
  - The flak tower is the AA tower's "Flak tower" branch (its quad 35 mm, no missiles; the siege
    fortresses use it).
  - The capture point's watchtower is a guard tower with double health while neutral.
  - The missile battery is the Patriot (90 m, not inside 20 m).
  - The coastal twin turret is the heavy fortress.
  - Old ids stay in `TowerCards` as not-cards so any leftover reference fails loudly in tests,
    not in play.
- **What each new tower does.**
  - EW tower: jams guided rounds and fire support aimed within 30 m (the EW jammer's code), no
    gun.
  - Dragon's teeth: blocks the way, fights nothing, is a last-choice target. Engineers do ×3 to
    it, and the commander has the line and its engineers knock it down when it stands between
    them and the objective with no other enemy round it.
  - Minefield: no target, no blocker. It lays its six mines at once within 5 m and lays the
    whole field again every 60 s.
  - C-RAM: an active protection of 35 m taking missiles, drones, all rockets and 30 % of shells,
    2 interceptors every 1.5 s, and a 20 mm gatling at aircraft.
  - Gun pit:
    - It stays down while no enemy on the ground is within 35 m. Down, it cannot fire, takes
      60 % less damage, and is seen only within 8 m, except by a scout, a counter-battery radar,
      a guard tower or a UAV scan.
    - It rises when an enemy comes that close.
    - The view lowers its `Lift` 1.6 m.
  - Drone hangar: 2 FPV drones every 20 s out to 70 m.
- **Light towers' own jobs.**
  - Guard tower: sees stealth and hidden units within its guns' reach, and gives friendly towers
    within 25 m 10 % more range (the best aura counts).
  - Every small tower with an anti-air weapon does +25 % to helicopters and drones (new `drone`
    flag on vehicles).
  - Light towers come back cheaper and sooner (see sized slots).
- **Cannon towers' weaknesses.** Gun tower and heavy fortress turrets turn at 28°/s and 20°/s,
  and reload in 6.0 s and 8.6 s (were 4.57 s and 7.14 s). Their coaxial guns no longer shoot
  aircraft (`mg_coax_ground`).
- **Branches (rank 7), each a trade, for a different fight:**
  - guard tower: Watchtower (sight, a stronger aura) / Gun nest (25 mm cannon, less sight);
  - MG bunker: Twin HMG / Flame bunker;
  - AA tower: Flak tower / SAM post;
  - EW tower: Drone jammer (45 m) / Radar spoofer (also finds guns within 80 m);
  - dragon's teeth: Hedgehogs (×2 health) / Wire and ditch (no block, slows by half);
  - minefield: Anti-tank field (4 heavier mines) / Scatter field (10 lighter);
  - gun tower: Long barrel / Autoloader;
  - ATGM tower: Top attack (×1.4 on heavy) / Multi-role (also aircraft, ×0.8 on heavy);
  - rocket battery: Cluster / Thermobaric;
  - C-RAM: Centurion (3 interceptors) / Hunter (45 m gatling, 1 interceptor);
  - gun pit: Ambush (first shot ×2) / Deep pit (−75 %, rises at 30 m);
  - artillery: Counter-battery / Extended range;
  - Patriot: PAC-3 (×1.4, 72 m) / Long-range radar (100 m);
  - drone hangar: Lancet / Swarm;
  - heavy fortress: Coastal battery (60 m) / Bastion (+55 % health).
  Weapons inherit the same way as vehicles (`"inherits"` in the weapons list), so a branch's
  weapon is its tower's with a change or two.
- **Utility modules** (utility slots):
  - repair bay: 1.5 %/s to vehicles within 35 m of the HQ, even under fire;
  - ammunition depot: reloads at home twice as fast;
  - airfield: aircraft within 14 m repair 3 %/s and rearm. The commander sends an aircraft back
    below 35 % health or out of ammunition and releases it at 90 % and rearmed;
  - logistics station: +8 supply through `TeamEconomy.SupplyBonus`;
  - radar station: everything in the base shows, and guns firing within 120 m show for 8 s.
  They reuse the map kit's hangar, ammunition dump, helipad, fuel depot and radar dome models.
- **Engineers** also repair friendly towers (at half their vehicle rate) and clear the enemy mines
  they see within their repair radius, one at a time.
- **Counter-buying against a base (supplement 5).** The commander reads the enemy towers it knows.
  Two or more cannon towers raise light fast vehicles, drones and artillery that outranges them.
  Two or more MG towers raise heavy armour. Two or more anti-air towers lower aircraft and raise
  artillery. Weighted by their share of the base. The player's auto-buy uses the same commander.
- **What a defence is worth to the AI.** It was the structure's health ÷ 250, so an HQ counted
  as a 90 CP army and no attack ever judged itself strong enough. It is now set by size: HQ 14,
  large 11, medium 7, small 4, and 1 for a module or anything with no gun. It is also weighed by
  what of the attacking group the defence can hit: only its ground or air share, and a slow
  cannon counts half against fast vehicles.
- **Drones on emplacements.** FPV drones, Lancets and the strike drone's missiles do ×1.5 on
  structures: precision munitions made for dug-in targets, and what the light swarm needs against
  a base of heavy guns.
- **Measured over 5 seeds, 8-minute battles.**
  - A fast light swarm with drones (49 CP) destroys every tower of a medium-and-large-only base
    and brings its HQ to 33–55 %.
  - Against the mixed base it destroys 13 % of the towers and leaves the HQ untouched.
- **Base table** (level 5, 5 seeds, score = HQ health left + share of the attackers destroyed,
  0–2). The mixed base scores 2.00 / 1.83 / 1.73 / 2.00 / 2.00 against the mixed, armour,
  light-and-drones, artillery and air armies. Against the mixed army it beats every one-tower
  base, the best of which is 1.94 (ATGM towers only). No one-tower base is best against all five.
  For example, ATGM towers only score 1.96 against armour but 1.07 against the swarm, and heavy
  fortresses only score 2.00 against armour but 1.19 against the swarm.
- **Pick rates.**
  - The first measurement searched outward from the mixed base. It was worthless, because the
    mixed base already scores the full 2.00 against a single army, so nothing could beat it.
  - Now each army is doubled and a level-5 base is filled from empty, one slot at a time (large,
    then medium, then small). Each slot takes whichever tower that fits scores best over 2 seeds.
    Towers within 0.02 of the best share the slot's credit. The attackers know where every
    structure is from the start.
  - Light towers are measured in the small slots, where they compete (an even share is 1 in 6):
    guard tower 32 %, AA tower 22 %, MG bunker 19 %, dragon's teeth 11 %, EW tower 10 %,
    minefield 7 %.
  - **The minefield was under 10 %, so it was buffed.** It now keeps 8 mines (was 6) and lays the
    field again every 45 s (was 60 s). Its branches moved with it so they stay trades: the
    anti-tank field has 5 heavy mines (was 4) every 45 s, and the scatter field 10 light mines
    every 35 s.
  - The EW tower sits at exactly 10 % and is left as it is. Its worth is against guided
    weapons and strikes, which only two of the five armies bring.
- **The default base and the reference base.**
  - With the attackers knowing the towers, the old reference mixed base scored only 1.44
    against the mixed army. It spent four of its eleven slots on specialists (EW tower, C-RAM,
    Patriot, ATGM tower). Several one-tower bases beat it: AA towers only 1.79, heavy fortresses
    only 1.79, rocket batteries only 1.77.
  - The player's default base, measured the same way, scored 1.19.
  - Five candidates were measured (5 seeds, the five armies):

    | candidate | mixed | armour | light+drones | artillery | air |
    |---|---|---|---|---|---|
    | default (artillery + Patriot; gun, rocket, gun) | 1.19 | 1.00 | 1.61 | 0.46 | 2.00 |
    | artillery + heavy fortress; gun, rocket, gun | 1.00 | 1.00 | 1.61 | 0.51 | 2.00 |
    | heavy fortress + Patriot; gun, rocket, ATGM | 1.63 | 1.78 | 1.61 | 0.50 | 2.00 |
    | **heavy fortress + artillery; gun, rocket, ATGM** | **1.86** | 1.37 | 1.61 | 0.30 | 2.00 |
    | greedy (2 heavy; rocket, AA, gun; 4 guard, 2 MG) | 1.71 | 1.91 | 1.78 | 0.44 | 2.00 |

  - **The player's default base is now: heavy fortress and artillery emplacement; gun tower,
    rocket battery and ATGM tower; two each of guard, AA and MG towers.** It is the only
    candidate that beats every one-tower base against the mixed army (1.86 against 1.79). The
    balance tests compare with this base (`BaseBalanceTests.Mixed` reads
    `PlayerProfile.Default*`).
  - Every base loses to the artillery army on its own (0.0–0.5). Five guns standing off beyond
    the towers' reach is how artillery beats static defences. The answer is the defending army
    and counter-battery fire, not the towers alone, so the towers were not changed for it.
  - The harness now tells the attackers where every structure is from the start (a scouted
    base), so the attack's tower sense (edge of reach, artillery first) plays out the same way
    every time.
- **Towers against vehicles of equal value** (small 5 CP, medium 8, large 12; 15 fights each).
  Most towers hold every fight. The C-RAM and the artillery emplacement hold none, and that is
  their design: the C-RAM has no gun for the ground, and the emplacement cannot fire inside its
  minimum range. They are specialists that protect a base under the cover of its other towers.
  Neither is buffed for a duel it is not built for.


## 3D. Tower equipment

- **Three more slots, not a second item type.** Tower pieces are ordinary `GearItem`s whose slot is
  one of three new `GearSlot` values after Special: `TowerWeapon`, `TowerStructure`,
  `TowerSystems` (`Gear.IsTower`). The save format, the bag, levels, merging (three of one slot and
  rarity), sub-stats, traits and the menus' line code all work unchanged, and the slot alone says
  which kind a piece is. A separate item class or a kind flag would have made slot 0 mean two things
  and every consumer check both. Vehicle loadouts keep their 7 slots a branch; the vehicle API
  refuses tower pieces and has no tower slots.
- **Their own catalogue beside the vehicle one** (`GearCatalog.TowerBases`, `TowerTraits`, a tower
  sub-stat table), so the 34 vehicle base types, 42 traits and every vehicle roll are untouched.
  13 base types: Weapon (damage; the ammunition hoist rate of fire) with range, damage against heavy
  armour, against aircraft, blast or shell speed as the implicit line; Structure (health; blast
  walls and slat screens less damage taken, as plating; the engineer bay repairs out of combat) with
  a resistance or a shorter repair delay; Systems (vision; traverse motors turret turn rate at 1.5×;
  ammunition handling magazine reload at 1.5×) with accuracy or magazine size. Main-stat values are
  the vehicle tables' (a base type can now name its main stat: `BaseTypeDef.Main`).
- **No brands on tower pieces.** Sets are a six-slot vehicle loadout's; with three slots a four-piece
  bonus could never be worn, and half the brand stats (speed, capture, summons) mean nothing to a tower.
- **Tower caps** (`GearCatalog.TowerStatCap`): the vehicle caps, except range +10 % (vehicles +12 %:
  a base's reach is what attackers and the AI's tower sense plan round) and regeneration 1 % a second
  (vehicles 2 %: siege fire must still be able to crack a tower). The card's rank multiplies on top.
- **The tower lines' numbers** (Epic / Legendary; the brief's numbers are the Legendary ones):
  - Fire Link +10 / +15 % damage while another friendly fixed defence hit the same target within 3 s.
    The HQ counts as a friendly tower (it is part of the base's fire net); the other tower needs no
    trait of its own.
  - Counter-Battery: artillery (a weapon with a minimum range) that hits the tower, directly or with
    its blast, is shown to the tower's side for 4 / 6 s. It reuses the radar's reveal status with no
    damage bonus; a called barrage has no gun to show.
  - Modular: once a battle a side's first tower of the type to fall is flown back in free; Epic waits
    half the cooldown, Legendary none. The 4 s flight stays. Towers going down with a lost outpost do
    not spend it.
  - Smoke Launchers: 10 m for 12 s / 14 m for 16 s, once a life (a re-dropped tower has its own).
  - Backup Generator: stuns and EMP knock-outs 50 % shorter at Epic, none at Legendary. Every stun
    setter (EMP skills and payload through `StatusSystem.Stun`, the EMP and SEAD strikes) asks
    `GearSystem.StunSeconds`; the SEAD strike's damage still lands.
  - Tower pools also carry five vehicle traits that work on a fixed defence, so an Epic piece has
    three to choose from: Executioner and Opening Salvo (Weapon), Aegis Barrier and Ablative Layer
    (Structure), Laser Designator (Systems), at their vehicle numbers.
- **Fit comes from the data** (`TowerFit`). A tower's weapons say what it has: a weapon that does
  damage (Armed), one for ground targets, one for aircraft, a magazine. The main weapon counts for
  everything it can target; a secondary only for what it is made for, so a gun tower's coaxial
  machine gun does not make it anti-air, while an AA tower's SAM box does. A stat line needs what it
  acts on (damage against aircraft needs a weapon for aircraft; health nothing; speed never fits a
  tower); a base type needs what its main and implicit lines need; a trait says its need in the
  catalogue. Sub-stats and traits are only rolled within the base type's need, so every line of a
  piece works on every tower the piece fits. An obstacle with no weapon takes Structure pieces only.
  `TowerFit.Matrix` lists, for every tower card and branch, the base types and traits that work for it.
- **Fit is checked against the def the tower fights as** (its rank-7 branch when one is chosen).
  Equipping an unfit piece is refused. A piece already on a tower whose branch changes stays on
  (a line with nothing to act on does nothing); `PlayerProfile.TowerFits` lets the screen flag it.
- **One loadout per tower type, shared** by every tower of that type in the camp and on outposts,
  re-dropped ones and its branch def included, and also by a field tower of that type dropped as a
  support (the same card). A piece is worn by one tower type at a time. The HQ and utility modules
  take none.
- **Crates:** a fifth of all equipment rolls are tower pieces, in every crate kind. The rarity is
  rolled first at the unchanged odds, so the pity counters and the rarity table stay as they were;
  the odds screen adds a line with the split and the chance of at least one tower piece. Tower pieces
  favour base types that work for a tower of the player's base (3 to 1), as vehicle pieces favour the
  deck's branches. The existing crate tests needed no change: the number of rolls, the pity and the
  rarity odds are the same.
- **Pictures:** tower pieces borrow their vehicle counterparts' slot pictures (weapon, armour or
  plating, optics) until they have their own `Resources/UI/Gear/<base id>.png`.

## 3F. Base loadout screen

- **Where it lives.** A third view of the Army tab (Deck | Equipment | Base, vi "Căn cứ"), next to the
  deck and equipment screens, because the base is the other loadout a battle takes. Device checks:
  `-mb-base` opens it; `-mb-base-map=<map>`, `-mb-base-gear` (Gear tab), `-mb-base-pick=<tower>` (a
  tower armed, its slots lit) and `-mb-base-confirm` (the branch-change question) go with it;
  `-mb-en` / `-mb-vi` force a language.
- **Layout.** Top: HQ level 1–5 (all open for now) with what the level opens, the map picker and Save.
  Left: the tower cards (size icon, rank, branch, how many are placed). Middle: the camp, under a
  legend that counts filled/open slots per size (so there is no fortification points bar), a "front"
  marker and a hint for what to do next. Right: the picked tower card with Branch and Gear tabs (and
  Take out when a filled slot is picked), then the outpost's two slots. The right column is a quarter of
  the width (320–420 px), so the camp gets what is left on 16:9 and gains on wider phones.
- **The camp diagram** is drawn from the map's conquest data for team 0, turned so the camp's front
  (the HQ's heading, towards the enemy) points up. All camps face north-east, so this matches the
  battle camera and the minimap. The grid, the map's roads and edge, and a tick for each tower's facing
  are drawn under the frames; frames are opaque so the roads never show through them.
- **Frames are not to scale.** A hardpoint is 5–9 m across, a few pixels on the diagram, so frames get a
  size per class (small 72, medium 84, large 96, HQ 86 px) that is still a finger target, 1 px borders for
  small and 2 px for the others, and the size icon in the corner. Where two frames would overlap they are
  pushed apart (a relaxation, then the smallest frame in the way moves to the nearest free spot), so the
  diagram keeps the camp's shape without frames on top of each other. `BaseScreenTests` checks every map
  at the 16:9 and the wide panel size.
- **Size icons.** The same corner brackets for all three sizes with a footprint square inside that grows
  (`slot_small`, `slot_medium`, `slot_large`), plus `hq` and `module` (utility), 24-unit stroke SVG.
- **Placing.** Drag a tower onto a slot, or tap a tower and then a slot, or tap a slot and then a tower.
  While a tower is carried only the open slots it fits light up (bone); the one under the finger turns
  green; the rest go dark. Dropping replaces what was there. A placed tower is dragged to another slot (a
  swap when both fit, otherwise its old slot is left empty) or back onto the tower list to take it out; a
  picked slot also shows Take out. In the list a mostly vertical pull scrolls and a sideways pull
  (towards the camp) starts a drag, so the list stays scrollable on touch.
- **Empty slots stay empty.** A loadout list may now hold an empty entry (`BaseLoadout.Empty`), kept by
  `Fitted` and skipped by `BaseSystem.Establish`, so emptying the second small slot does not move the
  third small tower into it. A tower that does not fit is still dropped as before (`HqLevelsOpenSizedSlots`).
- **The rules are in the Sim** (`BaseLayout`): which place each hardpoint reads (the i-th of its size,
  as the battle raises them; `BaseLayoutTests` compares it with `Establish` on every map), what fits,
  place, clear, move, and the layout that is saved.
- **Closed slots** (beyond the HQ level) are greyed with the level that opens them and keep their towers
  (shown dim): the saved layout is cut to the top level's slots, not the chosen level's, so lowering the
  HQ level and raising it again loses nothing. Closed slots are not drop targets.
- **Utility slots** are hatched "soon" slots while the catalog has no utility module. Once modules exist
  (the tower roster adds them) they are listed under Utility and only they light the utility slots up;
  the screen needs no change for that.
- **Outpost.** Its two places (small, then medium, the order of `BaseLoadout.Outpost`) are drop targets
  like the camp's but are never emptied: an outpost always flies in with two towers, so they are
  replaced, not cleared. An invalid saved outpost falls back to guard tower + gun turret.
- **Saving.** Save is the screen's one amber action; it writes `BaseLayout.ForSaving` (lists cut to the
  top level, what does not fit becomes a gap, trailing gaps dropped) through `PlayerProfile.BaseLoadout`.
  Leaving the view (another view, tab or page) saves too, so nothing is lost. The profile now remembers
  that the base was edited (`baseEdited`), so a camp cleared on purpose does not come back as the
  default loadout.
- **Branch choice** is on the picked tower card: its branches with name and info; locked below rank 7
  (with the rank to reach); the first pick is free and applies at once; a change asks first (the price
  in the question) and spends `PlayerProfile.BranchSwapCoins`. Only the AA turret has branches on this
  branch; the others say so.
- **Gear tab.** Weapon, Structure and Systems for the tower type. `PlayerProfile.TowerGear` is empty on
  this branch, so the slots show empty with a note. The one connection point is
  `BaseScreen.TowerGearIn(towerId, slot)`. The tower equipment API (feature/visual-overhaul) was not
  merged here: the merge was refused by the permission system, so the connection is left to the merge
  (see the hand-off note).
- **Style.** Field Command: graphite surfaces, hairlines, square corners. Amber only for Save and the
  chosen tab or level; lit slots in bone, the drop target in green. Every colour and size is in the
  stylesheet (`--base-*` and `--camp-*` properties; the diagram reads its colours from them); C# sets
  only positions. Tap targets are at least 72 px and text wraps instead of being cut with an ellipsis,
  as the coming Field Command 2.0 rules ask.
- **Tower icons.** `CardIcons.For` now has icons for the tower cards (a branch takes its tower's), which
  used to fall back to the tank. The HQ guide text speaks of sized hardpoints, not fortification points.

## 4M. New battlefields

Eight battlefields join the twelve (all in the skirmish rotation; the campaign engineer takes the
first four): Landing Beach, Hydro Dam, Capital, Silver Bug Launch Site (campaign), Salt Flats,
Border Bridge, Swamp, Coral Isles (skirmish). Each has Conquest (three points), Siege (the fortress
in the north-east) and Survival versions, both camps with 2 large, 3 medium and 6 small tower
slots and 3 utility slots, and an outpost (1 medium + 1 small) at every point.

- **Laid out on the battlefield itself.** The new builders work in world metres
  (`world_layout`), not on the 160 m design grid that is spread by 1.875 afterwards: causeways,
  bridges, rock walls and city blocks must sit exactly on the 4 m water grid and the 2 m
  navigation grid, and the spreading opens every seam. Nothing stands within 41 m of a camp (the
  design grid's 22 m, spread), as before. The twelve old battlefields come out byte-identical.
- **Builder fix.** Since the tower roster the keep's flak tower is `aa_turret.flak`, which has no
  size of its own in balance.json, and the builder stopped on every siege map. It plans it on the
  old 8 m Flakturm's ground, so the old siege maps stay as shipped.
- **Terrain runs into the edge.** On the new battlefields rock and water that straddle the
  outline stay (the old ones drop them), so a bluff or a river never leaves a gap along the edge
  to drive round. A bridge deck counts as terrain for the base planner: it is never pulled down
  to make room for a hardpoint.
- **Per-map kit.** `MAP_WAR` and `MAP_DENSIFY` change a theme's dressing for one map (counts,
  and a `where` test for the ground solid cover may take): the salt flats keep their sight lines
  (no tree clumps, hamlets or pylon line, 6 wrecks a half), the beach stays sand (trees and rock
  only above the bluffs), and nothing solid is dropped on a causeway, bridge or narrow shore of
  the water maps.
- **Water is river tiles.** The game draws the sea only beyond the north edge, so every sea,
  lake and swamp inside a battlefield is `river_water` (impassable) with `river_ford` shallows,
  in the theme's water colour. Beaches are a ring of shallows (walkable) round an island.
- **Landing Beach (temperate).** Temperate, not harbour: the harbour theme dresses the country
  round the map with factories; this is a Normandy-like coast. The sea lies along the south edge
  inside the map, behind the player's camp on the sand; hedgehogs (tank traps) in two staggered
  rows, wire, dunes (earth mounds), a sea wall broken every 34 m; the bluffs are two rows of cliff
  pieces set edge to edge (the obstacle clearance seals the seams), 20 m deep, with four exits
  20-28 m wide. Asymmetric by design: the enemy holds the plateau, the bluff tops and the village.
  Points: `beach` (the beach strongpoint, east), `draw` (the head of the main exit, centre),
  `village` (the church square, west).
- **Hydro Dam (temperate).** Temperate, not snow: the snow theme draws water as pale ice, which
  read as walkable. The river runs north-south so the dam crest lies square to the grid; the crest
  is 12 m (four walkable cells) and the only other crossings are the road bridge (the centre) and
  a 32 m ford. Points: `power_station`, `bridge`, `ford`.
- **Capital (urban).** Different from Metro City: the river splits round an island that carries
  the government quarter (the palace and the domed parliament face each other across the palace
  square, ministries along the tree-lined Mall), and each arm has one bridge, so the two bridges
  are the only ways across and every crossing goes over the island. The bridges are 25 m decks to
  carry the traffic. Dense blocks (buildings a metre apart, one solid mass) between avenues. The
  objectives are plazas, not roads, so their outposts fit. The outline takes the two flanks
  (forced) to carve a twentieth of the square. Points: `gardens`, `palace_square`, `station`.
- **Silver Bug Launch Site (desert).** Composed from the kit: the rocket is a refinery tower (a
  tall stack), the fixed and mobile service towers gantry cranes, the flame pit a tank ditch, the
  radar dishes radar stations and a dome, the perimeter fence razor wire gated at every road.
  The rocket stands on the north edge of the pad so the centre point stays open ground. Rail
  lines bring the stages in from the assembly building (north-west) and the propellant from the
  farm (south-east). Points: `assembly_building`, `launch_pad`, `propellant_farm`.
- **Salt Flats (desert).** The kit has no white ground, so the flats are the desert's sand. Nine
  rock clusters a half as stepping stones, 40-60 m apart along every approach, the direct run
  between the camps left open. Points: `salt_works`, `survey_beacon`, `brine_pumps`.
- **Border Bridge (temperate).** The river is 50 m wide and narrows to 24 m at the Great Bridge
  (a 42 m deck): on a wide river the bridge point had no bank within reach for its outpost.
  The detours are a 26 m ford in the far west and an old one-deck bridge in the far east. The
  centre point has a 14 m radius. Points: `border_village`, `great_bridge`, `customs_depot`.
- **Swamp (jungle).** Brown jungle water. Causeways and bridges run square to the 4 m grid:
  diagonal ones came out one cell wide in places. Causeways and the two main bridges to the centre
  are 12 m (four cells); the footbridges are 8 m (two cells), the narrow passes. The camps stand
  on 124 m squares of dry ground: smaller ones had no room for the third utility slot. Spur
  causeways lead round to the fortress gates for Siege.
- **Coral Isles (desert).** Desert, not harbour: sand, palms and the desert's turquoise water read
  as a lagoon; the harbour's grey-green and industrial scenery did not. The lighthouse is a silo
  (the white tower) with a floodlight mast and the keeper's cottage, on the centre island's north
  headland (off the point's centre), an old fort on the south one. Points: `west_isle`,
  `lighthouse`, `east_isle`.
- **Names and icons.** English and Vietnamese names as given, one-line subtitles; icons anchor,
  bolt, crown, missile, dune, flag, fog, sun. Weather favours the setting (fog and overcast for the
  landing, night for the launch site, clear for the salt flats, fog and rain in the swamp).
- **Tests.** `MapRouteTests` routes, on all twenty battlefields and all three versions, from
  every drop zone to every capture point and the other drop zone, and in Siege to the command HQ,
  with the movement system's pathfinder; the map lists of the base, traffic and battle tests take
  the eight new ids.

## 5L. Vehicle LOD and impostors

Big battles put 100 and more vehicles in view (48 enemies in Siege, Defend and the large operations,
the player's army, the bases' towers). Measured before this change, a fieldable model averaged 8,800
triangles and 22 draws (one per material of each moving part), so a hundred of them meant about
880,000 triangles and 2,200 draws in the main pass alone, and as many again in the shadow pass. On GLES
(no SRP Batcher, see `Atmosphere`) and with the hit-flash property block breaking instancing, each of
those draws is a full state change on the CPU: draws, not triangles, are the cost to cut.

- **Three levels, chosen by size on screen.** 0: the full merged model. 1: a simplified model with one
  mesh and one draw per moving part. 2: an impostor card. The camera is orthographic, so a vehicle's size
  on screen does not depend on how far it is from the middle of the view: only the zoom, the resolution
  (render scale included) and the vehicle's largest extent (length, span or height) count
  (`VehicleLod.PixelsPerMetreOf`). Level 1 below 128 px across, impostors below 24 px, each with a 12%
  band either side (`VehicleLod.Choose`): a vehicle drops a level at 88% of a threshold and comes back
  at 112%, so a pinch that stops near a threshold never flickers. At 1080 px and the widest game zoom
  (42) a tank is about 96 px (level 1), a jeep 56 px; impostors appear on small screens, low render
  scales, `-mb-overview` and any wider zoom a later change allows.
- **Level 1 is built at load, not in Blender.** Unity 6's mesh LOD generator (`MeshLodUtility`) is
  editor-only, and the game merges each model's parts at run time (`ModelLibrary.MergeRigidParts`), so
  the far level is made from the merged template when a battle prewarms its fieldable models: every
  sub-mesh of a part welded, simplified by `MeshSimplifier` (quadric edge collapse after Garland and
  Heckbert with meshoptimizer's vertex kinds: open edges and lines between surfaces only slide along
  themselves, a link-condition and flip check, pieces smaller than twice the error dropped) to half a
  pixel of error at the size level 1 takes over, then normals rebuilt with a 50 degree crease (hard where
  collapsed bevels leave sharp edges). A second GLB per model from Blender was rejected: it doubles the
  art in the APK, conflicts with every art branch, and Blender's decimator has no error bound (a bevelled
  box at ratio 0.3 collapses). A vertex-clustering decimator was rejected: at the same error it removes
  far less and blurs hard edges.
- **One material per army at level 1.** Each vertex names its kit surface by a palette column in its UV
  (`MaterialLibrary.Palette`: base colour and metallic, emission and roughness of every kit material,
  linear, from the live materials); the army's paint and camouflage and its glow come from
  `MaterialLibrary.LodSurface(team)`, kept in step with the skin (`ApplySkin`). The Lit shader has a
  `_VertexSurface` branch (a uniform branch; the full models do not pay for it). So a tank that takes 21
  draws up close takes 4 far away and keeps its exact colours; metallic and glowing parts keep theirs.
- **Recoil folds into the mount at level 1; everything else still moves.** Turrets, elevating barrels,
  weapon mounts, rotors, propellers and loose parts (erector, searchlight, lift, bombs) keep their own
  part and pivot, so turrets aim and rotors spin at level 1; only the barrel kick is folded into its
  mount (too small to see at that size). The view's animation (turret, mounts, elevation, spin, flight)
  runs at every level, because muzzle flashes, tracers and missiles leave from those transforms: effects
  are placed right at every level.
- **Impostors are relit, not pre-lit.** A pre-lit card would miss night, storms (the lightning flash
  lifts the sun for a moment), weather shifts mid-battle and blast lights. Each page (a model for one
  army: the player, the enemy, one shared by everyone else) holds 16 headings of 32 px, drawn from the
  simplified model with the game camera's rotation into two sheets: albedo and coverage (sRGB), and
  view-space normal, metallic and glow (linear), premultiplied by coverage so the mip chain keeps its
  edges. The card shader blends the two headings either side of the vehicle's own, and lights them with
  the sun and its shadow, every visible light, ambient and reflections. Its own light loop: URP's
  `UniversalFragmentPBR` reads the sun's strength from per-renderer data that instanced draws do not
  get, and the first cards came out black. Cards stand in the camera's plane, pushed towards the camera
  by the vehicle's size so the ground never cuts into them (an orthographic view does not move them on
  screen); alpha to coverage smooths their outline with MSAA. Sheets are 512 px (16 pages, 2 MB for both
  textures and mips), added as needed; every card on a sheet is one instanced draw.
- **Turret and pose are dropped on cards**, as the brief allows: a card shows the hull's heading with the
  turret at rest, aircraft level at their altitude. Rotors and propellers are left out of the bake (a
  still rotor reads as a cross); the view's rotor blur disc stays. Cards cast no shadow: a soft disc
  (`ViewRegistry.DrawBlobs`) stands under each card, as with shadows off.
- **Pages are baked when a vehicle is made**, two a frame, and a vehicle stays on meshes until its page
  is drawn: no hitch when the view zooms out over a new army. Wrecks never become cards (a turret can be
  thrown off, the hulk sinks away); they keep following the zoom between levels 0 and 1.
- **Nothing a player relies on changes with the level**: selection ring, health bar, ammunition and
  repair marks, the aircraft ground ring, nav lights, shields and team colours are the view's own objects
  and stay as they are; the hit flash and scorching tint all levels (`ImpostorTint` for cards).
- **Debug flags.** `-mb-no-lod` (nothing built, full models only, for comparison), `-mb-lod=0|1|2`
  (force a level where a vehicle has it), `-mb-lod-colours` (level 1 cyan, cards magenta), `-mb-crowd`
  (`-mb-crowd=N`: two armies of fifty, N a side, topped up in view), `-mb-zoom=N` (the starting zoom).
  `-mb-perf` now reports how many vehicles are at each level and how many cards went in how many draws.
- **Checking by eye.** `MachineBrigade.Editor.LodShots.Compare` (batch mode with graphics, D3D11) renders
  the full, simplified and impostor levels side by side at the sizes where each takes over, the atlas
  sheets and a hundred-vehicle crowd at each level.
- **Measured.**
  - Load-time census of all 94 models: a fieldable model averages 8,817 triangles and 22.2 draws
    at level 0. Its level 1 averages 2,719 triangles (31 %) and 3.6 draws; the worst keeps 73 % of
    its triangles. Building every level 1 takes 1.1 s in all, spread over the battle's prewarm.
  - A crowd of 100 vehicles in view (`-mb-crowd`, editor, D3D11):

    | level | triangles | renderers | CPU per frame |
    |---|---|---|---|
    | 0 | 740,590 | 545 | 2.24 ms |
    | 1 | 254,690 | 380 | 0.81 ms |
    | 2 | 200 | 0 | 0.75 ms |

    These are relative numbers from a desktop editor, not phone timings. A phone has to confirm
    them.
## 4. Campaign

- **The story is data written by a script.** `Tools/campaign/build_campaign.py` builds `Resources/Data/campaign.json` and
  `Scripts/Game/Hud/CampaignText.cs` from `story.py` (people, generals, chapters, boss files, timeline, the brigade's usual
  radio lines, the screens' labels) and `act1.py`–`act3.py` (the missions and their texts). It also turns reversed missions
  round, sets every mission's pay and checks the rules below, failing the build when one breaks. Why: 108 missions and 900
  texts in two languages are easier to keep consistent in one place than in a hand-edited JSON and a 1,500-line table.
  The texts live in their own table (`CampaignText`, read after `Strings` and `GuideText`), so `Strings.cs` hardly changes
  (fewer merge conflicts).
- **Setting names.** The coast is Lam Hải; its capital, Lam Thành (the map stays "Thủ Đô"). Hegemon's rule is the
  "Protectorate" (Chính quyền Bảo hộ), from the Night of Steel (Đêm Thép) two years ago. Lữ đoàn Cơ giới 7's nickname in
  Vietnamese is "Lữ Đoàn Máy".
- **Ids.** Main missions are `c<chapter>m<nn>` (c3m05), side missions `c<chapter>s<n>`; the menu shows 3-5 and 3-S1.
  Missions are listed chapter by chapter, the ten main ones, then the two side ones.
- **Order and gating.** A main mission opens when the main mission before it is won; the first of a chapter when the last
  chapter's operation is won. A side mission opens when the main mission it follows (`after`) is won, and never holds
  anything back. A won mission is always open. In this build a mission whose battlefield file is missing does not hold the
  missions after it back (the four story maps are on the maps branch), and its Start button says the battlefield is coming.
- **The chapters** (each: the fifth mission a boss, the tenth a multi-stage operation with a choice of two):

| Ch | Title (vi) | Maps | General | Mid-chapter boss | Operation | Cards unlocked | HQ level / module |
|---|---|---|---|---|---|---|---|
| 1 | Bờ biển lửa | Bãi Đổ Bộ, Lũng Xanh, Ashfield | (garrison) | Landing hovercraft | Ashfield fortress, Bastion (55 % health) | rocket technical, mortar, repair drop, rocket battery, tank destroyer, ZU-23, minefield | HQ 1 / repair bay |
| 2 | Vàng đen | Dunebreak, Hẻm Đá Đỏ | Varga | Behemoth | Refinery raid, Inferno | MLRS, SAM, flame tank, airstrike, heavy tank, ATGM tower, engineer | ammunition depot |
| 3 | Mùa đông dài | Frostpeak, Đèo Bão Tuyết | Orlov | Iron Bird | Frostpeak line, Ice Fortress | gun-SAM, attack helicopter, UAV scan, dragon's teeth, ATGM carrier, artillery emplacement, Patriot | HQ 2 / radar station |
| 4 | Cảng thép | Ironport, Bãi Sắt Gỉ | Kessler | Steel train | Take the port, Tempest | command vehicle, attack jet, wheeled gun, counter-battery radar, thermobaric, field tower, gun pit | logistics station |
| 5 | Lửa rừng | Sườn Dung Nham, Đèo Rừng Rậm | Sen | The Hive | Hive mothership; Sen defects | strike drone, FPV carrier, jammer, twin tank, long SAM, fighter, drone hangar | HQ 3 / airfield |
| 6 | Tổng phản công | Đập Thủy Điện, Whiteout and Ashfield reversed | Varga | Spectre | Defend the dam, Frost Monster, Hùng's relief | C-RAM, EW tower, scout heli, recon UAV, Lancet, smoke carrier | Epic tower piece |
| 7 | Chiến tranh trên không | Skyhold, Frostpeak reversed | Quạ Đen | Silver Bug (flees at 50 %) | Storm Skyhold, command airship | SEAD, heavy MLRS, gunship, Iron Beam, remote mines | HQ 4 / Epic tower piece |
| 8 | Thủ đô | Thành Phố Metro, Thủ Đô | Aurel | Doomsday Train | Liberate the capital; Hùng betrays | VBIED, turtle tank, BMPT, Shahed truck, sapper | Epic tower piece |
| 9 | Bãi phóng | Bãi Phóng Silver Bug, Dunebreak reversed | each in turn, Aurel | Silver Bug II | Silver Sky Falls: Tổng Tư Lệnh, Silver Bug complete | railgun, cruise missile, heavy fortress, tank buster, minelayer | HQ 5 / Legendary tower piece |

- **Cards.** The 56 campaign cards (38 vehicles, 7 supports, 11 towers) are each unlocked once, 5–7 a chapter, in an order
  where every flying boss (Iron Bird, the Hive mothership, Spectre, Silver Bug, the command airship) and every shoot-down
  mission comes after the player has at least two ground cards that shoot at aircraft in a sensible deck
  (`CampaignTests.NoMissionNeedsALockedCard`). New starter towers: guard tower, MG bunker, AA tower, gun tower (what HQ
  level 1's three small slots and one medium slot need). A tower or module not unlocked yet leaves its slot empty in
  battle, and the base screen keeps HQ levels above what the campaign opened shut (every level stays open while
  `TestUnlockAll` is on).
- **Only five utility modules exist**, so chapters 1–5 open one each and chapters 6–9 pay a tower piece on their
  operation instead (Epic, and Legendary for the last), the base reward nearest a module.
- **HQ levels** come with the first outpost (c1m04, level 1) and the bosses of chapters 3, 5, 7 and the Varga duel of
  chapter 9 (levels 2–5). `Campaign.HqLevelCap` is what the save has opened; the balance tests play every mission with
  the level and the towers a player has by then (`CampaignTests.RealisticBase`).
- **Generals are AI configurations** (`generals` in campaign.json): a signature deck used when a mission names none, the
  fire support they call (`enemySupports` overrides it) and their base style (section 7). Their taunts and defeat lines
  are radio texts; their portraits are in `Resources/UI/Portraits`.
- **The old campaign.** The 23 old missions live on inside the new one (`legacy`): m00→c1m03, m01→c1m08, m02→c1m09,
  m03→c3m05 (Iron Bird: the boss decides over the map), m04→c2m01, m05→c2m10, m06→c2m05, m07→c3m02, m08→c3m03,
  m09→c3m10, m10→c4m02, m11→c4m03, m12→c4m05, m13→c5m06, m14→c5m01, m15→c5m10, m16→c8m05, m17→c2m06, m18→c3m08,
  m19→c4m04, m20→c7m07, m21→c9m05, m22→c1m07. Their briefings were rewritten for the story.
- **Save migration** (`PlayerProfile.MigrateCampaign`, once, `campaignVersion` 2): each old mission's stars and best tier
  move to the mission it became (the better of the two if both were played); cards won stay unlocked (they are kept by
  id). A won mission is always open, so the new missions around the old ones can be played in any order the gating
  allows. Old ids still resolve (`Campaign.Get("m09")`, `-mb-m09`).
- **New mission types** (`MissionGoal`): *Outpost* (take a point, set it up, keep it standing N seconds), *Relieve* (destroy
  the marked besiegers before the allied HQ falls), *Evacuate* (evacuees leave a site one every few seconds and run for the
  exit without waiting for an escort; the army holds the site, then covers the road), *Duel* (level the general's HQ, a
  Target base). Also: a boss's health can be scaled (a weak Bastion, the Frost Monster at 3×), a boss can flee at a share of
  its health (the fight is won; it becomes untouchable and leaves the map in 8 s), a Defend base loses the mission when its
  HQ falls whatever the goal, and a convoy vehicle can be tougher than its def (Mai's plated Behemoth). A hunt with no
  targets of its own goes after marked vehicles (the traitor's base).
- **Bosses still being modelled** (landing hovercraft, rail supergun, earth borer, command airship, Tổng Tư Lệnh) are named
  in the data with a stand-in (`fallback`, `fallbackHealth`): the mobile fortress at half health, the armoured train ×1.8,
  the Behemoth ×1.4, Spectre ×0.9, the Bastion. Once their defs exist in balance.json the real boss is fielded with no data
  change. The Frost Monster is the Behemoth at 3× health and Silver Bug's complete form Silver Bug at 2.2×, each with its own
  name (`boss.<name>`), so the lead's multi-phase health bars can be added on those defs or on new ones.
- **Operations.** 4–7 stages each (a branch counts once). Every operation has one choice of two with different
  consequences: blow a depot (the enemy's income ×0.7 for the rest of the battle, `Income` event) or take a radio/radar
  point (a free airstrike every 50–55 s for the rest of the battle, a repeating `Strike` event). The auto commander clears a
  capture or demolition stage in one to three minutes, so each operation has 8–12 minutes of timed stages (the enemy's
  counterattack, holding a crest or a quay) to land in its 15–25 minute window (the last one 15–30). Holds inside an
  operation are defended points (Survive with a point): one point lost for 25 s must not end a 20-minute battle. The two
  siege operations (chapters 3 and 7) end by holding the gate against the counterattack instead of levelling the keep's HQ,
  which the auto commander never reached in 34 minutes; chapter 1's siege keeps its HQ stage (won in 15–18 min).
  `"operation": true` marks the nine for the Operations mode; `"replay": true` the duels and the base defences.
- **Chapter 8's betrayal.** General Hùng's army fights beside the player with its own HQ and towers (`ally.hq`,
  `ally.structures`); when the palace is taken, a `Betrayal` event turns them: his units and towers join the enemy, his HQ
  and towers are marked, the player holds for five minutes, then the last stage is a hunt of the traitor's base.
- **Map reuse.** Two missions on one battlefield differ in at least two of: direction (reversed), base (variant and base
  roles), weather, play area and goal. The builder and `CampaignTests.EveryReturnToAMapChangesItsSetUp` check every pair.
- **Reversed missions** play on `MapDefinition.Reversed()`: the sides swap camps, hardpoints and the units placed there (a
  fortress's towers become the player's: c6m01 defends the Ashfield fortress taken in chapter 1). They are written in the
  player's frame (the player's camp south-west) and turned round by the builder.
- **Duels.** The auto commander never reached a general's HQ behind a level 4–5 base (0–11 % in 20 minutes). A trace
  showed why: the army swung back and forth at mid-map for 29 minutes, because the general's field army and its
  reinforcements matched it, so it never got to the base. What changed:
  - the AI's demolition target may now be a fixed defence, so the HQ is shelled from safety like a building;
  - the general fights on the Defend stance behind his full base: level 2 or 3 in chapters 2–6, level 3 in act III
    (not 4–5: the auto commander cannot crack those in 30 minutes);
  - the general's strength is his base, not his field army: his income is ×0.6 and he gets one wave of reinforcements;
  - the player starts with a heavy battery (two artillery pieces and an MLRS) in the camp;
  - the HQ has 0.3 of its health, with 30 minutes on the clock.
  The two early duels (Varga in c2m09, Sen in c5m09) already won 5/5 without these changes and keep the gentler set-up:
  HQ 0.4, 25 minutes, full income, three reinforcements. The siege unit mix (artillery first) was tried on the duels and
  reverted: c5m09 dropped from 5/5 to 2/5, because the general's army has to be beaten in the field first.
- **Relief of the capital** (c8m03): the besiegers have 2.2× health, not the 3× of the other reliefs; at 3× the allied HQ
  fell in one seed of five with one tank of the ring left (4/5; 5/5 at 2.2×).
- **Outposts.** The commander held the lake in c3m04 for five minutes and never set the outpost up: it spent every CP as it
  came in. Holding a marked point with 16 CP of army on the field, it now saves up for the set-up.
- **Rewards.** Every main mission pays coins, XP, blueprints for the main deck (spread over the battle deck and the base's
  first six tower types, the cards furthest behind first; a replay pays a third), the story fragment of the Dossier; side
  missions pay rare (universal) blueprints or a tower piece (Rare, then Epic from chapter 4, Legendary at the end), once.
  "coin" is "xu" in every new Vietnamese text.
- **Economy curve.** A campaign-only player (every mission won once with two stars, the silver crate of each first clear,
  the rank-up coin bonuses, spending at once on the lowest card of a 14-card main deck) should have the deck at about rank 7
  as act III begins. The builder searches the two scales (coins, blueprints) that land there and a little over 8 at the end:
  coins 100 × (1 + index/30) (bosses ×1.5, operations ×2.4, side missions ×1.15 of the main before them), blueprints
  3 × (1 + index/22) with the same factors (side missions ×0.6).

  | Chapter | Missions | Coins | Coins so far | Deck blueprints | Blueprints so far | Deck rank at the end | Player level |
  |---|---|---|---|---|---|---|---|
  | 1 | 12 | 2,105 | 2,105 | 55 | 55 | 4.0 | 5 |
  | 2 | 12 | 2,685 | 4,790 | 74 | 129 | 5.0 | 7 |
  | 3 | 12 | 3,365 | 8,155 | 100 | 229 | 5.3 | 9 |
  | 4 | 12 | 3,955 | 12,110 | 120 | 349 | 6.1 | 11 |
  | 5 | 12 | 4,425 | 16,535 | 137 | 486 | 6.3 | 13 |
  | 6 | 12 | 5,155 | 21,690 | 163 | 649 | 7.0 | 14 |
  | 7 | 12 | 5,585 | 27,275 | 177 | 826 | 7.1 | 16 |
  | 8 | 12 | 6,175 | 33,450 | 199 | 1,025 | 7.6 | 18 |
  | 9 | 12 | 6,750 | 40,200 | 218 | 1,243 | 8.1 | 19 |

  Chart: `Docs/art/campaign_economy.png` (the builder prints the same curve per mission). Not counted: daily missions,
  win crates and ad crates, so a real player is a little ahead of the curve.
- **Radio chatter** (`RadioDirector`, presentation only): the mission's lines by trigger (start, a time, a point taken
  or lost, the boss arriving or at half, the HQ at half, a stage, enemy reinforcements, win, lose), each once; a moment with
  no line of its own gets one of the brigade's usual lines, at most one every 35 s (the one-off moments once). Stage radio
  events and the Sim's messages (betrayal, a boss fleeing, allied strikes) are spoken by whoever the key names. The panel is
  a portrait, a name and one line under the top bar; a tap skips it; at most three wait.
- **Story camera.** When a boss arrives, enemy reinforcements land or a general speaks for the first time, the camera
  glides there for 3.5 s (not when the player touched the view in the last 2 s; a touch hands it back). The slow-motion
  moment on a boss's death is unchanged.
- **Mobile storytelling.** No cutscenes: the Start button shows the chapter's opening card the first time a chapter is
  played (act, title, four sentences, its maps, the general), then the mission's briefing card (the speaker's portrait,
  the briefing, goal, weather and map chips, the general and one of their taunts), then deploys. The epilogue shows once
  after the last operation. The Dossier (campaign page, "Hồ sơ") has people (bios once met), boss files (once beaten),
  the timeline (a line per chapter finished) and the story files (a fragment per won mission). Device checks: `-mb-dossier`
  (`-mb-dossier-tab=bosses`, `-mb-dossier-all`), `-mb-chapter=3`, `-mb-brief=c3m05`, a mission `-mb-c3m05`.
- **Portraits** are drawn by `Tools/campaign/portraits.py` (PIL, 4× supersampled): flat busts on a teal ground for the
  Alliance, dark red for Hegemon, each with its own headgear, insignia and one feature to know them by at 48 px.
- **Style.** The new screens use the Field Command tokens (`--surface-*`, `--line-*`, `--text-*`, `--accent`), Barlow
  Condensed for caps and titles, Be Vietnam Pro for text; touch targets 72 px or more; text wraps, never an ellipsis. All in
  one block at the end of Hud.uss for the coming token theme.

- **Balance** (`CampaignTests.WinRateOverFiveSeeds`, run with `MB_BALANCE=1`; five seeds, the auto commander, the deck and
  base a player has by then, cards at rank 1 so the arsenal edge the enemy matches is zero, Normal):
  87 of 87 measured missions win all five seeds (the whole run: 16 minutes). Not measured, because their battlefield is
  on the maps branch (Assert.Ignore until it is merged): c1m01, c1m02, c1m05, c1s2, c6m04, c6m06, c6m08, c6m10, c6s2,
  c8m02, c8m06, c8m08, c8m09, c8m10, c8s2, c9m02, c9m04, c9m06, c9m08, c9m10, c9s1. The test prints one `SEEDS <id>:`
  line per mission (each seed's result, minutes, goal progress, peak army). Half the missions average under 3.5
  minutes. The operations:

  | Operation | Wins | Durations (min) | Window |
  |---|---|---|---|
  | c1m10 | 5/5 | 20.0, 17.3, 19.4, 18.9, 19.7 | 15–25 |
  | c2m10 | 5/5 | 16.9, 18.2, 19.0, 17.0, 16.4 | 15–25 |
  | c3m10 | 5/5 | 24.2, 19.7, 19.2, 18.5, 21.6 | 15–25 |
  | c4m10 | 5/5 | 15.9, 19.0, 18.1, 17.9, 16.1 | 15–25 |
  | c5m10 | 5/5 | 17.0, 17.1, 20.1, 19.7, 16.9 | 15–25 |
  | c7m10 | 5/5 | 18.2, 17.6, 18.6, 18.7, 17.1 | 15–25 |

- **How the missions were tuned** (never by cutting fire or explosions):
  - One seed per mission first (`MissionPlaysToAnEnd`), then five (`WinRateOverFiveSeeds`), six rounds.
  - Operations were far too short at first (5–7 minutes: the auto commander clears a capture or demolition stage in one to
    three). Timed stages brought them to 15–25 minutes.
  - Protect targets fell early: 14–22× building health (the old m22 had 12×).
  - Mid-bosses died in 1–2 minutes: Iron Bird 1.6×, Spectre 3.5×, Silver Bug 4.4× (it flees at half), Silver Bug II 2.4×,
    the steel train 1.6×.
  - Relief rings broke in 30 s: besiegers at 3×.
  - Hunts whose last target never came near the army: inner routes, 1.5–1.8× (was 2.5×), more time.
  - The jungle convoy's route crossed the river: it now keeps to the pass road.
  - Duels (see above) went from 0–11 % of the HQ in 20 minutes to 5/5.
- **Seen in the runs, left as they are:**
  - Many ordinary missions end in 1–4 minutes under the auto commander. The brief sets no length for them, and a player
    who steers the army takes longer.
  - The arsenal edge is zero in these runs (rank 1 cards). A real player's ranks make the campaign easier, because the
    enemy matches only 55 % of the edge.
## 5S. Siege and Defend upgrades

- **The outline stays as it was carved.** The battlefield's outline is still carved round the first
  fortress plan (the old `fortify`, now used only for that), so the Conquest and Survival versions, the
  camps and every campaign mission are byte for byte what they were. The new fortress
  (`Tools/maps/fortress.py`) is built into the finished siege battlefield, inside that outline. Why: a
  bigger fortress in the carve would have moved every map's edge (the carve is point-symmetric) and
  with it the campaign's balance.
- **"40-50 % of the map" is the ground behind the outer line.** The outer line runs square to the
  camp-to-camp diagonal (`x + z = c`), `c` found per map so that 45 % of the play area inside the
  outline lies behind it (45.0-45.5 % on the twelve maps). The map file stores it as `fortress.area`
  (a polygon) and `fortress.outerLine`. The walls and the keep stay square round the HQ (walls can only
  be axis-aligned 8 m pieces), so the ground between the outer line and the walls is the fortress's
  outer works: the battlefield as it was, with the strongpoints, obstacle belts and the line in.
- **Rings.** Ring 1, the outer line: 3 relay stations near its middle (50 m apart; flank relays 85 m
  out made the attack march up and down the line), a strongpoint every 26 m (small and medium tower
  hardpoints behind sandbags), belts of tank traps and wire with gaps. Ring 2, the walls: an L at
  x = z = 40, each arm with a closed main gate on the road to the keep and an open sally port far out
  on its flank, 3 shield generators, the super-gun, fuel depots and ammunition dumps (they chain
  when hit), stores and barracks (bounties). Ring 3, the keep (walls from
  83.4 to 134, a closed south gate and an open west one): the HQ, large towers and the utility
  modules. `siegeRings` are the distances to the wall lines (85 and 41.6).
- **No set piece closes every way.** The sally ports (open gateways) are the long way into each ring,
  so with every gate shut and every hardpoint filled the HQ, the relays, the generators, the super-gun,
  the line's stop and the defenders' rally can all be reached; the generator checks it, and again with
  every wall down, and warns if the walls would not hold with the sally ports shut too (none do). A
  hardpoint that cuts a route off is dropped, the one whose going opens it.
- **The attack breaks the gate first.** While the current stage's objective is behind the walls and
  nobody has broken them (no gate blown, no wall down) and the attacking army is outside, the
  attacking commander's goal is the walls' standing gate nearest it and its target that gate
  (`SiegeMode.AttackGoal`, `AttackTarget`); once breached, the objective. In stage 3 the enemy in
  Defend also blows in the keep's gate first; the player's army in Siege uses the keep's open gate
  (`KeepGateFirst`: going round to the shut one cost the sieges their last minutes). Stage objectives
  are the ones nearest the attacking army (not its camp). Gates are centred on odd metres so that,
  blown in, each leaves three navigation cells.
- **Gates and walls.** `fortress_gate` (3200 hp) blocks the way and direct fire until blown in; a
  `base_wall` piece keeps blocking for 1.4 s while it topples (`PropDef.Collapse`), then its rubble is
  passable. The view: a gate is two steel doors that go over inwards; a wall section rocks, goes over
  on its long side and settles into a low heap, in dust and fire.
- **Breaches and parked guns.** A wall coming down rebuilds the lane map at once, and every rebuild
  releases a firing spot that has become a doorway (the gun picks another): artillery must not park
  in a fresh breach. Shared code (LaneMap, TacticalAi), so noted for the merge.
- **The dome.** While a generator stands the dome covers the keep: its towers and the HQ cannot be
  hurt, and the keep's towers hold their fire (`Vehicle.HoldFire`). Invulnerable guns firing out
  through the dome killed most of the attackers in stage 2. It drops with a flash and a shockwave when
  the last generator dies (an alert, and the keep fight begins).
- **The super-gun** is a static `super_gun` (the heavy fortress model at 1.8x, 5200 hp, no gun of its
  own) in the walls' yard. It fires one `super_gun_shell` (450 damage, 15 m, 4 s warning circle) on a
  countdown at the attackers' thickest knot (their camp when nobody is out): first after 150 s, then
  every 90 s in Siege (90/75 s by default). Destroying it pays the attacker 25 CP at once and, in
  Siege, 100 coins at the end. In Defend it is the player's and fires at the waves.
- **The line in.** Every siege map has a runway (ashfield, dunebreak, redrock, greenvale, emberridge,
  skyhold, junglepass: its rail line could not be reached) or a rail line (frostpeak, ironport,
  whiteout, rustyard, metrocity, redrock: no room for a runway). It lies in the outer works by the west
  sally port, coming in over the north edge (rail) or from the west (runway). While the fortress holds
  its walls, the AI defender's ground deliveries come in by it: a train or a transport is announced
  (`SimEvent.Arrival`) 10 s before it stops, the vehicles get off at the stop when it does (at least
  16 s between two), no parachute. The player's own fortress (Defend) keeps the usual drops.
- **Searchlights and sirens.** At night up to 16 floodlight masts in the fortress sweep a light cone
  and a pool over the approaches and lock on to attackers within 42 m (view only). Every fortress alarm
  sounds the siren (the existing sound): gates blown in, a wall breached, the dome down, the super-gun
  firing or destroyed, a line lost, a wave; at night the fortress also sounds it when it spots
  attackers on its ground (at most once a minute; the session tells the mode when night falls).
- **The fortress's towers are a base loadout.** The fortress is its side's `TeamBase`
  (`BaseSystem.EstablishFortress`): its hardpoints by ring (about 11/12/8, 3 utility), the k-th of a
  size taking the loadout's towers of that size in order and over again (a fortress has more
  hardpoints than a camp); a size the loadout has none of takes the next smaller size's; each utility
  module once. Siege: the enemy's `BaseLoadout.ForAi(difficulty, style, seed)`; Defend: exactly the
  player's `PlayerProfile.BaseLoadout` (with its branches, ranks and gear, which the player's boosts
  add). Inner rings are tougher (health and damage by ring: default 1/1.25/1.5 and 1/1.1/1.2; Siege
  1/1.15/1.25 and 1/1.05/1.1; Defend 1/1.4/1.8 and 1/1.2/1.35).
  An AI fortress never flies towers back in (rebuilt keep towers made it untakeable); the player's can.
  Siege on Normal leaves a quarter of the outer two rings' tower hardpoints empty (`Manning`: Easy
  0.6, Normal 0.75, Hard 1).
- **Defend's lines.** The three rings are the outer, middle and inner line, the HQ the last stand
  (its 75/50/25 % phases). Losing a line (its relays, then its generators) blows up its remaining
  towers one after another, marks its hardpoints lost and pays the player a retreat reward (24, then
  32 CP in Defend, a toast). The HUD says "Line n/3". Defend's relays and generators are twice as
  tough (`LineHardening`) and its HQ 4.5 times (Siege 1.2).
- **Waves are swarms, drawn one ahead.** Defend and Endless waves are mostly cheap vehicles (armoured
  cars, rocket and ZU-23 technicals, FPV drone trucks, light tanks, car bombs, jeeps) growing wave on
  wave (Normal: 5, then +1.4 a wave, at most 36; Hard +1.6, Endless +2), a heavy vehicle for every third wave (at most a
  quarter of the wave), elites from wave 6 in Endless. The next wave is drawn when the last is sent,
  with its own random numbers, so the HUD's preview (icons and counts, elites marked) is exactly what
  lands. `SiegeRules.MaxAlive` (48) caps the attackers alive at once: a wave's vehicles beyond it wait
  off the map and come in as attackers fall (the preview shows how many wait).
- **HUD.** Two self-contained elements under the top bar, styled in Hud.uss: `SuperGunTimer` (red in
  the last 10 s, mint when it is the player's) and `WavePreview`. They sit at 104 px, below the boss
  bar's place; the theme rebuild can move them.
- **Weekly fortress.** It gets the new fortress (its map is a siege map) with the enemy's loadout;
  the session's other changes are kept to that and the gate goal, for the merge with the weekly
  ledger.
- **Campaign.** Mission m13 (Emberridge siege variant) raises the fortress's towers for the enemy
  (they were map units before); it still wins (14.1 min on its test seed).
- **Balance, 5 seeds on Normal** (`SiegeBalanceTests`, `MB_BALANCE=1`; ashfield, dunebreak, ironport,
  redrock, metrocity):
  - Siege: 5/5 won, in 14.0, 17.8, 12.8, 15.7 and 9.7 min (the run before: 5/5, 9.5-17.8 min; and
    `ModeEndingTests` on Ashfield: 5/5 won, 13.9-18.7 min). Stage 1 falls at 1.2-1.5 min, stage 2 at
    3.6-4.7 min; the keep takes the rest. The bank is 8 + 6 + 6 min, at most 15 min on the clock at
    once (Hard 7, Easy 9 to start), so no siege goes past about 21.5 min with its overtime.
  - Defend: 3/5 held on the five maps in the last two runs (Ashfield and Metro City fell at 9.8-10.2
    min, just before the enemy's clock of 10.5 min ran out; the run before those: 4/5), and 5/5 held on
    Greenvale (`ModeEndingTests`, 9.0-10.5 min). So `SiegeBalanceTests.DefendIsHeldOnNormal` (4/5
    wanted) is still failing when run by hand; it is behind `MB_BALANCE=1`, so the normal suite is
    green. Candidate fixes, unmeasured: stage bonuses of 45/60 s instead of 60/90 (the clock would
    end at 9.75 min, before both losses), or a slower third line. Defend stays short on purpose: a
    10-minute enemy clock let it finish the HQ in every seed.
  - Endless: the HQ falls after 10.3-11.7 min (5 seeds on Ironport).
  - What made the difference, in order: the relays moved in (the attack stalled marching along a 400 m
    line), the keep's guns silent under the dome, a smaller Siege garrison (12 CP, 0.6 CP/s, supply 26
    on Normal; with 20 CP and 0.85 CP/s it outnumbered the attack and killed it outside the walls),
    no rebuilt towers in an AI fortress, a quarter of the outer hardpoints empty on Normal, more CP for
    the attacker (38 CP, 2.4 CP/s, supply 44), more time, the HQ at 1.2x and the keep's open gate;
    for Defend a bigger purse for the player (30 CP, 1.35 CP/s) against a smaller one for the enemy
    (22 CP, 1.1 CP/s), tougher relays, generators, HQ and inner lines, bigger retreat rewards.
  - The sim is chaotic: the same settings went 3/5 to 5/5 and 2/5 to 4/5 with small map changes, so
    the lead should run the two tests again after merging other balance work.

- **Merging the fortress with the eight new maps (lead).**
  - The fortress generator was built on the first twelve maps. On the causeway battlefields,
    Swamp and Coral Isles, its walls cut every causeway: with the gates shut, nothing reaches the
    HQ. Those two keep the classic corner fortress in Siege (`CLASSIC_SIEGE` in build_maps.py),
    with its defences as map units. SiegeMode and the views accept a map without a fortress plan.
    The tests expect the classic fortress there.
  - All 20 maps were regenerated together from the merged generator, so the Conquest, Survival and
    Siege versions share one outline again. The Conquest versions moved a little from the committed
    ones (a few hardpoints by about 2 m, some building variants), because the merged generator
    draws its random numbers in a different order.
  - The campaign sweeps run again in the testing phase.
## 8. New content, elites and equipment

Prompt 8 (branch feature/content8). Every new thing is compared with what the game already had; the
comparisons, the numbers measured and what was dropped are here. Measurements come from the
equipment lab (`Tests/EditMode/EquipmentLab.cs`, `EquipmentRiskLab.cs`, MB_BALANCE=1): a duel is two
shooters of one card firing at a moving row of targets that hit back for nothing, summed through
`DamageSystem.DamageLog`; a soak is one vehicle under a fixed group's fire, its time alive per life.
Nothing new is tied to a weather, a biome or a map, and nothing is a hero card.

### A. Vehicles

- **Armoured bulldozer** (Heavy, 7 CP, 3,250 health in game (the brief said 3,500: see below), heavy armour, 5 m/s, a roof MG). Its main
  weapon is the blade (`dozer_blade`, a melee weapon: `WeaponDef.Melee`, 110 AP a blow every 1.6 s,
  4.5 m reach, three times the damage on structures, less on armour): the blow lands with the Blade
  node's stroke in the view. `breacher: true` flattens enemy obstacles it touches (dragon's teeth,
  hedgehogs, wire: `AbilitySystem.Plough`), gives it the engineer's breach bonus on structures, and has
  the tactical AI send it at the nearest obstacle or tower ahead within 70 m (a tower only when the group
  is strong enough), after the existing breach pass. `mineArmor: 0.5` halves a mine's blast (mines now
  hit as `HitKind.Mine`); it does not clear mines, the sapper does. Unlocked by mission 7 (act II) and
  added to Varga's deck (balance.json `generals.varga.deck`; a mission with Varga as its general adds it
  to its enemy deck).
  - Against the turtle tank (8 CP, the sponge): at the brief's 3,500 the bulldozer had more health (against 3,250) but
    no drone armour, no mine immunity and no gun, so the line does not fight while it soaks; measured
    under the same fire: equal under mixed fire (33.3 s a life each), 17.6 s against 17.0 s under tank fire (deaths fall on the attackers' salvos: the same 17.6 s at 3,500 and at 3,250 health). The brief's 3,500 health is cut to the turtle's 3,250 so the rule "no better a sponge than the turtle" holds by construction: with the same health the turtle adds drone armour, mine immunity and a 120 mm that fights while it soaks. Per CP the bulldozer still soaks more (7 CP against 8); it is meant to go in first at a base, not to hold a line.
  - Against the siege tank (12 CP, 203 mm, wrecks structures from range) and the sapper (5 CP, mines and
    repairs): the bulldozer is the close-range wrecker (a gun tower down in 37 s against 125 s for the
    turtle tank in `Prompt8ContentTests`), the siege tank the long-range one, the sapper the mine
    clearer; none replaces another.
  - Counters: the enemy commander scores cards that kill armour higher (+0.7 each, up to two) for every
    bulldozer it sees; its own bulldozer scores +1.8 against a side with two or more towers or obstacles
    known, -1.5 otherwise (no bulldozers in an open field battle).
- **SP howitzer**: no new vehicle, two mechanisms. Shoot-and-scoot (`scoot`: after 3 rounds from one
  spot, once its reload is under way, it drives 15-20 m to a spot across its line of fire, then angled
  back, then straight back, still in reach of its target and clear of its minimum range; it tries again
  after its next rounds if nowhere fits; never while the player has it on a move). Marked targets
  (`markedSpread: 0.15`): a target under a mark, a reveal or a scan (radar, UAV scan, laser designator)
  gets 15 % of its scatter (mean miss 3.0 m plain, 0.45 m marked). Its damage a second: 42 held in place, 44 with shoot-and-scoot (it moves during its reload, so the move costs no fire); no damage or price change was needed.
- **Not added:** a fast assault tank (the tank destroyer at the same 6 CP already out-hits it on heavy
  armour, 78 DPS, and the wheeled gun has the fast role) and a turretless tank destroyer (the twin tank
  at the same 9 CP has the same damage with a turret, and the tank destroyer the reach).

### B. New base types (values at Legendary, top level; the lower rarities follow the existing ladder)

| base | slot | Legendary | branches | against what was there |
|---|---|---|---|---|
| Flanking rounds | Weapon | +20 % damage into flank and rear | Armour, Light | the only flank bonus on a piece (the wheeled gun's is its own) |
| Airburst rounds | Weapon | +30 % damage on drones, rockets and missiles (shooting them down too) | Armour, Light | replaces the hyper-velocity charge; the proximity fuze stays for aircraft, this one for drones and rounds in flight |
| Spare magazine | Loader | a launcher that runs dry reloads at once, once a life | branches with launchers or magazines (read from the weapons) | the only magazine piece; hot swap shortens every reload, this saves one |
| Radar-absorbent coating | Armour | enemy missiles must come 20 % closer to lock on | all | flares and APS act after the lock; this before it |
| Laser warning | Optics | smoke 8 m round it when an anti-tank missile locks on, every 20 s | Armour, Light | the smoke discharger acts on health, this on the lock |
| Reverse gearbox | Engine | +40 % reverse speed; its AI backs off nose-on from enemies closing in | Armour, Light | Rearguard lowers damage when moving away, this makes the move |

### C. New unique lines (Epic / Legendary)

- **Vengeance** (Loader): a friend dying within 15 m gives +15 % / +20 % damage for 5 s; it never stacks
  with itself (the best holds). Dark Crown is a small permanent gain; Vengeance is a burst after a loss,
  so the two do not overlap.
- **Suppressive Fire** (Weapon): a hit slows the target's fire by 10 % / 15 % for 3 s, scaled by the
  proc coefficient (I.3).
- **Rearguard** (Engine): 15 % / 20 % less damage taken while moving away from the enemy.
All three hook into the existing gear events and show their small text over the vehicle when they fire.

### D. New brands

- **Phoenix Recovery**: 2 pieces +10 % repair received; 4 pieces: healing past full health becomes a
  shield of up to 10 % of health for 8 s. Overlap with the Quartermaster (also +10 % repair received on
  two pieces): kept, because the four-piece bonuses differ (refunds against overheal); the repair
  received line keeps its cap, so the two do not stack past it.
- **Wolfpack Tactics**: 2 pieces +4 % damage per friend within 15 m (up to three); 4 pieces: three or
  more firing at one target all fire 15 % faster.
- **Bulwark Engineering** (towers only): 2 pieces +10 % tower health; 4 pieces: a destroyed tower leaves
  a machine-gun post for 20 s (`bulwark_post`). Pieces are counted across the whole base's tower gear
  (one tower type rarely holds four), and it drops on 35 % of tower pieces.
- **Not added:** roof cage armour (the anti-rocket cage already cuts drone damage and the artillery roof
  bomb damage), a helicopter hunter (Light only, and the proximity fuze and AA pintle already do it),
  Talon Precision (on artillery the fire-control computer does it), cavalry (weaker than the existing
  rapid deployment), target marking and a data link (the laser designator does both), a first aid kit
  (the emergency repair kit does it).

### E. Bosses

The general part mechanism (`VehicleDef.Parts`, `BossSystem`): a boss lists parts, each with a share
of its health, a model node (`Part_*`), a position and radius for aiming, the weapon mounts and skills it
carries, and what its loss does (speed, spread, failure chance on the mounts it affects, damage to the
body). A `partLock` makes the body take no damage until enough parts of one kind are down. Shots at a
boss pick a part (a locked body: the lock's parts; otherwise the most threatening part, 40 % the body);
guided rounds fly to the part's position; a broken part hides its node and leaves a wreck piece. Prompt
9 puts parts on every boss with this data only.

| boss | general | what it does | how it differs from every boss before |
|---|---|---|---|
| Rail supergun | Kessler | static on its rail at the map edge; a shell every 20 s anywhere on the map, 3 s warning ring; a targeting station (kill it: the shells scatter) and gun emplacements guard it; tractors on the rail | the only boss that hits the whole map without moving: the player must dodge and push at once (the trains move, the fortresses have a reach) |
| Earth Worm | Varga | dives (not targetable), surfaces under the player's biggest group after a 2 s crack warning, stuns ground vehicles within 15 m, takes 1.5 times damage for 6 s after | the only boss that cannot be shot most of the time and comes to the player |
| Command airship | Quạ Đen | four engines, two drone hangars, one radar; the hull only after two engines; hangars down stop the drones, the radar down spoils its flak; anti-air and fighters only | the first multi-part boss: the fight is choosing what to break |
| Landing hovercraft | (coast) | runs its coastal route (the trains' route logic) and lands 3-4 vehicles at each landing point, five landings | a race against its landings, not a damage race; the trains carry nothing |
| Supreme Commander | Hùng | a super-heavy command vehicle with little fire of its own; every enemy within 40 m +20 % damage and +20 % fire rate; elite escorts, more at 60 % | a force multiplier: kill it first or fight a stronger army |

All five are in Boss Rush (with their escorts, 52 min limit), with guide cards, their generals' radio
lines on arrival and at half health, and their parts on the boss bar.
Campaign placement proposed (the campaign rework wires it; its branch already names these ids):
the hovercraft in chapter 1 (the landing beach), the Earth Worm in chapter 2 or 6 (Varga), the rail
supergun in chapter 4 (Kessler's port, as a stage of the chapter's operation), the airship in chapter 7
(Quạ Đen's sky war), the Supreme Commander in chapter 8 or 9 (after Hùng's betrayal), each a mid-chapter
boss or a stage, not a replacement for the chapter's final boss.

### H. Elites

- **One footing.** Every elite: 1.6 times its base card's health (the data's "hp"; a test holds it),
  1.25 times its damage (`VehicleDef.DamageScale`, from balance.json `elites.damageScale`), one or two
  of the existing elite skills. Signature guns kept (the 125 mm, the 152 mm HEAT, the 105 mm APFSDS at
  46 m, paired Hellfires, cluster rockets, airburst flak) but brought back to about the base card's damage
  a second, so the scale is the difference. Before, the ratios ran from 1.03 (the Grad) to 3.97 (the AA).
- **Measured power** (duel damage a second times time alive, 3 seeds, a 480 s soak so a tough elite is
  not capped by the window): all twelve between 1.84 and 2.2 (ROSTER_BALANCE.md has the before and after tables). What it took: the EW carrier
  keeps the EMP and drops its smoke (the brief's example); the heavy tank keeps its overdrive and drops
  its repair (repair alone made it 2.9); the battle tank's shield is 30 % (it alone was 2.65 at 60 %);
  the rocket elites' salvos are much lighter (sixteen cluster rockets on three targets were worth 2.9
  times the base's damage). The new elites' one skill is worth more than the others', so their damage
  scale is lower: FPV carrier 1.1, SP howitzer 1.15, long-range SAM 1.2, attack jet 1.0 (its long flares
  alone double its life under missile fire). elite_repair is now on no vehicle; it stays in the data.
- **New elites**: FPV carrier (barrage), attack jet (long flares), long-range SAM (overdrive), SP
  howitzer (barrage): the enemy decks' commonest cards with none. Each skill fits the class (flares only
  on aircraft; barrage on salvo and drone launchers and the howitzer). They use their base card's model
  repainted (see ASSET_DEBT.md). The Grad elite stays an enemy card.
- **Budget, not chance.** `EliteBudget` per side (sim): an elite costs 1.6 times its base card (the
  difference charged when the delivery is promoted); a share of the side's spending may go on elites
  (Easy 5 %, Normal 10 %, Hard 15 %, Heroic 20 %, Iron 25 %; the mission tier sets Heroic and Iron) with
  at most 1/2/3/4/5 out at once. A delivery is promoted when the elite's price keeps the elites' part of
  all spending within the share. A general's favoured cards get the whole share, the rest half
  (`otherShare`): Varga tanks and heavy tanks, Orlov artillery, Sen drones, Quạ Đen aircraft. Waves and
  reinforcements are counted at their CP value and follow the same budget; a siege's late waves raise
  the share as they did the chance (0.08 a wave from the sixth), and the cap with it. The menu battle
  gives both sides Normal. Boss escorts and summons are scripted and outside the budget.
  - Consequence: elites are no longer a free upgrade (a 25 % chance at Hard was up to +25 % power for
    nothing); at 1.6 times the price for about twice the power they are 1.25 times as strong per CP, so
    the budget adds share times 0.25 to the enemy's strength (Normal +2.5 %, Iron +6 %).
  - Enemy scaling: the campaign's matched boost (`EnemyScaling.Match`) is divided by the square root of
    1 plus that edge on health and damage (`EnemyScaling.WithElites`), never below the plain card, so the
    arsenal-matched enemy is as strong as before with elites in it, not stronger.
  - The mission's general is read from `MissionDef.General` once the campaign rework is merged (a
    reflection bridge until then, `MissionSession.GeneralOf`); quick modes have no general.
- **Refunds** at the elite price: an elite's `ArmyCost` is its price, used by the kill refund, the army
  value and the catch-up; the Quartermaster's own-loss refund uses it too.
- **Rewards**: each elite destroyed pays 10 coins, for the first four of a battle (at most 40 against
  120-300 for a quick battle's win; Normal fields about two in a quarter hour, so about +20 coins or
  7 %), and 6 % of them drop a blueprint of their base card (only of a card the player can own). The
  cap keeps a long battle near prompt 7's curve.
- **Readability**: a gold ring round an elite's minimap blip; a radio line when the first elite of a wave
  arrives (the first of the battle, of a new numbered wave, or after 60 s with none); the gold health
  bar as before; each base card's Guide tab shows its elite version with its own entry and skills.

### I. Equipment

- **I.1 Fit matrix from the data.** balance.json `branches` names each class's branch (Armour: Tank,
  Heavy, TankHunter; Light: Light, Scout, AntiAir, Support; Artillery; Air: Helicopter, Plane; an
  aircraft is always Air). So the long-range SAM is Light (anti-air) and the FPV carrier Armour (tank
  hunter), which the old rule by minimum range put in Artillery. `VehicleFit` reads what each card has
  from its weapons and body and what each line needs; a class meets a need when a third of its cards do
  (a half left the carousel autoloader with one class; a third keeps lone oddities out), a branch fits a
  piece when one of its classes meets the need of its base type and its unique line together. Crates
  drop only fitting pieces, the equipment screen refuses unfit ones (greyed, with the reason), the
  branch pages list their classes, and save version 3 takes unfit pieces off into the inventory.
  EQUIPMENT_FIT.md is generated from the code.
- **I.2 Twin Feed**: bursts of three or more get the extra round as before (+12 % salvo at Legendary);
  one- and two-round weapons get +15 % / +20 % damage a shot instead. The salvo share was raised from +12 % to +20 % at Legendary (+15 % Epic) so salvos match single shots. Measured (2 shooters, 5 seeds): tank cannon +14.5 %, long gun +15.7 %, railgun +22.8 % (it was -16.8 %: the old extra round wasted its charge), howitzer +22 %, flame +18 %, machine gun +17 %, heavy flak +23 %, bombs +16 %, jet cannon +11 %, flak +8 %, ATGM +8.5 %; the autocannon (-1 %) and the rocket salvo (+1.6 %) still gain nothing measurable (the missile of the IFV and the magazine of the MLRS dilute the duel), to look at in the testing phase
- **I.3 Proc coefficient**: the main weapon's time between hits (a burst or a charge counted whole,
  machine guns 1.7 times) over 1.5 s, clamped to 0.15-2.5, multiplies every on-hit chance and flat on-hit
  amount (ricochet, incendiary, shredder, suppression, momentum, suppressive fire...). Shredder needs
  more hits a stack on fast guns (a hit adds the proc coefficient's share of a stack, up to five stacks of 4 % more damage taken at Legendary). Spread of each offensive line's gain
  between weapon groups: Ricochet now carries the damage share of the hits that earned the bounce (a fast gun bounces seldom but hard), so it no longer favours slow guns 17 to 1 (railgun +28.5 %, flak +1.7 % before; now 7.6 % to 31 % across groups, flak +16 %, heavy flak +8 %). Incendiary, momentum and opening salvo retuned (below). The measured spread is still above the 1.5 times the brief asks for on several lines (EQUIPMENT_VALUES.md): the duel dilutes a main-weapon line with the secondaries, and its targets respawn every 0.5 s, which inflates opening and kill lines on slow guns; a fairer harness (MainOnly duels, longer-lived targets) is for the testing phase.
- **I.4 Cluster warheads** burst on the first two rounds of a salvo only (`ClusterRounds`), so a bomber's
  or a rocket launcher's salvo gets about the same +20-30 % as a single-shot gun. Measured after raising the bomblets to 8 at Legendary: howitzer +13.8 %, rocket salvo +11.4 %, bombs +8 % on a line of targets; on a tight group (3.5 m) MLRS +11.6 %, SP howitzer +6.6 %, bomber +5.6 %: no weapon runs away with it any more; the +20-30 % the brief aims at on structures is still to measure
- **I.5 Module scale**: fixed-effect modules (drone escort, uplink barrage, mine dispenser, EMP payload)
  and the fuel blast are scaled by clamp(CP / 7, 0.4, 1.3) of the card's price (an elite: its elite
  price); the fuel blast is capped at 1,500. Measured: a Legendary drone escort adds about 1.2 damage a second per CP on a 2 CP scout jeep and on a 7 CP battle tank alike (1.9 on the heavy tank), so spamming cheap cards with it no longer pays
- **I.6 Refund caps**: a kill refunds at most 45 % of the victim's price (base 25 %, War Profiteer and
  the Quartermaster four-piece included: together they would reach 50 %); the own-loss refund at most
  15 %. Snowball: the cap bites only on a stacked killer, so the winning side's pace changes by at most
  that 5 %.
- **I.7 Trade-off pieces** (heavy barrel, hair trigger, overtuned engine, monolithic plate) drop from
  Rare up only and their drawback grows with their rarity (-5/-6/-7 % speed on the heavy barrel), so
  every piece that drops is a net gain; the alternative (a scaled drawback at Common) left two tiers of
  nearly nothing.
- **I.8 Cleanup**: the hyper-velocity charge retired (airburst rounds take its place), turbocharger and
  turret drive merged into the drivetrain, mine rollers renamed underbelly armour (mines and blast
  damage, so it works in every battle), the signal relay adds 10 % vision, the monolithic plate's main
  stat shown (no raw key). Old pieces convert in place (same slot, rarity, level: `GearCatalog.Replaced`).
- **I.9 Tower gear**: three slots a tower type, shared by every tower of that type; `TowerFit` limits
  each piece to the tower types it works on; Bulwark counts across the base. One-tower bases in
  Legendary gear against the mixed base in the same gear: no one-tower base is the best against every army. Against the mixed army the mixed base scores 1.89 and only the ATGM and heavy-turret bases tie it; the rocket battery base is best against armour (1.86 against 1.38) and worst against a mixed army (1.35); every one-tower base collapses against artillery (0.31-0.74 against 1.00). No change to tower gear or hardpoints.

| base (Legendary tower gear) | mixed | armour | light+drones | artillery | air |
|---|---|---|---|---|---|
| mixed | 1.89 | 1.38 | 1.69 | 1.00 | 2.00 |
| only gun_turret | 1.86 | 1.67 | 1.61 | 0.74 | 2.00 |
| only atgm_tower | 1.89 | 1.59 | 1.41 | 0.31 | 2.00 |
| only rocket_turret | 1.35 | 1.86 | 1.47 | 0.31 | 1.99 |
| only heavy_turret | 1.89 | 1.21 | 1.42 | 0.31 | 1.98 |

Score: HQ health left plus share of the attackers destroyed (0-2), 3 seeds, 5 minutes.
- **I.10 No chained last stands**: once Unbreakable, the Aegis barrier or the Phoenix overheal saves a
  vehicle from a killing blow, the others cannot fire for 6 s (`LastStandGap`). Measured on a heavy tank under two tanks and a tank destroyer: Unbreakable alone +15 % time alive, with the emergency kit and the Phoenix four-piece +36 %: they add up, they do not chain
- **I.11 Values**: EQUIPMENT_VALUES.md (generated) lists every line and module's numbers and the lab's
  measured gains. Offensive lines mostly land between +8 % and +25 % where they apply; deliberate exceptions: Opening Salvo and Kill Reload on slow guns and bombs (+35 % railgun, +62 % bombs for Kill Reload: the lab's fast target turnover), Unbreakable on fragile vehicles (+140 % on the helicopter, +8 % on the tank: a flat 2.5 s and one blow are worth most where lives are shortest), and the lines that act outside a duel or soak and read zero there (sight, stealth, capture, economy, debuffs on targets that do not shoot back, friends dying, repairs out of combat). Retuned in this pass: Twin Feed (salvo share 12 % to 20 %), Incendiary (14 % to 25 %), Opening Salvo (80 % to 50 %), Momentum (4 % to 7 % a stack), Cluster Warhead (6 to 8 bomblets), Ricochet (bounce weight)

### J. Measurements and tests

- Tests: `Prompt8ContentTests` (the bulldozer, the SP gun, the five bosses and the part mechanism, Boss Rush), `EquipmentPrompt8Tests` (fit matrix, new bases, lines, brands, proc coefficient, Twin Feed, cluster, module scale, refund caps, trade-offs, migration), `ElitePrompt8Tests` (footing, budget, caps, generals, waves, refunds, rewards, enemy pace), plus the updated gear, tower gear and model tests. The last full EditMode run: 614 tests, 561 passed, 0 failed, 53 skipped (balance measurements), before the last tuning pass (see the hand-off).
- The lab (MB_BALANCE=1): `EquipmentLabTests` (roster DPS, elite power, offensive lines, Twin Feed), `EquipmentRiskLab` (risky combinations, defensive lines and modules, the sponge, the scoot, one-tower bases), `EquipmentDocsExport` (writes EQUIPMENT_FIT.md and EQUIPMENT_VALUES.md).
- Risky combinations measured (the full table is in EQUIPMENT_VALUES.md): Twin Feed on the battle tank +14 %, on the railgun +22 %; ricochet on flak +16 % and heavy flak +8 %, shredder on flak +9 %; cluster on the bomber within noise, on the MLRS +11 %; the drone escort module about the same per CP on a jeep as on a tank; War Profiteer with the Quartermaster four-piece capped at a 45 % refund (it would be 50 %), the Quartermaster's own-loss refund 10 % under the 15 % cap; Wolfpack on six jeeps +17 %, on three tanks +18 % (it is not a swarm tool only); the SP gun with the laser designator +8 %, the counter-battery radar adding nothing in a duel (it answers enemy artillery); Unbreakable, emergency kit and Phoenix on a heavy tank +36 % time alive.
- Not run (left to the testing phase by the lead's instruction): the five-seed campaign sweep after the elite budget, the Boss Rush and Conquest ending sweeps (the Boss Rush cap in `ModeEndingTests` is now 55 minutes for its ten bosses), the snowball measurement after the refund caps, the rerun of the offensive lines after the last retune of Twin Feed's salvo share.
## 9. Boss parts

Prompt 9 (branch feature/boss-parts, from f64198c): the general part mechanism of prompt 8 on every
boss, fire and smoke at the breaks, the part order, and the part row under the boss bar.

### A. The general rules

- **Health.** A part's full health is a share of the body's full health (`hp` in the data), read
  live, so a boss made tougher after it spawned (a mission's stronger form, the campaign's pace, a
  harder tier) has tougher parts: the scaling needs no code of its own. Each part is 8-15 % of the body
  (the Spectre's four engines 7 %: nine parts would pass 70 %); in all 50-70 % for bosses with five or
  more guns, and 35-47 % for the few with only three or four things worth breaking (the Supreme
  Commander, the Earth Worm, the trains, the Tempest, the Inferno): padding them with parts that do
  nothing would only make the fight longer.
- **Body health retuned** so the kill takes about +12 % longer than before (the brief's 10-15 %). The
  model: every part broken before the body falls costs its health in fire, and gives 30 % of it back to
  the body, so the fire needed is body + 0.7 x parts; the body is cut to 1.125 / (1 + 0.7 x share) of its
  old health (x0.76 to x0.90, table below). It is a model, not a measurement: the rounds that go at a
  part that never breaks are lost too (it makes the kill a little longer), and the guns that go
  silent make the fight easier (a little shorter). The five-seed kill times are for the testing phase.
- **The body always takes damage.** Only the command airship keeps its lock (its hull shut until two
  engines are down), and it keeps its prompt 8 design: no share of a broken part on the hull
  (`breakDamage: 0` on its parts) and the radio line on its drone bays.
- **Breaking a part:** its mounts never fire again; a skill stops once every part that carries it is
  broken (the Hive's two drone racks share its launches: one rack down silences its own launcher,
  both down end the launches); its mechanism stops (`stops`: the supergun's shot, its fire control,
  the Earth Worm's dives, the hovercraft's landings, the Supreme Commander's aura); its penalties apply
  (speed, turning, cadence, spread, lost locks); and the body takes 30 % of the part's full health
  (a raw hit: no armour, no shield, and it can finish the boss). Everything a broken part takes away
  is recomputed from scratch from the set of broken parts (`BossSystem.Recompute`), so a patch undoes
  exactly what the break did.
- **Only direct hits damage parts.** Blasts, fire, strikes, pierces and bounces land on the body
  (unchanged since prompt 8), so artillery gets no multiplied damage out of a boss. New: a round that
  lands on a part standing out past the hull's round footprint (a hovercraft's fans, a train's
  locomotive, a supergun's tractors) is a hit on that part; before, it missed the boss altogether.
- **Self-repair.** `train_patch` (the Iron Train's and the Bastion's) is a new skill kind, Patch, on a
  new trigger, PartBroken: once a battle, one broken part comes back at 50 % of its health instead of
  the body healing 20 %. The part with the strongest weapon is the one with the heaviest round against
  ground vehicles (its damage a round against the armour it suits better): a main gun before a rocket
  pod or a flak mount, whatever their rate (by damage a second the train would have mended its flak
  first). A part is patched at most once; its broken piece is taken off and the part shown whole again.
- **Health thresholds** (escorts, rage, shields, phases) still count on the body alone.
- **Aim.** A shooter goes for the live part most dangerous to it that its weapon can reach: the part
  whose guns can hit it (their damage a second against its armour), anti-air for the parts that shoot
  at aircraft (it is shielding its own), a tank hunter for the toughest part; a part that drives a
  skill or a mechanism counts a little extra; two rounds in five still go at the body. While the
  airship's hull is shut, the engines first, as in prompt 8.
- **The part order** (`CommandType.FocusPart`, journaled like every player command): every unit of
  the side whose weapon reaches the part aims every round at it, and units in reach of the boss pick
  it as their target first (x4 in the target score), until the part breaks or the order is cancelled
  (the same part tapped again, or a null part). The support AI never calls strikes on parts: a strike
  is a blast, and blasts land on the body (tested).
- **Boss Rush** pays 2 CP for every part broken, once a part (a patched part broken again does not
  pay twice), on top of the health-step bounties.
- **Checkpoints** are replays (prompt 5), so they keep the parts' health, broken and patched state as
  long as the battle replays the same: `SimWorld.StateHash` now takes every part's health (to a
  thousandth), broken and patched flags and every side's part order, and a replay test checks a
  battle with a part order, a cancel and broken parts replays to the same hash and the same parts.
- **The Bastion's four autocannon turrets** each cover their own quarter (a new per-mount `arc`,
  centre and half-width in degrees, handled like the broadside guns): front left, front right, rear
  left, rear right, 80 degrees either way, so two turrets bear on any bearing and breaking the two on one
  side opens that side.

### B. Every boss's parts

Mount numbers are the def's (0 the main weapon, then the secondaries in order). Health: old body
health → new.

| boss | body health | parts, share of the body | each part: share, what breaking it does |
|---|---|---|---|
| Iron Train (`armored_train`) | 5400 → 4400 | 5, 56 % | locomotive 12 %: speed x0.50; radio line<br>gun_car_front 12 %: mount 0 silent; radio line<br>gun_car_rear 12 %: mount 4 silent<br>rocket_car 10 %: mount 1 silent<br>flak_car 10 %: mount 3 silent |
| Doomsday Train (`nuke_train`) | 6400 → 5450 | 4, 46 % | locomotive 12 %: speed x0.50; radio line<br>twin_gun 14 %: mount 0 silent; radio line<br>flak_front 10 %: mount 1 silent<br>flak_rear 10 %: mount 2 silent |
| Behemoth (`behemoth`) | 6200 → 4950 | 6, 58 % | main_gun 14 %: mount 0 silent; radio line<br>gun_120 10 %: mount 1 silent<br>flak_r 8 %: mount 2 silent<br>flak_l 8 %: mount 3 silent<br>missiles_r 9 %: mount 4 silent<br>missiles_l 9 %: mount 5 silent |
| Tempest (`behemoth_tempest`) | 5600 → 4750 | 4, 47 % | railgun 15 %: mount 0 silent; radio line<br>coil_l 10 %: mount 1 silent<br>coil_r 10 %: mount 2 silent<br>shield 12 %: skill mothership_shield off; skill boss_bulwark off; radio line |
| Inferno (`behemoth_inferno`) | 6800 → 5800 | 4, 46 % | flamer_r 12 %: mount 0 silent; radio line<br>flamer_l 12 %: mount 3 silent<br>thermo 12 %: mount 1 silent<br>flak 10 %: mount 2 silent |
| The Hive (`fortress_hive`) | 8000 → 6350 | 6, 60 % | rack_l 12 %: mount 0 silent; skill mothership_launch off; radio line<br>rack_r 12 %: mount 1 silent; skill mothership_launch off; radio line<br>sam 10 %: mount 2 silent<br>flak_l 8 %: mount 3 silent<br>flak_r 8 %: mount 4 silent<br>emp 10 %: skill boss_emp off |
| Ice Fortress (`mobile_fortress`) | 9000 → 7000 | 7, 63 % | howitzer 13 %: mount 0 silent; skill fortress_barrage off; radio line<br>rockets_l 8 %: mount 1 silent<br>rockets_r 8 %: mount 2 silent<br>flak_l 8 %: mount 3 silent<br>flak_r 8 %: mount 4 silent<br>missiles 8 %: mount 5 silent<br>emp 10 %: skill boss_emp off |
| Bastion (`fortress_bastion`) | 11000 → 9000 | 5, 54 % | mortar 14 %: mount 0 silent; skill fortress_barrage off; radio line<br>turret_fl 10 %: mount 1 silent<br>turret_fr 10 %: mount 2 silent<br>turret_rl 10 %: mount 3 silent<br>turret_rr 10 %: mount 4 silent |
| Silver Bug (`silver_bug`) | 9000 → 7150 | 6, 60 % | laser 13 %: mount 0 silent; radio line<br>coilgun 10 %: mount 1 silent<br>flak 8 %: mount 2 silent<br>bay 10 %: mount 3 silent; skill saucer_drones off; radio line<br>shield 10 %: skill mothership_shield off; radio line<br>emp 9 %: skill saucer_emp off |
| Spectre (`sky_fortress`) | 12000 → 9100 | 9, 69 % | gun_105 9 %: mount 0 silent; radio line<br>gun_40a 8 %: mount 1 silent<br>gun_40b 8 %: mount 2 silent<br>gun_25 8 %: mount 3 silent<br>griffin 8 %: mount 4 silent<br>engine_1 7 %: speed x0.85<br>engine_2 7 %: speed x0.85<br>engine_3 7 %: speed x0.85<br>engine_4 7 %: speed x0.85 |
| Iron Bird (`mega_gunship`) | 15000 → 11500 | 8, 66 % | gun_l 8 %: mount 1 silent<br>gun_r 8 %: mount 2 silent<br>minigun_l 8 %: mount 4 silent<br>minigun_r 8 %: mount 5 silent<br>pod_l 8 %: mount 0 silent<br>pod_r 8 %: mount 6 silent<br>missiles 8 %: mount 3 silent<br>rotor_rear 10 %: turning x0.50 |
| Hive Mothership (`drone_mothership`) | 16000 → 12300 | 7, 66 % | cannon_bow 10 %: mount 0 silent; radio line<br>cannon_gondola 10 %: mount 4 silent<br>drone_bay 10 %: mount 1 silent; radio line<br>uav_bay 10 %: skill mothership_launch off<br>flak_top 8 %: mount 2 silent<br>flak_rear 8 %: mount 3 silent<br>shield 10 %: skill mothership_shield off; radio line |
| Rail Supergun (`rail_supergun`) | 7000 → 5500 | 6, 63 % | main_gun 15 %: no more shells; radio line<br>tractor_l 10 %: fires every x1.3<br>tractor_r 10 %: fires every x1.3<br>fire_control 12 %: shells fall wide<br>gun_l 8 %: mount 1 silent<br>gun_r 8 %: mount 2 silent |
| Earth Worm (`earth_borer`) | 9500 → 8150 | 4, 44 % | drill 14 %: mount 0 silent; no more dives; radio line<br>gun_l 10 %: mount 1 silent<br>gun_r 10 %: mount 2 silent<br>engine 10 %: speed x0.70 |
| Landing Hovercraft (`landing_hovercraft`) | 8000 → 6500 | 5, 54 % | ramp 14 %: no more landings; radio line<br>fan_l 10 %: speed x0.70<br>fan_r 10 %: speed x0.70<br>gun_l 10 %: mount 0 silent<br>gun_r 10 %: mount 1 silent |
| Supreme Commander (`supreme_command`) | 6500 → 5850 | 3, 35 % | antenna 15 %: no command aura; radio line<br>mg_l 10 %: mount 0 silent<br>mg_r 10 %: mount 1 silent |

Adapted to the data and the models:
- **Iron Train:** its model is one armoured car with one turret, but its data has two 150 mm guns: the
  two gun cars are the turret's gun and the second gun (a place on the hull), the locomotive and the
  second gun car places on the hull (no model of their own). The roof MG stays on the body.
- **Inferno:** its turret has two flamer nozzles but its data had one flamer: a second flamer mount
  was added and the flamer's damage halved (60 to 30), so the two together burn as before and each is a
  part.
- **Tempest:** the shield generator carries both of its shields (`mothership_shield` and `boss_bulwark`).
- **Silver Bug, Hive Mothership:** the shield and EMP emitters and the UAV bay have no nodes of their
  own in the models: they are places on the hull.
- **Rail Supergun:** its fire control is now its generator part (the model's `Part_generator`), not
  the separate targeting post in the field (removed from its guards): a part must sit on the boss to
  be hit. Breaking its gun ends the shelling; each tractor broken makes it fire 30 % less often (they
  power it). Its two autocannons are parts too.
- **Earth Worm:** its engine is a part as well (30 % slower). **Landing Hovercraft:** a fan broken, 30 %
  slower. **Iron Bird:** the rear rotor of its tandem pair is the "tail rotor": it turns (hull and guns)
  at half the rate.

### C. Fire and smoke at the breaks (the view only)

- All of it is in the Game assembly (`EffectsDirector.BossParts`, `VehicleView.BossParts`); the sim
  has no smoke zone, no sight change from it (tested: sight across a burning boss is the same before
  and after, and no smoke zone is added).
- A part under 50 %: thin smoke and sparks; under 25 %: thicker smoke and a small fire (a fire point).
  A break: a blast by its `fx` (guns and ammunition a big blast and, on High, flying debris; energy
  parts a flash, a blue shock ring and arcs; engines a fireball and smoke), then a fire and its black
  smoke column until the battle ends, arcs flickering on energy parts. The sim's own blast event for a
  break is drawn at the part instead of on the ground (it is still heard).
- The body: two small fires under 66 %, a big fire and thick smoke under 33 %.
- The fires ride on the part's parent node (a turret turns them with it) or on the model, so they follow
  the boss, and their smoke, emitted in the world, streams out behind a boss on the move; a flying or
  fast boss's broken engines also trail long black smoke.
- **Budget:** at most 8 fire points a boss (5 on Low); over the cap the two nearest are merged into
  one at their size-weighted middle, as big as both (`FireBudget`, tested). The points are rebuilt only
  when a part breaks or is patched, a part drops under a quarter or the body passes a threshold.
  Every fire goes through the shared `FireSpots` systems (pooled, culled off screen). Low also halves
  the smoke and sparks and drops the arcs; High throws physical debris. The heat haze round the fires
  on High is not done: there is no distortion pass in the pipeline (ASSET_DEBT).
- **Death:** every fire flares (a blast at each point) before the existing death blasts, and the wreck
  burns on for 25-35 s.
- **Sound:** the break is the sim's blast (heard as before); a low crackle follows a burning boss
  (louder the more parts are down, the fire loop's volume cap unchanged). Camera shake comes with the
  blast.
- **Outline:** the ordered part is drawn again from behind, pushed out along its normals, in pulsing
  gold (a new `MachineBrigade/Outline` shader), with a gold ring round it (the only mark for a part that
  is a place on the hull).
- **FPS** on the heaviest boss fight (many parts broken at once, escorts, Low): to measure in the
  testing phase on a device.

### D. Interface

- A row of small icons under the boss bar (`BossPartsRow`, styled in Hud.uss as one block): an icon by
  the kind of part, a thin health bar, broken ones greyed and crossed out, the ordered one ringed in
  gold. Tapping an icon, or the part on the boss itself (the nearest live part on screen within a
  finger's reach of the tap), orders every unit in reach at it; tapping it again cancels. A toast says
  which. The text line of prompt 8 on the boss's name (engine 3/4 ...) is gone; "hull shielded" stays.
- A radio line when an important part breaks (`radio` in the data): a main gun, a shield generator, a
  drone bay or rack, a locomotive, and the Earth Worm's drill, the hovercraft's ramp and the Supreme
  Commander's antenna, the three parts that end a boss's special mechanism. Other parts get the short
  toast. A patch has its own toast.
- The Guide tab of each boss lists its parts and what breaking each does, in words, from the data (so it
  cannot drift), with the general rule, its lock or self-repair, and a tip for fighting it part by part.

### E. Tests, and what is left to measure

- `BossPartsTests`: every boss's parts (count, shares, names, one part a mount); a broken part's guns
  fire no round and its skills are not used (all 17 bosses); the body always takes damage except the
  locked airship; a break costs the body 30 % of the part; blasts and strikes never touch a part; parts
  scale with the boss; each mechanism stops with its part (locomotive, rear rotor, engines, drill, ramp,
  fans, fire control, tractors, gun, antenna, shield generator); the Bastion's corner arcs; the
  self-repair patches exactly one part, the heaviest gun, once; aim goes for the dangerous part and two
  rounds in five at the body; the part order works, is refused for a broken or unknown part or one's
  own boss, is cancelled and ends when the part breaks; Boss Rush's 2 CP; the checkpoint replay; the
  fire cap; the guide words and radio lines; the smoke never touching sight.
- Left for the testing phase (the user's rule: short targeted runs only): kill times per boss with a
  standard deck over five seeds (the target: now to +15 %), every boss mission in the campaign and
  every Boss Rush fight still winnable on Normal, and the FPS check on the heaviest boss fight.

## 10. Field Command 2.0: foundation

The foundation of the prompt-10 rebuild: the token theme, fonts and type scale, the component
library with its preview screen, the card renders and the UI checks. The screens themselves
(sections D, E, G and H) are rebuilt on it afterwards.

- **One theme file.** `Resources/UI/Tokens.uss` holds every colour, font, type size, spacing step,
  border and control size as a `--fc-*` variable (the `:root` block, and `.fc-text-large` for the
  Large text size), then the kit's component classes (`fc-*`), which use `var()` only.
  `Theme.tss` imports it, so every panel of the game has the tokens at its root. `UiThemeTests`
  fails on a literal colour or font size below the token blocks, on an ellipsis, and on a colour,
  font size or spacing set from the kit's C#. In Hud.uss only the accent equals a token exactly, so
  `--amber` and `--accent` now read `var(--fc-accent)` (a pure rename; a test checks the old menu
  still resolves it); its other colours differ slightly from the brief's, and renaming them would
  restyle the old screens, so the rebuild moves them over screen by screen.
- **Units: 1 reference px = 1.114 panel px.** The brief's sizes are given at a 1400 px reference
  width. The game's panels are authored at 1280 x 720 and scale with the height on phones
  (`BattleHud.MatchFor`), so a 19.5:9 phone shows a panel 1560 px wide. The brief's device targets
  (44 pt touch targets, 11-12 pt body text) only hold if the 1400 px is that phone class's width,
  so the factor is 1560 / 1400. Converted: main button 42 px (37.7 at the reference), screen title
  30 (26.9), panel title and button labels 23 (20.6), body 21 (18.8), secondary 19 (17.1; nothing is
  smaller), big numbers 36; touch target 82 px (72 at the reference is 80.2; 44 pt on a 390 pt tall
  phone is 81.2), the main button's chamfer 20 px (18). Hairlines, bars and the spacing scale keep
  their literal values (1 px borders, the 2 px tab underline, the 3 px branch and nav bars, 4 px
  progress bars, the 8 px dot, spacing 4/8/12/16/20/24/32): converting them would only blur them.
- **Large text** (Settings > Text size: Thường / Lớn, `MatchSettings.TextSize`, saved as
  `mb.textSize`) is about 1.15x: 48 / 34 / 26 / 24 / 22, numbers 41. `Kit.ApplyTextSize` puts the
  `fc-text-large` class on a kit root; only type sizes change, so layouts must wrap, not overflow.
  The settings screen gets the option when it is rebuilt.
- **Contrast fixes.** Every text token was checked on every surface (and the battlefield panel
  over black, grey and white ground). One pair of the brief fails: danger red `#e0513a` reads
  4.45:1 on the panel and 3.98:1 on the selected panel (4.5 needed). It stays for borders, the
  notification dot and icons (3:1 for graphics); text in danger colour uses a new
  `--fc-danger-text: #ea6a55` (4.92:1 on the selected panel). Dim text `#8a939b` passes 4.5:1 on
  every surface, but is still only used from the body size up, as the brief says. Dark text on
  the accent, coin and bone faces is `--fc-ink: #101317` (6.7:1 or better).
- **Our side and theirs.** The brief asks for a bright blue for us and red for them, different in
  lightness too: `--fc-ally: #6cc0ff` (luminance 0.48) against `--fc-enemy: #e0513a` (0.22), a
  1.96:1 ratio between them; the test asks for at least 1.8.
- **Rarity colours.** Common `#9aa3ab`, uncommon `#6fbf5a`, rare `#4f9be8`, epic `#a877e8`,
  legendary `#ff7a2e` (redder than the accent, as asked). `GearArt`'s old frame colours stay
  until the equipment screen is rebuilt on `KitGearCard`.
- **Extra tokens** the brief did not name: `--fc-positive: #9ccb5e` (better in a comparison), the
  coin face's pressed `#cfa640` and pulse `#f3d67f`, a scrim, a pressed wash and a transparent
  `--fc-clear`.
- **Fonts.** Barlow Condensed SemiBold/Bold for titles, labels and big numbers; Barlow Regular,
  Medium and SemiBold for text, from the Google Fonts `ofl/barlow` release (OFL 1.1). All five
  carry every Vietnamese letter (checked with fontTools and by `UiLanguageTests` through
  `Font.HasCharacter`), but none has `▾`, so the dropdown and sort carets are drawn as the new
  `caret` icon, never typed. The licences moved to `Resources/Licenses/` (`OFL-<family>.txt` for
  every bundled family, including the older Be Vietnam Pro, Inter and JetBrains Mono);
  `UiLanguageTests` checks that each font family has one. Be Vietnam Pro stays for the old screens
  until they are rebuilt.
- **Corners and faces.** Square corners and 1 px borders everywhere. The main button is the only
  shape: a 9-sliced white face with the top-left and bottom-right corners cut (`fc_primary.png`,
  `Tools/art/ui_kit.py`), tinted by the accent token.
- **Touch targets larger than faces.** Chips, the plus beside the coins and text-only buttons
  have a smaller visible face (64 px, 44 px) inside a full 82 px target, so rows of chips do not
  turn into slabs.
- **Pressed.** Darker and 2 px down; phones have no hover. The kit's press rules are scoped under
  `.fc-root` so the old menu's `.menu .pressed` (scale 0.96) cannot win inside the menu.
- **Kit icons** carry `fc-icon` instead of the old `icon` class, whose colour rule in Hud.uss
  would otherwise override the kit's. Taps: every element with the `Tap` manipulator now carries
  the class `mb-tap`, so the checks can find the touch targets of old and new screens alike.
- **Danger buttons always ask.** `KitButton.Danger` needs a `KitConfirm` (title, text, confirm
  label); the dialog has Cancel (secondary) and a red confirm. A danger button cannot be built
  without one.
- **Disabled buttons say why.** `Disable(reason)` refuses an empty reason; the reason shows
  under the label ("Thiếu 320 xu", "Cần Sở chỉ huy cấp 3": the brief's "Cần cấp HQ 3" written
  without the English abbreviation).
- **Accent use.** Only the main button, the chosen navigation item and the chosen tab, plus the
  two uses the brief itself names (text-only buttons, a progress bar that is full enough to act).
  A chosen chip is bone with dark text; a chosen dropdown option has a check mark.
- **Upgrade mark** on a vehicle card: a bone square with a dark arrow, shown only when
  `PlayerProfile.CanRankUp` (blueprints and coins both there) and never on a locked card. Locked
  cards dim their art, name and cost to 45 % but keep the unlock line at full contrast.
- **The preview screen** (`KitPreview`): six pages (colour and type, buttons, controls, cards,
  frames and messages, a sample home screen made only of kit parts) with EN/VI and Normal/Large
  switches. `-mb-ui-kit` opens it (`-mb-ui-kit=cards` a page, `-mb-ui-large` in Large text); the
  hidden developer entry is five quick taps on the rank badge of the menu's top bar.
- **Proper names kept in Vietnamese** (checked by `UiLanguageTests` over every Vietnamese text of the game, the kit's, the menus', the guides' and the campaign's; every other unmarked Latin word counts as English): abbreviations and units `CP`, `HQ`, `HP`, `UAV`, `FPV`, `SAM`, `EMP`, `SEAD`, `MOAB`, `APS`, `ATGM`, `IFV`, `MLRS`, `GMLRS`, `EW`, `CIWS`, `FPS`, `mm`, `cm`, `MW`, and the Vietnamese abbreviations `PK` (phòng không), `TT` (trực thăng), `ST` (sát thương), `TL` (tên lửa), `SCH` (sở chỉ huy), `CT` (công trình); real weapons and vehicles the units are modelled on `AC-130`, `Ka-52`, `Grad`, `Smerch`, `TOS`, `Iskander`, `Patriot`, `Tunguska`, `ZU`, `BMPT`, `Terminator`, `Ataka`, `BTR`, `Object`, `Bradley`, `TOW`, `Centauro`, `PzH`, `Merkava`, `Trophy`, `Kornet`, `Iron`, `Cobra`, `Lancet`, `Shahed`, `Hellfire`, `Stinger`, `Apache`, `Little Bird`, `Reaper`, `Maverick`, `Alligator`, `Vikhr`, `Igla`, `JASSM`, `Wolf`, `Griffin`, `Centurion`; the bosses' and branches' code names `Behemoth`, `Inferno`, `Tempest`, `Hive`, `Bastion`, `Spectre`, `Titan`, `Napalm`; the equipment brands `Ironclad`, `Kestrel Dynamics`, `Vulcan Arms`, `Longbow Ordnance`, `Aegis Systems`, `Stormfront Aviation`, `Hivemind Robotics`, `Quartermaster`, `Spectre Electronics`, `Hammerfall Munitions`, `Phoenix Recovery`, `Wolfpack Tactics`, `Bulwark Engineering`; the story's people and faction `Varga`, `Kessler`, `Orlov`, `Aurel`, `Hegemon`; the game `Machine Brigade`; and three words Vietnamese took in whole: `radar`, `drone`, `boss`, with `vonfram` (tungsten) and `pin` (battery), which the syllable check cannot tell from English.
- **Card pictures** (`MachineBrigade.Editor.CardRenders`, batch with graphics:
  `-executeMethod MachineBrigade.Editor.CardRenders.RenderBatch [-mbCardsForce] [-mbCardsOnly id,id]`).
  The cards are every fieldable vehicle (`MatchSettings.AllVehicles`), every elite, boss and base
  structure with a `fort` (towers, their branches, the HQ, the utility modules): 122 cards over 92
  models. Each picture is one model: the high-detail variant (`<id>_hd.glb`, through
  `ModelLibrary.HighDetail`) where it ships, else the model, in the player's colours; elites and
  bosses (never the player's) wear the enemy's. One orthographic camera at pitch 26° and yaw -142°
  (the front to the right, like the battle's three-quarter view but lower), framed on the drawn
  silhouette (renderer bounds were loose on masts and antennas) with a margin; a key, a fill and a
  rim light and a flat ambient, no fog or post-processing; drawn at 1024 px with 4x MSAA and halved
  to 512 px with premultiplied alpha, so the edges are clean on any background. The soft shadow is
  the model's footprint seen from straight above, blurred and projected onto the ground under the
  model on the CPU: it needs no shadow map, so it looks the same for a jeep and a boss.
- **Staying fresh.** `Resources/UI/Cards/manifest.json` records, per card, the model, the source
  file and its SHA-1 (with the render version). `CardRenderWatch` renders a changed model again on
  import in an editor with graphics and logs a warning in batch; `CardRenderTests` fails while any
  card lacks a picture or its model file has changed, so a model change cannot ship with an old
  picture. `CardArt.For(cardId)` gives the picture at run time. The pictures import as UI textures
  (no mipmaps, clamped, 512 px, high-quality compression): 13 MB of PNG in the repository.
- **The class icons stay** the single-colour line icons (`KitBranches.ClassIcon`, the old
  `MenuScreen.ClassIcon`) for small places: chips, the card's corner, the minimap, tags.
- **Screenshots** (`MachineBrigade.Editor.UiShots.KitScreens`, batch with graphics). A runtime panel
  with the game's panel settings (1280 x 720, `BattleHud.MatchFor`'s match) renders into a texture
  through the UI test framework's `RuntimePanelSimulator`, so no scene, camera or play mode is
  needed. The four shapes are 1920 x 1080 (16:9), 2340 x 1080 (19.5:9) with a 96 px notch on the
  left, 2400 x 1080 (20:9) with a 72 px punch hole on the left and the 36 px gesture bar, and
  1440 x 1080 (4:3); the safe area comes from `KitSafeArea.Insets`, the same code the device uses.
  "-full" shots grow the panel to the page's scroll height so a long page can be read at once.
  The screen rebuild adds its screens to `UiShots.Screens`. The render and screenshot runs were
  made with the emulator running; it kept running (the editor uses D3D11, not OpenGL).
- **The UI test framework** (`com.unity.ui.test-framework`, built into 6000.6) is now a package of
  the project: its editor panel lays screens out in EditMode tests without a window, and its
  runtime panel renders the screenshots. Only the test and editor assemblies reference it.
- **The checks.** Strict for the kit (every preview page, both languages, both text sizes, all four
  shapes): no ellipsis, no one-line text running out of its box, no wrapped text squashed shorter
  than its lines, no word broken inside (a hyphen is a fair break), nothing off the screen outside a
  scroll view or clipped at the side of one, every `mb-tap` element at least 80.2 panel px both
  ways, no text under the secondary size, at most one primary (a preview specimen documents a
  state and does not count; the sample screen must have exactly one). `UiThemeTests` checks the
  brief's colours, every text/background pair, the type scale, touch target and spacing, and no
  literal colour or font size in the kit's rules or colour, font size or spacing in its C#;
  `UiLanguageTests` checks the Vietnamese texts for English words (unmarked Latin words that are
  not Vietnamese syllables, minus the names listed above), the fonts' coverage and the licences.
  For the old screens the same checks run and report (they are ignored, with the counts), because
  the rebuild replaces those screens: the five menu tabs at 16:9 have 154 touch targets under
  80 px and 664 texts under 19 px (none cut there); the Hud C# files hold 44 hard-coded colours or
  font sizes and Hud.uss 338 literal colours and 265 literal font sizes; 172 Vietnamese texts still
  hold English words (mostly weapon and model names such as rocket, laser, Lancet, Hellfire,
  Stinger, the English map names, and "coin" 12 times).
- **The layout rules the checks taught.** A text never shrinks in height (`flex-shrink: 0`); in a
  row it may give up width and wrap. A vertical scroll view keeps its content to the viewport's
  width (`Kit.Scroll`). A column beside a scrolling strip needs `flex-basis: 0`, or the strip's
  content widens it. When Large text does not fit a column, the column scrolls and the main
  button stays pinned below it (the sample screen's right column).
- **Left for the screen rebuild** (done, see 10b): sections D (navigation), E (each screen on the kit), G (the
  battle HUD on the kit and the field panel), H (names: map names, "coin", "Skin"), the text-size
  switch on the settings page, map preview pictures for the map dropdown (the kit shows card
  renders as stand-ins), `GearArt` frames in the rarity tokens, and adding each rebuilt screen to
  `UiShots.Screens` and to the strict checks (then removing its old-screen report).


### 10b. Field Command 2.0: the screens (D, E1-E11, G, H)

- **Sheets: a theme's imports lose to every other sheet.** UI Toolkit counts each sheet a theme
  (`Theme.tss`) imports as a *default* sheet, and a default sheet's rules lose to any rule of a
  normal sheet whatever the selectors' specificity or order (found when the base screen's
  overrides never won over Hud.uss, even with three-class selectors and literal values; only
  properties Hud.uss does not set got through). So `Screens.uss` is not in the theme: `BattleHud`
  loads it on the HUD's root after `Hud.uss`, and the screenshot tool and the checks do the same.
  `Tokens.uss` stays in the theme (its `:root` variables must reach every panel); its component
  rules still lose to a Hud.uss rule on the same element, which is why kit icons drop the old
  `icon` class and why screen-specific colours for icons live in Screens.uss.
- **D, navigation.** One top bar (the logo at home, the screen's title elsewhere, the rank badge
  with its XP bar, the coins with their plus, the one settings gear) and a left rail of five items
  (Home, Campaign, Operations, Army, Shop), the chosen one on the selected panel with the 3 px
  accent bar. Army has three tabs (Deck, Equipment, Base). Operations gathers the replays of the big
  operations, the weekly fortress, Boss Rush and the daily challenges. Skirmish and the challenge
  modes are picked in the home screen's mode dropdown. A page opened over the tabs (detail,
  settings, the shop's sheets) hides the tab under it and the rail; Back (and the Android back
  button) closes the top dialog, page or chapter.
- **E1 home.** The live battle behind at 38 %; the campaign card is the whole way in (no separate
  button); today's challenges with the time to the reset and Claim buttons; the deck strip with the
  renders and a short-deck reminder; the mode, battlefield, difficulty and weather as dropdowns
  beside DEPLOY, the one main button.
- **E7 match setup = the home's dropdowns.** The prompt's match setup screen is those four
  dropdowns: each mode with its full name and a one-line description, each battlefield with its
  picture (made from the map data by `Tools/maps/map_thumbs.py`, `Resources/UI/Maps/`), difficulty
  and weather beside them on the same screen. No separate setup page, so there is nothing to scroll
  to. The open mode and map pickers have their own screenshots (`setup-mode`, `setup-map`).
- **E2 campaign.** Nine chapter cards in three acts (picture, progress, stars, the chapter's boss,
  the lock); a chapter's missions (mid-chapter boss, the big operation and side missions marked) with
  the briefing panel: objectives, three stars, Normal / Heroic / Iron, recommended power, rewards with
  the cards they unlock, START. The detail panel is never half empty: the briefing and unlock cards
  fill it.
- **E3 deck.** The 8 + 2 deck with full cards, the overview (count, average CP) and the role cover
  (tank killer, anti-air, artillery, repair, recon; a missing role in the warning colour,
  `DeckRoles`, shared with the defeat hints), the doctrines (the old row of icons, the "sample decks")
  in a dropdown with their names and what each does, branch filter chips with a separate Sort button,
  the collection as vehicle cards.
- **E4 detail.** The same five tabs for every card (Stats, Guide, Weapons, In action, Equipment);
  every stat bar marks its class's average; the equipment's gain and the next level's are shown and
  labelled apart; blueprints have / need with "Enough to level up"; the armour, branch and CP tags under
  the name; the role description is not repeated between Guide and Stats.
- **Towers and structures have the detail page too** (the owner's request). The base screen's
  picked tower, placed slot or utility module has an info button that opens it; the arrows step
  through the base's structures. A tower shows its model, numbers against the towers of its size,
  weapons, In action, guide and rank; its Equipment tab lists its branches (which is chosen, the rank
  they open at) and its three gear slots, changed on the base screen, which the page's button opens
  with the tower picked. A utility module shows its model, health and what it does for the base
  (repair, reload, aircraft, supply, radar, from its data); no weapons or gear. Towers need no unlock.
- **E5 equipment** on gear cards: a slot tapped lists the fitting pieces with the comparison to the
  worn one at once; the slot names follow the design document ("Quang học", not "Lớp phủ").
- **E6 base** on the tokens over BaseScreen's own classes (its tests and drag code read them):
  every control a full touch target; the frames 82 / 88 / 96 px (small, medium, large) and the HQ 88,
  told apart by the size icon in each corner as much as by size (larger frames did not fit the camp
  on a 16:9 screen); the level's slot counts are the legend over the camp, so the toolbar does not
  repeat them; the hint has its own line under the legend.
- **E8 operations.** Each entry has its picture, the rules as they are now (Boss Rush runs one boss
  of each of the ten kinds: "10 trùm liên tiếp", from the data), a clock when it has a deadline, and
  its reward.
- **E9 shop.** Tabs; crates are renders of the crate model tinted by rank
  (`CardRenders.RenderShopArt`), coin packs are pictures (`Tools/art/shop_art.py`); every tile says
  its price and what is in it, a crate's odds a tap away before anything is bought; the "Skin" tab is
  "Ngụy trang".
- **E10 result.** The title is the mission's name or the mode's, never both (the old kicker "Chiến
  dịch 02 / Giữ cứ điểm" is gone); a score says whose is whose ("Ta 0 · Địch 331"); after a defeat
  one or two hints from the battle (`DefeatHints`: the enemy's aircraft and heavy armour against the
  deck's role cover, a fortress without artillery, a short deck, heavy losses without repair) and a
  button that opens the Army tab's deck; CONTINUE after a win (the next mission, or the menu) and PLAY
  AGAIN after a loss are the one main button, back to the menu is secondary; doubling the coins with
  an ad is a Claim button beside the coins. A lost multi-stage mission with a checkpoint plays again
  from the checkpoint (the main button, with a line that says so) or from the start (secondary).
  Pause and the choice between stages are kit dialogs.
- **E11 settings** on kit rows, with Text size (Normal / Large).
- **G battle HUD.** Everything on the field surface with a hairline. Attack / Defend with their full
  names, the one on in the text colour with dark text; Auto buy and Support are the kit's switches
  (no green of their own). The card tray: the 3D render, the full name and the CP of each card; a card
  the points pay for is bright, one they do not is dimmed with the CP missing ("Thiếu 3"); cooldowns
  are a clock sweep with the seconds; the CP box has the points in big figures, the income a second
  and the supply penalty in words ("Quá tiếp tế −29%", or "Tăng viện +15%" for the side behind); a
  tap on it explains. The boss bar has the name, the health in numbers, the phase marks and the
  prompt 9 parts row (icons at touch size; its calls are kept: both `SetBoss` overloads,
  `SetBossParts`, `BossPartTapped`; `SetBossHp` is new). Notices, air-raid warnings, elite arrivals
  and radio chatter share one toast style and one place: the column under the top bar (under the
  boss). Every control is a full 82 px touch target, so the layout is: minimap and its tools (two by
  two) top left, the score top centre, pause top right, the commander's rail down the right, the deck
  (one height, 160 px, 196 in Large text) along the bottom, the selection's orders beside the rail
  above the deck, the hint and the strike prompt above the deck on the left. `BattleHud` can build
  into a given root (the screenshots and the checks lay it out without a scene).
- **H names.** One Vietnamese name for each battlefield, used in every screen, story and briefing:

  | Map | English | Vietnamese |
  | --- | --- | --- |
  | ashfield | Ashfield | Đồng Tro |
  | dunebreak | Dunebreak | Đồi Cát |
  | frostpeak | Frostpeak | Đỉnh Sương Giá |
  | ironport | Ironport | Cảng Thép |
  | redrock | Redrock Canyon | Hẻm Đá Đỏ |
  | whiteout | Whiteout Pass | Đèo Bão Tuyết |
  | greenvale | Greenvale | Lũng Xanh |
  | rustyard | Rust Yard | Bãi Sắt Gỉ |
  | emberridge | Ember Ridge | Sườn Dung Nham |
  | junglepass | Jungle Pass | Đèo Rừng Rậm |
  | skyhold | Skyhold Airbase | Căn Cứ Tầng Mây |
  | metrocity | Metro City | Đô Thành |
  | landingbeach | Landing Beach | Bãi Đổ Bộ |
  | hydrodam | Hydro Dam | Đập Thủy Điện |
  | capital | Capital | Thủ Đô |
  | launchsite | Silver Bug Launch Site | Bãi Phóng Bọ Bạc |
  | saltflat | Salt Flats | Sa Mạc Muối |
  | borderbridge | Border Bridge | Cầu Biên Giới |
  | swamp | Swamp | Đầm Lầy |
  | coralisles | Coral Isles | Quần Đảo San Hô |

  In the Vietnamese texts "coin" is "xu" and "skin" "ngụy trang"; the loanwords are written the
  Vietnamese way (rốc-két, la-de, nhà chứa, pháo điện từ, súng máy nhiều nòng, công-te-nơ,
  mê-ga-oát, boong-ke); the Silver Bug boss is "Bọ Bạc", Nitro Dash "Bứt tốc". The names kept are
  the allow-list line above. `UiLanguageTests` now covers the campaign's texts too and is strict for
  every Vietnamese text.
- **The checks cover every rebuilt screen.** `UiLayoutTests.EveryRebuiltScreenPassesEveryCheck` runs
  each menu screen (`MenuScreen.ScreenNames`, 21 of them with the setup pickers and the tower and
  module pages) and `EveryBattleScreenPassesEveryCheck` each battle screen (the HUD in three modes,
  four results, pause, the stage choice) with the demo profile (`DemoProfile`: rank 12, two and a bit
  chapters won, levelled cards, crates, worn gear, a daily challenge to claim; nothing saved), in
  Vietnamese at the four shapes and in Large text and English at 16:9: no cut or squashed text, every
  tap target 80.2 px, no text under the secondary size, exactly one main button where the screen has
  one (none on the HUD), nothing clipped or off screen. `UiThemeTests` checks Screens.uss for literal
  colours and font sizes like the kit's rules. The old-menu report is gone.
- **Screenshots** of every screen in `Docs/ui-screens/`: `screen-*` (menus), `battle-*` (HUD,
  results, pause, choice), `kit-*` (the kit), at 16:9, 19.5:9 with a notch, 20:9 with a punch hole
  and 4:3, some also in Large text and English (`-mbShotsSet menu|battle|kit`, `-mbShotsOnly`,
  `-mbShotsShape` to take a part).
- **Left for the testing phase** (long checks, not run here): the HUD's frame rate on Low graphics
  against the old HUD on a phone; the safe area on a device with a notch and one with a punch-hole
  camera (the screenshots use the same inset code, but not a real device); a full EditMode run.

## 11A. Test feedback: explosions, flame, laser (2026-09-28)

The owner's play-test found tank-round and bomb blasts too small, the cruise missile's blast
smaller than the ground it wrecks, the flame tank's fire ugly and the Iron Beam's laser weak. All
of it is the view's: no simulation code, damage or radius changed (balance.json untouched).

- **Enlarging without blowing sprites up.** The flipbook sheets are 1024 px with 8 x 8 frames, so a
  frame is 128 px: a fireball simply drawn half as big again goes soft and its quad shows.
  `ExplosionEffect.Play` takes a second factor, `grow`, beside the old `scale`. Fire, smoke and dust
  come in more quads spread wider, each only a little bigger (size x grow^0.65, count x grow^1.4, at
  most 2.6 times, spread over 0.14 x (grow - 1) of their own size), so a big blast is a wider,
  lumpier cluster, and its secondary fireballs roll out further. Sparks, debris, dirt and embers
  come in greater numbers (x grow^1.5) thrown faster (x grow^0.8). The flash, shockwave rings, ground
  light and crater glow are drawn shapes, sharp at any size, so they simply grow. Chunks fly out
  x sqrt(grow). At grow 1 every factor is the old one, bit for bit.
- **Low stays cheap without losing anything.** A recipe's own particles are always emitted in full
  on every tier (explosions are never reduced); only the extra that enlarging adds is scaled by
  tier: High 100 %, Medium 75 %, Low 40 % (`ExplosionEffect.Density`, the pattern the boss-part fires
  already use for Low).
- **The flash and the air ring are pulled 30 m and 20 m towards the camera** (their own copies of the
  Flash and Shockwave materials). An enlarged flash is tens of metres across and the ground sliced
  it along a straight line; they are additive light, drawn over everything anyway.
- **Tank rounds** (armour-piercing shells) had only a spark spray and a dust puff (a Small blast at
  0.6 or 0.9, 13 particles, plus 16 or 36 sparks). They now play their own hit,
  `ExplosionEffect.CreateShellHit`: a white-hot flash, a small hot fireball bursting off the plate and
  a second one rolling out of it, 24 sparks, black smoke, a dust puff, metal flakes, embers, a snap
  of air and a little ground light, and the old spark burst. Enlarged by the tank's class
  (`BlastSizes.TankShell`): light tank and wheeled gun x1.3, main battle tank, tank destroyers,
  twin tank and the 120 mm turrets x1.4, heavy, elite heavy, titan (super-heavy) and the siege tank
  x1.5; any other gun by its damage. The siege tank's 203 mm is a high-explosive shell, so its
  artillery-style blast grows x1.5 instead. The spark burst grows by the same factor (count and
  speed). Kept tight on purpose: a kill's hulk blast after it is still the big one.
- **Bombs** by weight (`BlastSizes.Bomb`): GBU-12 (the small guided bomb), cluster bomblets and
  napalm canisters x1.3, carpet bombing (the heavy bomber's dozen) x1.45, FAB-500, JDAM and the
  strike jet's Mk 84s (airstrike, air raid) x1.5, any other bomb x1.4. The shock ring, the smoke
  column and the scorch mark grow with them. Barrages, SEAD and other strikes are shells or
  missiles and stay as they were.
- **The cruise missile and the MOAB** are drawn as wide as their blast radius: the Ultimate
  recipe's ground shockwave reaches 10.9 m at scale 1 (`BlastSizes.UltimateReach`), so grow is
  radius / 10.9 (1.65 for the cruise missile's 18 m, 2.47 for the MOAB's 27 m), with almost no random
  variation (0.97 to 1.03 instead of 0.85 to 1.2). Before, the cruise missile's ring reached about
  9.8 m of its 18 m and the MOAB's 14.7 m of its 27 m. The fireball cluster now fills about three
  quarters of the radius and the dust skirt rolls out to its edge. The air-launched cruise missile
  and JASSM (Huge, 5 to 6 m splash) already matched and are unchanged.
- **Particles per blast** at High / Low (before: the recipe alone): tank round x1.3 / x1.4 / x1.5
  59 / 69 / 75 on High and 49 / 51 / 54 on Low (its recipe is 42), plus 21 / 50 / 54 sparks on High
  (before: 13 and 16 or 36 sparks); GBU-12 (Large
  x1.3) 245 / 197 (168); FAB, Mk 84 (Huge x1.5) 502 / 366 (276); JDAM (Ultimate x1.5) 675 / 490 (371);
  cruise missile (x1.65) 774 / 530 (371); MOAB (x2.47) 1358 / 765 (371). The contact sheet's log
  prints them (`BlastRig.Budget`).
- **The flame tank.** The stream's balls of fire were the fire sheet's upright flames spun to random
  angles, which read as orange petals, round a thin white rod that read as a laser. Now: the rod is
  a thicker orange stream (0.5 to 0.7 m, spreading x0.45 to x2.2, shorter streaks); the rolling
  fireballs are the blast sheet's burning frames in a napalm-red material (`FxMaterials.FlameBall`),
  small at the nozzle and swelling as they fly, and they fly until they reach the target, then brake
  hard and billow up off it with the wind (`Emitters.Splash`), so the fire splashes onto the target
  instead of flying through it; upright flames lick up the target and the ground by it (never
  spun); an orange heat halo wraps the stream, the ground is lit where it lands, embers fly up; black
  smoke rolls off the far half and the target (10 a second, bigger and blacker than the 7 before).
  Rates: rod 90, balls 42 (as before), smoke 10, heat 24 a second (x Density). A hull's damage fire
  also stays upright now (it was spun the same way).
- **The laser** (`LaserBeams`, a new beam shader `MachineBrigade/Beam`). Before: a 0.09 m bar for
  0.08 s at every 0.1 s shot and a machine-gun flash. Now one held beam per emitter, following its
  turret and its target between shots: a white-hot core (0.3 m), a coloured glow (1.25 m) and a wide
  faint haze (3.4 m) on camera-facing lines, with energy ripples running down them and the width
  pulsing and the light flickering every frame; a 0.22 s charge-up when it starts (a ball of light
  swelling past its size at the emitter, sparks drawn in, the beam growing from a thin pilot line);
  at the hit a white-hot spot in a halo, 50 + 70 x Density sparks a second (one in four a molten drop
  that arcs down and bounces), smoke curling off the burn, the ground lit and a scorch mark every
  0.7 s where it has moved on; a 0.28 s afterglow when it stops (the core goes at once, the glow
  widens and fades, the burn cools, ionised air hangs along the line). Iron Beam and point defence
  are red; the silver bug's saucer laser is green and half as heavy again. Point-defence
  interceptions draw their own beam (mount -1), so they never steal the main one.
- **Contact sheets** (`EffectShots`, batch with graphics): `Impacts` (new: tank rounds, bombs and
  the cruise missile before and after in pairs of rows, the Mk 84 and the MOAB after, with red
  circles of the blast radius), `Lasers` (new: the Iron Beam on a helicopter, the saucer laser into
  the ground), `Flames` and `Blasts` as before.
- **Tests** (EditMode, `BlastSizeTests`): the class and bomb factors, grow 1 is the old blast, no tier
  ever loses a particle of its recipe, enlarged fireballs are more quads rather than only bigger ones,
  the cruise missile's ring reaches its blast radius, the flame stream's layers all emit and its
  flames stand upright, a laser is one beam while it fires and goes after its afterglow.
- **Left for the testing phase:** frame time on a Low-tier phone with several cruise missiles or a
  carpet-bombing run on screen (the fill of the enlarged smoke is the thing to watch; the counts above
  are within the old per-tier caps' growth); the first laser's pipeline build (line renderers are not
  in `WarmUpPipelines`, which only draws particle systems).

## 11B. Test feedback: muzzles, projectile flight, projectile sizes (2026-09-28)

- **Why rounds started off the barrel (the real cause).** A shot's effects were started while
  the simulation's events were dispatched, inside the step loop in `Update`. At that moment the
  vehicle transforms were still last frame's: drawn from the previous pair of snapshots, a step
  behind the turret, hull and flight pose the frame was about to show. The round, flash and trail
  were placed there, and the vehicle was then drawn somewhere else. The gap is however far the
  vehicle moved, turned or climbed in between. It is not tied to one heading in the world. It
  shows most when the barrel lies across the screen and hides when the barrel points along the
  camera's view, so it looked right at some headings and wrong at others. Measured (MuzzleTests,
  30 fps, turret swinging onto a target 70 degrees off the hull): 0.10-0.24 m on tanks, IFVs,
  artillery and turrets, 0.06-0.07 m on the SAM and MLRS, 2.4 m on a helicopter and 4.7 m on an
  attack jet. Now 0.000 m for every vehicle and heading tested.
- **The fix.** `EffectsDirector.Consume` queues `WeaponFired` and `WeaponCharging` with their
  shooter's view. `EffectsDirector.LaunchShots(views)` starts them right after
  `ViewRegistry.Render`: in `MatchRunner.LateUpdate` and in `FiringRange.Tick` (the detail page's
  in-action clip). Every round, flash and trail then leaves from the muzzle node as it is drawn in
  that frame: hull yaw, turret yaw, gun elevation (laid for the shot), recoil, flight pitch and
  bank, the launch point in use. This covers aircraft, helicopters, launchers, racks, artillery
  and towers alike. The shooter is held when it is queued, so a vehicle that fires and dies in
  one step still fires from its barrel. The sim is unchanged: the sim's spawn point was never
  used for drawing, and the sim's origin (hull centre plus radius) still only sets travel time
  and walls.
- **Recoil.** With shots started after the draw, the barrel's kick begins on the frame after the
  round leaves. Before, the barrel was drawn fully recoiled (0.12-0.45 m back) on the round's
  first frame, with the round and flash ahead of it.
- **Tracer streaks.** A streak was centred on its round, so on its first frame half its length
  (0.4-1.8 m) lay behind the muzzle, over the turret. The round is now the head of the streak.
  On the first frame the streak reaches 40 % of its length out of the barrel's tip, then trails
  its full length behind the round and ends on the target as it lands. Laser beams keep one
  centred bar (`TracerPool.Beam`).
- **Artillery in flight.** The shell model and its smoke puffs were already on one curve. What
  did not match was the start: the aim point is scattered (spread, and the first rounds of a
  bracket 1.6x wider), so the plain arc left the barrel up to about 10 degrees sideways, away from
  its blast. Lobbed shells, mortar bombs and artillery rockets now fly one quadratic curve from the
  drawn muzzle, through a point half the ground distance out along the laid barrel, onto the
  landing point (`WeaponEffects.Bend`, `ProjectilePool.Launch(control:)`). That point gives the
  same peak as the old arc for the barrel's angle. The model, its trail and its start agree along
  the whole arc, and the flight time is still the simulation's. The ballistic missile keeps its
  own high arc. Guided missiles keep homing.
- **Sizes (drawn only, times the weapon's `projectileScale` in balance.json; speeds are the
  data's).** Drones 2x: the FPV carrier's and drone hangar's FPVs, Lancets, Shaheds, and the drone
  mothership's FPVs too. At 0.56 m, dropped from an airship 26 m up, they could not be seen.
  Rockets 1.15x (Grad, GMLRS, Hydra, S-8, TOS, heavy and 107 mm). Ground-launched ATGMs and
  MANPADS 1.1x (TOW, Kornet, Ataka, Stinger, Igla). Air-launched, surface-to-air, air-to-air and
  cruise missiles 1.2x (Hellfire, Maverick, JASSM, cruise missile, SHORAD dart, Buk, Patriot,
  AIM-9, AIM-120, R-60). AAMs are sorted with the SAMs as large radar or IR missiles.
  `WeaponEffects.SizeOf` holds the table. The mothership's summoned strike drones are vehicles and
  keep their own size.
- **Tools.** `MuzzleTests` (EditMode): rounds start at the drawn barrel tip at headings
  0/90/180/270 with the turret swung onto a target; streak ends; the bend leaves along the barrel;
  the size table. `MachineBrigade.Editor.MuzzleShots.Run -mbShotsOut <folder>` (batch mode with
  graphics): headings.png shows each shooter at four headings on the frame its first round leaves,
  and flights.png shows artillery rounds and trails close up at four moments of flight.
  `VehicleView.LastMuzzleNode/LastMuzzleLocal` and `WeaponEffects.Launched` exist for them.
- **Debris rotation (found by the play smoke run).** `DebrisPool` multiplied each piece's spin
  into its rotation every frame without renormalising it. Over a long battle the quaternion
  drifted off unit length and `Matrix4x4.TRS` asserted: 47 errors in 40 s of Conquest. It is
  now normalised each step, a one-line change. PlaySmoke (menu 15 s, Conquest 40 s, Siege 40 s):
  0 errors.
- **Left for the testing phase.** A play-mode check on the device at 30 fps with moving
  columns. The measurement above steps a real sim and views, but EditMode time does not advance,
  so the barrel's kick and the hull smoothing are frozen there. Also left: the aircraft stores'
  fallback points, and the strike effects' cruise missiles (StrikeEffects, another lane), which
  keep their sizes.

## 11C. Test feedback: weapon targets, missile speed, fire rhythm (2026-09-28)

The owner's play-test found three things: the armoured car's main gun shooting at aircraft, every
missile flying too fast (seen on the attack helicopter's Hellfire), and fighter jets' cannons firing
a short blip and a long wait instead of a sustained stream.

### A. What a weapon may shoot at

The owner's rule (corrected during the work): **a dedicated anti-air vehicle or tower keeps its
main weapon on aircraft; every other vehicle's main gun fights the ground. Machine guns (the coax,
roof and hull guns: "the rifle") may still engage low aircraft and helicopters.** A tank with
nothing on the ground already swings its turret after an aircraft for the coaxial gun (round 6);
the armoured car, the IFV and the BMPT now do the same.

| Weapon | Carried by | Was | Now | Why |
|---|---|---|---|---|
| `autocannon_25` | armoured car (main), guard tower "nest" branch (main) | All | Ground | The owner's report; a non-AA main gun. The nest is a guard tower, not an AA tower: the AA towers cover the air. |
| `autocannon_30` | IFV and elite APC (main), heavy tanks (coax) | All | Ground | Same rule (the owner named the IFV). The heavy tank's coax only ever fired at the main gun's target. |
| `twin_30_bmpt` | BMPT (main) | All | Ground | Same rule (named by the owner). |
| `vikhr` | Ka-52 (main) | All | Ground | A non-AA main weapon; the Ka-52 keeps its Igla-V for aircraft. |
| `boss_missiles` | Behemoth, Mobile Fortress, Mega Gunship | All | Ground | An ATGM (Kornet model): ATGMs fight the ground. Each boss keeps its flak or machine guns for aircraft. |

Kept on purpose (checked): every flak gun and SAM (AA vehicles, AA towers, the C-RAM, the Iron
Beam, the heavy AA, the ZU-23 technical, the elite AA); machine guns everywhere (a jeep's, the
support vehicles' only guns, the helicopters' guns and door guns, the bunkers); the fighter's
cannon (the fighter is the anti-air aircraft). Four kept with a reason: `kornet_multi` (the ATGM
tower's "multi" branch exists to reach aircraft; without it the branch would be only its 0.8x
penalty on armour), `coilgun` (a boss gun, not a main gun: the Tempest's only air defence),
`autocannon_40` (the Bastion boss's corner turrets, its only air defence) and `hover_ciws` (a
close-in weapon system is an anti-air gun). Tank guns, howitzers, mortars, rocket artillery,
ATGMs, bombs and rockets were already ground only.

The view: a turreted vehicle's main barrel elevates to its aircraft (8-78 degrees, `VehicleView.
Elevate`, from the sim's aim height) and an anti-air main weapon rests at 18 degrees. A secondary
launcher (the AA vehicle's and the heavy AA's SAM rack) does not pitch: its missile climbs from the
rack. That is the muzzle and flight work's (not changed here).

### B. Missile speed

Every guided missile about a third slower (30-36 %); direct-fire rockets a fifth (unguided: slower
rounds miss a moving target more, so they lose less). Artillery rockets, drones and the ballistic
missile were already slow and stay. Flight time at the weapon's full range:

| Missile | Weapons | Speed before → after (m/s) | Flight at full range |
|---|---|---|---|
| ATGM | `atgm`, `atgm_heavy`, `ataka`, `atgm_post`, `boss_missiles` | 36 → 24 (-33 %) | 34 m: 0.94 → 1.42 s; 45 m: 1.25 → 1.88 s |
| Kornet | `kornet_twin` (+ `kornet_top`, `kornet_multi`) | 38 → 25 (-34 %) | 50 m: 1.32 → 2.0 s |
| Hellfire class | `heli_atgm`, `hellfire_volley`, `drone_missile`, `griffin`, `recon_missile` | 45 → 30 (-33 %) | 34 m: 0.76 → 1.13 s; 50 m: 1.1 → 1.67 s |
| Vikhr | `vikhr` | 50 → 34 (-32 %) | 55 m: 1.1 → 1.62 s |
| Air-to-ground | `maverick`, `kh29` | 50 → 32 (-36 %) | 40 m: 0.8 → 1.25 s |
| MANPADS / SHORAD | `sam`, `stinger_atas`, `igla_v` | 60 → 40 (-33 %) | 44 m: 0.73 → 1.1 s |
| Medium / long SAM | `sam_long`, `sam_battery` (+ `sam_pac3`, `sam_battery_lrr`) | 72 → 46 (-36 %) | 55 m: 0.76 → 1.2 s; 100 m: 1.39 → 2.17 s |
| S-400 48N6 | `sam_48n6` | 95 → 62 (-35 %) | 95 m: 1.0 → 1.53 s |
| Air-to-air | `air_to_air`, `wvr_aam`, `r60`, `aim9` | 74 → 48 (-35 %) | 60 m: 0.81 → 1.25 s |
| Cruise / stand-off | `air_cruise_missile`, `jassm` | 30 → 20 (-33 %) | 110 m: 3.7 → 5.5 s |
| Direct-fire rockets | `heli_rockets`, `gunship_rockets`, `scout_rockets`, `jet_rockets`, `s8_pods`, `hind_rockets` | 75 → 60 (-20 %) | 34 m: 0.45 → 0.57 s |

- **Still hitting moving targets:** a guided round lands on its target's position at impact
  (`DamageSystem.ResolveImpact`), whatever its speed; `WeaponTests.GuidedMissileHitsATargetThatDrivesAway` passes.
- **Flares:** a flare burns 1.5-3 s, and a slow missile's flight can now outlast it, so a missile
  is decoyed by flares out at impact *or put out while it flew* (`Projectile.LaunchedAt`).
- **APS:** it intercepts at impact, from its charges then; nothing depends on the speed (`ApsTests` passes).
- **Flight time against cooldown:** no weapon's flight at full range reaches its cooldown (the
  longest: the cruise missile, 5.5 s of 14 s; the stand-off JASSM 4.5 s of 10 s).
- **Speed-dependent logic:** only the fire-control computer's lead (`GearSystem.Lead`), which reads
  the speed, and the overkill check (more rounds in the air at once) use it. No range assumes a speed.
- **The launch:** the view flies a missile slowly off the rail and speeding up over its whole
  flight (`ProjectilePool`, boost 0.55), arriving on the sim's time: a 40-60 m Hellfire now takes
  1.3-2 s, starting at about 14 m/s and ending at 46. A distinct boost-then-cruise curve would be
  the flight view's change.

### C. Fire rhythm

**New: magazines.** Weapon data `clip` (rounds) and `clipReload` (seconds): the rounds are fired one
at a time, `cooldown` apart, at the target the mount bears on (they track it; a salvo keeps its
first aim point), and stop when it stops bearing; an empty magazine takes `clipReload` (±10 %) to
change, and a lull that long tops a part-used one up. The cooldown keeps up to one step of credit,
so a gun faster than the 20 Hz step fires two rounds in some steps; the view draws the rounds of one
step one cadence apart (`WeaponDef.RoundGap`). Backwards compatible: no `clip`, no change. A
magazine needs a single-round weapon (`burst` 1), checked at load. `roundWeight` sets how heavy a
round looks and sounds (tracer thickness, muzzle flash, the autocannon/MG report) when the damage
is not the calibre's: a gun made faster with lighter rounds still looks and sounds as before.
Card stats (`UnitStats`), the detail page's weapon line, the proc coefficient and a boss part's
firepower count a magazine over its change.

**The round-6 rules, kept:** no two weapons of a vehicle fire in the same instant
(`WeaponTurnTests`, all vehicles); the machine gun pauses round every heavy round and salvo; guns
other than machine guns and AA keep their 30 % slower, harder round-6 cadence (tank guns, cannons,
howitzers, rockets: unchanged); AA guns keep their 8-16-round bursts (flak, ZU-23, C-RAM unchanged).
A magazine gun counts as a gun in the rhythm: it takes turns with machine guns and gives way to a
heavy weapon lined up. **Where the owner's request wins:** the rapid-fire guns (jet cannons,
autocannons, machine guns, gatlings, the gunships' guns) fire faster than round 6's slower
cadence; and a ground vehicle's or a helicopter's main magazine gun, once it has opened up, keeps
its stream until the magazine is empty or the target stops bearing (the other mounts wait for the
change; a heavy weapon lined up still goes first when the stream would start). An aeroplane's
cannon takes turns like a machine gun: a pass lasts under a second, and its rockets and bombs must
still get their turn in it.

The jets' cannons fire a stream (20-25 rounds a second) for as long as the target is on the nose,
from a 3.5-3.6 s magazine, then a 1 s change; the magazine carries over between passes. **Limit:**
on a strafing pass the target is on the nose and in reach for under a second (30-32 m of reach at
27-32 m/s, and the pass pulls through at 9 m), so a pass shows a 1-1.4 s stream, not 3-4 s (before:
a 0.45-0.55 s burst). The whole magazine shows only where the target stays on the nose (the VTOL
fighter hovering, a long head-on approach). A longer stream per pass needs a longer cannon reach or
a slower, longer attack run (movement and balance, not the weapon data): left for the owner.
An attack jet's cannon was tried with the right of way too (its stream kept once started): its
bombs then never dropped, and letting them cut in left the cannon fewer rounds, so it takes turns.
Per-round damage was set from the measurement so each pass does what the old burst did.

The mega gunship boss keeps its guns' old cadence (`boss_heli_gun`, `boss_minigun`): a boss's
mounts take turns one step at a time, and a gun firing every step would starve the ones after it.

DPS, measured (`FireRhythmMeasure`, explicit: each shooter against a dummy for 60 s, strafing runs,
the rhythm and the damage tables included; the target in brackets):

| Shooter (target) | Mount | Rhythm before | Rhythm after | DPS before | DPS after | Rounds/60 s | Longest stream |
|---|---|---|---|---|---|---|---|
| attack_jet (main_battle_tank) | `jet_cannon` | 10 x 52 @0.05, 3.57 s | stream 20/s x 70 (3.5 s), 1 s change, 64 | 101.0 | 99.9 | 130 → 80 | 0.45 → 1.05 s |
| tank_buster (main_battle_tank) | `gau_gatling` | 14 x 62 @0.04, 3.14 s | stream 25/s x 90 (3.6 s), 1 s change, 44 | 190.1 | 189.8 | 168 → 218 | 0.55 → 1.40 s |
| fighter_jet (attack_helicopter) | `fighter_cannon` | 8 x 30 @0.05, 1.2 s | stream 20/s x 70 (3.5 s), 1 s change, 22 | 54.0 | 54.5 | 72 → 99 | 0.35 → 0.95 s |
| gunship_heli (ifv) | `gsh30k` | 6 x 41 @0.06, 2.14 s | stream 12.5/s x 30 (2.4 s), 1.2 s, 15.8 | 73.8 | 73.7 | 144 → 373 | 0.30 → 2.60 s |
| attack_helicopter (ifv) | `heli_gun` | MG 0.22 s, 16 | MG 0.12 s, 12 | 60.3 | 57.8 | 133 → 170 | 2.25 → 1.35 s |
| scout_heli (armored_car) | `minigun` | MG 0.07 s, 7 | MG 0.045 s (20/s), 5.6 | 47.6 | 48.9 | 241 → 308 | 1.15 → 0.70 s |
| sky_gunship (ifv) | `gunship_25mm` | MG 0.12 s, 19 | stream 16.7/s x 50 (3 s), 1.2 s, 12.4 | 45.0 | 45.2 | 67 → 174 | 0.45 → 0.50 s |
| armored_car (armored_car) | `autocannon_25` | 3 x 22 @0.1, 1.29 s | stream 5/s x 12 (2.2 s), 1.6 s, 15.5 | 44.0 | 46.5 | 121 → 180 | 0.20 → 2.25 s |
| armored_car (armored_car) | `mg_coax` | MG 0.16 s, 6 | MG 0.1 s, 4.8 | 17.3 | 14.7 | 102 → 108 | 0.50 → 1.30 s |
| armored_car (attack_helicopter) | `autocannon_25` | 3 x 22 @0.1, 1.29 s | stream 5/s x 12 (2.2 s), 1.6 s, 15.5 | 13.2 | 0.0 | 121 → 0 | 0.20 → 0.00 s |
| armored_car (attack_helicopter) | `mg_coax` | MG 0.16 s, 6 | MG 0.1 s, 4.8 | 5.2 | 10.0 | 102 → 244 | 0.50 → 1.15 s |
| ifv (ifv) | `autocannon_30` | 3 x 32 @0.12, 1.57 s | stream 5/s x 10 (1.8 s), 1.8 s, 22.4 | 52.8 | 59.7 | 99 → 160 | 0.25 → 1.90 s |
| ifv (ifv) | `mg_coax` | MG 0.16 s, 6 | MG 0.1 s, 4.8 | 19.6 | 12.5 | 115 → 92 | 0.80 → 1.40 s |
| ifv (attack_helicopter) | `autocannon_30` | 3 x 32 @0.12, 1.57 s | stream 5/s x 10 (1.8 s), 1.8 s, 22.4 | 15.8 | 0.0 | 99 → 0 | 0.25 → 0.00 s |
| ifv (attack_helicopter) | `mg_coax` | MG 0.16 s, 6 | MG 0.1 s, 4.8 | 6.9 | 10.0 | 136 → 244 | 0.80 → 1.15 s |
| bmpt (ifv) | `twin_30_bmpt` | 4 x 30 @0.08, 1.29 s | stream 6.7/s x 16 (2.25 s), 1.6 s, 21.3 | 74.0 | 84.5 | 148 → 238 | 0.25 → 2.35 s |
| bmpt (ifv) | `mg_coax` | MG 0.16 s, 6 | MG 0.1 s, 4.8 | 15.3 | 9.5 | 90 → 70 | 0.50 → 0.95 s |
| main_battle_tank (ifv) | `mg_coax` | MG 0.16 s, 6 | MG 0.1 s, 4.8 | 19.2 | 25.2 | 113 → 185 | 1.60 → 1.30 s |
| main_battle_tank (ifv) | `hmg_roof` | MG 0.2 s, 11 | MG 0.13 s, 8.8 | 34.0 | 28.7 | 110 → 115 | 2.05 → 1.35 s |
| scout_jeep (armored_car) | `mg_jeep` | MG 0.18 s, 9 | MG 0.12 s, 7.7 | 49.0 | 48.9 | 192 → 224 | 1.80 → 1.35 s |

| Shooter (target) | All mounts, DPS before → after |
|---|---|
| attack_jet (main_battle_tank) | 158 → 153 (-3 %) |
| tank_buster (main_battle_tank) | 273 → 273 (-0 %) |
| fighter_jet (attack_helicopter) | 159 → 153 (-4 %) |
| gunship_heli (ifv) | 159 → 152 (-5 %) |
| attack_helicopter (ifv) | 133 → 124 (-7 %) |
| heavy_attack_heli (ifv) | 52 → 52 (+0 %) |
| scout_heli (armored_car) | 84 → 84 (+1 %) |
| sky_gunship (ifv) | 325 → 325 (+0 %) |
| armored_car (armored_car) | 61 → 61 (-0 %) |
| armored_car (attack_helicopter) | 18 → 10 (-46 %) |
| ifv (ifv) | 84 → 84 (-0 %) |
| ifv (attack_helicopter) | 23 → 10 (-56 %) |
| bmpt (ifv) | 122 → 122 (-0 %) |
| main_battle_tank (ifv) | 88 → 86 (-2 %) |
| scout_jeep (armored_car) | 49 → 49 (-0 %) |
| heavy_aa (attack_helicopter) | 376 → 376 (+0 %) |
| aa_vehicle (attack_helicopter) | 166 → 160 (-3 %) |
| zu23_technical (attack_helicopter) | 195 → 195 (+0 %) |

**Also fixed:** `WeaponDef.Tuned` (the per-vehicle copy equipment makes) dropped the weapon's
charge, bonuses, round model and scale; it keeps them now.

### D. Left for the testing phase

- Campaign winnability (the usual seeds) and the boss missions with the Ka-52, the jets and the
  IFVs: the IFV and BMPT no longer shoot helicopters with their main guns, and bosses no longer
  shoot aircraft with their Kornets.
- DPS parity in real battles (the measurement is one shooter against one dummy): attack-jet and
  A-10 time-to-kill on tanks; the fighter against helicopters (hovering, it now streams its cannon).
- Missile hit rates with flares and APS in battle; SAMs against jets at long range.
- Performance on the device with faster machine guns and streams (more `WeaponFired` events and
  tracers a second).
- Equipment that fits "salvo" weapons (`SalvoInterval`) no longer fits the jets' and autocannons'
  magazines (they have no salvo); the fire-rate equipment speeds up a magazine's cadence.

## 11D. Test feedback: menu loading, music, in-action clips (2026-09-28)

Play-test findings: the first open of the game stuttered into the menu; several music tracks
seemed to play at once; the menu's background battle was heard (fire and explosions); the detail
page's In action clip (Xem bắn) showed only shooting, not the vehicle's special ability (the EW
jammer was the example).

- **How it was measured.** `MachineBrigade.Editor.StartupProbe` plays the menu from a cold start in
  batch mode with the profiler recording and reads every frame back (`ProfilerDriver`
  hierarchy views): the frame's time, the game's share of it (the frame less the editor's own
  `EditorLoop`, which throttles batch mode to 30-60 fps), the heaviest markers of each slow
  frame, when the curtain lifted, and once a second every audio source playing. It can also open
  In action ranges and log their simulation events. Runs are `-nographics`: the preview
  camera's render texture crashed the null device (a native crash in `ScriptableRenderContext.Submit`),
  so the probe drives the range with a camera that never draws. GPU work (shader and pipeline
  creation) is therefore not in these numbers, and editor numbers are not phone numbers.
- **The stutter's cause.** On the first open there was no curtain. `Curtain.Open` at the end of
  `MatchRunner.Start` was what created it (`Ensure(1f)`), and every `Curtain.Progress` before it
  did nothing because no curtain existed yet. So the build ran on screen: a 3.4 s first frame
  (catalogue, map, world), then 14 frames of 100-450 ms each (models, the prewarm loop, effects),
  then a 1041 ms frame (audio, weather, the interface's UI Toolkit panels: `UIElements.UpdateStyle`
  125 ms, `UIDocument.OnEnable`) and a 146 ms first `Update`, all drawn half-built, and then a
  black curtain popped up and faded away. Scene loads from inside the game were fine because
  `Curtain.Close` had put the curtain up first.
- **The fix.** `Curtain.Cover` puts the curtain up black at once (no fade, the bar at zero), and
  `MatchRunner.Start` calls it first, then yields one frame so the curtain is drawn before any
  work. Two more yields split the old 3.4 s first step (after the catalogue, after the world), so
  the bar moves. The rest of the build already yielded. Only the curtain's timing and loading
  logic changed, not its look.
- **The effect sounds decoded on first play.** The recorded effects import as Decompress On Load
  without preload or background loading, so each clip was decoded on the main thread the first
  time it sounded: a stall in the first seconds of a battle or of an In action range.
  `AudioDirector.Preload` now calls `LoadAudioData` on every clip while the curtain is down
  (about 90 ms in the editor, `SoundManager.LoadFMODSound`). The import settings are unchanged.
- **Measured (editor, batch mode, profiler).** Before: frames 0-15 of the first open, all on
  screen, took 3216, 433, 169, 133, 127, 110, 140, 110, 145, 186, 294, 151, 82, 92, ~1000 and
  119 ms of game time. After: the same work (0.4 s, then 2.8 s for the map and world, then 12
  frames of 85-330 ms, a 507 ms frame and a 116 ms first update) is all behind the curtain. After
  the curtain lifts, the first 5 s of the menu: game time p50 3.2-3.4 ms, p95 4.6-7.6 ms, max
  8.8-24.5 ms over two runs, no frame over 33 ms; over 34 s of menu with two In action ranges:
  p99 9.7 ms, max 24.6 ms. Opening an In action range builds its little world in one frame (up
  to about 60 ms in the editor, 5 frames over 33 ms across twelve ranges): left as it is, since it
  follows a tap.
- **Left for the device test phase:** frame times of the first seconds on a real phone
  (`-mb-perf` logs hitches with a breakdown), and GPU pipeline warm-up. `EffectsDirector.Prewarm`
  already draws every effect layer once behind the curtain; the preview camera's first In
  action frame compiled several shader variants in the editor (438 ms, `Shader.EditorCompileVariant`),
  which on a phone would be pipeline creation. A `GraphicsStateCollection` warm-up is the tool if
  the device shows it.
- **One music player.** `MusicDirector` is now one player for the whole session
  (`MusicDirector.Play(mood, seed)`), kept across scene loads (`DontDestroyOnLoad`) and driven by its
  own host in real time. The same track carries on (a rebuilt menu keeps its theme instead of
  restarting it); a new one cross-fades over 2 s on the second deck; a deck still fading is cut
  before a third track starts, so at most two tracks overlap, only during a cross-fade. A new track
  stops the last result stinger. With domain reload off, the static is reset at
  `SubsystemRegistration` and any stray player is destroyed when a new one is made.
  `Dispose` is kept as a no-op, so `MatchRunner`'s clean-up is untouched.
- **The audit.** Every sound in the game goes through `AudioDirector` (effects, loops, radio
  chimes, sirens, thunder, clicks) or `MusicDirector` (tracks and stingers). No screen (shop,
  detail, story panels, results, bosses) plays audio of its own; the detail page had no music of
  its own either. What was heard as a detail track was the In action range's guns on top of the
  menu theme and the lobby battle. Boss fights switch the music to the boss track; the old war-drum
  loop (`AudioDirector.BossMusic`) is never switched on.
- **The menu is silent but for wind.** The lobby's `AudioDirector` (no player side) now ignores
  the lobby battle's events and keeps its rotor, jet and fire loops at zero; only the wind plays,
  at 45 % of a battle's (0.07). Wind was chosen over nothing so the menu does not feel dead, and
  it cannot be mistaken for combat.
- **The In action range keeps its sounds, quieter.** `AudioDirector.ConsumeRange` plays the
  range's shots and blasts at 0.6 of a battle's level (delayed and scheduled sounds carry the same
  gain), and `UnitPreview` ducks the music to 45 % while the range plays, easing back when it
  closes. The range is a demonstration, so its weapons are heard, but it should not drown the menu.
- **Abilities in the In action clips.** `FiringRange.Abilities.cs` gives each vehicle or support with
  a special ability a scene of its own, chosen from its definition (not its id), with the real
  simulation doing the work. It adds friendly vehicles to repair, fortify or lead, and enemy
  sparring partners: `Vehicle.Sparring` (`SimWorld.MakeSparring`) is a unit that moves and fires
  as usual but, like a range dummy, cannot be destroyed. A scene can also add dragon's teeth for a
  breacher. A ring on the ground (`EffectsDirector.AbilityRing`, the existing shockwave ring)
  marks an aura. The scenes are:
  jammer (enemy ATGMs and a Lancet at its friends, out of their machine guns' reach, lose their
  lock), interceptor (rockets and missiles at its friends, burnt down by the laser), repair or
  rearm aura (two wounded friends, knocked down again once healed), fortify (a battered friendly
  guard tower), command aura (two light tanks under it), counter-battery radar (an enemy mortar
  shells its side, gets pinged, and a friendly mortar answers), breacher (a row of dragon's teeth
  ploughed, then another), flares (an enemy SAM vehicle at the aircraft), smoke when under fire
  (an armoured car opens up on it), recon drone (spotting pings on what it sees), EMP (the targets
  are real tanks shelling two friends, silenced by the blast), shield dome (enemy tanks fire on the
  friends under it). The mine layer, car bomb, remote mines and drone carriers already showed
  theirs. The smoke generator did not (its skill waits for an enemy within 11 m and the targets
  stand 21 m off), so it has the smoke scene too.
- **Checked headless** (`StartupProbe -mbProbeRange`, event counts per clip): jammer, 5 guided
  shots at its friends and none hit (`RangeSceneTests` checks the same with and without the
  jammer); interceptor, 4 interceptions; engineer, 52 repairs; sapper, 26; counter-battery, 3
  guns revealed and 3 rounds back; breacher, 8 obstacles ploughed; attack helicopter, 2 flare
  salvos; IFV and smoke generator, 2 smoke screens each; EMP and shield dome, the strike lands on
  the attackers or the friends; mine layer, 3 mines and one set off. With graphics
  (`-mbProbeShots`, the range camera rendered twice a second) the jammer, interceptor, command,
  breacher, counter-battery and EMP clips were looked at frame by frame. The jammer's attackers
  stood outside the frame and its ring pulsed too rarely to be seen, so its view was widened and
  it pulses every second; the breacher's row of teeth now waits 3 s before going up again,
  because each fall uses the big "defence falls" blast and eight in 14 s filled the frame.
- **Seen but not changed (other lanes):** the command vehicle's own machine gun never fired on
  the range (attack order on a target, not stunned, not moving), while the counter-battery radar
  with the same weapon and mount did; its clip shows the aura and the tanks it leads. A long menu
  (over a minute of lobby battle) logs thousands of "Quaternion To Matrix conversion failed"
  asserts from `DebrisPool.Draw`: the debris rotations drift off unit length as they spin (fixed
  meanwhile on lead/integration by 8e7d43c, which renormalises them each step). Dragon's teeth ploughed by a breacher go up in the defence-falls
  fireball; a concrete-crumble effect would suit them better.
- **Passive abilities with no scene:** stealth (the stealth bomber gets the flares scene), the
  turtle tank's mine and drone armour, the command vehicle's forward drop point, the artillery's
  shoot-and-scoot (it already relocates on the range after three rounds).

## 12E. Test feedback 2: the in-action preview (2026-09-29)

Play-test findings: on the detail page the In action clip (Xem bắn) was too small to watch, and the
previous / next buttons covered a third of it. Two requests came with it: tower information was
hard to find (only the base screen's info button led to it), and Boss Rush was missing from the
home screen's mode picker.

- **The layout: a theatre on the In action tab.** The other four tabs keep their two columns. On
  In action the page turns into a theatre: the preview leaves the left column and fills the whole
  space under the tabs, and a narrower side column (`--fc-detail-side`, 440 px) holds the name
  with the arrows, the firing note and the weapon rows, the deck toggle, and the dock (blueprints
  over the level-up button, which stays the page's one main button). The tags and counters are
  hidden there (every other tab shows them). The same elements move between the columns
  (`ArrangeDetail`), so the page's refresh fills both layouts. Towers and modules (the same page)
  get it too. Considered and turned down: a preview across the page's full height (the tab row
  needs about 700 px at Large text, which leaves a tall, narrow box that cuts the clips' sides on
  4:3), and a full-width preview over the dock (the dock's 120 px would come out of the height,
  and the height sets how big the vehicle looks).
- **Sizes (panel pixels at the 1280 x 720 reference).** Before: 480 x 300 on every shape, with
  82 px arrow faces over it on both sides. The theatre: about 808 x 517 at 16:9, 1024 x 517 at
  19.5:9 with the notch, 1080 x 493 at 20:9 with the punch hole and gesture bar, and 808 x 757 on
  a 4:3 tablet. That is 2.9 times the area at 16:9. The turntable box on the other tabs stays
  480 x 300 (`--fc-detail-stage`).
- **The arrows.** They are the kit's plain icon buttons: a 44 px face inside the full 82 px
  touch target, beside the name (previous is the arrow turned round, instead of the old U-turn
  icon), off the picture in both layouts. They keep their width next to a long name at Large text
  (`flex-shrink: 0`; the strict check caught 77 px at first).
- **The render texture follows its box.** `UnitPreview.Fit` sizes it to the stage's size on
  screen when the stage's geometry changes: the box's shape, and its pixels up to a longest side
  of 1600 and about 1280 x 720 (921,600) pixels. It uses 4x MSAA up to 520,000 pixels and 2x
  above. On a 1080p 16:9 phone the theatre gets about 1200 x 768 at 2x (was 640 x 480 at 4x,
  stretched and cropped into the box). A 2400 x 1080 phone gets about 1420 x 650, and a 1440 x 1080
  tablet 909 x 853. The turntable box gets 720 x 450 at 4x. Rendering it at 2x keeps the samples
  near the old texture's (about 1.8 M against 1.2 M) and it runs only while the tab is open. The
  development range capture (`-mb-range-hd`) pins its own size.
- **What the clips show is unchanged.** The old texture was 4:3, and the page cropped it to fill
  the box. The camera now renders that crop directly (`UnitPreview.Project`, a projection matrix
  with the field of view scaled by `max(0.8, (4/3) / aspect)`). The range and the turntable still
  frame the vehicle by the camera's field of view, so `FiringRange` is not touched. At the 1.6 box
  the view is exactly the old one, and the turntable looks as it did. A wider box sees across as
  much as the 4:3 frame and at most 20 % less top to bottom (the old page cut 17 %). A taller box
  (4:3 tablet) sees the frame's full width and more above and below. So the vehicle is about 1.7
  times as big on screen on every shape.
- **Towers beside the vehicles.** The Army tab has a fourth tab, **Tháp & mô-đun** (Towers &
  modules), between Deck and Equipment. It lists the base's towers by size and then its utility
  modules, as the same cards as vehicles: render, rank, size icon in the corner, the upgrade mark
  when a rank-up is affordable, and the lock line with where a locked one is won. A tap opens the
  same detail page, whose arrows step through the structures. The base screen's info button stays.
- **Rank, branch and gear on the tower's page.** The rank-up was already the dock's main button.
  On the Equipment tab, a tap on a branch now chooses it. The branch needs rank 7, the first choice
  is free, and a change asks first because it costs 800 coins (the base screen's rules,
  `PlayerProfile.TryChooseBranch`). A tap on a gear slot lists the bag's pieces that fit it, with
  the worn one ticked, and the first row takes the worn piece off
  (`TowerGearFor` / `EquipTower` / `UnequipTower`). The base layout reads the branch from the
  profile, so the base screen shows the change without anything else to do. "Đặt ở căn cứ" still
  opens the base screen with the structure picked.
- **Boss Rush in the mode picker.** Boss Rush is the ninth entry in the home screen's Chế độ
  picker, with its line ("10 trùm liên tiếp"), and it stays on Tác chiến too. It fights on the chosen
  map's sandbox, so the map picker still means something. **Deploy now starts the picker's
  mode.** Before this, after a weekly fortress played from Tác chiến, the picker read Conquest but
  XUẤT KÍCH started the weekly fortress again.
- **The weekly fortress stays on Tác chiến only.** Its map and stage are the week's, not the
  picker's, and its screen is what shows the stage reached. In the picker the map and difficulty
  choices would do nothing.
- **Checks and shots.** There are new screen names for the strict checks and UiShots: `detail-action`,
  `detail-tower-action`, `detail-module-action` and `army-towers`. Each runs at the 4 shapes, at
  Large text and in English, like the others. `KitInteractionTests.TheSetupModePickerOffersBossRush`
  opens the picker, finds Boss Rush and its line, taps it, and checks the mode. PlaySmoke's
  `-mbSmokePreview <png>` writes the preview texture at the end of the menu step (with
  `-mb-detail=<id> -mb-detail-firing`, the In action theatre). In batch mode (a 640 x 480 screen)
  it gave a 404 x 378 texture for the 4:3 theatre box, with the tank firing on the range in frame.
  `-mb-detail-firing` also opens a device check on the In action tab.

## 12G. Test feedback 2: the troop transport's route (2026-09-29)

The owner saw the transport that drops the enemy's bought vehicles fly for a while and then vanish mid-map. It flew a
straight line along the side's way into the battle, 112 m before the drop and 154 m after it, and was removed at the end
of that line, often over the battlefield.

- It now takes the shortest way over the map: in from the map edge nearest the drop, square to it, from 45 m beyond the
  edge (out of the battle's view); over the drop as the vehicle leaves it; a 32 m climbing U-turn, banked 35 degrees,
  towards the middle of that edge; and home the way it came, removed 45 m past the edge.
- When the delivery leaves it little time (the drop is released about 1.2 s after the order on a 3.5 s delivery), it comes
  in faster (up to 160 m/s) so it still starts beyond the edge, instead of appearing half-way.
- View only (`AirDrops`); the sim's delivery time and landing point are unchanged. `TransportRouteTests` checks that it
  appears and leaves beyond the edge, passes over the drop and never goes further in than the drop and its turn.

## 12H. Test feedback 2: fighter and helicopter sizes (2026-09-29)

The owner found the fighters too big next to the other aircraft. Drawn size against the real aircraft: the fighter was at
0.70 of an F-16, the bombers and the transport about 0.5 (B-52 0.44-0.54, B-2 0.47, C-130 0.53-0.57), the attack jet
0.57, the A-10 0.54-0.59, the helicopters 0.47-0.56. Bombers and the transport keep their size; the rest shrink so they
sit at or under the bombers' ratio (model `scale` only):

| Aircraft | Scale | Change | Drawn length |
|---|---|---|---|
| fighter_jet | 0.55 -> 0.39 | -30 % | 10.6 -> 7.5 m |
| attack_jet (and its elite) | 0.66 -> 0.56 | -15 % | 8.8 -> 7.5 m |
| tank_buster (A-10) | 0.56 -> 0.50 | -10 % | 9.6 -> 8.6 m |
| attack_helicopter and its elite | 0.81 -> 0.69 | -15 % | 8.3 -> 7.1 m |
| gunship_heli (Mi-24) | 0.68 -> 0.58 | -15 % | 9.8 -> 8.4 m |
| heavy_attack_heli (Ka-52) | 0.56 -> 0.48 | -15 % | 9.0 -> 7.7 m |
| scout_heli | 0.63 -> 0.57 | -10 % | 5.6 -> 5.1 m |

The owner then asked for the other aircraft too, where needed. Ground vehicles are drawn at 0.65-0.9 of the real
thing; the big aircraft sat at 0.46-0.53 but fly 40-46 m up, nearer the camera, so they still read large (a 26 m
bomber), and the strike drone was now bigger than the fighter:

| Aircraft | Scale | Change | Biggest extent |
|---|---|---|---|
| heavy_bomber | 1.44 -> 1.22 | -15 % | 26.0 -> 22.0 m |
| stealth_bomber | 1.52 -> 1.29 | -15 % | 24.4 -> 20.7 m |
| sky_gunship (also the troop transport's model) | 1.25 -> 1.06 | -15 % | 21.4 -> 18.2 m |
| strike_drone | 0.98 -> 0.78 | -20 % | 10.9 -> 8.7 m |
| recon_drone | 0.54 -> 0.49 | -10 % | 6.5 -> 5.9 m |

Flying bosses (the heavy gunship, the Spectre, the drone mothership, the command airship) keep their size: a boss is
meant to dwarf the rest.

The sim's `radius`, `length` and `width` are unchanged (hits, spacing and blasts behave as before); muzzles and parts are
model nodes, so they follow the smaller model.
