# Progress

Short record of what each milestone delivered and what is still missing. Newest first.

## 2026-09-28: Round 5 (playtest list): real armament, new vehicles, campaign depth, Defend as a base

The user's fifth list: bugs, one currency, real weapons for every vehicle, new vehicles (car
bombs, suicide drones and more), a repair vehicle, notes for every vehicle, an In action tab,
weather that eases in, fall damage, bigger bosses and a flying-saucer boss, campaign enemies that
scale with the player's arsenal and get reinforcements, more mission types, Defend with a real
base, an Endless mode, and a separate Survival.

### Done

**Fixes and quick changes**
- Deck slots keep their places (removing one card no longer removes another); gems are gone (coins only, old gems converted at 15 coins each); smaller rifle tracers; summoned aircraft fly in from behind and above instead of rising from the ground; the AI never drops strikes on its own troops; smoke and fire thin out along the line of sight to a boss; weather changes over eight seconds; crashing aircraft do fall damage; wings no longer vanish when the camera turns (shadow caster ceiling and camera distance); upgrade badges sit in place; economy faster (income 0.85, supply 0.9), boss rush easier; auto-buy counters the enemy's mix (air with anti-air and the other way round).

**Vehicles**
- Every vehicle's weapons checked against the real thing: the AC-130 fires its guns from the left side while orbiting, the B-2 carries JASSMs and hides (stealth), fighters carry air-to-air missiles and a gun, throttle back and hover to fight, and hunt aircraft; helicopters and jets have flares.
- Ten new vehicles with their own models and icons: armoured car bomb, ZU-23 technical, smoke carrier, Lancet truck, Shahed launcher, Iron Beam laser, railgun truck, turtle tank, BMPT and sapper (repairs towers slowly, with a wrench over what it mends).
- Notes for every vehicle on its detail page; the In action tab shows it firing on a little range of its own.
- Bosses bigger and better armed; a new boss, the Silver Bug flying saucer (laser, coilguns, shield, EMP, drones).
- Engine effects by kind (afterburners, turbofan trails, smoky old jets, props, rotor downwash), contrails high up, wingtip vortices, navigation lights.
- The grenade launchers are gone from the jeep and support vehicles, in the data and now in the models.

**Campaign**
- The enemy keeps pace with the arsenal: it gets 80 % of the average edge the player's card ranks and equipment give the deck (health from toughness, damage from firepower), boss and towers included.
- Enemy reinforcements: when the enemy army falls below 60 % of its peak, or the player's goal passes a milestone, a group is flown in by parachute (75 s apart, bigger each time, anti-air first against air), with a warning.
- Four new goals: Hunt (marked vehicles on patrol, hardened), Recon (bring a vehicle onto each objective for 3 s), Protect (keep the player's buildings standing until the clock runs out), Shoot down (a number of aircraft). Markers over the targets: red to destroy, blue to keep, amber to scout.
- Six new missions (m17 to m22) on Red Rock, Whiteout, Rust Yard, Skyhold, Dune Break and Greenvale, unlocking the ten new vehicles. Five-seed balance: m17 5/5, m18 5/5, m19 5/5, m20 5/5, m21 2/5 (the saucer), m22 3/5; the first sixteen 80/85.

**Modes**
- Defend is now the player's own base: the siege map's fortress (walls, gates, towers, relays, shield generators, HQ) and its garrison are the player's, and the enemy lays siege to it in the same three stages, with waves flown in on top of what it buys. Hold until its clock runs out.
- Endless: the same fortress, no clock, waves every 55 s that grow and turn elite; the best wave is kept.
- Survival stays the army-only mode (no base, no towers).

**Menus restyled: "Field Command"** (the user found the glossy Clash-style menu dated)
- Researched War Thunder Mobile's 2025 redesign, WoT Blitz Reforged, Delta Force, Arena Breakout and others (reference images and a spec in the session notes); chose a flat, tactical look.
- Graphite translucent surfaces over the battle, 1 px hairlines, 2 px corners; no bevel lips, gloss or drop shadows. Amber only for the one main action on a screen (a flat face with two corners cut) and for what is selected (a 3 px line); bone for confirming; Barlow Condensed uppercase labels with tracking (`UiKit.Uppercase`: USS has no text-transform).
- Navigation is a rail on the left; the home column is on the right over a soft scrim, Deploy bottom-right with a light sweep now and then, the deck at a glance bottom-left.
- Pause and result screens, equipment frames (square, graphite tinted by rarity with a glow and a bottom bar of the colour) and the battle HUD's buttons follow the same shapes; the battle HUD keeps its colours.
- Endless is on the Events tab with the record wave.

**Equipment rework** (merged from `feature/gear`, 093c1a7)
- Every piece has a base type (34, each with its own picture) with an implicit line, the main stat by level, 0/1/2/2/2 sub-stats by rarity (with a roll-quality bar), a trait on Epic and Legendary (42 traits: extra rounds, faster reload, ricochet, executioner, incendiary, shred, reactive blocks and more), and one of 10 brands (2-piece and 4-piece set bonuses). 14 special modules. Armour and plating merged; a new Optics slot. Old saves migrate (nothing is lost).
- In battle, traits show a short word over the vehicle when they fire (at most every 2 s).
- The loot boxes stay as they are (coins buy crates): the user's decision after the legal-risk note.

**Traffic** (merged from `feature/pathing`)
- A lane map (roads, main routes, narrow passes, doorways), no stopping in doorways, parked units making way by priority (a group bound for one place never asks its own members, and a unit holding its ground in the open is driven round), one direction at a time through a gate, costed repaths round parked hulls; siege gates 10 m wide on three walkable cells and an open keep yard.

**Battlefields** (Phase 4)
- Every map half as big again: 300 x 300 m. Woods, rocks, hamlets, wrecks, craters and poles grow with the area and a quarter more; the start units move out with their camps; the fortress keeps its plan in the enemy's corner.
- What lies outside the outline stays as decor (drawn, never simulated) so the country goes on past the edge, and a dashed line marks the boundary; the countryside reaches 130 m further.
- Houses, barns, garages and shops 1.3 times bigger (they were smaller than the tanks); campaign positions scaled with the maps.
- High graphics: a 4096 shadow map, soft shadows on phones too, 4x MSAA, and high-detail models (`<id>_hd`, same pivots) for the twelve most-seen vehicles when shadows are High and scenery is rich.
- Five-seed campaign balance on the new maps: 107/115 before retuning m13 (now 3/5, siege buying mix for a demolition inside a fortress).

**Design-review document**
- `ExportGameDoc` (MB_EXPORT) writes the game's numbers to JSON; `Tools/docs/build_doc.py` builds an illustrated PDF (modes, campaign, every vehicle with weapons and DPS, weapons and the damage table, towers, elites, bosses, fire support, equipment, economy, maps, AI, interface).
- The current edition, in Vietnamese: `Docs/Machine_Brigade_Design_Review.pdf` (62 pages, 76 vehicle renders, 13 map plans, 18 screenshots). Rebuild: run the Export test with `MB_EXPORT=<dir>/game.json`, then `python Tools/docs/build_doc.py <dir>/game.json <dir> <out.pdf>` (vehicle renders from `Tools/blender/preview_assets.py`, shots from the emulator).
- Test suite at the end of the round: 375 tests, 350 pass, 25 skipped (balance and export runs), none failing.

### Known limitations
- m21 (the saucer) is hard for the scripted test deck (2/5).
- The new modes, markers, menus and the map edge were checked on the emulator; frame rate on a real phone is still to be measured (the 300 m maps, the 4096 shadow map and the high-detail models all cost more there).
- Ads are still placeholders.

## 2026-09-27 (late): Mobile menu layout, vehicle detail page, equipment pictures

The user asked for a detail screen for each vehicle (health, damage, equipment), a menu split
the way mobile games split theirs (researched outside, then reworked), pictures for every piece
of equipment that show its rarity, and left the equipment numbers to us.

### Done

**Menu layout** (after Clash Royale, Brawl Stars and War Robots)
- Top bar: rank on the left (Back on a full page), the page title, coins and gems with a + that opens the matching shop section, settings.
- Five tabs along the bottom, 96 px tall: Shop, Army, BATTLE (raised, in the middle), Campaign, Events. Red dots only when there is something to do: an affordable rank-up (Army), a reward to claim (Events), a free or owned crate (Shop).
- Battle tab: the lobby battle behind; the next campaign mission and today's challenges on the left; the chosen battle and a 104 px DEPLOY in the bottom-right corner. Tapping the battle card opens Battle Setup as a full page (modes, maps, difficulty, weather, its own Deploy).
- Army tab: the deck strip (eight vehicles, two supports, average cost, what the deck lacks, the doctrine), filters and a sort by rank, then the collection as big cards (cost, rank, blueprint bar, in-deck tick, upgrade arrow, lock). A tap offers Details or Use/Remove. The Equipment view has branches, the seven-slot loadout with the whole set's total, the chosen piece's panel, and the inventory.
- Shop tab: a rail of Deals (a free crate every day, the ad crates, a gold crate at 30 % off once a day), Crates (odds one tap away), Gems, Skins, Units, Items.
- Events tab: today's challenges with progress bars and claim buttons; the weekly fortress, the boss rush and survival, one tap to play.
- Covered pages rest the lobby: its simulation pauses and its camera draws only a plain clear, with no scene and no post-processing.
- Every tappable part is at least 52 px tall, main actions 84 to 104 px. The layout is written as USS in `Hud.uss` ("menu v3").

**Vehicle detail page** (`MenuScreen.Detail.cs`)
- The vehicle's own model turns on a turntable (`UnitPreview`: its own camera on layer 31 into a render texture), with arrows to step through the collection.
- Role, class, branch and rank; what it is strong and weak against.
- Stats tab: health, damage per shot, damage per second, range, speed and sight as bars against the roster's best (`UnitStats`). The base is white, equipment and rank blue, the next rank's gain a green ghost. Then armour, cost, magazine and reload, minimum range, special module.
- Weapons tab: every mount, with damage, rate, range, targets and ammunition. Equipment tab: the branch's seven slots; a tap opens the Equipment view on that slot.
- Bottom bar: add to or remove from the deck, the blueprint bar, and the rank-up. It says what is missing, and sends the player to crates or to the shop when that is the way forward.

**Equipment pictures** (`Tools/blender/mb_gear_icons.py`, `GearArt`)
- Ten Blender-rendered pictures, one for each of the six slots and each of the four special modules: gun barrel, autoloader, armour plate, spaced plating, engine, repair kit, reactive bricks, repair arm, crew helmet, smoke launchers.
- Rarity frames drawn at run time: grey, green, blue, purple or gold with a glow at the heart, a bright border, a diagonal shine on legendary pieces, one to five pips and the level. They are used in the loadout, the inventory, the detail page and the crate results; the pieces are shown on top of the crate results.

**Equipment numbers** (unchanged from the arsenal round, now shown)
- The main stat at the top level runs from common to legendary: damage, fire rate and health 3/5/8/11/14 %; damage taken 2/3.5/5.5/7.5/9.5 %; speed 2/3.5/5/6.5/8 %; repair 0.2 to 1 % a second.
- A piece starts at 40 % of that number at level 1. Level caps are 5/10/15/20/25, at 30 coins a level.
- Each stat has a cap for the whole loadout.

**Fixes**
- The text table had `shop.owned` twice. An indexer initialiser keeps the last one silently, so the Owned label read "Owned: {0}". `StringsTests` now fails on a repeated key and on any literal key the code uses that the table lacks.

### Open
- Needs a look on a real phone: the render-texture turntable's cost, and touch comfort with thumbs.

## 2026-09-27: Siege playtest fixes, AI in waves, air drops, arsenal (ranks, equipment, crates)

The user played the siege and asked for:
- smaller aircraft (the attack helicopter was huge) that do not melt the moment they come near, or anti-air that is less deadly and shorter-ranged;
- siege tanks that fire at targets in range, reload visibly (an icon when empty) and shell from outside the enemy turrets' reach;
- better auto-buying and attacks in waves;
- enemy vehicles that no longer stand stuck in one place;
- a bigger purse for the siege attacker;
- reinforcements that drive in or parachute down instead of popping up;
- barrage and smoke rounds seen falling from the sky;
- flight effects for jets;
- an AI worth the name (research outside, copy code if needed), and the same fixes checked everywhere;
- more buildings in the fortress, paying a bounty when destroyed, which the AI shoots after the military targets;
- a menu that registers every tap, scrolls, and lets deck cards be removed;
- a smooth start to a battle (a loading screen or a fade);
- an audio review: the "enemy barrage coming" alert sounded wrong amid the explosions;
- bigger impacts from the turrets' guns;
- launchers that stand and reload when empty, with an icon over them;
- card ranks bought with coins, equipment in rarities white to gold, and crates (after battles, for coins or real money, a few a day for ads), with six equipment slots plus a special one.

Research was done by two agents: RTS AI (0 A.D., OpenRA, StarCraft bots, PurpleWave, Supreme Commander) and meta-progression (Clash Royale, Brawl Stars, Archero, Survivor.io, War Robots, loot-box law). Only permissively licensed code may be copied; nothing was copied this round, the designs were implemented from the descriptions.

### Done

**Menu and loading**
- Taps land: `Tap` fires on release within 18 px of the press, whoever holds the pointer. UI Toolkit's `Clickable` lost every tap a scroll view took over.
- Deck: the card detail is a fixed pane above the grid. It used to appear inside the scroll and push the cards down, so the next tap hit another card.
- `Curtain`: the screen and sound fade to black, a loading screen names the mode and map, the scene builds behind it and fades in after three frames. Every scene change goes through it; a second tap while it runs is ignored.
- In the editor, clicks count even when the Game view does not have focus.
- `Machine Brigade > Debug Flags` window: the development switches in Play mode (start a mode, map or weather, test views, switch-offs).

**Artillery and the siege**
- Fixed defences, once seen, stay known (buildings under the fog); the siege attacker starts with the fortress plans.
- Artillery and siege tanks shell the known defences first, then the mission's structure, from a firing spot inside their range and outside every known gun's reach (24 bearings on 3 rings). They never attack-move into the guns.
- Empty magazines reload in place, standing still: 10 to 28 s, three times as fast at home or beside a supply vehicle. An overhead gauge shows three shells, a reload bar, and blinks red while the vehicle is moving and the reload waits. The AI stops empty launchers to reload (moving out of reach first if threatened).
- The fortress has 14 more buildings (barracks, stores, offices, workshops), placed clear of the attack lanes. Each pays the attacker 2 to 6 CP when it falls, and 12 coins at the end. The attacking AI shoots them only with nothing military in reach.
- Siege attacker: 34 CP to start, 1.8 income, supply 40, 20 CP a stage. Defender income 0.85 (1.05 on Hard).
- Turret guns: a 120 mm of their own (Large, 1.35x), bastion shells 1.5x, twin 155 mm 1.3x, turret rockets 1.3x. Gun shells never flash the screen.

**Aircraft**
- Drawn about 0.55 of real size so a helicopter is about 1.5 tank lengths (the attack helicopter was 14.3 m against a 6.3 m tank).
- Helicopters are tougher (attack 500, scout 300, gunship 900, Hind 1250 base health).
- Fortress anti-air is toned down: quad flak 46 m and 34 damage, missile battery 62 m, 240 damage, two missiles. Mobile SAMs reach 44 m (long-range 55 m); helicopter weapons reach 34 to 36 m.
- Jets trail vapour and a hot exhaust, with wingtip vortices in hard turns.

**Movement and AI**
- The stuck check measures progress towards the waypoint. A hull edging back and forth against a corner used to pass it forever: 261 shakes in a test battle, now about 30.
- Arrival contagion: a hull stuck close to a crowded goal has arrived. A guard post it cannot reach moves to where it stands.
- Reinforcements gather at a staging point near home and go forward in threes (or after 25 s), not one by one.
- The line stops at the edge of known defences' reach until 80% of it has gathered, then goes in together.
- Remembered defences are not contact: nobody chases a gun seen minutes ago.
- Buying follows a role mix per stance (front line, fast, artillery, anti-air, air; a siege attacker brings 30% artillery), then counters.

**Reinforcements, fire support, audio**
- Bought ground vehicles are flown in: a transport passes over and the vehicle comes down under a parachute onto its landing point, decided when it is bought. Aircraft fly in from the map's edge. Delivery takes 3.5 s.
- Every barrage round is aimed 0.9 s ahead and drawn falling from the sky onto the spot it hits; smoke shells come down before the cloud.
- The interface beep for enemy strikes is gone. Barrages and heavy shells whistle down where they land.
- Points taken and lost come over the radio instead of the puzzle chimes. The fortress siren fades with distance.

**Arsenal**
- **Card ranks 1 to 10:** each rank adds +5% health and damage (+5% damage for strike cards). A rank costs coins (50 up to 5,000) and the card's blueprints (2 up to 90); universal blueprints make up the rest.
- **Equipment per branch** (Armour, Light, Artillery, Air):
  - six slots: gun, autoloader, armour, plating, engine, repair kit;
  - one special slot: reactive armour, auto-repair, veteran crew, or smoke dischargers (Epic and Legendary only).
- **Rarities:** Common, Uncommon, Rare, Epic, Legendary, with level caps 5 to 25. A new piece gives 40% of its rarity's top value; each level costs 30 coins times the level.
- **Caps:** damage and health +25%, rate of fire and speed +15%, damage taken -20%.
- **Merging:** three identical pieces make the next rarity. It always succeeds, the equipped or highest-level piece is kept, and the levels spent on the others are refunded.
- **Crates:**

  | Crate | Coins | Blueprints | Equipment rolls | Price |
  |---|---|---|---|---|
  | Battle | 60–120 | 6 | 1 | earned only |
  | Silver | 250–350 | 15 | 2 | 900 coins or 60 gems |
  | Gold | 800–1,000 | 45 | 4 | 3,000 coins or 180 gems |
  | Legendary | 2,000–2,500 | 120 (+10 universal) | 6 | 500 gems |

  - Rolls use odds per rarity. The gold crate's first roll is guaranteed Rare or better, the legendary crate's Epic or better.
  - Pity: an Epic within 5 gold crates, a Legendary within 25 gold or 4 legendary crates.
  - An odds screen on every crate shows the per-roll odds, the chance of at least one, and the player's own pity counters.
- **Sources:** a battle crate for each of the first five wins a day, a silver crate for a mission's first clear, three ad crates a day (the first silver) ten minutes apart.
- **Gems:** packs from $0.99 to $99.99. `GemStore.TestPurchases` grants them free in test builds; see the release checklist.
- Upgrades are applied to the player's vehicles and strikes in the simulation (`SimWorld.SetBoosts`); campaign balance runs without them.
- Tests never write the real profile.

**Results:** suite 236 passed, 17 skipped. Campaign: all 17 missions win 5/5 (checked before the arsenal, which campaign balance does not use).

### Still open
- A device check of the new screens (arsenal, loot card, curtain) and effects (drops, falling shells, contrails).
- The real ad network and store billing.
- Card blueprints only from crates (no shop sale yet); chapter-based rank caps are not enforced.

## 2026-09-27: AI review, catch-up for the losing side, bigger bombing blasts

The user asked for:
- artillery that no longer gets stuck at the map's edge when the enemy closes in and there is nowhere left to back off to;
- crowds of vehicles that no longer lock each other up (a random step aside, a little more room);
- no one shooting at the invulnerable camp bastions, while the AI still chases the enemy into its camp;
- a check of the other behaviours;
- bigger blasts for the bombing strikes;
- something that stops one side simply rolling the other over, after looking at how other games do it.

### Done

**Artillery at the map's edge**
- `SimWorld.EscapeRoute`: the way to back off from a threat. It tries straight back, then 35°, 70° and 110° to either side, and the way to its own camp. It picks the open spot that gains the most distance from the threat and keeps off the map's edge. A gun cornered against the edge used to drive into the clamp point and sit there.
- Used by the tactical AI (too close to fire, and kiting) and by the vehicle's own min-range retreat. With no way out (4 m or more), the gun stays and its machine gun fights.
- Artillery backs off only from ground threats. Running from a helicopter hovering overhead was the main way guns were herded into the edge: a gun cannot outrun one.
- Artillery sees 30 m (was 20 to 26 m, under its 20 to 25 m minimum range): it notices a threat before the threat is already inside its minimum range. It still needs spotters for its 70 to 90 m fire.

**Crowds**
- A vehicle wedged a second time with other hulls pressed round it steps aside first: a random open spot 3.5 to 6 m away, with the most room round it (`MovementSystem.TryUnjam`). Each vehicle picks its own way, so a knot breaks up instead of everyone dodging the same way.
- A vehicle that gives up on its route inside a crowd still moves out of the knot, so the others can pass.

**Invulnerable bastions**
- Nothing picks them as a target any more: not auto-fire, not guard or attack-move, not the tactical AI's target list, not aircraft run targets.
- A player order to attack one is refused.
- An ordered target that becomes shielded (a boss behind its glyph) is set aside: the vehicle shoots at something else meanwhile.
- The AI still chases enemies into their camp.
- With nothing else to do, the AI's army waits just outside the enemy camp's home zone (out of the bastions' reach) instead of parking under guns it cannot hurt.

**Bigger bombing blasts** (radius in metres)

| Strike or weapon | Was | Now |
|---|---|---|
| Airstrike | 6 | 8 |
| Napalm | 7 | 9 |
| Carpet bombing | 7 | 9 |
| Air raid | 6 | 8 |
| Cluster strike | 4 | 5.5 |
| Artillery barrage | 5 | 6 |
| Cruise missile | 15 | 18 |
| MOAB | 22 | 27 |
| Heavy bomber payload | 8 | 10 |
| Stealth bomber payload | 10 | 13 |
| Jet bombs | 7 | 8 |
| Guided bomb | 5 | 6 |

- The explosion is drawn as big as the strike reaches: 0.9x to 1.6x of its tier's size.

**Catch-up (quick modes)**
- What drives a snowball: the bigger army wins every fight, takes the points, earns more for them, and was paid a flat quarter of every kill.
- Other games work against it in several ways:
  - World in Conflict returns a lost unit's points;
  - Company of Heroes has upkeep;
  - Dota pays more for killing a dominant side (bounties);
  - many games give a safe, healing home base.
- Machine Brigade already had upkeep, home zones and bastions. Two gentle levers are new:
  - **Underdog reinforcements:** a side whose army is under three quarters of the other's earns faster, up to +50 % at a fifth or less. The boost settles over about 4 s. It is shown in mint next to the income ("+2.1/s +35%").
  - **Bounty by the odds:** a kill pays a quarter of the victim's cost, times √(victim side's army ÷ killer side's army), clamped to 0.5–1.5. The underdog picking off the big army's units earns up to 37.5 %; the big army finishing off the last of the small one earns as little as 12.5 %.
- Neither lever changes a close fight. Armies under 14 CP (the opening) change nothing.
- On in Conquest, King of the Hill, Deathmatch, Breakthrough and Defend. Off in campaign missions and the siege modes, which are balanced by hand.

**Tests:** `AiReviewTests`
- a gun at the edge escapes along it and opens the range;
- two packed groups of heavy tanks swap sides without locking up;
- no one targets a bastion, and an order to attack one is refused;
- the catch-up curve, the underdog's boost, and the bounty.

**Results:** suite 227 passed, 17 skipped. Campaign: all 17 missions win 5/5. Conquest AI-vs-AI matches on the twelve maps still end decisively, in 5.7 to 9.7 minutes.

## 2026-09-27: Launch points, directional armour, smarter fire, night, Defend, challenges

The user asked for:
- rounds that leave from the real launchers (both pods of the attack helicopter, both barrels of the twin tower together), checked on every vehicle;
- a list of every vehicle, defence and weapon;
- then, from a list of suggestions, items 1, 4, 8, 10, 11, 13, 7 and 6 (the screen flash only).

### Done

- **Launch points:**
  - Found from mesh names and vertices when a model's template is built.
  - Paired launchers (pods, missile rails, launch tubes) fire left and right in turn.
  - Launcher faces (tube bores, pod faces, box launchers) fire from a random tube across the face.
  - Only launchers round the slot's own muzzle count.
  - Twin guns fire both barrels together (0.05 s apart). L/R barrels are recognised and measured from their meshes.
- **Directional armour:**
  - Direct fire does 1.25x from the side and 1.6x from the rear (50° arcs).
  - Not aircraft, structures or fixed defences.
- **Smarter fire:**
  - Targets are scored by value and threat (1.2x if the target is aiming at the shooter, 0.3x if it is unarmed).
  - Heavy weapons (cooldown of 2 s or more) do not pile onto a target already doomed by shots in flight.
  - Artillery brackets: the spread narrows by 0.7x a shot on the same target, to 0.4x.
- **Night lighting:**
  - Blasts, gun flashes and fires light pools of warm light on the ground.
  - Illumination flares drift down over the fighting, lighting a 30 m circle.
- **Defend mode:** the enemy's Breakthrough against three dug-in sectors the player holds. The Defend stance entrenches still vehicles (-20 % direct-fire damage).
- **Challenges:**
  - Heroic and Iron tiers for every mission.
  - A third star per mission: no strikes, no aircraft, or a kill count.
  - A weekly fortress whose broken rings stay broken all week.
- **Track marks and trees:**
  - Every ground vehicle leaves track marks that fade over half a minute.
  - Hulls knock down trees, bushes, hedges and fences, which topple the way the vehicle drove.
- **Screen flash:** a brief flash of the whole screen on huge and ultimate blasts, stronger the nearer they are.
- **Balance:** campaign 17/17 at 5/5 (m03, m10, m13 and m16 retuned).

## 2026-09-27: Rarer, deadlier aircraft; neutral towers; defences that burn and stay

The user asked for:
- a gentler hit flash (many hits from many guns looked odd);
- dearer aircraft, since they were spammed, but deadlier ones (carpet bombing above all);
- ground vehicles that anti-air aside are not led round in circles by aircraft (the machine-gun logic);
- bombs that no longer burst before the bomber has flown over;
- fixed defences that smoke and burn when hurt and blow up when destroyed, leaving their ruin in place;
- better effects on the camp bastions and the other towers;
- neutral watchtowers, firing on both sides, on the capture points, with a sensible side for the towers of every mode.

### Done

**Hit flash**
- A soft flash, only for a hit that takes 2 % or more at once (never machine-gun patter), at most every 0.6 s, at 0.3 strength.
- Defences never flash; they smoke and burn instead.

**Air power**
- Aircraft cost about 1.45x as much, and a side may have at most six up at once (`TeamEconomy.MaxAircraft`, like the air slots of Wargame and World in Conflict).
- The commander keeps about a seventh of its army in the air.
- Aircraft weapons do 1.35x damage:
  - the heavy bomber's payload 400 (was 220);
  - the stealth bomber's 850 (was 520);
  - carpet bombing 330 (was 200), airstrike 240, air raid 210.
- Anti-air weapons do 1.4x damage, so anti-air stays the counter.
- Counters hold: 3 SAMs still beat 2 attack jets, and 3 AA vehicles beat 2 helicopters.

**Aircraft do not lead ground units about**
- A vehicle whose main weapon is a machine gun counted a helicopter as something to drive after, so a circling helicopter led it round and round.
- Now only anti-air vehicles go after aircraft. The rest shoot at one that comes into reach and hold their ground, and never swing their hull round after it.

**Bombs land under the bomber**
- A bomb keeps the bomber's forward speed as it falls, so it lands as the bomber passes over, not ahead of it (`BombsLandUnderTheBomber`).
- Airstrike aircraft now reach the bomb line as the first bomb lands.
- Each bomb drops from under the aircraft instead of out of empty air 25 m ahead of it.

**Defences**
- A damaged defence smokes from its top; badly hit, it burns in two places, throws sparks, and its ammunition pops.
- When destroyed:
  - a big blast at its top, a dust skirt, and concrete and steel thrown out;
  - a chain of ammunition blasts;
  - the ruin slumps over and leans, burns for 45 s and smoulders on.
- The ruin stays for the rest of the battle; it never sinks away as a vehicle hulk does.
- Twin and quad guns fire barrel by barrel, each from its own tip (the camp bastion, the flak tower, and any other model with side-by-side barrels).
- The bastion's roof carries twin flak for aircraft, instead of SAMs that came out of the middle of its roof.

**Neutral towers**
- Conquest and King of the Hill: a watchtower on each point that belongs to no side and fires on both, after Warcraft III's creep camps and the hostile mercenaries of Sins of a Solar Empire.
  - It stands again 100 s after it is knocked down, like a MOBA jungle camp.
  - It is grey, with a pale health bar and minimap blip.
- Each side's camp keeps its own bastions.
- Assault keeps towers that belong to the defender, as in Battlefield's Breakthrough.
- Siege keeps the whole fortress on the defender's side.

**AI and balance**
- The attack stance still prefers the weakest-held point, but only when there is a choice; a last point is attacked however hard it is held.
- A committed attack presses on for 60 s (it was 35 s, too short to cross open ground to a dug-in enemy), and the army waits 30 s (was 40 s) before committing.
- The test decks now look like a player's: the dearest aircraft (one at most), an anti-air card, an artillery card, then the dearest ground vehicles. With aircraft dearer, "the six dearest cards" had become half aircraft.
- m10 enemy: 15 CP at the start, 0.7 income.
- Campaign: all 17 missions win 5/5. Suite: 200 passed.

## 2026-09-27: Damage you can see, two-weapon vehicles, real air war, 200 m maps, epic siege, Attack and Defend

The user asked for:
- damage that shows on the hull, cluster rounds for the elite MLRS and Grad, and better weapons for the elites;
- at least two weapons on every vehicle, firing in turns with different delays (rockets and machine guns on attack helicopters), modelled on real vehicles;
- faster, higher jets and bombers; believable aircraft sizes; rotors that look right;
- aircraft that only anti-air kills easily, with other guns doing little to them and only aiming at them when nothing else is left; a jet to hunt enemy aircraft;
- some randomness in trajectories and blasts, so long-range weapons can miss;
- bigger maps, packed with more scenery;
- a fix for blasts and smoke screens drawn over each other;
- free, well-organised battle sounds;
- a grander siege: more sentries, bosses, a bigger base, several stages;
- Attack and Defend reworked after other games, with towers at the camps and at the spawn so no side is steamrolled.

### Done

**Damage and weapons**
- Hulls show damage:
  - grey smoke below 60 % health;
  - black smoke and flames below 30 %;
  - soot darkens them below 50 %.
- Hit feedback, after the usual arcade recipe:
  - a white flash (0.06 s, then a 0.12 s fade, at most every 0.15 s);
  - heavy hits rock the hull 1.5 to 4 degrees;
  - the health bar keeps a yellow trail of what was just lost, which catches up after 0.4 s.
- Cluster rockets (`ClusterDef`):
  - the elite MLRS and a new elite Grad scatter bomblets over the target;
  - each bomblet is its own small blast.
- Elites carry heavier weapons (HEAT 152 mm, APFSDS 105 mm, Hellfire volleys, AHEAD 35 mm).
- Every vehicle has at least two weapons, mounted as on the real thing:
  - machine guns fire runs of 6 to 10 rounds, then rest;
  - a heavy gun and its machine gun take turns;
  - each weapon starts at a random delay, and cooldowns vary by ±10 %.
- Guns keep their rhythm (`WeaponRhythmTests`).

**Air war**
- Aircraft sizes follow the real ones:
  - ground vehicles are about 0.8 of life size;
  - big aircraft about 0.5, so a bomber no longer dwarfs the map.
- Jets and bombers fly faster and higher; their turn rate grows with speed, so they do not wag their noses.
- Rotors turn at most 23 degrees a frame, with a blur disc, so they sweep instead of strobing.
- Guns and armour-piercing rounds do 0.3× damage to aircraft.
- Weapons that are not anti-air look at an aircraft only when nothing on the ground is in reach (and anti-air the other way round).
- The fighter jet hunts enemy aircraft; SAMs, flak and AA vehicles are what kill them easily.

**Randomness**
- Scatter grows with range, faster near the weapon's limit, so long shots can miss.
- Guided rounds sometimes lose lock (2 % point blank, up to 10 % at full range).
- Splash radius varies by ±15 %, and blasts vary in size and position.

**Maps**
- Battlefields are 200 m across instead of 160.
- Clumps of trees, rock outcrops and hamlets fill the open ground; every map was rebuilt.
- Blasts and smoke no longer pop over each other:
  - most effects emit into systems shared by the whole map, whose bounds span the battlefield, so Unity's distance sort between them was arbitrary;
  - each layer now has a fixed draw queue (`FxQueue`);
  - smoke screens are billowing flipbook smoke drawn over whatever burns inside or behind them;
  - blasts in front of a screen go into twin layers drawn over it (`BlastLayers.Route`).

**Audio**
- 63 recorded sounds in 27 categories: Sonniss GDC bundles (royalty-free) and CC0, credited file by file in `Resources/Audio/CREDITS.md`.
- The mix follows Wwise and FMOD practice:
  - variants never repeat twice running;
  - each category has a voice limit and a priority, so a rifle round never cuts a big blast;
  - far sounds are muffled, and big blasts far off arrive at the speed of sound (at most 0.3 s late);
  - big blasts duck the small arms for a moment;
  - fires crackle near the view.
- The synthesised sounds remain as a fallback.

**Siege**
- Three stages:
  - the outer line, whose relay stations must fall;
  - the wall ring, with its shield generators;
  - the keep, with the command HQ.
- Each stage's objectives are shielded until their stage.
- A time bank grows with each stage taken.
- A falling stage takes its defences down in a chain.
- The HQ fights harder as it weakens.
- A mobile-fortress guardian wakes at stage three.
- New fortress art:
  - a twin 155 mm coastal turret;
  - a flak tower with quad guns and a SAM box;
  - a Patriot-style missile battery;
  - a shield generator.
- 29 fixed defences per fortress, and every piece now stands on every map.

**Attack and Defend**
- Defend holds our front point, or the one under threat:
  - the army faces the enemy and chases only 26 m off the point;
  - it never falls back;
  - it digs in: a vehicle that stops goes hull-down and takes 20 % less direct-fire damage (artillery, rockets and bombs still land, which is how to dig it out).
- Attack goes for the weakest-held point: the enemies and towers seen round each point count against it.
- Watchtowers on captured points (Conquest, King of the Hill, Assault):
  - the holder's tower goes up 8 s after capture;
  - it is blown up when the point falls;
  - it is rebuilt 35 s after it is knocked down.
- Spawn protection in the capture modes:
  - two indestructible bastions per camp (heavy turret model, 40 m, hitting air and ground);
  - a 35 m home zone that repairs 2 % a second;
  - five seconds of spawn protection;
  - no enemy strikes on a camp.
- A side 100 tickets behind in Conquest gets a Behemoth, once.
- Assault is now a Breakthrough:
  - three sectors, A, then B (two points), then C, lie one behind the other towards the enemy camp;
  - only the front sector can be captured;
  - a sector taken locks, blows up its defences, adds time and CP, and moves the drop zone up;
  - overtime runs while a live point is still being fought over.
- AI fixes found along the way:
  - vehicles already at their rendezvous are no longer re-sent every decision, which kept whole armies shuffling;
  - an army of launchers and drone carriers closes to firing range instead of backing into the map's edge;
  - long-range units kite anything they outrange by 6 m or more.

**Balance** (five seeds, auto-commander, realistic decks)
- All 17 missions win 5/5. The siege mission (m13) takes 10 to 13 min.
- m03 player income ×1.2; m10 1.85; m13 1.85 with the HQ at ×2.2.
- The heavy turret has 2800 health and its guns reach 50 m; the flak tower has 2600 health.

### Known limitations
- Sounds have not been heard on a phone. Loop levels follow measured loudness, but still need a listen.
- The watchtowers borrow the guard-tower model.
- Real phones: there are still no measurements on one.

## 2026-09-27: No stutter, tougher vehicles, real artillery, APS, buildings that collapse

The user asked for:
- tougher vehicles (two to three times) and fewer of them;
- artillery that looks like artillery, plus more real equipment;
- an end to effects that stutter or seem to rewind, including in storms and when aircraft fire;
- Unity's own features wherever they help;
- AI tanks that no longer get stuck in the map's corners;
- better building explosions;
- every card unlocked for testing, with a note to lock them before release;
- a fix for the deck page that would not scroll, and a scan for other bugs.

### Done

**Stutter**
- Camera shake is off (`RtsCamera.ShakeEnabled`; its setting is hidden too).
  - Its noise ran at about 25 Hz, so at 30 fps the view jumped to a new place every frame.
  - Every blast, cannon, rocket and gunship shot added to it: that was the stutter in explosions, storms and aircraft attacks.
- Blasts no longer look like they restart.
  - Later fireballs of a blast now roll on from the middle of the sheet (new rolling-fireball layers) instead of flashing from frame 0.
  - The secondary pops are separate small explosions on a ring beyond the main fireball.
- Slow motion only plays when a boss dies, not for every ultimate explosion.
- The auto camera follows the fight on a critically damped spring, so it no longer lurches when its target changes.
- Rain streaks stretch with the frame time, so they no longer strobe at low frame rates.
  - Storms carry fewer drops.
  - Lightning is one flash that dies away.
- Every effect layer is drawn once as the battle loads, so Vulkan builds its pipelines then, not the first time a napalm strike appears.
- `AirMotionTests`: aircraft attacking ground targets fly smoothly in the simulation (no shuffling, no nose wag).

**AI and movement** (`StuckTests`: whole AI battles on all 12 maps)
- A hull that is blocked pivots towards its waypoint, then edges along the nearest free bearing, keeping to one side.
- A hull wedged twice backs off to open ground a few metres away.
- Anti-aircraft units stay behind their own armour instead of freezing on the spot.
- Results:
  - stalls fell from 1–4 per map to 0–1;
  - deep hull overlaps in a whole battle fell from 6 to 0;
  - heading wags fell from 261 to 104.

**Toughness and economy** (`balance.json`: `toughness`, `firepower`, `economy`)
- Vehicle health is ×2.5; bosses are ×0.85.
- Strike damage and vehicle and mine blasts are ×2; burning props are ×1.5; the MOAB does 4000 damage.
- Income is ×0.65 and supply ×0.8. A side may field at most 32 vehicles.
- Peak armies are about a quarter smaller.
- AI conquest battles destroy 17 vehicles a minute instead of 24.

**Artillery and new equipment**
- Rebuilt models:
  - the artillery is a CAESAR-style 6x6 truck gun;
  - the howitzer is a PzH 2000-style tracked gun with a rear turret and a long barrel;
  - the siege tank is a 2S7 Pion-style open-mount 203 mm gun.
- `grad_truck` (BM-21): a ripple of 20 rockets.
- `atgm_carrier` (Stryker ATGM style): two heavy missiles per launch.
- `aps_tank` (Merkava with Trophy): an active protection system that shoots down incoming missiles, drones and direct-fire rockets, with 2 interceptors reloading 6 s each (`ApsTests`).
- The new vehicles unlock in campaign missions 5, 7 and 11.
- The existing rocket vehicles stay: MLRS, Smerch-style heavy rockets, Iskander-style ballistic launcher, TOS thermobaric launcher and rocket technical.

**Buildings**
- A copy of the building shudders and sinks into the ground, leaning, while the rubble heap rises.
- A dust skirt rolls out, and billows pour up as each floor lands.
- Big buildings throw twice the chunks.
- Device check: `-mb-demolish`.

**Menus and testing**
- `Progression.TestUnlockAll` unlocks every card and doctrine. `Docs/RELEASE_CHECKLIST.md` lists what to switch back before a release.
- Menu pages scroll with a mouse drag. UI Toolkit only drag-scrolls for touch, which is why the deck page would not move in the editor.
- Shop cards line up: two-line name boxes, and the price pinned to the bottom of the card. The items note no longer lingers on other tabs.

**Balance** (five seeds, auto-commander, realistic decks)
- 16 of 17 missions win 5/5, and m16 wins 4/5.
- m03's three-star time is now 15 min.
- The player gets more CP in m06, m10 and m13.

### Known limitations
- **GPU Resident Drawer:** not enabled. It needs the Forward+ path on phones and should be tried only once a real device can be measured.
- **Real phones:** there are still no measurements on one. The camera shake and rewind fixes were found in code and in simulation measurements.

## 2026-09-27: Smooth blasts, map outlines, phone UI, line of fire, scale pass, map kit

The user asked for:
- smooth explosions, with a small shockwave and one big blast plus small ones;
- no hard army cap;
- a minimap with each map's own shape and its terrain;
- a phone-friendly UI with less text, redone menus, centred labels and better fonts;
- AI that cannot shoot through buildings or rock;
- richer maps;
- no jitter when vehicles touch;
- barrels that elevate when they fire high;
- at least two weapons per vehicle, listed in its description;
- wrecks that clear sooner;
- no doubled explosions;
- a project ready to play in the Unity editor, responsive on every device;
- sensible sizes: aircraft larger, tanks smaller, houses larger.

### Done

**Explosions**
- Point lights are gone from blasts. A fake ground light (an additive disc) replaces them, which removed most hitches.
  - Emulator hitches in the same battle: 203 → 68. This is a relative figure, not phone performance.
- Blasts from Medium up get a small air shockwave ring.
- A vehicle death plays one quick kill pop, then its own big blast.
  - Large wrecks cook off in a chain of small pops, not repeated big blasts.
  - This fixed the doubled or "reset" explosion: the old code played a Medium blast, then the delayed death blast, then a full cook-off chain.
- Wrecks burn for 12 s, stay 17 s and sink in 3 s.

**Economy**
- The hard cap is replaced by upkeep. Past the supply line (1.5 × the old cap), income falls, to half at twice supply (never below 25 %).
- Only a safety limit of 44 vehicles remains.
- The deck bar shows the income and the upkeep cut.

**Movement and combat**
- Contacts are calmer:
  - avoidance fades in and out;
  - there is a heading dead band while cruising;
  - braking is shared by push;
  - scripted units and bosses have right of way;
  - tanks settle at their final point.
- Ground vehicles are drawn through a velocity-predicting filter.
- Heading swings in a whole AI battle: 1426 → about 150.
- Line of fire:
  - buildings, rock, wrecks and walls that block fire are rasterised into a 1 m `CoverGrid`;
  - direct-fire weapons check it before targeting and firing;
  - a shot that is blocked anyway hits the wall;
  - vehicles close in until they are clear;
  - indirect weapons (mortars, artillery, bombs, drones) fire over.
- Barrels elevate: every model has an `Elevation` pivot on its gun, mortar or launcher group, which pitches to the ballistic angle for the current target.
- Every combat vehicle has at least two weapons. There are 18 new secondaries, with new models where needed (grenade launcher, guided bomb, drone gun, ATGM post).
- The tactical AI remembers each enemy it has seen, with a half-life of 45 s, and picks up nearby crates.

**Maps**
- Each map has its own outline, carved per map by `Tools/maps/boundary.py` inside the 160 m square: valleys, bays, a canyon rim.
  - Nothing drives or builds past it.
  - The outside is terrain with sparse, shadowless rock and trees.
- The minimap is the painted terrain, cut to the outline and turned to match the camera, with haloed blips.
- The map kit (22 new models) dresses every battlefield (`warzone` in `build_maps.py`):
  - wrecks with their craters in no man's land;
  - foxholes, trench lines, barricades, a wreck and a road checkpoint at every objective;
  - a field camp (command tent, camouflage nets, supply piles, a fuel bladder, a radio mast) beside each camp;
  - per theme: telegraph poles, pylons, ruins, dead trees and anti-tank ditches;
  - low road bridges across the Jungle Pass fords.
  - Cover comes in equal numbers on both halves. Campaign spawns and routes stay clear, and reachability is still proven.
  - Craters and wrecks scorch the ground beneath them.
- Props may turn in 45° steps; a diagonal prop keeps its bounding square as its footprint.

**Scale**
- `VehicleDef.Scale` resizes the model and the hull length and width; the hit radius is deliberately left alone, because scaling it upset the balance.
  - Aircraft are 1.05–2.0× larger.
  - Non-boss ground vehicles are 0.85×.
- `PropDef.Scale`: 25 buildings are 1.15× larger. The command HQ and the vehicle hangar are unscaled, so the fortress still fits.

**UI**
- Be Vietnam Pro for text (full Vietnamese coverage); Barlow Condensed stays for numbers.
- Battle HUD:
  - glass panels and icon-only tools;
  - a commander rail;
  - a selection card only when something is selected;
  - weapon chips and short names.
- It adapts to the screen shape (`MatchFor` from 4:3 to 16:9 and wider).
- Menus: icon mode tiles with one line for the chosen mode. Deck cards open a detail panel with every weapon (kind, calibre, targets, ammo).
- Button labels no longer end in an ellipsis.

**Editor**
- `EditorStartup` makes Play always start from the game scene (`Sandbox.unity`). It also opens that scene in a fresh session and adds the menu item *Machine Brigade → Open Game Scene*.
- Batch test and build runs use a mirrored worktree (`MachineBrigade-runner`), so the project can stay open in the editor.

**Balance** (five seeds per mission, auto-commander)
14 of 17 missions win 5/5; m02, m09 and m10 win 4/5. Before this round, 12 were 5/5 and m03 and m16 only 3/5.
The map kit first dropped m09 (the Mobile Fortress on Frostpeak) to 2/5, with stalls at the time limit, so the boss went from 10,500 to 9,000 hp.

### Known limitations
- **Ads:** still the placeholder; a real SDK needs the user's AdMob account.
- **Real phones:** nothing has been measured on one. On the emulator, Ashfield runs at about 23 fps with 15–24 vehicles (26.6 before the bigger buildings and the outside scenery). Use it only to compare builds.
- **Bridges:** they are visual. Vehicles cross at the ford underneath, and the deck is level with the ground.

## 2026-09-27: The big expansion (everything from the suggestion list, plus more)

The user asked for all of the earlier suggestions, and more:
- more vehicle variety: twin-barrel and longer tanks, artillery, long-range missiles with limited ammo that fall back to a machine gun;
- more aircraft;
- more debris and more realistic fire;
- units no longer driving through each other;
- an AI that holds its position instead of charging when outmatched;
- elite enemy units, a counter system and a rebalance;
- items bought with coins;
- a siege mode against a lit fortress, by day and by night;
- an optimisation pass once all of that was in.

### Done

**Collisions and AI**
- Hulls collide as capsules sized from each model's measured hull.
  - Drivers look ahead: they follow a friend going the same way, steer round anything parked or hostile, and pass oncoming traffic on the right.
  - New vehicles spawn on free ground.
  - Deep overlaps in a whole AI battle fell from 35 to 2 of about 200 contacts.
- The tactical AI weighs the odds (CP value × health, mobile units only).
  - Below 0.6 it falls back to a point it holds and waits for reinforcements. It attacks again at 0.95, or commits after 40 s so that dug-in defenders cannot stall it.
  - Buying is balanced: anti-air is matched to the enemy's aircraft, a core of ground units that can capture is kept, and high explosive is bought against demolition targets.
  - The main body no longer waits forever on vehicles that never finish a move.

**Abilities** (`AbilitySystem`)
- Limited ammunition: re-arm at home, or near an engineer; the AI sends empty launchers to re-arm.
- Engineers repair and re-arm the vehicles around them.
- EW jammers scramble missiles, drones and fire support aimed into their area.
- Mine layers lay mines, which the enemy sees only up close.
- Automatic skills: shield, repair, smoke, overdrive, barrage, flares, summon and EMP.

**Units**
- New ground vehicles:
  - twin-barrel tank, siege tank (203 mm), 300 mm rocket artillery, ballistic missile launcher, 240 mm siege mortar;
  - engineer, EW jammer, FPV drone carrier, mine layer.
- New aircraft: fighter jet, tank buster, recon drone, assault gunship.
- Seven elite enemy variants: refurbished models about 1.15× the base, black and gold with a red glow, gold health bars and skills. Deliveries turn elite at 10% on Normal and 25% on Hard.
- Six fixed defences: gun, AA and rocket turrets, bunker, howitzer pit, guard tower with a sweeping searchlight.
- Two bosses:
  - Hive Carrier: an airship that launches drone swarms.
  - Doomsday Train: raises its missile during a launch countdown.
- Boss phases on every boss: escorts called in, rage, bulwark shields and EMP pulses.

**Counters**
- Every vehicle has a class.
- `CounterTests` requires the counter to win twelve equal-CP skirmishes.
- Cards and the selection panel show "strong vs / weak vs".
- Defences are structures, so high explosive breaks them.

**Items, doctrines, events and daily challenges**
- **Items:** seven, bought in pairs for coins and carried into any battle: MOAB, cluster bombs, airdropped tanks, field repair, EMP, shield dome and a gunship on call.
- **Doctrines:** five, picked on the deck page.
- **Battle events:** supply crates to fight over, neutral bomber raids, and weather that changes mid-battle.
- **Daily challenges:** three a day, paid in coins.

**Modes**
- **Siege:** walls, gates, defences, a command HQ hardened 4×, floodlights, and fuel and ammo dumps that chain-explode. It works on all twelve maps' `_siege` variants.
- **Boss Rush:** four bosses in a row, with elite escorts.

**Maps**
- Four new battlefields:
  - Ember Ridge: volcanic, with lava rivers and a geothermal plant.
  - Jungle Pass: jungle, with a river, fords and a temple.
  - Skyhold Airbase: parked jets that chain-explode.
  - Metro City: urban, with a street grid, high-rises and lit windows at night.
- Three new themes.
- Every map has a Siege version.

**Campaign**
- An optional Boot Camp (m00) with timed tips, and m13–m16 built on the new content.
- Balanced with the deck a player really has at each point: 15 of 17 missions won in all five seeds, m06 and m11 in four of five.

**Effects**
- Flipbook fire, blasts and smoke: a Mantaflow fire loop, and procedural blast and smoke sheets.
- Mesh debris that bounces and burns, turret tosses, cook-off chains and textured scorch marks.
- Items with no damage (EMP, shield dome, airdrops) show pulses instead of blasts.

**Polish**
- War drums while a boss is on the field.
- Vibration on boss kills and cinematic blasts.
- Colour-blind team colours: blue and orange.

**Optimisation**
- Only the vehicles a battle can field are prewarmed.
- Metro City's skyline is limited to the ring the camera can see; before, it was 1M instanced triangles in 1631 batches.
- Static batching for map props that never move.
- Skill checks run at 4 Hz.
- Emulator measurements are relative only; see `PERFORMANCE.md`.

### Known limitations
- **Ads:** still the placeholder. A real SDK needs the user's AdMob account.
- **Real phones:** nothing has been measured on one. The emulator figures are for comparison between maps only.
- **Balance:** the counter targets and the campaign are tuned for the auto-commander; human play may need adjustments.

## 2026-09-27: Campaign, bosses, free-to-play economy, new modes, eight battlefields

The user asked for:
- a campaign with vehicles unlocked gradually, and bosses with cinematic moments (no veteran units carried between missions);
- a free game: coins after every match, a rewarded ad for double coins, skins and premium equipment bought with coins;
- more vehicles, aircraft and artillery, better bomber models and a detail pass on every model;
- more modes against the AI with difficulty levels (Deathmatch and others);
- more maps, with scenery that fits the terrain (rocks and scrub in the desert, forest in the snow).

### Done
- **Campaign "Operation Steel Fire".** Twelve missions over four battlefields, defined in `Resources/Data/campaign.json` and run by `MissionMode`.
  - Goals: capture, hold, destroy, escort a convoy, survive, kill a boss, intercept a train.
  - Missions can add waves, scripted convoys and boss routes, placed units, hardened demolition targets and their own army cap.
  - Each mission awards up to three stars, for winning, for speed and for losses.
  - Vehicles unlock as the campaign advances. Any card can be bought early with coins.
- **Bosses:**
  - behemoth (land battleship), in m06;
  - mobile fortress, in m09;
  - armoured train, in m12;
  - mega gunship (tandem rotors), in m03.

  Each boss has its own model, a boss health bar and a forced cinematic when it dies. The AI focuses its fire on the boss, and repair drops do not heal it.
- **Cinematic moments.** The biggest blasts trigger a short slow-motion moment with letterbox bars and the camera leaning in. There is at most one every 25 s, a boss death always gets one, and it can be switched off in Settings.
- **Free-to-play economy.** `PlayerProfile` is stored as JSON in PlayerPrefs `mb.profile`.
  - Coins and XP are paid after every match, and the result card offers a rewarded ad for double coins. `IRewardedAds` currently shows a 5 s placeholder in place of a real ad.
  - The shop has three tabs:
    - **Skins:** ten procedural camouflage patterns in the lit shader, previewed live on the menu battle.
    - **Premium:** coin-only cards.
    - **Unlocks:** campaign cards bought early.
- **Premium equipment:**
  - Titan super tank.
  - Heavy bomber: carpets twelve bombs.
  - Stealth bomber: three precision bombs with ultimate-tier blasts.
  - Sky gunship: side-firing 105 mm, 40 mm and 25 mm guns.
  - Napalm strike: leaves the ground burning.
  - Carpet bombing: flown by the heavy bomber model.
- **New vehicles:** IFV, 155 mm howitzer, thermobaric launcher (sets the impact area burning) and a twin-30 mm flak vehicle.
- **Quick modes against the AI**, each at Easy, Normal or Hard:
  - Conquest.
  - Deathmatch: first to 100 kills, or 12 minutes.
  - King of the Hill: hold the centre to 100 points.
  - Assault: take every point from a dug-in defender within 14 minutes.
  - Survival.
- **Eight battlefields.** New ones:
  - Redrock Canyon: desert canyon lanes, rock walls and an oasis market.
  - Whiteout Pass: a snow forest pass with a frozen lake.
  - Greenvale: hedgerowed farmland round a crossroads village.
  - Rust Yard: ruined industry and a marshalling yard.

  Dunebreak, Frostpeak and Ironport were re-dressed to fit their terrain: more boulders and cactus in the desert, more forest and snow rocks in the snow, a denser harbour.
- **Art (Blender agents):**
  - four boss models;
  - the strike jet, attack jet, drone, helicopters and munitions rebuilt with a fixed-wing kit;
  - three premium aircraft;
  - a detail pass on all 14 ground vehicles plus the car and truck: real track runs with sprockets and idlers, skirts, stowage, hatches and muzzle devices.
- **AI fixes found by measuring the campaign over eight seeds per mission** (94 of 96 won, up from 77):
  - The army now shoots demolition targets. Before, shells only splashed them, so a target with no enemy beside it never fell.
  - The main body no longer waits forever on vehicles that never finish a move: vehicles jostling for a slot, and anti-aircraft vehicles that hold short near tanks.
  - Hold missions leash the army to the point.
  - Missions raise the player's army cap to 30, because units placed at the start used to fill Conquest's 24 and no reinforcements ever came.

### Known limitations
- Ads are a placeholder. A real SDK (AdMob with test IDs, then the user's account) is still to be wired to `IRewardedAds`.
- There is no screenshot or clip sharing yet. It needs a native share plugin.
- Campaign balance is measured with a late-campaign deck (`CampaignTests`). A player still on the starter deck will find missions 5 to 12 longer.
- m06 and m12 are each lost once in eight seeds by the auto-commander, so the player may need to step in.
- Nothing new is measured on a real phone yet. The emulator checks were functional only.

## 2026-09-26: Command-console UI, three new battlefields, weather, settings, shadows

The user asked for:
- smoothness taken from how other games optimise;
- a full UI redesign with solid colours instead of see-through panels with outlines;
- more maps and weather;
- then muzzle fire and smoke for vehicles and aircraft;
- then more shadows, re-run performance research and proper settings.

### Done
- **UI redesign** (Stitch design system, Barlow Condensed and Inter):
  - Every panel is solid with a header strip, and buttons are tactile.
  - Selected states are solid amber; disabled states are solid greys.
  - The menu has numbered sections (mode, battlefield, difficulty, weather).
  - The result and pause cards have coloured heads, and the hint sits on a pill.
- **Maps.** Generated by `Tools/maps/build_maps.py`, each checked for reachability and played AI-versus-AI in the tests.
  - Dunebreak (desert): a refinery with exploding tanks and towers, an oasis market town and a pumpjack oil field.
  - Frostpeak (snow): a log-cabin village, a radar station and a lumber camp in pine forest.
  - Ironport (harbour): quays with gantry cranes and container yards, factories and a rail yard of tank wagons.
- **Art.** 25 new models from two Blender agents.
- **Map themes** (`MapTheme`):
  - ground palette, trees and clutter;
  - mountain colours;
  - water: river, frozen river or sea;
  - scenery houses and clear-day haze;
  - model grass colour and minimap colour.
- **Animated props:** radar dishes spin and pumpjacks rock.
- **Weather:**
  - Snow: drifting flakes.
  - Sandstorm: dust clouds, grit and an orange haze.
  - Fog: dense fog with low wisps.
  - Night: moonlight, lit windows and fires lighting the field.
- **Muzzle fire and smoke** (`MuzzleFx`) for vehicles and aircraft:
  - an orange core and a flame tongue on the barrel, with muzzle-brake side jets;
  - sparks and light gunsmoke that bursts out and hangs;
  - ground dust from cannons, back-blast from launchers, and a flicker for every machine-gun round.
- **Settings page** (scrolling, segmented), in the style of large mobile games:
  - **Graphics:**
    - preset: Auto, Low, Medium or High, becoming Custom when changed;
    - shadows, resolution, anti-aliasing;
    - frame-rate cap: 30, 60, 90 or 120, display-paced;
    - battery saver, glow level, brightness;
    - scenery density and effect detail.
  - **Gameplay:** screen shake, camera speed, interface size, FPS counter.
  - **Sound and language.**
- **Shadows:**
  - The single shadow map is refitted to the view every frame, so shadows are sharper zoomed in and cover the whole screen zoomed out.
  - Soft 4-tap filtering from Medium.
  - Tree shadows from Medium; clutter shadows on High.
  - Blob shadows when shadows are off.
- **Performance:**
  - Effects skip their particles off screen.
  - Particle screen size is capped.
  - Low bloom uses quarter resolution, four passes and the dual filter.
  - FSR 1 below full resolution.
  - Menus and pause draw every other frame until touched.
  - Swappy on release builds.
  - The frame-rate governor steps between 30, 60, 90 and 120.
- **Tools:** `EffectShots` renders effects frozen at chosen moments for tuning.

### Known limitations
- The emulator cannot judge performance. Real-device testing is still needed; see `Docs/PERFORMANCE.md` for Firebase Test Lab and Samsung Remote Test Lab.
- Not done yet from the research:
  - thermal scaling (Adaptive Performance);
  - pipeline-state warm-up;
  - a half-resolution particle pass;
  - tree shadow proxies;
  - a static shadow cache;
  - colour-blind mode.
- The refinery flare stack has a static flame model, not a live fire.

## 2026-09-26: Air power, a real town, mountains, effects that never reset, full audit

This milestone follows playtest feedback on four points:
- explosions and fires "reset" after a while;
- rings looked crude;
- unexplained stutter;
- buildings were illogical and repetitive, and the surroundings sparse.

The feedback also asked for:
- wrecks that stay (and later vanish);
- aircraft that fight as units and can be shot down;
- more vehicles;
- a full scan of the app for problems.

### Done

- **Effects that never reset:**
  - Explosions emit into a dozen shared particle systems. Before, pooled per-blast instances were cut short when a new blast needed the slot.
  - Fires burn in shared systems with no slot limit: they flare, die down and smoulder.
  - Wrecks burn for 45 s, stay about 75 s, then sink away.
  - Shot-down aircraft blow up in the air, fall with their momentum and explode on impact.
- **Stutter:**
  - The slow-motion dip on huge blasts was removed. It froze the game whenever one went off anywhere.
  - PhysX is no longer stepped; debris and turrets move on their own kinematics. It had spiked to 15 ms.
  - Rigid model parts are merged: a tank went from ~19 renderers to ~4.
  - Scenery is culled in cells and particle noise is a texture.
  - A frame-rate governor settles at a steady 30 fps when a device cannot hold 60.
  - `PerfProbe` (`-mb-perf`) logs frame times, hitches, engine markers and a scene census.
- **Ground markings:**
  - The `GroundMark` shader draws signed-distance, anti-aliased rings: objective rims with turning dashes and a capture arc, and strike telegraphs with a sweep to impact.
  - It also draws selection brackets, move markers and a ring under every aircraft.
- **Roster:**
  - Ten new vehicles: armoured car, tank destroyer, heavy tank, SAM launcher, mortar carrier, rocket technical, heavy gunship, scout helicopter, attack jet and strike drone.
  - Aeroplanes circle and fly strafing runs.
  - The commander keeps about a fifth of its army in the air.
  - Decks hold 8 vehicles.
- **Ashfield** is generated by `Tools/maps/build_ashfield.py`:
  - A paved square with a ring road, an outer lane, and streets lined with houses facing them.
  - Shops, apartments, a church, fuel depots, farmsteads, ruins, rock cover and forests.
  - The script proves every objective is reachable and reports anything it cannot place.
  - It uses 21 new building, barrier, civilian-vehicle and tree models.
- **Surroundings:** a faceted mountain range with snow and crags, forests climbing it, a river valley, and ground to the horizon.
- **Audit** by four reviewers (simulation, presentation, HUD/input/audio, data/balance). The fixes are in the last two commits:
  - Aeroplanes obey orders.
  - Artillery no longer freezes on close targets.
  - The commander defends drained points.
  - Kill rewards go to the right team.
  - Fog works with the orthographic camera on GLES.
  - Survival defeat is fair.
  - Audio pauses.
  - HUD updates only on change.
  - Balance was rebalanced from a DPS/EHP-per-CP audit.

### Known limitations

- The Android emulator tops out at about 30 fps even with nothing drawn, so smoothness can only be judged on a real phone.
- The back button is handled (Escape), but on the emulator GameActivity's text input consumes KEYCODE_BACK before Unity sees it; not verified on a device.
- Assault mode and further maps are still not started; there is still no background music (by request).

## 2026-09-26: Auto-play commander, cleaner and bigger explosions

Playtest feedback: explosions still showed claw-like streaks, the fire felt reduced, and most of the game should play itself rather than be micro-managed unit by unit.

### Done

- **The army plays itself.**
  - The player's side is run by the same commander AI as the enemy (Hard in Conquest). It buys vehicles, calls fire support, picks objectives and fights.
  - In Survival it holds a line between the base and the threat.
- **The player steers intent** from a commander panel:
  - Attack or Defend stance.
  - Auto buy and Auto support toggles, which are remembered between matches.
  - Tapping an objective chip (A, B, C) sends the whole army there. Tapping it again clears the focus.
- **Hand control is optional.** A vehicle given an order by hand is left alone until 20 s after that order finishes, then the commander takes it back.
- **The camera follows the fight** after 8 s without a touch.
- **Explosions:**
  - Sparks are round glowing points instead of stretched streaks.
  - There are more fireballs, sparks and burning debris, plus secondary pops for large and huge blasts.
  - Fire is brighter, more wrecks and heavy hits start fires, and wrecks burn for 40 s.
- **Tests:** 66 EditMode tests. The new `CommanderTests` cover focus points, the hand-control hold, auto buy and holding a line.

## 2026-09-26: Flicker fix, full roster, Conquest, strikes, weather and menus

### Done

- **Vehicle flicker fixed.** On OpenGL ES the URP SRP Batcher drew vehicles with stale transforms: turrets flashed back to an old pose and moving tanks stuttered. It was bisected on the emulator with screen recordings (single-frame brightness spikes per region, counted with OpenCV) and command-line debug switches (`Match.DebugFlags`). Before the fix there were 42–63 flashes per 14 s; after it, 0–1. The SRP Batcher is now off on GLES only. Specular anti-aliasing, a cap on reflected light and a bloom clamp remove sun glints on thin parts.
- **Weapons:**
  - Vehicles carry several mounts: coaxial guns, free roof guns and chin turrets, and hull-fixed pods. Each mount has its own target, cooldown and muzzle.
  - Salvos (MLRS, helicopter rockets), guided missiles that home in, flamethrowers and airburst flak.
- **Aircraft:**
  - The attack helicopter flies straight over obstacles and only anti-air weapons reach it; ground blasts cannot.
  - It banks, bobs, spins its rotors and crashes when shot down.
- **Roster:** jeep, APC, light tank, MBT, flame tank, self-propelled artillery, MLRS, anti-air vehicle and attack helicopter. There are 15 weapons in `balance.json`.
- **Models:** 19 new Blender models: the new vehicles, a strike jet, munitions, mountains, cliffs, boulders, sandbags, tank traps and dirt mounds. The existing tanks gained machine guns. Model tests check that every weapon mount has its muzzle.
- **Economy:**
  - Command Points with a bank cap and a unit cap, deployments with delivery, and kill rewards.
  - The player buys from a deck of 6 vehicles and 2 supports in both modes.
- **Fire support:** barrage, airstrike (jet flyover, falling bombs, one telegraph ring per bomb), cruise missile, smoke screen (blocks sight) and repair drop. All are telegraphed and friendly-safe.
- **Conquest mode:**
  - Three objectives on `ashfield_conquest`, capture rates (jeep ×2, APC ×3, aircraft cannot capture), contested points, ticket bleed and ticket loss per vehicle lost.
  - Results, and a Conquest AI that counter-picks, saves for strong units, strikes clusters, repairs groups and chooses objectives by value (Easy, Normal, Hard).
- **Menu and HUD:**
  - The main menu runs over a live AI-versus-AI battle. It offers mode, difficulty, weather, a deck editor and settings (volume, effects quality, reduced motion, FPS, language).
  - The in-match HUD has ticket bars and objective chips, the deck bar with CP meter and cooldowns, strike targeting, a rotated minimap (tap to jump), a mission banner, pause and results.
- **Environment:**
  - Weather: clear, overcast, rain and storm. Mood lighting and fog, rain streaks and splashes, wet ground, gusting foliage, lightning and thunder.
  - A ring of mountains and outcrops around the map. Terrain props inside it shape lanes and fortify the objectives.
- **Explosions:**
  - A new particle shader gives noise-eroded fireballs with hot cores and lit, billowing smoke. Every puff has its own seed and evolves over its life.
  - Burning debris flies on arcs, trailing smoke.
- **Audio:** synthesised launches, flak, flamethrowers, jet passes, a helicopter rotor loop, strike alarms, objective chimes, rain and thunder.
- **Tests:** 60 EditMode tests. They include headless AI-versus-AI Conquest matches with the shipped content and headless Survival waves.

### Known limitations

- Performance on a real phone is still unmeasured; the emulator runs on the desktop GPU.
- The terrain is flat inside the battlefield; the relief is the mountain ring outside it.
- There is no fog of war yet: the AI sees what its units see, but the player's view shows everything.
- Assault mode and further maps are not started.
- There is no background music (by request).

## 2026-09-26: Visual overhaul, battle effects, audio and tactical AI

The voxel look was replaced after playtest feedback ("stiff and crude", poor font and UI). Quality target: [3d_astra](https://github.com/buicongnguyen/3d_astra), whose Blender kit is reused with the owner's permission.

### Done

- **Art pipeline:** low-poly models generated by Blender scripts (`Tools/blender`, based on 3d_astra's `frontier_kit.py`): bevelled parts, weighted normals, baked vertex AO and named PBR materials, exported as GLB and loaded with glTFast. There are 24 models (4 vehicles, buildings, props, trees, rocks, rubble and debris).
- **Rendering:**
  - A `MachineBrigade/Lit` PBR shader with vertex AO, team tint and wind sway.
  - An orthographic 3/4 camera.
  - A procedural terrain texture with roads and footprints.
  - Hemisphere ambient, a reflection cubemap and fog.
  - ACES post-processing with bloom.
- **Surroundings:** the map no longer ends in a void. Fields, a river, forest belts, farmhouses and rocks extend 230 m out, drawn with GPU instancing (about 9,000 instances in 12 batches).
- **UI:** the HUD was rebuilt in UI Toolkit with the 3d_astra palette, the Inter font, vector icons and en/vi strings.
- **Jitter fixes:**
  - Hull overlap is resolved gradually instead of in one step.
  - Heading is held while rolling into the final waypoint.
  - Shadow bias and distance were tuned, and MSAA added.
- **Effects:**
  - Bigger explosion tiers with extra dirt, ember and dust-ring layers.
  - Machine-gun bursts of three staggered tracers.
  - Smoke trails behind tank and artillery shells, and muzzle smoke.
  - Lingering fires where fuel exploded or buildings collapsed.
  - Ammunition cook-offs in burning wrecks.
  - Tread dust behind moving vehicles.
  - Smoke columns darken at the source, thin into grey haze and drift with the wind, so they no longer hide the fight.
- **Audio:** every sound is synthesised at startup (`SoundSynth`): cannon, heavy gun, howitzer, machine gun, three explosion sizes, building collapse, a wind loop and a UI click. `AudioDirector` plays them from simulation events, panned by screen position and faded by distance from the camera, with per-sound cooldowns and a 20-voice pool.
- **AI:**
  - **Target choice (both sides):** vehicles prefer targets their weapon counters, badly damaged ones and ones that can be finished with this shot, and they focus fire with teammates.
  - **Guarding (both sides):** idle vehicles no longer stand still while being shot. They close in on visible enemies, and on whoever just hit them, within a 16 m leash, then drive back to their post. Artillery and unarmed vehicles hold position.
  - **Tactical opponent (`TacticalAi`, replaces the placeholder):**
    - The main body advances in bounds anchored on its lead vehicle and waits for stragglers.
    - Fast vehicles swing round a flank.
    - Artillery keeps a standoff distance, shells clusters of three or more, and backs away from anything inside its minimum range.
    - Badly damaged heavy vehicles pull back behind the line.
- **Tests:** 43 EditMode tests. New ones cover the AI (guarding, returning to post, target choice, artillery standoff, pulling back) and a headless 90 s sandbox battle that must reach contact.

### Known limitations

- Pulled-back vehicles stay in the rear; there is no repair yet.
- The flank side is fixed per match (chosen by seed).
- Audio has no music, and there is no volume setting yet.
- The Blender models cover only the four sandbox vehicles. APCs, MLRS, AA and helicopters come with Phase 3.

## 2026-09-26: Combat sandbox (Phase 1 and the start of Phase 2)

A playable test battle on the Ashfield sandbox map. It runs on the Android emulator (functional check only; no phone measurements yet).

### Done

- **Simulation** (`Scripts/Sim`, no engine references):
  - 20 Hz fixed step.
  - Stable entity ids.
  - Commands validated on submit: Move, Attack, Attack-move, Stop and Retreat.
  - Team vision.
  - Grid navigation: A* with corner-safe line-of-sight smoothing, formation slots, and stuck detection.
  - Turret aiming, projectiles with travel time, the damage table and splash.
  - Delayed explosions, with chain reactions that terminate.
  - Destroyed buildings unblock the grid.
- **Data:** `Resources/Data/balance.json` (4 weapons, 4 vehicles, 7 props) and `maps/ashfield_sandbox.json`. Both accept `//` comments. Load errors name the offending field.
- **Sandbox mode and placeholder AI:**
  - Starting forces for both sides.
  - Escalating enemy waves every 30 s.
  - A reinforcement call (+2 vehicles, 12 s cooldown).
  - Enemy groups attack-move towards the nearest player vehicle.
- **Voxel art generated in code:**
  - Jeep, light tank, main battle tank and artillery, in team colours.
  - Two house sizes, wall, fuel tank, barrel, ammo crate and tree.
  - A greedy mesher, pre-split debris chunks and rubble.
- **Effects:**
  - Five explosion tiers built from particle layers: flash, fireball, smoke, sparks, debris, shockwave and a light.
  - Muzzle flashes.
  - Tracers timed to the simulation, with arcing artillery shells.
  - Scorch decals in a ring buffer.
  - Burning wrecks, and turrets blown off by cook-offs.
  - Physics debris from destroyed props.
  - Camera shake, and brief slow motion on huge blasts.
  - All pooled, with Eco and High budgets.
- **Controls:**
  - Tap to select, move or attack; tapping a barrel or building attacks it.
  - Double-tap selects all vehicles of that type.
  - Long-press and drag box-selects.
  - One-finger pan and pinch zoom.
  - HUD buttons: All, Stop, Retreat, Attack-move, Reinforce and Restart.
  - Mouse wheel and right-drag in the editor.
- **Rendering:** three hand-written URP shaders (VoxelLit, Unlit, Particle). Vertex colours are linearised for the Linear colour space.
- **Tests:** 38 EditMode tests. They cover content parsing, navigation, commands (including R04 retreat), combat (T01 single damage, T05 chain termination, death explosions, building unblocking), determinism and the voxel mesher.

### Known limitations

- Vehicles drive through wrecks and each other's wrecks. The plan's "large wrecks block" rule is not implemented yet.
- Shots pass through buildings; there is no line-of-fire check.
- Explosions read small at the default zoom. Fireball size, lifetime and bloom need tuning.
- The pace is very lethal: most of the starting force is lost in under a minute. TTK and HP need tuning.
- The deck/CP economy, helicopters, fog-of-war visuals, Conquest tickets and the real AI are not started. These are Phase 3 onwards.
- HUD text is English only and uses the built-in font. Be Vietnam Pro and the localisation tables come with the menus.
- There are no haptics yet: `Handheld.Vibrate` is too long and a short Android vibration plugin is needed.
- The emulator runs on the desktop GPU, so its FPS says nothing about phone performance.
