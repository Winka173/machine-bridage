using NUnit.Framework;
using MachineBrigade.Game.Match;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Play-test 14 (roster version 9, Docs/fixes/playtest14_deleted.md): a save from before the deletion. A deleted card
    /// bought in the shop pays its price back with the coins its rank cost (its blueprints turn universal), a deleted
    /// support's unlock goes, a base slot holding a deleted structure is emptied, and gunship items still in the bag come
    /// back as coins; the menu's roster notice counts them. Written, not run.
    /// </summary>
    public class PlayTest14MigrationTests
    {
        [SetUp]
        public void Clear()
        {
            PlayerProfile.ResetForTests();
            PlayerProfile.TakeRosterNews();
        }

        [TearDown]
        public void Reset()
        {
            Progression.TestUnlockAll = true;
            PlayerProfile.ResetForTests();
        }

        [Test]
        public void TheDeletedCardsComeBackAsCoinsAndLeaveTheBase()
        {
            PlayerProfile.LoadForTests(@"{ ""rosterVersion"": 8, ""coins"": 0, ""universal"": 0,
                ""owned"": [ ""bmpt"" ], ""unlocked"": [ ""smoke_screen"" ],
                ""rankIds"": [ ""bmpt"" ], ""ranks"": [ 3 ], ""prints"": [ 4 ],
                ""baseLevel"": 5, ""baseLarge"": [ ""heavy_turret"", ""artillery_emplacement"" ],
                ""itemIds"": [ ""gunship_support"" ], ""itemCounts"": [ 3 ] }");
            Progression.TestUnlockAll = false;

            // The bought card: its price, what its rank cost, its blueprints universal; the card is gone.
            var expected = CardMerges.DeletedPt14["bmpt"] + CardRanks.CoinsSpent(3) + 3 * CardMerges.DeletedItemPricePt14;
            Assert.AreEqual(expected, PlayerProfile.Coins, "the price, the rank's coins and three gunship items");
            Assert.AreEqual(4 + CardRanks.BlueprintsSpent(3), PlayerProfile.UniversalBlueprints, "its blueprints turn universal");
            Assert.IsFalse(PlayerProfile.Owns("bmpt"), "no longer owned");
            Assert.IsFalse(PlayerProfile.IsUnlocked("bmpt"));
            Assert.AreEqual(1, PlayerProfile.Rank("bmpt"), "its rank is gone");
            Assert.AreEqual(0, PlayerProfile.Blueprints("bmpt"));

            // The unlocked support is gone without coins (it was won, not bought).
            Assert.IsFalse(PlayerProfile.IsUnlocked("smoke_screen"));

            // The deleted structure's slot is emptied; the other tower stays.
            var large = PlayerProfile.BaseLoadout.Large;
            CollectionAssert.Contains(large, "heavy_turret");
            CollectionAssert.DoesNotContain(large, "artillery_emplacement");
            CollectionAssert.DoesNotContain(PlayerProfile.BaseLoadout.Towers, "artillery_emplacement");

            // The gunship items are gone from the bag.
            Assert.AreEqual(0, PlayerProfile.ItemCount("gunship_support"));

            // The menu's notice counts the coins once.
            Assert.AreEqual(expected, PlayerProfile.TakeRosterNews().coins, "the notice's coins");
            Assert.AreEqual(0, PlayerProfile.TakeRosterNews().coins, "once");

            // Saved and read back: nothing of the deleted cards is left, and the migration does not run twice.
            var json = PlayerProfile.JsonForTests();
            foreach (var gone in new[] { "bmpt", "smoke_screen", "artillery_emplacement", "gunship_support" })
                StringAssert.DoesNotContain("\"" + gone + "\"", json, gone + " is out of the save");
            PlayerProfile.LoadForTests(json);
            Assert.AreEqual(expected, PlayerProfile.Coins, "no second refund");
        }
    }
}
