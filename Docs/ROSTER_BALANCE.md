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

## Prompt 8: DPS per CP before and after

Paper damage a second per CP (the lab's `RosterDpsTable`: every mount's damage over its cycle, times
the damage table, the elite damage scale counted), before prompt 8 and after it. Only four rows change:
the armoured bulldozer is new, and three cards move branch now that branches go by class (the FPV
carrier and the siege tank to Armour, the long-range SAM to Light; balance.json "branches"). "=": the
same as before.

| Vehicle | id | class | branch before → after | CP | HP | DPS/CP before (L / H / Air / Str) | DPS/CP after | Change |
|---|---|---|---|---|---|---|---|---|
| Scout jeep | scout_jeep | Scout | Light | 2 | 300 | = | 25.0 / 6.3 / 7.5 / 7.5 |  |
| Armored car | armored_car | Light | Light | 3 | 750 | = | 27.3 / 6.8 / 8.2 / 8.2 |  |
| Rocket technical | rocket_technical | Artillery | Artillery | 3 | 375 | = | 25.2 / 9.3 / 5.0 / 17.8 |  |
| Smoke generator carrier | smoke_carrier | Support | Light | 3 | 1000 | = | 18.3 / 4.6 / 5.5 / 5.5 |  |
| Armoured car bomb | vbied | Scout | Light | 3 | 650 | = | 233.3 / 140.0 / 0.0 / 175.0 |  |
| ZU-23 technical | zu23_technical | AntiAir | Light | 3 | 425 | = | 17.3 / 4.3 / 64.9 / 4.3 |  |
| Anti-air | aa_vehicle | AntiAir | Light | 4 | 875 | = | 7.9 / 2.0 / 42.7 / 2.0 |  |
| Engineer vehicle | engineer_vehicle | Support | Light | 4 | 1750 | = | 13.8 / 3.4 / 4.1 / 4.1 |  |
| Light tank | light_tank | Tank | Armor | 4 | 1000 | = | 14.6 / 9.2 / 2.8 / 7.0 |  |
| Mortar carrier | mortar_carrier | Artillery | Artillery | 4 | 800 | = | 19.6 / 6.9 / 4.1 / 12.9 |  |
| Counter-battery radar | counter_battery_radar | Support | Light | 5 | 900 | = | 11.0 / 2.8 / 3.3 / 3.3 |  |
| EW jammer | ew_jammer | Support | Light | 5 | 950 | = | 11.0 / 2.8 / 3.3 / 3.3 |  |
| Flame tank | flame_tank | Heavy | Armor | 5 | 1500 | = | 29.5 / 10.7 / 2.3 / 19.9 |  |
| Infantry fighting vehicle | ifv | Light | Light | 5 | 1300 | = | 20.3 / 7.4 / 5.4 / 7.2 |  |
| Mine layer | mine_layer | Support | Light | 5 | 1050 | = | 11.0 / 2.8 / 3.3 / 3.3 |  |
| Rocket launcher | mlrs | Artillery | Artillery | 5 | 800 | = | 19.3 / 7.8 / 3.3 / 15.8 |  |
| SAM launcher | sam_launcher | AntiAir | Light | 5 | 1000 | = | 11.0 / 2.8 / 34.1 / 3.3 |  |
| Fortification sapper | sapper | Support | Light | 5 | 2000 | = | 11.0 / 2.8 / 3.3 / 3.3 |  |
| Artillery | artillery | Artillery | Artillery | 6 | 750 | = | 13.2 / 4.7 / 2.8 / 8.7 |  |
| Anti-tank missile carrier | atgm_carrier | TankHunter | Armor | 6 | 1050 | = | 14.9 / 10.0 / 2.8 / 7.3 |  |
| Command vehicle | command_vehicle | Support | Light | 6 | 1400 | = | 9.2 / 2.3 / 2.8 / 2.8 |  |
| FPV drone carrier | fpv_carrier | TankHunter | Artillery → Armor | 6 | 1050 | = | 15.5 / 10.7 / 2.8 / 10.4 | branch by class |
| Recon drone | recon_drone | Plane | Air | 6 | 550 | = | 1.9 / 2.5 / 0.0 / 1.5 |  |
| Scout helicopter | scout_heli | Helicopter | Air | 6 | 750 | = | 18.0 / 6.7 / 3.5 / 13.0 |  |
| Tank destroyer | tank_destroyer | TankHunter | Armor | 6 | 1550 | = | 17.2 / 13.0 / 2.8 / 9.2 |  |
| Armoured bulldozer | armored_bulldozer | Heavy | new: Armor | 7 | 3250 | — | 11.9 / 5.9 / 2.4 / 20.0 | new card |
| Gun-missile air defence | heavy_aa | AntiAir | Light | 7 | 1200 | = | 12.6 / 3.1 / 54.6 / 3.1 |  |
| Loitering munition truck | lancet_truck | TankHunter | Armor | 7 | 950 | = | 10.0 / 4.8 / 2.4 / 4.9 |  |
| Main battle tank | main_battle_tank | Heavy | Armor | 7 | 2250 | = | 17.9 / 9.6 / 4.0 / 7.7 |  |
| Strike drone | strike_drone | Plane | Air | 7 | 650 | = | 11.5 / 12.2 / 0.0 / 15.0 |  |
| Wheeled tank hunter | wheeled_gun | TankHunter | Armor | 7 | 1100 | = | 12.3 / 10.7 / 1.6 / 7.2 |  |
| Shahed launcher truck | shahed_truck | Artillery | Artillery | 8 | 1000 | = | 12.8 / 5.2 / 2.1 / 10.9 |  |
| Turtle tank | turtle_tank | Tank | Armor | 8 | 3250 | = | 8.8 / 6.6 / 1.4 / 4.7 |  |
| Attack helicopter | attack_helicopter | Helicopter | Air | 9 | 1250 | = | 16.4 / 10.1 / 5.5 / 11.9 |  |
| BMPT Terminator | bmpt | Tank | Armor | 9 | 2875 | = | 18.1 / 8.9 / 3.9 / 9.2 |  |
| Heavy rocket artillery | heavy_rocket_artillery | Artillery | Artillery | 9 | 1050 | = | 15.4 / 7.1 / 1.8 / 15.7 |  |
| Iron Beam laser | iron_beam | AntiAir | Light | 9 | 1125 | = | 0.0 / 0.0 / 11.7 / 0.0 |  |
| Railgun truck | railgun_truck | TankHunter | Armor | 9 | 1050 | = | 5.6 / 7.5 / 0.0 / 4.5 |  |
| Thermobaric launcher | thermobaric_launcher | Artillery | Artillery | 9 | 2250 | = | 12.1 / 5.1 / 1.8 / 10.8 |  |
| Twin-barrel tank | twin_tank | Heavy | Armor | 9 | 2875 | = | 16.1 / 10.3 / 3.1 / 7.7 |  |
| Fighter jet | fighter_jet | Plane | Air | 10 | 1300 | = | 6.2 / 1.5 / 49.4 / 1.5 |  |
| Heavy tank | heavy_tank | Heavy | Armor | 10 | 4000 | = | 14.8 / 8.0 / 3.2 / 6.4 |  |
| Ballistic missile launcher | ballistic_launcher | Artillery | Artillery | 11 | 1125 | = | 9.8 / 4.1 / 1.5 / 8.7 |  |
| Long-range SAM | long_sam | AntiAir | Artillery → Light | 11 | 1100 | = | 0.0 / 0.0 / 10.2 / 0.0 | branch by class |
| Siege tank | siege_tank | Heavy | Artillery → Armor | 12 | 5500 | = | 8.2 / 3.3 / 1.4 / 14.3 | branch by class |
| Attack jet | attack_jet | Plane | Air | 13 | 1150 | = | 16.1 / 15.1 / 2.9 / 19.0 |  |
| Heavy gunship | gunship_heli | Helicopter | Air | 14 | 2750 | = | 21.7 / 15.5 / 3.0 / 14.9 |  |
| Ka-52 Alligator | heavy_attack_heli | Helicopter | Air | 14 | 3125 | = | 15.8 / 9.2 / 5.8 / 11.3 |  |
| Titan super tank | titan_tank | Heavy | Armor | 14 | 6500 | = | 13.9 / 11.4 / 2.0 / 7.8 |  |
| Tank buster | tank_buster | Plane | Air | 18 | 2250 | = | 15.3 / 17.8 / 2.3 / 14.7 |  |
| Heavy bomber | heavy_bomber | Plane | Air | 20 | 3750 | = | 21.1 / 12.7 / 1.0 / 31.6 |  |
| Stealth bomber | stealth_bomber | Plane | Air | 20 | 2250 | = | 12.7 / 7.6 / 0.0 / 19.0 |  |
| Sky gunship | sky_gunship | Plane | Air | 22 | 5000 | = | 18.1 / 9.3 / 0.0 / 17.5 |  |

The SP howitzer's damage a second in a duel (the lab's `ShootAndScootCostsLittleFire`): shoot-and-scoot
costs it nothing, since it moves while it reloads.

| SP howitzer | damage a second |
|---|---|
| held in place | 42 |
| shoot-and-scoot | 44 (+5.1%) |

The armoured bulldozer against the turtle tank and the heavy tank as a sponge (`TheBulldozerIsNoBetterSpongeThanTheTurtle`):

| card | CP | health | seconds alive a life (mixed fire) | a CP | (tank fire) | a CP |
|---|---|---|---|---|---|---|
| armored_bulldozer | 7 | 3250 | 33.3 | 4.76 | 17.6 | 2.52 |
| turtle_tank | 8 | 3250 | 33.3 | 4.17 | 17.0 | 2.13 |
| heavy_tank | 10 | 4000 | 42.8 | 4.28 | 20.0 | 2.00 |

## Prompt 8: elites against their base cards

Duel damage a second and time alive in a soak (480 s window), elite over base card, 3 seeds. Before:

| Elite | base | HP x | paper DPS x (best class) | duel DPS x | soak time x | power x (duel DPS x soak) | skills |
|---|---|---|---|---|---|---|---|
| elite_aa | aa_vehicle | 1.71 | 2.43 (Air) | 2.46 | 1.61 | 3.97 | elite_overdrive |
| elite_apc | ifv | 1.54 | 1.59 (Light) | 1.84 | 1.54 | 2.83 | elite_smoke, elite_emp |
| elite_attack_helicopter | attack_helicopter | 1.70 | 1.01 (Light) | 1.08 | 1.70 | 1.84 | elite_flares, elite_barrage |
| elite_grad | mlrs | 1.44 | 0.79 (Light) | 0.72 | 1.42 | 1.03 | elite_barrage |
| elite_heavy_tank | heavy_tank | 1.63 | 0.94 (Light) | 1.18 | 2.33 | 2.76 | elite_repair, elite_overdrive |
| elite_mbt | main_battle_tank | 1.67 | 1.11 (Light) | 1.28 | 1.86 | 2.38 | elite_shield, elite_smoke |
| elite_mlrs | mlrs | 1.72 | 1.31 (Light) | 1.74 | 1.64 | 2.86 | elite_barrage |
| elite_tank_destroyer | tank_destroyer | 1.45 | 1.18 (Light) | 1.50 | 1.40 | 2.10 | elite_barrage, elite_smoke |

After (the prompt 8 footing):

| Elite | base | HP x | paper DPS x (best class) | duel DPS x | soak time x | power x (duel DPS x soak) | skills |
|---|---|---|---|---|---|---|---|
| elite_aa | aa_vehicle | 1.60 | 1.31 (Air) | 1.39 | 1.51 | 2.11 | elite_overdrive |
| elite_apc | ifv | 1.60 | 1.25 (Light) | 1.33 | 1.60 | 2.12 | elite_emp |
| elite_artillery | artillery | 1.60 | 1.15 (Light) | 1.29 | 1.64 | 2.12 | elite_barrage |
| elite_attack_helicopter | attack_helicopter | 1.60 | 1.22 (Light) | 1.28 | 1.61 | 2.06 | elite_flares, elite_barrage |
| elite_attack_jet | attack_jet | 1.60 | 1.00 (Structure) | 1.00 | 2.18 | 2.18 | elite_flares |
| elite_fpv_carrier | fpv_carrier | 1.60 | 1.10 (Light) | 1.31 | 1.68 | 2.20 | elite_barrage |
| elite_grad | mlrs | 1.60 | 1.01 (Light) | 1.37 | 1.58 | 2.15 | elite_barrage |
| elite_heavy_tank | heavy_tank | 1.60 | 1.23 (Light) | 1.30 | 1.67 | 2.17 | elite_overdrive |
| elite_long_sam | long_sam | 1.60 | 1.20 (Air) | 1.20 | 1.76 | 2.12 | elite_overdrive |
| elite_mbt | main_battle_tank | 1.60 | 1.24 (Light) | 1.22 | 1.75 | 2.13 | elite_shield |
| elite_mlrs | mlrs | 1.60 | 0.95 (Light) | 1.17 | 1.57 | 1.84 | elite_barrage |
| elite_tank_destroyer | tank_destroyer | 1.60 | 1.23 (Light) | 1.48 | 1.49 | 2.20 | elite_barrage, elite_smoke |
