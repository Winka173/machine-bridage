# Changelog

## Prompt 15 (battle rules): armour levels, penetration, six damage types

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

## Prompt 13: combat value, ammunition, modes and difficulty

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

## Prompt 12: stuck vehicles in bases

- A stuck detector in the internal build (`StuckWatch`, `-mb-stuck`), batch runs and a report with
  heatmaps and the ten worst spots in `Docs/stuck-report/`.
- Fixed at their causes: reachable goals and formation slots, no mutual queueing, head-on in the open,
  detours off walls, re-planning over newly closed ground, towers clearing their pad, room for the keep's
  guardian and elites.
- Fortresses: double sally ports and keep gate, clear yards and approaches, a three-cell route for the
  biggest hull everywhere (`check_access.py` checks every map); Swamp's causeways widened.
- A logged safety net for what is left. Episodes over 10 s in 76 battles: 1285 before, 265 after.

## Prompt 14: the Base screen on the real camp, menus sized for a phone

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

## Prompt 11: a compact battle HUD, cards in line, short names, new shields

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

## Prompt 10: Field Command 2.0 (the interface)

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

## Prompt 9: boss parts

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

## Prompt 8: new content, elites and equipment

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
