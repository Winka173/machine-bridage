# VIỆC CHO AGENT CODE — FINAL

## Luật áp dụng
- Đây là quyết định cuối. Không hỏi lại về cân bằng và không để HOLD/DECIDE/CHECK.
- Với mỗi dòng manifest: kiểm `expected_before`; nếu khớp thì áp `new_value`. Nếu không khớp, báo CONFLICT nhưng **không tự chọn số khác**.
- Dữ liệu vision/stealth/radar/reveal được GIỮ cho hệ tương lai. Không xóa và không dùng chúng để bù cân bằng hiện tại.
- Sau khi áp, re-export toàn bộ gói và chạy validators + replay hash. Test là **validation sau thay đổi**, không phải điều kiện để quyết định số.

## 1. Boss range override per boss
Tạo lớp override theo `boss_id + weapon_id` cho `groundMinReach/minRange/maxRange`. Áp toàn bộ dòng `bossWeaponOverrides[...]` trong manifest. Không sửa shared weapon toàn cục nếu weapon còn được xe/tháp dùng. Close-defense (MG/CIWS/flak/flame) giữ min gần 0.

## 2. Mission fixed deck
10 mission đang `MAKE_LATER` phải chuyển `READY` theo manifest. Implement đầy đủ `specialRules` hiện đã ghi trong từng mission trước khi set READY trong cùng commit; không để trạng thái tạm.

## 3. Survival pacing
Chốt 10 wave, mục tiêu xấp xỉ 60 s/wave, tổng khoảng 10 phút. Nếu cadence hiện tại khác, chỉnh `Hang_so_che_do`/wave scheduler để median thiết kế bám mục tiêu; không đổi số wave.

## 4. Weekly mutator
Thay ghi chú `NEED_CODE_CHECK` bằng luật cuối: seed deterministic = `year*100 + ISO_week`; chọn 2 mutator khác nhau không vi phạm `excludes`; ưu tiên một mutator tăng áp lực và một mutator đổi luật chơi; nếu pool không đủ thì chọn theo thứ tự id ổn định. Cùng tuần + cùng version phải cho cùng cặp.

## 5. AI
`Laser.overwhelmed`: `Smoke -> Shift`. Không thêm retreat-on-health. `Rearm` của aircraft là chu trình nạp/attack pass, không được kích hoạt vì HP thấp. Tất cả 16 tactic giữ vector CP hiện tại (tổng=1.0) và module hiện tại.

## 6. VFX/feel
Giữ thang T0–T5 hiện có làm nền; khi các damage/cooldown/radius mới áp, map tier từ caliber/warhead và đảm bảo muzzle flash/recoil/explosion tăng cùng chiều. Không thay gameplay bằng VFX ngoài radius/damage đã có trong manifest.

## 7. Các thay đổi requires_code cụ thể
- `survival` — `matchRules.modes.survival.text.timeLimit`: `~8–12 phút; nếu nhịp đợt làm 10 đợt vượt mục tiêu thì chỉnh số đợt hoặc nhịp` → `10 đợt; nhịp mục tiêu khoảng 60 giây/đợt, tổng khoảng 10 phút`. Loại câu điều kiện chưa chốt; giữ 10 đợt với pacing mục tiêu rõ ràng.
- `armored_train/train_gun` — `bossWeaponOverrides[armored_train][train_gun].groundMinReach`: `0.0` → `25.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `armored_train/train_gun` — `bossWeaponOverrides[armored_train][train_gun].maxRange`: `42.0` → `80`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `armored_train/boss_rockets` — `bossWeaponOverrides[armored_train][boss_rockets].groundMinReach`: `0.0` → `14.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `bastion_mk0/p26_bastion_direct_b100` — `bossWeaponOverrides[bastion_mk0][p26_bastion_direct_b100].groundMinReach`: `0.0` → `19.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `bastion_mk0/p26_bastion_direct_b100` — `bossWeaponOverrides[bastion_mk0][p26_bastion_direct_b100].maxRange`: `36.0` → `61`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `behemoth/p26_behemoth_main_be152` — `bossWeaponOverrides[behemoth][p26_behemoth_main_be152].groundMinReach`: `0.0` → `32.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `behemoth/p26_behemoth_main_be152` — `bossWeaponOverrides[behemoth][p26_behemoth_main_be152].maxRange`: `40.0` → `103`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `behemoth/p26_behemoth_tiny_be120` — `bossWeaponOverrides[behemoth][p26_behemoth_tiny_be120].groundMinReach`: `0.0` → `25.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `behemoth/p26_behemoth_tiny_be120` — `bossWeaponOverrides[behemoth][p26_behemoth_tiny_be120].maxRange`: `32.0` → `80`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `behemoth/p26_behemoth_tiny_boss_missiles` — `bossWeaponOverrides[behemoth][p26_behemoth_tiny_boss_missiles].groundMinReach`: `0.0` → `1.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `behemoth/p26_behemoth_tiny_kornet_twin` — `bossWeaponOverrides[behemoth][p26_behemoth_tiny_kornet_twin].groundMinReach`: `0.0` → `25.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `behemoth/p26_behemoth_tiny_kornet_twin` — `bossWeaponOverrides[behemoth][p26_behemoth_tiny_kornet_twin].maxRange`: `32.0` → `80`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `behemoth/p26_behemoth_direct_be120` — `bossWeaponOverrides[behemoth][p26_behemoth_direct_be120].groundMinReach`: `0.0` → `25.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `behemoth/p26_behemoth_direct_be120` — `bossWeaponOverrides[behemoth][p26_behemoth_direct_be120].maxRange`: `32.0` → `80`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `behemoth/p26_behemoth_sec_be_rockets` — `bossWeaponOverrides[behemoth][p26_behemoth_sec_be_rockets].groundMinReach`: `0.0` → `30.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `behemoth/p26_behemoth_sec_be_rockets` — `bossWeaponOverrides[behemoth][p26_behemoth_sec_be_rockets].maxRange`: `45.0` → `96`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `behemoth_inferno/boss_thermo` — `bossWeaponOverrides[behemoth_inferno][boss_thermo].groundMinReach`: `0.0` → `21.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `behemoth_inferno/boss_thermo` — `bossWeaponOverrides[behemoth_inferno][boss_thermo].maxRange`: `46.0` → `68`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `behemoth_mk0/p26_behemoth_main_be152` — `bossWeaponOverrides[behemoth_mk0][p26_behemoth_main_be152].groundMinReach`: `0.0` → `36.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `behemoth_mk0/p26_behemoth_main_be152` — `bossWeaponOverrides[behemoth_mk0][p26_behemoth_main_be152].maxRange`: `40.0` → `116`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `behemoth_mk0/p26_behemoth_direct_be120` — `bossWeaponOverrides[behemoth_mk0][p26_behemoth_direct_be120].groundMinReach`: `0.0` → `24.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `behemoth_mk0/p26_behemoth_direct_be120` — `bossWeaponOverrides[behemoth_mk0][p26_behemoth_direct_be120].maxRange`: `32.0` → `77`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `behemoth_mk0/p26_behemoth_sec_be_rockets` — `bossWeaponOverrides[behemoth_mk0][p26_behemoth_sec_be_rockets].groundMinReach`: `0.0` → `23.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `behemoth_mk0/p26_behemoth_sec_be_rockets` — `bossWeaponOverrides[behemoth_mk0][p26_behemoth_sec_be_rockets].maxRange`: `45.0` → `74`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `behemoth_mk2/p26_behemoth_main_be152` — `bossWeaponOverrides[behemoth_mk2][p26_behemoth_main_be152].groundMinReach`: `0.0` → `32.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `behemoth_mk2/p26_behemoth_main_be152` — `bossWeaponOverrides[behemoth_mk2][p26_behemoth_main_be152].maxRange`: `40.0` → `103`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `behemoth_tempest/boss_railgun` — `bossWeaponOverrides[behemoth_tempest][boss_railgun].groundMinReach`: `0.0` → `33.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `behemoth_tempest/boss_railgun` — `bossWeaponOverrides[behemoth_tempest][boss_railgun].maxRange`: `80.0` → `106`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `behemoth_tempest/coilgun` — `bossWeaponOverrides[behemoth_tempest][coilgun].groundMinReach`: `0.0` → `17.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `command_airship/p26_roc_direct_roc_atgm` — `bossWeaponOverrides[command_airship][p26_roc_direct_roc_atgm].groundMinReach`: `0.0` → `1.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `command_airship/p26_roc_roc105` — `bossWeaponOverrides[command_airship][p26_roc_roc105].groundMinReach`: `0.0` → `22.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `command_airship/p26_roc_roc105` — `bossWeaponOverrides[command_airship][p26_roc_roc105].maxRange`: `58.0` → `71`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `daedalus/p26_daedalus_direct_dae_laser` — `bossWeaponOverrides[daedalus][p26_daedalus_direct_dae_laser].groundMinReach`: `0.0` → `13.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `daedalus/p26_daedalus_direct_dae_laser` — `bossWeaponOverrides[daedalus][p26_daedalus_direct_dae_laser].maxRange`: `36.0` → `42`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `daedalus/p26_daedalus_sec_dae57` — `bossWeaponOverrides[daedalus][p26_daedalus_sec_dae57].groundMinReach`: `0.0` → `13.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `daedalus/p26_daedalus_sec_dae57` — `bossWeaponOverrides[daedalus][p26_daedalus_sec_dae57].maxRange`: `28.0` → `42`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `drone_mothership/p26_matriarch_tiny_mothership_cannon` — `bossWeaponOverrides[drone_mothership][p26_matriarch_tiny_mothership_cannon].groundMinReach`: `0.0` → `13.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `drone_mothership/p26_matriarch_ma_drones` — `bossWeaponOverrides[drone_mothership][p26_matriarch_ma_drones].groundMinReach`: `0.0` → `1.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `drone_mothership/p26_matriarch_direct_ma_atgm` — `bossWeaponOverrides[drone_mothership][p26_matriarch_direct_ma_atgm].groundMinReach`: `0.0` → `1.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `earth_borer/borer_cannon` — `bossWeaponOverrides[earth_borer][borer_cannon].groundMinReach`: `0.0` → `16.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `earth_borer/borer_cannon` — `bossWeaponOverrides[earth_borer][borer_cannon].maxRange`: `34.0` → `52`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `fenrir/p26_jotunn_sec_jo_rockets` — `bossWeaponOverrides[fenrir][p26_jotunn_sec_jo_rockets].groundMinReach`: `0.0` → `16.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `fenrir/p26_jotunn_sec_jo_rockets` — `bossWeaponOverrides[fenrir][p26_jotunn_sec_jo_rockets].maxRange`: `45.0` → `52`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `fortress_bastion/p26_bastion_direct_b100` — `bossWeaponOverrides[fortress_bastion][p26_bastion_direct_b100].groundMinReach`: `0.0` → `28.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `fortress_bastion/p26_bastion_direct_b100` — `bossWeaponOverrides[fortress_bastion][p26_bastion_direct_b100].maxRange`: `36.0` → `90`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `fortress_bastion/p26_bastion_tiny_kornet_twin` — `bossWeaponOverrides[fortress_bastion][p26_bastion_tiny_kornet_twin].groundMinReach`: `0.0` → `1.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `hydra/p26_typhon_sec_ty57` — `bossWeaponOverrides[hydra][p26_typhon_sec_ty57].groundMinReach`: `0.0` → `35.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `hydra/p26_typhon_sec_ty57` — `bossWeaponOverrides[hydra][p26_typhon_sec_ty57].maxRange`: `40.0` → `112`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `hydra/p26_typhon_direct_ty100` — `bossWeaponOverrides[hydra][p26_typhon_direct_ty100].groundMinReach`: `0.0` → `8.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `hyperion/p26_icarus_sec_orbital_laser` — `bossWeaponOverrides[hyperion][p26_icarus_sec_orbital_laser].groundMinReach`: `0.0` → `14.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `hyperion/p26_icarus_sec_orbital_laser` — `bossWeaponOverrides[hyperion][p26_icarus_sec_orbital_laser].maxRange`: `36.0` → `45`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `hyperion/p26_icarus_main_ic_coil` — `bossWeaponOverrides[hyperion][p26_icarus_main_ic_coil].groundMinReach`: `0.0` → `21.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `hyperion/p26_icarus_main_ic_coil` — `bossWeaponOverrides[hyperion][p26_icarus_main_ic_coil].maxRange`: `55.0` → `68`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `hyperion/p26_icarus_direct_ic_laser` — `bossWeaponOverrides[hyperion][p26_icarus_direct_ic_laser].groundMinReach`: `0.0` → `18.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `hyperion/p26_icarus_direct_ic_laser` — `bossWeaponOverrides[hyperion][p26_icarus_direct_ic_laser].maxRange`: `36.0` → `58`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `icarus_mk0/p26_icarus_sec_orbital_laser` — `bossWeaponOverrides[icarus_mk0][p26_icarus_sec_orbital_laser].groundMinReach`: `0.0` → `11.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `ixion/p26_ixion_125` — `bossWeaponOverrides[ixion][p26_ixion_125].groundMinReach`: `0.0` → `30.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `ixion/p26_ixion_125` — `bossWeaponOverrides[ixion][p26_ixion_125].maxRange`: `38.0` → `96`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `ixion/pt14_ixion_kornet` — `bossWeaponOverrides[ixion][pt14_ixion_kornet].groundMinReach`: `0.0` → `1.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `ixion/pt14_ixion_grad` — `bossWeaponOverrides[ixion][pt14_ixion_grad].maxRange`: `55.0` → `58`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `kraken/p26_leviathan_lev406` — `bossWeaponOverrides[kraken][p26_leviathan_lev406].groundMinReach`: `0.0` → `120`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `kraken/p26_leviathan_lev406` — `bossWeaponOverrides[kraken][p26_leviathan_lev406].maxRange`: `160.0` → `300`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `kraken/p26_leviathan_sec_lev155` — `bossWeaponOverrides[kraken][p26_leviathan_sec_lev155].groundMinReach`: `0.0` → `88.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `kraken/p26_leviathan_sec_lev155` — `bossWeaponOverrides[kraken][p26_leviathan_sec_lev155].maxRange`: `110.0` → `282`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `kraken/p26_leviathan_direct_lev127` — `bossWeaponOverrides[kraken][p26_leviathan_direct_lev127].groundMinReach`: `0.0` → `29.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `kraken/p26_leviathan_direct_lev127` — `bossWeaponOverrides[kraken][p26_leviathan_direct_lev127].maxRange`: `90.0` → `93`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `leviathan/p26_leviathan_lev406` — `bossWeaponOverrides[leviathan][p26_leviathan_lev406].groundMinReach`: `0.0` → `103.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `leviathan/p26_leviathan_lev406` — `bossWeaponOverrides[leviathan][p26_leviathan_lev406].maxRange`: `160.0` → `300`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `leviathan/p26_leviathan_sec_lev155` — `bossWeaponOverrides[leviathan][p26_leviathan_sec_lev155].groundMinReach`: `0.0` → `90.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `leviathan/p26_leviathan_sec_lev155` — `bossWeaponOverrides[leviathan][p26_leviathan_sec_lev155].maxRange`: `110.0` → `288`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `leviathan/p26_leviathan_direct_lev127` — `bossWeaponOverrides[leviathan][p26_leviathan_direct_lev127].groundMinReach`: `0.0` → `42.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `leviathan/p26_leviathan_direct_lev127` — `bossWeaponOverrides[leviathan][p26_leviathan_direct_lev127].maxRange`: `90.0` → `135`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `locust/locust_drones` — `bossWeaponOverrides[locust][locust_drones].groundMinReach`: `0.0` → `1.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `mega_gunship/gunship_rockets` — `bossWeaponOverrides[mega_gunship][gunship_rockets].groundMinReach`: `0.0` → `10.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `mobile_fortress/p26_jotunn_jo203` — `bossWeaponOverrides[mobile_fortress][p26_jotunn_jo203].groundMinReach`: `0.0` → `48.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `mobile_fortress/p26_jotunn_jo203` — `bossWeaponOverrides[mobile_fortress][p26_jotunn_jo203].maxRange`: `60.0` → `154`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `mobile_fortress/p26_jotunn_sec_jo_rockets` — `bossWeaponOverrides[mobile_fortress][p26_jotunn_sec_jo_rockets].groundMinReach`: `0.0` → `32.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `mobile_fortress/p26_jotunn_sec_jo_rockets` — `bossWeaponOverrides[mobile_fortress][p26_jotunn_sec_jo_rockets].maxRange`: `45.0` → `103`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `mobile_fortress/p26_jotunn_direct_jo125` — `bossWeaponOverrides[mobile_fortress][p26_jotunn_direct_jo125].groundMinReach`: `0.0` → `30.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `mobile_fortress/p26_jotunn_direct_jo125` — `bossWeaponOverrides[mobile_fortress][p26_jotunn_direct_jo125].maxRange`: `38.0` → `96`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `moloch/p26_moloch_main_mo120` — `bossWeaponOverrides[moloch][p26_moloch_main_mo120].groundMinReach`: `0.0` → `25.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `moloch/p26_moloch_main_mo120` — `bossWeaponOverrides[moloch][p26_moloch_main_mo120].maxRange`: `32.0` → `80`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `moloch/p26_moloch_direct_mo120ap` — `bossWeaponOverrides[moloch][p26_moloch_direct_mo120ap].groundMinReach`: `0.0` → `25.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `moloch/p26_moloch_direct_mo120ap` — `bossWeaponOverrides[moloch][p26_moloch_direct_mo120ap].maxRange`: `32.0` → `80`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `monster/p26_bastion_direct_b100` — `bossWeaponOverrides[monster][p26_bastion_direct_b100].groundMinReach`: `0.0` → `28.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `monster/p26_bastion_direct_b100` — `bossWeaponOverrides[monster][p26_bastion_direct_b100].maxRange`: `36.0` → `90`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `monster/p26_bastion_tiny_kornet_twin` — `bossWeaponOverrides[monster][p26_bastion_tiny_kornet_twin].groundMinReach`: `0.0` → `1.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `nuke_train/p26_nemesis_main_ne152` — `bossWeaponOverrides[nuke_train][p26_nemesis_main_ne152].groundMinReach`: `0.0` → `32.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `nuke_train/p26_nemesis_main_ne152` — `bossWeaponOverrides[nuke_train][p26_nemesis_main_ne152].maxRange`: `40.0` → `103`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `nuke_train/p26_nemesis_sec_boss_rockets` — `bossWeaponOverrides[nuke_train][p26_nemesis_sec_boss_rockets].groundMinReach`: `0.0` → `20.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `nuke_train/p26_nemesis_sec_boss_rockets` — `bossWeaponOverrides[nuke_train][p26_nemesis_sec_boss_rockets].maxRange`: `45.0` → `64`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `nuke_train/p26_nemesis_direct_ne125` — `bossWeaponOverrides[nuke_train][p26_nemesis_direct_ne125].groundMinReach`: `0.0` → `30.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `nuke_train/p26_nemesis_direct_ne125` — `bossWeaponOverrides[nuke_train][p26_nemesis_direct_ne125].maxRange`: `38.0` → `96`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `nyx/boss_railgun` — `bossWeaponOverrides[nyx][boss_railgun].groundMinReach`: `0.0` → `39.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `nyx/boss_railgun` — `bossWeaponOverrides[nyx][boss_railgun].maxRange`: `80.0` → `125`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `nyx/p26_leviathan_direct_lev127` — `bossWeaponOverrides[nyx][p26_leviathan_direct_lev127].groundMinReach`: `0.0` → `25.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `scylla/naval_130_twin` — `bossWeaponOverrides[scylla][naval_130_twin].groundMinReach`: `0.0` → `41.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `scylla/naval_130_twin` — `bossWeaponOverrides[scylla][naval_130_twin].maxRange`: `90.0` → `132`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `scylla/p26_leviathan_direct_lev127` — `bossWeaponOverrides[scylla][p26_leviathan_direct_lev127].groundMinReach`: `0.0` → `28.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `silver_bug/p26_icarus_sec_orbital_laser` — `bossWeaponOverrides[silver_bug][p26_icarus_sec_orbital_laser].groundMinReach`: `0.0` → `12.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `silver_bug/p26_icarus_sec_orbital_laser` — `bossWeaponOverrides[silver_bug][p26_icarus_sec_orbital_laser].maxRange`: `36.0` → `39`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `silver_bug/p26_icarus_main_ic_coil` — `bossWeaponOverrides[silver_bug][p26_icarus_main_ic_coil].groundMinReach`: `0.0` → `19.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `silver_bug/p26_icarus_main_ic_coil` — `bossWeaponOverrides[silver_bug][p26_icarus_main_ic_coil].maxRange`: `55.0` → `61`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `silver_bug/p26_icarus_direct_ic_laser` — `bossWeaponOverrides[silver_bug][p26_icarus_direct_ic_laser].groundMinReach`: `0.0` → `21.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `silver_bug/p26_icarus_direct_ic_laser` — `bossWeaponOverrides[silver_bug][p26_icarus_direct_ic_laser].maxRange`: `36.0` → `68`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `typhon/p26_typhon_sec_ty57` — `bossWeaponOverrides[typhon][p26_typhon_sec_ty57].groundMinReach`: `0.0` → `21.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `typhon/p26_typhon_sec_ty57` — `bossWeaponOverrides[typhon][p26_typhon_sec_ty57].maxRange`: `40.0` → `68`. Bù vùng chết bằng dải sử dụng tối thiểu khoảng 3,2×, không vượt 300m map width.
- `typhon/p26_typhon_direct_ty100` — `bossWeaponOverrides[typhon][p26_typhon_direct_ty100].groundMinReach`: `0.0` → `21.0`. Tầm tối thiểu phải theo hình học nòng/góc hạ; close-defense giữ riêng.
- `c5m03` — `campaign.missions[id=c5m03].fixedDeck.status`: `MAKE_LATER` → `READY`. Mọi fixed deck đã có vehicleIds/supportIds/specialRules cụ thể; chốt trạng thái sẵn sàng.
- `c6m03` — `campaign.missions[id=c6m03].fixedDeck.status`: `MAKE_LATER` → `READY`. Mọi fixed deck đã có vehicleIds/supportIds/specialRules cụ thể; chốt trạng thái sẵn sàng.
- `c6m14` — `campaign.missions[id=c6m14].fixedDeck.status`: `MAKE_LATER` → `READY`. Mọi fixed deck đã có vehicleIds/supportIds/specialRules cụ thể; chốt trạng thái sẵn sàng.
- `c7m16` — `campaign.missions[id=c7m16].fixedDeck.status`: `MAKE_LATER` → `READY`. Mọi fixed deck đã có vehicleIds/supportIds/specialRules cụ thể; chốt trạng thái sẵn sàng.
- `c9m12` — `campaign.missions[id=c9m12].fixedDeck.status`: `MAKE_LATER` → `READY`. Mọi fixed deck đã có vehicleIds/supportIds/specialRules cụ thể; chốt trạng thái sẵn sàng.
- `c10m11` — `campaign.missions[id=c10m11].fixedDeck.status`: `MAKE_LATER` → `READY`. Mọi fixed deck đã có vehicleIds/supportIds/specialRules cụ thể; chốt trạng thái sẵn sàng.
- `c10m12` — `campaign.missions[id=c10m12].fixedDeck.status`: `MAKE_LATER` → `READY`. Mọi fixed deck đã có vehicleIds/supportIds/specialRules cụ thể; chốt trạng thái sẵn sàng.
- `c12m03` — `campaign.missions[id=c12m03].fixedDeck.status`: `MAKE_LATER` → `READY`. Mọi fixed deck đã có vehicleIds/supportIds/specialRules cụ thể; chốt trạng thái sẵn sàng.
- `i1m01` — `campaign.missions[id=i1m01].fixedDeck.status`: `MAKE_LATER` → `READY`. Mọi fixed deck đã có vehicleIds/supportIds/specialRules cụ thể; chốt trạng thái sẵn sàng.
- `i2m01` — `campaign.missions[id=i2m01].fixedDeck.status`: `MAKE_LATER` → `READY`. Mọi fixed deck đã có vehicleIds/supportIds/specialRules cụ thể; chốt trạng thái sẵn sàng.
