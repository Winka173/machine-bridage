// Map / visual / audio master spec Part BT (lane, final-A): the headless map stress harness over the engine-free Sim (no
// Unity). Reuses MapStressScenes.All / FocusOf (lane W2-A, Assets/MachineBrigade/Scripts/Sim/Navigation/MapStressScenes.cs)
// to run the five "conquest" scenes as two-side layered-AI Conquest battles (the AI MASTER P5 48v48 harness's own pattern:
// AutoDeploy off, Layered AI, a fixed roster topped up every 5 s) on the shipped map, and records the map metrics spec BT
// asks for: route failures (SevereUnstuck + heavyRouteFailure), spawn block events (TrafficStats.SpawnExitClears), choke
// queue seconds, boss route replans, naval close-approach / reverse events, average LOS engagement distance, lane usage
// share, stale chokes dropped, approach-route usage (maps.topology.telemetryApproaches forced on for this run only) and
// the AI step time (AiPerfCounters, per system). Weather is presentation only (spec Q1): nothing to measure in the Sim.
// The sixth scene ("fortress_siege", mode "siege") needs Game.Match's ModeSessions siege session and Unity play
// (STRESS_SCENES.json's own "harness" field already says so): this tool reports it skipped, not run.
// Usage: dotnet build -c Release Tools/simbuild/mapstress/MapStress.csproj
//        dotnet Temp/mapstress/net8.0/MapStress.dll [scene-id ...] (default: every scene) -> Docs/mapvisaudio/STRESS_MAP_RESULTS.md
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using MachineBrigade.Sim.Navigation;
using Vector2 = System.Numerics.Vector2;

internal static class Program
{
    private const float Step = 0.05f;
    private static string Root = "";

    private static int Main(string[] args)
    {
        CultureInfo.DefaultThreadCurrentCulture = CultureInfo.InvariantCulture;
        CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;
        Root = FindRoot();
        var data = Path.Combine(Root, "Assets", "MachineBrigade", "Resources", "Data");
        SimTunables.Apply(File.ReadAllText(Path.Combine(data, "tunables.json")));
        // This run only (in-memory; tunables.json is not touched): also count approach-route usage, off by default since
        // building the approach sets just to count them costs more than the plain map load gates need (spec H / BT).
        SimTunables.Maps.Topology.TelemetryApproaches = true;
        var catalog = Catalog.FromJson(File.ReadAllText(Path.Combine(data, "balance.json")));
        var ids = new HashSet<string>(args, StringComparer.Ordinal);
        var scenes = MapStressScenes.All.Where(s => ids.Count == 0 || ids.Contains(s.Id)).ToList();

        var sb = new StringBuilder();
        sb.AppendLine("# Map stress results (generated)");
        sb.AppendLine();
        sb.AppendLine("Headless `Tools/simbuild/mapstress` (no Unity) over the spec BT scenes (`MapStressScenes.All`, lane");
        sb.AppendLine("W2-A): the five \"conquest\" scenes run here as two-side layered-AI Conquest battles on the shipped");
        sb.AppendLine("map (`AutoDeploy` off, roster topped up every 5 s, as the AI MASTER P5 48v48 harness does); the sixth,");
        sb.AppendLine("`fortress_siege` (mode \"siege\"), needs `ModeSessions`' siege session and Unity play, reported skipped");
        sb.AppendLine("here. Weather is presentation only (spec Q1): no Sim effect to measure; render/audio metrics and the");
        sb.AppendLine("siege scene are the final part's own Unity-play pass. Never edit by hand: re-run the tool.");
        sb.AppendLine();

        foreach (var scene in scenes)
        {
            if (scene.Mode != "conquest")
            {
                sb.AppendLine($"## {scene.Title} (`{scene.Id}`)");
                sb.AppendLine();
                sb.AppendLine($"Skipped here: mode `{scene.Mode}` needs `ModeSessions` and Unity play (see `STRESS_SCENES.json`'s `harness` field).");
                sb.AppendLine();
                Console.WriteLine($"{scene.Id}: skipped (mode {scene.Mode})");
                continue;
            }
            Console.WriteLine($"{scene.Id}: running ({scene.MapId}, {scene.PerSide}v{scene.PerSide}, {scene.Seconds:0}s)...");
            var t0 = DateTime.UtcNow;
            sb.Append(Run(catalog, data, scene));
            Console.WriteLine($"{scene.Id}: done ({(DateTime.UtcNow - t0).TotalSeconds:0.0} s)");
        }

        var outPath = Path.Combine(Root, "Docs", "mapvisaudio", "STRESS_MAP_RESULTS.md");
        Directory.CreateDirectory(Path.GetDirectoryName(outPath)!);
        File.WriteAllText(outPath, sb.ToString(), new UTF8Encoding(false));
        Console.WriteLine("-> " + outPath);
        return 0;
    }

    private static string FindRoot()
    {
        var d = new DirectoryInfo(AppContext.BaseDirectory);
        while (d != null && !Directory.Exists(Path.Combine(d.FullName, "Assets", "MachineBrigade"))) d = d.Parent;
        return d?.FullName ?? Directory.GetCurrentDirectory();
    }

    /// <summary>The world as a battle starts it, topology-wise: props, the map's fixed defences, wall lines standing (gates open) (same as Tools/maps/topogen's Prepare).</summary>
    private static SimWorld Prepare(Catalog catalog, MapDefinition map, int seed)
    {
        var world = new SimWorld(catalog, map, seed);
        foreach (var u in map.Units)
            if (catalog.Vehicles.TryGetValue(u.DefId, out var def) && def.Static) world.SpawnVehicle(u.DefId, u.Team, u.Position, u.Heading);
        foreach (var line in map.Walls)
            foreach (var s in line.Segments) world.Grid.AddBlocker(s.Center, s.Width, s.Depth, SimWorld.ObstacleClearance);
        _ = world.Lanes;
        _ = world.Topology;
        return world;
    }

    /// <summary>Tops a side up to <paramref name="perSide"/> ground units round its rally (deterministic spots, as AiMasterP5Tests.Fill does).</summary>
    private static void Fill(SimWorld world, int team, int perSide, IReadOnlyList<string> roster)
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

    /// <summary>One <see cref="StressSceneUnit"/>: "sea" starts near the naval route node nearest the scene's focus, spread by <paramref name="k"/>; "rally" near the team's rally point.</summary>
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

    /// <summary>Seeds <paramref name="count"/> wrecks round <paramref name="at"/> (spawns a cheap unit, then kills it: the same path a real combat death takes).</summary>
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

    private static string Share(IReadOnlyDictionary<string, int> samples, int take)
    {
        var total = samples.Values.Sum();
        if (total == 0) return "no samples";
        return string.Join(", ", samples.OrderByDescending(kv => kv.Value).Take(take).Select(kv => $"{kv.Key} {kv.Value * 100.0 / total:0.0}%"));
    }

    private static string Run(Catalog catalog, string data, MapStressScene scene)
    {
        var map = MapDefinition.FromJson(File.ReadAllText(Path.Combine(data, "maps", scene.MapId + ".json")));
        var world = Prepare(catalog, map, scene.Seed);
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
        var steps = new List<double>(Math.Max(0, total - warmup));
        var watch = new Stopwatch();
        var unitSeconds = 0.0;
        int severeAtStart = 0, heavyAtStart = 0, replansAtStart = 0, navalAtStart = 0, spawnClearAtStart = 0;

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
                severeAtStart = world.SevereUnstuckCount;
                heavyAtStart = world.MapTelemetry.HeavyRouteFailures;
                replansAtStart = world.MapTelemetry.BossRouteReplans;
                navalAtStart = world.MapTelemetry.NavalCloseApproachEvents;
                spawnClearAtStart = world.Traffic.Stats.SpawnExitClears;
            }
            watch.Restart();
            mode.Tick(world, Step);
            a.Tick(world, Step);
            b.Tick(world, Step);
            world.Step(Step);
            watch.Stop();
            world.ClearEvents();
            if (i < warmup) continue;
            steps.Add(watch.Elapsed.TotalMilliseconds);
            unitSeconds += world.Vehicles.Count(v => v.IsAlive && !v.Def.Static) * Step;
        }

        var measured = steps.Where(x => x > 0).OrderBy(x => x).ToArray();
        var severe = world.SevereUnstuckCount - severeAtStart;
        var heavy = world.MapTelemetry.HeavyRouteFailures - heavyAtStart;
        var replans = world.MapTelemetry.BossRouteReplans - replansAtStart;
        var navalClose = world.MapTelemetry.NavalCloseApproachEvents - navalAtStart;
        var spawnClear = world.Traffic.Stats.SpawnExitClears - spawnClearAtStart;
        var per10 = unitSeconds > 0 ? severe / (unitSeconds / 600.0) : 0.0;
        var h = world.Health.Counters;
        var endedEarly = mode.Result != null;

        var sb = new StringBuilder();
        sb.AppendLine($"## {scene.Title} (`{scene.Id}`)");
        sb.AppendLine();
        sb.AppendLine($"Map `{scene.MapId}`, {scene.PerSide} v {scene.PerSide} ground units, seed {scene.Seed}, {scene.Seconds:0} s measured after " +
                      $"{scene.WarmupSeconds:0} s warm-up{(endedEarly ? " (match ended early: ticket result)" : "")}. Focus `{scene.Focus}` resolved to " +
                      $"{focusWhat} at ({focusAt.X:0.0},{focusAt.Y:0.0}); extras {scene.Extra.Sum(e => e.Count)}, wrecks seeded {scene.WreckSeed}.");
        sb.AppendLine();
        if (measured.Length > 0)
            sb.AppendLine($"- whole step (AI ticks + world step): mean {measured.Average():0.000} ms, p99 {measured[(int)(measured.Length * 0.99)]:0.000} ms, max {measured[^1]:0.000} ms");
        sb.AppendLine("- AiPerfCounters (per-system, lane W1-A P5 format):");
        foreach (var line in world.AiPerf.Report().Split('\n', StringSplitOptions.RemoveEmptyEntries)) sb.AppendLine("  " + line.Trim());
        sb.AppendLine($"- routeFailures: SevereUnstuck {severe} ({per10:0.00} per 10 unit-minutes), heavyRouteFailure {heavy}");
        sb.AppendLine($"- spawnBlockEvents (TrafficStats.SpawnExitClears): {spawnClear}");
        sb.AppendLine($"- chokeQueueSeconds: {world.MapTelemetry.ChokeQueueSeconds:0.0}");
        sb.AppendLine($"- bossRouteReplanCount: {replans}");
        sb.AppendLine($"- navalCollisionEvents (MapTelemetry.NavalCloseApproachEvents): {navalClose}; naval reverse events (Health.Counters.NavalReverseAttempts): {h.NavalReverseAttempts}");
        sb.AppendLine($"- averageLosEngagementDistance: {world.MapTelemetry.AverageEngagementDistance:0.0} m ({world.MapTelemetry.EngagementSamples} samples)");
        sb.AppendLine($"- laneUsageShare: {Share(world.MapTelemetry.LaneSamples, 5)}");
        sb.AppendLine($"- staleChokesDropped: {g.StaleChokesDropped}");
        sb.AppendLine($"- approach-route usage (maps.topology.telemetryApproaches forced on for this run): {Share(world.MapTelemetry.ApproachSamples, 8)}");
        sb.AppendLine($"- Part K: blocked {h.BlockedUnits} ({h.BlockedRatio:0.00}), deadlocks {h.DeadlockCycles}, anomalies {h.CombatAnomalies}, stalledObjectives {h.StalledObjectiveAssignments}");
        sb.AppendLine();
        return sb.ToString();
    }
}
