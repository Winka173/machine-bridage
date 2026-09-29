using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The roster cleanup: merged cards hand their progress to the card they became (the higher
    /// rank, the blueprints, the lower rank's coins back), retired and bought cards are refunded,
    /// APS tank owners get a Trophy APS module, and nothing in the game still asks for a card
    /// that is gone.
    /// </summary>
    public class RosterMergeTests
    {
        [TearDown]
        public void Restore() => PlayerProfile.Load();

        [Test]
        public void AMergedCardKeepsTheHigherRankAndRefundsTheLower()
        {
            // APC at rank 5 with 10 blueprints, IFV at rank 3: the IFV goes to rank 5, keeps the
            // APC's blueprints and gets back what its own three ranks cost.
            PlayerProfile.LoadForTests("{\"coins\":0,\"rankIds\":[\"apc\",\"ifv\"],\"ranks\":[5,3],\"prints\":[10,1]}");
            Assert.AreEqual(5, PlayerProfile.Rank("ifv"), "the higher rank moves across");
            Assert.AreEqual(10 + 1 + CardRanks.BlueprintsSpent(3), PlayerProfile.Blueprints("ifv"), "with the blueprints, and those spent on the lower rank");
            Assert.AreEqual(CardRanks.CoinsSpent(3), PlayerProfile.Coins, "and the coins spent on the lower rank come back");
            Assert.AreEqual(1, PlayerProfile.Rank("apc"), "the APC card is gone");
        }

        [Test]
        public void AMergedCardAtALowerRankIsRefunded()
        {
            // Howitzer rank 2, SP artillery rank 6: the artillery stays at 6, the howitzer's rank comes back.
            PlayerProfile.LoadForTests("{\"coins\":100,\"rankIds\":[\"artillery\",\"howitzer\"],\"ranks\":[6,2],\"prints\":[0,4]}");
            Assert.AreEqual(6, PlayerProfile.Rank("artillery"));
            Assert.AreEqual(100 + CardRanks.CoinsSpent(2), PlayerProfile.Coins);
            Assert.AreEqual(4 + CardRanks.BlueprintsSpent(2), PlayerProfile.Blueprints("artillery"));
        }

        [Test]
        public void UnlocksMoveToTheCardEachBecame()
        {
            Progression.TestUnlockAll = false;
            try
            {
                PlayerProfile.LoadForTests("{\"coins\":0,\"unlocked\":[\"grad_truck\",\"siege_mortar\"]}");
                Assert.IsTrue(PlayerProfile.IsUnlocked("mlrs"), "the Grad's unlock is the MLRS's");
                Assert.IsTrue(PlayerProfile.IsUnlocked("siege_tank"), "the 240 mm mortar's is the siege tank's");
                Assert.IsFalse(PlayerProfile.IsUnlocked("grad_truck"));
            }
            finally
            {
                Progression.TestUnlockAll = true;
            }
        }

        [Test]
        public void RetiredAndBoughtCardsAreRefunded()
        {
            // Bought carpet bombing: its price back and the airstrike for it. Play-test 7 (DECISIONS 22P): a sky gunship
            // bought on an old save is kept (it is the AC-130 card again) with its rank and blueprints; the Gunship support
            // card bought on a newer one becomes it.
            PlayerProfile.LoadForTests("{\"coins\":0,\"owned\":[\"sky_gunship\",\"carpet_bombing\"],\"rankIds\":[\"sky_gunship\"],\"ranks\":[4],\"prints\":[3]}");
            Assert.AreEqual(3000, PlayerProfile.Coins);
            Assert.IsTrue(PlayerProfile.Owns("sky_gunship"));
            Assert.AreEqual(4, PlayerProfile.Rank("sky_gunship"));
            Progression.TestUnlockAll = false;
            try
            {
                Assert.IsTrue(PlayerProfile.IsUnlocked("airstrike"), "carpet bombing became the airstrike");
            }
            finally
            {
                Progression.TestUnlockAll = true;
            }
            PlayerProfile.LoadForTests("{\"coins\":0,\"rosterVersion\":4,\"owned\":[\"gunship_strike\"]}");
            Assert.AreEqual(0, PlayerProfile.Coins, "no refund: the card carries over");
            Assert.IsTrue(PlayerProfile.Owns("sky_gunship"), "the Gunship support became the AC-130 card");
            Assert.IsFalse(PlayerProfile.Owns("gunship_strike"));
        }

        [Test]
        public void ApsTankOwnersGetATrophyApsModule()
        {
            PlayerProfile.LoadForTests("{\"coins\":0,\"unlocked\":[\"aps_tank\"]}");
            var modules = PlayerProfile.GearOwned.Where(g => g.Module == SpecialModule.TrophyAps).ToList();
            Assert.AreEqual(1, modules.Count, "one Trophy APS module");
            Assert.AreEqual(Rarity.Epic, modules[0].Rarity, "at Epic");
            Assert.AreEqual(GearSlot.Special, modules[0].Slot);

            PlayerProfile.LoadForTests("{\"coins\":0,\"unlocked\":[\"light_tank\"]}");
            Assert.IsFalse(PlayerProfile.GearOwned.Any(g => g.Module == SpecialModule.TrophyAps), "not for a player who never had it");
        }

        [Test]
        public void TheMigrationRunsOnce()
        {
            PlayerProfile.LoadForTests("{\"coins\":0,\"owned\":[\"carpet_bombing\"]}");
            var json = PlayerProfile.JsonForTests();
            PlayerProfile.LoadForTests(json);
            Assert.AreEqual(3000, PlayerProfile.Coins, "a saved, migrated profile is not refunded twice");
        }

        [Test]
        public void NothingAsksForACardThatIsGone()
        {
            var catalog = GameContent.LoadCatalog();
            foreach (var id in CardMerges.Into.Keys.Concat(CardMerges.Retired))
                Assert.IsFalse(catalog.Vehicles.ContainsKey(id) || catalog.TryGetSupport(id, out _), $"{id} is out of the catalog");
            var cards = new List<string>();
            cards.AddRange(MatchSettings.AllVehicles);
            cards.AddRange(MatchSettings.AllSupports);
            cards.AddRange(Progression.StarterVehicles);
            cards.AddRange(Progression.StarterSupports);
            foreach (var mission in Campaign.All)
            {
                cards.AddRange(mission.Unlocks);
                cards.AddRange(mission.EnemyDeck);
            }
            foreach (var id in cards)
            {
                Assert.IsFalse(CardMerges.IsGone(id), $"{id} was merged or retired but is still listed");
                Assert.IsTrue(catalog.Vehicles.ContainsKey(id) || catalog.TryGetSupport(id, out _), $"{id} is in the catalog");
            }
            Assert.IsTrue(MatchSettings.AllVehicles.Contains("sky_gunship"), "play-test 7: the AC-130 is a card again");
        }

        [Test]
        public void MergedIdsResolveToTheirCard()
        {
            Assert.AreEqual("ifv", CardMerges.Resolve("apc"));
            Assert.AreEqual("main_battle_tank", CardMerges.Resolve("aps_tank"));
            Assert.AreEqual("airstrike", CardMerges.Resolve("carpet_bombing"));
            Assert.AreEqual("sky_gunship", CardMerges.Resolve("gunship_strike"));
            Assert.AreEqual("light_tank", CardMerges.Resolve("light_tank"));
        }
    }
}
