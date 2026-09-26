using System.Collections.Generic;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Tests
{
    /// <summary>The player's army fights on its own; the player steers intent or takes vehicles by hand.</summary>
    public class CommanderTests
    {
        private static SimWorld TwoPointWorld() =>
            new SimWorld(TestWorlds.Catalog(), new MapDefinition("test", 100f,
                new[] { new TeamStart(0, new Vector2(0f, -40f)), new TeamStart(1, new Vector2(0f, 40f)) },
                new List<PropPlacement>(), new List<UnitPlacement>(),
                new[] { new CapturePointDef("left", "left", new Vector2(-30f, 0f), 8f), new CapturePointDef("right", "right", new Vector2(30f, 0f), 8f) }));

        private static void Run(SimWorld world, ConquestMode mode, ConquestAi ai, float seconds)
        {
            for (var i = 0; i < (int)(seconds / TestWorlds.Step + 0.5f); i++)
            {
                mode?.Tick(world, TestWorlds.Step);
                ai.Tick(world, TestWorlds.Step);
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
        }

        [Test]
        public void FocusPointSendsTheArmyThere()
        {
            var world = TwoPointWorld();
            var mode = new ConquestMode(new ConquestRules { Tickets = 1000 });
            mode.Setup(world);
            var ai = new ConquestAi(mode, 0, 1, AiDifficulty.Hard) { FocusPoint = "right", AutoDeploy = false, AutoStrike = false };
            var tanks = new[]
            {
                world.SpawnVehicle("tank", 0, new Vector2(-3f, -40f), 0f),
                world.SpawnVehicle("tank", 0, new Vector2(3f, -40f), 0f),
            };

            Run(world, mode, ai, 20f);

            foreach (var t in tanks) Assert.Greater(t.Position.X, 10f, "the army heads for the chosen point");
        }

        [Test]
        public void HandOrderedVehiclesAreLeftAloneForAWhile()
        {
            var world = TwoPointWorld();
            var mode = new ConquestMode(new ConquestRules { Tickets = 1000 });
            mode.Setup(world);
            var ai = new ConquestAi(mode, 0, 1, AiDifficulty.Hard) { FocusPoint = "right", AutoDeploy = false, AutoStrike = false };
            var tank = world.SpawnVehicle("tank", 0, new Vector2(0f, -40f), 0f);

            world.Submit(new Command(CommandType.Move, 0, new[] { tank.Id }, new Vector2(-20f, -30f), manual: true));
            Run(world, mode, ai, 12f);
            Assert.Less(Vector2.Distance(tank.Position, new Vector2(-20f, -30f)), 3f, "the hand order is carried out");
            Assert.IsTrue(tank.UnderPlayerControl(world.Time), "and the commander keeps its hands off after arrival");

            Run(world, mode, ai, 30f);
            Assert.IsFalse(tank.UnderPlayerControl(world.Time));
            Assert.Greater(tank.Position.X, 0f, "then the commander takes it back");
        }

        [Test]
        public void AutoDeployOffBuysNothing()
        {
            var world = TwoPointWorld();
            var mode = new ConquestMode(new ConquestRules { Tickets = 1000, StartCp = 30f });
            mode.Setup(world);
            var ai = new ConquestAi(mode, 0, 1, AiDifficulty.Hard) { AutoDeploy = false, AutoStrike = false };

            Run(world, mode, ai, 5f);

            Assert.AreEqual(0, world.CountAlive(0));
            world.TryGetEconomy(0, out var economy);
            Assert.GreaterOrEqual(economy.Cp, 30f);

            ai.AutoDeploy = true;
            Run(world, mode, ai, 5f);
            Assert.Greater(world.CountAlive(0), 0, "with auto buy on, it spends");
        }

        [Test]
        public void WithoutObjectivesTheCommanderHoldsItsLine()
        {
            var world = TestWorlds.World();
            world.EnableEconomy(new TeamEconomy(0, 0f, income: 0f));
            var ai = new ConquestAi(null, 0, 1, AiDifficulty.Hard) { DefendPoint = new Vector2(10f, 10f), AutoDeploy = false, AutoStrike = false };
            var tank = world.SpawnVehicle("tank", 0, new Vector2(-30f, -30f), 0f);

            Run(world, null, ai, 20f);

            Assert.Less(Vector2.Distance(tank.Position, new Vector2(10f, 10f)), 8f);
        }
    }
}
