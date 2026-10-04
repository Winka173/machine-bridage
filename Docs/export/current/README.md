# Machine Brigade: gói cân bằng

Xuất từ commit 13215908 (ngày 2026-10-04); so sánh `_truoc` / `_sau` với bản 5f5b3247 (5f5b3247). Gói chỉ phục vụ cân
bằng: giá trị cấu hình sửa được, cột suy ra để cân bằng (DPS, máu trên CP, số phát để hạ, so với ngoài đời), tham chiếu ngoài đời
và game. Ghi đè mỗi lần chạy; lịch sử nằm trong git.

## Cây thư mục (23 file và images/)

```
current/
├── README.md
├── 00_index.xlsx   Muc_luc_file, Muc_luc_sheet, Schema (có đơn vị), Phien_ban (băm sha256 từng file)
├── 01_chien_dau.xlsx  +  01_chien_dau.md      Chiến đấu
├── 02_boss.xlsx  +  02_boss.md      Boss
├── 03_can_cu.xlsx  +  03_can_cu.md      Căn cứ và tháp
├── 04_che_do_kinh_te_ai.xlsx  +  04_che_do_kinh_te_ai.md      Chế độ, kinh tế, meta, giao diện
├── 05_chien_dich.xlsx  +  05_chien_dich.md      Chiến dịch và cốt truyện
├── 06_ban_do.xlsx  +  06_ban_do.md      Bản đồ
├── 07_hinh_anh_am_thanh_model.xlsx  +  07_hinh_anh_am_thanh_model.md      Hình ảnh, âm thanh, model
├── 08_tham_chieu.xlsx  +  08_tham_chieu.md      Tham chiếu ngoài đời và game
├── 09_ai.xlsx  +  09_ai.md      AI
├── 10_trang_bi.xlsx  +  10_trang_bi.md      Trang bị
├── bulk.zip        21 CSV lớn (bố cục bản đồ, thoại, chuỗi địa phương hóa, nút model): <file>__<sheet>.csv
└── images/         29 ảnh phẳng, tiền tố file; chỉ ảnh mà một md dẫn tới
```

## Cách đọc

- Bắt đầu ở 00_index.xlsx: `Muc_luc_file` (mỗi file có gì), `Muc_luc_sheet` (306 sheet trong xlsx, 21 trong bulk.zip),
  `Schema` (mỗi cột: kiểu, đơn vị `don_vi`, nguồn khóa, công thức, `sua_duoc`), `Phien_ban` (ngày, commit, băm balance.json và
  campaign.json, băm từng file).
- 01_chien_dau: vũ khí, đạn, phương tiện, thẻ hỗ trợ, trang bị, commander, đội mở màn, ném bom. 02_boss, 03_can_cu: boss, tháp.
  04_che_do_kinh_te_ai: chế độ, độ khó, kinh tế, meta, giao diện. 05_chien_dich: chương, nhiệm vụ, biến cố.
  06_ban_do: bản đồ (mỗi bản đồ một dòng tóm tắt trong `Ban_do_tom_tat`; bố cục đầy đủ trong bulk.zip).
  07_hinh_anh_am_thanh_model: hiệu ứng, âm thanh, model. 08_tham_chieu: nguồn ngoài đời, cơ chế game, học thuyết.
  09_ai: chiến thuật, hồ sơ AI, tướng địch, tham số AI, vai trò và trạng thái đội, hành vi tháp / boss, luồng quyết định
  theo lớp, mục tiêu ưu tiên, độ khó, chống kẹt, tiếp tế máy bay, hằng số AI còn trong mã.
  10_trang_bi: trang bị xe và trang bị tháp, một file riêng — loại cơ bản, mô-đun, đặc tính, dòng phụ, bộ, trần cộng
  dồn, bảng chỉ số, bảng theo độ hiếm, giá nâng cấp theo cấp, luật ghép, hòm và tỷ lệ rơi, tên Anh/Việt theo id.
- Mỗi md chỉ có luật, giải thích, lý do thiết kế, tham khảo và bảng nhỏ (tối đa 20 dòng; bảng lớn ghi "xem sheet").
- Cột `_game` là giá trị mà mã game tính ra; cột công thức Excel sống tính lại từ cột dữ liệu gốc cùng file. Sheet `input_<tên>`
  là bản chép của sheet nguồn để công thức đọc cùng file: sửa ở sheet nguồn.
- Dấu hiệu thiếu dữ liệu: `NEED_SOURCE` (thông số ngoài đời chưa có nguồn), `KHONG_AP_DUNG` (ô vô nghĩa cho dòng đó; lý do ở
  `Schema.ly_do_khong_ap_dung`), `NEED_CODE_CHECK` (chỉ mã C# tính; ExportGameDoc điền khi chạy với game.json). Đơn vị
  `khong_ro` trong Schema: mã và chú thích không nói rõ.

## Cân bằng lại: nhập ngược (5 dòng)

1. Sửa số trong cột dữ liệu gốc của file xlsx (cột `Schema.sua_duoc` = co); không sửa id, nguon, raw_json, cột công thức, cột `_game`.
2. `python Tools/export/export.py import Docs/export/current --dry-run` (hoặc một file xlsx đã sửa; thêm `--game-json <game.json>` để so cả ô lấy từ game.json): so với dữ liệu hiện tại.
3. Ra `_qa/import/manifest_import.json` và `.md` (bundle_id, entity_id, field_path, expected_before, new_value, status = DECIDE).
4. Đặt status APPLY cho dòng muốn áp, rồi `python Tools/balance/p29_apply.py --manifest <json> --dry-run`; OK / ALREADY_APPLIED / CONFLICT.
5. Chạy lại không `--dry-run` để áp theo gói; không bao giờ sửa balance.json trực tiếp.

## Lệnh

`python Tools/export/export.py` (ghi gói), `check` (xuất hai lần và chạy mọi test, ghi `_qa/SELF_CHECK.md`), `pdf` (ghi
`_qa/*.pdf`), `diff <A> <B>` (ghi `_qa/diff/`), `import <gói|xlsx> --dry-run`, `--game-json <game.json>` (điền ô
NEED_CODE_CHECK từ ExportGameDoc). Thư mục `_qa/` chỉ sinh khi chạy, không commit.
