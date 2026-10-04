Áp dụng toàn bộ thay đổi cân bằng combat dưới đây vào Machine Brigade. Đây là quyết định cuối cùng; không để `HOLD`, `CHECK`, `DECIDE`, “đợi test”, hoặc placeholder chưa chốt.

## 1. Penetration curve mới

Cập nhật hệ số sát thương theo `penetration - armour`:

- `>= +2` → `1.20`
- `+1` → `1.00`
- `0` → `0.85`
- `-1` → `0.65`
- `-2` → `0.40`
- `-3` → `0.15`
- `<= -4` → `0.08`

Giá trị cũ dự kiến:

- `>= +2`: `1.20 → 1.20`
- `+1`: `1.00 → 1.00`
- `0`: `0.85 → 0.85`
- `-1`: `0.50 → 0.65`
- `-2`: `0.25 → 0.40`
- `-3`: `0.10 → 0.15`
- `<= -4`: trước đây nếu đang dùng chung bucket `<= -3 = 0.10`, tách riêng thành `0.08`

Nếu runtime/code hiện khác expected old value, ghi rõ actual old value trong changelog rồi vẫn áp final value ở trên.

### Quy tắc đặc biệt roof/aircraft

- Top attack tiếp tục đánh vào `roof armour`.
- Roof và aircraft không được hưởng overmatch trên `1.00`.
- Nghĩa là trên roof/aircraft:
  - pen dư `+1` hoặc nhiều hơn → tối đa `1.00`
  - bằng armour → `0.85`
  - `-1` → `0.65`
  - `-2` → `0.40`
  - `-3` → `0.15`
  - `<= -4` → `0.08`

Không thay đổi armour của boss trong task này.

Không thay đổi HP boss trong task này.

---

## 2. Damage Type table mới

Theo thứ tự:

`Ground / Air / Structure`

Áp dụng bảng sau:

### Kinetic
Old:
`1.00 / 0.30 / 0.60`

New:
`1.20 / 0.30 / 0.70`

Vai trò:
- direct-fire chống phương tiện ổn định
- tank gun / AP shell / autocannon / HMG
- ít bị soft-counter hơn missile
- không phải anti-air hoặc siege tối ưu

### ShapedCharge
Old:
`1.00 / 0.30 / 0.60`

New:
`1.30 / 0.20 / 0.45`

Vai trò:
- chuyên diệt xe/giáp
- ATGM / HEAT / loitering anti-armour
- mạnh hơn Kinetic khi thực sự hit
- đổi lại có thể bị APS / ERA / cage / point defence tùy weapon

### HighExplosive
Old:
`1.00 / 0.00 / 1.50`

New:
`1.00 / 0.00 / 1.60`

Vai trò:
- artillery / rocket / bomb / HE shell
- AoE
- phá công trình
- không phải anti-air

### Fragmentation
Old:
`0.50 / 1.30 / 0.10`

New:
`0.45 / 1.35 / 0.10`

Vai trò:
- anti-air / flak / airburst
- hiệu quả thấp với ground
- gần như không dùng để phá công trình

### Fire
Old:
`1.50 / 0.00 / 1.00`

New:
`1.35 / 0.00 / 1.10`

Vai trò:
- anti-ground/light
- area denial
- napalm/flamethrower
- không để Fire trở thành lựa chọn anti-armour mặc định

### Energy
Old:
`1.00 / 1.50 / 0.50`

New:
`0.90 / 1.50 / 0.40`

Vai trò:
- anti-air
- anti-shield
- beam/laser chính xác cao
- không phải anti-tank hoặc siege chính

Giữ rule hiện tại nếu runtime đã có:
- Energy bypasses shield.

---

## 3. Thermobaric

Thermobaric vẫn là modifier/flag, không tạo Damage Type mới.

Giữ quy tắc:

- thermobaric lên Structure = `×2.0`
- giá trị này thay thế HE Structure multiplier, không nhân chồng với `HighExplosive ×1.60`

Tức:

Sai:
`1.60 × 2.0`

Đúng:
`2.0`

---

## 4. Top attack cho bom thả từ máy bay

Các bom đối đất thả trực tiếp từ máy bay phải đánh `roof armour`.

Cập nhật:

### guided_bomb
- `topAttack / danh_noc: false → true`
- `damage: 210 → 250`
- giữ penetration hiện tại
- giữ Damage Type = `HighExplosive`

### jet_bombs
- `topAttack / danh_noc: false → true`
- giữ raw damage hiện tại
- giữ penetration hiện tại

### bomber_payload
- `topAttack / danh_noc: false → true`
- giữ raw damage hiện tại
- giữ penetration hiện tại

### stealth_payload
- `topAttack / danh_noc: false → true`
- giữ raw damage hiện tại
- giữ penetration hiện tại

Rà toàn bộ weapon family `bomb` / air-dropped anti-ground ordnance.

Nếu có các bom tương đương đang thả từ trên xuống nhưng `topAttack=false`, chuyển sang `true`, trừ khi dữ liệu/logic chỉ rõ đó không phải air-dropped ground bomb.

Không tự động biến rocket, cannon shell hoặc direct-fire missile thành top attack.

---

## 5. Missile / ATGM

Giữ sự khác biệt giữa direct attack và top attack.

### Giữ top attack cho:
- `kornet_top`
- Lancet-like loitering munition
- FPV/top-attack drone hiện đã có
- các guided bomb vừa nêu

### Bật top attack cho:
- `hellfire_standoff`

### Không tự động bật top attack cho:
- basic `atgm`
- `gun_launched_atgm`
- direct Kornet variants
- `kh29`
- `maverick`
- generic direct-fire rocket
- cruise missile chỉ vì nó là missile

Top attack phải là một gameplay property có chủ đích, không phải mặc định của mọi guided weapon.

---

## 6. Basic ATGM rebalance

Áp dụng:

### atgm
- `damage: 190 → 210`
- giữ penetration hiện tại
- giữ reload hiện tại
- giữ direct attack

### gun_launched_atgm
- `damage: 200 → 230`
- `penetration: 3 → 4`
- giữ reload hiện tại
- giữ direct attack

Không buff hàng loạt Hellfire / Maverick / Kh-29 / heavy ATGM ngoài các thay đổi cụ thể trong prompt này.

---

## 7. Kh-29 blast

Kh-29 warhead hiện khoảng 320 kg nhưng blast đang quá nhỏ / bằng 0.

Cập nhật Kh-29:

- giữ direct-hit damage hiện tại
- giữ penetration hiện tại
- giữ Damage Type hiện tại
- `core blast radius / loi_m: → 7 m`
- `edge radius / ria_m: → 14 m`

Không biến Kh-29 thành artillery splash weapon.

Direct hit vẫn là phần chính; blast chỉ để phản ánh đúng cảm giác warhead lớn và gây sát thương phụ xung quanh.

Nếu runtime dùng falloff riêng:
- core = full configured splash damage
- edge = falloff vùng ngoài theo convention hiện tại của game
- không tạo một multiplier mới ngoài hệ splash hiện có

---

## 8. Blast của missile lớn

Rà các missile có warhead lớn nhưng `core/edge = 0` hoặc quá nhỏ.

Áp nguyên tắc cuối:

- ATGM nhỏ 5–10 kg: có thể giữ splash 0 hoặc rất nhỏ
- Maverick-class ~50–60 kg: khoảng `core 3–4 m`
- Kh-29-class ~300+ kg: `core 7 m / edge 14 m`
- cruise missile ~400–450 kg: khoảng `core 8–10 m / edge 16–20 m`

Chỉ sửa các outlier rõ ràng có warhead lớn nhưng explosion radius không tương xứng.

Không buff toàn bộ missile theo cùng một blast radius.

---

## 9. Boss

Trong task này:

- KHÔNG thay đổi boss armour.
- KHÔNG thay đổi boss HP.
- KHÔNG áp các đề xuất cũ về giảm `5/3/2/2`, `4/4/4/4`, v.v.
- Boss giữ nguyên armour profile hiện tại.

Sau khi Damage Type + penetration mới được áp, chỉ regenerate các giá trị suy ra / DPS / TTK report nếu pipeline có hỗ trợ.

Không tự rebalance boss trong cùng commit.

---

## 10. Các hệ phòng thủ liên quan

Giữ nguyên gameplay rule hiện tại trừ khi cần cập nhật để tương thích với curve mới:

### Reactive Armour / ERA
- tiếp tục chống ShapedCharge
- tandem warhead tiếp tục bypass / giảm hiệu quả ERA theo logic hiện tại

### Cage / slat armour
- tiếp tục chống shaped-charge từ rocket / missile / drone
- không áp cho Kinetic
- không áp cho Thermobaric nếu rule hiện tại quy định vậy

### SELF_APS
- chỉ guided missiles, drones, direct rockets theo rule hiện tại
- không chặn tank direct shell

### Point Defense
- giữ logic hiện tại
- không biến thành hệ chặn tank shell

Không thay đổi các cooldown phòng thủ trong task này.

---

## 11. Trang bị liên quan penetration

Rà các stat có thể tác động trực tiếp đến breakpoint mới, đặc biệt:

- `tungsten_penetrator`
- `Penetration`
- `ResistRocket`
- `ResistHighExplosive`
- `ResistBlast`
- ERA-related modifier
- cage/slat-related modifier

Không tự balance lại giá trị trang bị trong commit này, trừ khi code/data cần sửa để tương thích với bucket `<= -4`.

Nhưng bắt buộc regenerate report cho biết từng tier `tungsten_penetrator` làm weapon nhảy qua breakpoint nào sau curve mới.

---

## 12. Đồng bộ runtime / export / UI

Tất cả hệ sau phải dùng cùng một giá trị:

- runtime combat
- simulation
- DamageTable / Penetration function
- DPS calculator
- AI evaluation nếu có tính damage
- balance export
- spreadsheet generated fields
- tooltip/UI
- handbook / docs
- tests

Không để runtime dùng curve mới nhưng spreadsheet hoặc docs vẫn hiện curve cũ.

---

## 13. Update toàn bộ tài liệu liên quan

Sau khi code/data sửa xong, regenerate/update toàn bộ tài liệu và file được sinh ra từ pipeline có liên quan.

Ít nhất phải rà và cập nhật nếu tồn tại:

- `01_chien_dau.md`
- `01_chien_dau.xlsx`
- `00_index.xlsx`
- `README.md`
- `CHANGES.md`
- generated balance documentation
- ammunition handbook
- Damage Type table
- penetration table
- weapon derived stats
- DPS-by-armour tables
- aircraft/boss shot calculations nếu phụ thuộc damage table
- generated schemas/indexes nếu formula hoặc description thay đổi
- any generated CSV/JSON balance exports
- any AI-readable docs / agent docs mô tả combat formula

Nếu repo có script generator/exporter, sửa **nguồn canonical** rồi chạy generator.

Không chỉnh tay generated file nếu nó sẽ bị generator ghi đè.

Phải xác nhận generated docs không còn:
- penetration cũ `50 / 25 / 10`
- Damage Type cũ
- `guided_bomb damage 210`
- bomb topAttack cũ
- Kh-29 blast cũ

---

## 14. Tests bắt buộc

### Penetration unit tests

Test ít nhất:

`penetration - armour = +3,+2,+1,0,-1,-2,-3,-4,-5,-6`

Expected:

- +3 → 1.20
- +2 → 1.20
- +1 → 1.00
- 0 → 0.85
- -1 → 0.65
- -2 → 0.40
- -3 → 0.15
- -4 → 0.08
- -5 → 0.08
- -6 → 0.08

### Roof tests

Xác nhận top attack / roof:

- overmatch không vượt `1.00`
- pen4 vs roof2 → 1.00
- pen4 vs roof3 → 1.00
- pen4 vs roof4 → 0.85
- pen4 vs roof5 → 0.65

### Damage Type tests

Test chính xác các table value mới:

- Kinetic `1.20/0.30/0.70`
- ShapedCharge `1.30/0.20/0.45`
- HighExplosive `1.00/0.00/1.60`
- Fragmentation `0.45/1.35/0.10`
- Fire `1.35/0.00/1.10`
- Energy `0.90/1.50/0.40`

### Combined tests

Test Damage Type × penetration.

Ví dụ:

Kinetic pen=armour:
`1.20 × 0.85 = 1.02`

ShapedCharge pen=armour:
`1.30 × 0.85 = 1.105`

Kinetic pen -1:
`1.20 × 0.65 = 0.78`

ShapedCharge pen -1:
`1.30 × 0.65 = 0.845`

ShapedCharge pen -2:
`1.30 × 0.40 = 0.52`

### Bomb tests

Xác nhận:

- guided_bomb damage = 250
- guided_bomb topAttack = true
- jet_bombs topAttack = true
- bomber_payload topAttack = true
- stealth_payload topAttack = true

### Kh-29 tests

Xác nhận:

- direct damage unchanged
- penetration unchanged
- core radius = 7
- edge radius = 14

### Regression tests

- deterministic replay
- no NaN/div0
- damage calculation parity runtime vs export
- AI damage estimation parity nếu có
- boss armour unchanged
- boss HP unchanged

---

## 15. Báo cáo cuối của AI code

Sau khi làm xong, trả report chi tiết với:

1. danh sách file code/data sửa;
2. từng `old_value → new_value`;
3. mọi function/call site dùng penetration multiplier;
4. mọi function/call site dùng Damage Type table;
5. danh sách weapon thay đổi topAttack;
6. danh sách missile blast đã sửa;
7. update các doc trong export_current
8. xác nhận runtime và generated documentation khớp nhau;
9. xác nhận:
   - `boss armour unchanged`
   - `boss HP unchanged`
   - không còn `HOLD/CHECK/DECIDE`
   - không có generated file nào còn chứa bảng damage/penetration cũ.

Nếu generator tạo thay đổi ngoài phạm vi do canonical source thay đổi, giữ các thay đổi generated hợp lệ và liệt kê chúng trong report.
