using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Movement;
using MachineBrigade.Sim.Navigation;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 33 L5 (DECISIONS "Prompt 33 L5"): the rails. A crossing goes OPEN -> WARNING -> CLOSED -> TRAIN_PASSING -> OPEN on
    /// the ticks its rule gives, warning at least its time; a Siege support train comes in at the gate on its entry tick, where
    /// the view's stand-in meets it; vehicles on the line are told to leave, whoever stays is put beside it, nobody is trapped
    /// or left under a train; new routes keep off a warning crossing; nobody parks on a rail; the boss trains are held on their
    /// lines; the maps the prompt names have their rails; the same battle twice ends the same. Written for the lead to run (the
    /// owner's rule: agents write tests, they do not run them).
    /// </summary>
    public class Prompt33RailTests
    {
        private const float Dt = 0.05f;
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        /// <summary>A plain 300 m field with one rail along z = 0 from a portal beyond the west edge to one beyond the east, crossed by a road at x = 0.</summary>
        private static SimWorld Field(int seed = 1, string kind = "line")
        {
            var map = new MapDefinition("rail_field", 300f,
                new[] { new TeamStart(0, new Vector2(-108.75f, -108.75f)), new TeamStart(1, new Vector2(108.75f, 108.75f)) },
                new List<PropPlacement>(), new List<UnitPlacement>());
            var crossing = new RailCrossingDef("x1", 190f, new Vector2(0f, 0f), 8f, 7f, 11f);
            map.Rails = new[] { new RailSpline("main", kind, new[] { new Vector2(-190f, 0f), new Vector2(190f, 0f) }, 40f, 340f, new[] { crossing }) };
            return new SimWorld(Catalog, map, seed);
        }

        /// <summary>A Siege-like line in: from a portal far beyond the north edge down to a buffer stop at z = 96, its gate at z = 146.</summary>
        private static SimWorld SiegeField(int seed = 1)
        {
            var map = new MapDefinition("siege_field", 300f,
                new[] { new TeamStart(0, new Vector2(-108.75f, -108.75f)), new TeamStart(1, new Vector2(108.75f, 108.75f)) },
                new List<PropPlacement>(), new List<UnitPlacement>());
            var crossing = new RailCrossingDef("x1", 98f, new Vector2(24f, 112f), 7f, 12f, 11f);
            map.Rails = new[] { new RailSpline("siege_line", "siege", new[] { new Vector2(24f, 210f), new Vector2(24f, 96f) }, 64f, 114f, new[] { crossing }) };
            return new SimWorld(Catalog, map, seed);
        }

        private static void Order(SimWorld world, Vehicle v, Vector2 to) =>
            Assert.IsTrue(world.Submit(new Command(CommandType.Move, v.Team, new[] { v.Id }, to)).Accepted, "the move is taken");

        private static void Run(SimWorld world, float seconds, Action<int> each = null)
        {
            var ticks = (int)(seconds / Dt);
            for (var t = 0; t < ticks; t++)
            {
                world.Step(Dt);
                world.ClearEvents();
                each?.Invoke(t);
            }
        }

        // ================================================================== the crossing's states

        [Test]
        public void ACrossingChangesStateOnTheTicksItsRuleGives()
        {
            var world = Field();
            var rails = world.Rails;
            var crossing = rails.Crossings[0];
            Assert.AreEqual(4f, crossing.WarnSeconds, 1e-4f, "max(4 s, 11 m / 4.5 m/s + 0.5 s)");
            Assert.IsTrue(crossing.Closes, "its closed state passed the load-time check");
            var train = world.SpawnVehicle("armored_train", 1, new Vector2(-40f, 0.5f), MathF.PI * 0.5f);
            Assert.IsTrue(train.OnRail, "the train is held on the rail");
            Assert.AreEqual(0f, train.Position.Y, 1e-3f, "on the line");
            Order(world, train, new Vector2(120f, 0f));
            var line = rails.Lines[0];
            var lo = crossing.Def.S - crossing.Def.Half - 1f;
            var hi = crossing.Def.S + crossing.Def.Half + 1f;
            var half = train.Def.Length * 0.5f;
            var top = train.Def.Speed;
            long warnedAt = -1, closedAt = -1, passingAt = -1, openAgainAt = -1, firstOn = -1, lastOn = -1;
            var bad = new List<string>();
            Run(world, 400f, _ =>
            {
                var front = train.RailS + half;
                var back = train.RailS - half;
                var on = back <= hi && front >= lo;
                var distance = lo - front;
                if (on && firstOn < 0) firstOn = world.Tick;
                if (on) lastOn = world.Tick;
                var state = crossing.State;
                if (state == CrossingState.Warning && warnedAt < 0)
                {
                    warnedAt = world.Tick;
                    // The first tick a train is within its warning + 1.5 s at its top speed, or 8 m.
                    if (!(distance / top <= crossing.WarnSeconds + RailSystem.CloseLead || distance <= RailSystem.WarnFloor))
                        bad.Add($"warned at tick {world.Tick} with the train {distance:0.00} m off");
                }
                if (state == CrossingState.Closed && closedAt < 0) closedAt = world.Tick;
                if (state == CrossingState.TrainPassing && passingAt < 0) passingAt = world.Tick;
                if (passingAt >= 0 && state == CrossingState.Open && openAgainAt < 0) openAgainAt = world.Tick;
                if (on && state != CrossingState.TrainPassing && state != CrossingState.Closed) bad.Add($"tick {world.Tick}: the train is on it, the crossing is {state}");
                // The prebuilt ground state follows the barriers one tick later.
                var site = world.NavStates.ActiveOf(crossing.Site);
                if (state is CrossingState.Open or CrossingState.Warning && crossing.Since < world.Tick && site != RailSystem.OpenState)
                    bad.Add($"tick {world.Tick}: {state} but its ground is {site}");
            });
            Assert.IsEmpty(bad, string.Join("\n", bad.Take(10)));
            Assert.Greater(warnedAt, 0, "it warned");
            Assert.Greater(closedAt, warnedAt);
            Assert.GreaterOrEqual((closedAt - warnedAt) * Dt, crossing.WarnSeconds - 1e-3, "WARNING lasted at least its time");
            Assert.AreEqual(firstOn, passingAt, "TRAIN_PASSING on the first tick the train is on it");
            Assert.AreEqual(lastOn + RailSystem.ClearHoldTicks, openAgainAt, "OPEN 0.5 s after the train has gone");
            var states = crossing.History.Select(h => h.state).ToList();
            CollectionAssert.AreEqual(new[] { CrossingState.Warning, CrossingState.Closed, CrossingState.TrainPassing, CrossingState.Open }, states.Take(4).ToList(),
                "OPEN -> WARNING -> CLOSED -> TRAIN_PASSING -> OPEN");
        }

        // ================================================================== the Siege support train

        [Test]
        public void ASupportTrainComesInAtTheGateOnItsTickWhereTheViewsTrainMeetsIt()
        {
            var world = SiegeField();
            var rails = world.Rails;
            var line = rails.Lines[0];
            world.Emit(SimEvent.ArrivalInbound(1, "rail", new Vector2(30f, 108f), new Vector2(0f, -1f), 10f));
            Assert.AreEqual(1, rails.Runs.Count, "the announced train has its run");
            var run = rails.Runs[0];
            Assert.AreEqual(line.Length - RailSystem.SupportStopBack, run.StopFront, 1e-3f, "its front stops where the view's does (12.5 m short of the end)");
            var crossing = rails.Crossings[0];
            long expectedEntry = -1;
            long warnedAt = -1, closedAt = -1;
            var bad = new List<string>();
            Run(world, 30f, _ =>
            {
                if (expectedEntry < 0 && run.FrontAt(world.Time) >= line.PlayFrom) expectedEntry = world.Tick;
                if (crossing.State == CrossingState.Warning && warnedAt < 0) warnedAt = world.Tick;
                if (crossing.State == CrossingState.Closed && closedAt < 0) closedAt = world.Tick;
                // The view's stand-in (FortressView, the same curve) at the gate on the entry tick.
                if (world.Tick == run.EntryTick)
                {
                    var stand = line.Length - RailSystem.SupportStopBack + RailSystem.SupportOffset((float)(world.Time - run.Due));
                    if (MathF.Abs(stand - run.FrontAt(world.Time)) > 1e-3f) bad.Add("the stand-in is not where the run is");
                    if (stand < line.PlayFrom || stand > line.PlayFrom + 2f) bad.Add($"the run came in {stand - line.PlayFrom:0.00} m past the gate");
                }
            });
            Assert.IsEmpty(bad, string.Join("\n", bad));
            Assert.AreEqual(expectedEntry, run.EntryTick, "in play from the first tick its front is past the gate");
            Assert.Greater(run.ExitTick, run.EntryTick, "and out again");
            Assert.IsTrue(rails.Finished.Contains(run));
            Assert.Greater(warnedAt, 0, "the crossing warned");
            Assert.GreaterOrEqual((closedAt - warnedAt) * Dt, crossing.WarnSeconds - 1e-3, "for at least its time");
        }

        // ================================================================== off the line, nobody trapped

        [Test]
        public void VehiclesOnTheLineAreToldToLeaveAndNobodyIsTrappedOrRunOver()
        {
            var world = Field(3);
            var rails = world.Rails;
            var line = rails.Lines[0];
            var train = world.SpawnVehicle("armored_train", 1, new Vector2(-60f, 0f), MathF.PI * 0.5f);
            // Parked on the line ahead of it, on the crossing, and across it.
            var parked = new List<Vehicle>
            {
                world.SpawnVehicle("main_battle_tank", 0, new Vector2(-30f, 0f), 0f),
                world.SpawnVehicle("light_tank", 0, new Vector2(-20f, 1.5f), MathF.PI * 0.5f),
                world.SpawnVehicle("ifv", 0, new Vector2(0f, -1f), 0f),
                world.SpawnVehicle("truck", 1, new Vector2(10f, 0.5f), 0f),
            };
            // One of them broken down (it cannot drive off): the train puts it beside the line.
            world.Status.Stun(parked[0], 1e9);
            Order(world, train, new Vector2(60f, 0f));
            var bad = new List<string>();
            Run(world, 420f, _ =>
            {
                var back = train.RailS - train.Def.Length * 0.5f;
                var front = train.RailS + train.Def.Length * 0.5f;
                foreach (var v in parked)
                {
                    if (!v.IsAlive) continue;
                    var s = line.Project(v.Position, out var lateral);
                    if (s >= back && s <= front && MathF.Abs(lateral) < train.Def.Width * 0.5f + v.Radius - 0.05f)
                        bad.Add($"tick {world.Tick}: {v.Def.Id} under the train");
                    if (!world.Grid.IsWalkable(v.Position)) bad.Add($"tick {world.Tick}: {v.Def.Id} on closed ground");
                }
            });
            Assert.IsEmpty(bad, string.Join("\n", bad.Take(10)));
            Assert.Greater(rails.Told, 0, "vehicles on the line were told to get off it");
            Assert.Greater(rails.Pushed, 0, "the one that could not was put beside the line");
            var main = world.Grid.MainRegion;
            foreach (var v in parked.Where(v => v.IsAlive))
                Assert.AreEqual(main, world.Grid.RegionOf(v.Position), v.Def.Id + " is not trapped");
        }

        [Test]
        public void ASupportTrainOnlyPushesABossTrainRams()
        {
            var world = SiegeField(4);
            var line = world.Rails.Lines[0];
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(24f, 120f), 0f);
            world.Status.Stun(tank, 1e9);
            var hp = tank.Hp;
            world.Emit(SimEvent.ArrivalInbound(1, "rail", new Vector2(30f, 108f), new Vector2(0f, -1f), 10f));
            Run(world, 15f);
            line.Project(tank.Position, out var lateral);
            Assert.GreaterOrEqual(MathF.Abs(lateral), RailSpline.BandHalf, "put beside the line");
            Assert.AreEqual(hp, tank.Hp, 1e-3f, "a support train does no damage");

            var field = Field(5);
            var train = field.SpawnVehicle("armored_train", 1, new Vector2(-40f, 0f), MathF.PI * 0.5f);
            var victim = field.SpawnVehicle("main_battle_tank", 0, new Vector2(-10f, 0f), 0f);
            field.Status.Stun(victim, 1e9);
            var before = victim.Hp;
            Order(field, train, new Vector2(60f, 0f));
            Run(field, 200f);
            Assert.Less(victim.Hp, before, "a boss train rams the enemy it pushes aside");
        }

        // ================================================================== routes and parking

        [Test]
        public void NewRoutesKeepOffACrossingThatWarns()
        {
            var world = Field(6);
            var crossing = world.Rails.Crossings[0];
            var train = world.SpawnVehicle("armored_train", 1, new Vector2(-24f, 0f), MathF.PI * 0.5f);
            Order(world, train, new Vector2(60f, 0f));
            Run(world, 0.5f);
            Assert.AreNotEqual(CrossingState.Open, crossing.State, "the train is within 8 m: the crossing warns");
            var start = new Vector2(0f, -30f);
            var tank = world.SpawnVehicle("main_battle_tank", 0, start, 0f);
            Order(world, tank, new Vector2(0f, 30f));
            if (tank.PathQueued) world.Step(Dt);
            Assert.Greater(tank.Path.Count, 0, "a route was found");
            var min = crossing.Def.Position - new Vector2(crossing.Def.Width, crossing.Def.Depth) * 0.5f;
            var max = crossing.Def.Position + new Vector2(crossing.Def.Width, crossing.Def.Depth) * 0.5f;
            var from = start;
            foreach (var p in tank.Path)
            {
                for (var k = 0; k <= 20; k++)
                {
                    var q = from + (p - from) * (k / 20f);
                    Assert.IsFalse(q.X > min.X && q.X < max.X && q.Y > min.Y && q.Y < max.Y, $"the route crosses the warning crossing at ({q.X:0.0}, {q.Y:0.0})");
                }
                from = p;
            }
        }

        [Test]
        public void NobodyParksOnARail()
        {
            var world = Field(7);
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-40f, -20f), 0f);
            Order(world, tank, new Vector2(-40f, 0.5f));
            Run(world, 1f);
            Assert.Greater(tank.Path.Count, 0);
            world.Rails.Lines[0].Project(tank.PathGoal, out var lateral);
            Assert.GreaterOrEqual(MathF.Abs(lateral), RailSpline.BandHalf + tank.Radius, "its route ends beside the line, not on it");
            Assert.Less(lateral, 0f, "on its own side");
        }

        // ================================================================== the maps and the boss trains

        [Test]
        public void TheMapsThePromptNamesHaveTheirRails()
        {
            foreach (var id in new[] { "ironport_conquest", "rustyard_conquest", "metrocity_conquest", "foundry_conquest", "capital_conquest" })
            {
                var map = GameContent.LoadMap(id);
                Assert.Greater(map.Rails.Count, 0, id + " has a rail line");
            }
            foreach (var id in new[] { "capital", "foundry", "frostpeak", "ironport", "junglepass", "metrocity", "orbitalgate", "redrock", "rustyard",
                         "veyra_old_quarter", "whiteout" })
            {
                var map = GameContent.LoadMap(id + "_siege");
                Assert.AreEqual(ArrivalKind.Rail, map.Fortress.Arrival.Kind, id + "_siege's line in is a rail");
                Assert.IsTrue(map.Rails.Any(r => r.Kind == "siege"), id + "_siege has its fortress line as a RailSpline");
            }
            foreach (var id in new[] { "ironport_conquest", "metrocity_conquest", "capital_conquest", "foundry_conquest", "rustyard_conquest", "ironport_siege" })
            {
                var map = GameContent.LoadMap(id);
                foreach (var r in map.Rails)
                {
                    Assert.Less(r.PlayFrom, r.PlayTo, $"{id} {r.Id}: a stretch in play");
                    Assert.IsTrue(r.GateAtFrom || r.GateAtTo, $"{id} {r.Id}: it runs out of the map through a gate");
                    var outside = r.GateAtFrom ? r.At(0f) : r.At(r.Length);
                    Assert.IsFalse(map.Contains(outside), $"{id} {r.Id}: its portal stands beyond the map");
                    foreach (var c in r.Crossings)
                    {
                        Assert.That(c.S, Is.InRange(r.PlayFrom, r.PlayTo), $"{id} {r.Id} {c.Id} in play");
                        Assert.GreaterOrEqual(RailSystem.WarningFor(c), RailSystem.MinWarning, $"{id} {r.Id} {c.Id} warns at least 4 s");
                    }
                }
            }
        }

        [Test]
        public void TheBossTrainsAreHeldOnTheirLinesAndTheirRoutesLieOnThem()
        {
            var checkedTrains = 0;
            foreach (var m in Campaign.Everything)
            {
                if (m.Boss == null || !Campaign.MapExists(m)) continue;
                var (def, _) = m.Boss.Resolve(Catalog);
                if (Catalog.Vehicle(def).Frame?.Move != BossMove.Rail) continue;
                var world = new SimWorld(Catalog, Campaign.LoadMap(m), 1);
                var train = world.SpawnVehicle(def, 1, m.Boss.Position, m.Boss.Heading);
                Assert.IsTrue(train.OnRail, $"{m.Id}: {def} is on a rail");
                checkedTrains++;
                var line = world.Rails.Lines[train.Rail];
                foreach (var w in m.Boss.Route)
                {
                    var s = line.Project(w, out var lateral);
                    Assert.LessOrEqual(MathF.Abs(lateral), 4.5f, $"{m.Id}: waypoint ({w.X}, {w.Y}) lies on the line (within the mission's 5 m reach)");
                    Assert.That(s, Is.InRange(line.PlayFrom - 0.01f, line.PlayTo + 0.01f), $"{m.Id}: waypoint ({w.X}, {w.Y}) in play");
                }
                if (train.Def.Static || m.Boss.Route.Count == 0) continue;
                world.Submit(new Command(CommandType.Move, 1, new[] { train.Id }, m.Boss.Route[0]));
                Run(world, 60f, _ =>
                {
                    line.Project(train.Position, out var off);
                    Assert.Less(MathF.Abs(off), 0.01f, $"{m.Id}: never off its line");
                });
            }
            Assert.GreaterOrEqual(checkedTrains, 3, "c4m05's and c7m05's Juggernaut, c11m05's Gungnir");
            // c7m10's Nemesis stage on Capital: its route along the avenue lies on the line.
            var capital = GameContent.LoadMap("capital_conquest");
            var nemesis = capital.Rails.Single(r => r.Id == "nemesis");
            foreach (var w in new[] { new Vector2(140f, 0f), new Vector2(100f, 0f), new Vector2(64f, 0f), new Vector2(36f, 0f) })
            {
                nemesis.Project(w, out var lateral);
                Assert.LessOrEqual(MathF.Abs(lateral), 4.5f, $"Nemesis's waypoint ({w.X}, {w.Y}) on its line");
            }
        }

        // ================================================================== replay

        [Test]
        public void TheSameBattleTwiceEndsTheSame()
        {
            (ulong hash, string history) Play()
            {
                var world = Field(9);
                var train = world.SpawnVehicle("armored_train", 1, new Vector2(-50f, 0f), MathF.PI * 0.5f);
                world.SpawnVehicle("main_battle_tank", 0, new Vector2(-20f, 0f), 0f);
                world.SpawnVehicle("ifv", 0, new Vector2(2f, 0f), 0f);
                world.Submit(new Command(CommandType.Move, 1, new[] { train.Id }, new Vector2(80f, 0f)));
                Run(world, 300f);
                var history = string.Join(",", world.Rails.Crossings[0].History.Select(h => $"{h.tick}:{h.state}"));
                return (world.StateHash(), history);
            }
            var a = Play();
            var b = Play();
            Assert.AreEqual(a.history, b.history, "the crossing changed state on the same ticks");
            Assert.AreEqual(a.hash, b.hash, "replay: the same fingerprint");
        }
    }
}
