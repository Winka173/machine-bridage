# Full fix report (Docs/prompts/fix_full_vi.txt, passes L0-L10)

Done locally 2026-10-02/03 in three lanes plus the lead (plan: Docs/FIX_FULL_PLAN.md). No tests, sims or measures were
run (owner rule); Unity compiles had 0 errors after every merge, CatalogCheck OK (253 vehicles, 372 weapons). Play-test 12
(03/10) found regressions from this pass; they were fixed the same day (section 10 below).

## 1. Prompt status (L0)
Docs/checks/fix_precheck.md lists every prompt 26-34 and earlier fix message as run / partly run / not run, with the code
checks C01-C16. Prompt 24 skipped; 26 in the reduced scope; 27 v2, 28-34 done locally.

## 2. Weapon flags before -> after (Docs/checks/full_weapon_audit.md, `Tools/balance/full_weapon_audit.py`)

| group | TOO FAST | TOO SLOW | UNIT | WAVE 1 | FAMILY | DISPLAY |
|---|---|---|---|---|---|---|
| boss | 25 -> 3 | 9 -> 0 | 1 -> 0 | 47 -> 0 | 7 -> 0 | 65 -> 0 |
| player | 29 -> 28 | 6 -> 6 | 0 -> 0 | 6 -> 6 | 1 -> 0 | 60 -> 0 |
| tower | 19 -> 17 | 1 -> 1 | 0 -> 0 | 1 -> 1 | 0 -> 0 | 26 -> 0 |
| all | 105 -> 80 | 17 -> 8 | 2 -> 1 | 80 -> 33 | 7 -> 0 | 139 -> 0 |

The player and tower flags left are kept on purpose until play-tests (owner call, 02/10): the 52 weapons in
Docs/balance/player_weapon_waitlist.md.

## 3. Bosses before -> after
Boss weapons were regrouped by family and calibre (per-shot damage up, cycles longer). The sustained DPS left after the
make-up was clamped to 80-120 % of the pre-fix value by a per-boss outgoingDamageMult (owner call, DECISIONS "Owner calls
after the full fix L3"): nuke_train x1.309, moloch x1.696, garuda x1.789, command_airship x1.789, ixion x1.757,
bastion_mk0 x1.471, earth_borer x1.085, kronos x0.744, scylla x0.739, supreme_command x0.759, armored_train x0.832,
nyx x0.836, mobile_fortress x0.951, leviathan and kraken x0.968. Per-boss tables: Docs/balance/boss_weapon_families.md
and the PDF section 21 B.

## 4. Player vehicles waiting for a decision
Docs/balance/player_weapon_waitlist.md (52 weapons, kept until play-tests).

## 5. Munition behaviour before -> after
Docs/checks/munition_behavior.md (rules A-G per munition group), Docs/checks/target_mask.md, Docs/checks/flare_baseline.md.
The delayed damage was the view flying rounds on Time.time while damage lands on the Sim tick (fix: a shot clock; see 10).
Flares now leave from Mount_Flare_L/_R/_TL/_TR.

## 6. Audio: the "keng" and the weak blasts
Docs/audio/diagnosis.md and metrics.md. Keng: every kinetic round played a bell-like hit clip. Weak blasts: prompt 34's
synthesised clips replaced the recorded ones and off-screen gain was 0.6. L7 rebuilt the library by size (120 clips).
Play-test 12 follow-up: Docs/audio/pt12.md.

## 7. Models (L8, Docs/models/scan/visual_scores.md)
230 models scored: final Tốt 22 / Cần sửa 121 / Kém 87 (visual alone: Tốt 125 / Cần sửa 75 / Kém 26 of 226 sheets).
Many final Kém come from part names only (Docs/models/scan/fix_backlog.md, a renaming job). None was worse than the old
model, so none was restored. 15 rebuilt (triangles before -> after): heavy_flak_tower 1,116 -> 8,902; flare_tower
680 -> 5,102; laser_ad_station 390 -> 3,434; visual_jammer 592 -> 3,672; fire_control_centre 612 -> 2,874; radar_site
900 -> 4,252; troop_shelter 916 -> 3,158; repair_bay 1,152 -> 5,214; interceptor_drone_vehicle 1,494 -> 4,068;
microwave_vehicle 1,664 -> 4,914; nlos_atgm_vehicle 2,048 -> 4,918; radar_scout 1,192 -> 3,362; recoilless_jeep
1,606 -> 3,386; sp_mortar 2,806 -> 5,748; wheeled_howitzer 2,136 -> 5,026. L9 item 7: 0 failures; over-budget is info
only (owner rule). Prompt 35 takes over the full model rebuild.

## 8. Own decisions
Every pass logged its calls in Docs/DECISIONS.md under "Sửa lỗi tổng hợp L0..L10", "Owner calls after the full fix L3",
"Owner: over-budget models are fine", "Play-test 12 (lane B)" and "Play-test 12 audio (lane C)". The main ones:
Mount_Flare names suffixed (a bare Mount_Flare reads as a weapon pivot); railguns keep MJ in caliberMm; the 52 player
weapons kept; guard_tower_b's thinner scan sheet is a ModelScan loading gap, not the model.

## 9. PDF items fixed
Docs/Machine_Brigade_Design_Review.pdf, 475 pages (03/10): section 10 ballistics columns (calibre and warhead apart,
family, barrels, full cycle, real rate, sustained DPS, changed marks), 10g warning and family columns, new 10j (L10 items
2-7), vehicle cards (calibre or warhead, cadence, barrels, core / edge, DPS); text items 13 (Legend mission c12m10), 14
(portraits), 17 (airfield: aircraft return when out of ammo); items 12, 15, 16, 18 already matched the code. New section 21:
A full weapon table before / after, B per-boss summary, C effects per tier and per weapon >= 120 mm with Unity shots at
fixed time marks (metre grid, MBT for scale, core / edge rings, salvo shots; 66 subjects, 554 shots), D audio per clip,
E model scores with before / after sheets. 17 picture slots stay "shot pending": 13 structures that have no old model to
compare and the 4 models ModelScan does not draw (cp_relay_a/b, minefield_a/b).

## 10. Play-test 12 regressions (03/10) and their fixes
- Rounds stuck at the muzzle: the L4 shot clock was one shared static, frozen while the battle sat behind the menu or was
  paused, and the in-action preview read it. Now each effects director owns its clock.
- Boss firing no longer shakes the camera; the boss preview fires every mount at its own target (naval bosses at a line
  abreast); smoke lifetime about halved; flares 20-40 m; big-calibre blast sizes follow calibre (gun turret, heavy
  turret); 2-3 wreck breakups per class.
- Audio: L7 had dropped the per-bank levels (machine guns +9.6 dB, autocannons +6.9 dB); yesterday's generator and levels
  are back for those, with burst clips for fast guns, and missiles got their own launch sounds.
