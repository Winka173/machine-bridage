# Stuck report: before

- Battles: 76; stuck episodes of 8 s or more: 2076; over 10 s: 1285; safety-net activations: 0.
- Simulated: 656 min of battle (386 s to run).

## By cause (8 s+ / over 10 s)

| cause | 8 s+ | over 10 s | seconds | 
|---|---|---|---|
| BlockedByFriend | 789 | 395 | 8684 |
| YieldWait | 578 | 418 | 7665 |
| OffRoute | 178 | 128 | 2359 |
| NoPath | 176 | 153 | 4696 |
| StalePath | 119 | 74 | 1380 |
| Unknown | 83 | 17 | 762 |
| BlockedByDefence | 60 | 34 | 670 |
| GateWait | 44 | 30 | 560 |
| Embedded | 38 | 33 | 744 |
| BlockedByObstacle | 10 | 3 | 98 |
| BlockedByEnemy | 1 | 0 | 9 |

## By mode (8 s+ / over 10 s)

| mode | 8 s+ | over 10 s |
|---|---|---|
| Siege | 576 | 329 |
| Endless | 516 | 331 |
| Defend | 512 | 322 |
| Weekly | 472 | 303 |

## By place (8 s+ / over 10 s)

| place | 8 s+ | over 10 s |
|---|---|---|
| fortress | 1141 | 689 |
| fortress+gate | 540 | 383 |
| field | 193 | 94 |
| camp0 | 75 | 30 |
| field+gate | 64 | 44 |
| camp1 | 59 | 43 |
| camp1+gate | 4 | 2 |

## By vehicle (8 s+ / over 10 s)

| vehicle | 8 s+ | over 10 s |
|---|---|---|
| aa_vehicle | 256 | 166 |
| siege_tank | 253 | 134 |
| main_battle_tank | 180 | 116 |
| scout_jeep | 161 | 109 |
| heavy_tank | 146 | 91 |
| titan_tank | 143 | 83 |
| armored_car | 114 | 77 |
| ifv | 104 | 62 |
| light_tank | 67 | 40 |
| elite_heavy_tank | 63 | 37 |
| armored_bulldozer | 60 | 32 |
| counter_battery_radar | 56 | 30 |
| rocket_technical | 46 | 31 |
| command_vehicle | 46 | 25 |
| thermobaric_launcher | 36 | 21 |
| vbied | 33 | 30 |
| twin_tank | 32 | 24 |
| flame_tank | 30 | 23 |
| artillery | 27 | 13 |
| sapper | 23 | 17 |
| mine_layer | 19 | 12 |
| engineer_vehicle | 18 | 11 |
| smoke_carrier | 18 | 13 |
| sam_launcher | 16 | 11 |
| wheeled_gun | 15 | 7 |

## By battlefield (8 s+ / over 10 s)

| battlefield | 8 s+ | over 10 s |
|---|---|---|
| capital | 431 | 304 |
| redrock | 357 | 235 |
| metrocity | 294 | 182 |
| junglepass | 226 | 138 |
| swamp | 187 | 119 |
| ashfield | 183 | 93 |
| ironport | 141 | 77 |
| coralisles | 59 | 34 |
| hydrodam | 27 | 22 |
| whiteout | 24 | 10 |
| landingbeach | 23 | 13 |
| rustyard | 23 | 10 |
| greenvale | 21 | 13 |
| launchsite | 20 | 9 |
| emberridge | 12 | 8 |
| skyhold | 11 | 7 |
| dunebreak | 11 | 3 |
| borderbridge | 10 | 5 |
| frostpeak | 9 | 1 |
| saltflat | 7 | 2 |

## By loadout (8 s+ / over 10 s)

| loadout | 8 s+ | over 10 s |
|---|---|---|
| obstacles | 933 | 601 |
| full | 857 | 539 |
| light | 286 | 145 |

## Battles

| mode | map | seed | loadout | minutes | result | 8 s+ | over 10 s | worst s | rescues |
|---|---|---|---|---|---|---|---|---|---|
| Defend | ashfield | 1 | full | 9.0 | won | 52 | 27 | 20 | 0 |
| Defend | ashfield | 2 | obstacles | 9.0 | won | 29 | 16 | 19 | 0 |
| Endless | ashfield | 1 | obstacles | 10.0 | open | 42 | 18 | 18 | 0 |
| Endless | ashfield | 2 | light | 6.4 | lost | 5 | 4 | 11 | 0 |
| Weekly | ashfield | 1 | light | 10.0 | open | 12 | 8 | 16 | 0 |
| Weekly | ashfield | 2 | full | 10.0 | open | 20 | 10 | 17 | 0 |
| Defend | ironport | 1 | obstacles | 9.0 | won | 28 | 17 | 22 | 0 |
| Defend | ironport | 2 | light | 6.3 | lost | 22 | 7 | 15 | 0 |
| Endless | ironport | 1 | light | 5.4 | lost | 17 | 11 | 18 | 0 |
| Endless | ironport | 2 | full | 10.0 | open | 23 | 13 | 30 | 0 |
| Weekly | ironport | 1 | full | 9.1 | lost | 11 | 6 | 12 | 0 |
| Weekly | ironport | 2 | obstacles | 9.0 | lost | 18 | 9 | 28 | 0 |
| Defend | metrocity | 1 | light | 4.7 | lost | 28 | 16 | 16 | 0 |
| Defend | metrocity | 2 | full | 10.0 | open | 69 | 45 | 51 | 0 |
| Endless | metrocity | 1 | full | 10.0 | open | 37 | 23 | 37 | 0 |
| Endless | metrocity | 2 | obstacles | 10.0 | open | 65 | 46 | 70 | 0 |
| Weekly | metrocity | 1 | obstacles | 10.0 | open | 62 | 37 | 66 | 0 |
| Weekly | metrocity | 2 | light | 6.6 | won | 20 | 12 | 15 | 0 |
| Defend | redrock | 1 | full | 9.0 | won | 48 | 35 | 33 | 0 |
| Defend | redrock | 2 | obstacles | 10.0 | open | 92 | 65 | 27 | 0 |
| Endless | redrock | 1 | obstacles | 10.0 | open | 67 | 41 | 37 | 0 |
| Endless | redrock | 2 | light | 6.3 | lost | 12 | 6 | 11 | 0 |
| Weekly | redrock | 1 | light | 10.0 | open | 27 | 9 | 17 | 0 |
| Weekly | redrock | 2 | full | 10.0 | open | 99 | 70 | 61 | 0 |
| Defend | junglepass | 1 | obstacles | 9.0 | won | 61 | 41 | 28 | 0 |
| Defend | junglepass | 2 | light | 7.1 | lost | 10 | 4 | 13 | 0 |
| Endless | junglepass | 1 | light | 6.7 | lost | 27 | 12 | 24 | 0 |
| Endless | junglepass | 2 | full | 10.0 | open | 35 | 21 | 18 | 0 |
| Weekly | junglepass | 1 | full | 10.0 | open | 32 | 17 | 33 | 0 |
| Weekly | junglepass | 2 | obstacles | 9.0 | lost | 40 | 32 | 215 | 0 |
| Defend | capital | 1 | light | 5.2 | lost | 7 | 2 | 17 | 0 |
| Defend | capital | 2 | full | 10.0 | open | 66 | 47 | 83 | 0 |
| Endless | capital | 1 | full | 10.0 | open | 123 | 90 | 41 | 0 |
| Endless | capital | 2 | obstacles | 10.0 | open | 63 | 46 | 55 | 0 |
| Weekly | capital | 1 | obstacles | 10.0 | open | 89 | 68 | 68 | 0 |
| Weekly | capital | 2 | light | 10.0 | open | 42 | 25 | 21 | 0 |
| Siege | ashfield | 1 | full | 10.6 | won | 12 | 4 | 19 | 0 |
| Siege | ashfield | 2 | obstacles | 8.9 | won | 11 | 6 | 22 | 0 |
| Siege | dunebreak | 1 | obstacles | 13.5 | won | 11 | 3 | 21 | 0 |
| Siege | dunebreak | 2 | light | 3.5 | won | 0 | 0 | 0 | 0 |
| Siege | frostpeak | 1 | light | 3.7 | won | 4 | 1 | 11 | 0 |
| Siege | frostpeak | 2 | full | 9.1 | won | 5 | 0 | 10 | 0 |
| Siege | ironport | 1 | full | 6.3 | won | 5 | 3 | 11 | 0 |
| Siege | ironport | 2 | obstacles | 10.6 | won | 17 | 11 | 18 | 0 |
| Siege | redrock | 1 | obstacles | 12.7 | won | 12 | 9 | 26 | 0 |
| Siege | redrock | 2 | light | 3.1 | won | 0 | 0 | 0 | 0 |
| Siege | whiteout | 1 | light | 4.2 | won | 3 | 1 | 10 | 0 |
| Siege | whiteout | 2 | full | 13.3 | won | 21 | 9 | 51 | 0 |
| Siege | greenvale | 1 | full | 6.0 | won | 7 | 4 | 21 | 0 |
| Siege | greenvale | 2 | obstacles | 8.6 | won | 14 | 9 | 18 | 0 |
| Siege | rustyard | 1 | obstacles | 11.3 | won | 20 | 9 | 22 | 0 |
| Siege | rustyard | 2 | light | 3.4 | won | 3 | 1 | 11 | 0 |
| Siege | emberridge | 1 | light | 2.9 | won | 0 | 0 | 0 | 0 |
| Siege | emberridge | 2 | full | 14.0 | open | 12 | 8 | 56 | 0 |
| Siege | junglepass | 1 | full | 8.1 | won | 13 | 7 | 19 | 0 |
| Siege | junglepass | 2 | obstacles | 10.3 | won | 8 | 4 | 26 | 0 |
| Siege | skyhold | 1 | obstacles | 6.1 | won | 10 | 7 | 16 | 0 |
| Siege | skyhold | 2 | light | 3.1 | won | 1 | 0 | 9 | 0 |
| Siege | metrocity | 1 | light | 3.2 | won | 2 | 0 | 10 | 0 |
| Siege | metrocity | 2 | full | 7.2 | won | 11 | 3 | 17 | 0 |
| Siege | landingbeach | 1 | full | 5.0 | won | 2 | 2 | 11 | 0 |
| Siege | landingbeach | 2 | obstacles | 9.4 | won | 21 | 11 | 55 | 0 |
| Siege | hydrodam | 1 | obstacles | 8.7 | won | 19 | 16 | 23 | 0 |
| Siege | hydrodam | 2 | light | 10.4 | won | 8 | 6 | 19 | 0 |
| Siege | capital | 1 | light | 5.7 | won | 2 | 0 | 9 | 0 |
| Siege | capital | 2 | full | 14.0 | open | 39 | 26 | 26 | 0 |
| Siege | launchsite | 1 | full | 6.1 | won | 4 | 2 | 12 | 0 |
| Siege | launchsite | 2 | obstacles | 14.0 | open | 16 | 7 | 20 | 0 |
| Siege | saltflat | 1 | obstacles | 11.0 | won | 7 | 2 | 45 | 0 |
| Siege | saltflat | 2 | light | 3.4 | won | 0 | 0 | 0 | 0 |
| Siege | borderbridge | 1 | light | 3.9 | won | 0 | 0 | 0 | 0 |
| Siege | borderbridge | 2 | full | 11.8 | won | 10 | 5 | 55 | 0 |
| Siege | swamp | 1 | full | 14.0 | lost | 101 | 62 | 115 | 0 |
| Siege | swamp | 2 | obstacles | 14.0 | open | 86 | 57 | 140 | 0 |
| Siege | coralisles | 1 | obstacles | 10.4 | won | 25 | 14 | 55 | 0 |
| Siege | coralisles | 2 | light | 14.0 | open | 34 | 20 | 67 | 0 |

## The ten worst spots (top10.png)

1. **capital (50, 121)**: 72 stuck, 1108 s; YieldWait 34, BlockedByFriend 14, Embedded 10, StalePath 8, OffRoute 4, Unknown 1, GateWait 1; worst: main_battle_tank #1086 (Endless seed 2 obstacles, from 543 s for 54 s, Embedded: on drone_hangar(defence); near light_tank(moving)@9.9 aa_vehicle(parked)@4.0 armored_car(moving)@4.2 aa_vehicle(moving)@3.2 ifv(moving)@10.0 aa_vehicle(moving)@6.3 light_tank(moving)@8.9 sieg)
2. **redrock (50, 121)**: 58 stuck, 850 s; YieldWait 28, OffRoute 15, BlockedByFriend 12, StalePath 2, Unknown 1; worst: titan_tank #773 (Endless seed 1 obstacles, from 408 s for 36 s, OffRoute: to (69.0;121.0) past shield_generator; near aa_vehicle(moving)@7.7 ifv(moving)@5.0 aa_vehicle(moving)@9.1 aa_vehicle(moving)@6.0 ifv(moving)@5.5 shield_generator@6 garage@10 floodlight_mast@10)
3. **capital (47, 132)**: 58 stuck, 820 s; YieldWait 32, BlockedByFriend 14, OffRoute 8, StalePath 4; worst: titan_tank #950 (Endless seed 1 full, from 509 s for 41 s, BlockedByFriend: ifv#1038 moving; near titan_tank(moving)@7.7 main_battle_tank(moving)@6.3 main_battle_tank(moving)@6.1 aa_vehicle(moving)@7.6 ifv(moving)@5.6 aa_vehicle(moving)@8.8 aa_vehicle(moving)
4. **capital (60, 122)**: 48 stuck, 713 s; YieldWait 21, Embedded 11, BlockedByFriend 6, OffRoute 5, StalePath 4, BlockedByDefence 1; worst: main_battle_tank #1035 (Defend seed 2 full, from 471 s for 82 s, Embedded: on missile_battery(defence); near siege_tank(moving)@6.9 light_tank(moving)@3.2 missile_battery(fixed)@5.7 armored_car(moving)@7.6)
5. **redrock (60, 120)**: 41 stuck, 575 s; YieldWait 20, BlockedByFriend 13, OffRoute 4, StalePath 2, GateWait 2; worst: aa_vehicle #810 (Defend seed 1 full, from 364 s for 32 s, YieldWait: behind ifv#796; near artillery_emplacement(fixed)@7.2 heavy_tank(moving)@5.0 aa_vehicle(moving)@7.2 aa_vehicle(moving)@5.7 ifv(moving)@4.8 aa_vehicle(moving)@3.7 garage@9)
6. **junglepass (102, 120)**: 12 stuck, 484 s; NoPath 7, BlockedByFriend 4, YieldWait 1; worst: scout_jeep #1013 (Weekly seed 2 obstacles, from 172 s for 113 s, NoPath: goal (101.0;139.0) in open ground; other region (209 cells); fortress; near gun_pit(fixed)@6.2 scout_jeep(parked)@3.1 twin_tank(parked)@5.1 vbied(parked)@4.9)
7. **metrocity (49, 121)**: 34 stuck, 474 s; YieldWait 16, OffRoute 7, BlockedByFriend 6, StalePath 5; worst: main_battle_tank #476 (Defend seed 2 full, from 308 s for 50 s, YieldWait: behind ifv#482; near missile_battery(fixed)@9.8 main_battle_tank(moving)@7.1 main_battle_tank(moving)@8.6 ifv(moving)@5.1 main_battle_tank(moving)@8.7 main_battle_tank(moving)@4.3 a)
8. **capital (37, 130)**: 28 stuck, 401 s; YieldWait 13, BlockedByFriend 7, OffRoute 3, StalePath 3, GateWait 2; worst: ifv #1038 (Endless seed 1 full, from 510 s for 31 s, BlockedByFriend: aa_vehicle#992 moving; near main_battle_tank(moving)@3.8 titan_tank(moving)@6.0 titan_tank(moving)@4.7 titan_tank(moving)@7.5 aa_vehicle(moving)@2.9 aa_vehicle(moving)@8.5 aa_vehicle(movin)
9. **metrocity (61, 121)**: 27 stuck, 376 s; YieldWait 10, BlockedByFriend 10, StalePath 3, OffRoute 3, Unknown 1; worst: siege_tank #452 (Defend seed 2 full, from 307 s for 38 s, YieldWait: behind armored_car#541; near mlrs(moving)@8.1 main_battle_tank(moving)@4.0 ifv(moving)@7.8 armored_car(moving)@6.8 light_tank(moving)@5.3 ifv(moving)@7.0 aa_vehicle(moving)@4.3 fuel_depot@7)
10. **swamp (104, 105)**: 8 stuck, 352 s; NoPath 7, BlockedByFriend 1; worst: vbied #2617 (Siege seed 2 obstacles, from 182 s for 138 s, NoPath: goal (111.8;144.5) in open ground; other region (148 cells); field; near command_vehicle(parked)@6.9 armored_car(parked)@4.7 rocket_technical(moving)@8.4 base_wall@9)
