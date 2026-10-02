# Prompt 32 L4: the HQ types compared (static)

Written by `Tools/balance/p32_hq_types.py` from balance.json (no sim). Value = CP-equivalent a minute of the base
under attack (damage dealt + damage prevented over the health a CP buys, + the temporary troops' baseCP).
Health a CP buys: ground 190, aircraft 137 (median card vehicle, health x toughness).
Assumptions: gun busy 50% of the minute; 1.5 vehicles a barrage blast; a 2-minute attack;
12 C-RAM-eligible rounds a minute in salvos of 6; towers mend 50% of the minute;
75% of the emergency dome used.

## With the data's coefficients

| HQ level | target | Fortress (ground) | Fortress (anti-air) | Garrison | Shield |
|---|---|---|---|---|---|
| 1 | 4-5 | 7.7 (high) | 13.7 (high) | 6.0 (high) | 11.6 (high) |
| 2 | 5-6 | 10.1 (high) | 17.8 (high) | 7.5 (high) | 17.8 (high) |
| 3 | 6-7 | 12.4 (high) | 21.9 (high) | 9.0 (high) | 20.9 (high) |
| 4 | 7-8 | 15.5 (high) | 27.3 (high) | 12.0 (high) | 28.8 (high) |
| 5 | 8-9 | 18.6 (high) | 32.8 (high) | 15.0 (high) | 37.6 (high) |

Parts (level: Fortress ground gun + barrage | anti-air gun + barrage | Garrison squad, CP, interval | Shield intercepts + mending + dome):

- HQ 1: Fortress x0.5 gun 5.1 + barrage 2.7 | AA gun 11.0 + 2.7 | Garrison light_tank (3 CP, every 60 s, cap 6) | Shield x0.5 2 interceptors (33% of a salvo) 5.4 + mending 3.1 + dome 3.1
- HQ 2: Fortress x0.65 gun 6.6 + barrage 3.5 | AA gun 14.3 + 3.5 | Garrison armored_car+scout_jeep (5 CP, every 60 s, cap 8) | Shield x0.65 3 interceptors (50% of a salvo) 8.1 + mending 5.8 + dome 3.9
- HQ 3: Fortress x0.8 gun 8.1 + barrage 4.3 | AA gun 17.6 + 4.3 | Garrison light_tank+armored_car (6 CP, every 60 s, cap 10) | Shield x0.8 3 interceptors (50% of a salvo) 8.1 + mending 8.2 + dome 4.7
- HQ 4: Fortress x1.0 gun 10.1 + barrage 5.3 | AA gun 22.0 + 5.3 | Garrison main_battle_tank (8 CP, every 60 s, cap 12) | Shield x1.0 4 interceptors (67% of a salvo) 10.7 + mending 12.2 + dome 5.9
- HQ 5: Fortress x1.2 gun 12.2 + barrage 6.4 | AA gun 26.4 + 6.4 | Garrison main_battle_tank+scout_jeep (10 CP, every 60 s, cap 15) | Shield x1.2 5 interceptors (83% of a salvo) 13.4 + mending 17.1 + dome 7.0

## Refitted coefficients (per HQ level, each type's tables by one factor)

- `base.hqTypes.fortress.scale`: [0.29, 0.36, 0.42, 0.49, 0.55]
- `base.hqTypes.fortress.airScale`: [0.16, 0.2, 0.23, 0.27, 0.31]
- `base.hqTypes.shield.scale`: [0.15, 0.19, 0.24, 0.26, 0.29]
- `base.hqTypes.shield.regen`: [0.00059, 0.00073, 0.0009, 0.00092, 0.00096]
- `base.hqTypes.shield.dome`: [0.024, 0.029, 0.036, 0.04, 0.043]
- `base.hqTypes.garrison.every`: [120.0, 100.0, 100.0, 130.0, 170.0]

## With the refitted coefficients

| HQ level | target | Fortress (ground) | Fortress (anti-air) | Garrison | Shield |
|---|---|---|---|---|---|
| 1 | 4-5 | 4.5 (in) | 4.4 (in) | 4.5 (in) | 4.5 (in) |
| 2 | 5-6 | 5.6 (in) | 5.5 (in) | 5.5 (in) | 5.5 (in) |
| 3 | 6-7 | 6.5 (in) | 6.3 (in) | 6.6 (in) | 6.5 (in) |
| 4 | 7-8 | 7.6 (in) | 7.4 (in) | 7.7 (in) | 7.5 (in) |
| 5 | 8-9 | 8.5 (in) | 8.5 (in) | 8.5 (in) | 8.5 (in) |
