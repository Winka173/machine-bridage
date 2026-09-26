using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Tests
{
    /// <summary>Aeroplanes cannot hover: they circle, fly strafing runs and stay over the battlefield.</summary>
    public class AircraftTests
    {
        [Test]
        public void AeroplanesNeverStopAndCircleTheirPost()
        {
            var world = TestWorlds.World();
            var jet = world.SpawnVehicle("jet", 0, Vector2.Zero, 0f);
            for (var i = 0; i < (int)(30f / TestWorlds.Step); i++)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                if (world.Time < 3.0) continue;
                Assert.Greater(jet.Speed, jet.Def.Speed * 0.8f, "an aeroplane never slows to a hover");
                Assert.IsTrue(world.Map.Contains(jet.Position), "it stays over the map");
                Assert.Less(jet.Position.Length(), 40f, "it circles its post rather than flying off");
            }
        }

        [Test]
        public void AeroplanesAttackInRepeatedRuns()
        {
            var world = TestWorlds.World();
            var jet = world.SpawnVehicle("jet", 0, new Vector2(-30f, 0f), 0f);
            world.SpawnVehicle("decoy", 1, new Vector2(10f, 0f), 0f);
            var runs = 0;
            var lastShot = -10.0;
            var closePasses = 0;
            var wasClose = false;
            for (var i = 0; i < (int)(60f / TestWorlds.Step); i++)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                {
                    if (e.Kind != SimEventKind.WeaponFired || e.Entity != jet.Id) continue;
                    // A pause of over two seconds between shots separates one run from the next.
                    if (world.Time - lastShot > 2.0) runs++;
                    lastShot = world.Time;
                }
                world.ClearEvents();
                var close = Vector2.Distance(jet.Position, new Vector2(10f, 0f)) < 12f;
                if (close && !wasClose) closePasses++;
                wasClose = close;
            }
            Assert.GreaterOrEqual(runs, 3, "it keeps coming round for more runs");
            Assert.GreaterOrEqual(closePasses, 3, "each run passes over the target");
        }

        [Test]
        public void AeroplanesFollowMoveOrdersPastEnemies()
        {
            var world = TestWorlds.World();
            var jet = world.SpawnVehicle("jet", 0, new Vector2(0f, 0f), 0f);
            world.SpawnVehicle("decoy", 1, new Vector2(12f, 0f), 0f);
            for (var i = 0; i < (int)(3f / TestWorlds.Step); i++)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
            // Mid-fight, sent away: it must break off rather than keep strafing the enemy.
            world.Submit(new Command(CommandType.Move, 0, new[] { jet.Id }, new Vector2(-35f, -35f)));
            var reached = false;
            for (var i = 0; i < (int)(12f / TestWorlds.Step) && !reached; i++)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                reached = Vector2.Distance(jet.Position, new Vector2(-35f, -35f)) < 20f;
            }
            Assert.IsTrue(reached, "a move order takes it away from the fight");
        }

        [Test]
        public void AeroplanesFlyToOrderedPoints()
        {
            var world = TestWorlds.World();
            var jet = world.SpawnVehicle("jet", 0, new Vector2(-30f, -30f), 0f);
            world.Submit(new Command(CommandType.Move, 0, new[] { jet.Id }, new Vector2(30f, 25f)));
            var reached = false;
            for (var i = 0; i < (int)(15f / TestWorlds.Step) && !reached; i++)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                reached = Vector2.Distance(jet.Position, new Vector2(30f, 25f)) < 20f;
            }
            Assert.IsTrue(reached, "it gets there");
        }
    }
}
