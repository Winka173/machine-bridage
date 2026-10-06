using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Navigation;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Map / visual / audio master spec Part CI, the map acceptance rows (lane W1-A): written by the lane, not run by it (owner
    /// token rule; the lead runs category "MapVAW1A"). Each shipped map's world is built as Tools/maps/topogen builds it (props,
    /// the map's fixed defences, the wall lines standing) and never stepped.
    /// </summary>
    [Category("MapVAW1A")]
    public class MapTopologyW1ATests
    {
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static IEnumerable<string> MapIds() =>
            Directory.GetFiles(Path.Combine(Application.dataPath, "MachineBrigade", "Resources", "Data", "maps"), "*.json")
                .Select(Path.GetFileNameWithoutExtension).OrderBy(s => s, StringComparer.Ordinal);

        private static readonly Dictionary<string, SimWorld> Worlds = new();

        private static SimWorld World(string id)
        {
            if (Worlds.TryGetValue(id, out var cached)) return cached;
            var map = GameContent.LoadMap(id);
            var world = new SimWorld(Catalog, map, 1);
            foreach (var u in map.Units)
                if (Catalog.Vehicles.TryGetValue(u.DefId, out var def) && def.Static) world.SpawnVehicle(u.DefId, u.Team, u.Position, u.Heading);
            foreach (var line in map.Walls)
                foreach (var s in line.Segments) world.Grid.AddBlocker(s.Center, s.Width, s.Depth, SimWorld.ObstacleClearance);
            _ = world.Lanes;
            _ = world.Topology;
            Worlds[id] = world;
            return world;
        }

        private static string Registry => Path.GetFullPath(Path.Combine(Application.dataPath, "..", "Docs", "maps", "MapWarningRegistry.json"));

        private static List<Dictionary<string, object>> Warnings()
        {
            var root = (Dictionary<string, object>)MiniJson.Parse(File.ReadAllText(Registry));
            return ((List<object>)root["warnings"]).Cast<Dictionary<string, object>>().ToList();
        }

        // ------------------------------------------------------------------ CI map row 1

        [Test]
        public void EveryObjectiveAndSpawnResolvesToATopologyComponent()
        {
            var problems = new List<string>();
            foreach (var id in MapIds())
            {
                var g = World(id).GameplayTopology;
                foreach (var a in g.Anchors)
                    if ((a.Kind is AnchorKind.Spawn or AnchorKind.MissionSpawn or AnchorKind.EntryGate or AnchorKind.Objective or AnchorKind.Base
                            or AnchorKind.Fortress or AnchorKind.Battery or AnchorKind.NavalLane or AnchorKind.NavalNode or AnchorKind.BossRoute) && !a.Resolved)
                        problems.Add($"{id}: {a}");
            }
            Assert.IsEmpty(problems, string.Join("\n", problems.Take(30)));
        }

        // ------------------------------------------------------------------ CI map row 2

        [Test]
        public void EveryHeavyAndBossRouteIsValidatedBySize()
        {
            var problems = new List<string>();
            foreach (var id in MapIds())
            {
                var g = World(id).GameplayTopology;
                var pairs = g.RouteAudits.GroupBy(r => (r.From, r.To));
                foreach (var pair in pairs)
                {
                    var classes = pair.Select(r => r.Class).Distinct().Count();
                    if (classes != 5) problems.Add($"{id} {pair.Key}: {classes} of 5 size classes audited");
                    foreach (var r in pair)
                    {
                        if (r.Class <= VehicleSizeClass.Medium && !r.Reachable) problems.Add($"{id} {pair.Key}: {r.Class} cannot reach");
                        if (r.Reachable && !(r.MinClearWidthM > 0f)) problems.Add($"{id} {pair.Key}: {r.Class} has no clear width");
                    }
                }
            }
            Assert.IsEmpty(problems, string.Join("\n", problems.Take(30)));
        }

        [Test]
        public void SizeClassesNeedMoreClearanceAsTheyGrow()
        {
            var g = World("ashfield_conquest").GameplayTopology;
            for (var k = 1; k < 5; k++)
                Assert.GreaterOrEqual(g.Classes[k].ClearanceCells, g.Classes[k - 1].ClearanceCells, g.Classes[k].Class.ToString());
            Assert.AreEqual(VehicleSizeClass.Boss, GameplayTopology.ClassOf(Catalog.Vehicle("behemoth")));
            Assert.AreEqual(VehicleSizeClass.SuperHeavy, GameplayTopology.ClassOf(Catalog.Vehicle("titan_tank")));
        }

        // ------------------------------------------------------------------ CI map row 3

        [Test]
        public void EveryBossNavalRoutePassesTheCurvatureAudit()
        {
            var problems = new List<string>();
            foreach (var id in MapIds())
            {
                var g = World(id).GameplayTopology;
                foreach (var t in g.NavalTurnAudits)
                {
                    Assert.AreEqual(t.Speed / (t.TurnRateDeg * MathF.PI / 180f), t.Rmin, 0.01f, $"{id} {t.Ship}: Rmin = speed / angular speed");
                    Assert.AreEqual(t.Rmin * SimTunables.Maps.Topology.NavalSafety, t.Required, 0.01f);
                    if (t.Boss && !t.Pass && !t.Mitigated) problems.Add($"{id}: {t.Ship} {t.Manoeuvre} at {t.Where} {t.Available:0.0} < {t.Required:0.0} m");
                }
            }
            Assert.IsEmpty(problems, string.Join("\n", problems.Take(30)));
            Assert.That(SimTunables.Maps.Topology.NavalSafety, Is.InRange(1.10f, 1.25f), "spec M safety factor");
        }

        // ------------------------------------------------------------------ CI map row 4

        [Test]
        public void EveryCriticalChokeHasWidthAndCapacity()
        {
            var problems = new List<string>();
            foreach (var id in MapIds())
                foreach (var c in World(id).GameplayTopology.Chokes)
                {
                    if (!(c.UsableWidthM > 0f) || !(c.EstimatedThroughput > 0f) || c.MaxLightSideBySide < 0) problems.Add($"{id}: {c}");
                    if (c.Critical && c.MaxLightSideBySide < 1) problems.Add($"{id}: critical {c} fits no light hull");
                    if (c.MaxLightSideBySide < c.MaxMediumSideBySide || c.MaxMediumSideBySide < c.MaxHeavySideBySide) problems.Add($"{id}: {c} capacity order");
                }
            Assert.IsEmpty(problems, string.Join("\n", problems.Take(30)));
        }

        // ------------------------------------------------------------------ CI map row 5

        [Test]
        public void NoNormalSpawnHasUnexplainedFullExitDirectFire()
        {
            var open = Warnings().Where(w => (string)w["code"] == "SPAWN_FULL_EXIT_DIRECT_FIRE" && (string)w["status"] == "OPEN").Select(w => (string)w["warningId"]).ToList();
            Assert.IsEmpty(open, string.Join("\n", open));
        }

        // ------------------------------------------------------------------ CI map row 6

        /// <summary>A 400 m square with the waterline at x = 0 (sea to the east) and one lane <paramref name="laneW"/> m out.</summary>
        private static MapDefinition Coast(float laneW)
        {
            const float half = 200f;
            var teams = new[] { new TeamStart(0, new Vector2(-150f, 0f)), new TeamStart(1, new Vector2(-150f, 100f)) };
            var lanes = new List<SeaLaneDef> { new() { Id = "far", W = laneW, Patrol = 120f, End = half - 4f } };
            var sea = SeaDef.Straight(new Vector2(0f, 1f), 0f, -half, half, lanes, new List<SeaLandingDef>(), Array.Empty<Vector2>(), new Vector2(half - 6f, 0f));
            return new MapDefinition("w1a_coast", half * 2f, teams, Array.Empty<PropPlacement>(), Array.Empty<UnitPlacement>()) { Sea = sea };
        }

        [Test]
        public void ShoreFireRegionsTellCannotEnterFromCannotInfluence()
        {
            var world = new SimWorld(Catalog, Coast(30f), 3);
            var g = world.GameplayTopology;
            Assert.IsNotEmpty(g.ShoreFireRegions, "a coast has shore fire regions");
            var land = g.Ground.ComponentAt(new Vector2(-10f, 0f));
            Assert.Greater(land, 0);
            Assert.AreEqual(0, g.Ground.ComponentAt(new Vector2(30f, 0f)), "a ground unit cannot enter the water");
            var reach = g.ShoreReach(land, "far");
            Assert.LessOrEqual(reach, 32f, "the lane is ~30 m from reachable shore");
            var tank = Catalog.Vehicle("main_battle_tank");
            Assert.LessOrEqual(reach, MachineBrigade.Sim.AI.WeaponEnvelope.Of(tank, MachineBrigade.Sim.AI.TargetLayer.Naval).MaxRange + 2f,
                "...yet a tank can influence a ship on it from the shore");
            foreach (var r in g.ShoreFireRegions)
            {
                Assert.LessOrEqual(r.MinDistanceToNavalLane, r.MaxDistanceToNavalLane);
                Assert.That(r.LosQuality, Is.InRange(0f, 1f));
            }
        }

        [Test]
        public void LaneStretchSamplesTheNearestLaneAsFeasibilityDid()
        {
            var sea = Coast(30f).Sea;
            var stretch = GameplayTopology.LaneStretch(sea, new Vector2(30f, 10f), 5f, 9);
            Assert.IsNotNull(stretch);
            Assert.AreEqual(10, stretch.Length);
            for (var k = 0; k < 9; k++)
            {
                var expected = sea.At(-120f + 240f * k / 8f, 30f);
                Assert.AreEqual(expected.X, stretch[k].X, 1e-3f);
                Assert.AreEqual(expected.Y, stretch[k].Y, 1e-3f);
            }
            Assert.IsNull(GameplayTopology.LaneStretch(sea, new Vector2(80f, 0f), 5f, 9), "no lane within radius + 12 m");
        }

        // ------------------------------------------------------------------ CI map row 7

        [Test]
        public void EveryMapWarningHasStateOwnerAndReason()
        {
            var statuses = new HashSet<string> { "OPEN", "FIXED", "ACCEPTED_INTENTIONAL", "PLAYTEST_REQUIRED" };
            var problems = new List<string>();
            foreach (var w in Warnings())
            {
                var id = (string)w["warningId"];
                if (!statuses.Contains((string)w["status"])) problems.Add($"{id}: status {w["status"]}");
                foreach (var key in new[] { "owner", "acceptedReason", "lastReviewedVersion", "metric", "severity" })
                    if (!w.TryGetValue(key, out var v) || string.IsNullOrWhiteSpace(v as string)) problems.Add($"{id}: no {key}");
            }
            Assert.IsEmpty(problems, string.Join("\n", problems.Take(30)));
        }

        // ------------------------------------------------------------------ spec BW, CI cross-system "no duplicate geometry inference"

        [Test]
        public void EveryShippedMapPassesTheLoadGates()
        {
            var problems = new List<string>();
            foreach (var id in MapIds())
                foreach (var gate in World(id).GameplayTopology.RunLoadGates(true))
                    if (!gate.Pass) problems.Add($"{id}: {gate}");
            Assert.IsEmpty(problems, string.Join("\n", problems.Take(30)));
        }

        [Test]
        public void TrafficPassagesAreTheTopologyChokes()
        {
            foreach (var id in new[] { "ashfield_conquest", "metrocity_conquest", "lighthousebay_conquest", "whiteout_siege" })
            {
                var world = World(id);
                var passages = world.Traffic.Passages;
                var chokes = world.GameplayTopology.Chokes;
                Assert.AreEqual(chokes.Count, passages.Count, id);
                for (var i = 0; i < chokes.Count; i++)
                {
                    Assert.AreEqual(chokes[i].Centre, passages[i].Centre, $"{id} passage {i + 1}");
                    Assert.AreEqual(chokes[i].OpenWidth, passages[i].Width, $"{id} passage {i + 1}");
                    Assert.AreEqual(chokes[i].Length, passages[i].Length, $"{id} passage {i + 1}");
                }
            }
        }

        [Test]
        public void FireSupportParkingRuleIsTheLaneMapRule()
        {
            var world = World("ashfield_conquest");
            var g = world.GameplayTopology;
            for (var y = -140f; y <= 140f; y += 7f)
            for (var x = -140f; x <= 140f; x += 7f)
            {
                var p = new Vector2(x, y);
                Assert.AreEqual(world.Grid.IsWalkable(p) && !world.Lanes.NoParkAt(p), g.ParkingAllowed(p), $"({x},{y})");
                var flags = world.Lanes.At(p);
                var expected = (flags & LaneFlags.Route) != 0 ? 1f : (flags & LaneFlags.Road) != 0 ? 0.5f : 0f;
                Assert.AreEqual(expected, g.TransitConflict(p), $"({x},{y})");
            }
        }

        [Test]
        public void TerrainSemanticsAndWeatherPresentationAreMetadataOnly()
        {
            foreach (TerrainTag tag in Enum.GetValues(typeof(TerrainTag)))
            {
                var s = GameplayTopology.SemanticsOf(tag);
                Assert.AreEqual(TerrainRules.PathCost(tag), s.MovementCost, tag.ToString());
                Assert.AreEqual(0f, s.DirectFireCover, "no terrain combat cover");
                Assert.AreEqual(0f, s.HullDownPotential, "flat ground");
            }
            foreach (var k in WeatherPresentation.Kinds)
                Assert.GreaterOrEqual(WeatherPresentation.Of(k).TelegraphBoost, 1f, k + ": telegraphs never fade (spec Q1)");
        }

        [Test]
        public void GeneratedPositionsAreInsideThePlayableGround()
        {
            var problems = new List<string>();
            foreach (var id in MapIds())
            {
                var world = World(id);
                var g = world.GameplayTopology;
                foreach (var p in g.Positions)
                    if (!world.Map.InsideBoundary(p.Position) || !world.Grid.IsWalkable(p.Position)) problems.Add($"{id}: {p.Id}");
                foreach (var s in g.StagingAreas)
                    if (g.InSpawnClearZone(s.Centre) || world.Lanes.NoParkAt(s.Centre)) problems.Add($"{id}: {s.Id}");
                foreach (var p in g.Positions.Where(p => p.Kind == TacticalPositionKind.HullDown))
                    Assert.AreEqual(1f, p.Terms["masked"], "hull-down only behind real low cover");
            }
            Assert.IsEmpty(problems, string.Join("\n", problems.Take(30)));
        }
    }
}
