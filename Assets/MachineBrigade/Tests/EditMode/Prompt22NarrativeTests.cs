using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine;
using UnityEngine.UIElements;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 22 D, the story's mechanics: the front map moves with each win and flips back at Thorne's betrayal (D.1); the
    /// clues about Thorne (D.2); the arcs and their payoff missions (D.3); the generals' reactive radio (D.4); the choices
    /// branch, rejoin the story, are saved and change what they say (D.5); the story loot (D.6); the intel files (D.7); the
    /// comic panels (D.8); nothing is ever taken away (D.9).
    /// </summary>
    public class Prompt22NarrativeTests
    {
        private bool _unlockAll;

        [SetUp]
        public void Fresh()
        {
            _unlockAll = Progression.TestUnlockAll;
            PlayerProfile.LoadForTests("{}");
        }

        [TearDown]
        public void Restore()
        {
            Progression.TestUnlockAll = _unlockAll;
            Campaign.Release = null;
            PlayerProfile.Load();
        }

        /// <summary>Wins every main mission on the path before <paramref name="stop"/> (null: all), choosing an option when asked.</summary>
        private static void PlayUpTo(string stop, bool second = false, int stars = 2)
        {
            for (var i = 0; i < Campaign.All.Count; i++)
            {
                var m = Campaign.All[i];
                if (m.Id == stop) return;
                if (m.Side || !Campaign.OnPath(m) || PlayerProfile.Completed(m.Id)) continue;
                if (Campaign.ChoicePending(m) is { } choice)
                {
                    Assert.IsTrue(Narrative.Choose(choice, Campaign.OptionsOf(choice)[second ? 1 : 0].Option), choice);
                    i--;
                    continue;
                }
                Assert.IsTrue(Campaign.IsOpen(i), m.Id + " is open on the way");
                PlayerProfile.RecordMission(m.Id, stars);
            }
        }

        private static FrontState StateOf(IEnumerable<FrontSector> sectors, string missionId) => sectors.First(s => s.Mission.Id == missionId).State;

        // ------------------------------------------------------------------ D.1 the front map

        [Test]
        public void TheFrontMovesWithEveryWin()
        {
            var main = Campaign.All.Where(m => !m.Side && m.Branch == null).ToList();
            Assert.AreEqual(0, FrontMap.Count(FrontMap.Sectors(), FrontState.Ours), "nothing is ours before the landing");
            var grids = new List<int>();
            foreach (var m in main.Take(40))
            {
                var before = FrontMap.Sectors().Where(s => s.State == FrontState.Ours).Select(s => s.Mission.Id).ToList();
                PlayerProfile.RecordMission(m.Id, 2);
                var after = FrontMap.Sectors();
                Assert.AreEqual(FrontState.Ours, StateOf(after, m.Id), m.Id + ": its ground is ours once won");
                CollectionAssert.AreNotEquivalent(before, after.Where(s => s.State == FrontState.Ours).Select(s => s.Mission.Id).ToList(), m.Id + ": the front moved");
                var grid = FrontMap.Grid(after, 96, 42);
                grids.Add(grid.Cast<FrontState>().Count(s => s == FrontState.Ours));
                Assert.IsNotEmpty(FrontMap.FrontLine(grid), m.Id + ": there is a front line");
            }
            Assert.Greater(grids[grids.Count - 1], grids[0], "the brigade's ground grows");
            Assert.IsTrue(FrontMap.Flags(FrontMap.Sectors()).Contains("ashfield"), "the Ashfield fortress taken flies a flag");
            foreach (var site in FrontMap.Sites) Assert.IsTrue(FrontMap.Land(site.Value), site.Key + " is on land");
            foreach (var m in Campaign.All) Assert.IsTrue(FrontMap.Sites.ContainsKey(m.Map), m.Map + " is on the map");
        }

        [Test]
        public void ThorneBetraysAndHisGroundFlipsBackUntilItIsRetaken()
        {
            PlayUpTo(FrontMap.BetrayalMission);
            var before = FrontMap.Sectors();
            Assert.AreEqual(0, FrontMap.Count(before, FrontState.Betrayed), "no Thorne ground before the betrayal");
            Assert.AreEqual(FrontState.Ours, StateOf(before, "c2m02"), "Red Rock is ours after chapter 2");
            Assert.IsFalse(FrontMap.Betrayed);
            PlayerProfile.RecordMission(FrontMap.BetrayalMission, 2);
            var after = FrontMap.Sectors();
            Assert.IsTrue(FrontMap.Betrayed);
            Assert.AreEqual(FrontState.Betrayed, StateOf(after, "c2m02"), "Red Rock turns with Thorne");
            Assert.AreEqual(FrontState.Betrayed, StateOf(after, "c4m02"), "so does Iron Harbor");
            Assert.AreEqual(FrontState.Ours, StateOf(after, "c1m01"), "Stormbeach stays ours");
            Assert.AreEqual(FrontState.Ours, StateOf(after, FrontMap.BetrayalMission), "Veyra is free");
            Assert.IsTrue(FrontMap.Grid(after, 96, 42).Cast<FrontState>().Any(s => s == FrontState.Betrayed), "the map shows it");
            Assert.IsFalse(FrontMap.Flags(after).Contains("redrock"), "no flag on ground lost again");
            // Chapters 8 and 9 take it back.
            PlayUpTo("i3m01");
            var back = FrontMap.Sectors();
            Assert.AreEqual(0, FrontMap.Count(back, FrontState.Betrayed), "Thorne's ground is retaken");
            Assert.AreEqual(FrontState.Ours, StateOf(back, "c2m02"));
        }

        [Test]
        public void TheFrontShowsOnlyTheActsSwitchedOn()
        {
            Campaign.Release = CampaignRelease.UpTo(1);
            Assert.IsTrue(FrontMap.Sectors().All(s => Campaign.Chapter(s.Mission.Chapter).Act == 1), "act I only");
            Campaign.Release = CampaignRelease.UpTo(2);
            Assert.IsTrue(FrontMap.Sectors().Any(s => s.Mission.Chapter == 5));
            Assert.IsFalse(FrontMap.Sectors().Any(s => Campaign.Chapter(s.Mission.Chapter).Act > 2));
        }

        // ------------------------------------------------------------------ D.5 choices

        [Test]
        public void AChoiceBranchesRejoinsAndIsSaved()
        {
            PlayUpTo("c4m14");
            Assert.IsNull(Narrative.Pending, "no choice before its mission is won");
            PlayerProfile.RecordMission("c4m14", 2);
            Assert.AreEqual("c4.pursuit", Narrative.Pending);
            Assert.AreEqual(-1, Campaign.NextAfter("c4m14"), "the choice is made on the campaign page");
            var sea = Campaign.Get("c4m17");
            var harbour = Campaign.Get("c4m18");
            Assert.AreEqual(("sea", "harbour"), (sea.Option, harbour.Option));
            Assert.AreEqual(("4-14A", "4-14B"), (Campaign.Label(sea), Campaign.Label(harbour)), "one slot, two options");
            Assert.AreEqual("4-15", Campaign.Label(Campaign.Get("c4m06")));
            Assert.IsFalse(Campaign.IsOpen(Campaign.IndexOf("c4m17")) || Campaign.IsOpen(Campaign.IndexOf("c4m18")), "not before the choice");
            Assert.IsFalse(Campaign.IsOpen(Campaign.IndexOf("c4m06")), "the story waits for it");
            Assert.IsFalse(Narrative.Choose("c4.pursuit", "moon"), "an option the choice does not have");
            Assert.IsTrue(Narrative.Choose("c4.pursuit", "harbour"));
            Assert.IsFalse(Narrative.Choose("c4.pursuit", "sea"), "made once");
            Assert.IsTrue(Campaign.IsOpen(Campaign.IndexOf("c4m18")), "the option taken opens");
            Assert.IsFalse(Campaign.IsOpen(Campaign.IndexOf("c4m17")), "the other never does");
            Assert.IsTrue(Campaign.NotTaken(sea));
            Assert.AreEqual(Campaign.IndexOf("c4m18"), Campaign.Next);
            Assert.IsFalse(Campaign.IsOpen(Campaign.IndexOf("c4m06")));
            CollectionAssert.Contains(Campaign.MissionsOf(4, side: false), harbour);
            CollectionAssert.DoesNotContain(Campaign.MissionsOf(4, side: false), sea);
            PlayerProfile.RecordMission("c4m18", 3);
            Assert.IsTrue(Campaign.IsOpen(Campaign.IndexOf("c4m06")), "back on the story's line");
            Assert.AreEqual(Campaign.IndexOf("c4m06"), Campaign.NextAfter("c4m18"));
            Assert.Greater(harbour.RarePrints, 0, "the harbour pays rare blueprints");
            Assert.Greater(sea.RewardCoins, harbour.RewardCoins, "the chase pays more coins");
            // The save keeps it.
            var json = PlayerProfile.JsonForTests();
            PlayerProfile.LoadForTests(json);
            Assert.AreEqual("harbour", PlayerProfile.StoryChoice("c4.pursuit"));
            Assert.IsTrue(Campaign.IsOpen(Campaign.IndexOf("c4m06")));
            PlayerProfile.LoadForTests("{}");
            Assert.IsNull(PlayerProfile.StoryChoice("c4.pursuit"), "an old save has made none");
        }

        [Test]
        public void EveryChoiceHasTwoOptionsWithTheirConsequences()
        {
            CollectionAssert.AreEqual(new[] { "c4.pursuit", "c8.miners", "c11.radar" }, Narrative.Choices.Select(c => c.id).ToArray());
            foreach (var (id, speaker, options) in Narrative.Choices)
            {
                var offer = Narrative.OfferOf(id);
                Assert.IsNotNull(offer, id);
                var missions = Campaign.OptionsOf(id);
                CollectionAssert.AreEqual(options, missions.Select(m => m.Option).ToArray(), id);
                var at = Campaign.IndexOf(offer.Id);
                CollectionAssert.AreEqual(missions, new[] { Campaign.All[at + 1], Campaign.All[at + 2] }, id + ": right after the mission that offers it");
                foreach (var m in missions)
                {
                    Assert.AreEqual(offer.Chapter, m.Chapter);
                    Assert.IsEmpty(m.Unlocks, m.Id + ": the card route never hangs on a choice");
                    Assert.IsFalse(m.Side || m.Operation, m.Id);
                    foreach (var key in new[] { $"storychoice.{id}.{m.Option}", $"storychoice.{id}.{m.Option}.info", $"mission.{m.Id}.name", $"mission.{m.Id}.brief" })
                        Assert.IsTrue(Strings.Has(key), key);
                }
                Assert.IsTrue(Strings.Has($"storychoice.{id}.title") && Strings.Has($"storychoice.{id}.body"), id);
            }
            var nine = Campaign.MissionsOf(9, side: false)[0];
            var twelve = Campaign.MissionsOf(12, side: false)[0];
            Assert.AreEqual(0f, Narrative.PlayerCpBonus(nine));
            Assert.AreEqual(1f, Narrative.EnemyVision(twelve));
            PlayerProfile.ChooseStory("c8.miners", "rescue");
            PlayerProfile.ChooseStory("c11.radar", "radar");
            Assert.AreEqual(Narrative.MinersCp, Narrative.PlayerCpBonus(nine), "the miners reinforce chapter 9");
            Assert.AreEqual(0f, Narrative.PlayerCpBonus(Campaign.MissionsOf(10, side: false)[0]), "and only chapter 9");
            Assert.AreEqual(Narrative.RadarVision, Narrative.EnemyVision(twelve), "a blinder enemy in chapter 12");
            Assert.AreEqual(2, Narrative.Effects(nine).Count + Narrative.Effects(twelve).Count, "each mission's page says so");
            Assert.Greater(Campaign.Get("c8m14").RewardCoins, Campaign.Get("c8m13").RewardCoins * 1.5f, "the direct strike pays more");
            Assert.Greater(Campaign.Get("c11m13").RarePrints, 0, "the short road pays rare blueprints");
        }

        // ------------------------------------------------------------------ D.6 story loot, D.9 nothing taken away

        [Test]
        public void TheStoryHandsOutItsCardsWithAReason()
        {
            var expected = new Dictionary<string, (string mission, string boss)>
            {
                ["railgun_truck"] = ("c4m10", "behemoth_tempest"), ["swarm_carrier"] = ("c5m10", "drone_mothership"),
            };
            foreach (var (card, (mission, boss)) in expected)
            {
                Assert.AreEqual(mission, Narrative.Loot.First(l => l.card == card).mission, card);
                var m = Campaign.Get(mission);
                CollectionAssert.Contains(m.Unlocks, card, $"{mission} unlocks {card}");
                Assert.IsTrue(Campaign.BossesOf(m).Any(b => b.Def == boss), $"{mission} fights {boss}");
            }
            foreach (var (card, mission) in Narrative.Loot)
            {
                Assert.AreEqual(1, Campaign.All.Count(m => m.Unlocks.Contains(card)), card + " is unlocked once");
                CollectionAssert.Contains(Campaign.Get(mission).Unlocks, card);
                Assert.IsTrue(Strings.Has(Narrative.LootReason(card)), card);
            }
            Assert.IsNull(Narrative.LootReason("main_battle_tank"));
            var catalog = GameContent.LoadCatalog();
            for (var c = 1; c <= 12; c++)
            {
                var cards = Campaign.MissionsOf(c, side: false).SelectMany(m => m.Unlocks)
                    .Count(id => !id.Contains('.') && !(catalog.Vehicles.TryGetValue(id, out var v) && v.Fort is { Kind: FortKind.Utility }));
                // Prompt 25 D2: the balance sheet's route opens 3 to 10 cards a chapter (was 4 to 7).
                Assert.That(cards, Is.InRange(3, 10), $"chapter {c} still opens three to ten cards");
            }
        }

        [TestCase(false)]
        [TestCase(true)]
        public void NoCardOrUnitIsEverTakenAway(bool second)
        {
            Progression.TestUnlockAll = false;
            var owned = new HashSet<string>();
            var every = Campaign.All.Where(m => m.Branch == null).SelectMany(m => m.Unlocks).ToHashSet();
            for (var i = 0; i < Campaign.All.Count; i++)
            {
                var m = Campaign.All[i];
                if (!Campaign.OnPath(m) || PlayerProfile.Completed(m.Id)) continue;
                if (Campaign.ChoicePending(m) is { } choice)
                {
                    Narrative.Choose(choice, Campaign.OptionsOf(choice)[second ? 1 : 0].Option);
                    i--;
                    continue;
                }
                var reward = Rewards.Mission(m, true, 300f, 1);
                reward.Claim();
                foreach (var id in owned) Assert.IsTrue(PlayerProfile.IsUnlocked(id), $"{id} is still the player's after {m.Id}");
                foreach (var id in m.Unlocks) owned.Add(id);
            }
            foreach (var id in every) Assert.IsTrue(PlayerProfile.IsUnlocked(id), id + " is the player's at the end, whatever was chosen");
        }

        // ------------------------------------------------------------------ D.7 intel files, D.2 clues

        [Test]
        public void IntelFilesComeFromSideObjectivesAndCostNothingToSkip()
        {
            foreach (var chapter in Campaign.Chapters)
                Assert.That(Narrative.IntelOf(chapter.Number).Count, Is.GreaterThanOrEqualTo(2), $"chapter {chapter.Short}");
            foreach (var f in Narrative.Intel)
            {
                var m = Campaign.Get(f.Mission);
                Assert.IsNotNull(m, f.Id);
                Assert.AreEqual(f.Chapter, m.Chapter, f.Id);
                Assert.AreEqual(!f.ThreeStars, m.Side, f.Id + ": a side mission, or a main mission's three stars");
                foreach (var key in new[] { "title", "from", "text" }) Assert.IsTrue(Strings.Has($"intel.{f.Id}.{key}"), f.Id + key);
            }
            // D.2: a clue about Thorne in each of chapters 4, 5 and 6, and Nadia says so on the radio there too.
            CollectionAssert.AreEquivalent(new[] { 4, 5, 6 }, Narrative.Intel.Where(f => f.Clue).Select(f => f.Chapter).ToArray());
            foreach (var mid in new[] { "c4m08", "c5m07", "c6m09" })
                Assert.IsTrue(Campaign.Get(mid).Radio.Any(r => r.Key == $"radio.linh.{mid}.d1"), mid + ": Nadia's clue");
            var clue = Narrative.Intel.First(f => f.Id == "c4.flank");
            Assert.IsFalse(Narrative.Found(clue));
            Assert.IsEmpty(Narrative.FoundBy(clue.Mission, 2), "two stars do not find it");
            Assert.AreEqual(clue.Id, Narrative.FoundBy(clue.Mission, 3).Single().Id);
            PlayerProfile.RecordMission(clue.Mission, 2);
            Assert.IsFalse(Narrative.Found(clue));
            Assert.IsTrue(Campaign.IsOpen(Campaign.IndexOf(clue.Mission) + 1), "the story goes on without it");
            PlayerProfile.RecordMission(clue.Mission, 3);
            Assert.IsTrue(Narrative.Found(clue));
            var side = Narrative.Intel.First(f => !f.ThreeStars);
            PlayerProfile.RecordMission(side.Mission, 1);
            Assert.IsTrue(Narrative.Found(side), "a side mission won finds its file");
        }

        // ------------------------------------------------------------------ D.3 arcs

        [Test]
        public void TheArcsEndInTheirPayoffMissions()
        {
            var payoffs = Narrative.Arcs.Where(b => b.Payoff).Select(b => (b.Who, b.Mission)).ToList();
            CollectionAssert.AreEquivalent(new[] { ("mai", "c12m10"), ("dieuhau", "c10m12"), ("linh", "c7m10"), ("khai", "c12m10"), ("varga", "c6m14"), ("varga", "c12m10") }, payoffs);
            foreach (var b in Narrative.Arcs)
            {
                Assert.IsNotNull(Campaign.Get(b.Mission), b.Key);
                Assert.IsTrue(Strings.Has(b.Key) && Strings.Has($"arc.{b.Who}.title"), b.Key);
            }
            Assert.AreEqual(3, Narrative.PayoffsAt("c12m10").Count, "Helion ends three stories");
        }

        // ------------------------------------------------------------------ D.8 comic panels

        [Test]
        public void EveryChapterEndsInThreeOrFourPanels()
        {
            foreach (var chapter in Campaign.Chapters)
            {
                var panels = Narrative.ComicOf(chapter.Number);
                Assert.That(panels.Count, Is.InRange(3, 4), $"chapter {chapter.Short}");
                foreach (var p in panels)
                {
                    Assert.IsTrue(Strings.Has(p.Key), p.Key);
                    Assert.IsTrue(p.Art.Split('|').Any(map => MapArt.For(map) != null), p.Key + ": a picture");
                    if (p.Render != null) Assert.IsNotNull(Resources.Load<Texture2D>(CardArt.Folder + p.Render), p.Key + ": " + p.Render);
                    Assert.IsNotNull(Resources.Load<Texture2D>("UI/Portraits/" + p.Speaker), p.Key + ": " + p.Speaker);
                }
            }
            PlayUpTo("c2m01");
            Assert.AreEqual(1, Narrative.ComicPending, "chapter 1's panels once it is done");
            Assert.AreEqual(-1, Campaign.NextAfter(Campaign.OperationOf(1).Id), "shown on the campaign page first");
            var page = new ComicPage(new VisualElement());
            var closed = 0;
            Assert.IsTrue(page.Show(1, () => closed++));
            Assert.AreEqual(1, page.Shown, "one panel, then the next");
            page.Next();
            Assert.AreEqual(2, page.Shown);
            page.Close();
            Assert.AreEqual(1, closed, "skipped");
            PlayerProfile.MarkChapterSeen(PlayerProfile.ComicSeen(1));
            Assert.AreEqual(0, Narrative.ComicPending);
            Assert.AreEqual(Campaign.IndexOf("c2m01"), Campaign.NextAfter(Campaign.OperationOf(1).Id));
            Assert.IsTrue(page.Show(1, null), "and seen again from the dossier");
            for (var i = 0; i < 4; i++) page.Next();
            Assert.IsFalse(page.Visible, "the last Next closes the page");
        }

        // ------------------------------------------------------------------ D.4 reactive radio

        [Test]
        public void TheGeneralAnswersTheWayThePlayerFights()
        {
            var catalog = GameContent.LoadCatalog();
            var mission = Campaign.All.First(m => m.General == "varga" && m.StarTime > 0f);
            var jet = catalog.Vehicles["attack_jet"];
            var tank = catalog.Vehicles["main_battle_tank"];
            var radio = new ReactiveRadio(mission);
            Assert.IsNull(radio.Next(10), "nothing to say yet");
            for (var i = 0; i < 5; i++) radio.Deployed(tank);
            for (var i = 0; i < 4; i++) radio.Deployed(jet);
            var air = radio.Next(60);
            Assert.AreEqual(ReactiveRadio.Key("varga", ReactiveRadio.Air, mission.Id), air);
            StringAssert.StartsWith("radio.varga.react.air.", air);
            Assert.IsTrue(Strings.Has(air), air);
            for (var i = 0; i < radio.HeavyLosses; i++) radio.LostOne();
            Assert.IsNull(radio.Next(70), "a little apart");
            StringAssert.StartsWith("radio.varga.react.losses.", radio.Next(90));
            radio.Interrupted();
            StringAssert.StartsWith("radio.varga.react.interrupt.", radio.Next(120));
            Assert.IsNull(radio.Next(400), "each moment once");
            StringAssert.StartsWith("radio.varga.react.fast.", radio.OnWin(radio.FastWin - 1));
            Assert.IsNull(new ReactiveRadio(mission).OnWin(radio.FastWin + 1), "a slow win: nothing");
            // Drones and guns.
            var drones = new ReactiveRadio(mission);
            for (var i = 0; i < 8; i++) drones.Deployed(catalog.Vehicles["fpv_carrier"]);
            StringAssert.StartsWith("radio.varga.react.drones.", drones.Next(50));
            var guns = new ReactiveRadio(mission);
            for (var i = 0; i < 8; i++) guns.Deployed(catalog.Vehicles["artillery"]);
            StringAssert.StartsWith("radio.varga.react.artillery.", guns.Next(50));
            // The same mission and moment, the same line; no general, no line.
            Assert.AreEqual(ReactiveRadio.Key("varga", ReactiveRadio.Air, mission.Id), ReactiveRadio.Key("varga", ReactiveRadio.Air, mission.Id));
            var none = new ReactiveRadio(Campaign.All.First(m => m.General == null));
            for (var i = 0; i < 9; i++) none.Deployed(jet);
            Assert.IsNull(none.Next(100));
            // Every general of the story has every moment, both lines, short, in both languages.
            foreach (var general in Campaign.All.Select(m => m.General).Where(g => g != null).Distinct())
                Assert.IsTrue(ReactiveRadio.Speaks(general), general + " answers");
            foreach (var general in Narrative.ReactGenerals)
                foreach (var moment in ReactiveRadio.Moments)
                    for (var n = 1; n <= Narrative.ReactLines; n++)
                    {
                        var key = $"radio.{general}.react.{moment}.{n}";
                        Assert.IsTrue(StoryText.Table.TryGetValue(key, out var t), key);
                        Assert.That(System.Math.Max(t.en.Length, t.vi.Length), Is.LessThanOrEqualTo(100), key);
                        Assert.AreEqual(general, RadioDirector.SpeakerOf(key), key + ": the general speaks it");
                    }
        }
    }
}
