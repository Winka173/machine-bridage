# 05_chien_dich — Chiến dịch và cốt truyện

Chương, nhiệm vụ, biến cố, bộ bài game, nhân vật, thống kê thoại.

Gói cân bằng Machine Brigade, commit 3817f14a, ngày 2026-10-06. Số liệu đầy đủ ở 05_chien_dich.xlsx; file này chỉ nêu luật, giải thích, lý do thiết kế, tham khảo và bảng nhỏ (tối đa 20 dòng, bảng lớn: xem sheet).

## Chiến dịch

**Bối cảnh:** tương lai gần, một vùng duyên hải hư cấu. Tập đoàn quân sự tư nhân **Hegemon** chiếm vùng này và chạy các chương trình vũ khí thử nghiệm: Behemoth, bầy drone và Dự án Icarus. Người chơi chỉ huy **Lữ đoàn Cơ giới 7** (Machine Brigade) của Liên minh Duyên hải.

**Cấu trúc:** 15 chương trong 4 hồi, 193 nhiệm vụ (174 chính, 19 phụ). Mỗi chương có 10 nhiệm vụ chính và 2 nhiệm vụ phụ; nhiệm vụ 5 là boss giữa chương, nhiệm vụ 10 là chiến dịch lớn nhiều giai đoạn (15–25 phút, riêng trận cuối game tới 30 phút). Không hai nhiệm vụ nào trên cùng một bản đồ có cùng cấu hình: mỗi lần quay lại đổi ít nhất 2 yếu tố (hướng xuất phát, vị trí căn cứ, thời tiết/đêm, vùng chơi, loại mục tiêu, phe giữ căn cứ). Trình tạo dữ liệu (Tools/campaign) tự kiểm tra luật này và luật không nhiệm vụ nào đòi thẻ chưa mở.

### Nhân vật

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
| **Kasimir Wolff** | Át chủ bài không quân Hegemon · biệt danh Raven | Kasimir Wolff, biệt danh Raven, chỉ huy không quân Hegemon từ Skyhold và có số lần hạ địch nhiều hơn cả phần còn lại cộng lại. Kiêu ngạo, tài giỏi, chán ngán bất kỳ ai chậm hơn mình. Hắn lái thứ to n… |
| **Giám đốc Lucien Aurel** | Người đứng đầu Hegemon; Dự án Icarus · biệt danh Sol | Aurel điều hành Dự án Icarus, một vũ khí quỹ đạo có thể tấn công bất kỳ điểm nào trên mặt đất. Ông ta tin rằng ai kiểm soát bầu trời sẽ kiểm soát thế giới, và nói về chiến tranh như kế toán nói về bá… |

### Tướng địch là cấu hình AI

Mỗi tướng có bộ bài, thói quen gọi hỏa lực, kiểu căn cứ, ưu tiên xe tinh nhuệ, chân dung, câu khiêu khích và câu khi thua.

| Tướng | Kiểu căn cứ | Thế trận | Bộ bài đặc trưng | Hỏa lực | Ưu tiên tinh nhuệ |
|---|---|---|---|---|---|
| **Tướng Viktor Varga** | varga | Tấn công | Tăng nhẹ lội nước, Tăng chủ lực, Tăng hạng nặng, Pháo chống tăng tự hành, Xe chiến đấu bộ binh, Tăng phun lửa, Tăng hai nòng, Xe phóng drone FPV | Pháo kích, Không kích, Sửa chữa | Tank, Heavy |
| **Đại tá Ilya Orlov** | orlov | Phòng thủ | Pháo phản lực dẫn đường, Lựu pháo tự hành, Xe cối tự hành, Pháo phản lực hạng nặng, Xe tên lửa phòng không tầm trung, Tăng chủ lực, Pháo cao xạ tự hành, Xe chỉ huy | Pháo kích, Tên lửa hành trình, Không kích | Artillery |
| **Đô đốc Magnus Kessler** | kessler | Phòng thủ | Pháo xung kích bánh lốp, Xe chiến đấu bộ binh, Tăng chủ lực, Tăng hạng nặng, Xe tên lửa phòng không tầm trung, Xe phóng drone FPV, Xe rải mìn, Pháo phản lực dẫn đường | Mìn rải từ xa, Pháo kích, Sửa chữa |  |
| **Tiến sĩ Elara Venn** | sen | Tấn công | UAV tấn công, Xe phóng drone FPV, UAV trinh sát, Xe gây nhiễu điện tử, Xe chiến đấu bộ binh, Tăng chủ lực, Pháo cao xạ tự hành | Không kích, Tên lửa hành trình, Sửa chữa | Drone |
| **Kasimir Wolff** | quaden | Tấn công | Trực thăng tấn công, Máy bay cường kích, Tiêm kích, UAV tấn công, Pháo cao xạ tự hành, Tăng chủ lực, Xe tên lửa phòng không tầm trung | Không kích, Tên lửa hành trình, Bom napalm | Air |
| **Tướng Roland Thorne** | aurel | Tấn công | Tăng chủ lực, Tăng hạng nặng, Siêu tăng, Xe chiến đấu bộ binh, Pháo cao xạ tự hành, Pháo phản lực dẫn đường, Pháo chống tăng tự hành | Pháo kích, Không kích, Tên lửa hành trình |  |
| **Giám đốc Lucien Aurel** | aurel | Tấn công | Tăng hạng nặng, Xe chiến đấu bộ binh, Xe pháo điện từ, Trực thăng tấn công, Xe tên lửa phòng không tầm xa, Pháo phản lực hạng nặng, Siêu tăng, Tiêm kích | Tên lửa hành trình, Không kích, Bom napalm |  |

### Dòng thời gian

- Hai năm trước cuộc đổ bộ: chính quyền Meridian Coast sụp đổ. Một tập đoàn khai khoáng thuê Hegemon giữ trật tự, và Hegemon giữ luôn cả vùng.
- Lữ đoàn đổ bộ ở Stormbeach, dựng căn cứ đầu tiên ở Greenvale rồi đánh chiếm pháo đài Ashfield. Bastion gục ngã và thiếu tá Brandt đầu hàng. Hồ sơ của ông ta nhắc đi nhắc lại một cái tên: tướng Varga.
- Varga lộ diện ở Dunebreak. Nhà máy lọc dầu bốc cháy cùng Inferno bên trong, và ở Red Rock, với đạo quân của Thorne bên cạnh, Behemoth gục ngã. Đêm đó Mara kể với Kade nơi cô đã học cách chế tạo nó.
- Lữ đoàn làm mù tuyến radar của Orlov, bắn rơi Harpy và hạ Jötunn trước cổng Frostpeak. Orlov rút pháo về phía bắc. Câu cuối của ông ta trên bộ đàm: "Mùa đông luôn quay lại."
- Juggernaut bị lật, Tempest gục ngay trên cầu tàu của nó và bến cảng về tay ta. Kessler chạy ra biển, và ngoài khơi Beacon Bay, lữ đoàn chiếm các trận địa pháo bờ biển cũ rồi đánh chìm Leviathan. Kessler sống sót; hạm đội của ông ta thì không. Một cánh quân của Thorne đã không có mặt ở nơi đã hứa.
- Locust gục ngã, Matriarch bị đẩy lui một lần rồi cuối cùng cũng rơi trên tán rừng đang cháy. Tiến sĩ Venn một mình bước ra khỏi xưởng drone, ra hàng cùng một ổ đĩa đề "Icarus", và bắt đầu làm việc cho Accord.
- Cuộc tổng phản công của Varga vỡ tan trước Hollow Dam. Trước đó, trong đúng một buổi sáng, Varga và Kade ngừng bắn để dân trong thung lũng kịp chạy; đó là lần duy nhất hai người nói chuyện với nhau. Moloch lao xuống hẻm sông. Quân của Thorne lại tới muộn.
- Veyra được giải phóng. Giữa trận cuối, căn cứ của Thorne quay pháo vào lữ đoàn; Nadia là người thấy đầu tiên và cứu được một nửa quân ta. Ta đánh ngược lại qua Behemoth Mk.II và chặn Nemesis ngay rìa trung tâm. Thorne trốn thoát cùng một phần ba đạo quân của Accord.
- Lữ đoàn đuổi theo Thorne vào Deepcut Mine. Ixion gục ngã; Moloch được kéo lên từ hẻm sông, cùng Tartarus dưới lòng đất, bị chặn lại trước khi tới căn cứ của ta. Thorne lại trốn thoát, ra biển.
- Typhon nổi lên giữa vịnh với Thorne trên đài chỉ huy, rồi chìm. Tin nhắn cuối của ông ta tới sau khi tàu đã chìm: tọa độ bãi phóng của Dự án Icarus, và một câu: "Đừng để tôi đã đúng." Không ai tìm thấy thi thể ông ta.
- Icarus Mk.0 lộ diện trên Skyhold rồi bỏ chạy: một bản thử nghiệm, Venn nói, cho một thứ lớn hơn nhiều. Hawk hạ Raven trên không, và trong trận đánh chiếm Skyhold, anh bắn phát cuối cùng.
- Orlov đánh trận cuối cùng với Monster rồi ra hàng qua bộ đàm. Venn phát hiện chương trình drone của mình đã nằm trong tay Aurel. Daedalus rơi xuống Skygate Array, và con đường tới Helion mở ra.
- Varga ngã xuống như một người lính; Kessler mặc cả tới phút cuối. Aurel phóng Icarus và một thanh vonfram rơi từ quỹ đạo, nhưng rồi Icarus rơi theo, đúng như cái tên của nó. Aurel chiến đấu tới cùng trong xác phi thuyền. Meridian Coast được giải phóng.
- Ở Foundry, Mara đối mặt với chiếc Behemoth Mk.0 cô từng vẽ khi còn là một kỹ sư trẻ, và mang bản thiết kế của nó về. Thiếu tá Brenn ký nhận từng trang.
- Lữ đoàn đưa tiến sĩ Venn qua Mirewood và Border Crossing với hai chiếc Locust bám theo. Tới bờ bên kia, bà đưa ra lựa chọn của mình: bà ở lại với lữ đoàn.
- Đội quân của đại tá Reyn tìm thấy Hawk và đưa anh ra qua Frostpeak và Jungle Pass, với Harpy trên đầu. Raven để anh đi, lần này.

### Chương 1: Coast of Fire

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| c1m01 | **Đổ bộ** Xuồng đổ bộ đã chạm cát. Chiếm bãi biển và con dốc phía trên trước khi đồn Hegemon kịp tỉnh ngủ. Quân ta tự chiến đấu: bạn chọn nơi đánh, mang theo gì và lúc nào pháo khai hỏa. | Stormbeach | Chiếm cứ điểm |  | 100 xu | Bán tải rốc-két |
| c1m02 | **Bịt mắt bờ biển** Trạm radar trên vách đá đang gọi pháo Hegemon bắn vào từng chiếc xuồng còn trong vịnh. Hạ nó xuống, các đợt đổ bộ sau sẽ vào bờ mà không bị phát hiện. | Stormbeach | Phá hủy |  | 105 xu | Xe cối tự hành |
| c1m03 | **Làng chài** Làng chài ở cửa sông, ngã tư phía trên và trang trại phía xa khống chế mọi con đường vào đất liền. Chỉ một nhúm lính trinh sát của Brandt giữ chúng. Chiếm cả ba là lữ đoàn có chỗ thở. | Greenvale | Chiếm cứ điểm |  | 105 xu | Tăng nhẹ lội nước |
| c1m04 | **Tiền đồn đầu tiên** Mara muốn lấy ngã tư làm căn cứ. Chiếm nó, lập tiền đồn ở đó và giữ vững trong lúc đội của cô thả tháp xuống. Trụ được rồi, lữ đoàn sẽ có sở chỉ huy đầu tiên trên Meridian Coast. | Greenvale | Lập tiền đồn |  | 110 xu · HQ 1 | Dàn rốc-két, Xưởng sửa chữa |
| c1m05 | **Bastion Mk.0** Brandt tung pháo đài nguyên mẫu băng qua cánh đồng Greenvale trong đêm để nghiền nát trại mới của ta. Nó chậm và giáp mỏng. Chặn nó lại. | Greenvale | Tiêu diệt boss Bastion Mk.0 · Pháo đài nguyên mẫu |  | 170 xu | Xe công binh |
| c1m06 | **Đường tiếp tế** Nhiên liệu và đạn cho các đơn vị tiền phương, năm xe tải dưới mưa. Đưa ít nhất ba xe tới trang trại phía tây. Xe tải sẽ chờ hộ tống; chúng không tự lao vào ổ phục kích đâu. | Greenvale | Hộ tống |  | 115 xu | Bán tải cao xạ |
| c1m08 | **Đường vào Ashfield** Thị trấn Ashfield cùng hai kho nhiên liệu nằm ngay trước pháo đài. Chiếm cả ba, pháo đài sẽ bị cắt khỏi đường cái. | Ashfield | Chiếm cứ điểm |  | 120 xu |  |
| c1m09 | **Đạn cho trận vây thành** Pháo đánh pháo đài cần đạn. Đưa đoàn xe chở đạn vòng đường phía đông vào thị trấn Ashfield; năm xe phải tới được ba. | Ashfield | Hộ tống |  | 125 xu |  |
| c1m10 | **Pháo đài Ashfield** chiến dịch lớn Lò gạch cũ trên đồi là điểm mạnh nhất của Hegemon trên Meridian Coast, và Bastion đi tuần trong sân của nó. Đốt kho nhiên liệu bên ngoài, chọn cách làm yếu tường… | Ashfield | Phá hủy |  | 305 xu |  |
| c1s1 | **Dấu xích trong sương** phụ Nadia nghe thấy tiếng động cơ trong sương quanh các trang trại Greenvale. Đưa một xe tới từng cứ điểm trong ba cứ điểm để xem trước khi thứ gì ngoài đó kịp cố thủ. | Greenvale | Trinh sát |  | 350 xu |  |

### Chương 2: Black Gold

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| c2m01 | **Dầu và cát** Lữ đoàn đã tới mỏ dầu Dunebreak. Hegemon muốn giành lại trước khi ta kịp phá giếng. Trụ vững ở mỏ dầu trong năm phút. | Dunebreak | Trụ vững | varga | 130 xu | Pháo cao xạ tự hành |
| c2m02 | **Giếng dầu Red Rock** Đầu giếng, ốc đảo và trạm dừng đoàn lạc đà ở Red Rock cấp dầu cho đường ống tới Dunebreak. Xe tăng của Varga giữ ốc đảo. Chiếm cả ba. | Red Rock | Chiếm cứ điểm | varga | 135 xu | Lựu pháo tự hành |
| c2m03 | **Đoàn xe đêm** Xe bồn nhiên liệu cho lữ đoàn, băng qua hẻm núi trong đêm, qua ốc đảo tới đầu giếng. Năm xe phải qua được ba. | Red Rock | Hộ tống |  | 135 xu | Tăng phun lửa |
| c2m04 | **Cắt đường ống** Năm trạm đường ống dẫn dầu từ Red Rock vào nhà máy lọc dầu. Cho nổ tung tất cả. Một trận đột kích, không căn cứ: vào nhanh, ra nhanh hơn. | Dunebreak | Phá hủy | varga | 140 xu | Không kích |
| c2m05 | **Inferno** Varga tung Inferno ra giữa bão cát để canh con đường tới nhà máy lọc dầu: một chiếc Behemoth dựng lại quanh các súng phun lửa. Tránh xa tầm với của nó và đẩy nó lùi lại. | Dunebreak | Tiêu diệt boss Inferno · Behemoth phun lửa | varga | 215 xu | Xe tiếp đạn |
| c2m06 | **Săn bọ cạp** Ba dàn pháo phản lực và tên lửa của Varga ẩn giữa các khối đá, đánh dấu màu đỏ. Tìm ra chúng trong bão cát và tiêu diệt. | Red Rock | Săn mục tiêu | varga | 145 xu | Tháp tên lửa chống tăng |
| c2m07 | **Đồn ốc đảo** Một đại đội dân quân Red Rock đã tuyên bố đứng về phía Accord và đang giữ ốc đảo. Xe tăng của Varga vây kín họ. Phá vòng vây trước khi sở chỉ huy của họ thất thủ. Các xe vây được đánh… | Red Rock | Giải vây |  | 150 xu | Xe bom bọc thép |
| c2m08 | **Giữ nhà máy lọc dầu** Ta đã đặt được một chân vào nhà máy lọc dầu. Varga đang tung lực lượng dự bị vào đó. Giữ sân nhà máy trong bốn phút. | Dunebreak | Giữ cứ điểm | varga | 155 xu |  |
| c2m09 | **Trại của Varga** Varga đã đào sở chỉ huy vào cuối hẻm núi: pháo chống tăng, những chiếc xe tăng hắn ưng ý nhất, và cái tính nóng của hắn. San phẳng sở chỉ huy. Hắn sẽ chạy; để hắn biết ta đang tới. | Red Rock | Đấu tướng | varga | 155 xu |  |
| c2m10 | **Đột kích nhà máy lọc dầu** Trận đột kích mà Varga sợ nhất: chiếm mỏ dầu và ốc đảo, chọn mục tiêu kế tiếp, rồi cho nổ tháp và bồn chứa của nhà máy, cùng Inferno bên trong. Giai đoạn: Mỏ dầu và ốc đả… | Dunebreak | Chiếm cứ điểm | varga | 290 xu |  |
| c2m11 | **Behemoth ở Red Rock** chiến dịch lớn Chiến dịch giành Red Rock, lần đầu tiên có đạo quân của tướng Thorne ở bên sườn. Chiếm giếng dầu, chọn đòn đánh, chiếm và giữ ốc đảo, rồi hạ chính Behemoth. Gia… | Red Rock | Chiếm cứ điểm | varga | 390 xu |  |
| c2s1 | **Bản đồ bãi mìn** phụ Nadia cần người tới xem ốc đảo, nhà máy và mỏ dầu trong đêm: Varga đang cho rải mìn, và cô muốn biết ở đâu. Nhìn rồi đi, đừng nấn ná. | Dunebreak | Trinh sát |  | 450 xu |  |
| c2s2 | **Trực thăng của Varga** phụ Varga gọi trực thăng tới săn đoàn xe của ta trên Red Rock. Hawk muốn bắn rơi mười chiếc trước khi mặt trời lặn. Mang phòng không theo. | Red Rock | Bắn hạ máy bay |  | 450 xu |  |

### Chương 3: The Long Winter

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| c3m01 | **Vào đèo** Whiteout Pass là con đường duy nhất lên phía bắc. Tiền đồn của Orlov giữ trạm tín hiệu, hồ băng và xưởng cưa. Chiếm cả ba trong tuyết. | Whiteout Pass | Chiếm cứ điểm | orlov | 165 xu | Xe tên lửa phòng không tầm trung |
| c3m02 | **Làm mù radar** Trạm đầu tiên trên tuyến radar của Orlov đứng trên cao điểm phía tây. Chừng nào nó còn nhìn thấy, pháo của hắn còn bắn trúng mọi thứ ta di chuyển. Phá hủy nó. | Frostpeak | Phá hủy | orlov | 170 xu | Trực thăng tấn công |
| c3m11 | **Đường radar** Con đường tới tuyến radar của Orlov chạy qua ba xóm nhỏ đóng băng trên sườn Frostpeak. Chiếm cả ba trong tuyết; người chỉ điểm của ông ta nấp ở từng xóm. | Frostpeak | Chiếm cứ điểm | orlov | 175 xu | Tiêm kích |
| c3m03 | **Ngôi làng trong sương** Ngôi làng dưới thung lũng là chỗ trú duy nhất trong vòng nhiều cây số. Orlov muốn lấy lại, và sương mù che pháo của hắn. Giữ làng trong ba phút rưỡi. | Frostpeak | Giữ cứ điểm | orlov | 175 xu | Trực thăng trinh sát vũ trang |
| c3m04 | **Căn cứ trên băng** Mara muốn dựng căn cứ tiền phương trên hồ băng, giữa đèo. Chiếm hồ, lập tiền đồn và giữ nó ba phút. Ban đêm. Trên băng. | Whiteout Pass | Lập tiền đồn | orlov | 180 xu | Nhà chứa xe |
| c3m05 | **Harpy** Harpy vẫn săn các đoàn tiếp tế của ta trên đèo, và một phi công át chủ bài lái chiếc phản lực mang phù hiệu đen bay cùng nó. Bắn rơi pháo hạm bay. Phòng không có là để cho lúc này. | Whiteout Pass | Tiêu diệt boss Harpy · Trực thăng khổng lồ | orlov | 275 xu · HQ 2 | UAV trinh sát |
| c3m06 | **Pháo của Orlov** Nadia đã định vị được ba khẩu đội của Orlov qua ánh chớp đầu nòng, đánh dấu màu đỏ. Chúng di chuyển sau mỗi loạt bắn. Săn chúng trong bóng tối. | Frostpeak | Săn mục tiêu | orlov | 185 xu | Xe rải mìn |
| c3m12 | **Dưới làn pháo** Orlov biết ta đang ở đâu. Trong năm phút, mọi khẩu pháo trên tuyến của ông ta sẽ nã vào một thung lũng, thung lũng của ta, và quân yểm hộ sẽ tràn vào sau làn đạn. Trụ vững. | Frostpeak | Trụ vững | orlov | 190 xu |  |
| c3m07 | **Những căn nhà gỗ trong tuyết** Các gia đình trên đèo đã trú trong những căn nhà gỗ và nhà kho phía nam. Orlov đang nã pháo vào mọi thứ còn mái che. Giữ ít nhất một căn đứng vững trong bảy phút. | Whiteout Pass | Bảo vệ | orlov | 195 xu |  |
| c3m08 | **Đoàn xe cứu thương** Thuốc men và bác sĩ cho trạm tín hiệu, nơi thương binh trên đèo đang chờ. Năm xe trong đêm; phải tới được ba xe. | Whiteout Pass | Hộ tống |  | 195 xu |  |
| c3m09 | **Trận địa pháo của Orlov** Sở chỉ huy của Orlov nằm sau một bức tường ụ pháo, nơi hắn nhìn thấy cả thung lũng. Chọc thủng và san phẳng nó. Hắn sẽ không chờ ta đâu. | Frostpeak | Đấu tướng | orlov | 200 xu |  |
| c3m10 | **Tuyến Frostpeak** chiến dịch lớn Trạm cuối của tuyến radar, pháo đài phía sau nó, và Jötunn canh cổng. Làm mù radar trên đồi, chọn đòn thứ hai, tiêu diệt Jötunn, rồi giữ cổng trước đợt phản kích củ… | Frostpeak | Phá hủy | orlov | 490 xu |  |
| c3s1 | **Pháo nằm ở đâu** phụ Trước trận đánh lớn, Nadia muốn mọi trận địa pháo quanh Frostpeak có mặt trên bản đồ của cô. Đưa xe tới đồi radar, ngôi làng và trại gỗ, trong sương mù. | Frostpeak | Trinh sát |  | 560 xu |  |
| c3s2 | **Fenrir** phụ Nadia phát hiện xe tiên phong mùa đông của Orlov giữa bão tuyết Whiteout Pass: Fenrir, một thợ săn hạng nặng đánh dấu mục tiêu cho pháo của ông ta. Đuổi theo và hạ nó trước khi bão tan. | Whiteout Pass | Tiêu diệt boss Fenrir · Xe tiên phong | orlov | 560 xu |  |

### Chương 13: Blueprints

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| i1m01 | **Cổng Foundry** Foundry có ba lối vào: cổng bốc dỡ, nhà ga đường ray và xưởng luyện. Chiếm cả ba trong đêm, thật lặng lẽ, trước khi lính gác biết ta đã tới. | Foundry | Chiếm cứ điểm | varga | 205 xu |  |
| i1m02 | **Sổ cái** Thiếu tá Brenn biết Hegemon lưu hồ sơ thế nào: ba bản một. Bản vẽ Behemoth bị chia ra ba phòng lưu trữ. Đưa xe tới từng phòng, phần còn lại để ông lo. | Foundry | Trinh sát | varga | 210 xu |  |
| i1m03 | **Behemoth Mk.0** Tiếng báo động đã đánh thức lính gác lâu năm nhất của Foundry: Behemoth Mk.0, bản nguyên mẫu Mara thiết kế khi cô chưa hiểu chuyện. Nó chậm và cũ, nhưng thuộc từng góc của các xưởng… | Foundry | Tiêu diệt boss Behemoth Mk.0 · Behemoth nguyên mẫu | varga | 320 xu |  |
| i1m04 | **Rời Foundry** Ta đã có bản vẽ; Hegemon muốn lấy lại trước khi chúng lên xe. Giữ bãi bốc dỡ cho tới khi đoàn xe chất hàng xong. | Foundry | Giữ cứ điểm | varga | 215 xu |  |

### Chương 4: Iron Harbor

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
| c4m08 | **Tàu rải mìn trên cạn** Đêm nào các xe rải mìn của Kessler cũng gieo mìn khắp những con đường vào cảng. Nadia đã đánh dấu ba chiếc. Săn chúng trước khi chúng xong một vòng. | Rust Yard | Săn mục tiêu | kessler | 245 xu | Tiếp viện thả dù |
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

### Chương 5: Burning Canopy

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| c5m01 | **Đền Tro** Lực lượng canh gác vòng ngoài của Venn giữ bến đền cổ và làng phía đông Jungle Pass. Chiếm trọn con đèo dưới mưa. | Jungle Pass | Chiếm cứ điểm | sen | 275 xu | UAV tấn công |
| c5m02 | **Xe bầy đàn** Ba xe phóng của Venn đêm nào cũng tung bầy drone qua đồng dung nham. Nadia đã đánh dấu chúng. Săn chúng dưới ánh sáng của dung nham. | Emberridge | Săn mục tiêu | sen | 275 xu | Xe phóng drone FPV |
| c5m03 | **Đường ven sông** Thiết bị bắc cầu cho công binh, ngược đường ven sông qua sương rừng tới làng phía tây. Năm xe phải tới được ba; drone của Venn sẽ săn lùng chúng. | Jungle Pass | Hộ tống |  | 280 xu | Xe phóng drone cảm tử tầm xa |
| c5m04 | **Nhà máy địa nhiệt** Mara muốn lấy nhà máy địa nhiệt giữa Emberridge: điện miễn phí cho một căn cứ tiền phương. Chiếm nó, lập tiền đồn, giữ ba phút. | Emberridge | Lập tiền đồn | sen | 285 xu | Sân bay dã chiến |
| c5m08 | **Giữ đèn sáng** Các bồn hơi của nhà máy địa nhiệt giờ cấp điện cho cả lữ đoàn. Drone của Venn đang lao tới từ phía nam. Giữ ít nhất một bồn đứng vững trong bảy phút. | Emberridge | Bảo vệ Locust · Tàu con drone | sen | 285 xu | Xe gây nhiễu điện tử |
| c5m12 | **Vòng ra phía sau** Quân canh vòng ngoài của Venn nhìn về đèo từ phía nam. Vòng qua các làng phía bắc và chiếm cả đèo từ phía sau, trong mưa. | Jungle Pass | Chiếm cứ điểm | sen | 290 xu |  |
| c5m05 | **Matriarch** Tàu sân bay drone của Venn, Matriarch, đang hạ xuống con đèo trong cơn bão, bầy drone tuôn ra từ bụng nó. Máy bay của ta không bay nổi trong thời tiết này. Phòng không và mọi khẩu pháo… | Jungle Pass | Tiêu diệt boss Matriarch · Tàu mẹ drone | sen | 440 xu |  |
| c5m06 | **Cổng Dung Nham** Xưởng drone nằm trong một pháo đài ở đầu bắc sườn núi. Phá tường trong đêm và san phẳng sở chỉ huy. | Emberridge | Phá hủy | sen | 295 xu |  |
| c5m11 | **Tín hiệu phòng thí nghiệm** Nadia lần theo một tín hiệu tới một phòng thí nghiệm trên sườn núi mà chính bản đồ của Hegemon bỏ sót. Đưa xe tới từng tòa nhà đã đánh dấu. Có thể Venn đang ở trong. | Emberridge | Trinh sát | sen | 300 xu |  |
| c5m07 | **Quét sạch tán rừng** Drone tấn công của Venn làm chủ bầu trời trên đèo. Bắn rơi mười bốn chiếc, và rừng lại thuộc về lữ đoàn. | Jungle Pass | Bắn hạ máy bay | sen | 305 xu |  |
| c5m13 | **Ngôi đền trong đêm** Bến lội qua ngôi đền là ngả qua duy nhất bầy drone không nhìn thấu được qua tán rừng. Giữ nó suốt đêm. | Jungle Pass | Giữ cứ điểm | sen | 305 xu |  |
| c5m09 | **Những nhà chứa trên đèo** Sở chỉ huy dã chiến của Venn được bao quanh bởi những nhà chứa drone và xe gây nhiễu. Phá nó trong đêm và san phẳng sở chỉ huy. Nadia nghĩ bà ấy có thể sẽ không đánh tới c… | Jungle Pass | Đấu tướng | sen | 310 xu |  |
| c5m10 | **Matriarch** chiến dịch lớn Matriarch đã quay lại lơ lửng trên Emberridge, tiếp bầy drone cho mọi đơn vị Hegemon trong rừng. Chiếm các đường đắp, chọn đòn kế tiếp, trụ vững trước bầy drone nó tung r… | Emberridge | Chiếm cứ điểm | sen | 750 xu | Máy bay mẹ thả drone |
| c5s1 | **Sổ ghi chép của Venn** phụ Venn có các trạm thực địa trong đèo, không ghi trong sổ sách của Hegemon. Nadia muốn tận mắt thấy cả ba trước khi có người dọn sạch chúng. | Jungle Pass | Trinh sát |  | 865 xu |  |
| c5s2 | **Làng đốt than** phụ Dân đốt than trên sườn núi đã cầm cự với Hegemon suốt hai năm trong một trại có rào lũy. Giờ họ bị vây kín. Phá vòng vây; quân vây được đánh dấu. | Emberridge | Giải vây |  | 865 xu |  |

### Chương 6: Counterstrike

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| c6m01 | **Ashfield rực lửa** Hegemon phản đòn đúng nơi ta giành chiến thắng đầu tiên. Varga đang tung thiết giáp vào pháo đài Ashfield, giờ là của ta, cả tháp lẫn tường. Giữ sở chỉ huy của nó đứng vững trong… | Ashfield | Bảo vệ | varga | 315 xu | Tăng hạng nặng |
| c6m13 | **Phòng tuyến của Brandt** Thiếu tá Brandt đã về phe ta, và ông biết chính xác Varga sẽ đánh vào Ashfield ở đâu. Chiếm quảng trường thị trấn, lập tiền đồn và giữ nó trong lúc công binh của ông dựng t… | Ashfield | Lập tiền đồn | varga | 320 xu | Tăng hai nòng |
| c6m02 | **Sơ tán Whiteout Pass** Đợt phản công của Varga đang tràn qua đèo. Dân làng ở hồ băng phải rời đi: sáu xe tải, cứ vài giây một chiếc, theo đường về trại của ta. Giữ hồ cho tới khi xe cuối cùng rời đ… | Whiteout Pass | Di tản | varga | 325 xu | Trạm đánh chặn C-RAM |
| c6m16 | **Lại Greenvale** Thiết giáp của Varga đã chiếm lại ngã tư Greenvale, ngôi làng và trang trại ta giành được những ngày đầu. Chiếm lại chúng từ phía bên kia, trong sương. | Greenvale | Chiếm cứ điểm | varga | 325 xu | Xe la-de phòng không |
| c6m11 | **Canh mùa gặt** Cuộc tổng phản công của Varga đã tới Greenvale, và Aurel muốn đốt các si-lô thóc cùng tháp nước để cả thung lũng chết đói mùa đông này. Giữ ít nhất một công trình đứng vững qua cơn b… | Greenvale | Bảo vệ | varga | 330 xu |  |
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
| c6m10 | **Bảo vệ con đập** chiến dịch lớn Quân bài cuối của Varga là Moloch, một nhà máy bánh xích vừa lăn vừa đóng xe tăng, và nó đang tiến về con đập. Giữ đỉnh đập cho tới khi quân của Thorne tới. Giai đoạ… | Hollow Dam | Giữ cứ điểm | varga | 880 xu |  |
| c6s1 | **Không kích đêm** phụ Máy bay đột kích đêm của Varga đang ném bom pháo đài Ashfield. Hawk muốn bắn rơi mười bốn chiếc trước bình minh. | Ashfield | Bắn hạ máy bay |  | 1010 xu |  |
| c6s2 | **Khảo sát con đập** phụ Mara cần biết con đập có chịu nổi một trận vây hãm hay không. Đưa xe tới trạm phát điện, cây cầu và bến lội để công binh của cô quan sát. | Hollow Dam | Trinh sát |  | 1010 xu |  |

### Chương 14: The Queen's Choice

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| i2m01 | **Vào Mirewood** Đại úy Mendez muốn qua khỏi Mirewood trước chạng vạng. Chiếm hai ngôi làng và ngôi đền chìm trên các đường đắp, thật nhanh, trong sương. | Mirewood | Chiếm cứ điểm | aurel | 370 xu | Xe phát khiên |
| i2m02 | **Chiếc Locust thứ nhất** Một chiếc Locust đã tìm ra đoàn xe: một tàu mang drone cỡ nhỏ trong chính chương trình của Venn, săn bà theo dấu hiệu vô tuyến. Bắn hạ nó trước khi bầy drone tới được đoàn x… | Mirewood | Tiêu diệt boss Locust · Tàu con drone | aurel | 560 xu |  |
| i2m03 | **Cây cầu lớn** Một toán dân quân Accord muốn đem Venn ra xử treo cổ đã tới Border Crossing trước, và chúng không chịu tránh đường. Giữ cây cầu lớn cho tới khi đoàn xe qua hết. | Border Crossing | Giữ cứ điểm |  | 375 xu |  |
| i2m04 | **Chiếc Locust thứ hai** Chiếc Locust thứ hai đã tìm ra ngả qua. Nó là thứ cuối cùng chắn giữa Venn và bờ bên kia. Bắn hạ nó và đưa bà qua. | Border Crossing | Tiêu diệt boss Locust · Tàu con drone | aurel | 570 xu |  |

### Chương 7: Veyra

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
| c7m02 | **Những cây cầu Veyra** Thủ đô nằm trên một hòn đảo giữa sông. Trước khi tướng Thorne tới, Nadia muốn quan sát khu vườn, quảng trường cung điện và nhà ga. | Veyra | Trinh sát | aurel | 415 xu | Nhà chứa máy bay |
| c7m17 | **Những cây cầu trong đêm** Trung tâm Veyra nằm trên hòn đảo sau ba đầu cầu. Chiếm khu vườn, quảng trường cung điện và nhà ga từ bờ bên kia, trong đêm, theo sau làn đạn của Dahl. | Veyra | Chiếm cứ điểm | aurel | 420 xu |  |
| c7m06 | **Quảng trường cung điện** Một chỗ đứng chân trong thủ đô: quảng trường cung điện. Vệ binh của Aurel muốn giành lại. Giữ nó trong sương mù bốn phút. | Veyra | Giữ cứ điểm | aurel | 425 xu |  |
| c7m11 | **Bão trên Veyra** Trực thăng của đội cận vệ Aurel đang săn quân kháng chiến trên các mái nhà Veyra giữa cơn bão. Bắn hạ mười bốn chiếc. | Veyra | Bắn hạ máy bay | aurel | 425 xu |  |
| c7m09 | **Dập tắt đài phát** Đài tuyên truyền của Hegemon phát cho cả nước mỗi đêm từ mái vòm radar cạnh cung điện. Đêm nay thì không. Phá hủy nó. | Veyra | Phá hủy | aurel | 430 xu |  |
| c7m18 | **Tuyến sông** Cận vệ của Aurel đang dồn mọi thứ vào tuyến sông của ta trước trận đánh cuối. Trụ vững năm phút; pháo của Dahl sẽ lo phần còn lại. | Veyra | Trụ vững | aurel | 435 xu |  |
| c7m08 | **Rời cung điện** Các gia đình đang trú trong cung điện phải ra ngoài trước trận quyết chiến: sáu xe tải qua cầu phía tây, cứ vài giây một chiếc. Phải thoát được bốn xe. | Veyra | Di tản | aurel | 435 xu |  |
| c7m10 | **Giải phóng Veyra** chiến dịch lớn Veyra, với đạo quân và căn cứ của tướng Thorne bên cạnh. Chiếm các đầu cầu, chọn đòn đánh, đánh chiếm cung điện và quảng trường, rồi chặn thứ cuối cùng Aurel tung… | Veyra | Chiếm cứ điểm | aurel | 1055 xu |  |
| c7s1 | **Những bức thư** phụ Nadia đã chặn được những bức thư giữa tướng Thorne và một người nào đó ở Metro City. Cô muốn tự mình xem ba điểm trao thư, một cách lặng lẽ. | Metro City | Trinh sát |  | 1215 xu |  |

### Chương 8: Underworld

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
| c8m13 | **Thợ mỏ Deepcut** Thorne đang giữ ba trăm thợ mỏ trong các lán trại dưới hố để đào đường cho Moloch. Dân quân của Varro thuộc từng đường hầm. Chiếm cả ba lán trại và mọi người thợ mỏ sẽ được ra ngoà… | Deepcut Mine | Chiếm cứ điểm | hung | 475 xu |  |
| c8m14 | **Đánh thẳng vào Moloch** Moloch lấy điện từ một đường dây duy nhất dẫn xuống hố, và viên quản lương của Thorne ngồi ngay cạnh tủ điện với lương của cả một năm. Giữ con dốc trong lúc công binh cắt đư… | Deepcut Mine | Trụ vững | hung | 955 xu |  |
| c8m10 | **Hố sâu nhất** chiến dịch lớn Chiến dịch vào khu mỏ của Thorne: chiếm miệng hố, chọn mục tiêu kế tiếp, phá các xưởng, rồi đối mặt với thứ đang chờ dưới đáy: Moloch, được kéo lên từ hẻm sông và chạy… | Deepcut Mine | Chiếm cứ điểm | hung | 1150 xu |  |
| c8s1 | **Bản đồ khảo sát** phụ Nadia muốn lấy bản đồ khảo sát của khu mỏ từ ba tòa nhà trên đồi cát. Nhìn thôi, đừng nán lại. | Dunebreak | Trinh sát | hung | 1325 xu |  |
| c8s2 | **Chuyến bay đêm** phụ Thorne đang chở vàng ra khỏi khu mỏ trong đêm. Bắn hạ các máy bay vận tải của hắn. | Red Rock | Bắn hạ máy bay | hung | 1325 xu |  |

### Chương 9: Rough Water

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| c9m01 | **Lại bến cảng** Thorne đã chiếm Ironport cùng tàn quân của Kessler. Chiếm lại cầu tàu trong cơn bão. | Ironport | Chiếm cứ điểm | hung | 485 xu | Xe la-de diệt tăng |
| c9m02 | **Trở lại bãi biển** Thorne đang đổ quân lên chính bãi biển nơi cuộc chiến của ta bắt đầu. Chiếm bãi biển từ phía bên kia, trong mưa. | Stormbeach | Chiếm cứ điểm | hung | 485 xu | Mìn rải từ xa |
| c9m03 | **Đoàn xe đêm** Đưa đoàn xe tải tiếp tế qua các con đường bến cảng trong đêm. Lính tuần của Thorne đang chờ. | Ironport | Hộ tống | hung | 490 xu | Oanh tạc cơ chiến lược |
| c9m04 | **Pháo bờ biển** Thorne đã đặt lại pháo trên bãi biển. Phá chúng trước khi tàu của hắn cập bờ. | Stormbeach | Phá hủy | hung | 495 xu |  |
| c9m05 | **Charybdis** Từ trong sương lao ra Charybdis, một tàu đệm khí đổ bộ lao lên bãi biển với tốc độ sáu mươi hải lý và đổ thiết giáp. Hạ nó trước khi nó kịp đổ quân. | Stormbeach | Tiêu diệt boss Charybdis · Tàu đệm khí đổ bộ | hung | 745 xu · HQ 4 |  |
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

### Chương 15: Hawk and Raven

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| i3m01 | **Hawk bị bắn rơi** Hawk bị bắn rơi sau chiến tuyến, đâu đó trên các điểm cao Frostpeak, và đèn hiệu của anh lúc có lúc không. Đoàn quân của đại tá Reyn sẽ lục soát đồi radar, ngôi làng và trại gỗ, t… | Frostpeak | Trinh sát | quaden | 530 xu |  |
| i3m02 | **Harpy** Raven đang tự mình săn đoàn cứu hộ, từ Harpy: pháo hạm bay to như con tàu, ổ rocket và một tốp trực thăng hộ tống. Cho bệ phóng di chuyển liên tục, để ý đòn tấn công của nó, và đuổi nó đi. | Jungle Pass | Tiêu diệt boss Harpy · Trực thăng khổng lồ | quaden | 800 xu |  |
| i3m03 | **Đoàn quân của Crown** Hawk đã tới được một ngôi làng ở Jungle Pass, và quân mặt đất của Raven vây kín nó. Đoàn thiết giáp hạng nặng của đại tá Reyn sẽ phá vòng vây. Các xe trong vòng vây đã được đá… | Jungle Pass | Giải vây | quaden | 535 xu |  |
| i3m04 | **Đường về nhà** Đoàn quân đã có Hawk và đang chạy về phòng tuyến của ta qua các điểm cao Frostpeak, với mọi thứ Raven còn lại bám đuôi. Trụ vững năm phút cho tới khi được đón. | Frostpeak | Trụ vững | quaden | 540 xu |  |

### Chương 10: War in the Sky

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| c10m01 | **Bầy quạ trên đèo** Cầm trong tay hồ sơ của Venn, lữ đoàn quay mũi về Skyhold. Phi đội của Wolff đón đánh ta trên Frostpeak, lần này từ phía nam. Bắn rơi mười hai chiếc. | Frostpeak | Bắn hạ máy bay | quaden | 545 xu | Oanh tạc cơ tàng hình |
| c10m02 | **Mắt nhìn Skyhold** Trước khi đánh căn cứ không quân, Nadia muốn tận mắt thấy nó: hai sân đỗ và đường băng. Đưa xe tới từng nơi, ngay dưới mũi Wolff. | Skyhold | Trinh sát | quaden | 545 xu | Pháo hạm bay |
| c10m11 | **Sân bay dã chiến của Vault** Đại úy Okoye có một sân bay dã chiến cho chiến dịch trên không, một đoạn đường trên các điểm cao Frostpeak, và một trăm chuyến bay vận tải cần hạ cánh ở đó. Giữ nó tron… | Frostpeak | Giữ cứ điểm | quaden | 550 xu |  |
| c10m03 | **Radar giờ là của ta** Trạm radar cũ của Orlov trên cao điểm giờ canh bầu trời cho ta, còn nhà thờ trong làng là trạm cứu thương. Wolff muốn xóa sổ cả hai. Giữ ít nhất một công trình đứng vững bảy p… | Frostpeak | Bảo vệ | quaden | 555 xu |  |
| c10m04 | **Đốt máy bay** Một trận đột kích đêm vào sân đỗ phía tây Skyhold: máy bay cường kích của Wolff đang đỗ thành hàng. Đốt chúng ngay tại chỗ. | Skyhold | Phá hủy | quaden | 555 xu |  |
| c10m05 | **Icarus Mk.0** Nhà chứa bị hàn cửa đã mở lúc bình minh. Icarus đang ở trên không phận Skyhold: phi thuyền quỹ đạo của Aurel, vỏ bạc, cánh ngắn, với động cơ chính đủ sức bỏ xa bất cứ thứ gì ta có. Ve… | Skyhold | Tiêu diệt boss Icarus Mk.0 · Phi thuyền nguyên mẫu | aurel | 840 xu |  |
| c10m06 | **Màn tên lửa** Wolff giấu các dàn tên lửa phòng không tầm xa trong sương để che chắn căn cứ. Nadia đã đánh dấu ba bệ phóng. Săn chúng để Hawk được bay. | Frostpeak | Săn mục tiêu | quaden | 565 xu |  |
| c10m13 | **Các con đèo lúc bình minh** Roc săn trên các con đèo trong đêm. Ban ngày thì ta chiếm được chúng: trạm tín hiệu, hồ băng và xưởng cưa, từ phía bắc, trước khi phi đội của Raven cất cánh. | Whiteout Pass | Chiếm cứ điểm | quaden | 565 xu |  |
| c10m08 | **Roc trên Whiteout** Sở chỉ huy bay của Wolff, Roc, lượn vòng trên cao quanh Whiteout Pass, gọi hỏa lực vào các đoàn xe của ta tới Skyhold. Đánh nó bằng mọi thứ với tới được bầu trời cho tới khi nó… | Whiteout Pass | Tiêu diệt boss Roc · Khí cầu chỉ huy | quaden | 855 xu |  |
| c10m14 | **Giờ tiếp nhiên liệu** Nadia có lịch trình của Raven: mỗi chiều có một giờ phi đội của hắn nằm dưới đất tiếp nhiên liệu. Trong giờ đó, chiếm cả hai sân đỗ và đường băng từ phía bên kia. | Skyhold | Chiếm cứ điểm | quaden | 575 xu |  |
| c10m07 | **Không kích** Wolff đáp trả bằng tất cả những gì hắn có: từng đợt, từng đợt máy bay lao vào trận địa của ta quanh Skyhold. Bắn rơi mười sáu chiếc. | Skyhold | Bắn hạ máy bay | quaden | 575 xu |  |
| c10m12 | **Hawk và Raven** Raven gửi lời qua tháp điều khiển Skyhold: hắn và Hawk, trên đường băng, giữa trưa. Hawk đã nhận lời. Giữ phần còn lại của phi đội Raven tránh xa anh và hạ Harpy. | Skyhold | Tiêu diệt boss Harpy · Trực thăng khổng lồ | quaden | 870 xu |  |
| c10m09 | **Tổ Wolff** Sở chỉ huy riêng của Wolff, ở đầu đông căn cứ, vây kín tên lửa. San phẳng nó; căn cứ không quân sẽ còn kháng cự, nhưng đã mất đầu. | Skyhold | Đấu tướng | quaden | 585 xu |  |
| c10m10 | **Tấn công Skyhold** chiến dịch lớn Chính căn cứ không quân. Làm mù radar, chọn đòn thứ hai, bắn rơi Roc của Wolff, quét sạch đợt máy bay cuối cùng của hắn, rồi giữ căn cứ trước đợt phản kích cuối củ… | Skyhold | Phá hủy | quaden | 1410 xu |  |
| c10s1 | **Phụ tùng** phụ Hai xe tải đang chở phụ tùng của Icarus rời căn cứ trong sương. Venn muốn chặn chúng trước khi chúng tới sa mạc. Chúng đã được đánh dấu. | Skyhold | Săn mục tiêu |  | 1620 xu |  |
| c10s2 | **Argus** phụ Argus, khí cầu trinh sát bọc giáp của Raven, đang chỉ điểm cho pháo Hegemon trên các điểm cao Frostpeak. Nadia muốn kiểm tra ba điểm nó đang theo dõi, và bắn hạ khí cầu nếu nó tới gần. | Frostpeak | Trinh sát Argus · Khí cầu trinh sát |  | 1620 xu |  |

### Chương 11: Skygate

| # | Nhiệm vụ | Bản đồ | Mục tiêu | Tướng | Thưởng | Mở khóa |
|---|---|---|---|---|---|---|
| c11m01 | **Bãi ray của cửa ngõ** Skygate Array của Aurel được tiếp tế qua bãi ray. Chiếm các ngả giao cắt trong đêm, từ phía bên kia. | Rust Yard | Chiếm cứ điểm | aurel | 590 xu | Siêu tăng |
| c11m02 | **Mắt nhìn cửa ngõ** Nadia muốn tận mắt thấy các trạm radar của cửa ngõ trước khi ta đánh. Đưa xe tới từng trạm, trong mưa. | Skyhold | Trinh sát | aurel | 595 xu |  |
| c11m03 | **Làm mù cửa ngõ** Phá các chảo radar dẫn đường cho tàu của Aurel từ quỹ đạo xuống. | Frostpeak | Phá hủy | aurel | 595 xu | Trạm tiếp tế CP |
| c11m04 | **Bệ phóng phụ** Aurel giấu các bệ phóng phụ quanh cửa ngõ. Tìm ra chúng trước khi hắn nạp nhiên liệu. | Skygate Array | Trinh sát | aurel | 600 xu · HQ 5 | Tháp pháo hạng nặng |
| c11m05 | **Monster** Orlov đang chờ ở đầu mối đường sắt của Skygate Array trong Rust Yard cùng Monster, một pháo đài biết đi dựng quanh khẩu pháo lớn nhất ông ta từng có. Đây là trận cuối của ông ta. Bắt khẩu… | Rust Yard | Tiêu diệt boss Monster · Pháo tự hành 800 mm | orlov | 905 xu |  |
| c11m06 | **Giữ sườn núi** Aurel muốn lấy lại sườn núi phía trên cửa ngõ. Giữ nó cho tới khi pháo vào vị trí. | Frostpeak | Giữ cứ điểm | aurel | 605 xu |  |
| c11m07 | **Locust trên cửa ngõ** Một tàu mang drone Locust che chắn bệ phóng phía tây. Đốt các bồn nhiên liệu của tên lửa và bắn hạ tàu mang drone. | Skygate Array | Phá hủy Locust · Tàu con drone | aurel | 610 xu |  |
| c11m11 | **Đoàn xe công binh** Công binh của Mara cần tới xác bệ phóng phía tây của Skygate trước khi người của Aurel dọn sạch. Đưa họ qua Rust Yard trong sương. | Rust Yard | Hộ tống | aurel | 615 xu |  |
| c11m08 | **Nhiên liệu cho Hawk** Nhiên liệu máy bay cho phi đội của Hawk, theo đường bộ qua đèo trong đêm, tới đường băng dã chiến ở trại gỗ. Năm xe bồn phải tới được ba. | Frostpeak | Hộ tống |  | 615 xu |  |
| c11m09 | **Người gác cổng** Viên chỉ huy cửa ngõ của Aurel cố thủ ở phía bên kia đèo. San phẳng sở chỉ huy. | Frostpeak | Đấu tướng | aurel | 620 xu |  |
| c11m12 | **Làm mù Skygate** Radar của Skygate Array chạy bằng các bồn nhiên liệu dưới chân cột ăng-ten. Đốt chúng đi và Hegemon sẽ đánh trận cuối trong cảnh nửa mù, từ bãi phóng Helion tới sa mạc muối. | Skygate Array | Phá hủy Locust · Tàu con drone | aurel | 620 xu |  |
| c11m13 | **Đường tắt** Đường công vụ chạy thẳng tới các bệ phóng. Đi thật nhanh, xem từng bệ phóng rồi rút trước khi Skygate quay pháo lại. Không có thời gian cho việc gì khác. | Skygate Array | Trinh sát | aurel | 930 xu |  |
| c11m10 | **Skygate Array** chiến dịch lớn Chiến dịch giành cửa ngõ: làm mù radar, chọn mục tiêu, phá tuyến phòng thủ, rồi hạ Daedalus khi nó đổ quân của Aurel từ quỹ đạo xuống. Giai đoạn: Làm mù radar trên đồ… | Skygate Array | Phá hủy | aurel | 1495 xu |  |
| c11s1 | **Xe nhiên liệu** phụ Các xe nhiên liệu của Aurel đang chạy tới bệ phóng trong đêm. Săn những chiếc đã đánh dấu. | Skyhold | Săn mục tiêu | aurel | 1720 xu |  |

### Chương 12: Helion

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
| c12m10 | **Icarus rơi** chiến dịch lớn Trận cuối cùng. Chiếm khu nhiên liệu, chọn đòn đánh, chiếm nhà lắp ráp, đập tan chiếc Behemoth cuối cùng của Varga, giữ bệ phóng, và khi Icarus rời bệ phóng lên quỹ đạo… | Helion Launch Complex | Chiếm cứ điểm | aurel | 1575 xu |  |

### Kể chuyện

- Briefing dạng thẻ có chân dung người giao nhiệm vụ.
- Thoại trong trận: dải chân dung nhỏ và tối đa 2 dòng trên khay thẻ, theo kịch bản từng màn và hàng đợi ưu tiên P0–P4 (phần 2c).
- Camera lia trong trận khi boss, chi viện hoặc tướng địch xuất hiện; không có cutscene.
- Màn chuyển chương có tóm tắt 3–4 câu; sau chương 9 là **Kết mạch Thorne** (đoạn chuyển, trước chương 15); phần kết thật của game sau c12m10, và thắng c12m10 mở cấp Huyền thoại của chế độ Tác chiến.
- Mục Hồ sơ trong menu: tiểu sử nhân vật, hồ sơ boss, dòng thời gian, các mẩu truyện mỗi nhiệm vụ trao.

### Phần thưởng và kinh tế chiến dịch

Mỗi chương mở 5–7 thẻ (xe, tháp, thẻ hỗ trợ), một cấp sở chỉ huy ở các chương 1/3/5/7/9 và một mô-đun tiện ích (chương 1–5; các chương sau trao một món đồ tháp). Mỗi nhiệm vụ trả bản thiết kế, xu và một mẩu truyện; nhiệm vụ phụ trả bản thiết kế hiếm hoặc đồ tháp. Boss bay chỉ xuất hiện khi người chơi đã có ít nhất hai thẻ phòng không mặt đất. Người chơi chỉ đánh chiến dịch đưa bộ bài chính (8 thẻ + 6 tháp) lên hạng 7,0 khi bắt đầu hồi III và 8,1 ở cuối chiến dịch.

Sheet 05_chien_dich/Chuong — Chương (15 dòng, 14 cột)

| id | maps | main | minis | general | tep_thoai_chuong | tep_thoai | so_cau_thoai | act | comic |
|---|---|---|---|---|---|---|---|---|---|
| 1 | landingbeach;greenvale;ashfield | fortress_bastion | bastion_mk0 | brandt | 1 | ch01.json | 82 | 1 | comic.1 |
| 2 | dunebreak;redrock | behemoth | behemoth_inferno | varga | 2 | ch02.json | 108 | 1 | comic.2 |
| 3 | whiteout;frostpeak | mobile_fortress | mega_gunship;fenrir | orlov | 3 | ch03.json | 111 | 1 | comic.3 |
| 4 | rustyard;ironport;lighthousebay | leviathan | behemoth_tempest;armored_train;scylla | kessler | 4 | ch04.json | 164 | 2 | comic.4 |
| 5 | junglepass;emberridge | drone_mothership | locust | sen | 5 | ch05.json | 121 | 2 | comic.5 |
| 6 | ashfield;whiteout;greenvale;landingbeach;hydrodam | moloch | landing_hovercraft;behemoth_mk2 | varga | 6 | ch06.json | 153 | 2 | comic.6 |
| 7 | metrocity;veyra_old_quarter;capital | nuke_train | behemoth_mk2;behemoth_inferno;armored_train | hung | 7 | ch07.json | 149 | 3 | comic.7 |
| 8 | redrock;openpit;hydrodam;dunebreak | moloch | ixion;earth_borer | hung | 8 | ch08.json | 129 | 3 | comic.8 |
| 9 | ironport;landingbeach;lighthousebay;coralisles | typhon | landing_hovercraft;scylla | hung | 9 | ch09.json | 131 | 3 | comic.9 |
| 10 | frostpeak;skyhold;whiteout | command_airship | icarus_mk0;argus;mega_gunship | quaden | 10 | ch10.json | 134 | 4 | comic.10 |
| 11 | rustyard;skyhold;frostpeak;orbitalgate | daedalus | monster;locust | aurel | 11 | ch11.json | 120 | 4 | comic.11 |
| 12 | launchsite;saltflat;dunebreak;lighthousebay | silver_bug | behemoth_mk2;scylla;locust | aurel | 12 | ch12.json | 93 | 4 | comic.12 |
| 13 | foundry |  | behemoth_mk0 | varga | 13 | ch13.json | 35 | 1 | comic.13 |
| 14 | swamp;borderbridge |  | locust |  | 14 | ch14.json | 44 | 2 | comic.14 |
| 15 | frostpeak;junglepass |  | mega_gunship | quaden | 15 | ch15.json | 40 | 3 | comic.15 |

*In 10 / 14 cột; 2 cột khác: xem sheet.*

Sheet 04_che_do_kinh_te_ai/Sao_chien_dich — Sao chiến dịch theo mục tiêu (15 dòng, 7 cột)

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

Sheet 05_chien_dich/Phat_hanh — Phát hành (3 dòng, 8 cột)

| id | khoa | gia_tri_chu |
|---|---|---|
| acts | acts | 1;2;3;4 |
| chaptersOff | chaptersOff |  |
| switchedOff | switchedOff | comingSoon |

Bảng đầy đủ: xem sheet `Nhiem_vu` (193 dòng), `Nhan_vat` (21 dòng), `Thoai` (1614 dòng, bulk.zip), `Trigger_thoai` (27 dòng).

## Bộ bài game

### Màn bộ bài game

23 màn dùng bộ bài do game định sẵn (8 thẻ xe + 2 thẻ hỗ trợ, không sửa được, hạng thẻ theo đường cong hạng của chương, không trang bị). Thẻ chưa mở khóa là thẻ **mượn** ("Mượn trong nhiệm vụ này"): dùng được trong màn, không mở khóa vĩnh viễn, tối đa 2 thẻ một màn (c1m01: 4, vì người chơi mới chỉ có 4 thẻ xe); các thẻ khóa khác của bảng được thay bằng thẻ đã mở cùng vai trò. Đồng minh đặt sẵn không chiếm ô thẻ, do AI đồng minh điều khiển theo lệnh Tấn công/Phòng thủ chung. Mục tiêu gốc của mọi màn giữ nguyên.

Bảng 23 dòng: số liệu đầy đủ ở các sheet của mục này trong file xlsx cùng tên.

Sheet 05_chien_dich/Bo_bai_game_dong_minh — Bộ bài game: đồng minh đặt sẵn (3 dòng, 13 cột)

| id | bo_bai_game_id | thu_tu | def | convoy | fallback | heading_deg | loss_if_destroyed | name | x_m |
|---|---|---|---|---|---|---|---|---|---|
| c6m03/0 | c6m03 | 0 | behemoth | TRUE |  | 225 | TRUE | behemoth_mara | 100 |
| c10m12/0 | c10m12 | 0 | fighter_jet |  |  | 225 | TRUE | hawk_jet | 92 |
| c12m03/0 | c12m03 | 0 | mara_behemoth |  | behemoth | 225 |  | behemoth_mara_repainted | 96 |

*In 10 / 13 cột; 1 cột khác: xem sheet.*

Bảng đầy đủ: xem sheet `Bo_bai_game` (23 dòng).

## Biến cố và sự kiện trong nhiệm vụ

### Biến cố

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

### Sự kiện trong nhiệm vụ và thoại trong trận

Mỗi nhiệm vụ ghép từ thư viện sự kiện dạng dữ liệu (67 sự kiện, 27 loại); cả chiến dịch có 550 sự kiện. Sự kiện kích hoạt theo thời gian, tiến độ nhiệm vụ, máu boss, số quân trên sân hoặc sau một sự kiện khác; chạy theo seed và vào chuỗi lệnh của trận nên replay và checkpoint khôi phục đúng. Mọi sự kiện lớn được báo trước bằng thông báo ở mép trên, một câu thoại và mũi tên hướng trên bản đồ nhỏ; quân địch không bao giờ xuất hiện trong vòng 45 m quanh quân người chơi. Viện quân có trần riêng ngoài trần quân thường: 16 xe địch, 10 xe Accord. Tướng địch rút lui khi còn 30% máu, trừ ở trận cuối của mình; từ chương 4 tướng ra trận bằng mini boss thay vì xe tinh nhuệ. Các con số là điểm khởi đầu, chờ đợt mô phỏng 5 seed.

### Viện quân theo tướng

| Tướng | Thành phần | Cách tới | Xe tinh nhuệ | Chương cuối |
|---|---|---|---|---|
| Thiếu tá Brandt | Bánh lốp, Xe bộ binh, Tăng chủ lực, Pháo xung kích, Tăng nhẹ | edge | Tăng chủ lực | 1 |
| Tướng Viktor Varga | Tăng nhẹ, Tăng chủ lực, Tăng nặng, Chống tăng, Hai nòng | edge | Tăng nặng | 12 |
| Đại tá Ilya Orlov | Phản lực, Lựu pháo, Xe cối, Phản lực nặng, Cao xạ | edge | Phản lực | 11 |
| Đô đốc Magnus Kessler | Xe bộ binh, Pháo xung kích, Tăng chủ lực, Rải mìn, PK tầm trung | sea, rail, landing, edge | Tăng chủ lực | 12 |
| Tiến sĩ Elara Venn | UAV tấn công, Drone FPV, UAV trinh sát, Gây nhiễu | edge, air | Drone FPV | 5 |
| Kasimir Wolff | TT tấn công, Cường kích, UAV tấn công | edge | Cường kích | 10 |
| Tướng Roland Thorne | Tăng chủ lực, Tăng nặng, Xe bộ binh, Cao xạ | edge, landing | Tăng nặng | 9 |
| Giám đốc Lucien Aurel | UAV tấn công, Drone FPV, Tăng nặng, Xe bộ binh, Pháo điện từ | pods, air, edge | Tăng nặng | 12 |

### Thoại trong trận

Mọi lời nhân vật trong trận là một dòng chữ kiểu phụ đề ngay trên khay thẻ: tên người nói in đậm, màu theo phe (ta xanh nhạt, địch đỏ đậm), rồi câu thoại; nền chỉ là một dải tối mờ, rộng tối đa nửa màn hình, tối đa 2 dòng, mở đầu bằng chân dung nhỏ của người nói (thiếu chân dung thì ô tạm theo phe với chữ cái đầu; DialogueViews), không lồng tiếng. Một câu một lúc, theo mức ưu tiên: cốt truyện, cảnh báo, sự kiện, phản ứng. Câu cốt truyện và cảnh báo xếp hàng (cảnh báo quá 12 s thì bỏ); câu sự kiện và phản ứng hiện ngay hoặc bỏ, cách nhau tối thiểu 9 s (20 s cho câu phản ứng khi có boss trên sân). Mỗi câu hiện 3–6 s theo độ dài, mờ dần 0,25 s, không bao giờ dừng trận. Cài đặt: Đầy đủ / Chỉ quan trọng / Tắt (câu cốt truyện luôn hiện). Sáu khoảnh khắc cốt truyện làm trận chậm 0,5 lần trong khi 2–3 câu liên tiếp chạy: Hollow Dam, Venn mất bầy drone, Thorne phản bội, Thorne trên Typhon, Varga ngã xuống, Icarus rơi.

Bảng đầy đủ: xem sheet `Bien_co` (67 dòng), `Bien_co_luat` (40 dòng), `Nhiem_vu_bien_co` (494 dòng).

## Nhiệm vụ nhiều giai đoạn

Chiến dịch lớn chạy nhiều giai đoạn trong cùng một trận. Mỗi giai đoạn là một nhiệm vụ riêng (mục tiêu, điều kiện thắng, quân, boss) đặt trên dữ liệu của nhiệm vụ mẹ. Xong một giai đoạn thì trả thưởng CP, chạy sự kiện cuối giai đoạn, lưu điểm lưu và sang giai đoạn tiếp theo hoặc một lựa chọn. Thua một giai đoạn là thua nhiệm vụ.

- **Sự kiện** ở đầu, cuối hoặc sau một số giây: chi viện địch, chi viện ta, mở rộng vùng chơi, đồng minh phản bội, radio, thưởng CP, không kích, thu nhập.
- **Lựa chọn nhánh:** mỗi chiến dịch lớn có ít nhất một giai đoạn chọn giữa hai mục tiêu có hệ quả khác nhau (ví dụ phá kho đạn: thu nhập địch ×0,7; hoặc chiếm đài radio: không kích miễn phí mỗi 50–55 giây). Trận vẫn chạy trong lúc chọn; sau 15 giây tự lấy phương án đầu.
- **Điểm lưu bằng phát lại:** mô phỏng xác định, nên thay vì chụp toàn bộ trạng thái, game ghi lệnh của người chơi (kèm bước mô phỏng) và các công tắc (thế trận, tự mua, yểm trợ, cứ điểm ưu tiên, nhánh đã chọn). Bài kiểm tra xác nhận trận khôi phục và trận chơi liền mạch giống hệt, kể cả qua một lựa chọn và một lần phản bội.
- **Chỉ huy đồng minh:** căn cứ riêng (sở chỉ huy, tháp) và quân riêng, do AI chiến thuật riêng điều khiển, cùng mục tiêu với người chơi, thả quân ở bãi riêng. Xe đồng minh không tính vào quân số, tiếp tế và giới hạn của người chơi. Sự kiện phản bội chuyển toàn bộ xe và công trình của đồng minh sang phe địch ngay trong trận (chương 8).
- **Vùng chơi mở rộng:** chiến dịch lớn bắt đầu trên một phần bản đồ; phe người chơi không đi ra ngoài biên (đường đứt nét vàng), camera cũng dừng ở biên và mở theo khi vùng chơi mở rộng. Lưới dẫn đường và làn giao thông đã phủ toàn bản đồ.
- **Địch đông:** trần xe địch 48 ở Công thành, Phòng thủ, Vô tận và chiến dịch lớn (32 ở chế độ thường); quân đông là bầy xe rẻ. Tìm đường tối đa 6 lượt mỗi bước mô phỏng (còn lại xếp hàng), hai chỉ huy AI nghĩ ở các bước khác nhau. Đo trên máy bàn quy đổi ×6 cho điện thoại yếu: 48 xe địch có thời gian bước trung bình 4,4 ms, p99 15,3 ms (ngân sách 8/16 ms).
- **Boss nhiều pha:** thanh máu có vạch pha; tới vạch boss dừng lại, biến hình vài giây (không nhận sát thương, camera lia tới, tướng lên radio) rồi đánh tiếp mạnh hơn (sát thương, tốc độ, giáp, kỹ năng, mô hình mới).

### Các chiến dịch lớn cuối chương

| # | Chiến dịch | Giai đoạn | Sự kiện | Lựa chọn | Đồng minh |
|---|---|---|---|---|---|
| c1m10 | **Pháo đài Ashfield** | Đốt kho nhiên liệu → Cho nổ kho đạn → Phá trạm radar → Bastion → Quân đồn trú phản kích → San phẳng sở chỉ huy | chi viện địch, không kích, radio, thu nhập | Cho nổ kho đạn / Phá trạm radar |  |
| c2m11 | **Behemoth ở Red Rock** | Giếng dầu → Phá các giàn bơm → Pháo của Thorne → Chiếm ốc đảo → Giữ ốc đảo → Behemoth | chi viện địch, không kích, radio, thu nhập | Phá các giàn bơm / Gọi pháo của Thorne | có |
| c3m10 | **Tuyến Frostpeak** | Làm mù radar trên đồi → Cho nổ kho nhiên liệu → Radar của pháo đài → Jötunn → Giữ cổng | chi viện địch, không kích, radio, thu nhập | Cho nổ kho nhiên liệu / Phá radar của pháo đài |  |
| c4m11 | **Leviathan** | Ngọn hải đăng → Trận địa pháo cũ → Yểm trợ trên không → Làng chài → Leviathan | chi viện địch, không kích, radio | Chiếm trận địa pháo bờ biển / Gọi không quân |  |
| c5m10 | **Matriarch** | Các đường đắp → Đốt nhiên liệu drone → Giữ trạm tiếp sóng → Giữ nhà máy địa nhiệt → Bầy drone → Matriarch | chi viện địch, không kích, radio, thu nhập | Đốt nhiên liệu drone / Giữ trạm tiếp sóng (120 giây) |  |
| c6m10 | **Bảo vệ con đập** | Giữ mặt đập → Đốt kho của Varga → Giữ trạm phát điện → Moloch → Chờ cứu viện | chi viện ta, chi viện địch, không kích, radio, thu nhập | Đốt kho của Varga ở bến lội / Giữ trạm phát điện (150 giây) | có |
| c7m10 | **Giải phóng Veyra** | Các đầu cầu → Đốt Bộ Hậu cần → Giữ khu vườn → Đánh chiếm cung điện → Giữ quảng trường → Phản bội → Phản đòn → Nemesis | chi viện địch, không kích, radio, thu nhập, đồng minh phản bội | Đốt Bộ Hậu cần / Giữ khu vườn (150 giây) | có |
| c8m10 | **Hố sâu nhất** | Nhà máy nghiền và bãi xuất quặng → Đốt kho nhiên liệu → Giữ nhà máy nghiền → Phá các si-lô quặng → Cho nổ xưởng chế biến → Giữ đáy hố → Moloch và Tartarus → Thorne phản kích | chi viện địch, không kích, radio, thu nhập | Đốt kho nhiên liệu / Giữ đài phát ở nhà máy nghiền |  |
| c9m10 | **Typhon trồi lên** | Bãi đường sắt → Đốt các toa nhiên liệu → Giữ trạm tín hiệu → Khu nhà máy và bến tàu → Giữ khu nhà máy → Typhon → Giữ cầu tàu | chi viện địch, không kích, radio, thu nhập | Đốt các toa nhiên liệu / Giữ trạm tín hiệu (150 giây) |  |
| c10m10 | **Tấn công Skyhold** | Làm mù radar → Đốt bãi nhiên liệu → Tháp điều khiển → Roc → Đợt cuối của Wolff → Giữ Skyhold | chi viện địch, không kích, radio, thu nhập | Đốt bãi nhiên liệu / Phá tháp điều khiển và vòm radar |  |
| c11m10 | **Skygate Array** | Làm mù radar trên đồi → Cho nổ kho nhiên liệu → Radar của pháo đài → Daedalus → Giữ cổng | chi viện địch, không kích, radio, thu nhập | Cho nổ kho nhiên liệu / Phá radar của pháo đài |  |
| c12m10 | **Icarus rơi** | Khu nhiên liệu đẩy → Đốt nhiên liệu đẩy → Làm mù radar phía tây → Nhà lắp ráp → Trận cuối của Varga → Đếm ngược → Giữ bệ phóng → Icarus | chi viện địch, không kích, radio, thu nhập | Đốt các bồn nhiên liệu đẩy / Phá radar phía tây |  |

Bảng đầy đủ: xem sheet `Nhiem_vu_giai_doan` (90 dòng), `Nhiem_vu_giai_doan_su_kien` (145 dòng), `Nhiem_vu_giai_doan_lua_chon` (28 dòng), `Nhiem_vu_dong_minh` (42 dòng).

## Tham khảo ngoài đời và game

Thông số ngoài đời lấy từ nguồn trong repo (sheet Nguon_tham_chieu của 08_tham_chieu); chỗ chưa có nguồn ghi NEED_SOURCE, không điền từ trí nhớ.

### Chien_dich_tham_chieu

231 dòng. Độ tin cậy: da_kiem_chung 0, uoc_dinh 0, ban_dau_doan 0, NEED_SOURCE 231. Loại: NEED_SOURCE 231.

- Chưa dòng nào có tham chiếu trong repo.

### Thoai_tham_chieu

21 dòng. Độ tin cậy: da_kiem_chung 0, uoc_dinh 0, ban_dau_doan 0, NEED_SOURCE 21. Loại: NEED_SOURCE 21.

- Chưa dòng nào có tham chiếu trong repo.

## Các sheet của file

Mọi sheet, số dòng và ý nghĩa cột nằm trong 00_index.xlsx (Muc_luc_sheet, Schema). Sheet `input_<tên>` là bản chép của một sheet nguồn để công thức Excel đọc cùng file; sửa ở sheet nguồn, không sửa bản chép.

- `Chuong` (15 dòng): Chương — campaign.json chapters: 15 chương (hồi, bản đồ, tướng, boss chủ lực / mini, truyện tranh)
- `Nhiem_vu` (193 dòng): Nhiệm vụ — campaign.json missions: 193 nhiệm vụ (chương, mục tiêu, bản đồ, giờ, boss, thời tiết, bộ bài địch, sao, biến cố); người nói chính từ script/chNN.json…
- `Nhiem_vu_quan` (332 dòng): Nhiệm vụ: quân đặt sẵn — missions[].units: quân đặt sẵn (đội, vị trí, hướng)
- `Nhiem_vu_radio` [bulk.zip] (353 dòng): Nhiệm vụ: radio — missions[].radio: khóa câu radio, lúc phát
- `Nhiem_vu_san` (80 dòng): Nhiệm vụ: mục tiêu săn — missions[].hunt: đơn vị phải săn và tuyến
- `Nhiem_vu_goi_y` (8 dòng): Nhiệm vụ: gợi ý — missions[].tips: khóa gợi ý, lúc hiện
- `Nhiem_vu_dong_minh` (42 dòng): Nhiệm vụ: quân đồng minh — missions[].ally.units
- `Nhiem_vu_dong_minh_cong_trinh` (25 dòng): Nhiệm vụ: công trình đồng minh — missions[].ally.structures
- `Nhiem_vu_dong_minh_tiep_vien` (8 dòng): Nhiệm vụ: tiếp viện đồng minh — missions[].ally.reinforcements
- `Nhiem_vu_bien_co` (494 dòng): Nhiệm vụ: biến cố — missions[].missionEvents: id biến cố (thư viện) hoặc bản ghi ghi đè
- `Nhiem_vu_giai_doan` (90 dòng): Nhiệm vụ: giai đoạn — missions[].stages: mục tiêu, CP, lựa chọn, sóng địch, biến cố mỗi giai đoạn
- `Nhiem_vu_giai_doan_su_kien` (145 dòng): Giai đoạn: sự kiện — stages[].events: radio, quân, hỗ trợ
- `Nhiem_vu_giai_doan_lua_chon` (28 dòng): Giai đoạn: lựa chọn — stages[].choices: khóa và giai đoạn kế
- `Nhiem_vu_giai_doan_bien_co` (56 dòng): Giai đoạn: biến cố — stages[].missionEvents
- `Nhiem_vu_nav_state` (13 dòng): Nhiệm vụ: trạng thái nav dựng sẵn — missions[].navStates: vùng đổi trạng thái (thủy triều, cầu)
- `Nhiem_vu_nav_state_trang_thai` (34 dòng): Trạng thái nav: các trạng thái — navStates[].states
- `Nhiem_vu_nav_chan` (25 dòng): Trạng thái nav: khối chặn — navStates[].states[].blocks: hình chữ nhật chặn
- `Bo_bai_game` (23 dòng): Bộ bài game — missions[].fixedDeck: 23 màn bộ bài cố định (8 xe, 2 hỗ trợ, đồng minh đặt sẵn, thẻ mượn, luật riêng, trạng thái)
- `Bo_bai_game_dong_minh` (3 dòng): Bộ bài game: đồng minh đặt sẵn — fixedDeck.placedAllies
- `Thoai` [bulk.zip] (1614 dòng): Thoại — script/chNN.json lines: mọi câu thoại một dòng (nhiệm vụ, thứ tự, trigger, điều kiện, người nói, ưu tiên, một lần / lặp, văn bản Việt / Anh, số ký tự)
- `Nhan_vat` (21 dòng): Nhân vật — script/speakers.json: tên, vai (roles), trigger được phép, ghi chú
- `Trigger_thoai` (27 dòng): Trigger thoại — speakers.json mainTriggers / scriptedTriggers và mọi trigger câu thoại dùng; ưu tiên, hồi chiêu, số lần: luật trong mã (Dialogue.cs)
- `Bien_co` (67 dòng): Biến cố — campaign.json eventLibrary.events: cơ chế (kind), báo trước, câu radio, thông báo, tham số, trigger, thưởng
- `Bien_co_luat` (40 dòng): Biến cố: luật chung — eventLibrary.rules (trừ difficulty: 04_che_do_kinh_te_ai/Do_kho; weatherSight: 06_ban_do/Thoi_tiet)
- `Phat_hanh` (3 dòng): Phát hành — release.json: hồi phát hành, chương tắt, cách hiện chương tắt
- `Kich_ban_goc` [bulk.zip] (1854 dòng): Kịch bản gốc — Tools/story/script/chNN.txt: mọi dòng không trống (công cụ dựng ra script/chNN.json); dòng '#' là ghi chú, '@' mở nhiệm vụ, còn lại 'trigger / người…
- `Ket_tran` (5 dòng): Kết trận — Màn kết trận: thời lượng và chuyển động chậm theo loại (thắng lớn đầu tiên, thắng đầu, chơi lại, thua), thời gian cho phép bỏ qua
- `Cutscene_khoanh_khac` (5 dòng): Khoảnh khắc chậm — Khoảnh khắc điện ảnh: bật mặc định, thời lượng tối đa, vào ra mờ, tỷ lệ
- `Thoai_moc_thoi_gian` (359 dòng): Thoại: mốc thời gian — Câu có thời điểm biết trước của mỗi nhiệm vụ (mission_start = 0 s, trigger time = at), theo thời gian; khoảng = mốc này - mốc trước (mốc đầu: từ 0 s)
- `Thoai_thong_ke` (193 dòng): Thoại: thống kê theo nhiệm vụ — Mỗi nhiệm vụ: số câu so với ngân sách theo kiểu nhiệm vụ (Tools/story/script_build.py L1: ngắn / phụ 4-8, thường 6-10, boss / chiến dịch lớn 10-16),…
- `Thoai_thong_ke_nhom` [bulk.zip] (2542 dòng): Thoại: số câu theo nhóm — Mỗi nhiệm vụ x (người nói / trigger / ưu tiên) x giá trị có mặt: số câu (COUNTIFS trên Thoai)
- `Nhiem_vu_thong_ke` (193 dòng): Nhiệm vụ: thống kê thoại — Mỗi nhiệm vụ: số câu có văn bản tiếng Việt / tiếng Anh, số câu theo ưu tiên P0-P4 (COUNTIFS trên Thoai)
- `Chien_dich_tham_chieu` (231 dòng): Chiến dịch: tham chiếu lịch sử / phim / game — Mỗi chương, nhiệm vụ, màn bộ bài game một dòng: tham chiếu lịch sử hoặc phim / game, mã màn (spec 12.2; chỉ dữ liệu có trong repo)
- `Thoai_tham_chieu` (21 dòng): Thoại: nhân vật và giọng lấy ý — Mỗi nhân vật một dòng: nhân vật / giọng lấy ý (chỉ mức ý tưởng) (spec 12.2; chỉ dữ liệu có trong repo)
- `Hang_so_chien_dich` (15 dòng): Hằng số chiến dịch, biến cố, thoại — Assets/MachineBrigade/Resources/Data/tunables.json: 'campaign' (lớp chủ → tên): một dòng một hằng số; mã game đọc qua SimTunables, giữ nguyên giá trị…
