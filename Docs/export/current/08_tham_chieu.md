# 08_tham_chieu — Tham chiếu ngoài đời và game

Nguồn ngoài đời, cơ chế lấy ý từ game, học thuyết quân sự, bản quyền tài liệu.

Gói cân bằng Machine Brigade, commit 9a62db3b, ngày 2026-10-06. Số liệu đầy đủ ở 08_tham_chieu.xlsx; file này chỉ nêu luật, giải thích, lý do thiết kế, tham khảo và bảng nhỏ (tối đa 20 dòng, bảng lớn: xem sheet).

## Cách đọc

File này giữ nguồn ngoài đời, cơ chế lấy ý từ game khác và học thuyết quân sự mà các file 01–07 dẫn tới (cột `nguon_id` của sheet `<tên>_tham_chieu`). Một dòng nguồn có `do_tin_cay`: `da_kiem_chung` (có tài liệu hoặc số đo kiểm được), `uoc_dinh` (ước theo nguồn gần đúng), `ban_dau_doan` (đoán ban đầu, chưa có nguồn).

Nguon_tham_chieu: 318 nguồn; độ tin cậy: 1 7, 2 141, 3 170. Loại: bai_bao 1, nha_phat_hanh_game 1, nha_san_xuat 3, tai_lieu_quan_su_chinh_thuc 3, tai_lieu_repo 167, thu_vien_am_thanh 36, wiki_game 3, wikipedia 104.

## Các sheet của file

Mọi sheet, số dòng và ý nghĩa cột nằm trong 00_index.xlsx (Muc_luc_sheet, Schema). Sheet `input_<tên>` là bản chép của một sheet nguồn để công thức Excel đọc cùng file; sửa ở sheet nguồn, không sửa bản chép.

- `Tham_chieu_game_co_che` (178 dòng): Cơ chế lấy ý từ game — Mỗi cơ chế lấy ý từ game một dòng (spec 12.3): từ các sheet tham chiếu 01-11, nghiên cứu AI, bảng cân bằng (đề xuất), DECISIONS
- `Tham_chieu_de_xuat` (103 dòng): Đề xuất: tham chiếu ngoài đời / game — Các sheet đề xuất của bảng cân bằng (Đề xuất thêm, Công trình mới, Tên lửa & bom mới, Boss mới, Thẻ hỗ trợ mới): mẫu thật, game, cảm giác khác (chưa…
- `Tham_chieu_hoc_thuyet` (44 dòng): Học thuyết quân sự và thuật ngữ — Học thuyết / thuật ngữ quân sự dùng cho AI (nghiên cứu AI: cột 'Ngoài đời' của Chiến thuật, 'Học thuyết ngoài đời' của Vai trò) kèm nguồn
- `Nguon_tham_chieu` (318 dòng): Nguồn tham chiếu — Mọi tài liệu mà ghi chú trong repo nêu tên, và chính các tài liệu repo mang ghi chú (spec 12.3). URL chỉ khi repo ghi; ngày truy cập theo nguồn repo…
- `Tai_lieu_ban_quyen` (209 dòng): Tài liệu và tác phẩm có bản quyền — Nguồn ngoài và game / phim được nhắc: chỉ dùng ý tưởng và thông số (sự kiện), không dùng văn bản, ảnh, tên, logo, mô hình (spec 12.5)
