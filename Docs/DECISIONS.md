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
- **Proper names kept in Vietnamese** (checked by `UiLanguageTests` over every Vietnamese text of the game, the kit's, the menus', the guides' and the campaign's; every other unmarked Latin word counts as English): abbreviations and units `CP`, `HQ`, `HP`, `HUD`, `UAV`, `FPV`, `SAM`, `EMP`, `SEAD`, `MOAB`, `APS`, `ATGM`, `IFV`, `MLRS`, `GMLRS`, `EW`, `CIWS`, `FPS`, `mm`, `cm`, `MW`, and the Vietnamese abbreviations `PK` (phòng không), `TT` (trực thăng), `ST` (sát thương), `TL` (tên lửa), `SCH` (sở chỉ huy), `CT` (công trình), `TN` (tinh nhuệ, in the short names of elites); real weapons and vehicles the units are modelled on `AC-130`, `Ka-52`, `Grad`, `Smerch`, `TOS`, `Iskander`, `Patriot`, `Tunguska`, `ZU`, `BMPT`, `Terminator`, `Ataka`, `BTR`, `Object`, `Bradley`, `TOW`, `Centauro`, `Sprut`, `PzH`, `Merkava`, `Trophy`, `Kornet`, `Iron`, `Cobra`, `Lancet`, `Shahed`, `Hellfire`, `Stinger`, `Apache`, `Little Bird`, `Reaper`, `Maverick`, `Alligator`, `Vikhr`, `Igla`, `JASSM`, `Wolf`, `Griffin`, `Centurion`; the bosses' and branches' code names `Behemoth`, `Inferno`, `Tempest`, `Hive`, `Bastion`, `Spectre`, `Titan`, `Napalm`; the equipment brands `Ironclad`, `Kestrel Dynamics`, `Vulcan Arms`, `Longbow Ordnance`, `Aegis Systems`, `Stormfront Aviation`, `Hivemind Robotics`, `Quartermaster`, `Spectre Electronics`, `Hammerfall Munitions`, `Phoenix Recovery`, `Wolfpack Tactics`, `Bulwark Engineering`; the story's people and faction `Varga`, `Kessler`, `Orlov`, `Aurel`, `Hegemon`; the game `Machine Brigade`; and three words Vietnamese took in whole: `radar`, `drone`, `boss`, with `vonfram` (tungsten) and `pin` (battery), which the syllable check cannot tell from English.
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

## 12A. Test feedback 2: muzzle flashes and the flame's origin (2026-09-29)

The owner's second play test: the scout jeep's muzzle flash (and many others') was drawn in the
wrong place although its rounds left from the right spot; the flame tank's fire looked right but
did not start from its nozzle. Added during the work: vehicles driving through a fire burning on
the ground must be drawn on top of it (the flames covered the whole vehicle), and ground fires
burn 20 % shorter, napalm excepted.

- **Root causes of the misplaced flashes (four, all in the flash path, not the round's).**
  1. *Stretched particles trail behind their position.* Unity draws a stretched billboard from
     the particle (its tip) back along its velocity by size x lengthScale + speed x velocityScale
     (measured by baking the mesh: `FlashTests.StretchedFlamesTrailBehindTheirParticle`). The
     muzzle's flame tongue was placed half a flame out, as if the quad were centred, so half of
     every tongue burned back over the barrel: about 1 m on a machine gun, 3 m on a tank gun,
     whichever way the vehicle faced. Tongues are now placed a whole flame out (at the size they
     are born at), so their base sits on the tip.
  2. *World-space flashes left behind.* The five muzzle systems are world space; the core and
     tongues stayed where they were lit for their 0.05-0.15 s, and the second and third flickers
     of a machine-gun burst were lit where the muzzle had been 55 and 110 ms earlier. A scout jeep
     at 12 m/s with a 360 deg/s turret trailed its flash by up to 2.6 m, a jet by 20-25 m. Now each
     core and tongue particle rides its muzzle: it gets a unique random seed, and
     `MuzzleFx.Follow` (called in `EffectsDirector.LaunchShots`, after the views are drawn) puts
     it back on the muzzle node the round left from (`LastMuzzleNode`/`LastMuzzleLocal`, the
     same anchor as the round) and turns it along the barrel every frame. The later flickers of a
     burst light at the tip where it is then. Sparks, smoke, the fireball and dust are thrown into
     the air and stay world space (only two small systems are read back, and only while a flash
     is alive).
  3. *Flashes faced the aim point, not the barrel.* Gun flashes (bullets, direct-fire shells,
     rails, the flamethrower's) were pointed from the muzzle at the aim point, up to 105 deg off
     the drawn barrel (a turret still swinging, a jet's nose gun at a ground target). They face
     along the drawn barrel now (`VehicleView.DrawnBarrelOf`: the part the mount turns with, with
     the hull's pitch, and the main gun's elevation). Launchers keep their launch line.
  4. *Depth pull in perspective views.* Fire, smoke and flash materials are pulled 3-30 m
     towards the camera so the ground does not slice them; with the battle's orthographic camera
     that only changes depth, but the detail page's range and preview cameras are perspective,
     where sliding along the view axis moved them across the screen, away from their muzzle and
     nozzle (by a fifth of their distance from the middle of the view at the range's framing).
     `MbDepth.hlsl` pulls along the ray to a perspective camera (Particle, Flipbook and Beam
     shaders); the orthographic path is unchanged.
- **The flame's origin.** The stream was fed for its whole trigger gap (up to 0.64 s) from the
  point where the trigger was last pulled, 2-3 m behind a flame tank on the move, and its burning
  streaks were born with their tip on the nozzle, trailing their whole length (2-3 m) back over
  the turret (the same stretched-particle geometry). The stream now keeps the nozzle's anchor,
  is fed from the nozzle as drawn once the views are drawn (`Emitters.FeedFlames`, from
  `LaunchShots`; tools that only tick keep the old order), and each streak starts with its back
  end on the nozzle; the fire balls and heat halo start just out of it. The flame shape fades
  over about the last tenth of a streak (Particle.shader, shape 3), so streaks and tongues are
  placed with that visible end on the muzzle (`MuzzleFx.FlameShapeMargin`). The look (DECISIONS
  11A) is unchanged: same particles, rates, sizes and colours. The flame tank's `Muzzle_main`
  node, which its rounds and now its stream leave from (11B), sits about 0.3 m beyond the end of
  the drawn nozzle; left as it is, so the stream and the damage agree.
- **Measured (`FlashTests.FlashesRideTheDrawnMuzzleOfEveryWeapon`, all 138 vehicles with a gun:
  elites, bosses, towers and aircraft included).** Each fights a dummy twice, once turning onto it
  and once driving past it, drawn in the game's frame order, and every live flash particle is
  measured against its drawn muzzle on every frame (3,200 flashes, 32,000 particle-frames). The
  same battles with the old behaviour switched back on (`MuzzleFx.RideMuzzles`,
  `WeaponEffects.AlongBarrel`, `Emitters.RideNozzles` false) give the before numbers. Worst
  distance of a flash's visible base from its drawn barrel tip over its life: before, median
  2.2 m, over 0.5 m on 115 of the 138, scout jeep 2.3 m, light tank 2.8 m, main battle tank
  3.5 m, twin tank 3.5 m, gun turret 3.3 m, behemoth 3.9 m, flame tank 2.2 m, attack helicopter
  8.7 m, attack jet 19.9 m, fighter jet 25.0 m; after, 0.000 m on every vehicle. Forward tongues
  point within 4.6 deg of the drawn barrel (their own jitter; 30-44 deg before). The flame
  stream's origin was 2.2-2.9 m off its nozzle on the move and its streaks started 3.3-3.8 m
  behind it; now 0.000 m and none behind. The test asserts 3 cm, 6 deg and 5 cm; it runs in about
  12 s. The
  vehicles that did not fire a flash in it are the unarmed structures, mine fields, dragon's
  teeth, drone hangars (their drones launch elsewhere), the bomber (bombs have no flash), the car
  bomb, the super gun (it does not fire inside the test's seven seconds) and the command vehicle
  and counter-battery radar, whose machine gun never fires at a dummy (seen in 11D too).
- **Render checks.** `MuzzleShots.Flashes` (-mbShotsOut folder, optional -mbShotsIds a+b):
  flashes_NN.png, a row per vehicle, facing 0/90/180/270 deg with the turret swung onto a dummy,
  frozen on the frame the most mounts show a flash, a green ball on each drawn tip a flash rides;
  a fifth column through a perspective camera like the range's, the vehicle off the middle.
  `MuzzleShots.GroundFire`: groundfire.png, a tank and a jeep parked in burning patches, before
  (left) and after (right).
- **Ground fires under the vehicles.** Decided: a fire burning on the ground lies on the ground
  *in depth*. Its flames' vertices slide along their view ray onto the ground plane (20 cm up;
  `MbOntoGround`, material float `_OntoGround`), so on screen a fire looks exactly as before but
  anything standing above the ground, a vehicle driving through it first of all, is drawn over it.
  Pushing the flames back by a fixed distance was rejected: the ground would then slice off their
  lower metres (the ground behind a flame at height h is only 0.78 h deeper in this view).
  Flattening the flames under vehicles would change their look and need a per-vehicle mask;
  render queues cannot put transparent flames under opaque vehicles without drawing them in the
  opaque pass. Which fires: `FireSpots` fires with no anchor below 0.7 m (blast and shell
  craters, thermobaric, napalm's burning ground, strike and boss-death rings, burning debris,
  the fires at a wrecked defence's foot, crashed aircraft) draw into a second flame system and a
  second firelight system with ground-lying copies of their materials (`FireSpots.OnGround`); the
  flame stream's licks on the ground draw into their own system. Fires riding a hull or up on a
  wreck (wreck fires, boss part fires, cook-off jets) and the licks on the target the stream hits
  are unchanged, so a burning vehicle still burns in front of itself. Trade-off: a vehicle or tree
  standing just behind a ground fire also covers the tips of its flames.
- **Ground fires burn 20 % shorter, napalm excepted.** `FireSpots.Ignite` burns a ground fire
  for 0.8 of the time it is lit for (`GroundBurn`) unless it is napalm (the napalm strike's
  burning strip passes `napalm: true`); fires on hulls and wrecks keep their time. The simulation
  has no burning-ground damage zones (fire damage is the Burn status on vehicles, unchanged), so
  balance.json was not touched: the drawn fire is the only thing that burns on the ground. The
  flamethrower's ground fires count as ground fires, not napalm (napalm is the strike).
  (`FlashTests.GroundFiresBurnAFifthShorterAndLieUnderVehicles`.)
- **Also:** at night the ground light of a shot is lit under its muzzle, not in front of the hull.
- **Not changed (other lanes):** a laser's beam re-reads its muzzle in `LaserBeams.Tick`, before
  the views are drawn (a frame behind a moving emitter); the napalm strike's fire wall is an
  explosion (`ExplosionEffect.CreateNapalm`) and still draws over vehicles for its few seconds.
- **After the fire-rhythm merge (12D).** `FlashTests` reported a drone mothership flak flash
  lit 12-13 m off its round. The flash was right: each shot's anchor is taken from that shot's own
  `MuzzleOf(mount)` (per shot and per mount, not per view), and every flash rode the part its round
  left from. The test was wrong. It paired the frame's rounds and flashes by order, and since 12D a
  stream's second round in one frame (boss flak: 20 rounds a second, a 50-round clip) is launched
  without a flash of its own, so from then on each flash was compared with the next round, the
  other flak gun's. Each flash is now paired with the round it is lit for, and the test also
  asserts that it rides that round's part (`MuzzleFx.Flashed` passes the anchor). Mounts sharing a
  slot each have their own muzzle (behemoth, mothership, mega gunship, fortresses, trains). One real
  fault was found: the Inferno's two flame projectors (mount 0 and a second mount on slot "main")
  both fired from `Muzzle_main`, which sits between the nozzles, and mount 0 also swapped nozzles
  shot by shot. Now each fires from its own nozzle, 1.5 m apart (`VehicleView._ownBarrel`;
  `FlashTests.TwinMainMountsFireFromTheirOwnBarrels`). The armored train's two MG mounts share
  its one `Muzzle_mg`, and its `train_gun` shares `Muzzle_main` with the main gun: the model has
  only one of each (Blender lane).

## 12B. Test feedback 2: missile plumes, sizes and speed (2026-09-29)

The owner's second play test: the SAM launcher's missiles were a little too big and had no fire or
smoke at the tail ("nên làm lửa bự và dài": make the flame big and long); other missiles lacked the
tail flame too; missiles, above all those fired by helicopters and jets, should fly slower still.

### A. Motor plumes

Before, a flying missile or rocket emitted one small fire puff a frame 0.6 m behind its pivot (life
0.08-0.16 s, 0.3-0.6 m) and small grey trail puffs 0.55 m apart that lived 0.6-1.1 s. It hardly
showed at battle zoom. Now every missile and rocket burns a plume from its model's tail while its
motor burns (`MotorPlumes`, a new file; `Plume.For` picks the plume by type):

- **Hot core:** a white-yellow point on the nozzle.
- **Tongue:** a short yellow stretched quad.
- **Flame cone:** one to five stretched fire quads end to end, yellow at the nozzle and red at the
  tip, tapering and flickering every frame (length ±18 %, width ±12 %). It is about 60 % of its full
  length off the rail and full length at cruise, so it stretches with speed. It is fattest off the
  rail, where the boost motor burns.
- **Glow:** a soft orange stretched glow under the whole cone. It feeds the bloom and joins the
  quads.
- **Smoke trail:** a smoke trail leaves the tip of the flame. Each puff starts warm-white, turns pale
  grey, grows to 3.6 times its size and drifts off with the wind, rising slowly.

The plume's size is measured in lengths of the munition as drawn:

| Munition | Flame length | Width at nozzle | Burns | Puff spacing |
|---|---|---|---|---|
| Ground SAMs (`sam`, `sam_long`, `sam_battery`, `sam_48n6`) | 2.6 | 0.24 | whole flight | 0.3 puffs |
| Air-to-air | 2.1 | 0.22 | whole flight | 0.3 |
| MANPADS (Stinger, Igla) | 2.0 | 0.28 | whole flight | 0.3 |
| Air-to-ground (Hellfire, Vikhr, Maverick, Griffin) | 1.6 | 0.27 | whole flight | 0.3 |
| Ground ATGMs (TOW, Kornet, Ataka) | 1.3 | 0.28 | whole flight | 0.3 |
| Direct-fire rockets (Hydra, S-8) | 1.7 | 0.3 | whole flight | 0.4 |
| Artillery rockets (Grad, GMLRS, TOS, 300 mm, 107 mm) | 1.6 | 0.26 | 85 % | 0.45 |
| Ballistic missile | 1.5 | 0.24 | 75 % | 0.3 |
| Cruise missiles, JASSM (a jet engine) | 0.6 | 0.13 | whole flight | 0.35 |
| Drones (propellers, electric motors) | none | | | |

So a 2.6 m SAM burns a flame about 6.7 m long, a 7 m ballistic missile one of about 10 m, and a
1.1 m ATGM a short, sharp flame of about 1.5 m. The support strike's cruise missile gets the cruise
plume (`StrikeEffects.LaunchCruise`, one line). Drones keep their old small motor puff and trail,
and so do shells and railgun slugs (no plume).

**Particle budget by graphics tier** (per motor, per frame; flame particles live 2.4 frames,
0.05-0.12 s):

| Tier | Cone quads | Tongue + core | Glow | Per frame | Smoke spacing | Smoke life |
|---|---|---|---|---|---|---|
| High | up to 5 | 2 | 1 | 4-8 | x1 | 3.2 s |
| Medium | up to 4 | 2 | 1 | 4-7 | x1.25 | 2.5 s |
| Low | up to 2 | 2 | none | 3-4 | x1.6 | 1.7 s |
| Before | | | | 1 puff | 0.55 m | 0.85 s |

Caps: 6000 / 4000 / 2500 smoke puffs (High, Medium, Low), 2400 cone quads, 900 tongues and cores,
600 glows. A Grad salvo (20 rockets) leaves about 2200 puffs on High. Low still carries more fire
and smoke than before, as the rule says: more flame particles a frame, and puffs that live twice as
long, closer together (0.24 m for a Hellfire against 0.55 m).

**Two things found on the way:**

- **Stretched billboards trail behind their particle.** Unity draws a stretched billboard from its
  particle backwards, against its velocity, not centred on the particle. A cone placed as if centred
  started half a quad behind the tail, which showed as a gap on thick rocket flames. The plume
  places each quad by its front end (`MotorPlumes.Head`). `MuzzleFx`'s tongue assumes centred quads,
  so its flame probably sits half inside the barrel. That is the muzzle work's to check.
- **One frame of lead.** Effects tick in `Update`, before Unity's particle update, so a particle
  emitted this frame is moved on by one frame before it is drawn. The flame's particles fly with the
  missile, so the plume stays on its tail as it moves. They are therefore emitted one frame back.
  Without that, a rocket's flame showed up to one body length ahead of it.

### B. Drawn sizes

Each missile was measured against its launcher: the missile model, the store on the launcher's
rails or its box or tube (glTF node bounds times the vehicle's scale), and the renders. The type
table `WeaponEffects.SizeOf` is unchanged (ATGM/MANPADS 1.1, rockets 1.15, AGM/SAM/AAM/cruise 1.2,
drones 2). The fit is per weapon, in balance.json's `projectileScale`. The worst cases were the
aircraft stores: an aircraft is drawn at 0.55-0.8 of its size, but the munition models are full
size, so a flying Hellfire was twice the one on the pylon. The plume now makes a missile readable,
so its model can match its launcher. Where a store shows on the launcher, a flying missile is drawn
at up to about 1.25 times that store.

| Weapon | Model | Launcher (store/box as drawn) | Drawn before | Drawn after | projectileScale |
|---|---|---|---|---|---|
| `sam_long` | Buk 3.6 m | SAM launcher's box 2.45 m | 4.32 m | 2.59 m | 0.6 |
| `sam` | SHORAD dart 2.2 m / Stinger (AA vehicle's mount) | heavy AA pack 2.0 m, AA vehicle launcher 1.0 m | 2.64 / 1.43 m | 1.98 / 1.07 m | 0.75 |
| `sam_battery` (+`sam_pac3`, `sam_battery_lrr`) | Patriot 3.4 m | canister 3.7 m | 4.08 m | 3.75 m | 0.92 |
| `atgm` | TOW 1.3 m | IFV 0.89 m, Titan and elite APC 0.98 m | 1.43 m | 1.14 m | 0.8 |
| `ataka` | Ataka 1.5 m | BMPT box 1.36 m | 1.65 m | 1.45 m | 0.88 |
| `heli_atgm` | Hellfire 1.4 m | Apache rack 0.81 m | 1.68 m | 1.04 m | 0.62 |
| `hellfire_volley` | Longbow 1.4 m | elite Apache rack 0.89 m | 1.68 m | 1.09 m | 0.65 |
| `drone_missile` | Hellfire 1.4 m | strike drone rack 0.88 m | 1.68 m | 1.09 m | 0.65 |
| `recon_missile` | MAM-L 1.0 m | recon drone rack 0.57 m | 1.20 m | 0.72 m | 0.6 |
| `vikhr` | Ataka 1.5 m | Ka-52 tubes 1.12 m | 1.80 m | 1.30 m | 0.72 |
| `maverick`, `kh29` | Maverick 2.0 m | A-10 rack 1.10 m | 2.40 m | 1.39 m | 0.58 |
| `air_to_air` | AIM-120 2.6 m | fighter (a quarter of its length, as real) | 3.12 m | 2.65 m | 0.85 |
| `wvr_aam` | AIM-9 2.2 m | fighter | 2.64 m | 2.11 m | 0.8 |
| `aim9` | AIM-9 2.2 m | A-10 | 2.64 m | 1.85 m | 0.7 |
| `r60` | R-60 1.6 m | attack jet rail 1.0 m | 1.92 m | 1.25 m | 0.65 |
| `stinger_atas` | Stinger 1.3 m | Apache | 1.43 m | 1.00 m | 0.7 |
| `igla_v` | Igla 1.3 m | Ka-52 tubes 0.95 m | 1.43 m | 1.12 m | 0.78 |
| `scout_rockets` | Hydra 1.0 m | scout heli pod 0.69 m | 1.15 m | 0.83 m | 0.72 |
| `gunship_rockets`, `s8_pods`, `hind_rockets` | S-8 1.2 m | pods 1.09-1.16 m | 1.38 m | 1.24 m | 0.9 |
| `ballistic_missile` | 7.1 m | the launcher's missile, about 6.3 m | 8.19 m | 6.96 m | 0.85 |

These fit their launchers already and are unchanged:

| Weapon | Drawn |
|---|---|
| `sam_48n6` | 5.3 m, the launcher tube 6.7 m |
| `atgm_heavy`, `kornet_twin`, `atgm_post`, `boss_missiles` | 1.43 m, launchers 1.5-1.9 m |
| `griffin` | 1.2 m, off the AC-130's ramp |
| JASSM | 3.6 m |
| cruise missile | 4.8 m |
| GMLRS | 3.2 m, the pod 3.1 m |
| TOS | 2.8 m, the launcher 4.2 m |
| 300 mm rocket | 4.1 m, the tubes 5.0 m |
| Grad (turret) | 2.5 m, the box 2.6 m |
| 107 mm rocket | 1.0 m |
| Hydra (Apache, A-10) | 1.15 m, the pods 1.13-1.15 m |
| drones | 2x, as before |

### C. Speed

Ground-launched guided missiles are about a fifth slower again. Aircraft-launched missiles are 28-30
% slower. The aircraft's unguided rockets are a fifth slower: they miss a moving target more when
slower, so they lose less. The cruise missiles lose 15 %, since they were already the slowest.
Artillery rockets, the ballistic missile, drones and ground direct-fire rockets are unchanged.

| Missile | Weapons | Speed (m/s): 11C → now | Flight at full range | Cooldown |
|---|---|---|---|---|
| ATGM | `atgm`, `atgm_heavy`, `ataka`, `atgm_post`, `boss_missiles` | 24 → 19 (-21 %) | 34 m: 1.42 → 1.79 s; 45 m: 1.88 → 2.37 s | 5-14 s |
| Kornet | `kornet_twin` (+`kornet_top`, `kornet_multi`) | 25 → 20 (-20 %) | 50 m: 2.0 → 2.5 s | 9 s |
| SHORAD | `sam` | 40 → 32 (-20 %) | 44 m: 1.1 → 1.38 s | 6 s |
| Medium/long SAM | `sam_long`, `sam_battery` (+`sam_pac3`, `sam_battery_lrr`) | 46 → 37 (-20 %) | 55 m: 1.2 → 1.49 s; 100 m: 2.17 → 2.7 s | 5.5-7 s |
| S-400 48N6 | `sam_48n6` | 62 → 50 (-19 %) | 95 m: 1.53 → 1.9 s | 8 s |
| Hellfire class (aircraft) | `heli_atgm`, `hellfire_volley`, `drone_missile`, `griffin`, `recon_missile` | 30 → 21 (-30 %) | 34 m: 1.13 → 1.62 s; 50 m: 1.67 → 2.38 s | 4-8 s |
| Vikhr (Ka-52) | `vikhr` | 34 → 24 (-29 %) | 55 m: 1.62 → 2.29 s | 6.5 s |
| Maverick / Kh-29 | `maverick`, `kh29` | 32 → 23 (-28 %) | 40 m: 1.25 → 1.74 s | 8-14 s |
| Air-to-air | `air_to_air`, `wvr_aam`, `r60`, `aim9` | 48 → 34 (-29 %) | 60 m: 1.25 → 1.76 s; 30 m: 0.62 → 0.88 s | 2.5-8 s |
| Helicopter MANPADS | `stinger_atas`, `igla_v` | 40 → 29 (-28 %) | 32 m: 0.8 → 1.1 s | 8-10 s |
| Cruise / stand-off | `air_cruise_missile`, `jassm` | 20 → 17 (-15 %) | 110 m: 5.5 → 6.5 s; 90 m: 4.5 → 5.3 s | 14 / 10 s |
| Aircraft rockets | `heli_rockets`, `gunship_rockets`, `scout_rockets`, `jet_rockets`, `s8_pods`, `hind_rockets` | 60 → 48 (-20 %) | 36 m: 0.6 → 0.75 s | 7-9 s |

- **No flight reaches its cooldown.** This is checked for every missile and rocket in
  `MissileFlightTests`. The closest is the AC-130's Griffin: 2.38 s of flight on a 4 s cooldown
  (60 %).
- **Guided missiles still hit moving targets.** A guided round lands on its target's position at
  impact (`DamageSystem.ResolveImpact`), and the view bends onto the live target. APS intercepts at
  impact and does not depend on speed. The fire-control lead (`GearSystem.Lead`) reads the speed.
- **Flares.** A missile is decoyed by flares out at impact or put out while it flew
  (`Projectile.LaunchedAt`, 11C). Longer flights (an AAM now takes 1.76 s at 60 m) overlap a flare's
  1.5-3 s burn more often. Missiles at flaring aircraft are therefore decoyed somewhat more often.
  That is left for the testing phase.

### D. Flight: boost, then cruise

The view flew a missile as (1-b)t + bt², slow off the rail and speeding up for its whole flight, so
it arrived at its fastest. With slower missiles that read as a missile creeping and then darting.
Now a boosted round leaves the rail at 20 % of its cruise speed and speeds up evenly to cruise over
the first `boost x 0.35` of its flight: 19 % for missiles, 21 % for the ballistic missile, 10 % for
direct-fire rockets, 7 % for artillery rockets. It then cruises at a steady speed, 3-8 % above its
average, and still arrives on the simulation's time (`ProjectilePool.Progress`). The flame
stretches as it speeds up (`SpeedAt`). The ballistic missile wobbles less than an artillery rocket (0.3,
not 0.7) and has a longer boost (0.6).

### E. Tools and tests

- **Contact sheets:** `MachineBrigade.Editor.MissileShots.Run -mbShotsOut <folder>
  [-mbShotsIds a+b]`, run in batch mode with graphics. It renders 30 launchers, six to a sheet
  (`missiles_1.png` to `missiles_5.png`), each firing its first missile or rocket at a target (a
  helicopter for anti-air weapons). The first frame shows the missile beside its launcher at 0.2 s,
  to judge its size. The next three close on the missile at 25, 50 and 80 % of its flight, with its
  flame and trail. `missiles.txt` lists each flight time and drawn length. It is a new file, apart
  from `MuzzleShots`.
- **`MissileFlightTests` (EditMode, new):**
  - The boost-then-cruise curve arrives on time, always moves forward, leaves at rail speed and
    cruises steadily.
  - Every missile and rocket burns a plume, and a SAM's plume is longer than an ATGM's; drones have
    none.
  - The new speeds are pinned, and every missile and rocket flight at full range is shorter than its
    cooldown.
  - The drawn sizes of the SAM launcher, the Apache's Hellfire and the A-10's Maverick are pinned.
- **Unchanged:** the `MuzzleTests` size table, since `SizeOf` is unchanged.

### F. Left for the testing phase

- Missile hit rates in battle with the slower missiles: flares against AAMs and SAMs, APS, and
  jammers.
- Aircraft rockets against moving columns: they are unguided, and 25 % more flight time means more
  misses.
- FPS on the device with many plumes: a Grad and MLRS barrage alongside helicopter salvos, on the Low
  and Medium tiers.
- The plume on dark maps and at night. It was judged on the sand stage only.
- Whether the owner finds the aircraft missiles too small now. They were cut to 55-75 % of their
  11B size to match their pylons. If so, raise their `projectileScale` a little; the plume already
  carries the eye.

## 12C. Test feedback 2: explosion size and life (2026-09-29)

The owner's second play test: tank-round explosions vanish too fast, every explosion should be a
tenth bigger, drone blasts should be bigger by the drone, and the fire-support cards all bring
the same round down (the smoke screen looked exactly like the artillery barrage). All of it is
the view's: no simulation code, damage, radius or balance.json changed.

- **Tank rounds linger by the tank's class** (`BlastSizes.ShellLife`, the same classes as the 11A
  sizes): light tank and wheeled gun +20 %; main battle tank, tank destroyers (and the elite one),
  twin tank, elite MBT and the 120 mm turrets +25 %; heavy, elite heavy, titan and the siege tank
  +30 %. The siege tank's 203 mm is a high-explosive landing, so its blast lingers +30 % too
  (`BlastSizes.GroundLife`); other artillery is unchanged.
- **How it lingers.** `ExplosionEffect.Play` takes a `life` factor. It stretches the lifetimes of
  the fire, smoke and dust layers (fireballs, rolling fireballs, smoke, dust, dust skirt) and the
  embers. The flash, sparks, air snap, ground light, metal flakes and the spark burst keep their
  0.07 to 0.4 s, and every burst still starts on time, so the hit stays snappy and only what
  follows it hangs on. The fireball flipbooks play over their life, so the flame itself rolls a
  fifth to a third slower into its smoke. That is what makes it read as lingering, and it reads
  heavier on the bigger guns. The white-hot pop in front of it is unchanged.
- **Low stays cheap: the extra life is scaled by tier** like the extra particles of 11A
  (`ExplosionEffect.Linger`, the extra over 1 times `Density`): High gets all of it, Medium 75 %,
  Low 40 % (so +8, +10 and +12 % on Low). A recipe's own life is never shortened.
- **Every blast a tenth bigger** (`BlastSizes.Bigger` = 1.1), multiplied onto every other factor:
  tank class, bomb weight, drone type, the cruise missile's radius match. So tank rounds are x1.43,
  x1.54 and x1.65; bombs x1.43 to x1.65; artillery, rockets, missiles and vehicle deaths, which had
  no factor, are x1.1. It is applied in `EffectsDirector.Explode` for every tier above Small, and
  to pops (bomblets, cook-offs, interceptions, the killing hit), airbursts, the napalm and
  thermobaric fire, the boss's great blast and the tank shell hit. It uses the existing `grow`, so
  the blasts get more quads spread wider rather than bigger sprites, and the flash, rings and glows
  grow. The Small tier is not a blast (bullets, flak, an autocannon's sparks) and keeps its size,
  and so do falling buildings (their dust). The bomb's ground ring and smoke column and the HE
  shell's ring and smoke grow with it; scorch marks do not (they are craters, not the blast).
- **The cruise missile and MOAB rings.** +10 % would put the ground shockwave 10 % past the
  damage radius (19.8 m on the cruise missile's 18 m). **Decision: the ring stays on the radius,
  and the fireball grows.** The ring is how a player reads the ground the strike wrecks, so it
  keeps matching the damage. The fireball cluster, smoke, dust skirt, flash, air ring and glows
  take the extra tenth: the fire now fills about 82 % of the radius instead of 75 %, and the dust
  rolls a little past the edge. `Play` takes the ring's own grow (`ring`), and EffectsDirector
  passes `BlastSizes.Reach(radius)` for it. The tests check that the ring is still within 0.95 to
  1.1 of the radius and that the flash is 10 % bigger.
- **Drones by type** (`BlastSizes.Drone`), times the general 1.1: FPV drones (the carrier's swarm,
  the hangars' and the airship's) x1.2, so x1.32; the Lancet (and the Lancet hangar) x1.25, so
  x1.375; the Shahed and the strike drone's missiles x1.3, so x1.43. **Decision:** the drone
  mothership's attack drones are loitering munitions like the Lancet (150 damage, a Large blast),
  so they get the Lancet's x1.25. The two factors multiply, like every other factor above.
- **Particles per blast, High / Medium / Low** (particles, then particle-seconds of the lingering
  layers + the rest, from `BlastRig.Budget`). Tank round, light: 11A 59 / 55 / 49 (29+41, 26+39,
  24+34 ps), now 71 / 61 / 52 (44+49, 33+44, 28+35). Main: 11A 69 / 59 / 51 (37+46, 29+41, 26+35),
  now 78 / 69 / 55 (49+54, 44+46, 29+39). Heavy: 11A 75 / 68 / 54 (40+51, 37+45, 26+38), now
  86 / 75 / 58 (58+60, 48+51, 32+40). The spark burst on top is 23 / 21 / 19 (light) and 55 / 51 / 44 to
  59 / 54 / 45 (the others). Siege 203 mm: 11A 502 / 446 / 366, now 574 / 502 / 393 (lingering
  454 to 669 ps on High, 333 to 399 on Low). Medium (a missile or rocket) 72 to 81 / 79 / 75;
  GBU-12 283 / 252 / 213 (11A 245 / 197 on High and Low); Mk 84 574 / 502 / 393 (11A 502 / 366);
  JDAM 774 / 677 / 530 (11A 675 / 490); cruise missile 891 / 761 / 582 (11A 774 / 530); MOAB
  1544 / 1247 / 840 (11A 1358 / 765); FPV 105 / 98 / 85, Lancet 113 / 104 / 88, Shahed 467 / 416 / 352
  (the Shahed was a plain Huge blast of 276). On Low a heavy round's lingering fill grows 23 %
  (26 to 32 ps), against 45 % on High.
- **Lifetimes, High / Medium / Low** (the shell hit, heavy class): hot fireball 1.05 to 1.3 s, now
  1.37 to 1.69 / 1.29 to 1.59 / 1.18 to 1.46 s; smoke 1.8 to 2.6 s, now 2.34 to 3.38 / 2.21 to 3.19 /
  2.02 to 2.91 s; embers 1.5 to 3.5 s, now up to 4.55 / 4.29 / 3.92 s; dust 1 to 1.8 s, now up to 2.34 s
  on High. The light class is +20 % (+15 % Medium, +8 % Low), the main class +25 % (+19 %, +10 %).
  The flash (0.07 to 0.1 s), air snap (0.12 to 0.16 s) and sparks (0.4 to 1.2 s) are as before.
- **Each fire-support card brings its own round down** (`StrikeEffects`, self-contained; AirDrops
  untouched, ProjectilePool only called through `Launch`). EffectsDirector hands every
  ShellInbound to `StrikeEffects.Inbound` first and draws the glowing shell only when that does
  not draw its own round.

  | Card | Coming down | Arriving |
  |---|---|---|
  | Artillery barrage | 155 mm HE shells nose-first inside their glowing tracer, steeply from the guns' side | HE blasts (Large, x1.1), dust rings |
  | Super-gun shells (events) | the same shell at 3.2 times the size, in its tracer | Ultimate blast |
  | Smoke screen | five white canister shells trailing a white wisp, no glow; each bursts open about 6 m up in a white puff | the canisters pour white smoke where they land and the screen builds from them; no HE blast |
  | Remote mines | a salvo of 107 mm rockets on a low arc, motors burning and trailing smoke | each mine thuds in with a dirt puff and a small ring |
  | SEAD strike | the jet passes and fires an anti-radiation missile (Maverick model) with its motor and trail | a Large blast on the radar |
  | Airstrike | the strike jet drops Mk 84s (the Mk 84 model, not the generic bomb) | Huge blasts x1.65 |
  | Bombing raid (air raid event) | a heavy bomber at 32 m (not the strike jet) drops FAB-500s: the carpet bombing | Huge blasts |
  | Napalm strike | the strike jet releases silver, finless canisters that tumble end over end | a rolling wall of fire, burning ground |
  | Cluster strike | four dispensers fall from the wings and split open 14 m up (sparks and a grey puff); forty yellow bomblets tumble onto their own marks | many small blasts along the line |
  | Cruise missile | the cruise missile diving in with its motor and trail (as before) | the Ultimate blast, its ring on the 18 m radius |
  | MOAB | a transport passes over 55 m up; the GBU-43 (the Mk 84 model x2.8) rolls out on a drogue chute, which is cut away as it pitches over, and falls nose-first | the Ultimate blast, its ring on the 27 m radius |
  | EMP | a blue energy warhead drops from high, a ball of light with a crackling blue trail | a blue-white flash and electric arcs, then the two blue rings |
  | Repair drop | a supply crate (the repair crate model, with its own canopy) drifting down | a dust puff; the crate stays for the 6 s it repairs, green sparkle on each vehicle |
  | Reinforcements | an airlift: the transport passes over and the two tanks and the IFV come down under canopies onto the spots they are handed over at, facing +X as the simulation spawns them | dust puffs; the real vehicles take over at touchdown and the chutes sag away |
  | Field tower | parachuted by AirDrops (as before) | white ring |
  | UAV scan | the recon drone flies in and circles (as before) | cyan ring |
  | Gunship support | the gunship's own view already flies in from behind as it spawns (VehicleView); a ghost ahead of it would pop, so nothing is added | small ring |
  | Shield dome, field repair | no round: a projected dome, a repair across the whole map | cyan ring; sparkle on each vehicle |

  The owner's list also named a rocket barrage, JDAM and carpet bombing. None of them is a card:
  the rocket artillery vehicles' rockets already fly with plumes, the JDAM is the stealth bomber's
  weapon, and carpet bombing is the heavy bomber's. The bombing-raid event now uses that bomber.
  Some choices go by support id (air raid, MOAB, the Mk 84 for the airstrike), like
  `BlastSizes`. Napalm is recognised by its fire damage, and a cluster strike by two dozen or more
  bombs. A support called with no direction runs along +X, as StrikeSystem's does (Point2 equal to
  Point gives UnitX), so the airlifted vehicles land facing the way the real ones spawn.
- **Contact sheets** (batch, with graphics): `EffectShots.Impacts` now compares 11A with 12C: tank
  rounds, the siege tank's and a howitzer's shell landing, drones (FPV, Lancet, Shahed), bombs and
  the cruise missile, before and after, then the Mk 84 and the MOAB. It is frozen at 0.04, 0.14,
  0.35, 0.9, 1.5, 2.5 and 3.2 s, so the longer life shows: at 1.5 s the 11A tank round is gone and
  the 12C one still burns; at 2.5 s the heavy round's smoke still hangs. `EffectShots.Supports` (new,
  through `SupportRig`, which replays StrikeSystem's timings) has one card a row from 1.3 s
  before its first impact to 1.6 s after. `BlastRig`'s "before" now means as after 11A.
- **Tests** (EditMode, `BlastSizeTests`): the life factors by class and the drone factors; a
  lingering shell hit stretches its fire, smoke, dust and embers by the factor on High and by 40 %
  of it on Low while its flash, sparks, air shock and ground light keep their life; the MOAB's
  flash is 10 % bigger while its ground ring stays put, and no tier loses a particle at x1.1; the
  cruise missile's ring still reaches its radius with the tenth added; each fire-support card
  draws its own round (smoke, mines and SEAD instead of the glowing shell; napalm, cluster, MOAB,
  EMP, repair drop and airlift come down as something of their own) and the rounds are cleared
  once down.
- **Left for the testing phase:** frame time on a Low phone in a tank battle (shell hits are the
  most frequent blasts, and their lingering fill is +23 % on Low); the cluster strike's forty
  bomblet objects (made and destroyed per strike, not pooled: it is a single-use item).

## 12D. Test feedback 2: sustained fire for AA and guns (2026-09-29)

The owner liked the jets' new cannon streams (11C C) and asked for the same on many more
weapons, anti-air first: "bắn nhiều để cho đã" (fire a lot, so it's satisfying). Every AA gun,
machine gun, helicopter gun and the one burst-firing autocannon now fire from a magazine (11C's
`clip` / `clipReload`): a stream of 2.5-4 s at 8-33 rounds a second, then a 1-1.5 s change. Each
weapon's damage a second is kept by lighter rounds (`roundWeight` keeps the old tracer, flash
and report), measured with `FireRhythmMeasure` (60 s against a dummy; it now also covers the AA
vehicles and towers, the headquarters, bunkers, the guard tower and the bosses' guns).

### A. What changed

| Group | Weapon | Measured on (target) | Rhythm before | Rhythm after | Damage/round | Rounds/s (60 s) | DPS before -> after | Longest stream |
|---|---|---|---|---|---|---|---|---|
| AA | `zu23` | zu23_technical (attack_helicopter) | 12 @ 22/s every 1.29 s | 20/s x 60, 1.5 s change | 14 -> 9.7 | 9.3 -> 13.4 | 194.6 -> 194.5 (-0 %) | 0.50 -> 3.05 s |
| AA | `flak_35` | aa_vehicle (attack_helicopter) | 10 @ 18/s every 1.40 s | 18.2/s x 50, 1.2 s change | 11 -> 6.85 | 7.2 -> 12.6 | 118.3 -> 129.3 (+9 %, see B.4) | 0.50 -> 2.80 s |
| AA | `twin_30_flak` | heavy_aa (attack_helicopter) | 16 @ 25/s every 1.60 s | 25/s x 80, 1.2 s change | 22 -> 12.75 | 10.1 -> 17.8 | 334.4 -> 339.8 (+2 %, B.4) | 0.60 -> 3.20 s |
| AA | `twin_30_flak` | aa_turret (attack_helicopter) | 16 @ 25/s every 1.60 s | 25/s x 80, 1.2 s change | 22 -> 12.75 | 10.1 -> 17.8 | 418.0 -> 424.7 (+2 %, B.4) | 0.60 -> 3.20 s |
| AA | `hq_flak` (was `twin_30_flak`) | headquarters (attack_helicopter), 2 mounts | 16 @ 25/s every 1.60 s | 25/s x 80, 1.2 s change | 22 -> 15.8 | 16.0 -> 22.4 | 660.0 -> 661.1 (+0 %) | 0.60 -> 3.20 s |
| AA | `flak_quad` | aa_turret.flak (attack_helicopter) | 12 @ 20/s every 1.75 s | 22.2/s x 90, 1.5 s change | 22 -> 9.15 | 6.8 -> 16.4 | 280.5 -> 281.1 (+0 %) | 0.55 -> 4.05 s |
| AA | `twin_35_ahead` | elite_aa (attack_helicopter) | 8 @ 17/s every 1.52 s | 16.7/s x 45, 1.2 s change | 16 -> 8.3 | 5.5 -> 12.2 | 164.0 -> 190.4 (+16 %, B.4) | 0.45 -> 2.70 s |
| AA | `c_ram_gatling` (+ `_long`) | c_ram (attack_helicopter) | 12 @ 33/s every 1.03 s | 33.3/s x 100, 1 s change | 7 -> 3.22 | 11.5 -> 25.0 | 120.8 -> 120.8 (+0 %) | 0.35 -> 3.00 s |
| AA | `hover_ciws` | landing_hovercraft (ifv), 2 mounts | 1 round a second (B.6) | 16.7/s x 50, 1.2 s change | 10 -> 1.83 | 2.0 -> 18.2 | 33.4 -> 33.2 (-1 %) | 0 -> 5.5 s |
| AA | `boss_flak` | behemoth (attack_helicopter), 2 mounts | 10 @ 20/s every 1.35 s | 20/s x 50, 1.2 s change | 21 -> 13.9 | 14.9 -> 22.4 | 468.3 -> 467.7 (-0 %) | 0.45 -> 4.00 s |
| AA | `airship_flak` | command_airship (attack_helicopter), 2 mounts | 8 @ 12/s every 1.66 s | 10/s x 24, 1.5 s change | 26 -> 20.25 | 6.6 -> 8.5 | 258.7 -> 258.7 (+0 %) | 0.60 -> 2.70 s |
| Air | `heli_gun` | attack_helicopter (ifv) | runs of 6-10 @ 8.3/s, ~1 s pause (x1.7 damage) | 10/s x 30, 1.2 s change | 12 -> 10 | 2.8 -> 5.8 | 57.8 -> 57.8 (+0 %) | 1.35 -> 2.95 s |
| Air | `minigun` | scout_heli (armored_car) | runs @ 22.2/s | 22.2/s x 70, 1 s change | 5.6 -> 3.05 | 5.1 -> 16.1 | 48.9 -> 49.1 (+0 %) | 0.70 -> 3.15 s |
| Air | `gsh_23v` | nominal (the Mi-24's standoff keeps it out of its reach in the test) | runs @ 22.2/s | 22.2/s x 60, 1.2 s change | 9.3 -> 6.2 | 6.1 -> 15.6 | 96 -> 96 (nominal) | - |
| Air | `door_gun` | nominal (side guns, the dummy is ahead) | runs @ 14.3/s | 16.7/s x 50, 1.2 s change | 6.4 -> 4.8 | 5.4 -> 12.1 | 58 -> 58 (nominal) | - |
| Air | `boss_heli_gun` | mega_gunship (ifv), 2 mounts | 1 round a second (B.6) | 10/s x 30, 1.2 s change | 16 -> 6 | 1.9 -> 8.5 | 50.8 -> 51.0 (+0 %) | 0 -> 6.3 s |
| Air | `boss_minigun` | mega_gunship (ifv), 2 mounts | 1 round a second (B.6) | 20/s x 60, 1.2 s change | 7 -> 2.25 | 1.9 -> 10.2 | 23.0 -> 22.9 (-0 %) | 0 -> 10.2 s |
| Air | `bomber_tail_guns` | heavy_bomber (attack_helicopter) | runs @ 5/s | 8.3/s x 25, 1.5 s change | 15 -> 12.4 | 1.4 -> 2.9 | 10.7 -> 10.7 (+0 %) | 2.05 -> 2.90 s |
| MG | `mg_coax` (+ `mg_coax_ground`) | main_battle_tank (ifv) | runs @ 10/s | 10/s x 30, 1.2 s change | 4.8 -> 5.8 | 3.1 -> 2.2 | 25.2 -> 13.0 (-48 %; the roof gun +33 %, the pair -5 %) | 1.30 -> 2.90 s |
| MG | `mg_coax` | armored_car / ifv (same) | runs @ 10/s | same | 4.8 -> 5.8 | 1.8 -> 2.4 / 1.5 -> 2.8 | 14.7 -> 13.7 (-7 %) / 12.5 -> 15.9 (+27 %) | ~1 s (fills the cannon's change) |
| MG | `mg_coax_ground` | gun_turret (armored_car) | runs @ 10/s | same | 4.8 -> 5.8 | 3.9 -> 6.5 | 32.0 -> 37.7 (+18 %) | 1.15 -> 2.95 s |
| MG | `hmg_roof` | guard_tower (armored_car) | runs @ 7.7/s | 8.3/s x 25, 1.4 s change | 8.8 -> 8.25 | 3.1 -> 5.8 | 46.9 -> 47.9 (+2 %) | 1.35 -> 2.95 s |
| MG | `hmg_roof` | main_battle_tank (ifv) | runs @ 7.7/s | same | 8.8 -> 8.25 | 1.9 -> 4.6 | 28.7 -> 38.2 (+33 %) | 1.35 -> 2.95 s |
| MG | `boss_hmg` (was `hmg_roof`) | supreme_command (armored_car), 2 mounts | 1 round a second (B.6) | 8.3/s x 25, 1.4 s change | 8.8 -> 2.5 | 1.9 -> 11.5 | 29.2 -> 28.8 (-1 %) | 0 -> 3.15 s |
| MG | `mg_jeep` | scout_jeep (armored_car) | runs @ 8.3/s | 10/s x 30, 1.2 s change | 7.7 -> 6.7 | 3.7 -> 7.3 | 48.9 -> 48.7 (-0 %) | 1.35 -> 2.95 s |
| MG | `bunker_hmg` | mg_bunker / bulwark_post (armored_car) | runs @ 12.5/s | 12.5/s x 40, 1.2 s change | 11.6 -> 9.4 | 4.3 -> 9.2 | 84.8 -> 86.5 (+2 %) / 88.1 -> 86.5 (-2 %) | 0.90 -> 3.20 s |
| MG | `bunker_hmg_twin` | mg_bunker.twin (armored_car) | runs @ 22.2/s | 22.2/s x 70, 1.2 s change | 11.2 -> 6.5 | 5.4 -> 15.8 | 102.5 -> 102.8 (+0 %) | 0.50 -> 3.15 s |
| Cannon | `autocannon_40` | fortress_bastion (attack_helicopter), 2 mounts | 3 @ 7/s every 1.71 s | 5/s x 12, 1.5 s change | 51 -> 27.9 | 3.5 -> 6.4 | 53.6 -> 53.6 (+0 %) | 0.30 -> 2.40 s |

Rounds a second are the 60 s average in the measurement (turn-taking, changes and pauses
included); the cadence in a stream is the "Rhythm after" figure. A machine gun's old damage was
multiplied by 1.7 in flight (its pauses, `RunDamage`); a magazine's damage is its own, so the
light guns' per-round figures fell less than their round counts rose.

Whole vehicles, all mounts (DPS before -> after): attack helicopter 124 -> 131 (+5 %: its gun is
level, its missiles hit once more in the minute), scout helicopter 84 -> 86, armoured car 61 -> 61,
IFV 84 -> 85, BMPT 122 -> 123, main battle tank 86 -> 84 (-3 %), jeep 49 -> 49, heavy AA
376 -> 376, AA vehicle 160 -> 161, ZU-23 technical 195 -> 194, elite AA 230 -> 230, AA tower
470 -> 471, quad-flak tower 280 -> 281, C-RAM 120 -> 120, headquarters 660 -> 661, MG bunker
92 -> 92, twin bunker 109 -> 110, bulwark post 88 -> 86, gun turret 60 -> 63 (+5 %), guard tower
54 -> 55, hovercraft 33 -> 33, mega gunship 193 -> 192, behemoth 468 -> 468, airship 259 -> 259,
supreme command 29 -> 29, armoured train 241 -> 247 (+2 %). Against a helicopter: the armoured
car's and the IFV's coaxial gun 10 -> 13 (+26 %), the tank's machine guns 20 -> 17 (-16 %).

### B. Rules changed (the owner's request wins over round 6 where they clash)

1. **AA guns stream** (round 6: "AA guns keep their 8-16-round bursts"). A dedicated AA vehicle's
   or tower's gun is its main weapon, so its stream has the right of way (11C's rule for a ground
   vehicle's main magazine gun): the SAM goes first if it is lined up when the stream would start,
   else it fires in the magazine change.
2. **Machine guns fire magazines** (round 6: runs of 6-10 rounds and a 1 s pause). They still take
   turns: quiet 0.45 s after a heavy round, silent 0.3 s before a heavy weapon lined up is due,
   broken off when one stands ready, and two guns never fire in the same instant (all kept;
   `WeaponTurnTests` and `WeaponRhythmTests` pass unchanged).
3. **The main gun's stream first:** a secondary gun (the coaxial gun, now on a magazine) breaks off
   when the main magazine gun stands ready and is held off by it (`Vehicle.LeadWaitingAt`, as a
   machine gun does for a heavy weapon), and makes way when the main gun's change is nearly done.
   Without it the armoured car's and the IFV's cannons lost a quarter of their fire to their
   coaxial guns' 3 s magazines. Other secondary magazine guns no longer count as "about to fire"
   for each other (they would break each other's streams); they take turns by the handover.
4. **Secondary magazine guns share the gaps:** at the start of a stream a gun gives way to another
   secondary magazine gun, at least as strong (`SustainedDps`), that could fire and has been quiet
   longer (`QuieterGunReady`). The headquarters' two flak guns alternate magazine by magazine; its
   small coaxial gun only fills in (as before; letting it take full turns cost the flak 27 %). A
   tank's coaxial and roof guns share the gaps between main-gun rounds; which gets more depends on
   the target (the pair is within 5 % of before).
5. **SAMs beside a stream fire about a fifth less often in gun reach** (they wait for the change):
   AA vehicles' flak rounds are heavier to keep the vehicle's total (the table's +2 to +16 % on
   the gun is the SAM's loss). The missile entries are not touched (another lane).
6. **Bosses take turns fairly:** a boss's mounts still fire one mount a step, but a mount held off
   by another's round has the next step, the one waiting longest first (`BossTurn`,
   `WeaponState.HeldAt` / `WaitingSince`). 11C kept the mega gunship's guns because a gun firing
   every step would starve the mounts after it; now it cannot, so the boss guns stream too
   (rockets and missiles keep their rate: mega gunship rockets 92 -> 91 DPS). **Found on the way:**
   a boss's machine guns fired one round a second, not in runs (the boss rule returned before a
   run started, so every round was followed by the 1 s pause), since bosses have had machine guns.
   Their damage a second is kept (hence the light rounds: the hovercraft's CIWS 1.83, the mega
   gunship's minigun 2.25, `boss_hmg` 2.5); raising it would be a boss balance decision for the owner.
7. **New entries:** `hq_flak` (the headquarters' roof guns: `twin_30_flak` with 15.8 damage, since
   its two mounts alternate) and `boss_hmg` (`hmg_roof` with 2.5 damage for the supreme command and
   the armoured train, B.6). Both inherit everything else, so they look and sound the same.
8. **A turret magazine gun chases aircraft** for a tank with nothing on the ground, as its machine
   gun did (`CoaxAirTarget` takes `IsGun`).

### C. Kept as they were, and why

- **The jets** (`jet_cannon`, `gau_gatling`, `fighter_cannon`): already streams; the 1-1.4 s per
  pass waits for the owner's call on reach or the dive (11C). Movement and reach not touched.
- **Already on magazines** (11C): `autocannon_25`, `autocannon_30`, `twin_30_bmpt`, `gsh30k`,
  `gunship_25mm`.
- **`gunship_40mm`** (the sky gunship's Bofors, 3-round clips): a heavy HE gun there; as a magazine
  gun it would take the 25 mm stream's turns. **`agl_40`** (grenade launcher, BMPT and guard tower):
  lobbed heavy rounds; on the BMPT it would take the coaxial gun's turns. **`gun_57mm`**: the light
  tank's main gun (tank guns keep round 6's cadence). **Lasers** (`hel_beam`, `saucer_laser`): beams.
  **`drone_gun`**: no carrier.

### D. Left for the testing phase

- Air raids on a base and on an army (the AA streams stop when the target stops bearing, so
  against fast jets a stream may deliver less than the burst did): survival of attack helicopters
  and jets against the heavy AA, the ZU-23, the AA tower and the headquarters; C-RAM interceptions
  are the APS's, not the gun's (unchanged).
- Device performance: rounds and tracers a second rose about 1.5-2.5x for AA guns and machine guns
  and 5-9x for the bosses' guns (the C-RAM 11.5 -> 25 a second, the heavy AA 10 -> 18, the
  hovercraft 2 -> 18). `-mb-perf` in a big battle with several AA and a boss, and the
  `WeaponFired` event count.
- Campaign and Boss Rush winnability over seeds (the rhythm changed who fires when; the DPS is kept
  per weapon in the measurement, not in battle).
- The tank's coaxial/roof split (B.4) and the machine guns against helicopters (-16 % for the
  tank's pair, +26 % for the armoured car's and IFV's coaxial gun).
- The boss machine guns' damage (B.6): whether the owner wants them at the data's intended rate.

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

## 12F. Test feedback 2: aircraft attack AI (2026-09-29)

The owner's second play-test: a jet should be able to stand in the air and pour its machine gun
and missiles into enemy aircraft, then fly a loop and come back; the strafing pass wasted its
firepower. Then: the same for every similar vehicle. Since 11C the jets' cannons fire 20-25-round
streams from a 3.5-3.6 s magazine, but a pass kept the target on the nose for 1-1.4 s.

### A. The attack hold (aeroplanes)

New vehicle data `attackHold` (seconds, fixed-wing only; 0 or absent: plain strafing passes).
An aeroplane with one, its target in reach of its guns (95 %) and within 35 degrees of the nose,
holds its guns on the target for that long (`MovementSystem.AttackHold`):

- **A VTOL jet (the fighter) hovers.** It glides in to 60 % of its cannon's reach (about 21 m),
  stops, and turns on the spot at 1.4x its turn rate to keep the nose on the target. The owner
  asked for it to stand still: it does, fully (speed 0), since the F-35B/Harrier can.
- **Any other jet crawls.** It slows to a pace that brings it over the target just as the hold
  ends (15-50 % of its speed: 6.3-6.4 m/s for the attack jet and the A-10), nose on the target, then
  pulls through over it (the bombs fall on the way) and flies on. It never stops dead: it is no VTOL.
- **Then the loop.** Full power straight out (a hovering jet first turns 63 degrees away, to
  alternate sides, instead of flying through its target), out to 2.2 turn radii, round and back in,
  easing off from 1.5x its reach so it arrives at half speed; then the next hold (at least 1.5 s
  after the last). A cycle takes 7.5-8 s, 3.6-4 s of it firing (it was about 5 s with 1 s firing).
- **Inside a flak gun's reach (+6 m) it never hangs** (the old VTOL rule, now for all): the hold
  becomes a half-speed run, over the target in about a second. SAMs do not stop a hold.
- **A fast jet is chased, not held on.** Behind an aeroplane flying faster than 35 % of its own
  speed, the fighter matches the target's speed to keep it at 55 % of its cannon's reach on the
  nose. A target that gets out of 125 % of the reach ends a hold and the chase resumes.
- **Passes are flown to the guns' reach** (`AttackReach`: the shortest hull gun that can hit the
  target, else the main weapon). This changed only the fighter, whose passes were laid out for its
  60 m missile: it pulled through at 18 m and hovered at 48 m, beyond its 30 m cannon.

| Aircraft | `attackHold` | Before | After |
|---|---|---|---|
| fighter_jet (VTOL) | 4 s | strafing passes; a 6 s hover every 18 s at 48 m (cannon out of reach) | hovers at ~21 m for 4 s: AAM, cannon stream (3.5 s), wvr AAM; breaks away, loops, back |
| attack_jet | 3.6 s | 1 s passes at 27-32 m/s | crawls in at 6.4 m/s: rockets, bombs, then the cannon (2-2.5 s) as it comes over the target |
| tank_buster (A-10) | 4 s | 1.4 s passes | crawls in at 6.3 m/s: rockets, Maverick, gatling (up to 3.2 s) |
| strike_drone | 3.5 s | passes (8 missiles a minute) | slows to half speed (9.5 m/s) with its nose on the target: 12 missiles and 5 guided bombs a minute |
| recon_drone, bombers | 0 | passes | unchanged: their weapons' reloads (8-14 s) are longer than a loop, so a pass wastes nothing |
| sky_gunship, sky_fortress | 0 (orbit) | pylon turn | unchanged: the target stays in the side guns' arc and reach all the time; the 25 mm gun's short streams come from the fire rhythm (it takes turns with the 105 and 40 mm), not from the flight |

**The view** (`VehicleView`, flight pose): in the hold the nose dips at the target (a third of the
angle down to it, at most 12 degrees), the bob grows and the airframe rocks 2 degrees; a jet slowed
right down (hovering) turns without banking. Breaking away it climbs 5 m pitching up (up to 12
degrees) and comes back down nose first into the next run. `AirHoldShots` (editor, graphics)
renders six moments of a hold for the fighter, the attack jet and the A-10.

### B. Helicopters

A helicopter held at 90 % of its **main** weapon's reach: the attack helicopter at ~31 m with a
34 m ATGM, so its 26 m gun (nearly half its firepower) and 30 m rockets never fired unless the
target drove up to it. It now hovers at 90 % of the shortest reach of the weapons it faces the
target with (`HoverReach`: not the door guns, not an empty launcher or one that cannot hit this
target), never nearer than 60 % of the main weapon's: the attack helicopter and the elite at ~23 m,
the gunship helicopter at ~25 m (its 28 mm gun), the scout unchanged (its main gun is the shortest).
The Ka-52 keeps its standoff (by design since 9: outside the reach of anti-air it outranges); its
gun and rockets fire only when a target comes near. Helicopters already hover and turn to face
their target (unchanged).

### C. Fire rules

Unchanged (no `CombatSystem` change): no two weapons of a vehicle fire in the same instant, the
machine gun pauses round heavy rounds, and an aeroplane's cannon takes turns with its rockets,
missiles and bombs (11C). In a hold the heavy weapons go first (a 1 s rocket ripple, the bombs),
then the cannon streams; the fighter's cannon streams its whole magazine (3.5 s), the A-10's 3.2 s,
the attack jet's 2-2.5 s (its rockets and bombs take the first 1.5 s of the hold). Giving the
cannon the right of way was not needed.

### D. Measured

`AirAttackMeasure` (explicit, run by name): each aircraft attack-moved at a target that never
fires back or dies, from out of reach, 60 s, all mounts (so the approach, holds and loops count).
"Recommended" is with the per-round damage change in E (tried locally, not committed).

| Shooter (target) | DPS before | DPS after | after, recommended damage | Cannon rounds / 60 s | Longest cannon stream |
|---|---|---|---|---|---|
| attack_jet (main_battle_tank) | 146 | 474 | 197 (+35 %) | 80 → 317 | 1.05 → 2.55 s |
| tank_buster (main_battle_tank) | 277 | 573 | 383 (+38 %) | 218 → 510 | 1.40 → 3.20 s |
| fighter_jet (attack_helicopter) | 136 | 385 | 211 (+55 %) | 76 → 497 | 0.95 → 3.50 s |
| strike_drone (main_battle_tank) | 58 | 80 (+37 %) | 80 | - | - |
| attack_helicopter (ifv, from 50 m) | 65 | 122 (+88 %: its gun now fires, 0 → 164 rounds) | 122 | - | - |
| elite_attack_helicopter (ifv) | 92 | 167 | 167 | - | - |
| gunship_heli (ifv) | 140 | 147 | 147 | - | - |
| heavy_attack_heli, scout_heli, recon_drone, heavy_bomber, stealth_bomber, sky_gunship | 52, 82, 18, 178, 158, 320 | same | same | - | - |

The helicopters' "after" is what 11C's `FireRhythmMeasure` (which starts them inside gun reach)
already assumed: 122 against its 124 for the attack helicopter.

Real fights (`AirAttackMeasure.PrintRealFights`, open field, attack-move, seeds 1 and 2):

| Fight | Before | After | After, recommended damage |
|---|---|---|---|
| 2 fighters vs 2 attack helicopters | won 14 s, 81-91 % hp left | won 5-6 s, 97 % | won 7-11 s, 94-95 % |
| 2 fighters vs 2 attack jets | won 6-7 s | won 7-9 s | won 8 s |
| 2 fighters vs 2 fighters | won 6-11 s, 0-1 lost | won 16-17 s, 1 lost | won 15-17 s, 1 lost |
| 2 attack jets vs 3 MBT + IFV | won 32-35 s, 71-75 % hp | won 15 s, 87 % | won 23-24 s, 79-80 % |
| 2 attack jets vs 3 MBT + AA vehicle | won 35-36 s, 27-30 % | won 12 s, 36-48 % | lost 16 s (both jets) / won 26 s (one jet, 5 %) |
| A-10 vs 3 MBT + IFV | won 55-60 s, 43-49 % | won 24-28 s, 84-87 % | won 32-33 s, 78-81 % |
| A-10 vs 3 MBT + AA vehicle | won 44-51 s, 20-32 % | won 22-27 s, 23-36 % | won 30-34 s, 8-21 % |
| A-10 vs 2 MBT + 2 AA vehicles | lost 12-13 s | **won** 19-21 s, 10-27 % | lost 17 s |
| 2 attack helicopters vs 3 IFV | won 28-43 s | won 24 s, 93 % | same |
| 2 attack helicopters vs 2 IFV + AA vehicle | won 33 s, 52-58 % | won 24-25 s, 75-83 % | same |
| 2 gunship helicopters vs 3 MBT | won 51-52 s, untouched | won 30-31 s, 84-85 % (tank MGs now reach them) | same |
| 2 strike drones vs 3 MBT | won 65 s / lost 72 s | won 50-53 s, 32-42 % | same |
| AC-130 vs 3 IFV + AA vehicle | won 25 s | same | same |

### E. Fairness, and the weapon change it needs (not made: weapon entries are the fire-rhythm lane)

With the hold the jets' cannons fire 4x (attack jet), 2.3x (A-10) and 6.5x (fighter) as many rounds
a minute, and their per-round damage was set in 11C so that a 1 s pass did what the old burst did.
Without a change the jets' DPS is 2-3x and a lone A-10 beats two AA vehicles: air would dominate.
**Needed: per-round damage `jet_cannon` 64 → 22, `gau_gatling` 44 → 27, `fighter_cannon` 22 → 8**
(x0.34, x0.61, x0.36 of the current values; recompute from `AirAttackMeasure` if the magazines
change). With it: jets +35-55 % DPS over before (the magazines are used, as the owner asked),
columns without anti-air fall 30-45 % faster, and anti-air matters more than before (a jet
holding over a column with an AA vehicle often dies; one A-10 against two AA vehicles loses again).
The helicopters' and the strike drone's gains need no change: the helicopters get back the DPS the
11C rhythm was balanced for, and the drone gains 37 % (its missiles were idle through its loops).

### F. Left for the testing phase

- Apply the damage in E, then sweep seeds: `ConquestBattleTests`, `CounterTests` (air against AA,
  AA against air), air-heavy campaign missions and the boss missions with jets (bosses' flak turns
  the hold into a quick run).
- "2 attack jets vs a column + AA" split 1-1 over two seeds with the damage in E: sweep more seeds
  to see whether AA is now too strong against holding jets.
- Helicopters at gun reach take tank and IFV machine-gun fire (the gunship helicopter went from
  untouched to 15 % lost): helicopter loss rates in real matches.
- The fighter against enemy fighters took longer (6-11 s → 15-17 s, the chase of a circling jet);
  watch air-to-air in matches.
- The owner's feel: the crawl speed (6.3 m/s for the attack jets), the hover distance (21 m), the
  4 s hold and the 7.5-8 s loop; the pose on the device (nose dip, climb away).
- Performance: 2.3-6.5x more cannon rounds (tracers, `WeaponFired` events) a minute per jet.

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

## 12I. Play test 3: flashes that read wrong, longer plumes (2026-09-29)

The owner (on the build before 12A/12B) saw flashes off the barrels and missiles without matching fire. Checked
from the model files (every Muzzle_ node against the geometry on its firing line): the main guns' and launchers'
muzzle nodes sit on the tips (armoured car, tanks 0.00 m, mortar 0.08 m in, rocket technical at the pod's face).
What read wrong was how the flashes were drawn:

- A tank gun's 3.8-4.5 m core was centred on the muzzle, half of it back over the barrel ("in the middle of the
  gun"). It now sits 1.1 m x scale ahead of the tip, at 3.2-3.8 m.
- A tank's coax MG flashes at the mantlet, 2-4 m behind the gun's tip, and with 12D's streams it read as the main
  gun firing mid-barrel. Machine-gun cores are now 0.8-1.05 m (were 1.25-1.6), 0.3 m ahead of the muzzle.
- A mortar used the artillery flash (5-6 m, over the carrier seen from above): mortars flash at 0.55 of it.
- A rocket or missile launch was a gun-like 2.2-2.8 m core with a forward tongue: now a 1.0-1.3 m ignition at the
  tube's mouth and the backblast; the missile's own motor plume carries the fire.
- Every motor plume (12B) is 40 % longer and 20 % wider.
- The flash test now measures a flash along its barrel's line (on the line, never behind the tip, at most 2.5 m
  ahead) instead of on the tip.
- Ground SAMs were not slowed further: 10 % slower (46 -> 41 m/s) and "SAM beats jets" fails outright (the jets'
  flares decoy nearly every missile). A slower SAM needs flare resistance to go with it: handed to the balance pass
  (13C), which owns the missile-versus-flare measurements.
- The frozen-moment missile sheets show a gap between fast rockets and their flames; it comes from the sheet
  jumping straight to each moment (one long frame). In the game the frame is short and the flame sits on the tail.

## 13A. Prompt 11: compact HUD, alignment, short names, shields (2026-09-29)

The owner found the battle HUD covering too much of the battlefield, cards and rows out of line,
raw keys on screen, and the shields ugly. No game logic or balance data changed.

### A. The compact battle HUD

- **Two layouts, one code path.** Settings > Display > "HUD gọn trong trận" (`MatchSettings.CompactHud`,
  saved as `mb.compactHud`, on by default); off gives the full HUD of 10b G unchanged. `BattleHud` builds
  the compact controls where the structure differs (the stance switch, the icon toggles, the tower
  button, the selection strip, the collapsible boss bar, the tray's names) and puts `fc-hud--compact` on
  its kit root; the rest is Screens.uss rules under that class (the "prompt 11 A" block). `HudSpec.Compact`
  (null: the setting) lets the screenshots and checks show either.
- **Measured, not guessed.** `UiLayoutTests.TheCompactHudLeavesTheBattlefieldClear` rasterises (4 px cells)
  the union of every shown HUD element with a fill, an image, a border, a text or an icon (invisible
  touch targets do not count) and fails above 30 %. With the demo battles (a selection open in Conquest
  and Siege, a boss and a notice, the Defend wave preview): Conquest 27.5 %, boss 26.5 %, Siege 27.5 %,
  Defend 25.8 % at 16:9; 22.0, 21.2, 22.0 and 20.6 % at 20:9. The full HUD: 64.0, 59.6, 62.0, 50.7 % at
  16:9 and 52.6, 50.0, 50.7, 40.6 % at 20:9.
- **Faces smaller than 44 pt, targets not.** Every control is still a full 82 panel px target (44 pt, the
  kit's rule); where the drawn face is smaller (44 px faces on the minimap tools, pause, the rail, the
  objective rings), a transparent target surrounds it. The objectives' targets reach above and below the
  top strip through negative margins, so the strip stays 52 px high. The layout check now skips an
  element whose picking is off (the closed boss bar's part icons only show state; the bar itself is the
  target), since it cannot be tapped.
- **A1 minimap** 216 -> 132 px (40 % less a side, 63 % less area); the zoom buttons are gone (pinch
  zooms; the event stays for the full HUD); select-all and box-select are 44 px faces on its right-hand
  corners. The item strip moves up under them.
- **A2 commander.** Attack / Defend is one two-icon switch (a tap flips it; the side on is the text
  colour with a dark icon); Auto buy (a new cart icon) and Support are icon toggles: on is the text
  colour with a dark icon, off the field panel with a dimmed icon struck through, so the state reads
  without colour; tooltips say it in words. Pause now has both as the kit's switches (both layouts).
- **A3 tray** 160 -> 104 px (35 %). A card is its render (68 px), the CP and the short name on one line;
  holding a card (0.45 s, `Tap`'s new hold callback, which then fires no tap) shows its full name over
  the tray. The CP box is the points, the bar and the income; the supply penalty or the underdog's
  boost is a chip over the box, only while it applies. Cards are 108 px so ten of them and the box fit
  across 1280 px. Large text: no card width fits every short name on one line across 1280 px (the
  widest deployable, "Pháo bánh lốp", is 110 px at 22 px against at most 102), so in Large text the name
  may take two lines and the tray is 134 px (the full HUD's Large tray is 196).
- **A4 boss bar** half as wide (340 px closed): name, phase and the bar, and the parts as 20 px icons that
  show state only. A tap opens it at full size (640 px, the health in numbers, parts as full targets that
  order focus fire as before) for 6 s; tapping a part keeps it open, another tap closes it. Its calls are
  unchanged (`SetBoss` both overloads, `SetBossParts`, `BossPartTapped`, `SetBossHp`).
- **A5** the objective (or the score, or the waves) and the clock are one strip at the top centre: the
  goal and its count on one line over a thin bar, the clock at its end; the score strip is the two
  numbers in the sides' colours over their bars, the rings and the clock (the captions went to a
  tooltip).
- **A6 notices** (toasts, radio, alerts) sit in the column right under the strip (under the boss bar
  when there is one), in the small text size, at most 600 px wide, 2.5-3.5 s each whatever the caller
  asked (the full HUD's default went from 2.2 to 3 s too), queued (three at most, the next after 1.2 s
  if one waits; errors go straight up). The banner at the start is a smaller strip in the same place.
- **A7** the standing hint ("Quân ta tự chiến đấu · Chạm A B C...") shows in the player's first three
  matches only (`MatchSettings.StartHintMatches`, counted in `mb.hintMatches` when a real match starts;
  `HudSpec.StartHint`); the attack-move and box-select hints still show while those modes are on.
- **A8 selection** is one strip right above the tray on the right: the render with the count on it, the
  short name, the health bar and numbers, Advance / Stop / Back. The weapons line and "strong against /
  weak to" are only in the full HUD and on the detail page.
- **A10 safe area**: unchanged code (`ApplySafeArea`, `KitSafeArea`); the shots at 19.5:9 with a notch
  and 20:9 with a punch hole and the gesture bar show it.
- **For the balance agent (prompt 13)**: the selection strip has `BattleHud.SelectionExtras`, an empty,
  hidden row under the health bar for the ammo icons (C.9); every tray card has an empty
  `fc-hcard__badges` row in the picture's top-left corner. Both are documented in the class comments.

### B. Alignment, short names, raw keys

- **B1 short names**, at most 15 letters in both languages (`Strings.Short`, keys `short.<id>`, checked
  by `LocalisationScanTests.EveryCardHasAShortName` over vehicles, supports, items, elites, bosses,
  towers, their branches and the utility modules). A branch without its own short name reads as the
  branch's name alone. Used in the tray, the deck strips (home, army), the selection strip, compact
  cards (chapter unlocks, Boss Rush), and on any card whose full name needs more than two lines. Elites
  are the base's short name with "TN" (tinh nhuệ), like the listed PK and TT; `TN` and `HUD` joined the
  allow-list of names kept in Vietnamese. The table (full Vietnamese name and id, then the short names):

  | Vehicles | English | Vietnamese |
  | --- | --- | --- |
  | Xe trinh sát (`scout_jeep`) | Scout | Trinh sát |
  | Tăng hạng nhẹ (`light_tank`) | Light tank | Tăng nhẹ |
  | Tăng chủ lực (`main_battle_tank`) | Battle tank | Tăng chủ lực |
  | Tăng phun lửa (`flame_tank`) | Flame tank | Phun lửa |
  | Pháo tự hành (`artillery`) | SP gun | Pháo tự hành |
  | Pháo phản lực (`mlrs`) | Rockets | Phản lực |
  | Xe phòng không (`aa_vehicle`) | Anti-air | Phòng không |
  | Trực thăng tấn công (`attack_helicopter`) | Attack heli | Trực thăng |
  | Xe bọc thép (`armored_car`) | Armoured car | Bọc thép |
  | Pháo chống tăng (`tank_destroyer`) | Tank killer | Chống tăng |
  | Tăng hạng nặng (`heavy_tank`) | Heavy tank | Tăng nặng |
  | Tên lửa phòng không (`sam_launcher`) | SAM | Tên lửa PK |
  | Xe súng cối (`mortar_carrier`) | Mortar | Súng cối |
  | Bán tải rốc-két (`rocket_technical`) | Technical | Bán tải |
  | Trực thăng hạng nặng (`gunship_heli`) | Gunship | TT hỏa lực |
  | Trực thăng trinh sát (`scout_heli`) | Scout heli | TT trinh sát |
  | Máy bay cường kích (`attack_jet`) | Attack jet | Cường kích |
  | UAV tấn công (`strike_drone`) | Strike UAV | UAV tấn công |
  | Pháo phản lực nhiệt áp (`thermobaric_launcher`) | Thermobaric | Nhiệt áp |
  | Xe chiến đấu bộ binh (`ifv`) | IFV | Xe bộ binh |
  | Pháo tên lửa phòng không (`heavy_aa`) | Gun-SAM | PK hỗn hợp |
  | Siêu tăng Titan (`titan_tank`) | Titan | Siêu tăng |
  | Oanh tạc cơ hạng nặng (`heavy_bomber`) | Bomber | Oanh tạc cơ |
  | Máy bay ném bom tàng hình (`stealth_bomber`) | Stealth | Tàng hình |
  | Pháo đài bay (`sky_gunship`) | Sky gunship | Pháo đài bay |
  | Tăng hai nòng (`twin_tank`) | Twin tank | Hai nòng |
  | Tăng công thành (`siege_tank`) | Siege tank | Công thành |
  | Xe tên lửa chống tăng (`atgm_carrier`) | ATGM | Diệt tăng TL |
  | Pháo phản lực hạng nặng (`heavy_rocket_artillery`) | Heavy MLRS | Phản lực 300 |
  | Xe phóng tên lửa đạn đạo (`ballistic_launcher`) | Ballistic | Đạn đạo |
  | Xe công binh (`engineer_vehicle`) | Engineer | Công binh |
  | Xe tác chiến điện tử (`ew_jammer`) | Jammer | Gây nhiễu |
  | Xe phóng drone FPV (`fpv_carrier`) | FPV drones | Drone FPV |
  | Xe rải mìn (`mine_layer`) | Mine layer | Rải mìn |
  | Tiêm kích (`fighter_jet`) | Fighter | Tiêm kích |
  | Cường kích diệt tăng (`tank_buster`) | Tank buster | Diệt tăng |
  | UAV trinh sát (`recon_drone`) | Recon UAV | UAV do thám |
  | Ka-52 Cá sấu (`heavy_attack_heli`) | Ka-52 | Ka-52 |
  | Xe bom tự sát bọc thép (`vbied`) | Car bomb | Xe bom |
  | Bán tải ZU-23 (`zu23_technical`) | ZU-23 | ZU-23 |
  | Xe tạo khói (`smoke_carrier`) | Smoke car | Xe khói |
  | Xe phóng Lancet (`lancet_truck`) | Lancet | Lancet |
  | Xe phóng Shahed (`shahed_truck`) | Shahed | Shahed |
  | La-de phòng không (`iron_beam`) | Laser AA | La-de PK |
  | Xe súng điện từ (`railgun_truck`) | Railgun | Pháo điện từ |
  | Xe tăng rùa (`turtle_tank`) | Turtle | Xe rùa |
  | BMPT Terminator (`bmpt`) | BMPT | BMPT |
  | Xe công binh công trình (`sapper`) | Sapper | Công binh CT |
  | Xe ủi bọc thép (`armored_bulldozer`) | Bulldozer | Xe ủi |
  | Xe chỉ huy (`command_vehicle`) | Command | Xe chỉ huy |
  | Pháo bánh lốp diệt tăng (`wheeled_gun`) | Wheeled gun | Pháo bánh lốp |
  | Radar phản pháo (`counter_battery_radar`) | CB radar | Phản pháo |
  | Tên lửa phòng không tầm xa (`long_sam`) | Long SAM | SAM tầm xa |

  | Elites | English | Vietnamese |
  | --- | --- | --- |
  | Tăng chủ lực tinh nhuệ (`elite_mbt`) | Elite MBT | Tăng tinh nhuệ |
  | Tăng hạng nặng tinh nhuệ (`elite_heavy_tank`) | Elite heavy | Tăng nặng TN |
  | Pháo chống tăng tinh nhuệ (`elite_tank_destroyer`) | Elite TD | Chống tăng TN |
  | Trực thăng tinh nhuệ (`elite_attack_helicopter`) | Elite heli | Trực thăng TN |
  | Pháo phản lực tinh nhuệ (`elite_mlrs`) | Elite MLRS | Phản lực TN |
  | Phòng không tinh nhuệ (`elite_aa`) | Elite AA | Phòng không TN |
  | Xe bọc thép tinh nhuệ (`elite_apc`) | Elite EW | Bọc thép TN |
  | Grad tinh nhuệ (`elite_grad`) | Elite Grad | Grad TN |
  | Xe phóng drone FPV tinh nhuệ (`elite_fpv_carrier`) | Elite FPV | Drone FPV TN |
  | Cường kích tinh nhuệ (`elite_attack_jet`) | Elite jet | Cường kích TN |
  | Tên lửa phòng không tầm xa tinh nhuệ (`elite_long_sam`) | Elite SAM | SAM tầm xa TN |
  | Pháo tự hành tinh nhuệ (`elite_artillery`) | Elite SPG | Lựu pháo TN |

  | Bosses | English | Vietnamese |
  | --- | --- | --- |
  | Quái vật thép Behemoth (`behemoth`) | Behemoth | Behemoth |
  | Pháo đài băng (`mobile_fortress`) | Ice Fortress | Pháo đài băng |
  | Đoàn tàu thép (`armored_train`) | Iron Train | Đoàn tàu thép |
  | Chim sắt (`mega_gunship`) | Iron Bird | Chim sắt |
  | Tàu mẹ Tổ Ong (`drone_mothership`) | Hive Carrier | Tàu mẹ Tổ Ong |
  | Đoàn tàu Tận thế (`nuke_train`) | Doomsday | Tàu Tận thế |
  | Đĩa bay Bọ Bạc (`silver_bug`) | Silver Bug | Bọ Bạc |
  | Hỏa ngục Inferno (`behemoth_inferno`) | Inferno | Inferno |
  | Bão điện Tempest (`behemoth_tempest`) | Tempest | Tempest |
  | Tổ ong Hive (`fortress_hive`) | Hive | Tổ ong Hive |
  | Thành lũy Bastion (`fortress_bastion`) | Bastion | Bastion |
  | Pháo đường ray siêu nặng (`rail_supergun`) | Supergun | Pháo ray |
  | Máy khoan Sâu Đất (`earth_borer`) | Earth Worm | Sâu Đất |
  | Khí cầu chỉ huy (`command_airship`) | Airship | Khí cầu |
  | Tàu đệm khí đổ bộ (`landing_hovercraft`) | Hovercraft | Tàu đệm khí |
  | Tổng Tư Lệnh (`supreme_command`) | Supreme Cmdr | Tổng Tư Lệnh |
  | Bóng ma Spectre (`sky_fortress`) | Spectre | Spectre |

  | Towers and structures | English | Vietnamese |
  | --- | --- | --- |
  | Sở chỉ huy (`headquarters`) | HQ | Sở chỉ huy |
  | Siêu pháo (`super_gun`) | Super-gun | Siêu pháo |
  | Tháp căn cứ (`spawn_bastion`) | Bastion | Tháp căn cứ |
  | Pháo đài hạng nặng (`heavy_turret`) | Fortress | Pháo đài |
  | Tên lửa Patriot tầm xa (`missile_battery`) | Patriot | Patriot |
  | Tháp tên lửa chống tăng (`atgm_tower`) | ATGM tower | Tháp ATGM |
  | Tháp pháo (`gun_turret`) | Gun turret | Tháp pháo |
  | Tháp phòng không (`aa_turret`) | AA turret | Tháp PK |
  | Tháp gây nhiễu EW (`ew_tower`) | EW tower | Tháp EW |
  | Răng rồng (`dragons_teeth`) | Dragon's teeth | Răng rồng |
  | Bãi mìn (`minefield`) | Minefield | Bãi mìn |
  | Trạm C-RAM (`c_ram`) | C-RAM | C-RAM |
  | Ụ pháo ẩn (`gun_pit`) | Gun pit | Ụ pháo ẩn |
  | Nhà chứa drone (`drone_hangar`) | Drone hangar | Nhà chứa drone |
  | Dàn rốc-két (`rocket_turret`) | Rockets | Dàn rốc-két |
  | Lô cốt súng máy (`mg_bunker`) | MG bunker | Lô cốt |
  | Trận địa pháo (`artillery_emplacement`) | Artillery | Trận địa pháo |
  | Ụ súng tạm (`bulwark_post`) | Fallback post | Ụ súng tạm |
  | Tháp canh (`guard_tower`) | Guard tower | Tháp canh |
  | Xe tiếp tế (`supply_truck`) | Supply truck | Xe tiếp tế |
  | Trạm chỉ thị mục tiêu (`targeting_station`) | Fire control | Trạm chỉ thị |

  | Tower branches | English | Vietnamese |
  | --- | --- | --- |
  | Tháp quan sát (`guard_tower.watch`) | Watchtower | Tháp quan sát |
  | Ổ súng (`guard_tower.nest`) | Gun nest | Ổ súng |
  | Súng máy đôi (`mg_bunker.twin`) | Twin HMG | Súng máy đôi |
  | Lô cốt phun lửa (`mg_bunker.flame`) | Flame bunker | Lô cốt lửa |
  | Máy gây nhiễu drone (`ew_tower.drone`) | Drone jammer | Chống drone |
  | Máy đánh lừa radar (`ew_tower.spoof`) | Radar spoofer | Đánh lừa radar |
  | Chông sắt (`dragons_teeth.hedgehog`) | Hedgehogs | Chông sắt |
  | Rào thép gai (`dragons_teeth.wire`) | Wire and ditch | Rào thép gai |
  | Bãi mìn chống tăng (`minefield.at`) | AT field | Mìn chống tăng |
  | Bãi mìn rải (`minefield.scatter`) | Scatter field | Bãi mìn rải |
  | Nòng dài (`gun_turret.long`) | Long barrel | Nòng dài |
  | Nạp đạn tự động (`gun_turret.auto`) | Autoloader | Nạp tự động |
  | Tấn công từ trên (`atgm_tower.top`) | Top attack | Đánh từ trên |
  | Đa năng (`atgm_tower.multi`) | Multi-role | Đa năng |
  | Rốc-két chùm (`rocket_turret.cluster`) | Cluster | Rốc-két chùm |
  | Nhiệt áp (`rocket_turret.thermo`) | Thermobaric | Nhiệt áp |
  | Centurion (`c_ram.centurion`) | Centurion | Centurion |
  | Săn máy bay (`c_ram.hunter`) | Hunter | Săn máy bay |
  | Phục kích (`gun_pit.ambush`) | Ambush | Phục kích |
  | Hầm sâu (`gun_pit.deep`) | Deep pit | Hầm sâu |
  | Phản pháo (`artillery_emplacement.cb`) | Counter-fire | Phản pháo |
  | Tầm xa (`artillery_emplacement.ext`) | Long range | Tầm xa |
  | PAC-3 (`missile_battery.pac3`) | PAC-3 | PAC-3 |
  | Radar tầm xa (`missile_battery.lrr`) | Long radar | Radar tầm xa |
  | Nhà chứa Lancet (`drone_hangar.lancet`) | Lancet hangar | Lancet |
  | Bầy đàn (`drone_hangar.swarm`) | Swarm | Bầy đàn |
  | Pháo bờ biển (`heavy_turret.coastal`) | Coastal gun | Pháo bờ biển |
  | Pháo đài thép (`heavy_turret.bastion`) | Bastion | Pháo đài thép |
  | Tháp cao xạ (`aa_turret.flak`) | Flak tower | Tháp cao xạ |
  | Trạm tên lửa (`aa_turret.sam`) | SAM post | Trạm tên lửa |

  | Utility modules | English | Vietnamese |
  | --- | --- | --- |
  | Xưởng sửa chữa (`repair_bay`) | Repair bay | Xưởng sửa chữa |
  | Kho đạn (`ammo_depot`) | Ammo depot | Kho đạn |
  | Sân bay dã chiến (`airfield`) | Airfield | Sân bay |
  | Trạm hậu cần (`logistics_station`) | Logistics | Trạm hậu cần |
  | Trạm radar (`radar_station`) | Radar | Trạm radar |

  | Fire support | English | Vietnamese |
  | --- | --- | --- |
  | Pháo kích (`artillery_barrage`) | Barrage | Pháo kích |
  | Không kích (`airstrike`) | Airstrike | Không kích |
  | Tên lửa hành trình (`cruise_missile`) | Cruise | Hành trình |
  | Màn khói (`smoke_screen`) | Smoke | Màn khói |
  | Sửa chữa (`repair_drop`) | Repair | Sửa chữa |
  | Bom napalm (`napalm_strike`) | Napalm | Napalm |
  | UAV quét (`uav_scan`) | UAV scan | UAV quét |
  | Mìn rải từ xa (`remote_mines`) | Mines | Rải mìn |
  | Tháp dã chiến (`field_tower`) | Tower | Tháp dã chiến |
  | Đòn SEAD (`sead_strike`) | SEAD | SEAD |

  | Items | English | Vietnamese |
  | --- | --- | --- |
  | Bom MOAB (`moab`) | MOAB | MOAB |
  | Bom chùm (`cluster_strike`) | Cluster | Bom chùm |
  | Tiếp viện thả dù (`reinforcements`) | Airdrop | Thả dù |
  | Sửa chữa toàn quân (`field_repair`) | Field repair | Sửa toàn quân |
  | Bom EMP (`emp_blast`) | EMP | EMP |
  | Khiên vòm (`shield_dome`) | Shield | Khiên vòm |
  | Pháo đài bay yểm trợ (`gunship_support`) | Gunship | Pháo đài bay |

- **B2 two-line name areas.** `Kit.FixedLines(label, lines, fallback)` holds a label at exactly that many
  lines of its own type (measured from the font, so it follows the text size), and swaps in the short
  name when the full one needs more; vehicle, tower, support and gear cards use two lines, the compact
  tray one (two in Large text). Grids and deck strips stretch their cards to the row's height, and a
  gear slot's card fills its cell, so an empty or locked card is as tall as its neighbours.
- **B3 scan.** Every rebuilt screen was looked at in the screenshots (16:9 and the other shapes); the
  misalignments found were all card name heights (the level line moving with one- to three-line names,
  locked tower cards taller than the rest, an empty gear slot shorter than a worn one). What is left for
  prompt 14: the towers' class icons (they use vehicle icons).
- **B4 raw keys and placeholders.** `Strings.Card` of a tower branch id ("aa_turret.flak") fell through
  to `support.<id>` and showed the raw key; it now reads "tower · branch". Boss Rush's "{0} trùm liên
  tiếp" is formatted everywhere in this build (home's mode list and Operations). The new
  `LocalisationScanTests.EveryScreenShowsWordsNotKeys` builds every menu and battle screen with the demo
  profile in both languages and fails on any text or tooltip with a `{0}` placeholder or a table key
  ("support.x", "unit.x", "branch.x" and the other key prefixes).
- **B5** `UiLayoutTests.CardsInARowLineUp`: on home, the deck, towers, equipment, a chapter, Operations
  and the battle tray (compact and full), at the four shapes in Normal and Large text, the cards of one
  row share their top and height, and the picture, the cost box (by its top right), the name area (with
  its height) and the level sit at the same place on each.

### C. Shields

- **One shader** (`Resources/Shaders/Shield.shader`, `MachineBrigade/Shield`) and one view helper
  (`Game/Effects/ShieldVisual.cs`: `SetSide`, `Hit`, `Flicker`, `Raise`, `Lower`, `Collapse`, `Tick`) for every
  shield: the fortress dome of Siege and Defend (exactly the sim's `DomeRadius`, 0.5 of it high, as before),
  the Shield Dome item (a dome of its radius at its point for its duration), vehicle shields (a hex bubble
  round the hull for the boss and elite shield skills: the Tempest, the Hive Carrier, the Silver Bug,
  `elite_shield`, and the item's per-vehicle shield), siege objectives that cannot be hurt yet (a small dome
  sized to the model), and the gear barriers (Aegis Barrier, Shared Shield: a faint bubble for 0.8 s when
  it takes a hit, a shatter when it breaks). The boss's "hull shielded" part lock has no shield: a bubble
  would say the parts inside cannot be hit, which is wrong.
- **The look.** A skin of hexagonal tiles, bright only towards the rim (fresnel), the middle almost clear so
  what is inside reads; a seam where a dome meets the ground. The tiles are real geometry, a geodesic sphere
  with a small fan of triangles per tile (hexagons and 12 pentagons, no stretching at the poles), so the
  per-tile effects (ripple, flicker, shatter) are worked per vertex and the pixel shader stays cheap. About
  4-5 m tiles on domes: the fortress dome (R about 60 m) is level 4 (10.7k vertices, 9.2k triangles), 3 on
  Low; the item dome level 2 (631 / 540), a bubble level 2 (1122 / 960); built once and cached.
- **Premultiplied blending, not additive**: additive red over green ground turned yellow and peach after
  the ACES tonemapper; premultiplied, only the bright rim hides a little of what is behind (at most 30 %).
- **Ripples**: up to four a shield at once, a flash where the round lands and a ring of lit tiles running
  out from it, from `ProjectileImpact`, `StrikeImpact` and `Damaged` events; kept in the shield's own space
  (they move with a moving vehicle); on a dome the hit is projected straight up onto the skin, on a bubble
  onto the side facing the camera; a burst on one spot is one ripple.
- **Flicker**: the fortress dome more as its generators lose health, a burst when one is hit, a 1.1 s surge
  when one falls while others stand; a boss bubble with its shield part's damage; the item dome in its last
  1.2 s, a vehicle shield in its last second.
- **Collapse** (0.9 s): a flare, then the tiles break away one by one, shrink and fly off. The dome's fall no
  longer uses the Ultimate fireball blast (a field giving way is not fire): the shatter, two shockwave rings
  (one in the side's colour, one white), a milder shake and flash (`EffectsDirector.Jolt`). The generators'
  own explosions still come from the sim.
- **Colours** by owner against the player: ours blue (0.24, 0.66, 1), the enemy's red-orange (1, 0.2, 0.05);
  colour-blind mode (0.22, 0.56, 1) against orange (1, 0.56, 0.08). The owner is the fortress's defender
  (dome, objectives), the team that used the item, the vehicle's own team. The item's ground ring takes its
  side's colour too. Under its own side's item dome a vehicle draws no bubble of its own (the dome is its
  shield); driving out, the bubble shows (the sim's shield goes with the vehicle).
- **Few particles**: only the existing shockwave rings (two when the fortress dome falls, one when the item
  dome goes up). **Low graphics** (`MatchSettings.Tier`, a `multi_compile_local` keyword, `_SHIELD_LITE`,
  because the materials are made at run time): no lattice, ripples or shimmer; the rim, the seam, the
  flicker, a whole-skin flash on a hit and the shatter stay, one tile level fewer. Two shared materials
  (full and Low) and a property block per shield; the shield's clock is a script property (the shots are
  deterministic); the hash avoids `sin()` for precision on phone GPUs. `Prewarm` draws a tiny shield for
  0.3 s behind the loading screen, so Vulkan does not stall the first time one appears.
- **View only**: no sim rule, size or balance changed (the dome's size is the sim's).
- Pictures: `Docs/art/shields/shields.png` (twelve panels: the enemy's dome, ours, ours at battle zoom,
  ripples of three ages, flicker, the collapse at three moments, bubbles, the item dome hit, objective
  shields, Low) and `Docs/art/shields/in-game-*.png` from real Siege and Defend matches with the dome coming
  down (`MachineBrigade.Editor.ShieldShots.Shields`, `ShieldPlayShots.Run`). `ShieldVisualTests` (four fast
  tests). Front and back faces are told apart with `SV_IsFrontFace`, checked in the editor on D3D11 only
  (a phone getting it wrong would draw both faces alike, which is harmless). Smoke behind the dome's rim is
  darkened a little (the shield draws after the particles, premultiplied).
- **To measure**: the frame rate of the heaviest battle on Low graphics on a real phone, before and after
  (the old dome was 637 vertices and 1152 triangles on the particle shader; the new shader does a little
  more a pixel, the same screen area; the lattice is off on Low).

### D. Checks and pictures

- Tests run (targeted, as the owner asked): `UiLayoutTests` (all strict checks green, with the new HUD
  and card checks), `LocalisationScanTests`, `UiThemeTests`, `UiLanguageTests`, `ShieldVisualTests`;
  PlaySmoke (menu 15 s, Conquest, Siege and Boss Rush 30 s each): 0 errors.
- New screenshots in `Docs/ui-screens/`: `battle-hud-score` (Conquest), `battle-hud-mission` (a boss),
  `battle-hud-boss-open` (its bar opened), `battle-hud-siege`, `battle-hud-defend`, `battle-hud-waves` at
  the four shapes, Large text and English for the main ones, and `battle-hud-score-full` /
  `battle-hud-mission-full` (the full HUD) at 16:9 and 20:9. Every other screen was shot again (cards
  changed across the menus).
- **To measure** (testing phase, a real phone): the frame rate of the heaviest battle on Low graphics
  before and after the shield change, and the compact HUD's cost against the full one.

## 13B. Prompt 12: stuck vehicles in bases (2026-09-29)

Diagnosed first, then fixed at the causes; each cause has a test written to fail before its fix
(`StuckCauseTests`, checked against d916258).

**Tools.** `StuckWatch` (sim): a ground vehicle with somewhere to go that moves less than 2.5 m in 8 s is
recorded with map, mode, seed, tick, side, place, goal, lane flags, what is within 10 m and why
(embedded, no path, goal unreachable, stale route, off route, gate wait, yield wait, blocked by a friend,
defence, enemy or wall). Its JSON carries seed, data hashes and the player's journal for a replay;
`StuckBatch.One` replays and traces a case. `StuckReporter` keeps it in the editor and development
builds (or `-mb-stuck`), writing to `persistentDataPath/stuck/`. Batches (`StuckBatch.Siege`, `.Modes`,
Explicit): by the owner's rule a small set (Siege on all 20 maps, Defend, Endless and Weekly on six,
two seeds, loadouts light, full and obstacles through `BaseSystem.LoadoutFor`), 76 battles, 6 min.
`Tools/maps/stuck_report.py` writes heatmaps, the ten worst spots and tables to `Docs/stuck-report/`.

**Causes found** (the spec's list): the 10 m sally ports took all two-way traffic of Defend, Endless
and Weekly (the worst spots); every siege fortress had no route three cells wide for the big hulls with
the gates shut and hardpoints full (0 of 20 passed), and the keep's drop zone led out through one- and
two-cell gaps; a tower landing on vehicles left them on blocked ground; routes planned across ground
closed since (a tower raised) were driven into it; goals behind a wall or in a sealed pocket failed the
search and were re-sent for ever, and group slots spread over both sides of a wall; two hulls given each
other's slot queued behind each other; a detour steered a titan into the wall; the keep's guardian and
elites spawned in a pocket. Not causes: lane map or grid not updated after a fall (they are), the lane
map disagreeing with the grid.

**Fixes.** NavGrid regions: goals resolve to the start's region, slots stay on the group's side of a
wall; slots untangled (groups up to 12); no queueing behind a hull queued behind us or oncoming;
head-on in the open settled after 1 s by a step aside; detours keep off walls; routes across newly
closed ground re-planned; a landing tower puts vehicles off its ground; spawns avoid sealed pockets;
the guardian and elites spawn with room. Map data: double 18 m sally ports and keep gate, a clear yard,
clear gateway mouths and main-gate roads, and `open_wide` (the builder removes clutter until, with every
gate shut and every hardpoint holding the biggest tower, every drop zone and gateway mouth is reached
three cells wide and every objective from within 15 m; it took 9 fuel depots, 1 ammunition dump, 8 of
554 tower hardpoints and some wrecks, on the classic fortresses 4 towers). Swamp's causeways and main
bridges 20 m, its centre opened. `Tools/maps/check_access.py` and `MapConnectivityTests` check all 40
files: all pass. Maps were rebuilt with the campaign file of 394c762 so every Conquest and Sandbox file
but Swamp's is unchanged (Rustyard's committed data was stale against today's c4m06).

**Safety net** (`MovementSystem.Rescue`): after 10 s without headway, off blocked ground ("place"),
else through its own side's hulls for 4 s and re-planned ("ghost"), then moved on along its route
("hop"); every activation logged and in the report.

**Numbers** (76 battles each; episodes of 8 s or more / over 10 s / over 20 s / worst):
before 2076 / 1285 / 174 / 214 s; after, net off 705 / 378 / 9 / 34 s; after, net on 578 / 265 / 4 /
28 s with 168 activations (162 ghost, 6 hop). Siege over 10 s: 329 -> 117 (net off) -> 87. On the
branch before merging prompts 13-14 the net-off run was 574 / 286. A five-map Siege sample on the final
code: 6 over 10 s, 5 activations (Swamp). Episodes over 10 s remain (queues in heavy traffic), so the
spec's "none over 10 s" is not reached; nothing is stuck for good. Replay tests pass. Tick (quick run,
48 enemies, desktop ms, mean / p99): lead 0.74-0.75 / 1.9-2.2, this branch 0.72-0.77 / 1.9-3.2 (the
untangling unbounded had doubled the p99; limited to groups of 12).

**Full sweep for the testing phase:** `StuckBatch` on all 20 maps for every mode (`MB_STUCK_MAPS`,
`MB_STUCK_MODES=Siege,Defend,Endless,Weekly`), `MB_STUCK_SEEDS=1,2,3,4,5`, every loadout on every map,
net on and off; `TickBudgetTests` in full; `SiegeBalanceTests`, `ModeEndingTests` and the Swamp and
Coral Isles battles (the fortress changes touch balance).

## 13C. Prompt 13: combat-value balance, ammo, modes, AI difficulty (2026-09-29)

One balance pass in the owner's order A → I. The owner's rule on test time wins over the brief's "5 seeds
for everything": part A runs each standard scenario once on a fixed seed; the few decisions that were close
were checked on two more seeds, and that is said where it was done. Everything else is listed for the testing
phase (13C.Z). The tables are in `Docs/COMBAT_VALUE.md` (generated) and the raw files in `Docs/balance/`.

### A. Measuring real combat value

**A.1 The theoretical table.** `FirePower.Sustained` (Sim, new) is what the design document's damage table,
the detail screen's DPS and the measurement's theoretical table now read: a salvo's rounds over its cooldown, a
magazine over its change, a launcher's rounds per load over the time to fire them *plus* the reload in place,
and (after C) an aircraft's stores per full load plus the time to take them on again at the holding pattern's
full rate. Before, `UnitStats.Dps` was volley / cycle, so every launcher counted as never running dry (the MLRS
90 → 79 DPS on light, the siege tank's 169 → 138 on structures). The design document's "attack jet 1,074 DPS
on heavy" came from the cannon at 64 damage (before 12F) streaming without end; the table now says 414 (the
cannon at 22), but that is still a gun firing whenever it can. The real figure comes from A.2: **131 DPS on
heavy for the attack jet, 280 for the A-10** in the tanks scenario (the brief's "about 100 and 190" came from
11C's one-pass measurement). The corrected table and the real DPS are both in `COMBAT_VALUE.md`.

**A.2-A.4 The measurement** (`CombatValueMeasure.MeasureTheRoster`, EditMode, explicit, `MB_BALANCE=1`):

- Each buyable vehicle, rank 1 and no equipment, in a group of about 14 CP of its kind (1 to 5 vehicles:
  equal-CP groups as `CounterTests` does, so a 3 CP car is not measured alone against two battle tanks), led by
  the tactical AI (so artillery stands off, empty launchers stop to reload, aircraft attack as they do in play),
  attacks a reference group placed 85 m (ground) or 135 m (aircraft) away, from arrival, for 90 s.
- The groups: **light** (3 armoured cars, a jeep), **tanks** (2 battle tanks), **fort** (a gun turret and an MG
  bunker), **air** (an attack helicopter and an attack jet), and **light+AA, tanks+AA, fort+AA** (an AA vehicle
  added; an AA tower at the fort). A destroyed group comes back 3 s later as another wave, so a strong unit is not
  left idle. Aircraft, helicopters and every launcher with limited ammunition also fight **long**: two battle
  tanks, two armoured cars and an AA vehicle for 4 minutes, so empty-and-reload cycles count.
- Everyone sees everyone (`RevealAll`: artillery has no spotter of its own there), except when the shooter is
  stealthy (the point of a stealth bomber is not being seen).
- Recorded per vehicle and group: the damage it really did (never more than its victim had left: a 700 blast on a
  300 HP car counts 300) by armour, the share of its time with a target in reach (on target), its survival, the
  time to destroy the first group, the real damage a second, and the **combat value per CP = damage × (1 + share
  of the time alive) / 2 / CP**. The survival factor rewards a unit that is still there for the next fight
  without counting its lifetime twice (the damage already stops when it dies); (1 + share) / 2 runs from 0.5
  (killed at once) to 1 (alive at the end).
- "Ground value" (the mean over the six ground groups) is the like-for-like figure for everything that fights
  the ground; anti-air is judged on the air group; support vehicles (engineer, jammer, radar, command vehicle)
  do nothing measurable here and are judged by what they do for others (E).
- The whole roster (52 vehicles, 263 runs + 26 long ones) takes 8 s: the sim is fast when the battlefield is small.
  `MB_CV_SEEDS=13,14,15` averages seeds, `MB_CV_BALANCE=<file>` measures another balance file (the before
  column), `MB_CV_ONLY=a,b` a few vehicles.

**A.5 Blast radii.** Checked against the data before 12C (`a455751`): no weapon's `splash`, no support's radius
and no vehicle's death blast changed; 12C touched only `Game/Effects`, the editor and tests. Nothing to restore.

**A.6 The earlier changes, measured.**

- *Fire burning 20 % shorter (12A):* view only. The simulation has no burning-ground zones; fire damage is the
  Burn status on vehicles, unchanged. The flame tank's, the flame bunker's and the Inferno's damage did not move.
- *Slower missiles (11C, 12B):* `MissileHitMeasure.PrintMissileHitRates` fires each launcher at a target that
  cannot die and drops flares (and, for the tanks, an Iron Beam's protection) for 90 s:

  | Launcher → target | Missile, speed | Hit rate now | At the 11C speed |
  |---|---|---|---|
  | AA vehicle → attack jet (flares) | `sam` 40 | 86 % | |
  | SAM launcher → attack jet | `sam_long` 46 | 77 % | |
  | missile battery → attack jet | `sam_battery` 46 | 92 % | |
  | long-range SAM → attack jet | `sam_48n6` 62 | 91 % | |
  | fighter → attack jet | `air_to_air` 34 | 100 % | 94 % (48) |
  | fighter → attack helicopter | `wvr_aam` 34 | 71 % | 79 % (48) |
  | ATGM carrier → battle tank + Iron Beam | `atgm_heavy` 19 | 45 % (11 of 22 shot down) | 45 % (24) |
  | ATGM carrier → battle tank, no protection | `atgm_heavy` 19 | 91 % | 91 % |
  | attack helicopter → tank + Iron Beam | `heli_atgm` 21 | 6 % (16 of 18 shot down) | 6 % (30) |
  | Ka-52 → tank + Iron Beam | `vikhr` 24 | 42 % | 42 % (34) |

  Active protection intercepts at impact, whatever the speed, so it takes the same share. Flares take a few
  points more of the slower air-to-air missiles (a longer flight overlaps a flare more often). The Iron Beam
  against the attack helicopter's single Hellfires (6 %) is its one strong counter; salvos of two get through.
- *Long streams (12D) and the new fighter AI (12F):* measured there at unchanged DPS per weapon; the combat
  value now includes them (the fighter's on-target share against aircraft is 76 %, its survival 28 s against the
  air group).

**The owner's slower SAMs (asked for during this pass).** Ground SAMs 10 % slower: `sam` 40 → 36 m/s,
`sam_long` 46 → 41, `sam_battery` 46 → 41 (its PAC-3 and long-range branches inherit it), `sam_48n6` 62 → 56.
Alone that breaks "SAM beats jets" (the lead's finding, reproduced: seed 1 lost, the jets untouched). So a guided
missile now has a seeker: **`flareResist`**, the share of flare decoys it sees through (a flare's pull, 35 %,
times 1 − resist; one roll per missile, the random draw unchanged so replays stay the same). Radar-guided SAMs
see through most flares, as they do: Buk 0.8, Patriot and S-400 0.85; the SHORAD/Stinger dart 0.5 (a two-colour
seeker). Air-to-air missiles and the helicopters' MANPADS keep 0 (the fighter is already the strongest thing in
the air, E). Measured (`PrintSamAgainstJets`, 4 seeds each):

| | SAM → attack jet hit rate | 3 SAM launchers vs 2 attack jets | 3 AA vehicles vs 2 attack helicopters |
|---|---|---|---|
| before (11C speeds) | 77 % | 4/4 won | 4/4 |
| 10 % slower | 77 % | 3/4 (seed 1 lost, jets untouched) | 4/4 |
| 10 % slower + seekers (shipped) | 92 % | 4/4 | 4/4 |

Found on the way: one A-10 (18 CP) beats two SAM launchers (10 CP) in 6 s on every seed, before and after; it is
an E question (SAM value per CP), not a speed one.

### B. Damage a round by the real weapon

**B.1 Data.** Every weapon has `real` (the real weapon: "2A42 30 mm", "9M133 Kornet", "FAB-500 (500 kg)"),
`family` and `size` (the calibre in mm; for missiles the missile's kg, for bombs, drones and AA missiles the
warhead's kg). Families: `mg`, `autocannon` (20-57 mm, AA guns included), `grenade`, `tank_gun`, `howitzer`,
`mortar`, `rocket`, `atgm`, `aa_missile`, `bomb`, `cruise`, `ballistic`, `drone`, and scales of their own for
`flame`, `laser`, `railgun`, `melee`, `special`. The weapon line reads "id, real name, family, size, ...".

**B.2 The scale** (per round, before armour), as the owner's reference with one number chosen in each band:

| Family | Size → damage |
|---|---|
| machine guns | 7.62 mm 5.5 · 12.7 mm 9.5 |
| autocannons | 20 mm 13 · 23 mm 14 · 25 mm 17 · 30 mm 22 · 35 mm 25 · 40 mm 30 · 57 mm 70 |
| grenade launcher | 40 mm 26 (low velocity, below the 40 mm cannon) |
| tank and direct guns | 57 mm 70 · 76 mm 120 · 105 mm 200 · 120 mm 240 · 125 mm 250 · 140 mm 280 · 152 mm 320 |
| howitzers | 105 mm 200 · 152/155 mm 320 · 203 mm 420 |
| mortars | 120 mm 150 · 240 mm 450 |
| rockets | 70 mm 28 · 80 mm 32 · 107 mm 45 · 122 mm 57 · 220 mm (TOS) 97 · 227 mm 100 · 300 mm 140 |
| ATGM / AGM (missile kg) | Griffin, MAM-L 180 · TOW-2, Konkurs 190 · Kornet, Ataka 230 · Vikhr, Hellfire 250 · Maverick 345 · Kh-29 360 |
| AA missiles (warhead kg) | Igla 150 · Stinger / SHORAD 170 · R-60 175 · AIM-9 220 · AIM-120 280 · Buk 320 · Patriot PAC-2 340 · PAC-3 360 · S-400 48N6 600 |
| bombs (kg) | 110 200 · 250 300 · 500 400 · 900 (car bomb) 700 · 907 (JDAM) 850 |
| cruise / ballistic | Kh-101 360 · JASSM 390 · Iskander 600 |
| drones (warhead kg) | FPV 140 · Lancet 240 · Shahed 320 |

Choices: the AA missiles' scale is by warhead, so the long-range 48N6 keeps its 600 one-shot (its identity);
PAC-3 is counted a little above PAC-2 (hit-to-kill) so the branch stays the upgrade; the thermobaric 220 mm sits
just under the 227 mm. The car bomb is a 900 kg charge in the bomb family, just under the JDAM.

**B.3 Inversions fixed** (all 142 weapons were redone; the brief's list):

| Brief's example | Before | Now |
|---|---|---|
| 105 mm of the tank destroyer / wheeled gun / gun pit above the 120 mm | 357 / 300 / 290 vs 200 | re-gunned (B.5): 125 mm 250, 120 mm 240, 120 mm 240; the battle tank's 120 mm 240 |
| 30 mm: Su-25 / Mi-24 GSh-30K / GAU-8 / BMPT / IFV | 22 (after 12F) / 15.8 / 27 / 21.3 / 22.4 | 22 on all five |
| Ka-52 23 mm vs 12.7 mm; 35 mm flak below the ZU-23 | 6.2; 6.85 vs 9.7 | 23 mm 14; 35 mm 25, ZU-23 14 |
| 25 mm: armoured car / gunship | 15.5 / 12.4 | 17 / 17 |
| 155 mm SP gun vs the gunship's 105 mm | 171 vs 347 | 320 vs 200 |
| S-8 80 mm vs helicopter rockets; elite Grad, elite MLRS | 22 vs 40; 19, 13 | S-8 32, Hydra 28; Grad 57, GMLRS 100 |
| elite Apache's Hellfire vs the Apache's | 128 vs 256 | 250 and 250 |
| the UAV's small bomb vs the Su-25's FAB | 297 vs 351 | GBU-39 200, FAB-250 300 |

Also: boss guns now fire the calibre's rounds (12D had cut them to 1.8-6 a round to keep the bosses' damage a
second: the hovercraft's AK-630 22, the mega gunship's M230 22, `boss_hmg` 9.5): the same real weapon hits the
same everywhere, and the boss's damage a second is kept by shorter bursts.

**B.4 Damage a second kept** (`bapply.py` in the session scratchpad, reproducible from `bplan.py`): for each
weapon the new round's damage, then
- single shots: the cooldown by the same factor (the battle tank's 120 mm 4.57 → 5.48 s, the SP gun 7.14 →
  13.4 s with its reload 28 → 52 s, the tank destroyer 5.57 → 3.9 s);
- salvos: the salvo's size first (the Apache's Hydras 8 × 40 → 11 × 28, the Su-25's S-8s 20 × 22 → 14 × 32,
  the A-10's 8 × 61 → 17 × 28, the MLRS 6 × 80 → 5 × 100), then the cooldown for the rest;
- magazines: the stream kept about as long as before (the owner likes long streams, 12D), the change 0.8-4.5 s,
  the cadence as near the old as that allows (the Gepard's 35 mm: 50 at 18/s → 23 at 10/s, change 1.2 → 4.3 s;
  the M230: 30 at 10/s → 22 at 9/s, change 4.3 s; C-RAM: 100 at 33/s → 23 at 8/s);
- launchers: the cycle and the reload in place scaled together.
Every weapon's `FirePower.Sustained` is within 1 % of before. `roundWeight` keeps a round from looking or
sounding lighter than before (the owner's rule); it is dropped where the damage now reaches it.

**B.5 Re-gunned rather than weakened:** the tank destroyer fires a 125 mm (2A75, as on the 2S25 Sprut) and its
elite a 125 mm APFSDS, the wheeled gun a 120 mm (Centauro II), the gun pit a dug-in 120 mm. Their guide lines and
notes say so; the weapon ids stay (saves, equipment).

**B.6 Autocannon rounds.** A kinetic weapon of the autocannon family (20-57 mm) uses the damage table's new
**Autocannon row: light 1.0, heavy 0.38, air 0.3, structure 0.4** (a machine gun's kinetic: 0.25 / 0.3 / 0.3; AP:
1.0 on heavy). A new damage type was rejected: resistance stats are indexed by damage type in saved equipment.
`DamageTable.Multiplier(weapon, armour)` is used wherever the weapon is known (targeting, the overkill check, a
hit's damage through `HitInfo.Weapon`, boss parts, the design document). The GAU-8 and the jets' cannons keep
their armour-piercing rounds (depleted uranium / API: they are tank-busting guns), and the AA guns their flak.

**B.7 Tests** (`CalibreTests`): damage never falls as the size rises within a family; the same real weapon (its
name without the variant note in brackets) hits the same on every carrier; the reference scale's bands hold;
every weapon that fires has a family, size and name; autocannon rounds sit between a machine gun's and a tank
gun's on armour.

**What B did to combat value** (three seeds, 13-15, before and after B, ground value): most vehicles within
±10 %. The movers, and why: the light tank −24 %, flame tank −18 %, bulldozer −13 %, sapper −13 %: the *reference*
light group's armoured cars now hit heavy armour 52 % harder with their 25 mm (B.6), so heavy vehicles in that
fight live shorter (their own damage a second did not move); the wheeled gun −26 % and tank destroyer −12 %:
the same, plus fewer, bigger shots against light targets; the fighter −34 % against aircraft (air group): its
AIM-120 at 280 (was 351) needs a fourth hit on a 1,250 HP helicopter whenever one is decoyed, which is the
direction E wants anyway. Nothing was re-tuned for these in B; E takes the roster as B left it.

### C. Stores and rearming on the field

**C.1 What runs out.** An aircraft's *stores* (bombs, missiles, rockets) have a count per full load: weapon
`load`, a carrier's own `loads` over it (the Ka-52's S-8s). Guns never run out (they change magazines in the air
as before); ground launchers and missile vehicles keep their magazine and reload in place (`ammo`, standing
still); supports and the air-raid event are not stores. The aircraft weapons that had `ammo` (AAMs, MANPADS,
JASSM, the bomber's cruise missiles, Griffin, the drone's bombs), which reloaded in place in mid-air, are stores
now. A salvo fires what is left (a half-empty rocket pod fires half a ripple). Bosses carry no stores (a boss
fight is its own).

| Aircraft | Stores per full load | Rearm, empty to full (full rate) |
|---|---|---|
| attack helicopter (and elite) | 4 Hellfire (elite 8 in pairs), 22 Hydra (2 salvos), 2 Stinger | 8.5 s |
| gunship helicopter | 32 S-8 (2 salvos), 4 Hellfire | 9 s |
| Ka-52 | 8 Vikhr (4 pairs), 24 S-8 (3 salvos), 2 Igla | 9 s |
| scout helicopter | 24 Hydra (2 salvos) | 8 s |
| strike drone / recon drone | 4 Hellfire + 2 GBU-39 / 4 MAM-L | 8.5 s |
| fighter | 4 AIM-120, 2 AIM-9X | 11 s |
| attack jet (and elite) | 16 S-8 (2 salvos of 8, D.1), 4 FAB-250 (2 pairs), 2 R-60 | 14 s |
| A-10 | 14 Hydra (2 pods of 7), 2 Maverick, 2 AIM-9 | 15 s |
| heavy bomber | 9 FAB-500 (one run, D.1), 2 Kh-101 | 16 s (brief: 20-22, see C.10) |
| stealth bomber | 2 JDAM (one run, D.1), 4 JASSM (2 pairs) | 16 s (brief: 20-22, see C.10) |
| AC-130 (the Gunship item) | 10 Griffin | 18 s |

**C.2 Coming back one round at a time** (`SupplySystem`, Sim, stepped after the abilities): every store fills in
the same time, one round at a time, anywhere on the map. **Full rate** once the aircraft has been out of danger
and not attacking for 3 s; **half rate** while it attacks (a target in reach, its attack hold, or a shot fired in
the last 3 s) or is inside enemy anti-air or fighter reach. Danger is the real one (every enemy AA gun, AA missile
and fighter, whether seen or not; checked every fifth step, spread over the aircraft). Rearming mends nothing.

**C.3 The holding pattern** (`SupplySystem.HoldingPoint`): from where the aircraft broke off, straight back
towards home from the nearest friendly ground unit within 60 m (or from where it broke off when there is none),
to the first spot out of every *known* enemy AA and fighter reach plus 6 m, the circle it will fly included;
turning up to 60 degrees either way when straight back is covered; at least 1.5 s of flight behind a friendly
line (2 s with none), at most 2.6 s; on the map with room to circle; with every spot covered, the least covered.
It is worked out again every second as the front moves, always from where the aircraft broke off (a pattern
worked out from where it circles would run away in front of it: that was the heavy bomber's 63 swings in
`AirMotionTests` during the work). There an aeroplane circles as it circles a post and a helicopter hovers; it
stays on the map, can be seen and shot, and its guns still fire at anything in reach. **The old rule of flying
off the map to rearm:** there was none in the simulation; aircraft reloaded their few magazines in mid-air and
went to the airfield (only if the base had one) when their main weapon was empty. That trip is gone (C.5).

**C.4 Leaving at the right time.** An aircraft goes to rearm when its stores are spent. Stores that cannot hit
what it fights do not count: an A-10's AIM-9s or an Apache's Stingers do not keep it on station; a fighter's
stores are all air-to-air, so they all count. It first finishes what it is doing (`SupplySystem.CanBreakOff`): no
salvo still firing, no attack hold under way, and an aeroplane not in its pass: it pulls through first. It flies
out on a straight line, can be hit and keeps shooting and dropping flares; the holding point is chosen out of known
AA, so the line away from the fight bends away from it. It comes back with half its stores (a bomber two thirds
of its bombs) and something to attack near its orders; full and with nothing to attack it stays there ready (an
aircraft on guard goes back to its post). The commander may send an aircraft early (the new `Rearm` command)
when its stores are under a fifth and nothing it can hit is near it (`TacticalAi.RearmInLulls`). Low health keeps
its old rule (the commander sends it to be mended below 35 %, released at 90 %), now only once its attack is over,
and to the HQ when there is no landing pad.

**C.5 Faster sites.** Landing pad (the airfield module): stores twice as fast as the holding pattern, mending
3 % a second as before. HQ (every base): 1.5 times, mending 1 % a second. Beside an ammunition carrier (a
helicopter only): twice as fast, no mending. A site is chosen when the flight there and the rearm take less time
than at the holding pattern (a site under enemy AA counts at the slow rate), or, with the aircraft under 60 %
health, a site that mends when it is at most 1.5 times (+5 s) as slow.

**C.6 The attack loop** keeps 12F's hold and loop. With stores and targets, an aircraft attacks as before; out of
stores it goes to its holding pattern; with no targets after rearming it waits there instead of circling the
battlefield.

**C.7 Ground launchers** reload in place as before. An empty one now drives to an ammunition carrier within
about 60 m, or home (the camp), when the drive and a reload there (three times as fast) take less time than
reloading where it stands (`TacticalAi.SendToRearm`; it moves out of an enemy's reach first, as before).

**C.8 Attack jet and A-10 cannon passes.** Already settled by 12F's attack hold: a 2-2.5 s stream on the attack
jet, up to 3.2 s on the A-10, in the 2-3 s the owner asked for. Nothing more changed; rockets and bombs are stores.

**C.10 Time spent fighting** (`CombatValueMeasure`, 3 seeds, every scenario, 90 s and the 4-minute run): the share
of an aircraft's time on the field attacking or ready to (on target, in its hold, or not on its way to rearm and
not rearming below half its stores):

| Aircraft | Ready | Flying out | At the holding pattern | Longest flight out |
|---|---|---|---|---|
| helicopters, drones, fighter, attack jet | 100 % | 0 | 0 | - (their stores come back as fast as they fire them) |
| A-10 | 91 % | 3.5 % | 8.8 % | 2.6 s |
| stealth bomber | 77 % | 9.5 % | 48 % | 4.5 s |
| heavy bomber | 70 % | 13 % | 42 % | 4.7 s |

The bombers' rearm is 16 s, not the brief's 20-22: at 21 s the heavy bomber was ready 63-68 % of the time and at
0.7 of its old value, well under the 70 % target. Their longest flight out (4.5-4.7 s) is where the nearest spot
out of an AA vehicle's reach is further than 2.6 s and a heavy bomber has to turn round first; it is flagged for
the testing phase. Helicopters never need the holding pattern at these rates: a Hellfire every 5 s against 4 in
8.5 s (half rate: one every 4.3 s) keeps pace. If the owner wants helicopters to go out to rearm, smaller loads
would do it (not done: C.10's target is fighting time, and they meet it).

### D. Bombers

**D.1 Counts** (and the calibre scale's damage, B): heavy bomber 12 → **9** FAB-500 a run (400 each); stealth
bomber 3 → **2** JDAM (850); attack jet rockets 20 → **16** a full load (two salvos of 8); airstrike 8 → **6** Mk 84
a run (700 each after the ×2 strike firepower: the scale's 900 kg), 8 from card rank 7 (was 11); air raid event
14 → **10** FAB-500 (400); cluster strike 40 → **30** bomblets; napalm 10 → **8** canisters; artillery barrage
12 × 220 → **8 × 320** (155 mm). The cruise missile card and the MOAB are unchanged (a 1,000 kg class strike; the
MOAB is the scale's 8,000).

**D.2 Behaviour.** A bomber picks its run by what its bombs would hit (`MovementSystem.BombTarget`, and the same
worth in the bomb mount's target choice, `CombatSystem.BombWorth`): the value of the enemies within its blast plus
4 m, a structure half as much again, a lone light vehicle a quarter; never releases where a friendly ground vehicle
is within the blast plus 3 m of the target; ground its side bombed in the last 10 s (16 m) is worth a third, a pause
between runs on one place. Bombers go in only with two thirds of their bombs (C.4).

**D.3 Aircraft against the ground.** Ground value (the six ground groups), per CP, after C-F: heavy bomber 438,
stealth bomber 390, attack jet 438, A-10 383, strike drone 343; the best ground unit of the same role: heavy rocket
artillery 456 and MLRS 441 (area and structures), tank destroyer 492 (armour). Every aircraft is at or under 1.0
times the best ground unit of its role (the brief's ceiling: 1.3). Without any enemy anti-air they are 1.5-2 times
as strong (attack jet: light 628, fort 1,156); with one AA vehicle they fall to 25-60.

### E. Roster review

Same role and price band within ±15 % of combat value per CP, from the measurement (3 seeds; before = the data
before prompt 13 with the same tool, so the numbers compare). Ground value unless marked "air".

| Vehicle | Change | Before → after (per CP) | Why |
|---|---|---|---|
| tank destroyer | 6 → 7 CP | 555 → 492 | the best anti-armour value by a third |
| ATGM carrier | 6 → 5 CP, 420 → 520 HP, salvo every 8.7 → 7.6 s | 165 → 307 | a third of its peers' value: light armour, slow missiles |
| wheeled gun | 7 → 6 CP, 440 → 620 HP, 105→120 mm gun 3.3 s | 146 → 234 | half its peers'; its flank bonus rarely comes into play; a fast flanker, left under the band on purpose |
| Lancet truck | 7 → 6 CP | 204 → 238 | its double damage on artillery and parked vehicles is its point; the reference groups have little of either (kept under the band) |
| MLRS | 5 → 6 CP | 551 → 441 | artillery's best by half |
| heavy rocket artillery | 9 → 11 CP | 527 → 456 | same |
| thermobaric launcher | 9 → 7 CP, 16 → 12.8 s | 243 → 267 | its 38 m reach puts it in the fight |
| rocket technical | 150 → 190 HP, 8 → 7 s | 235 → 245 | fragile against anything that moves |
| SP artillery | reload 52 → 36 s, 13.4 → 11 s | 284 → 314 | B's 155 mm stretched its cycle |
| turtle tank | 8 → 7 CP | 262 → 360 | the battle tank's gun on a slower, hull-aimed body |
| scout helicopter | 6 → 5 CP | 249 → 318 | |
| Ka-52 | 14 → 13 CP | 229 → 265 | stays under the band on purpose: the best of all helicopters with AA about (+AA: 223-300) |
| gunship helicopter | 14 → 15 CP | 469 → 384 | the brief's "highest heavy damage per CP of the helicopters" (tanks: 790 against the attack helicopter's 683) |
| A-10 | 18 → 16 CP | 559 → 383 | stores (C) took a third of it |
| stealth bomber | 20 → 18 CP | 535 → 390 | stores and 2 JDAM |
| heavy bomber | 20 → 22 CP | 598 → 438 | still the aircraft's best on structures (fort 1,177) |
| fighter | 10 → 12 CP | air 376 → 284 | the brief's "fighters dominate the air"; now between the AA vehicle (234) and the long-range SAM (410) |
| heavy AA | 7 → 6 CP, 480 → 540 HP | air 219 → 194 | dies first of the anti-air in the air group |
| ZU-23 technical | 170 → 210 HP | air 99 → 85 | |
| engineer | 4 → 3 CP | - | lost its rearm aura to the ammunition carrier (F) |

After it, per role: light 92-123; heavy 356-494 (the flame tank 356, an anti-light specialist: light group 700+);
tank hunters 234-492 (the tank destroyer, FPV carrier and railgun 403-492); artillery 245-456; helicopters 265-392;
aircraft 343-438; mobile anti-air in the air group 183-234 (the long-range SAM 410: it cannot hit the ground).
The railgun (the brief's "still weak: 68 DPS on heavy for 9 CP") measures 403, at the tank hunters' middle: its
pierce and reach are what the theoretical table missed; unchanged. **The Iron Beam** (`PrintPointDefenceValue`:
four tanks under two ATGM carriers, an MLRS, a Lancet, an FPV carrier and an attack helicopter for 45 s): it saves
4,214 HP (468 a CP, 22.7 interceptions) against two AA vehicles' 1,963 (245 a CP); unchanged at 9 CP. A C-RAM
saves as much (4,194).

**E.3 The sky gunship** is no card any more (`"card": false`): the AI never buys it, the design document lists it
with the items (`itemVehicles`). The Gunship item still flies it. The save migration and the 4,500-coin refund
were already done in prompt 2 (`CardMerges.Retired`); nothing else carried it as a card (it was only the design
document's list and the AI's list of every catalog vehicle when it has no deck).

**E.4 Behaviour against the guide text:** the tank destroyer, wheeled gun and gun pit (B.5), the wheeled gun's
damage a second (65 → 70), the AA tower's quad flak (35 → 23 mm), the engineer (repair only) and the airstrike's
bombs were corrected; G generates the behaviour lines from the data so they cannot drift again.

### F. Content for the stores

**F.1 The landing pad** (the airfield module, not a new building): stores twice as fast as the holding pattern,
mending 3 % a second (C.5). Two rank-7 branches (`airfield.hangar`: one more aircraft up at once for its side,
`EconomySystem.AircraftCap`, and a little tougher; `airfield.service`: stores and mending half as fast again, 4.5 %
a second, 16 m). A module's branch is chosen and fights as a tower's does (`PlayerProfile` and `BaseSystem` now
apply branches to modules). The enemy's base takes a landing pad in its first utility slot
(`BaseLoadout.ForAi`); a fortress's landing pad destroyed pays the attacker 12 CP in Siege (`SiegeRules.PadCp`),
and its aircraft then rearm only at their holding patterns and the HQ.

**F.2 The ammunition carrier** (`ammo_carrier`, Support, 4 CP, 520 HP light armour, 8.5 m/s, roof HMG, a big
death blast): launchers and missile carriers within 14 m reload three times as fast (the rearm aura the engineer
had), helicopters within 12 m take their stores on twice as fast. The engineer keeps its repair and mine clearing
and drops to 3 CP. The commander parks the carrier by its launchers and helicopters, 6 m back towards home and
out of known defences' reach, buys one once it fields three launchers or helicopters (never a second), and sends
empty launchers to it when that is quicker (C.7). Unlocked with the UAV scan in c3m03 (the mission after the
attack helicopter's). Its model is the supply truck's for now (**asset debt**, `Docs/ASSET_DEBT.md`); its card
render, In-action scene and short name come with the UI part (C.9, G).

No other vehicle or building was added for the stores.

### H. Every mode

**How it was measured** (`ModeBalanceMeasure`, `MB_BALANCE=1`): every mode played whole by both commanders on
two or three battlefields and two seeds (the owner's rule for this pass; the five-seed sweep is for the testing
phase). The player's side is its auto commander (Hard) with a **sample deck**: main battle tank, IFV, tank destroyer,
light tank, MLRS, AA vehicle, attack helicopter, engineer, rank 1, no equipment, the default base. The test build unlocks
every card, so the enemy draws from all of them.

The first measurement (H1) used the starter deck of seven against an enemy that fielded **every** card. That is
what a quick battle did before I.2, and it made the player lose almost everywhere (Deathmatch 0/6, King of the Hill
1/6, Endless and Survival always). With I.2's deck of eight or more chosen by roles, and the sample deck for the
player, the modes were tuned to these results (Normal):

| Mode | Target | Before (H1: starter deck, enemy with every card) | After |
|---|---|---|---|
| Conquest | 55-65 %, 6-10 min | 3/6, 6.2 min | 7/12 (58 %), 7.4 min (5.7-9.5) |
| Deathmatch | 6-9 min | 0/6, 7.9 min | 2/6, 8.5 min (7.9-9.5); 8/12 on four other seeds |
| King of the Hill | 55-65 %, 6-9 min | 1/6, 3.2 min | 8/12 (67 %), 7.4 min (4.9-8.2) |
| Assault | 60-70 % | 5/6, 6.2 min | 8/12 (67 %), 4.7 min (2.7-12.6) |
| Siege | 60-75 %, 10-15 min, narrower | 4/6, 14.4 min (10.9-19.3) | 6/6, 10.7 min (9.2-14.0) |
| Weekly, from stage 1 / 2 / 3 | last stage still a challenge | 0/2 (stage 1) | 0/2 each: 17-71 %, 71-83 %, 68-70 % |
| Defend | outer line lost 50-70 %, HQ held ~4/5 | outer line lost 6/6, HQ held 1/6 | outer line lost 6/6 (at 4.0-6.4 min, it was 1.4-2.4), HQ held 6/6 |
| Endless | median 12-15 min | 8.3 min (8.1-10.1) | 15.1 min (14.4-15.5) |
| Survival | median 8-12 min | 13.1 min (lost 4/4) | 12.0 min (9.8-14.3; the sample deck held 30 min before the waves' ceiling came off) |
| Boss Rush | 15-25 min | 15.2 min | 18.7 min (15.9-20.8) |

What was changed, by mode:

- **H.1 Conquest:** a slower bleed (0.6 → 0.5 a second) and less CP a point (0.3 → 0.15 a second), so the side
  ahead snowballs less, and the enemy's commander earns 18 % more here (it takes and holds points worse than the
  player's side: 10/12 without it, 9/12 at 10 %).
- **H.2 Deathmatch** is scored in CP now (`DeathmatchMode.Score` = the CP the other side lost, the kill ledger's
  price, an elite counting as its base card): a swarm of cheap vehicles thrown away scores little. First to
  **480 CP** wins (600 ran 8-9 minutes; the old target was 30 kills); the clock stays 12 minutes, and at the clock
  the higher score wins. The enemy's income is 1.2 here (1.35 before; it won every straight fight at 1.35).
  Saved records need nothing: the mode kept no score record, and the result screen shows the CP.
- **H.3 King of the Hill:** 170 to win (100 before; battles ran 3-4 minutes), the enemy's income 1.2 → 1.1. The
  hill's capture time (8 s) and the holder's rate (0.75 a second) were right; only the target was short.
- **H.4 Assault:** the defender 26 → 32 CP and 1.05 → 1.3 income, and the attacker's CP a sector 12 → 8. Each of
  A, B and C fell in 1-3 minutes, none stood out; the sector time bonus (240 s) was left.
- **H.5 Siege:** a tougher fortress (towers 1.2 → 1.75 times as tough, rings 1.1 / 1.25 / 1.4, Normal mans 90 % of
  the hardpoints, not 75 %), a bigger garrison (12 → 16 CP, Hard 22, income 0.6 → 0.8) and 300 s a ring broken
  (360). The spread narrowed (8.6-12.9 minutes, against 9.7-17.8 before this prompt). The measured side still
  won every siege: the clock would have to bind hard to lose one in four with this commander, and a stopwatch
  siege is worse than a winnable one; a human's slower siege decides it (**testing phase**).
- **H.6 Weekly fortress:** measured from each stage a week can start at. From stage 1 the 5-minute clock ends it
  at 17 % (by design: the rings broken stay broken for the week); from stages 2 and 3 it still held against the
  measured side after 9-14 minutes (44-68 %). The last stage is not easy once the rest is broken; if anything it is
  hard (**testing phase**: a human's week of attempts).
- **H.7 Defend:** the waves scale with the player's base (`BaseStrength`, below: size times
  `WaveScale(score) = clamp((score / 100)^0.75, 0.75, 2.5)`, the attacker's income times its square root), are
  drawn against the loadout (`SiegeRules.CounterBase`: more armour against machine-gun towers, fast light vehicles,
  drones and long guns against anti-armour towers, no aircraft into a sky of anti-air, raiders against artillery)
  and bring siege breakers from wave 2 (bulldozer, siege tank, heavy rocket artillery, artillery; one more every
  three waves). The outer line is tougher and the inner ones less so (1.45 / 1.25 / 1.4, it was 1 / 1.4 / 1.8),
  the first wave smaller and the growth steeper (4 + 1.7 a wave; Hard 5 + 1.9; Easy 3). The outer line fell in
  every battle but later (4.0-6.4 minutes, it was 1.4-2.4 with the starter deck) and the HQ held in all six
  (the aim is about 4 in 5; **testing phase**, with a player's own base).
- **H.8 Endless:** the same base scaling, a smoother climb (1.2 vehicles a wave plus 6 % a wave compounded, where
  it added 1.6 flat and hit its ceiling), its lines 1.2 / 1.3 / 1.5. The HQ fell at 11.8-16.4 minutes (median 15.3;
  it fell at 10.3-11.7 whatever the deck). How far it moves with the base's strength is for the testing phase.
- **H.9 Survival:** the waves by the deck's strength (`SandboxMode.DeckScale` = the deck's `EnemyScaling.Power`
  / 100: rank and equipment), 3 + 0.9 a wave with no ceiling (it stopped at 6), up to 48 alive (14 + 1.5 a wave),
  the heavier cards coming in as the waves go on, elites from wave 8 (6 % a wave, all of them by wave 24). The waves keep coming
  while the field is full (only the room under the ceiling is filled; they stopped altogether before, and a deck
  that held stood for ever), and the rally counts as overrun when the enemy holds it two to one (not only when
  nobody is left: new vehicles arrive at the rally). Aircraft rearm at their holding patterns there (no pad, no HQ;
  C's measurement covered it).
- **H.10 Boss Rush:** 15.9-20.8 minutes, median 18.7 (15-25 wanted). Boss times ran 0.5-6.6 minutes; the third and
  fourth in the order ran longest (up to 4.2 and 6.6), the last three shortest (0.5-0.6: the army is biggest by then);
  per-boss health left as it is (**testing phase**, over more seeds and orders). The bounties (8 CP at 75 / 50 / 25 %, 12 on the kill) let the army rebuild.
- **H.11 Campaign and Operations:** one seed over every mission (`CampaignTests.MissionPlaysToAnEnd`, before the merge of
  prompt 12): 88 of the 90 played won; c8m08 was lost (as before part C) and c8m10 did not end in 34 minutes (its
  last stage, hunt the rest, was unfinished once before too). The quick-mode changes do not reach missions, except
  a mission with no enemy deck of its own now drawing eight by roles (`EnemyDeck`). Operations' mutators and the
  15-25 minute frame: **testing phase**.
- **H.12 Help for the side behind** (`EconomySystem.Underdog`, `UnderdogRules`): in Conquest, Deathmatch, King of
  the Hill and Assault (each sets its own time; 0 turns it off, as the menu battle does), after 4 minutes, when
  one side's army on the field is worth 1.6 times the other's or more (and at least 14 CP), the weaker side earns
  25 % more for the rest of the match and is flown one free reinforcement: two or three of the deck's vehicle
  nearest its average price (three when that is 6 CP or less). Once a match, no health or damage added, and both
  sides are told (`assist.us` / `assist.them`). In Defend and Endless a player holding far too easily (the
  defenders worth 1.6 times the attackers after 4 minutes) draws one extra breaching wave instead: two of every
  breaker, elite where there is one (`assist.breach`).

**BaseStrength** (`Sim/Modes/BaseStrength.cs`, commit b5e6c74; the Base screen's number): a base's towers, modules
and HQ, each by its rank and equipment (`EnemyScaling`'s tougher-and-harder-hitting rule), against the mid-level
mark of 100 (an HQ at level 3 with its slots filled at rank 1). `Score(catalog, loadout, boosts)` for a loadout,
`Score(world, team)` for a base on the field, `WaveScale(score)` for the waves.

### I. The AI by difficulty

**I.1 Four levels.** Easy, Normal, Hard, and the new **Very Hard** above Hard (`AiDifficulty.VeryHard`, saved as 3;
Easy 0, Normal 1 and Hard 2 keep their numbers, anything else reads as Normal). One buying profile
(`BuyProfile`) for each:

| | Easy | Normal | Hard | Very Hard |
|---|---|---|---|---|
| Noise (randomness of a pick) | 3 | 0.8 | 0.6 | 0.4 |
| Counters what it has seen | 0 | 1 | 1.25 | 1.4 |
| Keeps its role shares | 0 | 0.5 | 1 | 1 |
| Weighs value per CP (part A) | 0 | 0.6 | 1 | 1.2 |
| Saves for the big cards (per CP of price) | 0 | 0.04 | 0.1 | 0.12 |
| Deck | 8 at random | 8 by roles | 10 by roles and value | 12 by roles and value, against the player's deck |
| Income | ×0.8 | ×1 | ×1.2 | ×1.4 |
| Decision every | 2.2 s | 1.1 s | 0.6 s | 0.45 s |
| Elite share of its spending (cap) | 5 % (1) | 10 % (2) | 15 % (3) | 30 % (6) |
| Rewards | ×0.7 | ×1 | ×1.45 | ×1.8 |
| Base (HQ level) | 2 | 3 | 5 | 5 |

Hard and Very Hard also: hold their strikes while the army holds back (they go in with the push), take a doctrine,
and hunt aircraft that are flying out to rearm or circling their holding pattern (I.3). Very Hard also: knows the
player's deck from the start (`ConquestAi.KnownDeck`, fed into what it counters at half weight until it has seen six
enemies; **never** where anything is: fog of war holds), masses its CP (it waits until two thirds of its bank before a
wave, then spends it all; it spends at once when under fire), and weighs the player's weakest point twice as much when
choosing where to attack. The enemy's income multiplier is applied once for every quick mode
(`ModeSession.Create`); Defend's attacker (it was 1.35 / 1.1 / 0.95 by hand) and the Siege garrison
(0.85 / 0.6 / 0.45) now take one base and the multiplier.

**I.2 Buying is one scoring function** (`ConquestAi` buy scoring, deterministic: every draw from the commander's seeded
random): 1 + noise × random + (value − 1) × the value weight + the counter score × the counter weight + the role
share gap × 5 × the mix weight + price × the saving weight. The **deck** (`ConquestAi.PickDeck`, the quick modes'
enemy and the campaign missions with no deck of their own) is chosen by roles in order (front line, armour, anti-air,
artillery, fast, aircraft, front, support, then again), only cards that fight filling the fighting roles (no siege
breaker, recon drone or bulldozer), a repair or ammunition vehicle preferred for support; Hard and Very Hard add the
value per CP; Very Hard adds weight to aircraft when the player's deck has little anti-air and to heavy armour when it
has little anti-armour. The combat value per CP is data (`"value"` on every vehicle, per class, from the F3
measurement, 0.5-1.5).

**I.3 Stores in the AI:** it buys an ammunition carrier once it fields three launchers or helicopters (never a second);
with the enemy flying three aircraft or more, its artillery and strike aircraft go for the enemy's landing pads and
ammunition carriers; on Hard and Very Hard its fighters go after enemy aircraft that are flying out or holding
(`TacticalAi.HuntSupply`).

**The ladder** (the sample deck and the player's auto commander at Hard against each level; Conquest, Deathmatch,
King of the Hill and Assault, three battlefields, four seeds each, the player's wins):

| Mode | Easy | Normal | Hard | Very Hard |
|---|---|---|---|---|
| Conquest | 12/12 | 10/12 | 11/12 | 9/12 |
| Deathmatch | 11/12 | 8/12 | 4/12 | 3/12 |
| King of the Hill | 12/12 | 6/12 | 6/12 | 0/12 |
| Assault | 12/12 | 11/12 | 8/12 | 2/12 |
| **All** | **47/48 (98 %)** | **35/48 (73 %)** | **29/48 (60 %)** | **14/48 (29 %)** |

Each level is harder than the one below over the four modes (before the merge of prompts 12 and 14 and before the
last Conquest, Hill and Assault changes). Normal against Hard is the closest step (73 % against 60 %, and Conquest
and the Hill on their own do not tell them apart); **testing phase**: more seeds, and a human.

**I.4 One ladder of names.** The quick modes said Easy / Normal / Hard; the campaign and Operations said
Normal / Heroic / Iron / Legend. They are one ladder now:

| Where | Before (EN / VI) | Now (EN / VI) | Saved as |
|---|---|---|---|
| Quick modes | Easy / Dễ | Easy / Dễ | difficulty 0 |
| Quick modes | Normal / Thường | Normal / Thường | 1 |
| Quick modes | Hard / Khó | Hard / Khó | 2 |
| Quick modes | (none) | **Very hard / Cực khó** | 3 (new) |
| Campaign, Operations tier 0 | Normal / Thường | Normal / Thường | tier 0 |
| Campaign, Operations tier 1 | Heroic / Anh hùng | **Hard / Khó** | tier 1 |
| Campaign, Operations tier 2 | Iron / Thép | **Very hard / Cực khó** | tier 2 |
| Operations tier 3 | Legend / Huyền thoại | Legend / Huyền thoại | tier 3 |

A tier's rules stay the tier's (Hard: the enemy 30 % stronger, rewards ×1.5; Very hard: that, 20 % less income and no
fire support, rewards ×2): they are close to the quick modes' levels, and the missions were tuned to them. Every
record is saved by number (a mission's best tier, an Operations tier, the chosen difficulty), so the records migrate
without a change; the internal keys (`heroic`, `iron` in operations.json, the elite budget's `Heroic` and `Iron`)
stay as they are. The short badge reads "V. HARD" / "CỰC KHÓ".

**Migration tests** (`Prompt13MigrationTests`): the sky gunship is no card and no deck or AI picks it; the engineer
repairs and the ammunition carrier rearms; Deathmatch scores the CP of what was destroyed; saved difficulties keep their
meaning and the tiers carry the quick modes' names in both languages.

**The C-RAM test** (`TowerRosterTests.TheCRamShootsDownRocketsAndSomeShells`) failed after B: the 155 mm shell is one
every 11 s now (7 before, for the same damage a second), so one gun sent four shells in the test's 40 s and at the
C-RAM's 30 % share this seed took none. The C-RAM and the shells are unchanged (it takes the same share of the
damage); the test now uses two guns and keeps the C-RAM standing (the 155 mm splash beside it destroyed it at 38 s).

### C.9, G, F: the interface parts

**C.9 Ammunition icons** (`VehicleView.Stores.cs`): beside the health bar, on its right so it never covers it, built
from quads in flat single colours like the repair mark. One set for aircraft, helicopters and launchers (it replaced the
launchers' three-shell gauge and reload bar): low (a magazine with one bar, coin yellow, under 20 %; a launcher's last
salvo), empty (the magazine's frame red, blinking gently), flying out (a grey return arrow), rearming (the magazine in
our green, a ring of 12 segments lit by the share of stores back, turning at 30° a second and dim at the slow rate,
90° and bright at the full one; a launcher reloading in place counts as the full rate) and full (the ring flashes for
0.6 s, then the icon goes). Enemy units show only empty and flying out. The health bar shows while the icon does.
Our holding patterns are faint mint rings on the minimap. The selection panel shows the selection's biggest store
under its health bar ("Rockets 14/22", launchers their salvos) in the `SelectionExtras` hook, yellow under 20 %, red
when empty, dim at the slow rate. Settings, Game: "Ammo icons: All units / Aircraft only" (`MatchSettings.AmmoIcons`,
saved; default all). The icon table is in the Guide tab of every unit that uses the icons, and c3m03 (the first
mission after the attack helicopter unlocks) shows it as a tip (`tip.ammoIcons`, in the campaign source and the JSON).
The icons are not in a screenshot test yet (**testing phase**: legibility at the default zoom on the smallest phone).

**G Detail lines** (`UnitLines`, `UnitText`): worked out from the data, in both languages. For each weapon: the real
name and calibre (`real`, else the kind and calibre), damage type and targets, damage a round and rounds a salvo, the
magazine (changed in place, seconds) or the stores (N bombs / missiles / rockets when full, full in `rearmTime` at the
holding pattern, half as fast attacking or in danger, faster at the landing pad x2 and over the HQ x1.5, beside an
ammunition carrier x2 for helicopters) or the shots or salvos reloaded in place, range, minimum range and splash.
Behaviour: how it moves and engages (stands and fires, stops to fire, fires on the move, keeps to the edge of its range,
hovers, dives and comes round, circles its target, bomb runs, hunts aircraft, artillery with its ranges and sight), after
firing (moves after N salvos, changes its magazine, comes round again), what it goes for first (its data's strong-against
classes, aircraft for anti-air, groups and buildings for bombers), when it pulls out and where (stores spent, two thirds
of its bombs, badly hurt to the pad or the HQ, a launcher to a carrier or home), and its skills (with their trigger and
cooldown), APS, jammer, repair and rearm auras, mines, counter-battery radar, stealth. Modules: the landing pad's
stores rate and mending, the hangar's extra aircraft. The weapons tab shows the old one-line figures and every line
behind "More" / "Xem thêm"; the guide tab has the Behaviour section; module facts carry the pad lines. The design
document export has `behavior`, `ammo` and each weapon's `name` for every vehicle, tower and module (Vietnamese).

**G.3 Hand-written text against the data** (`UnitLinesTests.HandWrittenTextAgreesWithTheData`): every calibre ("N mm")
and every "N bombs / rockets / missiles" in a unit's note or guide (its first paragraph, where it describes itself) must be
one of its own weapons' calibres or counts. It found four, corrected to the data: the IFV's 30 mm (the note said a
Bradley's 25 mm; the data is a 2A42 30 mm), the Ka-52's 23 mm (GSh-23V in the data), the Little Bird's 24 rockets in
salvos of 12 (the note said a seven-rocket pod), the TOS-1A's salvos of 9 (the note said 24 rockets).

**F The new cards' pictures:** the ammunition carrier's card render (`truck`, `CardRenders.RenderBatch`; the landing
pad's branches share the pad's picture), and its In-action scene (`FiringRange` `Scene.Resupply`: two rocket launchers
beside it, empty at the start, reloading and firing again; `SimWorld.DebugEmpty` empties them). `CardRenderTests` pass.

**Shared edits:** `SimWorld.DebugEmpty` (previews only), `SupplyRules` (the stores' rates as public constants, which
`SupplySystem` goes by), `Strings.Get`/`Has` also look in `UnitText.Table` (and the two language scans include it),
`SelectionController.Stores()`, `Minimap.Holding`, `MaterialLibrary` (four stores colours). No pathing or traffic code.

### Z. Left for the testing phase

- The five-seed sweep of every mode at every difficulty (this pass: two seeds, two or three battlefields; the ladder
  four seeds on four modes), with a human rather than the auto commander as the player's side: Siege (6/6 won by the
  measured side), Defend (the outer line fell every time, the HQ held every time), Weekly from each stage (never won),
  Deathmatch (2/6), and whether Normal and Hard are far enough apart (73 % against 60 %).
- Endless and Defend by the base's strength (the waves scale with `BaseStrength`; only the default base was measured).
- Boss Rush per boss over more seeds and orders; Operations' mutators and the 15-25 minute frame; the whole campaign on
  more seeds (one seed: 88 of 90 won, c8m08 lost as before, c8m10's last stage unfinished once more).
- The combat values and the aircraft's readiness over more seeds (A, C.10); the bombers' longest flight out (4.5-4.7 s,
  C); the ammunition icons' legibility on the smallest phone and the HUD cover with an aircraft selected.
- `CampaignText.cs` is out of step with `Tools/campaign/build_campaign.py` (hand edits since it was generated, such as
  "Bọ Bạc"): the generator was not run over it; c3m03's changes went into both the source and `campaign.json`.

## 13D. Prompt 14: Base screen, out-of-battle sizes (2026-09-29)

The owner found the menus oversized on a phone and the Base screen a diagram that did not look like the
camp. No game logic or balance data changed: the Base screen reads the sim's camps, ranges and base
strength, and the one sim change is an optional filter on the enemy AI's base picker (G5).

### A. Out-of-battle sizes in device points

- **One point, one size on every phone.** `Kit.PanelPxPerPoint` = `Kit.TouchTarget / 44` (1.823 panel px a
  point; the 80.2 px target is 44 pt). The menu panel is `ConstantPixelSize` at
  `BattleHud.MenuScale(width, height, dpi, mobile)` = dpi / (160 x 1.823) screen px a panel px, so a point is
  a 160th of an inch (Android's dp; iOS's point is a 163rd, 2 % off). Where the density is unknown or not a
  phone's (under 100 dpi, the editor, a desktop, the screenshots) the screen is taken for a phone
  `Kit.ReferencePhonePoints` (395 pt) high, the height scaling the menus had before, so the screenshots
  and layout checks measure what a phone shows. Settings > UI size multiplies it as before. A tablet now
  shows more around the same sized controls instead of everything bigger.
- **The battle HUD keeps its scaling** (ScaleWithScreenSize with the height, prompt 11's layout and its
  30 % cover check): `.fc-hud` in Tokens.uss sets its own type and 82 px target, its Large block keeps the
  old Large sizes, and `.fc-hud .fc-overlay` gives the result, pause, choice, ad and dialog overlays (they
  are menus shown over the battle: classed `fc-overlay`) the menu sizes again.
- **The scale, Normal text** (panel px, points in brackets; the brief's range): main button text 35 (19;
  18-20), screen title 33 (18; 17-20), panel title and buttons 26 (14.3; 14-15), body 24 (13.2; 13-14),
  secondary 20 (11), a card's name 22 (12; a new `--fc-fs-card`, between secondary and panel title, since
  cards are narrow), big numbers 36, numbers in text 25; nothing under 10 pt. Large multiplies the type by
  1.2 (UiThemeTests keeps it to type only, and the top bar: see J). Top bar 81 (44.4 pt), rail 132 (72 pt)
  with 42 px icons (23 pt) and 11 pt labels, tabs 73 (40 pt; their targets reach 44 pt through negative
  margins), buttons 81 (44 pt), the main button 96 (52.7 pt). Spacing stays 4 / 8 / 12 / 16 / 20 / 24 / 32
  panel px (the brief's 4 / 8 / 12 / 16 / 24 in points would be 7 / 15 / 22 / 29 / 44 px: too loose on a
  phone next to the smaller type; the steps are kept, 2.2 / 4.4 / 6.6 / 8.8 / 13 pt).
- **Cards in lists 22 % smaller**: vehicle cards 184 -> 144 px wide (79 pt), compact 136 -> 112, gear
  164 -> 128 (gear names may take three lines in Large text, their fixed name area is three lines there).
  `Kit.FixedLines` also falls back to the short name when one word is wider than the card (a Large-text
  case the line count alone missed).
- **Main content >= 70 %** (`UiLayoutTests.TheContentKeepsSeventyPercentOfTheScreen`: the shown page
  less its row of tabs, over the screen, every menu screen, 16:9 and 20:9): 70.5-88.8 % at 16:9 and
  72.1-88.8 % at 20:9 (the Army and Shop pages with tabs are the 70.5 / 72.1; home, campaign and setup 79.6 /
  81.4; details 78.6; settings 88.8). The 1280 x 720 reference phone is 702 x 395 pt.
- The top bar's coin and settings buttons are plain icon buttons with 44 pt targets.

### B-F. The Base screen

- **Layout**: a bar (the HQ badge, the map picker, the three base sets, Auto-arrange, "Saved"), then the
  tray (left), the camp map (centre), the panel (right), and the cover strip along the bottom.
- **The map is the camp's real picture** (`BaseMapArt`, below): the player's camp on the chosen map from
  above, the enemy's approach as red arrows, the slots at their real positions. It opens framed on the camp
  (the HQ, every slot and the arrows' heads with a 12 px margin: `CampMap.Focus`), not the whole picture
  with its margins, so the slots are as large as they can be at the default zoom; pinch or the wheel zooms
  (up to 3x), a drag on the ground pans, and the view keeps where the player left it until the map changes.
- **Slot faces sized 1 / 1.4 / 2** (small / medium / large; utility 1.4 as a hexagon; the HQ mark 1.6),
  in metres on the picture so they zoom with it. The small face is 0.9 x the closest pair's centre
  distance shared by their ratios, at most 12 m, per map (`BaseScreen.FaceMetres`), so no two faces touch
  on any of the 20 camps (`BaseScreenTests.SlotFacesKeepTheirRatioAndNeverTouch`); most camps get 11-12 m.
  Every face has a transparent 44 pt target round it.
- **A slot shows** its tower's render, rank ticks and a branch mark; empty, its size in words ("Nhỏ",
  "Vừa", "Lớn", "Tiện ích") under it; closed (the HQ level is too low), a lock and the level it opens at
  inside the face, and no tower even if the plan has one there (it does not fight at this level).
- **Tray** (C): tabs by size (Small / Medium / Large / Utility), compact cards with the render, the short
  name and "Used n" or where it unlocks ("Mở ở nhiệm vụ 62", "Mở ở cửa hàng"), locked cards dimmed. Drag a
  card onto a slot, or tap the card then a slot; while one is carried only the slots it fits light up. A
  tap on a filled slot selects it; dragging a tower off the map takes it out.
- **Ranges** (B7): the "Show ranges" switch paints every open tower's cover as one union (no darker
  overlaps): ground amber (`--fc-range-ground`, 30 %), air light blue (`--fc-range-air`, 36 %), told apart by
  lightness as well as hue; a tapped tower draws its reach as a ring (the longer of ground and air; the
  panel's reach line gives both) and a minimum range as a thinner inner ring. Ranges are `BaseRoles.Reach(def)` from the weapon data (the largest ground and air
  range of the weapons that do damage, the smallest minimum range), after the branch is applied; the test
  checks the drawn circle against it.
- **Panel** (D): the render, name, size, rank and branch; Health / DPS / Range bars against the best of
  the same size (the stats are `UnitStats`, so they follow prompt 13's corrected DPS); the reach line;
  Branch and Gear tabs (a module has no gear; one with rank-7 branches, the landing pad since 13 F.1,
  shows them); Replace (opens the tray on that size), Remove and Details (the detail page). With nothing
  chosen: an overview, the how-to and the strength with what it means.
- **Cover strip** (E1): the base's roles (`BaseRoles.Of` from the data: anti-light, anti-tank, anti-air,
  rocket/missile intercept, stealth detection, repair/resupply), a missing one in the danger colour with
  an info mark; "Sức mạnh căn cứ" and the counts in words ("Nhỏ 3/3 · Vừa 1/1 · Lớn 0/0 · Tiện ích 0/1").
- **Strength** (E2) is `BaseStrength.Score(catalog, PlayerProfile.BaseLoadoutFor(map), PlayerProfile.BoostFor)`,
  the same number Defend and Endless scale their waves with (100 = the Normal enemy base at HQ 3 with no
  upgrades; `BaseScreenTests.TheStrengthShownIsTheOneTheWavesScaleWith`).
- **HQ** (F1): a badge with the level and the next level's gain ("Lên cấp 2: thêm 1 ô nhỏ, 1 ô vừa")
  instead of the HQ tabs; the level is `Campaign.HqLevelCap` (the campaign opens levels; the chooser went
  with F.1).
- **Map picker** (F2): a dropdown whose list has each map's picture, a dot and a note on maps set up on
  their own or with towers that did not fit; closed, it is the name only (the bar stays one row).
- **Autosave** (F3): every change saves at once and "Đã lưu" shows for 1.6 s at the bar's end.

### G. One loadout for every map

- **By place, not by slot index.** `SlotPlaces.Keys(site)` labels a camp's slots: distance from the HQ over
  the furthest slot and bearing against the way the HQ faces the enemy. Under 0.4: beside the HQ; more than
  110 degrees round: rear; at 0.7 or more and within 40 degrees of the front: gate; at 0.7 or more
  otherwise: outer ring; the rest inner ring; utilities apart. Each gets an ordinal by bearing within its
  place and size (`PlaceKey` = place, size, ordinal).
- **A `BasePlan`** maps place keys to towers and is resolved on each map (`Resolve(mapId, site, level)`): a
  key the map has takes its tower; one it lacks goes to the nearest free key of the same size (place
  distance first, then ordinal); what finds no slot is a misfit, and the map picker marks that map with a
  warning dot. A map can be set up on its own (`Custom`: the slot list as it is, "Chỉnh riêng cho map
  này", marked in the picker); switching it off returns the map to the plan.
- **Three sets** (`PlayerProfile.BasePlanCount`), switched on the Base screen's bar and on the home
  screen's deck panel (chips "Bộ 1 / 2 / 3": a fifth dropdown squashed the home column in Large text); the
  set in use is what `PlayerProfile.BaseLoadoutOn(map, team)` gives the match (`ModeSessions`: four call
  sites).
- **Auto-arrange** (G5) fills the plan's towers with `BaseLoadout.ForAi("Normal", "default", seed,
  allowed: PlayerProfile.IsUnlocked)`: the enemy AI's own picker, limited to the player's towers (the new
  optional `Predicate<string> allowed` in the sim; the AI's calls are unchanged). Utilities are kept.
- **Migration** (version 2 -> 3, `PlayerProfile.MigrateToPlans`): the old sized lists become set 1's places
  on the reference camp; every map whose old slot-by-index result differs from the plan's is kept as its
  own (Custom) so no battle changes: for the test's version 2 profile 11 places and 19 of 20 maps kept on their own
  (`BasePlanTests.TheOldLoadoutBecomesThePlanAndNoMapChanges`). An unedited profile takes the defaults with
  no custom maps. `PlayerProfile.BaseLoadout` (get/set) stays for old callers, now on set 1's plan; it
  moved to PlayerProfile.BasePlans.cs (13 F.1's module-branch line ported there).

### H. Outpost

A separate Army tab: the outpost's two slots (small and medium) as faces round the point, a tray with the
Small and Medium tabs, and how the outpost works in words; it edits `BasePlan.Outpost` (on every map) with
autosave.

### I. Tower icons (helper)

Every tower, branch and module has an icon of its own in `Icons.cs` (`t_` prefix) through `TowerIcons.For(id)`, which `CardIcons.For` asks first. A branch uses its tower's icon; the
rail supergun shares `t_supergun` (the supergun timer too); the Army > Towers cards' corner shows the
structure icon; renders are unchanged. `TowerIconTests.EveryStructureHasALineIconOfItsOwn` checks every tower and module has one;
`Docs/ui-screens/kit-tower-icons.png` is the sheet.

### B1-B2. The camp pictures and arrows (helper)

`Machine Brigade > Render Base Map Pictures (stale / all)` (`BaseMapShots`) renders each map's player camp from above to
`Resources/UI/Bases/<map>.png` (1024 x 640, 16:10) with a JSON frame (the picture's rectangle in metres,
the approach arrows, the drop zone). The frame is the camp's slots and HQ with an 18 m margin and 30 m more
in front; the look is the game's camera lighting at -0.35 EV and -8 saturation with the ground outside the
map dimmed 50 %, so the slots read over it. Arrows are where the enemy's lanes (`LaneFlags.Route`) cross
into the frame, merged within 22 m. A SHA-1 of the map and camp data marks a picture stale
(`BaseMapArtTests`). Normal-quality compression. Conquest camps have no walls or gates in their data, so
none are drawn; the drop zone is drawn by the UI.

### J. Screenshots, Large text

- `Docs/ui-screens/`: every menu and battle screen at the four shapes, a set in Large text and in English
  (241 files), with the new `screen-army-base`, `-base-picked`, `-base-ranges`, `screen-army-outpost`,
  `screen-army-towers`, `screen-detail-tower`, `screen-detail-module` (and their In action tabs),
  `kit-tower-icons.png` and `basemaps-sheet.png`.
- Large text fixes found there: the top bar is 87 px (47.7 pt, inside the 44-48 range) at Large so the rank
  and XP keep two lines; the home column is 520 px at Large (440 Normal) so two dropdowns share a row and
  the campaign card keeps its room; the deck panel's base-set chips drop their caption at Large; the Base
  map's two switches stack in its corner in short words ("Chỉnh riêng", "Tầm bắn"; the full names as tooltips) and show icons only at Large; "Saved"
  floats at the bar's end instead of wrapping to a row of its own.

### Not done, and why

- **Moving the utility slots apart**: their places are map data (the camps); the Base screen shows them
  where they are.
- **Walls and gates on Conquest camps**: not in the camp data; nothing to draw.
- **FPS and touch on a real phone**: to measure (the owner's override: no device run in this pass).
- **Short names**: the landing pad's hangar branch (13 F.1) gets "Nhà chứa" (the full "Nhà chứa máy bay" is
  16 characters).

## 13E. Muzzle, launcher and missile-tail audit from the model files (2026-09-29)

The owner (on an older build): the armoured car's flash off its barrel, the rocket technical's not at its launcher,
tanks' "in the middle of the gun", the flame tank and the mortar wrong, missiles' tail fire not on the missile
(the thermobaric launcher). The ask: review everything, measured from the model files, not from pictures.

- **The audit (`MuzzleGeometryAudit`, Editor).** It covers every armed vehicle, elite, boss and tower: 126
  vehicles and 284 firing mounts, plus 36 on the high-detail `_hd` variants. Each is spawned through the
  game's own path: `ViewRegistry`, `ModelLibrary`'s merged template and launch points, and `VehicleView.MuzzleOf`'s
  slot mapping (the k-th mount of a slot, twin barrels in turn, pods and rails in turn, spots on a face). Every
  point a mount fires from is measured against the model's own triangles: the imported glTF meshes per part,
  before the per-material merge, placed on the spawned model's posed transforms.
  - *Which geometry:* only the muzzle's moving group, from the node hierarchy (its `Turret`, `Mount_` or
    `Part_`; the whole model for a hull or aircraft gun). The coax's line next to the main barrel and
    aircraft pylons no longer confuse it.
  - *Where the barrel ends:* along the line the flash is drawn on (`DrawnBarrelOf`), eight rays out sideways
    tell whether the line runs inside a barrel, tube or pod. The open end is where that stops, bisected to 1 mm.
  - *Off axis and angle:* from the same rays, the line's offset from the barrel's middle, and the barrel's own
    axis (its middle at the tip and 0.12-0.45 m back).
  - *Faces of tubes:* judged on the face itself (the front-most hit of rays from ahead, so a ray down a bore
    does not count) and on its normal.
  - *Bombs and drones:* must only be released on the model.
  - *Limits (drawn metres):* -0.08 to +0.15 along, 0.05 m or half the radius across, 6 degrees.
  - *Output:* `-executeMethod MachineBrigade.Editor.MuzzleGeometryAudit.Report` writes `Docs/muzzle-audit.md`,
    one row per mount (muzzle node, points, ahead of tip, off axis, axis angle, verdict, part, notes).
- **Counts.** The first run found 95 of 284 mounts wrong (11 of 36 on `_hd`). Now 34 (1 on `_hd`).
  - 61 fixed and none broken; every mount was compared against the first run after each change.
  - Of the 61, 45 are real fixes. 16 are bombs and drones the first run judged as if fired down a barrel.
  - The owner's list is right on every mount: armoured car, rocket technical, every tank (main gun on its
    tip, coax on its MG), flame tank, mortar, thermobaric launcher, MLRS, artillery, IFV, heavy rocket
    artillery, ATGM carrier, attack and scout helicopters.
  - On the older build the owner saw, the tanks' main-gun and armoured car's muzzles were already on their
    tips (12I). What read wrong there was how the flash was drawn, fixed in 12A and 12I.
- **Fixes.** They are general, in `ModelLibrary`, `VehicleView` and `WeaponEffects`, with no per-vehicle code
  and no balance data.
  1. *Launch faces on the real face.*
     - The fault: a face of tubes' launch point was the front of its bounding box, and the spots were spread
       in the turret's level plane. On a raised box (MLRS, missile batteries, rocket turrets, the rocket
       technical, the heavy rocket artillery), the point and most spots sat in the air ahead of the lower
       tubes. Their line ran 5-51 degrees off the tubes.
     - The fix: `ModelLibrary.Front` takes the face part's principal axes (a flat face gives its normal, a
       long pod its axis). It puts the point on the face plane through its front-most vertex and turns it
       square to the tubes. `MuzzleOf` then spreads the spots across that plane.
     - Pods and rails keep their bounds' front, since they sit level on pylons.
     - Before and after (ahead of the tip, angle):

       | Launcher | Before | After |
       |---|---|---|
       | MLRS | +0.23 m, 51° | -0.02 m, 0° |
       | Rocket technical | +0.21 m, 5° | 0.00 m, 0° |
       | Heavy rocket artillery | +1.61 m, 13° | 0.00 m, 0° |
       | Missile battery (3 variants) | +0.66 m, 33° | +0.03 m, 0° |
       | Rocket turret (3 variants) | +0.26 m, 15° | +0.06 m, 0° |
       | IFV's ATGM | 12° | 0° |
       | Hive's SAM | +0.35 m | +0.04 m |
       | Inferno's thermobaric box | 14° | 0° |
  2. *Twin and quad guns built as one part* fire from each barrel.
     - The fault: the Blender tools put one `Muzzle_` between the barrels, so every flash was lit in the air
       between them. The audit read this as the muzzle floating 1.2-1.5 m ahead: walking back from the gap,
       it met the mount's box. `ModelLibrary.AddBarrelPoints` fixes it.
     - How barrels are found: from the part's connected pieces, welded by position, that are long, thin, and
       run along the muzzle beside it. A barrel and its brake count as one.
     - What it does: one launch point on each barrel's tip. `VehicleView` fires any weapon from them in turn,
       and another mount of the slot keeps its own muzzle.
     - Left alone: recoiling parts (`Main_cannon`, `Main_cannon_2`), which VehicleView's twin barrels already
       handle.
     - Before and after (ahead of the tip):

       | Gun | Before | After |
       |---|---|---|
       | Behemoth and Inferno twin flak | +1.48 m | -0.06 m |
       | Mobile fortress flak | +1.18 m | -0.05 m |
       | Bastion's four twin autocannons, Hive and silver bug flak | no barrel on the line | -0.06 to -0.07 m |
       | Heavy bomber's 2×2 tail guns | 0.77 m ahead (between the barrels) | -0.02 m |
       | Attack jet's twin cannon (and elite, `_hd`) | +0.40 m | -0.01 m |
       | Mega gunship's guns | +0.18 m | 0.00 m |

     - One visible change in play: a boss flak stream now alternates between its barrels.
  3. *Muzzles turned along their barrels.*
     - The fault: the Blender tools place `Muzzle_` empties by position only, all facing the model's front.
     - The fix: `ModelLibrary.AlignMuzzles` turns a muzzle along the long, thin piece of a sibling part it
       sits on, when that barrel is built 10 degrees or more off the front. The piece can be the part itself,
       the part's side round the muzzle, or one of its connected pieces.
     - Covered: the mortar tube, the BMPT's grenade launchers, raised flak, and the AC-130s' side guns
       (depressed, inside one `Guns` part). Missile and rocket racks are left to the launch points.
     - The mortar's rest pitch now comes from the tube itself; the line from the trunnion to the muzzle ran
       6 degrees off it.
     - `VehicleView.DrawnBarrelOf` and `BarrelDirectionOf` use an aligned muzzle's or a measured launch
       point's forward. Flashes, the lobbed arc and a launch then face the way the barrel is drawn, raised,
       turned and banked.
     - Before and after (angle): mortar 6.2 → 0.0 degrees; BMPT grenade launchers 9.1 → 0.0; AC-130 guns
       and ramp 7 → 0.
  4. *Side guns.*
     - The fault: a door gunner or AC-130 gun (`aim` Left or Right) with no barrel direction of its own was
       drawn firing out of the nose.
     - The fix: it now faces its side. Gunship helicopter door guns: +0.22 m ahead and 0.12 m off → +0.03 m
       and 0.06 m. A second main mount firing from one of the main gun's twin barrels is raised with that
       gun's elevation.
  5. *Air-to-air missiles without their own rail* (Apache, elite Apache, fighter, A-10, Ka-52).
     - The fault: they left from a point 12 % beyond the outermost store, in thin air beside the wing.
     - The fix: they leave from the outermost store. Ka-52's Igla: 0.31 m off → 0.00 m.
  6. *Missiles and direct-fire rockets leave along their tube.*
     - The fault: a raised SAM box's missile left sideways out of the box.
     - The fix: the missile leaves along the tube and bends onto the target (`WeaponEffects.Leave`, the
       curve's middle control point). Pointing at the target, it flies the old path, arc included.
     - Their ignition and backblast face along the tube, and a second launcher's artillery rockets lob along
       their own tubes.
- **Missile tails.**
  - *The models:* every munition the game launches (39 models) has its nose on +Z, its axis through
    x = y = 0, and its nozzle at the bounds' tail, within 3 cm (the S-8's fins reach 3 cm past its nozzle).
    So `shot.Tail = bounds.min.z` is the drawn nozzle at every `projectileScale`.
  - *Real frames* (`PlumePlayCheck`, Play mode): Unity's own player loop at a fixed 30 and then 60 fps
    (`Time.captureFramerate`). The effects run in `Update` as in the game, Unity's particle update follows,
    and a camera follows the round so the looping plume systems are never culled.
    - Measured: each frame at the end of `PostLateUpdate`, just before the draw, the core born that frame
      sits within 1.4 cm of the drawn tail and on its line.
    - Rounds measured: the thermobaric rocket and the MLRS rocket on their lobbed paths, a Hydra, a Buk and
      a TOW.
  - *EditMode test:* `MissileFlightTests.PlumesStayOnTheirTailsFrameByFrame` repeats this in EditMode
    (within 1.2 cm).
  - *Where a gap can come from:* one long frame puts the flame a frame's travel behind, 1.4-3.4 m. That is
    only a hitch in the game. `ProjectilePool` caps its step at 0.1 s and Unity's particles do not.
  - *The old sheets:* `MissileShots` has always stepped at 60 fps, so the gap was not the tool jumping to
    each moment. Cropped at the same zoom, the old thermobaric sheet and the new one both show the core on
    the tail.
  - *Result:* no in-game gap was found, and the plume was not changed.
- **Tests.**
  - `MuzzleAuditTests` (new): the owner's list must be right on every mount. Any other wrong mount must be on
    its known list with the reason, so a model re-export, a slot mapping or a launcher change that moves a
    muzzle off its barrel fails. A known one that becomes right must be taken off the list. The file also
    holds `TiltedLauncherFacesLaunchAlongTheirTubes`.
  - `PlumesStayOnTheirTailsFrameByFrame` (new, in `MissileFlightTests`).
  - Targeted run: FlashTests, MuzzleTests, MissileFlightTests, EffectsTests, BlastSizeTests and the new ones
    pass, 38 of 38. FlashTests: every flash rides its drawn muzzle (0.000 m) with the barrel points, and
    tongues stay within 4.6 degrees.
  - PlaySmoke (menu 10 s, Conquest 30 s): 0 errors.
- **Left (34 mounts, 1 `_hd`; in `MuzzleAuditTests.Known` and `Docs/muzzle-audit.md`).** These need the models'
  empties moved or guns added in `Tools/blender` and a re-export (the Blender lane):
  - *No gun on the model:* the trucks' roof MG (ammo carrier, supply truck). They fire from `RoofFront`.
  - *No tube on the muzzle's line:* boss racks and pods (mobile fortress rockets and missiles, gunship
    helicopter's pods and missile tubes, heavy bomber's cruise missile, ballistic launcher's missile,
    aa_turret.sam).
  - *Stored missiles and aircraft stores:* sunk in their racks or ahead of them (behemoth racks, heavy AA's
    pack, stealth bomber's JASSM, fighter's AIM-120 and the strike drone's missiles, launched from the store's
    nose; mega gunship's pods).
  - *Single cases:*
    - the Tempest's railgun, whose muzzle sits between its open brake jaws, 0.38 m past the core;
    - silver bug's coilguns and laser lens;
    - elite Grad's face, 0.09 m inside;
    - drone mothership's flak (one mount has no barrel on its line);
    - armored train's pods, 0.42 m off.
  - *Angles over the limit:* aa_turret's twin flak (6.1 degrees, its rest pitch from the trunnion line);
    sky fortress's cannons (7 degrees); elite MLRS (22); the SAM launcher (17). In the render the SAM
    launcher's launch line runs along its raised box, so the audit is probably reading the tube rims'
    bevels. Left for a look.

## 13F. The last model muzzles, fixed in Blender (2026-09-29)

13E left 34 mounts (1 on `_hd`) whose barrel, tube or launcher was wrong in the model itself. This pass fixes 23 of
them in the Blender builders (`Tools/blender`) and re-exports the models; 12 stay on `MuzzleAuditTests.Known`.

- **How the models were rebuilt.** Blender 4.5.14 (`C:/Users/Winka/Tools/blender-4.5.14-windows-x64`), one model at a
  time through `build_assets.all_builders()` and `mb_round6.finish` (post steps and suffixed pivot names, as the round 6
  builders export). A rebuild of the untouched sources matched every committed file part for part (names, parents,
  positions, bounds, triangles). The one exception is the heavy AA's tyres, whose later bevel change had never been
  exported. Scales, footprints and the sim data are unchanged.
- **What was wrong, by kind.** None of these were the audit misreading bevels.
  - *Launchers too close together.* `ModelLibrary.LauncherGroups` splits a launcher part into launchers at gaps of
    0.35 m across the model. The gunship helicopter's two pods on a wing, the fighter's two AMRAAMs on a shoulder beam,
    the strike drone's missile pair and the mega gunship's pods stood 0.05-0.33 m apart. Each pair was read as one
    launcher, and rounds left from the air between them. They now stand 0.35 m or more apart.
  - *One box read as two launchers.* A box has vertices only at its sides, so the behemoth's racks, the heavy AA's
    packs and the armoured train's rocket box split into their two side walls. The behemoth and heavy AA boxes are
    now `Rack_box` / `Pack_box`. A liner inside the top middle tube (`Missile_racks`, `Missile_pack`) is the launcher,
    and the racks and packs are level so a launch leaves along the tubes. The train's box is `Rocket_box` and
    launches from its tube face.
  - *Parts of a launcher that did not elevate with its tubes.* `BarrelPattern` elevates `Tubes`, `Pod`, `Launcher_*`
    and similar parts, and leaves `Missile_box`, `Box_frame`, `Missile_pack` and `Pod_frame` behind.
    - The SAM launcher's tube mouths swung 17 degrees out of their boxes at rest (the 17 degrees 13E put down to
      bevels). The boxes, frames, lugs and cradle are now `Launcher_*`, and a bridge plate closes the gap between the
      two faces, where spots on the face fell onto the cradle.
    - The heavy AA's ring mouths no longer elevate apart from their packs.
    - The elite MLRS's bands and lugs elevate with its pods.
  - *Stores and barrels in several parts.*
    - The JASSM's dark nose is now part of `Standoff_missile`, so it launches from the nose tip, not 0.5 m back.
    - The mothership's flak barrels run through their hiders; a 0.2 m hider is too short to count as barrel.
    - The sky fortress's 40 mm barrels run into their muzzle cones. At 1.3x the barrel piece ended 2 cm short of
      `AlignMuzzles`' reach, and the guns are depressed 11.5 degrees, not 8, so the muzzle is turned along them.
    - The heavy AA's four barrels each have their own hider (`Muzzle_brake` .. `_4`), so they fire in turn from their
      own openings, not between each gun's pair.
  - *Muzzles off the end.* The Tempest's railgun muzzle is now at the core's end, at the root of its open jaws; it
    was 0.32 m out between the jaw tips. The sky fortress's ramp muzzle is on the middle tube's mouth. The Grad's dark
    face plate sits 6 cm inside the mouths, not 10.
- **The trucks' roof gun: a new model, `armed_truck`.**
  - The ammunition carrier and the supply truck used the civilian truck prop. It is built lying along X, as the map
    places it, so both units drove sideways, and it had no gun, so they fired from a point over the roof.
  - `armed_truck` is the same box truck built along the vehicle's front, with a team-painted cab and stripe and a
    small ring-mounted MG over the cab (`Turret`, `Muzzle_main`, from `mb_support._rws_turret`). The ring sits far
    enough forward that the barrel clears the taller cargo box when it turns round.
  - `balance.json` changes only the two units' `"model"` field. The civilian `truck` prop is unchanged.
- **Fixed (23 mounts, before and after).** Ahead of the tip, off axis and angle, as `Docs/muzzle-audit.md` reports them.

  | Mount | Before | After |
  |---|---|---|
  | ammo_carrier, supply_truck (main) | no gun on the model | 0.00 m, 0.00 m, 0° (`armed_truck`) |
  | gunship_heli rockets | no pod round the line | +0.06 m, 0.00 m, 0.4° (4 pods) |
  | gunship_heli missiles | no tube round the line | -0.02 m, 0.00 m, 2.8° |
  | fighter_jet AIM-120 (and `_hd`) | +1.00 m | -0.06 m, 0.00 m, 1.4° (6 rails) |
  | stealth_bomber JASSM | 0.51 m inside | +0.07 m, 0.02 m, 0° |
  | sam_launcher | +0.11 m, 17° | +0.04 m, face, 0° |
  | heavy_aa twin 30 mm | no barrel round the line | 0.00 m, 0.00 m, 0.3° (4 barrels) |
  | heavy_aa SAM | 0.17 m off, 12° | -0.04 m, 0.00 m, 0° |
  | behemoth racks (2 mounts) | 0.20 m off, 47° | -0.06 m, 0.00 m, 0° |
  | strike_drone missiles | +0.62 m | -0.04 m, 0.00 m, 0° |
  | mega_gunship pods (2 mounts) | +0.62 m, 0.14 m off | -0.05 m, 0.00 m, 0° |
  | armored_train rockets | 0.42 m off, 7° | -0.01 m, face, 0° |
  | elite_grad | 0.09 m inside | -0.06 m, face, 0° |
  | behemoth_tempest railgun | +0.38 m | +0.04 m, 0.00 m, 2.3° |
  | drone_mothership flak (2 mounts) | no barrel; 0.09 m inside | 0.00 m, 0.04 / 0.00 m, 4.7 / 0° |
  | sky_fortress 40 mm (2 mounts) | 7.4° | +0.03 m, 0.00 m, 0° |
  | sky_fortress ramp | +0.19 m | +0.03 m, 0.00 m, 0° |

- **Left (12 mounts, on `Known` with their reasons).** Each needs more than a model tweak.
  - *Mobile fortress (rockets ×2, missiles).* Its two rocket batteries are raised boxes, one per `Mount_rocket`.
    Paired launchers only launch along the muzzle's level forward. A face of tubes is found once per slot over the
    whole model, so the two batteries, and the missile slot too, read as one face between them. This needs per-mount
    faces in `ModelLibrary`.
  - *aa_turret twin flak (×2 variants), aa_turret.sam (×2), ballistic launcher, heavy bomber's cruise missile.* An
    elevation rest pitch taken from the trunnion line, and launchers with no tube modelled round their muzzle (an
    erector, a bay). Each is its own rig question.
  - *Silver bug (laser, coilguns).* Four coilguns on one part, spread round the saucer, and a lens 5 cm off.
  - *Elite MLRS (22 degrees).* The bands now elevate with the pods, but the face reading is unchanged. It needs a look
    at which surfaces the face rays meet.
- **Tests.** `MuzzleAuditTests.Known` is down to 12, and `TiltedLauncherFacesLaunchAlongTheirTubes` no longer skips
  the SAM launcher. The cards of every re-exported model were rendered again.

## 14A. Prompt 15: armour levels, penetration, damage types (sim) (2026-09-29)

The simulation and data half of prompt 15 (parts A, B, C, C.9, C.10 and the combat-value re-run); the icons and
screens (D, E) are the interface half and are recorded on their own. The owner's rule on test time wins over the brief's
"5 seeds for everything": the combat-value measure ran on one seed (13) and a campaign spot check on a few missions; the
rest is listed for the testing phase (14A.Z). The pure helpers the interface reads are `Sim.Content.Matchup` and
`Sim.Content.Armour`; `ExportGameDoc` carries every new field for the PDF.

### A. Armour levels

**A.1 The model.** Every unit has an armour level 0-4 on each face (`ArmourLevels`: front, side, rear, top). Data
`"armour"`: one number, the front (a vehicle's side one less, rear and roof two less, never under 0; a tower, a building,
an aircraft or a boss part the same all round), or four `[front, side, rear, top]` where the real vehicle differs. The
old `"armor": "Light/Heavy/Air"` is gone from the vehicles; `ArmorClass` stays as a broad class the roles, the commander
and the cards read, now worked out: Air (flying), Structure (a fixed defence that is no boss, unless `"structure": false`),
Heavy from front level 3, Light for 0-2. The light tank, which the class inference would have turned Light, keeps
`"class": "Tank"`. Props keep their class (Structure or a wreck's Heavy) with a level: 1 by default, `"armour"` for the few
that differ.

**A.1 table (front / side / rear / top; one number = the vehicle default or all round):**

| Level | Vehicles |
|---|---|
| 0 | scout jeep, rocket technical, ZU-23 technical, car bomb, ammunition carrier, supply truck |
| 1 | armoured car, SP artillery (an M109: aluminium), MLRS, heavy rocket artillery, ballistic launcher, mortar carrier, anti-air (Gepard), gun-missile AA, SAM launcher, long-range SAM, Iron Beam, ATGM carrier, FPV carrier, Lancet truck, Shahed truck, railgun truck, mine layer, smoke carrier, EW jammer, counter-battery radar |
| 2 | light tank, IFV, wheeled gun, command vehicle, engineer vehicle, sapper |
| 3 | battle tank, twin-barrel tank, BMPT, tank destroyer, flame tank (a tank hull), thermobaric launcher (a TOS-1A on a T-72 hull), siege tank; armoured bulldozer 3/3/2/2 (a D9R's cab is armoured all round) |
| 4 | heavy tank, Titan; turtle tank 4/3/3/3 (its shed covers the sides and the roof) |

| | Aircraft (all round) |
|---|---|
| 2 | A-10 (the "flying tank") |
| 1 | Su-25 (attack jet), Mi-24 (heavy gunship), Ka-52, AH-64 (attack helicopter) |
| 0 | scout helicopter, fighter, bombers, AC-130, drones |

| | Towers and structures (all round; an embrasured front one more) |
|---|---|
| 4 | HQ; heavy fortress and camp bastion 4/3/3/3 (embrasured concrete) |
| 3 | gun turret, super-gun, dragon's teeth |
| 2 | ATGM tower, AA turret, drone hangar, repair bay, ammunition depot, airfield hangar; MG bunker and hidden gun pit 3/2/2/2 (embrasured) |
| 1 | guard tower, fallback post (sandbags), artillery emplacement, rocket battery, C-RAM, Patriot battery, EW tower, airfield, logistics station, radar station, fire-control post |
| 0 | minefield |

Props: 1 (houses, walls, sandbags); a fortress gate, the base wall, the base gate and the command HQ 4 (the brief's
"fortress walls, gates and HQ"); a tank or artillery wreck 3. A tower keeps the structure kind, so high explosive keeps its
extra on it (C).

**A.4 Aircraft** stay their own kind of target (air) and have a level. The brief's 1-2 for the armoured ones went in at 2
first; the re-run (Z) showed every anti-air vehicle losing a fifth of its value per CP in the air group, so the Su-25, Mi-24
and Ka-52 are 1 (they still shrug off rifle-calibre fire and much of the 23 mm) and only the A-10 keeps 2.

**A.5 Boss parts** have their own level (data `"armour"` on each part), by kind, never more than the boss's front:
drill and locomotive 4; guns, main guns, turrets, coilguns, railguns, mortars, howitzers, engines, tractors and ramps 3;
flak, rockets, missiles, launchers, bays, hangars, shields, flamers, lasers, SAMs, stations 2; radars, antennas, fans,
rotors, EMP emitters and UAV bays 1. Ground bosses are 4 (the trains 4/3/3/2, the hovercraft 3, the rail supergun 3 after
the spot check, Z); air bosses 2.

**A.6 Elites** are a level thicker in front than their card (at most 4; an aircraft at most 2) and take 1.35 times their
card's health instead of 1.6. The power band of prompt 8 (1.8-2.2) holds: 1.35 health x about 1.25 for the thicker front
(a gun that pierced by a level now does 0.75) x 1.25 damage is about 2.1. The elite heavy tank, already at 4, keeps 1.6.

### B. Penetration and the damage a hit does

**B.1 Penetration levels** (`WeaponDef.Penetration`, data `"pen"` on every weapon; `Armour.DefaultPenetration` gives the same
by family and size for hand-built weapons): 0 a 7.62 mm machine gun; 1 12.7-14.5 mm, flamethrowers, 20-23 mm flak; 2
autocannons 20-40 mm (and the 57 mm), 30-57 mm flak, unguided rockets 70-122 mm, 105-120 mm shells, 120 mm mortars, 110-250
kg bombs, short-range anti-air missiles, the Iron Beam; 3 76-105 mm guns, light ATGMs (Konkurs, Griffin, MAM-L), FPV drones,
the GAU-8's depleted uranium, 152-155 mm shells, 220-300 mm rockets, 500 kg bombs, the Shahed, cruise missiles, medium and
long-range SAMs, the GBU-39 (a penetrator); 4 120 mm and up (darts), heavy ATGMs (TOW-2, Kornet, Ataka, Hellfire, Vikhr,
Maverick, Kh-29), the Lancet, railguns, 203 mm shells, 240 mm mortars, 900 kg and up, the Iskander. Shaped charges pierce by
their warhead, not their size.

**B.2 The multiplier** by the round's level against the level of the face it strikes: a level or more above 1; level
0.75; one under 0.4; two under 0.15; three or more under 0.05 (data `damageTable.penetration`). Equipment adds part
levels (C.9): a part level lies between its two neighbours.

**B.3 The face struck** (`DamageSystem.FaceOf`): direct fire by the shooter's bearing (within 50 degrees of the nose the
front, of the tail the rear, else the side: the old arcs); the **roof** for top-attack weapons (`"topAttack"`: the
top-attack Kornet, every diving drone), for bomblets, for everything lobbed or dropped (shells with a minimum range,
artillery rockets, bombs), for called strikes and mines (under the belly), and for an aeroplane's direct fire (it dives on
its target; a helicopter fires from low and stand-off and takes the face turned to it); a blast the face turned to it. The
old facing factors (side x1.25, rear x1.6) are gone: the levels do it (the brief's A.2). Kept on purpose: the aeroplane's
roof hit keeps the jets' cannons at what prompt 13 measured (the GAU-8 and the GSh-30 were armour-piercing, x1 on heavy;
now pen 3 and 2 against a battle tank's roof, 1).

**B.3 Blasts.** A blast's fragments pierce as a heavy machine gun (level 1, the brief's "fragments of high explosive")
against vehicles on the ground, whatever made it: a shell's splash, a called strike, a cook-off. Against structures and
aircraft a blast keeps its round's level (it is the blast that knocks a bunker down). A car bomb's blast carries its
charge's level (4) for the same reason. Damage that says nothing of its round (no weapon, no level, no kind: a scripted
kill, the firing range's damage, a test) meets the damage type's table only.

**B.4 Prompt 13's autocannon row is gone** (penetration does it: a 30 mm is 2, 0.4 on a battle tank's front, 0.75 on its
side). Prompt 13's calibre damage scale is kept as it was: no round's damage changed.

**B.5 The damage a hit does** = the round's damage (the calibre scale) x the penetration multiplier x the damage type
against the kind of target (C.7) x equipment, modules, elites, weapon bonuses and the rest as before. Targeting and the
overkill check estimate the same way from where the shooter stands (`DamageSystem.Estimate`), so a gun prefers a target it
pierces.

### C. The six damage types

**C.1-C.6** `DamageType`: Kinetic 0, ShapedCharge 1 (was ArmorPiercing), HighExplosive 2, Fire 3, Fragmentation 4 (was
Flak), Energy 5 (new). The numbers stay where the meaning carried over because saved resistance lines are numbers
(`StatId.ResistKinetic + type`; energy's resistance is appended, `Stats.Resist`).

**C.7 The damage-type table** (data `damageTable`; armour is no longer in it):

| Type | Ground | Air | Structure |
|---|---|---|---|
| Kinetic | 1.0 | 0.3 | 0.6 |
| Shaped charge | 1.0 | 0.3 | 0.6 |
| High explosive | 1.0 | 0 | 1.5 (thermobaric 2.0) |
| Fire | 1.5 | 0 | 1.0 |
| Fragmentation | 0.5 | 1.5 | 0.1 |
| Energy | 1.0 | 1.5 | 0.5 |

Reasons: kinetic and shaped charges on structures 0.6 keep a tank gun on a level-2 tower where the old AP row had it
(0.6) and put a 12.7 mm (0.24) and a 30 mm (0.45) either side of the old 0.3 and 0.4; air 0.3 as before. Fragmentation on
the ground 0.5 keeps flak where the old row was against armour (a Gepard 0.2 on a battle tank's front against 0.1, 0.5 on
the unarmoured against 0.4) while level 0-1 targets are what it is strong against. Fire went in at 1.25 and is 1.5 after
the re-run (its penetration of 1 makes it weak on thick armour, the brief's point; 1.5 makes it strong on 0-1). Energy 1.5
in the air keeps the Iron Beam's damage.

**C.3 The thermobaric tag** (`"thermobaric"`: the TOS-1A's rockets, the 122 mm thermobaric battery, the Inferno's): 2.0
instead of 1.5 on structures; its blast falls off half as much (0.625 at the edge instead of 0.25); it reaches half into a
gun pit's hole; cages do not stop it. The 122 mm battery's own x1.3 on structures was dropped (the tag gives x1.33).

**C.4 Fire burns on:** a fire hit sets its target burning for 30 % of what got through, over 3 s (fires add up, as
Incendiary Rounds do). It is worked out after armour, so it is weak on thick armour too.

**C.8 Every weapon reclassified** (the full table is 14A.W): kinetic for machine guns, autocannons, every tank gun's dart
(the old armour-piercing shells), the jets' cannons, railguns and the blows (blade, drill); shaped charge for anti-tank
missiles, air-to-ground missiles, FPV drones, Lancets, the elite heavy tank's HEAT round and mines; high explosive for
howitzers, mortars, rockets, bombs, cruise and ballistic missiles, the Shahed, the 40 mm grenade and the AC-130's and
the Hive Carrier's HE cannons; fire for the flamethrowers; fragmentation for flak, airburst, C-RAM, the fighter's cannon and
every anti-air missile; energy for the Iron Beam and the Silver Bug's laser (fire before). The view keeps the old looks:
`"piercing"` marks the rounds that were armour-piercing (sparks on impact), and the Iron Beam keeps its flak sound.

**C.9 The counters** (the brief's table, `ArmourTests.CountersFollowTheTable`):

| Defence | Stops | Does not stop |
|---|---|---|
| Reactive armour (module) | 40 % (Epic) / 55 % (Legendary) of a shaped-charge hit; a tandem warhead defeats it | kinetic, high explosive, anything else; mines |
| Reactive blocks (trait) | half a shaped-charge hit, a block at a time | kinetic rounds (they were "armour-piercing" before) |
| Cage (Slat Cage, Slat Screens; the turtle tank's shed against drones) | its share of shaped charges on rockets, missiles and drones | kinetic rounds, a HEAT shell, thermobaric blasts, mines |
| APS (Trophy, point defence) | missiles, drones, direct-fire rockets (a point-defence laser and the C-RAM also artillery rockets; the C-RAM a share of the shells) | tank shells, bullets, beams (energy); a point-defence laser in smoke, or aimed into it |
| Flares | missiles (by their seeker's flare resistance) | drones, bullets, flak, beams |
| Smoke | 80 % of a beam's damage into it or out of it | everything else |
| Jammer | guided rounds (missiles and drones) go wide | unguided rounds, beams |

The reactive armour module was 12-18 % off every hit; against shaped charges only it had to be stronger to be worth a
slot, and it fits ground vehicles only now (there is nothing to stop on an aircraft).

### C.9 Equipment by level, and the migration

| Piece | Before | Now |
|---|---|---|
| Tungsten Penetrator (vehicles), Sabot Rounds (towers) | +4-15 % damage on heavy vehicles | +0.4-1 penetration level (a whole level at Legendary's top), all its weapons |
| Appliqué Steel | -5-18 % kinetic damage | +0.4-1 armour level on the sides and rear |
| Armoured Tub (aircraft) | -6-22 % flak damage | +0.4-1 armour level all round |
| Composite Add-on, Composite Casemate | -4-15 % armour-piercing | -4-15 % shaped charges |
| damage vs light / heavy vehicles (sub-stat) | by class | against a face of level 0-2 / 3-4 |
| armour-piercing / flak resistance (sub-stat, brand) | | shaped-charge / fragmentation resistance (same saved numbers) |
| Slat Cage (Resist Rocket) | rockets, missiles, drones | their shaped charges only, not thermobaric |
| Tandem Warhead | +10-15 % on heavy vehicles | on a face of level 3-4 |
| Reactive armour module | -12-18 % of everything, any vehicle | -40/55 % of shaped charges, ground vehicles |

The Proximity Fuze and the Airburst Rounds keep "against aircraft" and "against drones": aircraft are still a kind of
target. Levels print as levels ("+0.72 penetration level"). **Migration** (gear version 3 to 4,
`Prompt15MigrationTests`): the base types and stat numbers keep their ids, so every piece keeps its id, slot, rarity and
level and reads its new line; a piece a branch wears that no longer fits it (reactive armour on the Air branch) becomes one
that fits in the same slot, of the same rarity and level, and stays on; a second load changes nothing.

### C.10 The commander counter-picks by penetration and damage type

`ConquestAi`'s counter score, for every AI with a counter weight (Normal and up; the prompt 13 buy scoring otherwise
unchanged): the ground enemies it has seen (and the player's deck on Very Hard, at half weight) are counted by the armour
they show, front x roof. A card's fit is its main weapon's penetration multiplier times the type against each of them
(the roof for a weapon that strikes it and for an aeroplane), weighted by their value, a secondary at half; it scores
(the ground share) x (its fit - 0.85 x the fit our army already has) x 8, which replaces the old "heavy" and "light"
answers. Against the defences seen: APS cuts the missiles', rockets' and drones' cards (-2.5 at full cover), reactive armour
or a cage the shaped charges' (-2), smoke the beams' (-2), jammers the guided (-2), flares the anti-air missiles' (by their
seeker). The old class-based rules for aircraft, artillery raiders and anti-air stay. `CounterBuyTests` pass on it (against
heavy tanks it buys tank destroyers and battle tanks, no anti-air).

### R. The combat-value re-run and the rebalance

Prompt 13's measure (`CombatValueMeasure.MeasureTheRoster`, `MB_BALANCE=1`), one seed (13), the whole roster, before and
after: "Prompt 13" is its shipped F3 file, "first" the new rules on prompt 13's roster, "shipped" after the changes below.
Ground value per CP unless marked "air" (raw files: `Docs/balance/combat_value_p15*.tsv`; the table in
`Docs/COMBAT_VALUE.md` section 4).

The mechanisms that moved things, measured: tank guns and cannons now do all their damage to the unarmoured and lightly
armoured (the old AP row had 0.75 on light); 7.62 mm fire does a third of what it did to armoured cars; autocannons hit a
tank's side three quarters and its front 0.4; fire is weak on thick armour; a blast's fragments pierce one level; armoured
aircraft shrug off machine guns.

| Changed | Why (first → shipped, value per CP) |
|---|---|
| IFV 5 → 6 CP | its 30 mm now pierces light armour and tank sides, and its level 2 shrugs off machine guns: 188 → 118 (+52 % → -4 %) |
| light tank 4 → 3 CP, 400 → 460 HP | its 57 mm lost the old armour-piercing row (0.4 on a battle tank's front): 62 → 150 (-61 % → -6 %) |
| flame tank 5 → 4 CP; fire on the ground 1.25 → 1.5; fire burns on (C.4) | fire of level 1 on thick armour: 190 → 289 (-47 % → -19 %; an anti-light specialist: light group 743) |
| scout helicopter 5 → 4 CP | its 7.62 mm on armoured cars: 197 → 243 (-38 % → -23 %) |
| car bomb 3 → 2 CP; its blast carries the charge's penetration (B.3) | fragments of level 1 on tanks and towers: 48 → 87 (-47 % → -4 %) |
| rocket technical 190 → 230 HP | 192 → 209 (-21 % → -15 %) |
| SAM launcher 400 → 460 HP | aeroplanes now hit its roof (level 0): air 150 → 155; `CounterTests` "SAM beats jets" failed at 400 and passes at 460 |
| Su-25, Mi-24, Ka-52 armour 2 → 1 (A.4) | anti-air lost a fifth in the air: AA vehicle air 189 → 252 |
| rail supergun armour 4 → 3 | the spot check lost its mission (c4m06) at 4: the player's army could not get through a level-4 front in 20 minutes; won at 3 (16.9 min) |
| every card's `"value"` (the commander's weight) | recomputed from the shipped run the way prompt 13 did (per CP over its class's median, 0.5-1.5; anti-air and the fighter on air) |

Tried and put back: the fighter at 14 CP and the long-range SAM at 13 (they rose +25 % and +33 % in the air on this seed with
no mechanism behind it; the measure's groups are lumpy, 18 CP rounded to whole vehicles, and a CP step halved their groups).
Left for a multi-seed look (Z): the long-range SAM (air +33 %), the fighter (+25 %), the gunship helicopter (-21 %, inside
the helicopters' band), the wheeled gun (+27 %, now mid-band after being left under it on purpose), the sapper (-50 %:
a support, judged by its aura) and the scout jeep (-26 %: a scout).

After it, per role (value per CP): light 105-118; tanks and heavy 289-525; tank hunters 278-461; artillery 209-446;
helicopters 243-415; aircraft 325-439 (the recon drone apart); mobile anti-air in the air 155-252, the long-range SAM 545.

**The campaign spot check** (`CampaignTests.WinRateOverFiveSeeds`, `MB_SEEDS=1`): c1m02, c2m05 (Behemoth), c3m05 (Iron
Bird), c5m06, c7m05 (Silver Bug), c8m05 (Doomsday Train) won; c4m06 (rail supergun) lost at level 4 and won at 3.
**Siege** (`ModeBalanceMeasure`, `MB_MODES=Siege`, one seed): won 3 of 3, 7.1 / 16.2 / 9.4 min (prompt 13: 13.3 / 14.0 / 9.2).

### T. Tests

New: `ArmourTests` (every unit and weapon has the new fields and the data states each weapon's `"pen"`; the multiplier
row, part levels, the high-explosive and thermobaric structure values; faces, top attack, the roof for lobbed rounds,
round x penetration x type in battle, and the pure helpers against the battle; the counter table),
`Prompt15MigrationTests` (an old save's pieces, lines and loadouts). Updated for the new rules: `CalibreTests` (the
autocannon test reads penetration), `GearSimTests` (reactive blocks on a missile, shaped-charge resistance on a HEAT shell,
the guardian's share of what gets through), `GearTraitTests` (the tandem target nose-on; expectations from the multiplier),
`ElitePrompt8Tests` (1.35 or 1.6 health), and the compile-only renames in a dozen more. Run: Weapon, Combat, Calibre,
Counter (and CounterBuy), Aps, Content, Stores, CheckpointReplay, Armour, Prompt15, GearSim, GearTrait, ElitePrompt8:
all green. The full suite was not run (the owner's rule).

### Z. Left for the testing phase

- The full EditMode suite: suites that set exact damage numbers by the old table may need their expectations read from
  the multiplier (as `GearTraitTests` now does); not run.
- Five seeds for the combat value (the fighter, the long-range SAM, the gunship helicopter and the wheeled gun above), the
  whole campaign, the big campaign and every mode; the rail supergun's mission at level 3 (won in 16.9 of 20 minutes).
- Walls, gates and the HQ at level 4 in Siege and Defend (Siege won 3 of 3 on one seed; Defend not run).
- The equipment lab (`EquipmentLab`) with the level lines, and the elites' power band measured rather than reasoned.
- The design document export (`ExportGameDoc`) run for the PDF.

### W. Every weapon (type, was, penetration, form, tags)

K kinetic, SC shaped charge, HE high explosive, Frag fragmentation, En energy; "(was)" when it changed (AP armour-piercing). Tags: top (strikes the roof), guided, splash, cluster, thermobaric. Forms are `WeaponForm` (the icon's shape).

| Weapon | Real weapon | Type (was) | Pen | Form | Tags |
|---|---|---|---|---|---|
| mg_jeep | M2 Browning 12.7 mm | K | 1 | BulletBig |  |
| mg_coax | PKT / M240 7.62 mm | K | 0 | BulletSmall |  |
| hmg_roof | M2 Browning 12.7 mm | K | 1 | BulletBig |  |
| autocannon_30 | 2A42 30 mm | K | 2 | BeltedAutocannon |  |
| gun_57mm | S-60 57 mm (2A91) | K (AP) | 2 | Dart |  |
| gun_120mm | Rh-120 L/44 120 mm | K (AP) | 4 | DoubleDart | splash |
| turret_gun_120 | Rh-120 L/44 120 mm | K (AP) | 4 | DoubleDart | splash |
| atgm | BGM-71 TOW-2 | SC (AP) | 4 | Atgm | guided |
| flamethrower | flamethrower | Fire | 1 | Flame | splash |
| howitzer | M284 155 mm | HE | 3 | HeShell | splash |
| mlrs_rockets | M31 GMLRS 227 mm | HE | 3 | RocketBig | splash |
| flak_35 | Oerlikon KDA 35 mm (Gepard) | Frag (Flak) | 2 | Airburst | splash |
| sam | Starstreak / Stinger SHORAD | Frag (Flak) | 2 | Sam | guided, splash |
| heli_atgm | AGM-114 Hellfire | SC (AP) | 4 | Atgm | guided |
| heli_gun | M230 30 mm | K | 2 | BeltedAutocannon |  |
| heli_rockets | Hydra 70 mm | HE | 2 | RocketSmall | splash |
| autocannon_25 | M242 Bushmaster 25 mm | K | 2 | BeltedAutocannon |  |
| gun_105_long | 2A75 125 mm (2S25 Sprut) | K (AP) | 4 | DoubleDart |  |
| gun_152 | 2A83 152 mm | K (AP) | 4 | DoubleDart | splash |
| sam_long | 9M317 Buk | Frag (Flak) | 3 | Sam | guided, splash |
| mortar_120 | 2B11 120 mm | HE | 2 | MortarBomb | splash |
| technical_rockets | Type 63 107 mm | HE | 2 | RocketSmall | splash |
| grad_rockets | BM-21 Grad 122 mm | HE | 2 | RocketSmall | splash |
| atgm_heavy | 9M133 Kornet | SC (AP) | 4 | Atgm | guided |
| gunship_rockets | S-8 80 mm | HE | 2 | RocketSmall | splash |
| minigun | M134 Minigun 7.62 mm | K | 0 | BulletSmall |  |
| scout_rockets | Hydra 70 mm | HE | 2 | RocketSmall | splash |
| jet_cannon | GSh-30-2 30 mm | K (AP) | 2 | BeltedAutocannon |  |
| jet_rockets | Hydra 70 mm | HE | 2 | RocketSmall | splash |
| jet_bombs | FAB-250 (250 kg) | HE | 2 | Bomb | splash |
| drone_missile | AGM-114 Hellfire | SC (AP) | 4 | Atgm | guided |
| gun_155_sph | M284 155 mm | HE | 3 | HeShell | splash |
| thermobaric_rockets | TOS-1A 220 mm thermobaric | HE | 3 | RocketBig | thermobaric, splash |
| twin_30_flak | 2A38 30 mm (twin) | Frag (Flak) | 2 | Airburst | splash |
| hq_flak | 2A38 30 mm (twin) | Frag (Flak) | 2 | Airburst | splash |
| gun_140_twin | NPzK 140 mm (twin) | K (AP) | 4 | DoubleDart | splash |
| bomber_payload | FAB-500 (500 kg) | HE | 3 | Bomb | splash |
| bomber_tail_guns | M3 12.7 mm (quad tail) | K | 1 | BulletBig |  |
| stealth_payload | GBU-31 JDAM (907 kg) | HE | 4 | HeavyBomb | splash |
| gunship_105 | M102 105 mm | HE | 2 | HeShell | splash |
| gunship_40mm | Bofors L/60 40 mm | HE | 2 | BeltedAutocannon | splash |
| gunship_25mm | GAU-12 Equalizer 25 mm | K | 2 | BeltedAutocannon |  |
| gun_105_twin | L7 105 mm (twin) | K (AP) | 3 | Dart | splash |
| gun_203_siege | M110 203 mm | HE | 4 | HeShell | splash |
| rockets_300mm | 9M55 Smerch 300 mm | HE | 3 | RocketBig | splash |
| ballistic_missile | 9M723 Iskander (700 kg) | HE | 4 | Ballistic | splash |
| mortar_240 | 2B8 240 mm | HE | 4 | MortarBomb | splash |
| fpv_swarm | FPV drone (1.5 kg) | SC (AP) | 3 | Fpv | top, guided, splash |
| air_to_air | AIM-120 AMRAAM | Frag (Flak) | 3 | Sam | guided, splash |
| wvr_aam | AIM-9X Sidewinder | Frag (Flak) | 2 | Sam | guided, splash |
| stinger_atas | FIM-92 Stinger (ATAS) | Frag (Flak) | 2 | Sam | guided, splash |
| igla_v | 9K38 Igla-V | Frag (Flak) | 2 | Sam | guided, splash |
| r60 | R-60 | Frag (Flak) | 2 | Sam | guided, splash |
| aim9 | AIM-9 Sidewinder | Frag (Flak) | 2 | Sam | guided, splash |
| jassm | AGM-158 JASSM (450 kg) | HE | 3 | Cruise | guided, splash |
| air_cruise_missile | Kh-101 (400 kg) | HE | 3 | Cruise | guided, splash |
| griffin | AGM-176 Griffin | SC (AP) | 3 | Atgm | guided |
| kh29 | Kh-29 | SC (AP) | 4 | Atgm | guided |
| s8_pods | S-8 80 mm | HE | 2 | RocketSmall | splash |
| gsh30k | GSh-30K 30 mm | K (AP) | 2 | BeltedAutocannon |  |
| gsh_23v | GSh-23V 23 mm | K | 2 | BeltedAutocannon |  |
| door_gun | PKT 7.62 mm | K | 0 | BulletSmall |  |
| detonator | car bomb (900 kg) | HE | 4 | CarBomb | splash |
| zu23 | ZU-23-2 23 mm | Frag (Flak) | 1 | Airburst |  |
| lancet | ZALA Lancet-3 (3 kg) | SC (AP) | 4 | Lancet | top, guided |
| shahed | Shahed-136 (50 kg) | HE | 3 | Shahed | top, guided, splash |
| hel_beam | Iron Beam laser (100 kW) | En (Flak) | 2 | Energy |  |
| railgun | railgun (32 MJ) | K (AP) | 4 | Rail |  |
| twin_30_bmpt | 2A42 30 mm (twin) | K | 2 | BeltedAutocannon |  |
| ataka | 9M120 Ataka | SC (AP) | 4 | Atgm | guided |
| vikhr | 9K121 Vikhr | SC (AP) | 4 | Atgm | guided |
| fighter_cannon | GAU-22/A 25 mm | Frag (Flak) | 2 | BeltedAutocannon |  |
| gau_gatling | GAU-8 Avenger 30 mm | K (AP) | 3 | BeltedAutocannon |  |
| maverick | AGM-65 Maverick | SC (AP) | 4 | Atgm | guided |
| recon_missile | MAM-L | SC (AP) | 3 | Atgm | guided |
| hind_rockets | S-8 80 mm | HE | 2 | RocketSmall | splash |
| gun_155_twin | M284 155 mm (twin) | HE | 3 | HeShell | splash |
| flak_quad | ZSU-23-4 23 mm (quad) | Frag (Flak) | 1 | Airburst | splash |
| sam_battery | MIM-104 Patriot PAC-2 | Frag (Flak) | 3 | Sam | guided, splash |
| bastion_gun | 2A83 152 mm (twin) | K (AP) | 4 | DoubleDart | splash |
| gun_152_heat | 2A83 152 mm HEAT | SC (AP) | 4 | DoubleDart | splash |
| gun_105_apfsds | 2A75 125 mm APFSDS | K (AP) | 4 | DoubleDart |  |
| hellfire_volley | AGM-114L Hellfire Longbow | SC (AP) | 4 | Atgm | guided |
| twin_35_ahead | Skyranger 35 mm AHEAD | Frag (Flak) | 2 | Airburst | splash |
| grad_cluster | BM-21 Grad 122 mm (cluster) | HE | 2 | Cluster | splash, cluster |
| gun_125_elite | 2A46M-5 125 mm | K (AP) | 4 | DoubleDart | splash |
| mlrs_elite | M30 GMLRS 227 mm (cluster) | HE | 3 | Cluster | splash, cluster |
| autocannon_40 | Bofors 40 mm | K | 2 | BeltedAutocannon | splash |
| gun_105_wheeled | Centauro II 120 mm | K (AP) | 4 | DoubleDart |  |
| sam_48n6 | S-400 48N6 | Frag (Flak) | 3 | Sam | guided, splash |
| kornet_twin | 9M133 Kornet | SC (AP) | 4 | Atgm | guided |
| dozer_blade | dozer blade | K (AP) | 3 | Blade |  |
| none |  | K | 0 | None |  |
| mg_coax_ground | PKT / M240 7.62 mm | K | 0 | BulletSmall |  |
| c_ram_gatling | Phalanx M61 20 mm | Frag (Flak) | 1 | Airburst | splash |
| gun_pit_105 | Rh-120 L/44 120 mm (dug in) | K (AP) | 4 | DoubleDart |  |
| fpv_hangar | FPV drone (1.5 kg) | SC (AP) | 3 | Fpv | top, guided, splash |
| bunker_hmg_twin | NSV 12.7 mm (twin) | K | 1 | BulletBig |  |
| bunker_flame | flamethrower (bunker) | Fire | 1 | Flame | splash |
| turret_gun_120_long | Rh-120 L/55 120 mm | K (AP) | 4 | DoubleDart | splash |
| turret_gun_120_auto | Rh-120 L/44 120 mm (autoloader) | K (AP) | 4 | DoubleDart | splash |
| kornet_top | 9M133 Kornet | SC (AP) | 4 | Atgm | top, guided |
| kornet_multi | 9M133 Kornet | SC (AP) | 4 | Atgm | guided |
| turret_rockets_cluster | BM-21 Grad 122 mm (cluster) | HE | 2 | Cluster | splash, cluster |
| turret_thermobaric | 122 mm thermobaric | HE | 2 | RocketSmall | thermobaric, splash |
| c_ram_gatling_long | Phalanx M61 20 mm | Frag (Flak) | 1 | Airburst | splash |
| howitzer_cb | M284 155 mm | HE | 3 | HeShell | splash |
| howitzer_ext | M284 155 mm (base bleed) | HE | 3 | HeShell | splash |
| sam_pac3 | Patriot PAC-3 MSE | Frag (Flak) | 3 | Sam | guided, splash |
| sam_battery_lrr | MIM-104 Patriot PAC-2 | Frag (Flak) | 3 | Sam | guided, splash |
| lancet_hangar | ZALA Lancet-3 (3 kg) | SC (AP) | 4 | Lancet | top, guided |
| fpv_hangar_swarm | FPV drone (1.5 kg) | SC (AP) | 3 | Fpv | top, guided, splash |
| gun_155_twin_long | M284 155 mm (twin, long) | HE | 3 | HeShell | splash |
| turret_rockets | BM-21 Grad 122 mm | HE | 2 | RocketSmall | splash |
| bunker_hmg | NSV 12.7 mm | K | 1 | BulletBig |  |
| saucer_laser | laser (150 kW) | En (Fire) | 3 | Energy | splash |
| coilgun | coilgun (10 MJ) | K (AP) | 4 | Rail |  |
| mothership_cannon | AU-220 57 mm | HE | 2 | BeltedAutocannon | splash |
| mothership_drones | ZALA Lancet-3 (3 kg) | SC (AP) | 4 | Lancet | top, guided, splash |
| gun_behemoth | 2A65 152 mm (twin) | HE | 3 | HeShell | splash |
| boss_howitzer | 2A44 203 mm | HE | 4 | HeShell | splash |
| boss_rockets | BM-21 Grad 122 mm | HE | 2 | RocketSmall | splash |
| boss_missiles | 9M133 Kornet | SC (AP) | 4 | Atgm | guided |
| boss_flak | Oerlikon 35 mm (twin) | Frag (Flak) | 2 | Airburst | splash |
| train_gun | B-38 152 mm | K (AP) | 4 | DoubleDart | splash |
| agl_40 | Mk 19 40 mm | HE | 2 | Grenade | splash |
| guided_bomb | GBU-39 SDB (110 kg) | HE | 3 | GuidedBomb | splash |
| atgm_post | 9M113 Konkurs | SC (AP) | 3 | Atgm | guided |
| drone_gun | M3P 12.7 mm | K | 1 | BulletBig |  |
| boss_flamer | flamethrower (heavy) | Fire | 2 | Flame | splash |
| boss_thermo | TOS-1A 220 mm thermobaric | HE | 3 | RocketBig | thermobaric, splash |
| boss_railgun | railgun (64 MJ) | K (AP) | 4 | Rail |  |
| boss_mortar | 2B8 240 mm | HE | 4 | MortarBomb | splash |
| supergun_800 | super-gun 800 mm | HE | 4 | SuperShell | splash |
| borer_drill | drill head | K (AP) | 4 | Drill |  |
| borer_cannon | 2A70 100/76 mm | K (AP) | 3 | Dart | splash |
| airship_flak | S-60 57 mm | Frag (Flak) | 2 | Airburst | splash |
| airship_drones | FPV drone (1.5 kg) | SC (AP) | 3 | Fpv | top, guided, splash |
| boss_heli_gun | M230 30 mm | K | 2 | BeltedAutocannon |  |
| boss_minigun | GShG 7.62 mm | K | 0 | BulletSmall |  |
| boss_hmg | NSV 12.7 mm | K | 1 | BulletBig |  |
| hover_ciws | AK-630 30 mm | K | 2 | BeltedAutocannon |  |


## 15A. Prompt 16: Lighthouse Bay, Leviathan and its fleet (2026-09-29)

Part 1 of prompt 16 (A, B, C, D, G); E (the old bosses' new weapons) and F (one escort system for every boss) are the
escort agent's (feature/p16-escorts). Leviathan's fleet is self-contained here, in the naval system; once both branches
are in, it can move onto F's `escorts` data (corvettes as `cover` with their own `aps` and `slot: "screen"`, attack boats
as `raid`, the jets as `drop: "edge"`). The fast attack boat's model id is `missile_boat` (for the hovercraft's escort
in E). The owner's rule on test time: one small new suite, no sweeps (Z).

### A. Lighthouse Bay (`lighthousebay`, Vịnh Hải Đăng)

**A.1 Layout** (`build_maps.py` `lighthousebay`, world layout). The sea fills the south-east beyond a coast that runs
diagonally between the two camps, so both sides meet it alike: the map is symmetric by the reflection through the
north-west to south-east diagonal ((x, z) -> (-z, -x), which swaps the camps), not by the usual half-turn. Everything is
laid out in the coast's frame (u along the coast, w out to sea). The sea is 36 % of the square (the brief's 35-40 %).
The outline keeps the square's edge on the sea's side (`lb_open_sea`): ships sail in and out there.

**A.2-A.3 Ground.** Two coves with sand beaches (surf tiles, fishing boats, net racks, a hamlet behind each, wrecks of
an old landing) and a wooden pier each; between them the rocky headland with the lighthouse (the east objective); high
cliffs by the camps with an abandoned coastal battery on each; a fishing village round the market (the town objective);
the old fort on the pine hill (the west objective); pine woods, bunkers and trenches on the cliff tops.

**A.2 Sea lanes** (map data `sea`, `SeaDef`): near, mid and far at w 92, 106 and 120 (70, 84 and 98 m off the cove
beaches). Ships never touch the ground's grid: the naval system steers them in the coast's frame. The brief's "reuse the
train's and hovercraft's fixed routes" is met by the same idea (a scripted line, never pathfinding), in the sea's own
frame rather than as waypoints, because the ships need lanes, stations and a run for the edge, not one route.

**A.4 Reach** (`Prompt16NavalTests.TheSeaLanesAreInReachAsDesigned`): a battle tank on a pier head (w 52) reaches a ship
on the near lane (40 m less its 12 m hull); off the pier heads and the headland's tip no short-range direct fire
(tanks, IFVs, armoured cars: 28-34 m) does; artillery on the shore, aircraft and the coastal batteries (135 m) reach the
far lane. Decided: the headland's tip beside the lighthouse counts as a third pier head, and medium-range tank hunters
(38-42 m) also reach the near lane from the headland's rocky flanks: the lighthouse point is the fight's centre.

**A.3 The coastal batteries** (`NavalSystem.Batteries`): abandoned until a side's ground vehicles hold one alone for 10 s;
then a `coastal_battery` (the heavy fortress's model and twin 155 mm, reach 135 m, `navalOnly`: it fires on ships only)
stands there for that side; destroyed, the battery stands abandoned again after 60 s. **The lighthouse**: whoever holds
it (the mode's point, else ground vehicles holding it alone) sees every ship within 170 m of its lamp. Ships show from
further off than other vehicles (their hull's size is added to the spotter's reach).

**A.5 Versions.** Conquest, Survival and Siege, with sized hardpoints and slot labels by hardpoints.py as every map. The
Siege version keeps the big fortress (the classic walled square was tried first and walled the attacker out of its own
coast); the sea comes back round the fortress's ground (`lb_refill_sea`) and walls, gates and hardpoints it put on the
water are dropped. `check_access.py` passes both versions. Campaign: 4-11 (D). Skirmish: in `MatchSettings.AllMaps`.

### B. Leviathan (`leviathan`)

**B.1** A battleship hull with a missile cruiser's cells, 64 x 11 m (the biggest model; its LOD is ModelLibrary's
automatic one): two twin 203 mm turrets, launch cells, a stepped superstructure with phased-array panels, a lattice mast
with a spinning radar, a raked funnel, two CIWS, a hangar and helicopter deck, a well-deck gate (`mb_naval.py`, 5.4 k
triangles). HP 11 000 (a starting point for the testing phase's kill-time measure).

**B.2 Parts** (9; each 7-9 % of the body, prompt 9's band): the turrets (`maingun`, each one lays half the salvo), the
launch cells (`vls`, stops the cruise missiles), two CIWS (`ciws`: a gun each, on part 2's `aps` mechanism: fewer interceptors with one broken, none with both),
the radar (`radar`: salvos and cruise missiles fall 2.2 times as wide, the CIWS guns spread twice as wide and the APS
misses 35 % of its interceptions), the flight deck (`flightdeck`: its helicopter launches), the well deck (`welldeck`:
the landing craft), the engine room and funnel as one part (`engine`: 65 % speed, so its run is slower). New mechanisms
`cruise`, `craft`, `radar` in `BossPartDef.Mechanisms` (the CIWS use part 2's `aps`).

**B.3 Armour** `[4, 4, 3, 2]`: sides 4, deck 2. Bombs, shells, artillery rockets and top attacks strike the deck by
prompt 15's rules; direct fire strikes the side. Decided: a pen-3 round on the side keeps prompt 15's 0.4 (weak, not
nothing); pen 2 and less are 0.15 and 0.05 ("almost nothing"). Parts have their own levels (turrets and the engine room
3, cells, CIWS and decks 2, the radar 1).

**CIWS** (the ship's APS, radius 26, 3 interceptors, 2.2 s): missiles, rockets and drones, never shells, bullets or beams
(prompt 15's APS rule). Phase 2: 5 interceptors, 1.3 s. Its salvo turrets are `"laid": true` weapons: the combat system
never fires them; the naval system lays and fires them.

**B.4 Phases** (marks 0.7 and 0.4, prompt 8's transformation): phase 1 on the far lane, salvos sweeping along the shore
18 m a salvo the way it sails (a group of enemies within 24 m of the sweep draws it), marked 2.8 s ahead, every 12 s, two
203 mm shells a turret (420 damage, the calibre scale). Phase 2 on the near lane: the well deck opens (3 landing craft,
two tanks each, every 40 s), the flight deck launches an attack helicopter every 55 s, two attack jets fly in off the sea,
cruise missiles at the biggest group every 50 s (marked 5 s ahead), the CIWS at its strongest; the salvos go for the
biggest group in reach. Phase 3: four cruise missiles at the player's HQ and towers at once, smoke, and a run along the
far lane to its farther end. **The clock**: set as the run begins from the route and the turn about (about 60-100 s),
shown on the boss bar ("Escaping 1:24"); it gets away at the edge once the clock is out, later if it was slowed (engine
room). Escaped: invulnerable, silent, hidden; the mission is lost (Boss Rush: it pays nothing and the rush goes on).

**B.5 Sinking** (`ShipSinking`, view only): it lists for 5 s, then the big ship breaks its back (a second copy of the
model is the stern half; the halves rear up and sink below the water, which hides what is under); smaller ships roll
over. Prompt 9's fires on the broken parts and five magazine blasts along the hull (the sim's, 0.8-3.6 s) play meanwhile.

**B.6 Radio**: Kessler on arrival, at each phase, when it runs, when it gets away and when it sinks; the part lines for
the cells, the last CIWS, the radar, the flight deck, the well deck and the engine room; the batteries and the lighthouse.

**B.7** Guide entries and part tips (GuideText, Strings), boss files for the dossier with the fleet under it, the boss bar
with the part icons (their armour chips are prompt 15's). Not done: the card render and the In-action clip (Z).

### C. The fleet

`sea_corvette` (2): HP 1600, armour [3, 3, 3, 1], a 76 mm (OTO Melara, 95 m) on the shore, a CIWS whose APS (32 m) covers
Leviathan while it keeps station 26 m off it on the same lane; in phase 3 it steams between Leviathan and the shore.
`missile_boat` (3): HP 420, armour [1, 1, 1, 0], 12 m/s: waits on the mid lane, dashes to the pier head nearest it, holds
8 s firing 80 mm rockets (55 m), runs back out: anything on the pier heads hits it there. `landing_craft`: runs two
tanks up a cove beach, lands them, goes back and is hoisted in. The phase 2 aircraft: the existing attack helicopter
(flight deck) and attack jet (two, off the sea). The fleet's ships are not bosses, cost nothing and are no cards; they
show in the dossier under Leviathan.

### D. Campaign and modes

**D.1 Chapter 4.** Decided: an **epilogue** boss mission after the operation, 4-11 "Leviathan" at Lighthouse Bay
(Overcast, Kessler, 25 min). The story is the brief's (the port lost, Kessler puts to sea), and the chapter already has
two boss fights (4-5, 4-6) before its operation, so a second boss mission in the middle would crowd it, and the
operation's final stage cannot change battlefield. The chapter's shape holds: an epilogue (`"epilogue": true`) is left
out of "ten main missions, the tenth the operation" (build_campaign.py, CampaignTests, `Campaign.OperationOf` now takes
the operation, not the last main mission); it pays like the chapter's boss and moves nobody else's pay (the economy tune
is unchanged: 100 / 3.00). It opens after 4-10 and chapter 5 waits for it. CampaignText.cs keeps its hand edits: only
the 16 new keys were added.

**D.2 Boss Rush**: Leviathan is its own kind (eleven bosses, 57 minutes). On a battlefield without a sea the rush goes to
Lighthouse Bay for it (the curtain: "Setting out to sea"), carrying the bosses beaten, the clock, the CP and the army
(each vehicle's health share, landed at the drop zone), and back to its own battlefield for the next boss. Half the
fleet sails there. The switch is a scene rebuild (`BossRushSession.Pending`); Boss Rush has no checkpoint replay, so
determinism is per battlefield.

**D.3 Operations**: 4-11 is replayable; two mutators in the rotation: **Sea storm** (the storm, and ships seen from 55 %
as far) and **Fleet** (a flagship brings one more escort and two more attack boats; off the sea, and on it, the enemy
earns 10 % more, so it means something on every battlefield the rotation draws).

**D.4 Rewards**: 4-11 opens the heavy fortress's coastal branch, now **Long-range coastal battery** (72 m instead of
60 m): a campaign-opened branch (`PlayerProfile.BranchOpen`) waits for its mission. A branch opened is not counted as a
card in the chapter's 5-7. The boss file and the mission's fragment go in the dossier.

**D.5** Lighthouse Bay is in the skirmish map list.

### G. Performance

Low graphics (shadows Low or Off) draws the water unlit and the wakes short (6 foam patches, no bow waves; 22 and bow
waves otherwise; `WakeView`). The naval system's step with the whole fleet: 0.03 ms (EditMode, the fleet test). The FPS
measure on a low-end phone in phase 2 is for the testing phase.

### T. Tests

`Prompt16NavalTests` (5, all pass): the lanes' reach (A.4); Leviathan and its fleet on the water, its armour by face and
its parts; the CIWS takes missiles and never shells, and stops with both CIWS; phase 2 on the near lane, phase 3's clock
runs down and it gets away; Boss Rush goes to sea and back with the army and the clock. `BossPartsTests.Expected` has
Leviathan (9). Nothing else was run (the owner's rule).

### Z. Left for the testing phase

- The stuck detector on Lighthouse Bay (every version, 5 seeds, both sides); 5-seed runs of 4-11, Boss Rush with the
  switch, and Operations with Sea storm and Fleet; Leviathan's kill time against prompt 9 and 13's band (HP 11 000 is a
  first figure).
- The suites this touches, not run: CampaignTests (the shape, 4-11 plays to an end), BossPartsTests, CalibreTests,
  OperationsModeTests (the rotation with 20 mutators), TowerRosterTests, ContentTests; PlaySmoke (the owner said none).
- The Base screen's map picture for Lighthouse Bay (`BaseMapShots`, graphics batch), Leviathan's and the fleet's card
  renders and In-action clip, screenshots of the map and of Leviathan in each phase for Docs/ui-screens.
- FPS on a low-end phone in phase 2 with the whole fleet, the helicopters, the landing craft and parts burning.
- Moving the fleet onto prompt 16 F's escort data once both branches are in.
## 14B. Prompt 15: armour and weapon icons, where they show (2026-09-29)

The UI half of prompt 15 (D and E). The data (armour levels by face, penetration, the six damage types, weapon forms
and tags, `Matchup`) is the sim agent's (14A); the UI reads it and changes none of it.

### D. The icon set

- **Drawn new, from scratch.** 57 icons in `Scripts/Game/Hud/Icons.Combat.cs`, generated by `Tools/art/combat_icons.py`
  (the shapes are code: rounds and missiles are drawn along an axis and turned 45 degrees so they fly up and right,
  shells and the ballistic missile stand, bombs fall nose down to the right, drones are seen from above). No existing
  icon was reused or recoloured. The generator also writes a quick preview (`--preview out.png`, 33 and 96 px) for
  drawing without Unity.
- **The renderer grew fills.** The kit's icons were strokes only; the battery-style shields need solid parts, so the SVG
  subset now takes `fill="1"` (non-zero), `fill="eo"` (even-odd: rivets and brick joints are holes), `stroke="0"`,
  `sw` (a shape's own stroke width) and `dash` (flattened and cut into dashes at parse time). Old icons are unchanged.
- **Armour, 15 icons**, "filling up like a battery": 0 a dashed hollow shield, 1 a hairline, 2 a double outline, 3 the lower
  half filled, 4 filled with five rivets (holes). Aircraft: a narrower shield with three wing strokes each side (a winged
  badge) in the same five states; a single wing silhouette was tried on paper, but it collides with the Shahed's delta
  and cannot hold a double outline at 18 pt. Structures: the shield with brick courses; the filled levels keep the joints
  as holes, so the bricks read at every level.
- **30 weapon forms**, one per `WeaponForm` of the sim (the enum was read before it was committed, so the names match):
  kinetic rounds show penetration by shape (a small ball with speed lines, a bullet, a round with its case and band, a
  dart, a dart with two heads, a dart with two electric rings); HE shell (upright, fuze and driving band), finned mortar
  round, airburst (a round with a spray of dots), grenade; small and heavy rockets; ATGM (short fat body, cone), SAM (slim,
  mid wings), cruise (straight wings across), ballistic (big, sharp, standing); bomb, guided bomb (with its curve), cluster
  (the case opening into dots), heavy bomb (fat, lattice fins), napalm (a finless canister and a flame); FPV (four rotors),
  Shahed (delta with wingtip fins), Lancet (two X wings); flamethrower, energy beam (emitter, beam, glowing head); dozer
  blade, drill, super-gun shell (leaving its shock rings), car-bomb charge (three sticks and a lit fuse).
- **Marks.** Damage types in a chip's corner, bold and mostly filled for 17 px: shaped charge a cone with its jet rays, HE
  an eight-point burst, fire a filled flame, fragmentation a cluster of seven dots, energy a ray with a four-point spark;
  thermobaric its own (a smaller burst in a ring); kinetic has none. Extra marks (detail page and tooltips only): top
  attack is an arrow down onto a turret (a bare arrow onto a line read as "download"), guided an S-curve with an
  arrowhead, splash a ring with a dot. The enemy tooltip's verdicts are drawn too (the fonts have no ✓ or ✕): a check,
  a tilde, a cross.
- **No two alike.** `CombatIconTests` compares the path data of every icon of the game (kit, vehicles, towers, this set).
- **Sizes.** `--fc-cicon` 34 px = 18.7 pt (the 18-20 pt of the brief) in cards, trays and the HUD; 52 px (28.5 pt) on the
  detail page; marks 17 / 24 px. The sheet `kit-combat-icons-small.png` is the whole set at 34 px on the smallest screen
  (1280 x 720, a panel pixel an image pixel): every shape reads apart there.
- **Chips.** A chip is the form icon with the mark overlapping its bottom-right corner on a square of the surface's
  colour (`--fc-chip-bg`: the card's, the field panel's in the HUD), so the mark cuts the lines under it.
- **Tooltips.** Every icon carries its words ("Giáp dày · mặt trước", "Tên lửa chống tăng · Nổ lõm · Xuyên rất cao · Đánh
  nóc · Dẫn đường"). A tap shows them where the icons are full touch targets or sit in one: the detail page's diagram,
  each weapon row, the strong / weak lines and the table, the HUD's selection strip, the legend. In card rows the card
  itself is the target (it opens the detail page, where every icon is tappable), so the row's icons are not separate
  targets: 34 px icons in a row could not be 44 pt targets without overlapping.
- **"Hiện số chi tiết"** (Settings > Display, `MatchSettings.ShowCombatNumbers`, `mb.showNumbers`, off by default): the
  tooltips add the levels in brackets and the multipliers ("×0,75"), the table's cells print theirs, the enemy tooltip
  its multipliers. Off, no number shows anywhere in the icons or their words.

### E. Where they show

- **Cards** (E1): a row between the name and the level, 34 px high: the front armour and the first two weapons, main
  first, "+N" for the rest, on the Army deck, the collection and the towers; the deck row's compact cards (112 px wide)
  take one chip and "+N" (two do not fit in 108 px). A card without a unit (a fire-support card) gets an empty row of the
  same height, so `CardsInARowLineUp` stays green. The Base and Outpost trays' rows show armour and two chips under the
  short name. The home deck strip does not (it is a strip, not the deck).
- **Detail page** (E2): the armour tag under the name is the front's shield and words; the left column's old class
  counters are replaced by the armour diagram (the unit from above, each face's border as thick as its level: dashed,
  2, 4, 7, 10 px; the turret ring as the roof; a four-line legend beside it; aircraft and uniform structures get one
  icon and "Như nhau mọi hướng") and "Mạnh với / Yếu trước" from `Matchup.Summary` (the columns its weapons pierce well
  as shields; the threats as chips, top attack as its mark). The Weapons tab has each weapon's large chip with its extra
  marks beside its name, and the effectiveness table after the list: the five shields, the winged shield (air, level 0)
  and the brick shield (structures, level 2) head the columns, each cell a bar as long as `Matchup.EffectRow`'s real
  multiplier (scaled to the table's largest, at least ×1). Screens `detail-armour` and `detail-weapons` scroll to them for
  the checks and shots.
- **Tray** (E3): nothing on the tray; a held card's tip shows the full name and the armour with every chip (up to four).
- **Selection strip** (E4): armour and two chips beside the health bar, one tap target that says them in words. The
  compact HUD's cover: Conquest 28.5 %, Siege 28.6 % at 16:9 (27.5 % both before), still under 30 %.
- **Enemy tap** (E5): `SelectionController.EnemyTapped` (a new event; the tap still orders focus fire when units are
  selected) makes `BattleHud.ShowEnemyTip`: the enemy's front armour and short name, then each deck vehicle with ✓ ~ ✕
  from `Matchup.Verdict` (its main weapon against the enemy's front, or roof for rounds from above; ✓ from ×0.6, ~ from
  ×0.12, the sim's thresholds). One column, 300 px, at the left edge; 5 s, or a tap closes it. Battle screen `hud-enemy`.
- **Boss parts** (E6): a small armour icon (18 px) in each part's corner, from `Matchup.PartArmour`, in the opened bar and
  the full HUD; the closed compact bar's 20 px cells stay state only (a second icon there would be unreadable).
- **Cover** (E7): five shields on the deck's overview (beside its summary, where there was room) and on the Base screen's
  cover strip for the towers: lit where a weapon pierces that level well (`Matchup.Effect` ≥ ×0.6), else dimmed, in the
  warning colour and struck through (the state reads without colour).
- **Legend** (E8): there is no menu-level Guide tab, so the legend is a page of its own, opened from every detail page's
  Guide tab ("Biểu tượng giáp và vũ khí") and from Settings: the three armour families, the diagram, every form grouped
  (kinetic from least to most piercing), the marks, the extra marks, the verdicts and the counter table (reactive armour
  and cages cut shaped charges, APS stops them and partly artillery rockets, flares partly fragmentation missiles, smoke cuts
  a beam by 80 %, a jammer sends guided rounds wide: the sim's table, 14A C.9; a note on thermobaric and cages). Screen
  `legend`, shot tall as `screen-legend-vi-full.png`.
- **Words.** Every new text has both languages; "icon" and "tooltip" are "biểu tượng" and "ô chú thích" in Vietnamese
  (`UiLanguageTests`).

### Checks and pictures

- Tests (targeted, the owner's rule): `CombatIconTests` (every `WeaponForm`, armour level of the three kinds and
  `DamageType` has an icon or mark entry, every weapon of the roster maps to one, no two icons share path data; the enemy
  tooltip's marks equal `Matchup.Against` through the sim's thresholds on eight enemies, all three marks seen), and the
  existing `UiLayoutTests` (all screens with `legend`, `detail-weapons`, `detail-armour`, `hud-enemy`; the cover check),
  `CardsInARowLineUp`, `LocalisationScanTests`, `UiThemeTests`, `UiLanguageTests`, `TowerIconTests`, with `CardRenderTests` and
  the sim's `ArmourTests` after the merge: 108 green. Play mode: PlayShots' six real matches (the menu, Conquest three times,
  Siege, Defend, Boss Rush) ran the new HUD code and logged no error; no separate PlaySmoke (the owner's token rule).
- Two layout faults the checks found: "+N" laid out a line shorter than it measures at its 17 px box (now a no-wrap
  label without vertical padding), and the enemy tooltip's cells had no width to resolve against (now a fixed width).
- Screenshots in `Docs/ui-screens/`: `kit-combat-icons.png` (16:9) and `kit-combat-icons-small.png` (the smallest screen),
  `screen-army-deck-vi-16x9`, `screen-detail-armour-vi-16x9`, `screen-detail-weapons-vi-16x9`, `screen-legend-vi-full`,
  `battle-hud-enemy-vi-16x9` (`IconSheet.Combat`; `UiShots -mbShotsOnly` now takes a comma list).

### Helper tasks for the design document (the lead)

- **Card pictures for every fixed defence.** The five utility modules already had renders, named after their models
  (`helipad.png`, `vehicle_hangar.png`...); the design document's picture library looked them up by id. It now reads the
  manifest (id to model). The fixed defences without a base slot (super-gun, spawn bastion, fallback post, targeting
  station) were not cards at all, so `CardArt.For` gave them nothing: a "structure" kind in `CardRenders.Kinds` lists
  them (three share their models' renders; the targeting station was rendered). 139 cards.
- **In-battle pictures** (`MachineBrigade.Editor.PlayShots.Run`, batch with graphics, no -quit): real matches on fixed
  maps and decks with the match's fixed seed, shot at a fixed sim tick, the camera put on a view worked out from the sim
  (the closest ground fight, a base's HQ, the boss, the aircraft's centre, the barrage's target), Camera.main rendered into
  a 1600 x 900 texture. The game's own HUD panel does not draw into a texture in batch mode, so for that frame the live
  HUD's elements are lent to an off-screen runtime panel of the same size and theme (the UI test framework's, as
  UiShots) and blended over (premultiplied). `battle3d-conquest`, `-siege`, `-defend` (and `-defend-base-hq`,
  `-base-1`, `-base-2` close over the towers), `-boss`, `-air`, `-barrage`.

### Left

- The Base screen's shields and the Outpost tray were checked by the layout tests, not looked at in a picture.
- On a phone (testing phase): the icons' legibility at 18.7 pt on a real 720p screen, and a tap on a moving enemy.

## 15B. Prompt 16: old bosses' new weapons, escorts for every boss (2026-09-29)

Prompt 16 parts E and F (branch feature/p16-escorts, from lead/integration 279c11e). Parts A-D (Lighthouse Bay,
Leviathan and its fleet) are another branch; the escort system below is the one Leviathan's fleet can use.

### E. The thin bosses' new weapons

Every new weapon follows the calibre scale (13C) and the damage types and penetration levels (14A), and is a part
(prompt 9) where the boss has a place for it, so breaking it takes it away. Parts stay 7-15 % of the body each and at
most 70 % in all (prompt 9's rule; `BossPartsTests` holds it).

| boss | new weapon | how it works | its part (share) | what breaking it does |
|---|---|---|---|---|
| Iron Train | mortar car (`train_mortar`, 2B11 120 mm twin, HE, pen 2) | a flatcar coupled behind the gun wagon; indirect, so it hits what hides behind cover (no line of fire needed) | `mortar_car` 10 % | the mortar falls silent |
| Tempest | interceptor laser (APS, `laser: true`, `rockets: true`: 26 m, 2 shots, 1.6 s) | Energy: burns missiles, drones and rockets out of the air round it (and round anything of its side within 26 m); smoke blinds it (14A C.6) | `interceptor` 8 % (the modelled launchers on the turret sides) | no more interceptions |
| Behemoth | hard-kill APS (11 m, 2 shots, 4 s) | direct-fire missiles and rockets only (a Trophy's): the anti-tank missile answer | `aps` 7 % (a place on the turret roof) | no more interceptions |
| Inferno | fire trail (`fireTrail`: a patch every 4 m, 3.5 m across, 18 dps Burn) | lit for 10 s, burns 8 s: the ground fires' time a fifth shorter (12A), the same in the sim and the view | `fuel` 8 % (its fuel tanks) | no more trail |
| Hive | jamming aura (`jammer: 30`) | the player's guided rounds fired from or aimed within 30 m of it are scrambled (they miss by 5-11 m: against its 7.5 m hull about half still hit) | `jammer` 8 % (a mast on the roof) | guided rounds fly true again |
| Bastion | twin Kornet mount (`kornet_twin`) | a roof launcher, all round | `kornet` 8 % | silent |
| Doomsday Train | rocket car (`boss_rockets`, Grad) and long-range SAM car (`sam_battery`, Patriot, 90 m) | two flatcars behind the missile wagon | `rocket_car` 10 %, `sam_car` 10 % | each falls silent |
| Rail Supergun | two AA mounts (`ciws_aa`, AK-630, aircraft only) on the bed's rear corners | shoot aircraft | `aa_l`, `aa_r` 7 % each; tractors 10 → 8 %, fire control 12 → 9 %, main gun 15 → 14 % | each falls silent |
| Landing hovercraft | two more CIWS (`ciws_aa`, aircraft only) that also intercept (APS 22 m, 2 shots, 3 s: missiles, drones, rockets; not shells, bullets or energy) and two 140 mm rocket launchers (`hover_rockets`, A-22 Ogon: 11 x 65, 55 m, every 22 s) | the Zubr's armament | `ciws_l`, `ciws_r`, `rockets_l`, `rockets_r` 7 % each; ramp 14 → 12 %, fans and guns 10 → 7 % | a CIWS broken halves its interceptors (rounded up), both: none; the rockets fall silent |

Kept as they were (the brief): Iron Bird, Spectre, Ice Fortress, Hive Mothership, Silver Bug, Earth Worm, command
airship; the Supreme Commander keeps no weapon worth the name.

New part mechanisms (`stops`): `aps`, `jammer`, `trail`. Unlike the older ones (one part each), these may be carried by
several parts and stop only with the last; a protection system holds its interceptors in proportion to the parts still
standing (`Vehicle.ApsMax`). The view: the Tempest's interceptions are drawn as the Iron Beam's beam from its turret side;
the trail's patches as ground fires (`SimEventKind.FireTrail`); new part kinds `aps`, `ciws`, `fuel`, `ew` have names and
icons. Models (Blender, `Tools/blender/mb_p16_arms.py`, wrapping the current builders): the Iron Train's mortar flatcar,
the Doomsday Train's rocket and SAM cars, the supergun's two CIWS, the hovercraft's two CIWS and two rocket launchers,
the Bastion's Kornet launcher; the other new parts are modelled already (the Tempest's launchers, the Inferno's tanks) or
places on the hull (the Behemoth's APS, the Hive's mast). The trains are longer with their cars (measured: the Iron
Train 25.06 x 3.4 m, the Doomsday Train 31.61 x 3.44 m; their origins stay where they were, so the capsule sits 2.6 and
4.8 m forward of the models' middle: the cars' last metres are outside it, ASSET_DEBT). The supergun's AA mounts stand
at the rear corners clear of the traversing carriage; turned inboard their barrels would pass through the generator
set, so each has a firing arc leaving that 60 degrees out (`arc: [-107, 150]` and `[107, 150]`). Two launchers of one
slot on their own mounts (the hovercraft's rocket boxes) each get launch points from their own face of tubes now
(`ModelLibrary.AddLaunchPoints`, a second pass over a slot's other muzzles on their own mounts); the mortar slot's
muzzle is recognised (`MuzzlePattern`).

**Health retuned** from a kill-time lab (the standard army of 15 against the boss alone, one seed, as prompt 9
measured; `BossEscortTests.EachChangedBossStillFallsInAboutTheSameTime` logs it against lead/integration's data):

| boss | health | kill time, before → now (with escorts) |
|---|---|---|
| Iron Train | 4400 → 4150 | 15.4 → 15.5 s, x1.01 (15.5) |
| Tempest | 4750 → 4150 | 15.3 → 15.6 s, x1.02 (20.9) |
| Behemoth | 4950 (kept) | 19.6 → 19.0 s, x0.97 (20.5) |
| Inferno | 5800 → 6300 | 15.3 → 15.5 s, x1.01 (16.2) |
| Hive | 6350 → 5800 | 23.4 → 24.1 s, x1.03 (24.4) |
| Bastion | 9000 → 9600 | 25.0 → 27.5 s, x1.10 (31.0) |
| Doomsday Train | 5450 → 6000 | 18.7 → 20.3 s, x1.09 (20.4) |
| Rail Supergun | 5500 → 5300 | 18.8 → 18.3 s, x0.98 (19.1) |
| Landing hovercraft | 6500 → 5200 | 15.3 → 15.2 s, x0.99 (14.8) |

All within prompt 9's "now to +15 %" (three a few per cent under). The lab with a small army (six vehicles) showed the
hovercraft's new weapons made it unkillable at first (the extra CIWS shredded tanks, the rockets every 14 s): the two
new CIWS and the supergun's AA mounts fire at aircraft only (`ciws_aa`), the hovercraft's rockets reload in 22 s and
its interceptors are 2 a 3 s; the Inferno's trail and the Tempest's laser needed health going the other way than the
model said (the trail hurts the army less than feared, the laser more). Escorts add 0-20 % to a kill here (more with
fewer shooters); missions and Boss Rush over five seeds are for the testing phase.

### F. Escorts for every boss

**One data-driven system** (`BossSystem.Escorts`, balance.json `escortRules` and `escorts`), replacing the old escort
skills (`behemoth_escort`, `fortress_escort`, `gunship_escort`, `nuke_escort`, `supreme_guard`, removed) and Boss Rush's
own escort list (`BossRushRules.Escorts`, removed).

- **Two kinds of wave:** one with the boss (spawned the step after it joins, as the camera turns to it), and one at
  each phase change: the boss's own phase marks (a change counts as its transformation begins), else the table's
  `marks`, else the rules' `[0.5]` (the rage mark most bosses already have); the Earth Worm's (`"on": "surface"`) each
  time it breaks out of the ground.
- **A helper in every wave** (any role but guard and raid): `repair` (an engineer mends the boss 0.3 % of its health a
  second within 12 m of its hull: the Support aura skips bosses, so this is the escorts' own), `jam` (an EW carrier's
  jammer covers it), `cover` (anti-air: flak, SAMs, fighters, a C-RAM), `spot` (it marks every enemy it sees: the boss's
  side deals 15 % more to them and a boss's guns scatter 0.6 as wide at a marked target), `smoke`. Where the brief's
  wave had no helper one was added (below), so the player always chooses between the boss and its helpers.
- **At most 4-6 alive** (`escortRules.cap`: Easy 4, Normal 5, Hard and Very Hard 6, Heroic and Iron 6), counted per
  boss; a wave's helpers come first, then its guards while there is room. **Strength by difficulty:** each vehicle goes
  through the side's elite budget (prompt 8 H, `ForWave`), so harder difficulties bring more elites; a unit marked
  `elite` is always its elite (a boss's signature).
- **Boss Rush:** two fewer alive (at least 3), half of each wave's guards (rounded up; the helpers all come), the guards
  as elites (Boss Rush's escorts were all elites): fewer and stronger, so a fight does not drag.
- **The leash** (28 m, a table may set its own; a raider 1.6 times it): a guard takes on the enemy nearest the boss
  within the leash plus its own reach, those attacking the boss first (their target or order is the boss, or they hit
  it last); past the leash it drops the chase and drives back to its station. **Stations:** guards beside the boss along
  its heading (so a train's run parallel to its rails), helpers behind it away from the enemy (the nearest enemy it sees
  within 80 m, else the enemy's rally), a screen between it and the enemy. The commander AIs leave escorts alone
  (`Vehicle.IsEscort`); when the boss falls they are released to the commander.
- **CP for kills:** 3 CP a guard, 4 a helper, to the side that destroyed it (on top of the usual refund), with a toast.
- **Arrivals:** beside it (default), `para` (air-dropped round it after a 3 s warning ring, the transport and a
  parachute from the unit's `escort_drop.<unit>` event support; a toast "escorts parachuting in"), `edge` (from the map
  edge behind the boss, driving or flying in: for a fleet's aircraft), `place` (at an offset in its frame). A wave may
  `halt` the boss (the Iron Train stops 6 s at a "station" to drop its light tanks) or only `refill` its own losses (the
  Tempest's jammers).
- **Interface (kept minimal, the UI agent owns the rest):** the boss bar shows a shield icon and the count of escorts
  alive (`BattleHud.SetBossEscorts`); an escort wears an orange diamond left of its health bar, shown whether the bar
  is or not (`VehicleView.RenderEscortMark`).
- **Where it is on:** the world's `EscortSettings` (null: none, the bare test battles and the menu's lobby). Missions and
  Boss Rush set Normal's by default; every session then sets its difficulty's (`ModeSession`), Boss Rush's smaller.
- **Checkpoints:** the escorts' groups, waves and members go into `StateHash`; their orders are ordinary sim commands
  (not journaled), so a replay rebuilds them.

**The tables** (arrival · each phase change), from the brief, a helper added where it had none:

| boss | arrival | phase change |
|---|---|---|
| Iron Train | 2 armoured cars beside the rails (one spots) | halts 6 s: 2 light tanks + an engineer |
| Tempest | 2 EW jammers + a SAM launcher | 2 jammers, only replacing those lost |
| Behemoth | 2 battle tanks + an AA gun | an elite heavy tank + an engineer |
| Inferno | 2 flame tanks + a smoke carrier | 2 flame tanks + an engineer |
| Iron Bird | 2 attack helicopters + a scout helicopter (spots) | a scout helicopter (spots) |
| Spectre | 2 fighters (cover) + a recon UAV (spots: its guns tighter) | 2 fighters |
| Ice Fortress | 2 heavy tanks + an engineer | an engineer |
| Hive | a heavy AA gun + a SAM launcher (the "mixed air defence") | 2 FPV carriers + a recon UAV |
| Bastion | air-dropped: a gun turret, an ATGM tower, a C-RAM (cover) | air-dropped: a gun turret + an AA turret |
| Hive Mothership | 2 strike UAVs + a recon UAV | a scout helicopter (spots) |
| Silver Bug (0.66, 0.33) | the beaten generals' elites: Varga's heavy tank, Orlov's Grad + a recon UAV | Sen's FPV carrier + a jammer; then Quạ Đen's attack helicopter + an engineer |
| Doomsday Train | 2 IFVs beside the rails + a scout helicopter | 2 IFVs + a smoke carrier |
| Rail Supergun | 2 patrol tanks + a counter-battery radar (spots); its fixed turrets are its guards, as before | 2 patrol tanks + an engineer |
| Earth Worm | none | each break-out: 2 IFVs and an engineer air-dropped beside it |
| Command airship | 2 fighters (cover) | an attack helicopter + a scout helicopter |
| Landing hovercraft | 2 hover gunboats (one spots) | a gunboat (spots) |
| Supreme Commander | kept as it was: none | at 60 %: 2 elite battle tanks (its command aura is the help) |

The hovercraft's gunboats (`hover_gunboat`: 30 mm CIWS, 520 health, 8.5 m/s, crosses land and water like the
hovercraft) borrow the hovercraft's model at a third of its size until the fleet's fast attack craft (part C) lands:
then point the table at that def or give `hover_gunboat` its model.

**For Leviathan (part C):** its fleet can be one table: `{ "boss": "leviathan", "leash": 60, "arrive": [ { "unit":
"<corvette>", "role": "cover", "count": 2, "slot": "flank" }, { "unit": "<missile_boat>", "role": "raid", "count": 3 } ],
"phases": [ { "units": [ ... landing craft, helicopters ... ], "radio": "..." }, { "units": [ { "unit": "<corvette>",
"role": "cover", "slot": "screen" } ] } ] }` with `"drop": "edge"` for the strike aircraft coming in from the sea, and
`"cap"` raised for it alone. The corvettes' CIWS cover of Leviathan is their own `aps` (it covers anything of their side
within its radius already); "screen" puts them between Leviathan and the shore.

### Tests (short, the owner's rule)

`BossEscortTests`: the mortar car over a house; the three protection systems until their parts break; the fire trail and
its tanks; the Hive's jammer; the new mounts firing (Kornet, rocket and SAM cars, supergun AA, hovercraft rockets); the
escorts' timing, cap, Boss Rush's smaller waves; the leash; the engineer's repair and the escort bounty; every boss has a
table with a helper in every wave; the kill time per changed boss (one seed, the boss alone). Suites kept green:
BossParts, BossPhase, Counter, Armour, CheckpointReplay, Prompt8Content.

Also fixed on the way: `BossPhaseTests` hit the boss with a default `HitInfo`, whose penetration is 0 since prompt 15
(the constructors' is -1, unknown), so the armour table cut the blow; the tests now pass an explicit scripted blow.
`MuzzleAuditTests`: the Ice Fortress's second rocket box (m1) fires from its own face now (the launch-point pass for a
slot's second mount), so it left the known list. Failing on lead/integration already and left as they are (not this
prompt's): `BossPartsTests.ShootersGoForThePartMostDangerousToThem` (a tank picks the Behemoth's flak before its main gun
since prompt 15's armour levels) and three `ModelTests.RoundsLeaveFromTheLaunchersOnBothSides` cases (heavy_aa,
gunship_heli, fighter_jet).

### Left for the testing phase

- Kill times over five seeds per boss with a standard deck, with and without escorts, and every boss mission and Boss
  Rush on Normal inside its frame (escorts add enemies: the missions' pace may want the caps or the waves trimmed).
- The escorts' formations on real maps (the trains' rails, the hovercraft's coast, the Bastion's towers dropped on
  rough ground), and the stuck detector over boss missions with escorts.
- FPS and tick time on the heaviest boss fight with a full escort and burning parts (Low, a low-end device).
- The escort icon and bar count on a device (and the UI agent's own escort icons, if it makes them, replacing mine).

## 16A. Prompt 17: long maps and layered bases (2026-09-29)

Parts A and B only (C, D and E are later agents').

### A. Map size by mode

- **Which modes.** Conquest, Deathmatch, King of the Hill, Assault, Survival and Boss Rush keep their 300 x 300 m files,
  byte for byte. Siege, Defend, Endless and the weekly fortress play on `<map>_long.json` when the map has one
  (`ModeSession.MapFile` -> `Fortified`: long, else `_siege`, else `_conquest`). Campaign missions keep their variants.
- **The long battlefield** (`Tools/maps/longmap.py`, all 20 maps with a siege version): 300 m across, 480 m along the
  attack (x -150..150, z -150..330; map data `bounds`, `size` 480). South of z = 118 it is the map's own Conquest
  battlefield where it always was (ground, dressing, the attacker's camp and its hardpoints, the three objectives), so
  campaign and camp coordinates hold; the extra 180 m run north, where the base stands, and the flanks are no wider.
  North of the seam a new outline (the map's own strip depth and noise, capped at 12 m, blended over 30 m) replaces the
  square's edge; the square's decor that falls inside comes back as props ("the scenery beyond the edge is played on
  now"), and the strip beyond the new edge gets the theme's trees, rocks and a house here and there.
  Why not grow the corner fortress: its diagonal geometry (outer line x + z = c, L-shaped walls) does not stretch along
  one axis; a base across the full width is what the owner's "outer wall with 2-3 gates" reads as.
- **The sim on a rectangle.** `MapDefinition` has `Min`/`Max` (a square map keeps -half..half), `Width`, `Length`,
  `Centre`, `IsLong`, `Clamp`, `EdgeDistance`; `Contains`, `ClampToMap`, the tactical AI's clamp, the supply drops, the
  crate drops, the aircraft's edge turn and orbit clamp, the airlift's edge and the dodge scoring use them. `NavGrid` and
  `CoverGrid` take an origin and a width and length (the old square constructors stay). Deterministic: no float order
  changed on the square maps (same cells, same centres).
- **Camera, zoom, minimap** (A.4). A long map is seen looking west (`RtsCamera.LongYaw` -90 degrees, the square maps
  -45), so its length runs across the landscape screen, attacker left as before; default zoom 21 (19) and widest 50
  (42); the view starts 22 m ahead of the rally. The camera clamps to the map's rectangle. The minimap keeps the
  rectangle: `Minimap.SetPicture(picture, min, max, yaw)` fits the rotated rectangle and turns with the camera; the
  ground paint (`TerrainPainter.Canvas`), the minimap picture, `BoundaryField`, the ground mesh, the skirt, pebbles and
  grass, the lava and river contours, the troop transports' way in (`AirDrops` Centre/HalfX/HalfZ) and the scenery ring
  (`Surroundings.Beyond`) work on the rectangle. The ground texture keeps the square's density (1024 x 1640 on a long map).
- **Path memory and time** (A.5), measured by `LongMapTests` (desktop, editor Mono): see the numbers below. The grid is
  150 x 240 cells (36,000; the square 22,500, x1.6). Memory a cell: NavGrid 12 B, the path finder 16 B, lanes and unit
  costs about 11 B, cover 4 B a square metre. No coarser cells or hierarchical search were needed; the path queue
  (6 routes a step) is unchanged. If the testing phase's tick budget on the long Siege shows path spikes, the next step
  is a two-level search (sector graph over 16 x 16 cell blocks) in `PathFinder`, not coarser cells (gates and sally
  ports are 3-7 cells wide).
- **Unit caps unchanged** (A.6): 32 vehicles + 6 aircraft a side, Siege/Defend's 48.
- **Operations** (A.3): the mechanism is prompt 5's `Expand` and `PlayArea`; no operation expands yet (every one plays
  the 300 m square). A later stage that needs about 500 m would use a long file as its map (`variant: "long"`) with the
  square as the first play area; left for the campaign agent, no mission data changed here.

### B. Layered bases on the long maps

- **Layout (B.1)**, north of the 300 m square, from the attack: the buffer zone (z 150-190), the forward works (the
  three relays of stage 1 and eight strongpoints: 6 small, 2 medium, behind sandbags), the outer wall along z = 218
  across the whole width with a closed main gate on the road and two open 18 m sally ports (x -103, 101), the yard (the
  shield generators, the super-gun, fuel and ammunition stores, hangars and barracks, the line in: a runway along the
  east yard or a rail line down the west yard), the inner wall (the keep: x -46.6..44.6 from z = 266, a closed south gate,
  open 18 m gateways in both side walls), the command HQ at (0, 305) and the defenders' drop zone in the keep's yard
  (0, 284). Each layer has its own hardpoints (map data `place`: outer_gate, outer_wall, yard, inner_wall, hq_side,
  forward).
- **Rings.** `fortress.rings` are polygons (inside the outer wall, inside the keep); `FortressDef.RingOf` and SiegeMode
  use them on a layered base (gates' outward from their wall's run, the fortress's props from `fortress.area`);
  `siegeRings` stay as axial distances for older readers. Stage 1 the forward relays, 2 the generators (yard), 3 the HQ.
- **Drops (B.2).** The defender's drop is inside the keep. The attacker's camp is the square's south-west camp; on a long
  map the attack's reinforcements (the player's purchases in Siege, the waves in Defend and Endless) land at the
  fortress's forward drops once a ring has fallen: (0, 128) before the buffer after stage 1, (-1, 196) before the outer
  wall after stage 2 (`SiegeMode.ForwardDrop`, through `BaseSystem.ForwardZone`); outposts and the command vehicle still
  win when they are further forward.
- **Buffer zone (B.3).** Two staggered rows of dragon's teeth (z 168), anti-tank ditches (z 178, painted dug ground),
  wire (z 185), each belt with gaps before the main gate, both sally ports and two between; shell holes; up to four
  firing positions on the attacker's side (z 136-140: earth banks open to the south, sandbags on the lip: the high
  ground the attack's guns fire from; `fortress.firing`). 1-4 fit per map (the square's buildings take the rest);
  the map stays static.
- **Slots by HQ level (B.4)**, `balance.json base.longLevels`: 4/1/0/1, 5/2/1/1, 6/3/1/2, 7/4/2/3, 8/5/3/4
  (small/medium/large/utility); every long base has exactly 8/5/3 + 4 utility base slots, listed most important first
  per size (outer gate, inner wall, outer wall, yard; large: yard, beside the HQ). The forward strongpoints
  (`longForward` 6 small, 2 medium) repeat the loadout's towers and do not count against the level. 300 m camps keep
  their table. `BaseRules.Slots/UtilitySlots(level, size, layered)`, `BaseLoadout.Layered`, `BaseLayout.Camp` read it.
- **Labels and the one loadout (B.5).** New `SlotPlace`s OuterGate, OuterWall, Yard, InnerWall (strings "Cổng ngoài",
  "Tường ngoài", "Sân trong", "Tường trong"). The plan keeps both kinds of places; a camp ignores the long places and a
  layered base the camps' own (beside the HQ and utility are shared). Until the player lays a long base out, its places
  borrow the camp counterparts' towers (outer gate <- gate, outer wall <- outer ring, yard and inner wall <- inner
  ring, over again, then any of the size): nobody's Defend base comes up empty. The first edit on a long base makes its
  places the plan's own; a camp's Auto-arrange keeps them. A long base can be set up on its own like a camp (key
  `<map>_long`). No save migration: old plans simply have no long places.
- **The Base screen** lists each map with a long battlefield twice, its camp and "<map> · dài" (the layered base),
  and shows the long table's locks and "Lên cấp" line there (`BaseSites.LongOf`, `PlanKey`). Its picture comes from
  `BaseMapShots` (now also `<map>_long`); until the pictures are rendered the screen draws the base without one.
- **Strength (B.6).** `BaseStrength.Power` of a layered loadout counts the extra slots and the forward repeats; Defend
  and Endless scale their waves on what stands (`Score(world, team)`), which already counts every tower raised.
- **Enemy fortress (B.7).** Siege and the weekly fortress raise the enemy's layered base from `BaseLoadout.ForAi(...,
  layered: true)` over every hardpoint (the AI fills all 28, as the corner fortress filled all of its), rings tougher
  inward as before; Defend raises exactly the player's plan on the layered base (`PlayerProfile.BaseLoadoutOnLayered`).

### Measurements

- **Path memory and time** (`LongMapTests`, desktop Ryzen 7 9700X, editor Mono, gates shut, every hardpoint holding the
  biggest tower): ashfield_long, swamp_long and metrocity_long are 150 x 240 cells; navigation memory (NavGrid, cover,
  the path finder's arrays, lanes and unit costs) 1.9 MB a map; a full-length route (the attack's camp to the HQ, the
  relays, the generators and the keep's drop zone, and back; 32 searches) 5.9 / 5.6 / 5.2 ms mean. Every route found.
- **Judgement.** Memory is well inside budget. Time: on the 6x slower phone a full-length route is about 35 ms, so a step
  that plans several of them at once would pass the 16 ms p99 step budget; most re-plans are short (the path queue's
  6 a step is unchanged). Not changed now (the owner's minimal rule); the testing phase's `TickBudgetTests` on the long
  Siege decides. The fix if it is over: an expansion budget per step on long maps (`PathCosts.MaxExpansions` already
  exists), then the two-level search above.
- **Tests run once** (EditMode: LongMap, MapConnectivity, BasePlan, BaseStrength, SiegeMode, Traffic, CheckpointReplay,
  Navigation, TransportRoute): 104 of 122 pass. The 18 failures are `TrafficTests.EverySiegeGateLeavesThreeCells` on the
  square `_siege` maps (not the long ones): `SimWorld.DebugDestroyProp` no longer destroys a `fortress_gate` since
  prompt 15 gave it armour 4 (its high-explosive blow is cut to 5 %), so the doors still stand. Not caused here; the
  lead should make DebugDestroyProp kill outright. PlaySmoke skipped (the owner's update).

### Merge notes (shared files touched)

Sim: MapDefinition, NavGrid, CoverGrid, JsonObject (FloatArrays), SimWorld (grids, ClampToMap, dodge edge), TacticalAi
(Clamp), SupplySystem, EconomySystem (EdgeBehind), BattleEvents (crate area), MissionMode (flee), MovementSystem
(aircraft edge), BaseSites, FortressDef, BaseRules, BaseLoadout, BaseLayout, BaseStrength, BaseSystem
(EstablishFortress), SiegeModes. Game: RtsCamera, Minimap, AirDrops, EffectsDirector, MapView, TerrainPainter,
BoundaryField, Surroundings, MatchRunner, ModeSessions (MapFile, fortress loadouts), BasePlan, PlayerProfile.BasePlans,
BaseScreen, Strings. Editor: BaseMapShots. Data: balance.json (base.longLevels, longForward), 20 new `*_long.json`.
Tools: longmap.py (new), build_maps.py / fortress.py / check_access.py / plot_map.py (rectangular grids; the square maps
build unchanged). No boss code touched.

**Lighthouse Bay:** once the lead merges it into `build_maps.MAPS` (with its SHAPES entry), `python Tools/maps/longmap.py
lighthousebay` writes `lighthousebay_long.json` (and runs check_access); nothing else is needed.

### For the testing phase (not run, by the token rule)

- `StuckBatch` on every `_long` map, Siege, Defend, Endless, Weekly, both sides, 5 seeds.
- `SiegeBalanceTests` and `ModeEndingTests` (they now play the long files): Siege 12-16 min with 60-75 % player wins,
  Defend's prompt 13 targets, Endless by base strength, the weekly's last stage; tune clocks and stage bonuses for the
  longer march there.
- `TickBudgetTests` on the heaviest long Siege; the base map pictures for the long bases (`BaseMapShots.RenderAll`
  with graphics, `-mbBaseMaps ashfield_long,...`); BaseScreenTests' face-spacing check on the long bases.

## 16C. Prompt 17: new units and towers (2026-09-29)

Part C of prompt 17: six vehicles and two towers. Parts A-B (long maps, layered bases) are on feature/p17-longmaps and
part D (the roster merges) comes after prompt 16's escorts, so this was built on lead/integration (db30d15) against the
roster as it is. The owner's token rule applies: one behaviour test per item, one targeted run, no sweeps.

### What each one is (data in balance.json)

| Id | Card | CP | Armour (front/side/rear/top) | Weapons (real, damage type, pen, form) | Stores / reload |
|---|---|---|---|---|---|
| `stealth_fighter` | Plane, act III | 20 | 0 (air) | `air_to_air` AIM-120 (Frag, 3, Sam), `guided_bomb` GBU-39 110 kg (HE, 3, GuidedBomb), `fighter_cannon` GAU-22 25 mm (Frag, 2, BeltedAutocannon) | 4 AAM + 2 bombs, the fighters' 11 s rearm (prompt 13 C) |
| `wingman_drone` | Plane (drone), act II | 6 | 0 (air) | `aim9` AIM-9 (Frag, 2, Sam) | 2 AAM, 11 s |
| `laser_tank` | Tank hunter, act II | 10 | 3/2/1/1 | `focus_laser` 300 kW (Energy, 4, Energy) | a 80-pulse stream, 1.5 s between |
| `shield_carrier` | Support, act II | 7 | 1/0/0/0 | `hmg_roof` M2 12.7 mm (K, 1, BulletBig) | magazine |
| `bunker_vehicle` | Heavy, act II | 8 | 2/2/1/1, dug in 4/2/1/1 | `gun_105_bunker` L7 105 mm (K, 3, Dart), `mg_coax` 7.62 mm (K, 0, BulletSmall) | single shots, 4.6 s |
| `swarm_carrier` | Plane, act III | 14 | 1 (air) | `swarm_drones` FPV 1.5 kg (SC, 3, Fpv; top attack, guided) | 8 drones a load, the bombers' 16 s rearm |
| `shield_tower` | large tower, act III | - | 2 all round | none | - |
| `cp_relay` | small tower, act II | - | 1 all round | none | - |

No new weapon form was needed (the laser is `Energy`, the swarm `Fpv`), so `combat_icons.py` is unchanged; the towers have
line icons of their own (`t_shieldgen`, `t_relay`) and the vehicles reuse their family's card icons.

### Rules (Sim)

- **Stealth fighter:** the existing aircraft stealth (seen at 0.4 of a spotter's sight, 2.5 s in plain sight after it fires,
  shown by radar stations over their base, guard towers within their guns' reach and UAV scans). `"sead"`: with no
  aircraft to fight and bombs left it goes for the nearest air defence it sees (`StrikeSystem.IsAirDefence`), and its
  free bomb mount weighs air defences x3. The commander rates it higher the more anti-air the enemy shows, which offsets
  the "interceptor with nothing to hunt" rule. Fewer stores than the fighter (4 AAM against 4 + 2) for 20 CP against 12:
  it pays for being unseen. The brief's "4 AAM and 2 small bombs in the bay; 25 mm gun" is the data.
- **Loyal wingman** (`"wingman"`): flies on the wing of the nearest manned aircraft of its side within 120 m (a leader with
  wingmen already counts 40 m further per wingman; a slow leader is circled), patrols halfway to the enemy with none;
  its own fights stay near the leader. **Decoy:** an anti-air missile fired at a manned aircraft with its wingman within
  25 m turns onto the wingman at 40 % (one draw a missile, and only when a wingman is alive, so battles without one draw
  the same numbers as before). **Cap:** `"airCapFree"` keeps it out of the six-aircraft count (deploy check, the AI's
  "air full" check, `AircraftCount`), and `"maxPerSide": 4`. It is faster than the fighter (46 m/s) to hold the wing.
- **Focused laser** (`"ramp"` on the weapon): x0.3 on a new target, rising linearly to x2 after 6 s on the same one; a new
  target or 2 s without a pulse on it starts again (`CombatSystem.RampScale`, per mount). Energy: APS, reactive armour and
  cages never stop it (prompt 15 C.9), smoke cuts it 80 %. Pen 4, so it pierces a heavy tank's front and a boss's hull.
- **Shield domes** (`"dome"`: carrier 12 m, 1,000 HP, 20 s; generator 25 m, 3,000 HP, 30 s; `DomeSystem`): every hit but
  energy (and burns, mines, redirected shares) on a ground unit or tower of its side inside is taken by the dome until its
  HP is spent; what a breaking dome cannot take goes through to the unit, never to a second dome. **No stacking:** a unit
  under two domes is covered by the one with most left. A shot from a ground vehicle inside the bubble passes. The dome is
  back at full its recharge time after its last hit (or its break), and scales with the emitter's rank like its health.
  Targeting: a covered unit is x0.3 for a weapon the dome stops, the emitter of a standing dome x2.5 (the generator first,
  or energy), and the commander's counter score adds up to +2.5 for energy weapons against domes it has seen.
- **Bunker vehicle** (`"deploy"`, `DeploySystem`): standing still 1 s with an enemy on the ground within its dug-in reach,
  or 4 s on guard away from its drop zone (a point, a choke, a siege line), it digs in for 3 s (no driving, no firing,
  moving armour); dug in: front +2 levels (4), reach x1.3 (34 → 44 m), turret all round; on its tracks the turret keeps
  within 45 degrees of the nose. A route more than 6 m away packs it up (3 s, the same way; a route given mid-dig packs up
  in the time it had dug), then it drives; while held it is never taken for stuck. The commander scores it up when
  holding (Defend stance, or every point taken).
- **Swarm carrier** (`"swarm"` on the weapon): a salvo of 8 FPV drones; each drone after the first takes the enemy on the
  ground within 18 m of the aim with the least already coming at it for its health, and a drone whose target is gone
  when it arrives strikes the nearest enemy within 18 m. The drones are projectiles, never aircraft (the six-aircraft cap
  counts the carrier only). Its bay spent, it flies out to rearm like a bomber (16 s). Countered as asked: fighters and
  SAMs shoot the carrier; APS (C-RAM, laser AA), EW towers and jammers stop or scramble its drones (the existing rules for
  drones).
- **Shield generator** (large slot): the dome above, two rank-7 branches by prompt 3's rule (a trade, not an upgrade):
  **Bulwark** (19 m, 4,800 HP) and **Pulse** (25 m, 2,100 HP, back 14 s after its last hit); three equipment slots like
  every tower (the tower gear system applies to every loadout tower). The enemy base picker draws it (default style 0.5,
  armour style 0.8).
- **CP relay** (small slot, `"relay"`, `EconomySystem.StepRelays`): +0.1 CP a second, the second relay +0.06, any more nothing
  (`RelayDef.MaxPerBase` = 2: `BaseLoadout.Fitted` leaves a third slot empty, the AI's picker stops at two, a fortress
  raises each relay once); nothing for 5 s after it is hit (the brief's "only while not under attack"); never on an outpost
  (`BaseLayout.Fits`, `BaseSystem.CallTower`). Branches: **Hardened** (1,100 HP, level 2, 0.08/0.05) and **Express** (0.12/0.07,
  450 HP, quiet 8 s). Attackers weigh an enemy relay x6 as a target. **Not a must-pick:** 0.16 CP a second is about 17 % of a
  side's base income (0.95) in exchange for two defensive small slots; the AI takes it at weight 0.35 (it showed in some
  of 40 seeded Hard bases, never in all: the test). Whether a human's optimal loadout always takes it is for the testing
  phase (the brief's sweep was not run, the owner's rule).

### AI use (both sides)

The commander (`ConquestAi.NewCardScore`): a wingman only with a manned aircraft of ours up (-4 without), a shield carrier
once the army is 5 vehicles (a second from 12), the bunker when holding, the stealth fighter by the enemy's anti-air; energy
weapons against seen domes. Tactics: the shield carrier is a support vehicle kept 3 m behind the front line (its dome over
the leading vehicles), the wingman is left to fly itself, the bunker digs in and packs up on its own. Counter-AI: domes pull
fire onto their emitter and away from covered units, relays draw attackers, SEAD and anti-air answer the new aircraft
through the existing rules (flares, SAM seekers, fighters hunting aircraft).

### Interface

Names, short names (15 letters at most), notes and Guide cards in both languages; the generated Behaviour lines cover the
new rules (`ul.dome`, `ul.deploy`, `ul.wingman`, `ul.airCapFree`, `ul.sead`, `ul.relay`, the weapon lines `ul.ramp` and
`ul.swarm`). Domes are drawn with prompt 11's shield (`EffectsDirector.Domes`: the sim's radius, follows the carrier,
ripples on `DomeHit`, flickers when low, shatters on `DomeChanged`). The bunker shows its state left of the health bar (an
amber bar filling while it digs in or packs up, a green bunker block dug in) and swings its spades down and raises its front
plate. In-action clips: a `Dome` scene (two friends under the dome shelled by two tanks) and a `Wingman` scene (a friendly
fighter and an enemy SAM vehicle); the laser, bunker, stealth fighter and swarm carrier use the plain range (their
weapons show their behaviour). Engine plumes for the three new aircraft.

### Tests

`Prompt17ContentTests` (8, one per item): stealth reveal and detection (sight, after firing, UAV scan, radar station); the
wingman on its leader's wing, pulling some SAMs, outside the cap; the laser's ramp (x0.3 to x2 within 6 s) and its reset on
a new target; the carrier's dome (absorbs, energy through, no stacking, overflow to the unit, back after 20 s, in battle);
the generator (covers 25 m, first target, placed by the AI, branches); the bunker's states and timings (3 s each way, armour
2 → 4, reach x1.3, no fire while busy); the swarm carrier (8 drones spread over a group, the side at its six aircraft); the
relay (pay, second relay, quiet after a hit, two to a base, not on outposts, the AI takes it sometimes and not always).

### Shared edits (other agents: merge by hand if they conflict)

`CombatSystem` (partial; the burst loop, `Launch`, target scoring, the stunned/busy check, the turret arc), `DamageSystem`
(the dome in `HitVehicle`, the swarm retarget), `MovementSystem` (the deploy hold, the wingman's flight, SEAD, the dug-in
reach), `EconomySystem` (relay income in `Earning`, the air cap exemption), `SimWorld` (two systems in the step),
`BaseLoadout` (relay cap), `BaseLayout.Fits`, `BaseSystem.CallTower`, `ConquestAi` (partial; buy scoring), `TacticalAi`
(support placement, wingmen), `WeaponDef`/`WeaponState`/`Projectile.Target` (now settable), `SimEvent` (two kinds appended),
`Vehicle.ArmourOn`, balance.json (three weapons after `hover_ciws`, six vehicles after `long_sam`, towers after
`guard_tower`, two base-style weights), campaign unlocks (act2.py, act3.py and campaign.json), `MatchSettings.AllVehicles`,
`CardIcons`, `TowerIcons`, `Icons` (two SVGs), `EffectsDirector` (two cases, one tick, three engines), `VehicleView` (three
lines), `FiringRange.Abilities` (two scenes), `UnitLines`, `Strings`/`GuideText`/`UnitText` (appended), `build_assets.py`
(one import and builder merge).

### Left (not done here, and why)

- **C.9 balance with `CombatValueMeasure`:** not run (the coordinator's rule for this pass: one targeted test run). Part D
  is not merged either, so the numbers above are starting values set by the calibre scale and by analogy (the stealth
  fighter against the fighter at 12 CP, the laser tank against the tank destroyer, the swarm carrier against the FPV
  carrier and the bombers). Run the measure after D, add the new ids to it, and set their `"value"` (all 1 now).
- **Card renders** (`CardRenders.RenderBatch`, needs a batch run with graphics) for the eight new cards; `CardRenderTests`
  will flag them until then.
- The whole EditMode suite, `ModelTests`/`MuzzleAuditTests` on the new models, PlaySmoke, and the performance check of many
  drone swarms (brief E): testing phase.
- Long maps (A-B) will need the relay and the generator in their slot labels only through the existing size rules.
