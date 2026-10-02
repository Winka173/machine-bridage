# Audio metrics (fix pass L7; play-test 12 lane C)

Written by `python Tools/sfx/analyze_sfx.py` (rerunnable; the numbers come from the .ogg files, nothing by hand).
LUFS: ITU-R BS.1770-4 integrated; M-max: the loudest 400 ms (what a one-shot hits at). Peak: sample / 4x true peak, dBFS.
Sub: share of the energy under 150 Hz. Tail: s from the peak until the 10 ms envelope stays 40 dB under it.
Keng: a 2-6 kHz peak at least 12 dB over its 1/3-octave median, under 160 Hz wide, that takes at least 120 ms to fall 20 dB (measured 30-400 ms after the onset; bins more than 30 dB under the loudest are not heard and skipped).

## Per size (must rise: louder, deeper, longer)

| size | shot M-max | shot sub % | shot tail s | blast M-max | blast sub % | blast tail s |
|---|---|---|---|---|---|---|
| <= 14.5 mm | -28.1 | 1.8 | 0.3 | -24.2 | 12.7 | 0.2 |
| 20-40 mm | -23.8 | 12.0 | 0.5 | -18.1 | 31.1 | 0.9 |
| 57-105 mm | -16.6 | 39.1 | 1.4 | -15.6 | 45.5 | 1.7 |
| 120-155 mm | -14.6 | 53.6 | 2.0 | -13.6 | 55.6 | 2.4 |
| 203-240 mm | -13.1 | 61.3 | 2.9 | -12.1 | 61.3 | 4.2 |
| bombs | - | - | - | -11.0 | 66.2 | 5.4 |
| big rockets / >= 406 mm | -11.6 | 70.0 | 4.7 | -10.1 | 71.0 | 7.1 |
| super weapons | -10.6 | 75.3 | 7.3 | -9.1 | 78.3 | 10.7 |

Rising check: every step rises.

Keng outside the armour-metal group: none.

## Per size before this pass (prompt 34 L6 banks, as the game played them) and after

| size | before shot (bank) | M-max | sub % | tail s | after shot M-max | sub % | tail s | before blast / hit (bank) | M-max | sub % | tail s | keng | after blast M-max | sub % | tail s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| <= 14.5 mm | p34/shot_t0 | -21.5 | 1.9 | 0.3 | -28.1 | 1.8 | 0.3 | impact_metal | -16.9 | 9.5 | 0.3 | 0/3 | -24.2 | 12.7 | 0.2 |
| 20-40 mm | p34/shot_t1 | -19.4 | 11.5 | 0.5 | -23.8 | 12.0 | 0.5 | p34/blast_he_t1 | -18.6 | 15.7 | 0.6 | 0/3 | -18.1 | 31.1 | 0.9 |
| 57-105 mm | p34/shot_t2 | -17.0 | 35.4 | 1.0 | -16.6 | 39.1 | 1.4 | p34/blast_he_t2 | -16.1 | 38.8 | 1.1 | 0/3 | -15.6 | 45.5 | 1.7 |
| 120-155 mm | p34/shot_t3 | -15.1 | 51.5 | 1.7 | -14.6 | 53.6 | 2.0 | p34/blast_he_t3 | -15.7 | 53.7 | 2.2 | 0/3 | -13.6 | 55.6 | 2.4 |
| 203-240 mm | p34/shot_t4 | -13.7 | 58.5 | 2.9 | -13.1 | 61.3 | 2.9 | p34/blast_he_t4 | -14.0 | 61.9 | 3.5 | 0/3 | -12.1 | 61.3 | 4.2 |
| bombs | - | - | - | - | - | - | - | p34/blast_he_t4 | -14.0 | 61.9 | 3.5 | 0/3 | -11.0 | 66.2 | 5.4 |
| big rockets / >= 406 mm | p34/shot_t5 | -12.6 | 69.3 | 4.5 | -11.6 | 70.0 | 4.7 | p34/blast_he_t5 | -13.0 | 71.2 | 5.3 | 0/3 | -10.1 | 71.0 | 7.1 |
| super weapons | p34/shot_t5 | -12.6 | 69.3 | 4.5 | -10.6 | 75.3 | 7.3 | p34/blast_he_t5 | -13.0 | 71.2 | 5.3 | 0/3 | -9.1 | 78.3 | 10.7 |

Before, the 20-40 mm to 203-240 mm kinetic rounds without a blast (autocannons, tank guns, railguns) landed on `p34/blast_ap_t1..t4`, the T0 machine guns on `impact_metal`, whatever they struck.

## Before / after (bank means)

| bank (before) | M-max | sub % | tail s | keng clips |
|---|---|---|---|---|
| autocannon | -16.0 | 45.9 | 0.45 | 0/3 |
| cannon | -15.5 | 56.6 | 1.01 | 0/3 |
| click | -22.4 | 16.9 | 0.04 | 0/2 |
| collapse | -15.3 | 73.5 | 2.09 | 0/2 |
| debris | -17.5 | 2.8 | 0.71 | 0/3 |
| drums_loop | -12.2 | 97.9 | 5.27 | 0/1 |
| explosion_huge | -12.9 | 75.8 | 4.06 | 0/3 |
| explosion_large | -13.5 | 61.3 | 2.26 | 0/4 |
| explosion_medium | -12.4 | 57.2 | 1.55 | 0/4 |
| explosion_small | -16.0 | 72.0 | 0.76 | 0/4 |
| fire_loop | -19.5 | 46.7 | 5.01 | 0/1 |
| flak | -20.0 | 76.9 | 0.51 | 0/3 |
| flame | -12.4 | 61.1 | 0.93 | 0/2 |
| heavy_cannon | -14.3 | 71.9 | 1.64 | 0/3 |
| impact_metal | -16.9 | 9.5 | 0.28 | 0/3 |
| jet_loop | -15.4 | 28.6 | 2.46 | 0/1 |
| jet_pass | -13.7 | 13.8 | 1.74 | 0/3 |
| mg | -14.0 | 71.1 | 0.62 | 0/3 |
| missile_launch | -12.3 | 39.7 | 1.25 | 0/2 |
| p34/blast_ap_t1 | -15.9 | 1.1 | 0.54 | 2/2 |
| p34/blast_ap_t2 | -15.3 | 1.2 | 0.71 | 2/2 |
| p34/blast_ap_t3 | -15.3 | 2.0 | 1.02 | 2/2 |
| p34/blast_ap_t4 | -15.3 | 2.4 | 1.55 | 2/2 |
| p34/blast_he_t1 | -18.6 | 15.7 | 0.58 | 0/3 |
| p34/blast_he_t2 | -16.1 | 38.8 | 1.08 | 0/3 |
| p34/blast_he_t3 | -15.7 | 53.7 | 2.22 | 0/3 |
| p34/blast_he_t4 | -14.0 | 61.9 | 3.55 | 0/3 |
| p34/blast_he_t5 | -13.0 | 71.2 | 5.31 | 0/3 |
| p34/blast_heat | -18.9 | 48.0 | 1.04 | 0/2 |
| p34/blast_thermo_t3 | -12.0 | 94.5 | 1.98 | 0/2 |
| p34/blast_thermo_t4 | -11.9 | 89.3 | 2.79 | 0/2 |
| p34/crash_fall | -11.4 | 1.4 | 0.32 | 0/2 |
| p34/crash_impact | -13.4 | 56.5 | 3.16 | 0/2 |
| p34/launch_t2 | -12.5 | 4.8 | 1.81 | 0/2 |
| p34/launch_t3 | -13.2 | 4.8 | 2.26 | 0/2 |
| p34/launch_t4 | -13.1 | 13.2 | 2.72 | 0/2 |
| p34/launch_t5 | -12.3 | 14.6 | 3.11 | 0/2 |
| p34/ship_engine | -15.0 | 96.5 | 3.37 | 0/1 |
| p34/ship_horn | -12.3 | 68.2 | 2.35 | 0/1 |
| p34/shot_t0 | -21.5 | 1.9 | 0.31 | 0/3 |
| p34/shot_t1 | -19.4 | 11.5 | 0.50 | 0/3 |
| p34/shot_t2 | -17.0 | 35.4 | 1.03 | 0/3 |
| p34/shot_t3 | -15.1 | 51.5 | 1.74 | 0/3 |
| p34/shot_t4 | -13.7 | 58.5 | 2.91 | 0/3 |
| p34/shot_t5 | -12.6 | 69.3 | 4.50 | 0/3 |
| p34/smallarms_cluster | -13.7 | 2.5 | 0.84 | 0/3 |
| p34/train_horn | -11.9 | 0.0 | 1.74 | 2/2 |
| p34/train_rails | -24.0 | 12.6 | 2.37 | 0/1 |
| p34/wreck_aircraft | -13.3 | 55.5 | 3.33 | 1/2 |
| p34/wreck_artillery | -14.6 | 47.2 | 3.60 | 0/2 |
| p34/wreck_drone | -20.4 | 15.8 | 0.56 | 0/2 |
| p34/wreck_heli | -15.1 | 53.0 | 2.24 | 0/2 |
| p34/wreck_ship | -12.6 | 92.6 | 3.51 | 0/2 |
| p34/wreck_tank | -13.8 | 13.3 | 2.59 | 0/2 |
| p34/wreck_truck | -15.5 | 45.4 | 3.22 | 0/2 |
| p34/wreck_wheeled | -15.2 | 24.8 | 0.88 | 0/2 |
| rain_loop | -15.7 | 17.5 | 2.99 | 0/1 |
| rocket_launch | -14.6 | 34.5 | 0.81 | 0/4 |
| rotor_loop | -15.8 | 66.9 | 0.26 | 0/1 |
| siren | -10.0 | 0.0 | 0.63 | 0/1 |
| thunder | -13.8 | 23.9 | 3.84 | 0/3 |
| wind_loop | -13.3 | 30.9 | 5.59 | 0/1 |

## Every clip

| clip | s | LUFS | M-max | peak | true peak | sub % | tail s | keng dB / ms / Hz | keng |
|---|---|---|---|---|---|---|---|---|---|
| autocannon/autocannon_1.ogg | 0.69 | -21.5 | -18.6 | -0.9 | -0.8 | 44.3 | 0.56 | 4 / 116 / 3854 |  |
| autocannon/autocannon_2.ogg | 0.69 | -15.5 | -14.0 | -0.9 | -0.9 | 43.9 | 0.46 | 4 / 35 / 4328 |  |
| autocannon/autocannon_3.ogg | 0.68 | -17.1 | -15.4 | -1.0 | -1.0 | 49.6 | 0.34 | 5 / 35 / 3962 |  |
| cannon/cannon_1.ogg | 1.50 | -16.7 | -14.5 | -1.6 | -1.6 | 70.3 | 0.82 | 3 / 81 / 2196 |  |
| cannon/cannon_2.ogg | 1.50 | -20.6 | -15.6 | -1.0 | -1.0 | 53.9 | 1.10 | 2 / 139 / 2046 |  |
| cannon/cannon_3.ogg | 1.38 | -22.5 | -16.5 | -0.9 | -0.9 | 45.5 | 1.11 | 0 / 0 / 0 |  |
| click/click_1.ogg | 0.09 | -21.0 | -21.0 | -1.7 | -1.3 | 32.5 | 0.03 | 8 / 35 / 3187 |  |
| click/click_2.ogg | 0.07 | -23.8 | -23.8 | -1.0 | -1.0 | 1.3 | 0.04 | 0 / 0 / 0 |  |
| collapse/collapse_1.ogg | 3.70 | -19.2 | -15.1 | -1.0 | -0.3 | 89.4 | 1.61 | 4 / 23 / 2455 |  |
| collapse/collapse_2.ogg | 3.85 | -20.1 | -15.5 | -1.0 | -1.0 | 57.5 | 2.57 | 0 / 116 / 2024 |  |
| debris/debris_1.ogg | 0.81 | -20.3 | -17.8 | -0.9 | -0.8 | 4.4 | 0.55 | 5 / 58 / 3230 |  |
| debris/debris_2.ogg | 0.85 | -20.5 | -16.5 | -1.6 | -1.5 | 1.4 | 0.71 | 4 / 70 / 4565 |  |
| debris/debris_3.ogg | 0.95 | -22.0 | -18.1 | -1.0 | -0.9 | 2.5 | 0.88 | 4 / 70 / 3252 |  |
| drums_loop/drums_loop_1.ogg | 7.38 | -15.7 | -12.2 | -1.0 | -1.0 | 97.9 | 5.27 | 0 / 0 / 0 |  |
| explosion_huge/explosion_huge_1.ogg | 5.00 | -16.8 | -13.4 | -1.0 | -1.0 | 74.9 | 4.16 | 2 / 139 / 3919 |  |
| explosion_huge/explosion_huge_2.ogg | 4.97 | -14.9 | -12.9 | -1.0 | -1.0 | 92.0 | 4.22 | 0 / 0 / 0 |  |
| explosion_huge/explosion_huge_3.ogg | 4.96 | -17.7 | -12.5 | -1.1 | -1.1 | 60.6 | 3.81 | 4 / 255 / 3725 |  |
| explosion_large/explosion_large_1.ogg | 3.00 | -18.0 | -12.5 | -1.0 | -1.0 | 52.3 | 2.57 | 2 / 418 / 2885 |  |
| explosion_large/explosion_large_2.ogg | 2.51 | -17.4 | -14.0 | -1.0 | -0.9 | 66.3 | 1.77 | 3 / 464 / 2261 |  |
| explosion_large/explosion_large_3.ogg | 3.00 | -19.0 | -13.6 | -1.0 | -0.9 | 53.0 | 2.30 | 3 / 116 / 3876 |  |
| explosion_large/explosion_large_4.ogg | 2.69 | -17.6 | -13.8 | -1.0 | -1.0 | 73.5 | 2.41 | 5 / 23 / 3790 |  |
| explosion_medium/explosion_medium_1.ogg | 2.00 | -18.5 | -12.8 | -0.9 | -0.9 | 33.1 | 1.54 | 1 / 35 / 2239 |  |
| explosion_medium/explosion_medium_2.ogg | 1.99 | -17.9 | -13.6 | -0.9 | -0.9 | 70.9 | 1.61 | 5 / 23 / 4242 |  |
| explosion_medium/explosion_medium_3.ogg | 2.00 | -17.1 | -11.8 | -0.9 | -0.8 | 46.7 | 1.67 | 3 / 290 / 3273 |  |
| explosion_medium/explosion_medium_4.ogg | 2.00 | -15.1 | -11.4 | -1.0 | -1.0 | 78.0 | 1.36 | 4 / 70 / 2153 |  |
| explosion_small/explosion_small_1.ogg | 0.95 | -17.6 | -14.1 | -1.7 | -1.6 | 51.9 | 0.87 | 4 / 58 / 2692 |  |
| explosion_small/explosion_small_2.ogg | 1.00 | -17.9 | -15.2 | -0.9 | -0.9 | 88.2 | 0.72 | 0 / 0 / 0 |  |
| explosion_small/explosion_small_3.ogg | 0.92 | -22.2 | -17.3 | -1.0 | -1.0 | 72.8 | 0.71 | 3 / 139 / 4867 |  |
| explosion_small/explosion_small_4.ogg | 0.96 | -22.2 | -17.5 | -1.0 | -1.0 | 75.3 | 0.73 | 3 / 163 / 4393 |  |
| fire_loop/fire_loop_1.ogg | 5.50 | -20.9 | -19.5 | -0.9 | -0.6 | 46.7 | 5.01 | 3 / 174 / 3575 |  |
| flak/flak_1.ogg | 0.60 | -19.7 | -19.7 | -0.9 | -0.9 | 73.3 | 0.50 | 0 / 0 / 0 |  |
| flak/flak_2.ogg | 0.61 | -19.5 | -19.5 | -0.9 | -0.9 | 79.8 | 0.50 | 4 / 104 / 2562 |  |
| flak/flak_3.ogg | 0.61 | -25.0 | -20.7 | -0.9 | -0.9 | 77.6 | 0.53 | 0 / 0 / 0 |  |
| flame/flame_1.ogg | 1.50 | -13.7 | -12.9 | -0.9 | -0.9 | 41.2 | 1.15 | 10 / 104 / 2885 |  |
| flame/flame_2.ogg | 1.38 | -12.6 | -12.0 | -1.0 | -1.0 | 81.1 | 0.71 | 0 / 0 / 0 |  |
| heavy_cannon/heavy_cannon_1.ogg | 2.00 | -19.6 | -14.3 | -1.0 | -1.0 | 76.5 | 1.86 | 3 / 81 / 2067 |  |
| heavy_cannon/heavy_cannon_2.ogg | 1.84 | -21.5 | -15.5 | -0.9 | -0.9 | 68.0 | 1.52 | 3 / 197 / 4500 |  |
| heavy_cannon/heavy_cannon_3.ogg | 1.98 | -17.8 | -13.0 | -1.0 | -1.0 | 71.1 | 1.53 | 0 / 0 / 0 |  |
| impact_metal/impact_metal_1.ogg | 0.45 | -17.1 | -17.1 | -0.7 | -0.7 | 8.5 | 0.28 | 8 / 58 / 4221 |  |
| impact_metal/impact_metal_2.ogg | 0.47 | -17.8 | -17.8 | -1.0 | -0.9 | 5.4 | 0.28 | 6 / 81 / 2541 |  |
| impact_metal/impact_metal_3.ogg | 0.44 | -15.7 | -15.7 | -1.9 | -1.5 | 14.6 | 0.28 | 8 / 255 / 3445 |  |
| jet_loop/jet_loop_1.ogg | 5.00 | -17.6 | -15.4 | -1.0 | -1.0 | 28.6 | 2.46 | 0 / 0 / 0 |  |
| jet_pass/jet_pass_1.ogg | 3.66 | -17.0 | -13.4 | -1.0 | -1.0 | 11.5 | 1.63 | 4 / 302 / 2390 |  |
| jet_pass/jet_pass_2.ogg | 3.76 | -16.4 | -13.2 | -1.0 | -1.0 | 5.1 | 1.57 | 4 / 267 / 3531 |  |
| jet_pass/jet_pass_3.ogg | 3.67 | -19.7 | -14.6 | -1.0 | -1.0 | 24.7 | 2.03 | 3 / 1950 / 2046 |  |
| mg/mg_1.ogg | 0.79 | -15.4 | -13.3 | -1.0 | -1.0 | 72.6 | 0.66 | 4 / 23 / 2239 |  |
| mg/mg_2.ogg | 0.75 | -17.6 | -14.8 | -0.9 | -0.9 | 68.8 | 0.59 | 4 / 35 / 5017 |  |
| mg/mg_3.ogg | 0.75 | -17.3 | -14.0 | -1.0 | -1.0 | 71.9 | 0.61 | 4 / 35 / 5017 |  |
| missile_launch/missile_launch_1.ogg | 1.47 | -14.8 | -12.5 | -1.0 | -1.0 | 57.4 | 1.06 | 3 / 476 / 2369 |  |
| missile_launch/missile_launch_2.ogg | 1.50 | -13.4 | -12.2 | -0.9 | -0.9 | 22.0 | 1.44 | 3 / 104 / 3618 |  |
| rain_loop/rain_loop_1.ogg | 8.00 | -16.2 | -15.7 | -1.0 | -1.0 | 17.5 | 2.99 | 3 / 639 / 2929 |  |
| rocket_launch/rocket_launch_1.ogg | 1.14 | -19.8 | -15.6 | -0.9 | -0.9 | 73.2 | 0.97 | 3 / 151 / 4328 |  |
| rocket_launch/rocket_launch_2.ogg | 1.15 | -20.2 | -15.5 | -0.9 | -0.9 | 63.1 | 0.94 | 3 / 46 / 3596 |  |
| rocket_launch/rocket_launch_3.ogg | 1.27 | -16.1 | -13.6 | -1.7 | -1.7 | 0.0 | 0.79 | 4 / 23 / 4221 |  |
| rocket_launch/rocket_launch_4.ogg | 1.00 | -15.2 | -13.5 | -1.9 | -1.8 | 1.5 | 0.55 | 3 / 337 / 2692 |  |
| rotor_loop/rotor_loop_1.ogg | 2.46 | -16.1 | -15.8 | -0.9 | -0.9 | 66.9 | 0.26 | 0 / 0 / 0 |  |
| sfx/blast_air_s1/blast_air_s1_1.ogg | 1.18 | -23.9 | -19.6 | -0.7 | -0.7 | 20.5 | 0.73 | 4 / 139 / 4910 |  |
| sfx/blast_air_s1/blast_air_s1_2.ogg | 1.25 | -23.7 | -19.6 | -1.1 | -1.1 | 21.7 | 0.80 | 3 / 163 / 2649 |  |
| sfx/blast_air_s2/blast_air_s2_1.ogg | 1.78 | -21.1 | -17.1 | -3.8 | -3.8 | 33.0 | 1.15 | 4 / 70 / 2692 |  |
| sfx/blast_air_s2/blast_air_s2_2.ogg | 1.88 | -22.3 | -17.1 | -3.1 | -3.1 | 33.5 | 1.19 | 3 / 46 / 2347 |  |
| sfx/blast_air_s3/blast_air_s3_1.ogg | 2.61 | -19.7 | -15.1 | -3.3 | -3.3 | 42.2 | 1.58 | 4 / 81 / 2692 |  |
| sfx/blast_air_s3/blast_air_s3_2.ogg | 2.66 | -20.7 | -15.1 | -3.1 | -3.1 | 43.1 | 1.68 | 3 / 58 / 2347 |  |
| sfx/blast_bomb/blast_bomb_1.ogg | 5.92 | -15.6 | -11.1 | -1.9 | -1.9 | 65.4 | 5.82 | 0 / 0 / 0 |  |
| sfx/blast_bomb/blast_bomb_2.ogg | 5.92 | -14.1 | -11.0 | -2.4 | -2.4 | 66.9 | 5.84 | 0 / 0 / 0 |  |
| sfx/blast_bomb/blast_bomb_3.ogg | 5.88 | -16.3 | -11.0 | -2.2 | -2.1 | 66.3 | 4.55 | 0 / 0 / 0 |  |
| sfx/blast_he_s1/blast_he_s1_1.ogg | 1.17 | -21.7 | -18.1 | -4.8 | -4.8 | 31.0 | 1.01 | 4 / 58 / 2692 |  |
| sfx/blast_he_s1/blast_he_s1_2.ogg | 1.19 | -22.3 | -18.1 | -5.8 | -5.8 | 31.1 | 1.03 | 3 / 186 / 5491 |  |
| sfx/blast_he_s1/blast_he_s1_3.ogg | 1.10 | -23.0 | -18.1 | -3.6 | -3.5 | 31.1 | 0.80 | 4 / 128 / 4177 |  |
| sfx/blast_he_s2/blast_he_s2_1.ogg | 2.23 | -21.7 | -15.6 | -3.2 | -3.1 | 45.5 | 1.82 | 0 / 0 / 0 |  |
| sfx/blast_he_s2/blast_he_s2_2.ogg | 2.18 | -20.4 | -15.6 | -0.7 | -0.4 | 45.7 | 1.61 | 4 / 23 / 4242 |  |
| sfx/blast_he_s2/blast_he_s2_3.ogg | 2.15 | -20.9 | -15.6 | -1.8 | -1.8 | 45.4 | 1.74 | 3 / 23 / 3273 |  |
| sfx/blast_he_s3/blast_he_s3_1.ogg | 3.41 | -19.9 | -13.6 | -0.9 | -0.9 | 55.8 | 2.67 | 3 / 348 / 2498 |  |
| sfx/blast_he_s3/blast_he_s3_2.ogg | 2.87 | -18.6 | -13.5 | -1.0 | -1.0 | 55.5 | 2.33 | 3 / 430 / 2261 |  |
| sfx/blast_he_s3/blast_he_s3_3.ogg | 2.93 | -19.7 | -13.7 | -0.9 | -0.8 | 55.6 | 2.31 | 3 / 255 / 2304 |  |
| sfx/blast_he_s4/blast_he_s4_1.ogg | 4.38 | -18.6 | -12.1 | -3.0 | -3.0 | 62.1 | 4.15 | 0 / 0 / 0 |  |
| sfx/blast_he_s4/blast_he_s4_2.ogg | 4.95 | -20.6 | -12.1 | -3.2 | -3.2 | 63.0 | 4.79 | 2 / 209 / 2153 |  |
| sfx/blast_he_s4/blast_he_s4_3.ogg | 4.47 | -16.2 | -12.0 | -2.8 | -2.7 | 58.8 | 3.67 | 0 / 0 / 0 |  |
| sfx/blast_he_s406/blast_he_s406_1.ogg | 7.22 | -14.0 | -10.1 | -0.8 | -0.8 | 70.0 | 7.11 | 0 / 0 / 0 |  |
| sfx/blast_he_s406/blast_he_s406_2.ogg | 7.22 | -13.1 | -10.0 | -1.7 | -1.7 | 72.0 | 7.13 | 0 / 0 / 0 |  |
| sfx/blast_heat_s2/blast_heat_s2_1.ogg | 1.59 | -20.0 | -16.6 | -4.7 | -4.7 | 33.0 | 1.19 | 4 / 46 / 2692 |  |
| sfx/blast_heat_s2/blast_heat_s2_2.ogg | 1.75 | -20.6 | -16.6 | -4.1 | -4.1 | 42.3 | 1.11 | 3 / 151 / 2412 |  |
| sfx/blast_heat_s3/blast_heat_s3_1.ogg | 2.61 | -20.6 | -14.6 | -3.6 | -3.6 | 46.4 | 2.10 | 0 / 0 / 0 |  |
| sfx/blast_heat_s3/blast_heat_s3_2.ogg | 2.66 | -19.3 | -14.6 | -2.8 | -2.8 | 47.9 | 1.82 | 4 / 23 / 4242 |  |
| sfx/blast_super/blast_super_1.ogg | 11.45 | -12.5 | -9.2 | -0.0 | 0.0 | 78.0 | 10.27 | 0 / 0 / 0 |  |
| sfx/blast_super/blast_super_2.ogg | 11.45 | -11.9 | -9.0 | 0.1 | 0.1 | 78.7 | 11.03 | 0 / 0 / 0 |  |
| sfx/blast_thermo_s3/blast_thermo_s3_1.ogg | 3.49 | -19.0 | -13.0 | -0.9 | -0.9 | 61.9 | 2.78 | 3 / 244 / 2476 |  |
| sfx/blast_thermo_s3/blast_thermo_s3_2.ogg | 3.18 | -17.4 | -12.9 | -0.7 | -0.6 | 61.6 | 2.54 | 0 / 0 / 0 |  |
| sfx/blast_thermo_s4/blast_thermo_s4_1.ogg | 4.72 | -17.5 | -11.4 | -3.1 | -3.1 | 67.4 | 4.36 | 0 / 0 / 0 |  |
| sfx/blast_thermo_s4/blast_thermo_s4_2.ogg | 4.86 | -19.4 | -11.4 | -1.1 | -1.0 | 68.9 | 4.68 | 0 / 0 / 0 |  |
| sfx/burst_s0_10/burst_s0_10_1.ogg | 0.57 | -23.7 | -23.0 | -8.1 | -7.7 | 1.9 | 0.51 | 4 / 58 / 5060 |  |
| sfx/burst_s0_10/burst_s0_10_2.ogg | 0.57 | -24.2 | -23.3 | -7.6 | -7.4 | 1.8 | 0.51 | 5 / 35 / 5039 |  |
| sfx/burst_s0_10/burst_s0_10_3.ogg | 0.57 | -23.6 | -23.1 | -7.8 | -7.6 | 1.5 | 0.31 | 4 / 163 / 2433 |  |
| sfx/burst_s0_16/burst_s0_16_1.ogg | 0.62 | -22.5 | -20.6 | -7.3 | -6.6 | 1.5 | 0.50 | 5 / 221 / 2433 |  |
| sfx/burst_s0_16/burst_s0_16_2.ogg | 0.62 | -22.8 | -21.0 | -7.4 | -6.6 | 1.6 | 0.56 | 5 / 23 / 2433 |  |
| sfx/burst_s0_16/burst_s0_16_3.ogg | 0.62 | -23.2 | -21.5 | -7.3 | -7.0 | 1.8 | 0.56 | 5 / 116 / 2433 |  |
| sfx/burst_s0_55/burst_s0_55_1.ogg | 0.70 | -21.1 | -18.8 | -8.0 | -8.0 | 1.9 | 0.43 | 5 / 232 / 2433 |  |
| sfx/burst_s0_55/burst_s0_55_2.ogg | 0.72 | -21.4 | -19.0 | -8.4 | -8.4 | 2.2 | 0.41 | 2 / 116 / 4134 |  |
| sfx/burst_s0_55/burst_s0_55_3.ogg | 0.70 | -21.5 | -19.1 | -7.7 | -7.6 | 1.7 | 0.33 | 3 / 58 / 2433 |  |
| sfx/burst_s1_10/burst_s1_10_1.ogg | 0.80 | -22.3 | -19.5 | -4.4 | -4.4 | 12.0 | 0.60 | 3 / 232 / 5146 |  |
| sfx/burst_s1_10/burst_s1_10_2.ogg | 0.80 | -21.9 | -19.3 | -5.8 | -5.8 | 15.1 | 0.50 | 3 / 151 / 4910 |  |
| sfx/burst_s1_10/burst_s1_10_3.ogg | 0.78 | -22.2 | -20.4 | -6.4 | -5.7 | 10.9 | 0.59 | 3 / 46 / 4027 |  |
| sfx/burst_s1_22/burst_s1_22_1.ogg | 0.91 | -21.7 | -19.3 | -7.8 | -7.7 | 15.3 | 0.67 | 3 / 139 / 4974 |  |
| sfx/burst_s1_22/burst_s1_22_2.ogg | 0.90 | -21.2 | -18.9 | -7.4 | -7.2 | 8.6 | 0.53 | 3 / 104 / 2261 |  |
| sfx/burst_s1_22/burst_s1_22_3.ogg | 0.91 | -22.1 | -20.0 | -7.5 | -7.5 | 14.2 | 0.58 | 3 / 139 / 5556 |  |
| sfx/burst_s1_35/burst_s1_35_1.ogg | 0.94 | -18.8 | -16.9 | -6.8 | -6.8 | 10.7 | 0.58 | 4 / 186 / 3488 |  |
| sfx/burst_s1_35/burst_s1_35_2.ogg | 0.95 | -18.8 | -16.9 | -5.0 | -4.9 | 11.3 | 0.52 | 4 / 325 / 5469 |  |
| sfx/burst_s1_35/burst_s1_35_3.ogg | 0.94 | -18.5 | -16.5 | -5.3 | -5.3 | 12.1 | 0.54 | 3 / 221 / 3704 |  |
| sfx/burst_s1_55/burst_s1_55_1.ogg | 0.93 | -17.8 | -15.7 | -3.4 | -3.4 | 12.6 | 0.60 | 3 / 174 / 5771 |  |
| sfx/burst_s1_55/burst_s1_55_2.ogg | 0.92 | -17.7 | -15.8 | -4.9 | -4.9 | 15.0 | 0.57 | 2 / 163 / 2455 |  |
| sfx/burst_s1_55/burst_s1_55_3.ogg | 0.92 | -17.9 | -15.9 | -4.3 | -4.2 | 10.5 | 0.59 | 4 / 163 / 2907 |  |
| sfx/crash_fall/crash_fall_1.ogg | 2.80 | -18.2 | -15.4 | -4.6 | -4.6 | 8.1 | 0.17 | 0 / 0 / 0 |  |
| sfx/crash_fall/crash_fall_2.ogg | 2.80 | -17.9 | -15.2 | -4.7 | -4.6 | 8.0 | 0.22 | 0 / 0 / 0 |  |
| sfx/crash_impact/crash_impact_1.ogg | 4.00 | -18.1 | -11.6 | -1.2 | -1.2 | 62.3 | 3.92 | 0 / 0 / 0 |  |
| sfx/crash_impact/crash_impact_2.ogg | 4.00 | -19.8 | -11.6 | -2.7 | -2.7 | 62.6 | 3.91 | 3 / 209 / 2347 |  |
| sfx/engine_heavy/engine_heavy_1.ogg | 4.00 | -20.6 | -20.1 | -2.1 | -2.1 | 62.2 | 2.87 | 0 / 0 / 0 |  |
| sfx/engine_tracked/engine_tracked_1.ogg | 4.00 | -21.5 | -21.2 | -3.7 | -3.7 | 55.4 | 2.08 | 0 / 0 / 0 |  |
| sfx/engine_wheeled/engine_wheeled_1.ogg | 4.00 | -23.6 | -23.3 | -7.1 | -7.1 | 40.2 | 3.92 | 3 / 23 / 2993 |  |
| sfx/flare_pop/flare_pop_1.ogg | 1.41 | -22.0 | -18.2 | -2.8 | -2.8 | 8.5 | 1.14 | 3 / 232 / 4242 |  |
| sfx/flare_pop/flare_pop_2.ogg | 1.43 | -21.8 | -18.2 | -4.2 | -4.2 | 8.3 | 1.10 | 3 / 186 / 3639 |  |
| sfx/hit_concrete_heavy/hit_concrete_heavy_1.ogg | 0.85 | -20.3 | -16.2 | -1.1 | -0.8 | 27.3 | 0.79 | 5 / 58 / 3230 |  |
| sfx/hit_concrete_heavy/hit_concrete_heavy_2.ogg | 0.86 | -21.3 | -16.3 | -1.6 | -1.5 | 27.2 | 0.78 | 6 / 81 / 3359 |  |
| sfx/hit_concrete_heavy/hit_concrete_heavy_3.ogg | 1.02 | -21.6 | -16.5 | -1.1 | -1.1 | 28.8 | 0.92 | 3 / 93 / 2885 |  |
| sfx/hit_concrete_light/hit_concrete_light_1.ogg | 0.40 | -25.1 | -25.1 | -1.7 | -1.5 | 13.3 | 0.33 | 6 / 46 / 3941 |  |
| sfx/hit_concrete_light/hit_concrete_light_2.ogg | 0.37 | -24.5 | -24.5 | -4.0 | -4.0 | 14.4 | 0.18 | 6 / 46 / 2304 |  |
| sfx/hit_concrete_light/hit_concrete_light_3.ogg | 0.40 | -24.9 | -24.9 | -4.7 | -4.4 | 13.3 | 0.33 | 5 / 58 / 3058 |  |
| sfx/hit_ground_heavy/hit_ground_heavy_1.ogg | 0.98 | -22.0 | -17.1 | -3.2 | -3.1 | 36.1 | 0.85 | 2 / 128 / 4587 |  |
| sfx/hit_ground_heavy/hit_ground_heavy_2.ogg | 0.87 | -21.4 | -17.2 | -2.6 | -2.6 | 37.8 | 0.63 | 3 / 128 / 2369 |  |
| sfx/hit_ground_heavy/hit_ground_heavy_3.ogg | 0.93 | -21.3 | -17.1 | -1.7 | -1.7 | 37.2 | 0.76 | 3 / 139 / 4177 |  |
| sfx/hit_ground_light/hit_ground_light_1.ogg | 0.31 | -24.7 | -24.7 | -4.2 | -4.2 | 13.8 | 0.24 | 7 / 46 / 2089 |  |
| sfx/hit_ground_light/hit_ground_light_2.ogg | 0.26 | -23.9 | -23.9 | -4.9 | -4.8 | 12.5 | 0.20 | 6 / 46 / 5060 |  |
| sfx/hit_ground_light/hit_ground_light_3.ogg | 0.28 | -24.1 | -24.1 | -4.4 | -4.3 | 11.8 | 0.21 | 7 / 70 / 2735 |  |
| sfx/hit_metal_heavy/hit_metal_heavy_1.ogg | 0.68 | -18.6 | -16.1 | -1.4 | -1.2 | 18.3 | 0.43 | 0 / 0 / 0 |  |
| sfx/hit_metal_heavy/hit_metal_heavy_2.ogg | 0.72 | -18.1 | -16.1 | -3.1 | -3.0 | 16.4 | 0.48 | 0 / 0 / 0 |  |
| sfx/hit_metal_heavy/hit_metal_heavy_3.ogg | 0.69 | -18.5 | -16.1 | -1.1 | -1.0 | 18.0 | 0.43 | 0 / 0 / 0 |  |
| sfx/hit_metal_light/hit_metal_light_1.ogg | 0.38 | -20.0 | -20.0 | -2.2 | -2.2 | 5.3 | 0.24 | 25 / 81 / 2627 |  |
| sfx/hit_metal_light/hit_metal_light_2.ogg | 0.39 | -20.1 | -20.1 | -2.4 | -2.4 | 5.0 | 0.24 | 25 / 81 / 2024 |  |
| sfx/hit_metal_light/hit_metal_light_3.ogg | 0.38 | -20.0 | -20.0 | -2.3 | -2.2 | 6.0 | 0.24 | 24 / 81 / 2089 |  |
| sfx/hit_pen_heavy/hit_pen_heavy_1.ogg | 0.99 | -20.4 | -15.1 | -1.3 | -1.3 | 41.7 | 0.86 | 2 / 151 / 3639 |  |
| sfx/hit_pen_heavy/hit_pen_heavy_2.ogg | 1.00 | -20.7 | -15.2 | -1.2 | -1.2 | 45.1 | 0.88 | 3 / 209 / 2067 |  |
| sfx/hit_pen_heavy/hit_pen_heavy_3.ogg | 0.89 | -19.0 | -15.2 | -1.1 | -1.1 | 44.2 | 0.65 | 2 / 81 / 2067 |  |
| sfx/hit_pen_light/hit_pen_light_1.ogg | 0.38 | -22.5 | -22.5 | -1.2 | -1.2 | 24.9 | 0.21 | 4 / 81 / 3618 |  |
| sfx/hit_pen_light/hit_pen_light_2.ogg | 0.36 | -22.2 | -22.2 | -1.7 | -1.7 | 24.9 | 0.22 | 5 / 93 / 4328 |  |
| sfx/hit_pen_light/hit_pen_light_3.ogg | 0.36 | -22.6 | -22.6 | -2.2 | -2.2 | 26.2 | 0.25 | 4 / 35 / 3575 |  |
| sfx/launch_atgm/launch_atgm_1.ogg | 1.53 | -20.1 | -17.2 | -4.8 | -4.6 | 7.1 | 0.99 | 4 / 209 / 4845 |  |
| sfx/launch_atgm/launch_atgm_2.ogg | 1.49 | -20.2 | -17.3 | -5.5 | -5.4 | 6.7 | 1.04 | 4 / 104 / 4759 |  |
| sfx/launch_atgm/launch_atgm_3.ogg | 1.54 | -20.2 | -17.3 | -4.8 | -4.8 | 7.3 | 1.06 | 3 / 81 / 2692 |  |
| sfx/launch_big/launch_big_1.ogg | 3.02 | -15.0 | -12.2 | -2.6 | -2.6 | 28.8 | 2.36 | 3 / 267 / 2627 |  |
| sfx/launch_big/launch_big_2.ogg | 2.97 | -15.0 | -12.2 | -3.5 | -3.3 | 28.5 | 2.39 | 3 / 197 / 4953 |  |
| sfx/launch_big/launch_big_3.ogg | 2.98 | -14.8 | -12.2 | -3.2 | -3.2 | 28.2 | 2.15 | 3 / 70 / 3273 |  |
| sfx/launch_cruise/launch_cruise_1.ogg | 2.84 | -15.7 | -12.7 | -1.5 | -1.5 | 22.6 | 2.10 | 2 / 337 / 5556 |  |
| sfx/launch_cruise/launch_cruise_2.ogg | 2.84 | -15.9 | -12.7 | -1.7 | -1.6 | 22.6 | 2.30 | 4 / 23 / 4974 |  |
| sfx/launch_cruise/launch_cruise_3.ogg | 2.84 | -15.5 | -12.7 | -3.2 | -3.2 | 22.9 | 2.58 | 3 / 430 / 5125 |  |
| sfx/launch_s2/launch_s2_1.ogg | 1.09 | -18.8 | -16.8 | -4.8 | -4.6 | 9.2 | 0.57 | 3 / 244 / 4500 |  |
| sfx/launch_s2/launch_s2_2.ogg | 1.13 | -19.8 | -16.7 | -4.2 | -4.2 | 8.6 | 0.63 | 4 / 70 / 5469 |  |
| sfx/launch_s2/launch_s2_3.ogg | 1.09 | -18.8 | -16.7 | -2.7 | -2.5 | 9.1 | 0.64 | 3 / 151 / 4565 |  |
| sfx/launch_s3/launch_s3_1.ogg | 1.91 | -17.6 | -14.7 | -2.9 | -2.9 | 17.7 | 1.27 | 3 / 267 / 3488 |  |
| sfx/launch_s3/launch_s3_2.ogg | 1.84 | -17.5 | -14.7 | -2.7 | -2.6 | 17.4 | 1.33 | 3 / 81 / 4005 |  |
| sfx/launch_s3/launch_s3_3.ogg | 1.86 | -18.3 | -14.7 | -3.1 | -3.1 | 17.3 | 1.32 | 3 / 81 / 4888 |  |
| sfx/launch_sam/launch_sam_1.ogg | 1.99 | -18.6 | -15.8 | -2.5 | -2.4 | 11.3 | 1.17 | 3 / 418 / 5835 |  |
| sfx/launch_sam/launch_sam_2.ogg | 1.98 | -18.9 | -15.7 | -3.0 | -3.0 | 11.3 | 1.40 | 4 / 279 / 4199 |  |
| sfx/launch_sam/launch_sam_3.ogg | 2.02 | -18.3 | -15.8 | -4.5 | -4.2 | 11.4 | 1.44 | 3 / 372 / 5879 |  |
| sfx/missile_hiss/missile_hiss_1.ogg | 0.50 | -23.0 | -21.2 | -7.2 | -6.9 | 1.7 | 0.02 | 3 / 70 / 4737 |  |
| sfx/missile_hiss/missile_hiss_2.ogg | 0.55 | -23.1 | -21.1 | -6.5 | -6.2 | 1.4 | 0.02 | 3 / 58 / 5857 |  |
| sfx/ship_engine/ship_engine_1.ogg | 4.00 | -19.4 | -19.1 | -5.1 | -5.1 | 71.3 | 1.08 | 2 / 313 / 2756 |  |
| sfx/ship_horn/ship_horn_1.ogg | 3.80 | -13.7 | -13.0 | -1.0 | -1.0 | 52.6 | 1.34 | 0 / 0 / 0 |  |
| sfx/shot_ac57/shot_ac57_1.ogg | 0.71 | -23.3 | -19.3 | -0.7 | -0.7 | 12.3 | 0.59 | 5 / 46 / 5512 |  |
| sfx/shot_ac57/shot_ac57_2.ogg | 0.71 | -22.6 | -18.6 | -1.7 | -1.6 | 15.9 | 0.60 | 4 / 23 / 2735 |  |
| sfx/shot_ac57/shot_ac57_3.ogg | 0.71 | -25.1 | -21.0 | -2.5 | -2.4 | 12.1 | 0.60 | 4 / 58 / 2713 |  |
| sfx/shot_s0/shot_s0_1.ogg | 0.35 | -26.4 | -26.4 | -8.2 | -8.0 | 4.0 | 0.31 | 6 / 46 / 4156 |  |
| sfx/shot_s0/shot_s0_2.ogg | 0.35 | -29.0 | -29.0 | -8.1 | -7.1 | 1.1 | 0.31 | 5 / 58 / 3424 |  |
| sfx/shot_s0/shot_s0_3.ogg | 0.35 | -28.4 | -28.4 | -6.8 | -6.6 | 0.6 | 0.31 | 6 / 35 / 4500 |  |
| sfx/shot_s0/shot_s0_4.ogg | 0.35 | -28.4 | -28.4 | -8.1 | -7.5 | 1.3 | 0.31 | 6 / 70 / 3704 |  |
| sfx/shot_s1/shot_s1_1.ogg | 0.60 | -26.4 | -23.8 | -5.5 | -5.2 | 10.3 | 0.50 | 4 / 81 / 3725 |  |
| sfx/shot_s1/shot_s1_2.ogg | 0.60 | -25.7 | -23.2 | -5.7 | -5.6 | 14.0 | 0.50 | 4 / 81 / 5039 |  |
| sfx/shot_s1/shot_s1_3.ogg | 0.60 | -28.3 | -25.7 | -7.2 | -6.8 | 10.6 | 0.50 | 4 / 151 / 3230 |  |
| sfx/shot_s1/shot_s1_4.ogg | 0.60 | -25.0 | -22.4 | -5.5 | -5.5 | 13.1 | 0.48 | 5 / 104 / 5728 |  |
| sfx/shot_s2/shot_s2_1.ogg | 1.92 | -21.0 | -16.6 | -2.8 | -2.8 | 38.5 | 1.74 | 4 / 128 / 2842 |  |
| sfx/shot_s2/shot_s2_2.ogg | 1.76 | -22.3 | -16.6 | -1.5 | -1.5 | 38.7 | 1.24 | 4 / 58 / 2584 |  |
| sfx/shot_s2/shot_s2_3.ogg | 1.74 | -22.5 | -16.6 | -3.2 | -3.2 | 40.2 | 1.26 | 1 / 81 / 2003 |  |
| sfx/shot_s3/shot_s3_1.ogg | 2.64 | -21.4 | -14.6 | -2.6 | -2.6 | 53.7 | 2.24 | 3 / 128 / 2089 |  |
| sfx/shot_s3/shot_s3_2.ogg | 2.42 | -21.1 | -14.6 | -3.6 | -3.6 | 53.9 | 1.70 | 4 / 186 / 4500 |  |
| sfx/shot_s3/shot_s3_3.ogg | 2.70 | -21.0 | -14.5 | -1.2 | -1.1 | 53.3 | 2.18 | 0 / 0 / 0 |  |
| sfx/shot_s4/shot_s4_1.ogg | 3.34 | -19.5 | -13.1 | -2.9 | -2.9 | 62.5 | 2.68 | 0 / 0 / 0 |  |
| sfx/shot_s4/shot_s4_2.ogg | 3.64 | -19.9 | -13.1 | -1.3 | -1.2 | 61.6 | 2.92 | 3 / 383 / 2519 |  |
| sfx/shot_s4/shot_s4_3.ogg | 3.61 | -19.9 | -13.1 | -2.4 | -2.4 | 59.7 | 3.17 | 2 / 209 / 2089 |  |
| sfx/shot_s406/shot_s406_1.ogg | 5.82 | -17.9 | -11.6 | -2.3 | -2.3 | 69.6 | 5.07 | 0 / 0 / 0 |  |
| sfx/shot_s406/shot_s406_2.ogg | 5.43 | -18.2 | -11.6 | -2.3 | -2.3 | 70.5 | 4.26 | 3 / 372 / 2089 |  |
| sfx/shot_super/shot_super_1.ogg | 7.45 | -15.2 | -10.6 | -1.0 | -0.9 | 73.1 | 7.20 | 0 / 0 / 0 |  |
| sfx/shot_super/shot_super_2.ogg | 7.45 | -15.1 | -10.6 | -0.9 | -0.9 | 77.5 | 7.32 | 0 / 0 / 0 |  |
| sfx/smallarms_cluster/smallarms_cluster_1.ogg | 1.60 | -18.4 | -17.9 | -5.2 | -5.2 | 2.2 | 0.35 | 3 / 163 / 4371 |  |
| sfx/smallarms_cluster/smallarms_cluster_2.ogg | 1.60 | -18.7 | -17.1 | -4.1 | -4.1 | 2.7 | 1.10 | 3 / 221 / 5599 |  |
| sfx/smallarms_cluster/smallarms_cluster_3.ogg | 1.60 | -17.8 | -15.8 | -4.1 | -3.9 | 2.6 | 1.23 | 4 / 23 / 3445 |  |
| sfx/train_horn/train_horn_1.ogg | 3.10 | -14.8 | -13.5 | -2.8 | -2.8 | 0.0 | 1.68 | 0 / 0 / 0 |  |
| sfx/train_horn/train_horn_2.ogg | 3.10 | -14.5 | -13.5 | -3.3 | -3.3 | 0.0 | 1.55 | 0 / 0 / 0 |  |
| sfx/train_rails/train_rails_1.ogg | 4.00 | -21.4 | -20.1 | -3.8 | -3.8 | 27.9 | 1.03 | 3 / 58 / 2433 |  |
| sfx/warn_whistle/warn_whistle_1.ogg | 1.25 | -23.2 | -19.0 | -9.2 | -9.2 | 3.3 | 0.05 | 4 / 35 / 3122 |  |
| sfx/warn_whistle/warn_whistle_2.ogg | 1.25 | -23.1 | -19.0 | -8.3 | -8.2 | 4.0 | 0.06 | 3 / 151 / 2541 |  |
| sfx/warn_whistle/warn_whistle_3.ogg | 1.25 | -23.2 | -19.0 | -9.0 | -9.0 | 3.8 | 0.03 | 3 / 313 / 2412 |  |
| sfx/warn_whistle_big/warn_whistle_big_1.ogg | 1.60 | -19.8 | -16.0 | -3.0 | -3.0 | 29.6 | 0.04 | 3 / 697 / 3036 |  |
| sfx/warn_whistle_big/warn_whistle_big_2.ogg | 1.60 | -20.0 | -16.0 | -3.3 | -3.3 | 29.9 | 0.03 | 3 / 151 / 3704 |  |
| sfx/wreck_aircraft/wreck_aircraft_1.ogg | 4.38 | -18.1 | -11.6 | -1.1 | -1.1 | 62.3 | 4.23 | 0 / 0 / 0 |  |
| sfx/wreck_aircraft/wreck_aircraft_2.ogg | 4.50 | -19.8 | -11.6 | -2.5 | -2.5 | 62.6 | 4.40 | 3 / 267 / 2347 |  |
| sfx/wreck_artillery/wreck_artillery_1.ogg | 3.50 | -17.1 | -12.6 | -3.1 | -3.0 | 56.1 | 3.06 | 2 / 35 / 2046 |  |
| sfx/wreck_artillery/wreck_artillery_2.ogg | 3.47 | -16.2 | -12.5 | -2.6 | -2.5 | 57.4 | 2.93 | 3 / 430 / 2283 |  |
| sfx/wreck_drone/wreck_drone_1.ogg | 1.17 | -22.0 | -18.6 | -5.8 | -5.8 | 28.5 | 1.01 | 5 / 58 / 2692 |  |
| sfx/wreck_drone/wreck_drone_2.ogg | 1.19 | -22.7 | -18.6 | -5.9 | -5.9 | 28.8 | 1.04 | 3 / 139 / 5491 |  |
| sfx/wreck_heli/wreck_heli_1.ogg | 3.40 | -18.1 | -12.6 | -2.9 | -2.8 | 57.2 | 2.80 | 2 / 325 / 2412 |  |
| sfx/wreck_heli/wreck_heli_2.ogg | 2.84 | -17.7 | -12.6 | -0.9 | -0.9 | 58.2 | 2.25 | 2 / 302 / 2261 |  |
| sfx/wreck_ship/wreck_ship_1.ogg | 4.50 | -12.3 | -10.6 | -2.0 | -1.9 | 71.6 | 4.12 | 3 / 197 / 2046 |  |
| sfx/wreck_ship/wreck_ship_2.ogg | 4.50 | -12.9 | -10.6 | -0.3 | -0.3 | 72.3 | 4.15 | 0 / 0 / 0 |  |
| sfx/wreck_tank/wreck_tank_1.ogg | 3.39 | -18.9 | -12.6 | -0.9 | -0.8 | 58.2 | 2.61 | 0 / 0 / 0 |  |
| sfx/wreck_tank/wreck_tank_2.ogg | 3.15 | -17.7 | -12.5 | -3.5 | -3.4 | 60.0 | 2.43 | 0 / 0 / 0 |  |
| sfx/wreck_truck/wreck_truck_1.ogg | 3.42 | -17.3 | -13.1 | -3.5 | -3.5 | 55.0 | 2.89 | 2 / 93 / 2261 |  |
| sfx/wreck_truck/wreck_truck_2.ogg | 3.27 | -17.4 | -13.0 | -0.8 | -0.8 | 55.6 | 2.70 | 2 / 476 / 2261 |  |
| sfx/wreck_wheeled/wreck_wheeled_1.ogg | 2.24 | -20.3 | -14.1 | -1.5 | -1.5 | 48.8 | 1.78 | 0 / 0 / 0 |  |
| sfx/wreck_wheeled/wreck_wheeled_2.ogg | 2.18 | -19.4 | -14.1 | -0.9 | -0.5 | 49.0 | 1.65 | 4 / 23 / 4242 |  |
| siren/siren_1.ogg | 2.78 | -12.2 | -10.0 | -0.9 | -0.9 | 0.0 | 0.63 | 6 / 151 / 2412 |  |
| thunder/thunder_1.ogg | 4.45 | -20.4 | -12.5 | -2.3 | -2.3 | 19.4 | 3.82 | 2 / 139 / 2455 |  |
| thunder/thunder_2.ogg | 4.55 | -19.6 | -15.3 | -0.9 | -0.9 | 31.6 | 4.09 | 2 / 151 / 2003 |  |
| thunder/thunder_3.ogg | 4.53 | -20.3 | -13.5 | -0.9 | -0.9 | 20.7 | 3.60 | 4 / 46 / 3467 |  |
| wind_loop/wind_loop_1.ogg | 8.00 | -15.0 | -13.3 | -1.0 | -1.0 | 30.9 | 5.59 | 0 / 0 / 0 |  |
