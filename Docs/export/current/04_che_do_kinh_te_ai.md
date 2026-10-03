# 04_che_do_kinh_te_ai — Chế độ, kinh tế, AI, meta, giao diện

Chế độ chơi, độ khó, kinh tế, tác chiến, AI, thăng hạng, mở khóa, cửa hàng, giao diện.

Gói cân bằng Machine Brigade, commit 0cafe94b, ngày 2026-10-03. Số liệu đầy đủ ở 04_che_do_kinh_te_ai.xlsx; file này chỉ nêu luật, giải thích, lý do thiết kế, tham khảo và bảng nhỏ (tối đa 20 dòng, bảng lớn: xem sheet).

## Tổng quan

**Thể loại:** RTS / auto-battler trên điện thoại (màn ngang). Người chơi chỉ huy một binh đoàn phương tiện: xe tăng, xe bọc thép, pháo, phòng không, trực thăng, máy bay. Trận đấu phần lớn tự chạy: chỉ huy AI của người chơi tự mua quân (Tự mua) và tự gọi hỏa lực (Yểm trợ); người chơi can thiệp bằng lệnh Tấn công / Phòng thủ, chọn thẻ để triển khai, gọi hỏa lực vào điểm chọn.

**Vòng lặp:** điểm chỉ huy (CP) tăng theo thời gian và cứ điểm giữ được → mua phương tiện từ bộ bài (8 xe + 2 hỗ trợ) → phương tiện được thả dù xuống bãi thả của phe → chiến đấu tự động theo hệ thống khắc chế giáp/đạn → hạ địch được hoàn một phần CP.

**Ngoài trận:** lên hạng thẻ (bản thiết kế + xu), trang bị theo nhánh (Thiết giáp, Xe nhẹ, Pháo binh, Không quân), căn cứ (loadout tháp theo ô cỡ), hòm đồ, chiến dịch 193 nhiệm vụ trong 15 chương, Tác chiến (chơi lại chiến dịch lớn, 4 cấp độ, mutator tuần), Pháo đài tuần, Săn trùm, Vô tận, Sinh tồn. Một loại tiền duy nhất: xu.

**Bản đồ:** 25 chiến trường 300 × 300 m, mỗi bản có phiên bản chiếm cứ điểm, sinh tồn và công thành; 25 bản dài 300 × 480 m (căn cứ nhiều lớp) cho Công thành, Phòng thủ, Vô tận và Pháo đài tuần. **Mô phỏng:** cố định 20 tick/giây, xác định (deterministic), tách khỏi phần hình ảnh.

![Trong trận (ảnh 3D; HUD ở ảnh này là bản trước phase 10, HUD mới ở phần 18): bản đồ nhỏ, thanh nhiệm vụ, nút lệnh, khay…](images/04_che_do_kinh_te_ai_shots_battle1.png)

*Hình: Trong trận (ảnh 3D; HUD ở ảnh này là bản trước phase 10, HUD mới ở phần 18): bản đồ nhỏ, thanh nhiệm vụ, nút lệnh, khay thẻ và CP. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

![Bản đồ sa mạc Dunebreak sau khi phóng to 50%; nhà cửa đã chỉnh tỷ lệ so với xe.](images/04_che_do_kinh_te_ai_shots_battle2.png)

*Hình: Bản đồ sa mạc Dunebreak sau khi phóng to 50%; nhà cửa đã chỉnh tỷ lệ so với xe. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

## Chế độ chơi

Bốn độ khó Dễ / Thường / Khó / Cực khó ảnh hưởng AI địch, thu nhập, xe tinh nhuệ và thưởng:

Thời tiết (nắng, âm u, mưa, bão, tuyết, bão cát, sương mù, đêm) đổi dần trong 8 giây và ảnh hưởng tầm nhìn/hình ảnh.

![Công thành.](images/04_che_do_kinh_te_ai_shots_siege.png)

*Hình: Công thành. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

![Phòng thủ căn cứ.](images/04_che_do_kinh_te_ai_shots_defend.png)

*Hình: Phòng thủ căn cứ. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

![Boss.](images/04_che_do_kinh_te_ai_shots_boss.png)

*Hình: Boss. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

![Nhiệm vụ săn: mục tiêu hiện hình thoi đỏ trên bản đồ nhỏ.](images/04_che_do_kinh_te_ai_shots_hunt.png)

*Hình: Nhiệm vụ săn: mục tiêu hiện hình thoi đỏ trên bản đồ nhỏ. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

Sheet 04_che_do_kinh_te_ai/Che_do — Chế độ (12 dòng, 51 cột)

| id | ten_che_do | kho_cp | cp_khoi_dau_nhan_he_so | ho_so_ai | trung_lap | lists_maps | numbers_anti_snipe_range | numbers_anti_snipe_share | numbers_base_radius |
|---|---|---|---|---|---|---|---|---|---|
| assault | Assault | 30;45 | TRUE | assault | ammo_depot |  |  |  |  |
| bossrush | BossRush | 45;60 | TRUE | bossrush |  |  |  |  |  |
| conquest | Conquest | 30;45 | TRUE | conquest | radar;workshop |  |  |  |  |
| deathmatch | Deathmatch | 30;45 | TRUE | deathmatch | ammo_depot;aa_site |  |  |  |  |
| defend | Defend | 30;45 | TRUE | defend |  |  |  |  |  |
| endless | Endless | 30;45 | TRUE | defend |  |  |  |  |  |
| hill | KingOfTheHill | 30;45 | TRUE | hill | workshop |  |  |  |  |
| operations | Operation |  | FALSE | operation |  |  |  |  |  |
| showdown | Showdown |  | TRUE | showdown | ammo_depot | ashfield;capital;coralisles;dunebreak;foundry;frostpeak;gre… | 60 | 0.25 | 46 |
| siege | Siege | 40;55 | TRUE | siege | aa_site |  |  |  |  |
| survival | Survival | 30;40 | TRUE | survival | workshop |  |  |  |  |
| weekly | Weekly |  | TRUE | siege | ammo_depot |  |  |  |  |

*In 10 / 51 cột; 38 cột khác: xem sheet.*

## Cân bằng chế độ và độ khó

Đo bằng bộ bài mẫu 8 thẻ, độ khó Thường, chỉ huy tự động của người chơi (2 seed trên 2–3 bản đồ mỗi chế độ; đo đủ 5 seed ở phase kiểm tra). Bên đang thua quá xa sau phút 4 (quân trên sân chênh từ 1,6 lần) được +25% thu nhập và một lần thả tiếp viện miễn phí; ở Phòng thủ và Vô tận, nếu người chơi áp đảo quá thì địch được thêm một đợt công phá. Đợt địch ở Phòng thủ và Vô tận mạnh theo **Sức mạnh căn cứ** (cùng con số hiện ở màn Căn cứ), có xe ủi, pháo công thành và pháo tầm xa bắn từ ngoài tầm tháp.

| Chế độ | Người chơi thắng | Thời lượng trung vị (phút) | Mục tiêu |
|---|---|---|---|
| Giữ cứ điểm | 7/12 | 7,4 | 55–65%, 6–10 phút |
| Tử chiến (điểm theo giá CP, ngưỡng 480) | 2/6 (8/12 ở seed khác) | 8,5 | 6–9 phút |
| Vua đồi (ngưỡng 170) | 8/12 | 7,4 | 55–65%, 6–9 phút |
| Công phá | 8/12 | 4,7 | 60–70% |
| Công thành | 6/6 | 10,7 (9,2–14) | 60–75%, 10–15 phút |
| Phòng thủ | giữ HQ 6/6, mất tuyến ngoài mọi trận (phút 4–6) |  | mất tuyến ngoài 50–70%, giữ HQ ~4/5 |
| Vô tận |  | 15,1 | 12–15 phút |
| Sinh tồn |  | 12,0 | 8–12 phút |
| Săn trùm | 4/4 | 18,7 | 15–25 phút |
| Pháo đài tuần | chưa thắng được từ giai đoạn 1–3 |  | giai đoạn cuối vẫn là thử thách |

### AI mua quân theo độ khó

Logic mua quân xác định (deterministic): một hàm chấm điểm (khắc chế quân địch đang thấy, vai trò còn thiếu, giá trị thực chiến theo giá) dùng ở mức khác nhau cho mỗi độ khó. Tên độ khó thống nhất: chiến dịch và Tác chiến đổi Anh hùng → Khó, Thép → Cực khó (kỷ lục lưu theo số nên giữ nguyên).

Sheet 04_che_do_kinh_te_ai/Do_kho — Độ khó (4 dòng, 13 cột)

| id | he_so_dich_tran_nhanh | thu_tu | bien_co_ally | bien_co_ally_waves | bien_co_directions | bien_co_elites | bien_co_escorts | bien_co_step | bien_co_warning |
|---|---|---|---|---|---|---|---|---|---|
| Easy | 0.4 | 0 | 0.7 | -1 | 1;2 | FALSE | 2 | 0 | 15 |
| Hard | 0.85 | 2 | 0.3 | -1 | 2;3 | FALSE | 4 | 2 | 8 |
| Normal | 0.75 | 1 | 0.5 | -1 | 2;2 | FALSE | 3 | 1 | 10 |
| VeryHard | 1.08 | 3 | 0.15 | 1 | 3;4 | TRUE | 5 | 3 | 6 |

*In 10 / 13 cột; 1 cột khác: xem sheet.*

## Luật trận, phần vô hạn, trung lập, thoại và kết trận

### 4 hồi

Chiến dịch có 15 chương trong 4 hồi (trường `act` của campaign.json); mỗi hồi kết bằng một chương chuyển tiếp (13, 14, 15). Sau c9m10 là **Kết mạch Thorne** (thẻ chuyển, trước chương 15, hiện một lần và có trong dòng thời gian của Hồ sơ); phần kết thật sau c12m10; thắng c12m10 mở cấp Huyền thoại của Tác chiến.

### Luật trận theo chế độ

Mỗi chế độ có bảy trường dữ liệu (thắng, thua, giờ, hiệp phụ, hòa, điểm, bắt kịp) trong `matchRules` của balance.json; số trong dữ liệu thay số cũ của phiên chế độ. Không có luật chung "hết quân là thua"; giờ tối đa của màn chiến dịch đặt theo từng màn. Tử chiến: mỗi xe hạ cho min(giá gốc CP, 18) điểm. Tác chiến: phần tổn thất tính theo CP gốc đã mất (2.000 khi mất 0, về 0 khi mất 150).

| Chế độ | Thắng | Thua | Giờ | Hiệp phụ | Hòa | Điểm | Bắt kịp |
|---|---|---|---|---|---|---|---|
| **Giữ cứ điểm** | Đối phương về 0 điểm, hoặc nhiều điểm hơn khi hết giờ | Về 0 điểm, hoặc ít điểm hơn khi hết giờ | 10 phút | Bằng điểm khi hết giờ: tối đa 60 s, bên chiếm thêm cứ điểm trước thắng | Hòa nếu hết hiệp phụ | 500 điểm mỗi bên; bên giữ ít cứ điểm hơn mất 0,8 × (chênh lệch số cứ điểm) điểm/s; 2 phút cuối ×2; giữ cả 3 không cộng thêm | Giảm (tối đa +25%) |
| **Tử chiến** | Đạt 480 điểm, hoặc nhiều điểm hơn khi hết giờ | Đối phương đạt 480 trước, hoặc ít điểm hơn khi hết giờ | 9 phút | Bằng điểm: tối đa 60 s, xe bị hạ đầu tiên quyết định | Hòa nếu hết hiệp phụ | Mỗi xe địch bị hạ: min(baseCP, 18) điểm. Dùng baseCP, không dùng giá sau giảm | Giảm (tối đa +25%) |
| **Vua đồi** | Đạt 170 điểm, hoặc dẫn khi hết giờ | Ngược lại | 9 phút | Bằng điểm hoặc đồi đang tranh khi hết giờ: tối đa 60 s; còn tranh thì kéo dài, một bên giữ riêng thì phân định | Hòa nếu hết hiệp phụ | Một mình giữ đồi: +1 điểm/s; tranh chấp hoặc trống: 0 | Như hiện có |
| **Công phá** | Chiếm A, B, C | Hết quỹ thời gian | Bắt đầu 4:00; chiếm A +2:30; chiếm B +2:30; quỹ tối đa 5:00 | Hết giờ khi đang chiếm dở: kéo dài tới khi chiếm xong hoặc bị đẩy ra, tối đa 60 s | Không có hòa | Không tính điểm; sao (nếu là màn chiến dịch) theo số khu | Như hiện có |
| **Công thành** | Hạ sở chỉ huy pháo đài | Hết giờ | Mặc định chế độ ~18 phút; màn chiến dịch dùng giờ riêng của màn | Mục tiêu cuối đang bị tấn công khi hết giờ: tối đa 60 s | Không có hòa | Không tính điểm | Như hiện có |
| **Phòng thủ** | Sở chỉ huy còn đứng khi hết giờ | Mất sở chỉ huy | ~12 phút (CHECK với thời lượng thiết kế hiện tại) | Không | Không | Không tính điểm; sao (nếu là màn chiến dịch) theo máu sở chỉ huy và số tuyến còn giữ; mất tuyến ngoài KHÔNG là thất bại | Không áp (đợt theo Sức mạnh căn cứ) |
| **Sinh tồn** | Qua hết đợt 10 (đợt 5 có mini boss, đợt 10 có boss chủ lực) | Mất toàn bộ quân hoặc địch chiếm bãi thả | ~8–12 phút; nếu nhịp đợt làm 10 đợt vượt mục tiêu thì chỉnh số đợt hoặc nhịp | Không | Không | Số đợt đã qua | Không áp |
| **Vô tận** | Không có trạng thái thắng | Mất sở chỉ huy | Không giới hạn | Không | Không | Xếp hạng theo thứ tự: đợt hoàn thành (giảm dần) → baseCP xe địch đã hạ (giảm dần) → thời gian sống (giảm dần) | Không áp |
| **Săn trùm** | Hạ đủ 10 boss | Mất toàn bộ quân hoặc hết 30 phút | 30 phút | Không | Không | Xếp hạng: số boss hạ (giảm dần) → thời gian hoàn thành (tăng dần) → số bộ phận phá (giảm dần). Thưởng CP mỗi bộ phận giữ nguyên | Không áp |
| **Pháo đài tuần** | Hạ sở chỉ huy trước khi tuần kết thúc | Mỗi lần đánh có thể dừng giữa chừng; lớp đã phá được giữ | Theo lần đánh (như Công thành) + chu kỳ tuần | Như Công thành | Không | Xếp hạng: đã phá xong? → số lần đánh (tăng dần) → tổng thời gian giao chiến (tăng dần) | Như Công thành |
| **Tác chiến** | Như màn gốc | Như màn gốc | Như màn gốc | Như màn gốc | Như màn gốc | Giữ công thức hiện có (5.000 + thời gian + tổn thất + máu sở chỉ huy, × hệ số cấp). Phần tổn thất đổi từ số xe sang baseCP đã mất: 2.000 khi mất 0, về 0 khi mất 150 baseCP | Như màn gốc |
| **showdown** | Phá nhà chính đối phương | Mất nhà chính | 12 phút | Hết 12 phút: bên có nhà chính còn nhiều % máu hơn từ 5 điểm phần trăm trở lên thắng ngay; chênh dưới 5 điểm → đột tử 90 s (tắt chống bắn tỉa, không xây lại tháp, thu nhập ×2, không đặt lại hồi chiêu… | Bằng nhau sau đột tử → hòa | Không có điểm phụ | Chỉ bắt kịp thu nhập, trần +25%; không tiếp viện miễn phí |

**Sao chiến dịch** (chỉ màn chiến dịch): ★1 hoàn thành; ★2 làm chủ kiểu màn (bảng dưới, theo mục tiêu); ★3 mục tiêu phụ riêng của màn. Không dùng mục tiêu dễ vỡ hay chạy giờ chặt.

**Bảng xếp hạng** sắp theo từng khóa lần lượt, không gộp thành một công thức (không farm được):

| Bảng | Thứ tự sắp |
|---|---|
| endless | đợt (cao hơn trước) → CP gốc đã hạ (cao hơn trước) → thời gian (cao hơn trước) |
| defendEndless | đợt (cao hơn trước) → CP gốc đã hạ (cao hơn trước) → thời gian (cao hơn trước) |
| survivalEndless | đợt (cao hơn trước) → CP gốc đã hạ (cao hơn trước) → thời gian (cao hơn trước) |
| bossrush | boss (cao hơn trước) → thời gian (thấp hơn trước) → bộ phận phá (cao hơn trước) |
| bossrushEndless | boss (cao hơn trước) → thời gian (thấp hơn trước) → bộ phận phá (cao hơn trước) |
| weekly | giai đoạn qua (cao hơn trước) → số lần đánh (thấp hơn trước) → thời gian (thấp hơn trước) |

### Phần vô hạn

- Thắng Phòng thủ, Sinh tồn hoặc Săn trùm: bảng kết quả có **Đánh tiếp (vô hạn)** và **Kết thúc**. Thưởng thắng được ghi nhận trước khi đánh tiếp; thua về sau không lấy lại gì.
- Vô tận (mục menu giữ nguyên) là Phòng thủ bắt đầu ngay ở phần vô hạn: chung mã và chung bảng xếp hạng.
- Tăng độ khó chỉ bằng chỉ số, không thêm xe quá đợt cuối của phần hữu hạn: Phòng thủ / Vô tận / Sinh tồn địch +4% mỗi đợt, ta +2% mỗi đợt (tối đa +30%); Săn trùm địch +8% mỗi boss.
- Sinh tồn hữu hạn 10 đợt: đợt 5 mini boss, đợt 10 boss chủ lực; phần vô hạn mỗi 5 đợt mini boss, mỗi 10 đợt boss chủ lực. Mini boss không có siêu vũ khí.
- Thưởng: 18 xu × 0,9^k mỗi đợt vượt (Săn trùm 60 xu × 0,9^k mỗi boss), trần 600 xu/ngày cho mọi phần vô hạn; huy hiệu +10/+20/+30 đợt, +5/+10 boss. Săn trùm chọn đánh tiếp ở bảng kết quả (không còn lựa chọn 20 s trong trận).

### Trung lập (V1)

Một phe đứng một mình (xe mặt đất) trong 10 m quanh điểm trong 8 s thì chiếm; phe kia chiếm lại cùng cách. **Vòm radar:** bên giữ nhìn thấy 45 m quanh nó. **Xưởng dã chiến:** xe mặt đất của bên giữ trong 14 m hồi 1.5% máu/giây. **Trận địa phòng không bỏ hoang:** chiếm thì dựng một tháp phòng không cho bên giữ; bị phá thì 60 s sau lại bỏ hoang. **Kho đạn:** xe bên giữ trong 14 m được tiếp đạn mỗi 6 s; bị bắn nát thì nổ (300 trong 14 m, trúng cả hai bên). Hải pháo bờ biển, ngọn hải đăng, đoàn xe tiếp tế trung lập giữ như cũ; thùng tiếp tế tranh chấp rơi giữa hai quân và báo trước 15 s. 0–2 loại mỗi bản đồ; bản đối xứng đặt thành cặp đối xứng.

Trên chiến trường mỗi điểm là một vòng tròn trên đất theo màu bên giữ, vạch chiếm chạy quanh theo màu bên đang chiếm; điểm phòng không bỏ hoang nhấp nháy khi chiếm được; chỗ thùng tiếp tế sắp rơi có vòng cảnh báo trong 15 s. Bản đồ nhỏ: ô vuông theo màu bên giữ, cung tiến độ chiếm, vòng hổ phách cho thùng đang rơi.

| Chế độ | Loại trung lập |
|---|---|
| Giữ cứ điểm | Vòm radar, Xưởng dã chiến |
| Tử chiến | Kho đạn, Trận địa phòng không bỏ hoang |
| Vua đồi | Xưởng dã chiến |
| Công phá | Kho đạn |
| Công thành | Trận địa phòng không bỏ hoang |
| Pháo đài tuần | Kho đạn |
| Sinh tồn | Xưởng dã chiến |
| Showdown | Kho đạn |

### Giao diện thoại

- Một dải thoại ở giữa phía dưới, trên khay thẻ, trong vùng an toàn: chân dung nhỏ (44 px; 52 px khi chữ Lớn) rồi tối đa 2 dòng, tên người nói in hoa theo màu phe. Nhân vật thiếu chân dung dùng chân dung tạm theo phe (ô màu tối của phe với chữ cái đầu).
- Không che đồng hồ mục tiêu, thanh boss và cảnh báo siêu vũ khí (tất cả ở dải trên cùng) ở 16:9, 20:9 và 4:3.
- Ưu tiên P0–P4: P0 cảnh báo hệ thống (không phụ thuộc cài đặt, cắt câu đang hiện); P1 cốt truyện / cảnh báo (bỏ qua khoảng cách, chờ câu đang hiện xong); P2 sự kiện của màn (giữ 12 s); P3 phản ứng, P4 không khí (quá 8 s thì bỏ). 9 s / 20 s (có boss) là khoảng cách tối thiểu.

### Chuỗi kết trận

- RUNNING → RESOLVED → PRESENTATION → RESULTS. Ở RESOLVED kết quả, thưởng, sao và điểm đã chốt; từ đó mô phỏng đứng yên (không bước mô phỏng, AI hay chế độ), nên kết quả không phụ thuộc phần trình diễn và replay chốt cùng tick.
- PRESENTATION chỉ là hình ảnh: ẩn khay thẻ và nút lệnh (giữ thanh boss, thông báo, thoại), khung điện ảnh, camera tới mục tiêu cuối trong 1,5 s đầu, boss nổ từng bộ phận cách nhau 0,4 s rồi nổ thân; thắng lần đầu hoặc trận lớn quay chậm ×0,3 từ giây 1,5 bằng đồng hồ hình ảnh (không chạm thời gian mô phỏng).
- Thời lượng: thắng lần đầu màn boss chính hoặc chiến dịch lớn 7 s (6–8), thắng lần đầu 4,5 s (4–5), chơi lại 3 s (2,5–4), thua 3,5 s (3–4, không quay chậm: camera về sở chỉ huy hoặc xe cuối, một vụ nổ, câu của tướng địch).

Sheet 04_che_do_kinh_te_ai/Vo_han — Vô hạn và bảng xếp hạng (6 dòng, 5 cột)

| id | thu_tu_xep_hang | he_so_tang_thuong |
|---|---|---|
| bossrush | -bosses;+seconds;-parts | 0.9 |
| bossrushEndless | -bosses;+seconds;-parts | 0.9 |
| defendEndless | -waves;-killedBaseCp;-seconds | 0.9 |
| endless | -waves;-killedBaseCp;-seconds | 0.9 |
| survivalEndless | -waves;-killedBaseCp;-seconds | 0.9 |
| weekly | -cleared;+attempts;+seconds | 0.9 |

Sheet 06_ban_do/Trung_lap_luat — Trung lập: luật (18 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so | gia_tri_chu |
|---|---|---|---|---|
| modes.Assault | neutrals | Assault |  | ammo_depot |
| modes.Conquest | neutrals | Conquest |  | radar;workshop |
| modes.Deathmatch | neutrals | Deathmatch |  | ammo_depot;aa_site |
| modes.KingOfTheHill | neutrals | KingOfTheHill |  | workshop |
| modes.Showdown | neutrals | Showdown |  | ammo_depot |
| modes.Siege | neutrals | Siege |  | aa_site |
| modes.Survival | neutrals | Survival |  | workshop |
| modes.Weekly | neutrals | Weekly |  | ammo_depot |
| numbers.captureRadius | neutrals | captureRadius | 10 |  |
| numbers.captureSeconds | neutrals | captureSeconds | 8 |  |
| numbers["aa.rebuild"] | neutrals | aa.rebuild | 60 |  |
| numbers["ammo.blast"] | neutrals | ammo.blast | 14 |  |
| numbers["ammo.damage"] | neutrals | ammo.damage | 300 |  |
| numbers["ammo.radius"] | neutrals | ammo.radius | 14 |  |
| numbers["ammo.seconds"] | neutrals | ammo.seconds | 6 |  |
| numbers["radar.radius"] | neutrals | radar.radius | 45 |  |
| numbers["workshop.radius"] | neutrals | workshop.radius | 14 |  |
| numbers["workshop.repair"] | neutrals | workshop.repair | 0.015 |  |

Sheet 05_chien_dich/Ket_tran — Kết trận (5 dòng, 5 cột)

| id | giay | chuyen_dong_cham |
|---|---|---|
| FirstBigWin | 7 | TRUE |
| FirstWin | 4.5 | TRUE |
| Loss | 3.5 | FALSE |
| Replay | 3 | FALSE |
| bo_qua_sau_giay | 0.75 |  |

## Tác chiến

Menu gồm 5 mục: Trang chủ, Chiến dịch, **Tác chiến**, Quân đội, Cửa hàng; Giao tranh (Giữ cứ điểm, Vua đồi, Tử chiến, Công phá, Công thành, Phòng thủ) và Thử thách (Sinh tồn, Vô tận) chọn ở ô chọn chế độ. Tác chiến gom: chơi lại các chiến dịch lớn và các trận nổi bật của cốt truyện (công thành, phòng thủ, đấu tướng) sau khi đã thắng trong chiến dịch (26 trận), chiến dịch của tuần, Pháo đài tuần, Săn trùm và thử thách hằng ngày.

### Cấp độ

Huyền thoại mở sau khi thắng **c12m10** (Icarus rơi, trận cuối chiến dịch; Operations.LegendMission). **Điểm** một trận thắng: 5000 + tối đa 3000 theo thời gian dưới 25 phút + tối đa 2000 theo tổn thất (150 xe mất thì bằng 0) + tối đa 2000 theo máu sở chỉ huy; nhân hệ số cấp cộng phần của mỗi mutator. Thua: 0 điểm. Kỷ lục (điểm cao nhất, thắng nhanh nhất) lưu riêng cho từng trận và từng cấp.

**Thưởng tuần gộp chung một sổ:** thắng lần đầu trong tuần Pháo đài tuần 600 xu, chiến dịch của tuần 800 xu.

### Vòng xoay 26 tuần

Mỗi tuần một chiến dịch và hai mutator, chọn theo số tuần (ISO, UTC) nên mọi người cùng một tuần; các cặp loại trừ nhau không bao giờ đi cùng, mỗi mutator đều xuất hiện trong nửa năm, không cặp nào lặp lại.

Bảng 26 dòng: số liệu đầy đủ ở các sheet của mục này trong file xlsx cùng tên.

Sheet 04_che_do_kinh_te_ai/Tac_chien_bac — Tác chiến: bậc (4 dòng, 7 cột)

| id | enemy | player_income | score | supports |
|---|---|---|---|---|
| heroic | 1.3 | 1.0 | 1.3 | TRUE |
| iron | 1.3 | 0.8 | 1.6 | FALSE |
| legend | 1.6 | 0.75 | 2.0 | FALSE |
| normal | 1.0 | 1.0 | 1.0 | TRUE |

Sheet 04_che_do_kinh_te_ai/Diem_tac_chien — Điểm Tác chiến (8 dòng, 8 cột)

| id | khoa | gia_tri_so |
|---|---|---|
| score.hq | hq | 2000 |
| score.losses | losses | 2000 |
| score.lossesAtZeroCp | lossesAtZeroCp | 150 |
| score.par | par | 1500 |
| score.time | time | 3000 |
| score.win | win | 5000 |
| weekly.fortress | fortress | 600 |
| weekly.operation | operation | 800 |

Sheet 04_che_do_kinh_te_ai/Mutator — Mutator (20 dòng, 28 cột)

| id | excludes | both_damage | both_hp | empty_base | enemy_air | enemy_cp | enemy_hp | enemy_income | extra_boss |
|---|---|---|---|---|---|---|---|---|---|
| armour_only | light_deck;enemy_air |  |  |  |  |  |  |  |  |
| empty_base | towers_x2 |  |  | TRUE |  |  |  |  |  |
| enemy_air | no_air;armour_only;light_deck |  |  |  | TRUE |  |  |  |  |
| fleet |  |  |  |  |  |  |  | 1.1 |  |
| general_boost | veterans |  |  |  |  | 1.5 |  | 1.3 |  |
| glass_cannon |  | 1.5 | 0.75 |  |  |  |  |  |  |
| iron_rain |  |  |  |  |  |  |  |  |  |
| lean_logistics |  |  |  |  |  |  |  |  |  |
| light_deck | armour_only |  |  |  |  |  |  |  |  |
| night_ops | storm |  |  |  |  |  |  |  |  |
| no_air | enemy_air |  |  |  |  |  |  |  |  |
| no_repair |  |  |  |  |  |  |  |  |  |
| no_support |  |  |  |  |  |  |  |  |  |
| sea_storm | storm |  |  |  |  |  |  |  |  |
| storm |  |  |  |  |  |  |  |  |  |
| swarm |  |  |  |  |  |  |  |  |  |
| time_attack | two_bosses |  |  |  |  |  |  |  |  |
| towers_x2 |  |  |  |  |  |  |  |  |  |
| two_bosses | time_attack |  |  |  |  |  |  |  | TRUE |
| veterans | general_boost |  |  |  |  |  | 1.25 |  |  |

*In 10 / 28 cột; 16 cột khác: xem sheet.*

Sheet 04_che_do_kinh_te_ai/Mutator_tuan — Mutator tuần (1 dòng, 5 cột)

| id | trang_thai | ghi_chu |
|---|---|---|
| can_doc_ma | XEM_05 | dữ liệu ở 04_che_do_kinh_te_ai/Mutator (operations.json); c… |

## Kinh tế

### Trong trận

**CP (điểm chỉ huy):** khởi đầu thường 12–34 CP tùy chế độ, thu nhập ~1 CP/giây × hệ số chung 0.9, +0.25 CP/giây cho mỗi cứ điểm giữ được, kho tối đa 30 CP. **Tiếp tế:** quân vượt mức tiếp tế (24 CP × 1.05) thì thu nhập giảm (tối đa −75%). **Hạ địch:** hoàn 25% giá xe bị hạ cho phe hạ. **Bắt kịp:** phe bị áp đảo được tăng thu nhập tới +50%. **Giới hạn:** 32 xe, 6 máy bay. Xe mua được thả dù sau 3,5 giây.

### Ngoài trận (một loại tiền: xu)

Thưởng trận nhanh: thắng 120 / hòa 70 / thua 40 xu + 1,5 xu mỗi xe hạ (tối đa 120) + 4 xu mỗi phút (tối đa 15), × hệ số độ khó; XP = 80% xu. Sinh tồn/Vô tận: 30 + 18 × số đợt + 1,5 × số xe hạ. Nhiệm vụ: thưởng theo sao và cấp độ. Thử thách hằng ngày 3 nhiệm vụ.

### Thu nhập theo chế độ (vòng 6: tăng vừa phải 12–26%)

Hệ số chung: thu nhập 0,85 → **0,95**, tiếp tế 0,9 → **1,05** (nhiều xe trên sân hơn khoảng 12%). Tham khảo: elixir của Clash Royale (tăng x2/x3 cuối trận), Potential của Arknights (giảm giá nhỏ theo bậc, có trần), Boss Rush của BTD6 (thưởng khi gây sát thương cho boss). Tiêm kích 12 → 10 CP, cường kích 13 CP, xe rùa 8 CP; pháo phòng không của boss 27 → 21 sát thương/viên; máy bay VTOL không dừng lơ lửng trong tầm pháo phòng không; AI không mua tiêm kích khi địch không có máy bay.

### Hạng thẻ

Từ hạng 7 thẻ rẻ hơn 5%, từ hạng 9 rẻ hơn 10% khi gọi (làm tròn CP nguyên, thẻ ≤ 5 CP không đổi). Giá trị quân, phí tiếp tế và tiền hoàn khi bị hạ vẫn tính theo giá gốc.

### Hòm đồ

Giữ nguyên mua bằng xu (quyết định của chủ dự án). Có cơ chế bảo hiểm (pity) cho Sử thi/Huyền thoại, tỷ lệ công khai trong game.

Sheet 04_che_do_kinh_te_ai/Kinh_te — Kinh tế (18 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so | gia_tri_chu |
|---|---|---|---|---|
| campaign.economy.payScale["2"] | economy | 2 | 1.66 |  |
| campaign.economy.payScale["3"] | economy | 3 | 1.0 |  |
| economy.armyCap.Campaign | economy | Campaign | 24 |  |
| economy.armyCap.Survival | economy | Survival | 30 |  |
| economy.armyCap.default | economy | default | 40 |  |
| economy.enemyScaling | economy | enemyScaling | 0.55 |  |
| economy.enemyScalingModes.Weekly | economy | Weekly | 0.5 |  |
| economy.income | economy | income | 0.9 |  |
| economy.startCp.modes | economy | modes |  | Conquest;Deathmatch;KingOfTheHill;Assault;Siege;Weekly;Defe… |
| economy.startCp.scale | economy | scale | 1.16 |  |
| economy.supply | economy | supply | 1.05 |  |
| economy.vehicleCap.Defend | economy | Defend | 48 |  |
| economy.vehicleCap.Endless | economy | Endless | 48 |  |
| economy.vehicleCap.Operation | economy | Operation | 48 |  |
| economy.vehicleCap.Siege | economy | Siege | 48 |  |
| economy.vehicleCap.default | economy | default | 32 |  |
| ma.hoan_cp_khi_ha | ma | hoàn CP khi hạ, bắt kịp, thưởng rút lui, thưởng bộ phận bos… |  | kill_share 0.25; tran_hoan_khi_ha 0.45; tran_hoan_khi_mat 0… |
| ma.tiep_te_cong_thuc | ma | tiếp tế: công thức, ngưỡng, đường phạt, tối đa -75 % |  | armyCap = round((economy.armyCap[mode] x supplyPriceScale +… |

Sheet 04_che_do_kinh_te_ai/Nang_hang — Giá nâng hạng (10 dòng, 6 cột)

| id | hang | xu | ban_thiet_ke |
|---|---|---|---|
| 1 | 1 | 0 | 0 |
| 2 | 2 | 50 | 2 |
| 3 | 3 | 100 | 4 |
| 4 | 4 | 200 | 8 |
| 5 | 5 | 400 | 12 |
| 6 | 6 | 700 | 20 |
| 7 | 7 | 1200 | 30 |
| 8 | 8 | 2000 | 45 |
| 9 | 9 | 3200 | 65 |
| 10 | 10 | 5000 | 90 |

Sheet 04_che_do_kinh_te_ai/Hom_do — Hòm đồ và tỷ lệ rơi (4 dòng, 18 cột)

| id | bac_hom | ty_le_0 | ty_le_1 | ty_le_2 | ty_le_3 | ty_le_4 | rolls | coins_low | coins_high |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 0.7 | 0.25 | 0.045 | 0.005 | 0 | 1 | 60 | 120 |
| 1 | 1 | 0.5 | 0.35 | 0.12 | 0.028 | 0.002 | 2 | 250 | 350 |
| 2 | 2 | 0.2 | 0.42 | 0.28 | 0.085 | 0.015 | 4 | 800 | 1000 |
| 3 | 3 | 0 | 0.25 | 0.45 | 0.24 | 0.06 | 6 | 2000 | 2500 |

*In 10 / 18 cột; 6 cột khác: xem sheet.*

Sheet 04_che_do_kinh_te_ai/Cua_hang — Cửa hàng (6 dòng, 6 cột)

| id | id_goi | xu | gia_hien_thi |
|---|---|---|---|
| coins_1200 | coins_1200 | 1200 | $0.99 |
| coins_7000 | coins_7000 | 7000 | $4.99 |
| coins_15000 | coins_15000 | 15000 | $9.99 |
| coins_32000 | coins_32000 | 32000 | $19.99 |
| coins_85000 | coins_85000 | 85000 | $49.99 |
| coins_180000 | coins_180000 | 180000 | $99.99 |

Sheet 01_chien_dau/Doi_mo_man_luat — Đội mở màn: luật (3 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so | gia_tri_chu |
|---|---|---|---|---|
| enemyModes | openingSquads | enemyModes |  | Conquest;Deathmatch;KingOfTheHill;Assault;Siege;Showdown |
| modes | openingSquads | modes |  | Conquest;Deathmatch;KingOfTheHill;Assault;Siege;Defend;Endl… |
| share | openingSquads | share | 0.6 |  |

Bảng đầy đủ: xem sheet `Doi_mo_man` (23 dòng).

## AI và hệ thống

- **Chỉ huy AI** (cho cả hai phe): chọn mục tiêu, tập hợp quân rồi tiến theo nhóm, giữ/chiếm cứ điểm, gọi hỏa lực vào cụm địch (không vào quân mình), mua quân khắc chế (địch nhiều máy bay → mua phòng không, nhiều giáp → mua diệt tăng...).
- **Giao thông:** bản đồ làn đường (đường, lộ trình chính, lối hẹp, cổng), cấm đỗ ở cổng/lối hẹp, xe đang đỗ nhường đường theo ưu tiên, nhóm cùng đích không bắt nhau nhường, luân phiên qua cổng, tìm đường vòng có tính chi phí khi bị kẹt.
- Đã sửa tận gốc: đích luôn quy về vùng xe tới được (không tìm đường tới túi kín hay sau cổng đóng), ô đội hình ở cùng phía tường và không chéo nhau, hai xe đối đầu ngoài bãi trống thì một xe tránh sang bên, lách xe không lao vào tường, đường đi qua chỗ vừa bị chặn (tháp mới dựng) được tính lại ngay, tháp hạ xuống đẩy xe ra khỏi chân tháp, xe pháo đài canh giữ xuất hiện ở chỗ rộng. Pháo đài: cửa phụ và cổng mở của thành trong là cổng đôi 18 m, sân sau cổng để trống, và mọi bãi thả, cổng, mục tiêu có đường rộng 3 ô cho xe lớn nhất khi mọi cổng đóng và mọi ô hardpoint đầy tháp lớn nhất (công cụ dựng map tự bỏ vật cản; Tools/maps/check_access.py kiểm tra mọi map). Lưới an toàn: sau 10 giây xe kẹt được đặt ra chỗ trống, hoặc tạm đi xuyên xe phe mình, hoặc nhích lên theo đường; mỗi lần đều ghi vào báo cáo.
- **Chiến đấu:** giáp có hướng, tầm tối thiểu cho pháo, đạn xuyên (railgun), laser, tên lửa dẫn đường, pháo sáng, APS, tàng hình, EMP, khói, mìn, xe tự sát, drone, rơi máy bay gây sát thương, xác xe cháy.
- **Trang bị trong trận:** 42 dòng unique móc vào các sự kiện bắn, trúng, hạ, chết, đứng yên, đổi mục tiêu; hệ thống trạng thái (cháy, chậm, xé giáp, đánh dấu, khiên); hiện chữ nhỏ trên xe khi kích hoạt.
- **Chiến dịch:** địch scale theo kho vũ khí người chơi, chi viện bằng dù, dấu mục tiêu trên chiến trường và bản đồ nhỏ.
- **Nhịp bắn (vòng 6):** các vũ khí của một xe không bao giờ bắn cùng lúc: súng máy nghỉ quanh mỗi phát pháo/tên lửa và mỗi loạt, hai súng máy thay phiên, vũ khí nặng đã ngắm được ưu tiên. Súng (trừ súng máy, pháo phòng không) bắn chậm hơn 30% và mạnh hơn tương ứng (giữ nguyên DPS). Pháo phòng không bắn loạt 8–16 viên (16–25 viên/giây) rồi nghỉ. Xe tăng hết mục tiêu mặt đất thì dùng súng máy đồng trục bắn máy bay. Railgun nạp năng lượng 0,9 giây rồi bắn xuyên hàng.
- **Đạn và vụ nổ:** 35 mô hình đạn riêng (TOW, Kornet, Ataka, Hellfire, Stinger, Igla, Pantsir, AIM-9, R-60, AIM-120, Patriot, Buk, Maverick, JASSM, Hydra, S-8, Grad, GMLRS, TOS, Mk 84, FAB, GBU-12, JDAM, Lancet, Shahed, đạn xuyên, đạn nổ lõm, đạn pháo 155, đạn cối, đạn railgun); tên lửa rời bệ chậm rồi tăng tốc (1–1,5 giây cho phát bắn 40–60 m). Vụ nổ theo loại: đạn xuyên tóe lửa, đạn lõm chớp sáng, đạn nổ tung đất và khói đen, nhiệt áp bùng quả cầu lửa thứ hai, bom có vòng sóng xung kích và cột bụi; boss nổ nhiều đợt rồi lóe trắng toàn màn hình.
- **Âm thanh:** nhạc nền tự sáng tác bằng script (Tools/music: MIDI + FluidSynth + SoundFont FluidR3 giấy phép MIT, không dùng AI): menu, 3 bản trận đấu, công thành, boss, thắng, thua; có mức âm lượng nhạc riêng. Clip Xem bắn có tiếng súng.
- **Bản đồ nhỏ:** hiện mọi xe địch (ngoài tầm nhìn thì mờ), boss là vòng đỏ nhấp nháy.
- **LOD:** xe nhỏ trên màn hình dùng mô hình đơn giản hóa (31% tam giác, 3,6 lượt vẽ thay vì 22), rất nhỏ thì thành thẻ impostor chiếu sáng lại; 100 xe trong khung: 741 nghìn → 255 nghìn tam giác.
- **Kiểm thử:** xem phần 17.
- **Đồ họa:** URP, mức Thấp/Vừa/Cao/Tùy chỉnh; Cao có shadow map 4096, bóng mềm, MSAA 4x và model chi tiết cho 12 xe phổ biến nhất.

Sheet 04_che_do_kinh_te_ai/Chien_thuat — Chiến thuật (16 dòng, 41 cột)

| id | counters | countered_by | prefer | commanders | chapter | check_with | cp | interlude | modules_artillery_prep |
|---|---|---|---|---|---|---|---|---|---|
| air_superiority | hit_and_run | blitz | fighter_jet;stealth_fighter;sam_launcher;long_sam;heavy_aa | reyes | 3 | sead | 0.15;0.12;0.08;0.08;0.2;0.1;0.22;0.05 | 0 |  |
| all_out | depth | blitz | main_battle_tank;heavy_tank;attack_jet;heavy_bomber | okoye | 10 | breakthrough | 0.3;0.2;0.1;0.1;0.1;0.08;0.07;0.05 | 0 |  |
| ambush | blitz | bounding | tank_destroyer;railgun_truck;fpv_carrier;scout_jeep;ew_jamm… | kerr | 0 |  | 0.15;0.15;0.3;0.1;0.12;0.08;0.02;0.08 | 1 |  |
| attrition | breakthrough | blitz;encircle | mlrs;shahed_truck;ballistic_launcher;recon_drone | quist | 8 |  | 0.1;0.1;0.2;0.3;0.1;0.05;0.05;0.1 | 0 |  |
| balanced |  |  |  | kade | 0 |  | 0.25;0.2;0.12;0.12;0.1;0.08;0.05;0.08 | 0 |  |
| base_defence | blitz | firepower;attrition | tank_destroyer;aa_vehicle;mine_layer;engineer_vehicle | brandt | 1 |  | 0.25;0.15;0.2;0.15;0.15;0.02;0.0;0.08 | 0 |  |
| blitz | firepower | depth;ambush | armored_car;ifv;wheeled_gun;main_battle_tank;attack_helicop… | mendez | 2 |  | 0.25;0.3;0.1;0.05;0.08;0.1;0.04;0.08 | 0 |  |
| bounding | ambush | blitz;firepower | main_battle_tank;ifv | kade | 3 |  | 0.3;0.25;0.12;0.1;0.1;0.05;0.0;0.08 | 0 |  |
| breakthrough | depth;encircle | encircle;dispersal | heavy_tank;titan_tank;twin_tank;armored_bulldozer;engineer_… | reyn | 6 | all_out | 0.4;0.15;0.08;0.12;0.1;0.05;0.02;0.08 | 0 |  |
| decapitation | firepower | depth | armored_car;scout_heli;attack_helicopter;stealth_fighter | kerr | 9 |  | 0.12;0.28;0.15;0.1;0.08;0.15;0.07;0.05 | 0 |  |
| depth | blitz;breakthrough | firepower;encircle | tank_destroyer;main_battle_tank;mine_layer;mortar_carrier;s… | brandt | 1 |  | 0.25;0.15;0.18;0.15;0.12;0.05;0.02;0.08 | 0 |  |
| dispersal | firepower;breakthrough | blitz | armored_car;light_tank;fpv_carrier;mortar_carrier | venn | 6 | hit_and_run | 0.15;0.25;0.15;0.15;0.1;0.1;0.03;0.07 | 0 |  |
| encircle | depth;base_defence | breakthrough | armored_car;ifv;wheeled_gun;light_tank;attack_helicopter | adler | 4 |  | 0.22;0.28;0.15;0.08;0.1;0.1;0.02;0.05 | 0 |  |
| firepower | depth;base_defence | blitz;hit_and_run;dispersal | artillery;mlrs;heavy_rocket_artillery;mortar_carrier;ammo_c… | dahl | 3 |  | 0.2;0.12;0.08;0.3;0.12;0.05;0.05;0.08 | 0 | 1.0 |
| hit_and_run | firepower | blitz;air_superiority | wheeled_gun;armored_car;tank_destroyer;attack_helicopter;st… | mendez | 5 | dispersal | 0.1;0.25;0.25;0.1;0.1;0.12;0.03;0.05 | 0 |  |
| sead |  |  | attack_jet;stealth_fighter;ew_jammer;ballistic_launcher | reyes | 7 | air_superiority | 0.15;0.12;0.1;0.15;0.1;0.1;0.2;0.08 | 0 |  |

*In 10 / 41 cột; 28 cột khác: xem sheet.*

Sheet 04_che_do_kinh_te_ai/AI_ho_so_che_do — Hồ sơ AI theo chế độ (20 dòng, 33 cột)

| id | tactics | advance | auto_ai | auto_ai_note | controllers | defender | engagement | escort_anchor | escort_max_advance_distance |
|---|---|---|---|---|---|---|---|---|---|
| assault | depth;base_defence;attrition;ambush;balanced | FALSE |  | Khu kế tiếp, quỹ thời gian | Commander;Static | ai | Normal |  |  |
| bossrush |  | FALSE |  | 1) né cảnh báo chết người 2) bộ phận boss nguy hiểm 3) bộ p… | Boss | none | Normal |  |  |
| capture | * | TRUE |  | Mục tiêu màn | Commander | none | Normal |  |  |
| conquest | * | TRUE |  | Giữ cứ điểm đang mất nhanh nhất | Commander | none | Normal |  |  |
| deathmatch | * | TRUE |  | Dồn hỏa lực, tránh biếu xe đắt | Commander | none | Normal |  |  |
| defend |  | FALSE |  | Giữ tuyến, lùi tuyến có trật tự | WaveDirector | player | Normal |  |  |
| escort | * | TRUE | escort | Ở quanh đoàn xe; mối đe dọa với đoàn trước; hỗ trợ không gọ… | Commander | none | Normal | convoyCentre | 30 |
| fixed_deck | * | FALSE |  | Theo special_rules; placed_allies theo lệnh Tấn công/Phòng… |  | none | Normal |  |  |
| hill | * | TRUE |  | Giữ đồi | Commander | none | Normal |  |  |
| hold | * | TRUE |  | Giữ mục tiêu | Commander | player | Normal |  |  |
| hunt | * | TRUE |  | Như cột trước | Commander | none | Normal |  |  |
| operation | * | TRUE |  | Mục tiêu giai đoạn | Commander;WaveDirector;Fortress;Boss;Static | none | Normal |  |  |
| outpost | * | TRUE |  | Theo bước | Commander | none | Normal |  |  |
| protect | * | TRUE | protectTarget | Mối đe dọa trực tiếp lớn nhất với công trình được bảo vệ (k… | Commander | player | Normal |  |  |
| recon | ambush;base_defence | FALSE |  | engagementPolicy = AVOID_UNLESS_BLOCKING; không đuổi; ưu ti… | Commander | none | AvoidUnlessBlocking |  |  |
| relieve | * | TRUE | breakSiege | Phá vòng vây → bảo vệ quân được giải vây → rồi mới đuổi | Commander | none | Normal |  |  |
| shootdown | * | TRUE |  | Giữ mạng phòng không và vùng phủ; không đuổi mục tiêu mặt đ… | Commander | none | Normal |  |  |
| showdown | * | TRUE |  | Thủ nhà, phá tuyến ngoài, đánh nhà chính | Commander | none | Normal |  |  |
| siege | depth;base_defence;attrition;ambush;balanced | FALSE |  | Mục tiêu giai đoạn; né vùng siêu pháo | WaveDirector;Fortress | ai | Normal |  |  |
| survival |  | FALSE |  | Giữ bãi thả; chặn mối đe dọa gần; không đuổi xa | WaveDirector;Boss | player | Normal |  |  |

*In 10 / 33 cột; 21 cột khác: xem sheet.*

Sheet 04_che_do_kinh_te_ai/AI_trang_thai — Trạng thái đội (7 dòng, 5 cột)

| id | commit | priority |
|---|---|---|
| APPROACH | 3.0 | 2 |
| COMBAT | 4.0 | 3 |
| FLANK | 6.0 | 2 |
| HOLD | 5.0 | 2 |
| OVERWATCH | 4.0 | 2 |
| REGROUP | 3.0 | 3 |
| TRAVEL | 4.0 | 1 |

Bảng đầy đủ: xem sheet `AI_tham_so` (49 dòng), `AI_vai_tro` (28 dòng).

## Giao diện

Phong cách **Field Command 2.0** (phase 10): nền xám thép phẳng, viền 1 px, góc vuông, một màu nhấn cam cho hành động chính (góc vát), chữ Barlow / Barlow Condensed (đủ dấu tiếng Việt). Mọi màn dựng trên một bộ token màu và chữ chung và một thư viện thành phần (nút, thẻ, tab, ô chọn, công tắc, thanh chỉ số, hộp thoại, thông báo). Điều hướng 5 mục bên trái: Trang chủ, Chiến dịch, Tác chiến, Quân đội, Cửa hàng; thanh trên cùng có cấp, kinh nghiệm, xu và cài đặt. Ảnh thẻ render từ mô hình 3D thật. Mỗi màn được kiểm tra tự động ở 4 tỉ lệ màn hình (16:9, 19,5:9 tai thỏ, 20:9 đục lỗ, 4:3) và cỡ chữ Lớn: không chữ bị cắt, không thành phần chồng nhau, vùng chạm đủ lớn. Tên gọi tiếng Việt thống nhất (mỗi bản đồ một tên, xu, ngụy trang, rốc-két, la-de).

Mọi xe, tháp, công trình, thẻ hỗ trợ và vật phẩm có tên ngắn (tối đa khoảng 14 ký tự) dùng ở chỗ chật; mọi thẻ có vùng tên cao cố định 2 dòng nên ảnh, CP và cấp luôn thẳng hàng. Khiên vẽ lại bằng một shader.

Màn Căn cứ là ảnh chụp thật từ trên xuống của trại trên từng bản đồ, mũi tên đỏ là hướng địch tới, ô tháp đúng vị trí thật với cỡ 1 / 1,4 / 2, ô tiện ích hình lục giác; phủ tầm bắn (mặt đất cam, trên không xanh nhạt), chụm hai ngón để phóng to. Một bố trí chính áp cho cả 20 bản đồ theo vị trí (cổng, vòng ngoài, vòng trong, cạnh SCH, phía sau), bản đồ nào cần thì chỉnh riêng; 3 bộ căn cứ; tự xếp theo cách AI địch xếp. Sức mạnh căn cứ là đúng con số dùng để tính độ mạnh các đợt địch. Tiền đồn có tab riêng. Mỗi tháp có icon riêng.

### Biểu tượng giáp và vũ khí

Bộ biểu tượng vẽ mới hoàn toàn theo nét của Field Command 2.0, không dùng số và không dựa vào màu: 57 hình, không hình nào trùng hình khác (test so dữ liệu nét). **Giáp** 5 cấp đầy dần như pin: nét đứt (không giáp), viền mảnh, viền đôi, tô nửa dưới, tô kín có đinh tán; máy bay là khiên có cánh, tháp và công trình là khiên vân gạch. **Dạng vũ khí** 30 hình theo dạng đạn thật, với đạn động năng hình cho biết độ xuyên (viên tròn, viên đạn, đạn có đai, mũi tên xuyên, mũi tên đầu kép, mũi tên có vòng điện). **Dấu loại sát thương** ở góc chip: nón lõm có tia, hình nổ, ngọn lửa, chùm chấm, tia sáng; nhiệt áp có dấu riêng; động năng không có dấu. **Dấu phụ** (chỉ ở màn chi tiết và tooltip): đánh nóc, dẫn đường, nổ lan. Cỡ nhỏ nhất 34 px = 18,7 pt. Hiện ở: hàng dưới mọi thẻ xe, tháp và công trình (giáp mặt trước và 2 chip, "+N" nếu còn; thẻ gọn 1 chip), khay căn cứ và tiền đồn, màn chi tiết (sơ đồ giáp theo hướng, chip ở tab Vũ khí, bảng hiệu quả, dòng Mạnh với / Yếu trước tạo từ dữ liệu), giữ thẻ trong trận, dải xe đang chọn, tooltip khi chạm địch (✓ ~ ✕ cho từng xe trong bộ bài), bộ phận trùm, hàng 5 khiên ở độ phủ bộ bài và căn cứ, trang chú thích kèm bảng khắc chế. Cài đặt "Hiện số chi tiết" (mặc định tắt) thêm cấp và hệ số vào tooltip.

### Mép bản đồ

![Đường ranh giới và cảnh ngoài viền.](images/04_che_do_kinh_te_ai_shots_edge.png)

*Hình: Đường ranh giới và cảnh ngoài viền. Đơn vị: ảnh chụp trong game, không lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (07_hinh_anh_am_thanh_model/Model).*

Sheet 04_che_do_kinh_te_ai/Skin — Skin (10 dòng, 11 cột)

| id | base_hex | metallic | pattern | price | roughness | scale | second_hex | third_hex |
|---|---|---|---|---|---|---|---|---|
| arctic | #e4e9ec |  | Blotches | 900 |  | 0.34 | #b4bec5 | #7b8790 |
| desert | #c7a46a |  | Blotches | 500 |  | 0.32 | #9a7646 | #6f5535 |
| gold | #d5a63c | 0.92 | Plain | 6000 | 0.26 | 0.35 | #b8872a | #f0cd6c |
| midnight | #272b31 | 0.35 | Digital | 3000 | 0.35 | 0.6 | #3b4550 | #4fd7ff |
| ocean | #4b6b8c |  | Digital | 1500 |  | 0.55 | #2c435e | #8aa7c4 |
| olive | #7a9654 |  | Plain | 0 |  |  | #7a9654 | #7a9654 |
| steel | #b3bcc3 | 0.9 | Plain | 4500 | 0.24 | 0.35 | #8c969e | #d7dde2 |
| tiger | #d9832c |  | Stripes | 2500 |  | 0.5 | #1e1b18 | #d9832c |
| urban | #8b9197 |  | Digital | 1200 |  | 0.55 | #5a6066 | #b9bdc1 |
| woodland | #617540 |  | Blotches | 800 |  | 0.36 | #3c4a29 | #6d5436 |

Sheet 04_che_do_kinh_te_ai/Nhiem_vu_ngay — Nhiệm vụ ngày (8 dòng, 6 cột)

| id | loai | muc_tieu | thuong_xu |
|---|---|---|---|
| bosses | bosses | 1;1;2 | 250 |
| buildings | buildings | 12;20;30 | 120 |
| captures | captures | 4;8;12 | 130 |
| elites | elites | 3;5;8 | 160 |
| items | items | 1;2;3 | 100 |
| kills | kills | 40;60;90 | 150 |
| strikes | strikes | 6;10;15 | 120 |
| wins | wins | 1;2;3 | 180 |

Bảng đầy đủ: xem sheet `Cai_dat_mac_dinh` (22 dòng), `Huong_dan` (316 dòng, bulk.zip), `Ban_do_menu` (25 dòng), `Mo_khoa` (88 dòng).

## Tham khảo ngoài đời và game

Thông số ngoài đời lấy từ nguồn trong repo (sheet Nguon_tham_chieu của 08_tham_chieu); chỗ chưa có nguồn ghi NEED_SOURCE, không điền từ trí nhớ.

### Che_do_tham_chieu

12 dòng. Độ tin cậy: da_kiem_chung 0, uoc_dinh 0, ban_dau_doan 1, NEED_SOURCE 11. Loại: NEED_SOURCE 11, game 1.

- `conquest` (Conquest): game: Company of Heroes; độ tin: ban_dau_doan; nguồn: R_decisions.

### AI_tham_chieu

56 dòng. Độ tin cậy: da_kiem_chung 14, uoc_dinh 0, ban_dau_doan 30, NEED_SOURCE 12. Loại: NEED_SOURCE 12, hoc_thuyet_quan_su 44.

- `chien_thuat/air_superiority` (Ưu thế trên không): học thuyết: Ưu thế trên không; game: Hearts of Iron IV;Ace Combat; giống: Tạo cửa sổ trên không rồi mới đưa đội mặt đất; khác có chủ đích: Tướng AI mua tiêm kích và phòng không trước; đội mặt đất chờ tới khi máy bay địch bị hạ h…; độ tin: da_kiem_chung; nguồn: R_machine_brigade_ai_research, D_hearts_of_iron_iv_land_doctrine.
- `chien_thuat/all_out` (Tổng tấn công): học thuyết: Tập trung lực lượng, đòn quyết định; game: StarCraft; giống: Để dành rồi tung một đợt lớn cùng lúc; khác có chủ đích: Tướng AI để dành CP tới ngưỡng rồi mua cả đợt; mọi đội cùng tấn công; thẻ hỗ trợ dồn cùng…; độ tin: ban_dau_doan; nguồn: R_machine_brigade_ai_research.
- `chien_thuat/ambush` (Phục kích): học thuyết: Phục kích, giữ lửa; game: Command: Modern Operations;Company of Heroes; giống: Ẩn và kỷ luật hỏa lực, phát đầu đồng loạt; khác có chủ đích: Đội dừng ở chỗ có vật che; giữ lửa tới khi địch vào ~60% tầm hoặc bị phát hiện; phát đầu…; độ tin: da_kiem_chung; nguồn: R_machine_brigade_ai_research, D_command_modern_operations_weapon_release_aut.
- `chien_thuat/attrition` (Tiêu hao): học thuyết: Chiến tranh tiêu hao; game: Hearts of Iron IV; giống: Đổi lãnh thổ lấy thời gian, quấy rối từ xa; khác có chủ đích: Ngưỡng tấn công 1,5 lần; ưu tiên vũ khí tầm xa và giữ khoảng cách; độ tin: da_kiem_chung; nguồn: R_machine_brigade_ai_research, D_hearts_of_iron_iv_land_doctrine.
- `chien_thuat/balanced` (Cân bằng): học thuyết: Vũ khí phối hợp (combined arms); giống: Phối hợp nhiều vai trò, không thiên lệch; khác có chủ đích: Không đổi tham số; độ tin: ban_dau_doan; nguồn: R_machine_brigade_ai_research.
- `chien_thuat/base_defence` (Bảo vệ căn cứ): học thuyết: Phòng thủ cố định; game: Tower defense;C&C; giống: Giữ quanh căn cứ và tháp; khác có chủ đích: Đội giữ trong vùng căn cứ; tháp ưu tiên chế độ Đầu đoàn; mua quân phòng thủ; độ tin: ban_dau_doan; nguồn: R_machine_brigade_ai_research.
- `chien_thuat/blitz` (Tấn công chớp nhoáng): học thuyết: Chiến tranh cơ động; game: Hearts of Iron IV; giống: Giữ đà tiến, đánh trước khi địch kịp dựng phòng tuyến; khác có chủ đích: Ngưỡng tấn công 1,2 → 0,9 lần sức mạnh địch; đội không chờ xe chậm; xe nhanh được ưu tiên…; độ tin: da_kiem_chung; nguồn: R_machine_brigade_ai_research, D_hearts_of_iron_iv_land_doctrine.
- `chien_thuat/bounding` (Yểm hộ luân phiên): học thuyết: Bounding overwatch; game: Steel Beasts;ArmA; giống: Tiến chậm, an toàn, một nhóm luôn yểm hộ; khác có chủ đích: Đội chia 2 nhóm; nhóm tiến không vượt quá tầm yểm hộ của nhóm dừng; tốc độ tiến giảm ~30%; độ tin: da_kiem_chung; nguồn: R_machine_brigade_ai_research, W_bounding_overwatch.
- `chien_thuat/breakthrough` (Tập trung đột phá): học thuyết: Schwerpunkt (điểm trọng tâm); game: Hearts of Iron IV;Total War; giống: Dồn gần hết quân vào một điểm để chọc thủng; khác có chủ đích: Tướng AI dồn ≥ 70% quân vào một hướng; xe hạng nặng đi đầu; bỏ giữ các điểm phụ; độ tin: da_kiem_chung; nguồn: R_machine_brigade_ai_research, D_hearts_of_iron_iv_land_doctrine.
- `chien_thuat/decapitation` (Săn đầu): học thuyết: Đánh vào chỉ huy và hậu cần (decapitation); game: Company of Heroes;WARNO; giống: Đánh sâu vào hỗ trợ, pháo, chỉ huy; khác có chủ đích: Ưu tiên mục tiêu: xe hỗ trợ, pháo, xe chỉ huy, radar; đội đánh sườn sâu; độ tin: ban_dau_doan; nguồn: R_machine_brigade_ai_research.
- `chien_thuat/depth` (Phòng thủ chiều sâu): học thuyết: Phòng thủ đàn hồi (elastic defense); game: Hearts of Iron IV; giống: Hấp thụ đợt tấn công qua nhiều tuyến, rồi phản công; khác có chủ đích: Đội giữ điểm gần tháp; khi tuyến trước thất thủ (sức mạnh ta dưới 0,6 lần địch trong vùng…; độ tin: da_kiem_chung; nguồn: R_machine_brigade_ai_research, D_hearts_of_iron_iv_land_doctrine.
- `chien_thuat/dispersal` (Phân tán): học thuyết: Phân tán chống hỏa lực; game: Supreme Commander; giống: Dàn rộng để vô hiệu bắn lan và siêu vũ khí (tham khảo khác: chiến sự drone hiện đại); khác có chủ đích: Khoảng cách tối thiểu giữa xe ×2; giảm dồn hỏa lực; né cảnh báo sớm hơn; độ tin: ban_dau_doan; nguồn: R_machine_brigade_ai_research.
- `chien_thuat/encircle` (Bao vây): học thuyết: Gọng kìm, bao vây; game: Total War;Hearts of Iron IV; giống: Đánh hai hướng cùng lúc vào hông và sau; khác có chủ đích: Tướng AI chia 2–3 đội theo hai hướng; trọng số đánh sườn tăng; hẹn giờ cho các đội cùng c…; độ tin: da_kiem_chung; nguồn: R_machine_brigade_ai_research, D_hearts_of_iron_iv_land_doctrine.
- `chien_thuat/firepower` (Hỏa lực áp đảo): học thuyết: Hỏa lực vượt trội; game: Hearts of Iron IV; giống: Pháo dọn đường rồi mới tiến; khác có chủ đích: Tướng AI ưu tiên mua pháo binh; đội chờ 1 đợt pháo trước khi tiến; pháo được giao mục tiê…; độ tin: da_kiem_chung; nguồn: R_machine_brigade_ai_research, D_hearts_of_iron_iv_land_doctrine.
- `chien_thuat/hit_and_run` (Bắn và chạy): học thuyết: Kiting, giữ cự ly; game: StarCraft II; giống: Giữ cự ly tối đa, không để địch áp sát; khác có chủ đích: Khoảng cách giao chiến 90–100% tầm; lùi khi địch vào 70% tầm; ưu tiên mua xe nhanh bắn xa; độ tin: ban_dau_doan; nguồn: R_machine_brigade_ai_research.
- … 29 dòng có tham chiếu nữa: xem sheet AI_tham_chieu.

### Meta_tham_chieu

13 dòng. Độ tin cậy: da_kiem_chung 0, uoc_dinh 0, ban_dau_doan 0, NEED_SOURCE 13. Loại: NEED_SOURCE 13.

- Chưa dòng nào có tham chiếu trong repo.

Nguồn được dùng (tiêu đề như repo ghi; link khi repo có):

- `D_command_modern_operations_weapon_release_aut`: Command: Modern Operations · Weapon Release Authorization — <https://command.matrixgames.com/?p=3598> (độ tin 1)
- `D_hearts_of_iron_iv_land_doctrine`: Hearts of Iron IV · Land doctrine — <https://hoi4.paradoxwikis.com/Land_doctrine> (độ tin 3)
- `R_decisions`: Docs/DECISIONS.md (nhật ký quyết định) (độ tin 3)
- `R_machine_brigade_ai_research`: Nghiên cứu AI (Machine_Brigade_AI_Research.xlsx) (độ tin 3)
- `W_bounding_overwatch`: Bounding overwatch — <https://en.wikipedia.org/wiki/Bounding_overwatch> (độ tin 2)

## Các sheet của file

Mọi sheet, số dòng và ý nghĩa cột nằm trong 00_index.xlsx (Muc_luc_sheet, Schema). Sheet `input_<tên>` là bản chép của một sheet nguồn để công thức Excel đọc cùng file; sửa ở sheet nguồn, không sửa bản chép.

- `Che_do` (12 dòng): Chế độ — matchRules.modes: mỗi chế độ một dòng (luật thắng / thua, giờ, hiệp phụ, điểm, bắt kịp)
- `Sao_chien_dich` (15 dòng): Sao chiến dịch theo mục tiêu — matchRules.starMastery (sao thứ 2: làm chủ mục tiêu) và starThird (sao thứ 3) theo kiểu mục tiêu; starTime / starLosses của từng nhiệm vụ ở 05_chien_…
- `Vo_han` (6 dòng): Vô hạn và bảng xếp hạng — matchRules.leaderboards: thứ tự xếp hạng ('-' giảm dần, '+' tăng dần) của các chế độ vô hạn / tuần; hệ số tăng, boss xen kẽ, thưởng: luật chế độ ở Ch…
- `Kinh_te` (18 dòng): Kinh tế — balance.json economy (trừ bankByMode: ở Che_do) và campaign.json economy
- `Do_kho` (4 dòng): Độ khó — Mỗi độ khó một dòng: economy.enemyScalingQuick (hệ số địch trận nhanh) và campaign eventLibrary.rules.difficulty (biến cố theo độ khó); tham số AI th…
- `Diem_tac_chien` (8 dòng): Điểm Tác chiến — operations.json score (điểm thắng, giờ, máu HQ, tổn thất) và weekly
- `Tac_chien_bac` (4 dòng): Tác chiến: bậc — operations.json tiers: hệ số địch, thu nhập, điểm, thẻ hỗ trợ
- `Mutator` (20 dòng): Mutator — operations.json mutators: mỗi mutator một dòng (hệ số, cờ, loại trừ)
- `Che_do_thoi_luong` (12 dòng): Chế độ: thời lượng lý thuyết — Thời lượng lý thuyết mỗi chế độ ở độ khó Bình thường: giờ của dữ liệu (matchRules.numbers) và của mã (đồng hồ quỹ giờ, thưởng giai đoạn, trần quỹ), h…
- `Kinh_te_suy_ra` (44 dòng): Kinh tế suy ra — CP mỗi bên đã kiếm được (CP khởi đầu + thu nhập x thời gian) ở 25 / 50 / 75 / 100 % thời lượng tham chiếu (Che_do_thoi_luong), theo chế độ x độ khó;…
- `Kiem_tinh_che_do` (36 dòng): Kiểm tĩnh chế độ (4 sổ) — Bốn sổ của kiểm tĩnh chế độ (Tools/audit/mode_static_audit.py,) ở 25 / 50 / 75 / 100 % thời lượng mục tiêu, Bình thường: Kinh tế (CP khởi đầu + thu n…
- `Che_do_tham_chieu` (12 dòng): Chế độ: tham chiếu game — Mỗi chế độ một dòng: game tham khảo, cơ chế giữ / đổi (spec 12.2; chỉ dữ liệu có trong repo)
- `Chien_thuat` (16 dòng): Chiến thuật — aiBehaviour.tactics: 16 chiến thuật (tỷ lệ CP theo nhóm, ưu tiên, khắc chế, mở khóa theo chương, commander, mô-đun ghi đè tham số)
- `AI_ho_so_che_do` (20 dòng): Hồ sơ AI theo chế độ — aiModeProfiles.profiles: controllers, chiến thuật cho phép, chính sách mục tiêu, đứng yên, áp lực tiêu / tiến, hỗ trợ, leash, mặt nạ mục tiêu
- `AI_ho_so_pha` (5 dòng): Hồ sơ AI: ghi đè theo pha — aiModeProfiles.profiles.<hồ sơ>.phaseOverrides[]
- `AI_ho_so_anh_xa` (29 dòng): Hồ sơ AI: chế độ / mục tiêu -> hồ sơ — aiModeProfiles.modes (chế độ) và aiModeProfiles.goals (kiểu mục tiêu nhiệm vụ) -> hồ sơ
- `AI_tuong` (12 dòng): Tướng địch — Mỗi tướng một dòng: campaign.json generals (bộ bài, hỗ trợ, thế, phong cách), balance.json generals (elite ưa thích, bài thêm), aiBehaviour.generals…
- `AI_tham_so` (49 dòng): Tham số AI — balance.json ai.economy / ai.params / ai.world: giá trị, khoảng cho phép, chỉ số đo, lý do; danh sách bậc (escalation) một dòng mỗi bậc
- `AI_vai_tro` (28 dòng): Vai trò đơn vị — aiBehaviour.roles: ngưỡng giao chiến, phản ứng khi bị áp đảo
- `AI_don_vi` (50 dòng): Vai trò của từng đơn vị — aiBehaviour.units: đơn vị -> vai trò AI
- `AI_trang_thai` (7 dòng): Trạng thái đội — aiBehaviour.states: ưu tiên và thời gian cam kết mỗi trạng thái
- `AI_thap` (18 dòng): Hành vi tháp — aiBehaviour.towers: cách chọn mục tiêu mặc định và các cách đổi được
- `AI_boss` (11 dòng): Hành vi boss — aiBehaviour.bosses: kiểu hành vi của boss (ngăn ';')
- `AI_xung_dot` (348 dòng): AI: xung đột ghi đè — Mỗi chế độ / kiểu mục tiêu nhiệm vụ (AI_ho_so_anh_xa) x tướng (AI_tuong): chiến thuật tướng ưa thích, hồ sơ có dùng nó không, chiến thuật vào trận th…
- `AI_xung_dot_do_kho` (80 dòng): AI: độ khó x hồ sơ — Mỗi hồ sơ AI x độ khó: cách đổi chiến thuật giữa trận của độ khó (AiSkill.For: Never / WhenLosing / Counter) và việc hồ sơ chặn nó (không chiến thuật…
- `AI_tham_chieu` (56 dòng): AI: học thuyết và game tham khảo — Chiến thuật, vai trò AI, tướng địch: học thuyết quân sự (nghiên cứu AI), game AI tham khảo, kiểu chỉ huy (spec 12.2; chỉ dữ liệu có trong repo)
- `Nang_hang` (10 dòng): Giá nâng hạng — Arsenal.cs Coins / Prints: xu và bản thiết kế cho mỗi lần lên hạng (hạng 1-10)
- `Hom_do` (4 dòng): Hòm đồ và tỷ lệ rơi — Arsenal.cs: mỗi bậc hòm một dòng (số lượt, xu thấp / cao, số bản thiết kế, số thẻ, giá xu, bảo hiểm Sử thi / Huyền thoại, phần tháp, tỷ lệ theo độ hi…
- `Trang_bi_hang` (27 dòng): Trang bị theo độ hiếm — Arsenal.cs LevelCap / Top / Cap / GoldGuaranteed / LegendaryGuaranteed: mỗi chỉ số một dòng theo bảng nguồn (bang / chi_so)
- `Cua_hang` (6 dòng): Cửa hàng — Arsenal.cs Packs: gói xu (id, số xu, giá hiển thị)
- `Nhiem_vu_ngay` (8 dòng): Nhiệm vụ ngày — DailyMissions.cs Pool: loại, mục tiêu theo bậc (ngăn ';'), thưởng xu
- `Skin` (10 dòng): Skin — Skins.cs All: id, giá, màu
- `Ban_do_menu` (25 dòng): Bản đồ trên menu — MatchSettings.cs AllMaps: id, chủ đề, biểu tượng, thời tiết có thể
- `Meta_bang_hang` (112 dòng): Bảng hằng meta (C#) — Mọi bảng static readonly còn lại của các file meta (tự tìm): mỗi phần tử một dòng (bang = <file>#<mảng>)
- `Mo_khoa` (88 dòng): Mở khóa — Tools/campaign/unlocks_sheet.json: thẻ -> chương mở khóa; thẻ mở khi thắng nhiệm vụ: 05_chien_dich/Nhiem_vu.unlocks
- `Mo_khoa_chung` (3 dòng): Mở khóa: ghi chú — unlocks_sheet.json: khóa ngoài bảng
- `Meta_kinh_te_nguon` (23 dòng): Meta: nguồn và chỗ tiêu xu — Mỗi nguồn xu (thưởng trận, nhiệm vụ, hòm, nhiệm vụ ngày, Vô tận, cửa hàng) và chỗ tiêu xu (nâng hạng, hòm, skin): số xu, đơn vị, trần; số trong mã (R…
- `Meta_kinh_te_tran` (12 dòng): Meta: xu mỗi trận nhanh — Xu một trận nhanh theo độ khó x kết quả (Rewards.Quick: cơ bản + min(hạ, trần) x xu + min(phút, trần) x xu, x hệ số độ khó), ở trận tham chiếu 20 xe…
- `Meta_kinh_te` (10 dòng): Meta: kinh tế nâng hạng — Một thẻ từ hạng 1 lên hạng h: xu và bản thiết kế cho lần nâng, tổng từ hạng 1 (CardRanks.CoinsSpent / BlueprintsSpent), số trận thắng nhanh Bình thườ…
- `Huong_dan` [bulk.zip] (316 dòng): Hướng dẫn người chơi — Chuỗi hướng dẫn trong game: thẻ Hướng dẫn của trang chi tiết (guide.<id>: GuideText, BossText, BigAttackText...), mẹo (tip.*) và gợi ý thao tác (hint…
- `Cai_dat_mac_dinh` (22 dòng): Cài đặt mặc định — Cài đặt mặc định của người chơi mới (âm lượng, đồ họa, rung, hỗ trợ, ngôn ngữ), đọc từ mã bởi ExportGameDoc
- `Mutator_tuan` (1 dòng): Mutator tuần — Mutator tuần của Tác chiến
- `Thu_hang` (1 dòng): Thứ hạng — Bảng xếp hạng
- `Thuong` (1 dòng): Thưởng — Thưởng trận / chiến dịch
- `Meta_tham_chieu` (13 dòng): Meta: game tham khảo cơ chế — Mỗi cơ chế ngoài trận một dòng (theo sheet): game tham khảo (nâng hạng, hòm đồ, nhiệm vụ ngày...) (spec 12.2; chỉ dữ liệu có trong repo)
- `Hang_so_che_do` (71 dòng): Hằng số chế độ, tiếp tế và cờ chế độ — Assets/MachineBrigade/Resources/Data/tunables.json: 'modes' (lớp chủ → tên): một dòng một hằng số; mã game đọc qua SimTunables, giữ nguyên giá trị kh…
- `Hang_so_ai` (32 dòng): Hằng số AI — Assets/MachineBrigade/Resources/Data/tunables.json: 'ai' (lớp chủ → tên): một dòng một hằng số; mã game đọc qua SimTunables, giữ nguyên giá trị khi c…
