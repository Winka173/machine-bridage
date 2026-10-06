# MACHINE BRIGADE — BALANCE MASTER UPDATE FINAL

**Status:** FINAL IMPLEMENTATION SOURCE OF TRUTH  
**Scope:** projectile speed, bombs, aircraft, ground vehicles, towers, structures, bosses, fire support, related regressions.  
**Important:** current XLSX/MD exports may still contain stale values. Update canonical/runtime source first, then regenerate exports.

---

## 1. Global rules

- Do not manually patch generated XLSX/MD as authority.
- Verify pipeline: `canonical source -> family inheritance -> variant override -> runtime effective -> generated export`.
- Preserve all previously locked combat rules.
- **Boss armour values must remain unchanged.**
- Do not silently alter unrelated Pen, armour, reload, fire rate, blast radius, CP/economy, repair, gear caps, or boss weakpoint armour unless this file explicitly says so.

### Locked penetration context

Normal penetration (`Pen - Armour`):

```text
>=+2  1.20
+1    1.00
0     0.85
-1    0.65
-2    0.40
-3    0.15
<=-4  0.08
```

Top Attack uses roof armour only and replaces normal penetration lookup:

```text
>=+2  1.15
+1    1.10
0     0.95
-1    0.75
-2    0.50
-3    0.25
<=-4  0.12
```

Relevant locked damage context:

```text
HE vs Structure = 1.60
Thermobaric vs Structure = 2.00, replacing HE 1.60
```

---

# 2. Projectile flight-feel design

Goal:

```text
launch -> visible flight/trail/arc -> anticipation -> impact
```

Avoid near-hitscan feel for missiles, aircraft rockets, mortar, howitzer, MLRS and boss missile/rocket barrages.

Direct tank/AP/APFSDS/direct kinetic cannon remain fast and responsive.

---

# 3. Final missile speed table

## Cruise — KEEP

```text
Cruise missile: 65–70 m/s
```

Keep JASSM, Kh-101, Kalibr, generic ground cruise and equivalent boss cruise near this range unless a concrete bug exists.

## Tactical / ATGM

```text
hellfire_standoff             70 m/s
hellfire_volley               70 m/s
drone_missile / Hellfire      70 m/s
gun-launched ATGM             70 m/s
TOW family                    70 m/s
Kornet family                 70 m/s
Konkurs family                keep ~60 m/s if already near this
Vikhr                         75 m/s
Maverick                      75 m/s
Kh-29                         75 m/s
APKWS                         80 m/s
anti_ship_missile             80 m/s
```

Kornet variants such as `kornet_multi`, `kornet_top`, `kornet_twin` should converge to the same intended family feel unless a documented exception exists.

## Short AAM / MANPADS

```text
Stinger ATAS       90 m/s
Igla-V             90 m/s
R-60               95 m/s
AIM-9 / WVR       100 m/s
```

## SHORAD / medium / long SAM-AAM

```text
generic SHORAD        100 m/s
Tamir                 105 m/s
Pantsir 57E6          110 m/s
AMRAAM                120 m/s
Buk player family     120 m/s
Patriot player        130 m/s
S-400 / 48N6          140 m/s
```

These values supersede earlier higher recommendations.

## Boss-specific intentional exceptions — KEEP

```text
boss/ship sam_post Buk        80 m/s
Nemesis sam_battery Patriot   95 m/s
boss Grad / boss_rockets      65 m/s
boss cruise                   65–70 m/s
```

Do not normalize these back upward to player SAM speeds.

---

# 4. Aircraft / helicopter rockets

```text
aircraft 70–80 mm rocket family   95 m/s
jet_rockets                      100 m/s
boat_rockets                      90 m/s
APKWS                             80 m/s
```

Fix any inheritance that silently pushes these back to ~180 m/s.

---

# 5. Mortar / artillery / rocket-artillery projectile speed

## Mortar

```text
standard 120 mm     45 m/s
AMOS                45 m/s
boss mortar         40 m/s
very heavy mortar   35–40 m/s
```

## Howitzer

```text
medium field artillery     55 m/s
long-range artillery       60 m/s
heavy artillery            65 m/s
huge/coastal indirect      65–70 m/s
```

## Guided artillery

Use base family speed or at most base +5–10 m/s. Guidance must not create near-hitscan shells.

## Rocket artillery

```text
TOS                    65 m/s
technical rockets      75 m/s
Grad                   80 m/s
Smerch                 80 m/s
GMLRS/M30/M31          85 m/s
boss rocket barrage    65–80 m/s depending intentional boss override
```

---

# 6. Flight-time validator

Primary audit should be in-game effective flight time, not raw m/s.

Audit:

```text
flightTimeAtMinRange
flightTimeAtHalfRange
flightTimeAtMaxRange
```

Use actual ballistic trajectory time where available.

Recommended bands:

```text
Direct cannon          ~0.15–0.45 s
Tactical missile       ~0.55–1.00 s
Short AAM/MANPADS      ~0.30–0.65 s
Medium/long SAM/AAM    ~0.40–0.80 s
Rocket artillery       ~0.70–1.60 s
Mortar/howitzer        ~0.90–2.00 s
Anti-ship missile      ~0.80–1.80 s
Cruise                 ~1.20 s+
```

Normally flag a tactical/guided missile if half practical range is below ~0.30–0.35 s, unless explicitly exempted.

ProjectileSpeed gear remains:

```text
+4/+6/+8/+10%
BuildCap = 30%
```

Regression must include legal max-cap builds.

---

# 7. Missile defence regression

After speed changes test:

- APS
- CIWS / point defence
- flare
- jammer
- missile reacquisition
- target leading
- intercept prediction
- proximity fuze
- minimum-range guidance
- terminal turning/overshoot
- warning + travel total reaction window

Do not pre-nerf APS/CIWS before measuring.

---

# 8. Bomb balance — FINAL

```text
Conventional aircraft bomb          damage ×1.25
Heavy-bomber conventional payload   damage ×1.30
Guided bomb / JDAM                   damage ×1.20
Cluster bomb                         damage ×1.15
Cluster effective coverage           ×1.10
```

Do not automatically increase Pen.
Do not globally reduce rearm time.
Do not add another generic bomb-vs-structure multiplier; HE/Thermobaric structure rules already apply.

---

# 9. Aircraft balance — FINAL

## HP

```text
fighter / attack jet / stealth fighter   ×1.15
attack helicopter / scout helicopter     ×1.15
heavy/twin-rotor gunship                  ×1.15
heavy bomber                              ×1.20
large airborne carrier/support            ×1.15
```

Do not globally raise aircraft armour.

## Ground-attack output

Non-bomb aircraft ground-attack cannon/rocket/tactical missile damage:

```text
×1.08–1.10
```

Avoid double-buffing payloads already covered under bombs.
AAM damage stays unchanged.

---

# 10. Ground vehicles — FINAL

```text
Main Battle Tank:
  HP ×1.05
  damage KEEP
  armour KEEP

Heavy Tank:
  HP ×1.08
  damage ×1.05
  armour KEEP

Titan Tank:
  KEEP HP/damage/armour

Twin Tank:
  KEEP

IFV:
  KEEP

Light Tank / Armored Car / Recon:
  KEEP

Tank Destroyer:
  HP ×1.05
  damage/Pen KEEP

Railgun Truck:
  KEEP
  only alter reload if post-patch simulation proves overtuned

Flame Tank:
  HP ×1.08
  damage KEEP

Breacher / Armored Bulldozer / Engineer assault:
  HP ×1.10
  wall modifier KEEP

Artillery/Mortar/MLRS platforms:
  HP KEEP
```

---

# 11. Towers — FINAL

Tower strength should come mainly from durability/time-on-field.

```text
Small combat tower:
  HP ×1.20
  damage ×1.08

Medium combat tower:
  HP ×1.25
  damage ×1.10

Large/heavy combat tower:
  HP ×1.30
  damage ×1.10

AA gun tower:
  HP by size
  damage KEEP

SAM tower:
  HP by size
  damage KEEP

C-RAM / laser / PD:
  HP ×1.15–1.20
  raw damage KEEP

EW/radar/flare utility tower:
  HP ×1.15
```

Do not globally buff tower armour.

---

# 12. Structures / base buildings — FINAL

```text
airfield                HP ×1.20
repair_bay              HP ×1.20
logistics_station       HP ×1.20
fire_control_centre     HP ×1.25
radar/EW/targeting      HP ×1.20
vehicle_hangar          HP ×1.20
aircraft_hangar         HP ×1.20
cp_relay-like utility   HP ×1.20
super_gun strategic body HP ×1.15 if destructible objective
HQ                      HP ×1.05
Spawn Bastion           KEEP
Walls/HESCO/T-wall      KEEP
Shield Tower body       HP ×1.10
Dome/Ward HP            KEEP
Shield recharge         KEEP
```

Do not buff walls.
Do not buff body and shield pool simultaneously beyond the values above.

### Structure repair audit

If structure repair is `% max HP/s`, keep it.
If it is flat HP/s and becomes too weak because of higher HP, allow structure/tower repair throughput +10–15% after audit.
Do not blanket-buff combat-vehicle repair.

---

# 13. Boss balance — FINAL

## Boss armour

```text
KEEP ALL BOSS ARMOUR VALUES
```

## Main boss

```text
hull HP ×1.08
```

## Mini-boss

```text
hull HP ×1.05
```

## Nyx

```text
outgoing damage ×1.10
```

## Scylla

```text
outgoing damage ×1.08
```

## Mobile Fortress

```text
damage KEEP
uptime KEEP
```

## Nemesis / Nuke Train

```text
damage KEEP
```

Do not pre-nerf. Re-evaluate only after final AI + projectile + balance patch simulation.

## Monster / Moloch / Leviathan / Kraken / Earth Borer

```text
damage KEEP
```

Apply normal main/mini HP rule based on classification.

### Boss parts

If part HP is proportional to boss hull HP, do not apply an additional generic part-HP buff. Avoid double-buffing.
Only adjust individual parts after regression if a specific part dies unrealistically fast.

---

# 14. Fire support — FINAL

## 120 mm mortar

```text
damage ×1.10
```

Example: 150 -> 165.

## AMOS

```text
damage ×1.10
salvo KEEP
cooldown KEEP
```

## 240 mm mortar

```text
damage KEEP
splash 9 -> 10 m
```

## Standard / long / heavy howitzer

```text
damage KEEP
effective splash/coverage ×1.10
Pen KEEP
```

Use family-specific rounding.

## Guided artillery

```text
damage KEEP
splash KEEP
accuracy/target correction remains the advantage
```

## Standard MLRS / GMLRS

```text
damage KEEP
effective salvo coverage +8–10%
```

Do not reduce cooldown or increase rocket count by default.

## Cluster MLRS

```text
bomblet damage KEEP
cluster/effective coverage +10%
```

## Grad / Smerch / Heavy Rocket Artillery

```text
raw damage KEEP
```

## TOS / Thermobaric launcher

```text
KEEP ALL COMBAT STATS
```

Thermobaric already gets Structure ×2.00.

## Ballistic launcher

```text
KEEP
```

## Ground cruise launcher

```text
damage KEEP
flight feel KEEP
```

---

# 15. Artillery Barrage support

`artillery_barrage` gets approximately:

```text
+10% total strike value
```

Preferred lever:
1. slightly more shells or coverage;
2. avoid pure per-shell damage increase if possible.

Use one primary buff lever, not both.

Important: do not accidentally buff unrelated scripted enemy barrage events if those are separate systems.
Audit support-card barrage versus scripted campaign barrage separately.

---

# 16. Fire-support survivability / logistics / AI

Fire-support platform HP stays unchanged:
- artillery
- mortar carrier
- MLRS
- heavy rocket artillery
- ballistic launcher
- ground cruise launcher

Survivability should come from range, positioning, escort and shoot-and-scoot.

Audit ammo/resupply. If supply throughput is genuinely too limiting, allow:

```text
artillery/MLRS resupply throughput +10%
```

only through ammo carrier/logistics mechanics.
Do not inflate default magazines globally.

Do not add a hidden counter-battery damage multiplier.
Counterbattery advantage should come from detection, acquisition and prioritization.

Heavy fire-support AI should use target-value thresholds based on:
- CP/value inside blast;
- objective importance;
- tower/structure value;
- enemy concentration;
- predicted overkill;
- reload/salvo opportunity cost.

Do not waste heavy salvos on lone low-value targets unless mission-critical.

---

# 17. Tower rebuild economy

Do not automatically increase rebuild CP.

After tower durability buff, measure defensive uptime/rebuild CP.
If large tower value becomes excessive, prefer:

```text
large-tower rebuild time +10%
```

before changing CP or undoing HP. Apply only if regression fails.

---

# 18. Mandatory regression matrix

## Ground
- MBT vs Heavy
- Heavy vs TD
- TD vs Titan
- Flame Tank assault
- Breacher vs walls
- Railgun vs Armour4/5

## Air
- Attack Helicopter vs SHORAD
- Attack Jet vs SAM
- Fighter vs AAM
- Heavy Bomber survivability
- Sortie value before/after bomb buffs

## Tower / structure
- assault squad TTK vs small/medium/large tower
- bomber TTK vs medium/large tower
- artillery TTK vs tower
- thermobaric/breacher vs fortification
- bomb vs utility building
- HQ TTK after +5%

## Boss
- main-boss TTK after +8% HP
- mini-boss TTK after +5%
- Nyx pressure after +10% output
- Scylla pressure after +8% output
- Nemesis pressure with no pre-nerf
- boss-part survivability

## Fire support
- mortar 120 / AMOS efficiency
- 240 mm coverage
- howitzer effective hits on formations
- MLRS coverage/cluster behavior
- artillery-barrage support value
- counterbattery duel
- resupply cadence

## Projectile
- min/half/max flight time
- legal geared projectile speed
- APS/CIWS intercept rate
- flare/jammer interaction
- AI lead/intercept prediction
- warning + travel total reaction window

---

# 19. Generated outputs

After canonical changes, regenerate/update as applicable:

```text
01_chien_dau.xlsx
01_chien_dau.md
02_boss.xlsx
02_boss.md
03_can_cu.xlsx
03_can_cu.md
04_che_do_kinh_te_ai.xlsx
04_che_do_kinh_te_ai.md
07_hinh_anh_am_thanh_model.xlsx/.md if dependent timing changes
09_ai.xlsx
09_ai.md
10_trang_bi.xlsx/.md if derived reports change
00_index.xlsx
README.md
CHANGES.md
```

Also regenerate relevant balance/flight/TTK/structure/fire-support/APS/AI audit reports and stale-value scans.

---

# 20. Required final implementation report

Report:

1. canonical files changed;
2. every affected ID;
3. old -> new effective projectile speeds;
4. old -> new HP/damage/splash/coverage;
5. main/mini boss HP application;
6. confirmation boss armour unchanged;
7. exact Nyx/Scylla final output values;
8. bomb payload changes;
9. aircraft HP/output changes;
10. tower/structure final values;
11. fire-support final values;
12. artillery-barrage implementation;
13. inheritance/raw-effective mismatches found;
14. APKWS result;
15. anti-ship missile result;
16. boss SAM/rocket exceptions preserved;
17. min/half/max flight times;
18. geared projectile-speed tests;
19. APS/CIWS/flare/jammer regression;
20. AI lead/intercept regression;
21. warning total-reaction-window audit;
22. structure repair throughput audit;
23. fire-support resupply audit;
24. boss-part double-buff audit;
25. regenerated outputs;
26. stale-data scan.

Final report must explicitly confirm:

```text
Boss armour unchanged.
Cruise stays ~65–70 m/s.
Hellfire = 70 m/s.
Kornet family = 70 m/s unless explicit documented exception.
Anti-ship missile = 80 m/s.
Player Buk = 120 m/s.
Player Patriot = 130 m/s.
S-400 = 140 m/s.
Boss/ship sam_post = 80 m/s.
Nemesis sam_battery = 95 m/s.
Boss Grad/rockets = 65 m/s.
Bomb buffs applied by payload class without global rearm reduction.
Aircraft buffed mainly through HP and modest ground-attack output, not armour inflation.
MBT/Heavy buffs kept conservative.
Titan not buffed.
Towers gained more durability than DPS.
Walls not buffed.
Shield body buffed without also buffing dome/ward pool.
Main boss HP +8%; mini-boss HP +5%.
Nyx damage +10%; Scylla +8%.
Nemesis not pre-nerfed.
120 mm mortar damage +10%.
240 mm mortar damage unchanged; splash 9 -> 10 m.
Howitzer raw damage unchanged; coverage about +10%.
MLRS raw damage unchanged; coverage increased.
TOS combat stats unchanged.
Fire-support vehicles did not receive blanket HP buffs.
Artillery Barrage gained ~10% total strike value without unintentionally buffing unrelated scripted barrages.
Generated outputs regenerated from canonical source.
```

This file is the final source of truth for this balance update.
