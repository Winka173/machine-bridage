# 02_phuong_tien — Phương tiện

Bộ xuất dữ liệu Machine Brigade, commit 90337539, ngày 2026-10-03. Sinh bởi `python Tools/export/export.py` (lượt 6): bảng in đúng ô của csv / xlsx; văn bản lấy từ tài liệu thiết kế (Tools/docs) và chuỗi trong game. Toàn văn: Machine_Brigade_Design_FULL_2026-10-03.md.

Xe, bệ vũ khí, thẻ hỗ trợ, kỹ năng, trang bị, commander, đội mở màn, xe tham chiếu, hệ số độ bền

Mục trong file này: 8. Phương tiện; 9. Bảng DPS tổng hợp; 12. Hỗ trợ hỏa lực; 12b. Bảng giá, hệ đạn và hồi đạn; 12c. Commander; 13. Trang bị.

## 8. Phương tiện

Trạng thái: Đã áp

Nguồn dữ liệu: 02_phuong_tien/Xe; 02_phuong_tien/Xe_vu_khi; 02_phuong_tien/Xe_bo_phan; 02_phuong_tien/Xe_ten_lua; 02_phuong_tien/Nhanh_xe; 02_phuong_tien/Ky_nang; 02_phuong_tien/Tinh_nhue_luat; 02_phuong_tien/May_bay_so_phat; 02_phuong_tien/Do_ben. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §8. Phương tiện, §8b.

#### 8. Phương tiện

Chỉ số gốc (hạng 1, chưa trang bị). DPS = sát thương mỗi loạt / chu kỳ bắn, cộng mọi vũ khí, nhân hệ số giáp (phần 10). Hạng thẻ cộng +5% máu và sát thương mỗi hạng (tối đa hạng 10: +45%).

**Nguồn tham khảo.** Dòng "Tham khảo" trên mỗi thẻ (xe, xe tinh nhuệ, tháp, nhánh hạng 7, boss) ghi hệ thống ngoài đời thật và phim hoặc game mà model được dựng theo, lấy từ Tools/docs/unit_refs.json. Tệp này tổng hợp từ các tham chiếu chủ dự án yêu cầu trong DECISIONS.md (19R, 19U, 20V, 20Y, 21H), chú thích của các script dựng model Blender, tên thật của vũ khí trong balance.json và kiến thức chung về khí tài; mục ghi "ước đoán" là suy đoán, chưa có nguồn ghi rõ.

![Model thường và model chi tiết (đồ họa Cao) của 12 xe phổ biến nhất.](../images/02_phuong_tien/shots_hd.png)

*Hình: Model thường và model chi tiết (đồ họa Cao) của 12 xe phổ biến nhất. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

#### 8b. Miêu tả, hình dạng và mở khóa

Miêu tả: dòng Cách đánh và Mạnh / yếu của thẻ Hướng dẫn trong game. Hình dạng: cột "Hình dạng (cho AI vẽ)" của file cân bằng (sheet Phương tiện, Công trình, Boss), bản mô tả để dựng model (Tools/docs/unit_sheet.json). Mở khóa: theo dữ liệu chiến dịch sau prompt 25 D2 (màn mở, giá mua sớm, chiến lợi phẩm cốt truyện).

#### Boss (41)

| Đơn vị | Miêu tả | Hình dạng (bản vẽ) | Mở khóa |
|---|---|---|---|
| **Bastion Mk.0 · Pháo đài nguyên mẫu** `bastion_mk0` | chiếc Bastion đầu tiên của Brandt: một khẩu cối hạng nặng và hai tháp pháo 40 mm trên xích, bò chậm về phía căn cứ ta. mặt trước dày, chậm; hai tháp pháo là thứ phòng thủ gần duy nhất. | Dựa trên: 2B8 240 mm, Bofors 40 mm · Sandcrawler (Star Wars) — ước đoán: bản đầu, nhỏ của Bastion. Kích thước hiện 24.0 × 9.9 × 9.7 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss chủ lực… | — |
| **Inferno · Behemoth phun lửa** `behemoth_inferno` | hai súng phun lửa lớn (20 m) đốt cháy mặt đất; hộp rốc-két nhiệt áp đánh tầm 10–46 m; còn 70% máu gọi 2 tăng tinh nhuệ. thiêu chảy xe nhẹ và xe tăng tới gần; yếu trước máy bay vì chỉ có một khẩu pháo… | Dựa trên: TOS-1A, Object 279 (1959) · Baneblade (Warhammer 40,000) — ước đoán: Behemoth phun lửa, thùng nhiên liệu đỏ. Kích thước hiện 17.0 × 8.8 × 7.5 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss… | — |
| **Harpy · Trực thăng khổng lồ** `mega_gunship` | hai giàn rốc-két, hai pháo 30 mm, một súng máy nhiều nòng và mỗi bên cửa một súng máy 12,7 mm; thả mồi nhiệt liên tục, hộ tống là 2 trực thăng tấn công và 1 trực thăng trinh sát vũ trang đánh dấu mục… | Dựa trên: CH-47 Chinook (cỡ khung), ACH-47A 'Guns-A-Go-Go' — ước đoán (ACH-47A): trực thăng hai rô-to vũ trang hạng nặng. Kích thước hiện 23.6 × 15.3 × 7.0 m; boss chủ lực ×1,3–1,5 so với mẫu, mini b… | — |
| **Fenrir · Xe tiên phong** `fenrir` | nhanh: lao vào, xả hai hộp rốc-két rồi rút; cao xạ đuổi trực thăng. nhẹ hơn Jötunn nhiều; không giữ trận địa được. | Dựa trên: NASA Crawler-Transporter, Kharkovchanka (1959) · Sandcrawler (Star Wars) — ước đoán: biến thể của pháo đài di động. Kích thước hiện 16.2 × 9.1 × 8.3 m; boss chủ lực ×1,3–1,5 so với mẫu, min… | — |
| **Behemoth Mk.0 · Behemoth nguyên mẫu** `behemoth_mk0` | bản lắp đầu tiên của Behemoth, chậm hơn bản hoàn chỉnh: pháo chính, hai pháo sườn và một giàn rốc-két trên cùng thân xe. mặt trước giáp cấp 3; không có pháo cao xạ và hệ thống bảo vệ chủ động, nên má… | Dựa trên: Object 279 (1959), giáp composite, APS và cảm biến hiện đại · Baneblade (Warhammer 40,000) — ước đoán: Behemoth đời đầu, nhỏ hơn. Kích thước hiện 17.0 × 10.1 × 7.3 m; boss chủ lực ×1,3–1,5… | — |
| **Juggernaut · Đoàn tàu bọc thép** `armored_train` | hai pháo nặng (42 m), hộp rốc-két, hai pháo cao xạ và súng máy; bị bắn thì núp trong khói, còn nửa máu thì tự vá 20% một lần. pháo của nó diệt xe tăng và xe nhẹ gần đường ray; nó không thể rời đường… | Dựa trên: tàu bọc thép Liên Xô BP-35, B-38 152 mm, 2B11 120 mm — ước đoán: đầu máy diesel bọc thép kéo toa pháo. Kích thước hiện 24.5 × 3.3 × 4.8 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơ… | — |
| **Tempest · Behemoth pháo điện từ** `behemoth_tempest` | pháo điện từ nạp năng lượng một giây (cuộn dây sáng lên) rồi xuyên thủng cả hàng tới 80 m; hai pháo điện từ bắn đất lẫn trời (55 m). trừng phạt xe đi thành hàng dọc; ở gần, EMP (22 m) làm choáng xe m… | Dựa trên: US Navy EMRG (pháo điện từ), Object 279 (1959) · Baneblade (Warhammer 40,000) — ước đoán: Behemoth hai tháp pháo điện từ. Kích thước hiện 17.0 × 7.0 × 6.8 m; boss chủ lực ×1,3–1,5 so với mẫ… | — |
| **Scylla · Tàu khu trục** `scylla` | nhanh hơn Leviathan, chạy tuyến gần bờ: pháo AK-130 130 mm đôi nã vào bờ, ống phóng bắn tên lửa chống hạm mỗi 15 giây, CIWS chặn tên lửa và drone. đủ gần để pháo xe tăng ở đầu cầu tàu bắn tới. | Dựa trên: Sovremenny-class (khu trục hạm), Kirov-class — Bản nhỏ của Leviathan. Kích thước hiện 48.8 × 9.2 × 14.2 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss chủ lực cùng dòng; bộ phậ… | — |
| **Nyx · Tàu khu trục tàng hình** `nyx` | tạm dùng thân Leviathan thu nhỏ. Pháo điện từ bắn mỗi 8 giây, hai CIWS chặn tên lửa và drone, rồi tới tên lửa chống hạm. Nó tàng hình: chỉ thấy ở gần hoặc ngay sau khi bắn. khó thấy; mỏng so với kích… | — | — |
| **Hive · Pháo đài drone** `fortress_hive` | không có pháo lớn: hai giàn phóng bầy drone tới 70 m, dàn tên lửa (62 m) và pháo cao xạ giữ bầu trời, còn thả thêm UAV tấn công. xé nát máy bay; drone của nó hại được xe tăng, nhưng xe tăng và pháo b… | Dựa trên: NASA Crawler-Transporter, ZALA Lancet-3, MIM-104 Patriot · Sandcrawler (Star Wars) — ước đoán: pháo đài bánh xích mang tổ drone. Kích thước hiện 16.4 × 9.3 × 8.5 m; boss chủ lực ×1,3–1,5 so… | — |
| **Locust · Tàu con drone** `locust` | khoang drone thả drone liên tục; cao xạ trên lưng. thân rất mỏng (giáp cấp 1): phòng không hạ nó nhanh. | Dựa trên: Airlander 10, drone FPV · Kirov Airship (Red Alert 2) — ước đoán: biến thể nhỏ của khí cầu mẹ. Kích thước hiện 25.4 × 12.6 × 10.6 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss… | — |
| **Stymphalos · Bầy UAV phản lực** `stymphalos` | tạm là một thân với khoang drone và cao xạ của tàu mẹ, nhanh. Nó bắn tên lửa nhỏ và thả drone liên tục. rất nhanh; giáp mỏng, phòng không hạ nó nhanh. | — | — |
| **Bastion · Pháo đài** `fortress_bastion` | khẩu cối hạng nặng bắn tầm 12–80 m, bốn tháp pháo tự động 40 mm (28 m) phủ mọi hướng, hai súng máy NSV giữ hai bên hông, còn nửa máu nó tự vá giáp một lần. pháo tự động xé nát xe nhẹ tới gần; giáp dà… | Dựa trên: 2B8 240 mm, Bofors 40 mm, 9M133 Kornet · Sandcrawler (Star Wars) — ước đoán: pháo đài bánh xích bọc giáp tấm dày. Kích thước hiện 40.0 × 16.5 × 16.1 m; boss chủ lực ×1,3–1,5 so với mẫu, min… | — |
| **Charybdis · Tàu đệm khí đổ bộ** `landing_hovercraft` | chạy theo lộ trình dọc bờ biển; cứ 35 giây dừng lại, hạ cửa đổ bộ và thả 3–4 xe lên bờ, tối đa năm lần. Bốn pháo CIWS sáu nòng che chắn cả đất lẫn trời (hai khẩu bắn hạ tên lửa và rốc-két) và hai dàn… | Dựa trên: LCAC, Zubr (Project 1232.2), A-22 Ogon 140 mm, AK-630 — Tàu đổ bộ đệm khí. Kích thước hiện 24.9 × 13.5 × 7.7 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss chủ lực cùng dòng; b… | — |
| **Behemoth Mk.II · Behemoth nâng cấp** `behemoth_mk2` | bản nâng cấp của Varga sau khi Behemoth gục: pháo chính, hai cao xạ và hệ thống bảo vệ chủ động bắn hạ tên lửa. mặt trước giáp cấp 4 dưới lớp băng; hông và sau mỏng hơn nhiều. | Dựa trên: Object 279 (1959), giáp composite, APS và cảm biến hiện đại · Baneblade (Warhammer 40,000) — ước đoán: Behemoth đời hai. Kích thước hiện 18.0 × 10.7 × 7.7 m; boss chủ lực ×1,3–1,5 so với mẫ… | — |
| **Cerberus · Đoàn xe ba khung** `cerberus` | tạm dùng thân Behemoth (pháo, cao xạ, ổ rốc-két). Pháo đầu bắn xe mặt đất, cao xạ giữa đuổi máy bay, ổ rốc-két sau phủ một vùng. mỗi bộ phận là một vũ khí riêng; chậm. | — | — |
| **Behemoth · Quái vật thép** `behemoth` | pháo chính hai nòng (40 m), pháo 120 mm, pháo cao xạ, tên lửa bắn cả đất lẫn trời (45 m) và bệ Kornet đôi sau tháp chính; còn 70% máu gọi 2 tăng tinh nhuệ. nghiền nát xe nhẹ và xe tăng; khắc tinh là… | Dựa trên: Object 279 (1959: bốn dải xích, thân dẹt), giáp composite, APS và cảm biến hiện đại, 2A65 152 mm · Baneblade (Warhammer 40,000) — ước đoán: 'thiết giáp hạm trên cạn' bốn cụm xích. Kích thướ… | — |
| **Atlas · Xe chỉ huy siêu nặng** `supreme_command` | chỉ có hai súng máy nhẹ; mọi quân địch trong 40 m quanh nó tăng 20% sát thương và 20% tốc độ bắn. Có cận vệ tinh nhuệ đi kèm, còn 60% máu thì gọi thêm. quân địch gần nó nguy hiểm hơn nhiều; bản thân… | Dựa trên: khung MZKT-7930, sở chỉ huy cơ động bọc thép — Tổng Tư Lệnh: xe chỉ huy siêu nặng bốn trục. Kích thước hiện 16.0 × 5.5 × 12.2 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss chủ… | — |
| **Tartarus · Máy khoan** `earth_borer` | chui xuống đất, khoan ngầm không bị nhắm tới dưới cụm xe mặt đất đông nhất của bạn, mặt đất nứt 2 giây rồi nó trồi lên gây rung chấn làm choáng mọi xe mặt đất trong 15 m. Mũi khoan và hai khẩu pháo k… | Dựa trên: 'Battle Mole' của Liên Xô, máy khoan hầm TBM, 2A70 100 mm — 'Earth Worm': máy khoan đất bọc thép ba đốt. Kích thước hiện 19.9 × 4.9 × 5.9 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ… | — |
| **Ixion · Xe tải mỏ bọc thép** `ixion` | xe tải mỏ bọc thép (BelAZ-75710) chạy thẳng khoảng 7 m/s và xoay rất chậm. Tháp pháo 125 mm hàn trên thùng xoay 360°, nạp đạn nổ mạnh với đám đông (nổ lõi 5 m, rìa 10 m) và đạn xuyên với mục tiêu đơn… | Dựa trên: BelAZ-75710 (xe tải mỏ lớn nhất thế giới), tháp pháo T-72 125 mm hàn trên thùng — Xe tải mỏ bọc thép của Thorne ở Deepcut Mine: ca-bin lệch trái, sáu bánh lớn, lưỡi húc chữ V (model tạm). K… | — |
| **Jötunn · Pháo đài di động** `mobile_fortress` | hai lựu pháo 203 mm (60 m), hộp rốc-két, pháo cao xạ, tháp 30 mm đôi chống drone và tên lửa; EMP làm choáng xe mặt đất trong 22 m; hộ tống là 2 tăng nặng và 1 xe công binh sửa cho nó, còn nửa máu thê… | Dựa trên: NASA Crawler-Transporter, Kharkovchanka (1959), 2A44 203 mm (2S7 Pion) · Sandcrawler (Star Wars) — ước đoán: pháo đài bánh xích bốn cụm, cầu chỉ huy lắp kính. Kích thước hiện 32.0 × 18.1 ×… | — |
| **Caspian · Tàu bay sát mặt nước** `caspian` | lao dọc bờ khoảng 6 giây mỗi lượt rồi vòng ra xa khoảng 20 giây; là mục tiêu trên mặt nước. Mỗi lượt lao nó phóng một tên lửa chống hạm vào cụm quân lớn nhất (có đánh dấu trước); hai pháo 23 mm đôi v… | Dựa trên: ekranoplan lớp Lun MD-160 ('Quái vật biển Caspi') — Thủy phi cơ hiệu ứng mặt đất. Kích thước hiện 36.0 × 26.5 × 10.9 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss chủ lực cùng… | — |
| **Hydra · Tàu ngầm mang drone** `hydra` | tạm dùng thân Typhon (pháo boong và cửa ống phóng, nhỏ và nhanh hơn). Nó lặn rồi nổi theo lịch ngắn, chỉ bắn khi nổi, và phóng tên lửa hành trình mỗi 16 giây. lúc lặn không đánh tới được; thân mỏng. | — | — |
| **Morrigan · Tiêm kích của Raven** `morrigan` | nhanh hơn mọi tiêm kích của ta và tàng hình: chỉ bị phát hiện ở cự ly gần, hoặc trong chốc lát sau khi khai hỏa. Tên lửa không đối không từ hai khoang săn máy bay của bạn; bom dẫn đường săn xe phòng… | Dựa trên:. Kích thước hiện 12.9 × 8.4 × 2.2 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss chủ lực cùng dòng; bộ phận phá được (tháp, xích, động cơ) phải tách thành khối riêng dễ nhìn; c… | — |
| **Spectre · Máy bay pháo** `sky_fortress` | bay vòng quanh mục tiêu, pháo 105 mm, hai 40 mm và một 25 mm bắn từ bên trái (50–58 m), kèm Griffin; không bắn được máy bay. hủy diệt quân mặt đất nằm dưới vòng bay; chỉ phòng không và tiêm kích với… | Dựa trên: AC-130 Spectre — Pháo hạm bay AC-130 phóng to 1,3 lần, sơn tối. Kích thước hiện 15.5 × 21.2 × 6.1 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss chủ lực cùng dòng; bộ phận phá… | — |
| **Icarus Mk.0 · Phi thuyền nguyên mẫu** `icarus_mk0` | không lên quỹ đạo: đổi tầng cao và thấp theo lịch cố định. Một tháp la-de, một khoang đổ bộ và một la-de phòng thủ điểm bắn hạ tên lửa. ở tầng cao chỉ phòng không tầm xa và tiêm kích bắn tới; ở tầng… | Dựa trên: Polyus / Skif-DM, ISS, Hubble · SOLG (Ace Combat 5), The Expanse — Bản đầu của Icarus (trạm vũ khí quỹ đạo, nhỏ hơn). Kích thước hiện 36.0 × 18.1 × 13.0 m; boss chủ lực ×1,3–1,5 so với mẫu,… | — |
| **Argus · Khí cầu trinh sát** `argus` | khi nó còn, pháo binh địch tản mát chỉ khoảng một nửa. Cao xạ và radar. chậm và to; chỉ phòng không và tiêm kích bắn tới. | Dựa trên: JLENS (khí cầu radar neo) · Kirov Airship (Red Alert 2) — ước đoán: biến thể của khí cầu chỉ huy, khí cầu radar neo. Kích thước hiện 35.0 × 24.2 × 12.4 m; boss chủ lực ×1,3–1,5 so với mẫu,… | — |
| **Leviathan · Thiết giáp hạm** `leviathan` | ba tháp pháo ba nòng 406 mm bắn loạt vào bờ, mỗi tháp một nòng, có cảnh báo trước và quét dần dọc bờ, và bắn cả chín nòng theo dải qua căn cứ khi tung siêu vũ khí; hai tháp ba nòng 155 mm tự bắn, tám… | Dựa trên: Iowa-class hiện đại hóa thập niên 1980 (Mk 7 406 mm), Kirov-class (bệ phóng thẳng đứng) — Thiết giáp hạm lớp Iowa hiện đại hóa, thêm bệ phóng thẳng đứng kiểu Kirov. Kích thước hiện 97.6 × 1… | — |
| **Matriarch · Tàu mẹ drone** `drone_mothership` | pháo và bầy drone cảm tử từ ba khoang phóng (70 m) đánh mặt đất, pháo cao xạ chống máy bay; cứ 30 giây phóng ra 3 UAV tấn công. nhấn chìm mặt đất bằng drone; chỉ phòng không và tiêm kích gây sát thươ… | Dựa trên: Airlander 10 (khí cầu mẹ hiện đại), drone FPV · Kirov Airship (Red Alert 2) — ước đoán: khí cầu bọc thép phóng drone. Kích thước hiện 55.0 × 27.3 × 23.1 m; boss chủ lực ×1,3–1,5 so với mẫu,… | — |
| **Moloch · Nhà máy di động** `moloch` | bò chậm theo đường của nhiệm vụ; hai cửa xưởng cứ 20 giây thả 1–2 xe (xe tăng nhẹ và xe bộ binh, từ pha 2 thêm tăng chủ lực), mỗi phút thêm một xe mỗi lượt, tối đa sáu xe còn sống. Bốn tháp pháo 120… | Dựa trên: xưởng cơ động bánh xích · Fatboy (Supreme Commander), MCV / War Factory (Command & Conquer) — ước đoán: nhà máy di động. Kích thước hiện 40.0 × 21.7 × 18.1 m; boss chủ lực ×1,3–1,5 so với m… | — |
| **Nemesis · Đoàn tàu tên lửa** `nuke_train` | pháo nặng hai nòng (40 m), toa pháo 152 mm và ba pháo cao xạ; bị bắn thì núp trong khói; phía sau có toa rốc-két và toa SAM tầm xa, xe bọc thép hộ tống chạy dọc đường ray. pháo của nó phá nát mọi thứ… | Dựa trên: RT-23 Molodets (tàu tên lửa BZhRK), MIM-104 Patriot — ước đoán: đoàn tàu bọc thép mang tên lửa đạn đạo. Kích thước hiện 70.0 × 5.8 × 8.4 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ h… | — |
| **Kronos · Máy xúc mỏ** `kronos` | chạy rất chậm theo đường cố định về căn cứ ta; bánh gầu nghiền mọi thứ phía trước (900 mỗi giây trong 6 m), cả tường lẫn tháp (gấp ba). Tới được HQ là thua nhiệm vụ. Hai tháp 30 mm, hai tháp pháo 57… | Dựa trên: Bagger 288 — Máy xúc gầu quay khổng lồ. Kích thước hiện 60.0 × 20.0 × 19.8 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss chủ lực cùng dòng; bộ phận phá được (tháp, xích, động… | — |
| **Monster · Pháo tự hành 800 mm** `monster` | tạm dùng thân Bastion (tháp pháo và khẩu cối, to hơn). Nó bò rất chậm, cứ 80 giây nòng 800 mm nâng lên bắn một quả 4.000 sát thương, nổ lan 20 m. giáp và máu khổng lồ, nhưng chậm hơn mọi boss. | — | — |
| **Typhon · Tàu ngầm tên lửa** `typhon` | lặn (không bắn tới được) và nổi (mục tiêu trên mặt nước) theo lịch từng pha, mỗi lần nổi ở một chỗ khác; bong bóng báo trước chỗ nổi. Khi nổi nó phóng tên lửa hành trình tầm ngắn mỗi 12 giây và tự vệ… | Dựa trên: Project 941 Akula (Typhoon) · The Hunt for Red October (1990) — Tàu ngầm tên lửa. Kích thước hiện 70.0 × 14.5 × 16.7 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss chủ lực cùng… | — |
| **Kraken · Tàu sân bay** `kraken` | tạm dùng thân tàu Leviathan (pháo, ống phóng tên lửa và CIWS). Boong cất cánh phóng tiêm kích và drone, và cứ 75 giây nó gọi một đợt không kích. thân tàu dài và dày nhất mặt nước; boong thang máy mỏn… | — | — |
| **Roc · Khí cầu chỉ huy** `command_airship` | hai tháp pháo phòng không 57 mm, hai tháp 30 mm đôi dưới bụng, drone từ hai nhà chứa và thỉnh thoảng mỗi nhà chứa thả một UAV tấn công. Mỗi bộ phận có máu riêng: thân không nhận sát thương cho tới kh… | Dựa trên: Airlander 10, Lockheed P-791 (khí cầu lai hiện đại) · Kirov Airship (Red Alert 2) — ước đoán: 'Sky Admiral', thiết giáp hạm bay hai túi khí. Kích thước hiện 80.0 × 55.4 × 28.3 m; boss chủ l… | — |
| **Garuda · Cánh bay ném bom khổng lồ** `garuda` | tạm dùng thân khí cầu chỉ huy (tháp súng và drone). Tháp phòng thủ và tên lửa đuổi máy bay; cứ 70 giây nó rải thảm 20 quả bom. mục tiêu rộng, nhiều súng; chỉ phòng không tầng thấp mới trúng tốt. | — | — |
| **Gungnir · Pháo điện từ đường ray** `rail_supergun` | cứ 25 giây một phát điện từ vào cụm xe mặt đất đông nhất của bạn, ở bất cứ đâu trên bản đồ: nó xuyên qua tối đa năm xe trên một đường thẳng (1.000 mỗi xe) rồi nổ ở xe cuối (2.000 trong lõi 12 m, còn… | Dựa trên: US Navy EMRG (pháo điện từ, phóng to), đoàn tàu BZhRK Barguzin, đầu máy diesel hiện đại — Pháo điện từ siêu nặng trên đường ray: toa pháo ray điện từ, các toa tụ điện, đầu máy diesel; mỗi 2… | — |
| **Daedalus · Tàu đổ bộ quỹ đạo** `daedalus` | khoảng 10 giây trên quỹ đạo (không bắn tới được), sau đó đổi tầng cao và thấp theo lịch cố định, không lên lại quỹ đạo. Ba cửa thả khoang thả liên tục khoang chở 1–2 xe (tối đa tám xe còn sống); khoa… | Dựa trên: Acclamator-class (Star Wars: Attack of the Clones) — Tàu đổ bộ tấn công của Aurel. Kích thước hiện 60.0 × 33.0 × 20.7 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss chủ lực cùn… | — |
| **Icarus · Phi thuyền quỹ đạo** `silver_bug` | tháp la-de chính và hai pháo coilgun bắn xuống mặt đất ở cả tầng cao lẫn tầng thấp; khoang đổ bộ thả xe xuống; cứ 60 giây có 7 thanh vonfram rơi từ vệ tinh của nó (khi đã rơi xuống đất: 9 thanh mỗi 5… | Dựa trên: Polyus / Skif-DM (trạm vũ khí quỹ đạo Liên Xô, 1987), ISS (giàn chính, cánh pin mặt trời, tấm tản nhiệt), Hubble / KH-11 (ống kính, cửa. Kích thước hiện 90.0 × 45.2 × 32.5 m; boss chủ lực ×… | — |
| **Hyperion · Trạm gương quỹ đạo** `hyperion` | tạm dùng thân Silver Bug (chỉ ở tầng cao). Tháp la-de phòng thủ điểm che chắn, mỗi phút thả hai khoang đổ bộ, cứ 65 giây một tia mặt trời đốt dải 70 × 6 m trong 4 giây. không bao giờ xuống tầng thấp,… | — | — |

Sheet: 02_phuong_tien/Xe — Xe (120 dòng, 193 cột)

| id | loai_thuc_the | ten_en | ten_vi | ten_ngan_vi | lop | nhanh | base_cp | mau_hp | mau_trong_tran_hp |
|---|---|---|---|---|---|---|---|---|---|
| aa_57mm_vehicle | xe | 57 mm AA vehicle | Xe phòng không 57 mm | PK 57 mm | AntiAir | Light | 7 | 759 | 1669.8 |
| aa_gun_vehicle | xe | 40 mm AA gun vehicle | Xe cao xạ 40 mm | Cao xạ 40 mm | AntiAir | Light | 6 | 559 | 1229.8 |
| aa_vehicle | xe | Self-propelled AA gun | Pháo cao xạ tự hành | Cao xạ |  |  | 4 | 350 | 770.0 |
| aerial_tanker | xe | Aerial tanker | Máy bay tiếp dầu | Tiếp dầu |  |  | 9 | 1300 | 2860.0 |
| airborne_light_tank | xe | Airborne light tank | Tăng nhẹ thả dù | Tăng thả dù | Tank | Armor | 6 | 727 | 1599.4 |
| airborne_light_tank_chute | vat_pham |  |  |  | Tank | Armor | 0 | 591 | 1300.2 |
| airborne_vehicle | xe | Airborne fighting vehicle | Xe đổ bộ đường không | Xe đổ bộ | Light | Light | 7 | 595 | 1309.0 |
| airborne_vehicle_chute | vat_pham |  |  |  | Light | Light | 0 | 500 | 1100.0 |
| ammo_carrier | xe | Ammo carrier | Xe tiếp đạn | Tiếp đạn | Support | Light | 4 | 520 | 1144.0 |
| amphib_light_vehicle | xe | Amphibious light vehicle | Xe lội nước tốc độ cao | Xe lội nước |  |  | 7 | 650 | 1430.0 |
| armored_bulldozer | xe | Armoured bulldozer | Xe ủi bọc thép | Xe ủi | Heavy | Armor | 8 | 1514 | 3330.8 |
| armored_car | xe | Armoured car | Xe bọc thép bánh lốp | Bánh lốp | Light | Light | 3 | 300 | 660.0 |
| artillery | xe | SP howitzer | Lựu pháo tự hành | Lựu pháo |  |  | 7 | 359 | 789.8 |
| attack_helicopter | xe | Attack helicopter | Trực thăng tấn công | TT tấn công |  |  | 11 | 1009 | 2219.8 |
| attack_jet | xe | Attack jet | Máy bay cường kích | Cường kích |  |  | 23 | 1127 | 2479.4 |

*15 / 120 dòng đầu: xem sheet 02_phuong_tien/Xe; in 10 / 193 cột; 87 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 02_phuong_tien/Xe_vu_khi — Xe: bệ vũ khí phụ (99 dòng, 11 cột)

| id | xe_id | thu_tu | weapon | aim | model | slot |
|---|---|---|---|---|---|---|
| aa_vehicle/0 | aa_vehicle | 0 | sam | Free | stinger | missile |
| airborne_vehicle/0 | airborne_vehicle | 0 | autocannon_30 | Turret |  | coax |
| armored_bulldozer/0 | armored_bulldozer | 0 | hmg_roof | Free |  | mg |
| armored_car/0 | armored_car | 0 | mg_coax | Turret |  | coax |
| artillery/0 | artillery | 0 | hmg_selfdef_15 | Free |  | mg |
| attack_helicopter/0 | attack_helicopter | 0 | heli_gun | Free |  | gun |
| attack_helicopter/1 | attack_helicopter | 1 | heli_rockets | Hull |  | rocket |
| attack_helicopter/2 | attack_helicopter | 2 | stinger_atas | Free |  | aam |
| attack_helicopter/3 | attack_helicopter | 3 | apkws_rocket | Free |  | rocket2 |
| attack_jet/0 | attack_jet | 0 | s8_pods | Hull |  | rocket |
| attack_jet/1 | attack_jet | 1 | jet_bombs | Hull |  | missile |
| attack_jet/2 | attack_jet | 2 | kh29 | Hull |  | missile |
| attack_jet/3 | attack_jet | 3 | r60 | Free |  | aam |
| bmpt/0 | bmpt | 0 | mg_coax | Turret |  | coax |
| bmpt/1 | bmpt | 1 | ataka | Turret |  | missile |

*15 / 99 dòng đầu: xem sheet 02_phuong_tien/Xe_vu_khi.*

Sheet: 02_phuong_tien/Xe_bo_phan — Xe: bộ phận (6 dòng, 17 cột)

| id | xe_id | thu_tu | armour | at_x_m | at_y_m | at_z_m | hp | id_goc | kind |
|---|---|---|---|---|---|---|---|---|---|
| sea_corvette/ciws | sea_corvette | 1 | 2 | 0 | -6.5 | 7.0 | 0.12 | ciws | ciws |
| sea_corvette/gun | sea_corvette | 0 | 2 | 0 | 9 | 4.2 | 0.14 | gun | gun |
| sea_cruiser/ciws_aft | sea_cruiser | 3 | 2 | -2.2 | -6.1 | 5.9 | 0.1 | ciws_aft | ciws |
| sea_cruiser/ciws_fore | sea_cruiser | 2 | 2 | 2.2 | 4.3 | 6.6 | 0.1 | ciws_fore | ciws |
| sea_cruiser/turret_aft | sea_cruiser | 1 | 3 | 0 | -11.5 | 4.0 | 0.12 | turret_aft | gun |
| sea_cruiser/turret_fore | sea_cruiser | 0 | 3 | 0 | 13.7 | 4.0 | 0.12 | turret_fore | gun |

*in 10 / 17 cột; 5 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 02_phuong_tien/Xe_ten_lua — Xe: tên lửa mang (5 dòng, 8 cột)

| id | xe_id | thu_tu | ammo | reload_s | weapon |
|---|---|---|---|---|---|
| bmpt/0 | bmpt | 0 | 4 | 30 | ataka |
| ifv/0 | ifv | 0 | 2 | 20 | atgm |
| light_tank/0 | light_tank | 0 | 2 | 25 | gun_launched_atgm |
| nlos_atgm_vehicle/0 | nlos_atgm_vehicle | 0 | 2 | 25 | spike_nlos |
| titan_tank/0 | titan_tank | 0 | 4 | 30 | atgm |

Sheet: 02_phuong_tien/Nhanh_xe — Nhánh quân (4 dòng, 4 cột)

| id | lop |
|---|---|
| Air | Helicopter;Plane |
| Armor | Tank;Heavy;TankHunter |
| Artillery | Artillery |
| Light | Light;Scout;AntiAir;Support |

Sheet: 02_phuong_tien/Ky_nang — Kỹ năng nội tại (24 dòng, 14 cột)

| id | dung_boi | amount | cooldown_s | count | duration_s | kind | once | radius_m | threshold |
|---|---|---|---|---|---|---|---|---|---|
| airship_launch_l | command_airship;garuda |  | 30 | 1 |  | Summon |  | 80 |  |
| airship_launch_r | command_airship;garuda |  | 30 | 1 |  | Summon |  | 80 |  |
| apc_smoke | ifv |  | 30 |  | 8 | Smoke |  | 7 |  |
| bomber_flares | glide_bomber;heavy_bomber;sky_gunship;swarm_carrier |  | 11 |  | 3 | Flares |  |  |  |
| boss_bulwark | bastion_mk0;behemoth;behemoth_mk0;behemoth_mk2;behemoth_tem… | 0.5 | 30 |  | 6 | Shield |  |  | 0.35 |
| boss_emp | behemoth_tempest;fenrir;fortress_hive;mobile_fortress |  | 35 |  | 4 | Emp |  | 22 |  |
| boss_flares | drone_mothership;locust;mega_gunship;morrigan;sky_fortress;… |  | 10 |  | 3 | Flares |  |  |  |
| boss_rage | behemoth;behemoth_inferno;behemoth_mk2;cerberus;daedalus;ea… | 1.2 |  |  | 9999 | Overdrive | TRUE |  | 0.5 |
| elite_barrage | elite_artillery;elite_attack_helicopter;elite_fpv_carrier;e… | 2.2 | 28 |  | 6 | Barrage |  |  |  |
| elite_emp | elite_apc |  | 30 |  | 3.5 | Emp |  | 14 |  |
| elite_flares | elite_attack_helicopter;elite_attack_jet |  | 14 |  | 3 | Flares |  |  |  |
| elite_overdrive | elite_aa;elite_heavy_tank;elite_long_sam | 1.5 | 25 |  | 6 | Overdrive |  |  |  |
| elite_repair |  | 0.3 | 30 |  | 8 | Repair |  |  | 0.5 |
| elite_shield | elite_mbt | 0.3 | 20 |  | 5 | Shield |  |  |  |
| elite_smoke | elite_tank_destroyer |  | 30 |  | 8 | Smoke |  | 9 | 0.55 |
| fortress_barrage | bastion_mk0;fenrir;fortress_bastion;mobile_fortress;monster | 2 | 25 |  | 8 | Barrage |  |  | 0.4 |
| heli_flares | attack_helicopter;gunship_heli |  | 20 |  | 1.5 | Flares |  |  |  |
| jet_flares | attack_jet;fighter_jet;interceptor_jet;stealth_fighter |  | 16 |  | 1.5 | Flares |  |  |  |
| leviathan_helos | kraken;leviathan;nyx;scylla |  | 55 | 1 |  | Summon |  |  | 0.7 |
| mothership_launch | drone_mothership;fortress_hive;locust;stymphalos |  | 30 | 3 |  | Summon |  | 70 |  |
| mothership_shield | behemoth_tempest;drone_mothership;locust;stymphalos | 0.5 | 30 |  | 8 | Shield |  |  | 0.5 |
| smoke_generator | smoke_carrier |  | 11 |  | 11 | Smoke |  | 11 |  |
| train_patch | armored_train;bastion_mk0;fortress_bastion;monster | 0.5 |  |  |  | Patch | TRUE |  |  |
| train_smoke | armored_train;behemoth_inferno;nuke_train |  | 25 |  | 8 | Smoke |  | 12 |  |

*in 10 / 14 cột; 2 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 02_phuong_tien/Tinh_nhue_luat — Luật tinh nhuệ (20 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so |
|---|---|---|---|
| blueprintChance | elites | blueprintChance | 0.06 |
| bountyCap | elites | bountyCap | 4 |
| budget.Easy | elites | Easy | 0.05 |
| budget.Hard | elites | Hard | 0.15 |
| budget.Heroic | elites | Heroic | 0.2 |
| budget.Iron | elites | Iron | 0.25 |
| budget.Normal | elites | Normal | 0.1 |
| budget.VeryHard | elites | VeryHard | 0.3 |
| cap.Easy | elites | Easy | 1 |
| cap.Hard | elites | Hard | 3 |
| cap.Heroic | elites | Heroic | 4 |
| cap.Iron | elites | Iron | 5 |
| cap.Normal | elites | Normal | 2 |
| cap.VeryHard | elites | VeryHard | 6 |
| coins | elites | coins | 10 |
| costScale | elites | costScale | 1.6 |
| damageScale | elites | damageScale | 1.25 |
| hpScale | elites | hpScale | 1.6 |
| otherShare | elites | otherShare | 0.5 |
| powerRatio | elites | powerRatio | 2.0 |

Sheet: 02_phuong_tien/May_bay_so_phat — Máy bay: số phát để hạ (26 dòng, 15 cột)

| id | mau_hp | giap | sat_thuong_phat_stinger | sat_thuong_phat_stinger_game | so_phat_stinger | sat_thuong_phat_buk | sat_thuong_phat_buk_game | so_phat_buk | sat_thuong_phat_ten_lua_tiem_kich |
|---|---|---|---|---|---|---|---|---|---|
| aerial_tanker | 2860.0 | 0 | 221.0 | 221.0 | 13.0 | 416.0 | 416.0 | 7.0 | 382.2 |
| airborne_light_tank_chute | 1300.2 | 2 | 187.85 | 187.85 | 7.0 | 416.0 | 416.0 | 4.0 | 382.2 |
| airborne_vehicle_chute | 1100.0 | 1 | 221.0 | 221.0 | 5.0 | 416.0 | 416.0 | 3.0 | 382.2 |
| attack_helicopter | 2219.8 | 1 | 221.0 | 221.0 | 11.0 | 416.0 | 416.0 | 6.0 | 382.2 |
| attack_jet | 2479.4 | 2 | 187.85 | 187.85 | 14.0 | 416.0 | 416.0 | 6.0 | 382.2 |
| drop_pod | 352.0 | 1 | 221.0 | 221.0 | 2.0 | 416.0 | 416.0 | 1.0 | 382.2 |
| fighter_jet | 1480.6 | 0 | 221.0 | 221.0 | 7.0 | 416.0 | 416.0 | 4.0 | 382.2 |
| glide_bomber | 3009.6 | 1 | 221.0 | 221.0 | 14.0 | 416.0 | 416.0 | 8.0 | 382.2 |
| gunship_heli | 3619.0 | 2 | 187.85 | 187.85 | 20.0 | 416.0 | 416.0 | 9.0 | 382.2 |
| heavy_bomber | 4529.8 | 0 | 221.0 | 221.0 | 21.0 | 416.0 | 416.0 | 11.0 | 382.2 |
| heavy_lift_helicopter | 2101.0 | 1 | 221.0 | 221.0 | 10.0 | 416.0 | 416.0 | 6.0 | 382.2 |
| interceptor_jet | 1650.0 | 0 | 221.0 | 221.0 | 8.0 | 416.0 | 416.0 | 4.0 | 382.2 |
| light_attack_heli | 1280.4 | 0 | 221.0 | 221.0 | 6.0 | 416.0 | 416.0 | 4.0 | 382.2 |
| prop_attack_plane | 1049.4 | 1 | 221.0 | 221.0 | 5.0 | 416.0 | 416.0 | 3.0 | 382.2 |
| recon_drone | 840.4 | 0 | 221.0 | 221.0 | 4.0 | 416.0 | 416.0 | 3.0 | 382.2 |
| recon_jet | 919.6 | 0 | 221.0 | 221.0 | 5.0 | 416.0 | 416.0 | 3.0 | 382.2 |
| scout_heli | 1139.6 | 0 | 221.0 | 221.0 | 6.0 | 416.0 | 416.0 | 3.0 | 382.2 |
| sky_gunship | 4899.4 | 0 | 221.0 | 221.0 | 23.0 | 416.0 | 416.0 | 12.0 | 382.2 |
| stealth_bomber | 2640.0 | 0 | 221.0 | 221.0 | 12.0 | 416.0 | 416.0 | 7.0 | 382.2 |
| stealth_fighter | 1339.8 | 0 | 221.0 | 221.0 | 7.0 | 416.0 | 416.0 | 4.0 | 382.2 |
| stealth_naval_strike | 2019.6 | 0 | 221.0 | 221.0 | 10.0 | 416.0 | 416.0 | 5.0 | 382.2 |
| strike_drone | 1331.0 | 0 | 221.0 | 221.0 | 7.0 | 416.0 | 416.0 | 4.0 | 382.2 |
| swarm_carrier | 2400.2 | 1 | 221.0 | 221.0 | 11.0 | 416.0 | 416.0 | 6.0 | 382.2 |
| twin_rotor_gunship | 4670.6 | 1 | 221.0 | 221.0 | 22.0 | 416.0 | 416.0 | 12.0 | 382.2 |
| uav_loiter_strike | 550.0 | 0 | 221.0 | 221.0 | 3.0 | 416.0 | 416.0 | 2.0 | 382.2 |
| wingman_drone | 789.8 | 0 | 221.0 | 221.0 | 4.0 | 416.0 | 416.0 | 2.0 | 382.2 |

*in 10 / 15 cột; 3 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 02_phuong_tien/Do_ben — Hệ số độ bền (2 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so |
|---|---|---|---|
| bosses | toughness | bosses | 0.85 |
| vehicles | toughness | vehicles | 2.2 |

#### Lời hướng dẫn trong game theo đơn vị (02_phuong_tien/Xe; chuỗi guide.<id> của GuideText.cs)

- **PK 57 mm** (`aa_57mm_vehicle`): Hai phát mỗi giây, tầm 52 m; trúng được cả xe nhẹ.
- **Cao xạ 40 mm** (`aa_gun_vehicle`): Cách đánh: bốn phát ngòi cận đích mỗi giây, vừa chạy vừa bắn, tầm 48 m. · Mạnh / yếu: thắng trực thăng, drone và xe nhẹ; xe tăng gần như miễn nhiễm. · Mẹo: đi cùng tuyến đầu để chống trực thăng.
- **Cao xạ** (`aa_vehicle`): Cách đánh: pháo đôi 35 mm cao xạ (36 m) bắn khi đang chạy, kèm tên lửa tầm ngắn (44 m) chỉ nhắm máy bay. · Mạnh / yếu: xé nát trực thăng, drone và máy bay phản lực; đạn cao xạ gần như vô hại với giáp nên thua xe tăng và xe bọc thép. · Mẹo: kèm một chiếc với mỗi cụm xe tăng: rẻ mà chặn được trực thăng địch.
- **Tiếp dầu** (`aerial_tanker`): Phần cộng thời gian bay cho máy bay phe ta chưa được làm.
- **Tăng thả dù** (`airborne_light_tank`): Pháo 105 mm, giáp mỏng, thả dù ở nơi phe ta nhìn thấy.
- **Xe đổ bộ** (`airborne_vehicle`): Cách đánh: chạm thẻ rồi chạm vùng phe ta nhìn thấy: nó nhảy dù xuống trong 6 giây; phòng không bắn được khi còn dưới dù. · Mạnh / yếu: chiếm cứ điểm trống, đánh pháo binh từ phía sau; thua xe tăng. · Mẹo: chạm thẻ hai lần để đưa nó về bãi thả.
- **Tiếp đạn** (`ammo_carrier`): Cách đánh: chỉ có súng máy nóc; bệ phóng và xe tên lửa hết đạn trong vòng 14 m nạp nhanh gấp ba, trực thăng trong vòng 12 m hồi tên lửa và rốc-két nhanh gấp đôi. · Mạnh / yếu: giữ pháo phản lực và trực thăng bắn liên tục; giáp mỏng và nổ rất mạnh, nên giữ xa chỗ giao tranh. · Mẹo: đỗ sau các bệ phóng; chỉ huy tự đưa bệ phóng hết đạn tới nó khi đi tới đó nhanh hơn nạp tại chỗ.
- **Xe lội nước** (`amphib_light_vehicle`): Pháo tự động trị xe nhẹ, dùng ở map ven biển.
- **Xe ủi** (`armored_bulldozer`): Cách đánh: chỉ có súng máy trên nóc; lưỡi ủi húc tháp, lô cốt và nhà cửa với sát thương gấp ba (4 m), ủi phẳng răng rồng khi lao qua, và chỉ nhận một nửa sức nổ của mìn. · Mạnh / yếu: phá công sự ở cự ly gần tốt nhất; gần như không làm gì được xe tăng, và xe diệt tăng, tên lửa chống tăng cùng mọi thứ bắn xa hơn diệt nó trên đường lao vào. · Mẹo: cho đi trước xe tăng khi tấn công vào căn cứ; nó không gỡ mìn (việc của công binh) và không thay được tăng rùa để che chắn cho đội hình.
- **Bánh lốp** (`armored_car`): Cách đánh: pháo 25 mm vừa chạy vừa bắn cả đất lẫn trời, mạnh nhất với xe nhẹ và trực thăng; chiếm cứ điểm nhanh gấp đôi. · Mạnh / yếu: thắng trinh sát, pháo binh, xe phòng không và xe hỗ trợ; đạn nảy khỏi xe tăng và tháp canh nên thua chúng. · Mẹo: vòng qua sườn tuyến địch để săn pháo binh và xe hỗ trợ phía sau.
- **Lựu pháo** (`artillery`): Cách đánh: dừng lại, nã ba quả đạn 155 mm nổ mạnh cầu vồng qua vật cản rồi dời 15–20 m mới bắn tiếp, nên đạn phản pháo rơi vào chỗ trống; không bắn được gần hơn 25 m. · Mạnh / yếu: phá công sự, tăng hạng nặng và xe diệt tăng từ xa, bắn mục tiêu bị đánh dấu (chỉ thị la-de, radar phản pháo, UAV quét) gần như không tản mát; trinh sát, xe bọc thép và máy bay áp sát là nó thua. · Mẹo: đi cùng UAV trinh sát hoặc chỉ thị la-de: mục tiêu bị đánh dấu trúng gần như tuyệt đối.
- **TT tấn công** (`attack_helicopter`): Cách đánh: tên lửa chống tăng Hellfire Longbow bắn cặp từ 55 m; nó treo ở rìa tầm đó, vòng sang phía tránh phòng không tầm ngắn; pháo 30 mm và rốc-két khi gần, 2 Stinger bắn máy bay; có mồi nhiệt. · Mạnh / yếu: hạ xe tăng, tăng nặng và pháo binh từ ngoài tầm pháo cao xạ và tên lửa tầm ngắn; xe tên lửa phòng không tầm xa, trạm PK tầm xa và tiêm kích bắn xa hơn nó. · Mẹo: nó tự giữ khoảng cách: đi kèm thứ xử lý được tên lửa tầm xa (đòn SEAD, pháo binh).
- **Cường kích** (`attack_jet`): Cách đánh: bổ nhào càn quét bằng pháo 30 mm, giàn rốc-két 80 mm và bom 250 kg, kèm hai tên lửa chống tăng Kh-29 từ 40 m; hai R-60 chỉ để tự vệ trước máy bay; có mồi nhiệt. · Mạnh / yếu: đập nát xe nhẹ, xe tăng, tăng nặng, pháo binh và công sự, chịu đòn tốt hơn máy bay khác; xe phòng không, tên lửa phòng không và tiêm kích địch vẫn hạ được. · Mẹo: tung vào mũi thiết giáp địch khi phòng không của chúng đã thưa; muốn giành bầu trời hãy mua tiêm kích.
- **Pháo tự nạp** (`auto_loader_howitzer`): Loạt đạn rơi cùng lúc, rồi nạp lâu.
- **TL chiến thuật** (`ballistic_launcher`): Cách đánh: dừng lại rồi phóng một cặp tên lửa đạn đạo vào mục tiêu cách 40–180 m, mỗi quả nổ cực lớn; hai cặp rồi nạp lại lâu. · Mạnh / yếu: xóa sổ công sự, trận địa pháo và cụm quân đông; bắn chậm và bó tay khi bị áp sát. · Mẹo: để dành cho cụm địch đông nhất hoặc tháp quan trọng; đồng đội phải thấy mục tiêu trước.
- **Hỗ trợ tăng** (`bmpt`): Cách đánh: pháo đôi 30 mm (bắn cả đất lẫn trời), tên lửa chống tăng Ataka bắn cặp từ 40 m, và súng phóng lựu bắn sang hai bên. · Mạnh / yếu: dọn xe nhẹ, trinh sát, trực thăng và phòng không quanh xe tăng ta, hại được cả xe tăng; thua tăng nặng và xe diệt tăng. · Mẹo: cho chạy cạnh tăng chủ lực: nó hạ những gì xe tăng khó bắn trúng.
- **Xe bắc cầu** (`bridging_vehicle`): Việc bắc cầu qua sông chưa được làm.
- **Công sự** (`bunker_vehicle`): Cách đánh: khi di chuyển có pháo 105 mm và súng máy đồng trục trong cung phía trước; dừng lại khi có địch trong tầm, hoặc canh giữ cứ điểm hay điểm nghẽn, thì triển khai (3 giây, không bắn): giáp trước cấp 4, tầm 44 m, tháp xoay 360°. Khi được lệnh đi, nó thu lại trước (3 giây). · Mạnh / yếu: làm chốt cho cứ điểm hoặc tuyến công thành; phản ứng chậm, pháo binh và máy bay đánh vào nóc mỏng. · Mẹo: đưa tới nơi tuyến cần trụ lại; biểu tượng trên xe cho biết đang triển khai hay đã triển khai.
- **TL chống hạm** (`coastal_ashm_vehicle`): Tên lửa nặng nạp chậm, mạnh nhất ở mục tiêu xa.
- **Xe hóa ụ súng** (`combat_wreck_car`): Đợt này nổ mạnh hơn khi bị hạ.
- **Chỉ huy** (`command_vehicle`): Cách đánh: chỉ có súng máy trên nóc; quân ta trong 25 m bắn nhanh hơn 10%; đứng yên 5 giây là thành bãi thả dù tiền tuyến, quân mới đáp xuống cạnh nó. · Mạnh / yếu: làm mọi cụm quân quanh nó mạnh hơn và đưa quân tiếp viện ra tận tiền tuyến; thứ gì với tới cũng hạ nó nhanh. · Mẹo: đỗ ngay sau đội xe tăng ở cứ điểm, ngoài tầm bắn thẳng của địch.
- **Radar phản pháo** (`counter_battery_radar`): Cách đánh: chỉ có súng máy trên nóc; pháo địch nào khai hỏa trong vòng 120 m quanh nó bị lộ vị trí với phe ta trong 8 giây, và pháo binh ta gây +15% sát thương lên nó. · Mạnh / yếu: biến pháo địch thành mục tiêu cho pháo, Lancet và máy bay của ta; vô dụng khi địch không có pháo binh. · Mẹo: mang theo cùng pháo binh hoặc Lancet khi địch dựa vào pháo và rốc-két.
- **Xe chói lóa** (`dazzler_vehicle`): Làm nhiễu loạn hỏa lực địch gần đó, tạm thời.
- **Phá mìn** (`demolition_line_vehicle`): Mìn phía trước nổ vô hại; mở đường tấn công.
- **Chiếm drone** (`drone_hijack_vehicle`): Hạ drone địch trong hình nón; chưa lật được phe.
- **Phòng không TN** (`elite_aa`): Cách đánh: pháo đôi 35 mm nổ trên không lan rộng, tầm 46 m, kèm tên lửa; tăng tốc bắn dồn khi có mục tiêu trong tầm. · Mạnh / yếu: xé nát trực thăng, máy bay phản lực và drone; đạn cao xạ gần như vô hại với giáp nên thua xe tăng, xe bọc thép. · Mẹo: giữ máy bay ta tránh xa cho tới khi xe tăng hoặc pháo binh hạ được nó.
- **Bọc thép TN** (`elite_apc`): Cách đánh: pháo tự động và tên lửa chống tăng của xe chiến đấu bộ binh, đánh đau hơn một phần tư; địch vào trong 14 m là dính EMP, bị choáng 3,5 giây. · Mạnh / yếu: thắng xe nhẹ, trinh sát và phòng không, tên lửa còn hại được xe tăng; thua cụm xe tăng đông và xe diệt tăng. · Mẹo: đánh từ ngoài 14 m (xe diệt tăng, pháo binh, máy bay) để EMP không chạm tới quân ta.
- **Lựu pháo TN** (`elite_artillery`): Cách đánh: đạn 155 mm như lựu pháo tự hành, tầm 25–90 m, đánh đau hơn 15%, máu nhiều hơn 60%; có mục tiêu là bắn dồn dập, cứ ba phát lại chạy 15–20 m. · Mạnh / yếu: phá cụm xe nhẹ và tháp canh; phản pháo trượt khi nó đã đổi chỗ, thứ gì áp sát được là thắng. · Mẹo: đừng đứng yên trong tầm của nó; tung xe nhanh hoặc máy bay tới chỗ nó vừa chạy tới, không phải chỗ nó vừa bắn.
- **Trực thăng TN** (`elite_attack_helicopter`): Cách đánh: phóng tên lửa Hellfire từng cặp vào thiết giáp, kèm pháo, rốc-két và Stinger; mồi nhiệt lâu hơn, bắn dồn dập khi có mục tiêu. · Mạnh / yếu: săn xe tăng, tăng nặng và pháo binh; thua xe phòng không, tên lửa phòng không và tiêm kích. · Mẹo: mồi nhiệt chỉ lừa được tên lửa: pháo cao xạ (xe phòng không, Tunguska) chắc ăn hơn cả.
- **Cường kích TN** (`elite_attack_jet`): Cách đánh: pháo, rốc-két và bom như máy bay cường kích, máu nhiều hơn 60%; mồi nhiệt 14 giây lại có và kéo dài gấp đôi. · Mạnh / yếu: xé nát đoàn xe mặt đất và tháp canh; pháo cao xạ không bị mồi nhiệt lừa, tiêm kích đuổi kịp nó. · Mẹo: tên lửa khó hạ nó: đáp trả bằng cao xạ (xe phòng không, Tunguska) hoặc tiêm kích.
- **Drone FPV TN** (`elite_fpv_carrier`): Cách đánh: drone cảm tử như xe phóng FPV, tầm 12–75 m, đánh đau hơn một phần mười, máu nhiều hơn 60%; có thiết giáp trong tầm là phóng dồn dập (nhanh gấp 2,2 lần trong 6 giây). · Mạnh / yếu: phá nát xe tăng và tăng nặng từ xa; tăng APS, xe la-de phòng không và xe gây nhiễu chặn drone, xe nhanh áp sát là hạ được. · Mẹo: thấy vòng vàng thì dàn xe tăng ra, tung xe bọc thép hoặc trực thăng lao thẳng vào nó.
- **Grad TN** (`elite_grad`): Cách đánh: dừng lại rồi phóng dồn 16 rốc-két chùm cách 18–78 m, mỗi quả tung bốn bom con; bắn dồn dập khi có mục tiêu. · Mạnh / yếu: phủ kín cụm xe nhẹ, tháp canh và pháo binh; yếu với xe tăng và bó tay khi bị áp sát. · Mẹo: đừng bao giờ đứng dồn cục trong tầm của nó; tung xe nhanh hoặc máy bay đánh thẳng vào.
- **Tăng nặng TN** (`elite_heavy_tank`): Cách đánh: pháo 152 mm sức nổ lớn, đánh đau hơn một phần tư, máu nhiều hơn 60%; có mục tiêu trong tầm là tăng tốc (chạy nhanh, bắn dồn trong 6 giây). · Mạnh / yếu: nghiền nát tăng chủ lực, xe nhẹ và tháp canh; muốn hạ phải dùng xe diệt tăng, pháo binh và máy bay. · Mẹo: đón đợt tăng tốc của nó từ ngoài tầm (xe diệt tăng bắn 40 m, pháo binh), rồi áp sát khi nó đã dùng xong.
- **SAM tầm xa TN** (`elite_long_sam`): Cách đánh: tên lửa lớn như bản thường, chỉ bắn máy bay, đánh đau hơn một phần năm, máu nhiều hơn 60%; có máy bay trong tầm là tăng tốc (nạp nhanh hơn trong 6 giây). · Mạnh / yếu: khóa kín bầu trời với trực thăng, máy bay và oanh tạc cơ; bất lực trước mặt đất và trong vòng 20 m. · Mẹo: giữ máy bay ta ở nhà, hạ nó bằng xe tăng, pháo binh hoặc một đòn đánh nhanh trên mặt đất.
- **Tăng tinh nhuệ** (`elite_mbt`): Cách đánh: pháo 125 mm đánh đau hơn tăng chủ lực một phần tư, máu nhiều hơn 60%; khi bị bắn thì bật khiên (giảm 30% sát thương trong 5 giây). · Mạnh / yếu: thắng tăng chủ lực và xe nhẹ khi đấu tay đôi; xe diệt tăng và trực thăng hạ được nó. · Mẹo: khiên chỉ kéo dài 5 giây và 20 giây mới có lại: chờ khiên tắt rồi dồn hỏa lực xe diệt tăng.
- **Phản lực TN** (`elite_mlrs`): Cách đánh: dừng lại rồi phóng 16 rốc-két chùm cách 20–75 m, mỗi quả tung năm bom con; bắn dồn dập khi có mục tiêu trong tầm. · Mạnh / yếu: rải thảm cụm xe nhẹ, tháp canh và pháo binh; không tự vệ được trước bất cứ thứ gì áp sát. · Mẹo: dàn quân ra, rồi tung trinh sát, xe bọc thép hoặc máy bay đánh thẳng vào nó.
- **Chống tăng TN** (`elite_tank_destroyer`): Cách đánh: pháo 125 mm bắn từ 46 m; có mục tiêu trong tầm là bắn dồn dập (nhanh gấp 2,2 lần), bị thương thì thả khói. · Mạnh / yếu: cực nguy hiểm với xe tăng và tăng nặng; thua pháo binh, máy bay và xe nhẹ nhanh áp sát. · Mẹo: đừng cho xe tăng lao thẳng vào nó; dùng pháo binh, trực thăng hoặc xe bọc thép đánh áp sát.
- **Công binh** (`engineer_vehicle`): Cách đánh: chỉ có súng máy nóc; sửa chữa xe ta trong vòng 14 m (2,5% máu mỗi giây) và tháp ta chậm bằng nửa, gỡ mìn nó thấy, phá vật cản nhưng chậm (xe ủi phá nhanh hơn). · Mạnh / yếu: giúp tuyến xe tăng và căn cứ đang giữ trụ lâu hơn hẳn; tự đánh thì yếu, trinh sát và xe bọc thép dễ bắt nạt nó. · Mẹo: đỗ ngay sau tuyến đầu hoặc giữa các tháp đang giữ; nạp đạn cho bệ phóng là việc của xe tiếp đạn.
- **Gây nhiễu** (`ew_jammer`): Cách đánh: chỉ có súng máy nóc; tên lửa, drone và hỏa lực yểm trợ của địch nhắm vào vùng gây nhiễu 32 m đều bị lệch. · Mạnh / yếu: khắc chế xe tên lửa chống tăng, xe drone, trực thăng và đòn yểm trợ địch; vô dụng trước súng và đạn pháo thường. · Mẹo: giữ ở giữa đội hình khi địch dùng nhiều tên lửa và drone.
- **FPV cáp quang** (`fibre_fpv_carrier`): Cách đánh: điều khiển từng chiếc drone cáp quang lao vào xe bọc thép, tầm 60 m, 6 giây một chiếc; gây nhiễu vô tác dụng. · Mạnh / yếu: thắng xe tăng núp sau xe gây nhiễu; hệ đánh chặn vẫn hạ được drone. · Mẹo: mang theo khi địch dùng nhiều gây nhiễu.
- **Tiêm kích** (`fighter_jet`): Cách đánh: tên lửa không đối không từ 60 m, tên lửa cận chiến và pháo; đánh chặn máy bay địch ở xa vị trí gác, có thể lơ lửng để bắn. · Mạnh / yếu: khắc tinh của trực thăng, oanh tạc cơ và mọi máy bay; gần như vô hại với mặt đất, vẫn sợ tên lửa phòng không. · Mẹo: mua ngay khi địch đưa bất cứ thứ gì lên trời; nó dọn sạch bầu trời cho máy bay của ta.
- **Phun lửa** (`flame_tank`): Cách đánh: súng phun lửa phải áp sát mới bắn; luồng lửa lan ra cả nhóm, cực mạnh với xe nhẹ và lô cốt. · Mạnh / yếu: thiêu rụi xe nhẹ, trinh sát và tháp canh khi áp sát; xe tăng và mọi thứ bắn xa hơn hạ nó trước khi tới nơi. · Mẹo: cho đi qua phố xá hoặc màn khói để áp sát địch trước khi bị bắn nát.
- **Drone FPV** (`fpv_carrier`): Cách đánh: dừng lại rồi phóng lần lượt từng chiếc drone cảm tử, vài giây một chiếc, lao xuống xe bọc thép cách 12–75 m; hết mười sáu chiếc thì nạp lại một lúc. · Mạnh / yếu: phá nát xe tăng và tăng nặng từ xa; tăng APS, xe la-de phòng không và xe gây nhiễu chặn drone, tăng mái che gần như miễn nhiễm. · Mẹo: bắn từ sau tuyến ta vào xe tăng nặng nhất của địch, giữ ngoài tầm pháo của chúng.
- **Ném bom lượn** (`glide_bomber`): Cách đánh: thả bom lượn từ cách 90 m rồi quay đi; bom lượn 20 m/s xuống mục tiêu. · Mạnh / yếu: đánh tháp và cụm quân ngoài tầm phòng không gần; hệ đánh chặn bắn hạ được bom. · Mẹo: tung vào công sự cố định, có tiêm kích che.
- **Nhiễu định vị** (`gps_jammer_vehicle`): Làm nhiễu loạn hỏa lực địch gần đó, tạm thời.
- **Tên lửa HT** (`ground_cruise_missile_vehicle`): Hai tên lửa chậm; địch có thời gian bắn hạ.
- **Xe robot** (`ground_drone_carrier`): Ba robot con chưa được làm.
- **TT vũ trang** (`gunship_heli`): Cách đánh: mở màn bằng loạt rốc-két lớn, rồi pháo 30 mm cố định và tên lửa chống tăng; xạ thủ bắn từ hai cửa hông. Có mồi nhiệt. · Mạnh / yếu: phá nát xe nhẹ, trinh sát và tháp canh; sợ xe phòng không và tiêm kích, nhưng rất lì đòn. · Mẹo: trực thăng duy nhất chiếm được cứ điểm: đưa nó đi chiếm điểm trống ở xa bên kia bản đồ.
- **PK hỗn hợp** (`heavy_aa`): Cách đánh: bốn nòng 30 mm cao xạ (42 m) và tên lửa phòng không (44 m), bắn cả khi đang chạy; tầm nhìn 60 m thấy máy bay từ sớm. · Mạnh / yếu: lá chắn di động tốt nhất trước trực thăng và máy bay; trên mặt đất thua xe tăng và xe bọc thép. · Mẹo: cho đi cùng đội hình chính để trực thăng và cường kích địch không được tự do tấn công.
- **Oanh tạc cơ** (`heavy_bomber`): Cách đánh: bay qua và thả một hàng 12 quả bom nặng; phóng tên lửa hành trình từ 110 m; súng đuôi bắn máy bay. · Mạnh / yếu: san phẳng công sự, pháo binh và cụm xe nhẹ; sợ tên lửa phòng không và tiêm kích. · Mẹo: tung vào công sự và trận địa pháo địch sau khi tiêm kích hoặc phòng không ta đã dọn sạch bầu trời.
- **TT cẩu tháp** (`heavy_lift_helicopter`): Việc cẩu tháp đặt tùy nơi chưa được làm.
- **Phản lực nặng** (`heavy_rocket_artillery`): Cách đánh: dừng lại rồi phóng 12 rốc-két 300 mm vào vùng cách 30–140 m, sức nổ lớn; ba loạt rồi nạp lại lâu tại chỗ. · Mạnh / yếu: đánh công sự, pháo binh và cụm thiết giáp từ bên kia bản đồ; không có khả năng tự vệ khi bị áp sát. · Mẹo: bắn xa hơn gần như mọi thứ: giữ ở góc căn cứ và cho trinh sát soi mục tiêu.
- **Tăng nặng** (`heavy_tank`): Cách đánh: pháo 152 mm tự đổi đạn xuyên khi bắn xe có giáp và đạn nổ mạnh khi bắn công trình hoặc cụm xe nhẹ; pháo 30 mm bên cạnh đáp trả trực thăng. Giáp trước cấp 4, hông cấp 3. · Mạnh / yếu: trụ lâu nhất khi đối đầu và phá công sự mạnh nhất; chậm, nên sợ xe diệt tăng, pháo binh và máy bay. · Mẹo: làm mũi nhọn đánh công sự và giữ tuyến; cho phòng không đi kèm và đừng để đi một mình.
- **Xuồng hộ tống** (`hover_gunboat`): Cách đánh: pháo 30 mm sáu nòng trên thân đệm khí nhỏ; nó chạy cạnh tàu đệm khí đổ bộ trên cả đất liền lẫn mặt nước. · Mạnh / yếu: nhanh, khó bắt, nhưng giáp mỏng: xe tăng hay pháo tự động nào cũng hạ được. · Mẹo: hạ chiếc đang đánh dấu mục tiêu trước (dấu hộ tống trên nó): khi nó còn, pháo của tàu đệm khí bắn chụm hơn.
- **Xe bộ binh** (`ifv`): Cách đánh: pháo tự động vừa chạy vừa bắn xe nhẹ và máy bay, kèm tên lửa chống tăng TOW (34 m) cho xe tăng; chiếm cứ điểm nhanh gấp 3, bị bắn thì tự thả khói. · Mạnh / yếu: thắng trinh sát, xe nhẹ, pháo binh và phòng không, gây sát thương cả xe tăng; đấu tay đôi với tăng vẫn thua. · Mẹo: tuyến hai lý tưởng sau xe tăng: lấp chỗ hở và chiếm điểm trong lúc xe tăng giao chiến.
- **Drone chặn** (`interceptor_drone_vehicle`): Cách đánh: 4 giây một drone đánh chặn, tầm 60 m, vào drone và trực thăng, cả drone địch đang bay tới. · Mạnh / yếu: làm mỏng bầy FPV và trực thăng; máy bay phản lực bay qua vô sự. · Mẹo: giữ cạnh xe tăng và pháo binh ta.
- **TK đánh chặn** (`interceptor_jet`): Cách đánh: lao vào, bắn hai tên lửa tầm siêu xa từ 90 m, ưu tiên máy bay lớn; không bắn trong 15 m. · Mạnh / yếu: diệt oanh tạc cơ và pháo hạm bay từ sớm; thua khi quần thảo gần. · Mẹo: giữ lại chờ oanh tạc cơ của địch.
- **La-de PK** (`iron_beam`): Cách đánh: tia la-de đốt hạ một drone, tên lửa hoặc rốc-két (cả rốc-két pháo binh) nhắm vào trong vòng 30 m quanh nó, cứ 1,2 giây một quả; giữa các lần đó nó bắn máy bay (45 m). · Mạnh / yếu: che cả cụm quân khỏi tên lửa chống tăng, Lancet, pháo phản lực và tên lửa trực thăng; đạn pháo và đạn súng bay qua được, và nó không có gì đánh mặt đất. · Mẹo: đỗ giữa đội xe tăng khi địch dựa vào tên lửa, drone hoặc rốc-két.
- **Đạn lảng vảng** (`lancet_truck`): Cách đánh: dừng lại rồi phóng từng chiếc drone Lancet bay tới 85 m rồi lao xuống mục tiêu: gấp đôi sát thương lên pháo binh và mọi xe đứng yên quá 3 giây; sáu chiếc rồi nạp lại. · Mạnh / yếu: chuyên diệt pháo binh, giàn phóng và tên lửa phòng không phía sau tuyến, cả xe tăng đứng yên; tăng APS, xe la-de phòng không và xe gây nhiễu chặn được drone. · Mẹo: cho trinh sát, UAV quét hoặc radar phản pháo tìm pháo địch trước, rồi thả Lancet săn chúng.
- **Tàu đổ bộ** (`landing_craft`): Cách đánh: từ khoang đổ bộ của Leviathan tới bãi cát, thả hai xe tăng rồi quay về lấy thêm; tối đa ba chuyến. · Mạnh / yếu: chậm và ít vũ khí; đánh chìm nó trên đường vào thì xe tăng chìm theo.
- **La-de diệt tăng** (`laser_tank`): Cách đánh: tia năng lượng (40 m) tăng từ ×0,3 lên ×2 trong 6 giây trên cùng một mục tiêu, đổi mục tiêu thì về lại mức thấp; xuyên cả giáp dày nhất. · Mạnh / yếu: nung chảy xe tăng nặng và boss; APS, giáp phản ứng nổ và lồng chắn không cản được, nhưng màn khói cắt 80% tia và bầy xe nhỏ giữ nó ở mức yếu nhất. · Mẹo: giữ nó trên một mục tiêu lớn, và che nó khỏi xe hạng nhẹ.
- **TT nhẹ** (`light_attack_heli`): Vài tên lửa chống tăng và súng máy; đánh sườn rồi rút.
- **Tăng nhẹ** (`light_tank`): Cách đánh: pháo 57 mm xuyên giáp vừa chạy vừa bắn, tầm ngắn nhất trong các xe tăng; súng đồng trục bắn máy bay khi mặt đất đã sạch. · Mạnh / yếu: thắng xe nhẹ, trinh sát và xe phòng không; thua tăng nặng hơn, xe diệt tăng và trực thăng tấn công. · Mẹo: lựa chọn rẻ để chặn xe bọc thép địch đầu trận; có CP thì thay bằng tăng chủ lực.
- **PK tầm xa** (`long_sam`): Cách đánh: dừng lại rồi phóng một tên lửa lớn mỗi 8 giây, chỉ bắn máy bay, xa tới 95 m (600 sát thương, không bắn gần hơn 20 m). · Mạnh / yếu: bắn xa hơn vũ khí của mọi máy bay, cả oanh tạc cơ và pháo hạm bay; bất lực trước mặt đất và trong vòng 20 m nên cần được che chắn. · Mẹo: để xa sau tuyến quân, có phòng không tầm ngắn ở gần cho thứ gì lọt xuống thấp.
- **Tăng chủ lực** (`main_battle_tank`): Cách đánh: pháo 120 mm xuyên giáp vừa chạy vừa bắn ở tầm trung, súng máy trên nóc, súng đồng trục bắn máy bay khi mặt đất đã sạch. · Mạnh / yếu: thắng xe nhẹ, trinh sát và phòng không; thua tăng hạng nặng, xe diệt tăng và trực thăng. · Mẹo: dẫn đầu mỗi đợt tiến công bằng 2–3 chiếc, xe diệt tăng theo sau và phòng không ở gần.
- **Vi sóng** (`microwave_vehicle`): Cách đánh: mỗi 8 giây một xung vi sóng làm rơi mọi drone địch trong hình nón 60°, tầm 30 m; xe không hề hấn. · Mạnh / yếu: quét sạch bầy FPV và máy bay drone; vô dụng với mọi thứ khác. · Mẹo: đỗ cạnh xe tăng ta, nơi drone lao xuống.
- **Rải mìn** (`mine_layer`): Cách đánh: có súng máy nóc; khi chạy, cứ 6 giây thả một quả mìn chống tăng (tối đa 8), xe địch cán phải là nổ tung. · Mạnh / yếu: trừng phạt xe tăng và đoàn xe đi theo một lối; tăng mái che có trục lăn phá mìn, máy bay thì không sợ. · Mẹo: chạy qua lại trên con đường địch hay đi, hoặc quanh cứ điểm của ta.
- **PL rải mìn** (`mine_rocket_truck`): Rải mìn phía trước; không gây sát thương trực tiếp.
- **Xuồng tên lửa** (`missile_boat`): Cách đánh: chờ ngoài khơi, lao vào sát đầu cầu tàu, bắn một loạt rốc-két 80 mm rồi quay ra. · Mạnh / yếu: nhanh nhưng giáp mỏng (cấp 1): mọi xe đứng ở đầu cầu tàu đều bắn trúng nó khi nó áp sát.
- **Phản lực** (`mlrs`): Cách đánh: dừng lại rồi phóng một loạt sáu rốc-két chính xác từ tới 110 m; sau bốn loạt phải đứng yên nạp đạn. · Mạnh / yếu: phá công sự, tăng hạng nặng và trận địa pháo từ ngoài tầm với; bất kỳ xe nhanh nào áp sát cũng hạ được nó. · Mẹo: nhắm vào chỗ địch tụ đông hoặc công trình; để xe công binh gần đó giúp nạp đạn nhanh hơn.
- **Xe sửa chữa** (`mobile_repair_vehicle`): Vùng sửa rộng hơn công binh, tốc độ chậm hơn.
- **Xe cối** (`mortar_carrier`): Cách đánh: dừng lại rồi bắn đạn cối 120 mm nổ mạnh qua tường và nhà; tầm nhìn ngắn nên bắn vào mục tiêu đồng đội phát hiện. · Mạnh / yếu: tốt với tháp canh, xe diệt tăng và thiết giáp đứng yên; bó tay khi bị áp sát. · Mẹo: tầm tối thiểu chỉ 10 m, gần hơn các pháo lớn; hãy nấp sau nhà cửa.
- **Tăng thế hệ mới** (`next_gen_tank`): Chặn được hai phát tên lửa hoặc đạn pháo đầu tiên.
- **TL ngoài tầm** (`nlos_atgm_vehicle`): Cách đánh: 10 giây một tên lửa lớn, tầm 90 m, bay vòng qua vật cản đánh nóc, vào mục tiêu phe ta nhìn thấy. · Mạnh / yếu: diệt xe tăng từ sau đồi; tự đi thì mù, bắn chậm. · Mẹo: đi cặp với trinh sát hoặc UAV quét.
- **Cường kích CQ** (`prop_attack_plane`): Súng và rốc-két trị xe nhẹ; mua theo tốp.
- **TL dẫn radar** (`radar_atgm_vehicle`): Cách đánh: hai tên lửa lớn cách nhau 0,6 giây, tầm 50 m, rồi nạp 9 giây; radar nhìn xuyên khói. · Mạnh / yếu: thắng xe tăng nấp trong khói; APS chặn được vài quả. · Mẹo: đem ra đối đầu xe tạo khói.
- **TS radar** (`radar_scout`): Cách đánh: khi chạy nhìn 50 m; đứng yên 2 giây thì dựng cột radar: nhìn 80 m và gần như ẩn. · Mạnh / yếu: chỉ điểm cho pháo binh từ xa, lật tẩy mồi nhử; di chuyển thì yếu. · Mẹo: đỗ ở cánh và để yên đó.
- **Radar PK** (`radar_support_vehicle`): Phần cộng tầm bắn cho PK chưa được làm.
- **Pháo điện từ** (`railgun_truck`): Cách đánh: đứng yên nạp năng lượng 0,9 giây (cuộn dây phát sáng), rồi bắn viên đạn xuyên thủng mọi xe trên đường bay, xa tới 90 m. · Mạnh / yếu: xuyên thủng cả hàng xe tăng và tăng nặng từ rất xa; bắn chậm, bị áp sát là thua. · Mẹo: ngắm dọc con đường hoặc cửa ải nơi địch đi thành hàng; cần đồng đội soi mục tiêu.
- **Súng không giật** (`recoilless_jeep`): Cách đánh: 6,7 giây một phát nổ lõm nặng, tầm 32 m; đỗ yên thì khó thấy cho tới khi bắn. · Mạnh / yếu: phục kích xe tăng từ sườn chỉ với 3 CP; thứ gì bắn trả cũng hạ được nó. · Mẹo: bắn vào sườn một chiếc tăng rồi chạy.
- **UAV trinh sát** (`recon_drone`): Cách đánh: bay cao với tầm nhìn 90 m, soi mục tiêu cho cả đội quân, kèm một tên lửa dẫn đường nhẹ (50 m) đánh mặt đất. · Mạnh / yếu: bắn tỉa trinh sát và pháo binh, giúp pháo ta bắn hết tầm; mong manh, gặp phòng không hay tiêm kích là rơi. · Mẹo: kết hợp với lựu pháo, pháo phản lực hoặc tên lửa đạn đạo để chúng bắn trúng thứ chúng không tự thấy.
- **Trinh sát nhanh** (`recon_jet`): Cách đánh: không vũ khí; bay thẳng một lượt ngang map, làm lộ dải rộng 60 m trong 20 giây, cả tàng hình, rồi rời trận. · Mạnh / yếu: tìm pháo binh, ụ súng ẩn và mồi nhử; bay cao, chỉ tên lửa tầm xa và tiêm kích với tới. · Mẹo: gọi ngay trước một trận pháo kích.
- **Pháo hạm sông** (`river_gunboat`): Chậm; pháo 100 mm bắn phá bờ.
- **Tàu tuần tra** (`river_patrol_boat`): Kiểm soát mặt sông; súng máy và súng phóng lựu.
- **Bán tải rốc-két** (`rocket_technical`): Cách đánh: dừng lại rồi phóng một loạt tám rốc-két khá tản mát tới 48 m; hết sáu loạt phải đứng yên nạp lại. Có thêm súng máy. · Mạnh / yếu: phá tháp canh và cụm địch với giá rẻ; chết trước gần như mọi khẩu súng với tới nó. · Mẹo: xe nhanh, chiếm cứ điểm nhanh gấp đôi: dùng sớm, sau đó giữ thật xa phía sau.
- **PK tầm trung** (`sam_launcher`): Cách đánh: dừng lại rồi phóng tên lửa từng cặp vào máy bay cách tới 55 m; chỉ có súng máy nóc để đánh mặt đất. · Mạnh / yếu: bắn rụng trực thăng, máy bay phản lực và oanh tạc cơ từ xa, kể cả trực thăng tấn công bắn từ xa; xe tăng, xe bọc thép áp sát là nó thua. · Mẹo: đặt sau tuyến đầu: một bệ phóng che được cả một vùng trời rộng.
- **TT trinh sát** (`scout_heli`): Cách đánh: lao vào với súng máy nhiều nòng (tầm gần, bắn được cả máy bay) và giàn 7 rốc-két; mắt tinh giúp soi mục tiêu cho cả quân. · Mạnh / yếu: xé nát trinh sát, xe nhẹ và xe hỗ trợ; xe tăng gần như miễn nhiễm, gặp phòng không là rụng nhanh. · Mẹo: dùng để săn xe hỗ trợ và pháo binh sau lưng địch, tránh xa phòng không.
- **Trinh sát** (`scout_jeep`): Cách đánh: súng máy tầm gần, vừa chạy vừa bắn. Nhìn xa để phát hiện địch cho cả quân, chiếm cứ điểm nhanh gấp đôi. · Mạnh / yếu: diệt được pháo binh và xe hỗ trợ đi lẻ; thua mọi xe bọc thép, xe tăng và tháp canh. · Mẹo: tung hai chiếc đầu trận để chiếm cứ điểm trống, sau đó cho đi trước làm mắt cho pháo binh.
- **Tàu hộ vệ** (`sea_corvette`): Cách đánh: pháo 76 mm bắn vào bờ; CIWS bắn hạ tên lửa và drone nhắm vào nó hoặc vào Leviathan trong vòng 32 m. Nó giữ vị trí chắn giữa Leviathan và bờ. · Mạnh / yếu: hông giáp cấp 3, boong cấp 1; đánh chìm nó trước thì máy bay và tên lửa của bạn đánh được tàu chính.
- **Tuần dương hạm** (`sea_cruiser`): Cách đánh: hai tháp pháo nòng đôi 203 mm bắn vào bờ; hai CIWS bắn hạ tên lửa và drone nhắm vào nó hoặc vào Leviathan trong vòng 30 m. Nó giữ vị trí giữa Leviathan và bờ, áp sát hơn khi tàu chính bỏ chạy. · Mạnh / yếu: hông giáp cấp 3, boong cấp 2; nó là tàu đầu tiên trong tầm bắn, đánh chìm nó thì tên lửa của bạn đánh được tàu chính.
- **Drone cảm tử** (`shahed_truck`): Cách đánh: dừng lại rồi phóng lần lượt từng chiếc drone cảm tử bay chậm xa tới 150 m, vài giây một chiếc, chuyên đánh công trình. · Mạnh / yếu: phá tháp canh, ụ pháo và pháo binh đứng yên ở xa; APS và xe la-de phòng không bắn hạ drone chậm, xe gây nhiễu làm chúng lạc. · Mẹo: ở chế độ Công thành, nhắm vào những tháp mà xe tăng ta chưa với tới.
- **Phát khiên** (`shield_carrier`): Cách đánh: vòm khiên 12 m quanh xe hấp thụ 1.000 sát thương từ đạn pháo, đạn súng, bom và tên lửa cho mọi đơn vị phe ta bên trong, rồi vỡ; hồi lại 20 giây sau đòn cuối. Có súng máy nóc. · Mạnh / yếu: giúp tuyến xe tăng áp sát dưới làn đạn; vũ khí năng lượng xuyên thẳng qua, nhiều vòm không cộng dồn, và bản thân xe giáp mỏng. · Mẹo: giữ ngay sau các xe tăng dẫn đầu; địch đã vào trong vòm thì vòm không chặn được.
- **TL PK nhẹ** (`shorad_vehicle`): Cách đánh: tám tên lửa tầm nhiệt một loạt, tầm 44 m, vừa chạy vừa bắn, rồi nạp 15 giây. · Mạnh / yếu: hạ trực thăng và drone trong một loạt; pháo sáng lừa được vài quả, dưới đất thứ gì cũng diệt được nó. · Mẹo: dành loạt tên lửa cho một cặp trực thăng.
- **Công thành** (`siege_tank`): Cách đánh: hai chế độ. Khi di chuyển là một xe tăng có pháo 105 mm bắn khi đang chạy. Dừng lại khi có địch trong tầm, hoặc khi canh giữ, nó vào thế công thành trong 2,5 giây: hạ chân chống, nâng tháp pháo, cối 240 mm ném đạn 450 sát thương xa từ 16 đến 70 m, nổ rộng 9 m, gấp đôi lên tháp và công trình; 10 quả rồi nạp lại. Thu lại mất 2,5 giây để đi tiếp, hoặc khi địch lọt vào trong 16 m. · Mạnh / yếu: nã công sự, tuyến xe tăng và đội hình dày từ ngoài tầm của chúng; sợ xe nhanh lọt vào trong tầm tối thiểu, máy bay và bị đánh vào sườn khi đang công thành. · Mẹo: cho nó vào thế ngay ngoài tầm địch, có quân chắn phía trước; khi đang hạ hay thu chân chống nó không bắn được.
- **Pháo hạm** (`sky_gunship`): Cách đánh: bay tới nơi bạn chỉ định và bay vòng ngược chiều kim đồng hồ quanh địch ở đó, cách chừng 22 m, pháo 105, 40 và 25 mm cùng bắn một lúc từ bên trái. · Mạnh / yếu: nghiền nát xe nhẹ, xe tăng, pháo binh và tháp; không bắn được máy bay nên sợ tên lửa phòng không và tiêm kích. · Mẹo: đưa vào trận đánh lớn trên mặt đất sau khi phòng không hoặc tiêm kích ta đã xử lý phòng không địch.
- **Xe khói** (`smoke_carrier`): Cách đánh: có súng máy nóc; mỗi khi địch trong tầm, nó phủ màn khói 11 m quanh mình, không ai nhìn xuyên qua được. · Mạnh / yếu: che chở xe tăng và xe chậm khi áp sát pháo tầm xa của địch; tự nó đánh rất yếu. · Mẹo: cho chạy đầu đội hình khi tiến vào xe diệt tăng hoặc xe tên lửa chống tăng để xe tăng ta áp sát được.
- **Cối tháp kín** (`sp_mortar`): Cách đánh: bốn quả cối 120 mm, tầm 60 m, rơi xuống cùng lúc, rồi nghỉ 10 giây. · Mạnh / yếu: nghiền một cụm quân trước khi kịp tản ra; áp sát thì thua xe tăng. · Mẹo: nhắm vào các cụm quân trinh sát tìm thấy.
- **OTC tàng hình** (`stealth_bomber`): Cách đánh: mỗi lượt thả ba quả bom cực lớn, phóng tên lửa JASSM từ 90 m; tàng hình: chỉ bị thấy ở gần hoặc ngay sau khi bắn. · Mạnh / yếu: phá hủy công sự, tăng hạng nặng và pháo binh; một khi lộ diện, tên lửa phòng không và tiêm kích vẫn hạ được. · Mẹo: dùng đánh vào cứ điểm phòng thủ mạnh nhất của địch, nơi máy bay khác sẽ bị bắn rơi.
- **TK tàng hình** (`stealth_fighter`): Cách đánh: tàng hình: địch chỉ thấy ở 40% tầm nhìn, và trong 2,5 giây sau mỗi lần khai hỏa; trạm radar, tháp canh và UAV quét làm lộ nó. Bốn tên lửa AIM-120 đánh máy bay, hai bom GBU-39 thả vào xe và tháp phòng không, pháo 25 mm. · Mạnh / yếu: dọn sạch bầu trời và SAM trước khi máy bay cường kích tới; mang ít đạn hơn tiêm kích thường nên về hồi đạn sớm hơn. · Mẹo: cho bay trước đoàn oanh tạc; radar, tháp canh và UAV quét là thứ tìm ra nó.
- **Tàng hình hạm** (`stealth_naval_strike`): Hai bom dẫn đường trị công trình và xe đứng yên; không pháo.
- **UAV tấn công** (`strike_drone`): Cách đánh: bay cao, phóng tên lửa Hellfire từ 48 m và bốn quả bom dẫn đường; không có vũ khí chống máy bay. · Mạnh / yếu: bắn tỉa xe tăng, tăng nặng và pháo binh; chậm và mỏng, gặp phòng không hay tiêm kích là rơi. · Mẹo: tầm nhìn 62 m biến nó thành trinh sát cho pháo binh; tránh xa tên lửa phòng không địch.
- **Tiếp tế** (`supply_truck`): Cách đánh: chỉ có súng máy nhẹ; nó chạy theo lộ trình tới kho và không chiếm được cứ điểm. · Mạnh / yếu: đủ giáp để chịu vài phát, nhưng không đánh lại được thứ gì đáng kể. · Mẹo: trong nhiệm vụ hộ tống, dùng xe tăng dọn đường phía trước và cho phòng không đi cùng xe tải.
- **Máy bay mẹ** (`swarm_carrier`): Cách đánh: bay qua mục tiêu, thả lần lượt tám drone FPV (nổ lõm, đánh nóc), mỗi chiếc một mục tiêu, và thả thêm hai bom dẫn đường từ cùng khoang khi bay qua; kho đạn hồi lại trong 16 giây. · Mạnh / yếu: đưa bầy drone tới nơi xe drone FPV hay nhà chứa drone không với tới; tiêm kích và SAM bắn hạ được nó, còn C-RAM, xe la-de phòng không, tháp EW và xe gây nhiễu chặn được drone. · Mẹo: tung ra khi phòng không địch đang bận; drone không chiếm chỗ máy bay của ta.
- **Chống tăng** (`tank_destroyer`): Cách đánh: pháo 125 mm xuyên giáp (như pháo tự hành 2S25), vừa chạy vừa bắn, xa hơn và nạp nhanh hơn pháo tăng chủ lực; súng máy nóc cho mục tiêu nhỏ. · Mạnh / yếu: hạ xe tăng, tăng hạng nặng và boss từ ngoài tầm với của chúng; sợ pháo binh và xe nhẹ áp sát. · Mẹo: để ngay sau hàng xe tăng để nó bắn trước; khắc tinh của thiết giáp nặng và boss.
- **Nhiệt áp** (`thermobaric_launcher`): Cách đánh: dừng lại rồi phóng 12 rốc-két nhiệt áp phủ kín một vùng cách 12–38 m; bốn loạt rồi phải đứng yên nạp lại. · Mạnh / yếu: quét sạch cụm địch, tháp canh và mọi thứ đứng dồn; phải tiến khá gần, dễ bị máy bay bắt. · Mẹo: giáp đủ dày để đi sau xe tăng: tiến sát sau lưng chúng rồi nã vào cứ điểm địch đang giữ.
- **Siêu tăng** (`titan_tank`): Cách đánh: pháo đôi 140 mm bắn loạt đôi tới 40 m, kèm tên lửa chống tăng và hai súng máy. · Mạnh / yếu: nghiền nát xe tăng, xe nhẹ và công sự; bị xe diệt tăng, pháo binh và máy bay bào dần. · Mẹo: làm trụ cho đợt tấn công lớn; phải có phòng không đi kèm để che trực thăng.
- **Pháo kéo CT** (`towed_at_gun`): Bắn xa, mạnh, không giáp.
- **Tăng rùa** (`turtle_tank`): Cách đánh: pháo 120 mm không xoay được, phải quay cả thân để ngắm. Mái thép chặn 80% sát thương drone, trục lăn kích nổ mìn vô hại. · Mạnh / yếu: đi xuyên bầy FPV, Lancet và bãi mìn, thắng xe nhẹ; thua tăng hạng nặng và xe diệt tăng. · Mẹo: cho đi đầu khi địch có xe drone và xe rải mìn; nó chậm, để các xe khác theo sau.
- **TT hai rô-to** (`twin_rotor_gunship`): Giữa trực thăng vũ trang và Pháo hạm bay; dễ bị bắn trúng.
- **Hai nòng** (`twin_tank`): Cách đánh: hai pháo 120 mm bắn gần như cùng lúc, một phát đôi ở 34 m, rồi nạp lâu (7 giây); tháp xoay nhanh, chạy nhanh hơn tăng nặng; giáp trước cấp 3. · Mạnh / yếu: phát mở màn thắng tay đôi với tăng chủ lực và tăng nặng; bắn lại chậm, nên xe diệt tăng, trực thăng và bầy xe nhẹ bào mòn được nó. · Mẹo: cho nó mở màn vào chiếc tăng nặng nhất của địch, để các xe khác che lúc nó nạp đạn.
- **Xe bom** (`vbied`): Cách đánh: lao thẳng vào địch rồi tự nổ: 700 sát thương trong bán kính 7,5 m, một nửa lên tháp và công trình. Bị bắn hạ giữa đường thì nổ ngay tại chỗ. · Mạnh / yếu: phá nát pháo binh, xe hỗ trợ và cụm xe nhẹ; súng bắn nhanh và xe bọc thép chặn được nó, và căn cứ chịu được cả dòng xe bom. · Mẹo: cho chạy sau đợt xe tăng hoặc xuyên qua màn khói để tới mục tiêu nguyên vẹn.
- **Pháo xung kích** (`wheeled_gun`): Cách đánh: pháo 120 mm xuyên giáp (như Centauro II) vừa chạy vừa bắn tới 38 m, khoảng 70 sát thương mỗi giây lên giáp dày, +25% khi trúng hông hoặc đuôi. · Mạnh / yếu: chạy vòng tuyến xe tăng và trừng phạt hai bên sườn; giáp mỏng nên đấu thẳng với tăng là thua, pháo tự động xé nát nó. · Mẹo: vòng qua sườn trong lúc xe tăng giữ mặt trước: phát nào trúng hông cũng đáng giá.
- **Pháo bánh lốp** (`wheeled_howitzer`): Cách đánh: bốn phát 155 mm trong 6 giây, tầm 90 m, rồi chạy ngay và nạp lại 25 giây. · Mạnh / yếu: phản pháo rơi vào chỗ trống; thân mỏng, dễ chết. · Mẹo: giữ thật xa phía sau, có trinh sát đi trước.
- **Drone hộ vệ** (`wingman_drone`): Cách đánh: bay kèm cánh máy bay dẫn (máy bay có người lái gần nhất trong 120 m; không có thì tuần tra trên chiến tuyến) với hai tên lửa AIM-9; tên lửa phòng không địch nhắm vào máy bay dẫn có bốn phần mười cơ hội chuyển sang nó. · Mạnh / yếu: giúp tiêm kích và oanh tạc cơ sống thêm vài quả tên lửa; một mình thì yếu, tiêm kích địch bắn hạ dễ. · Mẹo: mua khi đã có máy bay có người lái; không tính vào trần sáu máy bay (tối đa bốn chiếc mỗi phe).
- **Cao xạ bán tải** (`zu23_technical`): Cách đánh: pháo đôi 23 mm cao xạ vừa chạy vừa bắn máy bay và xe nhẹ (32 m); chiếm cứ điểm nhanh gấp đôi. · Mạnh / yếu: xé nát trực thăng, drone và trinh sát; xe tăng và xe bọc thép hạ nó trong vài giây. · Mẹo: đối sách rẻ và sớm trước trực thăng địch; về sau hãy mua xe phòng không thật sự.

*115 / 120 đơn vị có lời hướng dẫn.*

## 9. Bảng DPS tổng hợp

Trạng thái: Đã áp

Nguồn dữ liệu: 02_phuong_tien/Xe_suy_ra; 02_phuong_tien/Hoi_quy; 02_phuong_tien/Hoi_quy_du_lieu. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §9. Bảng DPS, §9b.

#### 9. Bảng DPS tổng hợp

#### 9b. Giá trị thực chiến

DPS lý thuyết (phần 9) đã sửa để tính đủ loạt bắn, băng đạn, thời gian thay băng, nạp của bệ phóng và số bom/tên lửa mỗi lần đầy đạn. Giá trị thực chiến đo trong mô phỏng: mỗi xe hạng 1, không trang bị, đánh các nhóm mục tiêu chuẩn (cụm xe nhẹ, cụm xe tăng, công sự có tháp, máy bay) trong khoảng 90 giây từ lúc tiếp đất, có và không có phòng không đối phương; tính cả thời gian không bắn (di chuyển, xoay tháp, nạp đạn, bay vòng, bị pháo sáng và APS chặn). Giá trị = sát thương thực × hệ số sống sót / CP. Mọi quyết định cân bằng của prompt 13 dựa trên bảng này.

**vs cụm xe** (prompt 25 E3): DPS lên 5 xe nhẹ cách nhau 4 m (một xe ở giữa, bốn xe quanh nó), mọi phát nhắm xe giữa; tính từ dữ liệu, không chạy mô phỏng: phát trúng thẳng như bảng 9 (vs nhẹ), cộng nổ lan lên bốn xe quanh theo bán kính nổ (dao động ±15%), độ suy giảm (25% ở mép, nhiệt áp 62,5%), cấp xuyên của mảnh nổ (tối đa 1 trên mặt đất) vào hông xe và hệ số loại đạn; bom chùm rải bom con lên cả năm. Trong ngoặc: bao nhiêu lần DPS lên một xe. **Hỗ trợ / CP** (E2): giá trị hỗ trợ của xe hỗ trợ, bảng dưới.

Số đo: `combat_value_pt6_after_summary.tsv`; chỉ các thẻ còn trong roster, CP theo dữ liệu hiện tại.

#### Giá trị hỗ trợ (E2)

Xe hỗ trợ không gây sát thương nên giá trị thực chiến bỏ sót chúng. Phép đo riêng (`CombatValueMeasure.MeasureTheSupportVehicles`, và `MeasureTheRoster` ghi vào cùng bảng tổng hợp): một xe đi cùng hai tăng chủ lực, một xe bộ binh, một pháo phản lực và một trực thăng tấn công, do AI chiến thuật dẫn, đánh một nhóm bắn tên lửa dẫn đường và bắn thẳng (hai BMPT, một tăng chủ lực, một trực thăng tấn công; hết đợt này 3 giây có đợt sau) trong 3 phút. Ghi: **máu sửa được**, **đạn nạp thêm** (viên: băng vơi được nạp đầy, phần thời gian nạp tại chỗ được rút ngắn quy ra viên, đạn trực thăng nạp cạnh xe), **tên lửa hút được** (đạn dẫn đường của địch bị gây nhiễu lúc phóng, và phần trăm trên mọi đạn dẫn đường địch bắn), **sát thương khiên chặn**. Giá trị hỗ trợ / CP = (máu sửa + khiên chặn + sát thương của số đạn nạp thêm và của tên lửa bị hút) × hệ số sống sót / CP, cùng thang với giá trị thực chiến. Ô "—": chưa đo (chờ phase kiểm tra).

| Xe | CP | Cơ chế | Máu sửa | Đạn nạp thêm (viên) | Tên lửa hút (quả) | Khiên chặn | Giá trị hỗ trợ / CP |
|---|---|---|---|---|---|---|---|
| **Xe công binh** | 3 | sửa 2,5% máu/s trong 14 m | — | — | — | — | — |
| **Xe tiếp đạn** | 4 | nạp đạn trong 14 m (1 viên mỗi 4 s, nạp tại chỗ nhanh ×3); trực thăng nạp đạn cạnh xe (trong 12 m) | — | — | — | — | — |
| **Xe sửa chữa lưu động** | 4 | sửa 1,5% máu/s trong 20 m | — | — | — | — | — |
| **Xe laser chói lóa** | 6 | gây nhiễu đạn dẫn đường trong 30 m | — | — | — | — | — |
| **Xe gây nhiễu điện tử** | 6 | gây nhiễu đạn dẫn đường trong 32 m | — | — | — | — | — |
| **Xe gây nhiễu định vị** | 6 | gây nhiễu đạn dẫn đường trong 28 m | — | — | — | — | — |
| **Xe phát khiên** | 8 | khiên 1.000 máu, bán kính 12 m, đầy lại sau 20 s | — | — | — | — | — |

Sheet: 02_phuong_tien/Xe_suy_ra — Xe: suy ra (120 dòng, 17 cột)

| id | nap_dan_may_bay | nap_lai_may_bay_s | he_so_vu_khi | dps_vu_khi_chinh | dps_vu_khi_chinh_game | dps_vu_khi_chinh_may_bay | dps_vu_khi_chinh_may_bay_game | mau_tren_cp | dps_tren_cp |
|---|---|---|---|---|---|---|---|---|---|
| aa_57mm_vehicle | 0 | 0.0 | 1.0 | 163.33800000000002 | 163.33800000000002 | 163.33800000000002 | 163.33800000000002 | 238.54285714285714 | 23.334000000000003 |
| aa_gun_vehicle | 0 | 0.0 | 1.0 | 92.90322580645162 | 92.90322580645162 | 92.90322580645162 | 92.90322580645162 | 204.96666666666667 | 15.483870967741936 |
| aa_vehicle | 0 | 0.0 | 1.0 | 88.0 | 88.0 | 88.0 | 88.0 | 192.5 | 22.0 |
| aerial_tanker | 0 | 0.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 317.77777777777777 | 0.0 |
| airborne_light_tank | 0 | 0.0 | 1.0 | 50.879999999999995 | 50.879999999999995 | 50.879999999999995 | 50.879999999999995 | 266.56666666666666 | 8.479999999999999 |
| airborne_light_tank_chute | 0 | 8.5 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 |  |  |
| airborne_vehicle | 0 | 0.0 | 1.0 | 38.89000000000001 | 38.89000000000001 | 38.89000000000001 | 38.89000000000001 | 187.0 | 5.555714285714287 |
| airborne_vehicle_chute | 0 | 8.5 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 |  |  |
| ammo_carrier | 0 | 0.0 | 1.0 | 58.96958410924891 | 58.96958410924891 | 58.96958410924891 | 58.96958410924891 | 286.0 | 14.742396027312228 |
| amphib_light_vehicle | 0 | 0.0 | 1.0 | 60.24878493317134 | 60.24878493317134 | 60.24878493317134 | 60.24878493317134 | 204.28571428571428 | 8.606969276167336 |
| armored_bulldozer | 0 | 0.0 | 1.0 | 78.574375 | 78.574375 | 78.574375 | 78.574375 | 416.35 | 9.821796875 |
| armored_car | 0 | 0.0 | 1.0 | 51.64034021871204 | 51.64034021871204 | 51.64034021871204 | 51.64034021871204 | 220.0 | 17.21344673957068 |
| artillery | 0 | 0.0 | 1.0 | 42.34173339079547 | 42.34173339079547 | 42.34173339079547 | 42.34173339079547 | 112.82857142857142 | 6.0488190558279245 |
| attack_helicopter | 8 | 9.0 | 1.0 | 64.33287804878049 | 64.33287804878049 | 64.33287804878049 | 64.33287804878049 | 201.8 | 5.848443458980044 |
| attack_jet | 0 | 14.0 | 1.0 | 456.5291393284446 | 456.5291393284446 | 456.5291393284446 | 456.5291393284446 | 107.8 | 19.8490930142802 |

*15 / 120 dòng đầu: xem sheet 02_phuong_tien/Xe_suy_ra; in 10 / 17 cột; 5 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 02_phuong_tien/Hoi_quy — Hồi quy theo CP (12 dòng, 5 cột)

| id | gia_tri | y_nghia |
|---|---|---|
| dps_he_so | 34.33713767277216 | hệ số a của DPS theo CP |
| dps_so_mu | 0.33805260449762203 | số mũ b của DPS theo CP |
| mau_he_so | 252.3044581970855 | hệ số a của máu theo CP |
| mau_so_mu | 0.8216877482994875 | số mũ b của máu theo CP |
| n_dps | 73.0 | số xe có DPS > 0 |
| n_mau | 79.0 | số xe trong hồi quy máu |
| trung_vi_dps_tren_cp_9_15 | 5.405517559572274 | trung vị DPS / CP, dải 9-15 |
| trung_vi_dps_tren_cp_ge16 | 4.66849585900156 | trung vị DPS / CP, dải >=16 |
| trung_vi_dps_tren_cp_le8 | 10.024829298572314 | trung vị DPS / CP, dải <=8 |
| trung_vi_mau_tren_cp_9_15 | 148.7 | trung vị máu / CP, dải 9-15 |
| trung_vi_mau_tren_cp_ge16 | 146.66339285714287 | trung vị máu / CP, dải >=16 |
| trung_vi_mau_tren_cp_le8 | 187.0 | trung vị máu / CP, dải <=8 |

Sheet: 02_phuong_tien/Hoi_quy_du_lieu — Hồi quy: dữ liệu (79 dòng, 19 cột)

| id | cp | mau_hp | dps_nhe | dps_nang | dps_may_bay | dps_max | ln_cp | ln_mau | ln_dps |
|---|---|---|---|---|---|---|---|---|---|
| aa_57mm_vehicle | 7 | 1669.8 | 81.66900000000001 | 40.834500000000006 | 212.33940000000004 | 212.33940000000004 | 1.9459101490553132 | 7.4204591377599 | 5.358185937924469 |
| aa_gun_vehicle | 6 | 1229.8 | 46.45161290322581 | 23.225806451612904 | 120.7741935483871 | 120.7741935483871 | 1.791759469228055 | 7.114606833519369 | 4.793922633112336 |
| aa_vehicle | 4 | 770.0 | 44.0 | 22.0 | 114.4 | 114.4 | 1.3862943611198906 | 6.646390514847729 | 4.739701078945697 |
| aerial_tanker | 9 | 2860.0 | 0.0 | 0.0 | 0.0 | 0.0 | 2.1972245773362196 | 7.958576903813898 |  |
| airborne_light_tank | 6 | 1599.4 | 61.05599999999999 | 43.248 | 15.263999999999998 | 61.05599999999999 | 1.791759469228055 | 7.377383837897789 | 4.111791475825822 |
| airborne_vehicle | 7 | 1309.0 | 38.89000000000001 | 19.445000000000004 | 0.0 | 38.89000000000001 | 1.9459101490553132 | 7.1770187659099 | 3.660737148167656 |
| amphib_light_vehicle | 7 | 1430.0 | 60.24878493317134 | 30.12439246658567 | 0.0 | 60.24878493317134 | 1.9459101490553132 | 7.265429723253953 | 4.098482405083113 |
| armored_bulldozer | 8 | 3330.8 | 94.28925 | 66.78821875 | 0.0 | 94.28925 | 2.0794415416798357 | 8.110967794361665 | 4.54636718526205 |
| armored_car | 3 | 660.0 | 51.64034021871204 | 25.82017010935602 | 0.0 | 51.64034021871204 | 1.0986122886681098 | 6.492239835020471 | 3.9443031542354388 |
| artillery | 7 | 789.8 | 42.34173339079547 | 35.99047338217615 | 0.0 | 42.34173339079547 | 1.9459101490553132 | 6.671779748852549 | 3.7457732046607606 |
| attack_helicopter | 11 | 2219.8 | 77.19945365853658 | 64.33287804878049 | 0.0 | 77.19945365853658 | 2.3978952727983707 | 7.70517238071788 | 4.346392380043727 |
| attack_jet | 23 | 2479.4 | 456.5291393284446 | 228.2645696642223 | 0.0 | 456.5291393284446 | 3.1354942159291497 | 7.815771874404047 | 6.12365253004263 |
| auto_loader_howitzer | 9 | 1830.4 | 52.36363636363637 | 26.181818181818183 | 0.0 | 52.36363636363637 | 2.1972245773362196 | 7.512289801185479 | 3.958212387897521 |
| ballistic_launcher | 14 | 1309.0 | 48.1648945755992 | 48.1648945755992 | 0.0 | 48.1648945755992 | 2.6390573296152584 | 7.1770187659099 | 3.874630427389569 |
| bmpt | 11 | 3190.0 | 133.93278924627938 | 66.96639462313969 | 0.0 | 133.93278924627938 | 2.3978952727983707 | 8.06777619577889 | 4.8973381013322435 |

*15 / 79 dòng đầu: xem sheet 02_phuong_tien/Hoi_quy_du_lieu; in 10 / 19 cột; 7 cột khác (và raw_json, nguon): xem sheet.*

## 12. Hỗ trợ hỏa lực

Trạng thái: Đã áp

Nguồn dữ liệu: 02_phuong_tien/The_ho_tro. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §12. Hỗ trợ.

Thẻ hỗ trợ trong bộ bài (2 ô), gọi vào một điểm trên bản đồ; không gọi được vào vùng căn cứ địch; vật phẩm dùng một lần mua bằng xu. Mỗi thẻ hỗ trợ có clip Xem bắn riêng (gọi hỏa lực lên một cụm mục tiêu).

![Clip Xem bắn của các thẻ hỗ trợ (pháo kích, không kích, tên lửa hành trình, napalm, ném bom rải thảm, MOAB, bom chùm, m…](../images/02_phuong_tien/r6_supports.png)

*Hình: Clip Xem bắn của các thẻ hỗ trợ (pháo kích, không kích, tên lửa hành trình, napalm, ném bom rải thảm, MOAB, bom chùm, máy bay pháo, EMP, khói, tiếp tế, chi viện). Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

Sheet: 02_phuong_tien/The_ho_tro — Thẻ hỗ trợ (40 dòng, 36 cột)

| id | ten_en | ten_vi | units | so_voi_ban_goc | blast_m | consumable | cooldown_s | count | cp |
|---|---|---|---|---|---|---|---|---|---|
| air_raid | Air raid | Không kích bất ngờ |  | giong | 8 |  | 0 | 10 |  |
| airstrike | Airstrike | Không kích |  | giong | 10 |  | 90 | 4 | 9 |
| ammo_resupply | Ammo resupply | Thả dù tiếp đạn |  | giong |  |  | 60 | 1 | 3 |
| artillery_barrage | Barrage | Pháo kích |  | giong | 7 |  | 60 | 6 | 5 |
| bug_crash | Icarus crashing | Icarus rơi |  | giong | 16 |  | 0 | 1 |  |
| chaff_strike | Radar chaff | Rải nhiễu radar |  | giong |  |  | 45 | 1 | 2 |
| cluster_at_strike | AT cluster bomb | Bom chùm chống tăng |  | giong | 3 |  | 90 | 10 | 9 |
| cluster_strike | Cluster bombs | Bom chùm |  | giong | 5.5 | TRUE | 15 | 30 |  |
| cruise_missile | Cruise missile | Tên lửa hành trình |  | giong | 9 |  | 120 | 1 | 14 |
| decoy_paradrop | Decoy paradrop | Mồi nhử thả dù | decoy_tank;decoy_tank;decoy_tank | giong |  |  | 45 | 3 | 2 |
| drone_intercept_strike | Drone intercept strike | Đòn tên lửa đánh chặn drone |  | giong | 2 |  | 40 | 6 | 3 |
| emp_blast | EMP blast | Bom EMP |  | giong |  | TRUE | 20 | 1 |  |
| escort_drop.aa_vehicle |  |  | aa_vehicle | giong |  |  | 0 | 1 |  |
| escort_drop.engineer_vehicle |  |  | engineer_vehicle | giong |  |  | 0 | 1 |  |
| escort_drop.ifv |  |  | ifv | giong |  |  | 0 | 1 |  |
| field_repair | Field repair | Sửa chữa toàn quân |  | giong |  | TRUE | 30 | 5 |  |
| field_tower | Field tower | Tháp dã chiến | guard_tower;atgm_tower | giong |  |  | 90 | 1 | 6 |
| glide_bomb_strike | Glide bomb strike | Đòn bom lượn |  | giong | 10 |  | 90 | 2 | 8 |
| guided_shell_strike | Guided shell | Đạn pháo dẫn đường |  | giong | 6 |  | 45 | 1 | 4 |
| gunship_support | Gunship on call | Pháo hạm yểm trợ | sky_gunship | giong |  | TRUE | 30 | 1 |  |
| hq_barrage |  |  |  | moi | 8 |  | 0 | 3 |  |
| illum_flare_strike | Illumination flare | Pháo sáng chiếu sáng |  | giong |  |  | 30 | 1 | 1 |
| instant_counter_battery | Instant counter-battery | Phản pháo tức thì |  | giong | 7 |  | 75 | 4 | 6 |
| jam_storm | Jamming storm | Bão gây nhiễu |  | giong |  |  | 90 | 1 | 5 |
| leviathan_cruise_mark | Leviathan's cruise missile | Tên lửa hành trình Leviathan |  | doi | 10 |  | 0 | 1 |  |
| leviathan_cruise_mark_7 | Caspian's cruise missile | Tên lửa hành trình Caspian |  | moi | 7 |  | 0 | 1 |  |
| leviathan_shell | Leviathan's shell | Đạn pháo Leviathan |  | doi | 14 |  | 0 | 1 |  |
| moab | MOAB | Bom MOAB |  | giong | 27 | TRUE | 20 | 1 |  |
| napalm_strike | Napalm strike | Bom napalm |  | giong | 9 |  | 90 | 8 | 9 |
| pod_drop | Drop pod | Khoang đổ bộ |  | giong | 4 |  | 0 | 1 |  |
| reinforcements | Airdropped armour | Tiếp viện thả dù | main_battle_tank;main_battle_tank;ifv | giong |  | TRUE | 30 | 3 |  |
| remote_mines | Remote mines | Mìn rải từ xa |  | giong | 4 |  | 60 | 8 | 5 |
| repair_drop | Repair | Sửa chữa |  | giong |  |  | 60 | 6 | 4 |
| sead_strike | SEAD strike | Đòn SEAD |  | giong | 3 |  | 90 | 1 | 7 |
| shield_dome | Shield dome | Khiên vòm |  | giong |  | TRUE | 20 | 1 |  |
| smoke_screen | Smoke | Màn khói |  | giong |  |  | 30 | 1 | 2 |
| super_gun_shell | Super-gun shell | Đạn siêu pháo |  | giong | 15 |  | 0 | 1 |  |
| supergun_shell | Rail supergun shell | Đạn siêu pháo đường ray |  | giong | 12 |  | 0 | 1 |  |
| uav_loiter_strike_support | Loitering UAV strike | UAV lượn tấn công | uav_loiter_strike | giong |  |  | 75 | 1 | 6 |
| uav_scan | UAV scan | UAV quét |  | giong |  |  | 45 | 1 | 2 |

*in 10 / 36 cột; 14 cột khác (và raw_json, nguon): xem sheet.*

### 12b. Bảng giá, hệ đạn và hồi đạn

Trạng thái: Đã áp

Nguồn dữ liệu: (không có sheet; chỉ văn bản). Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §12b. Bảng giá, §12b. Hệ đạn.

#### 12b. Bảng giá

Mọi giá trong game ở một chỗ. **CP** là điểm chỉ huy trả mỗi lần gọi trong trận. **Xu** là tiền duy nhất ngoài trận: mua thẻ cao cấp, mua sớm thẻ chiến dịch trước khi thắng màn mở khóa, mua vật phẩm. Thẻ có sẵn không cần mua. Giá lên hạng thẻ, hòm và gói xu ở phần kinh tế.

#### Tháp căn cứ (22)

Tháp không tốn CP khi đặt vào căn cứ: nó chiếm một ô theo cỡ. Bị phá trong trận thì xây lại bằng CP sau một thời gian chờ.

#### 12b. Hệ đạn và hồi đạn

- **Lượng đạn:** bom, tên lửa và rốc-két của máy bay và trực thăng có số lượng khi đầy đạn (ghi ở mục "Đạn và nạp đạn" trên mỗi thẻ); pháo máy bay và súng máy không giới hạn, chỉ thay băng.
- **Hồi dần trên chiến trường:** từng quả hồi theo thời gian, không cần căn cứ. Đang tấn công hoặc trong tầm phòng không/tiêm kích địch: một nửa tốc độ; ra khỏi vùng nguy hiểm liên tục 3 giây: đủ tốc độ.
- **Vòng chờ gần:** một vòng bay ngay sau tuyến quân ta gần nhất, ngoài tầm phòng không đã biết, cách chỗ giao tranh khoảng 2–3 giây bay; tính lại liên tục theo chiến tuyến. Không đơn vị nào bay về căn cứ hay ra ngoài bản đồ để nạp.
- **Rút đúng lúc:** hết đạn giữa lượt thì làm xong lượt (bổ nhào, lượt ném bom, vòng bay) rồi mới ra vòng chờ, bay theo đường thật, vẫn bị bắn được; chỉ huy AI cho ra sớm khi đạn dưới 20% và đang có quãng lặng.
- **Nạp nhanh hơn:** Bãi đáp ×2 (và hồi 3% máu/giây), sở chỉ huy ×1,5 (1% máu/giây), trực thăng cạnh Xe tiếp đạn ×2. Chỉ ghé khi nhanh hơn vòng chờ hoặc cần hồi máu.
- **Máy bay ném bom:** chỉ vào lượt mới khi có ít nhất 2/3 tải bom; ưu tiên cụm quân và công trình, không thả gần quân ta, nghỉ trước khi ném lại cùng khu vực. Oanh tạc cơ 9 quả, máy bay tàng hình 2, Su-25 16 rốc-két, không kích bất ngờ 10, bom chùm 30 quả con.
- **Xe tiếp đạn (mới, 4 CP):** điểm nạp tiền phương: trực thăng đứng cạnh hồi đạn nhanh gấp đôi, bệ phóng và xe tên lửa quanh nó nạp nhanh gấp ba. Xe công binh chỉ còn sửa chữa (3 CP).
- **Bãi đáp:** nhánh hạng 7: Nhà chứa (+1 trần máy bay) hoặc Phục vụ nhanh. AI địch đặt Bãi đáp trong căn cứ; phá Bãi đáp pháo đài trong Công thành được 12 CP.
- **Icon trên chiến trường:** cạnh thanh máu: sắp hết (vàng), hết (đỏ nhấp nháy), đang ra vòng chờ, đang hồi (vòng tiến độ mờ khi hồi chậm, sáng khi hồi đủ), lóe sáng khi đầy. Địch chỉ hiện hết đạn và đang ra vòng chờ. Bản đồ nhỏ hiện vòng chờ của ta.

### 12c. Commander

Trạng thái: Đã áp

Nguồn dữ liệu: 02_phuong_tien/Commander; 02_phuong_tien/Commander_noi_tai; 02_phuong_tien/Commander_gia; 06_ai/AI_tuong. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §12c.

Người chơi chọn một commander trước trận; nội tại của nó áp cho cả phe, trong mọi chế độ. Mỗi màn gắn với một tướng địch thì địch mang nội tại của tướng đó. Commander mở dần theo chương. Không còn chọn học thuyết riêng: lợi thế của năm học thuyết cũ đã gộp vào commander hợp lối chơi (Crown: thiết giáp, Hawk: không quân, Longshot: pháo binh, Rush: chớp nhoáng, Ledger: hậu cần), chỗ trùng loại thưởng thì gộp thành một con số, không cộng dồn; bảng dưới là số mới.

#### Commander của người chơi (14)

| Commander | Nhóm | Vai trò | Hợp lối chơi | Điểm mạnh | Điểm yếu | Mở khóa |
|---|---|---|---|---|---|---|
| **Đại tá Marcus Kade** Iron | chiến đấu | Chỉ huy 7th Mechanized Brigade · biệt danh Iron | Hợp với: Bộ bài cân bằng | Toàn quân +5% sát thương và +5% máu. | Không có. | Mở ở chương 1 |
| **Kỹ sư Mara Lind** Kỹ sư trưởng | chiến đấu | Kỹ sư trưởng, phụ trách căn cứ | Hợp với: Công binh và căn cứ vững | Trạm sửa chữa và công binh sửa nhanh hơn 25%; công binh rẻ hơn 20% CP. | Máy bay và trực thăng −10% sát thương. | Mở ở chương 2 |
| **Trung úy Jonah Reyes** Hawk | chiến đấu | Chỉ huy không quân · biệt danh Hawk | Hợp với: Máy bay và trực thăng | Máy bay và trực thăng +10% sát thương và +20% máu, hồi đạn nhanh hơn 15%; trần máy bay +1; yểm trợ hồi nhanh hơn 15%. | Tháp −10% máu. | Mở ở chương 3 |
| **Đại úy Nadia Kerr** Tình báo | chiến đấu | Sĩ quan tình báo | Hợp với: Trinh sát và đánh dấu mục tiêu | +15% tầm nhìn; phát hiện tàng hình từ xa hơn 25%; địch đang bị lộ nhận thêm 5% sát thương. | Xe hạng nặng −5% máu. | Mở ở chương 4 |
| **Tiến sĩ Elara Venn** Queen | chiến đấu | Drone của Hegemon; người tạo ra Hive · biệt danh Queen | Hợp với: Drone | Mọi drone +15% máu và +10% sát thương; drone ta bị gây nhiễu ít hơn 30%. | Xe tăng −5% sát thương. | Mở sau khi xong chương 5 |
| **Đại úy Kaia Mendez** Rush | chiến đấu | Đột kích đường không, lực lượng phản ứng nhanh | Hợp với: Xe nhanh, tấn công sớm | Xe +15% tốc độ; trinh sát và xe nhẹ +15% máu; thả dù nhanh hơn 25%. | Toàn quân −5% máu. | Mở ở Xen kẽ II |
| **Thiếu tá Brandt** Bulwark | chiến đấu | Đồn trú bờ biển phía tây của Hegemon · biệt danh Bulwark | Hợp với: Tháp và tháp dã chiến | Tháp +15% máu và +10% sát thương; tháp thả dù rẻ hơn 20% CP. | Xe −5% tốc độ. | Mở ở chương 6 |
| **Thiếu tá Piet Dahl** Longshot | chiến đấu | Pháo binh lữ đoàn | Hợp với: Pháo binh | Pháo binh +15% sát thương, +10% tầm bắn và +25% máu; yểm trợ hồi nhanh hơn 25%. | Xe bắn thẳng −10% sát thương. | Mở ở chương 7 |
| **Thiếu tá Otto Brenn** Ledger | kinh tế | Sĩ quan hậu cần lữ đoàn | Hợp với: Trận dài | Thu nhập CP +15%; trần tiếp tế +10%. | Toàn quân −5% sát thương. | Mở ở Xen kẽ I |
| **Đại úy Tomas Adler** Flag | kinh tế | Trinh sát tiền phương, chiếm cứ điểm | Hợp với: Chiếm và giữ cứ điểm | Mỗi cứ điểm cho thêm 75% CP; chiếm nhanh hơn 30%. | Ở chế độ không có cứ điểm, thu nhập −5%. | Mở ở chương 4 |
| **Đại úy Ines Varro** Tide | kinh tế | Đội xe và tiếp viện số đông | Hợp với: Nhiều xe rẻ | Xe giá từ 5 CP trở xuống rẻ hơn 15%; trần tiếp tế +15%. | Toàn quân −5% máu. | Mở ở chương 8 |
| **Đại tá August Reyn** Crown | kinh tế | Thiết giáp hạng nặng dự bị | Hợp với: Ít xe đắt, hạng nặng | Xe tăng, xe hạng nặng và xe giá từ 9 CP trở lên +20% máu; xe giá từ 9 CP trở lên +15% sát thương. | Mọi xe đắt hơn 10% CP. | Mở ở Xen kẽ III |
| **Thượng sĩ nhất Lena Quist** Magpie | kinh tế | Thu hồi và tận dụng chiến lợi phẩm | Hợp với: Đổi quân, hạ nhiều địch | Hạ địch hoàn 35% CP thay vì 25% (mọi khoản hoàn vẫn trong trần 45%). | Xe ta bị hạ không được hoàn CP. | Mở ở chương 8 |
| **Đại úy Selma Okoye** Vault | kinh tế | Quản lý ngân quỹ lữ đoàn | Hợp với: Tích CP để mua xe lớn | Trần CP tích trữ từ 30 lên 45; khi đang có từ 20 CP trở lên, thu nhập +10%. | 90 giây đầu trận thu nhập −10%. | Mở ở chương 10 |

#### Nội tại của tướng địch (8)

| Tướng | Điểm mạnh | Điểm yếu |
|---|---|---|
| **Thiếu tá Brandt** | Tháp +15% máu. | Xe −5% tốc độ. |
| **Tướng Viktor Varga** | Xe tăng và xe hạng nặng +10% máu. | Máy bay −10% sát thương. |
| **Đại tá Ilya Orlov** | Pháo binh +15% tầm, tản mát ít hơn 20%. | Xe nhẹ −5% máu. |
| **Đô đốc Magnus Kessler** | Tiếp viện rẻ hơn 10% CP; tàu +10% máu. | Tháp −5% máu. |
| **Tiến sĩ Elara Venn** | Drone +15% máu. | Xe tăng −5% sát thương. |
| **Kasimir Wolff** | Máy bay +10% sát thương; trần máy bay +1. | Xe mặt đất −5% sát thương. |
| **Tướng Roland Thorne** | Toàn quân +5% sát thương; quân dưới 50% máu được thêm 10% sát thương. | Không có. |
| **Giám đốc Lucien Aurel** | Vũ khí Năng lượng +15% sát thương; khiên +10% máu. | Xe nhẹ −5% máu. |

Sheet: 02_phuong_tien/Commander — Commander và nội tại tướng (22 dòng, 32 cột)

| id | ho | ten_vi | khai_bao_qua | air_cap | air_rearm | bank_bonus | delivery | early_income | early_seconds |
|---|---|---|---|---|---|---|---|---|---|
| adler | Economy | Đại úy {@adler} | new CommanderDef |  |  |  |  |  |  |
| brandt | Combat |  | new CommanderDef |  |  |  |  |  |  |
| brenn | Economy | Thiếu tá {@brenn} | new CommanderDef |  |  |  |  |  |  |
| dahl | Combat | Thiếu tá {@dahl} | Combat |  |  |  |  |  |  |
| gen.aurel | General |  | Gen |  |  |  |  |  |  |
| gen.brandt | General |  | Gen |  |  |  |  |  |  |
| gen.hung | General |  | Gen |  |  |  |  |  |  |
| gen.kessler | General |  | Gen |  |  |  |  |  |  |
| gen.orlov | General |  | Gen |  |  |  |  |  |  |
| gen.quaden | General |  | Gen | 1 |  |  |  |  |  |
| gen.sen | General |  | Gen |  |  |  |  |  |  |
| gen.varga | General |  | Gen |  |  |  |  |  |  |
| kade | Combat |  | Combat |  |  |  |  |  |  |
| kerr | Combat |  | new CommanderDef |  |  |  |  |  |  |
| lind | Combat |  | new CommanderDef |  |  |  |  |  |  |
| mendez | Combat | Đại úy {@mendez} | new CommanderDef |  |  |  | 0.75 |  |  |
| okoye | Economy | Đại úy {@okoye} | Econ |  |  | 15 |  | 0.9 | 90 |
| quist | Economy | Thượng sĩ nhất {@quist} | Econ |  |  |  |  |  |  |
| reyes | Combat |  | new CommanderDef | 1 | 1.15 |  |  |  |  |
| reyn | Economy | Đại tá {@reyn} | new CommanderDef |  |  |  |  |  |  |
| varro | Economy | Đại úy {@varro} | new CommanderDef |  |  |  |  |  |  |
| venn | Combat |  | new CommanderDef |  |  |  |  |  |  |

*in 10 / 32 cột; 19 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 02_phuong_tien/Commander_noi_tai — Commander: dòng nội tại (45 dòng, 8 cột)

| id | commander_id | thu_tu | reach_m | stat | value |
|---|---|---|---|---|---|
| adler/0 | adler | 0 | Vehicles | CaptureRate | 0.3 |
| brandt/0 | brandt | 0 | Towers | Health | 0.15 |
| brandt/1 | brandt | 1 | Towers | Damage | 0.1 |
| brandt/2 | brandt | 2 | Vehicles | Speed | -0.05 |
| brenn/0 | brenn | 0 | Army | Damage | -0.05 |
| dahl/0 | dahl | 0 | Artillery | Damage | 0.15 |
| dahl/1 | dahl | 1 | Artillery | Range | 0.1 |
| dahl/2 | dahl | 2 | Artillery | Health | 0.25 |
| dahl/3 | dahl | 3 | DirectFire | Damage | -0.1 |
| gen.aurel/0 | gen.aurel | 0 | Energy | Damage | 0.15 |
| gen.aurel/1 | gen.aurel | 1 | Shielded | Health | 0.1 |
| gen.aurel/2 | gen.aurel | 2 | Light | Health | -0.05 |
| gen.brandt/0 | gen.brandt | 0 | Towers | Health | 0.15 |
| gen.brandt/1 | gen.brandt | 1 | Vehicles | Speed | -0.05 |
| gen.hung/0 | gen.hung | 0 | Army | Damage | 0.05 |

*15 / 45 dòng đầu: xem sheet 02_phuong_tien/Commander_noi_tai.*

Sheet: 02_phuong_tien/Commander_gia — Commander: hệ số giá (5 dòng, 7 cột)

| id | commander_id | thu_tu | reach_m | scale |
|---|---|---|---|---|
| brandt/0 | brandt | 0 | AirdropTowers | 0.8 |
| gen.kessler/0 | gen.kessler | 0 | Vehicles | 0.9 |
| lind/0 | lind | 0 | Engineers | 0.8 |
| reyn/0 | reyn | 0 | Vehicles | 1.1 |
| varro/0 | varro | 0 | Cheap | 0.85 |

Sheet: 06_ai/AI_tuong — Tướng địch (12 dòng, 11 cột)

| id | chien_thuat_ua_thich | chien_dich_deck | chien_dich_supports | noi_tai | can_bang_deck | can_bang_elites | chien_dich_stance | chien_dich_style |
|---|---|---|---|---|---|---|---|---|
| aurel | all_out | heavy_tank;bmpt;railgun_truck;attack_helicopter;long_sam;he… | cruise_missile;airstrike;napalm_strike;sead_strike | gen.aurel |  |  | Attack | aurel |
| brandt | depth |  |  | gen.brandt |  |  |  |  |
| default | balanced |  |  | gen.default |  |  |  |  |
| hung |  | main_battle_tank;heavy_tank;titan_tank;bmpt;ifv;aa_vehicle;… | artillery_barrage;airstrike;cruise_missile | gen.hung |  |  | Attack | aurel |
| kessler | attrition | wheeled_gun;ifv;main_battle_tank;heavy_tank;sam_launcher;fp… | remote_mines;artillery_barrage;smoke_screen | gen.kessler |  |  | Defend | kessler |
| orlov | firepower | mlrs;artillery;mortar_carrier;heavy_rocket_artillery;sam_la… | artillery_barrage;cruise_missile;uav_scan | gen.orlov |  | Artillery | Defend | orlov |
| quaden |  | attack_helicopter;gunship_heli;attack_jet;fighter_jet;strik… | airstrike;sead_strike;napalm_strike | gen.quaden |  | Air | Attack | quaden |
| sen |  | strike_drone;fpv_carrier;lancet_truck;recon_drone;ew_jammer… | uav_scan;sead_strike;repair_drop | gen.sen |  | Drone | Attack | sen |
| thorne | balanced |  |  | gen.thorne |  |  |  |  |
| varga | breakthrough | light_tank;main_battle_tank;heavy_tank;tank_destroyer;ifv;f… | artillery_barrage;airstrike;smoke_screen | gen.varga | armored_bulldozer | Tank;Heavy | Attack | varga |
| venn | dispersal |  |  | gen.venn |  |  |  |  |
| wolff | air_superiority |  |  | gen.wolff |  |  |  |  |

## 13. Trang bị

Trạng thái: Đã áp

Nguồn dữ liệu: 02_phuong_tien/Trang_bi; 02_phuong_tien/Trang_bi_bo; 02_phuong_tien/Trang_bi_dac_tinh; 02_phuong_tien/Trang_bi_mo_dun; 02_phuong_tien/Trang_bi_dong_phu; 11_meta_giao_dien/Trang_bi_hang. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §13. Trang bị.

Mỗi nhánh (Thiết giáp, Xe nhẹ, Pháo binh, Không quân) có 7 ô: Vũ khí, Nạp đạn, Giáp, Quang học, Động cơ, Sửa chữa và Đặc biệt. Một món gồm: **loại đồ** (có dòng ẩn riêng), **chỉ số chính** tăng theo cấp (40% → 100%), **0/1/2/2/2 chỉ số phụ** theo độ hiếm (lăn 60–100%, có thanh chất lượng, tăng ở cấp 5/10/15/20), **một dòng unique** ở Sử thi và Huyền thoại (chọn 1 trong 3 khi ghép lên Sử thi), và **một thương hiệu** (bộ 2 món và 4 món). Ghép 3 món cùng ô cùng độ hiếm để lên bậc. Mỗi chỉ số có trần cho cả bộ.

Thường · cấp tối đa 5Khá · cấp tối đa 10Hiếm · cấp tối đa 15Sử thi · cấp tối đa 20Huyền thoại · cấp tối đa 25

#### Loại đồ (38)

|  | Loại | Ô | Dòng ẩn (Huyền thoại, cấp tối đa) | Thường → Huyền thoại |
|---|---|---|---|---|
|  | **Nòng dài** | Vũ khí | +8% tầm bắn | +2% tầm bắn / +3% tầm bắn / +4% tầm bắn / +6% tầm bắn / +8% tầm bắn |
|  | **Lõi xuyên vonfram** | Vũ khí | +1,0 cấp xuyên | +0,4 cấp xuyên / +0,55 cấp xuyên / +0,7 cấp xuyên / +0,85 cấp xuyên / +1,0 cấp xuyên |
|  | **Thuốc nổ phá mảnh** | Vũ khí | +20% bán kính nổ (không nổ: mạnh hơn với xe nhẹ) | +5% bán kính nổ (không nổ: mạnh hơn với xe nhẹ) / +8% bán kính nổ (không nổ: mạnh hơn với xe nhẹ) / +12% bán kính nổ (không nổ: mạnh hơn với xe nhẹ) / +16% bán kính nổ (không nổ: mạnh hơn với xe nhẹ)… |
|  | **Ngòi nổ cận đích** | Vũ khí | +20% sát thương lên máy bay | +5% sát thương lên máy bay / +8% sát thương lên máy bay / +12% sát thương lên máy bay / +16% sát thương lên máy bay / +20% sát thương lên máy bay |
|  | **Đạn phá boong-ke** | Vũ khí | +24% sát thương lên công trình | +6% sát thương lên công trình / +9% sát thương lên công trình / +13% sát thương lên công trình / +18% sát thương lên công trình / +24% sát thương lên công trình |
|  | **Nòng nặng** đánh đổi | Vũ khí | +12% tầm bắn -7% tốc độ | +0% tầm bắn / +0% tầm bắn / +8% tầm bắn / +10% tầm bắn / +12% tầm bắn |
|  | **Đạn đánh hông** | Vũ khí | +20% sát thương khi bắn trúng hông và đuôi | +5% sát thương khi bắn trúng hông và đuôi / +8% sát thương khi bắn trúng hông và đuôi / +12% sát thương khi bắn trúng hông và đuôi / +16% sát thương khi bắn trúng hông và đuôi / +20% sát thương khi b… |
|  | **Đạn nổ trên không** | Vũ khí | +30% sát thương lên drone; bắn hạ một phần rốc-két, tên lửa và drone nhắm vào nó | +8% sát thương lên drone; bắn hạ một phần rốc-két, tên lửa và drone nhắm vào nó / +12% sát thương lên drone; bắn hạ một phần rốc-két, tên lửa và drone nhắm vào nó / +18% sát thương lên drone; bắn hạ… |
|  | **Nạp đạn băng chuyền** | Nạp đạn | -20% thời gian nạp băng | -5% thời gian nạp băng / -8% thời gian nạp băng / -12% thời gian nạp băng / -16% thời gian nạp băng / -20% thời gian nạp băng |
|  | **Giá đạn mở rộng** | Nạp đạn | +30% sức chứa băng đạn | +10% sức chứa băng đạn / +15% sức chứa băng đạn / +20% sức chứa băng đạn / +25% sức chứa băng đạn / +30% sức chứa băng đạn |
|  | **Tiếp đạn dây** | Nạp đạn | +25% tốc bắn súng phụ | +8% tốc bắn súng phụ / +12% tốc bắn súng phụ / +16% tốc bắn súng phụ / +20% tốc bắn súng phụ / +25% tốc bắn súng phụ |
|  | **Giá phóng loạt** | Nạp đạn | -30% khoảng cách giữa các phát trong loạt | -10% khoảng cách giữa các phát trong loạt / -15% khoảng cách giữa các phát trong loạt / -20% khoảng cách giữa các phát trong loạt / -25% khoảng cách giữa các phát trong loạt / -30% khoảng cách giữa c… |
|  | **Cò nhạy** đánh đổi | Nạp đạn | +15% tốc độ bắn +14% độ tản mát | +0% tốc độ bắn / +0% tốc độ bắn / +10% tốc độ bắn / +12% tốc độ bắn / +15% tốc độ bắn |
|  | **Băng đạn dự phòng** | Nạp đạn | Bệ phóng hết đạn được nạp lại ngay 100% băng, một lần mỗi mạng | Bệ phóng hết đạn được nạp lại ngay 40% băng, một lần mỗi mạng / Bệ phóng hết đạn được nạp lại ngay 55% băng, một lần mỗi mạng / Bệ phóng hết đạn được nạp lại ngay 70% băng, một lần mỗi mạng / Bệ phón… |
|  | **Giáp tổng hợp gắn thêm** | Giáp | -15% sát thương nổ lõm | -4% sát thương nổ lõm / -6% sát thương nổ lõm / -9% sát thương nổ lõm / -12% sát thương nổ lõm / -15% sát thương nổ lõm |
|  | **Lớp lót chống mảnh** | Giáp | -15% sát thương nổ mạnh | -4% sát thương nổ mạnh / -6% sát thương nổ mạnh / -9% sát thương nổ mạnh / -12% sát thương nổ mạnh / -15% sát thương nổ mạnh |
|  | **Thép ốp tăng cường** | Giáp | +1,0 cấp giáp hông và sau | +0,4 cấp giáp hông và sau / +0,55 cấp giáp hông và sau / +0,7 cấp giáp hông và sau / +0,85 cấp giáp hông và sau / +1,0 cấp giáp hông và sau |
|  | **Thân xe chống cháy** | Giáp | -25% sát thương lửa, cháy ngắn hơn | -8% sát thương lửa, cháy ngắn hơn / -12% sát thương lửa, cháy ngắn hơn / -16% sát thương lửa, cháy ngắn hơn / -20% sát thương lửa, cháy ngắn hơn / -25% sát thương lửa, cháy ngắn hơn |
|  | **Buồng lái bọc giáp** | Giáp | +1,0 cấp giáp mọi mặt | +0,4 cấp giáp mọi mặt / +0,55 cấp giáp mọi mặt / +0,7 cấp giáp mọi mặt / +0,85 cấp giáp mọi mặt / +1,0 cấp giáp mọi mặt |
|  | **Tấm giáp nguyên khối** đánh đổi | Giáp | Chỉ số chính: máu, lớn hơn 80% so với các bộ giáp khác; không có dòng phụ -6% tốc độ | 0% / 0% / 0% / 0% / 0% |
|  | **Lớp phủ chống radar** | Giáp | Tên lửa địch phải lại gần hơn 20% mới khóa được | Tên lửa địch phải lại gần hơn 6% mới khóa được / Tên lửa địch phải lại gần hơn 9% mới khóa được / Tên lửa địch phải lại gần hơn 13% mới khóa được / Tên lửa địch phải lại gần hơn 16% mới khóa được / T… |
|  | **Giáp nêm mặt trước** | Giáp | -18% sát thương từ phía trước | -5% sát thương từ phía trước / -8% sát thương từ phía trước / -11% sát thương từ phía trước / -15% sát thương từ phía trước / -18% sát thương từ phía trước |
|  | **Lồng chống rốc-két** | Giáp | -22% sát thương nổ lõm từ rốc-két, tên lửa và drone (không tính nhiệt áp) | -6% sát thương nổ lõm từ rốc-két, tên lửa và drone (không tính nhiệt áp) / -9% sát thương nổ lõm từ rốc-két, tên lửa và drone (không tính nhiệt áp) / -13% sát thương nổ lõm từ rốc-két, tên lửa và dro… |
|  | **Mái che chống pháo** | Giáp | -22% sát thương pháo binh và bom | -6% sát thương pháo binh và bom / -9% sát thương pháo binh và bom / -13% sát thương pháo binh và bom / -17% sát thương pháo binh và bom / -22% sát thương pháo binh và bom |
|  | **Giáp gầm** | Giáp | -18% sát thương nổ lan và mìn (không tính trúng trực tiếp) | -5% sát thương nổ lan và mìn (không tính trúng trực tiếp) / -8% sát thương nổ lan và mìn (không tính trúng trực tiếp) / -11% sát thương nổ lan và mìn (không tính trúng trực tiếp) / -15% sát thương nổ… |
|  | **Hệ truyền động** | Động cơ | +20% tốc độ xoay thân | +5% tốc độ xoay thân / +8% tốc độ xoay thân / +12% tốc độ xoay thân / +16% tốc độ xoay thân / +20% tốc độ xoay thân |
|  | **Hộp số hành quân** | Động cơ | +20% tốc độ khi không thấy địch | +5% tốc độ khi không thấy địch / +8% tốc độ khi không thấy địch / +12% tốc độ khi không thấy địch / +16% tốc độ khi không thấy địch / +20% tốc độ khi không thấy địch |
|  | **Động cơ độ quá mức** đánh đổi | Động cơ | +15% tốc độ -6% máu | +0% tốc độ / +0% tốc độ / +10% tốc độ / +12% tốc độ / +15% tốc độ |
|  | **Hộp số lùi** | Động cơ | +40% tốc độ lùi; bị áp sát thì lùi lại mà vẫn giữ mặt trước hướng về địch | +15% tốc độ lùi; bị áp sát thì lùi lại mà vẫn giữ mặt trước hướng về địch / +20% tốc độ lùi; bị áp sát thì lùi lại mà vẫn giữ mặt trước hướng về địch / +28% tốc độ lùi; bị áp sát thì lùi lại mà vẫn g… |
|  | **Hộp dụng cụ** | Sửa chữa | Bắt đầu tự sửa sớm hơn 3 giây sau khi trúng đạn | Bắt đầu tự sửa sớm hơn 1 giây sau khi trúng đạn / Bắt đầu tự sửa sớm hơn 1,5 giây sau khi trúng đạn / Bắt đầu tự sửa sớm hơn 2 giây sau khi trúng đạn / Bắt đầu tự sửa sớm hơn 2,5 giây sau khi trúng đ… |
|  | **Huấn luyện kíp lái** | Sửa chữa | -15% hồi chiêu kỹ năng và mô-đun | -4% hồi chiêu kỹ năng và mô-đun / -6% hồi chiêu kỹ năng và mô-đun / -9% hồi chiêu kỹ năng và mô-đun / -12% hồi chiêu kỹ năng và mô-đun / -15% hồi chiêu kỹ năng và mô-đun |
|  | **Bình chữa cháy** | Sửa chữa | -42% thời gian cháy, chậm và choáng | -10% thời gian cháy, chậm và choáng / -18% thời gian cháy, chậm và choáng / -26% thời gian cháy, chậm và choáng / -34% thời gian cháy, chậm và choáng / -42% thời gian cháy, chậm và choáng |
|  | **Máy đo xa la-de** | Quang học | -25% tản mát ở tầm xa | -8% tản mát ở tầm xa / -12% tản mát ở tầm xa / -16% tản mát ở tầm xa / -20% tản mát ở tầm xa / -25% tản mát ở tầm xa |
|  | **Bộ ổn định pháo** | Quang học | -30% tản mát khi di chuyển | -10% tản mát khi di chuyển / -15% tản mát khi di chuyển / -20% tản mát khi di chuyển / -25% tản mát khi di chuyển / -30% tản mát khi di chuyển |
|  | **Kính tiềm vọng chỉ huy** | Quang học | +20% tầm nhìn khi đứng yên | +5% tầm nhìn khi đứng yên / +8% tầm nhìn khi đứng yên / +12% tầm nhìn khi đứng yên / +16% tầm nhìn khi đứng yên / +20% tầm nhìn khi đứng yên |
|  | **Lưới ngụy trang** | Quang học | Đứng yên: địch phải lại gần hơn 18% mới phát hiện | Đứng yên: địch phải lại gần hơn 5% mới phát hiện / Đứng yên: địch phải lại gần hơn 8% mới phát hiện / Đứng yên: địch phải lại gần hơn 11% mới phát hiện / Đứng yên: địch phải lại gần hơn 15% mới phát… |
|  | **Trạm chuyển tiếp tín hiệu** | Quang học | +30% tốc độ chiếm cứ điểm | +10% tốc độ chiếm cứ điểm / +15% tốc độ chiếm cứ điểm / +20% tốc độ chiếm cứ điểm / +25% tốc độ chiếm cứ điểm / +30% tốc độ chiếm cứ điểm |
|  | **Cảnh báo la-de** | Quang học | Khi bị tên lửa chống tăng khóa: thả khói 8 m (mỗi 20 giây) | Khi bị tên lửa chống tăng khóa: thả khói 6 m (mỗi 20 giây) / Khi bị tên lửa chống tăng khóa: thả khói 6,5 m (mỗi 20 giây) / Khi bị tên lửa chống tăng khóa: thả khói 7 m (mỗi 20 giây) / Khi bị tên lửa… |

#### Dòng unique (45)

| Dòng | Ô | Hiệu ứng |
|---|---|---|
| **Nạp kép** | Vũ khí | **Sử thi:** Loạt từ 3 viên: bắn thêm một viên và +15% sát thương cả loạt; vũ khí 1–2 viên: +15% sát thương mỗi phát. **Huyền thoại:** Loạt từ 3 viên: bắn thêm một viên và +20% sát thương cả loạt; vũ… |
| **Đạn cháy** | Vũ khí | **Sử thi:** Trúng đích gây cháy bằng 18% sát thương trong 4 giây; mục tiêu đang cháy hồi máu chậm một nửa. **Huyền thoại:** Trúng đích gây cháy bằng 25% sát thương trong 4 giây; mục tiêu đang cháy hồ… |
| **Đạn nảy** | Vũ khí | **Sử thi:** Phát trúng nảy sang kẻ địch gần nhất trong 8 m với 35% sát thương (pháo chậm mỗi phát, súng nhanh vài phát một lần). **Huyền thoại:** Phát trúng nảy sang kẻ địch gần nhất trong 10 m với 5… |
| **Đầu đạn chùm** | Vũ khí | **Sử thi:** 2 viên đầu mỗi loạt đạn pháo, rốc-két hoặc bom rải 5 quả bom con nơi chạm đất. **Huyền thoại:** 2 viên đầu mỗi loạt đạn pháo, rốc-két hoặc bom rải 8 quả bom con nơi chạm đất. |
| **Đạn xé giáp** | Vũ khí | **Sử thi:** Trúng đích khiến mục tiêu nhận thêm 3% sát thương từ mọi nguồn, tối đa 5 lớp (pháo chậm cộng nhiều lớp một lần). **Huyền thoại:** Trúng đích khiến mục tiêu nhận thêm 4% sát thương từ mọi… |
| **Loạt mở màn** | Vũ khí | **Sử thi:** Các phát bắn trong 1,5 giây đầu vào mục tiêu mới (ít nhất phát đầu) gây thêm 35% sát thương. **Huyền thoại:** Các phát bắn trong 1,5 giây đầu vào mục tiêu mới (ít nhất phát đầu) gây thêm… |
| **Pháo tích đà** | Vũ khí | **Sử thi:** Mỗi phát trúng liên tiếp cùng mục tiêu thêm 5% sát thương, tối đa 5 lần (pháo chậm lên nhanh hơn). **Huyền thoại:** Mỗi phát trúng liên tiếp cùng mục tiêu thêm 7% sát thương, tối đa 5 lần… |
| **Đao phủ** | Vũ khí | **Sử thi:** Thêm 40% sát thương lên mục tiêu dưới 30% máu. **Huyền thoại:** Thêm 60% sát thương lên mục tiêu dưới 30% máu. |
| **Đầu nổ kép** | Vũ khí | **Sử thi:** Rốc-két và tên lửa xuyên qua APS, giáp phản ứng và khiên, gây thêm 10% lên giáp cấp 3–4. **Huyền thoại:** Rốc-két và tên lửa xuyên qua APS, giáp phản ứng và khiên, gây thêm 15% lên giáp c… |
| **Đạn áp chế** | Vũ khí | **Sử thi:** Trúng đích làm chậm mục tiêu 15% trong 2 giây (một nửa với máy bay). **Huyền thoại:** Trúng đích làm chậm mục tiêu 25% trong 2 giây (một nửa với máy bay). |
| **Hỏa lực chế áp** | Vũ khí | **Sử thi:** Trúng đích làm mục tiêu giảm 10% tốc độ bắn trong 3 giây (lâu hơn với pháo chậm). **Huyền thoại:** Trúng đích làm mục tiêu giảm 15% tốc độ bắn trong 3 giây (lâu hơn với pháo chậm). |
| **Kíp ẩn thân** | Nạp đạn | **Sử thi:** Đứng yên 2 giây: +10% tốc độ bắn. **Huyền thoại:** Đứng yên 2 giây: +15% tốc độ bắn. |
| **Hạ là nạp** | Nạp đạn | **Sử thi:** Mỗi lần hạ địch rút ngắn tối đa 2 giây nạp đạn của pháo chính, nạp một viên nếu hết băng và +25% tốc độ bắn trong một lúc. **Huyền thoại:** Mỗi lần hạ địch rút ngắn tối đa 2 giây nạp đạn… |
| **Phản ứng nhanh** | Nạp đạn | **Sử thi:** Khi trúng đạn: tốc độ bắn ×1,4 trong 4 giây (mỗi 18 giây). **Huyền thoại:** Khi trúng đạn: tốc độ bắn ×1,6 trong 4 giây (mỗi 14 giây). |
| **Buồng quá áp** | Nạp đạn | **Sử thi:** Mỗi phát thứ 5 mạnh hơn 50% và nổ lan 4 m. **Huyền thoại:** Mỗi phát thứ 4 mạnh hơn 50% và nổ lan 4 m. |
| **Thay băng nóng** | Nạp đạn | **Sử thi:** Nạp băng cả khi di chuyển, nhanh hơn 25%. **Huyền thoại:** Nạp băng cả khi di chuyển, nhanh hơn 40%. |
| **Giá súng phòng không** | Nạp đạn | **Sử thi:** Súng máy phụ bắn được máy bay, với 60% sát thương. **Huyền thoại:** Súng máy phụ bắn được máy bay, với 80% sát thương. |
| **Trả thù** | Nạp đạn | **Sử thi:** Đồng minh bị hạ trong 15 m: +15% sát thương trong 5 giây (không cộng dồn). **Huyền thoại:** Đồng minh bị hạ trong 15 m: +20% sát thương trong 5 giây (không cộng dồn). |
| **Khiên Aegis** | Giáp | **Sử thi:** Mỗi 20 giây, một lớp khiên hấp thụ 10% máu tối đa. **Huyền thoại:** Mỗi 16 giây, một lớp khiên hấp thụ 15% máu tối đa. |
| **Bất khuất** | Giáp | **Sử thi:** Mỗi mạng một lần, đòn kết liễu để lại 1 máu và bất tử 1,5 giây. **Huyền thoại:** Mỗi mạng một lần, đòn kết liễu để lại 1 máu và bất tử 2,5 giây. |
| **Liên kết hộ vệ** | Giáp | **Sử thi:** Gánh 15% sát thương thay cho đồng minh xe nhẹ trong 10 m. **Huyền thoại:** Gánh 25% sát thương thay cho đồng minh xe nhẹ trong 10 m. |
| **Vương miện bóng tối** | Giáp | **Sử thi:** Mỗi xe bị hạ trong 25 m: +3% sát thương (5 lần) và hồi 2% máu. **Huyền thoại:** Mỗi xe bị hạ trong 25 m: +4% sát thương (5 lần) và hồi 3% máu. |
| **Giáp thích ứng** | Giáp | **Sử thi:** Mỗi phát trúng một loại sát thương cho 5% kháng loại đó trong 6 giây, cộng dồn 4 lần. **Huyền thoại:** Mỗi phát trúng một loại sát thương cho 6% kháng loại đó trong 6 giây, cộng dồn 4 lần. |
| **Khối giáp phản ứng** | Giáp | **Sử thi:** 3 khối giáp giảm nửa phát nổ lõm (không giảm động năng); hồi lại một khối mỗi 20 giây. **Huyền thoại:** 4 khối giáp giảm nửa phát nổ lõm (không giảm động năng); hồi lại một khối mỗi 15 gi… |
| **Lớp giáp hy sinh** | Giáp | **Sử thi:** 20% máu tối đa đầu tiên mất đi mỗi mạng được giảm một nửa. **Huyền thoại:** 30% máu tối đa đầu tiên mất đi mỗi mạng được giảm một nửa. |
| **Giáp nghiêng** | Giáp | **Sử thi:** Mỗi phát động năng hoặc nổ lõm thứ 6 bị bật ra. **Huyền thoại:** Mỗi phát động năng hoặc nổ lõm thứ 5 bị bật ra. |
| **Neo công thành** | Giáp | **Sử thi:** Đứng yên 3 giây: -15% sát thương nhận và +8% tầm bắn; mất 1 giây để rời đi. **Huyền thoại:** Đứng yên 3 giây: -20% sát thương nhận và +12% tầm bắn; mất 1 giây để rời đi. |
| **Bứt tốc** | Động cơ | **Sử thi:** Khi trúng đạn: tốc độ ×1,6 và bắn nhanh hơn trong 3 giây (mỗi 25 giây). **Huyền thoại:** Khi trúng đạn: tốc độ ×1,8 và bắn nhanh hơn trong 3 giây (mỗi 18 giây). |
| **Bắn rồi chạy** | Động cơ | **Sử thi:** Phát đầu sau khi dừng: +40% sát thương; sau khi bắn, +15% tốc độ trong 2 giây. **Huyền thoại:** Phát đầu sau khi dừng: +60% sát thương; sau khi bắn, +25% tốc độ trong 2 giây. |
| **Triển khai nhanh** | Động cơ | **Sử thi:** 10 giây đầu sau khi vào trận: +40% tốc độ và -20% sát thương nhận. **Huyền thoại:** 15 giây đầu sau khi vào trận: +40% tốc độ và -20% sát thương nhận. |
| **Bình xăng dễ nổ** | Động cơ | **Sử thi:** Khi bị hạ, phát nổ bằng 30% máu trong 8 m, chỉ gây hại cho địch. **Huyền thoại:** Khi bị hạ, phát nổ bằng 45% máu trong 10 m, chỉ gây hại cho địch. |
| **Đốt sau dự phòng** | Động cơ | **Sử thi:** Mỗi mạng một lần khi dưới 40% máu: +50% tốc độ trong 4 giây, kèm mồi nhiệt. **Huyền thoại:** Mỗi mạng một lần khi dưới 40% máu: +70% tốc độ trong 4 giây, kèm mồi nhiệt. |
| **Chặn hậu** | Động cơ | **Sử thi:** Khi di chuyển ra xa địch: nhận ít hơn 15% sát thương. **Huyền thoại:** Khi di chuyển ra xa địch: nhận ít hơn 20% sát thương. |
| **Thợ máy dã chiến** | Sửa chữa | **Sử thi:** Đồng minh trong 12 m khi ngoài giao tranh hồi 0,6% máu mỗi giây. **Huyền thoại:** Đồng minh trong 15 m khi ngoài giao tranh hồi 1,0% máu mỗi giây. |
| **Bộ sửa khẩn cấp** | Sửa chữa | **Sử thi:** Dưới 40% máu, hồi 20% trong 5 giây (mỗi 30 giây). **Huyền thoại:** Dưới 40% máu, hồi 30% trong 5 giây (mỗi 30 giây). |
| **Thợ hàn chiến trường** | Sửa chữa | **Sử thi:** Tự sửa cả khi đang bị bắn, ở mức 40%. **Huyền thoại:** Tự sửa cả khi đang bị bắn, ở mức 60%. |
| **Đội thu hồi** | Sửa chữa | **Sử thi:** Mỗi lần hạ địch hồi 8% máu, đồng minh trong 10 m hồi một nửa. **Huyền thoại:** Mỗi lần hạ địch hồi 12% máu, đồng minh trong 10 m hồi một nửa. |
| **Xe chở đạn** | Sửa chữa | **Sử thi:** Đồng minh trong 12 m nạp băng nhanh hơn 30%, kể cả khi di chuyển. **Huyền thoại:** Đồng minh trong 16 m nạp băng nhanh hơn 50%, kể cả khi di chuyển. |
| **Kiểm soát hư hại** | Sửa chữa | **Sử thi:** Xóa cháy, chậm, choáng và xé giáp, rồi miễn nhiễm 2 giây (mỗi 15 giây). **Huyền thoại:** Xóa cháy, chậm, choáng và xé giáp, rồi miễn nhiễm 2 giây (mỗi 10 giây). |
| **Kính ảnh nhiệt** | Quang học | **Sử thi:** Nhìn xuyên khói tới 60% tầm nhìn. **Huyền thoại:** Nhìn xuyên khói tới 100% tầm nhìn. |
| **Chỉ thị la-de** | Quang học | **Sử thi:** Đánh dấu mục tiêu trúng đạn 4 giây: đồng minh gây thêm 8% và pháo binh bắn tới xa hơn. **Huyền thoại:** Đánh dấu mục tiêu trúng đạn 6 giây: đồng minh gây thêm 12% và pháo binh bắn tới xa… |
| **Chế độ ngụy trang** | Quang học | **Sử thi:** Đứng yên và im lặng 4 giây: ẩn mình ngoài 8 m; phát đầu từ chỗ nấp gây thêm 25%. **Huyền thoại:** Đứng yên và im lặng 3 giây: ẩn mình ngoài 8 m; phát đầu từ chỗ nấp gây thêm 40%. |
| **Radar phản pháo** | Quang học | **Sử thi:** Pháo địch khai hỏa trong 80 m bị lộ 5 giây, và pháo binh gây thêm 15% lên nó. **Huyền thoại:** Pháo địch khai hỏa trong 100 m bị lộ 8 giây, và pháo binh gây thêm 25% lên nó. |
| **Gây nhiễu điện tử** | Quang học | **Sử thi:** Mỗi 15 giây, đạn dẫn đường nhắm vào đồng minh trong 12 m bị trượt trong 2 giây. **Huyền thoại:** Mỗi 12 giây, đạn dẫn đường nhắm vào đồng minh trong 16 m bị trượt trong 3 giây. |
| **Máy tính điều khiển hỏa lực** | Quang học | **Sử thi:** Đạn không dẫn đường đón đầu mục tiêu đang chạy, giảm 50% tản mát với chúng. **Huyền thoại:** Đạn không dẫn đường đón đầu mục tiêu đang chạy, giảm 75% tản mát với chúng. |

#### Module đặc biệt (14)

|  | Module | Hiệu ứng (Sử thi/Huyền thoại) |
|---|---|---|
|  | **Giáp phản ứng nổ** | Nhận ít hơn 55% sát thương nổ lõm (không giảm động năng; đầu nổ kép xuyên qua). |
|  | **Tự sửa chữa** | Hồi 1,8% máu mỗi giây khi vài giây không trúng đạn. |
|  | **Kíp lái kỳ cựu** | +12% sát thương và tốc độ bắn. |
|  | **Ống phóng khói** | Thả màn khói 10 m lần đầu tụt dưới nửa máu. Thả lần nữa khi dưới một phần tư máu. |
|  | **Hệ thống Trophy APS** | Bắn hạ tên lửa, drone và rốc-két bay tới: 2 lượt, mỗi lượt hồi sau 20 giây. |
|  | **Mồi bẫy nhiệt** | Khi bị phóng tên lửa, thả mồi nhiệt trong 4 giây (mỗi 18 giây). |
|  | **Drone hộ tống** | Mỗi 20 giây phóng 2 drone cảm tử vào kẻ địch gần nhất. |
|  | **Đầu nổ EMP** | Khi bị hạ, làm choáng xe mặt đất địch trong 14 m trong 3 giây. |
|  | **Máy rải mìn** | Khi di chuyển, thả một quả mìn mỗi 15 giây, tối đa 3 quả cùng lúc. |
|  | **Kẻ trục lợi chiến tranh** | Mỗi lần hạ địch hoàn thêm 80% CP. |
|  | **Kèn tập hợp** | Đồng minh trong 15 m gây thêm 10% sát thương (không cộng dồn). |
|  | **Vòm Aegis** | Mỗi mạng một lần, khi 3 đồng minh gần đó bị bắn, tất cả bất tử trong 3 giây. |
|  | **Bệ phóng mồi nhử** | Khi bị nhắm bằng tên lửa hoặc đạn pháo, mồi nhử hút chúng đi trong 6 giây (mỗi 25 giây). |
|  | **Pháo kích vệ tinh** | Mỗi 35 giây gọi 5 quả cối nhẹ vào mục tiêu của nó. |

#### Thương hiệu / bộ (13)

| Thương hiệu | Thưởng bộ 2 và bộ 4 |
|---|---|
| **Xưởng Ironclad** | 2: +6% máu · 4: Thành lũy: Đứng yên 2 giây: -15% sát thương nhận, và địch gần đó ưu tiên bắn nó. |
| **Kestrel Dynamics** | 2: +5% tốc độ · 4: Đánh và chạy: +20% tốc độ trong 2 giây sau mỗi phát bắn; đạn không dẫn đường bắn vào nó khi đang chạy +50% tản mát. |
| **Vulcan Arms** | 2: +25% sát thương cháy · 4: Bão lửa: Địch đang cháy nhận thêm 10% sát thương, và khi chết lửa lan sang kẻ địch trong 6 m. |
| **Longbow Ordnance** | 2: +5% tầm bắn · 4: Đòn tầm xa: +15% sát thương lên mục tiêu xa hơn 70% tầm bắn. |
| **Aegis Systems** | 2: -5% sát thương nhận vào · 4: Khiên chia sẻ: Mỗi 25 giây, khiên 12% cho đồng minh yếu nhất trong 12 m. |
| **Stormfront Aviation** | 2: -10% sát thương mảnh · 4: Càn quét: Mỗi loạt thứ 4 bắn hai lần; thả mồi nhiệt mỗi 30 giây. |
| **Hivemind Robotics** | 2: +15% sức mạnh drone, mìn và đơn vị gọi thêm · 4: Bầy đàn: Mỗi lần hạ địch phóng một drone cảm tử vào kẻ địch gần nhất (tối đa một chiếc mỗi 10 giây). |
| **Hậu cần Quartermaster** | 2: +10% lượng hồi máu nhận được · 4: Quyền thu hồi: Hạ địch hoàn thêm 20% CP, và hoàn lại 10% giá khi nó bị hạ. |
| **Spectre Electronics** | 2: +8% tầm nhìn · 4: Lưới bóng ma: +15% sát thương khi trong khói hoặc đang ẩn; tên lửa đầu tiên nhắm vào nó mỗi mạng bị mất khóa. |
| **Hammerfall Munitions** | 2: +8% sát thương lên công trình · 4: Đạn hạng nặng: Mỗi phát thứ 5 gây thêm 100% và nổ lan 4 m (mỗi phát thứ 3 nếu có Buồng quá áp). |
| **Phoenix Recovery** | 2: +10% lượng hồi máu nhận được · 4: Khiên tái sinh: Lượng hồi máu vượt quá máu tối đa thành khiên, tối đa 10% máu, tồn tại 8 giây. |
| **Wolfpack Tactics** | 2: Săn theo bầy: +4% sát thương cho mỗi đồng minh trong 15 m, tối đa 3. · 4: Dồn hỏa lực: Khi từ 3 xe ta trở lên cùng bắn một mục tiêu: +15% tốc độ bắn. |
| **Bulwark Engineering** | 2: +10% máu · 4: Ụ súng dã chiến: Tháp bị phá để lại một ụ súng máy tạm trong 20 giây. (tính số món trên toàn căn cứ) |

Sheet: 02_phuong_tien/Trang_bi — Trang bị: loại cơ bản (38 dòng, 16 cột)

| id | ten_vi | flat | implicit2 | implicit_stat | main_scale | min_rarity | no_subs | penalty | penalty_top |
|---|---|---|---|---|---|---|---|---|---|
| airburst_rounds | Đạn nổ trên không |  |  | DamageVsDrone |  |  |  |  |  |
| applique_steel | Thép ốp tăng cường |  |  | ArmourSide |  |  |  |  |  |
| armoured_tub | Buồng lái bọc giáp |  |  | ArmourAll |  |  |  |  |  |
| belt_feed | Tiếp đạn dây |  |  | SecondaryFireRate |  |  |  |  |  |
| bunker_buster | Đạn phá boong-ke |  |  | DamageVsStructure |  |  |  |  |  |
| camouflage_net | Lưới ngụy trang |  |  | Camouflage |  |  |  |  |  |
| carousel_autoloader | Nạp đạn băng chuyền |  |  | MagazineReload |  |  |  |  |  |
| commanders_periscope | Kính tiềm vọng chỉ huy |  |  | StillVision |  |  |  |  |  |
| composite_addon | Giáp tổng hợp gắn thêm |  |  | ResistShapedCharge |  |  |  |  |  |
| crew_drills | Huấn luyện kíp lái |  |  | Cooldowns |  |  |  |  |  |
| drivetrain | Hệ truyền động |  | TurretRate | TurnRate |  |  |  |  |  |
| extended_ammo_rack | Giá đạn mở rộng |  |  | Magazine |  |  |  |  |  |
| fire_extinguisher | Bình chữa cháy |  |  | StatusDuration |  |  |  |  |  |
| fire_retardant_hull | Thân xe chống cháy |  |  | ResistFire |  |  |  |  |  |
| flanking_rounds | Đạn đánh hông |  |  | DamageFlank |  |  |  |  |  |
| frontal_wedge | Giáp nêm mặt trước |  |  | ResistFrontal |  |  |  |  |  |
| gun_stabiliser | Bộ ổn định pháo |  |  | SpreadMoving |  |  |  |  |  |
| hair_trigger | Cò nhạy |  |  | FireRate |  | 2 |  | Spread | 0;0;-0.1;-0.12;-0.14 |
| he_frag_filler | Thuốc nổ phá mảnh |  |  | Splash |  |  |  |  |  |
| heavy_barrel | Nòng nặng |  |  | Range |  | 2 |  | Speed | 0;0;-0.05;-0.06;-0.07 |
| laser_rangefinder | Máy đo xa la-de |  |  | SpreadLong |  |  |  |  |  |
| laser_warning | Cảnh báo la-de | TRUE |  | LaserWarning |  |  |  |  |  |
| long_barrel | Nòng dài |  |  | Range |  |  |  |  |  |
| monolith_plate | Tấm giáp nguyên khối |  |  | Count | 1.8 | 2 | TRUE | Speed | 0;0;-0.04;-0.05;-0.06 |
| overhead_screen | Mái che chống pháo |  |  | ResistIndirect |  |  |  |  |  |
| overtuned_engine | Động cơ độ quá mức |  |  | Speed |  | 2 |  | Health | 0;0;-0.04;-0.05;-0.06 |
| proximity_fuze | Ngòi nổ cận đích |  |  | DamageVsAir |  |  |  |  |  |
| radar_absorbent_coating | Lớp phủ chống radar |  |  | LockRange |  |  |  |  |  |
| reverse_gearbox | Hộp số lùi |  |  | ReverseSpeed |  |  |  |  |  |
| salvo_rack | Giá phóng loạt |  |  | SalvoInterval |  |  |  |  |  |
| signal_relay | Trạm chuyển tiếp tín hiệu |  | Vision | CaptureRate |  |  |  |  |  |
| slat_cage | Lồng chống rốc-két |  |  | ResistRocket |  |  |  |  |  |
| spall_liner | Lớp lót chống mảnh |  |  | ResistHighExplosive |  |  |  |  |  |
| spare_magazine | Băng đạn dự phòng | TRUE |  | SpareMagazine |  |  |  |  |  |
| toolbox | Hộp dụng cụ |  |  | RegenDelay |  |  |  |  |  |
| transit_gearbox | Hộp số hành quân |  |  | TransitSpeed |  |  |  |  |  |
| tungsten_penetrator | Lõi xuyên vonfram |  |  | Penetration |  |  |  |  |  |
| underbelly_armor | Giáp gầm |  |  | ResistBlast |  |  |  |  |  |

*in 10 / 16 cột; 4 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 02_phuong_tien/Trang_bi_bo — Trang bị: bộ (brand) (13 dòng, 16 cột)

| id | four_piece_arg0 | four_piece_arg1 | four_piece_arg2 | four_piece_arg3 | index | stat | tower_only | two_piece_arg0 | two_piece_arg1 |
|---|---|---|---|---|---|---|---|---|---|
| aegis | SetSharedShield | 0.12 | 25 | 12 | 5 | DamageTaken |  |  |  |
| bulwark | SetBulwarkPost | 20 |  |  | BulwarkBrand | Health | TRUE |  |  |
| hammerfall | SetHeavyRound | 5 | 1 |  | 10 | DamageVsStructure |  |  |  |
| hivemind | SetSwarm | 10 |  |  | 7 | SummonPower |  |  |  |
| ironclad | SetBulwark | 0.15 |  |  | 1 | Health |  |  |  |
| kestrel | SetHitAndRun | 0.2 | 0.5 |  | 2 | Speed |  |  |  |
| longbow | SetDeepStrike | 0.15 |  |  | 4 | Range |  |  |  |
| phoenix | SetPhoenix | 0.1 | 8 |  | 11 | RepairReceived |  |  |  |
| quartermaster | SetSalvageRights | 0.2 | 0.1 |  | 8 | RepairReceived |  |  |  |
| spectre | SetGhostNet | 0.15 |  |  | 9 | Vision |  |  |  |
| stormfront | SetStrafingRun | 4 | 30 |  | 6 | ResistFragmentation |  |  |  |
| vulcan | SetFirestorm | 0.1 | 6 |  | 3 | BurnDamage |  |  |  |
| wolfpack | SetPackFocus | 0.15 |  |  | 12 | Count |  | SetPackHunt | 0.04 |

*in 10 / 16 cột; 3 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 02_phuong_tien/Trang_bi_dac_tinh — Trang bị: đặc tính (45 dòng, 8 cột)

| id | ten_vi | branches | epic | legendary | slot |
|---|---|---|---|---|---|
| AblativeLayer | Lớp giáp hy sinh | Any | 0.2 | 0.3 | Armor |
| AdaptivePlating | Giáp thích ứng | Any | 0.05 | 0.06 | Armor |
| AegisBarrier | Khiên Aegis | Any | 0.1;20 | 0.15;16 | Armor |
| AfterburnerReserve | Đốt sau dự phòng | Flying | 0.5 | 0.7 | Engine |
| AmmoCarrier | Xe chở đạn | Any | 0.3;12 | 0.5;16 | Repair |
| AngledGlacis | Giáp nghiêng | Ground | 6 | 5 | Armor |
| ClusterWarhead | Đầu đạn chùm | Lobs | 5 | 8 | Weapon |
| CombatWelder | Thợ hàn chiến trường | Any | 0.4 | 0.6 | Repair |
| CounterBatteryRadar | Radar phản pháo | Any | 0.15;80;5 | 0.25;100;8 | Optics |
| DamageControl | Kiểm soát hư hại | Any | 15 | 10 | Repair |
| DarkCrown | Vương miện bóng tối | Any | 0.03;0.02 | 0.04;0.03 | Armor |
| EmergencyRepairKit | Bộ sửa khẩn cấp | Any | 0.2 | 0.3 | Repair |
| EwJammer | Gây nhiễu điện tử | Any | 2;15;12 | 3;12;16 | Optics |
| Executioner | Đao phủ | Armed | 0.4 | 0.6 | Weapon |
| FieldMechanics | Thợ máy dã chiến | Any | 0.006;12 | 0.01;15 | Repair |

*15 / 45 dòng đầu: xem sheet 02_phuong_tien/Trang_bi_dac_tinh.*

Sheet: 02_phuong_tien/Trang_bi_mo_dun — Trang bị: mô-đun đặc biệt (14 dòng, 9 cột)

| id | epic | epic2 | legendary | legendary2 | need |
|---|---|---|---|---|---|
| AegisDome | 2 |  | 3 |  | Any |
| AutoRepair | 0.012 |  | 0.018 |  | Any |
| DecoyLauncher | 4 | 35 | 6 | 25 | Ground |
| DroneEscort | 1 | 25 | 2 | 20 | Any |
| EmpPayload | 2 | 10 | 3 | 14 | Any |
| FlareDispenser | 3 | 25 | 4 | 18 | Flying/Flares |
| MineDispenser | 2 | 20 | 3 | 15 | Ground |
| RallyHorn | 0.06 | 12 | 0.1 | 15 | Any |
| ReactiveArmor | 0.4 |  | 0.55 |  | Ground |
| SmokeDischarger | 8 | 0 | 10 | 1 | Ground |
| TrophyAps | 1 | 25 | 2 | 20 | Ground/ApsMount |
| UplinkBarrage | 3 | 45 | 5 | 35 | HitsGround |
| VeteranCrew | 0.08 |  | 0.12 |  | Armed |
| WarProfiteer | 0.5 |  | 0.8 |  | Armed |

Sheet: 02_phuong_tien/Trang_bi_dong_phu — Trang bị: dòng phụ (23 dòng, 7 cột)

| id | slots | values | weight |
|---|---|---|---|
| CaptureRate | Engine;Optics | 0.05;0.08;0.1;0.12 |  |
| Cooldowns | Repair;Optics | 0.03;0.05;0.07;0.09 |  |
| Damage | Loader;Optics | 0.015;0.02;0.03;0.04 |  |
| DamageVsAir | Weapon;Loader;Optics | 0.04;0.05;0.06;0.08 |  |
| DamageVsHeavy | Weapon;Loader;Optics | 0.03;0.04;0.05;0.06 |  |
| DamageVsLight | Weapon;Loader;Optics | 0.03;0.04;0.05;0.06 |  |
| DamageVsStructure | Weapon;Loader | 0.04;0.06;0.08;0.1 |  |
| FireRate | Weapon | 0.015;0.02;0.03;0.04 |  |
| Health | Armor;Repair;Engine | 0.02;0.03;0.04;0.05 |  |
| Magazine | Loader | 0.05;0.08;0.1;0.12 |  |
| MagazineReload | Loader;Repair | 0.04;0.06;0.08;0.1 |  |
| ProjectileSpeed | Weapon;Loader | 0.04;0.06;0.08;0.1 |  |
| Range | Weapon;Optics | 0.02;0.025;0.03;0.04 |  |
| Regen | Repair;Armor | 0.001;0.0015;0.002;0.0025 |  |
| ResistFire | Armor | 0.03;0.04;0.06;0.08 | 0.2 |
| ResistFragmentation | Armor | 0.03;0.04;0.06;0.08 | 0.2 |
| ResistHighExplosive | Armor | 0.03;0.04;0.06;0.08 | 0.2 |
| ResistKinetic | Armor | 0.03;0.04;0.06;0.08 | 0.2 |
| ResistShapedCharge | Armor | 0.03;0.04;0.06;0.08 | 0.2 |
| Speed | Engine;Armor | 0.015;0.02;0.03;0.04 |  |
| Spread | Weapon;Optics | 0.04;0.06;0.08;0.1 |  |
| TurretRate | Engine;Optics | 0.05;0.08;0.1;0.12 |  |
| Vision | Optics;Engine | 0.03;0.04;0.05;0.06 |  |

Sheet: 11_meta_giao_dien/Trang_bi_hang — Trang bị theo độ hiếm (27 dòng, 11 cột)

| id | bang | chi_so | gia_tri | gia_tri_0 | gia_tri_1 | gia_tri_2 | gia_tri_3 | gia_tri_4 |
|---|---|---|---|---|---|---|---|---|
| Cap/0 | Cap | 0 | 0.25 |  |  |  |  |  |
| Cap/1 | Cap | 1 | 0.15 |  |  |  |  |  |
| Cap/2 | Cap | 2 | 0.25 |  |  |  |  |  |
| Cap/3 | Cap | 3 | 0.25 |  |  |  |  |  |
| Cap/4 | Cap | 4 | 0.15 |  |  |  |  |  |
| Cap/5 | Cap | 5 | 0.02 |  |  |  |  |  |
| GoldGuaranteed/0 | GoldGuaranteed | 0 | 0 |  |  |  |  |  |
| GoldGuaranteed/1 | GoldGuaranteed | 1 | 0 |  |  |  |  |  |
| GoldGuaranteed/2 | GoldGuaranteed | 2 | 0.81 |  |  |  |  |  |
| GoldGuaranteed/3 | GoldGuaranteed | 3 | 0.16 |  |  |  |  |  |
| GoldGuaranteed/4 | GoldGuaranteed | 4 | 0.03 |  |  |  |  |  |
| LegendaryGuaranteed/0 | LegendaryGuaranteed | 0 | 0 |  |  |  |  |  |
| LegendaryGuaranteed/1 | LegendaryGuaranteed | 1 | 0 |  |  |  |  |  |
| LegendaryGuaranteed/2 | LegendaryGuaranteed | 2 | 0 |  |  |  |  |  |
| LegendaryGuaranteed/3 | LegendaryGuaranteed | 3 | 0.8 |  |  |  |  |  |
| LegendaryGuaranteed/4 | LegendaryGuaranteed | 4 | 0.2 |  |  |  |  |  |
| LevelCap/0 | LevelCap | 0 | 5 |  |  |  |  |  |
| LevelCap/1 | LevelCap | 1 | 10 |  |  |  |  |  |
| LevelCap/2 | LevelCap | 2 | 15 |  |  |  |  |  |
| LevelCap/3 | LevelCap | 3 | 20 |  |  |  |  |  |
| LevelCap/4 | LevelCap | 4 | 25 |  |  |  |  |  |
| Top/0 | Top | 0 |  | 0.03 | 0.05 | 0.08 | 0.11 | 0.14 |
| Top/1 | Top | 1 |  | 0.03 | 0.05 | 0.08 | 0.11 | 0.14 |
| Top/2 | Top | 2 |  | 0.03 | 0.05 | 0.08 | 0.11 | 0.14 |
| Top/3 | Top | 3 |  | 0.03 | 0.05 | 0.08 | 0.11 | 0.14 |
| Top/4 | Top | 4 |  | 0.02 | 0.035 | 0.05 | 0.065 | 0.08 |
| Top/5 | Top | 5 |  | 0.002 | 0.004 | 0.006 | 0.008 | 0.01 |

## Tham khảo ngoài đời và game

Trạng thái: Đã áp (lượt 10; chỉ dữ liệu trong repo, thiếu nguồn ghi NEED_SOURCE).

Nguồn dữ liệu: 02_phuong_tien/Phuong_tien_tham_chieu; 02_phuong_tien/Phuong_tien_so_sanh_that; 13_tham_chieu_nguon/Nguon_tham_chieu.

### Phuong_tien_tham_chieu

160 dòng. Độ tin cậy: da_kiem_chung 26, uoc_dinh 32, ban_dau_doan 17, NEED_SOURCE 85. Loại: NEED_SOURCE 85, doi_that 75.

- `aa_vehicle` (Pháo cao xạ tự hành): mẫu thật: Flakpanzer Gepard (Oerlikon KDA 35 mm);Stinger / Starstreak; giống: Pháo phòng không tự hành hai nòng 35 mm có radar; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_flakpanzer_gepard, R_unit_sheet, R_machine_brigade_can_bang.
- `ammo_carrier` (Xe tiếp đạn): mẫu thật: M977 HEMTT;KamAZ-5350;M2 Browning 12,7 mm; giống: xe tải hậu cần chở đạn, súng máy trên vòng nóc; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_heavy_expanded_mobility_tactical_t, R_unit_sheet, R_machine_brigade_can_bang.
- `armored_bulldozer` (Xe ủi bọc thép): mẫu thật: IDF Caterpillar D9R; giống: Xe ủi bọc thép chiến đấu; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, D_caterpillar_d9r_specifications, R_unit_sheet, R_machine_brigade_can_bang.
- `armored_car` (Xe bọc thép bánh lốp): mẫu thật: Pandur I 6x6;M242 Bushmaster 25 mm; giống: xe bọc thép 6x6 bánh lộ ngoài, tháp pháo tự động nhỏ; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_steyr_pandur, R_unit_sheet, R_machine_brigade_can_bang.
- `artillery` (Lựu pháo tự hành): mẫu thật: CAESAR 155 mm;M284 155 mm (M109A6/A7); giống: Lựu pháo tự hành bánh lốp 6x6, nòng 155 mm đặt sau sàn xe; độ tin: da_kiem_chung; nguồn: R_unit_refs, R_reference_real, W_wikipedia_m109_howitzer, R_unit_sheet, R_machine_brigade_can_bang.
- `attack_helicopter` (Trực thăng tấn công): mẫu thật: AH-64D Apache Longbow;AGM-114L Hellfire Longbow;Ka-52 Alligator (model thay thế); giống: Trực thăng tấn công hai chỗ ngồi nối tiếp, radar trên trục rô-to; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_boeing_ah_64_apache, R_unit_sheet, R_machine_brigade_can_bang.
- `attack_jet` (Máy bay cường kích): mẫu thật: Su-25 Frogfoot;A-10 Thunderbolt II (model tank_buster);GSh-30-2 30 mm; giống: Máy bay cường kích yểm trợ mặt đất; độ tin: da_kiem_chung; nguồn: R_unit_refs, R_reference_real, W_wikipedia_sukhoi_su_25, R_unit_sheet, R_machine_brigade_can_bang.
- `ballistic_launcher` (Xe phóng tên lửa chiến thuật): mẫu thật: 9K720 Iskander (9M723); giống: Xe phóng tên lửa đạn đạo, dựng đứng tên lửa khi phóng; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_9k720_iskander, R_unit_sheet, R_machine_brigade_can_bang.
- `bmpt` (Xe hỗ trợ tăng): mẫu thật: BMPT Terminator (khung T-72);9M120 Ataka; giống: Xe hỗ trợ xe tăng, hai pháo 30 mm; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_reference_real, R_unit_sheet, R_machine_brigade_can_bang.
- `bunker_vehicle` (Xe công sự triển khai): mẫu thật: xe công binh bánh xích có lưỡi ủi;L7 105 mm;công sự 'hull-down'; game: Red Alert 2: Yuri's Revenge; giống: xe tự đào ụ thành lô cốt; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, R_machine_brigade_can_bang.
- `command_vehicle` (Xe chỉ huy): mẫu thật: M1130 Stryker CV;BTR-80 KShM;LAV-C2; giống: Xe chỉ huy 8x8, cột ăng-ten kính viễn vọng gập; độ tin: da_kiem_chung; nguồn: R_unit_refs, R_reference_real, W_wikipedia_stryker, R_unit_sheet, R_machine_brigade_can_bang.
- `counter_battery_radar` (Xe radar phản pháo): mẫu thật: AN/TPQ-53;Zoopark-1;COBRA; giống: Xe radar phản pháo 6x6; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_reference_real, R_unit_sheet, R_machine_brigade_can_bang.
- `drop_pod` (Khoang đổ bộ): mẫu thật: khoang hồi quyển Soyuz (tên lửa hãm); game: Halo;Warhammer 40,000; giống: khoang thả xe từ quỹ đạo; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_soyuz_spacecraft.
- `elite_aa` (Phòng không tinh nhuệ): mẫu thật: Rheinmetall Skyranger 35 (đạn AHEAD);Gepard (khung gốc); giống: Phòng không tinh nhuệ, đạn nổ trên không AHEAD; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_flakpanzer_gepard.
- `elite_apc` (Xe bọc thép tinh nhuệ): mẫu thật: M2 Bradley / BMP-3 (khung gốc);2A42 30 mm; giống: Xe chiến đấu bộ binh tinh nhuệ; độ tin: da_kiem_chung; nguồn: R_unit_refs, R_reference_real, W_wikipedia_m2_bradley.
- … 60 dòng có tham chiếu nữa: xem sheet 02_phuong_tien/Phuong_tien_tham_chieu.

Nguồn được dùng (tiêu đề như repo ghi; link khi repo có):

- `D_army_recognition_buk_m1_2`: Army Recognition 'Buk-M1-2' (độ tin 2)
- `D_caterpillar_d9r_specifications`: Caterpillar D9R specifications (độ tin 1)
- `D_toyota_hilux_an10_an20_specifications`: Toyota Hilux AN10/AN20 specifications (độ tin 1)
- `R_machine_brigade_can_bang`: Rà soát cân bằng (Machine_Brigade_Can_bang.xlsx) (độ tin 3)
- `R_reference_real`: reference_real.json (kích thước thật, độ tin conf) (độ tin 3)
- `R_unit_refs`: unit_refs.json (tham chiếu ngoài đời / phim / game theo đơn vị) (độ tin 3)
- `R_unit_sheet`: unit_sheet.json (hình dạng, mô tả từ bảng cân bằng) (độ tin 3)
- `R_zu23_technical`: spec dựng lại zu23_technical (prompt 35) (độ tin 3)
- `W_wikipedia_2s25_sprut_sd`: Wikipedia '2S25 Sprut-SD' (độ tin 2)
- `W_wikipedia_2s4_tyulpan`: Wikipedia '2S4 Tyulpan' (độ tin 2)
- `W_wikipedia_9k720_iskander`: Wikipedia '9K720 Iskander' (độ tin 2)
- `W_wikipedia_b1_centauro`: Wikipedia 'B1 Centauro' (độ tin 2)
- `W_wikipedia_baykar_bayraktar_tb2`: Wikipedia 'Baykar Bayraktar TB2' (độ tin 2)
- `W_wikipedia_bm_21_grad`: Wikipedia 'BM-21 Grad' (độ tin 2)
- `W_wikipedia_bm_30_smerch`: Wikipedia 'BM-30 Smerch' (độ tin 2)
- `W_wikipedia_boeing_ah_64_apache`: Wikipedia 'Boeing AH-64 Apache' (độ tin 2)
- `W_wikipedia_boeing_b_52_stratofortress`: Wikipedia 'Boeing B-52 Stratofortress' (độ tin 2)
- `W_wikipedia_boxer_armoured_fighting_vehicle`: Wikipedia 'Boxer (armoured fighting vehicle)' (độ tin 2)
- `W_wikipedia_caesar_self_propelled_howitzer`: Wikipedia 'CAESAR self-propelled howitzer' (độ tin 2)
- `W_wikipedia_flakpanzer_gepard`: Wikipedia 'Flakpanzer Gepard' (độ tin 2)
- `W_wikipedia_general_atomics_mq_9_reaper`: Wikipedia 'General Atomics MQ-9 Reaper' (độ tin 2)
- `W_wikipedia_heavy_expanded_mobility_tactical_t`: Wikipedia 'Heavy Expanded Mobility Tactical Truck' (độ tin 2)
- `W_wikipedia_kamaz_typhoon`: Wikipedia 'KamAZ Typhoon' (độ tin 2)
- `W_wikipedia_kirov_class_battlecruiser`: Wikipedia 'Kirov-class battlecruiser' (độ tin 2)
- `W_wikipedia_kratos_xq_58_valkyrie`: Wikipedia 'Kratos XQ-58 Valkyrie' (độ tin 2)
- `W_wikipedia_lcm_8`: Wikipedia 'LCM-8' (độ tin 2)
- `W_wikipedia_leopard_2`: Wikipedia 'Leopard 2' (độ tin 2)
- `W_wikipedia_lockheed_ac_130`: Wikipedia 'Lockheed AC-130' (độ tin 2)
- `W_wikipedia_lockheed_c_130_hercules`: Wikipedia 'Lockheed C-130 Hercules' (độ tin 2)
- `W_wikipedia_lockheed_martin_f_22_raptor`: Wikipedia 'Lockheed Martin F-22 Raptor' (độ tin 2)
- `W_wikipedia_m109_howitzer`: Wikipedia 'M109 howitzer' (độ tin 2)
- `W_wikipedia_m113_armored_personnel_carrier`: Wikipedia 'M113 armored personnel carrier' (độ tin 2)
- `W_wikipedia_m142_himars`: Wikipedia 'M142 HIMARS' (độ tin 2)
- `W_wikipedia_m151_mutt`: Wikipedia 'M151 MUTT' (độ tin 2)
- `W_wikipedia_m2_bradley`: Wikipedia 'M2 Bradley' (độ tin 2)
- `W_wikipedia_m88_recovery_vehicle`: Wikipedia 'M88 Recovery Vehicle' (độ tin 2)
- `W_wikipedia_md_helicopters_mh_6_little_bird`: Wikipedia 'MD Helicopters MH-6 Little Bird' (độ tin 2)
- `W_wikipedia_mil_mi_24`: Wikipedia 'Mil Mi-24' (độ tin 2)
- `W_wikipedia_northrop_b_2_spirit`: Wikipedia 'Northrop B-2 Spirit' (độ tin 2)
- `W_wikipedia_pt_76`: Wikipedia 'PT-76' (độ tin 2)
- `W_wikipedia_soyuz_spacecraft`: Wikipedia 'Soyuz (spacecraft)' (độ tin 2)
- `W_wikipedia_steyr_pandur`: Wikipedia 'Steyr Pandur' (độ tin 2)
- `W_wikipedia_stryker`: Wikipedia 'Stryker' (độ tin 2)
- `W_wikipedia_sukhoi_su_25`: Wikipedia 'Sukhoi Su-25' (độ tin 2)
- `W_wikipedia_sukhoi_su_27`: Wikipedia 'Sukhoi Su-27' (độ tin 2)
- `W_wikipedia_t_54_t_55`: Wikipedia 'T-54/T-55' (độ tin 2)
- `W_wikipedia_t_72`: Wikipedia 'T-72' (độ tin 2)
- `W_wikipedia_t_90`: Wikipedia 'T-90' (độ tin 2)
- `W_wikipedia_tos_1`: Wikipedia 'TOS-1' (độ tin 2)

Sheet: 02_phuong_tien/Phuong_tien_so_sanh_that — Phương tiện: so sánh với thật (269 dòng, 17 cột)

| id | entity_id | thong_so | don_vi | gia_tri_game | gia_tri_that | ty_le | khoang_min | khoang_max | co_chu_dich |
|---|---|---|---|---|---|---|---|---|---|
| aa_vehicle/cao_m | aa_vehicle | cao_m | m | 2.92 | 3.29 | 0.8875379939209727 | 0.7 | 1.4 | FALSE |
| aa_vehicle/cao_tren_dai | aa_vehicle | cao_tren_dai |  | 0.45341614906832295 | 0.4283854166666667 | 1.0584304026883649 | 0.9 | 1.1 | FALSE |
| aa_vehicle/dai_m | aa_vehicle | dai_m | m | 6.44 | 7.68 | 0.8385416666666667 | 0.7 | 1.4 | FALSE |
| aa_vehicle/rong_m | aa_vehicle | rong_m | m | 3.06 | 3.71 | 0.8247978436657682 | 0.7 | 1.4 | FALSE |
| aa_vehicle/rong_tren_dai | aa_vehicle | rong_tren_dai |  | 0.47515527950310554 | 0.4830729166666667 | 0.9836098508312265 | 0.9 | 1.1 | FALSE |
| aerial_tanker/cao_m | aerial_tanker | cao_m | m | 5.7 | 12.4 | 0.4596774193548387 | 0.7 | 1.4 | TRUE |
| aerial_tanker/cao_tren_dai | aerial_tanker | cao_tren_dai |  | 0.2878787878787879 | 0.2556701030927835 | 1.1259775171065496 | 0.9 | 1.1 | FALSE |
| aerial_tanker/dai_m | aerial_tanker | dai_m | m | 19.8 | 48.5 | 0.40824742268041236 | 0.7 | 1.4 | TRUE |
| aerial_tanker/rong_m | aerial_tanker | rong_m | m | 22.62 | 56.4 | 0.4010638297872341 | 0.7 | 1.4 | TRUE |
| aerial_tanker/rong_tren_dai | aerial_tanker | rong_tren_dai |  | 1.1424242424242423 | 1.1628865979381442 | 0.9824038254889319 | 0.9 | 1.1 | FALSE |
| ammo_carrier/cao_m | ammo_carrier | cao_m | m | 2.46 | 2.84 | 0.8661971830985916 | 0.7 | 1.4 | FALSE |
| ammo_carrier/cao_tren_dai | ammo_carrier | cao_tren_dai |  | 0.29425837320574166 | 0.27925270403146507 | 1.0537350899656313 | 0.9 | 1.1 | FALSE |
| ammo_carrier/dai_m | ammo_carrier | dai_m | m | 8.36 | 10.17 | 0.8220255653883972 | 0.7 | 1.4 | FALSE |
| ammo_carrier/rong_m | ammo_carrier | rong_m | m | 2.02 | 2.44 | 0.8278688524590164 | 0.7 | 1.4 | FALSE |
| ammo_carrier/rong_tren_dai | ammo_carrier | rong_tren_dai |  | 0.24162679425837322 | 0.23992133726647 | 1.0071084006588753 | 0.9 | 1.1 | FALSE |

*15 / 269 dòng đầu: xem sheet 02_phuong_tien/Phuong_tien_so_sanh_that; in 10 / 17 cột; 5 cột khác (và raw_json, nguon): xem sheet.*

## Các sheet khác của file

Mọi sheet chưa in ở mục trên (sheet input_<tên> là bản chép từ file khác, không in lại).

### Doi_mo_man_suy_ra

Trạng thái: Đã áp

Nguồn dữ liệu: 02_phuong_tien/Doi_mo_man_suy_ra.

Sheet: 02_phuong_tien/Doi_mo_man_suy_ra — Đội mở màn: suy ra (23 dòng, 7 cột)

| id | base_cp_uoc_tinh | base_cp_uoc_tinh_game | tran_ngan_sach_ty_le | phan_tram_cp_khoi_dau |
|---|---|---|---|---|
| commander.adler | 5.0 | 5 | 0.6 | NEED_CODE_CHECK |
| commander.brandt | 10.0 | 10 | 0.6 | NEED_CODE_CHECK |
| commander.brenn | 0.0 | 0 | 0.6 | NEED_CODE_CHECK |
| commander.dahl | 6.0 | 6 | 0.6 | NEED_CODE_CHECK |
| commander.kade | 10.0 | 10 | 0.6 | NEED_CODE_CHECK |
| commander.kerr | 9.0 | 9 | 0.6 | NEED_CODE_CHECK |
| commander.lind | 10.0 | 10 | 0.6 | NEED_CODE_CHECK |
| commander.mendez | 8.0 | 8 | 0.6 | NEED_CODE_CHECK |
| commander.okoye | 0.0 | 0 | 0.6 | NEED_CODE_CHECK |
| commander.quist | 12.0 | 12 | 0.6 | NEED_CODE_CHECK |
| commander.reyes | 8.0 | 8 | 0.6 | NEED_CODE_CHECK |
| commander.reyn | 8.0 | 8 | 0.6 | NEED_CODE_CHECK |
| commander.varro | 6.0 | 6 | 0.6 | NEED_CODE_CHECK |
| commander.venn | 9.0 | 9 | 0.6 | NEED_CODE_CHECK |
| general.aurel | 7.0 | 7 | 0.6 | NEED_CODE_CHECK |
| general.default | 5.0 | 5 | 0.6 | NEED_CODE_CHECK |
| general.kessler | 9.0 | 9 | 0.6 | NEED_CODE_CHECK |
| general.orlov | 8.0 | 8 | 0.6 | NEED_CODE_CHECK |
| general.sen | 6.0 | 6 | 0.6 | NEED_CODE_CHECK |
| general.thorne | 8.0 | 8 | 0.6 | NEED_CODE_CHECK |
| general.varga | 3.0 | 3 | 0.6 | NEED_CODE_CHECK |
| general.venn | 6.0 | 6 | 0.6 | NEED_CODE_CHECK |
| general.wolff | 6.0 | 6 | 0.6 | NEED_CODE_CHECK |

### Doi_mo_man_vai_tro

Trạng thái: Đã áp

Nguồn dữ liệu: 02_phuong_tien/Doi_mo_man_vai_tro.

Sheet: 02_phuong_tien/Doi_mo_man_vai_tro — Đội mở màn: vai trò (19 dòng, 7 cột)

| id | ung_vien | cp_toi_da | re_nhat | re_nhat_cp |
|---|---|---|---|---|
| artillery | mortar_carrier;sp_mortar;wheeled_howitzer;artillery;auto_lo… |  | mortar_carrier | 4 |
| bunker | bunker_vehicle |  | bunker_vehicle | 7 |
| cheap4 |  | 4 | scout_jeep | 2 |
| drone | fpv_carrier;fibre_fpv_carrier;lancet_truck;ground_drone_car… |  | ground_drone_carrier | 6 |
| engineer | engineer_vehicle;demolition_line_vehicle;bridging_vehicle |  | engineer_vehicle | 3 |
| fortify | bunker_vehicle;siege_tank |  | bunker_vehicle | 7 |
| fpv | fpv_carrier;fibre_fpv_carrier |  | fpv_carrier | 7 |
| heavy | heavy_tank;twin_tank;armored_bulldozer;titan_tank;bunker_ve… |  | bunker_vehicle | 7 |
| heli | attack_helicopter;light_attack_heli;scout_heli;gunship_heli |  | scout_heli | 6 |
| light | armored_car;rocket_technical;recoilless_jeep;zu23_technical… |  | armored_car | 3 |
| light_tank | light_tank;airborne_light_tank |  | light_tank | 3 |
| mbt | main_battle_tank;next_gen_tank;twin_tank;turtle_tank |  | main_battle_tank | 8 |
| mine_layer | mine_layer;mine_rocket_truck |  | mine_layer | 6 |
| radar_scout | radar_scout;radar_support_vehicle;counter_battery_radar |  | radar_scout | 4 |
| repair | mobile_repair_vehicle;ammo_carrier |  | ammo_carrier | 4 |
| scout | scout_jeep;radar_scout;amphib_light_vehicle |  | scout_jeep | 2 |
| scout_heli | scout_heli;light_attack_heli |  | scout_heli | 6 |
| tank | light_tank;main_battle_tank;next_gen_tank;turtle_tank;twin_… |  | light_tank | 3 |
| wheeled | armored_car;wheeled_gun;ifv |  | armored_car | 3 |

### Xe_tham_chieu

Trạng thái: Đã áp

Nguồn dữ liệu: 02_phuong_tien/Xe_tham_chieu.

Sheet: 02_phuong_tien/Xe_tham_chieu — Xe tham chiếu (6 dòng, 10 cột)

| id | ten_vi_spec | don_vi_id | toc_do_m_s | mau_trong_tran_hp | giap_noc | cong_trinh |
|---|---|---|---|---|---|---|
| armored_car | Xe bọc thép bánh lốp | armored_car | 11.5 | 660.0 | 0 | FALSE |
| gun_turret | Tháp vừa (pháo) | gun_turret | 0 | 3960.0 | 3 | TRUE |
| heavy_tank | Tăng hạng nặng | heavy_tank | 4.2 | 4470.4 | 2 | FALSE |
| ifv | Xe chiến đấu bộ binh | ifv | 8 | 1370.6 | 0 | FALSE |
| main_battle_tank | Tăng chủ lực | main_battle_tank | 6.5 | 2310.0 | 1 | FALSE |
| xe_cham_tham_chieu | xe chậm tham chiếu của vòng cảnh báo |  | 4.5 |  |  |  |
