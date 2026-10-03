using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Tests
{
    /// <summary>The weekly fortress starting where the last attack got to, mission tiers and each mission's own third star.</summary>
    public class ChallengeTests
    {
        private static SiegeMode Siege(SimWorld world, int startStage)
        {
            var mode = new SiegeMode(new SiegeRules
            {
                StartStage = startStage,
                Attacker = new SideSetup { StartCp = 30f, Income = 1.6f },
                Defender = new SideSetup { StartCp = 16f, Income = 0.8f },
            });
            mode.Setup(world);
            return mode;
        }

        [Test]
        public void TheWeeklyFortressResumesAtTheStageReached()
        {
            var fresh = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("greenvale_siege"), seed: 7);
            var full = Siege(fresh, 1);
            var defencesAtStart = fresh.VehicleList.Count(v => v.Team == 1 && v.Def.Static);
            Assert.AreEqual(1, full.Stage);

            var second = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("greenvale_siege"), seed: 7);
            var resumed = Siege(second, 2);
            Assert.AreEqual(2, resumed.Stage, "the outer line was broken earlier this week");
            Assert.IsTrue(second.Props.Where(p => p.Def.Id == "radar_station_prop").All(p => !p.IsAlive), "its relays are gone");
            Assert.Less(second.VehicleList.Count(v => v.Team == 1 && v.Def.Static), defencesAtStart, "and its guns");
            Assert.Greater(resumed.SecondsLeft(second), full.SecondsLeft(fresh), "the clock carries the stage's bonus");

            var third = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("greenvale_siege"), seed: 7);
            var keep = Siege(third, 3);
            Assert.AreEqual(3, keep.Stage, "straight at the keep");
            Assert.IsTrue(third.VehicleList.Any(v => v.Def.Id == "mobile_fortress"), "its guardian is awake");
        }

        [Test]
        public void EachMissionHasItsOwnThirdStar()
        {
            var noStrikes = Campaign.All.First(m => m.Challenge == "NoStrikes");
            Assert.AreEqual(3, Rewards.Stars(noStrikes, true, 1f, 99, challenge: true), "the challenge met: three stars whatever the losses");
            Assert.AreEqual(2, Rewards.Stars(noStrikes, true, 1f, 0, challenge: false), "not met: the third star is lost");
            var plain = Campaign.All.First(m => m.Challenge == null && m.StarLosses >= 0);
            Assert.AreEqual(3, Rewards.Stars(plain, true, 1f, plain.StarLosses), "no challenge: the losses rule");
            Assert.AreEqual(2, Rewards.Stars(plain, true, 1f, plain.StarLosses + 1));
        }

        [Test]
        public void HarderTiersLeaveTheMissionAsItIs()
        {
            var waves = Campaign.All.First(m => m.Waves != null);
            var size = waves.Waves.Size;
            var cp = waves.EnemyCp;
            var heroic = waves.Harder(1.3f);
            Assert.Greater(heroic.EnemyCp, cp);
            Assert.Greater(heroic.Waves.Size, size - 1);
            Assert.AreEqual(cp, waves.EnemyCp, "the mission itself is unchanged");
            Assert.AreEqual(size, waves.Waves.Size);
            Assert.AreEqual(1.5f, Rewards.TierPay(1));
            Assert.AreEqual(2f, Rewards.TierPay(2));
        }
    }
}
