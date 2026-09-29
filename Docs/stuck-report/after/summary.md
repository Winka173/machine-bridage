# Stuck report: after

- Battles: 76; stuck episodes of 8 s or more: 578; over 10 s: 265; safety-net activations: 168.
- Simulated: 655 min of battle (361 s to run).
- Against `before`: 2076 episodes of 8 s+ (1285 over 10 s), 0 activations.

## By cause (8 s+ / over 10 s)

| cause | 8 s+ | over 10 s | seconds | before 8 s+ | before over 10 s |
|---|---|---|---|---|---|
| BlockedByFriend | 309 | 132 | 3065 | 789 | 395 |
| YieldWait | 144 | 78 | 1475 | 578 | 418 |
| OffRoute | 32 | 22 | 342 | 178 | 128 |
| NoPath | 0 | 0 | 0 | 176 | 153 |
| StalePath | 6 | 3 | 69 | 119 | 74 |
| Unknown | 34 | 3 | 308 | 83 | 17 |
| BlockedByDefence | 38 | 21 | 418 | 60 | 34 |
| GateWait | 11 | 4 | 122 | 44 | 30 |
| Embedded | 0 | 0 | 0 | 38 | 33 |
| BlockedByObstacle | 4 | 2 | 42 | 10 | 3 |
| BlockedByEnemy | 0 | 0 | 0 | 1 | 0 |

## By mode (8 s+ / over 10 s)

| mode | 8 s+ | over 10 s | before 8 s+ | before over 10 s |
|---|---|---|---|---|
| Siege | 188 | 87 | 576 | 329 |
| Endless | 169 | 82 | 516 | 331 |
| Defend | 104 | 45 | 512 | 322 |
| Weekly | 117 | 51 | 472 | 303 |

## By place (8 s+ / over 10 s)

| place | 8 s+ | over 10 s | before 8 s+ | before over 10 s |
|---|---|---|---|---|
| fortress | 425 | 198 | 1141 | 689 |
| fortress+gate | 65 | 31 | 540 | 383 |
| field | 44 | 14 | 193 | 94 |
| camp0 | 26 | 11 | 75 | 30 |
| camp1 | 13 | 10 | 59 | 43 |
| field+gate | 4 | 1 | 64 | 44 |
| camp1+gate | 1 | 0 | 4 | 2 |

## By vehicle (8 s+ / over 10 s)

| vehicle | 8 s+ | over 10 s | before 8 s+ | before over 10 s |
|---|---|---|---|---|
| siege_tank | 80 | 38 | 253 | 134 |
| aa_vehicle | 55 | 27 | 256 | 166 |
| main_battle_tank | 44 | 19 | 180 | 116 |
| heavy_tank | 61 | 22 | 146 | 91 |
| titan_tank | 51 | 22 | 143 | 83 |
| scout_jeep | 10 | 4 | 161 | 109 |
| ifv | 33 | 16 | 104 | 62 |
| armored_car | 15 | 7 | 114 | 77 |
| elite_heavy_tank | 36 | 20 | 63 | 37 |
| light_tank | 10 | 3 | 67 | 40 |
| counter_battery_radar | 18 | 7 | 56 | 30 |
| armored_bulldozer | 11 | 5 | 60 | 32 |
| command_vehicle | 16 | 11 | 46 | 25 |
| rocket_technical | 11 | 4 | 46 | 31 |
| twin_tank | 12 | 5 | 32 | 24 |
| thermobaric_launcher | 3 | 1 | 36 | 21 |
| artillery | 9 | 3 | 27 | 13 |
| vbied | 3 | 1 | 33 | 30 |
| flame_tank | 5 | 1 | 30 | 23 |
| mobile_fortress | 19 | 11 | 15 | 5 |
| sapper | 8 | 5 | 23 | 17 |
| engineer_vehicle | 11 | 5 | 18 | 11 |
| ew_jammer | 12 | 7 | 15 | 8 |
| mine_layer | 3 | 1 | 19 | 12 |
| smoke_carrier | 2 | 2 | 18 | 13 |

## By battlefield (8 s+ / over 10 s)

| battlefield | 8 s+ | over 10 s | before 8 s+ | before over 10 s |
|---|---|---|---|---|
| capital | 104 | 42 | 431 | 304 |
| redrock | 75 | 40 | 357 | 235 |
| metrocity | 72 | 32 | 294 | 182 |
| junglepass | 67 | 30 | 226 | 138 |
| ashfield | 67 | 34 | 183 | 93 |
| swamp | 15 | 7 | 187 | 119 |
| ironport | 53 | 25 | 141 | 77 |
| coralisles | 31 | 19 | 59 | 34 |
| hydrodam | 8 | 1 | 27 | 22 |
| landingbeach | 10 | 3 | 23 | 13 |
| rustyard | 9 | 2 | 23 | 10 |
| whiteout | 5 | 4 | 24 | 10 |
| borderbridge | 18 | 7 | 10 | 5 |
| launchsite | 7 | 2 | 20 | 9 |
| greenvale | 4 | 1 | 21 | 13 |
| emberridge | 12 | 5 | 12 | 8 |
| dunebreak | 10 | 7 | 11 | 3 |
| frostpeak | 9 | 3 | 9 | 1 |
| skyhold | 2 | 1 | 11 | 7 |
| saltflat | 0 | 0 | 7 | 2 |

## By loadout (8 s+ / over 10 s)

| loadout | 8 s+ | over 10 s | before 8 s+ | before over 10 s |
|---|---|---|---|---|
| obstacles | 192 | 92 | 933 | 601 |
| full | 251 | 115 | 857 | 539 |
| light | 135 | 58 | 286 | 145 |

## Battles

| mode | map | seed | loadout | minutes | result | 8 s+ | over 10 s | worst s | rescues |
|---|---|---|---|---|---|---|---|---|---|
| Defend | ashfield | 1 | full | 9.0 | won | 20 | 9 | 17 | 8 |
| Defend | ashfield | 2 | obstacles | 9.0 | won | 2 | 1 | 12 | 1 |
| Endless | ashfield | 1 | obstacles | 10.0 | open | 15 | 9 | 20 | 7 |
| Endless | ashfield | 2 | light | 4.7 | lost | 10 | 4 | 11 | 2 |
| Weekly | ashfield | 1 | light | 10.0 | open | 3 | 2 | 12 | 2 |
| Weekly | ashfield | 2 | full | 9.0 | lost | 8 | 4 | 13 | 1 |
| Defend | ironport | 1 | obstacles | 9.0 | won | 9 | 3 | 12 | 2 |
| Defend | ironport | 2 | light | 4.9 | lost | 0 | 0 | 0 | 0 |
| Endless | ironport | 1 | light | 6.0 | lost | 6 | 3 | 12 | 0 |
| Endless | ironport | 2 | full | 10.0 | open | 11 | 6 | 15 | 4 |
| Weekly | ironport | 1 | full | 10.0 | open | 12 | 6 | 15 | 3 |
| Weekly | ironport | 2 | obstacles | 10.0 | open | 9 | 4 | 14 | 4 |
| Defend | metrocity | 1 | light | 6.6 | lost | 9 | 5 | 13 | 1 |
| Defend | metrocity | 2 | full | 9.0 | won | 11 | 2 | 13 | 0 |
| Endless | metrocity | 1 | full | 10.0 | open | 14 | 7 | 29 | 4 |
| Endless | metrocity | 2 | obstacles | 10.0 | open | 4 | 2 | 12 | 0 |
| Weekly | metrocity | 1 | obstacles | 10.0 | open | 11 | 3 | 12 | 4 |
| Weekly | metrocity | 2 | light | 10.0 | open | 14 | 5 | 12 | 4 |
| Defend | redrock | 1 | full | 9.0 | won | 16 | 10 | 18 | 4 |
| Defend | redrock | 2 | obstacles | 9.0 | won | 4 | 1 | 10 | 0 |
| Endless | redrock | 1 | obstacles | 10.0 | open | 24 | 12 | 12 | 7 |
| Endless | redrock | 2 | light | 5.5 | lost | 8 | 4 | 12 | 2 |
| Weekly | redrock | 1 | light | 10.0 | open | 9 | 4 | 12 | 2 |
| Weekly | redrock | 2 | full | 10.0 | open | 8 | 6 | 13 | 5 |
| Defend | junglepass | 1 | obstacles | 9.0 | won | 5 | 1 | 11 | 0 |
| Defend | junglepass | 2 | light | 5.0 | lost | 9 | 6 | 14 | 6 |
| Endless | junglepass | 1 | light | 5.8 | lost | 4 | 2 | 12 | 2 |
| Endless | junglepass | 2 | full | 10.0 | open | 24 | 10 | 17 | 9 |
| Weekly | junglepass | 1 | full | 10.0 | open | 7 | 3 | 14 | 1 |
| Weekly | junglepass | 2 | obstacles | 10.0 | open | 10 | 6 | 15 | 4 |
| Defend | capital | 1 | light | 6.9 | lost | 10 | 2 | 13 | 3 |
| Defend | capital | 2 | full | 9.0 | won | 9 | 5 | 11 | 2 |
| Endless | capital | 1 | full | 10.0 | open | 32 | 14 | 14 | 9 |
| Endless | capital | 2 | obstacles | 10.0 | open | 17 | 9 | 14 | 5 |
| Weekly | capital | 1 | obstacles | 10.0 | open | 11 | 4 | 13 | 3 |
| Weekly | capital | 2 | light | 10.0 | open | 15 | 4 | 11 | 2 |
| Siege | ashfield | 1 | full | 5.6 | won | 3 | 0 | 10 | 0 |
| Siege | ashfield | 2 | obstacles | 14.0 | open | 6 | 5 | 15 | 1 |
| Siege | dunebreak | 1 | obstacles | 12.3 | won | 9 | 6 | 12 | 4 |
| Siege | dunebreak | 2 | light | 3.6 | won | 1 | 1 | 11 | 0 |
| Siege | frostpeak | 1 | light | 3.5 | won | 1 | 0 | 9 | 0 |
| Siege | frostpeak | 2 | full | 9.2 | won | 8 | 3 | 12 | 4 |
| Siege | ironport | 1 | full | 7.3 | won | 0 | 0 | 0 | 0 |
| Siege | ironport | 2 | obstacles | 10.4 | won | 6 | 3 | 11 | 2 |
| Siege | redrock | 1 | obstacles | 5.6 | won | 5 | 3 | 15 | 0 |
| Siege | redrock | 2 | light | 9.6 | won | 1 | 0 | 9 | 0 |
| Siege | whiteout | 1 | light | 2.6 | won | 1 | 1 | 11 | 0 |
| Siege | whiteout | 2 | full | 12.4 | won | 4 | 3 | 14 | 2 |
| Siege | greenvale | 1 | full | 5.5 | won | 2 | 0 | 9 | 0 |
| Siege | greenvale | 2 | obstacles | 11.5 | won | 2 | 1 | 11 | 1 |
| Siege | rustyard | 1 | obstacles | 7.9 | won | 2 | 1 | 11 | 1 |
| Siege | rustyard | 2 | light | 9.4 | won | 7 | 1 | 10 | 1 |
| Siege | emberridge | 1 | light | 3.7 | won | 0 | 0 | 0 | 0 |
| Siege | emberridge | 2 | full | 14.0 | open | 12 | 5 | 13 | 3 |
| Siege | junglepass | 1 | full | 9.3 | won | 1 | 0 | 9 | 0 |
| Siege | junglepass | 2 | obstacles | 10.4 | won | 7 | 2 | 12 | 2 |
| Siege | skyhold | 1 | obstacles | 9.7 | won | 2 | 1 | 10 | 0 |
| Siege | skyhold | 2 | light | 7.1 | won | 0 | 0 | 0 | 0 |
| Siege | metrocity | 1 | light | 3.0 | won | 0 | 0 | 0 | 0 |
| Siege | metrocity | 2 | full | 14.0 | open | 9 | 8 | 24 | 6 |
| Siege | landingbeach | 1 | full | 4.8 | won | 3 | 0 | 10 | 1 |
| Siege | landingbeach | 2 | obstacles | 13.7 | won | 7 | 3 | 14 | 2 |
| Siege | hydrodam | 1 | obstacles | 6.0 | won | 5 | 1 | 10 | 0 |
| Siege | hydrodam | 2 | light | 8.1 | won | 3 | 0 | 10 | 1 |
| Siege | capital | 1 | light | 4.7 | won | 1 | 0 | 9 | 0 |
| Siege | capital | 2 | full | 9.3 | won | 9 | 4 | 13 | 2 |
| Siege | launchsite | 1 | full | 6.4 | won | 2 | 1 | 11 | 0 |
| Siege | launchsite | 2 | obstacles | 13.8 | won | 5 | 1 | 12 | 1 |
| Siege | saltflat | 1 | obstacles | 7.8 | won | 0 | 0 | 0 | 0 |
| Siege | saltflat | 2 | light | 3.5 | won | 0 | 0 | 0 | 0 |
| Siege | borderbridge | 1 | light | 3.3 | won | 2 | 2 | 18 | 0 |
| Siege | borderbridge | 2 | full | 11.9 | won | 16 | 5 | 12 | 4 |
| Siege | swamp | 1 | full | 8.3 | won | 10 | 4 | 24 | 3 |
| Siege | swamp | 2 | obstacles | 14.0 | open | 5 | 3 | 12 | 1 |
| Siege | coralisles | 1 | obstacles | 7.4 | won | 10 | 7 | 14 | 5 |
| Siege | coralisles | 2 | light | 14.0 | open | 21 | 12 | 13 | 8 |

## The ten worst spots (top10.png)

1. **metrocity (116, 89)**: 10 stuck, 124 s; BlockedByFriend 7, OffRoute 1, GateWait 1, BlockedByDefence 1; worst: mobile_fortress #485 (Siege seed 2 full, from 436 s for 24 s, BlockedByDefence: airfield#373 parked; near base_wall@9 fortress_gate@3 base_wall@10)
2. **capital (102, 89)**: 12 stuck, 120 s; BlockedByFriend 4, BlockedByDefence 4, YieldWait 3, Unknown 1; worst: heavy_tank #897 (Endless seed 1 full, from 186 s for 11 s, BlockedByDefence: airfield#805 parked; near heavy_turret(fixed)@8.2 airfield(fixed)@6.1 base_wall@5 base_wall@7)
3. **redrock (92, 103)**: 12 stuck, 119 s; BlockedByFriend 7, YieldWait 5; worst: ammo_carrier #715 (Weekly seed 2 full, from 554 s for 13 s, BlockedByFriend: ammo_carrier#714 moving; near ammo_carrier(moving)@5.7 ammo_carrier(moving)@8.3 ammo_carrier(moving)@8.7 vbied(moving)@6.7 mobile_fortress(parked)@8.9)
4. **ashfield (90, 102)**: 11 stuck, 112 s; BlockedByFriend 9, YieldWait 2; worst: elite_heavy_tank #462 (Weekly seed 1 light, from 250 s for 12 s, BlockedByFriend: heavy_tank#446 moving; near command_vehicle(moving)@4.7 heavy_tank(moving)@5.6)
5. **metrocity (101, 92)**: 8 stuck, 103 s; BlockedByDefence 5, BlockedByFriend 2, YieldWait 1; worst: heavy_tank #428 (Endless seed 1 full, from 172 s for 28 s, BlockedByDefence: airfield#373 parked; near airfield(fixed)@5.7 ifv(moving)@9.5 titan_tank(moving)@5.8 aa_vehicle(moving)@6.5 base_wall@4 fortress_gate@9)
6. **ironport (101, 92)**: 10 stuck, 100 s; BlockedByFriend 7, BlockedByDefence 2, YieldWait 1; worst: aa_vehicle #491 (Endless seed 2 full, from 46 s for 12 s, BlockedByFriend: light_tank#494 moving; near missile_battery(fixed)@9.1 airfield(fixed)@5.0 aa_vehicle(moving)@6.5 light_tank(moving)@3.5 base_wall@7 base_wall@7)
7. **redrock (49, 119)**: 9 stuck, 85 s; YieldWait 5, BlockedByFriend 2, GateWait 1, OffRoute 1; worst: aa_vehicle #810 (Endless seed 1 obstacles, from 432 s for 10 s, GateWait: doorway 0; near main_battle_tank(parked)@7.0 aa_vehicle(moving)@9.8 aa_vehicle(moving)@4.2 aa_vehicle(moving)@4.1 heavy_tank(moving)@3.5 aa_vehicle(moving)@7.2 aa_vehicle(movin)
8. **junglepass (100, 94)**: 7 stuck, 82 s; BlockedByFriend 4, OffRoute 1, Unknown 1, BlockedByDefence 1; worst: aa_vehicle #901 (Endless seed 2 full, from 95 s for 16 s, BlockedByFriend: main_battle_tank#923 moving; near missile_battery(fixed)@7.0 airfield(fixed)@5.0 main_battle_tank(moving)@7.4 armored_car(moving)@7.4 aa_vehicle(moving)@9.8 main_battle_tank(moving)@3.7 light_ta)
9. **ashfield (60, 105)**: 7 stuck, 76 s; YieldWait 5, BlockedByFriend 2; worst: heavy_tank #511 (Defend seed 1 full, from 325 s for 17 s, YieldWait: behind ifv#494; near gun_pit(fixed)@4.8 titan_tank(moving)@8.3 titan_tank(moving)@4.3 ifv(moving)@5.5 main_battle_tank(moving)@9.2 aa_vehicle(moving)@5.3 aa_vehicle(moving)@9.0 aa_v)
10. **junglepass (92, 103)**: 8 stuck, 74 s; BlockedByFriend 6, YieldWait 2; worst: siege_tank #936 (Endless seed 1 light, from 242 s for 12 s, BlockedByFriend: heavy_tank#908 moving; near heavy_tank(moving)@5.8)
