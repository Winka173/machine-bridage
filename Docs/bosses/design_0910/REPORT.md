# Boss design workbook 09/10: deliverable summary (owner prompt section 13)

Branch `feature/boss-design-0910` in `C:\Users\Winka\Projects\MachineBrigade-art2` (not pushed, not merged). Phases A-G, one commit each ("Boss design 0910 <phase>: ...").
Source: `Machine_Brigade_Boss_Thiet_Ke_Tong_Hop.xlsx`; mapping and decisions: `MAPPING.md` (same folder); decisions log: `Docs/DECISIONS.md` "Boss design workbook (09/10)".

## 1. Files changed

Code (Sim, C#): `Content/BossTemplates.cs`, `Content/BossTemplates.Design.cs` (new: the `bossDesign` overlay), `Content/Catalog.cs`, `Content/Catalog.Extra.cs`,
`Content/Catalog.BossDesign.cs` (new: new-gun DPS budget, fire-group rules), `Content/Catalog.BossReach.cs` (damage / tempo / radius per boss weapon), `Content/Definitions.cs`,
`Content/VehicleDef.Extra.cs`, `Content/SkillDef.cs`, `Content/BossDesignRules.cs` (new: the structural rules), `Entities/Vehicle.cs`, `Entities/Vehicle.Boss.cs`,
`Abilities/AbilitySystem.cs` (summons, phase events, phase safety net), `Bosses/Brain/BossWeaponDirector.cs` (fire groups, heavy-AoE gap), `Bosses/BossSystem.BigAttacks.cs`,
`Bosses/BossSystem.Parts.cs` (summon modules are not mended), `Bosses/BossSystem.Tiers.cs`, `Combat/CombatSystem.cs`, `Modes/SiegeModes.cs` (Boss Rush kinds).
Game side: `Game/Views/VehicleView.cs` (new hardpoints fire from their part), `Game/Hud/BossText.cs`, `CampaignText.cs`, `Strings.cs` (names, guides, radar texts), `Editor/CatalogCheck.cs`.
Data: `Resources/Data/balance.json` (`bossDesign`, `bossFireGroups`, 18 `bd_*` weapons, `bd_*` / `deploy_*` library parts, 10 skills, six minis, phases, big-attack radii, bomb rows),
`campaign.json` (six mini ids appended to chapter lists), `Resources/UI/Cards/manifest.json` + six card PNGs (copies of the parent's). Docs: MAPPING.md, this file, `smoke_result.tsv`,
DECISIONS, CHANGELOG. Tools: `Tools/simbuild/regress/BossDesign.cs` and modes `bossdump`, `bossrules`, `bosssmoke` in `Program.cs`.
Tests: new `Tests/EditMode/BossDesign0910Tests.cs`; updated `Prompt20BossTests`, `Prompt26ABTests`, `Prompt8ContentTests` (not run).

## 2. Per-boss table (before -> after)

Columns: data hp (the Excel value, after the nerf) | in-match HP (data hp x toughness 0.85 x mini rank share 0.55; difficulty on top) | gun mounts | old guns' nerf (sheet 03)
| new-gun DPS budget (weapon level, sheet 03 col L; for the six new minis the whole-gun DPS) | summons (sheet 08). Phase: every boss has one phase at 50 % (before: 60/25 % main, 45 % mini, tier marks 60/25).

| boss | rank | data hp | in-match hp | mounts | old-gun nerf | new-gun DPS | summons |
|---|---|---|---|---|---|---|---|
| `argus` | mini | 99593 -> 74695 | 46560 -> 34920 | 2 -> 8 | x0.874 dmg, x0.700 tempo | 87.94 | argus_launch: recon_drone x1 / 85s, cap 2, first 18s |
| `armored_train` | mini | 39638 -> 29729 | 18531 -> 13898 | 6 -> 6 | x1.000 dmg, x0.950 tempo | - | - |
| `bastion_mk0` | mini | 20213 -> 15160 | 9450 -> 7087 | 3 -> 8 | x0.860 dmg, x0.820 tempo | 35.93 | bastion_mk0_deploy: armored_car x1 / 110s, cap 2, first 20s |
| `behemoth` | main | 38650 -> 23190 | 32853 -> 19712 | 10 -> 13 | x0.872 dmg, x0.760 tempo | 128.62 | behemoth_deploy: main_battle_tank x1 / 110s, cap 2, first 25s |
| `behemoth_inferno` | mini | 25830 -> 19373 | 12076 -> 9057 | 3 -> 6 | x0.891 dmg, x0.820 tempo | 55.99 | - |
| `behemoth_mk0` | mini | 35595 -> 26696 | 16641 -> 12480 | 4 -> 7 | x0.891 dmg, x0.820 tempo | 56.08 | - |
| `behemoth_mk2` | mini | 56175 -> 42131 | 26262 -> 19696 | 3 -> 8 | x0.860 dmg, x0.820 tempo | 123.54 | - |
| `behemoth_tempest` | mini | 39638 -> 29729 | 18531 -> 13898 | 3 -> 6 | x0.891 dmg, x0.820 tempo | 51.78 | - |
| `coeus` | mini | 99593 -> 74695 | 46560 -> 34920 | 5 -> 10 | x0.860 dmg, x0.820 tempo | 51.49 | coeus_launch: recon_drone x1 / 105s, cap 1, first 20s |
| `command_airship` | main | 222345 -> 155642 | 188993 -> 132296 | 8 -> 14 | x0.843 dmg, x0.700 tempo | 158.88 | airship_launch_l: strike_drone x1 / 65s, cap 2, first 14s; airship_launch_r: strike_drone x1 / 65s, cap 2, first 14s |
| `daedalus` | main | 259826 -> 181878 | 220852 -> 154596 | 6 -> 13 | x0.872 dmg, x0.760 tempo | 108.22 | pods: every 100s, 1 per drop, cap 2, first 25s |
| `drone_mothership` | main | 84049 -> 58834 | 71442 -> 50009 | 9 -> 15 | x0.842 dmg, x0.760 tempo | 166.77 | mothership_launch: strike_drone x2 / 45s, cap 6, first 10s |
| `earth_borer` | mini | 75600 -> 56700 | 35343 -> 26507 | 3 -> 3 | x1.000 dmg, x0.950 tempo | - | - |
| `fenrir` | mini | 31448 -> 23586 | 14702 -> 11026 | 3 -> 7 | x0.891 dmg, x0.820 tempo | 80.01 | fenrir_deploy: armored_car x1 / 115s, cap 1, first 25s |
| `fortress_bastion` | main | 27972 -> 16783 | 23776 -> 14266 | 11 -> 15 | x0.842 dmg, x0.760 tempo | 104.08 | bastion_deploy: main_battle_tank x1 / 85s, cap 3, first 20s |
| `hydra` | mini | 85365 -> 64024 | 39908 -> 29931 | 3 -> 6 | x0.891 dmg, x0.820 tempo | 79.65 | - |
| `hyperion` | main | 304906 -> 213434 | 259170 -> 181419 | 9 -> 15 | x0.842 dmg, x0.760 tempo | 202.9 | pods: every 90s, 1 per drop, cap 2, first 18s |
| `icarus_mk0` | mini | 99593 -> 74695 | 46560 -> 34920 | 3 -> 10 | x0.860 dmg, x0.820 tempo | 144.91 | pods: every 100s, 1 per drop, cap 1, first 20s |
| `ixion` | main | 106272 -> 69077 | 90331 -> 58715 | 7 -> 7 | x1.000 dmg, x0.950 tempo | - | ixion_deploy: armored_car x1 / 125s, cap 2, first 30s |
| `kraken` | main | 182123 -> 127486 | 154805 -> 108363 | 16 -> 13 | x0.842 dmg, x0.760 tempo | 489.78 | kraken_jets: stealth_naval_strike x2 / 55s, cap 4, first 12s |
| `landing_hovercraft` | mini | 56175 -> 42131 | 26262 -> 19696 | 5 -> 9 | x0.860 dmg, x0.820 tempo | 221.17 | - |
| `leviathan` | main | 65772 -> 39463 | 55906 -> 33544 | 16 -> 22 | x0.842 dmg, x0.760 tempo | 239.11 | - |
| `locust` | mini | 47933 -> 35950 | 22409 -> 16807 | 2 -> 8 | x0.860 dmg, x0.820 tempo | 56.6 | locust_launch: strike_drone x1 / 75s, cap 2, first 15s |
| `mega_gunship` | mini | 31448 -> 23586 | 14702 -> 11026 | 7 -> 7 | x1.000 dmg, x0.950 tempo | - | - |
| `mobile_fortress` | main | 48946 -> 29368 | 41604 -> 24963 | 9 -> 13 | x0.895 dmg, x0.760 tempo | 153.94 | jotunn_deploy: light_tank x1 / 95s, cap 2, first 25s |
| `moloch` | main | 101369 -> 60821 | 86164 -> 51698 | 7 -> 7 | x1.000 dmg, x0.950 tempo | - | workshop: every 110s, cap 2, first 25s |
| `monster` | main | 170734 -> 102440 | 145124 -> 87074 | 11 -> 11 | x1.000 dmg, x0.900 tempo | - | - |
| `nuke_train` | main | 127656 -> 82976 | 108508 -> 70530 | 7 -> 7 | x1.000 dmg, x0.900 tempo | - | - |
| `nyx` | mini | 39638 -> 29729 | 18531 -> 13898 | 6 -> 10 | x0.860 dmg, x0.820 tempo | 133.53 | - |
| `scylla` | mini | 39638 -> 29729 | 18531 -> 13898 | 8 -> 12 | x0.895 dmg, x0.760 tempo | 176.47 | - |
| `silver_bug` | main | 304906 -> 213434 | 259170 -> 181419 | 11 -> 17 | x0.777 dmg, x0.760 tempo | 225.0 | pods: every 80s, 1 per drop, cap 2, first 18s |
| `theia` | mini | 99593 -> 74695 | 46560 -> 34920 | 8 -> 9 | x0.860 dmg, x0.820 tempo | 152.11 | pods: every 75s, 2 per drop, cap 3, first 18s |
| `typhon` | main | 182123 -> 127486 | 154805 -> 108363 | 5 -> 5 | x1.000 dmg, x0.900 tempo | - | - |
| `roc_gunship` (new) | mini | - -> 77821 | - -> 36381 | - -> 8 | x0.70 dmg, x0.75 tempo | 563.91 (all guns) | - |
| `daedalus_assault` (new) | mini | - -> 63657 | - -> 29760 | - -> 7 | x0.70 dmg, x0.75 tempo | 480.96 (all guns) | - |
| `icarus_interceptor` (new) | mini | - -> 74702 | - -> 34923 | - -> 7 | x0.70 dmg, x0.75 tempo | 902.78 (all guns) | - |
| `matriarch_flak` (new) | mini | - -> 35300 | - -> 16503 | - -> 6 | x0.70 dmg, x0.75 tempo | 665.18 (all guns) | wasp_launch: strike_drone x1 / 60s, cap 2, first 12s |
| `jotunn_artillery` (new) | mini | - -> 22026 | - -> 10297 | - -> 7 | x0.70 dmg, x0.75 tempo | 718.38 (all guns) | - |
| `bastion_aa` (new) | mini | - -> 13426 | - -> 6277 | - -> 7 | x0.70 dmg, x0.75 tempo | 415.12 (all guns) | - |

## 3. Six new minis (sheet 05): status

All six are variants of their parent chassis (the parent's model, card and escorts), registered in data, the cards manifest, texts, Boss Rush kinds and the chapters' mini lists
(Bastion Flak ch.1, Jotunn Mortar ch.3, Matriarch Wasp ch.5, Roc Arsenal ch.10, Daedalus Assault ch.11, Icarus Sentinel ch.12). No campaign mission uses them as its boss, so Boss Hunt is unchanged.
`roc_gunship` 8 hardpoints, no bombs, no hangars; `daedalus_assault` 7 (pods cap 1, first 30 s, every 120 s); `icarus_interceptor` 7 (pods cap 1); `matriarch_flak` 6 (2 drone bays + own
summon: 2 drones, 60 s); `jotunn_artillery` 7; `bastion_aa` 7 (4 flak, 2 SAM, one 105 mm). Each has its own HP (parent target x 0.50 / 0.35 / 0.35 / 0.60 / 0.75 / 0.80: sheet 10 has no row),
gun nerf (damage 0.70, tempo 0.75), whole-gun DPS from sheet 05 split over all mounts. Looks: the parent's model, tint and size only; new guns have no models of their own.

## 4. Done, and not done

Done: HP targets; old-gun nerf and new-gun DPS budgets for all 33 rows; Roc / Argus bomb nerf and the eight AoE / super-weapon rows; shared heavy-AoE gap; fire groups (stagger, caps per
group and per target); Leviathan 22 / Kraken 13 hardpoints with the deck as a part; 111 new hardpoints on 24 existing bosses (and the six minis' own 42); periodic summons with cooldown / count / cap / first delay / warning ring /
safe arrival / no queue; hangars, decks, gates, doors and bays as parts that stop new units only; radar parts removed; one phase at 50 % per boss, once, with phase events; six minis;
rules checker, headless smoke, tests written.

Not done or only partly:
- **Models.** New hardpoints and the six minis have no models or muzzle nodes; shots leave from the carrying part's place. The prompt allows it; the redraw agent must add real nodes (Mount_/Muzzle_).
- **Animations / effects of summons.** No new launch or door animation: aircraft appear at the deck part, ground units arrive after a 3 s ring on the ground at the gate. No new phase-change effects beyond the existing transform (radio, blast, 2-3 s immune).
- **Warnings.** Bomb sticks and big attacks already warn (existing rings); no new warning for ordinary heavy shells or lasers (the single-beam laser rule of sheet 12 is not implemented).
- **Icarus / Hyperion sub-craft.** Sheet 08 names no unit id; the spacecraft's periodic summons are the existing pods (ground vehicles), not drones (MAPPING D7, D14). Needs the owner's id / art.
- **Phase behaviours of sheet 13** are approximations with existing systems: summons called, rhythm slower, shield skill. "Drones guard hangar / engine" (Matriarch) and "broadside salvo" (Leviathan) are not new AI behaviours.
- **Stealth** sub-guns of Nyx (only when revealed) and **FPS** with 20+ barrels: not implemented / not measured.
- **Part HP**: left as shares of the body (sheet 10 col J not applied separately); `breakDamage` of the new parts is 0.
- **Naval lane**: touched only where the Excel and the owner's rules require it (Leviathan / Kraken mounts, salvo off on Kraken, radar parts, Typhon sonar, Leviathan escapePhase 2 -> 1).
- Manual edits of generated big-attack lines (radii, units) in balance.json will be overwritten if `Tools/balance/import_xlsx.py` is re-run; this workbook should become its source.

## 5. Tests: run and not run

Run (on this checkout, no Unity): `dotnet build Tools/simbuild/Sim.csproj` 0 errors; `dotnet build Tools/simbuild/regress/Regress.csproj` 0 errors; catalog load
(`load`, `bossdump`) OK with 39 bosses and the 193 campaign missions; `bossrules` (BossDesignRules over the catalog) no breach; `bosssmoke`: 39 bosses spawned and stepped (90 s; summoners 360 s),
a big blow across 50 %, a heal and a second dip, summon caps and first-wave delay, carrying parts broken then no new units: 0 failures on the final run (`smoke_result.tsv`).
The smoke was run three times while developing: the first run found 9 failures: 7 were my own test placing the 50 % blow before the first-call delay (the phase calls the summons at once by design),
2 were real (Bastion / Bastion Mk.0's self-repair mended the broken gate: fixed, a summon module is never patched). Nothing else failed.
Not run: all Unity EditMode / PlayMode tests (CatalogCheck in Unity, `BossDesign0910Tests`, the updated Prompt20 / 26AB / 8Content tests), no FPS or damage measurement, no check of the
bomb stick against a tank column (the radius / damage numbers are the sheet's mid values; sheet 04 itself marks them as trial values), no visual check; the Game-side C# (VehicleView, texts) is
not compiled here (Unity only).
Tests likely to fail until updated by the lead's run (they assert old data): any test reading boss HP numbers, the escorts' phase counts, the 0.6 / 0.25 marks, `leviathan_helos`, the 16-mount
Leviathan / Kraken, the Boss Rush roster for fixed seeds (the two mini kinds grew), 33-boss counts in other files, `mothership_launch` without a cap.

## 6. Open points for the owner

1. Icarus / Hyperion / Coeus drones: give a unit id (or art) for the sub-craft; today pods and a recon drone stand in.
2. The six minis' HP ratios (sheet 10 has none) and whether they may be listed in the campaign chapters (they are, at the end of the lists, with no mission using them).
3. Bomb numbers (42 % / 80 % radius / 70 % tempo) need a tank-column test when the owner allows measurements.
4. Leviathan's `escapePhase` moved to the single phase (50 %): confirm, or switch it off.
