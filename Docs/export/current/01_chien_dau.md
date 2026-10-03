# 01_chien_dau — Chiến đấu

Vũ khí, đạn, phương tiện, thẻ hỗ trợ, trang bị, commander, đội mở màn, ném bom rải thảm.

Gói cân bằng Machine Brigade, commit 0cafe94b, ngày 2026-10-03. Số liệu đầy đủ ở 01_chien_dau.xlsx; file này chỉ nêu luật, giải thích, lý do thiết kế, tham khảo và bảng nhỏ (tối đa 20 dòng, bảng lớn: xem sheet).

## Phương tiện

Chỉ số gốc (hạng 1, chưa trang bị). DPS = sát thương mỗi loạt / chu kỳ bắn, cộng mọi vũ khí, nhân hệ số giáp (phần 10). Hạng thẻ cộng +5% máu và sát thương mỗi hạng (tối đa hạng 10: +45%).

**Nguồn tham khảo.** Dòng "Tham khảo" trên mỗi thẻ (xe, xe tinh nhuệ, tháp, nhánh hạng 7, boss) ghi hệ thống ngoài đời thật và phim hoặc game mà model được dựng theo, lấy từ Tools/docs/unit_refs.json.

![Model thường và model chi tiết (đồ họa Cao) của 12 xe phổ biến nhất.](images/01_chien_dau_shots_hd.png)

*Hình: Model thường và model chi tiết (đồ họa Cao) của 12 xe phổ biến nhất. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

### Miêu tả, hình dạng và mở khóa

Miêu tả: dòng Cách đánh và Mạnh / yếu của thẻ Hướng dẫn trong game. Hình dạng: cột "Hình dạng (cho AI vẽ)" của file cân bằng (sheet Phương tiện, Công trình, Boss), bản mô tả để dựng model (Tools/docs/unit_sheet.json).

### Boss (41)

Bảng 41 dòng: số liệu đầy đủ ở các sheet của mục này trong file xlsx cùng tên.

Sheet 01_chien_dau/Xe_bo_phan — Xe: bộ phận (6 dòng, 17 cột)

| id | xe_id | thu_tu | armour | at_x_m | at_y_m | at_z_m | hp | id_goc | kind |
|---|---|---|---|---|---|---|---|---|---|
| sea_corvette/ciws | sea_corvette | 1 | 2 | 0 | -6.5 | 7.0 | 0.12 | ciws | ciws |
| sea_corvette/gun | sea_corvette | 0 | 2 | 0 | 9 | 4.2 | 0.14 | gun | gun |
| sea_cruiser/ciws_aft | sea_cruiser | 3 | 2 | -2.2 | -6.1 | 5.9 | 0.1 | ciws_aft | ciws |
| sea_cruiser/ciws_fore | sea_cruiser | 2 | 2 | 2.2 | 4.3 | 6.6 | 0.1 | ciws_fore | ciws |
| sea_cruiser/turret_aft | sea_cruiser | 1 | 3 | 0 | -11.5 | 4.0 | 0.12 | turret_aft | gun |
| sea_cruiser/turret_fore | sea_cruiser | 0 | 3 | 0 | 13.7 | 4.0 | 0.12 | turret_fore | gun |

*In 10 / 17 cột; 5 cột khác: xem sheet.*

Sheet 01_chien_dau/Xe_ten_lua — Xe: tên lửa mang (3 dòng, 8 cột)

| id | xe_id | thu_tu | ammo | reload_s | weapon |
|---|---|---|---|---|---|
| ifv/0 | ifv | 0 | 2 | 20 | atgm |
| light_tank/0 | light_tank | 0 | 2 | 25 | gun_launched_atgm |
| titan_tank/0 | titan_tank | 0 | 4 | 30 | atgm |

Sheet 01_chien_dau/Nhanh_xe — Nhánh quân (4 dòng, 4 cột)

| id | lop |
|---|---|
| Air | Helicopter;Plane |
| Armor | Tank;Heavy;TankHunter |
| Artillery | Artillery |
| Light | Light;Scout;AntiAir;Support |

Sheet 01_chien_dau/Tinh_nhue_luat — Luật tinh nhuệ (20 dòng, 8 cột)

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

Sheet 01_chien_dau/May_bay_so_phat — Máy bay: số phát để hạ (14 dòng, 15 cột)

| id | mau_hp | giap | sat_thuong_phat_stinger | sat_thuong_phat_stinger_game | so_phat_stinger | sat_thuong_phat_buk | sat_thuong_phat_buk_game | so_phat_buk | sat_thuong_phat_ten_lua_tiem_kich |
|---|---|---|---|---|---|---|---|---|---|
| attack_helicopter | 2219.8 | 1 | 221.0 | 221.0 | 11.0 | 416.0 | 416.0 | 6.0 | 382.2 |
| attack_jet | 2479.4 | 2 | 187.85 | 187.85 | 14.0 | 416.0 | 416.0 | 6.0 | 382.2 |
| drop_pod | 352.0 | 1 | 221.0 | 221.0 | 2.0 | 416.0 | 416.0 | 1.0 | 382.2 |
| fighter_jet | 1480.6 | 0 | 221.0 | 221.0 | 7.0 | 416.0 | 416.0 | 4.0 | 382.2 |
| heavy_bomber | 4529.8 | 0 | 221.0 | 221.0 | 21.0 | 416.0 | 416.0 | 11.0 | 382.2 |
| recon_drone | 840.4 | 0 | 221.0 | 221.0 | 4.0 | 416.0 | 416.0 | 3.0 | 382.2 |
| scout_heli | 1139.6 | 0 | 221.0 | 221.0 | 6.0 | 416.0 | 416.0 | 3.0 | 382.2 |
| sky_gunship | 4899.4 | 0 | 221.0 | 221.0 | 23.0 | 416.0 | 416.0 | 12.0 | 382.2 |
| stealth_bomber | 2640.0 | 0 | 221.0 | 221.0 | 12.0 | 416.0 | 416.0 | 7.0 | 382.2 |
| stealth_fighter | 1339.8 | 0 | 221.0 | 221.0 | 7.0 | 416.0 | 416.0 | 4.0 | 382.2 |
| stealth_naval_strike | 2019.6 | 0 | 221.0 | 221.0 | 10.0 | 416.0 | 416.0 | 5.0 | 382.2 |
| strike_drone | 1331.0 | 0 | 221.0 | 221.0 | 7.0 | 416.0 | 416.0 | 4.0 | 382.2 |
| swarm_carrier | 2400.2 | 1 | 221.0 | 221.0 | 11.0 | 416.0 | 416.0 | 6.0 | 382.2 |
| twin_rotor_gunship | 4670.6 | 1 | 221.0 | 221.0 | 22.0 | 416.0 | 416.0 | 12.0 | 382.2 |

*In 10 / 15 cột; 3 cột khác: xem sheet.*

Sheet 01_chien_dau/Do_ben — Hệ số độ bền (2 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so |
|---|---|---|---|
| bosses | toughness | bosses | 0.85 |
| vehicles | toughness | vehicles | 2.2 |

Bảng đầy đủ: xem sheet `Xe` (79 dòng), `Xe_vu_khi` (76 dòng), `Ky_nang` (22 dòng).

## Bảng DPS tổng hợp

### Giá trị thực chiến

DPS lý thuyết (phần 9) đã sửa để tính đủ loạt bắn, băng đạn, thời gian thay băng, nạp của bệ phóng và số bom/tên lửa mỗi lần đầy đạn. Giá trị thực chiến đo trong mô phỏng: mỗi xe hạng 1, không trang bị, đánh các nhóm mục tiêu chuẩn (cụm xe nhẹ, cụm xe tăng, công sự có tháp, máy bay) trong khoảng 90 giây từ lúc tiếp đất, có và không có phòng không đối phương; tính cả thời gian không bắn (di chuyển, xoay tháp, nạp đạn, bay vòng, bị pháo sáng và APS chặn). Giá trị = sát thương thực × hệ số sống sót / CP.

Trong ngoặc: bao nhiêu lần DPS lên một xe. **Hỗ trợ / CP** (E2): giá trị hỗ trợ của xe hỗ trợ, bảng dưới.

Số đo: `combat_value_pt6_after_summary.tsv`; chỉ các thẻ còn trong roster, CP theo dữ liệu hiện tại.

### Giá trị hỗ trợ (E2)

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

Sheet 01_chien_dau/Hoi_quy — Hồi quy theo CP (12 dòng, 5 cột)

| id | gia_tri | y_nghia |
|---|---|---|
| dps_he_so | 33.75476093962859 | hệ số a của DPS theo CP |
| dps_so_mu | 0.38901176007751764 | số mũ b của DPS theo CP |
| mau_he_so | 236.7752654550339 | hệ số a của máu theo CP |
| mau_so_mu | 0.8437618680696132 | số mũ b của máu theo CP |
| n_dps | 49.0 | số xe có DPS > 0 |
| n_mau | 50.0 | số xe trong hồi quy máu |
| trung_vi_dps_tren_cp_9_15 | 5.509669893724608 | trung vị DPS / CP, dải 9-15 |
| trung_vi_dps_tren_cp_ge16 | 5.224377625201938 | trung vị DPS / CP, dải >=16 |
| trung_vi_dps_tren_cp_le8 | 13.75 | trung vị DPS / CP, dải <=8 |
| trung_vi_mau_tren_cp_9_15 | 148.7 | trung vị máu / CP, dải 9-15 |
| trung_vi_mau_tren_cp_ge16 | 150.0125 | trung vị máu / CP, dải >=16 |
| trung_vi_mau_tren_cp_le8 | 189.9333333333333 | trung vị máu / CP, dải <=8 |

Bảng đầy đủ: xem sheet `Xe_suy_ra` (79 dòng), `Hoi_quy_du_lieu` (50 dòng).

## Vũ khí và bảng sát thương

### Hệ số sát thương theo loại đạn và loại giáp

Bảng hiệu quả và ký hiệu ✓ ~ ✕ của từng xe nằm ở thẻ xe (phần 8).

Giáp có hướng (giáp mặt trước dày hơn hông/sau), đạn lệch theo tầm và chuyển động, pháo có tầm tối thiểu. Máy bay có pháo sáng, xe có hệ thống đánh chặn chủ động (APS) chặn tên lửa/drone, tàng hình chỉ lộ ở 40% tầm nhìn khi không bắn. Ký hiệu: ✓ hệ số từ 0.6 trở lên, ~ từ 0.12, ✕ thấp hơn (cùng ngưỡng với giao diện trong game).

### Khắc chế: phòng vệ chặn loại đạn nào

| Phòng vệ | Chặn hoặc giảm | Không chặn |
|---|---|---|
| Giáp phản ứng nổ (mô-đun) | Nổ lõm: giảm 40% (Sử thi) / 55% (Huyền thoại) một phát; đầu nổ song song xuyên qua | Động năng, nổ mạnh, mọi loại khác; mìn |
| Khối phản ứng nổ (dòng đặc biệt) | Nổ lõm: nửa một phát, mỗi lần một khối | Đạn động năng |
| Lồng chắn (Slat Cage, lưới chắn; mái che của xe rùa trước drone) | Phần nổ lõm của rốc-két, tên lửa và drone | Đạn động năng, đạn pháo HEAT, nổ nhiệt áp, mìn |
| APS (Trophy, phòng thủ điểm) | Tên lửa, drone, rốc-két bắn thẳng (laser phòng thủ điểm và C-RAM thêm rốc-két pháo binh; C-RAM một phần đạn pháo) | Đạn pháo xe tăng, đạn súng, tia năng lượng; laser phòng thủ điểm khi ở trong khói hoặc bắn vào khói |
| Pháo sáng | Tên lửa (theo độ kháng pháo sáng của đầu dò) | Drone, đạn súng, đạn phòng không, tia năng lượng |
| Khói | 80% sát thương của tia năng lượng bắn vào hoặc bắn ra | Mọi loại khác |
| Gây nhiễu | Đạn dẫn đường (tên lửa, drone) bay lệch | Đạn không dẫn đường, tia năng lượng |
| Khiên (xe mang khiên, tháp khiên) | Mọi phát trúng quân ở trong vòm, tới khi khiên vỡ | Năng lượng |

### Nhịp bắn, nạp đạn, đường đạn và di chuyển

Đọc thẳng từ dữ liệu game. **Viên/s** là nhịp khi đang bắn (trong một loạt, hoặc giữa hai phát). **Xả** là thời gian hết một băng hay một loạt. **Nghỉ/nạp** là thời gian thay băng hay nghỉ giữa hai loạt. **Bệ phóng** là số lượt bắn trước khi phải nạp lại cả bệ. **TB viên/s** tính cả thời gian nghỉ và nạp.

### Đường đạn

★: vũ khí đổi số trong lần sửa tổng hợp (so với commit 07444b14). Cỡ (mm) chỉ cho súng, pháo, cối, rốc-két; đầu nổ (kg) cho tên lửa, bom, drone. Nhịp ngoài đời: tối đa / duy trì (phát mỗi phút một nòng, nguồn ở bảng A8). DPS duy trì: một mục tiêu, cả nạp, hệ số của xe mang.

### Kích thước đạn (55 model)

Kích thước model đạn nhân tỷ lệ của vũ khí (projectileScale).

### Tầm nổ

Bán kính nổ lan (m) của mọi bom, tên lửa, rốc-két, đạn pháo và drone; của các thẻ hỗ trợ hỏa lực; của đòn lớn của boss; và của vụ nổ khi xe, tháp, boss bị phá. "Trúng trực tiếp" là quả chỉ gây sát thương cho mục tiêu nó trúng. Sát thương là mỗi phát, trước giáp.

### DPS theo cấp giáp, tên lửa, kích thước và siêu vũ khí

### DPS theo cấp giáp (234 vũ khí)

Mặt trúng là mặt trước ở cấp đó. Thưởng theo lớp giáp (ví dụ phá công sự) tính luôn; thưởng theo loại xe, đứng yên hay đánh sườn ghi ở thẻ xe.

### Tên lửa: tốc độ bay và thời gian bay (61)

Tốc độ bay (m/s) và thời gian bay tới tầm xa nhất (tầm / tốc độ; tên lửa dẫn đường bay một thời gian định lúc phóng và trúng nơi mục tiêu đang đứng khi tới). Cột nhanh hơn: tốc độ tên lửa phòng không so với máy bay nhanh nhất trong game (60 m/s; file cân bằng nhắm 1,2–1,5 lần mục tiêu nhanh nhất cần bắt).

### Kích thước model theo dữ liệu (151 đơn vị)

Thân va chạm: dài và rộng.

### Kích thước đạn theo dữ liệu (54 vũ khí)

Game vẽ model đạn khớp chiều dài này.

Bảng 54 dòng: số liệu đầy đủ ở các sheet của mục này trong file xlsx cùng tên.

### Siêu vũ khí của boss chủ lực (16)

Mỗi siêu vũ khí có âm cảnh báo riêng. Số ở đây là số gốc; trong trận cộng hệ số của cấp boss chủ lực (sát thương ×1,2, hồi ×0,85) và của độ khó.

| Boss | Siêu vũ khí | Gồm | Hồi | Cảnh báo | Cách né | Cách ngắt |
|---|---|---|---|---|---|---|
| **Bastion · Pháo đài** | **Pháo cối 420 mm** Một quả cối 420 mm: 2.000 trong lõi 10 m, còn 40% tới rìa 20 m, gấp đôi lên công trình và tháp; vòng đỏ báo trước 4 giây. Cứ 45 giây. | loạt nổ, 1 × 2.000, nổ 10 m | 45 s | 4 s | Ra khỏi vòng đỏ, hoặc giữ quân dưới vòm của máy phát khiên: vòm hấp thụ được vụ nổ. | Phá khẩu cối: mất luôn đòn này (tới lần tự vá duy nhất của nó). |
| **Behemoth · Quái vật thép** | **Loạt pháo chính dồn** Ba loạt, mỗi loạt hai quả 152 mm nổ mạnh, mỗi quả 600, rải trong vòng tròn bán kính 14 m: mỗi quả rơi vào vòng đỏ riêng (lõi 8,5 m đủ sát thương, rìa 17 m còn 40%), vạch trước… | loạt nổ, 6 × 600, nổ 8,5 m, trong vòng 14 m | 45 s | 3,5 s | Bước ra khỏi sáu vòng tròn: mỗi vụ nổ lan 8 m. | Phá pháo chính trong lúc cảnh báo. |
| **Jötunn · Pháo đài di động** | **Loạt pháo 203 mm** Bốn quả 203 mm, mỗi quả 900 (lõi 10 m, rìa 20 m còn 40%), rải trong vòng tròn bán kính 14 m, mỗi lựu pháo hai quả; cảnh báo 4 giây. Cứ 50 giây. | loạt nổ, 4 × 900, nổ 10 m, trong vòng 14 m | 50 s | 4 s | Rời khỏi vòng, hoặc núp dưới vòm khiên: khiên hấp thụ được. | Phá một lựu pháo: mỗi khẩu góp hai trong bốn quả. |
| **Leviathan · Thiết giáp hạm** | **Loạt bắn mạn chín nòng** Chín quả đạn 406 mm, mỗi quả 950 (lõi 12 m, rìa 20 m còn 40%), từ ba tháp pháo chính rải theo dải 60 × 12 m qua căn cứ, mạnh hơn một phần ba lên công trình; cảnh báo 4 giây… | dải bom, 9 × 950, nổ 12 m, dải 60 × 12 m | 50 s | 4 s | Đưa quân ra khỏi dải đánh dấu; đạn pháo không bắn hạ được, nên hãy dàn quân ra. | Phá một tháp pháo chính trong lúc cảnh báo (giáp cấp 4: xe diệt tăng, pháo binh, bom): mỗi tháp bị phá bớt ba quả đạn. |
| **Matriarch · Tàu mẹ drone** | **Bom trượt hạng nặng** Một quả bom trượt hạng nặng từ khoang bom: 1.600 trong lõi 16 m, còn 40% tới rìa 20 m, gấp đôi lên công trình và tháp; bom lượn chậm tới vòng đánh dấu, ít nhất 3 giây. Cứ 45 g… | tên lửa, 1 × 1.600, nổ 16 m, 250 máu, bắn hạ được | 45 s | 3,5 s | Chạy ra khỏi vòng; khi khoang bom mở, phòng không trúng tàu mẹ mạnh hơn 30%. | Phá khoang bom, hoặc bắn hạ quả bom khi nó lượn (máu 250): phòng không, C-RAM, la-de PK. |
| **Moloch · Nhà máy di động** | **Xả xưởng** Cửa xưởng mở 4 giây, rồi mọi cửa cùng xả: sáu xe một lúc, kèm tám phát pháo 152 mm nổ mạnh (mỗi phát 350, lõi 6 m, rìa 12 m còn 40%) vào cụm quân gần nhất. Cứ 50 giây. | thả quân, 6 xe; loạt nổ, 8 × 350, nổ 6 m, trong vòng 12 m | 50 s | 4 s | Đưa cụm quân ra khỏi vùng đánh dấu; sẵn sàng đón thêm sáu xe. | Phá một cửa xưởng lúc cảnh báo: chỉ ra một nửa; phá cả hai thì chỉ còn loạt pháo. |
| **Nemesis · Đoàn tàu tên lửa** | **Tên lửa Tận thế** Bốn giây dựng bệ phóng, rồi một tên lửa nhiệt áp bay vào HQ hoặc cụm quân lớn nhất, có đồng hồ bay (6 giây, xa hơn thì lâu hơn): 3.500 trong lõi 18 m, còn 40% tới rìa 20 m, mạnh h… | tên lửa, 1 × 3.500, nổ 18 m, 600 máu, bắn hạ được | 50 s | 4 s | Dàn quân ra khỏi điểm rơi được đánh dấu trước khi hết giờ. | Phá bệ phóng trong lúc dựng, hoặc bắn hạ tên lửa trên đường bay (máu 600): khẩu đội PAC-3 và Vòm Sắt, cùng mọi phòng không, C-RAM hay la-de PK bên dưới. |
| **Kronos · Máy xúc mỏ** | **Quét gầu** Bánh gầu quét cung 120° dài 25 m phía trước: khoảng 2.500 động năng (xuyên cao) mỗi đơn vị, gấp đôi lên công trình và tháp. Cứ 45 giây. | quét hình quạt, 120° × 25 m, 2.500 | 45 s | 4 s | Ra khỏi cung đánh dấu phía trước; đánh vào hông và sau. | Phá cần gầu (lúc cảnh báo hoặc trước đó). |
| **Monster · Pháo tự hành 800 mm** | **Đạn 800 mm** Một quả đạn 800 mm: 4.000 trong lõi 20 m, còn 40% tới rìa 20 m, nặng gấp đôi với công trình; nòng nâng từ từ, vòng đỏ hiện 4 giây. Mỗi 50 giây. | loạt nổ, 1 × 4.000, nổ 20 m | 50 s | 4 s | Ra khỏi vòng đỏ; vòng rất rộng nên đi sớm. | Phá khẩu cối (nòng): mất luôn phát đạn. |
| **Typhon · Tàu ngầm tên lửa** | **Phóng tên lửa từ dưới nước** Sáu tên lửa vào căn cứ ta: mỗi quả khoảng 700 nổ mạnh (lõi 9 m, rìa 18 m còn 40%), gấp đôi lên công trình; sau 4 giây cảnh báo có đồng hồ bay. Cứ 50 giây. | tên lửa, 6 × 700, nổ 9 m, 250 máu, bắn hạ được | 50 s | 4 s | Đưa quân ra khỏi các điểm đánh dấu; tháp không di chuyển được nên hãy che chắn. | Phá cửa ống phóng lúc cảnh báo (cửa lộ trên mặt nước), hoặc bắn hạ tên lửa (mỗi quả 250 máu). |
| **Kraken · Tàu sân bay** | **Đợt không kích** Mười hai quả bom, mỗi quả 400 (lõi 9 m, rìa 18 m còn 40%), thành dải 90 × 14 m theo hướng tàu; cảnh báo 4 giây. Mỗi 50 giây. | dải bom, 12 × 400, nổ 9 m, dải 90 × 14 m | 50 s | 4 s | Bước ngang ra khỏi dải đỏ. | Phá boong cất cánh trong lúc cảnh báo: đợt không kích và máy bay đều dừng. |
| **Roc · Khí cầu chỉ huy** | **Rải thảm** Mười sáu quả bom 250 kg, mỗi quả 400 (lõi 7 m, rìa 14 m còn 40%), thành dải 80 × 12 m theo đường bay; cảnh báo 4 giây. Cứ 50 giây. | dải bom, 16 × 400, nổ 7 m, dải 80 × 12 m | 50 s | 4 s | Bước ngang ra khỏi dải, tránh khỏi đường bay của nó. | Phá khoang bom. |
| **Garuda · Cánh bay ném bom khổng lồ** | **Rải thảm** Hai mươi quả bom, mỗi quả 350 (lõi 7 m, rìa 14 m còn 40%), thành dải 100 × 14 m theo đường bay; cảnh báo 4 giây. Mỗi 50 giây. | dải bom, 20 × 350, nổ 7 m, dải 100 × 14 m | 50 s | 4 s | Bước ngang ra khỏi dải. | Phá khoang bom. |
| **Daedalus · Tàu đổ bộ quỹ đạo** | **Đổ bộ ồ ạt từ quỹ đạo** Tám khoang cùng rơi vào một cụm quân: mỗi khoang chạm đất gây 600 động năng (xuyên cao, lõi 6 m, rìa 12 m còn 40%) rồi thả một xe; cảnh báo 4 giây. Cứ 50 giây. | loạt nổ, 8 × 600, nổ 6 m, trong vòng 12 m | 50 s | 4 s | Tản cụm quân bị đánh dấu ra; giáp dày cũng không cứu được. | Phá một cửa thả khoang lúc cảnh báo: chỉ còn bốn khoang rơi. |
| **Icarus · Phi thuyền quỹ đạo** | **Mưa thanh vonfram** Bảy thanh vonfram rơi xuống các cụm quân, ưu tiên xe tăng giáp dày, từ vệ tinh nó để lại trên quỹ đạo: 1.800 động năng mỗi thanh, xuyên rất cao, bán kính 7 m, có 4 giây cột sáng… | thanh tungsten từ vệ tinh, 7 × 1.800, nổ 7 m; từ pha 3: 9 phát, hồi 45 s | 45 s | 4 s | Ra khỏi các vòng tròn; khói và APS không chặn được. Vòm khiên hấp thụ một phần sát thương trong lúc còn hoạt động. | Phá ăng-ten liên kết vệ tinh trong lúc cảnh báo để hủy thanh đang rơi; phá hẳn thì hết mưa thanh vonfram cho tới khi nó tự vá lại. Ăng-ten bắn được ở tầng cao, tầng thấp, và cả khi đã rơi xuống đất. |
| **Hyperion · Trạm gương quỹ đạo** | **Tia mặt trời** Một tia đốt dải 70 × 6 m trong 4 giây, 500 mỗi giây; cảnh báo 4 giây. Mỗi 50 giây. | dải bom, 4 × 500, nổ 3 m, dải 70 × 6 m | 50 s | 4 s | Rời ngay dải hẹp. | Phá tia la-de chính trong lúc cảnh báo. |

### Đạn thay thế (hai loại đạn)

Nhịp bắn, tầm và băng đạn vẫn là của súng; chỉ loại sát thương, xuyên, sát thương, nổ lan và dạng đạn đổi. Cột cuối là đạn gốc của súng (sát thương / nổ lan m). Biểu tượng đổi đạn nằm trên ô vũ khí của thẻ, trang chi tiết xe và bảng hiệu ứng. Chưa cân bằng lại: số theo file Excel và số của súng.

### Hệ số sát thương, pháo sáng và APS của xe

Máu hiển thị = máu dữ liệu × độ lì (2,2). Hệ số sát thương nhân mọi vũ khí của xe, không sửa vũ khí dùng chung.

### Pháo sáng (số lần dự trữ)

Hồi một lần khi ở vòng chờ, nạp đầy khi về Bãi đáp hoặc sở chỉ huy. Mồi bẫy nhiệt: +1 lần, hồi nhanh hơn 25%, chỉ cho đơn vị đã có pháo sáng.

### APS

SELF_APS chỉ chặn tên lửa dẫn đường, drone, rốc-két bắn thẳng. Trophy: NONE không gắn; RETROFIT_ELIGIBLE 2 lần, hồi 20 s; BUILT_IN +1 lần, hồi ×0,75. Boss và tháp giữ số riêng.

| Thực thể | Khả năng | Chế độ | Lần / hồi / bán kính |
|---|---|---|---|
| Tăng chủ lực | RetrofitEligible | tự suy ra | — |
| Siêu tăng | BuiltIn | tự suy ra | 3 / 10 s / 20 m |
| Xe la-de phòng không | — | PointDefense | 1 / 0.8 s / 30 m |
| headquarters.shield | — | tự suy ra | 6 / 0.6 s / 45 m |
| c_ram | — | tự suy ra | 4 / 0.6 s / 35 m |
| c_ram.centurion | — | tự suy ra | 5 / 0.35 s / 35 m |
| c_ram.dome | — | tự suy ra | 6 / 12 s / 60 m |
| missile_battery.pac3 | — | tự suy ra | 4 / 16 s / 72 m |
| laser_ad_station | — | tự suy ra | 1 / 0.8 s / 40 m |
| Tăng thế hệ mới | BuiltIn | SelfAps | 2 / 10 s / 20 m |
| Behemoth · Quái vật thép | — | tự suy ra | 2 / 4 s / 11 m |
| Icarus · Phi thuyền quỹ đạo | — | tự suy ra | 3 / 1.4 s / 49.6 m |
| Tempest · Behemoth pháo điện từ | — | tự suy ra | 2 / 1.6 s / 26 m |
| Charybdis · Tàu đệm khí đổ bộ | — | tự suy ra | 2 / 3 s / 22 m |
| Leviathan · Thiết giáp hạm | — | tự suy ra | 3 / 2.2 s / 30 m |
| sea_corvette | — | PointDefense | 2 / 2.5 s / 32 m |
| sea_cruiser | — | PointDefense | 2 / 2.4 s / 30 m |
| Daedalus · Tàu đổ bộ quỹ đạo | — | tự suy ra | 2 / 1.6 s / 31.6 m |
| Icarus Mk.0 · Phi thuyền nguyên mẫu | — | PointDefense | 3 / 1.4 s / 19.5 m |
| mara_behemoth | — | tự suy ra | 2 / 4 s / 11 m |

### Gungnir

Boss chủ lực chương 11: máu 133.365; siêu vũ khí mỗi 45 s, nhắm toàn bản đồ, cảnh báo 3 s có đường ngắm; xuyên tối đa 5 xe × 1.000 rồi nổ 2.000 ở xe cuối (lõi 12 m, rìa 20 m còn 40%); không bắn máy bay, không chặn được, pháo sáng và APS không có tác dụng.

Sheet 01_chien_dau/Bang_sat_thuong — Bảng sát thương (6 dòng, 6 cột)

| id | mat_dat | may_bay | cong_trinh |
|---|---|---|---|
| Energy | 1.0 | 1.5 | 0.5 |
| Fire | 1.5 | 0.0 | 1.0 |
| Fragmentation | 0.5 | 1.3 | 0.1 |
| HighExplosive | 1.0 | 0.0 | 1.5 |
| Kinetic | 1.0 | 0.3 | 0.6 |
| ShapedCharge | 1.0 | 0.3 | 0.6 |

Sheet 01_chien_dau/Bang_xuyen_giap — Bảng xuyên giáp (6 dòng, 5 cột)

| id | chenh_xuyen_giap | he_so |
|---|---|---|
| buoc_0 | +2 | 1.2 |
| buoc_1 | +1 | 1.0 |
| buoc_2 | 0 | 0.85 |
| buoc_3 | -1 | 0.5 |
| buoc_4 | -2 | 0.25 |
| buoc_5 | -3 | 0.1 |

Sheet 01_chien_dau/He_so_toan_cuc — Hệ số toàn cục (4 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so |
|---|---|---|---|
| damageTable.thermobaric | damageTable | thermobaric | 2.0 |
| firepower.propBlasts | firepower | propBlasts | 1.5 |
| firepower.strikes | firepower | strikes | 2.0 |
| firepower.vehicleBlasts | firepower | vehicleBlasts | 2.0 |

Sheet 01_chien_dau/Phao_sang — Pháo sáng (11 dòng, 19 cột)

| id | loai_don_vi | mo_hinh | so_mount_flare | so_qua_moi_lan | do_nang_cap | so_voi_ban_goc | flare_charges | flare_recharge_s | flares_every_s |
|---|---|---|---|---|---|---|---|---|---|
| attack_helicopter | xe | attack_helicopter | 0 | 4;8 | FlareDispenser (01_chien_dau/Trang_bi_mo_dun) | doi | 2 |  |  |
| attack_jet | xe | attack_jet | 0 | 4;6 | FlareDispenser (01_chien_dau/Trang_bi_mo_dun) | doi | 2 |  |  |
| fighter_jet | xe | fighter_jet | 0 | 4;6 | FlareDispenser (01_chien_dau/Trang_bi_mo_dun) | doi | 2 |  |  |
| flare_searchlight_tower | thap | flare_searchlight_tower | 0 | 1;1 | FlareDispenser (01_chien_dau/Trang_bi_mo_dun) | giong |  |  | 15 |
| flare_tower | thap | flare_tower | 0 | 1;1 | FlareDispenser (01_chien_dau/Trang_bi_mo_dun) | giong |  |  | 15 |
| heavy_bomber | xe | heavy_bomber | 0 | 8;16 | FlareDispenser (01_chien_dau/Trang_bi_mo_dun) | doi | 3 |  |  |
| scout_heli | xe | scout_heli | 0 | 4;8 | FlareDispenser (01_chien_dau/Trang_bi_mo_dun) | doi | 2 | 20 |  |
| sky_gunship | xe | sky_gunship | 0 | 8;16 | FlareDispenser (01_chien_dau/Trang_bi_mo_dun) | doi | 3 |  |  |
| stealth_fighter | xe | stealth_fighter | 0 | 4;6 | FlareDispenser (01_chien_dau/Trang_bi_mo_dun) | doi | 2 |  |  |
| swarm_carrier | xe | swarm_carrier | 0 | 8;16 | FlareDispenser (01_chien_dau/Trang_bi_mo_dun) | doi | 3 |  |  |
| twin_rotor_gunship | xe | twin_rotor_gunship | 0 | 4;8 | FlareDispenser (01_chien_dau/Trang_bi_mo_dun) | doi | 3 | 20 |  |

*In 10 / 19 cột; 3 cột khác: xem sheet.*

Bảng đầy đủ: xem sheet `Khac_che` (21 dòng), `Vu_khi` (332 dòng), `Vu_khi_suy_ra` (332 dòng), `Vu_khi_he_so_thuong` (27 dòng), `Dan_thay_the` (68 dòng).

## Sổ tay đạn

### Sổ tay đạn / Ammunition handbook

Sinh từ dữ liệu (balance.json) như mục Sổ tay đạn trong Hồ sơ của game; chạm vào chip ĐÁNH NÓC, ĐẠN THAY THẾ, NỔ TRÊN KHÔNG, DẪN ĐƯỜNG, PHÁ CÔNG TRÌNH, PHÁ TƯỜNG trên trang chi tiết mở đúng mục. / Generated from the data, as the game's Dossier tab.

### Sổ tay đạn (tiếng Việt)

**Động năng**: mạnh với Mặt đất (×1), yếu với Máy bay (×0,3). Ví dụ: M2 Browning 12.7 mm, PKT / M240 7.62 mm, M242 Bushmaster 25 mm.

**Nổ lõm**: mạnh với Mặt đất (×1), yếu với Máy bay (×0,3). Ví dụ: BGM-71 TOW-2, APKWS (laser-guided Hydra 70), 9M120 Ataka.

**Nổ mạnh**: mạnh với Công trình (×1,5), yếu với Máy bay (×0). Ví dụ: Mk 19 40 mm, GBU-39 SDB (110 kg), AGM-158 JASSM (450 kg).

**Lửa**: mạnh với Mặt đất (×1,5), yếu với Máy bay (×0). Ví dụ: flamethrower.

**Mảnh**: mạnh với Máy bay (×1,3), yếu với Công trình (×0,1). Ví dụ: AIM-120 AMRAAM, GAU-22/A 25 mm, AIM-9 Sidewinder.

**Năng lượng**: mạnh với Máy bay (×1,5), yếu với Công trình (×0,5). Ví dụ: focused laser (300 kW), Iron Beam laser (100 kW).

Giáp có hướng: trước, hông, sau và nóc (xe tới cấp 4, boss tới cấp 5); trên nóc và lên máy bay không có mức áp đảo (×1 là cao nhất).

Ví dụ: một phát 2A42 30 mm của ifv (xuyên 2, sát thương 22) lên main_battle_tank (máu 2310): giáp trước cấp 4: ×0,25, 6; giáp hông cấp 2: ×0,85, 19.

| Dấu | Nghĩa |
|---|---|
| Đánh nóc | Trúng giáp nóc, mặt mỏng nhất. Ví dụ: Fibre-optic FPV drone (1.5 kg), FPV drone (1.5 kg), Switchblade 300 |
| Nhiệt áp | ×2 lên công trình thay cho ×1,5 của nổ mạnh (thay, không nhân thêm). Ví dụ: ODAB-500, TOS-1A 220 mm thermobaric |
| Dẫn đường | Bám mục tiêu; APS / phòng thủ điểm bắn hạ được, pháo sáng đánh lừa loại nhắm máy bay. Ví dụ: AIM-120 AMRAAM, BGM-71 TOW-2, AGM-158 JASSM (450 kg) |
| Nổ trên không | Đạn mảnh: ×1,3 lên máy bay. Ví dụ: AIM-120 AMRAAM, GAU-22/A 25 mm, AIM-9 Sidewinder |
| Đạn thay thế | Súng tự đổi khi mục tiêu hợp; giữ đạn ít nhất 2 s, đổi mất ít nhất 0,5 s. |
| Tầm tối thiểu | 120 mm AMOS (twin) (10 m), 9M723 Iskander (700 kg) (40 m), 155 mm L/52 (CAESAR) (25 m) |

| Hệ | Chặn |
|---|---|
| Giáp phản ứng nổ | Giảm tới 80% sát thương nổ lõm; đầu nổ kép xuyên qua. |
| Lồng chắn | Đỡ nổ lõm của rốc-két, tên lửa, drone; động năng và nhiệt áp đi qua. |
| SELF_APS | Chỉ tên lửa dẫn đường, drone, rốc-két bắn thẳng; không chặn đạn pháo xe tăng. |
| POINT_DEFENSE (C-RAM, la-de, vòm) | Tên lửa, drone, rốc-két, một phần đạn pháo binh (C-RAM 30%, la-de 0%); không chặn đạn pháo xe tăng; mỗi viên một hệ (gần nhất). |
| Pháo sáng | Đánh lừa tên lửa dẫn đường nhắm máy bay. |
| Khói | Che mục tiêu, làm mù la-de phòng thủ điểm. |
| Gây nhiễu | Làm tản drone và hỏa lực dẫn đường gọi vào vùng nhiễu. |
| Khiên | Vòm hấp thụ mọi đòn trừ năng lượng; khiên tháp chỉ đỡ đạn nhắm vào tháp. |

Xe phá tường (armored_bulldozer, engineer_vehicle, demolition_line_vehicle) gây ×1,5 lên tường (không lên tháp hay nhà chính).

### Ammunition handbook (English)

**Kinetic**: strong against Ground (×1), weak against Air (×0.3). For example: M2 Browning 12.7 mm, PKT / M240 7.62 mm, M242 Bushmaster 25 mm.

**Shaped charge**: strong against Ground (×1), weak against Air (×0.3). For example: BGM-71 TOW-2, APKWS (laser-guided Hydra 70), 9M120 Ataka.

**High explosive**: strong against Structures (×1.5), weak against Air (×0). For example: Mk 19 40 mm, GBU-39 SDB (110 kg), AGM-158 JASSM (450 kg).

**Fire**: strong against Ground (×1.5), weak against Air (×0). For example: flamethrower.

**Fragmentation**: strong against Air (×1.3), weak against Structures (×0.1). For example: AIM-120 AMRAAM, GAU-22/A 25 mm, AIM-9 Sidewinder.

**Energy**: strong against Air (×1.5), weak against Structures (×0.5). For example: focused laser (300 kW), Iron Beam laser (100 kW).

Armour has a direction: front, side, rear and roof (vehicles up to level 4, bosses up to 5); on the roof and on aircraft a round never overmatches (×1 is the most).

Worked example: one shot of the ifv's 2A42 30 mm (penetration 2, 22 damage) on a main_battle_tank (health 2310): front armour 4: ×0.25, 6; side armour 2: ×0.85, 19.

| Mark | Meaning |
|---|---|
| Top attack | Strikes the roof armour, the thinnest face. For example: Fibre-optic FPV drone (1.5 kg), FPV drone (1.5 kg), Switchblade 300 |
| Thermobaric | ×2 on structures instead of high explosive's ×1.5 (replaces, never adds). For example: ODAB-500, TOS-1A 220 mm thermobaric |
| Guided | Follows its target; APS and point defence can shoot it down, flares draw off those aimed at aircraft. For example: AIM-120 AMRAAM, BGM-71 TOW-2, AGM-158 JASSM (450 kg) |
| Airburst | Fragmentation: ×1.3 against aircraft. For example: AIM-120 AMRAAM, GAU-22/A 25 mm, AIM-9 Sidewinder |
| Second rounds | The gun switches on its own when the target suits; a round stays in 2 s at least, a switch takes 0.5 s at least. |
| Minimum range | 120 mm AMOS (twin) (10 m), 9M723 Iskander (700 kg) (40 m), 155 mm L/52 (CAESAR) (25 m) |

| System | Stops |
|---|---|
| Reactive armour | Cuts shaped charges by up to 80%; a tandem warhead goes through. |
| Cage | Takes shaped charges on rockets, missiles, drones; kinetic and thermobaric go through. |
| SELF_APS | Guided missiles, drones, direct-fire rockets only; never a tank's shell. |
| POINT_DEFENSE (C-RAM, lasers, dome) | Missiles, drones, rockets, a share of artillery shells (C-RAM 30%, laser 0%); never a tank's shell; one system per round (the nearest). |
| Flares | Draw off guided missiles aimed at aircraft. |
| Smoke | Hides what is in it, blinds point-defence lasers. |
| Jamming | Scatters drones and guided fire called into its bubble. |
| Shield | A dome absorbs every hit but energy; a tower's shield only rounds aimed at the tower. |

Wall breakers (armored_bulldozer, engineer_vehicle, demolition_line_vehicle) do ×1.5 to walls (not to towers or the HQ).

### Sổ tay đạn: bậc T0–T5 / Calibre tiers

Như mục "Bậc cỡ nòng T0–T5" của Sổ tay đạn trong game. Bậc lấy theo họ: càng to thì mỗi phát càng mạnh, nổ, hình và tiếng càng lớn, bù bằng thời gian nạp dài hơn. Đạn T4 và T5 của boss báo chỗ rơi ít nhất 0,5 s + lõi / 4,5 m/s (T4 ít nhất 2,5 s). / A round's tier comes from its family; a boss's T4-T5 rounds warn at least 0.5 s + core / 4.5 m/s.

| Bậc | Họ | Hình và tiếng | Look and sound |
|---|---|---|---|
| T0 | 12.7 mm heavy machine gun, 14.5 mm heavy machine gun, 7.62 mm machine gun, melee_bucket_wheel, melee_dozer_blade, melee_drill_head (+3) | Súng nhỏ: chớp mảnh, tiếng nổ giòn ngắn. | Small arms: a thin flash and a short crack. |
| T1 | 20 mm, 23 mm, 25 mm, 30 mm, 35 mm Oerlikon, 40 mm Bofors (+8) | Pháo tự động: chớp nhỏ, khói mỏng; nhiều súng cùng bắn nghe thành một trận đấu súng. | Autocannon: a small flash and thin smoke; many guns at once are heard as one firefight. |
| T2 | atgm_9k121_vikhr, atgm_9m113_konkurs, atgm_9m120_ataka, atgm_9m123_khrizantema, atgm_agm_114_hellfire, atgm_agm_114l_hellfire_longbow (+36) | Pháo vừa và rocket nhẹ: chớp vừa, quả cầu lửa nhỏ, bụi và đất tung lên. | Medium guns and light rockets: a medium flash, a small hot fireball, dust and earth thrown up. |
| T3 | atgm_agm_65_maverick, bomb_fab_250, 120 mm AP, 120 mm HE, 125 mm AP, 125 mm HE (+10) | Pháo nặng: chớp lớn, cầu lửa đầu nòng, khói dài và chậm, cột bụi; thân xe giật lùi. | Heavy guns: a big flash and muzzle fireball, long slow smoke, a dust column; the hull rocks back. |
| T4 | atgm_kh_29l, bal_9m723_iskander, 400 kg bomb, bomb_car_bomb, bomb_cbu_97_sensor_fuzed_weapon, bomb_fab_500 (+15) | Pháo rất nặng, Smerch, bom 400 kg: chớp rất lớn, cầu lửa cuộn, sóng xung kích trên mép vụ nổ, máy quay rung ngắn. | Very heavy guns, Smerch, 400 kg bombs: a very big flash, a rolling fireball, a shockwave on the blast's edge, a short camera shake. |
| T5 | 406 mm, 800 mm super-gun, EMRG electromagnetic railgun (Gungnir) | Siêu vũ khí: chớp sáng cả cảnh, đám mây hình nấm nhỏ, vòng trên lõi rồi trên mép, rung mạnh nhất. | Super weapons: a flash that lights the scene, a small mushroom cloud, rings on the core then the edge, the strongest shake. |

Sheet 01_chien_dau/So_tay_dan — Sổ tay đạn (2 dòng, 8 cột)

| id | nhom | khoa | gia_tri_chu |
|---|---|---|---|
| exampleShooter | handbook | exampleShooter | ifv |
| exampleTarget | handbook | exampleTarget | main_battle_tank |

Bảng đầy đủ: xem sheet `Dong_vu_khi` (55 dòng).

## Họ vũ khí, hành vi đạn và vòng cảnh báo

### Họ vũ khí, bảng boss, bán kính và cảnh báo

Mỗi vũ khí có `weaponFamilyId` (súng: lớp cỡ nòng; còn lại: vũ khí thật) và `weaponVariantId` khi đạn hay cách bắn khác (có lý do trong bảng). Bậc T0–T5 theo họ. Ở boss, cùng họ là cùng viên đạn (sát thương, lõi, rìa, tốc độ, loại); DPS của từng vũ khí giữ nguyên bằng chu kỳ dài hơn, và lõi rộng hơn 1,25 lần thì chu kỳ dài thêm đúng tỉ lệ đó. Vũ khí người chơi chỉ gắn nhãn (danh sách lệch: Docs/checks/player_weapon_family.md). Kiểm: `Tools/balance/p34_validate.py`.

### Vũ khí boss theo họ (136)

Sát thương một viên; lõi nhận đủ sát thương, rìa 40%. Hồi: thời gian hồi của vũ khí (loạt và băng giữ nhịp riêng). Cảnh báo: thời gian đạn T4+ không dẫn đường báo chỗ rơi (đạn ở trên không ít nhất bấy lâu).

### Cảnh báo theo khả năng thoát

Đạn T4+ của boss báo max(sàn, 0,5 s + lõi / 4,5 m/s), tối đa 6 s; sàn T4 2,5 s, 406 mm 3,5 s, siêu vũ khí T5 4 s. Vòng hiển thị là đúng vùng sát thương: vòng ngoài là rìa, vòng trong là lõi (tên lửa hành trình: lõi và rìa của vụ nổ hai lớp).

Bảng 24 dòng: số liệu đầy đủ ở các sheet của mục này trong file xlsx cùng tên.

Sheet 01_chien_dau/Ho_vu_khi_bien_the — Họ vũ khí: biến thể (20 dòng, 7 cột)

| id | ho_vu_khi_id | thu_tu | bien_the | ly_do |
|---|---|---|---|---|
| cal_25/flak | cal_25 | 0 | flak | air-burst rounds against aircraft, the family's others are… |
| cal_30/ciws | cal_30 | 0 | ciws | the AK-630 close-in weapon of the ships and hovercraft: a s… |
| cal_30/flak | cal_30 | 1 | flak | the 2A38 / AK-630 air-burst (fragmentation, a 2.5 m burst)… |
| cal_35/ap | cal_35 | 0 | ap | AP rounds (no burst) loaded against ground targets instead… |
| cal_40/flak | cal_40 | 0 | flak | proximity air-burst (3.5 m) against aircraft |
| cal_40/he | cal_40 | 1 | he | the AC-130's 40 mm HE against the ground (a 3 m burst), not… |
| cal_57/ap | cal_57 | 0 | ap | AP rounds (kinetic, no burst) instead of HE |
| cal_57/flak | cal_57 | 1 | flak | air-burst against aircraft |
| cal_100_105_ap/he | cal_100_105_ap | 0 | he | a high-explosive second round of an AP gun |
| cal_100_105_he/flak | cal_100_105_he | 0 | flak | the KS-19's time-fused flak against aircraft |
| cal_120_he/mortar | cal_120_he | 0 | mortar | a lobbed mortar bomb (slow, high arc), not a gun's HE shell |
| cal_127_130/ap | cal_127_130 | 0 | ap | an armour-piercing round fired direct (Leviathan's AK-127 i… |
| cal_152_155/ap | cal_152_155 | 0 | ap | an armour-piercing round fired direct (a tank gun's or a na… |
| cal_152_155/guided | cal_152_155 | 1 | guided | a guided shell (one at a time) |
| cal_152_155/heat | cal_152_155 | 2 | heat | a shaped-charge (HEAT) round |
| cal_152_155/smart | cal_152_155 | 3 | smart | a sensor-fuzed or guided shell with submunitions |
| rkt_70_80/guided | rkt_70_80 | 0 | guided | a laser-guided rocket (APKWS) |
| rkt_gmlrs_227/cluster | rkt_gmlrs_227 | 0 | cluster | the M30's cluster warhead |
| rkt_grad_122/cluster | rkt_grad_122 | 0 | cluster | a cluster warhead (bomblets) |
| rkt_grad_122/thermobaric | rkt_grad_122 | 1 | thermobaric | a thermobaric warhead |

Sheet 01_chien_dau/Hanh_vi_dan — Hành vi đạn: luật chung (11 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so | gia_tri_chu | don_vi |
|---|---|---|---|---|---|
| flareBurn | munitionRules | flareBurn |  | 3;4 | s |
| flareDecoyChance | munitionRules | flareDecoyChance | 0.35 |  |  |
| flareOffset | munitionRules | flareOffset | 10 |  | m |
| flareRelease.fighter | munitionRules | fighter |  | 4;6 |  |
| flareRelease.helicopter | munitionRules | helicopter |  | 4;8 |  |
| flareRelease.large | munitionRules | large |  | 8;16 |  |
| leadCap | munitionRules | leadCap | 3 |  |  |
| proximityFuze | munitionRules | proximityFuze | 7 |  | m |
| radarGuided | munitionRules | radarGuided |  | sam_aim_120_amraam;sam_r_37m;sam_9m317_buk;sam_mim_104_patr… |  |
| reachScale | munitionRules | reachScale | 1.3 |  |  |
| sightGuided | munitionRules | sightGuided |  | atgm_bgm_71_tow_2;atgm_gun_launched_atgm;atgm_kornet;atgm_9… |  |

Sheet 01_chien_dau/Hanh_vi_dan_nhom — Hành vi đạn theo nhóm (7 dòng, 12 cột)

| id | so_vu_khi | cach_nham | khi_no | khi_truot | co_canh_bao | thoi_gian_bay_toi_da_s | tuong_tac_phao_sang | tuong_tac_aps | tuong_tac_gay_nhieu |
|---|---|---|---|---|---|---|---|---|---|
| Bomb | 6 | dẫn đường 33% vũ khí, còn lại đón đầu (trần 3 s) | nổ lan 100% vũ khí | quá tầm × 1.3 tự hủy; đạn dẫn bằng mắt mất kẻ bắn hoặc tầm… | 0% vũ khí có vòng cảnh báo | 0.8 | pháo sáng mồi 0% vũ khí (xác suất 0.35) | APS chặn được 100%, CIWS 100% vũ khí | không bị nhiễu (không phải đạn dẫn đường) |
| Bullet | 111 | đón đầu (led, trần 3 s) | nổ lan 35% vũ khí | quá tầm × 1.3 tự hủy | 0% vũ khí có vòng cảnh báo | 0.4286 | pháo sáng mồi 0% vũ khí (xác suất 0.35) | APS chặn được 100%, CIWS 100% vũ khí | không bị nhiễu (không phải đạn dẫn đường) |
| Drone | 11 | dẫn đường (homing) | nổ lan 100% vũ khí; ngòi cận đích 7 m | quá tầm × 1.3 tự hủy; đạn dẫn bằng mắt mất kẻ bắn hoặc tầm… | 0% vũ khí có vòng cảnh báo | 7.5 | pháo sáng mồi 0% vũ khí (xác suất 0.35) | APS chặn được 100%, CIWS 100% vũ khí | bị nhiễu 100% vũ khí (đạn dẫn đường trong vòng nhiễu địch:… |
| Flame | 3 | đón đầu (led, trần 3 s) | nổ lan 100% vũ khí | quá tầm × 1.3 tự hủy | 0% vũ khí có vòng cảnh báo | 0.5263 | pháo sáng mồi 0% vũ khí (xác suất 0.35) | APS chặn được 100%, CIWS 100% vũ khí | không bị nhiễu (không phải đạn dẫn đường) |
| Missile | 45 | dẫn đường (homing) | nổ lan 47% vũ khí; ngòi cận đích 7 m | quá tầm × 1.3 tự hủy; đạn dẫn bằng mắt mất kẻ bắn hoặc tầm… | 0% vũ khí có vòng cảnh báo | 5.7143 | pháo sáng mồi 76% vũ khí (xác suất 0.35) | APS chặn được 100%, CIWS 100% vũ khí | bị nhiễu 100% vũ khí (đạn dẫn đường trong vòng nhiễu địch:… |
| Rocket | 27 | dẫn đường 4% vũ khí, còn lại đón đầu (trần 3 s) | nổ lan 100% vũ khí | quá tầm × 1.3 tự hủy; đạn dẫn bằng mắt mất kẻ bắn hoặc tầm… | 0% vũ khí có vòng cảnh báo | 1.1667 | pháo sáng mồi 0% vũ khí (xác suất 0.35) | APS chặn được 100%, CIWS 100% vũ khí | không bị nhiễu (không phải đạn dẫn đường) |
| Shell | 129 | dẫn đường 11% vũ khí, còn lại đón đầu (trần 3 s) | nổ lan 80% vũ khí | quá tầm × 1.3 tự hủy; đạn dẫn bằng mắt mất kẻ bắn hoặc tầm… | 0% vũ khí có vòng cảnh báo | 2 | pháo sáng mồi 0% vũ khí (xác suất 0.35) | APS chặn được 100%, CIWS 100% vũ khí | không bị nhiễu (không phải đạn dẫn đường) |

Sheet 01_chien_dau/Canh_bao_vong — Vòng cảnh báo (13 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so | don_vi |
|---|---|---|---|---|
| base | warningRules | base | 0.5 | s |
| bombMinKg | warningRules | bombMinKg | 400 | kg |
| cap | warningRules | cap | 6 | s |
| escapeSpeed | warningRules | escapeSpeed | 4.5 | m/s |
| fadeIn | warningRules | fadeIn | 0.4 | s |
| floor406 | warningRules | floor406 | 3.5 | s |
| floorT4 | warningRules | floorT4 | 2.5 | s |
| floorT5 | warningRules | floorT5 | 4 | s |
| gunMinMm | warningRules | gunMinMm | 203 | mm |
| maxShown | warningRules | maxShown | 6 |  |
| normalFire | warningRules | normalFire | FALSE |  |
| rocketMinMm | warningRules | rocketMinMm | 300 | mm |
| salvoMergeSeconds | warningRules | salvoMergeSeconds | 0.6 | s |

Sheet 01_chien_dau/Drone — Drone: tốc độ, đầu nổ, cỡ, vụ nổ (13 dòng, 19 cột)

| id | loai | ten_that | mang_boi | toc_do_m_s | do_cao_m | dau_no_kg | sat_thuong | loi_m | ria_m |
|---|---|---|---|---|---|---|---|---|---|
| airship_drones | dan_drone | FPV drone (1.5 kg) |  | 26 |  | 1.5 | 140 | 2.5 | 0 |
| fpv_hangar | dan_drone | FPV drone (1.5 kg) | drone_hangar | 26 |  | 1.5 | 140 | 2.5 | 0 |
| fpv_hangar_swarm | dan_drone | FPV drone (1.5 kg) | drone_hangar.swarm | 26 |  | 1.5 | 140 | 2.5 | 0 |
| fpv_swarm | dan_drone | FPV drone (1.5 kg) | elite_fpv_carrier;fpv_carrier | 26 |  | 1.5 | 140 | 2.5 | 0 |
| lancet | dan_drone | ZALA Lancet-3 (3 kg) |  | 28 |  | 3 | 240 | 3 | 0 |
| lancet_hangar | dan_drone | ZALA Lancet-3 (3 kg) | drone_hangar.lancet | 28 |  | 3 | 240 | 3 | 0 |
| locust_drones | dan_drone | ZALA Lancet-3 swarm | locust | 28 |  | 3 | 320 | 3 | 6 |
| mothership_drones | dan_drone | ZALA Lancet-3 (3 kg) | drone_bay | 28 |  | 3 | 240 | 3 | 0 |
| p26_matriarch_ma_drones | dan_drone | ZALA Lancet-3 swarm | drone_mothership | 28 |  | 3 | 320 | 3 | 6 |
| recon_drone | may_bay_drone |  |  | 13 | 34 | recon_missile:22 |  |  |  |
| shahed | dan_drone | Shahed-136 (50 kg) | shahed_truck | 20 |  | 50 | 344 | 4.5 | 0 |
| strike_drone | may_bay_drone |  |  | 13.9 | 30 | drone_missile:9;guided_bomb:110 |  |  |  |
| swarm_drones | dan_drone | FPV drone (1.5 kg) | swarm_carrier | 26 |  | 1.5 | 140 | 2.5 | 0 |

*In 10 / 19 cột; 7 cột khác: xem sheet.*

Bảng đầy đủ: xem sheet `Ho_vu_khi` (105 dòng).

## Hỗ trợ hỏa lực

Thẻ hỗ trợ trong bộ bài (2 ô), gọi vào một điểm trên bản đồ; không gọi được vào vùng căn cứ địch; vật phẩm dùng một lần mua bằng xu. Mỗi thẻ hỗ trợ có clip Xem bắn riêng (gọi hỏa lực lên một cụm mục tiêu).

![Clip Xem bắn của các thẻ hỗ trợ (pháo kích, không kích, tên lửa hành trình, napalm, ném bom rải thảm, MOAB, bom chùm, m…](images/01_chien_dau_r6_supports.png)

*Hình: Clip Xem bắn của các thẻ hỗ trợ (pháo kích, không kích, tên lửa hành trình, napalm, ném bom rải thảm, MOAB, bom chùm, máy bay pháo, EMP, khói, tiếp tế, chi viện). Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

Bảng đầy đủ: xem sheet `The_ho_tro` (24 dòng).

## Bảng giá, hệ đạn và hồi đạn

### Bảng giá

Mọi giá trong game ở một chỗ. **CP** là điểm chỉ huy trả mỗi lần gọi trong trận. **Xu** là tiền duy nhất ngoài trận: mua thẻ cao cấp, mua sớm thẻ chiến dịch trước khi thắng màn mở khóa, mua vật phẩm. Thẻ có sẵn không cần mua. Giá lên hạng thẻ, hòm và gói xu ở phần kinh tế.

### Tháp căn cứ (22)

Tháp không tốn CP khi đặt vào căn cứ: nó chiếm một ô theo cỡ. Bị phá trong trận thì xây lại bằng CP sau một thời gian chờ.

### Hệ đạn và hồi đạn

- **Lượng đạn:** bom, tên lửa và rốc-két của máy bay và trực thăng có số lượng khi đầy đạn (ghi ở mục "Đạn và nạp đạn" trên mỗi thẻ); pháo máy bay và súng máy không giới hạn, chỉ thay băng.
- **Hồi dần trên chiến trường:** từng quả hồi theo thời gian, không cần căn cứ. Đang tấn công hoặc trong tầm phòng không/tiêm kích địch: một nửa tốc độ; ra khỏi vùng nguy hiểm liên tục 3 giây: đủ tốc độ.
- **Vòng chờ gần:** một vòng bay ngay sau tuyến quân ta gần nhất, ngoài tầm phòng không đã biết, cách chỗ giao tranh khoảng 2–3 giây bay; tính lại liên tục theo chiến tuyến. Không đơn vị nào bay về căn cứ hay ra ngoài bản đồ để nạp.
- **Rút đúng lúc:** hết đạn giữa lượt thì làm xong lượt (bổ nhào, lượt ném bom, vòng bay) rồi mới ra vòng chờ, bay theo đường thật, vẫn bị bắn được; chỉ huy AI cho ra sớm khi đạn dưới 20% và đang có quãng lặng.
- **Nạp nhanh hơn:** Bãi đáp ×2 (và hồi 3% máu/giây), sở chỉ huy ×1,5 (1% máu/giây), trực thăng cạnh Xe tiếp đạn ×2. Chỉ ghé khi nhanh hơn vòng chờ hoặc cần hồi máu.
- **Máy bay ném bom:** chỉ vào lượt mới khi có ít nhất 2/3 tải bom; ưu tiên cụm quân và công trình, không thả gần quân ta, nghỉ trước khi ném lại cùng khu vực. Oanh tạc cơ 9 quả, máy bay tàng hình 2, Su-25 16 rốc-két, không kích bất ngờ 10, bom chùm 30 quả con.
- **Xe tiếp đạn (mới, 4 CP):** điểm nạp tiền phương: trực thăng đứng cạnh hồi đạn nhanh gấp đôi, bệ phóng và xe tên lửa quanh nó nạp nhanh gấp ba. Xe công binh chỉ còn sửa chữa (3 CP).
- **Bãi đáp:** nhánh hạng 7: Nhà chứa (+1 trần máy bay) hoặc Phục vụ nhanh. AI địch đặt Bãi đáp trong căn cứ; phá Bãi đáp pháo đài trong Công thành được 12 CP.
- **Icon trên chiến trường:** cạnh thanh máu: sắp hết (vàng), hết (đỏ nhấp nháy), đang ra vòng chờ, đang hồi (vòng tiến độ mờ khi hồi chậm, sáng khi hồi đủ), lóe sáng khi đầy. Địch chỉ hiện hết đạn và đang ra vòng chờ. Bản đồ nhỏ hiện vòng chờ của ta.

## Commander

Người chơi chọn một commander trước trận; nội tại của nó áp cho cả phe, trong mọi chế độ. Mỗi màn gắn với một tướng địch thì địch mang nội tại của tướng đó. Commander mở dần theo chương. Không còn chọn học thuyết riêng: lợi thế của năm học thuyết cũ đã gộp vào commander hợp lối chơi (Crown: thiết giáp, Hawk: không quân, Longshot: pháo binh, Rush: chớp nhoáng, Ledger: hậu cần), chỗ trùng loại thưởng thì gộp thành một con số, không cộng dồn; bảng dưới là số mới.

### Commander của người chơi (14)

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

### Nội tại của tướng địch (8)

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

Sheet 01_chien_dau/Commander_gia — Commander: hệ số giá (5 dòng, 7 cột)

| id | commander_id | thu_tu | reach_m | scale |
|---|---|---|---|---|
| brandt/0 | brandt | 0 | AirdropTowers | 0.8 |
| gen.kessler/0 | gen.kessler | 0 | Vehicles | 0.9 |
| lind/0 | lind | 0 | Engineers | 0.8 |
| reyn/0 | reyn | 0 | Vehicles | 1.1 |
| varro/0 | varro | 0 | Cheap | 0.85 |

Sheet 04_che_do_kinh_te_ai/AI_tuong — Tướng địch (12 dòng, 11 cột)

| id | chien_thuat_ua_thich | chien_dich_deck | chien_dich_supports | noi_tai | can_bang_deck | can_bang_elites | chien_dich_stance | chien_dich_style |
|---|---|---|---|---|---|---|---|---|
| aurel | all_out | heavy_tank;ifv;railgun_truck;attack_helicopter;long_sam;hea… | cruise_missile;airstrike;napalm_strike | gen.aurel |  |  | Attack | aurel |
| brandt | depth |  |  | gen.brandt |  |  |  |  |
| default | balanced |  |  | gen.default |  |  |  |  |
| hung |  | main_battle_tank;heavy_tank;titan_tank;ifv;aa_vehicle;mlrs;… | artillery_barrage;airstrike;cruise_missile | gen.hung |  |  | Attack | aurel |
| kessler | attrition | wheeled_gun;ifv;main_battle_tank;heavy_tank;sam_launcher;fp… | remote_mines;artillery_barrage;repair_drop | gen.kessler |  |  | Defend | kessler |
| orlov | firepower | mlrs;artillery;mortar_carrier;heavy_rocket_artillery;sam_la… | artillery_barrage;cruise_missile;airstrike | gen.orlov |  | Artillery | Defend | orlov |
| quaden |  | attack_helicopter;attack_jet;fighter_jet;strike_drone;aa_ve… | airstrike;cruise_missile;napalm_strike | gen.quaden |  | Air | Attack | quaden |
| sen |  | strike_drone;fpv_carrier;recon_drone;ew_jammer;ifv;main_bat… | airstrike;cruise_missile;repair_drop | gen.sen |  | Drone | Attack | sen |
| thorne | balanced |  |  | gen.thorne |  |  |  |  |
| varga | breakthrough | light_tank;main_battle_tank;heavy_tank;tank_destroyer;ifv;f… | artillery_barrage;airstrike;repair_drop | gen.varga | armored_bulldozer | Tank;Heavy | Attack | varga |
| venn | dispersal |  |  | gen.venn |  |  |  |  |
| wolff | air_superiority |  |  | gen.wolff |  |  |  |  |

Bảng đầy đủ: xem sheet `Commander` (22 dòng), `Commander_noi_tai` (45 dòng).

## Trang bị

Mỗi nhánh (Thiết giáp, Xe nhẹ, Pháo binh, Không quân) có 7 ô: Vũ khí, Nạp đạn, Giáp, Quang học, Động cơ, Sửa chữa và Đặc biệt. Một món gồm: **loại đồ** (có dòng ẩn riêng), **chỉ số chính** tăng theo cấp (40% → 100%), **0/1/2/2/2 chỉ số phụ** theo độ hiếm (lăn 60–100%, có thanh chất lượng, tăng ở cấp 5/10/15/20), **một dòng unique** ở Sử thi và Huyền thoại (chọn 1 trong 3 khi ghép lên Sử thi), và **một thương hiệu** (bộ 2 món và 4 món). Ghép 3 món cùng ô cùng độ hiếm để lên bậc. Mỗi chỉ số có trần cho cả bộ.

Thường · cấp tối đa 5Khá · cấp tối đa 10Hiếm · cấp tối đa 15Sử thi · cấp tối đa 20Huyền thoại · cấp tối đa 25

### Loại đồ (38)

Bảng 38 dòng: số liệu đầy đủ ở các sheet của mục này trong file xlsx cùng tên.

### Dòng unique (45)

Bảng 45 dòng: số liệu đầy đủ ở các sheet của mục này trong file xlsx cùng tên.

### Module đặc biệt (14)

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

### Thương hiệu / bộ (13)

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

Sheet 01_chien_dau/Trang_bi_bo — Trang bị: bộ (brand) (13 dòng, 16 cột)

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

*In 10 / 16 cột; 3 cột khác: xem sheet.*

Sheet 01_chien_dau/Trang_bi_mo_dun — Trang bị: mô-đun đặc biệt (14 dòng, 9 cột)

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

Bảng đầy đủ: xem sheet `Trang_bi` (38 dòng), `Trang_bi_dac_tinh` (45 dòng), `Trang_bi_dong_phu` (23 dòng), `Trang_bi_hang` (27 dòng).

## Tham khảo ngoài đời và game

Thông số ngoài đời lấy từ nguồn trong repo (sheet Nguon_tham_chieu của 08_tham_chieu); chỗ chưa có nguồn ghi NEED_SOURCE, không điền từ trí nhớ.

### Vu_khi_tham_chieu

332 dòng. Độ tin cậy: da_kiem_chung 245, uoc_dinh 43, ban_dau_doan 43, NEED_SOURCE 1. Loại: NEED_SOURCE 1, doi_that 331.

- `aa_25_triple` (Type 96 25 mm (triple)): mẫu thật: Type 96 25 mm (triple); độ tin: da_kiem_chung; nguồn: R_balance, R_full_weapon_audit, W_wikipedia_type_96_25_mm_at_aa_gun, R_machine_brigade_can_bang.
- `aa_25_triple_ap` (Type 96 25 mm AP (triple)): mẫu thật: Type 96 25 mm AP (triple); độ tin: da_kiem_chung; nguồn: R_balance, R_full_weapon_audit, W_wikipedia_type_96_25_mm_at_aa_gun.
- `agl_40` (Mk 19 40 mm): mẫu thật: Mk 19 40 mm; độ tin: da_kiem_chung; nguồn: R_balance, R_full_weapon_audit, D_us_army_fm_3_22_27, R_machine_brigade_can_bang.
- `air_cruise_missile` (Kh-101 (400 kg)): mẫu thật: Kh-101 (400 kg); độ tin: uoc_dinh; nguồn: R_balance, R_full_weapon_audit, R_machine_brigade_can_bang.
- `air_to_air` (AIM-120 AMRAAM): mẫu thật: AIM-120 AMRAAM; độ tin: uoc_dinh; nguồn: R_balance, R_full_weapon_audit, R_machine_brigade_can_bang.
- `airship_drones` (FPV drone (1.5 kg)): mẫu thật: FPV drone (1.5 kg); độ tin: ban_dau_doan; nguồn: R_balance, R_machine_brigade_can_bang.
- `airship_flak` (S-60 57 mm): mẫu thật: S-60 57 mm; độ tin: da_kiem_chung; nguồn: R_balance, R_full_weapon_audit, W_wikipedia_azp_s_60, R_machine_brigade_can_bang.
- `amos_120` (120 mm AMOS (twin)): mẫu thật: 120 mm AMOS (twin); khác có chủ đích: nhịp chậm hơn 30 % và mạnh hơn tương ứng (luật súng của game); độ tin: da_kiem_chung; nguồn: R_balance, R_full_weapon_audit, W_wikipedia_amos.
- `anti_ship_missile` (NSM / P-800 Oniks): mẫu thật: NSM / P-800 Oniks; độ tin: uoc_dinh; nguồn: R_balance, R_full_weapon_audit, W_wikipedia_bai_cua_tung_ten_lua_bang_warhead.
- `apkws_rocket` (APKWS (laser-guided Hydra 70)): mẫu thật: APKWS (laser-guided Hydra 70); độ tin: ban_dau_doan; nguồn: R_balance, R_full_weapon_audit, R_decisions.
- `atgm` (BGM-71 TOW-2): mẫu thật: BGM-71 TOW-2; độ tin: da_kiem_chung; nguồn: R_balance, R_full_weapon_audit, W_wikipedia_bgm_71_tow, W_wikipedia_bai_cua_tung_ten_lua_bang_warhead, R_machine_brigade_can_bang.
- `atgm_heavy` (9M133 Kornet): mẫu thật: 9M133 Kornet; độ tin: da_kiem_chung; nguồn: R_balance, R_full_weapon_audit, W_wikipedia_9m133_kornet, W_wikipedia_bai_cua_tung_ten_lua_bang_warhead.
- `atgm_post` (9M113 Konkurs): mẫu thật: 9M113 Konkurs; độ tin: da_kiem_chung; nguồn: R_balance, R_full_weapon_audit, W_wikipedia_9m113_konkurs, W_wikipedia_bai_cua_tung_ten_lua_bang_warhead.
- `autocannon_25` (M242 Bushmaster 25 mm): mẫu thật: M242 Bushmaster 25 mm; độ tin: da_kiem_chung; nguồn: R_balance, R_full_weapon_audit, W_wikipedia_m242_bushmaster, R_machine_brigade_can_bang.
- `autocannon_25_flak` (M242 Bushmaster 25 mm air-burst): mẫu thật: M242 Bushmaster 25 mm air-burst; độ tin: da_kiem_chung; nguồn: R_balance, R_full_weapon_audit, W_wikipedia_m242_bushmaster.
- … 316 dòng có tham chiếu nữa: xem sheet Vu_khi_tham_chieu.

### Phuong_tien_tham_chieu

103 dòng. Độ tin cậy: da_kiem_chung 24, uoc_dinh 28, ban_dau_doan 15, NEED_SOURCE 36. Loại: NEED_SOURCE 36, doi_that 67.

- `aa_vehicle` (Pháo cao xạ tự hành): mẫu thật: Flakpanzer Gepard (Oerlikon KDA 35 mm);Stinger / Starstreak; giống: Pháo phòng không tự hành hai nòng 35 mm có radar; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_flakpanzer_gepard, R_unit_sheet, R_machine_brigade_can_bang, R_aa_vehicle.
- `ammo_carrier` (Xe tiếp đạn): mẫu thật: M977 HEMTT;KamAZ-5350;M2 Browning 12,7 mm; giống: xe tải hậu cần chở đạn, súng máy trên vòng nóc; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_heavy_expanded_mobility_tactical_t, R_unit_sheet, R_machine_brigade_can_bang, R_ammo_carrier.
- `armored_bulldozer` (Xe ủi bọc thép): mẫu thật: IDF Caterpillar D9R; giống: Xe ủi bọc thép chiến đấu; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, D_caterpillar_d9r_specifications, R_unit_sheet, R_machine_brigade_can_bang, R_armored_bulldozer.
- `armored_car` (Xe bọc thép bánh lốp): mẫu thật: Pandur I 6x6;M242 Bushmaster 25 mm; giống: xe bọc thép 6x6 bánh lộ ngoài, tháp pháo tự động nhỏ; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_steyr_pandur, R_unit_sheet, R_machine_brigade_can_bang, R_armored_car.
- `artillery` (Lựu pháo tự hành): mẫu thật: CAESAR 155 mm;M284 155 mm (M109A6/A7); giống: Lựu pháo tự hành bánh lốp 6x6, nòng 155 mm đặt sau sàn xe; độ tin: da_kiem_chung; nguồn: R_unit_refs, R_reference_real, W_wikipedia_m109_howitzer, R_unit_sheet, R_machine_brigade_can_bang, R_artillery.
- `attack_helicopter` (Trực thăng tấn công): mẫu thật: AH-64D Apache Longbow;AGM-114L Hellfire Longbow;Ka-52 Alligator (model thay thế); giống: Trực thăng tấn công hai chỗ ngồi nối tiếp, radar trên trục rô-to; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_boeing_ah_64_apache, R_unit_sheet, R_machine_brigade_can_bang.
- `attack_jet` (Máy bay cường kích): mẫu thật: Su-25 Frogfoot;A-10 Thunderbolt II (model tank_buster);GSh-30-2 30 mm; giống: Máy bay cường kích yểm trợ mặt đất; độ tin: da_kiem_chung; nguồn: R_unit_refs, R_reference_real, W_wikipedia_sukhoi_su_25, R_unit_sheet, R_machine_brigade_can_bang, R_attack_jet.
- `ballistic_launcher` (Xe phóng tên lửa chiến thuật): mẫu thật: 9K720 Iskander (9M723); giống: Xe phóng tên lửa đạn đạo, dựng đứng tên lửa khi phóng; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_9k720_iskander, R_unit_sheet, R_machine_brigade_can_bang, R_ballistic_launcher.
- `command_vehicle` (Xe chỉ huy): mẫu thật: M1130 Stryker CV;BTR-80 KShM;LAV-C2; giống: Xe chỉ huy 8x8, cột ăng-ten kính viễn vọng gập; độ tin: da_kiem_chung; nguồn: R_unit_refs, R_reference_real, W_wikipedia_stryker, R_unit_sheet, R_machine_brigade_can_bang, R_command_vehicle.
- `drop_pod` (Khoang đổ bộ): mẫu thật: khoang hồi quyển Soyuz (tên lửa hãm); game: Halo;Warhammer 40,000; giống: khoang thả xe từ quỹ đạo; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_soyuz_spacecraft, R_drop_pod.
- `elite_aa` (Phòng không tinh nhuệ): mẫu thật: Rheinmetall Skyranger 35 (đạn AHEAD);Gepard (khung gốc); giống: Phòng không tinh nhuệ, đạn nổ trên không AHEAD; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_flakpanzer_gepard, R_elite_aa.
- `elite_apc` (Xe bọc thép tinh nhuệ): mẫu thật: M2 Bradley / BMP-3 (khung gốc);2A42 30 mm; giống: Xe chiến đấu bộ binh tinh nhuệ; độ tin: da_kiem_chung; nguồn: R_unit_refs, R_reference_real, W_wikipedia_m2_bradley, R_elite_apc.
- `elite_artillery` (Pháo tự hành tinh nhuệ): mẫu thật: CAESAR 155 mm; giống: Lựu pháo tự hành tinh nhuệ; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_caesar_self_propelled_howitzer.
- `elite_attack_helicopter` (Trực thăng tinh nhuệ): mẫu thật: AH-64 Apache;AGM-114L Hellfire Longbow; giống: Apache tinh nhuệ, bắn loạt Hellfire; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_boeing_ah_64_apache, R_elite_attack_helicopter.
- `elite_attack_jet` (Cường kích tinh nhuệ): mẫu thật: Su-25 Frogfoot;A-10 Thunderbolt II; giống: Cường kích tinh nhuệ; độ tin: da_kiem_chung; nguồn: R_unit_refs, R_reference_real, W_wikipedia_sukhoi_su_25.
- … 52 dòng có tham chiếu nữa: xem sheet Phuong_tien_tham_chieu.

Nguồn được dùng (tiêu đề như repo ghi; link khi repo có):

- `D_army_recognition_buk_m1_2`: Army Recognition 'Buk-M1-2' (độ tin 2)
- `D_caterpillar_d9r_specifications`: Caterpillar D9R specifications (độ tin 1)
- `D_rheinmetall_skyranger_30_35`: Rheinmetall Skyranger 30/35 (độ tin 1)
- `D_toyota_hilux_an10_an20_specifications`: Toyota Hilux AN10/AN20 specifications (độ tin 1)
- `D_us_army_fm_3_22_27`: US Army FM 3-22.27 (độ tin 1)
- `D_us_army_fm_3_22_65`: US Army FM 3-22.65 (độ tin 1)
- `D_us_army_m109a7_fact_file`: US Army M109A7 fact file (độ tin 1)
- `R_aa_vehicle`: spec dựng lại aa_vehicle (độ tin 3)
- `R_ammo_carrier`: spec dựng lại ammo_carrier (độ tin 3)
- `R_armored_bulldozer`: spec dựng lại armored_bulldozer (độ tin 3)
- `R_armored_car`: spec dựng lại armored_car (độ tin 3)
- `R_artillery`: spec dựng lại artillery (độ tin 3)
- `R_attack_jet`: spec dựng lại attack_jet (độ tin 3)
- `R_balance`: balance.json: tên thật của vũ khí (weapons[].real) (độ tin 3)
- `R_ballistic_launcher`: spec dựng lại ballistic_launcher (độ tin 3)
- `R_command_vehicle`: spec dựng lại command_vehicle (độ tin 3)
- `R_decisions`: Docs/DECISIONS.md (nhật ký quyết định) (độ tin 3)
- `R_drop_pod`: spec dựng lại drop_pod (độ tin 3)
- `R_elite_aa`: spec dựng lại elite_aa (độ tin 3)
- `R_elite_apc`: spec dựng lại elite_apc (độ tin 3)
- `R_elite_attack_helicopter`: spec dựng lại elite_attack_helicopter (độ tin 3)
- `R_elite_heavy_tank`: spec dựng lại elite_heavy_tank (độ tin 3)
- `R_elite_mbt`: spec dựng lại elite_mbt (độ tin 3)
- `R_elite_mlrs`: spec dựng lại elite_mlrs (độ tin 3)
- `R_elite_tank_destroyer`: spec dựng lại elite_tank_destroyer (độ tin 3)
- `R_engineer_vehicle`: spec dựng lại engineer_vehicle (độ tin 3)
- `R_ew_jammer`: spec dựng lại ew_jammer (độ tin 3)
- `R_flame_tank`: spec dựng lại flame_tank (độ tin 3)
- `R_fpv_carrier`: spec dựng lại fpv_carrier (độ tin 3)
- `R_full_weapon_audit`: full_weapon_audit.py: bảng REAL (nhịp bắn thật, mỗi dòng kèm nguồn) và WARHEAD (độ tin 3)
- … 138 nguồn nữa: xem sheet Nguon_tham_chieu của 08_tham_chieu.

Sheet 01_chien_dau/Vu_khi_so_sanh_that — Vũ khí: so sánh với thật: 246 dòng, 17 cột; bảng đầy đủ: xem sheet Vu_khi_so_sanh_that.

Sheet 01_chien_dau/Phuong_tien_so_sanh_that — Phương tiện: so sánh với thật: 221 dòng, 17 cột; bảng đầy đủ: xem sheet Phuong_tien_so_sanh_that.

## Các sheet của file

Mọi sheet, số dòng và ý nghĩa cột nằm trong 00_index.xlsx (Muc_luc_sheet, Schema). Sheet `input_<tên>` là bản chép của một sheet nguồn để công thức Excel đọc cùng file; sửa ở sheet nguồn, không sửa bản chép.

- `Vu_khi` (332 dòng): Vũ khí — Mỗi vũ khí (cả đạn thứ hai) một dòng: giá trị game (cột tiếng Việt) và trường gốc
- `Vu_khi_he_so_thuong` (27 dòng): Vũ khí: hệ số thưởng — bonuses[]: hệ số sát thương theo lớp / giáp / điều kiện
- `Ho_vu_khi` (105 dòng): Họ vũ khí — weaponFamilyTable: họ, bậc cỡ, số boss chung, biến thể và lý do
- `Ho_vu_khi_bien_the` (20 dòng): Họ vũ khí: biến thể — variants{}: biến thể của họ và lý do
- `Dong_vu_khi` (55 dòng): Dòng vũ khí thật — weaponFamilies + secondRounds.families: số chung của một hệ thống thật
- `Dan_thay_the` (68 dòng): Đạn thay thế — Liên kết vũ khí -> đạn thay thế (he, air, đạn thứ hai roundOf)
- `Bang_sat_thuong` (6 dòng): Bảng sát thương — damageTable: hệ số theo loại sát thương x mặt đất / máy bay / công trình
- `Bang_xuyen_giap` (6 dòng): Bảng xuyên giáp — damageTable.penetration: hệ số theo chênh xuyên - giáp (DamageTable.cs)
- `He_so_toan_cuc` (4 dòng): Hệ số toàn cục — firepower.* và damageTable.thermobaric: hệ số nhân chung
- `Khac_che` (21 dòng): Khắc chế (APS, phòng thủ điểm) — Mỗi đơn vị có hệ chặn: số lần, hồi, bán kính, loại đạn chặn
- `Phao_sang` (11 dòng): Pháo sáng — Mỗi đơn vị có pháo sáng: số lần, hồi, điểm phát Mount_Flare
- `Hanh_vi_dan` (11 dòng): Hành vi đạn: luật chung — munitionRules: pháo sáng mồi, ngòi cận đích, dẫn đường
- `Hanh_vi_dan_nhom` (7 dòng): Hành vi đạn theo nhóm — Mỗi dạng đạn (projectile): cách nhắm, khi nổ, cảnh báo (luật trong mã)
- `Drone` (13 dòng): Drone: tốc độ, đầu nổ, cỡ, vụ nổ — Mọi drone của game một dòng: drone đạn (FPV, Lancet, Shahed do xe phóng) và máy bay drone; tốc độ bay, đầu nổ (kg), sát thương, bán kính nổ lõi / rìa…
- `Canh_bao_vong` (13 dòng): Vòng cảnh báo — warningRules: loại đòn có vòng, sàn thời gian theo bậc, số vùng tối đa
- `Bom_rai_tham` (6 dòng): Ném bom rải thảm (liên kết) — Mỗi vũ khí thả bom một dòng: tham số dải chính (weapons[*].stick) và câu thẻ; bảng đủ (Bom_vu_khi, Bom_don_vi, Bom_hanh_vi, Bom_vet_tha, Bom_canh_bao…
- `Vu_khi_suy_ra` (332 dòng): Vũ khí: suy ra — Lớp B: chu kỳ, sát thương loạt, DPS duy trì theo giáp / công trình / máy bay, cảnh báo: công thức sống trên Vu_khi và các bảng hệ số, kèm cột _game (…
- `Vu_khi_tham_chieu` (332 dòng): Vũ khí: tham chiếu ngoài đời — Mỗi vũ khí một dòng: mẫu thật (tên thật balance.json), nhịp thật (bảng REAL), đầu đạn (WARHEAD), ghi chú bảng cân bằng (spec 12.2; chỉ dữ liệu có tro…
- `Vu_khi_so_sanh_that` (246 dòng): Vũ khí: so sánh với thật — So sánh game với thật (spec 12.4): mỗi thông số có đối chiếu một dòng; ty_le = game / thật, khoảng cho phép, co_lech_lon = ngoài khoảng mà không có c…
- `Xe` (79 dòng): Xe — Mỗi xe / máy bay / tàu của người chơi và địch, cả tinh nhuệ (elite): giá trị game và trường gốc
- `Xe_vu_khi` (76 dòng): Xe: bệ vũ khí phụ — secondary[]: bệ phụ (chỉ số bệ = thu_tu + 1; bệ 0 là vũ khí chính)
- `Xe_ten_lua` (3 dòng): Xe: tên lửa mang — missiles[]
- `Xe_bo_phan` (6 dòng): Xe: bộ phận — parts[] của xe không phải boss
- `The_ho_tro` (24 dòng): Thẻ hỗ trợ — supports[]: pháo kích, không kích, khói, thả hộ tống...
- `Ky_nang` (22 dòng): Kỹ năng nội tại — skills[]: khiên, khói, sửa... của xe, elite, boss
- `Tinh_nhue_luat` (20 dòng): Luật tinh nhuệ — elites: hệ số giá / máu / sát thương, ngân sách và trần theo độ khó
- `Nhanh_xe` (4 dòng): Nhánh quân — branches: nhánh -> các lớp xe
- `Do_ben` (2 dòng): Hệ số độ bền — toughness: máu trong trận = hp x hệ số (xe, boss)
- `Trang_bi` (38 dòng): Trang bị: loại cơ bản — 38 loại trang bị (ô, chỉ số ngầm, giá trị đỉnh 5 hạng, đánh đổi)
- `Trang_bi_mo_dun` (14 dòng): Trang bị: mô-đun đặc biệt — 14 mô-đun (Sử thi / Huyền thoại); FlareDispenser, TrophyAps chỉ nâng cấp hệ có sẵn
- `Trang_bi_dac_tinh` (45 dòng): Trang bị: đặc tính — 45 đặc tính (giá trị Sử thi / Huyền thoại)
- `Trang_bi_dong_phu` (23 dòng): Trang bị: dòng phụ — dòng phụ: giá trị theo hạng, ô được ra, trọng số
- `Trang_bi_bo` (13 dòng): Trang bị: bộ (brand) — bộ trang bị: thưởng 2 món / 4 món
- `Commander` (22 dòng): Commander và nội tại tướng — Commanders.cs: 14 commander của người chơi + nội tại 8 tướng địch
- `Commander_noi_tai` (45 dòng): Commander: dòng nội tại — Lines: chỉ số, giá trị, phạm vi
- `Commander_gia` (5 dòng): Commander: hệ số giá — Prices: phạm vi giá, hệ số
- `Doi_mo_man` (23 dòng): Đội mở màn — openingSquads.commanders / generals: vai trò của đội mở màn
- `Doi_mo_man_vai_tro` (18 dòng): Đội mở màn: vai trò — openingSquads.roles: thẻ chọn được cho mỗi vai trò
- `Doi_mo_man_luat` (3 dòng): Đội mở màn: luật — openingSquads.share / modes / enemyModes
- `Xe_tham_chieu` (6 dòng): Xe tham chiếu — Xe tham chiếu của Boss_hieu_qua (spec 03 B) và xe chậm tham chiếu của vòng cảnh báo
- `Xe_suy_ra` (79 dòng): Xe: suy ra — Lớp B: DPS vũ khí chính trên xe (màn chi tiết), máu / CP, DPS / CP, tỷ lệ so với đường cong máu của đội hình (Hoi_quy)
- `Hoi_quy_du_lieu` (50 dòng): Hồi quy: dữ liệu — Xe vào hồi quy (bộ lọc chuẩn: bỏ CP 0, Support, Scout; chỉ xe thẻ, không tinh nhuệ, có máu): ln CP, ln máu, ln DPS = max(nhẹ giáp 1, nặng giáp 3, máy…
- `Hoi_quy` (12 dòng): Hồi quy theo CP — Số mũ và hệ số của máu và DPS theo CP (máu = a x CP^b, bình phương nhỏ nhất trên ln), N, trung vị máu / CP và DPS / CP theo dải CP (<= 8, 9-15, >= 16)
- `May_bay_so_phat` (14 dòng): Máy bay: số phát để hạ — Mỗi máy bay: máu trong trận, giáp, sát thương một phát và số phát của tên lửa tham chiếu (Stinger, Buk, AMRAAM) để hạ (DamageTable.Effective, Air)
- `Doi_mo_man_suy_ra` (23 dòng): Đội mở màn: suy ra — baseCP ước tính của đội mở màn (bộ bài trống: thẻ rẻ nhất mỗi vai trò, Doi_mo_man_vai_tro.re_nhat_cp); % CP khởi đầu theo chế độ cần CP khởi đầu của…
- `Phuong_tien_tham_chieu` (103 dòng): Phương tiện: tham chiếu ngoài đời — Mỗi xe và thẻ hỗ trợ một dòng: mẫu thật, phim / game (unit_refs.json), kích thước thật (reference_real.json), bảng cân bằng (spec 12.2; chỉ dữ liệu c…
- `Phuong_tien_so_sanh_that` (221 dòng): Phương tiện: so sánh với thật — So sánh game với thật (spec 12.4): mỗi thông số có đối chiếu một dòng; ty_le = game / thật, khoảng cho phép, co_lech_lon = ngoài khoảng mà không có c…
- `So_tay_dan` (2 dòng): Sổ tay đạn — balance.json handbook: xe mẫu bắn và xe mẫu bị bắn của sổ tay đạn trên giao diện
- `Hang_so_vu_khi` (33 dòng): Hằng số vũ khí, đạn, sát thương và nổ — Assets/MachineBrigade/Resources/Data/tunables.json: 'weapons' (lớp chủ → tên): một dòng một hằng số; mã game đọc qua SimTunables, giữ nguyên giá trị…
- `Hang_so_phuong_tien` (94 dòng): Hằng số phương tiện: giá, thả dù, hồi đạn, tiếp tế, kỹ năng — Assets/MachineBrigade/Resources/Data/tunables.json: 'vehicles' (lớp chủ → tên): một dòng một hằng số; mã game đọc qua SimTunables, giữ nguyên giá trị…
- `Bom_vu_khi` (14 dòng): Ném bom: vũ khí — Mỗi vũ khí thả bom và mỗi đòn không kích / đòn lớn của boss một dòng: tham số dải bom (stick), khoảng cách giữa bom, độ dài dải, cảnh báo, đường thả…
- `Bom_don_vi` (17 dòng): Ném bom: đơn vị mang — Đơn vị mang bom: tốc độ, bán kính quay, độ cao thả, vũ khí bom, số bom mỗi lượt
- `Bom_hanh_vi` (18 dòng): Ném bom: hành vi theo mã — Từng bước hành vi ném bom theo mã (chọn mục tiêu, hướng vào, thả, rơi) và file hàm
- `Bom_canh_bao` (14 dòng): Ném bom: vòng cảnh báo — Vòng cảnh báo của bom theo luật (hình dạng, bán kính lõi và rìa, thời gian cảnh báo)
