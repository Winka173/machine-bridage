# Boss design workbook 09/10: Excel ids vs code ids (phase A)

Source: `Machine_Brigade_Boss_Thiet_Ke_Tong_Hop.xlsx` (text dump `sheets.md`), code at `feature/boss-design-0910` (lead 2ba1b195c).
Static facts below come from `balance.json` and from a catalog dump (`regress bossdump`, no simulation).

## 1. Ids

- All 33 roster ids of sheets 01/03/10 exist in the code with the same id (18 base bosses plus 15 variants of `variantOf`). Nothing in the Excel is unknown to the code, nothing in the code is missing from the Excel.
- The six new minis of sheet 05 do not exist (status "CHUA CO TRONG GAME"). Exact ids from the sheet: `roc_gunship`, `daedalus_assault`, `icarus_interceptor`, `matriarch_flak`, `jotunn_artillery`, `bastion_aa`. The owner prompt's display names map: Roc Arsenal = `roc_gunship`; Daedalus Assault = `daedalus_assault`; Icarus Sentinel = `icarus_interceptor`; Matriarch Wasp = `matriarch_flak`; Jotunn Mortar = `jotunn_artillery`; Bastion Flak = `bastion_aa`.
- HP "thiet ke goc" (sheet 10, col E) equals the `hp` field in `balance.json` for all 33 bosses (checked by script). "HP trong tran goc" (col F) = `hp * toughness.bosses (0.85)`. Mini bosses also carry `bossRanks.mini.hp = 0.55` (a share), which the Excel in-match column ignores (see D2).
- Sheet 07 weapon ids (219 rows) exist in the code (`p26_*`, `pt14_*`, plain ids). Weapons shared by a parent and its variants: `p26_roc_main_roc_bombs` (Roc, Argus), `p26_bastion_*` (Bastion, Monster, Bastion Mk.0), `p26_leviathan_*` (Leviathan, Kraken, Nyx, Scylla), `p26_icarus_*`/`pt14_*` (Icarus family), `p26_jotunn_*` (Jotunn, Fenrir), `p26_behemoth_*`, `p26_matriarch_*`. A per-boss value therefore cannot live on the weapon: it goes on the boss (`gunNerf`) or in `bossWeaponOverrides` (per boss and weapon).

## 2. Roster table (before -> target)

| id | rank | parent | mounts now (code / Excel old) -> target | HP (data) now -> target | code phase marks now | Excel 08 summon |
|---|---|---|---|---|---|---|
| `argus` | mini | command_airship | 2 / 2 -> 8 | 99593 -> 74695 (-25%) | 0.45 | drone trinh sát, 85s cd, 1/wave, cap 2, first 18s |
| `armored_train` | mini | unique | 6 / 6 -> 6 | 39638 -> 29728 (-25%) | 0.45 | none (set-piece) |
| `bastion_mk0` | mini | fortress_bastion | 3 / 3 -> 8 | 20213 -> 15160 (-25%) | 0.45 | xe bọc thép nhẹ, 110s cd, 1/wave, cap 2, first 20s |
| `behemoth` | main | behemoth | 10 / 10 -> 13 | 38650 -> 23190 (-40%) | 0.6,0.25 | xe tăng hạng trung / xe phòng không, 110s cd, 1/wave, cap 2, first 25s |
| `behemoth_inferno` | mini | behemoth | 3 / 3 -> 6 | 25830 -> 19372 (-25%) | 0.45 | not in 08 (no periodic summon) |
| `behemoth_mk0` | mini | behemoth | 4 / 4 -> 7 | 35595 -> 26696 (-25%) | 0.45 | not in 08 (no periodic summon) |
| `behemoth_mk2` | mini | behemoth | 3 / 3 -> 8 | 56175 -> 42131 (-25%) | 0.45 | not in 08 (no periodic summon) |
| `behemoth_tempest` | mini | behemoth | 3 / 3 -> 6 | 39638 -> 29728 (-25%) | 0.45 | not in 08 (no periodic summon) |
| `coeus` | mini | hyperion | 5 / 5 -> 10 | 99593 -> 74695 (-25%) | - | drone trinh sát, 105s cd, 1/wave, cap 1, first 20s |
| `command_airship` | main | command_airship | 8 / 8 -> 14 | 222345 -> 155642 (-30%) | 0.6,0.25 | drone trinh sát/FPV, 65s cd, 2/wave, cap 4, first 14s |
| `daedalus` | main | daedalus | 6 / 6 -> 13 | 259826 -> 181878 (-30%) | - | xe tăng nhẹ / IFV qua drop pod, 100s cd, 1/wave, cap 2, first 25s |
| `drone_mothership` | main | drone_mothership | 9 / 9 -> 15 | 84049 -> 58834 (-30%) | 0.6,0.25 | drone FPV / UAV vũ trang, 45s cd, 2/wave, cap 6, first 10s |
| `earth_borer` | mini | unique | 3 / 3 -> 3 | 75600 -> 56700 (-25%) | 0.45 | none (set-piece) |
| `fenrir` | mini | mobile_fortress | 3 / 3 -> 7 | 31448 -> 23586 (-25%) | 0.45 | xe trinh sát, 115s cd, 1/wave, cap 1, first 25s |
| `fortress_bastion` | main | fortress_bastion | 11 / 11 -> 15 | 27972 -> 16783 (-40%) | 0.6,0.25 | xe tăng hạng trung / IFV từ cổng, 85s cd, 1/wave, cap 3, first 20s |
| `hydra` | mini | typhon | 3 / 3 -> 6 | 85365 -> 64024 (-25%) | 0.45 | not in 08 (no periodic summon) |
| `hyperion` | main | silver_bug | 9 / 9 -> 15 | 304906 -> 213434 (-30%) | - | phi thuyền đánh chặn nhỏ / UAV, 90s cd, 1/wave, cap 2, first 18s |
| `icarus_mk0` | mini | silver_bug | 3 / 3 -> 10 | 99593 -> 74695 (-25%) | - | drone phòng thủ, 100s cd, 1/wave, cap 1, first 20s |
| `ixion` | main | unique | 7 / 7 -> 7 | 106272 -> 69077 (-35%) | 0.6,0.25 | xe khai thác vũ trang / xe bọc thép, 125s cd, 1/wave, cap 2, first 30s |
| `kraken` | main | leviathan | 16 / 16 -> 13 | 182123 -> 127486 (-30%) | 0.6,0.25 | attack_jet, 55s cd, 2/wave, cap 4, first 12s |
| `landing_hovercraft` | mini | unique | 5 / 5 -> 9 | 56175 -> 42131 (-25%) | 0.45 | not in 08 (no periodic summon) |
| `leviathan` | main | leviathan | 16 / 16 -> 22 | 65772 -> 39463 (-40%) | 0.6,0.25 | none (set-piece) |
| `locust` | mini | drone_mothership | 2 / 2 -> 8 | 47933 -> 35950 (-25%) | 0.45 | drone FPV, 75s cd, 1/wave, cap 2, first 15s |
| `mega_gunship` | mini | mega_gunship | 7 / 7 -> 7 | 31448 -> 23586 (-25%) | 0.45 | not in 08 (no periodic summon) |
| `mobile_fortress` | main | mobile_fortress | 9 / 9 -> 13 | 48946 -> 29368 (-40%) | 0.6,0.25 | xe tăng nhẹ / IFV hộ tống, 95s cd, 1/wave, cap 2, first 25s |
| `moloch` | main | unique | 7 / 7 -> 7 | 101369 -> 60821 (-40%) | 0.6,0.25 | xe tăng nhẹ / drone sửa chữa, 110s cd, 1/wave, cap 2, first 25s |
| `monster` | main | fortress_bastion | 11 / 11 -> 11 | 170734 -> 102440 (-40%) | 0.6,0.25 | none (set-piece) |
| `nuke_train` | main | unique | 7 / 7 -> 7 | 127656 -> 82976 (-35%) | 0.6,0.25 | none (set-piece) |
| `nyx` | mini | leviathan | 6 / 6 -> 10 | 39638 -> 29728 (-25%) | 0.45 | not in 08 (no periodic summon) |
| `scylla` | mini | leviathan | 8 / 8 -> 12 | 39638 -> 29728 (-25%) | 0.45 | not in 08 (no periodic summon) |
| `silver_bug` | main | silver_bug | 11 / 11 -> 17 | 304906 -> 213434 (-30%) | - | drone đánh chặn / phi thuyền con nhẹ, 80s cd, 1/wave, cap 2, first 18s |
| `theia` | mini | hyperion | 8 / 8 -> 9 | 99593 -> 74695 (-25%) | - | drone phòng không, 75s cd, 2/wave, cap 3, first 18s |
| `typhon` | main | typhon | 5 / 5 -> 5 | 182123 -> 127486 (-30%) | 0.6,0.25 | not in 08 (no periodic summon) |


(Mount counts: code = built mounts in the catalog; Excel "old" = sheet 01 col E; they agree for all 33 bosses. The mini phase mark 0.45 and the main marks 0.6/0.25 are the old thresholds to be replaced by one 0.5.)

## 3. What exists and is reused

| Excel need | Existing system | Use |
|---|---|---|
| HP, rank, toughness | `balance.json` `hp`, `toughness.bosses` 0.85, `bossRanks.mini.hp` 0.55, `bigAttackRules.difficulty.bossHp` | set `hp` to the sheet 10 target only; nothing else touched (no double nerf) |
| Parts, mounts, variants | `BossDefs`, `bossParts` library, `BossTemplates` (frame, library `use`, variant `keep`/`tune`) | new parts via library `use` (a new gun mount carried by a part) and a new variant key `add` |
| Per boss weapon values | `bossWeaponOverrides` (reach only) | extended with `damageMult`, `rateMult`, `radiusMult` (bombs, super weapons) |
| Summons | `SkillKind.Summon` skills (`airship_launch_*`, `kraken_jets`, `leviathan_helos`, `mothership_launch`), `max` cap, part `skills` link (part broken -> skill off), escorts `arrive`/`phase`, pods (Tiers) | extended: first-wave `delay`, `warn`, skip-at-cap (no queue), spawn at the module, no spawn on top of an enemy |
| Parts | `BossSystem.Parts` (`stops`, `mounts`, `skills`, `speed`) | door/gate/bay parts with `skills`; `radar` kind removed |
| Fire cadence | `BossWeaponDirector.CadenceAllows` (0.35 s heavy gap) | extended with fire groups (main, secondary, ciws, suppress), per-group stagger, max groups per target, shared heavy-AoE gap |
| Phases | `bossRanks` default phases (0.6/0.25 main, 0.45 mini), per-boss `phases`, tiers `marks`, skills with `HpBelow` | one phase at 0.5 for every boss |
| Big attacks / AoE | `bigAttacks`, `bigAttackScale`, bomb sticks (`stick`) | damage/cooldown/radius per Excel sheet 04 |

## 4. Conflicts and decisions (nothing guessed silently)

- **D1 Phases.** Sheet 13 lists Daedalus at "65 % / 30 %"; the owner rule and sheet 15 say one mark at 50 % for every boss. Decision: 50 % for all (Daedalus too: it lowers and opens the bay at 50 %). Old marks 60/25 (main), 45 (mini), tier marks 0.6/0.25, and the HP-threshold skills `boss_rage` (0.5), `boss_bulwark` (0.35), `fortress_barrage` (0.4), `leviathan_helos` (0.7) are removed as stacked buffs; `mothership_shield` becomes the Matriarch/Tempest 50 % phase skill. Mission HP events (`campaign.json` / `MissionEvents`) are separate code and stay.
- **D2 HP and rank share.** The Excel in-match column is `hp * 0.85`. In the game a mini also has `bossRanks.mini.hp = 0.55`; the Excel does not model it. Decision: set `hp` to the Excel "HP thiet ke hien tai" and keep the rank share and toughness (sheet-15 rule: reduce once, no second nerf). Part HP is a share of the body (`bossRanks.partsShare`), so it falls with the body; sheet 10 col J (79/74/66 %) is within a few points of that and is not applied a second time.
- **D3 DPS meaning.** Sheet 03 "DPS goc" = sum of "DPS duy tri" of sheet 07 (e.g. Argus 814.23 = 2 x 407.11) = weapon-level sustained DPS, before rank/difficulty multipliers. Decision: old guns get relative multipliers `gunNerf {damage, rate}` (sheet 03 cols H, I) applied on top of the existing rank buffs; new guns get an absolute budget `newGunDps` (col L, weapon-level) split over the new mounts and normalised at catalog load. Total = old x damage x rate + new budget = col G target.
- **D4 Bombs/AoE (sheet 04).** Roc and Argus bombs are `STICK` weapons (8 x 700, splash 10 m, 33 s). Targets: damage 42 %, rate 70 %, radius 80 % of the original (mid of the 35-50 / 65-75 / 75-85 ranges), net of the `gunNerf` (not applied twice). Behemoth, Daedalus, Matriarch, Bastion, Hyperion, Kraken, Leviathan, Icarus super weapons/salvos: damage 62 %, cooldown x 1/0.8, radius 90 % (mid of 55-70 / 75-85 / 85-95), through `bigAttackScale` (new `radius`) and the ships' `salvo`/`cruise` data. Falloff is the existing damage-table splash row.
- **D5 Kraken 13 mounts.** Kraken inherits Leviathan's 16 mounts; target 13 (sheet 02: 2 CIWS twin, 3 autocannon 30-40 mm, 2 x 76 mm, 2 SAM, 4 light AA). Decision: reach exactly 13 hardpoints with that composition by dropping the 406 mm super/aft turrets and surplus AA mounts; the flight deck is a part, not a gun mount.
- **D6 Leviathan 22 mounts.** +6 new hardpoints: 4 twin CIWS and 2 twin 57 mm as sheet 02 lists (boss-specific weapon ids `bd_*`).
- **D7 Missing unit ids in sheet 08.** Icarus: "drone / phi thuyen con (can ID)"; Hyperion: "phi thuyen danh chan nho / UAV (can mau)"; Coeus, Theia, Locust, Argus: drones. No new unit art/ids are invented: existing ids are reused. `strike_drone` (Roc, Matriarch, Locust, Icarus, Theia), `recon_drone` (Argus, Coeus, Icarus Mk.0), `attack_jet` (Hyperion), `stealth_naval_strike` stays Kraken's carrier jet (sheet allows "aircraft carrier wing da co"), `light_tank` / `ifv` (Daedalus, Jotunn, Moloch), `main_battle_tank` (Bastion, Behemoth), `armored_car` (Bastion Mk.0, Fenrir, Ixion). A dedicated Icarus sub-craft stays "needs art/ID" (reported).
- **D8 Pods vs 100 s.** Daedalus already drops pods every 12 s (cap 8). Sheet 08: one vehicle per 100 s, cap 2. Decision: pods tuned to first 25 s, every 100 s, one per drop, live cap 2; its mass-drop big attack no longer carries units.
- **D9 Radar / command tower parts.** Destructible `radar` parts exist on Roc, Argus, Leviathan (and Kraken). Decision: removed (the part, not the SAM mount it carried on Leviathan); Argus's spot aura and the fire control are permanent now. `sonar` on Typhon is not a radar/command tower and stays (naval lane).
- **D10 Escorts vs periodic summons.** Escort tables (`arrive` at start, `phase` at the phase) stay as separate systems; the new periodic summons are skills with their own cap, never counted as escorts. Escort `phase` waves fire once (one mark).
- **D11 Boss armour.** Unchanged (the Excel states none).
- **D12 New-mini HP.** Sheet 10 has no row for the six new minis: HP = parent target HP x a ratio taken from the existing siblings (documented in REPORT).
- **D13 Sheet text "giu ...".** It keeps the existing weapons; the listed additions become new mounts carried by new parts, reusing the parent model (rough placement allowed by the owner, to be redrawn).
- **D14 Spacecraft summons.** Icarus, Hyperion, Theia, Icarus Mk.0 and Daedalus already call units through `pods` (a pod bay is the hangar; a broken bay stops them, the pod falls with a 6 s ring and lands short of the player's group). Sheet 08 asks for "drones / sub-craft" with no unit id, so the periodic call is these pods retuned to the sheet's cooldown, count, cap and first delay (their units are ground vehicles); a real sub-craft needs an id and art. Coeus has no pod bay: it gets a recon-drone call from a new UAV pad part.
- **D15 Big-attack drops.** Daedalus's mass drop and Moloch's dump landed up to 8 / 6 units; capped at 2 each so the sheet's live caps (Daedalus 2, Moloch 2) hold.
- **D16 Self-repair.** The `train_patch` skill used to mend the part that drives a skill or mechanism first; it now never mends a summon module (hangar, deck, gate, door, pod bay), so "broken for the rest of the fight" holds (found by the smoke on Bastion).
- **D17 Typhon sonar.** The sonar part stopped the "radar" (fire control) mechanism; treated as the same destructible sensor and removed with the radar parts.

