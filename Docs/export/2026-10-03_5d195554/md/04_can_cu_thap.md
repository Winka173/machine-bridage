# 04_can_cu_thap — Căn cứ và tháp

Bộ xuất dữ liệu Machine Brigade, commit 5d195554, ngày 2026-10-03. Sinh bởi `python Tools/export/export.py` (lượt 6): bảng in đúng ô của csv / xlsx; văn bản lấy từ tài liệu thiết kế (Tools/docs) và chuỗi trong game. Toàn văn: Machine_Brigade_Design_FULL_2026-10-03.md.

Tháp và nhánh, tường, nhà chính (kiểu x cấp), mô-đun tiện ích, ô căn cứ theo cấp HQ, xây lại, loadout tham chiếu, AI xây căn cứ

Mục trong file này: 6. Căn cứ và tháp; 7. Công thành và Phòng thủ.

## 6. Căn cứ và tháp

Trạng thái: Đã áp

Nguồn dữ liệu: 04_can_cu_thap/Thap; 04_can_cu_thap/Thap_vu_khi; 04_can_cu_thap/Tuong; 04_can_cu_thap/Tuong_luat; 04_can_cu_thap/Nha_chinh; 04_can_cu_thap/Nha_chinh_kieu; 04_can_cu_thap/Mo_dun_tien_ich; 04_can_cu_thap/Loadout_can_cu; 04_can_cu_thap/Xay_lai; 04_can_cu_thap/Thap_gia_cong_thuc; 04_can_cu_thap/Can_cu_luat. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §6. Căn cứ, §Hệ căn cứ (prompt 32).

#### 6. Căn cứ và tháp

Căn cứ là một loadout chọn trước trận như bộ bài: sở chỉ huy (HQ) cấp 1–5 và các ô tháp theo cỡ **nhỏ / vừa / lớn** trên bản đồ căn cứ của từng map. Tháp cỡ nào vào ô cỡ đó hoặc ô to hơn; ô tiện ích nhận mô-đun. Tháp bị phá được thả dù lại trong trận (trả CP, có hồi chiêu; tháp nhỏ rẻ và nhanh hơn). Mỗi cứ điểm có tiền đồn 1 ô nhỏ + 1 ô vừa. Vai trò căn cứ theo chế độ: chỗ dựa (sở chỉ huy không bị phá) hoặc mục tiêu.

**Vai trò tháp nhỏ:** tháp canh thấy tàng hình và tăng 10% tầm cho tháp trong 25 m (nhánh Tháp quan sát: 15% trong 30 m, thay mức 10%, không cộng dồn); tháp phòng không nhỏ +25% sát thương lên drone và trực thăng. **Điểm yếu tháp pháo:** xoay chậm, nạp lâu, súng đồng trục không bắn máy bay. **AI** đọc căn cứ địch và mua quân khắc chế. **Thẻ tháp** lên hạng như xe; từ hạng 7 chọn 1 trong 2 nhánh (đổi nhánh 800 xu). **Trang bị tháp:** 3 ô (Vũ khí, Kết cấu, Hệ thống) dùng chung cho mọi tháp cùng loại trong căn cứ.

#### Thẻ tháp (22)

| Tháp | Cỡ | Máu | Dựng lại | Nhánh (hạng 7) | Hướng dẫn |
|---|---|---|---|---|---|
| **Tháp canh** | Nhỏ | 1.540 | 5 CP · 25 s | **Tháp quan sát**: Nhìn xa hơn 30%, và cho các tháp trong 30 m thêm 15% tầm bắn (thay cho mức 10% thường của tháp, không cộng dồn). **Ổ súng**: Pháo 25 mm thay súng máy: đánh mạnh xe nhẹ, nhìn gần hơ… | **Tháp canh · công sự cố định · nhẹ nhưng nhìn xa** Cách đánh: súng máy nặng (30 m, bắn cả máy bay); tầm nhìn 60 m giúp soi quân ta cho pháo địch. Mạnh / yếu: chặn trinh sát và xe nhẹ; là tháp yếu nh… |
| **Lô cốt súng máy** | Nhỏ | 3.300 | 6 CP · 25 s | **Súng máy đôi**: Súng máy nặng đôi: hỏa lực mạnh hơn, tầm hơi ngắn hơn. **Lô cốt phun lửa**: Súng phun lửa (16 m) đốt thứ gì lại gần; không bắn được máy bay. | **Lô cốt súng máy · công sự cố định · súng máy nặng** Cách đánh: súng máy nặng bắn nhanh (32 m, bắn cả máy bay). Mạnh / yếu: quét sạch trinh sát và xe nhẹ; gần như không làm xước xe tăng. Mẹo: đưa xe… |
| **Ụ pháo chống tăng** | Nhỏ | 1.500 | 4 CP · 25 s | **Pháo chống tăng tầm xa**: Pháo Rapira 100 mm: xuyên giáp dày tới 38 m, nhưng xoay chậm và chỉ phủ góc 45°. **Súng không giật**: SPG-9 73 mm: đạn lõm rẻ, bắn mọi hướng ở 28 m; yếu hơn với giáp dày n… | **Ụ pháo chống tăng · tháp ô nhỏ · diệt tăng giá rẻ** Cách đánh: 5 giây một phát xuyên giáp, tầm 38 m, chỉ trong 45° hai bên phía trước; pháo xoay chậm. Mạnh / yếu: chặn xe tăng lao thẳng tới; pháo b… |
| **Tháp phòng không** | Nhỏ | 2.420 | 6 CP · 25 s | **Tháp cao xạ**: Pháo cao xạ 23 mm bốn nòng tầm gần: hỏa lực mạnh hơn nhiều vào drone, bầy nhỏ và trực thăng, không có tên lửa. **Tổ Stinger**: Tên lửa Stinger thay cho pháo 23 mm: máy bay và trực th… | **Tháp phòng không · công sự cố định · chống máy bay (42 m)** Cách đánh: pháo đôi 30 mm cao xạ tới 42 m và tên lửa phòng không (44 m); cũng bắn mặt đất nhưng chẳng mấy tác dụng. Mạnh / yếu: xé nát tr… |
| **Tháp gây nhiễu EW** | Nhỏ | 1.760 | 3 CP · 25 s | **Máy gây nhiễu drone**: Gây nhiễu đạn điều khiển và drone xa tới 45 m. **Máy đánh lừa radar**: Còn tìm ra pháo khai hỏa trong 80 m và làm lộ chúng 6 giây. | **Tháp gây nhiễu EW · tháp nhỏ · gây nhiễu, không bắn** Cách đánh: tên lửa điều khiển, drone và hỏa lực yểm trợ nhắm vào trong vòng 30 m quanh nó bị lệch; không có súng. Mạnh / yếu: làm cùn tên lửa c… |
| **Răng rồng** | Nhỏ | 5.280 | 3 CP · 25 s | **Chông sắt**: Khó phá gấp đôi. **Rào thép gai**: Không chặn đường, nhưng làm xe địch trong 6 m chậm một nửa. | **Răng rồng · vật cản nhỏ · chặn đường** Cách đánh: các hàng khối bê tông không xe nào đi qua được; không đánh gì và bị bắn sau cùng. Mạnh / yếu: biến lối vào thành đường vòng dưới họng súng của ta;… |
| **Bãi mìn** | Nhỏ | 880 | 3 CP · 25 s |  | **Bãi mìn · vật cản nhỏ · tám quả mìn** Cách đánh: tám quả mìn chống tăng trong vòng 5 m, rải lại mỗi 45 giây; bãi mìn không phải mục tiêu. Mạnh / yếu: trừng phạt xe lao vào ồ ạt; trinh sát, công bin… |
| **Trạm tiếp tế CP** | Nhỏ | 1.320 | 6 CP · 25 s |  | **Trạm tiếp tế CP · tháp nhỏ · kinh tế** Cách đánh: không có súng; +0,1 CP mỗi giây cho phe mình, trạm thứ hai +0,06, trạm thứ ba không thêm gì; bị bắn thì ngừng trả 5 giây. Mạnh / yếu: thêm CP cho c… |
| **Đèn pha chiến trường** | Nhỏ | 1.199 | 3 CP · 25 s | **Đèn pha**: Chiếu sáng liên tục quanh nó và làm lóa quân tấn công trong luồng sáng. **Pháo sáng**: Bắn pháo sáng mỗi 15 giây tới 40 m: chiếu sáng vùng rộng theo đợt, giữa các đợt thì tối. | **Đèn pha chiến trường · công trình ô nhỏ · ánh sáng đêm** Cách đánh: ban đêm và trong sương mù, phe ta thấy mọi thứ trong 35 m quanh nó; địch trong vùng bắn kém 20%. Mạnh / yếu: biến trận đêm thành… |
| **Mồi nhử bơm hơi** | Nhỏ | 299 | 3 CP · 25 s | **Mồi nhử bơm hơi**: Giả làm tháp pháo: hỏa lực địch dồn vào nó cho tới khi địch phát hiện. **Khí cầu neo**: Làm tản bom thả trong 40 m và làm lộ máy bay địch trong 45 m. | **Mồi nhử bơm hơi · công trình ô nhỏ · hút hỏa lực** Cách đánh: trông như tháp pháo; địch bắn vào nó cho tới khi trinh sát, radar, drone hoặc UAV quét lật tẩy. Mạnh / yếu: làm địch phí đạn pháo và tê… |
| **Tháp tên lửa chống tăng** | Vừa | 1.980 | 7 CP · 40 s | **Tấn công từ trên**: Mạnh hơn 40% lên giáp dày. **Đa năng**: Bắn được cả trực thăng và máy bay; nhẹ hơn lên giáp. | **Tháp tên lửa chống tăng · công sự cố định · chống tăng (50 m)** Cách đánh: bệ phóng Kornet đôi bắn tên lửa chống tăng theo cặp xa tới 50 m. Mạnh / yếu: chặn xe tăng và giáp dày từ xa; APS và xe la-… |
| **Tháp pháo** | Vừa | 3.960 | 11 CP · 40 s | **Pháo bắn tỉa**: Pháo 120 mm nòng dài có ống ngắm: bắn xa hơn mọi pháo xe tăng, chậm, mỗi phát hạ được xe tăng; không bắn máy bay. **Pháo tự động 57 mm**: Loạt đạn 57 mm nhanh chỉ vào xe nhẹ (giáp t… | **Tháp pháo · công sự cố định · pháo xe tăng (32 m)** Cách đánh: pháo 120 mm xuyên giáp của tăng chủ lực đặt trên bệ cố định. Mạnh / yếu: thắng xe tăng và xe nhẹ lọt vào tầm 32 m; bị xe diệt tăng và… |
| **Trạm đánh chặn C-RAM** | Vừa | 2.860 | 5 CP · 40 s | **Centurion**: Súng đánh chặn tầm gần bắn nhanh: nhiều quả đánh chặn hơn, hồi nhanh. Chặn tên lửa, drone, rốc-két bắn thẳng, rốc-két pháo binh và một phần đạn pháo binh, đạn cối; không chặn đạn pháo… | **Trạm đánh chặn C-RAM · tháp vừa · bắn hạ đạn bay tới** Cách đánh: bắn hạ rốc-két, tên lửa, drone và khoảng một phần ba đạn pháo nhắm vào trong 35 m, hai quả đánh chặn cùng lúc; pháo nhiều nòng 20 m… |
| **Dàn rốc-két** | Vừa | 2.420 | 11 CP · 40 s | **Rốc-két chùm**: Mỗi rốc-két rải bom con: tốt hơn với cụm quân, trúng trực tiếp nhẹ hơn. **Rốc-két dẫn đường**: Hai rốc-két GMLRS chính xác ở tầm xa: mạnh với pháo binh và công trình, yếu trước bầy… | **Dàn rốc-két · công sự cố định · phóng loạt (55 m)** Cách đánh: phóng loạt sáu rốc-két theo đường cầu vồng vào mục tiêu mặt đất cách 8–55 m, vượt qua tường và vật che (từ sân trong vào quân địch đã… |
| **Tháp cao xạ hạng nặng** | Vừa | 3.001 | 7 CP · 40 s | **Cao xạ hạng nặng**: KS-19 100 mm: bắn chậm, nổ trên không bán kính lớn vào oanh tạc cơ và tốp máy bay dày; hạ nòng bắn được xe tăng ở 50 m. **Pháo PK 40 mm**: Bofors L/70: luồng đạn 40 mm đều đặn t… | **Tháp cao xạ hạng nặng · tháp ô vừa · đạn nổ trên không** Cách đánh: 2 giây một phát lớn, nổ trên không rộng 6 m, tầm 70 m; hạ nòng bắn xe tăng trong 50 m. Mạnh / yếu: bẻ gãy oanh tạc cơ và tốp máy… |
| **Trạm phòng không laser chống drone** | Vừa | 2.499 | 5 CP · 40 s | **Trạm la-de**: La-de 50 kW đốt drone ở 40 m và bắn hạ rốc-két, tên lửa nhắm gần nó; không bao giờ hết đạn; không chặn đạn pháo. **Lưới chắn drone**: Hành lang lưới thụ động: bắt drone bay vào trong… | **Trạm phòng không laser chống drone · tháp ô vừa · không bao giờ hết đạn** Cách đánh: laser chỉ bắn drone, tầm 40 m, cùng bộ đánh chặn rốc-két và đạn cối; khói làm tia yếu 80%. Mạnh / yếu: dập bầy d… |
| **Hầm che quân** | Vừa | 4.000 | 5 CP · 40 s |  | **Hầm che quân · công trình ô vừa · tránh đạn pháo** Cách đánh: xe ta trong 15 m nhận một nửa sát thương pháo, cối, bom và không kích; không che đạn bắn thẳng. Mạnh / yếu: giữ quân phòng thủ sống qua… |
| **Tháp pháo hạng nặng** | Lớn | 6.160 | 18 CP · 60 s | **Pháo bờ biển tầm xa**: Pháo 155 mm bắn tới 72 m. Mở khi đánh chìm Leviathan (4-11). **Pháo đài thép**: Chắc hơn nhiều, thêm hai tháp súng máy nhỏ xoay quanh đánh xe nhẹ và drone áp sát. | **Tháp pháo hạng nặng · công sự cố định · pháo đôi 155 mm (50 m)** Cách đánh: tháp pháo đôi 155 mm xoay chậm, bắn loạt đôi đạn nổ mạnh tới 50 m. Mạnh / yếu: phá nát xe nhẹ, cụm quân và xe tăng trong… |
| **Trạm tên lửa phòng không tầm xa** | Lớn | 4.180 | 13 CP · 60 s | **PAC-3 đánh chặn**: Bắn hạ tên lửa hành trình, tên lửa đạn đạo, đòn tên lửa hành trình và tên lửa từ đòn lớn của boss; bắn máy bay yếu hơn. **Radar tầm xa**: Bắn máy bay từ rất xa và làm lộ mọi máy… | **Trạm tên lửa phòng không tầm xa · công sự cố định · phòng không tầm xa (62 m)** Cách đánh: radar nhìn xa 85 m, phóng tên lửa từng cặp vào máy bay cách tới 62 m; không có gì để đánh mặt đất. Mạnh /… |
| **Nhà chứa drone** | Lớn | 4.840 | 12 CP · 60 s | **Nhà chứa Lancet**: Đạn bay lượn Lancet thay drone FPV: tầm xa, gấp đôi lên pháo binh và xe đỗ. **Bầy đàn**: Những đợt drone FPV đông hơn, thưa hơn. | **Nhà chứa drone · tháp lớn · drone FPV** Cách đánh: cứ 20 giây phóng hai drone FPV cảm tử vào địch xa tới 70 m, mạnh lên giáp và công trình. Mạnh / yếu: bào mòn thứ gì đứng ngoài tầm các tháp khác;… |
| **Trận địa pháo** | Lớn | 2.420 | 12 CP · 60 s | **Phản pháo**: Nhắm ngay pháo địch vừa khai hỏa trong tầm và làm lộ chúng một lúc; đánh pháo binh mạnh hơn. **Cối hạng nặng**: Cối 240 mm bắn cầu vồng, qua tường vào sân trong và sau vật che: tầm ngắ… | **Trận địa pháo · công sự cố định · tầm xa (90 m)** Cách đánh: lựu pháo nã vào mục tiêu mặt đất cách 25–90 m mỗi khi phe thủ nhìn thấy; không có gì tự vệ ở gần. Mạnh / yếu: gây đau cho mọi thứ dừng l… |
| **Máy phát khiên** | Lớn | 4.400 | 10 CP · 60 s | **Vòm khiên**: Một vòm lớn, chắc hơn, che cả khu vực. **Lá chắn tháp**: Không có vòm chung: mỗi tháp phe ta quanh nó có một khiên nhỏ riêng chặn đạn bắn trúng nó (không chặn vụ nổ xung quanh), tự hồi… | **Máy phát khiên · tháp lớn · che một phần căn cứ** Cách đánh: không có súng; vòm khiên 25 m hấp thụ 3.000 sát thương từ đạn pháo, bom, đạn súng và tên lửa cho mọi thứ phe ta bên dưới, rồi vỡ; hồi lạ… |

#### Mô-đun tiện ích (9)

| Mô-đun | Tác dụng |
|---|---|
| **Sân bay dã chiến** | **Sân bay dã chiến · mô-đun tiện ích** Cách đánh: máy bay bay trên nó hồi 3% máu mỗi giây và nạp đạn; chỉ huy tự đưa chúng về khi hết đạn. Mạnh / yếu: giúp trực thăng và máy bay bay… |
| **Sân bay dã chiến · Nhà chứa máy bay** |  |
| **Sân bay dã chiến · Phục vụ nhanh** |  |
| **Kho đạn** | **Kho đạn · mô-đun tiện ích** Cách đánh: xe nạp đạn tại căn cứ nhanh gấp đôi. Mạnh / yếu: rất hợp với giàn phóng và pháo binh hay hết đạn; nổ rất mạnh khi bị phá. Mẹo: mang theo khi bộ bài nhiều pháo… |
| **Trung tâm điều khiển hỏa lực** | **Trung tâm điều khiển hỏa lực · mô-đun tiện ích · liên kết tháp** Cách đánh: tháp trong 30 m gây thêm 12% sát thương và dồn hỏa lực vào một mục tiêu. Mạnh / yếu: biến cụm tháp thành một khối; vô dụn… |
| **Trạm hậu cần** | **Trạm hậu cần · mô-đun tiện ích** Cách đánh: mức tiếp tế của quân ta tăng thêm 8 CP: thu nhập chỉ giảm khi quân vượt mức tiếp tế. Mạnh / yếu: cho đội quân lớn giữ nguyên thu nhập; vô ích với đội quâ… |
| **Trạm radar** | **Trạm radar · mô-đun tiện ích** Cách đánh: mọi thứ trong căn cứ đều lộ, kể cả tàng hình và ẩn nấp, và pháo địch khai hỏa trong 120 m bị lộ 8 giây. Mạnh / yếu: làm lộ oanh tạc cơ tàng hình và pháo ẩn… |
| **Xưởng sửa chữa** | **Xưởng sửa chữa · mô-đun tiện ích** Cách đánh: xe trong vòng 35 m quanh sở chỉ huy hồi 1,5% máu mỗi giây, kể cả giữa trận. Mạnh / yếu: giữ quân phòng thủ đứng vững; không giúp gì xe ở ngoài chiến tr… |
| **Máy tạo nhiễu tầm nhìn** | **Máy tạo nhiễu tầm nhìn · mô-đun tiện ích · che căn cứ** Cách đánh: địch không thấy gì của ta trong 35 m quanh nó nếu xa hơn 15 m, trừ trinh sát. Mạnh / yếu: pháo binh không tìm được thứ nó che; tri… |

#### Đo cân bằng căn cứ

Căn cứ mặc định (pháo đài hạng nặng + ụ pháo; tháp pháo, giàn rocket, tháp ATGM; mỗi loại 2 tháp canh, phòng không, súng máy) đạt 1,86 trước quân hỗn hợp, cao hơn mọi căn cứ chỉ một loại tháp (tốt nhất 1,79); không căn cứ một loại nào mạnh nhất trước mọi loại quân. Tỷ lệ chọn tháp nhỏ trong ô nhỏ (tối ưu tham lam): tháp canh 32%, phòng không 22%, súng máy 19%, răng rồng 11%, EW 10%, bãi mìn 7% → bãi mìn được tăng lên 8 quả, rải lại mỗi 45 giây. Quân pháo binh đứng ngoài tầm tháp thắng mọi căn cứ nếu căn cứ đứng một mình: câu trả lời là quân và phản pháo.

#### Hệ căn cứ (prompt 32) / The base system (prompt 32)

Sinh từ dữ liệu (balance.json, các file bản đồ). / Generated from the data (balance.json, the map files).

#### 6a. Roster 22 tháp và nhánh / The 22-tower roster and its branches

| Tháp / Tower | Cỡ / Size | Xây lại / Rebuild CP | Nhánh A / Branch A | Nhánh B / Branch B |
|---|---|---|---|---|
| guard_tower (guard_tower) | Small | 5 | guard_tower.watch observation_reach, 5 CP | guard_tower.nest autocannon_25, 5 CP |
| mg_bunker (mg_bunker) | Small | 6 | mg_bunker.twin mg_twin, 6 CP | mg_bunker.flame flame_close, 6 CP |
| at_gun_emplacement (at_gun_emplacement) | Small | 4 | at_gun_emplacement.long at_gun_long_narrow, 4 CP | at_gun_emplacement.recoilless at_recoilless_wide, 3 CP |
| aa_turret (aa_turret) | Small | 6 | aa_turret.flak aa_gun_23_drones_helis, 6 CP | aa_turret.sam aa_manpads_aircraft, 5 CP |
| ew_tower (ew_tower) | Small | 3 | ew_tower.drone jam_drones_guided, 3 CP | ew_tower.spoof radar_spoof_counterbattery, 3 CP |
| dragons_teeth (dragons_teeth) | Small | 3 | dragons_teeth.hedgehog obstacle_block, 3 CP | dragons_teeth.wire wire_slow, 3 CP |
| minefield (minefield) | Small | 3 | không nhánh / no branch mines_at | không nhánh / no branch mines_at |
| cp_relay (cp_relay) | Small | 6 | không nhánh / no branch cp_income | không nhánh / no branch cp_income |
| searchlight (searchlight) | Small | 3 | searchlight.beam light_area, 3 CP | searchlight.flare light_flare_waves, 3 CP |
| inflatable_decoy (inflatable_decoy) | Small | 3 | inflatable_decoy.inflatable decoy_draw_fire, 3 CP | inflatable_decoy.balloon balloon_scatter_reveal, 3 CP |
| atgm_tower (atgm_tower) | Medium | 7 | atgm_tower.top atgm_top_attack, 7 CP | atgm_tower.multi atgm_multi, 6 CP |
| gun_turret (gun_turret) | Medium | 11 | gun_turret.long gun_sniper_120, 11 CP | gun_turret.auto gun_57_light, 11 CP |
| c_ram (c_ram) | Medium | 5 | c_ram.centurion intercept_close_fast, 5 CP | c_ram.dome intercept_far_slow, 5 CP |
| rocket_turret (rocket_turret) | Medium | 11 | rocket_turret.cluster rockets_cluster, 10 CP | rocket_turret.guided rockets_guided, 9 CP |
| heavy_flak_tower (heavy_flak_tower) | Medium | 7 | heavy_flak_tower.heavy aa_heavy_flak_area, 7 CP | heavy_flak_tower.bofors aa_40_steady, 6 CP |
| laser_ad_station (laser_ad_station) | Medium | 5 | laser_ad_station.laser antidrone_laser, 5 CP | laser_ad_station.net antidrone_net, 5 CP |
| troop_shelter (troop_shelter) | Medium | 5 | không nhánh / no branch shelter_troops | không nhánh / no branch shelter_troops |
| heavy_turret (heavy_turret) | Large | 18 | heavy_turret.coastal gun_coastal_long, 18 CP | heavy_turret.bastion fortress_close_defence, 18 CP |
| missile_battery (missile_battery) | Large | 13 | missile_battery.pac3 intercept_heavy_missiles, 9 CP | missile_battery.lrr sam_long_radar, 12 CP |
| drone_hangar (drone_hangar) | Large | 12 | drone_hangar.lancet drone_loitering, 14 CP | drone_hangar.swarm drone_fpv_swarm, 14 CP |
| artillery_emplacement (artillery_emplacement) | Large | 12 | artillery_emplacement.cb counter_battery, 12 CP | artillery_emplacement.mortar mortar_lobbed, 12 CP |
| shield_tower (shield_tower) | Large | 10 | shield_tower.bulwark shield_dome, 10 CP | shield_tower.ward tower_shields, 10 CP |

Hai nhánh của một tháp khác nhau về việc làm (towerRole riêng), không chỉ về số. / The two branches of a card differ in what they do (their own towerRole), not only in numbers.

#### 6b. Xây lại tháp / Rebuilding towers

Không gọi khi xe địch trong 20 m; nhà chính còn 25% máu: tháp nhỏ hoặc vừa rẻ nhất đã đổ xây lại miễn phí, một lần; Đối công: không xây lại sau 600 s. Giá riêng từng tháp (rebuildCp) ở bảng 6a. / No drop with an enemy within 20 m; at 25% HQ health the cheapest fallen small or medium tower comes back free, once; Showdown: no rebuilding after 600 s. Each tower's own price (rebuildCp) is in table 6a.

#### 6c. Tường / Walls

Tối đa 2 tuyến mỗi trại, 3 tuyến lùi ở Phòng thủ; 3-5 đoạn 12 x 2 m mỗi tuyến; 75 bản đồ, 279 tuyến, 1079 đoạn. INTACT/RUBBLE theo trạng thái NavGrid dựng sẵn, đổi ở tick sau khi đoạn bị phá; gạch vụn đi qua được, chậm 20%. Xe phá tường x1.5 chỉ lên tường. Đội AI chọn cổng hay phá tường theo routeCost + threatCost + breachTimeCost. AI địch: brandt t_wall, kessler t_wall, varga gun_wall, default hesco. / Up to 2 lines a camp, 3 fall-back lines in Defend; 3-5 segments of 12 x 2 m a line; 75 maps, 279 lines, 1079 segments. INTACT/RUBBLE on prebuilt NavGrid states, switched at the tick after a segment falls; rubble is passable, 20% slower. Wall breakers x1.5 on walls only. AI squads choose the gate or a breach by routeCost + threatCost + breachTimeCost (aiModeProfile wallRoute).

#### 6d. Kiểu nhà chính / HQ types

Một kỹ năng, hồi 120 s, một nút trên HUD. AI: brandt fortress, kessler fortress, varga garrison, orlov shield, aurel shield, Easy garrison, Normal fortress, Hard shield, VeryHard fortress. / One skill, 120 s cooldown, one HUD button.

#### 7. Phòng thủ / Vô tận theo cấp nhà chính / Defend and Endless by HQ level

Sức đợt = ReferenceBasePower(cấp nhà chính) x độ khó x đường cong đợt x tiến độ chiến dịch. / Wave strength = ReferenceBasePower(HQ level) x difficulty x wave curve x campaign progress. Căn cứ tham chiếu / The reference bases:

| HQ | Nhỏ / Small | Vừa / Medium | Lớn / Large | Mô-đun / Modules |
|---|---|---|---|---|
| 1 | guard_tower, mg_bunker, aa_turret | gun_turret |  | repair_bay |
| 2 | guard_tower, mg_bunker, aa_turret, at_gun_emplacement | gun_turret, atgm_tower |  | repair_bay |
| 3 | guard_tower, mg_bunker, aa_turret, at_gun_emplacement | gun_turret, heavy_flak_tower | heavy_turret | repair_bay, radar_station |
| 4 | guard_tower, mg_bunker, aa_turret, at_gun_emplacement, minefield | gun_turret, atgm_tower, heavy_flak_tower | heavy_turret | repair_bay, radar_station |
| 5 | guard_tower, mg_bunker, aa_turret, at_gun_emplacement, minefield, ew_tower | gun_turret, atgm_tower, c_ram | heavy_turret, missile_battery | repair_bay, radar_station, ammo_depot |

#### Chế độ Đối công / Showdown

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

#### 14. CP khởi đầu và đội mở màn / Starting CP and opening squads

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

Sheet: 04_can_cu_thap/Thap — Tháp (76 dòng, 153 cột)

| id | ten_en | ten_vi | ten_ngan_vi | ke_thua_tu | base_cp | mau_hp | mau_trong_tran_hp | giap_hong | giap_noc |
|---|---|---|---|---|---|---|---|---|---|
| aa_gun_tower | 40 mm AA gun | Pháo phòng không 40 mm | Pháo PK 40 mm |  | 0 | 1273 | 2800.6 | 2 | 2 |
| aa_turret | AA turret | Tháp phòng không | Tháp PK |  | 0 | 1100 | 2420.0 | 2 | 2 |
| aa_turret.flak |  |  | Tháp cao xạ | aa_turret | 0 | 1100 | 2420.0 | 2 | 2 |
| aa_turret.sam |  |  | Stinger | aa_turret | 0 | 1100 | 2420.0 | 2 | 2 |
| artillery_emplacement | Artillery emplacement | Trận địa pháo | Trận địa pháo |  | 0 | 1100 | 2420.0 | 1 | 1 |
| artillery_emplacement.cb |  |  | Phản pháo | artillery_emplacement | 0 | 1100 | 2420.0 | 1 | 1 |
| artillery_emplacement.mortar |  |  | Cối nặng | artillery_emplacement | 0 | 1100 | 2420.0 | 1 | 1 |
| at_gun_emplacement | Anti-tank gun emplacement | Ụ pháo chống tăng | Ụ chống tăng |  | 0 | 682 | 1500.4 | 1 | 1 |
| at_gun_emplacement.long |  |  | Pháo CT | at_gun_emplacement | 0 | 682 | 1500.4 | 1 | 1 |
| at_gun_emplacement.recoilless |  |  | SKZ | recoilless_gun_tower | 0 | 545 | 1199.0 | 1 | 1 |
| atgm_tower | ATGM tower | Tháp tên lửa chống tăng | Tháp ATGM |  | 0 | 900 | 1980.0 | 2 | 2 |
| atgm_tower.multi |  |  | Đa năng | atgm_tower | 0 | 900 | 1980.0 | 2 | 2 |
| atgm_tower.top |  |  | Đánh từ trên | atgm_tower | 0 | 900 | 1980.0 | 2 | 2 |
| barrage_balloon | Radar aerostat (JLENS) | Khí cầu neo radar (JLENS) | Khí cầu radar |  | 0 | 364 | 800.8 | 0 | 0 |
| blast_wall | Gabion blast wall | Tường chắn đạn | Tường chắn đạn |  | 0 | 1364 | 3000.8 | 3 | 3 |

*15 / 76 dòng đầu: xem sheet 04_can_cu_thap/Thap; in 10 / 153 cột; 75 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 04_can_cu_thap/Thap_vu_khi — Tháp: bệ vũ khí phụ (3 dòng, 8 cột)

| id | thap_id | thu_tu | weapon | aim | slot |
|---|---|---|---|---|---|
| aa_turret/0 | aa_turret | 0 | sam | Turret | missile |
| heavy_turret.bastion/0 | heavy_turret.bastion | 0 | hmg_roof | Free | gun |
| heavy_turret.bastion/1 | heavy_turret.bastion | 1 | hmg_roof | Free | gun |

Sheet: 04_can_cu_thap/Tuong — Tường (3 dòng, 81 cột)

| id | ten_en | ten_vi | ten_ngan_vi | base_cp | mau_hp | mau_trong_tran_hp | giap_hong | giap_noc | cong_trinh |
|---|---|---|---|---|---|---|---|---|---|
| wall_gun | Gun wall | Tường gắn súng | Tường súng | 0 | 2880 | 6336.0 | 3 | 3 | TRUE |
| wall_hesco | HESCO wall | Tường HESCO | HESCO | 0 | 2400 | 5280.0 | 3 | 3 | TRUE |
| wall_t | T-wall | Tường chữ T | Tường T | 0 | 3840 | 8448.0 | 4 | 4 | TRUE |

*in 10 / 81 cột; 38 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 04_can_cu_thap/Tuong_luat — Tường: luật (11 dòng, 8 cột)

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

Sheet: 04_can_cu_thap/Nha_chinh — Nhà chính (4 dòng, 84 cột)

| id | ten_en | ten_vi | ten_ngan_vi | lop | ke_thua_tu | base_cp | mau_hp | mau_trong_tran_hp | giap_hong |
|---|---|---|---|---|---|---|---|---|---|
| headquarters | Headquarters | Sở chỉ huy | Sở chỉ huy | Defense |  | 0 | 9000 | 19800.0 | 4 |
| headquarters.fortress_air | Headquarters · AA Fortress | Sở chỉ huy · Pháo đài phòng không | Pháo đài PK | Defense | headquarters | 0 | 9000 | 19800.0 | 4 |
| headquarters.fortress_ground | Headquarters · Fortress | Sở chỉ huy · Pháo đài | SCH Pháo đài | Defense | headquarters | 0 | 9000 | 19800.0 | 4 |
| headquarters.shield | Headquarters · Shield | Sở chỉ huy · Lá chắn | SCH Lá chắn | Defense | headquarters | 0 | 9000 | 19800.0 | 4 |

*in 10 / 84 cột; 46 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 04_can_cu_thap/Nha_chinh_kieu — Nhà chính: kiểu (3 dòng, 14 cột)

| id | nha_chinh | ai_air_share | air | barrage | charges | clear | dome_seconds_s | ground | hq |
|---|---|---|---|---|---|---|---|---|---|
| fortress | headquarters.fortress_ground;headquarters.fortress_air | 0.3 | headquarters.fortress_air | hq_barrage |  |  |  | headquarters.fortress_ground |  |
| garrison |  |  |  |  |  | 30 |  |  |  |
| shield | headquarters.shield |  |  |  | 4 |  | 10 |  | headquarters.shield |

*in 10 / 14 cột; 2 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 04_can_cu_thap/Mo_dun_tien_ich — Mô-đun tiện ích (9 dòng, 101 cột)

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

*in 10 / 101 cột; 58 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 04_can_cu_thap/Loadout_can_cu — Ô căn cứ theo cấp HQ (10 dòng, 9 cột)

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

Sheet: 04_can_cu_thap/Xay_lai — Xây lại tháp theo cỡ ô (3 dòng, 6 cột)

| id | cooldown_s | cp | drop |
|---|---|---|---|
| large | 60 | 7 | 5 |
| medium | 40 | 4 | 3.5 |
| small | 25 | 2 | 2.5 |

Sheet: 04_can_cu_thap/Thap_gia_cong_thuc — Tháp: công thức giá xây lại (60 dòng, 22 cột)

| id | co_o | vai_tro_gia | cach_tinh | he_so_trung_vi_doa | role_dps | mau_tren_cp_nhom | dps_tren_cp_nhom | so_xe_nhom | he_so_dung_yen |
|---|---|---|---|---|---|---|---|---|---|
| aa_turret | Small | air | chien_dau | 0.9974999999999999 | 219.4167303643507 | 158.0 | 30.334200000000003 | 11 | 0.625 |
| aa_turret.flak | Small | air | chien_dau | 0.9974999999999999 | 240.3845953002611 | 158.0 | 30.334200000000003 | 11 | 0.625 |
| aa_turret.sam | Small | air | chien_dau | 0.9974999999999999 | 49.64061096136568 | 158.0 | 30.334200000000003 | 11 | 0.725 |
| artillery_emplacement | Large | ground | chien_dau | 1.1099999999999999 | 72.08791208791209 | 109.28928571428571 | 8.485147678117894 | 12 | 0.725 |
| artillery_emplacement.cb | Large | ground | chien_dau | 1.1099999999999999 | 68.64922687931538 | 109.28928571428571 | 8.485147678117894 | 12 | 0.725 |
| artillery_emplacement.mortar | Large | ground | chien_dau | 1.1099999999999999 | 73.33333333333334 | 109.28928571428571 | 8.485147678117894 | 12 | 0.725 |
| at_gun_emplacement | Small | at | chien_dau | 0.9974999999999999 | 34.0 | 288.1801801801802 | 7.741351648351649 | 23 | 0.625 |
| at_gun_emplacement.long | Small | at | chien_dau | 0.9974999999999999 | 34.0 | 288.1801801801802 | 7.741351648351649 | 23 | 0.625 |
| at_gun_emplacement.recoilless | Small | at | chien_dau | 1.1099999999999999 | 22.938530734632685 | 288.1801801801802 | 7.741351648351649 | 23 | 0.575 |
| atgm_tower | Medium | at | chien_dau | 0.9375 | 82.88288288288288 | 266.56666666666666 | 7.741351648351649 | 23 | 0.625 |
| atgm_tower.multi | Medium | at | chien_dau | 0.9375 | 70.45045045045045 | 266.56666666666666 | 7.741351648351649 | 23 | 0.625 |
| atgm_tower.top | Medium | at | chien_dau | 0.9375 | 88.46153846153847 | 266.56666666666666 | 7.741351648351649 | 23 | 0.625 |
| c_ram | Medium | util:intercept | intercept |  |  |  |  |  |  |
| c_ram.centurion | Medium | util:intercept | intercept |  |  |  |  |  |  |
| c_ram.dome | Medium | util:intercept | intercept |  |  |  |  |  |  |

*15 / 60 dòng đầu: xem sheet 04_can_cu_thap/Thap_gia_cong_thuc; in 10 / 22 cột; 10 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 04_can_cu_thap/Can_cu_luat — Căn cứ: luật (21 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so | gia_tri_chu | don_vi |
|---|---|---|---|---|---|
| base.roster | base.roster |  |  | guard_tower;mg_bunker;at_gun_emplacement;aa_turret;ew_tower… |  |
| longForward.medium | base.longForward | medium | 2 |  |  |
| longForward.small | base.longForward | small | 6 |  |  |
| outpost.cp | base.outpost | cp | 6 |  | CP |
| outpost.slots | base.outpost | slots | 2 |  |  |
| rebuild.delay | base.rebuild | delay | 4 |  | s |
| rebuild.enemyRadius | base.rebuild | enemyRadius | 20 |  | m |
| rebuild.hqRescue | base.rebuild | hqRescue | 0.25 |  |  |
| rebuild.showdownCutoff | base.rebuild | showdownCutoff | 600 |  | s |
| roles.Assault | base.roles | Assault |  | Target |  |
| roles.BossRush | base.roles | BossRush |  | None |  |
| roles.Campaign | base.roles | Campaign |  | None |  |
| roles.Conquest | base.roles | Conquest |  | Anchor |  |
| roles.Deathmatch | base.roles | Deathmatch |  | Anchor |  |
| roles.Defend | base.roles | Defend |  | Defend |  |
| roles.Endless | base.roles | Endless |  | Defend |  |
| roles.KingOfTheHill | base.roles | KingOfTheHill |  | Anchor |  |
| roles.Showdown | base.roles | Showdown |  | Target |  |
| roles.Siege | base.roles | Siege |  | Target |  |
| roles.Survival | base.roles | Survival |  | None |  |
| roles.Weekly | base.roles | Weekly |  | Target |  |

## 7. Công thành và Phòng thủ

Trạng thái: Một phần — chờ prompt xuat_luot3 (sheet Dot_phong_thu)

Nguồn dữ liệu: 04_can_cu_thap/Dot_phong_thu; 04_can_cu_thap/Can_cu_AI_cap. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §7. Công thành.

- **Pháo đài chiếm 45% chiến trường** ở góc đông bắc: tuyến ngoài (trạm radar), tường chữ L có cổng chính đóng và cửa phụ mở, thành trong có sở chỉ huy. Tháp đặt trên ô có cỡ theo roster tháp mới, lấy từ loadout của phe giữ (AI theo độ khó và tướng); vòng trong mạnh hơn.
- **Set-piece:** tường sập có hoạt cảnh rồi thành đống gạch đi qua được; cổng thép bị phá đổ vào trong; máy phát khiên giữ vòm khiên che thành trong, phá máy cuối cùng thì vòm tắt kèm chớp sáng; siêu pháo bắn theo đồng hồ đếm ngược vào cụm quân đông nhất (phá nó là mục tiêu phụ: 25 CP, 100 xu); đèn pha quét và còi báo động ban đêm; chi viện địch đến bằng tàu hỏa trên đường ray hoặc máy bay vận tải hạ cánh trên đường băng, báo trước 10 giây.
- **Phòng thủ:** ba tuyến ngoài, giữa, trong và sở chỉ huy là trận chốt cuối. Mất một tuyến thì tháp ở đó nổ và người chơi được thưởng CP rút lui (24 rồi 32 CP); tuyến trong có tháp mạnh hơn. Căn cứ dùng đúng loadout của người chơi. Đợt địch kế tiếp hiện trước bằng icon và số lượng (đợt được lên kế hoạch trước nên đúng y như thứ đổ bộ); đợt là bầy xe rẻ lớn dần, trần 48 xe cùng lúc.
- **Đầm Lầy và Quần Đảo San Hô** giữ pháo đài kiểu cũ ở góc: tường mới sẽ cắt mọi đường đắp của hai bản đồ này.
- **Đo (độ khó Thường, 5 seed):** Công thành thắng 5/5 (9,7–17,8 phút); Phòng thủ giữ 3/5 trên 5 bản đồ và 5/5 ở bài kiểm tra kết thúc trận; Vô tận: sở chỉ huy rơi ở phút 10,3–11,7.

Sheet: 04_can_cu_thap/Dot_phong_thu — Loadout phòng thủ tham chiếu (5 dòng, 10 cột)

| id | small | medium | large | utilities | he_so_do_kho | duong_cong_dot | cap_hq |
|---|---|---|---|---|---|---|---|
| hq1 | guard_tower;mg_bunker;aa_turret | gun_turret |  | repair_bay | CHUA_AP:prompt_xuat_luot3 | CHUA_AP:prompt_xuat_luot3 | 1 |
| hq2 | guard_tower;mg_bunker;aa_turret;at_gun_emplacement | gun_turret;atgm_tower |  | repair_bay | CHUA_AP:prompt_xuat_luot3 | CHUA_AP:prompt_xuat_luot3 | 2 |
| hq3 | guard_tower;mg_bunker;aa_turret;at_gun_emplacement | gun_turret;heavy_flak_tower | heavy_turret | repair_bay;radar_station | CHUA_AP:prompt_xuat_luot3 | CHUA_AP:prompt_xuat_luot3 | 3 |
| hq4 | guard_tower;mg_bunker;aa_turret;at_gun_emplacement;minefield | gun_turret;atgm_tower;heavy_flak_tower | heavy_turret | repair_bay;radar_station | CHUA_AP:prompt_xuat_luot3 | CHUA_AP:prompt_xuat_luot3 | 4 |
| hq5 | guard_tower;mg_bunker;aa_turret;at_gun_emplacement;minefiel… | gun_turret;atgm_tower;c_ram | heavy_turret;missile_battery | repair_bay;radar_station;ammo_depot | CHUA_AP:prompt_xuat_luot3 | CHUA_AP:prompt_xuat_luot3 | 5 |

Sheet: 04_can_cu_thap/Can_cu_AI_cap — AI xây căn cứ: cấp HQ theo độ khó (4 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so |
|---|---|---|---|
| Easy | base.ai.levels | Easy | 2 |
| Hard | base.ai.levels | Hard | 5 |
| Normal | base.ai.levels | Normal | 3 |
| VeryHard | base.ai.levels | VeryHard | 5 |

## Các sheet khác của file

Mọi sheet chưa in ở mục trên (sheet input_<tên> là bản chép từ file khác, không in lại).

### Can_cu_AI_kieu

Trạng thái: Đã áp

Nguồn dữ liệu: 04_can_cu_thap/Can_cu_AI_kieu.

Sheet: 04_can_cu_thap/Can_cu_AI_kieu — AI xây căn cứ: trọng số (112 dòng, 6 cột)

| id | kieu | thap | trong_so |
|---|---|---|---|
| air/aa_turret | air | aa_turret | 2.0 |
| air/c_ram | air | c_ram | 1.2 |
| air/fire_control_centre | air | fire_control_centre | 1.0 |
| air/guard_tower | air | guard_tower | 0.8 |
| air/heavy_flak_tower | air | heavy_flak_tower | 1.8 |
| air/inflatable_decoy | air | inflatable_decoy | 1.0 |
| air/laser_ad_station | air | laser_ad_station | 1.0 |
| air/missile_battery | air | missile_battery | 1.6 |
| armour/aa_turret | armour | aa_turret | 0.8 |
| armour/at_gun_emplacement | armour | at_gun_emplacement | 1.6 |
| armour/fire_control_centre | armour | fire_control_centre | 1.0 |
| armour/guard_tower | armour | guard_tower | 0.6 |
| armour/gun_turret | armour | gun_turret | 2.0 |
| armour/heavy_turret | armour | heavy_turret | 1.4 |
| armour/inflatable_decoy | armour | inflatable_decoy | 0.6 |

*15 / 112 dòng đầu: xem sheet 04_can_cu_thap/Can_cu_AI_kieu.*

### Mo_dun_tien_ich_vu_khi

Trạng thái: Chưa áp — không có trong mã và dữ liệu

Nguồn dữ liệu: 04_can_cu_thap/Mo_dun_tien_ich_vu_khi.

Sheet: 04_can_cu_thap/Mo_dun_tien_ich_vu_khi — Mô-đun tiện ích: bệ vũ khí phụ (1 dòng, 8 cột)

| id | mo_dun_tien_ich_id | trang_thai | ghi_chu |
|---|---|---|---|
| KHONG_CO | KHONG_CO | KHONG_CO | không mô-đun tiện ích nào có bệ phụ (secondary[]) trong bal… |

### Nha_chinh_kieu_cap

Trạng thái: Đã áp

Nguồn dữ liệu: 04_can_cu_thap/Nha_chinh_kieu_cap.

Sheet: 04_can_cu_thap/Nha_chinh_kieu_cap — Nhà chính: kiểu x cấp HQ (15 dòng, 12 cột)

| id | kieu | cap_hq | scale | airScale | every | caps | regen | dome | squads_units |
|---|---|---|---|---|---|---|---|---|---|
| fortress/1 | fortress | 1 | 0.29 | 0.16 |  |  |  |  |  |
| fortress/2 | fortress | 2 | 0.36 | 0.2 |  |  |  |  |  |
| fortress/3 | fortress | 3 | 0.42 | 0.23 |  |  |  |  |  |
| fortress/4 | fortress | 4 | 0.49 | 0.27 |  |  |  |  |  |
| fortress/5 | fortress | 5 | 0.55 | 0.31 |  |  |  |  |  |
| garrison/1 | garrison | 1 |  |  | 120.0 | 6 |  |  | light_tank |
| garrison/2 | garrison | 2 |  |  | 100.0 | 8 |  |  | armored_car;scout_jeep |
| garrison/3 | garrison | 3 |  |  | 100.0 | 10 |  |  | light_tank;armored_car |
| garrison/4 | garrison | 4 |  |  | 130.0 | 12 |  |  | main_battle_tank |
| garrison/5 | garrison | 5 |  |  | 170.0 | 15 |  |  | main_battle_tank;scout_jeep |
| shield/1 | shield | 1 | 0.15 |  |  |  | 0.00059 | 0.024 |  |
| shield/2 | shield | 2 | 0.19 |  |  |  | 0.00073 | 0.029 |  |
| shield/3 | shield | 3 | 0.24 |  |  |  | 0.0009 | 0.036 |  |
| shield/4 | shield | 4 | 0.26 |  |  |  | 0.00092 | 0.04 |  |
| shield/5 | shield | 5 | 0.29 |  |  |  | 0.00096 | 0.043 |  |

### Nha_chinh_luat

Trạng thái: Đã áp

Nguồn dữ liệu: 04_can_cu_thap/Nha_chinh_luat.

Sheet: 04_can_cu_thap/Nha_chinh_luat — Nhà chính: luật (13 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so | gia_tri_chu | don_vi |
|---|---|---|---|---|---|
| hq | base | hq |  | headquarters |  |
| hqTypes.ai.Easy | base.hqTypes | Easy |  | garrison |  |
| hqTypes.ai.Hard | base.hqTypes | Hard |  | shield |  |
| hqTypes.ai.Normal | base.hqTypes | Normal |  | fortress |  |
| hqTypes.ai.VeryHard | base.hqTypes | VeryHard |  | fortress |  |
| hqTypes.ai.aurel | base.hqTypes | aurel |  | shield |  |
| hqTypes.ai.brandt | base.hqTypes | brandt |  | fortress |  |
| hqTypes.ai.kessler | base.hqTypes | kessler |  | fortress |  |
| hqTypes.ai.orlov | base.hqTypes | orlov |  | shield |  |
| hqTypes.ai.varga | base.hqTypes | varga |  | garrison |  |
| hqTypes.default | base.hqTypes | default |  | fortress |  |
| hqTypes.radius | base.hqTypes | radius | 45 |  | m |
| hqTypes.skillCooldown | base.hqTypes | skillCooldown | 120 |  | s |

### Nha_chinh_so_sanh

Trạng thái: Đã áp

Nguồn dữ liệu: 04_can_cu_thap/Nha_chinh_so_sanh.

Sheet: 04_can_cu_thap/Nha_chinh_so_sanh — Nhà chính: so sánh kiểu (20 dòng, 13 cột)

| id | kieu | cap_hq | muc_tieu_duoi_cp | muc_tieu_tren_cp | thanh_phan_1 | thanh_phan_2 | thanh_phan_3 | chia_cho | gia_tri_moi_phut_cp |
|---|---|---|---|---|---|---|---|---|---|
| fortress/1 | fortress | 1 | 4 | 5 | 2.938539575707716 | 1.5459371709371708 | 0.0 | 1.0 | 4.484476746644887 |
| fortress/2 | fortress | 2 | 5 | 6 | 3.6478422319130277 | 1.9190944190944188 | 0.0 | 1.0 | 5.566936651007446 |
| fortress/3 | fortress | 3 | 6 | 7 | 4.2558159372318665 | 2.2389434889434887 | 0.0 | 1.0 | 6.494759426175355 |
| fortress/4 | fortress | 4 | 7 | 8 | 4.965118593437177 | 2.6121007371007368 | 0.0 | 1.0 | 7.577219330537914 |
| fortress/5 | fortress | 5 | 8 | 9 | 5.573092298756015 | 2.931949806949807 | 0.0 | 1.0 | 8.505042105705822 |
| fortress_air/1 | fortress_air | 1 | 4 | 5 | 3.5199681687860194 | 0.8529308529308528 | 0.0 | 1.0 | 4.372899021716872 |
| fortress_air/2 | fortress_air | 2 | 5 | 6 | 4.399960210982525 | 1.066163566163566 | 0.0 | 1.0 | 5.466123777146091 |
| fortress_air/3 | fortress_air | 3 | 6 | 7 | 5.059954242629903 | 1.2260881010881008 | 0.0 | 1.0 | 6.2860423437180035 |
| fortress_air/4 | fortress_air | 4 | 7 | 8 | 5.939946284826408 | 1.439320814320814 | 0.0 | 1.0 | 7.379267099147222 |
| fortress_air/5 | fortress_air | 5 | 8 | 9 | 6.819938327022912 | 1.6525535275535272 | 0.0 | 1.0 | 8.47249185457644 |
| garrison/1 | garrison | 1 | 4 | 5 | 6.0 | 3.0 | 0.0 | 2.0 | 4.5 |
| garrison/2 | garrison | 2 | 5 | 6 | 5.0 | 6.0 | 0.0 | 2.0 | 5.5 |
| garrison/3 | garrison | 3 | 6 | 7 | 5.999999999999999 | 7.2 | 0.0 | 2.0 | 6.6 |
| garrison/4 | garrison | 4 | 7 | 8 | 8.0 | 7.384615384615385 | 0.0 | 2.0 | 7.6923076923076925 |
| garrison/5 | garrison | 5 | 8 | 9 | 10.0 | 7.0588235294117645 | 0.0 | 2.0 | 8.529411764705882 |
| shield/1 | shield | 1 | 4 | 5 | 2.685152685152685 | 0.9168463320463321 | 0.938223938223938 | 1.0 | 4.540222955422955 |
| shield/2 | shield | 2 | 5 | 6 | 2.685152685152685 | 1.7016046332046333 | 1.1336872586872586 | 1.0 | 5.520444577044577 |
| shield/3 | shield | 3 | 6 | 7 | 2.685152685152685 | 2.4475135135135138 | 1.4073359073359069 | 1.0 | 6.540002106002105 |
| shield/4 | shield | 4 | 7 | 8 | 2.685152685152685 | 3.216732046332046 | 1.5637065637065635 | 1.0 | 7.465591295191295 |
| shield/5 | shield | 5 | 8 | 9 | 2.685152685152685 | 4.102498841698842 | 1.6809845559845555 | 1.0 | 8.468636082836081 |

*in 10 / 13 cột; 1 cột khác (và raw_json, nguon): xem sheet.*

### Nha_chinh_vu_khi

Trạng thái: Đã áp

Nguồn dữ liệu: 04_can_cu_thap/Nha_chinh_vu_khi.

Sheet: 04_can_cu_thap/Nha_chinh_vu_khi — Nhà chính: bệ vũ khí phụ (11 dòng, 8 cột)

| id | nha_chinh_id | thu_tu | weapon | aim | slot |
|---|---|---|---|---|---|
| headquarters.fortress_air/0 | headquarters.fortress_air | 0 | hq_flak | Free | mg |
| headquarters.fortress_air/1 | headquarters.fortress_air | 1 | hq_flak | Free | mg |
| headquarters.fortress_air/2 | headquarters.fortress_air | 2 | mg_coax | Turret | coax |
| headquarters.fortress_air/3 | headquarters.fortress_air | 3 | bofors_l70 | Free | gun |
| headquarters.fortress_ground/0 | headquarters.fortress_ground | 0 | hq_flak | Free | mg |
| headquarters.fortress_ground/1 | headquarters.fortress_ground | 1 | hq_flak | Free | mg |
| headquarters.fortress_ground/2 | headquarters.fortress_ground | 2 | mg_coax | Turret | coax |
| headquarters.fortress_ground/3 | headquarters.fortress_ground | 3 | turret_gun_120_long | Free | gun |
| headquarters/0 | headquarters | 0 | hq_flak | Free | mg |
| headquarters/1 | headquarters | 1 | hq_flak | Free | mg |
| headquarters/2 | headquarters | 2 | mg_coax | Turret | coax |

### Tuong_duong_xe_cong_trinh

Trạng thái: Đã áp

Nguồn dữ liệu: 04_can_cu_thap/Tuong_duong_xe_cong_trinh.

Sheet: 04_can_cu_thap/Tuong_duong_xe_cong_trinh — Tháp: tương đương xe (60 dòng, 13 cột)

| id | gia_tri_tuong_duong_xe_cp | ty_le_so_voi_gia | doa_kinetic | so_phat_kinetic | doa_he | so_phat_he | doa_shaped | so_phat_shaped | doa_artillery |
|---|---|---|---|---|---|---|---|---|---|
| aa_turret | 10.538802941418044 | 1.7564671569030075 | ifv_30 | 216.0 | gun_105_wheeled_he | 8.0 | khrizantema | 14.0 | caesar_155 |
| aa_turret.flak | 11.030869099519423 | 1.838478183253237 | ifv_30 | 216.0 | gun_105_wheeled_he | 8.0 | khrizantema | 14.0 | caesar_155 |
| aa_turret.sam | 5.012737623976222 | 1.0025475247952444 | ifv_30 | 216.0 | gun_105_wheeled_he | 8.0 | khrizantema | 14.0 | caesar_155 |
| artillery_emplacement | 13.018439246619572 | 1.0848699372182977 | gun_125_armata_ke | 13.0 | gun_155_crusader | 6.0 | spike_nlos | 14.0 | thermobaric_rockets |
| artillery_emplacement.cb | 12.704147355021735 | 1.0586789462518114 | gun_125_armata_ke | 13.0 | gun_155_crusader | 6.0 | spike_nlos | 14.0 | thermobaric_rockets |
| artillery_emplacement.mortar | 13.130413718115848 | 1.0942011431763208 | gun_125_armata_ke | 13.0 | gun_155_crusader | 6.0 | spike_nlos | 14.0 | thermobaric_rockets |
| at_gun_emplacement | 4.787911144128944 | 1.196977786032236 | ifv_30 | 134.0 | gun_105_wheeled_he | 5.0 | khrizantema | 9.0 | caesar_155 |
| at_gun_emplacement.long | 4.787911144128944 | 1.196977786032236 | ifv_30 | 134.0 | gun_105_wheeled_he | 5.0 | khrizantema | 9.0 | caesar_155 |
| at_gun_emplacement.recoilless | 3.332655699640046 | 1.1108852332133485 | ifv_30 | 91.0 | gun_105_wheeled_he | 4.0 | khrizantema | 7.0 | caesar_155 |
| atgm_tower | 9.210178829642077 | 1.315739832806011 | gun_105_ags | 16.0 | gun_105_wheeled_he | 7.0 | lancet | 14.0 | mlrs_rockets |
| atgm_tower.multi | 8.49136531795029 | 1.415227552991715 | gun_105_ags | 16.0 | gun_105_wheeled_he | 7.0 | lancet | 14.0 | mlrs_rockets |
| atgm_tower.top | 9.515089606177254 | 1.3592985151681791 | gun_105_ags | 16.0 | gun_105_wheeled_he | 7.0 | lancet | 14.0 | mlrs_rockets |
| c_ram |  |  | gun_105_ags | 19.0 | gun_105_wheeled_he | 8.0 | lancet | 20.0 | mlrs_rockets |
| c_ram.centurion |  |  | gun_105_ags | 19.0 | gun_105_wheeled_he | 8.0 | lancet | 20.0 | mlrs_rockets |
| c_ram.dome |  |  | gun_105_ags | 19.0 | gun_105_wheeled_he | 8.0 | lancet | 20.0 | mlrs_rockets |

*15 / 60 dòng đầu: xem sheet 04_can_cu_thap/Tuong_duong_xe_cong_trinh; in 10 / 13 cột; 1 cột khác (và raw_json, nguon): xem sheet.*

### Tuong_vu_khi

Trạng thái: Chưa áp — không có trong mã và dữ liệu

Nguồn dữ liệu: 04_can_cu_thap/Tuong_vu_khi.

Sheet: 04_can_cu_thap/Tuong_vu_khi — Tường: bệ vũ khí phụ (1 dòng, 8 cột)

| id | tuong_id | trang_thai | ghi_chu |
|---|---|---|---|
| KHONG_CO | KHONG_CO | KHONG_CO | không loại tường nào có bệ phụ (secondary[]) trong balance.… |
