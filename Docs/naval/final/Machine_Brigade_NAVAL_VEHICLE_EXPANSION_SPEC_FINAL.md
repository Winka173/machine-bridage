# Machine Brigade — Naval Vehicle Expansion Spec (Final Draft)

## 0. Scope and design constraints

This spec expands the naval roster while reusing existing Machine Brigade systems.

Hard constraints:
- Do **not** add bridge-laying, troop transport, cargo transport, vehicle recovery, towing, revive/resurrection, salvage, or terrain-changing mechanics.
- Do **not** require a new radar/vision gameplay layer.
- Do **not** create new logistics subsystems just to support one unit.
- Prefer existing movement, weapon, projectile, aura, jammer, shield, interception, repair/resupply, stealth, and target-priority systems.
- If an existing hull/ID already fills a role, extend it with variants rather than creating a redundant unit.
- Do not modify boss armour or boss balance as part of this work.
- Do not reuse boss-only weapons directly when that would couple player balance to boss balance. Create player variants when necessary.

## 1. Existing naval baseline to preserve

Current relevant vehicle IDs include:
- `hover_gunboat` — light escort/gunboat.
- `missile_boat` — light missile/rocket boat.
- `river_patrol_boat` — light patrol craft.
- `river_gunboat` — heavier gunboat.
- `sea_corvette` — existing corvette baseline.
- `sea_cruiser` — existing cruiser baseline.
- `landing_craft` — transport/support; **do not use as the template for new combat roster mechanics**.

Use these as balance anchors. Do not duplicate their exact roles.

## 2. Naval progression

Target progression:

Patrol/FAC → Corvette → Frigate → Destroyer → Cruiser/Battlecruiser → Battleship

Specialists may sit between tiers but must have a clear weakness.

### Approximate purchasable CP targets

These are final starting values for implementation and regression. Adjust only if a canonical economy constraint makes a value impossible, and report any adjustment.

| Unit | CP |
|---|---:|
| Torpedo Boat | 7 |
| CIWS Escort Craft | 8 |
| AShM Corvette | 9 |
| Air-Defence Corvette | 9 |
| EW Corvette | 9 |
| Frigate | 11 |
| Missile Frigate | 12 |
| Air-Defence Frigate | 12 |
| ASW Corvette* | 10 |
| Rocket Artillery Ship | 12 |
| Monitor / Heavy Gunboat | 13 |
| Destroyer | 14 |
| Gun Destroyer | 14 |
| Missile Destroyer | 15 |
| Air-Defence Destroyer | 15 |
| Attack Submarine* | 14 |
| Gun Cruiser variant | 17 |
| Missile Cruiser variant | 18 |
| Battlecruiser | 19 |
| Battleship | 23 |

`*` ASW/Submarine content is only allowed if the existing submarine/underwater runtime used by current content can be reused without inventing a new navigation/detection subsystem. If not, omit those two IDs from implementation and explicitly report them as blocked by the “no complex new mechanic” rule. Do not simulate them with hidden omniscience.

## 3. Role rules

Every new ship must have:
- one primary role;
- one secondary capability at most;
- an explicit counter;
- an explicit matchup it should lose.

Avoid “everything ships” that combine top-tier gun, top-tier AShM, top-tier SAM and top-tier CIWS on one hull.

### Naval armour class guide

Use current canonical armour scale and inheritance rules. Suggested chassis classes:
- light craft: Armour 0–1;
- corvette: Armour 1–2;
- frigate: Armour 2;
- destroyer: Armour 2–3;
- cruiser/battlecruiser: Armour 3–4;
- battleship: Armour 4;
- no player naval Armour 5 by default.

Do not change the locked penetration tables.

## 4. New units

### 4.1 Torpedo Boat

ID: `torpedo_boat`

Role: cheap glass-cannon anti-capital craft.

Function:
- very fast;
- low HP;
- primary weapon is a slow/readable torpedo salvo;
- strong versus frigate/destroyer/cruiser;
- weak versus gunboat/corvette and air.

Implementation:
- CP 7.
- Armour 0–1.
- HP target: about 1.15–1.30 × current `missile_boat` HP.
- Primary: new player weapon `naval_torpedo_light`.
- Secondary: one light MG/autocannon at most; no meaningful DPS buff.
- Torpedo speed must be visibly slower than anti-ship missile speed.
- No stealth subsystem required.

Should lose to:
- `hover_gunboat`;
- gun corvette/`sea_corvette` at close range;
- aircraft if unsupported.

### 4.2 CIWS Escort Craft

ID: `ciws_escort_craft`

Role: low-cost missile/drone interception escort.

Function:
- protect nearby ships from missiles/rockets/drones;
- poor anti-surface damage.

Implementation:
- CP 8.
- Armour 1.
- HP roughly around `hover_gunboat` to slightly above it.
- Primary: player CIWS/interceptor weapon derived from existing CIWS logic.
- Interception radius/charges must be weaker than dedicated high-tier point defence.
- Surface damage intentionally low.

Should lose to:
- gun corvette;
- frigate;
- heavy direct cannon.

### 4.3 AShM Corvette

ID: `ashm_corvette`

Role: mid-light anti-ship missile specialist.

Implementation:
- CP 9.
- Armour 1–2.
- HP target around 0.85–0.95 × existing `sea_corvette`.
- Primary: `anti_ship_missile_corvette`.
- Use latest anti-ship projectile feel: effective speed around 80 m/s unless current canonical family explicitly requires the same value through inheritance.
- Pen 4.
- Damage balanced below frigate/destroyer AShM alpha.
- Secondary: light 30–57 mm gun only.

Should lose to:
- gun corvette at close range;
- CIWS-protected group if firing alone.

### 4.4 Air-Defence Corvette

ID: `aa_corvette`

Role: short/medium naval air defence.

Implementation:
- CP 9.
- Armour 1–2.
- HP near `ashm_corvette`.
- Primary: short/medium SAM.
- Secondary: CIWS/light gun.
- SAM damage KEEP relative to the chosen player SAM family.
- Do not give strong anti-surface missile damage.

Should lose to:
- dedicated anti-ship craft;
- gun destroyer.

### 4.5 EW Corvette

ID: `ew_corvette`

Role: simple jammer escort.

Implementation:
- CP 9.
- Armour 1.
- HP slightly below combat corvette.
- Primary combat weapon: light self-defence gun only.
- Utility: reuse existing jammer/aura logic.
- Do not add radar, reveal, fake contacts or target cloning.
- Aura may reduce guided lock/reacquisition/accuracy according to existing jammer semantics; do not invent hidden global miss chance.

Should lose to:
- almost any equal-CP direct-combat ship in a duel.

### 4.6 Frigate

ID: `frigate`

Role: general-purpose naval mainline unit.

Implementation:
- CP 11.
- Armour 2.
- HP target around 1.20–1.35 × `sea_corvette`.
- Primary: 100–127 mm naval gun.
- Secondary: limited AShM OR limited short SAM, not both at premium strength.
- Moderate speed.
- No special mechanic.

Should lose to:
- destroyer head-on;
- missile specialist at long range if unprotected.

### 4.7 Missile Frigate

ID: `missile_frigate`

Role: anti-surface missile specialist.

Implementation:
- CP 12.
- Armour 2.
- HP close to `frigate`.
- Primary: stronger/larger AShM salvo than `ashm_corvette`.
- Secondary: modest gun.
- Weaker AA than base frigate.
- Long cooldown / clear salvo cadence.

Should lose to:
- gun destroyer if closed to gun range;
- interception-heavy defence when unsupported.

### 4.8 Air-Defence Frigate

ID: `aa_frigate`

Role: medium naval area air defence.

Implementation:
- CP 12.
- Armour 2.
- HP close to base frigate.
- Primary: medium SAM.
- Secondary: CIWS.
- Surface gun only enough for self-defence.
- No long-range anti-ship alpha.

Should lose to:
- missile frigate / destroyer in surface duel.

### 4.9 ASW Corvette — conditional

ID: `asw_corvette`

Only implement if existing submarine gameplay can be reused without new radar/vision/sonar architecture.

Role:
- counter existing submarine-type targets.

Allowed mechanics:
- existing target filtering;
- existing projectile/homing;
- simple proximity/depth-charge weapon.

Forbidden:
- new acoustic simulation;
- new hidden detection game;
- new sonar UI.

CP 10.

### 4.10 Rocket Artillery Ship

ID: `rocket_artillery_ship`

Role: naval fire support.

Implementation:
- CP 12.
- Armour 1–2.
- HP below destroyer.
- Primary: navalized MLRS/GMLRS-style salvo using existing fire-support logic.
- Use locked artillery projectile-speed rules.
- Raw damage should follow the existing MLRS family; differentiate via salvo coverage/cadence, not an arbitrary huge damage multiplier.
- Weak in direct naval brawl.
- Respect minimum range.

Should lose to:
- fast attack craft that closes;
- destroyer in direct fire.

### 4.11 Monitor / Heavy Gunboat

ID: `naval_monitor`

Role: slow heavy gun / shore bombardment.

Implementation:
- CP 13.
- Armour 3.
- High HP for cost, low speed.
- Primary: 152–203 mm gun.
- Strong versus structure and medium ships.
- Weak versus long-range AShM and air.
- No large missile suite.

### 4.12 Destroyer

ID: `destroyer`

Role: heavy general-purpose surface combatant.

Implementation:
- CP 14.
- Armour 3.
- HP around 1.35–1.50 × frigate.
- Primary: 127–130 mm naval gun.
- Secondary: moderate AShM + short/medium SAM + limited CIWS.
- None of the secondary systems should equal a specialist destroyer variant.
- This is the naval “MBT” reference unit.

### 4.13 Gun Destroyer

ID: `gun_destroyer`

Role: surface brawler / shore bombardment.

Implementation:
- CP 14.
- Armour 3.
- HP similar to destroyer.
- Primary gun damage/output +10–15% over base destroyer through weapon choice/cadence, not all secondary weapons.
- Reduced missile capability.
- Strong versus corvette/frigate and structures.
- Weak to missile destroyer at standoff range.

### 4.14 Missile Destroyer

ID: `missile_destroyer`

Role: heavy anti-surface standoff.

Implementation:
- CP 15.
- Armour 2–3.
- HP slightly below base destroyer or equal.
- Primary role: large AShM salvo.
- Secondary gun weaker than gun destroyer.
- SAM only self-defence grade.
- Salvo must be interceptable and readable.

### 4.15 Air-Defence Destroyer

ID: `aa_destroyer`

Role: high-end fleet air defence.

Implementation:
- CP 15.
- Armour 3.
- HP around destroyer.
- Primary: medium/long SAM.
- Secondary: CIWS.
- Surface gun modest.
- Long-range SAM speed follows latest player SAM master; do not inherit boss-specific values.

Should lose to:
- dedicated surface destroyer/cruiser if isolated.

### 4.16 Attack Submarine — conditional

ID: `attack_submarine`

Only if existing submarine runtime/navigation from current content can be reused without a new subsystem.

Role:
- ambush anti-ship specialist.

Implementation:
- CP 14.
- Low/medium HP.
- Primary: torpedo.
- Any stealth must reuse an existing stealth mechanic.
- No new sonar minigame, depth layers, manual dive system or transport.

If this requires new architecture, omit and report blocked.

### 4.17 Gun Cruiser Variant

Use existing `sea_cruiser` as the anchor. Prefer a branch/variant rather than a redundant independent hull.

ID: `sea_cruiser.gun` or canonical project naming equivalent.

Role:
- heavy gun cruiser.

Implementation:
- CP 17 if purchasable.
- Armour 3–4.
- Primary: 152–203 mm heavy naval gun.
- Limited SAM/CIWS only.
- Strong versus destroyer/structure.
- Weak versus AShM concentration.

### 4.18 Missile Cruiser Variant

ID: `sea_cruiser.missile`

Role:
- heavy missile platform.

Implementation:
- CP 18.
- Armour 3.
- HP close to gun cruiser.
- Primary: long-range AShM/cruise-style naval strike weapon.
- Secondary: medium SAM + CIWS at non-specialist strength.
- Main gun reduced.
- Do not use boss cruise weapons directly.

### 4.19 Battlecruiser

ID: `battlecruiser`

Role:
- high-cost fast capital surface combatant.

Implementation:
- CP 19.
- Armour 3–4.
- HP between cruiser and battleship.
- Faster than battleship.
- Primary: heavy gun OR heavy AShM emphasis, with the other as secondary.
- Do not give battleship gun durability plus missile-cruiser alpha simultaneously.

### 4.20 Battleship

ID: `battleship`

Role:
- superheavy frontline capital ship.

Implementation:
- CP 23.
- Armour 4.
- Highest normal player naval HP.
- Primary: 280–406 mm heavy naval gun.
- Long reload, clear impact presentation.
- Secondary AA/CIWS exists but is not specialist-tier.
- No transport, aircraft spawning, repair aura or special subsystem.
- Must be vulnerable to concentrated Pen 4 AShM/torpedo/specialist weapons despite raw durability.

## 5. Existing units: role cleanup

Do not delete current units.

Recommended role anchors:
- `river_patrol_boat`: cheap patrol/light harassment.
- `hover_gunboat`: fast close escort / light point defence.
- `missile_boat`: cheap missile/rocket attack craft.
- `river_gunboat`: gun-heavy river/shore platform.
- `sea_corvette`: baseline gun/general corvette.
- `sea_cruiser`: baseline heavy cruiser; branch into gun/missile variants if supported.
- `landing_craft`: scripted/support transport only; no expansion priority.

## 6. Weapon policy

Damage buffs or tuning must refer to exact primary weapon IDs.

Do not silently buff:
- MG/HMG self-defence;
- coaxial/roof weapons;
- CIWS surface DPS;
- SAM damage when only durability/role is being changed.

Player anti-ship missile:
- Pen 4 unless a later explicit specialist rule says otherwise.
- effective speed target around 80 m/s.
- keep missile flight readable/interceptable.

Dedicated naval torpedo:
- slower than AShM;
- high anti-heavy value;
- readable wake/travel;
- no random one-shot/cookoff mechanic.

Heavy capital guns:
- fast kinetic/direct shells are allowed to remain fast;
- do not apply missile speed rules to gun shells.

## 7. AI doctrine requirements

Add explicit CombatRoleDoctrine for every new ship.

Required behavior:
- missile ships maintain standoff distance;
- gun ships close only to their preferred gun envelope;
- AA escorts stay near valuable naval groups;
- CIWS escort stays inside escort/intercept range but does not lead the formation;
- EW corvette stays protected and does not duel;
- rocket artillery ship respects minimum range and relocates if threatened;
- monitor does not chase fast craft;
- battleship does not waste primary heavy-gun salvo on a nearly dead patrol boat if a higher-value target exists;
- target feasibility must respect weapon target domain;
- overkill reservation applies to large AShM/torpedo/heavy-gun salvos.

No retreat-by-health.

## 8. Economy/value regression

For each new ship report:
- CP;
- HP/CP;
- primary effective DPS/CP versus intended target;
- salvo alpha/CP where relevant;
- interception value/CP for AA/CIWS;
- expected useful lifetime;
- role failure matchup.

New ships must not make existing `river_gunboat`, `sea_corvette` or `sea_cruiser` strictly obsolete.

## 9. Required matchup tests

At minimum:
- patrol/hover gunboat ↔ torpedo boat;
- sea_corvette ↔ AShM corvette;
- AShM corvette ↔ CIWS escort + corvette;
- frigate ↔ sea_corvette;
- missile frigate ↔ frigate;
- destroyer ↔ frigate;
- gun destroyer ↔ missile destroyer at close and long range;
- AA corvette/frigate/destroyer ↔ scout heli, attack heli, fighter/attack jet and cruise missile;
- rocket artillery ship ↔ shore tower/structure and moving ship;
- monitor ↔ medium tower/structure and destroyer;
- cruiser ↔ destroyer;
- battlecruiser ↔ cruiser;
- battleship ↔ concentrated AShM/torpedo and heavy gun;
- EW corvette protected group ↔ same group without EW.

## 10. Acceptance

Pass only if:
- no new complex transport/recovery/bridge/revive mechanic was introduced;
- no new radar/vision subsystem was introduced;
- existing ships retain meaningful niches;
- every new ship has a clear counter;
- specialist ships are not universal generalists;
- AShM/torpedo/rocket projectiles remain readable and interceptable where intended;
- AI uses range and role correctly;
- CP curve is monotonic enough that higher tiers feel stronger without making lower tiers useless;
- boss data and boss armour remain unchanged;
- exports/docs are regenerated only after canonical/runtime implementation and regressions pass.
