Chỉ áp dụng các thay đổi cân bằng trang bị dưới đây lên hệ thống hiện tại.

Không thay đổi lại:
- Penetration curve
- Top Attack table
- Damage Type table
- Splash Falloff
- Kinetic Overpenetration
- Armour/Pen 5 balance
- boss armour/HP
- weapon/bomb/missile balance
- các thay đổi combat khác đã được implement từ prompt trước

Mục tiêu của task này:
1. cân bằng trang bị xe;
2. cân bằng set bonus;
3. cân bằng trang bị tháp;
4. thêm đúng 3 trang bị còn thiếu;
5. khóa các interaction mới với Pen/Armour/TopAttack/DamageType;
6. không xóa gear hiện có trừ khi phát hiện runtime dead item rõ ràng theo mục audit.

# 1. BASE GEAR — armoured_tub

ID:

`armoured_tub`

Stat:

`ArmourAll`

Old:

`0.40 / 0.55 / 0.70 / 0.85 / 1.00`

New:

`0.25 / 0.35 / 0.45 / 0.55 / 0.65`

Lý do:
- ArmourAll tăng toàn bộ mặt giáp;
- không được mạnh ngang `applique_steel` chỉ tăng ArmourSide;
- tránh trở thành lựa chọn phòng thủ mặc định cho mọi build.

Giữ các field khác.

---

# 2. BASE GEAR — hair_trigger

ID:

`hair_trigger`

Old FireRate:

`0 / 0 / 0.10 / 0.12 / 0.15`

New FireRate:

`0 / 0 / 0.08 / 0.10 / 0.12`

Old Spread penalty:

`0 / 0 / -0.10 / -0.12 / -0.14`

New Spread penalty:

`0 / 0 / -0.08 / -0.10 / -0.12`

Giữ:
- MinRarity
- slot
- cơ chế trade-off

Lý do:
- FireRate cap hiện là 15%;
- Legendary không nên tự chạm cap và làm substat FireRate mất giá trị.

---

# 3. BASE GEAR — heavy_barrel

ID:

`heavy_barrel`

Old Range:

`0 / 0 / 0.08 / 0.10 / 0.12`

New Range:

`0 / 0 / 0.07 / 0.09 / 0.10`

Old Speed penalty:

`0 / 0 / -0.05 / -0.06 / -0.07`

New Speed penalty:

`0 / 0 / -0.03 / -0.04 / -0.05`

Giữ:
- Weapon slot
- MinRarity
- trade-off identity

Không đổi `long_barrel`.

Identity:
- `long_barrel` = Range sạch
- `heavy_barrel` = Range cao hơn nhưng có mobility penalty

---

# 4. BASE GEAR — overtuned_engine

ID:

`overtuned_engine`

Old Speed:

`0 / 0 / 0.10 / 0.12 / 0.15`

New Speed:

`0 / 0 / 0.08 / 0.10 / 0.12`

Old Health penalty:

`0 / 0 / -0.04 / -0.05 / -0.06`

New Health penalty:

`0 / 0 / -0.03 / -0.04 / -0.05`

Giữ MinRarity và các field khác.

Lý do:
- Speed cap = 15%;
- gear không nên tự chạm full cap.

---

# 5. KEEP — tungsten_penetrator

ID:

`tungsten_penetrator`

KEEP:

`0.40 / 0.55 / 0.70 / 0.85 / 1.00 Penetration`

Không nerf.

Không tăng cap Penetration.

Penetration gear cap vẫn:

`+1.00`

Lý do:
- Kinetic Overpenetration đã tự tạo nhược điểm khi dư xuyên quá nhiều;
- đây phải tiếp tục là gear anti-heavy chuyên dụng.

---

# 6. KEEP — applique_steel

ID:

`applique_steel`

KEEP hiện tại:

`ArmourSide = 0.40 / 0.55 / 0.70 / 0.85 / 1.00`

Không giảm.

Sau khi nerf ArmourAll của `armoured_tub`, hai item phải có identity:

- `applique_steel` = mạnh theo hướng
- `armoured_tub` = nhẹ hơn nhưng áp dụng toàn thân

---

# 7. DAMAGE VS HEAVY CLASSIFICATION

Hiện:

`DamageVsHeavy = armour 3–4`

Đổi thành:

`DamageVsHeavy = armour class 3–5`

`DamageVsLight = armour class 0–2`

Quan trọng:

Không dùng facing armour tại điểm vừa bị bắn để quyết định Heavy/Light.

Classification phải dựa trên:

`target base chassis / armour class`

Ví dụ:
- tank class Heavy vẫn là Heavy khi bị bắn rear Armour2;
- không được vừa nhận flank penetration benefit vừa bị tính thành Light.

Sửa cả:
- runtime logic
- tooltip/text
- generated docs
- tests

---

# 8. FRACTIONAL PENETRATION / ARMOUR RULE

Đây là rule bắt buộc.

Gear hiện có các stat lẻ:

- Penetration `+0.40 / +0.55 / +0.70 / +0.85 / +1.00`
- ArmourSide
- ArmourAll

Không được round/floor/ceil Pen hoặc Armour trước khi tính:

`penetration - armour`

Giữ float tới bước lookup multiplier.

## 8.1. Normal penetration interpolation

Nếu `diff` nằm giữa 2 breakpoint của PenetrationTable:

dùng linear interpolation giữa multiplier của 2 breakpoint.

Ví dụ:

- diff `0` → `0.85`
- diff `+1` → `1.00`

thì:

- `+0.40` → `0.91`
- `+0.50` → `0.925`
- `+0.70` → `0.955`
- `+0.85` → `0.9775`
- `+1.00` → `1.00`

Không round diff trước interpolation.

---

# 9. TOP ATTACK FRACTIONAL INTERPOLATION

TopAttackTable cũng dùng float/interpolation tương tự.

Ví dụ giữa:

- diff `0` → `0.95`
- diff `+1` → `1.10`

thì nội suy tuyến tính.

Không round Pen/roofArmour trước lookup.

Không thay các giá trị TopAttackTable đã chốt ở prompt trước.

---

# 10. RESIST INDIRECT VS TOP ATTACK

Khóa rule:

`topAttack == true`

KHÔNG đồng nghĩa:

`indirect == true`

`ResistIndirect` chỉ áp cho weapon/effect thật sự có indirect/lob/artillery behavior.

Áp cho:
- artillery
- mortar
- lobbed shell
- indirect rockets
- indirect explosive strike
- các weapon có explicit indirect flag/tag theo canonical runtime

Không tự động áp cho:
- Hellfire top attack
- direct top-attack ATGM
- Lancet
- FPV/top-attack drone
- guided anti-armour top attack

Bomb:
- chỉ áp ResistIndirect nếu canonical bomb behavior/tag định nghĩa nó là indirect;
- không suy ra chỉ từ `topAttack=true`.

Mục tiêu:
- `overhead_screen` không trở thành universal anti-top-attack gear.

---

# 11. REACTIVE ARMOR RULE

Module:

`ReactiveArmor`

Giữ số hiện tại:
- Epic `0.40`
- Legendary `0.55`

Không rebalance raw values trong task này.

Nhưng interaction phải dựa trên Damage Type / warhead logic:

ReactiveArmor áp cho:
- ShapedCharge
- HEAT
- ATGM ShapedCharge
- ShapedCharge drone

Không áp cho:
- Kinetic
- HE
- Fragmentation
- Fire
- Energy
- Thermobaric

Tandem warhead:
- bypass / reduce ERA theo existing tandem rule đã chốt;
- không để ReactiveArmor giảm full damage của tandem như HEAT thường.

Không dùng projectile family “missile” làm điều kiện duy nhất.

---

# 12. SET BONUS — vulcan

Set:

`vulcan`

Old 2-piece BurnDamage:

`0.25`

New:

`0.15`

Giữ 4-piece behavior `SetFirestorm` hiện tại.

Lý do:
- BurnDamage cap = 25%;
- set 2-piece không nên tự chạm cap hoàn toàn.

---

# 13. SET BONUS — hivemind

Set:

`hivemind`

Old SummonPower:

`0.15`

New:

`0.10`

Giữ `SetSwarm` 4-piece behavior.

Lý do:
- SummonPower cap = 15%;
- không tự full cap bằng 2-piece.

---

# 14. SET BONUS — phoenix

Set:

`phoenix`

Old RepairReceived:

`0.10`

New:

`0.06`

Giữ `SetPhoenix` 4-piece behavior.

---

# 15. SET BONUS — quartermaster

Set:

`quartermaster`

Old RepairReceived:

`0.10`

New:

`0.06`

Giữ `SetSalvageRights` 4-piece behavior.

Phoenix và Quartermaster vẫn tồn tại song song vì 4-piece identity khác nhau.

Không merge/xóa hai set.

---

# 16. TOWER GEAR — ammo_handling

ID:

`ammo_handling`

Old Magazine:

`0.10 / 0.15 / 0.20 / 0.25 / 0.30`

New Magazine:

`0.08 / 0.12 / 0.16 / 0.20 / 0.24`

Old:

`MainScale = 1.5`

New:

`MainScale = 1.25`

Với Main stat = `MagazineReload`

Expected reload progression tương ứng:

`0.10 / 0.15 / 0.20 / 0.25 / 0.30`

Không cho Legendary đồng thời:
- +30% Magazine
- và +30% MagazineReload

---

# 17. TOWER GEAR — ammo_hoist

ID:

`ammo_hoist`

Old ProjectileSpeed:

`0.08 / 0.12 / 0.16 / 0.20 / 0.25`

New:

`0.06 / 0.09 / 0.12 / 0.15 / 0.18`

Giữ Main stat FireRate hiện tại.

FireRate vẫn chịu build cap hiện tại.

---

# 18. KEEP TOWER GEAR

Không rebalance thêm:

- `sabot_rounds`
- `fortress_barrel`
- `flak_proximity_fuze`
- `blast_walls`
- `slat_screens`
- `reinforced_concrete`
- `composite_casemate`
- `search_radar`
- `traverse_motors`

trừ derived/generated fields cần update.

---

# 19. ADD NEW BASE GEAR — energy_dissipation_liner

Thêm gear mới:

ID:

`energy_dissipation_liner`

Tên VI:

`Tấm lót tản năng lượng`

Slot:

`Armor`

Implicit stat:

`ResistEnergy`

Values 5 rarity:

`0.04 / 0.06 / 0.09 / 0.12 / 0.15`

Không penalty.

Không plating nếu plating flag có interaction đặc biệt với physical armour; dùng convention phù hợp với các resistance-liner hiện tại.

Không cho max vượt ResistEnergy cap.

Mục tiêu:
- counter nhẹ Energy;
- không làm mất role anti-shield/anti-air của Energy.

---

# 20. ADD NEW BASE GEAR — field_service_interface

Thêm gear mới:

ID:

`field_service_interface`

Tên VI:

`Bộ tiếp nhận sửa chữa dã chiến`

Slot:

`Repair`

Implicit stat:

`RepairReceived`

Values:

`0.02 / 0.03 / 0.04 / 0.06 / 0.08`

Không penalty.

RepairReceived cap vẫn giữ:

`0.10`

Mục tiêu:
- tăng lựa chọn cho slot Repair;
- build thiên về nhận support/repair thay vì self-regen.

---

# 21. ADD NEW TOWER GEAR — grounding_mesh

Thêm tower gear:

ID:

`grounding_mesh`

Tên VI:

`Lưới tiếp địa năng lượng`

Slot:

`TowerStructure`

Implicit stat:

`ResistEnergy`

Values:

`0.04 / 0.06 / 0.09 / 0.12 / 0.15`

Không penalty.

Không đổi Energy bypass shield.

Gear này chỉ giảm Energy damage sau khi Energy đã bypass shield theo pipeline hiện tại.

---

# 22. DO NOT ADD MORE GEAR

Không thêm thêm:
- Penetration gear
- ArmourAll gear
- FireRate gear
- raw Damage gear
- anti-TopAttack gear
- APS module
- ERA module
- missile-defense module
- generic DamageTaken gear

Ngoài đúng 3 item mới ở trên.

---

# 23. DO NOT DELETE EXISTING GEAR

Final decision:

`delete count = 0`

Không xóa:
- long_barrel
- heavy_barrel
- composite_addon
- slat_cage
- overhead_screen
- underbelly_armor
- proximity_fuze
- airburst_rounds
- carousel_autoloader
- extended_ammo_rack
- camouflage_net
- radar_absorbent_coating
- Phoenix
- Quartermaster

---

# 24. SPECIAL AUDIT — monolith_plate

ID:

`monolith_plate`

Hiện có:
- `implicitStat = Count`
- `MainScale = 1.8`
- `NoSubs = true`
- `MinRarity = 2`
- Speed penalty ở rarity cao

Không tự xóa hoặc rebalance số trước khi kiểm runtime.

Bắt buộc xác định:
1. `Count` ở item này thực sự ảnh hưởng combat gì;
2. `MainScale = 1.8` được consume ở đâu;
3. item có tạo measurable combat benefit không;
4. `NoSubs=true` có đúng design không.

Nếu runtime effect tồn tại và hoạt động:
- KEEP nguyên.

Nếu `Count/MainScale` không được consume hoặc item thực tế không có benefit:
- report nó là dead item;
- sửa implementation để intended effect hoạt động;
- ưu tiên sửa implementation thay vì xóa item.

Không tự invent effect mới nếu source không cho thấy intended behavior.

---

# 25. BUILD CAPS — KEEP

Giữ các cap hiện tại:

- `Damage = 0.25`
- `FireRate = 0.15`
- `Health = 0.25`
- `Penetration = 1.00`
- `ProjectileSpeed = 0.30`
- `Range vehicle = 0.12`
- `Range tower = 0.10`
- `Speed = 0.15`
- standard damage-type resistance caps = `0.30`
- các cap khác giữ nguyên nếu prompt này không chỉ định.

Không tăng cap để accommodate Legendary gear.

Gear phải fit vào cap, không phải ngược lại.

---

# 26. SUBSTAT VALUES

Giữ hiện tại trừ classification Heavy:

- Damage
- FireRate
- Range
- ProjectileSpeed
- Health
- Magazine
- MagazineReload
- Regen
- ResistFire
- ResistFragmentation
- ResistHighExplosive
- ResistKinetic
- ResistShapedCharge
- Speed
- Spread
- TurretRate
- Vision
- DamageVsAir
- DamageVsLight
- DamageVsStructure
- các substat khác

Không rebalance hàng loạt substat.

---

# 27. CAP APPLICATION

Đảm bảo cap được áp trên tổng stat sau khi cộng:

- base gear
- substats
- traits
- sets
- module stat modifiers
- commander/other valid sources

Không cap từng source riêng rồi cộng lại nếu runtime design không yêu cầu như vậy.

Final effective stat phải không vượt BuildCap.

---

# 28. RARITY PROGRESSION

Kiểm tra sau thay đổi:

- Legendary > Epic > Rare > Uncommon > Common khi stat là benefit;
- penalty có progression hợp lý;
- không có rarity cao hơn nhưng effective value thấp hơn vì cap quá sớm;
- không có stat bị cap từ base gear trước khi substat/set có cơ hội đóng góp.

Đặc biệt test:
- hair_trigger
- heavy_barrel
- overtuned_engine
- armoured_tub
- tungsten_penetrator
- applique_steel
- ammo_handling
- ammo_hoist

---

# 29. INTERACTION TEST — PEN GEAR

Test `tungsten_penetrator` với fractional interpolation.

Ví dụ base Pen4:

- +0.40 → effective Pen4.40
- +0.55 → 4.55
- +0.70 → 4.70
- +0.85 → 4.85
- +1.00 → 5.00

Không round thành:
- 4
- hoặc 5

trước lookup.

Test normal penetration table và Kinetic Overpenetration cùng hoạt động đúng.

Overpenetration diff cũng dùng final float penetration.

---

# 30. INTERACTION TEST — ARMOUR GEAR

Test:
- ArmourAll +0.65
- ArmourSide +1.00

được giữ dạng float.

Facing armour:

`base facing armour + applicable gear armour`

sau đó dùng float diff.

Không biến armour gear thành integer tier sớm.

---

# 31. INTERACTION TEST — TOP ATTACK

Top Attack:

- dùng roofArmour
- cộng applicable ArmourAll nếu ArmourAll thực sự áp toàn mặt
- không cộng ArmourSide vào roof
- dùng float interpolation TopAttackTable
- không dùng Kinetic Overpenetration
- không tự dùng ResistIndirect chỉ vì `topAttack=true`

---

# 32. INTERACTION TEST — ENERGY RESIST

Test item mới:

`energy_dissipation_liner`

và:

`grounding_mesh`

Energy vẫn:

1. bypass shield;
2. sau đó damage đi qua Energy multiplier;
3. sau đó ResistEnergy giảm damage theo existing resistance pipeline.

Không cho ResistEnergy ngăn shield bypass.

---

# 33. INTERACTION TEST — DAMAGE VS HEAVY

Tạo test:

Heavy chassis Armour5:
- front 5 → DamageVsHeavy active
- side 3 → active
- rear 2 → vẫn active

Light chassis Armour2:
- nếu có temporary ArmourAll buff làm facing effective >2 → vẫn DamageVsLight nếu classification dựa trên chassis.

Không classification theo current facing armour.

---

# 34. INTERACTION TEST — ERA

Test:

ReactiveArmor vs:
- ShapedCharge normal → active
- HEAT → active
- tandem ShapedCharge → bypass/reduced according existing rule
- Kinetic → inactive
- HE → inactive
- Energy → inactive
- Thermobaric → inactive

---

# 35. GENERATED DATA / DOCS

Sau khi sửa canonical source, regenerate/update tất cả output liên quan.

Ít nhất rà/update:

- `10_trang_bi.xlsx`
- `10_trang_bi.md`
- `01_chien_dau.xlsx`
- `01_chien_dau.md`
- `03_can_cu.xlsx`
- `03_can_cu.md`
- `00_index.xlsx`
- `README.md`
- `CHANGES.md`

và nếu tồn tại:
- gear CSV/JSON exports
- localized gear names
- gear tooltips
- BuildCap docs
- rarity tables
- set bonus docs
- tower gear docs
- AI-readable gear docs
- combat derived tables
- penetration simulations
- loadout validation reports

Không patch generated outputs thủ công nếu có generator.

Sửa canonical source rồi regenerate.

---

# 36. FINAL VALIDATION SUMMARY

Final expected balance:

Base gear changed:
- `armoured_tub`
- `hair_trigger`
- `heavy_barrel`
- `overtuned_engine`

Sets changed:
- `vulcan`
- `hivemind`
- `phoenix`
- `quartermaster`

Tower gear changed:
- `ammo_handling`
- `ammo_hoist`

New gear:
- `energy_dissipation_liner`
- `field_service_interface`
- `grounding_mesh`

Deleted gear:
- `0`

Classification:
- `DamageVsHeavy: Armour 3–4 → Armour class 3–5`

Rules added/locked:
- fractional Pen interpolation
- fractional Armour handling
- TopAttack fractional interpolation
- Heavy/Light by chassis
- ResistIndirect separated from TopAttack
- ERA based on ShapedCharge interaction

---

# 37. FINAL REPORT

Trả report cuối gồm:

1. từng ID thay đổi;
2. `old_value → new_value`;
3. canonical source file/code;
4. 3 item mới đã thêm;
5. monolith_plate runtime audit result;
6. BuildCap validation;
7. fractional Pen/Armour test result;
8. TopAttack interaction test;
9. ERA interaction test;
10. Energy-resist test;
11. generated files đã regenerate;
12. xác nhận rõ:

`deleted gear = 0`

`new gear = 3`

`DamageVsHeavy = chassis armour class 3–5`

`fractional penetration/armour is not rounded before lookup`

`ResistIndirect is not automatically triggered by topAttack`

`boss armour/HP unchanged`

=== Trả lời của chủ dự án 04/10 (nguyên văn) ===
1. Có, giữ global BuildCap trên tổng tất cả nguồn; Veteran Crew không bypass cap. Thêm hiển thị phần bonus bị overcap nếu UI hỗ trợ.
2. Có, giảm thêm để effective final: hair_trigger Rare/Epic/Legendary = 8/10/11% FireRate; overtuned_engine = 8/10/12% Speed; monolith_plate Legendary Health = 24% thay vì 25.2%. Hãy chỉnh raw values dựa trên formula thực tế để đạt các effective target này.
3. Có, sửa ammo_handling để effective MagazineReload thực tế = 10/15/20/25/30%, đồng thời Magazine = 8/12/16/20/24%. Không giữ MainScale=1.25 nếu formula hiện tại khiến output sai; ưu tiên effective result này.
