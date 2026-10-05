# Flight feel report (lane B, 05/10, feature/flight-feel)

Spec: Docs/prompts/projectile_flight_feel_spec.md (P0/P1). Tool: `python Tools/balance/flight_feel_audit.py [--csv f]`
(raw -> family -> runtime replica of Catalog.cs, cross-checked on 359 weapons with 0 differences against the Unity snapshot before the edit,
plus the class validator). Nothing was run in Unity; no tests were run (owner rule). The Sim builds (dotnet build Tools/simbuild: 0 errors).

## 1. Pipeline and source of truth (spec 4, 7, 38, 39)

How the runtime speed is made (Catalog.cs `WeaponFamilies` + `Inherited`): a weapon with `inherits` takes its parent's already resolved
fields with its own on top, then **its `weaponFamily` row is laid over it (`JsonObject.Taking`): the family row's `projectileSpeed` beats the weapon's own line**;
`"weaponFamily": ""` opts out (the weapon keeps the parent's resolved or its own value). Variants (`weaponVariantId`, `weaponFamilyTable`) carry no speed.
No later stage scales speed: no boss multiplier (BossReach and `Tuned` copy the speed), no `flightProfile` factor (it only chooses the drawn path),
Sim flight = distance / `ProjectileSpeed` (CombatSystem.cs Fire); gear multiplies arm 0 by (1 + ProjectileSpeed stat, capped 0.30). The export reads the resolved value.

* `apkws_rocket`: own line 45 (dead value), family `apkws` row 180 (copied from Hydra 70 in prompt 25 A3) -> runtime and export 180. Now family 85 and own line 85.
* `anti_ship_missile`: own line 30 (dead), family `nsm_oniks` row 225 -> 225. Now family 95 and own line 95.
* Full scan (359 weapons incl. second rounds): the only own-line vs family-row disagreements were these two (the tool prints that count: 0 now). No hidden multiplier exists, so spreadsheet == runtime for every weapon (exported value = runtime value, 0 differences before and after).
* Cause: the family rows (prompt 25 A3) were set from real m/s with one scale, while weapon lines were hand-tuned later and silently shadowed. Remedy: family rows hold the speed; the `speedInheritanceSource` column of Vu_khi_suy_ra shows where each speed comes from.

## 2. Changed weapons (108 ids; old -> new, canonical location, flight min/half/max)

Canonical file: Assets/MachineBrigade/Resources/Data/balance.json. Flight time = range / speed (the Sim has no arcs).
New families (a spec speed differs for one member): `hydra_70_mm_jet` 100 (jet_rockets), `m284_155_mm_fixed` 65 (howitzer_fixed), `m284_155_mm_ext` 60 (howitzer_ext),
`m284_155_mm_coastal` 70 (gun_155_coastal, gun_155_twin_coastlr), `m284_155_mm_guided_fixed` 70, `m284_155_mm_guided_casemate` 65, `m284_155_mm_guided_coastal` 75. Edited family rows:
agm_114_hellfire 80, hydra_70_mm 95, s_8_80_mm 95, s_8_80_mm_boat 90, apkws 85, aim_9_sidewinder 115, 9m317_buk 145, mim_104_patriot_pac_2 165, nsm_oniks 95, 2b11_120_mm 45, 2b8_240_mm 40,
m284_155_mm_2 55, m284_155_mm_casemate 60, m284_155_mm_guided 60, bm_21_grad_122_mm(_2) 80, m31_gmlrs_227_mm 85, tos_1a_220_mm_thermobaric 65.

| id | class | old -> new m/s | location | flight min/half/max old (s) | new (s) |
|---|---|---|---|---|---|
| apkws_rocket | AIRCRAFT_ROCKET | 180 -> 85 | weaponFamilies[apkws] | 0.056/0.111/0.222 | 0.118/0.235/0.471 |
| boat_rockets | AIRCRAFT_ROCKET | 180 -> 90 | weaponFamilies[s_8_80_mm_boat] | 0.076/0.153/0.306 | 0.153/0.306/0.611 |
| gunship_rockets | AIRCRAFT_ROCKET | 180 -> 95 | weaponFamilies[s_8_80_mm] | 0.047/0.094/0.189 | 0.089/0.179/0.358 |
| heli_rockets | AIRCRAFT_ROCKET | 180 -> 95 | weaponFamilies[hydra_70_mm] | 0.042/0.083/0.167 | 0.079/0.158/0.316 |
| hind_rockets | AIRCRAFT_ROCKET | 180 -> 95 | weaponFamilies[s_8_80_mm] | 0.05/0.1/0.2 | 0.095/0.189/0.379 |
| jet_rockets | AIRCRAFT_ROCKET | 180 -> 100 | weaponFamilies[hydra_70_mm_jet] | 0.05/0.1/0.2 | 0.09/0.18/0.36 |
| s8_pods | AIRCRAFT_ROCKET | 180 -> 95 | weaponFamilies[s_8_80_mm] | 0.047/0.094/0.189 | 0.089/0.179/0.358 |
| scout_rockets | AIRCRAFT_ROCKET | 180 -> 95 | weaponFamilies[hydra_70_mm] | 0.039/0.078/0.156 | 0.074/0.147/0.295 |
| air_to_air | AIR_DEFENCE_MISSILE | 300 -> 140 | weapons[air_to_air] own line | 0.05/0.1/0.2 | 0.107/0.214/0.429 |
| buk_launcher | AIR_DEFENCE_MISSILE | 250 -> 145 | weaponFamilies[9m317_buk] | 0.055/0.11/0.22 | 0.095/0.19/0.379 |
| igla_v | AIR_DEFENCE_MISSILE | 170 -> 105 | weapons[igla_v] own line | 0.047/0.094/0.188 | 0.076/0.152/0.305 |
| missile_57e6 | AIR_DEFENCE_MISSILE | 300 -> 130 | weapons[missile_57e6] own line | 0.046/0.092/0.183 | 0.106/0.212/0.423 |
| patriot | AIR_DEFENCE_MISSILE | 300 -> 165 | weaponFamilies[mim_104_patriot_pac_2] | 0.067/0.15/0.3 | 0.121/0.273/0.545 |
| r60 | AIR_DEFENCE_MISSILE | 210 -> 110 | weapons[r60] own line | 0.033/0.067/0.133 | 0.064/0.127/0.255 |
| sam | AIR_DEFENCE_MISSILE | 200 -> 120 | weapons[sam] own line | 0.055/0.11/0.22 | 0.092/0.183/0.367 |
| sam_48n6 | AIR_DEFENCE_MISSILE | 300 -> 170 | weapons[sam_48n6] own line | 0.067/0.158/0.317 | 0.118/0.279/0.559 |
| sam_battery | AIR_DEFENCE_MISSILE | 95 -> 165 | weapons[sam_battery] own line | 0.211/0.474/0.947 | 0.121/0.273/0.545 |
| sam_battery_lrr | AIR_DEFENCE_MISSILE | 300 -> 165 | weaponFamilies[mim_104_patriot_pac_2] | 0.067/0.167/0.333 | 0.121/0.303/0.606 |
| sam_long | AIR_DEFENCE_MISSILE | 250 -> 145 | weaponFamilies[9m317_buk] | 0.055/0.11/0.22 | 0.095/0.19/0.379 |
| sam_pac3 | AIR_DEFENCE_MISSILE | 300 -> 165 | weapons[sam_pac3] own line | 0.067/0.12/0.24 | 0.121/0.218/0.436 |
| sam_post | AIR_DEFENCE_MISSILE | 80 -> 145 | weapons[sam_post] own line | 0.188/0.375/0.75 | 0.103/0.207/0.414 |
| stinger_atas | AIR_DEFENCE_MISSILE | 180 -> 105 | weapons[stinger_atas] own line | 0.042/0.083/0.167 | 0.071/0.143/0.286 |
| stinger_post | AIR_DEFENCE_MISSILE | 180 -> 105 | weapons[stinger_post] own line | 0.078/0.156/0.311 | 0.133/0.267/0.533 |
| tamir | AIR_DEFENCE_MISSILE | 180 -> 125 | weapons[tamir] own line | 0.083/0.167/0.333 | 0.12/0.24/0.48 |
| wvr_aam | AIR_DEFENCE_MISSILE | 210 -> 115 | weaponFamilies[aim_9_sidewinder] | 0.036/0.071/0.143 | 0.065/0.13/0.261 |
| anti_ship_missile | ANTI_SHIP_MISSILE | 225 -> 95 | weaponFamilies[nsm_oniks] | 0.156/0.311/0.622 | 0.368/0.737/1.474 |
| scylla_kh35 | ANTI_SHIP_MISSILE | 70 -> 90 | weapons[scylla_kh35] own line | 0.393/0.786/1.571 | 0.306/0.611/1.222 |
| p26_roc_main_roc_bombs | BOMB | 100 -> 60 | inherited from p26_roc_roc_bombs | 0.113/0.225/0.45 | 0.188/0.375/0.75 |
| p26_roc_roc_bombs | BOMB | 100 -> 60 | inherited from boss_howitzer | 0.113/0.225/0.45 | 0.188/0.375/0.75 |
| boss_howitzer | HOWITZER | 100 -> 60 | weapons[boss_howitzer] own line | 0.15/0.3/0.6 | 0.25/0.5/1.0 |
| boss_howitzer_guided | HOWITZER | 100 -> 60 | inherited from boss_howitzer | 0.15/0.3/0.6 | 0.25/0.5/1.0 |
| casemate_155 | HOWITZER | 100 -> 60 | weaponFamilies[m284_155_mm_casemate] | 0.2/0.375/0.75 | 0.333/0.625/1.25 |
| casemate_155_guided | HOWITZER | 45 -> 65 | weaponFamilies[m284_155_mm_guided_casemate] | 0.444/0.833/1.667 | 0.308/0.577/1.154 |
| gun_155_coastal | HOWITZER | 150 -> 70 | weaponFamilies[m284_155_mm_coastal] | 0.225/0.45/0.9 | 0.482/0.964/1.929 |
| gun_155_coastal_guided | HOWITZER | 150 -> 75 | weaponFamilies[m284_155_mm_guided_coastal] | 0.225/0.45/0.9 | 0.45/0.9/1.8 |
| gun_155_sph | HOWITZER | 100 -> 55 | weaponFamilies[m284_155_mm_2] | 0.25/0.5/1.0 | 0.455/0.909/1.818 |
| gun_155_twin_coastlr | HOWITZER | 150 -> 70 | weaponFamilies[m284_155_mm_coastal] | 0.12/0.24/0.48 | 0.257/0.514/1.029 |
| gun_155_twin_coastlr_guided | HOWITZER | 150 -> 75 | weaponFamilies[m284_155_mm_guided_coastal] | 0.12/0.24/0.48 | 0.24/0.48/0.96 |
| gun_203_siege | HOWITZER | 110 -> 65 | weapons[gun_203_siege] own line | 0.091/0.282/0.564 | 0.154/0.477/0.954 |
| howitzer | HOWITZER | 100 -> 55 | weaponFamilies[m284_155_mm_2] | 0.25/0.45/0.9 | 0.455/0.818/1.636 |
| howitzer_ext | HOWITZER | 100 -> 60 | weaponFamilies[m284_155_mm_ext] | 0.25/0.56/1.12 | 0.417/0.933/1.867 |
| howitzer_fixed | HOWITZER | 100 -> 65 | weaponFamilies[m284_155_mm_fixed] | 0.25/0.45/0.9 | 0.385/0.692/1.385 |
| howitzer_fixed_guided | HOWITZER | 45 -> 70 | weaponFamilies[m284_155_mm_guided_fixed] | 0.556/1.0/2.0 | 0.357/0.643/1.286 |
| howitzer_guided | HOWITZER | 45 -> 60 | weaponFamilies[m284_155_mm_guided] | 0.556/1.0/2.0 | 0.417/0.75/1.5 |
| p26_bastion_b155 | HOWITZER | 100 -> 60 | inherited from casemate_155 | 0.2/0.375/0.75 | 0.333/0.625/1.25 |
| p26_bastion_main_b155 | HOWITZER | 150 -> 60 | weapons[p26_bastion_main_b155] own line | 0.133/0.25/0.5 | 0.333/0.625/1.25 |
| p26_jotunn_jo203 | HOWITZER | 100 -> 60 | inherited from boss_howitzer | 0.15/0.3/0.6 | 0.25/0.5/1.0 |
| amos_120 | MORTAR | 60 -> 45 | weapons[amos_120] own line | 0.167/0.5/1.0 | 0.222/0.667/1.333 |
| boss_mortar | MORTAR | 60 -> 40 | weaponFamilies[2b8_240_mm] | 0.2/0.667/1.333 | 0.3/1.0/2.0 |
| mortar_120 | MORTAR | 60 -> 45 | weaponFamilies[2b11_120_mm] | 0.167/0.458/0.917 | 0.222/0.611/1.222 |
| mortar_240 | MORTAR | 60 -> 40 | weaponFamilies[2b8_240_mm] | 0.333/0.708/1.417 | 0.5/1.062/2.125 |
| p26_bastion_b240 | MORTAR | 60 -> 40 | inherited from boss_mortar | 0.2/0.667/1.333 | 0.3/1.0/2.0 |
| p26_bastion_sec_b240 | MORTAR | 60 -> 40 | inherited from p26_bastion_b240 | 0.233/0.667/1.333 | 0.35/1.0/2.0 |
| siege_mortar_240 | MORTAR | 60 -> 40 | weaponFamilies[2b8_240_mm] | 0.267/0.583/1.167 | 0.4/0.875/1.75 |
| train_mortar | MORTAR | 60 -> 45 | weaponFamilies[2b11_120_mm] | 0.167/0.5/1.0 | 0.222/0.667/1.333 |
| cruiser_203 | NAVAL_DIRECT | 110 -> 85 | weapons[cruiser_203] own line | 0.239/0.477/0.955 | 0.309/0.618/1.235 |
| cruiser_203_guided | NAVAL_DIRECT | 110 -> 85 | inherited from cruiser_203 | 0.239/0.477/0.955 | 0.309/0.618/1.235 |
| gun_100_river | NAVAL_DIRECT | 170 -> 100 | weapons[gun_100_river] own line | 0.103/0.206/0.412 | 0.175/0.35/0.7 |
| leviathan_460 | NAVAL_DIRECT | 200 -> 85 | weapons[leviathan_460] own line | 0.2/0.4/0.8 | 0.471/0.941/1.882 |
| leviathan_460_guided | NAVAL_DIRECT | 200 -> 85 | inherited from leviathan_460 | 0.2/0.4/0.8 | 0.471/0.941/1.882 |
| naval_100 | NAVAL_DIRECT | 110 -> 100 | weapons[naval_100] own line | 0.205/0.409/0.818 | 0.225/0.45/0.9 |
| naval_100_guided | NAVAL_DIRECT | 110 -> 100 | inherited from naval_100 | 0.205/0.409/0.818 | 0.225/0.45/0.9 |
| naval_127 | NAVAL_DIRECT | 110 -> 90 | weapons[naval_127] own line | 0.25/0.5/1.0 | 0.306/0.611/1.222 |
| naval_130_twin | NAVAL_DIRECT | 110 -> 90 | weapons[naval_130_twin] own line | 0.205/0.409/0.818 | 0.25/0.5/1.0 |
| naval_155_triple | NAVAL_DIRECT | 110 -> 88 | weapons[naval_155_triple] own line | 0.25/0.5/1.0 | 0.312/0.625/1.25 |
| naval_155_triple_guided | NAVAL_DIRECT | 110 -> 88 | inherited from naval_155_triple | 0.25/0.5/1.0 | 0.312/0.625/1.25 |
| naval_76 | NAVAL_DIRECT | 110 -> 95 | weapons[naval_76] own line | 0.216/0.432/0.864 | 0.25/0.5/1.0 |
| naval_76_guided | NAVAL_DIRECT | 110 -> 95 | inherited from naval_76 | 0.216/0.432/0.864 | 0.25/0.5/1.0 |
| nyx_ags_155 | NAVAL_DIRECT | 150 -> 88 | weapons[nyx_ags_155] own line | 0.133/0.267/0.533 | 0.227/0.455/0.909 |
| p26_leviathan_direct_lev127 | NAVAL_DIRECT | 110 -> 105 | weapons[p26_leviathan_direct_lev127] own line | 0.205/0.409/0.818 | 0.214/0.429/0.857 |
| p26_leviathan_lev127 | NAVAL_DIRECT | 110 -> 90 | weapons[p26_leviathan_lev127] own line | 0.205/0.409/0.818 | 0.25/0.5/1.0 |
| p26_leviathan_lev155 | NAVAL_DIRECT | 110 -> 88 | inherited from naval_155_triple | 0.25/0.5/1.0 | 0.312/0.625/1.25 |
| p26_leviathan_lev406 | NAVAL_DIRECT | 200 -> 85 | inherited from leviathan_460 | 0.2/0.4/0.8 | 0.471/0.941/1.882 |
| p26_leviathan_sec_lev155 | NAVAL_DIRECT | 150 -> 88 | weapons[p26_leviathan_sec_lev155] own line | 0.183/0.367/0.733 | 0.312/0.625/1.25 |
| p26_typhon_direct_ty100 | NAVAL_DIRECT | 120 -> 115 | weapons[p26_typhon_direct_ty100] own line | 0.188/0.375/0.75 | 0.196/0.391/0.783 |
| p26_typhon_ty100 | NAVAL_DIRECT | 110 -> 100 | inherited from naval_100 | 0.205/0.409/0.818 | 0.225/0.45/0.9 |
| pt14_co_203 | NAVAL_DIRECT | 110 -> 85 | inherited from cruiser_203 | 0.216/0.432/0.864 | 0.279/0.559/1.118 |
| pt14_co_v76 | NAVAL_DIRECT | 110 -> 95 | inherited from naval_76 | 0.159/0.318/0.636 | 0.184/0.368/0.737 |
| pt14_hp_155 | NAVAL_DIRECT | 110 -> 88 | inherited from naval_155_triple | 0.216/0.432/0.864 | 0.27/0.54/1.08 |
| pt14_hp_v127 | NAVAL_DIRECT | 110 -> 90 | inherited from naval_127 | 0.182/0.364/0.727 | 0.222/0.444/0.889 |
| boss_rockets | ROCKET_ARTILLERY | 65 -> 80 | weapons[boss_rockets] own line | 0.173/0.346/0.692 | 0.141/0.281/0.562 |
| grad_cluster | ROCKET_ARTILLERY | 130 -> 80 | weaponFamilies[bm_21_grad_122_mm_2] | 0.138/0.3/0.6 | 0.225/0.487/0.975 |
| grad_rockets | ROCKET_ARTILLERY | 130 -> 80 | weaponFamilies[bm_21_grad_122_mm] | 0.138/0.212/0.423 | 0.225/0.344/0.688 |
| mlrs_elite | ROCKET_ARTILLERY | 140 -> 85 | weapons[mlrs_elite] own line | 0.143/0.268/0.536 | 0.235/0.441/0.882 |
| mlrs_rockets | ROCKET_ARTILLERY | 140 -> 85 | weaponFamilies[m31_gmlrs_227_mm] | 0.143/0.393/0.786 | 0.235/0.647/1.294 |
| p26_behemoth_be_rockets | ROCKET_ARTILLERY | 130 -> 80 | weapons[p26_behemoth_be_rockets] own line | 0.087/0.173/0.346 | 0.141/0.281/0.562 |
| p26_behemoth_sec_be_rockets | ROCKET_ARTILLERY | 130 -> 80 | inherited from p26_behemoth_be_rockets | 0.087/0.173/0.346 | 0.141/0.281/0.562 |
| p26_jotunn_jo_rockets | ROCKET_ARTILLERY | 120 -> 80 | weapons[p26_jotunn_jo_rockets] own line | 0.094/0.188/0.375 | 0.141/0.281/0.562 |
| p26_jotunn_sec_jo_rockets | ROCKET_ARTILLERY | 120 -> 80 | inherited from p26_jotunn_jo_rockets | 0.094/0.188/0.375 | 0.141/0.281/0.562 |
| p26_nemesis_sec_boss_rockets | ROCKET_ARTILLERY | 65 -> 80 | weapons[p26_nemesis_sec_boss_rockets] own line | 0.173/0.346/0.692 | 0.141/0.281/0.562 |
| pt14_ixion_grad | ROCKET_ARTILLERY | 130 -> 80 | inherited from grad_rockets | 0.138/0.212/0.423 | 0.225/0.344/0.688 |
| pt14_train_grad | ROCKET_ARTILLERY | 65 -> 80 | weapons[pt14_train_grad] own line | 0.173/0.346/0.692 | 0.141/0.281/0.562 |
| rockets_300mm | ROCKET_ARTILLERY | 120 -> 80 | weapons[rockets_300mm] own line | 0.25/0.583/1.167 | 0.375/0.875/1.75 |
| technical_rockets | ROCKET_ARTILLERY | 80 -> 75 | weapons[technical_rockets] own line | 0.15/0.3/0.6 | 0.16/0.32/0.64 |
| thermobaric_rockets | ROCKET_ARTILLERY | 70 -> 65 | weaponFamilies[tos_1a_220_mm_thermobaric] | 0.171/0.343/0.686 | 0.185/0.369/0.738 |
| turret_gmlrs | ROCKET_ARTILLERY | 140 -> 85 | weaponFamilies[m31_gmlrs_227_mm] | 0.143/0.321/0.643 | 0.235/0.529/1.059 |
| turret_rockets | ROCKET_ARTILLERY | 130 -> 80 | weaponFamilies[bm_21_grad_122_mm] | 0.062/0.212/0.423 | 0.1/0.344/0.688 |
| turret_rockets_cluster | ROCKET_ARTILLERY | 130 -> 80 | weaponFamilies[bm_21_grad_122_mm_2] | 0.062/0.212/0.423 | 0.1/0.344/0.688 |
| turret_thermobaric | ROCKET_ARTILLERY | 130 -> 65 | weapons[turret_thermobaric] own line | 0.062/0.169/0.338 | 0.123/0.338/0.677 |
| drone_missile | TACTICAL_MISSILE | 110 -> 80 | weaponFamilies[agm_114_hellfire] | 0.109/0.218/0.436 | 0.15/0.3/0.6 |
| gun_launched_atgm | TACTICAL_MISSILE | 90 -> 75 | weapons[gun_launched_atgm] own line | 0.094/0.189/0.378 | 0.113/0.227/0.453 |
| hellfire_standoff | TACTICAL_MISSILE | 110 -> 80 | weaponFamilies[agm_114_hellfire] | 0.125/0.25/0.5 | 0.172/0.344/0.688 |
| hellfire_volley | TACTICAL_MISSILE | 110 -> 80 | weaponFamilies[agm_114_hellfire] | 0.102/0.205/0.409 | 0.141/0.281/0.562 |
| kh29 | TACTICAL_MISSILE | 120 -> 80 | weapons[kh29] own line | 0.083/0.167/0.333 | 0.125/0.25/0.5 |
| maverick | TACTICAL_MISSILE | 90 -> 80 | weapons[maverick] own line | 0.111/0.222/0.444 | 0.125/0.25/0.5 |
| pt14_co_spike | TACTICAL_MISSILE | 60 -> 75 | weapons[pt14_co_spike] own line | 0.333/0.667/1.333 | 0.267/0.533/1.067 |
| pt14_th_jagm | TACTICAL_MISSILE | 95 -> 85 | weapons[pt14_th_jagm] own line | 0.145/0.289/0.579 | 0.162/0.324/0.647 |
| vikhr | TACTICAL_MISSILE | 120 -> 85 | weapons[vikhr] own line | 0.115/0.229/0.458 | 0.162/0.324/0.647 |

Kept (not touched): cruise (jassm 70, air_cruise_missile 65, leviathan_cruise 70, hydra_club_s 70, cruise_missile_ground 70, nyx_tomahawk 70), bombs, drones (fpv 26, lancet 28, shahed 20),
ballistic_missile 200 (180 m reach: 0.9 s, validator ok), tank / APFSDS / MG / autocannon / railgun, the fort twin 155 and the boss and tank 152 direct guns (0.27-0.40 s), gunship_105 120, Kornet family 80, atgm 80, atgm_post 60 (Konkurs), recon_missile 60, hover_rockets 85.

### Superseded earlier slow-downs (conflicts)
| id | before this task | now | spec |
|---|---|---|---|
| boss_rockets (+ p26_behemoth_be_rockets 130, p26_jotunn_jo_rockets 120, p26_nemesis_sec_boss_rockets 65, sec copies) | 65 / 130 / 120 / 65 | 80 | 13, 14 (boss barrage 80) |
| pt14_train_grad | 65 | 80 | 13 (Grad 80) |
| sam_post (Buk post) | 80 | 145 | 6 (Buk 145) |
| sam_battery (Patriot car), sam_pac3, patriot, sam_battery_lrr | 95 / 300 | 165 | 6 (Patriot 165) |
| other play-test 14 values: pt14_co_spike 60, scylla_kh35 70, pt14_th_jagm 95 | | 75 (ATGM floor), 90 (anti-ship 90-100), 85 | 2, 7 |

## 3. Validator (spec 22-24, 42-43)
`NHANH_QUA` / `CHAM_QUA` are **not speed flags**: they are the fire-cycle flags of Tools/balance/full_weapon_audit.py (time of one round per barrel against the real rate, 0.6x and 2x). They stay: they audit rate of fire, which this task must not touch. The class-based effective flight-time validator is added next to them
(Tools/balance/flight_feel_audit.py `analyse`; exported as 10 columns of 01_chien_dau.xlsx sheet Vu_khi_suy_ra: toc_do_dan_hieu_dung_m_s, toc_do_dan_tran_trang_bi_m_s, thoi_gian_bay_tam_toi_thieu_s, thoi_gian_bay_nua_tam_s, thoi_gian_bay_tam_toi_da_s, thoi_gian_bay_tam_toi_da_tran_s, lop_cam_giac_dan, canh_bao_toc_do_dan, nguon_ke_thua_toc_do, khoang_cach_loat_m).
Warnings: TOO_FAST_FOR_CLASS / TOO_SLOW_FOR_CLASS (max-range flight outside the class band, or half-range flight under half the lower bound), TOO_FAST_AT_GEAR_CAP (flight at +30 % under 0.75x the lower bound), OWNER_EXCEPTION.
Bands (s at max range): DIRECT_FAST 0.15-0.50 (spec 0.45; +0.05 because the unchanged gunship 105 flies 0.48), TACTICAL_MISSILE 0.45-0.90, AIR_DEFENCE_MISSILE 0.25-1.00 (spec 0.50-1.00; a short MANPADS reach of 28-32 m cannot reach 0.5 s at the spec speeds), ROCKET_ARTILLERY 0.70-1.60, MORTAR 0.90-2.20 (spec 2.0; the heavy 240 mortar at 40 m/s over 85 m is 2.1 s), HOWITZER 0.90-2.00, CRUISE 1.20+,
extension classes (not in the spec enum): AIRCRAFT_ROCKET 0.25-0.65, NAVAL_DIRECT 0.60-2.00, ANTI_SHIP_MISSILE 0.90-1.80, BALLISTIC_MISSILE 0.60+; DRONE, BOMB and bullets are not validated. Min-range flight = minRange, else 25 % of reach. Ballistic arcs: the Sim has no trajectory (time = distance / speed; the drawn arc is stretched over the same time), so there is none to solve.
Result: old data 52 TOO_FAST and 47 at the gear cap; new data 14 TOO_FAST, 1 TOO_SLOW, 10 at the gear cap, 1 exception. Remaining warnings (the spec's speeds, applied as written; the game's short reach makes them fast or slow for their class):
- technical_rockets (ROCKET_ARTILLERY, 75 m/s, flight min/half/max 0.16/0.32/0.64 s): TOO_FAST_FOR_CLASS;TOO_FAST_AT_GEAR_CAP
- grad_rockets (ROCKET_ARTILLERY, 80 m/s, flight min/half/max 0.225/0.344/0.688 s): TOO_FAST_FOR_CLASS
- rockets_300mm (ROCKET_ARTILLERY, 80 m/s, flight min/half/max 0.375/0.875/1.75 s): TOO_SLOW_FOR_CLASS
- turret_rockets_cluster (ROCKET_ARTILLERY, 80 m/s, flight min/half/max 0.1/0.344/0.688 s): TOO_FAST_FOR_CLASS
- turret_thermobaric (ROCKET_ARTILLERY, 65 m/s, flight min/half/max 0.123/0.338/0.677 s): TOO_FAST_FOR_CLASS;TOO_FAST_AT_GEAR_CAP
- turret_rockets (ROCKET_ARTILLERY, 80 m/s, flight min/half/max 0.1/0.344/0.688 s): TOO_FAST_FOR_CLASS
- boss_rockets (ROCKET_ARTILLERY, 80 m/s, flight min/half/max 0.141/0.281/0.562 s): TOO_FAST_FOR_CLASS;TOO_FAST_AT_GEAR_CAP
- p26_behemoth_be_rockets (ROCKET_ARTILLERY, 80 m/s, flight min/half/max 0.141/0.281/0.562 s): TOO_FAST_FOR_CLASS;TOO_FAST_AT_GEAR_CAP
- p26_behemoth_sec_be_rockets (ROCKET_ARTILLERY, 80 m/s, flight min/half/max 0.141/0.281/0.562 s): TOO_FAST_FOR_CLASS;TOO_FAST_AT_GEAR_CAP
- p26_jotunn_jo_rockets (ROCKET_ARTILLERY, 80 m/s, flight min/half/max 0.141/0.281/0.562 s): TOO_FAST_FOR_CLASS;TOO_FAST_AT_GEAR_CAP
- p26_jotunn_sec_jo_rockets (ROCKET_ARTILLERY, 80 m/s, flight min/half/max 0.141/0.281/0.562 s): TOO_FAST_FOR_CLASS;TOO_FAST_AT_GEAR_CAP
- pt14_ixion_grad (ROCKET_ARTILLERY, 80 m/s, flight min/half/max 0.225/0.344/0.688 s): TOO_FAST_FOR_CLASS
- p26_nemesis_sec_boss_rockets (ROCKET_ARTILLERY, 80 m/s, flight min/half/max 0.141/0.281/0.562 s): TOO_FAST_FOR_CLASS;TOO_FAST_AT_GEAR_CAP
- pt14_train_grad (ROCKET_ARTILLERY, 80 m/s, flight min/half/max 0.141/0.281/0.562 s): TOO_FAST_FOR_CLASS;TOO_FAST_AT_GEAR_CAP
- pt14_co_spike (TACTICAL_MISSILE, 75 m/s, flight min/half/max 0.267/0.533/1.067 s): OWNER_EXCEPTION
- hover_rockets (ROCKET_ARTILLERY, 85 m/s, flight min/half/max 0.141/0.324/0.647 s): TOO_FAST_FOR_CLASS;TOO_FAST_AT_GEAR_CAP

Needs the owner's call (not changed): rocket artillery at 80 m/s over a 45-55 m reach flies 0.56-0.69 s (< 0.70); the boss barrages are the clearest (0.56 s). Smerch 80 over 140 m = 1.75 s (> 1.6).

## 8. Flight time before and after (min / half / max range) for the spec's test matrix
| id | class | m/s old -> new (at +30 % gear cap) | flight min/half/max OLD (s) | flight min/half/max NEW (s) | warning |
|---|---|---|---|---|---|
| hellfire_standoff | TACTICAL_MISSILE | 110 -> 80 (104.0) | 0.125 / 0.25 / 0.5 | 0.172 / 0.344 / 0.688 | ok |
| vikhr | TACTICAL_MISSILE | 120 -> 85 (110.5) | 0.115 / 0.229 / 0.458 | 0.162 / 0.324 / 0.647 | ok |
| maverick | TACTICAL_MISSILE | 90 -> 80 (104.0) | 0.111 / 0.222 / 0.444 | 0.125 / 0.25 / 0.5 | ok |
| kh29 | TACTICAL_MISSILE | 120 -> 80 (104.0) | 0.083 / 0.167 / 0.333 | 0.125 / 0.25 / 0.5 | ok |
| kornet_twin | TACTICAL_MISSILE | 80 -> 80 (104.0) | 0.156 / 0.312 / 0.625 | 0.156 / 0.312 / 0.625 | ok |
| apkws_rocket | AIRCRAFT_ROCKET | 180 -> 85 (110.5) | 0.056 / 0.111 / 0.222 | 0.118 / 0.235 / 0.471 | ok |
| anti_ship_missile | ANTI_SHIP_MISSILE | 225 -> 95 (123.5) | 0.156 / 0.311 / 0.622 | 0.368 / 0.737 / 1.474 | ok |
| stinger_atas | AIR_DEFENCE_MISSILE | 180 -> 105 (136.5) | 0.042 / 0.083 / 0.167 | 0.071 / 0.143 / 0.286 | ok |
| igla_v | AIR_DEFENCE_MISSILE | 170 -> 105 (136.5) | 0.047 / 0.094 / 0.188 | 0.076 / 0.152 / 0.305 | ok |
| r60 | AIR_DEFENCE_MISSILE | 210 -> 110 (143.0) | 0.033 / 0.067 / 0.133 | 0.064 / 0.127 / 0.255 | ok |
| wvr_aam | AIR_DEFENCE_MISSILE | 210 -> 115 (149.5) | 0.036 / 0.071 / 0.143 | 0.065 / 0.13 / 0.261 | ok |
| air_to_air | AIR_DEFENCE_MISSILE | 300 -> 140 (182.0) | 0.05 / 0.1 / 0.2 | 0.107 / 0.214 / 0.429 | ok |
| missile_57e6 | AIR_DEFENCE_MISSILE | 300 -> 130 (169.0) | 0.046 / 0.092 / 0.183 | 0.106 / 0.212 / 0.423 | ok |
| sam_long | AIR_DEFENCE_MISSILE | 250 -> 145 (188.5) | 0.055 / 0.11 / 0.22 | 0.095 / 0.19 / 0.379 | ok |
| patriot | AIR_DEFENCE_MISSILE | 300 -> 165 (214.5) | 0.067 / 0.15 / 0.3 | 0.121 / 0.273 / 0.545 | ok |
| sam_48n6 | AIR_DEFENCE_MISSILE | 300 -> 170 (221.0) | 0.067 / 0.158 / 0.317 | 0.118 / 0.279 / 0.559 | ok |
| mortar_120 | MORTAR | 60 -> 45 (58.5) | 0.167 / 0.458 / 0.917 | 0.222 / 0.611 / 1.222 | ok |
| amos_120 | MORTAR | 60 -> 45 (58.5) | 0.167 / 0.5 / 1.0 | 0.222 / 0.667 / 1.333 | ok |
| howitzer | HOWITZER | 100 -> 55 (71.5) | 0.25 / 0.45 / 0.9 | 0.455 / 0.818 / 1.636 | ok |
| howitzer_guided | HOWITZER | 45 -> 60 (78.0) | 0.556 / 1.0 / 2.0 | 0.417 / 0.75 / 1.5 | ok |
| gun_155_coastal | HOWITZER | 150 -> 70 (91.0) | 0.225 / 0.45 / 0.9 | 0.482 / 0.964 / 1.929 | ok |
| grad_rockets | ROCKET_ARTILLERY | 130 -> 80 (104.0) | 0.138 / 0.212 / 0.423 | 0.225 / 0.344 / 0.688 | TOO_FAST_FOR_CLASS |
| mlrs_rockets | ROCKET_ARTILLERY | 140 -> 85 (110.5) | 0.143 / 0.393 / 0.786 | 0.235 / 0.647 / 1.294 | ok |
| rockets_300mm | ROCKET_ARTILLERY | 120 -> 80 (104.0) | 0.25 / 0.583 / 1.167 | 0.375 / 0.875 / 1.75 | TOO_SLOW_FOR_CLASS |
| thermobaric_rockets | ROCKET_ARTILLERY | 70 -> 65 (84.5) | 0.171 / 0.343 / 0.686 | 0.185 / 0.369 / 0.738 | ok |
| naval_76 | NAVAL_DIRECT | 110 -> 95 (123.5) | 0.216 / 0.432 / 0.864 | 0.25 / 0.5 / 1.0 | ok |
| naval_100 | NAVAL_DIRECT | 110 -> 100 (130.0) | 0.205 / 0.409 / 0.818 | 0.225 / 0.45 / 0.9 | ok |
| naval_127 | NAVAL_DIRECT | 110 -> 90 (117.0) | 0.25 / 0.5 / 1.0 | 0.306 / 0.611 / 1.222 | ok |
| naval_155_triple | NAVAL_DIRECT | 110 -> 88 (114.4) | 0.25 / 0.5 / 1.0 | 0.312 / 0.625 / 1.25 | ok |
| boss_missiles | TACTICAL_MISSILE | 80 -> 80 (104.0) | 0.141 / 0.281 / 0.562 | 0.141 / 0.281 / 0.562 | ok |
| boss_rockets | ROCKET_ARTILLERY | 65 -> 80 (104.0) | 0.173 / 0.346 / 0.692 | 0.141 / 0.281 / 0.562 | TOO_FAST_FOR_CLASS;TOO_FAST_AT_GEAR_CAP |
| boss_mortar | MORTAR | 60 -> 40 (52.0) | 0.2 / 0.667 / 1.333 | 0.3 / 1.0 / 2.0 | ok |
| boss_howitzer | HOWITZER | 100 -> 60 (78.0) | 0.15 / 0.3 / 0.6 | 0.25 / 0.5 / 1.0 | ok |
| p26_leviathan_lev406 | NAVAL_DIRECT | 200 -> 85 (110.5) | 0.2 / 0.4 / 0.8 | 0.471 / 0.941 / 1.882 | ok |
| heli_rockets | AIRCRAFT_ROCKET | 180 -> 95 (123.5) | 0.042 / 0.083 / 0.167 | 0.079 / 0.158 / 0.316 | ok |
| jet_rockets | AIRCRAFT_ROCKET | 180 -> 100 (130.0) | 0.05 / 0.1 / 0.2 | 0.09 / 0.18 / 0.36 | ok |
| boat_rockets | AIRCRAFT_ROCKET | 180 -> 90 (117.0) | 0.076 / 0.153 / 0.306 | 0.153 / 0.306 / 0.611 | ok |
| jassm | CRUISE | 70 -> 70 (91.0) | 0.321 / 0.643 / 1.286 | 0.321 / 0.643 / 1.286 | ok |
| leviathan_cruise | CRUISE | 70 -> 70 (91.0) | 1.429 / 2.857 / 5.714 | 1.429 / 2.857 / 5.714 | ok |
| ballistic_missile | BALLISTIC_MISSILE | 200 -> 200 (260.0) | 0.2 / 0.45 / 0.9 | 0.2 / 0.45 / 0.9 | ok |
| lancet | DRONE | 28 -> 28 (36.4) | 0.893 / 1.786 / 3.571 | 0.893 / 1.786 / 3.571 | ok |
| fpv_swarm | DRONE | 26 -> 26 (33.8) | 0.462 / 1.442 / 2.885 | 0.462 / 1.442 / 2.885 | ok |
| shahed | DRONE | 20 -> 20 (26.0) | 1.0 / 3.75 / 7.5 | 1.0 / 3.75 / 7.5 | ok |
| gun_120mm | DIRECT_FAST | 170 -> 170 (221.0) | 0.047 / 0.094 / 0.188 | 0.047 / 0.094 / 0.188 | ok |
| gun_105_apfsds | DIRECT_FAST | 260 -> 260 (338.0) | 0.044 / 0.088 / 0.177 | 0.044 / 0.088 / 0.177 | ok |

## 10. Boss projectile inheritance (spec 14, 41)
No boss multiplier exists in the code (Catalog `Tuned`, BossReach, BossSystem checked: speed is copied). Boss rockets, mortars and howitzers now inherit their family: boss rockets 80 (Grad / Smerch class), boss_mortar and p26_bastion_b240 40, boss_howitzer / p26_jotunn_jo203 / p26_bastion(_main)_b155 60,
boss ATGM `boss_missiles` and copies 80 (Kornet family; the spec's 90 is "unless the family says otherwise"). Still different inside one `weaponFamilyId` (role splits; Tools/balance/fix_validate.py item 2 prints the same 27 pre-existing lines before and after, only numbers changed): cal_152_155 (indirect 60, naval 88, direct boss 152 gun 150), cal_203 (lobbed howitzer 60, naval cruiser 85), cal_127_130 (HE 90), cal_100_105_he (typhon AP 115, gunship direct 120).
Boss HP and armour: untouched.

## 11. Guided artillery (spec 12)
howitzer 55 -> howitzer_guided 60; howitzer_fixed 65 -> 70; casemate 60 -> 65; coastal 70 -> 75 (all base + 5; before: guided 45 against base 100, i.e. slower, and the direct guided 155 150). Naval and boss guided copies inherit the base speed (+0). gunship, behemoth and fort-twin guided keep their direct speed.

## 12. Naval direct shells (spec 16)
naval_76 95, naval_100 100, naval_127 and naval_130_twin 90, naval_155_triple / Leviathan sec 155 / nyx_ags_155 88, cruiser_203 85, the 460 mm 85 (not in the spec: 1.9 s over 160 m), gun_100_river 100; AP variants of the boss guns +15 % (typhon direct 100 -> 115, leviathan direct 127 90 -> 105). All were 110 (150 and 200 for the big boss ones).

## 13-17. Static regression (code read, nothing run)
* APS / CIWS (CombatSystem.PointDefence.cs): `EngageWindow` = 3 s of remaining flight, `ShortestBurst` 0.2 s, one round at a time, `ApsVolleySeconds` 0.4. All are time-based, none assumed a speed; the effect changes: rounds that flew 0.1-0.5 s (rarely engageable) now fly 0.3-2 s and sit in the window for their whole flight, so expect clearly more intercepts of rockets, mortar and howitzer shells and slow missiles. Nothing was nerfed (spec 27). **Needs a Unity run**: intercept rate per threat class; knobs in priority order: track / acquire time (to add), eligible-round rules, cooldown, probability, only then radius.
* Flares / jammer: time-based (`flareCueSeconds` 1.5, `flareGraceSeconds` 0.5 against `p.TimeLeft`): a flare cloud now catches slower missiles only in their last part; the 1.5 s cue matters for flights over 1.5 s (anti-ship 1.5 s; long SAM 0.6 s). Jam miss `guidedMissMin/Spread` are metres. No change; **needs a Unity run** for the decoy rate.
* Proximity fuze (`FixRules.ProximityFuze` 7 m) is a radius; rounds are time-parameterised (`TimeLeft`, `RoundAt` lerp), so intercept points use the actual flight time. No hard-coded speed in AI/, Strikes/, Modes/, Abilities/ (grep clean).
* AI lead (spec 31): `CombatSystem.LeadPoint` uses the arm's effective `ProjectileSpeed` (gear included) with `FixRules.LeadCap` 3 s: covers the longest new flight (2.1 s mortar, 1.9 s the 460 mm). Counter-battery uses distance only. No fix needed.
* **Fixed**: `BossSystem.MaxLead` 0.9 -> 2.5 s (BossSystem.BigAttacks.cs): the cap was tuned for 180-300 m/s rounds; with 40-60 m/s boss mortars and howitzers (2.0-2.25 s at reach) the view's shell would have flown about 2.5x faster than its data speed. The blast time (`Due` = the warning) is unchanged.
* Warning / reaction window (spec 15, 29): ordinary weapons do not warn (`warningRules.normalFire` false; snapshot: 0 warned weapons), so their reaction window is the flight itself (mortar 120 1.2 s, howitzer 1.6 s, MLRS 0.6-1.8 s). Boss big attacks: the ring runs until `Due` (3.5-4 s) and the shell flies inside it (the last min(flight, 2.5 s)): total = warning, never warning + flight. doomsday_missile 0.9 s, bastion_420 and monster_800 boss mortar 2.1-2.25 s, fortress_203 1.17 s, behemoth_barrage 3.5 s ring. No attack doubles its reaction time.
* Guidance turn (spec 34) and min range (spec 35): the Sim has no turning missile (a guided round is a timed straight flight to its aim point; divert rules only), so it cannot overshoot or U-turn; the drawn homing ease (`ProjectilePool` HomingRate, Game) is visual and time-based. `weapon.MinRange` gates fire (CombatSystem.cs 531). **Needs a Unity run** only for the look of slower Loft missiles.
* Salvo spacing (spec 36): `BurstInterval` is unchanged, so launch gaps in time are unchanged; the gap in metres is speed x interval: lowest s8_pods 4.8 m (was 9.0), hind_rockets 6.7, turret_thermobaric 7.8, jet_rockets 8.0, the rest 9.5 m or more. Nothing stacks; no change.
* ProjectileSpeed gear (spec 20-21): stat 0.04-0.10 per piece, cap 0.30, arm 0 only (GearCatalog.cs 437 and 499, GearSystem.cs 152). At the cap: Hellfire 80 -> 104, mortar 45 -> 58.5, boss rockets 80 -> 104 (0.43 s over 45 m). The validator flags 10 weapons at the cap: the rocket-artillery ones above.

## 19-20. Generated data and stale scan
Pack regenerated (`python Tools/export/export.py --game-json Docs/export/game_snapshot.json`, then `export.py check`: all PASS, NEED_CODE_CHECK 0). Stale old-speed scan: every numeric speed or flight cell of a changed weapon in the xlsx was compared with its old value: only the `_truoc` columns (comparison to base 5f5b3247) hold old values (21 cells, intended); the md files hold none.
Needs the lead's Unity re-export: game_snapshot.json `balancePack.weaponFlight[].speed / flightAtRangeSeconds`, `vehicles[].weapons[].speed / flightTime`, `secondRounds[].speed` for the changed ids (the file is stale; the pack shows the new numbers because its cells are computed from balance.json). Old tests asserting the pre-2026 scale (MissileFlightTests 19-24 m/s, PlayTest5/6/7 speeds) were already failing before this task and were not touched; PlayTest14LaneH/I and BalanceSheetTests (`FlightFeelOwnSpeed`) were updated (written, not run).

## 50. Confirmations
Cruise missile speeds were kept (no bug found). Tactical missiles remain faster than cruise (75-85 against 65-70; anti-ship 95). Balance is by in-game flight time (validator), not real m/s. Mortar is slow and high (45 / 40). Guided artillery is base + 5 at most (it was 45 against a base of 100, never 60 -> 150). The boss flag adds no speed (code checked; boss weapons now inherit their family). ProjectileSpeed gear stays capped at 30 % and the validator tests the capped flight. APS / CIWS were only read statically and nothing was nerfed; a Unity intercept measurement is still open. Warning lead and projectile travel were audited together (they do not add). APKWS (180 -> 85) and anti-ship (225 -> 95) raw / effective pipelines were verified and fixed. Bombs and drones were not changed. Direct tank / APFSDS / MG fire is unchanged. Boss HP and armour are unchanged. Damage, reload, fire rate, penetration and blast radius are unchanged (only `projectileSpeed` fields and family ids were edited).
