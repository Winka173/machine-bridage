using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 22, pass 1: no proper name of the old story in any text, in either language (A); twelve chapters of 9 to 18
    /// main missions and three interludes, no two missions in a row alike, each interlude with the act before it, a save of
    /// the twelve chapters of ten moved on (B); the story's beats and short radio lines (C).
    /// </summary>
    public class Prompt22StoryTests
    {
        [TearDown]
        public void Restore()
        {
            Campaign.Release = null;
            PlayerProfile.Load();
        }

        // ------------------------------------------------------------------ A: names

        /// <summary>The old proper names, Vietnamese and English (the places, the people, the faction, the chapters and acts).</summary>
        private static readonly string[] OldNames =
        {
            "Lũng Xanh", "Hẻm Đá Đỏ", "Đèo Bão Tuyết", "Bãi Sắt Gỉ", "Sườn Dung Nham", "Đèo Rừng Rậm", "Thành Phố Metro", "Thành phố Metro", "Đô Thành",
            "Bãi Đổ Bộ", "Đập Thủy Điện", "Thủ Đô", "Vịnh Hải Đăng", "Quần Đảo San Hô", "Sa Mạc Muối", "Cầu Biên Giới", "Đầm Lầy", "Mỏ Lộ Thiên",
            "Cửa Ngõ Quỹ Đạo", "Cửa ngõ quỹ đạo", "cửa ngõ quỹ đạo", "Bãi Phóng", "Đồng Tro", "Đồi Cát", "Đỉnh Sương Giá", "Cảng Thép", "Căn Cứ Tầng Mây",
            "Lam Hải", "Lam Thành", "Liên minh", "duyên hải", "Duyên hải", "Lữ đoàn Cơ giới", "Lữ Đoàn Cơ Giới", "Lữ Đoàn Máy", "Phương Bắc", "Đêm Thép", "Bảo hộ",
            "Quạ Đen", "Bà Già", "Trần Khải", "Lý Hàn", "Diều Hâu", "Lê Phong",
            "Bờ biển lửa", "Vàng đen", "Mùa đông dài", "Cảng thép", "Lửa rừng", "Tổng phản công", "Lòng đất", "Biển động", "Chiến tranh trên không", "Bầu trời bạc",
            "Landing Beach", "Hydro Dam", "Lighthouse Bay", "Orbital Gateway", "Orbital Gate", "orbital gate", "Icarus Launch Site", "Open-Pit Mine", "Redrock",
            "Ember Ridge", "Skyhold Airbase", "Coral Isles", "Border Bridge", "Coastal Alliance", "Lam Hai", "Northern Army", "Night of Steel", "Protectorate",
            "Dr Sen", "Elara Sen", "Steel Harbour", "Jungle Fire", "Rough Seas", "The Counterattack",
        };

        /// <summary>The old names that are words on their own: whole words only ("Khai hỏa", open fire, is Vietnamese).</summary>
        private static readonly Regex OldWords = new(@"(?<![\p{L}@{])(Sen|Linh|Mai|Khải|Khai(?! hỏa)|Hùng|Alliance)(?!\p{L})");

        [Test]
        public void NoTextUsesAnOldProperName()
        {
            var bad = new List<string>();
            foreach (var (key, en, vi, table) in Strings.Entries)
                foreach (var (lang, text) in new[] { ("en", en), ("vi", vi) })
                {
                    foreach (var name in OldNames)
                        if (text.Contains(name)) bad.Add($"{table} {key} ({lang}): {name}");
                    if (OldWords.Match(text) is { Success: true } m) bad.Add($"{table} {key} ({lang}): {m.Value}");
                }
            foreach (var (key, (en, vi)) in NameText.Table)
                if (OldNames.Any(n => en.Contains(n) || vi.Contains(n)) || OldWords.IsMatch(en + " " + vi)) bad.Add($"{key}: {en} / {vi}");
            Assert.IsEmpty(bad, string.Join("\n", bad.Take(60)));
            // The ids stay (a save, a record, a text key); the names are the spec's, the same in both languages.
            Assert.AreEqual(("Thorne", "Thorne"), NameText.Table["name.lyhan"]);
            Assert.AreEqual(("Raven", "Raven"), NameText.Table["name.quaden"]);
            Assert.AreEqual(("Hollow Dam", "Hollow Dam"), Strings.Texts["map.hydrodam"]);
            Assert.AreEqual(("Helion Launch Complex", "Helion Launch Complex"), Strings.Texts["map.launchsite"]);
            Assert.AreEqual(("Coast of Fire", "Coast of Fire"), CampaignText.Table["chapter.1.title"]);
            Assert.AreEqual(("Act I · Landfall", "Hồi I · Landfall"), CampaignText.Table["act.1"]);
            StringAssert.Contains("Meridian Accord", CampaignText.Table["campaign.story.prologue"].vi);
        }

        // ------------------------------------------------------------------ B: the campaign's shape

        /// <summary>Prompt 22 B.2 (the owner's note: 9-18 a chapter), chapter 1 raised from 8 to 9 (DECISIONS 22A).</summary>
        private static readonly Dictionary<int, (int main, int side)> Counts = new()
        {
            [1] = (9, 1), [2] = (11, 2), [3] = (12, 2), [13] = (4, 0), [4] = (16, 2), [5] = (13, 2), [6] = (16, 2), [14] = (4, 0),
            [7] = (18, 1), [8] = (12, 2), [9] = (14, 2), [15] = (4, 0), [10] = (14, 2), [11] = (11, 1), [12] = (10, 0),
        };

        [Test]
        public void TheChaptersRunNineToEighteenMissionsAndTheInterludesFour()
        {
            CollectionAssert.AreEqual(new[] { 1, 2, 3, 13, 4, 5, 6, 14, 7, 8, 9, 15, 10, 11, 12 }, Campaign.Chapters.Select(c => c.Number).ToArray(), "the order of play");
            foreach (var c in Campaign.Chapters)
            {
                var main = Campaign.MissionsOf(c.Number, side: false);
                var side = Campaign.MissionsOf(c.Number, side: true);
                Assert.AreEqual(Counts[c.Number], (main.Count, side.Count), $"chapter {c.Number}");
                if (c.IsInterlude)
                {
                    Assert.IsNull(c.Main, $"interlude {c.Short}: no main boss");
                    Assert.IsFalse(main.Any(m => m.Operation), $"interlude {c.Short}: no operation");
                    continue;
                }
                Assert.That(main.Count, Is.InRange(9, 18), $"chapter {c.Number}");
                var last = main[main.Count - 1];
                Assert.IsTrue(last.Operation && last.Stages.Count >= 4, $"chapter {c.Number}: the last mission is its big operation");
                Assert.AreEqual(1, main.Count(m => m.Operation), $"chapter {c.Number}: one operation");
                Assert.IsTrue(last.Stages.Any(s => s.Mission.Boss?.Def == c.Main), $"chapter {c.Number}: the operation fights {c.Main}");
            }
            Assert.AreEqual(168, Campaign.All.Count(m => !m.Side), "main missions");
            Assert.AreEqual(19, Campaign.All.Count(m => m.Side), "side missions");
        }

        /// <summary>B.4: no two missions in a row on one battlefield with one set-up (direction, base, weather, play area, goal).</summary>
        [Test]
        public void NoTwoMissionsInARowAreAlike()
        {
            var all = Campaign.All;
            var bad = new List<string>();
            for (var i = 1; i < all.Count; i++)
            {
                var a = all[i - 1];
                var b = all[i];
                if (a.Map != b.Map) continue;
                var same = a.Reversed == b.Reversed && a.Variant == b.Variant && a.PlayerBase == b.PlayerBase && a.EnemyBase == b.EnemyBase &&
                           a.Weather == b.Weather && a.PlayArea.HasValue == b.PlayArea.HasValue && a.Goal == b.Goal;
                if (same) bad.Add($"{a.Id} and {b.Id} on {a.Map}");
            }
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }

        [TestCase(1, 13)]
        [TestCase(2, 14)]
        [TestCase(3, 15)]
        [TestCase(4, 12)]
        public void AnInterludeGoesWithTheActBeforeIt(int lastAct, int final)
        {
            Campaign.Release = CampaignRelease.UpTo(lastAct);
            Assert.AreEqual(lastAct * 3, Campaign.LastChapter);
            Assert.AreEqual(final, Campaign.FinalChapter, "the release ends on the act's interlude (the story on chapter 12)");
            Assert.AreEqual(lastAct == 4, Campaign.StoryComplete);
            foreach (var c in Campaign.Chapters.Where(c => c.IsInterlude))
                Assert.AreEqual(c.Act <= lastAct, Campaign.All.Any(m => m.Chapter == c.Number), $"interlude {c.Short} with act {c.Act}");
            Assert.AreEqual(lastAct * 3, Operations.Big.Count, "an interlude has no operation");
            Campaign.Release = CampaignRelease.UpTo(lastAct, comingSoon: false);
            CollectionAssert.AreEquivalent(Campaign.Chapters.Where(c => c.Act <= lastAct).Select(c => c.Number), Campaign.ShownChapters.Select(c => c.Number));
            // An interlude on the screens: its Roman numeral, "Interlude II", the chapter before it.
            Assert.AreEqual(13, Campaign.PreviousChapter(4));
            Assert.AreEqual(3, Campaign.PreviousChapter(13));
            Assert.AreEqual(0, Campaign.PreviousChapter(1));
            Assert.AreEqual("II", Campaign.ChapterShort(14));
            Assert.AreEqual(Strings.Format("campaign.interludeName", ("interlude", "II")), Campaign.ChapterName(14));
            Assert.AreEqual(Strings.Format("campaign.chapterName", ("chapter", 4)), Campaign.ChapterName(4));
            if (lastAct >= 2) Assert.AreEqual("II-1", Campaign.Label(Campaign.Get("i2m01")));
        }

        /// <summary>B: a save of the twelve chapters of ten (campaign version 3) takes the missions that moved along, once.</summary>
        [Test]
        public void ATwelveChaptersOfTenSaveMovesOn()
        {
            var won = new List<(string id, int stars, int tier)>
            {
                ("c1m07", 3, 0), ("c1s2", 2, 0), ("c7s2", 1, 0), ("c11s2", 2, 1), ("c12s1", 3, 0), ("c2m10", 3, 1), ("c4m11", 2, 0),
            };
            // Chapters 1 and 2 as they were (their old ten), and chapter 3's ten.
            var before = Campaign.All.Where(m => m.Chapter <= 3 && !m.Side && m.Id != "c2m11" && m.Id != "c3m11" && m.Id != "c3m12").Select(m => m.Id);
            foreach (var id in before)
                if (won.All(w => w.id != id)) won.Add((id, 2, 0));
            var save = new StorySave
            {
                campaignVersion = 3, coins = 777, unlocked = new List<string> { "mlrs" },
                missionIds = won.Select(w => w.id).ToList(), missionStars = won.Select(w => w.stars).ToList(), missionTiers = won.Select(w => w.tier).ToList(),
                chaptersSeen = new List<int> { 1, 2, 3 },
            };
            PlayerProfile.LoadForTests(JsonUtility.ToJson(save));
            Progression.TestUnlockAll = false;
            foreach (var (from, to, stars, tier) in new[] { ("c1m07", "c6m11", 3, 0), ("c1s2", "c6m12", 2, 0), ("c7s2", "c7m11", 1, 0), ("c11s2", "c11m11", 2, 1) })
            {
                Assert.AreEqual(stars, PlayerProfile.Stars(to), $"{from} -> {to}: stars");
                Assert.AreEqual(tier, PlayerProfile.MissionTier(to), $"{from} -> {to}: tier");
                Assert.AreEqual(0, PlayerProfile.Stars(from), $"{from}: the old id is gone");
            }
            Assert.AreEqual(3, PlayerProfile.Stars("c2m10"), "a mission that stayed keeps its stars");
            Assert.AreEqual(1, PlayerProfile.MissionTier("c2m10"));
            Assert.AreEqual(2, PlayerProfile.Stars("c4m11"), "Leviathan is chapter 4's operation now");
            Assert.IsNull(Campaign.Get("c12s1"), "chapter 12 has no side mission any more");
            Assert.AreEqual(777, PlayerProfile.Coins);
            Assert.IsTrue(PlayerProfile.IsUnlocked("mlrs"));
            Assert.IsTrue(PlayerProfile.ChapterSeen(3) && !PlayerProfile.ChapterSeen(13));
            // The new missions round what was won are open to play; the campaign goes on from the first of them.
            Assert.AreEqual("c2m11", Campaign.All[Campaign.Next].Id, "chapter 2's new operation");
            Assert.IsTrue(Campaign.IsOpen(Campaign.IndexOf("c3m11")) && Campaign.IsOpen(Campaign.IndexOf("i1m01")));
            Assert.IsTrue(Campaign.IsOpen(Campaign.IndexOf("c3m10")), "a mission won stays open");
            Assert.IsFalse(Campaign.ChapterDone(2), "until its new operation is won");
            // Saved and read back, nothing moves twice.
            PlayerProfile.LoadForTests(PlayerProfile.JsonForTests());
            Assert.AreEqual(3, PlayerProfile.Stars("c6m11"));
            Assert.AreEqual(1, PlayerProfile.Stars("c7m11"));
        }

        [System.Serializable]
        private sealed class StorySave
        {
            public int campaignVersion;
            public int coins;
            public List<string> unlocked = new();
            public List<string> missionIds = new();
            public List<int> missionStars = new();
            public List<int> missionTiers = new();
            public List<int> chaptersSeen = new();
        }

        // ------------------------------------------------------------------ C: the story

        private static IEnumerable<string> LinesOf(MissionDef m) =>
            m.Radio.Select(r => r.Key).Concat(m.Stages.SelectMany(s => s.Events).Where(e => e.Key != null).Select(e => e.Key));

        private static bool Says(string missionId, string vi) => LinesOf(Campaign.Get(missionId)).Any(k => Strings.Has(k) && CampaignText.Table.TryGetValue(k, out var t) && t.vi.Contains(vi));

        [Test]
        public void TheStoryBeatsAreInTheirMissions()
        {
            // C.3 and C.5: the flash-forward and the ending.
            foreach (var key in new[] { "campaign.flash.kicker", "campaign.flash.title", "campaign.flash", "campaign.epilogue" }) Assert.IsTrue(Strings.Has(key), key);
            StringAssert.Contains("Họ vẫn chưa hiểu.", CampaignText.Table["campaign.flash"].vi);
            StringAssert.Contains("Dự án Icarus chưa bao giờ chỉ có một phi thuyền", CampaignText.Table["campaign.epilogue"].vi);
            // C.4, a few beats by their missions.
            Assert.IsTrue(Says("c1m10", "Người của tôi được đi ra an toàn"), "Brandt surrenders");
            Assert.IsNotNull(Campaign.Get("c2m11").Ally, "Thorne fights beside the brigade for the first time");
            Assert.IsTrue(Says("c3m10", "Mùa đông luôn quay lại"), "Orlov: winter always comes back");
            Assert.AreEqual("behemoth_mk0", Campaign.Get("i1m03").Boss.Def, "Blueprints: Behemoth Mk.0");
            Assert.IsTrue(Says("c5m09", "Titan"), "a clue about Thorne in chapter 5");
            Assert.AreEqual(MissionGoal.Evacuate, Campaign.Get("c6m14").Goal, "the ceasefire at the Hollow Dam");
            Assert.IsTrue(Says("c6m14", "Tôi hứa danh dự"), "Varga and Kade speak");
            var liberation = Campaign.Get("c7m10");
            Assert.IsTrue(liberation.Stages.Any(s => s.Events.Any(e => e.Kind == StageEventKind.Betrayal)), "the allied base turns");
            Assert.AreEqual("nuke_train", liberation.Stages[liberation.Stages.Count - 1].Mission.Boss.Def, "Nemesis is stopped last");
            Assert.IsTrue(Says("c7m10", "Tôi thì thấy rồi"), "Thorne: have you seen what they are about to launch?");
            Assert.IsTrue(Says("c9m10", "Đừng để tôi đã đúng."), "Thorne's last message");
            Assert.AreEqual("morrigan", Campaign.Get("c10m12").Boss.Def, "Hawk and Raven's duel");
            Assert.IsTrue(Says("c11m01", "vệ tinh đầu tiên"), "Aurel's first words on the radio");
            Assert.IsFalse(Campaign.All.TakeWhile(m => m.Chapter != 11).SelectMany(LinesOf).Any(k => k.StartsWith("radio.aurel.")), "Aurel is not on the radio before chapter 11");
            Assert.IsTrue(Says("c12m10", "Họ vẫn chưa hiểu."), "Aurel's last words echo the flash-forward");
        }

        /// <summary>C.7: a radio line fits in one or two lines on a phone, in both languages.</summary>
        [Test]
        public void EveryRadioLineIsShort()
        {
            var bad = new List<string>();
            foreach (var key in Campaign.All.SelectMany(LinesOf).Distinct())
            {
                Assert.IsTrue(CampaignText.Table.ContainsKey(key) || Strings.Has(key), key);
                if (!CampaignText.Table.TryGetValue(key, out var t)) continue;
                var en = NameText.Expand(t.en);
                var vi = t.vi;
                if (en.Length > 100 || vi.Length > 100) bad.Add($"{key}: {System.Math.Max(en.Length, vi.Length)}");
            }
            Assert.IsEmpty(bad, string.Join("\n", bad));
        }
    }
}
