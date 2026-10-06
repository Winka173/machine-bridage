# 06/10 owner prompt (verbatim): naval vehicle expansion (prompt + spec)

đây là list các phương tiện naval mới, thêm vào, ngân sách tam giác tăng 200% bình thường, đây sẽ là stage rework từ từ mọi phương tiện để đẹp hơn, nhớ là không test, áp dụng các biện pháp tiết kiệm token, xong thì deck phân ra thêm tab cho đầy đủ

<pasted_content id="e0cc">
Implement the attached Machine Brigade naval vehicle expansion as an additive canonical-data pass.

SOURCE OF TRUTH:
Use `Machine_Brigade_NAVAL_VEHICLE_EXPANSION_SPEC.md` as the implementation specification. Existing generated XLSX/MD files may be stale; trace canonical source -> inheritance/variant -> runtime -> export.

CRITICAL CONSTRAINTS:
- Do NOT add transport, troop carrying, landing logistics, bridge/ferry, towing, recovery, revive, salvage, carrier spawning, or ship-production queue mechanics.
- Do NOT add radar, vision, sonar, reveal, or new detection systems.
- Do NOT create a generic gun corvette: existing `sea_corvette` already fills that role.
- Do NOT create a generic gun cruiser: existing `sea_cruiser` already fills that role.
- Preserve existing `river_patrol_boat`, `river_gunboat`, `hover_gunboat`, `missile_boat`, `sea_corvette`, and `sea_cruiser`.
- `ew_corvette` may be implemented ONLY by reusing the existing generic jammer runtime. If that requires a new subsystem, mark it `BLOCKED_BY_EXISTING_RUNTIME` and skip it.
- Use existing naval movement/path/lane code. No new naval navigation subsystem.
- Anti-ship missile effective speed = 80 m/s.
- AShM Pen = 4 unless explicitly overridden later.
- No generic SAM/AAM damage buff.
- No random crit, morale, retreat-by-health, or random penetration systems.

ADD THESE DISTINCT NEW UNITS:
1. `torpedo_boat`
2. `ashm_corvette`
3. `aa_corvette`
4. `frigate`
5. `missile_frigate`
6. `aa_frigate`
7. `destroyer`
8. `gun_destroyer`
9. `missile_destroyer`
10. `aa_destroyer`
11. `rocket_artillery_ship`
12. `heavy_monitor`
13. `battlecruiser`
14. `battleship`
15. `missile_cruiser`
16. `ciws_escort_ship`
17. `ew_corvette` only if existing jammer runtime is directly reusable

DO NOT ADD:
- duplicate gun corvette
- duplicate gun cruiser
- radar picket ship
- sonar/ASW hunter
- new attack submarine
- transport/LST/carrier/drone carrier
- repair/revive/recovery/towing ships
- complex naval minelayer
- any ship that spawns combat units

IMPLEMENTATION:
- Use the stat targets and roles from the spec as initial canonical targets.
- Reuse existing weapon families only where it does not unintentionally alter old units.
- If a shared weapon change would affect unrelated units, create a ship-specific variant.
- Battleship heavy gun may be Pen5; do not spread Pen5 to normal AShM.
- CIWS/SAM must use existing interception/targeting pipelines.
- Torpedo is a simple slow guided naval projectile using the current projectile system, NOT an underwater simulation.
- Rocket artillery ship uses existing artillery/rocket logic.
- Do not invent new radar/vision/sonar mechanics.

AI:
Add explicit roles and target priorities for every new unit.
- missile/torpedo ships prioritize valuable/heavy naval targets
- AA ships prioritize aircraft
- CIWS escort remains near high-value allied naval units using existing escort/squad logic
- rocket artillery ship avoids close combat
- no full-salvo waste on nearly dead light targets
- no retreat-by-health

BALANCE REGRESSION:
For every new ship compare CP, HP/CP, primary DPS/CP and effective DPS against:
- `river_patrol_boat`
- `river_gunboat`
- `hover_gunboat`
- `missile_boat`
- `sea_corvette`
- `sea_cruiser`

Run at minimum:
- light-vs-light
- torpedo vs corvette/cruiser/battleship
- `sea_corvette` vs `ashm_corvette`
- general frigate vs specialist frigates
- destroyer vs frigate
- destroyer vs `sea_cruiser`
- missile salvo vs layered CIWS
- AA escort vs drones/helicopters/jets/bombers
- rocket artillery ship vs moving ship and shore structure
- heavy monitor vs destroyer/cruiser
- battlecruiser vs battleship
- battleship vs missile saturation and Pen5 specialist fire
- CIWS escort with and without protected capital ship

MODEL/VFX:
Create or wire readable hull/model assets, muzzle/launcher nodes, wake, launch/impact FX, wreck/death behavior and CIWS mounts where required. Do not add functional transport bays/doors.

PIPELINE:
1. modify canonical source
2. add weapon variants only where needed
3. add AI mappings
4. add models/reference metadata
5. run validators/regressions
6. run Unity `ExportGameDoc`
7. run export pipeline
8. stale-value scan

FINAL REPORT MUST INCLUDE:
- every canonical file changed
- every new unit ID
- final CP / HP / armour / speed / turn rate
- exact primary and secondary weapon IDs
- exact projectile speed / Pen / damage / splash for every new missile/torpedo/heavy gun
- AI role and target priorities
- comparison against existing naval anchors
- CIWS/SAM interaction results
- pathing/lane/turn-radius results
- any unit skipped and exact reason
- confirmation no radar/vision/sonar/transport/revive/recovery/carrier subsystem was introduced
- confirmation generated docs were regenerated and stale scan passed
</pasted_content id="e0cc">

spec:

<pasted_content id="e0cc">
Machine Brigade — Naval Vehicle Expansion Spec
Status
Implementation-ready addendum. This document extends the current naval roster without replacing existing naval units.
Core constraints
1. Do NOT add complicated transport/logistics mechanics: no troop carrying, landing transport gameplay, bridge/ferry mechanics, towing/recovery, revive/salvage, carrier-style unit spawning, or ship-production queue subsystem.
2. Do NOT add radar/vision/sonar-dependent gameplay in this pass: no radar picket ship, sonar hunter, detection/reveal subsystem, or new stealth-detection system.
3. Prefer existing systems: direct-fire gun, guided projectile, SAM/AAM targeting, CIWS/APS interception, artillery/rocket salvo, existing jammer aura if generic, and existing naval movement/path/lane code.
4. Do not duplicate existing naval roles. sea_corvette already fills gun-corvette; sea_cruiser already fills gun-cruiser. Preserve river_patrol_boat, river_gunboat, hover_gunboat, missile_boat, sea_corvette, sea_cruiser.
5. New ships must be understandable from weapons and silhouette. Avoid gimmicks.
6. Existing combat rules remain authoritative, including penetration/damage tables and latest projectile-speed locks. Anti-ship missile effective speed remains 80 m/s unless an explicit ship-specific exception is later approved.
Existing naval baseline
Treat these as existing anchors, not new units:
- river_patrol_boat — very light patrol / close defense
- river_gunboat — heavier river gun platform
- hover_gunboat — fast gun/CIWS craft
- missile_boat — light AShM platform
- sea_corvette — existing gun corvette
- sea_cruiser — existing heavy gun cruiser
New naval units
1. torpedo_boat
Role: cheap glass-cannon anti-heavy naval attacker.
- CP 5
- HP 500
- Armour 0
- Speed 13 m/s
- Primary: 2-round torpedo salvo
- Torpedo damage 360 each
- Pen 4
- ShapedCharge
- Projectile speed 55 m/s
- Range 65 m
- Min range 12 m
- Splash 3 m
- Salvo cooldown 12 s
- Weak self-defense gun
  Implementation: use current guided-projectile pipeline near sea level; no underwater simulation.
  Expected failure: loses to patrol/gun craft and sustained corvette fire.
2. ashm_corvette
Role: medium anti-ship missile specialist.
- CP 9
- HP 1150
- Armour [2,1,1,1]
- Speed 8.5 m/s
- 4 AShM per salvo
- Damage 450 each
- Pen 4
- Speed 80 m/s
- Splash 6 m
- Cooldown 18 s
- One light 57–76 mm gun or CIWS
  Expected failure: weaker than sea_corvette in sustained gun duel; punished if salvo is intercepted.
3. aa_corvette
Role: cheap fleet air-defense escort.
- CP 8
- HP 1050
- Armour [2,1,1,1]
- Speed 8.5 m/s
- Primary short/medium SAM using approved existing damage
- Secondary CIWS
- Surface gun deliberately weak
  Expected failure: poor vs gun corvette/frigate when isolated.
4. frigate
Role: mid-tier naval generalist, naval equivalent of an MBT.
- CP 12
- HP 1800
- Armour [3,2,2,1]
- Speed 6.5 m/s
- Main gun 100–127 mm
- Main-gun Pen 3
- Main-gun damage ~180–220
- Cooldown ~4.5–5.5 s
- 2 AShM, 450 damage each, Pen4, speed80
- Short/medium SAM
- 1 CIWS
  Expected failure: loses specialist missile/AA matchups and heavy gunnery duel.
5. missile_frigate
Role: dedicated medium-heavy anti-ship missile ship.
- CP 14
- HP 1750
- Armour [3,2,2,1]
- Speed 6.2 m/s
- 6 AShM
- Damage 450 each
- Pen4
- Speed80
- Splash 7 m
- Cooldown 22 s
- Modest 76–100 mm gun
- 1 CIWS
- Optional short SAM only
  Expected failure: weak during missile cooldown.
6. aa_frigate
Role: medium fleet air-defense specialist.
- CP 14
- HP 1850
- Armour [3,2,2,1]
- Speed 6.0 m/s
- Primary medium/long SAM
- Secondary short SAM or CIWS
- 76 mm surface gun only
- No AShM
- SAM damage stays on approved existing family values
  Expected failure: poor anti-surface CP efficiency.
7. destroyer
Role: heavy general-purpose surface combatant.
- CP 18
- HP 2800
- Armour [4,3,2,2]
- Speed 5.2 m/s
- Main gun 127–130 mm
- Pen 3–4 depending family
- Damage ~260
- Cooldown ~5.5 s
- 4 AShM, 450 damage, Pen4, speed80
- Medium SAM
- 2 CIWS
  Expected failure: should not outgun sea_cruiser in sustained heavy-gun combat.
8. gun_destroyer
Role: surface/shore-bombardment destroyer.
- CP 17
- HP 2900
- Armour [4,3,2,2]
- Speed 5.0 m/s
- 2 × 127–130 mm turrets
- Damage ~250 per gun
- Pen3
- Cooldown ~5.5 s
- No heavy AShM salvo
- Short SAM + CIWS
  Expected failure: vulnerable to long-range missile specialists.
9. missile_destroyer
Role: heavy anti-ship missile platform.
- CP 20
- HP 2700
- Armour [4,3,2,2]
- Speed 4.8 m/s
- 8 AShM
- Damage 450 each
- Pen4
- Speed80
- Splash 8 m
- Cooldown 26 s
- 100–127 mm secondary gun
- 2 CIWS
- Short/medium SAM
  Expected failure: high overkill risk; weak value during salvo cooldown.
10. aa_destroyer
Role: heavy fleet air/missile-defense escort.
- CP 20
- HP 2850
- Armour [4,3,2,2]
- Speed 4.8 m/s
- Primary long SAM
- Secondary medium/short SAM
- 2 CIWS
- 100–127 mm surface gun
- No heavy AShM salvo
  Expected failure: inefficient against surface-heavy enemy composition.
11. rocket_artillery_ship
Role: naval fire-support / saturation platform.
- CP 14
- HP 1450
- Armour [2,1,1,1]
- Speed 5.5 m/s
- Main weapon uses existing navalized GMLRS/Grad-style artillery behavior
- Projectile speed/damage follow latest fire-support master
- Broad coverage, long cooldown
- Light self-defense only
  Expected failure: very poor close combat.
12. heavy_monitor
Role: slow armored shore-bombardment / heavy gunboat.
- CP 15
- HP 2400
- Armour [4,3,3,2]
- Speed 3.5 m/s
- Main gun 152–203 mm
- Damage ~360
- Pen4
- Cooldown ~7 s
- Splash 5–6 m
- Light AA/CIWS
- No AShM
  Expected failure: easy missile target; poor open-ocean mobility.
13. battlecruiser
Role: fast capital anti-surface ship.
- CP 26
- HP 4200
- Armour [4,4,3,2]
- Speed 4.4 m/s
- 2 × 203–254 mm main guns
- Damage ~420
- Pen4
- Cooldown ~7.5 s
- 4 AShM, 450 damage, Pen4, speed80
- 2 CIWS
- 1 medium SAM layer
  Expected failure: cannot facetank battleship; vulnerable to Pen5 specialists.
14. battleship
Role: superheavy normal naval unit.
- CP 32
- HP 6000
- Armour [5,4,4,3]
- Speed 3.2 m/s
- 3 heavy gun turrets
- 280–406 mm identity
- ~600 damage per turret shot
- Pen5
- Cooldown ~10–12 s
- Splash 7–9 m
- Medium AA + CIWS
- No strategic cruise/ballistic superweapon
- No boss-only mechanics
  Expected failure: missile saturation, torpedo swarm, Pen5 specialist fire, very poor mobility.
15. missile_cruiser
Role: heavy missile support / area-denial ship.
- CP 25
- HP 3700
- Armour [4,3,3,2]
- Speed 4.0 m/s
- 8 AShM
- Damage 450 each
- Pen4
- Speed80
- Cooldown 28 s
- Medium/long SAM
- 2 CIWS
- Single 127–130 mm gun
  Expected failure: vulnerable to gun ships after salvo is spent.
16. ciws_escort_ship
Role: dedicated missile/rocket interception escort.
- CP 11
- HP 1350
- Armour [2,2,1,1]
- Speed 7.0 m/s
- 2–3 CIWS systems
- APS/intercept behavior derived from existing naval CIWS/C-RAM runtime
- Small 57–76 mm surface gun
- Low surface DPS
- No AShM
  Expected failure: poor direct combat; value comes from protecting higher-value ships.
17. ew_corvette — conditional
Role: simple electronic-warfare fleet support.
- CP 9
- HP 1000
- Armour [2,1,1,1]
- Speed 8.0 m/s
- Reuse existing ew_jammer-style jammer aura only
- Weak 57–76 mm gun
- No AShM
- No SAM beyond self-defense
  Do NOT add radar, vision reveal, fake contacts, deception AI, or any new sensor system.
  If current jammer runtime cannot be reused directly for naval units, do not implement this unit; report BLOCKED_BY_EXISTING_RUNTIME.
Explicitly not added
Do not create:
- generic gun corvette (already sea_corvette)
- generic gun cruiser (already sea_cruiser)
- radar picket ship
- sonar/ASW hunter
- new attack submarine
- transport ship/LST
- aircraft/drone carrier
- repair/revive/recovery/towing ship
- complex naval minelayer
- bridge/ferry/pontoon unit
- any ship that spawns combat units
Naval progression target
Light:
river_patrol_boat / hover_gunboat / missile_boat / torpedo_boat
Corvette:
sea_corvette / ashm_corvette / aa_corvette / optional ew_corvette
Frigate:
frigate / missile_frigate / aa_frigate
Destroyer:
destroyer / gun_destroyer / missile_destroyer / aa_destroyer
Heavy support:
rocket_artillery_ship / heavy_monitor / ciws_escort_ship
Capital:
sea_cruiser / missile_cruiser / battlecruiser / battleship
Old ships must retain niches:
- missile_boat = cheapest missile attacker
- sea_corvette = efficient gun corvette
- sea_cruiser = efficient heavy gun cruiser
AI doctrine
- torpedo_boat: TankHunter equivalent; large/heavy naval first
- ashm_corvette: anti-heavy missile
- aa_corvette: AntiAir escort
- frigate: balanced escort
- missile_frigate: anti-heavy missile
- aa_frigate: AntiAir
- destroyer: heavy generalist
- gun_destroyer: structure/surface
- missile_destroyer: anti-heavy missile
- aa_destroyer: AntiAir/intercept
- rocket_artillery_ship: Artillery
- heavy_monitor: siege/structure/heavy surface
- battlecruiser: heavy surface
- battleship: superheavy surface
- missile_cruiser: anti-heavy/long-range
- ciws_escort_ship: intercept escort
- ew_corvette: support
AI rules:
- no long chase by artillery/support ships
- AA ships prioritize aircraft
- CIWS escort remains near high-value allied naval units using existing escort/squad logic
- missile ships avoid wasting full salvo on near-dead light craft
- torpedo boat avoids patrol/gun craft when a heavy target exists
- respect existing naval lanes/turn radius
- no retreat-by-health
Weapon / projectile rules
1. Anti-ship missile effective speed = 80 m/s.
2. AShM Pen = 4 unless later explicitly overridden.
3. Do not create Pen5 AShM just because the ship is expensive.
4. Battleship heavy gun may use Pen5 as a true capital/superheavy weapon.
5. CIWS/SAM damage follows existing approved systems.
6. Do not globally change shared weapon families unless every current user is intended to change.
7. Prefer ship-specific weapon variants when necessary.
Economy / balance validation
For every new ship report:
- CP
- HP
- armour facings
- speed / turn rate
- primary weapon
- primary DPS
- effective DPS vs Light / Medium / Heavy naval
- HP/CP
- effective DPS/CP
- missile salvo value/CP where applicable
- expected counter
- expected target
- existing ship comparison anchor
Required matchup matrix:
- light vs light
- torpedo boat vs corvette/cruiser/battleship
- sea_corvette vs ashm_corvette
- general frigate vs specialist frigates
- destroyer vs frigate
- destroyer vs sea_cruiser
- missile ship vs layered CIWS
- AA escort vs drone/heli/jet/bomber
- rocket artillery ship vs moving surface target and shore structure
- heavy monitor vs destroyer/cruiser
- battlecruiser vs battleship
- battleship vs missile saturation
- battleship vs Pen5 specialists
- CIWS escort with/without protected capital ship
No new ship should dominate both its intended target and its intended counter.
Model / VFX
Each new ship needs:
- readable silhouette at normal gameplay camera distance
- visible main gun/launcher placement
- correct muzzle nodes
- CIWS mounts where used
- missile launch FX
- shell impact FX
- wake
- death/wreck behavior compatible with existing ship wreck rules
Do not add functional transport bays/doors.
Data / pipeline
Canonical source first.
1. add canonical vehicle entry
2. add/variant weapons only when required
3. add model/reference metadata
4. add AI role/doctrine mapping
5. add card/unlock/economy integration where appropriate
6. add campaign/mode eligibility only after base regression passes
7. run validators
8. run Unity ExportGameDoc
9. run export pipeline
10. stale-value scan
Generated XLSX/MD are outputs, not editing targets.
Acceptance
PASS only if:
- no duplicate generic gun corvette/cruiser
- no radar/vision/sonar subsystem
- no transport/revive/recovery/carrier subsystem
- each new ship has a distinct tactical role
- old naval units retain useful niches
- AShM uses approved 80 m/s effective speed
- AA/SAM damage is not globally buffed
- CIWS interactions are tested
- AI uses correct targets and avoids salvo waste
- pathing/turn/lane behavior works for every hull size
- CP progression is understandable
- generated docs regenerate cleanly
</pasted_content id="e0cc">

