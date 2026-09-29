# Machine Brigade glossary (English / Vietnamese)

Prompt 21 J2. Every translation uses these terms. The text tables live in `Assets/MachineBrigade/Scripts/Game/Hud/`
(`Strings.cs`, `CampaignText.cs`, `BossText.cs`, `BigAttackText.cs`, `OrbitalText.cs`, `GuideText.cs`, `UnitText.cs`,
`NameText.cs`); the key named in each table is the source of truth, and a change there changes every screen.

## Voice

- Tight military voice in both languages: short sentences, verbs first, no filler, numbers with their units.
- English: British spelling (armour, harbour, metres), sentence case for buttons and labels, title case for boss
  subtitles ("Icarus · Orbital Spacecraft").
- Vietnamese: sentence case; loanwords written the Vietnamese way (rốc-két, la-de, vonfram, sô-na, mô-đun); no English
  word except the kept names below.
- Each general keeps the voice of his or her lines in both languages: translate the meaning and the tone of a line,
  not its words. The radio's lines name their speaker first ("Raven: ...", "Chỉ huy: ...").

## Names (J1, J5)

- Proper names are the same in both languages: bosses (Behemoth, Icarus, Leviathan...), people and their call signs
  (Viktor Varga "Anvil", Ilya Orlov "Winter", Magnus Kessler "Maelstrom", Elara Sen "Queen", Kasimir Wolff "Raven",
  Lucien Aurel "Sol", Lý Hàn "Titan", Trần Khải "Iron", Diều Hâu "Hawk"), the faction (Hegemon), the equipment brands
  (Kestrel Dynamics...), and the real weapons and vehicles the units are modelled on (T-90, Ka-52, Grad, Patriot, TOS-1A,
  Lancet, GBU...).
  `NameText.Kept` lists them; the language scans allow them in both languages.
- The story's Vietnamese names are written `{@id}` in every text and filled from `NameText.Table`, so prompt 22 can
  swap them in one place: `{@dieuhau}` Diều Hâu, `{@lephong}` Lê Phong, `{@lyhan}` Lý Hàn, `{@trankhai}` Trần Khải,
  `{@khai}` Khải, `{@linh}` Linh, `{@mai}` Mai, `{@quaden}` Quạ Đen, `{@lamthanh}` Lam Thành, `{@bagia}` Bà Già.
- A boss's subtitle is translated: `Icarus · Orbital Spacecraft` / `Icarus · Phi thuyền quỹ đạo`.

## Armour and penetration

| English | Vietnamese |
|---|---|
| Unarmoured / Thin / Medium / Thick / Very thick armour (levels 0-4) | Không giáp / Giáp mỏng / Giáp vừa / Giáp dày / Giáp rất dày |
| Aircraft (armour kind) · Structure | Máy bay · Công trình |
| Front · Side · Rear · Roof (faces) | Mặt trước · Hông · Mặt sau · Nóc |
| Very low / Low / Medium / High / Very high penetration | Xuyên rất thấp / Xuyên thấp / Xuyên vừa / Xuyên cao / Xuyên rất cao |
| Pierces well · Pierces poorly · Does not pierce (✓ ~ ✕) | Xuyên tốt · Xuyên kém · Không xuyên |
| Reactive armour · Cage armour · APS · Flares · Smoke · Jammer | Giáp phản ứng nổ · Lồng chắn · APS · Pháo sáng · Màn khói · Gây nhiễu |

## Damage types

| English | Vietnamese |
|---|---|
| Kinetic | Động năng |
| Shaped charge | Nổ lõm |
| High explosive | Nổ mạnh |
| Fire | Lửa |
| Fragmentation | Mảnh |
| Energy | Năng lượng |
| Thermobaric · Top attack · Guided · Splash | Nhiệt áp · Đánh nóc · Dẫn đường · Nổ lan |

## Branches and classes

| English | Vietnamese |
|---|---|
| Armour · Light · Artillery · Air · Support (the five branches) | Thiết giáp · Xe nhẹ · Pháo binh · Không quân · Hỗ trợ |
| Scouts · Light armour · Tanks · Heavy tanks · Tank hunters | Trinh sát · Xe bọc thép nhẹ · Xe tăng · Tăng hạng nặng · Diệt tăng |
| Artillery · Anti-air · Support · Helicopters · Aircraft | Pháo binh · Phòng không · Hỗ trợ · Trực thăng · Máy bay |
| Fortifications · Bosses | Công sự · Boss |
| Boss · Main boss · Mini boss · Elite | Boss · Boss chủ lực · Mini boss · Tinh nhuệ |
| Tower · Structure · Module · Headquarters (HQ) | Tháp · Công trình · Mô-đun · Sở chỉ huy (SCH) |

## Base slots

| English | Vietnamese |
|---|---|
| Small · Medium · Large · Utility slot | Ô nhỏ · Ô vừa · Ô lớn · Ô tiện ích |
| HQ level | Cấp sở chỉ huy (SCH cấp) |
| Outpost | Tiền đồn |

## Modes and difficulties

| English | Vietnamese |
|---|---|
| Campaign | Chiến dịch |
| Conquest · Deathmatch · King of the Hill · Assault · Defend | Giữ cứ điểm · Tử chiến · Vua đồi · Công phá · Phòng thủ |
| Siege · Survival · Endless · Weekly fortress · Boss Hunt | Công thành · Sinh tồn · Vô tận · Pháo đài tuần · Săn trùm |
| Sandbox (prompt 21 part 1) | Sa bàn |
| Easy · Normal · Hard · Very hard | Dễ · Thường · Khó · Cực khó |

## Sandbox

| English | Vietnamese |
|---|---|
| Blue side · Red side | Phe Xanh · Phe Đỏ |
| Scenario · Seed · Tick | Kịch bản · Mã trận · Nhịp |
| Replay · Test · Duel · A/B comparison | Bản ghi trận · Bài kiểm tra · Đấu tay đôi · So sánh A/B |
| Overlay · Hardpoint · Test range | Lớp kiểm tra · Ô đặt tháp · Bãi thử |
| Common · Uncommon · Rare · Epic · Legendary | Thường · Khá · Hiếm · Sử thi · Huyền thoại |

## States

| English | Vietnamese |
|---|---|
| Out of ammo · Running low · Reloading | Hết đạn · Sắp hết đạn · Đang nạp đạn |
| Ready · Ready in 12 s · Cooling down | Sẵn sàng · Sẵn sàng sau 12 giây · Đang hồi chiêu |
| Dug in · Deploying | Đã triển khai · Xuất kích |
| Locked · In use · Empty | Chưa mở · Đang dùng · Trống |
| Captured · Lost (a point) | Đã chiếm · Mất |

## Units and numbers

| | English | Vietnamese |
|---|---|---|
| Thousands, decimals | 184,172 · 0.75 | 184.172 · 0,75 |
| Seconds, minutes | 12 s · 3 min | 12 giây · 3 phút |
| Metres, millimetres | 400 m · 120 mm | 400 m · 120 mm |
| Command points, percent | 12 CP · 25% | 12 CP · 25% |
| Rates on the HUD | +1.4/s | +1,4/s |
| Coins, blueprints | 1 coin, 2 coins · 1 blueprint | 1 xu, 2 xu · 1 bản thiết kế |

English counts use the plural form of the tables, `{count|# tank|# tanks}`; Vietnamese has none.

## Acts and chapters

| | English | Vietnamese |
|---|---|---|
| Act I | The Landing | Đổ bộ |
| Act II | The Counterattack | Phản công |
| Act III | Betrayal | Phản bội |
| Act IV | Silver Sky | Bầu trời bạc |
| Chapter 1 | Coast of Fire | Bờ biển lửa |
| Chapter 2 | Black Gold | Vàng đen |
| Chapter 3 | The Long Winter | Mùa đông dài |
| Chapter 4 | Steel Harbour | Cảng thép |
| Chapter 5 | Jungle Fire | Lửa rừng |
| Chapter 6 | Counterstrike | Tổng phản công |
| Chapter 7 | The Capital | Thủ đô |
| Chapter 8 | Underground | Lòng đất |
| Chapter 9 | Rough Seas | Biển động |
| Chapter 10 | War in the Air | Chiến tranh trên không |
| Chapter 11 | The Orbital Gateway | Cửa ngõ quỹ đạo |
| Chapter 12 | The Icarus Launch Site | Bãi phóng Icarus |

## Maps (J4)

One name per map and language, on every screen and in the story (`map.<id>` in `Strings.cs`):

| Map | English | Vietnamese |
|---|---|---|
| ashfield | Ashfield | Đồng Tro |
| dunebreak | Dunebreak | Đồi Cát |
| frostpeak | Frostpeak | Đỉnh Sương Giá |
| ironport | Ironport | Cảng Thép |
| redrock | Redrock Canyon | Hẻm Đá Đỏ |
| whiteout | Whiteout Pass | Đèo Bão Tuyết |
| greenvale | Greenvale | Lũng Xanh |
| rustyard | Rust Yard | Bãi Sắt Gỉ |
| emberridge | Ember Ridge | Sườn Dung Nham |
| junglepass | Jungle Pass | Đèo Rừng Rậm |
| skyhold | Skyhold Airbase | Căn Cứ Tầng Mây |
| metrocity | Metro City | Đô Thành |
| landingbeach | Landing Beach | Bãi Đổ Bộ |
| hydrodam | Hydro Dam | Đập Thủy Điện |
| capital | Capital | Thủ Đô |
| launchsite | Icarus Launch Site | Bãi Phóng Icarus |
| saltflat | Salt Flats | Sa Mạc Muối |
| borderbridge | Border Bridge | Cầu Biên Giới |
| swamp | Swamp | Đầm Lầy |
| coralisles | Coral Isles | Quần Đảo San Hô |
| lighthousebay | Lighthouse Bay | Vịnh Hải Đăng |
| openpit | Open-Pit Mine | Mỏ Lộ Thiên |
| orbitalgate | Orbital Gateway | Cửa Ngõ Quỹ Đạo |

The story names the capital city itself Lam Thành (`{@lamthanh}`), a proper name.
