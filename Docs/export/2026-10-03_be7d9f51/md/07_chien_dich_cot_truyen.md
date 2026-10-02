# 07_chien_dich_cot_truyen — Chiến dịch và cốt truyện

Bộ xuất dữ liệu Machine Brigade, commit be7d9f51, ngày 2026-10-03. Sinh bởi `python Tools/export/export.py` (lượt 6): bảng in đúng ô của csv / xlsx; văn bản lấy từ tài liệu thiết kế (Tools/docs) và chuỗi trong game. Toàn văn: Machine_Brigade_Design_FULL_2026-10-03.md.

Chương, nhiệm vụ (giai đoạn, quân, radio, biến cố, trạng thái nav), thoại (mỗi câu một dòng), nhân vật, trigger, bộ bài game, thư viện biến cố, phát hành, kịch bản gốc

Mục trong file này: 3. Chiến dịch; 3b. Bộ bài game; 3c. Biến cố và sự kiện trong nhiệm vụ; 4. Nhiệm vụ nhiều giai đoạn.

## 3. Chiến dịch

Trạng thái: Đã áp

Nguồn dữ liệu: 07_chien_dich_cot_truyen/Chuong; 07_chien_dich_cot_truyen/Nhiem_vu; 07_chien_dich_cot_truyen/Nhan_vat; 07_chien_dich_cot_truyen/Thoai; 07_chien_dich_cot_truyen/Trigger_thoai; 05_che_do_kinh_te/Sao_chien_dich; 07_chien_dich_cot_truyen/Phat_hanh. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §3. Chiến dịch.

**Bối cảnh:** tương lai gần, một vùng duyên hải hư cấu. Tập đoàn quân sự tư nhân **Hegemon** chiếm vùng này và chạy các chương trình vũ khí thử nghiệm: Behemoth, bầy drone và Dự án Icarus. Người chơi chỉ huy **Lữ đoàn Cơ giới 7** (Machine Brigade) của Liên minh Duyên hải.

**Cấu trúc:** 15 chương trong 4 hồi, 193 nhiệm vụ (174 chính, 19 phụ). Mỗi chương có 10 nhiệm vụ chính và 2 nhiệm vụ phụ; nhiệm vụ 5 là boss giữa chương, nhiệm vụ 10 là chiến dịch lớn nhiều giai đoạn (15–25 phút, riêng trận cuối game tới 30 phút). Không hai nhiệm vụ nào trên cùng một bản đồ có cùng cấu hình: mỗi lần quay lại đổi ít nhất 2 yếu tố (hướng xuất phát, vị trí căn cứ, thời tiết/đêm, vùng chơi, loại mục tiêu, phe giữ căn cứ). Trình tạo dữ liệu (Tools/campaign) tự kiểm tra luật này và luật không nhiệm vụ nào đòi thẻ chưa mở.

#### Nhân vật

| Nhân vật | Vai trò | Tiểu sử |
|---|---|---|
| **Đại tá Marcus Kade** | Chỉ huy 7th Mechanized Brigade · biệt danh Iron | Kade chỉ huy lữ đoàn ngoài chiến trường và trên sóng bộ đàm. Điềm tĩnh, thực dụng, chưa ai nghe ông lớn tiếng. Ông tin lữ đoàn hơn tin bất kỳ chính trị gia nào, và lên kế hoạch trận đánh như thợ máy… |
| **Kỹ sư Mara Lind** | Kỹ sư trưởng, phụ trách căn cứ | Mara giữ cho căn cứ vận hành và ký duyệt mọi lần nâng cấp sở chỉ huy. Trước chiến tranh, cô là kỹ sư trong chương trình Behemoth của Hegemon; bản nguyên mẫu đầu tiên là của cô. Khi thấy chúng được là… |
| **Trung úy Jonah Reyes** | Chỉ huy không quân · biệt danh Hawk | Jonah Reyes, biệt danh Hawk, lái mọi thứ biết cất cánh của lữ đoàn. Trẻ, ồn ào, liều lĩnh, và giỏi hơn những gì anh chịu nhận. Raven đã bắn hạ đồng đội bay cũ của anh trên vùng biển này, và từ đó Haw… |
| **Đại úy Nadia Kerr** | Sĩ quan tình báo | Nadia đọc thư của Hegemon. Bản chặn thu, ổ cứng thu được, một cuốn sổ cháy dở: cô biến tất cả thành mục tiêu, thành những nhiệm vụ phụ không ai có thời gian làm, và thành những câu hỏi không ai muốn… |
| **Tướng Roland Thorne** | Tư lệnh đạo quân lớn nhất của Accord · biệt danh Titan | Thorne chỉ huy đạo quân đồng minh lớn nhất của Accord và thắng nhiều trận hơn bất kỳ ai bên ta. Dũng cảm, hào phóng với lính của mình, và mệt mỏi theo một cách không ai giải thích được. Ông sát cánh… |
| **Tướng Viktor Varga** | Thiết giáp Hegemon; cha đẻ của Behemoth · biệt danh Anvil | Varga già, kiêu hãnh và trọng danh dự, và ông yêu những cỗ máy của mình như người ta yêu con. Ông chế tạo Behemoth và chưa bao giờ hết tin vào sức nặng. Ông tôn trọng một đối thủ xứng tầm, và ông đã… |
| **Đại tá Ilya Orlov** | Pháo binh Hegemon · biệt danh Winter | Orlov chưa từng nhìn mặt người nào ông ta giết, và ông ta muốn thế. Lạnh lùng, kiên nhẫn, chính xác, ông ta thích thắng từ khoảng cách đối thủ không nhìn thấy mình. Căn cứ của ông ta là những trận đị… |
| **Đô đốc Magnus Kessler** | Hậu cần và hải quân Hegemon · biệt danh Maelstrom | Kessler điều hành bến cảng, đường sắt và tàu chiến của Hegemon, và ông ta điều hành chiến tranh như một bảng cân đối: mỗi viên đạn là một khoản chi, mỗi thành phố là một tài sản. Ông ta chưa từng để… |
| **Tiến sĩ Elara Venn** | Drone của Hegemon; người tạo ra Hive · biệt danh Queen | Venn tạo ra bầy drone như người khác đan len. Bà thiết kế Hive làm hệ thống cứu hộ cho vùng thảm họa, để tìm người còn sống dưới đống đổ nát; Aurel vũ trang cho nó trước khi bà kịp uống xong ly cà ph… |
| **Kasimir Wolff** | Át chủ bài không quân Hegemon · biệt danh Raven | Kasimir Wolff, biệt danh Raven, chỉ huy không quân Hegemon từ Skyhold và có số lần hạ địch nhiều hơn cả phần còn lại cộng lại. Kiêu ngạo, tài giỏi, chán ngán bất kỳ ai chậm hơn mình. Hắn lái Morrigan… |
| **Giám đốc Lucien Aurel** | Người đứng đầu Hegemon; Dự án Icarus · biệt danh Sol | Aurel điều hành Dự án Icarus, một vũ khí quỹ đạo có thể tấn công bất kỳ điểm nào trên mặt đất. Ông ta tin rằng ai kiểm soát bầu trời sẽ kiểm soát thế giới, và nói về chiến tranh như kế toán nói về bá… |

#### Tướng địch là cấu hình AI

Mỗi tướng có bộ bài, thói quen gọi hỏa lực, kiểu căn cứ, ưu tiên xe tinh nhuệ, chân dung, câu khiêu khích và câu khi thua.

| Tướng | Kiểu căn cứ | Thế trận | Bộ bài đặc trưng | Hỏa lực | Ưu tiên tinh nhuệ |
|---|---|---|---|---|---|
| **Tướng Viktor Varga** | varga | Tấn công | Tăng nhẹ lội nước, Tăng chủ lực, Tăng hạng nặng, Pháo chống tăng tự hành, Xe chiến đấu bộ binh, Tăng phun lửa, Tăng hai nòng, Xe phóng drone FPV | Pháo kích, Không kích, Màn khói | Tank, Heavy |
| **Đại tá Ilya Orlov** | orlov | Phòng thủ | Pháo phản lực dẫn đường, Lựu pháo tự hành, Xe cối tự hành, Pháo phản lực hạng nặng, Xe tên lửa phòng không tầm trung, Tăng chủ lực, Pháo cao xạ tự hành, Xe radar phản pháo | Pháo kích, Tên lửa hành trình, UAV quét | Artillery |
| **Đô đốc Magnus Kessler** | kessler | Phòng thủ | Pháo xung kích bánh lốp, Xe chiến đấu bộ binh, Tăng chủ lực, Tăng hạng nặng, Xe tên lửa phòng không tầm trung, Xe phóng drone FPV, Xe rải mìn, Pháo phản lực dẫn đường | Mìn rải từ xa, Pháo kích, Màn khói |  |
| **Tiến sĩ Elara Venn** | sen | Tấn công | UAV tấn công, Xe phóng drone FPV, Xe phóng đạn lảng vảng, UAV trinh sát, Xe gây nhiễu điện tử, Xe chiến đấu bộ binh, Tăng chủ lực, Pháo cao xạ tự hành | UAV quét, Đòn SEAD, Sửa chữa | Drone |
| **Kasimir Wolff** | quaden | Tấn công | Trực thăng tấn công, Trực thăng vũ trang bọc giáp, Máy bay cường kích, Tiêm kích, UAV tấn công, Pháo cao xạ tự hành, Tăng chủ lực, Xe tên lửa phòng không tầm trung | Không kích, Đòn SEAD, Bom napalm | Air |
| **Tướng Roland Thorne** | aurel | Tấn công | Tăng chủ lực, Tăng hạng nặng, Siêu tăng, Xe hỗ trợ tăng, Xe chiến đấu bộ binh, Pháo cao xạ tự hành, Pháo phản lực dẫn đường, Pháo chống tăng tự hành | Pháo kích, Không kích, Tên lửa hành trình |  |
| **Giám đốc Lucien Aurel** | aurel | Tấn công | Tăng hạng nặng, Xe hỗ trợ tăng, Xe pháo điện từ, Trực thăng tấn công, Xe tên lửa phòng không tầm xa, Pháo phản lực hạng nặng, Siêu tăng, Tiêm kích | Tên lửa hành trình, Không kích, Bom napalm, Đòn SEAD |  |

#### Dòng thời gian

- Hai năm trước cuộc đổ bộ: chính quyền Meridian Coast sụp đổ. Một tập đoàn khai khoáng thuê Hegemon giữ trật tự, và Hegemon giữ luôn cả vùng.
- Lữ đoàn đổ bộ ở Stormbeach, dựng căn cứ đầu tiên ở Greenvale rồi đánh chiếm pháo đài Ashfield. Bastion gục ngã và thiếu tá Brandt đầu hàng. Hồ sơ của ông ta nhắc đi nhắc lại một cái tên: tướng Varga.
- Varga lộ diện ở Dunebreak. Nhà máy lọc dầu bốc cháy cùng Inferno bên trong, và ở Red Rock, với đạo quân của Thorne bên cạnh, Behemoth gục ngã. Đêm đó Mara kể với Kade nơi cô đã học cách chế tạo nó.
- Lữ đoàn làm mù tuyến radar của Orlov, bắn rơi Harpy và hạ Jötunn trước cổng Frostpeak. Orlov rút pháo về phía bắc. Câu cuối của ông ta trên bộ đàm: "Mùa đông luôn quay lại."
- Juggernaut bị lật, Tempest gục ngay trên cầu tàu của nó và bến cảng về tay ta. Kessler chạy ra biển, và ngoài khơi Beacon Bay, lữ đoàn chiếm các trận địa pháo bờ biển cũ rồi đánh chìm Leviathan. Kessler sống sót; hạm đội của ông ta thì không. Một cánh quân của Thorne đã không có mặt ở nơi đã hứa.
- Locust, Hive rồi Matriarch lần lượt rơi trên tán rừng đang cháy. Tiến sĩ Venn một mình bước ra khỏi xưởng drone, ra hàng cùng một ổ đĩa đề "Icarus", và bắt đầu làm việc cho Accord.
- Cuộc tổng phản công của Varga vỡ tan trước Hollow Dam. Trước đó, trong đúng một buổi sáng, Varga và Kade ngừng bắn để dân trong thung lũng kịp chạy; đó là lần duy nhất hai người nói chuyện với nhau. Moloch lao xuống hẻm sông. Quân của Thorne lại tới muộn.
- Veyra được giải phóng. Giữa trận cuối, căn cứ của Thorne quay pháo vào lữ đoàn; Nadia là người thấy đầu tiên và cứu được một nửa quân ta. Ta đánh ngược lại qua Atlas và chặn Nemesis ngay rìa trung tâm. Thorne trốn thoát cùng một phần ba đạo quân của Accord.
- Lữ đoàn đuổi theo Thorne vào Deepcut Mine. Tartarus và Ixion gục ngã, còn Kronos bị chặn lại trước khi tới căn cứ của ta. Thorne lại trốn thoát, ra biển.
- Typhon nổi lên giữa vịnh với Thorne trên đài chỉ huy, rồi chìm. Tin nhắn cuối của ông ta tới sau khi tàu đã chìm: tọa độ bãi phóng của Dự án Icarus, và một câu: "Đừng để tôi đã đúng." Không ai tìm thấy thi thể ông ta.
- Icarus Mk.0 lộ diện trên Skyhold rồi bỏ chạy: một bản thử nghiệm, Venn nói, cho một thứ lớn hơn nhiều. Hawk hạ Raven trên không, và trong trận đánh chiếm Skyhold, anh bắn phát cuối cùng.
- Orlov đánh trận cuối cùng với Gungnir rồi ra hàng qua bộ đàm. Venn phát hiện chương trình drone của mình đã nằm trong tay Aurel. Daedalus rơi xuống Skygate Array, và con đường tới Helion mở ra.
- Varga ngã xuống như một người lính; Kessler mặc cả tới phút cuối. Aurel phóng Icarus và một thanh vonfram rơi từ quỹ đạo, nhưng rồi Icarus rơi theo, đúng như cái tên của nó. Aurel chiến đấu tới cùng trong xác phi thuyền. Meridian Coast được giải phóng.
- Ở Foundry, Mara đối mặt với chiếc Behemoth Mk.0 cô từng vẽ khi còn là một kỹ sư trẻ, và mang bản thiết kế của nó về. Thiếu tá Brenn ký nhận từng trang.
- Lữ đoàn đưa tiến sĩ Venn qua Mirewood và Border Crossing với hai chiếc Locust bám theo. Tới bờ bên kia, bà đưa ra lựa chọn của mình: bà ở lại với lữ đoàn.
- Đội quân của đại tá Reyn tìm thấy Hawk và đưa anh ra qua Frostpeak và Jungle Pass, với Morrigan trên đầu. Raven để anh đi, lần này.

#### Chương 1: Coast of Fire

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| c1m01 | **Đổ bộ** Xuồng đổ bộ đã chạm cát. Chiếm bãi biển và con dốc phía trên trước khi đồn Hegemon kịp tỉnh ngủ. Quân ta tự chiến đấu: bạn chọn nơi đánh, mang theo gì và lúc nào pháo khai hỏa. | Stormbeach | Chiếm cứ điểm |  | 100 xu | Bán tải rốc-két |
| c1m02 | **Bịt mắt bờ biển** Trạm radar trên vách đá đang gọi pháo Hegemon bắn vào từng chiếc xuồng còn trong vịnh. Hạ nó xuống, các đợt đổ bộ sau sẽ vào bờ mà không bị phát hiện. | Stormbeach | Phá hủy |  | 105 xu | Xe cối tự hành |
| c1m03 | **Làng chài** Làng chài ở cửa sông, ngã tư phía trên và trang trại phía xa khống chế mọi con đường vào đất liền. Chỉ một nhúm lính trinh sát của Brandt giữ chúng. Chiếm cả ba là lữ đoàn có chỗ thở. | Greenvale | Chiếm cứ điểm |  | 105 xu | Sửa chữa |
| c1m04 | **Tiền đồn đầu tiên** Mara muốn lấy ngã tư làm căn cứ. Chiếm nó, lập tiền đồn ở đó và giữ vững trong lúc đội của cô thả tháp xuống. Trụ được rồi, lữ đoàn sẽ có sở chỉ huy đầu tiên trên Meridian Coast. | Greenvale | Lập tiền đồn |  | 110 xu · HQ 1 | Dàn rốc-két, Xưởng sửa chữa |
| c1m05 | **Bastion Mk.0** Brandt tung pháo đài nguyên mẫu băng qua cánh đồng Greenvale trong đêm để nghiền nát trại mới của ta. Nó chậm và giáp mỏng. Chặn nó lại. | Greenvale | Tiêu diệt boss Bastion Mk.0 · Pháo đài nguyên mẫu |  | 170 xu | Tăng nhẹ lội nước |
| c1m06 | **Đường tiếp tế** Nhiên liệu và đạn cho các đơn vị tiền phương, năm xe tải dưới mưa. Đưa ít nhất ba xe tới trang trại phía tây. Xe tải sẽ chờ hộ tống; chúng không tự lao vào ổ phục kích đâu. | Greenvale | Hộ tống |  | 115 xu | Bán tải cao xạ |
| c1m08 | **Đường vào Ashfield** Thị trấn Ashfield cùng hai kho nhiên liệu nằm ngay trước pháo đài. Chiếm cả ba, pháo đài sẽ bị cắt khỏi đường cái. | Ashfield | Chiếm cứ điểm |  | 120 xu | Bãi mìn |
| c1m09 | **Đạn cho trận vây thành** Pháo đánh pháo đài cần đạn. Đưa đoàn xe chở đạn vòng đường phía đông vào thị trấn Ashfield; năm xe phải tới được ba. | Ashfield | Hộ tống |  | 125 xu | Xe công binh |
| c1m10 | **Pháo đài Ashfield** chiến dịch lớn Lò gạch cũ trên đồi là điểm mạnh nhất của Hegemon trên Meridian Coast, và Bastion đi tuần trong sân của nó. Đốt kho nhiên liệu bên ngoài, chọn cách làm yếu tường… | Ashfield | Phá hủy |  | 305 xu |  |
| c1s1 | **Dấu xích trong sương** phụ Nadia nghe thấy tiếng động cơ trong sương quanh các trang trại Greenvale. Đưa một xe tới từng cứ điểm trong ba cứ điểm để xem trước khi thứ gì ngoài đó kịp cố thủ. | Greenvale | Trinh sát |  | 350 xu |  |

#### Chương 2: Black Gold

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| c2m01 | **Dầu và cát** Lữ đoàn đã tới mỏ dầu Dunebreak. Hegemon muốn giành lại trước khi ta kịp phá giếng. Trụ vững ở mỏ dầu trong năm phút. | Dunebreak | Trụ vững | varga | 130 xu | Pháo cao xạ tự hành |
| c2m02 | **Giếng dầu Red Rock** Đầu giếng, ốc đảo và trạm dừng đoàn lạc đà ở Red Rock cấp dầu cho đường ống tới Dunebreak. Xe tăng của Varga giữ ốc đảo. Chiếm cả ba. | Red Rock | Chiếm cứ điểm | varga | 135 xu | Lựu pháo tự hành |
| c2m03 | **Đoàn xe đêm** Xe bồn nhiên liệu cho lữ đoàn, băng qua hẻm núi trong đêm, qua ốc đảo tới đầu giếng. Năm xe phải qua được ba. | Red Rock | Hộ tống |  | 135 xu | Tăng phun lửa |
| c2m04 | **Cắt đường ống** Năm trạm đường ống dẫn dầu từ Red Rock vào nhà máy lọc dầu. Cho nổ tung tất cả. Một trận đột kích, không căn cứ: vào nhanh, ra nhanh hơn. | Dunebreak | Phá hủy | varga | 140 xu | Không kích |
| c2m05 | **Inferno** Varga tung Inferno ra giữa bão cát để canh con đường tới nhà máy lọc dầu: một chiếc Behemoth dựng lại quanh các súng phun lửa. Tránh xa tầm với của nó và đẩy nó lùi lại. | Dunebreak | Tiêu diệt boss Inferno · Behemoth phun lửa | varga | 215 xu | Xe tiếp đạn |
| c2m06 | **Săn bọ cạp** Ba dàn pháo phản lực và tên lửa của Varga ẩn giữa các khối đá, đánh dấu màu đỏ. Tìm ra chúng trong bão cát và tiêu diệt. | Red Rock | Săn mục tiêu | varga | 145 xu | Tháp tên lửa chống tăng, Kho đạn |
| c2m07 | **Đồn ốc đảo** Một đại đội dân quân Red Rock đã tuyên bố đứng về phía Accord và đang giữ ốc đảo. Xe tăng của Varga vây kín họ. Phá vòng vây trước khi sở chỉ huy của họ thất thủ. Các xe vây được đánh… | Red Rock | Giải vây |  | 150 xu | Xe bom bọc thép |
| c2m08 | **Giữ nhà máy lọc dầu** Ta đã đặt được một chân vào nhà máy lọc dầu. Varga đang tung lực lượng dự bị vào đó. Giữ sân nhà máy trong bốn phút. | Dunebreak | Giữ cứ điểm | varga | 155 xu | Xe thả khói |
| c2m09 | **Trại của Varga** Varga đã đào sở chỉ huy vào cuối hẻm núi: pháo chống tăng, những chiếc xe tăng hắn ưng ý nhất, và cái tính nóng của hắn. San phẳng sở chỉ huy. Hắn sẽ chạy; để hắn biết ta đang tới. | Red Rock | Đấu tướng | varga | 155 xu | Xe radar phản pháo |
| c2m10 | **Đột kích nhà máy lọc dầu** Trận đột kích mà Varga sợ nhất: chiếm mỏ dầu và ốc đảo, chọn mục tiêu kế tiếp, rồi cho nổ tháp và bồn chứa của nhà máy, cùng Inferno bên trong. Giai đoạn: Mỏ dầu và ốc đả… | Dunebreak | Chiếm cứ điểm | varga | 290 xu |  |
| c2m11 | **Behemoth ở Red Rock** chiến dịch lớn Chiến dịch giành Red Rock, lần đầu tiên có đạo quân của tướng Thorne ở bên sườn. Chiếm giếng dầu, chọn đòn đánh, chiếm và giữ ốc đảo, rồi hạ chính Behemoth. Gia… | Red Rock | Chiếm cứ điểm | varga | 390 xu |  |
| c2s1 | **Bản đồ bãi mìn** phụ Nadia cần người tới xem ốc đảo, nhà máy và mỏ dầu trong đêm: Varga đang cho rải mìn, và cô muốn biết ở đâu. Nhìn rồi đi, đừng nấn ná. | Dunebreak | Trinh sát |  | 450 xu |  |
| c2s2 | **Trực thăng của Varga** phụ Varga gọi trực thăng tới săn đoàn xe của ta trên Red Rock. Hawk muốn bắn rơi mười chiếc trước khi mặt trời lặn. Mang phòng không theo. | Red Rock | Bắn hạ máy bay |  | 450 xu |  |

#### Chương 3: The Long Winter

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| c3m01 | **Vào đèo** Whiteout Pass là con đường duy nhất lên phía bắc. Tiền đồn của Orlov giữ trạm tín hiệu, hồ băng và xưởng cưa. Chiếm cả ba trong tuyết. | Whiteout Pass | Chiếm cứ điểm | orlov | 165 xu | Xe tên lửa phòng không tầm trung |
| c3m02 | **Làm mù radar** Trạm đầu tiên trên tuyến radar của Orlov đứng trên cao điểm phía tây. Chừng nào nó còn nhìn thấy, pháo của hắn còn bắn trúng mọi thứ ta di chuyển. Phá hủy nó. | Frostpeak | Phá hủy | orlov | 170 xu | Trực thăng tấn công |
| c3m11 | **Đường radar** Con đường tới tuyến radar của Orlov chạy qua ba xóm nhỏ đóng băng trên sườn Frostpeak. Chiếm cả ba trong tuyết; người chỉ điểm của ông ta nấp ở từng xóm. | Frostpeak | Chiếm cứ điểm | orlov | 175 xu | Tiêm kích |
| c3m03 | **Ngôi làng trong sương** Ngôi làng dưới thung lũng là chỗ trú duy nhất trong vòng nhiều cây số. Orlov muốn lấy lại, và sương mù che pháo của hắn. Giữ làng trong ba phút rưỡi. | Frostpeak | Giữ cứ điểm | orlov | 175 xu | UAV quét |
| c3m04 | **Căn cứ trên băng** Mara muốn dựng căn cứ tiền phương trên hồ băng, giữa đèo. Chiếm hồ, lập tiền đồn và giữ nó ba phút. Ban đêm. Trên băng. | Whiteout Pass | Lập tiền đồn | orlov | 180 xu | Răng rồng, Trạm radar |
| c3m05 | **Harpy** Harpy vẫn săn các đoàn tiếp tế của ta trên đèo, và một phi công át chủ bài lái chiếc phản lực mang phù hiệu đen bay cùng nó. Bắn rơi pháo hạm bay. Phòng không có là để cho lúc này. | Whiteout Pass | Tiêu diệt boss Harpy · Trực thăng khổng lồ | orlov | 275 xu · HQ 2 | UAV trinh sát |
| c3m06 | **Pháo của Orlov** Nadia đã định vị được ba khẩu đội của Orlov qua ánh chớp đầu nòng, đánh dấu màu đỏ. Chúng di chuyển sau mỗi loạt bắn. Săn chúng trong bóng tối. | Frostpeak | Săn mục tiêu | orlov | 185 xu | Trực thăng trinh sát vũ trang |
| c3m12 | **Dưới làn pháo** Orlov biết ta đang ở đâu. Trong năm phút, mọi khẩu pháo trên tuyến của ông ta sẽ nã vào một thung lũng, thung lũng của ta, và quân yểm hộ sẽ tràn vào sau làn đạn. Trụ vững. | Frostpeak | Trụ vững | orlov | 190 xu | Xe rải mìn |
| c3m07 | **Những căn nhà gỗ trong tuyết** Các gia đình trên đèo đã trú trong những căn nhà gỗ và nhà kho phía nam. Orlov đang nã pháo vào mọi thứ còn mái che. Giữ ít nhất một căn đứng vững trong bảy phút. | Whiteout Pass | Bảo vệ | orlov | 195 xu |  |
| c3m08 | **Đoàn xe cứu thương** Thuốc men và bác sĩ cho trạm tín hiệu, nơi thương binh trên đèo đang chờ. Năm xe trong đêm; phải tới được ba xe. | Whiteout Pass | Hộ tống |  | 195 xu |  |
| c3m09 | **Trận địa pháo của Orlov** Sở chỉ huy của Orlov nằm sau một bức tường ụ pháo, nơi hắn nhìn thấy cả thung lũng. Chọc thủng và san phẳng nó. Hắn sẽ không chờ ta đâu. | Frostpeak | Đấu tướng | orlov | 200 xu |  |
| c3m10 | **Tuyến Frostpeak** chiến dịch lớn Trạm cuối của tuyến radar, pháo đài phía sau nó, và Jötunn canh cổng. Làm mù radar trên đồi, chọn đòn thứ hai, tiêu diệt Jötunn, rồi giữ cổng trước đợt phản kích củ… | Frostpeak | Phá hủy | orlov | 490 xu |  |
| c3s1 | **Pháo nằm ở đâu** phụ Trước trận đánh lớn, Nadia muốn mọi trận địa pháo quanh Frostpeak có mặt trên bản đồ của cô. Đưa xe tới đồi radar, ngôi làng và trại gỗ, trong sương mù. | Frostpeak | Trinh sát |  | 560 xu |  |
| c3s2 | **Fenrir** phụ Nadia phát hiện xe tiên phong mùa đông của Orlov giữa bão tuyết Whiteout Pass: Fenrir, một thợ săn hạng nặng đánh dấu mục tiêu cho pháo của ông ta. Đuổi theo và hạ nó trước khi bão tan. | Whiteout Pass | Tiêu diệt boss Fenrir · Xe tiên phong | orlov | 560 xu |  |

#### Chương 13: Blueprints

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| i1m01 | **Cổng Foundry** Foundry có ba lối vào: cổng bốc dỡ, nhà ga đường ray và xưởng luyện. Chiếm cả ba trong đêm, thật lặng lẽ, trước khi lính gác biết ta đã tới. | Foundry | Chiếm cứ điểm | varga | 205 xu | Tăng mái che |
| i1m02 | **Sổ cái** Thiếu tá Brenn biết Hegemon lưu hồ sơ thế nào: ba bản một. Bản vẽ Behemoth bị chia ra ba phòng lưu trữ. Đưa xe tới từng phòng, phần còn lại để ông lo. | Foundry | Trinh sát | varga | 210 xu |  |
| i1m03 | **Behemoth Mk.0** Tiếng báo động đã đánh thức lính gác lâu năm nhất của Foundry: Behemoth Mk.0, bản nguyên mẫu Mara thiết kế khi cô chưa hiểu chuyện. Nó chậm và cũ, nhưng thuộc từng góc của các xưởng… | Foundry | Tiêu diệt boss Behemoth Mk.0 · Behemoth nguyên mẫu | varga | 320 xu |  |
| i1m04 | **Rời Foundry** Ta đã có bản vẽ; Hegemon muốn lấy lại trước khi chúng lên xe. Giữ bãi bốc dỡ cho tới khi đoàn xe chất hàng xong. | Foundry | Giữ cứ điểm | varga | 215 xu |  |

#### Chương 4: Iron Harbor

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| c4m01 | **Rust Yard** Bãi dồn toa của Kessler nuôi cả bến cảng. Chiếm xưởng đúc, bãi dồn toa và bãi phế liệu, các đoàn tàu của hắn sẽ không còn chỗ lắp ráp. | Rust Yard | Chiếm cứ điểm | kessler | 220 xu | Xe chỉ huy |
| c4m02 | **Đánh chiếm khu nhà máy** Kessler giữ bến tàu, khu nhà máy và bãi đường sắt của Ironport. Chiếm cả ba dưới mưa, và lập tiền đồn trong khu nhà máy. | Ironport | Chiếm cứ điểm | kessler | 225 xu | Pháo chống tăng tự hành |
| c4m03 | **Đoàn xe bến cảng** Công binh và thuốc nổ cho bến tàu, năm xe tải xuyên qua bến cảng chìm trong sương. Phải tới được cầu tàu ba xe. | Ironport | Hộ tống |  | 225 xu | Pháo xung kích bánh lốp |
| c4m04 | **Mắt nhìn Bãi Sắt** Nadia cần biết Juggernaut đang được lắp ráp ở đâu. Đưa xe tới từng cứ điểm trong ba cứ điểm để quan sát, trước khi Kessler kịp cố thủ. | Rust Yard | Trinh sát | kessler | 230 xu | Trạm hậu cần |
| c4m05 | **Juggernaut** Đoàn tàu bọc thép của Kessler đang lao về bến tàu với một chuyến hàng mà Nadia nghe tên đã thấy không ổn. Phá hủy nó trước khi nó tới nơi. | Ironport | Chặn tàu Juggernaut · Đoàn tàu bọc thép | kessler | 350 xu | Tháp dã chiến |
| c4m12 | **Các cứ điểm của Flag** Đại úy Adler muốn ba cứ điểm dọc tường cảng, và muốn cờ của anh cắm trên từng cái trước trưa. Chiếm chúng từ phía đất liền, trong mưa. | Ironport | Chiếm cứ điểm | kessler | 235 xu | Pháo phản lực dẫn đường |
| c4m07 | **Kessler phản đòn** Giờ ta giữ khu nhà máy, và công nhân đã quay lại bàn máy. Kessler đang kéo tới từ phía nam để đốt trụi nó chứ không chịu mất. Giữ ít nhất một tòa nhà đứng vững trong bảy phút. | Ironport | Bảo vệ | kessler | 240 xu | Xe phòng không pháo – tên lửa |
| c4m16 | **Bản kê hàng** Hai xe chỉ huy của Kessler đang chở bản kê hàng của bến cảng ra khỏi Ironport, và Nadia muốn biết ông ta đã chở những gì. Chặn cả hai trước khi chúng ra tới cổng. | Ironport | Săn mục tiêu | kessler | 245 xu | Xe ủi bọc thép |
| c4m08 | **Tàu rải mìn trên cạn** Đêm nào các xe rải mìn của Kessler cũng gieo mìn khắp những con đường vào cảng. Nadia đã đánh dấu ba chiếc. Săn chúng trước khi chúng xong một vòng. | Rust Yard | Săn mục tiêu | kessler | 245 xu | Xe hỗ trợ tăng |
| c4m13 | **Sườn bỏ trống** Cánh quân của Thorne lẽ ra phải che sườn trái trong lúc ta giữ ngả qua xưởng đúc. Nó chưa tới. Một mình giữ ngả qua trong ba phút rưỡi. | Rust Yard | Giữ cứ điểm | kessler | 250 xu |  |
| c4m09 | **Tổng hành dinh của Đô đốc** Sở chỉ huy của Kessler nằm sau những dãy công-te-nơ ở đầu bắc bến cảng, phòng thủ thứ gì cũng có một ít và mìn ở khắp nơi. Phá nó giữa cơn bão và san phẳng sở chỉ huy. | Ironport | Đấu tướng | kessler | 255 xu |  |
| c4m10 | **Chiếm bến cảng** Cả bến cảng, trong một ngày: bãi đường sắt, rồi khu nhà máy và bến tàu. Trên cầu tàu, theo các bản chặn thu của Nadia, Tempest đang chờ với khẩu súng điện từ. Chiếm tất cả, tiêu di… | Ironport | Chiếm cứ điểm | kessler | 460 xu | Xe pháo điện từ |
| c4m14 | **Kessler chạy ra biển** Kessler đang đưa bộ tham mưu lên những con tàu cuối cùng ở cầu tàu đường sắt, và quân đoạn hậu giữ Rust Yard để câu giờ cho ông ta. Hôm nay ta không chặn được những con tàu.… | Rust Yard | Trụ vững | kessler | 260 xu |  |
| c4m17 | **Những chuyến tàu cuối** Bộ tham mưu của Kessler đang lao ra những chuyến tàu cuối cùng, mang theo sổ mật mã và hải đồ của cả dải bờ biển. Chặn cả hai xe tham mưu trên cầu tàu trước khi tàu nhổ neo,… | Ironport | Săn mục tiêu | kessler | 415 xu |  |
| c4m18 | **Đèn bến cảng** Ba chiếc phà chở đầy các gia đình vẫn còn neo ở Iron Harbor, và đội đoạn hậu của Kessler đang pháo kích cầu tàu để yểm hộ hắn chạy. Giữ nhà ga và chợ cá cho tới khi phà ra được khơi. | Ironport | Giữ cứ điểm | kessler | 260 xu |  |
| c4m06 | **Scylla** Kessler đã chạy ra biển. Tàu khu trục chỉ huy Scylla của ông ta đang chặn Beacon Bay trong sương cho hạm đội rút đi. Đánh chìm nó. | Beacon Bay | Tiêu diệt boss Scylla · Tàu khu trục | kessler | 395 xu |  |
| c4m15 | **Đêm ở làng chài** Các toán đổ bộ của Kessler đang lên bờ ở Beacon Bay. Giữ làng chài suốt đêm trong lúc pháo của ta tiến lên theo đường ven biển. | Beacon Bay | Giữ cứ điểm | kessler | 265 xu |  |
| c4m11 | **Leviathan** chiến dịch lớn Kessler đang ở trên Leviathan ngoài khơi Beacon Bay cùng phần còn lại của hạm đội, nã pháo vào bờ biển. Chiếm ngọn hải đăng để thấy tàu của ông ta, chọn hỏa lực, chiếm là… | Beacon Bay | Chiếm cứ điểm | kessler | 650 xu | Tháp pháo hạng nặng · Pháo bờ biển tầm xa |
| c4s1 | **Chuyến tàu tù binh** phụ Nadia đã tìm ra nơi Kessler giam giữ tù binh Accord: một đường tránh ở bãi phế liệu. Bốn xe tải để đưa họ ra; phải thoát được ba xe. | Rust Yard | Hộ tống |  | 745 xu |  |
| c4s2 | **Những viên cảng vụ** phụ Hai viên cảng vụ của Kessler vẫn đang điều hành các tuyến buôn lậu từ xe chỉ huy. Nadia đã đánh dấu họ. Bắt họ về, bằng cách khó. | Ironport | Săn mục tiêu |  | 745 xu |  |

#### Chương 5: Burning Canopy

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| c5m01 | **Đền Tro** Lực lượng canh gác vòng ngoài của Venn giữ bến đền cổ và làng phía đông Jungle Pass. Chiếm trọn con đèo dưới mưa. | Jungle Pass | Chiếm cứ điểm | sen | 275 xu | UAV tấn công |
| c5m02 | **Xe bầy đàn** Ba xe phóng của Venn đêm nào cũng tung bầy drone qua đồng dung nham. Nadia đã đánh dấu chúng. Săn chúng dưới ánh sáng của dung nham. | Emberridge | Săn mục tiêu | sen | 275 xu | Xe phóng drone FPV |
| c5m03 | **Đường ven sông** Thiết bị bắc cầu cho công binh, ngược đường ven sông qua sương rừng tới làng phía tây. Năm xe phải tới được ba; drone của Venn sẽ săn lùng chúng. | Jungle Pass | Hộ tống |  | 280 xu | Xe phóng drone cảm tử tầm xa |
| c5m04 | **Nhà máy địa nhiệt** Mara muốn lấy nhà máy địa nhiệt giữa Emberridge: điện miễn phí cho một căn cứ tiền phương. Chiếm nó, lập tiền đồn, giữ ba phút. | Emberridge | Lập tiền đồn | sen | 285 xu | Sân bay dã chiến |
| c5m08 | **Giữ đèn sáng** Các bồn hơi của nhà máy địa nhiệt giờ cấp điện cho cả lữ đoàn. Drone của Venn đang lao tới từ phía nam. Giữ ít nhất một bồn đứng vững trong bảy phút. | Emberridge | Bảo vệ Locust · Tàu con drone | sen | 285 xu | Xe phóng đạn lảng vảng |
| c5m12 | **Vòng ra phía sau** Quân canh vòng ngoài của Venn nhìn về đèo từ phía nam. Vòng qua các làng phía bắc và chiếm cả đèo từ phía sau, trong mưa. | Jungle Pass | Chiếm cứ điểm | sen | 290 xu | Xe gây nhiễu điện tử |
| c5m05 | **Hive** Pháo đài drone của Venn đang bò xuống con đèo trong cơn bão, bầy drone bốc lên từ các giàn phóng. Nó không có pháo chính và chẳng sợ máy bay nào. Đập vỡ nó bằng xe tăng và pháo binh. | Jungle Pass | Tiêu diệt boss Hive · Pháo đài drone | sen | 440 xu |  |
| c5m06 | **Cổng Dung Nham** Xưởng drone nằm trong một pháo đài ở đầu bắc sườn núi. Phá tường trong đêm và san phẳng sở chỉ huy. | Emberridge | Phá hủy | sen | 295 xu |  |
| c5m11 | **Tín hiệu phòng thí nghiệm** Nadia lần theo một tín hiệu tới một phòng thí nghiệm trên sườn núi mà chính bản đồ của Hegemon bỏ sót. Đưa xe tới từng tòa nhà đã đánh dấu. Có thể Venn đang ở trong. | Emberridge | Trinh sát | sen | 300 xu |  |
| c5m07 | **Quét sạch tán rừng** Drone tấn công của Venn làm chủ bầu trời trên đèo. Bắn rơi mười bốn chiếc, và rừng lại thuộc về lữ đoàn. | Jungle Pass | Bắn hạ máy bay | sen | 305 xu |  |
| c5m13 | **Ngôi đền trong đêm** Bến lội qua ngôi đền là ngả qua duy nhất bầy drone không nhìn thấu được qua tán rừng. Giữ nó suốt đêm. | Jungle Pass | Giữ cứ điểm | sen | 305 xu |  |
| c5m09 | **Những nhà chứa trên đèo** Sở chỉ huy dã chiến của Venn được bao quanh bởi những nhà chứa drone và xe gây nhiễu. Phá nó trong đêm và san phẳng sở chỉ huy. Nadia nghĩ bà ấy có thể sẽ không đánh tới c… | Jungle Pass | Đấu tướng | sen | 310 xu |  |
| c5m10 | **Matriarch** chiến dịch lớn Tàu mẹ của Hive đang lơ lửng trên Emberridge, tiếp bầy drone cho mọi đơn vị Hegemon trong rừng. Chiếm các đường đắp, chọn đòn kế tiếp, trụ vững trước bầy drone nó tung ra… | Emberridge | Chiếm cứ điểm | sen | 750 xu | Máy bay mẹ thả drone |
| c5s1 | **Sổ ghi chép của Venn** phụ Venn có các trạm thực địa trong đèo, không ghi trong sổ sách của Hegemon. Nadia muốn tận mắt thấy cả ba trước khi có người dọn sạch chúng. | Jungle Pass | Trinh sát |  | 865 xu |  |
| c5s2 | **Làng đốt than** phụ Dân đốt than trên sườn núi đã cầm cự với Hegemon suốt hai năm trong một trại có rào lũy. Giờ họ bị vây kín. Phá vòng vây; quân vây được đánh dấu. | Emberridge | Giải vây |  | 865 xu |  |

#### Chương 6: Counterstrike

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| c6m01 | **Ashfield rực lửa** Hegemon phản đòn đúng nơi ta giành chiến thắng đầu tiên. Varga đang tung thiết giáp vào pháo đài Ashfield, giờ là của ta, cả tháp lẫn tường. Giữ sở chỉ huy của nó đứng vững trong… | Ashfield | Bảo vệ | varga | 315 xu | Tăng hạng nặng |
| c6m13 | **Phòng tuyến của Brandt** Thiếu tá Brandt đã về phe ta, và ông biết chính xác Varga sẽ đánh vào Ashfield ở đâu. Chiếm quảng trường thị trấn, lập tiền đồn và giữ nó trong lúc công binh của ông dựng t… | Ashfield | Lập tiền đồn | varga | 320 xu | Tăng hai nòng |
| c6m02 | **Sơ tán Whiteout Pass** Đợt phản công của Varga đang tràn qua đèo. Dân làng ở hồ băng phải rời đi: sáu xe tải, cứ vài giây một chiếc, theo đường về trại của ta. Giữ hồ cho tới khi xe cuối cùng rời đ… | Whiteout Pass | Di tản | varga | 325 xu | Trạm đánh chặn C-RAM |
| c6m16 | **Lại Greenvale** Thiết giáp của Varga đã chiếm lại ngã tư Greenvale, ngôi làng và trang trại ta giành được những ngày đầu. Chiếm lại chúng từ phía bên kia, trong sương. | Greenvale | Chiếm cứ điểm | varga | 325 xu | Xe la-de phòng không |
| c6m11 | **Canh mùa gặt** Cuộc tổng phản công của Varga đã tới Greenvale, và Aurel muốn đốt các si-lô thóc cùng tháp nước để cả thung lũng chết đói mùa đông này. Giữ ít nhất một công trình đứng vững qua cơn b… | Greenvale | Bảo vệ | varga | 330 xu | Trực thăng vũ trang bọc giáp |
| c6m03 | **Behemoth của ta** Mara đã làm được: chiếc Behemoth trong sân pháo đài Ashfield đã chạy, và nó là của ta. Hộ tống nó từ Jötunn qua Ashfield ra tiền tuyến. Varga sẽ làm mọi cách để chặn chính cỗ máy… | Ashfield | Hộ tống | varga | 335 xu | Tháp gây nhiễu EW |
| c6m05 | **Behemoth Mk.II** Varga đã dựng lại chiếc Behemoth ta đốt ở Dunebreak: nặng hơn, lắp hệ sưởi cho tuyết, và đang xuống Whiteout Pass. Chặn Behemoth Mk.II trước khi nó tới phòng tuyến của ta. | Whiteout Pass | Tiêu diệt boss Behemoth Mk.II · Behemoth nâng cấp | varga | 505 xu |  |
| c6m12 | **Trinh sát trên vách đá** Trinh sát của Varga đang nấp trên vách đá Stormbeach, chỉ điểm cho cuộc đổ bộ Charybdis sắp tiến hành. Nadia đã đánh dấu ba tổ. Săn chúng trong mưa. | Stormbeach | Săn mục tiêu | varga | 340 xu |  |
| c6m08 | **Charybdis** Đợt tổng phản công của Varga tới từ biển: Charybdis, một tàu đệm khí đổ bộ, đang chở cả một đại đội thiết giáp lên chính bãi biển ta đã đổ bộ. Đánh chìm nó trước khi nó dỡ quân. | Stormbeach | Tiêu diệt boss Charybdis · Tàu đệm khí đổ bộ |  | 515 xu |  |
| c6m07 | **Đồn thị trấn** Varga đã vây kín thị trấn Ashfield, nơi dân quân Accord đặt sở chỉ huy. Phá vòng vây trước khi nó thất thủ; quân vây được đánh dấu. | Ashfield | Giải vây | varga | 345 xu |  |
| c6m04 | **Thung lũng con đập** Varga đang nhắm tới Hollow Dam, nơi thắp sáng nửa Meridian Coast. Tới đó trước hắn: trạm phát điện, cầu đường bộ và bến lội. | Hollow Dam | Chiếm cứ điểm | varga | 350 xu · HQ 3 |  |
| c6m06 | **Giữ cây cầu** Cây cầu đường bộ dưới chân đập là lối duy nhất cho thiết giáp hạng nặng vượt sông. Giữ nó trong sương mù bốn phút. Không được để cây cầu rơi vào tay Varga. | Hollow Dam | Giữ cứ điểm | varga | 355 xu |  |
| c6m09 | **Trại mùa đông của Varga** Varga dựng trại mùa đông ở phía nam đèo, ngay trên các vị trí cũ của ta, và đào sẵn mọi khẩu pháo chống tăng hắn có. San phẳng sở chỉ huy, đợt phản công của hắn sẽ mất đầu. | Whiteout Pass | Đấu tướng | varga | 355 xu |  |
| c6m15 | **Đường tràn** Thiết giáp của Varga giữ con đường tràn dưới chân đập: trạm phát điện, cây cầu và bến lội. Thorne hứa sẽ đánh bến lội từ phía bắc. Chiếm cả ba; đừng chờ ông ta. | Hollow Dam | Chiếm cứ điểm | varga | 360 xu |  |
| c6m14 | **Ngừng bắn** Hollow Dam đang nứt. Trong đúng một buổi sáng, Varga và Kade đồng ý ngừng bắn để các làng bên dưới kịp chạy. Bầy drone của Aurel thì chẳng đồng ý gì cả. Đưa các gia đình qua cầu và xuốn… | Hollow Dam | Di tản | varga | 365 xu |  |
| c6m10 | **Bảo vệ con đập** chiến dịch lớn Quân bài cuối của Varga là Moloch, một nhà máy bánh xích vừa lăn vừa đóng xe tăng, và nó đang tiến về con đập. Giữ đỉnh đập cho tới khi quân của Thorne tới. Giai đoạ… | Hollow Dam | Giữ cứ điểm | varga | 880 xu | Xe công sự triển khai |
| c6s1 | **Không kích đêm** phụ Máy bay đột kích đêm của Varga đang ném bom pháo đài Ashfield. Hawk muốn bắn rơi mười bốn chiếc trước bình minh. | Ashfield | Bắn hạ máy bay |  | 1010 xu |  |
| c6s2 | **Khảo sát con đập** phụ Mara cần biết con đập có chịu nổi một trận vây hãm hay không. Đưa xe tới trạm phát điện, cây cầu và bến lội để công binh của cô quan sát. | Hollow Dam | Trinh sát |  | 1010 xu |  |

#### Chương 14: The Queen's Choice

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| i2m01 | **Vào Mirewood** Đại úy Mendez muốn qua khỏi Mirewood trước chạng vạng. Chiếm hai ngôi làng và ngôi đền chìm trên các đường đắp, thật nhanh, trong sương. | Mirewood | Chiếm cứ điểm | aurel | 370 xu | Xe phát khiên |
| i2m02 | **Chiếc Locust thứ nhất** Một chiếc Locust đã tìm ra đoàn xe: một tàu mang drone cỡ nhỏ trong chính chương trình của Venn, săn bà theo dấu hiệu vô tuyến. Bắn hạ nó trước khi bầy drone tới được đoàn x… | Mirewood | Tiêu diệt boss Locust · Tàu con drone | aurel | 560 xu |  |
| i2m03 | **Cây cầu lớn** Một toán dân quân Accord muốn đem Venn ra xử treo cổ đã tới Border Crossing trước, và chúng không chịu tránh đường. Giữ cây cầu lớn cho tới khi đoàn xe qua hết. | Border Crossing | Giữ cứ điểm |  | 375 xu |  |
| i2m04 | **Chiếc Locust thứ hai** Chiếc Locust thứ hai đã tìm ra ngả qua. Nó là thứ cuối cùng chắn giữa Venn và bờ bên kia. Bắn hạ nó và đưa bà qua. | Border Crossing | Tiêu diệt boss Locust · Tàu con drone | aurel | 570 xu |  |

#### Chương 7: Veyra

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| c7m01 | **Vào thành phố** Metro City là cửa ngõ vào thủ đô. Chiếm công viên, quảng trường và bãi đỗ xe trong sương mù, từng con phố một. | Metro City | Chiếm cứ điểm | aurel | 385 xu | Máy bay cường kích |
| c7m03 | **Khởi nghĩa quảng trường** Thành phố đã nổi dậy: quân kháng chiến giữ quảng trường, và vệ binh của Aurel đã vây kín họ. Phá vòng vây trước khi sở chỉ huy của họ thất thủ; quân vây được đánh dấu. | Metro City | Giải vây | aurel | 385 xu | Pháo phản lực nhiệt áp |
| c7m16 | **Cánh quân của Thorne** Đạo quân của tướng Thorne đã tới Metro City cùng ta. Cánh quân của ông đánh các phố phía bắc cùng quân ta: công viên, quảng trường và bãi đỗ xe, từ phía đông. Nadia xin được… | Metro City | Chiếm cứ điểm | aurel | 390 xu | Tiêm kích tàng hình |
| c7m04 | **Những tòa tháp** Aurel ra lệnh nã pháo vào các tòa tháp của thành phố chứ không chịu để lại cho ta: hàng nghìn người đang sống trong đó. Giữ ít nhất một tòa đứng vững bảy phút. | Metro City | Bảo vệ | aurel | 395 xu | Pháo cối công thành |
| c7m05 | **Juggernaut giữa phố** Đoàn tàu bọc thép Juggernaut của Kessler đã được vá lại và đưa lên tuyến hàng hóa của Metro City để chở cận vệ của Aurel vào trung tâm. Tới kho ga, nó có một phút để dỡ pháo n… | Metro City | Chặn tàu Juggernaut · Đoàn tàu bọc thép | aurel | 595 xu |  |
| c7m07 | **Các chính ủy** Ba chính ủy của Aurel đang giữ cho quân đồn trú thành phố khỏi tan rã, di chuyển giữa các quận bằng xe chỉ huy trong cơn bão. Săn lùng họ; họ đã được đánh dấu. | Metro City | Săn mục tiêu | aurel | 400 xu |  |
| c7m12 | **Cổng Old Quarter** Old Quarter của Veyra là một mê cung phố hẹp quanh ba quảng trường, và cận vệ của Aurel giữ cả ba. Chiếm chúng trong đêm, từng con phố một. | Veyra Old Quarter | Chiếm cứ điểm | aurel | 405 xu |  |
| c7m15 | **Phố hẹp** Nadia muốn tận mắt thấy ba quảng trường của Old Quarter trước trận đánh lớn: ai đang giữ chúng, và cờ của ai bay trên đó. Đưa xe vào từng quảng trường, trong mưa. | Veyra Old Quarter | Trinh sát | aurel | 405 xu |  |
| c7m13 | **Inferno giữa Old Quarter** Cận vệ của Aurel có một chiếc Inferno riêng, chiếc thứ hai từ xưởng của Varga, và nó đang đốt Old Quarter từng con phố một. Chặn nó lại. | Veyra Old Quarter | Tiêu diệt boss Inferno · Behemoth phun lửa | aurel | 615 xu |  |
| c7m14 | **Pháo của Longshot** Thiếu tá Dahl đã đưa pháo của lữ đoàn vào quảng trường chính của Old Quarter, và cận vệ của Aurel muốn đuổi chúng ra. Giữ quảng trường bốn phút trong lúc Longshot căn pháo vào m… | Veyra Old Quarter | Giữ cứ điểm | aurel | 415 xu |  |
| c7m02 | **Những cây cầu Veyra** Thủ đô nằm trên một hòn đảo giữa sông. Trước khi tướng Thorne tới, Nadia muốn quan sát khu vườn, quảng trường cung điện và nhà ga. | Veyra | Trinh sát | aurel | 415 xu |  |
| c7m17 | **Những cây cầu trong đêm** Trung tâm Veyra nằm trên hòn đảo sau ba đầu cầu. Chiếm khu vườn, quảng trường cung điện và nhà ga từ bờ bên kia, trong đêm, theo sau làn đạn của Dahl. | Veyra | Chiếm cứ điểm | aurel | 420 xu |  |
| c7m06 | **Quảng trường cung điện** Một chỗ đứng chân trong thủ đô: quảng trường cung điện. Vệ binh của Aurel muốn giành lại. Giữ nó trong sương mù bốn phút. | Veyra | Giữ cứ điểm | aurel | 425 xu |  |
| c7m11 | **Bão trên Veyra** Trực thăng của đội cận vệ Aurel đang săn quân kháng chiến trên các mái nhà Veyra giữa cơn bão. Bắn hạ mười bốn chiếc. | Veyra | Bắn hạ máy bay | aurel | 425 xu |  |
| c7m09 | **Dập tắt đài phát** Đài tuyên truyền của Hegemon phát cho cả nước mỗi đêm từ mái vòm radar cạnh cung điện. Đêm nay thì không. Phá hủy nó. | Veyra | Phá hủy | aurel | 430 xu |  |
| c7m18 | **Tuyến sông** Cận vệ của Aurel đang dồn mọi thứ vào tuyến sông của ta trước trận đánh cuối. Trụ vững năm phút; pháo của Dahl sẽ lo phần còn lại. | Veyra | Trụ vững | aurel | 435 xu |  |
| c7m08 | **Rời cung điện** Các gia đình đang trú trong cung điện phải ra ngoài trước trận quyết chiến: sáu xe tải qua cầu phía tây, cứ vài giây một chiếc. Phải thoát được bốn xe. | Veyra | Di tản | aurel | 435 xu |  |
| c7m10 | **Giải phóng Veyra** chiến dịch lớn Veyra, với đạo quân và căn cứ của tướng Thorne bên cạnh. Chiếm các đầu cầu, chọn đòn đánh, đánh chiếm cung điện và quảng trường, rồi chặn thứ cuối cùng Aurel tung… | Veyra | Chiếm cứ điểm | aurel | 1055 xu |  |
| c7s1 | **Những bức thư** phụ Nadia đã chặn được những bức thư giữa tướng Thorne và một người nào đó ở Metro City. Cô muốn tự mình xem ba điểm trao thư, một cách lặng lẽ. | Metro City | Trinh sát |  | 1215 xu |  |

#### Chương 8: Underworld

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| c8m01 | **Vào khu mỏ** Dấu vết của Thorne dẫn lên vùng mỏ phía bắc. Chiếm các ngả qua hẻm núi từ phía bên kia, trong đêm. | Red Rock | Chiếm cứ điểm | hung | 445 xu | Xe tên lửa phòng không tầm xa |
| c8m02 | **Kho quặng** Ta đang giữ kho quặng trên miệng hố mỏ. Thorne muốn lấy lại nó ngay đêm nay. Giữ cho lữ đoàn trụ vững tới sáng. | Deepcut Mine | Trụ vững | hung | 445 xu | Pháo phản lực hạng nặng |
| c8m03 | **Săn khẩu đội** Các khẩu đội rốc-két của Thorne nã vào đường mỏ từ trên các khối đá. Nadia đã đánh dấu chúng. Săn chúng. | Red Rock | Săn mục tiêu | hung | 450 xu | Trạm tên lửa phòng không tầm xa |
| c8m11 | **Thủy triều dâng** Thợ mỏ của đại úy Varro thuộc mọi con đường vào Deepcut Mine, và họ mang theo mọi thứ còn chạy được. Cùng họ chiếm nhà máy nghiền, đáy hố và bãi xuất quặng. | Deepcut Mine | Chiếm cứ điểm | hung | 455 xu | Xe phóng tên lửa chiến thuật |
| c8m04 | **Thị trấn mỏ** Thợ mỏ ở thị trấn hẻm núi đã nổi dậy chống Thorne, và xe tăng của hắn vây kín họ. Phá vòng vây trong bão cát. | Red Rock | Giải vây | hung | 455 xu |  |
| c8m05 | **Tartarus** Thorne đã tung Tartarus, cỗ máy khoan cũ của Varga, luồn dưới Hollow Dam về phía trạm phát điện. Chặn nó trước khi nó tới nơi. | Hollow Dam | Chặn tàu Tartarus · Máy khoan | hung | 690 xu |  |
| c8m06 | **Miệng hầm** Các đường hầm mỏ thông ra dưới con đập. Giữ ngả qua trong đêm khi Thorne tìm cách chọc thủng. | Hollow Dam | Giữ cứ điểm | hung | 465 xu |  |
| c8m12 | **Chiến lợi phẩm của Magpie** Thượng sĩ Quist đã tìm ra ba kho trong hố mỏ mà Thorne bỏ lại vội vàng. Đưa xe tới từng kho trước khi người của ông ta quay lại. Việc khuân vác để cô lo. | Deepcut Mine | Trinh sát | hung | 465 xu |  |
| c8m07 | **Ixion** Một xe tải mỏ bọc thép có bánh cao hơn xe tăng đang lao xuống đường vận chuyển hết tốc lực: Ixion. Chặn nó trước khi nó húc vào đội hình của ta. | Deepcut Mine | Tiêu diệt boss Ixion · Xe tải mỏ bọc thép | hung | 705 xu |  |
| c8m08 | **Mắt nhìn hố mỏ** Trước khi vào hố mỏ sâu nhất, Nadia muốn tận mắt thấy nó. Đưa xe tới từng điểm đánh dấu trong cơn bão. | Hollow Dam | Trinh sát | hung | 475 xu |  |
| c8m09 | **Trại của Thorne** Thorne đã đào sở chỉ huy vào cuối hẻm núi. San phẳng nó. Hắn sẽ lại chạy; bắt hắn chạy nhanh hơn. | Red Rock | Đấu tướng | hung | 475 xu |  |
| c8m13 | **Thợ mỏ Deepcut** Thorne đang giữ ba trăm thợ mỏ trong các lán trại dưới hố để đào đường cho Kronos. Dân quân của Varro thuộc từng đường hầm. Chiếm cả ba lán trại và mọi người thợ mỏ sẽ được ra ngoà… | Deepcut Mine | Chiếm cứ điểm | hung | 475 xu |  |
| c8m14 | **Đánh thẳng vào Kronos** Kronos lấy điện từ một đường dây duy nhất dẫn xuống hố, và viên quản lương của Thorne ngồi ngay cạnh tủ điện với lương của cả một năm. Giữ con dốc trong lúc công binh cắt đư… | Deepcut Mine | Trụ vững | hung | 955 xu |  |
| c8m10 | **Hố sâu nhất** chiến dịch lớn Chiến dịch vào khu mỏ của Thorne: chiếm miệng hố, chọn mục tiêu kế tiếp, phá các xưởng, rồi đối mặt với thứ đang chờ dưới đáy: Kronos. Giai đoạn: Nhà máy nghiền và bãi… | Deepcut Mine | Chiếm cứ điểm | hung | 1150 xu |  |
| c8s1 | **Bản đồ khảo sát** phụ Nadia muốn lấy bản đồ khảo sát của khu mỏ từ ba tòa nhà trên đồi cát. Nhìn thôi, đừng nán lại. | Dunebreak | Trinh sát | hung | 1325 xu |  |
| c8s2 | **Chuyến bay đêm** phụ Thorne đang chở vàng ra khỏi khu mỏ trong đêm. Bắn hạ các máy bay vận tải của hắn. | Red Rock | Bắn hạ máy bay | hung | 1325 xu |  |

#### Chương 9: Rough Water

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| c9m01 | **Lại bến cảng** Thorne đã chiếm Ironport cùng tàn quân của Kessler. Chiếm lại cầu tàu trong cơn bão. | Ironport | Chiếm cứ điểm | hung | 485 xu | Xe la-de diệt tăng |
| c9m02 | **Trở lại bãi biển** Thorne đang đổ quân lên chính bãi biển nơi cuộc chiến của ta bắt đầu. Chiếm bãi biển từ phía bên kia, trong mưa. | Stormbeach | Chiếm cứ điểm | hung | 485 xu | Mìn rải từ xa |
| c9m03 | **Đoàn xe đêm** Đưa đoàn xe tải tiếp tế qua các con đường bến cảng trong đêm. Lính tuần của Thorne đang chờ. | Ironport | Hộ tống | hung | 490 xu | Oanh tạc cơ chiến lược |
| c9m04 | **Pháo bờ biển** Thorne đã đặt lại pháo trên bãi biển. Phá chúng trước khi tàu của hắn cập bờ. | Stormbeach | Phá hủy | hung | 495 xu | Trận địa pháo |
| c9m05 | **Caspian** Từ trong sương lao ra Caspian, một con tàu bay sát mặt sóng và đổ quân. Hạ nó trước khi nó tới bãi biển. | Stormbeach | Tiêu diệt boss Caspian · Tàu bay sát mặt nước | hung | 745 xu · HQ 4 |  |
| c9m11 | **Tín hiệu dưới Beacon Bay** Tiến sĩ Venn nghe thấy một thứ dưới Beacon Bay: một tàu ngầm liên lạc với bầu trời trên một băng tần không ai dùng. Đưa xe tới pháo đài, làng chài và ngọn hải đăng để bà… | Beacon Bay | Trinh sát | hung | 500 xu |  |
| c9m06 | **Sở chỉ huy bến cảng** Thorne đặt sở chỉ huy ở cầu tàu phía xa. San phẳng nó và cắt đường ra biển của hắn. | Ironport | Đấu tướng | hung | 505 xu |  |
| c9m12 | **Coral Keys** Thủy thủ của Thorne đã chiếm Coral Keys: hai hòn đảo và ngọn hải đăng ở giữa. Chiếm cả ba là Venn có thể thả phao nghe xuống eo biển. | Coral Keys | Chiếm cứ điểm | hung | 505 xu |  |
| c9m13 | **Những chiếc phao nghe** Thorne biết những chiếc phao để làm gì. Giữ ngọn hải đăng qua cơn bão trong lúc Venn ghi lại từng chữ Typhon gửi đi. | Coral Keys | Giữ cứ điểm | hung | 510 xu |  |
| c9m07 | **Người giữ hải đăng** Các trạm quan sát của ta trong khu bến cảng dẫn đường cho pháo. Giữ ít nhất một trạm đứng vững qua trận tấn công đêm của Thorne. | Ironport | Bảo vệ | hung | 515 xu |  |
| c9m08 | **Lại là Scylla** Scylla trở lại hoạt động dưới cờ của Thorne, canh vịnh trong mưa. Lần này đánh chìm hẳn nó. | Beacon Bay | Tiêu diệt boss Scylla · Tàu khu trục | hung | 775 xu |  |
| c9m14 | **Giữ mũi đất** Những con tàu cuối cùng của Kessler và thủy thủ của Thorne đang đổ bộ lên mũi đất Beacon Bay để yểm hộ Typhon. Trụ vững trước cuộc đổ bộ năm phút. | Beacon Bay | Trụ vững | hung | 520 xu |  |
| c9m09 | **Săn trên bãi biển** Các tổ súng cối của Thorne đang nã vào đường bờ biển. Săn những tổ đã đánh dấu. | Stormbeach | Săn mục tiêu | hung | 525 xu |  |
| c9m10 | **Typhon trồi lên** chiến dịch lớn Chiến dịch giành bờ biển: chiếm bến cảng, chọn mục tiêu, dọn sạch các xưởng, rồi chặn Typhon, chiếc tàu ngầm tên lửa là quân bài cuối của Thorne. Giai đoạn: Bãi đườ… | Ironport | Chiếm cứ điểm | hung | 1265 xu |  |
| c9s1 | **Những tàu rải mìn cuối cùng** phụ Những xe rải mìn cũ của Kessler giờ làm việc cho Thorne. Săn những chiếc đã đánh dấu trước khi chúng phong tỏa bến cảng. | Ironport | Săn mục tiêu | hung | 1455 xu |  |
| c9s2 | **Trạm vô tuyến** phụ Các trạm vô tuyến của Thorne trên bãi biển liên lạc với tàu của hắn. Chiếm chúng trong sương. | Stormbeach | Chiếm cứ điểm | hung | 1455 xu |  |

#### Chương 15: Hawk and Raven

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| i3m01 | **Hawk bị bắn rơi** Hawk bị bắn rơi sau chiến tuyến, đâu đó trên các điểm cao Frostpeak, và đèn hiệu của anh lúc có lúc không. Đoàn quân của đại tá Reyn sẽ lục soát đồi radar, ngôi làng và trại gỗ, t… | Frostpeak | Trinh sát | quaden | 530 xu |  |
| i3m02 | **Morrigan** Raven đang tự mình săn đoàn cứu hộ, bằng Morrigan: nhanh, khó thấy, và mang vũ khí nhắm vào phòng không của ta. Cho bệ phóng di chuyển liên tục, để ý đòn tấn công của nó, và đuổi nó đi. | Jungle Pass | Tiêu diệt boss Morrigan · Tiêm kích của Raven | quaden | 800 xu |  |
| i3m03 | **Đoàn quân của Crown** Hawk đã tới được một ngôi làng ở Jungle Pass, và quân mặt đất của Raven vây kín nó. Đoàn thiết giáp hạng nặng của đại tá Reyn sẽ phá vòng vây. Các xe trong vòng vây đã được đá… | Jungle Pass | Giải vây | quaden | 535 xu |  |
| i3m04 | **Đường về nhà** Đoàn quân đã có Hawk và đang chạy về phòng tuyến của ta qua các điểm cao Frostpeak, với mọi thứ Raven còn lại bám đuôi. Trụ vững năm phút cho tới khi được đón. | Frostpeak | Trụ vững | quaden | 540 xu |  |

#### Chương 10: War in the Sky

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| c10m01 | **Bầy quạ trên đèo** Cầm trong tay hồ sơ của Venn, lữ đoàn quay mũi về Skyhold. Phi đội của Wolff đón đánh ta trên Frostpeak, lần này từ phía nam. Bắn rơi mười hai chiếc. | Frostpeak | Bắn hạ máy bay | quaden | 545 xu | Đòn SEAD |
| c10m02 | **Mắt nhìn Skyhold** Trước khi đánh căn cứ không quân, Nadia muốn tận mắt thấy nó: hai sân đỗ và đường băng. Đưa xe tới từng nơi, ngay dưới mũi Wolff. | Skyhold | Trinh sát | quaden | 545 xu | Oanh tạc cơ tàng hình |
| c10m11 | **Sân bay dã chiến của Vault** Đại úy Okoye có một sân bay dã chiến cho chiến dịch trên không, một đoạn đường trên các điểm cao Frostpeak, và một trăm chuyến bay vận tải cần hạ cánh ở đó. Giữ nó tron… | Frostpeak | Giữ cứ điểm | quaden | 550 xu | Pháo hạm bay |
| c10m03 | **Radar giờ là của ta** Trạm radar cũ của Orlov trên cao điểm giờ canh bầu trời cho ta, còn nhà thờ trong làng là trạm cứu thương. Wolff muốn xóa sổ cả hai. Giữ ít nhất một công trình đứng vững bảy p… | Frostpeak | Bảo vệ | quaden | 555 xu |  |
| c10m04 | **Đốt máy bay** Một trận đột kích đêm vào sân đỗ phía tây Skyhold: máy bay cường kích của Wolff đang đỗ thành hàng. Đốt chúng ngay tại chỗ. | Skyhold | Phá hủy | quaden | 555 xu |  |
| c10m05 | **Icarus Mk.0** Nhà chứa bị hàn cửa đã mở lúc bình minh. Icarus đang ở trên không phận Skyhold: phi thuyền quỹ đạo của Aurel, vỏ bạc, cánh ngắn, với động cơ chính đủ sức bỏ xa bất cứ thứ gì ta có. Ve… | Skyhold | Tiêu diệt boss Icarus Mk.0 · Phi thuyền nguyên mẫu | aurel | 840 xu |  |
| c10m06 | **Màn tên lửa** Wolff giấu các dàn tên lửa phòng không tầm xa trong sương để che chắn căn cứ. Nadia đã đánh dấu ba bệ phóng. Săn chúng để Hawk được bay. | Frostpeak | Săn mục tiêu | quaden | 565 xu |  |
| c10m13 | **Các con đèo lúc bình minh** Spectre săn trên các con đèo trong đêm. Ban ngày thì ta chiếm được chúng: trạm tín hiệu, hồ băng và xưởng cưa, từ phía bắc, trước khi phi đội của Raven cất cánh. | Whiteout Pass | Chiếm cứ điểm | quaden | 565 xu |  |
| c10m08 | **Spectre** Máy bay pháo của Wolff bay vòng trên cao quanh Whiteout Pass, nã vào các đoàn xe của ta tới Skyhold. Bắn rơi Spectre bằng mọi thứ với tới được bầu trời. | Whiteout Pass | Tiêu diệt boss Spectre · Máy bay pháo | quaden | 855 xu |  |
| c10m14 | **Giờ tiếp nhiên liệu** Nadia có lịch trình của Raven: mỗi chiều có một giờ phi đội của hắn nằm dưới đất tiếp nhiên liệu. Trong giờ đó, chiếm cả hai sân đỗ và đường băng từ phía bên kia. | Skyhold | Chiếm cứ điểm | quaden | 575 xu |  |
| c10m07 | **Không kích** Wolff đáp trả bằng tất cả những gì hắn có: từng đợt, từng đợt máy bay lao vào trận địa của ta quanh Skyhold. Bắn rơi mười sáu chiếc. | Skyhold | Bắn hạ máy bay | quaden | 575 xu |  |
| c10m12 | **Hawk và Raven** Raven gửi lời qua tháp điều khiển Skyhold: hắn và Hawk, trên đường băng, giữa trưa. Hawk đã nhận lời. Giữ phần còn lại của phi đội Raven tránh xa anh và hạ Morrigan. | Skyhold | Tiêu diệt boss Morrigan · Tiêm kích của Raven | quaden | 870 xu |  |
| c10m09 | **Tổ Wolff** Sở chỉ huy riêng của Wolff, ở đầu đông căn cứ, vây kín tên lửa. San phẳng nó; căn cứ không quân sẽ còn kháng cự, nhưng đã mất đầu. | Skyhold | Đấu tướng | quaden | 585 xu |  |
| c10m10 | **Tấn công Skyhold** chiến dịch lớn Chính căn cứ không quân. Làm mù radar, chọn đòn thứ hai, bắn rơi Roc của Wolff, quét sạch đợt máy bay cuối cùng của hắn, rồi giữ căn cứ trước đợt phản kích cuối củ… | Skyhold | Phá hủy | quaden | 1410 xu | Drone hộ vệ |
| c10s1 | **Phụ tùng** phụ Hai xe tải đang chở phụ tùng của Icarus rời căn cứ trong sương. Venn muốn chặn chúng trước khi chúng tới sa mạc. Chúng đã được đánh dấu. | Skyhold | Săn mục tiêu |  | 1620 xu |  |
| c10s2 | **Argus** phụ Argus, khí cầu trinh sát bọc giáp của Raven, đang chỉ điểm cho pháo Hegemon trên các điểm cao Frostpeak. Nadia muốn kiểm tra ba điểm nó đang theo dõi, và bắn hạ khí cầu nếu nó tới gần. | Frostpeak | Trinh sát Argus · Khí cầu trinh sát |  | 1620 xu |  |

#### Chương 11: Skygate

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| c11m01 | **Bãi ray của cửa ngõ** Skygate Array của Aurel được tiếp tế qua bãi ray. Chiếm các ngả giao cắt trong đêm, từ phía bên kia. | Rust Yard | Chiếm cứ điểm | aurel | 590 xu | Siêu tăng |
| c11m02 | **Mắt nhìn cửa ngõ** Nadia muốn tận mắt thấy các trạm radar của cửa ngõ trước khi ta đánh. Đưa xe tới từng trạm, trong mưa. | Skyhold | Trinh sát | aurel | 595 xu |  |
| c11m03 | **Làm mù cửa ngõ** Phá các chảo radar dẫn đường cho tàu của Aurel từ quỹ đạo xuống. | Frostpeak | Phá hủy | aurel | 595 xu | Trạm tiếp tế CP |
| c11m04 | **Bệ phóng phụ** Aurel giấu các bệ phóng phụ quanh cửa ngõ. Tìm ra chúng trước khi hắn nạp nhiên liệu. | Skygate Array | Trinh sát | aurel | 600 xu · HQ 5 | Tháp pháo hạng nặng |
| c11m05 | **Gungnir** Orlov đang chờ ở đầu mối đường sắt của Skygate Array trong Rust Yard cùng Gungnir, khẩu pháo lớn nhất ông ta từng có. Đây là trận cuối của ông ta. Bắt khẩu pháo câm họng. | Rust Yard | Tiêu diệt boss Gungnir · Pháo điện từ đường ray | orlov | 905 xu |  |
| c11m06 | **Giữ sườn núi** Aurel muốn lấy lại sườn núi phía trên cửa ngõ. Giữ nó cho tới khi pháo vào vị trí. | Frostpeak | Giữ cứ điểm | aurel | 605 xu |  |
| c11m07 | **Locust trên cửa ngõ** Một tàu mang drone Locust che chắn bệ phóng phía tây. Đốt các bồn nhiên liệu của tên lửa và bắn hạ tàu mang drone. | Skygate Array | Phá hủy Locust · Tàu con drone | aurel | 610 xu |  |
| c11m11 | **Đoàn xe công binh** Công binh của Mara cần tới xác bệ phóng phía tây của Skygate trước khi người của Aurel dọn sạch. Đưa họ qua Rust Yard trong sương. | Rust Yard | Hộ tống | aurel | 615 xu |  |
| c11m08 | **Nhiên liệu cho Hawk** Nhiên liệu máy bay cho phi đội của Hawk, theo đường bộ qua đèo trong đêm, tới đường băng dã chiến ở trại gỗ. Năm xe bồn phải tới được ba. | Frostpeak | Hộ tống |  | 615 xu |  |
| c11m09 | **Người gác cổng** Viên chỉ huy cửa ngõ của Aurel cố thủ ở phía bên kia đèo. San phẳng sở chỉ huy. | Frostpeak | Đấu tướng | aurel | 620 xu |  |
| c11m12 | **Làm mù Skygate** Radar của Skygate Array chạy bằng các bồn nhiên liệu dưới chân cột ăng-ten. Đốt chúng đi và Hegemon sẽ đánh trận cuối trong cảnh nửa mù, từ bãi phóng Helion tới sa mạc muối. | Skygate Array | Phá hủy Locust · Tàu con drone | aurel | 620 xu |  |
| c11m13 | **Đường tắt** Đường công vụ chạy thẳng tới các bệ phóng. Đi thật nhanh, xem từng bệ phóng rồi rút trước khi Skygate quay pháo lại. Không có thời gian cho việc gì khác. | Skygate Array | Trinh sát | aurel | 930 xu |  |
| c11m10 | **Skygate Array** chiến dịch lớn Chiến dịch giành cửa ngõ: làm mù radar, chọn mục tiêu, phá tuyến phòng thủ, rồi hạ Daedalus khi nó đổ quân của Aurel từ quỹ đạo xuống. Giai đoạn: Làm mù radar trên đồ… | Skygate Array | Phá hủy | aurel | 1495 xu |  |
| c11s1 | **Xe nhiên liệu** phụ Các xe nhiên liệu của Aurel đang chạy tới bệ phóng trong đêm. Săn những chiếc đã đánh dấu. | Skyhold | Săn mục tiêu | aurel | 1720 xu |  |

#### Chương 12: Helion

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| c12m01 | **Trở lại Dunebreak** Con đường tới bãi phóng lại đi qua Dunebreak, lần này từ phía nam. Toán thiết giáp cuối cùng của Varga giữ nhà máy lọc dầu. Chiếm ốc đảo, nhà máy và mỏ dầu. | Dunebreak | Chiếm cứ điểm | varga | 625 xu |  |
| c12m05 | **Locust** Aurel chiếm lấy chương trình drone của Venn khi bà bỏ đi, và vẫn đóng tiếp. Một tàu Locust đang che chắn con đường qua Salt Flats tới Helion. Bắn hạ nó. | Salt Flats | Tiêu diệt boss Locust · Tàu con drone | aurel | 945 xu |  |
| c12m03 | **Xưởng Behemoth cuối cùng** Trại cuối cùng của Varga, giữa những đồi cát nơi hắn chế tạo chiếc Behemoth đầu tiên. Mọi khẩu pháo chống tăng còn lại, và mọi chiếc xe tăng. San phẳng sở chỉ huy của hắn. | Dunebreak | Đấu tướng | varga | 635 xu | Máy phát khiên |
| c12m02 | **Con tàu cuối cùng của Kessler** Kessler gom những con tàu cuối cùng về Beacon Bay, phía bắc Helion, để yểm hộ cuộc phóng từ biển, với Scylla dẫn đầu. San phẳng sở chỉ huy trên bờ của ông ta và đánh… | Beacon Bay | Đấu tướng Scylla · Tàu khu trục | kessler | 635 xu | Tên lửa hành trình |
| c12m04 | **Cận vệ của Aurel** Đội cận vệ riêng của Aurel giữ các bệ phóng phía bắc. San phẳng sở chỉ huy của chúng. | Helion Launch Complex | Đấu tướng | aurel | 640 xu | Nhà chứa drone |
| c12m07 | **Nhiên liệu cho Icarus** Nhiên liệu lò phản ứng của Icarus đang băng qua Salt Flats trong đêm trên ba xe tải có hộ tống. Nadia đã đánh dấu chúng. Chặn từng chiếc một. | Salt Flats | Săn mục tiêu | aurel | 645 xu |  |
| c12m06 | **Sân bay cuối cùng** Sân bay cuối cùng của Hegemon che chắn bệ phóng. Wolff đã không còn; Aurel tự điều khiển máy bay từ xa. San phẳng sở chỉ huy. | Helion Launch Complex | Đấu tướng | aurel | 645 xu |  |
| c12m08 | **Làm mù bãi phóng** Bốn trạm radar dẫn đường cho Icarus rời bệ phóng. Giữa cơn bão cát, phá hủy cả bốn. | Helion Launch Complex | Phá hủy | aurel | 650 xu |  |
| c12m09 | **Hậu vệ nhà máy lọc dầu** Trong khi lữ đoàn tập kết cho trận cuối, Aurel tung vệ binh vào nhà máy lọc dầu, giờ là kho tiếp tế của ta. Giữ nó bốn phút. | Dunebreak | Giữ cứ điểm | aurel | 655 xu |  |
| c12m10 | **Icarus rơi** chiến dịch lớn Trận cuối cùng. Chiếm khu nhiên liệu, chọn đòn đánh, chiếm nhà lắp ráp, tiêu diệt xe chỉ huy của Aurel, giữ bệ phóng, và khi Icarus rời bệ phóng lên quỹ đạo trong hình d… | Helion Launch Complex | Chiếm cứ điểm | aurel | 1575 xu |  |

#### Kể chuyện

- Briefing dạng thẻ có chân dung người giao nhiệm vụ.
- Thoại trong trận: dải chân dung nhỏ và tối đa 2 dòng trên khay thẻ, theo kịch bản từng màn và hàng đợi ưu tiên P0–P4 (phần 2c).
- Camera lia trong trận khi boss, chi viện hoặc tướng địch xuất hiện; không có cutscene.
- Màn chuyển chương có tóm tắt 3–4 câu; sau chương 9 là **Kết mạch Thorne** (đoạn chuyển, trước chương 15); phần kết thật của game sau c12m10, và thắng c12m10 mở cấp Huyền thoại của chế độ Tác chiến.
- Mục Hồ sơ trong menu: tiểu sử nhân vật, hồ sơ boss, dòng thời gian, các mẩu truyện mỗi nhiệm vụ trao.

#### Phần thưởng và kinh tế chiến dịch

Mỗi chương mở 5–7 thẻ (xe, tháp, thẻ hỗ trợ), một cấp sở chỉ huy ở các chương 1/3/5/7/9 và một mô-đun tiện ích (chương 1–5; các chương sau trao một món đồ tháp). Mỗi nhiệm vụ trả bản thiết kế, xu và một mẩu truyện; nhiệm vụ phụ trả bản thiết kế hiếm hoặc đồ tháp. Boss bay chỉ xuất hiện khi người chơi đã có ít nhất hai thẻ phòng không mặt đất. Người chơi chỉ đánh chiến dịch đưa bộ bài chính (8 thẻ + 6 tháp) lên hạng 7,0 khi bắt đầu hồi III và 8,1 ở cuối chiến dịch.

Sheet: 07_chien_dich_cot_truyen/Chuong — Chương (15 dòng, 14 cột)

| id | maps | main | minis | general | tep_thoai_chuong | tep_thoai | so_cau_thoai | act | comic |
|---|---|---|---|---|---|---|---|---|---|
| 1 | landingbeach;greenvale;ashfield | fortress_bastion | bastion_mk0 | brandt | 1 | ch01.json | 82 | 1 | comic.1 |
| 2 | dunebreak;redrock | behemoth | behemoth_inferno | varga | 2 | ch02.json | 108 | 1 | comic.2 |
| 3 | whiteout;frostpeak | mobile_fortress | mega_gunship;fenrir | orlov | 3 | ch03.json | 111 | 1 | comic.3 |
| 4 | rustyard;ironport;lighthousebay | leviathan | behemoth_tempest;armored_train;scylla | kessler | 4 | ch04.json | 164 | 2 | comic.4 |
| 5 | junglepass;emberridge | drone_mothership | locust;fortress_hive | sen | 5 | ch05.json | 121 | 2 | comic.5 |
| 6 | ashfield;whiteout;greenvale;landingbeach;hydrodam | moloch | landing_hovercraft;behemoth_mk2 | varga | 6 | ch06.json | 153 | 2 | comic.6 |
| 7 | metrocity;veyra_old_quarter;capital | nuke_train | supreme_command;behemoth_inferno;armored_train | hung | 7 | ch07.json | 149 | 3 | comic.7 |
| 8 | redrock;openpit;hydrodam;dunebreak | kronos | ixion;earth_borer | hung | 8 | ch08.json | 129 | 3 | comic.8 |
| 9 | ironport;landingbeach;lighthousebay;coralisles | typhon | caspian;scylla | hung | 9 | ch09.json | 131 | 3 | comic.9 |
| 10 | frostpeak;skyhold;whiteout | command_airship | sky_fortress;icarus_mk0;argus;morrigan | quaden | 10 | ch10.json | 134 | 4 | comic.10 |
| 11 | rustyard;skyhold;frostpeak;orbitalgate | daedalus | rail_supergun;locust | aurel | 11 | ch11.json | 120 | 4 | comic.11 |
| 12 | launchsite;saltflat;dunebreak;lighthousebay | silver_bug | behemoth_mk2;scylla;locust | aurel | 12 | ch12.json | 93 | 4 | comic.12 |
| 13 | foundry |  | behemoth_mk0 | varga | 13 | ch13.json | 35 | 1 | comic.13 |
| 14 | swamp;borderbridge |  | locust |  | 14 | ch14.json | 44 | 2 | comic.14 |
| 15 | frostpeak;junglepass |  | morrigan | quaden | 15 | ch15.json | 40 | 3 | comic.15 |

*in 10 / 14 cột; 2 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 07_chien_dich_cot_truyen/Nhiem_vu — Nhiệm vụ (193 dòng, 99 cột)

| id | chapter | map | general | enemy_deck | unlocks | after | boss_def | nguoi_noi_chinh | bo_bai_game |
|---|---|---|---|---|---|---|---|---|---|
| c1m01 | 1 | landingbeach |  | scout_jeep;armored_car | rocket_technical |  |  | khai | TRUE |
| c1m02 | 1 | landingbeach |  | scout_jeep;armored_car;light_tank;rocket_technical;ifv | mortar_carrier |  |  | linh | FALSE |
| c1m03 | 1 | greenvale |  | scout_jeep;armored_car;light_tank | repair_drop |  |  | linh | FALSE |
| c1m04 | 1 | greenvale |  | scout_jeep;armored_car;light_tank;rocket_technical;ifv | rocket_turret;repair_bay |  |  | mai | FALSE |
| c1m05 | 1 | greenvale |  | armored_car;light_tank;ifv;main_battle_tank;mortar_carrier;… | light_tank |  | bastion_mk0 | mai | FALSE |
| c1m06 | 1 | greenvale |  |  | zu23_technical |  |  | khai | FALSE |
| c1m08 | 1 | ashfield |  | armored_car;light_tank;ifv;main_battle_tank;mortar_carrier;… | minefield |  |  | linh | FALSE |
| c1m09 | 1 | ashfield |  |  | engineer_vehicle |  |  | khai | FALSE |
| c1m10 | 1 | ashfield |  | armored_car;light_tank;ifv;main_battle_tank;mortar_carrier;… |  |  |  | khai | FALSE |
| c1s1 | 1 | greenvale |  | scout_jeep;armored_car;light_tank;rocket_technical;ifv |  | c1m03 |  | linh | FALSE |
| c2m01 | 2 | dunebreak | varga |  | aa_vehicle |  |  | khai | FALSE |
| c2m02 | 2 | redrock | varga | armored_car;light_tank;main_battle_tank;ifv;tank_destroyer;… | artillery |  |  | linh | FALSE |
| c2m03 | 2 | redrock |  |  | flame_tank |  |  | khai | FALSE |
| c2m04 | 2 | dunebreak | varga | armored_car;light_tank;main_battle_tank;ifv;tank_destroyer;… | airstrike |  |  | khai | TRUE |
| c2m05 | 2 | dunebreak | varga | armored_car;light_tank;main_battle_tank;ifv;tank_destroyer;… | ammo_carrier |  | behemoth_inferno | mai | FALSE |

*15 / 193 dòng đầu: xem sheet 07_chien_dich_cot_truyen/Nhiem_vu; in 10 / 99 cột; 61 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 07_chien_dich_cot_truyen/Nhan_vat — Nhân vật (21 dòng, 8 cột)

| id | triggers | chan_dung | name | note | roles |
|---|---|---|---|---|---|
| adler | point_captured;point_lost | NEED_CODE_CHECK | Đại úy Adler |  | ground held;territory |
| aurel | mission_start;boss_spawn;victory;defeat | NEED_CODE_CHECK | Giám đốc Lucien Aurel | direct from chapter 11; before, at most one line a chapter… | enemy director |
| brandt | phase_start;mission_start;boss_spawn;victory;defeat | NEED_CODE_CHECK | Thiếu tá Brandt |  | fortification |
| brenn | objective_progress | NEED_CODE_CHECK | Thiếu tá Brenn |  | logistics;paperwork |
| dahl | event_triggered;objective_progress | NEED_CODE_CHECK | Thiếu tá Dahl |  | artillery;ballistics;bridges |
| dieuhau | first_unit_type_seen;objective_progress;momentum_high_once | NEED_CODE_CHECK | Trung úy Jonah Reyes |  | air |
| hq | objective_progress;event_triggered;enemy_reinforcement;time… | NEED_CODE_CHECK | Command |  | command net |
| hung | ally_arrives;ally_late;mission_start;boss_spawn;victory;def… | NEED_CODE_CHECK | Tướng Roland Thorne | ally_late only before chapter 7 | ally commander |
| kessler | mission_start;boss_spawn;victory;defeat | NEED_CODE_CHECK | Đô đốc Magnus Kessler |  | enemy general |
| khai | mission_start;phase_start;critical_failure_imminent;victory… | NEED_CODE_CHECK | Đại tá Marcus Kade |  | command |
| linh | enemy_reinforcement;general_tactic_change;first_unit_type_s… | NEED_CODE_CHECK | Đại úy Nadia Kerr |  | intelligence;anomaly |
| mai | boss_spawn;boss_part_destroyed;hq_below_50;neutral_captured | NEED_CODE_CHECK | Kỹ sư Mara Lind |  | mechanics;base;Behemoth |
| mendez | objective_progress;critical_failure_imminent | NEED_CODE_CHECK | Đại úy Kaia Mendez |  | movement;escort urgency |
| okoye | objective_progress | NEED_CODE_CHECK | Đại úy Okoye |  | logistics;fuel;airfield |
| orlov | mission_start;boss_spawn;victory;defeat | NEED_CODE_CHECK | Đại tá Ilya Orlov |  | enemy general |
| quaden | mission_start;boss_spawn;victory;defeat | NEED_CODE_CHECK | Kasimir Wolff |  | enemy ace |
| quist | neutral_captured;objective_progress | NEED_CODE_CHECK | Thượng sĩ Quist |  | salvage |
| reyn | mission_start;victory | NEED_CODE_CHECK | Đại tá Reyn |  | unit tradition;rescue duty |
| sen | first_unit_type_seen;event_triggered;mission_start;boss_spa… | NEED_CODE_CHECK | Tiến sĩ Elara Venn |  | drone;network;system |
| varga | mission_start;boss_spawn;victory;defeat | NEED_CODE_CHECK | Tướng Viktor Varga |  | enemy general |
| varro | point_captured | NEED_CODE_CHECK | Đại úy Varro |  | miners;tunnels |

Sheet: 07_chien_dich_cot_truyen/Thoai — Thoại (1614 dòng, 19 cột)

| id | nhiem_vu_id | thu_tu | trigger | nguoi_noi | khoa_loc | uu_tien | mot_lan_hay_lap | dieu_kien_arg | dieu_kien_at_s |
|---|---|---|---|---|---|---|---|---|---|
| script.c1m01.01 | c1m01 | 0 | mission_start | khai | script.c1m01.01 | 1 | TRUE |  |  |
| script.c1m01.02 | c1m01 | 1 | time | linh | script.c1m01.02 | 2 | TRUE |  | 20.0 |
| script.c1m01.03 | c1m01 | 2 | point_captured | dieuhau | script.c1m01.03 | 3 | TRUE | east |  |
| script.c1m01.04 | c1m01 | 3 | objective_progress | linh | script.c1m01.04 | 2 | TRUE | last |  |
| script.c1m01.05 | c1m01 | 4 | critical_failure_imminent | khai | script.c1m01.05 | 1 | TRUE |  |  |
| script.c1m01.06 | c1m01 | 5 | victory | khai | script.c1m01.06 | 1 | TRUE |  |  |
| script.c1m01.07 | c1m01 | 6 | defeat | khai | script.c1m01.07 | 1 | TRUE |  |  |
| script.c1m01.08 | c1m01 | 7 | time | linh | script.c1m01.08 | 2 | TRUE |  | 60.0 |
| script.c1m02.01 | c1m02 | 8 | mission_start | linh | script.c1m02.01 | 1 | TRUE |  |  |
| script.c1m02.02 | c1m02 | 9 | time | linh | script.c1m02.02 | 2 | TRUE |  | 40.0 |
| script.c1m02.03 | c1m02 | 10 | enemy_reinforcement | linh | script.c1m02.03 | 3 | TRUE |  |  |
| script.c1m02.04 | c1m02 | 11 | event_triggered | hq | script.c1m02.04 | 2 | TRUE |  |  |
| script.c1m02.05 | c1m02 | 12 | timer_60s | khai | script.c1m02.05 | 1 | TRUE |  |  |
| script.c1m02.06 | c1m02 | 13 | victory | khai | script.c1m02.06 | 1 | TRUE |  |  |
| script.c1m02.07 | c1m02 | 14 | defeat | linh | script.c1m02.07 | 1 | TRUE |  |  |

*15 / 1614 dòng đầu: xem sheet 07_chien_dich_cot_truyen/Thoai; in 10 / 19 cột; 7 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 07_chien_dich_cot_truyen/Trigger_thoai — Trigger thoại (27 dòng, 6 cột)

| id | loai | so_cau | hoi_chieu_so_lan |
|---|---|---|---|
| ally_arrives | chi_dung | 2 | NEED_CODE_CHECK |
| ally_late | chi_dung | 3 | NEED_CODE_CHECK |
| boss_hp | scripted | 68 | NEED_CODE_CHECK |
| boss_part_destroyed | chi_dung | 38 | NEED_CODE_CHECK |
| boss_phase_change | scripted | 31 | NEED_CODE_CHECK |
| boss_spawn | chi_dung | 50 | NEED_CODE_CHECK |
| critical_failure_imminent | main | 44 | NEED_CODE_CHECK |
| defeat | main | 193 | NEED_CODE_CHECK |
| enemy_reinforcement | chi_dung | 8 | NEED_CODE_CHECK |
| event_triggered | scripted | 158 | NEED_CODE_CHECK |
| expensive_unit_lost | chi_dung | 15 | NEED_CODE_CHECK |
| first_unit_type_seen | chi_dung | 14 | NEED_CODE_CHECK |
| general_tactic_change | chi_dung | 13 | NEED_CODE_CHECK |
| hq_below_50 | chi_dung | 20 | NEED_CODE_CHECK |
| mission_start | main | 217 | NEED_CODE_CHECK |
| momentum_high_once | main | 5 | NEED_CODE_CHECK |
| neutral_captured | nhan_vat | 0 | NEED_CODE_CHECK |
| objective_progress | scripted | 149 | NEED_CODE_CHECK |
| objective_stall_90s | main | 1 | NEED_CODE_CHECK |
| phase_end | scripted | 0 | NEED_CODE_CHECK |
| phase_start | scripted | 46 | NEED_CODE_CHECK |
| point_captured | scripted | 55 | NEED_CODE_CHECK |
| point_lost | scripted | 25 | NEED_CODE_CHECK |
| superweapon_warning | scripted | 38 | NEED_CODE_CHECK |
| time | scripted | 142 | NEED_CODE_CHECK |
| timer_60s | chi_dung | 20 | NEED_CODE_CHECK |
| victory | main | 259 | NEED_CODE_CHECK |

Sheet: 05_che_do_kinh_te/Sao_chien_dich — Sao chiến dịch theo mục tiêu (15 dòng, 7 cột)

| id | sao2_kind | sao2_value | sao3_kind | sao3_value |
|---|---|---|---|---|
| Boss | BossParts | 2 | NoAircraft |  |
| Capture | LossShare | 0.4 | Kills | 10 |
| Destroy | LossShare | 0.4 | NoStrikes |  |
| Duel | HqShare | 0.5 | Kills | 15 |
| Escort | ConvoyShare | 0.8 | Kills | 10 |
| Evacuate | ConvoyShare | 0.8 | Kills | 10 |
| Hold | HoldShare | 0.8 | Kills | 15 |
| Hunt | LossShare | 0.4 | Kills | 10 |
| Intercept | LossShare | 0.4 | NoStrikes |  |
| Outpost | HoldShare | 0.8 | Kills | 12 |
| Protect | ProtectShare | 0.75 | Kills | 15 |
| Recon | ReconQuiet | 0.67 | NoStrikes |  |
| Relieve | LossShare | 0.4 | Kills | 12 |
| ShootDown | LossShare | 0.4 | Kills | 12 |
| Survive | HqShare | 0.5 | Kills | 20 |

Sheet: 07_chien_dich_cot_truyen/Phat_hanh — Phát hành (3 dòng, 8 cột)

| id | khoa | gia_tri_chu |
|---|---|---|
| acts | acts | 1;2;3;4 |
| chaptersOff | chaptersOff |  |
| switchedOff | switchedOff | comingSoon |

### 3b. Bộ bài game

Trạng thái: Đã áp

Nguồn dữ liệu: 07_chien_dich_cot_truyen/Bo_bai_game; 07_chien_dich_cot_truyen/Bo_bai_game_dong_minh. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §Prompt 31: Màn bộ bài game.

23 màn dùng bộ bài do game định sẵn (8 thẻ xe + 2 thẻ hỗ trợ, không sửa được, hạng thẻ theo đường cong hạng của chương, không trang bị). Thẻ chưa mở khóa là thẻ **mượn** ("Mượn trong nhiệm vụ này"): dùng được trong màn, không mở khóa vĩnh viễn, tối đa 2 thẻ một màn (c1m01: 4, vì người chơi mới chỉ có 4 thẻ xe); các thẻ khóa khác của bảng được thay bằng thẻ đã mở cùng vai trò. Đồng minh đặt sẵn không chiếm ô thẻ, do AI đồng minh điều khiển theo lệnh Tấn công/Phòng thủ chung. Mục tiêu gốc của mọi màn giữ nguyên.

| Màn | Trạng thái | Thẻ xe | Thẻ hỗ trợ | Đồng minh đặt sẵn | Luật riêng |
|---|---|---|---|---|---|
| **c1m01** | Làm trước | **Xe lội nước tốc độ cao** (mượn), **Tăng nhẹ lội nước** (mượn), Xe bọc thép bánh lốp, **Bán tải rốc-két** (mượn), **Xe cối tự hành** (mượn), Xe chiến đấu bộ binh, Tăng chủ lực, Xe trinh sát hạng nhẹ | Màn khói, Pháo kích | — | Không có căn cứ lúc đầu trận: lữ đoàn lên bờ với những gì mang theo. Quân tiếp viện chỉ thả xuống dải bãi biển. Pháo bờ biển bắn theo nhịp; mỗi loạt đều được cảnh báo trước khi rơi. |
| **c2m04** | Làm trước | Xe bọc thép bánh lốp, Xe trinh sát hạng nhẹ, **Xe bom bọc thép** (mượn), Bán tải rốc-két, Xe chiến đấu bộ binh, Tăng nhẹ lội nước, Bán tải cao xạ, **Xe phá mìn bằng dây nổ** (mượn) | Màn khói, Sửa chữa | — | Đột kích không căn cứ: vào nhanh, ra nhanh hơn. |
| **c2s2** | Làm trước | Bán tải cao xạ, Pháo cao xạ tự hành, **Xe tên lửa phòng không nhẹ** (mượn), **Xe cao xạ 40 mm** (mượn), Xe bọc thép bánh lốp, Xe chiến đấu bộ binh, Xe công binh, Xe tiếp đạn | Màn khói, Sửa chữa | — | Trực thăng tới theo đợt, từ hướng được cảnh báo. |
| **c3m06** | Làm trước | Xe trinh sát hạng nhẹ, **Xe trinh sát bọc thép radar mặt đất** (mượn), Xe radar phản pháo, Xe cối tự hành, Lựu pháo tự hành, Trực thăng tấn công, UAV trinh sát, Xe bọc thép bánh lốp | **Phản pháo tức thì** (mượn), UAV quét | — | Ban đêm: pháo địch chỉ lộ khi khai hỏa và đổi chỗ sau mỗi loạt. Radar phản pháo sẽ tìm ra chúng. |
| **i1m01** | Làm sau | Xe trinh sát hạng nhẹ, **Xe trinh sát bọc thép radar mặt đất** (mượn), Xe bọc thép bánh lốp, Bán tải rốc-két, Tăng nhẹ lội nước, Xe thả khói, **Xe gây nhiễu điện tử** (mượn), Xe công binh | Màn khói, UAV quét | — | Lọt vào mà không bị phát hiện. Nếu địch thấy ta, còi báo động vang lên: cổng xưởng cán đóng lại và đồn binh kéo tới. |
| **c4m05** | Làm trước | Xe công binh, Xe bom bọc thép, Xe rải mìn, Pháo chống tăng tự hành, Lựu pháo tự hành, Pháo xung kích bánh lốp, **Pháo chống tăng kéo cỡ lớn** (mượn), Xe trinh sát hạng nhẹ | **Mìn rải từ xa** (mượn), Pháo kích | — | {seconds} giây để đặt bẫy trước khi đoàn tàu chạy. |
| **c4m06** | Làm trước | **Tàu tuần tra sông** (mượn), **Pháo hạm sông** (mượn), Xe chiến đấu bộ binh, Xe pháo điện từ, Tăng nhẹ lội nước, Trực thăng tấn công, Trực thăng trinh sát vũ trang, Pháo cao xạ tự hành | Pháo kích, Màn khói | — | Phần lớn là nước, trong sương: ai giữ hải đăng thì thấy mặt biển. |
| **c5m03** | Làm sau | **Xe vi sóng chống drone** (mượn), **Xe drone đánh chặn** (mượn), Pháo cao xạ tự hành, Bán tải cao xạ, Xe công binh, Xe thả khói, Xe bọc thép bánh lốp, Xe chiến đấu bộ binh | UAV quét, Màn khói | — | Bầy drone của Venn lao ra từ tán rừng theo hướng được cảnh báo. Bộ bài dựng để chống drone: giữ đoàn xe bắc cầu sống sót. |
| **c5m07** | Làm trước | Tiêm kích, Trực thăng trinh sát vũ trang, Trực thăng tấn công, UAV tấn công, Xe tên lửa phòng không tầm trung, Xe gây nhiễu điện tử, **Xe la-de phòng không** (mượn), Pháo cao xạ tự hành | **Đòn tên lửa đánh chặn drone** (mượn), UAV quét | — | Tối đa 6 máy bay cùng lúc, như mọi trận. |
| **c6m03** | Làm sau | **Xe sửa chữa lưu động** (mượn), Xe tiếp đạn, Xe công binh, Pháo cao xạ tự hành, Xe chiến đấu bộ binh, Xe thả khói, Pháo chống tăng tự hành, Xe trinh sát hạng nhẹ | Sửa chữa, Màn khói | behemoth_mara (Behemoth · Quái vật thép), là đoàn hộ tống, thua nếu bị phá | Behemoth của {@mai} là của ta: hộ tống nó tới cuối đường. Nó dừng lại khi lệnh là Phòng thủ; nếu nó bị hạ, nhiệm vụ thất bại. |
| **c6m14** | Làm sau | **Xe vi sóng chống drone** (mượn), Xe la-de phòng không, **Xe drone đánh chặn** (mượn), Bán tải cao xạ, Pháo cao xạ tự hành, Xe công binh, Xe ủi bọc thép, Xe tiếp đạn | UAV quét, Màn khói | — | Cánh quân của Varga giữ lệnh ngừng bắn suốt trận: không vũ khí nào của ta nhắm hay gây sát thương được cho họ, nên không phát bắn lạc nào phá được nó. Kẻ địch là drone của Aurel. |
| **i2m01** | Làm sau | Xe bọc thép bánh lốp, Xe chiến đấu bộ binh, **Xe lội nước tốc độ cao** (mượn), **Tăng nhẹ thả dù** (mượn), Xe trinh sát hạng nhẹ, Pháo cao xạ tự hành, Xe thả khói, Xe công binh | Màn khói, UAV quét | — | Nhẹ và nhanh trong sương: chiếm hai làng và ngôi đền chìm trước khi địch kịp thấy ta tới. |
| **c7m16** | Làm sau | Tăng chủ lực, Tăng hạng nặng, Xe hỗ trợ tăng, Xe chiến đấu bộ binh, Pháo cao xạ tự hành, Pháo phản lực dẫn đường, Pháo chống tăng tự hành, Lựu pháo tự hành | Pháo kích, Không kích | — | Ta chiến đấu bằng đạo quân của {@lyhan}. Giữa trận, cánh quân của ông ấy đổi hướng theo tin tình báo mới, rồi quay lại. |
| **c7m11** | Làm trước | **Xe phòng không 57 mm** (mượn), Xe phòng không pháo – tên lửa, Xe la-de phòng không, Xe tên lửa phòng không tầm trung, Bán tải cao xạ, **Xe tên lửa phòng không nhẹ** (mượn), UAV trinh sát, Xe chiến… | UAV quét, Không kích | — | Tối đa 6 máy bay cùng lúc, như mọi trận. Giữa trận, điện thành phố mất: trời tối hẳn và các tháp nối lưới điện ngừng hoạt động một lúc, của địch lẫn của ta. |
| **c8m11** | Làm trước | **Xe khi hỏng thành công sự** (mượn), Xe ủi bọc thép, Bán tải rốc-két, Bán tải cao xạ, **Xe jeep súng không giật** (mượn), Xe cối tự hành, Xe công binh, Xe bom bọc thép | Pháo kích, Màn khói | — | Bộ bài chắp vá của Varro: rẻ, nhiều, liều. |
| **c9m12** | Làm sau | **Xe lội nước tốc độ cao** (mượn), Tăng nhẹ lội nước, Pháo phản lực dẫn đường, **Tàu tuần tra sông** (mượn), Xe pháo điện từ, Trực thăng tấn công, Xe tên lửa phòng không tầm trung, Xe bọc thép bánh l… | Pháo kích, Màn khói | — | Nhảy đảo: chiếm điểm trên một đảo rồi vượt sang đảo kế. Đảo giữa là then chốt của cả hai bên. |
| **c9m08** | Làm trước | **Xe tên lửa chống hạm bờ biển** (mượn), **Xe phóng tên lửa hành trình** (mượn), Trực thăng tấn công, Máy bay cường kích, UAV trinh sát, Pháo phản lực dẫn đường, Xe tên lửa phòng không tầm trung, Xe… | Không kích, Màn khói | — | Pháo phòng thủ tầm gần của Scylla bắn hạ tên lửa: phóng dồn một lúc, hoặc phá pháo đó trước. |
| **i3m02** | Làm trước | Xe tên lửa phòng không tầm xa, Xe tên lửa phòng không tầm trung, Pháo cao xạ tự hành, UAV trinh sát, **Xe phòng không 57 mm** (mượn), Xe la-de phòng không, Xe phòng không pháo – tên lửa, Xe công binh | **Mồi nhử thả dù** (mượn), Màn khói | — | Morrigan săn phòng không: bắn xong thì đổi chỗ. Mồi nhử kéo hỏa lực của nó. |
| **i3m03** | Làm trước | Tăng hạng nặng, **Tăng thế hệ mới** (mượn), Tăng chủ lực, Xe hỗ trợ tăng, Tăng hai nòng, Xe phòng không pháo – tên lửa, **Xe sửa chữa lưu động** (mượn), Xe tiếp đạn | Sửa chữa, Pháo kích | — | Thiết giáp tinh nhuệ của Crown: mọi thẻ cao hơn đường cong chiến dịch một cấp. |
| **c10m11** | Làm sau | Xe tên lửa phòng không tầm trung, **Xe phòng không 57 mm** (mượn), Xe la-de phòng không, Xe phòng không pháo – tên lửa, **Xe radar phòng không di động** (mượn), Tăng chủ lực, Xe chiến đấu bộ binh, Xe… | Tháp dã chiến, Sửa chữa | — | Giữ đường băng dã chiến trong lúc máy bay vận tải hạ cánh: đồng hồ giữ điểm là bộ đếm hạ cánh. Tối đa 6 máy bay cùng lúc. |
| **c10m12** | Làm sau | Tiêm kích, **Drone hộ vệ** (mượn), Xe tên lửa phòng không tầm trung, UAV trinh sát, Xe phòng không pháo – tên lửa, Xe la-de phòng không, Tiêm kích tàng hình, Pháo cao xạ tự hành | **Rải nhiễu radar** (mượn), Đòn SEAD | hawk_jet (Tiêm kích), thua nếu bị phá | {@dieuhau} bay cùng ta theo lệnh chung. Giữ phi đội của Raven tránh xa anh ấy: nếu chiếc tiêm kích của anh ấy rơi, nhiệm vụ thất bại. |
| **c11m13** | Làm trước | **Máy bay trinh sát tốc độ cao** (mượn), Trực thăng trinh sát vũ trang, Xe bọc thép bánh lốp, Xe trinh sát hạng nhẹ, Xe thả khói, Xe gây nhiễu điện tử, **Xe gây nhiễu định vị** (mượn), Tăng nhẹ lội n… | Màn khói, Đòn SEAD | — | Chạy đua với giờ: xem từng bệ phóng rồi rút trước khi Skygate quay pháo. |
| **c12m03** | Làm sau | Tăng chủ lực, Xe hỗ trợ tăng, Pháo chống tăng tự hành, **Xe sửa chữa lưu động** (mượn), Xe tiếp đạn, Pháo phản lực dẫn đường, Xe tên lửa phòng không tầm trung, Xe công binh | Sửa chữa, Pháo kích | behemoth_mara_repainted (mara_behemoth) | Behemoth của {@mai}, đã sơn lại, chiến đấu bên ta theo lệnh chung: khi Tấn công nó nhắm vào sở chỉ huy địch, khi Phòng thủ nó giữ quanh căn cứ ta. |

Sheet: 07_chien_dich_cot_truyen/Bo_bai_game — Bộ bài game (23 dòng, 13 cột)

| id | nhiem_vu_id | vehicle_ids | support_ids | loaned_cards | muc_tieu_goc_giu | prep_seconds | rank_bonus | special_rules | status |
|---|---|---|---|---|---|---|---|---|---|
| c1m01 | c1m01 | amphib_light_vehicle;light_tank;armored_car;rocket_technica… | smoke_screen;artillery_barrage | amphib_light_vehicle;light_tank;rocket_technical;mortar_car… | NEED_CODE_CHECK |  |  | noBaseStart;beachLanding;coastalGuns | MAKE_FIRST |
| c2m04 | c2m04 | armored_car;scout_jeep;vbied;rocket_technical;ifv;light_tan… | smoke_screen;repair_drop | vbied;demolition_line_vehicle | NEED_CODE_CHECK |  |  | raidNoBase | MAKE_FIRST |
| c2s2 | c2s2 | zu23_technical;aa_vehicle;shorad_vehicle;aa_gun_vehicle;arm… | smoke_screen;repair_drop | shorad_vehicle;aa_gun_vehicle | NEED_CODE_CHECK |  |  | warnedAirWaves | MAKE_FIRST |
| c3m06 | c3m06 | scout_jeep;radar_scout;counter_battery_radar;mortar_carrier… | instant_counter_battery;uav_scan | radar_scout;instant_counter_battery | NEED_CODE_CHECK |  |  | nightGuns | MAKE_FIRST |
| c4m05 | c4m05 | engineer_vehicle;vbied;mine_layer;tank_destroyer;artillery;… | remote_mines;artillery_barrage | towed_at_gun;remote_mines | NEED_CODE_CHECK | 60 |  | trainPrep | MAKE_FIRST |
| c4m06 | c4m06 | river_patrol_boat;river_gunboat;ifv;railgun_truck;light_tan… | artillery_barrage;smoke_screen | river_patrol_boat;river_gunboat | NEED_CODE_CHECK |  |  | seaFogLighthouse | MAKE_FIRST |
| c5m03 | c5m03 | microwave_vehicle;interceptor_drone_vehicle;aa_vehicle;zu23… | uav_scan;smoke_screen | microwave_vehicle;interceptor_drone_vehicle | NEED_CODE_CHECK |  |  | droneCanopy | MAKE_LATER |
| c5m07 | c5m07 | fighter_jet;scout_heli;attack_helicopter;strike_drone;sam_l… | drone_intercept_strike;uav_scan | iron_beam;drone_intercept_strike | NEED_CODE_CHECK |  |  | airCap6 | MAKE_FIRST |
| c6m03 | c6m03 | mobile_repair_vehicle;ammo_carrier;engineer_vehicle;aa_vehi… | repair_drop;smoke_screen | mobile_repair_vehicle | NEED_CODE_CHECK |  |  | behemothOurs | MAKE_LATER |
| c6m14 | c6m14 | microwave_vehicle;iron_beam;interceptor_drone_vehicle;zu23_… | uav_scan;smoke_screen | microwave_vehicle;interceptor_drone_vehicle | NEED_CODE_CHECK |  |  | ceasefireFaction | MAKE_LATER |
| c7m11 | c7m11 | aa_57mm_vehicle;heavy_aa;iron_beam;sam_launcher;zu23_techni… | uav_scan;airstrike | aa_57mm_vehicle;shorad_vehicle | NEED_CODE_CHECK |  |  | airCap6;cityBlackout | MAKE_FIRST |
| c7m16 | c7m16 | main_battle_tank;heavy_tank;bmpt;ifv;aa_vehicle;mlrs;tank_d… | artillery_barrage;airstrike |  | NEED_CODE_CHECK |  |  | thorneAnomaly | MAKE_LATER |
| c8m11 | c8m11 | combat_wreck_car;armored_bulldozer;rocket_technical;zu23_te… | artillery_barrage;smoke_screen | combat_wreck_car;recoilless_jeep | NEED_CODE_CHECK |  |  | patchworkDeck | MAKE_FIRST |
| c9m08 | c9m08 | coastal_ashm_vehicle;ground_cruise_missile_vehicle;attack_h… | airstrike;smoke_screen | coastal_ashm_vehicle;ground_cruise_missile_vehicle | NEED_CODE_CHECK |  |  | ciwsSaturate | MAKE_FIRST |
| c9m12 | c9m12 | amphib_light_vehicle;light_tank;mlrs;river_patrol_boat;rail… | artillery_barrage;smoke_screen | amphib_light_vehicle;river_patrol_boat | NEED_CODE_CHECK |  |  | islandHop | MAKE_LATER |
| c10m11 | c10m11 | sam_launcher;aa_57mm_vehicle;iron_beam;heavy_aa;radar_suppo… | field_tower;repair_drop | aa_57mm_vehicle;radar_support_vehicle | NEED_CODE_CHECK |  |  | airfieldLanding | MAKE_LATER |
| c10m12 | c10m12 | fighter_jet;wingman_drone;sam_launcher;recon_drone;heavy_aa… | chaff_strike;sead_strike | wingman_drone;chaff_strike | NEED_CODE_CHECK |  |  | hawkWingman | MAKE_LATER |
| c11m13 | c11m13 | recon_jet;scout_heli;armored_car;scout_jeep;smoke_carrier;e… | smoke_screen;sead_strike | recon_jet;gps_jammer_vehicle | NEED_CODE_CHECK |  |  | timedRecon | MAKE_FIRST |
| c12m03 | c12m03 | main_battle_tank;bmpt;tank_destroyer;mobile_repair_vehicle;… | repair_drop;artillery_barrage | mobile_repair_vehicle | NEED_CODE_CHECK |  |  | maraBehemoth | MAKE_LATER |
| i1m01 | i1m01 | scout_jeep;radar_scout;armored_car;rocket_technical;light_t… | smoke_screen;uav_scan | radar_scout;ew_jammer | NEED_CODE_CHECK |  |  | factoryAlarm | MAKE_LATER |
| i2m01 | i2m01 | armored_car;ifv;amphib_light_vehicle;airborne_light_tank;sc… | smoke_screen;uav_scan | amphib_light_vehicle;airborne_light_tank | NEED_CODE_CHECK |  |  | mirewoodFog | MAKE_LATER |
| i3m02 | i3m02 | long_sam;sam_launcher;aa_vehicle;recon_drone;aa_57mm_vehicl… | decoy_paradrop;smoke_screen | aa_57mm_vehicle;decoy_paradrop | NEED_CODE_CHECK |  |  | morriganDecoys | MAKE_FIRST |
| i3m03 | i3m03 | heavy_tank;next_gen_tank;main_battle_tank;bmpt;twin_tank;he… | repair_drop;artillery_barrage | next_gen_tank;mobile_repair_vehicle | NEED_CODE_CHECK |  | 1 | eliteRank | MAKE_FIRST |

Sheet: 07_chien_dich_cot_truyen/Bo_bai_game_dong_minh — Bộ bài game: đồng minh đặt sẵn (3 dòng, 13 cột)

| id | bo_bai_game_id | thu_tu | def | convoy | fallback | heading_deg | loss_if_destroyed | name | x_m |
|---|---|---|---|---|---|---|---|---|---|
| c6m03/0 | c6m03 | 0 | behemoth | TRUE |  | 225 | TRUE | behemoth_mara | 100 |
| c10m12/0 | c10m12 | 0 | fighter_jet |  |  | 225 | TRUE | hawk_jet | 92 |
| c12m03/0 | c12m03 | 0 | mara_behemoth |  | behemoth | 225 |  | behemoth_mara_repainted | 96 |

*in 10 / 13 cột; 1 cột khác (và raw_json, nguon): xem sheet.*

### 3c. Biến cố và sự kiện trong nhiệm vụ

Trạng thái: Đã áp

Nguồn dữ liệu: 07_chien_dich_cot_truyen/Bien_co; 07_chien_dich_cot_truyen/Bien_co_luat; 07_chien_dich_cot_truyen/Nhiem_vu_bien_co. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §Prompt 31: Biến cố, §7c.

#### Prompt 31: Biến cố

Mọi biến cố đổi đường đi dùng trạng thái đường đi **dựng sẵn** (dựng và kiểm khi tải trận, không khoét lúc chạy), chỉ đổi ở ranh giới tick, mọi trạng thái đều còn đường vòng (kiểm lúc dựng chiến dịch và lúc tải trận), không nhốt xe (xe trên vùng vừa đóng được đặt ra ngoài), cảnh báo 8-12 giây bằng thông báo hệ thống và dấu trên bản đồ nhỏ (thoại chỉ là phụ), xảy ra theo đồng hồ trận hoặc điều kiện nên chơi lại cho cùng kết quả. Mây thấp bỏ (cần lối chơi theo độ cao). c9m02 và c7m17 là chiến trường đảo chiều nên không dùng trạng thái dựng sẵn; giữ biến cố cũ.

| Biến cố | Loại | Màn: lúc nào | Thay đổi | Trạng thái dựng sẵn |
|---|---|---|---|---|
| **Bão cát đổi hướng** | SandstormTurn | c2m06: 200 giây c12m07: 180 giây | Gió đổi hướng, bão cát tràn qua một nửa bản đồ: tầm nhìn nửa đó giảm, nửa kia quang hơn; cảnh bão chỉ phủ nửa có bão. | — |
| **Báo động nhà máy** | GroundChange | i1m01: 30 giây, khi bị phát hiện | Bị phát hiện thì còi báo động: cổng xưởng cán đóng (trạng thái dựng sẵn), đồn binh kéo tới. | i1m01: mill_gate (open → shut) |
| **Mất điện thành phố** | CityBlackout | c7m11: 240 giây | Đèn đường tắt, đêm xuống; mọi tháp nối lưới điện của cả hai phe ngừng 90 giây. | — |
| **Phản bội (báo trước)** | BetrayalWarning | c7m10 (square): 168 giây | Các cánh quân của Thorne được đánh dấu và có thoại 10 giây trước khi quay súng. | — |
| **Khoang đổ bộ quỹ đạo** | OrbitalPods | c11m10 (fortress): 60 giây | Ba khoang đáp xuống ba điểm dựng sẵn, dựng thành tháp địch; tháp bị phá thì điểm đó mở lại. | c11m10: pod_site_1 (clear → landed) c11m10: pod_site_2 (clear → landed) c11m10: pod_site_3 (clear → landed) |
| **Triều lên/xuống** | GroundChange | c1m01: 150 giây, lặp mỗi 150 giây | Mỗi 150 giây bãi cạn phía đông ngập rồi khô lại (hai trạng thái dựng sẵn). | c1m01: shoal (low → high) |
| **Cầu sập** | GroundChange | i2m03: 150 giây | Cây cầu phía đông sập ở mốc thời gian; cầu lớn và chỗ nước cạn phía tây vẫn qua được. | i2m03: east_bridge (standing → down) |
| **Cần cẩu đổ** | GroundChange | c4m02: khi gantry_crane bị phá c4m05: khi gantry_crane bị phá | Bắn sập cần cẩu trung lập thì cần trục đổ dọc bến, chặn lối giữa của bến (trạng thái dựng sẵn). | c4m02: crane (standing → fallen) c4m05: crane (standing → fallen) |
| **Hồ băng nứt** | IceCrack | c3m04: 20 giây | Xe hạng vừa và nặng (theo hạng trọng lượng, không theo CP) ở trên hồ quá 10 giây làm nứt băng và bị chậm 40% trong 8 giây. | — |
| **Đập nứt** | GroundChange | c6m14: 240 giây, lặp mỗi 150 giây, 3 lần c6m10: 300 giây, lặp mỗi 150 giây, 3 lần | Nước sông dưới đập dâng ba mức dựng sẵn, chỉ lên không xuống: giữa chỗ nước cạn, cả chỗ nước cạn, rồi hai bờ trũng. | c6m14: flood (dry → rising → high → flood) c6m10: flood (dry → rising → high → flood) |
| **Sập hầm mỏ** | GroundChange | c8m10: 240 giây | Hầm phía đông bắc sập, hầm cũ phía tây nam được phá mở (một lần đổi trạng thái). | c8m10: adits (north → south) |
| **Dung nham** | GroundChange | c5m10: 180 giây | Dòng dung nham cắt nhánh đông bắc của đường đắp phía tây sau 3 phút. | c5m10: lava (clear → cut) |
| **Cháy rừng** | ForestFire | c5m13: 150 giây | Một mặt lửa dựng sẵn theo gió đốt lần lượt bốn dải rừng (lửa, cháy xe, khói chắn tầm nhìn) rồi tắt; dải đang cháy là vùng cấm, xe trong đó bị đẩy ra. | c5m13: fire (none → front1 → front2 → front3 → front4 → out) |

#### 7c. Sự kiện trong nhiệm vụ và thoại trong trận (prompt 23)

Mỗi nhiệm vụ ghép từ thư viện sự kiện dạng dữ liệu (67 sự kiện, 27 loại); cả chiến dịch có 549 sự kiện. Sự kiện kích hoạt theo thời gian, tiến độ nhiệm vụ, máu boss, số quân trên sân hoặc sau một sự kiện khác; chạy theo seed và vào chuỗi lệnh của trận nên replay và checkpoint khôi phục đúng. Mọi sự kiện lớn được báo trước bằng thông báo ở mép trên, một câu thoại và mũi tên hướng trên bản đồ nhỏ; quân địch không bao giờ xuất hiện trong vòng 45 m quanh quân người chơi. Viện quân có trần riêng ngoài trần quân thường: 16 xe địch, 10 xe Accord. Tướng địch rút lui khi còn 30% máu, trừ ở trận cuối của mình; từ chương 4 tướng ra trận bằng mini boss thay vì xe tinh nhuệ. Các con số là điểm khởi đầu, chờ đợt mô phỏng 5 seed.

#### Viện quân theo tướng

| Tướng | Thành phần | Cách tới | Xe tinh nhuệ | Chương cuối |
|---|---|---|---|---|
| Thiếu tá Brandt | Bánh lốp, Xe bộ binh, Tăng chủ lực, Pháo xung kích, Tăng nhẹ | edge | Tăng chủ lực | 1 |
| Tướng Viktor Varga | Tăng nhẹ, Tăng chủ lực, Tăng nặng, Chống tăng, Hai nòng | edge | Tăng nặng | 12 |
| Đại tá Ilya Orlov | Phản lực, Lựu pháo, Xe cối, Phản lực nặng, Cao xạ | edge | Phản lực | 11 |
| Đô đốc Magnus Kessler | Xe bộ binh, Pháo xung kích, Tăng chủ lực, Rải mìn, PK tầm trung | sea, rail, landing, edge | Tăng chủ lực | 12 |
| Tiến sĩ Elara Venn | UAV tấn công, Drone FPV, Đạn lảng vảng, UAV trinh sát, Gây nhiễu | edge, air | Drone FPV | 5 |
| Kasimir Wolff | TT tấn công, TT vũ trang, Cường kích, UAV tấn công | edge | Cường kích | 10 |
| Tướng Roland Thorne | Tăng chủ lực, Tăng nặng, Xe bộ binh, Hỗ trợ tăng, Cao xạ | edge, landing | Tăng nặng | 9 |
| Giám đốc Lucien Aurel | UAV tấn công, Drone FPV, Tăng nặng, Hỗ trợ tăng, Pháo điện từ | pods, air, edge | Tăng nặng | 12 |

#### Thoại trong trận

Mọi lời nhân vật trong trận là một dòng chữ kiểu phụ đề ngay trên khay thẻ: tên người nói in đậm, màu theo phe (ta xanh nhạt, địch đỏ đậm), rồi câu thoại; nền chỉ là một dải tối mờ, rộng tối đa nửa màn hình, tối đa 2 dòng, có chân dung nhỏ của người nói, không lồng tiếng. Một câu một lúc, theo mức ưu tiên: cốt truyện, cảnh báo, sự kiện, phản ứng. Câu cốt truyện và cảnh báo xếp hàng (cảnh báo quá 12 s thì bỏ); câu sự kiện và phản ứng hiện ngay hoặc bỏ, cách nhau tối thiểu 9 s (20 s cho câu phản ứng khi có boss trên sân). Mỗi câu hiện 3–6 s theo độ dài, mờ dần 0,25 s, không bao giờ dừng trận. Nhật ký 20 câu gần nhất mở từ menu tạm dừng. Cài đặt: Đầy đủ / Chỉ quan trọng / Tắt (câu cốt truyện luôn hiện). Sáu khoảnh khắc cốt truyện làm trận chậm 0,5 lần trong khi 2–3 câu liên tiếp chạy: Hollow Dam, Venn mất bầy drone, Thorne phản bội, Thorne trên Typhon, Varga ngã xuống, Icarus rơi.

Sheet: 07_chien_dich_cot_truyen/Bien_co — Biến cố (67 dòng, 89 cột)

| id | nhiem_vu_dung | kind | lead | lines_betrayed | lines_broken | lines_end | lines_start | lines_warn_s | notices_betrayed |
|---|---|---|---|---|---|---|---|---|---|
| accord_artillery | c1m05;c1m10;c2m09;c3s2;i1m03;c4m05;c4m11;c5m06;c5m10;c6m05;… | AllyArtillery |  |  |  |  |  |  |  |
| accord_landing | c1m01;c1m10;c6m08 | AllyWave |  |  |  |  | radio.khai.ev.allyWave.landing.start |  |  |
| accord_relief | c1m06;c3m04;c4m07;c4m18;c5m08;c6m11;i2m03;c8m06;c9m13;i3m03… | AllyWave |  |  |  |  |  |  |  |
| accord_wave | c1m03;c1m09;c2m02;c2m10;c3m01;c3m10;c4m01;c4m10;c4m15;c4m11… | AllyWave |  |  |  |  |  |  |  |
| air_raids | c10m01;c10m11;c10m03;c10m06;c10m14;c10m09;c10m10;c10s1 | AirRaid |  |  |  |  |  |  |  |
| air_wave | c2s2;c5m07;c6s1;c7m11;c8s2;i3m01;c10m04;c10m13;c10m07;c10m1… | EnemyWave |  |  |  |  |  | radio.linh.ev.enemyWave.air.warn |  |
| alarm_wave | i1m01 | EnemyWave |  |  |  |  |  | radio.linh.ev.enemyWave.alarm.warn |  |
| betrayal_warning | c7m10 | BetrayalWarning | 10 |  |  |  |  | radio.linh.ev.betrayalWarning.warn |  |
| brandt_line | c6m01;c6m02;c6m03;c6m07;c6m09;c6m10 | AllyWave |  |  |  |  | radio.brandt.ev.allyWave.brandt.start |  |  |
| bridge_collapse | i2m03 | GroundChange | 10 |  |  |  |  |  |  |
| ceasefire | c6m14 | Ceasefire |  | radio.khai.ev.ceasefire.betrayed | radio.varga.ev.ceasefire.broken | radio.varga.ev.ceasefire.end | radio.khai.ev.ceasefire.start |  | event.ceasefire.betrayed |
| city_blackout | c7m11 | CityBlackout | 10 |  |  |  |  |  |  |
| cloud_over | c4s2;c5m04;c6m14;c7m09 | WeatherShift |  |  |  |  |  |  |  |
| counter_battery | c3m02;c3m06;c3m09;c3m10;c11m05 | CounterBattery |  |  |  |  |  |  |  |
| crane_fall | c4m02;c4m05 | GroundChange | 10 |  |  |  |  |  |  |

*15 / 67 dòng đầu: xem sheet 07_chien_dich_cot_truyen/Bien_co; in 10 / 89 cột; 32 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 07_chien_dich_cot_truyen/Bien_co_luat — Biến cố: luật chung (40 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so | gia_tri_chu |
|---|---|---|---|---|
| accordRoster | eventLibrary.rules | accordRoster |  | main_battle_tank;ifv;armored_car;aa_vehicle;tank_destroyer;… |
| caps.ally | eventLibrary.rules | ally | 10 |  |
| caps.enemy | eventLibrary.rules | enemy | 16 |  |
| generals.aurel.delivery | eventLibrary.rules | delivery |  | pods;air;edge |
| generals.aurel.elite | eventLibrary.rules | elite |  | heavy_tank |
| generals.aurel.lastChapter | eventLibrary.rules | lastChapter | 12 |  |
| generals.aurel.roster | eventLibrary.rules | roster |  | strike_drone;fpv_carrier;heavy_tank;bmpt;railgun_truck |
| generals.brandt.delivery | eventLibrary.rules | delivery |  | edge |
| generals.brandt.elite | eventLibrary.rules | elite |  | main_battle_tank |
| generals.brandt.lastChapter | eventLibrary.rules | lastChapter | 1 |  |
| generals.brandt.roster | eventLibrary.rules | roster |  | armored_car;ifv;main_battle_tank;wheeled_gun;light_tank |
| generals.hung.delivery | eventLibrary.rules | delivery |  | edge;landing |
| generals.hung.elite | eventLibrary.rules | elite |  | heavy_tank |
| generals.hung.lastChapter | eventLibrary.rules | lastChapter | 9 |  |
| generals.hung.roster | eventLibrary.rules | roster |  | main_battle_tank;heavy_tank;ifv;bmpt;aa_vehicle |
| generals.kessler.delivery | eventLibrary.rules | delivery |  | sea;rail;landing;edge |
| generals.kessler.elite | eventLibrary.rules | elite |  | main_battle_tank |
| generals.kessler.lastChapter | eventLibrary.rules | lastChapter | 12 |  |
| generals.kessler.roster | eventLibrary.rules | roster |  | ifv;wheeled_gun;main_battle_tank;mine_layer;sam_launcher |
| generals.orlov.delivery | eventLibrary.rules | delivery |  | edge |
| generals.orlov.elite | eventLibrary.rules | elite |  | mlrs |
| generals.orlov.lastChapter | eventLibrary.rules | lastChapter | 11 |  |
| generals.orlov.roster | eventLibrary.rules | roster |  | mlrs;artillery;mortar_carrier;heavy_rocket_artillery;aa_veh… |
| generals.quaden.delivery | eventLibrary.rules | delivery |  | edge |
| generals.quaden.elite | eventLibrary.rules | elite |  | attack_jet |
| generals.quaden.lastChapter | eventLibrary.rules | lastChapter | 10 |  |
| generals.quaden.minis | eventLibrary.rules | minis |  | morrigan |
| generals.quaden.roster | eventLibrary.rules | roster |  | attack_helicopter;gunship_heli;attack_jet;strike_drone |
| generals.sen.delivery | eventLibrary.rules | delivery |  | edge;air |
| generals.sen.elite | eventLibrary.rules | elite |  | fpv_carrier |
| generals.sen.lastChapter | eventLibrary.rules | lastChapter | 5 |  |
| generals.sen.roster | eventLibrary.rules | roster |  | strike_drone;fpv_carrier;lancet_truck;recon_drone;ew_jammer |
| generals.varga.delivery | eventLibrary.rules | delivery |  | edge |
| generals.varga.elite | eventLibrary.rules | elite |  | heavy_tank |
| generals.varga.lastChapter | eventLibrary.rules | lastChapter | 12 |  |
| generals.varga.roster | eventLibrary.rules | roster |  | light_tank;main_battle_tank;heavy_tank;tank_destroyer;twin_… |
| genericRoster | eventLibrary.rules | genericRoster |  | armored_car;ifv;light_tank;main_battle_tank;aa_vehicle;mlrs |
| miniFrom | eventLibrary.rules | miniFrom | 4 |  |
| nearSight | eventLibrary.rules | nearSight | 45 |  |
| retreatAt | eventLibrary.rules | retreatAt | 0.3 |  |

Sheet: 07_chien_dich_cot_truyen/Nhiem_vu_bien_co — Nhiệm vụ: biến cố (494 dòng, 23 cột)

| id | nhiem_vu_id | thu_tu | bien_co | params_radius_m | params_salvos | params_size | trigger_at | trigger_every_s | trigger_times |
|---|---|---|---|---|---|---|---|---|---|
| c1m01/0 | c1m01 | 0 | landing_assault |  |  | 4 |  |  |  |
| c1m01/1 | c1m01 | 1 | accord_landing |  |  |  |  |  |  |
| c1m01/2 | c1m01 | 2 | enemy_barrage | 16 | 2 |  | 90 | 80 | 4 |
| c1m01/3 | c1m01 | 3 | tide_turn |  |  |  |  |  |  |
| c1m02/0 | c1m02 | 0 | landing_assault |  |  |  |  |  |  |
| c1m02/1 | c1m02 | 1 | nadia_intel |  |  |  |  |  |  |
| c1m02/2 | c1m02 | 2 | rain_sets_in |  |  |  |  |  |  |
| c1m03/0 | c1m03 | 0 | enemy_wave |  |  |  |  |  |  |
| c1m03/1 | c1m03 | 1 | loot_drop |  |  |  |  |  |  |
| c1m03/2 | c1m03 | 2 | accord_wave |  |  |  |  |  |  |
| c1m04/0 | c1m04 | 0 | enemy_wave_late |  |  |  |  |  |  |
| c1m04/1 | c1m04 | 1 | supply_drop |  |  |  |  |  |  |
| c1m04/2 | c1m04 | 2 | rain_sets_in |  |  |  |  |  |  |
| c1m05/0 | c1m05 | 0 | accord_artillery |  |  |  |  |  |  |
| c1m05/1 | c1m05 | 1 | loot_repair |  |  |  |  |  |  |

*15 / 494 dòng đầu: xem sheet 07_chien_dich_cot_truyen/Nhiem_vu_bien_co.*

## 4. Nhiệm vụ nhiều giai đoạn

Trạng thái: Đã áp

Nguồn dữ liệu: 07_chien_dich_cot_truyen/Nhiem_vu_giai_doan; 07_chien_dich_cot_truyen/Nhiem_vu_giai_doan_su_kien; 07_chien_dich_cot_truyen/Nhiem_vu_giai_doan_lua_chon; 07_chien_dich_cot_truyen/Nhiem_vu_dong_minh. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §4. Nhiệm vụ.

Chiến dịch lớn chạy nhiều giai đoạn trong cùng một trận. Mỗi giai đoạn là một nhiệm vụ riêng (mục tiêu, điều kiện thắng, quân, boss) đặt trên dữ liệu của nhiệm vụ mẹ. Xong một giai đoạn thì trả thưởng CP, chạy sự kiện cuối giai đoạn, lưu điểm lưu và sang giai đoạn tiếp theo hoặc một lựa chọn. Thua một giai đoạn là thua nhiệm vụ.

- **Sự kiện** ở đầu, cuối hoặc sau một số giây: chi viện địch, chi viện ta, mở rộng vùng chơi, đồng minh phản bội, radio, thưởng CP, không kích, thu nhập.
- **Lựa chọn nhánh:** mỗi chiến dịch lớn có ít nhất một giai đoạn chọn giữa hai mục tiêu có hệ quả khác nhau (ví dụ phá kho đạn: thu nhập địch ×0,7; hoặc chiếm đài radio: không kích miễn phí mỗi 50–55 giây). Trận vẫn chạy trong lúc chọn; sau 15 giây tự lấy phương án đầu.
- **Điểm lưu bằng phát lại:** mô phỏng xác định, nên thay vì chụp toàn bộ trạng thái, game ghi lệnh của người chơi (kèm bước mô phỏng) và các công tắc (thế trận, tự mua, yểm trợ, cứ điểm ưu tiên, nhánh đã chọn). Khôi phục = dựng lại trận cùng seed và phát lại nhật ký sau màn chờ; dấu vân tay trạng thái (vị trí, máu, CP của mọi xe) phải trùng. Bài kiểm tra xác nhận trận khôi phục và trận chơi liền mạch giống hệt, kể cả qua một lựa chọn và một lần phản bội.
- **Chỉ huy đồng minh:** căn cứ riêng (sở chỉ huy, tháp) và quân riêng, do AI chiến thuật riêng điều khiển, cùng mục tiêu với người chơi, thả quân ở bãi riêng. Xe đồng minh không tính vào quân số, tiếp tế và giới hạn của người chơi. Sự kiện phản bội chuyển toàn bộ xe và công trình của đồng minh sang phe địch ngay trong trận (chương 8).
- **Vùng chơi mở rộng:** chiến dịch lớn bắt đầu trên một phần bản đồ; phe người chơi không đi ra ngoài biên (đường đứt nét vàng), camera cũng dừng ở biên và mở theo khi vùng chơi mở rộng. Lưới dẫn đường và làn giao thông đã phủ toàn bản đồ.
- **Địch đông:** trần xe địch 48 ở Công thành, Phòng thủ, Vô tận và chiến dịch lớn (32 ở chế độ thường); quân đông là bầy xe rẻ. Tìm đường tối đa 6 lượt mỗi bước mô phỏng (còn lại xếp hàng), hai chỉ huy AI nghĩ ở các bước khác nhau. Đo trên máy bàn quy đổi ×6 cho điện thoại yếu: 48 xe địch có thời gian bước trung bình 4,4 ms, p99 15,3 ms (ngân sách 8/16 ms).
- **Boss nhiều pha:** thanh máu có vạch pha; tới vạch boss dừng lại, biến hình vài giây (không nhận sát thương, camera lia tới, tướng lên radio) rồi đánh tiếp mạnh hơn (sát thương, tốc độ, giáp, kỹ năng, mô hình mới).

#### Các chiến dịch lớn cuối chương

| # | Chiến dịch | Giai đoạn | Sự kiện | Lựa chọn | Đồng minh |
|---|---|---|---|---|---|
| c1m10 | **Pháo đài Ashfield** | Đốt kho nhiên liệu → Cho nổ kho đạn → Phá trạm radar → Bastion → Quân đồn trú phản kích → San phẳng sở chỉ huy | chi viện địch, không kích, radio, thu nhập | Cho nổ kho đạn / Phá trạm radar |  |
| c2m11 | **Behemoth ở Red Rock** | Giếng dầu → Phá các giàn bơm → Pháo của Thorne → Chiếm ốc đảo → Giữ ốc đảo → Behemoth | chi viện địch, không kích, radio, thu nhập | Phá các giàn bơm / Gọi pháo của Thorne | có |
| c3m10 | **Tuyến Frostpeak** | Làm mù radar trên đồi → Cho nổ kho nhiên liệu → Radar của pháo đài → Jötunn → Giữ cổng | chi viện địch, không kích, radio, thu nhập | Cho nổ kho nhiên liệu / Phá radar của pháo đài |  |
| c4m11 | **Leviathan** | Ngọn hải đăng → Trận địa pháo cũ → Yểm trợ trên không → Làng chài → Leviathan | chi viện địch, không kích, radio | Chiếm trận địa pháo bờ biển / Gọi không quân |  |
| c5m10 | **Matriarch** | Các đường đắp → Đốt nhiên liệu drone → Giữ trạm tiếp sóng → Giữ nhà máy địa nhiệt → Bầy drone → Matriarch | chi viện địch, không kích, radio, thu nhập | Đốt nhiên liệu drone / Giữ trạm tiếp sóng (120 giây) |  |
| c6m10 | **Bảo vệ con đập** | Giữ mặt đập → Đốt kho của Varga → Giữ trạm phát điện → Moloch → Chờ cứu viện | chi viện ta, chi viện địch, không kích, radio, thu nhập | Đốt kho của Varga ở bến lội / Giữ trạm phát điện (150 giây) | có |
| c7m10 | **Giải phóng Veyra** | Các đầu cầu → Đốt Bộ Hậu cần → Giữ khu vườn → Đánh chiếm cung điện → Giữ quảng trường → Phản bội → Phản đòn → Nemesis | chi viện địch, không kích, radio, thu nhập, đồng minh phản bội | Đốt Bộ Hậu cần / Giữ khu vườn (150 giây) | có |
| c8m10 | **Hố sâu nhất** | Nhà máy nghiền và bãi xuất quặng → Đốt kho nhiên liệu → Giữ nhà máy nghiền → Phá các si-lô quặng → Cho nổ xưởng chế biến → Giữ đáy hố → Kronos → Thorne phản kích | chi viện địch, không kích, radio, thu nhập | Đốt kho nhiên liệu / Giữ đài phát ở nhà máy nghiền |  |
| c9m10 | **Typhon trồi lên** | Bãi đường sắt → Đốt các toa nhiên liệu → Giữ trạm tín hiệu → Khu nhà máy và bến tàu → Giữ khu nhà máy → Typhon → Giữ cầu tàu | chi viện địch, không kích, radio, thu nhập | Đốt các toa nhiên liệu / Giữ trạm tín hiệu (150 giây) |  |
| c10m10 | **Tấn công Skyhold** | Làm mù radar → Đốt bãi nhiên liệu → Tháp điều khiển → Roc → Đợt cuối của Wolff → Giữ Skyhold | chi viện địch, không kích, radio, thu nhập | Đốt bãi nhiên liệu / Phá tháp điều khiển và vòm radar |  |
| c11m10 | **Skygate Array** | Làm mù radar trên đồi → Cho nổ kho nhiên liệu → Radar của pháo đài → Daedalus → Giữ cổng | chi viện địch, không kích, radio, thu nhập | Cho nổ kho nhiên liệu / Phá radar của pháo đài |  |
| c12m10 | **Icarus rơi** | Khu nhiên liệu đẩy → Đốt nhiên liệu đẩy → Làm mù radar phía tây → Nhà lắp ráp → Trận cuối của Varga → Đếm ngược → Giữ bệ phóng → Icarus | chi viện địch, không kích, radio, thu nhập | Đốt các bồn nhiên liệu đẩy / Phá radar phía tây |  |

Sheet: 07_chien_dich_cot_truyen/Nhiem_vu_giai_doan — Nhiệm vụ: giai đoạn (90 dòng, 37 cột)

| id | nhiem_vu_id | thu_tu | boss_def | boss_heading_deg | boss_health | boss_name | boss_x_m | boss_z_m | cp |
|---|---|---|---|---|---|---|---|---|---|
| c1m10/0 | c1m10 | 0 |  |  |  |  |  |  | 8 |
| c1m10/1 | c1m10 | 1 |  |  |  |  |  |  | 6 |
| c1m10/2 | c1m10 | 2 |  |  |  |  |  |  | 6 |
| c1m10/3 | c1m10 | 3 | fortress_bastion | 225 | 0.55 |  | 92 | 92 | 10 |
| c1m10/4 | c1m10 | 4 |  |  |  |  |  |  | 8 |
| c1m10/5 | c1m10 | 5 |  |  |  |  |  |  |  |
| c2m10/0 | c2m10 | 0 |  |  |  |  |  |  | 8 |
| c2m10/1 | c2m10 | 1 |  |  |  |  |  |  | 6 |
| c2m10/2 | c2m10 | 2 |  |  |  |  |  |  | 6 |
| c2m10/3 | c2m10 | 3 |  |  |  |  |  |  | 6 |
| c2m10/4 | c2m10 | 4 |  |  |  |  |  |  | 10 |
| c2m10/5 | c2m10 | 5 |  |  |  |  |  |  | 8 |
| c2m10/6 | c2m10 | 6 | behemoth_inferno | 225 | 1.2 | behemoth_inferno | 30 | 30 | 8 |
| c2m10/7 | c2m10 | 7 |  |  |  |  |  |  |  |
| c2m11/0 | c2m11 | 0 |  |  |  |  |  |  | 8 |

*15 / 90 dòng đầu: xem sheet 07_chien_dich_cot_truyen/Nhiem_vu_giai_doan; in 10 / 37 cột; 11 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 07_chien_dich_cot_truyen/Nhiem_vu_giai_doan_su_kien — Giai đoạn: sự kiện (145 dòng, 13 cột)

| id | nhiem_vu_giai_doan_id | thu_tu | units | amount | at | every_s | key | kind | support |
|---|---|---|---|---|---|---|---|---|---|
| c1m10/0/0 | c1m10/0 | 0 |  |  | start |  | radio.khai.c1m10.s1 | Radio |  |
| c1m10/1/0 | c1m10/1 | 0 |  | 0.7 | end |  |  | Income |  |
| c1m10/1/1 | c1m10/1 | 1 |  |  | end |  | radio.enemyWeakened | Radio |  |
| c1m10/2/0 | c1m10/2 | 0 |  |  | end | 55 |  | Strike | airstrike |
| c1m10/2/1 | c1m10/2 | 1 |  |  | end |  | radio.alliedStrikes | Radio |  |
| c1m10/3/0 | c1m10/3 | 0 |  |  | start |  | radio.mai.c1m10.s3 | Radio |  |
| c1m10/4/0 | c1m10/4 | 0 |  |  | start |  | radio.khai.c1m10.s4 | Radio |  |
| c1m10/4/1 | c1m10/4 | 1 | main_battle_tank;ifv;mortar_carrier;light_tank |  | 30 |  |  | Reinforce |  |
| c1m10/4/2 | c1m10/4 | 2 | main_battle_tank;rocket_technical;ifv |  | 140 |  |  | Reinforce |  |
| c1m10/5/0 | c1m10/5 | 0 | main_battle_tank;ifv;mortar_carrier |  | start |  |  | Reinforce |  |
| c2m10/0/0 | c2m10/0 | 0 |  |  | start |  | radio.khai.c2m10.s1 | Radio |  |
| c2m10/1/0 | c2m10/1 | 0 |  | 0.7 | end |  |  | Income |  |
| c2m10/1/1 | c2m10/1 | 1 |  |  | end |  | radio.enemyWeakened | Radio |  |
| c2m10/2/0 | c2m10/2 | 0 |  |  | end | 55 |  | Strike | airstrike |
| c2m10/2/1 | c2m10/2 | 1 |  |  | end |  | radio.alliedStrikes | Radio |  |

*15 / 145 dòng đầu: xem sheet 07_chien_dich_cot_truyen/Nhiem_vu_giai_doan_su_kien; in 10 / 13 cột; 1 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 07_chien_dich_cot_truyen/Nhiem_vu_giai_doan_lua_chon — Giai đoạn: lựa chọn (28 dòng, 7 cột)

| id | nhiem_vu_giai_doan_id | thu_tu | key | next |
|---|---|---|---|---|
| c1m10/0/0 | c1m10/0 | 0 | dump | dump |
| c1m10/0/1 | c1m10/0 | 1 | radar | radar |
| c2m10/0/0 | c2m10/0 | 0 | tanks | tanks |
| c2m10/0/1 | c2m10/0 | 1 | oasis | oasis |
| c2m11/0/0 | c2m11/0 | 0 | pumps | pumps |
| c2m11/0/1 | c2m11/0 | 1 | guns | guns |
| c3m10/0/0 | c3m10/0 | 0 | depots | depots |
| c3m10/0/1 | c3m10/0 | 1 | radars | radars |
| c4m10/0/0 | c4m10/0 | 0 | crane | crane |
| c4m10/0/1 | c4m10/0 | 1 | signal | signal |
| c4m11/0/0 | c4m11/0 | 0 | battery | battery |
| c4m11/0/1 | c4m11/0 | 1 | strikes | strikes |
| c5m10/0/0 | c5m10/0 | 0 | fuel | fuel |
| c5m10/0/1 | c5m10/0 | 1 | relay | relay |
| c6m10/0/0 | c6m10/0 | 0 | spillway | spillway |
| c6m10/0/1 | c6m10/0 | 1 | station | station |
| c7m10/0/0 | c7m10/0 | 0 | ministry | ministry |
| c7m10/0/1 | c7m10/0 | 1 | gardens | gardens |
| c8m10/0/0 | c8m10/0 | 0 | tanks | tanks |
| c8m10/0/1 | c8m10/0 | 1 | oasis | oasis |
| c9m10/0/0 | c9m10/0 | 0 | crane | crane |
| c9m10/0/1 | c9m10/0 | 1 | signal | signal |
| c10m10/0/0 | c10m10/0 | 0 | fuel | fuel |
| c10m10/0/1 | c10m10/0 | 1 | tower | tower |
| c11m10/0/0 | c11m10/0 | 0 | depots | depots |
| c11m10/0/1 | c11m10/0 | 1 | radars | radars |
| c12m10/0/0 | c12m10/0 | 0 | propellant | propellant |
| c12m10/0/1 | c12m10/0 | 1 | radars | radars |

Sheet: 07_chien_dich_cot_truyen/Nhiem_vu_dong_minh — Nhiệm vụ: quân đồng minh (42 dòng, 10 cột)

| id | nhiem_vu_id | thu_tu | def | heading_deg | team | x_m | z_m |
|---|---|---|---|---|---|---|---|
| c2m07/0 | c2m07 | 0 | ifv | 45 | 0 | -2.0 | -6.0 |
| c2m07/1 | c2m07 | 1 | light_tank | 45 | 0 | -10.0 | -6.0 |
| c2m11/0 | c2m11 | 0 | main_battle_tank | 45 | 0 | -89.0 | -80.0 |
| c2m11/1 | c2m11 | 1 | main_battle_tank | 45 | 0 | -93.84 | -73.34 |
| c2m11/2 | c2m11 | 2 | ifv | 45 | 0 | -101.66 | -75.89 |
| c2m11/3 | c2m11 | 3 | aa_vehicle | 45 | 0 | -101.66 | -84.11 |
| c2m11/4 | c2m11 | 4 | mlrs | 45 | 0 | -93.84 | -86.66 |
| c5s2/0 | c5s2 | 0 | ifv | 45 | 0 | -62.0 | -26.0 |
| c5s2/1 | c5s2 | 1 | light_tank | 45 | 0 | -70.0 | -26.0 |
| c6m07/0 | c6m07 | 0 | ifv | 225 | 0 | 2.0 | 6.0 |
| c6m07/1 | c6m07 | 1 | main_battle_tank | 225 | 0 | 10.0 | 6.0 |
| c7m03/0 | c7m03 | 0 | ifv | 45 | 0 | -2.0 | -6.0 |
| c7m03/1 | c7m03 | 1 | main_battle_tank | 45 | 0 | -10.0 | -6.0 |
| c7m10/0 | c7m10 | 0 | main_battle_tank | 45 | 0 | -93.0 | 30.0 |
| c7m10/1 | c7m10 | 1 | heavy_tank | 45 | 0 | -96.5 | 36.06 |

*15 / 42 dòng đầu: xem sheet 07_chien_dich_cot_truyen/Nhiem_vu_dong_minh.*

## Các sheet khác của file

Mọi sheet chưa in ở mục trên (sheet input_<tên> là bản chép từ file khác, không in lại).

### Cutscene_khoanh_khac

Trạng thái: Chưa áp — chờ prompt xuat_luot5

Nguồn dữ liệu: 07_chien_dich_cot_truyen/Cutscene_khoanh_khac.

Sheet: 07_chien_dich_cot_truyen/Cutscene_khoanh_khac — Khoảnh khắc chậm (1 dòng, 5 cột)

| id | trang_thai | ghi_chu |
|---|---|---|
| chua_ap | CHUA_AP:prompt_xuat_luot5 | đọc hằng và điều kiện trong Assets/MachineBrigade/Scripts/G… |

### Kich_ban_goc

Trạng thái: Đã áp

Nguồn dữ liệu: 07_chien_dich_cot_truyen/Kich_ban_goc.

Sheet: 07_chien_dich_cot_truyen/Kich_ban_goc — Kịch bản gốc (1854 dòng, 7 cột)

| id | tep | dong_so | loai | noi_dung |
|---|---|---|---|---|
| ch01:0001 | ch01 | 1 | ghi_chu | # Chapter 1 · Coast of Fire (act 1). Enemy general: Brandt.… |
| ch01:0002 | ch01 | 2 | ghi_chu | # Threads: Brandt trusts his walls; Behemoth heard of once;… |
| ch01:0004 | ch01 | 4 | nhiem_vu | @c1m01 main=khai |
| ch01:0005 | ch01 | 5 | cau | mission_start / khai / 1 / Lữ đoàn, rời bãi cát trước. Mọi… |
| ch01:0006 | ch01 | 6 | cau | time@20 / linh / 2 / Hai điểm phải chiếm: lối ra bãi biển v… |
| ch01:0007 | ch01 | 7 | cau | point_captured:east / dieuhau / 3 / Lối ra bãi biển là của… |
| ch01:0008 | ch01 | 8 | cau | objective_progress:last / linh / 2 / Còn thị trấn. Lính gác… |
| ch01:0009 | ch01 | 9 | cau | critical_failure_imminent / khai / 1 / Ta đang bị đẩy xuống… |
| ch01:0010 | ch01 | 10 | cau | victory / khai / 1 / Đầu cầu đã vững. Giờ ta tìm chỗ dựng n… |
| ch01:0011 | ch01 | 11 | cau | defeat / khai / 1 / Lui về tàu. Ta sẽ đổ bộ lại khi trời tố… |
| ch01:0012 | ch01 | 12 | cau | time@60 / linh / 2 / Pháo bờ biển của Brandt bắn theo nhịp.… |
| ch01:0014 | ch01 | 14 | nhiem_vu | @c1m02 main=linh |
| ch01:0015 | ch01 | 15 | cau | mission_start / linh / 1 / Trạm radar trên vách đá đang gọi… |
| ch01:0016 | ch01 | 16 | cau | time@40 / linh / 2 / Ca trực vừa đổi. Lính mới chưa quen má… |
| ch01:0017 | ch01 | 17 | cau | enemy_reinforcement / linh / 3 / Xe từ thị trấn đang lên dố… |

*15 / 1854 dòng đầu: xem sheet 07_chien_dich_cot_truyen/Kich_ban_goc.*

### Nhiem_vu_dong_minh_cong_trinh

Trạng thái: Đã áp

Nguồn dữ liệu: 07_chien_dich_cot_truyen/Nhiem_vu_dong_minh_cong_trinh.

Sheet: 07_chien_dich_cot_truyen/Nhiem_vu_dong_minh_cong_trinh — Nhiệm vụ: công trình đồng minh (25 dòng, 10 cột)

| id | nhiem_vu_id | thu_tu | def | heading_deg | team | x_m | z_m |
|---|---|---|---|---|---|---|---|
| c2m07/0 | c2m07 | 0 | mg_bunker | 45 | 0 | 14.0 | 0.0 |
| c2m07/1 | c2m07 | 1 | gun_turret | 45 | 0 | -7.0 | 12.12 |
| c2m07/2 | c2m07 | 2 | guard_tower | 45 | 0 | -7.0 | -12.12 |
| c5s2/0 | c5s2 | 0 | mg_bunker | 45 | 0 | -46.0 | -20.0 |
| c5s2/1 | c5s2 | 1 | gun_turret | 45 | 0 | -67.0 | -7.88 |
| c5s2/2 | c5s2 | 2 | aa_turret | 45 | 0 | -67.0 | -32.12 |
| c6m07/0 | c6m07 | 0 | mg_bunker | 225 | 0 | -15.0 | -0.0 |
| c6m07/1 | c6m07 | 1 | gun_turret | 225 | 0 | -0.0 | -15.0 |
| c6m07/2 | c6m07 | 2 | aa_turret | 225 | 0 | 15.0 | -0.0 |
| c6m07/3 | c6m07 | 3 | guard_tower | 225 | 0 | 0.0 | 15.0 |
| c7m03/0 | c7m03 | 0 | mg_bunker | 45 | 0 | 15.0 | 0.0 |
| c7m03/1 | c7m03 | 1 | gun_turret | 45 | 0 | 0.0 | 15.0 |
| c7m03/2 | c7m03 | 2 | aa_turret | 45 | 0 | -15.0 | 0.0 |
| c7m03/3 | c7m03 | 3 | atgm_tower | 45 | 0 | -0.0 | -15.0 |
| c7m10/0 | c7m10 | 0 | gun_turret | 45 | 0 | -102.0 | 30.0 |
| c7m10/1 | c7m10 | 1 | aa_turret | 45 | 0 | -113.06 | 45.22 |
| c7m10/2 | c7m10 | 2 | mg_bunker | 45 | 0 | -130.94 | 39.4 |
| c7m10/3 | c7m10 | 3 | missile_battery | 45 | 0 | -130.94 | 20.6 |
| c7m10/4 | c7m10 | 4 | atgm_tower | 45 | 0 | -113.06 | 14.78 |
| c8m04/0 | c8m04 | 0 | mg_bunker | 225 | 0 | -14.0 | -0.0 |
| c8m04/1 | c8m04 | 1 | gun_turret | 225 | 0 | 7.0 | -12.12 |
| c8m04/2 | c8m04 | 2 | guard_tower | 225 | 0 | 7.0 | 12.12 |
| i3m03/0 | i3m03 | 0 | mg_bunker | 225 | 0 | -14.0 | -0.0 |
| i3m03/1 | i3m03 | 1 | gun_turret | 225 | 0 | 7.0 | -12.12 |
| i3m03/2 | i3m03 | 2 | guard_tower | 225 | 0 | 7.0 | 12.12 |

### Nhiem_vu_dong_minh_tiep_vien

Trạng thái: Đã áp

Nguồn dữ liệu: 07_chien_dich_cot_truyen/Nhiem_vu_dong_minh_tiep_vien.

Sheet: 07_chien_dich_cot_truyen/Nhiem_vu_dong_minh_tiep_vien — Nhiệm vụ: tiếp viện đồng minh (8 dòng, 7 cột)

| id | nhiem_vu_id | thu_tu | units | at |
|---|---|---|---|---|
| c2m11/0 | c2m11 | 0 | heavy_tank;ifv;tank_destroyer | 240 |
| c7m10/0 | c7m10 | 0 | main_battle_tank;ifv;mlrs | 240 |
| c7m10/1 | c7m10 | 1 | heavy_tank;aa_vehicle;tank_destroyer | 480 |
| c7m16/0 | c7m16 | 0 | main_battle_tank;bmpt | 200 |
| c8m11/0 | c8m11 | 0 | rocket_technical;armored_car;scout_jeep | 150 |
| c8m11/1 | c8m11 | 1 | zu23_technical;rocket_technical;armored_car | 330 |
| c8m13/0 | c8m13 | 0 | rocket_technical;armored_car;scout_jeep | 150 |
| c8m13/1 | c8m13 | 1 | zu23_technical;rocket_technical;armored_car | 330 |

### Nhiem_vu_giai_doan_bien_co

Trạng thái: Đã áp

Nguồn dữ liệu: 07_chien_dich_cot_truyen/Nhiem_vu_giai_doan_bien_co.

Sheet: 07_chien_dich_cot_truyen/Nhiem_vu_giai_doan_bien_co — Giai đoạn: biến cố (55 dòng, 11 cột)

| id | nhiem_vu_giai_doan_id | thu_tu | bien_co |
|---|---|---|---|
| c1m10/0/0 | c1m10/0 | 0 | enemy_wave |
| c1m10/3/0 | c1m10/3 | 0 | accord_artillery |
| c1m10/4/0 | c1m10/4 | 0 | enemy_counterattack |
| c1m10/4/1 | c1m10/4 | 1 | accord_landing |
| c2m10/0/0 | c2m10/0 | 0 | oil_convoy |
| c2m10/7/0 | c2m10/7 | 0 | accord_wave |
| c2m11/0/0 | c2m11/0 | 0 | oil_convoy |
| c2m11/3/0 | c2m11/3 | 0 | enemy_wave |
| c2m11/4/0 | c2m11/4 | 0 | enemy_barrage |
| c2m11/5/0 | c2m11/5 | 0 | skies_clear |
| c3m10/0/0 | c3m10/0 | 0 | counter_battery |
| c3m10/3/0 | c3m10/3 | 0 | hawk_strike |
| c3m10/4/0 | c3m10/4 | 0 | enemy_counterattack |
| c3m10/4/1 | c3m10/4 | 1 | accord_wave |
| c4m10/0/0 | c4m10/0 | 0 | landing_assault |

*15 / 55 dòng đầu: xem sheet 07_chien_dich_cot_truyen/Nhiem_vu_giai_doan_bien_co.*

### Nhiem_vu_goi_y

Trạng thái: Đã áp

Nguồn dữ liệu: 07_chien_dich_cot_truyen/Nhiem_vu_goi_y.

Sheet: 07_chien_dich_cot_truyen/Nhiem_vu_goi_y — Nhiệm vụ: gợi ý (8 dòng, 7 cột)

| id | nhiem_vu_id | thu_tu | at | key |
|---|---|---|---|---|
| c1m01/0 | c1m01 | 0 | 2 | tip.auto |
| c1m01/1 | c1m01 | 1 | 9 | tip.deploy |
| c1m01/2 | c1m01 | 2 | 16 | tip.points |
| c1m01/3 | c1m01 | 3 | 24 | tip.strike |
| c1m01/4 | c1m01 | 4 | 33 | tip.select |
| c1m01/5 | c1m01 | 5 | 43 | tip.counters |
| c1m01/6 | c1m01 | 6 | 54 | tip.items |
| c3m03/0 | c3m03 | 0 | 20 | tip.ammoIcons |

### Nhiem_vu_nav_chan

Trạng thái: Đã áp

Nguồn dữ liệu: 07_chien_dich_cot_truyen/Nhiem_vu_nav_chan.

Sheet: 07_chien_dich_cot_truyen/Nhiem_vu_nav_chan — Trạng thái nav: khối chặn (25 dòng, 9 cột)

| id | nhiem_vu_nav_state_trang_thai_id | thu_tu | d | w | x_m | z_m |
|---|---|---|---|---|---|---|
| c1m01/shoal/1/0 | c1m01/shoal/1 | 0 | 12 | 152 | 66 | -130 |
| c4m02/crane/1/0 | c4m02/crane/1 | 0 | 5 | 30 | 17 | 131 |
| c4m05/crane/1/0 | c4m05/crane/1 | 0 | 5 | 30 | 17 | 131 |
| c5m10/lava/1/0 | c5m10/lava/1 | 0 | 8 | 24 | -50 | 78 |
| c5m13/fire/1/0 | c5m13/fire/1 | 0 | 12 | 50 | -60 | -40 |
| c5m13/fire/2/0 | c5m13/fire/2 | 0 | 12 | 50 | -60 | -28 |
| c5m13/fire/3/0 | c5m13/fire/3 | 0 | 12 | 50 | -60 | -16 |
| c5m13/fire/4/0 | c5m13/fire/4 | 0 | 12 | 50 | -60 | -4 |
| c6m10/flood/1/0 | c6m10/flood/1 | 0 | 10 | 28 | 4 | -100 |
| c6m10/flood/2/0 | c6m10/flood/2 | 0 | 28 | 28 | 4 | -100 |
| c6m10/flood/3/0 | c6m10/flood/3 | 0 | 28 | 28 | 4 | -100 |
| c6m10/flood/3/1 | c6m10/flood/3 | 1 | 64 | 6 | -18 | -52 |
| c6m10/flood/3/2 | c6m10/flood/3 | 2 | 64 | 6 | 14 | -52 |
| c6m14/flood/1/0 | c6m14/flood/1 | 0 | 10 | 28 | 4 | -100 |
| c6m14/flood/2/0 | c6m14/flood/2 | 0 | 28 | 28 | 4 | -100 |
| c6m14/flood/3/0 | c6m14/flood/3 | 0 | 28 | 28 | 4 | -100 |
| c6m14/flood/3/1 | c6m14/flood/3 | 1 | 64 | 6 | -18 | -52 |
| c6m14/flood/3/2 | c6m14/flood/3 | 2 | 64 | 6 | 14 | -52 |
| c8m10/adits/0/0 | c8m10/adits/0 | 0 | 6 | 15 | -35 | -58 |
| c8m10/adits/1/0 | c8m10/adits/1 | 0 | 6 | 15 | 35 | 58 |
| c11m10/pod_site_1/1/0 | c11m10/pod_site_1/1 | 0 | 4.0 | 4.0 | 20 | 60 |
| c11m10/pod_site_2/1/0 | c11m10/pod_site_2/1 | 0 | 7.2 | 7.2 | 60 | 20 |
| c11m10/pod_site_3/1/0 | c11m10/pod_site_3/1 | 0 | 3.6 | 3.6 | -10 | 90 |
| i1m01/mill_gate/1/0 | i1m01/mill_gate/1 | 0 | 2 | 10 | 46 | 0 |
| i2m03/east_bridge/1/0 | i2m03/east_bridge/1 | 0 | 50 | 9 | 122 | 0 |

### Nhiem_vu_nav_state

Trạng thái: Đã áp

Nguồn dữ liệu: 07_chien_dich_cot_truyen/Nhiem_vu_nav_state.

Sheet: 07_chien_dich_cot_truyen/Nhiem_vu_nav_state — Nhiệm vụ: trạng thái nav dựng sẵn (13 dòng, 7 cột)

| id | nhiem_vu_id | thu_tu | id_goc | initial |
|---|---|---|---|---|
| c1m01/shoal | c1m01 | 0 | shoal | low |
| c4m02/crane | c4m02 | 0 | crane | standing |
| c4m05/crane | c4m05 | 0 | crane | standing |
| c5m10/lava | c5m10 | 0 | lava | clear |
| c5m13/fire | c5m13 | 0 | fire | none |
| c6m10/flood | c6m10 | 0 | flood | dry |
| c6m14/flood | c6m14 | 0 | flood | dry |
| c8m10/adits | c8m10 | 0 | adits | north |
| c11m10/pod_site_1 | c11m10 | 0 | pod_site_1 | clear |
| c11m10/pod_site_2 | c11m10 | 1 | pod_site_2 | clear |
| c11m10/pod_site_3 | c11m10 | 2 | pod_site_3 | clear |
| i1m01/mill_gate | i1m01 | 0 | mill_gate | open |
| i2m03/east_bridge | i2m03 | 0 | east_bridge | standing |

### Nhiem_vu_nav_state_trang_thai

Trạng thái: Đã áp

Nguồn dữ liệu: 07_chien_dich_cot_truyen/Nhiem_vu_nav_state_trang_thai.

Sheet: 07_chien_dich_cot_truyen/Nhiem_vu_nav_state_trang_thai — Trạng thái nav: các trạng thái (34 dòng, 6 cột)

| id | nhiem_vu_nav_state_id | thu_tu | name |
|---|---|---|---|
| c1m01/shoal/0 | c1m01/shoal | 0 | low |
| c1m01/shoal/1 | c1m01/shoal | 1 | high |
| c4m02/crane/0 | c4m02/crane | 0 | standing |
| c4m02/crane/1 | c4m02/crane | 1 | fallen |
| c4m05/crane/0 | c4m05/crane | 0 | standing |
| c4m05/crane/1 | c4m05/crane | 1 | fallen |
| c5m10/lava/0 | c5m10/lava | 0 | clear |
| c5m10/lava/1 | c5m10/lava | 1 | cut |
| c5m13/fire/0 | c5m13/fire | 0 | none |
| c5m13/fire/1 | c5m13/fire | 1 | front1 |
| c5m13/fire/2 | c5m13/fire | 2 | front2 |
| c5m13/fire/3 | c5m13/fire | 3 | front3 |
| c5m13/fire/4 | c5m13/fire | 4 | front4 |
| c5m13/fire/5 | c5m13/fire | 5 | out |
| c6m10/flood/0 | c6m10/flood | 0 | dry |
| c6m10/flood/1 | c6m10/flood | 1 | rising |
| c6m10/flood/2 | c6m10/flood | 2 | high |
| c6m10/flood/3 | c6m10/flood | 3 | flood |
| c6m14/flood/0 | c6m14/flood | 0 | dry |
| c6m14/flood/1 | c6m14/flood | 1 | rising |
| c6m14/flood/2 | c6m14/flood | 2 | high |
| c6m14/flood/3 | c6m14/flood | 3 | flood |
| c8m10/adits/0 | c8m10/adits | 0 | north |
| c8m10/adits/1 | c8m10/adits | 1 | south |
| c11m10/pod_site_1/0 | c11m10/pod_site_1 | 0 | clear |
| c11m10/pod_site_1/1 | c11m10/pod_site_1 | 1 | landed |
| c11m10/pod_site_2/0 | c11m10/pod_site_2 | 0 | clear |
| c11m10/pod_site_2/1 | c11m10/pod_site_2 | 1 | landed |
| c11m10/pod_site_3/0 | c11m10/pod_site_3 | 0 | clear |
| c11m10/pod_site_3/1 | c11m10/pod_site_3 | 1 | landed |
| i1m01/mill_gate/0 | i1m01/mill_gate | 0 | open |
| i1m01/mill_gate/1 | i1m01/mill_gate | 1 | shut |
| i2m03/east_bridge/0 | i2m03/east_bridge | 0 | standing |
| i2m03/east_bridge/1 | i2m03/east_bridge | 1 | down |

### Nhiem_vu_quan

Trạng thái: Đã áp

Nguồn dữ liệu: 07_chien_dich_cot_truyen/Nhiem_vu_quan.

Sheet: 07_chien_dich_cot_truyen/Nhiem_vu_quan — Nhiệm vụ: quân đặt sẵn (332 dòng, 10 cột)

| id | nhiem_vu_id | thu_tu | def | heading_deg | team | x_m | z_m |
|---|---|---|---|---|---|---|---|
| c1m06/0 | c1m06 | 0 | light_tank | 45 | 0 | -85.0 | -88.0 |
| c1m06/1 | c1m06 | 1 | ifv | 45 | 0 | -92.5 | -83.67 |
| c1m06/2 | c1m06 | 2 | main_battle_tank | 45 | 0 | -92.5 | -92.33 |
| c1m09/0 | c1m09 | 0 | light_tank | 45 | 0 | -84.0 | -90.0 |
| c1m09/1 | c1m09 | 1 | light_tank | 45 | 0 | -93.0 | -84.8 |
| c1m09/2 | c1m09 | 2 | ifv | 45 | 0 | -93.0 | -95.2 |
| c2m03/0 | c2m03 | 0 | main_battle_tank | 45 | 0 | -82.0 | -92.0 |
| c2m03/1 | c2m03 | 1 | ifv | 45 | 0 | -91.0 | -86.8 |
| c2m03/2 | c2m03 | 2 | aa_vehicle | 45 | 0 | -91.0 | -97.2 |
| c2m04/0 | c2m04 | 0 | main_battle_tank | 225 | 1 | 6.0 | 30.0 |
| c2m04/1 | c2m04 | 1 | tank_destroyer | 225 | 1 | -6.0 | 30.0 |
| c2m04/2 | c2m04 | 2 | light_tank | 225 | 1 | 106.0 | -50.0 |
| c2m04/3 | c2m04 | 3 | ifv | 225 | 1 | 94.0 | -50.0 |
| c2m06/0 | c2m06 | 0 | tank_destroyer | 225 | 1 | 75 | 52.5 |
| c2m06/1 | c2m06 | 1 | aa_vehicle | 225 | 1 | 82.5 | 63 |

*15 / 332 dòng đầu: xem sheet 07_chien_dich_cot_truyen/Nhiem_vu_quan.*

### Nhiem_vu_radio

Trạng thái: Đã áp

Nguồn dữ liệu: 07_chien_dich_cot_truyen/Nhiem_vu_radio.

Sheet: 07_chien_dich_cot_truyen/Nhiem_vu_radio — Nhiệm vụ: radio (353 dòng, 9 cột)

| id | nhiem_vu_id | thu_tu | arg | at | key | on |
|---|---|---|---|---|---|---|
| c1m01/0 | c1m01 | 0 |  |  | radio.khai.c1m01.1 | Start |
| c1m01/1 | c1m01 | 1 | east |  | radio.dieuhau.c1m01.2 | Capture |
| c1m01/2 | c1m01 | 2 |  |  | radio.khai.c1m01.3 | Win |
| c1m02/0 | c1m02 | 0 |  |  | radio.linh.c1m02.1 | Start |
| c1m02/1 | c1m02 | 1 |  |  | radio.khai.c1m02.2 | Win |
| c1m03/0 | c1m03 | 0 |  |  | radio.khai.c1m03.1 | Start |
| c1m03/1 | c1m03 | 1 | town |  | radio.linh.c1m03.2 | Capture |
| c1m03/2 | c1m03 | 2 |  |  | radio.khai.c1m03.q1 | Win |
| c1m04/0 | c1m04 | 0 |  |  | radio.mai.c1m04.1 | Start |
| c1m04/1 | c1m04 | 1 | town |  | radio.mai.c1m04.2 | Capture |
| c1m04/2 | c1m04 | 2 |  |  | radio.mai.c1m04.3 | Win |
| c1m05/0 | c1m05 | 0 |  |  | radio.linh.c1m05.1 | Start |
| c1m05/1 | c1m05 | 1 |  |  | radio.khai.c1m05.2 | Win |
| c1m06/0 | c1m06 | 0 |  |  | radio.khai.c1m06.1 | Start |
| c1m06/1 | c1m06 | 1 |  | 60 | radio.linh.c1m06.2 |  |

*15 / 353 dòng đầu: xem sheet 07_chien_dich_cot_truyen/Nhiem_vu_radio.*

### Nhiem_vu_san

Trạng thái: Đã áp

Nguồn dữ liệu: 07_chien_dich_cot_truyen/Nhiem_vu_san.

Sheet: 07_chien_dich_cot_truyen/Nhiem_vu_san — Nhiệm vụ: mục tiêu săn (80 dòng, 10 cột)

| id | nhiem_vu_id | thu_tu | def | heading_deg | route | x_m | z_m |
|---|---|---|---|---|---|---|---|
| c2m06/0 | c2m06 | 0 | elite_mlrs | 225 | 60;82.5;22.5;60;52.5;22.5;90;45 | 90 | 45 |
| c2m06/1 | c2m06 | 1 | elite_grad | 180 | -60;120;-37.5;75;-15;105 | -15 | 105 |
| c2m06/2 | c2m06 | 2 | sam_launcher | 225 | 82.5;-37.5;120;-45;105;0 | 105 | 0 |
| c2m07/0 | c2m07 | 0 | main_battle_tank | 225 |  | 36.3 | 11.23 |
| c2m07/1 | c2m07 | 1 | tank_destroyer | 225 |  | 8.43 | 37.05 |
| c2m07/2 | c2m07 | 2 | light_tank | 225 |  | -27.88 | 25.82 |
| c2m07/3 | c2m07 | 3 | mortar_carrier | 225 |  | -36.3 | -11.23 |
| c2m07/4 | c2m07 | 4 | ifv | 225 |  | -8.43 | -37.05 |
| c2m07/5 | c2m07 | 5 | main_battle_tank | 225 |  | 27.88 | -25.82 |
| c3m06/0 | c3m06 | 0 | mlrs | 225 | 80;90;40;60;70;40 | 60 | 70 |
| c3m06/1 | c3m06 | 1 | artillery | 225 | -40;120;0;90;-30;80 | -20 | 100 |
| c3m06/2 | c3m06 | 2 | mlrs | 225 | 110;-10;90;40;120;30 | 100 | 20 |
| c4m08/0 | c4m08 | 0 | mine_layer | 225 | 90;60;40;80;60;40 | 60 | 70 |
| c4m08/1 | c4m08 | 1 | mine_layer | 225 | -50;100;0;70;-30;60 | -20 | 90 |
| c4m08/2 | c4m08 | 2 | mine_layer | 225 | 90;-30;60;10;90;25 | 80 | -10 |

*15 / 80 dòng đầu: xem sheet 07_chien_dich_cot_truyen/Nhiem_vu_san.*

### Nhiem_vu_thong_ke

Trạng thái: Đã áp

Nguồn dữ liệu: 07_chien_dich_cot_truyen/Nhiem_vu_thong_ke.

Sheet: 07_chien_dich_cot_truyen/Nhiem_vu_thong_ke — Nhiệm vụ: thống kê thoại (193 dòng, 10 cột)

| id | so_cau_vi | so_cau_en | so_cau_p0 | so_cau_p1 | so_cau_p2 | so_cau_p3 | so_cau_p4 |
|---|---|---|---|---|---|---|---|
| c1m01 | 8.0 | 8.0 | 0.0 | 4.0 | 3.0 | 1.0 | 0.0 |
| c1m02 | 7.0 | 7.0 | 0.0 | 4.0 | 2.0 | 1.0 | 0.0 |
| c1m03 | 7.0 | 7.0 | 0.0 | 4.0 | 1.0 | 2.0 | 0.0 |
| c1m04 | 7.0 | 7.0 | 0.0 | 3.0 | 2.0 | 2.0 | 0.0 |
| c1m05 | 13.0 | 13.0 | 0.0 | 6.0 | 4.0 | 0.0 | 3.0 |
| c1m06 | 7.0 | 7.0 | 0.0 | 4.0 | 3.0 | 0.0 | 0.0 |
| c1m08 | 7.0 | 7.0 | 0.0 | 3.0 | 1.0 | 2.0 | 1.0 |
| c1m09 | 7.0 | 7.0 | 0.0 | 4.0 | 3.0 | 0.0 | 0.0 |
| c1m10 | 14.0 | 14.0 | 0.0 | 10.0 | 3.0 | 0.0 | 1.0 |
| c1s1 | 5.0 | 5.0 | 0.0 | 3.0 | 1.0 | 1.0 | 0.0 |
| c2m01 | 8.0 | 8.0 | 0.0 | 5.0 | 3.0 | 0.0 | 0.0 |
| c2m02 | 7.0 | 7.0 | 0.0 | 3.0 | 2.0 | 2.0 | 0.0 |
| c2m03 | 7.0 | 7.0 | 0.0 | 4.0 | 3.0 | 0.0 | 0.0 |
| c2m04 | 8.0 | 8.0 | 0.0 | 3.0 | 4.0 | 1.0 | 0.0 |
| c2m05 | 13.0 | 13.0 | 0.0 | 7.0 | 4.0 | 0.0 | 2.0 |

*15 / 193 dòng đầu: xem sheet 07_chien_dich_cot_truyen/Nhiem_vu_thong_ke.*

### Thoai_moc_thoi_gian

Trạng thái: Đã áp

Nguồn dữ liệu: 07_chien_dich_cot_truyen/Thoai_moc_thoi_gian.

Sheet: 07_chien_dich_cot_truyen/Thoai_moc_thoi_gian — Thoại: mốc thời gian (359 dòng, 8 cột)

| id | nhiem_vu_id | thu_tu_moc | moc_s | khoang_s |
|---|---|---|---|---|
| script.c1m01.01 | c1m01 | 0 | 0.0 | 0.0 |
| script.c1m01.02 | c1m01 | 1 | 20.0 | 20.0 |
| script.c1m01.08 | c1m01 | 2 | 60.0 | 40.0 |
| script.c1m02.01 | c1m02 | 0 | 0.0 | 0.0 |
| script.c1m02.02 | c1m02 | 1 | 40.0 | 40.0 |
| script.c1m03.01 | c1m03 | 0 | 0.0 | 0.0 |
| script.c1m03.02 | c1m03 | 1 | 0.0 | 0.0 |
| script.c1m04.01 | c1m04 | 0 | 0.0 | 0.0 |
| script.c1m05.01 | c1m05 | 0 | 3.0 | 3.0 |
| script.c1m05.03 | c1m05 | 1 | 30.0 | 27.0 |
| script.c1m06.01 | c1m06 | 0 | 0.0 | 0.0 |
| script.c1m06.02 | c1m06 | 1 | 60.0 | 60.0 |
| script.c1m08.01 | c1m08 | 0 | 0.0 | 0.0 |
| script.c1m09.01 | c1m09 | 0 | 0.0 | 0.0 |
| script.c1m10.01 | c1m10 | 0 | 0.0 | 0.0 |

*15 / 359 dòng đầu: xem sheet 07_chien_dich_cot_truyen/Thoai_moc_thoi_gian.*

### Thoai_thong_ke

Trạng thái: Đã áp

Nguồn dữ liệu: 07_chien_dich_cot_truyen/Thoai_thong_ke.

Sheet: 07_chien_dich_cot_truyen/Thoai_thong_ke — Thoại: thống kê theo nhiệm vụ (193 dòng, 12 cột)

| id | kieu_nhiem_vu | ngan_sach_duoi | ngan_sach_tren | so_cau_trung_nguyen_van | so_cau | vuot_ngan_sach | so_cau_vi_qua_dai | so_cau_en_qua_dai | khoang_im_lang_dai_nhat_s |
|---|---|---|---|---|---|---|---|---|---|
| c1m01 | normal | 6 | 10 | 0 | 8.0 | ok | 0.0 | 0.0 | 40.0 |
| c1m02 | normal | 6 | 10 | 0 | 7.0 | ok | 0.0 | 0.0 | 40.0 |
| c1m03 | normal | 6 | 10 | 0 | 7.0 | ok | 0.0 | 0.0 | 0.0 |
| c1m04 | normal | 6 | 10 | 0 | 7.0 | ok | 0.0 | 0.0 | 0.0 |
| c1m05 | boss | 10 | 16 | 0 | 13.0 | ok | 0.0 | 0.0 | 27.0 |
| c1m06 | normal | 6 | 10 | 0 | 7.0 | ok | 0.0 | 0.0 | 60.0 |
| c1m08 | normal | 6 | 10 | 0 | 7.0 | ok | 0.0 | 0.0 | 0.0 |
| c1m09 | normal | 6 | 10 | 0 | 7.0 | ok | 0.0 | 0.0 | 0.0 |
| c1m10 | boss | 10 | 16 | 0 | 14.0 | ok | 0.0 | 0.0 | 25.0 |
| c1s1 | short | 4 | 8 | 0 | 5.0 | ok | 0.0 | 0.0 | 0.0 |
| c2m01 | normal | 6 | 10 | 0 | 8.0 | ok | 0.0 | 0.0 | 15.0 |
| c2m02 | normal | 6 | 10 | 0 | 7.0 | ok | 0.0 | 0.0 | 0.0 |
| c2m03 | normal | 6 | 10 | 0 | 7.0 | ok | 0.0 | 0.0 | 45.0 |
| c2m04 | normal | 6 | 10 | 0 | 8.0 | ok | 0.0 | 0.0 | 125.0 |
| c2m05 | boss | 10 | 16 | 0 | 13.0 | ok | 0.0 | 0.0 | 20.0 |

*15 / 193 dòng đầu: xem sheet 07_chien_dich_cot_truyen/Thoai_thong_ke.*

### Thoai_thong_ke_nhom

Trạng thái: Đã áp

Nguồn dữ liệu: 07_chien_dich_cot_truyen/Thoai_thong_ke_nhom.

Sheet: 07_chien_dich_cot_truyen/Thoai_thong_ke_nhom — Thoại: số câu theo nhóm (2542 dòng, 8 cột)

| id | thoai_thong_ke_id | thu_tu | chieu | gia_tri | so_cau |
|---|---|---|---|---|---|
| c1m01/nguoi_noi/dieuhau | c1m01 | 0 | nguoi_noi | dieuhau | 1.0 |
| c1m01/nguoi_noi/khai | c1m01 | 1 | nguoi_noi | khai | 4.0 |
| c1m01/nguoi_noi/linh | c1m01 | 2 | nguoi_noi | linh | 3.0 |
| c1m01/trigger/critical_failure_imminent | c1m01 | 0 | trigger | critical_failure_imminent | 1.0 |
| c1m01/trigger/defeat | c1m01 | 1 | trigger | defeat | 1.0 |
| c1m01/trigger/mission_start | c1m01 | 2 | trigger | mission_start | 1.0 |
| c1m01/trigger/objective_progress | c1m01 | 3 | trigger | objective_progress | 1.0 |
| c1m01/trigger/point_captured | c1m01 | 4 | trigger | point_captured | 1.0 |
| c1m01/trigger/time | c1m01 | 5 | trigger | time | 2.0 |
| c1m01/trigger/victory | c1m01 | 6 | trigger | victory | 1.0 |
| c1m01/uu_tien/1 | c1m01 | 0 | uu_tien | 1 | 4.0 |
| c1m01/uu_tien/2 | c1m01 | 1 | uu_tien | 2 | 3.0 |
| c1m01/uu_tien/3 | c1m01 | 2 | uu_tien | 3 | 1.0 |
| c1m02/nguoi_noi/hq | c1m02 | 0 | nguoi_noi | hq | 1.0 |
| c1m02/nguoi_noi/khai | c1m02 | 1 | nguoi_noi | khai | 2.0 |

*15 / 2542 dòng đầu: xem sheet 07_chien_dich_cot_truyen/Thoai_thong_ke_nhom.*
