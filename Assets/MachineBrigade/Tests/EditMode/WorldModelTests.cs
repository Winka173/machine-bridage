using System.Collections.Generic;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Tests
{
    /// <summary>Prompt 28 pass 1: the parameter frame (L), the World Model (A) and determinism (N).</summary>
    public class WorldModelTests
    {
        private static (SimWorld world, ConquestMode mode, ConquestAi a, ConquestAi b) Match(int seed, Catalog catalog = null)
        {
            var world = new SimWorld(catalog ?? GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_conquest"), seed: seed);
            var mode = new ConquestMode(new ConquestRules
            {
                PlayerVehicles = MatchSettings.AllVehicles,
                PlayerSupports = MatchSettings.AllSupports,
                EnemyVehicles = MatchSettings.AllVehicles,
                EnemySupports = MatchSettings.AllSupports,
            });
            mode.Setup(world);
            world.Intel.Objectives = mode;
            return (world, mode, new ConquestAi(mode, 0, 1, AiDifficulty.Hard, seed + 1), new ConquestAi(mode, 1, 0, AiDifficulty.Normal, seed + 2));
        }

        private static void Step(SimWorld world, ConquestMode mode, ConquestAi a, ConquestAi b, float step = 0.05f)
        {
            mode.Tick(world, step);
            a.Tick(world, step);
            b.Tick(world, step);
            world.Step(step);
            world.ClearEvents();
        }

        [Test]
        public void EveryAiParameterHasAValueInsideItsRangeAndAMetric()
        {
            var ai = GameContent.LoadCatalog().Ai;
            var keys = ai.Keys.ToList();
            Assert.That(keys.Count(k => k.StartsWith("params.")), Is.EqualTo(21), "the sheet's 21 parameters");
            Assert.That(keys, Does.Contain("economy.armyBands.2").And.Contain("economy.escalation.3").And.Contain("world.cell"));
            foreach (var key in keys)
            {
                var p = ai.Param(key);
                Assert.That(p.Value, Is.InRange(p.Min, p.Max), key);
                Assert.That(p.Metric, Is.Not.Empty, key + ": a measurement metric (L.1)");
            }
            Assert.That(ai.ArmyBandEdges.Count, Is.EqualTo(3));
            Assert.That(ai.With("params.switchMargin", 15f).SwitchMargin, Is.EqualTo(15f));
            Assert.That(ai.SwitchMargin, Is.EqualTo(8f), "With copies");
        }

        [Test]
        public void ASideKnowsOnlyWhatItSeesAndForgetsSlowly()
        {
            var (world, mode, a, b) = Match(21);
            var stale = 0;
            for (var t = 0f; t < 120f; t += 0.05f)
            {
                Step(world, mode, a, b);
                if (world.Tick % 20 != 0) continue;
                foreach (var team in new[] { 0, 1 })
                {
                    var intel = world.Intel.For(team);
                    foreach (var c in intel.Contacts)
                    {
                        world.TryGetVehicle(c.Id, out var v);
                        if (c.InSight)
                        {
                            Assert.That(v != null && v.IsVisibleTo(team), Is.True, $"{c} is in sight only when visible");
                            Assert.That(c.Confidence(world.Time, intel.ConfidenceDecay), Is.EqualTo(1f));
                        }
                        else
                        {
                            stale++;
                            Assert.That(c.Confidence(world.Time, intel.ConfidenceDecay), Is.LessThan(1f));
                        }
                    }
                }
            }
            Assert.That(stale, Is.GreaterThan(0), "out-of-sight enemies are remembered with falling confidence");
        }

        [Test]
        public void AskingTheWorldModelNeverChangesTheBattle()
        {
            var (w1, m1, a1, b1) = Match(33);
            var (w2, m2, a2, b2) = Match(33);
            for (var t = 0f; t < 90f; t += 0.05f)
            {
                Step(w1, m1, a1, b1);
                Step(w2, m2, a2, b2);
                w1.Intel.For(0);
                w1.Intel.For(1);
            }
            Assert.That(Snapshot(w1), Is.EqualTo(Snapshot(w2)));
        }

        [Test]
        public void TheSameSeedReplaysTheSamePictureAndEvents()
        {
            string Run()
            {
                var (world, mode, a, b) = Match(45);
                var trace = new StringBuilder();
                for (var t = 0f; t < 90f; t += 0.05f)
                {
                    Step(world, mode, a, b);
                    if (world.Tick % 10 != 0) continue;
                    foreach (var team in new[] { 0, 1 })
                    {
                        var intel = world.Intel.For(team);
                        trace.Append(team).Append(':').Append(intel.Contacts.Count).Append('/').Append(intel.EnemyTotal.ToString("0.000"))
                            .Append('/').Append(intel.Front.Count).Append('|');
                        foreach (var e in intel.Events) trace.Append(e.Kind).Append(e.Reason).Append(e.Created.ToString("0.00")).Append(';');
                    }
                    trace.Append('\n');
                }
                return trace + Snapshot(world);
            }
            Assert.That(Run(), Is.EqualTo(Run()));
            Assert.That(new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_conquest"), seed: 5).AiRandom(0, 1).Next(),
                Is.EqualTo(new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_conquest"), seed: 5).AiRandom(0, 1).Next()));
        }

        private static string Snapshot(SimWorld world)
        {
            var s = new StringBuilder();
            foreach (var v in world.Vehicles.OrderBy(v => v.Id.Value))
                s.Append(v.Id.Value).Append(v.Def.Id).Append(v.Position.X.ToString("0.000")).Append(',').Append(v.Position.Y.ToString("0.000"))
                    .Append(',').Append(v.Hp.ToString("0.0")).Append(';');
            return s.ToString();
        }
    }
}
