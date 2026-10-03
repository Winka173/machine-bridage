# CHANGES — gói cân bằng (ngoài gói)

File duy nhất ngoài `Docs/export/current/`: mọi giá trị agent tự quyết hoặc đổi (luật C và D của
`Docs/prompts/export_pack_vi.txt`), số hằng số đã đưa ra dữ liệu và số còn lại. Lane C nối thêm phần của mình
(cấu trúc gói, số sheet / dòng / NEED_CODE_CHECK trước / sau).

## Lane B — phía game

Nhánh `feature/pack-b` (từ `lead/integration` a797fbe4). Commit:

| bước | commit | nội dung |
|---|---|---|
| (a) | 6eda9785 | test hash phát lại `Tests/EditMode/ReplayHashTests.cs` (8 trận cố định, ghi baseline lần chạy đầu) |
| (b) | e30c8da1 | 227 hằng số + 21 số của công thức / luật ra `Resources/Data/tunables.json` (giữ nguyên giá trị) |
| (c) | 2cd4cf00 | thay đổi theo luật C / D (bảng dưới) |
| (b2) | c5b2d282 | 11 khóa nữa (săn boss: dải mạnh, thời gian hạ mục tiêu; Vô tận: hệ số thưởng 0,9, địch mỗi boss 0,08), giữ giá trị |
| (d) | 620ce280 | hàm xuất công khai (`BalancePackFacts`) + khóa `balancePack` trong game.json (`ExportGameDoc.Pack.cs`) |

### Thay đổi giá trị và quyết định (luật C, D)

| # | mục | sheet / cột | cũ | mới | luật | lý do | commit | trận replay bị ảnh hưởng |
|---|---|---|---|---|---|---|---|---|
| D1 | AI đợt sóng (TacticalAi không phân tầng: BossRush, Sinh tồn, đợt sóng nhiệm vụ, AI đồng minh nhiệm vụ, Sandbox) kéo xe nặng dưới 30 % máu ra sau tuyến | 06 AI / hành vi | kéo lui (`PullBackDamaged`, ngưỡng 0,3) | bỏ | D: "không rút theo máu" | AI chỉ huy (phân tầng) đã tắt từ prompt 28 D.3; AI đợt sóng vẫn còn | 2cd4cf00 | survival, bossrush, campaign |
| D2 | Máy bay tiêm kích dưới 30 % máu bỏ cuộc không chiến (`BreakOffHealth`) | 02 Xe / AI máy bay | bỏ cuộc ở 0,3 máu | bỏ (vẫn phòng thủ khi bị đặt thế xấu) | D: "không rút theo máu (kể cả máy bay)", prompt 32 §0 | luật khóa nói rõ cả máy bay | 2cd4cf00 | mọi trận có tiêm kích (có thể cả 8) |
| D3 | Gungnir (`rail_supergun`) nằm trong ô mini của chương 11 | 03 Boss / Operations "boss thêm"; thẻ chương | có thể bị chọn làm boss mini thêm; chương 11 hiện "2 boss mini" | không bao giờ là mini thêm; đếm mini bỏ boss hạng main | D: "Gungnir là boss chủ lực" | dữ liệu đã `rank: main` (prompt 29 G1); 2 chỗ mã còn coi ô mini là mini | 2cd4cf00 | không (Operations không trong bộ replay) |
| C1 | Ngưỡng tiếp tế (HOLD E2) | 05 Kinh_te / ngưỡng | armyCap theo chế độ × supply 1,05 (mặc định 40 → tiếp tế 63 CP) | armyCap × **1,16** × 1,05 (mặc định 49 → tiếp tế 73 CP); thưởng tiếp tế (mô-đun, hỗ trợ săn boss) cộng sau, không nhân | C: luật trong prompt ("giá đã tăng theo nhóm giá → ngưỡng theo hệ số trung bình") | hệ số trung bình đã tính trong repo: `economy.startCp.scale` 1,16 (prompt 32 L6, "the new prices"); trung bình new/old của 78 dòng giá manifest_v2 B1 là 1,20 (chỉ các thẻ đã đổi giá; 1,16 tính cả thẻ ≤ 4 CP ×1,0) | 2cd4cf00 | mọi chế độ có kinh tế (cả 8) |
| C2 | Đường phạt tiếp tế, trần −75 %, bắt kịp, hoàn CP | 05 Kinh_te | số cứng trong mã | tham số dữ liệu, **giữ** (`modes.economyRules.*`, `modes.economySystem.*`) | B + C | không có luật đổi | e30c8da1 | không |
| C3 | Pháo đài thép (`heavy_turret.bastion`) | 04 Thap / giá xây lại, chỉ số | giá 18, chỉ số | **giữ** | C | chủ dự án đã quyết 02/10 ("Owner calls on the prompt 32 HOLD numbers": giá 18 được chấp nhận, chỉ số giữ); luật "giảm tới 13–15" của prompt hệ căn cứ bị quyết định riêng đó thay | — | không |
| C4 | Tháp nhỏ REBALANCE_STATS (mg_bunker, .twin, .flame, aa_turret, .flak) | 04 Thap / outgoingDamageMult | 0,6086 / 0,5036 / 0,3248 / 1 / 0,7869 (trần eq 11) | **giữ**; cờ: luật prompt này nói ≤ 8 CP, chủ dự án 02/10 nâng trần lên 11 | C | quyết định riêng của chủ dự án (sau luật ≤ 8) được giữ; cần chủ dự án xác nhận nếu muốn quay về 8 | — | không |
| C5 | Thưởng sức mạnh cho đơn vị nổ lan | 02 Xe_suy_ra / thuong_suc_manh | chưa áp (HOLD) | **giữ**; cờ `vehicles.priceRules.splashBonus = false` | C | không có luật | e30c8da1 | không |
| C6 | Thả quân tiền phương ở tiền đồn (chế độ nhanh); biến cố và trung lập LATER | 04 / 05 / 07 | tắt | **giữ**; cờ `modes.holdFlags.*` = false (true chưa có đường mã) | C | không có luật | e30c8da1 | không |
| C7 | Nhịp bắn xe người chơi chờ quyết (52 vũ khí, `Docs/balance/player_weapon_waitlist.md`) | 01 Vu_khi | như cũ | **giữ**, cờ giữ nguyên | C: chỉ sửa lỗi đơn vị rõ ràng | lượt L3 đã sửa lỗi đơn vị rõ ràng duy nhất (turret_rockets); 52 dòng còn lại đều có lý do, không dòng nào là lỗi đơn vị | — | không |

### Luật khóa đã kiểm (luật D) — khớp, không đổi

- Kinh tế chỉ có tiếp tế: phí duy trì duy nhất là phần vượt tiếp tế (`TeamEconomy.Upkeep`); prompt 29 §0 đã bỏ phí thứ hai. Khớp.
- Trần 32 xe + 6 máy bay: `TeamEconomy.MaxVehicles` 32 / `MaxAircraft` 6 (nay `modes.teamEconomy.*`). Phe địch 48 ở Công thành / Phòng thủ / Vô tận / chiến dịch lớn (`economy.vehicleCap`) là ngoại lệ có từ prompt 5 và được giữ ở mọi lần nhắc luật (DECISIONS dòng 5297). Giữ, ghi cờ.
- Chỉ pháo sáng và APS là tự vệ của xe: hệ chặn đạn của xe là `SelfAps` (chỉ tên lửa điều khiển, drone, rocket bắn thẳng) và pháo sáng theo lần. Khói tự vệ (`apc_smoke`, `elite_smoke`, đồ Laser warning) là che khuất (mất ngắm tên lửa dẫn theo tầm nhìn), không phải hệ chặn; có từ trước luật và được giữ qua prompt 29 / 32. Giữ, ghi cờ cho chủ dự án.
- POINT_DEFENSE không chặn đạn pháo xe tăng: `DamageSystem.TryIntercept` / `GunTakes` chỉ nhận tên lửa, drone, rocket, đạn pháo bắn cầu tầm; đạn xe tăng bắn thẳng bị loại. Khớp.
- Nhóm giá ≤ 4 ×1,0, 5–8 ×1,15, 9–13 ×1,25, ≥ 14 ×1,3 làm tròn nửa lên và thưởng min(15 %, 1,25 % × (baseCP − 8)): đã nướng vào dữ liệu (manifest_v2 B1 / B5); mã không tính lại. Nay là tham số `vehicles.priceRules.*` cho bộ xuất (Xe_suy_ra). Khớp.
- Vũ khí to thì mỗi phát mạnh hơn, nạp lâu hơn: dữ liệu; `full_weapon_audit.py` (cung_ho_nhat_quan) kiểm. Không có mã trái luật.
- Gungnir là boss chủ lực: dữ liệu `rank: main`; săn boss đếm main (prompt 29 C11). Hai chỗ mã còn sai: sửa (D3).
- Đội mở màn trừ vào CP khởi đầu, tối đa 60 %: `OpeningSquads.Apply` (ngân sách = CP khởi đầu × `openingSquads.share` 0,6, trừ qua `DeployOpening`). Khớp.
- Tướng địch "bỏ chạy" trong sự kiện chiến dịch (`retreatAt` 0,3, D.2 prompt 23) là cảnh truyện, không phải AI rút theo máu. Giữ, ghi cờ.

### Hằng số trong mã → dữ liệu (luật B, mục 4)

- Đã đưa ra: **238** hằng số khai báo (const / static readonly / thuộc tính; 227 ở (b), 11 ở (b2)) + **8** số trong công thức (tiếp tế = armyCap × 1,5;
  đường phạt 0,5; sàn 0,25; điểm bắt kịp đầy 0,2; khoảng tiền thưởng 0,5–1,5; 10 s tính công; và hệ số giá 1,16 của C1) +
  **14** số luật giá (nhóm giá, thưởng sức mạnh, thả dù theo nhóm) và cờ HOLD: 260 khóa trong
  `Assets/MachineBrigade/Resources/Data/tunables.json`, nhóm theo lĩnh vực (weapons 01, vehicles 02, bosses 03, bases 04,
  modes 05, ai 06, campaign 07, maps 08) → lớp chủ → tên; mỗi khóa có `value`, `unit`, `kind` (nhóm của bản quét),
  `linh_vuc`, `code`. Mã đọc qua `SimTunables` (thuộc tính cùng tên cũ); GameContent.LoadCatalog nạp file.
- Thứ tự ưu tiên đã làm hết: sát thương, thời gian / hồi chiêu, tầm / bán kính, tiếp tế, thưởng, trần, xác suất, tần suất cập
  nhật, giới hạn thực thể (mọi khai báo được bản quét gợi ý "co" trong Sim/** và Game/Match/**).
- Chưa đưa ra: **3 132** dòng "co" của bản quét (không tính SimTunables* và BalancePackFacts): **3 097** số viết thẳng trong
  biểu thức (so_cung: ban_kinh 882, sat_thuong 709, thoi_gian 626, gioi_han_thuc_the 239, tran 199, nguong 195, tan_suat 192,
  xac_suat 55; trong đó có CP khởi đầu từng chế độ ở các `SideSetup`) và **35** khai báo:
  - khong_anh_huong_loi_choi (giữ trong mã): nhịp thoại / radio (`Dialogue.*` 9, `RadioDirector.*` 4, `ReactiveRadio.*` 4),
    `FrontMap.Reach` (chạm UI), `DecisionLog.Capacity` (log), kích thước mảng / chỉ số (`ArmourLevels.Max`, `MaxUnit`,
    `DamageTable.PenetrationSteps`, `ConquestAi.Levels`), bố cục save (`Gear.NormalSlots`, `SubCount`, `TowerSlotCount`,
    `FixedDeckDef.VehicleSlots` / `SupportSlots`), sai số toán (`StickTolerance`, `MissionEvents.HalfTick`), số của sổ tay
    (`HandbookFacts.ReactiveCap`), `WeaponDef.BarrelGap` (hình);
  - còn ảnh hưởng lối chơi, chưa đưa: `Armour.FragmentPenetration` (1), `ClusterDef.DefaultPenetration` (2),
    `FixedDeckDef.MaxLoaned` (2), hai hằng cục bộ (`WorldModel` reach 25, `GearSystem` radius 10).
- Bản quét `Tools/export/scan_constants.py` (lane C) nên bỏ qua `Scripts/Sim/Content/SimTunables*.cs`: giá trị mặc định ở
  đó là bản sao của dữ liệu.

### Test (§4, §7.5)

- `ReplayHashTests` (EditMode): 8 trận cố định (Chiếm cứ điểm ashfield s3, Tử chiến greenvale s5, Vua đồi dunebreak s4, Công
  thành ashfield s7, Vô tận ironport s11, Sinh tồn frostpeak s6, Săn trùm liên tiếp ashfield s2, nhiệm vụ khung chiến dịch
  s9), 2 400 tick, băm `SimWorld.StateHash` mỗi 400 tick; baseline `Docs/export/replay_hashes.txt` (ghi ở lần chạy đầu, hoặc
  `MB_REPLAY_RECORD=1`; dòng `# rules: N`). Ở (b) mọi trận phải giống hệt; ở (c) trận trong `ChangedByRules` được phép khác
  khi baseline ghi trước luật (rules 0), sau khi ghi lại (rules 1) thì phải giống hệt.
- `TunablesTests`: file có đủ mọi khóa, không khóa lạ, giá trị bằng mặc định của mã.
- `BalancePackRuleTests`: D3 và C1. `AiTests` / `PlayTest6Tests`: hai test cũ khẳng định rút theo máu được viết lại theo luật khóa.

### Khóa mới cho bộ xuất (lane C)

- Nguồn dữ liệu mới: `Assets/MachineBrigade/Resources/Data/tunables.json` (JSONC; lĩnh vực → lớp → tên → `value` / `unit` /
  `kind` / `linh_vuc` / `code`); field_path cho nhập ngược: `tunables.<lĩnh vực>.<lớp>.<tên>.value`.
- game.json (ExportGameDoc, `MB_EXPORT`): khóa gốc mới `balancePack`, mỗi mục một khóa con; mục lỗi ghi `{"error": ...}`:
  `tunables` (key, unit, value của mọi khóa), `interception` (kinds = 9 cột chan_*; carriers[].blocks / shellShare),
  `roundGroups` (Hanh_vi_dan_nhom: homing, flareTakes, apsEligible, ciwsEligible, interceptable, warns, maxFlightSeconds; rules),
  `secondRounds` (Dan_thay_the: minSwitchSeconds, roundHoldSeconds, rounds[]), `flaresPerRelease` (Phao_sang so_qua:
  flaresMin / Max, charges, rechargeSeconds), `weaponFlight` (thoi_gian_bay_toi_tam: flightAtRangeSeconds),
  `vehicles` (Xe / Xe_suy_ra: priceGroup, priceFactor, splashUnit, powerBonus, dropByGroupSeconds, hpInBattle, selfDefence,
  selfDefenceRechargeSeconds = hoi_tu_ve_s, unlock = mo_khoa), `openingSquads` (phan_tram_cp_khoi_dau: share, maxShare),
  `aircraftShotBand` (KHONG_AP_DUNG + lý do), `boss` (timeToKillSeconds, compensation KHONG_AP_DUNG, hunt.bosses[].airDefence),
  `towers` (Thap: card = the_cu_gop_vao, outgoingDamageMult / balanceCut = co_can_bang, unlockRoute = mo_khoa,
  selfDefenceRechargeSeconds = hoi_tu_ve_s), `economy` (formula, modes[] armyCap / supply, upkeepCurve, catchUpCurve, refunds,
  endless.coinDecay = he_so_tang_thuong), `dialogue` (speakers[] / characters[].portrait = chan_dung, triggers[] once / repeat
  = hoi_chieu_so_lan, gapsSeconds, maxVisibleLines = so_dong_hien_thi_toi_da), `missions` (scriptStatus = trang_thai_kich_ban,
  deckGoal KHONG_AP_DUNG), `matchEnd` (Ket_tran), `cutscene` (Cutscene_khoanh_khac), `audio` (Am_thanh_mixer volumes,
  groups; Am_thanh_thu_vien library), `wrecks` (Xac_vo by tier), `models` (KHONG_AP_DUNG cho LOD1 + lý do), `previews`
  (Xem_truoc), `defaultSettings` (Cai_dat_mac_dinh).
- so_dong_hien_thi_toi_da: đo bằng độ rộng glyph của font UI (Barlow Regular qua UnityEngine.Font, cỡ 29 px chữ lớn), dải
  hẹp nhất (tham chiếu HUD 1280 × 720, cỡ UI ×1,1, dải nằm cạnh bảng chọn đang mở, có chân dung 52 px); UI Toolkit cần panel
  sống nên đây là ngắt dòng theo số đo font, không phải engine chữ.


## Lane C — cấu trúc gói và phần xuất

Nhánh `feature/pack-c`, một commit mỗi lượt: lượt 1 và bổ sung cấu trúc `63d102a8`, lượt 2 (md) `f8550c12`, lượt 5 (nhập ngược)
`3eae75bc`; sau khi gộp `lead/integration` (phần game của lane B) và đọc `game.json`: commit lượt 6 (kiểm tra, gói
`Docs/export/current/`, CHANGES / DECISIONS / CHANGELOG). Lane C không đổi giá trị game nào và không sửa C#, balance.json hay dữ liệu.

### Số sheet / dòng / cột, trước và sau (mỗi ô: sheet / dòng / cột)

| file | trước | sau |
|---|---|---|
| 01_chien_dau (cũ 01 + 02) | 50 / 3293 / 1051 | 57 / 3485 / 1350 |
| 02_boss (cũ 03) | 44 / 1851 / 805 | 45 / 1879 / 816 |
| 03_can_cu (cũ 04) | 28 / 676 / 666 | 30 / 890 / 702 |
| 04_che_do_kinh_te_ai (cũ 05 + 06 + 11) | 54 / 1980 / 657 | 46 / 1466 / 587 |
| 05_chien_dich (cũ 07) | 35 / 9134 / 555 | 31 / 2792 / 518 |
| 06_ban_do (cũ 08) | 41 / 151332 / 511 | 32 / 6583 / 425 |
| 07_hinh_anh_am_thanh_model (cũ 09 + 10) | 43 / 41539 / 563 | 33 / 16266 / 491 |
| 08_tham_chieu (cũ 13) | 7 / 7293 / 74 | 5 / 945 / 54 |
| 00_index (cũ 00_chi_muc) | 14 / 8116 / 130 | 4 / 5575 / 44 |
| 12_he_thong_trang_thai | 23 / 16009 / 191 | (bỏ khỏi gói) |
| bulk.zip | (nằm trong xlsx cũ) | 21 CSV / 177485 / 213 |

Tổng: trước 339 sheet / 241 223 dòng (13 file lĩnh vực và chỉ mục); sau 283 sheet trong 9 xlsx và 21 CSV trong bulk.zip.
Gói chỉ có 19 file và `images/` (29 ảnh, tiền tố file, chỉ ảnh mà một md dẫn tới; ảnh trước / sau dựng lại model, 304 MB, không còn).

### Sheet rời khỏi gói (bảng đầy đủ: `_qa/qa.xlsx`, sheet `Ngoai_goi`, sinh khi chạy)

- Mục 2.1 (quy trình, test, validator, manifest, lịch sử đo, quyết định, chờ quyết, bảng đơn vị tài liệu, thiếu nguồn): 24 sheet
  của file 12, `Tham_chieu_decisions`, `Thieu_nguon` (6 332 dòng); lá nguồn của chúng tính là Khong_xuat trong độ phủ.
- Lịch sử, không phải giá trị game: `Model_lich_su` (120 dòng ghi chú dựng lại model), `Anh_chup` (chỉ mục ảnh của md cũ).
- Mục 2.5 (một dòng KHONG_CO, game không có thứ đó): `Telemetry`, `Thanh_tuu`, `Tuong_vu_khi`, `Mo_dun_tien_ich_vu_khi` và 6 sheet
  `*_so_sanh_that` rỗng. Ô `KHONG_CO` trong sheet nhiều dòng đổi thành `KHONG_AP_DUNG`, lý do ở `Schema.ly_do_khong_ap_dung`.
- Mục 4: `Hang_so_trong_ma` chỉ còn ở `_qa/Hang_so_trong_ma.csv` (7 065 dòng sau khi bỏ `SimTunables*` và `BalancePackFacts`).
- Bom: 4 sheet tĩnh gộp vào 01 (`Bom_vu_khi`, `Bom_don_vi`, `Bom_hanh_vi`, `Bom_canh_bao`); `Bom_vet_tha` và `Bom_ket_qua_vung` là số đo
  của test Unity (vết thả, trước / sau), không phải dữ liệu: không vào gói. Thư mục `bom_2026-10-03` và các vết csv của nó xóa khỏi git.
- Mục 2.3: 21 sheet vào `bulk.zip` (`<file>__<sheet>.csv`); `06_ban_do` thêm `Ban_do_tom_tat` (mỗi bản đồ một dòng: vật thể theo loại,
  phần trăm diện tích mỗi tag địa hình, ô căn cứ, ô pháo đài, đường, làn, điểm nghẽn); `Thoai_thong_ke` (theo nhiệm vụ) giữ trong xlsx.

### Phân loại `Khac_chua_phan_loai`

| mục | vào | lý do |
|---|---|---|
| Anh_can_cu, Anh_can_cu_mui_ten, Anh_can_cu_vien | 03_can_cu | hình của chính ô căn cứ |
| So_tay_dan | 01_chien_dau | xe mẫu của sổ tay đạn |
| Anh_the (bulk), Hau_ky_hinh_anh | 07_hinh_anh_am_thanh_model | hình ảnh |
| Thoi_tiet, Do_kho | giữ ở 06_ban_do, 04_che_do_kinh_te_ai | chiến dịch chỉ dùng lại |
| Test_kich_ban, Validator_*, Bang_don_vi_tai_lieu | ngoài gói | không phải dữ liệu game |

### Đơn vị (`Don_vi_chua_ro` đã bỏ)

350 cột số (300 tên) chưa biết đơn vị được điền vào `Schema.don_vi` (`core/units_fill.py`: chú thích C# của `TierFx.Muzzle`,
`EffectLife.Band` và tên cột): s, m, m/s, deg, hp, hp/s, CP, xu, điểm, byte, `so_luong`, `he_so`, `ty_le`, `khong_don_vi`. Cột số đã
biết là không đơn vị cũng ghi `khong_don_vi`; sheet khóa / giá trị ghi `theo_cot_don_vi`. Còn **14** cột ghi `khong_ro` (mã và chú
thích không nói): `Trang_bi_bo` (two_piece_arg1-3, four_piece_arg1-3), `Boss.tiers_opening`, `Boss.tiers_shift`,
`Boss_khung.defaults_tiers_shift`, `AI_ho_so_che_do.hq_skill_threat`, `AI_tham_so.min` / `.max`, `Vat_the_loai.collapse`,
`VFX_chay_than_xe.power`.

### NEED_CODE_CHECK: trước / sau

- Trước: 5 723 ô (cả Schema và README). Sau khi gộp lane B và đọc `game.json` (`--game-json`): **103 ô, 8 sheet**; 5 326 ô điền từ
  `balancePack`; 7 cột KHONG_AP_DUNG kèm lý do (dải phát để hạ máy bay, bù boss, mục tiêu gốc bộ bài, LOD1 của model, độ lệch nòng
  RIPPLE, mở khóa xe tinh nhuệ, hướng dẫn người chơi mới); sáu sheet chỉ có một dòng dấu hiệu (cài đặt mặc định, khoảnh khắc điện
  ảnh, kết trận, xác vỡ, màn xem trước, mixer) thành sheet thật từ `game.json`.
- Còn lại, `game.json` chưa có giá trị (lane B / chủ dự án): `Bom_canh_bao.ban_kinh_ria_m` (10), `Bom_vu_khi` cột `ria_m` và
  `loai_sat_thuong` (14), `Bom_don_vi` cột `do_cao_tha_m` và `nap_lai_s` (10): bán kính rìa, độ cao thả, thời gian nạp của đòn không
  kích và đòn lớn nằm ở `StrikeSystem` / `BossSystem`; `Hanh_vi_dan_nhom.tuong_tac_gay_nhieu` (7); `Khac_che` dòng
  `main_battle_tank` (9: APS chỉ khi gắn Trophy); `Phao_sang` `flare_tower`, `flare_searchlight_tower` (2); `Sanhunt.tuan` (41);
  `Dot_phong_thu` cột `he_so_do_kho`, `duong_cong_dot` (10).
- Hai chỗ giá trị là gộp, không đo từng dòng (ghi ở `Schema.y_nghia`): `Thoai.so_dong_hien_thi_toi_da` = số dòng của dòng thoại tệ nhất
  (cùng số cho mọi dòng); `Hanh_vi_dan_nhom` (7 loại đạn) là trung bình theo số vũ khí của các nhóm chặn đạn của game (`roundGroups`;
  Bullet và Flame cùng nhóm `other`).

### Hằng số trong mã

- Lane B đã đưa ra 260 khóa (`tunables.json`); bộ xuất hiện chúng trong sheet lĩnh vực: `Hang_so_vu_khi`, `Hang_so_phuong_tien` (01),
  `Hang_so_boss` (02), `Hang_so_can_cu` (03), `Hang_so_che_do`, `Hang_so_ai` (04), `Hang_so_chien_dich` (05), `Hang_so_ban_do` (06);
  mỗi hằng số một dòng (giá trị, đơn vị, nhóm quét, tên C#), sửa được qua nhập ngược. Không có file 99.
- Chưa đưa ra: **3 132** dòng "co" của bản quét (`_qa/Hang_so_trong_ma.csv`): 3 097 số viết thẳng trong biểu thức và 35 khai báo
  (xem phần lane B); 3 933 dòng là hạ tầng.
- Cầu nối: dữ liệu JSON dưới `Assets/` mà không sheet nào nhận (khối mới của balance.json, file dữ liệu mới) vào sheet khóa / giá trị
  `Hang_so_<khối>` của file chọn theo tên khối (`core/pack.py`, `CONST_ROUTE`), nên độ phủ không vỡ khi lane B thêm khóa.

### Quyết định của lane C (không đổi giá trị game)

- `_truoc` / `_sau`: giữ; mốc so sánh là `5f5b3247`, commit ngay trước khi áp cân bằng đợt 2 (prompt 29), mặc định của `--base`.
- Chữ quy trình: "prompt N", "lượt N", CHUA_AP, "HOLD:" bị bỏ khỏi chữ của ô, md và Schema (không đụng chữ thoại, chuỗi địa phương
  hóa, giấy phép: chữ của chính game); chỗ nói tới file cũ (`09_hieu_ung_am_thanh/Am_thanh`) đổi sang tên mới.
- Dấu hiệu còn lại: `NEED_SOURCE` (thông số ngoài đời: `*_tham_chieu`, `Vu_khi.ngoai_doi_*`), `KHONG_AP_DUNG`, `NEED_CODE_CHECK`.
- Kiểm tra: `export.py check` xuất hai lần (hai tiến trình) và chạy mọi test của mục 7; CI chạy nó vào thư mục tạm và chạy
  `check --structure-only` trên `Docs/export/current`. Không chạy test game hay replay.

## Lane B — 103 ô NEED_CODE_CHECK còn lại (`feature/pack-b2`)

Không đổi giá trị game nào; luật A (hàm xuất chỉ đọc) và luật B (hằng số ra `tunables.json`, giữ nguyên giá trị). Không chạy
Unity hay test; Sim, Game và Tests biên dịch bằng .NET SDK với DLL của Unity 6. Bộ đọc lane C (`core/gamefill.py`) thử trên một
game.json giả (khóa mới, số giả): export + `check --structure-only` qua hết, NEED_CODE_CHECK 0.

| Sheet / cột | Ô | Cách | Giá trị / lý do |
|---|---|---|---|
| `Bom_vu_khi.ria_m`, `Bom_canh_bao.ban_kinh_ria_m` | 20 | A | thẻ hỗ trợ: 0 (StrikeSystem gọi `Splash` không có lớp rìa; sát thương giảm tới `rimShare` ở mép); siêu vũ khí boss: `BigStrikeDef.EdgeRadius` (gấp đôi lõi, tối đa 20 m) |
| `Bom_vu_khi.loai_sat_thuong` | 4 | A | `SupportDef.DamageType` (mặc định HighExplosive khi dữ liệu không ghi) |
| `Bom_don_vi.do_cao_tha_m` | 6 | A + KHONG_AP_DUNG | thẻ ném bom: độ cao hình của `StrikeEffects` (máy bay 24 m, oanh tạc cơ 32 m), mô phỏng không dùng; `glide_bomb_strike`, `cluster_at_strike`: KHONG_AP_DUNG (không có máy bay thả) |
| `Bom_don_vi.nap_lai_s` | 4 | KHONG_AP_DUNG | boss (argus, command_airship, garuda, morrigan): `VehicleDef.LoadOf` = 0 với boss, không về nạp |
| `Hanh_vi_dan_nhom.tuong_tac_gay_nhieu` | 7 | A + B | tỷ lệ vũ khí đạn dẫn đường (tên lửa, drone) không jamProof; trượt 5–11 m; hỗ trợ ×2,2; drone bầy boss 0,5 |
| `Khac_che` dòng `main_battle_tank` | 9 | A + B | `chan_*` = "khong" (xe khi chưa lắp); cột mới `aps_nang_cap` (Trophy: r 20 m, 2 đạn chặn, 20 s) và `chan_khi_nang_cap` (chặn được gì khi lắp) — APS là tự vệ duy nhất ngoài pháo sáng, nên nâng cấp ghi như APS |
| `Phao_sang` `flare_tower`, `flare_searchlight_tower` | 2 | A | `1;1`: tháp pháo sáng chiếu sáng bắn một quả mỗi lần (FieldWorksSystem.Flares), mỗi 15 s, chỉ ban đêm |
| `Sanhunt.tuan` | 41 | A | tuần = năm ISO × 100 + tuần ISO (UTC); `BossHunts.Weekly(tuần)` xuất cho 53 tuần năm 2026 (năm cố định để gói không đổi theo ngày); ô: số tuần / 53 rồi `Wnn#vị trí` |
| `Dot_phong_thu.he_so_do_kho` | 5 | A + B | `BaseStrength.WaveScale(ReferenceScore(cấp HQ))` |
| `Dot_phong_thu.duong_cong_dot` | 5 | A + B | số xe đợt 1–10 ở Thường (`SiegeMode.WaveSize`); Dễ / Khó trong game.json |

Theo từng dòng (trước là số gộp): `Hanh_vi_dan_nhom` đọc `roundGroups.projectileGroups` (đếm đúng trên dạng đạn của dòng; game.json cũ
vẫn dùng trung bình có trọng số); `Thoai.so_dong_hien_thi_toi_da` đọc `dialogue.maxVisibleLines.perLine` (số dòng của chính câu đó,
Việt hoặc Anh lấy số lớn, dải hẹp nhất). Cả hai đều làm được theo dòng; không còn chỗ gộp.

### Hằng số ra dữ liệu (luật B, 24 khóa mới, cùng giá trị)

- `weapons.damageRules.edgeFalloff` 0,25 (DamageSystem.EdgeFalloff).
- `weapons.jamRules`: `guidedMissMin` 5, `guidedMissSpread` 6 (CombatSystem.Launch), `strikeScatter` 2,2 (StrikeSystem.Launch),
  `swarmJamChance` 0,5 (BossSystem.BigAttacks, drone bầy).
- `vehicles.trophyRules`: `radius` 20, `charges` 2, `recharge` 20, `builtInExtraCharges` 1, `builtInRechargeScale` 0,75
  (GearSystem.Equip → `GearSystem.TrophyAps`).
- `modes.defendWaves`: `startEasy/Normal/Hard` 2/3/4, `endlessStartEasy/Normal/Hard` 4/5/6, `growth` 1,8, `growthHard` 2,0,
  `endlessGrowth` 1,2, `endlessCompound` 0,06, `waveMax` 36 (ModeSessions DefendSession.Build → `SiegeMode.DefendWave*`).
- `modes.baseStrengthRules`: `waveScaleExponent` 0,75, `waveScaleMin` 0,75, `waveScaleMax` 2,5 (BaseStrength.WaveScale).
- Tổng khóa `tunables.json`: 284. Test mới `TunablesTests.PassTwoMovesKeepTheOldLiterals` (viết, chưa chạy).

### Khóa game.json mới (`balancePack`)

- `interception.upgrades[]` (id, module, capability, baseHasAps, radius, charges, recharge, blocks, shellShare).
- `roundGroups.groups[].jamTakes`, `roundGroups.projectileGroups[]` (như groups, khóa `projectile`), `roundGroups.rules.jam*`.
- `flaresPerRelease[]` thêm dòng `size = illumination` (litRadius, litSeconds, range).
- `boss.hunt.weekRule`, `weeksYear`, `weeks[]` (week, run).
- `dialogue.maxVisibleLines.perLine` (khóa câu → số dòng).
- `strikes` (supports[] type / edgeRadius / rimShare / releaseAltitude; bigAttacks[].strikes[] edgeRadius / edgeShare / falloff;
  carriers[] rearmSeconds / loaded; supportRule, bigRule, altitudeRule).
- `defenceWaves` (rule, waveCount, levels[] level / referencePower / referenceScore / waveScale / incomeScale / waves{Easy, Normal, Hard}).
- Bộ đọc: sheet `Bom_*` vào file 01 sau công thức, nên `pack.add_bom_sheets` gọi `gamefill.fill_late` (ctx.game).


## Lane C — cấu trúc gói và phần xuất

Nhánh `feature/pack-c`, một commit mỗi lượt: lượt 1 và bổ sung cấu trúc `63d102a8`, lượt 2 (md) `f8550c12`, lượt 5 (nhập ngược)
`3eae75bc`; sau khi gộp `lead/integration` (phần game của lane B) và đọc `game.json`: commit lượt 6 (kiểm tra, gói
`Docs/export/current/`, CHANGES / DECISIONS / CHANGELOG). Lane C không đổi giá trị game nào và không sửa C#, balance.json hay dữ liệu.

### Số sheet / dòng / cột, trước và sau (mỗi ô: sheet / dòng / cột)

| file | trước | sau |
|---|---|---|
| 01_chien_dau (cũ 01 + 02) | 50 / 3293 / 1051 | 57 / 3485 / 1350 |
| 02_boss (cũ 03) | 44 / 1851 / 805 | 45 / 1879 / 816 |
| 03_can_cu (cũ 04) | 28 / 676 / 666 | 30 / 890 / 702 |
| 04_che_do_kinh_te_ai (cũ 05 + 06 + 11) | 54 / 1980 / 657 | 46 / 1466 / 587 |
| 05_chien_dich (cũ 07) | 35 / 9134 / 555 | 31 / 2792 / 518 |
| 06_ban_do (cũ 08) | 41 / 151332 / 511 | 32 / 6583 / 425 |
| 07_hinh_anh_am_thanh_model (cũ 09 + 10) | 43 / 41539 / 563 | 33 / 16266 / 491 |
| 08_tham_chieu (cũ 13) | 7 / 7293 / 74 | 5 / 945 / 54 |
| 00_index (cũ 00_chi_muc) | 14 / 8116 / 130 | 4 / 5575 / 44 |
| 12_he_thong_trang_thai | 23 / 16009 / 191 | (bỏ khỏi gói) |
| bulk.zip | (nằm trong xlsx cũ) | 21 CSV / 177485 / 213 |

Tổng: trước 339 sheet / 241 223 dòng (13 file lĩnh vực và chỉ mục); sau 283 sheet trong 9 xlsx và 21 CSV trong bulk.zip.
Gói chỉ có 19 file và `images/` (29 ảnh, tiền tố file, chỉ ảnh mà một md dẫn tới; ảnh trước / sau dựng lại model, 304 MB, không còn).

### Sheet rời khỏi gói (bảng đầy đủ: `_qa/qa.xlsx`, sheet `Ngoai_goi`, sinh khi chạy)

- Mục 2.1 (quy trình, test, validator, manifest, lịch sử đo, quyết định, chờ quyết, bảng đơn vị tài liệu, thiếu nguồn): 24 sheet
  của file 12, `Tham_chieu_decisions`, `Thieu_nguon` (6 332 dòng); lá nguồn của chúng tính là Khong_xuat trong độ phủ.
- Lịch sử, không phải giá trị game: `Model_lich_su` (120 dòng ghi chú dựng lại model), `Anh_chup` (chỉ mục ảnh của md cũ).
- Mục 2.5 (một dòng KHONG_CO, game không có thứ đó): `Telemetry`, `Thanh_tuu`, `Tuong_vu_khi`, `Mo_dun_tien_ich_vu_khi` và 6 sheet
  `*_so_sanh_that` rỗng. Ô `KHONG_CO` trong sheet nhiều dòng đổi thành `KHONG_AP_DUNG`, lý do ở `Schema.ly_do_khong_ap_dung`.
- Mục 4: `Hang_so_trong_ma` chỉ còn ở `_qa/Hang_so_trong_ma.csv` (7 065 dòng sau khi bỏ `SimTunables*` và `BalancePackFacts`).
- Bom: 4 sheet tĩnh gộp vào 01 (`Bom_vu_khi`, `Bom_don_vi`, `Bom_hanh_vi`, `Bom_canh_bao`); `Bom_vet_tha` và `Bom_ket_qua_vung` là số đo
  của test Unity (vết thả, trước / sau), không phải dữ liệu: không vào gói. Thư mục `bom_2026-10-03` và các vết csv của nó xóa khỏi git.
- Mục 2.3: 21 sheet vào `bulk.zip` (`<file>__<sheet>.csv`); `06_ban_do` thêm `Ban_do_tom_tat` (mỗi bản đồ một dòng: vật thể theo loại,
  phần trăm diện tích mỗi tag địa hình, ô căn cứ, ô pháo đài, đường, làn, điểm nghẽn); `Thoai_thong_ke` (theo nhiệm vụ) giữ trong xlsx.

### Phân loại `Khac_chua_phan_loai`

| mục | vào | lý do |
|---|---|---|
| Anh_can_cu, Anh_can_cu_mui_ten, Anh_can_cu_vien | 03_can_cu | hình của chính ô căn cứ |
| So_tay_dan | 01_chien_dau | xe mẫu của sổ tay đạn |
| Anh_the (bulk), Hau_ky_hinh_anh | 07_hinh_anh_am_thanh_model | hình ảnh |
| Thoi_tiet, Do_kho | giữ ở 06_ban_do, 04_che_do_kinh_te_ai | chiến dịch chỉ dùng lại |
| Test_kich_ban, Validator_*, Bang_don_vi_tai_lieu | ngoài gói | không phải dữ liệu game |

### Đơn vị (`Don_vi_chua_ro` đã bỏ)

350 cột số (300 tên) chưa biết đơn vị được điền vào `Schema.don_vi` (`core/units_fill.py`: chú thích C# của `TierFx.Muzzle`,
`EffectLife.Band` và tên cột): s, m, m/s, deg, hp, hp/s, CP, xu, điểm, byte, `so_luong`, `he_so`, `ty_le`, `khong_don_vi`. Cột số đã
biết là không đơn vị cũng ghi `khong_don_vi`; sheet khóa / giá trị ghi `theo_cot_don_vi`. Còn **14** cột ghi `khong_ro` (mã và chú
thích không nói): `Trang_bi_bo` (two_piece_arg1-3, four_piece_arg1-3), `Boss.tiers_opening`, `Boss.tiers_shift`,
`Boss_khung.defaults_tiers_shift`, `AI_ho_so_che_do.hq_skill_threat`, `AI_tham_so.min` / `.max`, `Vat_the_loai.collapse`,
`VFX_chay_than_xe.power`.

### NEED_CODE_CHECK: trước / sau

- Trước: 5 723 ô (cả Schema và README). Sau khi gộp lane B và đọc `game.json` (`--game-json`): **103 ô, 8 sheet**; 5 326 ô điền từ
  `balancePack`; 7 cột KHONG_AP_DUNG kèm lý do (dải phát để hạ máy bay, bù boss, mục tiêu gốc bộ bài, LOD1 của model, độ lệch nòng
  RIPPLE, mở khóa xe tinh nhuệ, hướng dẫn người chơi mới); sáu sheet chỉ có một dòng dấu hiệu (cài đặt mặc định, khoảnh khắc điện
  ảnh, kết trận, xác vỡ, màn xem trước, mixer) thành sheet thật từ `game.json`.
- Còn lại, `game.json` chưa có giá trị (lane B / chủ dự án): `Bom_canh_bao.ban_kinh_ria_m` (10), `Bom_vu_khi` cột `ria_m` và
  `loai_sat_thuong` (14), `Bom_don_vi` cột `do_cao_tha_m` và `nap_lai_s` (10): bán kính rìa, độ cao thả, thời gian nạp của đòn không
  kích và đòn lớn nằm ở `StrikeSystem` / `BossSystem`; `Hanh_vi_dan_nhom.tuong_tac_gay_nhieu` (7); `Khac_che` dòng
  `main_battle_tank` (9: APS chỉ khi gắn Trophy); `Phao_sang` `flare_tower`, `flare_searchlight_tower` (2); `Sanhunt.tuan` (41);
  `Dot_phong_thu` cột `he_so_do_kho`, `duong_cong_dot` (10).
- Hai chỗ giá trị là gộp, không đo từng dòng (ghi ở `Schema.y_nghia`): `Thoai.so_dong_hien_thi_toi_da` = số dòng của dòng thoại tệ nhất
  (cùng số cho mọi dòng); `Hanh_vi_dan_nhom` (7 loại đạn) là trung bình theo số vũ khí của các nhóm chặn đạn của game (`roundGroups`;
  Bullet và Flame cùng nhóm `other`).

### Hằng số trong mã

- Lane B đã đưa ra 260 khóa (`tunables.json`); bộ xuất hiện chúng trong sheet lĩnh vực: `Hang_so_vu_khi`, `Hang_so_phuong_tien` (01),
  `Hang_so_boss` (02), `Hang_so_can_cu` (03), `Hang_so_che_do`, `Hang_so_ai` (04), `Hang_so_chien_dich` (05), `Hang_so_ban_do` (06);
  mỗi hằng số một dòng (giá trị, đơn vị, nhóm quét, tên C#), sửa được qua nhập ngược. Không có file 99.
- Chưa đưa ra: **3 132** dòng "co" của bản quét (`_qa/Hang_so_trong_ma.csv`): 3 097 số viết thẳng trong biểu thức và 35 khai báo
  (xem phần lane B); 3 933 dòng là hạ tầng.
- Cầu nối: dữ liệu JSON dưới `Assets/` mà không sheet nào nhận (khối mới của balance.json, file dữ liệu mới) vào sheet khóa / giá trị
  `Hang_so_<khối>` của file chọn theo tên khối (`core/pack.py`, `CONST_ROUTE`), nên độ phủ không vỡ khi lane B thêm khóa.

### Quyết định của lane C (không đổi giá trị game)

- `_truoc` / `_sau`: giữ; mốc so sánh là `5f5b3247`, commit ngay trước khi áp cân bằng đợt 2 (prompt 29), mặc định của `--base`.
- Chữ quy trình: "prompt N", "lượt N", CHUA_AP, "HOLD:" bị bỏ khỏi chữ của ô, md và Schema (không đụng chữ thoại, chuỗi địa phương
  hóa, giấy phép: chữ của chính game); chỗ nói tới file cũ (`09_hieu_ung_am_thanh/Am_thanh`) đổi sang tên mới.
- Dấu hiệu còn lại: `NEED_SOURCE` (thông số ngoài đời: `*_tham_chieu`, `Vu_khi.ngoai_doi_*`), `KHONG_AP_DUNG`, `NEED_CODE_CHECK`.
- Kiểm tra: `export.py check` xuất hai lần (hai tiến trình) và chạy mọi test của mục 7; CI chạy nó vào thư mục tạm và chạy
  `check --structure-only` trên `Docs/export/current`. Không chạy test game hay replay.

## Play-test 13 (lane C)

Nhánh `feature/pt13-c`. Mọi số đổi trong lượt này (lý do ngoài đời: `Docs/DECISIONS.md` "Play-test 13 (lane C)").

### tunables.json (khóa mới, `weapons.countermeasures`)

| khóa | giá trị | ý nghĩa |
|---|---|---|
| flareCueSeconds | 1.5 s | pháo sáng bắn khi tên lửa còn ≤ 1.5 s là tới (cảnh báo giai đoạn cuối) |
| flareGraceSeconds | 0.5 s | tên lửa tới trong lúc đám pháo sáng cháy + 0.5 s đều bị thử cùng một lần tung |
| apsVolleySeconds | 0.4 s | một lần kích hoạt APS xe chặn mọi đạn tới trong 0.4 s, tốn 1 lần nạp |
| apsRechargeScale | x1.5 | APS xe nạp lại chậm hơn 1.5 lần (bù cho luật trên) |

### balance.json (luật, dữ liệu)

| mục | cũ | mới |
|---|---|---|
| warningRules.normalFire | (không có: bắn thường T4+ có vòng + giữ đạn) | false: bắn thường không vòng, không giữ |
| leviathan.salvo.warning | leviathan_shell (vòng 3.7 s) | bỏ: đạn bay theo tốc độ pháo 406 |
| boss_thermo (Inferno) | TOS-1A 220 mm rocket, 6 x 97 / 12.51 s, minRange 10 | pháo 125 mm đạn nhiệt áp, 291 / 6.255 s, bắn thẳng, 170 m/s |
| p26_behemoth_tiny_kornet_twin | 2 Kornet x 230 / 19.4 s | đạn pháo phụ 120 mm 230 / 9.7 s |
| flightProfile Ballistic | — | boss_rockets, p26_behemoth_be_rockets, p26_jotunn_jo_rockets (và các vũ khí kế thừa) |
| flightProfile Loft | — | sam_pac3, sam_48n6, tamir, leviathan_cruise, cruise_missile_ground, nsm_coastal; họ mim_104_patriot_pac_2, nsm_oniks |
| tiers.enterLow | (không có: mở màn trên quỹ đạo + hạ dần 4 s) | true (mặc định): vào thẳng tầng thấp |
| mainAim Hull | turret xoay | ballistic_launcher, ground_cruise_missile_vehicle, coastal_ashm_vehicle |

### Tốc độ đạn (projectileSpeed, m/s; ~0.3 x tốc độ trung bình ngoài đời, trần 300, không giảm)

Sửa ở họ vũ khí (family) khi vũ khí lấy tốc độ từ họ; cột cuối là vũ khí kích hoạt sửa khi khác tên.

| mục | cột | cũ | mới | vũ khí |
|---|---|---|---|---|
| apkws (family) | projectileSpeed | 45 | 180 | apkws_rocket |
| 9m120_ataka (family) | projectileSpeed | 26 | 120 | ataka |
| atgm | projectileSpeed | 20 | 80 |  |
| 9m133_kornet (family) | projectileSpeed | 22 | 80 | atgm_heavy |
| atgm_post | projectileSpeed | 19 | 60 |  |
| avenger_stingers | projectileSpeed | 42 | 200 |  |
| ballistic_missile | projectileSpeed | 50 | 200 |  |
| s_8_80_mm (family) | projectileSpeed | 40 | 180 | boat_rockets |
| boss_howitzer | projectileSpeed | 60 | 100 |  |
| 2b8_240_mm (family) | projectileSpeed | 38 | 60 | boss_mortar |
| boss_rockets | projectileSpeed | 45 | 130 |  |
| tos_1a_220_mm_thermobaric (family) | projectileSpeed | 35 | 70 | boss_thermo |
| 9m317_buk (family) | projectileSpeed | 50 | 250 | buk_launcher |
| caesar_155 | projectileSpeed | 45 | 100 |  |
| m284_155_mm_2 (family) | projectileSpeed | 45 | 100 | casemate_155 |
| cruise_missile_ground | projectileSpeed | 22 | 70 |  |
| cruiser_203 | projectileSpeed | 70 | 110 |  |
| agm_114_hellfire (family) | projectileSpeed | 26 | 110 | drone_missile |
| bm_21_grad_122_mm_2 (family) | projectileSpeed | 45 | 130 | grad_cluster |
| bm_21_grad_122_mm (family) | projectileSpeed | 45 | 130 | grad_rockets |
| griffin | projectileSpeed | 22 | 70 |  |
| gun_launched_atgm | projectileSpeed | 22 | 90 |  |
| hydra_70_mm (family) | projectileSpeed | 40 | 180 | heli_rockets |
| hover_rockets | projectileSpeed | 50 | 85 |  |
| igla_v | projectileSpeed | 24 | 170 |  |
| jassm | projectileSpeed | 20 | 70 |  |
| kh29 | projectileSpeed | 32 | 120 |  |
| khrizantema | projectileSpeed | 24 | 120 |  |
| leviathan_460 | projectileSpeed | 60 | 200 |  |
| leviathan_cruise | projectileSpeed | 24 | 70 |  |
| maverick | projectileSpeed | 23 | 90 |  |
| missile_57e6 | projectileSpeed | 55 | 300 |  |
| mlrs_elite | projectileSpeed | 50 | 140 |  |
| m31_gmlrs_227_mm (family) | projectileSpeed | 50 | 140 | mlrs_rockets |
| 2b11_120_mm (family) | projectileSpeed | 32 | 60 | mortar_120 |
| nsm_coastal | projectileSpeed | 40 | 85 |  |
| p26_behemoth_be_rockets | projectileSpeed | 45 | 130 |  |
| p26_jotunn_jo_rockets | projectileSpeed | 45 | 120 |  |
| mim_104_patriot_pac_2 (family) | projectileSpeed | 60 | 300 | patriot |
| r37m | projectileSpeed | 70 | 300 |  |
| r60 | projectileSpeed | 42 | 210 |  |
| recon_missile | projectileSpeed | 22 | 60 |  |
| rockets_300mm | projectileSpeed | 55 | 120 |  |
| sam | projectileSpeed | 42 | 200 |  |
| sam_48n6 | projectileSpeed | 65 | 300 |  |
| sam_pac3 | projectileSpeed | 65 | 300 |  |
| smart_155_bonus (family) | projectileSpeed | 45 | 100 | smart_at_shell |
| spike_nlos | projectileSpeed | 26 | 55 |  |
| stinger_atas | projectileSpeed | 42 | 180 |  |
| stinger_post | projectileSpeed | 42 | 180 |  |
| supergun_800 | projectileSpeed | 120 | 140 |  |
| tamir | projectileSpeed | 50 | 180 |  |
| technical_rockets | projectileSpeed | 38 | 80 |  |
| uav_loiter_missile | projectileSpeed | 26 | 110 |  |
| vikhr | projectileSpeed | 24 | 120 |  |
| aim_9_sidewinder (family) | projectileSpeed | 55 | 210 | aim9, wvr_aam |
| agm_88_harm (family) | projectileSpeed | 45 | 210 | anti_radar_missile |
| nsm_oniks (family) | projectileSpeed | 30 | 225 | anti_ship_missile |
| air_to_air | projectileSpeed | 60 | 300 | |
| air_cruise_missile | projectileSpeed | 22 | 65 | |
| amos_120 | projectileSpeed | 32 | 60 | |

Trận replay bị ảnh hưởng: mọi trận (tốc độ đạn, pháo sáng, APS, cảnh báo) — baseline của ReplayHashTests cần ghi lại.

## Gói cân bằng 2, mục 5 — tầm tối thiểu cho boss (lane C)

Nhánh `feature/pack2-c`. Thay đổi lối chơi do chủ dự án yêu cầu (`Docs/prompts/export_pack2_vi.txt` mục 5). Tính tĩnh hoàn
toàn: `python Tools/export/boss_min_range.py` đọc boss như loader dựng (`Tools/balance/p26_ab.expand` + `bossFrames.defaults`),
vũ khí đã phân giải (inherits) và GLB của boss (nút `Muzzle_*` / `Mount_*`, cách VehicleView gán bệ thứ k của một slot cho nút thứ
k theo tên; tỉ lệ vẽ = `modelSize` hoặc `scale`). Kết quả: sheet `Boss_tam_toi_thieu` trong 02_boss (223 dòng, mỗi bệ một dòng,
đủ cột mục 5.1); QA: `_qa/boss_tam_toi_thieu.csv`, `_qa/boss_goc_nong_uoc_dinh.md` (sinh khi chạy, không commit). Không chạy
Unity, test hay ExportGameDoc. Gói `Docs/export/current/` chưa xuất lại (lead xuất sau khi gộp các lane).

### Cách tính (đo từ tâm boss tới mép gần của mục tiêu)

- Bắn thẳng: `max(0, (độ cao nòng − độ cao tâm mục tiêu) / tan(góc hạ)) + khoảng cách ngang theo hướng ngắm` (trục xoay → đầu
  nòng; phần lệch của trục xoay so với tâm boss đổi dấu theo hướng nên lấy trung bình 0; bệ Hull: phần về phía trước).
- Bệ rocket không hạ được (0°): phóng ngang rồi rơi: `sqrt(2 × tầm × độ chênh cao) + khoảng cách theo hướng ngắm`.
- Bắn cầu: `v² sin(2θ)/g` với `v = sqrt(g × tầm tối đa)` (tốc độ đạn đạo của game: `projectileSpeed` là nhịp bay, dùng nó cho ra
  hơn 1 km, vượt mọi tầm game) = `tầm × min(sin 2θmin, sin 2θmax)`; cối 45–85°, pháo / rocket bắn cầu 5–70°.
- Tên lửa, drone: `max(khoảng cách vũ trang, khoảng cách khóa)` = 1 m (ước định: 65–100 m ngoài đời × tỉ lệ tầm game); bom: 0.
- Boss bay: góc nhìn xuống tối đa 65° của VehicleView.Elevate, từ độ cao bay. Vũ khí chỉ bắn máy bay: không áp.
- Độ cao tâm mục tiêu: nửa chiều cao model của xe ở `Xe_tham_chieu`: xe tăng chủ lực 1,13 m (dùng cho đề xuất), xe bọc thép bánh
  lốp 1,0 → 0,76 m, tăng hạng nặng 1,07 m (cột riêng cho xe nhẹ và hạng nặng).
- Góc nòng: dữ liệu vũ khí và bệ không có; mặc định theo lớp mục 5.2, đánh dấu `uoc_dinh` (danh sách cho chủ dự án kiểm:
  `_qa/boss_goc_nong_uoc_dinh.md`, 144 bệ): pháo boss 8°, pháo hạm 5°, súng phụ (dưới 100 mm, hạm dưới 130 mm) 15°, pháo nhỏ /
  CIWS / cao xạ ≤ 40 mm 15°, súng máy và phun lửa 20°, bệ rocket 0°.
- Đề xuất = max(hiện có, hình học), làm tròn nửa lên 1 m. Đề xuất chạm tầm (≥ tầm − 1 m) bị cắt còn 80 % tầm (`cat_theo_tam`):
  minRange ≥ range làm WeaponDef ném lỗi lúc nạp, và tầm tối thiểu vượt tầm thì súng câm với mặt đất.
- Vùng chết của boss = nhỏ nhất của tầm tối thiểu các nòng chính (pháo, rocket, bắn cầu); dải chết = từ mép thân (bán kính boss;
  boss bay: 0) tới đó. Vũ khí phủ: mọi vũ khí bắn được mặt đất có tầm tối thiểu nhỏ hơn bán kính vùng chết (súng máy, CIWS,
  cao xạ, phun lửa, tên lửa, drone, bom, cận chiến). `co_che_vung_chet` = phủ ≥ 90 % dải chết (hoặc dải dưới 2 m).

### Mã: boss có bị miễn tầm tối thiểu không — KHÔNG

`CombatSystem.InReach` (mọi bệ, mọi người bắn, cả boss: chọn mục tiêu qua `IsValidAutoTarget` / `BestInRange` và chặn bắn ở
`Fire`) đã áp `MinRange` (tới tâm) và `MinReach` (tới mép); không có miễn trừ cho boss nên **không thêm cờ
`ap_dung_tam_toi_thieu`**. Nhưng không ghi vào `minRange`: `minRange > 0` biến vũ khí thành bắn cầu (`WeaponDef.Indirect`,
Definitions.cs: bỏ kiểm đường bắn, luật đánh chặn đạn cầu, vai pháo binh trong Commander / ConquestAi / TacticalAi, radar phản
pháo) — tức đổi hành vi AI, điều mục 5.2 cấm. `minReach` cũng không hợp: nó chặn cả máy bay (cao xạ của boss không bắn được
trực thăng ngay trên đầu). Nên thêm khóa vũ khí **`groundMinReach`** (m, chỉ mục tiêu mặt đất, đo như minReach):

- `Scripts/Sim/Combat/CombatSystem.cs` InReach: `if (weapon.GroundMinReach > 0f && !IsFlying(target) && distance - target.Radius < weapon.GroundMinReach) return false;`
- `Scripts/Sim/Content/Catalog.P25A.cs`: thuộc tính `WeaponDef.GroundMinReach`, đọc `"groundMinReach"` (mặc định 0).
- `Scripts/Sim/Content/Definitions.cs` `Tuned`: bản sao vũ khí mang theo `GroundMinReach`.
- `Tools/export/core/units.py`: `groundMinReach` có đơn vị m.

Biên dịch Sim bằng .NET SDK (netstandard2.1, C# 9): thành công, 0 lỗi, 2 cảnh báo có từ trước. AI (đi tới mục tiêu, vai trò,
né pháo binh) vẫn đọc `MinRange` như cũ; vũ khí có vùng chết chỉ không bắn được và đổi sang mục tiêu khác trong tầm.

### Số đổi trong balance.json

65 vũ khí boss: 63 nhận `groundMinReach`, 2 vũ khí đã bắn cầu nâng `minRange` (`supergun_800` 30 → 69, `p26_bastion_sec_b240`
12 → 14). 3 vũ khí không phải của boss được ghim `groundMinReach: 0` để không thừa hưởng qua `inherits` (`p26_behemoth_be_rockets`,
`p26_jotunn_jo_rockets`, `p26_icarus_ic_coil`: giá trị game không đổi). 6 đạn thứ hai của súng boss (`roundOf`, cùng nòng)
thừa hưởng tầm tối thiểu của súng: `autocannon_40_flak` 16, `p26_ixion_125_he` 30, `borer_cannon_he` 20, `boss_heli_gun_flak`
12, `boss_hmg_api` 8, `train_gun_he` 19. Không thêm vũ khí, không đổi máu boss, không đổi AI.

Một vũ khí dùng ở nhiều bệ / nhiều boss có một giá trị: lấy đề xuất **nhỏ nhất** (không bắt bệ thấp chịu vùng chết của bệ cao);
các bệ bị tính thấp hơn hình học ghi ở cột ghi chú. Muốn đúng từng bệ: tách id vũ khí hoặc thêm ghi đè theo boss (chủ dự án
quyết). Vũ khí boss mà đơn vị thường cũng mang **giữ nguyên** (đề xuất trong ngoặc): `boss_flak` (mara_behemoth; 5),
`hover_ciws` (hover_gunboat, sea_corvette, sea_cruiser; 17), `zu23` (zu23_technical; 29), `gunship_rockets` (gunship_heli; 10),
`fighter_cannon` (fighter_jet, stealth_fighter; 21), `gunship_105` / `gunship_40mm` / `gunship_25mm` (sky_gunship; 22 / 22 / 21).

Bị cắt còn 80 % tầm vì hình học vượt tầm (ghi / tầm, m): `p26_bastion_direct_b100` 28/36 (bastion_mk0, fortress_bastion,
monster: hình học 36–53), `p26_ixion_125` 30/38 (68), `p26_kronos_direct_kr57` 22/28 (37), `p26_kronos_close_autocannon_30`
24/30 (38), `p26_moloch_main_mo120` 25/32 (40), `p26_moloch_direct_mo120ap` 25/32 (65), `p26_jotunn_jo203` 48/60 (64),
bệ cao của `p26_leviathan_sec_lev155` (114 → 88, ghi 82), `p26_typhon_sec_ty57` trên hydra (48 → 32, ghi 10) và
`p26_bastion_tiny_autocannon_40` trên monster (30 → 22, ghi 20). Các súng này gần như chỉ còn bắn được ở vòng ngoài của tầm.

### Theo boss và vũ khí (cũ → mới, m; cột trường: trường đã ghi, `-` không đổi)
| boss | vũ khí (bệ) | lớp | cũ | mới | trường | ghi chú |
|---|---|---|---|---|---|---|
| argus | p26_roc_main_roc_bombs (0,1) | bom | 0 | 0 | - |  |
| armored_train | train_gun (0,4) | phao_boss | 0 | 19 | groundMinReach | đề xuất của bệ 19/32 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| armored_train | boss_rockets (1) | be_rocket | 0 | 17 | groundMinReach |  |
| armored_train | boss_hmg (2) | sung_may | 0 | 8 | groundMinReach |  |
| armored_train | boss_flak (3,5) | phao_nho_ciws | 0 | 0 | - | dùng chung với mara_behemoth: giữ nguyên |
| bastion_mk0 | p26_bastion_sec_b240 (0) | ban_cau | 12 | 14 | minRange |  |
| bastion_mk0 | p26_bastion_direct_b100 (1,2) | phao_boss | 0 | 28 | groundMinReach | hình học 36/36 >= tầm 36: cắt 80 % |
| behemoth | p26_behemoth_main_be152 (0) | phao_boss | 0 | 21 | groundMinReach | đề xuất của bệ 36 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| behemoth | p26_behemoth_tiny_be120 (1) | phao_boss | 0 | 21 | groundMinReach |  |
| behemoth | p26_behemoth_close_boss_flak (2,3) | phao_nho_ciws | 0 | 13 | groundMinReach | đề xuất của bệ 20 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| behemoth | p26_behemoth_tiny_boss_missiles (4,5) | ten_lua | 0 | 1 | groundMinReach |  |
| behemoth | p26_behemoth_tiny_kornet_twin (6) | phao_boss | 0 | 21 | groundMinReach |  |
| behemoth | p26_behemoth_direct_be120 (7,8) | phao_boss | 0 | 21 | groundMinReach | đề xuất của bệ 24 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| behemoth | p26_behemoth_sec_be_rockets (9) | be_rocket | 0 | 15 | groundMinReach | đề xuất của bệ 23 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| behemoth_inferno | boss_flamer (0,2) | phun_lua | 0 | 18 | groundMinReach |  |
| behemoth_inferno | boss_thermo (1) | phao_boss | 0 | 21 | groundMinReach |  |
| behemoth_mk0 | p26_behemoth_main_be152 (0) | phao_boss | 0 | 21 | groundMinReach | đề xuất của bệ 36 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| behemoth_mk0 | p26_behemoth_direct_be120 (1,2) | phao_boss | 0 | 21 | groundMinReach | đề xuất của bệ 21/24 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| behemoth_mk0 | p26_behemoth_sec_be_rockets (3) | be_rocket | 0 | 15 | groundMinReach | đề xuất của bệ 23 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| behemoth_mk2 | p26_behemoth_main_be152 (0) | phao_boss | 0 | 21 | groundMinReach | đề xuất của bệ 36 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| behemoth_mk2 | p26_behemoth_close_boss_flak (1,2) | phao_nho_ciws | 0 | 13 | groundMinReach | đề xuất của bệ 20 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| behemoth_tempest | boss_railgun (0) | phao_boss | 0 | 39 | groundMinReach |  |
| behemoth_tempest | coilgun (1,2) | phao_boss | 0 | 21 | groundMinReach |  |
| caspian | hover_ciws (0) | phao_nho_ciws | 0 | 0 | - | dùng chung với hover_gunboat, sea_corvette, sea_cruiser: giữ nguyên |
| caspian | zu23 (1,2) | phao_nho_ciws | 0 | 0 | - | dùng chung với zu23_technical: giữ nguyên |
| cerberus | p26_behemoth_main_be152 (0) | phao_boss | 0 | 21 | groundMinReach |  |
| cerberus | p26_behemoth_close_boss_flak (1,2) | phao_nho_ciws | 0 | 13 | groundMinReach |  |
| cerberus | p26_behemoth_sec_be_rockets (3) | be_rocket | 0 | 15 | groundMinReach |  |
| command_airship | p26_roc_main_roc_bombs (0,1) | bom | 0 | 0 | - |  |
| command_airship | p26_roc_direct_roc_atgm (2,3) | ten_lua | 0 | 1 | groundMinReach |  |
| command_airship | p26_roc_close_twin_30_bmpt (4,5) | phao_nho_ciws | 0 | 15 | groundMinReach |  |
| command_airship | p26_roc_roc105 (6,7) | phao_boss | 0 | 17 | groundMinReach | đề xuất của bệ 18 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| daedalus | p26_daedalus_direct_dae_laser (0,3) | phao_boss | 0 | 12 | groundMinReach |  |
| daedalus | p26_daedalus_sec_dae57 (1,2) | sung_phu | 0 | 12 | groundMinReach |  |
| drone_mothership | p26_matriarch_tiny_mothership_cannon (0,4) | phao_boss | 0 | 11 | groundMinReach | đề xuất của bệ 11/13 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| drone_mothership | p26_matriarch_ma_drones (1) | drone | 0 | 1 | groundMinReach |  |
| drone_mothership | p26_matriarch_close_boss_flak (2,3) | phao_nho_ciws | 0 | 14 | groundMinReach | đề xuất của bệ 17 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| drone_mothership | p26_matriarch_direct_ma_atgm (5,8) | ten_lua | 0 | 1 | groundMinReach |  |
| drone_mothership | p26_matriarch_sec_autocannon_30 (6,7) | phao_nho_ciws | 0 | 12 | groundMinReach |  |
| earth_borer | borer_drill (0) | can_chien | 0 | 0 | - |  |
| earth_borer | borer_cannon (1,2) | sung_phu | 0 | 20 | groundMinReach |  |
| fenrir | p26_jotunn_sec_jo_rockets (0,1) | be_rocket | 0 | 23 | groundMinReach | đề xuất của bệ 23/34 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| fenrir | p26_jotunn_close_boss_flak (2) | phao_nho_ciws | 0 | 18 | groundMinReach |  |
| fortress_bastion | p26_bastion_sec_b240 (0) | ban_cau | 12 | 14 | minRange |  |
| fortress_bastion | p26_bastion_direct_b100 (1,2) | phao_boss | 0 | 28 | groundMinReach | hình học 36/36 >= tầm 36: cắt 80 % |
| fortress_bastion | p26_bastion_tiny_autocannon_40 (3,4) | phao_nho_ciws | 0 | 20 | groundMinReach |  |
| fortress_bastion | p26_bastion_tiny_kornet_twin (5) | ten_lua | 0 | 1 | groundMinReach |  |
| fortress_bastion | p26_bastion_close_boss_hmg (6,7) | sung_may | 0 | 18 | groundMinReach |  |
| fortress_bastion | p26_bastion_main_b155 (8) | ban_cau | 20 | 20 | - |  |
| fortress_bastion | p26_bastion_tiny_zu23 (9,10) | phao_nho_ciws | 0 | 23 | groundMinReach |  |
| fortress_hive | mothership_drones (0,1) | drone | 0 | 1 | groundMinReach |  |
| fortress_hive | boss_flak (2,3) | phao_nho_ciws | 0 | 0 | - | dùng chung với mara_behemoth: giữ nguyên |
| garuda | p26_roc_main_roc_bombs (0,1) | bom | 0 | 0 | - |  |
| garuda | p26_roc_direct_roc_atgm (2,3) | ten_lua | 0 | 1 | groundMinReach |  |
| garuda | p26_roc_close_twin_30_bmpt (4,5) | phao_nho_ciws | 0 | 15 | groundMinReach | đề xuất của bệ 17 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| garuda | p26_roc_roc105 (6,7) | phao_boss | 0 | 17 | groundMinReach |  |
| hydra | p26_typhon_sec_ty57 (0,1) | phao_ham | 0 | 10 | groundMinReach | đề xuất của bệ 10/32 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất); hình học 48 >= tầm 40: cắt 80 % |
| hydra | p26_typhon_direct_ty100 (2) | sung_phu | 0 | 10 | groundMinReach |  |
| hyperion | p26_icarus_sec_orbital_laser (0) | phao_boss | 0 | 11 | groundMinReach | đề xuất của bệ 14 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| hyperion | p26_icarus_main_ic_coil (1,2) | phao_boss | 0 | 13 | groundMinReach | đề xuất của bệ 21 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| hyperion | p26_icarus_direct_ic_laser (3,4) | phao_boss | 0 | 14 | groundMinReach | đề xuất của bệ 18 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| icarus_mk0 | p26_icarus_sec_orbital_laser (0) | phao_boss | 0 | 11 | groundMinReach |  |
| ixion | p26_ixion_125 (0) | phao_boss | 0 | 30 | groundMinReach | hình học 68 >= tầm 38: cắt 80 % |
| ixion | p26_ixion_mg (1,2) | sung_may | 0 | 26 | groundMinReach |  |
| kraken | p26_leviathan_lev406 (0,1,2) | phao_ham | 0 | 65 | groundMinReach | đề xuất của bệ 97 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| kraken | p26_leviathan_sec_lev155 (3,4) | phao_ham | 0 | 82 | groundMinReach | đề xuất của bệ 84 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| kraken | p26_leviathan_direct_lev127 (5,6) | sung_phu | 0 | 13 | groundMinReach | đề xuất của bệ 35 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| kraken | aa_25_triple (7,8,9,10,11,12,13,14) | phong_khong | 0 | 0 | - | chỉ bắn máy bay |
| kraken | sam_post (15) | phong_khong | 0 | 0 | - | chỉ bắn máy bay |
| kronos | p26_kronos_close_autocannon_30 (0,4) | phao_nho_ciws | 0 | 24 | groundMinReach | hình học 38/37 >= tầm 30: cắt 80 % |
| kronos | p26_kronos_direct_kr57 (1,2) | sung_phu | 0 | 22 | groundMinReach | hình học 37/37 >= tầm 28: cắt 80 % |
| kronos | bucket_wheel (3) | can_chien | 0 | 0 | - |  |
| kronos | p26_kronos_close_boss_rockets (5) | be_rocket | 0 | 30 | groundMinReach |  |
| landing_hovercraft | hover_ciws (0,1) | phao_nho_ciws | 0 | 0 | - | dùng chung với hover_gunboat, sea_corvette, sea_cruiser: giữ nguyên |
| landing_hovercraft | ciws_aa (2) | phong_khong | 0 | 0 | - | chỉ bắn máy bay |
| landing_hovercraft | hover_rockets (3,4) | ban_cau | 12 | 12 | - |  |
| leviathan | p26_leviathan_lev406 (0,1,2) | phao_ham | 0 | 65 | groundMinReach | đề xuất của bệ 65/72/92 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| leviathan | p26_leviathan_sec_lev155 (3,4) | phao_ham | 0 | 82 | groundMinReach | đề xuất của bệ 82/88 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất); hình học 114 >= tầm 110: cắt 80 % |
| leviathan | p26_leviathan_direct_lev127 (5,6) | sung_phu | 0 | 13 | groundMinReach | đề xuất của bệ 24/35 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| leviathan | aa_25_triple (7,8,9,10,11,12,13,14) | phong_khong | 0 | 0 | - | chỉ bắn máy bay |
| leviathan | sam_post (15) | phong_khong | 0 | 0 | - | chỉ bắn máy bay |
| locust | p26_matriarch_ma_drones (0) | drone | 0 | 1 | groundMinReach |  |
| locust | p26_matriarch_close_boss_flak (1) | phao_nho_ciws | 0 | 14 | groundMinReach | đề xuất của bệ 17 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| mega_gunship | gunship_rockets (0,4) | be_rocket | 0 | 0 | - | dùng chung với gunship_heli: giữ nguyên |
| mega_gunship | boss_heli_gun (1,2) | phao_nho_ciws | 0 | 12 | groundMinReach |  |
| mega_gunship | boss_minigun (3) | sung_may | 0 | 12 | groundMinReach |  |
| mega_gunship | boss_hmg (5,6) | sung_may | 0 | 8 | groundMinReach | đề xuất của bệ 12 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| mobile_fortress | p26_jotunn_jo203 (0,7) | phao_boss | 0 | 48 | groundMinReach | hình học 61/64 >= tầm 60: cắt 80 % |
| mobile_fortress | p26_jotunn_sec_jo_rockets (1,2) | be_rocket | 0 | 23 | groundMinReach |  |
| mobile_fortress | p26_jotunn_close_boss_flak (3,4) | phao_nho_ciws | 0 | 18 | groundMinReach |  |
| mobile_fortress | p26_jotunn_direct_jo125 (5) | phao_boss | 0 | 31 | groundMinReach |  |
| mobile_fortress | p26_jotunn_tiny_twin_30_flak (6) | phao_nho_ciws | 0 | 18 | groundMinReach |  |
| mobile_fortress | sam_post (8) | phong_khong | 0 | 0 | - | chỉ bắn máy bay |
| moloch | p26_moloch_main_mo120 (0,3) | phao_boss | 0 | 25 | groundMinReach | hình học 40/40 >= tầm 32: cắt 80 % |
| moloch | p26_moloch_tiny_zu23 (1,2) | phao_nho_ciws | 0 | 35 | groundMinReach |  |
| moloch | p26_moloch_direct_mo120ap (4,5) | phao_boss | 0 | 25 | groundMinReach | hình học 65/65 >= tầm 32: cắt 80 % |
| moloch | p26_moloch_close_boss_flak (6) | phao_nho_ciws | 0 | 35 | groundMinReach |  |
| monster | p26_bastion_sec_b240 (0) | ban_cau | 12 | 14 | minRange |  |
| monster | p26_bastion_direct_b100 (1,2) | phao_boss | 0 | 28 | groundMinReach | hình học 53/53 >= tầm 36: cắt 80 % |
| monster | p26_bastion_tiny_autocannon_40 (3,4) | phao_nho_ciws | 0 | 20 | groundMinReach | đề xuất của bệ 22 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất); hình học 30/30 >= tầm 28: cắt 80 % |
| monster | p26_bastion_tiny_kornet_twin (5) | ten_lua | 0 | 1 | groundMinReach |  |
| monster | p26_bastion_close_boss_hmg (6,7) | sung_may | 0 | 18 | groundMinReach | đề xuất của bệ 20 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| monster | p26_bastion_main_b155 (8) | ban_cau | 20 | 20 | - |  |
| monster | p26_bastion_tiny_zu23 (9,10) | phao_nho_ciws | 0 | 23 | groundMinReach | đề xuất của bệ 26 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| morrigan | air_to_air (0,1) | phong_khong | 0 | 0 | - | chỉ bắn máy bay |
| morrigan | guided_bomb (2) | bom | 0 | 0 | - |  |
| morrigan | fighter_cannon (3) | phao_nho_ciws | 0 | 0 | - | dùng chung với fighter_jet, stealth_fighter: giữ nguyên |
| nuke_train | p26_nemesis_main_ne152 (0) | phao_boss | 0 | 33 | groundMinReach |  |
| nuke_train | p26_nemesis_close_boss_flak (1,2,6) | phao_nho_ciws | 0 | 9 | groundMinReach | đề xuất của bệ 9/13 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| nuke_train | p26_nemesis_sec_boss_rockets (3) | be_rocket | 0 | 15 | groundMinReach |  |
| nuke_train | sam_battery (4) | phong_khong | 20 | 20 | - | chỉ bắn máy bay |
| nuke_train | p26_nemesis_direct_ne125 (5) | phao_boss | 0 | 19 | groundMinReach |  |
| nyx | boss_railgun (0) | phao_ham | 0 | 39 | groundMinReach | đề xuất của bệ 42 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| nyx | p26_leviathan_direct_lev127 (1,2) | sung_phu | 0 | 13 | groundMinReach | đề xuất của bệ 13/25 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| rail_supergun | supergun_800 (0) | ban_cau | 30 | 69 | minRange |  |
| rail_supergun | autocannon_40 (1,2) | phao_nho_ciws | 0 | 16 | groundMinReach |  |
| rail_supergun | ciws_aa (3,4) | phong_khong | 0 | 0 | - | chỉ bắn máy bay |
| scylla | naval_130_twin (0) | phao_ham | 0 | 72 | groundMinReach |  |
| scylla | p26_leviathan_direct_lev127 (1) | sung_phu | 0 | 13 | groundMinReach | đề xuất của bệ 35 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| silver_bug | p26_icarus_sec_orbital_laser (0) | phao_boss | 0 | 11 | groundMinReach |  |
| silver_bug | p26_icarus_main_ic_coil (1,2) | phao_boss | 0 | 13 | groundMinReach |  |
| silver_bug | p26_icarus_direct_ic_laser (3,4) | phao_boss | 0 | 14 | groundMinReach |  |
| silver_bug | p26_icarus_close_autocannon_40 (5,6) | phao_nho_ciws | 0 | 13 | groundMinReach |  |
| sky_fortress | gunship_105 (0) | phao_boss | 0 | 0 | - | dùng chung với sky_gunship: giữ nguyên |
| sky_fortress | gunship_40mm (1) | phao_nho_ciws | 0 | 0 | - | dùng chung với sky_gunship: giữ nguyên |
| sky_fortress | gunship_25mm (2) | phao_nho_ciws | 0 | 0 | - | dùng chung với sky_gunship: giữ nguyên |
| sky_fortress | griffin (3) | ten_lua | 0 | 1 | groundMinReach |  |
| stymphalos | p26_matriarch_ma_drones (0) | drone | 0 | 1 | groundMinReach |  |
| stymphalos | p26_matriarch_close_boss_flak (1) | phao_nho_ciws | 0 | 14 | groundMinReach |  |
| stymphalos | p26_matriarch_direct_ma_atgm (2) | ten_lua | 0 | 1 | groundMinReach |  |
| supreme_command | boss_hmg (0,1) | sung_may | 0 | 8 | groundMinReach | đề xuất của bệ 15 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| typhon | sam_post (0) | phong_khong | 0 | 0 | - | chỉ bắn máy bay |
| typhon | p26_typhon_sec_ty57 (1,2) | sung_phu | 0 | 10 | groundMinReach | đề xuất của bệ 17 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |
| typhon | p26_typhon_direct_ty100 (3) | sung_phu | 0 | 10 | groundMinReach | đề xuất của bệ 17 (vũ khí dùng ở bệ thấp hơn: lấy nhỏ nhất) |

### Boss có vùng chết chưa được phủ (`co_che_vung_chet = false`) — chủ dự án quyết thêm vũ khí phụ hay đổi bệ

| boss | vùng chết (m, từ tâm) | dải chết (m) | phủ | vũ khí gần nhất (tầm tối thiểu) |
|---|---|---|---|---|
| ixion | 30 | 19 | 21 % | p26_ixion_mg (26) |
| fenrir | 23 | 15,5 | 32 % | p26_jotunn_close_boss_flak (18) |
| mobile_fortress | 23 | 15,5 | 32 % | p26_jotunn_close_boss_flak (18), p26_jotunn_tiny_twin_30_flak |
| behemoth_inferno | 21 | 14,6 | 21 % | boss_flamer (18) |
| behemoth_mk2 | 21 | 14,6 | 55 % | p26_behemoth_close_boss_flak (13) |
| behemoth_tempest | 21 | 14,6 | 0 % | boss_railgun (39); coilgun đặt vùng chết |
| moloch | 25 | 14 | 0 % | p26_moloch_tiny_zu23 (35) |
| daedalus (bay) | 12 | 12 | 0 % | không có (mọi vũ khí cùng 12) |
| nuke_train | 15 | 11,2 | 54 % | p26_nemesis_close_boss_flak (9) |
| hyperion (bay) | 11 | 11 | 0 % | p26_icarus_main_ic_coil (13) |
| icarus_mk0 (bay) | 11 | 11 | 0 % | không có (một vũ khí) |
| silver_bug (bay) | 11 | 11 | 0 % | p26_icarus_close_autocannon_40 (13) |
| behemoth_mk0 | 15 | 8,6 | 0 % | p26_behemoth_main_be152 (21) |
| cerberus | 15 | 8,6 | 23 % | p26_behemoth_close_boss_flak (13) |
| kronos | 22 | 8 | 0 % | p26_kronos_close_autocannon_30 (24); bucket_wheel chỉ 6 m |
| bastion_mk0 | 14 | 6,5 | 0 % | p26_bastion_direct_b100 (28) |
| supreme_command | 8 | 3,5 | 0 % | không có (chỉ boss_hmg) |

### Xem lại thời gian hạ (dải chết ≥ 8 m; không đổi máu)

Công thức máu = P × t × 0,6 giả định đòn đánh gần cũng bị bắn; nay xe áp sát vào dải chết chỉ chịu vũ khí phủ nên thời gian hạ
mục tiêu của boss tăng: **xem lại thời gian hạ** cho rail_supergun (dải 55 m), ixion (19), command_airship và garuda (17, bay),
fenrir và mobile_fortress (15,5), behemoth_inferno, behemoth_mk2, behemoth_tempest (14,6), earth_borer, moloch (14),
armored_train (13,4), daedalus (12), nuke_train (11,2), drone_mothership, hyperion, icarus_mk0, silver_bug (11), behemoth,
behemoth_mk0, cerberus (8,6), kronos (8).

### Hệ quả cân bằng

- Áp sát boss để né pháo chính thì chịu: súng máy / cao xạ / CIWS đặt thấp (armored_train: boss_hmg + boss_flak phủ 100 %;
  behemoth: cao xạ + ATGM; rail_supergun: Bofors 40 mm phủ 96 %), mũi khoan (earth_borer: phủ 100 %), Kornet đôi
  (fortress_bastion, monster), bom / ATGM / 30 mm của khí cầu chỉ huy (command_airship, garuda), ATGM và drone (drone_mothership).
  Boss mà vũ khí dùng chung với đơn vị thường được giữ 0 (sky_fortress, mega_gunship, caspian, fortress_hive) không có vùng chết.
- Dễ bị áp sát nhất (dải chết lớn, phủ yếu): ixion (19 m, chỉ súng máy đặt cao phủ 21 %), moloch và behemoth_tempest (14 m,
  không gì phủ), fenrir / mobile_fortress (15,5 m, cao xạ 32 %), behemoth_inferno (phun lửa chỉ phủ 21 %), và các tàu vũ trụ
  bay thấp (daedalus, hyperion, icarus_mk0, silver_bug: 11–12 m ngay dưới bụng, không gì phủ).
- Tàu: pháo chính 406 mm không bắn được mặt đất trong 65 m, 155 mm trong 82 m; vùng chết của tàu do pháo phụ 127 mm đặt (13 m,
  lấy theo bệ thấp của nyx / scylla; bệ của leviathan / kraken cho 24–35 m). Cao xạ của tàu chỉ bắn máy bay.
- Pháo phòng thủ gần đặt cao cũng có vùng chết theo công thức (không ép về 0): moloch zu23 35 m, caspian zu23 29 m (giữ 0 vì dùng
  chung), behemoth cao xạ 20 m (ghi 13 theo bệ thấp của cerberus).
- Trận phát lại bị ảnh hưởng: mọi trận có boss — baseline của ReplayHashTests cần ghi lại; CatalogCheck cần chạy với khóa mới
  `groundMinReach` (chủ dự án chạy khi muốn: Unity Test Runner, EditMode, lọc `ReplayHashTests` và `CatalogCheck`).
