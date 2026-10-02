# C11: Boss Hunt after the Gungnir becomes a main boss (prompt 29)

- **The pools.** `BossHunts.Story` (Game) built each hunt boss's "main" flag from the chapter's slot only
  (`id == chapter.Main`). Chapter 11 lists `rail_supergun` among its minis (campaign.json; the mission c11m05 stays as
  it is), so the Gungnir would have stayed in the mini pool. Changed: a boss of the main rank counts as main wherever
  it is slotted (`id == chapter.Main || def.Rank == BossRank.Main`). The pools become 17 mains and 24 minis (the sheet
  "Gungnir": 16 -> 17, 25 -> 24). `BossHunt.Weekly` draws 3 mains and 7 minis from those pools (unchanged code), so
  the weekly hunt keeps its 3-2-2 shape.
- **Its health.** The main bosses' table by chapter (DECISIONS 26AB A1-A3, "P x t x 0.6" was how the table was built)
  gives chapter 11 = 133,350 shown (Daedalus). Data hp = 133,350 / bosses' toughness 0.85 = 156,882, to the hundred as
  Daedalus's data: **156,900** (shown 133,365). The manifest row's "bossHp(chapter=11, tier=major)" is that formula.
- In a hunt the boss's health is P x t x 0.6 x m (prompt 26 E1) on top; nothing changes there.
