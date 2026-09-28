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
- **Proper names kept in Vietnamese** (checked by `UiLanguageTests`, every other unmarked Latin word in a Vietnamese text counts as English): `CP`, `HQ`, `UAV`, `FPV`, `SAM`, `EMP`, `SEAD`, `MOAB`, `APS`, `ATGM`, `IFV`, `MLRS`, `AC-130`, `Ka-52`, `Grad`, `Griffin`, `Behemoth`, `Inferno`, `Tempest`, `Hive`, `Bastion`, `Spectre`, `Titan`, `Napalm`, `radar`, `drone`, `boss`, `Machine Brigade`, and the unit `mm` and the Vietnamese abbreviations `PK` (phòng không) and `TT` (trực thăng).
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
- **Left for the screen rebuild:** sections D (navigation), E (each screen on the kit), G (the
  battle HUD on the kit and the field panel), H (names: map names, "coin", "Skin"), the text-size
  switch on the settings page, map preview pictures for the map dropdown (the kit shows card
  renders as stand-ins), `GearArt` frames in the rarity tokens, and adding each rebuilt screen to
  `UiShots.Screens` and to the strict checks (then removing its old-screen report).
