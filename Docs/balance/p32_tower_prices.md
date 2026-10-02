# Prompt 32 L2: tower rebuild prices (Tools/balance/p32_tower_prices.py)

A static read of balance.json (no sim). Columns: equivalentCP (unclamped), the standing factor, the raw price
(equivalentCP x factor x 1.25), the clamped baseRebuildCP, the provisional price of the prompt and the gap.
Utility rows: their value and the anchor (see the script's docstring; DECISIONS "Prompt 32 L0/L1/L2").

| def | size | role | eq CP | factor | raw | price | provisional | gap | note |
|---|---|---|---|---|---|---|---|---|---|
| `guard_tower` | S | light | 6.34 | 0.575 | 4.56 | 5 | 4 | +1 | HP 1387 eff, DPS 64.6, reach 30 m, vs 14 vehicles |
| `guard_tower.watch` | S | light | 6.45 | 0.575 | 4.64 | 5 | 4 | +1 | HP 1387 eff, DPS 66.9, reach 30 m, vs 14 vehicles |
| `guard_tower.nest` | S | light | 6.44 | 0.575 | 4.63 | 5 | 4 | +1 | HP 1387 eff, DPS 66.7, reach 30 m, vs 14 vehicles |
| `mg_bunker` | S | light | 14.13 | 0.625 | 11.04 | 6 | 6 | +0 | HP 4889 eff, DPS 91.1, reach 32 m, vs 14 vehicles REBALANCE_STATS |
| `mg_bunker.twin` | S | light | 15.48 | 0.575 | 11.12 | 6 | 6 | +0 | HP 4889 eff, DPS 109.2, reach 28 m, vs 14 vehicles REBALANCE_STATS |
| `mg_bunker.flame` | S | light | 19.31 | 0.575 | 13.88 | 6 | 6 | +0 | HP 4889 eff, DPS 170.0, reach 16 m, vs 14 vehicles REBALANCE_STATS |
| `at_gun_emplacement` | S | at | 4.61 | 0.625 | 3.60 | 4 | 3 | +1 | HP 1504 eff, DPS 34.0, reach 38 m, vs 23 vehicles |
| `at_gun_emplacement.long` | S | at | 4.61 | 0.625 | 3.60 | 4 | 3 | +1 | HP 1504 eff, DPS 34.0, reach 38 m, vs 23 vehicles |
| `at_gun_emplacement.recoilless` | S | at | 3.21 | 0.575 | 2.31 | 3 | 3 | +0 | HP 1080 eff, DPS 22.9, reach 28 m, vs 23 vehicles |
| `aa_turret` | S | air | 10.54 | 0.625 | 8.23 | 6 | 6 | +0 | HP 2426 eff, DPS 219.4, reach 44 m, vs 11 vehicles REBALANCE_STATS |
| `aa_turret.flak` | S | air | 12.44 | 0.625 | 9.71 | 6 | 6 | +0 | HP 2426 eff, DPS 305.5, reach 46 m, vs 11 vehicles REBALANCE_STATS |
| `aa_turret.sam` | S | air | 5.01 | 0.725 | 4.54 | 5 | 6 | -1 | HP 2426 eff, DPS 49.6, reach 56 m, vs 11 vehicles |
| `ew_tower` | S | util:floor |  |  | 3.00 | 3 | 3 | +0 | size floor |
| `ew_tower.drone` | S | util:floor |  |  | 3.00 | 3 | 3 | +0 | size floor |
| `ew_tower.spoof` | S | util:floor |  |  | 3.00 | 3 | 3 | +0 | size floor |
| `dragons_teeth` | S | util:floor |  |  | 3.00 | 3 | 3 | +0 | size floor |
| `dragons_teeth.hedgehog` | S | util:floor |  |  | 3.00 | 3 | 3 | +0 | size floor |
| `dragons_teeth.wire` | S | util:floor |  |  | 3.00 | 3 | 3 | +0 | size floor |
| `minefield` | S | util:floor |  |  | 3.00 | 3 | 3 | +0 | size floor |
| `cp_relay` | S | util:relay |  |  | 10.80 | 6 | 3 | +3 | 10.8 CP in 120 s |
| `searchlight` | S | util:floor |  |  | 3.00 | 3 | 3 | +0 | size floor |
| `searchlight.beam` | S | util:floor |  |  | 3.00 | 3 | 3 | +0 | size floor |
| `searchlight.flare` | S | util:floor |  |  | 3.00 | 3 | 3 | +0 | size floor |
| `inflatable_decoy` | S | util:floor |  |  | 3.00 | 3 | 3 | +0 | size floor |
| `inflatable_decoy.inflatable` | S | util:floor |  |  | 3.00 | 3 | 3 | +0 | size floor |
| `inflatable_decoy.balloon` | S | util:floor |  |  | 3.00 | 3 | 3 | +0 | size floor |
| `atgm_tower` | M | at | 8.87 | 0.625 | 6.93 | 7 | 5 | +2 | HP 2112 eff, DPS 82.9, reach 50 m, vs 23 vehicles |
| `atgm_tower.top` | M | at | 9.16 | 0.625 | 7.16 | 7 | 5 | +2 | HP 2112 eff, DPS 88.5, reach 50 m, vs 23 vehicles |
| `atgm_tower.multi` | M | at | 8.17 | 0.625 | 6.39 | 6 | 5 | +1 | HP 2112 eff, DPS 70.5, reach 50 m, vs 23 vehicles |
| `gun_turret` | M | at | 14.82 | 0.625 | 11.57 | 11 |  |  | HP 5867 eff, DPS 83.3, reach 32 m, vs 23 vehicles |
| `gun_turret.long` | M | at | 13.95 | 0.625 | 10.90 | 11 | 6 | +5 | HP 5867 eff, DPS 73.8, reach 48 m, vs 23 vehicles |
| `gun_turret.auto` | M | light | 14.31 | 0.625 | 11.18 | 11 | 7 | +4 | HP 5867 eff, DPS 77.8, reach 40 m, vs 14 vehicles |
| `c_ram` | M | util:intercept |  |  | 5.00 | 5 | 5 | +0 | value 100 vs c_ram 100 |
| `c_ram.centurion` | M | util:intercept |  |  | 5.48 | 5 | 5 | +0 | value 120 vs c_ram 100 |
| `c_ram.dome` | M | util:intercept |  |  | 4.69 | 5 | 5 | +0 | value 88 vs c_ram 100 |
| `rocket_turret` | M | ground | 11.86 | 0.725 | 10.75 | 11 | 6 | +5 | HP 2180 eff, DPS 59.8, reach 55 m, vs 12 vehicles |
| `rocket_turret.cluster` | M | ground | 11.23 | 0.725 | 10.18 | 10 | 6 | +4 | HP 2180 eff, DPS 53.7, reach 55 m, vs 12 vehicles |
| `rocket_turret.guided` | M | ground | 9.82 | 0.725 | 8.90 | 9 | 6 | +3 | HP 2180 eff, DPS 41.0, reach 90 m, vs 12 vehicles |
| `heavy_flak_tower` | M | air | 7.22 | 0.725 | 6.54 | 7 | 6 | +1 | HP 3201 eff, DPS 78.0, reach 70 m, vs 11 vehicles |
| `heavy_flak_tower.heavy` | M | air | 7.22 | 0.725 | 6.54 | 7 | 6 | +1 | HP 3201 eff, DPS 78.0, reach 70 m, vs 11 vehicles |
| `heavy_flak_tower.bofors` | M | air | 7.92 | 0.625 | 6.19 | 6 | 6 | +0 | HP 2987 eff, DPS 100.6, reach 48 m, vs 11 vehicles |
| `laser_ad_station` | M | util:intercept |  |  | 4.95 | 5 |  |  | value 98 vs c_ram 100 |
| `laser_ad_station.laser` | M | util:intercept |  |  | 4.95 | 5 | 7 | -2 | value 98 vs c_ram 100 |
| `laser_ad_station.net` | M | util:intercept |  |  | 2.35 | 5 | 5 | +0 | value 22 vs c_ram 100 |
| `troop_shelter` | M | util:protect |  |  | 5.00 | 5 | 5 | +0 | value 900 vs troop_shelter 900 |
| `heavy_turret` | L | at | 24.21 | 0.625 | 18.92 | 18 | 10 | +8 | HP 12078 eff, DPS 108.1, reach 50 m, vs 23 vehicles |
| `heavy_turret.coastal` | L | ground | 34.25 | 0.725 | 31.04 | 18 | 11 | +7 | HP 12078 eff, DPS 90.1, reach 72 m, vs 12 vehicles |
| `heavy_turret.bastion` | L | at | 36.50 | 0.625 | 28.51 | 18 | 17 | +1 | HP 18722 eff, DPS 158.5, reach 50 m, vs 23 vehicles |
| `missile_battery` | L | air | 14.73 | 0.725 | 13.35 | 13 | 12 | +1 | HP 3766 eff, DPS 276.2, reach 90 m, vs 11 vehicles |
| `missile_battery.pac3` | L | air | 10.48 | 0.725 | 9.49 | 9 | 9 | +0 | HP 3766 eff, DPS 139.7, reach 72 m, vs 11 vehicles |
| `missile_battery.lrr` | L | air | 13.35 | 0.725 | 12.09 | 12 | 11 | +1 | HP 3766 eff, DPS 226.7, reach 100 m, vs 11 vehicles |
| `drone_hangar` | L | multi | 13.04 | 0.725 | 11.82 | 12 | 9 | +3 | HP 4852 eff, DPS 49.3, reach 70 m, vs 75 vehicles |
| `drone_hangar.lancet` | L | multi | 15.16 | 0.725 | 13.74 | 14 | 9 | +5 | HP 4852 eff, DPS 66.7, reach 100 m, vs 75 vehicles |
| `drone_hangar.swarm` | L | multi | 15.04 | 0.725 | 13.63 | 14 | 9 | +5 | HP 4852 eff, DPS 65.6, reach 70 m, vs 75 vehicles |
| `artillery_emplacement` | L | ground | 13.02 | 0.725 | 11.80 | 12 | 9 | +3 | HP 2180 eff, DPS 72.1, reach 90 m, vs 12 vehicles |
| `artillery_emplacement.cb` | L | ground | 12.70 | 0.725 | 11.51 | 12 | 9 | +3 | HP 2180 eff, DPS 68.6, reach 90 m, vs 12 vehicles |
| `artillery_emplacement.mortar` | L | ground | 13.13 | 0.725 | 11.90 | 12 | 9 | +3 | HP 2180 eff, DPS 73.3, reach 60 m, vs 12 vehicles |
| `shield_tower` | L | util:protect |  |  | 10.00 | 10 | 9 | +1 | value 3600 vs troop_shelter 900 |
| `shield_tower.bulwark` | L | util:protect |  |  | 10.00 | 10 | 9 | +1 | value 3600 vs troop_shelter 900 |
| `shield_tower.ward` | L | util:protect |  |  | 10.00 | 10 | 9 | +1 | value 3600 vs troop_shelter 900 |

## Reference threats by size band (median weapon of the card vehicles in the band, by penetration)

- Small (cp 3-8): kinetic `ifv_30`, he `gun_105_wheeled_he`, shaped `khrizantema`, artillery `caesar_155`
- Medium (cp 5-12): kinetic `gun_105_ags`, he `gun_105_wheeled_he`, shaped `lancet`, artillery `mlrs_rockets`
- Large (cp 9-20): kinetic `gun_125_armata_ke`, he `gun_155_crusader`, shaped `spike_nlos`, artillery `thermobaric_rockets`

Reference targets (median front armour): air 0.0, heavy 3.0, light 1.

## REBALANCE_STATS (small towers past equivalentCP 8)

| def | eq before | outgoingDamageMult | eq after | price after |
|---|---|---|---|---|
| `mg_bunker` | 14.13 | 0.3204 | 8.00 | 6 |
| `mg_bunker.twin` | 15.48 | 0.2672 | 8.00 | 6 |
| `mg_bunker.flame` | 19.31 | 0.1716 | 8.00 | 6 |
| `aa_turret` | 10.54 | 0.5762 | 8.00 | 6 |
| `aa_turret.flak` | 12.44 | 0.4139 | 8.00 | 6 |

## Steel fortress (HOLD)

Formula price 18 (raw 28.51, > 15). Tried in order:
- one roof MG fewer: raw 26.15, price 18
- health 4340 -> 2800 (not under the base turret's 2800): raw 21.00, price 18
Reached 13-15: no. Not applied: the cut that would reach 15 leaves the steel fortress weaker than the base heavy turret; HOLD stays with the owner.
