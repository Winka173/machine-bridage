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
using MachineBrigade.Sim.Movement;
using MachineBrigade.Sim.Navigation;
using MachineBrigade.Sim.Sandbox;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// AI MASTER lane P0-D + P1 (movement / traffic): the staged jam detector (spec 37-38, 102), ORCA-lite and the passing
    /// side (34-36, 87), passage reservations (30-32, 85), the congestion tests of section 111 (20 vehicles one objective,
    /// two squads opposite one gate, heavy + scout, a wreck in a choke), the spawn exit (40), the deadlock wait-for graph
    /// (190), command deduplication (186), the artillery parking lease (41) and the SEVERE_UNSTUCK counter. Written by the
    /// lane, not run by it (the lead runs category AIMasterP1).
    /// </summary>
    [Category("AIMasterP1")]
    public class AiMasterP1Tests
    {
        private const float Step = 0.05f;

        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        // ------------------------------------------------------------------ worlds

        /// <summary>Base-wall segments (8 m) along x = line from 'from' to 'to', with gaps (centre, width).</summary>
        private static void WallX(List<PropPlacement> props, float line, float from, float to, params (float at, float width)[] gaps)
        {
            for (var u = from; u + 8f <= to + 1e-3f; u += 8f)
            {
                var lo = u;
                var hi = u + 8f;
                if (gaps.Any(g => hi > g.at - g.width / 2f + 1e-3f && lo < g.at + g.width / 2f - 1e-3f)) continue;
                props.Add(new PropPlacement("base_wall", new Vector2(line, u + 4f), 90));
            }
        }

        private static SimWorld World(List<PropPlacement> props, Vector2 rally0, Vector2 rally1, float size = 160f) =>
            new SimWorld(Catalog, new MapDefinition("p1_traffic", size, new[] { new TeamStart(0, rally0), new TeamStart(1, rally1) }, props,
                new List<UnitPlacement>()));

        /// <summary>A wall across the map at x = 0 with one gate 8 m wide at y = 0.</summary>
        private static SimWorld OneGate(Vector2 rally0, Vector2 rally1)
        {
            var props = new List<PropPlacement>();
            // (Segments from -76 put segment ends at +-4: from -72 they fell at 0 and +-8, the gate was 16 m with 12 m open and
            // no doorway, and the passages found were the map-edge gaps.)
            WallX(props, 0f, -76f, 76f, (0f, 8f));
            return World(props, rally0, rally1);
        }

        /// <summary>A wall at x = 0 with two gates 8 m wide at y = +24 and y = -24.</summary>
        private static SimWorld TwoGates()
        {
            var props = new List<PropPlacement>();
            WallX(props, 0f, -76f, 76f, (24f, 8f), (-24f, 8f));
            return World(props, new Vector2(-60f, -60f), new Vector2(60f, 60f));
        }

        private static void Order(SimWorld world, CommandType type, Vehicle v, Vector2 point) =>
            world.Submit(new Command(type, v.Team, new[] { v.Id }, point));

        private static void Run(SimWorld world, float seconds, Action<SimWorld> each = null)
        {
            for (var t = 0f; t < seconds; t += Step)
            {
                world.Step(Step);
                world.ClearEvents();
                each?.Invoke(world);
            }
        }

        private static Passage GateAt(SimWorld world, Vector2 near) =>
            world.Traffic.Passages.OrderBy(p => Vector2.Distance(p.Centre, near)).First();

        // ------------------------------------------------------------------ spec 37-38, 102: the jam tracker

        [Test]
        public void JamTrackerReachesEachStageAtTheSpecTimes()
        {
            var jam = new JamTracker();
            var seen = new Dictionary<JamStage, float>();
            for (var t = 0.25f; t <= 13f; t += 0.25f)
            {
                jam.Tick(moveIntent: true, engaging: false, waiting: false, desiredSpeed: 8f, actualSpeed: 0.2f, progressPerSecond: 0f, dt: 0.25f, now: t);
                if (!seen.ContainsKey(jam.Stage)) seen[jam.Stage] = t;
            }
            Assert.AreEqual(1.5f, seen[JamStage.Soft], 1e-3f, "stage 1 at 1.5 s");
            Assert.AreEqual(3f, seen[JamStage.LocalReplan], 1e-3f, "stage 2 at 3 s");
            Assert.AreEqual(5f, seen[JamStage.Yield], 1e-3f, "stage 3 at 5 s");
            Assert.AreEqual(8f, seen[JamStage.CorridorReplan], 1e-3f, "stage 4 at 8 s");
            Assert.AreEqual(12f, seen[JamStage.Emergency], 1e-3f, "stage 5 at 12 s");
            Assert.AreEqual(1, jam.Episodes);
        }

        [Test]
        public void JamTrackerFreezesWhileWaitingDrainsOnProgressAndResetsWhenEngaging()
        {
            var jam = new JamTracker();
            for (var i = 0; i < 8; i++) jam.Tick(true, false, false, 8f, 0f, 0f, 0.25f, i * 0.25);
            Assert.AreEqual(JamStage.Soft, jam.Stage, "2 s of low progress is a soft jam");
            for (var i = 0; i < 40; i++) jam.Tick(true, false, true, 8f, 0f, 0f, 0.25f, 2 + i * 0.25);
            Assert.AreEqual(JamStage.Soft, jam.Stage, "a deliberate wait (queue, yield) never escalates");
            Assert.AreEqual(2f, jam.LowProgressSeconds, 1e-3f);
            jam.Tick(true, false, false, 8f, 6f, 6f, 0.25f, 12);
            Assert.AreEqual(1.5f, jam.LowProgressSeconds, 1e-3f, "progress drains the low time twice as fast");
            jam.Tick(true, true, false, 8f, 0f, 0f, 0.25f, 12.25);
            Assert.AreEqual(JamStage.None, jam.Stage, "engaging its target ends the episode");
            Assert.AreEqual(0f, jam.LowProgressSeconds);
        }

        [Test]
        public void ShipsNeverReverseGroundVehiclesMayWithRoom()
        {
            var ship = Catalog.Vehicles.Values.Where(d => d.Naval != null).OrderBy(d => d.Id, StringComparer.Ordinal).First();
            var tank = Catalog.Vehicle("main_battle_tank");
            Assert.IsFalse(JamPolicy.AllowsReverse(ship, false));
            Assert.AreEqual(EmergencyMove.WidenTurnAlternate, JamPolicy.Emergency(ship, false, roomBehind: true), "naval: never reverse");
            Assert.AreEqual(EmergencyMove.ShortReverse, JamPolicy.Emergency(tank, false, roomBehind: true));
            Assert.AreEqual(EmergencyMove.PivotAlternate, JamPolicy.Emergency(tank, false, roomBehind: false), "no room behind: pivot");
            Assert.AreEqual(EmergencyMove.PivotAlternate, JamPolicy.Emergency(tank, true, roomBehind: true), "a train never backs up");
        }

        // ------------------------------------------------------------------ spec 34-36, 87: steering maths

        [Test]
        public void PassingSideIsFixedPerPairSymmetricAndNotAllTheSame()
        {
            Assert.AreEqual(TrafficSteering.PassingSide(7, 42), TrafficSteering.PassingSide(42, 7), "one side per pair, whoever asks");
            Assert.AreEqual(TrafficSteering.PassingSide(7, 42), TrafficSteering.PassingSide(7, 42), "the same every time");
            var sides = Enumerable.Range(1, 40).Select(i => TrafficSteering.PassingSide(i, i + 100)).Distinct().Count();
            Assert.AreEqual(2, sides, "both sides occur over many pairs");
        }

        [Test]
        public void MinimumSeparationAndResponsibilityFollowTheSpec()
        {
            Assert.AreEqual(4.5f, TrafficSteering.MinSeparation(2f, 2f, false, false), 1e-4f);
            Assert.AreEqual(4.5f * 1.5f, TrafficSteering.MinSeparation(2f, 2f, true, false), 1e-4f, "splash threat widens it");
            Assert.AreEqual(4.5f * 0.85f, TrafficSteering.MinSeparation(2f, 2f, false, true), 1e-4f, "a travel column narrows it");
            Assert.Greater(TrafficSteering.Responsibility(30, 80), 0.69f, "the lower right of way takes 70-100 %");
            Assert.Less(TrafficSteering.Responsibility(80, 30), 0.31f, "the higher 0-30 %");
            Assert.AreEqual(0.5f, TrafficSteering.Responsibility(50, 50));
        }

        [Test]
        public void OrcaLiteOncomingPairBothKeepRightAndAPassingPairIsLeftAlone()
        {
            // A goes north, B comes south 0.5 m to the east of A's line: both must steer to their own right (they diverge).
            var a = TrafficSteering.Avoid(new Vector2(0f, 0f), new Vector2(0f, 6f), 2f, 50, 1, new Vector2(0.5f, 12f), new Vector2(0f, -6f), 2f, 50, 2,
                1.5f, 4.5f, -1);
            var b = TrafficSteering.Avoid(new Vector2(0.5f, 12f), new Vector2(0f, -6f), 2f, 50, 2, new Vector2(0f, 0f), new Vector2(0f, 6f), 2f, 50, 1,
                1.5f, 4.5f, -1);
            Assert.Greater(a.X, 0f, "A (north-bound) to its right: east");
            Assert.Less(b.X, 0f, "B (south-bound) to its right: west");
            var far = TrafficSteering.Avoid(new Vector2(0f, 0f), new Vector2(0f, 6f), 2f, 50, 1, new Vector2(20f, 12f), new Vector2(0f, -6f), 2f, 50, 2,
                1.5f, 4.5f, 1);
            Assert.AreEqual(Vector2.Zero, far, "no overlap within 1.5 s: no avoidance");
            var scout = TrafficSteering.Avoid(new Vector2(0f, 0f), new Vector2(0f, 6f), 2f, 30, 1, new Vector2(0.5f, 12f), new Vector2(0f, -6f), 2f, 80, 2,
                1.5f, 4.5f, 1);
            var heavy = TrafficSteering.Avoid(new Vector2(0.5f, 12f), new Vector2(0f, -6f), 2f, 80, 2, new Vector2(0f, 0f), new Vector2(0f, 6f), 2f, 30, 1,
                1.5f, 4.5f, 1);
            Assert.Greater(scout.Length(), heavy.Length() * 2f, "the scout takes most of the avoidance, the heavy keeps its line");
        }

        // ------------------------------------------------------------------ spec 30-32, 85: reservations

        [Test]
        public void TwoSquadsOppositeOneGateOneWayIsGrantedTheOtherQueuesAndGetsTheNextTurn()
        {
            var world = OneGate(new Vector2(-60f, 0f), new Vector2(60f, 0f));
            world.Step(Step);
            var traffic = world.Traffic;
            var gate = GateAt(world, Vector2.Zero);
            Assert.Less(Vector2.Distance(gate.Centre, Vector2.Zero), 4f, "the gate is a passage");
            const int east = 1 * 65536 + 1, west = 1 * 65536 + 2, eastToo = 1 * 65536 + 3;
            var wayEast = gate.DirectionOf(new Vector2(1f, 0f));
            Assert.AreEqual(PassageGrant.Granted, traffic.Request(gate, 1, east, wayEast, 50, 4, out _), "first come: granted");
            Assert.AreEqual(PassageGrant.Queued, traffic.Request(gate, 1, west, -wayEast, 50, 4, out var q), "the other way waits");
            Assert.AreEqual(0, q, "at Q1");
            Assert.AreEqual(PassageGrant.Granted, traffic.Request(gate, 1, eastToo, wayEast, 50, 3, out _), "the same way is batched");
            Assert.AreEqual(PassageGrant.Queued, traffic.Request(gate, 1, west, -wayEast, 50, 4, out _), "still waiting: no inching both ways");
            traffic.Release(gate, 1, east);
            traffic.Release(gate, 1, eastToo);
            Assert.AreEqual(PassageGrant.Granted, traffic.Request(gate, 1, west, -wayEast, 50, 4, out _), "the turn goes to the waiting way");
            Assert.AreEqual(PassageGrant.Queued, traffic.Request(gate, 1, east, wayEast, 50, 4, out _));
            // The queue positions are on the near side of the gate for each way, off its mouth.
            var qEast = gate.QueuePoint(wayEast, 0);
            Assert.Less(Vector2.Dot(qEast - gate.Centre, gate.Through * wayEast), 0f, "Q1 lies before the gate for its way");
        }

        [Test]
        public void AHigherRightOfWayTakesThePassageOnlyAfterTheTwoSecondHold()
        {
            var world = OneGate(new Vector2(-60f, 0f), new Vector2(60f, 0f));
            world.Step(Step);
            var traffic = world.Traffic;
            var gate = GateAt(world, Vector2.Zero);
            Assert.AreEqual(PassageGrant.Granted, traffic.Request(gate, 1, 10, 1, 30, 2, out _));
            Assert.AreEqual(PassageGrant.Queued, traffic.Request(gate, 1, 11, -1, 100, 1, out _), "held for 2 s: even a boss waits");
            Run(world, 2.1f);
            Assert.AreEqual(PassageGrant.Granted, traffic.Request(gate, 1, 11, -1, 100, 1, out _), "after the hold the boss takes it");
            Assert.AreEqual(1, traffic.Stats.PassagePreempts);
        }

        [Test]
        public void TwoGroupsOppositeOneGateBothGetThroughWithoutRelocation()
        {
            var world = OneGate(new Vector2(-60f, -60f), new Vector2(60f, 60f));
            var west = Enumerable.Range(0, 3).Select(i => world.SpawnVehicle("main_battle_tank", 0, new Vector2(-30f - i * 9f, (i - 1) * 6f), MathF.PI / 2)).ToList();
            var east = Enumerable.Range(0, 3).Select(i => world.SpawnVehicle("main_battle_tank", 0, new Vector2(30f + i * 9f, (i - 1) * 6f), -MathF.PI / 2)).ToList();
            foreach (var v in west) Order(world, CommandType.Move, v, new Vector2(45f, 0f));
            foreach (var v in east) Order(world, CommandType.Move, v, new Vector2(-45f, 0f));
            var t = 0f;
            for (; t < 120f; t += Step)
            {
                world.Step(Step);
                world.ClearEvents();
                if (west.All(v => v.Position.X > 8f) && east.All(v => v.Position.X < -8f)) break;
            }
            Debug.Log($"P1 opposite gate: through in {t:0.0} s; {world.Traffic.Stats}");
            Assert.IsTrue(west.All(v => v.Position.X > 8f) && east.All(v => v.Position.X < -8f), "both ways got through (no inching forever)");
            Assert.AreEqual(0, world.SevereUnstuckCount, "no relocation in normal traffic");
        }

        // ------------------------------------------------------------------ section 111: heavy + scout

        [Test]
        public void HeavyAndScoutMeetInAGateTheScoutGivesWayTheHeavyKeepsTheRoad()
        {
            var world = OneGate(new Vector2(-60f, -60f), new Vector2(60f, 60f));
            var heavy = world.SpawnVehicle("heavy_tank", 0, new Vector2(-20f, 0f), MathF.PI / 2);
            var scout = world.SpawnVehicle("scout_jeep", 0, new Vector2(20f, 0f), -MathF.PI / 2);
            world.Step(Step);
            Assert.Greater(world.Traffic.RightOfWay(heavy), world.Traffic.RightOfWay(scout), "heavy 80 over scout 30");
            Order(world, CommandType.Move, heavy, new Vector2(40f, 0f));
            Order(world, CommandType.Move, scout, new Vector2(-40f, 0f));
            var heavyBacked = false;
            var scoutGaveWay = false;
            Run(world, 45f, w =>
            {
                heavyBacked |= heavy.Traffic.Reversing(w.Time) || heavy.Traffic.YieldingTo == scout.Id;
                scoutGaveWay |= scout.Traffic.Reversing(w.Time) || scout.Traffic.YieldingTo.IsValid || scout.Traffic.GateWaitId != 0;
            });
            Assert.IsFalse(heavyBacked, "the heavy never backs out or steps aside for the scout");
            Assert.Greater(heavy.Position.X, 30f, "the heavy kept the road");
            Assert.Less(scout.Position.X, -30f, "the scout got through after");
            Assert.AreEqual(0, world.SevereUnstuckCount);
        }

        // ------------------------------------------------------------------ section 111: wreck in a choke

        [Test]
        public void AWreckInTheGateIsSeenAtOnceAndTheRouteGoesRoundIt()
        {
            var world = TwoGates();
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-45f, 22f), MathF.PI / 2);
            Order(world, CommandType.Move, tank, new Vector2(45f, 22f));
            Run(world, 2f);
            Assert.IsTrue(tank.HasPath && tank.Path.Any(p => Vector2.Distance(p, new Vector2(0f, 24f)) < 12f) ||
                          Vector2.Distance(tank.PathGoal, new Vector2(45f, 22f)) < 2f, "on its way through the north gate");
            // A friend dies in the north gate: its hulk closes it.
            var hulk = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 24f), 0f);
            hulk.Hp = 0f;
            world.Wrecks.Add(hulk, world.Time);
            var replansBefore = world.Traffic.Stats.WreckReplans;
            Run(world, 0.15f);
            Assert.Greater(world.Traffic.Stats.WreckReplans, replansBefore, "the route through the wreck was planned again at once");
            var wreck = world.Wrecks.List.First(w => w.Id == hulk.Id);
            var from = tank.Position;
            var clear = true;
            for (var i = tank.PathIndex; i < tank.Path.Count; i++)
            {
                MovementSystem.ClosestPoints(from, tank.Path[i], wreck.A, wreck.B, out var c1, out var c2);
                if (Vector2.Distance(c1, c2) < wreck.Radius + 1f) clear = false;
                from = tank.Path[i];
            }
            Assert.IsTrue(clear, "the new route keeps off the hulk");
            var stuckSince = (double)world.Time;
            var anchor = tank.Position;
            var worst = 0.0;
            Run(world, 40f, w =>
            {
                if (Vector2.Distance(anchor, tank.Position) > 2.5f)
                {
                    anchor = tank.Position;
                    stuckSince = w.Time;
                }
                else if (tank.HasPath) worst = Math.Max(worst, w.Time - stuckSince);
            });
            Assert.Greater(tank.Position.X, 30f, "it got through (the other gate)");
            Assert.Less(worst, 10.0, "never stood 10 s before noticing");
        }

        // ------------------------------------------------------------------ section 111: twenty vehicles, one objective

        [Test]
        public void TwentyVehiclesOneObjectiveShareCorridorsBatchAtTheGateAndNeverShareASlot()
        {
            // No fog: the objective (the enemy tank past the gate) is known. Under fog nothing is known of it and the side
            // holds at home (AI MASTER P3 memory: no target, no march), so no one ever went through the gate.
            var s = new SandboxScenario { Seed = 11, Fog = false };
            s.Sides[0].Ai = SandboxAi.Full;
            s.Sides[1].Ai = SandboxAi.Idle;
            for (var i = 0; i < 20; i++)
                s.Units.Add(new SandboxUnit { Def = "main_battle_tank", Team = 0, X = -50f + i % 5 * 7f, Y = -20f + i / 5 * 7f, Heading = 90f });
            s.Units.Add(new SandboxUnit { Def = "main_battle_tank", Team = 1, X = 55f, Y = 0f, Heading = 270f });
            var world = OneGate(new Vector2(-60f, 0f), new Vector2(60f, 0f));
            var battle = new SandboxBattle(s);
            battle.Setup(world);
            var duplicateSlots = 0;
            var maxCorridors = 0;
            for (var t = 0f; t < 90f && !world.IsOver; t += Step)
            {
                battle.Tick(world, Step);
                world.Step(Step);
                world.ClearEvents();
                if (world.Tick % 40 != 0) continue;
                var movers = world.Vehicles.Where(v => v.IsAlive && v.Team == 0 && v.Order.Kind is OrderKind.Move or OrderKind.AttackMove).ToList();
                for (var i = 0; i < movers.Count; i++)
                for (var j = i + 1; j < movers.Count; j++)
                    if (Vector2.Distance(movers[i].Order.Point, movers[j].Order.Point) < 0.5f) duplicateSlots++;
                maxCorridors = Math.Max(maxCorridors, movers.Select(v => v.Traffic.CorridorId).Where(c => c != 0).Distinct().Count());
            }
            var stats = world.Traffic.Stats;
            var squads = battle.Commander(0)?.Commander?.Squads.Squads.Count ?? 0;
            Debug.Log($"P1 twenty: squads {squads}, corridors live {maxCorridors}, {stats}");
            Assert.GreaterOrEqual(squads, 2, "20 vehicles are split into squads");
            Assert.Greater(stats.CorridorRoutes, 10, "members follow shared corridors, not 20 route searches");
            Assert.Greater(stats.PassageGrants, 0, "the gate on the way is reserved");
            Assert.AreEqual(0, duplicateSlots, "no two vehicles sent to one cell");
            Assert.AreEqual(0, world.SevereUnstuckCount);
        }

        // ------------------------------------------------------------------ spec 40: spawn exit

        [Test]
        public void SpawnExitIsNoParkingAndABlockedExitIsCleared()
        {
            var world = World(new List<PropPlacement>(), new Vector2(-50f, 0f), new Vector2(50f, 0f));
            Run(world, 1f);
            Assert.IsTrue(world.Bases.TryGetDropZone(0, out var zone));
            var traffic = world.Traffic;
            Assert.IsTrue(traffic.Exits.Any(e => e.Team == 0), "the drop zone has an exit");
            var gun = world.SpawnVehicle("main_battle_tank", 0, zone + new Vector2(30f, 0f), 0f);
            Assert.IsFalse(traffic.CanPark(zone + new Vector2(2f, 0f), gun), "no firing spot in the exit box");
            Assert.GreaterOrEqual(Vector2.Distance(traffic.OutOfExit(zone + new Vector2(2f, 0f), 0), zone), SimTunables.Ai.Traffic.SpawnRallyRadius - 0.5f,
                "a rally point there moves out to the rally ring");
            // Parked friends all round the drop zone, then a newcomer that has to get out through them.
            var parked = new List<Vehicle>();
            // Two rings (12 at 8 m, 18 at 14 m), hull to hull: one 8-hull 6 m ring is spread by the hulls' separation into
            // gaps a tank shoves through at 40 % speed (never "crawling", so nothing is blocked and nothing needs clearing).
            for (var k = 0; k < 30; k++)
            {
                var inner = k < 12;
                var angle = inner ? k * MathF.PI / 6f : (k - 12) * MathF.PI / 9f + MathF.PI / 18f;
                var ring = zone + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * (inner ? 8f : 14f);
                var tank = world.SpawnVehicle("main_battle_tank", 0, ring, 0f);
                // The spawn's free-spot search spreads hulls (to 1.6 x their bound): put each back on the ring.
                tank.Position = ring;
                parked.Add(tank);
            }
            Run(world, 4f);
            var newcomer = world.SpawnVehicle("main_battle_tank", 0, zone, MathF.PI / 2);
            // (Likewise the newcomer: the free-spot search would have put it outside the ring, with nothing to get through.)
            newcomer.Position = zone;
            Order(world, CommandType.Move, newcomer, zone + new Vector2(45f, 0f));
            Run(world, 25f);
            Assert.Greater(newcomer.Position.X, zone.X + 30f, "the newcomer got out");
            Assert.IsTrue(traffic.Stats.SpawnExitClears > 0 || parked.All(v => Vector2.Distance(v.Position, zone) >= SimTunables.Ai.Traffic.SpawnExitRadius) ||
                          parked.Sum(v => v.Traffic.Yields) > 0, "the parked ones made way (cleared to the ring, or yielded)");
            Assert.AreEqual(0, world.SevereUnstuckCount);
        }

        // ------------------------------------------------------------------ spec 190: deadlock cycle

        [Test]
        public void AWaitForCycleIsBrokenByItsLowestRightOfWay()
        {
            var world = World(new List<PropPlacement>(), new Vector2(-50f, -50f), new Vector2(50f, 50f));
            var a = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            var b = world.SpawnVehicle("main_battle_tank", 0, new Vector2(7f, 0f), 0f);
            var c = world.SpawnVehicle("scout_jeep", 0, new Vector2(3.5f, 6f), 0f);
            Order(world, CommandType.Move, a, new Vector2(30f, 0f));
            Order(world, CommandType.Move, b, new Vector2(3f, 30f));
            Order(world, CommandType.Move, c, new Vector2(-30f, 0f));
            // Step until the next step is the wait-for graph's (once a second).
            while ((world.Tick + 1) % SimTunables.Ai.Traffic.DeadlockTicks != 7) world.Step(Step);
            void Wait(Vehicle v, Vehicle on)
            {
                v.Traffic.QueueBehind = on.Id;
                v.Traffic.QueueUntil = world.Time + 10.0;
            }
            Wait(a, b);
            Wait(b, c);
            Wait(c, a);
            var before = world.Traffic.Stats.Deadlocks;
            world.Step(Step);
            Assert.AreEqual(before + 1, world.Traffic.Stats.Deadlocks, "A -> B -> C -> A found once");
            Assert.IsFalse(c.Traffic.QueueBehind.IsValid, "the scout (lowest right of way) stops waiting and makes way");
            Assert.IsTrue(a.Traffic.QueueBehind.IsValid && b.Traffic.QueueBehind.IsValid, "the others keep their places");
            Assert.IsTrue(world.AiLog.Entries.Any(e => e.Kind == DecisionKind.Traffic && e.Text.StartsWith("TRAFFIC_DEADLOCK_CYCLE")));
        }

        // ------------------------------------------------------------------ spec 186, 41

        [Test]
        public void AnEquivalentAiOrderIsNotIssuedAgain()
        {
            var world = World(new List<PropPlacement>(), new Vector2(-50f, -50f), new Vector2(50f, 50f));
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-30f, 0f), MathF.PI / 2);
            Order(world, CommandType.Move, tank, new Vector2(30f, 0f));
            Run(world, 1f);
            var index = tank.PathIndex;
            var path = tank.Path.ToList();
            Order(world, CommandType.Move, tank, new Vector2(30f, 0f));
            Assert.AreEqual(1, world.Traffic.Stats.CommandsDeduplicated);
            Assert.AreEqual(index, tank.PathIndex);
            CollectionAssert.AreEqual(path, tank.Path.ToList(), "its route was not reset");
            world.Submit(new Command(CommandType.Move, 0, new[] { tank.Id }, new Vector2(30f, 0f), manual: true));
            Assert.AreEqual(1, world.Traffic.Stats.CommandsDeduplicated, "a player's order always goes through");
        }

        [Test]
        public void ArtilleryParkingIsALeaseAndKeepsSplashSpacing()
        {
            var def = Catalog.Vehicles.Values.Where(d => d.Class == UnitClass.Artillery && !d.Static && !d.Flying && d.Naval == null && !d.Boss)
                .OrderBy(d => d.Id, StringComparer.Ordinal).First();
            var world = World(new List<PropPlacement>(), new Vector2(-60f, -60f), new Vector2(60f, 60f));
            var first = world.SpawnVehicle(def.Id, 0, new Vector2(0f, 0f), 0f);
            var second = world.SpawnVehicle(def.Id, 0, new Vector2(30f, 30f), 0f);
            world.Step(Step);
            world.Lanes.Reserve(first.Position, first);
            Assert.IsTrue(LaneMap.InUse(first), "booked where it stands");
            Assert.IsFalse(world.Traffic.CanPark(first.Position + new Vector2(4f, 0f), second), "not within 1.5 x the splash spacing");
            Assert.IsTrue(world.Traffic.CanPark(first.Position + new Vector2(25f, 0f), second));
            first.Position += new Vector2(6f, 0f);
            Assert.IsFalse(LaneMap.InUse(first), "the lease lapses once it is more than 5 m away");
        }

        // ------------------------------------------------------------------ SEVERE_UNSTUCK

        [Test]
        public void ARelocationIsTheLastFailSafeCountedAsSevereUnstuck()
        {
            var world = World(new List<PropPlacement>(), new Vector2(-50f, -50f), new Vector2(50f, 50f));
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            Run(world, 0.5f);
            // The ground closes under it (as in StuckCauseTests): the jam stages cannot help, only the fail-safe can.
            world.Grid.AddBlocker(new Vector2(0f, 0f), 4f, 4f, SimWorld.ObstacleClearance);
            void Commander(float seconds)
            {
                for (var t = 0f; t < seconds; t += Step)
                {
                    if (tank.Order.Kind == OrderKind.Idle && Vector2.Distance(tank.Position, new Vector2(30f, 0f)) > 6f) Order(world, CommandType.Move, tank, new Vector2(30f, 0f));
                    world.Step(Step);
                    world.ClearEvents();
                }
            }
            Commander(SimTunables.Ai.Navigation.FailSafeS - 2f);
            Assert.AreEqual(0, world.SevereUnstuckCount, "not before the fail-safe time (after stage 5)");
            Commander(8f);
            Assert.GreaterOrEqual(world.SevereUnstuckCount, 1, "then relocated, and counted");
            var stats = world.Traffic.Stats;
            Assert.AreEqual(stats.SevereUnstuck, stats.SeverePlace + stats.SevereHop);
            Assert.IsTrue(world.AiLog.Entries.Any(e => e.Kind == DecisionKind.Traffic && e.Text.StartsWith("SEVERE_UNSTUCK")), "logged SEVERE_UNSTUCK");
            Assert.IsTrue(world.Grid.IsWalkable(tank.Position), "on open ground now");
        }

        [Test]
        public void MovementDebugCarriesTheSpecFields()
        {
            var world = World(new List<PropPlacement>(), new Vector2(-50f, -50f), new Vector2(50f, 50f));
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-30f, 0f), MathF.PI / 2);
            Order(world, CommandType.Move, tank, new Vector2(30f, 0f));
            Run(world, 1f);
            var d = world.Traffic.DebugOf(tank);
            Assert.Greater(d.DesiredVelocity.Length(), 0.1f);
            Assert.AreEqual(new Vector2(30f, 0f).X, d.FormationSlot.X, 1f);
            Assert.AreEqual(JamStage.None, d.JamStage);
            Assert.GreaterOrEqual(d.TrafficPriority, TrafficSteering.PriorityScout);
            StringAssert.Contains("Move", d.StrategicTask);
        }
    }
}
