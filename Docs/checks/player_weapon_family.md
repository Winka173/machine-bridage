# Player weapon families: the deviations (prompt 34 L1)

Written by `Tools/balance/p34_families.py`. Prompt 34 does not change player weapons. This list shows where weapons
of the same family and variant differ in damage per round, round speed, blast (core / edge) or damage type. The
boss table (L2) is a different scale (boss damage), so it is shown for reference only. Fix later, after prompt 29
and the replacement-round balance.

A row is the family (and variant), the field that differs, then each value with the weapons that have it.
19 families with deviations.


- **atgm_agm_114_hellfire**, T2: 3 weapons
  - splash: 0 (drone_missile, heli_atgm); 2 (uav_loiter_missile)
- **cal_100_105_ap**, T2: 4 weapons
  - damage: 200 (at_gun_100); 212 (gun_105_ags, gun_105_bunker, siege_gun_105)
  - projectileSpeed: 190 (gun_105_ags, gun_105_bunker, siege_gun_105); 200 (at_gun_100)
  - splash: 0 (at_gun_100, gun_105_ags); 1.5 (gun_105_bunker, siege_gun_105)
- **cal_100_105_he**, T2 (boss table: 300 a round): 3 weapons
  - damage: 160 (gun_100_river); 200 (gun_100_2a70, gunship_105)
  - projectileSpeed: 120 (gun_100_2a70, gunship_105); 170 (gun_100_river)
  - splash: 3 (gun_100_2a70); 4 (gun_100_river); 5.5 (gunship_105)
- **cal_120_ap**, T3 (boss table: 260 a round): 5 weapons
  - damage: 240 (gun_120_twin, gun_120mm, turret_gun_120, turret_gun_120_long); 258 (gun_105_wheeled)
  - projectileSpeed: 170 (gun_120_twin, gun_120mm, turret_gun_120, turret_gun_120_long); 230 (gun_105_wheeled)
  - splash: 0 (gun_105_wheeled); 1.5 (gun_120_twin, gun_120mm, turret_gun_120, turret_gun_120_long)
- **cal_125_ap**, T3 (boss table: 400 a round): 4 weapons
  - projectileSpeed: 190 (gun_125_elite); 210 (gun_125_armata_ke); 220 (gun_105_long); 260 (gun_105_apfsds)
  - splash: 0 (gun_105_apfsds, gun_105_long, gun_125_armata_ke); 1.5 (gun_125_elite)
- **cal_12_7**, T0 (boss table: 15 a round): 10 weapons
  - projectileSpeed: 230 (hmg_roof, hmg_selfdef_15, hmg_selfdef_18, hmg_selfdef_21, mg_jeep, mg_jeep_selfdef, tower_hmg); 240 (bomber_tail_guns, bunker_hmg, bunker_hmg_twin)
- **cal_152_155**, T3 (boss table: 600 a round): 8 weapons
  - projectileSpeed: 150 (gun_155_coastal, gun_155_crusader, gun_155_twin_coastlr, gun_behemoth); 45 (caesar_155, howitzer, howitzer_cb, howitzer_fixed)
  - splash: 6 (gun_155_crusader); 6.5 (gun_behemoth); 7 (caesar_155, gun_155_coastal, gun_155_twin_coastlr, howitzer, howitzer_cb, howitzer_fixed)
- **cal_152_155 / ap**, T3 (boss table: 600 a round): 3 weapons
  - damage: 300 (gun_155_twin_ap); 320 (bastion_gun, gun_152)
  - projectileSpeed: 150 (gun_155_twin_ap); 160 (bastion_gun, gun_152)
  - splash: 0 (gun_155_twin_ap); 2.5 (bastion_gun, gun_152)
- **cal_23**, T1 (boss table: 7 a round): 2 weapons
  - damage: 14 (flak_quad); 7 (zu23)
  - projectileSpeed: 240 (zu23); 300 (flak_quad)
  - splash: 0 (zu23); 3.5 (flak_quad)
- **cal_25**, T1: 3 weapons
  - projectileSpeed: 210 (autocannon_25, tower_ac25); 280 (gunship_25mm)
- **cal_30**, T1 (boss table: 22 a round): 7 weapons
  - damage: 12 (hover_ciws); 22 (autocannon_30, heli_gun, ifv_30, twin_30_bmpt); 23 (gsh30k, jet_cannon)
  - projectileSpeed: 200 (autocannon_30, ifv_30, twin_30_bmpt); 220 (heli_gun); 300 (gsh30k, hover_ciws, jet_cannon)
- **cal_30 / flak**, T1 (boss table: 22 a round): 3 weapons
  - damage: 7 (tower_flak_30); 7.5 (hq_flak, twin_30_flak)
- **cal_35**, T1 (boss table: 25 a round): 3 weapons
  - damage: 25 (boss_flak); 26 (flak_35, twin_35_ahead)
  - projectileSpeed: 260 (boss_flak, flak_35); 300 (twin_35_ahead)
  - splash: 2.5 (boss_flak, flak_35); 4 (twin_35_ahead)
- **cal_57 / ap**, T2 (boss table: 120 a round): 2 weapons
  - damage: 70 (gun_57_auto); 77 (gun_57mm)
  - projectileSpeed: 150 (gun_57mm); 260 (gun_57_auto)
  - splash: 0 (gun_57mm); 1.5 (gun_57_auto)
- **cal_7_62**, T0: 4 weapons
  - projectileSpeed: 220 (door_gun); 240 (mg_coax, mg_coax_ground, minigun)
- **flame_flamethrower**, T1: 2 weapons
  - damage: 21 (flamethrower); 26 (bunker_flame)
  - splash: 2.5 (flamethrower); 4.5 (bunker_flame)
- **rkt_70_80**, T2: 5 weapons
  - damage: 30 (heli_rockets, scout_rockets); 32 (boat_rockets, gunship_rockets, s8_pods)
- **rkt_gmlrs_227**, T4: 2 weapons
  - damage: 100 (mlrs_rockets); 160 (turret_gmlrs)
- **sam_fim_92_stinger**, T2: 2 weapons
  - damage: 170 (stinger_post); 178 (stinger_atas)
  - splash: 1.5 (stinger_atas); 2 (stinger_post)

## Weapons that bosses and player vehicles share

Prompt 34 L2 changes boss weapons only. Where a boss carries a player's weapon and the boss table changes
its numbers, L2 gives the boss its own copy. These weapons are shared:

`air_to_air`, `boss_flak`, `fighter_cannon`, `guided_bomb`, `gunship_105`, `gunship_25mm`, `gunship_40mm`, `gunship_rockets`, `hover_ciws`, `zu23`
