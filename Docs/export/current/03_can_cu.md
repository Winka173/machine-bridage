# 03_can_cu — Căn cứ và tháp

Tháp và nhánh, tường, nhà chính, mô-đun tiện ích, xây lại, AI căn cứ.

Gói cân bằng Machine Brigade, commit 2320b4b0, ngày 2026-10-04. Số liệu đầy đủ ở 03_can_cu.xlsx; file này chỉ nêu luật, giải thích, lý do thiết kế, tham khảo và bảng nhỏ (tối đa 20 dòng, bảng lớn: xem sheet).

## Căn cứ và tháp

Căn cứ là một loadout chọn trước trận như bộ bài: sở chỉ huy (HQ) cấp 1–5 và các ô tháp theo cỡ **nhỏ / vừa / lớn** trên bản đồ căn cứ của từng map. Tháp cỡ nào vào ô cỡ đó hoặc ô to hơn; ô tiện ích nhận mô-đun. Tháp bị phá được thả dù lại trong trận (trả CP, có hồi chiêu; tháp nhỏ rẻ và nhanh hơn). Mỗi cứ điểm có tiền đồn 1 ô nhỏ + 1 ô vừa. Vai trò căn cứ theo chế độ: chỗ dựa (sở chỉ huy không bị phá) hoặc mục tiêu.

**Vai trò tháp nhỏ:** tháp canh thấy tàng hình và tăng 10% tầm cho tháp trong 25 m (nhánh Tháp quan sát: 15% trong 30 m, thay mức 10%, không cộng dồn); tháp phòng không nhỏ +25% sát thương lên drone và trực thăng. **Điểm yếu tháp pháo:** xoay chậm, nạp lâu, súng đồng trục không bắn máy bay. **AI** đọc căn cứ địch và mua quân khắc chế. **Thẻ tháp** lên hạng như xe; từ hạng 7 chọn 1 trong 2 nhánh (đổi nhánh 800 xu). **Trang bị tháp:** 3 ô (Vũ khí, Kết cấu, Hệ thống) dùng chung cho mọi tháp cùng loại trong căn cứ.

### Thẻ tháp (16)

| Tháp | Cỡ | Máu | Dựng lại | Nhánh (hạng 7) | Hướng dẫn |
|---|---|---|---|---|---|
| **Tháp canh** | Nhỏ | 1.540 | 5 CP · 25 s | **Tháp quan sát**: Nhìn xa hơn 30%, và cho các tháp trong 30 m thêm 15% tầm bắn (thay cho mức 10% thường của tháp, không cộng dồn). **Ổ súng**: Pháo 25 mm thay súng máy: đánh mạnh xe nhẹ, nhìn gần hơ… | **Tháp canh · công sự cố định · nhẹ nhưng nhìn xa** Cách đánh: súng máy nặng (30 m, bắn cả máy bay); tầm nhìn 60 m giúp soi quân ta cho pháo địch. Mạnh / yếu: chặn trinh sát và xe nhẹ; là tháp yếu nh… |
| **Lô cốt súng máy** | Nhỏ | 3.300 | 6 CP · 25 s | **Súng máy đôi**: Súng máy nặng đôi: hỏa lực mạnh hơn, tầm hơi ngắn hơn. **Lô cốt phun lửa**: Súng phun lửa (16 m) đốt thứ gì lại gần; không bắn được máy bay. | **Lô cốt súng máy · công sự cố định · súng máy nặng** Cách đánh: súng máy nặng bắn nhanh (32 m, bắn cả máy bay). Mạnh / yếu: quét sạch trinh sát và xe nhẹ; gần như không làm xước xe tăng. Mẹo: đưa xe… |
| **Tháp phòng không** | Nhỏ | 2.420 | 6 CP · 25 s | **Tháp cao xạ**: Pháo cao xạ 23 mm bốn nòng tầm gần: hỏa lực mạnh hơn nhiều vào drone, bầy nhỏ và trực thăng, không có tên lửa. **Tổ Stinger**: Tên lửa Stinger thay cho pháo 23 mm: máy bay và trực th… | **Tháp phòng không · công sự cố định · chống máy bay (42 m)** Cách đánh: pháo đôi 30 mm cao xạ tới 42 m và tên lửa phòng không (44 m); cũng bắn mặt đất nhưng chẳng mấy tác dụng. Mạnh / yếu: xé nát tr… |
| **Tháp gây nhiễu EW** | Nhỏ | 1.760 | 3 CP · 25 s | **Máy gây nhiễu drone**: Gây nhiễu đạn điều khiển và drone xa tới 45 m. **Máy đánh lừa radar**: Còn tìm ra pháo khai hỏa trong 80 m và làm lộ chúng 6 giây. | **Tháp gây nhiễu EW · tháp nhỏ · gây nhiễu, không bắn** Cách đánh: tên lửa điều khiển, drone và hỏa lực yểm trợ nhắm vào trong vòng 30 m quanh nó bị lệch; không có súng. Mạnh / yếu: làm cùn tên lửa c… |
| **Trạm tiếp tế CP** | Nhỏ | 1.320 | 6 CP · 25 s |  | **Trạm tiếp tế CP · tháp nhỏ · kinh tế** Cách đánh: không có súng; +0,1 CP mỗi giây cho phe mình, trạm thứ hai +0,06, trạm thứ ba không thêm gì; bị bắn thì ngừng trả 5 giây. Mạnh / yếu: thêm CP cho c… |
| **Tháp tên lửa chống tăng** | Vừa | 1.980 | 7 CP · 40 s | **Tấn công từ trên**: Mạnh hơn 40% lên giáp dày. **Đa năng**: Bắn được cả trực thăng và máy bay; nhẹ hơn lên giáp. | **Tháp tên lửa chống tăng · công sự cố định · chống tăng (50 m)** Cách đánh: bệ phóng Kornet đôi bắn tên lửa chống tăng theo cặp xa tới 50 m. Mạnh / yếu: chặn xe tăng và giáp dày từ xa; APS và xe la-… |
| **Tháp pháo** | Vừa | 3.960 | 11 CP · 40 s | **Pháo bắn tỉa**: Pháo 120 mm nòng dài có ống ngắm: bắn xa hơn mọi pháo xe tăng, chậm, mỗi phát hạ được xe tăng; không bắn máy bay. **Pháo tự động 57 mm**: Loạt đạn 57 mm nhanh chỉ vào xe nhẹ (giáp t… | **Tháp pháo · công sự cố định · pháo xe tăng (32 m)** Cách đánh: pháo 120 mm xuyên giáp của tăng chủ lực đặt trên bệ cố định. Mạnh / yếu: thắng xe tăng và xe nhẹ lọt vào tầm 32 m; bị xe diệt tăng và… |
| **Trạm đánh chặn C-RAM** | Vừa | 2.860 | 5 CP · 40 s | **Centurion**: Súng đánh chặn tầm gần bắn nhanh: nhiều quả đánh chặn hơn, hồi nhanh. Chặn tên lửa, drone, rốc-két bắn thẳng, rốc-két pháo binh và một phần đạn pháo binh, đạn cối; không chặn đạn pháo… | **Trạm đánh chặn C-RAM · tháp vừa · bắn hạ đạn bay tới** Cách đánh: bắn hạ rốc-két, tên lửa, drone và khoảng một phần ba đạn pháo nhắm vào trong 35 m, hai quả đánh chặn cùng lúc; pháo nhiều nòng 20 m… |
| **Dàn rốc-két** | Vừa | 2.420 | 11 CP · 40 s | **Rốc-két chùm**: Mỗi rốc-két rải bom con: tốt hơn với cụm quân, trúng trực tiếp nhẹ hơn. **Rốc-két dẫn đường**: Hai rốc-két GMLRS chính xác ở tầm xa: mạnh với pháo binh và công trình, yếu trước bầy… | **Dàn rốc-két · công sự cố định · phóng loạt (55 m)** Cách đánh: phóng loạt sáu rốc-két theo đường cầu vồng vào mục tiêu mặt đất cách 8–55 m, vượt qua tường và vật che (từ sân trong vào quân địch đã… |
| **Tháp la-de phòng thủ** | Vừa | 2.499 | 5 CP · 40 s | **Trạm la-de**: La-de 50 kW đốt drone ở 40 m và bắn hạ rốc-két, tên lửa nhắm gần nó; không bao giờ hết đạn; không chặn đạn pháo. | **Tháp la-de phòng thủ · tháp ô vừa · không bao giờ hết đạn** Cách đánh: laser chỉ bắn drone, tầm 40 m, cùng bộ đánh chặn rốc-két và đạn cối; khói làm tia yếu 80%. Mạnh / yếu: dập bầy drone và mưa rố… |
| **Nhà chứa xe** | Vừa | 3.960 | 8 CP · 40 s |  | **Nhà chứa xe · công trình ô vừa · xe nhẹ miễn phí** Cách đánh: cứ 60 giây gửi ra một xe hạng nhẹ (xe jeep trinh sát, xe bọc thép hoặc xe tăng hạng nhẹ: chọn ở tab Sở chỉ huy), miễn phí, khi còn ít h… |
| **Nhà chứa máy bay** | Vừa | 3.960 | 8 CP · 40 s |  | **Nhà chứa máy bay · công trình ô vừa · máy bay nhẹ miễn phí** Cách đánh: cứ 60 giây phóng một máy bay nhẹ (trực thăng trinh sát hoặc UAV trinh sát: chọn ở tab Sở chỉ huy), miễn phí, khi còn ít hơn h… |
| **Tháp pháo hạng nặng** | Lớn | 6.160 | 18 CP · 60 s | **Pháo bờ biển tầm xa**: Pháo 155 mm bắn tới 72 m. Mở khi đánh chìm Leviathan (4-11). **Pháo đài thép**: Chắc hơn nhiều, thêm hai tháp súng máy nhỏ xoay quanh đánh xe nhẹ và drone áp sát. | **Tháp pháo hạng nặng · công sự cố định · pháo đôi 155 mm (50 m)** Cách đánh: tháp pháo đôi 155 mm xoay chậm, bắn loạt đôi đạn nổ mạnh tới 50 m. Mạnh / yếu: phá nát xe nhẹ, cụm quân và xe tăng trong… |
| **Trạm tên lửa phòng không tầm xa** | Lớn | 4.180 | 13 CP · 60 s | **PAC-3 đánh chặn**: Bắn hạ tên lửa hành trình, tên lửa đạn đạo, đòn tên lửa hành trình và tên lửa từ đòn lớn của boss; bắn máy bay yếu hơn. **Radar tầm xa**: Bắn máy bay từ rất xa và làm lộ mọi máy… | **Trạm tên lửa phòng không tầm xa · công sự cố định · phòng không tầm xa (62 m)** Cách đánh: radar nhìn xa 85 m, phóng tên lửa từng cặp vào máy bay cách tới 62 m; không có gì để đánh mặt đất. Mạnh /… |
| **Nhà chứa drone** | Lớn | 4.840 | 12 CP · 60 s | **Nhà chứa Lancet**: Đạn bay lượn Lancet thay drone FPV: tầm xa, gấp đôi lên pháo binh và xe đỗ. **Bầy đàn**: Những đợt drone FPV đông hơn, thưa hơn. | **Nhà chứa drone · tháp lớn · drone FPV** Cách đánh: cứ 20 giây phóng hai drone FPV cảm tử vào địch xa tới 70 m, mạnh lên giáp và công trình. Mạnh / yếu: bào mòn thứ gì đứng ngoài tầm các tháp khác;… |
| **Máy phát khiên** | Lớn | 4.400 | 10 CP · 60 s | **Vòm khiên**: Một vòm lớn, chắc hơn, che cả khu vực. **Lá chắn tháp**: Không có vòm chung: mỗi tháp phe ta quanh nó có một khiên nhỏ riêng chặn đạn bắn trúng nó (không chặn vụ nổ xung quanh), tự hồi… | **Máy phát khiên · tháp lớn · che một phần căn cứ** Cách đánh: không có súng; vòm khiên 25 m hấp thụ 3.000 sát thương từ đạn pháo, bom, đạn súng và tên lửa cho mọi thứ phe ta bên dưới, rồi vỡ; hồi lạ… |

### Mô-đun tiện ích (4)

| Mô-đun | Tác dụng |
|---|---|
| **Sân bay dã chiến** | **Sân bay dã chiến · mô-đun tiện ích · hào quang trên không** Cách đánh: khi nó còn đứng, mọi máy bay của ta (máy bay và trực thăng, không tính drone) gây thêm 10% sát thương và bay nhanh hơn 10%. Mạ… |
| **Trung tâm chỉ huy phòng thủ** | **Trung tâm chỉ huy phòng thủ · mô-đun tiện ích · hào quang công trình** Cách đánh: khi nó còn đứng, mọi công trình của ta bắn xa hơn 15% và có thêm 10% máu. Mạnh / yếu: nâng cả căn cứ cùng lúc; trun… |
| **Trạm hậu cần** | **Trạm hậu cần · mô-đun tiện ích** Cách đánh: mức tiếp tế của quân ta tăng thêm 8 CP: thu nhập chỉ giảm khi quân vượt mức tiếp tế. Mạnh / yếu: cho đội quân lớn giữ nguyên thu nhập; vô ích với đội quâ… |
| **Xưởng sửa chữa** | **Xưởng sửa chữa · mô-đun tiện ích · hào quang mặt đất** Cách đánh: khi nó còn đứng, mọi xe mặt đất của ta, ở bất cứ đâu trên bản đồ, gây thêm 10% sát thương và có thêm 10% máu. Mạnh / yếu: nâng cả đ… |

### Đo cân bằng căn cứ

Căn cứ mặc định (pháo đài hạng nặng + ụ pháo; tháp pháo, giàn rocket, tháp ATGM; mỗi loại 2 tháp canh, phòng không, súng máy) đạt 1,86 trước quân hỗn hợp, cao hơn mọi căn cứ chỉ một loại tháp (tốt nhất 1,79); không căn cứ một loại nào mạnh nhất trước mọi loại quân. Tỷ lệ chọn tháp nhỏ trong ô nhỏ (tối ưu tham lam): tháp canh 32%, phòng không 22%, súng máy 19%, răng rồng 11%, EW 10%, bãi mìn 7% → bãi mìn được tăng lên 8 quả, rải lại mỗi 45 giây. Quân pháo binh đứng ngoài tầm tháp thắng mọi căn cứ nếu căn cứ đứng một mình: câu trả lời là quân và phản pháo.

### Hệ căn cứ / The base system

Sinh từ dữ liệu (balance.json, các file bản đồ). / Generated from the data (balance.json, the map files).

### Roster 22 tháp và nhánh / The 22-tower roster and its branches

| Tháp / Tower | Cỡ / Size | Xây lại / Rebuild CP | Nhánh A / Branch A | Nhánh B / Branch B |
|---|---|---|---|---|
| guard_tower (guard_tower) | Small | 5 | guard_tower.watch observation_reach, 5 CP | guard_tower.nest autocannon_25, 5 CP |
| mg_bunker (mg_bunker) | Small | 6 | mg_bunker.twin mg_twin, 6 CP | mg_bunker.flame flame_close, 6 CP |
| aa_turret (aa_turret) | Small | 6 | aa_turret.flak aa_gun_23_drones_helis, 6 CP | aa_turret.sam aa_manpads_aircraft, 5 CP |
| ew_tower (ew_tower) | Small | 3 | ew_tower.drone jam_drones_guided, 3 CP | ew_tower.spoof radar_spoof_counterbattery, 3 CP |
| cp_relay (cp_relay) | Small | 6 | không nhánh / no branch cp_income | không nhánh / no branch cp_income |
| atgm_tower (atgm_tower) | Medium | 7 | atgm_tower.top atgm_top_attack, 7 CP | atgm_tower.multi atgm_multi, 6 CP |
| gun_turret (gun_turret) | Medium | 11 | gun_turret.long gun_sniper_120, 11 CP | gun_turret.auto gun_57_light, 11 CP |
| c_ram (c_ram) | Medium | 5 | c_ram.centurion intercept_close_fast, 5 CP | c_ram.dome intercept_far_slow, 5 CP |
| rocket_turret (rocket_turret) | Medium | 11 | rocket_turret.cluster rockets_cluster, 10 CP | rocket_turret.guided rockets_guided, 9 CP |
| laser_ad_station (laser_ad_station) | Medium | 5 | laser_ad_station.laser antidrone_laser, 5 CP | - |
| heavy_turret (heavy_turret) | Large | 18 | heavy_turret.coastal gun_coastal_long, 18 CP | heavy_turret.bastion fortress_close_defence, 18 CP |
| missile_battery (missile_battery) | Large | 13 | missile_battery.pac3 intercept_heavy_missiles, 9 CP | missile_battery.lrr sam_long_radar, 12 CP |
| drone_hangar (drone_hangar) | Large | 12 | drone_hangar.lancet drone_loitering, 14 CP | drone_hangar.swarm drone_fpv_swarm, 14 CP |
| shield_tower (shield_tower) | Large | 10 | shield_tower.bulwark shield_dome, 10 CP | shield_tower.ward tower_shields, 10 CP |
| vehicle_hangar (vehicle_hangar) | Medium | 8 | - | - |
| aircraft_hangar (aircraft_hangar) | Medium | 8 | - | - |

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
| 2 | guard_tower, mg_bunker, aa_turret, mg_bunker | gun_turret, atgm_tower |  | repair_bay |
| 3 | guard_tower, mg_bunker, aa_turret, mg_bunker | gun_turret, rocket_turret | heavy_turret | repair_bay, logistics_station |
| 4 | guard_tower, mg_bunker, aa_turret, mg_bunker, guard_tower | gun_turret, atgm_tower, rocket_turret | heavy_turret | repair_bay, logistics_station |
| 5 | guard_tower, mg_bunker, aa_turret, mg_bunker, guard_tower, ew_tower | gun_turret, atgm_tower, c_ram | heavy_turret, missile_battery | repair_bay, logistics_station, airfield |

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
| kerr | scout, scout, light |
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
| orlov | artillery, scout |
| kessler | mine_layer, light |
| wolff | heli |
| sen | drone |
| venn | drone |
| thorne | mbt |
| aurel | heavy |
| default | scout, light |

Sheet 03_can_cu/Thap_vu_khi — Tháp: bệ vũ khí phụ (7 dòng, 10 cột)

| id | thap_id | thu_tu | weapon | aim | arc_deg_center_deg | arc_deg_half_deg | slot |
|---|---|---|---|---|---|---|---|
| aa_turret/0 | aa_turret | 0 | sam | Turret |  |  | missile |
| heavy_turret.bastion/0 | heavy_turret.bastion | 0 | hmg_roof | Free |  |  | gun |
| heavy_turret.bastion/1 | heavy_turret.bastion | 1 | hmg_roof | Free |  |  | gun |
| mg_bunker/0 | mg_bunker | 0 | bunker_pkm | Free | -30 | 40 | mg |
| mg_bunker/1 | mg_bunker | 1 | bunker_pkm | Free | 30 | 40 | mg |
| mg_bunker/2 | mg_bunker | 2 | bunker_pkm | Free | -90 | 40 | mg |
| mg_bunker/3 | mg_bunker | 3 | bunker_pkm | Free | 90 | 40 | mg |

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

Sheet 03_can_cu/Nha_chinh_kieu — Nhà chính: kiểu (3 dòng, 15 cột)

| id | nha_chinh | ai_air_share | air | barrage | callable | charges | clear | dome_seconds_s | ground |
|---|---|---|---|---|---|---|---|---|---|
| fortress | headquarters.fortress_ground;headquarters.fortress_air | 0.3 | headquarters.fortress_air | hq_barrage |  |  |  |  | headquarters.fortress_ground |
| garrison |  |  |  |  | scout_jeep;armored_car;light_tank |  | 30 |  |  |
| shield | headquarters.shield |  |  |  |  | 4 |  | 10 |  |

*In 10 / 15 cột; 3 cột khác: xem sheet.*

Sheet 03_can_cu/Mo_dun_tien_ich — Mô-đun tiện ích (4 dòng, 90 cột)

| id | ten_en | ten_vi | ten_ngan_vi | base_cp | mau_hp | mau_trong_tran_hp | giap_hong | giap_noc | cong_trinh |
|---|---|---|---|---|---|---|---|---|---|
| airfield | Airfield | Sân bay dã chiến | Sân bay | 0 | 1600 | 3520.0 | 1 | 1 | TRUE |
| fire_control_centre | Defence Command Centre | Trung tâm chỉ huy phòng thủ | TT phòng thủ | 0 | 1136 | 2499.2 | 1 | 1 | TRUE |
| logistics_station | Logistics station | Trạm hậu cần | Trạm hậu cần | 0 | 1400 | 3080.0 | 1 | 1 | TRUE |
| repair_bay | Repair bay | Xưởng sửa chữa | Xưởng sửa chữa | 0 | 1600 | 3520.0 | 2 | 2 | TRUE |

*In 10 / 90 cột; 47 cột khác: xem sheet.*

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

Bảng đầy đủ: xem sheet `Thap` (56 dòng), `Thap_gia_cong_thuc` (41 dòng), `Can_cu_luat` (21 dòng).

## Công thành và Phòng thủ

- **Pháo đài chiếm 45% chiến trường** ở góc đông bắc: tuyến ngoài (trạm radar), tường chữ L có cổng chính đóng và cửa phụ mở, thành trong có sở chỉ huy. Tháp đặt trên ô có cỡ theo roster tháp mới, lấy từ loadout của phe giữ (AI theo độ khó và tướng); vòng trong mạnh hơn.
- **Set-piece:** tường sập có hoạt cảnh rồi thành đống gạch đi qua được; cổng thép bị phá đổ vào trong; máy phát khiên giữ vòm khiên che thành trong, phá máy cuối cùng thì vòm tắt kèm chớp sáng; siêu pháo bắn theo đồng hồ đếm ngược vào cụm quân đông nhất (phá nó là mục tiêu phụ: 25 CP, 100 xu); đèn pha quét và còi báo động ban đêm; chi viện địch đến bằng tàu hỏa trên đường ray hoặc máy bay vận tải hạ cánh trên đường băng, báo trước 10 giây.
- **Phòng thủ:** ba tuyến ngoài, giữa, trong và sở chỉ huy là trận chốt cuối. Mất một tuyến thì tháp ở đó nổ và người chơi được thưởng CP rút lui (24 rồi 32 CP); tuyến trong có tháp mạnh hơn. Căn cứ dùng đúng loadout của người chơi. Đợt địch kế tiếp hiện trước bằng icon và số lượng (đợt được lên kế hoạch trước nên đúng y như thứ đổ bộ); đợt là bầy xe rẻ lớn dần, trần 48 xe cùng lúc.
- **Đầm Lầy và Quần Đảo San Hô** giữ pháo đài kiểu cũ ở góc: tường mới sẽ cắt mọi đường đắp của hai bản đồ này.
- **Đo (độ khó Thường, 5 seed):** Công thành thắng 5/5 (9,7–17,8 phút); Phòng thủ giữ 3/5 trên 5 bản đồ và 5/5 ở bài kiểm tra kết thúc trận; Vô tận: sở chỉ huy rơi ở phút 10,3–11,7.

Sheet 03_can_cu/Dot_phong_thu — Loadout phòng thủ tham chiếu (5 dòng, 10 cột)

| id | small | medium | large | utilities | he_so_do_kho | duong_cong_dot | cap_hq |
|---|---|---|---|---|---|---|---|
| hq1 | guard_tower;mg_bunker;aa_turret | gun_turret |  | repair_bay | 0.75 | 2;4;5;6;8;9;10;12;13;14 | 1 |
| hq2 | guard_tower;mg_bunker;aa_turret;mg_bunker | gun_turret;atgm_tower |  | repair_bay | 0.8722 | 3;4;6;7;9;10;12;14;15;17 | 2 |
| hq3 | guard_tower;mg_bunker;aa_turret;mg_bunker | gun_turret;rocket_turret | heavy_turret | repair_bay;logistics_station | 1.0414 | 3;5;7;9;11;12;14;16;18;20 | 3 |
| hq4 | guard_tower;mg_bunker;aa_turret;mg_bunker;guard_tower | gun_turret;atgm_tower;rocket_turret | heavy_turret | repair_bay;logistics_station | 1.1887 | 4;6;8;10;12;14;16;19;21;23 | 4 |
| hq5 | guard_tower;mg_bunker;aa_turret;mg_bunker;guard_tower;ew_to… | gun_turret;atgm_tower;c_ram | heavy_turret;missile_battery | repair_bay;logistics_station;airfield | 1.3554 | 4;7;9;11;14;16;19;21;24;26 | 5 |

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

69 dòng. Độ tin cậy: da_kiem_chung 0, uoc_dinh 17, ban_dau_doan 34, NEED_SOURCE 18. Loại: NEED_SOURCE 18, doi_that 48, game 3.

- `aa_turret` (Tháp phòng không): mẫu thật: 2K22 Tunguska (2A38 30 mm);Stinger; game: WARNO; giống: pháo phòng không hai nòng 35 mm trên ụ bao cát; độ tin: uoc_dinh; nguồn: R_unit_refs, R_machine_brigade_can_bang, R_aa_turret, R_machine_brigade_ai_research.
- `aa_turret.flak` (aa_turret.flak): mẫu thật: ZSU-23-4 Shilka (23 mm bốn nòng); giống: Nhánh pháo phòng không bốn nòng; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_machine_brigade_can_bang.
- `aa_turret.sam` (aa_turret.sam): mẫu thật: Mistral ATLAS;RBS-70;Starstreak LML; giống: Nhánh trạm tên lửa phòng không; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_machine_brigade_can_bang.
- `airfield` (Sân bay dã chiến): mẫu thật: bãi đáp trực thăng (chữ H); giống: Bãi đáp sửa chữa và nạp đạn cho máy bay; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_machine_brigade_can_bang.
- `atgm_tower` (Tháp tên lửa chống tăng): mẫu thật: 9M133 Kornet; giống: Tháp bê tông phóng tên lửa chống tăng; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_machine_brigade_can_bang, R_atgm_tower.
- `atgm_tower.multi` (atgm_tower.multi): mẫu thật: 9M133 Kornet;Kornet-EM (bệ nhiều ống); giống: ước đoán (Kornet-EM): nhánh đa năng bốn ống và radar nhỏ; độ tin: uoc_dinh; nguồn: R_unit_refs, R_machine_brigade_can_bang.
- `atgm_tower.top` (atgm_tower.top): mẫu thật: 9M133 Kornet;FGM-148 Javelin (đánh nóc); giống: ước đoán (Javelin): nhánh tên lửa đánh nóc; độ tin: uoc_dinh; nguồn: R_unit_refs, R_machine_brigade_can_bang.
- `barrage_balloon` (Khí cầu neo radar (JLENS)): mẫu thật: JLENS (khí cầu neo radar); giống: Khí cầu neo radar: bom địch kém chính xác, lộ máy bay tàng hình gần; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_barrage_balloon.
- `bulwark_post` (Ụ súng dã chiến): mẫu thật: NSV 12,7 mm;lô cốt hình nấm; giống: Ụ súng máy tạm sau khi tháp đổ (trang bị Bulwark); độ tin: ban_dau_doan; nguồn: R_unit_refs, R_machine_brigade_can_bang, R_bulwark_post.
- `c_ram` (Trạm đánh chặn C-RAM): mẫu thật: Centurion C-RAM;Phalanx Block 1B (M61 20 mm); giống: Pháo phòng thủ tầm gần chống rốc-két, pháo và cối; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_machine_brigade_can_bang, R_c_ram.
- `c_ram.centurion` (c_ram.centurion): mẫu thật: Centurion C-RAM;Phalanx CIWS; giống: Nhánh C-RAM tầm gần; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_machine_brigade_can_bang.
- `c_ram.dome` (c_ram.dome): mẫu thật: Iron Dome (tên lửa Tamir); giống: Nhánh Vòm Sắt đánh chặn rốc-két; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_machine_brigade_can_bang.
- `coastal_battery` (Trận địa pháo bờ biển): mẫu thật: A-222 Bereg (240 mm);AK-130 130 mm (tháp pháo hạm đặt trên bờ);K-300P Bastion-P;M284 155…; giống: Trận địa pháo bờ biển; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_machine_brigade_can_bang, R_coastal_battery.
- `cp_relay` (Trạm tiếp tế CP): mẫu thật: trạm tiếp sóng thông tin dã chiến; giống: Trạm tiếp sóng CP, cột lưới hai chảo ăng-ten; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_machine_brigade_can_bang, R_cp_relay.
- `cp_relay.hardened` (Trạm tiếp tế CP (cp_relay.hardened)): mẫu thật: trạm tiếp tế kiên cố; giống: nhánh trạm tiếp tế; độ tin: uoc_dinh; nguồn: R_unit_refs, R_machine_brigade_can_bang, R_cp_relay.
- … 36 dòng có tham chiếu nữa: xem sheet Can_cu_tham_chieu.

Nguồn được dùng (tiêu đề như repo ghi; link khi repo có):

- `R_aa_turret`: spec dựng lại aa_turret (độ tin 3)
- `R_atgm_tower`: spec dựng lại atgm_tower (độ tin 3)
- `R_barrage_balloon`: spec dựng lại barrage_balloon (độ tin 3)
- `R_bulwark_post`: spec dựng lại bulwark_post (độ tin 3)
- `R_c_ram`: spec dựng lại c_ram (độ tin 3)
- `R_coastal_battery`: spec dựng lại coastal_battery (độ tin 3)
- `R_cp_relay`: spec dựng lại cp_relay (độ tin 3)
- `R_decisions`: Docs/DECISIONS.md (nhật ký quyết định) (độ tin 3)
- `R_drone_hangar`: spec dựng lại drone_hangar (độ tin 3)
- `R_ew_tower`: spec dựng lại ew_tower (độ tin 3)
- `R_gun_turret`: spec dựng lại gun_turret (độ tin 3)
- `R_headquarters`: spec dựng lại headquarters (độ tin 3)
- `R_heavy_turret`: spec dựng lại heavy_turret (độ tin 3)
- `R_logistics_station`: spec dựng lại logistics_station (độ tin 3)
- `R_machine_brigade_ai_research`: Nghiên cứu AI (Machine_Brigade_AI_Research.xlsx) (độ tin 3)
- `R_machine_brigade_can_bang`: Rà soát cân bằng (Machine_Brigade_Can_bang.xlsx) (độ tin 3)
- `R_mg_bunker`: spec dựng lại mg_bunker (độ tin 3)
- `R_repair_bay`: spec dựng lại repair_bay (độ tin 3)
- `R_rocket_turret`: spec dựng lại rocket_turret (độ tin 3)
- `R_shield_tower`: spec dựng lại shield_tower (độ tin 3)
- `R_super_gun`: spec dựng lại super_gun (độ tin 3)
- `R_targeting_station`: spec dựng lại targeting_station (độ tin 3)
- `R_unit_refs`: unit_refs.json (tham chiếu ngoài đời / phim / game theo đơn vị) (độ tin 3)
- `R_wall_hesco`: spec dựng lại wall_hesco (độ tin 3)
- `R_wall_t`: spec dựng lại wall_t (độ tin 3)

Sheet 03_can_cu/Can_cu_so_sanh_that — Căn cứ và tháp: so sánh với thật: 32 dòng, 18 cột; bảng đầy đủ: xem sheet Can_cu_so_sanh_that.

## Các sheet của file

Mọi sheet, số dòng và ý nghĩa cột nằm trong 00_index.xlsx (Muc_luc_sheet, Schema). Sheet `input_<tên>` là bản chép của một sheet nguồn để công thức Excel đọc cùng file; sửa ở sheet nguồn, không sửa bản chép.

- `Thap` (56 dòng): Tháp — Mỗi tháp (thẻ và nhánh bậc 7) một dòng
- `Thap_vu_khi` (7 dòng): Tháp: bệ vũ khí phụ — secondary[]: bệ phụ (chỉ số bệ = thu_tu + 1; bệ 0 là vũ khí chính)
- `Tuong` (3 dòng): Tường — Mỗi loại tường một dòng (def + base.walls.types)
- `Tuong_luat` (11 dòng): Tường: luật — base.walls: xe phá tường, máu đoạn, số tuyến, mặc định, tường theo tướng
- `Nha_chinh` (4 dòng): Nhà chính — Nhà chính và các kiểu (fortress / shield...)
- `Nha_chinh_vu_khi` (11 dòng): Nhà chính: bệ vũ khí phụ — secondary[]: bệ phụ (chỉ số bệ = thu_tu + 1; bệ 0 là vũ khí chính)
- `Nha_chinh_kieu` (3 dòng): Nhà chính: kiểu — hqTypes.<kiểu>: trường không theo cấp
- `Nha_chinh_kieu_cap` (15 dòng): Nhà chính: kiểu x cấp HQ — hqTypes.<kiểu>.<danh sách>[cấp-1]: sức mạnh, đồn trú, khiên theo HQ 1-5
- `Nha_chinh_luat` (13 dòng): Nhà chính: luật — base.hq, hqTypes.default / skillCooldown / radius / ai (kiểu theo tướng, độ khó)
- `Mo_dun_tien_ich` (4 dòng): Mô-đun tiện ích — Trạm sửa, kho đạn, sân bay, trạm hậu cần, radar (ô tiện ích)
- `Loadout_can_cu` (10 dòng): Ô căn cứ theo cấp HQ — base.levels (thường) và base.longLevels (bản đồ dài): số ô mỗi cỡ
- `Xay_lai` (3 dòng): Xây lại tháp theo cỡ ô — base.rebuild.<cỡ>: CP, thời gian chờ, thời gian thả
- `Can_cu_luat` (21 dòng): Căn cứ: luật — base.rebuild (chung), longForward, outpost, roles (vai trò căn cứ theo chế độ), roster
- `Dot_phong_thu` (5 dòng): Loadout phòng thủ tham chiếu — base.reference: 5 loadout tham chiếu theo cấp HQ
- `Can_cu_AI_kieu` (87 dòng): AI xây căn cứ: trọng số — base.ai.styles.<kiểu>.<tháp>: trọng số chọn tháp ('*' = mọi tháp khác)
- `Thap_gia_cong_thuc` (41 dòng): Tháp: công thức giá xây lại — Từng bước giá xây lại (Tools/balance/p32_tower_prices.py): effectiveHP, roleDPS, equivalentCP, hệ số đứng yên, x 1,25, cận cỡ; so với giá game (BaseR…
- `Tuong_duong_xe_cong_trinh` (41 dòng): Tháp: tương đương xe — Giá trị tương đương xe (equivalentCP), tỷ lệ so với giá game, số phát của từng mối đe dọa tham chiếu theo cỡ ô để hạ tháp (DamageTable.Effective, Str…
- `Nha_chinh_so_sanh` (20 dòng): Nhà chính: so sánh kiểu — Giá trị phòng thủ tương đương mỗi phút căn cứ bị đánh (CP), 3 kiểu (Pháo đài mặt đất / phòng không, Đồn trú, Khiên) x HQ 1-5 (Tools/balance/p32_hq_ty…
- `Can_cu_AI_cap` (4 dòng): AI xây căn cứ: cấp HQ theo độ khó — base.ai.levels
- `Can_cu_tham_chieu` (69 dòng): Căn cứ và tháp: tham chiếu ngoài đời — Mỗi tháp / nhánh, tường, nhà chính, mô-đun một dòng: mẫu thật, game tham khảo cơ chế, kích thước thật (spec 12.2; chỉ dữ liệu có trong repo)
- `Can_cu_so_sanh_that` (32 dòng): Căn cứ và tháp: so sánh với thật — So sánh game với thật (spec 12.4): mỗi thông số có đối chiếu một dòng; ty_le = game / thật, khoảng cho phép, co_lech_lon = ngoài khoảng mà không có c…
- `Anh_can_cu` (20 dòng): Ảnh bản đồ căn cứ — Resources/UI/Bases/*.json: ảnh nhìn từ trên của căn cứ trên màn Căn cứ (bản đồ, tâm, hướng, bãi thả, HQ, mét mỗi ảnh, viền, mũi tên)
- `Anh_can_cu_vien` (142 dòng): Ảnh căn cứ: viền — outline[]: điểm viền căn cứ trên ảnh
- `Anh_can_cu_mui_ten` (52 dòng): Ảnh căn cứ: mũi tên — arrows[]: mũi tên hướng tấn công trên ảnh
- `Hang_so_can_cu` (33 dòng): Hằng số căn cứ và tháp — Assets/MachineBrigade/Resources/Data/tunables.json: 'bases' (lớp chủ → tên): một dòng một hằng số; mã game đọc qua SimTunables, giữ nguyên giá trị kh…
