using System.Linq;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Tests
{
    /// <summary>Multiple weapon mounts, salvos, guided missiles and aircraft.</summary>
    public class WeaponTests
    {
        [Test]
        public void RoofGunEngagesItsOwnTargetWhileTheMainGunFightsAnother()
        {
            var world = TestWorlds.World();
            var gunner = world.SpawnVehicle("gunner", 0, Vector2.Zero, 0f);
            var tank = world.SpawnVehicle("decoy", 1, new Vector2(15f, 0f), 0f);
            var light = world.SpawnVehicle("arty", 1, new Vector2(-12f, 3f), 0f);
            TestWorlds.Run(world, TestWorlds.Step);
            world.Submit(new Command(CommandType.Attack, 0, new[] { gunner.Id }, default, tank.Id));

            var mounts = new int[2];
            for (var i = 0; i < 60; i++)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.WeaponFired && e.Entity == gunner.Id) mounts[e.Mount]++;
                world.ClearEvents();
            }

            Assert.Greater(mounts[0], 0, "the main gun fires at the ordered target");
            Assert.Greater(mounts[1], 3, "the roof gun fires on its own");
            Assert.Less(light.Hp, light.MaxHp, "the roof gun hits the light vehicle behind");
        }

        [Test]
        public void SalvoFiresEveryRocketThenWaitsForTheCooldown()
        {
            var world = TestWorlds.World();
            var launcher = world.SpawnVehicle("launcher", 0, Vector2.Zero, 0f);
            world.SpawnVehicle("decoy", 1, new Vector2(30f, 0f), 0f);

            var shots = 0;
            for (var i = 0; i < (int)(4f / TestWorlds.Step); i++)
            {
                world.Step(TestWorlds.Step);
                shots += world.Events.Count(e => e.Kind == SimEventKind.WeaponFired && e.Entity == launcher.Id);
                world.ClearEvents();
            }

            Assert.AreEqual(TestWorlds.Salvo.Burst, shots);
            Assert.Greater(launcher.Cooldown, 5f);
        }

        [Test]
        public void GuidedMissileHitsATargetThatDrivesAway()
        {
            var world = TestWorlds.World();
            world.SpawnVehicle("hunter", 0, Vector2.Zero, 0f);
            var target = world.SpawnVehicle("dummy", 1, new Vector2(25f, 0f), 0f);
            TestWorlds.Run(world, 0.2f); // launched; 1.2 s of flight at 20 m/s
            world.Submit(new Command(CommandType.Move, 1, new[] { target.Id }, new Vector2(25f, 30f)));

            TestWorlds.Run(world, 2f);

            Assert.Less(target.Hp, target.MaxHp);
        }

        [Test]
        public void GroundGunsCannotHitAircraftButAntiAirCan()
        {
            var world = TestWorlds.World();
            var heli = world.SpawnVehicle("heli", 1, new Vector2(10f, 0f), 0f);
            var tank = world.SpawnVehicle("tank", 0, Vector2.Zero, 0f);

            TestWorlds.Run(world, 3f);
            Assert.AreEqual(heli.MaxHp, heli.Hp, "a tank gun cannot engage an aircraft");
            Assert.IsFalse(tank.Target.IsValid);

            var aa = world.SpawnVehicle("aa", 0, new Vector2(0f, -4f), 0f);
            TestWorlds.Run(world, 1f);
            Assert.Less(heli.Hp, heli.MaxHp, "flak reaches it");
            Assert.AreEqual(heli.Id, aa.Target);
        }

        [Test]
        public void AttackOrdersOnAircraftGoOnlyToVehiclesThatCanHitThem()
        {
            var world = TestWorlds.World();
            var heli = world.SpawnVehicle("heli", 1, new Vector2(12f, 0f), 0f);
            var tank = world.SpawnVehicle("tank", 0, Vector2.Zero, 0f);
            var aa = world.SpawnVehicle("aa", 0, new Vector2(0f, 4f), 0f);
            TestWorlds.Run(world, TestWorlds.Step);

            Assert.IsTrue(world.Submit(new Command(CommandType.Attack, 0, new[] { tank.Id, aa.Id }, default, heli.Id)).Accepted);
            Assert.AreEqual(OrderKind.Idle, tank.Order.Kind, "a tank gun cannot chase an aircraft");
            Assert.AreEqual(OrderKind.Attack, aa.Order.Kind);
            Assert.IsFalse(world.Submit(new Command(CommandType.Attack, 0, new[] { tank.Id }, default, heli.Id)).Accepted);
        }

        [Test]
        public void AircraftFlyStraightOverBuildings()
        {
            var world = TestWorlds.World(TestWorlds.Prop("house", 0f, 0f));
            var heli = world.SpawnVehicle("heli", 0, new Vector2(-20f, 0f), 0f);
            var tank = world.SpawnVehicle("tank", 0, new Vector2(-20f, 6f), 0f);

            world.Submit(new Command(CommandType.Move, 0, new[] { heli.Id }, new Vector2(20f, 0f)));
            TestWorlds.Run(world, 5f);

            Assert.Less(Vector2.Distance(heli.Position, new Vector2(20f, 0f)), 2f);
            Assert.AreEqual(OrderKind.Idle, heli.Order.Kind);
            Assert.Less(Vector2.Distance(tank.Position, new Vector2(-20f, 6f)), 1f, "aircraft do not shove ground vehicles");
        }

        [Test]
        public void GroundBlastsSpareAircraft()
        {
            var world = TestWorlds.World(TestWorlds.Prop("barrel", 0f, 0f));
            var heli = world.SpawnVehicle("heli", 1, new Vector2(1.5f, 0f), 0f);
            var tank = world.SpawnVehicle("tank", 0, new Vector2(-10f, 0f), 0f);
            var barrel = world.Props[0];
            TestWorlds.Run(world, TestWorlds.Step);
            world.Submit(new Command(CommandType.Attack, 0, new[] { tank.Id }, default, barrel.Id));

            TestWorlds.Run(world, 2f);

            Assert.IsFalse(barrel.IsAlive);
            Assert.AreEqual(heli.MaxHp, heli.Hp);
        }
    }
}
