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

## Play-test 14 lane C (cloud session 1): xóa đơn vị, hỗ trợ, công trình

Danh sách id đã xóa và thay thế: `Docs/fixes/playtest14_deleted.md`. Không đổi chỉ số của đơn vị còn lại; các giá trị dưới đây
đổi vì các thẻ bị xóa.

| # | mục | cũ | mới | lý do |
|---|---|---|---|---|
| PT14-1 | `Progression.StarterSupports` (thẻ hỗ trợ khởi đầu) | artillery_barrage, smoke_screen | artillery_barrage, **repair_drop** | smoke_screen bị xóa; người chơi mới vẫn có 2 thẻ hỗ trợ |
| PT14-2 | Mở khóa chiến dịch | c1m03 mở repair_drop; nhiều nhiệm vụ mở thẻ bị xóa | c1m03 không mở gì (repair_drop là thẻ khởi đầu); thẻ bị xóa bỏ khỏi danh sách mở khóa | thẻ bị xóa |
| PT14-3 | Luật kiểm chiến dịch (`build_campaign.py`): số thẻ mỗi chương mở | 3-10 | **2-10** (chương 10 còn 2) | thẻ bị xóa |
| PT14-4 | Kinh tế chiến dịch (generator tự tính lại) | blueprint scale 0,50; deck rank 7,00 đầu hồi IV, 7,21 cuối; hồi I-II trả x3,00 | blueprint scale **0,75**; deck rank **7,21** đầu hồi IV, **8,00** cuối; hồi I-II trả **x1,62** | ít thẻ hơn trên đường mở khóa |
| PT14-5 | Bộ bài cố định (fixed decks, 8 xe + 2 hỗ trợ) | thẻ bị xóa | thay bằng thẻ cùng vai trò chưa có trong bộ (log của `Tools/campaign/fixed_decks.py`, thẻ mượn tính lại theo kiểm tra) | thẻ bị xóa |
| PT14-6 | Deck/roster/đợt sóng địch trong chiến dịch, sự kiện (`EventDefs`, `events.py`, tướng) | bmpt, gunship_heli, lancet_truck, ... | ifv, attack_helicopter, fpv_carrier, ... (bỏ khi trùng) | thay thế theo kế hoạch |
| PT14-7 | `openingSquads.roles` | có thẻ bị xóa; vai "radar_scout" | bỏ thẻ bị xóa; vai "bunker" = siege_tank; vai "radar_scout" bỏ (Kerr, Orlov mất ô đó) | thẻ bị xóa |
| PT14-8 | `base.roster` (thẻ tháp) | 22 | **14** | công trình bị xóa |
| PT14-9 | `base.reference` (căn cứ chuẩn tính sức mạnh sóng Phòng thủ/Vô tận) | ô của tháp bị xóa | cùng số ô, tháp còn lại cùng cỡ (mg_bunker, guard_tower, rocket_turret; tiện ích logistics_station, airfield) | giữ sức mạnh chuẩn gần như cũ |
| PT14-10 | `base.ai.styles` (trọng số tháp AI) | có tháp bị xóa | bỏ các khóa đó (Kessler còn "*": 1,0) | công trình bị xóa |
| PT14-11 | Hộ tống boss (`escorts`, `escortTemplates`) | smoke_carrier, counter_battery_radar, lancet_truck, bmpt | ew_jammer, command_vehicle, fpv_carrier, ifv | thay thế |
| PT14-12 | Lính gác Gungnir (`guards`) | dragons_teeth x3 | blast_wall x3 | thay thế |
| PT14-13 | Bản đồ siege coralisles, swamp (và `build_maps.py`) | artillery_emplacement x2 | rocket_turret x2 | thay thế |
| PT14-14 | `PlayerProfile.DefaultLarge` (ô lớn mặc định) | heavy_turret, artillery_emplacement | heavy_turret, **missile_battery** | thay thế |
| PT14-15 | IFV `skills` | ["apc_smoke"] | [] | chủ dự án bỏ apc_smoke |
| PT14-16 | Giá tháp `p32_tower_prices.py`: mốc "protect" | troop_shelter = 5 | shield_tower = 9 (giá tạm của nó) | troop_shelter bị xóa; chỉ là công cụ, không ghi dữ liệu |
| PT14-17 | Save cũ (roster version 9) | - | hoàn tiền thẻ đã mua (`CardMerges.DeletedPt14`), xu + bản vẽ của cấp thẻ, 500 xu mỗi vật phẩm gunship | yêu cầu "file lưu cũ được hoàn lại" |

## Play-test 14 lane B (cloud session 1): UI and base systems

| # | mục | cũ | mới | lý do |
|---|---|---|---|---|
| PT14-B1 | repair_bay | sửa 1,5 %/s xe trong căn cứ | hào quang: mọi xe mặt đất +10 % sát thương, +10 % máu tối đa | kế hoạch PT14 |
| PT14-B2 | airfield | bãi đáp: sửa 3 %/s, nạp đạn; nhánh hangar/service | hào quang: mọi máy bay (không tính drone) +10 % sát thương, +10 % tốc độ; nạp đạn ở HQ; bỏ 2 nhánh | kế hoạch PT14 |
| PT14-B3 | fire_control_centre → Defence Command Centre | tháp trong 30 m +12 % sát thương, dồn mục tiêu | mọi công trình +15 % tầm, +10 % máu | kế hoạch PT14 |
| PT14-B4 | laser_ad_station | nhánh .laser / .net | chỉ .laser; tên Laser Defence Tower | kế hoạch PT14 |
| PT14-B5 | vehicle_hangar, aircraft_hangar (mới) | - | Medium, máu 1800, giáp 2, rebuildCp 8; 1 quân/60 s, tối đa 2 còn sống; mở ở c3m04 / c7m02; AI style mặc định 0,5 / 0,3 | kế hoạch PT14 |
| PT14-B6 | base.roster | 14 | 16 | thêm 2 hangar |
| PT14-B7 | reinforcements | thả 2 MBT + 1 IFV, chỉ tốn vật phẩm | người chơi chọn quân ≤ 20 CP gốc; gọi tốn ceil(1,5 × tổng) CP (và vật phẩm) | chủ dự án 03/10 |
| PT14-B8 | Garrison HQ | đội hỗn hợp theo cấp | tùy chọn: đội là đơn vị người chơi chọn (số lượng = số xe của đội cấp đó) | kế hoạch PT14 |
| PT14-B9 | Giá tháp p32_tower_prices | - | bỏ laser_ad_station.net | biến thể bị xóa |

## PT14 lead (03/10): opening squads after the radar_scout role was emptied
| What | Before | After | Why |
|---|---|---|---|
| commanders.kerr opening roles | scout, light (radar_scout emptied) | scout, scout, light | keeps 3 squads; recon role -> scout jeep |
| generals.orlov opening roles | artillery (radar_scout emptied) | artillery, scout | keeps 2 squads; spotter for the guns |
## Play-test 14 lane A (cloud session 2): gameplay + VFX

Nhánh `cloud/pt14-a`. Lý do ngoài đời: `Docs/DECISIONS.md` "Play-test 14 (lane A, cloud)". Sát thương không đổi.

| # | mục | cũ | mới | lý do |
|---|---|---|---|---|
| PT14-A1 | `armored_car` súng máy đồng trục | `mg_coax` (tầm 20 m) | `mg_coax_long` (kế thừa mg_coax, tầm **30 m**) | pháo 25 mm tầm 30 m: hai súng cùng bắn mục tiêu tháp pháo đang ngắm |
| PT14-A2 | `erectSeconds` (mới) — xe phóng chỉ bắn khi bệ đã dựng | bắn ngay khi có mục tiêu (bệ bật lên tức thì) | phát đầu chờ bệ dựng: mlrs 1,1 s, elite_mlrs 1,1, elite_grad 1,0, heavy_rocket_artillery 1,3, thermobaric_launcher 1,2, rocket_technical 0,7, sam_launcher 0,9, long_sam 1,6, elite_long_sam 1,6, ballistic_launcher 2,2, ground_cruise_missile_vehicle 2,2, missile_battery 1,2, shahed_truck 1,0, lancet_truck 0,8 (giữ dựng 1,2 s sau phát cuối) | bệ phóng nâng với tốc độ thường |
| PT14-A3 | Hộ tống boss (`escortRules.domains`) | bảng hộ tống có thể đưa xe tăng cho boss biển/trên không | xe khác miền đổi theo vai của nó: mặt đất main_battle_tank / light_tank / aa_vehicle / armored_car / engineer_vehicle / ew_jammer; trên không attack_helicopter / fighter_jet / scout_heli; biển missile_boat / hover_gunboat / sea_corvette / river_patrol_boat / river_gunboat | boss nào hộ tống miền đó |
| PT14-A4 | Tàu bọc thép, Nemesis (boss ray) | thân xoay về mục tiêu / hướng hỏa lực khi đứng | thân luôn theo ray, chỉ tháp pháo xoay | xe chạy trên ray |
| PT14-A5 | Leviathan loạt pháo chính | bắn ngay lúc chọn điểm ngắm (tháp nhảy tới hướng) | tháp xoay theo `turretTurnRate` (36°/s, tối thiểu 20°/s) rồi mới bắn khi lệch ≤ 2° (tối đa chờ 10 s); giữa hai loạt bám mục tiêu hiện tại | ngắm xong mới bắn; chu kỳ 60 s giữ nguyên, phát bắn trễ vài giây |
| PT14-A6 | `light_tank` tên lửa bắn qua nòng | có thể bắn cùng lúc với đạn pháo | nòng bận 1 s sau mỗi phát (tên lửa hoặc đạn), hai loại không ra cùng lúc | một nòng nạp một loại đạn |
| PT14-A7 | `boss_howitzer` cờ `"lobs": true` (kế thừa: p26_jotunn_jo203, boss_howitzer_guided) | vẽ như đạn xe tăng | vẽ như pháo binh (đường cầu vồng, lửa đầu nòng, nổ pháo) — chỉ hình ảnh, Sim không đọc | khôi phục hình pháo của boss |
| PT14-A8 | Âm thanh súng sky_gunship (bay vòng, cánh cố định) | như súng mặt đất cùng cỡ | to x1,5, vang xa thêm 20 m, phát đơn dùng bank cỡ lớn hơn một bậc (105 mm nghe như 155 mm) | chủ dự án: tiếng bắn phải mạnh |
| PT14-A9 | Động cơ rocket pháo binh / tên lửa đạn đạo (hình) | tắt ở 85 % / 75 % đường bay | cháy tới lúc nổ; khói kéo tới điểm nổ | vệt khói tới lúc nổ |

Trận replay bị ảnh hưởng: PT14-A1, A2, A3, A4, A5, A6 đổi Sim — baseline của ReplayHashTests cần ghi lại.

## Play-test 14 lane D (cloud session 3)

Nhánh `cloud/pt14-d`. Lý do: `Docs/DECISIONS.md` "Play-test 14 (lane D, cloud)".

| # | mục | cũ | mới | lý do |
|---|---|---|---|---|
| PT14-D1 | `reinforcements` (Tiếp viện thả dù) | vật phẩm mua bằng xu (900 xu / 2 cái), không tốn CP | thẻ hỗ trợ hỏa lực thường: thẻ 0 CP + giá gọi ceil(1,5 x CP quân chọn, tối đa 20 CP); hồi 30 s như cũ; lệnh gọi không kèm quân (AI) thả `units` vừa giới hạn | lead/chủ dự án: không còn là vật phẩm xu |
| PT14-D2 | Mở khóa `reinforcements` | cửa hàng vật phẩm | chiến dịch chương 4 (c4m08, `act11.ORPHANS`); mua sớm theo giá thẻ hỗ trợ | thẻ thường cần đường mở khóa |
| PT14-D3 | Save cũ (roster version 10) | - | mỗi vật phẩm `reinforcements` còn trong túi hoàn 450 xu (`CardMerges.CallItemPricePt14`) | hoàn tiền vật phẩm |
| PT14-D4 | Kinh tế chiến dịch (generator tính lại) | hồi I-II trả x1,64 | x1,66 | thêm một thẻ trên đường mở khóa |
| PT14-D5 | Locust (biến thể drone_mothership) vũ khí drone | dùng chung `p26_matriarch_ma_drones`: loạt 6 drone cách 0,2 s, hồi 4 s (~6 drone / 5 s) | vũ khí riêng `locust_drones`: 1 drone, hồi 2 s (1 drone / 2 s); sát thương mỗi drone giữ nguyên; Matriarch không đổi | chủ dự án: Locust 1 drone mỗi 2 s |
| PT14-D6 | Xóa 10 boss (Stymphalos, Hive, Cerberus, Atlas, Kronos, Caspian, Morrigan, Spectre, Garuda, Gungnir) và các mục chỉ chúng dùng | 41 boss (16 chính, 25 mini) | 31 boss (14 chính, 17 mini); danh sách: `Docs/fixes/playtest14_deleted.md` | chủ dự án bỏ 10 boss |
| PT14-D7 | Boss thay thế trong chiến dịch (máu nhân, bỏ chạy) | c5m05 Hive x1,1; c7m10 Atlas x0,8 chạy 50 %; c8m10 Kronos x1; c9m05 Caspian x1; i3m02 Morrigan x1 chạy 50 %; c10m08 Spectre x3,5; c10m12 Morrigan x1 chạy 50 %; c11m05 Gungnir x1 | c5m05 Matriarch x0,9 chạy 50 %; c7m10 Behemoth Mk.II x0,95 chạy 50 %; c8m10 Tartarus x2,6; c9m05 Charybdis x1,5; i3m02 Harpy x2,9 chạy 50 %; c10m08 Roc x2,7 chạy 50 %; c10m12 Harpy x2,9 chạy 50 %; c11m05 Monster x1,5 | giữ tổng sát thương cần gây ra gần như cũ (máu gốc boss mới x hệ số x phần phải đánh) |
| PT14-D8 | Ô boss các chương | ch.5 mini Locust, Hive; ch.7 Atlas, ...; ch.8 chính Kronos, mini Ixion, Tartarus; ch.9 Caspian, Scylla; ch.10 Spectre, Icarus Mk.0, Argus, Morrigan; ch.11 Gungnir, Locust; III Morrigan | ch.5 Locust; ch.7 Behemoth Mk.II, ...; ch.8 chính Tartarus, mini Ixion; ch.9 Charybdis, Scylla; ch.10 Icarus Mk.0, Argus, Harpy; ch.11 Monster, Locust; III Harpy | thay thế theo truyện |
| PT14-D9 | `mega_gunship` (Harpy) `duel` | không | `"duel": { "escorts": false }` (chỉ trong nhiệm vụ đấu tay đôi c10m12: không hộ tống, không tàng hình) | Raven đấu Hawk bằng Harpy |
| PT14-D10 | Sự kiện mini-boss xen kẽ III | `morrigan_hunt` (Morrigan) | `harpy_hunt` (Harpy); mini của Quaden: Harpy | Morrigan bị xóa |
| PT14-D11 | Tuyến cố định bản đồ openpit | `routes.kronos` | `routes.haul` (cùng tọa độ) | Kronos bị xóa; đường vận chuyển giữ nguyên |

## Play-test 14 session 5 (lane E, local): hangar theo ngân sách, hộp ATGM bên hông

Nhánh `feature/pt14-e`. Lý do: `Docs/DECISIONS.md` "Play-test 14 session 5 (local lane A)". Sát thương không đổi.

| # | mục | cũ | mới | lý do |
|---|---|---|---|---|
| PT14-E1 | `vehicle_hangar` `hangar.budget` (mới) | 2 xe còn sống mỗi hangar, loại nào cũng vậy | còn sống = floor(5 / CP của xe chọn): scout_jeep (2 CP) **2**, armored_car (3) **1**, light_tank (3) **1** | chủ dự án: "chọn light tank thì được 1, jeep thì được 2" |
| PT14-E2 | `aircraft_hangar` `hangar.budget` (mới) | 2 | floor(12 / CP): scout_heli (6) **2**, recon_drone (7) **1** | cùng quy tắc |
| PT14-E3 | `ifv`, `elite_apc` `sideErectSeconds` (mới) 0,6 | tên lửa ATGM bắn ngay khi có mục tiêu (hộp bên hông bật lên tức thì) | tên lửa chờ hộp dựng 0,6 s sau khi có mục tiêu (cùng luật `erectSeconds` của xe phóng); hộp nâng theo nhịp đó | hộp phóng nâng lên rồi mới bắn |

Trận replay bị ảnh hưởng: PT14-E1, E2, E3 đổi Sim — baseline của ReplayHashTests cần ghi lại.
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

## Play-test 14 lane C (cloud session 1): xóa đơn vị, hỗ trợ, công trình

Danh sách id đã xóa và thay thế: `Docs/fixes/playtest14_deleted.md`. Không đổi chỉ số của đơn vị còn lại; các giá trị dưới đây
đổi vì các thẻ bị xóa.

| # | mục | cũ | mới | lý do |
|---|---|---|---|---|
| PT14-1 | `Progression.StarterSupports` (thẻ hỗ trợ khởi đầu) | artillery_barrage, smoke_screen | artillery_barrage, **repair_drop** | smoke_screen bị xóa; người chơi mới vẫn có 2 thẻ hỗ trợ |
| PT14-2 | Mở khóa chiến dịch | c1m03 mở repair_drop; nhiều nhiệm vụ mở thẻ bị xóa | c1m03 không mở gì (repair_drop là thẻ khởi đầu); thẻ bị xóa bỏ khỏi danh sách mở khóa | thẻ bị xóa |
| PT14-3 | Luật kiểm chiến dịch (`build_campaign.py`): số thẻ mỗi chương mở | 3-10 | **2-10** (chương 10 còn 2) | thẻ bị xóa |
| PT14-4 | Kinh tế chiến dịch (generator tự tính lại) | blueprint scale 0,50; deck rank 7,00 đầu hồi IV, 7,21 cuối; hồi I-II trả x3,00 | blueprint scale **0,75**; deck rank **7,21** đầu hồi IV, **8,00** cuối; hồi I-II trả **x1,62** | ít thẻ hơn trên đường mở khóa |
| PT14-5 | Bộ bài cố định (fixed decks, 8 xe + 2 hỗ trợ) | thẻ bị xóa | thay bằng thẻ cùng vai trò chưa có trong bộ (log của `Tools/campaign/fixed_decks.py`, thẻ mượn tính lại theo kiểm tra) | thẻ bị xóa |
| PT14-6 | Deck/roster/đợt sóng địch trong chiến dịch, sự kiện (`EventDefs`, `events.py`, tướng) | bmpt, gunship_heli, lancet_truck, ... | ifv, attack_helicopter, fpv_carrier, ... (bỏ khi trùng) | thay thế theo kế hoạch |
| PT14-7 | `openingSquads.roles` | có thẻ bị xóa; vai "radar_scout" | bỏ thẻ bị xóa; vai "bunker" = siege_tank; vai "radar_scout" bỏ (Kerr, Orlov mất ô đó) | thẻ bị xóa |
| PT14-8 | `base.roster` (thẻ tháp) | 22 | **14** | công trình bị xóa |
| PT14-9 | `base.reference` (căn cứ chuẩn tính sức mạnh sóng Phòng thủ/Vô tận) | ô của tháp bị xóa | cùng số ô, tháp còn lại cùng cỡ (mg_bunker, guard_tower, rocket_turret; tiện ích logistics_station, airfield) | giữ sức mạnh chuẩn gần như cũ |
| PT14-10 | `base.ai.styles` (trọng số tháp AI) | có tháp bị xóa | bỏ các khóa đó (Kessler còn "*": 1,0) | công trình bị xóa |
| PT14-11 | Hộ tống boss (`escorts`, `escortTemplates`) | smoke_carrier, counter_battery_radar, lancet_truck, bmpt | ew_jammer, command_vehicle, fpv_carrier, ifv | thay thế |
| PT14-12 | Lính gác Gungnir (`guards`) | dragons_teeth x3 | blast_wall x3 | thay thế |
| PT14-13 | Bản đồ siege coralisles, swamp (và `build_maps.py`) | artillery_emplacement x2 | rocket_turret x2 | thay thế |
| PT14-14 | `PlayerProfile.DefaultLarge` (ô lớn mặc định) | heavy_turret, artillery_emplacement | heavy_turret, **missile_battery** | thay thế |
| PT14-15 | IFV `skills` | ["apc_smoke"] | [] | chủ dự án bỏ apc_smoke |
| PT14-16 | Giá tháp `p32_tower_prices.py`: mốc "protect" | troop_shelter = 5 | shield_tower = 9 (giá tạm của nó) | troop_shelter bị xóa; chỉ là công cụ, không ghi dữ liệu |
| PT14-17 | Save cũ (roster version 9) | - | hoàn tiền thẻ đã mua (`CardMerges.DeletedPt14`), xu + bản vẽ của cấp thẻ, 500 xu mỗi vật phẩm gunship | yêu cầu "file lưu cũ được hoàn lại" |

## Play-test 14 lane B (cloud session 1): UI and base systems

| # | mục | cũ | mới | lý do |
|---|---|---|---|---|
| PT14-B1 | repair_bay | sửa 1,5 %/s xe trong căn cứ | hào quang: mọi xe mặt đất +10 % sát thương, +10 % máu tối đa | kế hoạch PT14 |
| PT14-B2 | airfield | bãi đáp: sửa 3 %/s, nạp đạn; nhánh hangar/service | hào quang: mọi máy bay (không tính drone) +10 % sát thương, +10 % tốc độ; nạp đạn ở HQ; bỏ 2 nhánh | kế hoạch PT14 |
| PT14-B3 | fire_control_centre → Defence Command Centre | tháp trong 30 m +12 % sát thương, dồn mục tiêu | mọi công trình +15 % tầm, +10 % máu | kế hoạch PT14 |
| PT14-B4 | laser_ad_station | nhánh .laser / .net | chỉ .laser; tên Laser Defence Tower | kế hoạch PT14 |
| PT14-B5 | vehicle_hangar, aircraft_hangar (mới) | - | Medium, máu 1800, giáp 2, rebuildCp 8; 1 quân/60 s, tối đa 2 còn sống; mở ở c3m04 / c7m02; AI style mặc định 0,5 / 0,3 | kế hoạch PT14 |
| PT14-B6 | base.roster | 14 | 16 | thêm 2 hangar |
| PT14-B7 | reinforcements | thả 2 MBT + 1 IFV, chỉ tốn vật phẩm | người chơi chọn quân ≤ 20 CP gốc; gọi tốn ceil(1,5 × tổng) CP (và vật phẩm) | chủ dự án 03/10 |
| PT14-B8 | Garrison HQ | đội hỗn hợp theo cấp | tùy chọn: đội là đơn vị người chơi chọn (số lượng = số xe của đội cấp đó) | kế hoạch PT14 |
| PT14-B9 | Giá tháp p32_tower_prices | - | bỏ laser_ad_station.net | biến thể bị xóa |

## PT14 lead (03/10): opening squads after the radar_scout role was emptied
| What | Before | After | Why |
|---|---|---|---|
| commanders.kerr opening roles | scout, light (radar_scout emptied) | scout, scout, light | keeps 3 squads; recon role -> scout jeep |
| generals.orlov opening roles | artillery (radar_scout emptied) | artillery, scout | keeps 2 squads; spotter for the guns |
## Play-test 14 lane A (cloud session 2): gameplay + VFX

Nhánh `cloud/pt14-a`. Lý do ngoài đời: `Docs/DECISIONS.md` "Play-test 14 (lane A, cloud)". Sát thương không đổi.

| # | mục | cũ | mới | lý do |
|---|---|---|---|---|
| PT14-A1 | `armored_car` súng máy đồng trục | `mg_coax` (tầm 20 m) | `mg_coax_long` (kế thừa mg_coax, tầm **30 m**) | pháo 25 mm tầm 30 m: hai súng cùng bắn mục tiêu tháp pháo đang ngắm |
| PT14-A2 | `erectSeconds` (mới) — xe phóng chỉ bắn khi bệ đã dựng | bắn ngay khi có mục tiêu (bệ bật lên tức thì) | phát đầu chờ bệ dựng: mlrs 1,1 s, elite_mlrs 1,1, elite_grad 1,0, heavy_rocket_artillery 1,3, thermobaric_launcher 1,2, rocket_technical 0,7, sam_launcher 0,9, long_sam 1,6, elite_long_sam 1,6, ballistic_launcher 2,2, ground_cruise_missile_vehicle 2,2, missile_battery 1,2, shahed_truck 1,0, lancet_truck 0,8 (giữ dựng 1,2 s sau phát cuối) | bệ phóng nâng với tốc độ thường |
| PT14-A3 | Hộ tống boss (`escortRules.domains`) | bảng hộ tống có thể đưa xe tăng cho boss biển/trên không | xe khác miền đổi theo vai của nó: mặt đất main_battle_tank / light_tank / aa_vehicle / armored_car / engineer_vehicle / ew_jammer; trên không attack_helicopter / fighter_jet / scout_heli; biển missile_boat / hover_gunboat / sea_corvette / river_patrol_boat / river_gunboat | boss nào hộ tống miền đó |
| PT14-A4 | Tàu bọc thép, Nemesis (boss ray) | thân xoay về mục tiêu / hướng hỏa lực khi đứng | thân luôn theo ray, chỉ tháp pháo xoay | xe chạy trên ray |
| PT14-A5 | Leviathan loạt pháo chính | bắn ngay lúc chọn điểm ngắm (tháp nhảy tới hướng) | tháp xoay theo `turretTurnRate` (36°/s, tối thiểu 20°/s) rồi mới bắn khi lệch ≤ 2° (tối đa chờ 10 s); giữa hai loạt bám mục tiêu hiện tại | ngắm xong mới bắn; chu kỳ 60 s giữ nguyên, phát bắn trễ vài giây |
| PT14-A6 | `light_tank` tên lửa bắn qua nòng | có thể bắn cùng lúc với đạn pháo | nòng bận 1 s sau mỗi phát (tên lửa hoặc đạn), hai loại không ra cùng lúc | một nòng nạp một loại đạn |
| PT14-A7 | `boss_howitzer` cờ `"lobs": true` (kế thừa: p26_jotunn_jo203, boss_howitzer_guided) | vẽ như đạn xe tăng | vẽ như pháo binh (đường cầu vồng, lửa đầu nòng, nổ pháo) — chỉ hình ảnh, Sim không đọc | khôi phục hình pháo của boss |
| PT14-A8 | Âm thanh súng sky_gunship (bay vòng, cánh cố định) | như súng mặt đất cùng cỡ | to x1,5, vang xa thêm 20 m, phát đơn dùng bank cỡ lớn hơn một bậc (105 mm nghe như 155 mm) | chủ dự án: tiếng bắn phải mạnh |
| PT14-A9 | Động cơ rocket pháo binh / tên lửa đạn đạo (hình) | tắt ở 85 % / 75 % đường bay | cháy tới lúc nổ; khói kéo tới điểm nổ | vệt khói tới lúc nổ |

Trận replay bị ảnh hưởng: PT14-A1, A2, A3, A4, A5, A6 đổi Sim — baseline của ReplayHashTests cần ghi lại.

## Play-test 14 lane D (cloud session 3)

Nhánh `cloud/pt14-d`. Lý do: `Docs/DECISIONS.md` "Play-test 14 (lane D, cloud)".

| # | mục | cũ | mới | lý do |
|---|---|---|---|---|
| PT14-D1 | `reinforcements` (Tiếp viện thả dù) | vật phẩm mua bằng xu (900 xu / 2 cái), không tốn CP | thẻ hỗ trợ hỏa lực thường: thẻ 0 CP + giá gọi ceil(1,5 x CP quân chọn, tối đa 20 CP); hồi 30 s như cũ; lệnh gọi không kèm quân (AI) thả `units` vừa giới hạn | lead/chủ dự án: không còn là vật phẩm xu |
| PT14-D2 | Mở khóa `reinforcements` | cửa hàng vật phẩm | chiến dịch chương 4 (c4m08, `act11.ORPHANS`); mua sớm theo giá thẻ hỗ trợ | thẻ thường cần đường mở khóa |
| PT14-D3 | Save cũ (roster version 10) | - | mỗi vật phẩm `reinforcements` còn trong túi hoàn 450 xu (`CardMerges.CallItemPricePt14`) | hoàn tiền vật phẩm |
| PT14-D4 | Kinh tế chiến dịch (generator tính lại) | hồi I-II trả x1,64 | x1,66 | thêm một thẻ trên đường mở khóa |
| PT14-D5 | Locust (biến thể drone_mothership) vũ khí drone | dùng chung `p26_matriarch_ma_drones`: loạt 6 drone cách 0,2 s, hồi 4 s (~6 drone / 5 s) | vũ khí riêng `locust_drones`: 1 drone, hồi 2 s (1 drone / 2 s); sát thương mỗi drone giữ nguyên; Matriarch không đổi | chủ dự án: Locust 1 drone mỗi 2 s |
| PT14-D6 | Xóa 10 boss (Stymphalos, Hive, Cerberus, Atlas, Kronos, Caspian, Morrigan, Spectre, Garuda, Gungnir) và các mục chỉ chúng dùng | 41 boss (16 chính, 25 mini) | 31 boss (14 chính, 17 mini); danh sách: `Docs/fixes/playtest14_deleted.md` | chủ dự án bỏ 10 boss |
| PT14-D7 | Boss thay thế trong chiến dịch (máu nhân, bỏ chạy) | c5m05 Hive x1,1; c7m10 Atlas x0,8 chạy 50 %; c8m10 Kronos x1; c9m05 Caspian x1; i3m02 Morrigan x1 chạy 50 %; c10m08 Spectre x3,5; c10m12 Morrigan x1 chạy 50 %; c11m05 Gungnir x1 | c5m05 Matriarch x0,9 chạy 50 %; c7m10 Behemoth Mk.II x0,95 chạy 50 %; c8m10 Tartarus x2,6; c9m05 Charybdis x1,5; i3m02 Harpy x2,9 chạy 50 %; c10m08 Roc x2,7 chạy 50 %; c10m12 Harpy x2,9 chạy 50 %; c11m05 Monster x1,5 | giữ tổng sát thương cần gây ra gần như cũ (máu gốc boss mới x hệ số x phần phải đánh) |
| PT14-D8 | Ô boss các chương | ch.5 mini Locust, Hive; ch.7 Atlas, ...; ch.8 chính Kronos, mini Ixion, Tartarus; ch.9 Caspian, Scylla; ch.10 Spectre, Icarus Mk.0, Argus, Morrigan; ch.11 Gungnir, Locust; III Morrigan | ch.5 Locust; ch.7 Behemoth Mk.II, ...; ch.8 chính Tartarus, mini Ixion; ch.9 Charybdis, Scylla; ch.10 Icarus Mk.0, Argus, Harpy; ch.11 Monster, Locust; III Harpy | thay thế theo truyện |
| PT14-D9 | `mega_gunship` (Harpy) `duel` | không | `"duel": { "escorts": false }` (chỉ trong nhiệm vụ đấu tay đôi c10m12: không hộ tống, không tàng hình) | Raven đấu Hawk bằng Harpy |
| PT14-D10 | Sự kiện mini-boss xen kẽ III | `morrigan_hunt` (Morrigan) | `harpy_hunt` (Harpy); mini của Quaden: Harpy | Morrigan bị xóa |
| PT14-D11 | Tuyến cố định bản đồ openpit | `routes.kronos` | `routes.haul` (cùng tọa độ) | Kronos bị xóa; đường vận chuyển giữ nguyên |
| PT14-D12 | c8m10 stage cuối và ô boss chương 8 (sửa PT14-D7/D8 theo chủ dự án) | Tartarus x2,6 là boss chính; ch.8 chính Tartarus, mini Ixion | Moloch x1,4 là boss chính (Thorne kéo nó lên từ hẻm sông); Tartarus đào hầm trồi lên khi Moloch còn 60 % (sự kiện `tartarus`, như c8m02/c8m11); ch.8 chính Moloch, mini Ixion, Tartarus | chủ dự án: Moloch boss chính, Tartarus boss phụ trong cùng trận |

## Play-test 14 model wave M1 (lane models): boss part places and two own models

Nhánh `feature/pt14-models`. Lý do: `Docs/DECISIONS.md` "Play-test 14 model wave M1 (lane models)". Chỉ dữ liệu vẽ /
vị trí trúng (`at`) và model; sát thương, máu, vũ khí không đổi.

| # | mục | cũ | mới | lý do |
|---|---|---|---|---|
| PT14-M1-1 | `fortress_bastion` parts `at` | turret_fl/fr [∓3.2, 6.0, 4.7], rl/rr [∓2.6, -6.25, 4.7], kornet [-0.85, -3.75, 6.3], casemate [0, 7.6, 3.2], zu23 [∓3.9, -1.5, 5.2] | turrets [∓4.1, 4.35, 3.3] / [∓4.1, -4.25, 3.3] (sponson hai bên hông), kornet [-1.42, -2.75, 6.4], casemate [0, 8.7, 3.2], zu23 [∓3.42, -1.25, 5.4] | súng dời xuống sponson hai bên hông và hành lang bên (chủ: đặt cả ngay hông) |
| PT14-M1-2 | `mobile_fortress` parts `at` | howitzer [0, 3.0, 7.1], rockets [∓1.9, -6.0, 4.6], missiles [0, -6.05, 4.6], howitzer_2 [0, -2.0, 7.4], sam [2.6, -4.4, 5.6] | howitzer [0, 4.0, 7.0], rockets [∓2.15, -6.0, 5.0], missiles [0, 9.0, 3.3] (pháo 125 mm mũi), howitzer_2 [0, -2.1, 7.7], sam [1.25, 5.5, 6.3] (nóc cầu chỉ huy) | đúng 2 bệ phóng đối xứng phía sau; mount 5 bắn đạn 125 mm nên ra từ nòng pháo mũi chứ không từ nắp silo |
| PT14-M1-3 | `bastion_mk0` | vẽ bằng model fortress_bastion | `"model": "bastion_mk0"`; tune mortar `at` [0, -0.83, 9.66] (đơn vị đã nhân size 1.51 của cha) | model riêng (nguyên mẫu) |
| PT14-M1-4 | `fenrir` | vẽ bằng model mobile_fortress | `"model": "fenrir"`; tune `at` rockets_l/r [∓2.02, -6.3, 5.63], flak_l [0, 4.23, 5.47] (đã nhân size 1.657 của cha) | model riêng (xe xích hai khoang mùa đông) |

## Play-test 14 model wave M2 (lane models): trains, Ixion weapons, Harpy wings

Nhánh `feature/pt14-m2`. Lý do: `Docs/DECISIONS.md` "Play-test 14 model wave M2 (lane models)".

| # | mục | cũ | mới | lý do |
|---|---|---|---|---|
| PT14-M2-1 | `armored_train` `length`, parts `at` | 25.06; at y như cũ | 49.18; mọi `at` y + 7.17 (locomotive 14.67, gun_car_front 3.97, gun_car_rear 9.17, rocket_car -1.13, flak_car 0.82, mortar_car -5.33) | thêm 3 toa; model đặt giữa theo chiều dài |
| PT14-M2-2 | `nuke_train` `length`, parts `at` | 41.6; locomotive [0, -8.5, 2.5] (sai phía) | 60.12; mọi `at` y + 19.07; locomotive [0, 25.2, 2.5] (đầu máy thật) | thêm 2 toa; đặt giữa |
| PT14-M2-3 | `mega_gunship` parts | gun_l/r [∓0.56, 7.1, 1.1]; pod_l/r [∓2.67, 1.3, 1.4] không node; missiles [0, 1.25, 1.5] không node | gun_l/r [∓2.3, 1.05, 0.95]; pod_l/r [∓3.2, -0.1, 1.14] node Part_pod / Part_pod.001; missiles [0, 0.1, 1.42] node Part_missiles | súng và bệ phóng lên cánh |
| PT14-M2-4 | `mega_gunship` secondary 0, 1 (boss_heli_gun) | Free, không arc | Free, `arc` [-45, 70] / [45, 70] | nòng súng cánh không quay xuyên thân |
| PT14-M2-5 | `ixion` secondary | 2 x p26_ixion_mg | + pt14_ixion_30 (gun), 2 x pt14_ixion_kornet (missile), pt14_ixion_grad (rocket) | chủ nhân: thêm 4-5 vũ khí |
| PT14-M2-6 | vũ khí mới | — | pt14_ixion_30: 2A42 30 mm, kế thừa autocannon_30, 22 x 8 phát, hồi 3.5 s (~41 DPS); pt14_ixion_kornet: 9M133 Kornet-EM, kế thừa boss_missiles, 230, hồi 12 s (~19 DPS mỗi bệ); pt14_ixion_grad: BM-21V 122 mm, kế thừa grad_rockets, 57 x 9, hồi 20 s (~21 DPS) | tổng hỏa lực tầm xa thô của Ixion ~278 -> ~379 DPS (+36 %, trước outgoingDamageMult) |
## Gói cân bằng 2, bổ sung 03/10, mục 2-6 (lane A)

Nhánh `feature/pack2-add` (worktree MachineBrigade-art), `Docs/cloud/PT14_CLOUD_TASKS.md` session 6. Chỉ lý thuyết:
không chạy Unity, không chạy test, không chạy ExportGameDoc. Mục 1 (tầm tối thiểu boss) không nằm trong lượt này —
chờ session 7 sau khi lane model gộp xong (không đụng dữ liệu boss ở đây). `python Tools/export/export.py
--game-json Docs/export/game_snapshot.json` + `export.py check --game-json ...`: 15/15; `dotnet build
Tools/simbuild/Sim.csproj`: 0 lỗi; `mbconst check --base HEAD --dotnet`: (b)-(e) PASS, (a) 16/21 hunk chỉ đổi literal
(5 hunk còn lại là tính năng ghi đè theo từng vũ khí ở mục 2, sửa tay có lý do, không phải lượt công cụ).

### Mục 2 — Tên lửa (sheet `Ten_lua_tham_so`, 01_chien_dau, 45 dòng, 21 cột riêng + FK `vu_khi_id`)

| # | tham số | trước | sau | lý do |
|---|---|---|---|---|
| PK2A-1 | `weapons.guidance.baseFailChance` | hằng số 0,02 trong `CombatSystem.cs` | khóa dữ liệu, giá trị giữ 0,02 | luật B: tỉ lệ trượt gốc của một phát bắn đạn có dẫn (không phụ thuộc chuyển động mục tiêu) |
| PK2A-2 | `weapons.guidance.rangeFailCoeff` | hằng số 0,08 | khóa dữ liệu, giá trị giữ 0,08 | luật B: hệ số theo (tầm bắn / tầm tối đa)² trong cùng công thức trượt |
| PK2A-3 | `WeaponDef.ProximityFuze` (mới, `float?`) | không có; mọi vũ khí dùng `munitionRules.proximityFuze` = 7 m chung | cờ dữ liệu riêng từng vũ khí (balance.json `proximityFuze`), null = theo nhóm; chưa vũ khí nào ghi đè | đưa tham số nhóm xuống từng vũ khí theo yêu cầu bổ sung; **hành vi không đổi** (chưa cơ chế nào đọc giá trị này để nổ cận đích — xem ghi chú) |
| PK2A-4 | `WeaponDef.JamMissMin` / `JamMissSpread` (mới, `float?`) | không có; mọi vũ khí dùng `weapons.jamRules.guidedMissMin` (5 m) / `guidedMissSpread` (6 m) chung | cờ dữ liệu riêng từng vũ khí (`jamMissMin` / `jamMissSpread`), null = theo nhóm; `CombatSystem.cs` đọc `weapon.JamMissMin ?? SimTunables...GuidedMissMin` | đưa tham số nhóm xuống từng vũ khí theo yêu cầu bổ sung; **hành vi không đổi** (chưa vũ khí nào ghi đè, giá trị bằng giá trị nhóm cũ) |

Ghi chú PK2A-3: `MunitionRules.ProximityFuze` (và nay `WeaponDef.ProximityFuze`) không được bất kỳ luật bắn / nổ nào
trong mã đọc để quyết định nổ cận đích — nó chỉ góp vào công thức `FlareOffset` (khoảng pháo sáng phải xa cận đích
tối thiểu 2 m). Cờ riêng từng vũ khí đã có sẵn (balance.json `proximityFuze`) cho một lượt sau nối nó vào luật nổ
nếu chủ dự án muốn; **lượt này không nối**, vì nối nó sẽ đổi hành vi (luật D cấm trừ khi chủ dự án yêu cầu).

**Câu hỏi mục 2 (đọc mã, không chạy game): tên lửa dẫn đường đánh mặt đất có trượt khi mục tiêu chạy không?**
KHÔNG. `CombatSystem.Munitions.cs` luật A: "a guided round lands on its target wherever it drove: it cannot be
outrun" — `Homes(WeaponDef)` đúng với Guided/GuidedRocket/GuidedBomb/GuidedShell; điểm nổ là vị trí THỰC của mục
tiêu lúc đạn tới, không phải điểm đón đầu tính trước (điểm đón đầu `LeadPoint`/`Leads` chỉ áp cho đạn KHÔNG dẫn:
rocket, bom, pháo bắn cầu — luật D). Đạn dẫn có thể trượt, nhưng không lý do nào là "vì mục tiêu di chuyển":
(1) một lần tung xác suất lúc bắn (`weapons.guidance.baseFailChance + rangeFailCoeff × tầm²`, chỉ phụ thuộc tầm bắn,
không phụ thuộc tốc độ / hướng mục tiêu); (2) bị gây nhiễu lúc bắn (độc lập chuyển động); (3) tên lửa dẫn bằng tầm
nhìn (dây / chùm / laser) mất mục tiêu nếu bên bắn chết, một trong hai bên ở trong khói, hoặc (cả hai trên mặt đất)
có vật cản chắn tầm nhìn — cũng không phụ thuộc tốc độ; (4) tên lửa hồng ngoại bị pháo sáng kéo đi (một lần tung xác
suất theo đám pháo sáng); (5) mục tiêu ra khỏi tầm bay của đạn (`tầm × RangeFactor × ReachScale`) trước khi đạn tới —
trường hợp DUY NHẤT chuyển động có liên quan, và ngay cả vậy đạn chỉ tự hủy ở biên tầm bay, không phải "trượt" theo
nghĩa bắn hụt. Khớp với mặc định chính addendum đã nêu (mục 4.2): "không né được bằng cách chạy với tên lửa dẫn
đường" — nay xác nhận đúng bằng đọc mã, không phải giả định.

Cột `kieu_dan` của sheet suy từ `guided` + `weaponFamilyId` có trong `munitionRules.radarGuided` / `sightGuided`
không (dữ liệu không có cột phân loại kiểu dẫn riêng): chỉ ba nhóm mã phân biệt được — bám radar, dẫn theo tầm nhìn
bên bắn (dây / chùm / laser), hồng ngoại / mặc định; laser riêng, ảnh nhiệt, GPS-quán tính KHÔNG được mã phân biệt
(NEED_CODE_CHECK nếu chủ dự án cần tách thêm). Các cột động học (`toc_do_quay_deg_s`, `gia_toc_ngang_m_s2`,
`ban_kinh_quay_m`, `he_so_bam`, `thoi_gian_khoa_s`, `vertical_launch`): **KHONG_CO** — Sim không mô phỏng động học
bay chi tiết của tên lửa (đạn dẫn luôn tới đúng vị trí mục tiêu trừ khi bị chệch theo 5 lý do ở trên); mọi cột khác
(sát thương, lõi/rìa nổ, tầm, tầm tối thiểu, tốc độ đạn, cờ APS/CIWS/pháo sáng/jam-proof, băng đạn, thời gian nạp) đã
có sẵn ở `Vu_khi` (tra theo `vu_khi_id`), không chép lại.

### Mục 3 — Napalm và lửa (đã có trong dữ liệu; 5 khóa mới ở phần trang bị)

Cơ chế cháy theo thời gian (`DamageSystem.cs Hit`, `StatusSystem.cs Burn`) ĐÃ ra dữ liệu từ trước: `weapons.
damageSystem.fireBurnSeconds` = 3 s, `fireAfterburn` = 0,3 (đã có trong tunables.json). dps = sát thương lọt qua ×
fireAfterburn / fireBurnSeconds; bán kính = bán kính nổ của vũ khí (đã ở `Vu_khi.loi_m`/`ria_m`); chồng lên nhau =
`Burn(..., stack: true)` cộng phần sát thương còn lại của đám cháy cũ vào đám mới, cùng một cửa sổ `fireBurnSeconds`
(không phải hai đồng hồ riêng). 5 hằng số còn lại, đều trong nhánh trang bị Incendiary Rounds / Firestorm
(`GearSystem.cs`, chỗ duy nhất khác đốt lửa), chuyển ra `weapons.fire.*`:

| # | khóa | giá trị | ý nghĩa |
|---|---|---|---|
| PK2A-5 | `weapons.fire.incendiaryFlameSeconds` | 6 s | thời gian cháy khi vũ khí là súng phun lửa |
| PK2A-6 | `weapons.fire.incendiaryOtherSeconds` | 4 s | thời gian cháy khi vũ khí khác súng phun lửa |
| PK2A-7 | `weapons.fire.firestormShare` | 0,1 (10%) | tỉ lệ sát thương chuyển thành dps cháy khi chỉ có trang bị Firestorm (không có Incendiary Rounds) |
| PK2A-8 | `weapons.fire.firestormSpreadRadiusSqM` | 36 m² | bán kính² tìm đồng minh gần nhất để lửa nhảy sang khi xe mang Firestorm chết đang cháy (giữ dạng bình phương, không đổi thành bán kính 6 m, để không đổi bit nào của phép so sánh) |
| PK2A-9 | `weapons.fire.firestormSpreadSeconds` | 4 s | thời gian cháy mang theo khi lửa nhảy sang xe khác |

2 hằng số cháy của boss (`BossSystem.BigAttacks.cs:1205`, `BossSystem.Trail.cs:67`, cùng 1,2 s) **không đụng** (dữ
liệu boss thuộc lane model) — để lại cho session mục 1. Không tạo sheet `Chay_tham_so` riêng: 5 khóa trên đã hiện ở
sheet `Hang_so_vu_khi` (01_chien_dau, sheet hằng số chung sinh tự động từ tunables.json), nơi `fireBurnSeconds` /
`fireAfterburn` đã có sẵn — thêm một sheet riêng cho đúng 5 dòng đã thấy ở đó là chép hai lần.

### Mục 4 — Tháp / căn cứ (31 khóa mới, `Hang_so_can_cu` 2 → 33 dòng)

31 hằng số mặc định trong các cơ chế tháp/công trình của `Catalog.P25A.cs` (giá trị dự phòng của `o.Float("<khóa>",
<mặc_định>)` khi JSON công trình không ghi khóa đó — bản khởi tạo thuộc tính cùng số là mã chết, vì khi khối JSON
tồn tại mọi trường luôn được gán tay, nên chỉ di dời phần dự phòng) chuyển ra `bases.*`: `blastWall` (radiusM 8,
cutShare 0,3, coneDeg 50), `fireControl` (radiusM 30, damageShare 0,12, focus 2), `hangar` (everySeconds 60, alive
2, postM 20, budget 0), `searchlight` (radiusM 35, dazzleShare 0,2), `balloon` (radiusM 40, scatterShare 0,5),
`sightJammer` (radiusM 35, closeM 15), `shelter` (radiusM 15, cutShare 0,5), `flareTower` (everySeconds 15, rangeM
40, radiusM 30, seconds 15), `microwave` (rangeM 30, arcDeg 60, cooldownSeconds 8), `droneHunt` (reachM 60),
`paradrop` (fallSeconds 6, heightM 30, baseKeepOutM 45), `reconPass` (widthM 60, seconds 20) — đúng "chọn mục tiêu
tháp, hào quang, ngưỡng kích hoạt, bán kính" addendum yêu cầu (fireControl = chọn mục tiêu / dồn hỏa lực; blastWall /
shelter / searchlight / balloon / sightJammer / microwave / droneHunt = hào quang và ngưỡng; mọi cái còn lại là bán
kính). Không tạo sheet riêng: các khóa này tự hiện ở `Hang_so_can_cu` (03_can_cu) — chính addendum lấy số dòng của
sheet này làm mốc ("Hang_so_can_cu hiện 2 dòng"), nay 33 dòng. `TowerModes.cs` (36 dòng) không có hằng số nào để dời.

### Mục 5 — Gọn `Bom_vu_khi` (220 → 74 cột, 14 dòng giữ nguyên)

`Tools/export/bom.py sheet_vu_khi` trước đây lấy TOÀN BỘ cột của `Vu_khi` trừ id/nguon/raw_json làm cột — hầu hết là
chép lại từ Vu_khi (gia đình vũ khí, before/after theo dõi thay đổi, nhịp bắn ngoài đời, bản tiếng Anh trùng với cột
tiếng Việt đã có, và bản `stick_*` thô trùng với `STICK_COLS` tiếng Việt bom.py tự tính). Thay bằng danh sách cho
phép `BOMB_ONLY_COLS` (29 cột: các trường hiệu lực riêng của bom — sát thương, nổ, tầm, cờ ngòi/quỹ đạo, băng/nạp —
cộng 5 cột `cluster_*`) và thêm khóa ngoại `vu_khi_id` rõ ràng (= id vũ khí ở dòng vũ khí; để trống ở dòng thẻ hỗ trợ
/ siêu vũ khí boss vì không phải dòng Vu_khi). Kết quả 220 → 74 cột, 14 dòng không đổi.

**Lỗi tìm thấy và đã sửa khi làm mục này:** `static_sheets()` lọc dòng của `Bom_vu_khi` bằng `r[1] ==
"vu_khi_don_vi"` (chỉ số vị trí trong tuple dòng, không theo tên cột) để dựng tra cứu cho `Bom_canh_bao` và
`Bom_don_vi`; chèn `vu_khi_id` ngay sau "id" (chỉ số 1) làm rỗng bộ lọc đó một cách im lặng, vỡ `Bom_canh_bao` với
`KeyError`, bị `add_bom_sheets`'s `except KeyError: return` (dành cho bản xuất cũ/lenient) bắt mất — bỏ cả 4 sheet
bom mà không báo lỗi (`export.py check` mục "19 file đúng danh sách" vẫn PASS vì việc một sheet biến mất trong xlsx
không thuộc phép kiểm đó). Đã sửa bằng cách đặt `vu_khi_id` sau "nhom" (chỉ số 2); xuất lại toàn bộ và đọc lại danh
sách sheet để xác nhận đủ 4 sheet bom, số dòng không đổi.

### Mục 6 — Báo cáo (mục 2-5)

- Sheet mới: `Ten_lua_tham_so` (01_chien_dau, 45 dòng, 21 cột riêng + FK `vu_khi_id`).
- Cột mới: `Bom_vu_khi.vu_khi_id` (FK tới Vu_khi).
- Tham số chuyển ra dữ liệu: 38 khóa tunables.json mới (5 `weapons.fire.*`, 2 `weapons.guidance.*`, 31 `bases.*`;
  `mbconst check`: 38/38 lượt đổi literal-only sạch) + 3 cờ dữ liệu riêng từng vũ khí mới (`WeaponDef.ProximityFuze`,
  `JamMissMin`, `JamMissSpread`; sửa tay có lý do, không phải lượt công cụ — xem mục 2). Tổng cộng tunables.json từ
  291 lên 329 khóa.
- Tầm tối thiểu boss cũ/mới theo vũ khí, danh sách boss có vùng chết chưa được phủ: **không thuộc lượt này** (mục 1,
  session 7, chờ lane model).
- Cần chạy lại từ Unity: không cột nào trong 2-5 cần game.json mới (mọi NEED_CODE_CHECK đã về 0 với snapshot hiện
  có); việc nối `WeaponDef.ProximityFuze` vào luật nổ cận đích (nếu chủ dự án muốn dùng) sẽ cần kiểm bằng Unity sau
  khi sửa luật đó — chưa sửa ở đây.

## Play-test 14 model wave M3 (lane models): sea boss part places, Scylla's own model

Nhánh `feature/pt14-m3`. Lý do: `Docs/DECISIONS.md` "Play-test 14 model wave M3 (lane models)". Chỉ dữ liệu vẽ /
vị trí trúng (`at`), node và model; sát thương, máu, vũ khí không đổi.

| # | mục | cũ | mới | lý do |
|---|---|---|---|---|
| PT14-M3-1 | `leviathan` parts `at` | sec_fore [0, 7.2, 10.5]; ciws_aft [-2.1, -16.5, 6.9] | sec_fore [0, 6.0, 10.5]; ciws_aft [-2.6, -14.8, 7.0] | giếng tháp pháo phụ trước lùi 1.2 m để không chạm tháp B; pháo 127 mm sau đặt cạnh giếng sau |
| PT14-M3-2 | `scylla` | vẽ bằng model leviathan (x 0.56) | `"model": "scylla"`, `"modelSize": [49.3, 9.3, 14.2]`; tune `at` turret_fore [0, 30.4, 8.88], vls [0, 12.4, 7.48], ciws_fore [0, 14.6, 15.78] (đơn vị trước khi nhân size 0.5 của variant) | model riêng (tuần dương hạm), cùng kích thước như cũ |
| PT14-M3-3 | `kraken` tune `at` (mọi part) | theo model cũ (ô tên lửa) | turret_fore [0, 33.68, 7.93], turret_super [0, 25.09, 8.81], turret_aft [0, -42.46, 6.35], sec_fore [6.75, 15.61, 7.27], sec_aft [-6.32, -33.51, 9.08], vls [0, 18.6, 6.33], aa_port [-7.28, -8.77, 8.48], aa_starboard [6.84, -26.32, 8.48], ciws_fore [4.74, 21.4, 6.88], ciws_aft [-5.09, -45.79, 5.34], radar [6.4, 0, 16.63], flight_deck [-2.98, -26.32, 9.11], well_deck [0, -48.03, 3.92], machinery [6.4, -8.42, 14.89] (chia 1.14) | vẽ lại: tháp pháo thật ở mũi / đuôi, sàn bay chéo, đảo chỉ huy mạn phải |
| PT14-M3-4 | `nyx` tune `at` | (không có: theo leviathan x 0.616) | turret_fore [0, 24.0, 6.96], vls [0, 15.64, 5.71], ciws_fore [0, 9.73, 12.56], ciws_aft [0, -17.82, 12.56] (chia 0.55) | vị trí của model mới (VLS ở mũi, hai pháo 127 mm trên nóc thượng tầng) |
| PT14-M3-5 | `hydra` tune | (không có) | doors_l/r `at` [∓0.95, -7.51, 4.45], deck_gun `node` "Mount_gun.002" + `at` [0, 16.61, 6.23], rudder `at` [0, -30.45, 0.59] (chia 0.5057) | ba bệ súng của def nay có ba khẩu: Mount_gun / .001 là hai pháo đôi 57 mm, khẩu 100 mm (part deck_gun) là Mount_gun.002 |
