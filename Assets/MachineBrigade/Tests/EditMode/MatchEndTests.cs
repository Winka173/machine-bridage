using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Sandbox;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 30 L3: the end sequence. Once resolved the battle stands still, so the result is the same with or without the
    /// presentation, and a replay resolves on the same tick. Written in the cloud session, not yet run.
    /// </summary>
    public class MatchEndTests
    {
        private const float Step = 0.05f;
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static string Tank() =>
            Catalog.Vehicles.Values.First(d => !d.Static && !d.Flying && !d.Boss && d.Mounts.Count > 0 && d.CpCost > 0).Id;

        /// <summary>Two tanks a side facing each other; the match ends when the first vehicle dies.</summary>
        private static SimWorld Battle(int seed)
        {
            var world = new SimWorld(Catalog, SandboxMaps.Flat(), seed);
            var id = Tank();
            for (var i = 0; i < 2; i++)
            {
                world.SpawnVehicle(id, 0, new Vector2(-25f, i * 8f), 0f);
                world.SpawnVehicle(id, 1, new Vector2(25f, i * 8f), 180f);
            }
            return world;
        }

        private static void RunToEnd(SimWorld world, int maxSteps = 6000)
        {
            var start = world.Vehicles.Count;
            for (var i = 0; i < maxSteps && !world.IsOver; i++)
            {
                world.Step(Step);
                world.ClearEvents();
                if (world.Vehicles.Count(v => v.IsAlive) < start) world.IsOver = true;
            }
        }

        private static string Snapshot(SimWorld world)
        {
            var sb = new StringBuilder();
            sb.Append(world.Tick).Append('|').Append(world.Time.ToString("R"));
            foreach (var v in world.Vehicles.OrderBy(v => v.Id.Value))
                sb.Append('|').Append(v.Id.Value).Append(':').Append(v.Hp.ToString("R")).Append(':')
                    .Append(v.Position.X.ToString("R")).Append(',').Append(v.Position.Y.ToString("R"));
            for (var team = 0; team <= 1; team++)
                if (world.TryGetEconomy(team, out var e)) sb.Append("|cp").Append(team).Append(':').Append(e.Cp.ToString("R"));
            return sb.ToString();
        }

        [Test]
        public void TheBattleStandsStillOnceResolved()
        {
            var world = Battle(7);
            RunToEnd(world);
            Assert.That(world.IsOver, Is.True, "the scenario ends");
            Assert.AreEqual(MatchPhase.Resolved, world.Ending.Phase);
            Assert.AreEqual(world.Tick, world.Ending.ResolvedTick);
            var frozen = Snapshot(world);
            world.Ending.BeginPresentation(EndKind.FirstBigWin);
            for (var i = 0; i < 400; i++)
            {
                world.Step(Step);
                world.Ending.Advance(Step * 0.3); // slow motion is the view's alone
            }
            Assert.AreEqual(frozen, Snapshot(world), "no movement, damage, CP or time after the resolve");
            Assert.That(world.Submit(new Sim.Commands.Command(Sim.Commands.CommandType.Stop, 0, new EntityId[0], default)).Accepted, Is.False);
        }

        [Test]
        public void TheResultIsTheSameWithOrWithoutThePresentation()
        {
            var shown = Battle(11);
            var skipped = Battle(11);
            RunToEnd(shown);
            RunToEnd(skipped);
            shown.Ending.BeginPresentation(EndKind.FirstWin);
            for (var i = 0; i < 200; i++)
            {
                shown.Step(Step);
                shown.Ending.Advance(Step);
            }
            skipped.Ending.ShowResults();
            for (var i = 0; i < 200; i++) skipped.Step(Step);
            Assert.AreEqual(MatchPhase.Results, shown.Ending.Phase, "the presentation ends by itself");
            Assert.AreEqual(MatchPhase.Results, skipped.Ending.Phase);
            Assert.AreEqual(Snapshot(skipped), Snapshot(shown));
            Assert.AreEqual(skipped.Ending.ResolvedTick, shown.Ending.ResolvedTick, "a replay resolves on the same tick");
        }

        [Test]
        public void ATapSkipsOnlyAfterThreeQuartersOfASecond()
        {
            var end = new MatchEnd();
            var world = Battle(3);
            world.IsOver = true;
            world.Ending.BeginPresentation(EndKind.Replay);
            Assert.That(world.Ending.Skip(), Is.False);
            world.Ending.Advance(0.5);
            Assert.That(world.Ending.Skip(), Is.False);
            world.Ending.Advance(0.3);
            Assert.That(world.Ending.Skip(), Is.True);
            Assert.That(world.Ending.Skipped, Is.True);
            Assert.AreEqual(MatchPhase.Results, world.Ending.Phase);
            Assert.AreEqual(MatchPhase.Running, end.Phase);
            Assert.That(MatchEnd.DurationFor(EndKind.FirstBigWin), Is.InRange(6.0, 8.0));
            Assert.That(MatchEnd.DurationFor(EndKind.FirstWin), Is.InRange(4.0, 5.0));
            Assert.That(MatchEnd.DurationFor(EndKind.Replay), Is.InRange(2.5, 4.0));
            Assert.That(MatchEnd.DurationFor(EndKind.Loss), Is.InRange(3.0, 4.0));
        }
    }
}
