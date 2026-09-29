# Changelog

Every merge into `main` is a version, numbered from the first commit (a docs-only merge bumps the patch
number). Work on `feature/visual-overhaul` that is not on `main` yet sits under Unreleased; new entries go
there, and the next merge into `main` turns it into a version. Each version keeps its prompt notes and lists
its commits.

## Unreleased (feature/visual-overhaul)

### Design document: armour, penetration and weapon forms

- Every card shows armour levels by face and the main weapon's effect on each armour level, aircraft and structures (✓ ~ ✕).
- Every weapon table has penetration, form and tags. Section 10 adds a counters table and the icon legend.
- Fixed: the combat-value table uses the current roster, Boss Rush's "{0} bosses", the HQ instead of the bastion, the map, mission and difficulty counts.
### Prompt 19: the Silver Bug rebuilt as Aurel's orbital spacecraft (DECISIONS 18A)

- The final boss keeps its id `silver_bug` (records, progress and achievements stay) and is now a big military shuttle:
  new model, its crashed form, a satellite and a drop pod (`Tools/blender/mb_orbital.py`; the saucer builder is gone).
- Altitude tiers, data any boss can opt into (`"tiers"`): 15 s in low orbit at the start (out of reach, guns held),
  then a fixed cycle per phase, never back to orbit: phase 1 high 25 s / low 10 s, phase 2 high 15 s / low 20 s,
  3.5 s per change (hit as the lower tier meanwhile). High altitude: only long-range SAMs, Patriot batteries, fighters
  and stealth fighters (`"ceiling": "high"`); low: every anti-air weapon, helicopters, and railguns (`"ceiling": "low"`).
- Parts (70 % of the body, 7 % each): the main engine (broken: it stays low), four manoeuvring thrusters (slower,
  longer changes), two point-defence lasers (its APS against SAMs and fighters' missiles), the drop-pod bay, the
  satellite uplink (its big attack) and the ventral laser turret. Armour by altitude: hull 4, belly 2 (low), 3 crashed.
- Drop pods (`"pods"`): two at a time in orbit and at high altitude, 1-2 vehicles each, low-altitude targets while they
  fall 6 s (shot down, nothing lands), at most six of their vehicles alive. Escorts come as it leaves orbit, with two
  fighters; phase marks 70 % and 30 %.
- Big attack `bug_rod_rain` replaces `bug_laser_sweep` (a new `rods` shape): five tungsten rods on the densest groups,
  heavy armour first, 1 600 kinetic, penetration 4 on the roof, 6 m, 4 s of warning, every 60 s; the first from the craft
  in orbit, the rest from its satellite; the uplink broken cancels or ends it; smoke and APS do nothing, domes absorb
  part. No boss big attack is stopped by smoke now.
- Phase 3: it falls to a set point mid-map and fights on as a ground fortress (a ground target, the wreck model, four
  guns all round awake, passable debris that blocks fire, its ground closed to routes and cleared of units). Very Hard:
  it seizes the player's drones and drone launchers for 6 s now and then; jammer and EW-tower cover keeps them.
- HUD: an altitude chip with the seconds to the next change and the phase marks on the boss bar; tapping it lists the
  deck ✓ ~ ✕ by what reaches its tier. The Guide has an altitude section; every text is new or rewritten in both
  languages (`OrbitalText`, the campaign's chapter 9, the boss files, briefings and radio lines): no saucer is left.
- Boss Rush fights it on the Launch Site (`"arena"`), as the sea boss at sea. Sandbox calls for prompt 21:
  `JumpPhase`, `ForceTier`, `TriggerBig`, `SetBigOff`, `Break`.
- Tests: `OrbitalBossTests` (10) and the boss tests it touched; the 5-seed runs, the stuck check round the crash site
  and the FPS checks wait for the testing phase.
### Prompt 20 L-M: towers (Iron Dome, rocket battery, SAM post) and two new battlefields

- The C-RAM's rank-7 Iron Dome branch (it replaces the Hunter; a saved Hunter choice is dropped): interceptor missiles
  for rounds lobbed at anything within 60 m (artillery rockets, half the shells, drones, long-range missiles), never
  direct fire or energy; six in the launcher, reloaded whole 12 s after the last launch; its own icon, behaviour lines
  and notes. The enemy AI picks Iron Dome or Centurion by the player's deck.
- The rocket battery's rockets arc over walls and cover (checked; a test); an AI's layered base keeps rocket batteries
  in its yard against attackers at the wall. The AA tower's SAM post reaches 60 m, between the flak and the Patriot;
  the flak branch's quad 23 mm hits harder (22 a round), so it is the drone and swarm killer.
- Open-Pit Mine (terraced pit, haul roads, a fixed route for a slow boss in the map data) and Orbital Gateway (radar
  station, side launch pads, an open drop-pod field): Conquest, Survival, Siege and long versions, camps and outposts,
  menu pictures, names, guide text; in the skirmish list.

## v0.29.0: Prompts 15-18 (armour and penetration, the sea and escorts for every boss, long maps and new units, the roster review, big attacks) and the 187-page design review

2026-09-29 · merged into main

### Prompt 15 (battle rules): armour levels, penetration, six damage types

- Every unit has armour 0-4 on its front, sides, rear and roof (towers, buildings and aircraft the same all round,
  bunkers thicker in front, boss parts their own); every weapon a penetration 0-4 from the real weapon. A round a level
  above the armour does all its damage, level three quarters, then 0.4, 0.15 and 0.05. Top-attack missiles, drones,
  bomblets, artillery, bombs and diving aeroplanes hit the roof.
- Six damage types: kinetic, shaped charge, high explosive (thermobaric harder on buildings), fire (burns on),
  fragmentation (flak and anti-air missiles), energy (lasers). Reactive armour and cages stop shaped charges, APS shoots
  down missiles, rockets and drones, flares fool missiles, smoke scatters lasers.
- Equipment reads by level (+penetration, +side armour, damage against heavy armour 3-4); old pieces keep their slot,
  rarity and level. Elites are a level thicker in front. The commander picks what pierces the armour it sees.
- Rebalanced from the combat-value re-run: IFV 6 CP, light tank 3 CP, flame tank 4 CP, scout helicopter 4 CP, car bomb
  2 CP, sturdier SAM launcher and rocket technical.

### Prompt 16 (part 1): Lighthouse Bay, Leviathan and its fleet

- New battlefield, Lighthouse Bay: a rocky coast on the sea, two coves with beaches and piers, the lighthouse on its
  headland (hold it to see the fleet), abandoned coastal batteries to take (their guns fire on ships), a fishing
  village and an old fort. Conquest, Survival and Siege, and in the skirmish list.
- New boss, Kessler's Leviathan: a battleship at sea that shells the coast (marked, sweeping along it), fires cruise
  missiles, lands tanks, launches helicopters and calls jets; its CIWS shoots down missiles and drones, its sides shrug
  off direct fire but its deck does not. Below 40 % it runs for open sea on a clock. It lists, breaks in two and sinks.
- Its fleet: escort corvettes (their CIWS covers it), fast missile boats that raid the pier heads, landing craft.
- Chapter 4 ends with "Leviathan" (4-11); it opens the heavy fortress's Long-range coastal battery. Boss Rush sails to
  Lighthouse Bay for it and back; Operations adds the Sea storm and Fleet mutators.
- Low graphics: simpler water and wakes.

### Prompt 16 (part 2): the old bosses' new weapons, escorts for every boss

- New weapons, each a part you can break: the Iron Train's mortar car (it lobs over cover), the Tempest's interceptor
  laser and the Behemoth's protection system (they shoot down missiles, drones and rockets), the Inferno's fire trail,
  the Hive's jamming aura, the Bastion's Kornet launcher, the Doomsday Train's rocket and long-range SAM cars, two AA
  mounts on the Rail Supergun, and two more CIWS and two rocket launchers on the landing hovercraft. Their health was
  retuned so the fights last about as long as before (within 10 %).
- Every boss brings escorts: a group with it and another at each phase change, at most 4-6 alive by difficulty (fewer
  in Boss Rush). Each group has a helper that repairs the boss, jams your missiles, covers it from the air or marks your
  units for its guns, so you choose between the boss and its escorts. Escorts stay near their boss, pay CP when
  destroyed, wear an orange mark, and the boss bar counts them. The old escort calls are replaced by this.

### Prompt 17 A-B: long maps and layered bases

- Siege, Defend, Endless and the weekly fortress play on long battlefields: 300 m across and 480 m along the attack, the
  map's own battlefield in front and a layered base behind it (all 20 maps; the other modes keep their 300 m maps).
- The layered base: a buffer zone of dragon's teeth, ditches, wire and firing positions, forward works with the relays,
  an outer wall with a main gate and two sally ports, a yard, an inner wall (the keep) and the HQ; the defenders land in
  the keep, the attack's reinforcements land further forward as each ring falls.
- More slots on a long base: HQ level 1 to 5 open 4/1/0/1 up to 8/5/3/4 (small/medium/large/utility), plus forward
  strongpoints. New slot places (outer gate, outer wall, yard, inner wall); one base plan fits both kinds of base, and
  the Base screen shows each map's long base as its own entry.
- The camera looks along a long map's length, zooms out further, and the minimap keeps its rectangle.

### Prompt 17 C: new units and towers

- Stealth fighter (20 CP): unseen until it fires, four AIM-120s, two small guided bombs for air defences, a 25 mm gun.
- Loyal wingman drone (6 CP): flies with your manned aircraft and may draw the missiles fired at them; outside the
  six-aircraft cap, four a side.
- Focused-laser tank (10 CP): its beam burns harder the longer it stays on one target (x0.3 to x2 in 6 s).
- Shield carrier (7 CP) and shield generator (large tower): domes that take every hit but energy for the friends inside
  until they break; domes do not add up.
- Bunker vehicle (8 CP): digs in when it stands (3 s): thicker front, 30 % more reach, turret all round.
- Drone mothership (14 CP): flies a swarm of eight FPV drones anywhere; the drones are not aircraft.
- CP relay (small tower): more CP for its side, two to a base, not on outposts, silent for a while after a hit.

### Prompt 17 D: roster review

- Merged cards: the A-10 is now part of the attack jet (30 mm cannon, rockets, bombs, two Kh-29 anti-tank missiles,
  R-60s; armoured; 15 CP); the Ka-52 is part of the attack helicopter (Hellfires in pairs from 55 m, out of short-range
  flak, and Stingers; 11 CP); the ATGM carrier is gone (FPV carriers, IFVs and ATGM towers do its job); the fortification
  sapper is part of the engineer (repairs vehicles and towers, clears mines); the hidden gun pit is gone from the towers.
- Your progress moves across: the higher rank and the blueprints, the coins of the lower rank back, a bought Ka-52
  refunded; gun pits in your bases become gun turrets and their equipment moves over (or back to the bag).
- Twin-barrel tank: two 120 mm guns fired as one volley, a long reload, quicker than the heavy tank: the tank hunter.
  Heavy tank: its 152 mm loads high explosive for buildings and light vehicles on its own; 12 CP.
- The new units' costs from the combat-value measure: stealth fighter 14 CP, swarm carrier 8, bunker vehicle 6.
- Lighthouse Bay has a long Siege map; the hovercraft's escorts ride fast missile boats; the campaign opens 5-7 cards
  a chapter.

### Prompt 18: a big attack for every boss

- Every boss has one big attack, telegraphed: its zone lights up in its exact shape (a circle, a strip, a line, a sweep,
  the points of a walking barrage, a missile's landing) with a countdown, the part that fires it glows on the boss and
  flashes on the boss bar, and its general or your command says it on the radio. About 30 s after the boss appears,
  then on its own cooldown.
- Break that part during the warning and the attack is cancelled ("Broadside cancelled"); each gun car, rocket box,
  drone rack or flamer takes its own share; with the part gone for good the boss has lost its big attack until it
  patches it. An EMP delays the Tempest's and the Silver Bug's charge.
- The Doomsday Train's tactical missile, the Leviathan's cruise missile volley and the Hive's drone swarm fly and can be
  shot down by anti-air, C-RAM, point-defence lasers and APS. Smoke cuts the Silver Bug's laser to a fifth (not the
  Tempest's railgun); shield domes take the Ice Fortress's rocket rain.
- Your ground units inside a warning get out on their own if they can make it, and go back after.
- New boss parts: the Doomsday Train's missile erector and bomb bays on the Hive Carrier and the Command Airship.
- The boss's Guide tab explains its big attack: what it does, how to get out of it, how to stop it, whom it is for.
- By difficulty: Easy hits softer, less often, with a second more warning; Hard and Very Hard come round sooner.

<details><summary>29 commits</summary>

- `5f808c8` 2026-09-29 Design document: section 20, a picture library (every vehicle, elite, boss, tower and module rendered large, in-battle shots, effect sheets, model and terrain sheets, stuck heatmaps)
- `cd90e57` 2026-09-29 Prompt 15 D: the armour and weapon icon set drawn from scratch (57 icons: 15 armour, 30 weapon forms, 6 damage and thermobaric marks, 3 extra marks, 3 verdicts), fills, holes and dashes in the icon renderer, CombatFacts and KitCombat, the row on deck, collection and tower cards, the show-numbers setting
- `46b6e33` 2026-09-29 Prompt 15 E: the icons where they show: the detail page (armour diagram, chips on the Weapons tab, the effectiveness table, generated strong/weak lines), the legend page, the Base and Outpost trays, the five-shield cover rows, the tray's hold tip, the selection strip, the enemy tap tooltip, boss parts
- `0cc2d54` 2026-09-29 Prompt 15 sim, milestone 1: armour levels, penetration and the six damage types
- `c34a8df` 2026-09-29 Prompt 15: the combat icon tests, the icon sheet, the enemy tooltip battle shot; Vietnamese words for icon and tooltip
- `b14c49a` 2026-09-29 Prompt 15: the icons read the sim's data (armour by face, forms, penetration, tags, Matchup's effect row, verdicts and strong/weak summary); +N and enemy tooltip layout fixes; the stray music metas out of the index
- `0bf1fe0` 2026-09-29 Prompt 15: detail-weapons and detail-armour screens (scrolled to the table and the diagram), the deck's shields beside its summary, a narrower enemy tooltip; UiShots takes a comma list of names
- `a4af56f` 2026-09-29 Prompt 15 screenshots: the combat icon sheet at 16:9 and on the 1280 x 720 screen at the smallest size, the deck's card row and cover, the detail page (armour, Weapons tab with the table), the legend, the enemy tooltip with a held tray card
- `4d07b15` 2026-09-29 Prompt 15 sim: counters, the gear migration, counter-picking AI, first rebalance
- `fe23bb2` 2026-09-29 Card pictures for every fixed defence (the super-gun, the spawn bastion, the fallback post share their models' renders; the targeting station rendered), and the design document's picture library finds each card's render through the manifest (the utility modules' pictures are named after their models)
- `851c62d` 2026-09-29 Prompt 15 sim: the combat-value re-run, the rebalance and DECISIONS 14A
- `2c6fcdc` 2026-09-29 PlayShots: in-battle pictures from Play mode (fixed maps, decks and seed, views from the sim, the live HUD drawn off-screen and blended over); DECISIONS 14B; the design document's icon set pages
- `4855941` 2026-09-29 PlayShots: wait for the new match's world, and close views on the towers nearest the HQ
- `080eee9` 2026-09-29 Prompt 15: the legend's counter table follows the sim's (smoke cuts beams, a jammer row), the enemy tooltip's multiplier from above for aircraft as the sim's verdict, the test checks the sim's Verdict
- `739565d` 2026-09-29 Prompt 15 screenshots after the sim's rebalance, and the in-battle pictures (battle3d-conquest, -siege, -defend with three close views of the base, -boss, -air, -barrage: 3D and the compact HUD from Play mode)
- `5e7f5aa` 2026-09-29 DECISIONS 14B: the checks as run
- `8b42d05` 2026-09-29 Prompt 16 E+F WIP: old bosses' new weapons, escorts for every boss (uncompiled)
- `497e16a` 2026-09-29 Prompt 17 C sim: stealth fighter, loyal wingman, focused-laser tank, shield carrier, bunker vehicle, swarm carrier, shield generator and CP relay (data, domes, deploying, wingman flight and decoy, laser ramp, drone swarm, relay income, AI use)
- `3ff6baa` 2026-09-29 Prompt 16 A: Lighthouse Bay (Conquest, Survival, Siege): a coast on the sea in the south-east (36 % of the square), two coves with beaches and piers, the lighthouse headland, cliffs with a coastal battery each, a fishing village, the old fort; its sea data (lanes, landings, piers, batteries) in every version
- `5a7f328` 2026-09-29 Prompt 17 A-B: long battlefields (300 x 480 m) with the layered base, for every siege map
- `d652c02` 2026-09-29 Prompt 16 E+F: old bosses' new weapons as parts, one escort system for every boss, health retuned from the kill-time lab, DECISIONS 15B
- `f0ca969` 2026-09-29 Drop a stray draft and two Unity-generated music metas from the prompt 16 commit
- `1551778` 2026-09-29 Prompt 17 C: the eight new units and towers finished: temporary models, texts, Guide cards and Behaviour lines, icons, dome and deploy views, In-action scenes, campaign unlocks, behaviour tests, DECISIONS 16C, CHANGELOG, ASSET_DEBT
- `8d6a1a3` 2026-09-29 Prompt 17 A-B: the sim, views and Base screen on long battlefields; layered-base slots, labels and plans; DECISIONS 16A
- `8833077` 2026-09-29 Prompt 16 B-D, G: Leviathan and its fleet at sea, chapter 4's epilogue, Boss Rush's sea switch, two mutators, Low water
- `f974235` 2026-09-29 Prompt 17 D: roster review, merges and save migration; C.9 costs from the measure
- `15ab08f` 2026-09-29 Prompt 18: a telegraphed, interruptible big attack for every boss, three new boss parts
- `ba24e8d` 2026-09-29 Card renders for the prompt 17 units and towers, Leviathan, and the five bosses rebuilt in prompt 16
- `e993f93` 2026-09-29 Design review PDF: section 7b (Lighthouse Bay and the fleet, escorts, long maps and layered bases, the roster review, every boss's big attack), the damage table on prompt 15's six types and penetration; 187 pages

</details>

## v0.28.4: Docs: prompt 24 saved (on hold)

2026-09-29 · `9a112f5`

## v0.28.3: Save the owner's prompts 22 (story, names, Commander system) and 23 (mission events, text dialogue), on hold

2026-09-29 13:38 · `75f10f2`

## v0.28.2: Save the owner's prompt 19 (the Silver Bug as an orbital spacecraft), on hold like 20 and 21

2026-09-29 13:11 · `9f5707f`

## v0.28.1: Save the owner's spec prompts 8-18, 20 and 21 in Docs/prompts

2026-09-29 13:02 · `bfe6f14`

## v0.28.0: Play-test rounds 2-3 (flashes on every barrel, plumes, blasts, fire rhythm, aircraft AI and sizes), prompts 11-14 (compact HUD, short names, shields, stuck vehicles, combat-value balance with stores on the field and AI by difficulty, the Base screen), the model muzzle audit

2026-09-29 09:30 · `0ce9bef`

Targeted tests and play-mode smoke runs pass; the full suite and the long sweeps wait for the testing phase.

### Prompt 11: a compact battle HUD, cards in line, short names, new shields

- A compact battle HUD, on by default (Settings > Compact battle HUD; off gives the full one): a smaller
  minimap with select-all and box-select on its corner (pinch to zoom), the objective and the clock in one
  strip at the top, Attack / Defend as one icon switch and Auto buy and Support as icon toggles (also in
  the pause menu), a card tray a third lower with the render, the CP and a short name (hold a card for
  its full name), the supply penalty as a small chip, a boss bar half as wide that opens on a tap (tap a
  part there to focus fire on it), small notices at the top that go after about 3 s one after another, the
  selected vehicles as one strip above the tray with Advance / Stop / Back, and the "your army fights on
  its own" hint only in the first three matches. In a fight the HUD covers about a quarter of the screen
  (the full HUD more than half). Every control is still a 44 pt target.
- Every vehicle, tower, structure, support and item has a short name for tight places; every card's name
  area is two lines high, so pictures, CP and levels line up in every row; cards in a row are one height.
- A tower branch's name no longer shows as a raw "support." key.
- Every shield redrawn with one shader: a hex-tile energy dome, bright at the rim and clear in the middle,
  red-orange for the enemy and blue for us, rippling where rounds hit, flickering as its generators are
  damaged and shattering when it falls; a lighter version on Low graphics. Its size and rules are
  unchanged.

### Prompt 12: stuck vehicles in bases

- A stuck detector in the internal build (`StuckWatch`, `-mb-stuck`), batch runs and a report with
  heatmaps and the ten worst spots in `Docs/stuck-report/`.
- Fixed at their causes: reachable goals and formation slots, no mutual queueing, head-on in the open,
  detours off walls, re-planning over newly closed ground, towers clearing their pad, room for the keep's
  guardian and elites.
- Fortresses: double sally ports and keep gate, clear yards and approaches, a three-cell route for the
  biggest hull everywhere (`check_access.py` checks every map); Swamp's causeways widened.
- A logged safety net for what is left. Episodes over 10 s in 76 battles: 1285 before, 265 after.

### Prompt 13: combat value, ammunition, modes and difficulty

- Every card measured by what it really does in a fight for its CP (Docs/COMBAT_VALUE.md), and the theoretical
  damage a second corrected (magazines, salvos, reloads). Prices and weapons tuned by it: tank hunters, artillery,
  helicopters, aircraft and anti-air in line with the ground units of their role.
- Damage a round by the real calibre (a 155 mm shell hits harder and comes less often), the same weapon with the same
  figures everywhere, ground SAMs a little slower with flare resistance.
- Aircraft carry bombs, missiles and rockets that run out and come back on the field: they finish their attack, fly a
  few seconds behind our line to a holding pattern, and come back; faster at the landing pad, over the HQ and (for
  helicopters) beside the new Ammunition carrier. Bombers carry fewer bombs, go in with two thirds of them and never bomb
  near our own units. The Sky gunship is no longer a card (the Gunship item still flies it).
- New: the Ammunition carrier (launchers beside it reload much faster, helicopters rearm twice as fast); the engineer
  repairs only. The landing pad's rank-7 branches: Hangar (one more aircraft up) and Fast service.
- Ammunition icons beside the health bar (low, empty, flying out, rearming, full), holding patterns on the minimap, the
  stores bar in the selection panel, and a setting for every unit or aircraft only.
- Unit details: every weapon's real name, calibre, rounds, magazine or stores and how they come back ("More"), and a
  Behaviour section, both worked out from the data; four notes corrected where they disagreed with it.
- Every mode rebalanced: Deathmatch scored in the CP destroyed (first to 480), King of the Hill to 170, a stronger
  Assault defender, a tougher Siege fortress, Defend and Endless waves scaled by the base and carrying siege breakers,
  Survival waves that keep coming, and help for the side far behind after 4 minutes (more income and a free drop).
- The AI by difficulty: Easy, Normal, Hard and the new Very Hard (it knows your deck and masses its attacks; rewards
  x1.8); decks of 8 to 12 chosen by roles and value; it buys ammunition carriers, hunts rearming aircraft and goes for
  landing pads. The campaign's Heroic and Iron tiers are now called Hard and Very hard.

### Prompt 14: the Base screen on the real camp, menus sized for a phone

- Menus are sized in the phone's own points, so they look the same size on every phone and a tablet shows
  more: a slimmer top bar and rail, smaller tabs and buttons (44 pt to tap), smaller type (13 pt text,
  18 pt titles; Large text 1.2 times) and cards in lists about a fifth smaller. The page's content now takes
  70-89 % of the screen. The battle HUD is unchanged.
- The Base screen is a picture of your camp on the chosen map from above, with red arrows where the enemy
  comes from and every slot where it really is: small, medium and large slots sized 1 / 1.4 / 2, utility
  slots as hexagons, empty ones saying what they take, closed ones the HQ level they open at. Pinch to zoom,
  drag to pan. "Show ranges" paints the whole base's cover, ground in amber and air in light blue; tap a
  tower for its range ring.
- Towers come from a tray with a tab for each size: drag one onto a slot, or tap it then a slot; only the
  slots it fits light up. Towers you do not have yet are dimmed with where they unlock.
- Tapping a tower shows its render, size and rank, its health, damage and range against the other towers
  of its size, its branch and gear, and Replace, Remove and Details. With nothing chosen, an overview.
- Along the bottom: what the base covers (light vehicles, tanks, air, rockets and missiles, stealth,
  repair and resupply; a gap in red), its strength (the same number the Defend and Endless waves grow
  with) and how many slots of each size are used.
- The HQ shows its level and what the next one adds; the map list has pictures; every change saves at
  once ("Saved").
- One base for every map: towers are placed by where they stand (gate, outer ring, inner ring, beside the
  HQ, rear), so the same base fits all 20 maps; a tower with no matching slot goes to the nearest one of
  its size, and a map where something did not fit gets a dot. A map can be set up on its own. Three base
  sets, switched on the Base screen or on the home screen. "Auto-arrange" lays the base out the way the
  enemy's AI does, with your towers. Your old base carries over: every map where it would have stood
  differently is kept exactly as it was.
- The outpost has its own tab.
- Every tower and module has its own icon.

<details><summary>77 commits</summary>

- `364688a` 2026-09-29 Troop transport: in from the map edge nearest the drop, over it, a climbing U-turn and home by the same edge, removed only past the edge (it used to vanish mid-map)
- `22dcbce` 2026-09-29 AA guns fire long streams from magazines (test feedback 2): ZU-23, flak 35, twin 30, quad flak, AHEAD, C-RAM
- `418d12c` 2026-09-29 Explosions a tenth bigger and tank rounds lingering: ExplosionEffect.Play takes a life stretch (fire, smoke, dust and embers; flash and sparks stay quick; the extra life scaled by tier like the extra particles) and a ring grow so a matched cruise missile or MOAB ring stays on its radius; BlastSizes.Bigger (x1.1) on every blast above the Small tier, ShellLife by tank class (+20/25/30 %), drones by type (FPV x1.2, Lancet x1.25, Shahed and strike drone x1.3); render rig mirrors it, Impacts sheet gains shell-landing and drone rows and later moments; tests
- `93fc1ff` 2026-09-29 Smaller fighters and helicopters next to the bombers and the transport: fighter -30 %, attack jet and three helicopters -15 %, A-10 and scout helicopter -10 % (model scale only)
- `5de961e` 2026-09-29 Detail page: the In action tab becomes a theatre, the preview fills the space under the tabs with the name, weapons and dock in a side column; small arrows beside the name, off the picture; the preview texture follows its box (shape and pixels, capped), framed as the old 4:3 crop
- `d2a8cd6` 2026-09-29 Smaller bombers, gunship (and the troop transport) by 15 %, strike drone 20 %, recon drone 10 %; flying bosses keep their size
- `2fd818c` 2026-09-29 Machine guns and helicopter guns on magazines (test feedback 2): 2.5-3.2 s streams, then a 1-1.5 s change
- `2c5f41b` 2026-09-29 Muzzle flashes on the barrel tip, the flame stream on its nozzle, vehicles over ground fires
- `9692607` 2026-09-29 Missile and rocket motor plumes, boost-then-cruise flight, sizes fitted to launchers, slower missiles
- `e986a30` 2026-09-29 Army: a Towers & modules tab beside the deck, tower and module cards (render, rank, size, upgrade mark) that open the detail page; the tower's detail page chooses its branch and fits its three gear slots in place
- `36ef496` 2026-09-29 Home setup: Boss Rush in the mode picker with its line (still on Operations); Deploy starts the picker's mode; a test taps it in
- `e7bbc98` 2026-09-29 PlaySmoke: -mbSmokePreview writes the detail page's preview texture at the end of the menu step and reports its size
- `f45d75a` 2026-09-29 Bosses stream too (test feedback 2): the mega gunship's guns, the hovercraft's CIWS, boss flak, the airship's 57 mm, the Bastion's 40 mm
- `d7726a8` 2026-09-29 Aircraft attack hold: jets hold their guns on the target, a VTOL fighter hovers, helicopters close to gun reach
- `cc9fbab` 2026-09-29 Motor plumes attached to the tail (stretched quads trail back from their particle, one frame of flight compensated), continuous cone with a glow body, smaller core; MissileFlightTests
- `536b55f` 2026-09-29 Flame streaks and tongues start where their flame shape shows; night muzzle light under the muzzle; late flash snapshots
- `b5e916d` 2026-09-29 DECISIONS 12E and the screenshots: the In action theatre (vehicle, tower, module), the Towers & modules tab, the detail pages with the arrows beside the name
- `50cfc30` 2026-09-29 DECISIONS 12A: muzzle flashes and the flame's origin, vehicles over ground fires, ground fires 20 % shorter
- `a212aff` 2026-09-29 Secondary magazine guns yield only to a gun at least as strong (test feedback 2)
- `d10c754` 2026-09-29 DECISIONS 12B: missile plumes, sizes fitted to launchers, slower missiles, boost-then-cruise flight
- `405278f` 2026-09-29 DECISIONS 12D: sustained fire for AA and guns, the before/after table, the rules changed, what is left for testing
- `6e396ba` 2026-09-29 Fire test counts the ground flame layer (ground fires moved there in 12A)
- `187baaa` 2026-09-29 Attack-hold pose and tests: the nose dips at the target, a hovering jet yaws without banking and rocks, it climbs away and dives back in
- `4c5cc0b` 2026-09-29 Each fire-support card brings its own round down: smoke shells are white canister rounds that burst open and pour white smoke (no glowing HE shell, no blast); barrage shells ride their tracer; mines come on rockets and the SEAD strike fires a missile (both with motor plumes through ProjectilePool.Launch); napalm canisters tumble; cluster dispensers split open into bomblets; the strike jet drops Mk 84s and the bombing raid is a heavy bomber with FAB-500s; the MOAB rolls out of a transport on a drogue chute; the EMP is a blue energy warhead with a flash and arcs; a repair drop is a parachuted crate; reinforcements are airlifted under canopies. All in StrikeEffects (AirDrops untouched); EffectShots.Supports sheet through a SupportRig; test
- `d0e2339` 2026-09-29 DECISIONS 12F: aircraft attack hold, helicopters at gun reach, measurements, the cannon damage change it needs
- `af44650` 2026-09-29 DECISIONS 12C: explosion size and life (factors, how the tenth combines, the matched ring stays on the radius and the fireball grows, drones by type, counts and lifetimes per tier), each fire-support card's round and arrival, sheets and tests
- `5fd7df5` 2026-09-29 Ground SAMs back to the 11C speeds (the extra 20 % cut was for aircraft missiles; SAM must still beat jets)
- `687bcdd` 2026-09-29 Missile flight test pins the ground SAMs' restored speeds
- `06ed244` 2026-09-29 Flash test pairs each flash with its own round; the Inferno's two flame projectors fire from their own nozzles
- `0fa681f` 2026-09-29 Design document: tower cards by size (render, stats, weapons, DPS, guide) with branch variants named, weapon cycles with magazines, Behaviour and Ammo blocks on every card
- `79fb42b` 2026-09-29 Flashes that read right: tank-gun cores ahead of the tip, small machine-gun and mortar flashes, a small ignition and backblast for launches; motor plumes 40 % longer and 20 % wider
- `e8f2e3a` 2026-09-29 Prompt 13 A: combat-value measurement (CombatValueMeasure), theoretical DPS over a whole load (FirePower), missile hit rates (MissileHitMeasure); ground SAMs 10 % slower with flare-resistant seekers (flareResist) so SAM still beats jets
- `79e3ecb` 2026-09-29 Prompt 13 B: damage a round by the real weapon's calibre (family, size, real name on every weapon), the same real weapon hitting the same on every carrier, the damage a second kept by cadence, magazine and salvo size; autocannon rounds get their own armour row (x0.38 on heavy); tank destroyer re-gunned to 125 mm, wheeled gun and gun pit to 120 mm; calibre tests
- `4d7640f` 2026-09-29 Prompt 11 A/B: the compact battle HUD, short names, cards in line
- `b5e6c74` 2026-09-29 Prompt 13 H.7: BaseStrength, the base strength number (HQ, towers and modules at their CP worth times their rank and equipment; 100 = the Normal enemy base at HQ level 3) for the Base screen and the Defend and Endless wave scale
- `e2acb2f` 2026-09-29 Prompt 13 A+B: decisions (13C A, B), the combat-value and theoretical DPS tables in Docs, real DPS in the measurement
- `5a148dc` 2026-09-29 Prompt 11: screenshots of the compact HUD (Conquest, boss, boss bar open, Siege, Defend, Survival, full HUD) and every screen again; the design document's UI section shows them
- `307c10a` 2026-09-29 Shields redrawn (prompt 11C): one hex-tile energy shader for every shield
- `abb0492` 2026-09-29 Tests follow the calibre cadences: the home rearm waits the mortar's own reload, the laser-warner tank holds its fire, suppression lasts past the shooter's own reload, the gatling has the least proc coefficient
- `6227cd6` 2026-09-29 Shield shots: the final sheet and in-game captures under Docs/art/shields
- `53523d4` 2026-09-29 Shields: vehicles stay covered while their item dome shatters; Low domes one tile level coarser
- `1590b0f` 2026-09-29 Prompt 14 A (work in progress): out-of-battle sizes in device points
- `f1a2fd4` 2026-09-29 Prompt 11: decisions (13A: the compact HUD, short names and their table, cards in line, raw keys, the shields), changelog, and the shields in the design document
- `999f943` 2026-09-29 Prompt 14 I: tower and structure icons of their own
- `373af99` 2026-09-29 Prompt 14 G (work in progress): one base plan for every map, by slot place; three plans; the migration from the version 2 loadout; AI loadouts can be limited to the player's towers
- `bf99e0d` 2026-09-29 Prompt 13 C, D, E: aircraft stores on the field (loads, one round at a time, slow while attacking or in danger, full at the holding pattern after 3 s safe), the holding pattern behind the nearest friendly line out of known AA reach, 2-3 s away, the landing pad, HQ and ammunition carrier as faster sites; aircraft finish their attack before leaving; bombers go in with two thirds of their bombs, pick groups and structures, never drop near friends, pause on ground just bombed; fewer bombs a run (bomber 9, stealth 2, Su-25 16 rockets, airstrike 6, air raid 10, cluster 30); roster review by combat value (tank hunters, artillery, helicopters, aircraft, anti-air); the sky gunship is no card
- `c4b32a0` 2026-09-29 Prompt 14 B.1-B.2: the Base screen's map pictures and approach arrows
- `122bd61` 2026-09-29 Base map pictures: normal-quality compression, forced reimport after a render
- `61cde0d` 2026-09-29 Prompt 13 F (sim and data): the ammunition carrier (4 CP support: launchers reload three times as fast round it, helicopters rearm twice as fast beside it; the AI parks it by its launchers and helicopters and buys one when it has three of them), the engineer repairs only (3 CP), the landing pad's rank-7 branches (hangar: one more aircraft up; fast service), the enemy base takes a landing pad and a destroyed fortress pad pays the attacker; empty launchers drive to a carrier or home when that is quicker than reloading in place
- `58080e1` 2026-09-29 Prompt 13 C-F: decisions (13C C, D, E, F), asset debt for the ammunition carrier and the landing pad branches
- `1f3c401` 2026-09-29 Prompt 14 B-H (work in progress): the Base screen rebuilt on the real camp picture, the Outpost tab, base cover and strength
- `4221022` 2026-09-29 Prompt 14: the base map framed on the camp, closed slots with their level, the cover strip in one piece, base sets on the home screen; Sprut allowed in Vietnamese texts
- `d4b824c` 2026-09-29 Prompt 14 J: every screen re-shot; Large text fits on the Base screen, home and top bar
- `d09a1ac` 2026-09-29 Prompt 14: decisions (13D: out-of-battle sizes in points, the Base screen on the camp picture, one plan for every map, the outpost tab, tower icons, camp pictures), changelog, and the Base screens in the design document
- `bf92411` 2026-09-29 Prompt 14 J: every screen re-shot after the prompt 13 C-F merge; the Base map's switches in short words
- `f3680f3` 2026-09-29 Prompt 14: decisions 13D, the map switches' short words
- `f2def11` 2026-09-29 Stuck vehicles in bases (prompt 12): stuck detector, batch runs, root-cause fixes, wide fortress gateways, map access check, safety net
- `2d1eedd` 2026-09-29 Muzzle audit from the model files; muzzles turned along their barrels, launch points on the real tube face
- `3888f21` 2026-09-29 Muzzle audit enforced (MuzzleAuditTests), the plume checked on the tail frame by frame, Docs/muzzle-audit.md
- `756152c` 2026-09-29 Muzzle audit: no regressions against the first run (95 wrong -> 54, 41 fixed, none broken)
- `52cdf9c` 2026-09-29 Prompt 12: the keep's elite reinforcements land where they have room; far formation rings may reach round a gate (a garrison spreads out instead of packing the keep's yard)
- `24e90b6` 2026-09-29 Prompt 13: the C-RAM shell test counts over enough shells (two guns; the C-RAM kept standing). Since B a 155 mm shell is one every 11 s, not 7, so one gun's four shells in 40 s at the C-RAM's 30 % share were all missed on this seed; the C-RAM itself is unchanged
- `f524ec9` 2026-09-29 PlumePlayCheck: the motor flame on the drawn tail in real Play-mode frames at 30 and 60 fps (worst 1.4 cm); MLRS rocket in the frame test
- `88b6e3d` 2026-09-29 Prompt 13 H + I: every mode balanced on a sample deck (Conquest's bleed and point CP, Deathmatch scored in CP to 480, King of the Hill to 170, a stronger Assault defender, a tougher Siege fortress, Defend's lines and waves, Survival's waves that keep coming and the overrun rule), help for the side behind, waves scaled by base strength and drawn against the base with siege breakers; the AI by difficulty: one buying profile per level, decks chosen by roles and value, Very Hard (knows the deck, masses its CP, x1.4 income, 30 % elites, rewards x1.8), hunting rearming aircraft and supply on Hard+, one ladder of difficulty names; migration tests
- `6fe4827` 2026-09-29 Twin and quad guns built as one part fire from each barrel; side guns flash along their drawn barrels (54 -> 34 wrong, 61 fixed, none broken)
- `382fca2` 2026-09-29 DECISIONS 13E: muzzle, launcher and missile-tail audit from the model files
- `175ef71` 2026-09-29 Prompt 13 H: after the merge, Conquest's point CP 0.15 and its enemy 18 % more income, the Hill's enemy 1.1, Assault's defender 32 CP and 1.3, 8 CP a sector, Survival's waves without a ceiling (elites to all of them by wave 24); decisions 13C H and I, the C-RAM test note
- `636137b` 2026-09-29 Prompt 12: the stuck report (before, after with and without the safety net: heatmaps, top-10 spots, tables), DECISIONS 13B, changelog; timing: formation walk only when a slot is out of plain line, slot untangling for groups up to 12, detours keep their side when both are closed, open-ground head-ons after 1 s
- `d8ac786` 2026-09-29 Prompt 13 G and F (UI): ammunition and behaviour lines generated from the data (UnitLines: real weapon name and calibre, type and targets, damage and salvo, magazine or stores and how they come back with the faster sites, range; movement and engagement, after firing, target priority, withdrawal, skills and auras, the landing pad's rates) on the detail screen (Behaviour in the guide tab, every figure behind More on the weapons tab, the module facts) and in the design document export (behavior, ammo, weapon name); a test that the hand-written notes agree with the data (four notes corrected: the IFV's 30 mm, the Ka-52's 23 mm, the Little Bird's 24 rockets, the TOS-1A's salvos of 9); the ammunition carrier's card picture and its In-action scene (two launchers reloading beside it)
- `79f9eb4` 2026-09-29 Model muzzles in Blender: 12 known mounts fixed at the source
- `a7dc559` 2026-09-29 Prompt 13 C.9: ammunition icons beside the health bar for aircraft, helicopters and launchers (low, empty and blinking, flying out, rearming with a ring that fills and turns dim or bright by the rate, a flash when full; enemies only empty and flying out), our holding patterns as faint rings on the minimap, the selection panel's stores bar, a setting for every unit or aircraft only, the icon table in the guide tab and a tip in c3m03 (the first mission with our own aircraft; c3m03's ammunition carrier unlock now in the campaign source too)
- `46734e6` 2026-09-29 Model muzzles in Blender: 11 more known mounts fixed at the source
- `f39bc8b` 2026-09-29 Prompt 13: decisions (13C C.9, G, F interface; Z left for the testing phase), changelog, the final combat-value tables (after F) and the mode measurements under Docs/balance
- `1920972` 2026-09-29 Design document: combat value per vehicle (9b), stores and rearming (12b), mode results and AI difficulty (2b), the testing list for prompts 12-13
- `74dd111` 2026-09-29 Cards of the re-exported models, the muzzle audit (284 mounts, 12 wrong, _hd 0) and DECISIONS 13F
- `a58ad0f` 2026-09-29 The ammo carrier drives the armed truck too (the merge kept the old prop model)
- `5df60a5` 2026-09-29 Design review PDF after prompts 11-14 and the model audit (141 pages): behaviour and ammo on every card, tower cards, combat value, stores, modes and difficulty, every new screen

</details>

## v0.27.0: Story campaign (9 chapters, 108 missions), Siege and Defend upgrades, prompt 8 content and elites, boss parts on every boss, Field Command 2.0 UI, LOD, and the play-test fixes

2026-09-29 00:48 · `2a3328b`

Phases 1-10 of the 2026-09 programme and the owner's play-test fixes (DECISIONS 11A-11D).
Targeted tests and a play-mode smoke run (menu, Conquest, Siege, Defend, Boss Rush, a boss
mission, a multi-stage mission) pass with 0 errors; the full suite and the long balance sweeps
wait for the testing phase.

### Prompt 8: new content, elites and equipment

### New vehicles and mechanisms
- **Armoured bulldozer** (Heavy, 7 CP, 3,250 health, heavy armour, 5 m/s, a roof machine gun): its
  blade rams structures for three times the damage within 4.5 m, it ploughs dragon's teeth and
  hedgehogs flat as it drives into them, and its belly plate halves mine damage. The commander sends
  it at the enemy base's obstacles and towers ahead of the line; an enemy that sees two or more
  bulldozers buys more tank killers. Unlocked in act II (mission 7), in General Varga's deck.
- **SP howitzer**: shoot-and-scoot (after three rounds it drives 15-20 m to a new spot still in
  reach, so counter-battery fire lands on an empty field) and near-zero scatter on marked targets
  (radar, UAV scan, laser designator).

### Bosses (all in Boss Rush, with guides, radio lines and parts on the health bar)
- **Rail supergun** (Kessler): a gun on its rail at the map's edge, one shell every 20 s anywhere on
  the map with a 3 s warning ring; its targeting station and guard emplacements around it; kill the
  station and its shells scatter.
- **Earth Worm** (Varga): dives underground (no one can aim at it), surfaces under the player's
  biggest group after a 2 s crack warning, stuns ground vehicles within 15 m, and takes half as much
  damage again for a few seconds after.
- **Command airship** (Quạ Đen): the general part mechanism. Four engines, two drone hangars and a
  radar, each with its own health; the hull takes damage only once two engines are down; a hangar
  down stops its drones, the radar down makes its flak miss. Only anti-air and fighters reach it.
- **Landing hovercraft**: runs its route along the coast and lands three or four enemy vehicles at
  each landing point; stop it before it has landed them all.
- **Supreme Commander** (Hùng, after the betrayal): a super-heavy command vehicle that barely
  fights, but every enemy within 40 m hits 20 % harder and fires 20 % faster; elite escorts.

### Elites
- Every elite on one footing: 1.6 times its base card's health, 1.25 times its damage, one or two
  elite skills; measured power (duel damage a second times time alive) 1.8 to 2.2 times the base
  card's. The EW carrier keeps its EMP only; the heavy tank its overdrive; the battle tank's shield is
  30 %.
- New elites: FPV carrier (barrage), attack jet (long flares), long-range SAM (overdrive), SP howitzer
  (barrage), on their base card's model in dark armour and gold trim.
- A budget instead of a chance: elites cost the enemy 1.6 times the base card; a share of its
  spending may go on them (Easy 5 %, Normal 10 %, Hard 15 %, Heroic 20 %, Iron 25 %), with at most
  1/2/3/4/5 out at once; generals favour their own kind (Varga tanks, Orlov artillery, Sen drones,
  Quạ Đen aircraft). Waves and reinforcements follow the same budget. The campaign's enemy pace
  takes the elites' edge into account.
- A kill refunds at the elite price; each elite destroyed pays 10 coins after the battle (the first
  four) and has a 6 % chance of a blueprint of its base card.
- A gold ring on the minimap, a radio line when the first elite of a wave turns up, and each base
  card's Guide tab shows its elite version.

### Equipment
- The fit matrix comes from the data: which branch each class belongs to, what every card has and
  what every piece, line, module and brand needs. Crates drop only pieces that fit a branch; the
  equipment screen only takes a piece onto a branch it fits; the branch pages list their classes.
- New base types: flanking rounds, airburst rounds (replacing the hyper-velocity charge), spare
  magazine, radar-absorbent coating, laser warning, reverse gearbox. The turbocharger and turret
  drive are now one drivetrain; the mine rollers are underbelly armour (mines and blasts); the signal
  relay adds 10 % vision.
- New unique lines: Vengeance, Suppressive Fire, Rearguard. New brands: Phoenix Recovery, Wolfpack
  Tactics, Bulwark Engineering (towers only, counted across the base).
- Twin Feed: an extra round only for bursts of three or more; one- and two-round weapons hit 15 %
  (Epic) / 20 % (Legendary) harder instead.
- A proc coefficient by weapon (its time between hits over 1.5 s, 0.15 to 2.5) on every on-hit line;
  Shredder needs more hits a stack on fast guns.
- Cluster warheads burst on the first two rounds of a salvo only.
- Fixed-effect modules scale with the card's price (CP / 7, between 0.4 and 1.3); the fuel blast is
  capped at 1,500.
- Kill refunds capped at 45 % of the victim's price, own-loss refunds at 15 %.
- Trade-off pieces drop from Rare up, their drawback growing with their rarity.
- Last stands (Unbreakable, Aegis, Phoenix) cannot chain on one killing blow.
- Save version 3: retired, merged and no-longer-fitting pieces are converted in place (same slot,
  rarity and level) or taken off.
- Retuned from the lab's measurements (Legendary): Twin Feed's salvo share 12 % to 20 %, Incendiary
  14 % to 25 %, Opening Salvo 80 % to 50 %, Momentum 4 % to 7 % a stack, Cluster Warhead 6 to 8
  bomblets; a ricochet carries the damage share of the hits that earned it (fast guns bounce seldom
  but hard). The armoured bulldozer has the turtle tank's 3,250 health, not the brief's 3,500.

### Documents
- EQUIPMENT_FIT.md and EQUIPMENT_VALUES.md (generated by `EquipmentDocsExport`), ASSET_DEBT.md,
  ROSTER_BALANCE.md (the prompt 8 DPS per CP table), DECISIONS.md section 8.

### Prompt 9: boss parts

- Every boss is a body and parts (its guns, launchers, engines, shield and EMP emitters, a locomotive,
  a drill, a ramp, an antenna...), each with its own health and a small bar in a row of icons under the
  boss bar. A broken part's weapon or skill stops for the battle, its mechanism with it (the
  supergun's shot, the Earth Worm's dives, the hovercraft's landings, the Supreme Commander's aura),
  and the body loses 30 % of the part's health. Only direct hits damage parts. Body health is lower to
  keep the fights about as long.
- Tap a part on the boss, or its icon, and every unit in reach targets it until it breaks (tap again to
  cancel); it is outlined in gold.
- The Iron Train's and the Bastion's self-repair now patches one broken part (its heaviest gun) back
  to half health, once.
- The Bastion's four autocannon turrets each cover their own quarter.
- Boss Rush pays 2 CP for each part broken.
- Fire and smoke at the breaks: hurt parts smoke and spark, broken ones burn until the end of the
  battle, the body burns under two thirds and a third of its health, flying bosses trail smoke, every
  fire flares when the boss dies and the wreck burns on. At most 8 fire points a boss (5 on Low).
- Radio lines when a main gun, a shield generator, a drone bay or a locomotive breaks; each boss's
  Guide tab lists its parts and what breaking each does.

### Prompt 10: Field Command 2.0 (the interface)

- New look everywhere, on one theme of tokens (colours, Barlow fonts, type sizes, spacing, touch
  size): flat graphite panels, square corners, 1 px borders, one amber main button a screen.
- Navigation: a top bar (title, rank and XP, coins, settings) and a rail of five: Home, Campaign,
  Operations, Army, Shop. Army has Deck, Equipment and Base.
- Home: the battle behind, the campaign card, today's challenges, the deck strip with 3D renders,
  and the match setup as four dropdowns (mode with its description, battlefield with its picture,
  difficulty, weather) beside DEPLOY.
- Campaign: chapters in three acts with pictures, progress, stars and bosses; each mission's
  briefing, stars, tiers, recommended power and rewards.
- Army: deck overview with role cover, filter chips and sort, cards with renders; equipment with gear
  cards and comparisons; the base screen at touch size.
- Detail pages for every card with the same five tabs, class averages and the gains told apart, and
  now for towers and base modules as well (from the base screen's info button).
- Shop with crate renders and coin pack pictures; "Ngụy trang" instead of "Skin".
- Results: the mission's or mode's name, the score by side, hints after a defeat with a button to the
  deck, CONTINUE or PLAY AGAIN, and doubling the coins as a Claim button.
- Battle HUD: full-name Attack / Defend, on/off switches for Auto buy and Support, cards with renders,
  names, CP, what is missing and a cooldown clock, the CP box with income and the supply penalty in
  words, the boss bar with health in numbers, phases and parts, one style for notices and radio.
- Settings: Text size (Normal / Large).
- Vietnamese: one name per battlefield (Đồng Tro, Cảng Thép, Đô Thành...), "xu" for coins, no
  English words left except the listed names.

<details><summary>72 commits</summary>

- `405a130` 2026-09-28 Siege sim: fortress data, gates, collapsing walls, super-gun, line in, swarm waves
- `fc7cef5` 2026-09-28 Campaign mission types: outpost, relief, evacuation, duel; boss health and flight; free strikes and income from stage events; reversed maps
- `bd7fa46` 2026-09-28 Vehicle detail levels: simplified one-material LOD1 per moving part, impostor atlas, level choice by screen size
- `034ff7f` 2026-09-28 Impostor cards lit with their own light loop (instanced draws get no per-renderer sun), alpha to coverage; LodShots renders cards through a camera of their own
- `09b279f` 2026-09-28 Siege maps: a fortress holding 45 % of the battlefield, towers on sized hardpoints
- `e3e2aab` 2026-09-28 Campaign structure: chapters, side missions, generals, HQ levels by chapter, rewards, save migration hooks
- `c46d79d` 2026-09-28 Campaign generator, part 1: the kit, the story (people, generals, chapters, boss files, timeline) and act I's 36 missions
- `c53a4f5` 2026-09-28 Prompt 8 groundwork: branch from data, elite price, boss part and burrow data, a damage log and reveal-all for the equipment lab, mine blasts count as mines
- `eba149f` 2026-09-28 Debug flags for big battles: -mb-crowd (two armies of fifty topped up in view), -mb-zoom=N; -mb-perf reports the detail levels and impostor draws
- `3cb56ba` 2026-09-28 Checkpoint replay in its own class, tested on a real mission session (both commanders, the player's orders and switches)
- `7d1b413` 2026-09-28 Impostor cards drawn only in the battle camera; decisions 5L (LOD and impostors) with the measurements
- `967b4fb` 2026-09-28 WIP (paused): Field Command 2.0 tokens and component files in progress, not yet verified
- `3d562a0` 2026-09-28 Siege and Defend sessions and HUD: gate goals, fortress loadouts, super-gun timer, wave preview
- `959b9cd` 2026-09-28 Campaign generator, part 2: act II (chapters 4-6, 36 missions)
- `ed93df7` 2026-09-28 Story campaign data: 108 missions (90 main, 18 side) in 9 chapters, generals, chapters, 869 texts
- `9fba490` 2026-09-28 Story systems: radio chatter, story camera pans, briefing and chapter cards, the Dossier, portraits, campaign page by chapter
- `bc4dcf4` 2026-09-28 Equipment (prompt 8 B, C, D, I): fit matrix from the data, new base types, lines and brands, proc coefficient, Twin Feed, cluster, module scaling, refund caps, trade-offs, last stands, save upgrade
- `5ce02e2` 2026-09-28 Siege and Defend: tests, first balance pass (Siege 3/5, Defend 4/5 on Normal)
- `3f08411` 2026-09-28 Leave the music folder's editor-made meta files out (not this branch's)
- `ca112f5` 2026-09-28 Fortress views: shield dome, rail line and train, runway and transport, searchlights, collapsing walls, gate doors
- `f2ccd2d` 2026-09-28 Campaign tuning rounds 1-3; duel HQs are demolition targets; the AI saves CP for a held outpost
- `75b902e` 2026-09-28 Prompt 8 A+E: armoured bulldozer, SP gun shoot-and-scoot, boss parts and five bosses
- `88a4193` 2026-09-28 Siege device checks (debug flags for the fortress set pieces); a smaller transport on the runway
- `3c8e680` 2026-09-28 Campaign tuning round 4 after the first five-seed run (80 of 87 measured missions at 5/5)
- `c1ead52` 2026-09-28 Duels are sieges of a base: the siege mix, the brigade's heavy battery, a 0.3 HQ, 30 minutes; the plaza relief at 2.2x
- `f45288d` 2026-09-28 Duels: the general's strength is his base, not his field army
- `f48561c` 2026-09-28 Campaign: radio panel clears the boss bar; briefing aside separator
- `48ed040` 2026-09-28 Prompt 8 H: elites on one footing, four new elites, an elite budget instead of a chance
- `a349b77` 2026-09-28 Campaign: DECISIONS section 4, the economy chart; test fixes
- `056f80f` 2026-09-28 Siege and Defend: stores in the walls' yard, gates on odd metres, breach-aware firing spots, balance, decisions 5S
- `aec7e88` 2026-09-28 Prompt 8 I/J: lab retune, risk lab, generated equipment docs, decisions
- `babc2a1` 2026-09-28 Field Command 2.0 foundation: token theme, Barlow fonts and licences, the UI kit, its preview screen and the UI checks
- `ea1c138` 2026-09-28 Card pictures from the 3D models: the render tool, 92 renders for 122 cards and their freshness test
- `48fccfa` 2026-09-28 UI screenshot tool and the kit preview at four screen shapes; stricter layout checks
- `c81b70d` 2026-09-28 Design document export: chapters, characters, timeline, generals, bases and tower cards, Operations, boss phases and parts, mission chapters and stages
- `ef44e5f` 2026-09-28 Hud.uss reads the accent from the tokens; decisions 10: card renders, screenshots, the checks and what the rebuild takes over
- `cae097f` 2026-09-28 Design document: the programme's sections (story campaign, multi-stage missions, Operations, bases and towers, Siege and Defend, tests still to run); stale texts updated
- `869948a` 2026-09-28 Card renders for the bulldozer, the five new bosses and the new elites
- `77f1328` 2026-09-28 Design document: card renders on the vehicle cards, generals' styles in Vietnamese
- `88263f7` 2026-09-28 Prompt 9 A+B: parts on every boss, on the general part rules
- `06e0876` 2026-09-28 Prompt 9 C+D: fire and smoke at a boss's breaks, the part row, the part order from a tap
- `8a9118a` 2026-09-28 Prompt 9 docs: DECISIONS section 9 (rules, every boss's parts, effects, interface, tests), CHANGELOG, ASSET_DEBT
- `cf82a0a` 2026-09-28 Field Command 2.0 screens on the kit: navigation, home, campaign, operations, army, vehicle detail, shop, settings
- `0934d78` 2026-09-28 LOD test: the far level may drop radio whips (under a pixel far away), so it may be up to a fifth lower, never taller
- `a98479c` 2026-09-28 Design document: prompt 9's part rules and break effects, a parts table under every boss (share of the body, what breaking it does, lock, self-repair, tip)
- `fe0e305` 2026-09-28 E6 base screen on the tokens: Screens.uss off the theme so it can restyle old classes
- `c5cdbcd` 2026-09-28 E7 match setup: the home's mode and map pickers as screens of their own in the checks and shots
- `ab1a136` 2026-09-28 The editor compiles without the UI Toolkit test framework: the screenshot tool and the UI checks sit behind MB_UI_TEST_FRAMEWORK, set when the package is present
- `3cc8e9e` 2026-09-28 Design review PDF for phases 1-9 (97 pages): the programme's chapters, boss parts, a phase 10 preview from the rebuilt screens
- `2e1fa0e` 2026-09-28 E10 result, pause and stage choice on the kit
- `05650c8` 2026-09-28 Play-mode smoke run for batch mode: the menu and a list of matches (Conquest, Siege, Defend, Boss Rush, a boss mission, a multi-stage mission), every error and exception reported
- `816bb67` 2026-09-28 Boss Rush easy to find: the weekly fortress and the boss rush head the Operations tab's right column; the card says ten bosses
- `4eb15e7` 2026-09-28 G battle HUD on the kit
- `fd77d45` 2026-09-29 Menu load and sound (test feedback 11D): the first open is built behind the curtain, one music player for the session, the lobby battle silent
- `0d82485` 2026-09-29 Towers and base structures get the vehicles' detail page (owner request)
- `b480b26` 2026-09-29 Rounds leave from the barrel as it is drawn that frame, and tracer streaks trail their round
- `cc8a967` 2026-09-29 H names: one Vietnamese name per map, no English left in the Vietnamese texts
- `fb6db92` 2026-09-29 In action clips show each vehicle's and support's special ability (test feedback 11D)
- `7c15ad5` 2026-09-29 Lobbed rounds leave down their barrel and bend onto where they land; missiles 10-20 % and drones twice as big
- `047fa03` 2026-09-29 Prompt 10 screens: decisions (10b), changelog, every screen's screenshots at the four shapes
- `8826b39` 2026-09-29 Decisions 11B: muzzles, projectile flight and projectile sizes (causes, measurements, fixes, sizes, tools)
- `2c2bd67` 2026-09-29 Play-test fixes for effects: bigger tank-round, bomb and cruise-missile blasts that stay sharp, a reworked flame stream, a held laser beam
- `477f9cf` 2026-09-29 Test feedback 11C: main guns fight the ground, missiles fly a third slower, magazine guns fire in streams
- `8e7d43c` 2026-09-29 Debris rotation renormalised each step: the drifting quaternion made TRS assert (47 errors in 40 s of Conquest)
- `7cafdaf` 2026-09-29 Effects tuning from the contact sheets: a heavier Iron Beam glow, tank-round fireballs that burn a fifth of a second, hotter and bigger flame balls, the impact sheet's own moments
- `07b47fa` 2026-09-29 In action clips checked with graphics: the jammer's view widened and its ring every second, the breacher's teeth on a slower cycle; RangeSceneTests; DECISIONS 11D
- `2ecd169` 2026-09-29 DECISIONS 11C: weapon targets, missile speeds, magazines and the measured DPS before and after
- `8865e15` 2026-09-29 DECISIONS 11A: final particle counts and beam widths
- `1559803` 2026-09-29 Combat comments: the leading magazine gun is a ground vehicle's main gun (an aeroplane's cannon takes turns)
- `290645e` 2026-09-29 DECISIONS 11D: the debris drift is fixed on lead/integration
- `1a92d6a` 2026-09-29 HUD screenshot demo: fall back to the starter supports when another test left the deck without any
- `c744f72` 2026-09-29 Design review PDF after phase 10 and the play-test fixes (100 pages): the new screens and HUD, names from the data, magazines and round speeds, section 16b on the fixes, the testing list

</details>

## v0.26.0: Bases as a loadout, roster cleanup, towers with sized slots and gear, multi-stage missions, Operations, new bosses' models and eight new maps

2026-09-28 18:30 · `14b174b`

<details><summary>33 commits</summary>

- `95b0c64` 2026-09-28 Sized hardpoints replace fortification points; tower cards and branches
- `ea76b3c` 2026-09-28 Base layout rules for the base screen: slot mapping, fitting, gaps, saving
- `28477b9` 2026-09-28 Tower roster: new towers, merges, branches, utility modules, counters
- `9bd8912` 2026-09-28 Tower equipment: Weapon, Structure and Systems slots per tower type, tower lines, fit, crates
- `92cbfec` 2026-09-28 Tests for tower equipment: slots, fit, shared loadouts, caps, the five tower lines, crates, saves
- `6ac3d76` 2026-09-28 Base loadout screen: camp diagram, drag and tap placement, branches, gear tab
- `dde1100` 2026-09-28 Decisions for tower equipment (section 3D)
- `18704f7` 2026-09-28 Map builder: plan the keep's flak branch on the old Flakturm's ground
- `cb518b2` 2026-09-28 AI weighs defences by size and by what they can hit; drones on emplacements
- `8b9d260` 2026-09-28 Base screen: device fixes at 16:9 and 18.5:9
- `cfc0887` 2026-09-28 Base screen: utility slots come alive once utility modules exist
- `7dbd145` 2026-09-28 Base screen: compact outpost row, one placed count, decisions 3F
- `1fc9178` 2026-09-28 Phase 8 models: armoured combat bulldozer (D9R lineage)
- `67a6905` 2026-09-28 Multi-stage missions: stages, events, choices, checkpoints by replay, an allied commander and its betrayal, the play area
- `de4932f` 2026-09-28 Phase 8: rail supergun, its rail tractors and targeting station
- `7a6d70d` 2026-09-28 Phase 8: earth borer boss
- `74bfd7a` 2026-09-28 Phase 8: command airship boss
- `4cb20d0` 2026-09-28 Phase 8: landing hovercraft boss
- `2d10c26` 2026-09-28 Landing hovercraft: rub rail, crew doors, bollards
- `366bca2` 2026-09-28 Phase 8: supreme command boss
- `6713e9e` 2026-09-28 Phase 8: generic boss wreck pieces
- `86d69e9` 2026-09-28 Phase 8: Unity import metas for the new models; clean rebuild
- `2df12de` 2026-09-28 mb_phase8: drop unused imports, measured sizes in the docstrings
- `6389ca3` 2026-09-28 Tick budget: path finding spread over steps, commanders on different steps, enemy ceiling 48 in the big modes; the ally's own base; the measured default base
- `ccc87fb` 2026-09-28 Rail supergun: bed runs on under its two coupled tractors
- `6b8e340` 2026-09-28 Map builder: groundwork for battlefields laid out in world metres
- `e371f13` 2026-09-28 Eight new battlefields: Landing Beach, Hydro Dam, Capital, Silver Bug Launch Site, Salt Flats, Border Bridge, Swamp, Coral Isles
- `9f48725` 2026-09-28 Register the eight new battlefields in the game
- `c06436a` 2026-09-28 Map tests: routes from every drop zone on all twenty battlefields
- `3782c3e` 2026-09-28 Multi-phase bosses: the bar stops at each phase's mark, the boss transforms untouchable, then fights on stronger
- `8194005` 2026-09-28 Decisions 4M: the eight new battlefields
- `1052669` 2026-09-28 Operations mode (prompt 6): four tiers with Legend, scores and records, 18 weekly mutators on a 26-week rotation, one weekly reward ledger
- `85d56f1` 2026-09-28 The camera keeps to the play area and follows it as it opens; decisions for Operations (6) and the growing battlefield

</details>

## v0.25.0: Merge bases as a loadout and the roster cleanup (prompts 1-2)

2026-09-28 14:47 · `d119abe`

<details><summary>2 commits</summary>

- `1d8dcda` 2026-09-28 Bases as a loadout: HQ, fortification points, hardpoints, outposts
- `a60811a` 2026-09-28 Roster cleanup: merges, new vehicles and supports, balance

</details>

## v0.24.0: Round 6 (weapon turns, barrels, round models, impacts, railgun, bosses, Ka-52/Su-25, economy and rank discount, guide tab, music, minimap, loading, PDF)

2026-09-28 11:31 · `250a465`

<details><summary>5 commits</summary>

- `39529e4` 2026-09-28 Round 6, part 1: weapons take clear turns, rounds leave from the real barrels, slower guns, AA bursts, slower missiles
- `2f323ab` 2026-09-28 Round 6, part 2: own round models, impact kinds, railgun charge, boss deaths, new bosses, Ka-52 and Su-25, economy, music, minimap, loading
- `d9871fa` 2026-09-28 Metas for the new boss models and the music director
- `2ceeaef` 2026-09-28 Round 6, part 3: Guide tab for every unit, fire-support clips, touch fix after the deferred build
- `f8f54df` 2026-09-28 Round 6: review PDF rebuilt, progress notes, m13 retune, detail debug flag

</details>

## v0.23.0: Round 5 (armament, new vehicles, campaign depth, Defend base, Endless, Field Command menus, equipment rework, traffic, 300 m maps, HD models, design-review PDF)

2026-09-28 05:45 · `44c5380`

<details><summary>25 commits</summary>

- `0bb5759` 2026-09-27 Playtest fixes: deck slots keep their places, one currency, aircraft fly in and keep their wings, crash damage, strike safety, boss stays visible, weather eases in, economy and counter-buying
- `ef3508b` 2026-09-27 Menu colours by meaning and finished buttons
- `270b07d` 2026-09-27 Real armament: side-firing gunship, stealth, fighters that hunt aircraft, air-to-air missiles, flares, corrected ranges and sizes
- `1d785e1` 2026-09-28 New vehicles (sim, data, icons, notes), bigger bosses and a flying-saucer boss, an In action tab, flight effects
- `742e968` 2026-09-28 Campaign enemy keeps pace with the arsenal and calls reinforcements; tracked models for turtle tank, BMPT, sapper
- `8fcdbcd` 2026-09-28 New mission goals (hunt, recon, protect, shoot down), six new missions, Defend as a real base, Endless mode, eight new models
- `dd9f3c0` 2026-09-28 Remove the 40 mm grenade launchers from the jeep, engineer, jammer and mine layer models
- `3fe8b1b` 2026-09-28 Traffic rules: lane map, no-park doorways, yielding and routes round parked hulls
- `5694a7a` 2026-09-28 Gear engine in the sim: stat lines, weapon copies, status effects and trait hooks
- `0a2d892` 2026-09-28 Menus restyled "Field Command" (flat, tactical) after the user found the glossy menu dated
- `3821070` 2026-09-28 Flat battle HUD shapes, square rarity frames, settings values off amber
- `46a9f9e` 2026-09-28 48 equipment pictures for the gear rework (base types and special modules)
- `ac176da` 2026-09-28 Equipment affix model: base types, sub-stats, traits, brands, Optics slot and save migration
- `9b65351` 2026-09-28 Proc words over vehicles in battle and the gear style block
- `630ef83` 2026-09-28 Checks for every remaining trait, module and set; thermal sight share; trait choice API
- `b22e5c3` 2026-09-28 Look for a missing gear picture once; expose blocks left and burning for views
- `0ef45ef` 2026-09-28 Progress: equipment rework merged, loot boxes kept, what is left to do
- `1fa84e1` 2026-09-28 WIP: Gate token, wider fortress, anchored defences, traffic scenario tests
- `f00c1fe` 2026-09-28 Traffic: a group bound for one place and units holding in the open are not sent away
- `b1d5970` 2026-09-28 Battlefields half as big again (300 m), denser, the country going on past a marked boundary, bigger houses, sharper High shadows
- `fa38ecc` 2026-09-28 m13 rebalanced for the bigger fortress map: siege buying mix, no extra waves, more time
- `e700281` 2026-09-28 Design-review document generator: game data export test and HTML/PDF builder
- `1f900f2` 2026-09-28 Progress: traffic, bigger battlefields and the review document
- `42834ff` 2026-09-28 High-detail models for High graphics: the twelve most-seen vehicles
- `31454ab` 2026-09-28 Design-review PDF: readable equipment lines, image cache, current edition in Docs

</details>

## v0.22.0: Mobile menu layout, vehicle detail page, equipment pictures

2026-09-27 22:10 · `7ac15a6`

<details><summary>1 commits</summary>

- `69e180c` 2026-09-27 Mobile menu layout, vehicle detail page, equipment pictures with rarity frames

</details>

## v0.21.0: Arsenal (card ranks, equipment 6+1 slots, crates with odds and pity, gems), device-check fixes

2026-09-27 21:17 · `829a296`

<details><summary>3 commits</summary>

- `a30df89` 2026-09-27 Arsenal: card ranks 1-10 (coins and blueprints, +5% health and damage a rank, +5% strike damage), equipment per branch (six slots and a special module, white to gold, levels, caps, always-successful merging with refunds), crates (battle, silver, gold, legendary; odds and pity shown before buying or opening), gems with a test-build store, a battle crate for each of the first five wins a day, a silver one for a mission's first clear, three ad crates a day; upgrades applied to the player's vehicles and strikes in the simulation; tests never write the real profile
- `5ca94bd` 2026-09-27 Docs: progress for the siege playtest round and the arsenal; release checklist gains the gem store switch
- `98e4868` 2026-09-27 Device check fixes: compact brand strip and dock labels on the narrow main page, arsenal dock buttons sized to fit, crates tab without the empty detail pane, parachute canopy single-sided and about 1.3 vehicle lengths across, placeholder ads in the menu (arsenal ad crates)

</details>

## v0.20.0: Menu taps and scene curtain, siege AI and fortress buildings, in-place reload with ammo gauge, stuck fix, AI waves and role-mix buying, air drops, falling shells, jet trails, audio cleanup, smaller aircraft

2026-09-27 20:51 · `4080802`

<details><summary>7 commits</summary>

- `89ce098` 2026-09-27 Menu taps that land (fire on release within a finger's slop, whoever holds the pointer; no more taps lost to scroll views), a fixed card-detail pane so deck cards stop jumping under the finger, and a black curtain with a loading screen between scenes (fade out with the sound, build behind black, fade in after warm-up); editor clicks count without Game view focus
- `f49dba3` 2026-09-27 Artillery and siege guns shell known defences from outside their reach (firing-spot solver, defences before the mission structure); fixed defences stay known once seen, siege attackers start with the fortress plans; empty magazines reload in place standing still (3x at home or a supply vehicle) with an overhead ammo gauge and reload bar; smaller aircraft (helicopters ~1.5x a tank), tougher helicopters, fortress AA toned down; bigger fortress gun impacts without screen flash
- `e4e4213` 2026-09-27 Stuck check measures progress towards the waypoint (a hull edging back and forth against a corner passed it for ever: 261 shakes a battle, now about 30); arrival contagion near a crowded goal; an unreachable guard post moves to where the hull can stand
- `f28ea93` 2026-09-27 Reinforcements are flown in: a transport passes over and the vehicle comes down under a parachute onto its landing point (landing and elite roll decided when bought; delivery 3.5 s); aircraft fly in from the map's edge. Audio: the interface beep for enemy strikes is gone, barrages and heavy shells whistle down where they land instead; points taken or lost come over the radio instead of puzzle chimes; the fortress siren fades with distance
- `574fcc8` 2026-09-27 Fire support is seen coming: every barrage round is aimed a moment ahead and falls out of the sky from its guns' side onto the spot it hits; smoke shells come down before the cloud. Jets trail vapour and a hot exhaust, with wingtip vortices in hard turns; strike jets' trails sized to the aircraft
- `49682be` 2026-09-27 Siege: 14 fortress buildings per map (barracks, stores, offices, workshops) placed clear of the attack lanes, each paying the attacker 2-6 CP when knocked down and coins at the end; the attacking AI shoots them up when nothing military is in reach; a bigger purse for the attacker (34 CP, 1.8 income, supply 40, 20 CP a stage) and a leaner defender
- `8399ac5` 2026-09-27 AI in waves: reinforcements gather at a staging point and go forward in threes instead of one by one; the line stops at the edge of known defences' reach until most of it has gathered, then goes in together; remembered defences are not contact (seen-now vs known masks); purchases follow a role mix per stance (a siege attacker brings more artillery), then counters

</details>

## v0.19.0: Editor Debug Flags window

2026-09-27 19:31 · `8eeba49`

<details><summary>1 commits</summary>

- `ac358ba` 2026-09-27 Editor: Machine Brigade > Debug Flags window, so the development switches (start straight into a mode, map or weather, test views, switch-offs) work in Play mode without a command line

</details>

## v0.18.0: Launch points, directional armour, smarter fire, night lighting, Defend mode, challenges, track marks and felled trees, screen flash, AI review, catch-up, bigger bombing blasts

2026-09-27 19:23 · `30199a8`

<details><summary>7 commits</summary>

- `38acb95` 2026-09-27 Armour by facing (side 1.25x, rear 1.6x), smarter fire (no overkill for heavy weapons, value and threat targeting, artillery bracketing), screen flash on huge blasts, heavy guns for the Doomsday Train, names for the new defences and the elite Grad
- `e646ca6` 2026-09-27 Defend mode: hold three dug-in sectors against the enemy's Breakthrough (the Assault rules with the sides swapped)
- `b39c517` 2026-09-27 Challenges: Heroic and Iron tiers for every mission, each mission's own third star (no strikes, no aircraft, kills), and a weekly fortress whose broken rings stay broken all week
- `e51ed3d` 2026-09-27 Hulls knock down trees, bushes, hedges and fences (they topple the way the vehicle drove, then sink away); track marks behind every ground vehicle, fading over half a minute
- `ec02f73` 2026-09-27 Night lighting: blasts, gun flashes and fires light the ground, illumination flares drift down over the fighting
- `1febeb1` 2026-09-27 m16 player income 1.55 after the Doomsday Train's heavy guns; campaign 17/17 at 5/5
- `f59ecc9` 2026-09-27 AI review: artillery backs off along the map's edge (EscapeRoute) and only from ground threats, crowds step aside to a random open spot, nobody targets invulnerable bastions, artillery sees 30 m; catch-up for the losing side in quick modes (underdog reinforcements up to +50%, kill bounty by the odds); bigger bombing blasts drawn to size

</details>

## v0.17.0: Rounds leave from the real launchers, twin guns fire together

2026-09-27 18:29 · `fdf975d`

<details><summary>2 commits</summary>

- `84f67b2` 2026-09-27 Rounds leave from the real launchers: pods and rails on both sides in turn, a random tube across a launcher face, only launchers round the slot's own muzzle; twin guns fire both barrels together; L/R barrels recognised and measured from their meshes; fixed defences block routes; AA ignores fixed defences when taking cover; half the hit flash on aircraft
- `d275752` 2026-09-27 Only defences a mode puts down block routes (map fortresses keep their checked lanes); campaign back to 17/17 at 5/5

</details>

## v0.16.0: Straight direct-fire shells, no roof guns on the twin turrets

2026-09-27 18:02 · `7dc3ad5`

<details><summary>1 commits</summary>

- `870dedd` 2026-09-27 Direct-fire shells fly straight down the barrel whatever their blast size (only artillery and howitzers arc); no roof gun on the camp bastion or the coastal turret

</details>

## v0.15.0: Rarer, deadlier aircraft; neutral point towers; defences that burn and stay; bombs under the bomber; ground units ignore circling aircraft

2026-09-27 17:51 · `ba93704`

<details><summary>3 commits</summary>

- `50460c6` 2026-09-27 Air power rarer and stronger: aircraft cost about 1.45x, six at most per side, aircraft and bombers hit harder, anti-air 1.4x to stay the counter; ground units no longer chase circling aircraft; bombs land under the bomber; neutral watchtowers on capture points; defences burn, cook off and stay as ruins; twin guns fire barrel by barrel; a gentler hit flash
- `2c44846` 2026-09-27 Defences do not flash white; the camp bastion's roof carries twin flak instead of SAMs launched from its roof; -mb-towerwatch and -mb-bastion device checks
- `4b61532` 2026-09-27 Balance with rarer aircraft: player-like test decks, the last point is always attacked, committed attacks press on 60 s, m10 enemy economy eased; campaign 17/17 at 5/5

</details>

## v0.14.0: Damage you can see, two-weapon vehicles, air war, 200 m maps, three-stage siege with fortress art, Attack/Defend rework, Breakthrough, recorded audio

2026-09-27 16:41 · `e508a29`

<details><summary>12 commits</summary>

- `6282482` 2026-09-27 Weapons take turns and machine guns fire in bursts; guns leave aircraft to anti-aircraft; long shots can miss
- `5634a0f` 2026-09-27 Aircraft at believable sizes, jets and bombers faster and higher, rotors that sweep instead of strobing
- `c9d9e69` 2026-09-27 Damage shows on the hull; cluster rockets for the elite MLRS and a new elite Grad; elite weapons
- `1221030` 2026-09-27 200 m battlefields filled with more to see; Siege rebuilt as a three-stage fortress assault
- `f8b9487` 2026-09-27 Capture modes protect each camp: indestructible bastions, home-zone repair and spawn grace, no strikes on a camp, a comeback behemoth
- `1c9938f` 2026-09-27 Fortress defences for the multi-stage siege: heavy turret, flak tower, missile battery, shield generator
- `10f0adf` 2026-09-27 Blasts and smoke screens stop popping over each other: a fixed draw order per effect layer, flipbook smoke screens that cover what burns inside, blasts in front drawn over them
- `f2c3c14` 2026-09-27 Fortress art in the siege: heavy coastal turrets, flak towers, missile batteries and shield generators; spawn bastions on the heavy turret; fortress interior laid out so every piece stands
- `4c3ce9b` 2026-09-27 Real recorded sound effects: 63 licensed OGGs in Resources/Audio, with credits
- `d09f638` 2026-09-27 Attack and Defend stances that play differently: Defend holds the front point, never falls back and digs in (hull-down, -20% damage); Attack goes for the weakest-held point; watchtowers on captured points; Assault rebuilt as a three-sector Breakthrough; lone artillery closes to range and kites
- `6393a5b` 2026-09-27 Recorded battle sounds (Sonniss GDC bundles and CC0, credited in Resources/Audio/CREDITS.md) with a proper mix: variants without repeats, voice limits and priorities, distance muffling, speed-of-sound delay for far blasts, ducking under big blasts, fires crackling near the view
- `f1139d5` 2026-09-27 Hit feedback (white flash, hull rock, damage trail on the health bar); hull-down only against direct fire; campaign at 17/17 missions 5/5 with the new AI, maps and fortress; -mb-smokescreen device check; progress notes

</details>

## v0.13.0: No stutter, tougher vehicles and slower economy, real artillery, Grad, ATGM carrier, APS tank, collapsing buildings, unstuck AI

2026-09-27 14:39 · `c7edbdd`

<details><summary>8 commits</summary>

- `3e446e0` 2026-09-27 No more stutter from the camera and blasts; all cards unlocked for testing; menus drag with the mouse
- `d293b44` 2026-09-27 Vehicles no longer stall against walls, the map's edge or each other; anti-aircraft follows the armour
- `4f09b89` 2026-09-27 Tougher vehicles, a slower economy, buildings that collapse in their own dust
- `d1b7425` 2026-09-27 Artillery that reads as artillery, plus grad_truck, atgm_carrier and aps_tank
- `4c6cff1` 2026-09-27 Thicker dust when a building comes down; the flattened remains sink out of sight; -mb-demolish device check
- `2385422` 2026-09-27 Artillery that reads as artillery, a Grad truck, an ATGM carrier and an active-protection tank
- `74f97be` 2026-09-27 Campaign kept at 5/5 with the new cards in players' decks (m10, m13 income); shake setting hidden while shake is off
- `6d3d57f` 2026-09-27 Progress notes for the stutter, toughness, artillery and collapse round

</details>

## v0.12.0: Smooth blasts, map outlines and minimap, phone UI, line of fire, barrel elevation, scale pass, map kit on every battlefield

2026-09-27 13:06 · `315074f`

<details><summary>14 commits</summary>

- `29f1032` 2026-09-27 Smoother battles: no blast lights, one big blast per death, calm crowds, upkeep instead of an army cap
- `2719e5f` 2026-09-27 Barrels rise to fire; direct fire no longer goes through buildings and rock
- `f3ca406` 2026-09-27 Every battlefield has its own shape; the minimap shows the real map
- `f1baab9` 2026-09-27 Battle HUD made for phones, responsive on every screen shape; Editor ready; AI goes for crates
- `6f196c4` 2026-09-27 Second visible weapon on 18 single-weapon models
- `b3f3fa4` 2026-09-27 Aircraft drawn nearer their real size, ground vehicles a little smaller, houses and buildings 15 % larger
- `22c22ed` 2026-09-27 Every combat vehicle carries at least two weapons; aircraft flights no longer hover off their rally point
- `ba12234` 2026-09-27 Scale is visual and hull only: hit radius stays as given; m03 gets 19 min, the Doomsday Train 6400 hp
- `5a2df2e` 2026-09-27 Menus for phones: Be Vietnam Pro everywhere, icon mode tiles, deck card details with weapons
- `5a0093a` 2026-09-27 Map kit: battlefield dressing props (22 models)
- `041d30e` 2026-09-27 Lighter scenery: bay dressing budgeted, shadowless and mostly rock; countryside scatter stays outside the square; lighter small-arms impacts
- `54ab427` 2026-09-27 Map kit on every battlefield: wrecks, craters, trenches, field camps, checkpoints, pylons and poles; jungle bridges
- `49d0256` 2026-09-27 Mobile Fortress 9000 hp (m09 stalled to the time limit on the dressed Frostpeak); map kit noted in the generator header
- `b395c58` 2026-09-27 Shop cards line up: two-line name box, price pinned to the bottom, taller cards; the items note no longer lingers on other tabs; progress notes

</details>

## v0.11.0: The big expansion (collisions, odds AI, abilities, elites, statics, counters, items, doctrines, events, daily challenges, Siege and Boss Rush, four maps, campaign m00 and m13-m16, optimisation)

2026-09-27 09:35 · `a0aadd6`

<details><summary>29 commits</summary>

- `9a65c86` 2026-09-27 Vehicles collide as hulls and steer round each other
- `2682d52` 2026-09-27 AI weighs the odds: outmatched armies fall back and wait for reinforcements
- `835d25e` 2026-09-27 Abilities, elites, fixed defences and a third wave of vehicles
- `e78a02f` 2026-09-27 Counter system: who beats whom, proven in skirmishes and shown on the cards
- `d41f0d0` 2026-09-27 Items bought with coins: MOAB, cluster bombs, airdropped armour and more
- `5ed79c8` 2026-09-27 Art: seven elite enemy units (refurbished, up-armoured base vehicles)
- `e2ba3a5` 2026-09-27 Battle events: supply drops, bomber raids and weather that turns
- `ab41486` 2026-09-27 Third vehicle roster: twin tank, siege tank, heavy MLRS, ballistic TEL, siege mortar, two projectiles
- `ad5a7bd` 2026-09-27 Art: support vehicles, FPV drone, mine and air-dropped crates
- `1f10d5b` 2026-09-27 Doctrines: pick an army-wide edge before each battle
- `5fd38a2` 2026-09-27 Air art: fighter jet, tank buster, recon drone, heavy attack heli; drone mothership and nuke train bosses; icbm
- `b7dda67` 2026-09-27 Siege and Boss Rush modes
- `4e24295` 2026-09-27 Maps: Ember Ridge, Jungle Pass, Skyhold Airbase, Metro City; Siege for all twelve
- `2536921` 2026-09-27 Doomsday launch countdown; animated erector, searchlights, shields, elite bars
- `db8eb10` 2026-09-27 Siege base kit: six static defences and ten fortress props
- `95d21d5` 2026-09-27 Flipbook fire, smoke and fireballs; far more debris
- `af8a771` 2026-09-27 Siege: the command HQ is a hardened fortress core (4x health); siege tests on real fortress maps
- `c0c08cb` 2026-09-27 Menu colours for the volcanic, jungle and urban battlefields
- `89a9570` 2026-09-27 Trail smoke puffs grow less: fill back near the old budget
- `730891a` 2026-09-27 Theme art: volcanic, jungle, airbase and city props (28 models)
- `88e9152` 2026-09-27 Items that do no damage pulse instead of exploding: EMP and shield-dome rings, dust on airdrops; EMP skills ring too
- `06b7437` 2026-09-27 Effects director keeps the catalog for item pulses (fix build)
- `c52a900` 2026-09-27 Campaign: boot camp and four new missions; balanced with the deck a player really has
- `ef82f9c` 2026-09-27 War drums for boss fights, vibration, colour-blind team colours
- `165eeb3` 2026-09-27 Daily challenges: three a day for coins
- `92f08e6` 2026-09-27 Lava without the grid showing through; battlefield towers cut to 62% height so they do not hide the fight
- `2d7b430` 2026-09-27 Performance: prewarm only what a battle can field; lighter city skyline; skill checks at 4 Hz
- `8dccd4f` 2026-09-27 Static batching for still map props; docs for the big expansion; hull and merge helper scripts in Tools
- `edf7083` 2026-09-27 measure_hulls: repo-relative model path, usage note

</details>

## v0.10.0: Campaign, bosses, free-to-play economy, new modes, eight battlefields

2026-09-27 01:06 · `d932007`

<details><summary>18 commits</summary>

- `1bd3d0d` 2026-09-26 WIP: game modes, campaign, economy, skins data, rewards and ads flow
- `4994bcc` 2026-09-26 Aircraft art: overhaul the strike jet, attack jet and drone
- `40646bf` 2026-09-27 Boss focus for the AI, no field repairs on bosses, campaign balance
- `56eefdf` 2026-09-27 New vehicles: howitzer, thermobaric launcher, IFV, heavy AA truck, titan tank
- `b86b767` 2026-09-27 Menu for modes, campaign and shop; procedural camo skins
- `e12871d` 2026-09-27 Five new vehicles: howitzer, thermobaric launcher, IFV, heavy air defence, Titan
- `07d8967` 2026-09-27 Premium supports: napalm strike and carpet bombing
- `5719385` 2026-09-27 Maps: Redrock Canyon, Whiteout Pass, Greenvale Farms, Rust Yard; richer Dunebreak, Frostpeak, Ironport
- `41e241d` 2026-09-27 Cinematic moments on the biggest blasts
- `caaae7c` 2026-09-27 Art: four boss models (behemoth, mobile fortress, armoured train, mega gunship)
- `97b28de` 2026-09-27 Four new battlefields on the menu: Redrock Canyon, Whiteout Pass, Greenvale, Rust Yard
- `aab2e41` 2026-09-27 Aircraft art: polish the helicopters and munitions, add the heavy and stealth bombers
- `34b1da6` 2026-09-27 Aircraft art: add the sky gunship, finish the premium aircraft
- `d9959bd` 2026-09-27 Runtime: spin Propeller_2.. pivots and load-test the premium aircraft
- `9ffa5a2` 2026-09-27 Ground vehicles: detail pass on all 14 units plus the civilian car and truck
- `9c39927` 2026-09-27 Campaign: every mission winnable again on the richer maps
- `e90854c` 2026-09-27 Premium aircraft in battle: heavy bomber, stealth bomber, sky gunship
- `b648bd3` 2026-09-27 Docs: campaign, economy, modes, eight battlefields; shorter Vietnamese name for Greenvale

</details>

## v0.9.0: UI redesign, new maps and weather, muzzle fire, settings and shadows

2026-09-26 21:20 · `8c33c9f`

<details><summary>7 commits</summary>

- `03183aa` 2026-09-26 Harbour models: containers, gantry crane, factory, rail wagons, dock and street props
- `8354413` 2026-09-26 Desert and snow map models: adobe town, oilfield, mesa, snowy village and radar station
- `8ad8086` 2026-09-26 UI redesign, graphics tiers, off-screen culling, muzzle fire and smoke
- `4092fa3` 2026-09-26 Keep the market stall's jars inside its 4 m footprint
- `eaf8544` 2026-09-26 Three new battlefields, map themes, and snow, sandstorm, fog and night weather
- `6bd5c17` 2026-09-26 Full graphics settings, shadows fitted to the view, research-driven performance
- `b1fcfe1` 2026-09-26 Docs: new maps, settings, shadows and the performance research

</details>

## v0.8.0: Air power, a real town, mountains, effects that never reset, full audit

2026-09-26 19:25 · `1b5592b`

<details><summary>9 commits</summary>

- `ebe3aa1` 2026-09-26 Add ten vehicles and aircraft; chunkier attack helicopter
- `00deeae` 2026-09-26 Town buildings, barriers, civilian vehicles and more tree species
- `54e0141` 2026-09-26 Effects that never reset, no slow motion, steadier frames
- `ecb88a4` 2026-09-26 New units, aeroplanes, a real town and a mountain range
- `b3b51a4` 2026-09-26 Crisp animated ground markings; mountains coloured and forested
- `7a82c71` 2026-09-26 Menu fixes: language applies at once, back key closes pages or pauses, readable card costs, Survival hint
- `67cbd9f` 2026-09-26 Audit fixes: simulation, AI, balance and map generator
- `f28e082` 2026-09-26 Audit fixes: effects, rendering, HUD, input and audio
- `b0fa4fb` 2026-09-26 Docs: milestone entry, perf switches, SmoothStep and fog notes, map generator

</details>

## v0.7.0: Auto-play commander, cleaner and bigger explosions

2026-09-26 17:08 · `7d2a531`

<details><summary>2 commits</summary>

- `9ed7dd2` 2026-09-26 Sparks as glowing points, and more fire: secondaries, burning debris, lingering fires
- `c57b703` 2026-09-26 Auto-play commander: the army fights on its own, the player steers intent

</details>

## v0.6.0: Visual overhaul fixes

2026-09-26 16:42 · `e0dbaa3`

<details><summary>1 commits</summary>

- `7163f16` 2026-09-26 Explosions without hard lines or claw streaks, and cheaper

</details>

## v0.5.0: Visual overhaul fixes

2026-09-26 16:23 · `5d3e449`

<details><summary>1 commits</summary>

- `d08eaeb` 2026-09-26 Notes: device test flags and headless balance check

</details>

## v0.4.0: Flicker fix, full roster with aircraft, Conquest with CP and strikes, menus, weather, terrain, explosions

2026-09-26 16:22 · `7727e7c`

<details><summary>10 commits</summary>

- `8e977f7` 2026-09-26 Fix vehicle flicker; add weapon mounts, aircraft, CP, strikes and Conquest
- `531df6f` 2026-09-26 Main menu, Conquest HUD, deck, strikes targeting and minimap
- `56feec8` 2026-09-26 Add APC, MLRS, AA, flame tank, aircraft, munitions and terrain models
- `f7fed2d` 2026-09-26 Conquest AI saves for strong units and fields a mixed army; slower ticket drain
- `3cc7066` 2026-09-26 Use the new models: muzzles per mount, new materials, model tests, waves with the full roster
- `4bb5b43` 2026-09-26 Sounds for launches, flak, flamethrowers, jets, rotors, strike alarms and objective chimes
- `23d56ec` 2026-09-26 Weather, mountains and terrain props
- `fae5970` 2026-09-26 Noise-eroded fireballs, lit smoke, burning debris; bomb-line telegraphs; tap fixes; progress log
- `35f2c9a` 2026-09-26 AI flanks from alternating sides
- `0a77f5b` 2026-09-26 Fix issues from code review

</details>

## v0.3.0: Blender art, UI Toolkit HUD, surroundings, effects, audio and tactical AI

2026-09-26 14:19 · `6d69447`

<details><summary>6 commits</summary>

- `bc14eb1` 2026-09-26 Add Blender asset pipeline and first low-poly models
- `8bf96b2` 2026-09-26 Render Blender models in the match
- `bdab35c` 2026-09-26 Paint the battlefield like the reference
- `0798250` 2026-09-26 Rebuild the HUD with UI Toolkit in the reference style
- `b65e3f2` 2026-09-26 Surround the battlefield with countryside
- `9eb19f2` 2026-09-26 Battle effects, synthesised audio and tactical AI

</details>

## v0.2.0: Add playable combat sandbox

2026-09-26 12:28 · `90807b0`

Vehicles-only battle on the Ashfield sandbox map, running on the Android
emulator.

- Simulation: fixed-step world, validated commands (move, attack,
  attack-move, stop, retreat), team vision, grid A* with formations and
  stuck detection, projectiles with travel time, damage table, splash,
  delayed explosions with terminating chain reactions
- Data-driven balance and map JSON with a comment-tolerant reader
- Sandbox mode with enemy waves and reinforcements, placeholder AI
- Voxel models drawn in code, greedy mesher, debris chunks and rubble
- Pooled effects: five explosion tiers, tracers, scorch marks, burning
  wrecks with tossed turrets, physics debris, camera shake, slow motion
- Touch controls (tap, double tap, box select, pan, pinch) and HUD
- Hand-written URP shaders; scene generated from code
- 38 EditMode tests; progress and known limitations in Docs/PROGRESS.md

## v0.1.0: Set up Machine Brigade Unity project

2026-09-26 11:44 · `ed9e2f9`

Unity 6000.6.3f1 URP project for a vehicles-only 3D mobile tactics game.

- Game plan in Docs/GAME_PLAN.md; earlier RTS plans kept as reference
- Player settings applied from code (bundle id com.winka.machinebrigade,
  landscape, IL2CPP ARM64) and command-line Android/iOS build scripts
- Pure C# simulation assembly with a fixed-step SimClock and EditMode tests
- Emulator images denied Vulkan so they fall back to GLES3
- Tools/run-android.sh installs and launches the dev APK
