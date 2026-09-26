using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Tests
{
    /// <summary>Automatic behaviour: guarding, target choice and the tactical opponent.</summary>
    public class AiTests
    {
        [Test]
        public void IdleVehicleEngagesAnEnemyThatOutrangesIt()
        {
            var world = TestWorlds.World();
            var tank = world.SpawnVehicle("tank", 0, Vector2.Zero, 0f);
            var arty = world.SpawnVehicle("arty", 1, new Vector2(28f, 0f), 0f);

            TestWorlds.Run(world, 8f);

            Assert.IsTrue(tank.IsAlive);
            Assert.Less(arty.Hp, arty.MaxHp, "the tank should drive into range and hit back");
        }

        [Test]
        public void IdleVehicleReturnsToItsPostOnceTheThreatLeaves()
        {
            var world = TestWorlds.World();
            var tank = world.SpawnVehicle("tank", 0, Vector2.Zero, 0f);
            var decoy = world.SpawnVehicle("decoy", 1, new Vector2(26f, 0f), 0f);

            TestWorlds.Run(world, 3f);
            Assert.Greater(tank.Position.X, 2f, "the tank should close in on the enemy it can see");

            world.Submit(new Command(CommandType.Move, 1, new[] { decoy.Id }, new Vector2(46f, 30f)));
            TestWorlds.Run(world, 16f);

            Assert.Less(Vector2.Distance(tank.Position, Vector2.Zero), 3f, "the tank should drive back to its post");
            Assert.AreEqual(OrderKind.Idle, tank.Order.Kind);
        }

        [Test]
        public void AutoTargetingFinishesADamagedTargetBeforeANearerHealthyOne()
        {
            var world = TestWorlds.World();
            var tank = world.SpawnVehicle("tank", 0, Vector2.Zero, 0f);
            var damaged = world.SpawnVehicle("dummy", 1, new Vector2(12f, 0f), 0f);
            var nearer = world.SpawnVehicle("dummy", 1, new Vector2(0f, 8f), 0f);
            TestWorlds.Run(world, TestWorlds.Step); // spot the enemies

            Assert.IsTrue(world.Submit(new Command(CommandType.Attack, 0, new[] { tank.Id }, default, damaged.Id)).Accepted);
            TestWorlds.Run(world, 3.2f);
            Assert.Less(damaged.Hp, nearer.Hp);
            world.Submit(new Command(CommandType.Stop, 0, new[] { tank.Id }));
            TestWorlds.Run(world, 0.1f);

            Assert.AreEqual(damaged.Id, tank.Target);
        }

        [Test]
        public void ArtilleryBacksAwayFromEnemiesInsideItsMinimumRange()
        {
            var world = TestWorlds.World();
            var arty = world.SpawnVehicle("arty", 1, Vector2.Zero, 0f);
            var enemy = world.SpawnVehicle("dummy", 0, new Vector2(8f, 0f), 0f);
            var ai = new TacticalAi(1, 0);

            Run(world, ai, 7f);

            Assert.Greater(Vector2.Distance(arty.Position, enemy.Position), TestWorlds.Howitzer.MinRange);
        }

        [Test]
        public void BadlyDamagedHeavyVehiclePullsBackBehindTheLine()
        {
            var world = TestWorlds.World();
            var ai = new TacticalAi(1, 0);
            var line = new Vehicle[3];
            for (var i = 0; i < line.Length; i++) line[i] = world.SpawnVehicle("tank", 1, new Vector2(i * 4f, 0f), 0f);
            var enemy = world.SpawnVehicle("decoy", 0, new Vector2(4f, 26f), 0f);
            var wounded = line[1];
            wounded.Hp = wounded.MaxHp * 0.2f;
            TestWorlds.Run(world, TestWorlds.Step); // spot the enemy

            var before = Vector2.Distance(wounded.Position, enemy.Position);
            ai.Tick(world, 1f);

            Assert.AreEqual(OrderKind.Move, wounded.Order.Kind, "the wounded tank should be ordered back");
            TestWorlds.Run(world, 3f);
            Assert.Greater(Vector2.Distance(wounded.Position, enemy.Position), before + 4f);
        }

        private static void Run(SimWorld world, TacticalAi ai, float seconds)
        {
            var steps = (int)(seconds / TestWorlds.Step + 0.5f);
            for (var i = 0; i < steps; i++)
            {
                ai.Tick(world, TestWorlds.Step);
                world.Step(TestWorlds.Step);
            }
        }
    }
}
