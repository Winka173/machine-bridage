using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 30 L4: each mode's win, loss, overtime and draw rules on made-up states (the clock moved by one long step on
    /// an empty map, the scores given), the campaign's stars, the leaderboards' orders and the Operations losses by base
    /// CP. No battle is simulated. Written in the cloud session, not yet run.
    /// </summary>
    public class MatchRulesTests
    {
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static SimWorld EmptyWorld() =>
            new SimWorld(Catalog, new MapDefinition("rules", 100f,
                new[] { new TeamStart(0, new Vector2(-40f, -40f)), new TeamStart(1, new Vector2(40f, 40f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));

        [Test]
        public void TheDataHasEveryModesRules()
        {
            foreach (var mode in new[] { "conquest", "deathmatch", "hill", "assault", "siege", "defend", "survival", "endless", "bossrush", "weekly", "operations" })
            {
                var rules = Catalog.MatchRules.For(mode);
                Assert.IsNotNull(rules, mode);
                foreach (var field in new[] { "winCondition", "loseCondition", "timeLimit", "overtimeRule", "drawRule", "scoreRule", "catchUpPolicy" })
                    Assert.IsTrue(rules.Text.ContainsKey(field), $"{mode}.{field}");
            }
            Assert.AreEqual(500f, Catalog.MatchRules.For("conquest").Get("points", 0f));
            Assert.AreEqual(18f, Catalog.MatchRules.For("deathmatch").Get("killCap", 0f));
            Assert.AreEqual(0.25f, Catalog.MatchRules.For("conquest").Get("catchUpMax", 0f));
        }

        [Test]
        public void ConquestAtTheLimitThenOvertimeThenDraw()
        {
            var world = EmptyWorld();
            var mode = new ConquestMode(new ConquestRules { RulesId = null, TimeLimit = 600f, Overtime = 60f, BaseDefences = false, Outposts = false });
            mode.Setup(world);
            Assert.IsNull(mode.AtTheLimit(world, 1, 1), "no result before the limit");
            world.Step(600f);
            Assert.IsNull(mode.AtTheLimit(world, 1, 1), "level at the limit: overtime starts");
            Assert.IsTrue(mode.InOvertime);
            Assert.IsNull(mode.AtTheLimit(world, 1, 1));
            Assert.AreEqual(ConquestMode.PlayerTeam, mode.AtTheLimit(world, 2, 1), "the first side to take one more point wins");
            var draw = new ConquestMode(new ConquestRules { RulesId = null, TimeLimit = 600f, Overtime = 60f, BaseDefences = false, Outposts = false });
            var w2 = EmptyWorld();
            draw.Setup(w2);
            w2.Step(600f);
            draw.AtTheLimit(w2, 1, 1);
            w2.Step(61f);
            Assert.AreEqual(-1, draw.AtTheLimit(w2, 1, 1), "still level after the overtime: a draw");
        }

        [Test]
        public void ConquestTakesItsNumbersFromTheData()
        {
            var world = EmptyWorld();
            var rules = new ConquestRules { BaseDefences = false, Outposts = false };
            new ConquestMode(rules).Setup(world);
            Assert.AreEqual(500, rules.Tickets);
            Assert.AreEqual(0.8f, rules.Bleed, 1e-4f);
            Assert.AreEqual(600f, rules.TimeLimit);
            Assert.AreEqual(0.25f, world.CatchUpMax, 1e-4f, "catch-up at most +25 %");
        }

        [Test]
        public void DeathmatchScoresCappedBaseCpAndAKillDecidesTheOvertime()
        {
            var world = EmptyWorld();
            var mode = new DeathmatchMode(new DeathmatchRules { RulesId = null, TimeLimit = 540f, Overtime = 60f });
            mode.Setup(world);
            world.Step(540f);
            Assert.IsNull(mode.AtTheLimit(world, 100, 100), "level: overtime");
            Assert.IsTrue(mode.InOvertime);
            world.Step(61f);
            Assert.AreEqual(-1, mode.AtTheLimit(world, 100, 100), "no kill in the overtime: a draw");
            var ledger = new KillLedger { ScoreCap = 18 };
            Assert.AreEqual(18, ledger.ScoreCap);
        }

        [Test]
        public void KingOfTheHillOvertimeWhileContested()
        {
            var world = EmptyWorld();
            var mode = new KingOfTheHillMode(new KingOfTheHillRules { RulesId = null, TimeLimit = 540f, Overtime = 60f });
            var hill = new ObjectiveState(new CapturePointDef("hill", "hill", Vector2.Zero, 8f)) { Owner = 1, Contested = true };
            world.Step(540f);
            Assert.IsNull(mode.AtTheLimit(world, hill), "contested at the limit: overtime");
            hill.Contested = false;
            hill.Owner = 0;
            Assert.AreEqual(0, mode.AtTheLimit(world, hill), "level, one side alone on the hill: it wins");
        }

        [Test]
        public void CampaignStarsByMasteryAndTheMissionsOwnChallenge()
        {
            var stars = Catalog.MatchRules.Stars;
            var escort = new MissionDef { Id = "test", Goal = MissionGoal.Escort };
            var facts = new StarFacts { Won = true, ConvoySent = 5, ConvoyArrived = 4, Kills = 20 };
            Assert.AreEqual(3, stars.Count(escort, facts), "4 of 5 trucks is mastery; 20 kills meets the default third");
            facts.ConvoyArrived = 3;
            Assert.AreEqual(2, stars.Count(escort, facts));
            facts.Won = false;
            Assert.AreEqual(0, stars.Count(escort, facts), "stars are never a loss condition, and a loss has none");
            var own = new MissionDef { Id = "own", Goal = MissionGoal.Capture, Challenge = "NoStrikes" };
            var f2 = new StarFacts { Won = true, LostCp = 10, ArmyCpLeft = 40, UsedStrikes = true };
            Assert.AreEqual(2, stars.Count(own, f2), "the mission's own challenge is its third star");
            foreach (MissionGoal goal in System.Enum.GetValues(typeof(MissionGoal)))
                Assert.IsTrue(stars.Mastery(goal.ToString()).HasValue && stars.Third(goal.ToString()).HasValue, $"{goal} has its star rules");
        }

        [Test]
        public void LeaderboardsSortKeyByKey()
        {
            var board = Catalog.MatchRules.Board("endless");
            Assert.IsNotNull(board);
            BoardEntry E(string who, double waves, double cp, double s)
            {
                var e = new BoardEntry { Player = who };
                e.Values["waves"] = waves;
                e.Values["killedBaseCp"] = cp;
                e.Values["seconds"] = s;
                return e;
            }
            var list = new List<BoardEntry> { E("farm", 20, 9000, 9000), E("far", 21, 100, 100), E("tie", 20, 9000, 9500) };
            list.Sort(board);
            CollectionAssert.AreEqual(new[] { "far", "tie", "farm" }, list.Select(e => e.Player).ToArray(), "waves first; a long farm never passes who got further");
            var rush = Catalog.MatchRules.Board("bossrush");
            var a = new BoardEntry { Player = "a" };
            a.Values["bosses"] = 10;
            a.Values["seconds"] = 900;
            var b = new BoardEntry { Player = "b" };
            b.Values["bosses"] = 10;
            b.Values["seconds"] = 800;
            Assert.Less(rush.Compare(b, a), 0, "same bosses: the faster first");
        }

        [Test]
        public void OperationsLossesCountBaseCp()
        {
            var s = Operations.Data.Scoring;
            var normal = Operations.Tier(0);
            var none = new List<MutatorDef>();
            var all = s.Score(true, 1e6, 0, 0f, normal, none);
            var gone = s.Score(true, 1e6, 150, 0f, normal, none);
            Assert.AreEqual((int)s.Losses, all - gone, "2000 at no loss, nothing from 150 base CP lost");
            Assert.AreEqual(gone, s.Score(true, 1e6, 400, 0f, normal, none));
        }
    }
}
