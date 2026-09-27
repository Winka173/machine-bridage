using System.Collections.Generic;
using NUnit.Framework;
using MachineBrigade.Game.Match;

namespace MachineBrigade.Tests
{
    /// <summary>Daily challenges: three distinct ones a day, progress capped at the target, paid once.</summary>
    public class DailyTests
    {
        [SetUp]
        public void SetUp() => PlayerProfile.ResetForTests();

        [TearDown]
        public void TearDown() => PlayerProfile.Load();

        [Test]
        public void EachDayHasThreeDifferentChallenges()
        {
            for (var day = 20260901; day < 20260931; day++)
            {
                var kinds = new HashSet<string>();
                foreach (var task in DailyMissions.For(day)) kinds.Add(task.Kind);
                Assert.AreEqual(3, kinds.Count, $"day {day}");
            }
            Assert.AreEqual(DailyMissions.For(20260927)[0].Kind, DailyMissions.For(20260927)[0].Kind, "the same for everyone on a date");
        }

        [Test]
        public void FinishedChallengePaysOnce()
        {
            var task = DailyMissions.Current[0];
            DailyMissions.Record(task.Kind, task.Target + 5);
            Assert.AreEqual(task.Target, DailyMissions.Progress(0), "progress stops at the target");
            var before = PlayerProfile.Coins;
            Assert.IsTrue(DailyMissions.Claim(0));
            Assert.AreEqual(before + task.Reward, PlayerProfile.Coins);
            Assert.IsFalse(DailyMissions.Claim(0), "and only once");
        }
    }
}
