using System.Collections.Generic;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Aircraft fight the way their real counterparts do: the AC-130 circles its target with its
    /// guns out of the left side, the B-2 is seen only close up until it opens its bay, the fighter
    /// hunts enemy aircraft far from its post and can stop in the air to shoot.
    /// </summary>
    public class AirRealismTests
    {
        private static SimWorld Field()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 240f,
                new[] { new TeamStart(0, new Vector2(-100f, -100f)), new TeamStart(1, new Vector2(100f, 100f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));
            world.EnableEconomy(new TeamEconomy(0));
            world.EnableEconomy(new TeamEconomy(1));
            return world;
        }

        private static void Run(SimWorld world, float seconds)
        {
            for (var t = 0f; t < seconds; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
        }

        [Test]
        public void TheGunshipCirclesItsTargetWithItOnTheLeftAndHitsIt()
        {
            var world = Field();
            var gunship = world.SpawnVehicle("sky_gunship", 0, new Vector2(-40f, 0f), 0f);
            var tank = world.SpawnVehicle("heavy_tank", 1, new Vector2(0f, 0f), 0f);
            var full = tank.Hp;
            Run(world, 12f);
            var onLeft = 0;
            var samples = 0;
            for (var i = 0; i < 40; i++)
            {
                Run(world, 0.5f);
                if (!tank.IsAlive) break;
                var forward = Sim.Core.SimMath.Forward(gunship.Heading);
                var to = tank.Position - gunship.Position;
                // Headings turn clockwise, so the left of the nose is where the cross product is positive.
                if (forward.X * to.Y - forward.Y * to.X > 0f) onLeft++;
                samples++;
            }
            Assert.Less(tank.Hp, full, "its side guns hit the target");
            Assert.Greater(onLeft, samples * 0.7f, $"the target stays on its left ({onLeft}/{samples})");
            Assert.Less(Vector2.Distance(gunship.Position, tank.Position), 70f, "it circles, not flies away");
        }

        [Test]
        public void TheStealthBomberIsSeenOnlyCloseUpUntilItFires()
        {
            var world = Field();
            var aa = world.SpawnVehicle("aa_vehicle", 1, new Vector2(0f, 0f), 0f);
            var bomber = world.SpawnVehicle("stealth_bomber", 0, new Vector2(30f, 0f), 0f);
            Run(world, 0.2f);
            Assert.Less(30f, aa.Def.VisionRange, "the anti-air vehicle would see an ordinary aircraft there");
            Assert.IsFalse(bomber.IsVisibleTo(1), "a stealthy aircraft 30 m off is not seen");
            var plain = world.SpawnVehicle("heavy_bomber", 0, new Vector2(-30f, 0f), 0f);
            Run(world, 0.2f);
            Assert.IsTrue(plain.IsVisibleTo(1), "an ordinary bomber is");
        }

        [Test]
        public void TheFighterGoesAfterEnemyAircraftFarFromItsPost()
        {
            var world = Field();
            var fighter = world.SpawnVehicle("fighter_jet", 0, new Vector2(0f, 0f), 0f);
            var heli = world.SpawnVehicle("attack_helicopter", 1, new Vector2(95f, 0f), 0f);
            // Something of ours sees the helicopter; the fighter itself starts out of its sight.
            world.SpawnVehicle("recon_drone", 0, new Vector2(80f, 10f), 0f);
            var start = heli.Hp;
            Run(world, 25f);
            Assert.Less(heli.Hp, start, "the fighter intercepts it");
        }

        [Test]
        public void TheFighterStopsInTheAirToShoot()
        {
            var world = Field();
            var fighter = world.SpawnVehicle("fighter_jet", 0, new Vector2(-50f, 0f), 1.57f);
            world.SpawnVehicle("attack_helicopter", 1, new Vector2(0f, 0f), 0f);
            var slowest = float.MaxValue;
            for (var i = 0; i < 60; i++)
            {
                Run(world, 0.25f);
                slowest = System.Math.Min(slowest, fighter.Speed);
            }
            Assert.Less(slowest, fighter.Def.Speed * 0.2f, "it hovers for a while to shoot");
        }
    }
}
