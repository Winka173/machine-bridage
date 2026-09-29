
## 15B. Prompt 16: old bosses' new weapons, escorts for every boss (2026-09-29)

Prompt 16 parts E and F (branch feature/p16-escorts, from lead/integration 279c11e). Parts A-D (Lighthouse Bay,
Leviathan and its fleet) are another branch; the escort system below is the one Leviathan's fleet can use.

### E. The thin bosses' new weapons

Every new weapon follows the calibre scale (13C) and the damage types and penetration levels (14A), and is a part
(prompt 9) where the boss has a place for it, so breaking it takes it away. Parts stay 7-15 % of the body each and at
most 70 % in all (prompt 9's rule; `BossPartsTests` holds it).

| boss | new weapon | how it works | its part (share) | what breaking it does |
|---|---|---|---|---|
| Iron Train | mortar car (`train_mortar`, 2B11 120 mm twin, HE, pen 2) | a flatcar coupled behind the gun wagon; indirect, so it hits what hides behind cover (no line of fire needed) | `mortar_car` 10 % | the mortar falls silent |
| Tempest | interceptor laser (APS, `laser: true`, `rockets: true`: 26 m, 2 shots, 1.6 s) | Energy: burns missiles, drones and rockets out of the air round it (and round anything of its side within 26 m); smoke blinds it (14A C.6) | `interceptor` 8 % (the modelled launchers on the turret sides) | no more interceptions |
| Behemoth | hard-kill APS (11 m, 2 shots, 4 s) | direct-fire missiles and rockets only (a Trophy's): the anti-tank missile answer | `aps` 7 % (a place on the turret roof) | no more interceptions |
| Inferno | fire trail (`fireTrail`: a patch every 4 m, 3.5 m across, 18 dps Burn) | lit for 10 s, burns 8 s: the ground fires' time a fifth shorter (12A), the same in the sim and the view | `fuel` 8 % (its fuel tanks) | no more trail |
| Hive | jamming aura (`jammer: 30`) | the player's guided rounds fired from or aimed within 30 m of it are scrambled (they miss by 5-11 m: against its 7.5 m hull about half still hit) | `jammer` 8 % (a mast on the roof) | guided rounds fly true again |
| Bastion | twin Kornet mount (`kornet_twin`) | a roof launcher, all round | `kornet` 8 % | silent |
| Doomsday Train | rocket car (`boss_rockets`, Grad) and long-range SAM car (`sam_battery`, Patriot, 90 m) | two flatcars behind the missile wagon | `rocket_car` 10 %, `sam_car` 10 % | each falls silent |
| Rail Supergun | two AA mounts (`hover_ciws`, AK-630) on the bed's rear corners | shoot aircraft (and ground within 34 m) | `aa_l`, `aa_r` 7 % each; tractors 10 → 8 %, fire control 12 → 9 %, main gun 15 → 14 % | each falls silent |
| Landing hovercraft | two more CIWS (AK-630) that also intercept (APS 22 m, 3 shots, 1.5 s: missiles, drones, rockets; not shells, bullets or energy) and two 140 mm rocket launchers (`hover_rockets`, A-22 Ogon: 11 x 65, 55 m) | the Zubr's armament | `ciws_l`, `ciws_r`, `rockets_l`, `rockets_r` 7 % each; ramp 14 → 12 %, fans and guns 10 → 7 % | a CIWS broken halves its interceptors (rounded up), both: none; the rockets fall silent |

Kept as they were (the brief): Iron Bird, Spectre, Ice Fortress, Hive Mothership, Silver Bug, Earth Worm, command
airship; the Supreme Commander keeps no weapon worth the name.

New part mechanisms (`stops`): `aps`, `jammer`, `trail`. Unlike the older ones (one part each), these may be carried by
several parts and stop only with the last; a protection system holds its interceptors in proportion to the parts still
standing (`Vehicle.ApsMax`). The view: the Tempest's interceptions are drawn as the Iron Beam's beam from its turret side;
the trail's patches as ground fires (`SimEventKind.FireTrail`); new part kinds `aps`, `ciws`, `fuel`, `ew` have names and
icons. Models (Blender, `Tools/blender/mb_p16_arms.py`, wrapping the current builders): the Iron Train's mortar flatcar,
the Doomsday Train's rocket and SAM cars, the supergun's two CIWS, the hovercraft's two CIWS and two rocket launchers,
the Bastion's Kornet launcher; the other new parts are modelled already (the Tempest's launchers, the Inferno's tanks) or
places on the hull (the Behemoth's APS, the Hive's mast).

**Health retuned** with prompt 9's model (the fire needed is body + 0.7 x parts; each new part adds to it), then a little
lower where the weapon makes the boss harder to hurt (APS, jamming) or deadlier (more guns): Iron Train 4400 → 4150,
Tempest 4750 → 4450, Behemoth 4950 → 4650, Inferno 5800 → 5550, Hive 6350 → 6050, Bastion 9000 → 8600, Doomsday
Train 5450 → 4800, supergun 5500 → 5300, hovercraft 6500 → 5900. KILLTIMES

### F. Escorts for every boss

**One data-driven system** (`BossSystem.Escorts`, balance.json `escortRules` and `escorts`), replacing the old escort
skills (`behemoth_escort`, `fortress_escort`, `gunship_escort`, `nuke_escort`, `supreme_guard`, removed) and Boss Rush's
own escort list (`BossRushRules.Escorts`, removed).

- **Two kinds of wave:** one with the boss (spawned the step after it joins, as the camera turns to it), and one at
  each phase change: the boss's own phase marks (a change counts as its transformation begins), else the table's
  `marks`, else the rules' `[0.5]` (the rage mark most bosses already have); the Earth Worm's (`"on": "surface"`) each
  time it breaks out of the ground.
- **A helper in every wave** (any role but guard and raid): `repair` (an engineer mends the boss 0.3 % of its health a
  second within 12 m of its hull: the Support aura skips bosses, so this is the escorts' own), `jam` (an EW carrier's
  jammer covers it), `cover` (anti-air: flak, SAMs, fighters, a C-RAM), `spot` (it marks every enemy it sees: the boss's
  side deals 15 % more to them and a boss's guns scatter 0.6 as wide at a marked target), `smoke`. Where the brief's
  wave had no helper one was added (below), so the player always chooses between the boss and its helpers.
- **At most 4-6 alive** (`escortRules.cap`: Easy 4, Normal 5, Hard and Very Hard 6, Heroic and Iron 6), counted per
  boss; a wave's helpers come first, then its guards while there is room. **Strength by difficulty:** each vehicle goes
  through the side's elite budget (prompt 8 H, `ForWave`), so harder difficulties bring more elites; a unit marked
  `elite` is always its elite (a boss's signature).
- **Boss Rush:** two fewer alive (at least 3), half of each wave's guards (rounded up; the helpers all come), the guards
  as elites (Boss Rush's escorts were all elites): fewer and stronger, so a fight does not drag.
- **The leash** (28 m, a table may set its own; a raider 1.6 times it): a guard takes on the enemy nearest the boss
  within the leash plus its own reach, those attacking the boss first (their target or order is the boss, or they hit
  it last); past the leash it drops the chase and drives back to its station. **Stations:** guards beside the boss along
  its heading (so a train's run parallel to its rails), helpers behind it away from the enemy (the nearest enemy it sees
  within 80 m, else the enemy's rally), a screen between it and the enemy. The commander AIs leave escorts alone
  (`Vehicle.IsEscort`); when the boss falls they are released to the commander.
- **CP for kills:** 3 CP a guard, 4 a helper, to the side that destroyed it (on top of the usual refund), with a toast.
- **Arrivals:** beside it (default), `para` (air-dropped round it after a 3 s warning ring, the transport and a
  parachute from the unit's `escort_drop.<unit>` event support; a toast "escorts parachuting in"), `edge` (from the map
  edge behind the boss, driving or flying in: for a fleet's aircraft), `place` (at an offset in its frame). A wave may
  `halt` the boss (the Iron Train stops 6 s at a "station" to drop its light tanks) or only `refill` its own losses (the
  Tempest's jammers).
- **Interface (kept minimal, the UI agent owns the rest):** the boss bar shows a shield icon and the count of escorts
  alive (`BattleHud.SetBossEscorts`); an escort wears an orange diamond left of its health bar, shown whether the bar
  is or not (`VehicleView.RenderEscortMark`).
- **Where it is on:** the world's `EscortSettings` (null: none, the bare test battles and the menu's lobby). Missions and
  Boss Rush set Normal's by default; every session then sets its difficulty's (`ModeSession`), Boss Rush's smaller.
- **Checkpoints:** the escorts' groups, waves and members go into `StateHash`; their orders are ordinary sim commands
  (not journaled), so a replay rebuilds them.

**The tables** (arrival · each phase change), from the brief, a helper added where it had none:

| boss | arrival | phase change |
|---|---|---|
| Iron Train | 2 armoured cars beside the rails (one spots) | halts 6 s: 2 light tanks + an engineer |
| Tempest | 2 EW jammers + a SAM launcher | 2 jammers, only replacing those lost |
| Behemoth | 2 battle tanks + an AA gun | an elite heavy tank + an engineer |
| Inferno | 2 flame tanks + a smoke carrier | 2 flame tanks + an engineer |
| Iron Bird | 2 attack helicopters + a scout helicopter (spots) | a scout helicopter (spots) |
| Spectre | 2 fighters (cover) + a recon UAV (spots: its guns tighter) | 2 fighters |
| Ice Fortress | 2 heavy tanks + an engineer | an engineer |
| Hive | a heavy AA gun + a SAM launcher (the "mixed air defence") | 2 FPV carriers + a recon UAV |
| Bastion | air-dropped: a gun turret, an ATGM tower, a C-RAM (cover) | air-dropped: a gun turret + an AA turret |
| Hive Mothership | 2 strike UAVs + a recon UAV | a scout helicopter (spots) |
| Silver Bug (0.66, 0.33) | the beaten generals' elites: Varga's heavy tank, Orlov's Grad + a recon UAV | Sen's FPV carrier + a jammer; then Quạ Đen's attack helicopter + an engineer |
| Doomsday Train | 2 IFVs beside the rails + a scout helicopter | 2 IFVs + a smoke carrier |
| Rail Supergun | 2 patrol tanks + a counter-battery radar (spots); its fixed turrets are its guards, as before | 2 patrol tanks + an engineer |
| Earth Worm | none | each break-out: 2 IFVs and an engineer air-dropped beside it |
| Command airship | 2 fighters (cover) | an attack helicopter + a scout helicopter |
| Landing hovercraft | 2 hover gunboats (one spots) | a gunboat (spots) |
| Supreme Commander | kept as it was: none | at 60 %: 2 elite battle tanks (its command aura is the help) |

The hovercraft's gunboats (`hover_gunboat`: 30 mm CIWS, 520 health, 8.5 m/s, crosses land and water like the
hovercraft) borrow the hovercraft's model at a third of its size until the fleet's fast attack craft (part C) lands:
then point the table at that def or give `hover_gunboat` its model.

**For Leviathan (part C):** its fleet can be one table: `{ "boss": "leviathan", "leash": 60, "arrive": [ { "unit":
"<corvette>", "role": "cover", "count": 2, "slot": "flank" }, { "unit": "<missile_boat>", "role": "raid", "count": 3 } ],
"phases": [ { "units": [ ... landing craft, helicopters ... ], "radio": "..." }, { "units": [ { "unit": "<corvette>",
"role": "cover", "slot": "screen" } ] } ] }` with `"drop": "edge"` for the strike aircraft coming in from the sea, and
`"cap"` raised for it alone. The corvettes' CIWS cover of Leviathan is their own `aps` (it covers anything of their side
within its radius already); "screen" puts them between Leviathan and the shore.

### Tests (short, the owner's rule)

`BossEscortTests`: the mortar car over a house; the three protection systems until their parts break; the fire trail and
its tanks; the Hive's jammer; the new mounts firing (Kornet, rocket and SAM cars, supergun AA, hovercraft rockets); the
escorts' timing, cap, Boss Rush's smaller waves; the leash; the engineer's repair and the escort bounty; every boss has a
table with a helper in every wave; the kill time per changed boss (one seed, the boss alone). Suites kept green:
BossParts, BossPhase, Counter, Armour, CheckpointReplay, Prompt8Content.

### Left for the testing phase

- Kill times over five seeds per boss with a standard deck, with and without escorts, and every boss mission and Boss
  Rush on Normal inside its frame (escorts add enemies: the missions' pace may want the caps or the waves trimmed).
- The escorts' formations on real maps (the trains' rails, the hovercraft's coast, the Bastion's towers dropped on
  rough ground), and the stuck detector over boss missions with escorts.
- FPS and tick time on the heaviest boss fight with a full escort and burning parts (Low, a low-end device).
- The escort icon and bar count on a device (and the UI agent's own escort icons, if it makes them, replacing mine).
