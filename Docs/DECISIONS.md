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
- **Proper names kept in Vietnamese** (superseded by `NameText.Kept` in code, DECISIONS 20L; checked by `UiLanguageTests` over every Vietnamese text of the game, the kit's, the menus', the guides' and the campaign's; every other unmarked Latin word counts as English): abbreviations and units `CP`, `HQ`, `HP`, `HUD`, `UAV`, `FPV`, `SAM`, `EMP`, `SEAD`, `MOAB`, `APS`, `ATGM`, `IFV`, `MLRS`, `GMLRS`, `EW`, `CIWS`, `FPS`, `mm`, `cm`, `MW`, and the Vietnamese abbreviations `PK` (phòng không), `TT` (trực thăng), `ST` (sát thương), `TL` (tên lửa), `SCH` (sở chỉ huy), `CT` (công trình), `TN` (tinh nhuệ, in the short names of elites); real weapons and vehicles the units are modelled on `AC-130`, `Ka-52`, `Grad`, `Smerch`, `TOS`, `Iskander`, `Patriot`, `Tunguska`, `ZU`, `BMPT`, `Terminator`, `Ataka`, `BTR`, `Object`, `Bradley`, `TOW`, `Centauro`, `Sprut`, `PzH`, `Merkava`, `Trophy`, `Kornet`, `Iron`, `Cobra`, `Lancet`, `Shahed`, `Hellfire`, `Stinger`, `Apache`, `Little Bird`, `Reaper`, `Maverick`, `Alligator`, `Vikhr`, `Igla`, `JASSM`, `Wolf`, `Griffin`, `Centurion`; the bosses' and branches' code names `Behemoth`, `Inferno`, `Tempest`, `Hive`, `Bastion`, `Spectre`, `Titan`, `Napalm`; the equipment brands `Ironclad`, `Kestrel Dynamics`, `Vulcan Arms`, `Longbow Ordnance`, `Aegis Systems`, `Stormfront Aviation`, `Hivemind Robotics`, `Quartermaster`, `Spectre Electronics`, `Hammerfall Munitions`, `Phoenix Recovery`, `Wolfpack Tactics`, `Bulwark Engineering`; the story's people and faction `Varga`, `Kessler`, `Orlov`, `Aurel`, `Hegemon`; the game `Machine Brigade`; and three words Vietnamese took in whole: `radar`, `drone`, `boss`, with `vonfram` (tungsten) and `pin` (battery), which the syllable check cannot tell from English.
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

## 16D. Prompt 17: roster review, merges, save migration (2026-09-29)

Part D of prompt 17 on lead/integration (b2528d2, parts A-C merged), then C.9 for the new units and three follow-ups.
The owner's token rule: one measure run (the whole roster takes 11 s, so C.9 was measured, not guessed), one targeted
test run, no sweeps.

### D.1-D.5 The merges (`CardMerges.Into`, roster version 2)

Ids stay as they were (the surviving card keeps its id, display names live in the text tables), and the model of the
card that went is kept in the model library, named on the survivor as `"altModels"` (`VehicleDef.AltModels`, never
drawn now) for the camouflage prompt. The gone cards' defs are out of `balance.json` (as prompt 13's merges did); their
`unit.`/`short.`/`note.` strings stay for that prompt, their Guide cards are gone.

| Gone | Became | The merged card |
|---|---|---|
| `tank_buster` (A-10) | `attack_jet` "Cường kích" | The Su-25's model (it was already the "Cường kích" card, and its bombs are a loose part of that model); the A-10's kept. Weapons of both on the calibre scale: GSh-30-2 30 mm, S-8 80 mm pods, FAB-250 bombs, **two Kh-29L** (pen 4; the unused `kh29` is now a store of 2), two R-60s for self-defence. 460 → 700 HP and armour 1 → 2 (the A-10's toughness), 34 → 32 m/s. 13/16 → **15 CP**. |
| `heavy_attack_heli` (Ka-52) | `attack_helicopter` "Trực thăng tấn công" | The Apache's model; the Ka-52's kept. The Ka-52's stand-off (`"standoff"`: it holds at 60-92 % of its missiles' reach, away from short-range AA) with a new `hellfire_standoff` (AGM-114L Longbow: the Vikhr's numbers, pairs from 55 m), the M230, Hydras and two Stingers (the self-defence AAM). 500 → 800 HP. 9/13 → **11 CP**. The Mi-24 (`gunship_heli`) stays its own card. A bought Ka-52 (3,500) is refunded. |
| `atgm_carrier` | `fpv_carrier` | Unchanged. The ground anti-tank missile role is the IFV's, the BMPT's and the ATGM tower's. |
| `sapper` | `engineer_vehicle` "Công binh" | The engineer already repaired vehicles (2.5 %/s within 14 m) and towers at half that (1.25 %/s, twice the sapper's fortify), cleared the mines it sees and broke obstacles x3 with its MG, and does not rearm (prompt 13). That is the brief: obstacles are the bulldozer's (its blade flattens teeth as it drives; the engineer's 12.7 mm against armour 3 is slow even at x3). 700 → 800 HP (the sapper's), 3 CP. The `fortify` aura stays in code, unused. |
| `gun_pit` (tower) | `gun_turret` | The pit and its two branches are gone; the hidden-pit rule (`hidden`, `HideGunPits`) stays in code, unused. |

**Migration** (`PlayerProfile.MigrateRoster`, `RosterVersion` 1 → 2). The prompt 13 loop is idempotent, so a version-1
save runs it again with the new pairs: the unlock goes to the card it became (unless that is a starter), the higher rank
stays, the coins and blueprints spent on the lower rank come back, a bought premium card is refunded. New,
`MergeTower` (the gun pit): every slot holding it becomes the gun turret (the old sized lists, the three plans' slots,
outposts and per-map set-ups); its pieces move into the turret's empty slot of the same kind when they fit it
(`TowerFit.Fits`), otherwise they stay in the bag, owned and worn by nothing; its rank-7 branch choice is dropped (the
turret keeps its own). Vehicle equipment is worn per branch, not per card: nothing to move. Saved decks already read
merged ids through `CardMerges.Resolve`.

**Everything that named them:** `MatchSettings.AllVehicles`, the shop's premium list and `Progression`'s prices, the
enemy base style weights, the hovercraft's landing party (ATGM → FPV carrier), the campaign's enemy decks, generals,
waves and reinforcements (the card each became; a deck naming a card twice keeps it once), unlocks (below), the range's
jammer and interceptor scenes (an ATGM tower: missiles and no gun), the editor shot lists, and the tests (below).
Elites and boss escorts named none of them.

### D.6 Twin tank and heavy tank, told apart

- **Twin tank = tank hunter:** `gun_120_twin` (two Rh-120 rounds of 240, one volley 0.05 s apart, 7 s reload, 34 m),
  armour 3/2/1/1, 5.6 → 6 m/s, turret 55 → 65 degrees/s (the heavy tank: 4.2 m/s, 45).
- **Heavy tank = breakthrough:** its 152 mm loads `gun_152_he` (HE-FRAG 320, 5 m blast, pen 3) for a structure, a
  tower, a vehicle of front armour 1 or less, or a wall, and armour-piercing otherwise (`"he"` on the weapon,
  `WeaponDef.HeRound`, `CombatSystem.RoundFor` at launch; the mount's cooldown is shared). Armour 4/3/2/2 (explicit now).
  Its Behaviour line `ul.heRound`.
- **The check** (the measure, one seed): time to destroy the two battle tanks: twin **37.9 s**, heavy 42.3, titan 42.7
  (with AA: 44.6 / 48.3 / 52.7). Survival (share of the 90 s): heavy **82.8**, titan 82.6, twin 69.0. Structure value per
  CP (fort): heavy **541** at 10 CP (451 at 12), titan 393, twin 274. The group is the turreted heavy tanks (twin,
  heavy, titan); the siege tank (fort 808) is the 203 mm siege gun and the bunker vehicle a dug-in gun, neither a tank
  of this group. Met; nothing to retune.
- The HE round raised the heavy tank's ground value per CP from 497 (prompt 15) to 572, far over its class (median
  404), so it went **10 → 12 CP** (477 projected: the group of two is the same at 12).
- The Behaviour and Guide texts of both say what they are now.

### C.9 Costs from the measure

`CombatValueMeasure.MeasureTheRoster`, `MB_BALANCE=1`, the whole roster, seed 13 (408 runs, 11 s). Raw files:
`Docs/balance/combat_value_p17d*.tsv` (`_final` after the costs). The rule is prompt 13's: within ±15 % of the role's
median value per CP ("ground" for what fights the ground; the fighter and anti-air on "air"). Class medians this run:
heavy 404, tank hunter 427, helicopter 302, strike aircraft 402, fighter (air) 353. `"value"` (the commander's weight) is
per CP over the class median, as prompt 15 recomputed it.

| Unit | CP | Measured per CP | Why |
|---|---|---|---|
| stealth fighter | 20 → **14** | air 148 + SEAD ground 69 at 20; 212 + 99 at 14 | The fighter does 353 in the air for 12 CP; the stealth fighter does both jobs, together 311 at 14 (-12 %). Weight 0.88. |
| loyal wingman | **6** (kept) | 0 alone | A group of wingmen with no manned leader patrols and never engages; not measurable without a leader (testing phase). |
| focused laser tank | **10** (kept) | 432 | In the tank hunters' band (427). Fort 667: strong on hard targets, as asked. |
| shield carrier | **7** (kept) | support (0) | Judged by what it does for others, like the other support vehicles (testing phase: a dome measure). |
| bunker vehicle | 8 → **6** | 277 at 8; 361 at 6 (count unchanged) | The attack scenarios see it packing and unpacking; at 6 it is the battle tank's value. Weight 0.89. Its dug-in defence is for the testing phase. |
| swarm carrier | 14 → **8** | 205 at 14; 291 at 9 (final run); 327 at 8 | Next to the strike drone (325), the other drone platform, both under the strike band. Weight 0.81. |
| attack jet (merged) | **15** | 478 at 14; 446 at 15 | Top of the strike band (+11 %). Weight 1.11. |
| attack helicopter (merged) | **11** | 316 | In the helicopters' band (gunship 302). Weight 1.05. |
| twin tank | 9 (kept) | 442 | +9 %. Weight 1.09. |
| heavy tank | 10 → **12** | 572 at 10; 477 at 12 | See D.6. Weight 1.18. |

The two new towers (shield generator, CP relay) take slots, not CP; nothing to set. The "air" reference group is the
attack helicopter and the attack jet, both changed, so every anti-air value moved a little; no anti-air card was touched.

### Follow-ups

- **Campaign unlocks** (`build_campaign.py` failed its own "5 to 7 cards a chapter" rule since 16C: chapter 5 opened 10):
  the recon drone c6m05 → c3m05 (the ATGM carrier's reward), the focused laser tank and the CP relay → c4m10 (the gun
  pit's), the EW jammer c5m03 → c7m04, the smoke carrier c6m07 → c8m04, the counter-battery radar c4m03 → c8m06 (the
  sapper's); the A-10's c9m04 unlock is gone (the attack jet opens at c4m02). Chapters open 6/6/7/7/7/7/6/6/7 cards;
  coins and blueprints unchanged. `campaign.json` regenerated. **`CampaignText.cs` was left as committed:** the generator
  would have undone hand-made Vietnamese fixes in it (Bọ Bạc, rốc-két); nothing in D changed its texts.
- **Lighthouse Bay's long map:** `python Tools/maps/longmap.py lighthousebay` (28 hardpoints: base 8/5/3 and 4
  utilities, 8 forward; 3 relays, 3 generators, 4 firing positions). The long-map modes pick
  it up by name (`ModeSessions`).
- **The hovercraft's escort** (`hover_gunboat`) wears the fast missile boat's model (`missile_boat`, its 14 x 3.8 m
  hull, the CIWS on the boat's `mg` mount); it keeps its id, name and air cushion (it still crosses land). ASSET_DEBT says so.

### Tests

`Prompt17RosterTests` (5): the vehicle merges' migration (rank, blueprints, refunds, unlocks, once only), the gun pit's
(rank, equipment into the empty slot and back to the bag, slots, outposts, map set-ups, branch), the merged cards' weapons
and kept models, the heavy tank's round choice, Lighthouse Bay's long map and the escort's boat. Existing tests that named
the old cards: missile shooters are the ATGM tower (a Kornet on mount 0, no gun: APS, radar-absorbent coating, laser
warner, the jammer's range scene, Leviathan's CIWS) or the BMPT (Ataka beyond its cannons: boss protection parts, the
Iron Beam value); the A-10 and Ka-52 cases are the attack jet's and the attack helicopter's (the stand-off test, the stores
test, `CounterTests` "Attack jets beat heavy tanks", the measures); the sapper's tower repair is the engineer's; the gun
pit's hiding test is gone. **The stores test** (a jet out of stores mid-attack finishes its hold before it leaves) now holds
the in-flight refill off: out of danger the attack jet's 16-round S-8 pods refill about a round a second, so the jet is
never dry at once (prompt 13's rule, not D's; the A-10 passed on timing). Run: `Prompt17RosterTests`, `RosterMergeTests`,
the changed cases above, `UnitLinesTests`, `LocalisationScanTests`: 36 cases, 33 passed at first; the APS, jammer and
stores cases were fixed and passed on a rerun.

### Left for the testing phase

- The whole EditMode suite (among the changed tests not run: `CounterTests`' new case, `CombatIconTests`,
  `EquipmentLab`/`EquipmentRiskLab`, `BaseBalanceTests`, `CampaignTests`, `StuckBatch`), `ModelTests`/`MuzzleAuditTests`
  (the attack jet's second missile mount, the twin tank's new gun), PlaySmoke.
- `CampaignTests`' seeded sweeps: FPV carriers replace ATGM carriers in Kessler's and Varga's decks and early waves, the
  heavy tank costs 12 from chapter 2, the moved unlocks.
- A measure of the loyal wingman with a leader, of the shield carrier's dome, and of the bunker vehicle holding a line;
  a multi-seed look at the swarm carrier and the stealth fighter (the biggest cost changes).
- Card renders: unchanged ids, nothing new to render for D.
- The first-shot reading of "opening shot" (the twin tank's burst on a fresh target) could use a duel measure if the owner
  wants it sharper than the group numbers.

### For the prompts on hold

Stable ids apart from display names (the surviving card's id is unchanged, the merged ones resolve through
`CardMerges`), `altModels` for the camouflage prompt, every new name and line in the text tables (`Strings`,
`GuideText`, `UnitText`); no radio lines were added.

### Shared edits (other agents: merge by hand if they conflict)

`balance.json` (the five defs out; attack jet, attack helicopter, twin tank, heavy tank, engineer rewritten; three
weapons after `gun_105_bunker`; `kh29`, `gun_152`; the new units' costs; the hover gunboat; a style weight; the landing
party), `CombatSystem.Launch` (one line) and `CombatSystem.P17` (`RoundFor`), `Catalog`/`Catalog.P17` (`he`,
`altModels`), `WeaponDef.P17`/`VehicleDef.P17`/`Definitions` (copy), `CardMerges`, `PlayerProfile.Arsenal`
(`MergeTower`), `MatchSettings.AllVehicles`, `Progression`, `MenuScreen.Shop`, `FiringRange.Abilities`, `UnitLines`/
`UnitText`, `Strings` (five notes), `GuideText` (five cards rewritten, five dropped), Tools/campaign (act1-3, story) and
`campaign.json`, the tests listed above.

## 17A. Prompt 18: a big attack for every boss (2026-09-29)

Prompt 18 on feature/p18-attacks from lead/integration 3661222 (prompts 9, 13, 15, 16 and 17 merged). The owner's
token rule: compile, one targeted test run, no sweeps, no screenshots; the 5-seed runs are listed for the testing phase.

### A. One system, data-driven (`BossSystem.BigAttacks`, `BigAttackDefs`)

- Every boss names one entry of balance.json `"bigAttacks"` (`"bigAttack": "<id>"` on the boss). An entry is a list of
  strikes, each a shape from one shared library (`BigShape`: circle, strip, line, sweep, swarm, missile, drop, buff,
  quake) with its numbers. No class per boss: prompt 20 E.3 adds shapes to the same enum and system, prompt 19 F swaps
  the Silver Bug's `bug_laser_sweep` for a rod-rain entry by changing one id, prompt 20 G gives a mini boss
  `"bigAttackScale": { "damage": 0.7, "cooldown": 1.3 }` (parsed now, used by no boss yet). Damage, cooldown and warning
  are separate fields and scale separately (`BigAttackScale`: difficulty first, then the boss's own).
- Ids are stable and apart from display names: every name, radio line, cancel notice and guide line is a text key made
  from the id (`bigattack.<id>`, `radio.bigattack.<id>`, `bigattack.<id>.cancelled`, `guide.bigattack.<id>.how/dodge/stop`)
  in the new `BigAttackText` table (read by `Strings.Get/Has` and the localisation scan). No text is in code or data.
- Rhythm: the first about 30 s after the boss appears (`bigAttackRules.first`), then one per cooldown, measured start to
  start. Stunned, transforming, landing troops or underground (except the worm's own dive), it waits a second; with no
  target in reach it looks again in 3 s; with every part carrying it broken it has lost it and looks again every 2 s, so
  a self-repair (prompt 9) brings it back.
- The warning (`BigStage.Charging`): the zones exactly as they will land (`BigZone`: circle, or rectangle along an
  axis; a walking barrage and a missile volley also get one ring per point with its own countdown), the radio line,
  an alarm and a whistle, and the parts that carry it: their mounts hold fire (A.2, `Vehicle.MountHeld`, also through
  the firing), and mechanisms named in `"hold"` wait (the supergun's ordinary shell, the Leviathan's single cruise
  missiles; if one of those is still in the air the big attack waits for it to land, so the two never stack).
- Cancel (A.5): each strike lists its parts; with all of them broken during the warning the strike is cancelled (the
  whole attack with all strikes gone: `SimEvent BigAttack` 2, the HUD's short notice). `"perPart"` gives each standing
  part its own rounds, counted as it fires: a train gun car broken leaves 3 shells, a Hive rack 10 drones, an Iron Bird
  pod 24 rockets, an Inferno flamer its half of the ring (`"sectors"`: each part covers the side it sits on). The
  Supreme Commander's antenna carries both strikes; the hovercraft's rockets and ramp are separate strikes.
- EMP (`"empDelay"`, Tempest 2 s, Silver Bug 2.5 s): each time the boss is stunned during the warning the charge and
  every zone's countdown move on by that much.
- Damage goes through the damage rules (prompt 15): blasts hit as called strikes (top face, fragments pierce level 1 at
  most on vehicles, the strike's own level on structures, thermobaric tag, damage type table), a line or a sweep as a
  pierce from the boss (the face turned to it, its own penetration), a drone as a direct top-attack hit. So smoke cuts
  the laser to 20 % (the energy rule) and never the railgun, shield domes take everything but the beam, APS never sees
  a beam. `"structure"` multiplies damage on buildings and towers; `"falloff"` is the share left at a blast's rim.
  Everything scales with the boss (`DamageBoost`, `DamageScale`: campaign scaling, phases, elites) and the difficulty.
- Missiles and drones fly (`BigFlyer`): every 0.25 s the other side's anti-air under one (any weapon that can target
  aircraft, in its range) takes `aaHit` (0.5) of its paper damage a second off it, and each APS, C-RAM or
  point-defence laser in reach spends an interceptor for `intercept` (150) health; a laser APS is blind in smoke.
  Doomsday missile 600 health over 12 s, Leviathan missiles 250 over 8 s, Hive drones 60 at 26 m/s (they home on
  their targets, split over at most four of the heaviest armour in the group; a jammer at the target throws half off).
- Dodging (A.6): the other side's ground units inside a harmful zone (units that are not scripted, static or stunned)
  make for the nearest way out, the zone's blast radius and 3 m past its edge, if they can reach it before it lands
  and it is not inside another zone; after it has landed (and its burning ground is out) they go back to their earlier
  order or where they stood, unless they were given another order since. All in vehicle-list order: deterministic.
  Aircraft need no dodge: every big attack hits the ground only (as the ordinary ground blasts do).
- Everywhere the boss appears (A.8): `SimWorld.BigAttackSettings`, set by `ModeSessions` from the session's difficulty
  key for every mode (campaign, big campaign, Boss Rush, Operations), and by `MissionMode` and Boss Rush as Normal when
  nothing set them; bare test battles have none (as with escorts), so older measures are unchanged.
- Difficulty (A.7): Easy damage x0.8, cooldown x1.2, warning +1 s; Hard cooldown x0.9; Very Hard (and Heroic, Iron)
  cooldown x0.8, damage x1.1 (`bigAttackRules.difficulty`).

### B. Each boss (Normal, before armour)

Numbers are the spec's except five: four set from a first estimate against our health scale before the run (Tempest,
Inferno, Supreme Commander, Hive) and the Behemoth from the run's centre measure (section E). Aim `group` is the other side's
densest spot of ground units and towers within the entry's reach.

- Iron Train `train_broadside`: strip 60 x 12 along its heading, 6 x 330 HE (r 6), 3 a gun car; 3.5 s / 65 s.
- Tempest `tempest_rail`: line 90 x 3 from the boss, 1 300 kinetic pen 4 (spec 1 400, which would take a battle tank at the
  centre to 62 %; at 1 300 it measured 42 %), 15 % less each unit behind; 4 s / 60 s; EMP +2 s.
- Behemoth `behemoth_barrage`: circle r 14, 3 pairs x 340 HE (r 8; spec 480: an IFV at the centre measured 103 %).
- Doomsday Train `doomsday_missile`: erector 5 s, then one thermobaric missile (2 500, r 18, 30 % at the rim, 600 hp,
  12 s) at the HQ, or at the biggest group when it holds 4 units or more; 90 s.
- Rail Supergun `supergun_heavy`: one shell anywhere at the biggest group standing still, 1 800 (r 20), ground burning
  8 s (25 a second, r 10); fire control broken: up to 15 m off and the ring as wide; 4 s / 60 s; ordinary shots kept.
- Inferno `inferno_firestorm`: ring r 18 round it, 200 fire (spec 250) and the ground burning 10 s at 45 a second
  (spec 60): burning ground is raw damage; at 200 an armoured car lost 40 % to the burst alone; 3 s / 60 s.
- Supreme Commander `supreme_offensive`: its side within 60 m +35 % damage, +25 % fire rate for 12 s, and a bomber
  (the neutral raid's model) lays 8 x 340 (spec 300; an IFV at the centre measured 45 %) in a 50 x 10 strip on the biggest group; 4 s / 75 s.
- Hive `hive_swarm`: 20 drones x 180 (spec 150: four targets share the 20; at 180 a battle tank measured 32 %); 4 s / 70 s.
- Landing Hovercraft `hover_assault`: 24 x 58 rockets on a 40 x 20 strip, then 6 vehicles off the ramp (2 battle tanks,
  2 IFVs, 2 armoured cars, elites by the difficulty's budget; at most 6 of them alive, apart from the escort cap).
- Ice Fortress `fortress_rocket_rain`: 32 x 58 over 4 s in r 25, 16 a box; shield domes absorb it.
- Silver Bug `bug_laser_sweep`: 4 m beam down 120 m in 3 s, 900 energy once a unit; smoke 20 %; EMP +2.5 s.
- Earth Worm `borer_quake`: its next dive is the big one (the burrow runs it: under the biggest group, the crack is
  the 3 s warning), 700 (r 16, 30 % at the rim), 3 s stun on the ground; the drill broken, no dive, no quake.
- Bastion `bastion_mortar_walk`: 6 x 460 (r 9, x2 on structures), one every 0.7 s down a 60 m line towards the target.
- Spectre `spectre_orbit`: 8 s on one r 15 circle: 105 mm 300 every 1.5 s, each 40 mm 3 x 30 every 0.8 s, 25 mm 15
  every 0.2 s; it takes 1.5x damage from the warning to the end (the "hit 50 % more" read as damage: only anti-air and
  fighters reach it anyway), and breaks off after taking 8 % of its health while firing.
- Iron Bird `ironbird_rocket_run`: 48 x 32 rockets down a 70 x 8 line, 24 a pod; 3 s / 60 s.
- Hive Carrier `carrier_heavy_bomb`: one 850 bomb (r 14, x2 on structures) on a group within 40 m; it stops for the
  3.5 s warning and takes 1.3x damage meanwhile.
- Command Airship `airship_carpet`: 12 x 300 in a 70 x 12 strip along its course; 3.5 s / 70 s.
- Leviathan `leviathan_volley`: 6 cruise missiles x 450 (r 8, x2 on structures, 250 hp, 8 s) at the HQ, the toughest
  towers and the biggest group, in pairs; the launch cells broken in the warning cancel it. Its salvos, single cruise
  missiles, landing craft and phase-3 volley are unchanged (the single missiles wait while the volley charges).

### C. The three new parts

`nuke_train.erector` (0.09, armour 2), `drone_mothership.bomb_bay` (0.09, armour 2), `command_airship.bomb_bay` (0.07,
armour 2, no break damage like the rest of the airship's). Prompt 9's totals kept (each boss 0.70 of the body): the
train's flak cars 0.10 to 0.08 and its rocket car 0.10 to 0.09; the carrier's gondola cannon and UAV bay 0.10 to 0.08,
its shield 0.10 to 0.09; the airship's radar 0.08 to 0.07. Kinds `erector` (ballistic icon) and `bombbay` (bomb icon)
on the parts row; the break effects are the generic blast and smoke at the break (prompt 9); breaking one reads "its
big attack goes with it" in the Guide; each has a radio line. No model nodes yet (ASSET_DEBT).

### D. HUD and guide

- The boss bar has the attack's icon with a thin cooldown bar; it lights red with the seconds left while it charges,
  and the part icons that carry it flash (D.1). No new frame in the middle of the screen (prompt 11).
- Zones (`BigAttackZones`): one look for every boss, unlit HDR red outlines and strike rings whose fill runs to the
  moment it lands, no fill over the player's units (D.2); the charging part pulses on the model (A.3).
- A short notice when a big attack is cancelled or the Spectre breaks off (D.3). The Guide tab has a Big attack
  section: name and numbers from the data, how it works, how to get out of it, how to stop it, who it is for (D.4).
- Not done here: the "In action" clip with the big attack (D.5) and per-boss sounds (one alarm and whistle for all);
  both in ASSET_DEBT.

### E. Balance (first pass, one seed)

`BigAttackTests.EachBigAttackAtItsCentreHurtsButNeverWipesOutAGroup` puts five of each attack's primary target (rank 1,
standing, not dodging) at the centre and logs the share of one's health each lost. With the numbers of section B: train
46 %, Doomsday 44 % (a gun turret), Behemoth 103 % (at 480; now 340), Tempest 42 %, Inferno 40 %, Hive 32 %, Ice Fortress 12 %,
Bastion 19 % (a gun turret), Silver Bug 40 %, Spectre 33 %, Iron Bird 20 %, Hive Carrier 43 % (a turret), Supergun
106 % (its ordinary shell landed with it: fixed by the hold, 60 % expected), Earth Worm 40 %, Airship 74 % (an
armoured car; an IFV about 45 %), Hovercraft rockets 12 %, Supreme Commander 45 %, Leviathan 61 % (six missiles on one
turret with no base on the test field). No attack wiped out the group. Still outside 40-60 % and left for the 5-seed
tuning: the three 122/80 mm rocket attacks (Ice Fortress, Iron Bird, hovercraft: calibre-scale warheads spread over
the spec's areas; tighten the areas or aim the rockets at units), the Bastion and the Hive Carrier on towers.
The big attack's damage a second on paper (`BigAttackDef.Sustained`) is there for the combat-value meter (E.1); the
kill times and win rates (E.2, E.3) need the testing phase's runs.

### Tests

New `BigAttackTests` (11): every boss's entry and words and the new parts; the difficulty's scales; first at 30 s then
the cooldown; a broken part cancels it and it stays lost; each part its own rounds; EMP +2 s; every zone's shape and
size from its data (all 18 bosses); the Doomsday missile shot down by C-RAMs; smoke cuts the beam to a fifth and not
the slug (15 % less behind); units get out and back, twice the same; the centre measure. `BossPartsTests` updated (the
three bosses' part counts; a part that carries the big attack does something), `LocalisationScanTests` reads the new
table. One run of those (15 tests): 11 passed; the four failures fixed after it and not rerun (the owner's rule): the
parts test (the new parts carry only the big attack), the guide words test (it already failed on lead: the
Leviathan's `cruise`, `craft` and `radar` stops had no words; added), the rounds test (the Iron Train's self-repair
put its gun car straight back: the test uses the Iron Bird now), and the dodge test (a unit that has arrived is idle,
not on its move order: it now goes back from either).

### Left for the testing phase

- Rerun `BigAttackTests` and `BossPartsTests` (the four fixes above are unverified), then the suites.
- 5 seeds at each difficulty: every boss mission of the campaign and the big campaign, Boss Rush, Operations with a
  boss; win rates and kill times against prompts 9, 13 and 16's targets; tune the numbers in section E.
- FPS at Low on a low-end device during the Hive's swarm, the rocket rains and the Leviathan's volley.
- Screenshots of every big attack's warning into docs/ui-screens (F), and a look at the zones on every map and
  weather; the missile and drone rounds keep flying on screen after the sim shoots them down (the pop shows where).
- Whether auto-dodging suits the player's hand orders in play (it only moves units still on their earlier order).

### For the prompts on hold

Prompt 19 F: replace `bug_laser_sweep` with a new entry and point `silver_bug.bigAttack` at it (a rod rain is a circle
or strip of rounds with `"top": true`). Prompt 20 E.3: new shapes go in `BigShape` and `BossSystem.BigAttacks`; G: a
mini boss is a boss def with `"bigAttackScale"`. Prompt 23: the radio lines are one text key each.

### Shared edits (other agents: merge by hand if they conflict)

`balance.json` (`"bigAttack"` on the 18 bosses, three new parts and the part shares above, `bigAttackRules` and
`bigAttacks` after the escorts), `BossSystem` (Joined, Step, the burrow's crack and quake), `BossSystem.Parts` (the
aim's danger, the fingerprint), `Vehicle.Boss` (`MountHeld`, `BigAttack`, `BigTaken`, `BigQuake`), `DamageSystem`
(one line), `SimWorld` (`BigAttackSettings`), `SimEvent` (`BigAttack`), `VehicleDef.Extra`/`Catalog.Extra`,
`MissionMode`, `SiegeModes`, `ModeSessions`, `MatchRunner`, `AudioDirector`, `EffectsDirector`, `BattleHud`,
`MissionBar` (BossBar), `BossPartsRow`, `MenuScreen.BossParts`, `Strings` (the text hook, three stop words),
`Screens.uss`, `BossPartsTests`, `LocalisationScanTests`.

## 18A. Prompt 19: the Silver Bug as an orbital spacecraft (2026-09-29)

Prompt 19 on feature/p19-orbital from lead/integration 2226d83 (main v0.29.0; prompts 9, 13, 15-18 merged). The owner's
token rule: compile, one targeted test run, no sweeps, no screenshots; the 5-seed runs are listed for the testing phase.
The id stays `silver_bug` (records, progress, achievements); "Icarus" (prompt 20) will be a display name only.

### A. Altitude tiers, data any boss opts into (`TierDef`, `BossSystem.Tiers`, `Vehicle.Tiers`)

- `AltitudeTier`: None (every unit that does not opt in: the ordinary air/ground rules, unchanged), Low, High, Orbit
  (nothing reaches it; prompt 20's submerged Typhon can reuse it). Ordered from the lowest: a change counts as the lower
  of its two tiers (B.4), the descent from orbit as high.
- A boss's `"tiers"`: `opening` s in orbit (untouchable: `Invulnerable`, its guns held by the combat system's orbit
  gate; its big attack and first pods still come), `descend` s down (a satellite stays at `SatelliteAt`), then per
  phase (`marks`, 0.7 and 0.3) its `schedule` of steps repeated; `shift` s a change (3.5), longer by the speed its broken
  manoeuvring thrusters took (`shift / PartSpeed`); drawn `heights` (orbit 150, high 60, low 22 m, eased in the view).
  Never back to orbit: a schedule may only hold high and low (the parser refuses orbit there).
- Reach (`TierRules`, one rule for the sim and the HUD): a weapon's `"ceiling"` (railgun: low; the long-range SAM's
  48N6 and the Patriot family's missiles: high, the Patriot branches inherit it), a carrier's `"ceiling"` for its
  anti-air weapons (fighter and stealth fighter: high, so their AMRAAM, Sidewinder and gun), any weapon that can hit
  aircraft reaches low, and a helicopter's weapons reach low (the spec's "helicopters", read as the helicopters'
  own weapons). `CombatSystem.InReach` asks it for a tiered target; the air-versus-ground targeting penalty is off
  for one. The railgun's exception is for tiered targets only: an ordinary aircraft is still out of its reach.
- Opening 15 s; phase 1 high 25 / low 10, phase 2 high 15 / low 20 (the spec's starting points, kept for the testing
  phase's 5-seed tuning). Phase 3 is the crash (E). The main engine broken, it comes down and holds low (the HUD
  countdown goes); the schedule's timing runs on underneath.

### B. Parts and armour (C)

Ten parts, 7 % of the body each (prompt 9: 0.70 in all, 7-15 % each; the four thrusters and two lasers the spec asks for
leave no room above 7 %): `main_laser` (mount 0, the ventral `orbital_laser`: the saucer's 150 kW laser renamed, pen 4),
`main_engine` (stops `thrust`), four `thruster_*` (speed 0.88 each), `pd_laser_l/r` (stop `aps`: the boss's APS, 3
charges, laser, radius 30; in the air only a tiered craft's own APS intercepts rounds aimed at it, so the lasers take the
SAMs' and fighters' missiles, and smoke blinds them), `pod_bay` (stops `pods`), `uplink` (carries the big attack). New
kinds `mainengine`, `thruster`, `pdlaser`, `podbay`, `uplink` (words, icons, radio lines for three). Armour (`tiers.armour`):
upper hull 4 at high, belly 2 at low and during the fall (what faces the ground), 3 crashed; engines 1-2 as parts.
Removed from it: `saucer_laser` (renamed), the coilgun, flak and drone mounts, `saucer_emp`, `saucer_drones` (gone from the
data: nothing else used them), `mothership_shield` (kept for the bosses that still use it). `boss_rage` kept.

### C. Drop pods and escorts (D)

- `"pods"`: `count` 2 pods every 14 s (first at 4 s) while it is settled at a tier in `tiers` (orbit, high); each
  carries 1-2 of its `units` in turn (tanks, IFVs, a heavy tank, armoured cars, a BMPT; elites by the side's budget via
  `Economy.ForWave`). A pod is a real vehicle (`drop_pod`: flying, 400 health after the toughness scale, no weapon, no
  card, scripted so no AI orders it, the movement system leaves it alone) at tier low, so every weapon that reaches low
  can target it and the player can order fire on it; it falls 6 s onto a spot 30 m short of the other side's biggest
  group towards the boss (12 m scatter, open ground), under a `pod_drop` warning ring. Landed, it retires (no kill) and
  its vehicles come out; shot down, it falls as any aircraft and they are lost. At most 6 of the pods' vehicles alive
  and on the way at once (`PodLoad`), apart from the escort cap. A real vehicle rather than prompt 18's abstract flyer:
  the player sees their anti-air fire at it and can tap it; the cost is a unit on the list for 6 s.
- Escorts (prompt 16): the table's marks now 0.7 and 0.3 (the phase changes); arrive wave as before plus two
  `fighter_jet` on cover; it comes as the craft leaves orbit (`escortsOnDescend`), not while it is out of reach. The
  phase 2 and phase 3 waves stay (Sen's elite FPV carrier and a jammer; the elite attack helicopter and an engineer,
  the last wave at the crash).

### D. The big attack: tungsten rod rain (F)

`bug_rod_rain` replaces `bug_laser_sweep` on the prompt 18 system with a new shape `rods`: up to `count` 5 rings of 6 m,
one on each of the densest groups of the other side's ground units and towers anywhere (each unit weighing (1 + front
armour)^2: heavy tanks first), no two overlapping much; fewer groups than rods, the rest ring the first spot. 1 600
kinetic, penetration 4 on the roof (a penetrator, not a blast's fragments: `HitKind.Direct` top, so heavy armour takes it
in full), 30 % at the rim; 4 s warning, 60 s cooldown (difficulty scales as prompt 18), first 5 s after it appears, so
the first falls in the opening from the craft itself (`FromSatellite` false) and the rest from the satellite. Every
phase, every tier, and crashed. Smoke does nothing (not energy) and APS never sees it (no round in flight); shield domes
absorb it while their health holds (the dome rule). The uplink carries it: broken during the warning, cancelled; broken
for good, gone (it has no self-repair). Prompt 18's counter groups: the Silver Bug moves from "use smoke" to "get out of
the ring"; **no boss's big attack is stopped by smoke now** (the `sweep` shape stays in the library, used by none), to
weigh later. The Guide's who-for stays "heavily armoured tanks".

### E. Phase 3: the crash and the fortress (E.5, E.6)

- Below 30 %: it falls 6 s on a slope to `crash.at` (the map's centre, the nearest open ground; a mission could set its
  own later), under a `bug_crash` ring, hit as low meanwhile. Down: no longer a flier (`Vehicle.Flying` and `Kind` are
  per unit now: a crashed tiered boss is a ground target for every weapon), its tier None, the `silver_bug_wreck` form,
  mounts 1-4 awake (two 120 mm guns and two twin 35 mm flak all round, the calibre scale's boss guns), a 500 blast (r 16)
  on the other side, its ground closed to routes like a fixed defence's (`AnchorCrash`: the same square, opened when it
  dies) and any unit on it put off (prompt 12's `ClearGround`), and six `crash_debris` props round it: passable, blocking
  direct fire (cover without a stuck risk). Its remaining parts and the rods go on.
- The drone seizure: difficulties `VeryHard` and above (Heroic, Iron: the spec's "Very Hard only" read as not easier than
  it), 10 s after the landing then every 40 s: a 4 s warning (HQ and Aurel on the radio, a toast), then for 6 s the other
  side's drone aircraft and drone launchers (FPV carriers, Lancet trucks, the swarm carrier: whatever fires drones)
  change sides (`SimWorld.Defect`, and back), except those under their own side's jammer or EW tower
  (`Abilities.Jammed`). Drone rounds already in the air are not turned (their owner is fixed).

### F. Campaign and modes (G)

- The words are the campaign sources' (`Tools/campaign/act3.py`, `story.py`), regenerated. The generated
  `CampaignText.cs` had drifted from its sources (the checked-in table has later Vietnamese localisation the sources
  lack): only the 15 keys this prompt changed were taken from the regeneration, with the Vietnamese names the table
  uses (Bọ Bạc, Tầng Mây, Đồi Cát); the rest of the table is untouched. Porting that drift back into the sources is
  left for whoever next regenerates (flagged here). Mission data is unchanged (`campaign.json` identical).
- Boss Rush: a boss's `"arena"` is its battlefield; the Silver Bug's is the Launch Site, switched to and back like the
  sea boss (prompt 16 D.2), the curtain reading "Redeploying to its battlefield".
- Operations: no mutator names the Silver Bug. "Grounded" (no aircraft) leaves the boss's own escort fighters and pods
  (they are its, not bought); with no fighters and no long-range SAMs it is H.4's case.

### G. HUD, Guide, texts (B.5, A.4, E.7)

- Boss bar: an altitude chip (icon, tier, seconds to the next change; none crashed or stuck low) and the phase marks
  with "Phase n/3". Tapping the boss (or a pod): the deck ✓ its main weapon reaches the tier now, ~ only another weapon
  (a tank's roof gun at low), ✕ none, and a line when nothing reaches it. Toasts: leaving orbit, pods, the seizure; the
  crash through the boss-phase cinematic.
- Guide: an "Altitude tiers" section on the boss page (the rule, what reaches each tier, each phase's numbers from the
  data, pods, armour, crash, seizure, how to win without long-range anti-air), the rewritten card and parts tip.
- Every new word is a key (`OrbitalText`, a table hooked like prompt 18's, with the part words in `Strings`); radio lines
  are named in the data (`tiers.radio`: appear, descend, phase2, phase3, crash, down, hijack, hijackWarn): Aurel's keys
  are `radio.aurel.bug.*`, HQ's `radio.hq.bug.hijack`, so prompt 23's one subtitle line is a lookup. No saucer is left
  in data, words or tests.

### H. Balance (first pass, no runs)

Exposure over a phase's cycle (`TierDef.LowShare`, for the combat value meter): phase 1 low 17 of 42 s (40 %, the two
changes count as low), phase 2 27 of 42 s (64 %), phase 3 all; the opening's 15 s nothing. With long-range SAMs, a
Patriot or fighters it can be hit all the time after the opening (their missiles meet its point-defence lasers first:
break those). Paper numbers: the laser as the saucer's; the rods 8 000 over 60 s (`Sustained` 133/s, prompt 13 A).
Health unchanged (7 150, campaign scaling kept). Without high-reach weapons (H.4) the low windows, the pods (400 each)
and the crash (every weapon, belly-to-ground 3) are the way; that case and the 50-65 % first-try win rate on Normal
are for the 5-seed runs.

### Tests

New `OrbitalBossTests` (10): the reach rules per weapon; the opening out of reach, guns held, never back to orbit and the
phase 1 cycle to the second; phase 2's own cycle, the main engine holding it low, thrusters slowing the change; anti-air
and a railgun hit it low and not high while the long-range SAM does (point-defence lasers broken), the belly and hull
armour; five rod rings on five groups, the first from the craft in orbit, 1 600 on a heavy tank's roof, smoke no help,
a dome absorbing part, the next from the satellite; the uplink cancelling and ending the rods, the pod bay stopping the
pods; pods shot down in the air losing their load, never more than six; the crash at its point as a ground fortress
(wreck, guns, cover, the tank under it put off, a tank's gun reaching it, never moving); the seizure only at Very Hard
with the jammer's cover; no saucer in the words and every new key there. Updated: `BigAttackTests` (the entry id; the
zone test reads an attack's own first; the smoke test keeps the railgun half; a rods case), `BossPartsTests` (ten parts;
the body test brings a boss out of orbit first), `MuzzleAuditTests` (the saucer's two known rows gone). One run of the
filter (those and the localisation scan, 17): after two runs stopped at the catalog (a pod needs a positive speed, the
new stops needed listing) and one test fix (the railgun shot the pods' tanks: the test breaks the pod bay), 17/17 passed.

### Left for the testing phase

- The suites (the muzzle audit and model tests will see the new models' muzzles; card and model counts).
- 5 seeds at each difficulty: the big campaign's c9m10 "bug" stage, c7m05 and c9m05, Boss Rush, Operations with the
  Silver Bug; win rate (Normal first try 50-65 % with the standard end-of-campaign deck), fight length inside prompt 5's
  big-campaign frame, the share of time at each tier; the same with no long-range SAM, Patriot or fighter (H.4).
- The stuck check (prompt 12's `StuckWatch`) round the crash site on the Launch Site and on Skyhold and Dunebreak (the
  27 m square it closes at the map centre, the debris ring).
- FPS at Low on a low-end device: the descent from orbit, the rod rain, the crash.
- Screenshots at each tier and phase into docs/ui-screens (not taken, by the token rule).

### For the prompts on hold

Prompt 20: Daedalus, Icarus Mk.0 and Typhon are data (`"tiers"` without `opening` for Icarus Mk.0, without `crash` for
Daedalus, whose phase 3 holds low with a one-step schedule; `"pods"` with `max` 8); Typhon's dive is `Orbit` under another
name or a new tier value the same rules read. "Icarus" is `unit.silver_bug`'s text. Prompt 21's Sandbox: `JumpPhase`,
`ForceTier` (low or high), `TriggerBig`, `SetBigOff`, `Break` are plain `BossSystem` calls the tests use. Prompts 22-23:
every name and line is a key.

### Shared edits (other agents: merge by hand if they conflict)

`balance.json` (the Silver Bug, `drop_pod`, `orbital_laser`, ceilings on five weapons and two fighters, two skills gone,
two supports, the `crash_debris` prop, its escorts, `bug_rod_rain`), `Vehicle` (`Flying`, `Kind`, `ArmourOn`), `Vehicle.Boss`
(`MountWorks`, `InitParts`), `BossSystem` (Joined, Step), `BossSystem.Parts` (two stops, the fingerprint),
`BossSystem.BigAttacks` (the `rods` shape, the off switch), `BigAttackDefs` (`Rods`, `Difficulty`), `BigAttackState`,
`BossDefs` (two mechanisms), `CombatSystem` (reach, the orbit gate, aim height), `DamageSystem` (the APS in the air, the
crash fall height, the last radio line), `MovementSystem` (pods, the fall, the crashed hull), `SimWorld` (`AnchorCrash`,
`AddCover`), `SimEvent` (`TierChanged`), `Catalog`/`Catalog.Extra`/`Definitions` (hooks, `TryGetProp`, `Tuned`), `SiegeModes`
(Boss Rush arena), `MatchRunner`, `ModeSessions`, `BattleHud`, `MissionBar`, `KitCombat`, `BossPartsRow`,
`MenuScreen.BossParts`, `VehicleView`, `EffectsDirector.BigAttacks`, `LaserBeams`, `EffectShots`, `Strings`, `GuideText`,
`BigAttackText`, `CampaignText` (15 keys), `Tools/campaign/act3.py`, `story.py`, `Tools/blender/build_assets.py`.

## 18D. Design document: armour levels, penetration, weapon forms, and fixes (2026-09-29)

The owner's doc update (Docs/prompts/doc-review-update_vi.txt). Everything is generated from the export and the data; nothing is edited in the PDF.

- **Armour:** vehicle, tower and elite cards show the level on each face with its name (0 Không giáp, 1 Mỏng, 2 Vừa, 3 Dày, 4 Rất dày), one level when all faces match, and "công trình" on structures. Boss part tables have a column with each part's level, plus a line with the hull's faces. Sections 9 and 9b have a front-armour column.
- **Weapons:** every weapon table has columns for penetration and for form with tags (top attack, guided, splash, Thermobaric). The "Đạn và nạp đạn" lines add both. Each card has the main weapon's effect row against armour 0-4, air and structures, with the game's own ✓ ~ ✕ thresholds (`Matchup.GoodAt` 0.6, `PoorAt` 0.12), and the Strong-against / Weak-to lines.
- **Icons:** the combat icons are drawn in code (`CombatIcons`), with no image per icon. Section 10 therefore shows the game's icon legend sheet (`kit-combat-icons.png`) instead of an icon in every cell. Exporting each icon as a PNG would allow icons in the cells later.
- **Counters:** section 10 gives the defences table (reactive armour, reactive blocks, cage, APS, flares, smoke, jammer, shields). It is written from DECISIONS 14A C.9, which `ArmourTests.CountersFollowTheTable` holds the code to.
- **Fixes:**
  - 9b reads the newest `combat_value_*_summary.tsv`, keeps only cards still in the roster, and takes names and CP from the current data (it listed merged cards and the old car-bomb cost).
  - Boss Rush's subtitle has its count filled in the export, and the Boss Rush list comes from `BossRushRules.Kinds`.
  - Section 11 names the HQ instead of the bastion.
  - Sections 1 and 15 count the long maps.
  - Section 2's difficulty paragraph now reads the four-level table from DECISIONS 13C.
  - The campaign line reads its mission and chapter counts from the data.
- **Tests:** `ExportGameDoc.EveryUnitHasArmourLevelsAndEveryWeaponAPenetrationAndAForm` and `ExportGameDoc.NoModeLineKeepsAPlaceholder` (both languages).

## 19A. Prompt 20 pass 1: twelve chapters, four acts, names, act switches, economy (2026-09-29)

Parts A-D of prompt 20 on lead/integration cd87984 (branch feature/p20-pass1). Parts E-M (boss templates, the new
bosses and mini bosses, the two new maps, the towers) are pass 2; N-P (Boss Rush for 12 chapters, the chapter screen,
the full check) are pass 3. The owner's token rule: one targeted test run, no suites, no screenshots.

### A. Names (display only; every id kept)

Bosses read "Proper name · subtitle" in `unit.*` and `boss.*`; `short.*` is the proper name. Existing ids:
fortress_bastion Bastion · Pháo đài; behemoth Behemoth · Quái vật thép; mobile_fortress Jötunn · Pháo đài di động;
leviathan Leviathan · Tuần dương hạm; drone_mothership Matriarch · Tàu mẹ drone; nuke_train Nemesis · Đoàn tàu tên lửa;
command_airship Roc · Khí cầu chỉ huy; silver_bug Icarus · Phi thuyền quỹ đạo; behemoth_inferno Inferno · Behemoth phun
lửa; mega_gunship Harpy · Trực thăng khổng lồ; sky_fortress Spectre · Máy bay pháo; rail_supergun Gungnir · Pháo đường
ray; behemoth_tempest Tempest · Behemoth pháo điện từ; armored_train Juggernaut · Đoàn tàu bọc thép; landing_hovercraft
Charybdis · Tàu đệm khí đổ bộ; fortress_hive Hive · Pháo đài drone; supreme_command Atlas · Xe chỉ huy siêu nặng;
earth_borer Tartarus · Máy khoan. The old c3m08 "frozen Behemoth" is Behemoth Mk.II (prompt's "Quái vật băng giá"); the
old "Frost Monster" of c6m10 is Moloch's slot now. Generals: `char.<id>.name` and `.role` (call sign and boss theme):
Brandt (fortresses, new, portrait drawn by `portraits.py --only brandt`), Viktor Varga "Anvil" (giant monsters), Ilya
Orlov "Winter" (Norse winter), Magnus Kessler "Maelstrom" (sea monsters), Elara Sen "Queen" (insects, swarms), Kasimir
Wolff "Raven" (mythic birds; `quaden` id), Lucien Aurel "Sol" (Greek sky), Lý Hàn "Titan" (the Titans; `hung` id);
Diều Hâu "Hawk", Khải "Iron". "Silver Bug", "Bọ Bạc" and "S.B." became Icarus / Dự án Icarus.

How: one script over every table (`Strings`, `CampaignText`, `GuideText`, `UnitText`, `BigAttackText`, `OrbitalText`):
exact values for the name keys, then ordered substring swaps. "Quạ Đen" became "Wolff" except in our side's radio keys
(`radio.khai/linh/dieuhau/mai/hq/sen.*`) and the two dossier bios that say our side calls him that. The Tools/campaign
sources got the same swaps. The siege mode's "super-gun" is another thing and kept its name. Scan:
`Prompt20CampaignTests.NoTextUsesAnOldBossOrGeneralName` (the old names, the allowed places, the format of every boss
slot). Left for pass 3 (P): the design documents' boss chapters (`Docs/ASSET_DEBT.md`, `Docs/PROGRESS.md` are logs); the
exported PDF reads the tables and is current.

### B. Twelve chapters, four acts

| Act | Chapter | General | Mini bosses · main boss (slot ids) |
|---|---|---|---|
| I Đổ bộ | 1 Bờ biển lửa | Brandt | bastion_mk0 · fortress_bastion |
| | 2 Vàng đen | Varga | behemoth_inferno (c2m05) · behemoth (c2m10) |
| | 3 Mùa đông dài | Orlov | mega_gunship, fenrir (side c3s2) · mobile_fortress |
| II Phản công | 4 Cảng thép | Kessler | behemoth_tempest, armored_train, scylla (c4m06) · leviathan (c4m11) |
| | 5 Lửa rừng | Sen | locust (c5m08), fortress_hive · drone_mothership |
| | 6 Tổng phản công | Varga | landing_hovercraft (c6m08), behemoth_mk2 (c6m05) · moloch (c6m10) |
| III Phản bội | 7 Thủ đô | Aurel, Lý Hàn turns | supreme_command (c7m10's last stage, fleeing) · nuke_train (c7m05) |
| | 8 Lòng đất (new) | Lý Hàn | ixion (c8m07), earth_borer (c8m05) · kronos (c8m10) |
| | 9 Biển động (new) | Lý Hàn | caspian (c9m05), scylla (c9m08) · typhon (c9m10) |
| IV Bầu trời bạc | 10 Chiến tranh trên không | Wolff | sky_fortress (c10m08), icarus_mk0 (c10m05), argus (side c10s2) · command_airship |
| | 11 Cửa ngõ quỹ đạo (new) | Aurel; Orlov's last | rail_supergun (c11m05), locust (c11m07) · daedalus (c11m10) |
| | 12 Bãi phóng | Aurel | behemoth_mk2 (c12m10 stage), behemoth_tempest (c12m02), locust (c12m05) · silver_bug |

- Data: `campaign.json` chapters carry `"main"` and `"minis"`; a mission or stage fights a slot by its id with
  `"fallback"` (the existing `ScriptedUnitDef.Fallback`: until the def exists the stand-in is spawned, at
  `fallbackHealth`), so pass 2 only adds the def with that id. The builder fails a chapter whose slots are not fought.
- **Stand-ins for pass 2** (slot: stand-in, where): bastion_mk0: fortress_bastion x0.55 (c1m05); fenrir: behemoth x1.2
  (c3s2); scylla: leviathan x0.5 / x0.6 (c4m06, c9m08); locust: drone_mothership x0.4-0.7 (c5m08, c11m07, c12m05);
  behemoth_mk2: behemoth (c6m05 x2.2, c12m10 x1.6); moloch: mobile_fortress x1.8 (c6m10); ixion: behemoth x1.1 (c8m07);
  kronos: mobile_fortress x1.3 (c8m10); caspian: landing_hovercraft (c9m05); typhon: behemoth_tempest x1.8 (c9m10,
  chosen because it works on Ironport's ground; pass 2 builds the sea stage); argus: command_airship x0.45 (c10s2);
  icarus_mk0: silver_bug x4.4 (c10m05, flees at half); daedalus: silver_bug x2.0 (c11m10). Harpy, Spectre, Gungnir,
  Tartarus, Charybdis, Atlas, Juggernaut, Tempest, Inferno, Hive keep their defs. Pass 2 also: Locust as Icarus's escort
  (the escort tables are `balance.json`'s), Gungnir's `general`/radio (balance.json says Kessler; the mission says Orlov).
- **Deviations from "the tenth mission has the main boss", decided here:** chapter 4's Leviathan stays the epilogue
  after the operation (prompt 16: it needs the sea map, and reversed maps drop the sea); chapter 7's Nemesis stays the
  fifth mission (it needs the metro rails; the capital operation has no boss stage yet). Pass 2 can fold both in.
- **Moves** (old id -> new; texts, radio keys and saves follow the same table, `story.MOVES`): c7* -> c10*, c8* -> c7*,
  c9* -> c12*; c1m05 (hovercraft) -> c6m08, c6m08 (Earth Worm) -> c8m05, c4m06 (rail supergun) -> c11m05, c3m08
  (frozen Behemoth) -> c6m05, c3s2 -> c3m08 (a main mission now), c6m05 (Spectre) -> c10m08, c7m08 -> c11m08. The ids were
  renamed once in the sources and the table (a one-shot script, not kept: running it twice would move them again).
- **New missions:** c1m05, c3s2, c4m06 and all of chapters 8, 9 and 11 but their moved missions (36). Each is an existing
  mission of the same battlefield written again (`act4.clone`), so its positions, props and roads stay right; it differs
  from every mission on that map in at least two of direction, base, weather, area and goal (prompt 4's rule, the
  builder checks). Only Capture, Hold, Survive, Duel, Hunt, Recon, ShootDown and Relieve copies are flipped: a reversed
  map swaps the camps but not the props or the sea, so Destroy, Protect, Escort, Intercept and Boss copies keep their
  side and differ by weather and base (a few use `playerBase: "Defend"`). Pace: each new chapter's CP and income between
  its neighbours'.
- **Maps for part M:** chapter 8 stands on redrock, dunebreak and hydrodam; c8m02, c8m07 and c8m10 move to openpit.
  Chapter 11 stands on rustyard, frostpeak and skyhold; c11m04, c11m07 and c11m10 move to orbitalgate.
- **Story (short, in the tables for prompt 22):** chapter cards and timeline for 7-12 and 4 (Tempest is one of Varga's
  Behemoths waiting for Kessler's ship), act III "Phản bội"/act IV "Bầu trời bạc", Lý Hàn escapes at the end of 7 and is
  taken at the end of 9 (papers name Project Icarus), Wolff falls in 10, Orlov's last battle is Gungnir (c11m05), Varga's
  and Kessler's are in 12 (c12m03/c12m10, c12m02), Locust is Sen's programme kept by Aurel, chapter 12's end is the game's.
  The old c12m04 and c12m06 duels (Orlov, Wolff) are Aurel's now. Lý Hàn is a general (`hung`: his deck, Aurel's base
  style, taunts).
- **Texts:** `build_campaign.py` no longer rewrites `CampaignText.cs`: a key already there keeps its hand-localised words
  unless the sources mark it fresh (`retext`, `fresh=True`); new keys come from the sources (18A's drift stays, now safe).

### B.3 Save migration

`PlayerProfile.MigrateCampaign`, `CampaignVersion` 2 -> 3. A version-2 save moves every mission's stars and best tier to
its new id at once (campaign.json `"migration.moves"`), the chapter cards seen follow (7->10, 8->7, 9->12, the old
epilogue mark 10 -> 100) and the HQ level its old HQ missions opened is kept (`hqKept`, read by `HqLevelCap`: level 3 of
the old c5m05 now sits in chapter 6). A version 0/1 save (23 missions) goes straight to the new ids by `legacy`. Cards
won are kept by id. The epilogue mark is 100 and "To be continued" 100 + chapter, off the chapter numbers.

### C. Act switches

- `Resources/Data/release.json` (`CampaignRelease`): `"acts"`, `"chaptersOff"`, `"switchedOff": "comingSoon" | "hidden"`.
  The game has no remote config: a future one sets `Campaign.Release`; `-mb-acts=1,2` switches acts for a play test.
  Internal and test builds: all four acts.
- `Campaign.All` is the chapters switched on (a fresh copy when some are off); `Campaign.Everything` every mission
  (migration, records); `Campaign.Get` still finds a mission switched off. So Operations, its weekly rotation and the
  extra-boss mutator drop what is off. Boss Rush draws from `BossEnabled` bosses (fought in a chapter on, or in none):
  acts I-II leave six kinds; with everything on it draws exactly as before.
- The chapter screen shows a chapter off as a locked "Sắp ra mắt" card or hides it; the last chapter on ends with
  "Còn tiếp" (card and dossier) instead of the epilogue; the Legend tier opens after the last operation on.
- **Unlock sources when chapters are off:** everything a chapter off unlocks (cards, towers, modules, the tower branch)
  and its HQ level go to the operation of the nearest chapter on before it (else after it). Acts I-II: chapter 6's
  operation (c6m10) also gives the 24 cards of chapters 7-12 (vbied, turtle_tank, bmpt, smoke_carrier, shahed_truck,
  counter_battery_radar, thermobaric_launcher, bunker_vehicle, wingman_drone, remote_mines, iron_beam,
  artillery_emplacement, sead_strike, heavy_rocket_artillery, ew_jammer, gunship_heli, railgun_truck, stealth_fighter,
  cp_relay, heavy_turret, cruise_missile, shield_tower, swarm_carrier, mine_layer) and HQ levels 4-5. Acts I-III:
  chapter 9's operation (c9m10) gives chapters 10-12's 12 cards and HQ level 5. `HqLevelMission` finds the mission that
  opens a level or more.
- A save keeps the stars of missions switched off; switched back on, the campaign goes on from the first mission not won.

### D. Unlock route and economy

- Cards a chapter: 6, 6, 6, 5, 6, 6, 4, 4, 4, 4, 4, 4 (59; the builder's rule is now 4-7); the five modules stay in
  acts I-II. Moved from the old route: artillery_emplacement, wingman_drone, iron_beam, remote_mines -> 9;
  thermobaric_launcher, bunker_vehicle, shahed_truck, counter_battery_radar -> 8; railgun_truck, stealth_fighter,
  cp_relay, heavy_turret -> 11. HQ levels: c1m04, c3m05, c6m04, c9m05, c11m04 (`act4.UNLOCKS`, `HQ_LEVELS`).
- Pay (`build_campaign.tune`, prompt 7's model): coin scale 100, blueprint scale 1.75; the campaign-only deck (8 cards and
  6 towers) is rank 7.14 as act IV begins and 8.14 at the end (per chapter: 3.4, 4.4, 5.1, 5.6, 6.1, 6.3, 7.0, 7.1, 7.1,
  7.4, 8.0, 8.1). Acts I-II only: every mission pays x1.42 (`"economy.payScale"`), the deck ends at 7.0; acts I-III: x1.00
  (7.14). A shorter release never pays less. `Campaign.ExpectedRank` (the recommended power) climbs to 7 by act IV.
- Unit stats and mode difficulty untouched (the balance agent's).

### Tests

`Prompt20CampaignTests` (7): the name scan, the twelve chapters and their slots, the nine-chapter save's migration, the
act switches in three configurations (all four acts, I-II, I-III: missions, unlock sources, HQ levels, Operations, the
weekly draw, Boss Rush, pay, hidden/"Coming soon"), and a save going on when an act comes back. One run: 6 of 7 passed
(`boss.landing_hovercraft` had no name); the name was added and that case passed on a rerun. `CampaignTests`' shape test
now asks for 12 chapters (not run).

### Left for the testing phase

- 5-seed campaign runs of all 12 chapters at Normal (every new mission winnable with the deck open by then; the new
  chapters' pace; the stand-ins' fight lengths); Boss Rush and Operations with acts I-II.
- `CampaignTests` (its sweeps and the new shape), `LocalisationScanTests`, `RadioDirectorTests`, PlaySmoke (its default
  step is `Campaign=c11m05`, the rail supergun's mission).
- Stuck checks for bosses on their new routes: Bastion Mk.0 on Greenvale, Fenrir on Frostpeak, Scylla on Lighthouse Bay
  with no camp, Atlas leaving the capital, Ixion/Kronos on Dunebreak.

### Shared edits (other agents: merge by hand if they conflict)

`Tools/campaign/*` and `campaign.json`, `CampaignText.cs`, `Strings.cs` (boss and general names), `BigAttackText.cs`,
`OrbitalText.cs`, `CampaignDefs.cs`, `Progression.cs` (`Campaign`), `PlayerProfile.cs`, `SiegeModes.cs`
(`BossRushRules.Roster/KindsWhere`), `ModeSessions.cs` (one line), `MatchRunner.cs` (one line), `MenuScreen.Campaign/Story/
Home/Operations.cs`, `PlaySmoke.cs`, `CampaignTests.cs`. `balance.json` is untouched.

## 19B. Balance pass after prompt 18: towers, vehicles, supports, modes (2026-09-29)

The owner's pass (Docs/prompts/balance-after-p18_vi.txt, A-E), on lead 319a285. Damage a round stays on prompt 13's calibre
scale and prompt 15's penetration (14A): strength was moved with rhythm, magazines, loads, health, reach and price, plus two
damage-table cells. Every number below is from `Docs/balance/*p18_before*` / `*p18_after*`; the before/after tables for every
vehicle and tower are `Docs/balance/tables_p18.md` (`python Tools/balance/p18_tables.py`). The owner asked for the long runs,
so they ran in full (four extra worktrees with copied Libraries, several Unity instances at once).

**Not merged: lead's prompt 20 L-M towers.** The coordinator asked for lead/integration (with the C-RAM's Iron Dome branch, the
rocket battery in AI yards and the 60 m SAM post) to be merged into this branch; the merge was refused by the permission
system, so this branch stays on 319a285. The C-RAM, the rocket battery and the AA tower's branches keep their behaviour and
are measured and listed below with what they need; their numbers were not tuned (the AA tower's own flak and the Patriot
were: they are not the other agent's work).

### 1. Baselines (the section-17 measurements)

- **Campaign, 5 seeds, all 109 missions** (`CampaignTests.WinRateOverFiveSeeds`): 518/545 battles won (95 %), 97 missions won on
  every seed. Short of it: c8m08 0/5, c8m06 1/5, c7m08 2/5, c4m09, c4s2, c5m06, c5m08, c5m09 3/5, c8m10 3/5 (two seeds end
  at the 34-minute cap), c2m09, c4m11, c9m09 4/5 (`campaign_5seeds_p18_before.tsv`).
- **Stuck detector** (`StuckBatch.Modes`, 21 battlefields x Siege, Defend, Endless, Weekly x seeds 1-5, the three loadouts,
  safety net on; 420 battles, 52 min): 2,396 episodes over 10 s, 43 over 20 s, worst 277 s (`stuck_p18_before.txt`). The causes
  are prompt 12's: queues behind friends (1,176) and yielding (340); nothing new is stuck for good in Siege (worst 54 s) or
  Defend (20 s). The long ones are Endless and Weekly with the "obstacles" loadout: `StuckBatch.Loadout` also fills the
  *attacker's* camp hardpoints with dragon's teeth, and vehicles at the camp spawn (the same spot, 109,125, on every siege map)
  find no path (NoPath 37). That is the test's configuration, not play (a Weekly attacker has no base loadout); left, and noted
  for the StuckBatch owner.
- **Tick budget** (`TickBudgetTests`, 24-80 enemies): mean 0.57-1.33 ms desktop (x6 phone: 3.4-8.0 ms, inside 8 ms up to 80),
  p99 3.4-4.7 ms at every size (x6: 21-28 ms, over 16 ms). The p99 does not grow with the enemy count; it is the machine: four
  to five Unity instances ran the sweeps at the same time. Re-measure on a quiet machine (13B had p99 1.9-3.2).
- **Modes, 5 seeds x 2-3 battlefields, Normal** (`ModeBalanceMeasure`, sample deck, the player's auto commander):
  Siege 13/15; Defend won 15/15 with the outer line lost in all 15 (3.2-5.3 min); Weekly 6/15 (2/5 from each of stages 1, 2
  and 3); Deathmatch 4/15; Endless median 15.8 min; Survival 13.9; Boss Rush 0/10, every run at the 30-minute cap.
  **Ladder** (Conquest, Deathmatch, Hill, Assault, 60 battles a level): Easy 92 %, Normal 33 %, Hard 22 %, Very Hard 15 %.
- **Towers**: DPS as in the spec (A.2). Tower pick rate (`TowerPickRates`): aa 17 %, guard 15 %, mg 10 %, heavy fortress 5 %,
  Patriot 4 %, rocket 4 %, C-RAM 5 %, ATGM 1 %, gun 1 %, artillery 0 %, drone hangar 0 %.

### 2. New measurements (tests, `MB_BALANCE=1`)

- `TowerValueMeasure.MeasureTheTowers`: a tower (or one vehicle) alone holding a point against a ladder of attackers of rising CP
  (light vehicles, tanks, aircraft), three seeds a rung; its worth is the CP it holds against evenly, and the vehicles' median
  worth per CP turns that into "the CP of a vehicle doing the same" (A.1's bands). The combat-value measure's own scenarios are
  attacks, where a tower cannot take part. `PrintCRamInterception`: rockets stopped of two launchers' salvos.
- `BalancePassMeasure`: the wheeled gun's flank share (B.1), the HQ alone against aircraft (A.3), fire supports' damage per CP
  on a row of light vehicles, a column, tanks and a fort (C.1).
- `CombatValueMeasure`: an `arty` scenario (a howitzer, an MLRS and a rocket technical standing: the artillery hunters' fight,
  not in the ground mean), an `OnHit` hook, and per-mount theoretical DPS (`theoretical_mounts_*.tsv`).
- `TowerPickRates` also reports each slot size's shares (a medium tower competes in medium and large slots only).

### 3. Towers (A)

Tower weapons of their own where a vehicle shares the weapon (the rounds stay the calibre's): `tower_hmg`, `tower_agl`,
`tower_ac25`, `tower_flak_30`, `tower_kornet`, `howitzer_fixed`, `gun_155_twin_fort`, `patriot`. Theoretical DPS light /
heavy / air, before -> after (target):

| Tower | Before | After | Target | How |
|---|---|---|---|---|
| Guard tower | 44 / 10 / 14 | 78 / 19 / 25 | 80 / 15 / 25 | HMG 0.133 -> 0.085 s, magazine 40; grenades 10 -> 4.3 s |
| MG bunker | 73 / 19 / 26 | 98 / 28 / 33 | 100 / 25 / 30 | NSV 0.08 -> 0.062 s; Konkurs 24 -> 12 s |
| · twin | 87 / 22 / 32 | 115 / 32 / 40 | 120 / 28 / 35 | 0.064 -> 0.05 s |
| · flame | 117 / 23 / 0 | 150 / 30 / 0 | 150 / 30 / 0 | 0.25 -> 0.195 s |
| AA tower | 117 / 47 / 403 | 46 / 15 / 296 | 45 / 15 / 280 | own 30 mm flak, fuzed for aircraft: x0.48 / x0.40 on the ground, 0.09 s |
| Gun turret | 50 / 35 | 71 / 85 | 70 / 85 | 120 mm 7.2 -> 2.88 s (a fixed gun with its crew), x0.65 on light (APFSDS through a thin hull) |
| · long / auto | 46 / 31, 55 / 40 | 64 / 75, 79 / 97 | range for DPS, 80 / 95 | 3.31 s, 2.53 s |
| ATGM tower | 44 / 44 | 37 / 93 | 40 / 100 | Kornet pairs 9.9 -> 4.35 s, x0.4 on light |
| · top attack | 44 / 44 | 40 / 100 | best on thick armour | 4.0 s, roof hits |
| Artillery emplacement | 42 / 27 | 87 / 72 | 90 / 60 | the 155 mm at 3.9 s, 13 s reload (the field piece: 11 s, 36 s); reach and minimum range kept |
| Heavy fortress | 89 / 56 | 132 / 89 | 130 / 140 | twin 155 mm 8.8 -> 5.5 s |
| Patriot | 111 air | 203 air | 260 | 10.1 -> 4.24 s; PAC-3 7.5 -> 3.52 s (245, target 320); long-range radar inherits it (203 with 100 m) |
| Drone hangar | 13 / 13 | 59 / 59 | 60 / 70 | 4 drones every 6.5 s (was 2 every 20); Lancet 3.6 s (67), swarm 5.5 s (77) |

Worth in vehicle CP after (main role; `tower_value_p18_after.tsv`; before in brackets): guard 5.5 light (4.1), MG bunker 13.5
light (13.7), AA tower 5.4 air (4.9) and 7.2 / 5.4 on the ground (13.2 / 11.8), gun turret 15.3 tanks (11.8), ATGM tower 7.9
tanks (7.6), artillery emplacement 10.5 / 11.3 (5.2 / 6.1), heavy fortress 13.5 / 23.0 (14 / 25), Patriot 19.2 air (14.3),
drone hangar 6.9 tanks (6.0; Lancet branch 10.9). Read with care: a tower the attackers cannot hurt holds the whole ladder
(the MG bunker's front armour 3 against 25 mm cars, the fortress against the ladder's tanks), so those are "at least".
Choices where the spec's DPS and its CP bands disagree: the DPS targets were met (they are the owner's starting numbers);
the heavy fortress's heavy DPS stays under 140 because its gun is high explosive (HE on armour 3-4 does a third), and it
already holds more than its band. Large beats small in the same role: Patriot 19.2 air against the AA tower's 5.4; the
fortress and the MG bunker both hold the whole light ladder.

- **A.3 HQ:** its twin flak 0.054 -> 0.11 s (and the fragmentation cell, B.3): 880 -> 416 air DPS. Alone at level 5 it held
  5 minutes against four aircraft (53 CP, 27 % left; before 30 %) and fell to eight in every seed, before and after: it holds by
  its 9,000 health, not its guns. No base is safe from aircraft by its HQ alone.
- **Not tuned (the other agent's towers):** the C-RAM stops 20 % of an MLRS's rockets (Centurion 30 %, Hunter 10 %; 14-18 % of
  heavy rockets), far from "most of a medium salvo": the Iron Dome branch on lead is the answer to measure after the merge.
  The rocket battery is 58 / 43 against 110 / 45: its salvo about twice as often, and its structure factor, once merged. The
  AA tower's branches: flak 56 / 11 / 164 air (the lead's flak does 22 a round, more), SAM post 36 / 7 / 127 air (lead: 60 m).
- **A.4 pick rates** (after): in their own slot size (`tower_picks_p18_after.txt`): small AA tower 20 %, MG bunker 19 %, guard tower 21 %; medium gun turret 18 %, C-RAM 9 %, ATGM tower 8 %, rocket battery 4 %; large heavy fortress 32 %, Patriot 22 %, drone hangar 11 %, artillery emplacement 1 % (16 % in the mid-pass run on pass-3 data: the greedy pick scores each candidate over 2 seeds and is noisy). Under 10 %: the artillery emplacement, the ATGM tower, the C-RAM and the rocket battery (the last two wait for the merge). The mixed-base check (`AMixedBaseIsBest...`) was not re-run.
- Non-firing towers (EW, dragon's teeth, minefield, CP relay, shield generator, modules): measured in the pick run (EW
  EW 13 % of the small slots, dragon's teeth 11 %, minefield 6 % small, 28 % medium, 21 % large, CP relay 11 %, shield 0-2 %: a candidate for a look); none useless or forced; unchanged.

### 4. Vehicles (B)

| Vehicle | Change | Ground value per CP (air for anti-air), before -> after |
|---|---|---|
| Iron Beam | 9 -> 7 CP; beam 0.1 -> 0.0525 s (air 105 -> 200 DPS); APS beat 1.2 -> 0.8 s | air 20 -> 87; point defence 15.7 -> 17.0 interceptions (6,315 -> 4,332 HP saved: the attacking group's Lancets are stronger now; 619 a CP at 7 CP) |
| SAM launcher | own Buk rhythm 5.73 -> 2.9 s (air 169 -> 259), 460 -> 800 HP, 5 CP kept | air 337 -> 423 |
| Wheeled gun | 3.3 -> 2.75 s (+20 %), 620 -> 870 HP | 296 -> 466 (tank hunters' median 439) |
| IFV | its own 2A42 at +40 % rhythm (0.2 -> 0.143 s), 6 CP | 113 -> 138 (1.38 times the armoured car per CP) |
| Twin tank | 7 -> 5.5 s a pair | heavy DPS 77 -> 96 (target 95), real DPS on tanks 61 -> 73 (heavy tank 59) |
| Lancet | reach 85 -> 100 m (outranges the howitzer it hunts), 6 -> 8 drones a load, 12 -> 9 s | 282 -> 331; artillery fight 100 -> 126 |
| Thermobaric launcher | reach 38 -> 48 m; 7 -> 8 CP | fort 141 -> 745 (siege tank 820, heavy bomber 971) |
| Strike drone | 4 -> 3 Hellfires a load, 7 -> 8 CP, 260 -> 480 HP | 336 -> 340 |
| Attack jet | 4 -> 3 FAB-250 a load, 15 -> 16 CP, 700 -> 850 HP | 443 -> 418; fort 526 per CP against the siege tank's 820 |
| Rocket technical | x0.6 on structures | fort 458 -> 322 |
| Flame tank | 4 -> 5 CP | 282 -> 236 |
| Car bomb | 2 -> 3 CP | 82 -> 68 |
| Titan | 14 -> 16 CP (+35 % over the heavy class) | 524 -> 472 |
| Scout helicopter, gunship, recon drone | 300 -> 420, 1100 -> 1400, 220 -> 320 HP (B.3) | 255 -> 315, 304 -> 360, 55 -> 62 |

- **Found (B.1):** the wheeled gun's flank bonus does fire: 49 % of its hits on the light group land on a side or the rear,
  9-26 % on tanks (`flank_share_p18_*.txt`). The thermobaric launcher's low fort value was its 38 m reach: artillery keeps
  4 m outside a defence's reach, and against the 32-36 m fort guns it found no spot (4 % of its time on target).
- **B.3 aircraft against anti-air:** fragmentation on aircraft 1.5 -> 1.3 (the damage table), tougher aircraft (above).
  With AA / without, per CP: gunship 0.13 -> 0.33, heavy bomber 0.34 -> 0.36, stealth bomber 0.47 -> 0.56, swarm carrier 0.48
  -> 0.56 (in 30-40 % or over); scout helicopter 0.14 -> 0.23, attack jet 0.07 -> 0.13, strike drone 0.05 -> 0.09 (under).
  Tried and dropped: 1.1 on aircraft with a 1,250-HP attack jet (its ratio 0.22-0.3), which broke `CounterTests` "SAM beats
  jets" at every setting of the launcher; the counter test wins. `CounterTests` all pass, "Attack jets beat heavy tanks" too
  (it failed on lead).
- **B.4, class spread of ground value per CP (median, range):** light 119 (±16 %), tank hunters 439 (-25 / +6 %), heavy 388
  (-39 / +24 %), artillery 385 (-57 / +16 %), helicopters 322 (-2 / +12 %), aircraft 343. Outside ±15 % on purpose: the light
  tank (3 CP, a scout's tank), the flame tank (an anti-light specialist, 700+ against the light group), the rocket technical
  (cut on structures by B.2), the Titan (+24 % at 16 CP), the siege tank (a fort breaker), the Lancet (-25 %: an artillery
  hunter), the anti-air class (judged in the air; the Iron Beam by what it saves).

### 5. Supports (C)

- **C.1 Airstrike:** 6 x 350 -> 6 x 400 (the 500 kg class), radius 4 -> 6 m; its damage per CP rose 391 -> 412, the best
  support, so 8 -> 9 CP: 366 per CP, between the remote mines (350) and the barrage (368); napalm 283, cruise missile 181.
- **C.3 Texts from data:** `SupportLines` fills named placeholders (`{{count}}`, `{{length}}`, `{{rankCount}}`, `{{radius}}`,
  `{{width}}`, `{{blast}}`, `{{duration}}`, `{{delay}}`, `{{cp}}`, `{{damage}}`, `{{percent}}`, `{{units}}`, `{{unitRank}}`...)
  from the support's data in `Strings.Get`. Every support guide and info line with a number uses them (the air raid said
  fourteen bombs for 10, the cluster strike forty bomblets for 30, the barrage twelve shells for 8, the airstrike eight for 6).
  `SupportTextTests`: placeholders filled in both languages and the same in each; every number still written by hand, in
  digits or words ("fourteen", "bốn mươi"), before a count, a distance, a time, CP or a share, must be one of the support's
  own (a drop's count of each vehicle too); the scanner test reads the old wrong texts.
- **C.4 Raw keys:** `Strings.Support` names an escort drop "Escort drop: <unit>" / "Thả hộ tống: <unit>"; names and infos for
  `supergun_shell`, `leviathan_shell`, `leviathan_cruise_mark` and `air_raid`. `SupportTextTests.NoSupportShowsARawKey`.

### 6. Modes and difficulty (D)

- **Found (D.4):** at Normal the result followed the seed across every mode and battlefield (seed 1 won 11 of 12 battles,
  seed 3 none): the enemy's deck, drawn with the seed, took "any card that fits the role". Normal's deck now prefers the
  role's typical cards (noise 1 -> 0.5, minus |value - 1| x 1.2); the swing moved rather than went (seed 1 then lost 11 of
  12), so the deck is one cause and the chaotic sim the other. Deathmatch at Normal: 4/15 before, 0/15 after (Easy 15/15, Hard 7/15, Very Hard 7/15): Normal's enemy holds its ground by its towers, now twice as strong, and the CP score counts what the attacker loses; not fixed (it needs the mode's scoring or Normal's stance looked at).
- **D.5:** Hard's win rate (48 %) sat above Normal's (28-33 %): Normal's enemy income 1 -> 0.7 (0.85 gave 37 %). Hard and Very Hard buy by the
  `value` data, which is still prompt 13's F3 measurement (long-range SAM, fighter and car bomb at 1.5); a follow-up should
  refresh it from `combat_value_p18_after_summary.tsv` and measure the ladder again.
- **D.1 Siege:** garrison 16 -> 20 CP (Hard 22 -> 24), towers 1.75 -> 2.1 as tough, rings 1.05 / 1.15 / 1.25 as hard-hitting,
  Normal mans every hardpoint. **D.2 Defend:** the outer line 1.45 -> 2.0 as tough and 1.15 -> 1.3 as hard-hitting, the first
  wave 4 -> 3 (Easy 2, Hard 4) and growth 1.7 -> 1.8 (Hard 2.0); the inner lines as they were. **D.3 Weekly:** no bug: it was
  won from stages 1, 2 and 3 (2 of 5 each) at Normal before any change.
- **After (5 seeds):** | | Before | After | Target |
|---|---|---|---|
| Ladder Easy / Normal / Hard / Very Hard | 92 / 33 / 22 / 15 % | 93 / 53 / 48 / 25 % | 90 / 70 / 50 / 30 % |
| Normal: Conquest, Deathmatch, Hill, Assault | 3, 4, 7, 6 of 15 | 8, 0, 9, 15 of 15 | |
| Siege (Normal) | 13/15, median 8.1 min | 10/15 (67 %), 8.6 min | 60-75 % |
| Defend: outer line lost / HQ held | 15/15 / 15/15 | 15/15 / 15/15 | 50-70 % / ~4 in 5 |
| Weekly from stages 1-3 | 6/15 | 6/15 (8/15 at x0.85) | winnable at Normal |
| Endless / Survival median | 15.8 / 13.9 min | 15.6 / 9.2 min | |
| Boss Rush | 0/10, 30-min cap | 0/10, 30-min cap | 15-25 min |

The files: `modes_p18_before_*.txt`, `modes_p18_after_*.txt` (Normal re-measured at x0.7; `_x085` the full run at x0.85).
Defend's outer line still falls in every battle (2.2-6.7 min): its towers' health is not what breaks it (the line's objective
goes first); left for a look at the line's objective.

### 7. Campaign after (5 seeds)

513 of 545 battles won (94 %; 518, 95 % before), 92 missions won on every seed (97). Worse: c8m10, the last operation,
0/5, every seed at the 34-minute cap with the last stage (Hunt) at 100 % progress but not ended (3/5 before, where the other
two already stalled the same way): not diagnosed; the stronger enemy towers are the likely cause. c8m08 0/5 as before,
c8m06 1/5, c5m08 2/5, c2m09 and c4m06 3/5 (`campaign_5seeds_p18_after.tsv`).

### Tests

Run: `CounterTests` (all 13 pass), `RosterRoleTests`, `Prompt17RosterTests`, `TowerRosterTests`, `CalibreTests`,
`BlastSizeTests`, `UnitLinesTests`, `LocalisationScanTests`, `SupportTextTests`, `Prompt13MigrationTests`, `DeckTests`,
`BaseTests`, `BaseDefenceTests`, `ArmourTests`, `AirAndTowerTests`, `AircraftTests`, `ApsTests`, `WeaponTests`,
`WeaponRhythmTests`, `TowerCardTests`, `StringsTests`, `ItemTests`, `ContentTests`, `Prompt15MigrationTests`,
`Prompt17ContentTests`, `NewVehicleTests`, `StoresTests`, `EconomyTests`, `BaseStrengthTests`, `QuickModeTests`,
`DefendModeTests`, `DefendLinesTests`, `SiegeModeTests`, `AiTests`, `ModeEndingTests`, `CounterBuyTests`. Pinned numbers updated to the data: the twin tank's reload, the
wheeled gun's DPS band, the Iron Beam's beat (read from the data), the drone hangar's flights (read from the data).
`Prompt8ContentTests.BossRushBringsTheFiveNewBosses` (11 kinds for 10) and `TheAirshipsHullIsShutUntilTwoEnginesAreDown`
(8 parts for 7) fail on bosses this pass does not touch (prompt 18's parts and Boss Rush list); left for their owner, like
the known BossParts and ModelTests failures.

### Left

- The Lancet is not the best artillery hunter yet (126 in the artillery fight against the strike drone's 465 and the wheeled
  gun's 653); B.3's attack jet, strike drone and scout helicopter under 30 %; the heavy fortress's heavy DPS (89 of 140);
  the Patriot 203 / PAC-3 245 (260 / 320 wanted: its worth in CP is already over its band).
- After the lead merge: the C-RAM's dome, the rocket battery, the AA tower's branches; the pick run again.
- Boss Rush reaches its 30-minute cap in every measured run (prompt 18's big attacks and parts); the owner's 15-25 minutes.
- Refresh the vehicles' `value` data; the ladder again; the tick budget on a quiet machine.

## 19E. Prompt 20 pass 2 (E-K): the boss template system, main and mini bosses, the new bosses (2026-09-29)

Prompt 20 E-K on feature/p20-pass2 from lead/integration 8ac15b8 (L-M merged). The owner's token rule: compile, one
targeted run, no sweeps, no screenshots. Pass 1 (renames, chapters) was running beside it: no existing boss is renamed and
no boss is placed in a chapter here (see "Campaign" below for the merge that follows).

### E. The templates (`Sim/Content/BossTemplates.cs`, `Catalog.P20.cs`; docs/ADDING_A_BOSS.md)

- A JSON pre-pass before the vehicles are parsed, so everything downstream is the old vehicle data: **frames**
  (`bossFrames`: tracked, wheeled, hovercraft, train, ship, submarine, aircraft, spacecraft; "defaults" merged under the
  boss one level deep; the catalog checks the frame's rules: a spacecraft has tiers, a ship or submarine `naval`, a
  submarine a sea `burrow`, only aircraft and spacecraft fly), the **part and weapon library** (`bossParts`, `use`; a
  library part with a weapon adds and carries its own mount), `dropParts`, `size`, **variants** (`variantOf` +
  `variant`: size, keep, drop, tune, tint, mark, name; the parent's built data and model, mounts renumbered, dropped
  weapons' nodes hidden, phases / radio / big attack never inherited), and **ranks** (`bossRanks`). Big attacks may
  build on another (`from`, strikes merged by index). Escort templates by general (`escortTemplates`): a table with
  `template`, or a boss with no table gets its general's; a ship never (its `fleet`); a mini's waves cut to 3.
- The hovercraft needed an eighth frame ("hovercraft", moving as wheeled): the spec's seven have no hover.
- Existing bosses keep their hand-tuned parts and escort tables (the library and templates are there for new ones and for
  F.3's weapons); moving them onto frames, ranks, generals and sizes is data only.
- Every rank rule is data: main 3 phases (0.7, 0.3; damage x1.1 then x1.2 and speed x1.1) for a boss with no phases of its
  own, a 6 s camera pan, the "boss" track, reward 1; mini hp x0.55 (its parts' shares follow), weapons x0.8
  (`damageScale`), big attack x0.7 damage and x1.3 cooldown with the same warning (`bigAttackScale`), 2 phases (0.5), 3
  escorts, the compact bar, a 2.5 s look, `boss_mini` (the shared track, asset debt: it plays `boss` until it exists),
  reward 0.45 (exposed on the rank; Boss Rush's bounties are pass 3's). A tiered boss's tier marks are its phases.
- New mechanisms (`BossSystem.P20.cs`): `factory` (Moloch), `crush` (Kronos, Ixion: dps to what is in front of the hull,
  towers and walls x`structure`, an HQ flattened, armour cut per level, debris from a phase), `route` (a map route the
  boss follows unless a mission gives its own: `MissionMode` drops it), `spotAura` (Argus: its side's artillery spread
  x0.5 while its radar stands), `wake` (mounts woken by a phase: Typhon's deck gun), sea dives in `burrow` (`sea`,
  per-phase surface / under times, `stopPhase`; the naval system leaves a diving boss alone and it fires nothing under
  water), skimmer passes in `naval` (`passIn` / `passOut`: Caspian), per-phase pod intervals and a halt phase (Daedalus),
  count-based part stops for pods, doors, crushers and fire direction. Big-attack library: `arc` (a swing measured from the
  hull front), `charge` (the boss itself down a warned line), `seats` (a circle's rounds land troops), `cut` (the share
  left once a carrying part breaks; 0 stops it), `surface` (a diving boss comes up to launch with only its parts
  hittable: `BodyShut`). The arc's warning is three rings (the view draws rings and strips only).
- A ship boss's sinking line is its own (`<radioSpawn>.sunk`); Leviathan keeps Kessler's.

### F, G. Main and mini rules on the existing bosses

- Sizes: main x1.35 (Bastion, Behemoth, Jötunn), x1.3 (Matriarch, Roc, Nemesis), Leviathan x1.12, Icarus x1; minis x0.85.
  The hit radius and part positions scale with the model (prompt 19 kept the radius; a boss's must follow its hull).
- F.3 weapons, each a part: Bastion a 155 mm casemate and two ZU-23; Behemoth two 120 mm flank guns and a rocket pod;
  Jötunn a second 203 mm and a Buk SAM; Leviathan two 127 mm; Matriarch two 30 mm belly guns and a second drone bay; Roc
  two 105 mm pods; Nemesis a 152 mm gun car and an AA car (41.6 m now); Icarus two turrets that wake at the crash. New
  weapons on the calibre scale: `casemate_155`, `naval_127`, `naval_100`. With more than ten parts a part is 5-6 % of the
  body (the 70 % total holds; the parts test allows it).
- G.3 drops: Inferno the flak, Harpy a minigun and the missile rack, Tempest both coilguns, Juggernaut the mortar car, Hive
  the SAM, Spectre one 40 mm (its big attack loses that gun's strike), Charybdis one CIWS.
- Roc gets a second phase mark (0.7 and 0.35); the rest take their rank's phases or keep theirs (the minis had one each).
- HUD: "Boss" / "Mini boss" on the bar (a mini's bar at 86 %), the arrival pan by rank, the rank's or boss's own track.

### H-J. The new bosses

Moloch (workshop, 4 x 120 mm, flak, doors, tracks; "Workshop Dump" drop 3 a door + 8 x 152 mm), Daedalus (the Silver Bug's
airframe, 10 s orbit then high/low, three pod bays, max 8 pod vehicles, halts low in phase 3; "Orbital Mass Drop" 6 pods,
3 with a bay gone), Kronos (four tracks, cab, boom, bucket wheel, 2 x 30 mm, rockets; the open-pit "kronos" route, crushes
towers and the HQ; "Bucket Sweep" 120 deg x 25 m, 1 200), Typhon (dives on a schedule, surfaces elsewhere, stays up in
phase 3 with its deck gun; cruise missiles surfaced; "Underwater Launch" 3 x 500 at the base, rising to launch; corvette
and missile boats), Ixion (two wheels, steering wheel armour 1, 76 mm; crushes by armour; "Crushing Charge" 80 m, 900 and
2 s stun, a wheel broken throws it off), Caspian (passes 6 s in, 20 s out; "Anti-Ship Volley" 4 x 500); the variants
Bastion Mk.0, Fenrir (hit and run: shoot-and-scoot), Scylla (near lane, no escape, no landing craft), Locust (armour 1),
Behemoth Mk.II (front 4), Icarus Mk.0 (no orbit, 2 phases), Argus (fire direction). Starting numbers, unrun.
Names follow pass 1's rule; each has a Guide card, a parts tip, a radio line, its big attack's words (`BossText`).
Models: first passes in `Tools/blender/mb_p20_bosses.py` (Daedalus on the Silver Bug's hull builders); the variants use
their main boss's model with a tint.

### K. Generals

Data `general` on every boss per the table (Brandt's id is `brandt`, new; Gungnir moves to Orlov and Tartarus to Lý Hàn,
their radio keys with them). Each boss's arrival line speaks for its general.

### Modes and the Sandbox

Boss Rush gains seven kinds (the four new main bosses; the minis in three groups) and 88 minutes; pass 3 reworks it.
Operations' "two bosses" brings the mission boss's mini version. Sandbox calls (plain `BossSystem`): `JumpPhase` (tiers or
ordinary phases, one a call), `TriggerBig`, `SetBigOff`, `Break`, `Restore`, `ForceTier`, `SetEscorts`, `SwapRank`.

### Tests

New `Prompt20BossTests` (10: templates and ranks, a variant from data alone, Moloch, Kronos, Ixion, Typhon, Daedalus,
Argus, the Sandbox calls, the words); `BossPartsTests.Expected` and its share rule, `BigAttackTests` (the part order).
One run of that filter after a compile fix: 11/12, the old "last part" assertion fixed after (not rerun).

### For the testing phase

5-seed kill times and win rates of every boss at each difficulty (main 5-8 min, mini 1.5-3 min on Normal); the stuck
detector round the enlarged ground bosses, Kronos on the open-pit route and Ixion's charge; FPS with Moloch's and
Daedalus's spawns; the suites (muzzle audit and model tests on the new and rebuilt models, card counts, Boss Rush).

## 19L. Prompt 20 L-M: towers, two new battlefields (2026-09-29)

Parts L and M only. The boss code, the campaign's structure and chapters, and the boss and general renames are
other agents' (prompt 19 is rebuilding the Silver Bug); nothing of theirs is touched here.

### L.1 The Iron Dome branch of the C-RAM

- **Which branch goes.** The C-RAM keeps two rank-7 branches (the roster test wants two for every tower): Centurion
  (three interceptors, one back every 1.5 s) stays the quick close-in C-RAM; the Iron Dome (`c_ram.dome`) takes the
  Hunter's place (`c_ram.hunter`, a 45 m gatling at aircraft: the SAM post and the Patriot already do that job).
  Save: `RosterVersion` 3 drops a Hunter choice (`CardMerges.RetiredBranches`); the tower fights as itself and its next
  choice is free. The card manifest entry is renamed (same model and picture as the C-RAM's; a launcher model of its own
  is art debt).
- **What it takes** (`ApsDef.Direct` false): only rounds lobbed from afar: drones, artillery rockets, missiles with a
  minimum range (ballistic, GMLRS) and half the shells (`shells` 0.5; the C-RAM 0.3). Never direct fire (gun rounds,
  ATGMs, rocket pods, air-to-ground missiles: those are Centurion's) nor energy (as every APS). Why: the prompt's list
  (rockets, missiles, shells, drones; not direct fire) read with the real system's job; it gives the two branches
  different fights instead of one being the other plus reach.
- **Reach and shots.** Interceptors for rounds aimed within 60 m (C-RAM 35). Six in the launcher; the whole launcher is
  back 12 s after the last launch (`ApsDef.Reload`: prompt 13's magazine, the clock restarting at every launch, so a
  part-used launcher also refills in a quiet spell; nothing trickles back). At most 0.5 a second against the close-in
  C-RAM's 0.67: fewer shots, further out, a whole rocket salvo at once. The first try (four, 16 s) lost to the plain
  C-RAM even against lobbed fire (measure below), so it was raised once. An interceptor meets the round up to 10 m short of its
  mark (`ApsDef.Missiles`); the view draws a missile streak off the launcher and the burst 9 m up.
- **Its launcher's other missiles** (`tamir`): at drones and aircraft within 60 m, 110 fragmentation, six in the
  launcher, 20 s to reload: a drone killer, weak on aircraft (about a sixth of the SAM post's damage a second).
- **Shown**: its own line icon (`t_irondome`: a canister launcher under two intercept arcs; `TowerIcons.For` returns
  it for the branch, the branch rows on the Base screen and the detail page show it), generated Behaviour lines
  (`ul.apsMagazine`, `ul.apsLobbed` from the data), the branch note, the C-RAM guide's tip. The in-action clip is not
  made here (graphics; testing phase).
- **The AI picks by the deck it faces** (`BaseLoadout.ChooseAiBranches`, from `ForAi(..., against:)`): the sessions pass
  the player's deck for the enemy base, the Siege and weekly fortresses and a mission's enemy camp. A deck whose cards
  mostly lob their fire (main weapon a drone or with a minimum range) gets the branch that takes no direct fire and
  reaches furthest (the Iron Dome); otherwise the close-in branch with the most interceptors (Centurion). Easy keeps
  plain towers; with no deck given nothing changes (the base-strength references are the same). Only point-defence
  towers get an AI branch: branching every AI tower would move every mode's balance, which this prompt did not ask for.

### L.2 The rocket battery over walls

- **Checked in the sim**: its rockets (minimum range 8 m) are indirect, so `HasLineOfFire` never asks for a clear line and
  the wall-burst in `CombatSystem` skips them; vision is not blocked by walls; splash is not occluded. A test puts the
  battery 10 m behind a wall with a tank 8 m beyond it: the rockets hit, its machine gun (direct fire) does not; inside
  8 m only the machine gun fires. Nothing blocked them; no sim change was needed. The drawn arc is the launcher's
  elevation or 0.28 of the distance (at 18 m about 5 m high, over a 3 m wall); a look with graphics is for the testing
  phase.
- **Its job in the layered bases** (DECISIONS 16A): an AI-held layered fortress puts a rocket battery on every other
  medium hardpoint of its yard (`BaseSystem.YardTower`), about 30 m behind the outer wall: the attackers at the wall's
  foot, where the wall's own direct-fire towers cannot look, are in its 8-55 m. The player's own layered base stays
  exactly as laid out. The guide says so.

### L.3 The AA tower's SAM post

- `aa_turret.sam` fires `sam_post` (the Buk pair, 60 m; was 55) and sees 64 m. The three layers now read: flak branch
  46 m (quad 23 mm, the small tower's +25 % on helicopters and drones: close in, drones and small swarms), SAM post
  60 m (aircraft and helicopters), Patriot 72-100 m (the big umbrella). Branch notes updated.

### L.4 Measured (`CombatValueMeasure.PrintPrompt20Towers`, MB_BALANCE=1, one seed, about a second)

- **Point defence** (four undying tanks holding fire, 45 s; HP lost / interceptions). Direct fire (two BMPTs, an attack
  helicopter, an FPV carrier): none 5240; C-RAM 1400 / 18; Centurion 840 / 22; Iron Dome 840 / 10 (its drone kills
  and the ATGMs let through). Lobbed fire (MLRS, howitzer, mortar carrier, Lancet truck): none 4867; C-RAM 688 / 11;
  Centurion 784 / 14; Iron Dome 879 / 17 (four in 16 s: 1744 / 8). The tanks stand inside 35 m of the guard here, so
  the dome's reach is not counted: in a base its 60 m covers about three times the C-RAM's ground. Within the targets:
  each branch best at its own fight, none dominant.
- **Anti-air** (30 s against an undying helicopter held at 30/45/58/70/88 m; three drones at 30 m): AA tower 5606 at
  30 m, nothing beyond (its reach is 42-44 m), drones 11802; flak 2197 / 1555 / 0 / 0 / 0, drones 7960; SAM post 6011 /
  4800 / 4800 / 0 / 0, drones 6299; Patriot 3066 / 2040 at every distance to 88 m, drones 3765. The reach layers read
  as asked (flak 46 m, SAM post to 60 m, Patriot out to 90), but the flak branch was a weaker plain tower (drones 7960
  against 11802), not the drone killer the prompt keeps it as. Its quad 23 mm now does 22 a round (was 14, the twin
  30 mm's figure; bigger splash, no missiles): against the undying drones damage scales with it, about 12,500, above
  the plain tower, while it stays behind it on helicopters (no missiles). Not re-measured (the owner's one-run rule):
  the testing phase's measure checks it.
- **Rocket battery** 10 m behind a wall, two tanks and two armoured cars at its foot, 60 s: base 2822, cluster 3587,
  thermobaric 3590, all over the wall.
- **Base cover** (prompt 14): `BaseRoles` gives the dome Intercept and AntiAir with a 60 m air reach, the SAM post 60 m,
  the rocket battery 55 m with its 8 m minimum; the Base screen's circles and cover strip read the same data.

### M. Two new battlefields

- **Ids** `openpit` (Open-Pit Mine / Mỏ Lộ Thiên, desert) and `orbitalgate` (Orbital Gateway / Cửa Ngõ Quỹ Đạo, snow);
  display names only in `Strings` (`map.<id>`, `.sub`), so prompts 21-23 can rename them freely.
- **Open-pit mine**: three broken rings of rock stepping down to the pit floor (the centre objective), ramps through
  each ring, 14 m ore haul roads winding down and out to the processing plant and the spoil heaps (the side
  objectives), ore heaps, the plant's buildings and conveyors, haul trucks. The **fixed route** is data:
  `"routes": {"kronos": [x, z, ...]}` in its _conquest, _sandbox and _siege files (`MapDefinition.Routes`,
  `Route(name)`; `Reversed()` walks it the other way), 12 points and 433 m from the north-east camp road along the haul
  road through the pit to about 19 m from the player's HQ. It is laid as a 14 m road, so nothing stands on it; the
  builder checks every 2 m that 7 m either side is open (1694 cells, all open) and the new test checks the path on the
  sim's grid. Prompt 20 J's Kronos will read `map.Route("kronos")`; nothing drives it yet. The long file has no route
  (the boss plays the square).
- **Orbital gateway**: a radar station complex, two launch pads on the flanks (the rocket between its gantries, fuel
  tanks, flame trenches, blockhouses, sandbags), and a 60 x 60 m field at the centre kept clear of every solid prop
  (floodlights and runway lights round its edge) for drop pods.
- **Versions**: Conquest, Survival and Siege from `build_maps.py` (`MAPS_P20`, `WAR_P20`, `DENSIFY_P20`, the two
  `boundary.SHAPES`), the long battlefield from `longmap.py`; `MatchSettings.AllMaps` (skirmish list, the Base
  screen's maps, the weekly draw), menu pictures from `map_thumbs.py`. Camps on both maps: 2 large, 3 medium, 6 small
  tower and 3 utility hardpoints each side, an outpost pair at every objective; the slot labels come from the camp's
  geometry (`SlotPlaces.Keys`) as on every square map, and from the data on the long ones. `check_access` passes the
  _conquest, _siege and _long files, the _sandbox files pass its check too; `longmap` ok. Other maps' files unchanged.
- **Guide**: `guide.map.openpit` and `guide.map.orbitalgate` (terrain, lanes, who it favours, a tip) are in the Guide
  table; no screen lists battlefields yet (the Guide tab is per unit), so they wait for the battlefield page of
  prompt 20 O. Their campaign use (chapters 8 and 11) is the campaign agent's.
- **Open points**: the orbital gateway's centre objective has its two outpost hardpoints about 20 m from the centre,
  inside the landing field (slots, not props; a tower built there stands on the drop-pod ground; move them if the
  drop pods need the whole field). The siege fortress logs "could not place fuel_depot / ammo_dump / vehicle_hangar"
  on both maps (dressing only; every check passes). Base map pictures (`BaseMapShots`) need graphics.

### Tests (run once each; PlaySmoke and suites not run)

`Prompt20TowersMapsTests` (8) and the measure: the first run failed the wall test (the wall's seam sat on the line of
fire) and the anti-air measure's attackers never came in; both fixed, the rerun and one more run of the wall test (now
two salvos, the machine gun alone counted) pass 8 of 8. The rest of the lists that name the maps (BaseSiteTests,
TrafficTests, MapRouteTests, whose count is now 23 with Lighthouse Bay) were not run.

### For the testing phase

- `StuckBatch` (prompt 12) on openpit and orbitalgate: every version (conquest, sandbox, siege, long), both sides, 5 seeds;
  `BaseSiteTests`, `TrafficTests`, `MapRouteTests`, `MapConnectivity` on the two maps; `ConquestBattleTests` on them.
- 5 seeds: Siege and Defend on the long maps with the yard's rocket batteries; skirmish against lobbed and direct decks
  with the AI's C-RAM branch; `CombatValueMeasure.PrintPrompt20Towers` with `MB_CV_SEEDS`; `TowerPickRates`.
- With graphics: the Iron Dome's streak and burst, the rocket battery's arc over a wall, the in-action clip for the
  branch, `BaseMapShots` for both maps and their long bases; a launcher model for the Iron Dome (art debt).

### Shared edits (merge by hand if they conflict)

`balance.json` (`tamir`, `sam_post`, `c_ram.dome` for `c_ram.hunter`, `aa_turret.sam`), `SkillDef` (ApsDef), `Catalog`
(aps), `AbilitySystem` (APS reload), `DamageSystem.TryIntercept`, `MapDefinition` (Routes), `BaseLoadout` (ForAi's
`against`, `ChooseAiBranches`), `BaseSystem.EstablishFortress` (yard), `ModeSessions` (four `ForAi` calls),
`PlayerProfile.Arsenal` (RosterVersion 3), `CardMerges`, `EffectsDirector` (intercept), `UnitLines`, `UnitText`,
`Strings`, `GuideText`, `Icons`, `TowerIcons`, `BaseScreen` and `MenuScreen.Detail` (branch icon), `MatchSettings`,
the card manifest, `FireRhythmMeasure`, `CombatValueMeasure`, the three test lists, `Tools/maps/build_maps.py` and
`boundary.py`. No boss, campaign or rename code touched.

## 19N. Prompt 20 pass 3 (N-P): Boss Hunt, the chapter and boss screens, the moves to the new maps, the cheap checks (2026-09-29)

Parts N, O and P on feature/p20-pass3 from lead/integration f33c170 (passes 1 and 2 merged). The owner's token rule:
compile, one small test filter, no suites, no PlaySmoke, no screenshots; everything heavier is on the list at the end.

### N.1 The week's Boss Hunt (the old Boss Rush, `GameModeKind.BossRush`, same id and save keys)

- **Draw** (`Sim/Modes/BossHunt.cs`, `Game/Match/BossHunts.cs`): the story's bosses are every chapter slot of the
  chapters switched on (campaign.json `main` / `minis`), in story order (chapter by chapter, where a mission or stage
  first fights it). A week draws 3 main and 7 mini bosses with SplitMix64 seeded by the ISO week (year x 100 + week,
  `WeeklyFortress.Week`): System.Random's sequence is not promised across runtimes, so every device gets the same run.
  Each list is put back in story order and laid out as minis leading to mains, 2 + 2 + 3 (mains at 3rd, 6th and 10th).
  Fewer bosses on, a shorter run (act I alone: 4 minis and 3 mains).
- **Stronger down the run**: story order plus a ramp, boss health x0.9 at the first to x1.2 at the tenth and damage
  half that ramp (x0.95 to x1.1), through the enemy side's mutator hook (`SimWorld.SetMutators`, bosses only, so parts,
  phases and escorts follow the health). The full hunt keeps campaign strength (no ramp).
- **Clock** 45 minutes (ten bosses of 1.5-3 / 5-8 minutes and nine rests: the 30-40 minute target with room). CP as
  before (12 on the kill, 8 at 75/50/25 %, 2 a part); coins 120 a boss; the first clear of the week +1 500 coins
  (the Operations weekly ledger, key "hunt").
- **Rest** 20 s (`Breather`, as before): each vehicle of the army gets 30 % of its health back when a boss falls
  (`RestRepair`); a strip under the top bar shows the rest, its seconds, the next boss and the supports held.
- **Supports** (`HuntSupports`, 12): after each main boss (not after the last boss) three not held yet, drawn from the
  run's seed and the boss index (the same after a resume). Reinforced Hulls (health +15 %), Gunnery Drills (damage
  +10 %), Fast Loaders (fire rate +12 %), Tuned Engines (speed +12 %), Field Repairs (1 %/s out of fire), Rapid Tasking
  (support cooldowns -25 %, new `TeamEconomy.StrikeScale`), Supply Convoy (income +20 %), War Chest (35 CP now), Extra
  Crews (army cap +6), Mobile Workshop (rests repair 60 %), Bounty Contracts (boss CP +50 %), Free Reinforcements (the
  deck's three dearest vehicles airlifted, free). Each is a modest edge of a different kind so none is the pick; per-
  vehicle ones reach vehicles landed later too. The pick screen does not stop the battle (the rest runs); an offer not
  answered when the rest ends takes its first card (so a run never waits and a headless sim stays deterministic). The
  pick is a recorded input (`MatchJournal "support"`).
- **Checkpoints** after each main boss (the full hunt: after every boss), kept as the rest ends (after the pick).
  Decision: a checkpoint is the carry prompt 16 made for switching battlefields (bosses down, time used, CP, the army
  with its health, the supports), not prompt 5's step replay: the replay rebuilds one battle from its seed, and a hunt
  spans several battlefields and several sittings. It is saved in the profile (`PlayerProfile.Hunt.cs`, `hunts`); the
  week's is good until the week ends, both only for the same boss list. Taken up from the result screen's checkpoint
  button (as an operation's) or from the Operations page ("Continue" / "Start over"). Bosses paid in an earlier sitting
  are not paid again (`BossRushCarry.Paid`). The army lands again at the drop zone (positions are not kept).
- **Own battlefields**: unchanged mechanism (prompts 16 and 19): a ship to Lighthouse Bay, Icarus to the Launch Site,
  and Kronos to the open-pit mine (its `arena`, pass 2), back home after.
- **Left out: the trains** (Nemesis, Juggernaut). They run on their mission's rail line and no hunt battlefield has
  one; the old Boss Rush left them out too. So the hunts have 11 of the 12 main bosses and 18 of 19 minis. For later:
  a hunt stage on the capital's metro line.

### N.2 The full Boss Hunt

Every slot of the chapters on, in story order (29 now; it grows by itself when an act is switched on or a chapter
gains a boss), a checkpoint after every boss, a support after each main boss, no clock. It opens once the last
chapter on is done (its operation won). Board: the five best total times on this device (the run's time over every
battlefield and sitting, the time lost to a defeat not counted); no online board exists in the game. First clear:
10 000 coins and a legendary crate (once). Its supports' seed is fixed (2020), so the run is the same for everyone.

### N.3 Operations

The mutator `two_bosses` ("Extra mini boss" now) brings a mini boss: the mission's own when it is one, a main boss's
mini version, else its chapter's first mini (its general's); before, a Behemoth when the mission had none
(`MissionSession.ExtraBossFor`). No other mutator names a boss. The new chapters' operations were already in the
replay list (pass 1).

### O. Screens

1. Chapter screen: the four acts and twelve chapters and the act switches were pass 1's; each card now also says how
   many mini bosses it has.
2. Boss bar: the names were already "Proper name · subtitle" (`unit.*`, pass 1); a main boss's bar gets the big track
   (`fc-boss--main`, 14 px), a mini's the small one (86 %, 6 px track, smaller name).
3. Dossier boss files: rank and general under the name; once open, links to the boss's Guide page and to the boss it
   is a variant of. A boss's Guide page (its detail page, now without deck, level and blueprint parts): rank, chapters,
   the general's portrait, name, call sign and naming theme (`char.*.role`), "Variant of ..." and its variants, each a
   link; the page's arrows step through the bosses in story order. The Boss Hunt lists open each boss's page.
4. Boss Hunt: the rest strip and the support pick (three cards side by side, 760 pt, from prompt 10's kit like the
   stage choice); the Operations page shows the rules, reward, checkpoint, bosses in order, supports and the board.
5. Battlefields: a dossier tab ("Chiến trường") with every battlefield's picture, line, the chapters that fight on it
   and its guide where it has one (openpit and orbitalgate now); the Guide tab has a button to it.
Every new word is in the tables (`BossText`: `hunt.*`, `guide.boss.*`, `guide.map.*`, `dossier.maps`,
`campaign.minis`). "Boss Rush" reads "Boss Hunt" in English. Pass 2's Wolff lines said "Quạ Đen:"; they say "Raven:"
now (the rule of 19A). Timeline 10's doubled "Roc, Roc" is fixed in the sources.

### Pass 2's leftover: onto the two new battlefields (Tools/campaign/act4.py, `move`)

c8m02, c8m07, c8m10 on openpit; c11m04, c11m07, c11m10 on orbitalgate (`POINTS` and `WEATHER` for both in
campaign_kit). Both maps are in the standard frame, so the goal points stay; what named the old map changed:
c8m10's stages burn the fuel store (storage tanks by the crusher plant), blow the ore silos and the processing plant;
Kronos starts at the head of its "kronos" route (96, 96) and walks the whole haul road; Ixion comes down the haul road;
c11m07 burns the west pad's rocket fuel tanks (its three guards moved there); c11m10 (siege version, in snow) takes
the radar posts at (-12, 59) and round (42, 6). Chapter 8 and 11's map lists put the new maps first (their cards'
pictures). Only the changed keys moved in CampaignText.cs (briefs of c8m02, c8m07, c11m04, c11m07; c8m10's stage and
choice titles; timeline.10).

### Tests (`Prompt20HuntTests`, 9 cases; run twice: 9/9, then 9/9 after the last edits)

The week's draw (determinism, 7 + 3 in 2-2-3 groups, story order, the ramp, no train), the full hunt (every slot in
story order, opens after the last chapter), chapters switched off left out (acts I-II and I-III, and back), checkpoints
and resume (no support or checkpoint after a mini, 30 % repair, three offered after a main, the checkpoint's contents,
saved and taken up in a later sitting, stale for another week or list, the run going on), the twelve supports (fair
offers, the effects of four of them), every boss's rank and general (prompt 20 K) and its bar name, the extra-boss
mutator, no old names in any table (BossText too), the six moved missions (targets on the new maps, Kronos on its route).
`KitInteractionTests` and `ExportGameDoc` read the hunt's count now (not run).

### For the testing phase

- 5 seeds of the week's hunt on Normal (target 30-40 minutes, the ramp, the supports' pick rates and value) and of the
  full hunt through its checkpoints (several sittings, map switches for the sea bosses, Icarus and Kronos).
- Stuck checks for the six moved missions (openpit and orbitalgate with their props and routes, Ixion's charge down the
  haul road, Kronos through the pit), and the bosses' map switches in the hunt.
- FPS: the hunt with a support that adds vehicles (Free Reinforcements, Extra Crews) and Moloch's or Daedalus's spawns.
- With graphics: screenshots of the chapter screen, both boss bars, the rest strip and the support pick on a phone,
  the Operations hunt pages, the dossier's battlefields and a boss Guide page.
- Suites: KitInteractionTests, CampaignTests (the moved missions), LocalisationScanTests (the new keys),
  Prompt20CampaignTests, ModeEndingTests and SiegeModeTests (Boss Rush paths), PlaySmoke's BossRush step.

### Shared edits (merge by hand if they conflict)

`SiegeModes.cs` (BossRush classes partial, hooks), `EconomySystem.cs` (`StrikeScale`), `StrikeSystem.cs` (one line),
`ModeSessions.cs` (`BossRushSession`, `ExtraBossFor`), `MatchRunner.cs` (checkpoint button, switch, preload),
`PlayerProfile.cs` (three fields), `BattleHud.cs`, `MissionBar.cs`, `Screens.uss`, `MenuScreen.Operations/Home/Detail/
Story/Campaign.cs`, `Strings.cs` (Boss Hunt, the mutator), `BossText.cs`, `CampaignText.cs` (the keys above),
`campaign.json`, `Tools/campaign/act4.py`, `campaign_kit.py`, `story.py`, two tests. balance.json untouched.

## 19P. In-action clips, effects and sound: the owner's play-test list (2026-09-29)

The owner's list for the detail page's In action clip (Xem bắn), plus effects and sound. Branch `feature/inaction-fixes`
from `lead/integration` 6be4269.

### The clip (FiringRange, now in three files: the range, its ability scenes, the tower scenes)

- **Unlimited ammunition (1)**: the unit shown is topped up every step (`SimWorld.Refill`: magazines, an aircraft's
  stores, a fixed minefield laid again once half its mines are gone). Friends a scene empties on purpose (the ammunition
  carrier's and the depot's launchers) still run dry and reload, which is what those scenes show.
- **A mortal enemy (2)**: range targets and sparring partners of the enemy side are now `Vehicle.Mortal` (they neither heal
  nor stop at a sliver). 2.5 s after one is knocked out a new one comes in: an aircraft flies onto the spot, a ground
  vehicle drives up to it from 16 m beyond (holding its fire) and stands as a target once there; attackers come back on
  their mark with the same orders. Our side (the scene's friends, a tower on show) stays unkillable.
- **A gentle opening (3)**: every view in the range arrives with `VehicleView.GentleArrival` (a 3.2 s ease-out: fastest
  as it comes in, slowing all the way onto its station, over a shorter run), and nothing fires at a target until the
  target is drawn, flown in and inside the picture (`HoldUntilFramed`, 3 % margin, through `SimWorld.HoldFire`). The
  shooter itself need not be in the picture (a jammer scene's missiles come in from beyond the edge). Chosen over a
  slowed clock at the start: the battle keeps its real pace.
- **Jammed rounds (4)**: the sim decides at launch that a guided round is jammed (or has lost its lock) and where it
  lands (`Projectile.Miss`); the WeaponFired event now carries that miss (`SimEvent.Offset`, `Jammed`). The view flies
  the round true for the first 35 % (60 % for a lost lock), then a crackle of sparks and light, and it corkscrews
  (2.2 m, widest halfway), rolls and bends off onto the target plus the miss, where the sim's impact bursts: on the
  ground wide of a ground target, in the air beside an aircraft. Nothing vanishes any more.
- **The mine layer (5)**: once one of its mines is armed, enemy vehicles (an IFV, then an armoured car, a light tank)
  drive across, over an armed mine away from the layer, and back over another, holding their fire, one at a time, a new
  one 3 s after one is lost. Captured: two mines went off in 16 s.
- **Every clip reviewed (6)**: a headless probe of all 96 cards and the two gunship bosses (StartupProbe, 8 s each)
  before the change, and the new scenes with graphics after. Towers with nothing to shoot now have scenes:
  - CP relay: its pay counted over the picture ("CP relay: +0.10 CP/s · 1.3 CP paid", from the text tables), a gold
    pulse while it pays; an armoured car raids it for 2.5 s every 14 s, and for the quiet time the line turns red
    ("Under fire: no CP for 5 s") and the pulse red.
  - Dragon's teeth: a row of five across the enemy's road, a friendly tank behind; enemy vehicles on their way through
    go round the ends under its gun (the wire branch is passable and slows them instead; not captured).
  - Minefield: enemy vehicles drive across over its armed mines (four went off in 16 s).
  - Ammunition depot: the range's home is at the depot (`SetRally`) and emptied launchers beside it reload there faster,
    with a line over the picture; logistics station: the army supply it adds, as a line.
  - Shield generator: its attackers stood inside its 25 m dome (fire from inside is not stopped); they now stand
    outside it (103 dome hits in 16 s). EW tower and radar station keep the jammer and counter-battery scenes.
  - A big boss (the drone mothership) is framed from further back so it no longer fills the picture; a gunship is
    framed on its whole turn.
  - Left as they were: the repair bay and airfield (they work on a base, which the range has not), and mission-only
    pieces without a card or a weapon (super gun, targeting station, drop pod, landing craft, hover gunboat).

### Effects and sound

- **Laser beam sound (7)**: every beam weapon (the laser tank's focused laser, the Iron Beam, the orbital laser) is now
  one continuous hum while it burns: a synthesised seamless 2 s loop (a 110 Hz sawtooth with its octave and sub, a
  fluttering 1.76 kHz shimmer, a faint crackle), swelling in fast and dying away 0.2 s after the last shot, panned to the
  nearest beam, with a rising whine when a beam ignites after a pause; the per-shot machine-gun (or flak) clatter and the
  impact pings of beams are gone. No recorded clip exists for these (the synth stands in, like the other categories).
- **Hits on a shield (8)**: a dome hit now says where the round came from and whether it came down from above
  (`DomeHit`: Target, Airborne; Mount 1 when the dome took all of it). The view finds where the round's line crosses the
  dome's skin (above the unit for shells and bombs), ripples the hex shield there and flares it (a white-blue glow and a
  spray of sparks off the skin); a round the dome took whole bursts on the skin, as big as before, instead of on the
  unit under it. The Shield Dome item's dome flares the same way over where a round lands.
- **FPV drones (9)**: a quadcopter round (the `fpv_drone` model: the swarms, the carrier's, the hangar's and the drone
  mothership's) flies as one: no motor flame or smoke trail, level with the nose a little down and banking, a blur disc
  on each rotor, a buzz of weaving and bobbing corrections about its own line out to 6 m from the swarm's, then it tips
  over into its dive. It lifts off in a puff of dust with a synthesised prop buzz (not a rocket launch), is drawn a third
  bigger than other drones, and strikes with its own impact: a white-hot star, the charge's jet stabbing down, the drone
  flying apart in bright bits, a small black puff (the blast as big as before). Winged drones (Lancet, Shahed) keep
  their missile-like flight.
- **The sky gunship (10)**: three faults. In play it did not stay where it was called: it took on whatever its guns
  or its guard found and its turn glided after it, 60 m off within 12 s (PlayShots `gunship`, a new scene that calls
  the item over the fight: the plane was out of the picture even zoomed out). A called escort now has a post
  (`Vehicle.PostRadius`, the support's radius, at least 12 m, round the spot): it takes on only what is on its post
  unless ordered, and the side's AI leaves it alone; the rerun has it 23 m from the spot, in the picture at the usual
  zoom (`Docs/art/inaction/gunship-play.jpg`). It flew 40 m up in a 36 m turn, off the top of the battle camera for most
  of the turn: now 26 m up in a 22 m turn (data `orbitRadius`, new). And its 25 mm never fired: the fire-rhythm rules
  made each gun wait for the others' salvos and magazines; a gunship's broadside guns now fire together as a real
  AC-130's do (its 105, 40 and 25 mm each have their own crew). In a 16 s clip: 105 mm x4, 40 mm x46, 25 mm x97 (was x1,
  x24, x0). The data had every weapon; nothing was missing. In the clip it is framed on its whole turn.

### Tests (run once or twice; no suites)

`InActionTests` (7): a jammed round's miss in its event, mortal and unkillable targets, refill and held fire, dome hits'
origin, the gunship's turn and all three guns firing, a called gunship staying over its spot, the readouts in both
languages. First run 3 of 6 (the tests: spawn grace, a moving gun, heavy targets the 25 mm cannot hurt; and the real
25 mm fault above), then 6 of 6, then 7 of 7 with the post test. With graphics:
StartupProbe on 13 clips (gunship, gunship item, drone mothership, FPV carrier, EW jammer, shield generator, CP relay,
mine layer, minefield, dragon's teeth, AA vehicle, laser tank, ammunition depot; no errors) and again in HD for the jammer,
the FPV carrier, the shield generator and the mothership; PlayShots `gunship`. Crops in `Docs/art/inaction/`.

### For the testing phase

- Balance: the gunship item now fires its 25 mm, stays over its spot and flies lower (26 m: every weapon that hits
  aircraft still reaches it); `CounterTests` and a `ConquestBattleTests` sweep with the item; the AI's own use of it.
- Listen on the device: the beam hum and the drone buzz levels against the guns; the readout over the picture on a phone.
- The other scenes' opening with the in-frame rule (a long-range launcher may wait a moment longer before its first shot).

### Shared edits (merge by hand if they conflict)

`SimEvent` (Offset, Jammed, DomeStruck), `CombatSystem` (the miss in WeaponFired, the gunship's rhythm), `DomeSystem`,
`DamageSystem` and `AbilitySystem` (Unkillable), `Vehicle` (Mortal, LastHitAt), `SimWorld` (MakeMortal, Refill, HoldFire),
`Definitions`/`Catalog`/`MovementSystem` (orbitRadius, the escort's post), `StrikeSystem` and `TacticalAi` (the post),
`balance.json` (sky_gunship), `VehicleView` (GentleArrival),
`ProjectilePool`, `WeaponEffects`, `EffectsDirector` (+ Domes, Shields), `AudioDirector`, `SoundSynth`, `UnitPreview`,
`MenuScreen.Detail`, `Screens.uss`, `Strings` (range.*), `FiringRange*`, `StartupProbe` (-mbProbeHd, -mbProbeZoom,
-mbProbeEvery), `PlayShots` (the gunship scene).

## 19R. Play-test 4: missile speeds, fire rates, the bunker vehicle's dug-in mode, look-alike vehicles (2026-09-29)

The owner's play-test 4 items for agent B (`Docs/prompts/requests_vi.md`): missiles slower than they were, except those
already at or below the attack helicopter's, which he likes; every weapon's rate of fire researched and made
reasonable ("like the C-RAM, whose real rate is very high"); a real second mode for the bunker vehicle once it has dug
in, drawn anew; and the vehicles that look alike redrawn. Branch `feature/rates-models` from lead/integration 0505750.

### A. Missile speeds

**The reference.** The attack helicopter's missile is `hellfire_standoff` (AGM-114L Longbow) at **24 m/s**. Every
missile faster than that now flies at 24 m/s; those at or below it keep their speed.

| Weapons | Before (m/s) | Now |
|---|---|---|
| `sam` (SHORAD: aa_vehicle, heavy_aa) | 36 | 24 |
| `sam_long` and its `buk_launcher` (SAM launcher), `sam_post` (tower) | 41 | 24 |
| `sam_battery`, `patriot`, `sam_pac3`, `sam_battery_lrr` (towers) | 41 | 24 |
| `sam_48n6` (long-range SAM) | 56 | 24 |
| `tamir` (Iron Dome, tower) | 44 | 24 |
| `air_to_air`, `wvr_aam`, `r60`, `aim9` (jets, wingman) | 34 | 24 |
| `stinger_atas`, `igla_v` (helicopters' MANPADS) | 29 | 24 |
| `ballistic_missile` (Iskander) | 45 | 24 |
| Big attacks' missiles (Leviathan's, the Typhon's, the Caspian's, the ballistic strikes) | their `"flight"` s at any range | the entry's flight, or longer so they never pass 24 m/s (`BossSystem.MissileTopSpeed`) |

**Unchanged:** every ATGM, AGM and cruise missile (17-24 m/s already); **unguided rockets** (Hydra, S-8, Grad, GMLRS,
TOS, 300 mm, 107 mm: 45-55 m/s). The owner's "tên lửa" covers both, but the attack helicopter he picked fires Hydras
at 48 m/s next to its Hellfires, the lead's brief lists missiles only, and a rocket is unguided: slowed to a
missile's pace it would miss everything that moves. The player's cruise-missile support (a timed strike, not a
weapon) is also unchanged.

**Plumes follow the new speeds by construction:** a flame's length and width are in lengths of the munition as drawn
(12B), its smoke puffs are spaced by distance flown and live a fixed time, and the boost-then-cruise curve is a share
of the flight. A missile at 24 m/s keeps its flame on its tail and its puffs as dense per metre; its trail is shorter in
metres because it flew less far in the same seconds. `MissileFlightTests.PlumesStayOnTheirTailsFrameByFrame` (the Buk
missile at its new speed among the cases) passes.

**Checks:** `CounterTests` all pass (SAM beats jets, anti-air beats helicopters, fighters beat helicopters included).
`MissileFlightTests` pins the new speeds and now asserts that no missile (or the ballistic missile) flies faster than
`hellfire_standoff`; every flight at full range is still shorter than its cooldown (the closest: the tower `sam_battery_lrr`, 4.17 s
at 100 m on a 4.24 s cooldown, 98 %: one for the tower agent to watch; among vehicles the SAM launcher's Buk, 2.3 s on
2.5 s). Slower missiles give flares and point defence more time (11C: a missile is decoyed by flares out
while it flies), so missile-armed anti-air lost a little and aircraft a little more (section E); as the brief says,
rhythm was retuned rather than the speed put back: `buk_launcher` 2.9 → 2.5 s, `sam_48n6` 8 → 7.2 s.

### B. Fire rates

**Method.** For every vehicle, aircraft and boss weapon: the real system's rate of fire (cyclic rounds a minute),
its usual burst and its magazine or belt (published figures: manufacturers, Jane's, the usual references), against the
game's cadence. The damage a round stays on prompt 13's calibre scale and the penetration levels of prompt 15 are
untouched (`CalibreTests`). Where the game's cadence was more than about 20 % off, it moved to the real one, **up to the
60 rounds a second the simulation carries** (three a 20 Hz step, `CombatSystem.Stream`), in the real burst, and the
change after the burst (`clipReload`) or the salvo's cooldown was solved so that `FirePower.Sustained` (the damage a
second over a whole cycle) is kept within 1 %. The rounds a second over time, and so the projectiles and tracers the
view draws, are the same as before; only the peaks are real. A second pass (section E) shortened the bursts that
front-loaded damage enough to move the combat value.

**Changed (vehicles, aircraft, bosses)**, rhythm "cadence x burst / change":

| Weapon (carriers) | Real system | Before | Now |
|---|---|---|---|
| `mg_jeep`, `hmg_roof` (M2 12.7 mm; jeeps, trucks, roof guns) | 450-600 rpm, 5-10-round bursts, 100-round belt | 423-451 rpm x20-21 / 1.2-1.4 s | 550 rpm x25 / 2.2-2.3 s |
| `mg_coax` (PKT / M240 7.62 mm) | 650-800 rpm, 250-round belts | 631 rpm x32 / 1.2 s | 750 rpm x36 / 1.87 s |
| `door_gun` (PKT, Mi-24 doors) | 650-800 rpm | 905 rpm x40 / 1.21 s | 750 rpm x40 / 0.68 s |
| `ifv_30` (2A42 30 mm, IFV) | low 200-300, high 550-800 rpm | 420 rpm x10 / 1.24 s | 550 rpm x10 / 1.55 s |
| `twin_30_bmpt` (2 x 2A42, BMPT) | 2 x 550-800 rpm | 400 rpm x15 / 1.63 s | 1,091 rpm x10 / 1.99 s |
| `autocannon_25` (M242 25 mm, armoured car) | 200 or 500 rpm, short bursts | 300 rpm x10 / 1.67 s | 500 rpm x6 / 1.48 s |
| `gun_57mm` (57 mm, light tank; AU-220M module) | 80-120 rpm | 1 round / 2.53 s | 2 rounds 0.5 s apart / 4.56 s |
| `flak_35` (2 x KDA 35 mm, Gepard) | 2 x 550 = 1,100 rpm, 20-40-round bursts | 600 rpm x23 / 4.34 s | 1,101 rpm x16 / 3.73 s |
| `twin_30_flak` (2A38M twin 30 mm, heavy AA) | 4,060-5,000 rpm a mount | 866 rpm x46 / 1.21 s | 3,593 rpm (the cap) x20 / 1.56 s |
| `zu23` (ZU-23-2) | 2 x 800-1,000 rpm, 50-round boxes | 889 rpm x37 / 1.53 s | 1,802 rpm x16 / 1.21 s |
| `twin_35_ahead` (Skyranger 35 mm revolver) | 1,000 rpm, 20-24-round AHEAD bursts | 670 rpm x25 / 4.28 s | 1,000 rpm x24 / 4.79 s |
| `heli_gun`, `boss_heli_gun` (M230 30 mm) | 625 rpm, 10-50-round bursts | 541 / 299 rpm | 625 rpm (x22 / 4.6 s; the boss's x13 / 5.36 s) |
| `minigun` (M134, scout helicopter) | 2,000-4,000 rpm (3,000 on helicopters) | 732 rpm x39 / 1.01 s | 3,000 rpm x60 / 5.17 s |
| `gsh30k` (GSh-30K, Mi-24P) | 2,000-2,600 rpm | 556 rpm x20 / 1.22 s | 2,400 rpm x20 / 2.8 s |
| `jet_cannon` (GSh-30-2, Su-25) | 3,000 rpm, 250 rounds, 0.5-1 s bursts | 1,200 rpm x70 / 1 s | 3,000 rpm x30 / 1.33 s |
| `fighter_cannon` (GAU-22/A, F-35) | 3,300 rpm, 182 rounds | 566 rpm x31 / 1.01 s | 3,297 rpm x40 / 4.7 s |
| `gunship_25mm` (GAU-12 on the AC-130U) | 1,800 rpm there | 741 rpm x35 / 1.22 s | 1,802 rpm x45 / 3.64 s |
| `bomber_tail_guns` (4 x M3 12.7 mm) | 4 x 1,200 rpm | 642 rpm x34 / 1.48 s | 3,593 rpm (the cap) x25 / 2.96 s |
| `boss_minigun` (GShG-7.62, mega gunship) | 3,500 or 6,000 rpm | 982 rpm x40 / 4.38 s | 3,488 rpm x40 / 6.09 s |
| `boss_hmg` (NSV 12.7 mm, train, Supreme Command) | 700-800 rpm | 225 rpm x10 / 4.1 s | 750 rpm x10 / 5.78 s |
| `hover_ciws`, `ciws_aa` (AK-630M, boss escorts, rail super-gun) | 4,000-5,000 rpm | 142 rpm x7 / 4.44 s | 3,593 rpm (the cap) x15 / 14.7 s |
| `airship_flak` (S-60 57 mm, command airship) | 105-120 rpm, 4-round clips | 312 rpm x11 / 4.1 s | 120 rpm x8 / 0.88 s |
| `mothership_cannon` (AU-220M 57 mm) | 80-120 rpm | 4 rounds 0.18 s apart / 3.75 s | 4 rounds 0.5 s apart / 2.79 s |
| `grad_rockets`, `grad_cluster`, `boss_rockets` (BM-21 122 mm) | 40 rockets in 20 s (0.5 s apart) | 0.08 s apart | 0.5 s apart (the cooldowns 11.31, 8.44 and 2.44 s keep each cycle) |
| `thermobaric_rockets`, `boss_thermo` (TOS-1A 220 mm) | 24 rockets in 6-12 s | 0.14 / 0.2 s apart | 0.3 s apart (cooldowns 11.52, 12.51 s) |
| `technical_rockets` (Type 63 107 mm) | 12 rockets in 7-9 s | 0.2 s apart / 7 s | 0.5 s apart / 5.1 s (the cycle 7.8 → 7.1 s: a stretched ripple loses more of its last rockets) |
| `gsh_23v`, `gau_gatling` (no carrier now) | 3,000-3,400; 3,900 rpm | 1,207; 1,835 rpm | 3,297; 3,593 rpm, the change solved the same way |

The AK-630's damage a second on the boss escorts is small (22), so at its real rate it fires a quarter-second brrrt every
15 s: that is how a close-in gun reads, and the escorts' strength is unchanged.

**Reviewed and left alone** (within about 20 % of the real rate, or a real rate the calibre scale cannot carry):
`autocannon_30` (2A42 on low rate, 300 rpm, which is real); `boss_flak` (GDF twin 35 mm, 1,100 real, 1,200 here);
`autocannon_40` (Bofors L/70, 300); `agl_40` (Mk 19, 325-375 real, 300 here); `naval_76` (Super Rapido, 120);
`gun_120mm` (6-10 rpm with a loader, 11 here); `gun_152`, `gun_152_heat` (2A83 autoloader 10-12, 9.5-10);
`howitzer` (M109: 4 rpm for 3 minutes, 5.5 here); `mortar_120` (2B11 12-15, 9.4); `leviathan_203` (Mk 71, 12, 5 here);
the ATGMs and SAM launchers (TOW, Kornet, Hellfire ripples, Stinger, Buk: within their real reload and salvo times);
aircraft rocket pods (0.05-0.12 s ripples: real). **Faster than real, kept:** `gun_105_long` / `gun_105_apfsds` (the
Sprut's 2A75: 7 rpm, 15 here), `gun_125_elite` (T-90's autoloader 7-8, 10), `gun_105_wheeled` (Centauro II, manual,
6-8; 22 here), `gun_105_bunker` (L7, 6-10; 13), `gun_203_siege` (M110, 1.5-2; 6), `boss_howitzer` (2S7, 1.5-2.5; 6.4),
`boss_mortar` (2S4, 1; 6), `train_gun` (B-38, 5-7.5; 12), `borer_cannon` (2A70, 10; 29), `gunship_105` (M102 aboard,
6-10; 21), `gunship_40mm` (Bofors L/60 aboard, 100-120; about 280): a single round's damage is at the top of its
calibre band, so the real, slower rate would cut these units' damage by half or more, which the combat value forbids.
**Slower than real, kept:** the MLRS's and Smerch's ripples (M270: 12 rockets in 40-60 s; Smerch 12 in 38 s): at the
real pace a salvo would take 20-35 s of a 90 s fight; the Iskander launcher's two missiles (within a minute, 1.5 s
here).

**Shared with towers.** The towers' self-defence guns that use the vehicles' own `hmg_roof` and `mg_coax`
(headquarters, spawn bastion, missile battery, rocket battery, artillery emplacement) now fire the M2's and the PKT's
real cadence too, at the same damage a second. Tower weapons that inherit a changed vehicle weapon keep their own
rhythm: `tower_flak_30` (clip 46), `tower_ac25` (clip 10), `hq_flak` (change 1.21 s) and `mg_coax_ground` (cooldown,
clip and change) got their old values written in (no value changed). The towers' missiles are slower (section A).

### C. Real rates of the tower weapons (for the tower agent)

Researched here, not changed (tower weapons are MachineBrigade-bal's). The simulation carries at most 60 rounds a
second a mount; the vehicle weapons above keep their damage a second by solving the change after a real burst.

| Tower weapon | Real system | Real rate, burst, magazine | Game now |
|---|---|---|---|
| `c_ram_gatling` (+`_long`) | Phalanx M61A1 20 mm (C-RAM LPWS) | 4,500 rpm (75/s); bursts of about 1-2 s (60-150 rounds) until the threat breaks up; 1,550-round drum | 492 rpm x23 / 1 s |
| `tower_hmg` | M2 12.7 mm | 450-600 rpm, 5-10-round bursts, 100-round belts | 706 rpm x40 / 1.3 s |
| `tower_ac25` | M242 25 mm | 200 or 500 rpm; 300 ready rounds (Bradley) | 462 rpm x10 / 1.3 s |
| `tower_flak_30`, `hq_flak` | 2A38M twin 30 mm (Tunguska / Pantsir mount) | 4,060-5,000 rpm a mount; 83-150-round bursts | 667 rpm x46; 545 rpm x36 |
| `flak_quad` | ZSU-23-4 Shilka (4 x AZP-23) | 3,400-4,000 rpm; bursts of 3-5, 10 or up to 50 rounds a barrel; 2,000 rounds | 894 rpm x54 / 1.5 s |
| `bunker_hmg` | NSV / Kord 12.7 mm | 650-800 rpm, 50-round belt boxes | 968 rpm x39 / 1 s |
| `bunker_hmg_twin` | twin NSV | 2 x 650-800 rpm | 1,200 rpm x44 / 1.02 s |
| `mg_coax_ground` | PKT 7.62 mm | 700-800 rpm, 250-round belts | 631 rpm x32 / 1.2 s |
| `tower_agl` | Mk 19 40 mm | 325-375 rpm, 3-5-round bursts, 32/48-round belts | 3 rounds 0.2 s apart / 4.3 s |
| `turret_gun_120`, `_long` | Rh-120 L/44, L/55 with a loader | 6-10 rpm (a trained loader 6-8 s, bursts to 4-5 s) | 2.88 s; 3.31 s |
| `turret_gun_120_auto` | 120 mm with an autoloader (Leclerc 12 rpm, K2 15 rpm) | 4-5 s a round | 2.53 s |
| `howitzer_fixed`, `howitzer_cb`, `howitzer_ext` | M284 155 mm (M109A7); PzH 2000 for comparison | 4 rpm for 3 min, 1 rpm sustained; PzH 2000 10 rpm | 3.9 s x20 / 13 s; 5.3 s x20 / 21 s |
| `gun_155_twin_fort`, `gun_155_coastal`, `gun_155_twin_coastlr` | twin M284 155 mm | 4 rpm a gun | 2 rounds / 5.5-8.8 s |
| `bastion_gun` | twin 2A83 152 mm | 10-12 rpm a gun (autoloader) | 2 rounds / 5.16 s |
| `turret_rockets`, `turret_rockets_cluster` | BM-21 Grad 122 mm | 40 rockets in 20 s (0.5 s apart); 7-10 min to reload | 6 rockets 0.12 s apart / 7.78 s |
| `turret_thermobaric` | TOS-1A 220 mm | 24 rockets in 6-12 s (0.25-0.5 s apart) | 7 a salvo / 7.1 s |
| `atgm_post` | 9M113 Konkurs (9P135) | 2-3 rpm (20-30 s to reload a tube) | 12.1 s |
| `sam_post` | 9M317 Buk | salvos of 2 missiles 4-5 s apart, 4 on a launcher | 2 missiles 0.5 s apart / 5.73 s |
| `sam_battery`, `patriot`, `sam_battery_lrr` | MIM-104 PAC-2 | 4 on a launcher; two-missile ripples a few seconds apart | 2 missiles 0.45 s apart / 4.24-10.1 s |
| `sam_pac3` | PAC-3 MSE | 12 on a launcher; ripples a few seconds apart | 2 missiles 0.45 s apart / 3.52 s |
| `tamir` | Iron Dome Tamir | 20 on a launcher; launches 1-2 s apart in a salvo | 1 / 3.5 s |

### D. The bunker vehicle's dug-in mode

**Found on the way:** the old deploy animation never showed. `Spade_L`, `Spade_R` and `Plate_front` were not moving
parts to `ModelLibrary`, so the spawn merged their meshes into the hull (`MergeRigidParts`) and `VehicleView.Deploy`
turned empty transforms. The same was true of the far detail level.

**Model** (`Tools/blender/mb_p21_models.py`, replacing prompt 17's stand-in): a self-entrenching engineer hull (the
Strv 103's dozer blade, an engineer vehicle's push arms) with a low wide turret, the L7 105 mm with a thermal sleeve and
a coaxial MG. Every part that moves when it digs in is a `Deploy_*` pivot, which `ModelLibrary.DeployPattern` keeps as
its own rigid group at every detail level (and `frontier_kit` bakes as moving, so it casts no baked shadow on the hull):
- `Deploy_blade`: the dozer blade on its push arms; `Deploy_plate_l` / `_r`: armoured side plates hinged on the
  sponson edges, standing up beside the turret on the move (the mobile silhouette: a box with walls);
  `Deploy_spade_l` / `_r`: the rear earth spades; `Deploy_riser`: the turret's telescopic mount (the `Turret` rides it);
  `Deploy_berm`: the spoil bank round the scrape (earth banks, lumps, two courses of sandbags on the front bank).
- The bank is exported at **1 % scale**, so the cards, the impostor atlas and a vehicle on the move never show it;
  the far level's simplifier measures it at full size (`ModelLibrary.Lod`).

**Digging in** (`VehicleView.Deploy`, over the data's 3 s; packing up runs it backwards): the spades swing down and
back 125 degrees (first 35 %); the blade bites 6 degrees while the whole model sinks 0.8 m into its scrape and the bank
rises round it from the ground (15-70 %); the side plates fold out and down 95 degrees over the bank (45-85 %); last the
turret rises 0.75 m on its mount (70-100 %). Dug in, only the turret on its mount shows above a bank level with the hull
top: a low, wide pillbox where a tall walled vehicle stood. `ModelTests.BunkerVehicleKeepsItsDeployPartsApart` pins the
parts, the turret on the riser and the hidden bank.

**Footprint:** the blade and the plates make the hull 8.47 x 4.07 m (was 7.96 x 3.6), copied into `balance.json` from
`measure_hulls.py` (the collision capsule).

### E. Look-alike vehicles

Compared on the card renders side by side at about the default zoom's size (43 ground cards, then a closer sheet of 14).
The groups that read alike: the light tank and the battle tank (the same layout, smaller); the heavy tank, twin tank
and Titan (long green tanks with long guns; the Titan and the heavy tank the same size); the laser tank on the tank
destroyer's hull with a fat barrel; the shield carrier and the command vehicle (the same 8x8 box). Redrawn
(`mb_p21_models.py`), each after a real-world pattern:
- **Light tank:** an amphibious light tank (PT-76 / ZBD-05 lineage) with an unmanned 57 mm module (AU-220M) set well
  forward, a boat bow with a trim vane folded on the glacis, stern water-jet housings and a panoramic sight mast.
  Its `_hd` variant is the same builder. Length 4.91 → 5.17 m.
- **Titan:** a land battleship. The twin-140 mm turret moves 1 m forward and a superfiring rear turret on a raised
  plinth carries the heavy machine gun (`Mount_mg`, free yaw), clear of the main turret's sweep: the only tank with two
  turrets.
- **Laser tank:** a beam director instead of a barrel, a ball head on a yoke with a short telescope and a round window
  (the Rheinmetall / DE M-SHORAD look), and a power and cooling module (generator, radiator banks with fans, conduits)
  over the engine deck.
- **Shield carrier:** its emitter on a 5.6 m lattice mast with a glowing halo ring, capacitor drums on the roof.
- **Bunker vehicle:** section D (walls on the move, a pillbox dug in).
The heavy tank, twin tank, battle tank, tank destroyer and command vehicle keep their models: each now differs from its
look-alike by the other's redraw.

### F. Combat value

`CombatValueMeasure` on the whole roster, before and after, three seeds (13-15; one seed swung up to 50 % on the
aircraft's 4-minute runs): the median cell moved **2.3 %**; 14 of 120 cells (over 20 points) moved more than 10 %.
- **First pass, fixed:** at the real cadence some bursts front-loaded their damage (a whole burst lands while a target
  is in reach): anti-air vehicles +25-33 % on aircraft, the ZU-23 +30 %, the BMPT +12 %; the armoured car's 25 mm at
  200 rpm (a long even stream) made the light reference group weaker (the armoured car -13 %, the units fighting it
  +15-25 %). The second pass shortened those bursts (Gepard x16, Tunguska x20, ZU-23 x16, BMPT x10, GSh-30-2 x30,
  tail guns x25, the 25 mm at 500 rpm x6) and they came back within 10 %.
- **Left, and why:** aircraft against aircraft and on the 4-minute runs: the attack jet +34 % on air and +50 % on the
  long run, the fighter +18 % on air, the attack helicopter +18 % on the long run; the stealth fighter -46 %, stealth
  bomber -27 %, swarm carrier -21 % on the long run; the Iron Beam -25 % and the heavy bomber -22 % on air (small
  numbers). These are the slower missiles: aircraft live longer against missile anti-air and their own missiles are
  decoyed more. The owner asked for the speed; `CounterTests` hold; the testing phase's seed sweep should judge the
  aircraft. Also -12 % on the rocket technical's long run (its stretched ripple) and +11 % on the bunker vehicle with no
  anti-air (its wider capsule and the stronger reference group of the first pass; within noise).
- Towers were not measured (`TowerValueMeasure` is the tower agent's); their missiles are slower.

### G. Tests

Run once each: compile; `CounterTests` (15, pass); `MissileFlightTests` (pass, including the plume frames at the new
speeds); `CalibreTests`; `ModelTests`; `VehicleLodTests` (pass); `WeaponRhythmTests`, `WeaponTests`, `BigAttackTests`,
`ContentTests`, `Prompt17ContentTests`, `TheProcCoefficientFollowsTheWeaponsRhythm` (pass); `MuzzleAuditTests`;
`CardRenderTests`; the combat-value measure (section F). Failing, already on lead and not touched here:
`CalibreTests` (the towers' `flak_quad` 22 on the 23 mm band, `tamir` under `sam_pac3`), `ModelTests.RoundsLeave`
(heavy_aa, gunship_heli, fighter_jet), `ModelTests.EveryWeaponMountHasAMuzzleOnItsModel` (mobile_fortress's
`Muzzle_gun`), `MuzzleAuditTests` (36 tower and boss mounts; the new laser tank passes), `GearModelTests.AnOldSave...`.
`CardRenderTests.EveryCardHasAFreshPicture` now lists bunker_vehicle, light_tank, titan_tank, laser_tank and
shield_carrier: the lead renders the cards (ASSET_DEBT).

## 19T. Tower branches: two real choices for every tower (2026-09-29)

The owner's spec (Docs/prompts/tower-branches_vi.txt) sections A, B, D, E and F's tests, on lead bd814c9 / 2bcb306. The art (C.1,
C.2, C.4, C.6, C.7: branch models and modules, rank details, branch icons, LOD and Low versions) is the art agent's
(feature/tower-art, DECISIONS 19U); card renders and screenshots are the lead's after the merge. The Iron Dome (B.9) is prompt
20 L's and stays. Damage a round keeps the calibre scale, penetration and damage types (13, 14A); strength moves with rhythm,
magazines, reach, health and mechanisms. Raw files: `Docs/balance/*_branches*`.

### The three towers left from the balance pass (19B)

| Tower | Change | After (light / heavy / air DPS, or interception) | Target (19B / prompt 18 spec) |
|---|---|---|---|
| Rocket battery | Grad salvo 7.78 -> 3.35 s, blast 3.5 -> 4.5 m, x0.46 on heavy armour; cluster 3.2 s | 104 / 42 (cluster 107 / 44) | 110 / 45, more on groups and buildings |
| C-RAM | 2 -> 4 interceptors, 1.5 -> 0.6 s; Centurion 5, 0.35 s; Iron Dome as prompt 20 L | two MLRS for 60 s: 60 %, Centurion 90 %, Iron Dome 48 % (it reloads its six whole every 12 s: one salvo it stops whole) | most of a medium salvo |
| AA tower SAM post | Buk pair 5.73 -> 3.4 s at 60 m | 228 air | about 220, 60 m |
| AA tower flak | ZSU-23-4 back on the scale, 14 a round (prompt 20 had 22), 0.0671 -> 0.0324 s (same damage a second) | 88 / 18 / 305 air | the drone and swarm killer |

The Iron Dome's Tamir was sized 160 (its diameter in mm) in an AA-missile family scaled by warhead: size 1, so `CalibreTests` holds
(110 under the Igla's 150).

### A and B, what sets them apart (B)

A branch's model and icon come from its data's `"art"`: the art branch's `<tower>_a` / `<tower>_b` in the spec's A/B order
(`BranchArt`: the art's when it exists, else the tower's own, so nothing is missing before the art merge). Kept mechanisms (B.1-8)
got only their stale texts fixed. Remade (the ids that still describe their branch were kept):

| Tower | A | B |
|---|---|---|
| Gun turret | `gun_turret.long` Sniper gun: the 120 mm L/55 at 48 m (tank guns 32-38), 3.9 s, pen 4, x0.55 on light; no aircraft | `gun_turret.auto` 57 mm autocannon (AU-220): 70 a round (the scale), magazines of 6 at 0.5 s, pen 2, 40 m, hits the ground and the air; at an aircraft it loads its air-burst round (`"air"`: `gun_57_air`, fragmentation) |
| Rocket battery | `.cluster` as before | `rocket_turret.guided` (was `.thermo`): two GMLRS 227 mm (100 a round), 90 m, 20 m minimum, spread 0.8, x1.5 on artillery and structures, a 3 m blast |
| Emplacement | `.cb` counter-battery howitzer: goes for an enemy gun its radar just caught firing (a target priority x12 and a switch away from the current target, `CombatSystem.CounterBatteryTarget`), shows it 6 s, x1.25 on artillery | `artillery_emplacement.mortar` (was `.ext`): 2B8 240 mm (450 a round), 60 m, 8 m minimum, a 9 m blast, a slow high shell; lobbed, so it fires over walls |
| Heavy fortress | `.coastal` as before (72 m, opened by Leviathan) | `.bastion` Steel fortress: 4,340 HP and two 12.7 mm machine guns turning all round (`hmg_roof`, slot `mg`) for cars and drones up close |
| Patriot | `.pac3` interceptor: an APS of four `"heavy"` interceptors (72 m, 16 s to reload) that take only cruise and ballistic missiles (`DamageSystem.IsHeavyMissile`: their family, or a missile with a minimum range), the cruise-missile strike (`StrikeSystem.ShotDown`) and a boss's big-attack missiles (the big attacks' interception takes any APS); its SAMs slower (5.8 s: 164 air) | `.lrr` long-range radar: 100 m, 3.6 s (233 air), and every enemy aircraft within 140 m is seen by its side (`"revealAir"`, stealth too); no interceptors |
| Shield generator | `.bulwark` Shield dome: the tower's 25 m dome, 4,200 HP (it was a smaller 19 m one) | `shield_tower.ward` Tower shields (was `.pulse`): no dome; every tower of its side within 28 m carries its own 1,200-HP shield (`"wards"`, scaled by the generator's health), back 6 s after its last hit. It stops rounds aimed at the tower (direct hits and piercing), not the blasts of shells, rockets and bombs round it; energy goes through; a tower under a dome is covered by the dome only (`DomeSystem.StepWards`, `AbsorbWard`) |
| CP relay | `.hardened` CP relay: steady CP as before | `cp_relay.loot` Loot depot (was `.express`): no steady CP; an enemy vehicle destroyed within 40 m pays its side 20 % of the price, the kill's own refund and this together never past prompt 8's 45 % cap, the nearest depot only (`EconomySystem.PayLoot`) |
| MG bunker (kept) | twin | flame: its blast 2.5 -> 4.5 m (a flame fills the lane; the rush below) |

### Each wins somewhere, none everywhere (F.2)

`TowerValueMeasure` (a tower alone against ladders of attackers of rising CP; worth in vehicle CP, three seeds; now with a
"shelling" ladder of artillery and a "heavy" one of heavy tanks) and `BranchMeasure.PrintMechanismScenarios` (the fights a
ladder misses). The better branch in each case, the number in brackets the other's:

| Tower | A wins | B wins |
|---|---|---|
| Guard tower | light 5.51 (5.42), air 1.98 (1.16) | tanks 5.35 (5.17), heavy 5.70 (5.65) |
| MG bunker | light 13.5 (1.0), air 4.0 (1.3) | a rush of six cars within 5 m: 1,770 damage (1,582) |
| AA tower | light 13.4 (0.9) | air 19.2 (5.4) |
| ATGM tower | heavy 7.55 (6.80) | light 5.64 (4.79), tanks 8.60 (8.02), air 2.99 (1.16) |
| Gun turret | tanks 12.9 (11.1), heavy 9.1 (6.2) | light 13.5 (11.6), air 5.5 (1.7), the rush 1,132 (670) |
| Rocket battery | light 12.0 (4.9), tanks 11.1 (5.5) | shelling 15.0 (10.3), guns standing at 70 m 2,400 (0) |
| C-RAM | air 6.4 (3.2); MLRS rockets stopped 90 % (48 %) | shelling 6.46 (6.13), reach 60 m, shells 50 % |
| Emplacement | shelling 14.6 (10.2), tanks 11.3 (10.6) | light 10.9 (10.5), over a wall into a yard (the test) |
| Heavy fortress | guns standing at 70 m 7,040 (0) | heavy 23.1 (15.5), air 6.1 (2.1) |
| Patriot | a base under two Iskanders: 0 damage taken (16,612) | air 19.2 (16.7), aircraft seen at 140 m |
| Drone hangar | tanks 10.9 (7.0), shelling 47.4 (10.3) | light 4.62 (3.33) |
| Shield generator | a barrage every 8 s: towers lost 3,735 (4,505) | three tanks, a tower each: 521 (1,281) |
| CP relay | quiet, 3 minutes: 14 CP (0) | attacked by cars every 12 s: 50 CP (42, the kills' refunds included) |

EW tower, dragon's teeth and minefield keep their mechanisms (the spec's B.4-6) and do no damage the ladder can see (a ladder's
attackers stop short of the mines round the field); `TowerBranchTests.TheTwoBranchesOfEveryTowerDifferInTargetsReachOrMechanism`
checks every pair differs in what it hits, its reach band or a mechanism.

### The AI (A.5) and how often it picks each (F.3)

`BranchChoice`: each branch scored on paper against the deck it will face: its guns' damage a second on the deck's cards
(armour or air, the damage table, penetration), plus its mechanism against what the deck brings (interceptors by what the
deck fires, dome against area fire, tower shields against direct fire and heavy armour, loot against cheap light vehicles, the
radar against aircraft and stealth, counter-battery against artillery, mines by armour, jamming, obstacles), read against its
score on "a deck like any other" (all the decks the commanders draw by roles, Normal and Hard, 16 seeds), so the pick follows
how this deck differs from the usual one. A general's style weighs its branches (`"tower.branch"` weights in balance.json
`base.ai.styles`: Varga the sniper gun and top attack, Orlov counter-battery and guided rockets, Sen the swarm and drone
jammer, Quạ Đen the SAM post, radar and Iron Dome, Aurel the PAC-3, shield dome and steel fortress). The enemy's base takes it
from Normal up (`BaseLoadout.ForAi(..., against)`, prompt 20's hook). The player's branches stay the player's paid choice:
Auto-arrange places towers, it does not change a branch.

Picks over 121 decks (the sample deck and 40 seeds of enemy decks at Normal, Hard and Very Hard, each general's style in turn),
A / B: fortress 24 / 76, Patriot 52 / 48, ATGM 43 / 57, gun turret 39 / 61, AA 32 / 68, EW 58 / 42, teeth 28 / 72, mines 49 / 51,
C-RAM 64 / 36, hangar 57 / 43, rocket 23 / 77, MG 49 / 51, emplacement 63 / 37, guard 52 / 48, shield 43 / 57, relay 28 / 72.
Every branch 23 % or more (the spec's "about 25 %").

### Interface (D)

- `BranchLines.Picker`: the rank-7 choice on the Base screen and the detail page shows both branches side by side: the branch's
  render (its own once the card renders exist, the tower's until then), icon, role line, "Pick it when", and the facts where
  it differs from the other, from the data (reach, what it hits, interceptors, dome or tower shields, loot, CP, radar,
  counter-battery, over walls, mines, jamming, health).
- Every branch has a "when to pick it" line (`branch.<id>.when`), the role lines were rewritten where stale (the drone hangar's
  and C-RAM's numbers after 19B), names and short names for the new branches.
- The Guide tab of a tower has a block for each branch: role, when to pick it, what sets it apart, and its generated
  behaviour lines (`UnitLines.Behaviour`, prompt 13 G) with its own strong / weak summary.

### Migration (E)

Roster version 4 (`CardMerges.RenamedBranches`): `rocket_turret.thermo` -> `rocket_turret.guided`, `artillery_emplacement.ext` ->
`artillery_emplacement.mortar`, `shield_tower.pulse` -> `shield_tower.ward`, `cp_relay.express` -> `cp_relay.loot` (the same A/B
slot); `gun_turret.long/.auto`, `missile_battery.pac3/.lrr`, `heavy_turret.bastion` and `artillery_emplacement.cb` kept their
ids. A player with a branch chosen on a reworked tower (gun turret, rocket battery, emplacement, Patriot, heavy fortress,
shield generator, CP relay) gets one free change on it (`PlayerProfile.FreeBranchSwap`, spent by `TryChooseBranch`) and a
once-only notice on the menu listing those towers and their branches (`TakeBranchNews`). Ranks and tower equipment are
untouched (equipment is kept by tower, not branch).

### Tests

`TowerBranchTests` (new): every pair differs in kind; the 57 mm hits a helicopter with its air-burst round and the sniper gun
cannot; the mortar lands inside a walled yard where a direct-fire gun cannot; the counter-battery howitzer turns from a nearer
tank to the gun that fired; the PAC-3 shoots down a boss's missile (the Doomsday train's) and a cruise-missile strike and no
MLRS rockets; the long-range radar shows a jet at 130 m and the PAC-3 does not; the steel fortress's two all-round guns; tower
shields are each tower's own, come back, let energy through and never add to a dome; the loot depot pays near kills and stays
under the cap; the AI picks by the deck; the save migrates with one free change and one notice. The Iron Dome's rounds stay
`Prompt20TowersMapsTests`'s. Updated: `Prompt17ContentTests` (the shield branches), `TowerIconTests` (a branch may show its own
art's icon), `UiLanguageTests` (data placeholders are not words), `CombatValueMeasure`'s rocket list. Run once:
`TowerBranchTests`, `Prompt20TowersMapsTests`, `Prompt17ContentTests`, `CounterTests`, `CalibreTests`, `LocalisationScanTests`,
`UnitLinesTests`, `TowerRosterTests`, `TowerCardTests`, `BaseTests`, `BaseDefenceTests`, `ContentTests`, `ApsTests`,
`BigAttackTests`, `StringsTests`, the migration tests, `AirAndTowerTests`, `SupportTextTests`, `BaseScreenTests`, `ArmourTests`,
`WeaponTests`, `EconomyTests`, `BaseStrengthTests`, `MuzzleAuditTests`, `TowerIconTests`, `UiLanguageTests`, `CardRenderTests`,
`TowerGearTests`.

Failing and not from this job: `CardRenderTests` (renders to redo: the new branch ids, and boss models changed on lead),
`MuzzleAuditTests` (boss mounts: behemoth, fenrir...), `TowerIconTests` (`coastal_battery` has no icon), `UiLanguageTests` (proper
names such as Leviathan and Icarus), `ArmourTests` (`casemate_155`, `naval_127`, `naval_100` are written `{"id"` without the
space its text split expects), `TowerGearTests` x3 (sabot rounds fit the Patriot; they fail on the balance pass's tree over
319a285 too, so not from this job; not diagnosed), `BaseTests.TheAiStopsFeedingVehiclesIntoTowers` (a balance check, run
because the measures ran with MB_BALANCE=1: 14.9 % against 12.9 %, the stronger towers of 19B and this pass).

### Left

- The art agent's models and icons (`<tower>_a` / `_b`, DECISIONS 19U) wire in by name; until then branches look like their
  tower. The steel fortress's two guns share the tower model's one `mg` muzzle until its model brings two.
- Card renders for the four new branch ids and every branch's art, and the screenshots of every branch and rank (the lead's).
- FPS of a base full of branch towers on a low-end phone (F), the image-diff test of A against B and ranks 1/3/5/7 (F, the art).
- A branch-pick measure against human decks, and the Guide's per-branch page as its own tab if the owner wants one.

## 19U. Tower-branch prompt C: branch models, rank details, branch icons (2026-09-29)

Art side only (C.1, C.2, C.4, C.6, C.7 of `Docs/prompts/tower-branches_vi.txt`). No sim data or behaviour changed:
`balance.json` is untouched, so the balance pass (section B, in MachineBrigade-bal) can rename and rework the branches.

### How a branch picks its model and icon (the hook for the balance pass)

- **Letter = data order.** A tower's branch defs are lettered by their order in `balance.json` (`TowerCards.Branches`):
  the first is A, the second B. That is the spec's A/B order, so keep it when the branches are rewritten.
- **Model.** A branch entry that names no `"model"` of its own wears `<tower model>_<letter>` when that model ships
  (`TowerArt.ModelFor`, used by `VehicleView`, the detail preview, `CardRenders` and the LOD tests). A branch entry that
  names its own `"model"` keeps it: that is the data override (the existing `inherits` hook), so no new field was needed.
- **Icon.** `TowerIcons.For(<branch id>)` returns `<tower icon>_<letter>` when that icon is drawn, else the tower's
  icon. The Iron Dome's `t_irondome` is now `t_cram_b` (`Prompt20TowersMapsTests` follows).
- `TowerArt.Learn(catalog)` runs in `GameContent.LoadCatalog`, so every loaded catalog sets the letters.
- A third branch (letter c) finds no model or icon and shows the tower's until one is made or named.

### Id table

| Tower | Letter | Branch now (spec) | Model id | Icon id |
|---|---|---|---|---|
| guard_tower | A | guard_tower.watch (Observation) | guard_tower_a | t_guard_a |
| guard_tower | B | guard_tower.nest (25 mm gun nest) | guard_tower_b | t_guard_b |
| mg_bunker | A | mg_bunker.twin (twin MG) | mg_bunker_a | t_mg_a |
| mg_bunker | B | mg_bunker.flame (flame bunker) | mg_bunker_b | t_mg_b |
| aa_turret | A | aa_turret.flak (quad flak) | aa_turret_a | t_aa_a |
| aa_turret | B | aa_turret.sam (SAM post) | aa_turret_b | t_aa_b |
| ew_tower | A | ew_tower.drone (drone jammer) | ew_tower_a | t_ew_a |
| ew_tower | B | ew_tower.spoof (radar spoofer) | ew_tower_b | t_ew_b |
| dragons_teeth | A | dragons_teeth.hedgehog (steel hedgehogs) | dragons_teeth_a | t_teeth_a |
| dragons_teeth | B | dragons_teeth.wire (wire) | dragons_teeth_b | t_teeth_b |
| minefield | A | minefield.at (anti-tank) | minefield_a | t_mines_a |
| minefield | B | minefield.scatter (scatter) | minefield_b | t_mines_b |
| atgm_tower | A | atgm_tower.top (top attack) | atgm_tower_a | t_atgm_a |
| atgm_tower | B | atgm_tower.multi (multi-role) | atgm_tower_b | t_atgm_b |
| c_ram | A | c_ram.centurion (close-in C-RAM) | c_ram_a | t_cram_a |
| c_ram | B | c_ram.dome (Iron Dome) | c_ram_b | t_cram_b |
| gun_turret | A | gun_turret.long (-> 120 mm sniper) | gun_turret_a | t_gun_a |
| gun_turret | B | gun_turret.auto (-> 57 mm autocannon) | gun_turret_b | t_gun_b |
| rocket_turret | A | rocket_turret.cluster (cluster rockets) | rocket_turret_a | t_rockets_a |
| rocket_turret | B | rocket_turret.thermo (-> guided long-range rockets) | rocket_turret_b | t_rockets_b |
| artillery_emplacement | A | artillery_emplacement.cb (counter-battery howitzer) | artillery_emplacement_a | t_artillery_a |
| artillery_emplacement | B | artillery_emplacement.ext (-> 240 mm mortar) | artillery_emplacement_b | t_artillery_b |
| heavy_turret | A | heavy_turret.coastal (long-range coastal gun) | heavy_turret_a | t_fortress_a |
| heavy_turret | B | heavy_turret.bastion (-> steel fortress) | heavy_turret_b | t_fortress_b |
| missile_battery | A | missile_battery.pac3 (PAC-3) | missile_battery_a | t_patriot_a |
| missile_battery | B | missile_battery.lrr (long-range radar) | missile_battery_b | t_patriot_b |
| drone_hangar | A | drone_hangar.lancet (Lancet) | drone_hangar_a | t_hangar_a |
| drone_hangar | B | drone_hangar.swarm (swarm) | drone_hangar_b | t_hangar_b |
| shield_tower | A | shield_tower.bulwark (-> shield dome) | shield_tower_a | t_shieldgen_a |
| shield_tower | B | shield_tower.pulse (-> tower shields) | shield_tower_b | t_shieldgen_b |
| cp_relay | A | cp_relay.hardened (-> supply relay) | cp_relay_a | t_relay_a |
| cp_relay | B | cp_relay.express (-> spoils depot) | cp_relay_b | t_relay_b |

The landing pad's branches (`airfield.*`) are not in the spec and keep the pad's model and icon.

### What each model gives the mechanics

Every branch model keeps its tower's pivots and muzzles (`Turret`, `Radar`, `Mount_*`, `Muzzle_*`), so the current
weapons fire from the right place; `TowerBranchArtTests` checks each branch def's weapon slots against its model.
Points for the balance pass:
- `heavy_turret_b` (steel fortress): two small turrets at the roof's front corners on `Mount_gun` and `Mount_gun.001`
  with `Muzzle_gun` / `Muzzle_gun.001`, free to turn all the way round. Give the two MG mounts slot `gun`.
- `gun_turret_b`: two barrels (`Main_cannon`, `Main_cannon_2`), fired in turn by the view; `gun_turret_a` one long gun.
- `artillery_emplacement_b`: the tube is `Mortar_tube*`, so the runtime raises it as a mortar (high lob).
- `aa_turret_b`: `Muzzle_missile` and `.001` to `.003` on two two-tube boxes, a light MG on `Muzzle_main` (the SAM
  post's secondary). `aa_turret_a` has no missile box any more (the flak branch has no missile).
- `atgm_tower_b`: four tubes, `Muzzle_missile` to `.003`, and a small `Radar` on the launcher.
- `mg_bunker_b` has no ATGM on the roof (the flame branch has `secondary: []`); `mg_bunker_a` keeps it.
- `c_ram_b`: `Muzzle_main` and `Muzzle_gun` at the middle of the tilted launcher's face; the launcher is `Launcher_*`,
  so it elevates as a launcher.
- `shield_tower_b`: `Emitter` is now the low central orb (3.85 m); the eight small node orbs carry no pivots. The
  beams to each tower are an effect (C.3).
- `drone_hangar_a` / `_b`: `Muzzle_door_l` / `Muzzle_main` at the Lancet on its catapult / above the swarm rack.

### Rank details (C.2)

- Made at run time (`TowerRankDetails`), not in Blender: rays from four sides find the tower's static walls (never the
  turret or anything that turns), and a wall only counts when two side rays hit it too (not a railing or a leg). Rank
  bars (one a rank, up to six) stack on the side walls in Hazard yellow; from rank 3 an Armor plate stands in each
  quadrant (on the diagonal on round or chamfered bodies, beside the bars on square ones), thicker from rank 5 with a
  second layer and bolts. A low or open model (minefield, wire) wears the bars on a marker post at its corner.
- One renderer, two materials, no shadow casting; hidden at the impostor level and on the wreck. Meshes are cached per
  model, rank and leanness; the measure runs once per model.
- Rank source: the player's side from the profile (`PlayerProfile.Rank`), the other side from its HQ level
  (2 x level - 1: 1, 3, 5), the menu's backdrop battle none. A branch shows rank 7 at least (six bars, heavy plates).

### Low graphics and LOD (C.6)

- The shared runtime LOD (`ModelLibrary.EnsureLod`) and the impostor atlas cover the branch models like every other
  model; `VehicleLodTests` now includes them (every branch model within 75 % of its triangles far away). Three models
  were changed to get there: the SAM post has a concrete revetment instead of sandbags, the hedgehogs are bevelled
  girders, the wire is loops on round posts.
- The reduced version for Low graphics is that far level, not a second file: each branch's signature part is 0.4 m or
  more, so it stays in the simplified level (the test checks that the two branches of a tower differ there too).
  On the Low preset (`TowerArt.Lean`: low shadows and half scenery) the rank details drop their bolts and second plates.
- Draw calls: a branch model has about as many parts as its tower (they merge the same way); rank details add one.

### Tests (run once each)

`TowerBranchArtTests` (3, new), `ModelTests`, `VehicleLodTests`, `TowerIconTests`,
`Prompt20TowersMapsTests.TheCRamBranchesAreTheIronDomeAndTheCloseInCenturion`: 42 of 46 pass. The four failures were
already on lead: `ModelTests.RoundsLeave` (heavy_aa, gunship_heli, fighter_jet), and `TowerIconTests` on
`coastal_battery` (no tower icon mapped; unrelated to this branch). `CardRenderTests.EveryCardHasAFreshPicture` was not
run: it will list the 32 branch cards until the card pictures are rendered again.

### Shared edits (merge by hand if they conflict)

`Tools/blender/build_assets.py`, `Docs/art/models.json`, `Icons` (31 new icons, `t_irondome` renamed `t_cram_b`),
`TowerIcons`, `GameContent.LoadCatalog`, `MatchRunner` (rank provider, Lean), `VehicleView` (model id, rank details),
`MenuScreen.Detail` (preview), `CardRenders.Cards`, `VehicleLodTests.FieldableModels`, `TowerIconTests`,
`Prompt20TowersMapsTests`. New: `Tools/blender/mb_tower_branches.py`, `Game/Rendering/TowerArt.cs`, 32 GLBs.

5-seed kill times and win rates of every boss at each difficulty (main 5-8 min, mini 1.5-3 min on Normal); the stuck
detector round the enlarged ground bosses, Kronos on the open-pit route and Ixion's charge; FPS with Moloch's and
Daedalus's spawns; the suites (muzzle audit and model tests on the new and rebuilt models, card counts, Boss Rush).

**Lead note on the tower-branch merge (2026-09-29).** The art agent's `TowerArt` (a branch wears `<tower>_a`/`_b` by its order in balance.json, and its rank details) was kept in `VehicleView`, `TowerIcons` and `TowerIconTests`. The branch agent's `BranchArt` resolves to the same ids through each branch's `"art"` field and stays for the air-dropped towers. The flak branch is back at 14 a round with a faster rhythm, on the calibre scale. Three `TowerGearTests` fail since the balance pass (8ec75eb): ground-target gear fits the AA tower's SAM branch and the Patriot. Weapon inheritance and the roof MG (`targets: All`, which counts as air-only on a secondary mount) were checked and are not the cause. Next suspects: mount order (mount 0 counts as the main weapon in `TowerFit.Of`), and whether the AA tower now has a ground-only gun for its 45/15 ground target. If it does, the tests' "no gun for ground targets" expectation is out of date. Listed for the testing phase.

## 20S. Prompt 21 part 1: the Sandbox (2026-09-29)

Prompt 21 sections A-G and part 3's cheap checks; part 2 (both languages for the whole game) is another agent's. The
owner's note: towers and structures can be placed for testing, with their rank and rank-7 branch.

### Shape

- **The scenario is the truth.** `Sim/Sandbox/SandboxScenario` holds the map, weather, night, fog of war, the bosses'
  difficulty, a time limit, both sides (AI, CP, cooldowns, immortal, deck, supports, base) and the units (kind, side,
  place, heading, rank, equipment, elite, health, ammunition, altitude tier, immortal, a boss's phase, broken parts, big
  attack off, escorts off), plus pass conditions. `SandboxBattle` (an `IGameMode`) builds the battle from it.
- **Setting up does not step the battle.** The editor's changes are mirrored onto the standing field (everything but
  the bases taken off and placed again, views too). **Run and Reset rebuild the scene** from the scenario, like a
  checkpoint's replay: spawning during set-up uses entity ids and random draws that a fresh battle would not, so running
  the mirrored field would not be the scenario's battle. The cost is a loading curtain on Run (the price of C.6-C.7).
- **Every control is journalled.** A control (orders, immortal, CP, cooldowns, a support called, every boss tool, the
  difficulty) is queued and takes effect at the start of the next step, stamped with it; a replay feeds the journal in
  at the same steps. Units are named by entity id, which a rebuilt scenario gives out the same way. Speed and pause only
  change how many steps a frame takes (`SimClock`), never a step.
- Headings are degrees (0 north, clockwise), snapped to 15 degrees unless free; places are kept to the centimetre;
  floats are written round-trip, so a saved scenario read back is the same scenario (`ToJson` has a fixed key order).
- **Format version 2.** Version 1 is defined as the first draft (map, seed and units, the heading in radians under
  "h"): it opens, upgraded, and missing fields take their defaults. A newer game's file is refused rather than misread.
- Share codes: `MBS2.` and the JSON deflated in URL-safe base 64. An imported code (and a sample) is fitted to the
  player: a locked unit is replaced by an allowed one from the same tab, then the same class, then the nearest price (a
  tower by a tower of its size, an aircraft by an aircraft). If nothing of its kind is unlocked, the unit is left out.
  Each change shows as a toast.
- Rank and equipment reach the battle through `SimWorld.SpawnBoosted` (one unit's boost, whatever its side's): none,
  a **suggested set** (one Epic piece a vehicle slot, rolled from the unit id, the same on every device; towers get
  none), or the player's own loadout (it differs between players, so a shared code with "yours" fights with the
  reader's gear).
- The flat test range is built in code (`SandboxMaps.Flat`, 300 m, no props); its metre grid (10 m, heavier every 50 m)
  is drawn by the overlays. Night is the game's night weather, so night replaces the weather.

### Placement (B.4) and the owner's towers

- Ships only on the sea: snapped onto the nearest lane (refused on land, or on a map without a sea).
- Towers and structures: on a free hardpoint that takes their size, snapped to it and facing as it does (8 m reach);
  anywhere on the flat test range; anywhere in the internal build. The picker lists the tower; its rank-7 branch
  (DECISIONS 19T) is chosen on the unit from rank 7 (the unit's def becomes the branch; under rank 7 it goes back).
- Aircraft enter at their flying height (the simulation's own). An altitude-tier boss placed at a tier is taken out of
  its opening orbit and forced to that tier once it has left orbit.
- The ceiling (B.10): 64 ground vehicles and 12 aircraft a side (towers count against neither). The internal build
  only warns past it; the player version stops there. FPS at the ceiling is for the testing phase.

### The two versions (A)

- Internal = the editor or a development build (`-mb-sandbox-player` shows the player version there). Everything is
  offered, towers go anywhere, and the internal overlays (hit boxes, routes, stuck vehicles, the AI's buying scores)
  are offered. A player build is not a debug build, so they are never offered there; the code is shared.
- Player version: open once the last chapter switched on is done (`BossHunts.FullOpen`); before that the Operations
  tab shows it locked, with the condition. It offers unlocked cards, their elites, a tower's branch once opened, the
  bosses and mini bosses beaten, never one of a chapter switched off, and the ships and escorts of a beaten boss.
  Beaten bosses are recorded from now on when one dies in a campaign mission or the Boss Hunt (PlayerPrefs
  `mb.sandbox`); every boss of a mission already won counts too.
- **Nothing pays or counts:** the session has no outcome (so no result card, reward, crate or star), daily challenges
  are suspended during the battle, items are neither taken into it nor used, and the player's arsenal, discounts and
  doctrine stay out. The game has no telemetry sender yet: the battle carries `ModeTag` "Sandbox" and
  `SandboxSession.TelemetryTag` for the day one is added (balance telemetry must drop tagged battles).
- Entry: a card with the challenges on the Operations tab (prompt 6's grouping). The Guide (the combat legend page)
  has a Sandbox section, and a short guide shows on the first visit.

### AI and controls (C)

- Full AI: the commander AI (Hard). It buys from the side's deck (or the kinds already placed when the deck is empty)
  and calls supports. Fighting AI: the tactical AI, which buys nothing. Standing still: no AI.
- Hold position is a Sandbox state: the unit drops any move an AI gives it each step and still turns and shoots. "Back
  to the AI" releases it. Units of both sides take orders. Unlimited CP is topped up every step; cooldowns off clear
  the side's ready times every step.
- In the runner, `SandboxController` decides the steps a frame and owns taps (place, select, move, orders, a
  support's point) and drags from a selected unit (turn). The camera no longer follows the fight on its own here.

### Measuring (E, F)

- `SimWorld.HitLog` (null in every other battle) reports each hit's face, penetration multiplier (the ✓ ~ ✕ mark is
  `Matchup.Verdict` of it) and what got through. `SandboxStats` sums damage dealt and taken by type, rounds through and
  bounced, kills and the time to make them, lifetimes, and a 5-second real DPS. Combat value is the data's (prompt 13).
- Saved scenarios with checks ("win" within N s, "noStuck", "survive") in `Tests/EditMode/Scenarios` run in
  `SandboxTests.SavedScenariosPassTheirChecks`; "Save as test" writes there from the editor (a development build writes
  beside its saves). `SandboxLab.Run` is the headless runner the measures can call. The A/B screen compares Blue's
  equipment sets; `SandboxLab.Compare` also takes two catalogs (the data before and after a change) in tests.
- Duels over many seeds and A/B run one battle a frame so the screen keeps drawing.

### Tests

`SandboxTests` (13; run twice: 10/13, then 12/13. Run 1 found a bad share code throwing Mono's `IOException`, now a
`FormatException`, and two over-strict checks; run 2's one failure read the tier before the shift ended, fixed and
checked with a Sim-only probe, not re-run in Unity): placing and turning, with the
heading kept into the battle and the set-up mirror; towers on hardpoints, anywhere, and their branch at rank 7;
copy, move, delete, formations and undo; the ceiling; the same scenario and journal twice (and through the exported
replay); the controls; save and load, a code, and a version-1 file; the boss tools (parts, big attack, phase, escorts,
main and mini swap, tiers); overlays against the data; the player version's limits, a code's stand-ins and no pay-out;
duel and A/B; the scenario suite; the words in both languages with named parameters.

### For the testing phase

FPS and tick time at the ceiling (64 + 12 a side) on a low-end phone; the screen on a phone and a tablet at both text
sizes; a play-through of every tab, tool and overlay; how long Run takes to load.

### Shared edits (merge by hand if they conflict)

`SimWorld` (now partial), `DamageSystem` (the hit report), `ConquestAi` (buying scores), `Strings.Get/Has` (the
Sandbox's table), `MatchSettings.GameModeKind` (Sandbox, last), `ModeSessions.Create`, `MatchRunner` (seed, map,
weather, boosts, discounts, items, the controller, steps, camera, boss pan, beaten bosses, item use), `DailyMissions`
(Suspended), `MenuScreen.Operations` and `.Legend`. New: `Sim/Sandbox/*`, `Sim/SimWorld.Sandbox.cs`,
`Sim/AI/ConquestAi.Sandbox.cs`, `Game/Match/SandboxSession.cs`, `Game/Match/SandboxController.cs`,
`Game/Hud/SandboxScreen*.cs`, `Game/Hud/SandboxText.cs`, `Game/Hud/MenuScreen.Sandbox.cs`,
`Game/Views/SandboxOverlays.cs`, `Resources/UI/Sandbox.uss`, `Tests/EditMode/SandboxTests.cs`, `Tests/EditMode/Scenarios`.
## 20L. Prompt 21 part 2: Vietnamese and English for the whole game (2026-09-29)

Sections H to L of `Docs/prompts/prompt21_vi.txt`. The audit is `Docs/localization-report.md`, the terms
`Docs/glossary.md`.

- **The tables stay in C#.** No Unity Localization package: the 4,300 entries are `key → (en, vi)` in seven tables
  (`NameText` makes eight), the checks read them directly, and a language is one static flag. `Strings.Entries` and
  `Strings.Keys` list every table in the order `Strings.Get` reads them.
- **Named placeholders, named at the call site.** Every `{0}` became a name (`{count}`, `{seconds:0.#}`, `{card}`),
  chosen from the text around it and the argument passed, by hand where that was vague. A text with one placeholder
  takes one value (`Strings.Format(key, value)`); several are passed as pairs (`Strings.Format(key, ("card", a),
  ("size", b))`). Binding by order was rejected: in 19 texts the English order was not the argument order, and names at
  the call site make every binding visible. Without the positional overload, the compiler finds every call with two or
  more values. `{{` and `}}` are braces; an unknown name stays in the text so the screen scans show it.
- **Plurals.** `{count|# coin|# coins}` picks by the value (1 or "1" is singular), `#` is the number. English only;
  Vietnamese writes `{count} xu`. `EnglishCountsUseThePluralForm` stops a new "{count} coins".
- **Numbers.** `Strings.Culture` is the invariant culture for English and a copy of it with "." grouping and ","
  decimals for Vietnamese, built by hand rather than `CultureInfo("vi-VN")`: every platform (IL2CPP, invariant
  globalisation) formats the same way. `Strings.Num` writes whole numbers grouped (`#,0`) and fractions as `0.##`; filled
  whole numbers are grouped too. `Kit.Culture`, `UnitLines`, `BranchLines`, `SupportLines` and `CombatIcons` use it.
- **Units.** Seconds are "s" in English and "giây" in Vietnamese texts, "/s" in the HUD's rates in both; metres, mm and
  CP are the same in both; a percentage is "25%" in both (the texts had both spellings).
- **Names (prompt 22).** The story's Vietnamese names are written `{@id}` and filled from `NameText.Table` when a text is
  read (`{@map.id}` would take any key), so prompt 22 renames each one in one entry. The other proper names stay
  inline; `NameText.Kept` lists them and replaces the allow-list line of section 10, which the checks no longer read. The
  generals' call signs (Anvil, Winter, Maelstrom, Queen, Raven, Sol, Titan, Iron, Hawk) are names too.
- **One word for a boss in Vietnamese: "boss".** The owner writes "boss", "boss chủ lực" and "mini boss" in the brief (the Sandbox
  agent works from it), so "trùm" became "boss" except in the mode's name, Săn trùm.
- **One name per map.** The map table of prompt 10 wins: the story's Red Rock, Whiteout (pass), Skyhold, Launch Site and
  Orbital Gate became Redrock Canyon, Whiteout Pass, Skyhold Airbase, Icarus Launch Site and Orbital Gateway; Tầng Mây,
  Skyhold, Đá Đỏ, Ashfield, Ironport, Dunebreak, Frostpeak and "Thành Phố Metro" in Vietnamese became the table's names.
  Where a full name read badly ("Skyhold Airbase, the air base he flies from"), the sentence was reworded.
- **Boss subtitles.** Translated, and in title case in English as the brief writes them ("Icarus · Orbital
  Spacecraft"). A boss's card (`unit.`) and boss bar (`boss.`) show the same subtitle; where they differed, the card's
  won (Argus · Scout Airship, Locust · Drone Tender, Ixion · Giant Wheel). In title case two subtitles became old
  boss names that prompt 20 retired, so they are Roc · Flying Headquarters and Charybdis · Assault Hovercraft. Caspian is
  "Tàu bay sát mặt nước".
- **Switching in a battle relabels; the menu still reloads.** Reloading a battle restarts it, so the pause menu's
  switch (English / Tiếng Việt, as in the settings) saves the setting and `Relabel` rewrites the HUD in place. A text
  that is a table text in the old language (as it is, in capitals or highlighted) becomes the new one. A filled text is
  matched against its old template and filled again, its numbers written the new way. A text joined from table texts
  ("A · B") is translated part by part. Texts the HUD refreshes itself follow on their next update. The menu keeps its
  reload, which rebuilds every screen at once.
- **Tight spots (K).** The layout checks also run in English at 16:9 and 4:3 and in English Large. Four gear pieces got
  shorter English names (Tungsten Core, Carousel Loader, Halon System, Camo Net), because one long word broke in the
  gear card in Large text; the thermobaric launcher's short name is TOS-1A, the system it is modelled on. The branch
  picker shows short names and stacks its cards in Large text; the legend's cells widen in Large text.
- **Screenshots wait.** `UiShots -mbShotsSet l10n` shoots the main screens in both languages at the four shapes. It
  needs a run with graphics, and the emulator was running (the OpenGL crash in CLAUDE.md), so it is left for the testing
  phase; the report lists the screens.
- **The owner's all-English Base screen** is not in the current code (every `camp.*` text has both languages; the scan
  found only "map"). The likely cause is Auto on an English device; the screen scans now fail on any mixed screen.
- **Merge notes (the Sandbox branch, p20b).** Its `Strings.Format` calls with two or more values need names (they no
  longer compile); its `{0}` texts, English "{n} units" plurals and English words in Vietnamese fail `L10nTests` and
  `UiLanguageTests`, which list them. `Strings.Vietnamese` is still a plain flag; a screen built once and kept must
  be relabelled like the HUD (`Relabel.Apply`).
- **The join with the Sandbox (feature/p21-join).** Its texts already used named placeholders through its own
  `SandboxText.Format`, which now calls `Strings.Format` (language number format, plurals, names); `SandboxText.Number`
  uses `Strings.Culture`; `Strings.Entries` lists `SandboxText`, so every scan covers it. Its English counts take the
  plural form, its percentages read "25%", and its Vietnamese has no English left: tick is "nhịp", seed "mã trận",
  replay "bản ghi trận", test "bài kiểm tra", hardpoint "ô đặt tháp" (the glossary's Sandbox table).
- **Tests (run once, then after fixes):** `L10nTests`, `L10nSwitchTests`, `LocalisationScanTests`, `UiLanguageTests`,
  `StringsTests`, `SupportTextTests`, `UiLayoutTests`, `BaseScreenTests`, `BaseLayoutTests`, `KitInteractionTests`,
  `Prompt20CampaignTests`, `InActionTests.RangeReadoutsAreInBothLanguages`.


## 20V. Play-test 5: visuals and models (2026-09-29)

The owner's play-test 5 items marked [C] (`Docs/prompts/requests_vi.md`), and the coordinator's added item: every
explosion reworked, layered and grander. Branch `feature/pt5-visuals` from lead/integration 1801822. Agent D does the
fire rhythms, behaviours, missile speeds, C-RAM bursts and the siege tank (20W). Nothing here touches the simulation.

### A. In-action targets and the fire supports' camera

- **Targets** (`FiringRange.GroundTargets`): a scout jeep, an armoured car, a light tank, a main battle tank and a
  heavy tank, armour 0 to 4 at the front, so a weapon's effect on each reads side by side. The IFV is gone from the
  targets (its `apc_smoke` dischargers hid the clip); the tower scenes' crossing columns and the EMP clip's attacker
  swap it for a battle tank or a light tank. Friendly IFVs (repair, shields) stay: they do not lay smoke at the enemy.
- **Fire supports are framed with their sky** (`FiringRange.SupportSky`): the look point rises 42 % of the height
  the delivery flies at and the frame widens by 36 % of it: the strike jet 24 m, the bomber raid 32 m, the MOAB's
  transport 44 m, airdrops 30 m, the UAV 22 m, barrages and the EMP 20 m (the rounds' fall), the rest 14 m. The gunship
  on call is framed on its whole turn like a shown gunship (its orbit and altitude).

### B. Blasts: +20 / +30 %, and the rework

**Sizes** (`BlastSizes`, multiplied onto 11A and 12C): tank rounds `TankGrow` 1.2 wide and `TankLinger` 1.2 longer
(light 1.56 / 1.44, main 1.68 / 1.5, heavy 1.8 / 1.56); artillery and mortar shells 1.2 (`Artillery`, also the
barrage support); missiles and rockets 1.2 (`Round`, the HEAT branch, thermobaric's pop, fuel cloud and ring, the
cruise missile's fire and smoke while its ring stays on the radius); every drone 1.2 on top of its own (FPV 1.44,
Lancet 1.5, Shahed 1.56); the gun turret's rounds (`turret_gun_120*`, `gun_57_auto`) 1.3 instead of the tanks' 1.2
(1.82 on the 120 mm), keeping the old linger. The grow factor already spreads more quads rather than blowing sprites
up (11A), so nothing breaks up at the new sizes. Scorch decals follow the drawn size.

**The rework** (`ExplosionEffect`, each recipe's additions after `Richer()`): every blast keeps its old recipe in
full and gains layers by calibre and tier:

| Recipe | Added |
|---|---|
| Shell hit (tank rounds) | a second fire burst off the plate, 12 sparks, 2 burning flakes, rising smoke, embers |
| Medium (mortars, missiles, drones, 57 mm) | a white-hot core, 2 secondary fire bursts on a ring, 18 sparks, 6 fragments, 3 burning, 8 embers, rising smoke |
| Large (artillery, heavy rockets, big shells) | a core, 3 inner fire bursts, 40 sparks, 10 fragments, 4 burning, 16 embers, a second outer dust skirt, a 5-billow smoke column |
| Huge / Ultimate (bombs, heavy missiles, boss attacks, structure deaths) | 2 cores, 5 fire bursts, 60 / 90 sparks, 16 / 24 fragments, 6 / 8 burning, 30 / 40 embers, a second air ring, a wide outer skirt, a 7 / 9-billow column |
| Airburst | a core, 2 fire bursts, sparks, burning fragments, embers, smoke |
| Collapse (buildings, towers falling) | 2 fires in the ruin, sparks, a 4-billow dust and smoke column |
| Napalm | a 4-billow black column, embers |

The layers read in order: flash and fireball (with the new hot core), secondary fire bursts, debris and sparks, the
ground dust rings and shockwave, rising smoke, and on the big ones the **smoke column** (`BlastLayers.Column`, one new
shared system, 1,400 particles: billows climbing out of the crater a third of a second apart, each higher and bigger,
rising 0.9-1.9 m/s and hanging 6.5-12 s, leaning with the wind; its twin draws in front of smoke screens like the
other blended layers). Scorch decals: every Medium-up impact already left one; a fallen defence now scorches the
ground round its ruin too.

**Low budget:** the added layers are emitted at `RichShare`: all on High, 80 % on Medium, half on Low, never fewer
than one of each (so Low has the same shapes). The old recipe is always emitted in full (`CoreParticleCount`), so no
tier shows less fire or smoke than before. Per blast on High (the blast sheet's budget log): Medium 72 to 112 particles, Large 168 to 258, Huge
274 to 418, Ultimate 371 to 571; on Low each stays within the old High caps (Medium 95, Large 240, Huge 400, Ultimate
480; `EffectsTests` pins both). Frame time: a 60 s Conquest battle in Play mode (batch, with graphics, High) ran
1,666 frames (36 ms a frame in the editor, faster than the menu's 49 ms with its preview) with no errors; there is no
before-and-after on a phone yet (testing phase).

### C. The hull fire (low health)

`HullFire` replaces the old licks of flame (one random flipbook quad every 0.12 s) under a burning vehicle's smoke:
below 30 % health a vehicle burns at fixed fire points on its hull (the engine deck, then the turret ring, then a
flank: 1, 2 or 3 as `Severity` rises from 0 at 30 % to 1 at 3 %), each in four layers: a bright additive core
glowing on the hull (what makes a small fire read at a phone's zoom), upright tongues of flame (a brighter copy of
the Flames material), embers lifted by the heat and wandering, and a column of dark smoke climbing out of the fire,
blacker and thicker as it grows. Sizes, embers and smoke all grow with the damage; near death a small pop now and
then. Low: at most two fire points, a 0.12 s beat instead of 0.08 s, half the embers, smoke every other beat. The
burning vehicle's own smoke is the fire's column (the old grey billow stays for 30-60 %). Burning defences burn the
same way.

### D. Plumes

`Plume.ShortFlame` 0.6: the SAM launcher's Buk (`buk_launcher`, and `sam_long` / `sam_post`, the same missile), the
thermobaric launcher's and the heavy rocket artillery's rockets, the ballistic missile, the long-range SAM
(`sam_48n6`) and the Patriot batteries (`patriot`, `sam_battery`, `sam_pac3`, `sam_battery_lrr`) keep 60 % of their
flame. The flame is still measured in the munition's drawn lengths at its cruise speed (and drawn shorter off the
rail by the share of cruise speed it has reached), so agent D's speed changes do not change its length: it stays tied
to the munition's size. The smoke trails are unchanged.

### E. Railgun burn

`LaserBeams.Sear`: a railgun (or coilgun) slug leaves a burn where it struck, like the focused laser's: a white-hot
spot riding the target and cooling through orange over 2.6 s, sparks and molten drops dying down with it, smoke
curling off, the ground lit under it and a scorch decal under a ground target.

### F. Models (`Tools/blender/mb_pt5_models.py`, registered last in `build_assets.py`)

- **FPV drone** (404 to 1,520 triangles): a true-X carbon frame (plates on standoffs, tapered arms), motor bells,
  tri-blade props where the runtime rotor discs spin, a tilted camera pod with its lens, a strapped battery, a video
  antenna and whips, and the RPG-7 warhead (fuse, ogive, band, fins). It flies 20 % smaller
  (`WeaponEffects.QuadScale` 1.3 x 0.8).
- **Bunker vehicle dug in**, as 19R describes it, done properly: an emplacement. The spoil bank is one lofted
  horseshoe of earth (steep inner face, a crest 0.85 m at the front and 1 m down the sides, a long outer slope, open
  at the rear as the ramp), two staggered courses of sandbags across the front and round its corners, one course down
  the front of each side, grass and clods on the slopes, a camouflage net on four poles over the engine deck with
  foliage tied in, ammunition boxes and a can by the ramp. The pose goes hull-down: `HullSink` 0.8 to 1.25 (the hull
  top 0.45 m above the ground), `MountLift` 0.75 to 0.55 (the gun 1.42 m up, clear over the sandbags at 1.1 m), and
  `PlateFold` 95 to 20 degrees: the side plates lean out as armoured revetments lining the pit under the crest instead
  of lying flat on a low bank. The bank stays exported at 1 % (cards, impostors, the move). 11,384 triangles.
- **Gunship** (`sky_gunship`, `_hd`): the AC-130 airframe kept, the battery drawn anew and big (the owner read the
  old one as a bomber): the 25 mm GAU-12 in a blister behind the crew door, the 40 mm Bofors behind a mantlet just aft
  of the wing, the 105 mm howitzer in a long bulged fairing further aft with its recoil sleeve and muzzle brake (the
  AC-130U's layout), all sticking 1.5-3.5 m out of the left side and tilted down; a big sensor ball under the nose,
  a second behind the crew door, gun-deck windows. `Muzzle_mg`, `Muzzle_gun` and `Muzzle_main` sit at those three
  muzzles on the left (the sim's `Left` aims), `Muzzle_ramp` at the ramp launcher. 10,880 triangles (`_hd` 19,818).
- **Transport** (`transport_plane`, new): the same airframe without the battery, the sensors or the ramp launcher.
  AirDrops and StrikeEffects fly it for airdrops and the MOAB (at the gunship's scale), so a transport no longer
  carries a gunship's guns. 8,608 triangles.
- **Gunship card:** `CardRenders.Cards` gives an escort support its aircraft's card ("support" kind): the gunship on
  call shows `sky_gunship`; the shop's item tiles use a card picture when there is one. The pictures are the lead's
  to render (`sky_gunship`, `bunker_vehicle`, `stealth_fighter`, `fpv_carrier` unchanged).
- **Stealth fighter** (1,980 to 4,484 triangles): prompt 17's airframe with the middle filled in: intake lips, the
  bump ahead of each mouth and dark ducts, canopy sills, bow and aft frames, a HUD and seat, a dorsal spine with a
  sawtooth access panel, the refuelling door, the APU vent, blade antennas, EODAS windows and air-data probes,
  sawtooth panel lines across and along the body, the bay doors' seams on the belly, and hinge and spar lines on the
  wings.

### Tests and captures

`PlayTest5VisualTests` (10): the targets' armour 0-4 and no smoke; every support framed with its sky; the
airstrike's clip showing the jet's height and the targets; the rework's
additions, Low's share and the column; the hull fire's scaling and Low; the railgun burn cooling and going; the FPV
scale; the gunship's three muzzles well out on one side and the transport without guns; the gunship's card; the
bunker's pose. `BlastSizeTests` and `MissileFlightTests` take the new factors. Run once each: `PlayTest5VisualTests` 10/10 (the airstrike framing test added on a second run: the
targets and a point 24 m over them inside the picture), `BlastSizeTests`, `EffectsTests` (the budgets above, 27
systems with the column and its twin), `InActionTests`, `FlashTests`, `VehicleLodTests`, `MuzzleTests` pass;
`MissileFlightTests`, `ModelTests`, `RangeSceneTests`, `CardRenderTests` with these failures, none from this work:
`ModelTests.RoundsLeave` (3, known), `ModelTests.EveryWeaponMountHasAMuzzleOnItsModel` (mobile_fortress's
boss_howitzer, a boss mount), `MissileFlightTests.MissilesFlySlowerAndLandBeforeTheirCooldown` (sam_battery_lrr's
4.17 s flight against its 3.6 s cooldown: data), `RangeSceneTests.JammerScramblesTheMissilesAtItsFriends` (the ATGM
post never fires: sim), `GearModelTests.AnOldSaveMigratesWithNothingLost` (save migration); `CardRenderTests` until the
lead renders the cards (stealth_fighter, bunker_vehicle, and gunship_support from sky_gunship).
Captures in `Docs/art/pt5/`. `blasts.png` (the blast sheet: medium, large and a tank death at 0.25, 0.7, 1.6 and 4 s),
`hull_fire.png` (28 %, 15 %, 4 %, 4 % on Low, and a railgun burn), `bunker_dug_in.png`, `gunship.png`,
`stealth_fighter.png`, `fpv_drone.png` (Blender renders of the exported models, the bunker in its dug-in pose), and
`inaction_gunship_airstrike.png` (the In action clips: the gunship on call circling its targets, the airstrike). New
capture: `EffectShots.HullFires`.

### For the testing phase

The blasts' and the hull fire's cost in a long heavy fight on a low-end phone (Low); whether the smoke columns hide
too much of the field at the default zoom; the In-action framing of each fire support on a phone.


## 20X. Armour and damage balance: punchier fights after prompt 15 (2026-09-29)

The owner found damage too low across the board after the armour and penetration system (14A). Measured first, then
the global knobs: the penetration row, the faces hit, toughness, and one over-armoured unit. No weapon row changed
(agent D is changing the autocannons, jet cannons, missile speeds and the C-RAM; notes for the lead are at the end).

### Measured

New `ArmourBalanceMeasure.MeasureTimeToKill` (MB_BALANCE=1, 3 seeds, about 20 s): a shooter group against a target group
that holds its fire on the Sandbox's flat range; direct-fire shooters stand in reach so the face struck is the one set,
artillery and aircraft use the fighting AI, helicopter targets hover. Time to kill runs from the first hit to the last
target's end. It files every hit (`SimWorld.HitLog`) by its penetration step and face, and nets what armour took off
(1 - dealt / (dealt / multiplier)). A mixed battle (the same ten-vehicle army each side, both fighting) gives a whole
fight's spread. Files: `Docs/balance/armour_ttk_20x_{before,after}.tsv`.

Before the pass: 35 % of the matchups' hits landed two levels under (x0.15) and 21 % three or more under (x0.05), and
armour took 34 % of their damage; in the mixed battle 21 % landed at x0.15, none at x0.05, and armour took 17 %. The
x0.15 and x0.05 hits are mostly machine guns and autocannons on tanks and bunkers: many hits, little damage. The
prompt 13 comparison (`combat_value_F3` against today's run) shows why it felt weaker: damage against light vehicles and
tanks was where prompt 13 had it (x1.04, x1.07 median), against the fort group x0.66 and from non-AA weapons at the air
group x0.56; and the facing factors (side x1.25, rear x1.6) were gone, so a 120 mm dart did the same to a battle tank's
front, side and rear (all one level above: x1).

### Changed

| Knob | Before | After | Why |
|---|---|---|---|
| Penetration row (`damageTable.penetration`) | 1, 0.75, 0.4, 0.15, 0.05 | 1.2 (two or more above), 1, 0.85 (level), 0.5, 0.25, 0.1 | level-matched rounds lose less; the x0.15 and x0.05 hits do something; a new overmatch step makes a flank shot beat a front shot for the guns that pierce both |
| Overmatch where | | front, side and rear only: never a roof (top attacks, everything lobbed or dropped, an aeroplane's fire) nor an aircraft | with it on roofs every artillery shell, bomb, drone and jet gained a fifth everywhere (combat value: artillery and aircraft +15-35 % against the median, the fighter's air value -39 % over 3 seeds) |
| Front arc (`Armour.FrontArc`) | 50° | 40° (rear 50° kept) | more rounds from off the nose strike the thinner side (mixed battle: two-under hits 21 % → 16 %) |
| Toughness (`toughness.vehicles`) | 2.5 | 2.2 (bosses 0.85 kept) | every fight about an eighth shorter; the penetration row alone left light fights at 14-15 s and tank duels at 40 s |
| Turtle tank armour | 4/3/3/3 | 3/3/2/3 | its shed stops drones and rockets, not a dart; it had a heavy tank's front at 7 CP (tanks value 423 against the battle tank's 335; now 349) |

The row takes five values still (prompt 15's, no overmatch step); `DamageTable.Penetration(pen, armour, overmatch)` and
`DamageTable.Overmatches(kind, roof)` carry the rule, and every caller passes the face: the hit (`HitMultiplier`),
targeting (`Estimate`), the interface's helpers (`Matchup`) and the commander's counter score (`ConquestAi.Fit`, now 0-1.2).
The ✓ ~ ✕ thresholds (0.6, 0.12) keep every verdict they gave. The plunder check (`TacticalAi.PlunderWith`) needs 0.35
on a level-2 structure (was 0.25) so a heavy machine gun (now 0.3) still does not go plundering; the artillery check keeps
0.2. Damage per round is untouched: the calibre scale stands; the most a hit gains is x1.2 (the old side factor was x1.25).
The firepower knobs (strikes 2.0, blasts) stay, so strikes and blasts count a little more against the lower health.

### Time to kill, before and after (seconds, 3 seeds; "flank" is the target side on)

| Matchup | Before | After |
|---|---|---|
| 2 armoured cars vs 2 armoured cars | 15.2 | 13.2 |
| IFV vs 2 armoured cars | 15.0 | 13.1 |
| 2 IFVs vs 2 IFVs | 15.6 | 13.1 |
| 2 jeeps vs 2 armoured cars | 22.2 | 17.4 |
| MBT vs MBT, front | 45.9 | 34.9 |
| MBT vs MBT, flank | 34.9 | 25.6 |
| MBT vs heavy tank, front | 111.7 | 84.6 |
| MBT vs heavy tank, flank | 79.3 | 62.9 |
| light tank vs IFV, front | 48.4 | 34.3 |
| light tank vs MBT, flank | 84.1 | 59.4 |
| IFV vs MBT, front / flank | 46.4 / 28.7 | 34.0 / 21.1 |
| tank destroyer vs MBT, front | 32.7 | 25.1 |
| 2 armoured cars vs MBT, front (the wrong tool) | 57.7 | 39.4 |
| FPV carrier vs MBT | 51.3 | 36.0 |
| Lancet truck vs heavy tank | 97.1 | 75.1 |
| AA vehicle vs attack helicopter | 23.7 | 20.1 |
| SAM launcher vs attack jet | 10.7 | 8.8 |
| heavy AA vs attack jet | 13.5 | 9.3 |
| 2 SP howitzers vs 4 armoured cars | 57.2 | 49.7 |
| 2 MLRS vs 2 MBTs | 55.5 | 39.4 |
| 2 SP howitzers vs 2 MBTs | 86.5 | 74.4 |
| gun turret vs 2 MBTs | 57.4 | 48.7 |
| MG bunker vs 3 armoured cars | 25.7 | 19.6 |
| ATGM tower vs MBT | 25.7 | 23.7 |
| AA turret vs attack helicopter | 18.3 | 17.7 |
| 2 MBTs vs gun turret | 73.5 | 61.4 |
| 3 armoured cars vs MG bunker | 109.0 | 75.9 |

Fights are 10-35 % shorter. A flank shot beats a front shot everywhere (MBT on MBT 26 s against 35; the tank gun
x1.2 on the side against x1 on the front). The right counter wins: the tank destroyer kills a battle tank in 25 s, two
armoured cars (a CP less) in 39 s.

| Hit spread | Before | After |
|---|---|---|
| Matchups: one or more above / level / one / two / three under | 6 / 13 / 25 / 35 / 21 % | 7 / 13 / 24 / 36 / 20 % (two above: 0 %) |
| Matchups: net damage armour takes | 34 % | 27 % |
| Mixed battle: one or more above / level / one / two / three under | 22 / 39 / 18 / 21 / 0 % | 31 / 40 / 14 / 16 / 0 % |
| Mixed battle: net damage armour takes | 17 % | 5 % |
| Mixed battle: faces front / side / rear / top | 79 / 17 / 3 / 1 % | 79 / 12 / 9 / 1 % |

The share of hits at two and three under hardly moves in the placed duels (the same faces); what changes is what they do
(x0.25 and x0.1).

### Re-measured

- **Combat value** (`CombatValueMeasure`, one seed; `Docs/balance/combat_value_20x_*`): first kills sooner (tanks 42 →
  38 s, fort 58 → 51 s, tanks+AA 55 → 43 s median), per-CP values a little lower as enemies die sooner (median ground
  x0.94, air x0.95, fort x1.0). Outside ±20 % of the median: the turtle tank (intended), the IFV against tanks (73 from
  113: the tanks now kill it faster, x1.2 on its level-2 hull), the BMPT (ground 335 → 243: its level 3 now takes x0.5
  from autocannons; still the best tank-class value against light groups after the MBT), the laser tank against tanks
  (277 → 186, one seed), helicopters against tanks (+15-50 %: their missiles overmatch sides). By class the bands hold:
  heavy 174-510, tank hunters 311-425, artillery 182-461, helicopters 330-390, aircraft 55-463, anti-air in the air 58-565.
- **Towers** (`TowerValueMeasure`; `tower_value_20x_*`): medians after/before, the CP columns light 1.02, tanks 1.06,
  shelling 1.03, heavy 0.99, air 1.15; the worth columns 0.99-1.00: towers keep their worth.
- **Counters** (`CounterTests`): 12 of 12, faster and with the same margins (heavy tanks beat medium tanks in 35 s, was
  48; helicopters beat tanks 43 s, was 52; FPV drones beat heavy tanks in 79 s, was a 150 s time-out on points).
- **Sweep, 3 seeds, before → after** (`campaign_20x_*`, `modes_20x_*`): campaign c1m03, c2m05, c4m06, c5m06, c7m05,
  c8m07, c10m05, c11m03, c12m05: 27/27 → 27/27 (c5m06 15.3 → 13.4 min, c7m05 9.6 → 8.5); Conquest 6/9 → 5/9 (median 6.6
  → 6.7 min); Siege 7/9 → 8/9; Defend 9/9 → 9/9; Boss Rush 0/6 → 0/6 (both stop at 9 of 10 bosses in the 30-minute cap,
  a limit of the measure before this pass; the bosses' minutes each hardly move).

### Tests

`ArmourTests` (the six-step row, the five-value row still read, part levels between one and two above, no overmatch on a
roof or an aircraft, the 40-degree front, the hit expectations read from the table), `CalibreTests` (an autocannon x0.5
on a battle tank's front), `GearSimTests` (the ricochet's side and rear hits read from the table), `Prompt8ContentTests`
(the bulldozer's 2,860 health in game, the turtle's). Run: Counter, Armour, Calibre, Prompt8Content, GearSim, GearTrait,
Combat, CounterBuy, SandboxBattle and the measures, then again after the fixes: all pass but two failures older than
this pass, left alone: `ArmourTests.EveryUnitAndWeaponHasTheNewFields` (175 weapons, 172 found by its text scan: the rows
`casemate_155`, `naval_127` and `naval_100` are not written `{ "id":`) and `ElitePrompt8Tests.EveryEliteIsOnTheSameFooting`
(the elite attack helicopter's 675 health is under its card's 800 since prompt 17 D).

### For the lead (weapon rows not touched)

- **Autocannons** (agent D's 5 s bursts and 1 s reload): one level under is now x0.5 (was 0.4), so a 25-30 mm on a
  battle tank's front does a quarter more. Re-run `ArmourBalanceMeasure` after the rhythm change: if two armoured cars
  come within a quarter of the tank destroyer's time on a battle tank (now 39 against 25 s) or the IFV beats the MBT's
  own time on it (34 against 35 s), hold the 25/30 mm damage a second.
- **Jet cannons, missiles, C-RAM**: nothing moves for them from this pass on the roof or in the air (no overmatch there;
  level-1 aircraft take 0.85 at level instead of 0.75). Missile speeds are unaffected.
- **Left for the testing phase:** five seeds for the combat value (the laser tank, the BMPT, the fighter's air value),
  the whole campaign and every mode, and the elites' power band with the new row.



## 20W. Play-test 5, sim half: autocannon rhythm, the jets' tail chase, rocket and drone speeds, the C-RAM's bursts, the siege tank (2026-09-29)

The owner's play-test 5 items marked [D] (`Docs/prompts/requests_vi.md`). Branch `feature/pt5-sim` from lead/integration
1801822. Agent C (20V) has the visual half; nothing here touches blasts, plumes or the models C redraws.

### A. Autocannons: about 5 s of fire, about 1 s to change

**The rule.** Every autocannon a deployable unit carries now fires a magazine of about 5 s and changes it in 1 s:
`(clip - 1) x cooldown` is 4.9-5.1 s and `clipReload` 1 s. The damage a round stays on prompt 13's scale and the
penetration of prompt 15 is untouched. The owner asked to "rebalance the damage", but the scale's bands are narrow
(35 mm 24-26, 30 mm 20-24, 25 mm 16-18, 23 mm 13-15), so a 5 s stream at 19R's real cadence would need a round 4-5 times
under its band. **Decided:** the magazine and the cadence were solved so that `FirePower.Sustained` is unchanged (within
1 %); the cadence over the stream is therefore the old average (the tracers a minute are as before), not 19R's real
peak. This is 19R's own exception ("a real rate the calibre scale cannot carry"); 19R's real rates stay recorded there.
If the owner wants the old brrrt back, the choice is a lower band for autocannon rounds (the owner's scale) or a
higher damage a second.

| Weapon (carrier) | 19R | Now: cadence x magazine / change |
|---|---|---|
| `flak_35` (aa_vehicle) | 1,101 rpm x16 / 3.73 s | 242 rpm x21 / 1 s |
| `twin_30_flak` (heavy_aa) | 3,593 rpm x20 / 1.56 s | 755 rpm x64 / 1 s |
| `twin_35_ahead` (elite_aa) | 1,000 rpm x24 / 4.79 s | 269 rpm x23 / 1 s |
| `zu23` (zu23_technical) | 1,802 rpm x16 / 1.21 s | 662 rpm x56 / 1 s |
| `ifv_30` (ifv) | 550 rpm x10 / 1.55 s | 272 rpm x24 / 1 s |
| `autocannon_30` (heavy tank's secondary, elite APC, two bosses) | 300 rpm x10 / 1.74 s | 191 rpm x17 / 1 s |
| `twin_30_bmpt` (bmpt) | 1,091 rpm x10 / 1.99 s | 278 rpm x24 / 1 s |
| `autocannon_25` (armored_car) | 500 rpm x6 / 1.48 s | 196 rpm x17 / 1 s |
| `heli_gun` (attack helicopters) | 625 rpm x22 / 4.6 s | 228 rpm x20 / 1 s |
| `gsh30k` (gunship_heli) | 2,400 rpm x20 / 2.8 s | 427 rpm x37 / 1 s |
| `jet_cannon` (attack_jet) | 3,000 rpm x30 / 1.33 s | 1,119 rpm x94 / 1 s |
| `fighter_cannon` (fighter_jet, stealth_fighter) | 3,297 rpm x40 / 4.7 s | 521 rpm x44 / 1 s |
| `gunship_25mm` (sky_gunship) | 1,802 rpm x45 / 3.64 s | 622 rpm x53 / 1 s |
| `gunship_40mm` (sky_gunship) | 3-round salvos, 0.64 s | a belt: 325 rpm x28 / 1 s |

**Left as they were:** the towers' guns (`tower_flak_30`, `hq_flak`, `tower_ac25` keep their own rhythm over the
inherited one; the C-RAM's gun, section E), the bosses' and ships' (`boss_flak`, `boss_heli_gun`, `hover_ciws`,
`airship_flak`, `mothership_cannon`), and the 57 mm guns (the light tank's is a tank gun of 2 aimed rounds, the
tower's `gun_57_auto` a tower weapon). `gsh_23v` and `gau_gatling` have no carrier.

**What moved the combat value, and the two fixes.** Against aircraft passing through, a stream at the old average
lands about half of what the old front-loaded burst did; and an anti-air vehicle's lead gun, streaming for 5 s, held its
SAM for all of it (the IFV rule, 11C). First measure: `aa_vehicle` -45 % and `heavy_aa` -42 % on aircraft, every
aircraft up in the scenarios with an anti-air vehicle. Fixed by:
- **A SHORAD's missiles fire beside its gun's stream** (`CombatSystem.AirMissileBesideFlak`): an anti-aircraft missile on
  a vehicle whose lead gun is an anti-aircraft magazine gun takes its own turns, as a Tunguska's or a Pantsir's do.
- **Proximity-fuzed rounds against aeroplanes:** `flak_35` and `twin_35_ahead` x1.5, `twin_30_flak` x1.25 against class
  Plane (a data bonus, not the round's damage; helicopters, which hover in the stream, get none). An armour-Air bonus of
  1.6 was tried first: it made the anti-air too strong on helicopters (-30 % on the attack helicopter's long run).
  `tower_flak_30` and `hq_flak` do not take the bonus (`hq_flak` has `"bonuses": []`; the tower's own stays).

### B. Jets: the rhythm and a tail chase

Both fighters' `fighter_cannon` and the attack jet's `jet_cannon` have the rhythm of A. **New behaviour**
(`MovementSystem.DriveAeroplane`): a jet whose hull-fixed magazine cannon can hit aircraft (`TailGun`: the fighter and
the stealth fighter; the attack jet's cannon hits the ground only), chasing an enemy jet flying fast (`FastMover`), flies
for a point behind it (its heading, 55 % of the cannon's reach astern: lag pursuit) until it is inside the jet's rear
60-degree cone and within 1.4 x reach, then keeps its nose on the jet at the old speed match (a little over half the
reach) and does not pull through when the jet slips across its nose. `Vehicle.OnTail` marks it (in the cone, within
reach, nose within about 25 degrees). **Firing on the tail:** the cannon leads (`Leads`: a fixed-wing mount leads only
then), so its 5 s streams run on; the air-to-air missiles fire beside it (the same rule as the SHORAD's). A helicopter
target is still held on as before (12F). Test: a fighter chasing an attack jet round the field sits on its tail for 8 s
or more of 45 and streams 3 s or more.

### C. Missile, rocket and drone speeds

- `thermobaric_rockets` (TOS-1A) 45 and `rockets_300mm` (Smerch) 50 → **24 m/s**, the SAM's.
- The rocket battery tower: `turret_rockets` 55 → 24 (`turret_rockets_cluster` and `turret_thermobaric` inherit it) and
  its guided branch's `turret_gmlrs` 55 → 24. **Coordination with 19T:** no other branch number moved; the branch tests
  (`TowerBranchTests`) pass. `TowerValueMeasure` (the tower agent's) was not rerun: the rockets now give a moving target
  2-3 s to drive out of the 4.5 m splash, so the tower loses some of its value against vehicles on the move.
- The attack jet: `s8_pods` 48 → 36, `kh29` 23 → 17.25, `r60` 24 → 18 (25 % slower; only the attack jet carries them).
  The owner's "tên lửa" covers its rockets and missiles alike, and its S-8s were the fastest thing it fired.
- The drone mothership: `mothership_drones` (its Lancets) 26 → 15.6 (40 % slower). The strike drones its skill
  summons are ordinary strike drones and keep their speed.
- Unguided rockets at 24 m/s are no longer 19R's exception for these three launchers: they aim where the target was
  (only equipment leads), so the heavy launchers lose a little against movers; the C-RAM has longer to take them.

### D. The siege tank: reworked, not added

**Compared.** The old `siege_tank` was an M110 203 mm gun on a 3-armour heavy hull (3.6 m/s, 2,200 HP, 62 m, no fire on
the move, x2.4 on structures): a siege tank permanently in siege mode. The SP artillery (`artillery`) is a light-armoured
155 mm howitzer (90 m, minimum 25 m) that shoots and scoots; the mortar carrier a 120 mm on a light hull. A second,
StarCraft-2-style siege tank would have repeated the old one's siege mode on another armoured hull, and prompt 17 D had
already merged the siege mortar into it (`CardMerges`). **Decided: the existing `siege_tank` is reworked** into the
two-mode tank; id, CP 12, card merges, the Breachers list and saves stay.

**Data.**
- `siege_tank`: class **Artillery** (strong vs Defense, Heavy, Tank; by class weak vs scouts, light vehicles,
  helicopters and planes: what gets inside its minimum reach or above it), armour by face **[3, 2, 1, 1]**, 1,500 HP,
  5.5 m/s, vision 38, capsule 8.0 x 4.19 m (`measure_hulls.py`).
- Main weapon (mount 0, sieged): `siege_mortar_240`, the 2S4 Tyulpan's 2B8 240 mm (inherits `mortar_240`, the same
  450-damage bomb and pen 4 on the scale), 16-70 m (outside every tank gun's 32-34 m and most towers'), 9 m splash, a bomb
  every 8 s, 10 then 30 s to reload, x2 on structures.
- Tank mode (mount 1, `slot` gun, turret): `siege_gun_105`, the L7 105 mm (inherits `gun_105_bunker`, 200, pen 3), 34 m,
  4.6 s, on the move. Roof M2 on a free mount (mount 2).
- `"deploy": { "seconds": 2.5, "front": 0, "range": 1, "arc": 180, "siege": true, "tankMount": 1 }` (`DeployDef.Siege`,
  `TankMount`).

**Sim.** `Vehicle.MountWorks` gates the modes (`SiegeModeFires`): the mortar only sieged, the 105 mm only on its tracks,
neither while it sieges or packs up (the bunker's rule). On its tracks the turret is laid by the 105 mm's targets
(`SelectTarget(v, tankGun)`, which also fires on the move). `DeploySystem`: it sieges after standing 1 s with a ground
enemy between the mortar's minimum and full reach (or on guard 4 s away from its drop zone, as the bunker), never with an
enemy already inside the minimum; it packs up for a route more than 6 m long, or after 1 s with enemies inside the
minimum and nothing further to shell (`Crowded`). `MovementSystem.CloseIn` does not back it off from an enemy inside
the minimum (its gun fights it).

**AI, both sides.** Its main weapon has a minimum reach, so both commanders treat it as artillery: `TacticalAi`
stands it off behind the army outside every known gun's reach, kites what it outranges and shells defences and
structures from spots out of their reach (the existing `DirectArtillery`; `AiReviewTests.SiegeTankShellsAKnownTurret...`
passes), so it sieges out of the enemy's reach and packs up whenever it is sent forward. New: with a ground threat inside
its minimum reach and within its gun's, it attacks it in tank mode instead of running. **Counter-AI:** `ConquestAi`
counts it in the enemy's artillery and answers it with aircraft and fast hunters; its Artillery class tells the cards and
the counter buying the same (`Counters.WeakVs`).

**Model** (`Tools/blender/mb_p22_siege.py`, replacing the old builder in `build_all`): an 8 m tracked hull, a wide
turret on a column with the 240 mm mortar in a roof cradle (the elevating barrel, `Main_cannon*`, `Muzzle_main`) and the
105 mm on its right cheek (`Deploy_gun`, `Muzzle_gun`), a roof M2 (`Mount_mg`). Sieging (`VehicleView.AnimateSiege`, the
data's 2.5 s, backwards to pack up): the rear spades swing down (`Deploy_spade_*`, first 40 %), the outriggers fold out
and down 140 degrees on to their pads (`Deploy_brace_*`, 10-55 %), the 105 mm slides 0.9 m back into its sleeve (20-50 %),
the turret rises 0.45 m (`Deploy_riser`, 45-80 %), and the mortar swings up from level to 45 degrees, then is laid by
range to 55-72 (`VehicleView.SiegeElevation`, from 55 %). 10,704 triangles (the old model 9,608).

**The rest.** Guide card, card note and behaviour lines (`ul.siege`, `ul.siege.tank`) rewritten in both languages; the
short names stay; a new icon (`siegetank`: braces down, mortar up). **Campaign unlock:** no longer a premium card
(`Progression.PremiumPrices`, the shop's list): won in chapter 4's first mission (`c4m01`, beside the command vehicle),
early for 2,100 coins; anyone who bought it keeps it. The unit lines use `{0}` (the seconds) as every `ul.*` line does;
the localisation agent's named placeholders can take it over.

### E. The C-RAM: a burst at every round

**Before:** a C-RAM stopped a round the moment it landed with one interceptor charge, drawn as one tracer and a pop.
**Now** (`CombatSystem.EngageIncoming`, the data's `aps.burst`: `c_ram` 0.5 s, `c_ram.centurion` 0.3 s): the gun lays on
the incoming round landing soonest (within its 35 m of the mark, 0.2-3 s from landing, the same kinds as before:
rockets, guided rounds, 30-40 % of shells, decided once a shell), streams 3 rounds a step at it (60 a second,
`SimEvent.PointDefence`: the view draws tracers to the round's place and height and turns the turret on it) and after the
burst the round bursts in the air where it has got to, one charge spent. One round at a time; a round that would land
before a 0.2 s burst could run is not engaged. `DamageSystem.TryIntercept` leaves burst systems out; the Iron Dome's
missiles, the lasers and the tanks' hard-kill systems are as they were. **Rates** (`TowerValueMeasure.PrintCRamInterception`,
two launchers for 60 s, three seeds; the heavy rockets are now slower, section C):

| Guard vs | mlrs | rocket_technical | heavy_rocket_artillery |
|---|---|---|---|
| `c_ram` before → now | 60 → 70 % | 70 → 62 % | 35 → 48 % |
| `c_ram.centurion` | 90 → 81 % | 100 → 90 % | 55 → 69 % |
| `c_ram.dome` (unchanged) | 48 → 48 % | 34 → 34 % | 27 → 25 % |

### F. Combat value

`CombatValueMeasure`, the whole roster, seeds 13-15, before (the lead's tree) and after (`Docs/balance/combat_value_pt5_*`):
the median cell moved **0.5 %**; 44 of 324 cells (over 20 points) moved more than 10 %. The anti-air on aircraft is back
within 2 % (`aa_vehicle` 223 → 218, `heavy_aa` 286 → 283); the fighter -8 % and the stealth fighter -15 % on aircraft; the
attack jet -9 % over its ground scenarios (its slower rockets and missiles); the siege tank +5 % on the ground (+9 % with
no anti-air: stronger against light groups and artillery with its gun on the move, -13 % on defended forts).
The larger swings are small numbers and the aircraft's 4-minute runs (the stealth fighter's +74-114 % from 20-40 points,
the swarm carrier -41 % to +43 % by scenario, the rocket technical's long run), which 19R already found too noisy for
three seeds: the testing phase's sweep should judge the aircraft.

### G. Tests

New `PlayTest5Tests` (the 5 s / 1 s rhythm on every weapon of A, the Gepard's stream at a helicopter, the tail chase,
the speeds of C, the C-RAM's burst before every round it drops, the siege tank sieging for its mortar and firing only
it, fighting on the move with its gun, packing up to move and when rushed, and its artillery class and campaign unlock)
and `ModelTests.SiegeTankKeepsItsSiegePartsApart`. Run: compile; `PlayTest5Tests`, `CounterTests` (all pass: SAM beats
jets, anti-air beats helicopters, fighters beat helicopters), `ModelTests`, `VehicleLodTests`, `AirAttackTests`,
`AbilityTests`, `AiReviewTests`, `RosterRoleTests`, `MissileFlightTests` (the S-8's new speed pinned), `WeaponRhythmTests`,
`ApsTests`, `RosterBalanceTests`, `RosterMergeTests`, `StuckCauseTests`, `TrafficTests`, `InActionTests`,
`EquipmentPrompt8Tests`, `ContentTests`, `LocalisationScanTests`, `BigAttackTests`, `SiegeModeTests`, `CalibreTests`,
`CounterBuyTests`, `AircraftTests`, `AirRealismTests`, `AirMotionTests`, `TowerBranchTests`, and the two measures.
**Failing, already on lead** (checked on the lead's tree) and not touched: `AirAttackTests.AnAttackHelicopterComesIn...`
(its gun never fires, before this change too), `AiReviewTests.FortressBuildingsPayABounty...` (6 buildings on
`ashfield_siege`) and `...TheLosingSideIsReinforcedFaster...`, `MissileFlightTests` on the tower `sam_battery_lrr` (4.17 s of
flight on its 19T 3.6 s cooldown), `ModelTests.RoundsLeave` (3), `EveryWeaponMountHasAMuzzle` (mobile_fortress),
`GearModelTests.AnOldSave...`.

### Shared edits (merge by hand if they conflict)

`balance.json` (weapon lines of A and C, the two `siege_*` weapons, the `siege_tank` entry, the C-RAM's `aps`),
`campaign.json` (`c4m01` unlocks), `CombatSystem.cs`, `MovementSystem.cs`, `DamageSystem.cs`, `TacticalAi.cs`,
`VehicleView.cs` / `.Deploy.cs`, `EffectsDirector.cs` (two event cases), `Strings.cs`, `GuideText.cs`, `UnitText.cs`,
`Icons.cs`, `MenuScreen*.cs`, `Progression.cs`, `build_assets.py` and `Docs/art/models.json` (`resolve_merge.py`).

## 20Y. Boss redesigns: Leviathan as a battleship, Ixion, Icarus, the boss review, death smoke (2026-09-29)

The owner's requests (29/09): make Kessler's Leviathan a real battleship on the Yamato's lines, bigger if needed and with
more guns, and shrink the old model into an escort; then redesign Ixion (ugly, not scary) and Icarus (a shuttle, not a
warship), review the other bosses at the default zoom, and thin the boss death smoke. On feature/leviathan-yamato from lead/integration 5ba05ab. Every
redesign starts from outside references, listed per boss.

### A. Leviathan (`leviathan`, `Tools/blender/mb_naval.py`)

**References.** The IJN Yamato (1941) and its 1945 fit: the flush deck with its sheer and bow flare, the wide beam,
three triple 46 cm turrets (A and B forward, B superfiring, C aft), the pagoda tower with the 15 m rangefinder on the
director and the Type 21 radar above it, the single funnel raked aft, triple 15.5 cm secondaries superfiring over B and
C, the Type 96 25 mm triples in open tubs and the Type 89 twin 12.7 cm high-angle mounts along the sides, the stern's two
catapults, floatplane and crane, the anchors and their chains on the forecastle. The missile cells beside the funnel and
the stern gate keep prompt 16's hybrid (a battleship with a missile cruiser's cells; the Kirov and the 1980s Iowa
missile refits are the precedent). Hegemon's marks, not Japanese insignia: chevrons in the side's colour on the bow, a
hexagonal crest on the stem (no chrysanthemum), the side's colour on the turret roofs, the funnel band and the boot-top.
Wood-planked deck, gunmetal hull, the side's colour on the superstructure (Machine Brigade's palette).

**Size.** 86 x 14.4 m as built, drawn at the data's `size` 1.12 (96 x 16 m; the old ship was 72 x 12). Checked:
- **The lanes** (near, mid, far 14 m apart at w 92, 106, 120): its half beam is 8 m, so it clears the next lane's
  ships; the shore margin follows its hull (`HullRadius`). Its length only matters along the lane; at the far lane's
  ends the bow reaches past the square on the open sea's side, as the old ship's did (the sea runs on out there).
- **The camera**: the widest game zoom (42) shows about 150 m across, the whole ship with room; the arrival pan keeps its
  zoom.
- **The hit radius** is 11.2 before the size (12.5 m): `TheSeaLanesAreInReachAsDesigned` was 0.7 m short on lead (the
  headland's rocky flank 46.7 m off the near lane, direct fire's 34 m reach, the old 13.4 m radius). Parts keep their
  own reach, so long ships are hit at the bow and stern by what is there.
- **Its escorts** used to keep station 26 m ahead and astern on its own lane, inside its 72 m hull (naval ships skip the
  movement system's separation). A fleet entry now takes `abeam`: an escort keeps station beside the flagship on the
  shore side, inside its length ("at" along its line from its middle, "abeam" towards the shore; the k-th ship of an
  entry mirrored along and a row further in). `NavalSystem.StationOf`, `Vehicle.StationAt`. Entries without `abeam`
  (Typhon's corvette) keep the old station. With escorts abeam on the mid lane, the attack boats wait on the near lane
  while their flagship sails the far one (`RaiderLane`); an operation's extra escorts join the last escort entry only
  (two escort entries would have doubled them). `LeviathanSailsWithItsFleetOnTheLanes...` checks no two ships overlap.

**Guns (each a breakable part, on the calibre scale and prompt 15's penetration).**
| part | weapon | notes |
|---|---|---|
| `turret_fore`, `turret_super`, `turret_aft` (`maingun`, armour 4) | `leviathan_460`: 460 mm, pen 4, HE, 950 (the howitzer row's 2.07 a millimetre), laid | the salvo and the big attack; C's arc is [180, 150] |
| `sec_fore`, `sec_aft` (`gun`, armour 2: Yamato's thin-skinned secondaries) | `naval_155_triple`: 155 mm triple, pen 3, 320 x 3 every 10 s, 110 m | arcs [0, 135] and [180, 135], clear of the tower |
| `aa_port`, `aa_starboard` (`flak`, armour 1) | four `aa_25_triple` each: 25 mm, pen 1, 17 a round, aircraft only, 42 m | eight trainable tubs; more tubs and six twin 127 mm mounts are drawn only |
| `ciws_fore`, `ciws_aft` (`ciws`) | `hover_ciws` | part 2's APS (radius 30 now) |

The old `leviathan_203` and the two 127 mm mounts (prompt 20 F.3) are gone; `cruiser_203` is the cruiser's.

**The salvo** (`NavalSystem.Salvo`): one gun a turret, three shells of 950 every 14 s (was two turrets x two shells of
420 every 12 s), in one line along the shore across all standing turrets, marked 3 s ahead; each turret flashes once a
shell. Laid turrets are trained out to the beam on joining, turned inside their arcs as the ship comes about (`Lay`),
and aimed inside them when they fire, so C never swings across the superstructure.

**The big attack** `leviathan_volley` is the nine-gun broadside now: a circle at the base (the HQ), three ripples of one
gun a turret (`perPart` 3, `salvo` 3 over 2.4 s), 950 each, pen 4, x1.5 on buildings, radius 8, falloff 0.35, spread over
24 m, warned 5 s; each broken main turret takes its three rounds away; the cruise missiles wait while it charges. The
cruise missiles stay the launch cells' own mechanism (every 50 s from phase 2, four at the base as phase 3 begins), so
phases 1-3, the landing craft, the helicopters, the jets and the run are unchanged. Its words are new (Nine-Gun
Broadside / Loạt bắn mạn chín nòng).

**Parts and health.** 14 parts at 5 % each (70 %, prompt 20 F.3's rule for more than ten). Health stays 11 000, the main
rank's own (no share), so the fight's length stays where prompt 16 set it; the testing phase's 5-seed kill time is the
measure. Nodes: `Part_gun` / `.001` / `.002` (on `Mount_gun` / `.001` / `.002`), `Part_sec_f` / `Part_sec_a` (`Mount_gun.003`
/ `.004`), `Part_vls`, `Part_aa_l` (`Mount_mg.002`-`.005`), `Part_aa_r` (`.006`-`.009`), `Part_mg` / `.001`, `Part_radar`
(the rangefinder and the spinning `Radar`), `Part_deck`, `Part_welldeck`, `Part_engine` (the funnel). Every muzzle sits on
its middle barrel's tip (`MuzzleAuditTests`: none of its 15 mounts off). 26 k triangles (the LOD is automatic).

**At rest** the model's bores point forward (the kit's rule), so C and the aft secondary face the superstructure in a
card render: pose `Mount_gun.002` and `Mount_gun.004` aft (180 degrees) for the card. In the game they are laid.

### B. The missile cruiser (`sea_cruiser`)

Prompt 16's Leviathan model, kept as it was built and drawn at 0.72 (46 x 8 m): two twin 203 mm (`cruiser_203`, pen 4,
2 x 420 every 11 s, 105 m; the aft turret rests facing aft, arc [180, 150]), two CIWS (APS 30 m, covering the
flagship), HP 2600, armour [3, 3, 3, 2], 3.2 m/s; the cells, radar, hangar and helicopter deck are drawn only. Its
barrels are 1.1 m apart now, so each gets its own launch point (the twin rule) and the audit passes. Name, note, Guide
line and dossier file in both languages (Missile Cruiser / Tuần dương hạm tên lửa; "Kessler's old flagship, the first
Leviathan"). **The fleet**: the cruiser abeam forward (at 22, abeam -17), one corvette abeam aft (-27, -16), three attack
boats. Boss Rush's half share is now taken over all the escorts, first entries first (one each would round both
away): the cruiser sails there, as one of the two corvettes did before; Typhon's single corvette still stays home.

### C. Scylla, Boss Hunt, 4-11

Scylla is still Leviathan's variant: `variant.size` 0.62 -> 0.5 keeps it a 48 m destroyer on the bigger model (its
turret A, launch cells and forward CIWS; the dropped guns' nodes hidden), its own salvo (two 420 shells every 12 s, as
before) and its own big attack (`scylla_cruise` no longer builds on `leviathan_volley`: three cruise missiles as before).
Boss Hunt's trip to sea (`BossRushGoesToSeaForLeviathanAndBack`), the run and the clock, and `MissionPlaysToAnEnd` for
4-6 (Scylla) and 4-11 (Leviathan) pass.

### Tests (run once, then after fixes)

`Prompt16NavalTests` (the fleet: one cruiser, one corvette, three boats, nobody inside another's hull; 14 parts),
`BossPartsTests` (Leviathan 14), `BigAttackTests`, `ModelTests`, `VehicleLodTests`, `MuzzleAuditTests`, `ExportGameDoc`,
`Prompt20BossTests`, `Prompt20HuntTests`, `CampaignTests.MissionPlaysToAnEnd` (c4m06, c4m11). Failing and not touched here
(lead's): `BossPartsTests.ABrokenPartHurtsTheBodyByAThirdOfIt` and `ShootersGoForThePartMostDangerousToThem` (Behemoth),
`GearModelTests.AnOldSaveMigratesWithNothingLost`, `ModelTests.EveryWeaponMountHasAMuzzleOnItsModel` (the mobile
fortress's `boss_howitzer`), `ModelTests.RoundsLeave...` (3), `MuzzleAuditTests` (33 tower and boss mounts, none of them
the ships'). Captures: `Docs/art/leviathan/` (Blender's preview with the turrets trained, the fleet side by side).

### D. Ixion (`ixion`, `Tools/blender/mb_redesign_20y.py`)

The owner found it ugly and not scary. **References**: the Lebedenko "Tsar Tank" (1915: two 9 m spoked wheels on one axle,
the cabin slung between them, a trailing roller), the Ork "deff rolla" and battlewagon plating (Warhammer 40,000), the
Locust war machines' riveted slab armour and exhausts (Gears of War), the Shagohod's brute scale (Metal Gear Solid 3),
and scythed-chariot hub spikes. The model: two 10 m wheels with hollow studded treads, two rows of spikes, rusted rims,
eight I-beam spokes, an armoured disc and a 2.4 m scythe spike out of each hub; a war cabin in slab armour with rivet
rows, rust streaks, chains slung across the glacis, raked roof plates and red vision slits on the cupola; a spiked
roller drum on two arms across the front (the Crushing Charge's look); exhaust stacks with glowing mouths and soot; a
tail boom with a counterweight and the spiked steering roller. 21 x 12.7 m (17.5 m across the hub spikes), 22 k
triangles. Nodes and parts kept (`Part_wheel_l` / `_r`, `Part_steer`, `Turret` / `Muzzle_main`); data: length 21, width
12.7, radius 8.5, the parts' positions and radii moved with the model (wheels 5.0, the roller aft at 10.4 m).

### E. Icarus (`silver_bug`, `silver_bug_wreck`)

It looked like a space shuttle; the owner wants a film warship. **References**: the Imperial-class Star Destroyer (the
dagger plan, the side trench with its lit windows, the stepped superstructure, the command tower with its two shield
domes; Star Wars, 1977-83) and the Republic Venator (the dorsal flight-deck doors and its red stripes, drawn in the side's
colour; Revenge of the Sith). The model: a wedge hull (33.5 x 22 m) with greebles on its upper hull, three stepped tiers
with window bands, the tower, a seven-nozzle engine bank across the stern (`Thruster_main`), manoeuvring pods on struts,
a lit ventral hangar round the pod bay. **Kept**: every node's name and place (`mb_orbital.NODES`: the ventral laser
`Turret`, the coilguns `Mount_gun` / `.001`, the flak `Mount_mg` / `.001`, `Pd_laser_l` / `_r`, the five thrusters,
`Pod_bay`, `Uplink`) and the prompt 20 crash turrets `Mount_gun.002` / `.003` (now on the wreck too, which lacked them),
so the data, the altitude tiers, the crash (the `silver_bug_wreck` form, raised by `LIFT` onto its crater and debris) and
the parts are unchanged. The wreck: the same ship in dark plate, its back cracked, scorched, the tower broken off and
lying beside it. 14-16 k triangles. The Silver Bug's muzzle findings (m0-m2) are the same turrets' as on lead.

### F. The other bosses at the default zoom

Rendered one by one and judged side by side. Redrawn, each from its references, keeping every node's name and place:
- **Typhon**: the Project 941 Akula ("Typhoon"; The Hunt for Red October, 1990): a broad flattened hull in a dark
  anechoic coat with a waterline band in the side's colour, the missile hump, a long streamlined sail with its planes
  and masts, bow planes, a cruciform tail with twin shrouded screws, a dark sonar dome (was a glowing orange ball).
- **Caspian**: the Lun-class ekranoplan MD-160 ("the Caspian Sea Monster"): a flying-boat hull with chines and a planing
  step, a radome nose and glazing, the canard pylon with eight turbofans on it, the canister fairing, stub wings with
  flaps and endplate floats, the tall fin under its T-tail.
- **Daedalus**: it was the shuttle Icarus no longer is. Now Aurel's assault ship on the Republic Acclamator's lines
  (Attack of the Clones): a blunter wedge of the Icarus family with a spine, a bridge tower aft, six turbolaser turrets
  drawn along it, a five-nozzle engine bank, the three pod bays and the two hanging 30 mm guns as before.
Looked at and kept: Behemoth (and Tempest), Bastion, the mobile fortress, Hive, the mothership, Roc, the Earth Worm,
Charybdis, the supergun, both trains, the sky fortress, the gunship and Atlas are round 6 / prompt 16-19 builds with their
detail; Moloch and Kronos are plain first passes but read as what they are (a workshop, a bucket-wheel excavator) and are
left to the asset-debt list. The variants take their main boss's new model (Icarus Mk.0 the new Icarus).

### G. Boss death smoke

The owner: the smoke of a boss's death lasts too long and covers everything. It came from the fires, not the blasts: the
great blast lit a size-2 ground fire for 40 s, every part's fire relit for 25-35 s riding the wreck (14 of them on
Leviathan), and a boss's ruin burned like a tower's (45 s and 72 s), each then smouldering up to 45 s more under the
full black column. Now (`FireSpots.Ignite(..., smoke)`, `BossSmoke` = 0.35) those fires keep their size and flames but
smoke at a third of the rate, from a lighter, more transparent system (`Light Smoke`), and smoulder a tenth as long; they
burn shorter too (the great blast's 24 s, the parts' 14-20 s, a boss ruin's 20 s and 32 s). The finale's lingering puffs
are three lighter ones. The explosions themselves are unchanged (their own smoke lasts 5-8 s).

### Tests (the redesigns)

`OrbitalBossTests`, `Prompt20BossTests` (Ixion, Typhon, Daedalus), `BossPartsTests`, `BigAttackTests`, `ModelTests`,
`VehicleLodTests`, `MuzzleAuditTests`, `EffectsTests`, `FlashTests`, `Prompt16NavalTests`, `ExportGameDoc`: nothing new
fails (the lead's failures listed in C). Captures: `Docs/art/bosses_20y/redesigns.jpg` (Blender's preview). Card renders
are the lead's.

**Lead note (2026-09-29, the armour balance, 20X).** `BigAttackTests.SmokeDoesNothingToTheRailgun` fails since the armour balance (5b11cc5, checked on that branch alone). Against two MBTs, the one behind took 1.02 times the front one's damage, not 0.85, although the MBT's armour is the same on every face and both are hit head-on. The 1.2 overmatch or the narrower front arc probably touch the piercing slug's second hit. Listed for the testing phase.

## 21E. Play-test 6: the Gunship card, deck taps, the battle camera, the boss bar, the field tower, the mix (2026-09-29)

The owner's play-test 6 items marked [E] (`Docs/prompts/requests_vi.md`). Branch `feature/pt6-ui` from lead/integration
a864c3f. Agents F (behaviour, rates), H (effects, models, sizes), L (the bosses) and G (boss balance, economy, Boss Hunt)
do the other items.

### A. The Gunship (the owner's top item)

**Why it could not be found.** The sky gunship's card was retired in prompt 2 (`CardMerges.Retired`, its 4,500 coins
refunded) and 19B E.3 made `sky_gunship` `"card": false`: the AC-130 only flew for the one-use Gunship item
(`gunship_support`), bought in the shop's Items tab and called from the item strip. No card in the deck lists
(`MatchSettings.AllSupports`, `AllVehicles`) flew it. The deck screen's only "Gunship" was the short name of the Mi-24
(`gunship_heli`), a helicopter.

**Decision: a support card, not a vehicle.** `gunship_strike` (Escort, like the item): 12 CP, 120 s cooldown, 3 s
delay, the `sky_gunship` orbiting its mark for 20 s within 20 m (the item keeps its 30 s, no CP, one use). A support
because the design keeps the AC-130 a called aircraft (19B E.3: owned for a whole battle it would outclass every ground
unit, and neither the AI's buying nor the balance tables were built for it), the Escort kind already calls, posts and
times it (`StrikeSystem`, the `GuardPoint` of 19P), and "call it in battle" is what a support card does. Names: "Gunship"
in English, "Pháo hạm AC-130" in Vietnamese (short "Pháo hạm": prompt 21's scan keeps English words off the Vietnamese
screens); the Mi-24's English short name is now "Heavy
gunship" (its full name already was) so only the AC-130 reads Gunship. Route: premium, 4,500 coins in the shop's cards
(the old card's price; the heavy bomber is 4,000); unlocked in the test builds (`Progression.TestUnlockAll`). Its card
picture is the AC-130's render (`sky_gunship.png`, a manifest entry with the model's hash, no new render), its icon
`ac130`, its guide and info in both languages. The numbers are a first placing for G's balance pass.

**Proof:** `Docs/art/pt6/deck-gunship.png` (UiShots `screen-army-deck-gunship-en-full`: the demo profile with the card
bought and put in the deck: first support slot of the deck strip, and in the collection filtered to the supports, with
the new in-deck outline). The capture's debug screen `army-deck-supports` (the deck view with the Support filter) is in
`MenuScreen.ScreenNames`, so `UiLayoutTests` check it. Tall captures now measure the page's vertical scroll (the deck
page's first scroll view is its horizontal strip, which gave a 728 px "full" page).

### B. Deck

- **A tap on a card in the deck strip takes it out** (`DeckCard(..., removable: true)` → `ToggleInDeck`; the last card
  of a kind stays, with its note, as before). The strip's cards carry a remove mark (a cross on a dark square on the
  picture). The detail page stays a tap away from the collection card (its dialog: Info / Remove) and from the home
  screen's strip.
- **In-deck highlight:** a 3-4 px outline in the accent (`--fc-accent`) all round instead of a 1 px light line on three
  sides, the name in the accent, and a check on an accent square on the picture. The outline is drawn over the card
  (`fc-vcard__outline`), so the card's parts stay in line with its row's (`UiLayoutTests.CardsInARowLineUp`).

### C. Battle camera

- **Zoom buttons** in the compact HUD too (prompt 11 A1 had left them out: pinch only): plain faces in a second column
  beside select-all and box-select (the column wraps at two targets), ±25 % a tap about the screen's centre.
- **Deselect:** a close mark just over the selection panel's right-hand corner (compact and full; a fourth order widened
  the compact strip past the HUD's 30 % cover limit and broke "DESELECT" in large text), and a tap on a unit already
  selected clears the selection. A tap on empty ground stays a move order (it is
  the game's main order), so it does not deselect.
- **Mouse wheel:** Input System 1.20's default (uniform scroll) reports a notch as 1; the code divided by 120, so a notch
  zoomed 0.1 %. `TouchGestures.WheelZoom`: a notch is 15 % whether the system reports 1 or 120, at most three a frame.
- **Boss shots give the view back.** A boss's entrance (`StoryPan`) and the slow-motion shots of its phase change and
  fall (`StartCinematic`) hold the player's view (`RtsCamera.Hold`) and ease back to it when they end (`ReturnHeld`,
  about a second, exactly there after two). The slow-motion shot no longer closes in (it went to 82 % zoom). A pan,
  pinch, wheel, zoom button or minimap tap during a shot hands the view over at once and nothing is pulled back
  (`MatchRunner.TakeTheView`; the story pan used to keep pulling against the player's pan).

### D. Boss bar (compact HUD, prompt 11's)

The bar moves into the top row beside the goal or the bosses destroyed count (it sat in the column under them, two
lines of name and a row of 20 px part icons). Collapsed: 300 px wide (340), one line of call sign (the name before
" · ", `BossBar.CallSign`: "Juggernaut" of "Juggernaut · Armoured Train"), phase and chips over the bar, 16 px skull and
big-attack icons, parts 26 × 22 with 14 px icons (36 × 30 and 20 px). A tap opens it at full size on a line of its own
under the row (the row wraps). The column under the row starts at 96 px while the bar shows there (64 otherwise). The full HUD is unchanged.

### E. Field tower fire support

Two faults. The simulation put the tower exactly on the mark, checking only that the mark's centre was walkable, so its
hull could stand in a house's wall, on a tank or in another tower. And the parachute's canopy hung 5 m (scaled) over the
model's origin, through the middle of the taller watchtower. Now `SimWorld.ClearSpot` picks where it lands when it is
called (`StrikeSystem.Launch`, so the warning ring and the parachute use the same spot): the nearest spot to the mark,
in rings 2 m apart out to 16 m, whose whole footprint is open (the centre and eight points at the hull + 0.5 m), clear
of every ground vehicle by both hulls + 0.5 m, not in a gate or lane gap, and never in the enemy's camp; the mark itself
on open ground. `AirDrops`: the canopy rides 2 m over the model's own top (its meshes' bounds) and the cords meet the
top, for every airdropped vehicle.

### F. Sound

At the default settings the battle music plays at about 0.34 (bus 0.55 × music 0.7 × the track's trim); the rain loop
was 0.35 (rain) and 0.5 (storm) with the wind at 0.24 and 0.4 on top. Now rain 0.15, storm 0.18, sandstorm 0.1; wind
0.1 in clear weather, 0.12 rain, 0.14 storm, 0.2 sandstorm, 0.1 snow, 0.07 night (the lobby's 45 % as before): rain and
wind together stay under the music. Thunder 0.55 (0.85). **Ducking:** the music ducks only under alerts
(`MusicDirector.Alert`: to 60 % for 2.5 s when a boss's big attack sounds the siren or a fortress's alarm is heard);
nothing else ducks it in battle (the menu's In action range keeps its own duck).

### G. Tests

New `PlayTest6UiTests` (the Gunship card's data, name, route and picture, and only it reads Gunship; the card called
for its CP, cooldown, arrival and leaving; a field tower beside a house's wall and beside a parked tank, and on the
mark on open ground; the wheel's step at 1 and 120 a notch; a boss shot giving the view and zoom back and not after a
hand move; the call sign; the weather under the music and the alert's duck) and
`KitInteractionTests.ATapOnACardInTheDeckStripTakesItOut` (with `MatchSettings.SaveSuspended`, so the tap does not write
the player's saved settings). Captures: `Docs/art/pt6/deck-gunship.png`, `hud-boss-top-row.png`, `hud-deselect.png`.
Compact HUD cover (16:9): Conquest 29.2 % (28.5), a boss mission 26.1 % (27.1), Siege 29.6 % (28.9).

Run once each: compile; `UiLayoutTests`, `KitInteractionTests`, `L10nTests`, `L10nSwitchTests`,
`LocalisationScanTests`, `InActionTests`, `PlayTest6UiTests`, `SupportTextTests`, `CardRenderTests`, `RosterMergeTests`,
`RosterRoleTests`, `PlayTest5VisualTests`, `StringsTests`: 158 of 159 pass. **Failing, already on lead** (checked on
a864c3f with this work stashed): `RosterRoleTests.TheRadarRevealsGunsThatFireAndOurArtilleryHitsThemHarder`.

### Shared edits (merge by hand if they conflict)

`balance.json` (one support line after `sead_strike`), `Strings.cs`, `GuideText.cs`, `MenuScreen.cs` / `.Army.cs` /
`.Home.cs` / `.Shop.cs`, `MatchSettings.cs` (`AllSupports`, `SaveSuspended`), `Progression.cs`, `UI/Cards/manifest.json`,
`Tokens.uss`, `Screens.uss`, `KitCards.cs`, `BattleHud.cs`, `MissionBar.cs`, `ModeSessions.cs` (`ShowBoss`),
`MatchRunner.cs` (the camera's update and the HUD's wiring), `SelectionController.cs`, `TouchGestures.cs`,
`RtsCamera.cs`, `StrikeSystem.cs` (`Launch`), `SimWorld.cs` (`ClearSpot`), `AirDrops.cs`, `Weather.cs`,
`AudioDirector.cs`, `MusicDirector.cs`, `UiShots.cs`.


## 21H. Play-test 6: effects, models and sizes (2026-09-29)

The owner's play-test 6 items marked [H] (`Docs/prompts/requests_vi.md`). Branch `feature/pt6-vfx` from lead/integration
a864c3f. Nothing here changes the simulation's behaviour: one read-only accessor (`Vehicle.MountCooldown`) for the
view. Every redesign follows outside references, listed per item (the owner's rule). No fire or blast is smaller,
except the heavy fortress's blasts, which the owner asked to shrink.

### A. The siege tank, after StarCraft 2's siege tank

**References:** StarCraft 2's Siege Tank (Crucio), tank mode and siege mode: the low wide body between four armoured
tread pods with a turreted twin cannon, and the transformation (legs out, the hull braced and raised, the turret
turning round, the shock cannon running out and locking); the M110 and 2S4 Tyulpan for the recoil spades.

**Model** (`Tools/blender/mb_p22_siege.py`, rewritten): an 8 m hull, low (roof 1.38 m instead of 1.72) and wide
(4.2 m over the legs), between **four armoured track pods** (team-coloured wedges over each end of the tracks, trim
and vents), a glacis plate, two big exhaust stacks and an engine grille. A **broad turret with two ends**: the twin
105 mm (`Deploy_gun`, `Muzzle_gun` on the right barrel's brake) at one end, the **240 mm siege cannon** at the other:
a heavy cradle on trunnions, an outer sleeve with a team band, the inner tube with a **lock collar**, and a big muzzle
brake, drawn run in (`Main_cannon_cradle`, `_sleeve`, `_tube`, `Muzzle_brake`, `Muzzle_brake_ports`, `Muzzle_main`).
**Four hydraulic legs** fold along the pods' tops (`Deploy_brace_l/_r` front, `Deploy_leg_l/_r` rear), each with a ram
housing at its tip (`Deploy_*knee_*`) and a ram with a clawed foot pad (`Deploy_*ram_*`); two rear stabiliser spades
(`Deploy_spade_l/_r`); the turret on its ring (`Deploy_riser`); a roof M2. 15,472 triangles (was 10,704).

**Drawn sieged, spawned in tank mode.** The turret is drawn with the siege cannon forward, so its barrel group gets
the usual elevating pivot (ModelLibrary lays barrels whose muzzle points forward); `ModelLibrary.RestTurretYaw` turns
the turret round on the template, so every copy (the menu's preview, the level-of-detail bake, the battle) starts in
tank mode: twin guns forward, the stubby cannon over the engine deck. `VehicleView` adds the turn (`_turretSwing`, 180
in tank mode) to the sim's turret heading, so the twin guns face what the 105 mm shoots.

**The sequence** (`VehicleView.AnimateSiege`, the data's 2.5 s kept, packing up runs it backwards): the twin guns
slide 0.9 m into the turret (4-30 %); the four legs swing out from the pods (yaw 120 degrees, 0-26 %) and tilt 25
degrees down (14-36 %); the rams drive the pads on to the ground (28-46 %, the ram housings kept upright) and the
spades bite (30-50 %, 140 degrees); the rams push on and **lift the hull 0.25 m** (44-62 %); the turret's ring unlocks
0.15 m (40-48 %) and **the turret swings round** (46-74 %), bringing the siege cannon forward; **the cannon runs out**
1.9 m (70-86 %) and knocks 7 cm past and back as its collar **locks** against the sleeve (86-92 %); last it swings up
(from 88 %) and is laid by range at 55-72 degrees (45 idle), now at 150 degrees a second during the work so it keeps
pace. The tube and brake run out as recoil parts (`BarrelRunOf`), so the recoil still kicks the whole barrel.

### B. Launchers raise their launcher to fire

**References:** HIMARS and M270 (the pod raised and traversed to fire), BM-21 Grad and TOS-1A (the tube pack laid
by range), BM-30 Smerch, Buk (the rails laid on the target), S-300 (the canisters stood upright), 9K720 Iskander
(the missile erected upright), Patriot (the box raised to 38 degrees, flat for travel), the Shahed truck's rail,
the Lancet box launcher, and the Bradley's TOW launcher (raised from its stowed pose beside the turret).

`VehicleView.Launchers.cs`, view only. Each launcher has an erector profile (`Erectors`): laid at its target
(`Aimed`: mlrs, elite_mlrs, elite_grad, heavy_rocket_artillery, thermobaric_launcher, rocket_technical, sam_launcher)
or raised a set way from the pose it is drawn in (`Raised`: long_sam and elite_long_sam +84, stood upright;
ballistic_launcher +66, from its drawn 20 degrees to 86; lancet_truck +34; missile_battery and shahed_truck are drawn
at their firing angle and travel lowered, 34 and 12 degrees), with the erector's seconds (0.7-2.0). The launcher
comes up when its next round is within its erector's time and a second and it has a target or an enemy near; it
stays up while rounds follow and goes down to its travel pose while it reloads (a long cooldown or an empty
magazine) or once nothing is about. **No sim delay:** the sim has none for launchers (the railgun's charge is a
weapon of its own, and adding one would change fire rates, which is agent F's), and a ready launcher fires the moment
it has a target, so the director marks launchers with an enemy of their layer inside 1.25 times their reach
(`EffectsDirector.WarnLaunchers`, five times a second, `ThreatAt`): they are up before the enemy is in reach. A round
fired before the launcher is up (an enemy appearing inside the reach) still lays it at once (`LayForShot`) and holds
it up 1.2 s before it lowers. Models whose erector is drawn under other names join the elevating group
(`ModelLibrary.ErectorParts`: the Iskander's erector and missiles, the Shahed truck's rack and drone, the Lancet
truck's cell box). **ATGM carriers:** the IFV's and the elite APC's ATGM box gets its own pivot (`Deploy_atgm`, at the
box's rear foot; `ModelLibrary.SideLaunchers`) instead of riding the gun, and comes up 16 degrees to fire its missile
(`RaiseSideLauncher`, by the missile mount's target and cooldown, `Vehicle.MountCooldown`).

### C. The SEAD strike

**References:** the AGM-88 HARM's dive on to a radar, the SEAD and HARM hits of Battlefield and Wargame (an
electronic kill: a blue-white flash, arcing and a dead radar).

The anti-radiation missile is drawn 1.8 times a Maverick (`StrikeEffects.SeadScale`) with a long bright motor flame
and a thick smoke trail (`Plume(2.4, 0.3, 1.9, 1)`); it leaves the jet, pulls up over a crest 8 m above the jet's
height and dives steeply on to its air defence; six red points turn round the locked radar and close in on it, with a
red pulse over it, as the missile nears (`LockOn`). On the hit, on top of the warhead's blast (kept): an **electronic
kill** (`EffectsDirector.SeadKill`): a white-blue flash, two electric shock rings (10 and 6 m), 7 arcs crawling over
the vehicle, 48 hot and blue sparks, the smoke of burnt-out electronics, a light flash. **Disabled for its 8 s:** any
knocked-out vehicle (the SEAD strike's stun, and the EMP's, which showed nothing before) now shows it while it lasts
(`ShowStunned`): arcs crackle over the hull, blue sparks spit off it, burnt electronics smoke, and its radar stops
dead and slumps 50 degrees on its mount (`VehicleView.Spin`), coming back up when it recovers. Low: glow points
instead of arcs, fewer sparks. The big circle stays: it is where the strike looks for an air defence (20 m).

### D. Blasts

`BlastSizes.TurretBigger` 1.2: the gun turret's rounds (its 120 mm, the long branch's and the autocannon branch's
57 mm) 20 % bigger again (1.56 over 11A; 2.18 on the 120 mm's shell hit). `BlastSizes.FortressSmaller` 0.8: the heavy
fortress's twin 155 mm (and the coastal branch's) 20 % smaller, the owner's ask (its ground ring, smoke and scorch
follow the drawn size).

### E. Aircraft 15 % smaller

`VehicleView.AirShrink` 0.85 (the owner asked for 10-20 %) on every flying unit alike (planes, helicopters, drones,
the escorts), so their sizes against each other stay (`DrawScaleOf`); bosses keep their size (the boss agent's). The
support aircraft drawn by the strikes (the strike jets, the recon drone) and the transport take the same scale. The
muzzles and mounts are on the model and shrink with it; the view's other uses of the scale (the health bar's height,
the level-of-detail size, the impostor, the shield, the nav lights, the engine trails, the mission markers) follow the
drawn scale. The simulation's radii, altitudes and reach are unchanged.

### F. Fire on vehicles and bosses

**References:** burning tanks in World of Tanks (flames out of the engine deck, the black column), Battlefield 4 and
1 (a disabled vehicle's fire, sparks and smoke, the flare-ups), Company of Heroes 2 (fire licking from hatches, smoke
streaming behind a moving vehicle).

`HullFire` rewritten (it replaces 20V's look and prompt 9's boss part fires). Sources where a hit vehicle catches:
the **engine deck** (a wide grille, flames across it), the **turret's hatch** (a tall tongue out of the hatch, turning
with the turret) and a **breach in a flank** (flames licking out sideways and up); one, two or three as the damage
grows. Each source each beat: a hot glow on the metal, tall narrow tongues pinned at their base (the flame sheet at
its natural speed, 0.55-0.85 s), small flickers in the opening, sparks spat out as streaks falling back, embers, and
dark smoke pouring out and rising. **Attached:** every source is placed on the hull each beat and every flame carries
the hull's velocity, so the fire moves with the vehicle; embers keep 60 % of it and the smoke 25 %, so the smoke
streams out behind a vehicle on the move. **Flare-ups:** now and then (every few seconds, more often as it worsens) a
burst of taller flames, a pop of light, a shower of sparks and a gout of black smoke. **Bosses:** their fire points
(broken parts, parts under a quarter, the body's stages; `FireBudget` caps kept) burn the same way (`FeedPoint`, 2.2
times a point's size) instead of the ground fire riding the boss; the death flare-up bursts them; the wreck still
burns on the ground. **No heat shimmer:** a refraction pass needs the camera's opaque texture, which the phone
renderer (`Mobile_RPAsset`) leaves off. **Low:** at most two sources, a 0.12 s beat, one tongue a beat, no flickers,
half the sparks and embers, smoke every other beat, smaller and rarer flare-ups.

### Tests and captures

`PlayTest6VisualTests` (5): the siege tank spawns in tank mode with its legs, housings, rams and telescoping cannon
apart and the pads reaching the ground; every launcher has an elevating erector, the Iskander's, Shahed's and Lancet's
parts ride it, and the IFVs' ATGM box has its own pivot with the missile muzzle on it; aircraft drawn 15 % smaller all
alike, bosses and ground vehicles not; the fire moves with the hull and its smoke trails, Low flares up less, a boss's
part fire burns the same way; the SEAD missile drawn big. `BlastSizeTests` takes the turret's and fortress's factors.
Run once each (compile, then the filters): `PlayTest6VisualTests` 5/5, `PlayTest5VisualTests`, `EffectsTests`,
`FlashTests`, `VehicleLodTests`, `BlastSizeTests` pass; `MissileFlightTests`, `ModelTests`, `MuzzleAuditTests` with
the known failures only (`sam_battery_lrr`'s flight; `mobile_fortress`'s `boss_howitzer`; `RoundsLeave` x3; 36 tower
and boss muzzle rows; the siege tank's twin gun passes). Captures in `Docs/art/pt6/`: `siege_tank.png` (the In action
clip: tank mode firing, the legs out, the turret swinging round, the cannon up and firing), `launchers_mlrs_iskander.png`
and `launchers_s300_tos.png` (raised to fire, lowered after), `sead_strike.png` (the HARM's dive and the kill),
`hull_fire.png` (`EffectShots.HullFires`: 28, 15 and 4 % on High, 4 % on Low, and a tank at 10 % driving, its smoke
trailing). Card renders are the lead's (the siege tank's changed).

### For the testing phase

The siege tank's sequence at the default zoom on a phone; whether launchers warned by a far enemy bob up and down
at the edge of their reach; the fire's cost with many burning vehicles on Low; the SEAD kill's read at the battle
zoom.

## 21F. Play-test 6, combat: dogfights, cannons that keep firing, straight missiles, rhythms, damage, blasts, towers (2026-09-29)

The owner's play-test 6 items marked [F] (`Docs/prompts/requests_vi.md`), two additions sent during the work (towers
without a forced machine gun; missiles bursting inside a boss), branch `feature/pt6-combat` from lead/integration
a864c3f. The calibre scale (13B, CalibreTests' bands), prompt 15's penetration steps, 19R's missile speeds and 20W/20X
are kept; where a change reaches one of them it says so.

### A. Jets: a dogfight ends with one on the other's tail

**Measured first.** 20W's tail chase works on a jet that does not hunt back (the fighter on an attack jet: 37-54 s of
a minute on its tail). Two fighters told to attack each other never got there: both flew lag pursuit for a point
behind the other and turned round one circle for the whole minute (0 s on a tail of 60, 38 cannon rounds each).

**Now** (`MovementSystem.Dogfight`, `Vehicle.Defending`, `Vehicle.BreakingOff`):
- **Roles out of the merge.** When the enemy jet hunts it too (its target, cannon reaching aircraft) and it is within
  2.2 x its guns' reach, the jet worse placed (the enemy further astern of it than it is of the enemy, by 0.25 on the
  cosine; level, the later spawned) **defends**: it runs out, bending away from the enemy and weaving, at 82 % power
  (the jinking costs speed, so the chaser closes to its cannon's reach). It turns in again past 2.6 x reach or when the
  enemy slips in front of it (an overshoot). Never decided head-on, where both fire.
- **The chaser holds on:** inside the jet's rear cone and 1.4 x reach it turns 1.3 x quicker with it, and it is not
  sent back to the middle by the map-edge rule while it chases (it lost the tail there; the jet ahead turns back itself).
- **Breaking off:** under 30 % of its health a jet in a dogfight breaks off: it flies away from the enemy jet at full
  power and chases it no more (the tactical AI's refit, at 35 %, then takes an AI jet home; this covers the player's).
- **On a helicopter** (a hold, 12F): with its cannon on an aircraft and no flak about, the hold is renewed while the
  target stays in reach: a VTOL fighter hovers on it until it dies; the stealth fighter crawls on and passes only when
  over it. Under flak it still breaks away.

**After:** the two fighters: one on the other's tail 42 s of 60 (22 + 20, runs of 20 s and more), 314 cannon rounds;
the fighter on a helicopter 277 rounds in 40 s (124).

### B. Aircraft whose weapon is an autocannon keep firing

- **The attack jet** (its main weapon is its cannon): an attack hold lasts a whole magazine's stream (5.6 s; the data's
  3.8 before), and its cannon leads through the hold (`CombatSystem.Leads`: a jet in a hold streams its hull cannon on,
  as on a tail): 263 cannon rounds in 40 s on a ground target (210). A fighter in a hold on a helicopter streams too,
  its air-to-air missiles beside the stream (20W's rule for a jet on a tail). The attack jet's rockets, bombs and
  missiles still take their turns round the stream (with them fired beside it as well it measured +26 % combat value,
  without +17 %).
- **The anti-air vehicles** were measured, not changed: they stream at what comes into reach (the ZU-23 142 rounds,
  the gun-missile system 197 on an attack jet diving at them in 40 s); nothing of theirs orbits.
- **The heavy gunship** (`gsh30k`, 145 rounds in 40 s) and the sky gunship (its pylon turn) already fire all the time.
- **Not changed: the attack helicopter.** Its main weapon is its missile: it holds at its Hellfires' 52 m (the Ka-52
  standoff) with its 26 m gun silent, which `AirAttackTests.AnAttackHelicopterComesIn...` has failed on since the
  standoff came in. Letting it come in to its gun when no anti-aircraft gun or missile covers the spot was built and
  measured: +65 % combat value (light and tank groups doubled, the 4-minute mixed run -64 %). It is left for the owner:
  it is firing, not circling.

### C. Missiles

**Slower** (20 % again; `MissileFlightTests` and `PlayTest5Tests` pin them): the attack jet's `s8_pods` 36 → 28.8,
`kh29` 17.25 → 13.8, `r60` 18 → 14.4; the rocket technical's `technical_rockets` 48 → 38.4; the scout helicopter's
`scout_rockets` 48 → 38.4; the heavy gunship's `gunship_rockets` 48 → 38.4 (the mega gunship boss fires the same row)
and `heli_atgm` 21 → 16.8. Every flight stays under its cooldown.

**The jerking missiles: the cause was in the view.** The guidance was measured frame by frame (a Hellfire on a
target crossing at 8 m/s, 30, 60 and 144 fps with the frame time varying ±20 %): a smooth line, the nose never
wagging. The jerk was `ProjectilePool`: 96 models for every missile, rocket, drone, bomb and modelled shell in the air,
and with all of them busy a launch took the next slot anyway, so a round in mid-flight vanished and reappeared at a
launcher as another. Since 19R and 20W slowed the missiles and rockets (a 24 m/s rocket flies 2-6 s; one Smerch salvo
keeps 11 up for 6 s, a Hind 38 rockets), busy fights run out. **Now** the pool grows (to 512) instead of taking a
round out of the air. The homing's ease is by time (`1 - e^(-13 dt)`, the old 0.35 a frame at 30 fps) instead of a
fixed share a frame (four times quicker at 144 fps). Tests: `PlayTest6FlightTests`.

**Missiles burst on a big target's hull** (the owner's addition: they flew into the Matriarch's middle). The simulation
aimed a guided round at the target's middle and burst it there. **Now** (`HullContact`) a round fired straight at a big
target (a boss, or a hull 4 m or more from its middle to its edge: big ships, large aircraft, the large towers) bursts
where the line from its launch point to the middle crosses the hull's footprint (the data's length and width: a
capsule along the heading), or, aimed at a boss's part, on that part's hitbox towards the shooter; the blast and its
splash are centred there. Rounds that come down from above (lobbed, dropped, diving drones, top attacks) still burst
on the roof. The damage and the face struck are as before: the face is the one turned to the shooter, and the contact
point lies on that line, so it is the contact point's face. The view flies a guided missile onto the same point
(`WeaponEffects.HomeOn`). Test: a SAM at the Matriarch and an ATGM at Leviathan burst within 1 m of the hull or the
struck part's edge (before, they burst in the middle: 12 and 6 m inside).

### D. Rhythms

- **The light tank** (`gun_57mm`): one round every 2.53 s (a pair 0.5 s apart every 5.06 s), the damage a second kept,
  then E's +10 % on the round (70 → 77).
- **Machine guns** (every `mg` row but the bosses' `boss_minigun` and `boss_hmg`, left to the boss pass): a magazine
  15 % longer and a change 15 % shorter, less where the change is most of the cycle so that none gains more than about
  12 % a second: `mg_jeep` 25 → 28 rounds, 2.23 → 1.94 s; `mg_coax` 36 → 41, 1.87 → 1.59; `hmg_roof` 25 → 28, 2.32 →
  2.02; `minigun` 60 → 64, 5.17 → 4.81; `door_gun` 40 → 46; `tower_hmg`, `bunker_hmg(_twin)`, `mg_coax_ground`,
  `bomber_tail_guns` alike. +5-12 % a second: the machine guns' share of E.
- **Drones, steadily:** the FPV carrier, the Shahed launcher and the drone mothership launch one drone at a time.
  The rate was first the old average (a salvo's cycle over its drones), but single drones waste none on a target
  already dying and the mothership's stores come back over the field, so it measured the Shahed +48 %, the FPV carrier
  +23 % and the mothership +73 %; decided: `fpv_swarm` one every 2.8 s, 16 then 9 s (four of four, then 16 s),
  `shahed` one every 8.5 s, 5 then 8.5 s (five, then 30 s), `swarm_drones` one every 3.3 s (eight at once, 12 s).
  An aircraft's drone bay lets its drones go whichever way it faces (they fly to their own targets), and each single
  drone of a swarm still picks its own target round the aim (`SwarmTarget`, which before served a salvo's later
  drones only), not one of the last two it sent. The Lancet was already one at a time; the drone hangars (towers) and
  the bosses' drones are unchanged.

### E. Damage +5-10 % by vehicle, on the calibre scale

**The rule** (applied once to `balance.json`): a card's uplift by its cost, **+10 % up to 4 CP, +7.5 %
at 5-9, +5 % from 10** (the cheap cards gain most; the aircraft gain through A and B as well); a row several cards
carry takes their mean, an elite its card's. **Where the calibre band has room and every carrier of that real weapon
is a card**, the round is raised (to the band's top at most, never past a bigger calibre of its family), for every row
of that real weapon (`TheSameRealWeaponHitsTheSameOnEveryCarrier`); **the rest, or all of it where a tower or a boss
shares the round**, goes into the rhythm: a shorter cooldown (a salvo's whole cycle), a launcher's explicit reload
with it, and for the 5 s autocannons (20W) more rounds in the same 5 s stream at a quicker cadence (the 5 s / 1 s
rule kept). No band, no penetration step and no damage type moved (`CalibreTests` pass).

| Examples | Round | Rhythm |
|---|---|---|
| light tank `gun_57mm` (+10 %) | 70 → 77 | (D) |
| MBT `gun_120mm` (+7.5 %, bosses share it) | 240 kept | 5.48 → 5.10 s |
| heavy tank's L7 `gun_105_bunker`, siege tank's `siege_gun_105` | 200 → 212 | 4.6 → 4.54 s |
| 125 mm rows (`gun_105_long`, `gun_125_elite`, `gun_105_apfsds`) | 250 → 260 (band top) | the rest |
| `ifv_30`, `twin_30_bmpt` (+7.5 %) | 22 kept (a boss's 2A42) | 24 → 26 rounds in 5 s |
| `flak_35`, `twin_35_ahead` (+10 %) | 25 → 26 (band top) | 21 → 22, 23 → 24 rounds |
| `zu23` (+10 %) | 14 → 15 | 56 → 57 rounds |
| `jet_cannon`, `gsh30k` (+5 %) | 22 → 23 | |
| `fighter_cannon` (+5 %) | 17 → 18 | |
| Hellfires (`heli_atgm`, `hellfire_*`, `drone_missile`) | 250 → 260 | |
| air-to-air (`air_to_air`, `wvr_aam`, `r60`, `stinger_atas`, `aim9`) | +5-7.5 % | |
| rockets 70 / 80 / 107 / 227 (elite) / 300 mm | 28 → 30, 32 kept (a boss's), 45 → 49.5, 100 → 105, 140 → 145 | the rest |
| bombs 110 / 250 / 500 kg, the stealth bomber's, the car bomb | 200 → 210, 300 → 310, 400 → 420, 850 → 892, 700 → 770 | |
| howitzers, the MLRS, Grad, TOS, mortars, the Lancet and FPV rows (a tower's round too) | kept | 7.5-10 % quicker |
| the mine layer's mines | 450 → 484 | |

**Shared rows:** the towers and bosses that fire a card's row take its new rhythm: `autocannon_30` (Daedalus, Kronos),
`gun_120mm` (Behemoth, Silver Bug, Moloch), `sam` (the AA tower), `gunship_rockets` (the mega gunship),
`gunship_105/40mm/25mm` and `griffin` (the sky fortress); the machine guns' change is every tower's as well. For the
boss pass (G): these bosses are already 5-7.5 % up. Not changed: bosses' and towers' own rows, naval units, escorts,
strikes and blasts.

### F. Blasts, weapons and towers

- **The Lancet** has no blast in the simulation (a shaped charge on what it hits): its blast is drawn a fifth bigger
  (`impactScale` 1.2).
- **The long-range SAM**: measured, the S-400's round already had a 3 m blast and a Large burst against the SAM
  launcher's 2 m and Medium; the owner still found it small (it bursts round aircraft far off, often the ceiling-high
  jets). Decided: 3 → 3.6 m and Huge (the view's air burst x1.8 against x1.35).
- **The drone mothership** gets two guided bombs a load (`guided_bomb`, the GBU-39 the strike drone and the stealth
  fighter carry), dropped from its drone bay (its model has only `Muzzle_drone`, so the mount uses that slot). Guide
  and card note in both languages.
- **The C-RAM's gun fires only at incoming rounds**: `c_ram_gatling` is `interceptOnly` (`WeaponDef.InterceptOnly`: it
  takes no target on either layer), so it never lays on an aircraft or a vehicle; its bursts at rockets, missiles,
  shells and drones (the APS, 20W) are as before, both branches. The tower fit no longer counts it as anti-air. The
  Iron Dome branch keeps its Tamirs.
- **Towers keep a machine gun only where the real one has one** (the owner's addition): removed from the rocket
  battery, the artillery emplacement, the Patriot battery, the SAM post branch and the coastal turret (and its coastal
  branch, which inherits it). Kept: the MG bunker, the guard tower, the steel fortress's turrets, the gun turret (a
  tank-gun turret has its coaxial gun), the HQ and the spawn bastion. No test asks a tower for two weapons (checked);
  `TowerGearTests`' three failures are the same on the lead's tree (run with this work stashed): sabot rounds need
  only an armed tower since prompt 15, so they fit the missile battery and the SAM branch. Guides and the SAM branch's
  line updated in both languages.

### G. Measured

`CombatValueMeasure` (one seed, 13, before on the lead's tree and after; `Docs/balance/combat_value_pt6_*`):
the median cell **+0.9 %** (322 cells over 20 points), the ground median +1.2 %; 113 cells moved more than 10 % (one
seed; the aircraft's 4-minute runs are as noisy as 20W found). Up most: the Shahed launcher +22 %, the attack jet +17 %
(its full-magazine holds), the strike drone +15 %, the Lancet truck, the armoured bulldozer, the scout jeep and the drone
mothership +14 %, the FPV carrier +12 %. Down most: the flame tank -16 %, the car bomb -12 %, the IFV -11 %, the twin
tank -10 % (everything round them hits harder and they gained least). On aircraft: the gun-missile system +31 %, the
anti-air vehicle -33 %, the SAM launcher -10 %, the fighter -6 %, the stealth fighter +78 % (from 70 points: its
dogfights); `CounterTests` pass (SAMs beat jets, anti-air beats helicopters, fighters beat helicopters). The first run,
before the fixes of B and D, is in this section's text.

`ArmourBalanceMeasure` (`Docs/balance/armour_ttk_pt6_*`): fights between units 5-15 % shorter (a battle tank on a battle tank 34.9 → 33.0 s front,
25.6 → 23.4 flank; two armoured cars on two 15.2 → 13.6; an IFV on a battle tank 36.6 → 31.1; the anti-air vehicle on an
attack helicopter 25.2 → 20.3), a tower's fire unchanged (towers were not raised, but for their machine guns: the MG
bunker 19.6 → 18.1); longer only for the FPV carrier on a battle tank, 36.0 → 43.2 s (its active protection takes the
single drones one by one, where a salvo of four got through).

### H. Tests

New `PlayTest6Tests` (the mutual dogfight, the break-off, the fighter on a helicopter, the attack jet's and the heavy
gunship's cannons, the standoff helicopter out of flak, the C-RAM never on aircraft and still on rockets, the missile
at the Matriarch and at Leviathan, the new data) and `PlayTest6FlightTests` (the straight line frame by frame, the pool
growing). Updated for the intended changes: `AirAttackTests` (the fighter on a helicopter holds on instead of looping;
renamed), `PlayTest5Tests` and `MissileFlightTests` (the new speeds), `Prompt17ContentTests` (the mothership's drones one
at a time), `AbilityTests.JammerMakesGuidedMissilesMiss` (its target holds fire so the carrier lives to launch singles),
`WeaponRhythmTests.MainGunAndMachineGunTakeTurns` (30 s for the longer streams). Run: those, `CounterTests`, `CalibreTests`, `TowerGearTests`,
`TowerRosterTests`, `InActionTests`, `ContentTests`, `LocalisationScanTests`, `RosterRoleTests`, `RosterBalanceTests`,
`ApsTests`, `AircraftTests`, `AirRealismTests`, `AirMotionTests`, `TowerBranchTests`, `CounterBuyTests`, `BlastSizeTests`,
`ModelTests`, `MuzzleTests`, `FlashTests`, `BigAttackTests`, `Prompt16NavalTests`, `Prompt20BossTests`, `SiegeModeTests`,
`AiReviewTests`, `CombatTests`, `ArmourTests`, `BossPartsTests`, and the two measures.
**Failing, already on lead** (each checked on the lead's tree, this work stashed) and not touched:
`AirAttackTests.AnAttackHelicopterComesIn...`, `AirRealismTests.TheGunshipCirclesItsTargetWithItOnTheLeft...`,
`AiReviewTests.FortressBuildingsPayABounty...` and `...TheLosingSideIsReinforcedFaster...`, `BossPartsTests.ABrokenPart
HurtsTheBodyByAThirdOfIt` and `...ShootersGoForThePartMostDangerousToThem`, `GearModelTests.AnOldSaveMigrates...`,
`MissileFlightTests` on the tower `sam_battery_lrr`, `ModelTests.EveryWeaponMountHasAMuzzle...` (mobile_fortress) and
`...RoundsLeaveFromTheLaunchersOnBothSides` (3), `Prompt16NavalTests.LeviathanSailsWithItsFleet...` and
`...TheSeaLanesAreInReachAsDesigned`, `RosterRoleTests.TheRadarRevealsGunsThatFire...`, `TowerGearTests` (3, above).

### Shared edits (merge by hand if they conflict)

`balance.json` (about 90 weapon rows, `swarm_carrier`, `mine_layer`, five tower rows), `MovementSystem.cs`,
`CombatSystem.cs` / `.P17.cs`, `DamageSystem.cs`, the new `HullContact.cs`, `Definitions.cs`, `Catalog.cs`,
`Vehicle.P17.cs`, `WeaponState.cs`, `ProjectilePool.cs`, `WeaponEffects.cs`, `GuideText.cs`, `Strings.cs`, and the tests
above.

## 21B. Play-test 6 bugs: mission 1-1's Start, the gunship test, the boss page (2026-09-30)

On feature/pt6-bugs from lead/integration 84d4069.

### Mission 1-1's Start did nothing

- **Reproduced in Play mode** with a new tool, `MachineBrigade.Editor.MenuWalk.Run` (`-mbWalkProfile fresh|old|demo|prefs`,
  `-mbWalkMission c1m01|next`, `-mbWalkBack <n>`). It taps the real menu through the panel at each element's centre
  (Campaign, the chapter, the mission row, Start, each story card's main button), reports what was on top at each tap,
  and waits for the battle. The profile is loaded in memory with saving off, because the editor's prefs are shared by
  every tree. A new profile, an old save of the nine-chapter story (roster 1, gear 4) and the editor's own profile all
  reached the battle, with no exceptions and nothing covering a button. **One Back first broke it**: Start then showed
  nothing, and the chapter card's "seen" mark was used up.
- **Cause**: `MenuScreen.Back` closed "the dialog" with `Root.Q(className: "fc-scrim")`. The story card (chapter
  openings, briefings, epilogue) is a scrim too, is built once and stays in the menu hidden, and was added before every
  later page, so the query found it first. The first Back with no dialog open took it out of the menu for good (the
  top bar's Back, Android's back button or Escape: going from a chapter's missions back to the chapters is enough).
  Start then filled and "showed" a detached card. A Back with a real dialog open also took the story card and left
  the dialog. It was always wrong (Field Command 2.0), and it shows at 1-1 because that is where a new player first
  sees a story card.
- **Fix**: Back closes the topmost scrim that is open (the last in the tree), treating the story card as open only when
  it shows, and hides the story card instead of removing it. `StoryCard` also keeps its host and goes back into it if
  something took it out. The chapter's "seen" mark stays where it was (set when the card opens).
- **Test**: `CampaignStartTests` walks the same taps with the UI test framework's clicks for c1m01 (new profile, with
  and without a Back first, and the old save) and the demo profile's next mission (3-4), to the play callback, with
  Campaign mode and the mission set. It also checks that Back closes a real dialog and keeps the story card.

### The gunship test (AirRealismTests, 0/0)

The game was fine and the test broke. A trace over 13 s: the AC-130 reaches its 22 m orbit in 2 s, keeps the target on
its left every sample after that, fires its 105, 40 and 25 mm guns and the Griffin, and kills the heavy tank (3,520
health since the armour pass's toughness 2.2) in 12.5 s. The test waited 12 s before sampling, found the tank dead and
sampled nothing. It now samples from 3 s until the kill, needs at least 8 samples, and checks the farthest distance
while circling. The id is still `sky_gunship`, which the `gunship_strike` card calls; that card's own test is in
`PlayTest6UiTests`.

### The boss page (the owner: a boss detail shows "next level" and equipment)

- **One home, the detail page of a boss** (the boss wiki). Prompt 20 pass 3 made it the Guide page (19N), with the
  dock already empty, but the Stats tab still showed the card's gear and next-level gains, the class average and the CP
  cost, and the Equipment tab offered gear. Now, for a boss: no Equipment tab (hidden, and a page left on it opens on
  the file); Stats shows its numbers at campaign strength without gear, next level, average or cost, with a line saying
  a boss is no card, its armour on each face and its part count; the file (Guide) shows the name and subtitle (the
  title), rank, chapters, general, variant links, escorts (the wave that arrives with it and how many come at phase
  changes), each part with its armour and health, its altitude tiers and its big attack (these two were shown only for
  bosses with parts before).
- **`BossFile`** (Game/Hud) builds those facts, so the Sandbox shows the same file. **Every way in**: the week's Boss
  Hunt and the full hunt on Operations (already `OpenBossGuide`), the dossier's boss files (already), the campaign's
  mission page (new: a "Boss file: <name>" link for each boss the mission or its stages fight), and the Sandbox.
  Decision: the Sandbox runs inside a battle with no menu, so its boss entries (an info button on each boss in the
  unit list, and a "Boss file" button in the selected boss's tools) open the file as a dialog, not the menu page.
- The story card's briefing keeps its two buttons. The link sits on the mission page, next to the briefing it repeats.
- Strings (both languages, named placeholders, "boss" in Vietnamese as 20L says) are in `BossText` under "the boss
  file". `detail-boss` and `detail-boss-stats` join `MenuScreen.ScreenNames` for UiShots and the layout checks.
  `CampaignStartTests` checks that a boss page has no Equipment tab, no level, blueprint, deck or upgrade controls and
  no gains, and that the Sandbox's card carries the facts.

Tests run: CampaignStartTests, AirRealismTests, CampaignTests, KitInteractionTests, UiLayoutTests, PlayTest6UiTests,
L10nTests, Prompt20CampaignTests: 279 passed, 0 failed (145 of CampaignTests are explicit). Play mode: MenuWalk on new,
old, editor and demo profiles, with and without Back.

Files: `MenuScreen.cs` (`Back`, the debug screens), `StoryPanels.cs`, `MenuScreen.Detail.cs` (`BossStats`, the tabs),
`MenuScreen.BossParts.cs`, `MenuScreen.Campaign.cs` (`MissionBosses`), `BossFile.cs`, `SandboxScreen.cs`,
`BossText.cs`, `Editor/MenuWalk.cs`, `Tests/EditMode/CampaignStartTests.cs`, `Tests/EditMode/AirRealismTests.cs`.


## 21S. The Sandbox's screen made lean (2026-09-30)

The owner: the Sandbox's screen "is too much and takes space everywhere; optimise it" (requests, 29/09 23:50). Before,
three full panels stood on the battlefield at once (the picker 300 px down the left, the selection 330 px down the
right, a full-width bottom bar), over a battle HUD that still showed waves, the commander's switches, select-all and
box select. Now the battlefield keeps the screen; a panel shows only while it is used.

### Layout (phone first: the 1280 x 720 reference panel)

- **Rail** (left edge, under the compact minimap: 12 + 132 + 8 px): small icon faces in full 44 pt targets, with no
  panel behind them, so taps between them reach the battlefield. Setting up: the unit picker, the side new units go to
  (a blue or red flag), undo, redo, more. Running: both sides' switches (CP, cooldowns, immortal, a support to call),
  more. "More" is a short list: battle settings, scenarios, duel, A/B, statistics, leave.
- **Picker** (beside the rail, opens from it): a category dropdown (the seven tabs), a search chip that opens the
  name field, a filter chip that opens branch, armour and weapon, then an icon grid (each unit's card icon, its short
  name, its price; an elite's mark; bosses a skull, mini bosses a crown, ships an anchor). Its foot: the formation, how
  many at once, free rotation, and what a tap will place.
- **Card** (right, under pause), only with a selection: icon, name, delete and close; the count, side and heading;
  turn left and right, move, copy; side, elite, immortal as icon toggles; rank, health and ammunition steppers;
  equipment, a tower's rank-7 branch and a boss's starting tier as dropdowns; the boss section folded until opened.
  Running: health, orders as icons (go to, fire at, hold, back to the AI, hold fire, immortal) and the boss tools
  folded under their header.
- **Bar** (bottom, one row of 81 px): Run/Edit (the one main action), pause or resume, one tick, speed as minus, the
  value, plus (x0.25 to x4), the seed chip (tap: its field and why it matters), the clock, reset, the overlays' tray.
  Setting up, only Run, seed, reset and the tray show.
- **Tray** (over the bar): the overlays as small icon chips with short names (range, hits, DPS, ammo, zones; internal:
  hit boxes, routes, stuck, AI buying with its top scores).
- **Sheets** (beside the rail, one at a time): the battle's settings, scenarios, duel, A/B, statistics, both sides.
- Wide screens (panel wider than 1500 px: 20:9 phones, tablets in the menus' scale): a wider picker (580), card (420)
  and sheets (660). The frame keeps to the safe area on its own document (`KitSafeArea.Track`).
- **The battle HUD's Sandbox form** (`HudSpec.Sandbox`): the minimap with zoom, both sides' counts and pause stay; the
  wave and next-wave counts, the commander's switches, select-all, box select and the standing hint are left out.

### Style

The compact HUD's (prompt 11): `--sb-face` 44 px faces on the field panel colour, inside `--fc-touch` targets; chips
at the small type size; dropdowns without their own frame; on-state as the text colour with ink icons. Tokens only
(`Resources/UI/Sandbox.uss`). New line icons in the kit's Lucide style (`Icons.Sandbox.cs`: grid, search, filter,
undo, redo, more, one tick, turn left and right, copy, delete, layers, chart, A/B, free rotation).

### Strings (prompt 21's rules)

New keys in `SandboxText` in both languages with named placeholders: the rail, bar and card words (more, close, both
sides, "New units go to {side}", switch side, category, filters, "Tap the map to place: {unit}", fewer/more, lower/
higher, slower/faster, "×{speed}", "Seed {seed}" / "Mã trận {seed}" by the glossary, starting phase) and the tray's
short names. Every icon's words are its tooltip and screen-reader label.

### For the screenshots and checks

`SandboxController` has a preview constructor (no battlefield drawn), and `SandboxScreen` builds into a host panel;
`UiShots.BuildSandbox` lays a sample scenario out as the runner does (session, battle, the HUD's Sandbox form) in the
states `sandbox-setup`, `-palette`, `-card`, `-sheet`, `-run` (`-mbShotsSet sandbox`). The layer switches moved from
the overlays to the controller, so the tray works without them.

### Tests

- `UiLayoutTests.TheSandboxIsLeanAndPassesEveryCheck` (new): the five screens pass the kit's checks (no cut text, 44 pt
  targets, no text under the secondary size, one main action, nothing off screen or clipped) at the four shapes in
  Vietnamese, in English and Large text at 16:9; at rest the Sandbox covers 5.6 % of a 16:9 screen (4.2-4.6 % on the
  others), with a unit's card 27.3 % (20.5-26.2 %), under the bounds of 12 % and 30 % (prompt 11's compact HUD's).
- `SandboxTests.TheLeanScreenShowsOneLanguageAndOnlyWhatIsInUse` (new): every text and tooltip of the five screens in
  the screen's language (the L10n scan's rule), and only the rail and the bar at rest.
- One run of the three filters (UiLayoutTests, L10nTests and L10nSwitchTests, SandboxTests): 108 of 109. The new
  layout check found icon targets giving way beside long English labels and a squashed foot label in Large text
  (targets and panel rows no longer shrink); the two new checks then passed on a second, targeted run.

### Screenshots (Docs/art/sandbox/before, /after)

`-mbShotsSet sandbox`: the five states in Vietnamese at 16:9, 20:9 (punch-hole) and 4:3, and in English at 16:9. The
emulator was running, and CLAUDE.md's rule (no batch run on the GPU the emulator's OpenGL uses) stands, so the shots
were rendered on Windows' software adapter: `-force-d3d11 -force-device-index 1` picks the Microsoft Basic Render
Driver (DXGI lists the RTX 5070 Ti as 0 and WARP as 1; the log confirms "Renderer: Microsoft Basic Render Driver").
Slower, but it never touches the GPU; worth keeping for UI shots while the emulator runs.

### For the testing phase

Tapping through every control on a phone and a tablet (the drag that turns a unit, the tray and the seed field over
the bar, the picker over the minimap's corner), Large text in play, and the colour-blind side colours.

### Shared edits (merge by hand if they conflict)

`BattleHud` and `HudSpec` (`Sandbox`), `Icons` (the Sandbox set's lookup), `UiShots` (`BuildSandbox`, the sandbox
set), `UiLayoutTests`, `SandboxTests`. New: `Game/Hud/Icons.Sandbox.cs`, `Docs/art/sandbox`.

## 22P. Play-test 7, priority fixes: the AC-130 card, mounts firing together, slower missiles and drones, the siege tank, short self-defence guns, tower weapons (2026-09-30)

The owner's play-test 7 list (`Docs/prompts/requests_vi.md`, "Play-test 7"). Branch `feature/pt7-priority` from
lead/integration 55aa1a6.

### A. The AC-130 as an aircraft card (the owner's top item)

**Why it could not be found.** 21E made the AC-130 a support card (`gunship_strike`), listed with the supports; the
aircraft list (Scout Helicopter ... Heavy Bomber) held no AC-130, and its "Heavy Gunship" is the Mi-24. **Decided:
`sky_gunship` is a vehicle card again**, "AC-130 Gunship" / "Pháo hạm AC-130" (full and short name), in
`MatchSettings.AllVehicles` after the bombers, class Plane (inferred: a fixed-wing aircraft), Air branch (so the
Aircraft filter lists it), 22 CP, premium at 4,500 coins (the old card's and the support's price) in the shop's cards,
unlocked in the test builds. It flies as it did for the item: sent somewhere, it flies there and circles its post;
with an enemy in reach it flies its 22 m anticlockwise pylon turn round it, the 105, 40 and 25 mm all firing out of the
left side at once (B), Griffins from the ramp; it rearms like a bomber. Its card picture is the AC-130's render
(the support's manifest entry, now kind `vehicle`); guide rewritten (the old one said 50-58 m).

**The support card is removed**, not kept: two AC-130 cards (one in the supports) was the confusion. Saves: roster
version 5, `CardMerges.Into["gunship_strike"] = "sky_gunship"` (a bought Gunship support becomes the owned AC-130
card with its rank and blueprints, no refund); `CardMerges.Retired` is empty (a save not yet migrated keeps its old
sky gunship card; saves migrated before kept their refund). A support deck that held it drops it. The one-use
**Gunship item** (`gunship_support`, shop Items tab) stays: it is an item, not a card; its Vietnamese names now read
"Pháo hạm". The AI may field the AC-130 like any card (G's balance pass may want to price it).

**Proof capture:** UiShots `screen-army-deck-ac130-en-full` (debug screen `army-deck-air`: the collection filtered to
the aircraft, the AC-130 bought and first in the deck strip; the screen is in `MenuScreen.ScreenNames`, so
`UiLayoutTests` check it). **Not taken here:** the Android emulator was running, and graphics-mode Unity crashes it
(CLAUDE.md); the lead takes it after the merge (`-executeMethod MachineBrigade.Editor.UiShots.KitScreens -mbShotsSet
menu -mbShotsOnly army-deck-ac130`, into `Docs/art/pt7/`).

### B. Every mount fires on its own timing

The fire rhythm (`CombatSystem.InRhythm`) made a vehicle's mounts take turns: machine guns quiet round every heavy
round and salvo and before a heavy weapon was due, heavy weapons waiting after guns and each other, a main-gun stream
holding every other mount off, secondary magazine guns sharing gaps, bosses firing one mount a step (11B-12D, with
19P's gunship, 20W's SHORAD and tail-chase and 21F's hold exceptions). **All of it is gone**, for every vehicle, tower
and boss: each mount fires as soon as it is loaded, laid and in reach. Kept: a gun's first opening after a random
0.2-1 s (identical vehicles out of step), machine-gun runs of 6-10 rounds and a pause, each round's 10 % jitter, and
**twin barrels** (two mounts of one weapon: the Mi-24's door guns, the steel fortress's MG turrets, the HQ's flak, a
boss's pairs) never open fire in the same instant: the second waits `CombatSystem.TwinOffset` (0.1 s) after the
first, then keeps its own cadence (`WeaponState.FiredAt`, `OpenedAt`). The old bookkeeping (`Vehicle.HeavyRoundAt`,
`GunRoundAt`, `LeadWaitingAt`, `WeaponState.HeldAt` ...) is removed. The AC-130's 25 mm (20V: it never fired) now
streams beside the 105 and 40 mm by the general rule.

**Balance note for G:** multi-mount vehicles gain the fire their guns lost waiting (roughly: coaxial and roof guns
beside a main gun, AA vehicles' SAMs beside their flak, which 12D had compensated with heavier flak rounds; attack
jets' bombs and cannon on one pass; bosses' guns). Not re-measured here (`FireRhythmMeasure` is explicit).

### C. Slower missiles and drones (30 %)

Heavy gunship (Mi-24): `gunship_rockets` 38.4 -> 26.9 m/s (the mega gunship boss fires the same row), `heli_atgm`
16.8 -> 11.8. Attack jet: `s8_pods` 28.8 -> 20.2, `kh29` 13.8 -> 9.7, `r60` 14.4 -> 10.1 (its air-to-air missile
too: the owner named the jet's missiles). Drone mothership: `swarm_drones` 26 -> 18.2. Every flight at full reach
stays under its cooldown (the Kh-29's 4.1 s of 7.9, the drone's 3.3 s of 3.3).

### D. The siege tank

- **The twin 105 mm retracts right into the turret** sieged (3.0 m instead of 0.9: its brakes end flush with the
  turret's face; before, two long barrels still lay over the engine deck), over 2-34 % of the 2.5 s, and runs back out
  when it packs up (the same sequence backwards). `mb_p22_siege.py` `GUN_RETRACT`, `VehicleView.GunRetract`.
- **The roof machine gun** stood on the turret roof right beside the siege cannon's cradle and trunnions: sieged, with
  the cannon laid at 55-72 degrees, it sank into the cradle's side. It now stands at the twin guns' end of the roof,
  opposite the sight (Blender (0.95, 0.95) on the turret; 1.4 m from the trunnion instead of 0.8), clear of both
  guns in both modes, still on its free mount. Model rebuilt (`siege_tank.glb`, same 15,472 triangles); **its card
  picture needs a re-render** (the lead's, with graphics: `CardRenderTests.EveryCardHasAFreshPicture` fails on it
  until then). A close-up of both modes is for the lead's captures too.

### E. Short self-defence machine guns

The owner's "giảm range có thể bắn 30-50 tùy xe": their M2 reaches 30 m, so the cut is read as 30-50 % by vehicle (a
30-50 m cut would leave nothing). New rows inheriting `hmg_roof` / `mg_jeep`: `hmg_selfdef_21` (-30 %: the siege tank,
which also has its 105 mm), `hmg_selfdef_18` (-40 %: SAM launcher, mortar carrier, thermobaric launcher, FPV carrier),
`hmg_selfdef_15` (-50 %: SP artillery and its elite, MLRS, heavy rocket artillery, ballistic launcher, Lancet and
Shahed trucks, elite MLRS and Grad; and the non-combat vehicles whose only weapon is the M2: counter-battery radar,
command vehicle, ammunition carrier, EW jammer, mine layer, smoke carrier, shield carrier, engineer vehicle),
`mg_jeep_selfdef` (13 m, -40 %: the rocket technical). Tanks, IFVs and the bulldozer keep 30 m.

### F. Towers without the extra weapons

21F took the machine guns out of the data of the rocket battery, artillery emplacement, Patriot, SAM post and coastal
turret, but their models still drew them (roof HMGs on `Mount_mg`, coaxial guns): what the owner saw. Now:
- **Data:** the gun turret (and its branches) loses its coaxial gun; the heavy fortress had none; its steel-fortress
  branch keeps its **two MG turrets** (its mechanic), now on slot `gun` so they fire from the two turrets its model
  draws (`Mount_gun`, `Mount_gun.001`; they fired from the base's roof HMG before), and loses its coaxial gun; the MG
  bunker loses its ATGM post (keeps its machine gun; the twin branch inherits); the guard tower loses its grenade
  launcher (keeps its own gun; its branches inherit); the camp bastion loses its coaxial gun. Kept: the AA turret's
  SAM (both of its weapons are its anti-air; its branches already choose one), the HQ's flak and coaxial gun.
- **Models:** `TowerArt` learns, for every model worn only by static non-boss defs (their own and their branch
  letter's), the slots they fire from; `ModelLibrary.StripUnarmed` takes a `Mount_<slot>` (with everything on it)
  and the coaxial parts (`Coax*`, `Muzzle_coax`) off the template when no tower wearing the model fires that slot,
  before the merge: no tower draws a gun it does not have (the heavy fortress's roof HMG and coaxial gun, the gun
  turret's coaxial gun, the missile battery's, rocket turret's and artillery emplacement's roof HMGs, the MG bunker's
  ATGM, the guard tower's grenade launcher). Models shared with a vehicle or a boss are never stripped. Card pictures
  of these towers still show the old guns until re-rendered (the lead's).
- Guides updated in both languages (the gun turret, MG bunker, guard tower, camp bastion).

### G. Tests

New `PlayTest7Tests` (6): the AC-130 card's data, list, class, price, picture, left-side guns and names; **several
mounts fire together** (`SeveralMountsFireTogether`, five cases: the battle tank, the Mi-24, the AC-130, the steel
fortress, the mega gunship boss: at least two mounts fire, two different mounts fire within 0.1 s, twin mounts never
open fire under `TwinOffset` apart); the speeds of C; the machine-gun reaches of E; the towers' mounts and stripped
models of F (the steel fortress's two turrets drawn, the HQ's roof guns kept); the siege tank's 105 mm in and out and
its machine gun clear of the trunnion. Changed: `WeaponTurnTests` (round 6's "no two weapons fire together" removed),
`WeaponRhythmTests.MainGunAndMachineGunFireOnTheirOwnTimings`, `PlayTest5Tests` and `MissileFlightTests` (speeds),
`PlayTest6Tests` (speeds; the towers' second guns), `PlayTest6UiTests` (the support card's two tests removed), `Prompt13MigrationTests`,
`RosterMergeTests` (the AC-130 kept, the support migrated).

Run once (compile, then `PlayTest7Tests`, `CounterTests`, `InActionTests`, `AirRealismTests`, `TowerGearTests`,
`UiLayoutTests`, `L10nTests`, `L10nSwitchTests`, `LocalisationScanTests`, `StringsTests`, `WeaponTurnTests`,
`WeaponRhythmTests`, `PlayTest5Tests` (the siege tank's sim), `PlayTest6Tests`, `PlayTest6UiTests`,
`PlayTest6VisualTests` (the siege tank's model), `MissileFlightTests`, `Prompt13MigrationTests`, `RosterMergeTests`,
`Prompt17ContentTests` (the bunker vehicle's deploy), `CardRenderTests`): 210 of 217; after fixes the three classes
with my failures pass (27/27). **Left failing:** `CardRenderTests.EveryCardHasAFreshPicture` (the siege tank's picture,
above) and `TowerGearTests` x3 (the sabot-round fit on the missile battery and the SAM branch: the same three 21F found
on lead).

### For the testing phase

The AC-130 bought, fielded and sent about; mixed fire from tanks, IFVs, AA vehicles and bosses (and how much harder
they hit, B); the Mi-24's and attack jet's slower missiles against moving targets; the siege tank's sequence at the
default zoom.

### Shared edits (merge by hand if they conflict)

`balance.json` (six weapon speeds, four new MG rows, about 25 vehicle and tower lines, the `gunship_strike` row
removed), `CombatSystem.cs` (`InRhythm` and the turn helpers), `Vehicle.cs`, `WeaponState.cs`, `CardMerges.cs`,
`PlayerProfile.Arsenal.cs` (`RosterVersion` 5), `Progression.cs`, `MatchSettings.cs`, `Strings.cs`, `GuideText.cs`,
`MenuScreen.cs` / `.Shop.cs`, `UI/Cards/manifest.json`, `ModelLibrary.cs`, `TowerArt.cs`, `VehicleView.Deploy.cs`,
`UiShots.cs`, `siege_tank.glb`, `Tools/blender/mb_p22_siege.py`, the tests above.

## 22A. Prompt 22 pass 1: names, structure, story (2026-09-30)

Sections A, B and C of `Docs/prompts/prompt22_vi.txt`, with the owner's note of 30/09 (a chapter runs from 9 to 18
missions by the story's pace). The story is summed up, chapter by chapter and mission by mission, in `Docs/STORY.md`.

### A. Names

- **Every proper name is the spec's, the same in both languages**: the region (Meridian Coast), the faction (Meridian
  Accord, its 7th Mechanized Brigade, "Machine Brigade"), the capital (Veyra), the people and call signs, the maps, the
  chapters and acts. Descriptions, bosses' subtitles, radio and briefings stay translated. A proper name keeps the spelling
  it was given ("Mechanized", "Iron Harbor") while the running English stays British (glossary).
- **Ids stay**: saves, records, text keys and portraits keep `khai`, `hung`, `sen`, `quaden`, `landingbeach`, `capital`...
  The tokens of prompt 21 (`{@lyhan}`...) stay in the texts and read the new names from `NameText.Table`; new texts write
  the names as they are, and `NameText.Kept` lists every new name for the language scans.
- **How**: the map names in `Strings.cs`; a rename pass over every table and the campaign sources (people, places, the
  faction; "Khai" without its marks in the English texts too; "Khai hỏa", open fire, is left alone); the texts that named
  the old story rewritten (the Night of Steel, the "Protectorate", the Northern Army are gone; Kade is Colonel Marcus Kade;
  Bà Già, the captured Behemoth, is Matilda). Kasimir Wolff is Raven on every side: prompt 20's exception for "Quạ Đen" on
  our radio is gone.
- **Prompt 21's hand work kept**: prompt 21 localised in `CampaignText.cs`, by hand, words that prompt 20's sources mark
  fresh; a rebuild would have put the sources' words back (it did, once: "rocket" for "rốc-két"). `act5.py` now clears
  prompt 20's fresh marks, so only what prompt 22 writes (story.py, act5.py-act8.py) is fresh; `CampaignText.cs` was
  rebuilt from the committed one. `radio.betrayal` stays in `Strings.cs` only (prompt 21 moved it).

### B. Structure

- **Final counts** (main / side): chapter 1 9/1, 2 11/2, 3 12/2, interlude I 4/0; 4 16/2, 5 13/2, 6 16/2, interlude II
  4/0; 7 18/1, 8 12/2, 9 14/2, interlude III 4/0; 10 14/2, 11 11/1, 12 10/0: 168 main missions (156 in the chapters, 12
  in the interludes) and 19 side missions, 187 in all (was 121 and 24). The spec's counts, but chapter 1 raised from 8 to
  9 (the owner's floor); its ninth is the fishing village (c1m03 retold), so the chapter kept all its missions but one.
- **Interludes are chapters 13-15** (`interlude` 1-3 in campaign.json), played after chapters 3, 6 and 9: no mission id of
  the twelve moves, and `Campaign.Chapters` is the order of play. An interlude carries the act before it (its `act`), so the
  act switches of prompt 20 C take it along with no new code. `Campaign.LastChapter` stays the last of the twelve switched
  on (the Full Boss Hunt, the Sandbox and the Operations tiers follow it); `FinalChapter` is the last in order (an act's
  interlude ends a release: its "To be continued" comes after it). On the screens: "Interlude II" / "Chương xen kẽ II",
  its missions "II-3", the lock line names the chapter before ("Opens once Interlude I is finished").
- **New missions** are copies of missions already written on the same battlefield, or of one whose goal names only the
  map's points (capture, hold, survive, recon, outpost, a flying boss) on another, with the set-up changed (prompt 4):
  44 new, four moved. Ids go on from a chapter's last one (c4m12...), interludes i1m01-i3m04; `act8.ORDER` sets the order
  of play. The build checks the pairwise rule as before and adds: no two in a row alike, the counts, one operation per
  chapter and last, the operation fights the chapter's main boss, a set piece besides it (`setPiece`), no card in an
  interlude, every mission on a P22-content map or boss says so (`awaits`).
- **The last mission is the operation with the main boss**: c2m10 (the refinery raid) and c4m10 (the port) are staged set
  pieces now (still offered again in Operations as notable battles); chapter 2 ends on a new operation at Red Rock (c2m11,
  the Behemoth, Thorne's army beside us); c4m11 (Leviathan, prompt 16's epilogue) is chapter 4's operation (the lighthouse,
  a choice of the old coastal batteries or air cover, the fishing village, Leviathan); c7m10 ends on a new Nemesis
  intercept, and Nemesis's old mission (c7m05) brings Juggernaut back on the city's freight line. Inferno breaks off at
  half health in c2m05 and burns with the refinery in c2m10.
- **Moves** (campaign version 4, `migration22`): c1m07 to c6m11 (Harvest Guard, now Varga's counterstrike in Greenvale;
  the old campaign's m22 goes with it), c1s2 to c6m12, c7s2 and c11s2 to main missions c7m11 and c11m11. c12s1 and c12s2
  are gone (chapter 12 has no side mission; their stars go with them) and the legendary tower piece moved to c11s1. A
  version 2 save takes both steps. A player who had finished a chapter finds its new missions open and the campaign goes
  on from the first of them; a chapter whose operation is new (chapter 2) is done once that is won.
- **Where a boss had to fight**: Kessler's last stand is his Scylla (C.4), a ship, so c12m02 moved from the launch site to
  Beacon Bay, north of Helion; chapter 12's minis are Behemoth Mk.II, Scylla and Locust (Tempest stays in chapter 4).
  Gungnir, a gun on rails, stays on the Rust Yard's rails, called the Skygate Array's railhead. Fenrir's chase moved to the
  Whiteout Pass blizzard (reversed), and chapter 6's Behemoth Mk.II to fog so the two differ. The two Locusts of interlude
  II come one per battlefield (a mission fights one boss). Chapter 7's reappearances: Inferno in the Old Quarter (c7m13),
  Juggernaut in Metro City (c7m05).
- **Pay**: the tune is bound by blueprints (the coins of stars and crates are enough), so the coin scale stays at its
  floor, the old campaign's pay; the blueprint scale falls from 1.00 to 0.75 for 187 missions. The deck's rank is 7.14 as
  act IV begins and 8.00 at the end; acts I-II alone pay ×1.86, acts I-III ×1.00 (rank 7.14; a release never pays less).

### C. Story

- **The flash-forward** is a story card before chapter 1's card, shown once (mark 99 in the cards seen); a save that has
  seen chapter 1 skips it. **The ending** is the epilogue card (`campaign.epilogue`); the hooks for later content are in
  `Docs/STORY.md` (ships still in orbit, Kessler's river flotillas, a Hegemon general a season, Thorne's fate).
- **Beats** (C.4) are in their missions, in both languages; `Prompt22StoryTests.TheStoryBeatsAreInTheirMissions` checks a
  line of each chapter's key beat. Aurel speaks on the radio first in chapter 11: his earlier lines went to others (c7m01,
  c7m09, c10m05); a briefing's quote card still shows the general's taunt, which is not the radio. Raven first appears with
  the Harpy by radio (the Harpy stays Orlov's gunship and Orlov's deck); Hawk wins the duel (Morrigan breaks off at half)
  and shoots Raven down over Skyhold (c10m10). Thorne's last line is the spec's, "Đừng để tôi đã đúng." ("Don't let me
  have been right.").
- **Voices**: radio lines of 100 characters at most in both languages (a test; three old lines were shortened), each
  character in his or her own register (Varga speaks to the player as "ông", an equal; Orlov and Kessler keep "ngươi").
  A mission's radio line no mission plays any more is dropped from `CampaignText.cs` by the build.
- **The eight officers who join** (the commanders of prompt 22 F) speak from the chapter that brings them in, so each has a
  flat vector portrait in `portraits.py`'s style (placeholders like the others); Nadia's insignia is a captain's now.

### Waiting on the other agents (check after both merges)

- **Maps** `foundry` (interlude I, i1m01-i1m04) and `veyra_old_quarter` (c7m12-c7m15): assumed in the standard frame
  (camps in the corners, points west / town / east), weather lists assumed (`campaign_kit.WEATHER`); until the maps come,
  their missions read "Battlefield in the next update" and do not hold the campaign back.
- **Bosses** `behemoth_mk0` (i1m03, fought as the Behemoth at 0.9) and `morrigan` (i3m02, c10m12, as Spectre at 0.5 and
  0.6). Their names and files are in `CampaignText.cs` (story.py's boss files): if P22-content writes them too, keep one.
- **Mara's Behemoth** in c12m10 (`awaits: ally:mara_behemoth`; Mara's line for it already plays). **Pass 3**: c10m12 has
  `commander: dieuhau` and awaits `mode:air_duel` (aircraft only).
- **Pass 2 hooks**: `storyChoice` on c4m14 (`c4.pursuit`), c8m09 (`c8.miners`) and c11m09 (`c11.radar`), where D.5's
  choices come; `comic.<n>` on every chapter and interlude (D.8).

### Tests

- `Prompt22StoryTests` (new): no old proper name in any table in either language, the ids and new names as expected;
  the counts of every chapter and interlude, the operation last with the chapter's main boss; no two missions in a row
  alike; an interlude with the act before it for acts I, I-II, I-III and all four (and its labels); a save of the twelve
  chapters of ten moved on once; the story's beats; radio lines of 100 characters at most.
- Updated for prompt 22: `Prompt20CampaignTests` (no "Quạ Đen" exception, interludes in the act switches),
  `Prompt20HuntTests` (story order and act switches with interludes, 21 mini bosses, part E's two skipped until their
  defs exist), `CampaignTests.TwelveChaptersOfNineToEighteenMissionsAndThreeInterludes`.
- Runs: the new tests with the Prompt20Campaign, CampaignStart and L10n filters (and UiLanguage): 46 of 47
  (a duplicate `radio.betrayal`, fixed), then 50 of 50 with RadioDirector added; CampaignTests' data and shape tests with Prompt20Hunt's: 16 of 16.
  The 5-seed campaign runs wait for the testing phase.


## 22E. Prompt 22 E: new maps and bosses (2026-09-30)

Section E of `Docs/prompts/prompt22_vi.txt`, the new content only, on feature/p22-content from lead/integration 55aa1a6.
The campaign's structure and placement, the renames and the story are P22-story's; the Commander system is
P22-commanders'. Nothing of theirs is touched: no mission of campaign.json names the new content yet.

### E.1-2 Two battlefields

- **Ids** `foundry` and `veyra_old_quarter` (the brief's). The underscores are safe: the tools split versions with
  `rpartition('_')` and the game strips the known suffixes; the one place that cut at the first `_` (the hunt's
  checkpoint, `BossRushMode.HuntRestOver`) now strips `_conquest/_sandbox/_siege/_long` instead.
- **Names through NameText.** `name.foundry` ("Foundry") and `name.veyra_old_quarter` ("Veyra Old Quarter"), the same in
  both languages; `map.<id>` reads `{@<id>}`, so a later rename is one entry. The map words (`map.*`, `.sub`,
  `guide.map.*`) sit at the end of `BossText` with the bosses' (as prompt 20's hunt words did), so the story pass's
  renames of `Strings`/`GuideText` and these additions never touch the same lines.
- **Foundry** (theme urban): Hegemon's old tank works. A grid of 10 m factory lanes (8.6 m of floor between the
  buildings, four nav cells) cuts the ground into solid blocks of factories, warehouses, sheds, container stacks, tanks
  and silos (`city_block`, one mass per block): every way across is a narrow passage. "Indoor" is drawn as walled halls
  on open floors (the camera sees no roofs): the casting hall at the centre (the town point) walled round and opened
  only where the four lanes run in, furnaces and ladles on the floor between the lanes; the press shop (west point)
  and its image the rolling mill (east point) are walled yards with one 16 m doorway a side, off-centre so the
  gantry crane and presses stand clear of them. The outer lanes stop short of the camps' yards (the HQ stands behind
  the rally, where they crossed).
- **Veyra Old Quarter** (theme urban): the capital's old town. Six 10 m streets each way, jogging 3 m every 36 m (the
  old plots they bend round), townhouses, stone houses (offices), shops, cottages and sheds; the cathedral square at
  the centre (the church on its north side, the old town hall facing it), the market square (west) and the clock
  square (east), four small piazzas, lamps and stalls, the old wall's broken pieces on the edge. Nothing solid stands
  in a street (only parked cars, which do not block).
- **Siege versions.** Both dense maps build their Siege version with `siege=True` (`build_maps.SIEGE_OWN`, as Lighthouse
  Bay): the blocks of the fortress's ground (beyond the first lanes in the north-east) stay open and only their images
  are built, and the Foundry leaves out the casting hall's walls. Unblock-yourself choice: with the blocks built the
  fortress could not reach its gates or place its relays (the first build said so); the fortress builds its own walls.
- **Versions and checks.** Conquest, Survival and Siege from `build_maps.py` (`MAPS_P22`, `WAR_P22`, `DENSIFY_P22`, two
  `boundary.SHAPES`), the long battlefield from `longmap.py`, the menu pictures from `map_thumbs.py`, both in
  `MatchSettings.AllMaps` (skirmish, Survival, the Base screen, the weekly draw and the Boss Hunt, which fights on the
  chosen battlefield). Camps 2/3/6 large/medium/small towers and 3 utilities a side, labelled by `SlotPlaces` as every
  square map; outposts 2/1/2 on the Foundry (the casting hall's floor has room for one) and 2/2/2 on the Old Quarter;
  the long bases 28 hardpoints each. `check_access`: 6/6 files pass (_conquest, _siege, _long of both). The Battlefields
  tab of the dossier (19N) lists them from `AllMaps` with their guide.
- Every other map's files are unchanged.

### E.3 Behemoth Mk.0 · Behemoth nguyên mẫu (Varga)

Data only, by the variant rules of 19E: `variantOf: behemoth`, size 0.7, keeps the main gun, the two 120 mm flank guns
and the rocket pod (4 parts, 50 % of the body), `aps: null` (with its part gone the protection system would otherwise
run for ever), front armour 3, speed 2.2, a primer tint, mark and name `mk0` (the prototype met before the Behemoth).
No flak and no missiles: aircraft and missiles are the answer to it. Big attack `behemoth_mk0_barrage` from the
Behemoth's barrage with four rounds (two pairs); the mini rank scales it. It comes after Mk.II in balance.json, so the
Behemoth's mini version (the Sandbox's switch, `MiniVariant`) stays Mk.II.

### E.3 Morrigan · Tiêm kích của Raven (Wolff)

- **Model** `morrigan` (`Tools/blender/mb_p22_content.py`, 20.6 x 13.4 m, scale 0.62 in game, 1 312 triangles), from
  real stealth fighters: the Northrop YF-23 Black Widow II (the diamond wing, the two tails canted out 50 degrees, the
  exhaust troughs over the rear deck, the long flat-sided nose), the Su-57's tandem main bays between the intakes, and
  a raven's look (a blade nose, a dark body with the army's colour on wings and tails, a feathered trailing edge). Boss
  parts `Part_bay_l/r` (a missile each, `Muzzle_missile`, `Muzzle_missile.001`), `Part_bomb_bay` (`Muzzle_bomb`),
  `Part_engines`; the cannon's `Muzzle_gun` on the left shoulder.
- **Data**: a mini boss on the aircraft frame, fixed-wing, `stealth` (the aircraft rule: seen at 0.4 of a spotter's
  sight unless it fired in the last 2.5 s), speed 44 (the fighters 40), air-to-air missiles in both bays, the guided
  bomb, the cannon; `interceptor` and `sead` as the stealth fighter, so it hunts aircraft and then air defences.
  7 400 hp before the mini share, armour 1.
- **Its big attack** `morrigan_salvo` (prompt 18's rules: 3.5 s warning, 50 s cooldown, x1.3 as a mini; stopped by
  breaking the carrying parts during the warning, cut by `abortDamage` 0.1, delayed 2 s by an EMP): six homing
  air-to-air missiles from the two bays at up to six of the player's aircraft and two guided bombs from the centre bay
  on the strongest anti-air. New in the library (`BigAttackDefs`): a swarm strike's `prey` (`air`: the other side's
  aircraft, the dearest first; `antiAir`: its vehicles and towers whose main weapon hits aircraft) picked within the
  attack's reach and only if seen (`BossSystem.Prey`), and the aim `prey` (the first prey, else the biggest group).
  With no prey a strike falls on the ground group round its aim as before. Homing rounds leave no ring to step out of:
  the answer is the interrupt, anti-air and point defence shooting them down (`Intercepted`), and spreading out.
- **Duel mode** (`duel` in its data, `BossSystem.Duel`): a mission with `"duel": true` puts its boss into it on spawn:
  its escorts go home, its big attack becomes `morrigan_duel_salvo` (the missiles only, 42 s), and it goes dark at 70 %
  and 40 % of its health and every 45 s: 6 s of held fire and flares, so its stealth hides it again beyond close range
  (radio `radio.quaden.morrigan.duel` / `.dark`). The same flag cuts the player's deck (`MissionDef.PlayerDeck` "air",
  `Game/Match/MissionDecks`): its aircraft only, topped up to three from the unlocked fighters (the fighter jet always),
  and no support cards (aircraft against aircraft). Chapter 10's duel mission is the story pass's to write; its
  required commander (Hawk) is the Commander agent's.

### E.4 Mara's Behemoth

`mara_behemoth`: the Behemoth's model in the player's colours with a cold tint and `mark: accord`, the Behemoth's
weapons (main gun, 120 mm, two flak, two missile racks, the protection system), 6 000 hp, not a boss (no bar, no
parts). New flag `storyOnly`: never a card (`card` false), never bought or picked by an AI, `PlayerProfile.Unlock`
refuses it, the Sandbox's palette never offers it, and it is in no card list. A mission places it with the existing
`ally` block (`{"x", "z", "units": [{"def": "mara_behemoth", ...}]}`), whose allied AI drives it; the test fails if
any mission outside chapter 12 names it. Placing it in chapter 12's final battle is the story pass's.

### E.5 The Boss Hunts

The hunts take every chapter slot of the chapters switched on (19N). Until the story pass lists the new minis in a
chapter, `BossHunts.Unslotted` brings them in story order: Behemoth Mk.0 after chapter 3 (interlude I), Morrigan after
chapter 9 (interlude III), each only while that chapter is on; once a chapter lists one, its slot wins. So the full
hunt grows by two and the week's draw can pick them (both came up within the year's weeks tested). The old Boss Rush
kinds gain the pair.

### Strings (prompt 21's rules)

Both languages, named placeholders, proper names through NameText (`{@foundry}`, `{@veyra_old_quarter}`, `{@mai}` for
Mara); "Morrigan" joins `NameText.Kept` with the other bosses' code names. Keys: `unit/boss/short/note/bossfile/guide/
guide.parts.tip` for both bosses, `unit/short/note.mara_behemoth`, the radio lines, both salvos' and the barrage's
words, `guide.bigattack.target.air/.aironly`.

### Tests

One run of the targeted filter after a clean compile (94 tests): `Prompt22ContentTests` (8: the maps' versions, labels,
names, guide and picture; Behemoth Mk.0 by data alone; Morrigan's data and stealth; its salvo's prey, warning,
rounds, cooldown and interrupts; the duel mode; the duel's aircraft deck and the mission flag; Mara's Behemoth never a
card and only in chapter 12; both minis in the hunts), `MapConnectivityTests` and `StuckTests` (the six-minute AI
battle, the short stuck probe) on both maps, `VehicleLodTests` (6), `ModelTests`, `BossPartsTests`, `Prompt20HuntTests`
(9), and the two boss-list tests. 86 passed. Mine failed once: the salvo test read the prey before the world had
stepped (a unit is seen once the sight is worked out); fixed, and `Prompt22ContentTests` rerun: 8/8. The other seven
failures touch nothing of this work (not rerun on the base branch): `ModelTests` muzzle counts of mobile_fortress, heavy_aa,
gunship_heli and fighter_jet, `GearModelTests.AnOldSaveMigratesWithNothingLost` (caught by the filter's "ModelTests"),
and `BossPartsTests`' Behemoth share and shooter tests (the Behemoth's own parts). `check_access` on both maps' six files: 6/6.

### For the testing phase

- 5 seeds of Behemoth Mk.0 and Morrigan kill times on Normal (mini 1.5-3 min), Morrigan against an air-heavy and a
  ground-only deck (its fallback aim), and the duel against three fighters with Hawk.
- `StuckBatch` on both maps, every version (conquest, sandbox, siege, long), both sides, 5 seeds; `BaseSiteTests`,
  `TrafficTests`, `MapRouteTests` with the two maps added to their lists; `ConquestBattleTests` on them.
- With graphics: card renders and in-action clips of the two bosses, `BaseMapShots`, a look at both maps' density.

### Shared edits (merge by hand if they conflict)

`balance.json` (three vehicles after argus, three big attacks after argus_fire_call), `BigAttackDefs`,
`BossSystem.BigAttacks` (JoinBig's override, the prey aim and targets), `BossSystem.cs` (one line), `Vehicle` (duel
fields), `MissionDef` (`duel`, `playerDeck`), `MissionMode` (one line), `Catalog.Extra` (two calls), `BossHunt.cs`,
`SiegeModes` (Kinds), `SandboxAccess`, `MatchRunner` (the deck line), `MatchSettings` (two maps), `PlayerProfile`
(Unlock), `BossHunts`, `BossText`, `NameText`, `build_maps.py`, `boundary.py`, `build_assets.py`, `models.json`, the
test lists (`BossPartsTests`, `Prompt20BossTests`, `Prompt20HuntTests`, `ModelTests`). New: `Catalog.P22.cs`,
`BossSystem.P22.cs`, `MissionDecks.cs`, `mb_p22_content.py`, `Prompt22ContentTests.cs`, the maps' files and pictures,
`morrigan.glb`.
