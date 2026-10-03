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
