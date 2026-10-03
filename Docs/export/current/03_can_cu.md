# 03_can_cu — Căn cứ và tháp

Tháp và nhánh, tường, nhà chính, mô-đun tiện ích, xây lại, AI căn cứ.

Gói cân bằng Machine Brigade, commit 5f613736, ngày 2026-10-03. Số liệu đầy đủ ở 03_can_cu.xlsx; file này chỉ nêu luật, giải thích, lý do thiết kế, tham khảo và bảng nhỏ (tối đa 20 dòng, bảng lớn: xem sheet).

## Căn cứ và tháp

Căn cứ là một loadout chọn trước trận như bộ bài: sở chỉ huy (HQ) cấp 1–5 và các ô tháp theo cỡ **nhỏ / vừa / lớn** trên bản đồ căn cứ của từng map. Tháp cỡ nào vào ô cỡ đó hoặc ô to hơn; ô tiện ích nhận mô-đun. Tháp bị phá được thả dù lại trong trận (trả CP, có hồi chiêu; tháp nhỏ rẻ và nhanh hơn). Mỗi cứ điểm có tiền đồn 1 ô nhỏ + 1 ô vừa. Vai trò căn cứ theo chế độ: chỗ dựa (sở chỉ huy không bị phá) hoặc mục tiêu.

**Vai trò tháp nhỏ:** tháp canh thấy tàng hình và tăng 10% tầm cho tháp trong 25 m (nhánh Tháp quan sát: 15% trong 30 m, thay mức 10%, không cộng dồn); tháp phòng không nhỏ +25% sát thương lên drone và trực thăng. **Điểm yếu tháp pháo:** xoay chậm, nạp lâu, súng đồng trục không bắn máy bay. **AI** đọc căn cứ địch và mua quân khắc chế. **Thẻ tháp** lên hạng như xe; từ hạng 7 chọn 1 trong 2 nhánh (đổi nhánh 800 xu). **Trang bị tháp:** 3 ô (Vũ khí, Kết cấu, Hệ thống) dùng chung cho mọi tháp cùng loại trong căn cứ.

### Thẻ tháp (22)

Bảng 22 dòng: số liệu đầy đủ ở các sheet của mục này trong file xlsx cùng tên.

### Mô-đun tiện ích (9)

| Mô-đun | Tác dụng |
|---|---|
| **Sân bay dã chiến** | **Sân bay dã chiến · mô-đun tiện ích** Cách đánh: máy bay bay trên nó hồi 3% máu mỗi giây và nạp đạn; chúng về đây khi hết đạn (không còn bay về vì bị thương). Mạnh / yếu: giúp trực thăng và máy bay… |
| **Sân bay dã chiến · Nhà chứa máy bay** |  |
| **Sân bay dã chiến · Phục vụ nhanh** |  |
| **Kho đạn** | **Kho đạn · mô-đun tiện ích** Cách đánh: xe nạp đạn tại căn cứ nhanh gấp đôi. Mạnh / yếu: rất hợp với giàn phóng và pháo binh hay hết đạn; nổ rất mạnh khi bị phá. Mẹo: mang theo khi bộ bài nhiều pháo… |
| **Trung tâm điều khiển hỏa lực** | **Trung tâm điều khiển hỏa lực · mô-đun tiện ích · liên kết tháp** Cách đánh: tháp trong 30 m gây thêm 12% sát thương và dồn hỏa lực vào một mục tiêu. Mạnh / yếu: biến cụm tháp thành một khối; vô dụn… |
| **Trạm hậu cần** | **Trạm hậu cần · mô-đun tiện ích** Cách đánh: mức tiếp tế của quân ta tăng thêm 8 CP: thu nhập chỉ giảm khi quân vượt mức tiếp tế. Mạnh / yếu: cho đội quân lớn giữ nguyên thu nhập; vô ích với đội quâ… |
| **Trạm radar** | **Trạm radar · mô-đun tiện ích** Cách đánh: mọi thứ trong căn cứ đều lộ, kể cả tàng hình và ẩn nấp, và pháo địch khai hỏa trong 120 m bị lộ 8 giây. Mạnh / yếu: làm lộ oanh tạc cơ tàng hình và pháo ẩn… |
| **Xưởng sửa chữa** | **Xưởng sửa chữa · mô-đun tiện ích** Cách đánh: xe trong vòng 35 m quanh sở chỉ huy hồi 1,5% máu mỗi giây, kể cả giữa trận. Mạnh / yếu: giữ quân phòng thủ đứng vững; không giúp gì xe ở ngoài chiến tr… |
| **Máy tạo nhiễu tầm nhìn** | **Máy tạo nhiễu tầm nhìn · mô-đun tiện ích · che căn cứ** Cách đánh: địch không thấy gì của ta trong 35 m quanh nó nếu xa hơn 15 m, trừ trinh sát. Mạnh / yếu: pháo binh không tìm được thứ nó che; tri… |

### Đo cân bằng căn cứ

Căn cứ mặc định (pháo đài hạng nặng + ụ pháo; tháp pháo, giàn rocket, tháp ATGM; mỗi loại 2 tháp canh, phòng không, súng máy) đạt 1,86 trước quân hỗn hợp, cao hơn mọi căn cứ chỉ một loại tháp (tốt nhất 1,79); không căn cứ một loại nào mạnh nhất trước mọi loại quân. Tỷ lệ chọn tháp nhỏ trong ô nhỏ (tối ưu tham lam): tháp canh 32%, phòng không 22%, súng máy 19%, răng rồng 11%, EW 10%, bãi mìn 7% → bãi mìn được tăng lên 8 quả, rải lại mỗi 45 giây. Quân pháo binh đứng ngoài tầm tháp thắng mọi căn cứ nếu căn cứ đứng một mình: câu trả lời là quân và phản pháo.

### Hệ căn cứ / The base system

Sinh từ dữ liệu (balance.json, các file bản đồ). / Generated from the data (balance.json, the map files).

### Roster 22 tháp và nhánh / The 22-tower roster and its branches

Bảng 22 dòng: số liệu đầy đủ ở các sheet của mục này trong file xlsx cùng tên.

Hai nhánh của một tháp khác nhau về việc làm (towerRole riêng), không chỉ về số. / The two branches of a card differ in what they do (their own towerRole), not only in numbers.

### Xây lại tháp / Rebuilding towers

Không gọi khi xe địch trong 20 m; nhà chính còn 25% máu: tháp nhỏ hoặc vừa rẻ nhất đã đổ xây lại miễn phí, một lần; Đối công: không xây lại sau 600 s. Giá riêng từng tháp (rebuildCp) ở bảng 6a. / No drop with an enemy within 20 m; at 25% HQ health the cheapest fallen small or medium tower comes back free, once; Showdown: no rebuilding after 600 s. Each tower's own price (rebuildCp) is in table 6a.

### Tường / Walls

Tối đa 2 tuyến mỗi trại, 3 tuyến lùi ở Phòng thủ; 3-5 đoạn 12 x 2 m mỗi tuyến; 75 bản đồ, 279 tuyến, 1079 đoạn. INTACT/RUBBLE theo trạng thái NavGrid dựng sẵn, đổi ở tick sau khi đoạn bị phá; gạch vụn đi qua được, chậm 20%. Xe phá tường x1.5 chỉ lên tường. Đội AI chọn cổng hay phá tường theo routeCost + threatCost + breachTimeCost. AI địch: brandt t_wall, kessler t_wall, varga gun_wall, default hesco. / Up to 2 lines a camp, 3 fall-back lines in Defend; 3-5 segments of 12 x 2 m a line; 75 maps, 279 lines, 1079 segments. INTACT/RUBBLE on prebuilt NavGrid states, switched at the tick after a segment falls; rubble is passable, 20% slower. Wall breakers x1.5 on walls only. AI squads choose the gate or a breach by routeCost + threatCost + breachTimeCost (aiModeProfile wallRoute).

### Kiểu nhà chính / HQ types

Một kỹ năng, hồi 120 s, một nút trên HUD. AI: brandt fortress, kessler fortress, varga garrison, orlov shield, aurel shield, Easy garrison, Normal fortress, Hard shield, VeryHard fortress. / One skill, 120 s cooldown, one HUD button.

### Phòng thủ / Vô tận theo cấp nhà chính / Defend and Endless by HQ level

Sức đợt = ReferenceBasePower(cấp nhà chính) x độ khó x đường cong đợt x tiến độ chiến dịch. / Wave strength = ReferenceBasePower(HQ level) x difficulty x wave curve x campaign progress. Căn cứ tham chiếu / The reference bases:

| HQ | Nhỏ / Small | Vừa / Medium | Lớn / Large | Mô-đun / Modules |
|---|---|---|---|---|
| 1 | guard_tower, mg_bunker, aa_turret | gun_turret |  | repair_bay |
| 2 | guard_tower, mg_bunker, aa_turret, at_gun_emplacement | gun_turret, atgm_tower |  | repair_bay |
| 3 | guard_tower, mg_bunker, aa_turret, at_gun_emplacement | gun_turret, heavy_flak_tower | heavy_turret | repair_bay, radar_station |
| 4 | guard_tower, mg_bunker, aa_turret, at_gun_emplacement, minefield | gun_turret, atgm_tower, heavy_flak_tower | heavy_turret | repair_bay, radar_station |
| 5 | guard_tower, mg_bunker, aa_turret, at_gun_emplacement, minefield, ew_tower | gun_turret, atgm_tower, c_ram | heavy_turret, missile_battery | repair_bay, radar_station, ammo_depot |

### Chế độ Đối công / Showdown

| Trường / Field | Luật / Rule |
|---|---|
| winCondition | Phá nhà chính đối phương |
| loseCondition | Mất nhà chính |
| timeLimit | 12 phút |
| overtimeRule | Hết 12 phút: bên có nhà chính còn nhiều % máu hơn từ 5 điểm phần trăm trở lên thắng ngay; chênh dưới 5 điểm → đột tử 90 s (tắt chống bắn tỉa, không xây lại tháp, thu nhập ×2, không đặt lại hồi chiêu… |
| drawRule | Bằng nhau sau đột tử → hòa |
| scoreRule | Không có điểm phụ |
| catchUpPolicy | Chỉ bắt kịp thu nhập, trần +25%; không tiếp viện miễn phí |
| antiSnipeRule | Nhà chính chỉ nhận 25% sát thương từ pháo binh, tên lửa và máy bay bắn từ ngoài 60 m, cho tới khi outerDefenseBreached |
| breachRule | outerDefenseBreached khi quân mặt đất địch vào qua cổng chính (cổng trại là lối mở), hoặc một đoạn tường ngoài thành RUBBLE và mở được đường từ phía công vào trong căn cứ (kiểm bằng trạng thái NavGri… |
| escalation | Phút 6: thu nhập ×1,5 cho cả hai phe, trạm CP ngừng tạo CP; phút 10: tháp bị phá không xây lại (lần đã trừ CP thì hoàn tất) |
| mapEligibility | Chỉ bản đồ 300×300 đạt ngưỡng đối xứng của docs/checks/map_audit.md (không dùng 300×480) |

timeLimit 720, antiSnipeShare 0.25, antiSnipeRange 60, escalationAt 360, escalationIncome 1.5, rebuildCutoff 600, overtimeLead 0.05, suddenDeath 90, suddenDeathIncome 2, catchUpMax 0.25, baseRadius 46, neutralsMax 2

Bản đồ (300 x 300 đối xứng) / Maps (300 x 300 symmetric): ashfield, capital, coralisles, dunebreak, foundry, frostpeak, greenvale, ironport, junglepass, landingbeach, launchsite, lighthousebay, metrocity, openpit, orbitalgate, redrock, rustyard, saltflat, skyhold, swamp, veyra_old_quarter, whiteout.

### CP khởi đầu và đội mở màn / Starting CP and opening squads

CP khởi đầu x1.16 ở Conquest, Deathmatch, KingOfTheHill, Assault, Siege, Weekly, Defend, Endless, Survival, BossRush, Campaign, Showdown. Đội mở màn: mỗi vai lấy thẻ rẻ nhất của bộ bài, tối đa 60% CP khởi đầu. / Starting CP x1.16 in those modes; each role takes the deck's cheapest card of the role, within 60% of the starting CP.

| Chỉ huy / Commander | Vai / Roles |
|---|---|
| kade | mbt, scout |
| lind | engineer, repair, light |
| reyes | scout_heli, scout |
| kerr | scout, radar_scout, light |
| venn | fpv, scout |
| mendez | wheeled, light_tank, scout |
| brandt | bunker, engineer |
| dahl | artillery, scout |
| brenn | - |
| adler | scout, light |
| varro | cheap4, cheap4, cheap4 |
| reyn | mbt |
| quist | fortify, light, scout |
| okoye | - |

| Tướng địch / Enemy general | Vai / Roles |
|---|---|
| varga | tank |
| orlov | artillery, radar_scout |
| kessler | mine_layer, light |
| wolff | heli |
| sen | drone |
| venn | drone |
| thorne | mbt |
| aurel | heavy |
| default | scout, light |

Sheet 03_can_cu/Thap_vu_khi — Tháp: bệ vũ khí phụ (3 dòng, 8 cột)

| id | thap_id | thu_tu | weapon | aim | slot |
|---|---|---|---|---|---|
| aa_turret/0 | aa_turret | 0 | sam | Turret | missile |
| heavy_turret.bastion/0 | heavy_turret.bastion | 0 | hmg_roof | Free | gun |
| heavy_turret.bastion/1 | heavy_turret.bastion | 1 | hmg_roof | Free | gun |

Sheet 03_can_cu/Tuong — Tường (3 dòng, 81 cột)

| id | ten_en | ten_vi | ten_ngan_vi | base_cp | mau_hp | mau_trong_tran_hp | giap_hong | giap_noc | cong_trinh |
|---|---|---|---|---|---|---|---|---|---|
| wall_gun | Gun wall | Tường gắn súng | Tường súng | 0 | 2880 | 6336.0 | 3 | 3 | TRUE |
| wall_hesco | HESCO wall | Tường HESCO | HESCO | 0 | 2400 | 5280.0 | 3 | 3 | TRUE |
| wall_t | T-wall | Tường chữ T | Tường T | 0 | 3840 | 8448.0 | 4 | 4 | TRUE |

*In 10 / 81 cột; 38 cột khác: xem sheet.*

Sheet 03_can_cu/Tuong_luat — Tường: luật (11 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so | gia_tri_chu |
|---|---|---|---|---|
| ai.brandt | base.walls | brandt |  | t_wall |
| ai.default | base.walls | default |  | hesco |
| ai.kessler | base.walls | kessler |  | t_wall |
| ai.varga | base.walls | varga |  | gun_wall |
| breakerMultiplier | base.walls | breakerMultiplier | 1.5 |  |
| breakers | base.walls | breakers |  | armored_bulldozer;engineer_vehicle;demolition_line_vehicle |
| campLines | base.walls | campLines | 2 |  |
| default | base.walls | default |  | hesco |
| fortressLines | base.walls | fortressLines | 3 |  |
| rubbleSlow | base.walls | rubbleSlow | 0.2 |  |
| segmentHp | base.walls | segmentHp | 2400 |  |

Sheet 03_can_cu/Nha_chinh — Nhà chính (4 dòng, 84 cột)

| id | ten_en | ten_vi | ten_ngan_vi | lop | ke_thua_tu | base_cp | mau_hp | mau_trong_tran_hp | giap_hong |
|---|---|---|---|---|---|---|---|---|---|
| headquarters | Headquarters | Sở chỉ huy | Sở chỉ huy | Defense |  | 0 | 9000 | 19800.0 | 4 |
| headquarters.fortress_air | Headquarters · AA Fortress | Sở chỉ huy · Pháo đài phòng không | Pháo đài PK | Defense | headquarters | 0 | 9000 | 19800.0 | 4 |
| headquarters.fortress_ground | Headquarters · Fortress | Sở chỉ huy · Pháo đài | SCH Pháo đài | Defense | headquarters | 0 | 9000 | 19800.0 | 4 |
| headquarters.shield | Headquarters · Shield | Sở chỉ huy · Lá chắn | SCH Lá chắn | Defense | headquarters | 0 | 9000 | 19800.0 | 4 |

*In 10 / 84 cột; 46 cột khác: xem sheet.*

Sheet 03_can_cu/Nha_chinh_kieu — Nhà chính: kiểu (3 dòng, 14 cột)

| id | nha_chinh | ai_air_share | air | barrage | charges | clear | dome_seconds_s | ground | hq |
|---|---|---|---|---|---|---|---|---|---|
| fortress | headquarters.fortress_ground;headquarters.fortress_air | 0.3 | headquarters.fortress_air | hq_barrage |  |  |  | headquarters.fortress_ground |  |
| garrison |  |  |  |  |  | 30 |  |  |  |
| shield | headquarters.shield |  |  |  | 4 |  | 10 |  | headquarters.shield |

*In 10 / 14 cột; 2 cột khác: xem sheet.*

Sheet 03_can_cu/Mo_dun_tien_ich — Mô-đun tiện ích (9 dòng, 101 cột)

| id | ten_en | ten_vi | ten_ngan_vi | base_cp | mau_hp | mau_trong_tran_hp | giap_hong | giap_noc | cong_trinh |
|---|---|---|---|---|---|---|---|---|---|
| airfield | Airfield | Sân bay dã chiến | Sân bay | 0 | 1600 | 3520.0 | 1 | 1 | TRUE |
| airfield.hangar |  |  | Nhà chứa | 0 | 1800 | 3960.0 | 2 | 2 | TRUE |
| airfield.service |  |  |  | 0 | 1600 | 3520.0 | 1 | 1 | TRUE |
| ammo_depot | Ammunition depot | Kho đạn | Kho đạn | 0 | 1200 | 2640.0 | 2 | 2 | TRUE |
| fire_control_centre | Fire-control centre | Trung tâm điều khiển hỏa lực | TT hỏa lực | 0 | 1136 | 2499.2 | 1 | 1 | TRUE |
| logistics_station | Logistics station | Trạm hậu cần | Trạm hậu cần | 0 | 1400 | 3080.0 | 1 | 1 | TRUE |
| radar_station | Radar station | Trạm radar | Trạm radar | 0 | 1200 | 2640.0 | 1 | 1 | TRUE |
| repair_bay | Repair bay | Xưởng sửa chữa | Xưởng sửa chữa | 0 | 1600 | 3520.0 | 2 | 2 | TRUE |
| visual_jammer | Visual jammer | Máy tạo nhiễu tầm nhìn | Nhiễu tầm nhìn | 0 | 909 | 1999.8 | 1 | 1 | TRUE |

*In 10 / 101 cột; 58 cột khác: xem sheet.*

Sheet 03_can_cu/Loadout_can_cu — Ô căn cứ theo cấp HQ (10 dòng, 9 cột)

| id | bang | cap_hq | large | medium | small | utility |
|---|---|---|---|---|---|---|
| levels/1 | levels | 1 | 0 | 1 | 3 | 1 |
| levels/2 | levels | 2 | 0 | 2 | 4 | 1 |
| levels/3 | levels | 3 | 1 | 2 | 4 | 2 |
| levels/4 | levels | 4 | 1 | 3 | 5 | 2 |
| levels/5 | levels | 5 | 2 | 3 | 6 | 3 |
| longLevels/1 | longLevels | 1 | 0 | 1 | 4 | 1 |
| longLevels/2 | longLevels | 2 | 1 | 2 | 5 | 1 |
| longLevels/3 | longLevels | 3 | 1 | 3 | 6 | 2 |
| longLevels/4 | longLevels | 4 | 2 | 4 | 7 | 3 |
| longLevels/5 | longLevels | 5 | 3 | 5 | 8 | 4 |

Sheet 03_can_cu/Xay_lai — Xây lại tháp theo cỡ ô (3 dòng, 6 cột)

| id | cooldown_s | cp | drop |
|---|---|---|---|
| large | 60 | 7 | 5 |
| medium | 40 | 4 | 3.5 |
| small | 25 | 2 | 2.5 |

Bảng đầy đủ: xem sheet `Thap` (76 dòng), `Thap_gia_cong_thuc` (60 dòng), `Can_cu_luat` (21 dòng).

## Công thành và Phòng thủ

- **Pháo đài chiếm 45% chiến trường** ở góc đông bắc: tuyến ngoài (trạm radar), tường chữ L có cổng chính đóng và cửa phụ mở, thành trong có sở chỉ huy. Tháp đặt trên ô có cỡ theo roster tháp mới, lấy từ loadout của phe giữ (AI theo độ khó và tướng); vòng trong mạnh hơn.
- **Set-piece:** tường sập có hoạt cảnh rồi thành đống gạch đi qua được; cổng thép bị phá đổ vào trong; máy phát khiên giữ vòm khiên che thành trong, phá máy cuối cùng thì vòm tắt kèm chớp sáng; siêu pháo bắn theo đồng hồ đếm ngược vào cụm quân đông nhất (phá nó là mục tiêu phụ: 25 CP, 100 xu); đèn pha quét và còi báo động ban đêm; chi viện địch đến bằng tàu hỏa trên đường ray hoặc máy bay vận tải hạ cánh trên đường băng, báo trước 10 giây.
- **Phòng thủ:** ba tuyến ngoài, giữa, trong và sở chỉ huy là trận chốt cuối. Mất một tuyến thì tháp ở đó nổ và người chơi được thưởng CP rút lui (24 rồi 32 CP); tuyến trong có tháp mạnh hơn. Căn cứ dùng đúng loadout của người chơi. Đợt địch kế tiếp hiện trước bằng icon và số lượng (đợt được lên kế hoạch trước nên đúng y như thứ đổ bộ); đợt là bầy xe rẻ lớn dần, trần 48 xe cùng lúc.
- **Đầm Lầy và Quần Đảo San Hô** giữ pháo đài kiểu cũ ở góc: tường mới sẽ cắt mọi đường đắp của hai bản đồ này.
- **Đo (độ khó Thường, 5 seed):** Công thành thắng 5/5 (9,7–17,8 phút); Phòng thủ giữ 3/5 trên 5 bản đồ và 5/5 ở bài kiểm tra kết thúc trận; Vô tận: sở chỉ huy rơi ở phút 10,3–11,7.

Sheet 03_can_cu/Dot_phong_thu — Loadout phòng thủ tham chiếu (5 dòng, 10 cột)

| id | small | medium | large | utilities | he_so_do_kho | duong_cong_dot | cap_hq |
|---|---|---|---|---|---|---|---|
| hq1 | guard_tower;mg_bunker;aa_turret | gun_turret |  | repair_bay | NEED_CODE_CHECK | NEED_CODE_CHECK | 1 |
| hq2 | guard_tower;mg_bunker;aa_turret;at_gun_emplacement | gun_turret;atgm_tower |  | repair_bay | NEED_CODE_CHECK | NEED_CODE_CHECK | 2 |
| hq3 | guard_tower;mg_bunker;aa_turret;at_gun_emplacement | gun_turret;heavy_flak_tower | heavy_turret | repair_bay;radar_station | NEED_CODE_CHECK | NEED_CODE_CHECK | 3 |
| hq4 | guard_tower;mg_bunker;aa_turret;at_gun_emplacement;minefield | gun_turret;atgm_tower;heavy_flak_tower | heavy_turret | repair_bay;radar_station | NEED_CODE_CHECK | NEED_CODE_CHECK | 4 |
| hq5 | guard_tower;mg_bunker;aa_turret;at_gun_emplacement;minefiel… | gun_turret;atgm_tower;c_ram | heavy_turret;missile_battery | repair_bay;radar_station;ammo_depot | NEED_CODE_CHECK | NEED_CODE_CHECK | 5 |

Sheet 03_can_cu/Can_cu_AI_cap — AI xây căn cứ: cấp HQ theo độ khó (4 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so |
|---|---|---|---|
| Easy | base.ai.levels | Easy | 2 |
| Hard | base.ai.levels | Hard | 5 |
| Normal | base.ai.levels | Normal | 3 |
| VeryHard | base.ai.levels | VeryHard | 5 |

## Tham khảo ngoài đời và game

Thông số ngoài đời lấy từ nguồn trong repo (sheet Nguon_tham_chieu của 08_tham_chieu); chỗ chưa có nguồn ghi NEED_SOURCE, không điền từ trí nhớ.

### Can_cu_tham_chieu

96 dòng. Độ tin cậy: da_kiem_chung 0, uoc_dinh 22, ban_dau_doan 44, NEED_SOURCE 30. Loại: NEED_SOURCE 30, doi_that 63, game 3.

- `aa_turret` (Tháp phòng không): mẫu thật: 2K22 Tunguska (2A38 30 mm);Stinger; game: WARNO; giống: pháo phòng không hai nòng 35 mm trên ụ bao cát; độ tin: uoc_dinh; nguồn: R_unit_refs, R_machine_brigade_can_bang, R_aa_turret, R_machine_brigade_ai_research.
- `aa_turret.flak` (aa_turret.flak): mẫu thật: ZSU-23-4 Shilka (23 mm bốn nòng); giống: Nhánh pháo phòng không bốn nòng; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_machine_brigade_can_bang.
- `aa_turret.sam` (aa_turret.sam): mẫu thật: Mistral ATLAS;RBS-70;Starstreak LML; giống: Nhánh trạm tên lửa phòng không; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_machine_brigade_can_bang.
- `airfield` (Sân bay dã chiến): mẫu thật: bãi đáp trực thăng (chữ H); giống: Bãi đáp sửa chữa và nạp đạn cho máy bay; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_machine_brigade_can_bang.
- `airfield.hangar` (airfield.hangar): mẫu thật: nhà chứa máy bay dã chiến; giống: nhánh nhà chứa; độ tin: uoc_dinh; nguồn: R_unit_refs, R_machine_brigade_can_bang.
- `airfield.service` (airfield.service): mẫu thật: FARP (điểm tiếp đạn và nhiên liệu tiền phương); giống: nhánh phục vụ máy bay; độ tin: uoc_dinh; nguồn: R_unit_refs, R_machine_brigade_can_bang.
- `ammo_depot` (Kho đạn): mẫu thật: kho đạn dã chiến dưới lưới ngụy trang; giống: Kho đạn, nổ lớn khi bị phá; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_machine_brigade_can_bang.
- `artillery_emplacement` (Trận địa pháo): mẫu thật: 2A65 Msta-B / D-20 152 mm (lựu pháo kéo);M284 155 mm; game: WARNO; giống: lựu pháo kéo trong ụ bao cát; độ tin: uoc_dinh; nguồn: R_unit_refs, R_machine_brigade_can_bang, R_artillery_emplacement, R_machine_brigade_ai_research.
- `artillery_emplacement.cb` (artillery_emplacement.cb): mẫu thật: M284 155 mm; giống: Nhánh lựu pháo phản pháo; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_machine_brigade_can_bang.
- `artillery_emplacement.mortar` (artillery_emplacement.mortar): mẫu thật: 2B8 240 mm;2S4 Tyulpan;M-240 (cối kéo 240 mm); giống: Nhánh cối 240 mm bắn cầu vồng; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_machine_brigade_can_bang.
- `at_gun_emplacement` (Ụ pháo chống tăng): mẫu thật: 2A45 Sprut-B 125 mm; game: Company of Heroes; giống: Ụ pháo chống tăng; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_at_gun_emplacement.
- `atgm_tower` (Tháp tên lửa chống tăng): mẫu thật: 9M133 Kornet; giống: Tháp bê tông phóng tên lửa chống tăng; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_machine_brigade_can_bang, R_atgm_tower.
- `atgm_tower.multi` (atgm_tower.multi): mẫu thật: 9M133 Kornet;Kornet-EM (bệ nhiều ống); giống: ước đoán (Kornet-EM): nhánh đa năng bốn ống và radar nhỏ; độ tin: uoc_dinh; nguồn: R_unit_refs, R_machine_brigade_can_bang.
- `atgm_tower.top` (atgm_tower.top): mẫu thật: 9M133 Kornet;FGM-148 Javelin (đánh nóc); giống: ước đoán (Javelin): nhánh tên lửa đánh nóc; độ tin: uoc_dinh; nguồn: R_unit_refs, R_machine_brigade_can_bang.
- `barrage_balloon` (Khí cầu neo radar (JLENS)): mẫu thật: JLENS (khí cầu neo radar); giống: Khí cầu neo radar: bom địch kém chính xác, lộ máy bay tàng hình gần; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_barrage_balloon.
- … 51 dòng có tham chiếu nữa: xem sheet Can_cu_tham_chieu.

Nguồn được dùng (tiêu đề như repo ghi; link khi repo có):

- `R_aa_turret`: spec dựng lại aa_turret (độ tin 3)
- `R_artillery_emplacement`: spec dựng lại artillery_emplacement (độ tin 3)
- `R_at_gun_emplacement`: spec dựng lại at_gun_emplacement (độ tin 3)
- `R_atgm_tower`: spec dựng lại atgm_tower (độ tin 3)
- `R_barrage_balloon`: spec dựng lại barrage_balloon (độ tin 3)
- `R_bulwark_post`: spec dựng lại bulwark_post (độ tin 3)
- `R_c_ram`: spec dựng lại c_ram (độ tin 3)
- `R_coastal_battery`: spec dựng lại coastal_battery (độ tin 3)
- `R_cp_relay`: spec dựng lại cp_relay (độ tin 3)
- `R_decisions`: Docs/DECISIONS.md (nhật ký quyết định) (độ tin 3)
- `R_dragons_teeth`: spec dựng lại dragons_teeth (độ tin 3)
- `R_drone_hangar`: spec dựng lại drone_hangar (độ tin 3)
- `R_ew_tower`: spec dựng lại ew_tower (độ tin 3)
- `R_gun_turret`: spec dựng lại gun_turret (độ tin 3)
- `R_headquarters`: spec dựng lại headquarters (độ tin 3)
- `R_heavy_flak_tower`: spec dựng lại heavy_flak_tower (độ tin 3)
- `R_heavy_turret`: spec dựng lại heavy_turret (độ tin 3)
- `R_logistics_station`: spec dựng lại logistics_station (độ tin 3)
- `R_machine_brigade_ai_research`: Nghiên cứu AI (Machine_Brigade_AI_Research.xlsx) (độ tin 3)
- `R_machine_brigade_can_bang`: Rà soát cân bằng (Machine_Brigade_Can_bang.xlsx) (độ tin 3)
- `R_mg_bunker`: spec dựng lại mg_bunker (độ tin 3)
- `R_minefield`: spec dựng lại minefield (độ tin 3)
- `R_repair_bay`: spec dựng lại repair_bay (độ tin 3)
- `R_rocket_turret`: spec dựng lại rocket_turret (độ tin 3)
- `R_shield_tower`: spec dựng lại shield_tower (độ tin 3)
- `R_super_gun`: spec dựng lại super_gun (độ tin 3)
- `R_targeting_station`: spec dựng lại targeting_station (độ tin 3)
- `R_unit_refs`: unit_refs.json (tham chiếu ngoài đời / phim / game theo đơn vị) (độ tin 3)
- `R_wall_hesco`: spec dựng lại wall_hesco (độ tin 3)
- `R_wall_t`: spec dựng lại wall_t (độ tin 3)

Sheet 03_can_cu/Can_cu_so_sanh_that — Căn cứ và tháp: so sánh với thật: 37 dòng, 18 cột; bảng đầy đủ: xem sheet Can_cu_so_sanh_that.

## Các sheet của file

Mọi sheet, số dòng và ý nghĩa cột nằm trong 00_index.xlsx (Muc_luc_sheet, Schema). Sheet `input_<tên>` là bản chép của một sheet nguồn để công thức Excel đọc cùng file; sửa ở sheet nguồn, không sửa bản chép.

- `Thap` (76 dòng): Tháp — Mỗi tháp (thẻ và nhánh bậc 7) một dòng
- `Thap_vu_khi` (3 dòng): Tháp: bệ vũ khí phụ — secondary[]: bệ phụ (chỉ số bệ = thu_tu + 1; bệ 0 là vũ khí chính)
- `Tuong` (3 dòng): Tường — Mỗi loại tường một dòng (def + base.walls.types)
- `Tuong_luat` (11 dòng): Tường: luật — base.walls: xe phá tường, máu đoạn, số tuyến, mặc định, tường theo tướng
- `Nha_chinh` (4 dòng): Nhà chính — Nhà chính và các kiểu (fortress / shield...)
- `Nha_chinh_vu_khi` (11 dòng): Nhà chính: bệ vũ khí phụ — secondary[]: bệ phụ (chỉ số bệ = thu_tu + 1; bệ 0 là vũ khí chính)
- `Nha_chinh_kieu` (3 dòng): Nhà chính: kiểu — hqTypes.<kiểu>: trường không theo cấp
- `Nha_chinh_kieu_cap` (15 dòng): Nhà chính: kiểu x cấp HQ — hqTypes.<kiểu>.<danh sách>[cấp-1]: sức mạnh, đồn trú, khiên theo HQ 1-5
- `Nha_chinh_luat` (13 dòng): Nhà chính: luật — base.hq, hqTypes.default / skillCooldown / radius / ai (kiểu theo tướng, độ khó)
- `Mo_dun_tien_ich` (9 dòng): Mô-đun tiện ích — Trạm sửa, kho đạn, sân bay, trạm hậu cần, radar (ô tiện ích)
- `Loadout_can_cu` (10 dòng): Ô căn cứ theo cấp HQ — base.levels (thường) và base.longLevels (bản đồ dài): số ô mỗi cỡ
- `Xay_lai` (3 dòng): Xây lại tháp theo cỡ ô — base.rebuild.<cỡ>: CP, thời gian chờ, thời gian thả
- `Can_cu_luat` (21 dòng): Căn cứ: luật — base.rebuild (chung), longForward, outpost, roles (vai trò căn cứ theo chế độ), roster
- `Dot_phong_thu` (5 dòng): Loadout phòng thủ tham chiếu — base.reference: 5 loadout tham chiếu theo cấp HQ
- `Can_cu_AI_kieu` (112 dòng): AI xây căn cứ: trọng số — base.ai.styles.<kiểu>.<tháp>: trọng số chọn tháp ('*' = mọi tháp khác)
- `Thap_gia_cong_thuc` (60 dòng): Tháp: công thức giá xây lại — Từng bước giá xây lại (Tools/balance/p32_tower_prices.py): effectiveHP, roleDPS, equivalentCP, hệ số đứng yên, x 1,25, cận cỡ; so với giá game (BaseR…
- `Tuong_duong_xe_cong_trinh` (60 dòng): Tháp: tương đương xe — Giá trị tương đương xe (equivalentCP), tỷ lệ so với giá game, số phát của từng mối đe dọa tham chiếu theo cỡ ô để hạ tháp (DamageTable.Effective, Str…
- `Nha_chinh_so_sanh` (20 dòng): Nhà chính: so sánh kiểu — Giá trị phòng thủ tương đương mỗi phút căn cứ bị đánh (CP), 3 kiểu (Pháo đài mặt đất / phòng không, Đồn trú, Khiên) x HQ 1-5 (Tools/balance/p32_hq_ty…
- `Can_cu_AI_cap` (4 dòng): AI xây căn cứ: cấp HQ theo độ khó — base.ai.levels
- `Can_cu_tham_chieu` (96 dòng): Căn cứ và tháp: tham chiếu ngoài đời — Mỗi tháp / nhánh, tường, nhà chính, mô-đun một dòng: mẫu thật, game tham khảo cơ chế, kích thước thật (spec 12.2; chỉ dữ liệu có trong repo)
- `Can_cu_so_sanh_that` (37 dòng): Căn cứ và tháp: so sánh với thật — So sánh game với thật (spec 12.4): mỗi thông số có đối chiếu một dòng; ty_le = game / thật, khoảng cho phép, co_lech_lon = ngoài khoảng mà không có c…
- `Anh_can_cu` (20 dòng): Ảnh bản đồ căn cứ — Resources/UI/Bases/*.json: ảnh nhìn từ trên của căn cứ trên màn Căn cứ (bản đồ, tâm, hướng, bãi thả, HQ, mét mỗi ảnh, viền, mũi tên)
- `Anh_can_cu_vien` (142 dòng): Ảnh căn cứ: viền — outline[]: điểm viền căn cứ trên ảnh
- `Anh_can_cu_mui_ten` (52 dòng): Ảnh căn cứ: mũi tên — arrows[]: mũi tên hướng tấn công trên ảnh
- `Hang_so_can_cu` (2 dòng): Hằng số căn cứ và tháp — Assets/MachineBrigade/Resources/Data/tunables.json: 'bases' (lớp chủ → tên): một dòng một hằng số; mã game đọc qua SimTunables, giữ nguyên giá trị kh…
