using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Modes;
using MachineBrigade.Sim.Sandbox;

namespace MachineBrigade.Tests
{
    /// <summary>Prompt 30 L5: the endless part's numbers and the reopening of a won match. Written in the cloud, not yet run.</summary>
    public class EndlessTests
    {
        [Test]
        public void StatsGrowAndCoinsDecay()
        {
            Assert.AreEqual(1.4f, EndlessRules.EnemyScale(10), 1e-4f, "+4 % a wave");
            Assert.AreEqual(1.2f, EndlessRules.PlayerScale(10), 1e-4f, "+2 % a wave");
            Assert.AreEqual(1.3f, EndlessRules.PlayerScale(40), 1e-4f, "at most +30 %");
            Assert.AreEqual(1.8f, EndlessRules.EnemyScale(10, bosses: true), 1e-4f, "Boss Rush +8 % a boss");
            Assert.AreEqual(1f, EndlessRules.PlayerScale(10, bosses: true), "the player gets nothing more in Boss Rush");
            Assert.AreEqual(18, EndlessRules.Coins(0));
            Assert.AreEqual(16, EndlessRules.Coins(1));
            Assert.AreEqual(60, EndlessRules.Coins(0, bosses: true));
            Assert.AreEqual(54, EndlessRules.Coins(1, bosses: true));
            Assert.AreEqual(10, EndlessRules.Capped(18, 590), "the day's 600 over every mode");
            Assert.AreEqual(0, EndlessRules.Capped(18, 600));
            Assert.AreEqual(20, EndlessRules.BadgeAt(20));
            Assert.AreEqual(0, EndlessRules.BadgeAt(15));
            Assert.AreEqual(5, EndlessRules.BadgeAt(5, bosses: true));
            Assert.AreEqual(1, EndlessRules.BossOfWave(5), "a mini boss at wave 5");
            Assert.AreEqual(2, EndlessRules.BossOfWave(10), "a main boss at wave 10, instead of the mini");
            Assert.AreEqual(1, EndlessRules.BossOfWave(15));
            Assert.AreEqual(0, EndlessRules.BossOfWave(7));
        }

        [Test]
        public void AWonMatchReopensForTheEndlessPart()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), SandboxMaps.Flat(), 1);
            Assert.IsFalse(world.ContinueMatch(), "only a resolved match continues");
            world.IsOver = true;
            Assert.AreEqual(MatchPhase.Resolved, world.Ending.Phase);
            world.Ending.ShowResults();
            Assert.IsTrue(world.ContinueMatch());
            Assert.IsFalse(world.IsOver);
            Assert.AreEqual(MatchPhase.Running, world.Ending.Phase);
            Assert.AreEqual(1, world.Ending.Continued);
            var before = world.Tick;
            world.Step(0.05f);
            Assert.AreEqual(before + 1, world.Tick, "the battle runs again");
            world.SetTeamStats(1, 1.4f, 1.4f);
            Assert.AreEqual(1.4f, world.TeamStats(1).hp, 1e-4f);
        }

        [Test]
        public void SurvivalIsTenWavesThenOptional()
        {
            var mode = new SandboxMode();
            Assert.AreEqual(10, mode.FiniteWaves);
            Assert.IsFalse(mode.CanContinue, "nothing to continue before the win");
            Assert.IsNull(mode.Result);
        }
    }
}
