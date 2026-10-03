using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Tests
{
    /// <summary>Balance pack (lane B): the rule C / D changes (Docs/export/CHANGES.md).</summary>
    public class BalancePackRuleTests
    {
        [Test]
        public void AMainRankBossIsNeverTheMutatorsExtraMini()
        {
            // D3: Monster sits in chapter 11's mini slots but is a main boss (play-test 14: in Gungnir's place).
            var catalog = GameContent.LoadCatalog();
            Assert.AreEqual(BossRank.Main, catalog.Vehicles["monster"].Rank);
            foreach (var mission in Campaign.Everything)
            {
                var extra = MissionSession.ExtraBossFor(mission, catalog);
                // Its last fallback is the mission's own boss (on the mission or one of its stages): allowed.
                var own = mission.Boss?.Def;
                if (own == null)
                    foreach (var s in mission.Stages)
                        if (s.Mission.Boss != null)
                        {
                            own = s.Mission.Boss.Def;
                            break;
                        }
                if (extra == null || extra == own) continue;
                Assert.AreNotEqual(BossRank.Main, catalog.Vehicles[extra].Rank, mission.Id + ": " + extra);
            }
        }

        [Test]
        public void TheSupplyThresholdFollowsThePrices()
        {
            // C1: the mode's army cap x the average price factor the starting CP took (1.16), bonuses after it.
            GameContent.LoadTunables();
            Assert.AreEqual(1.16f, SimTunables.Modes.EconomyRules.SupplyPriceScale, 1e-6f);
            Assert.AreEqual(0.25f, SimTunables.Modes.EconomyRules.UpkeepFloor, 1e-6f, "upkeep never takes more than 75 %");
            Assert.AreEqual(1.5f, SimTunables.Modes.EconomyRules.SupplyPerArmyCap, 1e-6f);
        }
    }
}
