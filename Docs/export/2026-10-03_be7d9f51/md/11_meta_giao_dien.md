# 11_meta_giao_dien — Meta và giao diện

Bộ xuất dữ liệu Machine Brigade, commit be7d9f51, ngày 2026-10-03. Sinh bởi `python Tools/export/export.py` (lượt 6): bảng in đúng ô của csv / xlsx; văn bản lấy từ tài liệu thiết kế (Tools/docs) và chuỗi trong game. Toàn văn: Machine_Brigade_Design_FULL_2026-10-03.md.

Nâng hạng, hòm đồ và tỷ lệ rơi, cửa hàng, nhiệm vụ ngày, skin, mở khóa, thẻ khởi đầu, danh sách bản đồ menu, ảnh bản đồ căn cứ, sổ tay đạn, mọi bảng hằng C# của meta; thành tựu / telemetry / hướng dẫn (không có hoặc chờ)

Mục trong file này: 18. Giao diện.

## 18. Giao diện

Trạng thái: Một phần — chờ prompt 24; chờ prompt xuat_luot5; không có trong mã và dữ liệu (sheet Cai_dat_mac_dinh, Huong_dan, Thanh_tuu, Telemetry)

Nguồn dữ liệu: 11_meta_giao_dien/Cai_dat_mac_dinh; 11_meta_giao_dien/Huong_dan; 11_meta_giao_dien/Ban_do_menu; 11_meta_giao_dien/Skin; 11_meta_giao_dien/Mo_khoa; 11_meta_giao_dien/Nhiem_vu_ngay; 11_meta_giao_dien/Thanh_tuu; 11_meta_giao_dien/Telemetry. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §18. Giao diện.

Phong cách **Field Command 2.0** (phase 10): nền xám thép phẳng, viền 1 px, góc vuông, một màu nhấn cam cho hành động chính (góc vát), chữ Barlow / Barlow Condensed (đủ dấu tiếng Việt). Mọi màn dựng trên một bộ token màu và chữ chung và một thư viện thành phần (nút, thẻ, tab, ô chọn, công tắc, thanh chỉ số, hộp thoại, thông báo). Điều hướng 5 mục bên trái: Trang chủ, Chiến dịch, Tác chiến, Quân đội, Cửa hàng; thanh trên cùng có cấp, kinh nghiệm, xu và cài đặt. Ảnh thẻ render từ mô hình 3D thật. Mỗi màn được kiểm tra tự động ở 4 tỉ lệ màn hình (16:9, 19,5:9 tai thỏ, 20:9 đục lỗ, 4:3) và cỡ chữ Lớn: không chữ bị cắt, không thành phần chồng nhau, vùng chạm đủ lớn. Tên gọi tiếng Việt thống nhất (mỗi bản đồ một tên, xu, ngụy trang, rốc-két, la-de).

**Prompt 11:** HUD gọn trong trận (mặc định bật, tắt được trong Cài đặt): khi giao tranh HUD chỉ chiếm 26-28 % màn hình 16:9 và 21-23 % ở 20:9 (HUD đầy đủ 51-64 %). Mọi xe, tháp, công trình, thẻ hỗ trợ và vật phẩm có tên ngắn (tối đa khoảng 14 ký tự) dùng ở chỗ chật; mọi thẻ có vùng tên cao cố định 2 dòng nên ảnh, CP và cấp luôn thẳng hàng. Khiên vẽ lại bằng một shader.

**Prompt 14:** ngoài trận mọi cỡ tính theo point của máy (thanh trên 44 pt, thanh bên 72 pt với icon 23 pt, tab 40 pt, nút 44 pt, nút chính 53 pt, chữ 19 / 18 / 14 / 13 / 11 pt, cỡ Lớn gấp 1,2), thẻ trong danh sách nhỏ hơn 22 %; nội dung chiếm 70-89 % màn hình 16:9 và 20:9. Màn Căn cứ là ảnh chụp thật từ trên xuống của trại trên từng bản đồ, mũi tên đỏ là hướng địch tới, ô tháp đúng vị trí thật với cỡ 1 / 1,4 / 2, ô tiện ích hình lục giác; phủ tầm bắn (mặt đất cam, trên không xanh nhạt), chụm hai ngón để phóng to. Một bố trí chính áp cho cả 20 bản đồ theo vị trí (cổng, vòng ngoài, vòng trong, cạnh SCH, phía sau), bản đồ nào cần thì chỉnh riêng; 3 bộ căn cứ; tự xếp theo cách AI địch xếp. Sức mạnh căn cứ là đúng con số dùng để tính độ mạnh các đợt địch. Tiền đồn có tab riêng. Mỗi tháp có icon riêng.

#### Biểu tượng giáp và vũ khí (prompt 15)

Bộ biểu tượng vẽ mới hoàn toàn theo nét của Field Command 2.0, không dùng số và không dựa vào màu: 57 hình, không hình nào trùng hình khác (test so dữ liệu nét). **Giáp** 5 cấp đầy dần như pin: nét đứt (không giáp), viền mảnh, viền đôi, tô nửa dưới, tô kín có đinh tán; máy bay là khiên có cánh, tháp và công trình là khiên vân gạch. **Dạng vũ khí** 30 hình theo dạng đạn thật, với đạn động năng hình cho biết độ xuyên (viên tròn, viên đạn, đạn có đai, mũi tên xuyên, mũi tên đầu kép, mũi tên có vòng điện). **Dấu loại sát thương** ở góc chip: nón lõm có tia, hình nổ, ngọn lửa, chùm chấm, tia sáng; nhiệt áp có dấu riêng; động năng không có dấu. **Dấu phụ** (chỉ ở màn chi tiết và tooltip): đánh nóc, dẫn đường, nổ lan. Cỡ nhỏ nhất 34 px = 18,7 pt. Hiện ở: hàng dưới mọi thẻ xe, tháp và công trình (giáp mặt trước và 2 chip, "+N" nếu còn; thẻ gọn 1 chip), khay căn cứ và tiền đồn, màn chi tiết (sơ đồ giáp theo hướng, chip ở tab Vũ khí, bảng hiệu quả, dòng Mạnh với / Yếu trước tạo từ dữ liệu), giữ thẻ trong trận, dải xe đang chọn, tooltip khi chạm địch (✓ ~ ✕ cho từng xe trong bộ bài), bộ phận trùm, hàng 5 khiên ở độ phủ bộ bài và căn cứ, trang chú thích kèm bảng khắc chế. Cài đặt "Hiện số chi tiết" (mặc định tắt) thêm cấp và hệ số vào tooltip.

#### Mép bản đồ

![Đường ranh giới và cảnh ngoài viền.](../images/11_meta_giao_dien/shots_edge.png)

*Hình: Đường ranh giới và cảnh ngoài viền. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

Sheet: 11_meta_giao_dien/Cai_dat_mac_dinh — Cài đặt mặc định (1 dòng, 5 cột)

| id | trang_thai | ghi_chu |
|---|---|---|
| chua_ap | CHUA_AP:prompt_xuat_luot5 | hằng mặc định trong GraphicsOptions.cs, Haptics.cs, PlayerP… |

Sheet: 11_meta_giao_dien/Huong_dan — Hướng dẫn người chơi (403 dòng, 18 cột)

| id | khoa | nhom | bang | doi_tuong | dong_dau_vi | cach_danh_vi | manh_yeu_vi | meo_vi | khac_vi |
|---|---|---|---|---|---|---|---|---|---|
| chua_ap |  |  |  |  | hướng dẫn người chơi mới (prompt 24) đang hoãn; gợi ý trong… |  |  |  |  |
| guide.aa_57mm_vehicle | guide.aa_57mm_vehicle | guide | GuideText.cs | aa_57mm_vehicle | Xe phòng không 57 mm · cao xạ đòn nặng |  |  |  | Hai phát mỗi giây, tầm 52 m; trúng được cả xe nhẹ. |
| guide.aa_gun_tower | guide.aa_gun_tower | guide | GuideText.cs | aa_gun_tower | Pháo phòng không 40 mm · tháp ô vừa · cao xạ nhịp đều | bốn phát ngòi cận đích mỗi giây, tầm 48 m, bắn cả máy bay l… | thắng trực thăng, drone và xe nhẹ; xe tăng gần như miễn nhi… | khẩu ở giữa, giữa cao xạ bắn nhanh và cao xạ hạng nặng. |  |
| guide.aa_gun_vehicle | guide.aa_gun_vehicle | guide | GuideText.cs | aa_gun_vehicle | Xe cao xạ 40 mm · giáp nhẹ · cao xạ nhịp đều | bốn phát ngòi cận đích mỗi giây, vừa chạy vừa bắn, tầm 48 m. | thắng trực thăng, drone và xe nhẹ; xe tăng gần như miễn nhi… | đi cùng tuyến đầu để chống trực thăng. |  |
| guide.aa_turret | guide.aa_turret | guide | GuideText.cs | aa_turret | Tháp phòng không · công sự cố định · chống máy bay (42 m) | pháo đôi 30 mm cao xạ tới 42 m và tên lửa phòng không (44 m… | xé nát trực thăng và máy bay; lực lượng mặt đất phá nó dễ d… | dọn nó bằng xe tăng hoặc pháo binh trước khi máy bay ta bay… |  |
| guide.aa_vehicle | guide.aa_vehicle | guide | GuideText.cs | aa_vehicle | Pháo cao xạ tự hành · giáp mỏng · pháo và tên lửa | pháo đôi 35 mm cao xạ (36 m) bắn khi đang chạy, kèm tên lửa… | xé nát trực thăng, drone và máy bay phản lực; đạn cao xạ gầ… | kèm một chiếc với mỗi cụm xe tăng: rẻ mà chặn được trực thă… |  |
| guide.aerial_tanker | guide.aerial_tanker | guide | GuideText.cs | aerial_tanker | Máy bay tiếp dầu · không vũ trang, tạm thời |  |  |  | Phần cộng thời gian bay cho máy bay phe ta chưa được làm. |
| guide.air_raid | guide.air_raid | guide | GuideText.cs | air_raid | Không kích bất ngờ · sự kiện trận đấu · trúng cả hai phe | một đợt máy bay trung lập rải {{count}} quả bom dọc đường {… | gây sát thương mọi thứ bên dưới, cả ta lẫn địch; chỉ máy ba… | khi thấy cảnh báo, rút quân khỏi điểm nóng và để bom rơi tr… |  |
| guide.airborne_light_tank | guide.airborne_light_tank | guide | GuideText.cs | airborne_light_tank | Tăng nhẹ thả dù · rơi sau lưng địch |  |  |  | Pháo 105 mm, giáp mỏng, thả dù ở nơi phe ta nhìn thấy. |
| guide.airborne_vehicle | guide.airborne_vehicle | guide | GuideText.cs | airborne_vehicle | Xe đổ bộ đường không · giáp nhẹ · sau lưng địch | chạm thẻ rồi chạm vùng phe ta nhìn thấy: nó nhảy dù xuống t… | chiếm cứ điểm trống, đánh pháo binh từ phía sau; thua xe tă… | chạm thẻ hai lần để đưa nó về bãi thả. |  |
| guide.airfield | guide.airfield | guide | GuideText.cs | airfield | Sân bay dã chiến · mô-đun tiện ích | máy bay bay trên nó hồi 3% máu mỗi giây và nạp đạn; chúng v… | giúp trực thăng và máy bay bay được lâu hơn; chúng vẫn phải… | mang theo khi bộ bài có từ hai máy bay trở lên. |  |
| guide.airstrike | guide.airstrike | guide | GuideText.cs | airstrike | Không kích · một hàng bom · {{cp}} CP | {{delay}} giây sau khi gọi, máy bay thả {{count}} quả bom d… | đánh mạnh vào đoàn xe và tháp canh dọc đường; xe lẻ nằm ngo… | kéo dọc theo hướng tiến quân của địch để quả bom nào cũng t… |  |
| guide.ammo_carrier | guide.ammo_carrier | guide | GuideText.cs | ammo_carrier | Xe tiếp đạn · giáp mỏng · điểm nạp tiền phương | chỉ có súng máy nóc; bệ phóng và xe tên lửa hết đạn trong v… | giữ pháo phản lực và trực thăng bắn liên tục; giáp mỏng và… | đỗ sau các bệ phóng; chỉ huy tự đưa bệ phóng hết đạn tới nó… |  |
| guide.ammo_depot | guide.ammo_depot | guide | GuideText.cs | ammo_depot | Kho đạn · mô-đun tiện ích | xe nạp đạn tại căn cứ nhanh gấp đôi. | rất hợp với giàn phóng và pháo binh hay hết đạn; nổ rất mạn… | mang theo khi bộ bài nhiều pháo phản lực. |  |
| guide.ammo_resupply | guide.ammo_resupply | guide | GuideText.cs | ammo_resupply | Thả dù tiếp đạn · nạp đầy ngay · {{cp}} CP | mọi xe ta trong vòng {{radius}} m được nạp đầy đạn ngay lập… | giữ pháo binh và máy bay tiếp tục chiến đấu khi hết đạn; vô… | gọi cho lựu pháo và máy bay tấn công của bạn khi tốc độ bắn… |  |

*15 / 403 dòng đầu: xem sheet 11_meta_giao_dien/Huong_dan; in 10 / 18 cột; 6 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 11_meta_giao_dien/Ban_do_menu — Bản đồ trên menu (25 dòng, 6 cột)

| id | icon | theme | weathers |
|---|---|---|---|
| ashfield | pine | temperate | Clear;Clear;Overcast;Rain;Storm;Fog;Night |
| borderbridge | flag | temperate | Clear;Overcast;Rain;Fog;Storm;Night |
| capital | crown | urban | Clear;Night;Overcast;Rain;Fog;Storm |
| coralisles | sun | desert | Clear;Clear;Storm;Overcast;Night |
| dunebreak | dune | desert | Clear;Clear;Sandstorm;Overcast;Night |
| emberridge | flame | volcanic | Night;Night;Clear;Overcast;Fog;Storm |
| foundry | gear | urban | Overcast;Clear;Rain;Fog;Night;Night |
| frostpeak | snow | snow | Snow;Clear;Overcast;Fog;Night |
| greenvale | pine | temperate | Clear;Overcast;Rain;Storm;Fog;Night |
| hydrodam | bolt | temperate | Clear;Overcast;Rain;Fog;Storm;Night |
| ironport | anchor | harbor | Clear;Overcast;Rain;Storm;Fog;Night |
| junglepass | pine | jungle | Clear;Rain;Fog;Storm;Overcast;Night |
| landingbeach | anchor | temperate | Overcast;Fog;Clear;Rain;Storm;Night |
| launchsite | missile | desert | Clear;Night;Clear;Sandstorm;Night |
| lighthousebay | anchor | temperate | Overcast;Clear;Fog;Rain;Storm;Night |
| metrocity | home | urban | Night;Night;Clear;Rain;Overcast;Fog;Storm |
| openpit | gear | desert | Clear;Clear;Sandstorm;Overcast;Night |
| orbitalgate | globe | snow | Snow;Clear;Night;Overcast;Fog;Night |
| redrock | dune | desert | Clear;Clear;Sandstorm;Night |
| rustyard | anchor | harbor | Clear;Overcast;Rain;Fog;Night |
| saltflat | dune | desert | Clear;Clear;Clear;Sandstorm;Night |
| skyhold | jet | temperate | Clear;Clear;Overcast;Rain;Fog;Night |
| swamp | fog | jungle | Fog;Rain;Overcast;Storm;Clear;Night |
| veyra_old_quarter | tower | urban | Clear;Night;Overcast;Rain;Fog;Storm |
| whiteout | snow | snow | Snow;Snow;Fog;Clear;Night |

Sheet: 11_meta_giao_dien/Skin — Skin (10 dòng, 11 cột)

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

Sheet: 11_meta_giao_dien/Mo_khoa — Mở khóa (102 dòng, 7 cột)

| id | the | chuong |
|---|---|---|
| chapters.aa_vehicle | aa_vehicle | 2 |
| chapters.ammo_carrier | ammo_carrier | 2 |
| chapters.armored_bulldozer | armored_bulldozer | 4 |
| chapters.artillery | artillery | 2 |
| chapters.attack_helicopter | attack_helicopter | 3 |
| chapters.attack_jet | attack_jet | 7 |
| chapters.ballistic_launcher | ballistic_launcher | 8 |
| chapters.bmpt | bmpt | 4 |
| chapters.bunker_vehicle | bunker_vehicle | 6 |
| chapters.command_vehicle | command_vehicle | 4 |
| chapters.counter_battery_radar | counter_battery_radar | 2 |
| chapters.engineer_vehicle | engineer_vehicle | 1 |
| chapters.ew_jammer | ew_jammer | 5 |
| chapters.fighter_jet | fighter_jet | 3 |
| chapters.flame_tank | flame_tank | 2 |

*15 / 102 dòng đầu: xem sheet 11_meta_giao_dien/Mo_khoa.*

Sheet: 11_meta_giao_dien/Nhiem_vu_ngay — Nhiệm vụ ngày (8 dòng, 6 cột)

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

Sheet: 11_meta_giao_dien/Thanh_tuu — Thành tựu (1 dòng, 5 cột)

| id | trang_thai | ghi_chu |
|---|---|---|
| chua_ap | KHONG_CO | Không có trong mã và dữ liệu (tìm 03/10: 0 file C# nhắc tới… |

Sheet: 11_meta_giao_dien/Telemetry — Telemetry (1 dòng, 5 cột)

| id | trang_thai | ghi_chu |
|---|---|---|
| chua_ap | KHONG_CO | Không có hệ telemetry (chỉ SandboxSession.cs nhắc chữ 'Tele… |

## Các sheet khác của file

Mọi sheet chưa in ở mục trên (sheet input_<tên> là bản chép từ file khác, không in lại).

### Anh_can_cu

Trạng thái: Đã áp

Nguồn dữ liệu: 11_meta_giao_dien/Anh_can_cu.

Sheet: 11_meta_giao_dien/Anh_can_cu — Ảnh bản đồ căn cứ (20 dòng, 24 cột)

| id | map | arrows_from | brightness | camera | centre_x_m | centre_z_m | drop_radius_m | drop_zone_x_m | drop_zone_z_m |
|---|---|---|---|---|---|---|---|---|---|
| ashfield | ashfield | route | 0.494 | orthographic, straight down, front (HQ heading) up; the map… | -95.911 | -96.053 | 8.0 | -108.75 | -108.75 |
| borderbridge | borderbridge | route | 0.515 | orthographic, straight down, front (HQ heading) up; the map… | -97.089 | -90.986 | 8.0 | -108.75 | -108.75 |
| capital | capital | route | 0.399 | orthographic, straight down, front (HQ heading) up; the map… | -102.044 | -77.748 | 8.0 | -108.75 | -108.75 |
| coralisles | coralisles | route | 0.647 | orthographic, straight down, front (HQ heading) up; the map… | -103.257 | -100.257 | 8.0 | -108.75 | -108.75 |
| dunebreak | dunebreak | route | 0.642 | orthographic, straight down, front (HQ heading) up; the map… | -92.623 | -104.984 | 8.0 | -108.75 | -108.75 |
| emberridge | emberridge | route | 0.178 | orthographic, straight down, front (HQ heading) up; the map… | -91.657 | -92.549 | 8.0 | -108.75 | -108.75 |
| frostpeak | frostpeak | route | 0.768 | orthographic, straight down, front (HQ heading) up; the map… | -94.596 | -94.973 | 8.0 | -108.75 | -108.75 |
| greenvale | greenvale | route | 0.496 | orthographic, straight down, front (HQ heading) up; the map… | -96.562 | -89.526 | 8.0 | -108.75 | -108.75 |
| hydrodam | hydrodam | route | 0.512 | orthographic, straight down, front (HQ heading) up; the map… | -103.592 | -81.539 | 8.0 | -108.75 | -108.75 |
| ironport | ironport | route | 0.452 | orthographic, straight down, front (HQ heading) up; the map… | -93.661 | -107.146 | 8.0 | -108.75 | -108.75 |
| junglepass | junglepass | route | 0.298 | orthographic, straight down, front (HQ heading) up; the map… | -97.7 | -89.142 | 8.0 | -108.75 | -108.75 |
| landingbeach | landingbeach | route | 0.496 | orthographic, straight down, front (HQ heading) up; the map… | -92.225 | -88.391 | 8.0 | -108.75 | -108.75 |
| launchsite | launchsite | route | 0.64 | orthographic, straight down, front (HQ heading) up; the map… | -100.073 | -89.967 | 8.0 | -108.75 | -108.75 |
| metrocity | metrocity | route | 0.421 | orthographic, straight down, front (HQ heading) up; the map… | -97.257 | -99.257 | 8.0 | -108.75 | -108.75 |
| redrock | redrock | route | 0.629 | orthographic, straight down, front (HQ heading) up; the map… | -101.513 | -82.169 | 8.0 | -108.75 | -108.75 |
| rustyard | rustyard | route | 0.448 | orthographic, straight down, front (HQ heading) up; the map… | -95.869 | -90.599 | 8.0 | -108.75 | -108.75 |
| saltflat | saltflat | route | 0.64 | orthographic, straight down, front (HQ heading) up; the map… | -99.137 | -96.772 | 8.0 | -108.75 | -108.75 |
| skyhold | skyhold | route | 0.501 | orthographic, straight down, front (HQ heading) up; the map… | -104.219 | -100.42 | 8.0 | -108.75 | -108.75 |
| swamp | swamp | route | 0.298 | orthographic, straight down, front (HQ heading) up; the map… | -92.857 | -97.857 | 8.0 | -108.75 | -108.75 |
| whiteout | whiteout | route | 0.773 | orthographic, straight down, front (HQ heading) up; the map… | -94.063 | -93.872 | 8.0 | -108.75 | -108.75 |

*in 10 / 24 cột; 12 cột khác (và raw_json, nguon): xem sheet.*

### Anh_can_cu_mui_ten

Trạng thái: Đã áp

Nguồn dữ liệu: 11_meta_giao_dien/Anh_can_cu_mui_ten.

Sheet: 11_meta_giao_dien/Anh_can_cu_mui_ten — Ảnh căn cứ: mũi tên (52 dòng, 10 cột)

| id | anh_can_cu_id | thu_tu | at_x_m | at_z_m | dir_x_m | dir_z_m | routes |
|---|---|---|---|---|---|---|---|
| ashfield/0 | ashfield | 0 | -90.975 | -56.486 | -0.339 | -0.941 | 1 |
| ashfield/1 | ashfield | 1 | -70.778 | -81.894 | -0.812 | -0.584 | 2 |
| borderbridge/0 | borderbridge | 0 | -116.811 | -24.154 | 0.026 | -1.0 | 1 |
| borderbridge/1 | borderbridge | 1 | -65.396 | -68.118 | -0.723 | -0.691 | 2 |
| borderbridge/2 | borderbridge | 2 | -41.635 | -104.857 | -0.998 | -0.06 | 1 |
| capital/0 | capital | 0 | -54.224 | -107.234 | -1.0 | -0.024 | 4 |
| coralisles/0 | coralisles | 0 | -109.237 | -57.584 | -0.025 | -1.0 | 1 |
| coralisles/1 | coralisles | 1 | -85.541 | -67.465 | -0.516 | -0.856 | 2 |
| coralisles/2 | coralisles | 2 | -55.408 | -107.0 | -1.0 | 0.0 | 1 |
| dunebreak/0 | dunebreak | 0 | -87.642 | -51.02 | -0.405 | -0.914 | 1 |
| dunebreak/1 | dunebreak | 1 | -70.432 | -66.205 | -0.658 | -0.753 | 2 |
| dunebreak/2 | dunebreak | 2 | -48.921 | -106.964 | -1.0 | -0.017 | 1 |
| emberridge/0 | emberridge | 0 | -102.664 | -50.93 | -0.19 | -0.982 | 1 |
| emberridge/1 | emberridge | 1 | -68.651 | -68.858 | -0.688 | -0.725 | 2 |
| emberridge/2 | emberridge | 2 | -58.279 | -92.937 | -0.972 | -0.234 | 1 |

*15 / 52 dòng đầu: xem sheet 11_meta_giao_dien/Anh_can_cu_mui_ten.*

### Anh_can_cu_vien

Trạng thái: Đã áp

Nguồn dữ liệu: 11_meta_giao_dien/Anh_can_cu_vien.

Sheet: 11_meta_giao_dien/Anh_can_cu_vien — Ảnh căn cứ: viền (142 dòng, 7 cột)

| id | anh_can_cu_id | thu_tu | x_m | z_m |
|---|---|---|---|---|
| ashfield/0 | ashfield | 0 | -136.048 | -72.427 |
| ashfield/1 | ashfield | 1 | -125.623 | -120.163 |
| ashfield/2 | ashfield | 2 | -98.538 | -128.807 |
| ashfield/3 | ashfield | 3 | -64.204 | -136.09 |
| ashfield/4 | ashfield | 4 | -31.872 | -131.471 |
| ashfield/5 | ashfield | 5 | -67.29 | -86.283 |
| ashfield/6 | ashfield | 6 | -99.589 | -45.648 |
| ashfield/7 | ashfield | 7 | -133.462 | -37.519 |
| borderbridge/0 | borderbridge | 0 | -138.253 | -47.979 |
| borderbridge/1 | borderbridge | 1 | -133.943 | -87.849 |
| borderbridge/2 | borderbridge | 2 | -125.027 | -138.0 |
| borderbridge/3 | borderbridge | 3 | -65.253 | -138.0 |
| borderbridge/4 | borderbridge | 4 | -38.273 | -120.831 |
| borderbridge/5 | borderbridge | 5 | -43.336 | -96.777 |
| borderbridge/6 | borderbridge | 6 | -53.235 | -80.28 |

*15 / 142 dòng đầu: xem sheet 11_meta_giao_dien/Anh_can_cu_vien.*

### Meta_bang_hang

Trạng thái: Đã áp

Nguồn dữ liệu: 11_meta_giao_dien/Meta_bang_hang.

Sheet: 11_meta_giao_dien/Meta_bang_hang — Bảng hằng meta (C#) (167 dòng, 6 cột)

| id | bang | chi_so | gia_tri |
|---|---|---|---|
| GraphicsOptions#AntiAliasingLevels/0 | GraphicsOptions#AntiAliasingLevels | 0 | 1 |
| GraphicsOptions#AntiAliasingLevels/1 | GraphicsOptions#AntiAliasingLevels | 1 | 2 |
| GraphicsOptions#AntiAliasingLevels/2 | GraphicsOptions#AntiAliasingLevels | 2 | 4 |
| GraphicsOptions#FrameRates/0 | GraphicsOptions#FrameRates | 0 | 30 |
| GraphicsOptions#FrameRates/1 | GraphicsOptions#FrameRates | 1 | 60 |
| GraphicsOptions#FrameRates/2 | GraphicsOptions#FrameRates | 2 | 90 |
| GraphicsOptions#FrameRates/3 | GraphicsOptions#FrameRates | 3 | 120 |
| GraphicsOptions#RenderScales/0 | GraphicsOptions#RenderScales | 0 | 70 |
| GraphicsOptions#RenderScales/1 | GraphicsOptions#RenderScales | 1 | 85 |
| GraphicsOptions#RenderScales/2 | GraphicsOptions#RenderScales | 2 | 100 |
| MatchSettings#AllSupports/0 | MatchSettings#AllSupports | 0 | artillery_barrage |
| MatchSettings#AllSupports/1 | MatchSettings#AllSupports | 1 | airstrike |
| MatchSettings#AllSupports/2 | MatchSettings#AllSupports | 2 | cruise_missile |
| MatchSettings#AllSupports/3 | MatchSettings#AllSupports | 3 | smoke_screen |
| MatchSettings#AllSupports/4 | MatchSettings#AllSupports | 4 | repair_drop |

*15 / 167 dòng đầu: xem sheet 11_meta_giao_dien/Meta_bang_hang.*

### Meta_kinh_te

Trạng thái: Đã áp

Nguồn dữ liệu: 11_meta_giao_dien/Meta_kinh_te.

Sheet: 11_meta_giao_dien/Meta_kinh_te — Meta: kinh tế nâng hạng (10 dòng, 11 cột)

| id | xu_len_hang | xu_tich_luy | xu_tich_luy_game | ban_thiet_ke_tich_luy | ban_thiet_ke_tich_luy_game | so_tran_thang | gio_choi | trong_tran |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | TRUE |
| 2 | 50 | 50.0 | 50.0 | 2.0 | 2.0 | 1.0 | 0.15 | TRUE |
| 3 | 100 | 150.0 | 150.0 | 6.0 | 6.0 | 1.0 | 0.15 | TRUE |
| 4 | 200 | 350.0 | 350.0 | 14.0 | 14.0 | 2.0 | 0.3 | TRUE |
| 5 | 400 | 750.0 | 750.0 | 26.0 | 26.0 | 5.0 | 0.75 | TRUE |
| 6 | 700 | 1450.0 | 1450.0 | 46.0 | 46.0 | 8.0 | 1.2 | TRUE |
| 7 | 1200 | 2650.0 | 2650.0 | 76.0 | 76.0 | 15.0 | 2.25 | TRUE |
| 8 | 2000 | 4650.0 | 4650.0 | 121.0 | 121.0 | 25.0 | 3.75 | TRUE |
| 9 | 3200 | 7850.0 | 7850.0 | 186.0 | 186.0 | 43.0 | 6.45 | TRUE |
| 10 | 5000 | 12850.0 | 12850.0 | 276.0 | 276.0 | 70.0 | 10.5 | TRUE |

### Meta_kinh_te_nguon

Trạng thái: Đã áp

Nguồn dữ liệu: 11_meta_giao_dien/Meta_kinh_te_nguon.

Sheet: 11_meta_giao_dien/Meta_kinh_te_nguon — Meta: nguồn và chỗ tiêu xu (23 dòng, 9 cột)

| id | loai | don_vi_tinh | xu | tran | ghi_chu | nguon_ma |
|---|---|---|---|---|---|---|
| bac_anh_hung | nguon | he_so | 1.5 |  | Rewards.TierPay: Anh hùng | Game/Match/Rewards.cs:144 |
| bac_sat | nguon | he_so | 2.0 |  | Rewards.TierPay: Sắt | Game/Match/Rewards.cs:144 |
| cua_hang_goi_lon_nhat | nguon | goi | 180000.0 |  | gói xu lớn nhất (Cua_hang) | Cua_hang |
| hom_gia_cao_nhat | tieu | hom | 8000.0 |  | giá xu của hòm đắt nhất (Hom_do.coin_price) | Hom_do |
| hom_quang_cao_ngay | nguon | hom |  | 3.0 | DailyCrates.AdCrates: hòm xem quảng cáo mỗi ngày | Game/Match/Arsenal.cs:563 |
| hom_thang_ngay | nguon | hom |  | 5.0 | DailyCrates.WinCrates: hòm cho các trận thắng đầu mỗi ngày | Game/Match/Arsenal.cs:562 |
| nang_hang_tong | tieu | the | 12850.0 | 10.0 | xu nâng một thẻ hạng 1 -> tối đa (Nang_hang); trần: hạng tố… | Game/Match/Arsenal.cs:126 |
| nhiem_vu_choi_lai | nguon | he_so | 0.35 |  | Rewards.Mission: phần RewardCoins khi chơi lại | Game/Match/Rewards.cs:159 |
| nhiem_vu_lan_dau | nguon | he_so | 1.0 |  | Rewards.Mission: phần RewardCoins lần thắng đầu | Game/Match/Rewards.cs:159 |
| nhiem_vu_ngay | nguon | ngay | 151.25 | 3.0 | DailyMissions: số nhiệm vụ mỗi ngày (trần); xu: trung bình… | Game/Match/DailyMissions.cs:51 |
| nhiem_vu_sao | nguon | sao | 50.0 | 3.0 | Rewards.Mission: mỗi sao (x TierPay), tối đa 3 sao | Game/Match/Rewards.cs:160 |
| nhiem_vu_thua | nguon | tran | 30.0 |  | Rewards.Mission: thua | Game/Match/Rewards.cs:155 |
| skin_tong | tieu | skin | 20900.0 |  | tổng giá mọi skin (Skin.price) | Skin |
| song_sot_co_ban | nguon | tran | 30.0 |  | Rewards.Survival: cơ bản | Game/Match/Rewards.cs:104 |
| song_sot_dot | nguon | dot | 18.0 |  | Rewards.Survival: mỗi đợt | Game/Match/Rewards.cs:104 |
| song_sot_ha_xe | nguon | ha_xe | 1.5 | 150.0 | Rewards.Survival: mỗi xe hạ, tối đa | Game/Match/Rewards.cs:104 |
| tran_nhanh_ha_xe | nguon | ha_xe | 1.5 | 120.0 | Rewards.Quick: mỗi xe hạ, tối đa | Game/Match/Rewards.cs:95 |
| tran_nhanh_hoa | nguon | tran | 70.0 |  | Rewards.Quick: hòa | Game/Match/Rewards.cs:94 |
| tran_nhanh_phut | nguon | phut | 4.0 | 15.0 | Rewards.Quick: mỗi phút, tối đa (phút) | Game/Match/Rewards.cs:97 |
| tran_nhanh_thang | nguon | tran | 120.0 |  | Rewards.Quick: thắng | Game/Match/Rewards.cs:94 |
| tran_nhanh_thua | nguon | tran | 40.0 |  | Rewards.Quick: thua | Game/Match/Rewards.cs:94 |
| vo_tan_boss | nguon | boss | 60.0 | 600.0 | Endless: mỗi boss; trần xu mỗi ngày | Sim/Modes/Endless.cs:45 |
| vo_tan_dot | nguon | dot | 18.0 | 600.0 | Endless: mỗi đợt; trần xu mỗi ngày | Sim/Modes/Endless.cs:45 |

### Meta_kinh_te_tran

Trạng thái: Đã áp

Nguồn dữ liệu: 11_meta_giao_dien/Meta_kinh_te_tran.

Sheet: 11_meta_giao_dien/Meta_kinh_te_tran — Meta: xu mỗi trận nhanh (12 dòng, 10 cột)

| id | do_kho | ket_qua | he_so_do_kho | so_xe_ha | so_phut | xu | xu_game |
|---|---|---|---|---|---|---|---|
| Easy/hoa | Easy | hoa | 0.7 | 20.0 | 9.0 | 95.0 | 95.0 |
| Easy/thang | Easy | thang | 0.7 | 20.0 | 9.0 | 130.0 | 130.0 |
| Easy/thua | Easy | thua | 0.7 | 20.0 | 9.0 | 74.0 | 74.0 |
| Hard/hoa | Hard | hoa | 1.45 | 20.0 | 9.0 | 197.0 | 197.0 |
| Hard/thang | Hard | thang | 1.45 | 20.0 | 9.0 | 270.0 | 270.0 |
| Hard/thua | Hard | thua | 1.45 | 20.0 | 9.0 | 154.0 | 154.0 |
| Normal/hoa | Normal | hoa | 1.0 | 20.0 | 9.0 | 136.0 | 136.0 |
| Normal/thang | Normal | thang | 1.0 | 20.0 | 9.0 | 186.0 | 186.0 |
| Normal/thua | Normal | thua | 1.0 | 20.0 | 9.0 | 106.0 | 106.0 |
| VeryHard/hoa | VeryHard | hoa | 1.8 | 20.0 | 9.0 | 245.0 | 245.0 |
| VeryHard/thang | VeryHard | thang | 1.8 | 20.0 | 9.0 | 335.0 | 335.0 |
| VeryHard/thua | VeryHard | thua | 1.8 | 20.0 | 9.0 | 191.0 | 191.0 |

### Mo_khoa_chung

Trạng thái: Đã áp

Nguồn dữ liệu: 11_meta_giao_dien/Mo_khoa_chung.

Sheet: 11_meta_giao_dien/Mo_khoa_chung — Mở khóa: ghi chú (3 dòng, 8 cột)

| id | khoa | gia_tri_chu |
|---|---|---|
| _about | _about | Generated by Tools/balance/import_unlocks.py from the sheet… |
| loot | loot | wingman_drone;swarm_carrier;bunker_vehicle;railgun_truck |
| starters | starters | scout_jeep;armored_car;ifv;main_battle_tank |

### Thu_hang

Trạng thái: Đã áp

Nguồn dữ liệu: 11_meta_giao_dien/Thu_hang.

Sheet: 11_meta_giao_dien/Thu_hang — Thứ hạng (1 dòng, 5 cột)

| id | trang_thai | ghi_chu |
|---|---|---|
| chua_ap | XEM_05 | thứ tự xếp hạng ở 05_che_do_kinh_te/Vo_han (matchRules.lead… |

### Thuong

Trạng thái: Đã áp

Nguồn dữ liệu: 11_meta_giao_dien/Thuong.

Sheet: 11_meta_giao_dien/Thuong — Thưởng (1 dòng, 5 cột)

| id | trang_thai | ghi_chu |
|---|---|---|
| chua_ap | XEM_Meta_kinh_te_nguon | xu / XP / bản thiết kế mỗi nhiệm vụ: 07/Nhiem_vu (coins, xp… |
