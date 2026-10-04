# 06_ban_do — Bản đồ

Bản đồ, bản đồ gốc, biome, thời tiết, địa danh, ray, vật thể, ngân sách thực thể.

Gói cân bằng Machine Brigade, commit d48c7e2f, ngày 2026-10-04. Số liệu đầy đủ ở 06_ban_do.xlsx; file này chỉ nêu luật, giải thích, lý do thiết kế, tham khảo và bảng nhỏ (tối đa 20 dòng, bảng lớn: xem sheet).

## Biển, hộ tống, bản đồ dài, roster mới và đòn lớn

### Lighthouse Bay và hải chiến

- **Lighthouse Bay:** bờ biển đá, 2 vịnh có bãi và cầu tàu, hải đăng trên mũi đất (giữ nó thì thấy hạm đội), 2 trận địa pháo bờ biển chiếm được (chỉ bắn tàu), làng chài và pháo đài cũ. Biển chiếm 36% map, 3 tuyến biển. Có bản Giữ cứ điểm, Sinh tồn, Công thành và bản dài.
- **Tàu chạy trên tuyến biển:** xe tăng chỉ bắn tới tuyến gần từ đầu cầu tàu và mũi đất; xe săn tăng tầm trung (38–42 m) bắn được từ sườn đá.
- **Leviathan (Kessler):** 9 bộ phận, giáp hông cấp 4, boong cấp 2; 3 pha: loạt pháo có cảnh báo, tên lửa hành trình, đổ tăng, trực thăng và gọi jet; pha 3 chạy ra biển theo đồng hồ, thoát được thì thua nhiệm vụ. Chết thì nghiêng, gãy đôi và chìm.
- **Hạm đội:** 2 tàu hộ vệ (CIWS che Leviathan), 3 xuồng tên lửa đánh đầu cầu tàu, tàu đổ bộ.
- **Chiến dịch và chế độ:** nhiệm vụ 4-11 "Leviathan" cuối chương 4 (mở nhánh Pháo bờ biển tầm xa của Pháo đài hạng nặng); Săn trùm tự chuyển sang Lighthouse Bay cho Leviathan rồi quay lại, mang theo quân, CP và đồng hồ; Tác chiến có mutator Bão biển và Hạm đội.

### Hộ tống cho mọi boss

Mỗi boss mang một nhóm đi cùng và thêm một nhóm ở mỗi lần đổi pha; số hộ tống còn sống tối đa theo độ khó: Easy 5, Normal 7, Hard 8, VeryHard 9, Heroic 9, Iron 9 (Săn trùm ít hơn). Mỗi nhóm có một xe phụ trợ (sửa boss, gây nhiễu tên lửa ta, phòng không che boss, đánh dấu quân ta) nên người chơi phải chọn đánh boss hay hộ tống trước. Hộ tống không rời boss quá 28 m, hạ được thì thưởng CP, có dấu cam, và thanh máu boss đếm số hộ tống.

| Boss | Đi cùng | Khi đổi pha |
|---|---|---|
| Juggernaut · Đoàn tàu bọc thép | Xe bọc thép bánh lốp, Xe bọc thép bánh lốp, Pháo cao xạ tự hành (phòng không che boss), Xe bọc thép bánh lốp (đánh dấu quân ta) | Tăng nhẹ lội nước, Tăng nhẹ lội nước, Xe công binh (sửa boss) |
| Tempest · Behemoth pháo điện từ | Tăng chủ lực, Xe gây nhiễu điện tử (gây nhiễu tên lửa ta), Xe gây nhiễu điện tử (gây nhiễu tên lửa ta), Xe tên lửa phòng không tầm trung (phòng không che boss) | Xe gây nhiễu điện tử (gây nhiễu tên lửa ta), Xe gây nhiễu điện tử (gây nhiễu tên lửa ta) |
| Behemoth · Quái vật thép | Tăng chủ lực, Tăng chủ lực, Tăng hạng nặng, Pháo cao xạ tự hành (phòng không che boss) | Tăng hạng nặng ★, Xe công binh (sửa boss) |
| Inferno · Behemoth phun lửa | Tăng phun lửa, Tăng phun lửa, Pháo cao xạ tự hành (phòng không che boss), Xe gây nhiễu điện tử (thả khói) | Tăng phun lửa, Tăng phun lửa, Xe công binh (sửa boss) |
| Harpy · Trực thăng khổng lồ | Trực thăng tấn công, Trực thăng tấn công, Tiêm kích (phòng không che boss), Trực thăng trinh sát vũ trang (đánh dấu quân ta) | Trực thăng trinh sát vũ trang (đánh dấu quân ta) |
| Jötunn · Pháo đài di động | Tăng hạng nặng, Tăng hạng nặng, Xe tên lửa phòng không tầm trung (phòng không che boss), Xe công binh (sửa boss) | Xe công binh (sửa boss) |
| Bastion · Pháo đài | Pháo chống tăng tự hành, Pháo chống tăng tự hành, Tăng chủ lực, Xe phòng không pháo – tên lửa (phòng không che boss) | Tăng hạng nặng, Xe tên lửa phòng không tầm trung (phòng không che boss), Xe công binh (sửa boss) |
| Matriarch · Tàu mẹ drone | UAV tấn công, UAV tấn công, Tiêm kích (phòng không che boss), UAV trinh sát (đánh dấu quân ta) | Trực thăng trinh sát vũ trang (đánh dấu quân ta) |
| Icarus · Phi thuyền quỹ đạo | Tăng hạng nặng tinh nhuệ, Grad tinh nhuệ, UAV trinh sát (đánh dấu quân ta), Tiêm kích (phòng không che boss), Tiêm kích (phòng không che boss) | Xe phóng drone FPV tinh nhuệ, Xe gây nhiễu điện tử (gây nhiễu tên lửa ta) / Trực thăng tinh nhuệ, Xe công binh (sửa boss) |
| Nemesis · Đoàn tàu tên lửa | Xe chiến đấu bộ binh, Xe chiến đấu bộ binh, Xe tên lửa phòng không tầm trung (phòng không che boss), Trực thăng trinh sát vũ trang (đánh dấu quân ta) | Xe chiến đấu bộ binh, Xe chiến đấu bộ binh, Xe gây nhiễu điện tử (thả khói) |
| Tartarus · Máy khoan |  | Xe chiến đấu bộ binh, Pháo cao xạ tự hành (phòng không che boss), Xe công binh (sửa boss) |
| Roc · Khí cầu chỉ huy | Tiêm kích (phòng không che boss), Tiêm kích (phòng không che boss), Tiêm kích (phòng không che boss) | Trực thăng tấn công, Trực thăng trinh sát vũ trang (đánh dấu quân ta) |
| Charybdis · Tàu đệm khí đổ bộ | Xuồng đệm khí hộ tống, Xuồng đệm khí hộ tống, Pháo cao xạ tự hành (phòng không che boss), Xuồng đệm khí hộ tống (đánh dấu quân ta) | Xuồng đệm khí hộ tống (đánh dấu quân ta) |

### Bản đồ dài và căn cứ nhiều lớp

- Công thành, Phòng thủ, Vô tận và Pháo đài tuần chơi trên bản dài: 300 m ngang, 480 m dọc theo hướng tấn công (đủ cho 20 map có bản công thành, cộng Lighthouse Bay); các chế độ khác giữ map 300 × 300 m.
- Căn cứ nhiều lớp: vùng đệm (răng rồng, hào, dây thép gai, 1–4 ụ bắn), trạm tiền tiêu và 8 cứ điểm, tường ngoài có cổng chính và 2 cửa phụ, sân trong, thành trong, rồi HQ. Quân phòng thủ thả xuống trong thành; quân tấn công thả dù xa dần lên sau mỗi vòng tường bị phá.
- Ô theo cấp HQ từ 4/1/0/1 (nhỏ/vừa/lớn/tiện ích) tới 8/5/3/4; nhãn ô mới: cổng ngoài, tường ngoài, sân trong, tường trong. Một loadout dùng cho cả trại và căn cứ dài: căn cứ dài chưa chỉnh thì mượn tháp của trại.
- Camera nhìn về phía tây trên map dài (zoom mặc định 21, xa nhất 50); bản đồ nhỏ giữ hình chữ nhật.
- Tìm đường: 150 × 240 ô, 1,9 MB; một đường hết chiều dài mất 5–6 ms trên máy bàn, khoảng 35 ms trên điện thoại (đo lại ở phase kiểm tra).

### Đơn vị mới và rà soát roster

- **Mới:** tiêm kích tàng hình (14 CP), drone yểm trợ (6 CP, bay theo máy bay có người lái và hút tên lửa bắn vào chúng), xe tăng laser (10 CP, tia mạnh dần ×0,3 → ×2 trong 6 giây), xe mang khiên (7 CP) và tháp khiên (ô lớn), xe lô cốt (6 CP, đứng yên 3 giây thì đào hầm: giáp trước dày hơn, tầm +30%), máy bay mẹ thả 8 drone FPV (8 CP), tháp tiếp sóng CP (ô nhỏ, tối đa 2 mỗi căn cứ). Giá đo bằng bộ đo giá trị thực chiến.
- **Gộp:** A-10 vào Cường kích (model Su-25, cả hai bộ vũ khí và 2 Kh-29, 15 CP); Ka-52 vào Trực thăng tấn công (giữ Hellfire tầm 55 m và Stinger, 11 CP); xe ATGM vào xe phóng drone FPV; công binh phá mìn vào Công binh; ụ súng vào tháp pháo. Model cũ giữ làm mẫu phụ.
- **Tăng hai nòng và tăng hạng nặng:** tăng hai nòng bắn 2 phát 120 mm một lượt, nạp 7 giây, hạ xe tăng nhanh nhất (37,9 s); tăng hạng nặng đổi sang đạn nổ khi bắn công trình và xe nhẹ, 12 CP, sống dai và phá công trình tốt nhất theo CP.
- **Save:** giữ hạng cao hơn, hoàn xu và bản thiết kế của thẻ hạng thấp; Ka-52 đã mua được hoàn 3.500 xu; ụ súng trong loadout thành tháp pháo.

### Đòn lớn của mọi boss

Mỗi boss có một đòn lớn lấy từ cùng một hệ dữ liệu (mẫu hình dạng + tham số). Đòn đầu tiên khoảng 30 giây sau khi boss xuất hiện; luôn có cảnh báo trên mặt đất; phá bộ phận mang đòn trong lúc cảnh báo thì đòn yếu đi hoặc bị hủy; quân ta biết né khỏi vùng cảnh báo. Theo độ khó: Easy sát thương ×1, hồi ×1.2, cảnh báo +1 s; Normal sát thương ×1, hồi ×1; Hard sát thương ×1, hồi ×0.9; VeryHard sát thương ×1, hồi ×0.8; Heroic sát thương ×1, hồi ×0.8; Iron sát thương ×1, hồi ×0.8.

Bộ phận mới: bệ dựng tên lửa của Doomsday Train, khoang bom của Hive Carrier và của Khí cầu chỉ huy.

Sheet 06_ban_do/Ban_do_bien_lan — Biển: làn tàu (9 dòng, 9 cột)

| id | ban_do_id | thu_tu | end | id_goc | patrol | w |
|---|---|---|---|---|---|---|
| lighthousebay_conquest/far | lighthousebay_conquest | 2 | 88.1 | far | 76.0 | 120.0 |
| lighthousebay_conquest/mid | lighthousebay_conquest | 1 | 102.1 | mid | 82.0 | 106.0 |
| lighthousebay_conquest/near | lighthousebay_conquest | 0 | 116.1 | near | 88.0 | 92.0 |
| lighthousebay_sandbox/far | lighthousebay_sandbox | 2 | 88.1 | far | 76.0 | 120.0 |
| lighthousebay_sandbox/mid | lighthousebay_sandbox | 1 | 102.1 | mid | 82.0 | 106.0 |
| lighthousebay_sandbox/near | lighthousebay_sandbox | 0 | 116.1 | near | 88.0 | 92.0 |
| lighthousebay_siege/far | lighthousebay_siege | 2 | 88.1 | far | 76.0 | 120.0 |
| lighthousebay_siege/mid | lighthousebay_siege | 1 | 102.1 | mid | 82.0 | 106.0 |
| lighthousebay_siege/near | lighthousebay_siege | 0 | 116.1 | near | 88.0 | 92.0 |

Sheet 06_ban_do/Ban_do_bien_phao — Biển: khẩu đội bờ (6 dòng, 9 cột)

| id | ban_do_id | thu_tu | heading_deg | id_goc | x_m | z_m |
|---|---|---|---|---|---|---|
| lighthousebay_conquest/battery_e | lighthousebay_conquest | 1 | 135 | battery_e | 84.85 | 62.23 |
| lighthousebay_conquest/battery_w | lighthousebay_conquest | 0 | 135 | battery_w | -62.23 | -84.85 |
| lighthousebay_sandbox/battery_e | lighthousebay_sandbox | 1 | 135 | battery_e | 84.85 | 62.23 |
| lighthousebay_sandbox/battery_w | lighthousebay_sandbox | 0 | 135 | battery_w | -62.23 | -84.85 |
| lighthousebay_siege/battery_e | lighthousebay_siege | 1 | 135 | battery_e | 84.85 | 62.23 |
| lighthousebay_siege/battery_w | lighthousebay_siege | 0 | 135 | battery_w | -62.23 | -84.85 |

Sheet 06_ban_do/Ban_do_bien_do_bo — Biển: điểm đổ bộ (12 dòng, 8 cột)

| id | ban_do_id | thu_tu | inland | x_m | z_m |
|---|---|---|---|---|---|
| lighthousebay_conquest/0 | lighthousebay_conquest | 0 | -42.31;-59.51 | -34.89 | -66.94 |
| lighthousebay_conquest/1 | lighthousebay_conquest | 1 | -49.15;-72.47 | -41.72 | -79.9 |
| lighthousebay_conquest/2 | lighthousebay_conquest | 2 | 59.51;42.31 | 66.94 | 34.89 |
| lighthousebay_conquest/3 | lighthousebay_conquest | 3 | 72.47;49.15 | 79.9 | 41.72 |
| lighthousebay_sandbox/0 | lighthousebay_sandbox | 0 | -42.31;-59.51 | -34.89 | -66.94 |
| lighthousebay_sandbox/1 | lighthousebay_sandbox | 1 | -49.15;-72.47 | -41.72 | -79.9 |
| lighthousebay_sandbox/2 | lighthousebay_sandbox | 2 | 59.51;42.31 | 66.94 | 34.89 |
| lighthousebay_sandbox/3 | lighthousebay_sandbox | 3 | 72.47;49.15 | 79.9 | 41.72 |
| lighthousebay_siege/0 | lighthousebay_siege | 0 | -42.31;-59.51 | -34.89 | -66.94 |
| lighthousebay_siege/1 | lighthousebay_siege | 1 | -49.15;-72.47 | -41.72 | -79.9 |
| lighthousebay_siege/2 | lighthousebay_siege | 2 | 59.51;42.31 | 66.94 | 34.89 |
| lighthousebay_siege/3 | lighthousebay_siege | 3 | 72.47;49.15 | 79.9 | 41.72 |

Bảng đầy đủ: xem sheet `Ban_do_tuyen_bien` (87 dòng).

## Bản đồ

25 chiến trường 300 × 300 m, cộng 25 bản dài 300 × 480 m (phần 7b) (8 bản đồ mới: Stormbeach, Hollow Dam, Veyra, Helion Launch Complex, Salt Flats, Border Crossing, Mirewood, Coral Keys), đường viền không đều; phần ngoài viền vẫn được dựng như bản đồ (nhà, rừng, đá) chỉ để trang trí, ranh giới là đường đứt nét. Mỗi trại có sở chỉ huy và ô tháp nhỏ/vừa/lớn/tiện ích; mỗi cứ điểm có tiền đồn. Phiên bản công thành đặt pháo đài chiếm 45% bản đồ ở đông bắc (phần 7).

### Ashfield · temperate

Thị trấn · Ôn đới

### Dunebreak · desert

Lọc dầu · Sa mạc

### Frostpeak · snow

Làng núi · Tuyết

### Ironport · harbor

Cảng · Công nghiệp

### Red Rock · desert

Hẻm núi · Sa mạc

### Whiteout Pass · snow

Đèo rừng · Tuyết

### Greenvale · temperate

Đồng quê · Ôn đới

### Rust Yard · harbor

Khu công nghiệp · Đổ nát

### Emberridge · volcanic

Đồng dung nham · Núi lửa

### Jungle Pass · jungle

Đền cổ · Rừng nhiệt đới

### Skyhold · temperate

Sân bay quân sự · Ôn đới

### Metro City · urban

Trung tâm · Đô thị

### Stormbeach · temperate

Bãi biển và vách đá · Bờ biển

### Hollow Dam · temperate

Đập và hẻm sông · Ôn đới

### Veyra · urban

Khu chính phủ · Đô thị

### Helion Launch Complex · desert

Tổ hợp phóng · Sa mạc

### Salt Flats · desert

Đồng muối trống trải · Sa mạc

### Border Crossing · temperate

Vượt sông · Ôn đới

### Mirewood · jungle

Đường đắp · Rừng nhiệt đới

### Coral Keys · desert

Đảo và cầu · Nhiệt đới

### Beacon Bay · temperate

Bờ biển và tuyến biển · Ôn đới

### Deepcut Mine · desert

Hố mỏ bậc thang · Sa mạc

### Skygate Array · snow

Sân bay vũ trụ · Tuyết

### Foundry · urban

Xưởng xe tăng · Công nghiệp

### Veyra Old Quarter · urban

Phố cổ · Đô thị

### Bốn vùng, kiểu cạnh, địa hình, địa danh, đường ray, tuyến biển

#### Bốn vùng của bản đồ

| Vùng | Ở đâu | Nội dung | Lối chơi |
|---|---|---|---|
| 1. Vùng chơi | hình chữ nhật của bản đồ | navmesh, cứ điểm, căn cứ, tháp, chỗ nấp, vật chặn tầm nhìn, tag địa hình | Có |
| 2. Dải viền | 12–20 m ngoài mép (theo bản đồ) | chuyển cảnh: gờ đất, mương, vách, bãi, mép nước, góc dựng sẵn | Không |
| 3. Vành ngoài | 120 m quanh bản vuông; 73 / 128 m bên / đầu bản dài | trang trí instancing theo seed cố định; nửa xa dùng HLOD | Không; không collider, không chặn tầm nhìn |
| 4. Chân trời | ngoài vành | dãy núi thô, biển xa, đảo mờ, tàu xa, mặt đất chân trời, sương | Không |

Bề rộng vành = khung nhìn camera lớn nhất (trực giao, nghiêng 52°, zoom xa nhất 42 / 50, tỷ lệ 4:3, 16:9, 20:9, camera không xoay) + 15 %: tầm với 103.7 m (vuông), 63.5 / 111.1 m (dài).

#### Kiểu cạnh (edgeType) theo chiến trường

Phía BIỂN: mặt nước tới chân trời, sóng, bóng tàu xa, đảo mờ, không nhà, rừng, đất; bờ chuyển tiếp theo kiểu bờ (bãi: dải sóng vỗ; vách: đá trụ; cầu cảng: tường kè, cần cẩu, container). SÔNG chảy tiếp ra ngoài; VÁCH dựng thành vách đá; ĐÔ THỊ là thành phố của theme. Góc giao giữa hai kiểu dùng 10 tài sản góc dựng sẵn. Đường bộ, ray (tới cửa hầm), sông, bờ biển và tuyến biển (phao) kéo dài ra vành ngoài.

Bảng 25 dòng: số liệu đầy đủ ở các sheet của mục này trong file xlsx cùng tên.

Tài sản góc (số lần trong 100 file): outer_land 298, corner_land_cliff 146, outer_urban 64, bank_land_river 60, corner_land_sea 38, outer_sea 16, embankment_urban_river 14, outer_land_sea 12, outer_cliff 7, outer_river 3.

#### Tag địa hình

| Tag | Tên | Tác dụng | Phủ (cả 100 file) |
|---|---|---|---|
| ROAD | Đường | tốc độ +20 % | 11,6 % |
| ROUGH | Gồ ghề | tốc độ −15 % (đô thị, đổ nát, sỏi đá; chỗ nấp vẫn do nhà / vật thể) | 6,7 % |
| FOREST | Rừng | tốc độ −25 %; tầm nhìn của địch lên xe trong rừng ×0,7 | 4,2 % |
| SHALLOW_WATER | Nước nông | xe thường −50 %; xe lội nước và đệm khí không chậm | 0,8 % |

Chi phí đường tĩnh theo tag (không đổi theo tick). DEEP_FORD để sau: bộ tìm đường chưa có chi phí theo loại xe.

#### Địa danh

Địa danh không có vật thể trên bản đồ được dựng bằng mô hình trang trí (không collider) ở chỗ trống gần nhất, tránh cứ điểm, đường, ray, cổng.

Bảng 25 dòng: số liệu đầy đủ ở các sheet của mục này trong file xlsx cùng tên.

#### Đường ray (RailSpline)

Lớp riêng, không phải navmesh: từ cửa hầm ngoài bản đồ qua dải viền, cổng vào, tới điểm dừng; Juggernaut, Nemesis, Gungnir và tàu chi viện Công thành chạy trên ray. Chỗ cắt đường bộ: MỞ → CẢNH BÁO (≥ 4 s) → ĐÓNG → TÀU QUA → MỞ.

#### Tuyến tàu biển (SeaRouteGraph)

Tàu lớn đi trên đồ thị tuyến (đoạn, nút, vịnh tránh), giữ đoạn hiện tại và đoạn kế, khoảng cách tối thiểu nửa thân tàu này + nửa thân tàu trước + 10 m, ưu tiên cố định.

Sheet 06_ban_do/Ban_do_biome — Biome (8 dòng, 19 cột)

| id | band | band_set | berms | ditches | dry_beds | edge_band | far | far_set | far_tree |
|---|---|---|---|---|---|---|---|---|---|
| coast | 100 | dress_coast_dune_grass;dress_coast_dune_grass;dress_coast_d… | 4 | 1 | 1 | 14 | 20 | dress_temperate_tree_far | dress_temperate_tree_far |
| desert | 70 | dress_desert_scrub;dress_desert_scrub;dress_desert_scrub;dr… | 4 | 0 | 3 | 20 | 18 | dress_desert_far |  |
| harbor | 90 | dress_harbor_pallets;dress_harbor_pallets;dress_harbor_drum… | 5 | 3 | 0 | 14 | 12 | dress_harbor_shed_far | dress_temperate_tree_far |
| jungle | 150 | dress_jungle_palm_small;dress_jungle_palm_small;dress_jungl… | 3 | 2 | 2 | 14 | 45 | dress_jungle_tree_far | dress_jungle_tree_far |
| snow | 100 | dress_snow_drift;dress_snow_drift;dress_snow_drift;dress_sn… | 4 | 0 | 1 | 18 | 35 | dress_snow_pine_far | dress_snow_pine_far |
| temperate | 120 | dress_temperate_shrub;dress_temperate_shrub;dress_temperate… | 6 | 3 | 1 | 16 | 40 | dress_temperate_tree_far | dress_temperate_tree_far |
| urban | 80 | dress_urban_rubble;dress_urban_rubble;dress_urban_planter;d… | 4 | 2 | 0 | 12 | 6 | dress_urban_block_far | dress_temperate_tree_far |
| volcanic | 70 | dress_volcanic_ash_rocks;dress_volcanic_ash_rocks;dress_vol… | 3 | 0 | 2 | 16 | 18 | dress_volcanic_far | dress_volcanic_snag |

*In 10 / 19 cột; 7 cột khác: xem sheet.*

Sheet 06_ban_do/Thoi_tiet — Thời tiết (8 dòng, 5 cột)

| id | he_so_tam_nhin | so_nhiem_vu |
|---|---|---|
| Clear | 1.0 | 40 |
| Fog | 0.7 | 37 |
| Night | 0.75 | 42 |
| Overcast | 1.0 | 27 |
| Rain | 0.9 | 19 |
| Sandstorm | 0.75 | 8 |
| Snow | 0.85 | 7 |
| Storm | 0.8 | 13 |

Bảng đầy đủ: xem sheet `Ban_do` (100 dòng), `Ban_do_goc` (25 dòng), `Ban_do_dia_danh` (300 dòng), `Ban_do_rail` (23 dòng), `Ban_do_tag_dia_hinh` (38788 dòng, bulk.zip), `Ban_do_cong_vao` (3200 dòng), `Ban_do_trung_lap` (250 dòng), `Vat_the_loai` (122 dòng).

## Tham khảo ngoài đời và game

Thông số ngoài đời lấy từ nguồn trong repo (sheet Nguon_tham_chieu của 08_tham_chieu); chỗ chưa có nguồn ghi NEED_SOURCE, không điền từ trí nhớ.

### Ban_do_tham_chieu

33 dòng. Độ tin cậy: da_kiem_chung 0, uoc_dinh 0, ban_dau_doan 0, NEED_SOURCE 33. Loại: NEED_SOURCE 33.

- Chưa dòng nào có tham chiếu trong repo.

## Các sheet của file

Mọi sheet, số dòng và ý nghĩa cột nằm trong 00_index.xlsx (Muc_luc_sheet, Schema). Sheet `input_<tên>` là bản chép của một sheet nguồn để công thức Excel đọc cùng file; sửa ở sheet nguồn, không sửa bản chép.

- `Ban_do` (100 dòng): Bản đồ — Mỗi file bản đồ một dòng (25 bản đồ x 4 biến thể conquest / long / sandbox / siege): kích thước, chủ đề, viền, ô địa hình, đường biên, vòng công thàn…
- `Ban_do_bai_tha` (200 dòng): Bản đồ: bãi thả — teams[]: bãi thả quân của mỗi đội
- `Ban_do_cu_diem` (150 dòng): Bản đồ: cứ điểm — points[]: cứ điểm (tên, vị trí, bán kính)
- `Ban_do_cu_diem_tien_don` (298 dòng): Cứ điểm: ô tiền đồn — points[].outpost[]: ô tháp của tiền đồn
- `Ban_do_quan` (703 dòng): Bản đồ: quân đặt sẵn — units[]: quân đặt sẵn lúc vào trận
- `Ban_do_can_cu` (100 dòng): Bản đồ: căn cứ — bases[]: căn cứ mỗi đội (nhà chính)
- `Ban_do_can_cu_o` [bulk.zip] (1396 dòng): Căn cứ: ô — bases[].slots[]: ô xây (loại, cỡ, hướng)
- `Ban_do_tuong` (279 dòng): Bản đồ: tuyến tường — walls[]: tuyến tường (chủ, vòng, bán kính, cổng)
- `Ban_do_tuong_doan` [bulk.zip] (1079 dòng): Tuyến tường: đoạn — walls[].segments[]: đoạn tường (súng, thêm)
- `Ban_do_phao_dai_o` [bulk.zip] (1394 dòng): Pháo đài: ô — fortress.slots[]: ô của căn cứ nhiều lớp (vòng, chỗ, cỡ)
- `Ban_do_canh` [bulk.zip] (658 dòng): Bản đồ: cạnh — edges.segments[]: kiểu cạnh (edgeType), biến đổi (edgeModifier), bờ
- `Ban_do_goc_canh` [bulk.zip] (658 dòng): Bản đồ: góc cạnh — edges.corners[]: góc nối hai cạnh
- `Ban_do_lien_ket_canh` [bulk.zip] (1013 dòng): Bản đồ: lối ra cạnh — edges.links[]: đường / ray / biển ra khỏi bản đồ
- `Ban_do_cong_vao` (3200 dòng): Bản đồ: cổng vào — entryGates[]: cổng vào (vị trí, hướng vào, visualIngress, ray)
- `Ban_do_tag_dia_hinh` [bulk.zip] (38788 dòng): Bản đồ: tag địa hình — terrain.zones[].rects: mỗi hình chữ nhật một dòng (x0, z0, x1, z1)
- `Ban_do_dia_danh` (300 dòng): Bản đồ: địa danh — landmarks[]: landmarkId, tên Việt / Anh, bí danh, vị trí
- `Ban_do_trung_lap` (250 dòng): Bản đồ: trung lập — neutrals[]: loại, vị trí (luật: Trung_lap_luat)
- `Ban_do_vat_the` [bulk.zip] (89245 dòng): Bản đồ: vật thể — props[]: mỗi vật thể một dòng (loại, vị trí, xoay, trung lập)
- `Ban_do_trang_tri` [bulk.zip] (9347 dòng): Bản đồ: trang trí — decor[]: vật trang trí (không lối chơi)
- `Ban_do_duong` [bulk.zip] (1287 dòng): Bản đồ: đường — roads[]: đường (điểm x;z nối tiếp, rộng)
- `Ban_do_rail` (23 dòng): Bản đồ: ray — rails[]: RailSpline (điểm, đoạn chơi, chỗ cắt đường)
- `Ban_do_rail_giao_cat` (24 dòng): Ray: chỗ cắt đường — rails[].crossings[]
- `Ban_do_tuyen_bien` (87 dòng): Bản đồ: tuyến biển (nút) — seaRoutes.nodes[]: SeaRouteGraph nút (làn, kiểu)
- `Ban_do_tuyen_bien_doan` (108 dòng): Tuyến biển: đoạn — seaRoutes.segments[]: đoạn nối hai nút
- `Ban_do_bien_phao` (6 dòng): Biển: khẩu đội bờ — sea.batteries[]
- `Ban_do_bien_do_bo` (12 dòng): Biển: điểm đổ bộ — sea.landings[]
- `Ban_do_bien_lan` (9 dòng): Biển: làn tàu — sea.lanes[]
- `Ban_do_cu_diem_bai_tha_can_cu` (100 dòng): Bản đồ: cứ điểm, bãi thả, căn cứ, tường (đếm) — Mỗi bản đồ: số cứ điểm, bãi thả, căn cứ, ô căn cứ, tuyến tường, ô pháo đài, cổng vào, vật thể (đếm từ các sheet con)
- `Ban_do_goc` (25 dòng): Bản đồ gốc — map_dressing.json maps[]: 25 bản đồ gốc (biome, mật độ, đồi, hào, seed)
- `Ban_do_biome` (8 dòng): Biome — map_dressing.json biomes[]: dải, vòng, bộ trang trí theo vùng
- `Ban_do_dia_danh_mo_hinh` (69 dòng): Địa danh: mô hình — map_dressing.json landmarks[]: mô hình địa danh, vị trí, xoay, tỷ lệ
- `Ban_do_trang_tri_luat` (83 dòng): Trang trí: luật — map_dressing.json camera, edges, version
- `Vat_the_loai` (122 dòng): Loại vật thể — balance.json props[]: máu, giáp, kích thước, chặn đường / đạn, nổ khi vỡ
- `Trung_lap_luat` (18 dòng): Trung lập: luật — balance.json neutrals: số liệu (bán kính, thời gian chiếm, sửa, nổ) và loại theo chế độ
- `Thoi_tiet` (8 dòng): Thời tiết — campaign.json eventLibrary.rules.weatherSight (hệ số tầm nhìn) và số nhiệm vụ dùng
- `Ban_do_do_tinh` (100 dòng): Bản đồ: đo tĩnh — Mỗi file bản đồ x chỉ số đo tĩnh (Tools/audit/map_audit.py -> Docs/checks/map_audit.csv: quãng đường bãi thả -> mục tiêu, chênh trung vị, số làn độc…
- `Ngan_sach_thuc_the` (20 dòng): Ngân sách thực thể — Mỗi nguồn thực thể: sống lâu (xe, máy bay, tháp, tường, vật thể) / ngắn hạn (lửa, khói, tia, vòm); mô phỏng hay chỉ hình; đã có giới hạn trong mã hay…
- `Ngan_sach_thuc_the_che_do` (26 dòng): Ngân sách thực thể theo chế độ — Mỗi chế độ x phe: số xe tối đa game đặt (SimWorld.EnableEconomy: phe địch Catalog.VehicleCapFor(chế độ), người chơi TeamEconomy.MaxVehicles), máy bay…
- `Ban_do_tham_chieu` (33 dòng): Bản đồ: khu vực và game tham khảo — Mỗi biome và bản đồ gốc một dòng: khu vực địa lý / biome thật lấy ý, địa danh, game tham khảo cơ chế bản đồ (spec 12.2; chỉ dữ liệu có trong repo)
- `Hang_so_ban_do` (17 dòng): Hằng số bản đồ và đường đi — Assets/MachineBrigade/Resources/Data/tunables.json: 'maps' (lớp chủ → tên): một dòng một hằng số; mã game đọc qua SimTunables, giữ nguyên giá trị khi…
- `Ban_do_tom_tat` (100 dòng): Tóm tắt từng bản đồ — Một dòng một bản đồ: số vật thể theo loại, phần trăm diện tích mỗi tag địa hình (rect sau đè rect trước, lưới terrain_cell), số ô căn cứ, số ô pháo đ…
