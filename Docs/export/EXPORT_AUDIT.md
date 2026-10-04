# Export audit 04/10 (lane A) — trang bị + rà toàn gói

Owner 04/10: "có vẻ như toàn bộ trang bị chưa được export, check xem còn gì chưa export data luôn không". Việc này
chạy trên `feature/export-audit` (worktree `MachineBrigade-art`); không chạy Unity, không đổi giá trị game.

## 1. Trang bị (gear) — số đã thiếu, nay xuất

Trước lượt này, `02_phuong_tien/Trang_bi*` (và `Trang_bi_hang` ở 04) chỉ phủ `Bases`, `Modules`, `Traits`, `Subs`,
`Brands` của **xe** (`GearCatalog.cs`) cộng rổ độ hiếm của `Arsenal.cs` (`LevelCap`, `Top`, `Cap`, Gold/LegendaryGuaranteed,
tỷ lệ hòm). Số của **trang bị tháp** (`GearCatalog.Tower.cs`) và vài bảng chỉ số của `Gear.Model.cs` / `Gear.Tower.cs`
không nằm ở đâu trong gói — không phải vì bị loại có lý do, mà vì **không có `Source` nào đọc các mảng đó**: `.cs`
không tự động được quét (`core/sources.py` chỉ quét phần mở rộng có trong `KIND_BY_EXT`, không có `.cs`); một bảng C#
chỉ thành nguồn khi một domain tự gọi `ctx.cs_table(...)` trên nó. Không ai gọi trên `GearCatalog.Tower.cs`, nên
`COVERAGE.md` không hề biết các mảng đó tồn tại (khác với một lá bị "chưa ánh xạ" — các mảng này vô hình với toàn hệ
thống phủ kiểm).

Đã thêm vào `Tools/export/domains/d02_phuong_tien.py` (sheet mới ở pack `01_chien_dau.xlsx`):

| Sheet | Dòng | Nguồn | Nội dung |
|---|---|---|---|
| `Trang_bi_thap` | 13 | `GearCatalog.Tower.cs` `TowerBases` | 13 loại trang bị tháp, 3 ô (Weapon/Structure/Systems); cùng khuôn với `Trang_bi` của xe |
| `Trang_bi_dac_tinh_thap` | 10 | `GearCatalog.Tower.cs` `TowerTraits` | 10 đặc tính tháp (Sử thi/Huyền thoại); 5 khóa trùng đặc tính xe (ô tháp riêng, số có thể khác) — id ghép `@thap` để không đụng `Trang_bi_dac_tinh` |
| `Trang_bi_tran` | 53 | `GearCatalog.cs` `BuildCaps()` / `GearCatalog.Tower.cs` `BuildTowerCaps()` | trần cộng dồn cả loadout cho mỗi `StatId` (xe 6 ô, tháp 3 ô); trần được **dựng bằng hàm** (`Set(StatId.X, giá_trị)`, một vòng lặp theo khoảng enum), không phải mảng literal, nên `cs_table` không đọc được — một regex nhỏ mới (`core/context.py` `cs_custom`, `d02_phuong_tien.py` `_cap_extractor`/`_tower_override_extractor`) đọc đúng thân hai hàm này, đối chiếu thứ tự `StatId` (`VehicleBoost.cs`) để giải vòng lặp `for (var r = StatId.ResistKinetic; r <= StatId.ResistFragmentation; r++)` |
| `Trang_bi_chi_so` | 27 | `Gear.Model.cs` (`SubCount`, `SubBumpLevels`, `PlatingTop`), `Gear.Tower.cs` (`TowerSlots`, `StandardTop`, `RepairTop`) | bảng hằng còn lại theo độ hiếm / chỉ số (mỗi phần tử một dòng, khuôn như `11/Trang_bi_hang`) |

Cờ ẩn play-test 14 (owner 04/10: trang bị khói "bỏ luôn hoặc ẩn đi"): đã xuất đúng 3 món bị `Hidden = true`, khớp lời
brief — `laser_warning` (`Trang_bi`), `SmokeDischarger` (`Trang_bi_mo_dun`), `TowerSmokeLaunchers` (`Trang_bi_dac_tinh_thap`,
cột `hidden`).

Đã có sẵn, không cần đổi (kiểm lại cho chắc): `main stat theo ô x hạng` chính là `Arsenal.cs` `Top`/`Cap` (đã ở
`11/Trang_bi_hang`, bảng = `Top`/`Cap`, chỉ_số 0-5 = Weapon/Loader/Armor/Optics/Engine/Repair theo đúng thứ tự khai
báo); độ phủ hòm/tỷ lệ rơi theo hạng = `Hom_do` (`Odds`); trần lên hạng = `Trang_bi_hang` (`LevelCap`). `substat
rolls`/range (roll 60-100 %, tăng theo bước 5/10/15/20) là công thức trong `Gear.Model.cs SubValue`/`SubBumps`, không
phải bảng — giá trị **đỉnh** theo hạng đã có ở `Trang_bi_dong_phu` (`values`); bản thân khoảng roll (0,6–1) là 2 literal
nằm trong `~3.000` còn lại (mục 2).

Công thức không phải mảng, **không** xuất thành số (đổi giá trị thì phải sửa mã, không phải sheet), chỉ ghi chú ở đây:
`Arsenal.cs` (lớp `Gear`): `LevelCost(item) = item.level >= LevelCap[rarity] ? 0 : 30 * item.level` (30 xu một cấp, tối
đa 9.000 xu một món Huyền thoại); `Spent` = tổng dồn cùng công thức; `CanMerge` = cùng ô + cùng hạng + dưới Huyền thoại
(ghép ba thành một, không có reroll trong game — không có hệ thống nào tên "reroll" trong `Gear*`/`Arsenal.cs`).

Kiểm: `python Tools/export/export.py check --game-json Docs/export/game_snapshot.json` (PYTHONIOENCODING=utf-8) vẫn
**15/15 PASS** sau khi thêm; `sources` 1176→1186, `mapped` 817759→818085 (326 lá mới ánh xạ), `unmapped` vẫn 0,
`unreadable` vẫn 0. Không cần chạy lại `ExportGameDoc` trong Unity cho phần này (mọi số đọc thẳng từ C# tĩnh).

## 2. Rà toàn gói: còn gì chưa export

### Cách rà

`COVERAGE.md` (độ phủ lá) đã **0 chưa ánh xạ / 0 ánh xạ hai nơi** từ trước lượt này — nghĩa là mọi file được hệ thống
*coi là nguồn* (mọi JSON/YAML/csv/txt/glb/audio dưới `Assets/` và `Tools/`, cộng mọi bảng `.cs` một domain đã gọi
`cs_table`/`cs_strings` trên) đều đã vào một cột hoặc một luật loại trừ có lý do. Vậy điểm mù duy nhất của bộ xuất là
đúng như mục 1: **mảng/hằng trong `.cs` mà chưa domain nào từng gọi `cs_table` lên** — vô hình với `COVERAGE.md` vì
`.cs` không tự động thành nguồn (`core/sources.py` `KIND_BY_EXT` không có `.cs`).

Đã rà việc này bằng cách so khớp hai danh sách: (a) mọi file `.cs` dưới `Assets/MachineBrigade/Scripts/{Sim,Game}` có
khai báo `static readonly ...[] Ten = ...` (grep, 109 file, loại `Editor/` vì là công cụ dựng cảnh/chụp ảnh không phải
dữ liệu game), so với (b) mọi file `.cs` các domain đã từng gọi `cs_table`/`cs_arrays`/`cs_strings` lên (71 file, danh
sách lấy từ chính mã domain). Phần việc "export mọi cấu hình JSON/ScriptableObject game đọc" (`tunables.json`,
`operations.json`, `campaign.json`, bản đồ, `.asset`) **không có lỗ hổng cấu trúc** — các file này tự động thành nguồn
khi quét, nên một khóa mới trong đó mà chưa domain nào ánh xạ sẽ tự hiện "chưa ánh xạ (FAIL)" ở `COVERAGE.md` ngay lần
xuất sau; hệ thống tự khóa chặt phần này, không cần rà tay.

### Còn thiếu (ngoài trang bị), liệt kê — chưa xuất lượt này

| Nguồn | Gì thiếu | Vì sao chưa xuất | Trạng thái |
|---|---|---|---|
| `Game/Match/CardMerges.cs` | Danh sách thẻ/tháp bị gộp, đổi tên, nghỉ hưu (`Into`, `TowerInto`, `Retired*`, `Renamed*`) + giá hoàn (`PremiumPrices`, `TowerPrices`) khi một thẻ đã mua bị gộp/nghỉ | Là lịch sử di chuyển roster (không phải trang bị); cần sheet riêng kiểu khóa→khóa, ngoài phạm vi lượt này | Để lại; đã có trong `Hang_so_trong_ma.csv` (quét tĩnh, cờ `de_xuat_dua_ra_du_lieu`) |
| `Game/Match/FrontMap.cs` | Hình học bản đồ chiến dịch (`Coast`, `Islands`), `ThorneSites`, `RetakeChapters` | Có thể trùng một phần với dữ liệu bản đồ/chiến dịch đã ở 06/07; cần đối chiếu kỹ trước khi thêm sheet (tránh ánh xạ hai nơi) | Để lại, cần đối chiếu |
| `Game/Match/Narrative.Data.cs` | Nội dung cốt truyện: `Intel`, `Comics`, `Arcs`, `Loot`, `Choices` | File tự sinh từ `Tools/campaign/narrative.py` (không sửa `.cs` tay); nên đọc từ script nguồn, không phải `.cs` sinh ra — việc riêng | Để lại |
| `Sim/Content/OperationsData.cs` | `SwarmUnits` (hồ bầy đàn của Operations) | Nhỏ, 1 mảng string | Để lại, "co" trong Hang_so_trong_ma |
| `Sim/Modes/BaseLayout.cs` | `DefaultOutpost` (tiền đồn mặc định) | Nhỏ, 1 mảng string | Để lại |
| `Sim/Modes/MissionEvents.Kinds.cs` | `StoryOrder` (thứ tự nhiệm vụ cốt truyện) | Trùng một phần với `07/Chuong`; cần đối chiếu | Để lại |
| `Sim/Modes/MissionEvents.P31.cs` | `GridTowers` (hồ tháp sự kiện P31) | Nhỏ | Để lại |
| `Sim/Content/BossDefs.cs` / `BossTemplates.cs` | `Mechanisms` (danh mục cơ chế boss), `NotInherited` (loại trừ kế thừa template) | Meta/kỹ thuật kế thừa, không phải số cân bằng | Để lại |
| `Sim/Content/BalancePackFacts.cs` | `RoundKinds` | Nhãn loại đạn dùng nội bộ cho xuất `game.json`, không phải dữ liệu chơi | Không cần |

Các mục còn lại trong 109 file (phần lớn ở `Sim/Movement`, `Sim/Navigation`, `Sim/AI` thuật toán, `Sim/Sandbox`,
`Game/Hud`, `Game/Effects`, `Game/Rendering`, `Game/Views`): hằng số **thuật toán/trình bày** (vector hướng pathfinding,
bước làn đường, bán kính vòng rà AI, preset sandbox, màu/khung UI...), không phải số cân bằng người chơi chỉnh được —
đúng loại "không" (`khong`) mà chính `scan_constants.py` đã gắn cờ (xem mục dưới). Không xuất.

`Sim/Content/SimTunables.Pack2.*.cs`, `SimTunables.Rules.cs`, `SimTunables.Values.cs`: không phải thiếu — đầu file ghi
rõ "Generated by Tools/export/mbconst (move)... Edit Resources/Data/tunables.json, not this file"; nguồn thật là
`tunables.json` (đã xuất đủ), các `.cs` này chỉ là bản sao giá trị mặc định.

### ~3.000 literal còn trong mã (pack-2 pass-2, chỉ đếm, không dời)

`Tools/export/scan_constants.py` (sheet `12/Hang_so_trong_ma`, chỉ ở `_qa`, không tính vào `COVERAGE.md`) đã quét toàn
bộ `Sim/**` + `Game/**` (trừ `Editor/`) cho `const`, `static readonly` (kể cả mảng), default thuộc tính, default đọc
dữ liệu, và literal số trần trong `Sim/**` + `Game/Match/**`. Số hiện tại (lượt rà này, chưa đổi mã): **7.150 dòng**,
trong đó cờ `de_xuat_dua_ra_du_lieu = co` (quét tự đề xuất nên đưa ra dữ liệu) = **3.160** — khớp con số "~3.000" của
brief. Theo lĩnh vực (`linh_vuc`) trong nhóm `co`: 02 Phương tiện 1010, 06 Bản đồ 487, 05 Kinh tế 439, 01 Vũ khí 341,
03 Boss 319, 07 Chiến dịch 304, 08 Tham chiếu 132, 04 Căn cứ/Tháp 128. Riêng 4 file trang bị (`GearCatalog.cs`,
`GearCatalog.Tower.cs`, `Gear.Model.cs`, `Gear.Tower.cs`): 694 dòng quét được (hầu hết `so_cung` — từng số trong các
mảng `V(...)` đã nằm trong `Trang_bi*`/`Trang_bi_thap`/`Trang_bi_chi_so` thật sự, bản quét không biết việc đó nên vẫn
liệt; không phải lỗ hổng mới). Không dời số nào trong lượt này, như brief yêu cầu — chỉ đếm.

## Việc cần Unity (ExportGameDoc)

Không có. Mọi số của mục 1 và 2 đọc được bằng phân tích tĩnh mã C# (literal hoặc hàm đơn giản `Set(...)`), không cần
`game_snapshot.json` mới.
