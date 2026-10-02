# Tự kiểm bộ xuất (spec 9)

Commit 5d195554, ngày 2026-10-03, bản gốc so sánh `origin/main`. Lệnh: `python Tools/export/export.py check`.
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

## 1. Mọi file và sheet của mục 4 tồn tại; sheet rỗng chỉ khi có dòng CHUA_AP

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
| 09_hieu_ung_am_thanh | có | 16 |
| 10_model_tai_san | có | 20 |
| 11_meta_giao_dien | có | 24 |
| 12_he_thong_trang_thai | có | 23 |
| 13_tham_chieu_nguon | không | 0 |

Sheet spec 4 nêu mà chưa có:

(không có)

Sheet rỗng (0 dòng, không có dòng CHUA_AP):

(không có)

Sheet chỉ có dòng đánh dấu (CHUA_AP / NEED_CODE_CHECK / KHONG_CO): 37.

## 2. Độ phủ khóa, khóa ngoại, không (id, cột) nào hai giá trị giữa các file

Trạng thái: DAT.

Nguồn 1003, lá 803070; chưa ánh xạ 0; ánh xạ hai lần 0; chờ file chưa dựng 696 (Cho_anh_xa: file 13, lượt 10). Khóa ngoại: {'OK': 256}.

Khóa ngoại FAIL:

(không có)

Cùng (id, cột), giá trị khác nhau giữa các file (bỏ cột chung: ghi_chu, gia_tri_chu, gia_tri_so, khoa, mo_ta, nhom, trang_thai, raw_json, nguon, khối _truoc / _sau):

(không có)

## 3. Mỗi id đúng một dòng; số dòng khớp dữ liệu

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

## 4. Công thức khớp mã game; input chép khớp nguồn

Trạng thái: CHUA_DAT.

Cột công thức (Schema.cong_thuc): 189; cột _game: 51; cột phân tích so với bản Python (Schema.nguon_khoa 'python:', không cần _game): 140; sheet input_: 11.
So công thức với _game (sai số 1e-6) là test của lượt 5; ở đây: mỗi cột công thức có cột _game, và mọi ô input_ bằng giá trị ở file nguồn (cùng id, cùng cột).

Cột công thức thiếu _game:

| file | sheet | cột |
|---|---|---|
| 01_vu_khi_dan | Vu_khi | thoi_gian_bay_toi_tam_s |

Ô input_ khác nguồn:

(không có)

## 5. Số trong Excel khớp md và pdf (mẫu 200 ô, seed 20261003)

Trạng thái: DAT.

Ô số trong bảng md (mọi file md/, bảng có dòng 'Sheet: <file>/<sheet>'): 13610; mẫu 200 (seed 20261003); khác csv: 0. pdf Machine_Brigade_Design_2026-10-03.pdf: 118 trang; mẫu 200 ô của Machine_Brigade_Design_FULL_2026-10-03.md (seed 20261004); khác csv hoặc không thấy trên trang có id dòng: 0.

Ô md khác csv:

(không có)

Ô pdf lệch:

(không có)

## 6. Không ô số chứa chữ đơn vị; không ô trống ở cột bắt buộc

Trạng thái: DAT.

Ô số kèm đơn vị (cột số hoặc cột có đơn vị; cả ô là 'số đơn vị'):

(không có)

Cột kiểu số (Schema int / number) có ô chữ không phải dấu đánh dấu:

(không có)

Cột bắt buộc (Schema bat_buoc) có ô trống:

(không có)

## 7. Hai lần xuất liên tiếp cho file giống hệt

Trạng thái: DAT.

Hai lần xuất (hai tiến trình riêng) trên cùng dữ liệu: 361 file so băm sha256 (trừ README.md, MANIFEST.json, SELF_CHECK.md); khác: 0.

(không có)

## 8. Thứ không xuất và lý do; cột NEED_CODE_CHECK

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

## 9. Không có bí mật trong bất kỳ file

Trạng thái: DAT.

Quét 391 file (mọi file của bộ xuất và các thư mục diff_*; xlsx từng phần, pdf giải nén luồng, ảnh đọc thô): khóa API (Google, AWS, GitHub, Slack, sk-), khóa riêng, mật khẩu / keystore, JWT, bearer, api_key=, email, đường dẫn tuyệt đối máy cá nhân, tên người dùng máy.

(không có)

