# Naval FINAL spec: test plan (09/10)

The naval lane wrote these checks but did not run them. The lead runs them after the merge (the owner allowed tests for this work on 09/10).
The naval lane ran only the static checks listed at the end.

## 1. Build the headless harness (no Unity)

```
dotnet build Tools/simbuild/regress -o Temp/regress
```

## 2. Naval regression suite (headless Sim, fixed seeds)

From the repository root (Git Bash):

```
MB_SEEDS=1,2,3,4,5 Temp/regress/MachineBrigade.Tests.EditMode.exe naval Assets/MachineBrigade/Resources/Data/balance.json Assets/MachineBrigade/Resources/Data/tunables.json Temp/naval_suite.tsv
```

- Set `MB_SET` to `duel`, `aa`, `shore`, `capital`, `ew`, `budget`, `formation`, `lane`, `wreck`, `target` or `perf` to run one set only. Without it, every set runs.
- `MB_SEEDS` defaults to `1,2,3,4,5`. The same seed gives the same result. The `hash_seed1` column holds the state hash for determinism checks.
- The output is a TSV file with one row per matchup, averaged over the seeds. The console shows each matchup name as it finishes.

Static economy table (no simulation, a few seconds):

```
Temp/regress/MachineBrigade.Tests.EditMode.exe naval-econ Assets/MachineBrigade/Resources/Data/balance.json Assets/MachineBrigade/Resources/Data/tunables.json Temp/naval_econ.tsv
```

### What the suite covers (Tools/simbuild/regress/Naval.cs, `Matrix`)

Maps:
- **Coast:** the Sandbox's coastal range. The shore is at x = 90 and the lanes are near 106, mid 120 and far 134.
- **Narrow:** a 22 m channel with one lane, built in the harness.

Side A starts at z = -gap/2 and side B at +gap/2. Ships start on their own patrol lane, towers on the shore, aircraft and launchers inland. Both sides use the Sandbox "Combat" AI.

| set | rows |
|---|---|
| duel | prompt H and spec 9 duels: hover_gunboat / river_patrol_boat vs torpedo_boat; sea_corvette vs ashm_corvette (close 40 m, long 130 m); ashm_corvette vs sea_corvette + ciws_escort_craft; frigate vs sea_corvette; missile_frigate vs frigate; destroyer vs frigate; gun_destroyer vs missile_destroyer (close, long); cruiser branches vs destroyer; battlecruiser vs both cruiser branches; monitor vs destroyer / missile_destroyer; torpedo boats vs destroyer; specialist failure duels (aa_frigate, aa_destroyer, ew_corvette, ciws_escort_craft); anchor niches (missile_boat, river_gunboat) |
| aa | aa_corvette / aa_frigate / aa_destroyer vs scout_heli, attack_helicopter, fighter_jet, attack_jet and a cruise missile (ground_cruise_missile_vehicle); a frigate control row |
| shore | rocket_artillery_ship vs gun_turret, repair_bay, a moving sea_corvette and a closing torpedo_boat; naval_monitor vs gun_turret / repair_bay; gun_destroyer shore bombardment |
| capital | battleship vs concentrated AShM (3 ashm_corvette, 2 missile_destroyer), torpedoes (3 torpedo_boat), heavy guns (2 gun_destroyer, sea_cruiser.gun), battlecruiser |
| ew | the same group with and without the ew_corvette under the same AShM attack (compare side A's damage taken) |
| budget | equal-CP fills (36 / 42 / 30 / 28 / 46 CP) when both sides are CP-costed |
| formation | 3-ship and 5-ship groups; the mixed escort group (battleship + aa_destroyer + ciws_escort_craft + ew_corvette) |
| lane | the narrow channel with 3 v 3 and with battleship + CIWS vs 2 destroyers |
| wreck | a ship sunk (2 % HP, held fire) ahead of a column on the same lane, on the coast and in the narrow lane |
| target | battleship vs a 5 % HP river_patrol_boat + destroyer; missile_destroyer vs a 10 % HP torpedo_boat + frigate; salvo overkill with 2 missile_destroyers or 3 torpedo boats against one frigate |
| perf | missile saturation: 6 missile_destroyer + 4 missile_frigate vs battleship + 2 aa_destroyer + 2 ciws_escort_craft |

Columns of the suite TSV (QA guide section 1):
- `cpA` / `cpB`, `seeds`, `expect` (A / B / -), `winA` / `winB` / `draw`
- `verdict`: `as_expected` or `UNEXPECTED` when the expected side did not win most seeds; `record` when the row only records.
- `first_shot_*`, `time_to_range_*`: time until a ship has an enemy inside its main weapon's range.
- `ttk_s`: from the first hit on the loser to the end.
- `end_s`, `survivors_*`, `hp_left_*`
- `damage_by_source`: top 6 `side:weapon=damage`.
- `shots_by_weapon`: the ammunition used.
- `intercepts_A/B`: interceptions by that side's point defence.
- `target_switches`
- Pathing: `stuck` (StuckWatch episodes), `off_water` (a ship's position off the sea), `reverse`, `turn_over_rate` (a turn faster than 1.25 x the ship's rate).
- `range_ratio_*`: the ship's distance to its target / its main range, while it has one.
- `big_salvos` / `overkill_salvos` / `cheap_target_salvos`: naval main salvos of 600 HP or more a pull. Overkill means damage in flight was more than 1.15 x the target's HP. A cheap target is light or scout and worth less than 8 CP.
- `first_main_target_A`, `wreck_clearance_m`, `peak_projectiles`, `step_ms_avg/max`, `hash_seed1`

What counts as a failure:
- a `verdict` of `UNEXPECTED`
- any `off_water`, `reverse` or `turn_over_rate` above 0
- `stuck` above 0 in the lane and wreck rows
- `cheap_target_salvos` above 0 in the battleship target row while the destroyer lives

These are material regressions to fix before `ExportGameDoc` / `export.py`.

## 3. EditMode tests (Unity Test Runner)

Run `Assets/MachineBrigade/Tests/EditMode/NavalFinalTests.cs` (class `MachineBrigade.Tests.NavalFinalTests`) in the Unity Test Runner (EditMode). It checks:
- the 18 ids exist, the old ids are gone, the ASW / submarine ids are absent, and the renamed ships keep their models
- the spec weapon ids, with no boss weapon on a ship
- every player AShM is Pen 4 at 80 m/s, and the torpedo is slower than every AShM
- long SAM 115 m/s, battleship 3 x 200 simultaneous
- no player naval Armour 5, battleship Armour 4
- CP equals the spec and rises tier by tier
- HP ratios against the anchors
- every ship has an aiBehaviour role and the expected DoctrineRole, a patrol lane and astern escorts
- armed ships fire on the move with no stand-still reload
- the naval salvo guard, and no transport / fleet / aircraft spawning

Also run the existing suites the change touches:
- `AiMasterP2Tests`: the `CombatRoleDoctrine.Worth` signature gained an optional `navalSalvo` parameter.
- `CardRenderTests`: manifest entries were renamed and `sea_cruiser.gun` was added.
- `TunablesTests`: two new keys.
- `ReplayHashTests`: NavalSystem escort stance, only when a ship's data sets `patrol` or a negative `station`.

## 4. After the runs pass

Then run Unity `ExportGameDoc`, `Tools/export/export.py` and the stale-value scan. They regenerate `Docs/export/game_snapshot.json`; after that the 18 ids appear in `runtime_node_audit.py`. The naval lane did not run any of these (brief: no export).

## 5. What the naval lane ran (static only)

- `dotnet build Tools/simbuild/Sim.csproj`: 0 errors. The regress harness builds with 0 errors.
- Sim, Game, Editor and EditMode tests compiled against the Unity 6 DLLs (`literal_to_tunable._editor_tests`): 0 new errors.
- Catalog parse (`regress load`, the CatalogCheck rule): OK, 197 vehicles, 378 weapons.
- `Tools/balance/flight_feel_audit.py`: HARD_FAIL 0, no naval YELLOW.
- A scratch mount check of data weapons per slot against GLB `Mount_*` pivots: 0 hard, 3 idle mounts.
- `glb_check --only` on the renamed-id models: 0 errors.
- `barrel_audit.py` regenerated.
- `naval-econ`: static arithmetic, no simulation.
