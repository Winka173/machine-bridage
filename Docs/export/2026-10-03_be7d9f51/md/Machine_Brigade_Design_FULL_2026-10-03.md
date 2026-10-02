# Machine Brigade — Tài liệu thiết kế toàn văn (2026-10-03)

Commit be7d9f51. Sinh bởi `python Tools/export/export.py` (spec 6): ghép theo mục lục của tài liệu thiết kế (mục 1–19) cùng các mục mới 3b, 3c, 10i, 15b, 16b, 20, 21 và phụ lục P1–P5. Bảng in đúng ô của sheet (csv / xlsx cùng bộ xuất); bảng quá 40 dòng in 15 dòng đầu. PDF cùng ngày sinh từ chính file này.

<!-- SELF_CHECK -->
## Tự kiểm bộ xuất (spec 9; 00_chi_muc/SELF_CHECK.md)

Commit be7d9f51, ngày 2026-10-03, bản gốc so sánh `origin/main`. Lệnh: `python Tools/export/export.py check`.
Trạng thái: DAT = đạt; CHUA_DAT = có thiếu (liệt kê); CHUA_AP = phần của lượt sau. CI (.github/workflows/export.yml) chặn khi độ phủ, khóa ngoại, đồng nhất hoặc bí mật không đạt.

| # | Kiểm | Trạng thái | Thiếu |
|---|---|---|---|
| 1 | Mọi file và sheet của mục 4 tồn tại; sheet rỗng chỉ khi có dòng CHUA_AP | CHUA_DAT | file 13_tham_chieu_nguon chưa xuất (lượt 10, spec 12.3) |
| 2 | Độ phủ khóa, khóa ngoại, không (id, cột) nào hai giá trị giữa các file | DAT |  |
| 3 | Mỗi id đúng một dòng; số dòng khớp dữ liệu | DAT |  |
| 4 | Công thức khớp mã game; input chép khớp nguồn | CHUA_DAT | 1 cột công thức không có cột _game |
| 5 | Số trong Excel khớp md và pdf (mẫu 200 ô, seed 20261003) | DAT |  |
| 6 | Không ô số chứa chữ đơn vị; không ô trống ở cột bắt buộc | DAT |  |
| 7 | Hai lần xuất liên tiếp cho file giống hệt | DAT |  |
| 8 | Thứ không xuất và lý do; cột NEED_CODE_CHECK | DAT |  |
| 9 | Không có bí mật trong bất kỳ file | DAT |  |

CI: coverage DAT, foreign_keys DAT, determinism DAT, secrets DAT

Lớp tham chiếu (spec 12.6): CHUA_AP:prompt_xuat_luot10 (file 13 và sheet <tên>_tham_chieu chưa dựng; diff đã so mọi sheet nên sẽ báo thay đổi ở sheet tham chiếu).

### 1. Mọi file và sheet của mục 4 tồn tại; sheet rỗng chỉ khi có dòng CHUA_AP

Trạng thái: CHUA_DAT.

Files:

| file | có | số sheet |
|---|---|---|
| 01_vu_khi_dan | có | 15 |
| 02_phuong_tien | có | 29 |
| 03_boss | có | 39 |
| 04_can_cu_thap | có | 24 |
| 05_che_do_kinh_te | có | 11 |
| 06_ai | có | 13 |
| 07_chien_dich_cot_truyen | có | 32 |
| 08_ban_do | có | 39 |
| 09_hieu_ung_am_thanh | có | 18 |
| 10_model_tai_san | có | 21 |
| 11_meta_giao_dien | có | 24 |
| 12_he_thong_trang_thai | có | 23 |
| 13_tham_chieu_nguon | không | 0 |

Sheet spec 4 nêu mà chưa có:

(không có)

Sheet rỗng (0 dòng, không có dòng CHUA_AP):

(không có)

Sheet chỉ có dòng đánh dấu (CHUA_AP / NEED_CODE_CHECK / KHONG_CO): 33.

### 2. Độ phủ khóa, khóa ngoại, không (id, cột) nào hai giá trị giữa các file

Trạng thái: DAT.

Nguồn 1003, lá 803070; chưa ánh xạ 0; ánh xạ hai lần 0; chờ file chưa dựng 696 (Cho_anh_xa: file 13, lượt 10). Khóa ngoại: {'OK': 260}.

Khóa ngoại FAIL:

(không có)

Cùng (id, cột), giá trị khác nhau giữa các file (bỏ cột chung: ghi_chu, gia_tri_chu, gia_tri_so, khoa, mo_ta, nhom, trang_thai, raw_json, nguon, khối _truoc / _sau):

(không có)

### 3. Mỗi id đúng một dòng; số dòng khớp dữ liệu

Trạng thái: DAT.

| thực thể | sheet | số dòng | số trong nguồn | chênh | số spec nêu | id trùng | ghi chú |
|---|---|---|---|---|---|---|---|
| vũ khí | 01_vu_khi_dan/Vu_khi | 372 | 372 | 0 |  | 0 | balance.json weapons + secondRounds.rounds |
| xe | 02_phuong_tien/Xe | 120 |  |  |  | 0 | vehicles[] (253) chia vào 6 sheet: tổng 253 |
| boss | 03_boss/Boss | 41 |  |  | 41 | 0 |  |
| tháp | 04_can_cu_thap/Thap | 76 |  |  |  | 0 | phần của vehicles[] |
| thẻ hỗ trợ | 02_phuong_tien/The_ho_tro | 40 | 40 | 0 |  | 0 | balance.json supports |
| nhiệm vụ | 07_chien_dich_cot_truyen/Nhiem_vu | 193 | 193 | 0 | 193 | 0 | campaign.json missions |
| chương | 07_chien_dich_cot_truyen/Chuong | 15 | 15 | 0 | 15 | 0 | campaign.json chapters |
| bộ bài game | 07_chien_dich_cot_truyen/Bo_bai_game | 23 |  |  | 23 | 0 |  |
| bản đồ | 08_ban_do/Ban_do | 100 | 100 | 0 | 50 | 0 | maps/*.json: 25 bản đồ x 4 biến thể |
| commander | 02_phuong_tien/Commander | 22 |  |  |  | 0 | Commanders.cs |
| model | 10_model_tai_san/Model | 518 | 518 | 0 |  | 0 | Resources/Models/**/*.glb |
| clip | 09_hieu_ung_am_thanh/Am_thanh | 229 | 229 | 0 |  | 0 | Resources/Audio/** ogg / wav (Am_thanh có thêm dòng bank / nhạc nếu chênh) |

Bản đồ: spec nêu 50; dữ liệu có 25 bản đồ x 4 biến thể = 100 file (mỗi file một dòng).

Sheet có id trùng (mọi file):

(không có)

### 4. Công thức khớp mã game; input chép khớp nguồn

Trạng thái: CHUA_DAT.

Cột công thức (Schema.cong_thuc): 189; cột _game: 51; cột phân tích so với bản Python (Schema.nguon_khoa 'python:', không cần _game): 140; sheet input_: 11.
So công thức với _game (sai số 1e-6) là test của lượt 5; ở đây: mỗi cột công thức có cột _game, và mọi ô input_ bằng giá trị ở file nguồn (cùng id, cùng cột).

Cột công thức thiếu _game:

| file | sheet | cột |
|---|---|---|
| 01_vu_khi_dan | Vu_khi | thoi_gian_bay_toi_tam_s |

Ô input_ khác nguồn:

(không có)

### 5. Số trong Excel khớp md và pdf (mẫu 200 ô, seed 20261003)

Trạng thái: DAT.

Ô số trong bảng md (mọi file md/, bảng có dòng 'Sheet: <file>/<sheet>'): 14120; mẫu 200 (seed 20261003); khác csv: 0. pdf Machine_Brigade_Design_2026-10-03.pdf: 120 trang; mẫu 200 ô của Machine_Brigade_Design_FULL_2026-10-03.md (seed 20261004); khác csv hoặc không thấy trên trang có id dòng: 0.

Ô md khác csv:

(không có)

Ô pdf lệch:

(không có)

### 6. Không ô số chứa chữ đơn vị; không ô trống ở cột bắt buộc

Trạng thái: DAT.

Ô số kèm đơn vị (cột số hoặc cột có đơn vị; cả ô là 'số đơn vị'):

(không có)

Cột kiểu số (Schema int / number) có ô chữ không phải dấu đánh dấu:

(không có)

Cột bắt buộc (Schema bat_buoc) có ô trống:

(không có)

### 7. Hai lần xuất liên tiếp cho file giống hệt

Trạng thái: DAT.

Hai lần xuất (hai tiến trình riêng) trên cùng dữ liệu: 365 file so băm sha256 (trừ README.md, MANIFEST.json, SELF_CHECK.md); khác: 0.

(không có)

### 8. Thứ không xuất và lý do; cột NEED_CODE_CHECK

Trạng thái: DAT.

Khong_xuat: 21 luật; nguồn không đọc được: 0; cột có NEED_CODE_CHECK: 51 (5690 ô).

Khong_xuat (mẫu đường dẫn, lý do, số lá):

| id | nguồn | mẫu | lý do | số lá |
|---|---|---|---|---|
| KX001 | * | **.*password* | bảo mật: mật khẩu (spec 8) | 0 |
| KX002 | * | **.*keystore* | bảo mật: keystore (spec 8) | 0 |
| KX003 | * | **.*apikey* | bảo mật: khóa API (spec 8) | 0 |
| KX004 | * | **.*token | bảo mật: token (spec 8) | 0 |
| KX005 | * | **.*secret* | bảo mật: bí mật (spec 8) | 0 |
| KX006 | Assets/Settings/*.asset | ** | cấu hình render URP (không có trường lối chơi) | 1322 |
| KX007 | Assets/MachineBrigade/Settings/VulkanDeviceFilters.asset | ** | bộ lọc thiết bị Vulkan (không có trường lối chơi) | 17 |
| KX008 | Assets/MachineBrigade/Scenes/*.unity | ** | cảnh Unity: chỉ bố cục khởi động; lối chơi đọc từ dữ liệu lúc chạy (SceneBuilder dựng cảnh) | 437 |
| KX009 | Tools/music/requirements.txt | ** | danh sách gói Python của công cụ nhạc (không phải dữ liệu game) | 7 |
| KX010 | *.asset | docs[*]._class | mã lớp Unity của tài liệu YAML (siêu dữ liệu) | 6 |
| KX011 | *.asset | docs[*]._file_id | mã đối tượng Unity (siêu dữ liệu) | 6 |
| KX012 | *.asset | docs[*].*.m_ObjectHideFlags | cờ ẩn của Unity (siêu dữ liệu) | 6 |
| KX013 | *.asset | docs[*].*.m_CorrespondingSourceObject | liên kết prefab của Unity (siêu dữ liệu) | 6 |
| KX014 | *.asset | docs[*].*.m_PrefabInstance | liên kết prefab của Unity (siêu dữ liệu) | 6 |
| KX015 | *.asset | docs[*].*.m_PrefabAsset | liên kết prefab của Unity (siêu dữ liệu) | 6 |
| KX016 | *.asset | docs[*].*.m_GameObject | liên kết GameObject của Unity (siêu dữ liệu) | 6 |
| KX017 | *.asset | docs[*].*.m_Script | guid script của Unity (siêu dữ liệu) | 6 |
| KX018 | *.asset | docs[*].*.m_EditorHideFlags | cờ editor của Unity (siêu dữ liệu) | 6 |
| KX019 | *.asset | docs[*].*.m_EditorClassIdentifier | định danh editor của Unity (siêu dữ liệu) | 6 |
| KX020 | Assets/MachineBrigade/Settings/BattlefieldProfile.asset | docs[*].MonoBehaviour.components._items[*].* | VolumeProfile.components: id tài liệu Unity của các hiệu ứng (siêu dữ liệu; mỗi hiệu ứng là một d... | 5 |
| KX021 | Docs/checks/fix_validate.json | models.summary.scanDir | bảo mật: đường dẫn tuyệt đối máy cá nhân (spec 8) | 1 |

Nguồn không đọc được:

(không có)

Cột NEED_CODE_CHECK:

| file | sheet | cột | số ô |
|---|---|---|---|
| 01_vu_khi_dan | Dan_thay_the | dieu_kien_tu_doi | 70 |
| 01_vu_khi_dan | Dan_thay_the | thoi_gian_doi_s | 70 |
| 01_vu_khi_dan | Dan_thay_the | thoi_gian_giu_s | 70 |
| 01_vu_khi_dan | Hanh_vi_dan_nhom | cach_nham | 7 |
| 01_vu_khi_dan | Hanh_vi_dan_nhom | co_canh_bao | 7 |
| 01_vu_khi_dan | Hanh_vi_dan_nhom | khi_no | 7 |
| 01_vu_khi_dan | Hanh_vi_dan_nhom | khi_truot | 7 |
| 01_vu_khi_dan | Hanh_vi_dan_nhom | thoi_gian_bay_toi_da_s | 7 |
| 01_vu_khi_dan | Hanh_vi_dan_nhom | tuong_tac_aps | 7 |
| 01_vu_khi_dan | Hanh_vi_dan_nhom | tuong_tac_gay_nhieu | 7 |
| 01_vu_khi_dan | Hanh_vi_dan_nhom | tuong_tac_phao_sang | 7 |
| 01_vu_khi_dan | Khac_che | chan_artilleryRocket | 22 |
| 01_vu_khi_dan | Khac_che | chan_artilleryShell | 22 |
| 01_vu_khi_dan | Khac_che | chan_bullet | 22 |
| 01_vu_khi_dan | Khac_che | chan_directMissile | 22 |
| 01_vu_khi_dan | Khac_che | chan_directRocket | 22 |
| 01_vu_khi_dan | Khac_che | chan_drone | 22 |
| 01_vu_khi_dan | Khac_che | chan_energy | 22 |
| 01_vu_khi_dan | Khac_che | chan_mortarShell | 22 |
| 01_vu_khi_dan | Khac_che | chan_tankShell | 22 |
| 01_vu_khi_dan | Phao_sang | so_qua_moi_lan | 18 |
| 02_phuong_tien | Doi_mo_man_suy_ra | phan_tram_cp_khoi_dau | 23 |
| 02_phuong_tien | May_bay_so_phat | dai_muc_tieu | 26 |
| 02_phuong_tien | Xe | hoi_tu_ve_s | 11 |
| 02_phuong_tien | Xe | mau_trong_tran_hp | 12 |
| 02_phuong_tien | Xe | mo_khoa | 120 |
| 02_phuong_tien | Xe | nhom_gia | 120 |
| 02_phuong_tien | Xe_suy_ra | he_so_gia | 120 |
| 02_phuong_tien | Xe_suy_ra | nhom_gia | 120 |
| 02_phuong_tien | Xe_suy_ra | tha_du_theo_nhom_s | 120 |
| 02_phuong_tien | Xe_suy_ra | thuong_suc_manh | 120 |
| 03_boss | Boss | thoi_gian_ha_muc_tieu_s | 41 |
| 03_boss | Boss_dps | cach_bu | 41 |
| 03_boss | Sanhunt | phong_khong | 41 |
| 03_boss | Sanhunt | tuan | 41 |
| 04_can_cu_thap | Thap | co_can_bang | 76 |
| 04_can_cu_thap | Thap | hoi_tu_ve_s | 3 |
| 04_can_cu_thap | Thap | mo_khoa | 76 |
| 04_can_cu_thap | Thap | the_cu_gop_vao | 76 |
| 05_che_do_kinh_te | Kinh_te | gia_tri_chu | 2 |
| 05_che_do_kinh_te | Vo_han | he_so_tang_thuong | 6 |
| 07_chien_dich_cot_truyen | Bo_bai_game | muc_tieu_goc_giu | 23 |
| 07_chien_dich_cot_truyen | Nhan_vat | chan_dung | 21 |
| 07_chien_dich_cot_truyen | Nhiem_vu | trang_thai_kich_ban | 193 |
| 07_chien_dich_cot_truyen | Thoai | chan_dung | 1614 |
| 07_chien_dich_cot_truyen | Thoai | so_dong_hien_thi_toi_da | 1614 |
| 07_chien_dich_cot_truyen | Trigger_thoai | hoi_chieu_so_lan | 27 |
| 09_hieu_ung_am_thanh | Am_thanh_mixer | trang_thai | 1 |
| 09_hieu_ung_am_thanh | Xac_vo | trang_thai | 1 |
| 10_model_tai_san | Model | tam_giac_lod | 518 |
| 10_model_tai_san | Xem_truoc | trang_thai | 1 |

### 9. Không có bí mật trong bất kỳ file

Trạng thái: DAT.

Quét 395 file (mọi file của bộ xuất và các thư mục diff_*; xlsx từng phần, pdf giải nén luồng, ảnh đọc thô): khóa API (Google, AWS, GitHub, Slack, sk-), khóa riêng, mật khẩu / keystore, JWT, bearer, api_key=, email, đường dẫn tuyệt đối máy cá nhân, tên người dùng máy.

(không có)

<!-- /SELF_CHECK -->

## Mục lục

- 1. Tổng quan (05_che_do_kinh_te)
- 2. Chế độ chơi (05_che_do_kinh_te)

  - 2b. Cân bằng chế độ và độ khó (05_che_do_kinh_te)
  - 2c. Luật trận, phần vô hạn, trung lập, thoại và kết trận (05_che_do_kinh_te)
- 3. Chiến dịch (07_chien_dich_cot_truyen)

  - 3b. Bộ bài game (07_chien_dich_cot_truyen)
  - 3c. Biến cố và sự kiện trong nhiệm vụ (07_chien_dich_cot_truyen)
- 4. Nhiệm vụ nhiều giai đoạn (07_chien_dich_cot_truyen)
- 5. Tác chiến (05_che_do_kinh_te)
- 6. Căn cứ và tháp (04_can_cu_thap)
- 7. Công thành và Phòng thủ (04_can_cu_thap)

  - 7b. Biển, hộ tống, bản đồ dài, roster mới và đòn lớn (08_ban_do)
- 8. Phương tiện (02_phuong_tien)
- 9. Bảng DPS tổng hợp (02_phuong_tien)
- 10. Vũ khí và bảng sát thương (01_vu_khi_dan)

  - 10d. Tổng hợp boss (03_boss)
  - 10g. Boss: vụ nổ hai lớp, pha, giáp và cỡ (03_boss)
  - 10h. Săn trùm (Boss Hunt) (03_boss)
  - 10i. Sổ tay đạn (01_vu_khi_dan)
  - 10j. Họ vũ khí, hành vi đạn và vòng cảnh báo (01_vu_khi_dan)
- 11. Tháp canh, xe tinh nhuệ và boss (03_boss)
- 12. Hỗ trợ hỏa lực (02_phuong_tien)

  - 12b. Bảng giá, hệ đạn và hồi đạn (02_phuong_tien)
  - 12c. Commander (02_phuong_tien)
- 13. Trang bị (02_phuong_tien)
- 14. Kinh tế (05_che_do_kinh_te)
- 15. Bản đồ (08_ban_do)

  - 15b. Đo bản đồ tĩnh (08_ban_do)
- 16. AI và hệ thống (06_ai)

  - 16b. Kiểm tĩnh chế độ (05_che_do_kinh_te)
- 17. Kiểm thử và phép đo còn lại (12_he_thong_trang_thai)
- 18. Giao diện (11_meta_giao_dien)
- 19. Hình ảnh (10_model_tai_san)
- 20. Âm thanh (09_hieu_ung_am_thanh)

  - 20b. Hiệu ứng theo bậc và xác vỡ (09_hieu_ung_am_thanh)
- 21. Model (10_model_tai_san)
- P1. Hằng số trong mã (12_he_thong_trang_thai)
- P2. Lịch sử đo (12_he_thong_trang_thai)
- P3. Quyết định và chờ quyết (12_he_thong_trang_thai)
- P4. Trạng thái prompt, validator, manifest và save (12_he_thong_trang_thai)
- P5. Mục lục bảng dữ liệu, sửa chữ theo mã và ảnh (12_he_thong_trang_thai)

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

## 5. Tác chiến

Trạng thái: Đã áp

Nguồn dữ liệu: 05_che_do_kinh_te/Tac_chien_bac; 05_che_do_kinh_te/Diem_tac_chien; 05_che_do_kinh_te/Mutator; 11_meta_giao_dien/Mutator_tuan. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §5. Tác chiến.

Menu gồm 5 mục: Trang chủ, Chiến dịch, **Tác chiến**, Quân đội, Cửa hàng; Giao tranh (Giữ cứ điểm, Vua đồi, Tử chiến, Công phá, Công thành, Phòng thủ) và Thử thách (Sinh tồn, Vô tận) chọn ở ô chọn chế độ. Tác chiến gom: chơi lại các chiến dịch lớn và các trận nổi bật của cốt truyện (công thành, phòng thủ, đấu tướng) sau khi đã thắng trong chiến dịch (26 trận), chiến dịch của tuần, Pháo đài tuần, Săn trùm và thử thách hằng ngày.

#### Cấp độ

Huyền thoại mở sau khi thắng c12m10 (màn kết của chương 12). **Điểm** một trận thắng: 5000 + tối đa 3000 theo thời gian dưới 25 phút + tối đa 2000 theo tổn thất (150 xe mất thì bằng 0) + tối đa 2000 theo máu sở chỉ huy; nhân hệ số cấp cộng phần của mỗi mutator. Thua: 0 điểm. Kỷ lục (điểm cao nhất, thắng nhanh nhất) lưu riêng cho từng trận và từng cấp.

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

## 6. Căn cứ và tháp

Trạng thái: Đã áp

Nguồn dữ liệu: 04_can_cu_thap/Thap; 04_can_cu_thap/Thap_vu_khi; 04_can_cu_thap/Tuong; 04_can_cu_thap/Tuong_luat; 04_can_cu_thap/Nha_chinh; 04_can_cu_thap/Nha_chinh_kieu; 04_can_cu_thap/Mo_dun_tien_ich; 04_can_cu_thap/Loadout_can_cu; 04_can_cu_thap/Xay_lai; 04_can_cu_thap/Thap_gia_cong_thuc; 04_can_cu_thap/Can_cu_luat. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §6. Căn cứ, §Hệ căn cứ (prompt 32).

#### 6. Căn cứ và tháp

Căn cứ là một loadout chọn trước trận như bộ bài: sở chỉ huy (HQ) cấp 1–5 và các ô tháp theo cỡ **nhỏ / vừa / lớn** trên bản đồ căn cứ của từng map. Tháp cỡ nào vào ô cỡ đó hoặc ô to hơn; ô tiện ích nhận mô-đun. Tháp bị phá được thả dù lại trong trận (trả CP, có hồi chiêu; tháp nhỏ rẻ và nhanh hơn). Mỗi cứ điểm có tiền đồn 1 ô nhỏ + 1 ô vừa. Vai trò căn cứ theo chế độ: chỗ dựa (sở chỉ huy không bị phá) hoặc mục tiêu.

**Vai trò tháp nhỏ:** tháp canh thấy tàng hình và tăng 10% tầm cho tháp trong 25 m (nhánh Tháp quan sát: 15% trong 30 m, thay mức 10%, không cộng dồn); tháp phòng không nhỏ +25% sát thương lên drone và trực thăng. **Điểm yếu tháp pháo:** xoay chậm, nạp lâu, súng đồng trục không bắn máy bay. **AI** đọc căn cứ địch và mua quân khắc chế. **Thẻ tháp** lên hạng như xe; từ hạng 7 chọn 1 trong 2 nhánh (đổi nhánh 800 xu). **Trang bị tháp:** 3 ô (Vũ khí, Kết cấu, Hệ thống) dùng chung cho mọi tháp cùng loại trong căn cứ.

#### Thẻ tháp (22)

| Tháp | Cỡ | Máu | Dựng lại | Nhánh (hạng 7) | Hướng dẫn |
|---|---|---|---|---|---|
| **Tháp canh** | Nhỏ | 1.540 | 5 CP · 25 s | **Tháp quan sát**: Nhìn xa hơn 30%, và cho các tháp trong 30 m thêm 15% tầm bắn (thay cho mức 10% thường của tháp, không cộng dồn). **Ổ súng**: Pháo 25 mm thay súng máy: đánh mạnh xe nhẹ, nhìn gần hơ… | **Tháp canh · công sự cố định · nhẹ nhưng nhìn xa** Cách đánh: súng máy nặng (30 m, bắn cả máy bay); tầm nhìn 60 m giúp soi quân ta cho pháo địch. Mạnh / yếu: chặn trinh sát và xe nhẹ; là tháp yếu nh… |
| **Lô cốt súng máy** | Nhỏ | 3.300 | 6 CP · 25 s | **Súng máy đôi**: Súng máy nặng đôi: hỏa lực mạnh hơn, tầm hơi ngắn hơn. **Lô cốt phun lửa**: Súng phun lửa (16 m) đốt thứ gì lại gần; không bắn được máy bay. | **Lô cốt súng máy · công sự cố định · súng máy nặng** Cách đánh: súng máy nặng bắn nhanh (32 m, bắn cả máy bay). Mạnh / yếu: quét sạch trinh sát và xe nhẹ; gần như không làm xước xe tăng. Mẹo: đưa xe… |
| **Ụ pháo chống tăng** | Nhỏ | 1.500 | 4 CP · 25 s | **Pháo chống tăng tầm xa**: Pháo Rapira 100 mm: xuyên giáp dày tới 38 m, nhưng xoay chậm và chỉ phủ góc 45°. **Súng không giật**: SPG-9 73 mm: đạn lõm rẻ, bắn mọi hướng ở 28 m; yếu hơn với giáp dày n… | **Ụ pháo chống tăng · tháp ô nhỏ · diệt tăng giá rẻ** Cách đánh: 5 giây một phát xuyên giáp, tầm 38 m, chỉ trong 45° hai bên phía trước; pháo xoay chậm. Mạnh / yếu: chặn xe tăng lao thẳng tới; pháo b… |
| **Tháp phòng không** | Nhỏ | 2.420 | 6 CP · 25 s | **Tháp cao xạ**: Pháo cao xạ 23 mm bốn nòng tầm gần: hỏa lực mạnh hơn nhiều vào drone, bầy nhỏ và trực thăng, không có tên lửa. **Tổ Stinger**: Tên lửa Stinger thay cho pháo 23 mm: máy bay và trực th… | **Tháp phòng không · công sự cố định · chống máy bay (42 m)** Cách đánh: pháo đôi 30 mm cao xạ tới 42 m và tên lửa phòng không (44 m); cũng bắn mặt đất nhưng chẳng mấy tác dụng. Mạnh / yếu: xé nát tr… |
| **Tháp gây nhiễu EW** | Nhỏ | 1.760 | 3 CP · 25 s | **Máy gây nhiễu drone**: Gây nhiễu đạn điều khiển và drone xa tới 45 m. **Máy đánh lừa radar**: Còn tìm ra pháo khai hỏa trong 80 m và làm lộ chúng 6 giây. | **Tháp gây nhiễu EW · tháp nhỏ · gây nhiễu, không bắn** Cách đánh: tên lửa điều khiển, drone và hỏa lực yểm trợ nhắm vào trong vòng 30 m quanh nó bị lệch; không có súng. Mạnh / yếu: làm cùn tên lửa c… |
| **Răng rồng** | Nhỏ | 5.280 | 3 CP · 25 s | **Chông sắt**: Khó phá gấp đôi. **Rào thép gai**: Không chặn đường, nhưng làm xe địch trong 6 m chậm một nửa. | **Răng rồng · vật cản nhỏ · chặn đường** Cách đánh: các hàng khối bê tông không xe nào đi qua được; không đánh gì và bị bắn sau cùng. Mạnh / yếu: biến lối vào thành đường vòng dưới họng súng của ta;… |
| **Bãi mìn** | Nhỏ | 880 | 3 CP · 25 s |  | **Bãi mìn · vật cản nhỏ · tám quả mìn** Cách đánh: tám quả mìn chống tăng trong vòng 5 m, rải lại mỗi 45 giây; bãi mìn không phải mục tiêu. Mạnh / yếu: trừng phạt xe lao vào ồ ạt; trinh sát, công bin… |
| **Trạm tiếp tế CP** | Nhỏ | 1.320 | 6 CP · 25 s |  | **Trạm tiếp tế CP · tháp nhỏ · kinh tế** Cách đánh: không có súng; +0,1 CP mỗi giây cho phe mình, trạm thứ hai +0,06, trạm thứ ba không thêm gì; bị bắn thì ngừng trả 5 giây. Mạnh / yếu: thêm CP cho c… |
| **Đèn pha chiến trường** | Nhỏ | 1.199 | 3 CP · 25 s | **Đèn pha**: Chiếu sáng liên tục quanh nó và làm lóa quân tấn công trong luồng sáng. **Pháo sáng**: Bắn pháo sáng mỗi 15 giây tới 40 m: chiếu sáng vùng rộng theo đợt, giữa các đợt thì tối. | **Đèn pha chiến trường · công trình ô nhỏ · ánh sáng đêm** Cách đánh: ban đêm và trong sương mù, phe ta thấy mọi thứ trong 35 m quanh nó; địch trong vùng bắn kém 20%. Mạnh / yếu: biến trận đêm thành… |
| **Mồi nhử bơm hơi** | Nhỏ | 299 | 3 CP · 25 s | **Mồi nhử bơm hơi**: Giả làm tháp pháo: hỏa lực địch dồn vào nó cho tới khi địch phát hiện. **Khí cầu neo**: Làm tản bom thả trong 40 m và làm lộ máy bay địch trong 45 m. | **Mồi nhử bơm hơi · công trình ô nhỏ · hút hỏa lực** Cách đánh: trông như tháp pháo; địch bắn vào nó cho tới khi trinh sát, radar, drone hoặc UAV quét lật tẩy. Mạnh / yếu: làm địch phí đạn pháo và tê… |
| **Tháp tên lửa chống tăng** | Vừa | 1.980 | 7 CP · 40 s | **Tấn công từ trên**: Mạnh hơn 40% lên giáp dày. **Đa năng**: Bắn được cả trực thăng và máy bay; nhẹ hơn lên giáp. | **Tháp tên lửa chống tăng · công sự cố định · chống tăng (50 m)** Cách đánh: bệ phóng Kornet đôi bắn tên lửa chống tăng theo cặp xa tới 50 m. Mạnh / yếu: chặn xe tăng và giáp dày từ xa; APS và xe la-… |
| **Tháp pháo** | Vừa | 3.960 | 11 CP · 40 s | **Pháo bắn tỉa**: Pháo 120 mm nòng dài có ống ngắm: bắn xa hơn mọi pháo xe tăng, chậm, mỗi phát hạ được xe tăng; không bắn máy bay. **Pháo tự động 57 mm**: Loạt đạn 57 mm nhanh chỉ vào xe nhẹ (giáp t… | **Tháp pháo · công sự cố định · pháo xe tăng (32 m)** Cách đánh: pháo 120 mm xuyên giáp của tăng chủ lực đặt trên bệ cố định. Mạnh / yếu: thắng xe tăng và xe nhẹ lọt vào tầm 32 m; bị xe diệt tăng và… |
| **Trạm đánh chặn C-RAM** | Vừa | 2.860 | 5 CP · 40 s | **Centurion**: Súng đánh chặn tầm gần bắn nhanh: nhiều quả đánh chặn hơn, hồi nhanh. Chặn tên lửa, drone, rốc-két bắn thẳng, rốc-két pháo binh và một phần đạn pháo binh, đạn cối; không chặn đạn pháo… | **Trạm đánh chặn C-RAM · tháp vừa · bắn hạ đạn bay tới** Cách đánh: bắn hạ rốc-két, tên lửa, drone và khoảng một phần ba đạn pháo nhắm vào trong 35 m, hai quả đánh chặn cùng lúc; pháo nhiều nòng 20 m… |
| **Dàn rốc-két** | Vừa | 2.420 | 11 CP · 40 s | **Rốc-két chùm**: Mỗi rốc-két rải bom con: tốt hơn với cụm quân, trúng trực tiếp nhẹ hơn. **Rốc-két dẫn đường**: Hai rốc-két GMLRS chính xác ở tầm xa: mạnh với pháo binh và công trình, yếu trước bầy… | **Dàn rốc-két · công sự cố định · phóng loạt (55 m)** Cách đánh: phóng loạt sáu rốc-két theo đường cầu vồng vào mục tiêu mặt đất cách 8–55 m, vượt qua tường và vật che (từ sân trong vào quân địch đã… |
| **Tháp cao xạ hạng nặng** | Vừa | 3.001 | 7 CP · 40 s | **Cao xạ hạng nặng**: KS-19 100 mm: bắn chậm, nổ trên không bán kính lớn vào oanh tạc cơ và tốp máy bay dày; hạ nòng bắn được xe tăng ở 50 m. **Pháo PK 40 mm**: Bofors L/70: luồng đạn 40 mm đều đặn t… | **Tháp cao xạ hạng nặng · tháp ô vừa · đạn nổ trên không** Cách đánh: 2 giây một phát lớn, nổ trên không rộng 6 m, tầm 70 m; hạ nòng bắn xe tăng trong 50 m. Mạnh / yếu: bẻ gãy oanh tạc cơ và tốp máy… |
| **Trạm phòng không laser chống drone** | Vừa | 2.499 | 5 CP · 40 s | **Trạm la-de**: La-de 50 kW đốt drone ở 40 m và bắn hạ rốc-két, tên lửa nhắm gần nó; không bao giờ hết đạn; không chặn đạn pháo. **Lưới chắn drone**: Hành lang lưới thụ động: bắt drone bay vào trong… | **Trạm phòng không laser chống drone · tháp ô vừa · không bao giờ hết đạn** Cách đánh: laser chỉ bắn drone, tầm 40 m, cùng bộ đánh chặn rốc-két và đạn cối; khói làm tia yếu 80%. Mạnh / yếu: dập bầy d… |
| **Hầm che quân** | Vừa | 4.000 | 5 CP · 40 s |  | **Hầm che quân · công trình ô vừa · tránh đạn pháo** Cách đánh: xe ta trong 15 m nhận một nửa sát thương pháo, cối, bom và không kích; không che đạn bắn thẳng. Mạnh / yếu: giữ quân phòng thủ sống qua… |
| **Tháp pháo hạng nặng** | Lớn | 6.160 | 18 CP · 60 s | **Pháo bờ biển tầm xa**: Pháo 155 mm bắn tới 72 m. Mở khi đánh chìm Leviathan (4-11). **Pháo đài thép**: Chắc hơn nhiều, thêm hai tháp súng máy nhỏ xoay quanh đánh xe nhẹ và drone áp sát. | **Tháp pháo hạng nặng · công sự cố định · pháo đôi 155 mm (50 m)** Cách đánh: tháp pháo đôi 155 mm xoay chậm, bắn loạt đôi đạn nổ mạnh tới 50 m. Mạnh / yếu: phá nát xe nhẹ, cụm quân và xe tăng trong… |
| **Trạm tên lửa phòng không tầm xa** | Lớn | 4.180 | 13 CP · 60 s | **PAC-3 đánh chặn**: Bắn hạ tên lửa hành trình, tên lửa đạn đạo, đòn tên lửa hành trình và tên lửa từ đòn lớn của boss; bắn máy bay yếu hơn. **Radar tầm xa**: Bắn máy bay từ rất xa và làm lộ mọi máy… | **Trạm tên lửa phòng không tầm xa · công sự cố định · phòng không tầm xa (62 m)** Cách đánh: radar nhìn xa 85 m, phóng tên lửa từng cặp vào máy bay cách tới 62 m; không có gì để đánh mặt đất. Mạnh /… |
| **Nhà chứa drone** | Lớn | 4.840 | 12 CP · 60 s | **Nhà chứa Lancet**: Đạn bay lượn Lancet thay drone FPV: tầm xa, gấp đôi lên pháo binh và xe đỗ. **Bầy đàn**: Những đợt drone FPV đông hơn, thưa hơn. | **Nhà chứa drone · tháp lớn · drone FPV** Cách đánh: cứ 20 giây phóng hai drone FPV cảm tử vào địch xa tới 70 m, mạnh lên giáp và công trình. Mạnh / yếu: bào mòn thứ gì đứng ngoài tầm các tháp khác;… |
| **Trận địa pháo** | Lớn | 2.420 | 12 CP · 60 s | **Phản pháo**: Nhắm ngay pháo địch vừa khai hỏa trong tầm và làm lộ chúng một lúc; đánh pháo binh mạnh hơn. **Cối hạng nặng**: Cối 240 mm bắn cầu vồng, qua tường vào sân trong và sau vật che: tầm ngắ… | **Trận địa pháo · công sự cố định · tầm xa (90 m)** Cách đánh: lựu pháo nã vào mục tiêu mặt đất cách 25–90 m mỗi khi phe thủ nhìn thấy; không có gì tự vệ ở gần. Mạnh / yếu: gây đau cho mọi thứ dừng l… |
| **Máy phát khiên** | Lớn | 4.400 | 10 CP · 60 s | **Vòm khiên**: Một vòm lớn, chắc hơn, che cả khu vực. **Lá chắn tháp**: Không có vòm chung: mỗi tháp phe ta quanh nó có một khiên nhỏ riêng chặn đạn bắn trúng nó (không chặn vụ nổ xung quanh), tự hồi… | **Máy phát khiên · tháp lớn · che một phần căn cứ** Cách đánh: không có súng; vòm khiên 25 m hấp thụ 3.000 sát thương từ đạn pháo, bom, đạn súng và tên lửa cho mọi thứ phe ta bên dưới, rồi vỡ; hồi lạ… |

#### Mô-đun tiện ích (9)

| Mô-đun | Tác dụng |
|---|---|
| **Sân bay dã chiến** | **Sân bay dã chiến · mô-đun tiện ích** Cách đánh: máy bay bay trên nó hồi 3% máu mỗi giây và nạp đạn; chỉ huy tự đưa chúng về khi hết đạn. Mạnh / yếu: giúp trực thăng và máy bay bay… |
| **Sân bay dã chiến · Nhà chứa máy bay** |  |
| **Sân bay dã chiến · Phục vụ nhanh** |  |
| **Kho đạn** | **Kho đạn · mô-đun tiện ích** Cách đánh: xe nạp đạn tại căn cứ nhanh gấp đôi. Mạnh / yếu: rất hợp với giàn phóng và pháo binh hay hết đạn; nổ rất mạnh khi bị phá. Mẹo: mang theo khi bộ bài nhiều pháo… |
| **Trung tâm điều khiển hỏa lực** | **Trung tâm điều khiển hỏa lực · mô-đun tiện ích · liên kết tháp** Cách đánh: tháp trong 30 m gây thêm 12% sát thương và dồn hỏa lực vào một mục tiêu. Mạnh / yếu: biến cụm tháp thành một khối; vô dụn… |
| **Trạm hậu cần** | **Trạm hậu cần · mô-đun tiện ích** Cách đánh: mức tiếp tế của quân ta tăng thêm 8 CP: thu nhập chỉ giảm khi quân vượt mức tiếp tế. Mạnh / yếu: cho đội quân lớn giữ nguyên thu nhập; vô ích với đội quâ… |
| **Trạm radar** | **Trạm radar · mô-đun tiện ích** Cách đánh: mọi thứ trong căn cứ đều lộ, kể cả tàng hình và ẩn nấp, và pháo địch khai hỏa trong 120 m bị lộ 8 giây. Mạnh / yếu: làm lộ oanh tạc cơ tàng hình và pháo ẩn… |
| **Xưởng sửa chữa** | **Xưởng sửa chữa · mô-đun tiện ích** Cách đánh: xe trong vòng 35 m quanh sở chỉ huy hồi 1,5% máu mỗi giây, kể cả giữa trận. Mạnh / yếu: giữ quân phòng thủ đứng vững; không giúp gì xe ở ngoài chiến tr… |
| **Máy tạo nhiễu tầm nhìn** | **Máy tạo nhiễu tầm nhìn · mô-đun tiện ích · che căn cứ** Cách đánh: địch không thấy gì của ta trong 35 m quanh nó nếu xa hơn 15 m, trừ trinh sát. Mạnh / yếu: pháo binh không tìm được thứ nó che; tri… |

#### Đo cân bằng căn cứ

Căn cứ mặc định (pháo đài hạng nặng + ụ pháo; tháp pháo, giàn rocket, tháp ATGM; mỗi loại 2 tháp canh, phòng không, súng máy) đạt 1,86 trước quân hỗn hợp, cao hơn mọi căn cứ chỉ một loại tháp (tốt nhất 1,79); không căn cứ một loại nào mạnh nhất trước mọi loại quân. Tỷ lệ chọn tháp nhỏ trong ô nhỏ (tối ưu tham lam): tháp canh 32%, phòng không 22%, súng máy 19%, răng rồng 11%, EW 10%, bãi mìn 7% → bãi mìn được tăng lên 8 quả, rải lại mỗi 45 giây. Quân pháo binh đứng ngoài tầm tháp thắng mọi căn cứ nếu căn cứ đứng một mình: câu trả lời là quân và phản pháo.

#### Hệ căn cứ (prompt 32) / The base system (prompt 32)

Sinh từ dữ liệu (balance.json, các file bản đồ). / Generated from the data (balance.json, the map files).

#### 6a. Roster 22 tháp và nhánh / The 22-tower roster and its branches

| Tháp / Tower | Cỡ / Size | Xây lại / Rebuild CP | Nhánh A / Branch A | Nhánh B / Branch B |
|---|---|---|---|---|
| guard_tower (guard_tower) | Small | 5 | guard_tower.watch observation_reach, 5 CP | guard_tower.nest autocannon_25, 5 CP |
| mg_bunker (mg_bunker) | Small | 6 | mg_bunker.twin mg_twin, 6 CP | mg_bunker.flame flame_close, 6 CP |
| at_gun_emplacement (at_gun_emplacement) | Small | 4 | at_gun_emplacement.long at_gun_long_narrow, 4 CP | at_gun_emplacement.recoilless at_recoilless_wide, 3 CP |
| aa_turret (aa_turret) | Small | 6 | aa_turret.flak aa_gun_23_drones_helis, 6 CP | aa_turret.sam aa_manpads_aircraft, 5 CP |
| ew_tower (ew_tower) | Small | 3 | ew_tower.drone jam_drones_guided, 3 CP | ew_tower.spoof radar_spoof_counterbattery, 3 CP |
| dragons_teeth (dragons_teeth) | Small | 3 | dragons_teeth.hedgehog obstacle_block, 3 CP | dragons_teeth.wire wire_slow, 3 CP |
| minefield (minefield) | Small | 3 | không nhánh / no branch mines_at | không nhánh / no branch mines_at |
| cp_relay (cp_relay) | Small | 6 | không nhánh / no branch cp_income | không nhánh / no branch cp_income |
| searchlight (searchlight) | Small | 3 | searchlight.beam light_area, 3 CP | searchlight.flare light_flare_waves, 3 CP |
| inflatable_decoy (inflatable_decoy) | Small | 3 | inflatable_decoy.inflatable decoy_draw_fire, 3 CP | inflatable_decoy.balloon balloon_scatter_reveal, 3 CP |
| atgm_tower (atgm_tower) | Medium | 7 | atgm_tower.top atgm_top_attack, 7 CP | atgm_tower.multi atgm_multi, 6 CP |
| gun_turret (gun_turret) | Medium | 11 | gun_turret.long gun_sniper_120, 11 CP | gun_turret.auto gun_57_light, 11 CP |
| c_ram (c_ram) | Medium | 5 | c_ram.centurion intercept_close_fast, 5 CP | c_ram.dome intercept_far_slow, 5 CP |
| rocket_turret (rocket_turret) | Medium | 11 | rocket_turret.cluster rockets_cluster, 10 CP | rocket_turret.guided rockets_guided, 9 CP |
| heavy_flak_tower (heavy_flak_tower) | Medium | 7 | heavy_flak_tower.heavy aa_heavy_flak_area, 7 CP | heavy_flak_tower.bofors aa_40_steady, 6 CP |
| laser_ad_station (laser_ad_station) | Medium | 5 | laser_ad_station.laser antidrone_laser, 5 CP | laser_ad_station.net antidrone_net, 5 CP |
| troop_shelter (troop_shelter) | Medium | 5 | không nhánh / no branch shelter_troops | không nhánh / no branch shelter_troops |
| heavy_turret (heavy_turret) | Large | 18 | heavy_turret.coastal gun_coastal_long, 18 CP | heavy_turret.bastion fortress_close_defence, 18 CP |
| missile_battery (missile_battery) | Large | 13 | missile_battery.pac3 intercept_heavy_missiles, 9 CP | missile_battery.lrr sam_long_radar, 12 CP |
| drone_hangar (drone_hangar) | Large | 12 | drone_hangar.lancet drone_loitering, 14 CP | drone_hangar.swarm drone_fpv_swarm, 14 CP |
| artillery_emplacement (artillery_emplacement) | Large | 12 | artillery_emplacement.cb counter_battery, 12 CP | artillery_emplacement.mortar mortar_lobbed, 12 CP |
| shield_tower (shield_tower) | Large | 10 | shield_tower.bulwark shield_dome, 10 CP | shield_tower.ward tower_shields, 10 CP |

Hai nhánh của một tháp khác nhau về việc làm (towerRole riêng), không chỉ về số. / The two branches of a card differ in what they do (their own towerRole), not only in numbers.

#### 6b. Xây lại tháp / Rebuilding towers

Không gọi khi xe địch trong 20 m; nhà chính còn 25% máu: tháp nhỏ hoặc vừa rẻ nhất đã đổ xây lại miễn phí, một lần; Đối công: không xây lại sau 600 s. Giá riêng từng tháp (rebuildCp) ở bảng 6a. / No drop with an enemy within 20 m; at 25% HQ health the cheapest fallen small or medium tower comes back free, once; Showdown: no rebuilding after 600 s. Each tower's own price (rebuildCp) is in table 6a.

#### 6c. Tường / Walls

Tối đa 2 tuyến mỗi trại, 3 tuyến lùi ở Phòng thủ; 3-5 đoạn 12 x 2 m mỗi tuyến; 75 bản đồ, 279 tuyến, 1079 đoạn. INTACT/RUBBLE theo trạng thái NavGrid dựng sẵn, đổi ở tick sau khi đoạn bị phá; gạch vụn đi qua được, chậm 20%. Xe phá tường x1.5 chỉ lên tường. Đội AI chọn cổng hay phá tường theo routeCost + threatCost + breachTimeCost. AI địch: brandt t_wall, kessler t_wall, varga gun_wall, default hesco. / Up to 2 lines a camp, 3 fall-back lines in Defend; 3-5 segments of 12 x 2 m a line; 75 maps, 279 lines, 1079 segments. INTACT/RUBBLE on prebuilt NavGrid states, switched at the tick after a segment falls; rubble is passable, 20% slower. Wall breakers x1.5 on walls only. AI squads choose the gate or a breach by routeCost + threatCost + breachTimeCost (aiModeProfile wallRoute).

#### 6d. Kiểu nhà chính / HQ types

Một kỹ năng, hồi 120 s, một nút trên HUD. AI: brandt fortress, kessler fortress, varga garrison, orlov shield, aurel shield, Easy garrison, Normal fortress, Hard shield, VeryHard fortress. / One skill, 120 s cooldown, one HUD button.

#### 7. Phòng thủ / Vô tận theo cấp nhà chính / Defend and Endless by HQ level

Sức đợt = ReferenceBasePower(cấp nhà chính) x độ khó x đường cong đợt x tiến độ chiến dịch. / Wave strength = ReferenceBasePower(HQ level) x difficulty x wave curve x campaign progress. Căn cứ tham chiếu / The reference bases:

| HQ | Nhỏ / Small | Vừa / Medium | Lớn / Large | Mô-đun / Modules |
|---|---|---|---|---|
| 1 | guard_tower, mg_bunker, aa_turret | gun_turret |  | repair_bay |
| 2 | guard_tower, mg_bunker, aa_turret, at_gun_emplacement | gun_turret, atgm_tower |  | repair_bay |
| 3 | guard_tower, mg_bunker, aa_turret, at_gun_emplacement | gun_turret, heavy_flak_tower | heavy_turret | repair_bay, radar_station |
| 4 | guard_tower, mg_bunker, aa_turret, at_gun_emplacement, minefield | gun_turret, atgm_tower, heavy_flak_tower | heavy_turret | repair_bay, radar_station |
| 5 | guard_tower, mg_bunker, aa_turret, at_gun_emplacement, minefield, ew_tower | gun_turret, atgm_tower, c_ram | heavy_turret, missile_battery | repair_bay, radar_station, ammo_depot |

#### Chế độ Đối công / Showdown

| Trường / Field | Luật / Rule |
|---|---|
| winCondition | Phá nhà chính đối phương |
| loseCondition | Mất nhà chính |
| timeLimit | 12 phút |
| overtimeRule | Hết 12 phút: bên có nhà chính còn nhiều % máu hơn từ 5 điểm phần trăm trở lên thắng ngay; chênh dưới 5 điểm → đột tử 90 s (tắt chống bắn tỉa, không xây lại tháp, thu nhập ×2, không đặt lại hồi chiêu… |
| drawRule | Bằng nhau sau đột tử → hòa |
| scoreRule | Không có điểm phụ |
| catchUpPolicy | Chỉ bắt kịp thu nhập, trần +25%; không tiếp viện miễn phí |
| antiSnipeRule | Nhà chính chỉ nhận 25% sát thương từ pháo binh, tên lửa và máy bay bắn từ ngoài 60 m, cho tới khi outerDefenseBreached |
| breachRule | outerDefenseBreached khi quân mặt đất địch vào qua cổng chính (cổng trại là lối mở), hoặc một đoạn tường ngoài thành RUBBLE và mở được đường từ phía công vào trong căn cứ (kiểm bằng trạng thái NavGri… |
| escalation | Phút 6: thu nhập ×1,5 cho cả hai phe, trạm CP ngừng tạo CP; phút 10: tháp bị phá không xây lại (lần đã trừ CP thì hoàn tất) |
| mapEligibility | Chỉ bản đồ 300×300 đạt ngưỡng đối xứng của docs/checks/map_audit.md (không dùng 300×480) |

timeLimit 720, antiSnipeShare 0.25, antiSnipeRange 60, escalationAt 360, escalationIncome 1.5, rebuildCutoff 600, overtimeLead 0.05, suddenDeath 90, suddenDeathIncome 2, catchUpMax 0.25, baseRadius 46, neutralsMax 2

Bản đồ (300 x 300 đối xứng) / Maps (300 x 300 symmetric): ashfield, capital, coralisles, dunebreak, foundry, frostpeak, greenvale, ironport, junglepass, landingbeach, launchsite, lighthousebay, metrocity, openpit, orbitalgate, redrock, rustyard, saltflat, skyhold, swamp, veyra_old_quarter, whiteout.

#### 14. CP khởi đầu và đội mở màn / Starting CP and opening squads

CP khởi đầu x1.16 ở Conquest, Deathmatch, KingOfTheHill, Assault, Siege, Weekly, Defend, Endless, Survival, BossRush, Campaign, Showdown. Đội mở màn: mỗi vai lấy thẻ rẻ nhất của bộ bài, tối đa 60% CP khởi đầu. / Starting CP x1.16 in those modes; each role takes the deck's cheapest card of the role, within 60% of the starting CP.

| Chỉ huy / Commander | Vai / Roles |
|---|---|
| kade | mbt, scout |
| lind | engineer, repair, light |
| reyes | scout_heli, scout |
| kerr | scout, radar_scout, light |
| venn | fpv, scout |
| mendez | wheeled, light_tank, scout |
| brandt | bunker, engineer |
| dahl | artillery, scout |
| brenn | - |
| adler | scout, light |
| varro | cheap4, cheap4, cheap4 |
| reyn | mbt |
| quist | fortify, light, scout |
| okoye | - |

| Tướng địch / Enemy general | Vai / Roles |
|---|---|
| varga | tank |
| orlov | artillery, radar_scout |
| kessler | mine_layer, light |
| wolff | heli |
| sen | drone |
| venn | drone |
| thorne | mbt |
| aurel | heavy |
| default | scout, light |

Sheet: 04_can_cu_thap/Thap — Tháp (76 dòng, 153 cột)

| id | ten_en | ten_vi | ten_ngan_vi | ke_thua_tu | base_cp | mau_hp | mau_trong_tran_hp | giap_hong | giap_noc |
|---|---|---|---|---|---|---|---|---|---|
| aa_gun_tower | 40 mm AA gun | Pháo phòng không 40 mm | Pháo PK 40 mm |  | 0 | 1273 | 2800.6 | 2 | 2 |
| aa_turret | AA turret | Tháp phòng không | Tháp PK |  | 0 | 1100 | 2420.0 | 2 | 2 |
| aa_turret.flak |  |  | Tháp cao xạ | aa_turret | 0 | 1100 | 2420.0 | 2 | 2 |
| aa_turret.sam |  |  | Stinger | aa_turret | 0 | 1100 | 2420.0 | 2 | 2 |
| artillery_emplacement | Artillery emplacement | Trận địa pháo | Trận địa pháo |  | 0 | 1100 | 2420.0 | 1 | 1 |
| artillery_emplacement.cb |  |  | Phản pháo | artillery_emplacement | 0 | 1100 | 2420.0 | 1 | 1 |
| artillery_emplacement.mortar |  |  | Cối nặng | artillery_emplacement | 0 | 1100 | 2420.0 | 1 | 1 |
| at_gun_emplacement | Anti-tank gun emplacement | Ụ pháo chống tăng | Ụ chống tăng |  | 0 | 682 | 1500.4 | 1 | 1 |
| at_gun_emplacement.long |  |  | Pháo CT | at_gun_emplacement | 0 | 682 | 1500.4 | 1 | 1 |
| at_gun_emplacement.recoilless |  |  | SKZ | recoilless_gun_tower | 0 | 545 | 1199.0 | 1 | 1 |
| atgm_tower | ATGM tower | Tháp tên lửa chống tăng | Tháp ATGM |  | 0 | 900 | 1980.0 | 2 | 2 |
| atgm_tower.multi |  |  | Đa năng | atgm_tower | 0 | 900 | 1980.0 | 2 | 2 |
| atgm_tower.top |  |  | Đánh từ trên | atgm_tower | 0 | 900 | 1980.0 | 2 | 2 |
| barrage_balloon | Radar aerostat (JLENS) | Khí cầu neo radar (JLENS) | Khí cầu radar |  | 0 | 364 | 800.8 | 0 | 0 |
| blast_wall | Gabion blast wall | Tường chắn đạn | Tường chắn đạn |  | 0 | 1364 | 3000.8 | 3 | 3 |

*15 / 76 dòng đầu: xem sheet 04_can_cu_thap/Thap; in 10 / 153 cột; 75 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 04_can_cu_thap/Thap_vu_khi — Tháp: bệ vũ khí phụ (3 dòng, 8 cột)

| id | thap_id | thu_tu | weapon | aim | slot |
|---|---|---|---|---|---|
| aa_turret/0 | aa_turret | 0 | sam | Turret | missile |
| heavy_turret.bastion/0 | heavy_turret.bastion | 0 | hmg_roof | Free | gun |
| heavy_turret.bastion/1 | heavy_turret.bastion | 1 | hmg_roof | Free | gun |

Sheet: 04_can_cu_thap/Tuong — Tường (3 dòng, 81 cột)

| id | ten_en | ten_vi | ten_ngan_vi | base_cp | mau_hp | mau_trong_tran_hp | giap_hong | giap_noc | cong_trinh |
|---|---|---|---|---|---|---|---|---|---|
| wall_gun | Gun wall | Tường gắn súng | Tường súng | 0 | 2880 | 6336.0 | 3 | 3 | TRUE |
| wall_hesco | HESCO wall | Tường HESCO | HESCO | 0 | 2400 | 5280.0 | 3 | 3 | TRUE |
| wall_t | T-wall | Tường chữ T | Tường T | 0 | 3840 | 8448.0 | 4 | 4 | TRUE |

*in 10 / 81 cột; 38 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 04_can_cu_thap/Tuong_luat — Tường: luật (11 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so | gia_tri_chu |
|---|---|---|---|---|
| ai.brandt | base.walls | brandt |  | t_wall |
| ai.default | base.walls | default |  | hesco |
| ai.kessler | base.walls | kessler |  | t_wall |
| ai.varga | base.walls | varga |  | gun_wall |
| breakerMultiplier | base.walls | breakerMultiplier | 1.5 |  |
| breakers | base.walls | breakers |  | armored_bulldozer;engineer_vehicle;demolition_line_vehicle |
| campLines | base.walls | campLines | 2 |  |
| default | base.walls | default |  | hesco |
| fortressLines | base.walls | fortressLines | 3 |  |
| rubbleSlow | base.walls | rubbleSlow | 0.2 |  |
| segmentHp | base.walls | segmentHp | 2400 |  |

Sheet: 04_can_cu_thap/Nha_chinh — Nhà chính (4 dòng, 84 cột)

| id | ten_en | ten_vi | ten_ngan_vi | lop | ke_thua_tu | base_cp | mau_hp | mau_trong_tran_hp | giap_hong |
|---|---|---|---|---|---|---|---|---|---|
| headquarters | Headquarters | Sở chỉ huy | Sở chỉ huy | Defense |  | 0 | 9000 | 19800.0 | 4 |
| headquarters.fortress_air | Headquarters · AA Fortress | Sở chỉ huy · Pháo đài phòng không | Pháo đài PK | Defense | headquarters | 0 | 9000 | 19800.0 | 4 |
| headquarters.fortress_ground | Headquarters · Fortress | Sở chỉ huy · Pháo đài | SCH Pháo đài | Defense | headquarters | 0 | 9000 | 19800.0 | 4 |
| headquarters.shield | Headquarters · Shield | Sở chỉ huy · Lá chắn | SCH Lá chắn | Defense | headquarters | 0 | 9000 | 19800.0 | 4 |

*in 10 / 84 cột; 46 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 04_can_cu_thap/Nha_chinh_kieu — Nhà chính: kiểu (3 dòng, 14 cột)

| id | nha_chinh | ai_air_share | air | barrage | charges | clear | dome_seconds_s | ground | hq |
|---|---|---|---|---|---|---|---|---|---|
| fortress | headquarters.fortress_ground;headquarters.fortress_air | 0.3 | headquarters.fortress_air | hq_barrage |  |  |  | headquarters.fortress_ground |  |
| garrison |  |  |  |  |  | 30 |  |  |  |
| shield | headquarters.shield |  |  |  | 4 |  | 10 |  | headquarters.shield |

*in 10 / 14 cột; 2 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 04_can_cu_thap/Mo_dun_tien_ich — Mô-đun tiện ích (9 dòng, 101 cột)

| id | ten_en | ten_vi | ten_ngan_vi | base_cp | mau_hp | mau_trong_tran_hp | giap_hong | giap_noc | cong_trinh |
|---|---|---|---|---|---|---|---|---|---|
| airfield | Airfield | Sân bay dã chiến | Sân bay | 0 | 1600 | 3520.0 | 1 | 1 | TRUE |
| airfield.hangar |  |  | Nhà chứa | 0 | 1800 | 3960.0 | 2 | 2 | TRUE |
| airfield.service |  |  |  | 0 | 1600 | 3520.0 | 1 | 1 | TRUE |
| ammo_depot | Ammunition depot | Kho đạn | Kho đạn | 0 | 1200 | 2640.0 | 2 | 2 | TRUE |
| fire_control_centre | Fire-control centre | Trung tâm điều khiển hỏa lực | TT hỏa lực | 0 | 1136 | 2499.2 | 1 | 1 | TRUE |
| logistics_station | Logistics station | Trạm hậu cần | Trạm hậu cần | 0 | 1400 | 3080.0 | 1 | 1 | TRUE |
| radar_station | Radar station | Trạm radar | Trạm radar | 0 | 1200 | 2640.0 | 1 | 1 | TRUE |
| repair_bay | Repair bay | Xưởng sửa chữa | Xưởng sửa chữa | 0 | 1600 | 3520.0 | 2 | 2 | TRUE |
| visual_jammer | Visual jammer | Máy tạo nhiễu tầm nhìn | Nhiễu tầm nhìn | 0 | 909 | 1999.8 | 1 | 1 | TRUE |

*in 10 / 101 cột; 58 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 04_can_cu_thap/Loadout_can_cu — Ô căn cứ theo cấp HQ (10 dòng, 9 cột)

| id | bang | cap_hq | large | medium | small | utility |
|---|---|---|---|---|---|---|
| levels/1 | levels | 1 | 0 | 1 | 3 | 1 |
| levels/2 | levels | 2 | 0 | 2 | 4 | 1 |
| levels/3 | levels | 3 | 1 | 2 | 4 | 2 |
| levels/4 | levels | 4 | 1 | 3 | 5 | 2 |
| levels/5 | levels | 5 | 2 | 3 | 6 | 3 |
| longLevels/1 | longLevels | 1 | 0 | 1 | 4 | 1 |
| longLevels/2 | longLevels | 2 | 1 | 2 | 5 | 1 |
| longLevels/3 | longLevels | 3 | 1 | 3 | 6 | 2 |
| longLevels/4 | longLevels | 4 | 2 | 4 | 7 | 3 |
| longLevels/5 | longLevels | 5 | 3 | 5 | 8 | 4 |

Sheet: 04_can_cu_thap/Xay_lai — Xây lại tháp theo cỡ ô (3 dòng, 6 cột)

| id | cooldown_s | cp | drop |
|---|---|---|---|
| large | 60 | 7 | 5 |
| medium | 40 | 4 | 3.5 |
| small | 25 | 2 | 2.5 |

Sheet: 04_can_cu_thap/Thap_gia_cong_thuc — Tháp: công thức giá xây lại (60 dòng, 22 cột)

| id | co_o | vai_tro_gia | cach_tinh | he_so_trung_vi_doa | role_dps | mau_tren_cp_nhom | dps_tren_cp_nhom | so_xe_nhom | he_so_dung_yen |
|---|---|---|---|---|---|---|---|---|---|
| aa_turret | Small | air | chien_dau | 0.9974999999999999 | 219.4167303643507 | 158.0 | 30.334200000000003 | 11 | 0.625 |
| aa_turret.flak | Small | air | chien_dau | 0.9974999999999999 | 240.3845953002611 | 158.0 | 30.334200000000003 | 11 | 0.625 |
| aa_turret.sam | Small | air | chien_dau | 0.9974999999999999 | 49.64061096136568 | 158.0 | 30.334200000000003 | 11 | 0.725 |
| artillery_emplacement | Large | ground | chien_dau | 1.1099999999999999 | 72.08791208791209 | 109.28928571428571 | 8.485147678117894 | 12 | 0.725 |
| artillery_emplacement.cb | Large | ground | chien_dau | 1.1099999999999999 | 68.64922687931538 | 109.28928571428571 | 8.485147678117894 | 12 | 0.725 |
| artillery_emplacement.mortar | Large | ground | chien_dau | 1.1099999999999999 | 73.33333333333334 | 109.28928571428571 | 8.485147678117894 | 12 | 0.725 |
| at_gun_emplacement | Small | at | chien_dau | 0.9974999999999999 | 34.0 | 288.1801801801802 | 7.741351648351649 | 23 | 0.625 |
| at_gun_emplacement.long | Small | at | chien_dau | 0.9974999999999999 | 34.0 | 288.1801801801802 | 7.741351648351649 | 23 | 0.625 |
| at_gun_emplacement.recoilless | Small | at | chien_dau | 1.1099999999999999 | 22.938530734632685 | 288.1801801801802 | 7.741351648351649 | 23 | 0.575 |
| atgm_tower | Medium | at | chien_dau | 0.9375 | 82.88288288288288 | 266.56666666666666 | 7.741351648351649 | 23 | 0.625 |
| atgm_tower.multi | Medium | at | chien_dau | 0.9375 | 70.45045045045045 | 266.56666666666666 | 7.741351648351649 | 23 | 0.625 |
| atgm_tower.top | Medium | at | chien_dau | 0.9375 | 88.46153846153847 | 266.56666666666666 | 7.741351648351649 | 23 | 0.625 |
| c_ram | Medium | util:intercept | intercept |  |  |  |  |  |  |
| c_ram.centurion | Medium | util:intercept | intercept |  |  |  |  |  |  |
| c_ram.dome | Medium | util:intercept | intercept |  |  |  |  |  |  |

*15 / 60 dòng đầu: xem sheet 04_can_cu_thap/Thap_gia_cong_thuc; in 10 / 22 cột; 10 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 04_can_cu_thap/Can_cu_luat — Căn cứ: luật (21 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so | gia_tri_chu | don_vi |
|---|---|---|---|---|---|
| base.roster | base.roster |  |  | guard_tower;mg_bunker;at_gun_emplacement;aa_turret;ew_tower… |  |
| longForward.medium | base.longForward | medium | 2 |  |  |
| longForward.small | base.longForward | small | 6 |  |  |
| outpost.cp | base.outpost | cp | 6 |  | CP |
| outpost.slots | base.outpost | slots | 2 |  |  |
| rebuild.delay | base.rebuild | delay | 4 |  | s |
| rebuild.enemyRadius | base.rebuild | enemyRadius | 20 |  | m |
| rebuild.hqRescue | base.rebuild | hqRescue | 0.25 |  |  |
| rebuild.showdownCutoff | base.rebuild | showdownCutoff | 600 |  | s |
| roles.Assault | base.roles | Assault |  | Target |  |
| roles.BossRush | base.roles | BossRush |  | None |  |
| roles.Campaign | base.roles | Campaign |  | None |  |
| roles.Conquest | base.roles | Conquest |  | Anchor |  |
| roles.Deathmatch | base.roles | Deathmatch |  | Anchor |  |
| roles.Defend | base.roles | Defend |  | Defend |  |
| roles.Endless | base.roles | Endless |  | Defend |  |
| roles.KingOfTheHill | base.roles | KingOfTheHill |  | Anchor |  |
| roles.Showdown | base.roles | Showdown |  | Target |  |
| roles.Siege | base.roles | Siege |  | Target |  |
| roles.Survival | base.roles | Survival |  | None |  |
| roles.Weekly | base.roles | Weekly |  | Target |  |

## 7. Công thành và Phòng thủ

Trạng thái: Một phần — chờ prompt xuat_luot3 (sheet Dot_phong_thu)

Nguồn dữ liệu: 04_can_cu_thap/Dot_phong_thu; 04_can_cu_thap/Can_cu_AI_cap. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §7. Công thành.

- **Pháo đài chiếm 45% chiến trường** ở góc đông bắc: tuyến ngoài (trạm radar), tường chữ L có cổng chính đóng và cửa phụ mở, thành trong có sở chỉ huy. Tháp đặt trên ô có cỡ theo roster tháp mới, lấy từ loadout của phe giữ (AI theo độ khó và tướng); vòng trong mạnh hơn.
- **Set-piece:** tường sập có hoạt cảnh rồi thành đống gạch đi qua được; cổng thép bị phá đổ vào trong; máy phát khiên giữ vòm khiên che thành trong, phá máy cuối cùng thì vòm tắt kèm chớp sáng; siêu pháo bắn theo đồng hồ đếm ngược vào cụm quân đông nhất (phá nó là mục tiêu phụ: 25 CP, 100 xu); đèn pha quét và còi báo động ban đêm; chi viện địch đến bằng tàu hỏa trên đường ray hoặc máy bay vận tải hạ cánh trên đường băng, báo trước 10 giây.
- **Phòng thủ:** ba tuyến ngoài, giữa, trong và sở chỉ huy là trận chốt cuối. Mất một tuyến thì tháp ở đó nổ và người chơi được thưởng CP rút lui (24 rồi 32 CP); tuyến trong có tháp mạnh hơn. Căn cứ dùng đúng loadout của người chơi. Đợt địch kế tiếp hiện trước bằng icon và số lượng (đợt được lên kế hoạch trước nên đúng y như thứ đổ bộ); đợt là bầy xe rẻ lớn dần, trần 48 xe cùng lúc.
- **Đầm Lầy và Quần Đảo San Hô** giữ pháo đài kiểu cũ ở góc: tường mới sẽ cắt mọi đường đắp của hai bản đồ này.
- **Đo (độ khó Thường, 5 seed):** Công thành thắng 5/5 (9,7–17,8 phút); Phòng thủ giữ 3/5 trên 5 bản đồ và 5/5 ở bài kiểm tra kết thúc trận; Vô tận: sở chỉ huy rơi ở phút 10,3–11,7.

Sheet: 04_can_cu_thap/Dot_phong_thu — Loadout phòng thủ tham chiếu (5 dòng, 10 cột)

| id | small | medium | large | utilities | he_so_do_kho | duong_cong_dot | cap_hq |
|---|---|---|---|---|---|---|---|
| hq1 | guard_tower;mg_bunker;aa_turret | gun_turret |  | repair_bay | CHUA_AP:prompt_xuat_luot3 | CHUA_AP:prompt_xuat_luot3 | 1 |
| hq2 | guard_tower;mg_bunker;aa_turret;at_gun_emplacement | gun_turret;atgm_tower |  | repair_bay | CHUA_AP:prompt_xuat_luot3 | CHUA_AP:prompt_xuat_luot3 | 2 |
| hq3 | guard_tower;mg_bunker;aa_turret;at_gun_emplacement | gun_turret;heavy_flak_tower | heavy_turret | repair_bay;radar_station | CHUA_AP:prompt_xuat_luot3 | CHUA_AP:prompt_xuat_luot3 | 3 |
| hq4 | guard_tower;mg_bunker;aa_turret;at_gun_emplacement;minefield | gun_turret;atgm_tower;heavy_flak_tower | heavy_turret | repair_bay;radar_station | CHUA_AP:prompt_xuat_luot3 | CHUA_AP:prompt_xuat_luot3 | 4 |
| hq5 | guard_tower;mg_bunker;aa_turret;at_gun_emplacement;minefiel… | gun_turret;atgm_tower;c_ram | heavy_turret;missile_battery | repair_bay;radar_station;ammo_depot | CHUA_AP:prompt_xuat_luot3 | CHUA_AP:prompt_xuat_luot3 | 5 |

Sheet: 04_can_cu_thap/Can_cu_AI_cap — AI xây căn cứ: cấp HQ theo độ khó (4 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so |
|---|---|---|---|
| Easy | base.ai.levels | Easy | 2 |
| Hard | base.ai.levels | Hard | 5 |
| Normal | base.ai.levels | Normal | 3 |
| VeryHard | base.ai.levels | VeryHard | 5 |

### 7b. Biển, hộ tống, bản đồ dài, roster mới và đòn lớn

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do_tuyen_bien; 08_ban_do/Ban_do_bien_lan; 08_ban_do/Ban_do_bien_phao; 08_ban_do/Ban_do_bien_do_bo. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §7b.

#### Lighthouse Bay và hải chiến (prompt 16 A–D)

- **Lighthouse Bay:** bờ biển đá, 2 vịnh có bãi và cầu tàu, hải đăng trên mũi đất (giữ nó thì thấy hạm đội), 2 trận địa pháo bờ biển chiếm được (chỉ bắn tàu), làng chài và pháo đài cũ. Biển chiếm 36% map, 3 tuyến biển. Có bản Giữ cứ điểm, Sinh tồn, Công thành và bản dài.
- **Tàu chạy trên tuyến biển:** xe tăng chỉ bắn tới tuyến gần từ đầu cầu tàu và mũi đất; xe săn tăng tầm trung (38–42 m) bắn được từ sườn đá.
- **Leviathan (Kessler):** 9 bộ phận, giáp hông cấp 4, boong cấp 2; 3 pha: loạt pháo có cảnh báo, tên lửa hành trình, đổ tăng, trực thăng và gọi jet; pha 3 chạy ra biển theo đồng hồ, thoát được thì thua nhiệm vụ. Chết thì nghiêng, gãy đôi và chìm.
- **Hạm đội:** 2 tàu hộ vệ (CIWS che Leviathan), 3 xuồng tên lửa đánh đầu cầu tàu, tàu đổ bộ.
- **Chiến dịch và chế độ:** nhiệm vụ 4-11 "Leviathan" cuối chương 4 (mở nhánh Pháo bờ biển tầm xa của Pháo đài hạng nặng); Săn trùm tự chuyển sang Lighthouse Bay cho Leviathan rồi quay lại, mang theo quân, CP và đồng hồ; Tác chiến có mutator Bão biển và Hạm đội.

#### Hộ tống cho mọi boss (prompt 16 E–F)

Mỗi boss mang một nhóm đi cùng và thêm một nhóm ở mỗi lần đổi pha; số hộ tống còn sống tối đa theo độ khó: Easy 5, Normal 7, Hard 8, VeryHard 9, Heroic 9, Iron 9 (Săn trùm ít hơn). Mỗi nhóm có một xe phụ trợ (sửa boss, gây nhiễu tên lửa ta, phòng không che boss, đánh dấu quân ta) nên người chơi phải chọn đánh boss hay hộ tống trước. Hộ tống không rời boss quá 28 m, hạ được thì thưởng CP, có dấu cam, và thanh máu boss đếm số hộ tống.

| Boss | Đi cùng | Khi đổi pha |
|---|---|---|
| Juggernaut · Đoàn tàu bọc thép | Xe bọc thép bánh lốp, Xe bọc thép bánh lốp, Pháo cao xạ tự hành (phòng không che boss), Xe bọc thép bánh lốp (đánh dấu quân ta) | Tăng nhẹ lội nước, Tăng nhẹ lội nước, Xe công binh (sửa boss) |
| Tempest · Behemoth pháo điện từ | Tăng chủ lực, Xe gây nhiễu điện tử (gây nhiễu tên lửa ta), Xe gây nhiễu điện tử (gây nhiễu tên lửa ta), Xe tên lửa phòng không tầm trung (phòng không che boss) | Xe gây nhiễu điện tử (gây nhiễu tên lửa ta), Xe gây nhiễu điện tử (gây nhiễu tên lửa ta) |
| Behemoth · Quái vật thép | Tăng chủ lực, Tăng chủ lực, Tăng hạng nặng, Pháo cao xạ tự hành (phòng không che boss) | Tăng hạng nặng ★, Xe công binh (sửa boss) |
| Inferno · Behemoth phun lửa | Tăng phun lửa, Tăng phun lửa, Pháo cao xạ tự hành (phòng không che boss), Xe thả khói (thả khói) | Tăng phun lửa, Tăng phun lửa, Xe công binh (sửa boss) |
| Harpy · Trực thăng khổng lồ | Trực thăng tấn công, Trực thăng tấn công, Tiêm kích (phòng không che boss), Trực thăng trinh sát vũ trang (đánh dấu quân ta) | Trực thăng trinh sát vũ trang (đánh dấu quân ta) |
| Spectre · Máy bay pháo | Tiêm kích (phòng không che boss), Tiêm kích (phòng không che boss), Tiêm kích (phòng không che boss), UAV trinh sát (đánh dấu quân ta) | Tiêm kích (phòng không che boss), Tiêm kích (phòng không che boss) |
| Jötunn · Pháo đài di động | Tăng hạng nặng, Tăng hạng nặng, Xe tên lửa phòng không tầm trung (phòng không che boss), Xe công binh (sửa boss) | Xe công binh (sửa boss) |
| Hive · Pháo đài drone | Tăng chủ lực, Xe phòng không pháo – tên lửa (phòng không che boss), Xe tên lửa phòng không tầm trung (phòng không che boss) | Xe phóng drone FPV, Xe phóng drone FPV, UAV trinh sát (đánh dấu quân ta) |
| Bastion · Pháo đài | Pháo chống tăng tự hành, Pháo chống tăng tự hành, Tăng chủ lực, Xe phòng không pháo – tên lửa (phòng không che boss) | Tăng hạng nặng, Xe tên lửa phòng không tầm trung (phòng không che boss), Xe công binh (sửa boss) |
| Matriarch · Tàu mẹ drone | UAV tấn công, UAV tấn công, Tiêm kích (phòng không che boss), UAV trinh sát (đánh dấu quân ta) | Trực thăng trinh sát vũ trang (đánh dấu quân ta) |
| Icarus · Phi thuyền quỹ đạo | Tăng hạng nặng tinh nhuệ, Grad tinh nhuệ, UAV trinh sát (đánh dấu quân ta), Tiêm kích (phòng không che boss), Tiêm kích (phòng không che boss) | Xe phóng drone FPV tinh nhuệ, Xe gây nhiễu điện tử (gây nhiễu tên lửa ta) / Trực thăng tinh nhuệ, Xe công binh (sửa boss) |
| Nemesis · Đoàn tàu tên lửa | Xe chiến đấu bộ binh, Xe chiến đấu bộ binh, Xe tên lửa phòng không tầm trung (phòng không che boss), Trực thăng trinh sát vũ trang (đánh dấu quân ta) | Xe chiến đấu bộ binh, Xe chiến đấu bộ binh, Xe thả khói (thả khói) |
| Gungnir · Pháo điện từ đường ray | Tăng chủ lực, Tăng chủ lực, Pháo cao xạ tự hành (phòng không che boss), Xe radar phản pháo (đánh dấu quân ta) | Tăng chủ lực, Tăng chủ lực, Xe công binh (sửa boss) |
| Tartarus · Máy khoan |  | Xe chiến đấu bộ binh, Pháo cao xạ tự hành (phòng không che boss), Xe công binh (sửa boss) |
| Roc · Khí cầu chỉ huy | Tiêm kích (phòng không che boss), Tiêm kích (phòng không che boss), Tiêm kích (phòng không che boss) | Trực thăng tấn công, Trực thăng trinh sát vũ trang (đánh dấu quân ta) |
| Charybdis · Tàu đệm khí đổ bộ | Xuồng đệm khí hộ tống, Xuồng đệm khí hộ tống, Pháo cao xạ tự hành (phòng không che boss), Xuồng đệm khí hộ tống (đánh dấu quân ta) | Xuồng đệm khí hộ tống (đánh dấu quân ta) |
| Atlas · Xe chỉ huy siêu nặng | Tăng chủ lực ★, Tăng hạng nặng, Pháo cao xạ tự hành (phòng không che boss) | Tăng chủ lực ★, Tăng chủ lực ★, Pháo cao xạ tự hành (phòng không che boss) |

#### Bản đồ dài và căn cứ nhiều lớp (prompt 17 A–B)

- Công thành, Phòng thủ, Vô tận và Pháo đài tuần chơi trên bản dài: 300 m ngang, 480 m dọc theo hướng tấn công (đủ cho 20 map có bản công thành, cộng Lighthouse Bay); các chế độ khác giữ map 300 × 300 m.
- Căn cứ nhiều lớp: vùng đệm (răng rồng, hào, dây thép gai, 1–4 ụ bắn), trạm tiền tiêu và 8 cứ điểm, tường ngoài có cổng chính và 2 cửa phụ, sân trong, thành trong, rồi HQ. Quân phòng thủ thả xuống trong thành; quân tấn công thả dù xa dần lên sau mỗi vòng tường bị phá.
- Ô theo cấp HQ từ 4/1/0/1 (nhỏ/vừa/lớn/tiện ích) tới 8/5/3/4; nhãn ô mới: cổng ngoài, tường ngoài, sân trong, tường trong. Một loadout dùng cho cả trại và căn cứ dài: căn cứ dài chưa chỉnh thì mượn tháp của trại.
- Camera nhìn về phía tây trên map dài (zoom mặc định 21, xa nhất 50); bản đồ nhỏ giữ hình chữ nhật.
- Tìm đường: 150 × 240 ô, 1,9 MB; một đường hết chiều dài mất 5–6 ms trên máy bàn, khoảng 35 ms trên điện thoại (đo lại ở phase kiểm tra).

#### Đơn vị mới và rà soát roster (prompt 17 C–D)

- **Mới:** tiêm kích tàng hình (14 CP), drone yểm trợ (6 CP, bay theo máy bay có người lái và hút tên lửa bắn vào chúng), xe tăng laser (10 CP, tia mạnh dần ×0,3 → ×2 trong 6 giây), xe mang khiên (7 CP) và tháp khiên (ô lớn), xe lô cốt (6 CP, đứng yên 3 giây thì đào hầm: giáp trước dày hơn, tầm +30%), máy bay mẹ thả 8 drone FPV (8 CP), tháp tiếp sóng CP (ô nhỏ, tối đa 2 mỗi căn cứ). Giá đo bằng bộ đo giá trị thực chiến.
- **Gộp:** A-10 vào Cường kích (model Su-25, cả hai bộ vũ khí và 2 Kh-29, 15 CP); Ka-52 vào Trực thăng tấn công (giữ Hellfire tầm 55 m và Stinger, 11 CP); xe ATGM vào xe phóng drone FPV; công binh phá mìn vào Công binh; ụ súng vào tháp pháo. Model cũ giữ làm mẫu phụ.
- **Tăng hai nòng và tăng hạng nặng:** tăng hai nòng bắn 2 phát 120 mm một lượt, nạp 7 giây, hạ xe tăng nhanh nhất (37,9 s); tăng hạng nặng đổi sang đạn nổ khi bắn công trình và xe nhẹ, 12 CP, sống dai và phá công trình tốt nhất theo CP.
- **Save:** giữ hạng cao hơn, hoàn xu và bản thiết kế của thẻ hạng thấp; Ka-52 đã mua được hoàn 3.500 xu; ụ súng trong loadout thành tháp pháo.

#### Đòn lớn của mọi boss (prompt 18)

Mỗi boss có một đòn lớn lấy từ cùng một hệ dữ liệu (mẫu hình dạng + tham số). Đòn đầu tiên khoảng 30 giây sau khi boss xuất hiện; luôn có cảnh báo trên mặt đất; phá bộ phận mang đòn trong lúc cảnh báo thì đòn yếu đi hoặc bị hủy; quân ta biết né khỏi vùng cảnh báo. Theo độ khó: Easy sát thương ×1, hồi ×1.2, cảnh báo +1 s; Normal sát thương ×1, hồi ×1; Hard sát thương ×1, hồi ×0.9; VeryHard sát thương ×1, hồi ×0.8; Heroic sát thương ×1, hồi ×0.8; Iron sát thương ×1, hồi ×0.8.

Bộ phận mới: bệ dựng tên lửa của Doomsday Train, khoang bom của Hive Carrier và của Khí cầu chỉ huy. Prompt 19: đòn của Icarus là mưa thanh tungsten từ vệ tinh (thay cho tia laser quét); từ prompt 20 mini boss dùng đòn lớn thu nhỏ (sát thương ×0,7, hồi chiêu ×1,3).

Sheet: 08_ban_do/Ban_do_tuyen_bien — Bản đồ: tuyến biển (nút) (87 dòng, 10 cột)

| id | ban_do_id | thu_tu | id_goc | kind | lane | x_m | z_m |
|---|---|---|---|---|---|---|---|
| lighthousebay_conquest/far_0 | lighthousebay_conquest | 14 | far_0 | exit | far | -5.73 | -175.43 |
| lighthousebay_conquest/far_1 | lighthousebay_conquest | 15 | far_1 | track | far | 28.28 | -141.42 |
| lighthousebay_conquest/far_2 | lighthousebay_conquest | 16 | far_2 | track | far | 56.57 | -113.14 |
| lighthousebay_conquest/far_3 | lighthousebay_conquest | 17 | far_3 | track | far | 84.85 | -84.85 |
| lighthousebay_conquest/far_4 | lighthousebay_conquest | 18 | far_4 | track | far | 113.14 | -56.57 |
| lighthousebay_conquest/far_5 | lighthousebay_conquest | 19 | far_5 | track | far | 141.42 | -28.28 |
| lighthousebay_conquest/far_6 | lighthousebay_conquest | 20 | far_6 | exit | far | 175.43 | 5.73 |
| lighthousebay_conquest/hold_sea_far_2 | lighthousebay_conquest | 26 | hold_sea_far_2 | holding | far | 69.3 | -125.87 |
| lighthousebay_conquest/hold_sea_far_3 | lighthousebay_conquest | 27 | hold_sea_far_3 | holding | far | 97.58 | -97.58 |
| lighthousebay_conquest/hold_sea_far_4 | lighthousebay_conquest | 28 | hold_sea_far_4 | holding | far | 125.87 | -69.3 |
| lighthousebay_conquest/hold_shore_near_1 | lighthousebay_conquest | 21 | hold_shore_near_1 | holding | near | -2.83 | -110.31 |
| lighthousebay_conquest/hold_shore_near_2 | lighthousebay_conquest | 22 | hold_shore_near_2 | holding | near | 25.46 | -82.02 |
| lighthousebay_conquest/hold_shore_near_3 | lighthousebay_conquest | 23 | hold_shore_near_3 | holding | near | 53.74 | -53.74 |
| lighthousebay_conquest/hold_shore_near_4 | lighthousebay_conquest | 24 | hold_shore_near_4 | holding | near | 82.02 | -25.46 |
| lighthousebay_conquest/hold_shore_near_5 | lighthousebay_conquest | 25 | hold_shore_near_5 | holding | near | 110.31 | 2.83 |

*15 / 87 dòng đầu: xem sheet 08_ban_do/Ban_do_tuyen_bien.*

Sheet: 08_ban_do/Ban_do_bien_lan — Biển: làn tàu (9 dòng, 9 cột)

| id | ban_do_id | thu_tu | end | id_goc | patrol | w |
|---|---|---|---|---|---|---|
| lighthousebay_conquest/far | lighthousebay_conquest | 2 | 88.1 | far | 76.0 | 120.0 |
| lighthousebay_conquest/mid | lighthousebay_conquest | 1 | 102.1 | mid | 82.0 | 106.0 |
| lighthousebay_conquest/near | lighthousebay_conquest | 0 | 116.1 | near | 88.0 | 92.0 |
| lighthousebay_sandbox/far | lighthousebay_sandbox | 2 | 88.1 | far | 76.0 | 120.0 |
| lighthousebay_sandbox/mid | lighthousebay_sandbox | 1 | 102.1 | mid | 82.0 | 106.0 |
| lighthousebay_sandbox/near | lighthousebay_sandbox | 0 | 116.1 | near | 88.0 | 92.0 |
| lighthousebay_siege/far | lighthousebay_siege | 2 | 88.1 | far | 76.0 | 120.0 |
| lighthousebay_siege/mid | lighthousebay_siege | 1 | 102.1 | mid | 82.0 | 106.0 |
| lighthousebay_siege/near | lighthousebay_siege | 0 | 116.1 | near | 88.0 | 92.0 |

Sheet: 08_ban_do/Ban_do_bien_phao — Biển: khẩu đội bờ (6 dòng, 9 cột)

| id | ban_do_id | thu_tu | heading_deg | id_goc | x_m | z_m |
|---|---|---|---|---|---|---|
| lighthousebay_conquest/battery_e | lighthousebay_conquest | 1 | 135 | battery_e | 84.85 | 62.23 |
| lighthousebay_conquest/battery_w | lighthousebay_conquest | 0 | 135 | battery_w | -62.23 | -84.85 |
| lighthousebay_sandbox/battery_e | lighthousebay_sandbox | 1 | 135 | battery_e | 84.85 | 62.23 |
| lighthousebay_sandbox/battery_w | lighthousebay_sandbox | 0 | 135 | battery_w | -62.23 | -84.85 |
| lighthousebay_siege/battery_e | lighthousebay_siege | 1 | 135 | battery_e | 84.85 | 62.23 |
| lighthousebay_siege/battery_w | lighthousebay_siege | 0 | 135 | battery_w | -62.23 | -84.85 |

Sheet: 08_ban_do/Ban_do_bien_do_bo — Biển: điểm đổ bộ (12 dòng, 8 cột)

| id | ban_do_id | thu_tu | inland | x_m | z_m |
|---|---|---|---|---|---|
| lighthousebay_conquest/0 | lighthousebay_conquest | 0 | -42.31;-59.51 | -34.89 | -66.94 |
| lighthousebay_conquest/1 | lighthousebay_conquest | 1 | -49.15;-72.47 | -41.72 | -79.9 |
| lighthousebay_conquest/2 | lighthousebay_conquest | 2 | 59.51;42.31 | 66.94 | 34.89 |
| lighthousebay_conquest/3 | lighthousebay_conquest | 3 | 72.47;49.15 | 79.9 | 41.72 |
| lighthousebay_sandbox/0 | lighthousebay_sandbox | 0 | -42.31;-59.51 | -34.89 | -66.94 |
| lighthousebay_sandbox/1 | lighthousebay_sandbox | 1 | -49.15;-72.47 | -41.72 | -79.9 |
| lighthousebay_sandbox/2 | lighthousebay_sandbox | 2 | 59.51;42.31 | 66.94 | 34.89 |
| lighthousebay_sandbox/3 | lighthousebay_sandbox | 3 | 72.47;49.15 | 79.9 | 41.72 |
| lighthousebay_siege/0 | lighthousebay_siege | 0 | -42.31;-59.51 | -34.89 | -66.94 |
| lighthousebay_siege/1 | lighthousebay_siege | 1 | -49.15;-72.47 | -41.72 | -79.9 |
| lighthousebay_siege/2 | lighthousebay_siege | 2 | 59.51;42.31 | 66.94 | 34.89 |
| lighthousebay_siege/3 | lighthousebay_siege | 3 | 72.47;49.15 | 79.9 | 41.72 |

## 8. Phương tiện

Trạng thái: Đã áp

Nguồn dữ liệu: 02_phuong_tien/Xe; 02_phuong_tien/Xe_vu_khi; 02_phuong_tien/Xe_bo_phan; 02_phuong_tien/Xe_ten_lua; 02_phuong_tien/Nhanh_xe; 02_phuong_tien/Ky_nang; 02_phuong_tien/Tinh_nhue_luat; 02_phuong_tien/May_bay_so_phat; 02_phuong_tien/Do_ben. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §8. Phương tiện, §8b.

#### 8. Phương tiện

Chỉ số gốc (hạng 1, chưa trang bị). DPS = sát thương mỗi loạt / chu kỳ bắn, cộng mọi vũ khí, nhân hệ số giáp (phần 10). Hạng thẻ cộng +5% máu và sát thương mỗi hạng (tối đa hạng 10: +45%).

**Nguồn tham khảo.** Dòng "Tham khảo" trên mỗi thẻ (xe, xe tinh nhuệ, tháp, nhánh hạng 7, boss) ghi hệ thống ngoài đời thật và phim hoặc game mà model được dựng theo, lấy từ Tools/docs/unit_refs.json. Tệp này tổng hợp từ các tham chiếu chủ dự án yêu cầu trong DECISIONS.md (19R, 19U, 20V, 20Y, 21H), chú thích của các script dựng model Blender, tên thật của vũ khí trong balance.json và kiến thức chung về khí tài; mục ghi "ước đoán" là suy đoán, chưa có nguồn ghi rõ.

![Model thường và model chi tiết (đồ họa Cao) của 12 xe phổ biến nhất.](../images/02_phuong_tien/shots_hd.png)

*Hình: Model thường và model chi tiết (đồ họa Cao) của 12 xe phổ biến nhất. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

#### 8b. Miêu tả, hình dạng và mở khóa

Miêu tả: dòng Cách đánh và Mạnh / yếu của thẻ Hướng dẫn trong game. Hình dạng: cột "Hình dạng (cho AI vẽ)" của file cân bằng (sheet Phương tiện, Công trình, Boss), bản mô tả để dựng model (Tools/docs/unit_sheet.json). Mở khóa: theo dữ liệu chiến dịch sau prompt 25 D2 (màn mở, giá mua sớm, chiến lợi phẩm cốt truyện).

#### Boss (41)

| Đơn vị | Miêu tả | Hình dạng (bản vẽ) | Mở khóa |
|---|---|---|---|
| **Bastion Mk.0 · Pháo đài nguyên mẫu** `bastion_mk0` | chiếc Bastion đầu tiên của Brandt: một khẩu cối hạng nặng và hai tháp pháo 40 mm trên xích, bò chậm về phía căn cứ ta. mặt trước dày, chậm; hai tháp pháo là thứ phòng thủ gần duy nhất. | Dựa trên: 2B8 240 mm, Bofors 40 mm · Sandcrawler (Star Wars) — ước đoán: bản đầu, nhỏ của Bastion. Kích thước hiện 24.0 × 9.9 × 9.7 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss chủ lực… | — |
| **Inferno · Behemoth phun lửa** `behemoth_inferno` | hai súng phun lửa lớn (20 m) đốt cháy mặt đất; hộp rốc-két nhiệt áp đánh tầm 10–46 m; còn 70% máu gọi 2 tăng tinh nhuệ. thiêu chảy xe nhẹ và xe tăng tới gần; yếu trước máy bay vì chỉ có một khẩu pháo… | Dựa trên: TOS-1A, Object 279 (1959) · Baneblade (Warhammer 40,000) — ước đoán: Behemoth phun lửa, thùng nhiên liệu đỏ. Kích thước hiện 17.0 × 8.8 × 7.5 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss… | — |
| **Harpy · Trực thăng khổng lồ** `mega_gunship` | hai giàn rốc-két, hai pháo 30 mm, một súng máy nhiều nòng và mỗi bên cửa một súng máy 12,7 mm; thả mồi nhiệt liên tục, hộ tống là 2 trực thăng tấn công và 1 trực thăng trinh sát vũ trang đánh dấu mục… | Dựa trên: CH-47 Chinook (cỡ khung), ACH-47A 'Guns-A-Go-Go' — ước đoán (ACH-47A): trực thăng hai rô-to vũ trang hạng nặng. Kích thước hiện 23.6 × 15.3 × 7.0 m; boss chủ lực ×1,3–1,5 so với mẫu, mini b… | — |
| **Fenrir · Xe tiên phong** `fenrir` | nhanh: lao vào, xả hai hộp rốc-két rồi rút; cao xạ đuổi trực thăng. nhẹ hơn Jötunn nhiều; không giữ trận địa được. | Dựa trên: NASA Crawler-Transporter, Kharkovchanka (1959) · Sandcrawler (Star Wars) — ước đoán: biến thể của pháo đài di động. Kích thước hiện 16.2 × 9.1 × 8.3 m; boss chủ lực ×1,3–1,5 so với mẫu, min… | — |
| **Behemoth Mk.0 · Behemoth nguyên mẫu** `behemoth_mk0` | bản lắp đầu tiên của Behemoth, chậm hơn bản hoàn chỉnh: pháo chính, hai pháo sườn và một giàn rốc-két trên cùng thân xe. mặt trước giáp cấp 3; không có pháo cao xạ và hệ thống bảo vệ chủ động, nên má… | Dựa trên: Object 279 (1959), giáp composite, APS và cảm biến hiện đại · Baneblade (Warhammer 40,000) — ước đoán: Behemoth đời đầu, nhỏ hơn. Kích thước hiện 17.0 × 10.1 × 7.3 m; boss chủ lực ×1,3–1,5… | — |
| **Juggernaut · Đoàn tàu bọc thép** `armored_train` | hai pháo nặng (42 m), hộp rốc-két, hai pháo cao xạ và súng máy; bị bắn thì núp trong khói, còn nửa máu thì tự vá 20% một lần. pháo của nó diệt xe tăng và xe nhẹ gần đường ray; nó không thể rời đường… | Dựa trên: tàu bọc thép Liên Xô BP-35, B-38 152 mm, 2B11 120 mm — ước đoán: đầu máy diesel bọc thép kéo toa pháo. Kích thước hiện 24.5 × 3.3 × 4.8 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơ… | — |
| **Tempest · Behemoth pháo điện từ** `behemoth_tempest` | pháo điện từ nạp năng lượng một giây (cuộn dây sáng lên) rồi xuyên thủng cả hàng tới 80 m; hai pháo điện từ bắn đất lẫn trời (55 m). trừng phạt xe đi thành hàng dọc; ở gần, EMP (22 m) làm choáng xe m… | Dựa trên: US Navy EMRG (pháo điện từ), Object 279 (1959) · Baneblade (Warhammer 40,000) — ước đoán: Behemoth hai tháp pháo điện từ. Kích thước hiện 17.0 × 7.0 × 6.8 m; boss chủ lực ×1,3–1,5 so với mẫ… | — |
| **Scylla · Tàu khu trục** `scylla` | nhanh hơn Leviathan, chạy tuyến gần bờ: pháo AK-130 130 mm đôi nã vào bờ, ống phóng bắn tên lửa chống hạm mỗi 15 giây, CIWS chặn tên lửa và drone. đủ gần để pháo xe tăng ở đầu cầu tàu bắn tới. | Dựa trên: Sovremenny-class (khu trục hạm), Kirov-class — Bản nhỏ của Leviathan. Kích thước hiện 48.8 × 9.2 × 14.2 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss chủ lực cùng dòng; bộ phậ… | — |
| **Nyx · Tàu khu trục tàng hình** `nyx` | tạm dùng thân Leviathan thu nhỏ. Pháo điện từ bắn mỗi 8 giây, hai CIWS chặn tên lửa và drone, rồi tới tên lửa chống hạm. Nó tàng hình: chỉ thấy ở gần hoặc ngay sau khi bắn. khó thấy; mỏng so với kích… | — | — |
| **Hive · Pháo đài drone** `fortress_hive` | không có pháo lớn: hai giàn phóng bầy drone tới 70 m, dàn tên lửa (62 m) và pháo cao xạ giữ bầu trời, còn thả thêm UAV tấn công. xé nát máy bay; drone của nó hại được xe tăng, nhưng xe tăng và pháo b… | Dựa trên: NASA Crawler-Transporter, ZALA Lancet-3, MIM-104 Patriot · Sandcrawler (Star Wars) — ước đoán: pháo đài bánh xích mang tổ drone. Kích thước hiện 16.4 × 9.3 × 8.5 m; boss chủ lực ×1,3–1,5 so… | — |
| **Locust · Tàu con drone** `locust` | khoang drone thả drone liên tục; cao xạ trên lưng. thân rất mỏng (giáp cấp 1): phòng không hạ nó nhanh. | Dựa trên: Airlander 10, drone FPV · Kirov Airship (Red Alert 2) — ước đoán: biến thể nhỏ của khí cầu mẹ. Kích thước hiện 25.4 × 12.6 × 10.6 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss… | — |
| **Stymphalos · Bầy UAV phản lực** `stymphalos` | tạm là một thân với khoang drone và cao xạ của tàu mẹ, nhanh. Nó bắn tên lửa nhỏ và thả drone liên tục. rất nhanh; giáp mỏng, phòng không hạ nó nhanh. | — | — |
| **Bastion · Pháo đài** `fortress_bastion` | khẩu cối hạng nặng bắn tầm 12–80 m, bốn tháp pháo tự động 40 mm (28 m) phủ mọi hướng, hai súng máy NSV giữ hai bên hông, còn nửa máu nó tự vá giáp một lần. pháo tự động xé nát xe nhẹ tới gần; giáp dà… | Dựa trên: 2B8 240 mm, Bofors 40 mm, 9M133 Kornet · Sandcrawler (Star Wars) — ước đoán: pháo đài bánh xích bọc giáp tấm dày. Kích thước hiện 40.0 × 16.5 × 16.1 m; boss chủ lực ×1,3–1,5 so với mẫu, min… | — |
| **Charybdis · Tàu đệm khí đổ bộ** `landing_hovercraft` | chạy theo lộ trình dọc bờ biển; cứ 35 giây dừng lại, hạ cửa đổ bộ và thả 3–4 xe lên bờ, tối đa năm lần. Bốn pháo CIWS sáu nòng che chắn cả đất lẫn trời (hai khẩu bắn hạ tên lửa và rốc-két) và hai dàn… | Dựa trên: LCAC, Zubr (Project 1232.2), A-22 Ogon 140 mm, AK-630 — Tàu đổ bộ đệm khí. Kích thước hiện 24.9 × 13.5 × 7.7 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss chủ lực cùng dòng; b… | — |
| **Behemoth Mk.II · Behemoth nâng cấp** `behemoth_mk2` | bản nâng cấp của Varga sau khi Behemoth gục: pháo chính, hai cao xạ và hệ thống bảo vệ chủ động bắn hạ tên lửa. mặt trước giáp cấp 4 dưới lớp băng; hông và sau mỏng hơn nhiều. | Dựa trên: Object 279 (1959), giáp composite, APS và cảm biến hiện đại · Baneblade (Warhammer 40,000) — ước đoán: Behemoth đời hai. Kích thước hiện 18.0 × 10.7 × 7.7 m; boss chủ lực ×1,3–1,5 so với mẫ… | — |
| **Cerberus · Đoàn xe ba khung** `cerberus` | tạm dùng thân Behemoth (pháo, cao xạ, ổ rốc-két). Pháo đầu bắn xe mặt đất, cao xạ giữa đuổi máy bay, ổ rốc-két sau phủ một vùng. mỗi bộ phận là một vũ khí riêng; chậm. | — | — |
| **Behemoth · Quái vật thép** `behemoth` | pháo chính hai nòng (40 m), pháo 120 mm, pháo cao xạ, tên lửa bắn cả đất lẫn trời (45 m) và bệ Kornet đôi sau tháp chính; còn 70% máu gọi 2 tăng tinh nhuệ. nghiền nát xe nhẹ và xe tăng; khắc tinh là… | Dựa trên: Object 279 (1959: bốn dải xích, thân dẹt), giáp composite, APS và cảm biến hiện đại, 2A65 152 mm · Baneblade (Warhammer 40,000) — ước đoán: 'thiết giáp hạm trên cạn' bốn cụm xích. Kích thướ… | — |
| **Atlas · Xe chỉ huy siêu nặng** `supreme_command` | chỉ có hai súng máy nhẹ; mọi quân địch trong 40 m quanh nó tăng 20% sát thương và 20% tốc độ bắn. Có cận vệ tinh nhuệ đi kèm, còn 60% máu thì gọi thêm. quân địch gần nó nguy hiểm hơn nhiều; bản thân… | Dựa trên: khung MZKT-7930, sở chỉ huy cơ động bọc thép — Tổng Tư Lệnh: xe chỉ huy siêu nặng bốn trục. Kích thước hiện 16.0 × 5.5 × 12.2 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss chủ… | — |
| **Tartarus · Máy khoan** `earth_borer` | chui xuống đất, khoan ngầm không bị nhắm tới dưới cụm xe mặt đất đông nhất của bạn, mặt đất nứt 2 giây rồi nó trồi lên gây rung chấn làm choáng mọi xe mặt đất trong 15 m. Mũi khoan và hai khẩu pháo k… | Dựa trên: 'Battle Mole' của Liên Xô, máy khoan hầm TBM, 2A70 100 mm — 'Earth Worm': máy khoan đất bọc thép ba đốt. Kích thước hiện 19.9 × 4.9 × 5.9 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ… | — |
| **Ixion · Xe tải mỏ bọc thép** `ixion` | xe tải mỏ bọc thép (BelAZ-75710) chạy thẳng khoảng 7 m/s và xoay rất chậm. Tháp pháo 125 mm hàn trên thùng xoay 360°, nạp đạn nổ mạnh với đám đông (nổ lõi 5 m, rìa 10 m) và đạn xuyên với mục tiêu đơn… | Dựa trên: BelAZ-75710 (xe tải mỏ lớn nhất thế giới), tháp pháo T-72 125 mm hàn trên thùng — Xe tải mỏ bọc thép của Thorne ở Deepcut Mine: ca-bin lệch trái, sáu bánh lớn, lưỡi húc chữ V (model tạm). K… | — |
| **Jötunn · Pháo đài di động** `mobile_fortress` | hai lựu pháo 203 mm (60 m), hộp rốc-két, pháo cao xạ, tháp 30 mm đôi chống drone và tên lửa; EMP làm choáng xe mặt đất trong 22 m; hộ tống là 2 tăng nặng và 1 xe công binh sửa cho nó, còn nửa máu thê… | Dựa trên: NASA Crawler-Transporter, Kharkovchanka (1959), 2A44 203 mm (2S7 Pion) · Sandcrawler (Star Wars) — ước đoán: pháo đài bánh xích bốn cụm, cầu chỉ huy lắp kính. Kích thước hiện 32.0 × 18.1 ×… | — |
| **Caspian · Tàu bay sát mặt nước** `caspian` | lao dọc bờ khoảng 6 giây mỗi lượt rồi vòng ra xa khoảng 20 giây; là mục tiêu trên mặt nước. Mỗi lượt lao nó phóng một tên lửa chống hạm vào cụm quân lớn nhất (có đánh dấu trước); hai pháo 23 mm đôi v… | Dựa trên: ekranoplan lớp Lun MD-160 ('Quái vật biển Caspi') — Thủy phi cơ hiệu ứng mặt đất. Kích thước hiện 36.0 × 26.5 × 10.9 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss chủ lực cùng… | — |
| **Hydra · Tàu ngầm mang drone** `hydra` | tạm dùng thân Typhon (pháo boong và cửa ống phóng, nhỏ và nhanh hơn). Nó lặn rồi nổi theo lịch ngắn, chỉ bắn khi nổi, và phóng tên lửa hành trình mỗi 16 giây. lúc lặn không đánh tới được; thân mỏng. | — | — |
| **Morrigan · Tiêm kích của Raven** `morrigan` | nhanh hơn mọi tiêm kích của ta và tàng hình: chỉ bị phát hiện ở cự ly gần, hoặc trong chốc lát sau khi khai hỏa. Tên lửa không đối không từ hai khoang săn máy bay của bạn; bom dẫn đường săn xe phòng… | Dựa trên:. Kích thước hiện 12.9 × 8.4 × 2.2 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss chủ lực cùng dòng; bộ phận phá được (tháp, xích, động cơ) phải tách thành khối riêng dễ nhìn; c… | — |
| **Spectre · Máy bay pháo** `sky_fortress` | bay vòng quanh mục tiêu, pháo 105 mm, hai 40 mm và một 25 mm bắn từ bên trái (50–58 m), kèm Griffin; không bắn được máy bay. hủy diệt quân mặt đất nằm dưới vòng bay; chỉ phòng không và tiêm kích với… | Dựa trên: AC-130 Spectre — Pháo hạm bay AC-130 phóng to 1,3 lần, sơn tối. Kích thước hiện 15.5 × 21.2 × 6.1 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss chủ lực cùng dòng; bộ phận phá… | — |
| **Icarus Mk.0 · Phi thuyền nguyên mẫu** `icarus_mk0` | không lên quỹ đạo: đổi tầng cao và thấp theo lịch cố định. Một tháp la-de, một khoang đổ bộ và một la-de phòng thủ điểm bắn hạ tên lửa. ở tầng cao chỉ phòng không tầm xa và tiêm kích bắn tới; ở tầng… | Dựa trên: Polyus / Skif-DM, ISS, Hubble · SOLG (Ace Combat 5), The Expanse — Bản đầu của Icarus (trạm vũ khí quỹ đạo, nhỏ hơn). Kích thước hiện 36.0 × 18.1 × 13.0 m; boss chủ lực ×1,3–1,5 so với mẫu,… | — |
| **Argus · Khí cầu trinh sát** `argus` | khi nó còn, pháo binh địch tản mát chỉ khoảng một nửa. Cao xạ và radar. chậm và to; chỉ phòng không và tiêm kích bắn tới. | Dựa trên: JLENS (khí cầu radar neo) · Kirov Airship (Red Alert 2) — ước đoán: biến thể của khí cầu chỉ huy, khí cầu radar neo. Kích thước hiện 35.0 × 24.2 × 12.4 m; boss chủ lực ×1,3–1,5 so với mẫu,… | — |
| **Leviathan · Thiết giáp hạm** `leviathan` | ba tháp pháo ba nòng 406 mm bắn loạt vào bờ, mỗi tháp một nòng, có cảnh báo trước và quét dần dọc bờ, và bắn cả chín nòng theo dải qua căn cứ khi tung siêu vũ khí; hai tháp ba nòng 155 mm tự bắn, tám… | Dựa trên: Iowa-class hiện đại hóa thập niên 1980 (Mk 7 406 mm), Kirov-class (bệ phóng thẳng đứng) — Thiết giáp hạm lớp Iowa hiện đại hóa, thêm bệ phóng thẳng đứng kiểu Kirov. Kích thước hiện 97.6 × 1… | — |
| **Matriarch · Tàu mẹ drone** `drone_mothership` | pháo và bầy drone cảm tử từ ba khoang phóng (70 m) đánh mặt đất, pháo cao xạ chống máy bay; cứ 30 giây phóng ra 3 UAV tấn công. nhấn chìm mặt đất bằng drone; chỉ phòng không và tiêm kích gây sát thươ… | Dựa trên: Airlander 10 (khí cầu mẹ hiện đại), drone FPV · Kirov Airship (Red Alert 2) — ước đoán: khí cầu bọc thép phóng drone. Kích thước hiện 55.0 × 27.3 × 23.1 m; boss chủ lực ×1,3–1,5 so với mẫu,… | — |
| **Moloch · Nhà máy di động** `moloch` | bò chậm theo đường của nhiệm vụ; hai cửa xưởng cứ 20 giây thả 1–2 xe (xe tăng nhẹ và xe bộ binh, từ pha 2 thêm tăng chủ lực), mỗi phút thêm một xe mỗi lượt, tối đa sáu xe còn sống. Bốn tháp pháo 120… | Dựa trên: xưởng cơ động bánh xích · Fatboy (Supreme Commander), MCV / War Factory (Command & Conquer) — ước đoán: nhà máy di động. Kích thước hiện 40.0 × 21.7 × 18.1 m; boss chủ lực ×1,3–1,5 so với m… | — |
| **Nemesis · Đoàn tàu tên lửa** `nuke_train` | pháo nặng hai nòng (40 m), toa pháo 152 mm và ba pháo cao xạ; bị bắn thì núp trong khói; phía sau có toa rốc-két và toa SAM tầm xa, xe bọc thép hộ tống chạy dọc đường ray. pháo của nó phá nát mọi thứ… | Dựa trên: RT-23 Molodets (tàu tên lửa BZhRK), MIM-104 Patriot — ước đoán: đoàn tàu bọc thép mang tên lửa đạn đạo. Kích thước hiện 70.0 × 5.8 × 8.4 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ h… | — |
| **Kronos · Máy xúc mỏ** `kronos` | chạy rất chậm theo đường cố định về căn cứ ta; bánh gầu nghiền mọi thứ phía trước (900 mỗi giây trong 6 m), cả tường lẫn tháp (gấp ba). Tới được HQ là thua nhiệm vụ. Hai tháp 30 mm, hai tháp pháo 57… | Dựa trên: Bagger 288 — Máy xúc gầu quay khổng lồ. Kích thước hiện 60.0 × 20.0 × 19.8 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss chủ lực cùng dòng; bộ phận phá được (tháp, xích, động… | — |
| **Monster · Pháo tự hành 800 mm** `monster` | tạm dùng thân Bastion (tháp pháo và khẩu cối, to hơn). Nó bò rất chậm, cứ 80 giây nòng 800 mm nâng lên bắn một quả 4.000 sát thương, nổ lan 20 m. giáp và máu khổng lồ, nhưng chậm hơn mọi boss. | — | — |
| **Typhon · Tàu ngầm tên lửa** `typhon` | lặn (không bắn tới được) và nổi (mục tiêu trên mặt nước) theo lịch từng pha, mỗi lần nổi ở một chỗ khác; bong bóng báo trước chỗ nổi. Khi nổi nó phóng tên lửa hành trình tầm ngắn mỗi 12 giây và tự vệ… | Dựa trên: Project 941 Akula (Typhoon) · The Hunt for Red October (1990) — Tàu ngầm tên lửa. Kích thước hiện 70.0 × 14.5 × 16.7 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss chủ lực cùng… | — |
| **Kraken · Tàu sân bay** `kraken` | tạm dùng thân tàu Leviathan (pháo, ống phóng tên lửa và CIWS). Boong cất cánh phóng tiêm kích và drone, và cứ 75 giây nó gọi một đợt không kích. thân tàu dài và dày nhất mặt nước; boong thang máy mỏn… | — | — |
| **Roc · Khí cầu chỉ huy** `command_airship` | hai tháp pháo phòng không 57 mm, hai tháp 30 mm đôi dưới bụng, drone từ hai nhà chứa và thỉnh thoảng mỗi nhà chứa thả một UAV tấn công. Mỗi bộ phận có máu riêng: thân không nhận sát thương cho tới kh… | Dựa trên: Airlander 10, Lockheed P-791 (khí cầu lai hiện đại) · Kirov Airship (Red Alert 2) — ước đoán: 'Sky Admiral', thiết giáp hạm bay hai túi khí. Kích thước hiện 80.0 × 55.4 × 28.3 m; boss chủ l… | — |
| **Garuda · Cánh bay ném bom khổng lồ** `garuda` | tạm dùng thân khí cầu chỉ huy (tháp súng và drone). Tháp phòng thủ và tên lửa đuổi máy bay; cứ 70 giây nó rải thảm 20 quả bom. mục tiêu rộng, nhiều súng; chỉ phòng không tầng thấp mới trúng tốt. | — | — |
| **Gungnir · Pháo điện từ đường ray** `rail_supergun` | cứ 25 giây một phát điện từ vào cụm xe mặt đất đông nhất của bạn, ở bất cứ đâu trên bản đồ: nó xuyên qua tối đa năm xe trên một đường thẳng (1.000 mỗi xe) rồi nổ ở xe cuối (2.000 trong lõi 12 m, còn… | Dựa trên: US Navy EMRG (pháo điện từ, phóng to), đoàn tàu BZhRK Barguzin, đầu máy diesel hiện đại — Pháo điện từ siêu nặng trên đường ray: toa pháo ray điện từ, các toa tụ điện, đầu máy diesel; mỗi 2… | — |
| **Daedalus · Tàu đổ bộ quỹ đạo** `daedalus` | khoảng 10 giây trên quỹ đạo (không bắn tới được), sau đó đổi tầng cao và thấp theo lịch cố định, không lên lại quỹ đạo. Ba cửa thả khoang thả liên tục khoang chở 1–2 xe (tối đa tám xe còn sống); khoa… | Dựa trên: Acclamator-class (Star Wars: Attack of the Clones) — Tàu đổ bộ tấn công của Aurel. Kích thước hiện 60.0 × 33.0 × 20.7 m; boss chủ lực ×1,3–1,5 so với mẫu, mini boss nhỏ hơn boss chủ lực cùn… | — |
| **Icarus · Phi thuyền quỹ đạo** `silver_bug` | tháp la-de chính và hai pháo coilgun bắn xuống mặt đất ở cả tầng cao lẫn tầng thấp; khoang đổ bộ thả xe xuống; cứ 60 giây có 7 thanh vonfram rơi từ vệ tinh của nó (khi đã rơi xuống đất: 9 thanh mỗi 5… | Dựa trên: Polyus / Skif-DM (trạm vũ khí quỹ đạo Liên Xô, 1987), ISS (giàn chính, cánh pin mặt trời, tấm tản nhiệt), Hubble / KH-11 (ống kính, cửa. Kích thước hiện 90.0 × 45.2 × 32.5 m; boss chủ lực ×… | — |
| **Hyperion · Trạm gương quỹ đạo** `hyperion` | tạm dùng thân Silver Bug (chỉ ở tầng cao). Tháp la-de phòng thủ điểm che chắn, mỗi phút thả hai khoang đổ bộ, cứ 65 giây một tia mặt trời đốt dải 70 × 6 m trong 4 giây. không bao giờ xuống tầng thấp,… | — | — |

Sheet: 02_phuong_tien/Xe — Xe (120 dòng, 193 cột)

| id | loai_thuc_the | ten_en | ten_vi | ten_ngan_vi | lop | nhanh | base_cp | mau_hp | mau_trong_tran_hp |
|---|---|---|---|---|---|---|---|---|---|
| aa_57mm_vehicle | xe | 57 mm AA vehicle | Xe phòng không 57 mm | PK 57 mm | AntiAir | Light | 7 | 759 | 1669.8 |
| aa_gun_vehicle | xe | 40 mm AA gun vehicle | Xe cao xạ 40 mm | Cao xạ 40 mm | AntiAir | Light | 6 | 559 | 1229.8 |
| aa_vehicle | xe | Self-propelled AA gun | Pháo cao xạ tự hành | Cao xạ |  |  | 4 | 350 | 770.0 |
| aerial_tanker | xe | Aerial tanker | Máy bay tiếp dầu | Tiếp dầu |  |  | 9 | 1300 | 2860.0 |
| airborne_light_tank | xe | Airborne light tank | Tăng nhẹ thả dù | Tăng thả dù | Tank | Armor | 6 | 727 | 1599.4 |
| airborne_light_tank_chute | vat_pham |  |  |  | Tank | Armor | 0 | 591 | 1300.2 |
| airborne_vehicle | xe | Airborne fighting vehicle | Xe đổ bộ đường không | Xe đổ bộ | Light | Light | 7 | 595 | 1309.0 |
| airborne_vehicle_chute | vat_pham |  |  |  | Light | Light | 0 | 500 | 1100.0 |
| ammo_carrier | xe | Ammo carrier | Xe tiếp đạn | Tiếp đạn | Support | Light | 4 | 520 | 1144.0 |
| amphib_light_vehicle | xe | Amphibious light vehicle | Xe lội nước tốc độ cao | Xe lội nước |  |  | 7 | 650 | 1430.0 |
| armored_bulldozer | xe | Armoured bulldozer | Xe ủi bọc thép | Xe ủi | Heavy | Armor | 8 | 1514 | 3330.8 |
| armored_car | xe | Armoured car | Xe bọc thép bánh lốp | Bánh lốp | Light | Light | 3 | 300 | 660.0 |
| artillery | xe | SP howitzer | Lựu pháo tự hành | Lựu pháo |  |  | 7 | 359 | 789.8 |
| attack_helicopter | xe | Attack helicopter | Trực thăng tấn công | TT tấn công |  |  | 11 | 1009 | 2219.8 |
| attack_jet | xe | Attack jet | Máy bay cường kích | Cường kích |  |  | 23 | 1127 | 2479.4 |

*15 / 120 dòng đầu: xem sheet 02_phuong_tien/Xe; in 10 / 193 cột; 87 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 02_phuong_tien/Xe_vu_khi — Xe: bệ vũ khí phụ (99 dòng, 11 cột)

| id | xe_id | thu_tu | weapon | aim | model | slot |
|---|---|---|---|---|---|---|
| aa_vehicle/0 | aa_vehicle | 0 | sam | Free | stinger | missile |
| airborne_vehicle/0 | airborne_vehicle | 0 | autocannon_30 | Turret |  | coax |
| armored_bulldozer/0 | armored_bulldozer | 0 | hmg_roof | Free |  | mg |
| armored_car/0 | armored_car | 0 | mg_coax | Turret |  | coax |
| artillery/0 | artillery | 0 | hmg_selfdef_15 | Free |  | mg |
| attack_helicopter/0 | attack_helicopter | 0 | heli_gun | Free |  | gun |
| attack_helicopter/1 | attack_helicopter | 1 | heli_rockets | Hull |  | rocket |
| attack_helicopter/2 | attack_helicopter | 2 | stinger_atas | Free |  | aam |
| attack_helicopter/3 | attack_helicopter | 3 | apkws_rocket | Free |  | rocket2 |
| attack_jet/0 | attack_jet | 0 | s8_pods | Hull |  | rocket |
| attack_jet/1 | attack_jet | 1 | jet_bombs | Hull |  | missile |
| attack_jet/2 | attack_jet | 2 | kh29 | Hull |  | missile |
| attack_jet/3 | attack_jet | 3 | r60 | Free |  | aam |
| bmpt/0 | bmpt | 0 | mg_coax | Turret |  | coax |
| bmpt/1 | bmpt | 1 | ataka | Turret |  | missile |

*15 / 99 dòng đầu: xem sheet 02_phuong_tien/Xe_vu_khi.*

Sheet: 02_phuong_tien/Xe_bo_phan — Xe: bộ phận (6 dòng, 17 cột)

| id | xe_id | thu_tu | armour | at_x_m | at_y_m | at_z_m | hp | id_goc | kind |
|---|---|---|---|---|---|---|---|---|---|
| sea_corvette/ciws | sea_corvette | 1 | 2 | 0 | -6.5 | 7.0 | 0.12 | ciws | ciws |
| sea_corvette/gun | sea_corvette | 0 | 2 | 0 | 9 | 4.2 | 0.14 | gun | gun |
| sea_cruiser/ciws_aft | sea_cruiser | 3 | 2 | -2.2 | -6.1 | 5.9 | 0.1 | ciws_aft | ciws |
| sea_cruiser/ciws_fore | sea_cruiser | 2 | 2 | 2.2 | 4.3 | 6.6 | 0.1 | ciws_fore | ciws |
| sea_cruiser/turret_aft | sea_cruiser | 1 | 3 | 0 | -11.5 | 4.0 | 0.12 | turret_aft | gun |
| sea_cruiser/turret_fore | sea_cruiser | 0 | 3 | 0 | 13.7 | 4.0 | 0.12 | turret_fore | gun |

*in 10 / 17 cột; 5 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 02_phuong_tien/Xe_ten_lua — Xe: tên lửa mang (5 dòng, 8 cột)

| id | xe_id | thu_tu | ammo | reload_s | weapon |
|---|---|---|---|---|---|
| bmpt/0 | bmpt | 0 | 4 | 30 | ataka |
| ifv/0 | ifv | 0 | 2 | 20 | atgm |
| light_tank/0 | light_tank | 0 | 2 | 25 | gun_launched_atgm |
| nlos_atgm_vehicle/0 | nlos_atgm_vehicle | 0 | 2 | 25 | spike_nlos |
| titan_tank/0 | titan_tank | 0 | 4 | 30 | atgm |

Sheet: 02_phuong_tien/Nhanh_xe — Nhánh quân (4 dòng, 4 cột)

| id | lop |
|---|---|
| Air | Helicopter;Plane |
| Armor | Tank;Heavy;TankHunter |
| Artillery | Artillery |
| Light | Light;Scout;AntiAir;Support |

Sheet: 02_phuong_tien/Ky_nang — Kỹ năng nội tại (24 dòng, 14 cột)

| id | dung_boi | amount | cooldown_s | count | duration_s | kind | once | radius_m | threshold |
|---|---|---|---|---|---|---|---|---|---|
| airship_launch_l | command_airship;garuda |  | 30 | 1 |  | Summon |  | 80 |  |
| airship_launch_r | command_airship;garuda |  | 30 | 1 |  | Summon |  | 80 |  |
| apc_smoke | ifv |  | 30 |  | 8 | Smoke |  | 7 |  |
| bomber_flares | glide_bomber;heavy_bomber;sky_gunship;swarm_carrier |  | 11 |  | 3 | Flares |  |  |  |
| boss_bulwark | bastion_mk0;behemoth;behemoth_mk0;behemoth_mk2;behemoth_tem… | 0.5 | 30 |  | 6 | Shield |  |  | 0.35 |
| boss_emp | behemoth_tempest;fenrir;fortress_hive;mobile_fortress |  | 35 |  | 4 | Emp |  | 22 |  |
| boss_flares | drone_mothership;locust;mega_gunship;morrigan;sky_fortress;… |  | 10 |  | 3 | Flares |  |  |  |
| boss_rage | behemoth;behemoth_inferno;behemoth_mk2;cerberus;daedalus;ea… | 1.2 |  |  | 9999 | Overdrive | TRUE |  | 0.5 |
| elite_barrage | elite_artillery;elite_attack_helicopter;elite_fpv_carrier;e… | 2.2 | 28 |  | 6 | Barrage |  |  |  |
| elite_emp | elite_apc |  | 30 |  | 3.5 | Emp |  | 14 |  |
| elite_flares | elite_attack_helicopter;elite_attack_jet |  | 14 |  | 3 | Flares |  |  |  |
| elite_overdrive | elite_aa;elite_heavy_tank;elite_long_sam | 1.5 | 25 |  | 6 | Overdrive |  |  |  |
| elite_repair |  | 0.3 | 30 |  | 8 | Repair |  |  | 0.5 |
| elite_shield | elite_mbt | 0.3 | 20 |  | 5 | Shield |  |  |  |
| elite_smoke | elite_tank_destroyer |  | 30 |  | 8 | Smoke |  | 9 | 0.55 |
| fortress_barrage | bastion_mk0;fenrir;fortress_bastion;mobile_fortress;monster | 2 | 25 |  | 8 | Barrage |  |  | 0.4 |
| heli_flares | attack_helicopter;gunship_heli |  | 20 |  | 1.5 | Flares |  |  |  |
| jet_flares | attack_jet;fighter_jet;interceptor_jet;stealth_fighter |  | 16 |  | 1.5 | Flares |  |  |  |
| leviathan_helos | kraken;leviathan;nyx;scylla |  | 55 | 1 |  | Summon |  |  | 0.7 |
| mothership_launch | drone_mothership;fortress_hive;locust;stymphalos |  | 30 | 3 |  | Summon |  | 70 |  |
| mothership_shield | behemoth_tempest;drone_mothership;locust;stymphalos | 0.5 | 30 |  | 8 | Shield |  |  | 0.5 |
| smoke_generator | smoke_carrier |  | 11 |  | 11 | Smoke |  | 11 |  |
| train_patch | armored_train;bastion_mk0;fortress_bastion;monster | 0.5 |  |  |  | Patch | TRUE |  |  |
| train_smoke | armored_train;behemoth_inferno;nuke_train |  | 25 |  | 8 | Smoke |  | 12 |  |

*in 10 / 14 cột; 2 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 02_phuong_tien/Tinh_nhue_luat — Luật tinh nhuệ (20 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so |
|---|---|---|---|
| blueprintChance | elites | blueprintChance | 0.06 |
| bountyCap | elites | bountyCap | 4 |
| budget.Easy | elites | Easy | 0.05 |
| budget.Hard | elites | Hard | 0.15 |
| budget.Heroic | elites | Heroic | 0.2 |
| budget.Iron | elites | Iron | 0.25 |
| budget.Normal | elites | Normal | 0.1 |
| budget.VeryHard | elites | VeryHard | 0.3 |
| cap.Easy | elites | Easy | 1 |
| cap.Hard | elites | Hard | 3 |
| cap.Heroic | elites | Heroic | 4 |
| cap.Iron | elites | Iron | 5 |
| cap.Normal | elites | Normal | 2 |
| cap.VeryHard | elites | VeryHard | 6 |
| coins | elites | coins | 10 |
| costScale | elites | costScale | 1.6 |
| damageScale | elites | damageScale | 1.25 |
| hpScale | elites | hpScale | 1.6 |
| otherShare | elites | otherShare | 0.5 |
| powerRatio | elites | powerRatio | 2.0 |

Sheet: 02_phuong_tien/May_bay_so_phat — Máy bay: số phát để hạ (26 dòng, 15 cột)

| id | mau_hp | giap | sat_thuong_phat_stinger | sat_thuong_phat_stinger_game | so_phat_stinger | sat_thuong_phat_buk | sat_thuong_phat_buk_game | so_phat_buk | sat_thuong_phat_ten_lua_tiem_kich |
|---|---|---|---|---|---|---|---|---|---|
| aerial_tanker | 2860.0 | 0 | 221.0 | 221.0 | 13.0 | 416.0 | 416.0 | 7.0 | 382.2 |
| airborne_light_tank_chute | 1300.2 | 2 | 187.85 | 187.85 | 7.0 | 416.0 | 416.0 | 4.0 | 382.2 |
| airborne_vehicle_chute | 1100.0 | 1 | 221.0 | 221.0 | 5.0 | 416.0 | 416.0 | 3.0 | 382.2 |
| attack_helicopter | 2219.8 | 1 | 221.0 | 221.0 | 11.0 | 416.0 | 416.0 | 6.0 | 382.2 |
| attack_jet | 2479.4 | 2 | 187.85 | 187.85 | 14.0 | 416.0 | 416.0 | 6.0 | 382.2 |
| drop_pod | 352.0 | 1 | 221.0 | 221.0 | 2.0 | 416.0 | 416.0 | 1.0 | 382.2 |
| fighter_jet | 1480.6 | 0 | 221.0 | 221.0 | 7.0 | 416.0 | 416.0 | 4.0 | 382.2 |
| glide_bomber | 3009.6 | 1 | 221.0 | 221.0 | 14.0 | 416.0 | 416.0 | 8.0 | 382.2 |
| gunship_heli | 3619.0 | 2 | 187.85 | 187.85 | 20.0 | 416.0 | 416.0 | 9.0 | 382.2 |
| heavy_bomber | 4529.8 | 0 | 221.0 | 221.0 | 21.0 | 416.0 | 416.0 | 11.0 | 382.2 |
| heavy_lift_helicopter | 2101.0 | 1 | 221.0 | 221.0 | 10.0 | 416.0 | 416.0 | 6.0 | 382.2 |
| interceptor_jet | 1650.0 | 0 | 221.0 | 221.0 | 8.0 | 416.0 | 416.0 | 4.0 | 382.2 |
| light_attack_heli | 1280.4 | 0 | 221.0 | 221.0 | 6.0 | 416.0 | 416.0 | 4.0 | 382.2 |
| prop_attack_plane | 1049.4 | 1 | 221.0 | 221.0 | 5.0 | 416.0 | 416.0 | 3.0 | 382.2 |
| recon_drone | 840.4 | 0 | 221.0 | 221.0 | 4.0 | 416.0 | 416.0 | 3.0 | 382.2 |
| recon_jet | 919.6 | 0 | 221.0 | 221.0 | 5.0 | 416.0 | 416.0 | 3.0 | 382.2 |
| scout_heli | 1139.6 | 0 | 221.0 | 221.0 | 6.0 | 416.0 | 416.0 | 3.0 | 382.2 |
| sky_gunship | 4899.4 | 0 | 221.0 | 221.0 | 23.0 | 416.0 | 416.0 | 12.0 | 382.2 |
| stealth_bomber | 2640.0 | 0 | 221.0 | 221.0 | 12.0 | 416.0 | 416.0 | 7.0 | 382.2 |
| stealth_fighter | 1339.8 | 0 | 221.0 | 221.0 | 7.0 | 416.0 | 416.0 | 4.0 | 382.2 |
| stealth_naval_strike | 2019.6 | 0 | 221.0 | 221.0 | 10.0 | 416.0 | 416.0 | 5.0 | 382.2 |
| strike_drone | 1331.0 | 0 | 221.0 | 221.0 | 7.0 | 416.0 | 416.0 | 4.0 | 382.2 |
| swarm_carrier | 2400.2 | 1 | 221.0 | 221.0 | 11.0 | 416.0 | 416.0 | 6.0 | 382.2 |
| twin_rotor_gunship | 4670.6 | 1 | 221.0 | 221.0 | 22.0 | 416.0 | 416.0 | 12.0 | 382.2 |
| uav_loiter_strike | 550.0 | 0 | 221.0 | 221.0 | 3.0 | 416.0 | 416.0 | 2.0 | 382.2 |
| wingman_drone | 789.8 | 0 | 221.0 | 221.0 | 4.0 | 416.0 | 416.0 | 2.0 | 382.2 |

*in 10 / 15 cột; 3 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 02_phuong_tien/Do_ben — Hệ số độ bền (2 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so |
|---|---|---|---|
| bosses | toughness | bosses | 0.85 |
| vehicles | toughness | vehicles | 2.2 |

#### Lời hướng dẫn trong game theo đơn vị (02_phuong_tien/Xe; chuỗi guide.<id> của GuideText.cs)

- **PK 57 mm** (`aa_57mm_vehicle`): Hai phát mỗi giây, tầm 52 m; trúng được cả xe nhẹ.
- **Cao xạ 40 mm** (`aa_gun_vehicle`): Cách đánh: bốn phát ngòi cận đích mỗi giây, vừa chạy vừa bắn, tầm 48 m. · Mạnh / yếu: thắng trực thăng, drone và xe nhẹ; xe tăng gần như miễn nhiễm. · Mẹo: đi cùng tuyến đầu để chống trực thăng.
- **Cao xạ** (`aa_vehicle`): Cách đánh: pháo đôi 35 mm cao xạ (36 m) bắn khi đang chạy, kèm tên lửa tầm ngắn (44 m) chỉ nhắm máy bay. · Mạnh / yếu: xé nát trực thăng, drone và máy bay phản lực; đạn cao xạ gần như vô hại với giáp nên thua xe tăng và xe bọc thép. · Mẹo: kèm một chiếc với mỗi cụm xe tăng: rẻ mà chặn được trực thăng địch.
- **Tiếp dầu** (`aerial_tanker`): Phần cộng thời gian bay cho máy bay phe ta chưa được làm.
- **Tăng thả dù** (`airborne_light_tank`): Pháo 105 mm, giáp mỏng, thả dù ở nơi phe ta nhìn thấy.
- **Xe đổ bộ** (`airborne_vehicle`): Cách đánh: chạm thẻ rồi chạm vùng phe ta nhìn thấy: nó nhảy dù xuống trong 6 giây; phòng không bắn được khi còn dưới dù. · Mạnh / yếu: chiếm cứ điểm trống, đánh pháo binh từ phía sau; thua xe tăng. · Mẹo: chạm thẻ hai lần để đưa nó về bãi thả.
- **Tiếp đạn** (`ammo_carrier`): Cách đánh: chỉ có súng máy nóc; bệ phóng và xe tên lửa hết đạn trong vòng 14 m nạp nhanh gấp ba, trực thăng trong vòng 12 m hồi tên lửa và rốc-két nhanh gấp đôi. · Mạnh / yếu: giữ pháo phản lực và trực thăng bắn liên tục; giáp mỏng và nổ rất mạnh, nên giữ xa chỗ giao tranh. · Mẹo: đỗ sau các bệ phóng; chỉ huy tự đưa bệ phóng hết đạn tới nó khi đi tới đó nhanh hơn nạp tại chỗ.
- **Xe lội nước** (`amphib_light_vehicle`): Pháo tự động trị xe nhẹ, dùng ở map ven biển.
- **Xe ủi** (`armored_bulldozer`): Cách đánh: chỉ có súng máy trên nóc; lưỡi ủi húc tháp, lô cốt và nhà cửa với sát thương gấp ba (4 m), ủi phẳng răng rồng khi lao qua, và chỉ nhận một nửa sức nổ của mìn. · Mạnh / yếu: phá công sự ở cự ly gần tốt nhất; gần như không làm gì được xe tăng, và xe diệt tăng, tên lửa chống tăng cùng mọi thứ bắn xa hơn diệt nó trên đường lao vào. · Mẹo: cho đi trước xe tăng khi tấn công vào căn cứ; nó không gỡ mìn (việc của công binh) và không thay được tăng rùa để che chắn cho đội hình.
- **Bánh lốp** (`armored_car`): Cách đánh: pháo 25 mm vừa chạy vừa bắn cả đất lẫn trời, mạnh nhất với xe nhẹ và trực thăng; chiếm cứ điểm nhanh gấp đôi. · Mạnh / yếu: thắng trinh sát, pháo binh, xe phòng không và xe hỗ trợ; đạn nảy khỏi xe tăng và tháp canh nên thua chúng. · Mẹo: vòng qua sườn tuyến địch để săn pháo binh và xe hỗ trợ phía sau.
- **Lựu pháo** (`artillery`): Cách đánh: dừng lại, nã ba quả đạn 155 mm nổ mạnh cầu vồng qua vật cản rồi dời 15–20 m mới bắn tiếp, nên đạn phản pháo rơi vào chỗ trống; không bắn được gần hơn 25 m. · Mạnh / yếu: phá công sự, tăng hạng nặng và xe diệt tăng từ xa, bắn mục tiêu bị đánh dấu (chỉ thị la-de, radar phản pháo, UAV quét) gần như không tản mát; trinh sát, xe bọc thép và máy bay áp sát là nó thua. · Mẹo: đi cùng UAV trinh sát hoặc chỉ thị la-de: mục tiêu bị đánh dấu trúng gần như tuyệt đối.
- **TT tấn công** (`attack_helicopter`): Cách đánh: tên lửa chống tăng Hellfire Longbow bắn cặp từ 55 m; nó treo ở rìa tầm đó, vòng sang phía tránh phòng không tầm ngắn; pháo 30 mm và rốc-két khi gần, 2 Stinger bắn máy bay; có mồi nhiệt. · Mạnh / yếu: hạ xe tăng, tăng nặng và pháo binh từ ngoài tầm pháo cao xạ và tên lửa tầm ngắn; xe tên lửa phòng không tầm xa, trạm PK tầm xa và tiêm kích bắn xa hơn nó. · Mẹo: nó tự giữ khoảng cách: đi kèm thứ xử lý được tên lửa tầm xa (đòn SEAD, pháo binh).
- **Cường kích** (`attack_jet`): Cách đánh: bổ nhào càn quét bằng pháo 30 mm, giàn rốc-két 80 mm và bom 250 kg, kèm hai tên lửa chống tăng Kh-29 từ 40 m; hai R-60 chỉ để tự vệ trước máy bay; có mồi nhiệt. · Mạnh / yếu: đập nát xe nhẹ, xe tăng, tăng nặng, pháo binh và công sự, chịu đòn tốt hơn máy bay khác; xe phòng không, tên lửa phòng không và tiêm kích địch vẫn hạ được. · Mẹo: tung vào mũi thiết giáp địch khi phòng không của chúng đã thưa; muốn giành bầu trời hãy mua tiêm kích.
- **Pháo tự nạp** (`auto_loader_howitzer`): Loạt đạn rơi cùng lúc, rồi nạp lâu.
- **TL chiến thuật** (`ballistic_launcher`): Cách đánh: dừng lại rồi phóng một cặp tên lửa đạn đạo vào mục tiêu cách 40–180 m, mỗi quả nổ cực lớn; hai cặp rồi nạp lại lâu. · Mạnh / yếu: xóa sổ công sự, trận địa pháo và cụm quân đông; bắn chậm và bó tay khi bị áp sát. · Mẹo: để dành cho cụm địch đông nhất hoặc tháp quan trọng; đồng đội phải thấy mục tiêu trước.
- **Hỗ trợ tăng** (`bmpt`): Cách đánh: pháo đôi 30 mm (bắn cả đất lẫn trời), tên lửa chống tăng Ataka bắn cặp từ 40 m, và súng phóng lựu bắn sang hai bên. · Mạnh / yếu: dọn xe nhẹ, trinh sát, trực thăng và phòng không quanh xe tăng ta, hại được cả xe tăng; thua tăng nặng và xe diệt tăng. · Mẹo: cho chạy cạnh tăng chủ lực: nó hạ những gì xe tăng khó bắn trúng.
- **Xe bắc cầu** (`bridging_vehicle`): Việc bắc cầu qua sông chưa được làm.
- **Công sự** (`bunker_vehicle`): Cách đánh: khi di chuyển có pháo 105 mm và súng máy đồng trục trong cung phía trước; dừng lại khi có địch trong tầm, hoặc canh giữ cứ điểm hay điểm nghẽn, thì triển khai (3 giây, không bắn): giáp trước cấp 4, tầm 44 m, tháp xoay 360°. Khi được lệnh đi, nó thu lại trước (3 giây). · Mạnh / yếu: làm chốt cho cứ điểm hoặc tuyến công thành; phản ứng chậm, pháo binh và máy bay đánh vào nóc mỏng. · Mẹo: đưa tới nơi tuyến cần trụ lại; biểu tượng trên xe cho biết đang triển khai hay đã triển khai.
- **TL chống hạm** (`coastal_ashm_vehicle`): Tên lửa nặng nạp chậm, mạnh nhất ở mục tiêu xa.
- **Xe hóa ụ súng** (`combat_wreck_car`): Đợt này nổ mạnh hơn khi bị hạ.
- **Chỉ huy** (`command_vehicle`): Cách đánh: chỉ có súng máy trên nóc; quân ta trong 25 m bắn nhanh hơn 10%; đứng yên 5 giây là thành bãi thả dù tiền tuyến, quân mới đáp xuống cạnh nó. · Mạnh / yếu: làm mọi cụm quân quanh nó mạnh hơn và đưa quân tiếp viện ra tận tiền tuyến; thứ gì với tới cũng hạ nó nhanh. · Mẹo: đỗ ngay sau đội xe tăng ở cứ điểm, ngoài tầm bắn thẳng của địch.
- **Radar phản pháo** (`counter_battery_radar`): Cách đánh: chỉ có súng máy trên nóc; pháo địch nào khai hỏa trong vòng 120 m quanh nó bị lộ vị trí với phe ta trong 8 giây, và pháo binh ta gây +15% sát thương lên nó. · Mạnh / yếu: biến pháo địch thành mục tiêu cho pháo, Lancet và máy bay của ta; vô dụng khi địch không có pháo binh. · Mẹo: mang theo cùng pháo binh hoặc Lancet khi địch dựa vào pháo và rốc-két.
- **Xe chói lóa** (`dazzler_vehicle`): Làm nhiễu loạn hỏa lực địch gần đó, tạm thời.
- **Phá mìn** (`demolition_line_vehicle`): Mìn phía trước nổ vô hại; mở đường tấn công.
- **Chiếm drone** (`drone_hijack_vehicle`): Hạ drone địch trong hình nón; chưa lật được phe.
- **Phòng không TN** (`elite_aa`): Cách đánh: pháo đôi 35 mm nổ trên không lan rộng, tầm 46 m, kèm tên lửa; tăng tốc bắn dồn khi có mục tiêu trong tầm. · Mạnh / yếu: xé nát trực thăng, máy bay phản lực và drone; đạn cao xạ gần như vô hại với giáp nên thua xe tăng, xe bọc thép. · Mẹo: giữ máy bay ta tránh xa cho tới khi xe tăng hoặc pháo binh hạ được nó.
- **Bọc thép TN** (`elite_apc`): Cách đánh: pháo tự động và tên lửa chống tăng của xe chiến đấu bộ binh, đánh đau hơn một phần tư; địch vào trong 14 m là dính EMP, bị choáng 3,5 giây. · Mạnh / yếu: thắng xe nhẹ, trinh sát và phòng không, tên lửa còn hại được xe tăng; thua cụm xe tăng đông và xe diệt tăng. · Mẹo: đánh từ ngoài 14 m (xe diệt tăng, pháo binh, máy bay) để EMP không chạm tới quân ta.
- **Lựu pháo TN** (`elite_artillery`): Cách đánh: đạn 155 mm như lựu pháo tự hành, tầm 25–90 m, đánh đau hơn 15%, máu nhiều hơn 60%; có mục tiêu là bắn dồn dập, cứ ba phát lại chạy 15–20 m. · Mạnh / yếu: phá cụm xe nhẹ và tháp canh; phản pháo trượt khi nó đã đổi chỗ, thứ gì áp sát được là thắng. · Mẹo: đừng đứng yên trong tầm của nó; tung xe nhanh hoặc máy bay tới chỗ nó vừa chạy tới, không phải chỗ nó vừa bắn.
- **Trực thăng TN** (`elite_attack_helicopter`): Cách đánh: phóng tên lửa Hellfire từng cặp vào thiết giáp, kèm pháo, rốc-két và Stinger; mồi nhiệt lâu hơn, bắn dồn dập khi có mục tiêu. · Mạnh / yếu: săn xe tăng, tăng nặng và pháo binh; thua xe phòng không, tên lửa phòng không và tiêm kích. · Mẹo: mồi nhiệt chỉ lừa được tên lửa: pháo cao xạ (xe phòng không, Tunguska) chắc ăn hơn cả.
- **Cường kích TN** (`elite_attack_jet`): Cách đánh: pháo, rốc-két và bom như máy bay cường kích, máu nhiều hơn 60%; mồi nhiệt 14 giây lại có và kéo dài gấp đôi. · Mạnh / yếu: xé nát đoàn xe mặt đất và tháp canh; pháo cao xạ không bị mồi nhiệt lừa, tiêm kích đuổi kịp nó. · Mẹo: tên lửa khó hạ nó: đáp trả bằng cao xạ (xe phòng không, Tunguska) hoặc tiêm kích.
- **Drone FPV TN** (`elite_fpv_carrier`): Cách đánh: drone cảm tử như xe phóng FPV, tầm 12–75 m, đánh đau hơn một phần mười, máu nhiều hơn 60%; có thiết giáp trong tầm là phóng dồn dập (nhanh gấp 2,2 lần trong 6 giây). · Mạnh / yếu: phá nát xe tăng và tăng nặng từ xa; tăng APS, xe la-de phòng không và xe gây nhiễu chặn drone, xe nhanh áp sát là hạ được. · Mẹo: thấy vòng vàng thì dàn xe tăng ra, tung xe bọc thép hoặc trực thăng lao thẳng vào nó.
- **Grad TN** (`elite_grad`): Cách đánh: dừng lại rồi phóng dồn 16 rốc-két chùm cách 18–78 m, mỗi quả tung bốn bom con; bắn dồn dập khi có mục tiêu. · Mạnh / yếu: phủ kín cụm xe nhẹ, tháp canh và pháo binh; yếu với xe tăng và bó tay khi bị áp sát. · Mẹo: đừng bao giờ đứng dồn cục trong tầm của nó; tung xe nhanh hoặc máy bay đánh thẳng vào.
- **Tăng nặng TN** (`elite_heavy_tank`): Cách đánh: pháo 152 mm sức nổ lớn, đánh đau hơn một phần tư, máu nhiều hơn 60%; có mục tiêu trong tầm là tăng tốc (chạy nhanh, bắn dồn trong 6 giây). · Mạnh / yếu: nghiền nát tăng chủ lực, xe nhẹ và tháp canh; muốn hạ phải dùng xe diệt tăng, pháo binh và máy bay. · Mẹo: đón đợt tăng tốc của nó từ ngoài tầm (xe diệt tăng bắn 40 m, pháo binh), rồi áp sát khi nó đã dùng xong.
- **SAM tầm xa TN** (`elite_long_sam`): Cách đánh: tên lửa lớn như bản thường, chỉ bắn máy bay, đánh đau hơn một phần năm, máu nhiều hơn 60%; có máy bay trong tầm là tăng tốc (nạp nhanh hơn trong 6 giây). · Mạnh / yếu: khóa kín bầu trời với trực thăng, máy bay và oanh tạc cơ; bất lực trước mặt đất và trong vòng 20 m. · Mẹo: giữ máy bay ta ở nhà, hạ nó bằng xe tăng, pháo binh hoặc một đòn đánh nhanh trên mặt đất.
- **Tăng tinh nhuệ** (`elite_mbt`): Cách đánh: pháo 125 mm đánh đau hơn tăng chủ lực một phần tư, máu nhiều hơn 60%; khi bị bắn thì bật khiên (giảm 30% sát thương trong 5 giây). · Mạnh / yếu: thắng tăng chủ lực và xe nhẹ khi đấu tay đôi; xe diệt tăng và trực thăng hạ được nó. · Mẹo: khiên chỉ kéo dài 5 giây và 20 giây mới có lại: chờ khiên tắt rồi dồn hỏa lực xe diệt tăng.
- **Phản lực TN** (`elite_mlrs`): Cách đánh: dừng lại rồi phóng 16 rốc-két chùm cách 20–75 m, mỗi quả tung năm bom con; bắn dồn dập khi có mục tiêu trong tầm. · Mạnh / yếu: rải thảm cụm xe nhẹ, tháp canh và pháo binh; không tự vệ được trước bất cứ thứ gì áp sát. · Mẹo: dàn quân ra, rồi tung trinh sát, xe bọc thép hoặc máy bay đánh thẳng vào nó.
- **Chống tăng TN** (`elite_tank_destroyer`): Cách đánh: pháo 125 mm bắn từ 46 m; có mục tiêu trong tầm là bắn dồn dập (nhanh gấp 2,2 lần), bị thương thì thả khói. · Mạnh / yếu: cực nguy hiểm với xe tăng và tăng nặng; thua pháo binh, máy bay và xe nhẹ nhanh áp sát. · Mẹo: đừng cho xe tăng lao thẳng vào nó; dùng pháo binh, trực thăng hoặc xe bọc thép đánh áp sát.
- **Công binh** (`engineer_vehicle`): Cách đánh: chỉ có súng máy nóc; sửa chữa xe ta trong vòng 14 m (2,5% máu mỗi giây) và tháp ta chậm bằng nửa, gỡ mìn nó thấy, phá vật cản nhưng chậm (xe ủi phá nhanh hơn). · Mạnh / yếu: giúp tuyến xe tăng và căn cứ đang giữ trụ lâu hơn hẳn; tự đánh thì yếu, trinh sát và xe bọc thép dễ bắt nạt nó. · Mẹo: đỗ ngay sau tuyến đầu hoặc giữa các tháp đang giữ; nạp đạn cho bệ phóng là việc của xe tiếp đạn.
- **Gây nhiễu** (`ew_jammer`): Cách đánh: chỉ có súng máy nóc; tên lửa, drone và hỏa lực yểm trợ của địch nhắm vào vùng gây nhiễu 32 m đều bị lệch. · Mạnh / yếu: khắc chế xe tên lửa chống tăng, xe drone, trực thăng và đòn yểm trợ địch; vô dụng trước súng và đạn pháo thường. · Mẹo: giữ ở giữa đội hình khi địch dùng nhiều tên lửa và drone.
- **FPV cáp quang** (`fibre_fpv_carrier`): Cách đánh: điều khiển từng chiếc drone cáp quang lao vào xe bọc thép, tầm 60 m, 6 giây một chiếc; gây nhiễu vô tác dụng. · Mạnh / yếu: thắng xe tăng núp sau xe gây nhiễu; hệ đánh chặn vẫn hạ được drone. · Mẹo: mang theo khi địch dùng nhiều gây nhiễu.
- **Tiêm kích** (`fighter_jet`): Cách đánh: tên lửa không đối không từ 60 m, tên lửa cận chiến và pháo; đánh chặn máy bay địch ở xa vị trí gác, có thể lơ lửng để bắn. · Mạnh / yếu: khắc tinh của trực thăng, oanh tạc cơ và mọi máy bay; gần như vô hại với mặt đất, vẫn sợ tên lửa phòng không. · Mẹo: mua ngay khi địch đưa bất cứ thứ gì lên trời; nó dọn sạch bầu trời cho máy bay của ta.
- **Phun lửa** (`flame_tank`): Cách đánh: súng phun lửa phải áp sát mới bắn; luồng lửa lan ra cả nhóm, cực mạnh với xe nhẹ và lô cốt. · Mạnh / yếu: thiêu rụi xe nhẹ, trinh sát và tháp canh khi áp sát; xe tăng và mọi thứ bắn xa hơn hạ nó trước khi tới nơi. · Mẹo: cho đi qua phố xá hoặc màn khói để áp sát địch trước khi bị bắn nát.
- **Drone FPV** (`fpv_carrier`): Cách đánh: dừng lại rồi phóng lần lượt từng chiếc drone cảm tử, vài giây một chiếc, lao xuống xe bọc thép cách 12–75 m; hết mười sáu chiếc thì nạp lại một lúc. · Mạnh / yếu: phá nát xe tăng và tăng nặng từ xa; tăng APS, xe la-de phòng không và xe gây nhiễu chặn drone, tăng mái che gần như miễn nhiễm. · Mẹo: bắn từ sau tuyến ta vào xe tăng nặng nhất của địch, giữ ngoài tầm pháo của chúng.
- **Ném bom lượn** (`glide_bomber`): Cách đánh: thả bom lượn từ cách 90 m rồi quay đi; bom lượn 20 m/s xuống mục tiêu. · Mạnh / yếu: đánh tháp và cụm quân ngoài tầm phòng không gần; hệ đánh chặn bắn hạ được bom. · Mẹo: tung vào công sự cố định, có tiêm kích che.
- **Nhiễu định vị** (`gps_jammer_vehicle`): Làm nhiễu loạn hỏa lực địch gần đó, tạm thời.
- **Tên lửa HT** (`ground_cruise_missile_vehicle`): Hai tên lửa chậm; địch có thời gian bắn hạ.
- **Xe robot** (`ground_drone_carrier`): Ba robot con chưa được làm.
- **TT vũ trang** (`gunship_heli`): Cách đánh: mở màn bằng loạt rốc-két lớn, rồi pháo 30 mm cố định và tên lửa chống tăng; xạ thủ bắn từ hai cửa hông. Có mồi nhiệt. · Mạnh / yếu: phá nát xe nhẹ, trinh sát và tháp canh; sợ xe phòng không và tiêm kích, nhưng rất lì đòn. · Mẹo: trực thăng duy nhất chiếm được cứ điểm: đưa nó đi chiếm điểm trống ở xa bên kia bản đồ.
- **PK hỗn hợp** (`heavy_aa`): Cách đánh: bốn nòng 30 mm cao xạ (42 m) và tên lửa phòng không (44 m), bắn cả khi đang chạy; tầm nhìn 60 m thấy máy bay từ sớm. · Mạnh / yếu: lá chắn di động tốt nhất trước trực thăng và máy bay; trên mặt đất thua xe tăng và xe bọc thép. · Mẹo: cho đi cùng đội hình chính để trực thăng và cường kích địch không được tự do tấn công.
- **Oanh tạc cơ** (`heavy_bomber`): Cách đánh: bay qua và thả một hàng 12 quả bom nặng; phóng tên lửa hành trình từ 110 m; súng đuôi bắn máy bay. · Mạnh / yếu: san phẳng công sự, pháo binh và cụm xe nhẹ; sợ tên lửa phòng không và tiêm kích. · Mẹo: tung vào công sự và trận địa pháo địch sau khi tiêm kích hoặc phòng không ta đã dọn sạch bầu trời.
- **TT cẩu tháp** (`heavy_lift_helicopter`): Việc cẩu tháp đặt tùy nơi chưa được làm.
- **Phản lực nặng** (`heavy_rocket_artillery`): Cách đánh: dừng lại rồi phóng 12 rốc-két 300 mm vào vùng cách 30–140 m, sức nổ lớn; ba loạt rồi nạp lại lâu tại chỗ. · Mạnh / yếu: đánh công sự, pháo binh và cụm thiết giáp từ bên kia bản đồ; không có khả năng tự vệ khi bị áp sát. · Mẹo: bắn xa hơn gần như mọi thứ: giữ ở góc căn cứ và cho trinh sát soi mục tiêu.
- **Tăng nặng** (`heavy_tank`): Cách đánh: pháo 152 mm tự đổi đạn xuyên khi bắn xe có giáp và đạn nổ mạnh khi bắn công trình hoặc cụm xe nhẹ; pháo 30 mm bên cạnh đáp trả trực thăng. Giáp trước cấp 4, hông cấp 3. · Mạnh / yếu: trụ lâu nhất khi đối đầu và phá công sự mạnh nhất; chậm, nên sợ xe diệt tăng, pháo binh và máy bay. · Mẹo: làm mũi nhọn đánh công sự và giữ tuyến; cho phòng không đi kèm và đừng để đi một mình.
- **Xuồng hộ tống** (`hover_gunboat`): Cách đánh: pháo 30 mm sáu nòng trên thân đệm khí nhỏ; nó chạy cạnh tàu đệm khí đổ bộ trên cả đất liền lẫn mặt nước. · Mạnh / yếu: nhanh, khó bắt, nhưng giáp mỏng: xe tăng hay pháo tự động nào cũng hạ được. · Mẹo: hạ chiếc đang đánh dấu mục tiêu trước (dấu hộ tống trên nó): khi nó còn, pháo của tàu đệm khí bắn chụm hơn.
- **Xe bộ binh** (`ifv`): Cách đánh: pháo tự động vừa chạy vừa bắn xe nhẹ và máy bay, kèm tên lửa chống tăng TOW (34 m) cho xe tăng; chiếm cứ điểm nhanh gấp 3, bị bắn thì tự thả khói. · Mạnh / yếu: thắng trinh sát, xe nhẹ, pháo binh và phòng không, gây sát thương cả xe tăng; đấu tay đôi với tăng vẫn thua. · Mẹo: tuyến hai lý tưởng sau xe tăng: lấp chỗ hở và chiếm điểm trong lúc xe tăng giao chiến.
- **Drone chặn** (`interceptor_drone_vehicle`): Cách đánh: 4 giây một drone đánh chặn, tầm 60 m, vào drone và trực thăng, cả drone địch đang bay tới. · Mạnh / yếu: làm mỏng bầy FPV và trực thăng; máy bay phản lực bay qua vô sự. · Mẹo: giữ cạnh xe tăng và pháo binh ta.
- **TK đánh chặn** (`interceptor_jet`): Cách đánh: lao vào, bắn hai tên lửa tầm siêu xa từ 90 m, ưu tiên máy bay lớn; không bắn trong 15 m. · Mạnh / yếu: diệt oanh tạc cơ và pháo hạm bay từ sớm; thua khi quần thảo gần. · Mẹo: giữ lại chờ oanh tạc cơ của địch.
- **La-de PK** (`iron_beam`): Cách đánh: tia la-de đốt hạ một drone, tên lửa hoặc rốc-két (cả rốc-két pháo binh) nhắm vào trong vòng 30 m quanh nó, cứ 1,2 giây một quả; giữa các lần đó nó bắn máy bay (45 m). · Mạnh / yếu: che cả cụm quân khỏi tên lửa chống tăng, Lancet, pháo phản lực và tên lửa trực thăng; đạn pháo và đạn súng bay qua được, và nó không có gì đánh mặt đất. · Mẹo: đỗ giữa đội xe tăng khi địch dựa vào tên lửa, drone hoặc rốc-két.
- **Đạn lảng vảng** (`lancet_truck`): Cách đánh: dừng lại rồi phóng từng chiếc drone Lancet bay tới 85 m rồi lao xuống mục tiêu: gấp đôi sát thương lên pháo binh và mọi xe đứng yên quá 3 giây; sáu chiếc rồi nạp lại. · Mạnh / yếu: chuyên diệt pháo binh, giàn phóng và tên lửa phòng không phía sau tuyến, cả xe tăng đứng yên; tăng APS, xe la-de phòng không và xe gây nhiễu chặn được drone. · Mẹo: cho trinh sát, UAV quét hoặc radar phản pháo tìm pháo địch trước, rồi thả Lancet săn chúng.
- **Tàu đổ bộ** (`landing_craft`): Cách đánh: từ khoang đổ bộ của Leviathan tới bãi cát, thả hai xe tăng rồi quay về lấy thêm; tối đa ba chuyến. · Mạnh / yếu: chậm và ít vũ khí; đánh chìm nó trên đường vào thì xe tăng chìm theo.
- **La-de diệt tăng** (`laser_tank`): Cách đánh: tia năng lượng (40 m) tăng từ ×0,3 lên ×2 trong 6 giây trên cùng một mục tiêu, đổi mục tiêu thì về lại mức thấp; xuyên cả giáp dày nhất. · Mạnh / yếu: nung chảy xe tăng nặng và boss; APS, giáp phản ứng nổ và lồng chắn không cản được, nhưng màn khói cắt 80% tia và bầy xe nhỏ giữ nó ở mức yếu nhất. · Mẹo: giữ nó trên một mục tiêu lớn, và che nó khỏi xe hạng nhẹ.
- **TT nhẹ** (`light_attack_heli`): Vài tên lửa chống tăng và súng máy; đánh sườn rồi rút.
- **Tăng nhẹ** (`light_tank`): Cách đánh: pháo 57 mm xuyên giáp vừa chạy vừa bắn, tầm ngắn nhất trong các xe tăng; súng đồng trục bắn máy bay khi mặt đất đã sạch. · Mạnh / yếu: thắng xe nhẹ, trinh sát và xe phòng không; thua tăng nặng hơn, xe diệt tăng và trực thăng tấn công. · Mẹo: lựa chọn rẻ để chặn xe bọc thép địch đầu trận; có CP thì thay bằng tăng chủ lực.
- **PK tầm xa** (`long_sam`): Cách đánh: dừng lại rồi phóng một tên lửa lớn mỗi 8 giây, chỉ bắn máy bay, xa tới 95 m (600 sát thương, không bắn gần hơn 20 m). · Mạnh / yếu: bắn xa hơn vũ khí của mọi máy bay, cả oanh tạc cơ và pháo hạm bay; bất lực trước mặt đất và trong vòng 20 m nên cần được che chắn. · Mẹo: để xa sau tuyến quân, có phòng không tầm ngắn ở gần cho thứ gì lọt xuống thấp.
- **Tăng chủ lực** (`main_battle_tank`): Cách đánh: pháo 120 mm xuyên giáp vừa chạy vừa bắn ở tầm trung, súng máy trên nóc, súng đồng trục bắn máy bay khi mặt đất đã sạch. · Mạnh / yếu: thắng xe nhẹ, trinh sát và phòng không; thua tăng hạng nặng, xe diệt tăng và trực thăng. · Mẹo: dẫn đầu mỗi đợt tiến công bằng 2–3 chiếc, xe diệt tăng theo sau và phòng không ở gần.
- **Vi sóng** (`microwave_vehicle`): Cách đánh: mỗi 8 giây một xung vi sóng làm rơi mọi drone địch trong hình nón 60°, tầm 30 m; xe không hề hấn. · Mạnh / yếu: quét sạch bầy FPV và máy bay drone; vô dụng với mọi thứ khác. · Mẹo: đỗ cạnh xe tăng ta, nơi drone lao xuống.
- **Rải mìn** (`mine_layer`): Cách đánh: có súng máy nóc; khi chạy, cứ 6 giây thả một quả mìn chống tăng (tối đa 8), xe địch cán phải là nổ tung. · Mạnh / yếu: trừng phạt xe tăng và đoàn xe đi theo một lối; tăng mái che có trục lăn phá mìn, máy bay thì không sợ. · Mẹo: chạy qua lại trên con đường địch hay đi, hoặc quanh cứ điểm của ta.
- **PL rải mìn** (`mine_rocket_truck`): Rải mìn phía trước; không gây sát thương trực tiếp.
- **Xuồng tên lửa** (`missile_boat`): Cách đánh: chờ ngoài khơi, lao vào sát đầu cầu tàu, bắn một loạt rốc-két 80 mm rồi quay ra. · Mạnh / yếu: nhanh nhưng giáp mỏng (cấp 1): mọi xe đứng ở đầu cầu tàu đều bắn trúng nó khi nó áp sát.
- **Phản lực** (`mlrs`): Cách đánh: dừng lại rồi phóng một loạt sáu rốc-két chính xác từ tới 110 m; sau bốn loạt phải đứng yên nạp đạn. · Mạnh / yếu: phá công sự, tăng hạng nặng và trận địa pháo từ ngoài tầm với; bất kỳ xe nhanh nào áp sát cũng hạ được nó. · Mẹo: nhắm vào chỗ địch tụ đông hoặc công trình; để xe công binh gần đó giúp nạp đạn nhanh hơn.
- **Xe sửa chữa** (`mobile_repair_vehicle`): Vùng sửa rộng hơn công binh, tốc độ chậm hơn.
- **Xe cối** (`mortar_carrier`): Cách đánh: dừng lại rồi bắn đạn cối 120 mm nổ mạnh qua tường và nhà; tầm nhìn ngắn nên bắn vào mục tiêu đồng đội phát hiện. · Mạnh / yếu: tốt với tháp canh, xe diệt tăng và thiết giáp đứng yên; bó tay khi bị áp sát. · Mẹo: tầm tối thiểu chỉ 10 m, gần hơn các pháo lớn; hãy nấp sau nhà cửa.
- **Tăng thế hệ mới** (`next_gen_tank`): Chặn được hai phát tên lửa hoặc đạn pháo đầu tiên.
- **TL ngoài tầm** (`nlos_atgm_vehicle`): Cách đánh: 10 giây một tên lửa lớn, tầm 90 m, bay vòng qua vật cản đánh nóc, vào mục tiêu phe ta nhìn thấy. · Mạnh / yếu: diệt xe tăng từ sau đồi; tự đi thì mù, bắn chậm. · Mẹo: đi cặp với trinh sát hoặc UAV quét.
- **Cường kích CQ** (`prop_attack_plane`): Súng và rốc-két trị xe nhẹ; mua theo tốp.
- **TL dẫn radar** (`radar_atgm_vehicle`): Cách đánh: hai tên lửa lớn cách nhau 0,6 giây, tầm 50 m, rồi nạp 9 giây; radar nhìn xuyên khói. · Mạnh / yếu: thắng xe tăng nấp trong khói; APS chặn được vài quả. · Mẹo: đem ra đối đầu xe tạo khói.
- **TS radar** (`radar_scout`): Cách đánh: khi chạy nhìn 50 m; đứng yên 2 giây thì dựng cột radar: nhìn 80 m và gần như ẩn. · Mạnh / yếu: chỉ điểm cho pháo binh từ xa, lật tẩy mồi nhử; di chuyển thì yếu. · Mẹo: đỗ ở cánh và để yên đó.
- **Radar PK** (`radar_support_vehicle`): Phần cộng tầm bắn cho PK chưa được làm.
- **Pháo điện từ** (`railgun_truck`): Cách đánh: đứng yên nạp năng lượng 0,9 giây (cuộn dây phát sáng), rồi bắn viên đạn xuyên thủng mọi xe trên đường bay, xa tới 90 m. · Mạnh / yếu: xuyên thủng cả hàng xe tăng và tăng nặng từ rất xa; bắn chậm, bị áp sát là thua. · Mẹo: ngắm dọc con đường hoặc cửa ải nơi địch đi thành hàng; cần đồng đội soi mục tiêu.
- **Súng không giật** (`recoilless_jeep`): Cách đánh: 6,7 giây một phát nổ lõm nặng, tầm 32 m; đỗ yên thì khó thấy cho tới khi bắn. · Mạnh / yếu: phục kích xe tăng từ sườn chỉ với 3 CP; thứ gì bắn trả cũng hạ được nó. · Mẹo: bắn vào sườn một chiếc tăng rồi chạy.
- **UAV trinh sát** (`recon_drone`): Cách đánh: bay cao với tầm nhìn 90 m, soi mục tiêu cho cả đội quân, kèm một tên lửa dẫn đường nhẹ (50 m) đánh mặt đất. · Mạnh / yếu: bắn tỉa trinh sát và pháo binh, giúp pháo ta bắn hết tầm; mong manh, gặp phòng không hay tiêm kích là rơi. · Mẹo: kết hợp với lựu pháo, pháo phản lực hoặc tên lửa đạn đạo để chúng bắn trúng thứ chúng không tự thấy.
- **Trinh sát nhanh** (`recon_jet`): Cách đánh: không vũ khí; bay thẳng một lượt ngang map, làm lộ dải rộng 60 m trong 20 giây, cả tàng hình, rồi rời trận. · Mạnh / yếu: tìm pháo binh, ụ súng ẩn và mồi nhử; bay cao, chỉ tên lửa tầm xa và tiêm kích với tới. · Mẹo: gọi ngay trước một trận pháo kích.
- **Pháo hạm sông** (`river_gunboat`): Chậm; pháo 100 mm bắn phá bờ.
- **Tàu tuần tra** (`river_patrol_boat`): Kiểm soát mặt sông; súng máy và súng phóng lựu.
- **Bán tải rốc-két** (`rocket_technical`): Cách đánh: dừng lại rồi phóng một loạt tám rốc-két khá tản mát tới 48 m; hết sáu loạt phải đứng yên nạp lại. Có thêm súng máy. · Mạnh / yếu: phá tháp canh và cụm địch với giá rẻ; chết trước gần như mọi khẩu súng với tới nó. · Mẹo: xe nhanh, chiếm cứ điểm nhanh gấp đôi: dùng sớm, sau đó giữ thật xa phía sau.
- **PK tầm trung** (`sam_launcher`): Cách đánh: dừng lại rồi phóng tên lửa từng cặp vào máy bay cách tới 55 m; chỉ có súng máy nóc để đánh mặt đất. · Mạnh / yếu: bắn rụng trực thăng, máy bay phản lực và oanh tạc cơ từ xa, kể cả trực thăng tấn công bắn từ xa; xe tăng, xe bọc thép áp sát là nó thua. · Mẹo: đặt sau tuyến đầu: một bệ phóng che được cả một vùng trời rộng.
- **TT trinh sát** (`scout_heli`): Cách đánh: lao vào với súng máy nhiều nòng (tầm gần, bắn được cả máy bay) và giàn 7 rốc-két; mắt tinh giúp soi mục tiêu cho cả quân. · Mạnh / yếu: xé nát trinh sát, xe nhẹ và xe hỗ trợ; xe tăng gần như miễn nhiễm, gặp phòng không là rụng nhanh. · Mẹo: dùng để săn xe hỗ trợ và pháo binh sau lưng địch, tránh xa phòng không.
- **Trinh sát** (`scout_jeep`): Cách đánh: súng máy tầm gần, vừa chạy vừa bắn. Nhìn xa để phát hiện địch cho cả quân, chiếm cứ điểm nhanh gấp đôi. · Mạnh / yếu: diệt được pháo binh và xe hỗ trợ đi lẻ; thua mọi xe bọc thép, xe tăng và tháp canh. · Mẹo: tung hai chiếc đầu trận để chiếm cứ điểm trống, sau đó cho đi trước làm mắt cho pháo binh.
- **Tàu hộ vệ** (`sea_corvette`): Cách đánh: pháo 76 mm bắn vào bờ; CIWS bắn hạ tên lửa và drone nhắm vào nó hoặc vào Leviathan trong vòng 32 m. Nó giữ vị trí chắn giữa Leviathan và bờ. · Mạnh / yếu: hông giáp cấp 3, boong cấp 1; đánh chìm nó trước thì máy bay và tên lửa của bạn đánh được tàu chính.
- **Tuần dương hạm** (`sea_cruiser`): Cách đánh: hai tháp pháo nòng đôi 203 mm bắn vào bờ; hai CIWS bắn hạ tên lửa và drone nhắm vào nó hoặc vào Leviathan trong vòng 30 m. Nó giữ vị trí giữa Leviathan và bờ, áp sát hơn khi tàu chính bỏ chạy. · Mạnh / yếu: hông giáp cấp 3, boong cấp 2; nó là tàu đầu tiên trong tầm bắn, đánh chìm nó thì tên lửa của bạn đánh được tàu chính.
- **Drone cảm tử** (`shahed_truck`): Cách đánh: dừng lại rồi phóng lần lượt từng chiếc drone cảm tử bay chậm xa tới 150 m, vài giây một chiếc, chuyên đánh công trình. · Mạnh / yếu: phá tháp canh, ụ pháo và pháo binh đứng yên ở xa; APS và xe la-de phòng không bắn hạ drone chậm, xe gây nhiễu làm chúng lạc. · Mẹo: ở chế độ Công thành, nhắm vào những tháp mà xe tăng ta chưa với tới.
- **Phát khiên** (`shield_carrier`): Cách đánh: vòm khiên 12 m quanh xe hấp thụ 1.000 sát thương từ đạn pháo, đạn súng, bom và tên lửa cho mọi đơn vị phe ta bên trong, rồi vỡ; hồi lại 20 giây sau đòn cuối. Có súng máy nóc. · Mạnh / yếu: giúp tuyến xe tăng áp sát dưới làn đạn; vũ khí năng lượng xuyên thẳng qua, nhiều vòm không cộng dồn, và bản thân xe giáp mỏng. · Mẹo: giữ ngay sau các xe tăng dẫn đầu; địch đã vào trong vòm thì vòm không chặn được.
- **TL PK nhẹ** (`shorad_vehicle`): Cách đánh: tám tên lửa tầm nhiệt một loạt, tầm 44 m, vừa chạy vừa bắn, rồi nạp 15 giây. · Mạnh / yếu: hạ trực thăng và drone trong một loạt; pháo sáng lừa được vài quả, dưới đất thứ gì cũng diệt được nó. · Mẹo: dành loạt tên lửa cho một cặp trực thăng.
- **Công thành** (`siege_tank`): Cách đánh: hai chế độ. Khi di chuyển là một xe tăng có pháo 105 mm bắn khi đang chạy. Dừng lại khi có địch trong tầm, hoặc khi canh giữ, nó vào thế công thành trong 2,5 giây: hạ chân chống, nâng tháp pháo, cối 240 mm ném đạn 450 sát thương xa từ 16 đến 70 m, nổ rộng 9 m, gấp đôi lên tháp và công trình; 10 quả rồi nạp lại. Thu lại mất 2,5 giây để đi tiếp, hoặc khi địch lọt vào trong 16 m. · Mạnh / yếu: nã công sự, tuyến xe tăng và đội hình dày từ ngoài tầm của chúng; sợ xe nhanh lọt vào trong tầm tối thiểu, máy bay và bị đánh vào sườn khi đang công thành. · Mẹo: cho nó vào thế ngay ngoài tầm địch, có quân chắn phía trước; khi đang hạ hay thu chân chống nó không bắn được.
- **Pháo hạm** (`sky_gunship`): Cách đánh: bay tới nơi bạn chỉ định và bay vòng ngược chiều kim đồng hồ quanh địch ở đó, cách chừng 22 m, pháo 105, 40 và 25 mm cùng bắn một lúc từ bên trái. · Mạnh / yếu: nghiền nát xe nhẹ, xe tăng, pháo binh và tháp; không bắn được máy bay nên sợ tên lửa phòng không và tiêm kích. · Mẹo: đưa vào trận đánh lớn trên mặt đất sau khi phòng không hoặc tiêm kích ta đã xử lý phòng không địch.
- **Xe khói** (`smoke_carrier`): Cách đánh: có súng máy nóc; mỗi khi địch trong tầm, nó phủ màn khói 11 m quanh mình, không ai nhìn xuyên qua được. · Mạnh / yếu: che chở xe tăng và xe chậm khi áp sát pháo tầm xa của địch; tự nó đánh rất yếu. · Mẹo: cho chạy đầu đội hình khi tiến vào xe diệt tăng hoặc xe tên lửa chống tăng để xe tăng ta áp sát được.
- **Cối tháp kín** (`sp_mortar`): Cách đánh: bốn quả cối 120 mm, tầm 60 m, rơi xuống cùng lúc, rồi nghỉ 10 giây. · Mạnh / yếu: nghiền một cụm quân trước khi kịp tản ra; áp sát thì thua xe tăng. · Mẹo: nhắm vào các cụm quân trinh sát tìm thấy.
- **OTC tàng hình** (`stealth_bomber`): Cách đánh: mỗi lượt thả ba quả bom cực lớn, phóng tên lửa JASSM từ 90 m; tàng hình: chỉ bị thấy ở gần hoặc ngay sau khi bắn. · Mạnh / yếu: phá hủy công sự, tăng hạng nặng và pháo binh; một khi lộ diện, tên lửa phòng không và tiêm kích vẫn hạ được. · Mẹo: dùng đánh vào cứ điểm phòng thủ mạnh nhất của địch, nơi máy bay khác sẽ bị bắn rơi.
- **TK tàng hình** (`stealth_fighter`): Cách đánh: tàng hình: địch chỉ thấy ở 40% tầm nhìn, và trong 2,5 giây sau mỗi lần khai hỏa; trạm radar, tháp canh và UAV quét làm lộ nó. Bốn tên lửa AIM-120 đánh máy bay, hai bom GBU-39 thả vào xe và tháp phòng không, pháo 25 mm. · Mạnh / yếu: dọn sạch bầu trời và SAM trước khi máy bay cường kích tới; mang ít đạn hơn tiêm kích thường nên về hồi đạn sớm hơn. · Mẹo: cho bay trước đoàn oanh tạc; radar, tháp canh và UAV quét là thứ tìm ra nó.
- **Tàng hình hạm** (`stealth_naval_strike`): Hai bom dẫn đường trị công trình và xe đứng yên; không pháo.
- **UAV tấn công** (`strike_drone`): Cách đánh: bay cao, phóng tên lửa Hellfire từ 48 m và bốn quả bom dẫn đường; không có vũ khí chống máy bay. · Mạnh / yếu: bắn tỉa xe tăng, tăng nặng và pháo binh; chậm và mỏng, gặp phòng không hay tiêm kích là rơi. · Mẹo: tầm nhìn 62 m biến nó thành trinh sát cho pháo binh; tránh xa tên lửa phòng không địch.
- **Tiếp tế** (`supply_truck`): Cách đánh: chỉ có súng máy nhẹ; nó chạy theo lộ trình tới kho và không chiếm được cứ điểm. · Mạnh / yếu: đủ giáp để chịu vài phát, nhưng không đánh lại được thứ gì đáng kể. · Mẹo: trong nhiệm vụ hộ tống, dùng xe tăng dọn đường phía trước và cho phòng không đi cùng xe tải.
- **Máy bay mẹ** (`swarm_carrier`): Cách đánh: bay qua mục tiêu, thả lần lượt tám drone FPV (nổ lõm, đánh nóc), mỗi chiếc một mục tiêu, và thả thêm hai bom dẫn đường từ cùng khoang khi bay qua; kho đạn hồi lại trong 16 giây. · Mạnh / yếu: đưa bầy drone tới nơi xe drone FPV hay nhà chứa drone không với tới; tiêm kích và SAM bắn hạ được nó, còn C-RAM, xe la-de phòng không, tháp EW và xe gây nhiễu chặn được drone. · Mẹo: tung ra khi phòng không địch đang bận; drone không chiếm chỗ máy bay của ta.
- **Chống tăng** (`tank_destroyer`): Cách đánh: pháo 125 mm xuyên giáp (như pháo tự hành 2S25), vừa chạy vừa bắn, xa hơn và nạp nhanh hơn pháo tăng chủ lực; súng máy nóc cho mục tiêu nhỏ. · Mạnh / yếu: hạ xe tăng, tăng hạng nặng và boss từ ngoài tầm với của chúng; sợ pháo binh và xe nhẹ áp sát. · Mẹo: để ngay sau hàng xe tăng để nó bắn trước; khắc tinh của thiết giáp nặng và boss.
- **Nhiệt áp** (`thermobaric_launcher`): Cách đánh: dừng lại rồi phóng 12 rốc-két nhiệt áp phủ kín một vùng cách 12–38 m; bốn loạt rồi phải đứng yên nạp lại. · Mạnh / yếu: quét sạch cụm địch, tháp canh và mọi thứ đứng dồn; phải tiến khá gần, dễ bị máy bay bắt. · Mẹo: giáp đủ dày để đi sau xe tăng: tiến sát sau lưng chúng rồi nã vào cứ điểm địch đang giữ.
- **Siêu tăng** (`titan_tank`): Cách đánh: pháo đôi 140 mm bắn loạt đôi tới 40 m, kèm tên lửa chống tăng và hai súng máy. · Mạnh / yếu: nghiền nát xe tăng, xe nhẹ và công sự; bị xe diệt tăng, pháo binh và máy bay bào dần. · Mẹo: làm trụ cho đợt tấn công lớn; phải có phòng không đi kèm để che trực thăng.
- **Pháo kéo CT** (`towed_at_gun`): Bắn xa, mạnh, không giáp.
- **Tăng rùa** (`turtle_tank`): Cách đánh: pháo 120 mm không xoay được, phải quay cả thân để ngắm. Mái thép chặn 80% sát thương drone, trục lăn kích nổ mìn vô hại. · Mạnh / yếu: đi xuyên bầy FPV, Lancet và bãi mìn, thắng xe nhẹ; thua tăng hạng nặng và xe diệt tăng. · Mẹo: cho đi đầu khi địch có xe drone và xe rải mìn; nó chậm, để các xe khác theo sau.
- **TT hai rô-to** (`twin_rotor_gunship`): Giữa trực thăng vũ trang và Pháo hạm bay; dễ bị bắn trúng.
- **Hai nòng** (`twin_tank`): Cách đánh: hai pháo 120 mm bắn gần như cùng lúc, một phát đôi ở 34 m, rồi nạp lâu (7 giây); tháp xoay nhanh, chạy nhanh hơn tăng nặng; giáp trước cấp 3. · Mạnh / yếu: phát mở màn thắng tay đôi với tăng chủ lực và tăng nặng; bắn lại chậm, nên xe diệt tăng, trực thăng và bầy xe nhẹ bào mòn được nó. · Mẹo: cho nó mở màn vào chiếc tăng nặng nhất của địch, để các xe khác che lúc nó nạp đạn.
- **Xe bom** (`vbied`): Cách đánh: lao thẳng vào địch rồi tự nổ: 700 sát thương trong bán kính 7,5 m, một nửa lên tháp và công trình. Bị bắn hạ giữa đường thì nổ ngay tại chỗ. · Mạnh / yếu: phá nát pháo binh, xe hỗ trợ và cụm xe nhẹ; súng bắn nhanh và xe bọc thép chặn được nó, và căn cứ chịu được cả dòng xe bom. · Mẹo: cho chạy sau đợt xe tăng hoặc xuyên qua màn khói để tới mục tiêu nguyên vẹn.
- **Pháo xung kích** (`wheeled_gun`): Cách đánh: pháo 120 mm xuyên giáp (như Centauro II) vừa chạy vừa bắn tới 38 m, khoảng 70 sát thương mỗi giây lên giáp dày, +25% khi trúng hông hoặc đuôi. · Mạnh / yếu: chạy vòng tuyến xe tăng và trừng phạt hai bên sườn; giáp mỏng nên đấu thẳng với tăng là thua, pháo tự động xé nát nó. · Mẹo: vòng qua sườn trong lúc xe tăng giữ mặt trước: phát nào trúng hông cũng đáng giá.
- **Pháo bánh lốp** (`wheeled_howitzer`): Cách đánh: bốn phát 155 mm trong 6 giây, tầm 90 m, rồi chạy ngay và nạp lại 25 giây. · Mạnh / yếu: phản pháo rơi vào chỗ trống; thân mỏng, dễ chết. · Mẹo: giữ thật xa phía sau, có trinh sát đi trước.
- **Drone hộ vệ** (`wingman_drone`): Cách đánh: bay kèm cánh máy bay dẫn (máy bay có người lái gần nhất trong 120 m; không có thì tuần tra trên chiến tuyến) với hai tên lửa AIM-9; tên lửa phòng không địch nhắm vào máy bay dẫn có bốn phần mười cơ hội chuyển sang nó. · Mạnh / yếu: giúp tiêm kích và oanh tạc cơ sống thêm vài quả tên lửa; một mình thì yếu, tiêm kích địch bắn hạ dễ. · Mẹo: mua khi đã có máy bay có người lái; không tính vào trần sáu máy bay (tối đa bốn chiếc mỗi phe).
- **Cao xạ bán tải** (`zu23_technical`): Cách đánh: pháo đôi 23 mm cao xạ vừa chạy vừa bắn máy bay và xe nhẹ (32 m); chiếm cứ điểm nhanh gấp đôi. · Mạnh / yếu: xé nát trực thăng, drone và trinh sát; xe tăng và xe bọc thép hạ nó trong vài giây. · Mẹo: đối sách rẻ và sớm trước trực thăng địch; về sau hãy mua xe phòng không thật sự.

*115 / 120 đơn vị có lời hướng dẫn.*

## 9. Bảng DPS tổng hợp

Trạng thái: Đã áp

Nguồn dữ liệu: 02_phuong_tien/Xe_suy_ra; 02_phuong_tien/Hoi_quy; 02_phuong_tien/Hoi_quy_du_lieu. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §9. Bảng DPS, §9b.

#### 9. Bảng DPS tổng hợp

#### 9b. Giá trị thực chiến

DPS lý thuyết (phần 9) đã sửa để tính đủ loạt bắn, băng đạn, thời gian thay băng, nạp của bệ phóng và số bom/tên lửa mỗi lần đầy đạn. Giá trị thực chiến đo trong mô phỏng: mỗi xe hạng 1, không trang bị, đánh các nhóm mục tiêu chuẩn (cụm xe nhẹ, cụm xe tăng, công sự có tháp, máy bay) trong khoảng 90 giây từ lúc tiếp đất, có và không có phòng không đối phương; tính cả thời gian không bắn (di chuyển, xoay tháp, nạp đạn, bay vòng, bị pháo sáng và APS chặn). Giá trị = sát thương thực × hệ số sống sót / CP. Mọi quyết định cân bằng của prompt 13 dựa trên bảng này.

**vs cụm xe** (prompt 25 E3): DPS lên 5 xe nhẹ cách nhau 4 m (một xe ở giữa, bốn xe quanh nó), mọi phát nhắm xe giữa; tính từ dữ liệu, không chạy mô phỏng: phát trúng thẳng như bảng 9 (vs nhẹ), cộng nổ lan lên bốn xe quanh theo bán kính nổ (dao động ±15%), độ suy giảm (25% ở mép, nhiệt áp 62,5%), cấp xuyên của mảnh nổ (tối đa 1 trên mặt đất) vào hông xe và hệ số loại đạn; bom chùm rải bom con lên cả năm. Trong ngoặc: bao nhiêu lần DPS lên một xe. **Hỗ trợ / CP** (E2): giá trị hỗ trợ của xe hỗ trợ, bảng dưới.

Số đo: `combat_value_pt6_after_summary.tsv`; chỉ các thẻ còn trong roster, CP theo dữ liệu hiện tại.

#### Giá trị hỗ trợ (E2)

Xe hỗ trợ không gây sát thương nên giá trị thực chiến bỏ sót chúng. Phép đo riêng (`CombatValueMeasure.MeasureTheSupportVehicles`, và `MeasureTheRoster` ghi vào cùng bảng tổng hợp): một xe đi cùng hai tăng chủ lực, một xe bộ binh, một pháo phản lực và một trực thăng tấn công, do AI chiến thuật dẫn, đánh một nhóm bắn tên lửa dẫn đường và bắn thẳng (hai BMPT, một tăng chủ lực, một trực thăng tấn công; hết đợt này 3 giây có đợt sau) trong 3 phút. Ghi: **máu sửa được**, **đạn nạp thêm** (viên: băng vơi được nạp đầy, phần thời gian nạp tại chỗ được rút ngắn quy ra viên, đạn trực thăng nạp cạnh xe), **tên lửa hút được** (đạn dẫn đường của địch bị gây nhiễu lúc phóng, và phần trăm trên mọi đạn dẫn đường địch bắn), **sát thương khiên chặn**. Giá trị hỗ trợ / CP = (máu sửa + khiên chặn + sát thương của số đạn nạp thêm và của tên lửa bị hút) × hệ số sống sót / CP, cùng thang với giá trị thực chiến. Ô "—": chưa đo (chờ phase kiểm tra).

| Xe | CP | Cơ chế | Máu sửa | Đạn nạp thêm (viên) | Tên lửa hút (quả) | Khiên chặn | Giá trị hỗ trợ / CP |
|---|---|---|---|---|---|---|---|
| **Xe công binh** | 3 | sửa 2,5% máu/s trong 14 m | — | — | — | — | — |
| **Xe tiếp đạn** | 4 | nạp đạn trong 14 m (1 viên mỗi 4 s, nạp tại chỗ nhanh ×3); trực thăng nạp đạn cạnh xe (trong 12 m) | — | — | — | — | — |
| **Xe sửa chữa lưu động** | 4 | sửa 1,5% máu/s trong 20 m | — | — | — | — | — |
| **Xe laser chói lóa** | 6 | gây nhiễu đạn dẫn đường trong 30 m | — | — | — | — | — |
| **Xe gây nhiễu điện tử** | 6 | gây nhiễu đạn dẫn đường trong 32 m | — | — | — | — | — |
| **Xe gây nhiễu định vị** | 6 | gây nhiễu đạn dẫn đường trong 28 m | — | — | — | — | — |
| **Xe phát khiên** | 8 | khiên 1.000 máu, bán kính 12 m, đầy lại sau 20 s | — | — | — | — | — |

Sheet: 02_phuong_tien/Xe_suy_ra — Xe: suy ra (120 dòng, 17 cột)

| id | nap_dan_may_bay | nap_lai_may_bay_s | he_so_vu_khi | dps_vu_khi_chinh | dps_vu_khi_chinh_game | dps_vu_khi_chinh_may_bay | dps_vu_khi_chinh_may_bay_game | mau_tren_cp | dps_tren_cp |
|---|---|---|---|---|---|---|---|---|---|
| aa_57mm_vehicle | 0 | 0.0 | 1.0 | 163.33800000000002 | 163.33800000000002 | 163.33800000000002 | 163.33800000000002 | 238.54285714285714 | 23.334000000000003 |
| aa_gun_vehicle | 0 | 0.0 | 1.0 | 92.90322580645162 | 92.90322580645162 | 92.90322580645162 | 92.90322580645162 | 204.96666666666667 | 15.483870967741936 |
| aa_vehicle | 0 | 0.0 | 1.0 | 88.0 | 88.0 | 88.0 | 88.0 | 192.5 | 22.0 |
| aerial_tanker | 0 | 0.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 317.77777777777777 | 0.0 |
| airborne_light_tank | 0 | 0.0 | 1.0 | 50.879999999999995 | 50.879999999999995 | 50.879999999999995 | 50.879999999999995 | 266.56666666666666 | 8.479999999999999 |
| airborne_light_tank_chute | 0 | 8.5 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 |  |  |
| airborne_vehicle | 0 | 0.0 | 1.0 | 38.89000000000001 | 38.89000000000001 | 38.89000000000001 | 38.89000000000001 | 187.0 | 5.555714285714287 |
| airborne_vehicle_chute | 0 | 8.5 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 |  |  |
| ammo_carrier | 0 | 0.0 | 1.0 | 58.96958410924891 | 58.96958410924891 | 58.96958410924891 | 58.96958410924891 | 286.0 | 14.742396027312228 |
| amphib_light_vehicle | 0 | 0.0 | 1.0 | 60.24878493317134 | 60.24878493317134 | 60.24878493317134 | 60.24878493317134 | 204.28571428571428 | 8.606969276167336 |
| armored_bulldozer | 0 | 0.0 | 1.0 | 78.574375 | 78.574375 | 78.574375 | 78.574375 | 416.35 | 9.821796875 |
| armored_car | 0 | 0.0 | 1.0 | 51.64034021871204 | 51.64034021871204 | 51.64034021871204 | 51.64034021871204 | 220.0 | 17.21344673957068 |
| artillery | 0 | 0.0 | 1.0 | 42.34173339079547 | 42.34173339079547 | 42.34173339079547 | 42.34173339079547 | 112.82857142857142 | 6.0488190558279245 |
| attack_helicopter | 8 | 9.0 | 1.0 | 64.33287804878049 | 64.33287804878049 | 64.33287804878049 | 64.33287804878049 | 201.8 | 5.848443458980044 |
| attack_jet | 0 | 14.0 | 1.0 | 456.5291393284446 | 456.5291393284446 | 456.5291393284446 | 456.5291393284446 | 107.8 | 19.8490930142802 |

*15 / 120 dòng đầu: xem sheet 02_phuong_tien/Xe_suy_ra; in 10 / 17 cột; 5 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 02_phuong_tien/Hoi_quy — Hồi quy theo CP (12 dòng, 5 cột)

| id | gia_tri | y_nghia |
|---|---|---|
| dps_he_so | 34.33713767277216 | hệ số a của DPS theo CP |
| dps_so_mu | 0.33805260449762203 | số mũ b của DPS theo CP |
| mau_he_so | 252.3044581970855 | hệ số a của máu theo CP |
| mau_so_mu | 0.8216877482994875 | số mũ b của máu theo CP |
| n_dps | 73.0 | số xe có DPS > 0 |
| n_mau | 79.0 | số xe trong hồi quy máu |
| trung_vi_dps_tren_cp_9_15 | 5.405517559572274 | trung vị DPS / CP, dải 9-15 |
| trung_vi_dps_tren_cp_ge16 | 4.66849585900156 | trung vị DPS / CP, dải >=16 |
| trung_vi_dps_tren_cp_le8 | 10.024829298572314 | trung vị DPS / CP, dải <=8 |
| trung_vi_mau_tren_cp_9_15 | 148.7 | trung vị máu / CP, dải 9-15 |
| trung_vi_mau_tren_cp_ge16 | 146.66339285714287 | trung vị máu / CP, dải >=16 |
| trung_vi_mau_tren_cp_le8 | 187.0 | trung vị máu / CP, dải <=8 |

Sheet: 02_phuong_tien/Hoi_quy_du_lieu — Hồi quy: dữ liệu (79 dòng, 19 cột)

| id | cp | mau_hp | dps_nhe | dps_nang | dps_may_bay | dps_max | ln_cp | ln_mau | ln_dps |
|---|---|---|---|---|---|---|---|---|---|
| aa_57mm_vehicle | 7 | 1669.8 | 81.66900000000001 | 40.834500000000006 | 212.33940000000004 | 212.33940000000004 | 1.9459101490553132 | 7.4204591377599 | 5.358185937924469 |
| aa_gun_vehicle | 6 | 1229.8 | 46.45161290322581 | 23.225806451612904 | 120.7741935483871 | 120.7741935483871 | 1.791759469228055 | 7.114606833519369 | 4.793922633112336 |
| aa_vehicle | 4 | 770.0 | 44.0 | 22.0 | 114.4 | 114.4 | 1.3862943611198906 | 6.646390514847729 | 4.739701078945697 |
| aerial_tanker | 9 | 2860.0 | 0.0 | 0.0 | 0.0 | 0.0 | 2.1972245773362196 | 7.958576903813898 |  |
| airborne_light_tank | 6 | 1599.4 | 61.05599999999999 | 43.248 | 15.263999999999998 | 61.05599999999999 | 1.791759469228055 | 7.377383837897789 | 4.111791475825822 |
| airborne_vehicle | 7 | 1309.0 | 38.89000000000001 | 19.445000000000004 | 0.0 | 38.89000000000001 | 1.9459101490553132 | 7.1770187659099 | 3.660737148167656 |
| amphib_light_vehicle | 7 | 1430.0 | 60.24878493317134 | 30.12439246658567 | 0.0 | 60.24878493317134 | 1.9459101490553132 | 7.265429723253953 | 4.098482405083113 |
| armored_bulldozer | 8 | 3330.8 | 94.28925 | 66.78821875 | 0.0 | 94.28925 | 2.0794415416798357 | 8.110967794361665 | 4.54636718526205 |
| armored_car | 3 | 660.0 | 51.64034021871204 | 25.82017010935602 | 0.0 | 51.64034021871204 | 1.0986122886681098 | 6.492239835020471 | 3.9443031542354388 |
| artillery | 7 | 789.8 | 42.34173339079547 | 35.99047338217615 | 0.0 | 42.34173339079547 | 1.9459101490553132 | 6.671779748852549 | 3.7457732046607606 |
| attack_helicopter | 11 | 2219.8 | 77.19945365853658 | 64.33287804878049 | 0.0 | 77.19945365853658 | 2.3978952727983707 | 7.70517238071788 | 4.346392380043727 |
| attack_jet | 23 | 2479.4 | 456.5291393284446 | 228.2645696642223 | 0.0 | 456.5291393284446 | 3.1354942159291497 | 7.815771874404047 | 6.12365253004263 |
| auto_loader_howitzer | 9 | 1830.4 | 52.36363636363637 | 26.181818181818183 | 0.0 | 52.36363636363637 | 2.1972245773362196 | 7.512289801185479 | 3.958212387897521 |
| ballistic_launcher | 14 | 1309.0 | 48.1648945755992 | 48.1648945755992 | 0.0 | 48.1648945755992 | 2.6390573296152584 | 7.1770187659099 | 3.874630427389569 |
| bmpt | 11 | 3190.0 | 133.93278924627938 | 66.96639462313969 | 0.0 | 133.93278924627938 | 2.3978952727983707 | 8.06777619577889 | 4.8973381013322435 |

*15 / 79 dòng đầu: xem sheet 02_phuong_tien/Hoi_quy_du_lieu; in 10 / 19 cột; 7 cột khác (và raw_json, nguon): xem sheet.*

## 10. Vũ khí và bảng sát thương

Trạng thái: Đã áp

Nguồn dữ liệu: 01_vu_khi_dan/Bang_sat_thuong; 01_vu_khi_dan/Bang_xuyen_giap; 01_vu_khi_dan/Khac_che; 01_vu_khi_dan/He_so_toan_cuc; 01_vu_khi_dan/Vu_khi; 01_vu_khi_dan/Vu_khi_suy_ra; 01_vu_khi_dan/Vu_khi_he_so_thuong; 01_vu_khi_dan/Dan_thay_the; 01_vu_khi_dan/Phao_sang. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §10. Vũ khí, §10b, §10c, §10e, §10f, §Cân bằng đợt 2.

#### 10. Vũ khí và bảng sát thương

#### Hệ số sát thương theo loại đạn và loại giáp

Prompt 15: mỗi mặt giáp (trước, hông, sau, nóc) có cấp 0–4 (boss tới cấp 5, giáp siêu dày: DECISIONS 21G), mỗi vũ khí có cấp xuyên 0–4. Sát thương nhân theo cấp xuyên so với cấp giáp của mặt trúng đạn: hơn từ 2 cấp ×1.2, hơn 1 cấp ×1, ngang cấp ×0.85, thiếu 1 cấp ×0.5, thiếu 2 cấp ×0.25, thiếu từ 3 cấp ×0.1; đầu nổ nhiệt áp ×2 (xem DECISIONS 14A). Bảng hiệu quả và ký hiệu ✓ ~ ✕ của từng xe nằm ở thẻ xe (phần 8).

Giáp có hướng (giáp mặt trước dày hơn hông/sau), đạn lệch theo tầm và chuyển động, pháo có tầm tối thiểu. Máy bay có pháo sáng, xe có hệ thống đánh chặn chủ động (APS) chặn tên lửa/drone, tàng hình chỉ lộ ở 40% tầm nhìn khi không bắn. Ký hiệu: ✓ hệ số từ 0.6 trở lên, ~ từ 0.12, ✕ thấp hơn (cùng ngưỡng với giao diện trong game).

#### Khắc chế: phòng vệ chặn loại đạn nào

| Phòng vệ | Chặn hoặc giảm | Không chặn |
|---|---|---|
| Giáp phản ứng nổ (mô-đun) | Nổ lõm: giảm 40% (Sử thi) / 55% (Huyền thoại) một phát; đầu nổ song song xuyên qua | Động năng, nổ mạnh, mọi loại khác; mìn |
| Khối phản ứng nổ (dòng đặc biệt) | Nổ lõm: nửa một phát, mỗi lần một khối | Đạn động năng |
| Lồng chắn (Slat Cage, lưới chắn; mái che của xe rùa trước drone) | Phần nổ lõm của rốc-két, tên lửa và drone | Đạn động năng, đạn pháo HEAT, nổ nhiệt áp, mìn |
| APS (Trophy, phòng thủ điểm) | Tên lửa, drone, rốc-két bắn thẳng (laser phòng thủ điểm và C-RAM thêm rốc-két pháo binh; C-RAM một phần đạn pháo) | Đạn pháo xe tăng, đạn súng, tia năng lượng; laser phòng thủ điểm khi ở trong khói hoặc bắn vào khói |
| Pháo sáng | Tên lửa (theo độ kháng pháo sáng của đầu dò) | Drone, đạn súng, đạn phòng không, tia năng lượng |
| Khói | 80% sát thương của tia năng lượng bắn vào hoặc bắn ra | Mọi loại khác |
| Gây nhiễu | Đạn dẫn đường (tên lửa, drone) bay lệch | Đạn không dẫn đường, tia năng lượng |
| Khiên (xe mang khiên, tháp khiên) | Mọi phát trúng quân ở trong vòm, tới khi khiên vỡ | Năng lượng |

Luật này được test `ArmourTests.CountersFollowTheTable` kiểm tra (bảng gốc ở DECISIONS 14A C.9).

#### 10b. Nhịp bắn, nạp đạn, đường đạn và di chuyển

Đọc thẳng từ dữ liệu game. **Viên/s** là nhịp khi đang bắn (trong một loạt, hoặc giữa hai phát). **Xả** là thời gian hết một băng hay một loạt. **Nghỉ/nạp** là thời gian thay băng hay nghỉ giữa hai loạt. **Bệ phóng** là số lượt bắn trước khi phải nạp lại cả bệ. **TB viên/s** tính cả thời gian nghỉ và nạp. **DPS khi xả** là sát thương mỗi giây trong lúc bắn, trước giáp; **DPS duy trì** tính cả thời gian nạp (prompt 13). **Xoay thân / tháp** tính bằng độ mỗi giây, như balance.json (mã giữ radian mỗi giây; bản trước in số radian dưới nhãn °/s, prompt 25 C.4).

#### Kích thước đạn (55 model)

Kích thước model đạn nhân tỷ lệ của vũ khí (projectileScale).

#### 10c. Tầm nổ

Bán kính nổ lan (m) của mọi bom, tên lửa, rốc-két, đạn pháo và drone; của các thẻ hỗ trợ hỏa lực; của đòn lớn của boss; và của vụ nổ khi xe, tháp, boss bị phá. "Trúng trực tiếp" là quả chỉ gây sát thương cho mục tiêu nó trúng. Sát thương là mỗi phát, trước giáp.

#### 10e. DPS theo cấp giáp, tên lửa, kích thước và siêu vũ khí (prompt 25)

#### DPS theo cấp giáp (234 vũ khí)

DPS duy trì (prompt 13: cả loạt, băng, thay băng, nạp bệ) nhân hệ số của vũ khí lên từng cấp giáp 0–5 (5 là giáp boss), lên máy bay và lên công trình (loại sát thương × bước xuyên, bảng hiệu quả ✓ ~ ✕ của thẻ xe; đạn đánh nóc tính vào nóc). Mặt trúng là mặt trước ở cấp đó. Thưởng theo lớp giáp (ví dụ phá công sự) tính luôn; thưởng theo loại xe, đứng yên hay đánh sườn ghi ở thẻ xe.

#### Tên lửa: tốc độ bay và thời gian bay (61)

Tốc độ bay (m/s) và thời gian bay tới tầm xa nhất (tầm / tốc độ; tên lửa dẫn đường bay một thời gian định lúc phóng và trúng nơi mục tiêu đang đứng khi tới). Cột nhanh hơn: tốc độ tên lửa phòng không so với máy bay nhanh nhất trong game (60 m/s; file cân bằng nhắm 1,2–1,5 lần mục tiêu nhanh nhất cần bắt).

#### Kích thước model theo dữ liệu (151 đơn vị)

modelSize (prompt 25 B1): hộp của model kể cả nòng, dài × rộng × cao (m), theo sheet Kiểm tra từng mục (mặt đất 0,8 × thật, trên không 0,4 × thật); game vẽ model khớp chiều dài này. Thân va chạm: dài và rộng.

#### Kích thước đạn theo dữ liệu (54 vũ khí)

roundLength (prompt 25 B3): chiều dài đạn vẽ (m): 0,8 × thật khi phóng từ mặt đất, 0,5 × thật từ máy bay, tối thiểu 0,8 m; đạn 203 mm bằng 1,3 lần 155 mm. Game vẽ model đạn khớp chiều dài này.

| Vũ khí | Tên thật | Model đạn | Dài đạn (m) | Trên |
|---|---|---|---|---|
| `anti_radar_missile` | AGM-88 HARM | harm | 2,09 | TK đánh chặn |
| `apkws_rocket` | APKWS (laser-guided Hydra 70) | apkws | 0,8 | TT tấn công |
| `avenger_stingers` | Starstreak / Stinger SHORAD (Avenger pods) | shorad_dart | 1,22 | TL PK nhẹ |
| `bomber_payload` | FAB-500 (500 kg) | bomb | 1,2 | Oanh tạc cơ |
| `boss_missiles` | 9M133 Kornet | atgm_kornet | 0,96 | Behemoth của Mara |
| `buk_launcher` | 9M317 Buk | buk | 4,44 | PK tầm trung |
| `bunker_buster_bomb` | GBU-28 | gbu_28 | 2,92 | Ném bom lượn |
| `caesar_155` | 155 mm L/52 (CAESAR) | shell_155 | 0,8 | Pháo bánh lốp |
| `coyote_interceptor` | Coyote Block 2 | coyote_block2 | 0,8 | Drone chặn |
| `cruiser_203` | Mk 71 203 mm (twin) | shell_155 | 1,04 | Tuần dương hạm |
| `fpv_fibre` | Fibre-optic FPV drone (1.5 kg) | fpv_drone | 0,8 | FPV cáp quang |
| `fpv_hangar` | FPV drone (1.5 kg) | fpv_drone | 0,8 | Nhà chứa drone |
| `fpv_hangar_swarm` | FPV drone (1.5 kg) | fpv_drone | 0,8 | Bầy đàn |
| `fpv_swarm` | FPV drone (1.5 kg) | fpv_drone | 0,8 | Drone FPV, Drone FPV TN |
| `fpv_swarm_mini` | Switchblade 300 | switchblade_300 | 0,8 | FPV cáp quang |
| `glide_fab500` | FAB-500 M-62 with UMPK glide kit | bomb | 1,2 | Ném bom lượn |
| `guided_bomb` | GBU-39 SDB (110 kg) | gbu39 | 0,9 | Morrigan, TK tàng hình, UAV tấn công |
| `gun_155_coastal` | M284 155 mm (coastal battery) | shell_155 | 0,8 | Pháo bờ biển |
| `gun_155_twin_ap` | M284 155 mm (twin) AP | shell_155 | 0,8 | Pháo hạng nặng, Pháo đài thép |
| `gun_155_twin_coastlr` | M284 155 mm (twin, long-range coastal) | shell_155 | 0,8 | Pháo bờ biển |
| `howitzer` | M284 155 mm | shell_155 | 0,8 | Lựu pháo, Lựu pháo TN |
| `howitzer_cb` | M284 155 mm | shell_155 | 0,8 | Phản pháo |
| `howitzer_fixed` | M284 155 mm | shell_155 | 0,8 | Trận địa pháo |
| `jassm` | AGM-158 JASSM (450 kg) | jassm | 2,13 | Máy bay mẹ, OTC tàng hình |
| `jet_bombs` | FAB-250 (250 kg) | bomb_fab | 0,98 | Cường kích, Cường kích TN, Tàng hình hạm |
| `kh29` | Kh-29L | kh29l | 1,95 | Cường kích, Cường kích TN |
| `kornet_multi` | 9M133 Kornet | atgm_kornet | 0,96 | Đa năng |
| `kornet_top` | 9M133 Kornet | atgm_kornet | 0,96 | Đánh từ trên |
| `mortar_240_fixed` | 2B8 240 mm (emplacement) | mortar_bomb | 1,2 | Cối nặng |
| `one_shot_kornet` | 9M133 Kornet | atgm_kornet | 0,96 | TL một lần |
| `p26_bastion_main_b155` | M284 155 mm (Bastion) | shell_155 | 0,8 | Bastion, Monster |
| `p26_bastion_sec_b240` | 2B8 240 mm | mortar_bomb | 1,2 | Bastion, Bastion Mk.0, Monster |
| `p26_bastion_tiny_kornet_twin` | 9M133 Kornet | atgm_kornet | 0,96 | Bastion, Monster |
| `p26_behemoth_tiny_boss_missiles` | 9M133 Kornet | atgm_kornet | 0,96 | Behemoth |
| `p26_behemoth_tiny_kornet_twin` | 9M133 Kornet | atgm_kornet | 0,96 | Behemoth |
| `p26_jotunn_jo203` | 2A44 203 mm | shell_155 | 1,04 | Jötunn |
| `p26_leviathan_lev406` | Mk 7 406 mm/50 (Iowa, triple) | shell_155 | 1,56 | Kraken, Leviathan |
| `p26_leviathan_sec_lev155` | 155 mm/60 (triple) | shell_155 | 0,8 | Kraken, Leviathan |
| `p26_matriarch_direct_ma_atgm` | 9M133 Kornet | atgm_kornet | 0,96 | Matriarch, Stymphalos |
| `p26_roc_direct_roc_atgm` | Kornet (dropped from the bay) | atgm_kornet | 0,96 | Garuda, Roc |
| `p26_roc_main_roc_bombs` | bomb-bay stick 400 kg | shell_155 | 1,04 | Argus, Garuda, Roc |
| `patriot` | MIM-104 Patriot PAC-2 | patriot | 4,24 | Trạm PK tầm xa |
| `sam` | Starstreak / Stinger SHORAD | shorad_dart | 1,22 | Cao xạ, Phòng không TN, Tháp PK, Tổ vác vai |
| `sam_48n6` | S-400 48N6 | patriot | 6 | PK tầm xa, SAM tầm xa TN |
| `sam_battery` | MIM-104 Patriot PAC-2 | patriot | 4,24 | Nemesis |
| `sam_battery_lrr` | MIM-104 Patriot PAC-2 | patriot | 4,24 | Radar tầm xa |
| `sam_pac3` | Patriot PAC-3 MSE | patriot | 4,24 | PAC-3 |
| `sam_post` | 9M317 Buk | buk | 4,44 | Jötunn, Kraken, Leviathan, Typhon |
| `siege_mortar_240` | 2B8 240 mm (siege tank) | mortar_bomb | 1,2 | Công thành |
| `stealth_payload` | GBU-31 JDAM (907 kg) | jdam | 1,94 | OTC tàng hình |
| `stinger_post` | FIM-92 Stinger (tower post) | shorad_dart | 1,22 | Stinger |
| `swarm_drones` | FPV drone (1.5 kg) | fpv_drone | 0,8 | Máy bay mẹ |
| `thermobaric_bomb` | ODAB-500 | odab_500 | 1,23 | Ném bom lượn |
| `tower_kornet` | 9M133 Kornet | atgm_kornet | 0,96 | Tháp ATGM |

#### Siêu vũ khí của boss chủ lực (16)

Prompt 25 C1: chỉ 16 boss chủ lực có siêu vũ khí (đòn lớn của prompt 18 với số của file cân bằng); mini boss không có. Mỗi siêu vũ khí có âm cảnh báo riêng. Số ở đây là số gốc; trong trận cộng hệ số của cấp boss chủ lực (sát thương ×1,2, hồi ×0,85) và của độ khó.

| Boss | Siêu vũ khí | Gồm | Hồi | Cảnh báo | Cách né | Cách ngắt |
|---|---|---|---|---|---|---|
| **Bastion · Pháo đài** | **Pháo cối 420 mm** Một quả cối 420 mm: 2.000 trong lõi 10 m, còn 40% tới rìa 20 m, gấp đôi lên công trình và tháp; vòng đỏ báo trước 4 giây. Cứ 45 giây. | loạt nổ, 1 × 2.000, nổ 10 m | 45 s | 4 s | Ra khỏi vòng đỏ, hoặc giữ quân dưới vòm của máy phát khiên: vòm hấp thụ được vụ nổ. | Phá khẩu cối: mất luôn đòn này (tới lần tự vá duy nhất của nó). |
| **Behemoth · Quái vật thép** | **Loạt pháo chính dồn** Ba loạt, mỗi loạt hai quả 152 mm nổ mạnh, mỗi quả 600, rải trong vòng tròn bán kính 14 m: mỗi quả rơi vào vòng đỏ riêng (lõi 8,5 m đủ sát thương, rìa 17 m còn 40%), vạch trước… | loạt nổ, 6 × 600, nổ 8,5 m, trong vòng 14 m | 45 s | 3,5 s | Bước ra khỏi sáu vòng tròn: mỗi vụ nổ lan 8 m. | Phá pháo chính trong lúc cảnh báo. |
| **Jötunn · Pháo đài di động** | **Loạt pháo 203 mm** Bốn quả 203 mm, mỗi quả 900 (lõi 10 m, rìa 20 m còn 40%), rải trong vòng tròn bán kính 14 m, mỗi lựu pháo hai quả; cảnh báo 4 giây. Cứ 50 giây. | loạt nổ, 4 × 900, nổ 10 m, trong vòng 14 m | 50 s | 4 s | Rời khỏi vòng, hoặc núp dưới vòm khiên: khiên hấp thụ được. | Phá một lựu pháo: mỗi khẩu góp hai trong bốn quả. |
| **Leviathan · Thiết giáp hạm** | **Loạt bắn mạn chín nòng** Chín quả đạn 406 mm, mỗi quả 950 (lõi 12 m, rìa 20 m còn 40%), từ ba tháp pháo chính rải theo dải 60 × 12 m qua căn cứ, mạnh hơn một phần ba lên công trình; cảnh báo 4 giây… | dải bom, 9 × 950, nổ 12 m, dải 60 × 12 m | 50 s | 4 s | Đưa quân ra khỏi dải đánh dấu; đạn pháo không bắn hạ được, nên hãy dàn quân ra. | Phá một tháp pháo chính trong lúc cảnh báo (giáp cấp 4: xe diệt tăng, pháo binh, bom): mỗi tháp bị phá bớt ba quả đạn. |
| **Matriarch · Tàu mẹ drone** | **Bom trượt hạng nặng** Một quả bom trượt hạng nặng từ khoang bom: 1.600 trong lõi 16 m, còn 40% tới rìa 20 m, gấp đôi lên công trình và tháp; bom lượn chậm tới vòng đánh dấu, ít nhất 3 giây. Cứ 45 g… | tên lửa, 1 × 1.600, nổ 16 m, 250 máu, bắn hạ được | 45 s | 3,5 s | Chạy ra khỏi vòng; khi khoang bom mở, phòng không trúng tàu mẹ mạnh hơn 30%. | Phá khoang bom, hoặc bắn hạ quả bom khi nó lượn (máu 250): phòng không, C-RAM, la-de PK. |
| **Moloch · Nhà máy di động** | **Xả xưởng** Cửa xưởng mở 4 giây, rồi mọi cửa cùng xả: sáu xe một lúc, kèm tám phát pháo 152 mm nổ mạnh (mỗi phát 350, lõi 6 m, rìa 12 m còn 40%) vào cụm quân gần nhất. Cứ 50 giây. | thả quân, 6 xe; loạt nổ, 8 × 350, nổ 6 m, trong vòng 12 m | 50 s | 4 s | Đưa cụm quân ra khỏi vùng đánh dấu; sẵn sàng đón thêm sáu xe. | Phá một cửa xưởng lúc cảnh báo: chỉ ra một nửa; phá cả hai thì chỉ còn loạt pháo. |
| **Nemesis · Đoàn tàu tên lửa** | **Tên lửa Tận thế** Bốn giây dựng bệ phóng, rồi một tên lửa nhiệt áp bay vào HQ hoặc cụm quân lớn nhất, có đồng hồ bay (6 giây, xa hơn thì lâu hơn): 3.500 trong lõi 18 m, còn 40% tới rìa 20 m, mạnh h… | tên lửa, 1 × 3.500, nổ 18 m, 600 máu, bắn hạ được | 50 s | 4 s | Dàn quân ra khỏi điểm rơi được đánh dấu trước khi hết giờ. | Phá bệ phóng trong lúc dựng, hoặc bắn hạ tên lửa trên đường bay (máu 600): khẩu đội PAC-3 và Vòm Sắt, cùng mọi phòng không, C-RAM hay la-de PK bên dưới. |
| **Kronos · Máy xúc mỏ** | **Quét gầu** Bánh gầu quét cung 120° dài 25 m phía trước: khoảng 2.500 động năng (xuyên cao) mỗi đơn vị, gấp đôi lên công trình và tháp. Cứ 45 giây. | quét hình quạt, 120° × 25 m, 2.500 | 45 s | 4 s | Ra khỏi cung đánh dấu phía trước; đánh vào hông và sau. | Phá cần gầu (lúc cảnh báo hoặc trước đó). |
| **Monster · Pháo tự hành 800 mm** | **Đạn 800 mm** Một quả đạn 800 mm: 4.000 trong lõi 20 m, còn 40% tới rìa 20 m, nặng gấp đôi với công trình; nòng nâng từ từ, vòng đỏ hiện 4 giây. Mỗi 50 giây. | loạt nổ, 1 × 4.000, nổ 20 m | 50 s | 4 s | Ra khỏi vòng đỏ; vòng rất rộng nên đi sớm. | Phá khẩu cối (nòng): mất luôn phát đạn. |
| **Typhon · Tàu ngầm tên lửa** | **Phóng tên lửa từ dưới nước** Sáu tên lửa vào căn cứ ta: mỗi quả khoảng 700 nổ mạnh (lõi 9 m, rìa 18 m còn 40%), gấp đôi lên công trình; sau 4 giây cảnh báo có đồng hồ bay. Cứ 50 giây. | tên lửa, 6 × 700, nổ 9 m, 250 máu, bắn hạ được | 50 s | 4 s | Đưa quân ra khỏi các điểm đánh dấu; tháp không di chuyển được nên hãy che chắn. | Phá cửa ống phóng lúc cảnh báo (cửa lộ trên mặt nước), hoặc bắn hạ tên lửa (mỗi quả 250 máu). |
| **Kraken · Tàu sân bay** | **Đợt không kích** Mười hai quả bom, mỗi quả 400 (lõi 9 m, rìa 18 m còn 40%), thành dải 90 × 14 m theo hướng tàu; cảnh báo 4 giây. Mỗi 50 giây. | dải bom, 12 × 400, nổ 9 m, dải 90 × 14 m | 50 s | 4 s | Bước ngang ra khỏi dải đỏ. | Phá boong cất cánh trong lúc cảnh báo: đợt không kích và máy bay đều dừng. |
| **Roc · Khí cầu chỉ huy** | **Rải thảm** Mười sáu quả bom 250 kg, mỗi quả 400 (lõi 7 m, rìa 14 m còn 40%), thành dải 80 × 12 m theo đường bay; cảnh báo 4 giây. Cứ 50 giây. | dải bom, 16 × 400, nổ 7 m, dải 80 × 12 m | 50 s | 4 s | Bước ngang ra khỏi dải, tránh khỏi đường bay của nó. | Phá khoang bom. |
| **Garuda · Cánh bay ném bom khổng lồ** | **Rải thảm** Hai mươi quả bom, mỗi quả 350 (lõi 7 m, rìa 14 m còn 40%), thành dải 100 × 14 m theo đường bay; cảnh báo 4 giây. Mỗi 50 giây. | dải bom, 20 × 350, nổ 7 m, dải 100 × 14 m | 50 s | 4 s | Bước ngang ra khỏi dải. | Phá khoang bom. |
| **Daedalus · Tàu đổ bộ quỹ đạo** | **Đổ bộ ồ ạt từ quỹ đạo** Tám khoang cùng rơi vào một cụm quân: mỗi khoang chạm đất gây 600 động năng (xuyên cao, lõi 6 m, rìa 12 m còn 40%) rồi thả một xe; cảnh báo 4 giây. Cứ 50 giây. | loạt nổ, 8 × 600, nổ 6 m, trong vòng 12 m | 50 s | 4 s | Tản cụm quân bị đánh dấu ra; giáp dày cũng không cứu được. | Phá một cửa thả khoang lúc cảnh báo: chỉ còn bốn khoang rơi. |
| **Icarus · Phi thuyền quỹ đạo** | **Mưa thanh vonfram** Bảy thanh vonfram rơi xuống các cụm quân, ưu tiên xe tăng giáp dày, từ vệ tinh nó để lại trên quỹ đạo: 1.800 động năng mỗi thanh, xuyên rất cao, bán kính 7 m, có 4 giây cột sáng… | thanh tungsten từ vệ tinh, 7 × 1.800, nổ 7 m; từ pha 3: 9 phát, hồi 45 s | 45 s | 4 s | Ra khỏi các vòng tròn; khói và APS không chặn được. Vòm khiên hấp thụ một phần sát thương trong lúc còn hoạt động. | Phá ăng-ten liên kết vệ tinh trong lúc cảnh báo để hủy thanh đang rơi; phá hẳn thì hết mưa thanh vonfram cho tới khi nó tự vá lại. Ăng-ten bắn được ở tầng cao, tầng thấp, và cả khi đã rơi xuống đất. |
| **Hyperion · Trạm gương quỹ đạo** | **Tia mặt trời** Một tia đốt dải 70 × 6 m trong 4 giây, 500 mỗi giây; cảnh báo 4 giây. Mỗi 50 giây. | dải bom, 4 × 500, nổ 3 m, dải 70 × 6 m | 50 s | 4 s | Rời ngay dải hẹp. | Phá tia la-de chính trong lúc cảnh báo. |

#### 10f. Đạn thay thế (hai loại đạn)

Prompt 25 G: nhiều súng nạp được loại đạn thứ hai; súng tự chọn theo mục tiêu (xe giáp, xe nhẹ, máy bay, công trình), đổi đạn mất thời gian nạp của chính súng (tối thiểu 0,5 s) và giữ loại đạn ít nhất 2 s. Nhịp bắn, tầm và băng đạn vẫn là của súng; chỉ loại sát thương, xuyên, sát thương, nổ lan và dạng đạn đổi. Cột cuối là đạn gốc của súng (sát thương / nổ lan m). Biểu tượng đổi đạn nằm trên ô vũ khí của thẻ, trang chi tiết xe và bảng hiệu ứng. Chưa cân bằng lại: số theo file Excel và số của súng.

#### Cân bằng đợt 2

Áp từ manifest của file cân bằng đợt 2 (bản v2) bằng `Tools/balance/p29_apply.py`; nhật ký ở `Docs/balance/apply_log_p29.md`. Máu hiển thị = máu dữ liệu × độ lì (2,2). Hệ số sát thương nhân mọi vũ khí của xe, không sửa vũ khí dùng chung.

#### Pháo sáng (số lần dự trữ)

Hồi một lần khi ở vòng chờ, nạp đầy khi về Bãi đáp hoặc sở chỉ huy. Mồi bẫy nhiệt: +1 lần, hồi nhanh hơn 25%, chỉ cho đơn vị đã có pháo sáng.

#### APS

SELF_APS chỉ chặn tên lửa dẫn đường, drone, rốc-két bắn thẳng. Trophy: NONE không gắn; RETROFIT_ELIGIBLE 2 lần, hồi 20 s; BUILT_IN +1 lần, hồi ×0,75. Boss và tháp giữ số riêng.

| Thực thể | Khả năng | Chế độ | Lần / hồi / bán kính |
|---|---|---|---|
| Tăng chủ lực | RetrofitEligible | tự suy ra | — |
| Siêu tăng | BuiltIn | tự suy ra | 3 / 10 s / 20 m |
| Xe la-de phòng không | — | PointDefense | 1 / 0.8 s / 30 m |
| headquarters.shield | — | tự suy ra | 6 / 0.6 s / 45 m |
| c_ram | — | tự suy ra | 4 / 0.6 s / 35 m |
| c_ram.centurion | — | tự suy ra | 5 / 0.35 s / 35 m |
| c_ram.dome | — | tự suy ra | 6 / 12 s / 60 m |
| missile_battery.pac3 | — | tự suy ra | 4 / 16 s / 72 m |
| laser_ad_station | — | tự suy ra | 1 / 0.8 s / 40 m |
| Tăng thế hệ mới | BuiltIn | SelfAps | 2 / 10 s / 20 m |
| Behemoth · Quái vật thép | — | tự suy ra | 2 / 4 s / 11 m |
| Icarus · Phi thuyền quỹ đạo | — | tự suy ra | 3 / 1.4 s / 49.6 m |
| Tempest · Behemoth pháo điện từ | — | tự suy ra | 2 / 1.6 s / 26 m |
| Charybdis · Tàu đệm khí đổ bộ | — | tự suy ra | 2 / 3 s / 22 m |
| Leviathan · Thiết giáp hạm | — | tự suy ra | 3 / 2.2 s / 30 m |
| sea_corvette | — | PointDefense | 2 / 2.5 s / 32 m |
| sea_cruiser | — | PointDefense | 2 / 2.4 s / 30 m |
| Daedalus · Tàu đổ bộ quỹ đạo | — | tự suy ra | 2 / 1.6 s / 31.6 m |
| Icarus Mk.0 · Phi thuyền nguyên mẫu | — | PointDefense | 3 / 1.4 s / 19.5 m |
| mara_behemoth | — | tự suy ra | 2 / 4 s / 11 m |

#### Gungnir

Boss chủ lực chương 11: máu 133.365; siêu vũ khí mỗi 45 s, nhắm toàn bản đồ, cảnh báo 3 s có đường ngắm; xuyên tối đa 5 xe × 1.000 rồi nổ 2.000 ở xe cuối (lõi 12 m, rìa 20 m còn 40%); không bắn máy bay, không chặn được, pháo sáng và APS không có tác dụng.

Sheet: 01_vu_khi_dan/Bang_sat_thuong — Bảng sát thương (6 dòng, 6 cột)

| id | mat_dat | may_bay | cong_trinh |
|---|---|---|---|
| Energy | 1.0 | 1.5 | 0.5 |
| Fire | 1.5 | 0.0 | 1.0 |
| Fragmentation | 0.5 | 1.3 | 0.1 |
| HighExplosive | 1.0 | 0.0 | 1.5 |
| Kinetic | 1.0 | 0.3 | 0.6 |
| ShapedCharge | 1.0 | 0.3 | 0.6 |

Sheet: 01_vu_khi_dan/Bang_xuyen_giap — Bảng xuyên giáp (6 dòng, 5 cột)

| id | chenh_xuyen_giap | he_so |
|---|---|---|
| buoc_0 | +2 | 1.2 |
| buoc_1 | +1 | 1.0 |
| buoc_2 | 0 | 0.85 |
| buoc_3 | -1 | 0.5 |
| buoc_4 | -2 | 0.25 |
| buoc_5 | -3 | 0.1 |

Sheet: 01_vu_khi_dan/Khac_che — Khắc chế (APS, phòng thủ điểm) (22 dòng, 28 cột)

| id | loai_don_vi | he_phong_ve | chan_directMissile | chan_drone | chan_directRocket | chan_artilleryRocket | chan_mortarShell | chan_artilleryShell | chan_tankShell |
|---|---|---|---|---|---|---|---|---|---|
| behemoth | boss | SELF_APS | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| behemoth_mk0 | boss |  | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| behemoth_tempest | boss | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| c_ram | thap | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| c_ram.centurion | thap | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| c_ram.dome | thap | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| cerberus | boss |  | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| daedalus | boss | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| headquarters.shield | cong_trinh | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| icarus_mk0 | boss | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| iron_beam | xe | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| landing_hovercraft | boss | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| laser_ad_station | thap | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| leviathan | boss | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| main_battle_tank | xe | SELF_APS | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| mara_behemoth | xe | SELF_APS | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| missile_battery.pac3 | thap | SELF_APS | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| next_gen_tank | xe | SELF_APS | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| sea_corvette | xe | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| sea_cruiser | xe | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| silver_bug | boss | POINT_DEFENSE | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| titan_tank | xe | SELF_APS | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |

*in 10 / 28 cột; 15 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 01_vu_khi_dan/He_so_toan_cuc — Hệ số toàn cục (4 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so |
|---|---|---|---|
| damageTable.thermobaric | damageTable | thermobaric | 2.0 |
| firepower.propBlasts | firepower | propBlasts | 1.5 |
| firepower.strikes | firepower | strikes | 2.0 |
| firepower.vehicleBlasts | firepower | vehicleBlasts | 2.0 |

Sheet: 01_vu_khi_dan/Vu_khi — Vũ khí (372 dòng, 174 cột)

| id | ten_that | ho_id | bien_the_id | dong_vu_khi_id | nhom | co_mm | dau_no_kg | loai_sat_thuong | xuyen |
|---|---|---|---|---|---|---|---|---|---|
| aa_25_triple | Type 96 25 mm (triple) | cal_25 | flak |  | autocannon | 25 |  | Fragmentation | 1 |
| aa_25_triple_ap | Type 96 25 mm AP (triple) | cal_25 |  |  | autocannon | 25 |  | Kinetic | 2 |
| agl_40 | Mk 19 40 mm | gl_40 |  | mk_19_40_mm | grenade | 40 |  | HighExplosive | 2 |
| aim9 | AIM-9 Sidewinder | sam_aim_9_sidewinder |  | aim_9_sidewinder | aa_missile |  | 9.4 | Fragmentation | 2 |
| air_cruise_missile | Kh-101 (400 kg) | cruise_kh_101 |  |  | cruise |  | 400 | HighExplosive | 3 |
| air_to_air | AIM-120 AMRAAM | sam_aim_120_amraam |  |  | aa_missile |  | 20 | Fragmentation | 3 |
| airship_drones | FPV drone (1.5 kg) | drone_fpv_drone |  | fpv_drone | drone |  | 1.5 | ShapedCharge | 3 |
| airship_flak | S-60 57 mm | cal_57 | flak |  | autocannon | 57 |  | Fragmentation | 2 |
| amos_120 | 120 mm AMOS (twin) | cal_120_he | mortar |  | mortar | 120 |  | HighExplosive | 2 |
| anti_radar_missile | AGM-88 HARM | msl_agm_88_harm |  | agm_88_harm | missile |  | 68 | HighExplosive | 3 |
| anti_ship_missile | NSM / P-800 Oniks | msl_nsm_p_800_oniks |  | nsm_oniks | missile |  | 250 | HighExplosive | 4 |
| apkws_rocket | APKWS (laser-guided Hydra 70) | rkt_70_80 | guided | apkws | rocket | 70 |  | ShapedCharge | 2 |
| at_gun_100 | MT-12 Rapira 100 mm | cal_100_105_ap |  |  | tank_gun | 100 |  | Kinetic | 3 |
| ataka | 9M120 Ataka | atgm_9m120_ataka |  | 9m120_ataka | atgm |  | 7.4 | ShapedCharge | 4 |
| atgm | BGM-71 TOW-2 | atgm_bgm_71_tow_2 |  |  | atgm |  | 5.9 | ShapedCharge | 4 |

*15 / 372 dòng đầu: xem sheet 01_vu_khi_dan/Vu_khi; in 10 / 174 cột; 82 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 01_vu_khi_dan/Vu_khi_suy_ra — Vũ khí: suy ra (372 dòng, 55 cột)

| id | bac_so | vien_moi_lan_bop | vien_moi_lan_bop_game | vien_moi_chu_ky | vien_moi_chu_ky_game | chu_ky_day_du_s | chu_ky_day_du_s_game | sat_thuong_moi_loat | sat_thuong_moi_loat_game |
|---|---|---|---|---|---|---|---|---|---|
| aa_25_triple | 1 | 1.0 | 1 | 15 | 15 | 3.1 | 3.1 | 255.0 | 255.0 |
| aa_25_triple_ap | 1 | 1.0 | 1 | 15 | 15 | 3.1 | 3.1 | 255.0 | 255.0 |
| agl_40 | 1 | 1.0 | 1 | 6.0 | 6 | 4.2 | 4.2 | 156.0 | 156.0 |
| aim9 | 2 | 1.0 | 1 | 1.0 | 1 | 8.0 | 8.0 | 236.0 | 236.0 |
| air_cruise_missile | 4 | 1.0 | 1 | 1.0 | 1 | 11.2 | 11.2 | 378.0 | 378.0 |
| air_to_air | 2 | 1.0 | 1 | 1.0 | 1 | 3.99 | 3.99 | 294.0 | 294.0 |
| airship_drones | 2 | 1.0 | 1 | 3.0 | 3 | 9.049999999999999 | 9.049999999999999 | 420.0 | 420.0 |
| airship_flak | 2 | 1.0 | 1 | 8 | 8 | 4.88 | 4.88 | 560.0 | 560.0 |
| amos_120 | 3 | 1.0 | 1 | 4.0 | 4 | 10.75 | 10.75 | 600.0 | 600.0 |
| anti_radar_missile | 3 | 1.0 | 1 | 1.0 | 1 | 8.0 | 8.0 | 300.0 | 300.0 |
| anti_ship_missile | 4 | 1.0 | 1 | 1.0 | 1 | 30.0 | 30.0 | 450.0 | 450.0 |
| apkws_rocket | 2 | 1.0 | 1 | 1.0 | 1 | 1.0 | 1.0 | 90.0 | 90.0 |
| at_gun_100 | 2 | 1.0 | 1 | 1.0 | 1 | 5.0 | 5.0 | 200.0 | 200.0 |
| ataka | 2 | 1.0 | 1 | 2.0 | 2 | 11.42 | 11.42 | 494.0 | 494.0 |
| atgm | 2 | 1.0 | 1 | 1.0 | 1 | 12.33 | 12.33 | 190.0 | 190.0 |

*15 / 372 dòng đầu: xem sheet 01_vu_khi_dan/Vu_khi_suy_ra; in 10 / 55 cột; 43 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 01_vu_khi_dan/Vu_khi_he_so_thuong — Vũ khí: hệ số thưởng (31 dòng, 10 cột)

| id | vu_khi_id | thu_tu | armor | class | flank | mult | still |
|---|---|---|---|---|---|---|---|
| anti_radar_missile/0 | anti_radar_missile | 0 |  | AntiAir |  | 2 |  |
| borer_drill/0 | borer_drill | 0 | Structure |  |  | 2 |  |
| bucket_wheel/0 | bucket_wheel | 0 | Structure |  |  | 3 |  |
| bunker_buster_bomb/0 | bunker_buster_bomb | 0 | Structure |  |  | 2 |  |
| detonator/0 | detonator | 0 | Structure |  |  | 0.5 |  |
| dozer_blade/0 | dozer_blade | 0 | Structure |  |  | 3 |  |
| dozer_blade/1 | dozer_blade | 1 | Heavy |  |  | 0.4 |  |
| dozer_blade/2 | dozer_blade | 2 | Light |  |  | 0.55 |  |
| drone_missile/0 | drone_missile | 0 | Structure |  |  | 1.5 |  |
| flak_35/0 | flak_35 | 0 |  | Plane |  | 1.5 |  |
| fpv_swarm/0 | fpv_swarm | 0 | Structure |  |  | 1.5 |  |
| gun_105_wheeled/0 | gun_105_wheeled | 0 |  |  | TRUE | 1.25 |  |
| gun_203_siege/0 | gun_203_siege | 0 | Structure |  |  | 2.4 |  |
| howitzer_cb/0 | howitzer_cb | 0 |  | Artillery |  | 1.25 |  |
| kornet_multi/0 | kornet_multi | 0 | Light |  |  | 0.6 |  |
| kornet_multi/1 | kornet_multi | 1 | Heavy |  |  | 0.85 |  |
| lancet/0 | lancet | 0 |  | Artillery |  | 2 |  |
| lancet/1 | lancet | 1 |  |  |  | 2 | 3 |
| lancet/2 | lancet | 2 | Structure |  |  | 1.5 |  |
| siege_mortar_240/0 | siege_mortar_240 | 0 | Structure |  |  | 2 |  |
| swarm_drones/0 | swarm_drones | 0 | Structure |  |  | 1.5 |  |
| technical_rockets/0 | technical_rockets | 0 | Structure |  |  | 0.6 |  |
| tower_flak_30/0 | tower_flak_30 | 0 | Light |  |  | 0.48 |  |
| tower_flak_30/1 | tower_flak_30 | 1 | Heavy |  |  | 0.4 |  |
| tower_kornet/0 | tower_kornet | 0 | Light |  |  | 0.4 |  |
| turret_gmlrs/0 | turret_gmlrs | 0 |  | Artillery |  | 1.5 |  |
| turret_gmlrs/1 | turret_gmlrs | 1 | Structure |  |  | 1.5 |  |
| turret_gun_120/0 | turret_gun_120 | 0 | Light |  |  | 0.65 |  |
| turret_rockets/0 | turret_rockets | 0 | Heavy |  |  | 0.46 |  |
| twin_30_flak/0 | twin_30_flak | 0 |  | Plane |  | 1.25 |  |
| twin_35_ahead/0 | twin_35_ahead | 0 |  | Plane |  | 1.5 |  |

Sheet: 01_vu_khi_dan/Dan_thay_the — Đạn thay thế (70 dòng, 15 cột)

| id | vu_khi_goc | dan_id | lien_ket | loai_dan | dung_cho | loai_sat_thuong | xuyen | sat_thuong_moi_phat | loi_m |
|---|---|---|---|---|---|---|---|---|---|
| aa_25_triple/aa_25_triple_ap | aa_25_triple | aa_25_triple_ap | roundOf | ap | ground | Kinetic | 2 | 17 | 0 |
| autocannon_25/autocannon_25_flak | autocannon_25 | autocannon_25_flak | roundOf | flak | air | Fragmentation | 1 | 17 | 2 |
| autocannon_30/autocannon_30_flak | autocannon_30 | autocannon_30_flak | roundOf | flak | air | Fragmentation | 2 | 22 | 2.5 |
| autocannon_40/autocannon_40_flak | autocannon_40 | autocannon_40_flak | roundOf | flak | air | Fragmentation | 2 | 30 | 3.5 |
| bastion_gun/bastion_gun_he | bastion_gun | bastion_gun_he | roundOf | he | light;structure | HighExplosive | 3 | 320 | 6.5 |
| bomber_tail_guns/bomber_tail_guns_api | bomber_tail_guns | bomber_tail_guns_api | roundOf | api | any | Kinetic | 2 | 9.5 | 0.0 |
| borer_cannon/borer_cannon_he | borer_cannon | borer_cannon_he | roundOf | he | light;structure | HighExplosive | 2 | 120 | 3 |
| boss_flak/boss_flak_ap | boss_flak | boss_flak_ap | roundOf | ap | ground | Kinetic | 2 | 25 | 0 |
| boss_heli_gun/boss_heli_gun_flak | boss_heli_gun | boss_heli_gun_flak | roundOf | flak | air | Fragmentation | 2 | 22 | 2.5 |
| boss_hmg/boss_hmg_api | boss_hmg | boss_hmg_api | roundOf | api | any | Kinetic | 2 | 15 | 0 |
| boss_howitzer/boss_howitzer_guided | boss_howitzer | boss_howitzer_guided | roundOf | guided | armour | HighExplosive | 4 | 420 | 8 |
| bunker_hmg/bunker_hmg_api | bunker_hmg | bunker_hmg_api | roundOf | api | any | Kinetic | 2 | 9.5 | 0 |
| bunker_hmg_twin/bunker_hmg_twin_api | bunker_hmg_twin | bunker_hmg_twin_api | roundOf | api | any | Kinetic | 2 | 9.5 | 0 |
| casemate_155/casemate_155_guided | casemate_155 | casemate_155_guided | roundOf | guided | armour | HighExplosive | 3 | 320 | 7 |
| ciws_aa/ciws_aa_flak | ciws_aa | ciws_aa_flak | roundOf | flak | air | Fragmentation | 2 | 12 | 2.5 |

*15 / 70 dòng đầu: xem sheet 01_vu_khi_dan/Dan_thay_the; in 10 / 15 cột; 3 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 01_vu_khi_dan/Phao_sang — Pháo sáng (18 dòng, 19 cột)

| id | loai_don_vi | mo_hinh | so_mount_flare | so_qua_moi_lan | do_nang_cap | so_voi_ban_goc | flare_charges | flare_recharge_s | flares_every_s |
|---|---|---|---|---|---|---|---|---|---|
| aerial_tanker | xe | aerial_tanker | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 3 | 20 |  |
| attack_helicopter | xe | attack_helicopter | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 2 |  |  |
| attack_jet | xe | attack_jet | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 2 |  |  |
| fighter_jet | xe | fighter_jet | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 2 |  |  |
| flare_searchlight_tower | thap | flare_searchlight_tower | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | giong |  |  | 15 |
| flare_tower | thap | flare_tower | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | giong |  |  | 15 |
| glide_bomber | xe | glide_bomber | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 2 |  |  |
| gunship_heli | xe | gunship_heli | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 2 |  |  |
| heavy_bomber | xe | heavy_bomber | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 3 |  |  |
| heavy_lift_helicopter | xe | heavy_lift_helicopter | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 3 | 20 |  |
| interceptor_jet | xe | interceptor_jet | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 2 |  |  |
| light_attack_heli | xe | light_attack_heli | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 2 | 20 |  |
| prop_attack_plane | xe | prop_attack_plane | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 2 | 20 |  |
| scout_heli | xe | scout_heli | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 2 | 20 |  |
| sky_gunship | xe | sky_gunship | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 3 |  |  |
| stealth_fighter | xe | stealth_fighter | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 2 |  |  |
| swarm_carrier | xe | swarm_carrier | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 3 |  |  |
| twin_rotor_gunship | xe | twin_rotor_gunship | 0 | NEED_CODE_CHECK | FlareDispenser (02_phuong_tien/Trang_bi_mo_dun) | doi | 3 | 20 |  |

*in 10 / 19 cột; 3 cột khác (và raw_json, nguon): xem sheet.*

### 10d. Tổng hợp boss

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_dps; 03_boss/Boss_hieu_qua. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §10d.

Mọi boss và mini boss cạnh nhau, đọc từ dữ liệu hiện tại: máu thân (trước hệ số độ khó), giáp trước/hông/sau/nóc, số bộ phận và phần máu của chúng, DPS duy trì lên xe nhẹ, xe nặng, máy bay và công trình (trước giáp), đòn lớn đầu tiên và số hộ tống trong mọi đợt.

Sheet: 03_boss/Boss_dps — Boss: DPS duy trì (41 dòng, 12 cột)

| id | he_so_vu_khi | he_so_sat_thuong_ra | he_so_hang | so_be | tong_dps_duy_tri | tong_dps_duy_tri_game | cach_bu |
|---|---|---|---|---|---|---|---|
| argus | 1.44 | 1.7892 | 1.2 | 2 | 814.2273589164784 | 814.2273589164784 | NEED_CODE_CHECK |
| armored_train | 1.859 | 0.8319 | 1.2 | 6 | 1472.785778546959 | 1472.785778546959 | NEED_CODE_CHECK |
| bastion_mk0 | 1.51 | 1.4708 | 1.2 | 3 | 288.6319582945737 | 288.6319582945737 | NEED_CODE_CHECK |
| behemoth | 1.0 | 1.0 | 1.4 | 10 | 1098.635326362491 | 1098.635326362491 | NEED_CODE_CHECK |
| behemoth_inferno | 1.962 | 1.0 | 1.2 | 3 | 552.3849250535332 | 552.3849250535332 | NEED_CODE_CHECK |
| behemoth_mk0 | 0.884 | 1.0 | 1.2 | 4 | 563.0441464722239 | 563.0441464722239 | NEED_CODE_CHECK |
| behemoth_mk2 | 1.928 | 1.0 | 1.2 | 3 | 992.2860383669616 | 992.2860383669616 | NEED_CODE_CHECK |
| behemoth_tempest | 1.74 | 1.0 | 1.2 | 3 | 519.8567849686848 | 519.8567849686848 | NEED_CODE_CHECK |
| caspian | 6.0 | 1.0 | 1.2 | 3 | 1559.7600799733423 | 1559.7600799733423 | NEED_CODE_CHECK |
| cerberus | 1.326 | 1.0 | 1.2 | 4 | 1165.954442756663 | 1165.954442756663 | NEED_CODE_CHECK |
| command_airship | 1.0 | 1.7892 | 1.4 | 8 | 1225.8887184265823 | 1225.8887184265823 | NEED_CODE_CHECK |
| daedalus | 1.0 | 1.0 | 1.4 | 4 | 777.5524475524476 | 777.5524475524476 | NEED_CODE_CHECK |
| drone_mothership | 1.0 | 1.0 | 1.4 | 9 | 1187.8241562511437 | 1187.8241562511437 | NEED_CODE_CHECK |
| earth_borer | 2.874 | 1.0854 | 1.2 | 3 | 665.4804479999999 | 665.4804479999999 | NEED_CODE_CHECK |
| fenrir | 2.222 | 0.9508 | 1.2 | 3 | 803.3324875060612 | 803.3324875060612 | NEED_CODE_CHECK |

*15 / 41 dòng đầu: xem sheet 03_boss/Boss_dps.*

Sheet: 03_boss/Boss_hieu_qua — Boss: hiệu quả vũ khí chính (205 dòng, 20 cột)

| id | boss_id | vu_khi | xe_tham_chieu | giap_mat_trung | he_so_trung | he_so_trung_game | sat_thuong_moi_don | sat_thuong_moi_don_game | so_don_de_ha |
|---|---|---|---|---|---|---|---|---|---|
| argus/armored_car | argus | p26_roc_main_roc_bombs | armored_car | 0 | 1.0 | 1.0 | 2164.2163199999995 | 2164.2163199999995 | 1.0 |
| argus/gun_turret | argus | p26_roc_main_roc_bombs | gun_turret | 3 | 1.5 | 1.5 | 3246.3244799999993 | 3246.3244799999993 | 2.0 |
| argus/heavy_tank | argus | p26_roc_main_roc_bombs | heavy_tank | 2 | 1.0 | 1.0 | 2164.2163199999995 | 2164.2163199999995 | 3.0 |
| argus/ifv | argus | p26_roc_main_roc_bombs | ifv | 0 | 1.0 | 1.0 | 2164.2163199999995 | 2164.2163199999995 | 1.0 |
| argus/main_battle_tank | argus | p26_roc_main_roc_bombs | main_battle_tank | 1 | 1.0 | 1.0 | 2164.2163199999995 | 2164.2163199999995 | 2.0 |
| armored_train/armored_car | armored_train | train_gun | armored_car | 1 | 1.2 | 1.2 | 1336.1778144 | 1336.1778144 | 1.0 |
| armored_train/gun_turret | armored_train | train_gun | gun_turret | 3 | 0.6 | 0.6 | 668.0889072 | 668.0889072 | 6.0 |
| armored_train/heavy_tank | armored_train | train_gun | heavy_tank | 4 | 0.85 | 0.85 | 946.4592852000001 | 946.4592852000001 | 5.0 |
| armored_train/ifv | armored_train | train_gun | ifv | 2 | 1.2 | 1.2 | 1336.1778144 | 1336.1778144 | 2.0 |
| armored_train/main_battle_tank | armored_train | train_gun | main_battle_tank | 4 | 0.85 | 0.85 | 946.4592852000001 | 946.4592852000001 | 3.0 |
| bastion_mk0/armored_car | bastion_mk0 | p26_bastion_sec_b240 | armored_car | 0 | 1.0 | 1.0 | 2931.5985600000004 | 2931.5985600000004 | 1.0 |
| bastion_mk0/gun_turret | bastion_mk0 | p26_bastion_sec_b240 | gun_turret | 3 | 1.5 | 1.5 | 4397.3978400000005 | 4397.3978400000005 | 1.0 |
| bastion_mk0/heavy_tank | bastion_mk0 | p26_bastion_sec_b240 | heavy_tank | 2 | 1.0 | 1.0 | 2931.5985600000004 | 2931.5985600000004 | 2.0 |
| bastion_mk0/ifv | bastion_mk0 | p26_bastion_sec_b240 | ifv | 0 | 1.0 | 1.0 | 2931.5985600000004 | 2931.5985600000004 | 1.0 |
| bastion_mk0/main_battle_tank | bastion_mk0 | p26_bastion_sec_b240 | main_battle_tank | 1 | 1.0 | 1.0 | 2931.5985600000004 | 2931.5985600000004 | 1.0 |

*15 / 205 dòng đầu: xem sheet 03_boss/Boss_hieu_qua; in 10 / 20 cột; 8 cột khác (và raw_json, nguon): xem sheet.*

### 10g. Boss: vụ nổ hai lớp, pha, giáp và cỡ

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss_phase; 03_boss/Boss_be_goc. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §10g.

Prompt 26: vũ khí nổ của boss có hai lớp. **Lõi** (bán kính nổ của vũ khí) nhận đủ sát thương; **rìa** (gấp đôi lõi, tối đa 20 m) nhận 40% sát thương. Vũ khí không có rìa nổ một lớp, giảm dần theo khoảng cách. Máu, vũ khí và cỡ của boss được làm lại theo chương (mục tiêu hạ boss chủ lực từ 2,5 phút ở chương 1 tới 4 phút ở chương 12, mini boss 60 đến 90 giây); Ixion và Gungnir được làm lại; mỗi boss có mốc thời đại ở dòng Tham khảo của thẻ. Pha: hệ số nhân vào từ mốc máu đó trở đi.

#### Pha, giáp và cỡ model (41 boss)

| Boss | Cấp | Máu | Giáp T/H/S/N | Cỡ model (m) | Pha |
|---|---|---|---|---|---|
| **Bastion Mk.0 · Pháo đài nguyên mẫu** | mini | 8.999 | 4/4/4/3 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Inferno · Behemoth phun lửa** | mini | 11.500 | 4/3/2/2 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Harpy · Trực thăng khổng lồ** | mini | 14.002 | 2/2/2/2 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Fenrir · Xe tiên phong** | mini | 14.002 | 4/4/3/2 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Behemoth Mk.0 · Behemoth nguyên mẫu** | mini | 15.848 | 3/3/2/1 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Juggernaut · Đoàn tàu bọc thép** | mini | 17.648 | 4/3/3/2 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Tempest · Behemoth pháo điện từ** | mini | 17.648 | 4/3/2/2 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Scylla · Tàu khu trục** | mini | 17.648 | 4/4/3/2 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Nyx · Tàu khu trục tàng hình** | mini | 17.648 | 4/4/3/2 | 53 × 9 × 11 | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Hive · Pháo đài drone** | mini | 21.341 | 4/3/2/2 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Locust · Tàu con drone** | mini | 21.341 | 1/1/1/1 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Stymphalos · Bầy UAV phản lực** | mini | 21.341 | 1/1/1/1 | 16 × 26 × 3 | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Bastion · Pháo đài** | chủ lực | 22.015 | 5/3/2/3 | — | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.2, tốc độ ×1.1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Charybdis · Tàu đệm khí đổ bộ** | mini | 25.011 | 3/2/1/1 | — | 45%: sát thương ×1, tốc độ ×1.2, nhận sát thương ×1, nhịp bắn ×1 |
| **Behemoth Mk.II · Behemoth nâng cấp** | mini | 25.011 | 4/3/2/2 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Cerberus · Đoàn xe ba khung** | mini | 25.011 | 3/3/2/2 | 16 × 8 × 6 | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Behemoth · Quái vật thép** | chủ lực | 28.518 | 5/3/2/2 | — | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.2, tốc độ ×1.1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Atlas · Xe chỉ huy siêu nặng** | mini | 29.359 | 4/3/2/2 | — | 45%: sát thương ×1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1, hồi 8% máu |
| **Tartarus · Máy khoan** | mini | 33.660 | 4/3/2/2 | — | 45%: sát thương ×1, tốc độ ×1.15, nhận sát thương ×1, nhịp bắn ×1 |
| **Ixion · Xe tải mỏ bọc thép** | mini | 33.660 | 4/3/2/2 | 26 × 12 × 10 | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Jötunn · Pháo đài di động** | chủ lực | 35.020 | 5/3/2/2 | — | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.2, tốc độ ×1.1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Caspian · Tàu bay sát mặt nước** | mini | 38.008 | 2/2/2/1 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Hydra · Tàu ngầm mang drone** | mini | 38.008 | 4/3/2/2 | 35 × 7 × 8 | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Morrigan · Tiêm kích của Raven** | mini | 41.140 | 1/1/1/1 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Spectre · Máy bay pháo** | mini | 44.342 | 2/2/2/2 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Icarus Mk.0 · Phi thuyền nguyên mẫu** | mini | 44.342 | 4/4/4/4 | — | — |
| **Argus · Khí cầu trinh sát** | mini | 44.342 | 2/2/2/2 | — | 45%: sát thương ×1.15, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Leviathan · Thiết giáp hạm** | chủ lực | 44.370 | 5/3/2/2 | — | 60%: sát thương ×1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Matriarch · Tàu mẹ drone** | chủ lực | 53.635 | 2/2/2/2 | — | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.2, tốc độ ×1.1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Moloch · Nhà máy di động** | chủ lực | 62.985 | 5/3/2/2 | — | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.2, tốc độ ×1.1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Nemesis · Đoàn tàu tên lửa** | chủ lực | 75.352 | 5/3/2/2 | — | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.2, tốc độ ×1.1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Kronos · Máy xúc mỏ** | chủ lực | 87.635 | 5/3/2/2 | — | 60%: sát thương ×1, tốc độ ×1.45, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.3, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Monster · Pháo tự hành 800 mm** | chủ lực | 87.635 | 5/3/2/3 | 40 × 22 × 13 | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.2, tốc độ ×1.1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Typhon · Tàu ngầm tên lửa** | chủ lực | 100.002 | 5/3/2/2 | — | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.2, tốc độ ×1.1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Kraken · Tàu sân bay** | chủ lực | 100.002 | 5/3/2/2 | 110 × 18 × 24 | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.2, tốc độ ×1.1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Roc · Khí cầu chỉ huy** | chủ lực | 116.662 | 2/2/2/2 | — | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.25, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Garuda · Cánh bay ném bom khổng lồ** | chủ lực | 116.662 | 2/2/2/2 | 28 × 70 × 4 | 60%: sát thương ×1.1, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 25%: sát thương ×1.2, tốc độ ×1.1, nhận sát thương ×1, nhịp bắn ×1.25 |
| **Gungnir · Pháo điện từ đường ray** | chủ lực | 133.365 | 3/2/1/1 | — | 45%: sát thương ×1.2, tốc độ ×1, nhận sát thương ×1, nhịp bắn ×1 |
| **Daedalus · Tàu đổ bộ quỹ đạo** | chủ lực | 133.365 | 3/3/3/3 | — | — |
| **Icarus · Phi thuyền quỹ đạo** | chủ lực | 149.982 | 4/4/4/4 | — | — |
| **Hyperion · Trạm gương quỹ đạo** | chủ lực | 149.982 | 4/4/4/4 | 67 × 44 × 20 | — |

Sheet: 03_boss/Boss_phase — Boss: pha (10 dòng, 12 cột)

| id | boss_id | thu_tu | at | damage | fire_rate | heal | radio | speed_m_s | transform |
|---|---|---|---|---|---|---|---|---|---|
| command_airship/0 | command_airship | 0 | 0.6 | 1.1 |  |  | radio.quaden.airship.phase2 |  | 2.5 |
| command_airship/1 | command_airship | 1 | 0.25 | 1.25 | 1.25 |  | radio.quaden.airship.half |  | 3 |
| earth_borer/0 | earth_borer | 0 | 0.45 |  |  |  | radio.hung.borer.half | 1.15 | 2.5 |
| kronos/0 | kronos | 0 | 0.6 |  |  |  | radio.hung.kronos.phase2 | 1.45 | 2.5 |
| kronos/1 | kronos | 1 | 0.25 | 1.3 | 1.25 |  | radio.hung.kronos.phase3 |  | 3 |
| landing_hovercraft/0 | landing_hovercraft | 0 | 0.45 |  |  |  | radio.kessler.hovercraft.half | 1.2 | 2.5 |
| leviathan/0 | leviathan | 0 | 0.6 |  |  |  | radio.kessler.leviathan.phase2 |  | 2.5 |
| leviathan/1 | leviathan | 1 | 0.25 |  | 1.25 |  | radio.kessler.leviathan.phase3 |  | 3 |
| rail_supergun/0 | rail_supergun | 0 | 0.45 | 1.2 |  |  | radio.orlov.supergun.half |  | 3 |
| supreme_command/0 | supreme_command | 0 | 0.45 |  |  | 0.08 | radio.hung.supreme.half |  | 3 |

Sheet: 03_boss/Boss_be_goc — Boss: bệ phụ gốc (107 dòng, 11 cột)

| id | boss_id | thu_tu | weapon | aim | slot |
|---|---|---|---|---|---|
| armored_train/0 | armored_train | 0 | boss_rockets | Free | rocket |
| armored_train/1 | armored_train | 1 | boss_hmg | Free | mg |
| armored_train/2 | armored_train | 2 | boss_flak | Free | mg |
| armored_train/3 | armored_train | 3 | train_gun | Free | main |
| armored_train/4 | armored_train | 4 | train_mortar | Free | mortar |
| armored_train/5 | armored_train | 5 | boss_flak | Free | mg |
| behemoth/0 | behemoth | 0 | gun_120mm | Free | gun |
| behemoth/1 | behemoth | 1 | boss_flak | Free | mg |
| behemoth/2 | behemoth | 2 | boss_flak | Free | mg |
| behemoth/3 | behemoth | 3 | boss_missiles | Hull | missile |
| behemoth/4 | behemoth | 4 | boss_missiles | Hull | missile |
| behemoth/5 | behemoth | 5 | kornet_twin | Free | missile |
| behemoth_inferno/0 | behemoth_inferno | 0 | boss_thermo | Free | rocket |
| behemoth_inferno/1 | behemoth_inferno | 1 | boss_flak | Free | mg |
| behemoth_inferno/2 | behemoth_inferno | 2 | boss_flamer | Turret | main |

*15 / 107 dòng đầu: xem sheet 03_boss/Boss_be_goc.*

### 10h. Săn trùm (Boss Hunt)

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Sanhunt; 03_boss/Sanhunt_ho_tro; 03_boss/Sanhunt_chua_xep. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §10h. Săn trùm.

Prompt 26 E: máu boss theo sức mạnh bộ bài; mọi số dưới đây là giá trị khởi đầu, chờ đo ở phase kiểm tra.

- **Sức mạnh P:** đo một lần lúc bắt đầu từ bộ bài mang theo (sát thương giấy mỗi giây của các thẻ chiến đấu, tính cả hạng thẻ, trang bị và chỉ huy) × 10 xe ra trận × 0,3 trúng boss, tối thiểu 60. Máu boss = P × thời gian mục tiêu × 0,6 × hệ số m × hệ số bậc; sát thương boss là của dữ liệu × m × hệ số bậc.
- **Tuần:** 10 boss (3 chủ lực, 7 mini; nhóm 3, 2, 2 mini dẫn tới mỗi boss chủ lực), mục tiêu mini 66 s, chủ lực 2.8 phút; m = 1 + 0.06 × số thứ tự (×1 tới ×1,54); nghỉ 15 s giữa các boss, quân sống sót được sửa 30% và chỉ giữ 50% CP; điểm hồi sinh sau mỗi boss chủ lực; đồng hồ 30 phút.
- **Toàn bộ:** 41 boss (17 chủ lực) theo thứ tự cốt truyện, chủ lực 2,5 phút, mini 1 phút; m từ ×0.8 tới ×1.3; điểm hồi sinh và lưu sau mỗi boss; mỗi boss là một trận mới (không giữ quân, CP khởi đầu như nhau), chỉ hỗ trợ tác chiến được giữ.
- **Hỗ trợ tác chiến:** sau mỗi boss chủ lực chọn 1 trong 3; tổng sức mạnh quân từ hỗ trợ tối đa +40%; khi đã chạm trần chỉ còn các hỗ trợ đổi cách chơi (thẻ bắn nhanh hơn, thả xe).
- **Bậc:** bốn độ khó của bảng chọn là bốn bậc (bảng dưới). Chưa làm: bậc Huyền thoại và các biến thể (mutator) cho Săn trùm.

#### Lời trong game

Tuần: 10 boss tuần này: 7 mini boss dẫn tới 3 boss chủ lực, boss sau mạnh hơn boss trước. Máu boss theo sức mạnh bộ bài bạn mang. Nghỉ 15 giây giữa các boss, xe còn sống được sửa 30% và giữ 50% CP; sau mỗi boss chủ lực (tối đa +40% sức mạnh đội quân từ hỗ trợ), chọn một trong ba hỗ trợ tác chiến và lưu điểm hồi sinh. Đồng hồ 30 phút.

Toàn bộ: Toàn bộ 41 boss chủ lực và mini boss của các chương đang mở, theo đúng thứ tự cốt truyện. Có điểm hồi sinh sau mỗi boss: chơi dần qua bao nhiêu lần cũng được. Mỗi boss là một trận mới: quân không được giữ và bạn bắt đầu với cùng lượng CP; chỉ hỗ trợ tác chiến được giữ (chọn sau mỗi boss chủ lực, tối đa +40% sức mạnh đội quân, sau đó chỉ còn các hỗ trợ đổi cách chơi). Xếp hạng theo tổng thời gian.

#### Hỗ trợ tác chiến (12)

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

Sheet: 03_boss/Sanhunt — Săn trùm (41 dòng, 9 cột)

| id | thu_tu | chu_luc | chuong | cach_xep | phong_khong | tuan |
|---|---|---|---|---|---|---|
| argus | 36 | FALSE | 10 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| armored_train | 9 | FALSE | 4 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| bastion_mk0 | 1 | FALSE | 1 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| behemoth | 4 | TRUE | 2 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| behemoth_inferno | 3 | FALSE | 2 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| behemoth_mk0 | 8 | FALSE | 13 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| behemoth_mk2 | 18 | FALSE | 6 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| behemoth_tempest | 10 | FALSE | 4 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| caspian | 28 | FALSE | 9 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| cerberus | 21 | FALSE | 6 | unslotted | NEED_CODE_CHECK | NEED_CODE_CHECK |
| command_airship | 35 | TRUE | 10 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| daedalus | 39 | TRUE | 11 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| drone_mothership | 16 | TRUE | 5 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| earth_borer | 24 | FALSE | 8 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |
| fenrir | 7 | FALSE | 3 | slot | NEED_CODE_CHECK | NEED_CODE_CHECK |

*15 / 41 dòng đầu: xem sheet 03_boss/Sanhunt.*

Sheet: 03_boss/Sanhunt_ho_tro — Săn trùm: hỗ trợ tác chiến (12 dòng, 8 cột)

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

Sheet: 03_boss/Sanhunt_chua_xep — Săn trùm: boss chưa có ô chương (10 dòng, 4 cột)

| id | sau_chuong |
|---|---|
| behemoth_mk0 | 3 |
| cerberus | 6 |
| garuda | 10 |
| hydra | 9 |
| hyperion | 12 |
| kraken | 9 |
| monster | 8 |
| morrigan | 9 |
| nyx | 4 |
| stymphalos | 5 |

### 10i. Sổ tay đạn

Trạng thái: Đã áp

Nguồn dữ liệu: 11_meta_giao_dien/So_tay_dan; 01_vu_khi_dan/Dong_vu_khi. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §Sổ tay đạn / Ammunition, §Sổ tay đạn: bậc.

#### Sổ tay đạn / Ammunition handbook

Sinh từ dữ liệu (balance.json) như mục Sổ tay đạn trong Hồ sơ của game; chạm vào chip ĐÁNH NÓC, ĐẠN THAY THẾ, NỔ TRÊN KHÔNG, DẪN ĐƯỜNG, PHÁ CÔNG TRÌNH, PHÁ TƯỜNG trên trang chi tiết mở đúng mục. / Generated from the data, as the game's Dossier tab.

#### Sổ tay đạn (tiếng Việt)

**Động năng**: mạnh với Mặt đất (×1), yếu với Máy bay (×0,3). Ví dụ: M2 Browning 12.7 mm, PKT / M240 7.62 mm, M242 Bushmaster 25 mm.

**Nổ lõm**: mạnh với Mặt đất (×1), yếu với Máy bay (×0,3). Ví dụ: BGM-71 TOW-2, APKWS (laser-guided Hydra 70), 9M120 Ataka.

**Nổ mạnh**: mạnh với Công trình (×1,5), yếu với Máy bay (×0). Ví dụ: Mk 19 40 mm, GBU-39 SDB (110 kg), AGM-158 JASSM (450 kg).

**Lửa**: mạnh với Mặt đất (×1,5), yếu với Máy bay (×0). Ví dụ: flamethrower.

**Mảnh**: mạnh với Máy bay (×1,3), yếu với Công trình (×0,1). Ví dụ: AIM-120 AMRAAM, GAU-22/A 25 mm, AIM-9 Sidewinder.

**Năng lượng**: mạnh với Máy bay (×1,5), yếu với Công trình (×0,5). Ví dụ: focused laser (300 kW), Iron Beam laser (100 kW).

Giáp có hướng: trước, hông, sau và nóc (xe tới cấp 4, boss tới cấp 5); trên nóc và lên máy bay không có mức áp đảo (×1 là cao nhất).

Ví dụ: một phát 2A42 30 mm của ifv (xuyên 2, sát thương 22) lên main_battle_tank (máu 2310): giáp trước cấp 4: ×0,25, 6; giáp hông cấp 2: ×0,85, 19.

| Dấu | Nghĩa |
|---|---|
| Đánh nóc | Trúng giáp nóc, mặt mỏng nhất. Ví dụ: Fibre-optic FPV drone (1.5 kg), FPV drone (1.5 kg), Switchblade 300 |
| Nhiệt áp | ×2 lên công trình thay cho ×1,5 của nổ mạnh (thay, không nhân thêm). Ví dụ: ODAB-500, TOS-1A 220 mm thermobaric |
| Dẫn đường | Bám mục tiêu; APS / phòng thủ điểm bắn hạ được, pháo sáng đánh lừa loại nhắm máy bay. Ví dụ: AIM-120 AMRAAM, BGM-71 TOW-2, AGM-158 JASSM (450 kg) |
| Nổ trên không | Đạn mảnh: ×1,3 lên máy bay. Ví dụ: AIM-120 AMRAAM, GAU-22/A 25 mm, AIM-9 Sidewinder |
| Đạn thay thế | Súng tự đổi khi mục tiêu hợp; giữ đạn ít nhất 2 s, đổi mất ít nhất 0,5 s. |
| Tầm tối thiểu | 120 mm AMOS (twin) (10 m), 9M723 Iskander (700 kg) (40 m), 155 mm L/52 (CAESAR) (25 m) |

| Hệ | Chặn |
|---|---|
| Giáp phản ứng nổ | Giảm tới 80% sát thương nổ lõm; đầu nổ kép xuyên qua. |
| Lồng chắn | Đỡ nổ lõm của rốc-két, tên lửa, drone; động năng và nhiệt áp đi qua. |
| SELF_APS | Chỉ tên lửa dẫn đường, drone, rốc-két bắn thẳng; không chặn đạn pháo xe tăng. |
| POINT_DEFENSE (C-RAM, la-de, vòm) | Tên lửa, drone, rốc-két, một phần đạn pháo binh (C-RAM 30%, la-de 0%); không chặn đạn pháo xe tăng; mỗi viên một hệ (gần nhất). |
| Pháo sáng | Đánh lừa tên lửa dẫn đường nhắm máy bay. |
| Khói | Che mục tiêu, làm mù la-de phòng thủ điểm. |
| Gây nhiễu | Làm tản drone và hỏa lực dẫn đường gọi vào vùng nhiễu. |
| Khiên | Vòm hấp thụ mọi đòn trừ năng lượng; khiên tháp chỉ đỡ đạn nhắm vào tháp. |

Xe phá tường (armored_bulldozer, engineer_vehicle, demolition_line_vehicle) gây ×1,5 lên tường (không lên tháp hay nhà chính).

#### Ammunition handbook (English)

**Kinetic**: strong against Ground (×1), weak against Air (×0.3). For example: M2 Browning 12.7 mm, PKT / M240 7.62 mm, M242 Bushmaster 25 mm.

**Shaped charge**: strong against Ground (×1), weak against Air (×0.3). For example: BGM-71 TOW-2, APKWS (laser-guided Hydra 70), 9M120 Ataka.

**High explosive**: strong against Structures (×1.5), weak against Air (×0). For example: Mk 19 40 mm, GBU-39 SDB (110 kg), AGM-158 JASSM (450 kg).

**Fire**: strong against Ground (×1.5), weak against Air (×0). For example: flamethrower.

**Fragmentation**: strong against Air (×1.3), weak against Structures (×0.1). For example: AIM-120 AMRAAM, GAU-22/A 25 mm, AIM-9 Sidewinder.

**Energy**: strong against Air (×1.5), weak against Structures (×0.5). For example: focused laser (300 kW), Iron Beam laser (100 kW).

Armour has a direction: front, side, rear and roof (vehicles up to level 4, bosses up to 5); on the roof and on aircraft a round never overmatches (×1 is the most).

Worked example: one shot of the ifv's 2A42 30 mm (penetration 2, 22 damage) on a main_battle_tank (health 2310): front armour 4: ×0.25, 6; side armour 2: ×0.85, 19.

| Mark | Meaning |
|---|---|
| Top attack | Strikes the roof armour, the thinnest face. For example: Fibre-optic FPV drone (1.5 kg), FPV drone (1.5 kg), Switchblade 300 |
| Thermobaric | ×2 on structures instead of high explosive's ×1.5 (replaces, never adds). For example: ODAB-500, TOS-1A 220 mm thermobaric |
| Guided | Follows its target; APS and point defence can shoot it down, flares draw off those aimed at aircraft. For example: AIM-120 AMRAAM, BGM-71 TOW-2, AGM-158 JASSM (450 kg) |
| Airburst | Fragmentation: ×1.3 against aircraft. For example: AIM-120 AMRAAM, GAU-22/A 25 mm, AIM-9 Sidewinder |
| Second rounds | The gun switches on its own when the target suits; a round stays in 2 s at least, a switch takes 0.5 s at least. |
| Minimum range | 120 mm AMOS (twin) (10 m), 9M723 Iskander (700 kg) (40 m), 155 mm L/52 (CAESAR) (25 m) |

| System | Stops |
|---|---|
| Reactive armour | Cuts shaped charges by up to 80%; a tandem warhead goes through. |
| Cage | Takes shaped charges on rockets, missiles, drones; kinetic and thermobaric go through. |
| SELF_APS | Guided missiles, drones, direct-fire rockets only; never a tank's shell. |
| POINT_DEFENSE (C-RAM, lasers, dome) | Missiles, drones, rockets, a share of artillery shells (C-RAM 30%, laser 0%); never a tank's shell; one system per round (the nearest). |
| Flares | Draw off guided missiles aimed at aircraft. |
| Smoke | Hides what is in it, blinds point-defence lasers. |
| Jamming | Scatters drones and guided fire called into its bubble. |
| Shield | A dome absorbs every hit but energy; a tower's shield only rounds aimed at the tower. |

Wall breakers (armored_bulldozer, engineer_vehicle, demolition_line_vehicle) do ×1.5 to walls (not to towers or the HQ).

#### Sổ tay đạn: bậc T0–T5 / Calibre tiers

Như mục "Bậc cỡ nòng T0–T5" của Sổ tay đạn trong game. Bậc lấy theo họ: càng to thì mỗi phát càng mạnh, nổ, hình và tiếng càng lớn, bù bằng thời gian nạp dài hơn. Đạn T4 và T5 của boss báo chỗ rơi ít nhất 0,5 s + lõi / 4,5 m/s (T4 ít nhất 2,5 s). / A round's tier comes from its family; a boss's T4-T5 rounds warn at least 0.5 s + core / 4.5 m/s.

| Bậc | Họ | Hình và tiếng | Look and sound |
|---|---|---|---|
| T0 | 12.7 mm heavy machine gun, 14.5 mm heavy machine gun, 7.62 mm machine gun, melee_bucket_wheel, melee_dozer_blade, melee_drill_head (+3) | Súng nhỏ: chớp mảnh, tiếng nổ giòn ngắn. | Small arms: a thin flash and a short crack. |
| T1 | 20 mm, 23 mm, 25 mm, 30 mm, 35 mm Oerlikon, 40 mm Bofors (+8) | Pháo tự động: chớp nhỏ, khói mỏng; nhiều súng cùng bắn nghe thành một trận đấu súng. | Autocannon: a small flash and thin smoke; many guns at once are heard as one firefight. |
| T2 | atgm_9k121_vikhr, atgm_9m113_konkurs, atgm_9m120_ataka, atgm_9m123_khrizantema, atgm_agm_114_hellfire, atgm_agm_114l_hellfire_longbow (+36) | Pháo vừa và rocket nhẹ: chớp vừa, quả cầu lửa nhỏ, bụi và đất tung lên. | Medium guns and light rockets: a medium flash, a small hot fireball, dust and earth thrown up. |
| T3 | atgm_agm_65_maverick, bomb_fab_250, 120 mm AP, 120 mm HE, 125 mm AP, 125 mm HE (+9) | Pháo nặng: chớp lớn, cầu lửa đầu nòng, khói dài và chậm, cột bụi; thân xe giật lùi. | Heavy guns: a big flash and muzzle fireball, long slow smoke, a dust column; the hull rocks back. |
| T4 | atgm_kh_29l, bal_9m723_iskander, 400 kg bomb, bomb_car_bomb, bomb_cbu_97_sensor_fuzed_weapon, bomb_fab_500 (+15) | Pháo rất nặng, Smerch, bom 400 kg: chớp rất lớn, cầu lửa cuộn, sóng xung kích trên mép vụ nổ, máy quay rung ngắn. | Very heavy guns, Smerch, 400 kg bombs: a very big flash, a rolling fireball, a shockwave on the blast's edge, a short camera shake. |
| T5 | 406 mm, 800 mm super-gun, EMRG electromagnetic railgun (Gungnir) | Siêu vũ khí: chớp sáng cả cảnh, đám mây hình nấm nhỏ, vòng trên lõi rồi trên mép, rung mạnh nhất. | Super weapons: a flash that lights the scene, a small mushroom cloud, rings on the core then the edge, the strongest shake. |

Sheet: 11_meta_giao_dien/So_tay_dan — Sổ tay đạn (2 dòng, 8 cột)

| id | nhom | khoa | gia_tri_chu |
|---|---|---|---|
| exampleShooter | handbook | exampleShooter | ifv |
| exampleTarget | handbook | exampleTarget | main_battle_tank |

Sheet: 01_vu_khi_dan/Dong_vu_khi — Dòng vũ khí thật (55 dòng, 12 cột)

| id | ten_that | khoi_nguon | so_vu_khi | projectile_model | projectile_scale | projectile_speed_m_s | round_length | round_weight | splash_m |
|---|---|---|---|---|---|---|---|---|---|
| 2a38_30_mm | 2A38 30 mm | weaponFamilies | 3 |  |  | 280 |  | 7.5 | 2.5 |
| 2a38_30_mm_ap | 2A38 30 mm AP | secondRounds.families | 3 |  |  | 280 |  | 7.5 | 0 |
| 2a42_30_mm | 2A42 30 mm | weaponFamilies | 3 |  |  | 200 |  | 32 | 0 |
| 2a42_30_mm_air_burst | 2A42 30 mm air-burst | secondRounds.families | 3 |  |  | 200 |  | 32 | 2.5 |
| 2a75_125_mm_he | 2A75 125 mm HE | secondRounds.families | 2 |  |  | 260 |  | 345 | 3 |
| 2a83_152_mm | 2A83 152 mm | weaponFamilies | 2 |  |  | 160 |  | 343 | 2.5 |
| 2a83_152_mm_he_frag | 2A83 152 mm HE-FRAG | secondRounds.families | 3 |  |  | 150 |  | 343 | 6.5 |
| 2b8_240_mm | 2B8 240 mm | weaponFamilies | 4 | mortar_bomb | 1.3333 | 38 | 1.2 | 543 | 9 |
| 2b11_120_mm | 2B11 120 mm | weaponFamilies | 2 | mortar_bomb |  | 32 |  |  | 5 |
| 9m120_ataka | 9M120 Ataka | weaponFamilies | 2 | atgm_ataka |  | 26 |  |  | 0 |
| 9m133_kornet | 9M133 Kornet | weaponFamilies | 7 | atgm_kornet | 0.7385 | 22 | 0.96 |  | 0 |
| 9m317_buk | 9M317 Buk | weaponFamilies | 3 | buk | 1.2333 | 50 | 4.44 |  | 2 |
| agm_88_harm | AGM-88 HARM | weaponFamilies | 1 |  |  | 45 | 2.09 | 360 | 4 |
| agm_114_hellfire | AGM-114 Hellfire | weaponFamilies | 4 | hellfire_longbow |  | 26 |  | 270 | 0 |
| aim_9_sidewinder | AIM-9 Sidewinder | weaponFamilies | 2 | aim9 |  | 55 |  | 260 | 1.5 |

*15 / 55 dòng đầu: xem sheet 01_vu_khi_dan/Dong_vu_khi.*

### 10j. Họ vũ khí, hành vi đạn và vòng cảnh báo

Trạng thái: Đã áp

Nguồn dữ liệu: 01_vu_khi_dan/Ho_vu_khi; 01_vu_khi_dan/Ho_vu_khi_bien_the; 01_vu_khi_dan/Hanh_vi_dan; 01_vu_khi_dan/Hanh_vi_dan_nhom; 01_vu_khi_dan/Canh_bao_vong. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §10i. Họ vũ khí.

Mỗi vũ khí có `weaponFamilyId` (súng: lớp cỡ nòng; còn lại: vũ khí thật) và `weaponVariantId` khi đạn hay cách bắn khác (có lý do trong bảng). Bậc T0–T5 theo họ. Ở boss, cùng họ là cùng viên đạn (sát thương, lõi, rìa, tốc độ, loại); DPS của từng vũ khí giữ nguyên bằng chu kỳ dài hơn, và lõi rộng hơn 1,25 lần thì chu kỳ dài thêm đúng tỉ lệ đó. Vũ khí người chơi chỉ gắn nhãn (danh sách lệch: Docs/checks/player_weapon_family.md). Kiểm: `Tools/balance/p34_validate.py`.

#### Vũ khí boss theo họ (136)

Sát thương một viên; lõi nhận đủ sát thương, rìa 40%. Hồi: thời gian hồi của vũ khí (loạt và băng giữ nhịp riêng). Cảnh báo: thời gian đạn T4+ không dẫn đường báo chỗ rơi (đạn ở trên không ít nhất bấy lâu).

#### Cảnh báo theo khả năng thoát

Đạn T4+ của boss báo max(sàn, 0,5 s + lõi / 4,5 m/s), tối đa 6 s; sàn T4 2,5 s, 406 mm 3,5 s, siêu vũ khí T5 4 s. Vòng hiển thị là đúng vùng sát thương: vòng ngoài là rìa, vòng trong là lõi (tên lửa hành trình: lõi và rìa của vụ nổ hai lớp). Gungnir giữ 3 s (ngoại lệ có tên: prompt 29 G1).

| Họ | Tên | Bậc | Lõi (boss) | Cảnh báo |
|---|---|---|---|---|
| `atgm_kh_29l` | atgm_kh_29l | T4 | — | 2,5 s |
| `bal_9m723_iskander` | bal_9m723_iskander | T4 | — | 2,5 s |
| `bomb_400` | 400 kg bomb | T4 | 10 m | 2,72 s |
| `bomb_car_bomb` | bomb_car_bomb | T4 | — | 2,5 s |
| `bomb_cbu_97_sensor_fuzed_weapon` | bomb_cbu_97_sensor_fuzed_weapon | T4 | — | 2,5 s |
| `bomb_fab_500` | bomb_fab_500 | T4 | — | 2,5 s |
| `bomb_fab_500_m_62_with_umpk_glide_kit` | bomb_fab_500_m_62_with_umpk_glide_kit | T4 | — | 2,5 s |
| `bomb_gbu_28` | bomb_gbu_28 | T4 | — | 2,5 s |
| `bomb_gbu_31_jdam` | bomb_gbu_31_jdam | T4 | — | 2,5 s |
| `bomb_odab_500` | bomb_odab_500 | T4 | — | 2,5 s |
| `cal_203` | 203 mm | T4 | 8,5 m | 2,5 s |
| `cal_240` | 240 mm | T4 | 10 m | 2,72 s |
| `cruise_3m_54_kalibr` | cruise_3m_54_kalibr | T4 | — | 2,5 s |
| `cruise_agm_158_jassm` | cruise_agm_158_jassm | T4 | — | 2,5 s |
| `cruise_kh_101` | cruise_kh_101 | T4 | — | 2,5 s |
| `cruise_nsm_coastal_defence` | cruise_nsm_coastal_defence | T4 | — | 2,5 s |
| `cruise_typhon_mrc` | cruise_typhon_mrc | T4 | — | 2,5 s |
| `msl_nsm_p_800_oniks` | msl_nsm_p_800_oniks | T4 | — | 2,5 s |
| `rkt_gmlrs_227` | GMLRS 227 mm | T4 | — | 2,5 s |
| `rkt_smerch_300` | Smerch 300 mm rockets | T4 | 8 m | 2,5 s |
| `rkt_tos_220` | TOS-1A 220 mm thermobaric | T4 | — | 2,5 s |
| `cal_406` | 406 mm | T5 | 14 m | 3,61 s |
| `cal_800` | 800 mm super-gun | T5 | — | 4 s |
| `gungnir_emrg` | EMRG electromagnetic railgun (Gungnir) | T5 | — | 4 s |

Sheet: 01_vu_khi_dan/Ho_vu_khi — Họ vũ khí (105 dòng, 11 cột)

| id | ten | bac | boss_sat_thuong | boss_loi_m | boss_ria_m | so_vu_khi | vu_khi |
|---|---|---|---|---|---|---|---|
| atgm_9k121_vikhr | atgm_9k121_vikhr | 2 |  |  |  | 1 | vikhr |
| atgm_9m113_konkurs | atgm_9m113_konkurs | 2 |  |  |  | 1 | atgm_post |
| atgm_9m120_ataka | atgm_9m120_ataka | 2 |  |  |  | 2 | ataka;heli_ataka |
| atgm_9m123_khrizantema | atgm_9m123_khrizantema | 2 |  |  |  | 1 | khrizantema |
| atgm_agm_65_maverick | atgm_agm_65_maverick | 3 |  |  |  | 1 | maverick |
| atgm_agm_114_hellfire | atgm_agm_114_hellfire | 2 |  |  |  | 3 | drone_missile;heli_atgm;uav_loiter_missile |
| atgm_agm_114l_hellfire_longbow | atgm_agm_114l_hellfire_longbow | 2 |  |  |  | 2 | hellfire_standoff;hellfire_volley |
| atgm_agm_176_griffin | atgm_agm_176_griffin | 2 |  |  |  | 1 | griffin |
| atgm_bgm_71_tow_2 | atgm_bgm_71_tow_2 | 2 |  |  |  | 1 | atgm |
| atgm_gun_launched_atgm | atgm_gun_launched_atgm | 2 |  |  |  | 1 | gun_launched_atgm |
| atgm_kh_29l | atgm_kh_29l | 4 |  |  |  | 1 | kh29 |
| atgm_kornet | 9M133 Kornet | 2 | 230 | 0 | 0 | 14 | atgm_heavy;boss_missiles;kornet_multi;kornet_top;kornet_twi… |
| atgm_mam_l | atgm_mam_l | 2 |  |  |  | 1 | recon_missile |
| atgm_spike_nlos | atgm_spike_nlos | 2 |  |  |  | 1 | spike_nlos |
| bal_9m723_iskander | bal_9m723_iskander | 4 |  |  |  | 1 | ballistic_missile |

*15 / 105 dòng đầu: xem sheet 01_vu_khi_dan/Ho_vu_khi.*

Sheet: 01_vu_khi_dan/Ho_vu_khi_bien_the — Họ vũ khí: biến thể (20 dòng, 7 cột)

| id | ho_vu_khi_id | thu_tu | bien_the | ly_do |
|---|---|---|---|---|
| cal_25/flak | cal_25 | 0 | flak | air-burst rounds against aircraft, the family's others are… |
| cal_30/ciws | cal_30 | 0 | ciws | the AK-630 close-in weapon of the ships and hovercraft: a s… |
| cal_30/flak | cal_30 | 1 | flak | the 2A38 / AK-630 air-burst (fragmentation, a 2.5 m burst)… |
| cal_35/ap | cal_35 | 0 | ap | AP rounds (no burst) loaded against ground targets instead… |
| cal_40/flak | cal_40 | 0 | flak | proximity air-burst (3.5 m) against aircraft |
| cal_40/he | cal_40 | 1 | he | the AC-130's 40 mm HE against the ground (a 3 m burst), not… |
| cal_57/ap | cal_57 | 0 | ap | AP rounds (kinetic, no burst) instead of HE |
| cal_57/flak | cal_57 | 1 | flak | air-burst against aircraft |
| cal_100_105_ap/he | cal_100_105_ap | 0 | he | a high-explosive second round of an AP gun |
| cal_100_105_he/flak | cal_100_105_he | 0 | flak | the KS-19's time-fused flak against aircraft |
| cal_120_he/mortar | cal_120_he | 0 | mortar | a lobbed mortar bomb (slow, high arc), not a gun's HE shell |
| cal_127_130/ap | cal_127_130 | 0 | ap | an armour-piercing round fired direct (Leviathan's AK-127 i… |
| cal_152_155/ap | cal_152_155 | 0 | ap | an armour-piercing round fired direct (a tank gun's or a na… |
| cal_152_155/guided | cal_152_155 | 1 | guided | a guided shell (one at a time) |
| cal_152_155/heat | cal_152_155 | 2 | heat | a shaped-charge (HEAT) round |
| cal_152_155/smart | cal_152_155 | 3 | smart | a sensor-fuzed or guided shell with submunitions |
| rkt_70_80/guided | rkt_70_80 | 0 | guided | a laser-guided rocket (APKWS) |
| rkt_gmlrs_227/cluster | rkt_gmlrs_227 | 0 | cluster | the M30's cluster warhead |
| rkt_grad_122/cluster | rkt_grad_122 | 0 | cluster | a cluster warhead (bomblets) |
| rkt_grad_122/thermobaric | rkt_grad_122 | 1 | thermobaric | a thermobaric warhead |

Sheet: 01_vu_khi_dan/Hanh_vi_dan — Hành vi đạn: luật chung (11 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so | gia_tri_chu | don_vi |
|---|---|---|---|---|---|
| flareBurn | munitionRules | flareBurn |  | 3;4 | s |
| flareDecoyChance | munitionRules | flareDecoyChance | 0.35 |  |  |
| flareOffset | munitionRules | flareOffset | 10 |  | m |
| flareRelease.fighter | munitionRules | fighter |  | 4;6 |  |
| flareRelease.helicopter | munitionRules | helicopter |  | 4;8 |  |
| flareRelease.large | munitionRules | large |  | 8;16 |  |
| leadCap | munitionRules | leadCap | 3 |  |  |
| proximityFuze | munitionRules | proximityFuze | 7 |  | m |
| radarGuided | munitionRules | radarGuided |  | sam_aim_120_amraam;sam_r_37m;sam_9m317_buk;sam_mim_104_patr… |  |
| reachScale | munitionRules | reachScale | 1.3 |  |  |
| sightGuided | munitionRules | sightGuided |  | atgm_bgm_71_tow_2;atgm_gun_launched_atgm;atgm_kornet;atgm_9… |  |

Sheet: 01_vu_khi_dan/Hanh_vi_dan_nhom — Hành vi đạn theo nhóm (7 dòng, 12 cột)

| id | so_vu_khi | cach_nham | khi_no | khi_truot | co_canh_bao | thoi_gian_bay_toi_da_s | tuong_tac_phao_sang | tuong_tac_aps | tuong_tac_gay_nhieu |
|---|---|---|---|---|---|---|---|---|---|
| Bomb | 8 | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| Bullet | 116 | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| Drone | 14 | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| Flame | 3 | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| Missile | 58 | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| Rocket | 29 | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |
| Shell | 144 | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK | NEED_CODE_CHECK |

Sheet: 01_vu_khi_dan/Canh_bao_vong — Vòng cảnh báo (12 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so | don_vi |
|---|---|---|---|---|
| base | warningRules | base | 0.5 | s |
| bombMinKg | warningRules | bombMinKg | 400 | kg |
| cap | warningRules | cap | 6 | s |
| escapeSpeed | warningRules | escapeSpeed | 4.5 | m/s |
| fadeIn | warningRules | fadeIn | 0.4 | s |
| floor406 | warningRules | floor406 | 3.5 | s |
| floorT4 | warningRules | floorT4 | 2.5 | s |
| floorT5 | warningRules | floorT5 | 4 | s |
| gunMinMm | warningRules | gunMinMm | 203 | mm |
| maxShown | warningRules | maxShown | 6 |  |
| rocketMinMm | warningRules | rocketMinMm | 300 | mm |
| salvoMergeSeconds | warningRules | salvoMergeSeconds | 0.6 | s |

## 11. Tháp canh, xe tinh nhuệ và boss

Trạng thái: Đã áp

Nguồn dữ liệu: 03_boss/Boss; 03_boss/Boss_vu_khi; 03_boss/Boss_bo_phan; 03_boss/Boss_sieu_vu_khi; 03_boss/Boss_ho_tong; 03_boss/Boss_hang; 04_can_cu_thap/Thap (lời hướng dẫn: 10_model_tai_san/Dia_phuong_hoa guide.<id>). Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §11. Tháp canh.

#### Tháp và công sự

Tháp cố định chặn lưới đường đi khi xuất hiện; trong Chiếm cứ điểm mỗi cứ điểm có tháp trung lập bắn mọi phe và dựng lại sau một thời gian; mỗi phe có sở chỉ huy (HQ) có máu (phá được hay không tùy chế độ, phần 6). Tháp của căn cứ người chơi xếp theo cỡ ô (phần 6), có hạng, nhánh ở hạng 7 và 3 ô đồ.

#### Xe tinh nhuệ

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

#### Boss

Mọi boss có bộ phận theo cùng một bộ luật (phase 9); boss cuối chương còn có thanh máu nhiều pha.

- **Máu bộ phận** là một phần máu thân (đọc trực tiếp, nên tăng theo cấp chiến dịch, độ khó và bản mạnh của nhiệm vụ): mỗi bộ phận 8–15%; boss từ 5 súng trở lên có tổng 50–70%, boss chỉ có 3–4 thứ phá được có tổng 35–47%.
- **Máu thân** giảm còn ×0,76 đến ×0,90 (1,125 / (1 + 0,7 × tổng phần bộ phận)) để trận dài hơn khoảng 12% (ước tính theo mô hình, đo ở phase kiểm tra).
- **Vỡ một bộ phận:** súng trên đó im cả trận; kỹ năng dừng khi mọi bộ phận mang nó đều vỡ; cơ chế dừng (phát bắn của siêu pháo, đào hầm của Giun Đất, đổ quân của tàu đệm khí, hào quang của Tổng Tư Lệnh); áp dụng phạt tốc độ, quay, nhịp bắn, độ tản; thân mất thêm 30% máu của bộ phận đó.
- **Chỉ phát trúng trực tiếp** làm hại bộ phận; nổ lan, lửa và hỏa lực hỗ trợ rơi vào thân. Đạn trúng bộ phận nhô ra ngoài thân (quạt, đầu máy, đầu kéo) nay tính là trúng.
- **Tự sửa:** Tàu Thép và Bastion một lần mỗi trận hồi bộ phận đã vỡ có phát bắn mặt đất nặng nhất lên 50%.
- **Nhắm bắn:** mỗi xe nhắm bộ phận nguy hiểm nhất với nó trong tầm (phòng không nhắm bộ phận bắn máy bay, diệt tăng nhắm bộ phận dày nhất); 2 trên 5 phát vẫn vào thân.
- **Lệnh bắn bộ phận:** chạm vào biểu tượng bộ phận dưới thanh máu boss hoặc chạm thẳng vào bộ phận trên mô hình: mọi xe trong tầm dồn hỏa lực vào đó tới khi vỡ; chạm lại để hủy.
- **Săn trùm** thưởng 2 CP cho mỗi bộ phận vỡ.

##### Lửa và khói ở chỗ vỡ

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

giáp thân trước 4 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 6 bộ phận; pha ở 45%.

**Mẹo:** hai **giàn phóng drone** nuôi bầy drone của nó: phá cả hai là hết phóng. **Cột gây nhiễu** làm tên lửa dẫn đường trong 30 m bay lệch: phá nó bằng pháo trước khi trông vào tên lửa. Nên phá bộ phát EMP trước khi áp sát.

Pháo đài drone của Venn: không có pháo chính, chỉ có các giàn phóng hết bầy này tới bầy khác, một dàn tên lửa phòng không và pháo cao xạ. Cực nguy hiểm với máy bay; xe tăng và pháo binh mới hạ được nó.

giáp thân trước 1 / hông 1 / sau 1 / nóc 1; Tổng 35% máu thân trong 2 bộ phận; pha ở 45%.

**Mẹo: khoang drone** là tất cả những gì nó có.

Một tàu mang drone cỡ nhỏ trong chương trình drone của Venn. Aurel vẫn cho đóng tiếp sau khi bà bỏ đi.

giáp thân trước 1 / hông 1 / sau 1 / nóc 1; Tổng 35% máu thân trong 3 bộ phận; pha ở 45%.

**Mẹo: khoang drone** là vũ khí của nó; phá cả hai thì chỉ còn cao xạ.

Tám drone phản lực nhỏ bay như một, theo kiểu Loyal Wingman; câu trả lời của Matriarch khi mất tàu mẹ.

giáp thân trước 5 / hông 3 / sau 2 / nóc 3; Tổng 35% máu thân trong 9 bộ phận; tự sửa một bộ phận một lần mỗi trận; pha ở 60%, 25%.

**Mẹo:** mỗi **tháp pháo tự động** chỉ phủ một góc: phá các tháp ở một phía rồi đánh từ phía đó. Khi tự vá nó ưu tiên khẩu cối.

Pháo đài biết đi đầu tiên của Hegemon: bốn tháp pháo tự động, một khẩu cối hạng nặng và kíp lái biết tự vá giáp dưới làn đạn. Chiếc ở Ashfield là mẫu đời đầu, chậm hơn và mỏng hơn những chiếc về sau.

giáp thân trước 3 / hông 2 / sau 1 / nóc 1; Tổng 35% máu thân trong 8 bộ phận; pha ở 45%.

**Mẹo:** phá **cửa đổ bộ** là nó hết đổ quân; mỗi **quạt đẩy** bị phá làm nó chậm 30%. Hai **pháo phòng thủ tầm gần** bắn hạ tên lửa và rốc-két: phá chúng trước khi tấn công bằng tên lửa.

Tàu đệm khí đổ bộ của Hegemon, chở cả một đại đội thiết giáp lên bãi biển với tốc độ sáu mươi hải lý và tự yểm trợ cuộc đổ bộ bằng pháo của mình. Phải đánh nó trước khi nó kịp dỡ quân.

giáp thân trước 4 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 4 bộ phận; pha ở 45%.

**Mẹo: pháo chính** là đòn mạnh nhất; **hệ thống bảo vệ** bắn hạ hai tên lửa mỗi loạt.

Chiếc Behemoth của Varga dựng lại sau lần bại trận đầu tiên: nặng hơn, lắp hệ sưởi cho mùa đông, và hung hãn hơn.

giáp thân trước 3 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 4 bộ phận; pha ở 45%.

**Mẹo:** cao xạ đuổi máy bay; **pháo chính** là vũ khí mạnh nhất.

Đoàn xe tải quân sự nối rơ-moóc, mỗi xe mang một vũ khí: toán lính hoang mạc trên đường.

giáp thân trước 5 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 10 bộ phận; pha ở 60%, 25%.

**Mẹo:** cho xe tăng dồn bắn **pháo chính**: mất cặp nòng đó nó chỉ còn là khối thép chậm chạp với cao xạ và tên lửa. **Hệ thống bảo vệ chủ động** bắn hạ hai tên lửa chống tăng mỗi lượt: phá nó, hoặc dùng pháo. Phòng không nên phá cao xạ trước nếu máy bay ta ở gần.

Chiến hạm mặt đất của Varga: pháo chính mỗi phát hạ một xe tăng, đội hộ tống bám theo vào trận và lớp vỏ chịu được gần hết hỏa lực của lữ đoàn. Mara nói các tấm giáp phía sau là điểm yếu của nó.

giáp thân trước 4 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 3 bộ phận; pha ở 45%.

**Mẹo:** phá **ăng-ten chỉ huy** trước tiên: quân của nó mất ngay hào quang chỉ huy.

Xe chỉ huy riêng của Aurel, Atlas: lớp giáp nặng nhất Hegemon từng đúc, bao quanh hệ thống liên lạc điều hành toàn bộ bãi phóng.

giáp thân trước 4 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 4 bộ phận; pha ở 45%.

**Mẹo:** đánh vào **mũi khoan** trong vài giây ngay sau khi nó trồi lên: vỡ rồi là nó không bao giờ chui xuống đất được nữa.

Cỗ máy khoan cũ của Varga, Tartarus: nó nghiến xuyên dưới tường thành và thân đập rồi trồi lên đúng chỗ không ai canh. Phải tiêu diệt nó trước khi nó tới trạm phát điện.

giáp thân trước 4 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 8 bộ phận; pha ở 45%.

**Mẹo:** phá **tháp pháo trên thùng** là mất pháo 125 mm; phá một **lốp trước** thì cú lao lệch và dừng; **lốp sau** giáp cấp 1; phá **ca-bin** là súng máy ngừng bắn.

Xe tải mỏ bọc thép của Thorne ở Deepcut Mine: một chiếc BelAZ-75710 hàn tháp pháo xe tăng lên thùng, lưỡi húc ở mũi và súng máy trên nóc ca-bin.

giáp thân trước 5 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 9 bộ phận; pha ở 60%, 25%.

**Mẹo:** phá **lựu pháo** để chấm dứt các loạt pháo dồn, và phá bộ phát EMP trước khi thiết giáp ta áp sát.

Mỏ neo của tuyến Frostpeak: một pháo đài di động với lựu pháo, đội hộ tống và xung EMP làm tê liệt mọi thứ xung quanh.

giáp thân trước 2 / hông 2 / sau 2 / nóc 1; Tổng 35% máu thân trong 4 bộ phận; pha ở 45%.

**Mẹo:** phá **bệ tên lửa** trên lưng để chặn tên lửa của nó; phá **cụm động cơ** ở mũi để các lượt lao chậm lại.

Một con tàu bay sát mặt sóng với tốc độ của máy bay và đổ quân lên bất cứ bãi biển nào.

giáp thân trước 4 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 4 bộ phận; pha ở 45%.

**Mẹo: cửa ống phóng** mang tên lửa của nó; pháo boong chỉ bắn khi nổi.

Tàu ngầm mang drone theo khái niệm: nhỏ hơn Typhon, nhanh hơn, và im lặng cho tới khi nắp ống mở.

giáp thân trước 1 / hông 1 / sau 1 / nóc 1; Tổng 35% máu thân trong 4 bộ phận; pha ở 45%.

**Mẹo:** phá cả hai **khoang tên lửa** là hết tên lửa; phá **động cơ** thì nó chậm lại.

Chiếc tiêm kích riêng của Wolff, làm cho một mình hắn: nhanh, khó thấy trên radar, mang tên lửa không đối không và bom dẫn đường.

giáp thân trước 2 / hông 2 / sau 2 / nóc 2; Tổng 35% máu thân trong 8 bộ phận; pha ở 45%.

**Mẹo:** mỗi **động cơ** bị phá làm vòng bay chậm 15%: bay chậm hơn là phòng không ta có thêm thời gian. Khẩu 105 mm là thứ giết xe tăng.

Pháo hạm bay vòng trên cao quanh con mồi với khẩu 105 mm và hai khẩu 40 mm dọc sườn. Nó không bao giờ hạ thấp. Hoặc phòng không và tiêm kích, hoặc chẳng gì cả.

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

giáp thân trước 5 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 10 bộ phận; pha ở 60%, 25%.

**Mẹo:** mỗi **cụm xích** (giáp cấp 2) bị phá là nó chậm lại; **cần gầu** mang đòn quét; **bánh gầu** (giáp cấp 4) là thứ nghiền.

Một máy xúc bánh gầu to bằng cả tòa nhà, được Thorne bọc thép và chĩa thẳng vào lữ đoàn.

giáp thân trước 5 / hông 3 / sau 2 / nóc 3; Tổng 35% máu thân trong 9 bộ phận; tự sửa một bộ phận một lần mỗi trận; pha ở 60%, 25%.

**Mẹo: khẩu cối** là nòng dài có máu riêng; phá nó là hết quả đạn 800 mm. Bốn tháp pháo chỉ để tự vệ.

Một khẩu pháo cỡ 2B1 Oka thay Gungnir làm mối đe dọa lớn của quân đội: chậm, to và tự tin.

giáp thân trước 5 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 7 bộ phận; pha ở 60%, 25%.

**Mẹo: cửa ống phóng** mang tên lửa (lộ trên mặt nước lúc cảnh báo); **tháp chỉ huy** ngắm tên lửa phòng không; **sô-na** là hệ điều khiển hỏa lực.

Tàu ngầm tên lửa của Kessler, giờ trong tay Thorne: nổi lên, phóng một loạt rồi lại lặn.

giáp thân trước 5 / hông 3 / sau 2 / nóc 2; Tổng 35% máu thân trong 14 bộ phận; pha ở 60%, 25%.

**Mẹo: boong cất cánh** nuôi máy bay và mang đòn không kích; phá nó trước. **CIWS** bắn hạ tên lửa trước khi chúng trúng.

Soái hạm của hạm đội mới của Kessler: tàu sân bay đánh bằng máy bay, không bằng pháo.

giáp thân trước 2 / hông 2 / sau 2 / nóc 2; Tổng 35% máu thân trong 10 bộ phận; thân không nhận sát thương tới khi vỡ động cơ ×2; pha ở 60%, 25%.

**Mẹo:** phá hai **động cơ** để mở thân; sau đó tới các nhà chứa drone và radar ngắm cao xạ.

Sở chỉ huy bay của Wolff trên Skyhold: radar, tên lửa và một khoang chứa drone. Nó điều khiển mọi máy bay Hegemon trên Meridian Coast.

giáp thân trước 2 / hông 2 / sau 2 / nóc 2; Tổng 35% máu thân trong 10 bộ phận; thân không nhận sát thương tới khi vỡ động cơ ×2; pha ở 60%, 25%.

**Mẹo:** phá khoang bom là hết thảm bom; phá động cơ thì nó chậm lại.

Người kế nhiệm máy bay ném bom của Wolff: một cánh bay to bằng nhà chứa máy bay, có tiêm kích hộ tống.

giáp thân trước 3 / hông 2 / sau 1 / nóc 1; Tổng 35% máu thân trong 8 bộ phận; pha ở 45%.

**Mẹo:** phá **trạm chỉ thị mục tiêu** là đạn rơi lệch; mỗi **đầu máy kéo** bị phá làm nó bắn thưa hơn; phá **pháo chính** là nó hết bắn.

Một khẩu pháo điện từ trên đoàn tàu: toa pháo ray điện từ, các toa tụ điện và đầu máy diesel hiện đại. Kessler dùng nó bắn một phát xuyên cả đội hình từ cách bốn mươi cây số.

giáp thân trước 3 / hông 3 / sau 3 / nóc 3; Tổng 35% máu thân trong 8 bộ phận.

**Mẹo:** phá **cửa thả khoang** (mỗi cửa mất là thả chậm hơn; mất một cửa thì đòn đổ bộ lớn chỉ còn ba khoang) và **tháp la-de phòng thủ** trước khi dùng tên lửa.

Con tàu đưa quân của Aurel từ quỹ đạo xuống Skygate Array, từng khoang một.

giáp thân trước 4 / hông 4 / sau 4 / nóc 4; Tổng 35% máu thân trong 12 bộ phận.

**Mẹo:** phá **động cơ đẩy chính** để nhốt nó ở tầng thấp, và phá **ăng-ten liên kết vệ tinh** để chặn thanh vonfram; nên dọn hai **tháp la-de phòng thủ điểm** trước khi trông vào tên lửa.

Chiến hạm quỹ đạo của Aurel: thân tàu hình mũi dao, thượng tầng bậc thang dưới tháp chỉ huy và cả một dãy động cơ ở đuôi, được chế tạo để tấn công từ quỹ đạo và đưa Aurel ra ngoài tầm với của mọi người. Chiếc đầu tiên xuất hiện sẽ bỏ chạy khi bị thương đủ nặng. Chiếc trên bệ phóng đã hoàn chỉnh.

giáp thân trước 4 / hông 4 / sau 4 / nóc 4; Tổng 35% máu thân trong 9 bộ phận.

**Mẹo:** tia **la-de chính** mang đòn tia mặt trời; phá nó là hết tia. **Tháp la-de phòng thủ** bắn hạ tên lửa của bạn.

Một trong những chấm sáng cuối cùng còn trên quỹ đạo sau phần kết: trạm gương kiểu Znamya.

Sheet: 03_boss/Boss — Boss (41 dòng, 329 cột)

| id | phan_loai | ten_en | ten_vi | ten_ngan_vi | base_cp | mau_hp | mau_trong_tran_hp | giap_hong | giap_noc |
|---|---|---|---|---|---|---|---|---|---|
| argus | mini | Argus · Scout Airship | Argus · Khí cầu trinh sát | Argus | 0 | 94850 | 80622.5 | 2 | 2 |
| armored_train | mini | Juggernaut · Armoured Train | Juggernaut · Đoàn tàu bọc thép | Juggernaut | 0 | 37750 | 32087.5 | 3 | 2 |
| bastion_mk0 | mini | Bastion Mk.0 · Prototype Fortress | Bastion Mk.0 · Pháo đài nguyên mẫu | Bastion Mk.0 | 0 | 19250 | 16362.5 | 4 | 3 |
| behemoth | main | Behemoth · Steel Monster | Behemoth · Quái vật thép | Behemoth | 0 | 33550 | 28517.5 | 3 | 2 |
| behemoth_inferno | mini | Inferno · Flame Behemoth | Inferno · Behemoth phun lửa | Inferno | 0 | 24600 | 20910.0 | 3 | 2 |
| behemoth_mk0 | mini | Behemoth Mk.0 · Prototype Behemoth | Behemoth Mk.0 · Behemoth nguyên mẫu | Behemoth Mk.0 | 0 | 33900 | 28815.0 | 3 | 1 |
| behemoth_mk2 | mini | Behemoth Mk.II · Upgraded Behemoth | Behemoth Mk.II · Behemoth nâng cấp | Behemoth Mk.II | 0 | 53500 | 45475.0 | 3 | 2 |
| behemoth_tempest | mini | Tempest · Railgun Behemoth | Tempest · Behemoth pháo điện từ | Tempest | 0 | 37750 | 32087.5 | 3 | 2 |
| caspian | mini | Caspian · Ekranoplan | Caspian · Tàu bay sát mặt nước | Caspian | 0 | 81300 | 69105.0 | 2 | 1 |
| cerberus | mini | Cerberus · Three-Car Convoy | Cerberus · Đoàn xe ba khung | Cerberus | 0 | 53500 | 45475.0 | 3 | 2 |
| command_airship | main | Roc · Flying Headquarters | Roc · Khí cầu chỉ huy | Roc | 0 | 137250 | 116662.5 | 2 | 2 |
| daedalus | main | Daedalus · Orbital Lander | Daedalus · Tàu đổ bộ quỹ đạo | Daedalus | 0 | 156900 | 133365.0 | 2 | 1 |
| drone_mothership | main | Matriarch · Drone Mothership | Matriarch · Tàu mẹ drone | Matriarch | 0 | 63100 | 53635.0 | 2 | 2 |
| earth_borer | mini | Tartarus · Tunnelling Machine | Tartarus · Máy khoan | Tartarus | 0 | 72000 | 61200.0 | 3 | 2 |
| fenrir | mini | Fenrir · Vanguard | Fenrir · Xe tiên phong | Fenrir | 0 | 29950 | 25457.5 | 4 | 2 |

*15 / 41 dòng đầu: xem sheet 03_boss/Boss; in 10 / 329 cột; 163 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 03_boss/Boss_vu_khi — Boss: vũ khí theo bệ (223 dòng, 22 cột)

| id | boss_id | chi_so_be | vu_khi | slot | aim | bo_phan | so_nong | sat_thuong_moi_phat | thoi_gian_nap_s |
|---|---|---|---|---|---|---|---|---|---|
| argus/0 | argus | 0 | p26_roc_main_roc_bombs | gun | Free |  | 1 | 700 | 33.34 |
| argus/1 | argus | 1 | p26_roc_main_roc_bombs | gun | Free |  | 1 | 700 | 33.34 |
| armored_train/0 | armored_train | 0 | train_gun | main |  | gun_car_front | 1 | 600 | 8 |
| armored_train/1 | armored_train | 1 | boss_rockets | rocket | Free | rocket_car | 1 | 200 | 2.44 |
| armored_train/2 | armored_train | 2 | boss_hmg | mg | Free |  | 1 | 15 | 0.0833 |
| armored_train/3 | armored_train | 3 | boss_flak | mg | Free | flak_car | 1 | 25 | 0.05 |
| armored_train/4 | armored_train | 4 | train_gun | main | Free | gun_car_rear | 1 | 600 | 8 |
| armored_train/5 | armored_train | 5 | boss_flak | mg | Free |  | 1 | 25 | 0.05 |
| bastion_mk0/0 | bastion_mk0 | 0 | p26_bastion_sec_b240 | main |  | mortar | 1 | 1100 | 60 |
| bastion_mk0/1 | bastion_mk0 | 1 | p26_bastion_direct_b100 | gun | Free | turret_fl | 2 | 240 | 8.6 |
| bastion_mk0/2 | bastion_mk0 | 2 | p26_bastion_direct_b100 | gun | Free | turret_fr | 2 | 240 | 8.6 |
| behemoth/0 | behemoth | 0 | p26_behemoth_main_be152 | main |  | main_gun | 2 | 600 | 8.98 |
| behemoth/1 | behemoth | 1 | p26_behemoth_tiny_be120 | gun | Free | gun_120 | 1 | 260 | 7.5 |
| behemoth/2 | behemoth | 2 | p26_behemoth_close_boss_flak | mg | Free | flak_r | 1 | 25 | 0.05 |
| behemoth/3 | behemoth | 3 | p26_behemoth_close_boss_flak | mg | Free | flak_l | 1 | 25 | 0.05 |

*15 / 223 dòng đầu: xem sheet 03_boss/Boss_vu_khi; in 10 / 22 cột; 8 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 03_boss/Boss_bo_phan — Boss: bộ phận (198 dòng, 29 cột)

| id | boss_id | thu_tu | use | armour | at_x_m | at_y_m | at_z_m | hp | id_goc |
|---|---|---|---|---|---|---|---|---|---|
| armored_train/flak_car | armored_train | 4 |  | 2 | 0 | -6.35 | 3.2 | 0.1 | flak_car |
| armored_train/gun_car_front | armored_train | 1 |  | 3 | 0 | -3.2 | 3.7 | 0.12 | gun_car_front |
| armored_train/gun_car_rear | armored_train | 2 |  | 3 | 0 | 2.0 | 3.0 | 0.12 | gun_car_rear |
| armored_train/locomotive | armored_train | 0 |  | 4 | 0 | 7.5 | 2.5 | 0.12 | locomotive |
| armored_train/mortar_car | armored_train | 5 |  | 2 | 0 | -12.5 | 2.6 | 0.1 | mortar_car |
| armored_train/rocket_car | armored_train | 3 |  | 2 | 0 | -8.3 | 3.0 | 0.1 | rocket_car |
| behemoth/aps | behemoth | 6 |  | 1 | 0 | 0.6 | 5.2 | 0.07 | aps |
| behemoth/flak_l | behemoth | 3 |  | 2 | -0.9 | -1.15 | 4.8 | 0.07 | flak_l |
| behemoth/flak_r | behemoth | 2 |  | 2 | 0.9 | -1.15 | 4.8 | 0.07 | flak_r |
| behemoth/gun_120 | behemoth | 1 |  | 3 | 0 | 3.45 | 2.8 | 0.07 | gun_120 |
| behemoth/main_gun | behemoth | 0 |  | 3 | 0 | 3.5 | 4.1 | 0.07 | main_gun |
| behemoth/missiles_l | behemoth | 5 |  | 2 | -2.6 | -2.5 | 2.3 | 0.07 | missiles_l |
| behemoth/missiles_r | behemoth | 4 |  | 2 | 2.6 | -2.5 | 2.3 | 0.07 | missiles_r |
| behemoth/rocket_pod | behemoth | 9 | rocket_pod |  | 0 | -3.8 | 4.4 |  | rocket_pod |
| behemoth/side_gun_l | behemoth | 7 | side_gun_120 |  | -3.4 | 1.0 | 2.6 |  | side_gun_l |

*15 / 198 dòng đầu: xem sheet 03_boss/Boss_bo_phan; in 10 / 29 cột; 8 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 03_boss/Boss_sieu_vu_khi — Siêu vũ khí (17 dòng, 18 cột)

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
| garuda_carpet | garuda | group | 50 |  |  |  |  | bomb |  |
| hyperion_sun_beam | hyperion | group | 50 |  |  |  |  | ballistic |  |
| ixion_crush_charge | ixion | group | 10 |  | 6 |  |  | barrage |  |
| kraken_air_raid | kraken | group | 50 |  |  |  |  | bomb |  |
| kronos_bucket_sweep | kronos | self | 45 |  |  |  |  | dune |  |
| leviathan_volley | leviathan | base | 50 |  |  |  | cruise | artillery |  |
| moloch_factory_dump | moloch | group | 50 |  |  |  |  | reinforce |  |
| monster_800_shell | monster | group | 50 |  |  |  |  | mortar |  |
| typhon_underwater_launch | typhon | base | 50 |  |  |  | cruise | missile |  |

*in 10 / 18 cột; 6 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 03_boss/Boss_ho_tong — Hộ tống boss (17 dòng, 9 cột)

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
| fortress_hive | fortress_hive |  |  |  |  |  |
| landing_hovercraft | landing_hovercraft |  |  |  |  |  |
| mega_gunship | mega_gunship |  |  |  |  |  |
| mobile_fortress | mobile_fortress |  |  |  |  |  |
| nuke_train | nuke_train |  |  |  |  |  |
| rail_supergun | rail_supergun |  |  |  |  |  |
| silver_bug | silver_bug | 0.6;0.25 |  |  |  |  |
| sky_fortress | sky_fortress |  |  |  |  |  |
| supreme_command | supreme_command | 0.6 |  |  |  |  |

Sheet: 03_boss/Boss_hang — Hạng boss (42 dòng, 8 cột)

| id | nhom | khoa | gia_tri_so | gia_tri_chu | don_vi |
|---|---|---|---|---|---|
| main.airDamage | bossRanks | airDamage | 1.6 |  |  |
| main.bigAttackScale.cooldown | bossRanks | cooldown | 0.85 |  | s |
| main.bigAttackScale.damage | bossRanks | damage | 0.857 |  |  |
| main.bigAttackScale.warn | bossRanks | warn | 0 |  | s |
| main.damageScale | bossRanks | damageScale | 1.4 |  |  |
| main.fireRate | bossRanks | fireRate | 1.25 |  |  |
| main.intro | bossRanks | intro | 6 |  | s |
| main.music | bossRanks | music |  | boss |  |
| main.partsShare | bossRanks | partsShare | 0.35 |  |  |
| main.phases[0].at | bossRanks | at | 0.6 |  |  |
| main.phases[0].damage | bossRanks | damage | 1.1 |  |  |
| main.phases[0].transform | bossRanks | transform | 2.5 |  |  |
| main.phases[1].at | bossRanks | at | 0.25 |  |  |
| main.phases[1].damage | bossRanks | damage | 1.2 |  |  |
| main.phases[1].fireRate | bossRanks | fireRate | 1.25 |  |  |

*15 / 42 dòng đầu: xem sheet 03_boss/Boss_hang.*

#### Lời hướng dẫn trong game theo đơn vị (04_can_cu_thap/Thap; chuỗi guide.<id> của GuideText.cs)

- **Pháo PK 40 mm** (`aa_gun_tower`): Cách đánh: bốn phát ngòi cận đích mỗi giây, tầm 48 m, bắn cả máy bay lẫn xe nhẹ. · Mạnh / yếu: thắng trực thăng, drone và xe nhẹ; xe tăng gần như miễn nhiễm. · Mẹo: khẩu ở giữa, giữa cao xạ bắn nhanh và cao xạ hạng nặng.
- **Tháp PK** (`aa_turret`): Cách đánh: pháo đôi 30 mm cao xạ tới 42 m và tên lửa phòng không (44 m); cũng bắn mặt đất nhưng chẳng mấy tác dụng. · Mạnh / yếu: xé nát trực thăng và máy bay; lực lượng mặt đất phá nó dễ dàng. · Mẹo: dọn nó bằng xe tăng hoặc pháo binh trước khi máy bay ta bay vào.
- **Trận địa pháo** (`artillery_emplacement`): Cách đánh: lựu pháo nã vào mục tiêu mặt đất cách 25–90 m mỗi khi phe thủ nhìn thấy; không có gì tự vệ ở gần. · Mạnh / yếu: gây đau cho mọi thứ dừng lại trong tầm; không bắn được gần hơn 25 m, và khá mỏng manh. · Mẹo: dùng xe nhanh lao vào: trong vòng 25 m pháo của nó chịu thua. Diệt tai mắt của nó trước.
- **Ụ chống tăng** (`at_gun_emplacement`): Cách đánh: 5 giây một phát xuyên giáp, tầm 38 m, chỉ trong 45° hai bên phía trước; pháo xoay chậm. · Mạnh / yếu: chặn xe tăng lao thẳng tới; pháo binh và xe vòng sườn diệt được nó. · Mẹo: quay mặt nó về con đường thiết giáp địch đi.
- **Tháp ATGM** (`atgm_tower`): Cách đánh: bệ phóng Kornet đôi bắn tên lửa chống tăng theo cặp xa tới 50 m. · Mạnh / yếu: chặn xe tăng và giáp dày từ xa; APS và xe la-de phòng không bắn hạ được tên lửa của nó, pháo binh bắn xa hơn nó. · Mẹo: nã pháo từ ngoài 50 m, hoặc cho tăng có APS hay xe la-de phòng không đi cùng đợt tấn công.
- **Khí cầu radar** (`barrage_balloon`): Cách đánh: bom địch ném trong 40 m quanh nó tản mát thêm 50%; trực thăng địch tránh vùng; nó còn làm lộ máy bay trong 45 m, cả máy bay tàng hình. · Mạnh / yếu: phá các lượt ném bom vào căn cứ; bom dẫn đường không bị ảnh hưởng. · Mẹo: đặt trên những tháp cần giữ nhất.
- **Tường chắn đạn** (`blast_wall`): Cách đánh: không súng, không chặn đường; tháp trong 10 m sau nó nhận ít hơn 30% sát thương bắn thẳng. · Mạnh / yếu: giữ tháp tuyến đầu trước xe tăng; đạn cầu vồng và bom vẫn vượt qua. · Mẹo: đặt trước tháp mạnh nhất.
- **Hầm ngầm** (`bunker_shelter_tower`): Xe phe ta gần đó nhận ít hơn một nửa sát thương từ pháo, cối, bom, không kích.
- **C-RAM** (`c_ram`): Cách đánh: bắn hạ rốc-két, tên lửa, drone và khoảng một phần ba đạn pháo nhắm vào trong 35 m, hai quả đánh chặn cùng lúc; pháo nhiều nòng 20 mm chỉ bắn đạn bay tới, không bắn máy bay. · Mạnh / yếu: che căn cứ khỏi pháo binh, rốc-két và drone; không có gì đánh xe mặt đất. · Mẹo: đặt nơi pháo địch sẽ gây hại nhất, giữa các tháp của ta. Ở hạng 7, Vòm Sắt đổi súng nhiều nòng lấy tên lửa đánh chặn (60 m, sáu quả một lượt, không chặn đạn bắn thẳng); Centurion giữ vai trò che chắn tầm gần bắn nhanh.
- **Trạm CP** (`cp_relay`): Cách đánh: không có súng; +0,1 CP mỗi giây cho phe mình, trạm thứ hai +0,06, trạm thứ ba không thêm gì; bị bắn thì ngừng trả 5 giây. · Mạnh / yếu: thêm CP cho căn cứ yên ổn; chiếm một ô phòng thủ nhỏ, và quân địch tấn công căn cứ sẽ nhắm nó trước. · Mẹo: tối đa hai trạm mỗi căn cứ, không đặt ở tiền đồn; cân nhắc với tòa tháp mà nó thay chỗ.
- **Răng rồng** (`dragons_teeth`): Cách đánh: các hàng khối bê tông không xe nào đi qua được; không đánh gì và bị bắn sau cùng. · Mạnh / yếu: biến lối vào thành đường vòng dưới họng súng của ta; công binh phá nhanh gấp ba. · Mẹo: bịt lỗ hổng địch sẽ đi qua; nhánh rào thép gai thì làm chậm thay vì chặn.
- **Nhà chứa drone** (`drone_hangar`): Cách đánh: cứ 20 giây phóng hai drone FPV cảm tử vào địch xa tới 70 m, mạnh lên giáp và công trình. · Mạnh / yếu: bào mòn thứ gì đứng ngoài tầm các tháp khác; APS, la-de và máy gây nhiễu chặn được drone. · Mẹo: nhánh Lancet bắn tới 85 m và săn pháo binh; nhánh Bầy đàn phóng bốn chiếc một lần.
- **Lưới drone** (`drone_net_tower`): Drone bay qua bị hạ; xe đi qua bình thường.
- **Tháp EW** (`ew_tower`): Cách đánh: tên lửa điều khiển, drone và hỏa lực yểm trợ nhắm vào trong vòng 30 m quanh nó bị lệch; không có súng. · Mạnh / yếu: làm cùn tên lửa chống tăng, Lancet và các đòn không kích vào căn cứ; thứ gì chỉ cần lái tới bắn là hạ được nó. · Mẹo: đặt cạnh các tháp mà tên lửa địch hay nhắm; nhánh: máy gây nhiễu drone 45 m, hoặc máy đánh lừa radar tìm pháo.
- **Tháp pháo sáng** (`flare_searchlight_tower`): Mỗi 15 giây ban đêm, một quả pháo sáng trên đầu địch gần nhất.
- **Tháp pháo sáng** (`flare_tower`): Cách đánh: ban đêm và trong sương mù, 15 giây một quả pháo sáng trên địch gần nhất trong 40 m, làm lộ mọi thứ trong 30 m. · Mạnh / yếu: tìm quân đột kích đêm, cả tàng hình; ban ngày vô dụng. · Mẹo: đi cặp với đèn pha ở map đêm.
- **Tháp canh** (`guard_tower`): Cách đánh: súng máy nặng (30 m, bắn cả máy bay); tầm nhìn 60 m giúp soi quân ta cho pháo địch. · Mạnh / yếu: chặn trinh sát và xe nhẹ; là tháp yếu nhất, gục nhanh trước xe tăng và đạn nổ mạnh. · Mẹo: hạ nó sớm bằng xe tăng hoặc pháo binh để địch mất tai mắt.
- **Tháp pháo** (`gun_turret`): Cách đánh: pháo 120 mm xuyên giáp của tăng chủ lực đặt trên bệ cố định. · Mạnh / yếu: thắng xe tăng và xe nhẹ lọt vào tầm 32 m; bị xe diệt tăng và pháo binh bắn xa hơn. · Mẹo: đứng ngoài 32 m, để xe diệt tăng (40 m) hoặc pháo binh phá nó.
- **Cao xạ nặng** (`heavy_flak_tower`): Cách đánh: 2 giây một phát lớn, nổ trên không rộng 6 m, tầm 70 m; hạ nòng bắn xe tăng trong 50 m. · Mạnh / yếu: bẻ gãy oanh tạc cơ và tốp máy bay dày; quá chậm với tiêm kích lẻ và drone. · Mẹo: đặt cạnh pháo phòng không bắn nhanh để lo trực thăng.
- **Pháo hạng nặng** (`heavy_turret`): Cách đánh: tháp pháo đôi 155 mm xoay chậm, bắn loạt đôi đạn nổ mạnh tới 50 m. · Mạnh / yếu: phá nát xe nhẹ, cụm quân và xe tăng trong góc bắn; là công trình nên ăn 1,5× sát thương nổ mạnh, sợ ít đạn súng máy. · Mẹo: pháo cối công thành, lựu pháo và pháo phản lực bắn xa hơn nó; tháp xoay chậm nên hãy đánh từ hai hướng.
- **Mồi nhử** (`inflatable_decoy`): Cách đánh: trông như tháp pháo; địch bắn vào nó cho tới khi trinh sát, radar, drone hoặc UAV quét lật tẩy. · Mạnh / yếu: làm địch phí đạn pháo và tên lửa; gần như không có máu. · Mẹo: đặt nơi loạt pháo đầu tiên sẽ rơi.
- **Trạm laser** (`laser_ad_station`): Cách đánh: laser chỉ bắn drone, tầm 40 m, cùng bộ đánh chặn rốc-két và đạn cối; khói làm tia yếu 80%. · Mạnh / yếu: dập bầy drone và mưa rốc-két; vô dụng trước máy bay và xe tăng. · Mẹo: giữ khói của ta tránh xa nó.
- **Tổ vác vai** (`manpads_tower`): Tên lửa Stinger tầm ngắn, chỉ bắn máy bay và trực thăng.
- **Lô cốt** (`mg_bunker`): Cách đánh: súng máy nặng bắn nhanh (32 m, bắn cả máy bay). · Mạnh / yếu: quét sạch trinh sát và xe nhẹ; gần như không làm xước xe tăng. · Mẹo: đưa xe tăng vào, đừng dùng xe nhẹ; tăng phun lửa hoặc pháo binh phá nó rất nhanh.
- **Bãi mìn** (`minefield`): Cách đánh: tám quả mìn chống tăng trong vòng 5 m, rải lại mỗi 45 giây; bãi mìn không phải mục tiêu. · Mạnh / yếu: trừng phạt xe lao vào ồ ạt; trinh sát, công binh và UAV quét thấy mìn, công binh gỡ được. · Mẹo: đặt trên đường vào căn cứ, sau các họng súng buộc địch phải chậm lại.
- **Trạm PK tầm xa** (`missile_battery`): Cách đánh: radar nhìn xa 85 m, phóng tên lửa từng cặp vào máy bay cách tới 62 m; không có gì để đánh mặt đất. · Mạnh / yếu: bắn xa hơn gần như mọi máy bay; nhưng bất kỳ lực lượng mặt đất nào cũng áp sát và phá được nó. · Mẹo: dùng xe tăng hoặc pháo binh diệt nó trước; máy bay tránh xa cho tới khi nó bị hạ.
- **TL một lần** (`one_shot_atgm_tower`): Tám tên lửa Kornet chặn đợt tấn công lớn, rồi hết đạn.
- **Súng không giật** (`recoilless_gun_tower`): Yếu hơn ụ pháo chống tăng nhưng rẻ hơn.
- **Dàn rốc-két** (`rocket_turret`): Cách đánh: phóng loạt sáu rốc-két theo đường cầu vồng vào mục tiêu mặt đất cách 8–55 m, vượt qua tường và vật che (từ sân trong vào quân địch đã áp sát tường). · Mạnh / yếu: trừng phạt cụm xe nhẹ và pháo binh; xe tăng chịu rốc-két khá tốt, đạn nổ mạnh phá nó nhanh. · Mẹo: dàn quân khi tiến vào và dùng xe tăng lao tới: trong vòng 8 m nó không bắn được gì.
- **Đèn pha** (`searchlight`): Cách đánh: ban đêm và trong sương mù, phe ta thấy mọi thứ trong 35 m quanh nó; địch trong vùng bắn kém 20%. · Mạnh / yếu: biến trận đêm thành bất lợi cho kẻ tấn công; ban ngày vô dụng. · Mẹo: mang theo cho trận đêm và sương mù.
- **Máy phát khiên** (`shield_tower`): Cách đánh: không có súng; vòm khiên 25 m hấp thụ 3.000 sát thương từ đạn pháo, bom, đạn súng và tên lửa cho mọi thứ phe ta bên dưới, rồi vỡ; hồi lại 30 giây sau đòn cuối. · Mạnh / yếu: giữ các tháp quanh nó đứng vững qua trận pháo kích; vũ khí năng lượng xuyên qua, nhiều vòm không cộng dồn, và máy phát là mục tiêu đầu tiên của địch. · Mẹo: đặt giữa những tháp mạnh nhất; nhánh hạng 7 cho vòm nhỏ mà bền hơn, hoặc hồi lại nhanh hơn.
- **Tháp căn cứ** (`spawn_bastion`): Cách đánh: đứng yên; pháo nặng hai nòng bắn loạt đôi tới 40 m. · Mạnh / yếu: cực lì, giáp dày như xe tăng chứ không phải giáp công trình nên đạn xuyên giáp hiệu quả nhất; thắng xe nhẹ và xe tăng. · Mẹo: đừng đánh trực diện; dùng pháo binh, pháo nặng từ ngoài 40 m, hoặc máy bay để bào dần.
- **Siêu pháo** (`super_gun`): Cách đánh: theo đồng hồ đếm ngược ở đầu màn hình, nó bắn một quả đạn cực lớn vào chỗ quân tấn công đông nhất (vào trại nếu không ai ở ngoài), 4 giây sau khi vòng cảnh báo hiện ra. · Mạnh / yếu: một phát xóa sổ cả đoàn xe nhẹ; nó không có súng bắn gần. · Mẹo: tản quân khi đồng hồ sắp hết; phá được nó là nhiệm vụ phụ, thưởng CP ngay và xu cuối trận.
- **Hầm che quân** (`troop_shelter`): Cách đánh: xe ta trong 15 m nhận một nửa sát thương pháo, cối, bom và không kích; không che đạn bắn thẳng. · Mạnh / yếu: giữ quân phòng thủ sống qua trận pháo kích; vô dụng trước xe tăng. · Mẹo: kéo quân phòng thủ về quanh nó khi đạn pháo tới.

*34 / 76 đơn vị có lời hướng dẫn.*

#### Lời hướng dẫn trong game theo đơn vị (03_boss/Boss; chuỗi guide.<id> của GuideText.cs)

- **Argus** (`argus`): Cách đánh: khi nó còn, pháo binh địch tản mát chỉ khoảng một nửa. Cao xạ và radar. · Mạnh / yếu: chậm và to; chỉ phòng không và tiêm kích bắn tới. · Mẹo: phá radar là pháo binh địch lại bắn tản mát.
- **Juggernaut** (`armored_train`): Cách đánh: hai pháo nặng (42 m), hộp rốc-két, hai pháo cao xạ và súng máy; bị bắn thì núp trong khói, còn nửa máu thì tự vá 20% một lần. · Mạnh / yếu: pháo của nó diệt xe tăng và xe nhẹ gần đường ray; nó không thể rời đường ray. · Mẹo: bố trí xe diệt tăng và pháo binh dọc tuyến đường phía trước nó, cách đường ray hơn 45 m.
- **Bastion Mk.0** (`bastion_mk0`): Cách đánh: chiếc Bastion đầu tiên của Brandt: một khẩu cối hạng nặng và hai tháp pháo 40 mm trên xích, bò chậm về phía căn cứ ta. · Mạnh / yếu: mặt trước dày, chậm; hai tháp pháo là thứ phòng thủ gần duy nhất. · Mẹo: phá khẩu cối là nó hết nguy hiểm từ xa.
- **Behemoth** (`behemoth`): Cách đánh: pháo chính hai nòng (40 m), pháo 120 mm, pháo cao xạ, tên lửa bắn cả đất lẫn trời (45 m) và bệ Kornet đôi sau tháp chính; còn 70% máu gọi 2 tăng tinh nhuệ. · Mạnh / yếu: nghiền nát xe nhẹ và xe tăng; khắc tinh là xe diệt tăng, giáp dày khiến đạn súng máy vô dụng. · Mẹo: đánh từ ngoài 45 m; còn nửa máu nó nổi điên (bắn nhanh hơn), dưới 35% thỉnh thoảng bật khiên.
- **Inferno** (`behemoth_inferno`): Cách đánh: hai súng phun lửa lớn (20 m) đốt cháy mặt đất; hộp rốc-két nhiệt áp đánh tầm 10–46 m; còn 70% máu gọi 2 tăng tinh nhuệ. · Mạnh / yếu: thiêu chảy xe nhẹ và xe tăng tới gần; yếu trước máy bay vì chỉ có một khẩu pháo cao xạ. · Mẹo: giữ khoảng cách: xe diệt tăng và pháo binh bắn từ ngoài 46 m, trực thăng tấn công và cường kích đánh từ trên cao.
- **Behemoth Mk.0** (`behemoth_mk0`): Cách đánh: bản lắp đầu tiên của Behemoth, chậm hơn bản hoàn chỉnh: pháo chính, hai pháo sườn và một giàn rốc-két trên cùng thân xe. · Mạnh / yếu: mặt trước giáp cấp 3; không có pháo cao xạ và hệ thống bảo vệ chủ động, nên máy bay và tên lửa không gặp cản trở nào. · Mẹo: mang máy bay và tên lửa; phá pháo chính, khẩu mạnh nhất của nó.
- **Behemoth Mk.II** (`behemoth_mk2`): Cách đánh: bản nâng cấp của Varga sau khi Behemoth gục: pháo chính, hai cao xạ và hệ thống bảo vệ chủ động bắn hạ tên lửa. · Mạnh / yếu: mặt trước giáp cấp 4 dưới lớp băng; hông và sau mỏng hơn nhiều. · Mẹo: đánh vào hông; phá hệ thống bảo vệ trước khi dùng tên lửa.
- **Tempest** (`behemoth_tempest`): Cách đánh: pháo điện từ nạp năng lượng một giây (cuộn dây sáng lên) rồi xuyên thủng cả hàng tới 80 m; hai pháo điện từ bắn đất lẫn trời (55 m). · Mạnh / yếu: trừng phạt xe đi thành hàng dọc; ở gần, EMP (22 m) làm choáng xe mặt đất, và nó bật khiên khi bị thương. · Mẹo: dàn quân và áp sát từ nhiều hướng; khi cuộn dây sáng lên, hãy tránh khỏi đường ngắm của nó.
- **Caspian** (`caspian`): Cách đánh: lao dọc bờ khoảng 6 giây mỗi lượt rồi vòng ra xa khoảng 20 giây; là mục tiêu trên mặt nước. Mỗi lượt lao nó phóng một tên lửa chống hạm vào cụm quân lớn nhất (có đánh dấu trước); hai pháo 23 mm đôi và một AK-630 che chắn. · Mạnh / yếu: giáp mỏng; phá cụm động cơ ở mũi thì nó chậm lại. · Mẹo: để sẵn pháo bắn nhanh trên bờ đón lượt lao, và phòng không hoặc C-RAM cho tên lửa.
- **Cerberus** (`cerberus`): Cách đánh: tạm dùng thân Behemoth (pháo, cao xạ, ổ rốc-két). Pháo đầu bắn xe mặt đất, cao xạ giữa đuổi máy bay, ổ rốc-két sau phủ một vùng. · Mạnh / yếu: mỗi bộ phận là một vũ khí riêng; chậm. · Mẹo: phá cao xạ trước thì không kích thoải mái; phá pháo chính thì đoàn xe không làm hại xe tăng nữa.
- **Roc** (`command_airship`): Cách đánh: hai tháp pháo phòng không 57 mm, hai tháp 30 mm đôi dưới bụng, drone từ hai nhà chứa và thỉnh thoảng mỗi nhà chứa thả một UAV tấn công. Mỗi bộ phận có máu riêng: thân không nhận sát thương cho tới khi hai động cơ bị phá. · Mạnh / yếu: chỉ phòng không và tiêm kích với tới; phá nhà chứa thì ngừng thả drone, phá radar thì pháo phòng không của nó bắn lệch. · Mẹo: bắn động cơ trước để mở thân, rồi tới radar; mang pháo cao xạ và tên lửa phòng không, thêm tiêm kích để diệt UAV.
- **Daedalus** (`daedalus`): Cách đánh: khoảng 10 giây trên quỹ đạo (không bắn tới được), sau đó đổi tầng cao và thấp theo lịch cố định, không lên lại quỹ đạo. Ba cửa thả khoang thả liên tục khoang chở 1–2 xe (tối đa tám xe còn sống); khoang đang rơi bắn hạ được. Pha 3 nó dừng hẳn ở tầng thấp, mở toàn bộ khoang. Hai pháo 30 mm và hai pháo 57 mm bắn từ dưới bụng. · Mạnh / yếu: tự nó bắn yếu hơn Icarus; thân trên cấp 3, bụng 2. Tháp la-de phòng thủ chặn tên lửa bắn vào nó. · Mẹo: bắn hạ khoang đang rơi và phá cửa thả: mỗi cửa mất là thả chậm hơn, đòn đổ bộ lớn cũng hụt đi.
- **Matriarch** (`drone_mothership`): Cách đánh: pháo và bầy drone cảm tử từ ba khoang phóng (70 m) đánh mặt đất, pháo cao xạ chống máy bay; cứ 30 giây phóng ra 3 UAV tấn công. · Mạnh / yếu: nhấn chìm mặt đất bằng drone; chỉ phòng không và tiêm kích gây sát thương được, còn nửa máu thì bật khiên. · Mẹo: dồn pháo cao xạ và tên lửa phòng không bên dưới, tăng APS hoặc la-de chặn drone, tiêm kích dọn UAV tấn công.
- **Tartarus** (`earth_borer`): Cách đánh: chui xuống đất, khoan ngầm không bị nhắm tới dưới cụm xe mặt đất đông nhất của bạn, mặt đất nứt 2 giây rồi nó trồi lên gây rung chấn làm choáng mọi xe mặt đất trong 15 m. Mũi khoan và hai khẩu pháo kết liễu nốt. · Mạnh / yếu: cực nguy hiểm với cụm xe tăng dày; ngay sau khi trồi lên nó nhận thêm 50% sát thương trong 6 giây, và máy bay không bao giờ nằm dưới nó. · Mẹo: rời khỏi vết nứt ngay, rồi dồn hỏa lực vào nó lúc nó lộ thân.
- **Fenrir** (`fenrir`): Cách đánh: nhanh: lao vào, xả hai hộp rốc-két rồi rút; cao xạ đuổi trực thăng. · Mạnh / yếu: nhẹ hơn Jötunn nhiều; không giữ trận địa được. · Mẹo: đón nó lúc rút, đặt xe diệt tăng trên đường rút.
- **Bastion** (`fortress_bastion`): Cách đánh: khẩu cối hạng nặng bắn tầm 12–80 m, bốn tháp pháo tự động 40 mm (28 m) phủ mọi hướng, hai súng máy NSV giữ hai bên hông, còn nửa máu nó tự vá giáp một lần. · Mạnh / yếu: pháo tự động xé nát xe nhẹ tới gần; giáp dày chặn đạn súng máy, cối không bắn được trong vòng 12 m. · Mẹo: mang xe diệt tăng và pháo hạng nặng, để dành hỏa lực dồn cho sau lần tự vá duy nhất của nó.
- **Hive** (`fortress_hive`): Cách đánh: không có pháo lớn: hai giàn phóng bầy drone tới 70 m, dàn tên lửa (62 m) và pháo cao xạ giữ bầu trời, còn thả thêm UAV tấn công. · Mạnh / yếu: xé nát máy bay; drone của nó hại được xe tăng, nhưng xe tăng và pháo binh mới là thứ hạ được nó. · Mẹo: để máy bay ở nhà; mang tăng APS hoặc xe la-de phòng không chặn drone, rồi dùng xe tăng và pháo binh bào dần.
- **Garuda** (`garuda`): Cách đánh: tạm dùng thân khí cầu chỉ huy (tháp súng và drone). Tháp phòng thủ và tên lửa đuổi máy bay; cứ 70 giây nó rải thảm 20 quả bom. · Mạnh / yếu: mục tiêu rộng, nhiều súng; chỉ phòng không tầng thấp mới trúng tốt. · Mẹo: dàn quân ra và để ý dải dài; phá khoang bom để chặn thảm bom.
- **Hydra** (`hydra`): Cách đánh: tạm dùng thân Typhon (pháo boong và cửa ống phóng, nhỏ và nhanh hơn). Nó lặn rồi nổi theo lịch ngắn, chỉ bắn khi nổi, và phóng tên lửa hành trình mỗi 16 giây. · Mạnh / yếu: lúc lặn không đánh tới được; thân mỏng. · Mẹo: chờ bong bóng; phá cửa ống phóng để chặn tên lửa.
- **Hyperion** (`hyperion`): Cách đánh: tạm dùng thân Silver Bug (chỉ ở tầng cao). Tháp la-de phòng thủ điểm che chắn, mỗi phút thả hai khoang đổ bộ, cứ 65 giây một tia mặt trời đốt dải 70 × 6 m trong 4 giây. · Mạnh / yếu: không bao giờ xuống tầng thấp, chỉ tên lửa tầm xa và pháo điện từ với tới. · Mẹo: giữ sẵn tên lửa tầm xa và pháo ray; rời dải ngay khi có cảnh báo.
- **Icarus Mk.0** (`icarus_mk0`): Cách đánh: không lên quỹ đạo: đổi tầng cao và thấp theo lịch cố định. Một tháp la-de, một khoang đổ bộ và một la-de phòng thủ điểm bắn hạ tên lửa. · Mạnh / yếu: ở tầng cao chỉ phòng không tầm xa và tiêm kích bắn tới; ở tầng thấp mọi vũ khí phòng không đều tới. · Mẹo: chờ lúc nó xuống thấp; phá la-de phòng thủ điểm trước khi dùng tên lửa.
- **Ixion** (`ixion`): Cách đánh: xe tải mỏ bọc thép (BelAZ-75710) chạy thẳng khoảng 7 m/s và xoay rất chậm. Tháp pháo 125 mm hàn trên thùng xoay 360°, nạp đạn nổ mạnh với đám đông (nổ lõi 5 m, rìa 10 m) và đạn xuyên với mục tiêu đơn lẻ, khoảng 780 mỗi 2 giây; cứ khoảng 10 giây nó lao theo đường thẳng báo trước 2 giây, khoảng 900 và choáng 1 giây, tháp pháo vẫn bắn trong lúc lao; hai súng máy 12,7 mm trên nóc; khi rẽ n… · Mạnh / yếu: giáp trước 4, hông 3, sau và nóc 2; bốn lốp sau giáp cấp 1 là điểm yếu; phá một lốp trước thì cú lao lệch và dừng, phá cả hai thì nó quay vòng rất chậm; phá tháp pháo trên thùng là mất pháo, phá ca-bin là súng máy ngừng bắn. · Mẹo: tránh khỏi đường lao, đánh vào hông và đuôi khi nó xoay, và tránh dải mìn.
- **Kraken** (`kraken`): Cách đánh: tạm dùng thân tàu Leviathan (pháo, ống phóng tên lửa và CIWS). Boong cất cánh phóng tiêm kích và drone, và cứ 75 giây nó gọi một đợt không kích. · Mạnh / yếu: thân tàu dài và dày nhất mặt nước; boong thang máy mỏng (giáp 2). · Mẹo: phá boong cất cánh là máy bay hết xuất kích; trong 4 giây cảnh báo hãy ra khỏi dải đỏ dài.
- **Kronos** (`kronos`): Cách đánh: chạy rất chậm theo đường cố định về căn cứ ta; bánh gầu nghiền mọi thứ phía trước (900 mỗi giây trong 6 m), cả tường lẫn tháp (gấp ba). Tới được HQ là thua nhiệm vụ. Hai tháp 30 mm, hai tháp pháo 57 mm tự động và một giàn rốc-két che chắn. Pha 2 nó đi nhanh hơn; pha 3 bánh gầu quay nhanh và hất đá vụn ra xung quanh. · Mạnh / yếu: bánh gầu giáp cấp 4, thân 3, cụm xích 2. Mỗi cụm xích bị phá là nó chậm lại. · Mẹo: phá cụm xích để câu giờ, phá cần gầu để chặn đòn quét; đừng xây tường chắn đường nó.
- **Charybdis** (`landing_hovercraft`): Cách đánh: chạy theo lộ trình dọc bờ biển; cứ 35 giây dừng lại, hạ cửa đổ bộ và thả 3–4 xe lên bờ, tối đa năm lần. Bốn pháo CIWS sáu nòng che chắn cả đất lẫn trời (hai khẩu bắn hạ tên lửa và rốc-két) và hai dàn rốc-két 140 mm bắn phá bờ. · Mạnh / yếu: mỗi lần đổ bộ là địch thêm quân; nó to và xoay chậm, đánh trúng nó trên đường tới là cắt bớt số lần đổ bộ. · Mẹo: đón đầu nó trước lần đổ bộ đầu tiên bằng xe diệt tăng và pháo binh, và giữ lực lượng dự bị cho số quân đã lên bờ.
- **Leviathan** (`leviathan`): Cách đánh: ba tháp pháo ba nòng 406 mm bắn loạt vào bờ, mỗi tháp một nòng, có cảnh báo trước và quét dần dọc bờ, và bắn cả chín nòng theo dải qua căn cứ khi tung siêu vũ khí; hai tháp ba nòng 155 mm tự bắn, tám bệ 25 mm và một bệ tên lửa phòng không tầm trung bắn máy bay; tên lửa hành trình đánh vào cụm quân và căn cứ; CIWS bắn hạ tên lửa, rốc-két và drone (không chặn đạn pháo, đạn súng hay Năng… · Mạnh / yếu: hông tàu giáp cấp 4, boong chỉ cấp 2: pháo binh, bom, pháo phản lực và đòn đánh nóc đánh vào boong; pháo xe tăng chỉ với tới khi nó áp sát, đứng ở đầu cầu tàu. · Mẹo: giữ ngọn hải đăng và trận địa pháo bờ biển; mang pháo binh và máy bay; phá CIWS (hoặc tuần dương hạm và tàu hộ vệ) trước khi dùng tên lửa, phá một tháp pháo chính khi loạt bắn mạn được đánh dấu, và phá buồng máy trước khi nó bỏ chạy.
- **Locust** (`locust`): Cách đánh: khoang drone thả drone liên tục; cao xạ trên lưng. · Mạnh / yếu: thân rất mỏng (giáp cấp 1): phòng không hạ nó nhanh. · Mẹo: phá khoang drone là nó hết đòn.
- **Harpy** (`mega_gunship`): Cách đánh: hai giàn rốc-két, hai pháo 30 mm, một súng máy nhiều nòng và mỗi bên cửa một súng máy 12,7 mm; thả mồi nhiệt liên tục, hộ tống là 2 trực thăng tấn công và 1 trực thăng trinh sát vũ trang đánh dấu mục tiêu, 50% thì nổi điên. · Mạnh / yếu: pháo xe tăng và pháo binh không chạm được nó: chỉ phòng không và tiêm kích gây sát thương. · Mẹo: dồn pháo cao xạ (xe phòng không, Tunguska) vì đạn pháo không bị mồi nhiệt lừa, thêm tiêm kích để diệt trực thăng hộ tống.
- **Jötunn** (`mobile_fortress`): Cách đánh: hai lựu pháo 203 mm (60 m), hộp rốc-két, pháo cao xạ, tháp 30 mm đôi chống drone và tên lửa; EMP làm choáng xe mặt đất trong 22 m; hộ tống là 2 tăng nặng và 1 xe công binh sửa cho nó, còn nửa máu thêm 1 xe công binh. · Mạnh / yếu: xé nát xe nhẹ và xe tăng dồn quanh nó; xe diệt tăng và pháo hạng nặng bào dần được nó. · Mẹo: đánh từ ngoài 22 m để né EMP, và coi chừng dưới 40% máu nó bắn nhanh gấp đôi.
- **Moloch** (`moloch`): Cách đánh: bò chậm theo đường của nhiệm vụ; hai cửa xưởng cứ 20 giây thả 1–2 xe (xe tăng nhẹ và xe bộ binh, từ pha 2 thêm tăng chủ lực), mỗi phút thêm một xe mỗi lượt, tối đa sáu xe còn sống. Bốn tháp pháo 120 mm, cao xạ và hai ZU-23 trên nóc che chắn. · Mạnh / yếu: giáp trước cấp 4, hông 3, sau 2: cửa xưởng ở phía sau, giáp mỏng cũng ở đó. Phá cụm xích thì nó chậm lại. · Mẹo: vòng ra sau, phá cả hai cửa trước: nó ngừng sinh xe, siêu vũ khí chỉ còn loạt pháo.
- **Monster** (`monster`): Cách đánh: tạm dùng thân Bastion (tháp pháo và khẩu cối, to hơn). Nó bò rất chậm, cứ 80 giây nòng 800 mm nâng lên bắn một quả 4.000 sát thương, nổ lan 20 m. · Mạnh / yếu: giáp và máu khổng lồ, nhưng chậm hơn mọi boss. · Mẹo: ra khỏi vòng đỏ trong 6 giây nó hiện; phá khẩu cối (nòng dài) là mất đòn này.
- **Morrigan** (`morrigan`): Cách đánh: nhanh hơn mọi tiêm kích của ta và tàng hình: chỉ bị phát hiện ở cự ly gần, hoặc trong chốc lát sau khi khai hỏa. Tên lửa không đối không từ hai khoang săn máy bay của bạn; bom dẫn đường săn xe phòng không. · Mạnh / yếu: rất nhanh và khó thấy; giáp mỏng, các khoang và động cơ phá được. · Mẹo: giữ ra-đa và phòng không gần máy bay để thấy được nó; bắn ngay lúc nó khai hỏa; phá các khoang tên lửa để chặn tên lửa của nó.
- **Nemesis** (`nuke_train`): Cách đánh: pháo nặng hai nòng (40 m), toa pháo 152 mm và ba pháo cao xạ; bị bắn thì núp trong khói; phía sau có toa rốc-két và toa SAM tầm xa, xe bọc thép hộ tống chạy dọc đường ray. · Mạnh / yếu: pháo của nó phá nát mọi thứ gần đường ray; nó không rời được đường ray và không có tên lửa để đánh. · Mẹo: dùng pháo binh và xe diệt tăng đánh mạnh và sớm; phải chặn nó trước khi tới bãi phóng.
- **Nyx** (`nyx`): Cách đánh: tạm dùng thân Leviathan thu nhỏ. Pháo điện từ bắn mỗi 8 giây, hai CIWS chặn tên lửa và drone, rồi tới tên lửa chống hạm. Nó tàng hình: chỉ thấy ở gần hoặc ngay sau khi bắn. · Mạnh / yếu: khó thấy; mỏng so với kích cỡ. · Mẹo: giữ radar hoặc drone trên mặt nước để thấy nó; phá CIWS trước khi dùng tên lửa.
- **Gungnir** (`rail_supergun`): Cách đánh: cứ 25 giây một phát điện từ vào cụm xe mặt đất đông nhất của bạn, ở bất cứ đâu trên bản đồ: nó xuyên qua tối đa năm xe trên một đường thẳng (1.000 mỗi xe) rồi nổ ở xe cuối (2.000 trong lõi 12 m, còn 40% tới rìa 20 m); vòng đỏ báo điểm ngắm trước 3 giây. Tường, tháp pháo, tháp phòng không và trạm chỉ thị mục tiêu bảo vệ nền pháo; hai khẩu 40 mm che chắn. · Mạnh / yếu: trừng phạt đội quân dồn cục; không di chuyển được, và mất trạm chỉ thị thì đạn rơi lệch xa. · Mẹo: luôn di chuyển và tản ra khi thấy vòng đỏ; phá trạm chỉ thị trước, rồi cho xe tăng tiến vào sau pháo binh.
- **Scylla** (`scylla`): Cách đánh: nhanh hơn Leviathan, chạy tuyến gần bờ: pháo AK-130 130 mm đôi nã vào bờ, ống phóng bắn tên lửa chống hạm mỗi 15 giây, CIWS chặn tên lửa và drone. · Mạnh / yếu: đủ gần để pháo xe tăng ở đầu cầu tàu bắn tới. · Mẹo: giữ cầu tàu bằng xe tăng, phá CIWS trước khi dùng tên lửa.
- **Icarus** (`silver_bug`): Cách đánh: tháp la-de chính và hai pháo coilgun bắn xuống mặt đất ở cả tầng cao lẫn tầng thấp; khoang đổ bộ thả xe xuống; cứ 60 giây có 7 thanh vonfram rơi từ vệ tinh của nó (khi đã rơi xuống đất: 9 thanh mỗi 50 giây). · Tầng độ cao: mở màn ở quỹ đạo thấp, ngoài tầm bắn; sau đó lặp cố định tầng cao (chỉ PK tầm xa, trạm PK tầm xa và tiêm kích bắn tới) và tầng thấp (mọi vũ khí bắn được máy bay, cộng pháo điện từ); dưới 30% máu nó rơi xuống thành pháo đài mặt đất, bốn tháp pháo thường trên xác. · Mạnh / yếu: bụng nó (giáp cấp 2) lộ ra ở tầng thấp; hai tháp la-de phòng thủ điểm của nó bắn hạ bớt SAM và tên lửa của ta. · Mẹo: giữ phòng không tầm xa sẵn sàng cho các đợt tầng cao, dồn mọi vũ khí khác vào các đợt tầng thấp, bắn hạ khoang đổ bộ trước khi chúng chạm đất, và phá ăng-ten liên kết vệ tinh để hủy một đợt mưa thanh vonfram.
- **Spectre** (`sky_fortress`): Cách đánh: bay vòng quanh mục tiêu, pháo 105 mm, hai 40 mm và một 25 mm bắn từ bên trái (50–58 m), kèm Griffin; không bắn được máy bay. · Mạnh / yếu: hủy diệt quân mặt đất nằm dưới vòng bay; chỉ phòng không và tiêm kích với tới nó. · Mẹo: xây cao xạ và tên lửa phòng không sớm, thêm tiêm kích vì pháo của nó không bắn được máy bay; bay kèm là 2 tiêm kích và 1 UAV đánh dấu quân ta (hạ UAV thì pháo của nó bắn lệch hơn), còn nửa máu thêm 2 tiêm kích.
- **Stymphalos** (`stymphalos`): Cách đánh: tạm là một thân với khoang drone và cao xạ của tàu mẹ, nhanh. Nó bắn tên lửa nhỏ và thả drone liên tục. · Mạnh / yếu: rất nhanh; giáp mỏng, phòng không hạ nó nhanh. · Mẹo: phá khoang drone và cao xạ; phòng không diện rộng và đạn nổ trên không là tốt nhất.
- **Atlas** (`supreme_command`): Cách đánh: chỉ có hai súng máy nhẹ; mọi quân địch trong 40 m quanh nó tăng 20% sát thương và 20% tốc độ bắn. Có cận vệ tinh nhuệ đi kèm, còn 60% máu thì gọi thêm. · Mạnh / yếu: quân địch gần nó nguy hiểm hơn nhiều; bản thân nó gần như không đánh lại được và không chạy thoát được thứ gì. · Mẹo: kéo trận đánh ra xa nó, hoặc đánh nó từ xa bằng pháo binh và máy bay; hạ nó là cả đạo quân yếu đi ngay.
- **Typhon** (`typhon`): Cách đánh: lặn (không bắn tới được) và nổi (mục tiêu trên mặt nước) theo lịch từng pha, mỗi lần nổi ở một chỗ khác; bong bóng báo trước chỗ nổi. Khi nổi nó phóng tên lửa hành trình tầm ngắn mỗi 12 giây và tự vệ bằng tên lửa phòng không. Pha 3 nổi hẳn, thêm pháo boong 100 mm. · Mạnh / yếu: thân giáp cấp 4, tháp chỉ huy và boong 2: pháo binh, bom và đòn đánh nóc đánh vào boong. · Mẹo: chờ sẵn pháo binh và máy bay chỗ bong bóng; phá cửa ống phóng lúc cảnh báo (cửa mở trên mặt nước) hoặc bắn hạ tên lửa.

*41 / 41 đơn vị có lời hướng dẫn.*

## 12. Hỗ trợ hỏa lực

Trạng thái: Đã áp

Nguồn dữ liệu: 02_phuong_tien/The_ho_tro. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §12. Hỗ trợ.

Thẻ hỗ trợ trong bộ bài (2 ô), gọi vào một điểm trên bản đồ; không gọi được vào vùng căn cứ địch; vật phẩm dùng một lần mua bằng xu. Mỗi thẻ hỗ trợ có clip Xem bắn riêng (gọi hỏa lực lên một cụm mục tiêu).

![Clip Xem bắn của các thẻ hỗ trợ (pháo kích, không kích, tên lửa hành trình, napalm, ném bom rải thảm, MOAB, bom chùm, m…](../images/02_phuong_tien/r6_supports.png)

*Hình: Clip Xem bắn của các thẻ hỗ trợ (pháo kích, không kích, tên lửa hành trình, napalm, ném bom rải thảm, MOAB, bom chùm, máy bay pháo, EMP, khói, tiếp tế, chi viện). Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

Sheet: 02_phuong_tien/The_ho_tro — Thẻ hỗ trợ (40 dòng, 36 cột)

| id | ten_en | ten_vi | units | so_voi_ban_goc | blast_m | consumable | cooldown_s | count | cp |
|---|---|---|---|---|---|---|---|---|---|
| air_raid | Air raid | Không kích bất ngờ |  | giong | 8 |  | 0 | 10 |  |
| airstrike | Airstrike | Không kích |  | giong | 10 |  | 90 | 4 | 9 |
| ammo_resupply | Ammo resupply | Thả dù tiếp đạn |  | giong |  |  | 60 | 1 | 3 |
| artillery_barrage | Barrage | Pháo kích |  | giong | 7 |  | 60 | 6 | 5 |
| bug_crash | Icarus crashing | Icarus rơi |  | giong | 16 |  | 0 | 1 |  |
| chaff_strike | Radar chaff | Rải nhiễu radar |  | giong |  |  | 45 | 1 | 2 |
| cluster_at_strike | AT cluster bomb | Bom chùm chống tăng |  | giong | 3 |  | 90 | 10 | 9 |
| cluster_strike | Cluster bombs | Bom chùm |  | giong | 5.5 | TRUE | 15 | 30 |  |
| cruise_missile | Cruise missile | Tên lửa hành trình |  | giong | 9 |  | 120 | 1 | 14 |
| decoy_paradrop | Decoy paradrop | Mồi nhử thả dù | decoy_tank;decoy_tank;decoy_tank | giong |  |  | 45 | 3 | 2 |
| drone_intercept_strike | Drone intercept strike | Đòn tên lửa đánh chặn drone |  | giong | 2 |  | 40 | 6 | 3 |
| emp_blast | EMP blast | Bom EMP |  | giong |  | TRUE | 20 | 1 |  |
| escort_drop.aa_vehicle |  |  | aa_vehicle | giong |  |  | 0 | 1 |  |
| escort_drop.engineer_vehicle |  |  | engineer_vehicle | giong |  |  | 0 | 1 |  |
| escort_drop.ifv |  |  | ifv | giong |  |  | 0 | 1 |  |
| field_repair | Field repair | Sửa chữa toàn quân |  | giong |  | TRUE | 30 | 5 |  |
| field_tower | Field tower | Tháp dã chiến | guard_tower;atgm_tower | giong |  |  | 90 | 1 | 6 |
| glide_bomb_strike | Glide bomb strike | Đòn bom lượn |  | giong | 10 |  | 90 | 2 | 8 |
| guided_shell_strike | Guided shell | Đạn pháo dẫn đường |  | giong | 6 |  | 45 | 1 | 4 |
| gunship_support | Gunship on call | Pháo hạm yểm trợ | sky_gunship | giong |  | TRUE | 30 | 1 |  |
| hq_barrage |  |  |  | moi | 8 |  | 0 | 3 |  |
| illum_flare_strike | Illumination flare | Pháo sáng chiếu sáng |  | giong |  |  | 30 | 1 | 1 |
| instant_counter_battery | Instant counter-battery | Phản pháo tức thì |  | giong | 7 |  | 75 | 4 | 6 |
| jam_storm | Jamming storm | Bão gây nhiễu |  | giong |  |  | 90 | 1 | 5 |
| leviathan_cruise_mark | Leviathan's cruise missile | Tên lửa hành trình Leviathan |  | doi | 10 |  | 0 | 1 |  |
| leviathan_cruise_mark_7 | Caspian's cruise missile | Tên lửa hành trình Caspian |  | moi | 7 |  | 0 | 1 |  |
| leviathan_shell | Leviathan's shell | Đạn pháo Leviathan |  | doi | 14 |  | 0 | 1 |  |
| moab | MOAB | Bom MOAB |  | giong | 27 | TRUE | 20 | 1 |  |
| napalm_strike | Napalm strike | Bom napalm |  | giong | 9 |  | 90 | 8 | 9 |
| pod_drop | Drop pod | Khoang đổ bộ |  | giong | 4 |  | 0 | 1 |  |
| reinforcements | Airdropped armour | Tiếp viện thả dù | main_battle_tank;main_battle_tank;ifv | giong |  | TRUE | 30 | 3 |  |
| remote_mines | Remote mines | Mìn rải từ xa |  | giong | 4 |  | 60 | 8 | 5 |
| repair_drop | Repair | Sửa chữa |  | giong |  |  | 60 | 6 | 4 |
| sead_strike | SEAD strike | Đòn SEAD |  | giong | 3 |  | 90 | 1 | 7 |
| shield_dome | Shield dome | Khiên vòm |  | giong |  | TRUE | 20 | 1 |  |
| smoke_screen | Smoke | Màn khói |  | giong |  |  | 30 | 1 | 2 |
| super_gun_shell | Super-gun shell | Đạn siêu pháo |  | giong | 15 |  | 0 | 1 |  |
| supergun_shell | Rail supergun shell | Đạn siêu pháo đường ray |  | giong | 12 |  | 0 | 1 |  |
| uav_loiter_strike_support | Loitering UAV strike | UAV lượn tấn công | uav_loiter_strike | giong |  |  | 75 | 1 | 6 |
| uav_scan | UAV scan | UAV quét |  | giong |  |  | 45 | 1 | 2 |

*in 10 / 36 cột; 14 cột khác (và raw_json, nguon): xem sheet.*

### 12b. Bảng giá, hệ đạn và hồi đạn

Trạng thái: Đã áp

Nguồn dữ liệu: (không có sheet; chỉ văn bản). Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §12b. Bảng giá, §12b. Hệ đạn.

#### 12b. Bảng giá

Mọi giá trong game ở một chỗ. **CP** là điểm chỉ huy trả mỗi lần gọi trong trận. **Xu** là tiền duy nhất ngoài trận: mua thẻ cao cấp, mua sớm thẻ chiến dịch trước khi thắng màn mở khóa, mua vật phẩm. Thẻ có sẵn không cần mua. Giá lên hạng thẻ, hòm và gói xu ở phần kinh tế.

#### Tháp căn cứ (22)

Tháp không tốn CP khi đặt vào căn cứ: nó chiếm một ô theo cỡ. Bị phá trong trận thì xây lại bằng CP sau một thời gian chờ.

#### 12b. Hệ đạn và hồi đạn

- **Lượng đạn:** bom, tên lửa và rốc-két của máy bay và trực thăng có số lượng khi đầy đạn (ghi ở mục "Đạn và nạp đạn" trên mỗi thẻ); pháo máy bay và súng máy không giới hạn, chỉ thay băng.
- **Hồi dần trên chiến trường:** từng quả hồi theo thời gian, không cần căn cứ. Đang tấn công hoặc trong tầm phòng không/tiêm kích địch: một nửa tốc độ; ra khỏi vùng nguy hiểm liên tục 3 giây: đủ tốc độ.
- **Vòng chờ gần:** một vòng bay ngay sau tuyến quân ta gần nhất, ngoài tầm phòng không đã biết, cách chỗ giao tranh khoảng 2–3 giây bay; tính lại liên tục theo chiến tuyến. Không đơn vị nào bay về căn cứ hay ra ngoài bản đồ để nạp.
- **Rút đúng lúc:** hết đạn giữa lượt thì làm xong lượt (bổ nhào, lượt ném bom, vòng bay) rồi mới ra vòng chờ, bay theo đường thật, vẫn bị bắn được; chỉ huy AI cho ra sớm khi đạn dưới 20% và đang có quãng lặng.
- **Nạp nhanh hơn:** Bãi đáp ×2 (và hồi 3% máu/giây), sở chỉ huy ×1,5 (1% máu/giây), trực thăng cạnh Xe tiếp đạn ×2. Chỉ ghé khi nhanh hơn vòng chờ hoặc cần hồi máu.
- **Máy bay ném bom:** chỉ vào lượt mới khi có ít nhất 2/3 tải bom; ưu tiên cụm quân và công trình, không thả gần quân ta, nghỉ trước khi ném lại cùng khu vực. Oanh tạc cơ 9 quả, máy bay tàng hình 2, Su-25 16 rốc-két, không kích bất ngờ 10, bom chùm 30 quả con.
- **Xe tiếp đạn (mới, 4 CP):** điểm nạp tiền phương: trực thăng đứng cạnh hồi đạn nhanh gấp đôi, bệ phóng và xe tên lửa quanh nó nạp nhanh gấp ba. Xe công binh chỉ còn sửa chữa (3 CP).
- **Bãi đáp:** nhánh hạng 7: Nhà chứa (+1 trần máy bay) hoặc Phục vụ nhanh. AI địch đặt Bãi đáp trong căn cứ; phá Bãi đáp pháo đài trong Công thành được 12 CP.
- **Icon trên chiến trường:** cạnh thanh máu: sắp hết (vàng), hết (đỏ nhấp nháy), đang ra vòng chờ, đang hồi (vòng tiến độ mờ khi hồi chậm, sáng khi hồi đủ), lóe sáng khi đầy. Địch chỉ hiện hết đạn và đang ra vòng chờ. Bản đồ nhỏ hiện vòng chờ của ta.

### 12c. Commander

Trạng thái: Đã áp

Nguồn dữ liệu: 02_phuong_tien/Commander; 02_phuong_tien/Commander_noi_tai; 02_phuong_tien/Commander_gia; 06_ai/AI_tuong. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §12c.

Người chơi chọn một commander trước trận; nội tại của nó áp cho cả phe, trong mọi chế độ. Mỗi màn gắn với một tướng địch thì địch mang nội tại của tướng đó. Commander mở dần theo chương. Không còn chọn học thuyết riêng: lợi thế của năm học thuyết cũ đã gộp vào commander hợp lối chơi (Crown: thiết giáp, Hawk: không quân, Longshot: pháo binh, Rush: chớp nhoáng, Ledger: hậu cần), chỗ trùng loại thưởng thì gộp thành một con số, không cộng dồn; bảng dưới là số mới.

#### Commander của người chơi (14)

| Commander | Nhóm | Vai trò | Hợp lối chơi | Điểm mạnh | Điểm yếu | Mở khóa |
|---|---|---|---|---|---|---|
| **Đại tá Marcus Kade** Iron | chiến đấu | Chỉ huy 7th Mechanized Brigade · biệt danh Iron | Hợp với: Bộ bài cân bằng | Toàn quân +5% sát thương và +5% máu. | Không có. | Mở ở chương 1 |
| **Kỹ sư Mara Lind** Kỹ sư trưởng | chiến đấu | Kỹ sư trưởng, phụ trách căn cứ | Hợp với: Công binh và căn cứ vững | Trạm sửa chữa và công binh sửa nhanh hơn 25%; công binh rẻ hơn 20% CP. | Máy bay và trực thăng −10% sát thương. | Mở ở chương 2 |
| **Trung úy Jonah Reyes** Hawk | chiến đấu | Chỉ huy không quân · biệt danh Hawk | Hợp với: Máy bay và trực thăng | Máy bay và trực thăng +10% sát thương và +20% máu, hồi đạn nhanh hơn 15%; trần máy bay +1; yểm trợ hồi nhanh hơn 15%. | Tháp −10% máu. | Mở ở chương 3 |
| **Đại úy Nadia Kerr** Tình báo | chiến đấu | Sĩ quan tình báo | Hợp với: Trinh sát và đánh dấu mục tiêu | +15% tầm nhìn; phát hiện tàng hình từ xa hơn 25%; địch đang bị lộ nhận thêm 5% sát thương. | Xe hạng nặng −5% máu. | Mở ở chương 4 |
| **Tiến sĩ Elara Venn** Queen | chiến đấu | Drone của Hegemon; người tạo ra Hive · biệt danh Queen | Hợp với: Drone | Mọi drone +15% máu và +10% sát thương; drone ta bị gây nhiễu ít hơn 30%. | Xe tăng −5% sát thương. | Mở sau khi xong chương 5 |
| **Đại úy Kaia Mendez** Rush | chiến đấu | Đột kích đường không, lực lượng phản ứng nhanh | Hợp với: Xe nhanh, tấn công sớm | Xe +15% tốc độ; trinh sát và xe nhẹ +15% máu; thả dù nhanh hơn 25%. | Toàn quân −5% máu. | Mở ở Xen kẽ II |
| **Thiếu tá Brandt** Bulwark | chiến đấu | Đồn trú bờ biển phía tây của Hegemon · biệt danh Bulwark | Hợp với: Tháp và tháp dã chiến | Tháp +15% máu và +10% sát thương; tháp thả dù rẻ hơn 20% CP. | Xe −5% tốc độ. | Mở ở chương 6 |
| **Thiếu tá Piet Dahl** Longshot | chiến đấu | Pháo binh lữ đoàn | Hợp với: Pháo binh | Pháo binh +15% sát thương, +10% tầm bắn và +25% máu; yểm trợ hồi nhanh hơn 25%. | Xe bắn thẳng −10% sát thương. | Mở ở chương 7 |
| **Thiếu tá Otto Brenn** Ledger | kinh tế | Sĩ quan hậu cần lữ đoàn | Hợp với: Trận dài | Thu nhập CP +15%; trần tiếp tế +10%. | Toàn quân −5% sát thương. | Mở ở Xen kẽ I |
| **Đại úy Tomas Adler** Flag | kinh tế | Trinh sát tiền phương, chiếm cứ điểm | Hợp với: Chiếm và giữ cứ điểm | Mỗi cứ điểm cho thêm 75% CP; chiếm nhanh hơn 30%. | Ở chế độ không có cứ điểm, thu nhập −5%. | Mở ở chương 4 |
| **Đại úy Ines Varro** Tide | kinh tế | Đội xe và tiếp viện số đông | Hợp với: Nhiều xe rẻ | Xe giá từ 5 CP trở xuống rẻ hơn 15%; trần tiếp tế +15%. | Toàn quân −5% máu. | Mở ở chương 8 |
| **Đại tá August Reyn** Crown | kinh tế | Thiết giáp hạng nặng dự bị | Hợp với: Ít xe đắt, hạng nặng | Xe tăng, xe hạng nặng và xe giá từ 9 CP trở lên +20% máu; xe giá từ 9 CP trở lên +15% sát thương. | Mọi xe đắt hơn 10% CP. | Mở ở Xen kẽ III |
| **Thượng sĩ nhất Lena Quist** Magpie | kinh tế | Thu hồi và tận dụng chiến lợi phẩm | Hợp với: Đổi quân, hạ nhiều địch | Hạ địch hoàn 35% CP thay vì 25% (mọi khoản hoàn vẫn trong trần 45%). | Xe ta bị hạ không được hoàn CP. | Mở ở chương 8 |
| **Đại úy Selma Okoye** Vault | kinh tế | Quản lý ngân quỹ lữ đoàn | Hợp với: Tích CP để mua xe lớn | Trần CP tích trữ từ 30 lên 45; khi đang có từ 20 CP trở lên, thu nhập +10%. | 90 giây đầu trận thu nhập −10%. | Mở ở chương 10 |

#### Nội tại của tướng địch (8)

| Tướng | Điểm mạnh | Điểm yếu |
|---|---|---|
| **Thiếu tá Brandt** | Tháp +15% máu. | Xe −5% tốc độ. |
| **Tướng Viktor Varga** | Xe tăng và xe hạng nặng +10% máu. | Máy bay −10% sát thương. |
| **Đại tá Ilya Orlov** | Pháo binh +15% tầm, tản mát ít hơn 20%. | Xe nhẹ −5% máu. |
| **Đô đốc Magnus Kessler** | Tiếp viện rẻ hơn 10% CP; tàu +10% máu. | Tháp −5% máu. |
| **Tiến sĩ Elara Venn** | Drone +15% máu. | Xe tăng −5% sát thương. |
| **Kasimir Wolff** | Máy bay +10% sát thương; trần máy bay +1. | Xe mặt đất −5% sát thương. |
| **Tướng Roland Thorne** | Toàn quân +5% sát thương; quân dưới 50% máu được thêm 10% sát thương. | Không có. |
| **Giám đốc Lucien Aurel** | Vũ khí Năng lượng +15% sát thương; khiên +10% máu. | Xe nhẹ −5% máu. |

Sheet: 02_phuong_tien/Commander — Commander và nội tại tướng (22 dòng, 32 cột)

| id | ho | ten_vi | khai_bao_qua | air_cap | air_rearm | bank_bonus | delivery | early_income | early_seconds |
|---|---|---|---|---|---|---|---|---|---|
| adler | Economy | Đại úy {@adler} | new CommanderDef |  |  |  |  |  |  |
| brandt | Combat |  | new CommanderDef |  |  |  |  |  |  |
| brenn | Economy | Thiếu tá {@brenn} | new CommanderDef |  |  |  |  |  |  |
| dahl | Combat | Thiếu tá {@dahl} | Combat |  |  |  |  |  |  |
| gen.aurel | General |  | Gen |  |  |  |  |  |  |
| gen.brandt | General |  | Gen |  |  |  |  |  |  |
| gen.hung | General |  | Gen |  |  |  |  |  |  |
| gen.kessler | General |  | Gen |  |  |  |  |  |  |
| gen.orlov | General |  | Gen |  |  |  |  |  |  |
| gen.quaden | General |  | Gen | 1 |  |  |  |  |  |
| gen.sen | General |  | Gen |  |  |  |  |  |  |
| gen.varga | General |  | Gen |  |  |  |  |  |  |
| kade | Combat |  | Combat |  |  |  |  |  |  |
| kerr | Combat |  | new CommanderDef |  |  |  |  |  |  |
| lind | Combat |  | new CommanderDef |  |  |  |  |  |  |
| mendez | Combat | Đại úy {@mendez} | new CommanderDef |  |  |  | 0.75 |  |  |
| okoye | Economy | Đại úy {@okoye} | Econ |  |  | 15 |  | 0.9 | 90 |
| quist | Economy | Thượng sĩ nhất {@quist} | Econ |  |  |  |  |  |  |
| reyes | Combat |  | new CommanderDef | 1 | 1.15 |  |  |  |  |
| reyn | Economy | Đại tá {@reyn} | new CommanderDef |  |  |  |  |  |  |
| varro | Economy | Đại úy {@varro} | new CommanderDef |  |  |  |  |  |  |
| venn | Combat |  | new CommanderDef |  |  |  |  |  |  |

*in 10 / 32 cột; 19 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 02_phuong_tien/Commander_noi_tai — Commander: dòng nội tại (45 dòng, 8 cột)

| id | commander_id | thu_tu | reach_m | stat | value |
|---|---|---|---|---|---|
| adler/0 | adler | 0 | Vehicles | CaptureRate | 0.3 |
| brandt/0 | brandt | 0 | Towers | Health | 0.15 |
| brandt/1 | brandt | 1 | Towers | Damage | 0.1 |
| brandt/2 | brandt | 2 | Vehicles | Speed | -0.05 |
| brenn/0 | brenn | 0 | Army | Damage | -0.05 |
| dahl/0 | dahl | 0 | Artillery | Damage | 0.15 |
| dahl/1 | dahl | 1 | Artillery | Range | 0.1 |
| dahl/2 | dahl | 2 | Artillery | Health | 0.25 |
| dahl/3 | dahl | 3 | DirectFire | Damage | -0.1 |
| gen.aurel/0 | gen.aurel | 0 | Energy | Damage | 0.15 |
| gen.aurel/1 | gen.aurel | 1 | Shielded | Health | 0.1 |
| gen.aurel/2 | gen.aurel | 2 | Light | Health | -0.05 |
| gen.brandt/0 | gen.brandt | 0 | Towers | Health | 0.15 |
| gen.brandt/1 | gen.brandt | 1 | Vehicles | Speed | -0.05 |
| gen.hung/0 | gen.hung | 0 | Army | Damage | 0.05 |

*15 / 45 dòng đầu: xem sheet 02_phuong_tien/Commander_noi_tai.*

Sheet: 02_phuong_tien/Commander_gia — Commander: hệ số giá (5 dòng, 7 cột)

| id | commander_id | thu_tu | reach_m | scale |
|---|---|---|---|---|
| brandt/0 | brandt | 0 | AirdropTowers | 0.8 |
| gen.kessler/0 | gen.kessler | 0 | Vehicles | 0.9 |
| lind/0 | lind | 0 | Engineers | 0.8 |
| reyn/0 | reyn | 0 | Vehicles | 1.1 |
| varro/0 | varro | 0 | Cheap | 0.85 |

Sheet: 06_ai/AI_tuong — Tướng địch (12 dòng, 11 cột)

| id | chien_thuat_ua_thich | chien_dich_deck | chien_dich_supports | noi_tai | can_bang_deck | can_bang_elites | chien_dich_stance | chien_dich_style |
|---|---|---|---|---|---|---|---|---|
| aurel | all_out | heavy_tank;bmpt;railgun_truck;attack_helicopter;long_sam;he… | cruise_missile;airstrike;napalm_strike;sead_strike | gen.aurel |  |  | Attack | aurel |
| brandt | depth |  |  | gen.brandt |  |  |  |  |
| default | balanced |  |  | gen.default |  |  |  |  |
| hung |  | main_battle_tank;heavy_tank;titan_tank;bmpt;ifv;aa_vehicle;… | artillery_barrage;airstrike;cruise_missile | gen.hung |  |  | Attack | aurel |
| kessler | attrition | wheeled_gun;ifv;main_battle_tank;heavy_tank;sam_launcher;fp… | remote_mines;artillery_barrage;smoke_screen | gen.kessler |  |  | Defend | kessler |
| orlov | firepower | mlrs;artillery;mortar_carrier;heavy_rocket_artillery;sam_la… | artillery_barrage;cruise_missile;uav_scan | gen.orlov |  | Artillery | Defend | orlov |
| quaden |  | attack_helicopter;gunship_heli;attack_jet;fighter_jet;strik… | airstrike;sead_strike;napalm_strike | gen.quaden |  | Air | Attack | quaden |
| sen |  | strike_drone;fpv_carrier;lancet_truck;recon_drone;ew_jammer… | uav_scan;sead_strike;repair_drop | gen.sen |  | Drone | Attack | sen |
| thorne | balanced |  |  | gen.thorne |  |  |  |  |
| varga | breakthrough | light_tank;main_battle_tank;heavy_tank;tank_destroyer;ifv;f… | artillery_barrage;airstrike;smoke_screen | gen.varga | armored_bulldozer | Tank;Heavy | Attack | varga |
| venn | dispersal |  |  | gen.venn |  |  |  |  |
| wolff | air_superiority |  |  | gen.wolff |  |  |  |  |

## 13. Trang bị

Trạng thái: Đã áp

Nguồn dữ liệu: 02_phuong_tien/Trang_bi; 02_phuong_tien/Trang_bi_bo; 02_phuong_tien/Trang_bi_dac_tinh; 02_phuong_tien/Trang_bi_mo_dun; 02_phuong_tien/Trang_bi_dong_phu; 11_meta_giao_dien/Trang_bi_hang. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §13. Trang bị.

Mỗi nhánh (Thiết giáp, Xe nhẹ, Pháo binh, Không quân) có 7 ô: Vũ khí, Nạp đạn, Giáp, Quang học, Động cơ, Sửa chữa và Đặc biệt. Một món gồm: **loại đồ** (có dòng ẩn riêng), **chỉ số chính** tăng theo cấp (40% → 100%), **0/1/2/2/2 chỉ số phụ** theo độ hiếm (lăn 60–100%, có thanh chất lượng, tăng ở cấp 5/10/15/20), **một dòng unique** ở Sử thi và Huyền thoại (chọn 1 trong 3 khi ghép lên Sử thi), và **một thương hiệu** (bộ 2 món và 4 món). Ghép 3 món cùng ô cùng độ hiếm để lên bậc. Mỗi chỉ số có trần cho cả bộ.

Thường · cấp tối đa 5Khá · cấp tối đa 10Hiếm · cấp tối đa 15Sử thi · cấp tối đa 20Huyền thoại · cấp tối đa 25

#### Loại đồ (38)

|  | Loại | Ô | Dòng ẩn (Huyền thoại, cấp tối đa) | Thường → Huyền thoại |
|---|---|---|---|---|
|  | **Nòng dài** | Vũ khí | +8% tầm bắn | +2% tầm bắn / +3% tầm bắn / +4% tầm bắn / +6% tầm bắn / +8% tầm bắn |
|  | **Lõi xuyên vonfram** | Vũ khí | +1,0 cấp xuyên | +0,4 cấp xuyên / +0,55 cấp xuyên / +0,7 cấp xuyên / +0,85 cấp xuyên / +1,0 cấp xuyên |
|  | **Thuốc nổ phá mảnh** | Vũ khí | +20% bán kính nổ (không nổ: mạnh hơn với xe nhẹ) | +5% bán kính nổ (không nổ: mạnh hơn với xe nhẹ) / +8% bán kính nổ (không nổ: mạnh hơn với xe nhẹ) / +12% bán kính nổ (không nổ: mạnh hơn với xe nhẹ) / +16% bán kính nổ (không nổ: mạnh hơn với xe nhẹ)… |
|  | **Ngòi nổ cận đích** | Vũ khí | +20% sát thương lên máy bay | +5% sát thương lên máy bay / +8% sát thương lên máy bay / +12% sát thương lên máy bay / +16% sát thương lên máy bay / +20% sát thương lên máy bay |
|  | **Đạn phá boong-ke** | Vũ khí | +24% sát thương lên công trình | +6% sát thương lên công trình / +9% sát thương lên công trình / +13% sát thương lên công trình / +18% sát thương lên công trình / +24% sát thương lên công trình |
|  | **Nòng nặng** đánh đổi | Vũ khí | +12% tầm bắn -7% tốc độ | +0% tầm bắn / +0% tầm bắn / +8% tầm bắn / +10% tầm bắn / +12% tầm bắn |
|  | **Đạn đánh hông** | Vũ khí | +20% sát thương khi bắn trúng hông và đuôi | +5% sát thương khi bắn trúng hông và đuôi / +8% sát thương khi bắn trúng hông và đuôi / +12% sát thương khi bắn trúng hông và đuôi / +16% sát thương khi bắn trúng hông và đuôi / +20% sát thương khi b… |
|  | **Đạn nổ trên không** | Vũ khí | +30% sát thương lên drone; bắn hạ một phần rốc-két, tên lửa và drone nhắm vào nó | +8% sát thương lên drone; bắn hạ một phần rốc-két, tên lửa và drone nhắm vào nó / +12% sát thương lên drone; bắn hạ một phần rốc-két, tên lửa và drone nhắm vào nó / +18% sát thương lên drone; bắn hạ… |
|  | **Nạp đạn băng chuyền** | Nạp đạn | -20% thời gian nạp băng | -5% thời gian nạp băng / -8% thời gian nạp băng / -12% thời gian nạp băng / -16% thời gian nạp băng / -20% thời gian nạp băng |
|  | **Giá đạn mở rộng** | Nạp đạn | +30% sức chứa băng đạn | +10% sức chứa băng đạn / +15% sức chứa băng đạn / +20% sức chứa băng đạn / +25% sức chứa băng đạn / +30% sức chứa băng đạn |
|  | **Tiếp đạn dây** | Nạp đạn | +25% tốc bắn súng phụ | +8% tốc bắn súng phụ / +12% tốc bắn súng phụ / +16% tốc bắn súng phụ / +20% tốc bắn súng phụ / +25% tốc bắn súng phụ |
|  | **Giá phóng loạt** | Nạp đạn | -30% khoảng cách giữa các phát trong loạt | -10% khoảng cách giữa các phát trong loạt / -15% khoảng cách giữa các phát trong loạt / -20% khoảng cách giữa các phát trong loạt / -25% khoảng cách giữa các phát trong loạt / -30% khoảng cách giữa c… |
|  | **Cò nhạy** đánh đổi | Nạp đạn | +15% tốc độ bắn +14% độ tản mát | +0% tốc độ bắn / +0% tốc độ bắn / +10% tốc độ bắn / +12% tốc độ bắn / +15% tốc độ bắn |
|  | **Băng đạn dự phòng** | Nạp đạn | Bệ phóng hết đạn được nạp lại ngay 100% băng, một lần mỗi mạng | Bệ phóng hết đạn được nạp lại ngay 40% băng, một lần mỗi mạng / Bệ phóng hết đạn được nạp lại ngay 55% băng, một lần mỗi mạng / Bệ phóng hết đạn được nạp lại ngay 70% băng, một lần mỗi mạng / Bệ phón… |
|  | **Giáp tổng hợp gắn thêm** | Giáp | -15% sát thương nổ lõm | -4% sát thương nổ lõm / -6% sát thương nổ lõm / -9% sát thương nổ lõm / -12% sát thương nổ lõm / -15% sát thương nổ lõm |
|  | **Lớp lót chống mảnh** | Giáp | -15% sát thương nổ mạnh | -4% sát thương nổ mạnh / -6% sát thương nổ mạnh / -9% sát thương nổ mạnh / -12% sát thương nổ mạnh / -15% sát thương nổ mạnh |
|  | **Thép ốp tăng cường** | Giáp | +1,0 cấp giáp hông và sau | +0,4 cấp giáp hông và sau / +0,55 cấp giáp hông và sau / +0,7 cấp giáp hông và sau / +0,85 cấp giáp hông và sau / +1,0 cấp giáp hông và sau |
|  | **Thân xe chống cháy** | Giáp | -25% sát thương lửa, cháy ngắn hơn | -8% sát thương lửa, cháy ngắn hơn / -12% sát thương lửa, cháy ngắn hơn / -16% sát thương lửa, cháy ngắn hơn / -20% sát thương lửa, cháy ngắn hơn / -25% sát thương lửa, cháy ngắn hơn |
|  | **Buồng lái bọc giáp** | Giáp | +1,0 cấp giáp mọi mặt | +0,4 cấp giáp mọi mặt / +0,55 cấp giáp mọi mặt / +0,7 cấp giáp mọi mặt / +0,85 cấp giáp mọi mặt / +1,0 cấp giáp mọi mặt |
|  | **Tấm giáp nguyên khối** đánh đổi | Giáp | Chỉ số chính: máu, lớn hơn 80% so với các bộ giáp khác; không có dòng phụ -6% tốc độ | 0% / 0% / 0% / 0% / 0% |
|  | **Lớp phủ chống radar** | Giáp | Tên lửa địch phải lại gần hơn 20% mới khóa được | Tên lửa địch phải lại gần hơn 6% mới khóa được / Tên lửa địch phải lại gần hơn 9% mới khóa được / Tên lửa địch phải lại gần hơn 13% mới khóa được / Tên lửa địch phải lại gần hơn 16% mới khóa được / T… |
|  | **Giáp nêm mặt trước** | Giáp | -18% sát thương từ phía trước | -5% sát thương từ phía trước / -8% sát thương từ phía trước / -11% sát thương từ phía trước / -15% sát thương từ phía trước / -18% sát thương từ phía trước |
|  | **Lồng chống rốc-két** | Giáp | -22% sát thương nổ lõm từ rốc-két, tên lửa và drone (không tính nhiệt áp) | -6% sát thương nổ lõm từ rốc-két, tên lửa và drone (không tính nhiệt áp) / -9% sát thương nổ lõm từ rốc-két, tên lửa và drone (không tính nhiệt áp) / -13% sát thương nổ lõm từ rốc-két, tên lửa và dro… |
|  | **Mái che chống pháo** | Giáp | -22% sát thương pháo binh và bom | -6% sát thương pháo binh và bom / -9% sát thương pháo binh và bom / -13% sát thương pháo binh và bom / -17% sát thương pháo binh và bom / -22% sát thương pháo binh và bom |
|  | **Giáp gầm** | Giáp | -18% sát thương nổ lan và mìn (không tính trúng trực tiếp) | -5% sát thương nổ lan và mìn (không tính trúng trực tiếp) / -8% sát thương nổ lan và mìn (không tính trúng trực tiếp) / -11% sát thương nổ lan và mìn (không tính trúng trực tiếp) / -15% sát thương nổ… |
|  | **Hệ truyền động** | Động cơ | +20% tốc độ xoay thân | +5% tốc độ xoay thân / +8% tốc độ xoay thân / +12% tốc độ xoay thân / +16% tốc độ xoay thân / +20% tốc độ xoay thân |
|  | **Hộp số hành quân** | Động cơ | +20% tốc độ khi không thấy địch | +5% tốc độ khi không thấy địch / +8% tốc độ khi không thấy địch / +12% tốc độ khi không thấy địch / +16% tốc độ khi không thấy địch / +20% tốc độ khi không thấy địch |
|  | **Động cơ độ quá mức** đánh đổi | Động cơ | +15% tốc độ -6% máu | +0% tốc độ / +0% tốc độ / +10% tốc độ / +12% tốc độ / +15% tốc độ |
|  | **Hộp số lùi** | Động cơ | +40% tốc độ lùi; bị áp sát thì lùi lại mà vẫn giữ mặt trước hướng về địch | +15% tốc độ lùi; bị áp sát thì lùi lại mà vẫn giữ mặt trước hướng về địch / +20% tốc độ lùi; bị áp sát thì lùi lại mà vẫn giữ mặt trước hướng về địch / +28% tốc độ lùi; bị áp sát thì lùi lại mà vẫn g… |
|  | **Hộp dụng cụ** | Sửa chữa | Bắt đầu tự sửa sớm hơn 3 giây sau khi trúng đạn | Bắt đầu tự sửa sớm hơn 1 giây sau khi trúng đạn / Bắt đầu tự sửa sớm hơn 1,5 giây sau khi trúng đạn / Bắt đầu tự sửa sớm hơn 2 giây sau khi trúng đạn / Bắt đầu tự sửa sớm hơn 2,5 giây sau khi trúng đ… |
|  | **Huấn luyện kíp lái** | Sửa chữa | -15% hồi chiêu kỹ năng và mô-đun | -4% hồi chiêu kỹ năng và mô-đun / -6% hồi chiêu kỹ năng và mô-đun / -9% hồi chiêu kỹ năng và mô-đun / -12% hồi chiêu kỹ năng và mô-đun / -15% hồi chiêu kỹ năng và mô-đun |
|  | **Bình chữa cháy** | Sửa chữa | -42% thời gian cháy, chậm và choáng | -10% thời gian cháy, chậm và choáng / -18% thời gian cháy, chậm và choáng / -26% thời gian cháy, chậm và choáng / -34% thời gian cháy, chậm và choáng / -42% thời gian cháy, chậm và choáng |
|  | **Máy đo xa la-de** | Quang học | -25% tản mát ở tầm xa | -8% tản mát ở tầm xa / -12% tản mát ở tầm xa / -16% tản mát ở tầm xa / -20% tản mát ở tầm xa / -25% tản mát ở tầm xa |
|  | **Bộ ổn định pháo** | Quang học | -30% tản mát khi di chuyển | -10% tản mát khi di chuyển / -15% tản mát khi di chuyển / -20% tản mát khi di chuyển / -25% tản mát khi di chuyển / -30% tản mát khi di chuyển |
|  | **Kính tiềm vọng chỉ huy** | Quang học | +20% tầm nhìn khi đứng yên | +5% tầm nhìn khi đứng yên / +8% tầm nhìn khi đứng yên / +12% tầm nhìn khi đứng yên / +16% tầm nhìn khi đứng yên / +20% tầm nhìn khi đứng yên |
|  | **Lưới ngụy trang** | Quang học | Đứng yên: địch phải lại gần hơn 18% mới phát hiện | Đứng yên: địch phải lại gần hơn 5% mới phát hiện / Đứng yên: địch phải lại gần hơn 8% mới phát hiện / Đứng yên: địch phải lại gần hơn 11% mới phát hiện / Đứng yên: địch phải lại gần hơn 15% mới phát… |
|  | **Trạm chuyển tiếp tín hiệu** | Quang học | +30% tốc độ chiếm cứ điểm | +10% tốc độ chiếm cứ điểm / +15% tốc độ chiếm cứ điểm / +20% tốc độ chiếm cứ điểm / +25% tốc độ chiếm cứ điểm / +30% tốc độ chiếm cứ điểm |
|  | **Cảnh báo la-de** | Quang học | Khi bị tên lửa chống tăng khóa: thả khói 8 m (mỗi 20 giây) | Khi bị tên lửa chống tăng khóa: thả khói 6 m (mỗi 20 giây) / Khi bị tên lửa chống tăng khóa: thả khói 6,5 m (mỗi 20 giây) / Khi bị tên lửa chống tăng khóa: thả khói 7 m (mỗi 20 giây) / Khi bị tên lửa… |

#### Dòng unique (45)

| Dòng | Ô | Hiệu ứng |
|---|---|---|
| **Nạp kép** | Vũ khí | **Sử thi:** Loạt từ 3 viên: bắn thêm một viên và +15% sát thương cả loạt; vũ khí 1–2 viên: +15% sát thương mỗi phát. **Huyền thoại:** Loạt từ 3 viên: bắn thêm một viên và +20% sát thương cả loạt; vũ… |
| **Đạn cháy** | Vũ khí | **Sử thi:** Trúng đích gây cháy bằng 18% sát thương trong 4 giây; mục tiêu đang cháy hồi máu chậm một nửa. **Huyền thoại:** Trúng đích gây cháy bằng 25% sát thương trong 4 giây; mục tiêu đang cháy hồ… |
| **Đạn nảy** | Vũ khí | **Sử thi:** Phát trúng nảy sang kẻ địch gần nhất trong 8 m với 35% sát thương (pháo chậm mỗi phát, súng nhanh vài phát một lần). **Huyền thoại:** Phát trúng nảy sang kẻ địch gần nhất trong 10 m với 5… |
| **Đầu đạn chùm** | Vũ khí | **Sử thi:** 2 viên đầu mỗi loạt đạn pháo, rốc-két hoặc bom rải 5 quả bom con nơi chạm đất. **Huyền thoại:** 2 viên đầu mỗi loạt đạn pháo, rốc-két hoặc bom rải 8 quả bom con nơi chạm đất. |
| **Đạn xé giáp** | Vũ khí | **Sử thi:** Trúng đích khiến mục tiêu nhận thêm 3% sát thương từ mọi nguồn, tối đa 5 lớp (pháo chậm cộng nhiều lớp một lần). **Huyền thoại:** Trúng đích khiến mục tiêu nhận thêm 4% sát thương từ mọi… |
| **Loạt mở màn** | Vũ khí | **Sử thi:** Các phát bắn trong 1,5 giây đầu vào mục tiêu mới (ít nhất phát đầu) gây thêm 35% sát thương. **Huyền thoại:** Các phát bắn trong 1,5 giây đầu vào mục tiêu mới (ít nhất phát đầu) gây thêm… |
| **Pháo tích đà** | Vũ khí | **Sử thi:** Mỗi phát trúng liên tiếp cùng mục tiêu thêm 5% sát thương, tối đa 5 lần (pháo chậm lên nhanh hơn). **Huyền thoại:** Mỗi phát trúng liên tiếp cùng mục tiêu thêm 7% sát thương, tối đa 5 lần… |
| **Đao phủ** | Vũ khí | **Sử thi:** Thêm 40% sát thương lên mục tiêu dưới 30% máu. **Huyền thoại:** Thêm 60% sát thương lên mục tiêu dưới 30% máu. |
| **Đầu nổ kép** | Vũ khí | **Sử thi:** Rốc-két và tên lửa xuyên qua APS, giáp phản ứng và khiên, gây thêm 10% lên giáp cấp 3–4. **Huyền thoại:** Rốc-két và tên lửa xuyên qua APS, giáp phản ứng và khiên, gây thêm 15% lên giáp c… |
| **Đạn áp chế** | Vũ khí | **Sử thi:** Trúng đích làm chậm mục tiêu 15% trong 2 giây (một nửa với máy bay). **Huyền thoại:** Trúng đích làm chậm mục tiêu 25% trong 2 giây (một nửa với máy bay). |
| **Hỏa lực chế áp** | Vũ khí | **Sử thi:** Trúng đích làm mục tiêu giảm 10% tốc độ bắn trong 3 giây (lâu hơn với pháo chậm). **Huyền thoại:** Trúng đích làm mục tiêu giảm 15% tốc độ bắn trong 3 giây (lâu hơn với pháo chậm). |
| **Kíp ẩn thân** | Nạp đạn | **Sử thi:** Đứng yên 2 giây: +10% tốc độ bắn. **Huyền thoại:** Đứng yên 2 giây: +15% tốc độ bắn. |
| **Hạ là nạp** | Nạp đạn | **Sử thi:** Mỗi lần hạ địch rút ngắn tối đa 2 giây nạp đạn của pháo chính, nạp một viên nếu hết băng và +25% tốc độ bắn trong một lúc. **Huyền thoại:** Mỗi lần hạ địch rút ngắn tối đa 2 giây nạp đạn… |
| **Phản ứng nhanh** | Nạp đạn | **Sử thi:** Khi trúng đạn: tốc độ bắn ×1,4 trong 4 giây (mỗi 18 giây). **Huyền thoại:** Khi trúng đạn: tốc độ bắn ×1,6 trong 4 giây (mỗi 14 giây). |
| **Buồng quá áp** | Nạp đạn | **Sử thi:** Mỗi phát thứ 5 mạnh hơn 50% và nổ lan 4 m. **Huyền thoại:** Mỗi phát thứ 4 mạnh hơn 50% và nổ lan 4 m. |
| **Thay băng nóng** | Nạp đạn | **Sử thi:** Nạp băng cả khi di chuyển, nhanh hơn 25%. **Huyền thoại:** Nạp băng cả khi di chuyển, nhanh hơn 40%. |
| **Giá súng phòng không** | Nạp đạn | **Sử thi:** Súng máy phụ bắn được máy bay, với 60% sát thương. **Huyền thoại:** Súng máy phụ bắn được máy bay, với 80% sát thương. |
| **Trả thù** | Nạp đạn | **Sử thi:** Đồng minh bị hạ trong 15 m: +15% sát thương trong 5 giây (không cộng dồn). **Huyền thoại:** Đồng minh bị hạ trong 15 m: +20% sát thương trong 5 giây (không cộng dồn). |
| **Khiên Aegis** | Giáp | **Sử thi:** Mỗi 20 giây, một lớp khiên hấp thụ 10% máu tối đa. **Huyền thoại:** Mỗi 16 giây, một lớp khiên hấp thụ 15% máu tối đa. |
| **Bất khuất** | Giáp | **Sử thi:** Mỗi mạng một lần, đòn kết liễu để lại 1 máu và bất tử 1,5 giây. **Huyền thoại:** Mỗi mạng một lần, đòn kết liễu để lại 1 máu và bất tử 2,5 giây. |
| **Liên kết hộ vệ** | Giáp | **Sử thi:** Gánh 15% sát thương thay cho đồng minh xe nhẹ trong 10 m. **Huyền thoại:** Gánh 25% sát thương thay cho đồng minh xe nhẹ trong 10 m. |
| **Vương miện bóng tối** | Giáp | **Sử thi:** Mỗi xe bị hạ trong 25 m: +3% sát thương (5 lần) và hồi 2% máu. **Huyền thoại:** Mỗi xe bị hạ trong 25 m: +4% sát thương (5 lần) và hồi 3% máu. |
| **Giáp thích ứng** | Giáp | **Sử thi:** Mỗi phát trúng một loại sát thương cho 5% kháng loại đó trong 6 giây, cộng dồn 4 lần. **Huyền thoại:** Mỗi phát trúng một loại sát thương cho 6% kháng loại đó trong 6 giây, cộng dồn 4 lần. |
| **Khối giáp phản ứng** | Giáp | **Sử thi:** 3 khối giáp giảm nửa phát nổ lõm (không giảm động năng); hồi lại một khối mỗi 20 giây. **Huyền thoại:** 4 khối giáp giảm nửa phát nổ lõm (không giảm động năng); hồi lại một khối mỗi 15 gi… |
| **Lớp giáp hy sinh** | Giáp | **Sử thi:** 20% máu tối đa đầu tiên mất đi mỗi mạng được giảm một nửa. **Huyền thoại:** 30% máu tối đa đầu tiên mất đi mỗi mạng được giảm một nửa. |
| **Giáp nghiêng** | Giáp | **Sử thi:** Mỗi phát động năng hoặc nổ lõm thứ 6 bị bật ra. **Huyền thoại:** Mỗi phát động năng hoặc nổ lõm thứ 5 bị bật ra. |
| **Neo công thành** | Giáp | **Sử thi:** Đứng yên 3 giây: -15% sát thương nhận và +8% tầm bắn; mất 1 giây để rời đi. **Huyền thoại:** Đứng yên 3 giây: -20% sát thương nhận và +12% tầm bắn; mất 1 giây để rời đi. |
| **Bứt tốc** | Động cơ | **Sử thi:** Khi trúng đạn: tốc độ ×1,6 và bắn nhanh hơn trong 3 giây (mỗi 25 giây). **Huyền thoại:** Khi trúng đạn: tốc độ ×1,8 và bắn nhanh hơn trong 3 giây (mỗi 18 giây). |
| **Bắn rồi chạy** | Động cơ | **Sử thi:** Phát đầu sau khi dừng: +40% sát thương; sau khi bắn, +15% tốc độ trong 2 giây. **Huyền thoại:** Phát đầu sau khi dừng: +60% sát thương; sau khi bắn, +25% tốc độ trong 2 giây. |
| **Triển khai nhanh** | Động cơ | **Sử thi:** 10 giây đầu sau khi vào trận: +40% tốc độ và -20% sát thương nhận. **Huyền thoại:** 15 giây đầu sau khi vào trận: +40% tốc độ và -20% sát thương nhận. |
| **Bình xăng dễ nổ** | Động cơ | **Sử thi:** Khi bị hạ, phát nổ bằng 30% máu trong 8 m, chỉ gây hại cho địch. **Huyền thoại:** Khi bị hạ, phát nổ bằng 45% máu trong 10 m, chỉ gây hại cho địch. |
| **Đốt sau dự phòng** | Động cơ | **Sử thi:** Mỗi mạng một lần khi dưới 40% máu: +50% tốc độ trong 4 giây, kèm mồi nhiệt. **Huyền thoại:** Mỗi mạng một lần khi dưới 40% máu: +70% tốc độ trong 4 giây, kèm mồi nhiệt. |
| **Chặn hậu** | Động cơ | **Sử thi:** Khi di chuyển ra xa địch: nhận ít hơn 15% sát thương. **Huyền thoại:** Khi di chuyển ra xa địch: nhận ít hơn 20% sát thương. |
| **Thợ máy dã chiến** | Sửa chữa | **Sử thi:** Đồng minh trong 12 m khi ngoài giao tranh hồi 0,6% máu mỗi giây. **Huyền thoại:** Đồng minh trong 15 m khi ngoài giao tranh hồi 1,0% máu mỗi giây. |
| **Bộ sửa khẩn cấp** | Sửa chữa | **Sử thi:** Dưới 40% máu, hồi 20% trong 5 giây (mỗi 30 giây). **Huyền thoại:** Dưới 40% máu, hồi 30% trong 5 giây (mỗi 30 giây). |
| **Thợ hàn chiến trường** | Sửa chữa | **Sử thi:** Tự sửa cả khi đang bị bắn, ở mức 40%. **Huyền thoại:** Tự sửa cả khi đang bị bắn, ở mức 60%. |
| **Đội thu hồi** | Sửa chữa | **Sử thi:** Mỗi lần hạ địch hồi 8% máu, đồng minh trong 10 m hồi một nửa. **Huyền thoại:** Mỗi lần hạ địch hồi 12% máu, đồng minh trong 10 m hồi một nửa. |
| **Xe chở đạn** | Sửa chữa | **Sử thi:** Đồng minh trong 12 m nạp băng nhanh hơn 30%, kể cả khi di chuyển. **Huyền thoại:** Đồng minh trong 16 m nạp băng nhanh hơn 50%, kể cả khi di chuyển. |
| **Kiểm soát hư hại** | Sửa chữa | **Sử thi:** Xóa cháy, chậm, choáng và xé giáp, rồi miễn nhiễm 2 giây (mỗi 15 giây). **Huyền thoại:** Xóa cháy, chậm, choáng và xé giáp, rồi miễn nhiễm 2 giây (mỗi 10 giây). |
| **Kính ảnh nhiệt** | Quang học | **Sử thi:** Nhìn xuyên khói tới 60% tầm nhìn. **Huyền thoại:** Nhìn xuyên khói tới 100% tầm nhìn. |
| **Chỉ thị la-de** | Quang học | **Sử thi:** Đánh dấu mục tiêu trúng đạn 4 giây: đồng minh gây thêm 8% và pháo binh bắn tới xa hơn. **Huyền thoại:** Đánh dấu mục tiêu trúng đạn 6 giây: đồng minh gây thêm 12% và pháo binh bắn tới xa… |
| **Chế độ ngụy trang** | Quang học | **Sử thi:** Đứng yên và im lặng 4 giây: ẩn mình ngoài 8 m; phát đầu từ chỗ nấp gây thêm 25%. **Huyền thoại:** Đứng yên và im lặng 3 giây: ẩn mình ngoài 8 m; phát đầu từ chỗ nấp gây thêm 40%. |
| **Radar phản pháo** | Quang học | **Sử thi:** Pháo địch khai hỏa trong 80 m bị lộ 5 giây, và pháo binh gây thêm 15% lên nó. **Huyền thoại:** Pháo địch khai hỏa trong 100 m bị lộ 8 giây, và pháo binh gây thêm 25% lên nó. |
| **Gây nhiễu điện tử** | Quang học | **Sử thi:** Mỗi 15 giây, đạn dẫn đường nhắm vào đồng minh trong 12 m bị trượt trong 2 giây. **Huyền thoại:** Mỗi 12 giây, đạn dẫn đường nhắm vào đồng minh trong 16 m bị trượt trong 3 giây. |
| **Máy tính điều khiển hỏa lực** | Quang học | **Sử thi:** Đạn không dẫn đường đón đầu mục tiêu đang chạy, giảm 50% tản mát với chúng. **Huyền thoại:** Đạn không dẫn đường đón đầu mục tiêu đang chạy, giảm 75% tản mát với chúng. |

#### Module đặc biệt (14)

|  | Module | Hiệu ứng (Sử thi/Huyền thoại) |
|---|---|---|
|  | **Giáp phản ứng nổ** | Nhận ít hơn 55% sát thương nổ lõm (không giảm động năng; đầu nổ kép xuyên qua). |
|  | **Tự sửa chữa** | Hồi 1,8% máu mỗi giây khi vài giây không trúng đạn. |
|  | **Kíp lái kỳ cựu** | +12% sát thương và tốc độ bắn. |
|  | **Ống phóng khói** | Thả màn khói 10 m lần đầu tụt dưới nửa máu. Thả lần nữa khi dưới một phần tư máu. |
|  | **Hệ thống Trophy APS** | Bắn hạ tên lửa, drone và rốc-két bay tới: 2 lượt, mỗi lượt hồi sau 20 giây. |
|  | **Mồi bẫy nhiệt** | Khi bị phóng tên lửa, thả mồi nhiệt trong 4 giây (mỗi 18 giây). |
|  | **Drone hộ tống** | Mỗi 20 giây phóng 2 drone cảm tử vào kẻ địch gần nhất. |
|  | **Đầu nổ EMP** | Khi bị hạ, làm choáng xe mặt đất địch trong 14 m trong 3 giây. |
|  | **Máy rải mìn** | Khi di chuyển, thả một quả mìn mỗi 15 giây, tối đa 3 quả cùng lúc. |
|  | **Kẻ trục lợi chiến tranh** | Mỗi lần hạ địch hoàn thêm 80% CP. |
|  | **Kèn tập hợp** | Đồng minh trong 15 m gây thêm 10% sát thương (không cộng dồn). |
|  | **Vòm Aegis** | Mỗi mạng một lần, khi 3 đồng minh gần đó bị bắn, tất cả bất tử trong 3 giây. |
|  | **Bệ phóng mồi nhử** | Khi bị nhắm bằng tên lửa hoặc đạn pháo, mồi nhử hút chúng đi trong 6 giây (mỗi 25 giây). |
|  | **Pháo kích vệ tinh** | Mỗi 35 giây gọi 5 quả cối nhẹ vào mục tiêu của nó. |

#### Thương hiệu / bộ (13)

| Thương hiệu | Thưởng bộ 2 và bộ 4 |
|---|---|
| **Xưởng Ironclad** | 2: +6% máu · 4: Thành lũy: Đứng yên 2 giây: -15% sát thương nhận, và địch gần đó ưu tiên bắn nó. |
| **Kestrel Dynamics** | 2: +5% tốc độ · 4: Đánh và chạy: +20% tốc độ trong 2 giây sau mỗi phát bắn; đạn không dẫn đường bắn vào nó khi đang chạy +50% tản mát. |
| **Vulcan Arms** | 2: +25% sát thương cháy · 4: Bão lửa: Địch đang cháy nhận thêm 10% sát thương, và khi chết lửa lan sang kẻ địch trong 6 m. |
| **Longbow Ordnance** | 2: +5% tầm bắn · 4: Đòn tầm xa: +15% sát thương lên mục tiêu xa hơn 70% tầm bắn. |
| **Aegis Systems** | 2: -5% sát thương nhận vào · 4: Khiên chia sẻ: Mỗi 25 giây, khiên 12% cho đồng minh yếu nhất trong 12 m. |
| **Stormfront Aviation** | 2: -10% sát thương mảnh · 4: Càn quét: Mỗi loạt thứ 4 bắn hai lần; thả mồi nhiệt mỗi 30 giây. |
| **Hivemind Robotics** | 2: +15% sức mạnh drone, mìn và đơn vị gọi thêm · 4: Bầy đàn: Mỗi lần hạ địch phóng một drone cảm tử vào kẻ địch gần nhất (tối đa một chiếc mỗi 10 giây). |
| **Hậu cần Quartermaster** | 2: +10% lượng hồi máu nhận được · 4: Quyền thu hồi: Hạ địch hoàn thêm 20% CP, và hoàn lại 10% giá khi nó bị hạ. |
| **Spectre Electronics** | 2: +8% tầm nhìn · 4: Lưới bóng ma: +15% sát thương khi trong khói hoặc đang ẩn; tên lửa đầu tiên nhắm vào nó mỗi mạng bị mất khóa. |
| **Hammerfall Munitions** | 2: +8% sát thương lên công trình · 4: Đạn hạng nặng: Mỗi phát thứ 5 gây thêm 100% và nổ lan 4 m (mỗi phát thứ 3 nếu có Buồng quá áp). |
| **Phoenix Recovery** | 2: +10% lượng hồi máu nhận được · 4: Khiên tái sinh: Lượng hồi máu vượt quá máu tối đa thành khiên, tối đa 10% máu, tồn tại 8 giây. |
| **Wolfpack Tactics** | 2: Săn theo bầy: +4% sát thương cho mỗi đồng minh trong 15 m, tối đa 3. · 4: Dồn hỏa lực: Khi từ 3 xe ta trở lên cùng bắn một mục tiêu: +15% tốc độ bắn. |
| **Bulwark Engineering** | 2: +10% máu · 4: Ụ súng dã chiến: Tháp bị phá để lại một ụ súng máy tạm trong 20 giây. (tính số món trên toàn căn cứ) |

Sheet: 02_phuong_tien/Trang_bi — Trang bị: loại cơ bản (38 dòng, 16 cột)

| id | ten_vi | flat | implicit2 | implicit_stat | main_scale | min_rarity | no_subs | penalty | penalty_top |
|---|---|---|---|---|---|---|---|---|---|
| airburst_rounds | Đạn nổ trên không |  |  | DamageVsDrone |  |  |  |  |  |
| applique_steel | Thép ốp tăng cường |  |  | ArmourSide |  |  |  |  |  |
| armoured_tub | Buồng lái bọc giáp |  |  | ArmourAll |  |  |  |  |  |
| belt_feed | Tiếp đạn dây |  |  | SecondaryFireRate |  |  |  |  |  |
| bunker_buster | Đạn phá boong-ke |  |  | DamageVsStructure |  |  |  |  |  |
| camouflage_net | Lưới ngụy trang |  |  | Camouflage |  |  |  |  |  |
| carousel_autoloader | Nạp đạn băng chuyền |  |  | MagazineReload |  |  |  |  |  |
| commanders_periscope | Kính tiềm vọng chỉ huy |  |  | StillVision |  |  |  |  |  |
| composite_addon | Giáp tổng hợp gắn thêm |  |  | ResistShapedCharge |  |  |  |  |  |
| crew_drills | Huấn luyện kíp lái |  |  | Cooldowns |  |  |  |  |  |
| drivetrain | Hệ truyền động |  | TurretRate | TurnRate |  |  |  |  |  |
| extended_ammo_rack | Giá đạn mở rộng |  |  | Magazine |  |  |  |  |  |
| fire_extinguisher | Bình chữa cháy |  |  | StatusDuration |  |  |  |  |  |
| fire_retardant_hull | Thân xe chống cháy |  |  | ResistFire |  |  |  |  |  |
| flanking_rounds | Đạn đánh hông |  |  | DamageFlank |  |  |  |  |  |
| frontal_wedge | Giáp nêm mặt trước |  |  | ResistFrontal |  |  |  |  |  |
| gun_stabiliser | Bộ ổn định pháo |  |  | SpreadMoving |  |  |  |  |  |
| hair_trigger | Cò nhạy |  |  | FireRate |  | 2 |  | Spread | 0;0;-0.1;-0.12;-0.14 |
| he_frag_filler | Thuốc nổ phá mảnh |  |  | Splash |  |  |  |  |  |
| heavy_barrel | Nòng nặng |  |  | Range |  | 2 |  | Speed | 0;0;-0.05;-0.06;-0.07 |
| laser_rangefinder | Máy đo xa la-de |  |  | SpreadLong |  |  |  |  |  |
| laser_warning | Cảnh báo la-de | TRUE |  | LaserWarning |  |  |  |  |  |
| long_barrel | Nòng dài |  |  | Range |  |  |  |  |  |
| monolith_plate | Tấm giáp nguyên khối |  |  | Count | 1.8 | 2 | TRUE | Speed | 0;0;-0.04;-0.05;-0.06 |
| overhead_screen | Mái che chống pháo |  |  | ResistIndirect |  |  |  |  |  |
| overtuned_engine | Động cơ độ quá mức |  |  | Speed |  | 2 |  | Health | 0;0;-0.04;-0.05;-0.06 |
| proximity_fuze | Ngòi nổ cận đích |  |  | DamageVsAir |  |  |  |  |  |
| radar_absorbent_coating | Lớp phủ chống radar |  |  | LockRange |  |  |  |  |  |
| reverse_gearbox | Hộp số lùi |  |  | ReverseSpeed |  |  |  |  |  |
| salvo_rack | Giá phóng loạt |  |  | SalvoInterval |  |  |  |  |  |
| signal_relay | Trạm chuyển tiếp tín hiệu |  | Vision | CaptureRate |  |  |  |  |  |
| slat_cage | Lồng chống rốc-két |  |  | ResistRocket |  |  |  |  |  |
| spall_liner | Lớp lót chống mảnh |  |  | ResistHighExplosive |  |  |  |  |  |
| spare_magazine | Băng đạn dự phòng | TRUE |  | SpareMagazine |  |  |  |  |  |
| toolbox | Hộp dụng cụ |  |  | RegenDelay |  |  |  |  |  |
| transit_gearbox | Hộp số hành quân |  |  | TransitSpeed |  |  |  |  |  |
| tungsten_penetrator | Lõi xuyên vonfram |  |  | Penetration |  |  |  |  |  |
| underbelly_armor | Giáp gầm |  |  | ResistBlast |  |  |  |  |  |

*in 10 / 16 cột; 4 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 02_phuong_tien/Trang_bi_bo — Trang bị: bộ (brand) (13 dòng, 16 cột)

| id | four_piece_arg0 | four_piece_arg1 | four_piece_arg2 | four_piece_arg3 | index | stat | tower_only | two_piece_arg0 | two_piece_arg1 |
|---|---|---|---|---|---|---|---|---|---|
| aegis | SetSharedShield | 0.12 | 25 | 12 | 5 | DamageTaken |  |  |  |
| bulwark | SetBulwarkPost | 20 |  |  | BulwarkBrand | Health | TRUE |  |  |
| hammerfall | SetHeavyRound | 5 | 1 |  | 10 | DamageVsStructure |  |  |  |
| hivemind | SetSwarm | 10 |  |  | 7 | SummonPower |  |  |  |
| ironclad | SetBulwark | 0.15 |  |  | 1 | Health |  |  |  |
| kestrel | SetHitAndRun | 0.2 | 0.5 |  | 2 | Speed |  |  |  |
| longbow | SetDeepStrike | 0.15 |  |  | 4 | Range |  |  |  |
| phoenix | SetPhoenix | 0.1 | 8 |  | 11 | RepairReceived |  |  |  |
| quartermaster | SetSalvageRights | 0.2 | 0.1 |  | 8 | RepairReceived |  |  |  |
| spectre | SetGhostNet | 0.15 |  |  | 9 | Vision |  |  |  |
| stormfront | SetStrafingRun | 4 | 30 |  | 6 | ResistFragmentation |  |  |  |
| vulcan | SetFirestorm | 0.1 | 6 |  | 3 | BurnDamage |  |  |  |
| wolfpack | SetPackFocus | 0.15 |  |  | 12 | Count |  | SetPackHunt | 0.04 |

*in 10 / 16 cột; 3 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 02_phuong_tien/Trang_bi_dac_tinh — Trang bị: đặc tính (45 dòng, 8 cột)

| id | ten_vi | branches | epic | legendary | slot |
|---|---|---|---|---|---|
| AblativeLayer | Lớp giáp hy sinh | Any | 0.2 | 0.3 | Armor |
| AdaptivePlating | Giáp thích ứng | Any | 0.05 | 0.06 | Armor |
| AegisBarrier | Khiên Aegis | Any | 0.1;20 | 0.15;16 | Armor |
| AfterburnerReserve | Đốt sau dự phòng | Flying | 0.5 | 0.7 | Engine |
| AmmoCarrier | Xe chở đạn | Any | 0.3;12 | 0.5;16 | Repair |
| AngledGlacis | Giáp nghiêng | Ground | 6 | 5 | Armor |
| ClusterWarhead | Đầu đạn chùm | Lobs | 5 | 8 | Weapon |
| CombatWelder | Thợ hàn chiến trường | Any | 0.4 | 0.6 | Repair |
| CounterBatteryRadar | Radar phản pháo | Any | 0.15;80;5 | 0.25;100;8 | Optics |
| DamageControl | Kiểm soát hư hại | Any | 15 | 10 | Repair |
| DarkCrown | Vương miện bóng tối | Any | 0.03;0.02 | 0.04;0.03 | Armor |
| EmergencyRepairKit | Bộ sửa khẩn cấp | Any | 0.2 | 0.3 | Repair |
| EwJammer | Gây nhiễu điện tử | Any | 2;15;12 | 3;12;16 | Optics |
| Executioner | Đao phủ | Armed | 0.4 | 0.6 | Weapon |
| FieldMechanics | Thợ máy dã chiến | Any | 0.006;12 | 0.01;15 | Repair |

*15 / 45 dòng đầu: xem sheet 02_phuong_tien/Trang_bi_dac_tinh.*

Sheet: 02_phuong_tien/Trang_bi_mo_dun — Trang bị: mô-đun đặc biệt (14 dòng, 9 cột)

| id | epic | epic2 | legendary | legendary2 | need |
|---|---|---|---|---|---|
| AegisDome | 2 |  | 3 |  | Any |
| AutoRepair | 0.012 |  | 0.018 |  | Any |
| DecoyLauncher | 4 | 35 | 6 | 25 | Ground |
| DroneEscort | 1 | 25 | 2 | 20 | Any |
| EmpPayload | 2 | 10 | 3 | 14 | Any |
| FlareDispenser | 3 | 25 | 4 | 18 | Flying/Flares |
| MineDispenser | 2 | 20 | 3 | 15 | Ground |
| RallyHorn | 0.06 | 12 | 0.1 | 15 | Any |
| ReactiveArmor | 0.4 |  | 0.55 |  | Ground |
| SmokeDischarger | 8 | 0 | 10 | 1 | Ground |
| TrophyAps | 1 | 25 | 2 | 20 | Ground/ApsMount |
| UplinkBarrage | 3 | 45 | 5 | 35 | HitsGround |
| VeteranCrew | 0.08 |  | 0.12 |  | Armed |
| WarProfiteer | 0.5 |  | 0.8 |  | Armed |

Sheet: 02_phuong_tien/Trang_bi_dong_phu — Trang bị: dòng phụ (23 dòng, 7 cột)

| id | slots | values | weight |
|---|---|---|---|
| CaptureRate | Engine;Optics | 0.05;0.08;0.1;0.12 |  |
| Cooldowns | Repair;Optics | 0.03;0.05;0.07;0.09 |  |
| Damage | Loader;Optics | 0.015;0.02;0.03;0.04 |  |
| DamageVsAir | Weapon;Loader;Optics | 0.04;0.05;0.06;0.08 |  |
| DamageVsHeavy | Weapon;Loader;Optics | 0.03;0.04;0.05;0.06 |  |
| DamageVsLight | Weapon;Loader;Optics | 0.03;0.04;0.05;0.06 |  |
| DamageVsStructure | Weapon;Loader | 0.04;0.06;0.08;0.1 |  |
| FireRate | Weapon | 0.015;0.02;0.03;0.04 |  |
| Health | Armor;Repair;Engine | 0.02;0.03;0.04;0.05 |  |
| Magazine | Loader | 0.05;0.08;0.1;0.12 |  |
| MagazineReload | Loader;Repair | 0.04;0.06;0.08;0.1 |  |
| ProjectileSpeed | Weapon;Loader | 0.04;0.06;0.08;0.1 |  |
| Range | Weapon;Optics | 0.02;0.025;0.03;0.04 |  |
| Regen | Repair;Armor | 0.001;0.0015;0.002;0.0025 |  |
| ResistFire | Armor | 0.03;0.04;0.06;0.08 | 0.2 |
| ResistFragmentation | Armor | 0.03;0.04;0.06;0.08 | 0.2 |
| ResistHighExplosive | Armor | 0.03;0.04;0.06;0.08 | 0.2 |
| ResistKinetic | Armor | 0.03;0.04;0.06;0.08 | 0.2 |
| ResistShapedCharge | Armor | 0.03;0.04;0.06;0.08 | 0.2 |
| Speed | Engine;Armor | 0.015;0.02;0.03;0.04 |  |
| Spread | Weapon;Optics | 0.04;0.06;0.08;0.1 |  |
| TurretRate | Engine;Optics | 0.05;0.08;0.1;0.12 |  |
| Vision | Optics;Engine | 0.03;0.04;0.05;0.06 |  |

Sheet: 11_meta_giao_dien/Trang_bi_hang — Trang bị theo độ hiếm (27 dòng, 11 cột)

| id | bang | chi_so | gia_tri | gia_tri_0 | gia_tri_1 | gia_tri_2 | gia_tri_3 | gia_tri_4 |
|---|---|---|---|---|---|---|---|---|
| Cap/0 | Cap | 0 | 0.25 |  |  |  |  |  |
| Cap/1 | Cap | 1 | 0.15 |  |  |  |  |  |
| Cap/2 | Cap | 2 | 0.25 |  |  |  |  |  |
| Cap/3 | Cap | 3 | 0.25 |  |  |  |  |  |
| Cap/4 | Cap | 4 | 0.15 |  |  |  |  |  |
| Cap/5 | Cap | 5 | 0.02 |  |  |  |  |  |
| GoldGuaranteed/0 | GoldGuaranteed | 0 | 0 |  |  |  |  |  |
| GoldGuaranteed/1 | GoldGuaranteed | 1 | 0 |  |  |  |  |  |
| GoldGuaranteed/2 | GoldGuaranteed | 2 | 0.81 |  |  |  |  |  |
| GoldGuaranteed/3 | GoldGuaranteed | 3 | 0.16 |  |  |  |  |  |
| GoldGuaranteed/4 | GoldGuaranteed | 4 | 0.03 |  |  |  |  |  |
| LegendaryGuaranteed/0 | LegendaryGuaranteed | 0 | 0 |  |  |  |  |  |
| LegendaryGuaranteed/1 | LegendaryGuaranteed | 1 | 0 |  |  |  |  |  |
| LegendaryGuaranteed/2 | LegendaryGuaranteed | 2 | 0 |  |  |  |  |  |
| LegendaryGuaranteed/3 | LegendaryGuaranteed | 3 | 0.8 |  |  |  |  |  |
| LegendaryGuaranteed/4 | LegendaryGuaranteed | 4 | 0.2 |  |  |  |  |  |
| LevelCap/0 | LevelCap | 0 | 5 |  |  |  |  |  |
| LevelCap/1 | LevelCap | 1 | 10 |  |  |  |  |  |
| LevelCap/2 | LevelCap | 2 | 15 |  |  |  |  |  |
| LevelCap/3 | LevelCap | 3 | 20 |  |  |  |  |  |
| LevelCap/4 | LevelCap | 4 | 25 |  |  |  |  |  |
| Top/0 | Top | 0 |  | 0.03 | 0.05 | 0.08 | 0.11 | 0.14 |
| Top/1 | Top | 1 |  | 0.03 | 0.05 | 0.08 | 0.11 | 0.14 |
| Top/2 | Top | 2 |  | 0.03 | 0.05 | 0.08 | 0.11 | 0.14 |
| Top/3 | Top | 3 |  | 0.03 | 0.05 | 0.08 | 0.11 | 0.14 |
| Top/4 | Top | 4 |  | 0.02 | 0.035 | 0.05 | 0.065 | 0.08 |
| Top/5 | Top | 5 |  | 0.002 | 0.004 | 0.006 | 0.008 | 0.01 |

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

## 15. Bản đồ

Trạng thái: Đã áp

Nguồn dữ liệu: 08_ban_do/Ban_do; 08_ban_do/Ban_do_goc; 08_ban_do/Ban_do_biome; 08_ban_do/Thoi_tiet; 08_ban_do/Ban_do_dia_danh; 08_ban_do/Ban_do_rail; 08_ban_do/Ban_do_tag_dia_hinh; 08_ban_do/Ban_do_cong_vao; 08_ban_do/Ban_do_trung_lap; 08_ban_do/Vat_the_loai. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §15. Bản đồ.

25 chiến trường 300 × 300 m, cộng 25 bản dài 300 × 480 m (phần 7b) (8 bản đồ mới: Stormbeach, Hollow Dam, Veyra, Helion Launch Complex, Salt Flats, Border Crossing, Mirewood, Coral Keys), đường viền không đều; phần ngoài viền vẫn được dựng như bản đồ (nhà, rừng, đá) chỉ để trang trí, ranh giới là đường đứt nét. Mỗi trại có sở chỉ huy và ô tháp nhỏ/vừa/lớn/tiện ích; mỗi cứ điểm có tiền đồn. Phiên bản công thành đặt pháo đài chiếm 45% bản đồ ở đông bắc (phần 7).

#### Ashfield · temperate

Thị trấn · Ôn đới

#### Dunebreak · desert

Lọc dầu · Sa mạc

#### Frostpeak · snow

Làng núi · Tuyết

#### Ironport · harbor

Cảng · Công nghiệp

#### Red Rock · desert

Hẻm núi · Sa mạc

#### Whiteout Pass · snow

Đèo rừng · Tuyết

#### Greenvale · temperate

Đồng quê · Ôn đới

#### Rust Yard · harbor

Khu công nghiệp · Đổ nát

#### Emberridge · volcanic

Đồng dung nham · Núi lửa

#### Jungle Pass · jungle

Đền cổ · Rừng nhiệt đới

#### Skyhold · temperate

Sân bay quân sự · Ôn đới

#### Metro City · urban

Trung tâm · Đô thị

#### Stormbeach · temperate

Bãi biển và vách đá · Bờ biển

#### Hollow Dam · temperate

Đập và hẻm sông · Ôn đới

#### Veyra · urban

Khu chính phủ · Đô thị

#### Helion Launch Complex · desert

Tổ hợp phóng · Sa mạc

#### Salt Flats · desert

Đồng muối trống trải · Sa mạc

#### Border Crossing · temperate

Vượt sông · Ôn đới

#### Mirewood · jungle

Đường đắp · Rừng nhiệt đới

#### Coral Keys · desert

Đảo và cầu · Nhiệt đới

#### Beacon Bay · temperate

Bờ biển và tuyến biển · Ôn đới

#### Deepcut Mine · desert

Hố mỏ bậc thang · Sa mạc

#### Skygate Array · snow

Sân bay vũ trụ · Tuyết

#### Foundry · urban

Xưởng xe tăng · Công nghiệp

#### Veyra Old Quarter · urban

Phố cổ · Đô thị

#### 15g. Bốn vùng, kiểu cạnh, địa hình, địa danh, đường ray, tuyến biển (prompt 33)

##### Bốn vùng của bản đồ

| Vùng | Ở đâu | Nội dung | Lối chơi |
|---|---|---|---|
| 1. Vùng chơi | hình chữ nhật của bản đồ | navmesh, cứ điểm, căn cứ, tháp, chỗ nấp, vật chặn tầm nhìn, tag địa hình | Có |
| 2. Dải viền | 12–20 m ngoài mép (theo bản đồ) | chuyển cảnh: gờ đất, mương, vách, bãi, mép nước, góc dựng sẵn | Không |
| 3. Vành ngoài | 120 m quanh bản vuông; 73 / 128 m bên / đầu bản dài | trang trí instancing theo seed cố định; nửa xa dùng HLOD | Không; không collider, không chặn tầm nhìn |
| 4. Chân trời | ngoài vành | dãy núi thô, biển xa, đảo mờ, tàu xa, mặt đất chân trời, sương | Không |

Bề rộng vành = khung nhìn camera lớn nhất (trực giao, nghiêng 52°, zoom xa nhất 42 / 50, tỷ lệ 4:3, 16:9, 20:9, camera không xoay) + 15 %: tầm với 103.7 m (vuông), 63.5 / 111.1 m (dài).

##### Kiểu cạnh (edgeType) theo chiến trường

Phía BIỂN: mặt nước tới chân trời, sóng, bóng tàu xa, đảo mờ, không nhà, rừng, đất; bờ chuyển tiếp theo kiểu bờ (bãi: dải sóng vỗ; vách: đá trụ; cầu cảng: tường kè, cần cẩu, container). SÔNG chảy tiếp ra ngoài; VÁCH dựng thành vách đá; ĐÔ THỊ là thành phố của theme. Góc giao giữa hai kiểu dùng 10 tài sản góc dựng sẵn. Đường bộ, ray (tới cửa hầm), sông, bờ biển và tuyến biển (phao) kéo dài ra vành ngoài.

| Chiến trường | Bắc | Đông | Nam | Tây |
|---|---|---|---|---|
| Ashfield | đất | đất | đất | đất |
| Border Crossing | đất | đất / sông / đất | đất | đất / sông / đất |
| Veyra | đô thị | đô thị / sông / đô thị | đô thị | đô thị / sông / đô thị |
| Coral Keys | biển (bãi) / đất | biển (bãi) / đất | đất / biển (bãi) | đất / biển (bãi) |
| Dunebreak | đất (công nghiệp) | đất (công nghiệp) | đất (công nghiệp) | đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) |
| Emberridge | đất | đất | đất | đất |
| Foundry | đô thị (công nghiệp) | đô thị (công nghiệp) | đô thị (công nghiệp) | đô thị (công nghiệp) |
| Frostpeak | đất / vách / đất | đất | đất | đất |
| Greenvale | đất | đất | đất | đất |
| Hollow Dam | sông / đất | đất | đất / sông / đất | đất / sông |
| Ironport | biển (cảng, cầu cảng) | đất (công nghiệp) | đất (công nghiệp) | đất (công nghiệp) |
| Jungle Pass | đất | đất / vách / đất | đất | đất / vách / đất |
| Stormbeach | đất | biển (bãi) / đất / vách / đất | biển (bãi) | biển (bãi) / đất / vách / đất |
| Helion Launch Complex | đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) | đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) | đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) | đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) |
| Beacon Bay | đất | đất / biển (vách) / đất | đất / biển (bãi) / đất | đất |
| Metro City | đô thị | đô thị | đô thị | đô thị |
| Deepcut Mine | vách (công nghiệp) / đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) | vách (công nghiệp) / đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) | đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) / vách (công nghiệp) | đất (công nghiệp) / vách (công nghiệp) / đất (công nghiệp) / vách (công nghiệp) |
| Skygate Array | đất (công nghiệp) | đất (công nghiệp) | đất (công nghiệp) | đất (công nghiệp) |
| Red Rock | đất | đất | đất / vách / đất | đất / vách / đất |
| Rust Yard | biển (công nghiệp, cầu cảng) | đất (công nghiệp) | đất (công nghiệp) | đất (công nghiệp) |
| Salt Flats | đất | đất | đất | đất |
| Skyhold | đất | đất | đất | đất |
| Mirewood | đất / sông / đất | đất / sông / đất | đất / sông / đất | đất / sông / đất |
| Veyra Old Quarter | đô thị | đô thị | đô thị | đô thị |
| Whiteout Pass | đất | đất | đất | đất |

Tài sản góc (số lần trong 100 file): outer_land 298, corner_land_cliff 146, outer_urban 64, bank_land_river 60, corner_land_sea 38, outer_sea 16, embankment_urban_river 14, outer_land_sea 12, outer_cliff 7, outer_river 3.

##### Tag địa hình

| Tag | Tên | Tác dụng | Phủ (cả 100 file) |
|---|---|---|---|
| ROAD | Đường | tốc độ +20 % | 11,6 % |
| ROUGH | Gồ ghề | tốc độ −15 % (đô thị, đổ nát, sỏi đá; chỗ nấp vẫn do nhà / vật thể) | 6,7 % |
| FOREST | Rừng | tốc độ −25 %; tầm nhìn của địch lên xe trong rừng ×0,7 | 4,2 % |
| SHALLOW_WATER | Nước nông | xe thường −50 %; xe lội nước và đệm khí không chậm | 0,8 % |

Chi phí đường tĩnh theo tag (không đổi theo tick). DEEP_FORD để sau: bộ tìm đường chưa có chi phí theo loại xe.

##### Địa danh

Mỗi chiến trường 3 địa danh (landmarkId, tên song ngữ, khớp thoại prompt 30). Địa danh không có vật thể trên bản đồ được dựng bằng mô hình trang trí (không collider) ở chỗ trống gần nhất, tránh cứ điểm, đường, ray, cổng.

| Chiến trường | Địa danh |
|---|---|
| Ashfield | Tháp nước kho phía tây · Tháp nước kho phía đông · Tháp cổ thị trấn |
| Border Crossing | Cây cầu lớn · Nhà thờ làng biên giới · Đèn pha đầu cầu |
| Veyra | Dinh thự (mô hình trang trí) · Nhà ga (mô hình trang trí) · Tòa tháp Bộ |
| Coral Keys | Ngọn hải đăng (mô hình trang trí) · Tháp canh đảo tây · Tháp canh đảo đông |
| Dunebreak | Nhà máy lọc dầu · Cột vô tuyến sa mạc · Ra-đa phía bắc |
| Emberridge | Nhà máy địa nhiệt (mô hình trang trí) · Cột đá vỏ chai · Sườn núi lửa |
| Foundry | Ống khói xưởng đúc · Xưởng phía bắc · Xưởng phía nam |
| Frostpeak | Trạm ra-đa · Nhà thờ làng · Tháp nước trại gỗ |
| Greenvale | Si-lô trại phía tây · Nhà thờ ngã tư · Tháp nước trại phía đông |
| Hollow Dam | Con đập (mô hình trang trí) · Tháp đập · Trạm thủy điện |
| Ironport | Cần cẩu cảng · Bến tàu · Tháp nước ga hàng (mô hình trang trí) |
| Jungle Pass | Ngôi đền · Khúc cạn đền · Nhà thờ làng phía tây (mô hình trang trí) |
| Stormbeach | Trạm ra-đa · Nhà thờ làng · Vách đá |
| Helion Launch Complex | Giàn phóng · Nhà chứa lắp ráp · Núi bàn phía bắc |
| Beacon Bay | Ngọn hải đăng · Pháo đài cũ · Làng chài |
| Metro City | Tòa tháp phía bắc · Quảng trường · Biển quảng cáo bãi xe |
| Deepcut Mine | Cần cẩu máy nghiền · Đáy mỏ · Trạm bốc quặng |
| Skygate Array | Dàn ăng-ten · Giàn phóng phía tây · Bãi đáp |
| Red Rock | Tháp nước trạm lữ hành · Núi bàn đỏ · Nhà thờ thị trấn mỏ (mô hình trang trí) |
| Rust Yard | Tháp nước bãi · Xưởng đúc · Tháp đổ bến cảng |
| Salt Flats | Mốc trắc địa (mô hình trang trí) · Ra-đa trắc địa · Trạm bơm nước muối |
| Skyhold | Đài kiểm soát · Chảo ra-đa · Nhà chứa máy bay phía tây |
| Mirewood | Đền chìm · Tháp canh làng tây · Ra-đa đầm lầy |
| Veyra Old Quarter | Nhà thờ lớn · Quảng trường đồng hồ (mô hình trang trí) · Cột vô tuyến khu phố cổ |
| Whiteout Pass | Cột tín hiệu · Hồ băng · Tháp canh đèo |

##### Đường ray (RailSpline)

Lớp riêng, không phải navmesh: từ cửa hầm ngoài bản đồ qua dải viền, cổng vào, tới điểm dừng; Juggernaut, Nemesis, Gungnir và tàu chi viện Công thành chạy trên ray. Chỗ cắt đường bộ: MỞ → CẢNH BÁO (≥ 4 s) → ĐÓNG → TÀU QUA → MỞ.

##### Tuyến tàu biển (SeaRouteGraph)

Tàu lớn đi trên đồ thị tuyến (đoạn, nút, vịnh tránh), giữ đoạn hiện tại và đoạn kế, khoảng cách tối thiểu nửa thân tàu này + nửa thân tàu trước + 10 m, ưu tiên cố định.

##### 12 validator (Tools/maps/validate_p33.py, lần chạy đầy đủ gần nhất)

Ảnh mép bản đồ ở zoom xa nhất cho mỗi biome: cần ảnh chụp từ Unity (ghi trong LOCAL_TODO).

Sheet: 08_ban_do/Ban_do — Bản đồ (100 dòng, 44 cột)

| id | ban_do_goc | bien_the | tep | asymmetry_intended | asymmetry_reason | boundary | bounds | edges_band | edges_outer |
|---|---|---|---|---|---|---|---|---|---|
| ashfield_conquest | ashfield | conquest | ashfield_conquest.json |  |  | -146.62;-86.0;-146.19;-86.15;-146.0;-86.88;-145.94;-92.56;-… |  | 16.0 | 120.0 |
| ashfield_long | ashfield | long | ashfield_long.json | TRUE | Long battlefield: the attacker's square and the defender's… | -146.62;-86.0;-146.19;-86.15;-146.0;-86.88;-145.94;-92.56;-… | -150.0;-150.0;150.0;330.0 | 16.0 | 120.0 |
| ashfield_sandbox | ashfield | sandbox | ashfield_sandbox.json |  |  | -146.62;-86.0;-146.19;-86.15;-146.0;-86.88;-145.94;-92.56;-… |  | 16.0 | 120.0 |
| ashfield_siege | ashfield | siege | ashfield_siege.json | TRUE | Siege: one side holds the fortress, the other attacks it (p… | -146.62;-86.0;-146.19;-86.15;-146.0;-86.88;-145.94;-92.56;-… |  | 16.0 | 120.0 |
| borderbridge_conquest | borderbridge | conquest | borderbridge_conquest.json |  |  | -143.62;-144.38;-141.92;-144.98;-98.08;-144.02;-96.99;-143.… |  | 16.0 | 120.0 |
| borderbridge_long | borderbridge | long | borderbridge_long.json | TRUE | Long battlefield: the attacker's square and the defender's… | -146.62;158.0;-146.19;157.83;-146.0;156.97;-146.0;148.03;-1… | -150.0;-150.0;150.0;330.0 | 16.0 | 120.0 |
| borderbridge_sandbox | borderbridge | sandbox | borderbridge_sandbox.json |  |  | -143.62;-144.38;-141.92;-144.98;-98.08;-144.02;-96.99;-143.… |  | 16.0 | 120.0 |
| borderbridge_siege | borderbridge | siege | borderbridge_siege.json | TRUE | Siege: one side holds the fortress, the other attacks it (p… | -143.62;-144.38;-141.92;-144.98;-98.08;-144.02;-96.99;-143.… |  | 16.0 | 120.0 |
| capital_conquest | capital | conquest | capital_conquest.json |  |  | -146.62;-45.0;-146.19;-45.18;-146.0;-46.09;-146.0;-104.91;-… |  | 16.0 | 120.0 |
| capital_long | capital | long | capital_long.json | TRUE | Long battlefield: the attacker's square and the defender's… | -146.62;-45.0;-146.19;-45.18;-146.0;-46.09;-146.0;-104.91;-… | -150.0;-150.0;150.0;330.0 | 16.0 | 120.0 |
| capital_sandbox | capital | sandbox | capital_sandbox.json |  |  | -146.62;-45.0;-146.19;-45.18;-146.0;-46.09;-146.0;-104.91;-… |  | 16.0 | 120.0 |
| capital_siege | capital | siege | capital_siege.json | TRUE | Siege: one side holds the fortress, the other attacks it (p… | -146.62;-45.0;-146.19;-45.18;-146.0;-46.09;-146.0;-104.91;-… |  | 16.0 | 120.0 |
| coralisles_conquest | coralisles | conquest | coralisles_conquest.json |  |  | -147.62;-135.0;-147.19;-135.17;-147.0;-136.03;-146.91;-145.… |  | 16.0 | 120.0 |
| coralisles_long | coralisles | long | coralisles_long.json | TRUE | Long battlefield: the attacker's square and the defender's… | -147.62;-135.0;-147.19;-135.17;-147.0;-136.03;-146.91;-145.… | -150.0;-150.0;150.0;330.0 | 16.0 | 120.0 |
| coralisles_sandbox | coralisles | sandbox | coralisles_sandbox.json |  |  | -147.62;-135.0;-147.19;-135.17;-147.0;-136.03;-146.91;-145.… |  | 16.0 | 120.0 |

*15 / 100 dòng đầu: xem sheet 08_ban_do/Ban_do; in 10 / 44 cột; 22 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 08_ban_do/Ban_do_goc — Bản đồ gốc (25 dòng, 13 cột)

| id | biome | bien_the | berms | density | ditches | dry_beds | edge_band | far_tree | hills |
|---|---|---|---|---|---|---|---|---|---|
| ashfield | temperate | ashfield_conquest;ashfield_long;ashfield_sandbox;ashfield_s… | 6 | 1.0 | 3 | 1 | 16.0 |  | 8 |
| borderbridge | temperate | borderbridge_conquest;borderbridge_long;borderbridge_sandbo… | 6 | 1.0 | 3 | 1 | 16.0 |  | 8 |
| capital | urban | capital_conquest;capital_long;capital_sandbox;capital_siege | 4 | 1.0 | 2 | 0 | 12.0 |  | 0 |
| coralisles | coast | coralisles_conquest;coralisles_long;coralisles_sandbox;cora… | 4 | 1.0 | 1 | 1 | 12.0 | none | 5 |
| dunebreak | desert | dunebreak_conquest;dunebreak_long;dunebreak_sandbox;dunebre… | 4 | 1.0 | 0 | 3 | 20.0 |  | 6 |
| emberridge | volcanic | emberridge_conquest;emberridge_long;emberridge_sandbox;embe… | 3 | 1.0 | 0 | 2 | 16.0 |  | 8 |
| foundry | harbor | foundry_conquest;foundry_long;foundry_sandbox;foundry_siege | 5 | 1.0 | 3 | 0 | 12.0 |  | 3 |
| frostpeak | snow | frostpeak_conquest;frostpeak_long;frostpeak_sandbox;frostpe… | 4 | 1.0 | 0 | 1 | 18.0 |  | 8 |
| greenvale | temperate | greenvale_conquest;greenvale_long;greenvale_sandbox;greenva… | 6 | 1.1 | 3 | 1 | 16.0 |  | 8 |
| hydrodam | temperate | hydrodam_conquest;hydrodam_long;hydrodam_sandbox;hydrodam_s… | 6 | 1.0 | 3 | 1 | 16.0 |  | 8 |
| ironport | harbor | ironport_conquest;ironport_long;ironport_sandbox;ironport_s… | 5 | 1.0 | 3 | 0 | 14.0 |  | 3 |
| junglepass | jungle | junglepass_conquest;junglepass_long;junglepass_sandbox;jung… | 3 | 1.0 | 2 | 2 | 12.0 |  | 6 |
| landingbeach | coast | landingbeach_conquest;landingbeach_long;landingbeach_sandbo… | 4 | 1.0 | 1 | 1 | 14.0 |  | 5 |
| launchsite | desert | launchsite_conquest;launchsite_long;launchsite_sandbox;laun… | 4 | 0.8 | 0 | 3 | 20.0 |  | 6 |
| lighthousebay | coast | lighthousebay_conquest;lighthousebay_long;lighthousebay_san… | 4 | 1.0 | 1 | 1 | 14.0 |  | 5 |
| metrocity | urban | metrocity_conquest;metrocity_long;metrocity_sandbox;metroci… | 4 | 1.0 | 2 | 0 | 12.0 |  | 0 |
| openpit | desert | openpit_conquest;openpit_long;openpit_sandbox;openpit_siege | 4 | 0.9 | 0 | 3 | 18.0 |  | 6 |
| orbitalgate | snow | orbitalgate_conquest;orbitalgate_long;orbitalgate_sandbox;o… | 4 | 0.9 | 0 | 1 | 16.0 |  | 8 |
| redrock | desert | redrock_conquest;redrock_long;redrock_sandbox;redrock_siege | 4 | 1.0 | 0 | 3 | 18.0 |  | 6 |
| rustyard | harbor | rustyard_conquest;rustyard_long;rustyard_sandbox;rustyard_s… | 5 | 1.0 | 3 | 0 | 14.0 |  | 3 |
| saltflat | desert | saltflat_conquest;saltflat_long;saltflat_sandbox;saltflat_s… | 4 | 0.6 | 0 | 3 | 20.0 |  | 6 |
| skyhold | temperate | skyhold_conquest;skyhold_long;skyhold_sandbox;skyhold_siege | 6 | 0.8 | 3 | 1 | 18.0 |  | 8 |
| swamp | jungle | swamp_conquest;swamp_long;swamp_sandbox;swamp_siege | 3 | 1.1 | 2 | 2 | 14.0 |  | 6 |
| veyra_old_quarter | urban | veyra_old_quarter_conquest;veyra_old_quarter_long;veyra_old… | 4 | 1.0 | 2 | 0 | 12.0 |  | 0 |
| whiteout | snow | whiteout_conquest;whiteout_long;whiteout_sandbox;whiteout_s… | 4 | 0.8 | 0 | 1 | 20.0 |  | 8 |

*in 10 / 13 cột; 1 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 08_ban_do/Ban_do_biome — Biome (8 dòng, 19 cột)

| id | band | band_set | berms | ditches | dry_beds | edge_band | far | far_set | far_tree |
|---|---|---|---|---|---|---|---|---|---|
| coast | 100 | dress_coast_dune_grass;dress_coast_dune_grass;dress_coast_d… | 4 | 1 | 1 | 14 | 20 | dress_temperate_tree_far | dress_temperate_tree_far |
| desert | 70 | dress_desert_scrub;dress_desert_scrub;dress_desert_scrub;dr… | 4 | 0 | 3 | 20 | 18 | dress_desert_far |  |
| harbor | 90 | dress_harbor_pallets;dress_harbor_pallets;dress_harbor_drum… | 5 | 3 | 0 | 14 | 12 | dress_harbor_shed_far | dress_temperate_tree_far |
| jungle | 150 | dress_jungle_palm_small;dress_jungle_palm_small;dress_jungl… | 3 | 2 | 2 | 14 | 45 | dress_jungle_tree_far | dress_jungle_tree_far |
| snow | 100 | dress_snow_drift;dress_snow_drift;dress_snow_drift;dress_sn… | 4 | 0 | 1 | 18 | 35 | dress_snow_pine_far | dress_snow_pine_far |
| temperate | 120 | dress_temperate_shrub;dress_temperate_shrub;dress_temperate… | 6 | 3 | 1 | 16 | 40 | dress_temperate_tree_far | dress_temperate_tree_far |
| urban | 80 | dress_urban_rubble;dress_urban_rubble;dress_urban_planter;d… | 4 | 2 | 0 | 12 | 6 | dress_urban_block_far | dress_temperate_tree_far |
| volcanic | 70 | dress_volcanic_ash_rocks;dress_volcanic_ash_rocks;dress_vol… | 3 | 0 | 2 | 16 | 18 | dress_volcanic_far | dress_volcanic_snag |

*in 10 / 19 cột; 7 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 08_ban_do/Thoi_tiet — Thời tiết (8 dòng, 5 cột)

| id | he_so_tam_nhin | so_nhiem_vu |
|---|---|---|
| Clear | 1.0 | 40 |
| Fog | 0.7 | 37 |
| Night | 0.75 | 42 |
| Overcast | 1.0 | 27 |
| Rain | 0.9 | 19 |
| Sandstorm | 0.75 | 8 |
| Snow | 0.85 | 7 |
| Storm | 0.8 | 13 |

Sheet: 08_ban_do/Ban_do_dia_danh — Bản đồ: địa danh (300 dòng, 14 cột)

| id | ban_do_id | thu_tu | aliases | id_goc | kind | name_en | name_vi | prop | x_m |
|---|---|---|---|---|---|---|---|---|---|
| ashfield_conquest/ashfield.town_tower | ashfield_conquest | 2 | the square | ashfield.town_tower | ruin_tower | Old town tower | Tháp cổ thị trấn | ruin_tower | 10.0 |
| ashfield_conquest/ashfield.wt_east | ashfield_conquest | 1 | the depot | ashfield.wt_east | water_tower | East depot water tower | Tháp nước kho phía đông | water_tower | 52.5 |
| ashfield_conquest/ashfield.wt_west | ashfield_conquest | 0 | the depot | ashfield.wt_west | water_tower | West depot water tower | Tháp nước kho phía tây | water_tower | -52.5 |
| ashfield_long/ashfield.town_tower | ashfield_long | 2 | the square | ashfield.town_tower | ruin_tower | Old town tower | Tháp cổ thị trấn | ruin_tower | 10.0 |
| ashfield_long/ashfield.wt_east | ashfield_long | 1 | the depot | ashfield.wt_east | water_tower | East depot water tower | Tháp nước kho phía đông | water_tower | 52.5 |
| ashfield_long/ashfield.wt_west | ashfield_long | 0 | the depot | ashfield.wt_west | water_tower | West depot water tower | Tháp nước kho phía tây | water_tower | -52.5 |
| ashfield_sandbox/ashfield.town_tower | ashfield_sandbox | 2 | the square | ashfield.town_tower | ruin_tower | Old town tower | Tháp cổ thị trấn | ruin_tower | 10.0 |
| ashfield_sandbox/ashfield.wt_east | ashfield_sandbox | 1 | the depot | ashfield.wt_east | water_tower | East depot water tower | Tháp nước kho phía đông | water_tower | 52.5 |
| ashfield_sandbox/ashfield.wt_west | ashfield_sandbox | 0 | the depot | ashfield.wt_west | water_tower | West depot water tower | Tháp nước kho phía tây | water_tower | -52.5 |
| ashfield_siege/ashfield.town_tower | ashfield_siege | 2 | the square | ashfield.town_tower | ruin_tower | Old town tower | Tháp cổ thị trấn | ruin_tower | 10.0 |
| ashfield_siege/ashfield.wt_east | ashfield_siege | 1 | the depot | ashfield.wt_east | water_tower | East depot water tower | Tháp nước kho phía đông | water_tower | 52.5 |
| ashfield_siege/ashfield.wt_west | ashfield_siege | 0 | the depot | ashfield.wt_west | water_tower | West depot water tower | Tháp nước kho phía tây | water_tower | -52.5 |
| borderbridge_conquest/borderbridge.bridge_lights | borderbridge_conquest | 2 |  | borderbridge.bridge_lights | floodlight | Bridge floodlights | Đèn pha đầu cầu | floodlight_mast | 6.0 |
| borderbridge_conquest/borderbridge.great_bridge | borderbridge_conquest | 0 | the bridge | borderbridge.great_bridge | bridge | The great bridge | Cây cầu lớn |  | 0.0 |
| borderbridge_conquest/borderbridge.village_church | borderbridge_conquest | 1 |  | borderbridge.village_church | church | Border village church | Nhà thờ làng biên giới | church | -58.0 |

*15 / 300 dòng đầu: xem sheet 08_ban_do/Ban_do_dia_danh; in 10 / 14 cột; 1 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 08_ban_do/Ban_do_rail — Bản đồ: ray (23 dòng, 11 cột)

| id | ban_do_id | thu_tu | id_goc | kind | play_from | play_to | points |
|---|---|---|---|---|---|---|---|
| capital_conquest/nemesis | capital_conquest | 0 | nemesis | line | 55.5 | 154.0 | 190.0;-4.0;140.0;-4.0;36.0;-4.0 |
| capital_sandbox/nemesis | capital_sandbox | 0 | nemesis | line | 55.5 | 154.0 | 190.0;-4.0;140.0;-4.0;36.0;-4.0 |
| capital_siege/nemesis | capital_siege | 0 | nemesis | line | 55.5 | 154.0 | 190.0;-4.0;140.0;-4.0;36.0;-4.0 |
| capital_siege/siege_line | capital_siege | 1 | siege_line | siege | 64.5 | 114.0 | 24.0;210.0;24.0;96.0 |
| foundry_conquest/works | foundry_conquest | 0 | works | line | 44.5 | 164.0 | 46.0;190.0;46.0;145.0;46.0;26.0 |
| foundry_sandbox/works | foundry_sandbox | 0 | works | line | 44.5 | 164.0 | 46.0;190.0;46.0;145.0;46.0;26.0 |
| foundry_siege/siege_line | foundry_siege | 0 | siege_line | siege | 64.5 | 114.0 | 24.0;210.0;24.0;96.0 |
| frostpeak_siege/siege_line | frostpeak_siege | 0 | siege_line | siege | 76.5 | 114.0 | 24.0;210.0;24.0;96.0 |
| ironport_conquest/quay | ironport_conquest | 0 | quay | line | 42.5 | 318.0 | -190.0;106.8;-138.75;106.8;128.0;106.8 |
| ironport_sandbox/quay | ironport_sandbox | 0 | quay | line | 42.5 | 318.0 | -190.0;106.8;-138.75;106.8;128.0;106.8 |
| ironport_siege/siege_line | ironport_siege | 0 | siege_line | siege | 65.0 | 114.0 | 24.0;210.0;24.0;96.0 |
| junglepass_siege/siege_line | junglepass_siege | 0 | siege_line | siege | 69.0 | 111.0 | 24.0;210.0;24.0;96.0 |
| metrocity_conquest/avenue | metrocity_conquest | 0 | avenue | line | 40.5 | 355.28 | 190.0;101.25;128.0;101.25;75.0;101.25;0.0;101.25;-67.5;101.… |
| metrocity_sandbox/avenue | metrocity_sandbox | 0 | avenue | line | 40.5 | 355.28 | 190.0;101.25;128.0;101.25;75.0;101.25;0.0;101.25;-67.5;101.… |
| metrocity_siege/siege_line | metrocity_siege | 0 | siege_line | siege | 65.5 | 114.0 | 24.0;210.0;24.0;96.0 |
| orbitalgate_siege/siege_line | orbitalgate_siege | 0 | siege_line | siege | 63.5 | 114.0 | 24.0;210.0;24.0;96.0 |
| redrock_siege/siege_line | redrock_siege | 0 | siege_line | siege | 68.5 | 106.5 | 24.0;210.0;24.0;96.0 |
| rustyard_conquest/siding | rustyard_conquest | 0 | siding | line | 41.5 | 66.0 | 190.0;11.25;140.0;11.25;124.0;11.25 |
| rustyard_sandbox/siding | rustyard_sandbox | 0 | siding | line | 41.5 | 66.0 | 190.0;11.25;140.0;11.25;124.0;11.25 |
| rustyard_siege/siding | rustyard_siege | 0 | siding | line | 41.5 | 66.0 | 190.0;11.25;140.0;11.25;124.0;11.25 |
| rustyard_siege/siege_line | rustyard_siege | 1 | siege_line | siege | 65.0 | 114.0 | 24.0;210.0;24.0;96.0 |
| veyra_old_quarter_siege/siege_line | veyra_old_quarter_siege | 0 | siege_line | siege | 65.0 | 114.0 | 24.0;210.0;24.0;96.0 |
| whiteout_siege/siege_line | whiteout_siege | 0 | siege_line | siege | 69.5 | 114.0 | 24.0;210.0;24.0;96.0 |

Sheet: 08_ban_do/Ban_do_tag_dia_hinh — Bản đồ: tag địa hình (38788 dòng, 10 cột)

| id | ban_do_id | thu_tu | x0_m | z0_m | x1_m | z1_m | tag |
|---|---|---|---|---|---|---|---|
| ashfield_conquest/0/0 | ashfield_conquest | 0 | -4.0 | -144.0 | 4.0 | -28.0 | ROAD |
| ashfield_conquest/0/1 | ashfield_conquest | 0 | -110.0 | -112.0 | -108.0 | -106.0 | ROAD |
| ashfield_conquest/0/2 | ashfield_conquest | 0 | -112.0 | -110.0 | -110.0 | -108.0 | ROAD |
| ashfield_conquest/0/3 | ashfield_conquest | 0 | -108.0 | -110.0 | -106.0 | -104.0 | ROAD |
| ashfield_conquest/0/4 | ashfield_conquest | 0 | -106.0 | -108.0 | -104.0 | -102.0 | ROAD |
| ashfield_conquest/0/5 | ashfield_conquest | 0 | -104.0 | -106.0 | -102.0 | -100.0 | ROAD |
| ashfield_conquest/0/6 | ashfield_conquest | 0 | -102.0 | -104.0 | -100.0 | -98.0 | ROAD |
| ashfield_conquest/0/7 | ashfield_conquest | 0 | -100.0 | -102.0 | -98.0 | -96.0 | ROAD |
| ashfield_conquest/0/8 | ashfield_conquest | 0 | -98.0 | -100.0 | -96.0 | -94.0 | ROAD |
| ashfield_conquest/0/9 | ashfield_conquest | 0 | -96.0 | -98.0 | -94.0 | -92.0 | ROAD |
| ashfield_conquest/0/10 | ashfield_conquest | 0 | -94.0 | -96.0 | -92.0 | -90.0 | ROAD |
| ashfield_conquest/0/11 | ashfield_conquest | 0 | -92.0 | -94.0 | -90.0 | -88.0 | ROAD |
| ashfield_conquest/0/12 | ashfield_conquest | 0 | -90.0 | -92.0 | -88.0 | -86.0 | ROAD |
| ashfield_conquest/0/13 | ashfield_conquest | 0 | -88.0 | -90.0 | -86.0 | -84.0 | ROAD |
| ashfield_conquest/0/14 | ashfield_conquest | 0 | -86.0 | -88.0 | -84.0 | -82.0 | ROAD |

*15 / 38788 dòng đầu: xem sheet 08_ban_do/Ban_do_tag_dia_hinh.*

Sheet: 08_ban_do/Ban_do_cong_vao — Bản đồ: cổng vào (3200 dòng, 16 cột)

| id | ban_do_id | thu_tu | id_goc | in_x | in_z | kind | path | side | visual_ingress_length |
|---|---|---|---|---|---|---|---|---|---|
| ashfield_conquest/edge4 | ashfield_conquest | 4 | edge4 | 0 | -1 | edge | -45.0;270.0;-45.0;150.0;-45.0;113.0 | N | 157.0 |
| ashfield_conquest/edge5 | ashfield_conquest | 5 | edge5 | 0 | -1 | edge | 15.0;270.0;15.0;150.0;15.0;135.0 | N | 135.0 |
| ashfield_conquest/edge6 | ashfield_conquest | 6 | edge6 | 0 | -1 | edge | 45.0;270.0;45.0;150.0;45.0;141.0 | N | 129.0 |
| ashfield_conquest/edge7 | ashfield_conquest | 7 | edge7 | 0 | -1 | edge | 75.0;270.0;75.0;150.0;75.0;143.0 | N | 127.0 |
| ashfield_conquest/edge8 | ashfield_conquest | 8 | edge8 | 0 | -1 | edge | 105.0;270.0;105.0;150.0;105.0;143.0 | N | 127.0 |
| ashfield_conquest/edge9 | ashfield_conquest | 9 | edge9 | 0 | -1 | edge | 135.0;270.0;135.0;150.0;135.0;141.0 | N | 129.0 |
| ashfield_conquest/edge10 | ashfield_conquest | 10 | edge10 | -1 | 0 | edge | 270.0;-15.0;150.0;-15.0;121.0;-15.0 | E | 149.0 |
| ashfield_conquest/edge11 | ashfield_conquest | 11 | edge11 | -1 | 0 | edge | 270.0;15.0;150.0;15.0;137.0;15.0 | E | 133.0 |
| ashfield_conquest/edge12 | ashfield_conquest | 12 | edge12 | -1 | 0 | edge | 270.0;45.0;150.0;45.0;141.0;45.0 | E | 129.0 |
| ashfield_conquest/edge13 | ashfield_conquest | 13 | edge13 | -1 | 0 | edge | 270.0;75.0;150.0;75.0;143.0;75.0 | E | 127.0 |
| ashfield_conquest/edge14 | ashfield_conquest | 14 | edge14 | -1 | 0 | edge | 270.0;105.0;150.0;105.0;143.0;105.0 | E | 127.0 |
| ashfield_conquest/edge15 | ashfield_conquest | 15 | edge15 | 0 | 1 | edge | -135.0;-270.0;-135.0;-150.0;-135.0;-142.0 | S | 128.0 |
| ashfield_conquest/edge16 | ashfield_conquest | 16 | edge16 | 0 | 1 | edge | -105.0;-270.0;-105.0;-150.0;-105.0;-142.0 | S | 128.0 |
| ashfield_conquest/edge17 | ashfield_conquest | 17 | edge17 | 0 | 1 | edge | -75.0;-270.0;-75.0;-150.0;-75.0;-142.0 | S | 128.0 |
| ashfield_conquest/edge18 | ashfield_conquest | 18 | edge18 | 0 | 1 | edge | -45.0;-270.0;-45.0;-150.0;-45.0;-142.0 | S | 128.0 |

*15 / 3200 dòng đầu: xem sheet 08_ban_do/Ban_do_cong_vao; in 10 / 16 cột; 2 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 08_ban_do/Ban_do_trung_lap — Bản đồ: trung lập (250 dòng, 8 cột)

| id | ban_do_id | thu_tu | kind | x_m | z_m |
|---|---|---|---|---|---|
| ashfield_conquest/0 | ashfield_conquest | 0 | radar | 0.0 | -84.85 |
| ashfield_conquest/1 | ashfield_conquest | 1 | radar | -0.0 | 84.85 |
| ashfield_conquest/2 | ashfield_conquest | 2 | ammo_depot | -74.25 | -10.61 |
| ashfield_conquest/3 | ashfield_conquest | 3 | ammo_depot | 74.25 | 10.61 |
| ashfield_sandbox/0 | ashfield_sandbox | 0 | radar | 0.0 | -84.85 |
| ashfield_sandbox/1 | ashfield_sandbox | 1 | radar | -0.0 | 84.85 |
| ashfield_sandbox/2 | ashfield_sandbox | 2 | ammo_depot | -74.25 | -10.61 |
| ashfield_sandbox/3 | ashfield_sandbox | 3 | ammo_depot | 74.25 | 10.61 |
| ashfield_siege/0 | ashfield_siege | 0 | aa_site | -2.12 | -78.49 |
| ashfield_siege/1 | ashfield_siege | 1 | ammo_depot | -63.64 | 0.0 |
| borderbridge_conquest/0 | borderbridge_conquest | 0 | workshop | -6.36 | -74.25 |
| borderbridge_conquest/1 | borderbridge_conquest | 1 | workshop | 6.36 | 74.25 |
| borderbridge_conquest/2 | borderbridge_conquest | 2 | aa_site | -95.46 | -31.82 |
| borderbridge_conquest/3 | borderbridge_conquest | 3 | aa_site | 95.46 | 31.82 |
| borderbridge_sandbox/0 | borderbridge_sandbox | 0 | workshop | -6.36 | -74.25 |

*15 / 250 dòng đầu: xem sheet 08_ban_do/Ban_do_trung_lap.*

Sheet: 08_ban_do/Vat_the_loai — Loại vật thể (122 dòng, 17 cột)

| id | armor | armour | blocks | blocks_fire | collapse | crush | depth_m | explosion_damage | explosion_delay_s |
|---|---|---|---|---|---|---|---|---|---|
| adobe_house | Structure |  | TRUE |  |  |  | 9.36 |  |  |
| adobe_large | Structure |  | TRUE |  |  |  | 12.09 |  |  |
| ammo_crate | Light |  |  |  |  |  | 1.25 | 90 | 0.2 |
| ammo_dump | Structure |  | TRUE | FALSE |  |  | 5 | 300 | 0.3 |
| apartment | Structure |  | TRUE |  |  |  | 10.4 |  |  |
| artillery_wreck | Heavy | 3 | TRUE | FALSE |  |  | 6.48 |  |  |
| bamboo_clump | Light |  |  |  |  | TRUE | 2.5 |  |  |
| barn | Structure |  | TRUE |  |  |  | 12.48 |  |  |
| barrel | Light |  |  |  |  |  | 1 | 70 | 0.15 |
| barricade | Heavy |  | TRUE | FALSE |  |  | 1.9 |  |  |
| basalt_rock_a | Structure |  | TRUE |  |  |  | 4 |  |  |
| basalt_rock_b | Structure |  | TRUE |  |  |  | 5 |  |  |
| basalt_rock_c | Structure |  | TRUE |  |  |  | 3 |  |  |
| base_gate | Structure | 4 |  |  |  |  | 2 |  |  |
| base_wall | Structure | 4 | TRUE |  | 1.4 |  | 1.2 |  |  |

*15 / 122 dòng đầu: xem sheet 08_ban_do/Vat_the_loai; in 10 / 17 cột; 5 cột khác (và raw_json, nguon): xem sheet.*

### 15b. Đo bản đồ tĩnh

Trạng thái: Một phần — chờ prompt xuất dữ liệu (sheet đo bản đồ tĩnh của spec 4 chưa có trong 08_ban_do; số đo nằm ở báo cáo Docs/checks/map_audit.md, in dưới đây)

Nguồn dữ liệu: 08_ban_do/Ban_do_cu_diem_bai_tha_can_cu. Văn bản: Docs/checks/map_audit.md.

#### Báo cáo `Docs/checks/map_audit.md`

##### Map audit (prompt 30 L8, static, read-only)

Generated by `Tools/audit/map_audit.py` from the map files; the full table is `map_audit.csv`. Nothing was changed and nothing was simulated.

**Limits of a static measure:** it does not show win rates, real traffic jams or flow, the real value of artillery (spotting, minimum ranges, the AI), how the AI picks lanes, how long fights last, or performance. Paths are on the 2 m navigation grid, sightlines on a flat ground with one eye height. Symmetric versions (Conquest, Sandbox) are compared side against side; Siege and the long battlefields are reported by role.

100 files: 0 RED, 100 YELLOW, 0 GREEN.

Thresholds: medianPathDelta ≤ 10 % GREEN, 10-15 % YELLOW, > 15 % RED (symmetric); fewer than 2 lanes RED (symmetric); a drop zone within 40 m of an enemy fixed defence RED; sightline P95 above the tank gun's 32 m YELLOW (information); neutralValueDelta > 10 % YELLOW, > 20 % RED (symmetric).

| Map | Kind | Flags | Lanes | Path delta | Chokes (mand./opt.) | Sightline P95 | Exits | Neutral Δ |
|---|---|---|---|---|---|---|---|---|
| ashfield_conquest | symmetric | YELLOW sightline | 4 | 0.3% | 0/0 | 150.0 | open/open | 1% |
| ashfield_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| ashfield_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 1% |
| ashfield_siege | asymmetric | YELLOW sightline | 4 | by role | 0/2 | 150.0 | open/7 | 50% |
| borderbridge_conquest | symmetric | YELLOW sightline | 3 | 3.1% | 0/0 | 150.0 | open/open | 1% |
| borderbridge_long | asymmetric | YELLOW sightline | 4 | by role | 0/5 | 150.0 | open/4 | - |
| borderbridge_sandbox | symmetric | YELLOW sightline | 3 | by role | 0/0 | 150.0 | open/open | 1% |
| borderbridge_siege | asymmetric | YELLOW sightline | 4 | by role | 0/5 | 150.0 | open/7 | 22% |
| capital_conquest | symmetric | YELLOW sightline | 4 | 4.1% | 0/7 | 150.0 | open/open | 0% |
| capital_long | asymmetric | YELLOW sightline | 4 | by role | 0/9 | 150.0 | open/4 | - |
| capital_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/7 | 150.0 | open/open | 0% |
| capital_siege | asymmetric | YELLOW sightline | 4 | by role | 0/3 | 144.0 | open/7 | 35% |
| coralisles_conquest | symmetric | YELLOW sightline | 4 | 0.0% | 0/0 | 150.0 | open/open | 2% |
| coralisles_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| coralisles_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 2% |
| coralisles_siege | asymmetric | YELLOW sightline | 4 | by role | 0/2 | 150.0 | open/2 | 35% |
| dunebreak_conquest | symmetric | YELLOW sightline | 4 | 0.6% | 0/0 | 150.0 | open/open | 1% |
| dunebreak_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| dunebreak_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 1% |
| dunebreak_siege | asymmetric | YELLOW sightline | 4 | by role | 0/1 | 150.0 | open/7 | 40% |
| emberridge_conquest | symmetric | YELLOW sightline; YELLOW exits | 4 | 0.1% | 0/0 | 150.0 | open/1 | 1% |
| emberridge_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| emberridge_sandbox | symmetric | YELLOW sightline; YELLOW exits | 4 | by role | 0/0 | 150.0 | open/1 | 1% |
| emberridge_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/7 | 49% |
| foundry_conquest | symmetric | YELLOW sightline | 4 | 2.4% | 0/2 | 118.0 | open/open | 1% |
| foundry_long | asymmetric | YELLOW sightline | 4 | by role | 0/3 | 150.0 | open/4 | - |
| foundry_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/2 | 118.0 | open/open | 1% |
| foundry_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 110.0 | open/7 | 29% |
| frostpeak_conquest | symmetric | YELLOW sightline; YELLOW exits | 4 | 0.2% | 0/0 | 150.0 | open/1 | 1% |
| frostpeak_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| frostpeak_sandbox | symmetric | YELLOW sightline; YELLOW exits | 4 | by role | 0/0 | 150.0 | open/1 | 1% |
| frostpeak_siege | asymmetric | YELLOW sightline | 4 | by role | 0/1 | 150.0 | open/7 | 42% |
| greenvale_conquest | symmetric | YELLOW sightline | 4 | 0.4% | 0/0 | 150.0 | open/open | 1% |
| greenvale_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| greenvale_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 1% |
| greenvale_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/7 | 44% |
| hydrodam_conquest | symmetric | YELLOW path delta; YELLOW sightline | 4 | 14.1% | 0/0 | 150.0 | open/open | 0% |
| hydrodam_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| hydrodam_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 0% |
| hydrodam_siege | asymmetric | YELLOW sightline | 4 | by role | 0/2 | 150.0 | open/7 | 40% |
| ironport_conquest | symmetric | YELLOW sightline | 4 | 1.2% | 0/0 | 150.0 | open/2 | 2% |
| ironport_long | asymmetric | YELLOW sightline | 4 | by role | 0/2 | 150.0 | open/4 | - |
| ironport_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/2 | 2% |
| ironport_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/7 | 42% |
| junglepass_conquest | symmetric | YELLOW sightline | 4 | 0.0% | 0/0 | 150.0 | open/open | 1% |
| junglepass_long | asymmetric | YELLOW sightline | 4 | by role | 0/1 | 150.0 | open/4 | - |
| junglepass_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 1% |
| junglepass_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/7 | 53% |
| landingbeach_conquest | symmetric | YELLOW sightline; YELLOW exits | 4 | 5.0% | 0/0 | 150.0 | 1/open | 2% |
| landingbeach_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | 1/4 | - |
| landingbeach_sandbox | symmetric | YELLOW sightline; YELLOW exits | 4 | by role | 0/0 | 150.0 | 1/open | 2% |
| landingbeach_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | 1/7 | 42% |
| launchsite_conquest | symmetric | YELLOW sightline | 4 | 1.0% | 0/0 | 150.0 | open/open | 0% |
| launchsite_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| launchsite_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 0% |
| launchsite_siege | asymmetric | YELLOW sightline | 4 | by role | 0/2 | 150.0 | open/7 | 43% |
| lighthousebay_conquest | symmetric | YELLOW sightline | 4 | 0.8% | 0/1 | 150.0 | open/open | 0% |
| lighthousebay_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| lighthousebay_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/1 | 150.0 | open/open | 0% |
| lighthousebay_siege | asymmetric | YELLOW sightline | 4 | by role | 0/2 | 150.0 | open/7 | 46% |
| metrocity_conquest | symmetric | YELLOW sightline | 4 | 0.8% | 0/0 | 150.0 | open/open | 0% |
| metrocity_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| metrocity_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 0% |
| metrocity_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/7 | 43% |
| openpit_conquest | symmetric | YELLOW sightline | 4 | 4.6% | 0/1 | 134.0 | open/open | 1% |
| openpit_long | asymmetric | YELLOW sightline | 4 | by role | 0/3 | 150.0 | open/4 | - |
| openpit_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/1 | 134.0 | open/open | 1% |
| openpit_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 122.0 | open/7 | 45% |
| orbitalgate_conquest | symmetric | YELLOW sightline | 4 | 1.3% | 0/0 | 150.0 | open/open | 0% |
| orbitalgate_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| orbitalgate_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 0% |
| orbitalgate_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/7 | 47% |
| redrock_conquest | symmetric | YELLOW sightline; YELLOW exits | 4 | 0.0% | 0/1 | 150.0 | 1/open | 1% |
| redrock_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | 1/4 | - |
| redrock_sandbox | symmetric | YELLOW sightline; YELLOW exits | 4 | by role | 0/1 | 150.0 | 1/open | 1% |
| redrock_siege | asymmetric | YELLOW sightline | 4 | by role | 0/1 | 150.0 | 1/7 | 54% |
| rustyard_conquest | symmetric | YELLOW sightline; YELLOW exits | 4 | 0.5% | 0/0 | 150.0 | 1/1 | 1% |
| rustyard_long | asymmetric | YELLOW sightline | 4 | by role | 0/1 | 150.0 | open/4 | - |
| rustyard_sandbox | symmetric | YELLOW sightline; YELLOW exits | 4 | by role | 0/0 | 150.0 | 1/1 | 1% |
| rustyard_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | 1/7 | 48% |
| saltflat_conquest | symmetric | YELLOW sightline | 4 | 1.6% | 0/0 | 150.0 | open/open | 0% |
| saltflat_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| saltflat_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 0% |
| saltflat_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/7 | 43% |
| skyhold_conquest | symmetric | YELLOW sightline; YELLOW exits | 4 | 0.0% | 0/1 | 150.0 | open/1 | 2% |
| skyhold_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| skyhold_sandbox | symmetric | YELLOW sightline; YELLOW exits | 4 | by role | 0/1 | 150.0 | open/1 | 2% |
| skyhold_siege | asymmetric | YELLOW sightline | 4 | by role | 0/1 | 150.0 | open/7 | 42% |
| swamp_conquest | symmetric | YELLOW sightline | 4 | 0.7% | 0/1 | 150.0 | open/open | 1% |
| swamp_long | asymmetric | YELLOW sightline | 4 | by role | 0/1 | 150.0 | open/4 | - |
| swamp_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/1 | 150.0 | open/open | 1% |
| swamp_siege | asymmetric | YELLOW sightline | 4 | by role | 0/3 | 150.0 | open/2 | 44% |
| veyra_old_quarter_conquest | symmetric | YELLOW sightline | 4 | 2.7% | 0/0 | 136.0 | open/open | 0% |
| veyra_old_quarter_long | asymmetric | YELLOW sightline | 4 | by role | 0/1 | 150.0 | open/4 | - |
| veyra_old_quarter_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 136.0 | open/open | 0% |
| veyra_old_quarter_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 136.0 | open/7 | 45% |
| whiteout_conquest | symmetric | YELLOW sightline | 4 | 0.0% | 0/0 | 150.0 | open/open | 0% |
| whiteout_long | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/4 | - |
| whiteout_sandbox | symmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/open | 0% |
| whiteout_siege | asymmetric | YELLOW sightline | 4 | by role | 0/0 | 150.0 | open/7 | 39% |

Sheet: 08_ban_do/Ban_do_cu_diem_bai_tha_can_cu — Bản đồ: cứ điểm, bãi thả, căn cứ, tường (đếm) (100 dòng, 13 cột)

| id | ban_do | so_cu_diem | so_bai_tha | so_can_cu | so_o_can_cu | so_tuyen_tuong | so_o_phao_dai | so_cong_vao | so_lan_ra_canh |
|---|---|---|---|---|---|---|---|---|---|
| ashfield_conquest | ashfield_conquest | 3 | 2 | 2 | 28 | 4 | 0 | 27 | 8 |
| ashfield_long | ashfield_long | 3 | 2 | 1 | 14 | 5 | 28 | 39 | 7 |
| ashfield_sandbox | ashfield_sandbox | 0 | 2 | 0 | 0 | 0 | 0 | 27 | 8 |
| ashfield_siege | ashfield_siege | 0 | 2 | 1 | 14 | 3 | 30 | 27 | 8 |
| borderbridge_conquest | borderbridge_conquest | 3 | 2 | 2 | 28 | 4 | 0 | 28 | 10 |
| borderbridge_long | borderbridge_long | 3 | 2 | 1 | 14 | 3 | 28 | 42 | 10 |
| borderbridge_sandbox | borderbridge_sandbox | 0 | 2 | 0 | 0 | 0 | 0 | 28 | 10 |
| borderbridge_siege | borderbridge_siege | 0 | 2 | 1 | 14 | 3 | 31 | 29 | 9 |
| capital_conquest | capital_conquest | 3 | 2 | 2 | 28 | 4 | 0 | 39 | 21 |
| capital_long | capital_long | 3 | 2 | 1 | 14 | 4 | 28 | 48 | 17 |
| capital_sandbox | capital_sandbox | 0 | 2 | 0 | 0 | 0 | 0 | 39 | 21 |
| capital_siege | capital_siege | 0 | 2 | 1 | 14 | 3 | 29 | 40 | 20 |
| coralisles_conquest | coralisles_conquest | 3 | 2 | 2 | 28 | 4 | 0 | 28 | 8 |
| coralisles_long | coralisles_long | 3 | 2 | 1 | 14 | 5 | 28 | 39 | 8 |
| coralisles_sandbox | coralisles_sandbox | 0 | 2 | 0 | 0 | 0 | 0 | 28 | 8 |

*15 / 100 dòng đầu: xem sheet 08_ban_do/Ban_do_cu_diem_bai_tha_can_cu; in 10 / 13 cột; 1 cột khác (và raw_json, nguon): xem sheet.*

## 16. AI và hệ thống

Trạng thái: Đã áp

Nguồn dữ liệu: 06_ai/Chien_thuat; 06_ai/AI_ho_so_che_do; 06_ai/AI_tham_so; 06_ai/AI_vai_tro; 06_ai/AI_trang_thai. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §16. AI.

- **Chỉ huy AI** (cho cả hai phe): chọn mục tiêu, tập hợp quân rồi tiến theo nhóm, giữ/chiếm cứ điểm, gọi hỏa lực vào cụm địch (không vào quân mình), mua quân khắc chế (địch nhiều máy bay → mua phòng không, nhiều giáp → mua diệt tăng...).
- **Giao thông:** bản đồ làn đường (đường, lộ trình chính, lối hẹp, cổng), cấm đỗ ở cổng/lối hẹp, xe đang đỗ nhường đường theo ưu tiên, nhóm cùng đích không bắt nhau nhường, luân phiên qua cổng, tìm đường vòng có tính chi phí khi bị kẹt.
- **Xe kẹt (prompt 12):** bộ phát hiện xe kẹt (xe có đích mà 8 giây không đi quá 2,5 m) ghi lại lý do, vị trí, vật xung quanh và dữ liệu phát lại; chạy trong bản build nội bộ, báo cáo có bản đồ nhiệt ở Docs/stuck-report. Đã sửa tận gốc: đích luôn quy về vùng xe tới được (không tìm đường tới túi kín hay sau cổng đóng), ô đội hình ở cùng phía tường và không chéo nhau, hai xe đối đầu ngoài bãi trống thì một xe tránh sang bên, lách xe không lao vào tường, đường đi qua chỗ vừa bị chặn (tháp mới dựng) được tính lại ngay, tháp hạ xuống đẩy xe ra khỏi chân tháp, xe pháo đài canh giữ xuất hiện ở chỗ rộng. Pháo đài: cửa phụ và cổng mở của thành trong là cổng đôi 18 m, sân sau cổng để trống, và mọi bãi thả, cổng, mục tiêu có đường rộng 3 ô cho xe lớn nhất khi mọi cổng đóng và mọi ô hardpoint đầy tháp lớn nhất (công cụ dựng map tự bỏ vật cản; Tools/maps/check_access.py kiểm tra mọi map). Lưới an toàn: sau 10 giây xe kẹt được đặt ra chỗ trống, hoặc tạm đi xuyên xe phe mình, hoặc nhích lên theo đường; mỗi lần đều ghi vào báo cáo.
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

Sheet: 06_ai/Chien_thuat — Chiến thuật (16 dòng, 41 cột)

| id | counters | countered_by | prefer | commanders | chapter | check_with | cp | interlude | modules_artillery_prep |
|---|---|---|---|---|---|---|---|---|---|
| air_superiority | hit_and_run | blitz | fighter_jet;stealth_fighter;wingman_drone;sam_launcher;long… | reyes | 3 | sead | 0.15;0.12;0.08;0.08;0.2;0.1;0.22;0.05 | 0 |  |
| all_out | depth | blitz | main_battle_tank;heavy_tank;attack_jet;heavy_bomber | okoye | 10 | breakthrough | 0.3;0.2;0.1;0.1;0.1;0.08;0.07;0.05 | 0 |  |
| ambush | blitz | bounding | tank_destroyer;railgun_truck;fpv_carrier;scout_jeep;ew_jamm… | kerr | 0 |  | 0.15;0.15;0.3;0.1;0.12;0.08;0.02;0.08 | 1 |  |
| attrition | breakthrough | blitz;encircle | mlrs;shahed_truck;ballistic_launcher;lancet_truck;recon_dro… | quist | 8 |  | 0.1;0.1;0.2;0.3;0.1;0.05;0.05;0.1 | 0 |  |
| balanced |  |  |  | kade | 0 |  | 0.25;0.2;0.12;0.12;0.1;0.08;0.05;0.08 | 0 |  |
| base_defence | blitz | firepower;attrition | bunker_vehicle;tank_destroyer;aa_vehicle;mine_layer;enginee… | brandt | 1 |  | 0.25;0.15;0.2;0.15;0.15;0.02;0.0;0.08 | 0 |  |
| blitz | firepower | depth;ambush | armored_car;ifv;wheeled_gun;main_battle_tank;attack_helicop… | mendez | 2 |  | 0.25;0.3;0.1;0.05;0.08;0.1;0.04;0.08 | 0 |  |
| bounding | ambush | blitz;firepower | main_battle_tank;ifv;bmpt;smoke_carrier | kade | 3 |  | 0.3;0.25;0.12;0.1;0.1;0.05;0.0;0.08 | 0 |  |
| breakthrough | depth;encircle | encircle;dispersal | heavy_tank;titan_tank;twin_tank;armored_bulldozer;engineer_… | reyn | 6 | all_out | 0.4;0.15;0.08;0.12;0.1;0.05;0.02;0.08 | 0 |  |
| decapitation | firepower | depth | armored_car;scout_heli;attack_helicopter;lancet_truck;steal… | kerr | 9 |  | 0.12;0.28;0.15;0.1;0.08;0.15;0.07;0.05 | 0 |  |
| depth | blitz;breakthrough | firepower;encircle | bunker_vehicle;tank_destroyer;main_battle_tank;mine_layer;m… | brandt | 1 |  | 0.25;0.15;0.18;0.15;0.12;0.05;0.02;0.08 | 0 |  |
| dispersal | firepower;breakthrough | blitz | armored_car;light_tank;fpv_carrier;mortar_carrier | venn | 6 | hit_and_run | 0.15;0.25;0.15;0.15;0.1;0.1;0.03;0.07 | 0 |  |
| encircle | depth;base_defence | breakthrough | armored_car;ifv;wheeled_gun;light_tank;attack_helicopter | adler | 4 |  | 0.22;0.28;0.15;0.08;0.1;0.1;0.02;0.05 | 0 |  |
| firepower | depth;base_defence | blitz;hit_and_run;dispersal | artillery;mlrs;heavy_rocket_artillery;mortar_carrier;counte… | dahl | 3 |  | 0.2;0.12;0.08;0.3;0.12;0.05;0.05;0.08 | 0 | 1.0 |
| hit_and_run | firepower | blitz;air_superiority | wheeled_gun;armored_car;tank_destroyer;attack_helicopter;st… | mendez | 5 | dispersal | 0.1;0.25;0.25;0.1;0.1;0.12;0.03;0.05 | 0 |  |
| sead |  |  | attack_jet;stealth_fighter;ew_jammer;lancet_truck;ballistic… | reyes | 7 | air_superiority | 0.15;0.12;0.1;0.15;0.1;0.1;0.2;0.08 | 0 |  |

*in 10 / 41 cột; 28 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 06_ai/AI_ho_so_che_do — Hồ sơ AI theo chế độ (20 dòng, 33 cột)

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

*in 10 / 33 cột; 21 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 06_ai/AI_tham_so — Tham số AI (49 dòng, 11 cột)

| id | khoi | tham_so | bac | max | metric | min | reason | value |
|---|---|---|---|---|---|---|---|---|
| economy.airCap | economy | airCap |  | 6.0 | FPS ở trần quân | 6.0 |  | 6.0 |
| economy.attackThreshold | economy | attackThreshold |  | 1.2 | Tỷ lệ thời gian có giao tranh | 1.2 | Tỷ lệ sức mạnh ta / địch tối thiểu | 1.2 |
| economy.baseIncome | economy | baseIncome |  | 1.0 | Số quân trung bình còn sống mỗi phe | 1.0 | Thu nhập khi chưa có cứ điểm | 1.0 |
| economy.escalation/0 | economy | escalation | 0 | 30.0 | Tỷ lệ thời gian có giao tranh | 30.0 | Các bậc sau: khoảng 50, 70, 90 s (bảng luật bên dưới) | 30.0 |
| economy.escalation/1 | economy | escalation | 1 | 50.0 | Tỷ lệ thời gian có giao tranh | 50.0 | Các bậc sau: khoảng 50, 70, 90 s (bảng luật bên dưới) | 50.0 |
| economy.escalation/2 | economy | escalation | 2 | 70.0 | Tỷ lệ thời gian có giao tranh | 70.0 | Các bậc sau: khoảng 50, 70, 90 s (bảng luật bên dưới) | 70.0 |
| economy.escalation/3 | economy | escalation | 3 | 90.0 | Tỷ lệ thời gian có giao tranh | 90.0 | Các bậc sau: khoảng 50, 70, 90 s (bảng luật bên dưới) | 90.0 |
| economy.finalPhase | economy | finalPhase |  | 120 | Tỷ lệ thời gian có giao tranh | 120 | Chế độ giao tranh có pha cuối (ví dụ 2 phút cuối, điểm từ c… | 120 |
| economy.finalPhaseScale | economy | finalPhaseScale |  | 2 | Tỷ lệ thời gian có giao tranh | 2 | Chế độ giao tranh có pha cuối (ví dụ 2 phút cuối, điểm từ c… | 2 |
| economy.groundCap | economy | groundCap |  | 32.0 | FPS ở trần quân | 32.0 | Không chiến thuật nào được nới | 32.0 |
| economy.perPoint | economy | perPoint |  | 0.25 | Số quân trung bình còn sống mỗi phe | 0.25 | Như hiện tại; chỉnh theo dữ liệu game | 0.25 |
| economy.stockCap | economy | stockCap |  | 30.0 | Số quân trung bình còn sống mỗi phe | 30.0 | Chỉ huy Vault: 45 | 30.0 |
| economy.stockCapVault | economy | stockCapVault |  | 45.0 | Số quân trung bình còn sống mỗi phe | 45.0 | Chỉ huy Vault: 45 | 45.0 |
| economy.useOrLoseRamp | economy | useOrLoseRamp |  | 30.0 | Số quân trung bình còn sống mỗi phe | 30.0 | Từ ngưỡng mặc định xuống ngưỡng thấp nhất | 30.0 |
| economy.useOrLoseThreshold | economy | useOrLoseThreshold |  | 0.9 | Số quân trung bình còn sống mỗi phe | 0.9 | Khi đã chạm trần quân và CP đầy | 0.9 |

*15 / 49 dòng đầu: xem sheet 06_ai/AI_tham_so.*

Sheet: 06_ai/AI_vai_tro — Vai trò đơn vị (28 dòng, 5 cột)

| id | engage | overwhelmed |
|---|---|---|
| Arty |  | Scoot |
| AttackHeli | 0.85;1.0 | Rearm |
| Bomber |  | Hold |
| Bunker |  | Hold |
| CAS | 0.6;1.0 | Rearm |
| Drone |  | Hold |
| Fighter | 0.8;1.0 | Rearm |
| Flame |  | Hold |
| Gunship |  | Shift |
| GunshipHeli | 0.7;0.9 | Rearm |
| Heavy | 0.6;0.8 | Hold |
| IFV | 0.7;0.9 | Shift |
| Laser |  | Smoke |
| Light | 0.85;1.0 | Hold |
| MBT | 0.75;0.9 | Cover |
| MLRS |  | Scoot |
| Rail | 0.9;1.0 | Shift |
| Recon |  | Shift |
| SAM | 0.8;1.0 | Shift |
| SPAAG | 0.7;0.9 | Hold |
| ScoutHeli | 0.9;1.0 | Rearm |
| Siege |  | Hold |
| Stealth | 0.9;1.0 | Shift |
| Strike |  | Scoot |
| Support |  | Hold |
| TD | 0.9;1.0 | Shift |
| UAV | 0.9;1.0 | Shift |
| VBIED |  | Hold |

Sheet: 06_ai/AI_trang_thai — Trạng thái đội (7 dòng, 5 cột)

| id | commit | priority |
|---|---|---|
| APPROACH | 3.0 | 2 |
| COMBAT | 4.0 | 3 |
| FLANK | 6.0 | 2 |
| HOLD | 5.0 | 2 |
| OVERWATCH | 4.0 | 2 |
| REGROUP | 3.0 | 3 |
| TRAVEL | 4.0 | 1 |

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

## 19. Hình ảnh

Trạng thái: Đã áp

Nguồn dữ liệu: 10_model_tai_san/Anh_the; 10_model_tai_san/Anh_chup. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §19. Hình ảnh, §20. Thư viện hình ảnh.

#### 19. Hình ảnh

![Mô hình đạn: tên lửa chống tăng và phòng không vác vai.](../images/10_model_tai_san/r6_munitions_1.png)

*Hình: Mô hình đạn: tên lửa chống tăng và phòng không vác vai. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Tên lửa không đối không, phòng không, không đối đất.](../images/10_model_tai_san/r6_munitions_2.png)

*Hình: Tên lửa không đối không, phòng không, không đối đất. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Rocket.](../images/10_model_tai_san/r6_munitions_3.png)

*Hình: Rocket. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Bom và drone.](../images/10_model_tai_san/r6_munitions_4.png)

*Hình: Bom và drone. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Đạn pháo, đạn cối, đạn xuyên, đạn railgun.](../images/10_model_tai_san/r6_munitions_5.png)

*Hình: Đạn pháo, đạn cối, đạn xuyên, đạn railgun. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Mô hình mới: Ka-52, Su-25, pháo công thành, Inferno, Tempest, Hive, Bastion, Spectre.](../images/10_model_tai_san/r6_new_models.png)

*Hình: Mô hình mới: Ka-52, Su-25, pháo công thành, Inferno, Tempest, Hive, Bastion, Spectre. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Súng phun lửa làm lại: luồng nhiên liệu cong, cầu lửa cuộn, khói đen.](../images/10_model_tai_san/r6_flame.png)

*Hình: Súng phun lửa làm lại: luồng nhiên liệu cong, cầu lửa cuộn, khói đen. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Railgun: nạp năng lượng, tia sáng lưu lại.](../images/10_model_tai_san/r6_railgun.png)

*Hình: Railgun: nạp năng lượng, tia sáng lưu lại. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Boss chết: nổ nhiều đợt, lóe trắng, sóng xung kích.](../images/10_model_tai_san/r6_boss_death.png)

*Hình: Boss chết: nổ nhiều đợt, lóe trắng, sóng xung kích. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Kiểm tra đầu nòng: mỗi chấm màu là nơi một vũ khí bắn ra.](../images/10_model_tai_san/r6_muzzle_audit.png)

*Hình: Kiểm tra đầu nòng: mỗi chấm màu là nơi một vũ khí bắn ra. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

#### 20. Thư viện hình ảnh

Ảnh render từ mô hình 3D của game (cùng ảnh dùng cho thẻ), ảnh chụp trong trận, các bảng hiệu ứng và bản đồ nhiệt.

![Docs/doc-images/r6/supports.png](../images/10_model_tai_san/r6_supports.png)

*Hình: Docs/doc-images/r6/supports.png. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Docs/doc-images/shots/battle1.png](../images/10_model_tai_san/shots_battle1.png)

*Hình: Docs/doc-images/shots/battle1.png. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Docs/doc-images/shots/battle2.png](../images/10_model_tai_san/shots_battle2.png)

*Hình: Docs/doc-images/shots/battle2.png. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Docs/doc-images/shots/boss.png](../images/10_model_tai_san/shots_boss.png)

*Hình: Docs/doc-images/shots/boss.png. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Docs/doc-images/shots/defend.png](../images/10_model_tai_san/shots_defend.png)

*Hình: Docs/doc-images/shots/defend.png. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Docs/doc-images/shots/edge.png](../images/10_model_tai_san/shots_edge.png)

*Hình: Docs/doc-images/shots/edge.png. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Docs/doc-images/shots/hd.png](../images/10_model_tai_san/shots_hd.png)

*Hình: Docs/doc-images/shots/hd.png. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Docs/doc-images/shots/hunt.png](../images/10_model_tai_san/shots_hunt.png)

*Hình: Docs/doc-images/shots/hunt.png. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![Docs/doc-images/shots/siege.png](../images/10_model_tai_san/shots_siege.png)

*Hình: Docs/doc-images/shots/siege.png. Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

Sheet: 10_model_tai_san/Anh_the — Ảnh thẻ (241 dòng, 7 cột)

| id | model | hash | kind | source |
|---|---|---|---|---|
| aa_57mm_vehicle | aa_57mm_vehicle | v2:bee71d1a6cc830be5788b6e1f0413408c5def34f | vehicle | Models/aa_57mm_vehicle |
| aa_gun_tower | aa_gun_tower | v2:1025a648efa86c1a0f59d2dc0ae2a29a4aad7e0a | tower | Models/aa_gun_tower |
| aa_gun_vehicle | aa_gun_vehicle | v2:eabe9ddd7406a58560f750dfcff157f149cc737f | vehicle | Models/aa_gun_vehicle |
| aa_turret | aa_turret | v2:8e6d00e266ceabf8144865cadf4698469e56c52d | tower | Models/aa_turret |
| aa_turret.flak | aa_turret_a | v2:88bfa5196b539f88f3b14802e198760b04a3ef74 | tower | Models/aa_turret_a |
| aa_turret.sam | aa_turret_b | v2:7e53712ff36be3f744fd6f2b6aada66cf57615d1 | tower | Models/aa_turret_b |
| aa_vehicle | aa_vehicle | v2:1289d1f47da30d893895ed85aecd655e3cfd9e3a | vehicle | Models/aa_vehicle_hd |
| aerial_tanker | aerial_tanker | v2:ec43c999483b9d865ae4076d882d2a2b72d2f367 | vehicle | Models/aerial_tanker |
| airborne_light_tank | airborne_light_tank | v2:1a7e46957def37e7b3fb34242a576a3bcd2145c2 | vehicle | Models/airborne_light_tank |
| airborne_vehicle | airborne_vehicle | v2:ea40410f88ec13e047b1f3f76f4daab0374f2f8e | vehicle | Models/airborne_vehicle |
| airfield | helipad | v2:8632041388de13a52d29dd466a586f52537c2c7f | tower | Models/helipad |
| airfield.hangar | helipad_a | v2:50d7f6fdbd14fc77ec64f4f7af9c3edcec4ffaef | tower | Models/helipad_a |
| airfield.service | helipad_b | v2:2d958e133edb19b63ebf5fdf1b49ead6a07c2014 | tower | Models/helipad_b |
| ammo_carrier | ammo_carrier | v2:c50fe4b2c580acfcb7a71103f48365d7b686c387 | vehicle | Models/ammo_carrier |
| ammo_depot | ammo_dump | v2:9d916519cf62f2a2b36cafdfde3845217891da6d | tower | Models/ammo_dump |

*15 / 241 dòng đầu: xem sheet 10_model_tai_san/Anh_the.*

Sheet: 10_model_tai_san/Anh_chup — Ảnh chụp (47 dòng, 12 cột)

| id | nguon_anh | loai | muc | tieu_de_muc | chu_thich | rong_px | cao_px | thuoc_do | trang_thai |
|---|---|---|---|---|---|---|---|---|---|
| images/02_phuong_tien/r6_supports.png | Docs/doc-images/r6/supports.png | review | 12 | Hỗ trợ hỏa lực | Clip Xem bắn của các thẻ hỗ trợ (pháo kích, không kích, tên… | 1280 | 2880 | ảnh chụp, không lưới mét; thước: Tăng chủ lực main_battle_t… | present |
| images/02_phuong_tien/shots_hd.png | Docs/doc-images/shots/hd.png | review | 8 | Phương tiện | Model thường và model chi tiết (đồ họa Cao) của 12 xe phổ b… | 1500 | 1418 | ảnh chụp, không lưới mét; thước: Tăng chủ lực main_battle_t… | present |
| images/05_che_do_kinh_te/shots_battle1.png | Docs/doc-images/shots/battle1.png | review | 1 | Tổng quan | Trong trận (ảnh 3D; HUD ở ảnh này là bản trước phase 10, HU… | 1500 | 730 | ảnh chụp, không lưới mét; thước: Tăng chủ lực main_battle_t… | present |
| images/05_che_do_kinh_te/shots_battle2.png | Docs/doc-images/shots/battle2.png | review | 1 | Tổng quan | Bản đồ sa mạc Dunebreak sau khi phóng to 50%; nhà cửa đã ch… | 1500 | 730 | ảnh chụp, không lưới mét; thước: Tăng chủ lực main_battle_t… | present |
| images/05_che_do_kinh_te/shots_boss.png | Docs/doc-images/shots/boss.png | review | 2 | Chế độ chơi | Boss. | 1500 | 730 | ảnh chụp, không lưới mét; thước: Tăng chủ lực main_battle_t… | present |
| images/05_che_do_kinh_te/shots_defend.png | Docs/doc-images/shots/defend.png | review | 2 | Chế độ chơi | Phòng thủ căn cứ. | 1500 | 730 | ảnh chụp, không lưới mét; thước: Tăng chủ lực main_battle_t… | present |
| images/05_che_do_kinh_te/shots_hunt.png | Docs/doc-images/shots/hunt.png | review | 2 | Chế độ chơi | Nhiệm vụ săn: mục tiêu hiện hình thoi đỏ trên bản đồ nhỏ. | 1500 | 730 | ảnh chụp, không lưới mét; thước: Tăng chủ lực main_battle_t… | present |
| images/05_che_do_kinh_te/shots_siege.png | Docs/doc-images/shots/siege.png | review | 2 | Chế độ chơi | Công thành. | 1500 | 730 | ảnh chụp, không lưới mét; thước: Tăng chủ lực main_battle_t… | present |
| images/09_hieu_ung_am_thanh/tier_T0_fire_0.2s.png | Builds/effect_shots/tier_T0/fire_0.2s.png | fx | 20b | Hiệu ứng theo bậc và xác vỡ | tier_T0 fire_0.2s |  |  | m: lưới 1 m (vạch 5 m đậm), vòng lõi đỏ, vòng rìa cam; Tăng… | pending |
| images/09_hieu_ung_am_thanh/tier_T0_impact_0.5s.png | Builds/effect_shots/tier_T0/impact_0.5s.png | fx | 20b | Hiệu ứng theo bậc và xác vỡ | tier_T0 impact_0.5s |  |  | m: lưới 1 m (vạch 5 m đậm), vòng lõi đỏ, vòng rìa cam; Tăng… | pending |
| images/09_hieu_ung_am_thanh/tier_T1_fire_0.2s.png | Builds/effect_shots/tier_T1/fire_0.2s.png | fx | 20b | Hiệu ứng theo bậc và xác vỡ | tier_T1 fire_0.2s |  |  | m: lưới 1 m (vạch 5 m đậm), vòng lõi đỏ, vòng rìa cam; Tăng… | pending |
| images/09_hieu_ung_am_thanh/tier_T1_impact_0.5s.png | Builds/effect_shots/tier_T1/impact_0.5s.png | fx | 20b | Hiệu ứng theo bậc và xác vỡ | tier_T1 impact_0.5s |  |  | m: lưới 1 m (vạch 5 m đậm), vòng lõi đỏ, vòng rìa cam; Tăng… | pending |
| images/09_hieu_ung_am_thanh/tier_T2_fire_0.2s.png | Builds/effect_shots/tier_T2/fire_0.2s.png | fx | 20b | Hiệu ứng theo bậc và xác vỡ | tier_T2 fire_0.2s |  |  | m: lưới 1 m (vạch 5 m đậm), vòng lõi đỏ, vòng rìa cam; Tăng… | pending |
| images/09_hieu_ung_am_thanh/tier_T2_impact_0.5s.png | Builds/effect_shots/tier_T2/impact_0.5s.png | fx | 20b | Hiệu ứng theo bậc và xác vỡ | tier_T2 impact_0.5s |  |  | m: lưới 1 m (vạch 5 m đậm), vòng lõi đỏ, vòng rìa cam; Tăng… | pending |
| images/09_hieu_ung_am_thanh/tier_T3_fire_0.2s.png | Builds/effect_shots/tier_T3/fire_0.2s.png | fx | 20b | Hiệu ứng theo bậc và xác vỡ | tier_T3 fire_0.2s |  |  | m: lưới 1 m (vạch 5 m đậm), vòng lõi đỏ, vòng rìa cam; Tăng… | pending |

*15 / 47 dòng đầu: xem sheet 10_model_tai_san/Anh_chup.*

## 20. Âm thanh

Trạng thái: Một phần — cần đọc mã (NEED_CODE_CHECK) (sheet Am_thanh_mixer)

Nguồn dữ liệu: 09_hieu_ung_am_thanh/Am_thanh; 09_hieu_ung_am_thanh/Am_thanh_bank; 09_hieu_ung_am_thanh/Am_thanh_loat; 09_hieu_ung_am_thanh/Am_thanh_mixer; 09_hieu_ung_am_thanh/Am_thanh_thu_vien; 09_hieu_ung_am_thanh/Am_thanh_mau. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §16b. Hiệu ứng.

Hình và tiếng chỉ là hiển thị, không đổi kết quả mô phỏng. Hiệu ứng bậc được **vẽ lại** và chồng lên vụ nổ sẵn có của viên đạn (không vụ nổ nào nhỏ đi). Giới hạn chi tiết đầy đủ cùng lúc: T5 1, T4 3, T3 6; xa camera thì rút gọn (dưới 70 m đầy đủ, dưới 140 m 45%). Âm thanh tổng hợp bằng script (Tools/sfx/build_sfx.py, không dùng AI), mỗi phát ba lớp trộn sẵn: cơ cấu, tiếng nổ, đuôi vang. 32 kênh, từ 24 kênh bận thì tiếng mới dưới ưu tiên 60 chỉ chiếm kênh kém quan trọng nhất. Số liệu cảnh thử tải: Docs/balance/p34_stress_counts.json (cảnh `-mb-play -mb-lighthousebay -mb-p34stress`; FPS: NEED PROFILE).

#### Bắn, nổ và tiếng theo bậc

| Bậc | Phát bắn | Vụ nổ | Camera | Tiếng |
|---|---|---|---|---|
| T0 | Chớp mảnh của vũ khí | Nổ nhỏ (công thức Small) | — | shot_t0: tiếng giòn 35 ms, đuôi 0,08 s; súng nhỏ thành cụm đấu súng |
| T1 | Khói mỏng | Nổ nhỏ, đạn nổ trên không giữ chùm mảnh | — | shot_t1; cụm đấu súng từ khẩu thứ ba trong 20 m |
| T2 | Chớp vừa, khói ngắn | Cầu lửa nhỏ nóng, bụi và đất | — | shot_t2, blast_he_t2; ưu tiên 25-30 |
| T3 | Chớp lớn cháy lâu, cầu lửa đầu nòng, khói dài, vòng bụi, thân xe giật lùi | Cầu lửa vừa, cột bụi 5 cuộn, hố sáng nhỏ | — | shot_t3, blast_he_t3; ưu tiên 40 gần |
| T4 | Chớp rất lớn, hai cầu lửa, khói cuộn, vòng áp suất, mặt đất sáng; tàu: vòng nước và bụi nước | Cầu lửa cuộn lớn, cột 8 cuộn, mảnh văng, hai váy bụi; sóng xung kích trên rìa | Rung 0,22 (chỉ trên màn hình, trong 90 m) | shot_t4, blast_he_t4, tiếng rền dưới; ưu tiên 50 gần |
| T5 | Chớp sáng cả cảnh, khói rất dài, vòng áp suất đôi, hai vòng nước | Cầu lửa rất lớn, cột 10 cuộn thành mũ nấm nhỏ, mảnh xa, ba váy bụi, hố sáng 12 s; vòng trên lõi rồi rìa | Rung 0,6 | shot_t5, blast_he_t5; ưu tiên 60 (giữ 8 kênh cuối cho cảnh báo và T5 / boss) |

#### Xác vỡ theo lớp xe

Xác sống 30-45 s (boss 90 s), cháy 40% thời gian đó; tối đa khoảng 12 xác đầy đủ gần camera (Trung bình 9, Thấp 6), để lại vết cháy. Mảnh vỡ chỉ là hình: không có collider, không chặn đường hay tầm nhìn.

| Lớp | Cách vỡ |
|---|---|
| Xích (tăng; cả tàu hỏa) | Tháp pháo văng, thân cháy |
| Bánh lốp | Hai bánh văng xoáy, khung lật nghiêng hoặc ngửa trong 0,9 s |
| Xe tải | Hàng nổ dây chuyền 4-6 tiếng dọc thùng, thùng cháy |
| Pháo | Đạn trong xe nổ 6-9 tiếng, cột lửa 2-3,5 s, tháp văng một nửa số lần |
| Tiêm kích | Mất một cánh kéo lửa, xoáy ốc rơi |
| Trực thăng | Rotor đuôi văng, rotor chính bay mất, xoay ngày càng nhanh |
| Máy bay lớn | Mất cánh, động cơ cháy, rơi dài và nghiêng |
| Tàu | Nghiêng, gãy đôi (từ 24 m) và chìm; xuồng lật |
| Drone | Một tiếng nổ nhỏ, không còn gì |

#### Màn xem trước theo môi trường

Xem bắn, chi tiết xe / boss / tháp: đơn vị đứng đúng chỗ của nó. Cảnh tạm đúng loại cho tới khi tài sản biome, mặt nước và đường ray của prompt 33 được gộp vào. Bắn thử dùng đúng hiệu ứng và tiếng theo bậc; mỗi viên nổ hiện vòng rìa và lõi đúng cỡ vùng sát thương.

| Môi trường | Cảnh | Đơn vị |
|---|---|---|
| Mặt đất | Đất theo biome của bản đồ đang chọn (mặc định ôn đới) | Xe mặt đất, boss mặt đất |
| Biển | Mặt biển có sóng, mục tiêu đứng trên bờ phía trước | Tàu, xuồng, boss biển |
| Mép nước | Nửa sau trên nước, nửa trước trên bờ | Xe lội nước, đệm khí |
| Đường ray | Đoạn ray (đá ballast, tà vẹt, hai ray, ụ chặn) | Tàu hỏa, Juggernaut, Nemesis, Gungnir |
| Trên không | Bay vòng / lơ lửng, đất ở phía dưới | Máy bay, trực thăng, boss bay |
| Ô căn cứ | Bệ bê tông, viền tối, dấu góc | Tháp |
| Bờ biển | Pháo bờ biển trên bệ ở bờ, một tàu ngoài biển làm mục tiêu | Khẩu đội bờ biển |

Báo cáo chi tiết trong repo: `Docs/audio/metrics.md`; `Docs/audio/diagnosis.md`.

Sheet: 09_hieu_ung_am_thanh/Am_thanh — Âm thanh: clip (229 dòng, 14 cột)

| id | bank | nhom | duong_dan | do_dai_s | kenh | tan_so_mau_hz | nen | tac_gia | nguon_goc |
|---|---|---|---|---|---|---|---|---|---|
| Music/battle_1 |  | Music | Assets/MachineBrigade/Resources/Audio/Music/battle_1.ogg | 135.0 | 2 | 44100 | ogg | Armored Advance | Assets/MachineBrigade/Resources/Audio/Music/MUSIC_CREDITS.md |
| Music/battle_2 |  | Music | Assets/MachineBrigade/Resources/Audio/Music/battle_2.ogg | 132.414 | 2 | 44100 | ogg | Iron Rain | Assets/MachineBrigade/Resources/Audio/Music/MUSIC_CREDITS.md |
| Music/battle_3 |  | Music | Assets/MachineBrigade/Resources/Audio/Music/battle_3.ogg | 139.13 | 2 | 44100 | ogg | Air Superiority | Assets/MachineBrigade/Resources/Audio/Music/MUSIC_CREDITS.md |
| Music/boss |  | Music | Assets/MachineBrigade/Resources/Audio/Music/boss.ogg | 125.217 | 2 | 44100 | ogg | Colossus | Assets/MachineBrigade/Resources/Audio/Music/MUSIC_CREDITS.md |
| Music/defeat |  | Music | Assets/MachineBrigade/Resources/Audio/Music/defeat.ogg | 9.5 | 2 | 44100 | ogg | Defeat (stinger) | Assets/MachineBrigade/Resources/Audio/Music/MUSIC_CREDITS.md |
| Music/menu |  | Music | Assets/MachineBrigade/Resources/Audio/Music/menu.ogg | 108.0 | 2 | 44100 | ogg | Command Briefing | Assets/MachineBrigade/Resources/Audio/Music/MUSIC_CREDITS.md |
| Music/siege |  | Music | Assets/MachineBrigade/Resources/Audio/Music/siege.ogg | 115.556 | 2 | 44100 | ogg | Hold the Line | Assets/MachineBrigade/Resources/Audio/Music/MUSIC_CREDITS.md |
| Music/victory |  | Music | Assets/MachineBrigade/Resources/Audio/Music/victory.ogg | 8.621 | 2 | 44100 | ogg | Victory (stinger) | Assets/MachineBrigade/Resources/Audio/Music/MUSIC_CREDITS.md |
| autocannon/autocannon_1 | autocannon | shot | Assets/MachineBrigade/Resources/Audio/autocannon/autocannon… | 0.695 | 1 | 44100 | ogg | Fascinated Sound | The Gun Locker SFX Pack: "Automatic Cannon - MK44 - 03 - Si… |
| autocannon/autocannon_2 | autocannon | shot | Assets/MachineBrigade/Resources/Audio/autocannon/autocannon… | 0.695 | 1 | 44100 | ogg | Fascinated Sound | The Gun Locker SFX Pack: "Automatic Cannon - MK44 - 03 - Si… |
| autocannon/autocannon_3 | autocannon | shot | Assets/MachineBrigade/Resources/Audio/autocannon/autocannon… | 0.682 | 1 | 44100 | ogg | Fascinated Sound | The Gun Locker SFX Pack: "Automatic Cannon - MK44 - 03 - Si… |
| cannon/cannon_1 | cannon | shot | Assets/MachineBrigade/Resources/Audio/cannon/cannon_1.ogg | 1.5 | 1 | 44100 | ogg | Bluezone Corporation | Tank - Explosion Sound Effects: "Bluezone_BC0271_tank_artil… |
| cannon/cannon_2 | cannon | shot | Assets/MachineBrigade/Resources/Audio/cannon/cannon_2.ogg | 1.5 | 1 | 44100 | ogg | Pole Position Production | The Warfare Library: "warfare_t1b_cannon_firing_forest_dist… |
| cannon/cannon_3 | cannon | shot | Assets/MachineBrigade/Resources/Audio/cannon/cannon_3.ogg | 1.384 | 1 | 44100 | ogg | Pole Position Production | The Warfare Library: "warfare_t1b_cannon_firing_forest_dist… |
| click/click_1 |  | click | Assets/MachineBrigade/Resources/Audio/click/click_1.ogg | 0.092 | 1 | 44100 | ogg | Kenney (www.kenney.nl) | UI Audio pack ("click1.ogg") |

*15 / 229 dòng đầu: xem sheet 09_hieu_ung_am_thanh/Am_thanh; in 10 / 14 cột; 1 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 09_hieu_ung_am_thanh/Am_thanh_bank — Âm thanh: bank (87 dòng, 9 cột)

| id | so_clip | group | kept | row | size | variants |
|---|---|---|---|---|---|---|
| autocannon | 3 | shot | TRUE |  |  |  |
| blast_air_s1 | 2 | blast_air |  |  | s1 | 2 |
| blast_air_s2 | 2 | blast_air |  |  | s2 | 2 |
| blast_air_s3 | 2 | blast_air |  |  | s3 | 2 |
| blast_bomb | 3 | blast |  | blast | bomb | 3 |
| blast_he_s1 | 3 | blast |  | blast | s1 | 3 |
| blast_he_s2 | 3 | blast |  | blast | s2 | 3 |
| blast_he_s3 | 3 | blast |  | blast | s3 | 3 |
| blast_he_s4 | 3 | blast |  | blast | s4 | 3 |
| blast_he_s406 | 2 | blast |  | blast | s406 | 2 |
| blast_heat_s2 | 2 | blast_heat |  |  | s2 | 2 |
| blast_heat_s3 | 2 | blast_heat |  |  | s3 | 2 |
| blast_super | 2 | blast |  | blast | super | 2 |
| blast_thermo_s3 | 2 | blast_thermo |  |  | s3 | 2 |
| blast_thermo_s4 | 2 | blast_thermo |  |  | s4 | 2 |

*15 / 87 dòng đầu: xem sheet 09_hieu_ung_am_thanh/Am_thanh_bank.*

Sheet: 09_hieu_ung_am_thanh/Am_thanh_loat — Âm thanh: loạt bắn nhanh (7 dòng, 7 cột)

| id | bank | co | nhip_phat_s | so_phat |
|---|---|---|---|---|
| burst_s0_10 | burst_s0_10 | S0 | 10 | 3 |
| burst_s0_16 | burst_s0_16 | S0 | 16 | 5 |
| burst_s0_55 | burst_s0_55 | S0 | 55 | 18 |
| burst_s1_10 | burst_s1_10 | S1 | 10 | 3 |
| burst_s1_22 | burst_s1_22 | S1 | 22 | 7 |
| burst_s1_35 | burst_s1_35 | S1 | 35 | 12 |
| burst_s1_55 | burst_s1_55 | S1 | 55 | 18 |

Sheet: 09_hieu_ung_am_thanh/Am_thanh_mixer — Âm thanh: mixer (1 dòng, 5 cột)

| id | trang_thai | ghi_chu |
|---|---|---|
| chua_ap | NEED_CODE_CHECK | AudioDirector.cs / EffectsLimiter.cs (hằng trong mã; Docs/a… |

Sheet: 09_hieu_ung_am_thanh/Am_thanh_thu_vien — Âm thanh: thư viện (1 dòng, 8 cột)

| id | khoa | gia_tri_chu |
|---|---|---|
| note | note | Fix pass L7: the sound library (Tools/sfx/build_sfx.py); si… |

Sheet: 09_hieu_ung_am_thanh/Am_thanh_mau — Âm thanh: bản ghi mẫu (3 dòng, 29 cột)

| id | tep | do_dai_s | kenh | tan_so_mau_hz | lufs_mmax_tinh | so_moc | events | played | cooldown |
|---|---|---|---|---|---|---|---|---|---|
| boss_battle | Docs/audio/samples/boss_battle.ogg | 48.0 | 2 | 44100 | -13.9 | 8 | 1288 | 972 | 261 |
| crowded_battle | Docs/audio/samples/crowded_battle.ogg | 43.0 | 2 | 44100 | -15.0 | 8 | 5930 | 1830 | 2802 |
| normal_battle | Docs/audio/samples/normal_battle.ogg | 43.0 | 2 | 44100 | -15.6 | 8 | 1150 | 739 | 251 |

*in 10 / 29 cột; 17 cột khác (và raw_json, nguon): xem sheet.*

### 20b. Hiệu ứng theo bậc và xác vỡ

Trạng thái: Một phần — cần đọc mã (NEED_CODE_CHECK) (sheet Xac_vo)

Nguồn dữ liệu: 09_hieu_ung_am_thanh/VFX_bac; 09_hieu_ung_am_thanh/VFX_chay_than_xe; 09_hieu_ung_am_thanh/VFX_vu_khi; 09_hieu_ung_am_thanh/Xac_vo; 09_hieu_ung_am_thanh/Hau_ky_hinh_anh.

#### Ảnh hiệu ứng theo bậc (Unity, EffectShots.FxBatch)

*Ảnh chờ (pending): ảnh hiệu ứng nằm ngoài repo (Builds/effect_shots của máy chạy Unity, EffectShots.FxBatch). Chạy lại `python Tools/export/export.py --effect-shots <thư mục>` để chèn. Đơn vị khi có ảnh: m, thước so sánh Tăng chủ lực (main_battle_tank).*

Sheet: 09_hieu_ung_am_thanh/VFX_bac — VFX theo bậc (6 dòng, 21 cột)

| id | bac | rung_camera_dong_thoi | ban_dust_ring | ban_flash | ban_flash_life | ban_light | ban_pressure | ban_puff_life | ban_puff_life_arg0 |
|---|---|---|---|---|---|---|---|---|---|
| T0 | 0 | XEM_VFX_ngan_sach | 0 | 0 | 0 | 0 | 0 | zero |  |
| T1 | 1 | XEM_VFX_ngan_sach | 0 | 0 | 0 | 0 | 0 |  | 1.2 |
| T2 | 2 | XEM_VFX_ngan_sach | 0 | 1.2 | 0.1 | 0 | 0 |  | 1.8 |
| T3 | 3 | XEM_VFX_ngan_sach | 8 | 2.4 | 0.16 | 9 | 0 |  | 3.5 |
| T4 | 4 | XEM_VFX_ngan_sach | 16 | 3.6 | 0.24 | 16 | 7 |  | 5 |
| T5 | 5 | XEM_VFX_ngan_sach | 26 | 5 | 0.34 | 28 | 12 |  | 7 |

*in 10 / 21 cột; 9 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 09_hieu_ung_am_thanh/VFX_chay_than_xe — VFX: lửa thân xe (3 dòng, 14 cột)

| id | bodies | embers | low_tongues | power | reach_m | size | smoke_alpha | smoke_shade | smoke_size |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 1 | 0.5 | 1 | 2.8 | 4.5 | 1 | 0.6 | 0.34 | 1 |
| 1 | 1 | 1.1 | 1 | 4 | 6 | 1.2 | 0.74 | 0.16 | 1.15 |
| 2 | 2 | 1.8 | 2 | 5.2 | 7.5 | 1.45 | 0.8 | 0.06 | 1.35 |

*in 10 / 14 cột; 2 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 09_hieu_ung_am_thanh/VFX_vu_khi — VFX theo vũ khí (70 dòng, 14 cột)

| id | loai | vu_khi | bac | co_mm | so_nong | loat | don_vi_mang | thu_muc | so_anh |
|---|---|---|---|---|---|---|---|---|---|
| amos_120 | vu_khi | amos_120 | 3 | 120 | 1 | FALSE | sp_mortar | Builds/effect_shots/amos_120/ | 8 |
| bastion_gun | vu_khi | bastion_gun | 3 | 152 | 2 | TRUE | headquarters;headquarters.fortress_air;headquarters.fortres… | Builds/effect_shots/bastion_gun/ | 10 |
| boss_howitzer | vu_khi | boss_howitzer | 4 | 203 | 1 | FALSE | howitzer_203 | Builds/effect_shots/boss_howitzer/ | 8 |
| boss_rockets | vu_khi | boss_rockets | 3 | 122 | 1 | FALSE | armored_train;rocket_pod | Builds/effect_shots/boss_rockets/ | 8 |
| boss_thermo | vu_khi | boss_thermo | 4 | 220 | 1 | FALSE | behemoth_inferno | Builds/effect_shots/boss_thermo/ | 8 |
| caesar_155 | vu_khi | caesar_155 | 3 | 155 | 1 | FALSE | wheeled_howitzer | Builds/effect_shots/caesar_155/ | 8 |
| casemate_155 | vu_khi | casemate_155 | 3 | 155 | 1 | FALSE | casemate_155 | Builds/effect_shots/casemate_155/ | 8 |
| cruiser_203 | vu_khi | cruiser_203 | 4 | 203 | 2 | TRUE | sea_cruiser | Builds/effect_shots/cruiser_203/ | 10 |
| grad_cluster | vu_khi | grad_cluster | 3 | 122 | 1 | FALSE | elite_grad | Builds/effect_shots/grad_cluster/ | 8 |
| gun_105_apfsds | vu_khi | gun_105_apfsds | 3 | 125 | 1 | FALSE | elite_tank_destroyer | Builds/effect_shots/gun_105_apfsds/ | 8 |
| gun_105_long | vu_khi | gun_105_long | 3 | 125 | 1 | FALSE | tank_destroyer | Builds/effect_shots/gun_105_long/ | 8 |
| gun_105_wheeled | vu_khi | gun_105_wheeled | 3 | 120 | 1 | FALSE | wheeled_gun | Builds/effect_shots/gun_105_wheeled/ | 8 |
| gun_120_twin | vu_khi | gun_120_twin | 3 | 120 | 1 | FALSE | twin_tank | Builds/effect_shots/gun_120_twin/ | 8 |
| gun_120mm | vu_khi | gun_120mm | 3 | 120 | 1 | FALSE | main_battle_tank;mara_behemoth;side_gun_120;turret_120;turt… | Builds/effect_shots/gun_120mm/ | 8 |
| gun_125_armata_ke | vu_khi | gun_125_armata_ke | 3 | 125 | 1 | FALSE | next_gen_tank;towed_at_gun | Builds/effect_shots/gun_125_armata_ke/ | 8 |

*15 / 70 dòng đầu: xem sheet 09_hieu_ung_am_thanh/VFX_vu_khi; in 10 / 14 cột; 2 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 09_hieu_ung_am_thanh/Xac_vo — Xác vỡ (1 dòng, 5 cột)

| id | trang_thai | ghi_chu |
|---|---|---|
| chua_ap | NEED_CODE_CHECK | Assets/MachineBrigade/Scripts/Game/Effects/WreckClasses.cs… |

Sheet: 09_hieu_ung_am_thanh/Hau_ky_hinh_anh — Hậu kỳ hình ảnh (52 dòng, 8 cột)

| id | hieu_ung | thiet_lap | ghi_de | gia_tri | dimension |
|---|---|---|---|---|---|
| BattlefieldProfile.m_Enabled | BattlefieldProfile | m_Enabled |  | 1 |  |
| BattlefieldProfile.m_Name | BattlefieldProfile | m_Name |  | BattlefieldProfile |  |
| Bloom.active | Bloom | active |  | 1 |  |
| Bloom.clamp | Bloom | clamp | 1 | 6 |  |
| Bloom.dirtIntensity | Bloom | dirtIntensity | 0 | 0 |  |
| Bloom.dirtTexture | Bloom | dirtTexture | 0 | {fileID: 0} | 1 |
| Bloom.downscale | Bloom | downscale | 0 | 0 |  |
| Bloom.filter | Bloom | filter | 0 | 0 |  |
| Bloom.highQualityFiltering | Bloom | highQualityFiltering | 1 | 1 |  |
| Bloom.intensity | Bloom | intensity | 1 | 0.45 |  |
| Bloom.m_Enabled | Bloom | m_Enabled |  | 1 |  |
| Bloom.m_Name | Bloom | m_Name |  | Bloom |  |
| Bloom.maxIterations | Bloom | maxIterations | 0 | 6 |  |
| Bloom.scatter | Bloom | scatter | 1 | 0.6 |  |
| Bloom.skipIterations | Bloom | skipIterations | 1 | 0 |  |

*15 / 52 dòng đầu: xem sheet 09_hieu_ung_am_thanh/Hau_ky_hinh_anh.*

## 21. Model

Trạng thái: Một phần — cần đọc mã (NEED_CODE_CHECK) (sheet Xem_truoc)

Nguồn dữ liệu: 10_model_tai_san/Model; 10_model_tai_san/Model_tieu_chuan; 10_model_tai_san/Model_kiem_chuan; 10_model_tai_san/Kich_thuoc_that; 10_model_tai_san/Kit_chi_tiet; 10_model_tai_san/Giay_phep_tai_san; 10_model_tai_san/Xem_truoc. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §10h. Prompt 27; Docs/models/MODEL_STANDARD.md.

Prompt 27 thay các model mượn tạm (stand-in) bằng model riêng và đặt một mức chất lượng chung cho mọi model. Quy trình: **STEP0_AUDIT** kiểm kê mọi model và thẻ; **BASELINE** chạy bộ kiểm tra GLB (`Tools/assets/glb_check.py`: tỉ lệ so với `modelSize`, tam giác diện tích 0, màu đỉnh COLOR_0, nút bộ phận boss) và ghi mốc; **EXPERIMENT_1** thử bộ dựng V2 trên bốn model (xe tăng chủ lực, máy bay tiêm kích, silver_bug, trực thăng tấn công) và được chủ dự án duyệt; **BUDGETS** đặt trần số tam giác, renderer và bộ phận động theo loại; **art-bible** ghi luật tạo hình, bảng màu và công thức V2. Mỗi model một commit: dựng lại, kiểm tĩnh, render thẻ, xem trước trong Unity, chấp nhận mốc mới kèm lý do. Không chạy test, mô phỏng hay đo hiệu năng cho đến khi chủ dự án cho phép.

**Đợt 1** (42 model có tên riêng; đợt 1a: 2, đợt 1b: 8, đợt 1c: 32): Ixion và Gungnir, tám boss lô D (Kraken, Monster, Garuda, Hyperion, Stymphalos, Nyx, Cerberus, Hydra) và 32 đơn vị lô B; mọi lớp màu sơn tạm đã bỏ, không số liệu nào đổi. **Đợt 2** sửa 18 model validator đánh dấu (sai tỉ lệ, tam giác diện tích 0, thiếu nút bộ phận boss, vượt trần ngân sách) theo nguyên tắc thay đổi nhỏ nhất.

#### Báo cáo `Docs/models/MODEL_STANDARD.md`

##### Model standard (fix pass 8)

Source: Docs/prompts/fix_full_vi.txt "Lượt 8" item 1 (owner, 2026-10-02); DECISIONS "Sửa lỗi tổng hợp L8 prep".
Where this file and Docs/models/BUDGETS.md disagree, this file decides how a model is **scored**. L9 item 7 is
`python Tools/balance/fix_validate.py 7` (budget information only, the parts and LOD1 against the pass 8 scores); the
prompt 27 caps in `Tools/assets/glb_check.py` stay an error gate for draw calls, while their triangle and vertex caps
only warn (the owner's rule of 02/10).
Checked statically by `python Tools/models/scan_prep.py` (Docs/models/scan/static_scores.csv) and visually on the
sheets that `MachineBrigade.Editor.ModelScan.RenderBatch` draws (Docs/models/scan/README.md).

###### 1. Triangle budgets

LOD0 = the normal GLB (every platform loads it; phones only load this one). The `_hd` twin (the PC High tiers) may
carry up to 2.4 x the class maximum (BUDGETS.md's median `_hd` / normal ratio). The scorer reports it but does not
grade on it.

**Owner rule (02/10): a model over its budget is kept.** Budgets are a guide, not a cap; the scorer reports
over-budget as information only and never grades a model down or cuts it for that (DECISIONS "Owner: over-budget
models are fine").

| class (scorer) | what | LOD0 triangles |
|---|---|---|
| light | wheeled and other light vehicles (trucks, cars, APCs on wheels) | 3,000-5,000 |
| heavy | tanks, tracked and heavy vehicles (tracked, or class Tank / Heavy) | 4,000-7,000 |
| jet, helicopter | aircraft and helicopters | 4,000-7,000 |
| air_other | drop pods, parachute loads | at most 7,000 |
| ship | ships (`naval`) | 8,000-15,000 |
| boss | bosses (every frame) | 10,000-20,000 |
| tower | towers (defs with `fort`, their branch `_a` / `_b` models) | 2,000-4,000 |
| structure, hq | other static structures; the HQs (`headquarters`, `command_hq`) | 2,000-6,000 |
| obstacle | walls, dragon's teeth, minefields (`wall`, `obstacle`, `passable`) | at most 6,000 |

- Below the minimum is a fault too (too little detail to read), not only above the maximum.
- **LOD1 ~50 %** of LOD0: the game builds it at run time (`ModelLibrary.Lod`, `MeshSimplifier`, half a pixel of

  error at the 128 px switch). ModelScan writes `triangles0` / `triangles1` per model; accepted band 35-65 %.
- **LOD2 ~20 %**: the impostor (`ImpostorAtlas`, below 24 px) takes this level for every vehicle. A model drawn large

  enough that its impostor is never used (bosses, ships) needs no mesh LOD2; if one is ever added, about 20 % of LOD0.

###### 2. Minimum parts per class

A part is a named node. A role is met by a `Part_<role>` node **or** by the kit's merged-material node of that
part (the names in the table). Note: `Part_*` nodes are runtime parts (damage, boss parts): ModelLibrary keeps each as
a mesh of its own, so one draw and one shadow draw each. Do **not** add a `Part_*` node per wheel or per blade to pass
this list; "every road wheel", "every blade", "every barrel" are geometry rules, checked on the sheet (each wheel its
own disc with a hub, each blade its own blade). Roles marked (w) only apply when the def is armed; (t) only with a
turret (`turretTurnRate`).

| class | roles (accepted node names, start of the name) |
|---|---|
| tracked | hull (Hull, Body, Chassis); turret (t) (Turret, Casemate); mantlet (t) (Mantlet, Gun_mantlet, Elevation, Cradle); barrels (w) (Main_cannon, Barrel, Gun, Tubes, Launcher, Pod, Missiles, Mount_*); every road wheel (Wheels, Roadwheels, Bogies); drive sprocket (Sprockets); idler (Idlers); tracks with links / tread (Tracks, Track_links, Treads); side skirts (Skirts, Skirt_edge); hatches (Hatch, Hatches, Cupola); sights (Sight, Periscope, Optics, Sensor); roof MG (w) (MG, Mount_mg, Rws, Hmg); smoke dischargers (Smoke, Smoke_launchers, Smoke_brackets); stowage (Stowage, Tarp, Crates, Jerrycans, Bins, Racks, Straps, Ammo_boxes, Bags) |
| wheeled | every wheel (Wheels, Tyres); axles (Axles, Undercarriage, Suspension, Hubs); cab (Cab, Cabin, Hull, Body); glass (Glass, Windows, Windscreen, Lit_windows, Canopy, Visors); lights (Lamps, Lights, Headlights, Tail_lamps, Light_rims); stowage (as above); weapon (w) |
| jet | fuselage; cockpit glass (Canopy, Cockpit, Glass); wings with the reference's sweep and taper (Wing, Part_wing); horizontal and vertical tail (Tail, Fins, Tailplane, Stabilator, Rudder); intakes (Intake, Intake_lips, Inlet); exhausts (Nozzle, Exhaust); pylons (Pylons, Hardpoints, Racks); stores on them (Missiles, Bombs, Pods, Rockets, Drop_tanks); flare dispensers (Flares, Mount_flare) |
| helicopter | fuselage; glass (Canopy, Glass, Windows); rotor hub (Rotor_hub, Rotor_grips, Hub); every blade (Rotor_blades, Blades); tail rotor (Tail_rotor); landing gear (Undercarriage, Skids, Gear, Tyres); stub wings (Wing, Stub_wing, Pylons); weapons (Gun, Gun_turret, Missiles, Pods, Rockets, Launchers) |
| ship | hull with bow flare (Hull); superstructure tiers (Superstructure, Bridge, Deckhouse, Tier, Island, Funnel); radar mast (Mast, Radar, Antenna); every turret and barrel (Turret, Gun_house, Main_cannon, Barrel); CIWS (CIWS, Phalanx, AK630, Gatling, Mount_ciws); boats (Boat, RHIB, Lifeboat, Davit); deck details (Deck, Rails, Bollards, Hatches, Vents, Winch, Anchor) |
| tower, structure, hq | base (Base, Plinth, Footing, Emplacement, Pad, Foundation, Slab, Block, Race); sandbags / walls (Sandbags, Hesco, Wall, Parapet, Barriers, Blast_bags, Revetment, Berm, Coping); roof (Roof, Roof_deck, Canopy, Cupola, Tower_deck, Deck, Turret, Dome, Shelter); antennas (Antenna, Mast, Aerial, Radar, Dish, Flag_pole); faction detail differs (Accord: practical, field-built - sandbags, timber, nets; Hegemon: prefabricated - cast concrete, modular panels) - visual check |
| boss | body (Hull, Fuselage, Body, Chassis, Deck, Envelope, Gondola); weapons; by frame: running gear (ground: Tracks, Wheels, Bogies, Legs, Rail_wheels), lift (air: Rotor, Wing, Envelope, Propeller, Engine), superstructure (naval); and every `parts[].node` of its def present |
| obstacle | none (budget and look only) |

###### 3. General rules

1. **Proportions within 10 %** of the real reference: width/length and height/length against
   `Docs/models/reference_dimensions.md` (data: `Tools/models/reference_real.json`). Absolute size is free (the game
   draws aircraft and ships smaller on purpose; the view fits the length to `modelSize`). Fictional designs
   (conf "inspiration") are not judged.
2. **No single-box turret or hull**: at least two stacked or angled volumes, sloped glacis / cheeks; large bevels on
   every big edge (the kit's chamfers), no 90-degree slab edge on a hull or turret read from 28 px per metre.
3. **Materials and detail colours separated**: hull paint, steel, rubber, glass, lamps, markings in their own
   materials (the kit's names), so the team colour and wear read.
4. **Mounts and muzzles**: a `Muzzle_<slot>` per barrel of every weapon (the weapon's `barrels`; a secondary on the
   main gun's slot shares its barrels); a `Mount_<slot>` per freely aimed (`aim: Free`) secondary; the main weapon on a
   `Turret` (or `Mount_<mainSlot>`) when the def turns a turret; `Mount_Flare` x 2 or more when the def has
   `flareCharges`; `Mount_APS` when it has `aps`. Bosses: as many `Muzzle_*` as `mountWeapons`, every part node.
5. **Readable silhouette at the normal camera distance**: the battle camera's default zoom (orthographic size 19 on
   a 1080 px screen = 28.4 px per metre, pitch 52). The ModelScan sheet shows exactly that; the type must be named from
   the left cell alone.

###### 4. Grades

- **Kém** (poor): triangles over 1.5 x the class maximum or under half the minimum; 4 or more required parts missing;

  the main weapon's muzzle missing; proportions more than 25 % off a high-confidence reference; or the visual pass
  finds the silhouette unreadable / a box model.
- **Cần sửa** (needs fixing): any other fault above (over or under budget, 1-3 parts, a secondary muzzle or mount,

  Mount_Flare / Mount_APS, boss part node, proportions 10-25 %, LOD1 outside 35-65 %), or a visual fault.
- **Tốt** (good): nothing found, statically and on the sheet.
- Final grade = the lower of the static and the visual grade, with one exception: a "missing part" that the sheet

  shows modelled inside a merged node (an idler inside `Wheels`, a mantlet inside `Turret_body`) is cleared by the
  visual pass, which says so in its reason (the static check only sees node names). Old vs new (models rebuilt in prompt 27): the lower
  scoring version loses; when the new one scores lower, restore the old GLB or rebuild it to pass.

###### 5. How the scorer assigns a class

Own def = the def whose id is the model, else the first def drawing it. HQ ids -> hq; `boss` -> boss; `naval` -> ship;
`flying` -> jet (`fixedWing`), helicopter (has a `Rotor*` node) or air_other; static or speed 0 -> obstacle (`wall`,
`obstacle`, `passable` or a wall / teeth / minefield id), tower (`fort` or `branchOf`; the `_a` / `_b` files) or
structure; otherwise tracked (Tracks / Sprockets nodes), wheeled (Tyres / Wheels nodes) or ground.

![ixion: trước / sau dựng lại (front, rear, side, top, 3/4, zoom trận x2)](../images/10_model_tai_san/ixion_before_after.png)

*Hình: ixion: trước / sau dựng lại (front, rear, side, top, 3/4, zoom trận x2). Đơn vị: m; ảnh không có lưới mét; model ixion 27.02 × 13.03 × 10.372 m (glb x × y × z); thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![ixion: ảnh quét trong Unity (ModelScan: 3 góc play / side / rear ở cự ly camera trận)](../images/10_model_tai_san/ixion_unity_scan.png)

*Hình: ixion: ảnh quét trong Unity (ModelScan: 3 góc play / side / rear ở cự ly camera trận). Đơn vị: m; ảnh không có lưới mét; model ixion 27.02 × 13.03 × 10.372 m (glb x × y × z); thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![rocket_turret: trước / sau dựng lại (front, rear, side, top, 3/4, zoom trận x2)](../images/10_model_tai_san/rocket_turret_before_after.png)

*Hình: rocket_turret: trước / sau dựng lại (front, rear, side, top, 3/4, zoom trận x2). Đơn vị: m; ảnh không có lưới mét; model rocket_turret 4.685 × 4.717 × 3.434 m (glb x × y × z); thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![rocket_turret: ảnh quét trong Unity (ModelScan: 3 góc play / side / rear ở cự ly camera trận)](../images/10_model_tai_san/rocket_turret_unity_scan.png)

*Hình: rocket_turret: ảnh quét trong Unity (ModelScan: 3 góc play / side / rear ở cự ly camera trận). Đơn vị: m; ảnh không có lưới mét; model rocket_turret 4.685 × 4.717 × 3.434 m (glb x × y × z); thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![zu23_technical: trước / sau dựng lại (front, rear, side, top, 3/4, zoom trận x2)](../images/10_model_tai_san/zu23_technical_before_after.png)

*Hình: zu23_technical: trước / sau dựng lại (front, rear, side, top, 3/4, zoom trận x2). Đơn vị: m; ảnh không có lưới mét; model zu23_technical 4.582 × 1.61 × 1.64 m (glb x × y × z); thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![zu23_technical: ảnh quét trong Unity (ModelScan: 3 góc play / side / rear ở cự ly camera trận)](../images/10_model_tai_san/zu23_technical_unity_scan.png)

*Hình: zu23_technical: ảnh quét trong Unity (ModelScan: 3 góc play / side / rear ở cự ly camera trận). Đơn vị: m; ảnh không có lưới mét; model zu23_technical 4.582 × 1.61 × 1.64 m (glb x × y × z); thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

![bộ chi tiết kit35: 70 chi tiết dựng model (Tools/blender/mb_kit35.py; số đo ở 10_model_tai_san/Kit_chi_tiet)](../images/10_model_tai_san/kit_catalog_kit35_catalog.png)

*Hình: bộ chi tiết kit35: 70 chi tiết dựng model (Tools/blender/mb_kit35.py; số đo ở 10_model_tai_san/Kit_chi_tiet). Đơn vị: ảnh chụp trong game, không có lưới mét; thước so sánh: Tăng chủ lực (main_battle_tank) 7.79 × 3.07 × 2.307 m (glb x × y × z, 10_model_tai_san/Model).*

Sheet: 10_model_tai_san/Model — Model (518 dòng, 21 cột)

| id | loai | lop_ngan_sach | tam_giac | so_nut | so_part | so_mount | so_muzzle | co_mount_flare | co_mount_aps |
|---|---|---|---|---|---|---|---|---|---|
| aa_57mm_vehicle | ground | ground | 6028 | 38 | 0 | 0 | 2 | FALSE | FALSE |
| aa_gun_tower | structure | tower | 1724 | 12 | 0 | 0 | 2 | FALSE | FALSE |
| aa_gun_vehicle | ground | ground | 3556 | 26 | 0 | 0 | 2 | FALSE | FALSE |
| aa_turret | structure | tower | 6306 | 34 | 0 | 0 | 4 | FALSE | FALSE |
| aa_turret_a | structure | tower | 6670 | 33 | 0 | 0 | 5 | FALSE | FALSE |
| aa_turret_b | structure | tower | 2610 | 33 | 0 | 0 | 5 | FALSE | FALSE |
| aa_vehicle | ground | ground | 4964 | 36 | 0 | 0 | 4 | FALSE | FALSE |
| aa_vehicle_hd | ground | ground | 12556 | 42 | 0 | 0 | 4 | FALSE | FALSE |
| adobe_house | prop | prop | 1660 | 19 | 0 | 0 | 0 | FALSE | FALSE |
| adobe_large | prop | prop | 3946 | 28 | 0 | 0 | 0 | FALSE | FALSE |
| aerial_tanker | air | jet | 4164 | 33 | 1 | 6 | 1 | TRUE | FALSE |
| aim9 | unlisted |  | 238 | 10 | 0 | 0 | 0 | FALSE | FALSE |
| aim120 | munition | munition | 222 | 8 | 0 | 0 | 0 | FALSE | FALSE |
| airborne_light_tank | ground | ground | 5550 | 34 | 0 | 0 | 3 | FALSE | FALSE |
| airborne_light_tank_chute | air | jet | 3514 | 23 | 0 | 0 | 3 | FALSE | FALSE |

*15 / 518 dòng đầu: xem sheet 10_model_tai_san/Model; in 10 / 21 cột; 9 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 10_model_tai_san/Model_tieu_chuan — Model: tiêu chuẩn (14 dòng, 13 cột)

| id | lop | bac | moving_parts_muc | moving_parts_tran | renderers_muc | renderers_tran | triangles_muc | triangles_tran | vertices_muc |
|---|---|---|---|---|---|---|---|---|---|
| boss_l/normal | boss_l | normal | 41 | 52 | 240 | 299 | 56000 | 70000 | 72000 |
| boss_m/normal | boss_m | normal | 25 | 31 | 178 | 222 | 44000 | 55000 | 56000 |
| boss_s/normal | boss_s | normal | 22 | 28 | 130 | 162 | 36000 | 45000 | 43000 |
| ground/hd | ground | hd | 8 | 10 | 83 | 103 | 18800 | 23300 | 27300 |
| ground/normal | ground | normal | 8 | 10 | 61 | 76 | 7800 | 9700 | 10100 |
| helicopter/hd | helicopter | hd | 5 | 6 | 61 | 76 | 15900 | 20000 | 22500 |
| helicopter/normal | helicopter | normal | 5 | 6 | 45 | 56 | 6600 | 8300 | 8300 |
| jet/hd | jet | hd | 6 | 7 | 49 | 60 | 12300 | 15400 | 19200 |
| jet/normal | jet | normal | 6 | 7 | 36 | 44 | 5100 | 6400 | 7100 |
| munition/normal | munition | normal | 2 | 3 | 14 | 17 | 500 | 1600 | 600 |
| prop/normal | prop | normal | 2 | 3 | 46 | 58 | 6900 | 8600 | 9900 |
| scenery/normal | scenery | normal | 2 | 3 | 12 | 14 | 3700 | 4600 | 9700 |
| structure/normal | structure | normal | 2 | 3 | 39 | 48 | 7900 | 9900 | 9800 |
| tower/normal | tower | normal | 8 | 9 | 144 | 180 | 14700 | 18400 | 20100 |

*in 10 / 13 cột; 1 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 10_model_tai_san/Model_kiem_chuan — Model: kiểm chuẩn (baseline) (518 dòng, 72 cột)

| id | model | animations | bounds_max_x_m | bounds_max_y_m | bounds_max_z_m | bounds_min_x_m | bounds_min_y_m | bounds_min_z_m | budget_class |
|---|---|---|---|---|---|---|---|---|---|
| aa_57mm_vehicle | aa_57mm_vehicle | 0 | 1.295 | 2.63 | 2.75 | -1.295 | -0.0376 | -2.9901 | ground |
| aa_gun_tower | aa_gun_tower | 0 | 2.85 | 3.1969 | 3.0366 | -2.85 | -0.01 | -2.85 | tower |
| aa_gun_vehicle | aa_gun_vehicle | 0 | 1.31 | 2.945 | 2.9257 | -1.31 | -0.0386 | -2.715 | ground |
| aa_turret | aa_turret | 0 | 2.25 | 3.1849 | 3.188 | -2.25 | -0.02 | -2.25 | tower |
| aa_turret_a | aa_turret_a | 0 | 2.25 | 3.2617 | 3.188 | -2.25 | -0.02 | -2.25 | tower |
| aa_turret_b | aa_turret_b | 0 | 2.25 | 2.7398 | 2.25 | -2.25 | -0.02 | -2.25 | tower |
| aa_vehicle | aa_vehicle | 0 | 1.54 | 2.8703 | 3.54 | -1.54 | -0.01 | -2.945 | ground |
| aa_vehicle_hd | aa_vehicle_hd | 0 | 1.545 | 2.8703 | 3.54 | -1.545 | -0.01 | -2.945 | ground |
| adobe_house | adobe_house | 0 | 3.53 | 5.0 | 3.6937 | -3.74 | -0.04 | -3.54 | prop |
| adobe_large | adobe_large | 0 | 6.04 | 9.76 | 4.785 | -5.73 | 0.0 | -4.54 | prop |
| aerial_tanker | aerial_tanker | 0 | 11.31 | 5.7 | 9.9 | -11.31 | 0.02 | -10.0754 | jet |
| aim9 | aim9 | 0 | 0.1434 | 0.1434 | 1.1 | -0.1434 | -0.1434 | -1.1 |  |
| aim120 | aim120 | 0 | 0.1177 | 0.1177 | 1.3 | -0.1177 | -0.1177 | -1.3 | munition |
| airborne_light_tank | airborne_light_tank | 0 | 1.31 | 1.8 | 3.25 | -1.31 | -0.047 | -3.2001 | ground |
| airborne_light_tank_chute | airborne_light_tank_chute | 0 | 4.5018 | 11.0 | 4.5 | -4.5018 | -0.047 | -4.5 | jet |

*15 / 518 dòng đầu: xem sheet 10_model_tai_san/Model_kiem_chuan; in 10 / 72 cột; 52 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 10_model_tai_san/Kich_thuoc_that — Kích thước thật tham chiếu (105 dòng, 11 cột)

| id | conf | ref | size_cao_m | size_dai_m | size_rong_m | source |
|---|---|---|---|---|---|---|
| aa_vehicle | approx | Flakpanzer Gepard 1A2 | 3.29 | 7.68 | 3.71 | Wikipedia 'Flakpanzer Gepard' (radar stowed) |
| aerial_tanker | approx | B-52H (same frame as the heavy bomber) | 12.4 | 48.5 | 56.4 | Wikipedia 'Boeing B-52 Stratofortress' |
| ammo_carrier | approx | M977 / M985 HEMTT | 2.84 | 10.17 | 2.44 | Wikipedia 'Heavy Expanded Mobility Tactical Truck' |
| amphib_light_vehicle | approx | M2A3 Bradley (same frame as the IFV) | 2.98 | 6.55 | 3.6 | Wikipedia 'M2 Bradley' |
| armored_bulldozer | approx | Caterpillar D9R (IDF kit) | 4.0 | 8.1 | 4.3 | Caterpillar D9R specifications (blade and ripper) |
| armored_car | approx | Pandur I 6x6 | 1.82 | 5.7 | 2.5 | Wikipedia 'Steyr Pandur' (height to the hull roof) |
| armored_train | inspiration | BP-35 armoured train |  |  |  | a train set |
| artillery | high | M109A6 Paladin | 3.24 | 9.12 | 3.15 | Wikipedia 'M109 howitzer' |
| attack_helicopter | approx | AH-64D Apache Longbow | 3.87 | 17.73 | 14.63 | Wikipedia 'Boeing AH-64 Apache' (length with rotors; height… |
| attack_jet | high | Su-25 Frogfoot | 4.8 | 15.53 | 14.36 | Wikipedia 'Sukhoi Su-25' |
| ballistic_launcher | approx | 9P78-1 Iskander-M TEL (MZKT-7930) |  | 13.07 | 3.07 | Wikipedia '9K720 Iskander' (height not reliable) |
| behemoth | inspiration | Object 279 (four tracks, flat hull), a giant | 2.47 | 10.24 | 3.4 | Wikipedia 'Object 279' (hull 7.77 m); the boss is a fiction… |
| behemoth_inferno | inspiration | Object 279 with a TOS-1A pack |  |  |  | fictional |
| behemoth_tempest | inspiration | Object 279 with a railgun |  |  |  | fictional |
| bmpt | none | BMPT Terminator |  |  |  | no reliable overall figure found yet |

*15 / 105 dòng đầu: xem sheet 10_model_tai_san/Kich_thuoc_that.*

Sheet: 10_model_tai_san/Kit_chi_tiet — Bộ chi tiết kit35 (70 dòng, 8 cột)

| id | tam_giac | x_m | y_m | z_m |
|---|---|---|---|---|
| armour_plate | 652 | 3.0 | 2.0 | 0.225 |
| axle | 120 | 1.8 | 0.261 | 0.411 |
| backpack | 144 | 0.408 | 0.32 | 0.51 |
| beacon | 114 | 0.24 | 0.228 | 0.26 |
| bogie | 956 | 2.015 | 3.569 | 0.994 |
| bomb | 182 | 0.486 | 2.2 | 0.293 |
| breakable_panel | 412 | 2.0 | 1.5 | 0.225 |
| chamfer_box | 92 | 2.0 | 3.0 | 1.0 |
| ciws | 330 | 1.1 | 2.01 | 2.2 |
| crate | 120 | 0.854 | 0.512 | 0.41 |
| dish | 222 | 1.04 | 0.48 | 1.04 |
| door | 292 | 1.16 | 2.0 | 2.08 |
| drop_tank | 96 | 0.6 | 3.01 | 0.6 |
| era_bricks | 1584 | 1.26 | 0.7 | 0.076 |
| exhaust | 230 | 0.284 | 0.277 | 0.743 |

*15 / 70 dòng đầu: xem sheet 10_model_tai_san/Kit_chi_tiet.*

Sheet: 10_model_tai_san/Giay_phep_tai_san — Giấy phép tài sản (5 dòng, 7 cột)

| id | tep | tai_san | giay_phep | so_dong |
|---|---|---|---|---|
| OFL-Barlow | OFL-Barlow.txt | Barlow | SIL Open Font License | 75 |
| OFL-BarlowCondensed | OFL-BarlowCondensed.txt | BarlowCondensed | SIL Open Font License | 75 |
| OFL-BeVietnamPro | OFL-BeVietnamPro.txt | BeVietnamPro | SIL Open Font License | 75 |
| OFL-Inter | OFL-Inter.txt | Inter | SIL Open Font License | 75 |
| OFL-JetBrainsMono | OFL-JetBrainsMono.txt | JetBrainsMono | SIL Open Font License | 74 |

Sheet: 10_model_tai_san/Xem_truoc — Màn xem trước (1 dòng, 5 cột)

| id | trang_thai | ghi_chu |
|---|---|---|
| chua_ap | NEED_CODE_CHECK | Assets/MachineBrigade/Scripts/Editor/ModelPreview.cs và pre… |

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

## Mục "Chưa áp"

(không có)

Mục "Một phần": 2c. Luật trận, phần vô hạn, trung lập, thoại và kết trận; 7. Công thành và Phòng thủ; 15b. Đo bản đồ tĩnh; 16b. Kiểm tĩnh chế độ; 18. Giao diện; 20. Âm thanh; 20b. Hiệu ứng theo bậc và xác vỡ; 21. Model; P4. Trạng thái prompt, validator, manifest và save.
