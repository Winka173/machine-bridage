Chỉ áp dụng các thay đổi cân bằng Armour/Penetration dưới đây lên dữ liệu hiện tại.

Không thay đổi lại các hệ thống đã được xử lý ở prompt trước như:
- Penetration curve
- Top Attack table
- Damage Type table
- guided bomb / bomb top attack
- Kh-29 blast
- ATGM rebalance khác

Đây chỉ là **bảng quyết định unit/weapon nào được nâng lên Armour 5 hoặc Penetration 5**.

# 1. Player vehicles — Armour 5

Áp dụng:

### titan_tank
- armour_front: `4 → 5`
- armour_side: KEEP `3`
- armour_rear: KEEP `2`
- armour_top: KEEP `2`

Final:
`5 / 3 / 2 / 2`

### elite_heavy_tank
- armour_front: `4 → 5`
- armour_side: KEEP `3`
- armour_rear: KEEP `2`
- armour_top: KEEP `2`

Final:
`5 / 3 / 2 / 2`

### mara_behemoth
- armour_front: `4 → 5`
- armour_side: KEEP `3`
- armour_rear: KEEP `3`
- armour_top: KEEP `2`

Final:
`5 / 3 / 3 / 2`

Không tăng Armour 5 cho các player vehicle khác.

Đặc biệt KEEP:
- `main_battle_tank`
- `heavy_tank`
- `next_gen_tank`
- `elite_mbt`
- `elite_tank_destroyer`

Không tạo player vehicle có profile `5/5/5/5`.

---

# 2. Player weapons — Penetration 5

Áp dụng:

| Weapon | Old Pen | New Pen |
|---|---:|---:|
| `railgun` | 4 | **5** |
| `gun_140_twin` | 4 | **5** |
| `gun_152` | 4 | **5** |
| `gun_152_heat` | 4 | **5** |
| `gun_125_elite` | 4 | **5** |
| `gun_105_apfsds` | 4 | **5** |
| `gun_125_armata_ke` | 4 | **5** |

Không tự động tăng damage/reload/range của các weapon này trong cùng task.

Mục tiêu chỉ là tạo tier dedicated heavy anti-armour.

---

# 3. Player weapons giữ Pen 4

Không nâng các weapon sau chỉ vì chúng là late-game:

- `gun_120mm`
- `gun_120_twin`
- `gun_105_long`
- `gun_105_wheeled`
- generic `atgm`
- `hellfire_standoff`
- `hellfire_volley`
- `drone_missile`
- `kh29`
- `cruise_missile_ground`
- `stealth_payload`
- `ballistic_missile`
- `siege_mortar_240`

Nếu các ID tương đương trong canonical data dùng alias khác, map đúng weapon family nhưng không mở rộng ngoài danh sách có chủ đích.

---

# 4. Towers — Penetration 5

### heavy_turret / heavy_turret.bastion

Weapon:
`gun_155_twin_ap`

Cập nhật:

- penetration: `4 → 5`

Giữ nguyên các field khác trừ khi generator tự cập nhật derived values.

### gun_turret.long

`turret_gun_120_long`

- Penetration hiện đã là `5`
- KEEP `5`

---

# 5. Towers — Armour

Không tăng bất kỳ tower nào lên Armour 5.

Giữ maximum tower armour hiện tại là 4.

Ví dụ:

- gun turret profile hiện tại → KEEP
- heavy turret `4/3/3/3` → KEEP
- coastal/spawn bastion `4/3/3/3` → KEEP

Không đổi HP tower trong task này.

---

# 6. Boss armour

KHÔNG thay đổi armour của bất kỳ boss nào.

Giữ nguyên toàn bộ:

- armour_front
- armour_side
- armour_rear
- armour_top

Kể cả các profile hiện có như:

- `5/3/2/2`
- `5/3/2/3`
- `4/4/4/4`
- và các profile khác

Boss HP cũng KEEP nguyên trong task này.

---

# 7. Boss weapons — nâng Penetration 5

Áp dụng:

| Weapon | Old Pen | New Pen |
|---|---:|---:|
| `boss_railgun` | 4 | **5** |
| `p26_ixion_125` | 4 | **5** |
| `train_gun` | 4 | **5** |
| `borer_drill` | 4 | **5** |

Không tự động tăng raw damage/reload/range.

---

# 8. Boss weapons Pen 5 hiện có — KEEP

Rà và xác nhận các weapon sau vẫn Pen 5:

- `p26_bastion_direct_b100`
- `p26_behemoth_direct_be120`
- `p26_behemoth_tiny_be120`
- `p26_jotunn_direct_jo125`
- `p26_leviathan_direct_lev127`
- `p26_matriarch_direct_ma_atgm`
- `p26_moloch_direct_mo120ap`
- `p26_nemesis_direct_ne125`
- `p26_roc_direct_roc_atgm`
- `p26_icarus_main_ic_coil`

Nếu một weapon trong canonical source khác Pen 5, report actual value trước khi áp final `5`.

---

# 9. Boss weapons giữ Pen hiện tại

Không nâng các heavy HE / top-attack / energy weapon sau chỉ vì raw damage hoặc cỡ nòng lớn:

### KEEP Pen 4
- `p26_leviathan_lev406`
- `p26_bastion_sec_b240`
- `p26_jotunn_jo203`
- `p26_moloch_main_mo120`
- `locust_drones`
- `p26_matriarch_ma_drones`
- `p26_roc_main_roc_bombs`
- boss Energy/laser weapons đang Pen 4

Lý do:
- HE thắng bằng damage + blast
- top attack thắng bằng TopAttackTable
- Energy có niche riêng
- không để mọi endgame weapon đều thành Pen 5

---

# 10. Balance intent

Final hierarchy phải là:

### Armour
- 0–4 = normal gameplay range
- 5 = exceptional/super-heavy/endgame armour

### Penetration
- 0–1 = light weapon
- 2 = autocannon/light anti-armour
- 3 = medium gun / older AT
- 4 = modern tank gun / strong ATGM
- 5 = dedicated heavy anti-armour / elite APFSDS / railgun / heavy boss direct gun

Không nâng hàng loạt Armour/Pen chỉ để “dịch thang số lên”.

---

# 11. Derived data

Sau khi áp thay đổi, regenerate toàn bộ derived values liên quan:

- DPS vs armour
- damage vs armour 0–5
- shots-to-kill
- unit comparison
- boss effective damage
- tower effective damage
- any balance export using penetration
- generated spreadsheets/docs có bảng weapon/unit stats

Không thay đổi raw HP/damage/reload chỉ vì derived output thay đổi.

---

# 12. Validation

Xác nhận:

- chỉ 3 player vehicles được nâng Armour 5
- chỉ các player weapon liệt kê được nâng Pen 5
- tower chỉ `gun_155_twin_ap` được nâng thêm Pen 5
- tower armour không vượt 4
- boss armour unchanged
- boss HP unchanged
- chỉ 4 boss weapon mới được nâng Pen 5
- các boss Pen 5 hiện có vẫn giữ
- không có accidental mass-upgrade của Pen 4 → 5

---

# 13. Update generated documentation

Sau khi sửa canonical data:

- regenerate/update các file generated liên quan
- cập nhật `01_chien_dau.md`
- cập nhật `01_chien_dau.xlsx`
- cập nhật `02_boss.md`
- cập nhật `02_boss.xlsx`
- cập nhật `00_index.xlsx`
- cập nhật `CHANGES.md`
- cập nhật các bảng unit/weapon comparison
- cập nhật generated JSON/CSV nếu có

Không patch generated file thủ công nếu có generator.

---

# 14. Report cuối

Trả report gồm:

- unit/weapon
- old value
- new value
- file canonical đã sửa
- generated files đã regenerate
- validation result

Xác nhận rõ:

`boss armour unchanged`
`boss HP unchanged`
`tower armour max remains 4`
`player Armour 5 only on titan_tank, elite_heavy_tank, mara_behemoth`
