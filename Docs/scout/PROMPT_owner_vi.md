# 10/10 owner prompt (verbatim): no Fog of War, scout Target Designation, stealth



<pasted_content id="e0cc">
# MACHINE BRIGADE — BỎ FOG OF WAR, HOÀN THIỆN SCOUT TARGET DESIGNATION & STEALTH

## 0. Mục tiêu

Bạn là senior Unity/C# gameplay engineer, AI engineer và game balance designer, làm việc trực tiếp trên repository Machine Brigade.

Game là RTS/auto-battler 3D dành cho mobile, sử dụng Unity URP, simulation deterministic ở 20 tick/giây, có hệ thống AI tự điều khiển phương tiện, đội hình, chọn mục tiêu, mua quân, triển khai và gọi hỏa lực.

**Yêu cầu chính:**

1. Không triển khai Fog of War.
2. Bỏ các phần Fog of War nếu đã tồn tại nhưng không còn cần thiết.
3. Giữ bản đồ và đơn vị địch hiển thị đầy đủ cho người chơi.
4. Giữ hệ thống `vision`, stealth, radar, phát hiện tàng hình và các cơ chế chiến đấu hiện có nếu chúng vẫn phục vụ gameplay.
5. Chuyển vai trò scout sang hỗ trợ hỏa lực bằng cơ chế **Target Designation — Chỉ thị mục tiêu**.
6. Scout tự động đánh dấu mục tiêu nguy hiểm để quân đồng minh gây thêm sát thương.
7. Không thêm cơ chế giảm độ tản hoặc tăng độ chính xác pháo cho scout.
8. Không thay đổi hệ thống đường đạn, độ tản, dẫn bắn, vận tốc đạn hoặc thời gian bay hiện tại.
9. Bảo đảm stealth tiếp tục có tác dụng chiến thuật ngay cả khi quân địch luôn hiển thị.
10. Duy trì hiệu năng mobile, deterministic simulation và cân bằng các chế độ chơi.

**Không được bắt đầu bằng việc viết hệ thống mới. Phải audit source hiện tại để xác định những cơ chế đã có và có thể tái sử dụng.**

## 1. Quy trình bắt buộc: kiểm tra source trước

Đọc trực tiếp source code và dữ liệu trong repository.

Ưu tiên kiểm tra:

- `Assets/MachineBrigade/Scripts/Sim/`
- `Assets/MachineBrigade/Scripts/Sim/AI/`
- `Assets/MachineBrigade/Scripts/Sim/AI/P2/`
- `Assets/MachineBrigade/Scripts/Game/Match/`
- `Assets/MachineBrigade/Resources/Data/balance.json`
- `Assets/MachineBrigade/Resources/Data/tunables.json`
- Các hệ thống simulation, target acquisition, weapon targeting, damage, stealth, radar, reveal, minimap và HUD.
- Các tests và công cụ đo cân bằng hiện có.

Các đường dẫn trên là điểm tìm kiếm ban đầu; phải xác minh file và class thực tế.

Kiểm tra toàn bộ những khái niệm sau:

`vision`, `stealth`, `reveal_stealth`, `reveal_air`, `radar`, `jammer`, `spot_aura`, `target`, `mark`, `status`, `damage`, `target priority`, `guard_tower`, `missile_battery`, `recon_drone`, `scout_jeep`, `scout_heli`.

Đặc biệt xác định:

- Cách simulation tính tầm nhìn và mục tiêu có thể bị tấn công.
- Điều kiện stealth bị phát hiện.
- Hành vi radar phòng không.
- Vai trò hiện tại của scout.
- Các trạng thái đánh dấu mục tiêu đã tồn tại.
- AI chọn mục tiêu và điều khiển đội scout như thế nào.
- Vị trí chính xác của bước áp dụng sát thương lên mục tiêu.
- Khác biệt giữa sát thương trực tiếp, sát thương nổ lan, DOT và sát thương từ kỹ năng.
- Cách dữ liệu cấu hình được nạp vào simulation.
- Những hệ thống vision nào vẫn cần thiết sau khi bỏ Fog of War.

### Báo cáo audit

Trước khi sửa, tạo bảng:

| Hệ thống | File/class thực tế | Hiện có | Cần sửa | Lý do |
|---|---|---|---|---|

Phân biệt ba trường hợp:

- Đã có đầy đủ: tái sử dụng.
- Đã có một phần: mở rộng tối thiểu.
- Chưa có: chỉ tạo phần thực sự cần thiết.

Không viết lại hệ thống đã hoạt động tốt.

## 2. Không triển khai Fog of War

Quy tắc hiển thị:

- Toàn bộ địa hình luôn hiển thị.
- Tất cả đơn vị địch đang tồn tại đều có thể được người chơi nhìn thấy trên chiến trường.
- Minimap hiển thị quân hai phe theo các quy tắc HUD bình thường.
- Không cần khám phá bản đồ.
- Không cần Fog Mask.
- Không cần last-known contact.
- Không cần contact uncertainty.
- Không cần radar blip giả.
- Không cần các cấp thông tin Unknown/Detected/Tracked.

Loại bỏ các đoạn mã chỉ dành riêng cho Fog of War nếu chúng tồn tại và không còn được hệ thống khác sử dụng.

**Không được xóa `vision` hoặc radar một cách máy móc.** Những cơ chế này có thể vẫn cần thiết cho khóa mục tiêu, stealth, phòng không, AI hoặc hiệu ứng đặc biệt.

Phân biệt rõ:

- Visibility của giao diện.
- Khả năng phát hiện và khóa mục tiêu của simulation.

Việc người chơi nhìn thấy một xe không có nghĩa mọi đơn vị đồng minh đều có thể bắn xe đó.

Không làm thay đổi hành vi chiến đấu hiện tại ngoài các yêu cầu được nêu trong prompt.

## 3. Target Designation — Chỉ thị mục tiêu

### 3.1. Nguyên tắc

Các đơn vị trinh sát tự động đánh dấu mục tiêu địch có giá trị chiến thuật.

Khi mục tiêu bị đánh dấu, sát thương hợp lệ do đơn vị thuộc phe scout gây lên mục tiêu đó được tăng.

Không yêu cầu người chơi thao tác thủ công.

Không thêm nút mới trên HUD.

Không yêu cầu scout phải trực tiếp tấn công mục tiêu.

### 3.2. Cấu hình ban đầu

| Thuộc tính | Giá trị đề xuất |
|---|---|
| `damageBonus` | 0.10 (+10%) |
| `bossDamageBonus` | 0.05 (+5%) |
| `markDurationSeconds` | 5 |
| `retargetIntervalSeconds` | 2 |
| `maxTargetsPerScout` | 1 |
| `stacking` | false |
| `applyToSelf` | false |
| `applyToAlliedTeams` | false |
| `affectsDirectDamage` | true |
| `affectsSplashDamage` | false |
| `affectsDamageOverTime` | false |
| `affectsSelfDamage` | false |
| `affectsFriendlyFire` | false |

Các giá trị này là cấu hình thử nghiệm mới, không được coi là số đang có trong source.

Nếu source đã có một cơ chế đánh dấu tương đương, ưu tiên tái sử dụng, tránh tạo hai debuff cùng chức năng.

### 3.3. Luật sát thương

Một mục tiêu bị scout phe A đánh dấu:

- Đơn vị phe A tấn công trực tiếp được +10% sát thương hợp lệ lên mục tiêu đó.
- Scout không tự nhận bonus từ dấu do chính nó tạo.
- Phe B không hưởng lợi từ dấu của phe A.
- Nhiều scout phe A cùng đánh dấu vẫn chỉ được một bonus.
- Bonus chỉ áp dụng đúng mục tiêu được đánh dấu.
- Không tăng sát thương lên các mục tiêu xung quanh do nổ lan.
- Boss chỉ nhận bonus +5%.
- Không ảnh hưởng sát thương của môi trường, tự hủy, va chạm hoặc đòn script không có nguồn sát thương hợp lệ.

Đối với vũ khí có cả sát thương trực tiếp và nổ lan:

**Chỉ phần sát thương trực tiếp lên mục tiêu đánh dấu được tăng.**

Không nhân toàn bộ vụ nổ lên +10%.

Nếu đường xử lý damage hiện tại không phân biệt hai thành phần này rõ ràng, phải phân tích và bổ sung điều kiện tại vị trí thích hợp, không nhân bonus ở một bước tổng khiến nổ lan bị tăng ngoài ý muốn.

### 3.4. Thứ tự áp dụng sát thương

Kiểm tra pipeline hiện tại.

Đặt Target Designation ở bước thích hợp sao cho:

- Không phá giáp có hướng.
- Không thay đổi bảng xuyên giáp.
- Không tác động hai lần qua crit, status hoặc damage modifier khác.
- Không phá APS, khiên và phòng vệ.
- Không làm mất thông tin damage source.
- Không áp bonus sau khi damage đã được ghi nhận và không thể phân biệt nguồn.

Phải document thứ tự nhân hệ số trong code và kiểm thử.

## 4. Scout tự động chọn mục tiêu

Scout cần chọn mục tiêu theo thứ tự ưu tiên chiến thuật, không đơn giản chỉ chọn mục tiêu gần nhất.

Ưu tiên chung:

1. Kẻ địch đang gây nguy hiểm trực tiếp cho đội hình được scout hỗ trợ.
2. Pháo binh hoặc đơn vị hỏa lực tầm xa nguy hiểm.
3. Xe phòng không có khả năng đe dọa UAV hoặc scout heli.
4. Xe tăng hạng nặng, xe tinh nhuệ.
5. Xe hỗ trợ quan trọng.
6. Các mục tiêu khác trong phạm vi.

Thứ tự thực tế có thể thay đổi theo vai trò scout và tình hình chiến đấu.

Yêu cầu:

- Chỉ chọn mục tiêu sống, hợp lệ, thuộc phe đối phương.
- Không đánh dấu công trình không thể tấn công.
- Không chọn mục tiêu ngoài phạm vi.
- Không liên tục đổi mục tiêu mỗi tick.
- Ưu tiên giữ mục tiêu hiện tại nếu nó vẫn phù hợp.
- Cho phép chuyển sang mục tiêu nguy hiểm hơn theo ngưỡng điểm.
- Không giữ dấu vĩnh viễn sau khi scout chết.
- Không phụ thuộc render hoặc vị trí camera.

Tái sử dụng hệ thống scoring và target priority hiện tại nếu phù hợp.

## 5. Khác biệt giữa các scout

Kiểm tra chính xác những đơn vị hiện có và thống nhất ID theo catalog.

Cấu hình thử nghiệm:

| Đơn vị | Tầm đánh dấu | Số mục tiêu | Vai trò |
|---|---:|---:|---|
| `scout_jeep` | 35 m | 1 | Chỉ thị mục tiêu mặt đất |
| `recon_drone` | 55 m | 1 | Chỉ thị mục tiêu giá trị cao từ trên không |
| `scout_heli` | 45 m | 1 | Chỉ thị cơ động, ưu tiên phòng không và pháo binh |

Không tạo đơn vị mới.

Không thay đổi CP, HP, tốc độ hoặc vũ khí trước khi đo hiệu quả.

Nếu các đơn vị trinh sát đã có khả năng đánh dấu mục tiêu thì cần đối chiếu và tránh cộng thêm cùng một lợi ích hai lần.

Nếu một ID không tồn tại, không tự ý tạo ID thay thế; tìm đúng ID thực tế trong catalog.

## 6. Thời gian tồn tại và chống spam

Scout cập nhật lựa chọn mục tiêu mỗi 2 giây.

Khi chọn được mục tiêu:

- Áp dụng dấu trong 5 giây.
- Nếu vẫn hợp lệ, có thể làm mới thời gian.
- Nếu đổi mục tiêu, dấu do scout đó duy trì ở mục tiêu cũ phải được thu hồi theo luật sở hữu dấu.
- Nếu scout chết, không còn làm mới dấu.
- Nếu scout rời phạm vi, không còn làm mới dấu.
- Dấu cũ tự hết hạn, không tồn tại vô hạn.

Nếu nhiều scout cùng đánh dấu một mục tiêu:

- Bonus không cộng dồn.
- Việc một scout chết không được xóa dấu hợp lệ của scout khác.
- Phải quản lý thời gian và nguồn dấu chính xác.

Ưu tiên cấu trúc dữ liệu nhỏ, không cấp phát bộ nhớ liên tục mỗi tick.

## 7. AI chọn mục tiêu

Scout không chỉ tạo debuff mà cần giúp đội quân tập trung hỏa lực hợp lý.

Khi một mục tiêu đang được đánh dấu:

- AI đồng minh có thể tăng điểm ưu tiên mục tiêu đó.
- Không bắt AI bỏ mục tiêu đang đánh để chuyển ngay.
- Không cho phép bắn ngoài tầm vũ khí.
- Không bỏ qua điều kiện quay tháp, tầm tối thiểu, loại mục tiêu hoặc giới hạn vũ khí.
- Không ưu tiên một mục tiêu mà đơn vị không thể gây sát thương hiệu quả.

Ưu tiên tận dụng hệ thống đánh giá mục tiêu hiện có.

Đề xuất:

`markedTargetPriorityMultiplier = 1.10`

Chỉ áp dụng nếu có lợi cho việc chọn mục tiêu.

Không cộng trực tiếp bonus AI với bonus damage thành một hệ số sát thương thứ hai.

Đối với pháo binh, giữ nguyên logic bắn, quỹ đạo, dẫn bắn và độ tản hiện tại.

## 8. AI điều khiển scout

Kiểm tra hành vi scout trong hệ thống AI đội hình.

Scout là đơn vị hỗ trợ, không được mặc định hành xử như xe tăng chủ lực.

Yêu cầu:

- Scout Jeep ưu tiên đi cùng hoặc hơi trước đội chính, nhưng không lao sâu vào cụm xe tăng.
- Recon Drone ưu tiên vị trí còn sống sót và vẫn có thể chỉ thị mục tiêu.
- Scout Heli hạn chế áp sát cụm phòng không khi không cần thiết.
- Không rút lui chỉ vì HP thấp nếu luật AI hiện tại đã cấm rút lui theo ngưỡng máu.
- Không làm hỏng hệ thống tìm đường, đội hình hoặc tránh vật cản.
- Không tạo AI trinh sát riêng nếu hệ thống vai trò hiện tại đủ khả năng mở rộng.

Chỉ thêm các điều kiện thực sự cần thiết.

## 9. Stealth khi không có Fog of War

Không được xóa hệ stealth.

Người chơi luôn thấy model địch, nhưng hệ thống chiến đấu vẫn áp dụng phát hiện và khóa mục tiêu theo luật stealth.

Giữ:

- Stealth khó bị khóa ở khoảng cách xa.
- Các đơn vị có `reveal_stealth` tiếp tục khắc chế stealth.
- Radar và phòng không tuân thủ phạm vi phát hiện của chúng.
- Khi stealth khai hỏa, sử dụng đúng luật lộ diện hiện có.
- Đòn đánh đã phóng vẫn hoạt động theo luật dẫn đường và phòng vệ hiện tại.

Không tự thêm:

- Né đạn theo tỷ lệ ngẫu nhiên.
- Giảm sát thương nhận vô điều kiện.
- Bất tử khi chưa bắn.
- Bonus sát thương tấn công đầu.
- Thời gian tàng hình hoặc lộ diện mới chưa được xác nhận là cần thiết.

Audit các đơn vị stealth hiện có, bao gồm máy bay tàng hình và những biến thể khác trong roster.

Chỉ đề xuất thay đổi nếu phép đo cho thấy stealth mất vai trò chiến thuật khi bỏ Fog of War.

## 10. Radar và tháp canh

Giữ nguyên các vai trò chiến đấu đang hoạt động:

- Radar phòng không.
- Phát hiện stealth.
- Aura hỗ trợ tháp.
- Phản pháo.
- Các tác dụng riêng của nhánh nâng cấp.

Không mặc định biến radar thành nguồn Target Designation.

Không bổ sung aura tăng damage toàn quân vào radar.

Không tăng thêm chỉ số cho guard tower trước khi đánh giá tác dụng hiện tại.

Các radar trung lập không còn giá trị nếu chỉ tăng tầm nhìn thì cần được audit và đề xuất chuyển đổi riêng. Không tự ý thay đổi chúng trong nhiệm vụ này nếu ảnh hưởng mục tiêu chiếm cứ điểm, chiến dịch hoặc AI.

## 11. HUD và VFX mobile

Khi mục tiêu bị đánh dấu, hiển thị một biểu tượng ngắm đỏ nhỏ phía trên mục tiêu.

Yêu cầu:

- Không che thanh máu.
- Không che model quá nhiều.
- Không thêm hiệu ứng particle nặng.
- Không tạo một GameObject UI mới cho từng lần refresh.
- Dùng pooling hoặc cơ chế HUD marker hiện có.
- Giới hạn marker theo camera/LOD nếu cần.
- Chỉ hiện một biểu tượng dù có nhiều scout đánh dấu.
- Không làm minimap quá nhiều icon.

Tooltip tiếng Việt:

**Chỉ thị mục tiêu:** Mục tiêu nhận thêm 10% sát thương trực tiếp từ đồng minh của đơn vị trinh sát. Không cộng dồn.

Tooltip boss tương ứng +5%.

Hiệu ứng nên rõ ràng nhưng không gây rối khi nhiều đơn vị giao chiến.

## 12. Dữ liệu và khả năng cân bằng

Đưa các thông số mới vào hệ thống dữ liệu hiện có thay vì hardcode.

Tối thiểu cần cấu hình được:

- Bonus damage.
- Bonus lên boss.
- Phạm vi đánh dấu theo scout.
- Thời gian tồn tại.
- Chu kỳ cập nhật.
- Số mục tiêu tối đa.
- Hệ số ưu tiên mục tiêu.
- Quy tắc cộng dồn.
- Nhóm sát thương được áp dụng.

Tuân thủ cấu trúc `balance.json`, `tunables.json` và quy trình chỉnh dữ liệu đang có trong repository.

Không tự ý thay đổi schema hoặc thêm một hệ config song song.

## 13. Deterministic simulation và hiệu năng

Machine Brigade chạy simulation cố định 20 tick/giây.

Tất cả logic Target Designation phải chạy trong simulation.

Không phụ thuộc vào:

- Frame rate.
- `Time.deltaTime` của Unity renderer.
- Unity physics không deterministic nếu simulation hiện tại không sử dụng.
- Thứ tự dictionary không ổn định.
- Random không có seed.
- Camera và trạng thái giao diện.

Với các giá trị ban đầu:

- 2 giây = 40 simulation ticks.
- 5 giây = 100 simulation ticks.

Dùng tick thay cho thời gian thực ở trạng thái mô phỏng.

Yêu cầu tối ưu:

- Không scan toàn bộ đơn vị mỗi frame nếu không cần.
- Tái sử dụng spatial query hiện có.
- Tránh LINQ và allocation trong vòng lặp chiến đấu nóng.
- Không phát sinh hiệu ứng UI trùng lặp.
- Không làm tăng đáng kể thời gian xử lý AI hoặc damage.

## 14. Kiểm thử bắt buộc

### Unit tests

Kiểm tra:

1. Một scout đánh dấu một mục tiêu → +10% direct damage.
2. Hai scout cùng đánh dấu → vẫn +10%.
3. Scout phe A không tăng sát thương phe B.
4. Scout không hưởng bonus từ dấu tự tạo.
5. Boss nhận +5%.
6. Sát thương nổ lan không nhận bonus.
7. Damage over time không nhận bonus.
8. Mục tiêu chết → dấu được thu hồi.
9. Scout chết → dấu hết hạn chính xác.
10. Scout đổi mục tiêu → không để lại dấu vô hạn.
11. Hai scout cùng đánh dấu, một scout chết → dấu của scout còn sống vẫn hợp lệ.
12. Mục tiêu ngoài tầm → không được làm mới dấu.
13. AI không tấn công mục tiêu ngoài tầm chỉ vì đã được đánh dấu.
14. Stealth giữ nguyên hành vi chiến đấu.
15. Simulation replay cùng seed → cùng state hash.

### Gameplay tests

Đo cùng seed, cùng bản đồ, cùng đối thủ:

- Đội hình không scout.
- Đội hình có Scout Jeep.
- Đội hình có Recon Drone.
- Đội hình có Scout Heli.
- Đội hình có hai scout cùng loại.
- Đội hình có nhiều loại scout.

Phải tính cả CP mà scout chiếm dụng.

Các chỉ số:

- Damage thực tế.
- Damage/CP.
- Thời gian tiêu diệt.
- Số mục tiêu đánh dấu.
- Tổng thời gian đánh dấu có tác dụng.
- Tỷ lệ sống sót của scout.
- Tỷ lệ thắng.
- Thời lượng trận.

Kiểm tra ít nhất các kiểu địch:

- Đội xe nhẹ.
- Đội xe tăng hạng nặng.
- Đội pháo binh.
- Đội phòng không và máy bay.
- Đội công thành/căn cứ.
- Boss.

Nếu scout quá mạnh hoặc quá yếu, báo cáo số liệu và đề xuất cân bằng; không tự ý nâng quá mức bonus ban đầu mà không có kết quả đo.

## 15. Regression tests

Chạy những tests hiện có liên quan tới:

- Combat và damage.
- Armour/penetration.
- Splash.
- APS và shield.
- Stealth và radar.
- AI targeting.
- Unit roles và đội hình.
- Replay hash.
- Campaign.
- Boss.
- Minimap/HUD.

Đặc biệt chú ý các trường hợp:

- Boss có nhiều bộ phận.
- Đạn có cả direct hit và area damage.
- Tên lửa và drone dẫn đường.
- Pháo binh bắn loạt.
- Laser và railgun.
- Đơn vị hỗ trợ không có vũ khí.
- Đơn vị được thả dù hoặc hồi sinh.
- Tháp được xây lại.
- Đổi quyền sở hữu đơn vị hoặc công trình.

Không được cập nhật replay baseline chỉ để che một regression không giải thích được.

## 16. Phạm vi không được tự ý thay đổi

Không:

- Triển khai Fog of War.
- Thêm radar contact system.
- Thêm hệ thống sương shader.
- Thay đổi độ tản pháo.
- Thay đổi quỹ đạo đạn.
- Làm đạn tự động trúng đích.
- Thay đổi toàn bộ AI chỉ huy.
- Cân bằng lại tất cả phương tiện.
- Thay đổi CP không có số liệu.
- Thay đổi stealth nếu chưa có bằng chứng cần thiết.
- Thêm cơ chế trinh sát thủ công.
- Tạo thêm thao tác UI trên mobile.
- Thay đổi luật chiến dịch ngoài phạm vi.
- Thay đổi hệ thống kinh tế và tiến trình mở khóa.
- Ghi đè hoặc xóa hệ thống cũ khi chưa kiểm tra phụ thuộc.

## 17. Quy trình triển khai

Thực hiện theo thứ tự:

**Bước A — Audit**

Kiểm tra source, xác định chính xác những gì đã có và phần cần thay đổi.

**Bước B — Thiết kế kỹ thuật**

Chọn vị trí lưu trạng thái mark, đường xử lý damage, đường cập nhật scout và các điểm tích hợp AI.

Tái sử dụng hệ thống hiện tại tối đa.

**Bước C — Implement**

Sửa mã, dữ liệu, localization và HUD.

**Bước D — Tests**

Chạy unit tests, deterministic replay và regression tests.

**Bước E — Balance**

Đo giá trị thực chiến trước và sau, ưu tiên đánh giá hiệu quả trên CP.

**Bước F — Báo cáo**

Trình bày:

1. Danh sách file đã sửa.
2. Các cơ chế hiện có được tái sử dụng.
3. Các class/hàm mới hoặc đã chỉnh sửa.
4. Dữ liệu và tham số mới.
5. Những phần Fog of War đã loại bỏ, nếu có.
6. Kết quả unit tests và replay.
7. Số liệu cân bằng trước/sau.
8. Vấn đề chưa giải quyết.
9. Các thay đổi ngoài phạm vi được đề xuất nhưng chưa áp dụng.

## 18. Tiêu chí nghiệm thu

Chỉ xem là hoàn tất khi:

- Người chơi thấy toàn bộ chiến trường và quân địch.
- Không có cơ chế khám phá bản đồ.
- Scout tự động chỉ thị mục tiêu đúng phạm vi.
- Mục tiêu nhận đúng +10% direct damage, boss +5%.
- Bonus không cộng dồn.
- Không tăng splash damage hoặc DOT.
- Pháo binh giữ nguyên độ tản, đường đạn và logic bắn hiện tại.
- Stealth vẫn hoạt động và có khắc chế.
- AI không spam chuyển mục tiêu.
- Scout không thường xuyên lao vào vị trí tự sát do logic mới.
- HUD hiển thị rõ và gọn trên mobile.
- Simulation deterministic.
- Tests liên quan vượt qua.
- Không có regression nghiêm trọng.

**Mục tiêu cuối cùng: Machine Brigade không cần Fog of War để tạo chiến thuật. Scout mang lại lợi thế phối hợp hỏa lực, stealth mang lại lợi thế tiếp cận và sinh tồn; cả hai dễ hiểu, tự động và phù hợp một game chiến đấu quy mô lớn trên mobile.**

Hãy bắt đầu bằng audit source thật, không giả định rằng các tính năng trong tài liệu đã được triển khai đầy đủ. Sau audit, thực hiện các thay đổi phù hợp và báo cáo kết quả kiểm chứng thực tế, không chỉ dừng ở kế hoạch.
</pasted_content id="e0cc">

