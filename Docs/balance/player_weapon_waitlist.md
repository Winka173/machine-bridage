# Player and tower weapons waiting for the owner (full fix prompt L3, rule 9)

Written by `Tools/balance/full_weapon_audit.py`. The player rule: fix only clear unit errors and clear too-fast /
too-slow cadences, keeping the DPS (player balance waits for prompt 29's follow-up). Changed in this pass:
`turret_rockets` and `turret_rockets_cluster` (the BM-21's real 0.5 s between rockets, the cycle and the DPS kept).
Everything below is still flagged by the audit and was left as it is, with the reason.

| weapon | carriers | flags | game / reference | why left |
|---|---|---|---|---|
| `amos_120` (120 mm AMOS (twin)) | sp_mortar | TOO FAST | x0.82 | the real reference is an estimate (no published launch interval): not a clear error |
| `avenger_stingers` (Starstreak / Stinger SHORAD (Avenger pods)) | shorad_vehicle | TOO FAST | x0.77 | the real reference is an estimate (no published launch interval): not a clear error |
| `ballistic_missile` (9M723 Iskander (700 kg)) | ballistic_launcher | TOO FAST | x0.40 | DECISIONS 19R kept the ripple off the real pace on purpose (a real salvo would take 20-35 s of a 90 s fight) |
| `boss_missiles` (9M133 Kornet) | mara_behemoth | TOO FAST | x0.32 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
| `buk_launcher` (9M317 Buk) | sam_launcher | TOO FAST | x0.41 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
| `caesar_155` (155 mm L/52 (CAESAR)) | wheeled_howitzer | TOO FAST | x0.90 | the real reference is an estimate (no published launch interval): not a clear error |
| `cruise_missile_ground` (Typhon MRC (ground-launched Tomahawk)) | ground_cruise_missile_vehicle | TOO SLOW | x7.50 | the real reference is an estimate (no published launch interval): not a clear error |
| `flak_35` (Oerlikon KDA 35 mm (Gepard)) | aa_vehicle | TOO SLOW | x5.42 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
| `flak_88` (KS-19 100 mm (1947)) | heavy_flak_tower | TOO FAST | x0.50 | a tower or dug-in site: the balance pass after prompt 18 (A.2) gave the sites a faster rhythm than the vehicles on purpose |
| `gun_100_river` (A-190 100 mm (Buyan-class river gunboat)) | river_gunboat | TOO SLOW | x2.80 | a play-test or prompt-22+ unit tuned on purpose (22P siege tank, 25 F2 new units): not a clear error |
| `gun_105_ags` (105 mm low-recoil (M8 AGS, cancelled)) | airborne_light_tank | TOO FAST | x0.58 | a play-test or prompt-22+ unit tuned on purpose (22P siege tank, 25 F2 new units): not a clear error |
| `gun_105_apfsds` (2A75 125 mm APFSDS) | elite_tank_destroyer | TOO FAST | x0.32 | DECISIONS 19R kept it faster than real on purpose (a round at the top of its calibre band: the real rate would halve the unit's damage) |
| `gun_105_bunker` (L7 105 mm) | bunker_vehicle | TOO FAST | x0.53 | DECISIONS 19R kept it faster than real on purpose (a round at the top of its calibre band: the real rate would halve the unit's damage) |
| `gun_105_long` (2A75 125 mm (2S25 Sprut)) | tank_destroyer | TOO FAST | x0.27 | DECISIONS 19R kept it faster than real on purpose (a round at the top of its calibre band: the real rate would halve the unit's damage) |
| `gun_105_wheeled` (Centauro II 120 mm) | wheeled_gun | TOO FAST | x0.35 | DECISIONS 19R kept it faster than real on purpose (a round at the top of its calibre band: the real rate would halve the unit's damage) |
| `gun_120_twin` (Rh-120 L/44 120 mm (twin)) | twin_tank | TOO FAST | x0.48 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
| `gun_120mm` (Rh-120 L/44 120 mm) | main_battle_tank, mara_behemoth, turtle_tank | TOO FAST | x0.48 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
| `gun_125_armata_ke` (125 mm smoothbore (T-14 Armata)) | next_gen_tank, towed_at_gun | TOO FAST | x0.47 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
| `gun_125_elite` (2A46M-5 125 mm) | elite_mbt | TOO FAST | x0.53 | DECISIONS 19R kept it faster than real on purpose (a round at the top of its calibre band: the real rate would halve the unit's damage) |
| `gun_140_twin` (NPzK 140 mm (twin)) | titan_tank | TOO FAST | x0.53 | a play-test or prompt-22+ unit tuned on purpose (22P siege tank, 25 F2 new units): not a clear error |
| `gun_155_coastal` (M284 155 mm (coastal battery)) | coastal_battery | TOO FAST | x0.21 | a tower or dug-in site: the balance pass after prompt 18 (A.2) gave the sites a faster rhythm than the vehicles on purpose |
| `gun_155_crusader` (XM2001 Crusader 155 mm (cancelled)) | auto_loader_howitzer | TOO FAST | x0.96 | the real reference is an estimate (no published launch interval): not a clear error |
| `gun_155_twin_ap` (M284 155 mm (twin) AP) | heavy_turret | TOO FAST | x0.26 | a tower or dug-in site: the balance pass after prompt 18 (A.2) gave the sites a faster rhythm than the vehicles on purpose |
| `gun_155_twin_coastlr` (M284 155 mm (twin, long-range coastal)) | heavy_turret.coastal | TOO FAST | x0.26 | a tower or dug-in site: the balance pass after prompt 18 (A.2) gave the sites a faster rhythm than the vehicles on purpose |
| `gun_57mm` (S-60 57 mm (2A91)) | light_tank | TOO SLOW | x4.50 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
| `gunship_105` (M102 105 mm) | sky_gunship | TOO FAST | x0.32 | DECISIONS 19R kept it faster than real on purpose (a round at the top of its calibre band: the real rate would halve the unit's damage) |
| `gunship_40mm` (Bofors L/60 40 mm) | sky_gunship | TOO FAST | x0.41 | DECISIONS 19R kept it faster than real on purpose (a round at the top of its calibre band: the real rate would halve the unit's damage) |
| `howitzer` (M284 155 mm) | artillery | TOO FAST | x0.41 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
| `howitzer_cb` (M284 155 mm) | artillery_emplacement.cb | TOO FAST | x0.21 | a tower or dug-in site: the balance pass after prompt 18 (A.2) gave the sites a faster rhythm than the vehicles on purpose |
| `howitzer_fixed` (M284 155 mm) | artillery_emplacement | TOO FAST | x0.21 | a tower or dug-in site: the balance pass after prompt 18 (A.2) gave the sites a faster rhythm than the vehicles on purpose |
| `jassm` (AGM-158 JASSM (450 kg)) | stealth_bomber, swarm_carrier | TOO FAST | x0.20 | the real reference is an estimate (no published launch interval): not a clear error |
| `kornet_multi` (9M133 Kornet) | atgm_tower.multi | TOO FAST | x0.28 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
| `kornet_top` (9M133 Kornet) | atgm_tower.top | TOO FAST | x0.26 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
| `mlrs_elite` (M30 GMLRS 227 mm (cluster)) | elite_mlrs | TOO FAST | x0.03 | DECISIONS 19R kept the ripple off the real pace on purpose (a real salvo would take 20-35 s of a 90 s fight) |
| `mlrs_rockets` (M31 GMLRS 227 mm) | mlrs | TOO FAST | x0.06 | DECISIONS 19R kept the ripple off the real pace on purpose (a real salvo would take 20-35 s of a 90 s fight) |
| `mortar_240_fixed` (2B8 240 mm (emplacement)) | artillery_emplacement.mortar | TOO FAST | x0.08 | a tower or dug-in site: the balance pass after prompt 18 (A.2) gave the sites a faster rhythm than the vehicles on purpose |
| `naval_76` (OTO Melara 76/62) | sea_corvette | TOO SLOW | x2.52 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
| `one_shot_kornet` (9M133 Kornet) | one_shot_atgm_tower | TOO FAST | x0.06 | a tower or dug-in site: the balance pass after prompt 18 (A.2) gave the sites a faster rhythm than the vehicles on purpose |
| `patriot` (MIM-104 Patriot PAC-2) | missile_battery | TOO FAST | x0.53 | the real reference is an estimate (no published launch interval): not a clear error |
| `recoilless_106` (M40 106 mm recoilless rifle) | recoilless_jeep | TOO FAST | x0.39 | a play-test or prompt-22+ unit tuned on purpose (22P siege tank, 25 F2 new units): not a clear error |
| `rockets_300mm` (9M55 Smerch 300 mm) | heavy_rocket_artillery | TOO FAST | x0.08 | DECISIONS 19R kept the ripple off the real pace on purpose (a real salvo would take 20-35 s of a 90 s fight) |
| `sam_battery_lrr` (MIM-104 Patriot PAC-2) | missile_battery.lrr | TOO FAST | x0.65 | the real reference is an estimate (no published launch interval): not a clear error |
| `sam_pac3` (Patriot PAC-3 MSE) | missile_battery.pac3 | TOO FAST | x1.12 | the real reference is an estimate (no published launch interval): not a clear error |
| `siege_gun_105` (L7 105 mm (siege tank)) | siege_tank | TOO FAST | x0.54 | a play-test or prompt-22+ unit tuned on purpose (22P siege tank, 25 F2 new units): not a clear error |
| `siege_mortar_240` (2B8 240 mm (siege tank)) | siege_tank | TOO FAST | x0.12 | a play-test or prompt-22+ unit tuned on purpose (22P siege tank, 25 F2 new units): not a clear error |
| `spg9_73mm` (SPG-9 Kopyo 73 mm) | recoilless_gun_tower | TOO FAST | x0.47 | a tower or dug-in site: the balance pass after prompt 18 (A.2) gave the sites a faster rhythm than the vehicles on purpose |
| `tamir` (Tamir interceptor (Iron Dome)) | c_ram.dome | TOO SLOW | x6.83 | the real reference is an estimate (no published launch interval): not a clear error |
| `tower_kornet` (9M133 Kornet) | atgm_tower | TOO FAST | x0.28 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
| `turret_gmlrs` (M31 GMLRS 227 mm (tower)) | rocket_turret.guided | TOO FAST | x0.10 | DECISIONS 19R kept the ripple off the real pace on purpose (a real salvo would take 20-35 s of a 90 s fight) |
| `turret_gun_120` (Rh-120 L/44 120 mm) | gun_turret | TOO FAST | x0.27 | a tower or dug-in site: the balance pass after prompt 18 (A.2) gave the sites a faster rhythm than the vehicles on purpose |
| `turret_gun_120_long` (Rh-120 L/55 120 mm) | gun_turret.long, headquarters.fortress_ground | TOO FAST | x0.36 | a tower or dug-in site: the balance pass after prompt 18 (A.2) gave the sites a faster rhythm than the vehicles on purpose |
| `twin_30_bmpt` (2A42 30 mm (twin)) | bmpt | TOO SLOW | x5.55 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
