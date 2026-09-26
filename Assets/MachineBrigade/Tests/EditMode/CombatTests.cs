using System.Linq;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Tests
{
    public class CombatTests
    {
        /// <summary>T01: every hit applies its damage exactly once.</summary>
        [Test]
        public void EachShotDamagesExactlyOnce()
        {
            var world = TestWorlds.World();
            world.SpawnVehicle("tank", 0, Vector2.Zero, 0f);
            var target = world.SpawnVehicle("dummy", 1, new Vector2(0f, 10f), 0f);
            world.ClearEvents();

            var fired = 0;
            var impacts = 0;
            var damaged = 0;
            for (var i = 0; i < 15; i++)
            {
                world.Step(TestWorlds.Step);
                fired += world.Events.Count(e => e.Kind == SimEventKind.WeaponFired && e.Team == 0);
                impacts += world.Events.Count(e => e.Kind == SimEventKind.ProjectileImpact && e.Team == 0);
                damaged += world.Events.Count(e => e.Kind == SimEventKind.Damaged && e.Entity == target.Id);
                world.ClearEvents();
            }

            Assert.AreEqual(1, fired, "one shot per 1 s cooldown in 0.75 s");
            Assert.AreEqual(1, impacts);
            Assert.AreEqual(1, damaged);
            Assert.AreEqual(900f, target.Hp, 1e-3f, "100 AP damage x 1.0 against heavy armour");
        }

        [Test]
        public void SplashSparesTheShootersTeam()
        {
            var world = TestWorlds.World();
            world.SpawnVehicle("mortar", 0, new Vector2(0f, -15f), 0f);
            var friend = world.SpawnVehicle("tank", 0, new Vector2(3f, 5f), 0f);
            var enemy = world.SpawnVehicle("dummy", 1, new Vector2(0f, 5f), 0f);

            TestWorlds.Run(world, 0.6f);

            Assert.Less(enemy.Hp, enemy.MaxHp, "the mortar hit its target");
            Assert.AreEqual(friend.MaxHp, friend.Hp, "splash must not hurt friendly vehicles");
        }

        /// <summary>T05: a chain of barrels detonates each barrel once and then stops.</summary>
        [Test]
        public void ChainReactionTerminatesWithOneExplosionPerBarrel()
        {
            var world = TestWorlds.World(
                TestWorlds.Prop("barrel", 0f, 0f), TestWorlds.Prop("barrel", 3f, 0f), TestWorlds.Prop("barrel", 6f, 0f),
                TestWorlds.Prop("barrel", 9f, 0f), TestWorlds.Prop("barrel", 12f, 0f));
            var shooter = world.SpawnVehicle("tank", 0, new Vector2(0f, -10f), 0f);
            var first = world.Props[0];
            world.Submit(new Command(CommandType.Attack, 0, new[] { shooter.Id }, target: first.Id));

            var explosions = 0;
            for (var i = 0; i < 200; i++)
            {
                world.Step(TestWorlds.Step);
                explosions += world.Events.Count(e => e.Kind == SimEventKind.Explosion);
                world.ClearEvents();
            }

            Assert.AreEqual(5, explosions);
            Assert.IsTrue(world.Props.All(p => !p.IsAlive));
            Assert.AreEqual(0, world.PendingExplosionCount);
        }

        [Test]
        public void DeathExplosionHappensOnceAfterItsDelay()
        {
            var world = TestWorlds.World();
            world.SpawnVehicle("tank", 0, Vector2.Zero, 0f);
            var boomer = world.SpawnVehicle("boomer", 1, new Vector2(0f, 10f), 0f);
            world.Submit(new Command(CommandType.Retreat, 1, new[] { boomer.Id }));

            var destroyed = 0;
            var explosions = 0;
            for (var i = 0; i < 60; i++)
            {
                world.Step(TestWorlds.Step);
                destroyed += world.Events.Count(e => e.Kind == SimEventKind.VehicleDestroyed && e.Entity == boomer.Id);
                explosions += world.Events.Count(e => e.Kind == SimEventKind.Explosion && e.Entity == boomer.Id);
                world.ClearEvents();
            }

            Assert.AreEqual(1, destroyed);
            Assert.AreEqual(1, explosions);
            Assert.IsFalse(world.TryGetVehicle(boomer.Id, out _), "dead vehicles leave the world");
        }

        [Test]
        public void DestroyedBuildingBecomesPassable()
        {
            var world = TestWorlds.World(TestWorlds.Prop("house", 0f, 0f));
            Assert.IsFalse(world.Grid.IsWalkable(Vector2.Zero));
            var shooter = world.SpawnVehicle("tank", 0, new Vector2(0f, -15f), 0f);
            world.Submit(new Command(CommandType.Attack, 0, new[] { shooter.Id }, target: world.Props[0].Id));

            TestWorlds.Run(world, 8f);

            Assert.IsFalse(world.Props[0].IsAlive);
            Assert.IsTrue(world.Grid.IsWalkable(Vector2.Zero));
        }
    }
}
