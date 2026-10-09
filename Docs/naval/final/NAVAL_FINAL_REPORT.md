# Naval FINAL spec: implementation report (09/10)

Branch `feature/naval-final` (worktree `MachineBrigade-bal`), from lead `c78effdb7`.

Sources of truth:
- `Docs/naval/final/Machine_Brigade_NAVAL_VEHICLE_EXPANSION_SPEC_FINAL.md`
- `Docs/naval/final/Prompt_IMPLEMENT_NAVAL_EXPANSION_FULL.txt`

These supersede `Docs/naval/PROMPT_owner_vi.md` (06/10). This pass reconciles the 06/10 first pass (17 ships with models, `Docs/naval/NAVAL_DATA_REPORT.md`) to the FINAL spec, starting from the canonical data.

**This lane ran no tests, simulations or measurements.** The owner allowed tests on 09/10, but the lead runs them after the merge. The "Test result" column therefore reads "pending lead run". The commands are in `Docs/naval/final/TEST_PLAN.md`.

All HP below are data values. The runtime applies the catalog's uniform HP scale (x 2.2), which leaves every ratio unchanged.

## K. Ship table

| Ship ID | Role | CP | HP | Armour | Primary weapon ID | Secondary IDs | Primary damage | Pen | Reload/cooldown | Range | Projectile speed | Splash | HP/CP | Intended prey | Intended counter | AI doctrine | Test result |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| torpedo_boat | cheap anti-capital glass cannon | 7 | 520 | [0, 0, 0, 0] | naval_torpedo_light | hmg_roof | 360 x2 (720 / pull) | 4 | 12 s (burst 2 @ 1.4 s) | 65 m (min 12) | 55 m/s | 3 m | 74 | destroyer / cruiser / capital | hover_gunboat, sea_corvette close, aircraft | TD -> TankDestroyer; patrol far; station 24; naval salvo guard | pending lead run |
| ciws_escort_craft | missile / drone interception escort ; aps r36 c3 / 1.8 s | 8 | 580 | [1, 1, 1, 0] | escort_ciws_ak630 | naval_76_selfdef | 12 x1 x3 mounts | 2 | 0.017 s | 34 m | 300 m/s | 0 m | 72 | incoming AShM, rockets, drones | sea_corvette, frigate, heavy direct cannon | Support -> Support; patrol far; station -16 | pending lead run |
| ashm_corvette | light anti-ship missile specialist ; aps r28 c1 / 3 s | 9 | 1440 | [2, 1, 1, 1] | anti_ship_missile_corvette | hover_ciws | 450 x3 (1350 / pull) | 4 | 20 s (burst 3 @ 0.6 s) | 140 m | 80 m/s | 6 m | 160 | frigate / corvette at standoff | sea_corvette close; CIWS-protected group | TD -> TankDestroyer; patrol far; station 30; naval salvo guard | pending lead run |
| aa_corvette | short / medium naval air defence ; aps r30 c2 / 2.6 s | 9 | 1400 | [2, 1, 1, 1] | sam | hover_ciws, hmg_roof | 170 x1 | 2 | 4.452 s | 44 m | 100 m/s | 2 m | 156 | helicopters, drones | dedicated anti-ship craft, gun destroyer | SAM -> AntiAir; patrol far; station 18 | pending lead run |
| ew_corvette | jammer escort (existing jammer aura) ; jammer 30 | 9 | 1300 | [1, 1, 1, 1] | naval_76_selfdef | - | 171 x1 | 3 | 4.643 s | 95 m | 95 m/s | 3 m | 144 | none (protects guided-fire targets) | any equal-CP direct-combat ship | Support -> Support; patrol far; station -24 | pending lead run |
| frigate | general-purpose mainline ; aps r30 c2 / 2.6 s | 11 | 2000 | [2, 2, 2, 1] | naval_100 | anti_ship_missile_light, hover_ciws | 229 x2 (458 / pull) | 3 | 5 s (burst 2 @ 0.5 s) | 90 m | 100 m/s | 3.5 m | 182 | sea_corvette, light craft | destroyer head-on; missile specialist at range | MBT -> MainBattle; patrol near; station 34 | pending lead run |
| missile_frigate | anti-surface missile specialist ; aps r28 c1 / 3 s | 12 | 1950 | [2, 2, 2, 1] | anti_ship_missile_frigate | naval_76, hover_ciws | 450 x5 (2250 / pull) | 4 | 24 s (burst 5 @ 0.5 s) | 140 m | 80 m/s | 7 m | 162 | frigate at standoff | gun destroyer in gun range; interception-heavy group | TD -> TankDestroyer; patrol far; station 36; naval salvo guard | pending lead run |
| aa_frigate | medium area air defence ; aps r32 c2 / 2.2 s | 12 | 2000 | [2, 2, 2, 1] | sam_long | hover_ciws, naval_76 | 320 x2 (640 / pull) | 3 | 5.73 s (burst 2 @ 0.5 s) | 55 m | 120 m/s | 2 m | 167 | jets, helicopters | missile frigate / destroyer in a surface duel | SAM -> AntiAir; patrol far; station 20; naval salvo guard | pending lead run |
| rocket_artillery_ship | naval fire support (MLRS) | 12 | 1700 | [2, 1, 1, 1] | naval_mlrs_salvo | hmg_roof | 100 x8 (800 / pull) | 3 | 15.9 s (burst 8 @ 0.25 s) | 110 m (min 20) | 85 m/s | 4.9 m | 142 | shore towers / structures, clusters | fast attack craft that closes; destroyer | MLRS -> FireSupport; patrol far; station -30; naval salvo guard | pending lead run |
| naval_monitor | slow heavy gun / shore bombardment ; aps r26 c1 / 3 s | 13 | 2900 | [3, 3, 2, 2] | naval_203_monitor | hover_ciws | 360 x1 | 4 | 7 s | 62 m (min 10) | 65 m/s | 5.5 m | 223 | towers, structures, medium ships | long-range AShM, air | Heavy -> MainBattle; patrol near; station 36 | pending lead run |
| destroyer | heavy general-purpose (naval MBT) ; aps r30 c2 / 2.6 s | 14 | 2800 | [3, 3, 2, 2] | naval_127 | anti_ship_missile_quad, sam, hover_ciws | 286 x2 (572 / pull) | 3 | 5.143 s (burst 2 @ 0.5 s) | 110 m | 90 m/s | 6 m | 200 | frigate, corvettes | gun cruiser; AShM concentration | MBT -> MainBattle; patrol mid; station 40 | pending lead run |
| gun_destroyer | surface brawler / bombardment ; aps r28 c2 / 2.6 s | 14 | 2850 | [3, 3, 2, 2] | naval_127_gd | sam, hover_ciws | 286 x2 x2 mounts (572 / pull) | 3 | 9.53 s (burst 2 @ 0.5 s) | 110 m | 90 m/s | 6 m | 204 | corvette / frigate, structures | missile destroyer at standoff | Heavy -> MainBattle; patrol near; station 40 | pending lead run |
| missile_destroyer | heavy anti-surface standoff ; aps r30 c2 / 2.6 s | 15 | 2700 | [3, 2, 2, 2] | anti_ship_missile_destroyer | naval_100, sam, hover_ciws | 450 x7 (3150 / pull) | 4 | 26 s (burst 7 @ 0.45 s) | 140 m | 80 m/s | 8 m | 180 | destroyers, cruisers | gun destroyer closing; interception | TD -> TankDestroyer; patrol far; station 42; naval salvo guard | pending lead run |
| aa_destroyer | high-end fleet air defence ; aps r34 c3 / 2 s | 15 | 2800 | [3, 3, 2, 2] | sam_48n6 | sam_long, hover_ciws, naval_100 | 630 x1 | 3 | 7.2 s | 95 m (min 20) | 115 m/s | 6 m | 187 | jets, cruise missiles | surface destroyer / cruiser when isolated | SAM -> AntiAir; patrol far; station 22; naval salvo guard | pending lead run |
| sea_cruiser.gun | heavy gun cruiser (sea_cruiser branch) ; aps r30 c2 / 2.4 s | 17 | 3600 | [4, 3, 3, 2] | cruiser_203 | hover_ciws | 600 x2 x2 mounts (1200 / pull) | 4 | 16.857 s | 105 m | 85 m/s | 8 m | 212 | destroyers, structures | AShM concentration | Heavy -> MainBattle; patrol mid; station 38; naval salvo guard | pending lead run |
| sea_cruiser.missile | heavy missile cruiser (sea_cruiser branch) ; aps r30 c2 / 2.4 s | 18 | 3500 | [3, 3, 3, 2] | anti_ship_missile_cruiser | naval_100, sam_long, hover_ciws | 450 x8 (3600 / pull) | 4 | 28 s (burst 8 @ 0.45 s) | 140 m | 80 m/s | 7 m | 194 | destroyers, cruisers | battlecruiser, gun ships closing | TD -> TankDestroyer; patrol far; station 38; naval salvo guard | pending lead run |
| battlecruiser | fast capital, gun emphasis ; aps r30 c2 / 2.4 s | 19 | 4400 | [4, 3, 3, 2] | naval_203_bc | anti_ship_missile_quad, sam, hover_ciws | 420 x2 (840 / pull) | 4 | 7.5 s | 105 m | 85 m/s | 8 m | 232 | cruisers | battleship; concentrated AShM | Heavy -> MainBattle; patrol mid; station 30; naval salvo guard | pending lead run |
| battleship | superheavy frontline capital ; aps r32 c2 / 2.2 s | 23 | 5800 | [4, 4, 4, 3] | naval_406_bs | sam, hover_ciws | 200 x3 x3 mounts (600 / pull) | 5 | 11 s | 105 m | 85 m/s | 8 m | 252 | battlecruiser, cruisers | concentrated Pen 4 AShM / torpedo | Heavy -> MainBattle; patrol mid; station 44; naval salvo guard | pending lead run |

How to read the AI doctrine column:
- The `aiBehaviour.units` role id comes first, then the `DoctrineRole` it maps to (`CombatRoleDoctrine.BaseRole`).
- `patrol` is the lane the ship holds when it has no flagship: far for standoff, near for the gun envelope off the shore, mid for capitals.
- `station` is the escort station on a flagship. A negative station keeps the ship astern, so it never leads.
- "naval salvo guard": the ship's main battery fires 600 HP or more a trigger pull. Its main salvo treats a cheap (under 8 CP) light, scout, support or drone target as a last resort while anything better is in reach.

## Economy (static, `regress naval-econ`, runtime catalog values, no simulation)

Column notes:
- HP is runtime HP (x 2.2).
- `alpha` is the main battery's damage a trigger pull, over every mount of the main weapon.
- `eff_dps` is sustained main-battery DPS x `DamageTable.Effective` (penetration and damage-type tables) against the prey's front armour.
- Lifetime = HP / the counter's effective main-battery DPS (one counter ship, main weapon only).
- Ships with cp 0 are the fleet anchors, which are never bought, so their per-CP values are n/a.

| ship | cp | hp | armour_F | primary | main_mounts | alpha | alpha_per_cp | dps_raw | hp_per_cp | prey | eff_dps_vs_prey | eff_dps_per_cp | intercepts_per_min_per_cp | counter | counter_eff_dps | lifetime_vs_counter_s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| river_patrol_boat | 6 | 990 | 0 | mg_jeep | 1 | 10 | 1.58 | 58.6 | 165.00 | torpedo_boat | 70.3 | 11.71 | 0.00 | river_gunboat | 64.1 | 15 |
| river_gunboat | 11 | 3150 | 2 | gun_100_river | 1 | 229 | 20.82 | 53.4 | 286.40 | river_patrol_boat | 64.1 | 5.83 | 0.00 | frigate | 83.3 | 38 |
| hover_gunboat | 0 | 1144 | 1 | hover_ciws | 1 | 12 | n/a (cp 0) | 119.6 | n/a (cp 0) | torpedo_boat | 172.3 | n/a (cp 0) | n/a (cp 0) | sea_corvette | 79.8 | 14 |
| missile_boat | 0 | 924 | 1 | boat_rockets | 1 | 320 | n/a (cp 0) | 39.6 | n/a (cp 0) | sea_corvette | 25.7 | n/a (cp 0) | n/a (cp 0) | hover_gunboat | 143.6 | 6 |
| sea_corvette | 0 | 3520 | 3 | naval_76 | 1 | 342 | n/a (cp 0) | 66.5 | n/a (cp 0) | ashm_corvette | 66.5 | n/a (cp 0) | n/a (cp 0) | frigate | 70.8 | 50 |
| sea_cruiser | 0 | 5720 | 3 | cruiser_203 | 2 | 2400 | n/a (cp 0) | 142.4 | n/a (cp 0) | destroyer | 142.4 | n/a (cp 0) | n/a (cp 0) | missile_destroyer | 109.8 | 52 |
| torpedo_boat | 7 | 1144 | 0 | naval_torpedo_light | 1 | 720 | 102.86 | 53.7 | 163.43 | destroyer | 69.9 | 9.98 | 0.00 | hover_gunboat | 172.3 | 7 |
| ciws_escort_craft | 8 | 1276 | 1 | escort_ciws_ak630 | 3 | 36 | 4.50 | 358.9 | 159.50 | strike_drone | 107.7 | 13.46 | 4.54 | sea_corvette | 79.8 | 16 |
| ashm_corvette | 9 | 3168 | 2 | anti_ship_missile_corvette | 1 | 1350 | 150.00 | 63.7 | 352.00 | frigate | 76.4 | 8.49 | 2.33 | sea_corvette | 66.5 | 48 |
| aa_corvette | 9 | 3080 | 2 | sam | 1 | 170 | 18.89 | 38.2 | 342.22 | attack_helicopter | 51.5 | 5.73 | 2.79 | ashm_corvette | 76.4 | 40 |
| ew_corvette | 9 | 2860 | 1 | naval_76_selfdef | 1 | 171 | 19.00 | 36.8 | 317.78 | missile_boat | 44.2 | 4.91 | 0.00 | frigate | 99.9 | 29 |
| frigate | 11 | 4400 | 2 | naval_100 | 1 | 458 | 41.64 | 83.3 | 400.00 | sea_corvette | 70.8 | 6.43 | 2.28 | destroyer | 101.4 | 43 |
| missile_frigate | 12 | 4290 | 2 | anti_ship_missile_frigate | 1 | 2250 | 187.50 | 86.5 | 357.50 | frigate | 103.8 | 8.65 | 1.75 | gun_destroyer | 114.1 | 38 |
| aa_frigate | 12 | 4400 | 2 | sam_long | 1 | 640 | 53.33 | 102.7 | 366.67 | attack_jet | 138.7 | 11.56 | 2.44 | missile_frigate | 103.8 | 42 |
| rocket_artillery_ship | 12 | 3740 | 2 | naval_mlrs_salvo | 1 | 800 | 66.67 | 45.3 | 311.67 | gun_turret | 61.6 | 5.14 | 0.00 | torpedo_boat | 69.9 | 54 |
| naval_monitor | 13 | 6380 | 3 | naval_203_monitor | 1 | 360 | 27.69 | 51.4 | 490.77 | gun_turret | 82.3 | 6.33 | 1.62 | missile_destroyer | 109.8 | 58 |
| destroyer | 14 | 6160 | 3 | naval_127 | 1 | 572 | 40.86 | 101.4 | 440.00 | frigate | 101.4 | 7.24 | 1.79 | sea_cruiser.gun | 142.4 | 43 |
| gun_destroyer | 14 | 6270 | 3 | naval_127_gd | 2 | 1144 | 81.71 | 114.1 | 447.86 | frigate | 114.1 | 8.15 | 1.79 | missile_destroyer | 109.8 | 57 |
| missile_destroyer | 15 | 5940 | 3 | anti_ship_missile_destroyer | 1 | 3150 | 210.00 | 109.8 | 396.00 | destroyer | 109.8 | 7.32 | 1.67 | gun_destroyer | 96.9 | 61 |
| aa_destroyer | 15 | 6160 | 3 | sam_48n6 | 1 | 630 | 42.00 | 87.5 | 410.67 | attack_jet | 118.1 | 7.88 | 2.20 | gun_destroyer | 96.9 | 64 |
| sea_cruiser.gun | 17 | 7920 | 4 | cruiser_203 | 2 | 2400 | 141.18 | 142.4 | 465.88 | destroyer | 142.4 | 8.37 | 1.59 | missile_destroyer | 93.3 | 85 |
| sea_cruiser.missile | 18 | 7700 | 3 | anti_ship_missile_cruiser | 1 | 3600 | 200.00 | 115.6 | 427.78 | destroyer | 115.6 | 6.42 | 1.50 | battlecruiser | 112.0 | 69 |
| battlecruiser | 19 | 9680 | 4 | naval_203_bc | 1 | 840 | 44.21 | 112.0 | 509.47 | sea_cruiser.gun | 95.2 | 5.01 | 1.42 | battleship | 163.6 | 59 |
| battleship | 23 | 12760 | 4 | naval_406_bs | 3 | 1800 | 78.26 | 163.6 | 554.78 | battlecruiser | 163.6 | 7.11 | 1.27 | missile_destroyer | 93.3 | 137 |

Reading:
- **Existing ships keep their niches.**
  - `sea_corvette` and `sea_cruiser` are untouched cp-0 fleet anchors (the Leviathan fleet still names them).
  - `river_gunboat` keeps the highest HP/CP of any light hull (286).
  - `river_patrol_boat` keeps the best effective DPS/CP against light craft (11.7).
  - `hover_gunboat` keeps the best anti-torpedo-boat output (172 eff DPS; it is the torpedo boat's counter).
  - `missile_boat` keeps cheap rocket harassment.
- **Specialists are not generalists.**
  - AShM alpha/CP: corvette 150 < frigate 187.5 < cruiser 200 < destroyer 210. The generalists' AShM is light (2 x 450) or quad (4 x 450).
  - The AA ships have no AShM.
  - The gun destroyer's main output is 114.1 against the destroyer's 101.4 (+12.5 %), with no AShM.
  - The EW and CIWS ships carry only a self-defence 76 mm (half rate).
- **HP/CP rises by tier**: 72-74, then 144-160, 142-182, 223 (monitor: high HP for cost), 180-200, 194-212, 232 (battlecruiser), 252 (battleship).
- **Glass cannon**: the torpedo boat lives about 7 s under the hover gunboat's fire.

## Canonical files changed

- `Assets/MachineBrigade/Resources/Data/balance.json`, edited as text:
  - the naval `weapons` block (15 rows)
  - the naval `vehicles` block (18 ships)
  - `aiBehaviour.units` (18 explicit entries)
- `Assets/MachineBrigade/Resources/Data/tunables.json`: `ai.roleDoctrine.navalSalvoMinAlpha` 600 HP and `ai.roleDoctrine.navalSalvoMinWorth` 8 CP.
- Sim (doctrine mapping only):
  - `Sim/AI/P2/CombatRoleDoctrine.cs`: `NavalSalvo()`, plus an optional `navalSalvo` parameter on `Worth` (the guard applies to TankDestroyer / MainBattle).
  - `Sim/Combat/CombatSystem.P2.cs`: a ship's main battery is every mount of its main weapon, and the call passes `navalSalvo`.
  - `Sim/Content/NavalDefs.cs` and `Catalog.Naval.cs`: `NavalDef.Patrol` (data "patrol").
  - `Sim/Bosses/NavalSystem.cs`: a negative station means astern of the flagship; with no flagship the escort patrols its own `patrol` lane (default "near", as before).
  - `Sim/Content/SimTunables.AiMasterP2.cs`: the two keys.
- UI and assets:
  - `Game/Hud/Strings.cs`: names vi/en for the renamed and new ids; the old keys removed.
  - `Resources/UI/Cards/manifest.json`: ids renamed with the same model and picture; `sea_cruiser.gun` added on the `sea_cruiser` picture.
  - `Docs/models/barrel_audit.json`: regenerated.
- Tools:
  - `Tools/balance/flight_feel_audit.py`: `TORPEDO` feel class, band 0.9-2.5 s.
  - `Tools/simbuild/regress/Naval.cs` and `Program.cs`: modes `naval` and `naval-econ`.
- Tests: `Assets/MachineBrigade/Tests/EditMode/NavalFinalTests.cs` (compile only). Its `.meta` is left to Unity / the lead.

### Renames

Every reference was updated: AI map, strings vi/en, card manifest, deck codex (data-driven: `def.Naval != null`) and barrel audit. The exporter has no per-id table.

| old id | new id | model (kept) |
|---|---|---|
| `ciws_escort_ship` | `ciws_escort_craft` | `ciws_escort_ship.glb` |
| `heavy_monitor` | `naval_monitor` | `heavy_monitor.glb` |
| `missile_cruiser` (06/10) | `sea_cruiser.missile` | `missile_cruiser.glb` |
| (new) | `sea_cruiser.gun` | `sea_cruiser.glb` |

The GLB names, Blender builders, `Docs/art/models.json` and `Tools/assets/baseline.json` stay keyed by model name.

`Docs/export/game_snapshot.json` is generated and still lists the old ids until the next `ExportGameDoc`.

### Cruiser variants (the variant mechanism)

Dotted vehicle ids with `"inherits"` are the project's vehicle variant mechanism (the towers' rank-7 branches, `Catalog.Inherited`). The UI resolves `unit.<dotted id>` names directly.

- `"branchOf"` is not set. It belongs to the tower roster (`TowerRoster`, `BaseLoadout`, `CardId`).
- `sea_cruiser.gun`:
  - takes sea_cruiser's hull, `cruiser_203` x 2 turrets and CIWS;
  - CP 17, HP 3600, armour [4, 3, 3, 2], speed 4.0;
  - full size (`scale` 1), radius 8, no part damage.
- `sea_cruiser.missile`:
  - is the 06/10 `missile_cruiser` hull and model with the variant's own weapons;
  - CP 18, HP 3500, armour [3, 3, 3, 2].
- **Decision on the 06/10 `missile_cruiser`:** it became `sea_cruiser.missile`. The old id is gone.
- `sea_cruiser` itself (cp 0, the Leviathan fleet escort) is unchanged.

## Exact new weapon ids (inherited vs overridden fields)

| weapon id | inherits | overridden | inherited / kept |
|---|---|---|---|
| `naval_torpedo_light` | - (own row; renamed from 06/10 `torpedo_naval`) | all: Pen 4 ShapedCharge, 360 x 2, cd 12, range 65 / min 12, 55 m/s, splash 3, targets Ground | - |
| `anti_ship_missile_corvette` | `anti_ship_missile` (`weaponFamily` "") | burst 3 @ 0.6, cd 20, splash 6 | Pen 4, 450, range 140, 80 m/s, Loft |
| `anti_ship_missile_light` | `anti_ship_missile` | burst 2 @ 1.0 | cd 30, splash 7, Pen 4, 80 m/s |
| `anti_ship_missile_quad` | `anti_ship_missile` | burst 4 @ 0.6 | cd 30, splash 7, Pen 4, 80 m/s |
| `anti_ship_missile_frigate` | `anti_ship_missile` | burst 5 @ 0.5, cd 24 | splash 7, Pen 4, 80 m/s |
| `anti_ship_missile_destroyer` | `anti_ship_missile` | burst 7 @ 0.45, cd 26, splash 8 | Pen 4, 80 m/s |
| `anti_ship_missile_cruiser` | `anti_ship_missile` | burst 8 @ 0.45, cd 28 | splash 7, Pen 4, 80 m/s |
| `escort_ciws_ak630` | `hover_ciws` | targets Air (aircraft and drones; no surface fire) | AK-630 family 300 m/s, 12 dmg, clip 60 |
| `naval_127_gd` | `naval_127` | cd 9.53 (two mounts = 1.125 x the destroyer's one) | 286 x 2, Pen 3, 110 m, 90 m/s |
| `naval_76_selfdef` | `naval_76` | burst 1 (half rate) | 171, Pen 3, 95 m, 95 m/s |
| `naval_mlrs_salvo` | `mlrs_rockets` | burst 8 @ 0.25, cd 15.9 (same rockets a second as the MLRS), spread 3.0, ammo 0 | 100, Pen 3, 110 / min 20, 85 m/s, splash 4.9 |
| `naval_203_monitor` (kept) | `gun_203_siege` | + ammo 0 (was a 12-round stand-still magazine) | 360, cd 7, splash 5.5, Structure x 2.4 |
| `naval_203_bc` (kept) | `cruiser_203` | unchanged | 420 x 2 barrels simultaneous, cd 7.5 |
| `naval_406_bs` (kept) | `cruiser_203` | + caliberMm 406 (was the parent's 203) | 3 barrels SIMULTANEOUS x 200 = 600 a volley, Pen 5, cd 11, 85 m/s |

Removed 06/10 ids, with no references left:
- `torpedo_naval`
- `ashm_corvette_salvo`
- `frigate_ashm`
- `ashm_quad`
- `missile_frigate_salvo`
- `missile_destroyer_salvo`
- `missile_cruiser_salvo`

Reused unchanged:
- `naval_76`, `naval_100`, `naval_127`, `cruiser_203`
- `hover_ciws`, `hmg_roof`
- `sam` (short, 100 m/s), `sam_long` (medium, 120 m/s), `sam_48n6` (long, 115 m/s)

None of these is boss-only.

## Rule checks

- **One primary, at most one secondary capability.** MG, CIWS gun, `aps` and the short `sam` count as self-defence.
  - frigate: gun + light AShM. Its SAM was dropped.
  - missile_frigate: AShM + 76 mm. SAM dropped; `aps` 1 charge, weaker than the frigate's.
  - destroyer: the spec's named exception, with quad AShM + short SAM + limited CIWS.
  - battlecruiser: gun + quad AShM. Its medium SAM became the short `sam`.
  - battleship: its secondary AA is `sam` + 2 CIWS (was `sam_long`); `aps` 2 charges (was 3).
  - ew_corvette: its SAM was dropped.
  - Three model mounts are now idle (frigate and missile_frigate second missile pivot, ew_corvette SAM pedestal).
- **Armour.** No player naval Armour 5. The battleship is [4, 4, 4, 3] (was 5 front).
- **AShM, torpedo and guns.** AShM Pen 4 / 80 m/s. The torpedo runs at 55 m/s. Heavy gun shells keep 85-90 m/s. Long SAM stays at 115.
- **Pen 5 / owner exception.** Pen 5 is only on `naval_406_bs`, the owner's 06/10 exception, kept.
- **Battleship turrets.** The triple turrets are kept: 3 x 200 simultaneous.
- **No idle armed ship.**
  - `rocket_artillery_ship` now fires on the move with no erect time. A ship on patrol never stops, so the land stop-to-fire rule would have idled it.
  - The naval magazine weapons have no stand-still reload, for the same reason.
- **Torpedo boat targets.** `torpedo_boat` is `navalOnly`: the torpedo is never spent on land targets, and its MG hits ships only ("weak vs air").
- **Hard constraints (§A, §I).**
  - No transport, radar, sonar, revive, salvage, recovery or terrain mechanic.
  - No new vision layer. The EW corvette uses the existing `Def.Jammer` aura.
  - Boss data and boss armour untouched; the six anchors and `landing_craft` unchanged.
  - Locked tables untouched.
  - No crit, morale, retreat-by-health, random penetration or cook-off.

## AI behaviour (spec §7 / prompt §F) with existing systems

Ship movement is the naval system's lane steering (Escort / Raider / Patrol). `MovementSystem` skips `Def.Naval` units, so the land roles' engage bands do not move ships.

| requirement | how it is met |
|---|---|
| missile ships keep standoff | They patrol the far lane. AShM range is 140 m against 62-110 m for the guns. |
| gun ships close to their envelope | Gun ships patrol the near lane, the closest to the shore. The capitals take the mid lane. |
| AA escorts near valuable groups | Short escort stations on the flagship (18-22 m). |
| CIWS escort does not lead | Station -16: always astern of the flagship (new, `NavalSystem.Escort`). |
| EW corvette protected, does not duel | Station -24 astern, Support doctrine, self-defence gun only. |
| artillery min range + relocate | Min range 20 m and the FireSupport ladder; continuous patrol movement. A threat-triggered scoot for ships would need new naval steering; not added. |
| monitor no chase | Ships never pursue: the naval system steers to lane goals only. |
| capital target value / no salvo waste | Naval salvo guard on every main-battery mount. It is a multiplier, so a lone target is still shot. |
| overkill reservation | The generic guard covers torpedo / AShM / heavy-gun salvos (`CombatSystem.P0A Overkilled`, P3 planned check). |
| target domain | Weapon `targets` and `navalOnly`. |
| no idle armed unit | Fire on the move; no stand-still reloads; last-resort multipliers never zero. |
| no retreat-by-health / morale | None exists or was added. |

## Conditional ASW / submarine

**`asw_corvette` and `attack_submarine`: BLOCKED_BY_NO_COMPLEX_NEW_MECHANIC.**

The only underwater runtime is the bosses' (prompt 20 J.4: `Vehicle.Burrow` driven by `BossSystem` phases). Player ships have no dive control, depth targeting or detection. Reusing it would need new dive steering and detection, so both ids are omitted.

## Regressions run

None was run by this lane. The commands are in `Docs/naval/final/TEST_PLAN.md`. Static validators run:

| check | result |
|---|---|
| `dotnet build Tools/simbuild/Sim.csproj` | 0 errors |
| `dotnet build Tools/simbuild/regress` | 0 errors |
| Unity assemblies compiled with dotnet (Sim, Game, Editor, EditMode tests) | 0 errors, 0 new |
| CatalogCheck rule (catalog parse, `regress load`) | OK, 197 vehicles, 378 weapons |
| `flight_feel_audit.py` | HARD_FAIL 0; YELLOW 6, all pre-existing, none naval |
| mount check (data weapons per slot vs GLB `Mount_*`, scratch) | 24 ships, 0 hard, 3 idle mounts |
| `glb_check --only` on the renamed-id models | 0 errors |
| `barrel_audit.py` | regenerated |

`runtime_node_audit.py` reads the pre-pass `game_snapshot.json`. Run it after `ExportGameDoc`.

## Remaining warnings / HARD_FAILs

- No HARD_FAIL is known.
- Battle outcomes are unverified until the lead's naval suite. Watch especially:
  - missile_frigate vs frigate;
  - sea_corvette vs ashm_corvette at range;
  - battleship vs 2 missile_destroyers.
- Spec ambiguity on "AShM corvette damage below frigate/destroyer AShM alpha": it was read as below the specialists' (1350 < 2250 / 3150). Under the literal reading the frigate's "limited" AShM (900) would outgun the specialist corvette.
- Three idle model mounts.
- `.meta` for `NavalFinalTests.cs` is left to Unity.
- `sea_corvette`'s armour (front 3) is above the spec's corvette guide. It is an anchor and was not changed.

## Campaign / mode references affected

None. Every naval ship is `"card": false` (AI / codex only).
- The Deck's Naval codex lists ships by `def.Naval`.
- No campaign, mission or mode file names a new or renamed id.
- The Leviathan fleet names only `sea_cruiser` / `sea_corvette`, which are unchanged.

## Exports regenerated / stale scan

Not run, per the brief. `game_snapshot.json` and the generated XLSX/MD are stale for the naval roster. After the regressions pass, run:
1. `ExportGameDoc`
2. `export.py`
3. the stale-value scan
