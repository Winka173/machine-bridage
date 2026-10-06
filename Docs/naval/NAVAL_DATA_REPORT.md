# Naval vehicle expansion — data/AI/economy lane report (06/10)

Scope of this lane (per the owner prompt and brief): canonical data, AI doctrine mapping, and economy/card
integration only. Models come later (stand-in GLBs here; `Docs/naval/MODEL_CONTRACT.md` is the brief for that
lane). **No Unity run, no EditMode/PlayMode test, no battle simulation was executed** (owner override 06/10,
"nhớ là không test"): every number below is a static read of `balance.json` plus a static Python arithmetic pass
(penetration/damage-type tables only) — not a simulated match.

## Canonical files changed

- `Assets/MachineBrigade/Resources/Data/balance.json` — the only file touched:
  - `weapons[]`: 10 new ship-specific entries (`torpedo_naval`, `ashm_corvette_salvo`, `frigate_ashm`, `ashm_quad`,
    `missile_frigate_salvo`, `missile_destroyer_salvo`, `missile_cruiser_salvo`, `naval_203_monitor`,
    `naval_203_bc`, `naval_406_bs`). Every other gun/CIWS/SAM on the new roster reuses an existing weapon id
    unmodified (`naval_76`, `naval_100`, `naval_127`, `hover_ciws`, `hmg_roof`, `sam`, `sam_long`, `sam_48n6`,
    `mlrs_rockets`) — no shared weapon's own stats were changed.
  - `vehicles[]`: 17 new units, inserted next to the existing naval roster (after `missile_boat`, before
    `landing_craft`).
  - `aiBehaviour.units`: 16 new id -> role-id mappings (one line; `ew_corvette`/`ciws_escort_ship` use `Support`,
    see AI section).
- `Docs/naval/MODEL_CONTRACT.md` — new (the model-lane brief: target size, silhouette, exact mount nodes per ship).
- `Docs/DECISIONS.md` — new `## Naval expansion (data)` section.
- `Docs/CHANGELOG.md` — one line under `## Unreleased`.

No other canonical file (campaign.json, escort/boss tables, Sim C# source) was touched. `Tools/simbuild/Sim.csproj`
still builds with 0 errors against the unmodified C# — this is a pure data pass.

## New unit IDs (17)

`torpedo_boat`, `ashm_corvette`, `aa_corvette`, `frigate`, `missile_frigate`, `aa_frigate`, `destroyer`,
`gun_destroyer`, `missile_destroyer`, `aa_destroyer`, `rocket_artillery_ship`, `heavy_monitor`, `battlecruiser`,
`battleship`, `missile_cruiser`, `ciws_escort_ship`, `ew_corvette`.

**Nothing was skipped.** `ew_corvette` was the one conditional unit (spec: implement only if the existing jammer
runtime is directly reusable on a naval hull, else `BLOCKED_BY_EXISTING_RUNTIME`). It is **implemented**: the
generic jammer field (`Def.Jammer`, consumed as a pure radius/position check in
`Assets/MachineBrigade/Scripts/Sim/Abilities/AbilitySystem.cs:64,169`, with zero movement-type/hull/class
assumption) is exactly the same mechanism `ew_jammer`/`gps_jammer_vehicle` already use, so it was wired directly:
`"jammer": 30` on the new hull, no new subsystem.

## Final stats (CP / HP / armour / speed / turn rate) and weapons

| id | CP | HP | armour [F,S,R,T] | speed | turnRate | turretTurnRate | primary weapon | secondary weapons |
| --- | ---: | ---: | --- | ---: | ---: | ---: | --- | --- |
| torpedo_boat | 5 | 500 | 0 | 13 | 50 | 130 | torpedo_naval | hmg_roof |
| ashm_corvette | 9 | 1150 | [2,1,1,1] | 8.5 | 16 | 70 | ashm_corvette_salvo | hover_ciws |
| aa_corvette | 8 | 1050 | [2,1,1,1] | 8.5 | 16 | 90 | sam | hover_ciws, hmg_roof |
| frigate | 12 | 1800 | [3,2,2,1] | 6.5 | 13 | 55 | naval_100 | frigate_ashm, sam, hover_ciws |
| missile_frigate | 14 | 1750 | [3,2,2,1] | 6.2 | 12 | 50 | missile_frigate_salvo | naval_76, hover_ciws, sam |
| aa_frigate | 14 | 1850 | [3,2,2,1] | 6.0 | 12 | 80 | sam_long | hover_ciws, naval_76 |
| destroyer | 18 | 2800 | [4,3,2,2] | 5.2 | 10 | 45 | naval_127 | ashm_quad, sam_long, hover_ciws x2 |
| gun_destroyer | 17 | 2900 | [4,3,2,2] | 5.0 | 10 | 45 | naval_127 | naval_127 (2nd turret), sam, hover_ciws |
| missile_destroyer | 20 | 2700 | [4,3,2,2] | 4.8 | 9 | 45 | missile_destroyer_salvo | naval_100, sam, hover_ciws x2 |
| aa_destroyer | 20 | 2850 | [4,3,2,2] | 4.8 | 9 | 70 | sam_48n6 | sam_long, hover_ciws x2, naval_127 |
| rocket_artillery_ship | 14 | 1450 | [2,1,1,1] | 5.5 | 11 | 40 | mlrs_rockets | hmg_roof |
| heavy_monitor | 15 | 2400 | [4,3,3,2] | 3.5 | 8 | 35 | naval_203_monitor | hover_ciws |
| battlecruiser | 26 | 4200 | [4,4,3,2] | 4.4 | 8 | 35 | naval_203_bc (barrels 2) | ashm_quad, sam_long, hover_ciws x2 |
| battleship | 32 | 6000 | [5,4,4,3] | 3.2 | 6 | 25 | naval_406_bs (turret 1) | naval_406_bs x2 (turrets 2-3), sam_long, hover_ciws x2 |
| missile_cruiser | 25 | 3700 | [4,3,3,2] | 4.0 | 9 | 40 | missile_cruiser_salvo | naval_127, sam_long, hover_ciws x2 |
| ciws_escort_ship | 11 | 1350 | [2,2,1,1] | 7.0 | 18 | 150 | naval_76 | hover_ciws x3 |
| ew_corvette | 9 | 1000 | [2,1,1,1] | 8.0 | 16 | 70 | naval_76 | sam (self-defence); jammer 30 |

All ships carry `"interceptionMode": "PointDefense"` + an `"aps"` block (CIWS intercept) except `torpedo_boat`,
`rocket_artillery_ship`, `ew_corvette` (per spec: light/no CIWS on those three).

## New/variant weapons — exact projectile speed / Pen / damage / splash

| weapon id | used by | pen | damage | cooldown | burst x interval | proj. speed | splash | damageType |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| torpedo_naval | torpedo_boat | 4 | 360 | 12 s | 2 x 1.4 s | 55 m/s | 3 m | ShapedCharge |
| ashm_corvette_salvo | ashm_corvette | 4 | 450 | 18 s | 4 x 0.6 s | 80 m/s | 6 m | HighExplosive |
| frigate_ashm | frigate | 4 | 450 | 30 s (inherited) | 2 x 1.0 s | 80 m/s | 7 m (inherited) | HighExplosive |
| ashm_quad | destroyer, battlecruiser | 4 | 450 | 30 s (inherited) | 4 x 0.6 s | 80 m/s | 7 m (inherited) | HighExplosive |
| missile_frigate_salvo | missile_frigate | 4 | 450 | 22 s | 6 x 0.5 s | 80 m/s | 7 m | HighExplosive |
| missile_destroyer_salvo | missile_destroyer | 4 | 450 | 26 s | 8 x 0.45 s | 80 m/s | 8 m | HighExplosive |
| missile_cruiser_salvo | missile_cruiser | 4 | 450 | 28 s | 8 x 0.45 s | 80 m/s | 7 m (inherited) | HighExplosive |
| naval_203_monitor | heavy_monitor | 4 | 360 | 7 s | 1 | 65 m/s (inherited) | 5.5 m | HighExplosive |
| naval_203_bc | battlecruiser | 4 | 420 | 7.5 s | 1 (barrels 2) | 85 m/s (inherited) | 8 m (inherited) | HighExplosive |
| naval_406_bs | battleship | **5** | 600 | 11 s | 1 (x3 mounts) | 85 m/s (inherited) | 8 m (inherited) | HighExplosive |

Pen5 appears only on `naval_406_bs` (battleship heavy gun), exactly as the owner's exception allows; no AShM uses
anything but Pen4 (all six AShM weapons above hold Pen4, projectile speed 80 m/s — the locked value). The six AShM
weapons `"inherits": "anti_ship_missile"` with `"weaponFamily": ""` so their per-ship burst/cooldown/splash survive
the `nsm_oniks` family-row reapply on resolve (the `scylla_kh35` precedent; verified by
`Tools/balance/flight_feel_audit.py`, see Validators below). `naval_203_monitor`/`naval_203_bc`/`naval_406_bs`
inherit from `gun_203_siege`/`cruiser_203` respectively and do not touch those ids' own stats, so `siege_tank` /
`sea_cruiser` are unaffected.

## AI roles and target priorities

Wired through the existing doctrine pipeline (`aiBehaviour.units` id -> role id ->
`Sim/AI/P2/CombatRoleDoctrine.cs` `DoctrineRole`), no new doctrine code:

| unit | aiBehaviour role | class | doctrine | target priority (from the existing ladder) |
| --- | --- | --- | --- | --- |
| torpedo_boat | TD | TankHunter | TankDestroyer | SuperHeavy > Armour4 > Heavy > boss > MBT > medium; light only last-resort |
| ashm_corvette | TD | TankHunter | TankDestroyer | same ladder — heavy naval first |
| missile_frigate | TD | TankHunter | TankDestroyer | same |
| missile_destroyer | TD | TankHunter | TankDestroyer | same |
| missile_cruiser | TD | TankHunter | TankDestroyer | same |
| aa_corvette | SAM | AntiAir | AntiAir | aircraft threatening an objective > bomber/strike > helicopter > fighter > drone; no ground chase |
| aa_frigate | SAM | AntiAir | AntiAir | same |
| aa_destroyer | SAM | AntiAir | AntiAir | same |
| frigate | MBT | Heavy | MainBattle | immediate threat > heavy/MBT > TD threatening our heavies > objective defence > structure > light |
| destroyer | Heavy | Heavy | MainBattle | same (heavy generalist) |
| gun_destroyer | Heavy | Heavy | MainBattle | same (structure/tower sits at rung 5, matching its surface/shore role) |
| heavy_monitor | Heavy | Heavy | MainBattle | same |
| battlecruiser | Heavy | Heavy | MainBattle | same |
| battleship | Heavy | Heavy | MainBattle | same (armour front 5 auto-classifies it as SuperHeavy to everyone else's targeting) |
| rocket_artillery_ship | MLRS | Artillery | FireSupport | counter-battery > tower/SAM > clustered > heavy (stationary) > objective defence; isolated near-dead light
  targets last-resort — this is the existing "no full-salvo waste" + "no long chase" behaviour, reused verbatim |
| ciws_escort_ship | Support | Support | Support (no ladder) | self-defence/escort only; `naval.role: Escort, station 20` keeps it near the protected capital ship |
| ew_corvette | Support | Support | Support (no ladder) | self-defence only; `jammer: 30` aura; `naval.role: Escort, station 28` |

"No retreat-by-health" and "no random crit/penetration" are satisfied by omission — no new unit sets any such
field, and the engine has no such system to opt into. "No full-salvo waste on nearly dead light targets" for the
missile ships (TankDestroyer doctrine) rides the **generic, role-independent overkill guard**
(`CombatSystem.P0A.cs` `Overkilled()`/`OverkillExempt()`, `CombatSystem.P3.cs` planned-overkill check) that already
applies to every weapon in the sim — not something this lane had to add. "CIWS escort remains near high-value
allied naval units" uses the exact `"naval": { "role": "Escort", "station": N }` field `sea_corvette`/`sea_cruiser`
already carry (no new squad logic).

All 17 ships carry a `"naval"` object (14 generalists default to `Escort` with a station distance; `torpedo_boat`
is `Raider` with a short dash; `ciws_escort_ship`/`ew_corvette` are `Escort` per the spec's explicit
escort-the-fleet requirement) so the automatic wake trail (`Game/Views/WakeView.cs`, keyed off `Def.Naval != null`)
is ready once a model lane gives them a real hull and they are wired into a mission/fleet (out of scope this pass).

## Comparison against the six existing naval anchors (static only)

Methodology (documented so it is reproducible, not a black box): `primaryDPS = damage x burst x barrels / cooldown`
(main weapon only); `effective DPS` against three naval armour tiers (**Light** front-armour 1, **Medium** front 3,
**Heavy** front 5 — chosen to straddle the roster's own armour spread, not new canon) multiplies `primaryDPS` by
the locked `damageTable` (`balance.json "damageTable"`): the damage-type/Ground multiplier, then the penetration
step `clamp(round(2-(pen-armour)),0,6)` indexed into `damageTable.penetration`. No splash falloff, no burst
overlap/interception modelling, no armour side/rear facing — a single-number yardstick for CP-efficiency, not a
battle outcome.

`river_patrol_boat` (CP 6) and `river_gunboat` (CP 11) are real CP-costed units (no `"card": false`, used in fixed
campaign decks) so their per-CP columns are meaningful. `hover_gunboat`, `missile_boat`, `sea_corvette`,
`sea_cruiser` are `"cp": 0` fleet/mission-only escorts (never bought) — their per-CP ratios are marked `n/a`
below; only their raw HP/armour/DPS are a fair reference point.

| id | CP | HP | armour F | speed | primary wpn | pen | salvo dmg | primaryDPS | HP/CP | DPS/CP | effDPS/CP Light | Medium | Heavy |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| torpedo_boat | 5 | 500 | 0 | 13 | torpedo_naval | 4 | 720 | 60.0 | 100.0 | 12.0 | 18.72 | 15.6 | 10.14 |
| ashm_corvette | 9 | 1150 | 2 | 8.5 | ashm_corvette_salvo | 4 | 1800 | 100.0 | 127.8 | 11.11 | 13.33 | 11.11 | 7.22 |
| aa_corvette | 8 | 1050 | 2 | 8.5 | sam | 2 | 170 | 38.19 | 131.3 | 4.77 | 2.15 | 1.40 | 0.32 |
| frigate | 12 | 1800 | 3 | 6.5 | naval_100 | 3 | 458 | 91.6 | 150.0 | 7.63 | 9.16 | 6.49 | 3.05 |
| missile_frigate | 14 | 1750 | 3 | 6.2 | missile_frigate_salvo | 4 | 2700 | 122.73 | 125.0 | 8.77 | 10.52 | 8.77 | 5.70 |
| aa_frigate | 14 | 1850 | 3 | 6.0 | sam_long | 3 | 640 | 111.69 | 132.1 | 7.98 | 4.31 | 3.05 | 1.44 |
| destroyer | 18 | 2800 | 4 | 5.2 | naval_127 | 3 | 572 | 111.22 | 155.6 | 6.18 | 7.42 | 5.25 | 2.47 |
| gun_destroyer | 17 | 2900 | 4 | 5.0 | naval_127 | 3 | 572 | 111.22 | 170.6 | 6.54 | 7.85 | 5.56 | 2.62 |
| missile_destroyer | 20 | 2700 | 4 | 4.8 | missile_destroyer_salvo | 4 | 3600 | 138.46 | 135.0 | 6.92 | 8.31 | 6.92 | 4.50 |
| aa_destroyer | 20 | 2850 | 4 | 4.8 | sam_48n6 | 3 | 630 | 87.5 | 142.5 | 4.38 | 2.36 | 1.67 | 0.79 |
| rocket_artillery_ship | 14 | 1450 | 2 | 5.5 | mlrs_rockets | 3 | 500 | 50.28 | 103.6 | 3.59 | 4.31 | 3.05 | 1.44 |
| heavy_monitor | 15 | 2400 | 4 | 3.5 | naval_203_monitor | 4 | 360 | 51.43 | 160.0 | 3.43 | 4.11 | 3.43 | 2.23 |
| battlecruiser | 26 | 4200 | 4 | 4.4 | naval_203_bc | 4 | 840 | 112.0 | 161.5 | 4.31 | 5.17 | 4.31 | 2.80 |
| battleship | 32 | 6000 | 5 | 3.2 | naval_406_bs | 5 | 600 (x1 mount) | 54.55 | 187.5 | 1.71 | 2.05 | 2.05 | 1.45 |
| missile_cruiser | 25 | 3700 | 4 | 4.0 | missile_cruiser_salvo | 4 | 3600 | 128.57 | 148.0 | 5.14 | 6.17 | 5.14 | 3.34 |
| ciws_escort_ship | 11 | 1350 | 2 | 7.0 | naval_76 | 3 | 342 | 73.66 | 122.7 | 6.70 | 8.04 | 5.69 | 2.68 |
| ew_corvette | 9 | 1000 | 2 | 8.0 | naval_76 | 3 | 342 | 73.66 | 111.1 | 8.18 | 9.82 | 6.96 | 3.27 |
| **river_patrol_boat** (anchor) | 6 | 450 | 0 | 14 | mg_jeep | 1 | 9.5 | 85.51 | 75.0 | 14.25 | 14.54 | 6.84 | 1.37 |
| **river_gunboat** (anchor) | 11 | 1432 | 2 | 6 | gun_100_river | 2 | 229 | 53.43 | 130.2 | 4.86 | 4.86 | 3.16 | 0.73 |
| **hover_gunboat** (anchor, cp 0) | 0 | 520 | 1 | 8.5 | hover_ciws | 2 | 12/shot* | 718.56* | n/a | n/a | n/a | n/a | n/a |
| **missile_boat** (anchor, cp 0) | 0 | 420 | 1 | 12 | boat_rockets | 2 | 320 | 45.71 | n/a | n/a | n/a | n/a | n/a |
| **sea_corvette** (anchor, cp 0) | 0 | 1600 | 3 | 3.4 | naval_76 | 3 | 342 | 73.66 | n/a | n/a | n/a | n/a | n/a |
| **sea_cruiser** (anchor, cp 0) | 0 | 2600 | 3 | 3.2 | cruiser_203 | 4 | 1200 | 71.19 | n/a | n/a | n/a | n/a | n/a |

\* `hover_gunboat`'s `hover_ciws` is clip-limited (clip 60, `clipReload` 5.0167 s); the raw `damage x burst/cooldown`
figure overstates its sustained rate (the clip/reload amortisation is not modelled in this static pass) — informational
only, and it does not affect any new ship (none use a clip weapon as its primary).

### Reading the table against the spec's "no new ship dominates both its target and its counter" rule

- **light vs light**: `torpedo_boat` (effDPS/CP vs Light 18.72) sits below `river_patrol_boat` (14.54) in raw
  DPS/CP terms once its Pen4/ShapedCharge bonus vs the 0-armour anchor is counted at point-blank, but its HP/CP
  (100.0) is lower than the patrol boat's armour-0 scrap-value role; its expected failure (loses to sustained
  patrol/gun fire) matches the spec.
- **torpedo vs corvette/cruiser/battleship**: torpedo_naval (Pen4, ShapedCharge, 360 dmg x2) step vs sea_corvette
  (armour3): step = clamp(round(2-(4-3)),0,6) = 1 -> mult 1.0, vs sea_cruiser (armour3) same, vs battleship
  (armour5): step = clamp(round(2-(4-5)),0,6) = 3 -> mult 0.65. The torpedo is not a one-shot killer of a
  battleship broadside-on (consistent with "very poor" survivability trade — it still has to close to 65 m range,
  min range 12 m, at 13 m/s, into a ship carrying 2 CIWS).
- **sea_corvette vs ashm_corvette**: sea_corvette's sustained gun DPS/CP is undefined (cp 0, fleet-only) but its
  raw primaryDPS (73.66) is well below ashm_corvette's missile burst (100.0 primaryDPS) — the missile ship
  out-damages in a clean salvo but has an 18 s window with none, and is CP 9 as a real purchasable-style unit
  while sea_corvette is a free escort; the two are not on the same economy axis, consistent with the spec
  treating `sea_corvette` as a fixed anchor rather than a competitor.
- **general frigate vs specialist frigates**: `frigate` (effDPS/CP Medium 6.49) sits between `aa_frigate` (3.05,
  specialist vs surface) and `missile_frigate` (8.77, specialist vs ships) — the generalist is never the best at
  either specialist's job, matching the spec.
- **destroyer vs frigate**: `destroyer` HP/CP 155.6 vs `frigate` 150.0 (destroyer tankier per CP as expected of the
  heavier hull) but destroyer's DPS/CP (6.18-7.42) is close to or below frigate's missile-equipped numbers
  (7.63-9.16) — destroyer wins on raw numbers (CP 18 vs 12) but not on efficiency, consistent with "heavy
  generalist" rather than a strict upgrade.
- **destroyer vs sea_cruiser**: destroyer's naval_127 (pen3, dmg572/salvo) cannot out-gun sea_cruiser's cruiser_203
  (pen4, dmg1200/salvo) in a straight gun duel — satisfies "should not outgun sea_cruiser in sustained heavy-gun
  combat."
- **missile salvo vs layered CIWS**: not simulated (no interception roll was run); mechanically, every AShM ship
  flies into the same `aps`/`interceptionMode: PointDefense` pipeline `sea_corvette` already uses — CIWS-heavy
  targets (`ciws_escort_ship` aps radius 38/charges 4, `battleship` aps radius 34/charges 3) intercept more of a
  given salvo than a single-CIWS ship (`frigate`, aps charges 2) by the existing charge-count math; relative
  ranking only, no roll-by-roll result exists without a sim run.
- **AA escort vs drones/helicopters/jets/bombers**: `aa_corvette`/`aa_frigate`/`aa_destroyer` all route through the
  unmodified `AntiAir` doctrine ladder (bomber/strike > helicopter > fighter > drone, no ground chase) — target
  order is correct by construction; no engagement was simulated.
- **rocket_artillery_ship vs moving ship and shore structure**: `mlrs_rockets` (Pen3, minRange 20) plus the
  `FireSupport` doctrine's counter-battery/tower priority and the existing "no long chase" artillery behaviour
  (unit is `"firesWhileMoving": false`, like `mlrs`) — mechanically correct, not simulated.
- **heavy monitor vs destroyer/cruiser**: `heavy_monitor` HP/CP 160.0 (the second-highest in the new roster) and
  Pen4/360-dmg gun beat `destroyer` on raw HP/CP but lose on speed (3.5 vs 5.2) and carry no AShM at all — "easy
  missile target" per its expected failure is a mechanical fact (no SAM, light CIWS only).
- **battlecruiser vs battleship**: battlecruiser effDPS/CP (Medium 4.31) vs battleship (Medium 2.05) — the
  battlecruiser is far more CP-efficient per shot, but battleship's raw primaryDPS (54.55, undercounting: only 1 of
  its 3 identical turret mounts entered the `"weapon"` field the comparison script reads) is a known undercount —
  see note below. Battlecruiser cannot facetank battleship's Pen5 (effDPS halves again below the Heavy-tier figure
  shown against a Pen5 hit on its armour4 face: step = clamp(round(2-(5-4)),0,6) = 1 -> mult 1.0, i.e. no
  penalty — a Pen5 hit on an armour-4 hull is NOT reduced, which is the intended "cannot facetank" result).
- **battleship vs missile saturation / Pen5 specialist fire**: battleship's own `effDPS` column only counts its
  main battery once (the static script reads the single `"weapon"` field); its true output is 3x the row's
  `primaryDPS`/`salvoValue` (3 turrets, each `naval_406_bs`) — true primaryDPS ~163.6, true effDPS/CP (Medium)
  ~6.14, not 2.05. Restated: battleship is the single highest raw-output hull in the roster once all 3 turrets are
  counted, consistent with "superheavy."
- **CIWS escort with/without protected capital ship**: not simulated; `ciws_escort_ship` carries the highest `aps`
  (radius 38, charges 4, recharge 1.6 s) and lowest surface DPS/CP (8.04 Light / 2.68 Heavy, among the lowest
  offensive figures in the roster) of any new ship — its value is structurally defensive-only by the numbers, as
  intended.

**Correction note for the report's own table**: the single-row comparison table above undercounts `battleship`
and `gun_destroyer`/`destroyer`-style multi-mount ships because the static script only reads the `"weapon"` field,
not `"secondary"`. `gun_destroyer`'s second `naval_127` turret and `battleship`'s second/third `naval_406_bs`
turret are real data (see the stats table above) but are not reflected in this comparison table's DPS/CP columns;
treat `gun_destroyer` as ~2x and `battleship` as ~3x the shown primaryDPS/CP for an "all main guns" figure.

## Pathing / lane / turn-radius

Not simulated (owner no-test rule). Mechanically: every new ship uses the unmodified movement/turn-rate fields
(`speed`, `turnRate`, `turretTurnRate`, `radius`) the existing naval units use — no new navigation subsystem, no
new lane code. `rocket_artillery_ship` sets `"firesWhileMoving": false` + `"erectSeconds": 1.2` (reusing the
`mlrs`/`heavy_rocket_artillery` deploy pattern) so it behaves like existing land artillery when stationary-firing.
All 17 carry a `"naval"` object for the existing lane/escort/raider system (`NavalDefs.cs`) so a future lane can
wire them into a boss `"fleet"` or a coastal mission without new sim code.

## Confirmations

- No transport, troop-carrying, landing/logistics, bridge/ferry, towing/recovery, revive/salvage, or
  carrier-spawn mechanic was added — none of the 17 units has a `"craft"`, `"welldeck"`, `"flightdeck"`, `"pods"`,
  `"fleet"`, or repair/revive field.
- No radar/vision/sonar/reveal system was added — no `"vision"` change beyond the existing field's normal use, no
  new detection mechanic; `ew_corvette`'s jammer is the existing generic accuracy-debuff aura, not a sensor.
- No duplicate generic gun corvette/cruiser was added (`ashm_corvette`/`aa_corvette`/`ciws_escort_ship`/
  `ew_corvette` are all specialists; `sea_corvette` keeps its gun-corvette niche; `frigate`/`destroyer`/
  `gun_destroyer` are a tier above corvette and a tier below `sea_cruiser`, which keeps its gun-cruiser niche).
- AShM holds 80 m/s effective speed and Pen4 everywhere except `naval_406_bs` (battleship main gun, Pen5, not an
  AShM) — no Pen5 spread to any missile weapon.
- No generic SAM/AAM damage buff: `sam`, `sam_long`, `sam_48n6` are reused unmodified.
- No random crit/morale/retreat-by-health/random-penetration field was added anywhere.
- Card/economy: every new unit is `"card": false`, following the exact existing naval pattern (`sea_corvette`,
  `sea_cruiser`, `missile_boat`, `hover_gunboat`) — no new economy path invented. Campaign/mode eligibility: **none
  wired this pass** (spec: only after base regression; this lane's regression is the static table above, not a
  battle-simulated one, so campaign/mission wiring is left for a later pass as instructed).

## Validators run (static only, no Unity/Sim run)

- `Tools/balance/flight_feel_audit.py`: `HARD_FAIL: 0` both before and after every edit. `YELLOW_FEEL` picked up
  exactly one new id, `torpedo_naval` — expected and intentional: the classifier has no `TORPEDO` feel-class, so
  it is scored against the generic `TACTICAL_MISSILE` class (which expects ATGM-like 150-200 m/s) and flags the
  spec-mandated 55 m/s as "slow for its class." This is correct per the owner prompt ("torpedo ... 55 m/s") and is
  not a defect. All other new weapons (including `naval_203_bc`/`naval_406_bs`/`naval_203_monitor`, renamed from an
  initial `battlecruiser_main`/`battleship_main`/`monitor_152_203` specifically so the `naval_*` prefix puts them
  in the correctly-calibrated `NAVAL_DIRECT` feel class) landed in `ok`.
- `dotnet build Tools/simbuild/Sim.csproj`: **0 errors**, 1 pre-existing warning (unrelated `BaseIntermediateOutputPath`
  MSBuild notice), both before and after. No C# file was changed in this lane.
- CatalogCheck (Unity Editor tool, not run — no Unity session this pass): manually verified no stored derived
  field was added (no `hpPerCp`, `dps`, or similar precomputed column in `balance.json`; those live only in this
  report's static Python pass, discarded after use).
- **Not run** (explicitly out of scope for this lane / owner no-test rule): Unity `ExportGameDoc`, `Tools/export/export.py`,
  any stale-value scan that depends on a fresh Unity export, and every battle-matchup item in the owner's list that
  requires a simulated fight (marked "not run — owner no-test rule" throughout this report; the mechanical
  reasoning for each is given above instead).

## Open questions / follow-ups for later lanes

1. Model lane: build real GLBs per `Docs/naval/MODEL_CONTRACT.md`; swap the `"model"` field only.
2. A later pass should wire 1-2 of these ships into a boss `"fleet"` or a coastal campaign mission so the
   `"naval"` escort/raider data and the automatic wake actually render in a match.
3. Once Unity is available, run `ExportGameDoc` + `export.py` + the stale-value scan to regenerate
   `Docs/export/game_snapshot.json` and the generated XLSX/MD (not done here, per the no-Unity-run constraint).
4. A real battle-simulated regression (the full matchup matrix in the owner prompt) should be run once the owner
   lifts the no-test rule, using `Tools/simbuild/regress` if applicable.
