Chỉ áp dụng 2 thay đổi cơ chế dưới đây.

Không thay đổi lại:
- Penetration curve
- Top Attack table
- Damage Type table
- Armour/Pen 5 balance
- bomb/missile/ATGM balance
- boss armour/HP
- các thay đổi khác từ prompt trước

Đây là prompt bổ sung riêng cho:

1. Splash Falloff
2. Kinetic Overpenetration

# 1. Splash Falloff mới

Chuẩn hóa damage falloff theo khoảng cách từ tâm vụ nổ.

Quan trọng:

- bonus ở tâm chỉ áp lên **phần splash/explosion damage**
- không áp bonus tâm lên direct-hit damage
- direct hit và splash phải được tính tách biệt nếu weapon có cả hai

## 1.1. Bảng multiplier

Theo khoảng cách:

| Vùng | Splash multiplier |
|---|---:|
| đúng tâm `r = 0` | `1.10` |
| `0–25% coreRadius` | `1.08` |
| `25–50% coreRadius` | `1.05` |
| `50–100% coreRadius` | `1.00` |
| `core → 25% đoạn core-edge` | `0.85` |
| `25–50% đoạn core-edge` | `0.65` |
| `50–75% đoạn core-edge` | `0.45` |
| `75–100% đoạn core-edge` | `0.25` |
| `r >= edgeRadius` | `0.00` |

Viết gọn:

`110 / 108 / 105 / 100 / 85 / 65 / 45 / 25 / 0`

---

## 1.2. Cách xác định vùng ngoài core

Nếu:

```text
r > coreRadius
```

thì:

```text
edgeProgress =
(r - coreRadius) /
(edgeRadius - coreRadius)
```

Mapping:

```text
edgeProgress <= 0.25 → 0.85
edgeProgress <= 0.50 → 0.65
edgeProgress <= 0.75 → 0.45
edgeProgress < 1.00  → 0.25
edgeProgress >= 1.00 → 0.00
```

Trong core:

```text
coreProgress =
r / coreRadius
```

Mapping:

```text
r == 0               → 1.10
coreProgress <= 0.25 → 1.08
coreProgress <= 0.50 → 1.05
coreProgress <= 1.00 → 1.00
```

---

## 1.3. Edge cases

Nếu:

```text
coreRadius <= 0
```

thì không chia cho 0.

Nếu:

```text
edgeRadius <= coreRadius
```

thì xử lý deterministic theo dữ liệu canonical hiện tại, nhưng không crash/NaN.

Nếu weapon chỉ có một radius:

- map radius đó thành vùng explosion hiện tại theo convention của engine;
- không tự invent thêm radius mới trong task này.

---

## 1.4. Damage pipeline explosive

Nếu weapon có direct damage + splash:

```text
TotalDamage =
DirectHitDamage
+
SplashDamage × SplashFalloffMultiplier
```

Không được:

```text
(DirectHitDamage + SplashDamage)
× SplashFalloffMultiplier
```

Không được áp `1.10` center bonus lên direct-hit component.

---

## 1.5. Ví dụ Kh-29

Với:

```text
coreRadius = 7 m
edgeRadius = 14 m
```

Expected:

- `r = 0` → `1.10`
- `0 < r <= 1.75` → `1.08`
- `1.75 < r <= 3.5` → `1.05`
- `3.5 < r <= 7` → `1.00`
- `7 < r <= 8.75` → `0.85`
- `8.75 < r <= 10.5` → `0.65`
- `10.5 < r <= 12.25` → `0.45`
- `12.25 < r < 14` → `0.25`
- `r >= 14` → `0.00`

---

# 2. Kinetic Overpenetration

Thêm modifier riêng cho direct Kinetic projectile khi penetration cao hơn armour quá nhiều.

Mục tiêu:

- Pen cao vẫn mạnh với heavy armour
- nhưng không trở thành universal best damage chống xe rất nhẹ

Chỉ áp cho:

- Kinetic
- direct projectile
- AP/APFSDS-like
- railgun
- cannon direct shot

Không áp cho:

- ShapedCharge
- HEAT
- ATGM
- HighExplosive
- Fragmentation
- Fire
- Energy
- splash damage
- bombs
- explicit Top Attack

---

## 2.1. Overpenetration table

Dùng:

```text
penetration - armour
```

Bảng final:

- `<= +2` → `1.00`
- `+3` → `0.95`
- `+4` → `0.85`
- `>= +5` → `0.75`

Viết gọn:

`100 / 95 / 85 / 75`

cho:

`<=+2 / +3 / +4 / >=+5`

---

## 2.2. Direct Kinetic formula

Final direct Kinetic damage:

```text
FinalDamage =
BaseDamage
× DamageTypeMultiplier
× PenetrationMultiplier
× OverpenetrationMultiplier
× other legitimate modifiers
```

Overpenetration được tính SAU khi xác định:

```text
penetration - armour
```

Nhưng không thay thế PenetrationTable.

---

## 2.3. Ví dụ Pen 5

Với Kinetic Ground multiplier:

```text
1.20
```

và direct Penetration multiplier `1.20` khi diff >= +2:

### Pen5 vs Armour3

Diff `+2`

```text
1.20 × 1.20 × 1.00
= 1.44
```

### Pen5 vs Armour2

Diff `+3`

```text
1.20 × 1.20 × 0.95
= 1.368
```

### Pen5 vs Armour1

Diff `+4`

```text
1.20 × 1.20 × 0.85
= 1.224
```

### Pen5 vs Armour0

Diff `+5`

```text
1.20 × 1.20 × 0.75
= 1.08
```

---

## 2.4. Railgun validation example

Nếu:

```text
BaseDamage = 510
Pen = 5
DamageType = Kinetic
```

Expected:

### Armour5
Diff `0`

```text
510 × 1.20 × 0.85
= 520.2
```

### Armour4
Diff `+1`

```text
510 × 1.20 × 1.00
= 612
```

### Armour3
Diff `+2`

```text
510 × 1.20 × 1.20
= 734.4
```

### Armour2
Diff `+3`

```text
510 × 1.20 × 1.20 × 0.95
= 697.68
```

### Armour1
Diff `+4`

```text
510 × 1.20 × 1.20 × 0.85
= 624.24
```

### Armour0
Diff `+5`

```text
510 × 1.20 × 1.20 × 0.75
= 550.8
```

---

# 3. Top Attack interaction

Explicit:

```text
topAttack = true
```

không dùng Kinetic Overpenetration modifier.

Top Attack tiếp tục dùng TopAttackTable riêng đã được implement ở prompt trước.

Không double-dip:

```text
TopAttackMultiplier
× OverpenetrationMultiplier
```

---

# 4. Splash interaction với Damage Type

Splash Falloff chỉ điều chỉnh spatial damage.

Damage Type multiplier vẫn được áp bình thường theo pipeline hiện tại.

Ví dụ HE splash lên Ground:

```text
SplashFinal =
BaseSplashDamage
× HighExplosiveGroundMultiplier
× SplashFalloff
× other modifiers
```

Thermobaric vs Structure vẫn giữ rule đã implement trước đó.

Không thay Damage Type values trong task này.

---

# 5. Tests bắt buộc — Splash

Test boundary chính xác:

### Core
- `r = 0` → `1.10`
- `r = 0.25 core` → `1.08`
- `r = 0.50 core` → `1.05`
- `r = core` → `1.00`

### Edge
- `edgeProgress = 0.25` → `0.85`
- `0.50` → `0.65`
- `0.75` → `0.45`
- `<1.00` → `0.25`
- `>=1.00` → `0.00`

Test:
- no NaN
- no divide-by-zero
- deterministic boundary behavior

---

# 6. Tests bắt buộc — Overpenetration

Test:

```text
diff +2 → 1.00
diff +3 → 0.95
diff +4 → 0.85
diff +5 → 0.75
diff +6 → 0.75
```

Test thêm:

- Kinetic direct → modifier active
- ShapedCharge → modifier inactive
- HE → inactive
- Fragmentation → inactive
- Energy → inactive
- Top Attack → inactive
- splash → inactive

---

# 7. Update generated docs/data

Sau khi sửa canonical source, cập nhật/regenerate các tài liệu liên quan tới hai cơ chế này, ví dụ nếu tồn tại:

- combat formula docs
- `01_chien_dau.md`
- `01_chien_dau.xlsx`
- `00_index.xlsx`
- README
- CHANGES
- DamageTable docs
- blast/splash documentation
- penetration documentation
- DPS/damage exports
- simulation outputs
- AI-readable combat docs

Tài liệu phải thể hiện rõ:

### Splash Falloff
`110 / 108 / 105 / 100 / 85 / 65 / 45 / 25 / 0`

### Kinetic Overpenetration
`<=+2: 100% / +3: 95% / +4: 85% / >=+5: 75%`

Không để docs cũ mô tả splash là full damage toàn core/edge nếu runtime đã đổi.

---

# 8. Report cuối

Report:

1. file code/data sửa;
2. call site tính splash;
3. call site tính direct Kinetic;
4. old behavior → new behavior;
5. test result;
6. generated docs đã update;
7. xác nhận:
   - center bonus không buff direct-hit damage;
   - overpenetration chỉ áp Kinetic direct;
   - Top Attack không dùng overpenetration;
   - không thay các bảng balance khác từ prompt trước.

---
Ý kiến chủ dự án kèm prompt (04/10): "không cần test"
