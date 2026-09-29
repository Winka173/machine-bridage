# Machine Brigade glossary (English / Vietnamese)

Prompt 21 J2. Every translation uses these terms. The text tables live in `Assets/MachineBrigade/Scripts/Game/Hud/`
(`Strings.cs`, `CampaignText.cs`, `BossText.cs`, `BigAttackText.cs`, `OrbitalText.cs`, `GuideText.cs`, `UnitText.cs`,
`NameText.cs`); the key named in each table is the source of truth, and a change there changes every screen.

## Voice

- Tight military voice in both languages: short sentences, verbs first, no filler, numbers with their units.
- English: British spelling (armour, harbour, metres), sentence case for buttons and labels, title case for boss
  subtitles ("Icarus · Orbital Spacecraft"). A proper name keeps the spelling it was given ("7th Mechanized Brigade",
  "Iron Harbor", prompt 22).
- Vietnamese: sentence case; loanwords written the Vietnamese way (rốc-két, la-de, vonfram, sô-na, mô-đun); no English
  word except the kept names below.
- Each general keeps the voice of his or her lines in both languages: translate the meaning and the tone of a line,
  not its words. The radio's lines name their speaker first ("Raven: ...", "Chỉ huy: ...").

## Names (J1, J5, prompt 22 A)

- No proper name is Vietnamese, in either language: people, call signs, factions, places, maps, chapters and acts
  (prompt 22 A). The descriptions, the bosses' subtitles, the radio and the briefings are translated.
- Proper names are the same in both languages: bosses (Behemoth, Icarus, Leviathan, Morrigan...), people and their
  call signs, the factions (Hegemon, the Meridian Accord and its 7th Mechanized Brigade, "Machine Brigade"), the region
  (the Meridian Coast) and its capital (Veyra), the equipment brands (Kestrel Dynamics...), and the real weapons and
  vehicles the units are modelled on (T-90, Ka-52, Grad, Patriot, TOS-1A, Lancet, GBU...).
  `NameText.Kept` lists them; the language scans allow them in both languages.
- Our side: Colonel Marcus Kade "Iron" / Đại tá Marcus Kade; Engineer Mara Lind / Kỹ sư Mara Lind; Lieutenant Jonah
  Reyes "Hawk" / Trung úy Jonah Reyes; Captain Nadia Kerr / Đại úy Nadia Kerr; General Roland Thorne "Titan" / Tướng
  Roland Thorne; Major Brandt "Bulwark"; and the officers who join on the way: Major Otto Brenn "Ledger", Captain Tomas
  Adler "Flag", Captain Kaia Mendez "Rush", Major Piet Dahl "Longshot", Captain Ines Varro "Tide", Sergeant Major Lena
  Quist "Magpie" (Thượng sĩ), Colonel August Reyn "Crown", Captain Selma Okoye "Vault".
- Hegemon: General Viktor Varga "Anvil", Colonel Ilya Orlov "Winter", Admiral Magnus Kessler "Maelstrom", Dr Elara
  Venn "Queen" (Tiến sĩ Elara Venn), Kasimir Wolff "Raven" (never "Quạ Đen"), Director Lucien Aurel "Sol".
- The tokens of prompt 21 stay in the texts and read the new names from `NameText.Table`: `{@khai}` Kade,
  `{@trankhai}` Marcus Kade, `{@mai}` Mara, `{@dieuhau}` Hawk, `{@lephong}` Jonah Reyes, `{@linh}` Nadia, `{@lyhan}`
  Thorne, `{@quaden}` Raven, `{@lamthanh}` Veyra, `{@bagia}` Matilda (the Behemoth Mara restarts). New texts write the
  names as they are.
- A call sign is "biệt danh" in Vietnamese ("biệt danh Iron"). "The Accord" is "Accord" ("quân Accord").
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

Prompt 22: English in both languages, the act's word translated ("Hồi I · Landfall"); an interlude is "Interlude II" /
"Chương xen kẽ II"; a mission of one "II-3".

| | English and Vietnamese |
|---|---|
| Act I | Landfall |
| Act II | Counteroffensive |
| Act III | Betrayal |
| Act IV | Silver Sky |
| Chapter 1 | Coast of Fire |
| Chapter 2 | Black Gold |
| Chapter 3 | The Long Winter |
| Interlude I | Blueprints |
| Chapter 4 | Iron Harbor |
| Chapter 5 | Burning Canopy |
| Chapter 6 | Counterstrike |
| Interlude II | The Queen's Choice |
| Chapter 7 | Veyra |
| Chapter 8 | Underworld |
| Chapter 9 | Rough Water |
| Interlude III | Hawk and Raven |
| Chapter 10 | War in the Sky |
| Chapter 11 | Skygate |
| Chapter 12 | Helion |

## Maps (J4, prompt 22 A)

One name per map, the same in both languages, on every screen and in the story (`map.<id>` in `Strings.cs`; the ids
stay):

| Map | Name |
|---|---|
| ashfield | Ashfield |
| dunebreak | Dunebreak |
| frostpeak | Frostpeak |
| ironport | Ironport |
| redrock | Red Rock |
| whiteout | Whiteout Pass |
| greenvale | Greenvale |
| rustyard | Rust Yard |
| emberridge | Emberridge |
| junglepass | Jungle Pass |
| skyhold | Skyhold |
| metrocity | Metro City |
| landingbeach | Stormbeach |
| hydrodam | Hollow Dam |
| capital | Veyra |
| launchsite | Helion Launch Complex |
| saltflat | Salt Flats |
| borderbridge | Border Crossing |
| swamp | Mirewood |
| coralisles | Coral Keys |
| lighthousebay | Beacon Bay |
| openpit | Deepcut Mine |
| orbitalgate | Skygate Array |
| foundry | Foundry (prompt 22 E) |
| veyra_old_quarter | Veyra Old Quarter (prompt 22 E) |

The capital city is Veyra, like its battlefield; "thủ đô" / "the capital" stay the common words.
