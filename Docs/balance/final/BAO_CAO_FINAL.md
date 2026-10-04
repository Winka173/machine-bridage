# MACHINE BRIGADE — FINAL RECHECK & DECISIONS

Ngày: 2026-10-04  
Bundle: `MB_FINAL_2026_10_04`

## Kết luận
Pass này mở rộng khỏi phạm vi cũ sang AI chiến thuật, toàn bộ mode, campaign event/status, neutral, gameplay map/base, VFX và metadata gameplay. 
Tổng cộng **1,686 cột `sua_duoc=co`** trong schema mở rộng đều có quyết định cuối ở sheet `Field_Decisions`.
Manifest có **226 thay đổi cụ thể old→new**. Không có status HOLD/DECIDE/CHECK trong manifest mới.

Các cột nguồn ngoài đời còn `NEED_SOURCE` là metadata tham chiếu, **không phải quyết định gameplay**: gameplay value tương ứng vẫn được chốt KEEP hoặc APPLY và không bị chặn.

## Thay đổi lớn đã chốt
1. Boss HP theo TTK chương; Ixion main; superweapon 45 s.
2. Boss min/max range: **63 cặp boss–weapon** có override cuối; mục tiêu dải dùng khoảng 3.2×, cap 300 m.
3. Máy bay: HP giảm có chọn lọc theo band số phát để hạ; không tăng HP như manifest cũ.
4. Súng lớn player/tower: **25 weapon** giảm fire-rate 30% và tăng damage/phát tương ứng.
5. Assault + KingOfTheHill catch-up: 0.50 → 0.25.
6. Defend: text time limit chốt 12 phút; Siege chốt 18 phút; Survival chốt 10 wave ≈10 phút.
7. AI Laser: Smoke → Shift. Các tactic còn lại giữ.
8. Guard Tower: base aura 25 m giữ; Watch branch 30 → 35 m.
9. 10 mission fixedDeck `MAKE_LATER` → `READY` trong cùng bundle code.
10. Vision/stealth/radar/reveal: giữ cho tương lai, không xóa.

## AI chiến thuật
Có 16 tactic. Tất cả vector CP cộng đúng 1.0. Không đổi vì cấu trúc counter/prefer/module đang phân vai rõ.
- Blitz: nhanh, cohesion thấp, áp threshold 0.9.
- Depth: hold + fallback + counterattack, là counter tự nhiên của blitz/breakthrough.
- Firepower: artillery prep, 30% ngân sách artillery.
- Ambush: HoldFire, AT-heavy.
- Hit-and-run: kite 0.7, Light/AT/Air cao.
- SEAD: ưu tiên AntiAir, air/support nhiều.
- Air superiority: 22% support/air-defense + 20% AA, chờ air package.
Chi tiết toàn bộ 16 tactic ở workbook.

## Chế độ
12 mode đã rà. Ngoài các thay đổi nêu trên, point/time/overtime/score rules giữ nguyên.
Catch-up tối đa +25% được thống nhất ở mode có catch-up.

## Neutral
18 rule hiện tại giữ. Radar/vision neutral vẫn giữ dữ liệu cho tương lai.
Có thêm 10 neutral-event mới trong workbook, ưu tiên objective di động, lựa chọn risk/reward và pathing.

## Gợi ý mới
- 15 phương tiện mới; top 5: RCH155 MRSI, KF51 130mm, TRX-HPM, Coyote carrier, UGV breacher.
- 10 boss mới; top 5: Ægir, Hel, Talos, Sköll & Hati, Fenrir.
- 10 tower mới; top 5: Rail Lance, MRSI Mortar, HPM, 57mm Airburst, Coyote Nest.
Mỗi đề xuất có stats khởi điểm và ít nhất ba trục cảm giác khác đồ cũ gần nhất.

## Quy tắc agent
Agent chỉ dùng giá trị trong `Manifest_FINAL.json` và workbook. Không tự cân số khác. Validation sau apply không được dùng để trì hoãn quyết định.
