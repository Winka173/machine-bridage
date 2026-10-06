# 06/10 owner prompt (verbatim): balance v2 + boss missile flight-feel addendum

sửa cho tôi cái này trước, xong update bản window, dừng các task đang làm và tiếp tục lại sau khi xong

<pasted_content id="e0cc">
Implement the latest Machine Brigade balance pass using the decisions below as the **final source of truth**.

IMPORTANT:
- Current XLSX/MD exports may still contain stale values.
- Do not trust stale exports over this prompt.
- Modify canonical/runtime source first.
- Then regenerate all generated XLSX/MD/reports.
- Do not manually patch generated outputs as authority.
- Preserve all previously locked combat rules.
- **Boss armour must not be changed.**

# 1. LOCKED COMBAT RULES

Use the approved penetration tables.

Normal penetration:

```text
penetration - armour

>= +2 : 1.20
+1    : 1.00
0     : 0.85
-1    : 0.65
-2    : 0.40
-3    : 0.15
<= -4 : 0.08
```

Top Attack uses roof armour only and replaces the normal penetration lookup:

```text
>= +2 : 1.15
+1    : 1.10
0     : 0.95
-1    : 0.75
-2    : 0.50
-3    : 0.25
<= -4 : 0.12
```

Do not multiply normal Pen × Top Attack.

Relevant structure multipliers remain:

```text
HighExplosive vs Structure = 1.60
Thermobaric vs Structure = 2.00 replacing HE 1.60
```

# 2. FINAL PROJECTILE / MISSILE SPEEDS

Use effective runtime speed as authority after inheritance/override resolution.

## Cruise missiles

Generic cruise baseline:

```text
65–70 m/s
```

Do not globally slow cruise below this unless there is a concrete bug.

## Tactical / ATGM

```text
hellfire_standoff         70
hellfire_volley           70
drone_missile             70
gun_launched_atgm         70
TOW family                70
Kornet family             70
Konkurs family            ~60

Vikhr                     75
Maverick                  75
Kh-29                     75
APKWS                     80
```

Top-attack variants do not get extra speed just because they are top attack.

## Anti-ship

```text
anti_ship_missile = 80 m/s effective
```

Audit the full inheritance/runtime pipeline because this weapon has shown inconsistent raw/effective values in older exports.

## AAM / SAM

```text
Stinger ATAS            90
Igla-V                  90
R-60                    95
AIM-9 / WVR            100

generic SHORAD         100
Tamir                  105
Pantsir 57E6           110

AMRAAM                 120
player Buk             120
player Patriot         130
S-400 / 48N6           115   <-- latest visual-feel correction
```

The long-range SAM was still visually too fast, so its final target is now:

```text
sam_48n6 / long_sam = 115 m/s effective
```

Damage/Pen remain unchanged.

For long-range SAM fragmentation footprint:

```text
splash ×1.25
cap around 5–6 m
```

Do not turn it into an anti-ground explosive weapon.

## Boss-specific intentional exceptions

Keep:

```text
boss/ship sam_post        80
Nemesis sam_battery       95
boss Grad/rocket override 65
boss cruise               65–70
```

Do not normalize these upward.

# 3. TACTICAL BALLISTIC LAUNCHER

Current tactical ballistic projectile is too fast.

Final:

```text
ballistic_missile
projectile speed: 200 -> 90 m/s
damage: KEEP 630
splash: 10 -> 14 m
```

Do not increase raw damage.

Increase impact/VFX scale to visually match the larger footprint, roughly +25–35% if the presentation system requires an explicit scale.

# 4. DRONE MOTHERSHIP / SWARM CARRIER

The drone swarm itself remains slow and readable.

Keep drone/Lancet-type flight speed as currently intended.

The fast-feeling weapon is the cruise missile secondary.

Create or use a dedicated mothership variant rather than globally changing all JASSM users.

Target:

```text
jassm_swarm_carrier
speed = 60 m/s
damage = inherit current JASSM damage
Pen = KEEP
splash = current ×1.20
cooldown/load = KEEP
```

Generic JASSM remains in the normal cruise 65–70 band.

# 5. CRUISE MISSILE EXPLOSION FOOTPRINT

Cruise missile impact currently feels too small.

Gameplay readability takes priority over previous real-warhead scaling where that scaling made the explosion visually underwhelming.

Do not increase cruise damage in this pass; increase footprint only.

Final guidance:

```text
light/small cruise         ~8 m splash
standard cruise            ~12 m splash
heavy cruise               ~14 m splash
boss/strategic cruise      ~14–16 m splash
```

Specific targets:

```text
jassm                     10 -> 12 m
generic ground cruise     -> 12 m
air_cruise_missile        -> 12 m
Kh-101/Kalibr-like normal -> 12 m

hydra_club_s              6.5 -> 10 m
nyx_tomahawk-like         8.5 -> 11 m
boss heavy cruise         ~14 m where currently around 10
```

Do not blindly change every boss cruise to the same radius.

Preserve weapon identity and existing mission design.

IMPORTANT:
Any warning circles, inner/core zones, outer/edge rings and VFX footprint must be updated to match the new actual damage radius.

Do not leave stale warning markers from the previous 6.5 m cruise-radius pass.

# 6. AIRCRAFT ROCKET / ARTILLERY SPEEDS

Keep the latest approved values:

```text
aircraft rocket family    ~95
jet rockets               100
boat rockets               90
APKWS                      80

120 mm mortar              45
AMOS                       45
boss mortar                40
heavy mortar               35–40

medium howitzer            55
long artillery             60
heavy artillery            65
very large indirect        65–70

TOS                        65
technical rockets          75
Grad                       80
Smerch                     80
GMLRS                      85
```

Guided artillery may be only about +5–10 m/s over its base family.

# 7. PROJECTILE VALIDATOR

Do not raise canonical projectile speeds just to make old validator warnings disappear.

Use class-aware validation.

Statuses:

```text
HARD_FAIL
YELLOW_FEEL
PASS_INTENTIONAL_SHORT_RANGE
```

Reason codes:

```text
CANONICAL_SHORT_RANGE
INHERITANCE_MISMATCH
TOO_FAST_FOR_CLASS
TOO_SLOW_FOR_CLASS
INTENTIONAL_BOSS_OVERRIDE
```

Use typical/max range as primary validation.

Half-range is supporting data, not an unconditional fail.

Recommended hard-fast thresholds:

```text
ATGM/tactical missile:
hard fail only if <0.25 s at half range AND <0.45 s at max/typical range

Short AAM/MANPADS:
hard fail <0.18 s typical

Medium/long SAM/AAM:
hard fail <0.22 s typical

Rocket artillery:
hard fail <0.45 s max

Mortar/howitzer:
hard fail <0.60 s actual-arc max

Heavy 240 mm mortar:
hard fail <0.75 s actual-arc max
target may extend to ~2.2 s
```

# 8. BOMB BALANCE

Final:

```text
conventional aircraft bomb      damage ×1.25
heavy bomber conventional       damage ×1.30
guided/JDAM/stealth bomb        damage ×1.20
```

Aircraft cluster-bomb rule is currently N/A because no aircraft carries a cluster bomb.

Do not automatically apply the aircraft cluster-bomb rule to `cluster_strike`.

`airstrike`:
- if it ultimately uses the same canonical conventional bomb payload, it should receive the bomb buff once through the canonical payload.
- do not double-buff again at the support layer.

`cluster_strike`:
- KEEP unchanged for now.
- only rebalance separately if support-value regression proves it weak.

# 9. AIRCRAFT BALANCE

Final HP buffs:

```text
fighter / attack jet / stealth fighter   HP ×1.15
attack helicopter / scout helicopter     HP ×1.15
heavy gunship / twin rotor               HP ×1.15
heavy bomber                             HP ×1.20
large airborne carrier/support           HP ×1.15
```

Do not globally increase aircraft armour.

Non-bomb aircraft ground attack weapons:

```text
damage approximately ×1.08–1.10
```

AAM damage remains unchanged.

# 10. GROUND VEHICLE BALANCE

Final:

```text
MBT
HP ×1.05
damage KEEP
armour KEEP

Heavy Tank
HP ×1.08
damage ×1.05
armour KEEP

Titan
KEEP all

Twin Tank
KEEP

IFV
KEEP

Light Tank / Armored Car / Recon
KEEP

standard Tank Destroyer
HP ×1.05
damage KEEP
Pen hierarchy below

Flame Tank
HP ×1.08
damage KEEP

Breacher / Bulldozer / Engineer assault
HP ×1.10
wall modifier KEEP

Artillery / Mortar / MLRS vehicles
HP KEEP
```

# 11. ANTI-ARMOUR SPECIALIST PENETRATION HIERARCHY

Pen 5 is reserved for true specialist Armour4–5 / superheavy / boss killers.

Final hierarchy:

```text
wheeled_gun                  Pen 4 KEEP

standard tank_destroyer
gun_105_long                 Pen 4 KEEP

elite_tank_destroyer
gun_105_apfsds               Pen 4 -> 5

laser_tank
focus_laser                  Pen 4 -> 5

railgun_truck
railgun                      Pen 4 -> 5

normal MBT guns              mostly Pen 4

recoilless_jeep
recoilless_106               Pen 3 -> 4
damage 220 KEEP
```

Do not give Pen 5 to every expensive or elite vehicle.

# 12. LASER TANK DESTROYER

The unit explicitly presents itself as a Heavy/Tank/Boss specialist, but the old weapon underdelivered.

Final:

```text
focus_laser
Pen 4 -> 5
damage 12.5 -> 14
cooldown KEEP 0.1
ramp KEEP
range KEEP
damage type Energy KEEP
```

Do not additionally inflate beam ramp or cooldown in the same pass.

# 13. RAILGUN TRUCK

Final:

```text
railgun
Pen 4 -> 5
damage KEEP
reload KEEP initially
```

Only increase reload later if post-patch simulation proves the new Pen 5 causes overperformance.

# 14. ELITE TANK DESTROYER

Final:

```text
gun_105_apfsds
Pen 4 -> 5
damage KEEP
```

Standard `gun_105_long` remains Pen 4.

# 15. RECOILLESS JEEP

This is a true TankHunter but currently has only Pen 3.

Final:

```text
recoilless_106
Pen 3 -> 4
damage 220 KEEP
```

Keep its weak chassis and immobile firing constraints.

# 16. RECON DRONE

Do not turn recon drone into an anti-heavy platform.

Final:

```text
recon_missile
Pen 3 KEEP
damage KEEP
```

Its role remains Scout/Artillery hunting and reconnaissance.

# 17. IFV ATGM

Audit the runtime value.

The IFV's dedicated ATGM should be:

```text
Pen 4
```

If current runtime effective Pen is below 4 due to stale inheritance, fix to Pen 4.

Do not raise to Pen 5.

# 18. SIEGE TANK DIRECT GUN

The direct 105 mm siege gun is not a superheavy killer.

Final:

```text
siege_gun_105
Pen KEEP 2
damage KEEP
```

Its identity is siege/structure pressure and HE utility, not TD competition.

# 19. ANTI-SHIP PLATFORM

Final:

```text
anti_ship_missile
Pen 4 KEEP
speed = 80
damage KEEP
```

Do not turn the missile boat into a general-purpose armour killer.

# 20. TOWERS

Final:

```text
Small combat tower:
HP ×1.20
damage ×1.08

Medium combat tower:
HP ×1.25
damage ×1.10

Large/heavy tower:
HP ×1.30
damage ×1.10

AA gun tower:
HP by size
damage KEEP

SAM tower:
HP by size
damage KEEP

C-RAM / laser / point defence:
HP ×1.15–1.20
damage KEEP

EW/radar/flare utility:
HP ×1.15
```

Do not globally buff armour.

The following previously unnamed units remain unchanged in this pass unless a separate regression fails:

```text
coastal_battery
bunker_shelter_tower
wheeled_gun
blast_wall
bulwark_post
```

Do not infer class-wide buffs for them automatically.

# 21. STRUCTURES

Final:

```text
airfield                HP ×1.20
repair_bay              HP ×1.20
logistics_station       HP ×1.20
fire_control_centre     HP ×1.25
radar/EW/targeting      HP ×1.20
vehicle_hangar          HP ×1.20
aircraft_hangar         HP ×1.20
cp_relay-like utility   HP ×1.20

destructible super gun  HP ×1.15

HQ                      HP ×1.05
Spawn Bastion           KEEP
Walls/HESCO/T-wall      KEEP

Shield tower body       HP ×1.10
dome/ward HP            KEEP
shield recharge         KEEP
```

Do not buff wall HP.

# 22. STRUCTURE REPAIR

If structure/tower repair uses % max HP/s:

```text
KEEP
```

If repair uses flat HP/s:
audit effective repair time.

If the new HP buffs make repair too weak, allow:

```text
structure/tower repair throughput +10–15%
```

Do not globally buff vehicle repair.

# 23. BOSS BALANCE

Boss armour:

```text
KEEP ALL VALUES
```

Main boss hull:

```text
HP ×1.08
```

Mini-boss hull:

```text
HP ×1.05
```

Nyx:

```text
outgoing damage ×1.10
```

Scylla:

```text
outgoing damage ×1.08
```

Mobile Fortress:

```text
damage KEEP
```

Nemesis:

```text
damage KEEP
```

Do not pre-nerf.

Monster / Moloch / Leviathan / Kraken / Earth Borer:

```text
damage KEEP
```

If boss-part HP is derived from hull HP, do not add another generic part-HP multiplier.

# 24. FIRE SUPPORT

Final:

```text
120 mm mortar
damage ×1.10

AMOS
damage ×1.10
salvo/cooldown KEEP

240 mm mortar
damage KEEP
splash 9 -> 10

standard/long/heavy howitzer
damage KEEP
coverage/splash ×1.10

guided artillery
damage KEEP
accuracy remains its main advantage

standard MLRS/GMLRS
damage KEEP
effective coverage +8–10%

cluster MLRS
bomblet damage KEEP
coverage +10%

Grad/Smerch/heavy rockets
damage KEEP

TOS / thermobaric
KEEP ALL COMBAT STATS

ballistic launcher
raw damage KEEP

ground cruise
damage KEEP
```

# 25. ARTILLERY BARRAGE SUPPORT

Final:

```text
~+10% total strike value
```

Prefer:
- slightly more shells,
or
- slightly better coverage.

Do not simultaneously raise shell count and shell damage unless test proves necessary.

Do not accidentally propagate this buff into unrelated scripted enemy barrage events.

# 26. FIRE SUPPORT LOGISTICS

Do not increase base magazines globally.

If resupply becomes a limiting problem after the changes, allow:

```text
artillery/MLRS resupply throughput +10%
```

only via ammo carrier/logistics infrastructure.

# 27. COUNTER-BATTERY

Do not add hidden bonus damage versus artillery.

Counter-battery strength should come from:
- detection after firing,
- target priority,
- firing-position intelligence,
- decision speed,
- shoot-and-scoot behavior.

# 28. FIRE SUPPORT TARGET VALUE

Heavy MLRS / ballistic / heavy artillery / major support strikes should not waste salvos on lone low-value targets.

Use:
- total target CP/value in blast,
- objective importance,
- tower/structure value,
- concentration,
- predicted overkill,
- reload opportunity cost.

# 29. PROJECTILE SPEED GEAR

Keep:

```text
ProjectileSpeed substat +4/+6/+8/+10%
BuildCap 30%
```

Test all relevant projectiles both naked and at legal max-cap gear.

# 30. MANDATORY REGRESSION

Run:

## Ground
- MBT vs Heavy
- Heavy vs standard TD
- elite TD vs Armour5
- laser tank vs Armour4/5/boss
- railgun vs Armour4/5
- recoilless jeep ambush performance
- IFV ATGM vs medium/heavy
- breacher vs wall

## Air
- attack helicopter vs SHORAD
- attack jet vs SAM
- heavy bomber survivability
- sortie value after bomb buff

## Missiles
- ballistic launcher max/half/min flight time
- long-SAM flight feel
- drone mothership cruise
- JASSM standard
- cruise explosion footprint
- warning marker match

## Towers/Structures
- normal assault squad TTK
- bomber vs tower
- artillery vs tower
- TOS vs fortification
- utility-building survivability

## Boss
- main boss TTK
- mini-boss TTK
- Nyx/Scylla pressure
- Nemesis pressure
- boss-part survivability

## Fire support
- 120 mortar
- AMOS
- 240 mortar
- howitzer coverage
- MLRS coverage
- artillery barrage
- resupply cadence

## Defences
- APS
- CIWS
- flare
- jammer
- intercept prediction
- AI lead
- proximity fuze

# 31. PIPELINE AUDIT

For all affected weapons, report:

```text
canonical source
→ family inheritance
→ variant override
→ runtime effective
→ generated export
```

Mandatory mismatch checks:

```text
apkws_rocket
anti_ship_missile
Kornet variants
long_sam / sam_48n6
player Buk
player Patriot
boss sam_post
Nemesis sam_battery
boss Grad family
ballistic_missile
jassm
jassm_swarm_carrier
focus_laser
gun_105_apfsds
railgun
recoilless_106
IFV atgm
```

# 32. REGENERATE OUTPUTS

After canonical/runtime changes, regenerate all relevant generated outputs including:

```text
01_chien_dau.xlsx
01_chien_dau.md
02_boss.xlsx
02_boss.md
03_can_cu.xlsx
03_can_cu.md
04_che_do_kinh_te_ai.xlsx
04_che_do_kinh_te_ai.md
07_hinh_anh_am_thanh_model.xlsx/.md if timing/VFX derived
09_ai.xlsx
09_ai.md
10_trang_bi.xlsx/.md if effective reports change
00_index.xlsx
README.md
CHANGES.md
```

Also regenerate:
- projectile flight audit
- weapon audit
- boss DPS/TTK audit
- tower/structure durability audit
- fire-support audit
- APS/CIWS regression
- AI lead/intercept regression
- warning-radius audit
- stale-value scan

# 33. FINAL REPORT

Provide a detailed implementation report containing:

1. every canonical file changed;
2. every affected ID;
3. exact old -> new values;
4. final runtime effective values;
5. final projectile speeds;
6. final Pen values for all specialist anti-armour weapons;
7. cruise splash values by family;
8. ballistic missile speed/splash;
9. long-SAM speed/splash;
10. drone-mothership cruise result;
11. laser TD result;
12. elite TD result;
13. railgun result;
14. recoilless jeep result;
15. IFV ATGM result;
16. boss HP application;
17. explicit confirmation boss armour was unchanged;
18. tower/structure results;
19. fire-support results;
20. flight-time min/half/max;
21. ProjectileSpeed gear max values;
22. APS/CIWS/flare/jammer regression;
23. AI lead/intercept regression;
24. warning-marker/radius audit;
25. structure repair audit;
26. fire-support resupply audit;
27. generated file list;
28. remaining validator HARD_FAIL items;
29. stale data/inheritance mismatches found.

Final implementation must prioritize the exact decisions in this prompt over stale numbers still present in old exports.
</pasted_content id="e0cc">

<pasted_content id="e0cc">
## ADDENDUM — BOSS MISSILE / ROCKET FLIGHT-FEEL AUDIT

In addition to all previous balance instructions, perform a dedicated audit of **all boss-fired missiles, rockets, cruise weapons, guided ordnance, VLS weapons, air-to-ground missiles, anti-ship missiles, tactical missiles and missile-like superweapons**.

Reason:
Several bosses, including Hyperion-like/boss missile platforms, still have missiles that visually travel far too quickly. Some boss weapons may be using stale family speeds, inherited player missile values, old raw projectile speeds, or boss-specific overrides that were never updated.

Do NOT assume existing boss projectile speeds are intentional just because they are currently in data.

### 1. Audit every boss missile source

Scan all main bosses, mini-bosses, variants, inherited boss frames and boss-mounted weapons.

Include at minimum:
- primary weapons;
- secondary weapons;
- mount weapons;
- VLS;
- boss `big_attack` weapons;
- salvo weapons;
- cruise weapons;
- phase-specific weapons;
- boss air-wing/launch weapons where the boss directly owns the projectile definition;
- inherited boss variants;
- hidden/alternate weapons used only in later phases;
- Hyperion and any Hyperion variants;
- naval bosses;
- airship/gunship bosses;
- mobile fortress/land bosses;
- train bosses;
- drone/mothership bosses.

For each boss projectile, trace:

```text
boss id
→ weapon/mount id
→ weapon family
→ inherited family speed
→ boss override
→ runtime effective projectile speed
→ effective range
→ min range if any
→ actual flight time at typical/max range
```

### 2. General boss missile design rule

Boss status must **not automatically increase projectile speed**.

Boss missiles should usually be:
- more damaging;
- larger;
- more numerous;
- more durable against interception if explicitly designed;
- better telegraphed;
- fired in more complex patterns;

but **not near-hitscan simply because they belong to a boss**.

The player should normally be able to visually perceive:

```text
launch
→ missile/rocket in flight
→ trail
→ approach
→ impact
```

For boss attacks with warning markers, the warning is not a substitute for visible projectile travel.

### 3. Target boss speed bands

Use these as gameplay targets, not real-world Mach speeds.

```text
boss tactical ATGM / direct guided missile:
~65–80 m/s

boss heavy tactical missile:
~75–90 m/s

boss rocket / barrage rocket:
~60–80 m/s

boss anti-ship missile:
~70–85 m/s

boss cruise missile:
~60–70 m/s

boss short-range SAM:
~80–100 m/s

boss medium/long SAM:
~85–115 m/s

boss mortar:
~35–45 m/s

boss indirect artillery:
~50–70 m/s
```

Existing intentional overrides remain valid unless the audit proves a specific visual problem:

```text
boss/ship sam_post      80 m/s
Nemesis sam_battery     95 m/s
boss Grad/rockets       65 m/s
boss cruise             ~65–70 m/s
```

### 4. Hyperion-specific requirement

Audit every missile/rocket/guided weapon fired by Hyperion.

Do not rely only on the visible main weapon ID.

Check:
- inherited weapons;
- mount weapons;
- phase weapons;
- secondary arrays;
- big attack definitions;
- weapon-family speed;
- runtime effective speed.

If any Hyperion missile feels near-instant at normal combat range, reduce it into the appropriate class band above.

Do not change Hyperion boss armour.

Do not compensate by raising raw missile damage unless separate balance testing proves necessary.

### 5. Automatic boss missile outlier detection

Generate a boss projectile report and flag boss missiles when:

```text
effectiveSpeed > expected class band
```

or when:

```text
flightTimeAtTypicalRange < ~0.35 s
```

for tactical/barrage boss missiles, unless the weapon is explicitly intended as a very-fast intercept missile.

For heavy boss missiles / superweapon missiles, prefer roughly:

```text
~0.7–2.0 s visible flight time
```

after any pre-launch warning, depending on range and attack design.

Do not force every projectile into exactly the same flight time.

### 6. Do not blindly normalize by family

If a player weapon and boss weapon share a family, a boss-specific variant is allowed and preferred where necessary.

Example:

```text
player missile family
→ retain player balance

boss-specific missile variant
→ slower visual speed appropriate to boss encounter
```

Do not slow player weapons accidentally while fixing a boss.

Likewise, do not inherit a fast player SAM/ATGM speed into a boss weapon simply because both share the same real-world family.

### 7. Boss warning timing interaction

For every boss attack that has both a warning and a projectile:

separately report:

```text
PreLaunchWarning
ProjectileTravel
TotalReactionWindow
```

Do not treat these as one value.

If slowing a boss projectile makes total reaction time excessive, adjust:
1. warning timing;
2. launch delay;
3. attack cadence;

before restoring the missile to near-hitscan speed.

Do not reduce projectile visibility just to maintain old total reaction time.

### 8. Boss missile explosion footprint

During this audit also flag boss missiles whose impact footprint looks disproportionately small compared with:
- missile size;
- warning radius;
- visual effect;
- damage;
- role.

Do not automatically increase every boss missile splash.

Use rough identity hierarchy:

```text
small boss missile / ATGM:
0–3 m gameplay splash

SAM fragmentation:
~3–6 m

heavy tactical missile:
~8–14 m

boss anti-ship missile:
~8–14 m

boss cruise:
~10–16 m

ballistic/superweapon:
~14 m+ where appropriate
```

The warning marker must never be smaller than the actual gameplay damage area.

VFX should visually match the gameplay footprint.

### 9. Guided missile turning regression

After reducing boss missile speed, verify homing behavior.

Slower missiles with unchanged steering may become unrealistically agile.

Test:
- turn rate;
- terminal steering;
- overshoot;
- circling;
- 180-degree U-turns;
- minimum-range launches;
- target lead;
- moving targets;
- air targets;
- ships;
- interception.

If guidance becomes too strong, adjust:
1. turn rate;
2. steering acceleration;
3. terminal steering;
4. minimum range;
5. reacquisition;

rather than raising projectile speed back to the old excessive value.

### 10. APS / CIWS regression

Slower boss missiles spend more time inside interception envelopes.

Audit:
- APS;
- CIWS;
- point defence;
- intercept eligibility;
- acquisition delay;
- shots available per incoming missile;
- simultaneous salvo behavior.

Do NOT automatically nerf APS/CIWS.

If a boss missile becomes too easy to intercept, prefer:
1. boss projectile interception eligibility;
2. acquisition/track timing;
3. salvo density;
4. missile durability/intercept resistance if such a system already exists;
5. intercept probability;

before increasing missile speed.

### 11. Boss salvo readability

For missile barrages, ensure individual projectiles are visually separable.

Audit:
- salvo spacing;
- launch interval;
- trail overlap;
- synchronized impacts;
- staggered impacts;
- warning markers.

Do not fire an entire barrage in such a tight packet that slower projectiles visually merge into one blob.

### 12. Preserve these non-goals

Do NOT use this audit to:
- alter boss armour;
- globally increase boss HP;
- globally increase boss damage;
- change unrelated boss cannon speeds;
- slow direct kinetic shells;
- modify boss phase logic unless required by timing;
- rewrite boss weapon identity.

This is primarily a **flight-feel and projectile readability correction**.

### 13. Required boss missile audit output

Produce a table containing every boss missile-like weapon:

```text
Boss
Weapon ID
Mount/attack source
Projectile class
Old effective speed
New effective speed
Range
Min range
Typical flight time
Max-range flight time
Splash before
Splash after
Warning time
Total reaction window
Inheritance source
Reason for change / KEEP
```

Sort changed outliers first.

### 14. Acceptance criteria

The boss missile audit is complete only when:

- Hyperion missile speeds have been explicitly reviewed.
- No boss tactical/heavy missile is near-hitscan at normal combat distance without an intentional documented reason.
- No stale player-family speed is silently overriding an intended slower boss variant.
- All intentional boss-specific speed overrides are preserved.
- Boss warning and projectile travel are tracked separately.
- Slower boss missiles still guide correctly.
- APS/CIWS interaction is retested.
- Explosion footprint and warning radius visually agree.
- Boss armour remains completely unchanged.

Where exact values are not explicitly specified by previous balance instructions, choose the lowest speed that still keeps the boss attack threatening, readable and mechanically reliable within the target bands above.

Document every judgment call in the implementation report.
</pasted_content id="e0cc">

