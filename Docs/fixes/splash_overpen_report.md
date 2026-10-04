# Splash falloff and kinetic overpenetration, 04/10 (lane A): report

Branch `feature/pen5-splash` (worktree MachineBrigade-art), after the Armour/Pen 5 change (`Docs/fixes/armour_pen5_report.md`).
Source: `Docs/prompts/splash_overpen_vi.md` (sections 1-8). Decisions: `Docs/DECISIONS.md` "Armour/Pen 5 and splash/overpen
04/10 (lane A)"; old -> new log: `Docs/export/CHANGES.md` "SPLASH OVERPEN". No Unity run.

## 1. Code / data files changed

- `Assets/MachineBrigade/Resources/Data/balance.json`: `damageTable.splashFalloff` [1.10, 1.08, 1.05, 1.00, 0.85, 0.65, 0.45, 0.25, 0] and `damageTable.overpenetration` [1.00, 0.95, 0.85, 0.75] (new rows, with a comment); no other table touched.
- `Scripts/Sim/Content/DamageTable.cs`: the two rows (code defaults equal to the data), `SplashStepAt`, `SplashFalloff`, `SplashStep`, `Overpenetrates`, `Overpenetration`, `OverpenetrationStep`; `Effective(weapon, ...)` multiplies the overpenetration of a direct Kinetic weapon.
- `Scripts/Sim/Content/Catalog.cs`: parses the two rows.
- `Scripts/Sim/Combat/DamageSystem.cs`: `ApplyFalloff` (the splash row), `HitMultiplier` and `Estimate` (overpenetration).
- `Scripts/Sim/Bosses/BossSystem.BigAttacks.cs`: `BlastAt` through the new `Share` (the splash row for blasts); `Scripts/Sim/Content/BigAttackDefs.cs`: `IsBlast`.
- Comments only: `WeaponDef.P17.cs`, `Definitions.cs` (ExplosionDef), `BigAttackDefs.cs` (`EdgeShare` no longer read).
- UI text: `Game/Hud/BaseText.cs` (`hb.blast`, `hb.blast.plain` rewritten, new `hb.pen.over`), `AmmoHandbook.cs` (blast entry shows both rows, overpenetration line, `Row` helper), `UnitText.cs` / `UnitLines.cs` (`ul.splashEdge`: "falling off" instead of "at 40%"), `BigAttackText.cs` / `BossText.cs` (13 big-attack descriptions: "falling off" / "giảm dần" instead of "full damage" / "40%").
- Unity export (in Tests/EditMode, runs in the lead's re-export): `ExportGameDoc.cs` writes `splashFalloff` and `overpenetration` into game.json; `ExportGameDoc.Pack.cs` strike `rimShare` reads the splash row (same 0.25 / 0.625).
- Exporter (canonical source of the pack): `Tools/export/domains/_game.py` (`splash_row`, `over_row`, `splash_step_at`, `splash_falloff`, `overpenetrates`, `overpenetration`, `over_mult`; `effective` includes it), `_layer_b.py` (`armour_index` x the overpenetration row; old body now `armour_table`), `_b01.py` (new column `Vu_khi_suy_ra.xuyen_qua`; `he_so_xuyen_giap_*` / DPS include it), `_b02.py`, `_b03.py`, `_b04.py` (input `input_bang_xuyen_qua`, formulas and Python partners), `d01_vu_khi_dan.py` (new sheets `Bang_xuyen_qua`, `Bang_no_lan`), `core/doc_parts.py`, `core/gamefill.py` (column meaning).
- Calculators / doc generators: `Tools/balance/p32_tower_prices.py` (`armour_mult` x overpenetration), `Tools/docs/prompt25.py` (`falloff`, `splash_share`: cluster DPS), `prompt32.py` (handbook: both tables and their rules), `prompt26.py`, `prompt29.py`, `prompt34.py`, `build_doc.py` (texts), `Docs/GAME_PLAN.md` (damage model: both tables).

## 2. Call sites of the splash calculation

- `Sim/Combat/DamageSystem.cs:702` `ApplyFalloff`: the only per-target blast share for every `Splash` (line 455): a round's blast (`Burst`, line 118: weapon splash and equipment's extra splash), queued explosions (`Step`: cook-offs, death blasts, bomblets, Gungnir's final blast, boss rings / debris / pods, naval salvos), strikes (`StrikeSystem.cs:578, 668`), mines (`AbilitySystem.cs:540`), ammo dumps (`Neutrals.cs:219`), mission events (`MissionEvents.Kinds.cs:1279`).
  Two-layer blast (edge > core): `SplashFalloff(r, core, edge)`. One-radius blast: core 0, the radius is the edge (the engine's one-radius convention: the zone over which the damage fell off to 25 % at the rim); a thermobaric one keeps prompt 15 C.3 (every band under 100 % half as far down: 92.5 / 82.5 / 72.5 / 62.5 %). r is the distance to the target's hull edge, as before.
- `Sim/Bosses/BossSystem.BigAttacks.cs:855` `BlastAt` -> `Share` (line 902): two-layer big attacks the splash row; a one-layer blast shape (the 800 mm shell, core = edge 20 m) core 0 / radius as edge; shapes with no blast (rods, sweeps, swings, charges, rings) keep their linear `falloff`, as before.
- Not a damage calculation, unchanged: bomb-stick aim geometry (`CombatSystem.Bombs.cs`), warning rings (`WarnRadius`).

## 3. Call sites of the direct Kinetic calculation

- `Sim/Combat/DamageSystem.cs:98` (`Hit`: a round striking its target) -> `Apply` -> `HitMultiplier` (line 180): `over` at line 210, only for `HitKind.Direct` / `HitKind.Pierce` with a weapon whose damage type is the hit's, `DamageType.Kinetic` and `TopAttack == false`; multiplied after `ArmourMultiplier` (the direct table), never instead of it. A blast (`HitKind.Splash`), a strike, a mine, a fire, a weapon-less hit (boss rods) never read it. `_lastPen` (the Sandbox hit report's penetration share) includes it.
- `PierceLine` (line 732): a railgun slug going on through hits with `HitKind.Pierce`, so each vehicle it passes takes it too.
- `Estimate` (line 222, targeting and overkill: the AI's per-shot estimate): the same factor with the shooter's `PenetrationUp`.
- `DamageTable.Effective(weapon, ...)` (line 199): every AI / UI reader of a weapon's effect (Matchup effect table and verdicts, ConquestAi Fit, TacticalAi structure choice, boss part weights, CombatFacts tooltips, AmmoHandbook worked example). `Effective(type, ...)` (no weapon: threat profiles, strikes) does not.
- Ports: `_game.py effective` / `over_mult`, the Excel formulas through `_layer_b.armour_index` (`Vu_khi_suy_ra`, `Hoi_quy_du_lieu`, `May_bay_so_phat`, `Boss_hieu_qua`, `Tuong_duong_xe_cong_trinh`), `p32_tower_prices.Model.armour_mult`.

## 4. Old -> new behaviour

| | old | new |
|---|---|---|
| two-layer blast | core 100 % flat, edge `edgeShare` 40 % flat, r = edge still 40 % | 110 % at r = 0, core 108 / 105 / 100 %, edge 85 / 65 / 45 / 25 %, 0 at r >= edge |
| one-radius blast | linear 100 % at the centre -> 25 % at the rim, 0 beyond | 110 % at r = 0, then 85 / 65 / 45 / 25 % by quarters, 0 at r >= radius |
| one-radius thermobaric blast | linear 100 % -> 62.5 % | 110 %, then 92.5 / 82.5 / 72.5 / 62.5 % |
| big attacks with core + edge | core 100 %, edge 40 % | the splash row |
| direct Kinetic, pen - armour <= +2 / +3 / +4 / >= +5 | x 1 | x 1.00 / 0.95 / 0.85 / 0.75 after the direct table |

Kh-29 (core 7, edge 14): r = 0 1.10; 0 < r <= 1.75 1.08; <= 3.5 1.05; <= 7 1.00; <= 8.75 0.85; <= 10.5 0.65; <= 12.25 0.45; < 14 0.25; >= 14 0 (the bounds are exact in float).
Railgun 510, pen 5, Kinetic, ground: armour 5 / 4 / 3 / 2 / 1 / 0 -> 520.2 / 612 / 734.4 / 697.68 / 624.24 / 550.8 (the prompt's numbers; the exporter's port gives the same).
Edge cases: core <= 0: no core progress (no division); edge <= core: no edge zone (0 past the core); NaN distance or a blast of no size: 0; negative distance: 0; NaN pen - armour: overpenetration 1.00. No crash, no NaN.

## 5. Tests

Skipped at the owner's word ("không cần test", 04/10): none written, none run. Compile check: `dotnet build Tools/simbuild/Sim.csproj` OK (0 errors; bin / obj / Temp/simbuild deleted after). Game-layer files (AmmoHandbook, UnitLines, texts) are outside that project: reviewed by hand.
For the lead's next suite run, tests that pin the old behaviour will need their expected numbers moved: `Prompt26ABTests` (edge takes 40 %), `CombatFinalTests.RuntimeHitsAndTheAiEstimateMatchTheTables` (runtime = table without overpenetration for Kinetic rounds three or more levels over), handbook string tests (`hb.blast` arguments), and any exact-damage test of a blast or of a Kinetic shot on light armour.

## 6. Generated docs updated

`python Tools/export/export.py check --game-json Docs/export/game_snapshot.json`: 15 / 15 PASS (unmapped 0, foreign keys 304 OK, formulas 292 OK, NEED_CODE_CHECK 0, identical across two processes).
- `01_chien_dau.md / .xlsx`: new sheets `Bang_xuyen_qua` (4 rows) and `Bang_no_lan` (9 rows), shown in the md; `Vu_khi_suy_ra.xuyen_qua`; armour multipliers and DPS with overpenetration; handbook prose (both tables' rules); no "còn 40%" / "full damage" left in any pack md.
- `02_boss.xlsx`, `03_can_cu.xlsx`, `04_che_do_kinh_te_ai.xlsx`: `input_bang_xuyen_qua`, `xuyen_qua` inputs, the formulas and their values; `00_index.xlsx`, `README.md`, `bulk.zip`.
- `Docs/Machine_Brigade_Design_Review.html`: the ammunition handbook section regenerated by `prompt32.ammo_handbook` and spliced in (both tables); the parts built from game.json (section 10g, Gungnir, 10i, big attacks, unit lines) updated with the same substitutions the strings and generators now make (old 40 % / full-damage phrases only), because a regeneration from the 04/10 snapshot would also have changed unrelated numbers.
- `Docs/GAME_PLAN.md` damage model.

Needs the lead (Unity): re-export `ExportGameDoc` (game.json with `splashFalloff` / `overpenetration`, the new strings, re-measured DPS / time-to-kill / price cells), then `export.py` and `build_doc.py` for the HTML / PDF; the game-measured cells of `02_boss` (Boss.thoi_gian_ha_muc_tieu_s, `dpsVs`) still hold the old falloff and no overpenetration.

## 7. Confirmations

- center bonus does not buff direct-hit damage: the 1.10 is in the splash row only (`ApplyFalloff`, `Share`); the direct hit (`DamageSystem.cs:98`) never reads it, and the struck target stays out of its own round's blast (`Splash(..., exclude: hit)`), so TotalDamage = DirectHit + Splash x falloff for every other target.
- overpenetration applies only to direct Kinetic: `HitKind.Direct` / `Pierce`, `DamageType.Kinetic`, a weapon present.
- Top Attack does not use overpenetration: `Overpenetrates` is false for every `topAttack` weapon (no TopAttackMultiplier x Overpenetration).
- no other balance table from earlier prompts changed: `penetration`, `topAttack`, the six damage types, `thermobaric`, Armour/Pen 5 values, bombs / missiles / ATGMs, boss armour and HP are as before; the damage-type multiplier still applies to splash as before.
