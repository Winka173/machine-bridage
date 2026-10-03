# 08_ban_do — Bản đồ

Bộ xuất dữ liệu Machine Brigade, commit 90337539, ngày 2026-10-03. Sinh bởi `python Tools/export/export.py` (lượt 6): bảng in đúng ô của csv / xlsx; văn bản lấy từ tài liệu thiết kế (Tools/docs) và chuỗi trong game. Toàn văn: Machine_Brigade_Design_FULL_2026-10-03.md.

100 file bản đồ (25 bản đồ x 4 biến thể): bãi thả, cứ điểm, căn cứ, tường, pháo đài, cạnh, cổng vào, tag địa hình, địa danh, ray, tuyến biển, trung lập, vật thể, trang trí, đường, quân đặt sẵn; bản đồ gốc, biome, loại vật thể, thời tiết

Mục trong file này: 7b. Biển, hộ tống, bản đồ dài, roster mới và đòn lớn; 15. Bản đồ; 15b. Đo bản đồ tĩnh.

### 7b. Biển, hộ tống, bản đồ dài, roster mới và đòn lớn

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_tuyen_bien; 08_ban_do/Ban_do_bien_lan; 08_ban_do/Ban_do_bien_phao; 08_ban_do/Ban_do_bien_do_bo. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §7b.

#### Lighthouse Bay và hải chiến (prompt 16 A–D)

- **Lighthouse Bay:** bờ biển đá, 2 vịnh có bãi và cầu tàu, hải đăng trên mũi đất (giữ nó thì thấy hạm đội), 2 trận địa pháo bờ biển chiếm được (chỉ bắn tàu), làng chài và pháo đài cũ. Biển chiếm 36% map, 3 tuyến biển. Có bản Giữ cứ điểm, Sinh tồn, Công thành và bản dài.
- **Tàu chạy trên tuyến biển:** xe tăng chỉ bắn tới tuyến gần từ đầu cầu tàu và mũi đất; xe săn tăng tầm trung (38–42 m) bắn được từ sườn đá.
- **Leviathan (Kessler):** 9 bộ phận, giáp hông cấp 4, boong cấp 2; 3 pha: loạt pháo có cảnh báo, tên lửa hành trình, đổ tăng, trực thăng và gọi jet; pha 3 chạy ra biển theo đồng hồ, thoát được thì thua nhiệm vụ. Chết thì nghiêng, gãy đôi và chìm.
- **Hạm đội:** 2 tàu hộ vệ (CIWS che Leviathan), 3 xuồng tên lửa đánh đầu cầu tàu, tàu đổ bộ.
- **Chiến dịch và chế độ:** nhiệm vụ 4-11 "Leviathan" cuối chương 4 (mở nhánh Pháo bờ biển tầm xa của Pháo đài hạng nặng); Săn trùm tự chuyển sang Lighthouse Bay cho Leviathan rồi quay lại, mang theo quân, CP và đồng hồ; Tác chiến có mutator Bão biển và Hạm đội.

#### Hộ tống cho mọi boss (prompt 16 E–F)

Mỗi boss mang một nhóm đi cùng và thêm một nhóm ở mỗi lần đổi pha; số hộ tống còn sống tối đa theo độ khó: Easy 5, Normal 7, Hard 8, VeryHard 9, Heroic 9, Iron 9 (Săn trùm ít hơn). Mỗi nhóm có một xe phụ trợ (sửa boss, gây nhiễu tên lửa ta, phòng không che boss, đánh dấu quân ta) nên người chơi phải chọn đánh boss hay hộ tống trước. Hộ tống không rời boss quá 28 m, hạ được thì thưởng CP, có dấu cam, và thanh máu boss đếm số hộ tống.

| Boss | Đi cùng | Khi đổi pha |
|---|---|---|
| Juggernaut · Đoàn tàu bọc thép | Xe bọc thép bánh lốp, Xe bọc thép bánh lốp, Pháo cao xạ tự hành (phòng không che boss), Xe bọc thép bánh lốp (đánh dấu quân ta) | Tăng nhẹ lội nước, Tăng nhẹ lội nước, Xe công binh (sửa boss) |
| Tempest · Behemoth pháo điện từ | Tăng chủ lực, Xe gây nhiễu điện tử (gây nhiễu tên lửa ta), Xe gây nhiễu điện tử (gây nhiễu tên lửa ta), Xe tên lửa phòng không tầm trung (phòng không che boss) | Xe gây nhiễu điện tử (gây nhiễu tên lửa ta), Xe gây nhiễu điện tử (gây nhiễu tên lửa ta) |
| Behemoth · Quái vật thép | Tăng chủ lực, Tăng chủ lực, Tăng hạng nặng, Pháo cao xạ tự hành (phòng không che boss) | Tăng hạng nặng ★, Xe công binh (sửa boss) |
| Inferno · Behemoth phun lửa | Tăng phun lửa, Tăng phun lửa, Pháo cao xạ tự hành (phòng không che boss), Xe thả khói (thả khói) | Tăng phun lửa, Tăng phun lửa, Xe công binh (sửa boss) |
| Harpy · Trực thăng khổng lồ | Trực thăng tấn công, Trực thăng tấn công, Tiêm kích (phòng không che boss), Trực thăng trinh sát vũ trang (đánh dấu quân ta) | Trực thăng trinh sát vũ trang (đánh dấu quân ta) |
| Spectre · Máy bay pháo | Tiêm kích (phòng không che boss), Tiêm kích (phòng không che boss), Tiêm kích (phòng không che boss), UAV trinh sát (đánh dấu quân ta) | Tiêm kích (phòng không che boss), Tiêm kích (phòng không che boss) |
| Jötunn · Pháo đài di động | Tăng hạng nặng, Tăng hạng nặng, Xe tên lửa phòng không tầm trung (phòng không che boss), Xe công binh (sửa boss) | Xe công binh (sửa boss) |
| Hive · Pháo đài drone | Tăng chủ lực, Xe phòng không pháo – tên lửa (phòng không che boss), Xe tên lửa phòng không tầm trung (phòng không che boss) | Xe phóng drone FPV, Xe phóng drone FPV, UAV trinh sát (đánh dấu quân ta) |
| Bastion · Pháo đài | Pháo chống tăng tự hành, Pháo chống tăng tự hành, Tăng chủ lực, Xe phòng không pháo – tên lửa (phòng không che boss) | Tăng hạng nặng, Xe tên lửa phòng không tầm trung (phòng không che boss), Xe công binh (sửa boss) |
| Matriarch · Tàu mẹ drone | UAV tấn công, UAV tấn công, Tiêm kích (phòng không che boss), UAV trinh sát (đánh dấu quân ta) | Trực thăng trinh sát vũ trang (đánh dấu quân ta) |
| Icarus · Phi thuyền quỹ đạo | Tăng hạng nặng tinh nhuệ, Grad tinh nhuệ, UAV trinh sát (đánh dấu quân ta), Tiêm kích (phòng không che boss), Tiêm kích (phòng không che boss) | Xe phóng drone FPV tinh nhuệ, Xe gây nhiễu điện tử (gây nhiễu tên lửa ta) / Trực thăng tinh nhuệ, Xe công binh (sửa boss) |
| Nemesis · Đoàn tàu tên lửa | Xe chiến đấu bộ binh, Xe chiến đấu bộ binh, Xe tên lửa phòng không tầm trung (phòng không che boss), Trực thăng trinh sát vũ trang (đánh dấu quân ta) | Xe chiến đấu bộ binh, Xe chiến đấu bộ binh, Xe thả khói (thả khói) |
| Gungnir · Pháo điện từ đường ray | Tăng chủ lực, Tăng chủ lực, Pháo cao xạ tự hành (phòng không che boss), Xe radar phản pháo (đánh dấu quân ta) | Tăng chủ lực, Tăng chủ lực, Xe công binh (sửa boss) |
| Tartarus · Máy khoan |  | Xe chiến đấu bộ binh, Pháo cao xạ tự hành (phòng không che boss), Xe công binh (sửa boss) |
| Roc · Khí cầu chỉ huy | Tiêm kích (phòng không che boss), Tiêm kích (phòng không che boss), Tiêm kích (phòng không che boss) | Trực thăng tấn công, Trực thăng trinh sát vũ trang (đánh dấu quân ta) |
| Charybdis · Tàu đệm khí đổ bộ | Xuồng đệm khí hộ tống, Xuồng đệm khí hộ tống, Pháo cao xạ tự hành (phòng không che boss), Xuồng đệm khí hộ tống (đánh dấu quân ta) | Xuồng đệm khí hộ tống (đánh dấu quân ta) |
| Atlas · Xe chỉ huy siêu nặng | Tăng chủ lực ★, Tăng hạng nặng, Pháo cao xạ tự hành (phòng không che boss) | Tăng chủ lực ★, Tăng chủ lực ★, Pháo cao xạ tự hành (phòng không che boss) |

#### Bản đồ dài và căn cứ nhiều lớp (prompt 17 A–B)

- Công thành, Phòng thủ, Vô tận và Pháo đài tuần chơi trên bản dài: 300 m ngang, 480 m dọc theo hướng tấn công (đủ cho 20 map có bản công thành, cộng Lighthouse Bay); các chế độ khác giữ map 300 × 300 m.
- Căn cứ nhiều lớp: vùng đệm (răng rồng, hào, dây thép gai, 1–4 ụ bắn), trạm tiền tiêu và 8 cứ điểm, tường ngoài có cổng chính và 2 cửa phụ, sân trong, thành trong, rồi HQ. Quân phòng thủ thả xuống trong thành; quân tấn công thả dù xa dần lên sau mỗi vòng tường bị phá.
- Ô theo cấp HQ từ 4/1/0/1 (nhỏ/vừa/lớn/tiện ích) tới 8/5/3/4; nhãn ô mới: cổng ngoài, tường ngoài, sân trong, tường trong. Một loadout dùng cho cả trại và căn cứ dài: căn cứ dài chưa chỉnh thì mượn tháp của trại.
- Camera nhìn về phía tây trên map dài (zoom mặc định 21, xa nhất 50); bản đồ nhỏ giữ hình chữ nhật.
- Tìm đường: 150 × 240 ô, 1,9 MB; một đường hết chiều dài mất 5–6 ms trên máy bàn, khoảng 35 ms trên điện thoại (đo lại ở phase kiểm tra).

#### Đơn vị mới và rà soát roster (prompt 17 C–D)

- **Mới:** tiêm kích tàng hình (14 CP), drone yểm trợ (6 CP, bay theo máy bay có người lái và hút tên lửa bắn vào chúng), xe tăng laser (10 CP, tia mạnh dần ×0,3 → ×2 trong 6 giây), xe mang khiên (7 CP) và tháp khiên (ô lớn), xe lô cốt (6 CP, đứng yên 3 giây thì đào hầm: giáp trước dày hơn, tầm +30%), máy bay mẹ thả 8 drone FPV (8 CP), tháp tiếp sóng CP (ô nhỏ, tối đa 2 mỗi căn cứ). Giá đo bằng bộ đo giá trị thực chiến.
- **Gộp:** A-10 vào Cường kích (model Su-25, cả hai bộ vũ khí và 2 Kh-29, 15 CP); Ka-52 vào Trực thăng tấn công (giữ Hellfire tầm 55 m và Stinger, 11 CP); xe ATGM vào xe phóng drone FPV; công binh phá mìn vào Công binh; ụ súng vào tháp pháo. Model cũ giữ làm mẫu phụ.
- **Tăng hai nòng và tăng hạng nặng:** tăng hai nòng bắn 2 phát 120 mm một lượt, nạp 7 giây, hạ xe tăng nhanh nhất (37,9 s); tăng hạng nặng đổi sang đạn nổ khi bắn công trình và xe nhẹ, 12 CP, sống dai và phá công trình tốt nhất theo CP.
- **Save:** giữ hạng cao hơn, hoàn xu và bản thiết kế của thẻ hạng thấp; Ka-52 đã mua được hoàn 3.500 xu; ụ súng trong loadout thành tháp pháo.

#### Đòn lớn của mọi boss (prompt 18)

Mỗi boss có một đòn lớn lấy từ cùng một hệ dữ liệu (mẫu hình dạng + tham số). Đòn đầu tiên khoảng 30 giây sau khi boss xuất hiện; luôn có cảnh báo trên mặt đất; phá bộ phận mang đòn trong lúc cảnh báo thì đòn yếu đi hoặc bị hủy; quân ta biết né khỏi vùng cảnh báo. Theo độ khó: Easy sát thương ×1, hồi ×1.2, cảnh báo +1 s; Normal sát thương ×1, hồi ×1; Hard sát thương ×1, hồi ×0.9; VeryHard sát thương ×1, hồi ×0.8; Heroic sát thương ×1, hồi ×0.8; Iron sát thương ×1, hồi ×0.8.

Bộ phận mới: bệ dựng tên lửa của Doomsday Train, khoang bom của Hive Carrier và của Khí cầu chỉ huy. Prompt 19: đòn của Icarus là mưa thanh tungsten từ vệ tinh (thay cho tia laser quét); từ prompt 20 mini boss dùng đòn lớn thu nhỏ (sát thương ×0,7, hồi chiêu ×1,3).

Sheet: 08_ban_do/Ban_do_tuyen_bien — Bản đồ: tuyến biển (nút) (87 dòng, 10 cột)

| id | ban_do_id | thu_tu | id_goc | kind | lane | x_m | z_m |
|---|---|---|---|---|---|---|---|
| lighthousebay_conquest/far_0 | lighthousebay_conquest | 14 | far_0 | exit | far | -5.73 | -175.43 |
| lighthousebay_conquest/far_1 | lighthousebay_conquest | 15 | far_1 | track | far | 28.28 | -141.42 |
| lighthousebay_conquest/far_2 | lighthousebay_conquest | 16 | far_2 | track | far | 56.57 | -113.14 |
| lighthousebay_conquest/far_3 | lighthousebay_conquest | 17 | far_3 | track | far | 84.85 | -84.85 |
| lighthousebay_conquest/far_4 | lighthousebay_conquest | 18 | far_4 | track | far | 113.14 | -56.57 |
| lighthousebay_conquest/far_5 | lighthousebay_conquest | 19 | far_5 | track | far | 141.42 | -28.28 |
| lighthousebay_conquest/far_6 | lighthousebay_conquest | 20 | far_6 | exit | far | 175.43 | 5.73 |
| lighthousebay_conquest/hold_sea_far_2 | lighthousebay_conquest | 26 | hold_sea_far_2 | holding | far | 69.3 | -125.87 |
| lighthousebay_conquest/hold_sea_far_3 | lighthousebay_conquest | 27 | hold_sea_far_3 | holding | far | 97.58 | -97.58 |
| lighthousebay_conquest/hold_sea_far_4 | lighthousebay_conquest | 28 | hold_sea_far_4 | holding | far | 125.87 | -69.3 |
| lighthousebay_conquest/hold_shore_near_1 | lighthousebay_conquest | 21 | hold_shore_near_1 | holding | near | -2.83 | -110.31 |
| lighthousebay_conquest/hold_shore_near_2 | lighthousebay_conquest | 22 | hold_shore_near_2 | holding | near | 25.46 | -82.02 |
| lighthousebay_conquest/hold_shore_near_3 | lighthousebay_conquest | 23 | hold_shore_near_3 | holding | near | 53.74 | -53.74 |
| lighthousebay_conquest/hold_shore_near_4 | lighthousebay_conquest | 24 | hold_shore_near_4 | holding | near | 82.02 | -25.46 |
| lighthousebay_conquest/hold_shore_near_5 | lighthousebay_conquest | 25 | hold_shore_near_5 | holding | near | 110.31 | 2.83 |

*15 / 87 dòng đầu: xem sheet 08_ban_do/Ban_do_tuyen_bien.*

Sheet: 08_ban_do/Ban_do_bien_lan — Biển: làn tàu (9 dòng, 9 cột)

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

Sheet: 08_ban_do/Ban_do_bien_phao — Biển: khẩu đội bờ (6 dòng, 9 cột)

| id | ban_do_id | thu_tu | heading_deg | id_goc | x_m | z_m |
|---|---|---|---|---|---|---|
| lighthousebay_conquest/battery_e | lighthousebay_conquest | 1 | 135 | battery_e | 84.85 | 62.23 |
| lighthousebay_conquest/battery_w | lighthousebay_conquest | 0 | 135 | battery_w | -62.23 | -84.85 |
| lighthousebay_sandbox/battery_e | lighthousebay_sandbox | 1 | 135 | battery_e | 84.85 | 62.23 |
| lighthousebay_sandbox/battery_w | lighthousebay_sandbox | 0 | 135 | battery_w | -62.23 | -84.85 |
| lighthousebay_siege/battery_e | lighthousebay_siege | 1 | 135 | battery_e | 84.85 | 62.23 |
| lighthousebay_siege/battery_w | lighthousebay_siege | 0 | 135 | battery_w | -62.23 | -84.85 |

Sheet: 08_ban_do/Ban_do_bien_do_bo — Biển: điểm đổ bộ (12 dòng, 8 cột)

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

## 15. Bản đồ

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do; 08_ban_do/Ban_do_goc; 08_ban_do/Ban_do_biome; 08_ban_do/Thoi_tiet; 08_ban_do/Ban_do_dia_danh; 08_ban_do/Ban_do_rail; 08_ban_do/Ban_do_tag_dia_hinh; 08_ban_do/Ban_do_cong_vao; 08_ban_do/Ban_do_trung_lap; 08_ban_do/Vat_the_loai. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §15. Bản đồ.

25 chiến trường 300 × 300 m, cộng 25 bản dài 300 × 480 m (phần 7b) (8 bản đồ mới: Stormbeach, Hollow Dam, Veyra, Helion Launch Complex, Salt Flats, Border Crossing, Mirewood, Coral Keys), đường viền không đều; phần ngoài viền vẫn được dựng như bản đồ (nhà, rừng, đá) chỉ để trang trí, ranh giới là đường đứt nét. Mỗi trại có sở chỉ huy và ô tháp nhỏ/vừa/lớn/tiện ích; mỗi cứ điểm có tiền đồn. Phiên bản công thành đặt pháo đài chiếm 45% bản đồ ở đông bắc (phần 7).

#### Ashfield · temperate

Thị trấn · Ôn đới

#### Dunebreak · desert

Lọc dầu · Sa mạc

#### Frostpeak · snow

Làng núi · Tuyết

#### Ironport · harbor

Cảng · Công nghiệp

#### Red Rock · desert

Hẻm núi · Sa mạc

#### Whiteout Pass · snow

Đèo rừng · Tuyết

#### Greenvale · temperate

Đồng quê · Ôn đới

#### Rust Yard · harbor

Khu công nghiệp · Đổ nát

#### Emberridge · volcanic

Đồng dung nham · Núi lửa

#### Jungle Pass · jungle

Đền cổ · Rừng nhiệt đới

#### Skyhold · temperate

Sân bay quân sự · Ôn đới

#### Metro City · urban

Trung tâm · Đô thị

#### Stormbeach · temperate

Bãi biển và vách đá · Bờ biển

#### Hollow Dam · temperate

Đập và hẻm sông · Ôn đới

#### Veyra · urban

Khu chính phủ · Đô thị

#### Helion Launch Complex · desert

Tổ hợp phóng · Sa mạc

#### Salt Flats · desert

Đồng muối trống trải · Sa mạc

#### Border Crossing · temperate

Vượt sông · Ôn đới

#### Mirewood · jungle

Đường đắp · Rừng nhiệt đới

#### Coral Keys · desert

Đảo và cầu · Nhiệt đới

#### Beacon Bay · temperate

Bờ biển và tuyến biển · Ôn đới

#### Deepcut Mine · desert

Hố mỏ bậc thang · Sa mạc

#### Skygate Array · snow

Sân bay vũ trụ · Tuyết

#### Foundry · urban

Xưởng xe tăng · Công nghiệp

#### Veyra Old Quarter · urban

Phố cổ · Đô thị

#### 15g. Bốn vùng, kiểu cạnh, địa hình, địa danh, đường ray, tuyến biển (prompt 33)

##### Bốn vùng của bản đồ

| Vùng | Ở đâu | Nội dung | Lối chơi |
|---|---|---|---|
| 1. Vùng chơi | hình chữ nhật của bản đồ | navmesh, cứ điểm, căn cứ, tháp, chỗ nấp, vật chặn tầm nhìn, tag địa hình | Có |
| 2. Dải viền | 12–20 m ngoài mép (theo bản đồ) | chuyển cảnh: gờ đất, mương, vách, bãi, mép nước, góc dựng sẵn | Không |
| 3. Vành ngoài | 120 m quanh bản vuông; 73 / 128 m bên / đầu bản dài | trang trí instancing theo seed cố định; nửa xa dùng HLOD | Không; không collider, không chặn tầm nhìn |
| 4. Chân trời | ngoài vành | dãy núi thô, biển xa, đảo mờ, tàu xa, mặt đất chân trời, sương | Không |

Bề rộng vành = khung nhìn camera lớn nhất (trực giao, nghiêng 52°, zoom xa nhất 42 / 50, tỷ lệ 4:3, 16:9, 20:9, camera không xoay) + 15 %: tầm với 103.7 m (vuông), 63.5 / 111.1 m (dài).

##### Kiểu cạnh (edgeType) theo chiến trường

Phía BIỂN: mặt nước tới chân trời, sóng, bóng tàu xa, đảo mờ, không nhà, rừng, đất; bờ chuyển tiếp theo kiểu bờ (bãi: dải sóng vỗ; vách: đá trụ; cầu cảng: tường kè, cần cẩu, container). SÔNG chảy tiếp ra ngoài; VÁCH dựng thành vách đá; ĐÔ THỊ là thành phố của theme. Góc giao giữa hai kiểu dùng 10 tài sản góc dựng sẵn. Đường bộ, ray (tới cửa hầm), sông, bờ biển và tuyến biển (phao) kéo dài ra vành ngoài.

| Chiến trường | Bắc | Đông | Nam | Tây |
|---|---|---|---|---|
| Ashfield | đất | đất | đất | đất |
| Border Crossing | đất | đất / sông / đất | đất | đất / sông / đất |
| Veyra | đô thị | đô thị / sông / đô thị | đô thị | đô thị / sông / đô thị |
| Coral Keys | biển (bãi) / đất | biển (bãi) / đất | đất / biển (bãi) | đất / biển (bãi) |
| Dunebreak | đất (công nghiệp) | đất (công nghiệp) | đất (công nghiệp) | đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) |
| Emberridge | đất | đất | đất | đất |
| Foundry | đô thị (công nghiệp) | đô thị (công nghiệp) | đô thị (công nghiệp) | đô thị (công nghiệp) |
| Frostpeak | đất / vách / đất | đất | đất | đất |
| Greenvale | đất | đất | đất | đất |
| Hollow Dam | sông / đất | đất | đất / sông / đất | đất / sông |
| Ironport | biển (cảng, cầu cảng) | đất (công nghiệp) | đất (công nghiệp) | đất (công nghiệp) |
| Jungle Pass | đất | đất / vách / đất | đất | đất / vách / đất |
| Stormbeach | đất | biển (bãi) / đất / vách / đất | biển (bãi) | biển (bãi) / đất / vách / đất |
| Helion Launch Complex | đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) | đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) | đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) | đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) |
| Beacon Bay | đất | đất / biển (vách) / đất | đất / biển (bãi) / đất | đất |
| Metro City | đô thị | đô thị | đô thị | đô thị |
| Deepcut Mine | vách (công nghiệp) / đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) | vách (công nghiệp) / đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) | đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) / vách (công nghiệp) | đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) / vách (công nghiệp) |
| Skygate Array | đất (công nghiệp) | đất (công nghiệp) | đất (công nghiệp) | đất (công nghiệp) |
| Red Rock | đất | đất | đất / vách / đất | đất / vách / đất |
| Rust Yard | biển (công nghiệp, cầu cảng) | đất (công nghiệp) | đất (công nghiệp) | đất (công nghiệp) |
| Salt Flats | đất | đất | đất | đất |
| Skyhold | đất | đất | đất | đất |
| Mirewood | đất / sông / đất | đất / sông / đất | đất / sông / đất | đất / sông / đất |
| Veyra Old Quarter | đô thị | đô thị | đô thị | đô thị |
| Whiteout Pass | đất | đất | đất | đất |

Tài sản góc (số lần trong 100 file): outer_land 298, corner_land_cliff 146, outer_urban 64, bank_land_river 60, corner_land_sea 38, outer_sea 16, embankment_urban_river 14, outer_land_sea 12, outer_cliff 7, outer_river 3.

##### Tag địa hình

| Tag | Tên | Tác dụng | Phủ (cả 100 file) |
|---|---|---|---|
| ROAD | Đường | tốc độ +20 % | 11,6 % |
| ROUGH | Gồ ghề | tốc độ −15 % (đô thị, đổ nát, sỏi đá; chỗ nấp vẫn do nhà / vật thể) | 6,7 % |
| FOREST | Rừng | tốc độ −25 %; tầm nhìn của địch lên xe trong rừng ×0,7 | 4,2 % |
| SHALLOW_WATER | Nước nông | xe thường −50 %; xe lội nước và đệm khí không chậm | 0,8 % |

Chi phí đường tĩnh theo tag (không đổi theo tick). DEEP_FORD để sau: bộ tìm đường chưa có chi phí theo loại xe.

##### Địa danh

Mỗi chiến trường 3 địa danh (landmarkId, tên song ngữ, khớp thoại prompt 30). Địa danh không có vật thể trên bản đồ được dựng bằng mô hình trang trí (không collider) ở chỗ trống gần nhất, tránh cứ điểm, đường, ray, cổng.

| Chiến trường | Địa danh |
|---|---|
| Ashfield | Tháp nước kho phía tây · Tháp nước kho phía đông · Tháp cổ thị trấn |
| Border Crossing | Cây cầu lớn · Nhà thờ làng biên giới · Đèn pha đầu cầu |
| Veyra | Dinh thự (mô hình trang trí) · Nhà ga (mô hình trang trí) · Tòa tháp Bộ |
| Coral Keys | Ngọn hải đăng (mô hình trang trí) · Tháp canh đảo tây · Tháp canh đảo đông |
| Dunebreak | Nhà máy lọc dầu · Cột vô tuyến sa mạc · Ra-đa phía bắc |
| Emberridge | Nhà máy địa nhiệt (mô hình trang trí) · Cột đá vỏ chai · Sườn núi lửa |
| Foundry | Ống khói xưởng đúc · Xưởng phía bắc · Xưởng phía nam |
| Frostpeak | Trạm ra-đa · Nhà thờ làng · Tháp nước trại gỗ |
| Greenvale | Si-lô trại phía tây · Nhà thờ ngã tư · Tháp nước trại phía đông |
| Hollow Dam | Con đập (mô hình trang trí) · Tháp đập · Trạm thủy điện |
| Ironport | Cần cẩu cảng · Bến tàu · Tháp nước ga hàng (mô hình trang trí) |
| Jungle Pass | Ngôi đền · Khúc cạn đền · Nhà thờ làng phía tây (mô hình trang trí) |
| Stormbeach | Trạm ra-đa · Nhà thờ làng · Vách đá |
| Helion Launch Complex | Giàn phóng · Nhà chứa lắp ráp · Núi bàn phía bắc |
| Beacon Bay | Ngọn hải đăng · Pháo đài cũ · Làng chài |
| Metro City | Tòa tháp phía bắc · Quảng trường · Biển quảng cáo bãi xe |
| Deepcut Mine | Cần cẩu máy nghiền · Đáy mỏ · Trạm bốc quặng |
| Skygate Array | Dàn ăng-ten · Giàn phóng phía tây · Bãi đáp |
| Red Rock | Tháp nước trạm lữ hành · Núi bàn đỏ · Nhà thờ thị trấn mỏ (mô hình trang trí) |
| Rust Yard | Tháp nước bãi · Xưởng đúc · Tháp đổ bến cảng |
| Salt Flats | Mốc trắc địa (mô hình trang trí) · Ra-đa trắc địa · Trạm bơm nước muối |
| Skyhold | Đài kiểm soát · Chảo ra-đa · Nhà chứa máy bay phía tây |
| Mirewood | Đền chìm · Tháp canh làng tây · Ra-đa đầm lầy |
| Veyra Old Quarter | Nhà thờ lớn · Quảng trường đồng hồ (mô hình trang trí) · Cột vô tuyến khu phố cổ |
| Whiteout Pass | Cột tín hiệu · Hồ băng · Tháp canh đèo |

##### Đường ray (RailSpline)

Lớp riêng, không phải navmesh: từ cửa hầm ngoài bản đồ qua dải viền, cổng vào, tới điểm dừng; Juggernaut, Nemesis, Gungnir và tàu chi viện Công thành chạy trên ray. Chỗ cắt đường bộ: MỞ → CẢNH BÁO (≥ 4 s) → ĐÓNG → TÀU QUA → MỞ.

##### Tuyến tàu biển (SeaRouteGraph)

Tàu lớn đi trên đồ thị tuyến (đoạn, nút, vịnh tránh), giữ đoạn hiện tại và đoạn kế, khoảng cách tối thiểu nửa thân tàu này + nửa thân tàu trước + 10 m, ưu tiên cố định.

##### 12 validator (Tools/maps/validate_p33.py, lần chạy đầy đủ gần nhất)

Ảnh mép bản đồ ở zoom xa nhất cho mỗi biome: cần ảnh chụp từ Unity (ghi trong LOCAL_TODO).

Sheet: 08_ban_do/Ban_do — Bản đồ (100 dòng, 44 cột)

| id | ban_do_goc | bien_the | tep | asymmetry_intended | asymmetry_reason | boundary | bounds | edges_band | edges_outer |
|---|---|---|---|---|---|---|---|---|---|
| ashfield_conquest | ashfield | conquest | ashfield_conquest.json |  |  | -146.62;-86.0;-146.19;-86.15;-146.0;-86.88;-145.94;-92.56;-… |  | 16.0 | 120.0 |
| ashfield_long | ashfield | long | ashfield_long.json | TRUE | Long battlefield: the attacker's square and the defender's… | -146.62;-86.0;-146.19;-86.15;-146.0;-86.88;-145.94;-92.56;-… | -150.0;-150.0;150.0;330.0 | 16.0 | 120.0 |
| ashfield_sandbox | ashfield | sandbox | ashfield_sandbox.json |  |  | -146.62;-86.0;-146.19;-86.15;-146.0;-86.88;-145.94;-92.56;-… |  | 16.0 | 120.0 |
| ashfield_siege | ashfield | siege | ashfield_siege.json | TRUE | Siege: one side holds the fortress, the other attacks it (p… | -146.62;-86.0;-146.19;-86.15;-146.0;-86.88;-145.94;-92.56;-… |  | 16.0 | 120.0 |
| borderbridge_conquest | borderbridge | conquest | borderbridge_conquest.json |  |  | -143.62;-144.38;-141.92;-144.98;-98.08;-144.02;-96.99;-143.… |  | 16.0 | 120.0 |
| borderbridge_long | borderbridge | long | borderbridge_long.json | TRUE | Long battlefield: the attacker's square and the defender's… | -146.62;158.0;-146.19;157.83;-146.0;156.97;-146.0;148.03;-1… | -150.0;-150.0;150.0;330.0 | 16.0 | 120.0 |
| borderbridge_sandbox | borderbridge | sandbox | borderbridge_sandbox.json |  |  | -143.62;-144.38;-141.92;-144.98;-98.08;-144.02;-96.99;-143.… |  | 16.0 | 120.0 |
| borderbridge_siege | borderbridge | siege | borderbridge_siege.json | TRUE | Siege: one side holds the fortress, the other attacks it (p… | -143.62;-144.38;-141.92;-144.98;-98.08;-144.02;-96.99;-143.… |  | 16.0 | 120.0 |
| capital_conquest | capital | conquest | capital_conquest.json |  |  | -146.62;-45.0;-146.19;-45.18;-146.0;-46.09;-146.0;-104.91;-… |  | 16.0 | 120.0 |
| capital_long | capital | long | capital_long.json | TRUE | Long battlefield: the attacker's square and the defender's… | -146.62;-45.0;-146.19;-45.18;-146.0;-46.09;-146.0;-104.91;-… | -150.0;-150.0;150.0;330.0 | 16.0 | 120.0 |
| capital_sandbox | capital | sandbox | capital_sandbox.json |  |  | -146.62;-45.0;-146.19;-45.18;-146.0;-46.09;-146.0;-104.91;-… |  | 16.0 | 120.0 |
| capital_siege | capital | siege | capital_siege.json | TRUE | Siege: one side holds the fortress, the other attacks it (p… | -146.62;-45.0;-146.19;-45.18;-146.0;-46.09;-146.0;-104.91;-… |  | 16.0 | 120.0 |
| coralisles_conquest | coralisles | conquest | coralisles_conquest.json |  |  | -147.62;-135.0;-147.19;-135.17;-147.0;-136.03;-146.91;-145.… |  | 16.0 | 120.0 |
| coralisles_long | coralisles | long | coralisles_long.json | TRUE | Long battlefield: the attacker's square and the defender's… | -147.62;-135.0;-147.19;-135.17;-147.0;-136.03;-146.91;-145.… | -150.0;-150.0;150.0;330.0 | 16.0 | 120.0 |
| coralisles_sandbox | coralisles | sandbox | coralisles_sandbox.json |  |  | -147.62;-135.0;-147.19;-135.17;-147.0;-136.03;-146.91;-145.… |  | 16.0 | 120.0 |

*15 / 100 dòng đầu: xem sheet 08_ban_do/Ban_do; in 10 / 44 cột; 22 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 08_ban_do/Ban_do_goc — Bản đồ gốc (25 dòng, 13 cột)

| id | biome | bien_the | berms | density | ditches | dry_beds | edge_band | far_tree | hills |
|---|---|---|---|---|---|---|---|---|---|
| ashfield | temperate | ashfield_conquest;ashfield_long;ashfield_sandbox;ashfield_s… | 6 | 1.0 | 3 | 1 | 16.0 |  | 8 |
| borderbridge | temperate | borderbridge_conquest;borderbridge_long;borderbridge_sandbo… | 6 | 1.0 | 3 | 1 | 16.0 |  | 8 |
| capital | urban | capital_conquest;capital_long;capital_sandbox;capital_siege | 4 | 1.0 | 2 | 0 | 12.0 |  | 0 |
| coralisles | coast | coralisles_conquest;coralisles_long;coralisles_sandbox;cora… | 4 | 1.0 | 1 | 1 | 12.0 | none | 5 |
| dunebreak | desert | dunebreak_conquest;dunebreak_long;dunebreak_sandbox;dunebre… | 4 | 1.0 | 0 | 3 | 20.0 |  | 6 |
| emberridge | volcanic | emberridge_conquest;emberridge_long;emberridge_sandbox;embe… | 3 | 1.0 | 0 | 2 | 16.0 |  | 8 |
| foundry | harbor | foundry_conquest;foundry_long;foundry_sandbox;foundry_siege | 5 | 1.0 | 3 | 0 | 12.0 |  | 3 |
| frostpeak | snow | frostpeak_conquest;frostpeak_long;frostpeak_sandbox;frostpe… | 4 | 1.0 | 0 | 1 | 18.0 |  | 8 |
| greenvale | temperate | greenvale_conquest;greenvale_long;greenvale_sandbox;greenva… | 6 | 1.1 | 3 | 1 | 16.0 |  | 8 |
| hydrodam | temperate | hydrodam_conquest;hydrodam_long;hydrodam_sandbox;hydrodam_s… | 6 | 1.0 | 3 | 1 | 16.0 |  | 8 |
| ironport | harbor | ironport_conquest;ironport_long;ironport_sandbox;ironport_s… | 5 | 1.0 | 3 | 0 | 14.0 |  | 3 |
| junglepass | jungle | junglepass_conquest;junglepass_long;junglepass_sandbox;jung… | 3 | 1.0 | 2 | 2 | 12.0 |  | 6 |
| landingbeach | coast | landingbeach_conquest;landingbeach_long;landingbeach_sandbo… | 4 | 1.0 | 1 | 1 | 14.0 |  | 5 |
| launchsite | desert | launchsite_conquest;launchsite_long;launchsite_sandbox;laun… | 4 | 0.8 | 0 | 3 | 20.0 |  | 6 |
| lighthousebay | coast | lighthousebay_conquest;lighthousebay_long;lighthousebay_san… | 4 | 1.0 | 1 | 1 | 14.0 |  | 5 |
| metrocity | urban | metrocity_conquest;metrocity_long;metrocity_sandbox;metroci… | 4 | 1.0 | 2 | 0 | 12.0 |  | 0 |
| openpit | desert | openpit_conquest;openpit_long;openpit_sandbox;openpit_siege | 4 | 0.9 | 0 | 3 | 18.0 |  | 6 |
| orbitalgate | snow | orbitalgate_conquest;orbitalgate_long;orbitalgate_sandbox;o… | 4 | 0.9 | 0 | 1 | 16.0 |  | 8 |
| redrock | desert | redrock_conquest;redrock_long;redrock_sandbox;redrock_siege | 4 | 1.0 | 0 | 3 | 18.0 |  | 6 |
| rustyard | harbor | rustyard_conquest;rustyard_long;rustyard_sandbox;rustyard_s… | 5 | 1.0 | 3 | 0 | 14.0 |  | 3 |
| saltflat | desert | saltflat_conquest;saltflat_long;saltflat_sandbox;saltflat_s… | 4 | 0.6 | 0 | 3 | 20.0 |  | 6 |
| skyhold | temperate | skyhold_conquest;skyhold_long;skyhold_sandbox;skyhold_siege | 6 | 0.8 | 3 | 1 | 18.0 |  | 8 |
| swamp | jungle | swamp_conquest;swamp_long;swamp_sandbox;swamp_siege | 3 | 1.1 | 2 | 2 | 14.0 |  | 6 |
| veyra_old_quarter | urban | veyra_old_quarter_conquest;veyra_old_quarter_long;veyra_old… | 4 | 1.0 | 2 | 0 | 12.0 |  | 0 |
| whiteout | snow | whiteout_conquest;whiteout_long;whiteout_sandbox;whiteout_s… | 4 | 0.8 | 0 | 1 | 20.0 |  | 8 |

*in 10 / 13 cột; 1 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 08_ban_do/Ban_do_biome — Biome (8 dòng, 19 cột)

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

*in 10 / 19 cột; 7 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 08_ban_do/Thoi_tiet — Thời tiết (8 dòng, 5 cột)

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

Sheet: 08_ban_do/Ban_do_dia_danh — Bản đồ: địa danh (300 dòng, 14 cột)

| id | ban_do_id | thu_tu | aliases | id_goc | kind | name_en | name_vi | prop | x_m |
|---|---|---|---|---|---|---|---|---|---|
| ashfield_conquest/ashfield.town_tower | ashfield_conquest | 2 | the square | ashfield.town_tower | ruin_tower | Old town tower | Tháp cổ thị trấn | ruin_tower | 10.0 |
| ashfield_conquest/ashfield.wt_east | ashfield_conquest | 1 | the depot | ashfield.wt_east | water_tower | East depot water tower | Tháp nước kho phía đông | water_tower | 52.5 |
| ashfield_conquest/ashfield.wt_west | ashfield_conquest | 0 | the depot | ashfield.wt_west | water_tower | West depot water tower | Tháp nước kho phía tây | water_tower | -52.5 |
| ashfield_long/ashfield.town_tower | ashfield_long | 2 | the square | ashfield.town_tower | ruin_tower | Old town tower | Tháp cổ thị trấn | ruin_tower | 10.0 |
| ashfield_long/ashfield.wt_east | ashfield_long | 1 | the depot | ashfield.wt_east | water_tower | East depot water tower | Tháp nước kho phía đông | water_tower | 52.5 |
| ashfield_long/ashfield.wt_west | ashfield_long | 0 | the depot | ashfield.wt_west | water_tower | West depot water tower | Tháp nước kho phía tây | water_tower | -52.5 |
| ashfield_sandbox/ashfield.town_tower | ashfield_sandbox | 2 | the square | ashfield.town_tower | ruin_tower | Old town tower | Tháp cổ thị trấn | ruin_tower | 10.0 |
| ashfield_sandbox/ashfield.wt_east | ashfield_sandbox | 1 | the depot | ashfield.wt_east | water_tower | East depot water tower | Tháp nước kho phía đông | water_tower | 52.5 |
| ashfield_sandbox/ashfield.wt_west | ashfield_sandbox | 0 | the depot | ashfield.wt_west | water_tower | West depot water tower | Tháp nước kho phía tây | water_tower | -52.5 |
| ashfield_siege/ashfield.town_tower | ashfield_siege | 2 | the square | ashfield.town_tower | ruin_tower | Old town tower | Tháp cổ thị trấn | ruin_tower | 10.0 |
| ashfield_siege/ashfield.wt_east | ashfield_siege | 1 | the depot | ashfield.wt_east | water_tower | East depot water tower | Tháp nước kho phía đông | water_tower | 52.5 |
| ashfield_siege/ashfield.wt_west | ashfield_siege | 0 | the depot | ashfield.wt_west | water_tower | West depot water tower | Tháp nước kho phía tây | water_tower | -52.5 |
| borderbridge_conquest/borderbridge.bridge_lights | borderbridge_conquest | 2 |  | borderbridge.bridge_lights | floodlight | Bridge floodlights | Đèn pha đầu cầu | floodlight_mast | 6.0 |
| borderbridge_conquest/borderbridge.great_bridge | borderbridge_conquest | 0 | the bridge | borderbridge.great_bridge | bridge | The great bridge | Cây cầu lớn |  | 0.0 |
| borderbridge_conquest/borderbridge.village_church | borderbridge_conquest | 1 |  | borderbridge.village_church | church | Border village church | Nhà thờ làng biên giới | church | -58.0 |

*15 / 300 dòng đầu: xem sheet 08_ban_do/Ban_do_dia_danh; in 10 / 14 cột; 1 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 08_ban_do/Ban_do_rail — Bản đồ: ray (23 dòng, 11 cột)

| id | ban_do_id | thu_tu | id_goc | kind | play_from | play_to | points |
|---|---|---|---|---|---|---|---|
| capital_conquest/nemesis | capital_conquest | 0 | nemesis | line | 55.5 | 154.0 | 190.0;-4.0;140.0;-4.0;36.0;-4.0 |
| capital_sandbox/nemesis | capital_sandbox | 0 | nemesis | line | 55.5 | 154.0 | 190.0;-4.0;140.0;-4.0;36.0;-4.0 |
| capital_siege/nemesis | capital_siege | 0 | nemesis | line | 55.5 | 154.0 | 190.0;-4.0;140.0;-4.0;36.0;-4.0 |
| capital_siege/siege_line | capital_siege | 1 | siege_line | siege | 64.5 | 114.0 | 24.0;210.0;24.0;96.0 |
| foundry_conquest/works | foundry_conquest | 0 | works | line | 44.5 | 164.0 | 46.0;190.0;46.0;145.0;46.0;26.0 |
| foundry_sandbox/works | foundry_sandbox | 0 | works | line | 44.5 | 164.0 | 46.0;190.0;46.0;145.0;46.0;26.0 |
| foundry_siege/siege_line | foundry_siege | 0 | siege_line | siege | 64.5 | 114.0 | 24.0;210.0;24.0;96.0 |
| frostpeak_siege/siege_line | frostpeak_siege | 0 | siege_line | siege | 76.5 | 114.0 | 24.0;210.0;24.0;96.0 |
| ironport_conquest/quay | ironport_conquest | 0 | quay | line | 42.5 | 318.0 | -190.0;106.8;-138.75;106.8;128.0;106.8 |
| ironport_sandbox/quay | ironport_sandbox | 0 | quay | line | 42.5 | 318.0 | -190.0;106.8;-138.75;106.8;128.0;106.8 |
| ironport_siege/siege_line | ironport_siege | 0 | siege_line | siege | 65.0 | 114.0 | 24.0;210.0;24.0;96.0 |
| junglepass_siege/siege_line | junglepass_siege | 0 | siege_line | siege | 69.0 | 111.0 | 24.0;210.0;24.0;96.0 |
| metrocity_conquest/avenue | metrocity_conquest | 0 | avenue | line | 40.5 | 355.28 | 190.0;101.25;128.0;101.25;75.0;101.25;0.0;101.25;-67.5;101.… |
| metrocity_sandbox/avenue | metrocity_sandbox | 0 | avenue | line | 40.5 | 355.28 | 190.0;101.25;128.0;101.25;75.0;101.25;0.0;101.25;-67.5;101.… |
| metrocity_siege/siege_line | metrocity_siege | 0 | siege_line | siege | 65.5 | 114.0 | 24.0;210.0;24.0;96.0 |
| orbitalgate_siege/siege_line | orbitalgate_siege | 0 | siege_line | siege | 63.5 | 114.0 | 24.0;210.0;24.0;96.0 |
| redrock_siege/siege_line | redrock_siege | 0 | siege_line | siege | 68.5 | 106.5 | 24.0;210.0;24.0;96.0 |
| rustyard_conquest/siding | rustyard_conquest | 0 | siding | line | 41.5 | 66.0 | 190.0;11.25;140.0;11.25;124.0;11.25 |
| rustyard_sandbox/siding | rustyard_sandbox | 0 | siding | line | 41.5 | 66.0 | 190.0;11.25;140.0;11.25;124.0;11.25 |
| rustyard_siege/siding | rustyard_siege | 0 | siding | line | 41.5 | 66.0 | 190.0;11.25;140.0;11.25;124.0;11.25 |
| rustyard_siege/siege_line | rustyard_siege | 1 | siege_line | siege | 65.0 | 114.0 | 24.0;210.0;24.0;96.0 |
| veyra_old_quarter_siege/siege_line | veyra_old_quarter_siege | 0 | siege_line | siege | 65.0 | 114.0 | 24.0;210.0;24.0;96.0 |
| whiteout_siege/siege_line | whiteout_siege | 0 | siege_line | siege | 69.5 | 114.0 | 24.0;210.0;24.0;96.0 |

Sheet: 08_ban_do/Ban_do_tag_dia_hinh — Bản đồ: tag địa hình (38788 dòng, 10 cột)

| id | ban_do_id | thu_tu | x0_m | z0_m | x1_m | z1_m | tag |
|---|---|---|---|---|---|---|---|
| ashfield_conquest/0/0 | ashfield_conquest | 0 | -4.0 | -144.0 | 4.0 | -28.0 | ROAD |
| ashfield_conquest/0/1 | ashfield_conquest | 0 | -110.0 | -112.0 | -108.0 | -106.0 | ROAD |
| ashfield_conquest/0/2 | ashfield_conquest | 0 | -112.0 | -110.0 | -110.0 | -108.0 | ROAD |
| ashfield_conquest/0/3 | ashfield_conquest | 0 | -108.0 | -110.0 | -106.0 | -104.0 | ROAD |
| ashfield_conquest/0/4 | ashfield_conquest | 0 | -106.0 | -108.0 | -104.0 | -102.0 | ROAD |
| ashfield_conquest/0/5 | ashfield_conquest | 0 | -104.0 | -106.0 | -102.0 | -100.0 | ROAD |
| ashfield_conquest/0/6 | ashfield_conquest | 0 | -102.0 | -104.0 | -100.0 | -98.0 | ROAD |
| ashfield_conquest/0/7 | ashfield_conquest | 0 | -100.0 | -102.0 | -98.0 | -96.0 | ROAD |
| ashfield_conquest/0/8 | ashfield_conquest | 0 | -98.0 | -100.0 | -96.0 | -94.0 | ROAD |
| ashfield_conquest/0/9 | ashfield_conquest | 0 | -96.0 | -98.0 | -94.0 | -92.0 | ROAD |
| ashfield_conquest/0/10 | ashfield_conquest | 0 | -94.0 | -96.0 | -92.0 | -90.0 | ROAD |
| ashfield_conquest/0/11 | ashfield_conquest | 0 | -92.0 | -94.0 | -90.0 | -88.0 | ROAD |
| ashfield_conquest/0/12 | ashfield_conquest | 0 | -90.0 | -92.0 | -88.0 | -86.0 | ROAD |
| ashfield_conquest/0/13 | ashfield_conquest | 0 | -88.0 | -90.0 | -86.0 | -84.0 | ROAD |
| ashfield_conquest/0/14 | ashfield_conquest | 0 | -86.0 | -88.0 | -84.0 | -82.0 | ROAD |

*15 / 38788 dòng đầu: xem sheet 08_ban_do/Ban_do_tag_dia_hinh.*

Sheet: 08_ban_do/Ban_do_cong_vao — Bản đồ: cổng vào (3200 dòng, 16 cột)

| id | ban_do_id | thu_tu | id_goc | in_x | in_z | kind | path | side | visual_ingress_length |
|---|---|---|---|---|---|---|---|---|---|
| ashfield_conquest/edge4 | ashfield_conquest | 4 | edge4 | 0 | -1 | edge | -45.0;270.0;-45.0;150.0;-45.0;113.0 | N | 157.0 |
| ashfield_conquest/edge5 | ashfield_conquest | 5 | edge5 | 0 | -1 | edge | 15.0;270.0;15.0;150.0;15.0;135.0 | N | 135.0 |
| ashfield_conquest/edge6 | ashfield_conquest | 6 | edge6 | 0 | -1 | edge | 45.0;270.0;45.0;150.0;45.0;141.0 | N | 129.0 |
| ashfield_conquest/edge7 | ashfield_conquest | 7 | edge7 | 0 | -1 | edge | 75.0;270.0;75.0;150.0;75.0;143.0 | N | 127.0 |
| ashfield_conquest/edge8 | ashfield_conquest | 8 | edge8 | 0 | -1 | edge | 105.0;270.0;105.0;150.0;105.0;143.0 | N | 127.0 |
| ashfield_conquest/edge9 | ashfield_conquest | 9 | edge9 | 0 | -1 | edge | 135.0;270.0;135.0;150.0;135.0;141.0 | N | 129.0 |
| ashfield_conquest/edge10 | ashfield_conquest | 10 | edge10 | -1 | 0 | edge | 270.0;-15.0;150.0;-15.0;121.0;-15.0 | E | 149.0 |
| ashfield_conquest/edge11 | ashfield_conquest | 11 | edge11 | -1 | 0 | edge | 270.0;15.0;150.0;15.0;137.0;15.0 | E | 133.0 |
| ashfield_conquest/edge12 | ashfield_conquest | 12 | edge12 | -1 | 0 | edge | 270.0;45.0;150.0;45.0;141.0;45.0 | E | 129.0 |
| ashfield_conquest/edge13 | ashfield_conquest | 13 | edge13 | -1 | 0 | edge | 270.0;75.0;150.0;75.0;143.0;75.0 | E | 127.0 |
| ashfield_conquest/edge14 | ashfield_conquest | 14 | edge14 | -1 | 0 | edge | 270.0;105.0;150.0;105.0;143.0;105.0 | E | 127.0 |
| ashfield_conquest/edge15 | ashfield_conquest | 15 | edge15 | 0 | 1 | edge | -135.0;-270.0;-135.0;-150.0;-135.0;-142.0 | S | 128.0 |
| ashfield_conquest/edge16 | ashfield_conquest | 16 | edge16 | 0 | 1 | edge | -105.0;-270.0;-105.0;-150.0;-105.0;-142.0 | S | 128.0 |
| ashfield_conquest/edge17 | ashfield_conquest | 17 | edge17 | 0 | 1 | edge | -75.0;-270.0;-75.0;-150.0;-75.0;-142.0 | S | 128.0 |
| ashfield_conquest/edge18 | ashfield_conquest | 18 | edge18 | 0 | 1 | edge | -45.0;-270.0;-45.0;-150.0;-45.0;-142.0 | S | 128.0 |

*15 / 3200 dòng đầu: xem sheet 08_ban_do/Ban_do_cong_vao; in 10 / 16 cột; 2 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 08_ban_do/Ban_do_trung_lap — Bản đồ: trung lập (250 dòng, 8 cột)

| id | ban_do_id | thu_tu | kind | x_m | z_m |
|---|---|---|---|---|---|
| ashfield_conquest/0 | ashfield_conquest | 0 | radar | 0.0 | -84.85 |
| ashfield_conquest/1 | ashfield_conquest | 1 | radar | -0.0 | 84.85 |
| ashfield_conquest/2 | ashfield_conquest | 2 | ammo_depot | -74.25 | -10.61 |
| ashfield_conquest/3 | ashfield_conquest | 3 | ammo_depot | 74.25 | 10.61 |
| ashfield_sandbox/0 | ashfield_sandbox | 0 | radar | 0.0 | -84.85 |
| ashfield_sandbox/1 | ashfield_sandbox | 1 | radar | -0.0 | 84.85 |
| ashfield_sandbox/2 | ashfield_sandbox | 2 | ammo_depot | -74.25 | -10.61 |
| ashfield_sandbox/3 | ashfield_sandbox | 3 | ammo_depot | 74.25 | 10.61 |
| ashfield_siege/0 | ashfield_siege | 0 | aa_site | -2.12 | -78.49 |
| ashfield_siege/1 | ashfield_siege | 1 | ammo_depot | -63.64 | 0.0 |
| borderbridge_conquest/0 | borderbridge_conquest | 0 | workshop | -6.36 | -74.25 |
| borderbridge_conquest/1 | borderbridge_conquest | 1 | workshop | 6.36 | 74.25 |
| borderbridge_conquest/2 | borderbridge_conquest | 2 | aa_site | -95.46 | -31.82 |
| borderbridge_conquest/3 | borderbridge_conquest | 3 | aa_site | 95.46 | 31.82 |
| borderbridge_sandbox/0 | borderbridge_sandbox | 0 | workshop | -6.36 | -74.25 |

*15 / 250 dòng đầu: xem sheet 08_ban_do/Ban_do_trung_lap.*

Sheet: 08_ban_do/Vat_the_loai — Loại vật thể (122 dòng, 17 cột)

| id | armor | armour | blocks | blocks_fire | collapse | crush | depth_m | explosion_damage | explosion_delay_s |
|---|---|---|---|---|---|---|---|---|---|
| adobe_house | Structure |  | TRUE |  |  |  | 9.36 |  |  |
| adobe_large | Structure |  | TRUE |  |  |  | 12.09 |  |  |
| ammo_crate | Light |  |  |  |  |  | 1.25 | 90 | 0.2 |
| ammo_dump | Structure |  | TRUE | FALSE |  |  | 5 | 300 | 0.3 |
| apartment | Structure |  | TRUE |  |  |  | 10.4 |  |  |
| artillery_wreck | Heavy | 3 | TRUE | FALSE |  |  | 6.48 |  |  |
| bamboo_clump | Light |  |  |  |  | TRUE | 2.5 |  |  |
| barn | Structure |  | TRUE |  |  |  | 12.48 |  |  |
| barrel | Light |  |  |  |  |  | 1 | 70 | 0.15 |
| barricade | Heavy |  | TRUE | FALSE |  |  | 1.9 |  |  |
| basalt_rock_a | Structure |  | TRUE |  |  |  | 4 |  |  |
| basalt_rock_b | Structure |  | TRUE |  |  |  | 5 |  |  |
| basalt_rock_c | Structure |  | TRUE |  |  |  | 3 |  |  |
| base_gate | Structure | 4 |  |  |  |  | 2 |  |  |
| base_wall | Structure | 4 | TRUE |  | 1.4 |  | 1.2 |  |  |

*15 / 122 dòng đầu: xem sheet 08_ban_do/Vat_the_loai; in 10 / 17 cột; 5 cột khác (và raw_json, nguon): xem sheet.*

### 15b. Đo bản đồ tĩnh

Trạng thái: Một phần — chờ prompt xuất dữ liệu (sheet đo bản đồ tĩnh của spec 4 chưa có trong 08_ban_do; số đo nằm ở báo cáo Docs/checks/map_audit.md, in dưới đây)

Nguồn dữ liệu: 08_ban_do/Ban_do_cu_diem_bai_tha_can_cu. Văn bản: Docs/checks/map_audit.md.

#### Báo cáo `Docs/checks/map_audit.md`

##### Map audit (prompt 30 L8, static, read-only)

Generated by `Tools/audit/map_audit.py` from the map files; the full table is `map_audit.csv`. Nothing was changed and nothing was simulated.

**Limits of a static measure:** it does not show win rates, real traffic jams or flow, the real value of artillery (spotting, minimum ranges, the AI), how the AI picks lanes, how long fights last, or performance. Paths are on the 2 m navigation grid, sightlines on a flat ground with one eye height. Symmetric versions (Conquest, Sandbox) are compared side against side; Siege and the long battlefields are reported by role.

100 files: 0 RED, 100 YELLOW, 0 GREEN.

Thresholds: medianPathDelta ≤ 10 % GREEN, 10-15 % YELLOW, > 15 % RED (symmetric); fewer than 2 lanes RED (symmetric); a drop zone within 40 m of an enemy fixed defence RED; sightline P95 above the tank gun's 32 m YELLOW (information); neutralValueDelta > 10 % YELLOW, > 20 % RED (symmetric).

| Map | Kind | Flags | Lanes | Path delta | Chokes (mand./opt.) | Sightline P95 | Exits | Neutral Δ |
|---|---|---|---|---|---|---|---|---|
| ashfield_conquest | symmetric | YELLOW sightline | 4 | 0.3% | 0/0 | 150.0 | open/open | 1% |
| ashfield_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| ashfield_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 1% |
| ashfield_siege | asymmetric | YELLOW sightline | 4 | by role | 0/2 | 150.0 | open/7 | 50% |
| borderbridge_conquest | symmetric | YELLOW sightline | 3 | 3.1% | 0/0 | 150.0 | open/open | 1% |
| borderbridge_long | asymmetric | YELLOW sightline | 4 | by role | 0/5 | 150.0 | open/4 | - |
| borderbridge_sandbox | symmetric | YELLOW sightline | 3 | by role | 0/0 | 150.0 | open/open | 1% |
| borderbridge_siege | asymmetric | YELLOW sightline | 4 | by role | 0/5 | 150.0 | open/7 | 22% |
| capital_conquest | symmetric | YELLOW sightline | 4 | 4.1% | 0/7 | 150.0 | open/open | 0% |
| capital_long | asymmetric | YELLOW sightline | 4 | by role | 0/9 | 150.0 | open/4 | - |
| capital_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/7 | 150.0 | open/open | 0% |
| capital_siege | asymmetric | YELLOW sightline | 4 | by role | 0/3 | 144.0 | open/7 | 35% |
| coralisles_conquest | symmetric | YELLOW sightline | 4 | 0.0% | 0/0 | 150.0 | open/open | 2% |
| coralisles_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| coralisles_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 2% |
| coralisles_siege | asymmetric | YELLOW sightline | 4 | by role | 0/2 | 150.0 | open/2 | 35% |
| dunebreak_conquest | symmetric | YELLOW sightline | 4 | 0.6% | 0/0 | 150.0 | open/open | 1% |
| dunebreak_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| dunebreak_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 1% |
| dunebreak_siege | asymmetric | YELLOW sightline | 4 | by role | 0/1 | 150.0 | open/7 | 40% |
| emberridge_conquest | symmetric | YELLOW sightline; YELLOW exits | 4 | 0.1% | 0/0 | 150.0 | open/1 | 1% |
| emberridge_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| emberridge_sandbox | symmetric | YELLOW sightline; YELLOW exits | 4 | by role | 0/0 | 150.0 | open/1 | 1% |
| emberridge_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/7 | 49% |
| foundry_conquest | symmetric | YELLOW sightline | 4 | 2.4% | 0/2 | 118.0 | open/open | 1% |
| foundry_long | asymmetric | YELLOW sightline | 4 | by role | 0/3 | 150.0 | open/4 | - |
| foundry_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/2 | 118.0 | open/open | 1% |
| foundry_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 110.0 | open/7 | 29% |
| frostpeak_conquest | symmetric | YELLOW sightline; YELLOW exits | 4 | 0.2% | 0/0 | 150.0 | open/1 | 1% |
| frostpeak_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| frostpeak_sandbox | symmetric | YELLOW sightline; YELLOW exits | 4 | by role | 0/0 | 150.0 | open/1 | 1% |
| frostpeak_siege | asymmetric | YELLOW sightline | 4 | by role | 0/1 | 150.0 | open/7 | 42% |
| greenvale_conquest | symmetric | YELLOW sightline | 4 | 0.4% | 0/0 | 150.0 | open/open | 1% |
| greenvale_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| greenvale_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 1% |
| greenvale_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/7 | 44% |
| hydrodam_conquest | symmetric | YELLOW path delta; YELLOW sightline | 4 | 14.1% | 0/0 | 150.0 | open/open | 0% |
| hydrodam_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| hydrodam_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 0% |
| hydrodam_siege | asymmetric | YELLOW sightline | 4 | by role | 0/2 | 150.0 | open/7 | 40% |
| ironport_conquest | symmetric | YELLOW sightline | 4 | 1.2% | 0/0 | 150.0 | open/2 | 2% |
| ironport_long | asymmetric | YELLOW sightline | 4 | by role | 0/2 | 150.0 | open/4 | - |
| ironport_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/2 | 2% |
| ironport_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/7 | 42% |
| junglepass_conquest | symmetric | YELLOW sightline | 4 | 0.0% | 0/0 | 150.0 | open/open | 1% |
| junglepass_long | asymmetric | YELLOW sightline | 4 | by role | 0/1 | 150.0 | open/4 | - |
| junglepass_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 1% |
| junglepass_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/7 | 53% |
| landingbeach_conquest | symmetric | YELLOW sightline; YELLOW exits | 4 | 5.0% | 0/0 | 150.0 | 1/open | 2% |
| landingbeach_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | 1/4 | - |
| landingbeach_sandbox | symmetric | YELLOW sightline; YELLOW exits | 4 | by role | 0/0 | 150.0 | 1/open | 2% |
| landingbeach_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | 1/7 | 42% |
| launchsite_conquest | symmetric | YELLOW sightline | 4 | 1.0% | 0/0 | 150.0 | open/open | 0% |
| launchsite_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| launchsite_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 0% |
| launchsite_siege | asymmetric | YELLOW sightline | 4 | by role | 0/2 | 150.0 | open/7 | 43% |
| lighthousebay_conquest | symmetric | YELLOW sightline | 4 | 0.8% | 0/1 | 150.0 | open/open | 0% |
| lighthousebay_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| lighthousebay_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/1 | 150.0 | open/open | 0% |
| lighthousebay_siege | asymmetric | YELLOW sightline | 4 | by role | 0/2 | 150.0 | open/7 | 46% |
| metrocity_conquest | symmetric | YELLOW sightline | 4 | 0.8% | 0/0 | 150.0 | open/open | 0% |
| metrocity_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| metrocity_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 0% |
| metrocity_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/7 | 43% |
| openpit_conquest | symmetric | YELLOW sightline | 4 | 4.6% | 0/1 | 134.0 | open/open | 1% |
| openpit_long | asymmetric | YELLOW sightline | 4 | by role | 0/3 | 150.0 | open/4 | - |
| openpit_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/1 | 134.0 | open/open | 1% |
| openpit_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 122.0 | open/7 | 45% |
| orbitalgate_conquest | symmetric | YELLOW sightline | 4 | 1.3% | 0/0 | 150.0 | open/open | 0% |
| orbitalgate_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| orbitalgate_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 0% |
| orbitalgate_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/7 | 47% |
| redrock_conquest | symmetric | YELLOW sightline; YELLOW exits | 4 | 0.0% | 0/1 | 150.0 | 1/open | 1% |
| redrock_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | 1/4 | - |
| redrock_sandbox | symmetric | YELLOW sightline; YELLOW exits | 4 | by role | 0/1 | 150.0 | 1/open | 1% |
| redrock_siege | asymmetric | YELLOW sightline | 4 | by role | 0/1 | 150.0 | 1/7 | 54% |
| rustyard_conquest | symmetric | YELLOW sightline; YELLOW exits | 4 | 0.5% | 0/0 | 150.0 | 1/1 | 1% |
| rustyard_long | asymmetric | YELLOW sightline | 4 | by role | 0/1 | 150.0 | open/4 | - |
| rustyard_sandbox | symmetric | YELLOW sightline; YELLOW exits | 4 | by role | 0/0 | 150.0 | 1/1 | 1% |
| rustyard_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | 1/7 | 48% |
| saltflat_conquest | symmetric | YELLOW sightline | 4 | 1.6% | 0/0 | 150.0 | open/open | 0% |
| saltflat_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| saltflat_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 0% |
| saltflat_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/7 | 43% |
| skyhold_conquest | symmetric | YELLOW sightline; YELLOW exits | 4 | 0.0% | 0/1 | 150.0 | open/1 | 2% |
| skyhold_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| skyhold_sandbox | symmetric | YELLOW sightline; YELLOW exits | 4 | by role | 0/1 | 150.0 | open/1 | 2% |
| skyhold_siege | asymmetric | YELLOW sightline | 4 | by role | 0/1 | 150.0 | open/7 | 42% |
| swamp_conquest | symmetric | YELLOW sightline | 4 | 0.7% | 0/1 | 150.0 | open/open | 1% |
| swamp_long | asymmetric | YELLOW sightline | 4 | by role | 0/1 | 150.0 | open/4 | - |
| swamp_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/1 | 150.0 | open/open | 1% |
| swamp_siege | asymmetric | YELLOW sightline | 4 | by role | 0/3 | 150.0 | open/2 | 44% |
| veyra_old_quarter_conquest | symmetric | YELLOW sightline | 4 | 2.7% | 0/0 | 136.0 | open/open | 0% |
| veyra_old_quarter_long | asymmetric | YELLOW sightline | 4 | by role | 0/1 | 150.0 | open/4 | - |
| veyra_old_quarter_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 136.0 | open/open | 0% |
| veyra_old_quarter_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 136.0 | open/7 | 45% |
| whiteout_conquest | symmetric | YELLOW sightline | 4 | 0.0% | 0/0 | 150.0 | open/open | 0% |
| whiteout_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| whiteout_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 0% |
| whiteout_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/7 | 39% |

Sheet: 08_ban_do/Ban_do_cu_diem_bai_tha_can_cu — Bản đồ: cứ điểm, bãi thả, căn cứ, tường (đếm) (100 dòng, 13 cột)

| id | ban_do | so_cu_diem | so_bai_tha | so_can_cu | so_o_can_cu | so_tuyen_tuong | so_o_phao_dai | so_cong_vao | so_lan_ra_canh |
|---|---|---|---|---|---|---|---|---|---|
| ashfield_conquest | ashfield_conquest | 3 | 2 | 2 | 28 | 4 | 0 | 27 | 8 |
| ashfield_long | ashfield_long | 3 | 2 | 1 | 14 | 5 | 28 | 39 | 7 |
| ashfield_sandbox | ashfield_sandbox | 0 | 2 | 0 | 0 | 0 | 0 | 27 | 8 |
| ashfield_siege | ashfield_siege | 0 | 2 | 1 | 14 | 3 | 30 | 27 | 8 |
| borderbridge_conquest | borderbridge_conquest | 3 | 2 | 2 | 28 | 4 | 0 | 28 | 10 |
| borderbridge_long | borderbridge_long | 3 | 2 | 1 | 14 | 3 | 28 | 42 | 10 |
| borderbridge_sandbox | borderbridge_sandbox | 0 | 2 | 0 | 0 | 0 | 0 | 28 | 10 |
| borderbridge_siege | borderbridge_siege | 0 | 2 | 1 | 14 | 3 | 31 | 29 | 9 |
| capital_conquest | capital_conquest | 3 | 2 | 2 | 28 | 4 | 0 | 39 | 21 |
| capital_long | capital_long | 3 | 2 | 1 | 14 | 4 | 28 | 48 | 17 |
| capital_sandbox | capital_sandbox | 0 | 2 | 0 | 0 | 0 | 0 | 39 | 21 |
| capital_siege | capital_siege | 0 | 2 | 1 | 14 | 3 | 29 | 40 | 20 |
| coralisles_conquest | coralisles_conquest | 3 | 2 | 2 | 28 | 4 | 0 | 28 | 8 |
| coralisles_long | coralisles_long | 3 | 2 | 1 | 14 | 5 | 28 | 39 | 8 |
| coralisles_sandbox | coralisles_sandbox | 0 | 2 | 0 | 0 | 0 | 0 | 28 | 8 |

*15 / 100 dòng đầu: xem sheet 08_ban_do/Ban_do_cu_diem_bai_tha_can_cu; in 10 / 13 cột; 1 cột khác (và raw_json, nguon): xem sheet.*

## Tham khảo ngoài đời và game

Trạng thái: Đã áp (lượt 10; chỉ dữ liệu trong repo, thiếu nguồn ghi NEED_SOURCE).

Nguồn dữ liệu: 08_ban_do/Ban_do_tham_chieu; 08_ban_do/Ban_do_so_sanh_that; 13_tham_chieu_nguon/Nguon_tham_chieu.

### Ban_do_tham_chieu

33 dòng. Độ tin cậy: da_kiem_chung 0, uoc_dinh 0, ban_dau_doan 0, NEED_SOURCE 33. Loại: NEED_SOURCE 33.

- Chưa dòng nào có tham chiếu trong repo (xem 13_tham_chieu_nguon/Thieu_nguon).

Sheet: 08_ban_do/Ban_do_so_sanh_that — Bản đồ: so sánh với thật (1 dòng, 5 cột)

| id | trang_thai | ghi_chu |
|---|---|---|
| khong_co | KHONG_CO | bản đồ không có thông số ngoài đời để đối chiếu |

## Các sheet khác của file

Mọi sheet chưa in ở mục trên (sheet input_<tên> là bản chép từ file khác, không in lại).

### Ban_do_bai_tha

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_bai_tha.

Sheet: 08_ban_do/Ban_do_bai_tha — Bản đồ: bãi thả (200 dòng, 8 cột)

| id | ban_do_id | thu_tu | team | x_m | z_m |
|---|---|---|---|---|---|
| ashfield_conquest/0 | ashfield_conquest | 0 | 0 | -108.75 | -108.75 |
| ashfield_conquest/1 | ashfield_conquest | 1 | 1 | 108.75 | 108.75 |
| ashfield_long/0 | ashfield_long | 0 | 0 | -108.75 | -108.75 |
| ashfield_long/1 | ashfield_long | 1 | 1 | 0.0 | 284.0 |
| ashfield_sandbox/0 | ashfield_sandbox | 0 | 0 | -108.75 | -108.75 |
| ashfield_sandbox/1 | ashfield_sandbox | 1 | 1 | 108.75 | 108.75 |
| ashfield_siege/0 | ashfield_siege | 0 | 0 | -108.75 | -108.75 |
| ashfield_siege/1 | ashfield_siege | 1 | 1 | 108.0 | 108.0 |
| borderbridge_conquest/0 | borderbridge_conquest | 0 | 0 | -108.75 | -108.75 |
| borderbridge_conquest/1 | borderbridge_conquest | 1 | 1 | 108.75 | 108.75 |
| borderbridge_long/0 | borderbridge_long | 0 | 0 | -108.75 | -108.75 |
| borderbridge_long/1 | borderbridge_long | 1 | 1 | 0.0 | 284.0 |
| borderbridge_sandbox/0 | borderbridge_sandbox | 0 | 0 | -108.75 | -108.75 |
| borderbridge_sandbox/1 | borderbridge_sandbox | 1 | 1 | 108.75 | 108.75 |
| borderbridge_siege/0 | borderbridge_siege | 0 | 0 | -108.75 | -108.75 |

*15 / 200 dòng đầu: xem sheet 08_ban_do/Ban_do_bai_tha.*

### Ban_do_can_cu

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_can_cu.

Sheet: 08_ban_do/Ban_do_can_cu — Bản đồ: căn cứ (100 dòng, 9 cột)

| id | ban_do_id | thu_tu | hq_heading_deg | hq_x_m | hq_z_m | team |
|---|---|---|---|---|---|---|
| ashfield_conquest/0 | ashfield_conquest | 0 | 46 | -120.5 | -115.5 | 0 |
| ashfield_conquest/1 | ashfield_conquest | 1 | 226 | 120.5 | 115.5 | 1 |
| ashfield_long/0 | ashfield_long | 0 | 46 | -120.5 | -115.5 | 0 |
| ashfield_siege/0 | ashfield_siege | 0 | 46 | -120.5 | -115.5 | 0 |
| borderbridge_conquest/0 | borderbridge_conquest | 0 | 46 | -122.5 | -111.0 | 0 |
| borderbridge_conquest/1 | borderbridge_conquest | 1 | 226 | 122.5 | 111.0 | 1 |
| borderbridge_long/0 | borderbridge_long | 0 | 46 | -122.5 | -111.0 | 0 |
| borderbridge_siege/0 | borderbridge_siege | 0 | 46 | -122.5 | -111.0 | 0 |
| capital_conquest/0 | capital_conquest | 0 | 46 | -122.5 | -111.0 | 0 |
| capital_conquest/1 | capital_conquest | 1 | 226 | 122.5 | 111.0 | 1 |
| capital_long/0 | capital_long | 0 | 46 | -122.5 | -111.0 | 0 |
| capital_siege/0 | capital_siege | 0 | 46 | -122.5 | -111.0 | 0 |
| coralisles_conquest/0 | coralisles_conquest | 0 | 45 | -120.0 | -116.5 | 0 |
| coralisles_conquest/1 | coralisles_conquest | 1 | 225 | 120.0 | 116.5 | 1 |
| coralisles_long/0 | coralisles_long | 0 | 45 | -120.0 | -116.5 | 0 |

*15 / 100 dòng đầu: xem sheet 08_ban_do/Ban_do_can_cu.*

### Ban_do_can_cu_o

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_can_cu_o.

Sheet: 08_ban_do/Ban_do_can_cu_o — Căn cứ: ô (1396 dòng, 10 cột)

| id | ban_do_can_cu_id | thu_tu | facing | kind | size | x_m | z_m |
|---|---|---|---|---|---|---|---|
| ashfield_conquest/0/0 | ashfield_conquest/0 | 0 | 49 | tower | large | -122.0 | -91.0 |
| ashfield_conquest/0/1 | ashfield_conquest/0 | 1 | 42 | tower | large | -97.0 | -123.0 |
| ashfield_conquest/0/2 | ashfield_conquest/0 | 2 | 52 | tower | medium | -113.0 | -67.0 |
| ashfield_conquest/0/3 | ashfield_conquest/0 | 3 | 48 | tower | medium | -103.0 | -84.0 |
| ashfield_conquest/0/4 | ashfield_conquest/0 | 4 | 42 | tower | medium | -85.0 | -105.0 |
| ashfield_conquest/0/5 | ashfield_conquest/0 | 5 | 49 | tower | small | -94.0 | -66.0 |
| ashfield_conquest/0/6 | ashfield_conquest/0 | 6 | 42 | tower | small | -72.0 | -90.0 |
| ashfield_conquest/0/7 | ashfield_conquest/0 | 7 | 39 | tower | small | -68.0 | -107.0 |
| ashfield_conquest/0/8 | ashfield_conquest/0 | 8 | 36 | tower | small | -64.0 | -130.0 |
| ashfield_conquest/0/9 | ashfield_conquest/0 | 9 | 39 | tower | small | -78.0 | -122.0 |
| ashfield_conquest/0/10 | ashfield_conquest/0 | 10 | 53 | tower | small | -130.0 | -72.0 |
| ashfield_conquest/0/11 | ashfield_conquest/0 | 11 | 53 | utility | medium | -103.0 | -51.0 |
| ashfield_conquest/0/12 | ashfield_conquest/0 | 12 | 33 | utility | medium | -43.0 | -127.0 |
| ashfield_conquest/0/13 | ashfield_conquest/0 | 13 | 57 | utility | medium | -128.0 | -45.0 |
| ashfield_conquest/1/0 | ashfield_conquest/1 | 0 | 229 | tower | large | 122.0 | 91.0 |

*15 / 1396 dòng đầu: xem sheet 08_ban_do/Ban_do_can_cu_o.*

### Ban_do_canh

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_canh.

Sheet: 08_ban_do/Ban_do_canh — Bản đồ: cạnh (658 dòng, 11 cột)

| id | ban_do_id | thu_tu | from | side | to | type |
|---|---|---|---|---|---|---|
| ashfield_conquest/0 | ashfield_conquest | 0 | -150.0 | N | 150.0 | LAND |
| ashfield_conquest/1 | ashfield_conquest | 1 | -150.0 | E | 150.0 | LAND |
| ashfield_conquest/2 | ashfield_conquest | 2 | -150.0 | S | 150.0 | LAND |
| ashfield_conquest/3 | ashfield_conquest | 3 | -150.0 | W | 150.0 | LAND |
| ashfield_long/0 | ashfield_long | 0 | -150.0 | N | 150.0 | LAND |
| ashfield_long/1 | ashfield_long | 1 | -150.0 | E | 330.0 | LAND |
| ashfield_long/2 | ashfield_long | 2 | -150.0 | S | 150.0 | LAND |
| ashfield_long/3 | ashfield_long | 3 | -150.0 | W | 330.0 | LAND |
| ashfield_sandbox/0 | ashfield_sandbox | 0 | -150.0 | N | 150.0 | LAND |
| ashfield_sandbox/1 | ashfield_sandbox | 1 | -150.0 | E | 150.0 | LAND |
| ashfield_sandbox/2 | ashfield_sandbox | 2 | -150.0 | S | 150.0 | LAND |
| ashfield_sandbox/3 | ashfield_sandbox | 3 | -150.0 | W | 150.0 | LAND |
| ashfield_siege/0 | ashfield_siege | 0 | -150.0 | N | 150.0 | LAND |
| ashfield_siege/1 | ashfield_siege | 1 | -150.0 | E | 150.0 | LAND |
| ashfield_siege/2 | ashfield_siege | 2 | -150.0 | S | 150.0 | LAND |

*15 / 658 dòng đầu: xem sheet 08_ban_do/Ban_do_canh.*

### Ban_do_cu_diem

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_cu_diem.

Sheet: 08_ban_do/Ban_do_cu_diem — Bản đồ: cứ điểm (150 dòng, 10 cột)

| id | ban_do_id | thu_tu | id_goc | name | radius_m | x_m | z_m |
|---|---|---|---|---|---|---|---|
| ashfield_conquest/east | ashfield_conquest | 2 | east | depot_east | 11.0 | 56.25 | -86.25 |
| ashfield_conquest/town | ashfield_conquest | 1 | town | town | 16.0 | 0.0 | 0.0 |
| ashfield_conquest/west | ashfield_conquest | 0 | west | depot_west | 11.0 | -56.25 | 86.25 |
| ashfield_long/east | ashfield_long | 2 | east | depot_east | 11.0 | 56.25 | -86.25 |
| ashfield_long/town | ashfield_long | 1 | town | town | 16.0 | 0.0 | 0.0 |
| ashfield_long/west | ashfield_long | 0 | west | depot_west | 11.0 | -56.25 | 86.25 |
| borderbridge_conquest/east | borderbridge_conquest | 2 | east | customs_depot | 13.0 | 60.0 | -84.0 |
| borderbridge_conquest/town | borderbridge_conquest | 1 | town | great_bridge | 14.0 | 0.0 | 0.0 |
| borderbridge_conquest/west | borderbridge_conquest | 0 | west | border_village | 13.0 | -60.0 | 84.0 |
| borderbridge_long/east | borderbridge_long | 2 | east | customs_depot | 13.0 | 60.0 | -84.0 |
| borderbridge_long/town | borderbridge_long | 1 | town | great_bridge | 14.0 | 0.0 | 0.0 |
| borderbridge_long/west | borderbridge_long | 0 | west | border_village | 13.0 | -60.0 | 84.0 |
| capital_conquest/east | capital_conquest | 2 | east | station | 13.0 | 84.0 | -100.0 |
| capital_conquest/town | capital_conquest | 1 | town | palace_square | 16.0 | 0.0 | 0.0 |
| capital_conquest/west | capital_conquest | 0 | west | gardens | 13.0 | -84.0 | 100.0 |

*15 / 150 dòng đầu: xem sheet 08_ban_do/Ban_do_cu_diem.*

### Ban_do_cu_diem_tien_don

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_cu_diem_tien_don.

Sheet: 08_ban_do/Ban_do_cu_diem_tien_don — Cứ điểm: ô tiền đồn (298 dòng, 10 cột)

| id | ban_do_cu_diem_id | thu_tu | facing | kind | size | x_m | z_m |
|---|---|---|---|---|---|---|---|
| ashfield_conquest/east/0 | ashfield_conquest/east | 0 | 339 | tower | medium | 49.0 | -67.0 |
| ashfield_conquest/east/1 | ashfield_conquest/east | 1 | 89 | tower | small | 71.0 | -86.0 |
| ashfield_conquest/town/0 | ashfield_conquest/town | 0 | 344 | tower | medium | -6.0 | 21.0 |
| ashfield_conquest/town/1 | ashfield_conquest/town | 1 | 156 | tower | small | 9.0 | -20.0 |
| ashfield_conquest/west/0 | ashfield_conquest/west | 0 | 159 | tower | medium | -49.0 | 67.0 |
| ashfield_conquest/west/1 | ashfield_conquest/west | 1 | 269 | tower | small | -71.0 | 86.0 |
| ashfield_long/east/0 | ashfield_long/east | 0 | 339 | tower | medium | 49.0 | -67.0 |
| ashfield_long/east/1 | ashfield_long/east | 1 | 89 | tower | small | 71.0 | -86.0 |
| ashfield_long/town/0 | ashfield_long/town | 0 | 344 | tower | medium | -6.0 | 21.0 |
| ashfield_long/town/1 | ashfield_long/town | 1 | 156 | tower | small | 9.0 | -20.0 |
| ashfield_long/west/0 | ashfield_long/west | 0 | 159 | tower | medium | -49.0 | 67.0 |
| ashfield_long/west/1 | ashfield_long/west | 1 | 269 | tower | small | -71.0 | 86.0 |
| borderbridge_conquest/east/0 | borderbridge_conquest/east | 0 | 147 | tower | medium | 69.0 | -98.0 |
| borderbridge_conquest/east/1 | borderbridge_conquest/east | 1 | 13 | tower | small | 64.0 | -67.0 |
| borderbridge_conquest/town/0 | borderbridge_conquest/town | 0 | 210 | tower | medium | -14.0 | -24.0 |

*15 / 298 dòng đầu: xem sheet 08_ban_do/Ban_do_cu_diem_tien_don.*

### Ban_do_dia_danh_mo_hinh

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_dia_danh_mo_hinh.

Sheet: 08_ban_do/Ban_do_dia_danh_mo_hinh — Địa danh: mô hình (69 dòng, 12 cột)

| id | map | id_goc | model | on_play | radius_m | scale | x_m | yaw_deg | z_m |
|---|---|---|---|---|---|---|---|---|---|
| borderbridge_siege/borderbridge.village_church | borderbridge_siege | borderbridge.village_church | church | FALSE | 12.2 | 1.0 | -61.0 | 90.0 | 135.0 |
| capital_conquest/capital.palace | capital_conquest | capital.palace | dress_landmark_palace_dome | FALSE | 15.6 | 1.0 | 135.0 | 90.0 | -27.0 |
| capital_conquest/capital.station | capital_conquest | capital.station | dress_landmark_station_clock | FALSE | 12.5 | 1.0 | 147.0 | 90.0 | -82.0 |
| capital_long/capital.palace | capital_long | capital.palace | dress_landmark_palace_dome | FALSE | 15.6 | 1.0 | 135.0 | 90.0 | -27.0 |
| capital_long/capital.station | capital_long | capital.station | dress_landmark_station_clock | FALSE | 12.5 | 1.0 | 147.0 | 90.0 | -82.0 |
| capital_sandbox/capital.palace | capital_sandbox | capital.palace | dress_landmark_palace_dome | FALSE | 15.6 | 1.0 | 135.0 | 90.0 | -27.0 |
| capital_sandbox/capital.station | capital_sandbox | capital.station | dress_landmark_station_clock | FALSE | 12.5 | 1.0 | 147.0 | 90.0 | -82.0 |
| capital_siege/capital.ministry_tower | capital_siege | capital.ministry_tower | skyscraper | FALSE | 9.9 | 1.0 | -132.0 | 0.0 | 44.0 |
| capital_siege/capital.palace | capital_siege | capital.palace | dress_landmark_palace_dome | FALSE | 15.6 | 1.0 | 135.0 | 90.0 | -27.0 |
| capital_siege/capital.station | capital_siege | capital.station | dress_landmark_station_clock | FALSE | 12.5 | 1.0 | 147.0 | 90.0 | -82.0 |
| coralisles_conquest/coralisles.lighthouse | coralisles_conquest | coralisles.lighthouse | lighthouse | FALSE | 5.1 | 1.0 | 0.0 | 0.0 | -129.0 |
| coralisles_long/coralisles.lighthouse | coralisles_long | coralisles.lighthouse | lighthouse | FALSE | 5.1 | 1.0 | 0.0 | 0.0 | -129.0 |
| coralisles_sandbox/coralisles.lighthouse | coralisles_sandbox | coralisles.lighthouse | lighthouse | FALSE | 5.1 | 1.0 | 0.0 | 0.0 | -129.0 |
| coralisles_siege/coralisles.lighthouse | coralisles_siege | coralisles.lighthouse | lighthouse | FALSE | 5.1 | 1.0 | 75.0 | 0.0 | 51.0 |
| dunebreak_long/dunebreak.north_radar | dunebreak_long | dunebreak.north_radar | radar_dome | FALSE | 5.7 | 1.0 | -82.0 | 0.0 | 111.0 |

*15 / 69 dòng đầu: xem sheet 08_ban_do/Ban_do_dia_danh_mo_hinh.*

### Ban_do_do_tinh

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_do_tinh.

Sheet: 08_ban_do/Ban_do_do_tinh — Bản đồ: đo tĩnh (100 dòng, 45 cột)

| id | doi_xung | co_bao_cao | vung_nav_roi | tiep_can_muc_tieu | duong_toi_muc_tieu_0_m | duong_toi_muc_tieu_1_m | chenh_trung_vi | khoang_cach_cham_tran_m | muc_tieu_toi_muc_tieu_m |
|---|---|---|---|---|---|---|---|---|---|
| ashfield_conquest | symmetric | YELLOW sightline | 0.0 | ok | 152.3 | 152.9 | 0.003 | 146.6 | 103.4 |
| ashfield_long | asymmetric | YELLOW sightline | 0.0 | ok | 190.0 | 343.9 |  | 256.2 | 108.2 |
| ashfield_sandbox | symmetric | YELLOW sightline | 0.0 | ok |  |  |  | 146.6 |  |
| ashfield_siege | asymmetric | YELLOW sightline | 0.0 | ok | 353.1 | 18.5 |  | 168.3 |  |
| borderbridge_conquest | symmetric | YELLOW sightline | 0.0 | ok | 154.2 | 149.5 | 0.031 | 150.7 | 108.4 |
| borderbridge_long | asymmetric | YELLOW sightline | 0.0 | ok | 202.8 | 341.7 |  | 258.0 | 108.4 |
| borderbridge_sandbox | symmetric | YELLOW sightline | 0.0 | ok |  |  |  | 150.7 |  |
| borderbridge_siege | asymmetric | YELLOW sightline | 0.0 | ok | 365.7 | 18.5 |  | 174.6 |  |
| capital_conquest | symmetric | YELLOW sightline | 0.0 | ok | 319.2 | 306.3 | 0.040999999999999995 | 312.7 | 168.9 |
| capital_long | asymmetric | YELLOW sightline | 0.0 | ok | 406.0 | 347.8 |  | 376.7 | 169.3 |
| capital_sandbox | symmetric | YELLOW sightline | 0.0 | ok |  |  |  | 312.7 |  |
| capital_siege | asymmetric | YELLOW sightline | 0.0 | ok | 411.1 | 19.5 |  | 196.7 |  |
| coralisles_conquest | symmetric | YELLOW sightline | 0.0 | ok | 203.4 | 203.5 | 0.0 | 202.7 | 200.3 |
| coralisles_long | asymmetric | YELLOW sightline | 0.0 | ok | 230.4 | 370.6 |  | 269.8 | 206.8 |
| coralisles_sandbox | symmetric | YELLOW sightline | 0.0 | ok |  |  |  | 202.7 |  |

*15 / 100 dòng đầu: xem sheet 08_ban_do/Ban_do_do_tinh; in 10 / 45 cột; 30 cột khác (và raw_json, nguon): xem sheet.*

### Ban_do_duong

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_duong.

Sheet: 08_ban_do/Ban_do_duong — Bản đồ: đường (1287 dòng, 7 cột)

| id | ban_do_id | thu_tu | points | width_m |
|---|---|---|---|---|
| ashfield_conquest/0 | ashfield_conquest | 0 | -11.25;0.0;11.25;0.0 | 26 |
| ashfield_conquest/1 | ashfield_conquest | 1 | -31.875;-31.875;31.875;-31.875;31.875;31.875;-31.875;31.875… | 7 |
| ashfield_conquest/2 | ashfield_conquest | 2 | -78.75;-78.75;78.75;-78.75;78.75;78.75;-78.75;78.75;-78.75;… | 5 |
| ashfield_conquest/3 | ashfield_conquest | 3 | -31.875;0.0;-146.25;0.0 | 6 |
| ashfield_conquest/4 | ashfield_conquest | 4 | 31.875;0.0;146.25;0.0 | 6 |
| ashfield_conquest/5 | ashfield_conquest | 5 | 0.0;31.875;0.0;146.25 | 6 |
| ashfield_conquest/6 | ashfield_conquest | 6 | 0.0;-31.875;0.0;-146.25 | 6 |
| ashfield_conquest/7 | ashfield_conquest | 7 | -108.75;-108.75;-78.75;-78.75 | 5 |
| ashfield_conquest/8 | ashfield_conquest | 8 | 108.75;108.75;78.75;78.75 | 5 |
| ashfield_long/0 | ashfield_long | 0 | -11.25;0.0;11.25;0.0 | 26 |
| ashfield_long/1 | ashfield_long | 1 | -31.88;0.0;-146.25;0.0 | 6 |
| ashfield_long/2 | ashfield_long | 2 | 31.88;0.0;146.25;0.0 | 6 |
| ashfield_long/3 | ashfield_long | 3 | 0.0;31.88;0.0;146.25 | 6 |
| ashfield_long/4 | ashfield_long | 4 | 0.0;-31.88;0.0;-146.25 | 6 |
| ashfield_long/5 | ashfield_long | 5 | -108.75;-108.75;-78.75;-78.75 | 5 |

*15 / 1287 dòng đầu: xem sheet 08_ban_do/Ban_do_duong.*

### Ban_do_goc_canh

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_goc_canh.

Sheet: 08_ban_do/Ban_do_goc_canh — Bản đồ: góc cạnh (658 dòng, 10 cột)

| id | ban_do_id | thu_tu | between | outer | piece | x_m | z_m |
|---|---|---|---|---|---|---|---|
| ashfield_conquest/0 | ashfield_conquest | 0 | LAND;LAND | TRUE | outer_land | -150.0 | 150.0 |
| ashfield_conquest/1 | ashfield_conquest | 1 | LAND;LAND | TRUE | outer_land | 150.0 | 150.0 |
| ashfield_conquest/2 | ashfield_conquest | 2 | LAND;LAND | TRUE | outer_land | 150.0 | -150.0 |
| ashfield_conquest/3 | ashfield_conquest | 3 | LAND;LAND | TRUE | outer_land | -150.0 | -150.0 |
| ashfield_long/0 | ashfield_long | 0 | LAND;LAND | TRUE | outer_land | -150.0 | 330.0 |
| ashfield_long/1 | ashfield_long | 1 | LAND;LAND | TRUE | outer_land | 150.0 | 330.0 |
| ashfield_long/2 | ashfield_long | 2 | LAND;LAND | TRUE | outer_land | 150.0 | -150.0 |
| ashfield_long/3 | ashfield_long | 3 | LAND;LAND | TRUE | outer_land | -150.0 | -150.0 |
| ashfield_sandbox/0 | ashfield_sandbox | 0 | LAND;LAND | TRUE | outer_land | -150.0 | 150.0 |
| ashfield_sandbox/1 | ashfield_sandbox | 1 | LAND;LAND | TRUE | outer_land | 150.0 | 150.0 |
| ashfield_sandbox/2 | ashfield_sandbox | 2 | LAND;LAND | TRUE | outer_land | 150.0 | -150.0 |
| ashfield_sandbox/3 | ashfield_sandbox | 3 | LAND;LAND | TRUE | outer_land | -150.0 | -150.0 |
| ashfield_siege/0 | ashfield_siege | 0 | LAND;LAND | TRUE | outer_land | -150.0 | 150.0 |
| ashfield_siege/1 | ashfield_siege | 1 | LAND;LAND | TRUE | outer_land | 150.0 | 150.0 |
| ashfield_siege/2 | ashfield_siege | 2 | LAND;LAND | TRUE | outer_land | 150.0 | -150.0 |

*15 / 658 dòng đầu: xem sheet 08_ban_do/Ban_do_goc_canh.*

### Ban_do_lien_ket_canh

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_lien_ket_canh.

Sheet: 08_ban_do/Ban_do_lien_ket_canh — Bản đồ: lối ra cạnh (1013 dòng, 17 cột)

| id | ban_do_id | thu_tu | dir_x | dir_z | from | kind | side | width_m | x_m |
|---|---|---|---|---|---|---|---|---|---|
| ashfield_conquest/0 | ashfield_conquest | 0 | -1.0 | 0.0 | -146.25;0.0 | road | W | 6 | -150.0 |
| ashfield_conquest/1 | ashfield_conquest | 1 | 1.0 | 0.0 | 146.25;0.0 | road | E | 6 | 150.0 |
| ashfield_conquest/2 | ashfield_conquest | 2 | 0.0 | 1.0 | 0.0;146.25 | road | N | 6 | 0.0 |
| ashfield_conquest/3 | ashfield_conquest | 3 | 0.0 | -1.0 | 0.0;-146.25 | road | S | 6 | 0.0 |
| ashfield_conquest/4 | ashfield_conquest | 4 | 0 | 1 |  | air | N |  | 0.0 |
| ashfield_conquest/5 | ashfield_conquest | 5 | 1 | 0 |  | air | E |  | 150.0 |
| ashfield_conquest/6 | ashfield_conquest | 6 | 0 | -1 |  | air | S |  | 0.0 |
| ashfield_conquest/7 | ashfield_conquest | 7 | -1 | 0 |  | air | W |  | -150.0 |
| ashfield_long/0 | ashfield_long | 0 | -1.0 | 0.0 | -146.25;0.0 | road | W | 6 | -150.0 |
| ashfield_long/1 | ashfield_long | 1 | 1.0 | 0.0 | 146.25;0.0 | road | E | 6 | 150.0 |
| ashfield_long/2 | ashfield_long | 2 | 0.0 | -1.0 | 0.0;-146.25 | road | S | 6 | 0.0 |
| ashfield_long/3 | ashfield_long | 3 | 0 | 1 |  | air | N |  | 0.0 |
| ashfield_long/4 | ashfield_long | 4 | 1 | 0 |  | air | E |  | 150.0 |
| ashfield_long/5 | ashfield_long | 5 | 0 | -1 |  | air | S |  | 0.0 |
| ashfield_long/6 | ashfield_long | 6 | -1 | 0 |  | air | W |  | -150.0 |

*15 / 1013 dòng đầu: xem sheet 08_ban_do/Ban_do_lien_ket_canh; in 10 / 17 cột; 1 cột khác (và raw_json, nguon): xem sheet.*

### Ban_do_phao_dai_o

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_phao_dai_o.

Sheet: 08_ban_do/Ban_do_phao_dai_o — Pháo đài: ô (1394 dòng, 12 cột)

| id | ban_do_id | thu_tu | facing | place | ring | size | x_m | z_m |
|---|---|---|---|---|---|---|---|---|
| ashfield_long/0 | ashfield_long | 0 | 178 | outer_gate | 2 | small | -16.0 | 226.0 |
| ashfield_long/1 | ashfield_long | 1 | 182 | outer_gate | 2 | small | 14.0 | 226.0 |
| ashfield_long/2 | ashfield_long | 2 | 178 | inner_wall | 3 | small | -16.0 | 274.0 |
| ashfield_long/3 | ashfield_long | 3 | 182 | inner_wall | 3 | small | 14.0 | 274.0 |
| ashfield_long/4 | ashfield_long | 4 | 171 | outer_wall | 2 | small | -60.0 | 225.0 |
| ashfield_long/5 | ashfield_long | 5 | 189 | outer_wall | 2 | small | 58.0 | 225.0 |
| ashfield_long/6 | ashfield_long | 6 | 165 | yard | 2 | small | -128.0 | 256.0 |
| ashfield_long/7 | ashfield_long | 7 | 195 | yard | 2 | small | 126.0 | 256.0 |
| ashfield_long/8 | ashfield_long | 8 | 176 | outer_gate | 2 | medium | -30.0 | 230.0 |
| ashfield_long/9 | ashfield_long | 9 | 183 | inner_wall | 3 | medium | 28.0 | 278.0 |
| ashfield_long/10 | ashfield_long | 10 | 168 | outer_wall | 2 | medium | -82.0 | 227.0 |
| ashfield_long/11 | ashfield_long | 11 | 192 | outer_wall | 2 | medium | 80.0 | 227.0 |
| ashfield_long/12 | ashfield_long | 12 | 188 | yard | 2 | medium | 62.0 | 250.0 |
| ashfield_long/13 | ashfield_long | 13 | 169 | yard | 2 | large | -88.0 | 250.0 |
| ashfield_long/14 | ashfield_long | 14 | 191 | yard | 2 | large | 88.0 | 250.0 |

*15 / 1394 dòng đầu: xem sheet 08_ban_do/Ban_do_phao_dai_o.*

### Ban_do_quan

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_quan.

Sheet: 08_ban_do/Ban_do_quan — Bản đồ: quân đặt sẵn (703 dòng, 11 cột)

| id | ban_do_id | thu_tu | def | heading_deg | start | team | x_m | z_m |
|---|---|---|---|---|---|---|---|---|
| ashfield_conquest/0 | ashfield_conquest | 0 | scout_jeep | 45 | TRUE | 0 | -98.75 | -108.75 |
| ashfield_conquest/1 | ashfield_conquest | 1 | scout_jeep | 45 | TRUE | 0 | -108.75 | -98.75 |
| ashfield_conquest/2 | ashfield_conquest | 2 | ifv | 45 | TRUE | 0 | -102.5 | -102.5 |
| ashfield_conquest/3 | ashfield_conquest | 3 | light_tank | 45 | TRUE | 0 | -111.25 | -111.25 |
| ashfield_conquest/4 | ashfield_conquest | 4 | scout_jeep | 225 | TRUE | 1 | 98.75 | 108.75 |
| ashfield_conquest/5 | ashfield_conquest | 5 | scout_jeep | 225 | TRUE | 1 | 108.75 | 98.75 |
| ashfield_conquest/6 | ashfield_conquest | 6 | ifv | 225 | TRUE | 1 | 102.5 | 102.5 |
| ashfield_conquest/7 | ashfield_conquest | 7 | light_tank | 225 | TRUE | 1 | 111.25 | 111.25 |
| ashfield_long/0 | ashfield_long | 0 | scout_jeep | 45 | TRUE | 0 | -98.75 | -108.75 |
| ashfield_long/1 | ashfield_long | 1 | scout_jeep | 45 | TRUE | 0 | -108.75 | -98.75 |
| ashfield_long/2 | ashfield_long | 2 | ifv | 45 | TRUE | 0 | -102.5 | -102.5 |
| ashfield_long/3 | ashfield_long | 3 | light_tank | 45 | TRUE | 0 | -111.25 | -111.25 |
| ashfield_sandbox/0 | ashfield_sandbox | 0 | light_tank | 45 | TRUE | 0 | -98.75 | -108.75 |
| ashfield_sandbox/1 | ashfield_sandbox | 1 | light_tank | 45 | TRUE | 0 | -108.75 | -98.75 |
| ashfield_sandbox/2 | ashfield_sandbox | 2 | main_battle_tank | 45 | TRUE | 0 | -102.5 | -102.5 |

*15 / 703 dòng đầu: xem sheet 08_ban_do/Ban_do_quan.*

### Ban_do_rail_giao_cat

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_rail_giao_cat.

Sheet: 08_ban_do/Ban_do_rail_giao_cat — Ray: chỗ cắt đường (24 dòng, 13 cột)

| id | ban_do_rail_id | thu_tu | closes | depth_m | id_goc | length_m | s | width_m | x_m |
|---|---|---|---|---|---|---|---|---|---|
| capital_siege/nemesis/x1 | capital_siege/nemesis | 0 |  | 7.0 | x1 | 11.0 | 119.0 | 9.0 | 71.0 |
| capital_siege/siege_line/x1 | capital_siege/siege_line | 0 |  | 18.0 | x1 | 11.0 | 106.0 | 7.0 | 24.0 |
| foundry_conquest/works/x1 | foundry_conquest/works | 0 |  | 12.0 | x1 | 11.0 | 78.0 | 7.0 | 46.0 |
| foundry_conquest/works/x2 | foundry_conquest/works | 1 |  | 12.0 | x2 | 11.0 | 142.0 | 7.0 | 46.0 |
| foundry_sandbox/works/x1 | foundry_sandbox/works | 0 |  | 12.0 | x1 | 11.0 | 78.0 | 7.0 | 46.0 |
| foundry_sandbox/works/x2 | foundry_sandbox/works | 1 |  | 12.0 | x2 | 11.0 | 142.0 | 7.0 | 46.0 |
| foundry_siege/siege_line/x1 | foundry_siege/siege_line | 0 |  | 12.0 | x1 | 11.0 | 98.0 | 7.0 | 24.0 |
| ironport_conquest/quay/x1 | ironport_conquest/quay | 0 |  | 7.0 | x1 | 11.0 | 190.0 | 8.0 | 0.0 |
| ironport_conquest/quay/x2 | ironport_conquest/quay | 1 | FALSE | 7.0 | x2 | 13.9 | 296.8 | 9.07 | 106.8 |
| ironport_sandbox/quay/x1 | ironport_sandbox/quay | 0 |  | 7.0 | x1 | 11.0 | 190.0 | 8.0 | 0.0 |
| ironport_sandbox/quay/x2 | ironport_sandbox/quay | 1 | FALSE | 7.0 | x2 | 13.9 | 296.8 | 9.07 | 106.8 |
| ironport_siege/siege_line/x1 | ironport_siege/siege_line | 0 |  | 9.0 | x1 | 11.0 | 103.12 | 7.0 | 24.0 |
| metrocity_conquest/avenue/x1 | metrocity_conquest/avenue | 0 |  | 7.0 | x1 | 11.0 | 88.75 | 18.0 | 101.25 |
| metrocity_conquest/avenue/x2 | metrocity_conquest/avenue | 1 |  | 7.0 | x2 | 11.0 | 156.25 | 18.0 | 33.75 |
| metrocity_conquest/avenue/x3 | metrocity_conquest/avenue | 2 |  | 7.0 | x3 | 11.0 | 223.75 | 18.0 | -33.75 |
| metrocity_conquest/avenue/x4 | metrocity_conquest/avenue | 3 |  | 18.0 | x4 | 11.0 | 355.28 | 7.0 | -101.25 |
| metrocity_sandbox/avenue/x1 | metrocity_sandbox/avenue | 0 |  | 7.0 | x1 | 11.0 | 88.75 | 18.0 | 101.25 |
| metrocity_sandbox/avenue/x2 | metrocity_sandbox/avenue | 1 |  | 7.0 | x2 | 11.0 | 156.25 | 18.0 | 33.75 |
| metrocity_sandbox/avenue/x3 | metrocity_sandbox/avenue | 2 |  | 7.0 | x3 | 11.0 | 223.75 | 18.0 | -33.75 |
| metrocity_sandbox/avenue/x4 | metrocity_sandbox/avenue | 3 |  | 18.0 | x4 | 11.0 | 355.28 | 7.0 | -101.25 |
| metrocity_siege/siege_line/x1 | metrocity_siege/siege_line | 0 |  | 18.0 | x1 | 11.0 | 108.75 | 7.0 | 24.0 |
| orbitalgate_siege/siege_line/x1 | orbitalgate_siege/siege_line | 0 |  | 10.2 | x1 | 11.17 | 87.16 | 7.0 | 24.0 |
| redrock_siege/siege_line/x1 | redrock_siege/siege_line | 0 |  | 6.53 | x1 | 11.05 | 87.9 | 7.0 | 24.0 |
| veyra_old_quarter_siege/siege_line/x1 | veyra_old_quarter_siege/siege_line | 0 |  | 12.14 | x1 | 11.1 | 100.67 | 7.0 | 24.0 |

*in 10 / 13 cột; 1 cột khác (và raw_json, nguon): xem sheet.*

### Ban_do_trang_tri

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_trang_tri.

Sheet: 08_ban_do/Ban_do_trang_tri — Bản đồ: trang trí (9347 dòng, 9 cột)

| id | ban_do_id | thu_tu | def | rot | x_m | z_m |
|---|---|---|---|---|---|---|
| ashfield_conquest/0 | ashfield_conquest | 0 | fence | 90 | 134.05 | -31.9 |
| ashfield_conquest/1 | ashfield_conquest | 1 | tree |  | -112.5 | 134.05 |
| ashfield_conquest/2 | ashfield_conquest | 2 | tree |  | -121.9 | 107.8 |
| ashfield_conquest/3 | ashfield_conquest | 3 | tree |  | -128.45 | 76.9 |
| ashfield_conquest/4 | ashfield_conquest | 4 | tree |  | -114.4 | 95.6 |
| ashfield_conquest/5 | ashfield_conquest | 5 | tree |  | -117.2 | 116.25 |
| ashfield_conquest/6 | ashfield_conquest | 6 | tree |  | -119.05 | 137.8 |
| ashfield_conquest/7 | ashfield_conquest | 7 | tree |  | -91.9 | 129.4 |
| ashfield_conquest/8 | ashfield_conquest | 8 | tree |  | -134.05 | 115.3 |
| ashfield_conquest/9 | ashfield_conquest | 9 | tree |  | -132.2 | 139.7 |
| ashfield_conquest/10 | ashfield_conquest | 10 | tree |  | -114.4 | 99.4 |
| ashfield_conquest/11 | ashfield_conquest | 11 | tree |  | -108.75 | 113.45 |
| ashfield_conquest/12 | ashfield_conquest | 12 | tree |  | -102.2 | 137.8 |
| ashfield_conquest/13 | ashfield_conquest | 13 | tree |  | -121.9 | 104.05 |
| ashfield_conquest/14 | ashfield_conquest | 14 | tree |  | -134.05 | 120.95 |

*15 / 9347 dòng đầu: xem sheet 08_ban_do/Ban_do_trang_tri.*

### Ban_do_trang_tri_luat

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_trang_tri_luat.

Sheet: 08_ban_do/Ban_do_trang_tri_luat — Trang trí: luật (83 dòng, 8 cột)

| id | khoa | gia_tri_so | gia_tri_chu | don_vi |
|---|---|---|---|---|
| camera.aspects | aspects |  | 1.3333;1.7778;2.2222 |  |
| camera.maxZoomLong | maxZoomLong | 50.0 |  |  |
| camera.maxZoomSquare | maxZoomSquare | 42.0 |  |  |
| camera.pad | pad | 0.15 |  | m |
| camera.reachLongEnd | reachLongEnd | 111.11 |  |  |
| camera.reachLongSide | reachLongSide | 63.45 |  |  |
| camera.reachSquare | reachSquare | 103.68 |  |  |
| camera.ringLongEnd | ringLongEnd | 128.0 |  |  |
| camera.ringLongSide | ringLongSide | 73.0 |  |  |
| camera.ringSquare | ringSquare | 120.0 |  |  |
| camera.rotates | rotates | FALSE |  |  |
| camera.tiltDegrees | tiltDegrees | 52.0 |  |  |
| camera.yawLong | yawLong | -90.0 |  |  |
| camera.yawSquare | yawSquare | -45.0 |  |  |
| edges.corners[0].first | first |  | LAND |  |

*15 / 83 dòng đầu: xem sheet 08_ban_do/Ban_do_trang_tri_luat.*

### Ban_do_tuong

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_tuong.

Sheet: 08_ban_do/Ban_do_tuong — Bản đồ: tuyến tường (279 dòng, 11 cột)

| id | ban_do_id | thu_tu | gate_w | gate_x_m | gate_z_m | owner | radius_m | ring |
|---|---|---|---|---|---|---|---|---|
| ashfield_conquest/0 | ashfield_conquest | 0 | 24.0 | -70.5 | -57.5 | camp0 | 58 | 1 |
| ashfield_conquest/1 | ashfield_conquest | 1 | 24.0 | -86.5 | -87.5 | camp0 | 34 | 2 |
| ashfield_conquest/2 | ashfield_conquest | 2 | 24.0 | 70.5 | 57.5 | camp1 | 58 | 1 |
| ashfield_conquest/3 | ashfield_conquest | 3 | 24.0 | 86.5 | 87.5 | camp1 | 34 | 2 |
| ashfield_long/0 | ashfield_long | 0 | 24.0 | -120.5 | -57.5 | camp0 | 58 | 1 |
| ashfield_long/1 | ashfield_long | 1 | 24.0 | -92.5 | -81.5 | camp0 | 34 | 2 |
| ashfield_long/2 | ashfield_long | 2 | 24.0 | 0.0 | 163.0 | fortress | 142.0 | 1 |
| ashfield_long/3 | ashfield_long | 3 | 24.0 | 0.0 | 209.0 | fortress | 96.0 | 2 |
| ashfield_long/4 | ashfield_long | 4 | 24.0 | 0.0 | 257.0 | fortress | 48.0 | 3 |
| ashfield_siege/0 | ashfield_siege | 0 | 24.0 | -70.5 | -57.5 | camp0 | 58 | 1 |
| ashfield_siege/1 | ashfield_siege | 1 | 24.0 | -86.5 | -87.5 | camp0 | 34 | 2 |
| ashfield_siege/2 | ashfield_siege | 2 | 24.0 | 77.4 | 103.4 | fortress | 47.6 | 2 |
| borderbridge_conquest/0 | borderbridge_conquest | 0 | 24.0 | -52.5 | -47.0 | camp0 | 70 | 1 |
| borderbridge_conquest/1 | borderbridge_conquest | 1 | 24.0 | -88.5 | -83.0 | camp0 | 34 | 2 |
| borderbridge_conquest/2 | borderbridge_conquest | 2 | 24.0 | 52.5 | 47.0 | camp1 | 70 | 1 |

*15 / 279 dòng đầu: xem sheet 08_ban_do/Ban_do_tuong.*

### Ban_do_tuong_doan

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_tuong_doan.

Sheet: 08_ban_do/Ban_do_tuong_doan — Tuyến tường: đoạn (1079 dòng, 12 cột)

| id | ban_do_tuong_id | thu_tu | d | facing | gun | w | x_m | z_m |
|---|---|---|---|---|---|---|---|---|
| ashfield_conquest/0/0 | ashfield_conquest/0 | 0 | 2.0 | 0 | TRUE | 12.0 | -88.5 | -57.5 |
| ashfield_conquest/0/1 | ashfield_conquest/0 | 1 | 12.0 | 90 |  | 2.0 | -62.5 | -67.5 |
| ashfield_conquest/0/2 | ashfield_conquest/0 | 2 | 2.0 | 0 |  | 12.0 | -102.5 | -59.5 |
| ashfield_conquest/0/3 | ashfield_conquest/0 | 3 | 12.0 | 90 |  | 2.0 | -62.5 | -89.5 |
| ashfield_conquest/1/0 | ashfield_conquest/1 | 0 | 2.0 | 0 | TRUE | 12.0 | -98.5 | -75.5 |
| ashfield_conquest/1/1 | ashfield_conquest/1 | 1 | 12.0 | 90 |  | 2.0 | -86.5 | -117.5 |
| ashfield_conquest/1/2 | ashfield_conquest/1 | 2 | 2.0 | 0 |  | 12.0 | -112.5 | -75.5 |
| ashfield_conquest/1/3 | ashfield_conquest/1 | 3 | 12.0 | 90 |  | 2.0 | -86.5 | -131.5 |
| ashfield_conquest/2/0 | ashfield_conquest/2 | 0 | 2.0 | 180 | TRUE | 12.0 | 88.5 | 57.5 |
| ashfield_conquest/2/1 | ashfield_conquest/2 | 1 | 12.0 | 270 |  | 2.0 | 62.5 | 89.5 |
| ashfield_conquest/2/2 | ashfield_conquest/2 | 2 | 2.0 | 180 |  | 12.0 | 102.5 | 59.5 |
| ashfield_conquest/2/3 | ashfield_conquest/2 | 3 | 12.0 | 270 |  | 2.0 | 58.5 | 101.5 |
| ashfield_conquest/3/0 | ashfield_conquest/3 | 0 | 2.0 | 180 | TRUE | 12.0 | 98.5 | 75.5 |
| ashfield_conquest/3/1 | ashfield_conquest/3 | 1 | 12.0 | 270 |  | 2.0 | 86.5 | 117.5 |
| ashfield_conquest/3/2 | ashfield_conquest/3 | 2 | 2.0 | 180 |  | 12.0 | 112.5 | 75.5 |

*15 / 1079 dòng đầu: xem sheet 08_ban_do/Ban_do_tuong_doan.*

### Ban_do_tuyen_bien_doan

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_tuyen_bien_doan.

Sheet: 08_ban_do/Ban_do_tuyen_bien_doan — Tuyến biển: đoạn (108 dòng, 9 cột)

| id | ban_do_id | thu_tu | nut_a | nut_b | a | b |
|---|---|---|---|---|---|---|
| lighthousebay_conquest/0 | lighthousebay_conquest | 0 | lighthousebay_conquest/near_0 | lighthousebay_conquest/near_1 | near_0 | near_1 |
| lighthousebay_conquest/1 | lighthousebay_conquest | 1 | lighthousebay_conquest/near_1 | lighthousebay_conquest/near_2 | near_1 | near_2 |
| lighthousebay_conquest/2 | lighthousebay_conquest | 2 | lighthousebay_conquest/near_2 | lighthousebay_conquest/near_3 | near_2 | near_3 |
| lighthousebay_conquest/3 | lighthousebay_conquest | 3 | lighthousebay_conquest/near_3 | lighthousebay_conquest/near_4 | near_3 | near_4 |
| lighthousebay_conquest/4 | lighthousebay_conquest | 4 | lighthousebay_conquest/near_4 | lighthousebay_conquest/near_5 | near_4 | near_5 |
| lighthousebay_conquest/5 | lighthousebay_conquest | 5 | lighthousebay_conquest/near_5 | lighthousebay_conquest/near_6 | near_5 | near_6 |
| lighthousebay_conquest/6 | lighthousebay_conquest | 6 | lighthousebay_conquest/mid_0 | lighthousebay_conquest/mid_1 | mid_0 | mid_1 |
| lighthousebay_conquest/7 | lighthousebay_conquest | 7 | lighthousebay_conquest/mid_1 | lighthousebay_conquest/mid_2 | mid_1 | mid_2 |
| lighthousebay_conquest/8 | lighthousebay_conquest | 8 | lighthousebay_conquest/mid_2 | lighthousebay_conquest/mid_3 | mid_2 | mid_3 |
| lighthousebay_conquest/9 | lighthousebay_conquest | 9 | lighthousebay_conquest/mid_3 | lighthousebay_conquest/mid_4 | mid_3 | mid_4 |
| lighthousebay_conquest/10 | lighthousebay_conquest | 10 | lighthousebay_conquest/mid_4 | lighthousebay_conquest/mid_5 | mid_4 | mid_5 |
| lighthousebay_conquest/11 | lighthousebay_conquest | 11 | lighthousebay_conquest/mid_5 | lighthousebay_conquest/mid_6 | mid_5 | mid_6 |
| lighthousebay_conquest/12 | lighthousebay_conquest | 12 | lighthousebay_conquest/far_0 | lighthousebay_conquest/far_1 | far_0 | far_1 |
| lighthousebay_conquest/13 | lighthousebay_conquest | 13 | lighthousebay_conquest/far_1 | lighthousebay_conquest/far_2 | far_1 | far_2 |
| lighthousebay_conquest/14 | lighthousebay_conquest | 14 | lighthousebay_conquest/far_2 | lighthousebay_conquest/far_3 | far_2 | far_3 |

*15 / 108 dòng đầu: xem sheet 08_ban_do/Ban_do_tuyen_bien_doan.*

### Ban_do_vat_the

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_vat_the.

Sheet: 08_ban_do/Ban_do_vat_the — Bản đồ: vật thể (89245 dòng, 10 cột)

| id | ban_do_id | thu_tu | def | x_m | z_m |
|---|---|---|---|---|---|
| ashfield_conquest/0 | ashfield_conquest | 0 | fuel_tank | -67.5 | 94.7 |
| ashfield_conquest/1 | ashfield_conquest | 1 | fuel_tank | -56.25 | 100.3 |
| ashfield_conquest/2 | ashfield_conquest | 2 | fuel_tank | -45.0 | 94.7 |
| ashfield_conquest/3 | ashfield_conquest | 3 | water_tower | -52.5 | 119.05 |
| ashfield_conquest/4 | ashfield_conquest | 4 | barrel | -62.8 | 76.9 |
| ashfield_conquest/5 | ashfield_conquest | 5 | barrel | -54.4 | 82.5 |
| ashfield_conquest/6 | ashfield_conquest | 6 | barrel | -67.5 | 77.8 |
| ashfield_conquest/7 | ashfield_conquest | 7 | barrel | -61.9 | 96.55 |
| ashfield_conquest/8 | ashfield_conquest | 8 | barrel | -54.4 | 92.8 |
| ashfield_conquest/9 | ashfield_conquest | 9 | barrel | -57.2 | 90.0 |
| ashfield_conquest/10 | ashfield_conquest | 10 | barrel | -51.55 | 84.4 |
| ashfield_conquest/11 | ashfield_conquest | 11 | barrel | -60.0 | 86.25 |
| ashfield_conquest/12 | ashfield_conquest | 12 | barrel | -50.6 | 90.95 |
| ashfield_conquest/13 | ashfield_conquest | 13 | barrel | -52.5 | 88.1 |
| ashfield_conquest/14 | ashfield_conquest | 14 | barrel | -59.05 | 80.6 |

*15 / 89245 dòng đầu: xem sheet 08_ban_do/Ban_do_vat_the.*

### Ngan_sach_thuc_the

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ngan_sach_thuc_the.

Sheet: 08_ban_do/Ngan_sach_thuc_the — Ngân sách thực thể (20 dòng, 12 cột)

| id | loai_song | lop | pham_vi | gioi_han_ma | dem_ban_do | ghi_chu | nguon_ma | co_gioi_han | uoc_tinh_toi_da |
|---|---|---|---|---|---|---|---|---|---|
| dan_bay | ngan_han | mo_phong | toan_tran |  |  | đạn đang bay: không tìm thấy giới hạn trong Sim/Combat (the… |  | FALSE |  |
| den_nhiet | ngan_han | hien_thi | toan_tran | 4.0 |  | đèn nhiệt (máy yếu LowMax) | Game/Effects/HeatLights.cs:17 | TRUE | 4.0 |
| doan_tuong | song_lau | mo_phong | moi_ban_do |  | so_doan_tuong | đoạn tường của các tuyến tường |  | FALSE | 21.0 |
| duong_ngam | ngan_han | hien_thi | toan_tran | 4.0 |  | đường ngắm | Game/Effects/AimLines.cs:16 | TRUE | 4.0 |
| khoi_lon | ngan_han | hien_thi | toan_tran | 3.0 |  | cột khói lớn cùng lúc (spec 09: tối đa 3) | Game/Effects/ImpactSmoke.cs:22 | TRUE | 3.0 |
| lua_chay | ngan_han | hien_thi | toan_tran | 160.0 |  | đốm lửa trên nền | Game/Effects/FireSpots.cs:34 | TRUE | 160.0 |
| lua_ngan_sach | ngan_han | hien_thi | toan_tran | 8.0 |  | lửa lớn cùng lúc (máy yếu LowCap) | Game/Effects/FireBudget.cs:14 | TRUE | 8.0 |
| may_bay | song_lau | mo_phong | moi_phe | 6.0 |  | TeamEconomy.MaxAircraft, + 1 mỗi bãi đáp nhánh hangar, + co… | Sim/Economy/EconomySystem.cs:107 | TRUE | 6.0 |
| may_bay_sandbox | song_lau | mo_phong | moi_phe | 12.0 |  | Sandbox | Sim/Sandbox/SandboxRules.cs:56 | TRUE | 12.0 |
| nhat_ky_ai | ngan_han | mo_phong | toan_tran | 4000.0 |  | mục nhật ký quyết định AI giữ lại | Sim/AI/DecisionLog.cs:118 | TRUE | 4000.0 |
| o_can_cu | song_lau | mo_phong | moi_ban_do |  | so_o_can_cu | tháp / công trình: ô xây của các căn cứ (mỗi ô tối đa một) |  | FALSE | 28.0 |
| o_phao_dai | song_lau | mo_phong | moi_ban_do |  | so_o_phao_dai | ô pháo đài nhiều lớp |  | FALSE | 31.0 |
| quan_dat_san | song_lau | mo_phong | moi_ban_do |  | so_quan_dat_san | quân đặt sẵn của file bản đồ (không có trần riêng) |  | FALSE | 31.0 |
| tia_laser | ngan_han | hien_thi | toan_tran | 12.0 |  | tia laser cùng lúc | Game/Effects/LaserBeams.cs:35 | TRUE | 12.0 |
| trung_lap | song_lau | mo_phong | moi_ban_do |  | so_trung_lap | điểm trung lập |  | FALSE | 4.0 |
| vat_the | song_lau | mo_phong | moi_ban_do |  | so_vat_the | vật thể phá được / chặn đường |  | FALSE | 2835.0 |
| vom_khien_vat_pham | ngan_han | hien_thi | toan_tran | 4.0 |  | vòm khiên vật phẩm | Game/Effects/EffectsDirector.Shields.cs:24 | TRUE | 4.0 |
| xe_dich | song_lau | mo_phong | moi_phe | 48.0 |  | economy.vehicleCap (input_kinh_te): lớn nhất của các chế độ… |  | TRUE | 48.0 |
| xe_nguoi_choi | song_lau | mo_phong | moi_phe | 32.0 |  | TeamEconomy.MaxVehicles (người chơi giữ mức này) | Sim/Economy/EconomySystem.cs:95 | TRUE | 32.0 |
| xe_sandbox | song_lau | mo_phong | moi_phe | 64.0 |  | Sandbox | Sim/Sandbox/SandboxRules.cs:56 | TRUE | 64.0 |

### Ngan_sach_thuc_the_che_do

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ngan_sach_thuc_the_che_do.

Sheet: 08_ban_do/Ngan_sach_thuc_the_che_do — Ngân sách thực thể theo chế độ (26 dòng, 9 cột)

| id | che_do | phe | xe_toi_da | xe_toi_da_game | may_bay_toi_da | uoc_tinh_song_lau |
|---|---|---|---|---|---|---|
| Assault/dich | Assault | dich | 32 | 32.0 | 6.0 | 91.0 |
| Assault/nguoi_choi | Assault | nguoi_choi | 32.0 | 32.0 | 6.0 | 91.0 |
| BossRush/dich | BossRush | dich | 32 | 32.0 | 6.0 | 91.0 |
| BossRush/nguoi_choi | BossRush | nguoi_choi | 32.0 | 32.0 | 6.0 | 91.0 |
| Campaign/dich | Campaign | dich | 32 | 32.0 | 6.0 | 91.0 |
| Campaign/nguoi_choi | Campaign | nguoi_choi | 32.0 | 32.0 | 6.0 | 91.0 |
| Conquest/dich | Conquest | dich | 32 | 32.0 | 6.0 | 91.0 |
| Conquest/nguoi_choi | Conquest | nguoi_choi | 32.0 | 32.0 | 6.0 | 91.0 |
| Deathmatch/dich | Deathmatch | dich | 32 | 32.0 | 6.0 | 91.0 |
| Deathmatch/nguoi_choi | Deathmatch | nguoi_choi | 32.0 | 32.0 | 6.0 | 91.0 |
| Defend/dich | Defend | dich | 48 | 48.0 | 6.0 | 107.0 |
| Defend/nguoi_choi | Defend | nguoi_choi | 32.0 | 32.0 | 6.0 | 91.0 |
| Endless/dich | Endless | dich | 48 | 48.0 | 6.0 | 107.0 |
| Endless/nguoi_choi | Endless | nguoi_choi | 32.0 | 32.0 | 6.0 | 91.0 |
| KingOfTheHill/dich | KingOfTheHill | dich | 32 | 32.0 | 6.0 | 91.0 |
| KingOfTheHill/nguoi_choi | KingOfTheHill | nguoi_choi | 32.0 | 32.0 | 6.0 | 91.0 |
| Operation/dich | Operation | dich | 48 | 48.0 | 6.0 | 107.0 |
| Operation/nguoi_choi | Operation | nguoi_choi | 32.0 | 32.0 | 6.0 | 91.0 |
| Showdown/dich | Showdown | dich | 32 | 32.0 | 6.0 | 91.0 |
| Showdown/nguoi_choi | Showdown | nguoi_choi | 32.0 | 32.0 | 6.0 | 91.0 |
| Siege/dich | Siege | dich | 48 | 48.0 | 6.0 | 107.0 |
| Siege/nguoi_choi | Siege | nguoi_choi | 32.0 | 32.0 | 6.0 | 91.0 |
| Survival/dich | Survival | dich | 32 | 32.0 | 6.0 | 91.0 |
| Survival/nguoi_choi | Survival | nguoi_choi | 32.0 | 32.0 | 6.0 | 91.0 |
| Weekly/dich | Weekly | dich | 32 | 32.0 | 6.0 | 91.0 |
| Weekly/nguoi_choi | Weekly | nguoi_choi | 32.0 | 32.0 | 6.0 | 91.0 |
