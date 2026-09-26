using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Tests
{
    public class CommandTests
    {
        [Test]
        public void CannotCommandAnotherTeamsUnits()
        {
            var world = TestWorlds.World();
            var enemy = world.SpawnVehicle("tank", 1, Vector2.Zero, 0f);

            var result = world.Submit(new Command(CommandType.Move, 0, new[] { enemy.Id }, new Vector2(5f, 5f)));

            Assert.AreEqual(CommandError.NoUnits, result.Error);
            Assert.AreEqual(OrderKind.Idle, enemy.Order.Kind);
        }

        [Test]
        public void RejectsNonFiniteAndOutOfBoundsDestinations()
        {
            var world = TestWorlds.World();
            var tank = world.SpawnVehicle("tank", 0, Vector2.Zero, 0f);

            Assert.AreEqual(CommandError.InvalidPoint,
                world.Submit(new Command(CommandType.Move, 0, new[] { tank.Id }, new Vector2(float.NaN, 0f))).Error);
            Assert.AreEqual(CommandError.OutOfBounds,
                world.Submit(new Command(CommandType.Move, 0, new[] { tank.Id }, new Vector2(500f, 0f))).Error);
        }

        [Test]
        public void MoveReachesTheDestinationAndReturnsToIdle()
        {
            var world = TestWorlds.World(TestWorlds.Prop("house", 0f, 0f));
            var tank = world.SpawnVehicle("tank", 0, new Vector2(-20f, 0f), 0f);

            Assert.IsTrue(world.Submit(new Command(CommandType.Move, 0, new[] { tank.Id }, new Vector2(20f, 0f))).Accepted);
            TestWorlds.Run(world, 20f);

            Assert.Less(Vector2.Distance(tank.Position, new Vector2(20f, 0f)), 1.5f);
            Assert.AreEqual(OrderKind.Idle, tank.Order.Kind);
        }

        [Test]
        public void AttackOrderOnHiddenVehicleIsRejected()
        {
            var world = TestWorlds.World();
            var tank = world.SpawnVehicle("tank", 0, new Vector2(-40f, 0f), 0f);
            var far = world.SpawnVehicle("tank", 1, new Vector2(40f, 0f), 0f);
            world.Step(TestWorlds.Step);

            var result = world.Submit(new Command(CommandType.Attack, 0, new[] { tank.Id }, target: far.Id));

            Assert.AreEqual(CommandError.TargetNotVisible, result.Error);
        }

        /// <summary>V2 R04: a fighting vehicle withdraws immediately and keeps its cooldown.</summary>
        [Test]
        public void RetreatLeavesAFightImmediately()
        {
            var world = TestWorlds.World();
            var tank = world.SpawnVehicle("tank", 0, new Vector2(0f, 0f), 0f);
            var enemy = world.SpawnVehicle("dummy", 1, new Vector2(0f, 15f), SimMath.Tau / 2f);
            TestWorlds.Run(world, 0.5f);
            Assert.AreEqual(enemy.Id, tank.Target, "precondition: the tank is engaging");

            var before = Vector2.Distance(tank.Position, enemy.Position);
            var cooldown = tank.Cooldown;
            Assert.IsTrue(world.Submit(new Command(CommandType.Retreat, 0, new[] { tank.Id })).Accepted);
            Assert.AreEqual(cooldown, tank.Cooldown, "ordering a retreat must not reset the cooldown");

            TestWorlds.Run(world, 2f);

            Assert.AreEqual(OrderKind.Retreat, tank.Order.Kind);
            Assert.Greater(Vector2.Distance(tank.Position, enemy.Position), before + 3f);
        }

        [Test]
        public void StopClearsOrdersAndPath()
        {
            var world = TestWorlds.World();
            var tank = world.SpawnVehicle("tank", 0, Vector2.Zero, 0f);
            world.Submit(new Command(CommandType.Move, 0, new[] { tank.Id }, new Vector2(30f, 0f)));

            world.Submit(new Command(CommandType.Stop, 0, new[] { tank.Id }));
            TestWorlds.Run(world, 2f);

            Assert.AreEqual(OrderKind.Idle, tank.Order.Kind);
            Assert.Less(tank.Position.Length(), 3f, "only residual coasting after stop");
        }

        [Test]
        public void SameSeedAndCommandsGiveTheSameBattle()
        {
            Vector2 Play()
            {
                var world = TestWorlds.World();
                var a = world.SpawnVehicle("mortar", 0, new Vector2(-10f, 0f), 0f);
                world.SpawnVehicle("tank", 1, new Vector2(10f, 3f), 0f);
                world.Submit(new Command(CommandType.AttackMove, 0, new[] { a.Id }, new Vector2(20f, 0f)));
                TestWorlds.Run(world, 10f);
                return a.Position;
            }

            Assert.AreEqual(Play(), Play());
        }
    }
}
