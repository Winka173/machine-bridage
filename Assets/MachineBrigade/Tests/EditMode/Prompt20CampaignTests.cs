using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 20, pass 1: the new boss and general names everywhere (A), the twelve chapters in four
    /// acts with their boss slots (B), the nine-chapter save moving to them (B.3), and the act switches
    /// in three configurations (C.4).
    /// </summary>
    public class Prompt20CampaignTests
    {
        [TearDown]
        public void Restore()
        {
            Campaign.Release = null;
            PlayerProfile.Load();
        }

        // ------------------------------------------------------------------ A: names

        /// <summary>Old display names no text may still use (the ids stay as they were).</summary>
        private static readonly string[] OldNames =
        {
            "Silver Bug", "Bọ Bạc", "Iron Bird", "Chim sắt", "Chim Sắt", "Ice Fortress", "Pháo đài băng", "Pháo Đài Băng",
            "Hive Carrier", "Hive Mothership", "Tàu mẹ Tổ Ong", "Tàu Mẹ Tổ Ong", "Tổ Ong", "Doomsday Train", "Tận Thế",
            "Iron Train", "Đoàn tàu thép", "Đoàn Tàu Thép", "Rail Supergun", "Supreme Commander", "Tổng Tư Lệnh",
            "Earth Worm", "Sâu Đất", "Frost Monster", "Quái Vật Băng", "Frozen Behemoth", "Landing Hovercraft",
            "Command Airship", "Khinh Hạm", "Black Crow", "Hùng", "Quạ Đen",
        };

        /// <summary>Where an old name stays on purpose: our side still calls Wolff "Quạ Đen" on the radio and in its own files.</summary>
        private static bool Allowed(string key, string name) =>
            name == "Quạ Đen" && (key.StartsWith("radio.khai.") || key.StartsWith("radio.linh.") || key.StartsWith("radio.dieuhau.") ||
                                  key.StartsWith("radio.mai.") || key.StartsWith("radio.hq.") || key == "char.quaden.bio" || key == "char.dieuhau.bio");

        [Test]
        public void NoTextUsesAnOldBossOrGeneralName()
        {
            var bad = new List<string>();
            foreach (var (key, (en, vi)) in Strings.Texts.Concat(GuideText.Table).Concat(CampaignText.Table).Concat(UnitText.Table)
                         .Concat(BigAttackText.Table).Concat(OrbitalText.Table))
                foreach (var name in OldNames)
                    if ((en.Contains(name) || vi.Contains(name)) && !Allowed(key, name))
                        bad.Add($"{key}: {name}");
            Assert.IsEmpty(bad, string.Join("\n", bad.Take(40)));
            // "Proper name · subtitle", the proper name untranslated, the project renamed.
            Assert.AreEqual(("Icarus · Orbital spacecraft", "Icarus · Phi thuyền quỹ đạo"), Strings.Texts["unit.silver_bug"]);
            StringAssert.Contains("Dự án Icarus", CampaignText.Table["char.aurel.role"].vi);
            foreach (var c in Campaign.Chapters)
                foreach (var slot in c.Minis.Prepend(c.Main))
                {
                    Assert.IsTrue(Strings.Has("boss." + slot), $"boss.{slot}");
                    StringAssert.Contains(" · ", Strings.Get("boss." + slot), $"boss.{slot} as name · subtitle");
                }
        }


        // ------------------------------------------------------------------ B: twelve chapters, four acts

        [Test]
        public void TwelveChaptersInFourActsFightTheirBosses()
        {
            var catalog = GameContent.LoadCatalog();
            Assert.AreEqual(12, Campaign.ChapterCount);
            CollectionAssert.AreEqual(new[] { 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4 }, Campaign.Chapters.Select(c => c.Act).ToArray());
            foreach (var c in Campaign.Chapters)
            {
                var fought = Campaign.MissionsOf(c.Number).SelectMany(Campaign.BossesOf).ToList();
                foreach (var slot in c.Minis.Prepend(c.Main))
                    Assert.IsTrue(fought.Any(b => b.Def == slot), $"chapter {c.Number}: {slot} is fought");
                // A boss pass 2 has not built is fought as a stand-in that exists.
                foreach (var b in fought)
                    Assert.IsTrue(catalog.Vehicles.ContainsKey(b.Resolve(catalog).def), $"chapter {c.Number}: {b.Def}");
            }
            Assert.AreEqual("Kasimir Wolff", CampaignText.Table["char.quaden.name"].en);
            Assert.AreEqual("Tướng Lý Hàn", CampaignText.Table["char.hung.name"].vi);
        }

        [Test]
        public void NineChapterProgressMovesToTwelveChapters()
        {
            var old = new (string id, int stars, int tier, string now)[]
            {
                ("c7m05", 3, 1, "c10m05"), ("c8m01", 2, 0, "c7m01"), ("c9m03", 1, 0, "c12m03"), ("c3m08", 3, 0, "c6m05"),
                ("c1m05", 2, 0, "c6m08"), ("c6m08", 3, 0, "c8m05"), ("c4m06", 1, 0, "c11m05"), ("c3s2", 2, 0, "c3m08"),
                ("c6m05", 1, 0, "c10m08"), ("c7m08", 2, 0, "c11m08"), ("c2m01", 3, 0, "c2m01"),
            };
            var save = new StorySave
            {
                campaignVersion = 2, coins = 555, unlocked = new List<string> { "gunship_heli", "heavy_turret" },
                missionIds = old.Select(o => o.id).ToList(), missionStars = old.Select(o => o.stars).ToList(), missionTiers = old.Select(o => o.tier).ToList(),
                chaptersSeen = new List<int> { 1, 7, 8, 9, 10 },
            };
            PlayerProfile.LoadForTests(JsonUtility.ToJson(save));
            Progression.TestUnlockAll = false;
            foreach (var o in old)
            {
                Assert.AreEqual(o.stars, PlayerProfile.Stars(o.now), $"{o.id} -> {o.now}: stars");
                Assert.AreEqual(o.tier, PlayerProfile.MissionTier(o.now), $"{o.id} -> {o.now}: tier");
            }
            Assert.AreEqual(0, PlayerProfile.Stars("c9m01"), "nothing lands where nothing was won");
            foreach (var c in new[] { 1, 10, 7, 12, PlayerProfile.EpilogueSeen }) Assert.IsTrue(PlayerProfile.ChapterSeen(c), $"card {c} seen");
            Assert.IsFalse(PlayerProfile.ChapterSeen(8) || PlayerProfile.ChapterSeen(9), "chapters 8 and 9 are new");
            Assert.IsTrue(PlayerProfile.IsUnlocked("gunship_heli") && PlayerProfile.IsUnlocked("heavy_turret"), "cards won stay won");
            Assert.AreEqual(555, PlayerProfile.Coins);
            Assert.AreEqual(5, Campaign.HqLevelCap, "the HQ level the old c9m03 opened is kept");
            // The new chapters are open to play from where the save stood; saved and read back, nothing moves twice.
            Assert.IsTrue(Campaign.IsOpen(Campaign.IndexOf("c10m05")));
            PlayerProfile.LoadForTests(PlayerProfile.JsonForTests());
            Assert.AreEqual(3, PlayerProfile.Stars("c10m05"));
            Assert.AreEqual(2, PlayerProfile.Stars("c7m01"));
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

        // ------------------------------------------------------------------ C: act switches

        [TestCase(4)]
        [TestCase(2)]
        [TestCase(3)]
        public void ActSwitchesKeepTheCampaignWhole(int lastAct)
        {
            Progression.TestUnlockAll = false;
            var every = Campaign.Everything;
            Campaign.Release = CampaignRelease.UpTo(lastAct);
            var last = lastAct * 3;
            Assert.AreEqual(last, Campaign.LastChapter);
            Assert.AreEqual(lastAct == 4, Campaign.StoryComplete, "the game's epilogue only at the story's end, else To be continued");
            Assert.IsTrue(Campaign.All.All(m => m.Chapter <= last), "only chapters switched on");
            Assert.AreEqual(12, Campaign.ShownChapters.Count(), "the rest show as Coming soon");
            // Every card, tower, module and HQ level has a source.
            var opened = Campaign.All.SelectMany(m => m.Unlocks).ToHashSet();
            foreach (var u in every.SelectMany(m => m.Unlocks)) Assert.IsTrue(opened.Contains(u), $"{u} still unlocks");
            Assert.AreEqual(5, Campaign.All.Max(m => m.HqLevel), "every HQ level");
            // Operations and the rotations bring only what is switched on.
            Assert.AreEqual(last, Operations.Big.Count);
            Assert.IsTrue(Operations.Big.All(m => m.Chapter <= last));
            if (Operations.Week(202640) is { } week) Assert.LessOrEqual(week.mission.Chapter, last);
            var rush = BossRushRules.Roster(7, Campaign.BossEnabled);
            foreach (var id in rush) Assert.IsTrue(Campaign.BossEnabled(id), id);
            if (lastAct == 2) CollectionAssert.DoesNotContain(rush, "silver_bug");
            if (lastAct == 4) CollectionAssert.AreEqual(BossRushRules.Roster(7), rush, "everything on draws as before");
            // A shorter release pays more (campaign.json "economy").
            var scale = Campaign.Meta.PayScale.TryGetValue(lastAct, out var k) ? k : 1f;
            var first = every.First(m => m.Id == "c1m01");
            Assert.AreEqual((int)System.Math.Round(first.RewardCoins * scale / 5f) * 5, Campaign.Get("c1m01").RewardCoins);
            Campaign.Release = CampaignRelease.UpTo(lastAct, comingSoon: false);
            Assert.AreEqual(last, Campaign.ShownChapters.Count(), "hidden instead of Coming soon");
        }

        [Test]
        public void ASaveContinuesWhenAnActIsSwitchedBackOn()
        {
            PlayerProfile.ResetForTests();
            Progression.TestUnlockAll = false;
            // Won with every act on: chapters 1 to 6 and the first mission of chapter 7.
            foreach (var m in Campaign.All.Where(m => m.Chapter <= 6 || m.Id == "c7m01")) PlayerProfile.RecordMission(m.Id, 2);
            Campaign.Release = CampaignRelease.UpTo(2);
            Assert.IsNull(Campaign.All.FirstOrDefault(m => m.Id == "c7m01"));
            Assert.AreEqual(2, PlayerProfile.Stars("c7m01"), "a mission switched off keeps its stars");
            Assert.IsTrue(Campaign.ChapterDone(6));
            Campaign.Release = CampaignRelease.UpTo(4);
            Assert.AreEqual("c7m02", Campaign.All[Campaign.Next].Id, "the campaign goes on from where it stopped");
        }
    }
}
