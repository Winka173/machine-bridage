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

        /// <summary>Pack pass 2: the Defend wave curve, the wave scale and the Trophy APS read the moved numbers as the old literals.</summary>
        [Test]
        public void PassTwoMovesKeepTheOldLiterals()
        {
            SimTunables.Reset();
            var easy = MachineBrigade.Sim.AI.AiDifficulty.Easy;
            var normal = MachineBrigade.Sim.AI.AiDifficulty.Normal;
            var veryHard = MachineBrigade.Sim.AI.AiDifficulty.VeryHard;
            // DefendSession.Build before the move: start 2 / 3 / 4 (endless 4 / 5 / 6), growth 1.8 / 2.0 (endless 1.2), compound 0.06, max 36.
            Assert.AreEqual(2, MachineBrigade.Sim.Modes.SiegeMode.DefendWaveStart(false, easy));
            Assert.AreEqual(3, MachineBrigade.Sim.Modes.SiegeMode.DefendWaveStart(false, normal));
            Assert.AreEqual(4, MachineBrigade.Sim.Modes.SiegeMode.DefendWaveStart(false, veryHard));
            Assert.AreEqual(4, MachineBrigade.Sim.Modes.SiegeMode.DefendWaveStart(true, easy));
            Assert.AreEqual(5, MachineBrigade.Sim.Modes.SiegeMode.DefendWaveStart(true, normal));
            Assert.AreEqual(6, MachineBrigade.Sim.Modes.SiegeMode.DefendWaveStart(true, veryHard));
            Assert.AreEqual(1.8f, MachineBrigade.Sim.Modes.SiegeMode.DefendWaveGrowth(false, normal));
            Assert.AreEqual(2.0f, MachineBrigade.Sim.Modes.SiegeMode.DefendWaveGrowth(false, veryHard));
            Assert.AreEqual(1.2f, MachineBrigade.Sim.Modes.SiegeMode.DefendWaveGrowth(true, normal));
            Assert.AreEqual(0.06f, MachineBrigade.Sim.Modes.SiegeMode.DefendWaveCompound(true));
            Assert.AreEqual(0f, MachineBrigade.Sim.Modes.SiegeMode.DefendWaveCompound(false));
            Assert.AreEqual(36, MachineBrigade.Sim.Modes.SiegeMode.DefendWaveMax);
            foreach (var scale in new[] { 0.75f, 1f, 1.7f, 2.5f })
                for (var wave = 1; wave <= 14; wave++)
                {
                    var old = System.Math.Min(36, (int)System.MathF.Round((5 + 1.2f * (wave - 1)) * System.MathF.Pow(1f + 0.06f, wave - 1) * scale));
                    Assert.AreEqual(old, MachineBrigade.Sim.Modes.SiegeMode.WaveSize(5, 1.2f, 0.06f, 36, scale, wave), $"wave {wave} x{scale}");
                }
            Assert.AreEqual(System.Math.Clamp(System.MathF.Pow(2f, 0.75f), 0.75f, 2.5f), MachineBrigade.Sim.Modes.BaseStrength.WaveScale(200f));
            Assert.AreEqual(0.75f, MachineBrigade.Sim.Modes.BaseStrength.WaveScale(1f));
            // GearSystem.Equip before the move: RETROFIT_ELIGIBLE gets 2 interceptors every 20 s (radius 20 with none of its own).
            var tank = GameContent.LoadCatalog().Vehicles["main_battle_tank"];
            var trophy = MachineBrigade.Sim.Abilities.GearSystem.TrophyAps(tank);
            Assert.IsNotNull(trophy);
            Assert.AreEqual(tank.Aps?.Radius ?? 20f, trophy!.Radius);
            Assert.AreEqual(2, trophy.Charges);
            Assert.AreEqual(20f, trophy.Recharge);
            Assert.AreEqual(0.25f, SimTunables.Weapons.DamageRules.EdgeFalloff);
            Assert.AreEqual(2.2f, SimTunables.Weapons.JamRules.StrikeScatter);
        }

        private static string LoadText() =>
            System.IO.File.ReadAllText(System.IO.Path.Combine(UnityEngine.Application.dataPath, "MachineBrigade", "Resources", "Data", "tunables.json"));
    }
}
