# 09/10 owner prompt (verbatim): boss system from Machine_Brigade_Boss_Thiet_Ke_Tong_Hop.xlsx

làm cái này trước: đọc file @Machine_Brigade_Boss_Thiet_Ke_Tong_Hop.xlsx và sửa theo đó, code trước, khi làm vũ khí và boss mới, design boss mới / vũ khí mới cứ làm sơ sài cũng được, tôi đang có 1 agent khác sẽ vào và vẽ lại toàn bộ boss và vũ khí, nhớ áp dụng các quy tắc tiết kiệm token hết mức có thể, test cũng ở mức tối thiểu

<pasted_content id="e0cc">
# PROMPT TRIỂN KHAI HỆ THỐNG BOSS – MACHINE BRIGADE

Bạn là Senior Game Developer, Gameplay Programmer, Combat Designer và AI Engineer. Nhiệm vụ của bạn là **triển khai toàn bộ thiết kế Boss và Mini-boss trong file Excel `Machine_Brigade_Boss_Thiet_Ke_Tong_Hop.xlsx` vào source code game Machine Brigade hiện tại**.

## 1. NGUYÊN TẮC BẮT BUỘC

1. Đọc và phân tích **toàn bộ 16 sheet** trong file Excel trước khi chỉnh code.
2. Đối chiếu thiết kế Excel với source code, dữ liệu boss, vũ khí, AI, nhiệm vụ, spawn, model và hệ thống chiến đấu đang có.
3. **Excel là nguồn thiết kế mục tiêu.** Source code hiện tại là nguồn để xác định cấu trúc, API, đơn vị đo và các ràng buộc kỹ thuật.
4. Không xóa bất kỳ boss hoặc mini-boss nào đang tồn tại, kể cả những họ có hơn 3 mini-boss.
5. Giữ nguyên boss độc bản; không ép tất cả boss phải có mini-boss.
6. Không phá hệ thống nhiệm vụ, chiến dịch, Boss Hunt, độ khó, save/load hoặc dữ liệu hiện tại.
7. Không tự tạo ID vũ khí, quân lính, prefab, animation hoặc asset rồi giả định chúng đã tồn tại. Nếu chưa có, hãy tạo theo đúng cấu trúc dự án hoặc ghi rõ phần còn thiếu.
8. Không bỏ qua nội dung Excel chỉ vì việc triển khai phức tạp.
9. Nếu dữ liệu Excel chưa đủ hoặc mâu thuẫn với code, phải xác minh và ghi lại quyết định xử lý; không âm thầm đoán.
10. Các thay đổi phải có kiểm thử và dễ điều chỉnh về sau.

## 2. CÁC SHEET CẦN XỬ LÝ

Đọc và liên kết dữ liệu giữa các sheet:

- `00_Tong_quan`: nguyên tắc cân bằng tổng thể.
- `01_Danh_sach_Boss`: boss hiện có và cấu hình bệ súng.
- `02_Sung_bo_sung`: danh sách vũ khí cần bổ sung.
- `03_Nerf_33`: ngân sách DPS và mức nerf cho từng boss.
- `04_Bom_AoE`: cân bằng bom, sát thương diện rộng.
- `05_Mini_boss_moi`: 6 mini-boss cần tạo.
- `06_QA_Nguong`: tiêu chí kiểm thử cân bằng.
- `07_Tham_chieu_219`: 219 cấu hình vũ khí gốc làm tham chiếu.
- `08_Trieu_hoi`: hệ thống triệu hồi theo boss.
- `09_Luat_can_bang`: giới hạn triệu hồi và quy tắc chiến đấu.
- `10_Can_bang_HP`: HP gốc và HP mục tiêu.
- `11_Bo_phan`: bộ phận có thể phá hủy và tác động gameplay.
- `12_Nhom_hoa_luc`: phân nhóm hỏa lực và AI chọn mục tiêu.
- `13_Pha_AI`: thay đổi hành vi tại 50% HP.
- `14_Kiem_thu`: tiêu chí kiểm thử.
- `15_Huong_dan`: chỉ dẫn triển khai bổ sung.

Không chỉnh dữ liệu chỉ dựa trên một sheet riêng lẻ. Phải ghép thông tin theo Boss ID và Weapon ID.

## 3. GIẢM HP BOSS

Triển khai các giá trị HP mục tiêu từ `10_Can_bang_HP`.

Mục tiêu tổng thể: giảm HP boss khoảng **25–40%**, tùy từng boss và vai trò.

Yêu cầu:
- Phân biệt HP thiết kế, HP thực tế trong trận và HP của các bộ phận.
- Không nerf trùng hai lần thông qua hệ số độ khó hoặc `toughness.bosses`.
- Không khiến boss chết quá nhanh trước khi người chơi có cơ hội phá các bộ phận quan trọng.
- Kiểm tra armor, damage resistance, HP scaling và các hệ số theo chương.

Không thay thế các con số cụ thể trong Excel bằng một công thức chung nếu file đã quy định riêng từng boss.

## 4. BỔ SUNG VŨ KHÍ VÀ GIẢM DAMAGE

Triển khai vũ khí mới theo `02_Sung_bo_sung`, đồng bộ với `01_Danh_sach_Boss`, `03_Nerf_33` và `07_Tham_chieu_219`.

**Mục tiêu là tăng độ hoành tráng, không tăng sức mạnh tổng thể.**

- Boss lớn như phi thuyền, chiến hạm và khí cầu có nhiều bệ pháo hơn.
- Các loại pháo chính, pháo phụ, CIWS, laser phòng thủ điểm, rocket và tên lửa phải có chức năng riêng.
- Giảm damage và tốc bắn của cả súng cũ lẫn súng mới theo ngân sách DPS Excel.
- Không nhân tổng DPS theo số khẩu súng.
- Phân bổ thời điểm bắn để nhiều pháo không cùng dồn sát thương lên một mục tiêu.
- Giữ hiệu ứng bắn, xoay tháp pháo, muzzle flash, âm thanh, đường đạn và hiệu ứng va chạm.

Đặc biệt:
- **Leviathan có 22 bệ pháo đề xuất.**
- **Kraken có 13 bệ súng đề xuất**, ít hơn Leviathan vì Kraken là tàu sân bay, sức mạnh chính đến từ máy bay.
- Số bệ súng phải phản ánh hardpoint thực tế, không tính boong phóng máy bay là bệ pháo.

Nếu asset hiện tại không đủ điểm gắn súng, cần bổ sung hardpoint và kiểm tra vị trí, góc quay, góc bắn, va chạm và khả năng hiển thị.

## 5. NERF BOM VÀ SÁT THƯƠNG DIỆN RỘNG

Ưu tiên xử lý Roc và Argus.

Theo Excel, bom khí cầu cần thử:
- Damage mỗi lần nổ còn khoảng **35–50%** so với gốc.
- Tốc độ thả bom còn **65–75%**.
- Bán kính sát thương còn **75–85%**.
- Sát thương giảm dần theo khoảng cách tới tâm nổ.

Bổ sung cảnh báo trước khi bom, pháo hạng nặng và laser gây sát thương.

Ngăn các đòn diện rộng mạnh chồng lên nhau quá nhanh. Nếu boss có nhiều vũ khí hạng nặng, cân nhắc sử dụng lịch khai hỏa hoặc nhóm hồi chiêu chung theo thiết kế.

Không được để một đợt bom thông thường dễ dàng xóa sạch đội hình 5–8 xe tăng khỏe cùng cấp.

## 6. TRIỆU HỒI QUÂN THEO VAI TRÒ BOSS

Triển khai đầy đủ sheet `08_Trieu_hoi`.

Ví dụ:
- Kraken phóng máy bay từ boong.
- Roc phóng drone từ hangar.
- Matriarch triển khai drone chiến đấu.
- Icarus và Hyperion triển khai phi thuyền con hoặc drone.
- Daedalus thả xe cơ giới và đơn vị đổ bộ.
- Bastion, Jötunn và các boss mặt đất phù hợp triển khai xe tăng hoặc IFV.
- Moloch có khả năng sản xuất đơn vị cơ giới.

Sử dụng **cooldown, số lượng mỗi đợt và giới hạn quân sống** đã ghi trong Excel.

Yêu cầu:
1. Triệu hồi có animation hoặc hiệu ứng hợp lý: máy bay cất cánh, drone ra khỏi hangar, xe xuất phát từ cửa, đơn vị đổ bộ đáp xuống.
2. Không cho quân xuất hiện tức thời ngay sát người chơi nếu không có cơ chế báo trước.
3. Không spawn vô hạn.
4. Khi đạt giới hạn quân sống, bỏ qua đợt triệu hồi; không tích lũy lượt chờ.
5. Phân biệt quân hộ tống xuất hiện lúc bắt đầu, quân triệu hồi định kỳ và quân của sự kiện chuyển pha.
6. Quân đã triệu hồi vẫn chiến đấu nếu bộ phận triệu hồi bị phá.
7. Cân bằng tổng sức ép từ cả vũ khí boss lẫn quân triệu hồi.

## 7. BỘ PHẬN CÓ THỂ PHÁ HỦY

Triển khai sheet `11_Bo_phan`.

**KHÔNG tạo radar hoặc tháp chỉ huy dưới dạng bộ phận có thể phá hủy.**

Các bộ phận quan trọng:
- Tháp pháo: bị phá thì ngừng bắn.
- CIWS/phòng không: bị phá thì mất khả năng phòng thủ tương ứng.
- Động cơ: bị phá thì giảm khả năng di chuyển theo thiết kế.
- Hangar: bị phá thì ngừng gọi drone hoặc phi thuyền con.
- Boong phóng máy bay: bị phá thì ngừng cho máy bay mới cất cánh.
- **Cửa triển khai/khoang đổ bộ của boss mặt đất: bị phá thì không thể triệu hồi thêm xe tăng, IFV hoặc quân mới.**

Không áp dụng cơ chế phá cửa khiến một boss không có cửa hoặc hệ thống triển khai tương ứng bị lỗi.

Nếu có nhiều khẩu súng nhỏ, có thể gom chúng thành một subsystem phá hủy được, theo quy tắc Excel.

## 8. AI CHIẾN ĐẤU VÀ NHÓM HỎA LỰC

Triển khai sheet `12_Nhom_hoa_luc`.

Tách các hệ thống súng theo nhiệm vụ:
- Pháo chính ưu tiên mục tiêu bọc giáp nặng.
- Pháo phụ tấn công phương tiện và mục tiêu thích hợp.
- CIWS ưu tiên máy bay, drone và tên lửa.
- Súng trấn áp tạo áp lực bằng nhiều phát bắn sát thương thấp.
- Bom và vũ khí diện rộng có khu vực cảnh báo.

Hạn chế số nhóm súng đồng thời nhắm cùng một mục tiêu, sử dụng góc bắn thực tế và thời gian khai hỏa lệch pha.

Không cho toàn bộ 15–22 tháp pháo cùng lúc bắn tập trung vào một xe tăng, trừ khi đó là một cơ chế đặc biệt đã được quy định và cân bằng rõ ràng.

## 9. CHUYỂN PHA DUY NHẤT Ở 50% HP

Triển khai `13_Pha_AI` với quy tắc bắt buộc:

**Mỗi boss chỉ có một mốc chuyển pha tại 50% HP, kích hoạt tối đa một lần trong trận.**

- Không giữ các mốc cũ 60%, 25% hoặc các mốc khác.
- Không cộng chồng nhiều buff damage và tốc bắn từ hệ thống cũ.
- Ở 50% HP, boss đổi hành vi chiến đấu theo Excel.
- Bổ sung hoạt ảnh/hiệu ứng báo hiệu chuyển pha nếu asset cho phép.
- Phải xử lý trường hợp một phát bắn làm HP vượt qua ngưỡng 50%.
- Chuyển pha không được kích hoạt lại do hồi máu, load game hoặc thay đổi trạng thái.

Nếu boss có các sự kiện nhiệm vụ theo HP, kiểm tra riêng để bảo toàn logic nhiệm vụ mà vẫn chỉ có một pha boss.

## 10. TẠO 6 MINI-BOSS MỚI

Triển khai các mẫu trong `05_Mini_boss_moi`:

1. Roc Arsenal (`roc_gunship`)
2. Daedalus Assault (`daedalus_assault`)
3. Icarus Sentinel
4. Matriarch Wasp
5. Jötunn Mortar
6. Bastion Flak

Lấy **ID chính xác và cấu hình chi tiết từ Excel**, không tự suy đoán ID còn thiếu.

Mỗi mini-boss phải:
- Có ngoại hình, bố trí vũ khí hoặc phong cách chiến đấu khác boss gốc.
- Có AI, HP, damage, tốc bắn và giới hạn triệu hồi riêng.
- Kế thừa chassis hoặc asset gốc khi phù hợp.
- Có hardpoint và liên kết prefab/model hợp lệ.
- Không có siêu vũ khí ngang sức boss chính nếu thiết kế không cho phép.
- Không làm hỏng các mini-boss cũ.

## 11. KIỂM THỬ

Sau khi triển khai, thực hiện kiểm thử theo `06_QA_Nguong` và `14_Kiem_thu`.

Bắt buộc kiểm tra:

- Boss và mini-boss cũ vẫn spawn bình thường.
- Sáu mini-boss mới được đăng ký dữ liệu hợp lệ.
- HP đúng theo Excel và không bị nerf trùng.
- Tổng DPS đúng giới hạn mục tiêu.
- Bom khí cầu không còn tiêu diệt hàng loạt xe tăng khỏe quá dễ dàng.
- Kraken ít súng hơn Leviathan và có cơ chế phóng máy bay.
- Phá boong Kraken chặn máy bay mới.
- Phá hangar Roc/Matriarch/Icarus chặn drone hoặc phi thuyền mới.
- Phá cửa/khoang đổ bộ boss mặt đất chặn quân mới.
- Quân đã triệu hồi không tự biến mất chỉ vì nguồn triệu hồi bị phá.
- Boss chỉ chuyển pha đúng một lần tại 50% HP.
- Không có bộ phận radar/tháp chỉ huy có thể phá hủy.
- Súng mới không bắn xuyên thân boss, sai hướng hoặc ngoài góc bắn.
- Không gây suy giảm FPS nghiêm trọng khi nhiều pháo và đơn vị triệu hồi cùng hoạt động.
- Không hỏng save/load, màn chơi, chiến dịch hoặc Boss Hunt.

Nếu không thể chạy game tự động, hãy thực hiện các bài test dữ liệu/code khả thi và cung cấp hướng dẫn kiểm thử thủ công; không được báo đã pass những bài test chưa chạy.

## 12. TRÌNH TỰ THỰC HIỆN

**Giai đoạn A – Phân tích**

Đọc toàn bộ Excel và source code, tạo bảng đối chiếu giữa thiết kế và code hiện tại. Xác định dữ liệu và hệ thống nào có thể tái sử dụng.

**Giai đoạn B – Cân bằng**

Sửa HP, damage, tốc bắn, bom/AoE và ngân sách DPS.

**Giai đoạn C – Vũ khí**

Bổ sung hardpoint, vũ khí, hệ thống nhóm hỏa lực và AI chọn mục tiêu.

**Giai đoạn D – Triệu hồi và bộ phận**

Thêm triệu hồi định kỳ, giới hạn quân, module triển khai có thể phá hủy và hiệu ứng tương ứng.

**Giai đoạn E – Pha chiến đấu**

Chỉ giữ một mốc 50% HP và cập nhật hành vi từng boss.

**Giai đoạn F – Mini-boss mới**

Tạo 6 mini-boss theo Excel, đăng ký dữ liệu và tích hợp vào các chế độ chơi phù hợp.

**Giai đoạn G – Kiểm thử**

Chạy kiểm thử, sửa lỗi, đối chiếu từng Boss ID với Excel và đánh giá hiệu năng.

## 13. KẾT QUẢ PHẢI BÀN GIAO

Sau khi hoàn thành, hãy cung cấp:

1. Danh sách file code và dữ liệu đã thay đổi.
2. Bảng đối chiếu từng boss: HP trước/sau, số bệ trước/sau, damage/tốc bắn và khả năng triệu hồi.
3. Danh sách 6 mini-boss mới cùng trạng thái tích hợp.
4. Danh sách cơ chế đã triển khai và những phần chưa thể hoàn thành do thiếu asset hoặc API.
5. Kết quả kiểm thử thực tế, lỗi đã sửa và các vấn đề còn tồn tại.

**Không được chỉ trả về kế hoạch hoặc mô tả giải pháp. Hãy trực tiếp sửa source code trong dự án, triển khai theo các giai đoạn và kiểm tra kết quả.**

Ưu tiên tính đúng đắn, bảo toàn dữ liệu và tính nhất quán với Excel. Không tuyên bố đã hoàn thành nếu còn cơ chế quan trọng chưa hoạt động.

**MỤC TIÊU CUỐI CÙNG:** Machine Brigade có những boss khổng lồ với rất nhiều tháp pháo, phi đội, drone và xe cơ giới; các trận đánh đẹp mắt, khác biệt, có chiến thuật phá bộ phận rõ ràng, nhưng HP và damage được cân bằng để người chơi không phải chịu những trận quá dài hoặc chết tức thì một cách bất công.
</pasted_content id="e0cc">

