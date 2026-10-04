# 10_trang_bi — Trang bị

Trang bị xe và trang bị tháp: loại cơ bản, mô-đun, đặc tính, dòng phụ, bộ, trần cộng dồn, bảng chỉ số, bảng theo độ hiếm, giá nâng cấp theo cấp, luật ghép, hòm và tỷ lệ rơi, tên Anh/Việt theo id.

Gói cân bằng Machine Brigade, commit 13abf306, ngày 2026-10-04. Số liệu đầy đủ ở 10_trang_bi.xlsx; file này chỉ nêu luật, giải thích, lý do thiết kế, tham khảo và bảng nhỏ (tối đa 20 dòng, bảng lớn: xem sheet).

## Các sheet của file

Mọi sheet, số dòng và ý nghĩa cột nằm trong 00_index.xlsx (Muc_luc_sheet, Schema). Sheet `input_<tên>` là bản chép của một sheet nguồn để công thức Excel đọc cùng file; sửa ở sheet nguồn, không sửa bản chép.

- `Trang_bi` (38 dòng): Trang bị: loại cơ bản — 38 loại trang bị (ô, chỉ số ngầm, giá trị đỉnh 5 hạng, đánh đổi)
- `Trang_bi_mo_dun` (14 dòng): Trang bị: mô-đun đặc biệt — 14 mô-đun (Sử thi / Huyền thoại); FlareDispenser, TrophyAps chỉ nâng cấp hệ có sẵn
- `Trang_bi_dac_tinh` (45 dòng): Trang bị: đặc tính — 45 đặc tính (giá trị Sử thi / Huyền thoại)
- `Trang_bi_dong_phu` (23 dòng): Trang bị: dòng phụ — dòng phụ: giá trị theo hạng, ô được ra, trọng số
- `Trang_bi_bo` (13 dòng): Trang bị: bộ (brand) — bộ trang bị: thưởng 2 món / 4 món
- `Trang_bi_thap` (13 dòng): Trang bị tháp: loại cơ bản — 13 loại trang bị tháp, 3 ô (Weapon/Structure/Systems); numbers ở mức đỉnh 5 hạng như trang bị xe
- `Trang_bi_dac_tinh_thap` (10 dòng): Trang bị tháp: đặc tính — 10 đặc tính tháp (giá trị Sử thi / Huyền thoại); 5 khóa trùng Trang_bi_dac_tinh (ô tháp riêng, số có thể khác)
- `Trang_bi_tran` (53 dòng): Trang bị: trần cộng dồn — Trần tối đa cả loadout có thể cộng vào một chỉ số (StatId không liệt kê: GearCatalog không đặt trần riêng, chỉ số đó không rơi làm trang bị hoặc khôn…
- `Trang_bi_chi_so` (27 dòng): Trang bị: bảng chỉ số — Gear.Model.cs / Gear.Tower.cs: bảng hằng còn lại theo độ hiếm hoặc theo chỉ số (mỗi phần tử một dòng)
- `Trang_bi_nang_cap` (75 dòng): Trang bị: giá nâng cấp theo cấp — Arsenal.cs Gear.LevelCost / Gear.Spent: xu để lên mỗi cấp (30 x cấp hiện tại, 0 khi đã ở trần của độ hiếm) và tổng xu đã tiêu từ cấp 1 tới cấp đó (ho…
- `Trang_bi_ghep` (11 dòng): Trang bị: luật ghép — Arsenal.cs Gear.CanMerge / PlayerProfile.Arsenal.cs TryMerge, MergeAll: ghép 3 trang bị cùng ô và cùng độ hiếm (dưới Huyền thoại) thành 1 trang bị độ…
- `Trang_bi_thung` (4 dòng): Trang bị: hòm và tỷ lệ rơi — Arsenal.cs Crates: mỗi lượt quay rơi 1 trong 5 độ hiếm (bảng tỷ lệ riêng theo hòm; hòm Vàng và Huyền thoại bảo đảm lượt đầu), rồi 1 trong 2 loại (tra…
- `Trang_bi_thung_nguon` (8 dòng): Trang bị: blueprint vạn năng và nguồn hòm hàng ngày — Arsenal.cs Crates.Open (blueprint vạn năng kèm hòm Vàng/Huyền thoại) và DailyCrates (hòm miễn phí mỗi ngày: thắng trận, xem quảng cáo)
- `Trang_bi_ten` (156 dòng): Trang bị: tên Anh/Việt theo id — Tên hiển thị (chuỗi HUD) của mọi id trang bị: loại cơ bản xe, mô-đun, đặc tính, dòng phụ, bộ, loại cơ bản tháp, đặc tính tháp. Một dòng một id, tra c…
- `Trang_bi_hang` (27 dòng): Trang bị theo độ hiếm — Arsenal.cs LevelCap / Top / Cap / GoldGuaranteed / LegendaryGuaranteed: mỗi chỉ số một dòng theo bảng nguồn (bang / chi_so)
