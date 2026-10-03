# 05_che_do_kinh_te — Chế độ và kinh tế

Bộ xuất dữ liệu Machine Brigade, commit 90337539, ngày 2026-10-03. Sinh bởi `python Tools/export/export.py` (lượt 6): bảng in đúng ô của csv / xlsx; văn bản lấy từ tài liệu thiết kế (Tools/docs) và chuỗi trong game. Toàn văn: Machine_Brigade_Design_FULL_2026-10-03.md.

Chế độ và luật trận, sao chiến dịch, bảng xếp hạng (vô hạn), Tác chiến (điểm, bậc, tuần, mutator), kinh tế, độ khó

Mục trong file này: 1. Tổng quan; 2. Chế độ chơi; 2b. Cân bằng chế độ và độ khó; 2c. Luật trận, phần vô hạn, trung lập, thoại và kết trận; 5. Tác chiến; 14. Kinh tế; 16b. Kiểm tĩnh chế độ.

## 1. Tổng quan

Trạng thái: Đã áp

Nguồn dữ liệu: (không có sheet; chỉ văn bản). Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §1. Tổng quan.

**Thể loại:** RTS / auto-battler trên điện thoại (màn ngang). Người chơi chỉ huy một binh đoàn phương tiện: xe tăng, xe bọc thép, pháo, phòng không, trực thăng, máy bay. Trận đấu phần lớn tự chạy: chỉ huy AI của người chơi tự mua quân (Tự mua) và tự gọi hỏa lực (Yểm trợ); người chơi can thiệp bằng lệnh Tấn công / Phòng thủ, chọn thẻ để triển khai, gọi hỏa lực vào điểm chọn.

**Vòng lặp:** điểm chỉ huy (CP) tăng theo thời gian và cứ điểm giữ được → mua phương tiện từ bộ bài (8 xe + 2 hỗ trợ) → phương tiện được thả dù xuống bãi thả của phe → chiến đấu tự động theo hệ thống khắc chế giáp/đạn → hạ địch được hoàn một phần CP.

**Ngoài trận:** lên hạng thẻ (bản thiết kế + xu), trang bị theo nhánh (Thiết giáp, Xe nhẹ, Pháo binh, Không quân), căn cứ (loadout tháp theo ô cỡ), hòm đồ, chiến dịch 193 nhiệm vụ trong 15 chương, Tác chiến (chơi lại chiến dịch lớn, 4 cấp độ, mutator tuần), Pháo đài tuần, Săn trùm, Vô tận, Sinh tồn. Một loại tiền duy nhất: xu.

**Bản đồ:** 25 chiến trường 300 × 300 m, mỗi bản có phiên bản chiếm cứ điểm, sinh tồn và công thành; 25 bản dài 300 × 480 m (căn cứ nhiều lớp) cho Công thành, Phòng thủ, Vô tận và Pháo đài tuần. **Mô phỏng:** cố định 20 tick/giây, xác định (deterministic), tách khỏi phần hình ảnh.

![Trong trận (ảnh 3D; HUD ở ảnh này là bản trước phase 10, HUD mới ở phần 18): bản đồ nhỏ, thanh nhiệm vụ, nút lệnh, khay…](../images/05_che_do_kinh_te/shots_battle1.png)

*Hình: Trong trận (ảnh 3D; HUD ở ảnh này là bản trước phase 10, HUD mới ở phần 18): bản đồ nhỏ, thanh nhiệm vụ, nút lệnh, khay thẻ và CP. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Bản đồ sa mạc Dunebreak sau khi phóng to 50%; nhà cửa đã chỉnh tỷ lệ so với xe.](../images/05_che_do_kinh_te/shots_battle2.png)

*Hình: Bản đồ sa mạc Dunebreak sau khi phóng to 50%; nhà cửa đã chỉnh tỷ lệ so với xe. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

## 2. Chế độ chơi

Trạng thái: Đã áp

Nguồn dữ liệu: 05_che_do_kinh_te/Che_do. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §2. Chế độ chơi.

| Chế độ | Tóm tắt | Luật |
|---|---|---|
| **Giữ cứ điểm** | Giữ nhiều cứ điểm hơn | Hai phe tranh 3 cứ điểm; giữ nhiều cứ điểm hơn thì điểm đối phương giảm dần; hết điểm là thua. |
| **Sinh tồn** | Không căn cứ, không tháp: chỉ quân của bạn chống các đợt địch | Không căn cứ, không tháp: chỉ quân của bạn chống các đợt địch ngày càng mạnh; bị quét sạch hoặc để địch chiếm bãi là thua. |
| **Tử chiến** | Hạ đủ 480 CP xe địch trước | Tử chiến: hạ đủ số điểm tiêu diệt trước. |
| **Vua đồi** | Một mình giữ trung tâm | Vua đồi: giữ cứ điểm trung tâm để tích điểm. |
| **Công phá** | Chọc thủng ba khu phòng ngự | Công phá: người chơi đánh chiếm lần lượt 3 khu phòng thủ (A, B, C) trong quỹ thời gian; mỗi khu chiếm được cộng thêm giờ. |
| **Chiến dịch** |  | Chiến dịch 15 chương, 193 nhiệm vụ (xem phần 3); chơi lại các trận lớn ở Tác chiến (phần 5). |
| **Công thành** | San phẳng pháo đài địch | Công thành: pháo đài chiếm 45% bản đồ, 3 giai đoạn (trạm radar tuyến ngoài → máy phát khiên trong tường → sở chỉ huy), cổng, tường sập, vòm khiên, siêu pháo, chi viện bằng tàu hỏa hoặc đường băng (ph… |
| **Săn trùm** | 10 boss tuần này | Săn trùm (Boss Hunt): tuần này 10 boss (3 chủ lực) tăng dần, máu boss theo sức mạnh bộ bài; chế độ toàn bộ 41 boss theo thứ tự cốt truyện; hỗ trợ tác chiến tối đa +40% (xem phần 10h). Thưởng thêm 2 C… |
| **Phòng thủ** | Giữ pháo đài của bạn trước cuộc công thành | Phòng thủ: pháo đài là loadout căn cứ của bạn, ba tuyến lùi (mất tuyến được thưởng CP rút lui) và sở chỉ huy là trận chốt; đợt địch hiện trước bằng icon. |
| **Pháo đài tuần** | Mỗi tuần một pháo đài; vòng thành đã phá được giữ | Pháo đài tuần: một cuộc công thành mà vòng thành đã phá được giữ nguyên cả tuần; thắng lần đầu trong tuần có thưởng. |
| **Vô tận** | Pháo đài của bạn trước các đợt địch không ngừng | Vô tận: pháo đài của bạn trước các đợt địch không ngừng (mỗi 55 giây, to dần, tinh nhuệ dần); lưu kỷ lục đợt xa nhất. |
| **Sandbox** |  |  |
| **Đối công** | Căn cứ đối căn cứ: phá nhà chính đối phương |  |

Bốn độ khó Dễ / Thường / Khó / Cực khó ảnh hưởng AI địch, thu nhập, xe tinh nhuệ và thưởng:

Thời tiết (nắng, âm u, mưa, bão, tuyết, bão cát, sương mù, đêm) đổi dần trong 8 giây và ảnh hưởng tầm nhìn/hình ảnh.

![Công thành.](../images/05_che_do_kinh_te/shots_siege.png)

*Hình: Công thành. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Phòng thủ căn cứ.](../images/05_che_do_kinh_te/shots_defend.png)

*Hình: Phòng thủ căn cứ. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Boss.](../images/05_che_do_kinh_te/shots_boss.png)

*Hình: Boss. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Nhiệm vụ săn: mục tiêu hiện hình thoi đỏ trên bản đồ nhỏ.](../images/05_che_do_kinh_te/shots_hunt.png)

*Hình: Nhiệm vụ săn: mục tiêu hiện hình thoi đỏ trên bản đồ nhỏ. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

Sheet: 05_che_do_kinh_te/Che_do — Chế độ (12 dòng, 51 cột)

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

*in 10 / 51 cột; 38 cột khác (và raw_json, nguon): xem sheet.*

### 2b. Cân bằng chế độ và độ khó

Trạng thái: Đã áp

Nguồn dữ liệu: 05_che_do_kinh_te/Do_kho. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §2b. Cân bằng.

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

#### AI mua quân theo độ khó

Logic mua quân xác định (deterministic): một hàm chấm điểm (khắc chế quân địch đang thấy, vai trò còn thiếu, giá trị thực chiến theo giá) dùng ở mức khác nhau cho mỗi độ khó. Tên độ khó thống nhất: chiến dịch và Tác chiến đổi Anh hùng → Khó, Thép → Cực khó (kỷ lục lưu theo số nên giữ nguyên).

Sheet: 05_che_do_kinh_te/Do_kho — Độ khó (4 dòng, 13 cột)

| id | he_so_dich_tran_nhanh | thu_tu | bien_co_ally | bien_co_ally_waves | bien_co_directions | bien_co_elites | bien_co_escorts | bien_co_step | bien_co_warning |
|---|---|---|---|---|---|---|---|---|---|
| Easy | 0.4 | 0 | 0.7 | -1 | 1;2 | FALSE | 2 | 0 | 15 |
| Hard | 0.85 | 2 | 0.3 | -1 | 2;3 | FALSE | 4 | 2 | 8 |
| Normal | 0.75 | 1 | 0.5 | -1 | 2;2 | FALSE | 3 | 1 | 10 |
| VeryHard | 1.08 | 3 | 0.15 | 1 | 3;4 | TRUE | 5 | 3 | 6 |

*in 10 / 13 cột; 1 cột khác (và raw_json, nguon): xem sheet.*

### 2c. Luật trận, phần vô hạn, trung lập, thoại và kết trận

Trạng thái: Một phần — chờ prompt xuat_luot5 (sheet Ket_tran)

Nguồn dữ liệu: 05_che_do_kinh_te/Vo_han; 08_ban_do/Trung_lap_luat; 07_chien_dich_cot_truyen/Ket_tran. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §2c.

#### 4 hồi

Chiến dịch có 15 chương trong 4 hồi (trường `act` của campaign.json); mỗi hồi kết bằng một chương chuyển tiếp (13, 14, 15). Sau c9m10 là **Kết mạch Thorne** (thẻ chuyển, trước chương 15, hiện một lần và có trong dòng thời gian của Hồ sơ); phần kết thật sau c12m10; thắng c12m10 mở cấp Huyền thoại của Tác chiến.

#### Luật trận theo chế độ

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

#### Phần vô hạn

- Thắng Phòng thủ, Sinh tồn hoặc Săn trùm: bảng kết quả có **Đánh tiếp (vô hạn)** và **Kết thúc**. Thưởng thắng được ghi nhận trước khi đánh tiếp; thua về sau không lấy lại gì.
- Vô tận (mục menu giữ nguyên) là Phòng thủ bắt đầu ngay ở phần vô hạn: chung mã và chung bảng xếp hạng.
- Tăng độ khó chỉ bằng chỉ số, không thêm xe quá đợt cuối của phần hữu hạn: Phòng thủ / Vô tận / Sinh tồn địch +4% mỗi đợt, ta +2% mỗi đợt (tối đa +30%); Săn trùm địch +8% mỗi boss.
- Sinh tồn hữu hạn 10 đợt: đợt 5 mini boss, đợt 10 boss chủ lực; phần vô hạn mỗi 5 đợt mini boss, mỗi 10 đợt boss chủ lực. Mini boss không có siêu vũ khí.
- Thưởng: 18 xu × 0,9^k mỗi đợt vượt (Săn trùm 60 xu × 0,9^k mỗi boss), trần 600 xu/ngày cho mọi phần vô hạn; huy hiệu +10/+20/+30 đợt, +5/+10 boss. Săn trùm chọn đánh tiếp ở bảng kết quả (không còn lựa chọn 20 s trong trận).

#### Trung lập (V1)

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

#### Giao diện thoại

- Một dải thoại ở giữa phía dưới, trên khay thẻ, trong vùng an toàn: chân dung nhỏ (44 px; 52 px khi chữ Lớn) rồi tối đa 2 dòng, tên người nói in hoa theo màu phe. Nhân vật thiếu chân dung dùng chân dung tạm theo phe (ô màu tối của phe với chữ cái đầu).
- Không che đồng hồ mục tiêu, thanh boss và cảnh báo siêu vũ khí (tất cả ở dải trên cùng) ở 16:9, 20:9 và 4:3.
- Ưu tiên P0–P4: P0 cảnh báo hệ thống (không phụ thuộc cài đặt, cắt câu đang hiện); P1 cốt truyện / cảnh báo (bỏ qua khoảng cách, chờ câu đang hiện xong); P2 sự kiện của màn (giữ 12 s); P3 phản ứng, P4 không khí (quá 8 s thì bỏ). 9 s / 20 s (có boss) là khoảng cách tối thiểu. Cài đặt Đầy đủ / Chỉ quan trọng / Tắt; nhật ký 20 câu từ menu tạm dừng; 6 khoảnh khắc cốt truyện chậm ×0,5.
- Kịch bản 193 màn (1.601 câu), song ngữ, theo người nói chính và điểm kích hoạt của từng màn; validator kiểm ngân sách, độ dài, trùng câu, trigger, ngôn ngữ, tên riêng và các mốc cốt truyện.

#### Chuỗi kết trận

- RUNNING → RESOLVED → PRESENTATION → RESULTS. Ở RESOLVED kết quả, thưởng, sao và điểm đã chốt; từ đó mô phỏng đứng yên (không bước mô phỏng, AI hay chế độ), nên kết quả không phụ thuộc phần trình diễn và replay chốt cùng tick.
- PRESENTATION chỉ là hình ảnh: ẩn khay thẻ và nút lệnh (giữ thanh boss, thông báo, thoại), khung điện ảnh, camera tới mục tiêu cuối trong 1,5 s đầu, boss nổ từng bộ phận cách nhau 0,4 s rồi nổ thân; thắng lần đầu hoặc trận lớn quay chậm ×0,3 từ giây 1,5 bằng đồng hồ hình ảnh (không chạm thời gian mô phỏng).
- Thời lượng: thắng lần đầu màn boss chính hoặc chiến dịch lớn 7 s (6–8), thắng lần đầu 4,5 s (4–5), chơi lại 3 s (2,5–4), thua 3,5 s (3–4, không quay chậm: camera về sở chỉ huy hoặc xe cuối, một vụ nổ, câu của tướng địch). Chạm để bỏ qua sau 0,75 s; câu cốt truyện bị bỏ qua hiện ở bảng kết quả (mục "Trên kênh liên lạc") và vào nhật ký.

Sheet: 05_che_do_kinh_te/Vo_han — Vô hạn và bảng xếp hạng (6 dòng, 5 cột)

| id | thu_tu_xep_hang | he_so_tang_thuong |
|---|---|---|
| bossrush | -bosses;+seconds;-parts | NEED_CODE_CHECK |
| bossrushEndless | -bosses;+seconds;-parts | NEED_CODE_CHECK |
| defendEndless | -waves;-killedBaseCp;-seconds | NEED_CODE_CHECK |
| endless | -waves;-killedBaseCp;-seconds | NEED_CODE_CHECK |
| survivalEndless | -waves;-killedBaseCp;-seconds | NEED_CODE_CHECK |
| weekly | -cleared;+attempts;+seconds | NEED_CODE_CHECK |

Sheet: 08_ban_do/Trung_lap_luat — Trung lập: luật (18 dòng, 8 cột)

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

Sheet: 07_chien_dich_cot_truyen/Ket_tran — Kết trận (1 dòng, 5 cột)

| id | trang_thai | ghi_chu |
|---|---|---|
| chua_ap | CHUA_AP:prompt_xuat_luot5 | đọc hằng trong Assets/MachineBrigade/Scripts/Game/Match/Mat… |

## 5. Tác chiến

Trạng thái: Đã áp

Nguồn dữ liệu: 05_che_do_kinh_te/Tac_chien_bac; 05_che_do_kinh_te/Diem_tac_chien; 05_che_do_kinh_te/Mutator; 11_meta_giao_dien/Mutator_tuan. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §5. Tác chiến.

Menu gồm 5 mục: Trang chủ, Chiến dịch, **Tác chiến**, Quân đội, Cửa hàng; Giao tranh (Giữ cứ điểm, Vua đồi, Tử chiến, Công phá, Công thành, Phòng thủ) và Thử thách (Sinh tồn, Vô tận) chọn ở ô chọn chế độ. Tác chiến gom: chơi lại các chiến dịch lớn và các trận nổi bật của cốt truyện (công thành, phòng thủ, đấu tướng) sau khi đã thắng trong chiến dịch (26 trận), chiến dịch của tuần, Pháo đài tuần, Săn trùm và thử thách hằng ngày.

#### Cấp độ

Huyền thoại mở sau khi thắng **c12m10** (Icarus rơi, trận cuối chiến dịch; Operations.LegendMission). **Điểm** một trận thắng: 5000 + tối đa 3000 theo thời gian dưới 25 phút + tối đa 2000 theo tổn thất (150 xe mất thì bằng 0) + tối đa 2000 theo máu sở chỉ huy; nhân hệ số cấp cộng phần của mỗi mutator. Thua: 0 điểm. Kỷ lục (điểm cao nhất, thắng nhanh nhất) lưu riêng cho từng trận và từng cấp.

**Thưởng tuần gộp chung một sổ:** thắng lần đầu trong tuần Pháo đài tuần 600 xu, chiến dịch của tuần 800 xu.

#### Vòng xoay 26 tuần

Mỗi tuần một chiến dịch và hai mutator, chọn theo số tuần (ISO, UTC) nên mọi người cùng một tuần; các cặp loại trừ nhau không bao giờ đi cùng, mỗi mutator đều xuất hiện trong nửa năm, không cặp nào lặp lại.

| Tuần | Chiến dịch | Mutator 1 | Mutator 2 |
|---|---|---|---|
| 1 | Pháo đài Ashfield | Đêm bão | Không hỏa lực |
| 2 | Behemoth ở Red Rock | Chỉ dùng xe dưới 8 CP | Bão biển |
| 3 | Tuyến Frostpeak | Pháo giấy | Mưa bom |
| 4 | Leviathan | Tháp địch ×2 | Bầy đàn |
| 5 | Matriarch | Địch toàn không quân | Thêm mini boss |
| 6 | Bảo vệ con đập | Tác chiến đêm | Hạm đội |
| 7 | Giải phóng Veyra | Chạy đua thời gian | Căn cứ trống |
| 8 | Hố sâu nhất | Không có trạm sửa chữa | Hậu cần cạn kiệt |
| 9 | Typhon trồi lên | Chỉ thiết giáp | Địch lão luyện |
| 10 | Tấn công Skyhold | Tướng địch tăng cường | Cấm không quân |
| 11 | Skygate Array | Không hỏa lực | Không có trạm sửa chữa |
| 12 | Icarus rơi | Đêm bão | Thêm mini boss |
| 13 | Pháo đài Ashfield | Tháp địch ×2 | Địch lão luyện |
| 14 | Behemoth ở Red Rock | Chỉ dùng xe dưới 8 CP | Chạy đua thời gian |
| 15 | Tuyến Frostpeak | Bầy đàn | Tác chiến đêm |
| 16 | Leviathan | Hậu cần cạn kiệt | Mưa bom |
| 17 | Matriarch | Pháo giấy | Bão biển |
| 18 | Bảo vệ con đập | Địch toàn không quân | Tướng địch tăng cường |
| 19 | Giải phóng Veyra | Căn cứ trống | Hạm đội |
| 20 | Hố sâu nhất | Chỉ thiết giáp | Cấm không quân |
| 21 | Typhon trồi lên | Đêm bão | Mưa bom |
| 22 | Tấn công Skyhold | Tháp địch ×2 | Chỉ dùng xe dưới 8 CP |
| 23 | Skygate Array | Thêm mini boss | Chỉ thiết giáp |
| 24 | Icarus rơi | Địch toàn không quân | Tác chiến đêm |
| 25 | Pháo đài Ashfield | Bầy đàn | Bão biển |
| 26 | Behemoth ở Red Rock | Không hỏa lực | Hậu cần cạn kiệt |

Sheet: 05_che_do_kinh_te/Tac_chien_bac — Tác chiến: bậc (4 dòng, 7 cột)

| id | enemy | player_income | score | supports |
|---|---|---|---|---|
| heroic | 1.3 | 1.0 | 1.3 | TRUE |
| iron | 1.3 | 0.8 | 1.6 | FALSE |
| legend | 1.6 | 0.75 | 2.0 | FALSE |
| normal | 1.0 | 1.0 | 1.0 | TRUE |

Sheet: 05_che_do_kinh_te/Diem_tac_chien — Điểm Tác chiến (8 dòng, 8 cột)

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

Sheet: 05_che_do_kinh_te/Mutator — Mutator (20 dòng, 28 cột)

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

*in 10 / 28 cột; 16 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 11_meta_giao_dien/Mutator_tuan — Mutator tuần (1 dòng, 5 cột)

| id | trang_thai | ghi_chu |
|---|---|---|
| chua_ap | XEM_05 | dữ liệu ở 05_che_do_kinh_te/Mutator (operations.json); chọn… |

## 14. Kinh tế

Trạng thái: Đã áp

Nguồn dữ liệu: 05_che_do_kinh_te/Kinh_te; 11_meta_giao_dien/Nang_hang; 11_meta_giao_dien/Hom_do; 11_meta_giao_dien/Cua_hang; 02_phuong_tien/Doi_mo_man; 02_phuong_tien/Doi_mo_man_luat. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §14. Kinh tế.

#### Trong trận

**CP (điểm chỉ huy):** khởi đầu thường 12–34 CP tùy chế độ, thu nhập ~1 CP/giây × hệ số chung 0.9, +0.25 CP/giây cho mỗi cứ điểm giữ được, kho tối đa 30 CP. **Tiếp tế:** quân vượt mức tiếp tế (24 CP × 1.05) thì thu nhập giảm (tối đa −75%). **Hạ địch:** hoàn 25% giá xe bị hạ cho phe hạ. **Bắt kịp:** phe bị áp đảo được tăng thu nhập tới +50%. **Giới hạn:** 32 xe, 6 máy bay. Xe mua được thả dù sau 3,5 giây.

#### Ngoài trận (một loại tiền: xu)

Thưởng trận nhanh: thắng 120 / hòa 70 / thua 40 xu + 1,5 xu mỗi xe hạ (tối đa 120) + 4 xu mỗi phút (tối đa 15), × hệ số độ khó; XP = 80% xu. Sinh tồn/Vô tận: 30 + 18 × số đợt + 1,5 × số xe hạ. Nhiệm vụ: thưởng theo sao và cấp độ. Thử thách hằng ngày 3 nhiệm vụ.

#### Thu nhập theo chế độ (vòng 6: tăng vừa phải 12–26%)

Hệ số chung: thu nhập 0,85 → **0,95**, tiếp tế 0,9 → **1,05** (nhiều xe trên sân hơn khoảng 12%). Tham khảo: elixir của Clash Royale (tăng x2/x3 cuối trận), Potential của Arknights (giảm giá nhỏ theo bậc, có trần), Boss Rush của BTD6 (thưởng khi gây sát thương cho boss). Tiêm kích 12 → 10 CP, cường kích 13 CP, xe rùa 8 CP; pháo phòng không của boss 27 → 21 sát thương/viên; máy bay VTOL không dừng lơ lửng trong tầm pháo phòng không; AI không mua tiêm kích khi địch không có máy bay.

#### Hạng thẻ

Từ hạng 7 thẻ rẻ hơn 5%, từ hạng 9 rẻ hơn 10% khi gọi (làm tròn CP nguyên, thẻ ≤ 5 CP không đổi). Giá trị quân, phí tiếp tế và tiền hoàn khi bị hạ vẫn tính theo giá gốc.

#### Hòm đồ

Giữ nguyên mua bằng xu (quyết định của chủ dự án). Có cơ chế bảo hiểm (pity) cho Sử thi/Huyền thoại, tỷ lệ công khai trong game.

Sheet: 05_che_do_kinh_te/Kinh_te — Kinh tế (18 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so | gia_tri_chu |
|---|---|---|---|---|
| campaign.economy.payScale["2"] | economy | 2 | 3.0 |  |
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
| ma.hoan_cp_khi_ha | ma | hoàn CP khi hạ, bắt kịp, thưởng rút lui, thưởng bộ phận bos… |  | NEED_CODE_CHECK |
| ma.tiep_te_cong_thuc | ma | tiếp tế: công thức, ngưỡng, đường phạt, tối đa -75 % |  | NEED_CODE_CHECK |

Sheet: 11_meta_giao_dien/Nang_hang — Giá nâng hạng (10 dòng, 6 cột)

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

Sheet: 11_meta_giao_dien/Hom_do — Hòm đồ và tỷ lệ rơi (4 dòng, 18 cột)

| id | bac_hom | ty_le_0 | ty_le_1 | ty_le_2 | ty_le_3 | ty_le_4 | rolls | coins_low | coins_high |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 0.7 | 0.25 | 0.045 | 0.005 | 0 | 1 | 60 | 120 |
| 1 | 1 | 0.5 | 0.35 | 0.12 | 0.028 | 0.002 | 2 | 250 | 350 |
| 2 | 2 | 0.2 | 0.42 | 0.28 | 0.085 | 0.015 | 4 | 800 | 1000 |
| 3 | 3 | 0 | 0.25 | 0.45 | 0.24 | 0.06 | 6 | 2000 | 2500 |

*in 10 / 18 cột; 6 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 11_meta_giao_dien/Cua_hang — Cửa hàng (6 dòng, 6 cột)

| id | id_goi | xu | gia_hien_thi |
|---|---|---|---|
| coins_1200 | coins_1200 | 1200 | $0.99 |
| coins_7000 | coins_7000 | 7000 | $4.99 |
| coins_15000 | coins_15000 | 15000 | $9.99 |
| coins_32000 | coins_32000 | 32000 | $19.99 |
| coins_85000 | coins_85000 | 85000 | $49.99 |
| coins_180000 | coins_180000 | 180000 | $99.99 |

Sheet: 02_phuong_tien/Doi_mo_man — Đội mở màn (23 dòng, 7 cột)

| id | ben | vai_tro | base_cp_uoc_tinh | thieu_vai_tro_hoan_cp |
|---|---|---|---|---|
| commander.adler | commander | scout;light | 5 | bo_vai_tro_giu_cp |
| commander.brandt | commander | bunker;engineer | 10 | bo_vai_tro_giu_cp |
| commander.brenn | commander |  | 0 | bo_vai_tro_giu_cp |
| commander.dahl | commander | artillery;scout | 6 | bo_vai_tro_giu_cp |
| commander.kade | commander | mbt;scout | 10 | bo_vai_tro_giu_cp |
| commander.kerr | commander | scout;radar_scout;light | 9 | bo_vai_tro_giu_cp |
| commander.lind | commander | engineer;repair;light | 10 | bo_vai_tro_giu_cp |
| commander.mendez | commander | wheeled;light_tank;scout | 8 | bo_vai_tro_giu_cp |
| commander.okoye | commander |  | 0 | bo_vai_tro_giu_cp |
| commander.quist | commander | fortify;light;scout | 12 | bo_vai_tro_giu_cp |
| commander.reyes | commander | scout_heli;scout | 8 | bo_vai_tro_giu_cp |
| commander.reyn | commander | mbt | 8 | bo_vai_tro_giu_cp |
| commander.varro | commander | cheap4;cheap4;cheap4 | 6 | bo_vai_tro_giu_cp |
| commander.venn | commander | fpv;scout | 9 | bo_vai_tro_giu_cp |
| general.aurel | general | heavy | 7 | bo_vai_tro_giu_cp |
| general.default | general | scout;light | 5 | bo_vai_tro_giu_cp |
| general.kessler | general | mine_layer;light | 9 | bo_vai_tro_giu_cp |
| general.orlov | general | artillery;radar_scout | 8 | bo_vai_tro_giu_cp |
| general.sen | general | drone | 6 | bo_vai_tro_giu_cp |
| general.thorne | general | mbt | 8 | bo_vai_tro_giu_cp |
| general.varga | general | tank | 3 | bo_vai_tro_giu_cp |
| general.venn | general | drone | 6 | bo_vai_tro_giu_cp |
| general.wolff | general | heli | 6 | bo_vai_tro_giu_cp |

Sheet: 02_phuong_tien/Doi_mo_man_luat — Đội mở màn: luật (3 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so | gia_tri_chu |
|---|---|---|---|---|
| enemyModes | openingSquads | enemyModes |  | Conquest;Deathmatch;KingOfTheHill;Assault;Siege;Showdown |
| modes | openingSquads | modes |  | Conquest;Deathmatch;KingOfTheHill;Assault;Siege;Defend;Endl… |
| share | openingSquads | share | 0.6 |  |

### 16b. Kiểm tĩnh chế độ

Trạng thái: Một phần — chờ prompt xuất dữ liệu (sheet kiểm tĩnh chế độ của spec 4 chưa có; số nằm ở báo cáo Docs/checks/mode_static_audit.md và showdown_static.md, in dưới đây)

Nguồn dữ liệu: (không có sheet; chỉ văn bản). Văn bản: Docs/checks/mode_static_audit.md; Docs/checks/showdown_static.md.

#### Báo cáo `Docs/checks/mode_static_audit.md`

##### Mode static audit (prompt 30 L8, theory only)

Generated by `Tools/audit/mode_static_audit.py`. Four ledgers per mode (Economy, Free/scripted, Static, Tempo) at 25/50/75/100 % of the mode's target length (the middle of the sheet's range), Normal difficulty. Strength is in CP-equivalents; the band is enemy / player. **No win rate is predicted.** Old measured numbers belong in the design document's measurement history, not here.

Constants: global income scale 0.9; wave vehicle 8.1 CP on average (Survival's roster); a fixed defence ≈ 15.1 CP and a mini boss ≈ 212, a main boss ≈ 370 CP by health per CP of that roster; a player base at level 3 ≈ 7 towers.

Limits: CP that could be spent is not CP that is spent well; bank caps, supply upkeep, the catch-up, the underdog help, card ranks, commanders, events and the AI's choices are not modelled; Assault's sector defences and Weekly's carried-over damage are left out.

###### Conquest (6-10 min, symmetric)

**Flags:** no symmetric mode outside 20 %.

Source: ConquestSession: StartCp 14, PointIncome 0.15, enemy income x1.18.

| % | Player econ | Player free | Player static | Enemy econ | Enemy free | Enemy static | Band (E/P) | Flag |
|---|---|---|---|---|---|---|---|---|
| 25 | 146 | 0 | 0 | 166 | 0 | 0 | 1.13 | GREEN |
| 50 | 279 | 0 | 0 | 317 | 0 | 0 | 1.14 | GREEN |
| 75 | 411 | 0 | 0 | 469 | 0 | 0 | 1.14 | GREEN |
| 100 | 543 | 0 | 0 | 621 | 0 | 0 | 1.14 | GREEN |

Tempo (drop zone to first objective, player / enemy): 28 s / 28 s.

###### Deathmatch (6-9 min, symmetric)

Source: DeathmatchSession: 18/1.35 vs 18/1.2.

| % | Player econ | Player free | Player static | Enemy econ | Enemy free | Enemy static | Band (E/P) | Flag |
|---|---|---|---|---|---|---|---|---|
| 25 | 155 | 0 | 0 | 140 | 0 | 0 | 0.90 | GREEN |
| 50 | 291 | 0 | 0 | 261 | 0 | 0 | 0.90 | GREEN |
| 75 | 428 | 0 | 0 | 382 | 0 | 0 | 0.89 | GREEN |
| 100 | 565 | 0 | 0 | 504 | 0 | 0 | 0.89 | GREEN |

Tempo (drop zone to first objective, player / enemy): 28 s / 28 s.

###### KingOfTheHill (6-9 min, symmetric)

Source: KingOfTheHillSession: 16/1.2 vs 16/1.1; the holder +0.35/s.

| % | Player econ | Player free | Player static | Enemy econ | Enemy free | Enemy static | Band (E/P) | Flag |
|---|---|---|---|---|---|---|---|---|
| 25 | 155 | 0 | 0 | 145 | 0 | 0 | 0.93 | GREEN |
| 50 | 294 | 0 | 0 | 274 | 0 | 0 | 0.93 | GREEN |
| 75 | 434 | 0 | 0 | 403 | 0 | 0 | 0.93 | GREEN |
| 100 | 573 | 0 | 0 | 532 | 0 | 0 | 0.93 | GREEN |

Tempo (drop zone to first objective, player / enemy): 28 s / 28 s.

###### Assault (8-12 min, asymmetric)

Source: AssaultSession: attacker 20/1.45, defender 32/1.3, 8 CP and +0.25/s a sector; sector defences not counted.

| % | Player econ | Player free | Player static | Enemy econ | Enemy free | Enemy static | Band (E/P) | Flag |
|---|---|---|---|---|---|---|---|---|
| 25 | 216 | 0 | 0 | 208 | 0 | 0 | 0.96 | - |
| 50 | 453 | 0 | 0 | 383 | 0 | 0 | 0.85 | - |
| 75 | 724 | 0 | 0 | 559 | 0 | 0 | 0.77 | - |
| 100 | 1030 | 0 | 0 | 734 | 0 | 0 | 0.71 | - |

Tempo (drop zone to first objective, player / enemy): 28 s / 28 s.

###### Siege (10-15 min, asymmetric)

Source: SiegeSession: attacker 38/2.4, defender 20/0.8; fortress hardpoints from the maps (31).

| % | Player econ | Player free | Player static | Enemy econ | Enemy free | Enemy static | Band (E/P) | Flag |
|---|---|---|---|---|---|---|---|---|
| 25 | 443 | 0 | 0 | 155 | 0 | 469 | 1.41 | - |
| 50 | 848 | 0 | 0 | 290 | 0 | 469 | 0.90 | - |
| 75 | 1253 | 0 | 0 | 425 | 0 | 469 | 0.71 | - |
| 100 | 1658 | 0 | 0 | 560 | 0 | 469 | 0.62 | - |

Tempo (drop zone to first objective, player / enemy): 58 s / 3 s.

###### Weekly (10-15 min, asymmetric)

Source: as Siege (broken rings stay broken over the week: not modelled).

| % | Player econ | Player free | Player static | Enemy econ | Enemy free | Enemy static | Band (E/P) | Flag |
|---|---|---|---|---|---|---|---|---|
| 25 | 443 | 0 | 0 | 155 | 0 | 469 | 1.41 | - |
| 50 | 848 | 0 | 0 | 290 | 0 | 469 | 0.90 | - |
| 75 | 1253 | 0 | 0 | 425 | 0 | 469 | 0.71 | - |
| 100 | 1658 | 0 | 0 | 560 | 0 | 469 | 0.62 | - |

Tempo (drop zone to first objective, player / enemy): 58 s / 3 s.

###### Defend (11-13 min, asymmetric)

Source: DefendSession: defender 30/1.35 + its base; attacker 22/1.1 + waves 3 + 1.8/wave every 70 s.

| % | Player econ | Player free | Player static | Enemy econ | Enemy free | Enemy static | Band (E/P) | Flag |
|---|---|---|---|---|---|---|---|---|
| 25 | 249 | 0 | 106 | 200 | 63 | 0 | 0.74 | - |
| 50 | 467 | 0 | 106 | 378 | 268 | 0 | 1.13 | - |
| 75 | 686 | 0 | 106 | 557 | 477 | 0 | 1.31 | - |
| 100 | 905 | 0 | 106 | 735 | 901 | 0 | 1.62 | - |

Tempo (drop zone to first objective, player / enemy): 31 s / 53 s.

###### Survival (8-12 min, asymmetric)

Source: SurvivalSession / SandboxMode: player 16/0.9; waves 3 + 0.9/wave every 30 s from 20 s; bosses at 5 and 10.

| % | Player econ | Player free | Player static | Enemy econ | Enemy free | Enemy static | Band (E/P) | Flag |
|---|---|---|---|---|---|---|---|---|
| 25 | 138 | 0 | 0 | 0 | 407 | 0 | 2.96 | - |
| 50 | 259 | 0 | 0 | 0 | 1155 | 0 | 4.46 | - |
| 75 | 380 | 0 | 0 | 0 | 1155 | 0 | 3.03 | - |
| 100 | 502 | 0 | 0 | 0 | 1155 | 0 | 2.30 | - |

Tempo (drop zone to first objective, player / enemy): 28 s / 28 s.

###### BossRush (15-25 min, asymmetric)

Source: BossRushSession: player 30/1.5; ten bosses over the run.

| % | Player econ | Player free | Player static | Enemy econ | Enemy free | Enemy static | Band (E/P) | Flag |
|---|---|---|---|---|---|---|---|---|
| 25 | 435 | 0 | 0 | 0 | 728 | 0 | 1.67 | - |
| 50 | 840 | 0 | 0 | 0 | 1456 | 0 | 1.73 | - |
| 75 | 1245 | 0 | 0 | 0 | 2184 | 0 | 1.75 | - |
| 100 | 1650 | 0 | 0 | 0 | 2912 | 0 | 1.76 | - |

Tempo (drop zone to first objective, player / enemy): 28 s / 28 s.

#### Báo cáo `Docs/checks/showdown_static.md`

##### Showdown: static base-break estimate (prompt 32 L7)

Generated by `Tools/balance/p32_showdown_static.py` (no simulation). An army of the average ground card (fixed, no
reinforcement) against an HQ 5 base (base.reference level 5) with two wall lines, under the fire of the towers covering
the approach; the assumptions are in the script's header and DECISIONS "Prompt 32 L3 / L7 / L9".

| walls | army | vehicles | outer segment | covering towers | inner segment | HQ down | left |
|---|---|---|---|---|---|---|---|
| none | 40 CP | 5 x main_battle_tank | - | - (0) | - | held (stopped at heavy_turret) | 0.0 |
| none | 80 CP | 10 x main_battle_tank | - | 1:38 (6) | - | held (stopped at HQ) | 0.0 |
| none | 120 CP | 15 x main_battle_tank | - | 1:14 (6) | - | 2:30 | 8.7 |
| none | 160 CP | 20 x main_battle_tank | - | 1:05 (6) | - | 1:53 | 15.8 |
| hesco | 40 CP | 5 x main_battle_tank | 1:10 | - (0) | - | held (stopped at heavy_turret) | 0.0 |
| hesco | 80 CP | 10 x main_battle_tank | 0:52 | 2:02 (6) | 2:32 | held (stopped at HQ) | 0.0 |
| hesco | 120 CP | 15 x main_battle_tank | 0:48 | 1:24 (6) | 1:34 | 3:03 | 6.8 |
| hesco | 160 CP | 20 x main_battle_tank | 0:46 | 1:12 (6) | 1:19 | 2:10 | 14.8 |
| t_wall | 40 CP | 5 x main_battle_tank | - | - (0) | - | held (stopped at outer wall segment) | 0.0 |
| t_wall | 80 CP | 10 x main_battle_tank | 1:22 | - (0) | - | held (stopped at heavy_turret) | 0.0 |
| t_wall | 120 CP | 15 x main_battle_tank | 1:05 | 1:46 (6) | 2:24 | held (stopped at HQ) | 0.0 |
| t_wall | 160 CP | 20 x main_battle_tank | 0:58 | 1:26 (6) | 1:48 | 2:47 | 12.4 |
| gun_wall | 40 CP | 5 x main_battle_tank | 1:20 | - (0) | - | held (stopped at heavy_turret) | 0.0 |
| gun_wall | 80 CP | 10 x main_battle_tank | 0:55 | 2:12 (6) | 3:03 | held (stopped at HQ) | 0.0 |
| gun_wall | 120 CP | 15 x main_battle_tank | 0:50 | 1:26 (6) | 1:38 | 3:11 | 6.4 |
| gun_wall | 160 CP | 20 x main_battle_tank | 0:47 | 1:13 (6) | 1:21 | 2:12 | 14.6 |

###### Reading

- 40 CP: none held, hesco held, t_wall held, gun_wall held.
- 80 CP: none held, hesco held, t_wall held, gun_wall held.
- 120 CP: none 2.5 min, hesco 3.0 min, t_wall held, gun_wall 3.2 min.
- 160 CP: none 1.9 min, hesco 2.2 min, t_wall 2.8 min, gun_wall 2.2 min.

Showdown's 12 minutes buy about 950 CP a side at its income (21 at the start, 1.35 CP/s x 0.9, x1.5 from minute 6),
most of it spent against the other side's army; an attack that breaks a walled HQ 5 base needs an army of the size
where the base falls above, arriving with the defender's army beaten. The walls add the segments' time (the T-wall
the most) and keep the covering towers firing longer. Verdict (static): 12 minutes is a reasonable limit: a side
that wins the field battle by minute 6-8 has time to break in; an even match goes to the HQ lead or sudden death.
NEED SIM: the real times (no simulation was run).

## Tham khảo ngoài đời và game

Trạng thái: Đã áp (lượt 10; chỉ dữ liệu trong repo, thiếu nguồn ghi NEED_SOURCE).

Nguồn dữ liệu: 05_che_do_kinh_te/Che_do_tham_chieu; 05_che_do_kinh_te/Che_do_so_sanh_that; 13_tham_chieu_nguon/Nguon_tham_chieu.

### Che_do_tham_chieu

12 dòng. Độ tin cậy: da_kiem_chung 0, uoc_dinh 0, ban_dau_doan 1, NEED_SOURCE 11. Loại: NEED_SOURCE 11, game 1.

- `conquest` (Conquest): game: Company of Heroes; giống: DECISIONS mục '28 5 (cloud, 2026-10-02)': Conquest đã trừ dần bên giữ ít điểm hơn; độ tin: ban_dau_doan; nguồn: R_decisions.

Nguồn được dùng (tiêu đề như repo ghi; link khi repo có):

- `R_decisions`: Docs/DECISIONS.md (nhật ký quyết định) (độ tin 3)

Sheet: 05_che_do_kinh_te/Che_do_so_sanh_that — Chế độ: so sánh với thật (1 dòng, 5 cột)

| id | trang_thai | ghi_chu |
|---|---|---|
| khong_co | KHONG_CO | chế độ chơi không có thông số ngoài đời để đối chiếu |

## Các sheet khác của file

Mọi sheet chưa in ở mục trên (sheet input_<tên> là bản chép từ file khác, không in lại).

### Che_do_thoi_luong

Trạng thái: Đã áp

Nguồn dữ liệu: 05_che_do_kinh_te/Che_do_thoi_luong.

Sheet: 05_che_do_kinh_te/Che_do_thoi_luong — Chế độ: thời lượng lý thuyết (12 dòng, 20 cột)

| id | doc_gio_du_lieu | gio_bat_dau_ma_s | thuong_giai_doan_s | tran_quy_ma_s | dot_dau_s | cach_dot_s | nguon_ma | gio_du_lieu_s | hiep_phu_s |
|---|---|---|---|---|---|---|---|---|---|
| assault | FALSE | 300.0 |  |  |  |  | Game/Match/ModeSessions.cs:602 |  | 60.0 |
| bossrush | FALSE | 1800.0 |  |  |  |  | Game/Match/BossHunts.cs:19 | 1800 | 0.0 |
| conquest | TRUE |  |  |  |  |  |  | 600 | 60.0 |
| deathmatch | TRUE |  |  |  |  |  |  | 540 | 60.0 |
| defend | FALSE | 480.0 | 150.0 | 900.0 |  |  | Game/Match/ModeSessions.cs:691 | 720 | 0.0 |
| endless | FALSE |  |  |  |  |  |  |  | 0.0 |
| hill | TRUE |  |  |  |  |  |  | 540 | 60.0 |
| operations | FALSE |  |  |  |  |  |  |  | 0.0 |
| showdown | TRUE |  |  |  |  |  |  | 720 | 90.0 |
| siege | FALSE | 480.0 | 600.0 | 900.0 |  |  | Game/Match/ModeSessions.cs:869, 874 | 1080 | 60.0 |
| survival | FALSE |  |  |  | 20.0 | 30.0 | Sim/Modes/SandboxMode.cs:69, Sim/Modes/SandboxMode.cs:70 |  | 0.0 |
| weekly | FALSE | 300.0 | 540.0 | 600.0 |  |  | Game/Match/ModeSessions.cs:792, Sim/Modes/SiegeModes.cs:35 |  | 60.0 |

*in 10 / 20 cột; 8 cột khác (và raw_json, nguon): xem sheet.*

### Kiem_tinh_che_do

Trạng thái: Đã áp

Nguồn dữ liệu: 05_che_do_kinh_te/Kiem_tinh_che_do.

Sheet: 05_che_do_kinh_te/Kiem_tinh_che_do — Kiểm tĩnh chế độ (4 sổ) (36 dòng, 21 cột)

| id | che_do | phan_tram | doi_xung | thoi_luong_muc_tieu_s | mien_phi_nguoi_choi_cp | mien_phi_dich_cp | tinh_nguoi_choi_cp | tinh_dich_cp | nhip_nguoi_choi_s |
|---|---|---|---|---|---|---|---|---|---|
| assault/25 | assault | 25.0 | FALSE | 600.0 | 0.0 | 0.0 | 0.0 | 0.0 | 26.092307692307692 |
| assault/50 | assault | 50.0 | FALSE | 600.0 | 0.0 | 0.0 | 0.0 | 0.0 | 26.092307692307692 |
| assault/75 | assault | 75.0 | FALSE | 600.0 | 0.0 | 0.0 | 0.0 | 0.0 | 26.092307692307692 |
| assault/100 | assault | 100.0 | FALSE | 600.0 | 0.0 | 0.0 | 0.0 | 0.0 | 26.092307692307692 |
| bossrush/25 | bossrush | 25.0 | FALSE | 1200.0 | 0.0 | 727.9434765436433 | 0.0 | 0.0 | 26.092307692307692 |
| bossrush/50 | bossrush | 50.0 | FALSE | 1200.0 | 0.0 | 1455.8869530872867 | 0.0 | 0.0 | 26.092307692307692 |
| bossrush/75 | bossrush | 75.0 | FALSE | 1200.0 | 0.0 | 2183.8304296309298 | 0.0 | 0.0 | 26.092307692307692 |
| bossrush/100 | bossrush | 100.0 | FALSE | 1200.0 | 0.0 | 2911.7739061745733 | 0.0 | 0.0 | 26.092307692307692 |
| conquest/25 | conquest | 25.0 | TRUE | 480.0 | 0.0 | 0.0 | 0.0 | 0.0 | 26.092307692307692 |
| conquest/50 | conquest | 50.0 | TRUE | 480.0 | 0.0 | 0.0 | 0.0 | 0.0 | 26.092307692307692 |
| conquest/75 | conquest | 75.0 | TRUE | 480.0 | 0.0 | 0.0 | 0.0 | 0.0 | 26.092307692307692 |
| conquest/100 | conquest | 100.0 | TRUE | 480.0 | 0.0 | 0.0 | 0.0 | 0.0 | 26.092307692307692 |
| deathmatch/25 | deathmatch | 25.0 | TRUE | 450.0 | 0.0 | 0.0 | 0.0 | 0.0 | 26.092307692307692 |
| deathmatch/50 | deathmatch | 50.0 | TRUE | 450.0 | 0.0 | 0.0 | 0.0 | 0.0 | 26.092307692307692 |
| deathmatch/75 | deathmatch | 75.0 | TRUE | 450.0 | 0.0 | 0.0 | 0.0 | 0.0 | 26.092307692307692 |
| deathmatch/100 | deathmatch | 100.0 | TRUE | 450.0 | 0.0 | 0.0 | 0.0 | 0.0 | 26.092307692307692 |
| defend/25 | defend | 25.0 | FALSE | 720.0 | 0.0 | 63.317647058823525 | 107.40269913996251 | 0.0 | 27.907692307692308 |
| defend/50 | defend | 50.0 | FALSE | 720.0 | 0.0 | 267.88235294117646 | 107.40269913996251 | 0.0 | 27.907692307692308 |
| defend/75 | defend | 75.0 | FALSE | 720.0 | 0.0 | 477.31764705882347 | 107.40269913996251 | 0.0 | 27.907692307692308 |
| defend/100 | defend | 100.0 | FALSE | 720.0 | 0.0 | 901.0588235294116 | 107.40269913996251 | 0.0 | 27.907692307692308 |
| hill/25 | hill | 25.0 | TRUE | 450.0 | 0.0 | 0.0 | 0.0 | 0.0 | 26.092307692307692 |
| hill/50 | hill | 50.0 | TRUE | 450.0 | 0.0 | 0.0 | 0.0 | 0.0 | 26.092307692307692 |
| hill/75 | hill | 75.0 | TRUE | 450.0 | 0.0 | 0.0 | 0.0 | 0.0 | 26.092307692307692 |
| hill/100 | hill | 100.0 | TRUE | 450.0 | 0.0 | 0.0 | 0.0 | 0.0 | 26.092307692307692 |
| siege/25 | siege | 25.0 | FALSE | 750.0 | 0.0 | 0.0 | 0.0 | 475.6405247626911 | 53.95384615384615 |
| siege/50 | siege | 50.0 | FALSE | 750.0 | 0.0 | 0.0 | 0.0 | 475.6405247626911 | 53.95384615384615 |
| siege/75 | siege | 75.0 | FALSE | 750.0 | 0.0 | 0.0 | 0.0 | 475.6405247626911 | 53.95384615384615 |
| siege/100 | siege | 100.0 | FALSE | 750.0 | 0.0 | 0.0 | 0.0 | 475.6405247626911 | 53.95384615384615 |
| survival/25 | survival | 25.0 | FALSE | 600.0 | 0.0 | 407.14037673699397 | 0.0 | 0.0 | 26.092307692307692 |
| survival/50 | survival | 50.0 | FALSE | 600.0 | 0.0 | 1154.6488988819735 | 0.0 | 0.0 | 26.092307692307692 |
| survival/75 | survival | 75.0 | FALSE | 600.0 | 0.0 | 1154.6488988819735 | 0.0 | 0.0 | 26.092307692307692 |
| survival/100 | survival | 100.0 | FALSE | 600.0 | 0.0 | 1154.6488988819735 | 0.0 | 0.0 | 26.092307692307692 |
| weekly/25 | weekly | 25.0 | FALSE | 750.0 | 0.0 | 0.0 | 0.0 | 475.6405247626911 | 53.95384615384615 |
| weekly/50 | weekly | 50.0 | FALSE | 750.0 | 0.0 | 0.0 | 0.0 | 475.6405247626911 | 53.95384615384615 |
| weekly/75 | weekly | 75.0 | FALSE | 750.0 | 0.0 | 0.0 | 0.0 | 475.6405247626911 | 53.95384615384615 |
| weekly/100 | weekly | 100.0 | FALSE | 750.0 | 0.0 | 0.0 | 0.0 | 475.6405247626911 | 53.95384615384615 |

*in 10 / 21 cột; 9 cột khác (và raw_json, nguon): xem sheet.*

### Kinh_te_suy_ra

Trạng thái: Đã áp

Nguồn dữ liệu: 05_che_do_kinh_te/Kinh_te_suy_ra.

Sheet: 05_che_do_kinh_te/Kinh_te_suy_ra — Kinh tế suy ra (44 dòng, 32 cột)

| id | che_do | do_kho | cp_khoi_dau_nguoi_choi_ma | thu_nhap_nguoi_choi_ma_cp_s | cp_khoi_dau_dich_ma | thu_nhap_dich_ma_cp_s | he_so_dich_che_do | he_so_dich_do_kho | thuong_muc_tieu_cp_s |
|---|---|---|---|---|---|---|---|---|---|
| assault/Easy | assault | Easy | 20.0 | 1.45 | 32.0 | 1.3 | 1.0 | 0.8 | 0.0 |
| assault/Hard | assault | Hard | 20.0 | 1.45 | 32.0 | 1.3 | 1.0 | 1.2 | 0.0 |
| assault/Normal | assault | Normal | 20.0 | 1.45 | 32.0 | 1.3 | 1.0 | 0.7 | 0.0 |
| assault/VeryHard | assault | VeryHard | 20.0 | 1.45 | 32.0 | 1.3 | 1.0 | 1.4 | 0.0 |
| bossrush/Easy | bossrush | Easy | 40.0 | 1.8 |  |  |  |  | 0.0 |
| bossrush/Hard | bossrush | Hard | 40.0 | 1.6 |  |  |  |  | 0.0 |
| bossrush/Normal | bossrush | Normal | 40.0 | 1.8 |  |  |  |  | 0.0 |
| bossrush/VeryHard | bossrush | VeryHard | 40.0 | 1.45 |  |  |  |  | 0.0 |
| conquest/Easy | conquest | Easy | 14.0 | 1.0 | 14.0 | 1.0 | 1.18 | 0.8 | 0.22499999999999998 |
| conquest/Hard | conquest | Hard | 14.0 | 1.0 | 14.0 | 1.0 | 1.18 | 1.2 | 0.22499999999999998 |
| conquest/Normal | conquest | Normal | 14.0 | 1.0 | 14.0 | 1.0 | 1.18 | 0.7 | 0.22499999999999998 |
| conquest/VeryHard | conquest | VeryHard | 14.0 | 1.0 | 14.0 | 1.0 | 1.18 | 1.4 | 0.22499999999999998 |
| deathmatch/Easy | deathmatch | Easy | 18.0 | 1.35 | 18.0 | 1.2 | 1.0 | 0.8 | 0.0 |
| deathmatch/Hard | deathmatch | Hard | 18.0 | 1.35 | 18.0 | 1.2 | 1.0 | 1.2 | 0.0 |
| deathmatch/Normal | deathmatch | Normal | 18.0 | 1.35 | 18.0 | 1.2 | 1.0 | 0.7 | 0.0 |

*15 / 44 dòng đầu: xem sheet 05_che_do_kinh_te/Kinh_te_suy_ra; in 10 / 32 cột; 20 cột khác (và raw_json, nguon): xem sheet.*
