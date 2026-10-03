using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 25 D2 (DECISIONS 25D2): the balance spreadsheet's unlock route (sheet "Phương tiện", columns "Mở khóa đề xuất"
    /// and "Mua sớm"; applied by Tools/balance/import_unlocks.py and Tools/campaign/act11.py, the sheet's rows in
    /// <see cref="UnlockSheetData"/>). Every card has exactly one unlock source, story loot is never sold, a chapter switched
    /// off hands its cards on, and a save from before keeps the cards that stopped being starters. Written under the
    /// owner's rule of 30/09 (no test runs until the test phase): not run yet.
    /// </summary>
    public class Prompt25UnlockTests
    {
        [TearDown]
        public void Restore()
        {
            Campaign.Release = null;
            Progression.TestUnlockAll = true;
            PlayerProfile.Load();
        }

        /// <summary>Every card of the deck, the supports' tray and the base (towers).</summary>
        private static IEnumerable<string> Cards(Catalog catalog) =>
            MatchSettings.AllVehicles.Concat(MatchSettings.AllSupports).Concat(TowerCards.All(catalog)).Distinct();

        /// <summary>
        /// Prompt 25 I: every card has exactly one unlock source, a starter, a premium card of the shop or one campaign
        /// mission (buying a campaign card early is a way to that source, not a second one), with every act switched on and
        /// in the shorter releases of prompt 20.
        /// </summary>
        [TestCase(4)]
        [TestCase(3)]
        [TestCase(2)]
        public void EveryCardHasExactlyOneUnlockSource(int lastAct)
        {
            var catalog = GameContent.LoadCatalog();
            Campaign.Release = CampaignRelease.UpTo(lastAct);
            foreach (var id in Cards(catalog))
            {
                var missions = Campaign.All.Where(m => m.Unlocks.Contains(id)).Select(m => m.Id).ToList();
                var starter = Progression.IsStarter(id);
                var premium = Progression.IsPremium(id);
                var sources = (starter ? 1 : 0) + (premium ? 1 : 0) + missions.Count;
                Assert.AreEqual(1, sources, $"{id} (acts I-{lastAct}): starter {starter}, premium {premium}, missions {string.Join(", ", missions)}");
            }
        }

        /// <summary>The sheet's route: each vehicle opens in the chapter it names, at its early price; four starters; one premium card.</summary>
        [Test]
        public void EveryVehicleOpensWhereTheSheetSaysAtItsEarlyPrice()
        {
            var catalog = GameContent.LoadCatalog();
            foreach (var (id, chapter, early, loot) in UnlockSheetData.Cards)
            {
                CollectionAssert.Contains(MatchSettings.AllVehicles, id, "a card of the sheet");
                if (chapter == 0)
                {
                    Assert.IsTrue(Progression.IsStarter(id), id + " is a starter");
                    Assert.IsNull(Progression.UnlockMission(id), id + ": no mission opens a starter");
                    continue;
                }
                Assert.IsFalse(Progression.IsStarter(id) || Progression.IsPremium(id), id + " opens in the campaign");
                var mission = Progression.UnlockMission(id);
                Assert.IsNotNull(mission, id);
                Assert.AreEqual(chapter, mission.Chapter, $"{id} opens in {Campaign.ChapterName(chapter)} ({mission.Id})");
                Assert.IsFalse(mission.Side || mission.Branch != null, id + ": on the way every player plays");
                Assert.AreEqual(loot, Progression.IsStoryLoot(id), id);
                if (!loot) Assert.AreEqual(early, Progression.Price(id, catalog), id + ": the sheet's early price");
            }
            CollectionAssert.AreEquivalent(UnlockSheetData.Cards.Where(c => c.chapter == 0).Select(c => c.id), Progression.StarterVehicles);
            CollectionAssert.AreEqual(new[] { "napalm_strike" }, Progression.PremiumCards.Where(id => !Progression.IsNewContent(id)).ToArray(),
                "the premium vehicles open in the campaign now (prompt 25 F2: the new content is sold in the shop)");
            foreach (var id in UnlockSheetData.NotCards) CollectionAssert.DoesNotContain(MatchSettings.AllVehicles, id, "no card");
        }

        /// <summary>
        /// Story loot (the rail gun, the drone mothership, and Kessler's
        /// cruise missiles) opens with its story beat and a line in both languages that says why; the shop never sells it
        /// early. Every other campaign card is for sale early.
        /// </summary>
        [Test]
        public void StoryLootCannotBeBoughtEarly()
        {
            var catalog = GameContent.LoadCatalog();
            var story = Narrative.Loot.Select(l => l.card).ToList();
            CollectionAssert.IsSubsetOf(new[] { "railgun_truck", "swarm_carrier" }, Progression.SheetLoot, "the spec's two left after play-test 14");
            CollectionAssert.IsSubsetOf(Progression.SheetLoot, story, "the sheet's loot is the story's");
            var was = Strings.Vietnamese;
            try
            {
                foreach (var (id, beat) in Narrative.Loot)
                {
                    Assert.IsTrue(Progression.IsStoryLoot(id), id);
                    Assert.IsFalse(Progression.CanBuyEarly(id), id + " is not sold early");
                    Assert.IsFalse(Progression.IsPremium(id), id + " is not sold at all");
                    Assert.AreEqual(0, Progression.Price(id, catalog), id + " has no price");
                    Assert.AreEqual(beat, Progression.UnlockMission(id)?.Id, id + " opens with its story beat");
                    var reason = Narrative.LootReason(id);
                    Assert.IsTrue(Strings.Has(reason), id + " says why");
                    Strings.Vietnamese = false;
                    var en = Strings.Get(reason);
                    Strings.Vietnamese = true;
                    var vi = Strings.Get(reason);
                    Assert.IsFalse(string.IsNullOrWhiteSpace(en) || string.IsNullOrWhiteSpace(vi) || en == vi, id + ": one line in each language");
                }
            }
            finally
            {
                Strings.Vietnamese = was;
            }
            foreach (var id in MatchSettings.AllVehicles.Concat(MatchSettings.AllSupports))
                if (Progression.Route(id) == CardRoute.Campaign && !story.Contains(id))
                    Assert.IsTrue(Progression.CanBuyEarly(id) && Progression.Price(id, catalog) > 0, id + " is for sale early");
        }

        /// <summary>Prompt 20's act switches: a card of a chapter switched off opens in the last operation switched on before it.</summary>
        [TestCase(2)]
        [TestCase(3)]
        public void ACardOfAnActSwitchedOffOpensInTheNearestChapterOn(int lastAct)
        {
            var every = Campaign.Everything;
            Campaign.Release = CampaignRelease.UpTo(lastAct);
            var receiver = Campaign.OperationOf(lastAct * 3);
            foreach (var m in every)
            {
                if (Campaign.ChapterEnabled(m.Chapter)) continue;
                foreach (var id in m.Unlocks)
                {
                    var at = Progression.UnlockMission(id);
                    Assert.IsNotNull(at, $"{id} (of {m.Id}) still opens");
                    Assert.IsTrue(Campaign.ChapterEnabled(at.Chapter), $"{id} opens in a chapter switched on");
                    if (m.Chapter <= Campaign.ChapterCount) Assert.AreEqual(receiver.Id, at.Id, $"{id}: chapter {lastAct * 3}'s operation, the nearest before chapter {m.Chapter}");
                }
            }
        }

        /// <summary>The light tank, the AA vehicle and the SP gun stopped being starters: a save that has played keeps them, a new player wins them.</summary>
        [Test]
        public void ASaveFromBeforeKeepsTheFormerStarterCards()
        {
            Progression.TestUnlockAll = false;
            CollectionAssert.AreEquivalent(new[] { "light_tank", "aa_vehicle", "artillery" }, Progression.FormerStarters);
            PlayerProfile.LoadForTests("{\"coins\":0,\"rosterVersion\":5,\"missionIds\":[\"c1m01\"],\"missionStars\":[2]}");
            foreach (var id in Progression.FormerStarters) Assert.IsTrue(PlayerProfile.IsUnlocked(id), id + " stays the player's");
            PlayerProfile.LoadForTests(PlayerProfile.JsonForTests());
            foreach (var id in Progression.FormerStarters) Assert.IsTrue(PlayerProfile.IsUnlocked(id), id + " after the migration ran once");
            PlayerProfile.LoadForTests("{\"coins\":0}");
            foreach (var id in Progression.FormerStarters) Assert.IsFalse(PlayerProfile.IsUnlocked(id), id + " is won in the campaign by a new player");
            PlayerProfile.LoadForTests("{\"coins\":0,\"rosterVersion\":4,\"owned\":[\"gunship_strike\"]}");
            Assert.IsTrue(PlayerProfile.Owns("sky_gunship"), "a bought Gunship support is a bought AC-130 still");
        }
    }
}
