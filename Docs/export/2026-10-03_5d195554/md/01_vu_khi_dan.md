# 01_vu_khi_dan — Vũ khí và đạn

Bộ xuất dữ liệu Machine Brigade, commit 5d195554, ngày 2026-10-03. Sinh bởi `python Tools/export/export.py` (lượt 6): bảng in đúng ô của csv / xlsx; văn bản lấy từ tài liệu thiết kế (Tools/docs) và chuỗi trong game. Toàn văn: Machine_Brigade_Design_FULL_2026-10-03.md.

Vũ khí, họ, dòng vũ khí thật, đạn thay thế, bảng sát thương, khắc chế (APS), hành vi đạn, pháo sáng, vòng cảnh báo

Mục trong file này: 10. Vũ khí và bảng sát thương; 10i. Sổ tay đạn; 10j. Họ vũ khí, hành vi đạn và vòng cảnh báo.

## 10. Vũ khí và bảng sát thương

Trạng thái: Đã áp

Nguồn dữ liệu: 01_vu_khi_dan/Bang_sat_thuong; 01_vu_khi_dan/Bang_xuyen_giap; 01_vu_khi_dan/Khac_che; 01_vu_khi_dan/He_so_toan_cuc; 01_vu_khi_dan/Vu_khi; 01_vu_khi_dan/Vu_khi_suy_ra; 01_vu_khi_dan/Vu_khi_he_so_thuong; 01_vu_khi_dan/Dan_thay_the; 01_vu_khi_dan/Phao_sang. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §10. Vũ khí, §10b, §10c, §10e, §10f, §Cân bằng đợt 2.

#### 10. Vũ khí và bảng sát thương

#### Hệ số sát thương theo loại đạn và loại giáp

Prompt 15: mỗi mặt giáp (trước, hông, sau, nóc) có cấp 0–4 (boss tới cấp 5, giáp siêu dày: DECISIONS 21G), mỗi vũ khí có cấp xuyên 0–4. Sát thương nhân theo cấp xuyên so với cấp giáp của mặt trúng đạn: hơn từ 2 cấp ×1.2, hơn 1 cấp ×1, ngang cấp ×0.85, thiếu 1 cấp ×0.5, thiếu 2 cấp ×0.25, thiếu từ 3 cấp ×0.1; đầu nổ nhiệt áp ×2 (xem DECISIONS 14A). Bảng hiệu quả và ký hiệu ✓ ~ ✕ của từng xe nằm ở thẻ xe (phần 8).

Giáp có hướng (giáp mặt trước dày hơn hông/sau), đạn lệch theo tầm và chuyển động, pháo có tầm tối thiểu. Máy bay có pháo sáng, xe có hệ thống đánh chặn chủ động (APS) chặn tên lửa/drone, tàng hình chỉ lộ ở 40% tầm nhìn khi không bắn. Ký hiệu: ✓ hệ số từ 0.6 trở lên, ~ từ 0.12, ✕ thấp hơn (cùng ngưỡng với giao diện trong game).

#### Khắc chế: phòng vệ chặn loại đạn nào

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

Luật này được test `ArmourTests.CountersFollowTheTable` kiểm tra (bảng gốc ở DECISIONS 14A C.9).

#### 10b. Nhịp bắn, nạp đạn, đường đạn và di chuyển

Đọc thẳng từ dữ liệu game. **Viên/s** là nhịp khi đang bắn (trong một loạt, hoặc giữa hai phát). **Xả** là thời gian hết một băng hay một loạt. **Nghỉ/nạp** là thời gian thay băng hay nghỉ giữa hai loạt. **Bệ phóng** là số lượt bắn trước khi phải nạp lại cả bệ. **TB viên/s** tính cả thời gian nghỉ và nạp. **DPS khi xả** là sát thương mỗi giây trong lúc bắn, trước giáp; **DPS duy trì** tính cả thời gian nạp (prompt 13). **Xoay thân / tháp** tính bằng độ mỗi giây, như balance.json (mã giữ radian mỗi giây; bản trước in số radian dưới nhãn °/s, prompt 25 C.4).

#### Kích thước đạn (55 model)

Kích thước model đạn nhân tỷ lệ của vũ khí (projectileScale).

#### 10c. Tầm nổ

Bán kính nổ lan (m) của mọi bom, tên lửa, rốc-két, đạn pháo và drone; của các thẻ hỗ trợ hỏa lực; của đòn lớn của boss; và của vụ nổ khi xe, tháp, boss bị phá. "Trúng trực tiếp" là quả chỉ gây sát thương cho mục tiêu nó trúng. Sát thương là mỗi phát, trước giáp.

#### 10e. DPS theo cấp giáp, tên lửa, kích thước và siêu vũ khí (prompt 25)

#### DPS theo cấp giáp (234 vũ khí)

DPS duy trì (prompt 13: cả loạt, băng, thay băng, nạp bệ) nhân hệ số của vũ khí lên từng cấp giáp 0–5 (5 là giáp boss), lên máy bay và lên công trình (loại sát thương × bước xuyên, bảng hiệu quả ✓ ~ ✕ của thẻ xe; đạn đánh nóc tính vào nóc). Mặt trúng là mặt trước ở cấp đó. Thưởng theo lớp giáp (ví dụ phá công sự) tính luôn; thưởng theo loại xe, đứng yên hay đánh sườn ghi ở thẻ xe.

#### Tên lửa: tốc độ bay và thời gian bay (61)

Tốc độ bay (m/s) và thời gian bay tới tầm xa nhất (tầm / tốc độ; tên lửa dẫn đường bay một thời gian định lúc phóng và trúng nơi mục tiêu đang đứng khi tới). Cột nhanh hơn: tốc độ tên lửa phòng không so với máy bay nhanh nhất trong game (60 m/s; file cân bằng nhắm 1,2–1,5 lần mục tiêu nhanh nhất cần bắt).

#### Kích thước model theo dữ liệu (151 đơn vị)

modelSize (prompt 25 B1): hộp của model kể cả nòng, dài × rộng × cao (m), theo sheet Kiểm tra từng mục (mặt đất 0,8 × thật, trên không 0,4 × thật); game vẽ model khớp chiều dài này. Thân va chạm: dài và rộng.

#### Kích thước đạn theo dữ liệu (54 vũ khí)

roundLength (prompt 25 B3): chiều dài đạn vẽ (m): 0,8 × thật khi phóng từ mặt đất, 0,5 × thật từ máy bay, tối thiểu 0,8 m; đạn 203 mm bằng 1,3 lần 155 mm. Game vẽ model đạn khớp chiều dài này.

| Vũ khí | Tên thật | Model đạn | Dài đạn (m) | Trên |
|---|---|---|---|---|
| `anti_radar_missile` | AGM-88 HARM | harm | 2,09 | TK đánh chặn |
| `apkws_rocket` | APKWS (laser-guided Hydra 70) | apkws | 0,8 | TT tấn công |
| `avenger_stingers` | Starstreak / Stinger SHORAD (Avenger pods) | shorad_dart | 1,22 | TL PK nhẹ |
| `bomber_payload` | FAB-500 (500 kg) | bomb | 1,2 | Oanh tạc cơ |
| `boss_missiles` | 9M133 Kornet | atgm_kornet | 0,96 | Behemoth của Mara |
| `buk_launcher` | 9M317 Buk | buk | 4,44 | PK tầm trung |
| `bunker_buster_bomb` | GBU-28 | gbu_28 | 2,92 | Ném bom lượn |
| `caesar_155` | 155 mm L/52 (CAESAR) | shell_155 | 0,8 | Pháo bánh lốp |
| `coyote_interceptor` | Coyote Block 2 | coyote_block2 | 0,8 | Drone chặn |
| `cruiser_203` | Mk 71 203 mm (twin) | shell_155 | 1,04 | Tuần dương hạm |
| `fpv_fibre` | Fibre-optic FPV drone (1.5 kg) | fpv_drone | 0,8 | FPV cáp quang |
| `fpv_hangar` | FPV drone (1.5 kg) | fpv_drone | 0,8 | Nhà chứa drone |
| `fpv_hangar_swarm` | FPV drone (1.5 kg) | fpv_drone | 0,8 | Bầy đàn |
| `fpv_swarm` | FPV drone (1.5 kg) | fpv_drone | 0,8 | Drone FPV, Drone FPV TN |
| `fpv_swarm_mini` | Switchblade 300 | switchblade_300 | 0,8 | FPV cáp quang |
| `glide_fab500` | FAB-500 M-62 with UMPK glide kit | bomb | 1,2 | Ném bom lượn |
| `guided_bomb` | GBU-39 SDB (110 kg) | gbu39 | 0,9 | Morrigan, TK tàng hình, UAV tấn công |
| `gun_155_coastal` | M284 155 mm (coastal battery) | shell_155 | 0,8 | Pháo bờ biển |
| `gun_155_twin_ap` | M284 155 mm (twin) AP | shell_155 | 0,8 | Pháo hạng nặng, Pháo đài thép |
| `gun_155_twin_coastlr` | M284 155 mm (twin, long-range coastal) | shell_155 | 0,8 | Pháo bờ biển |
| `howitzer` | M284 155 mm | shell_155 | 0,8 | Lựu pháo, Lựu pháo TN |
| `howitzer_cb` | M284 155 mm | shell_155 | 0,8 | Phản pháo |
| `howitzer_fixed` | M284 155 mm | shell_155 | 0,8 | Trận địa pháo |
| `jassm` | AGM-158 JASSM (450 kg) | jassm | 2,13 | Máy bay mẹ, OTC tàng hình |
| `jet_bombs` | FAB-250 (250 kg) | bomb_fab | 0,98 | Cường kích, Cường kích TN, Tàng hình hạm |
| `kh29` | Kh-29L | kh29l | 1,95 | Cường kích, Cường kích TN |
| `kornet_multi` | 9M133 Kornet | atgm_kornet | 0,96 | Đa năng |
| `kornet_top` | 9M133 Kornet | atgm_kornet | 0,96 | Đánh từ trên |
| `mortar_240_fixed` | 2B8 240 mm (emplacement) | mortar_bomb | 1,2 | Cối nặng |
| `one_shot_kornet` | 9M133 Kornet | atgm_kornet | 0,96 | TL một lần |
| `p26_bastion_main_b155` | M284 155 mm (Bastion) | shell_155 | 0,8 | Bastion, Monster |
| `p26_bastion_sec_b240` | 2B8 240 mm | mortar_bomb | 1,2 | Bastion, Bastion Mk.0, Monster |
| `p26_bastion_tiny_kornet_twin` | 9M133 Kornet | atgm_kornet | 0,96 | Bastion, Monster |
| `p26_behemoth_tiny_boss_missiles` | 9M133 Kornet | atgm_kornet | 0,96 | Behemoth |
| `p26_behemoth_tiny_kornet_twin` | 9M133 Kornet | atgm_kornet | 0,96 | Behemoth |
| `p26_jotunn_jo203` | 2A44 203 mm | shell_155 | 1,04 | Jötunn |
| `p26_leviathan_lev406` | Mk 7 406 mm/50 (Iowa, triple) | shell_155 | 1,56 | Kraken, Leviathan |
| `p26_leviathan_sec_lev155` | 155 mm/60 (triple) | shell_155 | 0,8 | Kraken, Leviathan |
| `p26_matriarch_direct_ma_atgm` | 9M133 Kornet | atgm_kornet | 0,96 | Matriarch, Stymphalos |
| `p26_roc_direct_roc_atgm` | Kornet (dropped from the bay) | atgm_kornet | 0,96 | Garuda, Roc |
| `p26_roc_main_roc_bombs` | bomb-bay stick 400 kg | shell_155 | 1,04 | Argus, Garuda, Roc |
| `patriot` | MIM-104 Patriot PAC-2 | patriot | 4,24 | Trạm PK tầm xa |
| `sam` | Starstreak / Stinger SHORAD | shorad_dart | 1,22 | Cao xạ, Phòng không TN, Tháp PK, Tổ vác vai |
| `sam_48n6` | S-400 48N6 | patriot | 6 | PK tầm xa, SAM tầm xa TN |
| `sam_battery` | MIM-104 Patriot PAC-2 | patriot | 4,24 | Nemesis |
| `sam_battery_lrr` | MIM-104 Patriot PAC-2 | patriot | 4,24 | Radar tầm xa |
| `sam_pac3` | Patriot PAC-3 MSE | patriot | 4,24 | PAC-3 |
| `sam_post` | 9M317 Buk | buk | 4,44 | Jötunn, Kraken, Leviathan, Typhon |
| `siege_mortar_240` | 2B8 240 mm (siege tank) | mortar_bomb | 1,2 | Công thành |
| `stealth_payload` | GBU-31 JDAM (907 kg) | jdam | 1,94 | OTC tàng hình |
| `stinger_post` | FIM-92 Stinger (tower post) | shorad_dart | 1,22 | Stinger |
| `swarm_drones` | FPV drone (1.5 kg) | fpv_drone | 0,8 | Máy bay mẹ |
| `thermobaric_bomb` | ODAB-500 | odab_500 | 1,23 | Ném bom lượn |
| `tower_kornet` | 9M133 Kornet | atgm_kornet | 0,96 | Tháp ATGM |

#### Siêu vũ khí của boss chủ lực (16)

Prompt 25 C1: chỉ 16 boss chủ lực có siêu vũ khí (đòn lớn của prompt 18 với số của file cân bằng); mini boss không có. Mỗi siêu vũ khí có âm cảnh báo riêng. Số ở đây là số gốc; trong trận cộng hệ số của cấp boss chủ lực (sát thương ×1,2, hồi ×0,85) và của độ khó.

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

#### 10f. Đạn thay thế (hai loại đạn)

Prompt 25 G: nhiều súng nạp được loại đạn thứ hai; súng tự chọn theo mục tiêu (xe giáp, xe nhẹ, máy bay, công trình), đổi đạn mất thời gian nạp của chính súng (tối thiểu 0,5 s) và giữ loại đạn ít nhất 2 s. Nhịp bắn, tầm và băng đạn vẫn là của súng; chỉ loại sát thương, xuyên, sát thương, nổ lan và dạng đạn đổi. Cột cuối là đạn gốc của súng (sát thương / nổ lan m). Biểu tượng đổi đạn nằm trên ô vũ khí của thẻ, trang chi tiết xe và bảng hiệu ứng. Chưa cân bằng lại: số theo file Excel và số của súng.

#### Cân bằng đợt 2

Áp từ manifest của file cân bằng đợt 2 (bản v2) bằng `Tools/balance/p29_apply.py`; nhật ký ở `Docs/balance/apply_log_p29.md`. Máu hiển thị = máu dữ liệu × độ lì (2,2). Hệ số sát thương nhân mọi vũ khí của xe, không sửa vũ khí dùng chung.

#### Pháo sáng (số lần dự trữ)

Hồi một lần khi ở vòng chờ, nạp đầy khi về Bãi đáp hoặc sở chỉ huy. Mồi bẫy nhiệt: +1 lần, hồi nhanh hơn 25%, chỉ cho đơn vị đã có pháo sáng.

#### APS

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

#### Gungnir

Boss chủ lực chương 11: máu 133.365; siêu vũ khí mỗi 45 s, nhắm toàn bản đồ, cảnh báo 3 s có đường ngắm; xuyên tối đa 5 xe × 1.000 rồi nổ 2.000 ở xe cuối (lõi 12 m, rìa 20 m còn 40%); không bắn máy bay, không chặn được, pháo sáng và APS không có tác dụng.

Sheet: 01_vu_khi_dan/Bang_sat_thuong — Bảng sát thương (6 dòng, 6 cột)

| id | mat_dat | may_bay | cong_trinh |
|---|---|---|---|
| Energy | 1.0 | 1.5 | 0.5 |
| Fire | 1.5 | 0.0 | 1.0 |
| Fragmentation | 0.5 | 1.3 | 0.1 |
| HighExplosive | 1.0 | 0.0 | 1.5 |
| Kinetic | 1.0 | 0.3 | 0.6 |
| ShapedCharge | 1.0 | 0.3 | 0.6 |

Sheet: 01_vu_khi_dan/Bang_xuyen_giap — Bảng xuyên giáp (6 dòng, 5 cột)

| id | chenh_xuyen_giap | he_so |
|---|---|---|
| buoc_0 | +2 | 1.2 |
| buoc_1 | +1 | 1.0 |
| buoc_2 | 0 | 0.85 |
| buoc_3 | -1 | 0.5 |
| buoc_4 | -2 | 0.25 |
| buoc_5 | -3 | 0.1 |

Sheet: 01_vu_khi_dan/Khac_che — Khắc chế (APS, phòng thủ điểm) (22 dòng, 28 cột)

| id | loai_don_vi | he_phong_ve | chan_directMissile | chan_drone | chan_directRocket | chan_artilleryRocket | chan_mortarShell | chan_artilleryShell | chan_tankShell |
|---|---|---|---|---|---|---|---|---|---|
| behemoth | boss | SELF_APS | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| behemoth_mk0 | boss |  | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| behemoth_tempest | boss | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| c_ram | thap | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| c_ram.centurion | thap | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| c_ram.dome | thap | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| cerberus | boss |  | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| daedalus | boss | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| headquarters.shield | cong_trinh | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| icarus_mk0 | boss | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| iron_beam | xe | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| landing_hovercraft | boss | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| laser_ad_station | thap | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| leviathan | boss | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| main_battle_tank | xe | SELF_APS | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| mara_behemoth | xe | SELF_APS | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| missile_battery.pac3 | thap | SELF_APS | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| next_gen_tank | xe | SELF_APS | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| sea_corvette | xe | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| sea_cruiser | xe | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| silver_bug | boss | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| titan_tank | xe | SELF_APS | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |

*in 10 / 28 cột; 15 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 01_vu_khi_dan/He_so_toan_cuc — Hệ số toàn cục (4 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so |
|---|---|---|---|
| damageTable.thermobaric | damageTable | thermobaric | 2.0 |
| firepower.propBlasts | firepower | propBlasts | 1.5 |
| firepower.strikes | firepower | strikes | 2.0 |
| firepower.vehicleBlasts | firepower | vehicleBlasts | 2.0 |

Sheet: 01_vu_khi_dan/Vu_khi — Vũ khí (372 dòng, 174 cột)

| id | ten_that | ho_id | bien_the_id | dong_vu_khi_id | nhom | co_mm | dau_no_kg | loai_sat_thuong | xuyen |
|---|---|---|---|---|---|---|---|---|---|
| aa_25_triple | Type 96 25 mm (triple) | cal_25 | flak |  | autocannon | 25 |  | Fragmentation | 1 |
| aa_25_triple_ap | Type 96 25 mm AP (triple) | cal_25 |  |  | autocannon | 25 |  | Kinetic | 2 |
| agl_40 | Mk 19 40 mm | gl_40 |  | mk_19_40_mm | grenade | 40 |  | HighExplosive | 2 |
| aim9 | AIM-9 Sidewinder | sam_aim_9_sidewinder |  | aim_9_sidewinder | aa_missile |  | 9.4 | Fragmentation | 2 |
| air_cruise_missile | Kh-101 (400 kg) | cruise_kh_101 |  |  | cruise |  | 400 | HighExplosive | 3 |
| air_to_air | AIM-120 AMRAAM | sam_aim_120_amraam |  |  | aa_missile |  | 20 | Fragmentation | 3 |
| airship_drones | FPV drone (1.5 kg) | drone_fpv_drone |  | fpv_drone | drone |  | 1.5 | ShapedCharge | 3 |
| airship_flak | S-60 57 mm | cal_57 | flak |  | autocannon | 57 |  | Fragmentation | 2 |
| amos_120 | 120 mm AMOS (twin) | cal_120_he | mortar |  | mortar | 120 |  | HighExplosive | 2 |
| anti_radar_missile | AGM-88 HARM | msl_agm_88_harm |  | agm_88_harm | missile |  | 68 | HighExplosive | 3 |
| anti_ship_missile | NSM / P-800 Oniks | msl_nsm_p_800_oniks |  | nsm_oniks | missile |  | 250 | HighExplosive | 4 |
| apkws_rocket | APKWS (laser-guided Hydra 70) | rkt_70_80 | guided | apkws | rocket | 70 |  | ShapedCharge | 2 |
| at_gun_100 | MT-12 Rapira 100 mm | cal_100_105_ap |  |  | tank_gun | 100 |  | Kinetic | 3 |
| ataka | 9M120 Ataka | atgm_9m120_ataka |  | 9m120_ataka | atgm |  | 7.4 | ShapedCharge | 4 |
| atgm | BGM-71 TOW-2 | atgm_bgm_71_tow_2 |  |  | atgm |  | 5.9 | ShapedCharge | 4 |

*15 / 372 dòng đầu: xem sheet 01_vu_khi_dan/Vu_khi; in 10 / 174 cột; 82 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 01_vu_khi_dan/Vu_khi_suy_ra — Vũ khí: suy ra (372 dòng, 55 cột)

| id | bac_so | vien_moi_lan_bop | vien_moi_lan_bop_game | vien_moi_chu_ky | vien_moi_chu_ky_game | chu_ky_day_du_s | chu_ky_day_du_s_game | sat_thuong_moi_loat | sat_thuong_moi_loat_game |
|---|---|---|---|---|---|---|---|---|---|
| aa_25_triple | 1 | 1.0 | 1 | 15 | 15 | 3.1 | 3.1 | 255.0 | 255.0 |
| aa_25_triple_ap | 1 | 1.0 | 1 | 15 | 15 | 3.1 | 3.1 | 255.0 | 255.0 |
| agl_40 | 1 | 1.0 | 1 | 6.0 | 6 | 4.2 | 4.2 | 156.0 | 156.0 |
| aim9 | 2 | 1.0 | 1 | 1.0 | 1 | 8.0 | 8.0 | 236.0 | 236.0 |
| air_cruise_missile | 4 | 1.0 | 1 | 1.0 | 1 | 11.2 | 11.2 | 378.0 | 378.0 |
| air_to_air | 2 | 1.0 | 1 | 1.0 | 1 | 3.99 | 3.99 | 294.0 | 294.0 |
| airship_drones | 2 | 1.0 | 1 | 3.0 | 3 | 9.049999999999999 | 9.049999999999999 | 420.0 | 420.0 |
| airship_flak | 2 | 1.0 | 1 | 8 | 8 | 4.88 | 4.88 | 560.0 | 560.0 |
| amos_120 | 3 | 1.0 | 1 | 4.0 | 4 | 10.75 | 10.75 | 600.0 | 600.0 |
| anti_radar_missile | 3 | 1.0 | 1 | 1.0 | 1 | 8.0 | 8.0 | 300.0 | 300.0 |
| anti_ship_missile | 4 | 1.0 | 1 | 1.0 | 1 | 30.0 | 30.0 | 450.0 | 450.0 |
| apkws_rocket | 2 | 1.0 | 1 | 1.0 | 1 | 1.0 | 1.0 | 90.0 | 90.0 |
| at_gun_100 | 2 | 1.0 | 1 | 1.0 | 1 | 5.0 | 5.0 | 200.0 | 200.0 |
| ataka | 2 | 1.0 | 1 | 2.0 | 2 | 11.42 | 11.42 | 494.0 | 494.0 |
| atgm | 2 | 1.0 | 1 | 1.0 | 1 | 12.33 | 12.33 | 190.0 | 190.0 |

*15 / 372 dòng đầu: xem sheet 01_vu_khi_dan/Vu_khi_suy_ra; in 10 / 55 cột; 43 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 01_vu_khi_dan/Vu_khi_he_so_thuong — Vũ khí: hệ số thưởng (31 dòng, 10 cột)

| id | vu_khi_id | thu_tu | armor | class | flank | mult | still |
|---|---|---|---|---|---|---|---|
| anti_radar_missile/0 | anti_radar_missile | 0 |  | AntiAir |  | 2 |  |
| borer_drill/0 | borer_drill | 0 | Structure |  |  | 2 |  |
| bucket_wheel/0 | bucket_wheel | 0 | Structure |  |  | 3 |  |
| bunker_buster_bomb/0 | bunker_buster_bomb | 0 | Structure |  |  | 2 |  |
| detonator/0 | detonator | 0 | Structure |  |  | 0.5 |  |
| dozer_blade/0 | dozer_blade | 0 | Structure |  |  | 3 |  |
| dozer_blade/1 | dozer_blade | 1 | Heavy |  |  | 0.4 |  |
| dozer_blade/2 | dozer_blade | 2 | Light |  |  | 0.55 |  |
| drone_missile/0 | drone_missile | 0 | Structure |  |  | 1.5 |  |
| flak_35/0 | flak_35 | 0 |  | Plane |  | 1.5 |  |
| fpv_swarm/0 | fpv_swarm | 0 | Structure |  |  | 1.5 |  |
| gun_105_wheeled/0 | gun_105_wheeled | 0 |  |  | TRUE | 1.25 |  |
| gun_203_siege/0 | gun_203_siege | 0 | Structure |  |  | 2.4 |  |
| howitzer_cb/0 | howitzer_cb | 0 |  | Artillery |  | 1.25 |  |
| kornet_multi/0 | kornet_multi | 0 | Light |  |  | 0.6 |  |
| kornet_multi/1 | kornet_multi | 1 | Heavy |  |  | 0.85 |  |
| lancet/0 | lancet | 0 |  | Artillery |  | 2 |  |
| lancet/1 | lancet | 1 |  |  |  | 2 | 3 |
| lancet/2 | lancet | 2 | Structure |  |  | 1.5 |  |
| siege_mortar_240/0 | siege_mortar_240 | 0 | Structure |  |  | 2 |  |
| swarm_drones/0 | swarm_drones | 0 | Structure |  |  | 1.5 |  |
| technical_rockets/0 | technical_rockets | 0 | Structure |  |  | 0.6 |  |
| tower_flak_30/0 | tower_flak_30 | 0 | Light |  |  | 0.48 |  |
| tower_flak_30/1 | tower_flak_30 | 1 | Heavy |  |  | 0.4 |  |
| tower_kornet/0 | tower_kornet | 0 | Light |  |  | 0.4 |  |
| turret_gmlrs/0 | turret_gmlrs | 0 |  | Artillery |  | 1.5 |  |
| turret_gmlrs/1 | turret_gmlrs | 1 | Structure |  |  | 1.5 |  |
| turret_gun_120/0 | turret_gun_120 | 0 | Light |  |  | 0.65 |  |
| turret_rockets/0 | turret_rockets | 0 | Heavy |  |  | 0.46 |  |
| twin_30_flak/0 | twin_30_flak | 0 |  | Plane |  | 1.25 |  |
| twin_35_ahead/0 | twin_35_ahead | 0 |  | Plane |  | 1.5 |  |

Sheet: 01_vu_khi_dan/Dan_thay_the — Đạn thay thế (70 dòng, 15 cột)

| id | vu_khi_goc | dan_id | lien_ket | loai_dan | dung_cho | loai_sat_thuong | xuyen | sat_thuong_moi_phat | loi_m |
|---|---|---|---|---|---|---|---|---|---|
| aa_25_triple/aa_25_triple_ap | aa_25_triple | aa_25_triple_ap | roundOf | ap | ground | Kinetic | 2 | 17 | 0 |
| autocannon_25/autocannon_25_flak | autocannon_25 | autocannon_25_flak | roundOf | flak | air | Fragmentation | 1 | 17 | 2 |
| autocannon_30/autocannon_30_flak | autocannon_30 | autocannon_30_flak | roundOf | flak | air | Fragmentation | 2 | 22 | 2.5 |
| autocannon_40/autocannon_40_flak | autocannon_40 | autocannon_40_flak | roundOf | flak | air | Fragmentation | 2 | 30 | 3.5 |
| bastion_gun/bastion_gun_he | bastion_gun | bastion_gun_he | roundOf | he | light;structure | HighExplosive | 3 | 320 | 6.5 |
| bomber_tail_guns/bomber_tail_guns_api | bomber_tail_guns | bomber_tail_guns_api | roundOf | api | any | Kinetic | 2 | 9.5 | 0.0 |
| borer_cannon/borer_cannon_he | borer_cannon | borer_cannon_he | roundOf | he | light;structure | HighExplosive | 2 | 120 | 3 |
| boss_flak/boss_flak_ap | boss_flak | boss_flak_ap | roundOf | ap | ground | Kinetic | 2 | 25 | 0 |
| boss_heli_gun/boss_heli_gun_flak | boss_heli_gun | boss_heli_gun_flak | roundOf | flak | air | Fragmentation | 2 | 22 | 2.5 |
| boss_hmg/boss_hmg_api | boss_hmg | boss_hmg_api | roundOf | api | any | Kinetic | 2 | 15 | 0 |
| boss_howitzer/boss_howitzer_guided | boss_howitzer | boss_howitzer_guided | roundOf | guided | armour | HighExplosive | 4 | 420 | 8 |
| bunker_hmg/bunker_hmg_api | bunker_hmg | bunker_hmg_api | roundOf | api | any | Kinetic | 2 | 9.5 | 0 |
| bunker_hmg_twin/bunker_hmg_twin_api | bunker_hmg_twin | bunker_hmg_twin_api | roundOf | api | any | Kinetic | 2 | 9.5 | 0 |
| casemate_155/casemate_155_guided | casemate_155 | casemate_155_guided | roundOf | guided | armour | HighExplosive | 3 | 320 | 7 |
| ciws_aa/ciws_aa_flak | ciws_aa | ciws_aa_flak | roundOf | flak | air | Fragmentation | 2 | 12 | 2.5 |

*15 / 70 dòng đầu: xem sheet 01_vu_khi_dan/Dan_thay_the; in 10 / 15 cột; 3 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 01_vu_khi_dan/Phao_sang — Pháo sáng (18 dòng, 19 cột)

| id | loai_don_vi | mo_hinh | so_mount_flare | so_qua_moi_lan | do_nang_cap | so_voi_ban_goc | flare_charges | flare_recharge_s | flares_every_s |
|---|---|---|---|---|---|---|---|---|---|
| aerial_tanker | xe | aerial_tanker | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 3 | 20 |  |
| attack_helicopter | xe | attack_helicopter | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 2 |  |  |
| attack_jet | xe | attack_jet | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 2 |  |  |
| fighter_jet | xe | fighter_jet | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 2 |  |  |
| flare_searchlight_tower | thap | flare_searchlight_tower | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | giong |  |  | 15 |
| flare_tower | thap | flare_tower | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | giong |  |  | 15 |
| glide_bomber | xe | glide_bomber | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 2 |  |  |
| gunship_heli | xe | gunship_heli | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 2 |  |  |
| heavy_bomber | xe | heavy_bomber | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 3 |  |  |
| heavy_lift_helicopter | xe | heavy_lift_helicopter | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 3 | 20 |  |
| interceptor_jet | xe | interceptor_jet | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 2 |  |  |
| light_attack_heli | xe | light_attack_heli | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 2 | 20 |  |
| prop_attack_plane | xe | prop_attack_plane | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 2 | 20 |  |
| scout_heli | xe | scout_heli | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 2 | 20 |  |
| sky_gunship | xe | sky_gunship | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 3 |  |  |
| stealth_fighter | xe | stealth_fighter | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 2 |  |  |
| swarm_carrier | xe | swarm_carrier | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 3 |  |  |
| twin_rotor_gunship | xe | twin_rotor_gunship | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 3 | 20 |  |

*in 10 / 19 cột; 3 cột khác (và raw_json, nguon): xem sheet.*

### 10i. Sổ tay đạn

Trạng thái: Đã áp

Nguồn dữ liệu: 11_meta_giao_dien/So_tay_dan; 01_vu_khi_dan/Dong_vu_khi. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §Sổ tay đạn / Ammunition, §Sổ tay đạn: bậc.

#### Sổ tay đạn / Ammunition handbook

Sinh từ dữ liệu (balance.json) như mục Sổ tay đạn trong Hồ sơ của game; chạm vào chip ĐÁNH NÓC, ĐẠN THAY THẾ, NỔ TRÊN KHÔNG, DẪN ĐƯỜNG, PHÁ CÔNG TRÌNH, PHÁ TƯỜNG trên trang chi tiết mở đúng mục. / Generated from the data, as the game's Dossier tab.

#### Sổ tay đạn (tiếng Việt)

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

#### Ammunition handbook (English)

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

#### Sổ tay đạn: bậc T0–T5 / Calibre tiers

Như mục "Bậc cỡ nòng T0–T5" của Sổ tay đạn trong game. Bậc lấy theo họ: càng to thì mỗi phát càng mạnh, nổ, hình và tiếng càng lớn, bù bằng thời gian nạp dài hơn. Đạn T4 và T5 của boss báo chỗ rơi ít nhất 0,5 s + lõi / 4,5 m/s (T4 ít nhất 2,5 s). / A round's tier comes from its family; a boss's T4-T5 rounds warn at least 0.5 s + core / 4.5 m/s.

| Bậc | Họ | Hình và tiếng | Look and sound |
|---|---|---|---|
| T0 | 12.7 mm heavy machine gun, 14.5 mm heavy machine gun, 7.62 mm machine gun, melee_bucket_wheel, melee_dozer_blade, melee_drill_head (+3) | Súng nhỏ: chớp mảnh, tiếng nổ giòn ngắn. | Small arms: a thin flash and a short crack. |
| T1 | 20 mm, 23 mm, 25 mm, 30 mm, 35 mm Oerlikon, 40 mm Bofors (+8) | Pháo tự động: chớp nhỏ, khói mỏng; nhiều súng cùng bắn nghe thành một trận đấu súng. | Autocannon: a small flash and thin smoke; many guns at once are heard as one firefight. |
| T2 | atgm_9k121_vikhr, atgm_9m113_konkurs, atgm_9m120_ataka, atgm_9m123_khrizantema, atgm_agm_114_hellfire, atgm_agm_114l_hellfire_longbow (+36) | Pháo vừa và rocket nhẹ: chớp vừa, quả cầu lửa nhỏ, bụi và đất tung lên. | Medium guns and light rockets: a medium flash, a small hot fireball, dust and earth thrown up. |
| T3 | atgm_agm_65_maverick, bomb_fab_250, 120 mm AP, 120 mm HE, 125 mm AP, 125 mm HE (+9) | Pháo nặng: chớp lớn, cầu lửa đầu nòng, khói dài và chậm, cột bụi; thân xe giật lùi. | Heavy guns: a big flash and muzzle fireball, long slow smoke, a dust column; the hull rocks back. |
| T4 | atgm_kh_29l, bal_9m723_iskander, 400 kg bomb, bomb_car_bomb, bomb_cbu_97_sensor_fuzed_weapon, bomb_fab_500 (+15) | Pháo rất nặng, Smerch, bom 400 kg: chớp rất lớn, cầu lửa cuộn, sóng xung kích trên mép vụ nổ, máy quay rung ngắn. | Very heavy guns, Smerch, 400 kg bombs: a very big flash, a rolling fireball, a shockwave on the blast's edge, a short camera shake. |
| T5 | 406 mm, 800 mm super-gun, EMRG electromagnetic railgun (Gungnir) | Siêu vũ khí: chớp sáng cả cảnh, đám mây hình nấm nhỏ, vòng trên lõi rồi trên mép, rung mạnh nhất. | Super weapons: a flash that lights the scene, a small mushroom cloud, rings on the core then the edge, the strongest shake. |

Sheet: 11_meta_giao_dien/So_tay_dan — Sổ tay đạn (2 dòng, 8 cột)

| id | nhom | khoa | gia_tri_chu |
|---|---|---|---|
| exampleShooter | handbook | exampleShooter | ifv |
| exampleTarget | handbook | exampleTarget | main_battle_tank |

Sheet: 01_vu_khi_dan/Dong_vu_khi — Dòng vũ khí thật (55 dòng, 12 cột)

| id | ten_that | khoi_nguon | so_vu_khi | projectile_model | projectile_scale | projectile_speed_m_s | round_length | round_weight | splash_m |
|---|---|---|---|---|---|---|---|---|---|
| 2a38_30_mm | 2A38 30 mm | weaponFamilies | 3 |  |  | 280 |  | 7.5 | 2.5 |
| 2a38_30_mm_ap | 2A38 30 mm AP | secondRounds.families | 3 |  |  | 280 |  | 7.5 | 0 |
| 2a42_30_mm | 2A42 30 mm | weaponFamilies | 3 |  |  | 200 |  | 32 | 0 |
| 2a42_30_mm_air_burst | 2A42 30 mm air-burst | secondRounds.families | 3 |  |  | 200 |  | 32 | 2.5 |
| 2a75_125_mm_he | 2A75 125 mm HE | secondRounds.families | 2 |  |  | 260 |  | 345 | 3 |
| 2a83_152_mm | 2A83 152 mm | weaponFamilies | 2 |  |  | 160 |  | 343 | 2.5 |
| 2a83_152_mm_he_frag | 2A83 152 mm HE-FRAG | secondRounds.families | 3 |  |  | 150 |  | 343 | 6.5 |
| 2b8_240_mm | 2B8 240 mm | weaponFamilies | 4 | mortar_bomb | 1.3333 | 38 | 1.2 | 543 | 9 |
| 2b11_120_mm | 2B11 120 mm | weaponFamilies | 2 | mortar_bomb |  | 32 |  |  | 5 |
| 9m120_ataka | 9M120 Ataka | weaponFamilies | 2 | atgm_ataka |  | 26 |  |  | 0 |
| 9m133_kornet | 9M133 Kornet | weaponFamilies | 7 | atgm_kornet | 0.7385 | 22 | 0.96 |  | 0 |
| 9m317_buk | 9M317 Buk | weaponFamilies | 3 | buk | 1.2333 | 50 | 4.44 |  | 2 |
| agm_88_harm | AGM-88 HARM | weaponFamilies | 1 |  |  | 45 | 2.09 | 360 | 4 |
| agm_114_hellfire | AGM-114 Hellfire | weaponFamilies | 4 | hellfire_longbow |  | 26 |  | 270 | 0 |
| aim_9_sidewinder | AIM-9 Sidewinder | weaponFamilies | 2 | aim9 |  | 55 |  | 260 | 1.5 |

*15 / 55 dòng đầu: xem sheet 01_vu_khi_dan/Dong_vu_khi.*

### 10j. Họ vũ khí, hành vi đạn và vòng cảnh báo

Trạng thái: Đã áp

Nguồn dữ liệu: 01_vu_khi_dan/Ho_vu_khi; 01_vu_khi_dan/Ho_vu_khi_bien_the; 01_vu_khi_dan/Hanh_vi_dan; 01_vu_khi_dan/Hanh_vi_dan_nhom; 01_vu_khi_dan/Canh_bao_vong. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §10i. Họ vũ khí.

Mỗi vũ khí có `weaponFamilyId` (súng: lớp cỡ nòng; còn lại: vũ khí thật) và `weaponVariantId` khi đạn hay cách bắn khác (có lý do trong bảng). Bậc T0–T5 theo họ. Ở boss, cùng họ là cùng viên đạn (sát thương, lõi, rìa, tốc độ, loại); DPS của từng vũ khí giữ nguyên bằng chu kỳ dài hơn, và lõi rộng hơn 1,25 lần thì chu kỳ dài thêm đúng tỉ lệ đó. Vũ khí người chơi chỉ gắn nhãn (danh sách lệch: Docs/checks/player_weapon_family.md). Kiểm: `Tools/balance/p34_validate.py`.

#### Vũ khí boss theo họ (136)

Sát thương một viên; lõi nhận đủ sát thương, rìa 40%. Hồi: thời gian hồi của vũ khí (loạt và băng giữ nhịp riêng). Cảnh báo: thời gian đạn T4+ không dẫn đường báo chỗ rơi (đạn ở trên không ít nhất bấy lâu).

#### Cảnh báo theo khả năng thoát

Đạn T4+ của boss báo max(sàn, 0,5 s + lõi / 4,5 m/s), tối đa 6 s; sàn T4 2,5 s, 406 mm 3,5 s, siêu vũ khí T5 4 s. Vòng hiển thị là đúng vùng sát thương: vòng ngoài là rìa, vòng trong là lõi (tên lửa hành trình: lõi và rìa của vụ nổ hai lớp). Gungnir giữ 3 s (ngoại lệ có tên: prompt 29 G1).

| Họ | Tên | Bậc | Lõi (boss) | Cảnh báo |
|---|---|---|---|---|
| `atgm_kh_29l` | atgm_kh_29l | T4 | — | 2,5 s |
| `bal_9m723_iskander` | bal_9m723_iskander | T4 | — | 2,5 s |
| `bomb_400` | 400 kg bomb | T4 | 10 m | 2,72 s |
| `bomb_car_bomb` | bomb_car_bomb | T4 | — | 2,5 s |
| `bomb_cbu_97_sensor_fuzed_weapon` | bomb_cbu_97_sensor_fuzed_weapon | T4 | — | 2,5 s |
| `bomb_fab_500` | bomb_fab_500 | T4 | — | 2,5 s |
| `bomb_fab_500_m_62_with_umpk_glide_kit` | bomb_fab_500_m_62_with_umpk_glide_kit | T4 | — | 2,5 s |
| `bomb_gbu_28` | bomb_gbu_28 | T4 | — | 2,5 s |
| `bomb_gbu_31_jdam` | bomb_gbu_31_jdam | T4 | — | 2,5 s |
| `bomb_odab_500` | bomb_odab_500 | T4 | — | 2,5 s |
| `cal_203` | 203 mm | T4 | 8,5 m | 2,5 s |
| `cal_240` | 240 mm | T4 | 10 m | 2,72 s |
| `cruise_3m_54_kalibr` | cruise_3m_54_kalibr | T4 | — | 2,5 s |
| `cruise_agm_158_jassm` | cruise_agm_158_jassm | T4 | — | 2,5 s |
| `cruise_kh_101` | cruise_kh_101 | T4 | — | 2,5 s |
| `cruise_nsm_coastal_defence` | cruise_nsm_coastal_defence | T4 | — | 2,5 s |
| `cruise_typhon_mrc` | cruise_typhon_mrc | T4 | — | 2,5 s |
| `msl_nsm_p_800_oniks` | msl_nsm_p_800_oniks | T4 | — | 2,5 s |
| `rkt_gmlrs_227` | GMLRS 227 mm | T4 | — | 2,5 s |
| `rkt_smerch_300` | Smerch 300 mm rockets | T4 | 8 m | 2,5 s |
| `rkt_tos_220` | TOS-1A 220 mm thermobaric | T4 | — | 2,5 s |
| `cal_406` | 406 mm | T5 | 14 m | 3,61 s |
| `cal_800` | 800 mm super-gun | T5 | — | 4 s |
| `gungnir_emrg` | EMRG electromagnetic railgun (Gungnir) | T5 | — | 4 s |

Sheet: 01_vu_khi_dan/Ho_vu_khi — Họ vũ khí (105 dòng, 11 cột)

| id | ten | bac | boss_sat_thuong | boss_loi_m | boss_ria_m | so_vu_khi | vu_khi |
|---|---|---|---|---|---|---|---|
| atgm_9k121_vikhr | atgm_9k121_vikhr | 2 |  |  |  | 1 | vikhr |
| atgm_9m113_konkurs | atgm_9m113_konkurs | 2 |  |  |  | 1 | atgm_post |
| atgm_9m120_ataka | atgm_9m120_ataka | 2 |  |  |  | 2 | ataka;heli_ataka |
| atgm_9m123_khrizantema | atgm_9m123_khrizantema | 2 |  |  |  | 1 | khrizantema |
| atgm_agm_65_maverick | atgm_agm_65_maverick | 3 |  |  |  | 1 | maverick |
| atgm_agm_114_hellfire | atgm_agm_114_hellfire | 2 |  |  |  | 3 | drone_missile;heli_atgm;uav_loiter_missile |
| atgm_agm_114l_hellfire_longbow | atgm_agm_114l_hellfire_longbow | 2 |  |  |  | 2 | hellfire_standoff;hellfire_volley |
| atgm_agm_176_griffin | atgm_agm_176_griffin | 2 |  |  |  | 1 | griffin |
| atgm_bgm_71_tow_2 | atgm_bgm_71_tow_2 | 2 |  |  |  | 1 | atgm |
| atgm_gun_launched_atgm | atgm_gun_launched_atgm | 2 |  |  |  | 1 | gun_launched_atgm |
| atgm_kh_29l | atgm_kh_29l | 4 |  |  |  | 1 | kh29 |
| atgm_kornet | 9M133 Kornet | 2 | 230 | 0 | 0 | 14 | atgm_heavy;boss_missiles;kornet_multi;kornet_top;kornet_twi… |
| atgm_mam_l | atgm_mam_l | 2 |  |  |  | 1 | recon_missile |
| atgm_spike_nlos | atgm_spike_nlos | 2 |  |  |  | 1 | spike_nlos |
| bal_9m723_iskander | bal_9m723_iskander | 4 |  |  |  | 1 | ballistic_missile |

*15 / 105 dòng đầu: xem sheet 01_vu_khi_dan/Ho_vu_khi.*

Sheet: 01_vu_khi_dan/Ho_vu_khi_bien_the — Họ vũ khí: biến thể (20 dòng, 7 cột)

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

Sheet: 01_vu_khi_dan/Hanh_vi_dan — Hành vi đạn: luật chung (11 dòng, 8 cột)

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

Sheet: 01_vu_khi_dan/Hanh_vi_dan_nhom — Hành vi đạn theo nhóm (7 dòng, 12 cột)

| id | so_vu_khi | cach_nham | khi_no | khi_truot | co_canh_bao | thoi_gian_bay_toi_da_s | tuong_tac_phao_sang | tuong_tac_aps | tuong_tac_gay_nhieu |
|---|---|---|---|---|---|---|---|---|---|
| Bomb | 8 | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| Bullet | 116 | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| Drone | 14 | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| Flame | 3 | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| Missile | 58 | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| Rocket | 29 | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| Shell | 144 | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |

Sheet: 01_vu_khi_dan/Canh_bao_vong — Vòng cảnh báo (12 dòng, 8 cột)

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
| rocketMinMm | warningRules | rocketMinMm | 300 | mm |
| salvoMergeSeconds | warningRules | salvoMergeSeconds | 0.6 | s |
