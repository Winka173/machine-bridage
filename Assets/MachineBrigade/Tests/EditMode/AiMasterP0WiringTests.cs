using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// AI MASTER P0 wiring (lane A, DECISIONS "AI MASTER P0 wiring + preview wrecks (lane A)"): target access answered by
    /// P0-B's reachable firing region (a ground unit judges a ship from the shore), and a target behind breakable walls is
    /// "breach first", not dropped; a target no breach opens still is. Written by the lane, not run by it (the lead runs them).
    /// </summary>
    [Category("AIMasterP0Wiring")]
    public class AiMasterP0WiringTests
    {
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        [TearDown]
        public void TearDown() => GameContent.LoadTunables();

        private static SimWorld Field(List<PropPlacement> props = null, float size = 300f) =>
            new SimWorld(Catalog, new MapDefinition("field", size,
                new[] { new TeamStart(0, new Vector2(-size * 0.4f, -size * 0.4f)), new TeamStart(1, new Vector2(size * 0.4f, size * 0.4f)) },
                props ?? new List<PropPlacement>(), new List<UnitPlacement>()), seed: 5);

        private static Vehicle Dummy(SimWorld world, string id, int team, Vector2 at)
        {
            var v = world.SpawnVehicle(id, team, at, MathF.PI);
            world.MakeDummy(v);
            return v;
        }

        private static void Run(SimWorld world, float seconds)
        {
            for (var t = 0f; t < seconds; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
        }

        private static bool Logged(SimWorld world, string code) => world.AiLog.Entries.Any(e => e.Text.StartsWith(code, StringComparison.Ordinal));

        private static float Reach(string id) => Catalog.Vehicle(id).Weapon.Range;

        /// <summary>
        /// A square yard of destructible base walls (props, 8 m long) round <paramref name="centre"/>, its half side well past a
        /// main battle tank's reach, so nothing outside can shoot what stands in the middle.
        /// </summary>
        private static SimWorld Yard(Vector2 centre, out float half)
        {
            half = MathF.Ceiling((Reach("main_battle_tank") + 12f) / 8f) * 8f;
            var walls = new List<PropPlacement>();
            for (var d = -half; d <= half + 0.1f; d += 8f)
            {
                walls.Add(new PropPlacement("base_wall", centre + new Vector2(d, -half), 0));
                walls.Add(new PropPlacement("base_wall", centre + new Vector2(d, half), 0));
                walls.Add(new PropPlacement("base_wall", centre + new Vector2(-half, d), 90));
                walls.Add(new PropPlacement("base_wall", centre + new Vector2(half, d), 90));
            }
            var size = 2f * (MathF.Abs(centre.X) + half + 40f);
            return Field(walls, MathF.Max(300f, size));
        }

        // ------------------------------------------------------------------------------------------------ 1: P0-B wired in

        [Test]
        public void W1_TheAccessTestIsAnsweredByTheReachableFiringRegion()
        {
            var world = Field();
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-40f, -40f), 0f);
            Assert.True(world.TargetAccess.CanInfluence(tank, new Vector2(40f, 40f), false));
            Assert.GreaterOrEqual(world.TargetAccess.Resolved, 1, "P0-B's firing region answers while the topology matches the grid");
        }

        [Test]
        public void W1_ANewBlockerIsSeenAtOnceWhileTheTopologyLags()
        {
            var world = Field();
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-40f, -40f), 0f);
            var at = new Vector2(40f, 40f);
            Assert.True(world.TargetAccess.CanInfluence(tank, at, false));
            var resolved = world.TargetAccess.Resolved;
            world.Grid.AddBlocker(at, 120f, 120f, 0f);
            Assert.False(world.TargetAccess.CanInfluence(tank, at, false), "the grid's own regions answer until the topology is rebuilt");
            Assert.AreEqual(resolved, world.TargetAccess.Resolved, "a stale topology is not asked");
        }

        [Test]
        public void W1_AShoreTankJudgesAShipFromTheShore()
        {
            // A straight coast at x = 0, the sea to the east (as AiMasterP0BTests.Coast).
            const float half = 200f;
            var reach = Reach("main_battle_tank");
            var lanes = new List<SeaLaneDef> { new() { Id = "far", W = reach + 40f, Patrol = 120f, End = half - 4f } };
            var sea = SeaDef.Straight(new Vector2(0f, 1f), 0f, -half, half, lanes, new List<SeaLandingDef>(), Array.Empty<Vector2>(),
                new Vector2(half - 6f, 0f));
            var map = new MapDefinition("wire_coast", half * 2f,
                new[] { new TeamStart(0, new Vector2(-150f, 0f)), new TeamStart(1, new Vector2(reach + 40f, 0f)) },
                Array.Empty<PropPlacement>(), Array.Empty<UnitPlacement>()) { Sea = sea };
            var world = new SimWorld(Catalog, map, 7);
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-150f, 0f), 0f);
            Assert.True(world.TargetAccess.CanInfluence(tank, new Vector2(reach * 0.5f, 0f), false, 4f),
                "a ship close inshore is in reach of the beach");
            Assert.False(world.TargetAccess.CanInfluence(tank, new Vector2(reach + 40f, 0f), false, 4f),
                "a ship out on the far lane: no ground the tank can drive to reaches it (the sea is not its ground)");
            Assert.GreaterOrEqual(world.TargetAccess.Resolved, 1);
        }

        // ------------------------------------------------------------------------------------------------ 2: breach first

        [Test]
        public void W2_ATargetBehindBreakableWallsResolvesToTheWallFirst()
        {
            var centre = new Vector2(40f, 40f);
            var world = Yard(centre, out var half);
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-60f, -60f), 0f);
            var target = Dummy(world, "light_tank", 1, centre);
            Assert.False(world.TargetAccess.CanInfluence(tank, target.Position, false, target.Radius), "sealed in by the wall ring");
            var blocker = world.TargetAccess.BreachFirst(tank, target);
            Assert.NotNull(blocker, "a breakable wall makes it breach-first, not unreachable");
            Assert.IsInstanceOf<Prop>(blocker);
            Assert.That(blocker.Position.X < centre.X - half + 6f || blocker.Position.Y < centre.Y - half + 6f,
                "the wall on the tank's side: " + blocker.Position);
        }

        [Test]
        public void W2_TheAiOrderGoesOntoTheWallInsteadOfBeingDropped()
        {
            var centre = new Vector2(40f, 40f);
            var world = Yard(centre, out _);
            world.RevealAll = true;
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-60f, -60f), 0f);
            var target = Dummy(world, "light_tank", 1, centre);
            Run(world, 0.1f);
            world.Submit(new Command(CommandType.Attack, 0, new[] { tank.Id }, target.Position, target.Id));
            Run(world, 0.5f);
            Assert.AreEqual(OrderKind.Attack, tank.Order.Kind, "not dropped to Idle");
            Assert.AreNotEqual(target.Id, tank.Order.Target, "the wall first");
            Assert.That(world.TryGetTarget(tank.Order.Target, out var wall) && wall is Prop, "the order's target is a wall segment");
            Assert.GreaterOrEqual(world.CombatWatch.Breaches, 1);
            Assert.AreEqual(0, world.CombatWatch.Dropped);
            Assert.That(Logged(world, CombatReasons.TargetBreachFirst));
        }

        [Test]
        public void W2_ATargetNoBreachOpensIsStillDropped()
        {
            var world = Field();
            world.RevealAll = true;
            // Unbreakable ground round the target (the same box as AiMasterP0ATests' sealed pocket).
            var box = new Vector2(60f, 60f);
            world.Grid.AddBlocker(box, 90f, 90f, 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-40f, -40f), 0f);
            var target = Dummy(world, "light_tank", 1, box);
            Assert.IsNull(world.TargetAccess.BreachFirst(tank, target), "nothing to break: truly unreachable");
            Run(world, 0.1f);
            world.Submit(new Command(CommandType.Attack, 0, new[] { tank.Id }, target.Position, target.Id));
            Run(world, 0.5f);
            Assert.AreNotEqual(OrderKind.Attack, tank.Order.Kind);
            Assert.GreaterOrEqual(world.CombatWatch.Dropped, 1);
            Assert.AreEqual(0, world.CombatWatch.Breaches);
        }

        [Test]
        public void W2_ThePlayersOrderIsLeftAlone()
        {
            var centre = new Vector2(40f, 40f);
            var world = Yard(centre, out _);
            world.RevealAll = true;
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-60f, -60f), 0f);
            var target = Dummy(world, "light_tank", 1, centre);
            Run(world, 0.1f);
            tank.ManualOrder = true;
            tank.SetOrder(new Order(OrderKind.Attack, target.Position, target.Id));
            Run(world, 0.5f);
            Assert.AreEqual(target.Id, tank.Order.Target, "the player's order stays on the target they chose");
            Assert.AreEqual(0, world.CombatWatch.Breaches);
        }

        [Test]
        public void W2_TheBreachAnswerIsTheSameEveryTime()
        {
            EntityId First()
            {
                var centre = new Vector2(40f, 40f);
                var world = Yard(centre, out _);
                var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-60f, -60f), 0f);
                var target = Dummy(world, "light_tank", 1, centre);
                return world.TargetAccess.BreachFirst(tank, target)?.Id ?? EntityId.None;
            }
            var a = First();
            Assert.That(a.IsValid);
            Assert.AreEqual(a, First(), "deterministic: the same wall on a fresh world");
        }
    }
}
