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
using MachineBrigade.Sim.Modes;
using MachineBrigade.Sim.Navigation;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The traffic rules (lane map, making way, taking turns through doorways, routing round parked
    /// hulls) in small deterministic scenarios with the real vehicles, and the siege fortress's
    /// gates.
    /// </summary>
    public class TrafficTests
    {
        private const float Step = TestWorlds.Step;

        private static readonly string[] SiegeMaps =
        {
            "ashfield", "dunebreak", "frostpeak", "ironport", "redrock", "whiteout", "greenvale", "rustyard", "emberridge",
            "junglepass", "skyhold", "metrocity",
            "landingbeach", "hydrodam", "capital", "launchsite", "saltflat", "borderbridge", "swamp", "coralisles",
        };

        /// <summary>Base-wall segments (8 m) end to end along x = line (axis 'y') or y = line (axis 'x'), with an optional opening.</summary>
        private static void Wall(List<PropPlacement> props, char axis, float line, float from, float to, float gate = float.NaN, float width = 0f)
        {
            var centres = new List<float>();
            if (float.IsNaN(gate))
            {
                for (var u = from; u + 8f <= to + 1e-3f; u += 8f) centres.Add(u + 4f);
            }
            else
            {
                for (var u = gate - width / 2; u - 8f >= from - 1e-3f; u -= 8f) centres.Add(u - 4f);
                for (var u = gate + width / 2; u + 8f <= to + 1e-3f; u += 8f) centres.Add(u + 4f);
            }
            foreach (var c in centres)
                props.Add(axis == 'x' ? new PropPlacement("base_wall", new Vector2(c, line), 0) : new PropPlacement("base_wall", new Vector2(line, c), 90));
        }

        private static SimWorld World(float size, List<PropPlacement> props, Vector2 rally0, Vector2 rally1, List<RoadDef> roads = null) =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("traffic", size,
                new[] { new TeamStart(0, rally0), new TeamStart(1, rally1) }, props, new List<UnitPlacement>(), roads: roads));

        private static void Order(SimWorld world, CommandType type, Vehicle v, Vector2 point, Sim.Core.EntityId target = default) =>
            world.Submit(new Command(type, v.Team, new[] { v.Id }, point, target));

        private static void Run(SimWorld world, float seconds)
        {
            for (var t = 0f; t < seconds; t += Step)
            {
                world.Step(Step);
                world.ClearEvents();
            }
        }

        /// <summary>
        /// A road through a walled corridor two cells wide, with a bay 16 m wide on its south side at
        /// the middle, and a target dummy 60 m past the bay (always in sight).
        /// </summary>
        private static SimWorld Corridor(out Vehicle target)
        {
            var props = new List<PropPlacement>();
            Wall(props, 'x', 4.1f, -28f, 28f);
            Wall(props, 'x', -4.1f, -28f, 28f, 0f, 16f);
            Wall(props, 'y', -8.6f, -14.1f, -4.0f);
            Wall(props, 'y', 8.6f, -14.1f, -4.0f);
            Wall(props, 'x', -14.7f, -8f, 8f);
            var roads = new List<RoadDef> { new RoadDef(6f, new[] { new Vector2(-78f, 0f), new Vector2(78f, 0f) }) };
            var world = World(160f, props, new Vector2(-70f, 0f), new Vector2(70f, 0f), roads);
            target = world.SpawnVehicle("main_battle_tank", 1, new Vector2(60f, 0f), -Mathf.PI / 2);
            world.MakeDummy(target);
            world.Step(Step);
            return world;
        }

        private static List<Vehicle> Column(SimWorld world, int count)
        {
            var tanks = new List<Vehicle>();
            for (var i = 0; i < count; i++) tanks.Add(world.SpawnVehicle("main_battle_tank", 0, new Vector2(-24f - i * 8f, 0f), Mathf.PI / 2));
            foreach (var v in tanks) Order(world, CommandType.Move, v, new Vector2(45f, 0f));
            return tanks;
        }

        private static float PassTime(SimWorld world, List<Vehicle> tanks, float limit, float past)
        {
            var t = 0f;
            for (; t < limit + 5f; t += Step)
            {
                world.Step(Step);
                world.ClearEvents();
                if (tanks.All(v => v.Position.X > past)) break;
            }
            return t;
        }

        [Test]
        public void LaneMapMarksDoorwaysRoadsAndRoutes()
        {
            var props = new List<PropPlacement>();
            Wall(props, 'y', 0f, -48f, 48f, 1f, 10f);
            var roads = new List<RoadDef> { new RoadDef(6f, new[] { new Vector2(-45f, -30f), new Vector2(45f, -30f) }) };
            var world = World(100f, props, new Vector2(-40f, 1f), new Vector2(40f, 1f), roads);
            var lanes = world.Lanes;
            var gate = new Vector2(0.5f, 1f);
            Assert.AreNotEqual(LaneFlags.None, lanes.At(gate) & LaneFlags.Narrow, "a gate is a doorway");
            Assert.IsTrue(lanes.NoParkAt(gate) && lanes.NoParkAt(new Vector2(5f, 1f)), "nobody stops in it or its mouth");
            Assert.Greater(lanes.DoorwayAt(gate), 0);
            Assert.IsFalse(lanes.NoParkAt(new Vector2(-20f, 20f)), "open ground is free to stop on");
            Assert.AreNotEqual(LaneFlags.None, lanes.At(new Vector2(-20f, -30f)) & LaneFlags.Road);
            Assert.AreNotEqual(LaneFlags.None, lanes.At(new Vector2(-20f, 1f)) & LaneFlags.Route, "the way between the camps is a main route");
            var slots = Formation.Slots(gate, 6, 5f, world.Grid, lanes);
            Assert.IsTrue(slots.All(s => !lanes.NoParkAt(s)), "a group sent into the gate stops beside it");
        }

        [Test]
        public void AnIdleVehicleDoesNotStandInAGate()
        {
            var props = new List<PropPlacement>();
            Wall(props, 'y', 0f, -48f, 48f, 1f, 10f);
            var world = World(100f, props, new Vector2(-40f, -40f), new Vector2(40f, 40f));
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0.5f, 1f), 0f);
            Run(world, 6f);
            Assert.IsFalse(world.Lanes.NoParkAt(tank.Position), "it drove out of the gate and its mouth");
            Assert.IsFalse(world.Lanes.NoParkAt(tank.GuardPoint), "and made that its post");
        }

        /// <summary>
        /// Research scenario 1: a rocket launcher shelling a target 60 m ahead from the middle of a
        /// road; five tanks come along the road. It steps off the road (a short drive, still in
        /// range) instead of plugging it.
        /// </summary>
        [Test]
        public void ArtilleryParkedOnTheRoadMakesWayForAColumn()
        {
            var world = Corridor(out var target);
            var mlrs = world.SpawnVehicle("mlrs", 0, Vector2.Zero, Mathf.PI / 2);
            var start = mlrs.Position;
            Order(world, CommandType.Attack, mlrs, target.Position, target.Id);
            Run(world, 1f);
            Assert.AreEqual(OrderKind.Attack, mlrs.Order.Kind);
            var tanks = Column(world, 5);
            var t = PassTime(world, tanks, 15f, 12f);
            Debug.Log($"Road jam: column past after {t:0.0} s; launcher moved {Vector2.Distance(mlrs.Position, start):0.0} m, " +
                      $"lanes {world.Lanes.At(mlrs.Position)}, yields {mlrs.Traffic.Yields}");
            Assert.Less(t, 15f, "all five tanks get past within 15 s");
            Assert.LessOrEqual(Vector2.Distance(mlrs.Position, start), 10f, "the launcher moves at most 10 m");
            Assert.LessOrEqual(Vector2.Distance(mlrs.Position, target.Position) - target.Radius, mlrs.Def.Weapon.Range, "and keeps its target in range");
            Assert.AreEqual(LaneFlags.None, world.Lanes.At(mlrs.Position) & (LaneFlags.Route | LaneFlags.NoPark), "off the route");
        }

        /// <summary>An idle vehicle in a one-lane corridor is asked to make way, steps into the bay beside it, and the column passes.</summary>
        [Test]
        public void AParkedFriendStepsAsideWhenAsked()
        {
            var world = Corridor(out _);
            var parked = world.SpawnVehicle("mlrs", 0, Vector2.Zero, Mathf.PI / 2);
            var start = parked.Position;
            Run(world, 1f);
            var tanks = Column(world, 5);
            var t = PassTime(world, tanks, 20f, 12f);
            Debug.Log($"Corridor: column past after {t:0.0} s; the parked launcher yielded {parked.Traffic.Yields} times, moved {Vector2.Distance(parked.Position, start):0.0} m");
            Assert.Less(t, 20f, "the column gets past");
            Assert.GreaterOrEqual(parked.Traffic.Yields, 1, "because it was asked and made way");
            Assert.LessOrEqual(Vector2.Distance(parked.Position, start), 12f, "a short step aside");
            Assert.IsFalse(world.Lanes.NoParkAt(parked.Position));
        }

        /// <summary>
        /// Research scenario 2: a tank idle in a 10 m gate, three tanks either side ordered through.
        /// Everyone gets through, taking turns, without anyone being shoved aside over and over.
        /// </summary>
        [Test]
        public void TanksTakeTurnsThroughAPluggedGate()
        {
            var props = new List<PropPlacement>();
            Wall(props, 'y', 0f, -48f, 48f, 1f, 10f);
            var world = World(100f, props, new Vector2(-40f, 1f), new Vector2(40f, 1f));
            world.SpawnVehicle("main_battle_tank", 0, new Vector2(0.2f, 1f), 0.3f);
            var west = new List<Vehicle>();
            var east = new List<Vehicle>();
            for (var i = 0; i < 3; i++)
            {
                west.Add(world.SpawnVehicle("main_battle_tank", 0, new Vector2(-20f - i * 8f, 1f + (i - 1) * 5f), Mathf.PI / 2));
                east.Add(world.SpawnVehicle("main_battle_tank", 0, new Vector2(20f + i * 8f, 1f + (i - 1) * 5f), -Mathf.PI / 2));
            }
            Run(world, 0.5f);
            for (var i = 0; i < 3; i++)
            {
                Order(world, CommandType.Move, west[i], new Vector2(30f, 1f + (i - 1) * 6f));
                Order(world, CommandType.Move, east[i], new Vector2(-30f, 1f + (i - 1) * 6f));
            }
            var t = 0f;
            for (; t < 30f; t += Step)
            {
                world.Step(Step);
                world.ClearEvents();
                if (west.All(v => v.Position.X > 8f) && east.All(v => v.Position.X < -8f)) break;
            }
            var most = world.VehicleList.Max(v => v.Traffic.Yields);
            Debug.Log($"Gate plug: all through after {t:0.0} s; most yields by one vehicle {most}");
            Assert.Less(t, 25f, "all six get through within 25 s");
            Assert.LessOrEqual(most, 4, "no vehicle makes way more than four times");
        }

        /// <summary>Research scenario 3: two tanks meet head-on in a gate two cells wide (the old 7 m gate); both are through within 12 s.</summary>
        [Test]
        public void HeadOnInANarrowGateIsSettled()
        {
            var props = new List<PropPlacement>();
            Wall(props, 'y', 0f, -48f, 48f, 0f, 7f);
            var world = World(100f, props, new Vector2(-40f, -40f), new Vector2(40f, 40f));
            Assert.IsFalse(world.Grid.IsWalkable(new Vector2(0.5f, -3f)) || world.Grid.IsWalkable(new Vector2(0.5f, 3f)), "a two-cell gate");
            var a = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-14f, 0f), Mathf.PI / 2);
            var b = world.SpawnVehicle("main_battle_tank", 0, new Vector2(14f, 0f), -Mathf.PI / 2);
            Order(world, CommandType.Move, a, new Vector2(25f, 0f));
            Order(world, CommandType.Move, b, new Vector2(-25f, 0f));
            var t = 0f;
            for (; t < 20f; t += Step)
            {
                world.Step(Step);
                world.ClearEvents();
                if (a.Position.X > 8f && b.Position.X < -8f) break;
            }
            Debug.Log($"Head-on: both through after {t:0.0} s");
            Assert.Less(t, 12f, "both through within 12 s");
        }

        /// <summary>A vehicle stuck behind a hull it cannot get past plans a route round parked hulls, within the search budget.</summary>
        [Test]
        public void AStuckVehicleRoutesRoundParkedHulls()
        {
            // Two gates in a wall; a heavy tank parked (stunned, so it cannot make way) in the near one.
            var props = new List<PropPlacement>();
            Wall(props, 'y', 0f, -48f, 48f);
            props.RemoveAll(p => MathF.Abs(p.Position.Y - 4f) < 1f || MathF.Abs(p.Position.Y + 20f) < 1f);
            var world = World(100f, props, new Vector2(-40f, -40f), new Vector2(40f, 40f));
            var plug = world.SpawnVehicle("heavy_tank", 0, new Vector2(0f, 4f), Mathf.PI / 2);
            plug.StunnedUntil = 1e9;
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-12f, 4f), Mathf.PI / 2);
            Order(world, CommandType.Move, tank, new Vector2(15f, 4f));
            var t = 0f;
            for (; t < 40f && tank.Position.X < 8f; t += Step)
            {
                world.Step(Step);
                world.ClearEvents();
            }
            Debug.Log($"Stuck: through the other gate after {t:0.0} s at ({tank.Position.X:0.0},{tank.Position.Y:0.0}); most nodes in a step {world.Movement.PathNodesMaxTick}");
            Assert.Greater(tank.Position.X, 8f, "it found the way round through the other gate");
            Assert.LessOrEqual(world.Movement.PathNodesMaxTick, Sim.Movement.MovementSystem.PathNodeBudgetPerTick);
        }

        /// <summary>
        /// Research scenario 5: every siege gateway leaves at least three walkable 2 m cells across
        /// (with the fixed defences on their ground): the sally ports as they are, the gates once
        /// their doors are blown in.
        /// </summary>
        [TestCaseSource(nameof(SiegeMaps))]
        public void EverySiegeGateLeavesThreeCells(string map)
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(map + "_siege"), 1);
            new SiegeMode(new SiegeRules()).Setup(world);
            foreach (var doors in world.Props.Where(p => p.IsAlive && p.Def.Id == "fortress_gate").ToList()) world.DebugDestroyProp(doors);
            var gates = world.Props.Where(p => p.Def.Id == "base_gate").ToList();
            // The open gateways (the two sally ports and the keep's west gate) are double since prompt 12: two frames each.
            if (!ContentTests.ClassicSiege.Contains(map))
                Assert.AreEqual(9, gates.Count, "the walls' two gates and two double sally ports, the keep's gate and its double open gate");
            else Assert.Greater(gates.Count, 0, "the classic fortress's gates");
            foreach (var gate in gates)
            {
                var along = gate.Rotation == 90 ? new Vector2(0f, 1f) : new Vector2(1f, 0f);
                int best = 0, run = 0;
                for (var s = -8f; s <= 8f; s += world.Grid.CellSize)
                {
                    run = world.Grid.IsWalkable(gate.Position + along * s) ? run + 1 : 0;
                    best = Math.Max(best, run);
                }
                Assert.GreaterOrEqual(best, 3, $"{map}: the gate at {gate.Position} is {best} cells wide");
            }
        }

        /// <summary>
        /// Research scenario 4: attacking artillery in real sieges picks firing spots that are never
        /// in a doorway or its mouth, and never on a spot another gun has booked.
        /// </summary>
        [TestCaseSource(nameof(SiegeMaps))]
        public void FiringSpotsKeepOutOfDoorways(string map)
        {
            int checks = 0, onNoPark = 0, shared = 0;
            for (var seed = 1; seed <= 5; seed++)
            {
                var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(map + "_siege"), seed);
                var mode = new SiegeMode(new SiegeRules
                {
                    Attacker = new SideSetup
                    {
                        StartCp = 40f, Income = 1.6f, ArmyCap = 36,
                        Vehicles = new[] { "main_battle_tank", "heavy_tank", "tank_destroyer", "siege_tank", "mlrs", "engineer_vehicle" },
                    },
                    Defender = new SideSetup { StartCp = 16f, Income = 0.8f, Vehicles = new[] { "main_battle_tank", "ifv", "aa_vehicle" } },
                });
                mode.Setup(world);
                var defender = new ConquestAi(mode, 1, 0, AiDifficulty.Normal, 3) { Stance = CommanderStance.Defend, DefendPoint = mode.Fortress };
                var attacker = new ConquestAi(mode, 0, 1, AiDifficulty.Hard, 4 + seed)
                {
                    Goal = w => w.TryGetProp(mode.Target(w), out var objective) ? objective.Position : mode.Fortress,
                    Demolish = w => mode.Target(w),
                    RoleMix = ConquestAi.SiegeMix,
                };
                for (var i = 0; i < 90 * 20 && mode.Result == null; i++)
                {
                    mode.Tick(world, Step);
                    defender.Tick(world, Step);
                    attacker.Tick(world, Step);
                    world.Step(Step);
                    world.ClearEvents();
                    if (i % 10 != 0) continue;
                    // The lane map as it is now first (a wall that just fell makes a doorway, and a
                    // booking in it is released when the map is rebuilt), then the bookings.
                    _ = world.Lanes;
                    var guns = world.VehicleList.Where(v => v.IsAlive && v.Team == 0 && v.Def.Weapon.MinRange > 0f && LaneMap.InUse(v)).ToList();
                    foreach (var g in guns)
                    {
                        checks++;
                        if (world.Lanes.NoParkAt(g.Traffic.ReservedAt)) onNoPark++;
                    }
                    for (var a = 0; a < guns.Count; a++)
                    for (var b = a + 1; b < guns.Count; b++)
                    {
                        var (ax, ay) = world.Grid.CellOf(guns[a].Traffic.ReservedAt);
                        var (bx, by) = world.Grid.CellOf(guns[b].Traffic.ReservedAt);
                        if (Math.Abs(ax - bx) <= 2 && Math.Abs(ay - by) <= 2) shared++;
                    }
                }
            }
            Debug.Log($"Firing spots on {map}: {checks} checks, in doorways {onNoPark}, shared bookings {shared}");
            Assert.Greater(checks, 0, "the guns booked firing spots");
            Assert.AreEqual(0, onNoPark, "no firing spot in a doorway or its mouth");
            Assert.LessOrEqual(shared, checks / 1000, "guns do not share a booked spot");
        }

        /// <summary>
        /// Research scenarios 6 and 7: a 150-vehicle battle plays out identically twice from the same
        /// seed, and the path searches never overrun their per-step budget or keep a request waiting
        /// more than a second.
        /// </summary>
        [Test]
        public void ABigBattleIsDeterministicAndWithinTheSearchBudget()
        {
            var first = Battle(out var nodes, out var wait, out var yields);
            var second = Battle(out _, out _, out _);
            Debug.Log($"150-vehicle battle: hash {first}, most nodes in a step {nodes}, longest wait {wait:0.00} s, yields {yields}");
            Assert.AreEqual(first, second, "same seed, same battle");
            Assert.LessOrEqual(nodes, Sim.Movement.MovementSystem.PathNodeBudgetPerTick, "the per-step search budget holds");
            Assert.LessOrEqual(wait, 1.0, "the search queue drains within a second");
        }

        private static long Battle(out int nodes, out double wait, out int yields)
        {
            var kinds = new[] { "main_battle_tank", "heavy_tank", "tank_destroyer", "siege_tank", "mlrs", "light_tank", "ifv", "aa_vehicle" };
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("greenvale_conquest"), seed: 3);
            var mode = new ConquestMode(new ConquestRules
            {
                PlayerVehicles = kinds, EnemyVehicles = kinds, PlayerSupports = Array.Empty<string>(), EnemySupports = Array.Empty<string>(),
            });
            mode.Setup(world);
            world.TryGetRally(0, out var r0);
            world.TryGetRally(1, out var r1);
            for (var i = 0; i < 75; i++)
            {
                var offset = new Vector2(i % 9 * 5f - 20f, i / 9 * 5f - 20f) * 0.9f;
                world.SpawnVehicle(kinds[i % kinds.Length], 0, r0 + offset, 0.8f);
                world.SpawnVehicle(kinds[(i + 3) % kinds.Length], 1, r1 - offset, 3.9f);
            }
            var ai0 = new ConquestAi(mode, 0, 1, AiDifficulty.Hard, 5) { AutoDeploy = false, AutoStrike = false };
            var ai1 = new ConquestAi(mode, 1, 0, AiDifficulty.Hard, 6) { AutoDeploy = false, AutoStrike = false };
            long hash = 17;
            for (var i = 0; i < 3 * 60 * 20; i++)
            {
                mode.Tick(world, Step);
                ai0.Tick(world, Step);
                ai1.Tick(world, Step);
                world.Step(Step);
                world.ClearEvents();
                if (i % 20 != 0) continue;
                foreach (var v in world.VehicleList)
                    hash = hash * 31 + BitConverter.SingleToInt32Bits(v.Position.X) * 7 + BitConverter.SingleToInt32Bits(v.Position.Y) + v.Id.Value;
            }
            nodes = world.Movement.PathNodesMaxTick;
            wait = world.Movement.PathQueueLongestWait;
            yields = world.VehicleList.Sum(v => v.Traffic.Yields);
            return hash;
        }
    }
}
