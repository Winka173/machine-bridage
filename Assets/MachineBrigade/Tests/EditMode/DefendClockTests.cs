using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Owner fix 11 (2026-10-03): Defend's clock reads matchRules defend.timeLimit (720 s) instead of the code's
    /// 480 + 150 = 630 s. At Normal the start plus both stage bonuses equals the data; the other difficulties keep their
    /// offset from Normal. Only the session is built (no tick). Written by lane A, not yet run.
    /// </summary>
    public class DefendClockTests
    {
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static SiegeMode Build(AiDifficulty difficulty, out SimWorld world)
        {
            var kept = MatchSettings.Difficulty;
            try
            {
                MatchSettings.Difficulty = difficulty;
                world = new SimWorld(Catalog, GameContent.LoadMap(ModeSession.MapFile(GameModeKind.Defend, "greenvale")), seed: 1);
                var session = ModeSession.Create(GameModeKind.Defend, false, world, 1);
                Assert.IsInstanceOf<SiegeMode>(session.Mode, "Defend runs on the siege mode");
                return (SiegeMode)session.Mode;
            }
            finally
            {
                MatchSettings.Difficulty = kept;
            }
        }

        private static float BonusTotal(SiegeRules rules)
        {
            var total = 0f;
            foreach (var bonus in rules.StageBonus) total += bonus;
            return total;
        }

        [Test]
        public void TheDefendSessionsLimitIsTheDataValue()
        {
            var limit = Catalog.MatchRules.For("defend").Get("timeLimit", 0f);
            Assert.Greater(limit, 0f, "matchRules defend.timeLimit is set");
            var mode = Build(AiDifficulty.Normal, out var world);
            Assert.AreEqual(limit, mode.Rules.StartSeconds + BonusTotal(mode.Rules), 0.001f, "Normal: start + stage bonuses = the data's timeLimit");
            Assert.AreEqual(mode.Rules.StartSeconds, mode.SecondsLeft(world), 0.001f, "the clock starts at the start");
        }

        [Test]
        public void TheDifficultiesKeepTheirOffsetFromNormal()
        {
            var normal = Build(AiDifficulty.Normal, out _).Rules.StartSeconds;
            Assert.AreEqual(normal + 60f, Build(AiDifficulty.Hard, out _).Rules.StartSeconds, 0.001f, "Hard: 60 s longer");
            Assert.AreEqual(normal - 60f, Build(AiDifficulty.Easy, out _).Rules.StartSeconds, 0.001f, "Easy: 60 s shorter");
        }
    }
}
