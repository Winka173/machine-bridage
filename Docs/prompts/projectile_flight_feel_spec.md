# MACHINE BRIGADE — PROJECTILE FLIGHT FEEL MASTER SPEC
## Canonical balance and implementation specification for missile / rocket / artillery / naval projectile speed

**Status:** FINAL  
**Scope:** projectile speed, projectile flight-time feel, missile families, aircraft rockets, artillery shells, mortar, MLRS, boss projectiles, naval gun shells, warning timing, APS/CIWS regression, projectile-speed gear interaction, validator rules.  
**Supersedes:** earlier projectile-speed suggestions and any older per-ID speed recommendations that conflict with this file.

---

# 0. DESIGN GOAL

The current battlefield is spatially compressed compared with real-world distances.

Therefore:

> Do NOT balance projectile speed by copying real-world m/s.

The primary balance target is:

```text
time-to-target in game
```

The player should clearly experience:

```text
launch / muzzle event
→ projectile visible in flight
→ readable approach
→ impact
```

The game should avoid:

```text
muzzle flash
→ effectively instant damage
```

for missile, rocket-artillery and indirect artillery classes.

The intended feel is:
- direct tank/naval AP remains fast/snappy;
- missiles are visibly fast but not hitscan;
- rocket artillery has satisfying travel;
- mortar/howitzer visibly arcs;
- cruise missiles remain the slowest large guided missiles and already feel correct;
- drones and bombs remain mostly unchanged because their current travel feel is already good.

---

# 1. GLOBAL PRINCIPLES

## 1.1. Cruise missile baseline

Cruise missiles remain approximately:

```text
65–70 m/s
```

KEEP current cruise families unless a separate bug is found:
- JASSM
- Kh-101
- Kalibr
- generic ground cruise missile

These already create clear travel-time feel.

Other tactical missiles should generally remain faster than cruise missiles.

---

## 1.2. Projectile hierarchy

Target hierarchy:

```text
Cruise missile
    ~65–70

ATGM / Hellfire / Vikhr / Maverick
    ~75–85

Unguided aircraft rockets
    ~90–100

Short-range AAM / MANPADS
    ~105–115

SHORAD / medium SAM
    ~120–150

Long-range SAM
    ~160–170

Rocket artillery
    ~65–90

Mortar
    ~35–45

Howitzer / indirect artillery
    ~55–70

Direct tank / naval cannon
    faster than indirect artillery
```

This is not a realism table.
It is a gameplay-feel hierarchy.

---

# 2. TACTICAL MISSILES — FINAL VALUES

Final effective runtime targets:

```text
hellfire_standoff      80 m/s
hellfire_volley        80 m/s
drone_missile          80 m/s

vikhr                   85 m/s
maverick                80 m/s
kh29                    80 m/s
gun_launched_atgm       75 m/s
```

Ground direct ATGM:

```text
TOW family              75–80 m/s
Kornet family           75–80 m/s
Konkurs family          ~60 m/s
```

Do not reduce them further unless flight-time audit proves they remain too fast.

---

# 3. AIRCRAFT / HELICOPTER ROCKETS

The current 70–80 mm rocket family is too fast when effective runtime speed is around 180 m/s.

Final target:

```text
rkt_70_80 family:
    effective speed = 95 m/s
```

Applies to equivalent aircraft rocket systems such as:
- heli_rockets
- scout_rockets
- gunship_rockets
- s8_pods
- hind_rockets

Specific exceptions:

```text
jet_rockets     100 m/s
boat_rockets     90 m/s
```

Guided APKWS should not silently inherit an excessive family speed.

---

# 4. APKWS PIPELINE AUDIT

`apkws_rocket` showed a suspicious mismatch between raw and effective/projected values in earlier exports.

Mandatory audit:

```text
canonical raw
→ family inheritance
→ variant inheritance
→ normalization
→ runtime effective speed
→ generated xlsx/md value
```

Final intended effective APKWS speed:

```text
80–90 m/s
```

Prefer:

```text
85 m/s
```

unless inheritance design strongly requires using the 95 m/s base rocket family.

Do not accept:
```text
raw 45
→ effective 180
```

unless an explicit design rule documents why.

---

# 5. AIR-TO-AIR MISSILES

Final effective speeds:

```text
stinger_atas     105 m/s
igla_v           105 m/s
r60              110 m/s
wvr_aam          115 m/s
air_to_air       140 m/s   // AMRAAM-like medium-range family
```

These should remain visibly faster than ATGM and aircraft rockets.

---

# 6. SURFACE-TO-AIR MISSILES

Final effective speeds:

```text
generic SHORAD       120 m/s
Pantsir 57E6         130 m/s
Tamir                125 m/s
Buk family           145 m/s
Patriot family       165 m/s
S-400 / 48N6         170 m/s
```

Do not push long-range SAM back to 250–300 m/s in compressed game scale unless the map scale changes.

---

# 7. ANTI-SHIP MISSILE PIPELINE AUDIT

`anti_ship_missile` previously showed a major raw/effective mismatch.

Audit the same full pipeline as APKWS.

Target effective speed:

```text
90–100 m/s
```

Recommended default:

```text
95 m/s
```

Anti-ship missile should:
- be heavier/slower-feeling than high-end SAM;
- still be faster than cruise missile;
- remain visually trackable;
- give point defence a meaningful but not excessive engagement window.

Do not use a hidden family override that jumps to ~225 m/s without explicit documentation.

---

# 8. CRUISE MISSILES — KEEP

KEEP current effective values if approximately:

```text
JASSM              ~70 m/s
Kh-101             ~65 m/s
Kalibr             ~70 m/s
generic cruise     ~70 m/s
```

Do not slow them further from this task.

They already provide the desired satisfying flight feel.

---

# 9. BALLISTIC MISSILES

Do not automatically reduce ballistic missiles into cruise-speed territory.

If current ballistic flight time is already clearly visible and not hitscan:
- KEEP.

Balance by:
- trajectory;
- warning;
- travel time;
- impact scale.

Only reduce speed if validator shows unusually short in-game travel relative to its threat class.

---

# 10. MORTAR — FINAL SPEED STANDARD

Mortar must visibly arc.

Final family targets:

```text
standard 120 mm mortar      45 m/s
AMOS-like mortar            45 m/s
boss mortar                 40 m/s
very heavy/special mortar   35–40 m/s
```

The existing weapon-family semantics already describe mortar as:

```text
slow, high arc
```

The runtime should respect that identity.

Target max-range flight feel:

```text
roughly 1.0–1.6 s
```

depending on actual ballistic path.

---

# 11. HOWITZER / INDIRECT ARTILLERY

Final standard:

```text
medium field artillery      55 m/s
long-range artillery        60 m/s
heavy artillery             65 m/s
huge/coastal indirect       65–70 m/s
```

Example intended mapping:

```text
howitzer           55
howitzer_ext       60
howitzer_fixed     65
```

Exact IDs may differ.
Map by family/role rather than blindly by name.

---

# 12. GUIDED ARTILLERY SHELL

Guidance must not automatically make artillery shells dramatically faster.

Rule:

```text
guided artillery speed
=
base family speed
OR
base family speed + 5–10 m/s maximum
```

Example:

```text
155 mm indirect shell       60
155 mm guided shell         65
```

Do not use:

```text
60 → 150
```

just because `guided=true`.

Guidance advantage should come from:
- accuracy;
- target correction;
- target selection;
- lower spread;
not near-hitscan travel.

---

# 13. ROCKET ARTILLERY / MLRS

Final family targets:

```text
TOS-type rocket artillery       65 m/s
light technical rockets         75 m/s
Grad 122 mm                     80 m/s
Smerch 300 mm                   80 m/s
GMLRS / M30 / M31               85 m/s
boss rocket barrage             80 m/s
```

Target flight feel:
- clearly visible salvo;
- meaningful rocket trail;
- impact anticipation;
- not so slow that rockets appear to float.

---

# 14. BOSS PROJECTILES

Boss status must NOT automatically increase projectile speed.

Boss weapon should inherit family feel.

Recommended:

```text
boss tactical missile       90 m/s unless family says otherwise
boss rocket barrage         80 m/s
boss mortar                 40 m/s
boss indirect artillery     55–70 m/s
```

Boss superweapon may be slower when:
- long warning is intentional;
- visual travel is part of spectacle.

Do not increase boss projectile speed merely to make boss stronger.
Boss difficulty should come from:
- damage;
- pattern;
- targeting;
- phase;
- coverage;
- pressure;
not hidden near-hitscan travel.

---

# 15. BOSS WARNING VS TRAVEL TIME

Existing high-tier boss attacks already use substantial warning floors.

Do not accidentally double reaction time.

Separate:

```text
PreLaunchWarning
ProjectileTravel
TotalReactionWindow
```

For each boss attack define all three.

Avoid accidental pipeline:

```text
3.5 s warning
→ launch
→ 2.0 s projectile travel
```

unless intended total reaction is actually 5.5 s.

For normal artillery:
prefer:

```text
fire
→ incoming cue / marker
→ shell travel
→ impact
```

instead of an unnecessarily long static pre-warning.

---

# 16. NAVAL DIRECT-FIRE SHELLS

Do not apply indirect-artillery speed to all naval guns.

Normalize direct HE/naval shell families approximately:

```text
76 mm         95 m/s
100 mm       100 m/s
127–130 mm    90 m/s
152–155 mm    85–90 m/s
```

Direct naval AP may remain:

```text
~10–20% faster
```

than equivalent HE.

Reason:
- direct fire should feel sharper than indirect artillery;
- large naval shells should still be visible;
- family speeds should be internally consistent.

---

# 17. TANK / DIRECT CANNON

Do NOT globally slow:
- tank AP;
- APFSDS;
- railgun;
- direct anti-armour cannon

to indirect-artillery speeds.

Direct tank cannon should remain:
- fast;
- responsive;
- distinct from mortar/howitzer.

Only audit extreme outliers.

---

# 18. BOMBS — KEEP

Current bomb travel/fall feel is already good.

KEEP bomb speeds/fall times unless a specific bomb is proven broken.

FAB-class payloads with visible fall-time around ~1+ second are desirable.

Do not slow bombs further by default.

---

# 19. LOITERING / FPV DRONES — KEEP

Current approximate speeds such as:

```text
FPV          ~26 m/s
Lancet       ~28 m/s
Shahed       ~20 m/s
```

already provide:
- visual travel;
- interception time;
- top-attack readability.

KEEP unless an individual drone has a bug.

---

# 20. PROJECTILE SPEED GEAR — KEEP

Current ProjectileSpeed substat progression:

```text
+4 / +6 / +8 / +10%
```

can remain.

Global ProjectileSpeed cap:

```text
30%
```

can remain.

Regression examples:

```text
Hellfire 80
+30%
= 104 m/s
```

Still acceptable.

```text
Mortar 45
+30%
= 58.5 m/s
```

Still visibly lobbed.

Therefore:
- no nerf required to ProjectileSpeed gear in this task.

---

# 21. EFFECTIVE SPEED MUST BE TESTED AFTER GEAR

Validator/tests must consider:

```text
base speed
× gear modifiers
× traits/modules if any
× runtime modifiers
= effective projectile speed
```

The game should remain within acceptable flight-time bounds even at legal cap.

Do not validate only naked base values.

---

# 22. FLIGHT-TIME VALIDATOR — REPLACE RAW SPEED THINKING

`NHANH_QUA / CHAM_QUA` should primarily evaluate:

```text
effective flight time
```

not just raw m/s.

For a straight projectile:

```text
flightTime = range / effectiveSpeed
```

For arc/ballistic projectile:

```text
flightTime = actual simulated/derived trajectory time
```

Do not use straight-line `range/speed` for mortar if actual arc path/time is available.

---

# 23. TARGET FLIGHT-TIME BANDS

Recommended normal max-range target bands:

```text
Direct cannon:
    ~0.15–0.45 s

Tactical missile:
    ~0.45–0.90 s

Long-range SAM/AAM:
    ~0.50–1.00 s

Rocket artillery:
    ~0.70–1.60 s

Mortar/howitzer:
    ~0.90–2.00 s

Cruise missile:
    ~1.20 s+
    often significantly longer
```

These are audit targets, not absolute hard caps.

Warnings:
- below lower band => `TOO_FAST_FOR_CLASS`
- above upper band => `TOO_SLOW_FOR_CLASS`

Allow explicit owner exception.

---

# 24. MIN-RANGE FLIGHT FEEL

Do not optimize only max range.

Audit:
- min range;
- median practical range;
- max range.

A projectile can look correct at max range but become effectively hitscan at normal engagement distance.

Recommended validator outputs:

```text
flightTimeAtMinRange
flightTimeAt50PercentRange
flightTimeAtMaxRange
```

---

# 25. PROJECTILE ACCELERATION

If runtime supports acceleration, do not assume constant speed.

For missiles, a satisfying model may use:

```text
launch speed
→ short acceleration
→ cruise speed
```

But do not add acceleration unless implementation is already stable.

If adding it:
- final average flight time should still meet target bands;
- interception logic must use actual velocity;
- VFX trail must match.

Constant-speed implementation is acceptable if simpler.

---

# 26. APS / CIWS / POINT-DEFENCE REGRESSION

Lower projectile speed increases defensive engagement time.

Mandatory regression after speed changes.

Test:
- direct missile;
- drone;
- direct rocket;
- artillery rocket;
- mortar shell where system is eligible;
- artillery shell where eligible.

Measure:

```text
intercept probability
time inside defence radius
shots available per threat
charges consumed
track/acquire timing
```

---

# 27. DO NOT AUTO-NERF APS FIRST

Do not immediately change:
- APS radius;
- charge count;
- recharge;
- point-defence radius

just because projectiles got slower.

First measure actual intercept rate.

If defence becomes too strong, adjustment priority:

1. acquisition/track time;
2. eligible projectile rules;
3. engagement cooldown/timing;
4. intercept probability;
5. only then consider radius/recharge.

Preserve the identity of APS/CIWS.

---

# 28. FLARE / JAMMER REGRESSION

Slower AAM/ATGM increases decoy window.

Test:
- flare decoy chance;
- flare burn duration;
- missile reacquisition if implemented;
- jammer interaction;
- missile terminal guidance.

Do not automatically nerf flares before tests.

---

# 29. WARNING LEAD TIME REGRESSION

Slower projectile already creates reaction time.

For each warning class compute:

```text
TotalReactionWindow =
PreLaunchWarning
+ RelevantProjectileTravel
```

Do not over-warning routine weapons.

Suggested:
- ordinary mortar/artillery can rely significantly on travel/incoming cue;
- boss T4/T5 keeps explicit telegraph;
- top attack gets terminal cue;
- cruise missile can rely on long visible approach plus appropriate warning.

---

# 30. VISUAL / AUDIO DEPENDENCY

The speed rework only feels good if projectile presentation supports it.

Ensure:
- missile motor/trail remains visible;
- rocket artillery trails are readable;
- mortar/howitzer arc is visible enough;
- incoming artillery cue aligns with actual travel;
- top-attack missile has distinct terminal behavior;
- big shell impact timing matches sound.

Coordinate with:
`Machine_Brigade_MAP_VISUAL_AUDIO_MASTER_SPEC.md`

---

# 31. AI LEAD / PREDICTION REGRESSION

Projectile speed affects target leading.

Audit:
- air interception;
- moving ground target leading;
- naval target leading;
- artillery prediction;
- boss aiming.

Do not leave old lead constants tuned for 180–300 m/s missiles.

AI should use actual effective projectile speed.

---

# 32. PROXIMITY FUZE / INTERCEPT REGRESSION

Any:
- proximity fuze;
- airburst;
- CIWS intercept;
- predicted intercept point

must use new actual projectile velocity.

Do not keep hardcoded assumptions based on old family speed.

---

# 33. DAMAGE / DPS MUST NOT CHANGE FROM SPEED ALONE

Projectile speed changes should NOT silently alter:
- base damage;
- reload;
- fire rate;
- blast radius;
- penetration

unless a separate balance decision exists.

The goal is flight feel, not hidden DPS rebalance.

---

# 34. HOMING / TURNING QUALITY

Slower guided missile may turn more effectively if turn rate is unchanged.

Regression test:
- missile overshoot;
- terminal turn;
- circling;
- impossible 180-degree correction.

If slower speed makes guidance unrealistically perfect:
adjust:
- turn rate;
- lead logic;
- terminal steering

rather than increasing speed back to hitscan levels.

---

# 35. MISSILE MINIMUM RANGE

Slower tactical missiles make minimum-range behavior more important.

Ensure:
- weapon respects min range;
- missile does not perform absurd immediate U-turn;
- AI does not fire guided missile when target is too close if weapon cannot turn.

---

# 36. SALVO SPACING

Visible travel makes salvo timing more important.

For:
- rocket pods;
- MLRS;
- boss rocket barrage

ensure salvo does not visually collapse into one projectile stack.

Keep/create small launch spacing appropriate to family.

Do not change DPS unless spacing is already part of existing weapon behavior.

---

# 37. CAMERA / SFX FEEL

Do not compensate slower projectiles by exaggerating camera shake.

Satisfaction should come from:
- launch sound;
- trail;
- visible travel;
- incoming cue;
- impact.

Camera shake remains secondary.

---

# 38. PIPELINE SOURCE OF TRUTH

For every affected weapon record:

```text
canonical weapon data
→ weapon family inheritance
→ variant inheritance
→ boss/AI inheritance if applicable
→ runtime effective value
→ generated export
```

The effective runtime value is the final balance authority.

Do not accept cases where:
- spreadsheet says 80;
- runtime uses 180.

---

# 39. SPECIFIC PIPELINE BUG CANDIDATES

Mandatory audit:

```text
apkws_rocket
anti_ship_missile
```

Also scan all weapons where:

```text
abs(raw projectileSpeed - exported effective speed)
```

is unexpectedly large without documented inheritance.

Generate report:

```text
id
rawSpeed
familySpeed
variantOverride
runtimeSpeed
exportedSpeed
reason
```

---

# 40. FAMILY CONSISTENCY AUDIT

Weapons with the same real/family identity should not have wildly different speeds without explicit reason.

Examples:
- Hellfire family;
- Kornet family;
- 70–80 mm rocket family;
- Buk family;
- Patriot family;
- 152–155 artillery family;
- 127–130 naval family.

Family variant difference must be documented.

---

# 41. BOSS INHERITANCE AUDIT

Boss variant using an existing family should normally inherit family flight feel.

Do not let generated boss balancing multiply projectile speed implicitly.

Audit:

```text
boss weapon speed
vs
base family speed
```

Flag if deviation > reasonable threshold without explicit reason.

---

# 42. GENERATED AUDIT FIELDS

Recommended derived fields:

```text
effectiveProjectileSpeedMps
flightTimeMinRangeS
flightTimeHalfRangeS
flightTimeMaxRangeS
projectileFeelClass
projectileSpeedWarning
speedInheritanceSource
```

---

# 43. PROJECTILE FEEL CLASSES

Suggested enum:

```text
DIRECT_FAST
TACTICAL_MISSILE
AIR_DEFENCE_MISSILE
ROCKET_ARTILLERY
MORTAR
HOWITZER
CRUISE
DRONE
BOMB
```

Validator thresholds depend on class.

Do not use a single universal speed threshold.

---

# 44. TEST MATRIX

## Missile
- Hellfire at min/half/max range
- Vikhr
- Maverick
- Kh-29
- Kornet
- APKWS
- anti-ship missile

## Air defence
- Stinger
- Igla
- R-60
- AIM-9/WVR
- AMRAAM
- Pantsir
- Buk
- Patriot
- S-400

## Artillery
- 120 mortar
- AMOS
- 155 howitzer
- guided 155
- Grad
- GMLRS
- Smerch
- TOS

## Naval
- 76
- 100
- 127/130
- 152/155 if present

## Boss
- boss missile
- boss rocket barrage
- boss mortar
- boss indirect shell
- T4/T5 telegraphed strike

## Defence
- SELF_APS
- point defence
- CIWS
- flares
- jammer

---

# 45. PLAYER-FEEL ACCEPTANCE

Playtest questions:

1. Can the player visually register the projectile after launch?
2. Does the impact feel connected to the launch?
3. Does the projectile look energetic rather than floating?
4. Is there enough time to appreciate trail/arc?
5. Does missile still feel faster than cruise missile?
6. Does mortar/howitzer feel meaningfully slower than direct cannon?
7. Does SAM still feel dangerous and responsive?
8. Do APS/CIWS remain useful but not oppressive?
9. Does boss projectile feel powerful rather than instant/unfair?
10. Does heavy naval shell feel large and physical?

---

# 46. NON-GOALS

Do not:
- slow every projectile in the game;
- slow bullets/MG/autocannon by this task unless a specific bug exists;
- slow direct APFSDS to artillery speeds;
- slow bombs that already have good fall time;
- slow FPV/Lancet/Shahed that already feel good;
- make cruise missile faster to match other missiles;
- change damage/reload to compensate automatically;
- change boss HP/armour;
- change APS before measuring regression;
- use real-world Mach values directly in game scale.

---

# 47. IMPLEMENTATION PRIORITY

## P0
1. Fix family/effective speed source of truth.
2. Apply tactical missile values.
3. Apply AAM/SAM values.
4. Apply mortar/howitzer/MLRS values.
5. Audit APKWS / anti-ship pipeline.
6. Apply boss projectile family inheritance.
7. Add flight-time validator.

## P1
8. Naval shell normalization.
9. Warning/travel timing regression.
10. APS/CIWS/flair regression.
11. AI lead/prediction regression.
12. guidance-turn regression.

## P2
13. presentation polish.
14. telemetry.
15. per-family final tuning after playtest.

---

# 48. FINAL EXPECTED SPEED TABLE

```text
CRUISE
65–70

ATGM / HELLFIRE
75–85

AIRCRAFT ROCKET
90–100

SHORT AAM / MANPADS
105–115

SHORAD
120–130

MEDIUM SAM
140–150

LONG SAM
165–170

ANTI-SHIP
95

MORTAR
35–45

HOWITZER
55–70

ROCKET ARTILLERY
65–85

NAVAL DIRECT HE
85–100

DRONE
KEEP ~20–28

BOMB
KEEP current fall behavior

DIRECT TANK AP/APFSDS
KEEP fast/snappy
```

---

# 49. FINAL REPORT REQUIRED

Coding AI must report:

1. all changed weapon IDs;
2. `old_speed → new_speed`;
3. canonical file/location;
4. family inheritance changes;
5. APKWS pipeline result;
6. anti-ship pipeline result;
7. all raw/effective mismatch findings;
8. flight-time min/half/max before/after;
9. `NHANH_QUA/CHAM_QUA` validator replacement;
10. boss projectile inheritance audit;
11. guided artillery audit;
12. naval shell audit;
13. APS/CIWS regression results;
14. flare/jammer regression results;
15. AI lead/prediction regression;
16. guidance-turn regression;
17. warning total-reaction-window audit;
18. ProjectileSpeed gear cap test;
19. generated docs/data regenerated;
20. stale old-speed scan.

---

# 50. FINAL NON-NEGOTIABLE CONFIRMATIONS

Final report must explicitly confirm:

```text
Cruise missile speeds were kept unless a concrete bug was found.

Tactical missiles remain faster than cruise missiles.

Missile / artillery balance is based primarily on in-game flight time, not real-world m/s.

Mortar is slow/high-arc.

Guided artillery is not automatically near-hitscan.

Boss flag does not automatically increase projectile speed.

ProjectileSpeed gear remains capped and does not break the new feel bands.

APS/CIWS were regression-tested before any defensive nerf.

Warning lead time and projectile travel were audited together.

APKWS and anti-ship raw/effective speed pipelines were verified.

Bomb and loitering-drone speeds were not globally reduced.

Direct tank/APFSDS fire remains fast and responsive.

Boss HP/armour remain unchanged.
```

This document is the single source of truth for projectile flight-feel rebalance.
