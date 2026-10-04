# 02_boss — Boss

Boss, bộ phận, siêu vũ khí, hộ tống, pha, Săn trùm.

Gói cân bằng Machine Brigade, commit 13215908, ngày 2026-10-04. Số liệu đầy đủ ở 02_boss.xlsx; file này chỉ nêu luật, giải thích, lý do thiết kế, tham khảo và bảng nhỏ (tối đa 20 dòng, bảng lớn: xem sheet).

## Tổng hợp boss

Mọi boss và mini boss cạnh nhau, đọc từ dữ liệu hiện tại: máu thân (trước hệ số độ khó), giáp trước/hông/sau/nóc, số bộ phận và phần máu của chúng, DPS duy trì lên xe nhẹ, xe nặng, máy bay và công trình (trước giáp), đòn lớn đầu tiên và số hộ tống trong mọi đợt.

Bảng đầy đủ: xem sheet `Boss_dps` (33 dòng), `Boss_hieu_qua` (165 dòng).

## Boss: vụ nổ hai lớp, pha, giáp và cỡ

Từ 04/10 sát thương nổ giảm theo bảng giảm nổ lan (01/Bang_no_lan): trong lõi 110% ở tâm, 108 / 105 / 100% theo quãng lõi; từ lõi ra rìa 85 / 65 / 45 / 25% theo từng phần tư; ngoài rìa 0. Vũ khí không có rìa nổ một bán kính: không lõi, bán kính đó là rìa. Máu, vũ khí và cỡ của boss được làm lại theo chương (mục tiêu hạ boss chủ lực từ 2,5 phút ở chương 1 tới 4 phút ở chương 12, mini boss 60 đến 90 giây); Ixion và Gungnir được làm lại; mỗi boss có mốc thời đại ở dòng Tham khảo của thẻ. Pha: hệ số nhân vào từ mốc máu đó trở đi.

### Pha, giáp và cỡ model (31 boss)

Bảng 31 dòng: số liệu đầy đủ ở các sheet của mục này trong file xlsx cùng tên.

Sheet 02_boss/Boss_phase — Boss: pha (6 dòng, 11 cột)

| id | boss_id | thu_tu | at | damage | fire_rate | radio | speed_m_s | transform |
|---|---|---|---|---|---|---|---|---|
| command_airship/0 | command_airship | 0 | 0.6 | 1.1 |  | radio.quaden.airship.phase2 |  | 2.5 |
| command_airship/1 | command_airship | 1 | 0.25 | 1.25 | 1.25 | radio.quaden.airship.half |  | 3 |
| earth_borer/0 | earth_borer | 0 | 0.45 |  |  | radio.hung.borer.half | 1.15 | 2.5 |
| landing_hovercraft/0 | landing_hovercraft | 0 | 0.45 |  |  | radio.kessler.hovercraft.half | 1.2 | 2.5 |
| leviathan/0 | leviathan | 0 | 0.6 |  |  | radio.kessler.leviathan.phase2 |  | 2.5 |
| leviathan/1 | leviathan | 1 | 0.25 |  | 1.25 | radio.kessler.leviathan.phase3 |  | 3 |

Bảng đầy đủ: xem sheet `Boss_be_goc` (133 dòng).

## Săn trùm (Boss Hunt)

- **Sức mạnh P:** đo một lần lúc bắt đầu từ bộ bài mang theo (sát thương giấy mỗi giây của các thẻ chiến đấu, tính cả hạng thẻ, trang bị và chỉ huy) × 10 xe ra trận × 0,3 trúng boss, tối thiểu 60. Máu boss = P × thời gian mục tiêu × 0,6 × hệ số m × hệ số bậc; sát thương boss là của dữ liệu × m × hệ số bậc.
- **Tuần:** 10 boss (3 chủ lực, 7 mini; nhóm 3, 2, 2 mini dẫn tới mỗi boss chủ lực), mục tiêu mini 66 s, chủ lực 2.8 phút; m = 1 + 0.06 × số thứ tự (×1 tới ×1,54); nghỉ 15 s giữa các boss, quân sống sót được sửa 30% và chỉ giữ 50% CP; điểm hồi sinh sau mỗi boss chủ lực; đồng hồ 30 phút.
- **Toàn bộ:** 31 boss (14 chủ lực) theo thứ tự cốt truyện, chủ lực 2,5 phút, mini 1 phút; m từ ×0.8 tới ×1.3; điểm hồi sinh và lưu sau mỗi boss; mỗi boss là một trận mới (không giữ quân, CP khởi đầu như nhau), chỉ hỗ trợ tác chiến được giữ.
- **Hỗ trợ tác chiến:** sau mỗi boss chủ lực chọn 1 trong 3; tổng sức mạnh quân từ hỗ trợ tối đa +40%; khi đã chạm trần chỉ còn các hỗ trợ đổi cách chơi (thẻ bắn nhanh hơn, thả xe).
- **Bậc:** bốn độ khó của bảng chọn là bốn bậc (bảng dưới). Chưa làm: bậc Huyền thoại và các biến thể (mutator) cho Săn trùm.

### Lời trong game

Tuần: 10 boss tuần này: 7 mini boss dẫn tới 3 boss chủ lực, boss sau mạnh hơn boss trước. Máu boss theo sức mạnh bộ bài bạn mang. Nghỉ 15 giây giữa các boss, xe còn sống được sửa 30% và giữ 50% CP; sau mỗi boss chủ lực (tối đa +40% sức mạnh đội quân từ hỗ trợ), chọn một trong ba hỗ trợ tác chiến và lưu điểm hồi sinh. Đồng hồ 30 phút.

Toàn bộ: Toàn bộ 31 boss chủ lực và mini boss của các chương đang mở, theo đúng thứ tự cốt truyện. Có điểm hồi sinh sau mỗi boss: chơi dần qua bao nhiêu lần cũng được. Mỗi boss là một trận mới: quân không được giữ và bạn bắt đầu với cùng lượng CP; chỉ hỗ trợ tác chiến được giữ (chọn sau mỗi boss chủ lực, tối đa +40% sức mạnh đội quân, sau đó chỉ còn các hỗ trợ đổi cách chơi). Xếp hạng theo tổng thời gian.

### Hỗ trợ tác chiến (12)

| Hỗ trợ | Id | Tác dụng | Sức mạnh quân |
|---|---|---|---|
| Gia cố thân xe | `hull` | Máu toàn quân +15%, cả xe tới sau. | +15% |
| Huấn luyện pháo thủ | `gunnery` | Sát thương toàn quân +10%. | +10% |
| Nạp đạn nhanh | `loaders` | Toàn quân bắn nhanh hơn 12%. | +12% |
| Tinh chỉnh động cơ | `engines` | Toàn quân chạy nhanh hơn 12%. | +6% |
| Sửa chữa dã chiến | `regen` | Khi không trúng đạn, mỗi xe tự hồi 1% máu mỗi giây. | +8% |
| Điều phối nhanh | `rapid` | Hồi chiêu thẻ hỗ trợ ngắn hơn 25%. | đổi cách chơi, không tính vào trần |
| Đoàn tiếp tế | `logistics` | Thu nhập CP +20%. | +10% |
| Quỹ chiến tranh | `warchest` | Nhận ngay 35 CP. | +5% |
| Thêm kíp lái | `supply` | Giới hạn quân +6. | +8% |
| Xưởng lưu động | `workshop` | Giờ nghỉ sửa quân gấp đôi. | +5% |
| Hợp đồng săn thưởng | `bounty` | Tiền thưởng CP khi hạ boss +50%. | +5% |
| Tiếp viện miễn phí | `airdrop` | Ba xe đắt nhất trong bộ bài được thả xuống ngay, miễn phí. | đổi cách chơi, không tính vào trần |

Sheet 02_boss/Sanhunt_ho_tro — Săn trùm: hỗ trợ tác chiến (12 dòng, 8 cột)

| id | ten_vi | icon | kind | strength | value |
|---|---|---|---|---|---|
| airdrop | Tiếp viện miễn phí | reinforce | Airdrop |  | 3 |
| bounty | Hợp đồng săn thưởng | trophy | Bounty | 0.05 | 0.5 |
| engines | Tinh chỉnh động cơ | move | Engines | 0.06 | 0.12 |
| gunnery | Huấn luyện pháo thủ | crosshair | Gunnery | 0.1 | 0.1 |
| hull | Gia cố thân xe | shield | Hull | 0.15 | 0.15 |
| loaders | Nạp đạn nhanh | ammo | Loaders | 0.12 | 0.12 |
| logistics | Đoàn tiếp tế | cp | Logistics | 0.1 | 0.2 |
| rapid | Điều phối nhanh | airstrike | Rapid |  | 0.25 |
| regen | Sửa chữa dã chiến | repair | Regen | 0.08 | 0.01 |
| supply | Thêm kíp lái | people | Supply | 0.08 | 6 |
| warchest | Quỹ chiến tranh | coin | WarChest | 0.05 | 35 |
| workshop | Xưởng lưu động | gear | Workshop | 0.05 | 1 |

Sheet 02_boss/Sanhunt_chua_xep — Săn trùm: boss chưa có ô chương (8 dòng, 4 cột)

| id | sau_chuong |
|---|---|
| behemoth_mk0 | 3 |
| coeus | 12 |
| hydra | 9 |
| hyperion | 12 |
| kraken | 9 |
| monster | 8 |
| nyx | 4 |
| theia | 12 |

Bảng đầy đủ: xem sheet `Sanhunt` (33 dòng).

## Tháp canh, xe tinh nhuệ và boss

### Tháp và công sự

Tháp cố định chặn lưới đường đi khi xuất hiện; trong Chiếm cứ điểm mỗi cứ điểm có tháp trung lập bắn mọi phe và dựng lại sau một thời gian; mỗi phe có sở chỉ huy (HQ) có máu (phá được hay không tùy chế độ, phần 6). Tháp của căn cứ người chơi xếp theo cỡ ô (phần 6), có hạng, nhánh ở hạng 7 và 3 ô đồ.

### Xe tinh nhuệ

Phiên bản tân trang: +60% máu, +25% sát thương, 1–2 kỹ năng tinh nhuệ, thanh máu vàng và vòng vàng trên bản đồ nhỏ; sức mạnh thực đo được 1,8–2,2 lần bản thường. Địch không còn nhận tinh nhuệ theo xác suất mà theo **ngân sách**: tinh nhuệ giá 1,6 lần, phần chi tiêu theo độ khó (Dễ 5%, Thường 10%, Khó 15%, Anh hùng 20%, Thép 25%), trần 1–5 xe cùng lúc; tướng ưu tiên loại xe của mình. Hạ tinh nhuệ hoàn CP theo giá thật và thưởng một ít xu, có tỷ lệ nhỏ rơi bản thiết kế.

| Tên | Giá | Giáp | Máu | Tốc độ | Vũ khí | DPS nhẹ/nặng/bay | Kỹ năng | Tham khảo |
|---|---|---|---|---|---|---|---|---|
| **Phòng không tinh nhuệ** | 6 CP (địch) | Trước 2 (Vừa) · Hông 0 (Không giáp) · Sau 0 (Không giáp) · Nóc 0 (Không giáp) | 1.041 | 8.5 | twin_35_ahead, sam | 102 / 51 / 182 | elite_overdrive | Rheinmetall Skyranger 35 (đạn AHEAD), Gepard (khung gốc) — Phòng không tinh nhuệ, đạn nổ trên không AHEAD |
| **Xe bọc thép tinh nhuệ** | 11 CP (địch) | Trước 3 (Dày) · Hông 1 (Mỏng) · Sau 0 (Không giáp) · Nóc 0 (Không giáp) | 1.544 | 9 | autocannon_30, mg_coax, atgm | 125 / 62 / 11 | elite_emp | M2 Bradley / BMP-3 (khung gốc), 2A42 30 mm — Xe chiến đấu bộ binh tinh nhuệ |
| **Pháo tự hành tinh nhuệ** | 11 CP (địch) | Trước 2 (Vừa) · Hông 0 (Không giáp) · Sau 0 (Không giáp) · Nóc 0 (Không giáp) | 891 | 6 | howitzer, hmg_selfdef_15 | 101 / 60 / 21 | elite_barrage | CAESAR 155 mm — Lựu pháo tự hành tinh nhuệ |
| **Trực thăng tinh nhuệ** | 18 CP (địch) | cấp 2 (Vừa) | 1.485 | 15 | hellfire_volley, heli_gun, heli_rockets, stinger_atas | 164 / 98 / 136 | elite_flares, elite_barrage | AH-64 Apache, AGM-114L Hellfire Longbow — Apache tinh nhuệ, bắn loạt Hellfire |
| **Cường kích tinh nhuệ** | 37 CP (địch) | cấp 2 (Vừa) | 1.366 | 32 | jet_cannon, s8_pods, jet_bombs, kh29, r60 | 553 / 301 / 25 | elite_flares | Su-25 Frogfoot, A-10 Thunderbolt II — Cường kích tinh nhuệ |
| **Xe phóng drone FPV tinh nhuệ** | 11 CP (địch) | Trước 2 (Vừa) · Hông 0 (Không giáp) · Sau 0 (Không giáp) · Nóc 0 (Không giáp) | 1.247 | 9 | fpv_swarm, hmg_selfdef_18 | 107 / 66 / 21 | elite_barrage | KamAZ Typhoon-K, RG-33 MRAP, drone FPV — Xe phóng drone FPV tinh nhuệ |
| **Grad tinh nhuệ** | 13 CP (địch) | Trước 2 (Vừa) · Hông 0 (Không giáp) · Sau 0 (Không giáp) · Nóc 0 (Không giáp) | 950 | 8.5 | grad_cluster, hmg_selfdef_15 | 86 / 50 / 18 | elite_barrage | BM-21 Grad (khung Ural-375D) — Xe tải Grad 122 mm tinh nhuệ, đầu đạn chùm |
| **Tăng hạng nặng tinh nhuệ** | 26 CP (địch) | Trước 4 (Rất dày) · Hông 3 (Dày) · Sau 2 (Vừa) · Nóc 2 (Vừa) | 5.632 | 4.6 | gun_152_heat, autocannon_30, hmg_roof | 198 / 110 / 18 | elite_overdrive | Object 195 / T-95 (2A83 152 mm, đạn HEAT) — Siêu tăng tinh nhuệ, đạn nổ lõm 152 mm |
| **Tên lửa phòng không tầm xa tinh nhuệ** | 29 CP (địch) | Trước 2 (Vừa) · Hông 0 (Không giáp) · Sau 0 (Không giáp) · Nóc 0 (Không giáp) | 1.307 | 6 | sam_48n6 | 0 / 0 / 165 | elite_overdrive | S-400 (48N6), S-300PMU (5P85) — Tên lửa phòng không tầm xa tinh nhuệ |
| **Tăng chủ lực tinh nhuệ** | 13 CP (địch) | Trước 4 (Rất dày) · Hông 2 (Vừa) · Sau 1 (Mỏng) · Nóc 1 (Mỏng) | 2.673 | 6.2 | gun_125_elite, mg_coax, hmg_roof | 118 / 65 / 29 | elite_shield | T-90M (2A46M-5 125 mm), Leopard 2A4 / M1 Abrams (khung gốc) — Xe tăng chủ lực tinh nhuệ, giáp tăng cường sơn đen |
| **Pháo phản lực tinh nhuệ** | 13 CP (địch) | Trước 2 (Vừa) · Hông 0 (Không giáp) · Sau 0 (Không giáp) · Nóc 0 (Không giáp) | 950 | 6.5 | mlrs_elite, hmg_selfdef_15 | 89 / 53 / 18 | elite_barrage | M142 HIMARS / M270, M30 GMLRS 227 mm (đầu đạn chùm) — Xe phóng rốc-két tinh nhuệ, đầu đạn chùm |
| **Pháo chống tăng tinh nhuệ** | 11 CP (địch) | Trước 4 (Rất dày) · Hông 2 (Vừa) · Sau 1 (Mỏng) · Nóc 1 (Mỏng) | 1.841 | 7.5 | gun_105_apfsds, hmg_roof | 117 / 81 / 18 | elite_barrage, elite_smoke | 2S25 Sprut-SD (2A75 125 mm APFSDS) — Pháo chống tăng tinh nhuệ, đạn xuyên dưới cỡ |

### Boss

Mọi boss có bộ phận theo cùng một bộ luật (phase 9); boss cuối chương còn có thanh máu nhiều pha.

- **Máu bộ phận** là một phần máu thân (đọc trực tiếp, nên tăng theo cấp chiến dịch, độ khó và bản mạnh của nhiệm vụ): mỗi bộ phận 8–15%; boss từ 5 súng trở lên có tổng 50–70%, boss chỉ có 3–4 thứ phá được có tổng 35–47%.
- **Máu thân** giảm còn ×0,76 đến ×0,90 (1,125 / (1 + 0,7 × tổng phần bộ phận)) để trận dài hơn khoảng 12% (ước tính theo mô hình, đo ở phase kiểm tra).
- **Vỡ một bộ phận:** súng trên đó im cả trận; kỹ năng dừng khi mọi bộ phận mang nó đều vỡ; cơ chế dừng (phát bắn của siêu pháo, đào hầm của Giun Đất, đổ quân của tàu đệm khí, hào quang của Tổng Tư Lệnh); áp dụng phạt tốc độ, quay, nhịp bắn, độ tản; thân mất thêm 30% máu của bộ phận đó.
- **Chỉ phát trúng trực tiếp** làm hại bộ phận; nổ lan, lửa và hỏa lực hỗ trợ rơi vào thân. Đạn trúng bộ phận nhô ra ngoài thân (quạt, đầu máy, đầu kéo) nay tính là trúng.
- **Tự sửa:** Tàu Thép và Bastion một lần mỗi trận hồi bộ phận đã vỡ có phát bắn mặt đất nặng nhất lên 50%.
- **Nhắm bắn:** mỗi xe nhắm bộ phận nguy hiểm nhất với nó trong tầm (phòng không nhắm bộ phận bắn máy bay, diệt tăng nhắm bộ phận dày nhất); 2 trên 5 phát vẫn vào thân.
- **Lệnh bắn bộ phận:** chạm vào biểu tượng bộ phận dưới thanh máu boss hoặc chạm thẳng vào bộ phận trên mô hình: mọi xe trong tầm dồn hỏa lực vào đó tới khi vỡ; chạm lại để hủy.
- **Săn trùm** thưởng 2 CP cho mỗi bộ phận vỡ.

#### Lửa và khói ở chỗ vỡ

- Dưới 50% máu bộ phận bốc khói và tóe lửa điện, dưới 25% bắt cháy.
- Lúc vỡ: súng và kho đạn nổ lớn (có mảnh văng ở đồ họa Cao), bộ phận năng lượng lóe sáng với vòng xanh và tia điện, động cơ bùng cầu lửa; bộ phận biến mất, thay bằng mảnh xác.
- Sau khi vỡ, lửa và cột khói đen ở lại tới hết trận; thân boss cháy thêm ở 66% và 33% máu; boss bay hoặc chạy nhanh kéo vệt khói từ động cơ vỡ.
- Tối đa 8 điểm lửa mỗi boss (5 ở đồ họa Thấp, khói và tia lửa giảm một nửa). Khi boss chết mọi đám cháy bùng lên, xác cháy 25–35 giây.
- Chỉ là hình ảnh: mô phỏng không thấy khói, tầm nhìn qua boss đang cháy không đổi.

giáp thân trước 4 / hông 4 / sau 4 / nóc 3; Tổng 35% máu thân trong 3 bộ phận; tự sửa một bộ phận một lần mỗi trận; pha ở 45%.

**Mẹo:** phá **khẩu cối** trước; hai tháp pháo chỉ bắn gần.

Pháo đài biết đi đầu tiên của Brandt, bản nguyên mẫu của Bastion: ít pháo hơn, giáp mỏng hơn, vẫn kíp lái lì lợm ấy.

giáp thân trước 4 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 4 bộ phận; pha ở 45%.

**Mẹo:** mỗi **súng phun lửa** bị phá là lửa giảm một nửa; phá cả hai thì nó chỉ còn bắn rốc-két nhiệt áp. Trong lúc đó hãy giữ ngoài 20 m và tránh vệt lửa phía sau nó: **thùng nhiên liệu** nuôi vệt lửa đó.

Một chiếc Behemoth dựng lại quanh hai súng phun lửa lớn và một hộp rốc-két nhiệt áp. Nó đốt cháy cả mặt đất. Tránh xa tầm với của nó và cứ thế mà nện.

giáp thân trước 2 / hông 2 / sau 2 / nóc 2; Tổng 35% máu thân trong 6 bộ phận; pha ở 45%.

**Mẹo:** phá **cánh quạt sau** là nó xoay chậm một nửa và khó ngắm; hộp rốc-két và pháo dưới mũi là thứ làm hại quân mặt đất.

Pháo hạm bay của Orlov, to như con tàu và chậm như vậy: ổ rốc-két, pháo sáng mồi bẫy và một tốp trực thăng hộ tống. Chỉ phòng không và tiêm kích với tới nó. Mang theo mọi bệ phóng có được.

giáp thân trước 4 / hông 4 / sau 3 / nóc 2; Tổng 35% máu thân trong 3 bộ phận; pha ở 45%.

**Mẹo:** mỗi **hộp rốc-két** bị phá là rốc-két của nó giảm một nửa; cao xạ là thứ duy nhất chống máy bay.

Xe tiên phong mùa đông của Orlov: một thợ săn hạng nặng chạy trước các trận địa pháo qua tuyết và đánh dấu mục tiêu cho chúng.

giáp thân trước 3 / hông 3 / sau 2 / nóc 1; Tổng 35% máu thân trong 4 bộ phận; pha ở 45%.

**Mẹo: pháo chính** là khẩu mạnh nhất; phá cả hai **pháo sườn** thì nó chỉ còn bắn được phía trước.

Chiếc Behemoth đầu tiên từng được chế tạo, do một kỹ sư trẻ tên Mara Lind vẽ và Varga hoàn thiện. Chậm hơn, mỏng hơn và già hơn những đứa con của nó, và vẫn canh giữ Foundry nơi nó ra đời.

giáp thân trước 4 / hông 3 / sau 3 / nóc 2; Tổng 35% máu thân trong 5 bộ phận; tự sửa một bộ phận một lần mỗi trận; pha ở 45%.

**Mẹo:** phá **đầu máy** trước để nó chậm một nửa, rồi tới các toa pháo. Nó tự vá một bộ phận một lần, ưu tiên pháo nặng, nên hãy phá toa đó lần nữa.

Đoàn tàu bọc thép của Kessler: toa pháo và toa giáp chạy đúng giờ. Bị bắn là nó tự thả khói, vừa chạy vừa tự vá. Phải chặn nó trước khi tới bến cảng.

giáp thân trước 4 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 5 bộ phận; pha ở 45%.

**Mẹo:** phá **máy phát khiên** trước khi nó xuống máu, không thì khiên sẽ nuốt đợt dồn hỏa lực của bạn; **bộ phát la-de** bắn hạ tên lửa, drone và rốc-két, nên hãy dùng pháo, đạn hoặc khói cho tới khi phá được nó.

Một chiếc Behemoth dựng quanh khẩu súng điện từ: nạp điện, phát sáng rồi xuyên thủng mọi thứ trên một đường thẳng. Hai pháo điện từ và một tấm khiên. Dàn quân ra và áp sát.

giáp thân trước 4 / hông 4 / sau 3 / nóc 2; Tổng 35% máu thân trong 3 bộ phận; pha ở 45%.

**Mẹo:** phá **ống phóng tên lửa** để chặn tên lửa hành trình, phá **CIWS** trước khi dùng tên lửa.

Tàu khu trục chỉ huy của Kessler: nhanh, nhiều vũ khí, và luôn là chiếc đầu tiên vào cảng.

giáp thân trước 4 / hông 4 / sau 3 / nóc 2; Tổng 35% máu thân trong 4 bộ phận; pha ở 45%.

**Mẹo: CIWS** chặn tên lửa của bạn; ống phóng mang tên lửa chống hạm của nó.

Tàu khu trục kiểu Zumwalt mà hạm đội không bao giờ ghi tên: nó chỉ hiện trên radar khi nó muốn.

giáp thân trước 1 / hông 1 / sau 1 / nóc 1; Tổng 35% máu thân trong 2 bộ phận; pha ở 45%.

**Mẹo: khoang drone** là tất cả những gì nó có.

Một tàu mang drone cỡ nhỏ trong chương trình drone của Venn. Aurel vẫn cho đóng tiếp sau khi bà bỏ đi.

giáp thân trước 5 / hông 3 / sau 2 / nóc 3; Tổng 35% máu thân trong 9 bộ phận; tự sửa một bộ phận một lần mỗi trận; pha ở 60%, 25%.

**Mẹo:** mỗi **tháp pháo tự động** chỉ phủ một góc: phá các tháp ở một phía rồi đánh từ phía đó. Khi tự vá nó ưu tiên khẩu cối.

Pháo đài biết đi đầu tiên của Hegemon: bốn tháp pháo tự động, một khẩu cối hạng nặng và kíp lái biết tự vá giáp dưới làn đạn. Chiếc ở Ashfield là mẫu đời đầu, chậm hơn và mỏng hơn những chiếc về sau.

giáp thân trước 3 / hông 2 / sau 1 / nóc 1; Tổng 35% máu thân trong 8 bộ phận; pha ở 45%.

**Mẹo:** phá **cửa đổ bộ** là nó hết đổ quân; mỗi **quạt đẩy** bị phá làm nó chậm 30%. Hai **pháo phòng thủ tầm gần** bắn hạ tên lửa và rốc-két: phá chúng trước khi tấn công bằng tên lửa.

Tàu đệm khí đổ bộ của Hegemon, chở cả một đại đội thiết giáp lên bãi biển với tốc độ sáu mươi hải lý và tự yểm trợ cuộc đổ bộ bằng pháo của mình. Phải đánh nó trước khi nó kịp dỡ quân.

giáp thân trước 4 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 4 bộ phận; pha ở 45%.

**Mẹo: pháo chính** là đòn mạnh nhất; **hệ thống bảo vệ** bắn hạ hai tên lửa mỗi loạt.

Chiếc Behemoth của Varga dựng lại sau lần bại trận đầu tiên: nặng hơn, lắp hệ sưởi cho mùa đông, và hung hãn hơn.

giáp thân trước 5 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 10 bộ phận; pha ở 60%, 25%.

**Mẹo:** cho xe tăng dồn bắn **pháo chính**: mất cặp nòng đó nó chỉ còn là khối thép chậm chạp với cao xạ và tên lửa. **Hệ thống bảo vệ chủ động** bắn hạ hai tên lửa chống tăng mỗi lượt: phá nó, hoặc dùng pháo. Phòng không nên phá cao xạ trước nếu máy bay ta ở gần.

Chiến hạm mặt đất của Varga: pháo chính mỗi phát hạ một xe tăng, đội hộ tống bám theo vào trận và lớp vỏ chịu được gần hết hỏa lực của lữ đoàn. Mara nói các tấm giáp phía sau là điểm yếu của nó.

giáp thân trước 4 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 4 bộ phận; pha ở 45%.

**Mẹo:** đánh vào **mũi khoan** trong vài giây ngay sau khi nó trồi lên: vỡ rồi là nó không bao giờ chui xuống đất được nữa.

Cỗ máy khoan cũ của Varga, Tartarus: nó nghiến xuyên dưới tường thành và thân đập rồi trồi lên đúng chỗ không ai canh. Phải tiêu diệt nó trước khi nó tới trạm phát điện.

giáp thân trước 4 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 8 bộ phận; pha ở 45%.

**Mẹo:** phá **tháp pháo trên thùng** là mất pháo 125 mm; phá một **lốp trước** thì cú lao lệch và dừng; **lốp sau** giáp cấp 1; phá **ca-bin** là súng máy ngừng bắn.

Xe tải mỏ bọc thép của Thorne ở Deepcut Mine: một chiếc BelAZ-75710 hàn tháp pháo xe tăng lên thùng, lưỡi húc ở mũi và súng máy trên nóc ca-bin.

giáp thân trước 5 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 9 bộ phận; pha ở 60%, 25%.

**Mẹo:** phá **lựu pháo** để chấm dứt các loạt pháo dồn, và phá bộ phát EMP trước khi thiết giáp ta áp sát.

Mỏ neo của tuyến Frostpeak: một pháo đài di động với lựu pháo, đội hộ tống và xung EMP làm tê liệt mọi thứ xung quanh.

giáp thân trước 4 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 4 bộ phận; pha ở 45%.

**Mẹo: cửa ống phóng** mang tên lửa của nó; pháo boong chỉ bắn khi nổi.

Tàu ngầm mang drone theo khái niệm: nhỏ hơn Typhon, nhanh hơn, và im lặng cho tới khi nắp ống mở.

giáp thân trước 4 / hông 4 / sau 4 / nóc 4; Tổng 35% máu thân trong 3 bộ phận.

**Mẹo: la-de phòng thủ điểm** là lớp bảo vệ, **khoang đổ bộ** mang các đợt thả.

Chiếc Icarus đầu tiên chưa hoàn thiện, bay trên Skyhold như một cuộc thử nghiệm thực địa. Đánh nó đủ đau, nó sẽ bỏ chạy.

giáp thân trước 2 / hông 2 / sau 2 / nóc 2; Tổng 35% máu thân trong 3 bộ phận; pha ở 45%.

**Mẹo: radar** chỉ điểm cho pháo địch.

Khí cầu trinh sát bọc giáp của Wolff: thấy hết mọi thứ và chỉ đường cho máy bay của hắn.

giáp thân trước 5 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 14 bộ phận; pha ở 60%, 25%.

**Mẹo:** chiếm **hải đăng** để thấy hạm đội; phá cả hai **CIWS** (hoặc đánh chìm tuần dương hạm và tàu hộ vệ bên cạnh) trước khi dùng tên lửa và drone; mỗi **pháo chính** bị phá bớt một phần ba loạt pháo và loạt bắn mạn; phá **radar** thì đạn pháo rơi lệch; phá **buồng máy** thì nó chạy chậm lại.

Soái hạm của Kessler: thiết giáp hạm lớn nhất từng được đóng, ba tháp pháo ba nòng 406 mm, tháp chỉ huy kiểu chùa trên cả một rừng súng, ống phóng cạnh ống khói và khoang chở tàu đổ bộ. Hông tàu chặn được đạn xe tăng; boong thì không. Nó không bao giờ đánh ở nơi nó không rút được.

giáp thân trước 2 / hông 2 / sau 2 / nóc 2; Tổng 35% máu thân trong 11 bộ phận; pha ở 60%, 25%.

**Mẹo:** phá **cửa thả drone** và **khoang phóng UAV** để chặn drone, và phá **máy phát khiên** trước khi nó xuống máu.

Tàu sân bay biết bay của Hive: phóng drone từ bụng, bắn pháo sáng mồi bẫy và dựng khiên khi bị thương. Chỉ những gì bắn được lên trời mới kết liễu được nó.

giáp thân trước 5 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 9 bộ phận; pha ở 60%, 25%.

**Mẹo:** vòng ra sau đánh **cửa xưởng** (giáp cấp 2): phá một cửa là sinh xe giảm một nửa, phá cả hai là ngừng hẳn; phá **cụm xích** để làm chậm.

Nhà máy di động của Varga: vừa lăn bánh vừa đóng xe tăng, rồi tung chúng ra trận qua các cửa thả.

giáp thân trước 5 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 9 bộ phận; pha ở 60%, 25%.

**Mẹo: đầu máy** là bộ phận quan trọng nhất: phá nó là tàu chỉ bò nửa tốc độ trong khi bạn đánh toa tên lửa.

Một đoàn tàu tên lửa đang băng qua Metro City tới bãi phóng. Tới nơi là đếm ngược bắt đầu. Đừng để nó tới nơi.

giáp thân trước 5 / hông 3 / sau 2 / nóc 3; Tổng 35% máu thân trong 9 bộ phận; tự sửa một bộ phận một lần mỗi trận; pha ở 60%, 25%.

**Mẹo: khẩu cối** là nòng dài có máu riêng; phá nó là hết quả đạn 800 mm. Bốn tháp pháo chỉ để tự vệ.

Một pháo đài biết đi dựng quanh khẩu pháo cỡ 2B1 Oka, mối đe dọa lớn của Orlov: chậm, to và tự tin.

giáp thân trước 5 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 7 bộ phận; pha ở 60%, 25%.

**Mẹo: cửa ống phóng** mang tên lửa (lộ trên mặt nước lúc cảnh báo); **tháp chỉ huy** ngắm tên lửa phòng không; **sô-na** là hệ điều khiển hỏa lực.

Tàu ngầm tên lửa của Kessler, giờ trong tay Thorne: nổi lên, phóng một loạt rồi lại lặn.

giáp thân trước 5 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 14 bộ phận; pha ở 60%, 25%.

**Mẹo: boong cất cánh** nuôi máy bay và mang đòn không kích; phá nó trước. **CIWS** bắn hạ tên lửa trước khi chúng trúng.

Soái hạm của hạm đội mới của Kessler: tàu sân bay đánh bằng máy bay, không bằng pháo.

giáp thân trước 2 / hông 2 / sau 2 / nóc 2; Tổng 35% máu thân trong 10 bộ phận; thân không nhận sát thương tới khi vỡ động cơ ×2; pha ở 60%, 25%.

**Mẹo:** phá hai **động cơ** để mở thân; sau đó tới các nhà chứa drone và radar ngắm cao xạ.

Sở chỉ huy bay của Wolff trên Skyhold: radar, tên lửa và một khoang chứa drone. Nó điều khiển mọi máy bay Hegemon trên Meridian Coast.

giáp thân trước 3 / hông 3 / sau 3 / nóc 3; Tổng 35% máu thân trong 8 bộ phận.

**Mẹo:** phá **cửa thả khoang** (mỗi cửa mất là thả chậm hơn; mất một cửa thì đòn đổ bộ lớn chỉ còn ba khoang) và **tháp la-de phòng thủ** trước khi dùng tên lửa.

Con tàu đưa quân của Aurel từ quỹ đạo xuống Skygate Array, từng khoang một.

giáp thân trước 4 / hông 4 / sau 4 / nóc 4; Tổng 35% máu thân trong 12 bộ phận.

**Mẹo:** phá **động cơ đẩy chính** để nhốt nó ở tầng thấp, và phá **ăng-ten liên kết vệ tinh** để chặn thanh vonfram; nên dọn hai **tháp la-de phòng thủ điểm** trước khi trông vào tên lửa.

Chiến hạm quỹ đạo của Aurel: thân tàu hình mũi dao, thượng tầng bậc thang dưới tháp chỉ huy và cả một dãy động cơ ở đuôi, được chế tạo để tấn công từ quỹ đạo và đưa Aurel ra ngoài tầm với của mọi người. Chiếc đầu tiên xuất hiện sẽ bỏ chạy khi bị thương đủ nặng. Chiếc trên bệ phóng đã hoàn chỉnh.

giáp thân trước 4 / hông 4 / sau 4 / nóc 4; Tổng 35% máu thân trong 9 bộ phận.

**Mẹo:** tia **la-de chính** mang đòn tia mặt trời; phá nó là hết tia. **Tháp la-de phòng thủ** bắn hạ tên lửa của bạn.

Một trong những chấm sáng cuối cùng còn trên quỹ đạo sau phần kết: trạm gương kiểu Znamya.

Sheet 02_boss/Boss_sieu_vu_khi — Siêu vũ khí (15 dòng, 18 cột)

| id | dung_boi | aim | cooldown_s | exposed_s | first | halt_s | hold | icon | late_cooldown_s |
|---|---|---|---|---|---|---|---|---|---|
| airship_carpet | command_airship | group | 50 |  |  |  |  | bomb |  |
| bastion_420_shell | fortress_bastion | group | 45 |  |  |  |  | mortar |  |
| behemoth_barrage | behemoth | group | 45 |  |  |  |  | artillery |  |
| bug_rod_rain | silver_bug | group | 45 |  | 5 |  |  | ballistic | 45 |
| carrier_heavy_bomb | drone_mothership | group | 45 | 1.3 |  | TRUE |  | bomb |  |
| daedalus_mass_drop | daedalus | group | 50 |  |  |  |  | reinforce |  |
| doomsday_missile | nuke_train | hq | 50 |  |  |  |  | ballistic |  |
| fortress_203_barrage | mobile_fortress | group | 50 |  |  |  |  | artillery |  |
| hyperion_sun_beam | hyperion | group | 50 |  |  |  |  | ballistic |  |
| ixion_crush_charge | ixion | group | 45 |  | 6 |  |  | barrage |  |
| kraken_air_raid | kraken | group | 50 |  |  |  |  | bomb |  |
| leviathan_volley | leviathan | base | 50 |  |  |  | cruise | artillery |  |
| moloch_factory_dump | moloch | group | 50 |  |  |  |  | reinforce |  |
| monster_800_shell | monster | group | 50 |  |  |  |  | mortar |  |
| typhon_underwater_launch | typhon | base | 50 |  |  |  | cruise | missile |  |

*In 10 / 18 cột; 6 cột khác: xem sheet.*

Sheet 02_boss/Boss_ho_tong — Hộ tống boss (13 dòng, 9 cột)

| id | boss | marks | on | phase_drop | phase_halt_s | phase_refill |
|---|---|---|---|---|---|---|
| armored_train | armored_train |  |  |  | 6 |  |
| behemoth | behemoth |  |  |  |  |  |
| behemoth_inferno | behemoth_inferno |  |  |  |  |  |
| behemoth_tempest | behemoth_tempest |  |  |  |  | TRUE |
| command_airship | command_airship |  |  |  |  |  |
| drone_mothership | drone_mothership |  |  |  |  |  |
| earth_borer | earth_borer |  | surface | para |  |  |
| fortress_bastion | fortress_bastion |  |  |  |  |  |
| landing_hovercraft | landing_hovercraft |  |  |  |  |  |
| mega_gunship | mega_gunship |  |  |  |  |  |
| mobile_fortress | mobile_fortress |  |  |  |  |  |
| nuke_train | nuke_train |  |  |  |  |  |
| silver_bug | silver_bug | 0.6;0.25 |  |  |  |  |

Bảng đầy đủ: xem sheet `Boss` (33 dòng), `Boss_vu_khi` (219 dòng), `Boss_bo_phan` (153 dòng), `Boss_hang` (42 dòng).

## Tham khảo ngoài đời và game

Thông số ngoài đời lấy từ nguồn trong repo (sheet Nguon_tham_chieu của 08_tham_chieu); chỗ chưa có nguồn ghi NEED_SOURCE, không điền từ trí nhớ.

### Boss_tham_chieu

33 dòng. Độ tin cậy: da_kiem_chung 4, uoc_dinh 17, ban_dau_doan 6, NEED_SOURCE 6. Loại: NEED_SOURCE 6, doi_that 24, game 1, gia_tuong 2.

- `argus` (Argus · Khí cầu trinh sát): mẫu thật: JLENS (khí cầu radar neo); game: Red Alert 2; giống: biến thể của khí cầu chỉ huy, khí cầu radar neo; độ tin: uoc_dinh; nguồn: R_unit_refs, R_machine_brigade_can_bang, R_unit_sheet.
- `armored_train` (Juggernaut · Đoàn tàu bọc thép): mẫu thật: tàu bọc thép Liên Xô BP-35;B-38 152 mm;2B11 120 mm; giống: đầu máy diesel bọc thép kéo toa pháo; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, R_machine_brigade_can_bang, R_armored_train, R_unit_sheet.
- `bastion_mk0` (Bastion Mk.0 · Pháo đài nguyên mẫu): mẫu thật: 2B8 240 mm;Bofors 40 mm; phim / truyện: Star Wars; giống: bản đầu, nhỏ của Bastion; độ tin: uoc_dinh; nguồn: R_unit_refs, R_machine_brigade_can_bang, R_unit_sheet.
- `behemoth` (Behemoth · Quái vật thép): mẫu thật: Object 279 (1959: bốn dải xích, thân dẹt);giáp composite, APS và cảm biến hiện đại;2A65 1…; game: Warhammer 40,000; giống: 'thiết giáp hạm trên cạn' bốn cụm xích; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_object_279, R_machine_brigade_can_bang, R_behemoth, R_unit_sheet.
- `behemoth_inferno` (Inferno · Behemoth phun lửa): mẫu thật: TOS-1A;Object 279 (1959); game: Warhammer 40,000; giống: Behemoth phun lửa, thùng nhiên liệu đỏ; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, R_machine_brigade_can_bang, R_behemoth_inferno, R_unit_sheet.
- `behemoth_mk0` (Behemoth Mk.0 · Behemoth nguyên mẫu): mẫu thật: Object 279 (1959);giáp composite, APS và cảm biến hiện đại; game: Warhammer 40,000; giống: Behemoth đời đầu, nhỏ hơn; độ tin: uoc_dinh; nguồn: R_unit_refs, R_machine_brigade_can_bang, R_unit_sheet.
- `behemoth_mk2` (Behemoth Mk.II · Behemoth nâng cấp): mẫu thật: Object 279 (1959);giáp composite, APS và cảm biến hiện đại; game: Warhammer 40,000; giống: Behemoth đời hai; độ tin: uoc_dinh; nguồn: R_unit_refs, R_machine_brigade_can_bang, R_unit_sheet.
- `behemoth_tempest` (Tempest · Behemoth pháo điện từ): mẫu thật: US Navy EMRG (pháo điện từ);Object 279 (1959); game: Warhammer 40,000; giống: Behemoth hai tháp pháo điện từ; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, R_machine_brigade_can_bang, R_behemoth_tempest, R_unit_sheet.
- `command_airship` (Roc · Khí cầu chỉ huy): mẫu thật: Airlander 10;Lockheed P-791 (khí cầu lai hiện đại); game: Red Alert 2; giống: 'Sky Admiral', thiết giáp hạm bay hai túi khí; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_hybrid_air_vehicles_airlander_10, R_machine_brigade_can_bang, R_command_airship, R_unit_sheet.
- `daedalus` (Daedalus · Tàu đổ bộ quỹ đạo): phim / truyện: Star Wars: Attack of the Clones; giống: Tàu đổ bộ tấn công của Aurel; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_reference_real, R_machine_brigade_can_bang, R_daedalus, R_mb_p20_bosses, R_unit_sheet.
- `drone_mothership` (Matriarch · Tàu mẹ drone): mẫu thật: Airlander 10 (khí cầu mẹ hiện đại);drone FPV; game: Red Alert 2; giống: khí cầu bọc thép phóng drone; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, W_wikipedia_hybrid_air_vehicles_airlander_10, R_machine_brigade_can_bang, R_drone_mothership, R_unit_sheet.
- `earth_borer` (Tartarus · Máy khoan): mẫu thật: 'Battle Mole' của Liên Xô;máy khoan hầm TBM;2A70 100 mm; giống: 'Earth Worm': máy khoan đất bọc thép ba đốt; độ tin: ban_dau_doan; nguồn: R_unit_refs, R_reference_real, R_machine_brigade_can_bang, R_earth_borer, R_unit_sheet.
- `fenrir` (Fenrir · Xe tiên phong): mẫu thật: NASA Crawler-Transporter;Kharkovchanka (1959); phim / truyện: Star Wars; giống: biến thể của pháo đài di động; độ tin: uoc_dinh; nguồn: R_unit_refs, R_machine_brigade_can_bang, R_unit_sheet.
- `fortress_bastion` (Bastion · Pháo đài): mẫu thật: 2B8 240 mm;Bofors 40 mm;9M133 Kornet; phim / truyện: Star Wars; giống: pháo đài bánh xích bọc giáp tấm dày; độ tin: uoc_dinh; nguồn: R_unit_refs, R_reference_real, R_machine_brigade_can_bang, R_fortress_bastion, R_unit_sheet.
- `icarus_mk0` (Icarus Mk.0 · Phi thuyền nguyên mẫu): game: Halo; phim / truyện: Star Wars;The Expanse; giống: Bản đầu của Icarus (chiến hạm vũ trụ, nhỏ hơn); độ tin: ban_dau_doan; nguồn: R_unit_refs, R_machine_brigade_can_bang, R_unit_sheet.
- … 12 dòng có tham chiếu nữa: xem sheet Boss_tham_chieu.

Nguồn được dùng (tiêu đề như repo ghi; link khi repo có):

- `R_armored_train`: spec dựng lại armored_train (độ tin 3)
- `R_behemoth`: spec dựng lại behemoth (độ tin 3)
- `R_behemoth_inferno`: spec dựng lại behemoth_inferno (độ tin 3)
- `R_behemoth_tempest`: spec dựng lại behemoth_tempest (độ tin 3)
- `R_command_airship`: spec dựng lại command_airship (độ tin 3)
- `R_daedalus`: spec dựng lại daedalus (độ tin 3)
- `R_drone_mothership`: spec dựng lại drone_mothership (độ tin 3)
- `R_earth_borer`: spec dựng lại earth_borer (độ tin 3)
- `R_fortress_bastion`: spec dựng lại fortress_bastion (độ tin 3)
- `R_ixion`: spec dựng lại ixion (độ tin 3)
- `R_landing_hovercraft`: spec dựng lại landing_hovercraft (độ tin 3)
- `R_leviathan`: spec dựng lại leviathan (độ tin 3)
- `R_machine_brigade_can_bang`: Rà soát cân bằng (Machine_Brigade_Can_bang.xlsx) (độ tin 3)
- `R_mb_p20_bosses`: script Blender mb_p20_bosses.py (docstring) (độ tin 3)
- `R_mb_redesign_20y`: script Blender mb_redesign_20y.py (docstring) (độ tin 3)
- `R_mega_gunship`: spec dựng lại mega_gunship (độ tin 3)
- `R_mobile_fortress`: spec dựng lại mobile_fortress (độ tin 3)
- `R_moloch`: spec dựng lại moloch (độ tin 3)
- `R_monster`: spec dựng lại monster (độ tin 3)
- `R_nuke_train`: spec dựng lại nuke_train (độ tin 3)
- `R_reference_real`: reference_real.json (kích thước thật, độ tin conf) (độ tin 3)
- `R_typhon`: spec dựng lại typhon (độ tin 3)
- `R_unit_refs`: unit_refs.json (tham chiếu ngoài đời / phim / game theo đơn vị) (độ tin 3)
- `R_unit_sheet`: unit_sheet.json (hình dạng, mô tả từ bảng cân bằng) (độ tin 3)
- `W_wikipedia_belaz_75710`: Wikipedia 'BelAZ 75710' (độ tin 2)
- `W_wikipedia_boeing_ch_47_chinook`: Wikipedia 'Boeing CH-47 Chinook' (độ tin 2)
- `W_wikipedia_crawler_transporter`: Wikipedia 'Crawler-transporter' (độ tin 2)
- `W_wikipedia_hybrid_air_vehicles_airlander_10`: Wikipedia 'Hybrid Air Vehicles Airlander 10' (độ tin 2)
- `W_wikipedia_iowa_class_battleship`: Wikipedia 'Iowa-class battleship' (độ tin 2)
- `W_wikipedia_landing_craft_air_cushion`: Wikipedia 'Landing Craft Air Cushion' (độ tin 2)
- … 2 nguồn nữa: xem sheet Nguon_tham_chieu của 08_tham_chieu.

Sheet 02_boss/Boss_so_sanh_that — Boss: so sánh với thật: 108 dòng, 18 cột; bảng đầy đủ: xem sheet Boss_so_sanh_that.

## Các sheet của file

Mọi sheet, số dòng và ý nghĩa cột nằm trong 00_index.xlsx (Muc_luc_sheet, Schema). Sheet `input_<tên>` là bản chép của một sheet nguồn để công thức Excel đọc cùng file; sửa ở sheet nguồn, không sửa bản chép.

- `Boss` (33 dòng): Boss — Mỗi boss (41: chủ lực, mini, biến thể) một dòng: giá trị game (đã dựng) và trường gốc
- `Boss_be_goc` (133 dòng): Boss: bệ phụ gốc — secondary[]: bệ phụ (chỉ số bệ = thu_tu + 1; bệ 0 là vũ khí chính)
- `Boss_bo_phan` (153 dòng): Boss: bộ phận — parts[]: bộ phận phá được (use = mẫu ở Boss_bo_phan_thu_vien)
- `Boss_phase` (6 dòng): Boss: pha — phases[]: ngưỡng máu, biến hình, đổi vũ khí / sát thương
- `Boss_bien_the_chinh` (64 dòng): Boss: chỉnh bộ phận của biến thể — variant.tune: bộ phận -> trường đổi
- `Boss_ham_doi` (8 dòng): Boss: hạm đội đi kèm — fleet[]
- `Boss_tiers_schedule` (14 dòng): Boss: tiers_schedule — Danh sách con 'tiers_schedule' của Boss (tự sinh).
- `Boss_tiers_schedule_steps` (24 dòng): Boss: tiers_schedule: steps — Danh sách con 'steps' của Boss_tiers_schedule (tự sinh).
- `Boss_air` (1 dòng): Boss: air — Danh sách con 'air' của Boss (tự sinh).
- `Boss_vu_khi` (219 dòng): Boss: vũ khí theo bệ — Mỗi bệ của boss khi dựng (thư viện bộ phận, mountWeapons, biến thể): một dòng; số lấy từ 01_chien_dau/Vu_khi (giá trị game)
- `Boss_tam_toi_thieu` (219 dòng): Boss: tầm tối thiểu — Mỗi bệ của mỗi boss một dòng: độ cao nòng từ GLB (vẽ lại) và dữ liệu, góc nòng (barrelLimits), tầm tối thiểu theo hình học, đề xuất, vùng chết và vũ…
- `Boss_goc_nong` (41 dòng): Boss: góc nòng — barrelLimits: góc hạ / nâng nòng theo lớp và họ vũ khí (estimated = uoc_dinh), luật xếp lớp, độ cao mục tiêu tham chiếu; đọc bởi Tools/export/boss_mi…
- `Boss_ghi_de_tam` (68 dòng): Boss: tầm riêng theo vũ khí — MB_FINAL F2: mỗi cặp boss + vũ khí có tầm riêng một dòng (balance.json bossWeaponOverrides; chỉ bệ của boss đó, vũ khí chung không đổi; biến thể khôn…
- `Boss_bo_phan_thu_vien` (19 dòng): Thư viện bộ phận boss — bossParts: mẫu bộ phận (máu theo phần, giáp, vũ khí, xác)
- `Boss_khung` (8 dòng): Khung boss — bossFrames: kiểu di chuyển và trường mặc định theo khung
- `Boss_hang` (42 dòng): Hạng boss — bossRanks: main / mini: hệ số sát thương, nhịp, máu, pha, thưởng
- `Boss_sieu_vu_khi` (15 dòng): Siêu vũ khí — bigAttacks: cảnh báo, chu kỳ, cách nhắm, tầm, mục tiêu
- `Boss_sieu_vu_khi_don` (16 dòng): Siêu vũ khí: đòn — strikes[]: hình, số lượng, sát thương, bán kính
- `Boss_sieu_vu_khi_luat` (34 dòng): Siêu vũ khí: luật — bigAttackRules: lần đầu, chặn, né, theo độ khó
- `Boss_ho_tong` (13 dòng): Hộ tống boss — escorts[]: đội đến cùng boss và đội gọi thêm ở pha sau
- `Boss_ho_tong_den` (48 dòng): Hộ tống: đến cùng boss — escorts[].arrive[]
- `Boss_ho_tong_pha` (8 dòng): Hộ tống: gọi ở pha sau — escorts[].phase.units[]
- `Boss_ho_tong_phase` (17 dòng): Hộ tống boss: phase — Danh sách con 'phase' của Boss_ho_tong (tự sinh).
- `Boss_ho_tong_phases` (2 dòng): Hộ tống boss: phases — Danh sách con 'phases' của Boss_ho_tong (tự sinh).
- `Boss_ho_tong_phases_units` (4 dòng): Hộ tống boss: phases: units — Danh sách con 'units' của Boss_ho_tong_phases (tự sinh).
- `Boss_ho_tong_mau` (8 dòng): Hộ tống mẫu theo tướng — escortTemplates: đội hộ tống mặc định của mỗi tướng
- `Boss_ho_tong_mau_den` (32 dòng): Hộ tống mẫu: đến — escortTemplates.*.arrive[]
- `Boss_ho_tong_mau_pha` (14 dòng): Hộ tống mẫu: pha sau — escortTemplates.*.phase[]
- `Boss_ho_tong_mau_phases` (2 dòng): Hộ tống mẫu theo tướng: phases — Danh sách con 'phases' của Boss_ho_tong_mau (tự sinh).
- `Boss_ho_tong_mau_phases_units` (4 dòng): Hộ tống mẫu theo tướng: phases: units — Danh sách con 'units' của Boss_ho_tong_mau_phases (tự sinh).
- `Boss_ho_tong_luat` (42 dòng): Hộ tống: luật — escortRules: trần theo độ khó, Săn trùm, dây buộc, thưởng
- `Sanhunt` (33 dòng): Săn trùm — Boss của Săn trùm theo thứ tự cốt truyện (port BossHunts.Story: chương theo thứ tự dữ liệu, boss theo nhiệm vụ đầu tiên đánh nó, rồi ô chương, rồi Un…
- `Boss_dps` (33 dòng): Boss: DPS duy trì — Tổng DPS duy trì của boss (FirePower.Sustained mọi bệ, trên mặt đất, trước bảng sát thương; chưa nhân hạng / pha / fireRate) bây giờ và ở bản gốc
- `Boss_hieu_qua` (165 dòng): Boss: hiệu quả vũ khí chính — Mỗi boss x vũ khí chính (bệ 0) x xe tham chiếu (spec 03 B): số đòn để hạ, thời gian hạ khi dồn hỏa lực, số xe trúng lõi / rìa (5 xe cách 8 m: hàng và…
- `Sanhunt_chua_xep` (8 dòng): Săn trùm: boss chưa có ô chương — BossHunts.Unslotted: boss mới và chương nó đứng sau
- `Sanhunt_ho_tro` (12 dòng): Săn trùm: hỗ trợ tác chiến — HuntSupports.All (BossHunt.cs): 12 hỗ trợ chọn sau boss chủ lực
- `Boss_tham_chieu` (33 dòng): Boss: tham chiếu ngoài đời — Mỗi boss một dòng: nguồn cảm hứng, phần lấy từ mẫu nào, hệ số phóng to, phần giả tưởng (spec 12.2; chỉ dữ liệu có trong repo)
- `Boss_so_sanh_that` (108 dòng): Boss: so sánh với thật — So sánh game với thật (spec 12.4): mỗi thông số có đối chiếu một dòng; ty_le = game / thật, khoảng cho phép, co_lech_lon = ngoài khoảng mà không có c…
- `Hang_so_boss` (28 dòng): Hằng số boss: đòn lớn, pha, hộ tống — Assets/MachineBrigade/Resources/Data/tunables.json: 'bosses' (lớp chủ → tên): một dòng một hằng số; mã game đọc qua SimTunables, giữ nguyên giá trị k…
