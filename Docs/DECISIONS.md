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
