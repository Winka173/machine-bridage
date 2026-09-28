using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Tests
{
    /// <summary>Prompt 13 H.7: the base strength number (Base screen, Defend and Endless waves).</summary>
    public class BaseStrengthTests
    {
        [Test]
        public void TheMidLevelEnemyBaseIsTheHundredMarkAndUpgradesAndLevelsRaiseIt()
        {
            var catalog = GameContent.LoadCatalog();
            var reference = BaseLoadout.ForAi(catalog, "Normal", "default", 1, 3);
            Assert.AreEqual(100f, BaseStrength.Score(catalog, reference), 0.01f, "the mark");
            var top = BaseLoadout.ForAi(catalog, "Normal", "default", 1, 5);
            Assert.Greater(BaseStrength.Score(catalog, top), 120f, "HQ level 5 opens more slots");
            Assert.Less(BaseStrength.Score(catalog, BaseLoadout.HqOnly(1)), 40f, "a bare HQ");
            // Rank and equipment: a quarter more health and damage on every structure.
            var upgraded = BaseStrength.Score(catalog, reference, _ => new VehicleBoost(1.25f, 1.25f, 1f, 1f, 1f, 0f, SpecialModule.None, 0f));
            Assert.AreEqual(125f, upgraded, 0.5f, "√(1.25 × 1.25)");
            Assert.AreEqual(1f, BaseStrength.WaveScale(100f), 1e-4f);
            Assert.Greater(BaseStrength.WaveScale(200f), 1.5f);
            Assert.AreEqual(0.75f, BaseStrength.WaveScale(10f), 1e-4f);
        }
    }
}
