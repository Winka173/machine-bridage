using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Balance pack (lane B, rule B): the gameplay constants moved to Resources/Data/tunables.json. The shipped file
    /// names every key the code reads, and its values equal the code's defaults (so moving them changed no battle:
    /// ReplayHashTests checks the battles themselves).
    /// </summary>
    public class TunablesTests
    {
        [TearDown]
        public void TearDown() => GameContent.LoadTunables();

        [Test]
        public void TheShippedFileSetsEveryKey()
        {
            var keys = SimTunables.Keys.ToList();
            var set = SimTunables.Apply(LoadText());
            Assert.AreEqual("", string.Join(", ", SimTunables.Problems), "keys the file has but the code does not read");
            Assert.AreEqual(keys.Count, set, "every key the code reads is in the file");
            Assert.AreEqual(keys.Count, keys.Distinct().Count(), "no key twice");
        }

        [Test]
        public void TheShippedValuesAreTheCodesDefaults()
        {
            SimTunables.Apply(LoadText());
            var moved = SimTunables.Keys.Where(k => SimTunables.ValueText(k) != SimTunables.DefaultText(k))
                .Select(k => k + " = " + SimTunables.ValueText(k) + " (code " + SimTunables.DefaultText(k) + ")").ToList();
            Assert.AreEqual("", string.Join("\n", moved), "the file and the code's defaults agree");
        }

        [Test]
        public void AValueInTheFileReachesTheCode()
        {
            SimTunables.Apply("{ \"weapons\": { \"combatSystem\": { \"retargetSeconds\": { \"value\": 0.75 } } }, " +
                              "\"modes\": { \"endlessRules\": { \"waveBadges\": [ 5, 15 ] } } }");
            Assert.AreEqual(0.75f, SimTunables.Weapons.CombatSystem.RetargetSeconds, 1e-6f);
            CollectionAssert.AreEqual(new[] { 5, 15 }, SimTunables.Modes.EndlessRules.WaveBadges);
            Assert.AreEqual(SimTunables.DefaultText("modes.economySystem.killReward"), SimTunables.ValueText("modes.economySystem.killReward"),
                "a key the file leaves out keeps the code's default");
            SimTunables.Apply("{ \"weapons\": { \"nope\": { \"x\": 1 } } }");
            CollectionAssert.Contains(SimTunables.Problems, "weapons.nope.x", "an unknown key is reported, not applied");
        }

        private static string LoadText() =>
            System.IO.File.ReadAllText(System.IO.Path.Combine(UnityEngine.Application.dataPath, "MachineBrigade", "Resources", "Data", "tunables.json"));
    }
}
