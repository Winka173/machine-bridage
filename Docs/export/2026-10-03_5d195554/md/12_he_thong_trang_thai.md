# 12_he_thong_trang_thai — Hệ thống và trạng thái

Bộ xuất dữ liệu Machine Brigade, commit 5d195554, ngày 2026-10-03. Sinh bởi `python Tools/export/export.py` (lượt 6): bảng in đúng ô của csv / xlsx; văn bản lấy từ tài liệu thiết kế (Tools/docs) và chuỗi trong game. Toàn văn: Machine_Brigade_Design_FULL_2026-10-03.md.

Trạng thái prompt, DECISIONS, chờ quyết, kiểm tra mã, bản đồ trường dữ liệu, kết quả áp manifest, test, validator, lịch sử đo, chuyển đổi save, bảng đơn vị tài liệu, chưa phân loại; Hang_so_trong_ma ở lượt 5

Mục trong file này: 17. Kiểm thử và phép đo còn lại; P1. Hằng số trong mã; P2. Lịch sử đo; P3. Quyết định và chờ quyết; P4. Trạng thái prompt, validator, manifest và save; P5. Mục lục bảng dữ liệu, sửa chữ theo mã và ảnh.

## 17. Kiểm thử và phép đo còn lại

Trạng thái: Đã áp

Nguồn dữ liệu: 12_he_thong_trang_thai/Test; 12_he_thong_trang_thai/Validator; 12_he_thong_trang_thai/Kiem_tra_file. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §17, §16b. Sửa sau buổi chơi thử.

#### 17. Kiểm thử và phép đo còn lại

Bài kiểm tra tự động chạy trong Unity (EditMode): mô phỏng xác định, nên mỗi luật có bài riêng (điểm lưu phát lại khớp tuyệt đối, phản bội không làm lỗi AI, trần xe, vùng chơi, mutator, bộ phận boss...). Các phép đo dài (5 seed, phòng thí nghiệm trang bị) dồn vào một phase kiểm tra riêng:

- Quét 5 seed toàn chiến dịch sau khi gộp mọi nhánh (21 nhiệm vụ trên 8 bản đồ mới chưa đo; các chiến dịch lớn giữ trong 15–25 phút).
- Tác chiến: mọi tuần của vòng xoay thắng được qua 5 seed ở cấp Thường.
- Công thành, Phòng thủ (mục tiêu ≥ 4/5), Vô tận, Pháo đài tuần ở các độ khó và 7 bản đồ còn lại.
- Xe tinh nhuệ theo ngân sách: tỷ lệ sức mạnh 1,8–2,2 lần; chiến dịch và Săn trùm sau khi đổi sang ngân sách.
- Trang bị: độ chênh giữa các nhóm vũ khí (mục tiêu ≤ 1,5 lần), Nạp kép trên pháo tự động và giàn rocket, đầu đạn chùm lên công trình, cầu tuyết sau trần hoàn CP.
- Đã chạy trong đợt cân bằng sau prompt 18 (DECISIONS 19B, số liệu trong Docs/balance, tables_p18.md): quét 5 seed toàn chiến dịch trước/sau, bộ phát hiện xe kẹt trên 21 bản đồ × 4 chế độ × 5 seed (420 trận), ngân sách tick, mọi chế độ ở 4 độ khó × 5 seed; còn lại ở đây là phần chưa đạt.
- Boss: thời gian hạ trong +15% sau khi có bộ phận; mọi trận boss và Săn trùm thắng được (Săn trùm chạm trần 30 phút ở cả 10 trận đo, sau prompt 18).
- Hiệu năng: ngân sách tick đo lại trên máy yên tĩnh và điện thoại yếu thật; FPS trận boss nặng nhất ở mức đồ họa Thấp; đảo và đầm lầy (2.500 vật thể).
- Sau buổi chơi thử: khả năng thắng chiến dịch và trận boss khi súng chính xe thường không còn bắn máy bay; thời gian hạ tăng của máy bay cường kích và A-10 với nhịp bắn mới; tỷ lệ trúng của tên lửa chậm hơn khi có pháo sáng và APS; FPS khi nhiều tên lửa hành trình hoặc ném bom rải thảm cùng lúc ở đồ họa Thấp; khung hình những giây đầu trên điện thoại thật.
- Giao diện: FPS của HUD mới ở đồ họa Thấp; vùng an toàn trên máy tai thỏ và đục lỗ thật; toàn bộ bài kiểm tra EditMode.
- Cân bằng (prompt 13): đủ 5 seed mọi chế độ với người chơi thật, nhất là Công thành, Phòng thủ, Pháo đài tuần và Tử chiến; khoảng cách Thường và Khó; Vô tận/Phòng thủ với căn cứ mạnh yếu khác nhau; thời gian từng boss; mọi mutator Tác chiến; toàn bộ chiến dịch nhiều seed; lượt bay ra vòng chờ dài nhất của oanh tạc cơ (4,5 giây, trên mục tiêu 3 giây).
- Xe kẹt (prompt 12): chạy công cụ phát hiện xe kẹt đủ 20 bản đồ mọi chế độ, 5 seed, mọi loadout, bật và tắt lưới an toàn; TickBudgetTests đầy đủ; trận Đầm Lầy và Quần Đảo San Hô.

#### 16b. Sửa sau buổi chơi thử (28/9)

Chủ dự án chơi thử bản phase 1-9 và báo 16 lỗi; bốn nhóm sửa song song, mỗi nhóm có bài kiểm tra riêng và chạy thử chế độ Play (0 lỗi).

#### Nòng súng và đường đạn

- **Đạn ra lệch nòng:** nguyên nhân là hiệu ứng bắn được đặt khi xe còn ở tư thế của khung hình trước (lệch tới 2,4 m ở trực thăng, 4,7 m ở máy bay). Giờ đạn, chớp lửa và vệt khói xuất phát từ đầu nòng đúng như được vẽ trong khung hình đó, ở mọi hướng thân, tháp pháo, góc nâng và tư thế bay: đo được 0,000 m trên 400 phát.
- **Đạn pháo, cối:** bay trên một đường cong duy nhất ra khỏi nòng theo hướng nòng; đạn, vệt khói và điểm bắt đầu khớp nhau suốt đường bay.
- **Kích thước:** tên lửa chống tăng và vác vai ×1,1; rocket ×1,15; không đối đất, phòng không, không đối không, hành trình ×1,2; drone ×2.

#### Vũ khí

- **Mục tiêu:** xe chuyên phòng không (và tháp phòng không) giữ vũ khí chính bắn máy bay và ngóc nòng lên theo máy bay; xe khác chỉ bắn máy bay bằng súng máy. Đổi sang chỉ bắn mặt đất: pháo 25 mm (xe bọc thép, tổ súng của tháp canh), pháo 30 mm (IFV, APC tinh nhuệ), pháo đôi BMPT, Vikhr của Ka-52, tên lửa của boss.
- **Nhịp bắn:** cơ chế băng đạn mới (bắn liên tục theo mục tiêu rồi thay băng), DPS giữ như cũ.

| Tên lửa | Tốc độ (m/s) | Thời gian bay |
|---|---|---|
| Tên lửa chống tăng (TOW, Ataka...) | 36 → 24 | 0,94 → 1,42 s ở 34 m |
| Kornet | 38 → 25 | 1,32 → 2,0 s ở 50 m |
| Hellfire và cùng lớp | 45 → 30 | 0,76 → 1,13 s ở 34 m |
| Vikhr (Ka-52) | 50 → 34 | 1,1 → 1,62 s ở 55 m |
| Maverick, Kh-29 | 50 → 32 | 0,8 → 1,25 s ở 40 m |
| Phòng không tầm ngắn (SAM, Stinger, Igla-V) | 60 → 40 | 0,73 → 1,1 s ở 44 m |
| Phòng không tầm xa | 72 → 46 | 1,39 → 2,17 s ở 100 m |
| 48N6 | 95 → 62 | 1,0 → 1,53 s |
| Không đối không (AIM-9, R-60...) | 74 → 48 | 0,81 → 1,25 s ở 60 m |
| Tên lửa hành trình, JASSM | 30 → 20 | 3,7 → 5,5 s ở 110 m |
| Rocket bắn thẳng (6 loại) | 75 → 60 | 0,45 → 0,57 s ở 34 m |

| Vũ khí | Trước | Sau | DPS |
|---|---|---|---|
| Pháo máy bay cường kích | loạt 10 viên, hồi 3,57 s | luồng 20 viên/s, băng 70, thay 1 s | 101 → 100 |
| Gatling GAU (A-10) | loạt 14 viên | luồng 25 viên/s, băng 90, thay 1 s | 190 → 190 |
| Pháo tiêm kích | loạt 8 viên | luồng 20 viên/s, băng 70, thay 1 s | 54 → 54,5 |
| GSh-30K | loạt 6 viên | luồng 12,5 viên/s, băng 30, thay 1,2 s | 73,8 → 73,7 |
| Pháo 25 mm máy bay pháo | súng máy | luồng 16,7 viên/s, băng 50, thay 1,2 s | 45 → 45 |
| Pháo tự động 25 mm (xe bọc thép) | loạt 3, hồi 1,29 s | luồng 5 viên/s, băng 12, thay 1,6 s | 44 → 46,5 |
| Pháo tự động 30 mm (IFV) | loạt 3 | luồng 5 viên/s, băng 10, thay 1,8 s | 52,8 → 59,7 |
| Pháo đôi 30 mm (BMPT) | loạt 4 | luồng 6,7 viên/s, băng 16, thay 1,6 s | 74 → 84,5 |
| Súng máy | hồi 0,16–0,22 s | hồi 0,1–0,13 s, viên nhẹ hơn | gần như giữ nguyên |

Máy bay cường kích bắn một luồng 1–1,4 giây mỗi lượt bổ nhào (trước 0,45–0,55 s); muốn đủ 3–4 giây mỗi lượt cần tầm pháo xa hơn hoặc bổ nhào chậm hơn: chờ chủ dự án quyết.

#### Vụ nổ, lửa, laser

- **Nổ đạn tăng:** công thức riêng (chớp sáng, cầu lửa và cầu lửa thứ hai, tia lửa, khói đen, bụi, mảnh kim loại); tăng nhẹ ×1,3, tăng chủ lực và diệt tăng ×1,4, tăng nặng và siêu nặng ×1,5.
- **Bom:** GBU-12, bom chùm, napalm ×1,3; ném bom rải thảm ×1,45; FAB-500, JDAM, Mk 84 ×1,5. Tên lửa hành trình và MOAB: vòng sóng xung kích bằng đúng bán kính sát thương (18 m và 27 m).
- **Giữ chất lượng khi phóng to:** thêm nhiều hạt hơn thay vì phóng to từng hạt (khung ảnh 128 px), chớp sáng không còn bị mặt đất cắt; đồ họa Thấp giữ 40% phần hạt thêm.
- **Xe phun lửa:** luồng lửa cam dày loang dần, cầu lửa napalm phồng khi bay và bốc lên ở mục tiêu, lửa đứng thẳng, hơi nóng, than hồng, khói đen dày hơn.
- **Iron Beam:** tia la-de liên tục có lõi trắng, quầng đỏ cam, nạp năng lượng 0,22 s, điểm cháy trắng, tia lửa và giọt kim loại nóng chảy, lưu sáng 0,28 s.

#### Menu, âm thanh, clip Xem bắn

- **Giật lúc mở game:** màn chờ chưa hiện ở lần mở đầu tiên nên người chơi thấy quá trình dựng (khung đầu 3,2 giây). Giờ màn chờ che từ khung đầu, âm thanh nạp trước; 5 giây đầu sau màn chờ không khung nào quá 33 ms (đo trên editor).
- **Nhạc:** một trình phát nhạc cho cả phiên, chuyển bài có crossfade 2 giây; menu không còn tiếng súng nổ của trận nền (chỉ gió nhẹ); clip Xem bắn nhỏ tiếng hơn và hạ nhạc.
- **Clip Xem bắn thể hiện kỹ năng đặc biệt:**

| Phương tiện | Clip cho thấy |
|---|---|
| Xe gây nhiễu | tên lửa của địch bắn vào xe tăng bên cạnh bị mất khóa, bay lệch; vòng tím nhấp nháy |
| Iron Beam | đốt rơi rocket và tên lửa bắn vào xe nó bảo vệ; bắn cả trực thăng |
| Xe công binh | sửa hai xe tăng bị thương |
| Xe đặc công | gia cố tháp canh bị hỏng |
| Xe chỉ huy | xe tăng trong vùng hào quang bắn nhanh hơn; vòng vàng |
| Radar phản pháo | cối địch bắn là bị lộ (chấm đỏ), cối ta bắn trả |
| Xe ủi bọc thép | ủi phẳng một hàng răng rồng |
| Máy bay, trực thăng | xe phòng không địch bắn, pháo sáng kéo tên lửa đi |
| IFV, xe thả khói | địch áp sát thì thả màn khói |
| Drone trinh sát | đánh dấu mọi mục tiêu thấy được |
| EMP, vòm khiên | EMP làm im xe tăng đang bắn; vòm khiên đỡ đạn cho xe bên trong |

Sheet: 12_he_thong_trang_thai/Test — Test (224 dòng, 7 cột)

| id | nhom | so_test | lop | ket_qua |
|---|---|---|---|---|
| EditMode/AbilityTests.cs | EditMode | 7 | AbilityTests | KHONG_CHAY |
| EditMode/AiModeProfileTests.cs | EditMode | 12 | AiModeProfileTests | KHONG_CHAY |
| EditMode/AiParamSweep.cs | EditMode | 1 | AiParamSweep;Result | KHONG_CHAY |
| EditMode/AiReviewTests.cs | EditMode | 8 | AiReviewTests | KHONG_CHAY |
| EditMode/AiScenarioTests.cs | EditMode | 17 | AiScenarioTests | KHONG_CHAY |
| EditMode/AiTests.cs | EditMode | 5 | AiTests | KHONG_CHAY |
| EditMode/AirAndTowerTests.cs | EditMode | 4 | AirAndTowerTests | KHONG_CHAY |
| EditMode/AirAttackMeasure.cs | EditMode | 3 | AirAttackMeasure | KHONG_CHAY |
| EditMode/AirAttackTests.cs | EditMode | 4 | AirAttackTests;Log | KHONG_CHAY |
| EditMode/AirMotionTests.cs | EditMode | 1 | AirMotionTests;Meter | KHONG_CHAY |
| EditMode/AirRealismTests.cs | EditMode | 4 | AirRealismTests | KHONG_CHAY |
| EditMode/AircraftReturnTests.cs | EditMode | 2 | AircraftReturnTests | KHONG_CHAY |
| EditMode/AircraftTests.cs | EditMode | 4 | AircraftTests | KHONG_CHAY |
| EditMode/ApsTests.cs | EditMode | 1 | ApsTests | KHONG_CHAY |
| EditMode/ArmourBalanceMeasure.cs | EditMode | 1 | ArmourBalanceMeasure;Matchup;RunResult;Tally | KHONG_CHAY |

*15 / 224 dòng đầu: xem sheet 12_he_thong_trang_thai/Test.*

Sheet: 12_he_thong_trang_thai/Validator — Validator (13 dòng, 5 cột)

| id | muc_dich | lan_chay |
|---|---|---|
| Tools/assets/glb_check.py | Prompt 27 step 2: the GLB baseline and machine validator (s… | KHONG_CHAY |
| Tools/audit/map_audit.py | Prompt 30 L8: the static map audit (sheet "Đo bản đồ"). Rea… | KHONG_CHAY |
| Tools/audit/mode_static_audit.py | Prompt 30 L8: the static mode audit (sheet "Chế độ"): four… | KHONG_CHAY |
| Tools/balance/fix_validate.py | Full fix prompt L9: the validators for items 1-6 and 8 in o… | KHONG_CHAY |
| Tools/balance/full_weapon_audit.py | Full fix prompt L1: the audit of every weapon (DECISIONS "S… | KHONG_CHAY |
| Tools/balance/p32_base_audit.py | Prompt 32 L9: the base system's static audits (no simulatio… | KHONG_CHAY |
| Tools/balance/p34_validate.py | Prompt 34 L9: the six validators in one run (DECISIONS "Pro… | KHONG_CHAY |
| Tools/balance/target_mask_check.py | Prompt 29 appendix: the weapon target-mask check, read stat… | KHONG_CHAY |
| Tools/blender/check_hd.py | blender -b --python check_hd.py -- <normal_dir> <hd_dir> <n… | KHONG_CHAY |
| Tools/blender/check_muzzles.py | blender -b --python Tools/blender/check_muzzles.py -- <name… | KHONG_CHAY |
| Tools/blender/specs/validate_specs.py | Prompt 35 section 4: check the build specs (Tools/blender/s… | KHONG_CHAY |
| Tools/maps/check_access.py | Access for the biggest hull (prompt 12 C.2): on a map file… | KHONG_CHAY |
| Tools/maps/validate_p33.py | Prompt 33 L7: the twelve map validators (DECISIONS "Prompt… | KHONG_CHAY |

Sheet: 12_he_thong_trang_thai/Kiem_tra_file — Kiểm tra: file báo cáo (27 dòng, 7 cột)

| id | loai | kich_thuoc_byte | tieu_de | sha256 |
|---|---|---|---|---|
| aa_multipliers.md | md | 733 | C10: anti-air multipliers against aircraft (prompt 29, read… | 4617aac6a692d58f09f3dfcb86e9b2692ea60de54aceb6fb2cd38d2aa14… |
| aircraft_rtb.md | md | 832 | C12: aircraft returning on low health (prompt 29, read only) | 46fd789b2334451143220230e8d9cebd6c72b92a68a81bd0797576f1bb3… |
| aoe_list.md | md | 1768 | C16: AoE list against main weapons with splash (prompt 29,… | 7a255d3fc249958d67c90da4c6edea527f09148878efe46117675c4232f… |
| aps_audit.md | md | 2258 | C06 + C07: APS audit (prompt 29, read only) | 63b6a4ac77f769c451fa27769ecd0480feec7dcaaa1af66362cfe573dcf… |
| attack_flags.md | md | 1173 | C13: attack capability flags (prompt 29, read only) | ec469bca569d2ce8955e12edf72650ed0a78b0abc6864f9484d744c9007… |
| base_overlap.md | md | 3586 | Base system overlaps (prompt 32 L9, static) | 6ad74a871701dab04bcd3d72333eb5330d51900bd83db6afda89c2aebac… |
| base_perf.md | md | 2709 | Base system performance (prompt 32 L9, static) | 1b47199b2defd95f0ce612bd963db371d5dbd989fefa76dc158705981f9… |
| boss_hunt.md | md | 1136 | C11: Boss Hunt after the Gungnir becomes a main boss (promp… | b2293e0a955075e4fd8da5fb8c9b34db5dcac7166650ed4debdb5f19a04… |
| fix_precheck.md | md | 5620 | Full fix prompt, pass 0: precheck (lane A, 2026-10-02) | 2168674e5c7474f93b76db600b2c7615086e75f7a1ef1ffbbcf49380676… |
| fix_validate.json | json | 125636 | models;note;recordedRateFlags;weapons | 07a2fc500b5ed34b1ecdc46e6d256d1527ece803952003a1fab8b6ffa22… |
| flare_baseline.md | md | 649 | C05: flare baseline (prompt 29, read only) | 1b71525d2983816200335d6ae4b40d75198f0acf6c22ca7e4d88228fe65… |
| full_weapon_audit.md | md | 83313 | Full weapon audit (full fix prompt L1) | 17a5af783b2fda0abef22b4dff0d13a3b9efe908b911c9f5ba0e296bee7… |
| map_audit.csv | csv | 15098 |  | 5bc309a280fa71f11929d43d948840e24750004b25c45d32e67022bcf5c… |
| map_audit.md | md | 10758 | Map audit (prompt 30 L8, static, read-only) | e41546d86905ad21ca37a1fee5b1516a67345d53e6b2e1919d6424937c6… |
| mode_static_audit.md | md | 5781 | Mode static audit (prompt 30 L8, theory only) | 95a3592a7329aad9faad25b97313a15b95c44dac946c40668e9d8c26189… |
| munition_behavior.md | md | 6992 | Munition behaviour (fix prompt L4 step 1, read from the cod… | d8f86159b4496584f7fcb3257586c1cd99c4cf055819588a8a611e48198… |
| p30_precheck.md | md | 4979 | Prompt 30 pass 0: precheck (read only) | 6876571fdb1e302eef029e27553b8b137c229e32e60fa195bd0169fd0da… |
| p31_precheck.md | md | 7339 | Prompt 31 pass 0: precheck (read only, 2026-10-02) | 220e2c4d7174129c637124223546c5d43a76f7a532259cb5881d56adff7… |
| p32_precheck.md | md | 4010 | Prompt 32 L0: precheck (2026-10-02, lead pass) | 1b7fe6d5ca36e95c8cf06a01189efdab12826b2de9e44b32b64fa0b40d8… |
| p33_precheck.md | md | 5587 | Prompt 33 L0: precheck (2026-10-02, lead pass) | 403bef1f1ad74cb9232317b101ef65d320d057482d8c6b1880b29bfbc98… |
| p34_precheck.md | md | 6080 | Prompt 34 pass 0: precheck (read only, 2026-10-02) | 42d76bade53bc82af44ce0cbb639aba34caea0fb44139450c1fcc7e827d… |
| player_weapon_family.md | md | 4770 | Player weapon families: the deviations (prompt 34 L1) | 7a2d5af543f515e575009360b6abdc49286285b4999bf3526941c0ac959… |
| runtime_cost.md | md | 598 | C15: where the discounted (runtime) call cost is used (prom… | 9c6c19377a5ebdd27ddb433035e85400dcf352ab1c4ace92a250f4a4d22… |
| showdown_static.md | md | 2863 | Showdown: static base-break estimate (prompt 32 L7) | a9c196db6a8d49acca19ee71c2285a75f301042e86e09711eaf3f79269e… |
| target_mask.md | md | 2795 | Target-mask check (prompt 29 appendix) | fb32bc38eb6c389ef9594f9d4842f83c9c3d44cb6b09b0b75d956abb8cc… |
| weapon_map.md | md | 1164 | C09: vehicle-weapon mapping (prompt 29, read only) | b9c36d235809deb81cfeb86b4a0a815dc09b17bb5967b3fe0ae479ab8d5… |
| zero_cp.md | md | 1442 | C03: zero-CP cards (prompt 29, read only) | 16a7bdb8d7fca38d665426a7b690892a3ca772518c4f747b1152e638ae4… |

## P1. Hằng số trong mã

Trạng thái: Đã áp

Nguồn dữ liệu: 12_he_thong_trang_thai/Hang_so_trong_ma.

Sheet: 12_he_thong_trang_thai/Hang_so_trong_ma — Hằng số trong mã (7249 dòng, 13 cột)

| id | tep | dong | ten | gia_tri | ngu_canh | loai | nhom | linh_vuc | de_xuat_dua_ra_du_lieu |
|---|---|---|---|---|---|---|---|---|---|
| Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.cs:20:26 | Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.… | 20 | Ambient | 10 | public const int Ambient = 10; | const | khac | 09 | khong |
| Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.cs:23:26 | Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.… | 23 | SmallArms | 20 | public const int SmallArms = 20; | const | khac | 09 | khong |
| Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.cs:26:26 | Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.… | 26 | FarShot | 25 | public const int FarShot = 25; | const | khac | 09 | khong |
| Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.cs:29:26 | Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.… | 29 | FarBlast | 30 | public const int FarBlast = 30; | const | sat_thuong | 09 | khong |
| Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.cs:32:26 | Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.… | 32 | NearShot | 40 | public const int NearShot = 40; | const | khac | 09 | khong |
| Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.cs:35:26 | Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.… | 35 | NearBlast | 50 | public const int NearBlast = 50; | const | sat_thuong | 09 | khong |
| Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.cs:38:26 | Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.… | 38 | Boss | 60 | public const int Boss = 60; | const | khac | 09 | khong |
| Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.cs:41:26 | Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.… | 41 | Warning | 70 | public const int Warning = 70; | const | thoi_gian | 09 | khong |
| Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.cs:65:28 | Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.… | 65 | EffectVoices | 24 | internal const int EffectVoices = 24; | const | khac | 09 | khong |
| Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.cs:68:30 | Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.… | 68 | OffScreenGain | 0.85 | internal const float OffScreenGain = 0.85f; | const | khac | 09 | khong |
| Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.cs:71:30 | Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.… | 71 | ClusterRadius | 20f, ClusterWindow = 0.5f | internal const float ClusterRadius = 20f, ClusterWindow = 0… | const | ban_kinh | 09 | khong |
| Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.cs:74:28 | Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.… | 74 | ClusterFrom | 3 | internal const int ClusterFrom = 3; | const | khac | 09 | khong |
| Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.cs:77:30 | Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.… | 77 | NearShare | 0.45 | internal const float NearShare = 0.45f; | const | nguong | 09 | khong |
| Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.cs:80:30 | Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.… | 80 | CompressorAttack | 0.03f, CompressorRelease = 0.3f | internal const float CompressorAttack = 0.03f, CompressorRe… | const | khac | 09 | khong |
| Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.cs:260:28 | Assets/MachineBrigade/Scripts/Game/Audio/AudioDirector.P34.… | 260 | BurstVoices | 3 | internal const int BurstVoices = 3; | const | khac | 09 | khong |

*15 / 7249 dòng đầu: xem sheet 12_he_thong_trang_thai/Hang_so_trong_ma; in 10 / 13 cột; 1 cột khác (và raw_json, nguon): xem sheet.*

## P2. Lịch sử đo

Trạng thái: Đã áp

Nguồn dữ liệu: 12_he_thong_trang_thai/Lich_su_do. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §Phụ lục: Lịch sử đo.

Các bảng đo dưới đây đo trên dữ liệu hoặc luật khác bản hiện tại (prompt 29 R10). Bảng 9b: không có dấu hash (đo trước prompt 29). Bảng 2b: đo tay ở prompt 13, không có dấu hash.

Sheet: 12_he_thong_trang_thai/Lich_su_do — Lịch sử đo (5739 dòng, 10 cột)

| id | khoa | gia_tri_so | gia_tri_chu | don_vi | stale | commit_do |
|---|---|---|---|---|---|---|
| fix_boss_before.argus[0].air | air | FALSE |  |  | STALE | 3854ce5d |
| fix_boss_before.argus[0].barrels | barrels | 1 |  |  | STALE | 3854ce5d |
| fix_boss_before.argus[0].core | core | 10 |  | m | STALE | 3854ce5d |
| fix_boss_before.argus[0].cycle | cycle | 35.440000000000005 |  |  | STALE | 3854ce5d |
| fix_boss_before.argus[0].damage | damage | 700 |  |  | STALE | 3854ce5d |
| fix_boss_before.argus[0].dps | dps | 158.01354401805867 |  |  | STALE | 3854ce5d |
| fix_boss_before.argus[0].edge | edge | 20 |  | m | STALE | 3854ce5d |
| fix_boss_before.argus[0].fam | fam |  | bomb_400 |  | STALE | 3854ce5d |
| fix_boss_before.argus[0].id | id |  | p26_roc_main_roc_bombs |  | STALE | 3854ce5d |
| fix_boss_before.argus[0].laid | laid | FALSE |  |  | STALE | 3854ce5d |
| fix_boss_before.argus[0].mount | mount | 0 |  |  | STALE | 3854ce5d |
| fix_boss_before.argus[0].n | n | 8 |  |  | STALE | 3854ce5d |
| fix_boss_before.argus[0].real | real |  | bomb-bay stick 400 kg |  | STALE | 3854ce5d |
| fix_boss_before.argus[0].sim | sim | FALSE |  |  | STALE | 3854ce5d |
| fix_boss_before.argus[1].air | air | FALSE |  |  | STALE | 3854ce5d |

*15 / 5739 dòng đầu: xem sheet 12_he_thong_trang_thai/Lich_su_do.*

## P3. Quyết định và chờ quyết

Trạng thái: Đã áp

Nguồn dữ liệu: 12_he_thong_trang_thai/DECISIONS; 12_he_thong_trang_thai/Cho_quyet.

Sheet: 12_he_thong_trang_thai/DECISIONS — DECISIONS (708 dòng, 7 cột)

| id | cap | tieu_de | dong | muc_cha |
|---|---|---|---|---|
| D0001 | 2 | 1. Bases as a loadout | 7 |  |
| D0002 | 2 | 2. Roster cleanup and balance | 50 |  |
| D0003 | 2 | 5. Multi-stage missions and big battles | 155 |  |
| D0004 | 2 | 6. Operations and the menu groups | 277 |  |
| D0005 | 2 | 7. Sized slots (the supplementary prompt; replaces fortific… | 351 |  |
| D0006 | 2 | 3. Towers: cards, branches | 385 |  |
| D0007 | 2 | 3D. Tower equipment | 532 |  |
| D0008 | 2 | 3F. Base loadout screen | 596 |  |
| D0009 | 2 | 4M. New battlefields | 664 |  |
| D0010 | 2 | 5L. Vehicle LOD and impostors | 742 |  |
| D0011 | 2 | 4. Campaign | 826 |  |
| D0012 | 2 | 5S. Siege and Defend upgrades | 1003 |  |
| D0013 | 2 | 8. New content, elites and equipment | 1132 |  |
| D0014 | 3 | A. Vehicles | 1141 | D0013 |
| D0015 | 3 | B. New base types (values at Legendary, top level; the lowe… | 1173 | D0013 |

*15 / 708 dòng đầu: xem sheet 12_he_thong_trang_thai/DECISIONS.*

Sheet: 12_he_thong_trang_thai/Cho_quyet — Chờ quyết (146 dòng, 6 cột)

| id | dong | muc | noi_dung |
|---|---|---|---|
| Q0001 | 174 | D0003 | The commanders are set up for each stage's goal (hold leash… |
| Q0002 | 526 | D0006 | Most towers hold every fight. The C-RAM and the artillery e… |
| Q0003 | 627 | D0008 | - **Empty slots stay empty.** A loadout list may now hold a… |
| Q0004 | 842 | D0011 | anything back. A won mission is always open. In this build… |
| Q0005 | 1028 | D0012 | every wall down, and warns if the walls would not hold with… |
| Q0006 | 1046 | D0012 | hurt, and the keep's towers hold their fire (`Vehicle.HoldF… |
| Q0007 | 1155 | D0014 | under the same fire: equal under mixed fire (33.3 s a life… |
| Q0008 | 1526 | D0028 | (44 pt touch targets, 11-12 pt body text) only hold if the… |
| Q0009 | 1634 | D0028 | 80 px and 664 texts under 19 px (none cut there); the Hud C… |
| Q0010 | 1636 | D0028 | hold English words (mostly weapon and model names such as r… |
| Q0011 | 2754 | D0050 | pass waits for the owner's call on reach or the dive (11C).… |
| Q0012 | 2868 | D0054 | - **Any other jet crawls.** It slows to a pace that brings… |
| Q0013 | 2873 | D0054 | easing off from 1.5x its reach so it arrives at half speed;… |
| Q0014 | 2875 | D0054 | - **Inside a flak gun's reach (+6 m) it never hangs** (the… |
| Q0015 | 2876 | D0054 | becomes a half-speed run, over the target in about a second… |

*15 / 146 dòng đầu: xem sheet 12_he_thong_trang_thai/Cho_quyet.*

## P4. Trạng thái prompt, validator, manifest và save

Trạng thái: Một phần — chờ prompt xuat_luot8 (sheet Trang_thai_prompt)

Nguồn dữ liệu: 12_he_thong_trang_thai/Trang_thai_prompt; 12_he_thong_trang_thai/Validator_model; 12_he_thong_trang_thai/Validator_vu_khi; 12_he_thong_trang_thai/Manifest_ap; 12_he_thong_trang_thai/Chuyen_doi_save; 12_he_thong_trang_thai/Khac_chua_phan_loai.

Sheet: 12_he_thong_trang_thai/Trang_thai_prompt — Trạng thái prompt (28 dòng, 9 cột)

| id | chu_de | trang_thai_nguyen_van | trang_thai | file_prompt | commit_dau_cuoi | test |
|---|---|---|---|---|---|---|
| 0 | shared context and working rules | standing | Da_chay | prompt00_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| 1 to 7 | bases, roster, towers, campaign, multi-stage missions, Oper… | done | Da_chay | prompt01_vi.txt;prompt02_vi.txt;prompt03_vi.txt;prompt04_vi… | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| 8 to 15 | content, boss parts, UI 2.0, compact HUD, stuck vehicles, b… | done | Da_chay | prompt08_vi.txt;prompt09_vi.txt;prompt10_vi.txt;prompt11_vi… | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| 16 | Lighthouse Bay, Leviathan and fleet, old-boss weapons, esco… | done | Da_chay | prompt16_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| 17 | long maps, layered bases, roster merges, new units | done | Da_chay | prompt17_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| 18 | a big attack for every boss | done | Da_chay | prompt18_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| 19 | the Silver Bug rebuilt as an orbital spacecraft: altitude t… | done | Da_chay | prompt19_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| 20 | 12-chapter campaign, main and mini bosses, renames, Boss Hu… | done | Da_chay | prompt20_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| 21 | Sandbox mode, full Vietnamese and English | done | Da_chay | prompt21_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| 22 | the full story, non-Vietnamese proper names, 12 chapters +… | done (v0.30.0) | Da_chay | prompt22_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| 23 | data-driven mission events (reinforcements by difficulty, f… | done (v0.31.0; balance runs wait for the test phase) | Da_chay | prompt23_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| 24 | camouflage and real-model skins (with a reserved list of re… | skipped for now (owner, 2026-09-30) | Chua | prompt24_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| 25 | apply the balance spreadsheet Docs/balance/Machine_Brigade_… | done 2026-10-01 but the PDF (92 of 93 new items; dx23 dropp… | Mot_phan | prompt25_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| 26 | boss health by time-to-kill, boss weapons with two-layer bl… | started 2026-10-01 in a reduced scope (DECISIONS "26 scope") | Mot_phan | prompt26_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| 27 | REPLACED 2026-10-01 by prompt27_v2_en.md (owner, English):… | on hold until the owner asks | Chua | prompt27_v2_en.md;prompt27_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| 28 | Redo the AI in three layers (AI general, squad, unit) on a… | queued: after prompt 27, when the owner asks (its "run all… | Da_chay | prompt28_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| 29 | Apply balance round 2 (v2) by the manifest of Docs/balance/… | 2026-10-02: given to a Claude cloud session (Docs/CLOUD_HAN… | Chua | prompt29_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| 30 | In-battle storytelling (portrait strip, P0-P4 dialogue queu… | 2026-10-02: given to the cloud after the prompt 28 appendix… | Chua | prompt30_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| 31 | Fixed-deck game missions (23), placed allies, loaned cards,… | 2026-10-02: queued for the cloud after prompt 30; deck scre… | Da_chay | prompt31_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| 32 | Base system: tower roster 32 -> 22 with the two-branch rule… | 2026-10-02: done locally (two lanes, Docs/LOCAL_PLAN_P31_P3… | Da_chay | prompt32_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| 33 | Maps: four zones (play, edge band, outer ring, horizon), ed… | 2026-10-02: queued locally after 31 L3 and 32 L3 (navigatio… | Chua | prompt33_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| 34 | Boss weapons by family and calibre (per-shot damage up, cyc… | 2026-10-02: done locally, lane C | Da_chay | prompt34_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| balance-after-p18_vi.txt | spec ngoài bảng prompt |  | Chua | balance-after-p18_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| doc-review-update_vi.txt | spec ngoài bảng prompt |  | Chua | doc-review-update_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| export_full_vi.txt | spec ngoài bảng prompt |  | Chua | export_full_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| fix_full_vi.txt | spec ngoài bảng prompt |  | Chua | fix_full_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| requests_vi.md | spec ngoài bảng prompt |  | Chua | requests_vi.md | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |
| tower-branches_vi.txt | spec ngoài bảng prompt |  | Chua | tower-branches_vi.txt | CHUA_AP:prompt_xuat_luot8 | KHONG_CHAY |

Sheet: 12_he_thong_trang_thai/Validator_model — Validator: điểm model (230 dòng, 12 cột)

| id | model | budget | budget_status | class | lod1_share | parts_missing | static_grade | triangles | visual_grade |
|---|---|---|---|---|---|---|---|---|---|
| aa_57mm_vehicle | aa_57mm_vehicle | 4000-7000 | ok | tracked | 0.5 | mantlet;idler;roof_mg;stowage | Kém | 6028 | Tốt |
| aa_gun_tower | aa_gun_tower | 2000-4000 | under | tower | 0.588 |  | Cần sửa | 1724 | Cần sửa |
| aa_gun_vehicle | aa_gun_vehicle | 4000-7000 | under | tracked | 0.556 | mantlet;idler;skirts;sight;roof_mg;smoke;stowage | Kém | 3556 | Cần sửa |
| aa_turret | aa_turret | 2000-4000 | over | tower | 0.689 |  | Kém | 6306 | Tốt |
| aa_turret_a | aa_turret_a | 2000-4000 | over | tower | 0.674 |  | Kém | 6670 | Tốt |
| aa_turret_b | aa_turret_b | 2000-4000 | ok | tower | 0.619 |  | Tốt | 2610 | Tốt |
| aa_vehicle | aa_vehicle | 4000-7000 | ok | tracked | 0.486 | mantlet;idler;sight;roof_mg;smoke;stowage | Kém | 4964 | Tốt |
| aerial_tanker | aerial_tanker | 4000-7000 | ok | jet | 0.35 | tail;exhaust;pylons;stores | Kém | 4164 | Tốt |
| airborne_light_tank | airborne_light_tank | 4000-7000 | ok | tracked | 0.448 | mantlet;idler;roof_mg;stowage | Kém | 5550 | Cần sửa |
| airborne_light_tank_chute | airborne_light_tank_chute | 0-7000 | ok | air_other | 0.344 |  | Cần sửa | 3514 | Tốt |
| airborne_vehicle | airborne_vehicle | 4000-7000 | under | tracked | 0.61 | mantlet;idler;skirts;sight;roof_mg;smoke;stowage | Kém | 3260 | Cần sửa |
| airborne_vehicle_chute | airborne_vehicle_chute | 0-7000 | ok | air_other | 0.293 |  | Cần sửa | 3262 | Tốt |
| ammo_carrier | ammo_carrier | 3000-5000 | ok | wheeled | 0.543 | axles | Cần sửa | 3388 | Tốt |
| ammo_dump | ammo_dump | 2000-4000 | over | tower | 0.524 | base;roof | Cần sửa | 5276 | Tốt |
| amphib_light_vehicle | amphib_light_vehicle | 4000-7000 | ok | tracked | 0.524 | mantlet;idler;skirts;roof_mg;smoke;stowage | Kém | 4606 | Cần sửa |

*15 / 230 dòng đầu: xem sheet 12_he_thong_trang_thai/Validator_model.*

Sheet: 12_he_thong_trang_thai/Validator_vu_khi — Validator: vũ khí (240 dòng, 9 cột)

| id | vu_khi | ly_do_da_ghi | cycle | flags | n | reason |
|---|---|---|---|---|---|---|
| aa_25_triple | aa_25_triple |  | 3.1 |  | 15 |  |
| agl_40 | agl_40 |  | 4.2 |  | 6 |  |
| aim9 | aim9 |  | 8.0 |  | 1 |  |
| air_cruise_missile | air_cruise_missile |  | 11.2 |  | 1 |  |
| air_to_air | air_to_air |  | 3.99 |  | 1 |  |
| amos_120 | amos_120 | the real reference is an estimate (no published launch inte… | 10.75 | TOO FAST | 4 | the real reference is an estimate (no published launch inte… |
| anti_radar_missile | anti_radar_missile |  | 8.0 |  | 1 |  |
| apkws_rocket | apkws_rocket |  | 1.0 |  | 1 |  |
| at_gun_100 | at_gun_100 |  | 5.0 |  | 1 |  |
| ataka | ataka |  | 11.42 |  | 2 |  |
| atgm | atgm |  | 12.33 |  | 1 |  |
| autocannon_25 | autocannon_25 |  | 2.634 |  | 8 |  |
| autocannon_30 | autocannon_30 |  | 2.611 |  | 10 |  |
| autocannon_40 | autocannon_40 |  | 3.52 |  | 10 |  |
| avenger_stingers | avenger_stingers | the real reference is an estimate (no published launch inte… | 18.5 | TOO FAST | 8 | the real reference is an estimate (no published launch inte… |

*15 / 240 dòng đầu: xem sheet 12_he_thong_trang_thai/Validator_vu_khi.*

Sheet: 12_he_thong_trang_thai/Manifest_ap — Kết quả áp manifest (prompt 29) (6 dòng, 5 cột)

| id | so_goi | goi |
|---|---|---|
| ALREADY_APPLIED (whole bundle) | 0 | (many B1 bundles had ALREADY_APPLIED rows: outgoingDamageMu… |
| BLOCKED | 0 |  |
| CONFLICT | 0 | (two false CONFLICT rows from re-checking B0 after B1 were… |
| OK (applied) | 128 data bundles + 9 code | E1; B0 x7; B1 x97 (sky_gunship last, pass 7); B2-FLR x17; B… |
| SKIPPED (HOLD) | 13 | E2, B5 x12 |
| SKIPPED (REJECT) | 7 | R-supergun, R-radar, R-floor, R-typhon, R-icarus, R-round-h… |

Sheet: 12_he_thong_trang_thai/Chuyen_doi_save — Chuyển đổi save cũ (55 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so | gia_tri_chu |
|---|---|---|---|---|
| migration22.moves.c1m07 | migration22 | c1m07 |  | c6m11 |
| migration22.moves.c1s2 | migration22 | c1s2 |  | c6m12 |
| migration22.moves.c7s2 | migration22 | c7s2 |  | c7m11 |
| migration22.moves.c11s2 | migration22 | c11s2 |  | c11m11 |
| migration.chaptersSeen["7"] | migration | 7 | 10 |  |
| migration.chaptersSeen["8"] | migration | 8 | 7 |  |
| migration.chaptersSeen["9"] | migration | 9 | 12 |  |
| migration.chaptersSeen["10"] | migration | 10 | 100 |  |
| migration.hq.c1m04 | migration | c1m04 | 1 |  |
| migration.hq.c3m05 | migration | c3m05 | 2 |  |
| migration.hq.c5m05 | migration | c5m05 | 3 |  |
| migration.hq.c7m05 | migration | c7m05 | 4 |  |
| migration.hq.c9m03 | migration | c9m03 | 5 |  |
| migration.moves.c1m05 | migration | c1m05 |  | c6m08 |
| migration.moves.c3m08 | migration | c3m08 |  | c6m05 |

*15 / 55 dòng đầu: xem sheet 12_he_thong_trang_thai/Chuyen_doi_save.*

Sheet: 12_he_thong_trang_thai/Khac_chua_phan_loai — Chưa phân loại chắc (9 dòng, 5 cột)

| id | noi_dat | ly_do |
|---|---|---|
| K01 | 12_he_thong_trang_thai/Test_kich_ban | kịch bản test sandbox, không phải dữ liệu game |
| K02 | 12_he_thong_trang_thai/Bang_don_vi_tai_lieu | bảng đơn vị của tài liệu cũ (mô tả chữ), không phải dữ liệu… |
| K03 | 11_meta_giao_dien/Anh_can_cu | ảnh căn cứ của giao diện; có thể thuộc 08 |
| K04 | 10_model_tai_san/Anh_the | ảnh thẻ render từ model; có thể thuộc 11 |
| K05 | 09_hieu_ung_am_thanh/Hau_ky_hinh_anh | hậu kỳ hình ảnh |
| K06 | 11_meta_giao_dien/So_tay_dan | xe mẫu của sổ tay đạn (giao diện) |
| K07 | 08_ban_do/Thoi_tiet | thời tiết: chiến dịch (07) hay bản đồ (08) |
| K08 | 05_che_do_kinh_te/Do_kho | biến cố theo độ khó: 05 hay 07 |
| K09 | 12_he_thong_trang_thai/Validator_* | kết quả validator; điểm model cũng là 10/Model_cham_diem (l… |

## P5. Mục lục bảng dữ liệu, sửa chữ theo mã và ảnh

Trạng thái: Đã áp

Nguồn dữ liệu: (không có sheet; chỉ văn bản).

#### Sửa chữ theo mã (spec 6)

| văn bản cũ (mẫu) | thay bằng | căn cứ trong mã / dữ liệu | số chỗ |
|---|---|---|---|
| Huyền thoại mở sau khi thắng chiến dịch lớn cuối cùng | Huyền thoại mở sau khi thắng c12m10 (màn kết của chương 12) | Operations.LegendMission = "c12m10" (Operations.cs) | 1 chỗ |
| tối đa 2 dòng, không chân dung, không lồng tiếng | tối đa 2 dòng, có chân dung nhỏ của người nói, không lồng tiếng | DialogueViews vẽ chân dung nhỏ trên dải thoại trong trận (fix L10 mục 14) | 1 chỗ |
| chỉ huy tự đưa chúng về khi dưới 35% máu hoặc hết đạn | chỉ huy tự đưa chúng về khi hết đạn | TacticalAi.Refit: không còn ngưỡng 35 % máu từ prompt 29 B3-AI (fix L10 mục 17) | 1 chỗ |
| phí duy trì | tiếp tế | thuật ngữ trong mã và chuỗi: tiếp tế (supply), fix L10 mục 16 | 1 chỗ |
| tháp canh thấy tàng hình và tăng 10% tầm cho tháp gần | tháp canh thấy tàng hình và tăng 10% tầm cho tháp trong 25 m (nhánh Tháp quan sát: 15% trong 30 m, thay mức 10%, không… | balance.json guard_tower.towerRangeAura {radius 25, range 0.1}, guard_tower.watch {radius 30, range 0.15}; chuỗi branch.guard_tower.watch.info | 1 chỗ |
| 15 chương trong 4 hồi | (giữ: đúng với mã) | campaign.json chapters[].act: 1-4 (4, 4, 4, 3 chương): đúng | 2 chỗ |
| C-RAM 30%, la-de 0% | (giữ: đúng với mã) | c_ram aps.shells 0.3, iron_beam / laser_ad_station aps.shells 0: đúng | 1 chỗ |
| không chặn đạn pháo | (giữ: đúng với mã) | laser_ad_station aps.shells 0 (Trạm la-de): đúng | 4 chỗ |

Bản PDF cũ: 102 bảng số bỏ (các sheet thay), 234 thẻ đơn vị bỏ (chỉ số ở sheet, lời hướng dẫn từ chuỗi), 308 ảnh ngoài repo bỏ.

## Các sheet khác của file

Mọi sheet chưa in ở mục trên (sheet input_<tên> là bản chép từ file khác, không in lại).

### Bang_don_vi_tai_lieu

Trạng thái: Đã áp

Nguồn dữ liệu: 12_he_thong_trang_thai/Bang_don_vi_tai_lieu.

Sheet: 12_he_thong_trang_thai/Bang_don_vi_tai_lieu — Bảng đơn vị của tài liệu (152 dòng, 7 cột)

| id | description | shape | sheet | unlock |
|---|---|---|---|---|
| aa_turret | pháo đôi 30 mm cao xạ tới 42 m và tên lửa phòng không (44 m… | Ụ bao cát tròn với pháo phòng không 2 nòng trên bệ xoay và… | Công trình |  |
| aa_turret.flak |  | Ụ bao cát tròn với pháo phòng không 2 nòng trên bệ xoay và… | Công trình |  |
| aa_turret.sam |  | Ụ bao cát tròn với pháo phòng không 2 nòng trên bệ xoay và… | Công trình |  |
| aa_vehicle | pháo đôi 35 mm cao xạ (36 m) bắn khi đang chạy, kèm tên lửa… | Khung xích, tháp vuông với 2 pháo 35 mm hai bên tháp, radar… | Phương tiện | Chương 2 |
| airfield | máy bay bay trên nó hồi 3% máu mỗi giây và nạp đạn; chỉ huy… | Bãi đáp bê tông phẳng có vạch sơn và đèn. Kích thước hiện 1… | Công trình |  |
| airfield.hangar |  | Bãi đáp bê tông phẳng có vạch sơn và đèn. Nhánh: Nhà chứa m… | Công trình |  |
| airfield.service |  | Bãi đáp bê tông phẳng có vạch sơn và đèn. Nhánh: Xe tiếp nh… | Công trình |  |
| ammo_carrier | chỉ có súng máy nóc; bệ phóng và xe tên lửa hết đạn trong v… | Xe tải 8 bánh chở giá đạn kim loại mở, thùng đạn xếp tầng m… | Phương tiện | Chương 2 |
| ammo_depot | xe nạp đạn tại căn cứ nhanh gấp đôi. rất hợp với giàn phóng… | Nhà kho bán chìm có ụ đất, thùng đạn xếp ngoài. Kích thước… | Công trình |  |
| argus | khi nó còn, pháo binh địch tản mát chỉ khoảng một nửa; đòn… | Dựa trên: JLENS (khí cầu radar neo) · Kirov Airship (Red Al… | Boss |  |
| armored_bulldozer | chỉ có súng máy trên nóc; lưỡi ủi húc tháp, lô cốt và nhà c… | Xe ủi xích bọc thép hộp, lưỡi ủi rất lớn, ca-bin kính chống… | Phương tiện | Chương 4 |
| armored_car | pháo 25 mm vừa chạy vừa bắn cả đất lẫn trời, mạnh nhất với… | Xe 6 bánh lộ ngoài, thân hình hộp vát nghiêng phía trước, t… | Phương tiện | Có sẵn |
| armored_train | hai pháo nặng (42 m), hộp rốc-két, pháo cao xạ và súng máy;… | Dựa trên: tàu bọc thép Liên Xô BP-35, B-38 152 mm, 2B11 120… | Boss |  |
| artillery | dừng lại, nã ba quả đạn 155 mm nổ mạnh cầu vồng qua vật cản… | Lựu pháo tự hành xích (M109A7): tháp lớn vuông phía sau, nò… | Phương tiện | Chương 2 |
| artillery_emplacement | lựu pháo nã vào mục tiêu mặt đất cách 25–90 m mỗi khi phe t… | Lựu pháo kéo đặt trong ụ đất và bao cát hình chữ U. Kích th… | Công trình |  |

*15 / 152 dòng đầu: xem sheet 12_he_thong_trang_thai/Bang_don_vi_tai_lieu.*

### Bang_don_vi_tai_lieu_chung

Trạng thái: Đã áp

Nguồn dữ liệu: 12_he_thong_trang_thai/Bang_don_vi_tai_lieu_chung.

Sheet: 12_he_thong_trang_thai/Bang_don_vi_tai_lieu_chung — Bảng đơn vị: ghi chú (1 dòng, 8 cột)

| id | khoa | gia_tri_chu |
|---|---|---|
| _about | _about | Generated by Tools/docs/unit_sheet.py from Docs/balance/Mac… |

### Kiem_tra_ma

Trạng thái: Đã áp

Nguồn dữ liệu: 12_he_thong_trang_thai/Kiem_tra_ma.

Sheet: 12_he_thong_trang_thai/Kiem_tra_ma — Kiểm tra mã (CHECK) (16 dòng, 7 cột)

| id | ten | ket_qua | trang_thai | file |
|---|---|---|---|---|
| C01 | field map | every Manifest path mapped; new keys outgoingDamageMult, dr… | xong | Docs/balance_field_map.md |
| C02 | the 20 supply questions: needs reading the supply/refund/ca… |  | chua_lam |  |
| C03 | zero-CP cards | not bought by the AI; deck filter is UI (local); the suppor… | xong | Docs/checks/zero_cp.md |
| C04 | entity budget |  | chua_lam |  |
| C05 | flares | all 23 baselines match | xong | Docs/checks/flare_baseline.md |
| C06 | APS | one code path; bosses carry the same aps; classified, numbe… | xong | Docs/checks/aps_audit.md |
| C07 | iron_beam | 0.8 s in the data | xong | Docs/checks/aps_audit.md |
| C08 | tracing round 1's unplanned changes through git history |  | chua_lam |  |
| C09 | weapon map | exact ids only, no fuzzy match in the game | xong | Docs/checks/weapon_map.md |
| C10 | AA vs aircraft | x1.3 confirmed (Fragmentation x1.3, no overmatch on aircraf… | xong | Docs/checks/aa_multipliers.md |
| C11 | Boss Hunt | main-rank bosses count as mains: 17 / 24 | xong | Docs/checks/boss_hunt.md |
| C12 | aircraft return | one condition in TacticalAi.Refit; removed | xong | Docs/checks/aircraft_rtb.md |
| C13 | attack flags | none stored; S05 adds overrides | xong | Docs/checks/attack_flags.md |
| C14 | role metrics for cheap cards |  | chua_lam |  |
| C15 | runtime cost | spend/afford only; one classification (AI shares) moved to… | xong | Docs/checks/runtime_cost.md |
| C16 | AoE list | 3 listed without splash (missile blasts), 28 splash weapons… | xong | Docs/checks/aoe_list.md |

### Manifest_ap_goi

Trạng thái: Đã áp

Nguồn dữ liệu: 12_he_thong_trang_thai/Manifest_ap_goi.

Sheet: 12_he_thong_trang_thai/Manifest_ap_goi — Manifest: gói đã áp (129 dòng, 4 cột)

| id | goi |
|---|---|
| B0-engineer_vehicle | B0-engineer_vehicle |
| B0-flame_tank | B0-flame_tank |
| B0-light_tank | B0-light_tank |
| B0-siege_tank | B0-siege_tank |
| B0-sky_gunship | B0-sky_gunship |
| B0-thermobaric_launcher | B0-thermobaric_launcher |
| B0-vbied | B0-vbied |
| B1-aa_57mm_vehicle | B1-aa_57mm_vehicle |
| B1-aa_gun_vehicle | B1-aa_gun_vehicle |
| B1-aa_vehicle | B1-aa_vehicle |
| B1-aerial_tanker | B1-aerial_tanker |
| B1-airborne_light_tank | B1-airborne_light_tank |
| B1-airborne_vehicle | B1-airborne_vehicle |
| B1-ammo_carrier | B1-ammo_carrier |
| B1-amphib_light_vehicle | B1-amphib_light_vehicle |

*15 / 129 dòng đầu: xem sheet 12_he_thong_trang_thai/Manifest_ap_goi.*

### Test_kich_ban

Trạng thái: Đã áp

Nguồn dữ liệu: 12_he_thong_trang_thai/Test_kich_ban.

Sheet: 12_he_thong_trang_thai/Test_kich_ban — Test: kịch bản (1 dòng, 13 cột)

| id | difficulty | fog | format | limit | map | name | night | seed | version |
|---|---|---|---|---|---|---|---|---|---|
| platoon_beats_light_tank | Normal | FALSE | machine-brigade-sandbox | 0 | sandbox_flat | platoon_beats_light_tank | FALSE | 21 | 2 |

*in 10 / 13 cột; 1 cột khác (và raw_json, nguon): xem sheet.*

### Test_kich_ban_checks

Trạng thái: Đã áp

Nguồn dữ liệu: 12_he_thong_trang_thai/Test_kich_ban_checks.

Sheet: 12_he_thong_trang_thai/Test_kich_ban_checks — Kịch bản: checks (2 dòng, 8 cột)

| id | test_kich_ban_id | thu_tu | kind | seconds_s | team |
|---|---|---|---|---|---|
| platoon_beats_light_tank/0 | platoon_beats_light_tank | 0 | win | 60 | 0 |
| platoon_beats_light_tank/1 | platoon_beats_light_tank | 1 | noStuck | 60 | 0 |

### Test_kich_ban_sides

Trạng thái: Đã áp

Nguồn dữ liệu: 12_he_thong_trang_thai/Test_kich_ban_sides.

Sheet: 12_he_thong_trang_thai/Test_kich_ban_sides — Kịch bản: sides (2 dòng, 14 cột)

| id | test_kich_ban_id | thu_tu | ai | base | base_level | cooldowns | cp | immortal | income |
|---|---|---|---|---|---|---|---|---|---|
| platoon_beats_light_tank/0 | platoon_beats_light_tank | 0 | Combat | None | Normal | TRUE | -1 | FALSE | 1 |
| platoon_beats_light_tank/1 | platoon_beats_light_tank | 1 | Combat | None | Normal | TRUE | -1 | FALSE | 1 |

### Test_kich_ban_units

Trạng thái: Đã áp

Nguồn dữ liệu: 12_he_thong_trang_thai/Test_kich_ban_units.

Sheet: 12_he_thong_trang_thai/Test_kich_ban_units — Kịch bản: units (4 dòng, 10 cột)

| id | test_kich_ban_id | thu_tu | def | heading_deg | team | x_m | y_m |
|---|---|---|---|---|---|---|---|
| platoon_beats_light_tank/0 | platoon_beats_light_tank | 0 | main_battle_tank | 0 | 0 | -10 | -30 |
| platoon_beats_light_tank/1 | platoon_beats_light_tank | 1 | main_battle_tank | 0 | 0 | 0 | -30 |
| platoon_beats_light_tank/2 | platoon_beats_light_tank | 2 | main_battle_tank | 0 | 0 | 10 | -30 |
| platoon_beats_light_tank/3 | platoon_beats_light_tank | 3 | light_tank | 180 | 1 | 0 | 30 |

### Truong_du_lieu

Trạng thái: Đã áp

Nguồn dữ liệu: 12_he_thong_trang_thai/Truong_du_lieu.

Sheet: 12_he_thong_trang_thai/Truong_du_lieu — Bản đồ trường dữ liệu (19 dòng, 9 cột)

| id | field_path | rows | real_key | read_current | write | status |
|---|---|---|---|---|---|---|
| F001 | units.<id>.hp | 82 | vehicles[id].hp x toughness.vehicles (2.2; bosses toughness… | data hp x toughness | data hp = ROUND_HALF_UP(value / toughness); values compare… | exists |
| F002 | units.<id>.cost | 78 | vehicles[id].cp (baseCP, R7/S04) | cp | cp | exists |
| F003 | units.<id>.speed | 4 | vehicles[id].speed (m/s) | speed | speed | exists |
| F004 | units.<id>.outgoingDamageMult | 90 | vehicles[id].outgoingDamageMult | absent = 1.0 | the key | created in pass 1 (S03). Not the existing weaponDamage (pro… |
| F005 | units.<id>.dropDelaySec | 37 | vehicles[id].dropDelay | absent = 3.5 (EconomySystem.DeliverySeconds) | the key | created in pass 1 (S04); delivery reads it |
| F006 | units.<id>.flare.maxCharges | 17 | vehicles[id].flareCharges | absent = 0 (today flares are a skill with a cooldown, no ch… | the key | created in pass 5 (S06) |
| F007 | units.<id>.flare.rechargeSec | 17 | vehicles[id].flareRecharge, else the cooldown of the vehicl… | override, else skill cooldown, else null | the key; null new value removes the flare skill from the ve… | created in pass 5 (S06); the shared skills are not edited (… |
| F008 | units.<id>.apsCapability | 3 | vehicles[id].apsCapability | absent = "—" (NONE) | the key | created in pass 5 (S07) |
| F009 | units.<id>.interception.rechargeSec | 2 | vehicles[id].aps.recharge | aps.recharge (absent aps: null) | the key | exists |
| F010 | units.<id>.interception.maxCharges | 1 | vehicles[id].aps.charges | absent aps: 0 | the key | exists |
| F011 | units.<id>.interception.shellChance | 1 | vehicles[id].aps.shells | absent: 0 | the key | exists |
| F012 | units.<id>.interception.blocks.artilleryRocket | 1 | vehicles[id].aps.rockets | absent: false | the key | exists (the "rockets" flag lets APS take artillery rockets) |
| F013 | modes.<mode>.cpStockCap | 7 | economy.bankByMode[tag] = [from, to] (new data), read by Si… | the code's bank for the mode: default 30 (TeamEconomy), Sie… | [expected_before, new_value] per mode tag | created in pass 4 (E1); mode names -> tags below |
| F014 | economy.supplyThreshold | 1 | TeamEconomy.Supply (army cap x 1.5) | HOLD (E2) | not written | HOLD |
| F015 | aircraft.returnBecauseLowHP | 1 | code: TacticalAi.Refit (RefitBelow) | code | code (pass 6) | code |
| F016 | equipment.trophy_aps.rule | 1 | code: gear trait TrophyAps (VehicleBoost.cs) | code | code (pass 5, S07) | code |
| F017 | boss.gungnir.* | 5 | vehicle rail_supergun (the Gungnir) and its big attack | data + code | pass 7 (G1) | partly code |
| F018 | weapons.<id>.range, units.<id>.dps, balance.hpFloorCurve, m… | 6 | REJECT rows | - | never | REJECT |
| F019 | — | 9 | system bundles S01-S09 (code) | - | code | code |

### Validator_ket_qua

Trạng thái: Đã áp

Nguồn dữ liệu: 12_he_thong_trang_thai/Validator_ket_qua.

Sheet: 12_he_thong_trang_thai/Validator_ket_qua — Validator: kết quả fix_validate (765 dòng, 8 cột)

| id | khoa | gia_tri_so | gia_tri_chu |
|---|---|---|---|
| models.failures | failures |  |  |
| models.lod1OutsideBand | lod1OutsideBand |  | aa_turret 69%;aa_turret_a 67%;airborne_light_tank_chute 34%… |
| models.notScanned | notScanned |  | cp_relay_a;cp_relay_b;minefield_a;minefield_b |
| models.overBudgetInfo[0].class | class |  | tower |
| models.overBudgetInfo[0].max | max | 4000 |  |
| models.overBudgetInfo[0].model | model |  | aa_turret |
| models.overBudgetInfo[0].over | over |  | +58% |
| models.overBudgetInfo[0].triangles | triangles | 6306 |  |
| models.overBudgetInfo[1].class | class |  | tower |
| models.overBudgetInfo[1].max | max | 4000 |  |
| models.overBudgetInfo[1].model | model |  | aa_turret_a |
| models.overBudgetInfo[1].over | over |  | +67% |
| models.overBudgetInfo[1].triangles | triangles | 6670 |  |
| models.overBudgetInfo[2].class | class |  | tower |
| models.overBudgetInfo[2].max | max | 4000 |  |

*15 / 765 dòng đầu: xem sheet 12_he_thong_trang_thai/Validator_ket_qua.*
