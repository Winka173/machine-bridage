# 09_hieu_ung_am_thanh — Hiệu ứng và âm thanh

Bộ xuất dữ liệu Machine Brigade, commit 5d195554, ngày 2026-10-03. Sinh bởi `python Tools/export/export.py` (lượt 6): bảng in đúng ô của csv / xlsx; văn bản lấy từ tài liệu thiết kế (Tools/docs) và chuỗi trong game. Toàn văn: Machine_Brigade_Design_FULL_2026-10-03.md.

Clip âm thanh, bank thư viện, envelope, bảng loạt bắn nhanh, VFX theo bậc, lửa thân xe, hậu kỳ hình ảnh; xác vỡ / mixer (mã)

Mục trong file này: 20. Âm thanh; 20b. Hiệu ứng theo bậc và xác vỡ.

## 20. Âm thanh

Trạng thái: Một phần — chờ prompt xuat_luot6; cần đọc mã (NEED_CODE_CHECK) (sheet Am_thanh_mixer, Am_thanh_mau)

Nguồn dữ liệu: 09_hieu_ung_am_thanh/Am_thanh; 09_hieu_ung_am_thanh/Am_thanh_bank; 09_hieu_ung_am_thanh/Am_thanh_loat; 09_hieu_ung_am_thanh/Am_thanh_mixer; 09_hieu_ung_am_thanh/Am_thanh_thu_vien; 09_hieu_ung_am_thanh/Am_thanh_mau. Văn bản: Docs/Machine_Brigade_Design_Review.html (Tools/docs/build_doc.py) §16b. Hiệu ứng.

Hình và tiếng chỉ là hiển thị, không đổi kết quả mô phỏng. Hiệu ứng bậc được **vẽ lại** và chồng lên vụ nổ sẵn có của viên đạn (không vụ nổ nào nhỏ đi). Giới hạn chi tiết đầy đủ cùng lúc: T5 1, T4 3, T3 6; xa camera thì rút gọn (dưới 70 m đầy đủ, dưới 140 m 45%). Âm thanh tổng hợp bằng script (Tools/sfx/build_sfx.py, không dùng AI), mỗi phát ba lớp trộn sẵn: cơ cấu, tiếng nổ, đuôi vang. 32 kênh, từ 24 kênh bận thì tiếng mới dưới ưu tiên 60 chỉ chiếm kênh kém quan trọng nhất. Số liệu cảnh thử tải: Docs/balance/p34_stress_counts.json (cảnh `-mb-play -mb-lighthousebay -mb-p34stress`; FPS: NEED PROFILE).

#### Bắn, nổ và tiếng theo bậc

| Bậc | Phát bắn | Vụ nổ | Camera | Tiếng |
|---|---|---|---|---|
| T0 | Chớp mảnh của vũ khí | Nổ nhỏ (công thức Small) | — | shot_t0: tiếng giòn 35 ms, đuôi 0,08 s; súng nhỏ thành cụm đấu súng |
| T1 | Khói mỏng | Nổ nhỏ, đạn nổ trên không giữ chùm mảnh | — | shot_t1; cụm đấu súng từ khẩu thứ ba trong 20 m |
| T2 | Chớp vừa, khói ngắn | Cầu lửa nhỏ nóng, bụi và đất | — | shot_t2, blast_he_t2; ưu tiên 25-30 |
| T3 | Chớp lớn cháy lâu, cầu lửa đầu nòng, khói dài, vòng bụi, thân xe giật lùi | Cầu lửa vừa, cột bụi 5 cuộn, hố sáng nhỏ | — | shot_t3, blast_he_t3; ưu tiên 40 gần |
| T4 | Chớp rất lớn, hai cầu lửa, khói cuộn, vòng áp suất, mặt đất sáng; tàu: vòng nước và bụi nước | Cầu lửa cuộn lớn, cột 8 cuộn, mảnh văng, hai váy bụi; sóng xung kích trên rìa | Rung 0,22 (chỉ trên màn hình, trong 90 m) | shot_t4, blast_he_t4, tiếng rền dưới; ưu tiên 50 gần |
| T5 | Chớp sáng cả cảnh, khói rất dài, vòng áp suất đôi, hai vòng nước | Cầu lửa rất lớn, cột 10 cuộn thành mũ nấm nhỏ, mảnh xa, ba váy bụi, hố sáng 12 s; vòng trên lõi rồi rìa | Rung 0,6 | shot_t5, blast_he_t5; ưu tiên 60 (giữ 8 kênh cuối cho cảnh báo và T5 / boss) |

#### Xác vỡ theo lớp xe

Xác sống 30-45 s (boss 90 s), cháy 40% thời gian đó; tối đa khoảng 12 xác đầy đủ gần camera (Trung bình 9, Thấp 6), để lại vết cháy. Mảnh vỡ chỉ là hình: không có collider, không chặn đường hay tầm nhìn.

| Lớp | Cách vỡ |
|---|---|
| Xích (tăng; cả tàu hỏa) | Tháp pháo văng, thân cháy |
| Bánh lốp | Hai bánh văng xoáy, khung lật nghiêng hoặc ngửa trong 0,9 s |
| Xe tải | Hàng nổ dây chuyền 4-6 tiếng dọc thùng, thùng cháy |
| Pháo | Đạn trong xe nổ 6-9 tiếng, cột lửa 2-3,5 s, tháp văng một nửa số lần |
| Tiêm kích | Mất một cánh kéo lửa, xoáy ốc rơi |
| Trực thăng | Rotor đuôi văng, rotor chính bay mất, xoay ngày càng nhanh |
| Máy bay lớn | Mất cánh, động cơ cháy, rơi dài và nghiêng |
| Tàu | Nghiêng, gãy đôi (từ 24 m) và chìm; xuồng lật |
| Drone | Một tiếng nổ nhỏ, không còn gì |

#### Màn xem trước theo môi trường

Xem bắn, chi tiết xe / boss / tháp: đơn vị đứng đúng chỗ của nó. Cảnh tạm đúng loại cho tới khi tài sản biome, mặt nước và đường ray của prompt 33 được gộp vào. Bắn thử dùng đúng hiệu ứng và tiếng theo bậc; mỗi viên nổ hiện vòng rìa và lõi đúng cỡ vùng sát thương.

| Môi trường | Cảnh | Đơn vị |
|---|---|---|
| Mặt đất | Đất theo biome của bản đồ đang chọn (mặc định ôn đới) | Xe mặt đất, boss mặt đất |
| Biển | Mặt biển có sóng, mục tiêu đứng trên bờ phía trước | Tàu, xuồng, boss biển |
| Mép nước | Nửa sau trên nước, nửa trước trên bờ | Xe lội nước, đệm khí |
| Đường ray | Đoạn ray (đá ballast, tà vẹt, hai ray, ụ chặn) | Tàu hỏa, Juggernaut, Nemesis, Gungnir |
| Trên không | Bay vòng / lơ lửng, đất ở phía dưới | Máy bay, trực thăng, boss bay |
| Ô căn cứ | Bệ bê tông, viền tối, dấu góc | Tháp |
| Bờ biển | Pháo bờ biển trên bệ ở bờ, một tàu ngoài biển làm mục tiêu | Khẩu đội bờ biển |

Báo cáo chi tiết trong repo: `Docs/audio/metrics.md`; `Docs/audio/diagnosis.md`.

Sheet: 09_hieu_ung_am_thanh/Am_thanh — Âm thanh: clip (229 dòng, 14 cột)

| id | bank | nhom | duong_dan | do_dai_s | kenh | tan_so_mau_hz | nen | tac_gia | nguon_goc |
|---|---|---|---|---|---|---|---|---|---|
| Music/battle_1 |  | Music | Assets/MachineBrigade/Resources/Audio/Music/battle_1.ogg | 135.0 | 2 | 44100 | ogg | Armored Advance | Assets/MachineBrigade/Resources/Audio/Music/MUSIC_CREDITS.md |
| Music/battle_2 |  | Music | Assets/MachineBrigade/Resources/Audio/Music/battle_2.ogg | 132.414 | 2 | 44100 | ogg | Iron Rain | Assets/MachineBrigade/Resources/Audio/Music/MUSIC_CREDITS.md |
| Music/battle_3 |  | Music | Assets/MachineBrigade/Resources/Audio/Music/battle_3.ogg | 139.13 | 2 | 44100 | ogg | Air Superiority | Assets/MachineBrigade/Resources/Audio/Music/MUSIC_CREDITS.md |
| Music/boss |  | Music | Assets/MachineBrigade/Resources/Audio/Music/boss.ogg | 125.217 | 2 | 44100 | ogg | Colossus | Assets/MachineBrigade/Resources/Audio/Music/MUSIC_CREDITS.md |
| Music/defeat |  | Music | Assets/MachineBrigade/Resources/Audio/Music/defeat.ogg | 9.5 | 2 | 44100 | ogg | Defeat (stinger) | Assets/MachineBrigade/Resources/Audio/Music/MUSIC_CREDITS.md |
| Music/menu |  | Music | Assets/MachineBrigade/Resources/Audio/Music/menu.ogg | 108.0 | 2 | 44100 | ogg | Command Briefing | Assets/MachineBrigade/Resources/Audio/Music/MUSIC_CREDITS.md |
| Music/siege |  | Music | Assets/MachineBrigade/Resources/Audio/Music/siege.ogg | 115.556 | 2 | 44100 | ogg | Hold the Line | Assets/MachineBrigade/Resources/Audio/Music/MUSIC_CREDITS.md |
| Music/victory |  | Music | Assets/MachineBrigade/Resources/Audio/Music/victory.ogg | 8.621 | 2 | 44100 | ogg | Victory (stinger) | Assets/MachineBrigade/Resources/Audio/Music/MUSIC_CREDITS.md |
| autocannon/autocannon_1 | autocannon | shot | Assets/MachineBrigade/Resources/Audio/autocannon/autocannon… | 0.695 | 1 | 44100 | ogg | Fascinated Sound | The Gun Locker SFX Pack: "Automatic Cannon - MK44 - 03 - Si… |
| autocannon/autocannon_2 | autocannon | shot | Assets/MachineBrigade/Resources/Audio/autocannon/autocannon… | 0.695 | 1 | 44100 | ogg | Fascinated Sound | The Gun Locker SFX Pack: "Automatic Cannon - MK44 - 03 - Si… |
| autocannon/autocannon_3 | autocannon | shot | Assets/MachineBrigade/Resources/Audio/autocannon/autocannon… | 0.682 | 1 | 44100 | ogg | Fascinated Sound | The Gun Locker SFX Pack: "Automatic Cannon - MK44 - 03 - Si… |
| cannon/cannon_1 | cannon | shot | Assets/MachineBrigade/Resources/Audio/cannon/cannon_1.ogg | 1.5 | 1 | 44100 | ogg | Bluezone Corporation | Tank - Explosion Sound Effects: "Bluezone_BC0271_tank_artil… |
| cannon/cannon_2 | cannon | shot | Assets/MachineBrigade/Resources/Audio/cannon/cannon_2.ogg | 1.5 | 1 | 44100 | ogg | Pole Position Production | The Warfare Library: "warfare_t1b_cannon_firing_forest_dist… |
| cannon/cannon_3 | cannon | shot | Assets/MachineBrigade/Resources/Audio/cannon/cannon_3.ogg | 1.384 | 1 | 44100 | ogg | Pole Position Production | The Warfare Library: "warfare_t1b_cannon_firing_forest_dist… |
| click/click_1 |  | click | Assets/MachineBrigade/Resources/Audio/click/click_1.ogg | 0.092 | 1 | 44100 | ogg | Kenney (www.kenney.nl) | UI Audio pack ("click1.ogg") |

*15 / 229 dòng đầu: xem sheet 09_hieu_ung_am_thanh/Am_thanh; in 10 / 14 cột; 1 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 09_hieu_ung_am_thanh/Am_thanh_bank — Âm thanh: bank (87 dòng, 9 cột)

| id | so_clip | group | kept | row | size | variants |
|---|---|---|---|---|---|---|
| autocannon | 3 | shot | TRUE |  |  |  |
| blast_air_s1 | 2 | blast_air |  |  | s1 | 2 |
| blast_air_s2 | 2 | blast_air |  |  | s2 | 2 |
| blast_air_s3 | 2 | blast_air |  |  | s3 | 2 |
| blast_bomb | 3 | blast |  | blast | bomb | 3 |
| blast_he_s1 | 3 | blast |  | blast | s1 | 3 |
| blast_he_s2 | 3 | blast |  | blast | s2 | 3 |
| blast_he_s3 | 3 | blast |  | blast | s3 | 3 |
| blast_he_s4 | 3 | blast |  | blast | s4 | 3 |
| blast_he_s406 | 2 | blast |  | blast | s406 | 2 |
| blast_heat_s2 | 2 | blast_heat |  |  | s2 | 2 |
| blast_heat_s3 | 2 | blast_heat |  |  | s3 | 2 |
| blast_super | 2 | blast |  | blast | super | 2 |
| blast_thermo_s3 | 2 | blast_thermo |  |  | s3 | 2 |
| blast_thermo_s4 | 2 | blast_thermo |  |  | s4 | 2 |

*15 / 87 dòng đầu: xem sheet 09_hieu_ung_am_thanh/Am_thanh_bank.*

Sheet: 09_hieu_ung_am_thanh/Am_thanh_loat — Âm thanh: loạt bắn nhanh (7 dòng, 7 cột)

| id | bank | co | nhip_phat_s | so_phat |
|---|---|---|---|---|
| burst_s0_10 | burst_s0_10 | S0 | 10 | 3 |
| burst_s0_16 | burst_s0_16 | S0 | 16 | 5 |
| burst_s0_55 | burst_s0_55 | S0 | 55 | 18 |
| burst_s1_10 | burst_s1_10 | S1 | 10 | 3 |
| burst_s1_22 | burst_s1_22 | S1 | 22 | 7 |
| burst_s1_35 | burst_s1_35 | S1 | 35 | 12 |
| burst_s1_55 | burst_s1_55 | S1 | 55 | 18 |

Sheet: 09_hieu_ung_am_thanh/Am_thanh_mixer — Âm thanh: mixer (1 dòng, 5 cột)

| id | trang_thai | ghi_chu |
|---|---|---|
| chua_ap | NEED_CODE_CHECK | AudioDirector.cs / EffectsLimiter.cs (hằng trong mã; Docs/a… |

Sheet: 09_hieu_ung_am_thanh/Am_thanh_thu_vien — Âm thanh: thư viện (1 dòng, 8 cột)

| id | khoa | gia_tri_chu |
|---|---|---|
| note | note | Fix pass L7: the sound library (Tools/sfx/build_sfx.py); si… |

Sheet: 09_hieu_ung_am_thanh/Am_thanh_mau — Âm thanh: bản ghi mẫu (1 dòng, 5 cột)

| id | trang_thai | ghi_chu |
|---|---|---|
| chua_ap | CHUA_AP:prompt_xuat_luot6 | Docs/audio (bản trộn mẫu của Tools/sfx/render_mix.py) |

### 20b. Hiệu ứng theo bậc và xác vỡ

Trạng thái: Một phần — chờ prompt xuat_luot6; cần đọc mã (NEED_CODE_CHECK) (sheet VFX_vu_khi, Xac_vo)

Nguồn dữ liệu: 09_hieu_ung_am_thanh/VFX_bac; 09_hieu_ung_am_thanh/VFX_chay_than_xe; 09_hieu_ung_am_thanh/VFX_vu_khi; 09_hieu_ung_am_thanh/Xac_vo; 09_hieu_ung_am_thanh/Hau_ky_hinh_anh.

#### Ảnh hiệu ứng theo bậc (Unity, EffectShots.FxBatch)

*Ảnh chờ (pending): ảnh hiệu ứng nằm ngoài repo (Builds/effect_shots của máy chạy Unity, EffectShots.FxBatch). Chạy lại `python Tools/export/export.py --effect-shots <thư mục>` để chèn. Đơn vị khi có ảnh: m, thước so sánh Tăng chủ lực (main_battle_tank).*

Sheet: 09_hieu_ung_am_thanh/VFX_bac — VFX theo bậc (6 dòng, 21 cột)

| id | bac | rung_camera_dong_thoi | ban_dust_ring | ban_flash | ban_flash_life | ban_light | ban_pressure | ban_puff_life | ban_puff_life_arg0 |
|---|---|---|---|---|---|---|---|---|---|
| T0 | 0 | XEM_VFX_ngan_sach | 0 | 0 | 0 | 0 | 0 | zero |  |
| T1 | 1 | XEM_VFX_ngan_sach | 0 | 0 | 0 | 0 | 0 |  | 1.2 |
| T2 | 2 | XEM_VFX_ngan_sach | 0 | 1.2 | 0.1 | 0 | 0 |  | 1.8 |
| T3 | 3 | XEM_VFX_ngan_sach | 8 | 2.4 | 0.16 | 9 | 0 |  | 3.5 |
| T4 | 4 | XEM_VFX_ngan_sach | 16 | 3.6 | 0.24 | 16 | 7 |  | 5 |
| T5 | 5 | XEM_VFX_ngan_sach | 26 | 5 | 0.34 | 28 | 12 |  | 7 |

*in 10 / 21 cột; 9 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 09_hieu_ung_am_thanh/VFX_chay_than_xe — VFX: lửa thân xe (3 dòng, 14 cột)

| id | bodies | embers | low_tongues | power | reach_m | size | smoke_alpha | smoke_shade | smoke_size |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 1 | 0.5 | 1 | 2.8 | 4.5 | 1 | 0.6 | 0.34 | 1 |
| 1 | 1 | 1.1 | 1 | 4 | 6 | 1.2 | 0.74 | 0.16 | 1.15 |
| 2 | 2 | 1.8 | 2 | 5.2 | 7.5 | 1.45 | 0.8 | 0.06 | 1.35 |

*in 10 / 14 cột; 2 cột khác (và raw_json, nguon): xem sheet.*

Sheet: 09_hieu_ung_am_thanh/VFX_vu_khi — VFX theo vũ khí (1 dòng, 5 cột)

| id | trang_thai | ghi_chu |
|---|---|---|
| chua_ap | CHUA_AP:prompt_xuat_luot6 | ảnh chụp (lượt 6: images/09); bậc theo 01_vu_khi_dan/Vu_khi |

Sheet: 09_hieu_ung_am_thanh/Xac_vo — Xác vỡ (1 dòng, 5 cột)

| id | trang_thai | ghi_chu |
|---|---|---|
| chua_ap | NEED_CODE_CHECK | Assets/MachineBrigade/Scripts/Game/Effects/WreckClasses.cs… |

Sheet: 09_hieu_ung_am_thanh/Hau_ky_hinh_anh — Hậu kỳ hình ảnh (52 dòng, 8 cột)

| id | hieu_ung | thiet_lap | ghi_de | gia_tri | dimension |
|---|---|---|---|---|---|
| BattlefieldProfile.m_Enabled | BattlefieldProfile | m_Enabled |  | 1 |  |
| BattlefieldProfile.m_Name | BattlefieldProfile | m_Name |  | BattlefieldProfile |  |
| Bloom.active | Bloom | active |  | 1 |  |
| Bloom.clamp | Bloom | clamp | 1 | 6 |  |
| Bloom.dirtIntensity | Bloom | dirtIntensity | 0 | 0 |  |
| Bloom.dirtTexture | Bloom | dirtTexture | 0 | {fileID: 0} | 1 |
| Bloom.downscale | Bloom | downscale | 0 | 0 |  |
| Bloom.filter | Bloom | filter | 0 | 0 |  |
| Bloom.highQualityFiltering | Bloom | highQualityFiltering | 1 | 1 |  |
| Bloom.intensity | Bloom | intensity | 1 | 0.45 |  |
| Bloom.m_Enabled | Bloom | m_Enabled |  | 1 |  |
| Bloom.m_Name | Bloom | m_Name |  | Bloom |  |
| Bloom.maxIterations | Bloom | maxIterations | 0 | 6 |  |
| Bloom.scatter | Bloom | scatter | 1 | 0.6 |  |
| Bloom.skipIterations | Bloom | skipIterations | 1 | 0 |  |

*15 / 52 dòng đầu: xem sheet 09_hieu_ung_am_thanh/Hau_ky_hinh_anh.*

## Các sheet khác của file

Mọi sheet chưa in ở mục trên (sheet input_<tên> là bản chép từ file khác, không in lại).

### Am_thanh_envelope

Trạng thái: Đã áp

Nguồn dữ liệu: 09_hieu_ung_am_thanh/Am_thanh_envelope.

Sheet: 09_hieu_ung_am_thanh/Am_thanh_envelope — Âm thanh: envelope (216 dòng, 6 cột)

| id | clip | so_mau | rms_x1000 |
|---|---|---|---|
| #1 |  |  | # Fix pass L7: each clip's RMS at 50 Hz (x1000), by clip na… |
| autocannon_1 | autocannon_1 | 34 | 270;403;117;264;31;27;30;20;46;27;15;15;18;18;18;22;17;22;2… |
| autocannon_2 | autocannon_2 | 34 | 265;396;116;262;32;27;29;216;401;185;268;42;33;32;202;398;2… |
| autocannon_3 | autocannon_3 | 34 | 245;411;200;272;90;29;29;28;19;45;31;215;413;235;278;104;37… |
| blast_air_s1_1 | blast_air_s1_1 | 59 | 372;120;71;99;109;161;115;75;55;65;55;111;86;46;49;39;34;34… |
| blast_air_s1_2 | blast_air_s1_2 | 62 | 350;110;86;93;143;126;113;88;82;66;56;57;128;60;41;38;46;41… |
| blast_air_s2_1 | blast_air_s2_1 | 89 | 326;224;155;179;175;147;147;133;135;103;104;113;123;137;127… |
| blast_air_s2_2 | blast_air_s2_2 | 94 | 323;208;195;181;162;184;176;172;131;139;128;128;109;111;100… |
| blast_air_s3_1 | blast_air_s3_1 | 130 | 324;329;236;246;200;201;175;184;188;172;163;157;160;167;170… |
| blast_air_s3_2 | blast_air_s3_2 | 133 | 307;291;257;203;232;230;205;210;196;236;228;188;177;161;122… |
| blast_bomb_1 | blast_bomb_1 | 296 | 364;439;460;421;436;397;394;413;411;392;364;320;317;335;308… |
| blast_bomb_2 | blast_bomb_2 | 296 | 435;458;434;408;402;453;434;395;389;378;363;397;418;298;243… |
| blast_bomb_3 | blast_bomb_3 | 294 | 444;446;416;437;465;389;377;369;406;355;390;301;347;380;356… |
| blast_he_s1_1 | blast_he_s1_1 | 58 | 208;172;112;184;176;165;126;147;133;112;104;103;96;127;130;… |
| blast_he_s1_2 | blast_he_s1_2 | 59 | 197;164;174;183;158;153;127;169;147;150;131;139;113;98;87;7… |

*15 / 216 dòng đầu: xem sheet 09_hieu_ung_am_thanh/Am_thanh_envelope.*

### Am_thanh_so_do

Trạng thái: Đã áp

Nguồn dữ liệu: 09_hieu_ung_am_thanh/Am_thanh_so_do.

Sheet: 09_hieu_ung_am_thanh/Am_thanh_so_do — Âm thanh: số đo (221 dòng, 18 cột)

| id | do_dai_s | lufs | lufs_mmax | dinh_db | dinh_that_db | duoi_150hz_pct | duoi_s | keng_noi_db | keng_tat_s |
|---|---|---|---|---|---|---|---|---|---|
| autocannon/autocannon_1 | 0.695 | -21.5 | -18.6 | -0.9 | -0.8 | 44.3 | 0.56 | 4.2 | 0.116 |
| autocannon/autocannon_2 | 0.695 | -15.5 | -14.0 | -0.9 | -0.9 | 43.9 | 0.46 | 3.9 | 0.035 |
| autocannon/autocannon_3 | 0.682 | -17.1 | -15.4 | -1.0 | -1.0 | 49.6 | 0.34 | 4.9 | 0.035 |
| cannon/cannon_1 | 1.5 | -16.7 | -14.5 | -1.6 | -1.6 | 70.3 | 0.82 | 3.4 | 0.081 |
| cannon/cannon_2 | 1.5 | -20.6 | -15.6 | -1.0 | -1.0 | 53.9 | 1.1 | 2.3 | 0.139 |
| cannon/cannon_3 | 1.384 | -22.5 | -16.5 | -0.9 | -0.9 | 45.5 | 1.11 | 0.0 | 0.0 |
| click/click_1 | 0.092 | -21.0 | -21.0 | -1.7 | -1.3 | 32.5 | 0.03 | 8.1 | 0.035 |
| click/click_2 | 0.065 | -23.8 | -23.8 | -1.0 | -1.0 | 1.3 | 0.04 | 0.0 | 0.0 |
| collapse/collapse_1 | 3.697 | -19.2 | -15.1 | -1.0 | -0.3 | 89.4 | 1.61 | 4.4 | 0.023 |
| collapse/collapse_2 | 3.853 | -20.1 | -15.5 | -1.0 | -1.0 | 57.5 | 2.57 | 0.4 | 0.116 |
| debris/debris_1 | 0.805 | -20.3 | -17.8 | -0.9 | -0.8 | 4.4 | 0.55 | 5.1 | 0.058 |
| debris/debris_2 | 0.853 | -20.5 | -16.5 | -1.6 | -1.5 | 1.4 | 0.71 | 3.8 | 0.07 |
| debris/debris_3 | 0.954 | -22.0 | -18.1 | -1.0 | -0.9 | 2.5 | 0.88 | 4.5 | 0.07 |
| drums_loop/drums_loop_1 | 7.385 | -15.7 | -12.2 | -1.0 | -1.0 | 97.9 | 5.27 | 0.0 | 0.0 |
| explosion_huge/explosion_huge_1 | 5.0 | -16.8 | -13.4 | -1.0 | -1.0 | 74.9 | 4.16 | 2.5 | 0.139 |

*15 / 221 dòng đầu: xem sheet 09_hieu_ung_am_thanh/Am_thanh_so_do; in 10 / 18 cột; 6 cột khác (và raw_json, nguon): xem sheet.*

### Am_thanh_so_do_bac

Trạng thái: Đã áp

Nguồn dữ liệu: 09_hieu_ung_am_thanh/Am_thanh_so_do_bac.

Sheet: 09_hieu_ung_am_thanh/Am_thanh_so_do_bac — Âm thanh: bảng theo bậc cỡ (15 dòng, 13 cột)

| id | bac_co | vai | ten | lufs_mmax | lufs | duoi_150hz_pct | duoi_s | bank | tang_deu |
|---|---|---|---|---|---|---|---|---|---|
| blast/bomb | bomb | blast | bombs | -11.03 | -15.33 | 66.2 | 5.4 | blast_bomb | TRUE |
| blast/s0 | s0 | blast | <= 14.5 mm | -24.23 | -24.23 | 12.7 | 0.22 | hit_ground_light |  |
| blast/s1 | s1 | blast | 20-40 mm | -18.1 | -22.33 | 31.07 | 0.95 | blast_he_s1 | TRUE |
| blast/s2 | s2 | blast | 57-105 mm | -15.6 | -21.0 | 45.53 | 1.72 | blast_he_s2 | TRUE |
| blast/s3 | s3 | blast | 120-155 mm | -13.6 | -19.4 | 55.63 | 2.44 | blast_he_s3 | TRUE |
| blast/s4 | s4 | blast | 203-240 mm | -12.07 | -18.47 | 61.3 | 4.2 | blast_he_s4 | TRUE |
| blast/s406 | s406 | blast | big rockets / >= 406 mm | -10.05 | -13.55 | 71.0 | 7.12 | blast_he_s406 | TRUE |
| blast/super | super | blast | super weapons | -9.1 | -12.2 | 78.35 | 10.65 | blast_super | TRUE |
| shot/s0 | s0 | shot | <= 14.5 mm | -28.05 | -28.05 | 1.75 | 0.31 | shot_s0 |  |
| shot/s1 | s1 | shot | 20-40 mm | -23.77 | -26.35 | 12.0 | 0.49 | shot_s1 | TRUE |
| shot/s2 | s2 | shot | 57-105 mm | -16.6 | -21.93 | 39.13 | 1.41 | shot_s2 | TRUE |
| shot/s3 | s3 | shot | 120-155 mm | -14.57 | -21.17 | 53.63 | 2.04 | shot_s3 | TRUE |
| shot/s4 | s4 | shot | 203-240 mm | -13.1 | -19.77 | 61.27 | 2.92 | shot_s4 | TRUE |
| shot/s406 | s406 | shot | big rockets / >= 406 mm | -11.6 | -18.05 | 70.05 | 4.67 | shot_s406 | TRUE |
| shot/super | super | shot | super weapons | -10.6 | -15.15 | 75.3 | 7.26 | shot_super | TRUE |

### VFX_ngan_sach

Trạng thái: Đã áp

Nguồn dữ liệu: 09_hieu_ung_am_thanh/VFX_ngan_sach.

Sheet: 09_hieu_ung_am_thanh/VFX_ngan_sach — VFX: ngân sách (8 dòng, 17 cột)

| id | loai | toan_chi_tiet_toi_da | trong_so | ban_s | rung_tai_no | tran_trong_so | he_so_rung_khi_ban | gioi_han_ma | yeu_cau |
|---|---|---|---|---|---|---|---|---|---|
| T0 | bac |  | 0.0 | 2.5 | 0.0 | 12.0 | 0.5 |  |  |
| T1 | bac |  | 0.0 | 2.5 | 0.0 | 12.0 | 0.5 |  |  |
| T2 | bac |  | 0.0 | 2.5 | 0.0 | 12.0 | 0.5 |  |  |
| T3 | bac | 6.0 | 1.0 | 2.5 | 0.0 | 12.0 | 0.5 |  |  |
| T4 | bac | 3.0 | 3.0 | 4.0 | 0.22 | 12.0 | 0.5 |  |  |
| T5 | bac | 1.0 | 6.0 | 6.0 | 0.6 | 12.0 | 0.5 |  |  |
| hat_tong | hat_tong |  |  |  |  |  |  | 11756.0 |  |
| khoi_lon | khoi_lon |  |  |  |  |  |  | 3.0 | 3.0 |

*in 10 / 17 cột; 5 cột khác (và raw_json, nguon): xem sheet.*

### VFX_ngan_sach_hat

Trạng thái: Đã áp

Nguồn dữ liệu: 09_hieu_ung_am_thanh/VFX_ngan_sach_hat.

Sheet: 09_hieu_ung_am_thanh/VFX_ngan_sach_hat — VFX: trần hạt mỗi bộ phát (9 dòng, 6 cột)

| id | tep | dong | hat_toi_da |
|---|---|---|---|
| Game/Effects/Emitters.cs:83 | Game/Effects/Emitters.cs | 83 | 1500.0 |
| Game/Effects/Emitters.cs:98 | Game/Effects/Emitters.cs | 98 | 2400.0 |
| Game/Effects/Emitters.cs:116 | Game/Effects/Emitters.cs | 116 | 200.0 |
| Game/Effects/ExplosionEffect.cs:282 | Game/Effects/ExplosionEffect.cs | 282 | 3000.0 |
| Game/Effects/NightLights.cs:47 | Game/Effects/NightLights.cs | 47 | 300.0 |
| Game/Effects/NightLights.cs:162 | Game/Effects/NightLights.cs | 162 | 8.0 |
| Game/Effects/ParticleBuilder.cs:56 | Game/Effects/ParticleBuilder.cs | 56 | 128.0 |
| Game/Effects/StrikeEffects.cs:484 | Game/Effects/StrikeEffects.cs | 484 | 220.0 |
| Game/Effects/TrackMarks.cs:22 | Game/Effects/TrackMarks.cs | 22 | 4000.0 |
