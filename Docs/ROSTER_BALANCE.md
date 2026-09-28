# Roster balance: before and after the roster cleanup (prompt 2)

Damage per second per CP against each armour class (light / heavy / air / structure), from the
game's own numbers (`ExportGameDoc`): every weapon's damage over its cycle, times the damage
table, with bonuses that depend only on the target's armour counted in. Conditional bonuses
(the Lancet's, the wheeled gun's flank bonus) are named in the last column. "Before" is the
round 6 build; "after" is this one. Names are the game's Vietnamese card names.

| Vehicle | id | CP before | CP after | DPS/CP before (L / H / Air / Str) | DPS/CP after (L / H / Air / Str) | Change |
|---|---|---|---|---|---|---|
| Xe trinh sát | scout_jeep | 2 | 2 | 25.0 / 6.2 / 7.5 / 7.5 | 25.0 / 6.2 / 7.5 / 7.5 |  |
| Xe bọc thép | armored_car | 3 | 3 | 27.3 / 6.8 / 8.2 / 8.2 | 27.3 / 6.8 / 8.2 / 8.2 |  |
| Bán tải rocket | rocket_technical | 3 | 3 | 25.2 / 9.3 / 5.0 / 17.8 | 25.2 / 9.3 / 5.0 / 17.8 |  |
| Xe tạo khói | smoke_carrier | 3 | 3 | 18.3 / 4.6 / 5.5 / 5.5 | 18.3 / 4.6 / 5.5 / 5.5 |  |
| Xe bom tự sát bọc thép | vbied | 3 | 3 | 233.3 / 140.0 / 0.0 / 350.0 | 233.3 / 140.0 / 0.0 / 175.0 | Structure DPS 1050→525, ×0.5 on structures |
| Bán tải ZU-23 | zu23_technical | 3 | 3 | 17.3 / 4.3 / 64.9 / 4.3 | 17.3 / 4.3 / 64.9 / 4.3 |  |
| Xe phòng không | aa_vehicle | 4 | 4 | 7.9 / 2.0 / 42.7 / 2.0 | 7.9 / 2.0 / 42.7 / 2.0 |  |
| Xe chở quân | apc | 4 | — | 22.6 / 5.7 / 6.8 / 6.8 | — | merged into ifv |
| Xe công binh | engineer_vehicle | 4 | 4 | 13.8 / 3.4 / 4.1 / 4.1 | 13.8 / 3.4 / 4.1 / 4.1 |  |
| Tăng hạng nhẹ | light_tank | 4 | 4 | 14.6 / 9.2 / 2.8 / 7.0 | 14.6 / 9.2 / 2.8 / 7.0 |  |
| Xe súng cối | mortar_carrier | 4 | 4 | 19.6 / 6.9 / 4.1 / 12.9 | 19.6 / 6.9 / 4.1 / 12.9 |  |
| Radar phản pháo | counter_battery_radar | — | 5 | — | 11.0 / 2.8 / 3.3 / 3.3 | new |
| Xe tác chiến điện tử | ew_jammer | 5 | 5 | 11.0 / 2.8 / 3.3 / 3.3 | 11.0 / 2.8 / 3.3 / 3.3 |  |
| Tăng phun lửa | flame_tank | 5 | 5 | 29.5 / 10.7 / 2.2 / 19.9 | 29.5 / 10.7 / 2.2 / 19.9 |  |
| Xe chiến đấu bộ binh | ifv | 5 | 5 | 20.3 / 7.4 / 5.4 / 7.2 | 20.3 / 7.4 / 5.4 / 7.2 | takes over the APC: captures 3×, smoke when hit |
| Xe rải mìn | mine_layer | 5 | 5 | 11.0 / 2.8 / 3.3 / 3.3 | 11.0 / 2.8 / 3.3 / 3.3 |  |
| Pháo phản lực | mlrs | 5 | 5 | 19.3 / 7.8 / 3.3 / 15.8 | 19.3 / 7.8 / 3.3 / 15.8 |  |
| Tên lửa phòng không | sam_launcher | 5 | 5 | 11.0 / 2.8 / 34.1 / 3.3 | 11.0 / 2.8 / 34.1 / 3.3 |  |
| Xe công binh công trình | sapper | 5 | 5 | 11.0 / 2.8 / 3.3 / 3.3 | 11.0 / 2.8 / 3.3 / 3.3 |  |
| Pháo tự hành | artillery | 6 | 6 | 13.2 / 4.7 / 2.8 / 8.7 | 13.2 / 4.7 / 2.8 / 8.7 |  |
| Xe tên lửa chống tăng | atgm_carrier | 6 | 6 | 14.9 / 10.0 / 2.8 / 7.3 | 14.9 / 10.0 / 2.8 / 7.3 |  |
| Xe chỉ huy | command_vehicle | — | 6 | — | 9.2 / 2.3 / 2.8 / 2.8 | new |
| Xe phóng drone FPV | fpv_carrier | 6 | 6 | 15.5 / 10.7 / 2.8 / 7.8 | 15.5 / 10.7 / 2.8 / 7.8 |  |
| Xe phóng rocket Grad | grad_truck | 6 | — | 14.8 / 5.6 / 2.8 / 11.1 | — | merged into mlrs |
| UAV trinh sát | recon_drone | 6 | 6 | 1.9 / 2.5 / 0.0 / 1.5 | 1.9 / 2.5 / 0.0 / 1.5 |  |
| Trực thăng trinh sát | scout_heli | 6 | 6 | 18.0 / 6.7 / 3.5 / 13.0 | 18.0 / 6.7 / 3.5 / 13.0 |  |
| Pháo chống tăng | tank_destroyer | 6 | 6 | 17.2 / 13.0 / 2.8 / 9.2 | 17.2 / 13.0 / 2.8 / 9.2 |  |
| Pháo tên lửa phòng không | heavy_aa | 7 | 7 | 12.6 / 3.1 / 54.6 / 3.1 | 12.6 / 3.1 / 54.6 / 3.1 |  |
| Xe phóng Lancet | lancet_truck | 7 | 7 | 10.0 / 4.8 / 2.4 / 4.1 | 10.0 / 4.8 / 2.4 / 4.1 | ×2 on artillery and on vehicles parked 3 s |
| Tăng chủ lực | main_battle_tank | 7 | 7 | 17.9 / 9.6 / 4.0 / 7.7 | 17.9 / 9.6 / 4.0 / 7.7 | APS owners got an Epic Trophy APS module |
| UAV tấn công | strike_drone | 7 | 7 | 11.5 / 12.2 / 0.0 / 12.2 | 11.5 / 12.2 / 0.0 / 12.2 |  |
| Pháo bánh lốp diệt tăng | wheeled_gun | — | 7 | — | 12.3 / 10.7 / 1.6 / 7.2 | new |
| Lựu pháo tự hành | howitzer | 8 | — | 10.0 / 3.6 / 2.1 / 6.7 | — | merged into artillery |
| Xe phóng Shahed | shahed_truck | 8 | 8 | 12.8 / 5.2 / 2.1 / 10.9 | 12.8 / 5.2 / 2.1 / 10.9 |  |
| Xe tăng rùa | turtle_tank | 8 | 8 | 8.8 / 6.6 / 1.4 / 4.7 | 8.8 / 6.6 / 1.4 / 4.7 |  |
| Tăng đánh chặn chủ động | aps_tank | 9 | — | 13.9 / 7.4 / 3.1 / 6.0 | — | merged into main_battle_tank |
| Trực thăng tấn công | attack_helicopter | 9 | 9 | 16.4 / 10.1 / 5.5 / 11.9 | 16.4 / 10.1 / 5.5 / 11.9 |  |
| BMPT Terminator | bmpt | 9 | 9 | 18.1 / 8.9 / 3.9 / 9.2 | 18.1 / 8.9 / 3.9 / 9.2 |  |
| Pháo phản lực hạng nặng | heavy_rocket_artillery | 9 | 9 | 15.4 / 7.1 / 1.8 / 15.7 | 15.4 / 7.1 / 1.8 / 15.7 |  |
| Laser phòng không | iron_beam | 9 | 9 | 0.0 / 0.0 / 11.7 / 0.0 | 0.0 / 0.0 / 11.7 / 0.0 | point defence: 1 drone/missile/rocket per 1.2 s within 30 m |
| Xe súng điện từ | railgun_truck | 11 | 9 | 4.6 / 6.2 / 0.0 / 3.7 | 5.6 / 7.5 / 0.0 / 4.5 | CP 11→9 |
| Cối công thành 240 mm | siege_mortar | 9 | — | 9.6 / 3.6 / 1.8 / 7.1 | — | merged into siege_tank |
| Pháo phản lực nhiệt áp | thermobaric_launcher | 9 | 9 | 12.1 / 5.1 / 1.8 / 10.8 | 12.1 / 5.1 / 1.8 / 10.8 |  |
| Tăng hai nòng | twin_tank | 9 | 9 | 16.1 / 10.3 / 3.1 / 7.7 | 16.1 / 10.3 / 3.1 / 7.7 |  |
| Tiêm kích | fighter_jet | 10 | 10 | 6.2 / 1.5 / 49.4 / 1.5 | 6.2 / 1.5 / 49.4 / 1.5 |  |
| Tăng hạng nặng | heavy_tank | 10 | 10 | 14.8 / 8.0 / 3.2 / 6.4 | 14.8 / 8.0 / 3.2 / 6.4 |  |
| Xe phóng tên lửa đạn đạo | ballistic_launcher | 11 | 11 | 9.8 / 4.1 / 1.5 / 8.7 | 9.8 / 4.1 / 1.5 / 8.7 |  |
| Tên lửa phòng không tầm xa | long_sam | — | 11 | — | 0.0 / 0.0 / 10.2 / 0.0 | new |
| Tăng công thành | siege_tank | 13 | 12 | 7.5 / 3.0 / 1.3 / 6.2 | 8.2 / 3.3 / 1.4 / 14.3 | CP 13→12, bunker-buster ×2.4 on structures |
| Máy bay cường kích | attack_jet | 13 | 13 | 16.1 / 15.1 / 2.9 / 19.0 | 16.1 / 15.1 / 2.9 / 19.0 |  |
| Trực thăng hạng nặng | gunship_heli | 13 | 14 | 23.4 / 16.7 / 3.2 / 16.0 | 21.7 / 15.5 / 3.0 / 14.9 | CP 13→14 |
| Ka-52 Cá sấu | heavy_attack_heli | 14 | 14 | 15.8 / 9.2 / 5.8 / 11.3 | 15.8 / 9.2 / 5.8 / 11.3 | Vikhr 50→55 m, stands off short-range AA |
| Siêu tăng Titan | titan_tank | 14 | 14 | 13.9 / 11.4 / 2.0 / 7.8 | 13.9 / 11.4 / 2.0 / 7.8 |  |
| Cường kích diệt tăng | tank_buster | 16 | 18 | 17.2 / 20.0 / 2.6 / 16.6 | 15.3 / 17.8 / 2.3 / 14.7 | CP 16→18 |
| Oanh tạc cơ hạng nặng | heavy_bomber | 20 | 20 | 21.1 / 12.7 / 0.9 / 31.6 | 21.1 / 12.7 / 0.9 / 31.6 |  |
| Máy bay ném bom tàng hình | stealth_bomber | 22 | 20 | 11.5 / 6.9 / 0.0 / 17.3 | 12.7 / 7.6 / 0.0 / 19.0 | CP 22→20 |
| Pháo đài bay | sky_gunship | 22 | — | 18.1 / 9.3 / 0.0 / 17.5 | — | no longer a card (the Gunship item flies it) |

## Campaign win rates over five seeds

The balance check plays every mission five times with the deck a player has at that point (the
starter cards and everything unlocked before it). Every mission's decks changed with the
merges, so all 23 were run.

| Mission | Round 6 | After | Note |
|---|---|---|---|
| m00–m11, m14–m22 | 5/5 each except below | 5/5 | |
| m12 | 5/5 | 5/5 | after the stalled-train fix and its new 20-minute clock (4/5 before) |
| m13 | 2/5 | 1/5 | the fortress assault; guns no longer share firing spots (see DECISIONS) |
| **Total** | **110/115** | **111/115** | |

The first run gave mission enemies the new default supply of 40 as well. m12, m13, m15, m16,
m20 and m22 dropped to 0–2/5 in it. The campaign now keeps its tuned 24 (`economy.armyCap.Campaign`)
until its rework in prompt 4. The test's player deck now picks an anti-air card that also fights
on the ground: the long-range SAM hits only aircraft. The table above is the rerun with both fixes.

## Measurements

- **Railgun:** 574 shots over 15 Hard battles (3 maps × 5 seeds, 8 minutes) hit 568 targets
  directly and 134 more by piercing: 1.22 vehicles a shot. That is under 2, so the railgun drops to 9 CP.
- **Iron Beam:** a 4-tank group under two ATGM carriers, a Lancet launcher, an MLRS and an attack
  helicopter lost 5,528 HP in 30 s with the Iron Beam against 7,136 HP with two AA vehicles (8 CP),
  with 28 intercepts a minute. It stays at 9 CP.
- **Car bombs at a base:** 12 car bombs in waves of four at an HQ with an MG bunker, a gun tower
  and a guard tower: none reached it (HQ at 100 %).
