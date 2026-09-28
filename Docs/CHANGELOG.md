# Changelog

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
