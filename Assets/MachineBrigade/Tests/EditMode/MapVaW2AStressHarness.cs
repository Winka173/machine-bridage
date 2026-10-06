using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using MachineBrigade.Sim.Navigation;
using Debug = UnityEngine.Debug;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Map / visual / audio master spec Part BT (lane, final-A): the Unity-side twin of the headless
    /// <c>Tools/simbuild/mapstress</c> harness, for a lead who wants the same reading from inside the editor (or wants it
    /// next to a Unity profiler capture). Reuses <see cref="MapStressScenes"/> (lane W2-A) exactly as the headless tool does;
    /// see its report for a run already taken (Docs/mapvisaudio/STRESS_MAP_RESULTS.md) and for which metric means what.
    /// Explicit: run it on purpose (Test Runner, category "MapVaW2AStress"); this lane writes it, not run by it (owner
    /// token rule). The "fortress_siege" scene (mode "siege") needs <c>ModeSessions</c>' siege session, not this harness's
    /// bare <see cref="ConquestMode"/> battle: its test case is marked ignored here.
    /// </summary>
    [Category("MapVaW2AStress")]
    public class MapVaW2AStressHarness
    {
        private const float Step = 0.05f;

        [TestCase("urban_choke_48v48"), TestCase("open_desert_48v48"), TestCase("naval_boss_escorts"), TestCase("weather_storm"),
         TestCase("wreck_density"), Explicit("map stress harness: the lead runs it"), Timeout(3600000)]
        public void Scene_ReportsMapMetrics(string sceneId)
        {
            var scene = MapStressScenes.Get(sceneId);
            Assert.NotNull(scene, sceneId);
            Assert.AreEqual("conquest", scene.Mode, "the siege scene needs ModeSessions, not this harness");
            var report = Measure(scene);
            Debug.Log(report);
            TestContext.WriteLine(report);
            try
            {
                Directory.CreateDirectory("Temp");
                File.WriteAllText(Path.Combine("Temp", $"map_stress_{sceneId}.txt"), report);
            }
            catch (IOException)
            {
                // The report is in the log anyway.
            }
        }

        [Test, Explicit("the siege scene needs Unity play (ModeSessions siege session), not this harness")]
        public void FortressSiege_NeedsModeSessions() => Assert.Ignore("mode \"siege\": run it through ModeSessions in Unity play, not this harness");

        internal static string Measure(MapStressScene scene)
        {
            var catalog = GameContent.LoadCatalog();
            var map = GameContent.LoadMap(scene.MapId);
            var world = new SimWorld(catalog, map, scene.Seed);
            foreach (var u in map.Units)
                if (catalog.Vehicles.TryGetValue(u.DefId, out var def) && def.Static) world.SpawnVehicle(u.DefId, u.Team, u.Position, u.Heading);
            foreach (var line in map.Walls)
                foreach (var s in line.Segments) world.Grid.AddBlocker(s.Center, s.Width, s.Depth, SimWorld.ObstacleClearance);
            _ = world.Lanes;
            _ = world.Topology;
            SimTunables.Maps.Topology.TelemetryApproaches = true; // this run only (reset after by the test runner's TearDown convention elsewhere).
            var g = world.GameplayTopology;
            var (focusWhat, focusAt) = MapStressScenes.FocusOf(scene, g, map.Centre);

            var mode = new ConquestMode(new ConquestRules
            {
                PlayerVehicles = catalog.Vehicles.Keys.ToList(), PlayerSupports = catalog.Supports.Keys.ToList(),
                EnemyVehicles = catalog.Vehicles.Keys.ToList(), EnemySupports = catalog.Supports.Keys.ToList(),
            });
            mode.Setup(world);
            world.Intel.Objectives = mode;
            var a = new ConquestAi(mode, 0, 1, AiDifficulty.Normal, scene.Seed + 1) { AutoDeploy = false, Layered = true };
            var b = new ConquestAi(mode, 1, 0, AiDifficulty.Normal, scene.Seed + 2) { AutoDeploy = false, Layered = true };
            Fill(world, 0, scene.PerSide, scene.Roster);
            Fill(world, 1, scene.PerSide, scene.Roster);
            int k0 = 0, k1 = 0;
            foreach (var u in scene.Extra)
                for (var j = 0; j < u.Count; j++)
                    SpawnExtra(world, g, u, focusAt, u.Team == 0 ? k0++ : k1++);
            if (scene.WreckSeed > 0) SeedWrecks(world, scene.WreckSeed, focusAt, scene.Roster[0], scene.Seed);

            var warmup = (int)(scene.WarmupSeconds / Step);
            var total = warmup + (int)(scene.Seconds / Step);
            var watch = new Stopwatch();
            var steps = new double[Math.Max(0, total - warmup)];
            for (var i = 0; i < total && mode.Result == null; i++)
            {
                if (i % 100 == 0)
                {
                    Fill(world, 0, scene.PerSide, scene.Roster);
                    Fill(world, 1, scene.PerSide, scene.Roster);
                }
                if (i == warmup)
                {
                    world.AiPerf.Reset();
                    world.AiPerf.Enabled = true;
                }
                watch.Restart();
                mode.Tick(world, Step);
                a.Tick(world, Step);
                b.Tick(world, Step);
                world.Step(Step);
                watch.Stop();
                world.ClearEvents();
                if (i >= warmup) steps[i - warmup] = watch.Elapsed.TotalMilliseconds;
            }

            var measured = steps.Where(x => x > 0).OrderBy(x => x).ToArray();
            var h = world.Health.Counters;
            var sb = new StringBuilder();
            sb.Append($"{scene.Title} ({scene.Id}): map {scene.MapId}, {scene.PerSide}v{scene.PerSide}, seed {scene.Seed}, {scene.Seconds:0} s after {scene.WarmupSeconds:0} s warm-up\n");
            if (measured.Length > 0)
                sb.Append($"whole step: mean {measured.Average():0.000} ms, p99 {measured[(int)(measured.Length * 0.99)]:0.000} ms, max {measured[^1]:0.000} ms\n");
            sb.Append(world.AiPerf.Report());
            sb.Append($"SevereUnstuck {world.SevereUnstuckCount}, heavyRouteFailure {world.MapTelemetry.HeavyRouteFailures}, " +
                      $"bossRouteReplans {world.MapTelemetry.BossRouteReplans}, navalCloseApproach {world.MapTelemetry.NavalCloseApproachEvents}, " +
                      $"navalReverseAttempts {h.NavalReverseAttempts}, chokeQueueSeconds {world.MapTelemetry.ChokeQueueSeconds:0.0}, " +
                      $"staleChokesDropped {g.StaleChokesDropped}, avgEngageDist {world.MapTelemetry.AverageEngagementDistance:0.0} m\n");
            return sb.ToString();
        }

        private static void Fill(SimWorld world, int team, int perSide, System.Collections.Generic.IReadOnlyList<string> roster)
        {
            world.TryGetRally(team, out var at);
            var alive = world.Vehicles.Count(v => v.IsAlive && v.Team == team && !v.Def.Static);
            for (var i = alive; i < perSide; i++)
            {
                var angle = i * 2.39996f;
                var p = world.Map.Clamp(at + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * (5f + i % 7 * 2.5f), 1f);
                world.SpawnVehicle(roster[i % roster.Count], team, p, 0f);
            }
        }

        private static void SpawnExtra(SimWorld world, GameplayTopology g, StressSceneUnit u, Vector2 focusAt, int k)
        {
            Vector2 at;
            if (u.At == "sea")
            {
                NavalNodeInfo best = null;
                foreach (var n in g.NavalNodes)
                    if (n.Kind != SeaNodeKind.Exit && (best == null || Vector2.Distance(n.Position, focusAt) < Vector2.Distance(best.Position, focusAt))) best = n;
                at = best?.Position ?? focusAt;
                at += new Vector2(MathF.Cos(k * 1.7f), MathF.Sin(k * 1.7f)) * (10f + k * 6f);
            }
            else
            {
                world.TryGetRally(u.Team, out at);
                at = world.Map.Clamp(at + new Vector2(MathF.Cos(k * 1.7f), MathF.Sin(k * 1.7f)) * (8f + k * 4f), 1f);
            }
            world.SpawnVehicle(u.Unit, u.Team, at, 0f);
        }

        private static void SeedWrecks(SimWorld world, int count, Vector2 at, string unitId, int seed)
        {
            for (var i = 0; i < count; i++)
            {
                var angle = seed * 0.3f + i * 0.9f;
                var r = 4f + i % 9 * 3f;
                var p = at + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * r;
                if (!world.Grid.TryNearestWalkable(p, 8, out var walkable)) walkable = p;
                var v = world.SpawnVehicle(unitId, i % 2, walkable, 0f);
                world.DebugDamage(v, 50f);
            }
        }
    }
}
