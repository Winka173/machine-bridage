using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Bosses;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Navigation;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 33 L4 (DECISIONS "Prompt 33 L4"): the big ships' sea route graph. Every sea map has its graph, checked and the
    /// same as the rule builds from its lanes; the escorts' slots are good and inside the leash; no two big ships overlap
    /// from any start in the data (the missions' sea bosses, every flagship on every lane at both ends of its patrol); two
    /// big ships meeting head-on on a two-way lane both get past (one pulls into a passing bay); the boss's run makes the
    /// others give way; the same battle twice ends in the same fingerprint. Written for the lead to run (the owner's rule:
    /// agents write tests, they do not run them).
    /// </summary>
    public class Prompt33SeaRouteTests
    {
        private const float Dt = 0.05f;
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static readonly string[] SeaMaps = { "lighthousebay_conquest", "lighthousebay_sandbox", "lighthousebay_siege" };

        private static SimWorld Bay(int seed = 1) => new(Catalog, GameContent.LoadMap("lighthousebay_sandbox"), seed);

        private static List<Vehicle> Big(SimWorld world) =>
            world.Vehicles.Where(v => v.IsAlive && !v.Escaped && v.Def.Naval != null && v.Def.Length >= NavalSystem.BigShipLength &&
                                      v.Burrow == Vehicle.BurrowState.Surface).ToList();

        /// <summary>Whether two hulls (oriented rectangles, length along the heading) overlap: the separating axis test.</summary>
        private static bool Overlap(Vehicle a, Vehicle b)
        {
            var axes = new[]
            {
                Sim.Core.SimMath.Forward(a.Heading), Sim.Core.SimMath.Forward(a.Heading + MathF.PI * 0.5f),
                Sim.Core.SimMath.Forward(b.Heading), Sim.Core.SimMath.Forward(b.Heading + MathF.PI * 0.5f),
            };
            foreach (var axis in axes)
            {
                float Reach(Vehicle v)
                {
                    var f = Sim.Core.SimMath.Forward(v.Heading);
                    var r = Sim.Core.SimMath.Forward(v.Heading + MathF.PI * 0.5f);
                    return MathF.Abs(Vector2.Dot(f, axis)) * v.Def.Length * 0.5f + MathF.Abs(Vector2.Dot(r, axis)) * v.Def.Width * 0.5f;
                }
                var gap = MathF.Abs(Vector2.Dot(b.Position - a.Position, axis));
                if (gap >= Reach(a) + Reach(b)) return false;
            }
            return true;
        }

        private static List<string> Overlaps(SimWorld world, string what)
        {
            var bad = new List<string>();
            var big = Big(world);
            for (var i = 0; i < big.Count; i++)
            for (var k = i + 1; k < big.Count; k++)
                if (Overlap(big[i], big[k]))
                    bad.Add($"{what} t={world.Time:0.0}: {big[i].Def.Id}#{big[i].Id.Value} and {big[k].Def.Id}#{big[k].Id.Value} overlap");
            return bad;
        }

        // ================================================================== the graph

        [Test]
        public void EverySeaMapHasItsGraphCheckedAndAsTheRuleBuildsIt()
        {
            foreach (var id in SeaMaps)
            {
                var map = GameContent.LoadMap(id);
                Assert.IsNotNull(map.Sea, id + " has a sea");
                Assert.IsNotNull(map.SeaRoutes, id + ": map data \"seaRoutes\" (Tools/maps/transit.py)");
                var graph = map.SeaRoutes;
                var problems = graph.Validate(map.Sea, map.HalfSize);
                Assert.IsEmpty(problems, id + ":\n" + string.Join("\n", problems));
                var rule = SeaRouteGraph.FromSea(map.Sea, map.HalfSize);
                Assert.AreEqual(rule.Nodes.Count, graph.Nodes.Count, id + ": the same nodes as the rule");
                Assert.AreEqual(rule.Segments.Count, graph.Segments.Count, id + ": the same segments as the rule");
                foreach (var n in rule.Nodes)
                {
                    Assert.IsTrue(graph.TryGet(n.Id, out var m), $"{id}: node {n.Id}");
                    Assert.Less(Vector2.Distance(n.Position, m.Position), 0.05f, $"{id}: node {n.Id} where the rule puts it");
                    Assert.AreEqual(n.Kind, m.Kind, $"{id}: node {n.Id}'s kind");
                }
                Assert.Greater(graph.Nodes.Count(n => n.Kind == SeaNodeKind.Holding), 0, id + " has passing bays");
                Assert.AreEqual(2 * map.Sea.Lanes.Count, graph.Nodes.Count(n => n.Kind == SeaNodeKind.Exit), id + ": every lane runs out of the map at both ends");
            }
        }

        [Test]
        public void TheSandboxCoastBuildsItsGraphFromItsLanes()
        {
            var lanes = new[]
            {
                new SeaLaneDef { Id = "near", W = 40f, Patrol = 70f, End = 115f },
                new SeaLaneDef { Id = "mid", W = 54f, Patrol = 70f, End = 115f },
                new SeaLaneDef { Id = "far", W = 68f, Patrol = 70f, End = 115f },
            };
            var sea = SeaDef.Straight(new Vector2(1f, 0f), 10f, -150f, 150f, lanes, Array.Empty<SeaLandingDef>(), Array.Empty<Vector2>(), new Vector2(0f, -140f));
            var graph = SeaRouteGraph.FromSea(sea, 150f);
            Assert.IsEmpty(graph.Validate(sea, 150f), string.Join("\n", graph.Validate(sea, 150f)));
            Assert.Greater(graph.Segments.Count(s => s.Kind == SeaSegmentKind.Cross), 0, "lanes joined across");
            // Along each lane from one exit to the other.
            foreach (var lane in lanes)
            {
                var first = graph.Segments.First(s => s.Kind == SeaSegmentKind.Track && s.Lane == lane.Id && graph.Nodes[s.A].Kind == SeaNodeKind.Exit);
                var walked = 0;
                for (var s = first.Index; s >= 0; s = graph.NextAlong(s, 1)) walked++;
                Assert.AreEqual(graph.Segments.Count(s => s.Kind == SeaSegmentKind.Track && s.Lane == lane.Id), walked, lane.Id + " end to end");
            }
        }

        // ================================================================== the escorts' slots

        [Test]
        public void EscortSlotsAreGoodSlotsInsideTheLeash()
        {
            var names = new HashSet<string> { "PORT_FORWARD", "STARBOARD_FORWARD", "PORT_REAR", "STARBOARD_REAR" };
            foreach (var bossId in new[] { "leviathan", "typhon" })
            foreach (var extra in new[] { 0, 1 })
            {
                var world = Bay();
                world.SeaRules.ExtraEscorts = extra;
                var sea = world.Map.Sea;
                var boss = world.SpawnVehicle(bossId, 1, sea.At(-20f, sea.Lane(world.Catalog.Vehicle(bossId).Naval.LaneFor(0)).W), 0f);
                world.Step(Dt);
                var escorts = world.Vehicles.Where(v => v.IsAlive && v.Flagship == boss.Id && v.Def.Naval?.Role == NavalRole.Escort).ToList();
                Assert.Greater(escorts.Count, 0, bossId + " sails with escorts");
                Assert.AreEqual(0, world.Naval.SlotProblems, $"{bossId} (+{extra}): every escort found a slot");
                var leash = world.Catalog.EscortRules.Leash;
                foreach (var e in escorts)
                {
                    Assert.IsTrue(e.OnStation, e.Def.Id + " keeps a slot");
                    Assert.LessOrEqual(NavalSystem.HullDistance(boss.Def, e.StationAt), leash + 1e-3f, $"{bossId}: {e.Def.Id}'s slot inside the {leash} m leash");
                    Assert.IsTrue(names.Contains(NavalSystem.SlotName(e.StationAt, boss.NavalDir)), NavalSystem.SlotName(e.StationAt, boss.NavalDir));
                    Assert.GreaterOrEqual(MathF.Abs(e.StationAt.Y), (boss.Def.Width + e.Def.Width) * 0.5f + NavalSystem.LateralMargin, e.Def.Id + " clear of its flagship's side");
                }
                for (var i = 0; i < escorts.Count; i++)
                for (var k = i + 1; k < escorts.Count; k++)
                {
                    var a = escorts[i];
                    var b = escorts[k];
                    var apart = MathF.Abs(a.StationAt.Y - b.StationAt.Y) >= (a.Def.Width + b.Def.Width) * 0.5f + NavalSystem.LateralMargin ||
                                MathF.Abs(a.StationAt.X - b.StationAt.X) >= (a.Def.Length + b.Def.Length) * 0.5f + NavalSystem.GapExtra;
                    Assert.IsTrue(apart, $"{bossId}: {a.Def.Id} and {b.Def.Id}'s slots keep the minimum gap");
                }
            }
        }

        [Test]
        public void ASlotKeepsItsPlaceWhenTheBossComesAbout()
        {
            // Fixed in the coast's frame: port-forward sailing +u is starboard-rear sailing -u.
            var at = new Vector2(22f, -17f);
            Assert.AreEqual("PORT_FORWARD", NavalSystem.SlotName(at, 1));
            Assert.AreEqual("STARBOARD_REAR", NavalSystem.SlotName(at, -1));
            Assert.AreEqual("STARBOARD_FORWARD", NavalSystem.SlotName(new Vector2(22f, 17f), 1));
            Assert.AreEqual("PORT_REAR", NavalSystem.SlotName(new Vector2(-22f, -17f), 1));
        }

        // ================================================================== no overlap, no deadlock, replay

        [Test]
        public void NoBigShipsOverlapFromAnyStartInTheData()
        {
            var bad = new List<string>();
            // The missions' sea bosses where they start.
            foreach (var m in Campaign.Everything)
            {
                if (m.Boss == null || !Campaign.MapExists(m)) continue;
                var (def, _) = m.Boss.Resolve(Catalog);
                if (Catalog.Vehicle(def).Naval == null) continue;
                var map = Campaign.LoadMap(m);
                if (map.Sea == null) continue;
                var world = new SimWorld(Catalog, map, 1);
                world.SpawnVehicle(def, 1, m.Boss.Position, m.Boss.Heading);
                bad.AddRange(Run(world, 60f, m.Id));
            }
            // Every flagship on every lane, at both ends of its patrol and in the middle; with an operation's extra escort.
            foreach (var bossId in new[] { "leviathan", "typhon" })
            {
                if (!Catalog.Vehicles.ContainsKey(bossId)) continue;
                var probe = Bay();
                foreach (var lane in probe.Map.Sea.Lanes)
                foreach (var u in new[] { -lane.Patrol, 0f, lane.Patrol })
                foreach (var extra in bossId == "leviathan" ? new[] { 0, 1 } : new[] { 0 })
                {
                    var world = Bay();
                    world.SeaRules.ExtraEscorts = extra;
                    world.SpawnVehicle(bossId, 1, world.Map.Sea.At(u, lane.W), 0f);
                    bad.AddRange(Run(world, 45f, $"{bossId} {lane.Id} u={u:0} +{extra}"));
                }
            }
            Assert.IsEmpty(bad, string.Join("\n", bad.Take(30)));
        }

        private static IEnumerable<string> Run(SimWorld world, float seconds, string what)
        {
            var bad = new List<string>();
            var ticks = (int)(seconds / Dt);
            for (var t = 0; t < ticks; t++)
            {
                world.Step(Dt);
                world.ClearEvents();
                // After the fleet has spawned (the step after the flagship), every half second.
                if (t > 2 && t % 10 == 0) bad.AddRange(Overlaps(world, what));
                if (bad.Count > 0) break;
            }
            return bad;
        }

        [Test]
        public void TwoBigShipsMeetingHeadOnOnATwoWayLaneBothGetPast()
        {
            var world = Bay(7);
            var sea = world.Map.Sea;
            var near = sea.Lane("near");
            // Two escorts with no flagship patrol the near lane on their own: here sailing at each other.
            var west = world.SpawnVehicle("sea_cruiser", 1, sea.At(-60f, near.W), 0f);
            var east = world.SpawnVehicle("sea_corvette", 1, sea.At(60f, near.W), 0f);
            Assert.AreEqual(1, west.NavalDir);
            Assert.AreEqual(-1, east.NavalDir);
            var bad = new List<string>();
            var passed = false;
            for (var t = 0; t < (int)(150f / Dt) && !passed; t++)
            {
                world.Step(Dt);
                world.ClearEvents();
                if (t % 10 == 0) bad.AddRange(Overlaps(world, "head-on"));
                // Past each other: the one from the west is east of the other.
                passed = sea.Frame(west.Position).X > sea.Frame(east.Position).X + 5f;
            }
            Assert.IsEmpty(bad, string.Join("\n", bad.Take(10)));
            Assert.IsTrue(passed, "no deadlock: they got past each other within 150 s");
            Assert.Greater(world.Naval.Holds, 0, "one of them pulled into a passing bay");
        }

        [Test]
        public void ShipsInTheWayOfTheBossesRunGiveWay()
        {
            var world = Bay(5);
            world.SeaRules.FleetShare = 0f;
            var sea = world.Map.Sea;
            var far = sea.Lane("far");
            var boss = world.SpawnVehicle("leviathan", 1, sea.At(-10f, far.W), 0f);
            world.Step(Dt);
            // A lone escort (no flagship of its own) sitting on the far lane ahead of the run.
            boss.NavalDir = 1;
            var lone = world.SpawnVehicle("sea_corvette", 1, sea.At(70f, far.W), 0f);
            boss.Escaping = true;
            var held = false;
            var bad = new List<string>();
            for (var t = 0; t < (int)(40f / Dt); t++)
            {
                world.Step(Dt);
                world.ClearEvents();
                held |= lone.SeaHolding;
                if (t % 10 == 0) bad.AddRange(Overlaps(world, "the run"));
            }
            Assert.IsTrue(held, "the corvette pulled into a holding node out of the boss's way");
            Assert.IsEmpty(bad, string.Join("\n", bad.Take(10)));
        }

        [Test]
        public void TheSameBattleTwiceEndsTheSame()
        {
            ulong Play()
            {
                var world = Bay(11);
                world.SeaRules.ExtraEscorts = 1;
                var sea = world.Map.Sea;
                world.SpawnVehicle("leviathan", 1, sea.At(60f, sea.Lane("far").W), 0f);
                var near = sea.Lane("near");
                world.SpawnVehicle("sea_cruiser", 1, sea.At(-70f, near.W), 0f);
                world.SpawnVehicle("sea_corvette", 1, sea.At(40f, near.W), 0f);
                for (var t = 0; t < (int)(90f / Dt); t++)
                {
                    world.Step(Dt);
                    world.ClearEvents();
                }
                return world.StateHash();
            }
            Assert.AreEqual(Play(), Play(), "replay: the same ships in the same places");
        }
    }
}
