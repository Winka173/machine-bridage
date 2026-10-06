# Player and tower weapons waiting for the owner (full fix prompt L3, rule 9)

Written by `Tools/balance/full_weapon_audit.py`. The player rule: fix only clear unit errors and clear too-fast /
too-slow cadences, keeping the DPS (player balance waits for prompt 29's follow-up). Changed in this pass:
`turret_rockets` and `turret_rockets_cluster` (the BM-21's real 0.5 s between rockets, the cycle and the DPS kept).
Everything below is still flagged by the audit and was left as it is, with the reason.

| weapon | carriers | flags | game / reference | why left |
|---|---|---|---|---|
| `amos_120` (120 mm AMOS (twin)) | sp_mortar | TOO FAST | x1.16 | the real reference is an estimate (no published launch interval): not a clear error |
| `ballistic_missile` (9M723 Iskander (700 kg)) | ballistic_launcher | TOO FAST | x0.40 | DECISIONS 19R kept the ripple off the real pace on purpose (a real salvo would take 20-35 s of a 90 s fight) |
| `boss_missiles` (9M133 Kornet) | mara_behemoth | TOO FAST | x0.32 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
| `buk_launcher` (9M317 Buk) | sam_launcher | TOO FAST | x0.41 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
| `cruise_missile_ground` (Typhon MRC (ground-launched Tomahawk)) | ground_cruise_missile_vehicle | TOO SLOW | x7.50 | the real reference is an estimate (no published launch interval): not a clear error |
| `cruiser_203` (Mk 71 203 mm (twin)) | sea_cruiser | TOO SLOW | x2.36 | flagged, intent unknown: waits for the owner |
| `flak_35` (Oerlikon KDA 35 mm (Gepard)) | aa_vehicle | TOO SLOW | x5.42 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
| `gun_100_river` (A-190 100 mm (Buyan-class river gunboat)) | river_gunboat | TOO SLOW | x4.00 | a play-test or prompt-22+ unit tuned on purpose (22P siege tank, 25 F2 new units): not a clear error |
| `gun_105_apfsds` (2A75 125 mm APFSDS) | elite_tank_destroyer | TOO FAST | x0.46 | DECISIONS 19R kept it faster than real on purpose (a round at the top of its calibre band: the real rate would halve the unit's damage) |
| `gun_105_long` (2A75 125 mm (2S25 Sprut)) | tank_destroyer | TOO FAST | x0.39 | DECISIONS 19R kept it faster than real on purpose (a round at the top of its calibre band: the real rate would halve the unit's damage) |
| `gun_105_wheeled` (Centauro II 120 mm) | wheeled_gun | TOO FAST | x0.49 | DECISIONS 19R kept it faster than real on purpose (a round at the top of its calibre band: the real rate would halve the unit's damage) |
| `gun_155_coastal` (M284 155 mm (coastal battery)) | coastal_battery | TOO FAST | x0.29 | a tower or dug-in site: the balance pass after prompt 18 (A.2) gave the sites a faster rhythm than the vehicles on purpose |
| `gun_155_twin_ap` (M284 155 mm (twin) AP) | heavy_turret | TOO FAST | x0.37 | a tower or dug-in site: the balance pass after prompt 18 (A.2) gave the sites a faster rhythm than the vehicles on purpose |
| `gun_155_twin_coastlr` (M284 155 mm (twin, long-range coastal)) | heavy_turret.coastal | TOO FAST | x0.37 | a tower or dug-in site: the balance pass after prompt 18 (A.2) gave the sites a faster rhythm than the vehicles on purpose |
| `gun_57mm` (S-60 57 mm (2A91)) | light_tank | TOO SLOW | x6.43 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
| `gunship_105` (M102 105 mm) | sky_gunship | TOO FAST | x0.46 | DECISIONS 19R kept it faster than real on purpose (a round at the top of its calibre band: the real rate would halve the unit's damage) |
| `gunship_40mm` (Bofors L/60 40 mm) | sky_gunship | TOO FAST | x0.41 | DECISIONS 19R kept it faster than real on purpose (a round at the top of its calibre band: the real rate would halve the unit's damage) |
| `howitzer` (M284 155 mm) | artillery | TOO FAST | x0.55 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
| `jassm` (AGM-158 JASSM (450 kg)) | stealth_bomber | TOO FAST | x0.20 | the real reference is an estimate (no published launch interval): not a clear error |
| `jassm_swarm_carrier` (AGM-158 JASSM (swarm-carrier variant)) | swarm_carrier | TOO FAST | x0.20 | flagged, intent unknown: waits for the owner |
| `kornet_multi` (9M133 Kornet) | atgm_tower.multi | TOO FAST | x0.28 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
| `kornet_top` (9M133 Kornet) | atgm_tower.top | TOO FAST | x0.26 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
| `mlrs_elite` (M30 GMLRS 227 mm (cluster)) | elite_mlrs | TOO FAST | x0.03 | DECISIONS 19R kept the ripple off the real pace on purpose (a real salvo would take 20-35 s of a 90 s fight) |
| `mlrs_rockets` (M31 GMLRS 227 mm) | mlrs | TOO FAST | x0.06 | DECISIONS 19R kept the ripple off the real pace on purpose (a real salvo would take 20-35 s of a 90 s fight) |
| `naval_76` (OTO Melara 76/62) | sea_corvette | TOO SLOW | x3.60 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
| `one_shot_kornet` (9M133 Kornet) | one_shot_atgm_tower | TOO FAST | x0.06 | a tower or dug-in site: the balance pass after prompt 18 (A.2) gave the sites a faster rhythm than the vehicles on purpose |
| `patriot` (MIM-104 Patriot PAC-2) | missile_battery | TOO FAST | x0.53 | the real reference is an estimate (no published launch interval): not a clear error |
| `recoilless_106` (M40 106 mm recoilless rifle) | recoilless_jeep | TOO FAST | x0.56 | a play-test or prompt-22+ unit tuned on purpose (22P siege tank, 25 F2 new units): not a clear error |
| `rockets_300mm` (9M55 Smerch 300 mm) | heavy_rocket_artillery | TOO FAST | x0.08 | DECISIONS 19R kept the ripple off the real pace on purpose (a real salvo would take 20-35 s of a 90 s fight) |
| `sam_battery_lrr` (MIM-104 Patriot PAC-2) | missile_battery.lrr | TOO FAST | x0.65 | the real reference is an estimate (no published launch interval): not a clear error |
| `sam_pac3` (Patriot PAC-3 MSE) | missile_battery.pac3 | TOO FAST | x1.12 | the real reference is an estimate (no published launch interval): not a clear error |
| `siege_mortar_240` (2B8 240 mm (siege tank)) | siege_tank | TOO FAST | x0.16 | a play-test or prompt-22+ unit tuned on purpose (22P siege tank, 25 F2 new units): not a clear error |
| `tamir` (Tamir interceptor (Iron Dome)) | c_ram.dome | TOO SLOW | x6.83 | the real reference is an estimate (no published launch interval): not a clear error |
| `tower_kornet` (9M133 Kornet) | atgm_tower | TOO FAST | x0.28 | DECISIONS 19R reviewed it as close to the real rate (or set this pattern); the stricter rule here flags it: the owner's call |
| `turret_gmlrs` (M31 GMLRS 227 mm (tower)) | rocket_turret.guided | TOO FAST | x0.10 | DECISIONS 19R kept the ripple off the real pace on purpose (a real salvo would take 20-35 s of a 90 s fight) |
| `turret_gun_120` (Rh-120 L/44 120 mm) | gun_turret | TOO FAST | x0.38 | a tower or dug-in site: the balance pass after prompt 18 (A.2) gave the sites a faster rhythm than the vehicles on purpose |
| `turret_gun_120_long` (Rh-120 L/55 120 mm) | gun_turret.long, headquarters.fortress_ground | TOO FAST | x0.52 | a tower or dug-in site: the balance pass after prompt 18 (A.2) gave the sites a faster rhythm than the vehicles on purpose |
