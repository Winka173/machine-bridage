# 06/10 owner prompt (verbatim): cheap/mid tier addendum + boss missile rescan

làm cái này xong, export window xong hãy làm tiếp cái kia, và kiểm tra tôi thấy rất nhiều tên lửa các boss tốc độ cực nhanh, thường là các loại nhắm thẳng mục tiêu, scan lại toàn bộ:

<pasted_content id="e0cc">
## ADDENDUM — LOW / MID TIER VEHICLES, SMALL-MEDIUM AIRCRAFT, AND TOWERS

Apply this addendum after all previous balance instructions.

Primary goal:
- cheap combat units should no longer be disposable filler;
- mid-tier units must remain clearly stronger than newly buffed cheap units;
- small/medium aircraft should survive long enough to perform their role;
- towers should remain useful without becoming excessive HP sponges.

IMPORTANT DAMAGE RULE:

When this addendum says `damage +X%`, apply it to the unit's **primary role weapon only** unless explicitly stated otherwise.

Do NOT automatically buff:
- coaxial MG;
- roof HMG;
- self-defense MG;
- defensive pintle;
- AA secondary missile;
- generic secondary cannon;
- death explosion.

Examples:

```text
IFV damage buff
→ main autocannon only
→ do not buff coax MG
→ do not buff ATGM unless explicitly requested

Wheeled Gun damage buff
→ main 105 mm weapon only

Flame Tank damage buff
→ flamethrower only

Scout Helicopter damage buff
→ main gun / primary rocket package as specified
→ do not buff unrelated AAM

AA Vehicle gun buff
→ primary AA gun only
→ SAM secondary damage KEEP

Technical damage buff
→ mounted primary combat weapon
→ not generic MG sidearm
```

If weapon inheritance makes a change affect unrelated units, create/use a unit-specific weapon variant rather than globally buffing the shared family.

---

# 1. TIER PHILOSOPHY

Use base canonical CP before card/rank discounts.

Approximate categories:

```text
Cheap combat:
~2–5 CP

Mid-tier combat:
~6–9 CP

High-tier:
~10+ CP or role-specific premium platform
```

Do not mechanically rebalance purely by CP if the unit has a special role.

Target curve:

```text
Cheap:
HP +25–35%
primary-role damage +10–20%
usually CP +1

Mid:
HP +10–18%
primary-role damage +5–10%
CP mostly KEEP

High:
use previous master decisions
```

No hidden boss-damage resistance.

Cheap/mid vehicles should become more durable through real HP/stat changes.

---

# 2. CHEAP GROUND COMBAT UNITS

## armored_car

Final target:

```text
HP:
300 -> approximately 400

CP:
3 -> 4

Primary weapon:
autocannon_25
damage/effective primary output +15%

Armour KEEP
Pen KEEP
speed KEEP
capture KEEP
```

Do NOT buff:
- coax/secondary MG if any;
- death explosion.

If `autocannon_25` is shared with unrelated units, use a vehicle-specific multiplier or variant so only `armored_car` receives this +15%.

---

## scout_jeep

Final:

```text
HP +30%

Primary weapon:
main scout/light direct-fire weapon +10%

CP:
+1 only if current base CP <= 2

vision KEEP
capture KEEP
speed KEEP
armour KEEP
```

Do not buff auxiliary/self-defense MG separately if it is not the actual main weapon.

---

## rocket_technical

Final:

```text
HP +35%
CP +1
```

Primary weapon:

```text
technical_rockets
raw damage +15%
```

KEEP:
- rocket count;
- splash;
- reload/cooldown;
- range;
- projectile speed from projectile master.

Do not buff any cab/self-defense MG.

---

## zu23_technical

Final:

```text
HP +35%
CP +1
```

Primary weapon:

```text
zu23
damage +20%
```

KEEP:
- Pen;
- range;
- cadence unless inherited scaling requires a unit-specific output multiplier;
- projectile speed.

Do not buff unrelated secondary MG.

---

## recoilless_jeep

Final:

```text
HP +30%

CP:
3 -> 4
```

Primary weapon:

```text
recoilless_106
damage = 314 KEEP
cooldown = 9.524 s KEEP
Pen = 4
```

Do NOT apply a generic cheap-unit +damage multiplier here.

This weapon was already rebased from the older 220 damage value.

---

# 3. LIGHT TANK

Final:

```text
HP +18%

CP:
+1 only if base CP <= 5
otherwise KEEP
```

Primary weapon:

```text
light_tank main cannon
damage +10%
```

Apply only to the actual main cannon ID mounted by `light_tank`.

KEEP:
- secondary/coax MG;
- Pen;
- armour;
- speed.

If its main cannon is shared with another tank that should not receive the buff, create a `light_tank` weapon variant.

---

# 4. IFV

Final:

```text
HP +12%
CP KEEP
armour KEEP
```

Primary weapon:

```text
ifv_30
damage +8%
```

ATGM:

```text
Pen = 4
damage KEEP
```

Do NOT buff:
- `mg_coax`;
- secondary HMG;
- ATGM damage;
- secondary utility weapons.

This is an anti-light/medium sustained-fire buff, not an anti-heavy buff.

---

# 5. WHEELED GUN / WHEELED TANK DESTROYER

Final:

```text
HP +10%
CP KEEP
Pen 4 KEEP
```

Primary weapon:

```text
gun_105_wheeled
damage +5%
```

Do NOT buff:
- `mg_coax`;
- `hmg_roof`;
- secondary MGs.

Do not raise this platform to Pen 5.

---

# 6. STANDARD TANK DESTROYER

Final total buff versus original pre-pass baseline:

```text
HP +10% total
CP KEEP
Pen 4 KEEP
```

Primary weapon:

```text
gun_105_long
damage +5%
```

Do not stack the previous +5% HP and this +10% as separate multipliers.

Final intended total HP gain is +10% from original baseline.

Do NOT buff:
- coax MG;
- roof MG;
- secondary weapon.

---

# 7. ELITE / SPECIALIST TANK HUNTERS

Previous decisions remain:

## elite_tank_destroyer

```text
gun_105_apfsds
Pen 5
damage KEEP
```

No new +5/+10% damage from this addendum.

## laser_tank

```text
focus_laser
Pen 5
damage 14
cooldown KEEP
ramp KEEP
```

No additional damage buff.

## railgun_truck

```text
railgun
Pen 5
damage KEEP
reload KEEP
```

No extra mid-tier damage multiplier.

These already received specialist-role buffs.

---

# 8. FLAME TANK

Final total versus original baseline:

```text
HP +12%
CP KEEP
armour KEEP
```

Primary weapon:

```text
flamethrower
damage +5%
```

Do NOT buff:

```text
mg_coax
```

Fire damage-type multipliers remain unchanged.

---

# 9. FPV CARRIER

Final:

```text
HP +12%
CP KEEP
```

Primary role weapon/system:

```text
fpv_swarm
damage KEEP
launch cadence KEEP
```

Do not buff drone payload damage.

Reason:
top-attack / roof-armour resolution already makes this role stronger.

Self-defense HMG:
KEEP.

---

# 10. AA VEHICLE

Final:

```text
HP +12%
CP KEEP
```

Primary AA gun:

Use the actual main gun mounted by `aa_vehicle`.

Apply:

```text
primary AA gun damage +8%
```

If the main gun is `twin_30_flak`, `twin_35_ahead`, or another ID, apply the +8% only for the `aa_vehicle` primary role output.

Secondary missile:

```text
sam
damage KEEP
```

Do NOT increase SAM damage.

Do not globally buff the weapon family if shared by towers/elite units; use unit-specific scaling/variant where necessary.

---

# 11. SAM LAUNCHER

Final:

```text
HP +10%
CP KEEP
```

Primary SAM weapon:

```text
damage KEEP
Pen KEEP
```

Projectile speed follows latest missile master.

Do not buff SAM launcher DPS in this pass.

---

# 12. CHEAP / MID SUPPORT VEHICLES

Examples:
- command vehicle;
- EW jammer;
- supply vehicle;
- ammo carrier;
- engineer support;
- mine layer.

Do not apply generic damage buffs.

If current CP <=5 and survivability is clearly poor:

```text
HP +15–20%
```

If mid-tier:

```text
HP +10–15%
```

CP generally KEEP unless the unit becomes clearly too efficient in utility/CP regression.

---

# 13. CHEAP FIRE SUPPORT VEHICLES

Do NOT apply generic low-cost +damage multipliers to:

- mortar_carrier;
- artillery;
- MLRS;
- heavy rocket artillery;
- ballistic launcher;
- cruise launcher.

They use the dedicated fire-support balance rules already defined.

If a cheap fire-support chassis is excessively fragile:

```text
HP +10–15% maximum
```

Do not increase frontline durability further.

---

# 14. RECON DRONE

Final:

```text
HP +20%
CP KEEP unless base CP <=5
```

If base CP <=5:

```text
CP +1
```

Primary weapon:

```text
recon_missile
damage KEEP
Pen 3 KEEP
```

Do not buff its weapon damage.

This is primarily a reconnaissance / scout-artillery hunter.

---

# 15. STRIKE DRONE

Final:

```text
HP +18%
```

If base CP <=7:

```text
CP +1
```

Primary ground-attack weapon:

Apply:

```text
primary strike-drone ground weapon damage +10%
```

Identify the actual primary weapon ID at runtime/canonical data and report it explicitly.

Do NOT buff:
- AAM;
- self-defense weapon;
- unrelated drone secondary.

If the primary weapon is shared with another platform, use a strike-drone-specific variant or outgoing multiplier.

---

# 16. SCOUT HELICOPTER

Final:

```text
HP +18%
```

If base CP <=7:

```text
CP +1
```

Primary ground weapons:

```text
main gun +8%
primary unguided rocket package +8%
```

Use the actual mounted weapon IDs.

Likely classes may include:
- helicopter gun;
- scout rocket family.

Explicitly report the IDs changed.

Do NOT buff:
- Stinger/AAM secondary;
- flare;
- unrelated missile.

If only one ground weapon is actually the main offensive weapon, apply +8% only to that one rather than blindly buffing every secondary slot.

---

# 17. ATTACK HELICOPTER

Keep previous aircraft pass.

Final:

```text
HP +15%
CP KEEP
```

Ground-attack weapons:

```text
main cannon +10%
main rocket package +10%
main tactical ground missile +10% damage maximum
```

BUT:
Do not double-buff any weapon that already received a prior explicit +8–10% aircraft-ground-weapon buff.

Final target is approximately +10% versus original baseline, not +10% on top of +10%.

Do NOT buff:
- Stinger/AAM;
- flares.

Bomb rules do not apply.

---

# 18. FIGHTER JET

Refined final:

```text
HP +12%
CP KEEP
```

Weapons:

```text
AAM damage KEEP
fighter cannon damage KEEP
```

Do not apply generic aircraft +10% ground damage unless this fighter has a clearly separate ground-attack payload.

Air-superiority role should remain the reason to buy it.

---

# 19. ATTACK JET

Final:

```text
HP +15%
CP KEEP
```

Primary ground-attack weapons:

```text
jet_cannon +8–10%
S-8 / main rocket package +8–10%
Kh-29 or equivalent main ground missile +8–10%
```

Do not double-stack old aircraft buffs.

Final total increase should remain approximately +8–10% versus original baseline for each eligible ground weapon.

Bomb payload uses the separate bomb balance:

```text
conventional bomb ×1.25
guided/JDAM ×1.20
heavy bomber conventional ×1.30
```

Do NOT also apply aircraft +10% to bomb damage.

AAM:

```text
KEEP
```

---

# 20. STEALTH FIGHTER / OTHER MEDIUM AIRCRAFT

For medium combat aircraft not separately defined:

```text
HP +12–15%
CP KEEP
```

Weapon rule:

- air-superiority weapon: KEEP;
- dedicated ground-attack primary: +8–10%;
- bomb: use bomb rule only;
- defensive gun/secondary: KEEP.

Do not blanket-buff every weapon slot.

---

# 21. HEAVY BOMBER / HEAVY GUNSHIP

Keep previous master values.

Heavy bomber:

```text
HP +20%
bomb payload according to bomb rules
other weapons KEEP unless already explicitly listed
```

Heavy gunship / twin rotor:

```text
HP +15%
```

Do not add another generic mid-aircraft buff.

---

# 22. TOWER FINAL CURVE

Replace previous Large-tower HP +30% target with:

```text
Small combat tower:
HP +20%
primary combat weapon damage +8%

Medium combat tower:
HP +25%
primary combat weapon damage +10%

Large combat tower:
HP +25%
primary combat weapon damage +10%

Heavy/special fortress-style tower:
HP +20%
primary combat weapon damage +5–10% only if classified direct combat
```

Do not buff every secondary weapon.

Do not automatically buff defensive MGs mounted on a tower.

---

# 23. MG BUNKER

Final:

```text
HP +20%
```

Primary weapon:

```text
mg_bunker main weapon
damage +10%
```

For variants:
- flame variant: buff only its main flame weapon if classified combat;
- twin variant: buff only its main twin weapon.

Do not propagate to unrelated MG families outside these bunker variants.

---

# 24. ROCKET TURRET

Final:

```text
HP +25%
```

Primary weapon:

```text
rocket_turret main rocket weapon
damage +10%
```

For variants:
- cluster;
- guided;

apply +10% only to the primary rocket payload if the variant is intended as an equivalent combat branch.

KEEP:
- splash unless separately changed by fire-support/cluster rules;
- reload;
- range.

Avoid double-buffing cluster coverage.

---

# 25. MEDIUM GUN TURRET

Final:

```text
HP +25%
```

Primary direct-fire cannon:

```text
damage +10%
```

Do NOT buff:
- coax/self-defense MG;
- utility secondary.

---

# 26. HEAVY / LARGE GUN TURRET

Final:

```text
HP +25%
```

Primary heavy cannon:

```text
damage +10%
```

No armour buff.

No secondary MG buff.

---

# 27. MISSILE BATTERY / SAM TOWERS

Final:

```text
HP +25% if Large
```

Missile damage:

```text
KEEP
```

Includes:
- normal missile battery;
- LRR variant;
- PAC-3 variant;
- equivalent SAM tower branches.

Projectile speeds use latest missile master.

Do not apply generic +10% tower damage to SAM missiles.

---

# 28. AA GUN TOWERS

HP according to tower size.

Primary AA gun:

```text
damage KEEP
```

Previous rule remains:
AA gun towers gain durability, not extra DPS.

Do not accidentally inherit the generic combat-tower +8/+10% damage multiplier.

---

# 29. C-RAM / LASER POINT DEFENCE

Final:

```text
HP +15–20%
damage KEEP
```

Do not increase interception DPS through this rebalance.

---

# 30. UTILITY TOWERS

Examples:
- EW;
- radar;
- flare;
- targeting;
- drone-net utility.

Final:

```text
HP +15%
combat damage KEEP / none
```

No generic damage buff.

---

# 31. SHIELD TOWER

Keep previous:

```text
body HP +10%
dome/ward HP KEEP
recharge KEEP
```

No generic tower +25% HP.

No weapon buff unless it has a distinct combat weapon explicitly balanced elsewhere.

---

# 32. EXPLICIT UNCHANGED ENTITIES

Continue to keep these unchanged unless separate regression proves otherwise:

```text
coastal_battery
bunker_shelter_tower
blast_wall
bulwark_post
```

`wheeled_gun` is no longer globally unchanged because this addendum explicitly gives it:
- HP +10%;
- main gun damage +5%;
- Pen4 KEEP.

---

# 33. DO NOT DOUBLE-APPLY BUFFS

Before implementation, build an application ledger for every affected unit:

```text
unit
original HP
previous approved HP multiplier
new final intended HP multiplier
primary weapon
previous approved weapon multiplier
new final intended weapon multiplier
CP old
CP final
```

Always apply the **final total versus original baseline**, not cumulative multipliers from every prompt.

Examples:

```text
Flame Tank:
old prompt +8% HP
new final +12% HP
=> final = original ×1.12
NOT original ×1.08 ×1.12

Attack Helicopter:
old ground weapon +10%
new says +10%
=> final remains original ×1.10
NOT ×1.21
```

---

# 34. PRIMARY-WEAPON AUDIT

For every damage buff in this addendum, report the exact weapon ID.

Required report format:

```text
unit_id
primary role
primary weapon ID
old damage
new damage
secondary weapons
secondary weapons changed? yes/no
reason
```

All secondary weapons should normally report:

```text
changed = NO
```

unless this addendum explicitly names them.

Examples that must be visible in final report:

```text
armored_car -> autocannon_25
rocket_technical -> technical_rockets
zu23_technical -> zu23
recoilless_jeep -> recoilless_106 (damage unchanged)
light_tank -> exact main cannon ID
ifv -> ifv_30
wheeled_gun -> gun_105_wheeled
tank_destroyer -> gun_105_long
flame_tank -> flamethrower
aa_vehicle -> exact primary AA gun
strike_drone -> exact primary ground weapon
scout_heli -> exact main gun / rocket ID changed
attack_helicopter -> exact cannon/rocket/ground-missile IDs
attack_jet -> jet_cannon / rocket / ground missile IDs
tower IDs -> exact primary tower weapon IDs
```

---

# 35. REGRESSION — VALUE PER CP

After all changes calculate for each combat vehicle:

```text
HP / CP
primary DPS / CP
effective DPS vs intended target / CP
useful combat lifetime / CP
```

Use three opponent types where relevant:

```text
Light / Armour1–2
Medium / Armour3
Heavy / Armour4–5
```

Do not judge specialist units on raw DPS only.

---

# 36. CHEAP VS MID CURVE ACCEPTANCE

Check representative comparisons:

```text
armored_car vs IFV
light_tank vs IFV
recoilless_jeep vs wheeled_gun
wheeled_gun vs standard TD
standard TD vs elite TD
cheap AA vs aa_vehicle
recon drone vs strike drone
scout heli vs attack heli
small tower vs medium tower vs large tower
```

Acceptance:

- cheap units should be worth fielding;
- mid-tier should remain more reliable per individual unit;
- premium specialists should retain stronger niche performance;
- cheap spam must not dominate every matchup.

---

# 37. BOSS SURVIVABILITY TESTS

Test cheap/mid units against:

```text
boss MG/autocannon
small boss missile
secondary rocket
edge splash
heavy direct cannon
heavy cruise/ballistic
T4/T5 attack
```

Desired:

Cheap unit:
- may survive small incidental hit / edge splash;
- should usually die to a direct heavy boss attack.

Mid unit:
- should survive more incidental/small secondary pressure;
- may still die to major direct boss weapon.

Do not globally nerf boss damage to achieve this.

Use the vehicle HP buffs, slower boss projectiles, positioning, and readable telegraphs.

---

# 38. CAMPAIGN IMPACT AUDIT

Cheap and mid canonical IDs are used by campaign AI, fixed decks and scripted militia.

Audit all missions using changed IDs, especially:

```text
rocket_technical
zu23_technical
scout_jeep
armored_car
light_tank
ifv
wheeled_gun
attack_helicopter
strike_drone
recon_drone
```

Do not automatically create campaign-only nerfs.

First measure encounter strength after canonical changes.

---

# 39. FINAL IMPLEMENTATION REPORT

Report:

1. every changed unit;
2. original HP -> final HP;
3. original CP -> final CP;
4. exact primary weapon ID;
5. original primary damage -> final primary damage;
6. every secondary weapon and confirmation whether it changed;
7. final Pen;
8. final HP/CP;
9. final primary DPS/CP;
10. campaign encounters materially affected;
11. tower primary weapon IDs changed;
12. confirmation SAM/AA/utility exceptions were respected;
13. confirmation no coax/HMG/self-defense weapons were accidentally buffed;
14. confirmation no previously approved multiplier was double-applied.

This addendum overrides conflicting older cheap/mid-tier recommendations.
</pasted_content id="e0cc">

