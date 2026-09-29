using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Navigation;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 12: one small scenario for each cause of stuck vehicles the stuck report found
    /// (Docs/stuck-report, DECISIONS 13B), each written to fail before its fix. The geometry is
    /// taken from the batch runs' traces where it could be (the titan against the fortress wall on
    /// Greenvale, the two siege tanks on Ashfield).
    /// </summary>
    public class StuckCauseTests
    {
        private const float Step = TestWorlds.Step;

        /// <summary>Base-wall pieces (8 m) end to end along y = <paramref name="line"/> from x0 to x1.</summary>
        private static void WallX(List<PropPlacement> props, float line, float x0, float x1)
        {
            for (var x = x0; x + 8f <= x1 + 1e-3f; x += 8f) props.Add(new PropPlacement("base_wall", new Vector2(x + 4f, line), 0));
        }

        /// <summary>Base-wall pieces along x = <paramref name="line"/> from y0 to y1.</summary>
        private static void WallY(List<PropPlacement> props, float line, float y0, float y1)
        {
            for (var y = y0; y + 8f <= y1 + 1e-3f; y += 8f) props.Add(new PropPlacement("base_wall", new Vector2(line, y + 4f), 90));
        }

        private static SimWorld World(float size, List<PropPlacement> props) =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("stuck", size,
                new[] { new TeamStart(0, new Vector2(-size * 0.4f, -size * 0.4f)), new TeamStart(1, new Vector2(size * 0.4f, size * 0.4f)) },
                props, new List<UnitPlacement>()));

        private static void Run(SimWorld world, float seconds, Func<bool> done = null)
        {
            for (var t = 0f; t < seconds && !(done?.Invoke() ?? false); t += Step)
            {
                world.Step(Step);
                world.ClearEvents();
            }
        }

        private static void Move(SimWorld world, Vehicle v, Vector2 to) => world.Submit(new Command(CommandType.Move, v.Team, new[] { v.Id }, to));

        /// <summary>
        /// Embedded: a tower flown into its hardpoint while a tank stood there left the tank on
        /// blocked ground, where every step it tried was refused; it never drove off (the rebuilt
        /// drone hangars and gun pits of Endless held 3 tanks each, 10-70 s, until they died).
        /// </summary>
        [Test]
        public void ATowerLandingOnATankPutsItOffItsGround()
        {
            var world = World(120f, new List<PropPlacement>());
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            Run(world, 0.5f);
            world.SpawnVehicle("gun_pit", 0, new Vector2(0.5f, 0.5f), 0f);
            Move(world, tank, new Vector2(30f, 0f));
            Run(world, 12f);
            Assert.IsTrue(world.Grid.IsWalkable(tank.Position), "the tank is off the gun pit's ground");
            Assert.Less(Vector2.Distance(tank.Position, new Vector2(30f, 0f)), 6f, $"and drove away (at {tank.Position})");
        }

        /// <summary>
        /// No path / goal out of reach: a goal whose nearest open ground is a pocket sealed by walls
        /// failed the route search, the vehicle stopped where it was, and the commander sent it
        /// again and again (up to 140 s in Swamp's fortress). Now the goal resolves to the nearest
        /// ground the vehicle can reach: it drives up to the wall.
        /// </summary>
        [Test]
        public void AGoalInASealedPocketTakesTheTankUpToIt()
        {
            var props = new List<PropPlacement>();
            // A sealed 16 x 16 m yard: walls all round.
            WallX(props, 8.6f, -8f, 8f);
            WallX(props, -8.6f, -8f, 8f);
            WallY(props, 8.6f, -8f, 8f);
            WallY(props, -8.6f, -8f, 8f);
            var world = World(120f, props);
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-35f, 0f), SimMath.DegToRad(90f));
            Assert.AreNotEqual(world.Grid.RegionOf(tank.Position), world.Grid.RegionOf(Vector2.Zero), "the yard is a pocket of its own");
            Move(world, tank, Vector2.Zero);
            Run(world, 15f);
            Assert.Less(Vector2.Distance(tank.Position, Vector2.Zero), 16f, $"it came up to the yard's wall (at {tank.Position})");
        }

        /// <summary>
        /// A group's slots behind a wall: slots were any open ground in rings round the point, so a
        /// group sent to one side of a wall got slots on the other side too, a long way round
        /// (through the sally port) or in a pocket. Now every slot is on the group's side.
        /// </summary>
        [Test]
        public void AGroupsSlotsStayOnItsSideOfAWall()
        {
            var props = new List<PropPlacement>();
            // A long wall along y = 0 with its only opening 40 m off.
            WallX(props, 0f, -56f, 32f);
            WallX(props, 0f, 42f, 58f);
            var world = World(140f, props);
            var group = new List<Vehicle>();
            for (var i = 0; i < 9; i++) group.Add(world.SpawnVehicle("heavy_tank", 0, new Vector2(-12f + i * 3f, -20f), 0f));
            world.Submit(new Command(CommandType.Move, 0, group.Select(v => v.Id).ToArray(), new Vector2(0f, -4f)));
            foreach (var v in group)
                Assert.Less(v.Order.Point.Y, 0f, $"#{v.Id.Value}'s slot {v.Order.Point} is on the group's side of the wall");
        }

        /// <summary>
        /// Head-on in the open: two siege tanks sent to each other's formation slots met nose to
        /// nose, and each queued behind the other ("no way round"), crawling for 20 s (Ashfield,
        /// seed 1). Now neither queues behind a hull coming the other way, the slots are handed out
        /// without crossing, and a head-on in the open sends the loser aside.
        /// </summary>
        [Test]
        public void TwoSiegeTanksSwappingPlacesGetPastEachOther()
        {
            // As the trace had them at 566 s: nose to nose, each sent to where the other stands.
            var world = World(140f, new List<PropPlacement>());
            var a = world.SpawnVehicle("siege_tank", 0, new Vector2(-21.2f, -31.0f), SimMath.DegToRad(74f));
            var b = world.SpawnVehicle("siege_tank", 0, new Vector2(-14.9f, -25.5f), SimMath.DegToRad(-149f));
            var goalA = new Vector2(-13.1f, -24.7f);
            var goalB = new Vector2(-20f, -30f);
            Move(world, a, goalA);
            Move(world, b, goalB);
            Run(world, 25f, () => Vector2.Distance(a.Position, goalA) < 5f && Vector2.Distance(b.Position, goalB) < 5f);
            Assert.Less(Vector2.Distance(a.Position, goalA), 6f, $"a got there (at {a.Position})");
            Assert.Less(Vector2.Distance(b.Position, goalB), 6f, $"b got there (at {b.Position})");
        }

        /// <summary>The slots of a group move never cross: two vehicles do not get each other's side.</summary>
        [Test]
        public void FormationSlotsAreHandedOutWithoutCrossing()
        {
            var world = World(140f, new List<PropPlacement>());
            // The hull nearest the centre chooses first and takes the slot nearest itself (a little
            // west), which sends the far west hull all the way east, across its path.
            var near = world.SpawnVehicle("siege_tank", 0, new Vector2(2f, 0f), 0f);
            var west = world.SpawnVehicle("siege_tank", 0, new Vector2(-10f, 0f), 0f);
            var result = new Dictionary<EntityId, Vector2>();
            Formation.Assign(new[] { near, west }, new List<Vector2> { new(-3f, 0f), new(8f, 0f) }, Vector2.Zero, result);
            Assert.AreEqual(new Vector2(-3f, 0f), result[west.Id], "the west hull takes the west slot");
            Assert.AreEqual(new Vector2(8f, 0f), result[near.Id], "and the other the east one: nobody crosses");
        }

        /// <summary>
        /// Steering round a parked friend into a wall: a titan tank pressed against the fortress
        /// wall held its detour heading (into the wall), so it could not advance, and would not
        /// slide along the wall because its nose was off its waypoint: it stood 19 s (Greenvale,
        /// seed 1). Now the detour never points the nose into a wall.
        /// </summary>
        [Test]
        public void SteeringRoundAParkedFriendNeverDrivesIntoTheWall()
        {
            var props = new List<PropPlacement>();
            WallX(props, 40f, 88f, 136f);
            var world = World(300f, props);
            var parked = world.SpawnVehicle("titan_tank", 0, new Vector2(115.5f, 36f), SimMath.DegToRad(91f));
            var titan = world.SpawnVehicle("titan_tank", 0, new Vector2(109.4f, 35.9f), SimMath.DegToRad(77f));
            Assert.IsTrue(world.Grid.IsWalkable(titan.Position));
            titan.SetOrder(new Order(OrderKind.Move, new Vector2(118f, 22f), EntityId.None));
            titan.SetPath(new List<Vector2> { new(111f, 35f), new(118f, 22f) }, new Vector2(118f, 22f));
            Run(world, 3f, () => titan.PathIndex > 0);
            Assert.Greater(titan.PathIndex, 0, $"it got past its first waypoint within 3 s (at {titan.Position}, heading {titan.Heading * Mathf.Rad2Deg:0})");
            Assert.IsTrue(parked.IsAlive);
        }

        /// <summary>
        /// A stale route: a route planned before a tower was raised across it led the tank into the
        /// tower's footprint, where it pushed until the stuck rules planned again. Now closed ground
        /// re-plans every route across it at once.
        /// </summary>
        [Test]
        public void ARouteAcrossGroundClosedSinceIsPlannedAgain()
        {
            var world = World(160f, new List<PropPlacement>());
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-40f, 0f), SimMath.DegToRad(90f));
            Move(world, tank, new Vector2(40f, 0f));
            Run(world, 1f);
            world.SpawnVehicle("heavy_turret", 1, new Vector2(0f, 0f), 0f);
            Run(world, 0.2f);
            var from = tank.Position;
            for (var i = tank.PathIndex; i < tank.Path.Count; i++)
            {
                Assert.IsTrue(world.Grid.LineOfSight(from, tank.Path[i]), $"leg {i} to {tank.Path[i]} goes round the turret");
                from = tank.Path[i];
            }
        }

        /// <summary>
        /// The safety net (C.3): a hull that has not got anywhere for ten seconds with somewhere to
        /// go is helped out, and every time it is, the log says so. Here the ground is closed under
        /// it directly (no defence to clear it), which nothing but the net can mend.
        /// </summary>
        [Test]
        public void TheSafetyNetFreesAHullStuckForTenSecondsAndLogsIt()
        {
            var world = World(120f, new List<PropPlacement>());
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            Run(world, 0.5f);
            world.Grid.AddBlocker(new Vector2(0f, 0f), 4f, 4f, SimWorld.ObstacleClearance);
            // (Its commander sends it again whenever the stuck rules give up on its route.)
            void Commander(float seconds)
            {
                for (var t = 0f; t < seconds; t += Step)
                {
                    if (tank.Order.Kind == OrderKind.Idle && Vector2.Distance(tank.Position, new Vector2(30f, 0f)) > 6f) Move(world, tank, new Vector2(30f, 0f));
                    world.Step(Step);
                    world.ClearEvents();
                }
            }
            Commander(9f);
            Assert.AreEqual(0, world.Movement.RescueLog.Count, "not before ten seconds");
            Commander(14f);
            Assert.GreaterOrEqual(world.Movement.RescueLog.Count, 1, "it stepped in");
            Assert.AreEqual("place", world.Movement.RescueLog[0].Kind, "off the blocked ground");
            Assert.Less(Vector2.Distance(tank.Position, new Vector2(30f, 0f)), 6f, $"and the tank drove on (at {tank.Position})");
        }

        /// <summary>The safety net stays out of battles where nothing is stuck.</summary>
        [Test]
        public void TheSafetyNetLeavesMovingTrafficAlone()
        {
            var world = World(160f, new List<PropPlacement>());
            var tanks = new List<Vehicle>();
            for (var i = 0; i < 8; i++) tanks.Add(world.SpawnVehicle("main_battle_tank", 0, new Vector2(-50f + (i % 4) * 6f, -10f + (i / 4) * 6f), SimMath.DegToRad(90f)));
            world.Submit(new Command(CommandType.Move, 0, tanks.Select(v => v.Id).ToArray(), new Vector2(50f, 0f)));
            Run(world, 40f);
            Assert.AreEqual(0, world.Movement.RescueLog.Count, "no rescue for a group that simply drove");
        }
    }
}
