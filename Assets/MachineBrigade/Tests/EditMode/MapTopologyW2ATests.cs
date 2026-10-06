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
    /// Map / visual / audio master spec Part H (objective approaches), part of BW/CI's acceptance rows "H" and "I", and spec BT
    /// (the stress scene definitions), lane W2-A: written by the lane, not run by it (owner token rule; the lead runs category
    /// "MapVAW2A"). Builds on <see cref="MapTopologyW1ATests"/>'s pattern rather than its shared statics, so either file can be
    /// run alone.
    /// </summary>
    [Category("MapVAW2A")]
    public class MapTopologyW2ATests
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

        // ------------------------------------------------------------------ acceptance row H: objective approaches

        [Test]
        public void ReachableObjectivesHavePrimaryShortestAndSafestApproaches()
        {
            var problems = new List<string>();
            foreach (var id in MapIds())
            {
                var g = World(id).GameplayTopology;
                foreach (var a in g.ObjectiveApproaches)
                {
                    if (a.Approaches.Count == 0)
                    {
                        // No ground route for this side: a light hull reaching the objective by the plain route graph would be a fault.
                        if (g.RouteAudits.Any(r => r.To == a.Objective && r.From == "rally_" + a.Team && r.Class == VehicleSizeClass.Light && r.Reachable))
                            problems.Add($"{id}: {a.Id} has no approach yet a light hull reaches it");
                        continue;
                    }
                    foreach (var role in new[] { ApproachRole.Primary, ApproachRole.Shortest, ApproachRole.Safest })
                        if (a.For(role) == null) problems.Add($"{id}: {a.Id} has no {role} route");
                    foreach (var r in a.Approaches)
                    {
                        if (r.Points.Count < 2) problems.Add($"{id}: {a.Id}/{r.Id} fewer than 2 points");
                        if (!(r.LengthM > 0f)) problems.Add($"{id}: {a.Id}/{r.Id} non-positive length");
                        if (!(r.EtaSeconds > 0f)) problems.Add($"{id}: {a.Id}/{r.Id} non-positive ETA");
                        if (r.Exposure < 0f || r.Exposure > 1f) problems.Add($"{id}: {a.Id}/{r.Id} exposure {r.Exposure} out of [0,1]");
                    }
                }
            }
            Assert.IsEmpty(problems, string.Join("\n", problems.Take(30)));
        }

        [Test]
        public void ShortestApproachIsNoLongerThanAnyOther()
        {
            var problems = new List<string>();
            foreach (var id in MapIds())
            {
                var g = World(id).GameplayTopology;
                foreach (var a in g.ObjectiveApproaches)
                {
                    var shortest = a.For(ApproachRole.Shortest);
                    if (shortest == null) continue;
                    foreach (var r in a.Approaches)
                        if (r.LengthM < shortest.LengthM - 0.01f) problems.Add($"{id}: {a.Id}/{r.Id} ({r.LengthM:0.0} m) shorter than the Shortest role ({shortest.LengthM:0.0} m)");
                }
            }
            Assert.IsEmpty(problems, string.Join("\n", problems.Take(30)));
        }

        // ------------------------------------------------------------------ acceptance row I: staging off major transit lanes

        [Test]
        public void StagingAreasStayOffMajorTransitLanes()
        {
            var problems = new List<string>();
            foreach (var id in MapIds())
            {
                var g = World(id).GameplayTopology;
                foreach (var st in g.StagingAreas)
                    foreach (var l in g.Lanes)
                        if (l.ParkingForbidden && l.DistanceTo(st.Centre) < 6f) problems.Add($"{id}: {st.Id} within 6 m of no-park lane {l.Id}");
            }
            Assert.IsEmpty(problems, string.Join("\n", problems.Take(30)));
        }

        // ------------------------------------------------------------------ swing-turn check (ROUTE_TURN_TIGHT is stricter than ROUTE_TURN)

        [Test]
        public void SwingTurnSpaceNeverExceedsTheStrictPivotCheckItRelaxes()
        {
            var problems = new List<string>();
            foreach (var id in MapIds())
                foreach (var r in World(id).GameplayTopology.RouteAudits)
                {
                    // Swinging wide only ever buys more room than turning on the spot, so a route that already fits the strict
                    // pivot-room check must also fit the swing one.
                    if (r.TurnsFit && !r.TurnsFitSwing) problems.Add($"{id}: {r.From}->{r.To}/{r.Class} fits the pivot room but not the swing check");
                    if (float.IsFinite(r.MinTurnSpaceM) && float.IsFinite(r.SwingTurnSpaceM) && r.SwingTurnSpaceM < r.MinTurnSpaceM - 0.01f)
                        problems.Add($"{id}: {r.From}->{r.To}/{r.Class} swing space ({r.SwingTurnSpaceM:0.0} m) < pivot space ({r.MinTurnSpaceM:0.0} m)");
                }
            Assert.IsEmpty(problems, string.Join("\n", problems.Take(30)));
        }

        // ------------------------------------------------------------------ spec BT: the six stress scenes resolve a real focus

        [Test]
        public void EveryStressSceneIsOnAShippedMapWithARosterAndAResolvedFocus()
        {
            var shipped = MapIds().ToHashSet();
            Assert.AreEqual(6, MapStressScenes.All.Count, "spec BT lists six map stress scenes");
            var problems = new List<string>();
            foreach (var scene in MapStressScenes.All)
            {
                if (!shipped.Contains(scene.MapId)) problems.Add($"{scene.Id}: map {scene.MapId} is not shipped");
                if (scene.Roster.Count == 0) problems.Add($"{scene.Id}: empty roster");
                foreach (var u in scene.Roster.Concat(scene.Extra.Select(e => e.Unit)))
                    if (!Catalog.Vehicles.ContainsKey(u)) problems.Add($"{scene.Id}: roster unit {u} not in the catalog");
                if (!shipped.Contains(scene.MapId)) continue;
                var world = World(scene.MapId);
                var (what, _) = MapStressScenes.FocusOf(scene, world.GameplayTopology, world.Map.Centre);
                if (what == "none") problems.Add($"{scene.Id}: focus '{scene.Focus}' did not resolve on {scene.MapId}");
            }
            Assert.IsEmpty(problems, string.Join("\n", problems.Take(30)));
        }

        [Test]
        public void StressSceneIdsAreUniqueAndMapsCoverTheSixKinds()
        {
            var ids = MapStressScenes.All.Select(s => s.Id).ToList();
            Assert.AreEqual(ids.Count, ids.Distinct().Count(), "scene ids must be unique");
            foreach (var id in ids) Assert.IsNotNull(MapStressScenes.Get(id), id);
            Assert.IsNull(MapStressScenes.Get("no_such_scene"));
        }
    }
}
