# Balance master final: implementation report

Branch feature/balance-final (worktree MachineBrigade-bal), 06/10. Source of truth: Docs/prompts/balance_master_final_spec.md;
owner brief: Docs/prompts/balance_master_final_vi.md (execution order 1-12 followed). Measurements were allowed by the owner for
this pass (spec 18): they ran headless on the engine-free Sim (new harness Tools/simbuild/regress, a port of the EditMode
ArmourBalanceMeasure / CombatValueMeasure benches) plus Python calculators over balance.json. One targeted Unity EditMode run
(ExportGameDoc, 70 s, passed, 0 compile errors) refreshed the snapshot before the owner's later stop on export regeneration;
that snapshot was used only as a third cross-check (below) and was not committed.

Every old -> new value is in Docs/balance/balance_final_changes.json (177 entries, written by
Tools/balance/balance_final_apply.py, which made every canonical edit in place with jsonc_edit: comments kept). Raw measurement
files: Docs/balance/balance_final/.

## 1. Canonical files changed

| file | what |
|---|---|
| Assets/MachineBrigade/Resources/Data/balance.json | every value below (weapons, weaponFamilies, secondRounds.rounds, vehicles, supports) |
| Assets/MachineBrigade/Resources/Data/campaign.json | the two scripted "Strike" events now name `scripted_barrage` (were `artillery_barrage`) |
| Assets/MachineBrigade/Scripts/Sim/Modes/BattleEvents.P28.cs | pressure barrage (battle event) -> `scripted_barrage` |
| Assets/MachineBrigade/Scripts/Sim/Modes/MissionEvents.Kinds.cs | default support of the Barrage, AllyArtillery and enemy-strike mission events -> `scripted_barrage` (3 sites) |
| Assets/MachineBrigade/Scripts/Sim/Modes/SiegeModes.cs | the siege HQ-phase barrage -> `scripted_barrage` |
| Assets/MachineBrigade/Scripts/Game/Hud/Strings.cs | name string `support.scripted_barrage` ("Barrage" / "Pháo kích") |
| Tools/balance/flight_feel_audit.py | validator bands set to the final spec 6 bands; new class AIR_DEFENCE_SHORT; half-range floor 0.30 s for tactical missiles |
| Tools/balance/balance_final_apply.py (new) | the apply script and its log |
| Tools/simbuild/regress (new) | headless regression harness (dotnet; no Unity) |

tunables.json, the boss data blocks (bossFrames, bossRanks, bossParts, bossWeaponOverrides, bigAttacks), gear, economy,
damage table and walls were not touched (diff-checked, sections 6 and 26).

## 2-4, 8-12. Every affected id, exact old -> new

Rounding: HP half-up to whole points (1050 x 1.05 = 1102.5 -> 1103), damage whole points from 50 up and one decimal below,
damage multipliers 4 decimals, radii 0.1 m. Inherited children take the new value automatically (tower branches, HQ types,
boss copies through families); they are in the runtime diff (Docs/balance/balance_final/rtdiff.txt: 268 runtime field
changes, all expected).

### Projectile speed (spec 3-5)

| section | id | field | old | new | rule |
|---|---|---|---|---|---|
| weaponFamilies | agm_114_hellfire | projectileSpeed | 80 | 70 | spec 3 final missile speed: Hellfire family (hellfire_standoff, hellfire_volley, drone_missile) |
| weaponFamilies | 9m133_kornet | projectileSpeed | 80 | 70 | spec 3 final missile speed: Kornet family (tower/twin/top/multi/one-shot, atgm_heavy, boss_missiles + copies) |
| weapons | atgm | projectileSpeed | 80 | 70 | spec 3 final missile speed: TOW family (BGM-71 TOW-2) |
| weapons | gun_launched_atgm | projectileSpeed | 75 | 70 | spec 3 final missile speed: gun-launched ATGM |
| weapons | pt14_th_jagm | projectileSpeed | 85 | 70 | spec 3 final missile speed: JAGM = Hellfire family (own line over drone_missile) |
| weapons | vikhr | projectileSpeed | 85 | 75 | spec 3 final missile speed: Vikhr |
| weapons | maverick | projectileSpeed | 80 | 75 | spec 3 final missile speed: Maverick |
| weapons | kh29 | projectileSpeed | 80 | 75 | spec 3 final missile speed: Kh-29 |
| weaponFamilies | apkws | projectileSpeed | 85 | 80 | spec 3 final missile speed/4: APKWS family row (the runtime source) |
| weapons | apkws_rocket | projectileSpeed | 85 | 80 | spec 3 final missile speed/4: APKWS own line kept equal to its family row |
| weaponFamilies | nsm_oniks | projectileSpeed | 95 | 80 | spec 3 final missile speed: anti-ship family row (the runtime source) |
| weapons | anti_ship_missile | projectileSpeed | 95 | 80 | spec 3 final missile speed: anti-ship own line kept equal to its family row |
| weapons | pt14_hp_nsm | projectileSpeed | 90 | 80 | spec 3 final missile speed: anti-ship (Hyperion's NSM, own line over anti_ship_missile) |
| weapons | scylla_kh35 | projectileSpeed | 90 | 80 | spec 3 final missile speed: anti-ship (Scylla's Kh-35, own line over anti_ship_missile) |
| weapons | stinger_atas | projectileSpeed | 105 | 90 | spec 3 final missile speed: Stinger ATAS |
| weapons | stinger_post | projectileSpeed | 105 | 90 | spec 3 final missile speed: Stinger (MANPADS post) |
| weapons | igla_v | projectileSpeed | 105 | 90 | spec 3 final missile speed: Igla-V |
| weapons | r60 | projectileSpeed | 110 | 95 | spec 3 final missile speed: R-60 |
| weaponFamilies | aim_9_sidewinder | projectileSpeed | 115 | 100 | spec 3 final missile speed: AIM-9 / WVR family row (wvr_aam) |
| weapons | sam | projectileSpeed | 120 | 100 | spec 3 final missile speed: generic SHORAD |
| weapons | tamir | projectileSpeed | 125 | 105 | spec 3 final missile speed: Tamir |
| weapons | missile_57e6 | projectileSpeed | 130 | 110 | spec 3 final missile speed: Pantsir 57E6 |
| weapons | air_to_air | projectileSpeed | 140 | 120 | spec 3 final missile speed: AMRAAM |
| weaponFamilies | 9m317_buk | projectileSpeed | 145 | 120 | spec 3 final missile speed: Buk player family row (buk_launcher, sam_long) |
| weaponFamilies | mim_104_patriot_pac_2 | projectileSpeed | 165 | 130 | spec 3 final missile speed: Patriot player family row (patriot, sam_battery_lrr) |
| weapons | sam_pac3 | projectileSpeed | 165 | 130 | spec 3 final missile speed: Patriot player (PAC-3 branch, own line over sam_battery) |
| weapons | sam_48n6 | projectileSpeed | 170 | 140 | spec 3 final missile speed: S-400 / 48N6 |
| weapons | sam_post | projectileSpeed | 145 | 80 | spec 3 boss-specific intentional exception (KEEP, restored): boss/ship sam_post Buk |
| weapons | sam_battery | projectileSpeed | 165 | 95 | spec 3 boss-specific intentional exception (KEEP, restored): Nemesis sam_battery Patriot (nuke_train only) |
| weapons | boss_rockets | projectileSpeed | 80 | 65 | spec 3/5 boss Grad / boss_rockets 65 (intentional boss override, restored) |
| weapons | p26_behemoth_be_rockets | projectileSpeed | 80 | 65 | spec 3/5 boss Grad / boss_rockets 65 (intentional boss override, restored) |
| weapons | p26_jotunn_jo_rockets | projectileSpeed | 80 | 65 | spec 3/5 boss Grad / boss_rockets 65 (intentional boss override, restored) |
| weapons | p26_nemesis_sec_boss_rockets | projectileSpeed | 80 | 65 | spec 3/5 boss Grad / boss_rockets 65 (intentional boss override, restored) |
| weapons | pt14_train_grad | projectileSpeed | 80 | 65 | spec 3/5 boss Grad / boss_rockets 65 (intentional boss override, restored) |
| weapons | pt14_ixion_grad | projectileSpeed | null | 65 | spec 3/5 boss Grad / boss_rockets 65 (intentional boss override, restored): Ixion's Grad (own line; it opted out of the Grad family) |
| weapons | hover_rockets | projectileSpeed | 85 | 65 | spec 3/5 boss Grad / boss_rockets 65 (intentional boss override, restored): landing hovercraft's 140 mm boss barrage (85 was outside the 65-80 boss band) |

### Bomb payloads (spec 8)

| section | id | field | old | new | rule |
|---|---|---|---|---|---|
| weapons | jet_bombs | damage | 310 | 388 | spec 8 conventional aircraft bomb (FAB-250) (x1.25) |
| weapons | bomber_payload | damage | 420 | 546 | spec 8 heavy-bomber conventional payload (FAB-500) (x1.3) |
| weapons | stealth_payload | damage | 892 | 1070 | spec 8 guided bomb / JDAM (GBU-31) (x1.2) |
| weapons | guided_bomb | damage | 250 | 300 | spec 8 guided bomb (GBU-39 SDB) (x1.2) |

### Aircraft HP and ground-attack output (spec 9)

| section | id | field | old | new | rule |
|---|---|---|---|---|---|
| vehicles | fighter_jet | hp | 600 | 690 | spec 9 aircraft HP: fighter / attack jet / stealth fighter (x1.15) |
| vehicles | stealth_fighter | hp | 600 | 690 | spec 9 aircraft HP: fighter / attack jet / stealth fighter (x1.15) |
| vehicles | attack_jet | hp | 650 | 748 | spec 9 aircraft HP: fighter / attack jet / stealth fighter (x1.15) |
| vehicles | elite_attack_jet | hp | 621 | 714 | spec 9 aircraft HP: fighter / attack jet / stealth fighter (x1.15) |
| vehicles | stealth_naval_strike | hp | 750 | 863 | spec 9 aircraft HP: fighter / attack jet / stealth fighter (x1.15) |
| vehicles | attack_helicopter | hp | 700 | 805 | spec 9 aircraft HP: attack / scout helicopter (x1.15) |
| vehicles | elite_attack_helicopter | hp | 675 | 776 | spec 9 aircraft HP: attack / scout helicopter (x1.15) |
| vehicles | scout_heli | hp | 518 | 596 | spec 9 aircraft HP: attack / scout helicopter (x1.15) |
| vehicles | twin_rotor_gunship | hp | 1400 | 1610 | spec 9 aircraft HP: heavy / twin-rotor gunship (x1.15) |
| vehicles | sky_gunship | hp | 1400 | 1610 | spec 9 aircraft HP: heavy / twin-rotor gunship (x1.15) |
| vehicles | heavy_bomber | hp | 1400 | 1680 | spec 9 aircraft HP: heavy bomber (x1.2) |
| vehicles | stealth_bomber | hp | 1200 | 1440 | spec 9 aircraft HP: heavy bomber (x1.2) |
| vehicles | swarm_carrier | hp | 1091 | 1255 | spec 9 aircraft HP: large airborne carrier (x1.15) |
| weapons | hellfire_standoff | damage | 260 | 281 | spec 9 non-bomb aircraft ground-attack output (aircraft-only weapon) (x1.08) |
| weapons | hellfire_volley | damage | 260 | 281 | spec 9 non-bomb aircraft ground-attack output (aircraft-only weapon) (x1.08) |
| weapons | apkws_rocket | damage | 90 | 97 | spec 9 non-bomb aircraft ground-attack output (aircraft-only weapon) (x1.08) |
| weapons | kh29 | damage | 378 | 408 | spec 9 non-bomb aircraft ground-attack output (aircraft-only weapon) (x1.08) |
| weapons | heli_gun | damage | 22 | 23.8 | spec 9 non-bomb aircraft ground-attack output (aircraft-only weapon) (x1.08) |
| weapons | heli_rockets | damage | 30 | 32.4 | spec 9 non-bomb aircraft ground-attack output (aircraft-only weapon) (x1.08) |
| weapons | minigun | damage | 5.5 | 5.9 | spec 9 non-bomb aircraft ground-attack output (aircraft-only weapon) (x1.08) |
| weapons | scout_rockets | damage | 30 | 32.4 | spec 9 non-bomb aircraft ground-attack output (aircraft-only weapon) (x1.08) |
| weapons | jet_cannon | damage | 23 | 24.8 | spec 9 non-bomb aircraft ground-attack output (aircraft-only weapon) (x1.08) |
| weapons | s8_pods | damage | 32 | 34.6 | spec 9 non-bomb aircraft ground-attack output (aircraft-only weapon) (x1.08) |
| vehicles | sky_gunship | outgoingDamageMult | 1.5159 | 1.6372 | spec 9 ground-attack output: sky gunship (all three guns ground attack; gunship_105 is shared with a boss part) (x1.08) |

### Ground vehicles (spec 10)

| section | id | field | old | new | rule |
|---|---|---|---|---|---|
| vehicles | main_battle_tank | hp | 1050 | 1103 | spec 10 ground: Main Battle Tank HP (x1.05) |
| vehicles | elite_mbt | hp | 1215 | 1276 | spec 10 ground: Main Battle Tank HP (x1.05) |
| vehicles | next_gen_tank | hp | 1318 | 1384 | spec 10 ground: Main Battle Tank HP (x1.05) |
| vehicles | heavy_tank | hp | 2032 | 2195 | spec 10 ground: Heavy Tank HP (x1.08) |
| vehicles | elite_heavy_tank | hp | 2560 | 2765 | spec 10 ground: Heavy Tank HP (x1.08) |
| vehicles | heavy_tank | outgoingDamageMult | 1.3538 | 1.4215 | spec 10 ground: Heavy Tank damage (x1.05) |
| vehicles | elite_heavy_tank | outgoingDamageMult | null | 1.05 | spec 10 ground: Heavy Tank damage (x1.05; the elite had no own multiplier) |
| vehicles | tank_destroyer | hp | 741 | 778 | spec 10 ground: Tank Destroyer HP (x1.05) |
| vehicles | elite_tank_destroyer | hp | 837 | 879 | spec 10 ground: Tank Destroyer HP (x1.05) |
| vehicles | flame_tank | hp | 741 | 800 | spec 10 ground: Flame Tank HP (x1.08) |
| vehicles | armored_bulldozer | hp | 1514 | 1665 | spec 10 ground: breacher / bulldozer / engineer assault HP (x1.1) |
| vehicles | engineer_vehicle | hp | 800 | 880 | spec 10 ground: breacher / bulldozer / engineer assault HP (x1.1) |
| vehicles | demolition_line_vehicle | hp | 545 | 600 | spec 10 ground: breacher / bulldozer / engineer assault HP (x1.1) |

### Towers (spec 11)

| section | id | field | old | new | rule |
|---|---|---|---|---|---|
| vehicles | guard_tower | hp | 700 | 840 | spec 11 tower: small combat HP (x1.2) |
| vehicles | mg_bunker | hp | 1500 | 1800 | spec 11 tower: small combat HP (x1.2) |
| vehicles | recoilless_gun_tower | hp | 545 | 654 | spec 11 tower: small combat HP (x1.2) |
| vehicles | guard_tower | outgoingDamageMult | null | 1.08 | spec 11 tower: small combat damage (x1.08) |
| vehicles | mg_bunker | outgoingDamageMult | 0.6086 | 0.6573 | spec 11 tower: small combat damage (x1.08) |
| vehicles | mg_bunker.twin | outgoingDamageMult | 0.5036 | 0.5439 | spec 11 tower: small combat damage (x1.08) |
| vehicles | mg_bunker.flame | outgoingDamageMult | 0.3248 | 0.3508 | spec 11 tower: small combat damage (x1.08) |
| vehicles | recoilless_gun_tower | outgoingDamageMult | null | 1.08 | spec 11 tower: small combat damage (x1.08) |
| vehicles | atgm_tower | hp | 900 | 1125 | spec 11 tower: medium combat HP (x1.25) |
| vehicles | atgm_tower | outgoingDamageMult | null | 1.1 | spec 11 tower: medium combat damage (x1.10) |
| vehicles | gun_turret | hp | 1800 | 2250 | spec 11 tower: medium combat HP (x1.25) |
| vehicles | gun_turret | outgoingDamageMult | null | 1.1 | spec 11 tower: medium combat damage (x1.10) |
| vehicles | rocket_turret | hp | 1100 | 1375 | spec 11 tower: medium combat HP (x1.25) |
| vehicles | rocket_turret | outgoingDamageMult | null | 1.1 | spec 11 tower: medium combat damage (x1.10) |
| vehicles | one_shot_atgm_tower | hp | 909 | 1136 | spec 11 tower: medium combat HP (x1.25) |
| vehicles | one_shot_atgm_tower | outgoingDamageMult | null | 1.1 | spec 11 tower: medium combat damage (x1.10) |
| vehicles | heavy_turret | hp | 2800 | 3640 | spec 11 tower: large combat HP (x1.3) |
| vehicles | heavy_turret.bastion | hp | 4340 | 5642 | spec 11 tower: large combat HP (x1.3) |
| vehicles | drone_hangar | hp | 2200 | 2860 | spec 11 tower: large combat HP (x1.3) |
| vehicles | heavy_turret | outgoingDamageMult | null | 1.1 | spec 11 tower: large combat damage (x1.10) |
| vehicles | drone_hangar | outgoingDamageMult | null | 1.1 | spec 11 tower: large combat damage (x1.10) |
| vehicles | aa_turret | hp | 1100 | 1320 | spec 11 tower: AA gun / SAM tower, small (HP by size, damage KEEP) (x1.2) |
| vehicles | manpads_tower | hp | 545 | 654 | spec 11 tower: SAM tower, small (HP by size, damage KEEP) (x1.2) |
| vehicles | aa_gun_tower | hp | 1273 | 1591 | spec 11 tower: AA gun tower, medium (HP by size, damage KEEP) (x1.25) |
| vehicles | missile_battery | hp | 1900 | 2470 | spec 11 tower: SAM tower, large (HP by size, damage KEEP) (x1.3) |
| vehicles | c_ram | hp | 1300 | 1495 | spec 11 tower: C-RAM / laser / point defence HP (raw damage KEEP) (x1.15) |
| vehicles | laser_ad_station | hp | 1136 | 1306 | spec 11 tower: C-RAM / laser / point defence HP (raw damage KEEP) (x1.15) |
| vehicles | drone_net_tower | hp | 364 | 419 | spec 11 tower: C-RAM / laser / point defence HP (raw damage KEEP) (x1.15) |
| vehicles | ew_tower | hp | 800 | 920 | spec 11 tower: EW / radar / flare utility HP (x1.15) |
| vehicles | flare_tower | hp | 455 | 523 | spec 11 tower: EW / radar / flare utility HP (x1.15) |
| vehicles | flare_searchlight_tower | hp | 455 | 523 | spec 11 tower: EW / radar / flare utility HP (x1.15) |
| vehicles | barrage_balloon | hp | 364 | 419 | spec 11 tower: EW / radar / flare utility HP (x1.15) |

### Structures (spec 12)

| section | id | field | old | new | rule |
|---|---|---|---|---|---|
| vehicles | airfield | hp | 1600 | 1920 | spec 12 structure HP (x1.2) |
| vehicles | repair_bay | hp | 1600 | 1920 | spec 12 structure HP (x1.2) |
| vehicles | logistics_station | hp | 1400 | 1680 | spec 12 structure HP (x1.2) |
| vehicles | vehicle_hangar | hp | 1800 | 2160 | spec 12 structure HP (x1.2) |
| vehicles | aircraft_hangar | hp | 1800 | 2160 | spec 12 structure HP (x1.2) |
| vehicles | cp_relay | hp | 600 | 720 | spec 12 structure HP (x1.2) |
| vehicles | targeting_station | hp | 700 | 840 | spec 12 structure HP (x1.2) |
| vehicles | fire_control_centre | hp | 1136 | 1420 | spec 12 structure HP: fire control centre (x1.25) |
| vehicles | super_gun | hp | 5200 | 5980 | spec 12 structure HP: super gun (destructible objective) (x1.15) |
| vehicles | headquarters | hp | 9000 | 9450 | spec 12 structure HP: HQ (its three HQ types inherit it) (x1.05) |
| vehicles | shield_tower | hp | 2000 | 2200 | spec 12 structure HP: Shield Tower body (dome / ward pool KEEP) (x1.1) |
| vehicles | shield_tower.ward | hp | 2000 | 2200 | spec 12 structure HP: Shield Tower body (dome / ward pool KEEP) (x1.1) |

### Bosses (spec 13)

| section | id | field | old | new | rule |
|---|---|---|---|---|---|
| weapons | boss_heli_gun | damage | null | 22 | spec 13 boss damage KEEP: pinned (it inherits heli_gun, which the aircraft pass raises) |
| weapons | boss_minigun | damage | null | 5.5 | spec 13 boss damage KEEP: pinned (it inherits minigun, which the aircraft pass raises) |
| vehicles | behemoth | hp | 35787 | 38650 | spec 13 main boss hull HP (armour KEEP) (x1.08) |
| vehicles | mobile_fortress | hp | 45320 | 48946 | spec 13 main boss hull HP (armour KEEP) (x1.08) |
| vehicles | armored_train | hp | 37750 | 39638 | spec 13 mini boss hull HP (armour KEEP) (x1.05) |
| vehicles | mega_gunship | hp | 29950 | 31448 | spec 13 mini boss hull HP (armour KEEP) (x1.05) |
| vehicles | drone_mothership | hp | 77823 | 84049 | spec 13 main boss hull HP (armour KEEP) (x1.08) |
| vehicles | nuke_train | hp | 118200 | 127656 | spec 13 main boss hull HP (armour KEEP) (x1.08) |
| vehicles | silver_bug | hp | 282320 | 304906 | spec 13 main boss hull HP (armour KEEP) (x1.08) |
| vehicles | behemoth_inferno | hp | 24600 | 25830 | spec 13 mini boss hull HP (armour KEEP) (x1.05) |
| vehicles | behemoth_tempest | hp | 37750 | 39638 | spec 13 mini boss hull HP (armour KEEP) (x1.05) |
| vehicles | fortress_bastion | hp | 25900 | 27972 | spec 13 main boss hull HP (armour KEEP) (x1.08) |
| vehicles | earth_borer | hp | 72000 | 75600 | spec 13 mini boss hull HP (armour KEEP) (x1.05) |
| vehicles | command_airship | hp | 205875 | 222345 | spec 13 main boss hull HP (armour KEEP) (x1.08) |
| vehicles | landing_hovercraft | hp | 53500 | 56175 | spec 13 mini boss hull HP (armour KEEP) (x1.05) |
| vehicles | leviathan | hp | 60900 | 65772 | spec 13 main boss hull HP (armour KEEP) (x1.08) |
| vehicles | moloch | hp | 93860 | 101369 | spec 13 main boss hull HP (armour KEEP) (x1.08) |
| vehicles | daedalus | hp | 240580 | 259826 | spec 13 main boss hull HP (armour KEEP) (x1.08) |
| vehicles | typhon | hp | 168632 | 182123 | spec 13 main boss hull HP (armour KEEP) (x1.08) |
| vehicles | ixion | hp | 98400 | 106272 | spec 13 main boss hull HP (armour KEEP) (x1.08) |
| vehicles | bastion_mk0 | hp | 19250 | 20213 | spec 13 mini boss hull HP (armour KEEP) (x1.05) |
| vehicles | fenrir | hp | 29950 | 31448 | spec 13 mini boss hull HP (armour KEEP) (x1.05) |
| vehicles | scylla | hp | 37750 | 39638 | spec 13 mini boss hull HP (armour KEEP) (x1.05) |
| vehicles | locust | hp | 45650 | 47933 | spec 13 mini boss hull HP (armour KEEP) (x1.05) |
| vehicles | behemoth_mk2 | hp | 53500 | 56175 | spec 13 mini boss hull HP (armour KEEP) (x1.05) |
| vehicles | icarus_mk0 | hp | 94850 | 99593 | spec 13 mini boss hull HP (armour KEEP) (x1.05) |
| vehicles | argus | hp | 94850 | 99593 | spec 13 mini boss hull HP (armour KEEP) (x1.05) |
| vehicles | behemoth_mk0 | hp | 33900 | 35595 | spec 13 mini boss hull HP (armour KEEP) (x1.05) |
| vehicles | kraken | hp | 168632 | 182123 | spec 13 main boss hull HP (armour KEEP) (x1.08) |
| vehicles | monster | hp | 158087 | 170734 | spec 13 main boss hull HP (armour KEEP) (x1.08) |
| vehicles | hyperion | hp | 282320 | 304906 | spec 13 main boss hull HP (armour KEEP) (x1.08) |
| vehicles | theia | hp | 94850 | 99593 | spec 13 mini boss hull HP (armour KEEP) (x1.05) |
| vehicles | coeus | hp | 94850 | 99593 | spec 13 mini boss hull HP (armour KEEP) (x1.05) |
| vehicles | nyx | hp | 37750 | 39638 | spec 13 mini boss hull HP (armour KEEP) (x1.05) |
| vehicles | hydra | hp | 81300 | 85365 | spec 13 mini boss hull HP (armour KEEP) (x1.05) |
| vehicles | nyx | outgoingDamageMult | 0.8362 | 0.9198 | spec 13 Nyx outgoing damage (x1.1) |
| vehicles | nyx | cruise.damage | 400 | 440 | spec 13 Nyx outgoing damage: its Tomahawk cruise strike (laid by NavalSystem, outside outgoingDamageMult) (x1.1) |
| vehicles | scylla | outgoingDamageMult | 0.7389 | 0.798 | spec 13 Scylla outgoing damage (x1.08) |
| vehicles | scylla | cruise.damage | 450 | 486 | spec 13 Scylla outgoing damage: its Kalibr cruise strike (laid by NavalSystem, outside outgoingDamageMult) (x1.08) |
| weaponFamilies | 2b8_240_mm_boss | (new row) | null | {"id": "2b8_240_mm_boss", "real": "2B8 240 mm", "projectileSpeed": 40, "splash": 9, "projectileModel": "mortar_bomb",... | spec 13/14: boss_mortar keeps its 9 m splash (boss damage KEEP) when the 240 mm row goes to 10 m |
| weapons | boss_mortar | weaponFamily | "2b8_240_mm" | "2b8_240_mm_boss" | spec 13 boss damage KEEP: boss_mortar off the player 240 mm row (same speed, model, 9 m) |

### Fire support and Artillery Barrage (spec 14-15)

| section | id | field | old | new | rule |
|---|---|---|---|---|---|
| weapons | mortar_120 | damage | 214 | 235 | spec 14 fire support: 120 mm mortar damage (x1.1) |
| weapons | amos_120 | damage | 214 | 235 | spec 14 fire support: AMOS damage (salvo, cooldown KEEP) (x1.1) |
| weaponFamilies | 2b8_240_mm | splash | 9 | 10 | spec 14 fire support: 240 mm splash 9 -> 10 (mortar_240, siege_mortar_240; damage KEEP) |
| weaponFamilies | m284_155_mm_2 | splash | 7 | 7.7 | spec 14 fire support: howitzer effective splash (family row; raw damage, Pen KEEP) (x1.1) |
| weaponFamilies | m284_155_mm_ext | splash | 7 | 7.7 | spec 14 fire support: howitzer effective splash (family row; raw damage, Pen KEEP) (x1.1) |
| weaponFamilies | m284_155_mm_fixed | splash | 7 | 7.7 | spec 14 fire support: howitzer effective splash (family row; raw damage, Pen KEEP) (x1.1) |
| weapons | howitzer_fixed | edge | 14 | 15.4 | spec 14 fire support: howitzer two-layer edge (howitzer_ext inherits it) (x1.1) |
| secondRounds.rounds | howitzer_fixed_guided | edge | null | 14 | spec 14 guided artillery splash KEEP: edge pinned (it inherits howitzer_fixed's edge, raised) |
| weapons | gun_203_siege | splash | 8 | 8.8 | spec 14 fire support: heavy 203 mm howitzer splash (own line, no family) (x1.1) |
| weaponFamilies | m31_gmlrs_227_mm_mlrs | (new row) | null | {"id": "m31_gmlrs_227_mm_mlrs", "real": "M31 GMLRS 227 mm", "projectileSpeed": 85, "splash": 4.9, "projectileModel": ... | spec 14 standard MLRS coverage +9 % (splash 4.5 -> 4.9); turret_gmlrs (tower) stays on m31_gmlrs_227_mm |
| weapons | mlrs_rockets | weaponFamily | "m31_gmlrs_227_mm" | "m31_gmlrs_227_mm_mlrs" | spec 14 fire support: MLRS card salvo on its own row (coverage) |
| weapons | grad_cluster | cluster.radius | 5 | 5.5 | spec 14 fire support: cluster MLRS coverage +10 % (bomblet damage KEEP) (x1.1) |
| weapons | mlrs_elite | cluster.radius | 6 | 6.6 | spec 14 fire support: cluster MLRS coverage +10 % (bomblet damage KEEP) (x1.1) |
| supports | scripted_barrage | (new event support) | null | {"id": "scripted_barrage", "kind": "Barrage", "pen": 3, "event": true, "cooldown": 60, "delay": 1.5, "radius": 10, "c... | spec 15: scripted campaign / battle-event / siege barrages keep the old artillery_barrage values |
| supports | artillery_barrage | blast | 7 | 7.7 | spec 15 artillery_barrage ~+10 % total strike value: blast radius 7 -> 7.7 (coverage lever only; measured +9.9 % on a 4-IFV group, +10.7 % on a spread group, +13.7 % on one tank); count, damage, cooldown KEEP |

Runtime effects that follow from these (not separate edits): runtime MaxHp = data hp x toughness (vehicles 2.2, bosses 0.85
and the rank share); the 240 mm mortars' derived warning seconds 2.5 -> 2.72 s (warning formula base + splash / escape speed;
ordinary fire does not warn, warningRules.normalFire false); elites' and two structures' AI "Power" (combat value) rise with HP.

Decisions inside the spec's ranges (owner may override):
* Aircraft ground-attack output x1.08 (low end of 1.08-1.10), on aircraft-only weapons; the AC-130 sky gunship through its
  outgoingDamageMult (its 105 mm is shared with a boss part). twin_rotor_gunship's agl_40 is shared with the river patrol boat,
  so only its heli_gun rises. Fighters' cannon and all AAM / cruise payloads unchanged; drones (strike / recon) unchanged.
* Classes applied to their elites too (elite MBT / heavy / TD / attack helicopter / attack jet) so the elite-over-base gap holds;
  next_gen_tank (Armata) counted as an MBT. elite_heavy_tank got outgoingDamageMult 1.05 (it had none).
* Towers: tower damage through each tower's outgoingDamageMult (tower weapons untouched; branches inherit it; branches with
  their own multiplier scaled). C-RAM / laser / point defence at x1.15 (low end). barrage_balloon (radar aerostat) counted as
  radar utility x1.15; targeting_station as radar / targeting x1.20.
* Not changed (not named by the spec; owner decision 1): coastal_battery (campaign emplacement), bunker_shelter_tower,
  blast_wall (wall-like), bulwark_post (gear-made temporary post), wheeled_gun, mara_behemoth (story ally).
* Howitzer coverage = splash radius x1.10 on the player families (m284_155_mm_2, _ext, _fixed) and the 203 mm; two-layer edge
  x1.10; guided rounds keep 7 m (their own rows). Standard MLRS coverage = the mlrs card salvo splash 4.5 -> 4.9 (+9 %) on a
  new row `m31_gmlrs_227_mm_mlrs`; the GMLRS tower branch stays on the old row (it already takes the tower damage buff).
  Cluster MLRS = cluster.radius x1.10 (elite_mlrs, elite_grad). Tower rocket branches, Smerch, Grad, technical and TOS unchanged.
* 240 mm: the splash lives on the family row, which the boss mortar shared: the boss mortar moved to a copy row
  `2b8_240_mm_boss` (9 m, same speed and model), so only mortar_240 / siege_mortar_240 reach 10 m.
* Bombs: no aircraft-carried cluster bomb exists (the only cluster bomb is the consumable `cluster_strike` support), so the
  cluster-bomb rule had no target; support cards other than artillery_barrage were not changed (owner decision 2).

## 3, 17, 18. Runtime-effective projectile speeds, flight times, legal max-geared speeds

53 runtime speeds changed (all 359 weapons checked). Flight time = distance / speed (the Sim flies a straight timed path).
Min distance = minRange, else 25 % of reach. Gear: ProjectileSpeed +4/+6/+8/+10 % a piece, BuildCap 30 %, main weapon (arm 0)
only (GearCatalog.cs, GearSystem.cs). Legal max-geared = speed x 1.30.

| class | id | m/s old -> new | runtime source | flight min/half/max OLD (s) | flight min/half/max NEW (s) | legal max-geared m/s (+30 %) | max-range flight at cap (s) | gear applies | validator |
|---|---|---|---|---|---|---|---|---|---|
| AIRCRAFT_ROCKET | apkws_rocket | 85 -> 80 | family apkws | 0.118 / 0.235 / 0.471 | 0.125 / 0.25 / 0.5 | 104.0 | 0.385 | secondary/boss mount (gear cap does not apply) | ok |
| AIR_DEFENCE_MISSILE | air_to_air | 140 -> 120 | own line | 0.107 / 0.214 / 0.429 | 0.125 / 0.25 / 0.5 | 156.0 | 0.385 | main of fighter_jet,stealth_fighter | ok |
| AIR_DEFENCE_MISSILE | buk_launcher | 145 -> 120 | family 9m317_buk | 0.095 / 0.19 / 0.379 | 0.115 / 0.229 / 0.458 | 156.0 | 0.353 | main of sam_launcher | ok |
| AIR_DEFENCE_MISSILE | missile_57e6 | 130 -> 110 | own line | 0.106 / 0.212 / 0.423 | 0.125 / 0.25 / 0.5 | 143.0 | 0.385 | secondary/boss mount (gear cap does not apply) | ok |
| AIR_DEFENCE_MISSILE | patriot | 165 -> 130 | family mim_104_patriot_pac_2 | 0.121 / 0.273 / 0.545 | 0.154 / 0.346 / 0.692 | 169.0 | 0.533 | main of missile_battery | ok |
| AIR_DEFENCE_MISSILE | sam | 120 -> 100 | own line | 0.092 / 0.183 / 0.367 | 0.11 / 0.22 / 0.44 | 130.0 | 0.338 | main of manpads_tower | ok |
| AIR_DEFENCE_MISSILE | sam_48n6 | 170 -> 140 | own line | 0.118 / 0.279 / 0.559 | 0.143 / 0.339 / 0.679 | 182.0 | 0.522 | main of long_sam,elite_long_sam | ok |
| AIR_DEFENCE_MISSILE | sam_battery | 165 -> 95 | own line | 0.121 / 0.273 / 0.545 | 0.211 / 0.474 / 0.947 | 123.5 | 0.729 | secondary/boss mount (gear cap does not apply) | TOO_SLOW_FOR_CLASS |
| AIR_DEFENCE_MISSILE | sam_battery_lrr | 165 -> 130 | family mim_104_patriot_pac_2 | 0.121 / 0.303 / 0.606 | 0.154 / 0.385 / 0.769 | 169.0 | 0.592 | main of missile_battery.lrr | ok |
| AIR_DEFENCE_MISSILE | sam_long | 145 -> 120 | family 9m317_buk | 0.095 / 0.19 / 0.379 | 0.115 / 0.229 / 0.458 | 156.0 | 0.353 | secondary/boss mount (gear cap does not apply) | ok |
| AIR_DEFENCE_MISSILE | sam_pac3 | 165 -> 130 | own line (over sam_battery) | 0.121 / 0.218 / 0.436 | 0.154 / 0.277 / 0.554 | 169.0 | 0.426 | main of missile_battery.pac3 | ok |
| AIR_DEFENCE_MISSILE | sam_post | 145 -> 80 | own line (over sam_long) | 0.103 / 0.207 / 0.414 | 0.188 / 0.375 / 0.75 | 104.0 | 0.577 | main of typhon | ok |
| AIR_DEFENCE_MISSILE | tamir | 125 -> 105 | own line | 0.12 / 0.24 / 0.48 | 0.143 / 0.286 / 0.571 | 136.5 | 0.44 | main of c_ram.dome | ok |
| AIR_DEFENCE_SHORT | igla_v | 105 -> 90 | own line | 0.076 / 0.152 / 0.305 | 0.089 / 0.178 / 0.356 | 117.0 | 0.274 | secondary/boss mount (gear cap does not apply) | ok |
| AIR_DEFENCE_SHORT | r60 | 110 -> 95 | own line | 0.064 / 0.127 / 0.255 | 0.074 / 0.147 / 0.295 | 123.5 | 0.227 | secondary/boss mount (gear cap does not apply) | TOO_FAST_FOR_CLASS |
| AIR_DEFENCE_SHORT | stinger_atas | 105 -> 90 | own line | 0.071 / 0.143 / 0.286 | 0.083 / 0.167 / 0.333 | 117.0 | 0.256 | secondary/boss mount (gear cap does not apply) | ok |
| AIR_DEFENCE_SHORT | stinger_post | 105 -> 90 | own line (over sam) | 0.133 / 0.267 / 0.533 | 0.156 / 0.311 / 0.622 | 117.0 | 0.479 | main of aa_turret.sam | ok |
| AIR_DEFENCE_SHORT | wvr_aam | 115 -> 100 | family aim_9_sidewinder | 0.065 / 0.13 / 0.261 | 0.075 / 0.15 / 0.3 | 130.0 | 0.231 | secondary/boss mount (gear cap does not apply) | ok |
| ANTI_SHIP_MISSILE | anti_ship_missile | 95 -> 80 | family nsm_oniks | 0.368 / 0.737 / 1.474 | 0.438 / 0.875 / 1.75 | 104.0 | 1.346 | secondary/boss mount (gear cap does not apply) | ok |
| ANTI_SHIP_MISSILE | pt14_hp_nsm | 90 -> 80 | own line (over anti_ship_missile) | 0.264 / 0.528 / 1.056 | 0.297 / 0.594 / 1.188 | 104.0 | 0.913 | secondary/boss mount (gear cap does not apply) | ok |
| ANTI_SHIP_MISSILE | scylla_kh35 | 90 -> 80 | own line (over anti_ship_missile) | 0.306 / 0.611 / 1.222 | 0.344 / 0.688 / 1.375 | 104.0 | 1.058 | secondary/boss mount (gear cap does not apply) | ok |
| ROCKET_ARTILLERY | boss_rockets | 80 -> 65 | own line | 0.141 / 0.281 / 0.562 | 0.173 / 0.346 / 0.692 | 84.5 | 0.533 | secondary/boss mount (gear cap does not apply) | TOO_FAST_FOR_CLASS |
| ROCKET_ARTILLERY | hover_rockets | 85 -> 65 | own line | 0.141 / 0.324 / 0.647 | 0.185 / 0.423 / 0.846 | 84.5 | 0.651 | secondary/boss mount (gear cap does not apply) | ok |
| ROCKET_ARTILLERY | p26_behemoth_be_rockets | 80 -> 65 | own line (over boss_rockets) | 0.141 / 0.281 / 0.562 | 0.173 / 0.346 / 0.692 | 84.5 | 0.533 | secondary/boss mount (gear cap does not apply) | TOO_FAST_FOR_CLASS |
| ROCKET_ARTILLERY | p26_behemoth_sec_be_rockets | 80 -> 65 | inherited from p26_behemoth_be_rockets | 0.141 / 0.281 / 0.562 | 0.173 / 0.346 / 0.692 | 84.5 | 0.533 | secondary/boss mount (gear cap does not apply) | TOO_FAST_FOR_CLASS |
| ROCKET_ARTILLERY | p26_jotunn_jo_rockets | 80 -> 65 | own line (over boss_rockets) | 0.141 / 0.281 / 0.562 | 0.173 / 0.346 / 0.692 | 84.5 | 0.533 | secondary/boss mount (gear cap does not apply) | TOO_FAST_FOR_CLASS |
| ROCKET_ARTILLERY | p26_jotunn_sec_jo_rockets | 80 -> 65 | inherited from p26_jotunn_jo_rockets | 0.141 / 0.281 / 0.562 | 0.173 / 0.346 / 0.692 | 84.5 | 0.533 | secondary/boss mount (gear cap does not apply) | TOO_FAST_FOR_CLASS |
| ROCKET_ARTILLERY | p26_nemesis_sec_boss_rockets | 80 -> 65 | own line (over boss_rockets) | 0.141 / 0.281 / 0.562 | 0.173 / 0.346 / 0.692 | 84.5 | 0.533 | secondary/boss mount (gear cap does not apply) | TOO_FAST_FOR_CLASS |
| ROCKET_ARTILLERY | pt14_ixion_grad | 80 -> 65 | own line (over grad_rockets) | 0.225 / 0.344 / 0.688 | 0.277 / 0.423 / 0.846 | 84.5 | 0.651 | secondary/boss mount (gear cap does not apply) | ok |
| ROCKET_ARTILLERY | pt14_train_grad | 80 -> 65 | own line (over boss_rockets) | 0.141 / 0.281 / 0.562 | 0.173 / 0.346 / 0.692 | 84.5 | 0.533 | secondary/boss mount (gear cap does not apply) | TOO_FAST_FOR_CLASS |
| TACTICAL_MISSILE | atgm | 80 -> 70 | own line | 0.125 / 0.25 / 0.5 | 0.143 / 0.286 / 0.571 | 91.0 | 0.44 | secondary/boss mount (gear cap does not apply) | TOO_FAST_FOR_CLASS |
| TACTICAL_MISSILE | atgm_heavy | 80 -> 70 | family 9m133_kornet | 0.131 / 0.263 / 0.525 | 0.15 / 0.3 / 0.6 | 91.0 | 0.462 | secondary/boss mount (gear cap does not apply) | ok |
| TACTICAL_MISSILE | boss_missiles | 80 -> 70 | family 9m133_kornet | 0.141 / 0.281 / 0.562 | 0.161 / 0.321 / 0.643 | 91.0 | 0.495 | secondary/boss mount (gear cap does not apply) | ok |
| TACTICAL_MISSILE | drone_missile | 80 -> 70 | family agm_114_hellfire | 0.15 / 0.3 / 0.6 | 0.171 / 0.343 / 0.686 | 91.0 | 0.527 | main of strike_drone | ok |
| TACTICAL_MISSILE | gun_launched_atgm | 75 -> 70 | own line | 0.113 / 0.227 / 0.453 | 0.121 / 0.243 / 0.486 | 91.0 | 0.374 | secondary/boss mount (gear cap does not apply) | TOO_FAST_FOR_CLASS;TOO_FAST_AT_GEAR_CAP |
| TACTICAL_MISSILE | hellfire_standoff | 80 -> 70 | family agm_114_hellfire | 0.172 / 0.344 / 0.688 | 0.196 / 0.393 / 0.786 | 91.0 | 0.604 | main of attack_helicopter | ok |
| TACTICAL_MISSILE | hellfire_volley | 80 -> 70 | family agm_114_hellfire | 0.141 / 0.281 / 0.562 | 0.161 / 0.321 / 0.643 | 91.0 | 0.495 | main of elite_attack_helicopter | ok |
| TACTICAL_MISSILE | kh29 | 80 -> 75 | own line | 0.125 / 0.25 / 0.5 | 0.133 / 0.267 / 0.533 | 97.5 | 0.41 | secondary/boss mount (gear cap does not apply) | TOO_FAST_FOR_CLASS;TOO_FAST_AT_GEAR_CAP |
| TACTICAL_MISSILE | kornet_multi | 80 -> 70 | family 9m133_kornet | 0.156 / 0.312 / 0.625 | 0.179 / 0.357 / 0.714 | 91.0 | 0.549 | main of atgm_tower.multi | ok |
| TACTICAL_MISSILE | kornet_top | 80 -> 70 | family 9m133_kornet | 0.156 / 0.312 / 0.625 | 0.179 / 0.357 / 0.714 | 91.0 | 0.549 | main of atgm_tower.top | ok |
| TACTICAL_MISSILE | kornet_twin | 80 -> 70 | family 9m133_kornet | 0.156 / 0.312 / 0.625 | 0.179 / 0.357 / 0.714 | 91.0 | 0.549 | secondary/boss mount (gear cap does not apply) | ok |
| TACTICAL_MISSILE | maverick | 80 -> 75 | own line | 0.125 / 0.25 / 0.5 | 0.133 / 0.267 / 0.533 | 97.5 | 0.41 | secondary/boss mount (gear cap does not apply) | TOO_FAST_FOR_CLASS;TOO_FAST_AT_GEAR_CAP |
| TACTICAL_MISSILE | one_shot_kornet | 80 -> 70 | family 9m133_kornet | 0.156 / 0.312 / 0.625 | 0.179 / 0.357 / 0.714 | 91.0 | 0.549 | main of one_shot_atgm_tower | ok |
| TACTICAL_MISSILE | p26_bastion_tiny_kornet_twin | 80 -> 70 | inherited from kornet_twin | 0.156 / 0.312 / 0.625 | 0.179 / 0.357 / 0.714 | 91.0 | 0.549 | secondary/boss mount (gear cap does not apply) | ok |
| TACTICAL_MISSILE | p26_behemoth_tiny_boss_missiles | 80 -> 70 | inherited from boss_missiles | 0.141 / 0.281 / 0.562 | 0.161 / 0.321 / 0.643 | 91.0 | 0.495 | secondary/boss mount (gear cap does not apply) | ok |
| TACTICAL_MISSILE | p26_matriarch_direct_ma_atgm | 80 -> 70 | inherited from p26_matriarch_ma_atgm | 0.172 / 0.344 / 0.688 | 0.196 / 0.393 / 0.786 | 91.0 | 0.604 | secondary/boss mount (gear cap does not apply) | ok |
| TACTICAL_MISSILE | p26_matriarch_ma_atgm | 80 -> 70 | inherited from boss_missiles | 0.172 / 0.344 / 0.688 | 0.196 / 0.393 / 0.786 | 91.0 | 0.604 | secondary/boss mount (gear cap does not apply) | ok |
| TACTICAL_MISSILE | p26_roc_direct_roc_atgm | 80 -> 70 | inherited from p26_roc_roc_atgm | 0.172 / 0.344 / 0.688 | 0.196 / 0.393 / 0.786 | 91.0 | 0.604 | secondary/boss mount (gear cap does not apply) | ok |
| TACTICAL_MISSILE | p26_roc_roc_atgm | 80 -> 70 | inherited from boss_missiles | 0.172 / 0.344 / 0.688 | 0.196 / 0.393 / 0.786 | 91.0 | 0.604 | secondary/boss mount (gear cap does not apply) | ok |
| TACTICAL_MISSILE | pt14_ixion_kornet | 80 -> 70 | inherited from boss_missiles | 0.141 / 0.281 / 0.562 | 0.161 / 0.321 / 0.643 | 91.0 | 0.495 | secondary/boss mount (gear cap does not apply) | ok |
| TACTICAL_MISSILE | pt14_th_jagm | 85 -> 70 | own line (over drone_missile) | 0.162 / 0.324 / 0.647 | 0.196 / 0.393 / 0.786 | 91.0 | 0.604 | secondary/boss mount (gear cap does not apply) | ok |
| TACTICAL_MISSILE | tower_kornet | 80 -> 70 | family 9m133_kornet | 0.156 / 0.312 / 0.625 | 0.179 / 0.357 / 0.714 | 91.0 | 0.549 | main of atgm_tower | ok |
| TACTICAL_MISSILE | vikhr | 85 -> 75 | own line | 0.162 / 0.324 / 0.647 | 0.183 / 0.367 / 0.733 | 97.5 | 0.564 | secondary/boss mount (gear cap does not apply) | ok |

changed 53

Validator (Tools/balance/flight_feel_audit.py, final spec 6 bands) on the final data: 25 flags, all the spec's own speeds at
the game's short ranges, none changed: TOW `atgm` 70 m/s over 40 m (half 0.29 s), gun_launched_atgm 0.49 s, kh29 / maverick
75 m/s over 40 m (0.53 s), atgm_post (Konkurs, kept 60) 0.57 s, r60 over 28 m (0.30 s), the Grad / tower / boss rocket
barrages over 44-55 m (0.68-0.69 s, band 0.70), technical rockets 0.64 s, Smerch 1.75 s and mortar_240 2.13 s (slightly over),
gunship 105 mm 0.48 s (direct band 0.45), sam_battery (Nemesis exception) 0.95 s, pt14_co_spike (documented exception, 75 kept).
Owner decision 3.

Pipeline check (canonical -> family inheritance -> variant override -> runtime -> generated):
* Python resolver (Catalog.cs replica) vs the real Sim Catalog loaded headless: 0 differences in speed, damage and splash on
  all 359 weapons, before and after.
* The Unity snapshot from the one EditMode run vs the headless runtime: 0 differences on 359 speeds and 179 unit HPs.
* Generated export: not regenerated (owner's stop); the committed pack and snapshot are stale for the changed ids.

## 5, 7, 24. Bosses

Main boss hull HP x1.08 (15 bosses), mini-boss x1.05 (18 incl. Nyx and Scylla); runtime MaxHp keeps the rank share (mini 0.55)
and toughness 0.85 on top. Part HP is a share of the hull (BossTemplates.Rank, partsShare 0.35 normalised), so parts rise with
the hull and got no extra buff: the built-boss diff shows 0 part HP or armour changes on 254 built entries (double-buff audit:
none). Nyx: outgoingDamageMult 0.8362 -> 0.9198 (x1.1000) and its Tomahawk cruise strike 400 -> 440. Scylla: 0.7389 -> 0.7980
(x1.0800), Kalibr cruise 450 -> 486 (the cruise strike is laid by NavalSystem and does not read outgoingDamageMult;
weaponDamage 1.865 / 2.195 unchanged). Mobile Fortress, Nemesis (nuke_train), Monster, Moloch, Leviathan, Kraken, Earth Borer:
damage unchanged. Boss copies of buffed aircraft guns (boss_heli_gun, boss_minigun) were pinned to their old damage.

## 6. Boss armour

Diff check: 33 raw boss entries, 254 built boss entries and parts, 33 runtime boss defs, 19 bossParts library parts: 0 armour
changes. bossFrames and bossRanks equal.

## 12. Artillery Barrage support vs scripted barrages

Lever: coverage only, blast radius 7 -> 7.7 m (count 6, damage 160, cooldown 60, scatter radius 10 unchanged). A first try at
7.35 m (+10 % area) measured only +5 %, because a hit counts out to blast + the target's hull; a sweep (7.6 / 7.7 / 7.8) picked
7.7. Scripted barrages now use the new event support `scripted_barrage` (the card's old values, event: true, no CP): the battle
event pressure barrage, the mission Barrage / AllyArtillery / enemy-strike defaults, the siege HQ barrage and the two campaign
Strike events. The AI generals' `artillery_barrage` in their decks is the card itself (unchanged id). hq_barrage untouched.

| support | 1 MBT at centre | 4 IFV formation (6 m) | 4 armoured cars spread (12 m) |
|---|---|---|---|
| artillery_barrage before (blast 7) | 684 | 2872 | 1757 |
| artillery_barrage after (blast 7.7) | 778 (+13.7 %) | 3157 (+9.9 %) | 1945 (+10.7 %) |
| scripted_barrage after | 684 (= old card) | 2872 | 1757 |
| hq_barrage before / after | 2132 / 2132 | 7718 / 7718 | 3009 / 3009 |

Mean damage over 40 seeds, undying targets; sweep files barrage_sweep_blast_*.tsv (7.6: +8.4 to +10.2 %, 7.8: +11.2 to +17.0 %).

## 13-16. Inheritance / raw-effective mismatches; APKWS; anti-ship; boss exceptions

* APKWS: own line and family row `apkws` both 85 -> 80; runtime 80 (the old 180 m/s family shadow was fixed in flight feel; no
  dead own line left). Damage 90 -> 97 (aircraft output).
* anti_ship_missile: own line and family `nsm_oniks` 95 -> 80; its two boss children had own lines (pt14_hp_nsm 90, scylla_kh35
  90) that the family change would not reach: set to 80. Runtime 80 / 80 / 80.
* Kornet: one family row `9m133_kornet` 80 -> 70 reaches tower_kornet, kornet_top, kornet_multi, kornet_twin, one_shot_kornet,
  atgm_heavy, boss_missiles and the boss copies that opt out of the family (empty weaponFamily) but inherit the resolved speed
  (p26 matriarch / roc / behemoth / bastion copies, pt14_ixion_kornet): all 70, no exception.
* Buk / Patriot / S-400 player: buk_launcher and sam_long through `9m317_buk` 120; patriot and sam_battery_lrr through
  `mim_104_patriot_pac_2` 130; sam_pac3 own line 130 (it inherits sam_battery; own line wins); sam_48n6 140.
* Boss exceptions restored (the flight-feel pass had normalised them up): sam_post 145 -> 80 (Leviathan, Typhon, the sam_medium
  part); sam_battery 165 -> 95 (user: nuke_train only); boss Grad / boss_rockets 80 -> 65 with its children (p26 behemoth /
  jotunn / nemesis copies, pt14_train_grad); pt14_ixion_grad had opted out of the Grad family and inherited 80: own line 65;
  hover_rockets (landing hovercraft) 85 -> 65. Boss cruise 65-70 unchanged.
* Guided artillery: guided rounds use their own secondRounds family rows (base + 5 m/s, splash 7): unchanged.
  howitzer_fixed_guided inherited its gun's two-layer edge, which this pass raises: pinned at 14.
* Hidden shares found and isolated: boss_heli_gun / boss_minigun inherit the buffed aircraft guns (pinned); boss_mortar shared
  the 240 mm row (own row); mlrs_rockets shared its row with the GMLRS tower (own row).

## 9-11, 18. Regression matrix (spec 18): before -> after

Headless Sim, flat range, 3 seeds; shooters vs targets that hold their fire unless "both fire"; "~" = not finished in the limit,
estimated from the damage rate (as ArmourBalanceMeasure). Fire-support and air rows use the fighting AI. Shot granularity (one
salvo more or less) makes some rows move more than the HP change.

| set | matchup | TTK before (s) | TTK after (s) | change | killed b/a | side-0 win b/a | damage dealt b/a |
|---|---|---|---|---|---|---|---|
| ground | MBT vs Heavy (front) | 69.0 | 70.2 | +2 % | 3/3 / 3/3 | 1.00 / 1.00 | 4808 / 4829 |
| ground | MBT vs Heavy (flank) | 46.5 | 46.5 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 4851 / 4851 |
| ground | Heavy vs MBT (front) | 12.9 | 12.9 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 2317 / 2433 |
| ground | MBT vs MBT (front) | 32.0 | 37.3 | +17 % | 3/3 / 3/3 | 1.00 / 1.00 | 2390 / 2427 |
| ground | MBT vs MBT duel (both fire) | ~31.9 | ~33.3 | +4 % | 1/3 / 1/3 | 0.33 / 0.33 | 2254 / 2342 |
| ground | Heavy vs TD (front) | 5.4 | 5.4 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 1637 / 1719 |
| ground | TD vs Heavy (front) | 40.8 | 44.9 | +10 % | 3/3 / 3/3 | 1.00 / 1.00 | 4474 / 4989 |
| ground | Heavy vs TD duel (both fire) | 10.2 | 10.2 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 1996 / 2095 |
| ground | TD vs Titan (front) | 97.4 | 97.4 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 7728 / 7728 |
| ground | TD vs Titan (flank) | 54.6 | 54.6 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 7990 / 7990 |
| ground | Flame Tank assault: 2 flame vs MG bunker | 30.9 | 36.3 | +17 % | 3/3 / 3/3 | 1.00 / 1.00 | 3306 / 3961 |
| ground | Flame Tank assault: 2 flame vs 2 IFV | 12.7 | 12.7 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 2743 / 2743 |
| ground | Flame Tank survives: 2 IFV vs flame tank | 7.4 | 7.7 | +4 % | 3/3 / 3/3 | 1.00 / 1.00 | 1637 / 1765 |
| ground | Breacher vs HESCO wall | 119.4 | 119.4 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 3457 / 3457 |
| ground | Breacher vs T-wall | 119.4 | 119.4 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 1296 / 1296 |
| ground | MBT vs bulldozer (breacher survival) | 32.0 | 39.5 | +23 % | 3/3 / 3/3 | 1.00 / 1.00 | 3394 / 4066 |
| ground | Railgun vs MBT (armour 4) | 17.6 | 17.6 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 2536 / 2536 |
| ground | Railgun vs Titan (armour 5) | 80.6 | 80.6 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 7904 / 7904 |
| air | SHORAD (aa_vehicle) vs attack helicopter | 119.8 | 119.7 | -0 % | 3/3 / 3/3 | 1.00 / 1.00 | 693 / 703 |
| air | SHORAD (heavy_aa) vs attack helicopter | 5.0 | 5.5 | +10 % | 3/3 / 3/3 | 1.00 / 1.00 | 1543 / 1774 |
| air | Attack helicopter vs aa_vehicle | 2.5 | 2.5 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 1112 / 1201 |
| air | SAM (sam_launcher) vs attack jet | 5.2 | 6.7 | +29 % | 3/3 / 3/3 | 1.00 / 1.00 | 1481 / 1975 |
| air | SAM (long_sam) vs attack jet | 9.8 | 9.8 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 2460 / 2460 |
| air | Fighter vs fighter (AAM) | 8.9 | 8.9 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 1630 / 1690 |
| air | Fighter vs attack helicopter (AAM) | 4.6 | 4.8 | +4 % | 3/3 / 3/3 | 1.00 / 1.00 | 1797 / 1874 |
| air | Heavy bomber survival vs long_sam | 21.7 | 26.2 | +21 % | 3/3 / 3/3 | 1.00 / 1.00 | 3731 / 4552 |
| air | Heavy bomber survival vs heavy_aa | 11.3 | 14.3 | +27 % | 3/3 / 3/3 | 1.00 / 1.00 | 3248 / 3707 |
| air | Sortie: attack jet vs 3 MBT | 14.4 | 14.3 | -1 % | 3/3 / 3/3 | 1.00 / 1.00 | 7207 / 7618 |
| air | Sortie: heavy bomber vs 4 IFV | 45.9 | 44.5 | -3 % | 3/3 / 3/3 | 1.00 / 1.00 | 6314 / 6461 |
| air | Sortie: stealth bomber vs gun turret | 2.9 | 2.9 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 5471 / 6276 |
| air | Sortie: attack helicopter vs 2 MBT | 23.4 | 22.4 | -4 % | 3/3 / 3/3 | 1.00 / 1.00 | 4662 / 4869 |
| air | Sortie: sky gunship vs 4 armoured cars | 5.8 | 5.7 | -2 % | 3/3 / 3/3 | 1.00 / 1.00 | 2715 / 2733 |
| tower | Assault squad (2 MBT + IFV) vs guard tower (small) | 9.3 | 9.3 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 2093 / 2093 |
| tower | Assault squad vs gun turret (medium) | 23.5 | 27.8 | +18 % | 3/3 / 3/3 | 1.00 / 1.00 | 4114 / 4950 |
| tower | Assault squad vs heavy turret (large) | 55.8 | 73.8 | +32 % | 3/3 / 3/3 | 1.00 / 1.00 | 6162 / 8077 |
| tower | Gun turret vs 2 MBT (tower damage) | 56.3 | 56.3 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 4947 / 5437 |
| tower | MG bunker vs 3 armoured cars (tower damage) | 24.5 | 23.4 | -4 % | 3/3 / 3/3 | 1.00 / 1.00 | 1989 / 1989 |
| tower | Gun turret vs assault squad (both fire) | ~53.0 | ~50.5 | -5 % | 0/3 / 0/3 | 0.00 / 0.00 | 2691 / 3855 |
| tower | Bomber vs gun turret (medium) | 44.9 | 44.9 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 4360 / 5126 |
| tower | Bomber vs heavy turret (large) | 59.8 | 66.4 | +11 % | 3/3 / 3/3 | 1.00 / 1.00 | 6396 / 8582 |
| tower | 2 SP howitzers vs gun turret | 28.7 | 39.0 | +36 % | 3/3 / 3/3 | 1.00 / 1.00 | 4121 / 5571 |
| tower | Thermobaric launcher vs MG bunker | 16.8 | 24.4 | +45 % | 3/3 / 3/3 | 1.00 / 1.00 | 3414 / 4041 |
| tower | Breacher (bulldozer) vs MG bunker | 22.2 | 25.3 | +14 % | 3/3 / 3/3 | 1.00 / 1.00 | 3379 / 4042 |
| tower | Attack jet bombs vs repair bay (utility) | 12.8 | 12.9 | +1 % | 3/3 / 3/3 | 1.00 / 1.00 | 3614 / 4252 |
| tower | 4 MBT + 2 SP howitzers vs HQ | 76.4 | 82.9 | +9 % | 3/3 / 3/3 | 1.00 / 1.00 | 19973 / 20901 |
| fire | 2 mortar carriers vs 4 armoured cars | 75.4 | 68.9 | -9 % | 3/3 / 3/3 | 1.00 / 1.00 | 3050 / 3052 |
| fire | AMOS (sp_mortar) vs 4 armoured cars | 68.9 | 68.9 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 3041 / 3267 |
| fire | Siege tank 240 mm vs 4 IFV | 81.8 | 70.8 | -13 % | 3/3 / 3/3 | 1.00 / 1.00 | 7322 / 6896 |
| fire | 2 SP howitzers vs 4 armoured cars (formation) | 29.9 | 29.4 | -2 % | 3/3 / 3/3 | 1.00 / 1.00 | 3541 / 3239 |
| fire | 2 SP howitzers vs 2 MBT | 46.8 | 45.7 | -2 % | 3/3 / 3/3 | 1.00 / 1.00 | 4985 / 5109 |
| fire | 2 MLRS vs 4 IFV | 70.9 | 67.4 | -5 % | 3/3 / 3/3 | 1.00 / 1.00 | 5666 / 5714 |
| fire | 2 MLRS vs 2 MBT | 55.4 | 63.0 | +14 % | 3/3 / 3/3 | 1.00 / 1.00 | 4738 / 4980 |
| fire | Elite MLRS (cluster) vs 4 armoured cars | 36.4 | 36.4 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 2821 / 2812 |
| fire | Elite Grad (cluster) vs 4 armoured cars | 45.1 | 45.2 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 2755 / 2714 |
| fire | TOS vs 4 IFV (unchanged) | 94.4 | 94.4 | +0 % | 3/3 / 3/3 | 1.00 / 1.00 | 5717 / 5717 |
| fire | Counter-battery duel: SP howitzer vs SP howitzer | ~18.2 | ~14.4 | -21 % | 1/3 / 1/3 | 0.33 / 0.33 | 942 / 826 |
| fire | Counter-battery duel: MLRS vs SP howitzer | ~13.9 | ~13.9 | +0 % | 1/3 / 1/3 | 0.33 / 0.33 | 470 / 470 |
| boss | Army vs Behemoth (main) | ~84.8 | ~98.1 | +16 % | 0/3 / 0/3 | 0.00 / 0.00 | 12236 / 11665 |
| boss | Army vs Mobile Fortress (main) | ~96.8 | ~105.9 | +9 % | 0/3 / 0/3 | 0.00 / 0.00 | 11419 / 11265 |
| boss | Army vs Fortress Bastion (main) | ~73.3 | ~80.3 | +10 % | 0/3 / 0/3 | 0.00 / 0.00 | 10424 / 10527 |
| boss | Army vs Behemoth Inferno (mini) | 41.2 | 43.0 | +4 % | 3/3 / 3/3 | 1.00 / 1.00 | 21397 / 22324 |
| boss | Army vs Behemoth Mk0 (mini) | ~32.0 | ~33.2 | +4 % | 0/3 / 0/3 | 0.00 / 0.00 | 16160 / 16370 |
| boss | Army vs Earth Borer (mini) | ~124.4 | ~127.6 | +3 % | 2/3 / 2/3 | 0.67 / 0.67 | 41857 / 43005 |

Read-out: MBT +17 % to kill (HP +5 %, one more 120 mm hit); heavy-tank duels unchanged in outcome; TD vs heavy +10 %; Titan,
IFV, light and railgun rows identical (railgun not overtuned: no reload change). Flame tank and breacher survive longer (+4 %,
+23 %); breacher vs walls identical (walls not buffed). Aircraft survive SAM / SHORAD 10-29 % longer, the bomber 21-27 %;
sorties 1-4 % faster. Towers: heavy +32 %, medium +18 %, small +0 % (overkill), HQ +9 %; tower damage +10 % (gun turret dealt
4947 -> 5437 in its window). Fire support: mortars -9 %, 240 mm -13 %, MLRS vs IFV -5 %; howitzer hit share on a moving car
0.84 -> 0.89; TOS identical. Boss TTK: main +9 to +16 %, mini +3 to +4 %.

### Boss pressure (damage to 6 undying MBTs in 60 s)

| boss | damage_to_6_undying_MBT_60s before -> after | seeds before -> after | note before -> after |
|---|---|---|---|
| behemoth | 66540 -> 67120 | 3 -> 3 |  ->  |
| mobile_fortress | 29747 -> 29747 | 3 -> 3 |  ->  |
| nuke_train | 41447 -> 41447 | 3 -> 3 |  ->  |
| nyx | 64075 -> 69308 | 3 -> 3 |  ->  |
| scylla | 68917 -> 73624 | 3 -> 3 |  ->  |
| leviathan | 60132 -> 60132 | 3 -> 3 |  ->  |
| moloch | 85764 -> 85764 | 3 -> 3 |  ->  |
| monster | 77226 -> 77465 | 3 -> 3 |  ->  |
| kraken | 139620 -> 139620 | 3 -> 3 |  ->  |
| earth_borer | 12251 -> 12251 | 3 -> 3 |  ->  |
| behemoth_inferno | 77539 -> 77539 | 3 -> 3 |  ->  |
| fortress_bastion | 37055 -> 37033 | 3 -> 3 |  ->  |

Nyx +8.2 % and Scylla +6.8 % in total: their own fire and cruise rose exactly +10 % / +8 %; the fleet missile boats they bring
are not boss output. Nemesis and Mobile Fortress identical (no pre-nerf); Behemoth +0.9 %, Monster +0.3 % (slower boss missiles
and rockets change timing only).

## 19. APS / CIWS / flare / jammer

4 undying MBTs (holding fire) under 45 s of fire with each guard; then air defence vs undying aircraft for 60 s with and without
an enemy EW jammer; then 2 Titans (vehicle APS) under guided and lobbed fire.

| fire | guard | tanks_hp_lost_45s before -> after | interceptions before -> after | diverted_rounds before -> after | shots_fired before -> after |
|---|---|---|---|---|---|
| direct (ATGM, heli, FPV) | none | 28678 -> 30034 | 0.0 -> 0.0 | 0.0 -> 0.0 | 446.3 -> 445.0 |
| direct (ATGM, heli, FPV) | c_ram | 10940 -> 12095 | 73.3 -> 72.3 | 0.0 -> 0.0 | 291.0 -> 289.7 |
| direct (ATGM, heli, FPV) | c_ram.centurion | 7202 -> 7086 | 81.0 -> 83.7 | 0.0 -> 0.0 | 303.0 -> 303.3 |
| direct (ATGM, heli, FPV) | c_ram.dome | 21095 -> 21738 | 16.0 -> 16.0 | 0.0 -> 0.0 | 339.7 -> 349.3 |
| direct (ATGM, heli, FPV) | iron_beam | 7635 -> 8031 | 33.3 -> 33.3 | 0.0 -> 0.0 | 1111.0 -> 1108.3 |
| direct (ATGM, heli, FPV) | aa_vehicle | 24892 -> 25484 | 0.0 -> 0.0 | 0.3 -> 0.3 | 380.0 -> 387.7 |
| direct (ATGM, heli, FPV) | laser_ad_station | 17378 -> 17501 | 44.0 -> 44.0 | 0.0 -> 0.0 | 291.7 -> 292.0 |
| lobbed (MLRS, howitzer, mortar, Shahed) | none | 6497 -> 6565 | 0.0 -> 0.0 | 0.0 -> 0.0 | 31.0 -> 31.0 |
| lobbed (MLRS, howitzer, mortar, Shahed) | c_ram | 423 -> 567 | 27.0 -> 27.0 | 0.0 -> 0.0 | 30.3 -> 30.3 |
| lobbed (MLRS, howitzer, mortar, Shahed) | c_ram.centurion | 461 -> 567 | 27.0 -> 27.0 | 0.0 -> 0.0 | 30.7 -> 30.7 |
| lobbed (MLRS, howitzer, mortar, Shahed) | c_ram.dome | 557 -> 882 | 12.7 -> 12.7 | 0.0 -> 0.0 | 30.7 -> 30.7 |
| lobbed (MLRS, howitzer, mortar, Shahed) | iron_beam | 393 -> 499 | 12.3 -> 12.3 | 0.0 -> 0.0 | 31.0 -> 31.0 |
| lobbed (MLRS, howitzer, mortar, Shahed) | aa_vehicle | 6497 -> 6565 | 0.0 -> 0.0 | 0.0 -> 0.0 | 31.0 -> 31.0 |
| lobbed (MLRS, howitzer, mortar, Shahed) | laser_ad_station | 393 -> 499 | 12.3 -> 12.3 | 0.0 -> 0.0 | 31.0 -> 31.0 |
| guided missiles (2 IFV TOW, light tank GL-ATGM, strike drone Hellfire) | none | 5992 -> 6284 | 0.0 -> 0.0 | 0.0 -> 0.0 | 31.0 -> 31.0 |
| guided missiles (2 IFV TOW, light tank GL-ATGM, strike drone Hellfire) | c_ram | 3483 -> 3632 | 8.7 -> 9.0 | 0.0 -> 0.0 | 31.0 -> 31.0 |
| guided missiles (2 IFV TOW, light tank GL-ATGM, strike drone Hellfire) | c_ram.centurion | 3483 -> 3632 | 8.7 -> 9.0 | 0.0 -> 0.0 | 31.0 -> 31.0 |
| guided missiles (2 IFV TOW, light tank GL-ATGM, strike drone Hellfire) | c_ram.dome | 6706 -> 6998 | 0.0 -> 0.0 | 0.0 -> 0.0 | 31.0 -> 31.0 |
| guided missiles (2 IFV TOW, light tank GL-ATGM, strike drone Hellfire) | iron_beam | 2217 -> 2366 | 11.0 -> 11.3 | 0.0 -> 0.0 | 131.0 -> 131.0 |
| guided missiles (2 IFV TOW, light tank GL-ATGM, strike drone Hellfire) | aa_vehicle | 6992 -> 7284 | 0.0 -> 0.0 | 0.0 -> 0.0 | 31.0 -> 31.0 |
| guided missiles (2 IFV TOW, light tank GL-ATGM, strike drone Hellfire) | laser_ad_station | 2769 -> 3061 | 10.7 -> 10.7 | 0.0 -> 0.0 | 31.0 -> 31.0 |

| air_defence | target | damage_60s before -> after | hits before -> after | diverted before -> after | shots before -> after |
|---|---|---|---|---|---|
| sam_launcher | attack_helicopter | 15306 -> 15306 | 31.0 -> 31.0 | 0.0 -> 0.0 | 36.0 -> 36.0 |
| sam_launcher (+enemy ew_jammer) | attack_helicopter | 123 -> 123 | 1.0 -> 1.0 | 0.0 -> 0.0 | 36.0 -> 36.0 |
| sam_launcher | attack_jet | 11685 -> 11685 | 23.7 -> 23.7 | 0.0 -> 0.0 | 26.0 -> 26.0 |
| sam_launcher (+enemy ew_jammer) | attack_jet | 8270 -> 8270 | 17.0 -> 17.0 | 0.0 -> 0.0 | 26.0 -> 26.0 |
| long_sam | attack_jet | 7935 -> 7935 | 7.0 -> 7.0 | 0.0 -> 0.0 | 7.0 -> 7.0 |
| long_sam (+enemy ew_jammer) | attack_jet | 3055 -> 3055 | 5.7 -> 5.7 | 0.0 -> 0.0 | 7.0 -> 7.0 |
| aa_vehicle | attack_helicopter | 4747 -> 4811 | 78.0 -> 81.7 | 0.3 -> 0.3 | 79.0 -> 82.7 |
| aa_vehicle (+enemy ew_jammer) | attack_helicopter | 96 -> 115 | 1.7 -> 2.0 | 0.0 -> 0.0 | 171.3 -> 173.3 |
| manpads_tower | attack_helicopter | 2678 -> 2678 | 9.3 -> 9.3 | 0.7 -> 0.7 | 10.7 -> 10.7 |
| manpads_tower (+enemy ew_jammer) | attack_helicopter | 0 -> 0 | 0.0 -> 0.0 | 0.0 -> 0.0 | 14.0 -> 14.0 |
| missile_battery | heavy_bomber | 12018 -> 11766 | 26.7 -> 26.7 | 0.0 -> 0.0 | 28.0 -> 28.0 |
| missile_battery (+enemy ew_jammer) | heavy_bomber | 9930 -> 9723 | 25.0 -> 24.7 | 0.0 -> 0.0 | 28.0 -> 28.0 |
| heavy_aa | fighter_jet | 12829 -> 12946 | 669.0 -> 669.7 | 0.0 -> 0.0 | 682.3 -> 682.3 |
| heavy_aa (+enemy ew_jammer) | fighter_jet | 3092 -> 3052 | 217.0 -> 216.3 | 0.0 -> 0.0 | 928.0 -> 927.7 |
| fighter_jet | attack_helicopter | 24718 -> 24718 | 458.7 -> 458.7 | 0.7 -> 0.7 | 459.3 -> 459.3 |
| fighter_jet (+enemy ew_jammer) | attack_helicopter | 14525 -> 14525 | 437.7 -> 437.7 | 0.0 -> 0.0 | 458.7 -> 458.7 |

| aps_target | attackers | hp_lost_45s before -> after | aps_interceptions before -> after | shots before -> after |
|---|---|---|---|---|
| titan_tank x2 | ATGM / missile | 16926 -> 17724 | 15.0 -> 15.3 | 647.7 -> 648.7 |
| titan_tank x2 | rockets / lobbed | 4502 -> 4607 | 0.0 -> 0.0 | 57.0 -> 57.0 |

| shooter | moving_target | shots before -> after | hits before -> after | hit_share before -> after | damage_60s before -> after |
|---|---|---|---|---|---|
| main_battle_tank | armored_car | 294.3 -> 294.3 | 286.7 -> 286.7 | 0.97 -> 0.97 | 6165 -> 6165 |
| ifv | main_battle_tank | 333.3 -> 333.3 | 333.3 -> 333.3 | 1.00 -> 1.00 | 7597 -> 7597 |
| tank_destroyer | armored_car | 12.0 -> 12.0 | 12.0 -> 12.0 | 1.00 -> 1.00 | 6204 -> 6204 |
| light_tank | main_battle_tank | 114.0 -> 114.0 | 113.7 -> 113.7 | 1.00 -> 1.00 | 2966 -> 2966 |
| aa_vehicle | attack_helicopter | 181.3 -> 182.0 | 180.3 -> 180.0 | 0.99 -> 0.99 | 8857 -> 8651 |
| sam_launcher | attack_helicopter | 36.0 -> 36.0 | 32.0 -> 32.0 | 0.89 -> 0.89 | 15676 -> 15676 |
| heavy_aa | attack_helicopter | 1396.7 -> 1377.3 | 1391.7 -> 1372.7 | 1.00 -> 1.00 | 20257 -> 20365 |
| atgm_tower | main_battle_tank | 22.0 -> 22.0 | 21.0 -> 21.0 | 0.95 -> 0.95 | 7535 -> 8288 |
| artillery | armored_car | 6.3 -> 6.3 | 5.3 -> 5.7 | 0.84 -> 0.89 | 2319 -> 2399 |
| mortar_carrier | armored_car | 9.0 -> 9.0 | 7.3 -> 7.3 | 0.81 -> 0.81 | 1320 -> 1449 |
| mlrs | ifv | 25.0 -> 25.0 | 25.0 -> 25.0 | 1.00 -> 1.00 | 2690 -> 2712 |

Result: interceptions move by at most +2.7 a run (C-RAM 73.3 -> 72.3, Centurion 81.0 -> 83.7, Dome 16 = 16, Iron Beam 33.3 =
33.3, laser 44 = 44; against the slower guided missiles C-RAM 8.7 -> 9.0, Iron Beam 11.0 -> 11.3; Titan APS 15.0 -> 15.3). HP
lost rises where the attackers were buffed (attack helicopter, mortar, MLRS coverage), not from point defence losing reach.
SAM / jammer / flare rows are identical (speeds 145 -> 120, 165 -> 130 change no hit or decoy outcome in 60 s; flare decoys
are rare in these set-ups, 0.3-0.7 a run, unchanged). APS / CIWS not pre-nerfed; no change needed.

## 20. AI lead / intercept

The second block of the APS table: crossing targets (back and forth across the shooter's front, 60 s), hit share before ->
after: MBT 0.97 = 0.97, IFV TOW 1.00 = 1.00, ATGM tower 0.95 = 0.95, sam_launcher 0.89 = 0.89, howitzer 0.84 -> 0.89 (splash),
mortar 0.81 = 0.81, MLRS 1.00 = 1.00. CombatSystem.LeadPoint uses the arm's effective speed (gear included) capped by
FixRules.LeadCap 3 s, which covers the longest new flight (Smerch 1.75 s, 240 mm 2.1 s); BossSystem.MaxLead 2.5 s unchanged.
No fix needed.

## 21. Warning + travel reaction window

Ordinary fire has no warning ring (warningRules.normalFire false): its reaction window is the flight itself (flight table:
tactical missiles 0.5-0.8 s at reach, Patriot 0.69 s, S-400 0.68 s, boss rockets 0.69 s, mortars 1.2-2.1 s). Boss warned
rounds (T4+): travel = max(flight, warn seconds), so the window is the warning (2.5-6 s); no warned boss round changed speed
(122 mm boss rockets do not warn; boss mortar / howitzer speeds unchanged). Derived: 240 mm warn seconds 2.5 -> 2.72 s (bigger
splash), relevant only if a 240 mm round is warned. Big attacks (warn 3-4 s) unchanged.

## 22. Structure repair throughput

Every repair path is a share of max HP a second (engineer aura repair.rate 0.025, x0.5 on structures; sapper fortify aura;
repair_drop / field_repair shares; HQ shield regen; crate repair; boss-hunt rest): repaired HP a second rises with max HP, so
the time to full is unchanged. No repair change (spec: keep when % of max HP).

## 23. Fire-support resupply

| platform | weapon | ammo (rounds/mag) | cycle per mag (s) | magazine reload (s) | reload share of time | sustained dmg/s on paper | beside an ammo carrier (reload x3 faster) |
|---|---|---|---|---|---|---|---|
| mortar_carrier | mortar_120 | 18 | 128.6 | 35.7 | 22 % | 25.7 | 30.1 (+17 %) |
| sp_mortar | amos_120 | unlimited | 15.36 | - | 0 % | 61.2 | no effect |
| siege_tank | siege_mortar_240 | 10 | 108.8 | 28.6 | 21 % | 46.8 | 54.3 (+16 %) |
| artillery | howitzer | 20 | 204.1 | 33.5 | 14 % | 38.5 | 42.5 (+10 %) |
| mlrs | mlrs_rockets | 4 | 44.6 | 15.5 | 26 % | 33.3 | 40.2 (+21 %) |
| elite_mlrs | mlrs_elite | 6 | 61.5 | 19.9 | 24 % | 38.7 | 46.2 (+20 %) |
| elite_grad | grad_cluster | 3 | 39.0 | 13.7 | 26 % | 35.7 | 43.2 (+21 %) |
| heavy_rocket_artillery | rockets_300mm | 3 | 54.8 | 18.9 | 26 % | 64.9 | 78.3 (+21 %) |
| thermobaric_launcher | thermobaric_rockets | 4 | 51.8 | 21.7 | 29 % | 47.5 | 59.2 (+24 %) |
| rocket_technical | technical_rockets | 6 | 45.6 | 18.0 | 28 % | 23.3 | 28.8 (+23 %) |
| ballistic_launcher | ballistic_missile | 2 | 48.4 | 18.2 | 27 % | 37.8 | 46.3 (+22 %) |
| ground_cruise_missile_vehicle | cruise_missile_ground | unlimited | 45.0 | - | 0 % | 20.0 | no effect |

There is no finite stock: an empty magazine reloads in place; an ammunition carrier tops up part-empty magazines and makes the
in-place reload 3x faster (+10 to +24 % sustained). Supply is not genuinely limiting: no resupply buff, no magazine change.
Counter-battery: no damage multiplier added (duel rows above). Fire-support platform HP unchanged.

Tower rebuild economy (spec 17): rebuild CP and cooldown unchanged (base.rebuild equal). Large towers last about 30 % longer
under assault (heavy turret TTK +32 %), in line with +30 % HP; no regression failure, so no rebuild-time change.

## 25. Regenerated outputs

Skipped by owner (06/10 update: no export.py run, no snapshot refresh, no export stale-value scan, no CHANGES.md entry).
Docs/export/current and Docs/export/game_snapshot.json are as before this pass and stale for the ids above until the next pack
rebuild (Unity ExportGameDoc, then export.py). Written instead: this report, Docs/balance/balance_final_changes.json and
Docs/balance/balance_final/ (measurements, flight table, audits).

## 26. Stale-data scan

Export scan skipped by owner (see 25). Scans done: own projectileSpeed line vs family row: 0 dead values; raw vs runtime > 25 %:
0; Python resolver vs runtime: 0 differences; keep-list fields (Pen, cooldown, reload, clip, burst, ammo, range, minRange on
every weapon; armour, CP, rebuildCp, rearm, APS, flares, jammer, repair / rearm auras on every vehicle): 0 changes
(Docs/balance/balance_final/audit.txt). Stale until the pack rebuild: Docs/export/current 01-04, 09 and game_snapshot.json
(weaponFlight speeds, unit HP, tower multipliers, boss HP, supports).

## Final confirmation

* Boss armour unchanged (0 changes on 33 bosses, 254 built entries, 19 parts).
* Cruise stays ~65-70 m/s (jassm 70, air_cruise_missile 65, cruise_missile_ground 70, leviathan_cruise 70, nyx_tomahawk 70, hydra_club_s 70).
* Hellfire = 70 m/s.
* Kornet family = 70 m/s, no exception.
* Anti-ship missile = 80 m/s.
* Player Buk = 120 m/s.
* Player Patriot = 130 m/s.
* S-400 = 140 m/s.
* Boss/ship sam_post = 80 m/s.
* Nemesis sam_battery = 95 m/s.
* Boss Grad/rockets = 65 m/s.
* Bomb buffs applied by payload class without global rearm reduction (rearmTime untouched).
* Aircraft buffed mainly through HP and modest ground-attack output (x1.08), not armour inflation (armour untouched).
* MBT/Heavy buffs kept conservative (MBT HP +5 %; heavy HP +8 %, damage +5 %).
* Titan not buffed.
* Towers gained more durability than DPS (HP +15 to +30 %, damage +8 to +10 %, AA / SAM / PD damage kept).
* Walls not buffed.
* Shield body buffed (+10 %) without also buffing the dome / ward pool (base.hqTypes and shield data unchanged).
* Main boss HP +8 %; mini-boss HP +5 %.
* Nyx damage +10 %; Scylla +8 %.
* Nemesis not pre-nerfed.
* 120 mm mortar damage +10 % (214 -> 235; AMOS 214 -> 235).
* 240 mm mortar damage unchanged; splash 9 -> 10 m.
* Howitzer raw damage unchanged; coverage about +10 % (7 -> 7.7 m).
* MLRS raw damage unchanged; coverage increased (4.5 -> 4.9 m; cluster radius +10 %).
* TOS combat stats unchanged.
* Fire-support vehicles did not receive blanket HP buffs.
* Artillery Barrage gained ~10 % total strike value without unintentionally buffing unrelated scripted barrages.
* Generated outputs: not regenerated (skipped by owner); canonical source and runtime verified instead.

## Open owner decisions

1. Unlisted units kept as they were: coastal_battery, bunker_shelter_tower, wheeled_gun (also blast_wall, bulwark_post).
2. The cluster-bomb rule has no aircraft target: apply it to the consumable cluster_strike (and conventional x1.25 to airstrike)?
3. Accept the 25 validator flags (spec speeds at short ranges) or set per-weapon exceptions / ranges.
4. When to rebuild the export pack (Unity ExportGameDoc + export.py) so the docs match.
