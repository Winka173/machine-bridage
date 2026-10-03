# 13_tham_chieu_nguon — Tham chiếu ngoài đời và game (nguồn)

Bộ xuất dữ liệu Machine Brigade, commit 90337539, ngày 2026-10-03. Sinh bởi `python Tools/export/export.py` (lượt 6): bảng in đúng ô của csv / xlsx; văn bản lấy từ tài liệu thiết kế (Tools/docs) và chuỗi trong game. Toàn văn: Machine_Brigade_Design_FULL_2026-10-03.md.

Nguồn tham chiếu, cơ chế lấy từ game, học thuyết, danh sách thiếu nguồn, tài liệu bản quyền (spec 12.3; chỉ dữ liệu trong repo, không tra web)

Mục: (không có mục riêng trong tài liệu thiết kế; chỉ bảng).

## Các sheet khác của file

Mọi sheet chưa in ở mục trên (sheet input_<tên> là bản chép từ file khác, không in lại).

### Nguon_tham_chieu

Trạng thái: Đã áp

Nguồn dữ liệu: 13_tham_chieu_nguon/Nguon_tham_chieu.

Sheet: 13_tham_chieu_nguon/Nguon_tham_chieu — Nguồn tham chiếu (179 dòng, 14 cột)

| id | loai | tieu_de | url | do_tin_cay | trich_tu | so_lan_dung | ghi_chu |
|---|---|---|---|---|---|---|---|
| D_96_general_library | thu_vien_am_thanh | 96 General Library |  | 2 | 09_hieu_ung_am_thanh/Am_thanh | 1 |  |
| D_army_recognition_buk_m1_2 | bai_bao | Army Recognition 'Buk-M1-2' |  | 2 | Tools/models/reference_real.json | 7 |  |
| D_attack_aircraft_maneuvers | thu_vien_am_thanh | Attack Aircraft Maneuvers |  | 2 | 09_hieu_ung_am_thanh/Am_thanh | 1 |  |
| D_battlefield_howitzers | thu_vien_am_thanh | Battlefield Howitzers |  | 2 | 09_hieu_ung_am_thanh/Am_thanh | 1 |  |
| D_bullet_impact_sounds | thu_vien_am_thanh | Bullet Impact Sounds |  | 2 | 09_hieu_ung_am_thanh/Am_thanh | 1 |  |
| D_caterpillar_d9r_specifications | nha_san_xuat | Caterpillar D9R specifications |  | 1 | Tools/models/reference_real.json | 7 |  |
| D_combat_drone | thu_vien_am_thanh | Combat Drone |  | 2 | 09_hieu_ung_am_thanh/Am_thanh | 2 |  |
| D_command_modern_operations_weapon_release_aut | nha_phat_hanh_game | Command: Modern Operations · Weapon Release Authorization | https://command.matrixgames.com/?p=3598 | 1 | Docs/ai/Machine_Brigade_AI_Research.xlsx | 21 | Thế FREE / TIGHT / HOLD và giới hạn vũ khí theo loại mục ti… |
| D_designed_fire | thu_vien_am_thanh | Designed Fire |  | 2 | 09_hieu_ung_am_thanh/Am_thanh | 1 |  |
| D_detonation_explosion | thu_vien_am_thanh | Detonation - Explosion |  | 2 | 09_hieu_ung_am_thanh/Am_thanh | 2 |  |
| D_eradication_small_pack | thu_vien_am_thanh | Eradication - Small Pack |  | 2 | 09_hieu_ung_am_thanh/Am_thanh | 1 |  |
| D_essentials_01_thunder | thu_vien_am_thanh | Essentials 01 Thunder |  | 2 | 09_hieu_ung_am_thanh/Am_thanh | 1 |  |
| D_essentials_03_fireworks | thu_vien_am_thanh | Essentials 03 Fireworks |  | 2 | 09_hieu_ung_am_thanh/Am_thanh | 1 |  |
| D_explosion_sfx_pack | thu_vien_am_thanh | Explosion SFX Pack |  | 2 | 09_hieu_ung_am_thanh/Am_thanh | 1 |  |
| D_explosion_sound_pack | thu_vien_am_thanh | Explosion Sound Pack |  | 2 | 09_hieu_ung_am_thanh/Am_thanh | 1 |  |

*15 / 179 dòng đầu: xem sheet 13_tham_chieu_nguon/Nguon_tham_chieu.*

### Tai_lieu_ban_quyen

Trạng thái: Đã áp

Nguồn dữ liệu: 13_tham_chieu_nguon/Tai_lieu_ban_quyen.

Sheet: 13_tham_chieu_nguon/Tai_lieu_ban_quyen — Tài liệu và tác phẩm có bản quyền (220 dòng, 8 cột)

| id | loai | ten | cach_dung | dung_o |
|---|---|---|---|---|
| game/ace_combat | game | Ace Combat | chỉ lấy ý (cơ chế / hình dáng); không dùng tên, logo, văn b… | 03_boss/Boss_tham_chieu;06_ai/AI_boss; 03_boss/Boss_tham_ch… |
| game/ace_combat_5 | game | Ace Combat 5 | chỉ lấy ý (cơ chế / hình dáng); không dùng tên, logo, văn b… | 13_tham_chieu_nguon/Tham_chieu_de_xuat |
| game/age_of_empires | game | Age of Empires | chỉ lấy ý (cơ chế / hình dáng); không dùng tên, logo, văn b… | 06_ai/AI_tham_so |
| game/arma | game | ArmA | chỉ lấy ý (cơ chế / hình dáng); không dùng tên, logo, văn b… | 06_ai/AI_tham_chieu |
| game/battlefield | game | Battlefield | chỉ lấy ý (cơ chế / hình dáng); không dùng tên, logo, văn b… | 06_ai/AI_tham_chieu;13_tham_chieu_nguon/Tham_chieu_de_xuat;… |
| game/battlefield_1942 | game | Battlefield 1942 | chỉ lấy ý (cơ chế / hình dáng); không dùng tên, logo, văn b… | 13_tham_chieu_nguon/Tham_chieu_de_xuat |
| game/battlestations_pacific | game | Battlestations: Pacific | chỉ lấy ý (cơ chế / hình dáng); không dùng tên, logo, văn b… | 13_tham_chieu_nguon/Tham_chieu_de_xuat |
| game/bloons_td_6 | game | Bloons TD 6 | chỉ lấy ý (cơ chế / hình dáng); không dùng tên, logo, văn b… | 04_can_cu_thap/Can_cu_tham_chieu;04_can_cu_thap/Can_cu_tham… |
| game/broken_arrow | game | Broken Arrow | chỉ lấy ý (cơ chế / hình dáng); không dùng tên, logo, văn b… | 13_tham_chieu_nguon/Tham_chieu_de_xuat |
| game/c_c | game | C&C | chỉ lấy ý (cơ chế / hình dáng); không dùng tên, logo, văn b… | 06_ai/AI_tham_chieu;13_tham_chieu_nguon/Tham_chieu_de_xuat |
| game/c_c_generals | game | C&C Generals | chỉ lấy ý (cơ chế / hình dáng); không dùng tên, logo, văn b… | 13_tham_chieu_nguon/Tham_chieu_de_xuat |
| game/call_of_duty | game | Call of Duty | chỉ lấy ý (cơ chế / hình dáng); không dùng tên, logo, văn b… | 06_ai/AI_tham_chieu |
| game/command_conquer | game | Command & Conquer | chỉ lấy ý (cơ chế / hình dáng); không dùng tên, logo, văn b… | 02_phuong_tien/Phuong_tien_tham_chieu;03_boss/Boss_tham_chi… |
| game/command_modern_operations | game | Command: Modern Operations | chỉ lấy ý (cơ chế / hình dáng); không dùng tên, logo, văn b… | 04_can_cu_thap/Can_cu_tham_chieu;04_can_cu_thap/Can_cu_tham… |
| game/company_of_heroes | game | Company of Heroes | chỉ lấy ý (cơ chế / hình dáng); không dùng tên, logo, văn b… | 04_can_cu_thap/Can_cu_tham_chieu;04_can_cu_thap/Can_cu_tham… |

*15 / 220 dòng đầu: xem sheet 13_tham_chieu_nguon/Tai_lieu_ban_quyen.*

### Tham_chieu_de_xuat

Trạng thái: Đã áp

Nguồn dữ liệu: 13_tham_chieu_nguon/Tham_chieu_de_xuat.

Sheet: 13_tham_chieu_nguon/Tham_chieu_de_xuat — Đề xuất: tham chiếu ngoài đời / game (103 dòng, 10 cột)

| id | sheet_nguon | ten_de_xuat | ten_mau_that | ten_game | cam_giac_khac_khi_choi | do_tin_cay | nguon_id |
|---|---|---|---|---|---|---|---|
| boss_moi/000 | Boss mới | Kraken · Tàu sân bay | Lớp Nimitz / Kuznetsov | Red Alert 3 (Shogun), World of Warships |  | uoc_dinh | R_machine_brigade_can_bang |
| boss_moi/001 | Boss mới | Monster · Pháo tự hành 800 mm | 2B1 Oka và Object 271 (1957) | Company of Heroes (pháo siêu nặng), Metal Gear |  | uoc_dinh | R_machine_brigade_can_bang |
| boss_moi/002 | Boss mới | Garuda · Cánh bay ném bom khổng lồ | Cánh bay B-2 phóng to; B-21 Raider | Ace Combat (Hresvelgr, Aigaion) |  | uoc_dinh | R_machine_brigade_can_bang |
| boss_moi/003 | Boss mới | Hyperion · Trạm gương quỹ đạo | Gương quỹ đạo Znamya (Nga, thử nghiệm 1993) | Ace Combat 5 (SOLG), C&C (Ion Cannon) |  | uoc_dinh | R_machine_brigade_can_bang |
| boss_moi/004 | Boss mới | Stymphalos · Bầy UAV phản lực | Loyal Wingman (MQ-28, XQ-58) | Mechabellum (Wasp), Ace Combat |  | uoc_dinh | R_machine_brigade_can_bang |
| boss_moi/005 | Boss mới | Nyx · Tàu khu trục tàng hình | Lớp Zumwalt | World of Warships, Battlefield |  | uoc_dinh | R_machine_brigade_can_bang |
| boss_moi/006 | Boss mới | Cerberus · Đoàn xe ba khung | Đoàn xe tải quân sự nối rơ-moóc | Mad Max, C&C (xe hộ tống) |  | uoc_dinh | R_machine_brigade_can_bang |
| boss_moi/007 | Boss mới | Hydra · Tàu ngầm mang drone | Tàu ngầm mang UUV/drone (khái niệm) | Battlestations: Pacific |  | uoc_dinh | R_machine_brigade_can_bang |
| cong_trinh_moi/000 | Công trình mới | Tháp cao xạ hạng nặng 100 mm (KS-19) | KS-19 100 mm (1947) | Red Alert 2 (Flak Cannon) | Nổ chậm, to, khói đen trên trời | uoc_dinh | R_machine_brigade_can_bang |
| cong_trinh_moi/001 | Công trình mới | Ụ pháo chống tăng | 2A45 Sprut-B, MT-12 Rapira | Company of Heroes (pháo chống tăng) | Chống tăng rẻ ở vòng ngoài căn cứ | uoc_dinh | R_machine_brigade_can_bang |
| cong_trinh_moi/002 | Công trình mới | Tổ tên lửa vác vai | Tổ MANPADS | Wargame | Phòng không rẻ, không bắn đất | uoc_dinh | R_machine_brigade_can_bang |
| cong_trinh_moi/003 | Công trình mới | Ụ súng không giật | SPG-9 Kopyo | Company of Heroes | Chống tăng rẻ hơn Ụ pháo chống tăng nhưng yếu hơn | uoc_dinh | R_machine_brigade_can_bang |
| cong_trinh_moi/004 | Công trình mới | Tường chắn đạn | Tường Hesco | Company of Heroes (vật che) | Xếp căn cứ theo tuyến che chắn | uoc_dinh | R_machine_brigade_can_bang |
| cong_trinh_moi/005 | Công trình mới | Mồi nhử bơm hơi | Mồi nhử bơm hơi | Red Alert (công trình giả) | Đánh lừa pháo và tên lửa địch | uoc_dinh | R_machine_brigade_can_bang |
| cong_trinh_moi/006 | Công trình mới | Trung tâm điều khiển hỏa lực | Trung tâm điều khiển hỏa lực (FDC) | Bloons TD 6 (Monkey Village) | Cụm tháp liên kết | uoc_dinh | R_machine_brigade_can_bang |

*15 / 103 dòng đầu: xem sheet 13_tham_chieu_nguon/Tham_chieu_de_xuat.*

### Tham_chieu_decisions

Trạng thái: Đã áp

Nguồn dữ liệu: 13_tham_chieu_nguon/Tham_chieu_decisions.

Sheet: 13_tham_chieu_nguon/Tham_chieu_decisions — Tham chiếu trong DECISIONS (14 dòng, 9 cột)

| id | muc | muc_con | dong | van_ban | game_phim_nhac_den | nguon_id |
|---|---|---|---|---|---|---|
| REF001 | 20Y. Boss redesigns: Leviathan as a battleship, Ixion, Icar… | A. Leviathan (`leviathan`, `Tools/blender/mb_naval.py`) | 7882 | The IJN Yamato (1941) and its 1945 fit: the flush deck with… |  | R_decisions |
| REF002 | 20Y. Boss redesigns: Leviathan as a battleship, Ixion, Icar… | D. Ixion (`ixion`, `Tools/blender/mb_redesign_20y.py`) | 7972 | the Lebedenko "Tsar Tank" (1915: two 9 m spoked wheels on o… | Warhammer;Gears of War;Metal Gear | R_decisions |
| REF003 | 20Y. Boss redesigns: Leviathan as a battleship, Ixion, Icar… | E. Icarus (`silver_bug`, `silver_bug_wreck`) | 7985 | the Imperial-class Star Destroyer (the dagger plan, the sid… | Star Wars;Star Destroyer;Venator | R_decisions |
| REF004 | 21H. Play-test 6: effects, models and sizes (2026-09-29) | A. The siege tank, after StarCraft 2's siege tank | 8153 | StarCraft 2's Siege Tank (Crucio), tank mode and siege mode… | StarCraft | R_decisions |
| REF005 | 21H. Play-test 6: effects, models and sizes (2026-09-29) | B. Launchers raise their launcher to fire | 8184 | HIMARS and M270 (the pod raised and traversed to fire), BM-… |  | R_decisions |
| REF006 | 21H. Play-test 6: effects, models and sizes (2026-09-29) | C. The SEAD strike | 8209 | the AGM-88 HARM's dive on to a radar, the SEAD and HARM hit… | Battlefield;Wargame | R_decisions |
| REF007 | 21H. Play-test 6: effects, models and sizes (2026-09-29) | F. Fire on vehicles and bosses | 8241 | burning tanks in World of Tanks (flames out of the engine d… | World of Tanks;Battlefield;Company of Heroes | R_decisions |
| REF008 | 22R. Play-test 8 B: the burning-vehicle fire, faster-cleari… | A. The fire on damaged vehicles, drawn a third time | 9706 | War Thunder's and World of Tanks' burning tanks (flames out… | World of Tanks;War Thunder;Company of Heroes | R_decisions |
| REF009 | 22R. Play-test 8 B: the burning-vehicle fire, faster-cleari… | D. Icarus, redesigned | 9771 | the Soviet Polyus / Skif-DM orbital weapons platform (1987:… | Ace Combat;The Expanse | R_decisions |
| REF010 | 23M. Play-test 9 models: Icarus a spaceship, the stealth je… | A. Icarus, a warship again | 10614 | (looked up for this pass): - Star Wars: the Imperial Star D… | Halo;Star Wars;Star Destroyer;Venator | R_decisions |
| REF011 | 23M. Play-test 9 models: Icarus a spaceship, the stealth je… | B. The stealth jet, slim | 10672 | the F-22 Raptor (18.9 x 13.6 m; the 42 degree leading edge,… |  | R_decisions |
| REF012 | PT10 visuals. The In action preview and the flak burst (202… | Shared edits (merge by hand if they conflict) | 12199 | WWII 88 mm and Bofors 40 mm barrage footage, Cold War ZSU-2… | War Thunder;Battlefield | R_decisions |
| REF013 | 26CD. Boss sizes, Ixion, Gungnir and the post-1945 rule (pr… | D2. Gungnir, the rail electromagnetic supergun | 12715 | US Navy EMRG scaled up, the BZhRK Barguzin train, a modern… |  | R_decisions |
| REF014 | Bộ xuất dữ liệu toàn bộ (lane C, pass 10) | For the lead (compile, render, build) | 17741 | " passages), `Docs/ASSET_LICENSES.md` and the audio credits… |  | R_decisions |

### Tham_chieu_game_co_che

Trạng thái: Đã áp

Nguồn dữ liệu: 13_tham_chieu_nguon/Tham_chieu_game_co_che.

Sheet: 13_tham_chieu_nguon/Tham_chieu_game_co_che — Cơ chế lấy ý từ game (182 dòng, 14 cột)

| id | ten_game | co_che | nhom | diem_giong | diem_khac_co_chu_dich | muc_ap_dung | dan_den_sheet | thuc_the | nguon_id |
|---|---|---|---|---|---|---|---|---|---|
| AI/ace_combat/boss_bay | Ace Combat | boss bay | AI | Bay theo đường cố định; chọn vòng bay tránh vùng phòng khôn… |  | chi_lay_y | 06_ai/AI_boss; 03_boss/Boss_tham_chieu | Boss trên không (Matriarch, Roc, Daedalus, Icarus) | R_machine_brigade_ai_research |
| AI/ace_combat/chon_chien_thuat | Ace Combat | chọn chiến thuật | AI | Tạo cửa sổ trên không rồi mới đưa đội mặt đất | Tướng AI mua tiêm kích và phòng không trước; đội mặt đất ch… | chi_lay_y | 06_ai/AI_tham_chieu | air_superiority | D_hearts_of_iron_iv_land_doctrine;R_machine_brigade_ai_rese… |
| AI/ace_combat/hanh_vi_vai_tro | Ace Combat | hành vi vai trò | AI | Chọn đường bay tránh phòng không tầm xa |  | chi_lay_y | 06_ai/AI_tham_chieu | Bomber;Fighter;Stealth | D_command_modern_operations_weapon_release_aut;R_machine_br… |
| AI/age_of_empires/bang_thong_tin_chung_blackboard_va_ban_do_anh_huong | Age of Empires | Bảng thông tin chung (blackboard) và bản đồ ảnh hưởng | AI | Lưới ô ghi sức mạnh, mối đe dọa theo loại, tiền tuyến, điểm… |  | chi_lay_y | 06_ai/AI_tham_so |  | R_machine_brigade_ai_research |
| AI/arma/khong_ghi_co_che | ArmA | (không ghi cơ chế) | AI | Tiến chậm, an toàn, một nhóm luôn yểm hộ | Đội chia 2 nhóm; nhóm tiến không vượt quá tầm yểm hộ của nh… | chi_lay_y | 06_ai/AI_tham_chieu | bounding | R_machine_brigade_ai_research;W_bounding_overwatch |
| AI/battlefield/hanh_vi_vai_tro | Battlefield | hành vi vai trò | AI | Dời tâm vòng bay ra khỏi vùng phòng không |  | chi_lay_y | 06_ai/AI_tham_chieu | Gunship;GunshipHeli | R_machine_brigade_ai_research |
| AI/battlefield/khong_ghi_co_che | Battlefield | (không ghi cơ chế) | AI | Dùng pháo sáng khi bị khóa; bay vòng ra khỏi vùng phòng khô… |  | chi_lay_y | 06_ai/AI_tham_chieu | AttackHeli | R_machine_brigade_ai_research |
| AI/bloons_td_6/che_do_chon_muc_tieu | Bloons TD 6 | chế độ chọn mục tiêu | AI | Tháp canh thép 11 m trên lô cốt |  | chi_lay_y | 04_can_cu_thap/Can_cu_tham_chieu;04_can_cu_thap/Can_cu_tham… | Tháp canh;guard_tower | R_machine_brigade_ai_research;R_machine_brigade_can_bang;R_… |
| AI/c_c/hanh_vi_vai_tro | C&C | hành vi vai trò | AI | Triển khai ở chỗ có vật che, quay mặt về hướng địch |  | chi_lay_y | 06_ai/AI_tham_chieu | Bunker;Siege | R_machine_brigade_ai_research |
| AI/c_c/khong_ghi_co_che | C&C | (không ghi cơ chế) | AI | Giữ quanh căn cứ và tháp | Đội giữ trong vùng căn cứ; tháp ưu tiên chế độ Đầu đoàn; mu… | chi_lay_y | 06_ai/AI_tham_chieu | base_defence | R_machine_brigade_ai_research |
| AI/c_c/mammoth_overlord | C&C | Mammoth/Overlord | AI | Đứng chắn trước đồng đội khi địch dồn hỏa lực |  | chi_lay_y | 06_ai/AI_tham_chieu | Heavy | R_machine_brigade_ai_research |
| AI/c_c/sieu_vu_khi_nho | C&C | siêu vũ khí nhỏ | AI | Không phóng vào mục tiêu đang di chuyển nhanh |  | chi_lay_y | 06_ai/AI_tham_chieu | Strike | R_machine_brigade_ai_research |
| AI/call_of_duty/ac_130 | Call of Duty | AC-130 | AI | Dời tâm vòng bay ra khỏi vùng phòng không |  | chi_lay_y | 06_ai/AI_tham_chieu | Gunship | R_machine_brigade_ai_research |
| AI/command_modern_operations/chon_muc_tieu_cua_patriot | Command: Modern Operations | chọn mục tiêu của Patriot | AI | PAC-3: ưu tiên tên lửa hành trình, đạn đạo, siêu vũ khí boss |  | chi_lay_y | 04_can_cu_thap/Can_cu_tham_chieu; 06_ai/AI_thap | Patriot | R_machine_brigade_ai_research |
| AI/command_modern_operations/emcon | Command: Modern Operations | EMCON | AI | cột lưới thép gây nhiễu điện tử |  | chi_lay_y | 04_can_cu_thap/Can_cu_tham_chieu;04_can_cu_thap/Can_cu_tham… | Tháp gây nhiễu EW;ew_tower | R_machine_brigade_ai_research;R_machine_brigade_can_bang;R_… |

*15 / 182 dòng đầu: xem sheet 13_tham_chieu_nguon/Tham_chieu_game_co_che.*

### Tham_chieu_hoc_thuyet

Trạng thái: Đã áp

Nguồn dữ liệu: 13_tham_chieu_nguon/Tham_chieu_hoc_thuyet.

Sheet: 13_tham_chieu_nguon/Tham_chieu_hoc_thuyet — Học thuyết quân sự và thuật ngữ (44 dòng, 8 cột)

| id | thuat_ngu | mo_ta | dung_o | do_tin_cay | nguon_id |
|---|---|---|---|---|---|
| ai_vai_tro_arty | Vai trò Lựu pháo / cối / pháo công thành | Bắn gián tiếp từ xa theo soi của trinh sát; bắn rồi dời vị… | 06_ai/AI_vai_tro/Arty | ban_dau_doan | R_machine_brigade_ai_research |
| ai_vai_tro_attackheli | Vai trò Trực thăng tấn công | Đánh từ ngoài tầm phòng không gần, núp sau địa hình, bắn tê… | 06_ai/AI_vai_tro/AttackHeli | ban_dau_doan | R_machine_brigade_ai_research |
| ai_vai_tro_bomber | Vai trò Oanh tạc cơ | Một lượt lớn vào mục tiêu đã chọn từ trước rồi rời đi. | 06_ai/AI_vai_tro/Bomber | ban_dau_doan | R_machine_brigade_ai_research |
| ai_vai_tro_bunker | Vai trò Xe công sự / xe ủi | Triển khai ở điểm giữ, chịu đòn; xe ủi phá chướng ngại mở đ… | 06_ai/AI_vai_tro/Bunker | ban_dau_doan | R_machine_brigade_ai_research |
| ai_vai_tro_cas | Vai trò Cường kích | Yểm trợ gần: đánh cụm xe và công trình ở tuyến đầu. | 06_ai/AI_vai_tro/CAS | ban_dau_doan | R_machine_brigade_ai_research |
| ai_vai_tro_drone | Vai trò Xe phóng drone / đạn lảng vảng | Đứng xa, phóng drone đánh nóc xe giáp và pháo binh. | 06_ai/AI_vai_tro/Drone | ban_dau_doan | R_machine_brigade_ai_research |
| ai_vai_tro_fighter | Vai trò Tiêm kích | Giành ưu thế trên không; hạ máy bay địch trước khi chúng đá… | 06_ai/AI_vai_tro/Fighter | da_kiem_chung | R_machine_brigade_ai_research;D_command_modern_operations_w… |
| ai_vai_tro_flame | Vai trò Tăng phun lửa | Dọn công sự và xe nhẹ ở tầm rất gần, đi sau khói hoặc xe tă… | 06_ai/AI_vai_tro/Flame | ban_dau_doan | R_machine_brigade_ai_research |
| ai_vai_tro_gunship | Vai trò Pháo hạm bay | Bay vòng chậm trên vùng ít phòng không, bắn liên tục. | 06_ai/AI_vai_tro/Gunship | ban_dau_doan | R_machine_brigade_ai_research |
| ai_vai_tro_gunshipheli | Vai trò Trực thăng vũ trang bọc giáp | Bay như "xe tăng bay": chịu được súng máy, yểm trợ gần cho… | 06_ai/AI_vai_tro/GunshipHeli | ban_dau_doan | R_machine_brigade_ai_research |
| ai_vai_tro_heavy | Vai trò Tăng hạng nặng / siêu tăng | Mũi đột phá: hút hỏa lực và mở đường cho đội; chậm, nên đi… | 06_ai/AI_vai_tro/Heavy | ban_dau_doan | R_machine_brigade_ai_research |
| ai_vai_tro_ifv | Vai trò Xe chiến đấu bộ binh | Đi cùng xe tăng, diệt xe nhẹ và hạ tăng bằng tên lửa ở tầm… | 06_ai/AI_vai_tro/IFV | ban_dau_doan | R_machine_brigade_ai_research |
| ai_vai_tro_laser | Vai trò La-de phòng không | Đánh chặn drone, rốc-két, cối; chi phí mỗi phát rất thấp. | 06_ai/AI_vai_tro/Laser | ban_dau_doan | R_machine_brigade_ai_research |
| ai_vai_tro_light | Vai trò Xe nhẹ / bọc thép bánh lốp | Trinh sát vũ trang và đánh nhanh: phát hiện, quấy rối, rồi… | 06_ai/AI_vai_tro/Light | ban_dau_doan | R_machine_brigade_ai_research |
| ai_vai_tro_mbt | Vai trò Tăng chủ lực | Đi đầu đội hình, đánh xe giáp ở 2–2,5 km; dùng thế "thân kh… | 06_ai/AI_vai_tro/MBT | da_kiem_chung | R_machine_brigade_ai_research;W_bounding_overwatch |

*15 / 44 dòng đầu: xem sheet 13_tham_chieu_nguon/Tham_chieu_hoc_thuyet.*

### Thieu_nguon

Trạng thái: Đã áp

Nguồn dữ liệu: 13_tham_chieu_nguon/Thieu_nguon.

Sheet: 13_tham_chieu_nguon/Thieu_nguon — Thiếu nguồn (5840 dòng, 11 cột)

| id | uu_tien | file | sheet | dong_id | entity_id | cot | ten_hien_thi | ten_mau_that |
|---|---|---|---|---|---|---|---|---|
| P1/01_vu_khi_dan/Vu_khi_tham_chieu/aa_25_triple/ngoai_doi_khoi_luong_dan_kg | 1 | 01_vu_khi_dan | Vu_khi_tham_chieu | aa_25_triple | aa_25_triple | ngoai_doi_khoi_luong_dan_kg | Type 96 25 mm (triple) | Type 96 25 mm (triple) |
| P1/01_vu_khi_dan/Vu_khi_tham_chieu/aa_25_triple/ngoai_doi_khoi_luong_thuoc_no_kg | 1 | 01_vu_khi_dan | Vu_khi_tham_chieu | aa_25_triple | aa_25_triple | ngoai_doi_khoi_luong_thuoc_no_kg | Type 96 25 mm (triple) | Type 96 25 mm (triple) |
| P1/01_vu_khi_dan/Vu_khi_tham_chieu/aa_25_triple/ngoai_doi_nap | 1 | 01_vu_khi_dan | Vu_khi_tham_chieu | aa_25_triple | aa_25_triple | ngoai_doi_nap | Type 96 25 mm (triple) | Type 96 25 mm (triple) |
| P1/01_vu_khi_dan/Vu_khi_tham_chieu/aa_25_triple/ngoai_doi_so_toc_dau_nong_m_s | 1 | 01_vu_khi_dan | Vu_khi_tham_chieu | aa_25_triple | aa_25_triple | ngoai_doi_so_toc_dau_nong_m_s | Type 96 25 mm (triple) | Type 96 25 mm (triple) |
| P1/01_vu_khi_dan/Vu_khi_tham_chieu/aa_25_triple/ngoai_doi_tam_hieu_qua_m | 1 | 01_vu_khi_dan | Vu_khi_tham_chieu | aa_25_triple | aa_25_triple | ngoai_doi_tam_hieu_qua_m | Type 96 25 mm (triple) | Type 96 25 mm (triple) |
| P1/01_vu_khi_dan/Vu_khi_tham_chieu/aa_25_triple/ngoai_doi_tam_toi_da_m | 1 | 01_vu_khi_dan | Vu_khi_tham_chieu | aa_25_triple | aa_25_triple | ngoai_doi_tam_toi_da_m | Type 96 25 mm (triple) | Type 96 25 mm (triple) |
| P1/01_vu_khi_dan/Vu_khi_tham_chieu/aa_25_triple_ap/ngoai_doi_khoi_luong_dan_kg | 1 | 01_vu_khi_dan | Vu_khi_tham_chieu | aa_25_triple_ap | aa_25_triple_ap | ngoai_doi_khoi_luong_dan_kg | Type 96 25 mm AP (triple) | Type 96 25 mm AP (triple) |
| P1/01_vu_khi_dan/Vu_khi_tham_chieu/aa_25_triple_ap/ngoai_doi_khoi_luong_thuoc_no_kg | 1 | 01_vu_khi_dan | Vu_khi_tham_chieu | aa_25_triple_ap | aa_25_triple_ap | ngoai_doi_khoi_luong_thuoc_no_kg | Type 96 25 mm AP (triple) | Type 96 25 mm AP (triple) |
| P1/01_vu_khi_dan/Vu_khi_tham_chieu/aa_25_triple_ap/ngoai_doi_nap | 1 | 01_vu_khi_dan | Vu_khi_tham_chieu | aa_25_triple_ap | aa_25_triple_ap | ngoai_doi_nap | Type 96 25 mm AP (triple) | Type 96 25 mm AP (triple) |
| P1/01_vu_khi_dan/Vu_khi_tham_chieu/aa_25_triple_ap/ngoai_doi_so_toc_dau_nong_m_s | 1 | 01_vu_khi_dan | Vu_khi_tham_chieu | aa_25_triple_ap | aa_25_triple_ap | ngoai_doi_so_toc_dau_nong_m_s | Type 96 25 mm AP (triple) | Type 96 25 mm AP (triple) |
| P1/01_vu_khi_dan/Vu_khi_tham_chieu/aa_25_triple_ap/ngoai_doi_tam_hieu_qua_m | 1 | 01_vu_khi_dan | Vu_khi_tham_chieu | aa_25_triple_ap | aa_25_triple_ap | ngoai_doi_tam_hieu_qua_m | Type 96 25 mm AP (triple) | Type 96 25 mm AP (triple) |
| P1/01_vu_khi_dan/Vu_khi_tham_chieu/aa_25_triple_ap/ngoai_doi_tam_toi_da_m | 1 | 01_vu_khi_dan | Vu_khi_tham_chieu | aa_25_triple_ap | aa_25_triple_ap | ngoai_doi_tam_toi_da_m | Type 96 25 mm AP (triple) | Type 96 25 mm AP (triple) |
| P1/01_vu_khi_dan/Vu_khi_tham_chieu/agl_40/ngoai_doi_khoi_luong_dan_kg | 1 | 01_vu_khi_dan | Vu_khi_tham_chieu | agl_40 | agl_40 | ngoai_doi_khoi_luong_dan_kg | Mk 19 40 mm | Mk 19 40 mm |
| P1/01_vu_khi_dan/Vu_khi_tham_chieu/agl_40/ngoai_doi_khoi_luong_thuoc_no_kg | 1 | 01_vu_khi_dan | Vu_khi_tham_chieu | agl_40 | agl_40 | ngoai_doi_khoi_luong_thuoc_no_kg | Mk 19 40 mm | Mk 19 40 mm |
| P1/01_vu_khi_dan/Vu_khi_tham_chieu/agl_40/ngoai_doi_nap | 1 | 01_vu_khi_dan | Vu_khi_tham_chieu | agl_40 | agl_40 | ngoai_doi_nap | Mk 19 40 mm | Mk 19 40 mm |

*15 / 5840 dòng đầu: xem sheet 13_tham_chieu_nguon/Thieu_nguon.*
