# Stuck report: after-nonet

- Battles: 76; stuck episodes of 8 s or more: 705; over 10 s: 378; safety-net activations: 0.
- Simulated: 656 min of battle (374 s to run).
- Against `before`: 2076 episodes of 8 s+ (1285 over 10 s), 0 activations.

## By cause (8 s+ / over 10 s)

| cause | 8 s+ | over 10 s | seconds | before 8 s+ | before over 10 s |
|---|---|---|---|---|---|
| BlockedByFriend | 412 | 211 | 4329 | 789 | 395 |
| YieldWait | 178 | 114 | 1964 | 578 | 418 |
| OffRoute | 33 | 23 | 362 | 178 | 128 |
| NoPath | 1 | 1 | 24 | 176 | 153 |
| StalePath | 2 | 2 | 24 | 119 | 74 |
| Unknown | 31 | 6 | 287 | 83 | 17 |
| BlockedByDefence | 33 | 16 | 362 | 60 | 34 |
| GateWait | 10 | 3 | 92 | 44 | 30 |
| Embedded | 0 | 0 | 0 | 38 | 33 |
| BlockedByObstacle | 4 | 1 | 40 | 10 | 3 |
| BlockedByEnemy | 1 | 1 | 34 | 1 | 0 |

## By mode (8 s+ / over 10 s)

| mode | 8 s+ | over 10 s | before 8 s+ | before over 10 s |
|---|---|---|---|---|
| Siege | 263 | 117 | 576 | 329 |
| Endless | 147 | 94 | 516 | 331 |
| Defend | 140 | 80 | 512 | 322 |
| Weekly | 155 | 87 | 472 | 303 |

## By place (8 s+ / over 10 s)

| place | 8 s+ | over 10 s | before 8 s+ | before over 10 s |
|---|---|---|---|---|
| fortress | 519 | 293 | 1141 | 689 |
| fortress+gate | 42 | 24 | 540 | 383 |
| field | 93 | 35 | 193 | 94 |
| camp0 | 20 | 8 | 75 | 30 |
| field+gate | 16 | 10 | 64 | 44 |
| camp1 | 15 | 8 | 59 | 43 |
| camp1+gate | 0 | 0 | 4 | 2 |

## By vehicle (8 s+ / over 10 s)

| vehicle | 8 s+ | over 10 s | before 8 s+ | before over 10 s |
|---|---|---|---|---|
| siege_tank | 96 | 48 | 253 | 134 |
| aa_vehicle | 55 | 31 | 256 | 166 |
| main_battle_tank | 43 | 27 | 180 | 116 |
| heavy_tank | 62 | 26 | 146 | 91 |
| titan_tank | 56 | 25 | 143 | 83 |
| scout_jeep | 14 | 8 | 161 | 109 |
| ifv | 35 | 21 | 104 | 62 |
| armored_car | 20 | 16 | 114 | 77 |
| elite_heavy_tank | 35 | 23 | 63 | 37 |
| light_tank | 16 | 10 | 67 | 40 |
| armored_bulldozer | 22 | 9 | 60 | 32 |
| counter_battery_radar | 23 | 16 | 56 | 30 |
| command_vehicle | 27 | 12 | 46 | 25 |
| rocket_technical | 16 | 7 | 46 | 31 |
| flame_tank | 15 | 9 | 30 | 23 |
| twin_tank | 7 | 5 | 32 | 24 |
| thermobaric_launcher | 3 | 0 | 36 | 21 |
| engineer_vehicle | 19 | 11 | 18 | 11 |
| mobile_fortress | 22 | 8 | 15 | 5 |
| artillery | 8 | 5 | 27 | 13 |
| sapper | 11 | 6 | 23 | 17 |
| ew_jammer | 19 | 8 | 15 | 8 |
| vbied | 1 | 0 | 33 | 30 |
| ammo_carrier | 29 | 14 | 0 | 0 |
| mine_layer | 8 | 6 | 19 | 12 |

## By battlefield (8 s+ / over 10 s)

| battlefield | 8 s+ | over 10 s | before 8 s+ | before over 10 s |
|---|---|---|---|---|
| capital | 154 | 88 | 431 | 304 |
| redrock | 59 | 30 | 357 | 235 |
| metrocity | 75 | 41 | 294 | 182 |
| junglepass | 92 | 58 | 226 | 138 |
| ashfield | 95 | 58 | 183 | 93 |
| swamp | 60 | 25 | 187 | 119 |
| ironport | 56 | 30 | 141 | 77 |
| coralisles | 20 | 9 | 59 | 34 |
| rustyard | 13 | 5 | 23 | 10 |
| hydrodam | 8 | 1 | 27 | 22 |
| launchsite | 13 | 5 | 20 | 9 |
| landingbeach | 7 | 3 | 23 | 13 |
| whiteout | 6 | 6 | 24 | 10 |
| borderbridge | 19 | 8 | 10 | 5 |
| greenvale | 4 | 1 | 21 | 13 |
| emberridge | 10 | 3 | 12 | 8 |
| frostpeak | 9 | 4 | 9 | 1 |
| dunebreak | 3 | 2 | 11 | 3 |
| skyhold | 2 | 1 | 11 | 7 |
| saltflat | 0 | 0 | 7 | 2 |

## By loadout (8 s+ / over 10 s)

| loadout | 8 s+ | over 10 s | before 8 s+ | before over 10 s |
|---|---|---|---|---|
| obstacles | 236 | 138 | 933 | 601 |
| full | 300 | 142 | 857 | 539 |
| light | 169 | 98 | 286 | 145 |

## Battles

| mode | map | seed | loadout | minutes | result | 8 s+ | over 10 s | worst s | rescues |
|---|---|---|---|---|---|---|---|---|---|
| Defend | ashfield | 1 | full | 9.0 | won | 23 | 11 | 16 | 0 |
| Defend | ashfield | 2 | obstacles | 9.0 | won | 1 | 1 | 12 | 0 |
| Endless | ashfield | 1 | obstacles | 10.0 | open | 20 | 17 | 21 | 0 |
| Endless | ashfield | 2 | light | 4.5 | lost | 6 | 3 | 12 | 0 |
| Weekly | ashfield | 1 | light | 10.0 | open | 2 | 2 | 12 | 0 |
| Weekly | ashfield | 2 | full | 10.0 | open | 18 | 9 | 15 | 0 |
| Defend | ironport | 1 | obstacles | 9.0 | won | 6 | 5 | 21 | 0 |
| Defend | ironport | 2 | light | 4.9 | lost | 0 | 0 | 0 | 0 |
| Endless | ironport | 1 | light | 6.0 | lost | 6 | 3 | 12 | 0 |
| Endless | ironport | 2 | full | 10.0 | open | 12 | 5 | 34 | 0 |
| Weekly | ironport | 1 | full | 10.0 | open | 3 | 2 | 16 | 0 |
| Weekly | ironport | 2 | obstacles | 10.0 | open | 12 | 7 | 16 | 0 |
| Defend | metrocity | 1 | light | 6.8 | lost | 26 | 21 | 19 | 0 |
| Defend | metrocity | 2 | full | 9.0 | won | 11 | 2 | 13 | 0 |
| Endless | metrocity | 1 | full | 10.0 | open | 13 | 7 | 18 | 0 |
| Endless | metrocity | 2 | obstacles | 10.0 | open | 4 | 2 | 12 | 0 |
| Weekly | metrocity | 1 | obstacles | 10.0 | open | 7 | 2 | 15 | 0 |
| Weekly | metrocity | 2 | light | 10.0 | open | 5 | 3 | 11 | 0 |
| Defend | redrock | 1 | full | 9.0 | won | 18 | 9 | 19 | 0 |
| Defend | redrock | 2 | obstacles | 9.0 | won | 4 | 1 | 10 | 0 |
| Endless | redrock | 1 | obstacles | 10.0 | open | 10 | 5 | 13 | 0 |
| Endless | redrock | 2 | light | 4.4 | lost | 4 | 3 | 11 | 0 |
| Weekly | redrock | 1 | light | 10.0 | open | 9 | 4 | 12 | 0 |
| Weekly | redrock | 2 | full | 10.0 | open | 8 | 5 | 16 | 0 |
| Defend | junglepass | 1 | obstacles | 9.0 | won | 5 | 1 | 11 | 0 |
| Defend | junglepass | 2 | light | 5.1 | lost | 8 | 6 | 17 | 0 |
| Endless | junglepass | 1 | light | 5.9 | lost | 8 | 6 | 15 | 0 |
| Endless | junglepass | 2 | full | 10.0 | open | 25 | 17 | 19 | 0 |
| Weekly | junglepass | 1 | full | 10.0 | open | 10 | 6 | 19 | 0 |
| Weekly | junglepass | 2 | obstacles | 10.0 | open | 24 | 16 | 17 | 0 |
| Defend | capital | 1 | light | 9.2 | lost | 25 | 13 | 14 | 0 |
| Defend | capital | 2 | full | 9.0 | won | 13 | 10 | 18 | 0 |
| Endless | capital | 1 | full | 10.0 | open | 13 | 8 | 14 | 0 |
| Endless | capital | 2 | obstacles | 10.0 | open | 26 | 18 | 22 | 0 |
| Weekly | capital | 1 | obstacles | 10.0 | open | 20 | 11 | 33 | 0 |
| Weekly | capital | 2 | light | 10.0 | open | 37 | 20 | 19 | 0 |
| Siege | ashfield | 1 | full | 5.6 | won | 3 | 0 | 10 | 0 |
| Siege | ashfield | 2 | obstacles | 14.0 | open | 22 | 15 | 13 | 0 |
| Siege | dunebreak | 1 | obstacles | 6.8 | won | 2 | 1 | 11 | 0 |
| Siege | dunebreak | 2 | light | 3.6 | won | 1 | 1 | 11 | 0 |
| Siege | frostpeak | 1 | light | 3.5 | won | 1 | 0 | 9 | 0 |
| Siege | frostpeak | 2 | full | 14.0 | open | 8 | 4 | 14 | 0 |
| Siege | ironport | 1 | full | 7.3 | won | 0 | 0 | 0 | 0 |
| Siege | ironport | 2 | obstacles | 14.0 | open | 17 | 8 | 14 | 0 |
| Siege | redrock | 1 | obstacles | 5.6 | won | 5 | 3 | 15 | 0 |
| Siege | redrock | 2 | light | 9.6 | won | 1 | 0 | 9 | 0 |
| Siege | whiteout | 1 | light | 2.6 | won | 1 | 1 | 11 | 0 |
| Siege | whiteout | 2 | full | 12.9 | won | 5 | 5 | 14 | 0 |
| Siege | greenvale | 1 | full | 5.5 | won | 2 | 0 | 9 | 0 |
| Siege | greenvale | 2 | obstacles | 8.4 | won | 2 | 1 | 11 | 0 |
| Siege | rustyard | 1 | obstacles | 8.2 | won | 6 | 2 | 11 | 0 |
| Siege | rustyard | 2 | light | 11.2 | won | 7 | 3 | 11 | 0 |
| Siege | emberridge | 1 | light | 3.7 | won | 0 | 0 | 0 | 0 |
| Siege | emberridge | 2 | full | 14.0 | open | 10 | 3 | 11 | 0 |
| Siege | junglepass | 1 | full | 9.3 | won | 1 | 0 | 9 | 0 |
| Siege | junglepass | 2 | obstacles | 7.6 | won | 11 | 6 | 15 | 0 |
| Siege | skyhold | 1 | obstacles | 9.7 | won | 2 | 1 | 10 | 0 |
| Siege | skyhold | 2 | light | 7.1 | won | 0 | 0 | 0 | 0 |
| Siege | metrocity | 1 | light | 3.0 | won | 0 | 0 | 0 | 0 |
| Siege | metrocity | 2 | full | 14.0 | open | 9 | 4 | 16 | 0 |
| Siege | landingbeach | 1 | full | 4.8 | won | 3 | 0 | 10 | 0 |
| Siege | landingbeach | 2 | obstacles | 14.0 | open | 4 | 3 | 14 | 0 |
| Siege | hydrodam | 1 | obstacles | 6.0 | won | 5 | 1 | 10 | 0 |
| Siege | hydrodam | 2 | light | 8.1 | won | 3 | 0 | 10 | 0 |
| Siege | capital | 1 | light | 4.7 | won | 1 | 0 | 9 | 0 |
| Siege | capital | 2 | full | 10.9 | won | 19 | 8 | 20 | 0 |
| Siege | launchsite | 1 | full | 6.4 | won | 2 | 1 | 11 | 0 |
| Siege | launchsite | 2 | obstacles | 6.7 | won | 11 | 4 | 24 | 0 |
| Siege | saltflat | 1 | obstacles | 7.8 | won | 0 | 0 | 0 | 0 |
| Siege | saltflat | 2 | light | 3.5 | won | 0 | 0 | 0 | 0 |
| Siege | borderbridge | 1 | light | 3.3 | won | 2 | 2 | 18 | 0 |
| Siege | borderbridge | 2 | full | 14.0 | open | 17 | 6 | 14 | 0 |
| Siege | swamp | 1 | full | 14.0 | open | 54 | 20 | 24 | 0 |
| Siege | swamp | 2 | obstacles | 11.6 | won | 6 | 5 | 14 | 0 |
| Siege | coralisles | 1 | obstacles | 6.3 | won | 4 | 2 | 14 | 0 |
| Siege | coralisles | 2 | light | 14.0 | open | 16 | 7 | 19 | 0 |

## The ten worst spots (top10.png)

1. **capital (101, 90)**: 16 stuck, 178 s; BlockedByFriend 8, YieldWait 6, BlockedByDefence 2; worst: mlrs #888 (Defend seed 2 full, from 182 s for 18 s, BlockedByFriend: armored_car#866 moving; near missile_battery(fixed)@7.1 airfield(fixed)@5.5 aa_vehicle(parked)@6.7 light_tank(moving)@3.3 armored_car(moving)@3.8 light_tank(moving)@6.8 main_battle_tank(mov)
2. **capital (92, 90)**: 13 stuck, 156 s; BlockedByFriend 8, YieldWait 4, BlockedByDefence 1; worst: turtle_tank #905 (Weekly seed 1 obstacles, from 492 s for 32 s, BlockedByFriend: long_sam#863 moving; near heavy_turret(fixed)@7.7 command_vehicle(parked)@5.9 long_sam(moving)@4.2 heavy_rocket_artillery(parked)@7.1 rocket_technical(parked)@6.3 rocket_technical(parked)
3. **junglepass (101, 93)**: 13 stuck, 154 s; BlockedByFriend 8, BlockedByDefence 3, OffRoute 1, YieldWait 1; worst: counter_battery_radar #959 (Weekly seed 1 full, from 426 s for 19 s, BlockedByFriend: command_vehicle#912 moving; near heavy_turret(fixed)@7.0 airfield(fixed)@5.6 ew_jammer(moving)@6.2 command_vehicle(moving)@4.6 rocket_technical(parked)@9.0 wheeled_gun(moving)@7.4 counter_batte)
4. **capital (92, 102)**: 15 stuck, 151 s; BlockedByFriend 9, OffRoute 3, YieldWait 3; worst: armored_car #1023 (Defend seed 2 full, from 521 s for 14 s, OffRoute: to (101.8;86.9) past missile_battery(defence); near missile_battery(fixed)@9.2 airfield(fixed)@8.1 main_battle_tank(moving)@4.6 light_tank(moving)@5.3 light_tank(moving)@6.0 scout_jeep(moving)@9.7 scout_jeep(movi)
5. **swamp (5, -5)**: 13 stuck, 141 s; BlockedByFriend 8, YieldWait 4, OffRoute 1; worst: armored_bulldozer #2555 (Siege seed 1 full, from 342 s for 16 s, YieldWait: behind armored_bulldozer#2527; near siege_tank(moving)@4.5 armored_bulldozer(moving)@7.7 siege_tank(moving)@9.8 titan_tank(moving)@5.1 siege_tank(moving)@9.6 armored_bulldozer(moving)@9.1)
6. **ashfield (49, 105)**: 12 stuck, 138 s; BlockedByFriend 7, YieldWait 4, GateWait 1; worst: main_battle_tank #496 (Defend seed 1 full, from 308 s for 15 s, BlockedByFriend: aa_vehicle#488 moving; near heavy_tank(moving)@7.6 aa_vehicle(moving)@3.7 titan_tank(moving)@5.9 ifv(parked)@4.8 aa_vehicle(moving)@6.5 aa_vehicle(moving)@5.4 base_wall@10 base_wall@10)
7. **junglepass (93, 103)**: 13 stuck, 131 s; BlockedByFriend 11, YieldWait 2; worst: ammo_carrier #945 (Weekly seed 2 obstacles, from 453 s for 14 s, BlockedByFriend: fpv_carrier#932 moving; near ew_jammer(parked)@6.3 fpv_carrier(moving)@4.2 ammo_carrier(moving)@7.2 ammo_carrier(moving)@4.4 counter_battery_radar(moving)@4.3 heavy_tank(moving)@9.6 enginee)
8. **ashfield (61, 104)**: 10 stuck, 130 s; YieldWait 5, BlockedByFriend 4, OffRoute 1; worst: aa_vehicle #575 (Endless seed 1 obstacles, from 480 s for 20 s, BlockedByFriend: main_battle_tank#572 moving; near titan_tank(moving)@9.1 main_battle_tank(moving)@3.6 artillery(moving)@4.8 aa_vehicle(moving)@8.8 aa_vehicle(parked)@8.5 ifv(moving)@6.2 ifv(moving)@6.2)
9. **ashfield (92, 102)**: 11 stuck, 114 s; BlockedByFriend 7, YieldWait 4; worst: siege_tank #509 (Endless seed 1 obstacles, from 226 s for 12 s, BlockedByFriend: titan_tank#521 moving; near heavy_turret(fixed)@9.4 heavy_tank(moving)@5.8 titan_tank(moving)@5.4 aa_vehicle(moving)@9.3 base_wall@4)
10. **capital (116, 108)**: 8 stuck, 102 s; BlockedByFriend 6, YieldWait 2; worst: counter_battery_radar #922 (Siege seed 2 full, from 318 s for 20 s, YieldWait: behind ew_jammer#857; near gun_pit(fixed)@6.8 engineer_vehicle(moving)@6.7 ew_jammer(parked)@2.7 counter_battery_radar(parked)@2.5)
