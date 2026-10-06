// Map / visual / audio master spec Part V (lane W1-A): writes the generated (never hand-authored) map topology outputs from
// the shipped data through the game's own GameplayTopology (one implementation: the runtime's), into Docs/maps:
//   GameplayTopology.json, MapConnectivity.json, TacticalPositions.json, NavalRouteAudit.json, SpawnFairnessAudit.json,
//   MapWarningRegistry.json (+ GAMEPLAY_TOPOLOGY.md, a summary); lane W2-A adds ObjectiveApproaches.json (spec H),
//   MapAcceptance.json (spec CI map rows per map, the CJ map_topology / naval_route / spawn_fairness / tactical_position
//   validators in one pass) and STRESS_SCENES.json (spec BT scene definitions with their focus resolved on the topology).
//   --check: exit 1 when an acceptance row fails (prints the failures; writes nothing with a map prefix).
// Each map's world is built as a battle starts it (props, the map's fixed defences, wall lines standing with their gates open)
// and never stepped: nothing is simulated. Canonical map JSON stays the authority; statuses / owners / reasons of warnings
// come from Docs/maps/map_warning_reviews.json (hand-authored), the static audit's flags from Docs/checks/map_audit.csv.
//   dotnet build -c Release Tools/maps/topogen/TopoGen.csproj && dotnet Temp/topogen/TopoGen.dll [--check] [map-prefix ...]
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Numerics;
using System.Text;
using System.Text.Json;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Navigation;

internal static class Program
{
    private static string Root = "";

    private static int Main(string[] args)
    {
        CultureInfo.DefaultThreadCurrentCulture = CultureInfo.InvariantCulture;
        CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;
        Root = FindRoot();
        var data = Path.Combine(Root, "Assets", "MachineBrigade", "Resources", "Data");
        SimTunables.Apply(File.ReadAllText(Path.Combine(data, "tunables.json")));
        var catalog = Catalog.FromJson(File.ReadAllText(Path.Combine(data, "balance.json")));
        var files = Directory.GetFiles(Path.Combine(data, "maps"), "*.json").OrderBy(f => f, StringComparer.Ordinal).ToList();
        var check = args.Contains("--check");
        args = args.Where(a => !a.StartsWith("--", StringComparison.Ordinal)).ToArray();
        if (args.Length > 0) files = files.Where(f => args.Any(a => Path.GetFileName(f).StartsWith(a, StringComparison.Ordinal))).ToList();
        var outDir = Path.Combine(Root, "Docs", "maps");
        Directory.CreateDirectory(outDir);

        var topo = new List<(string id, string json)>();
        var conn = new List<(string id, string json)>();
        var pos = new List<(string id, string json)>();
        var naval = new List<(string id, string json)>();
        var fair = new List<(string id, string json)>();
        var warnings = new List<Dictionary<string, object?>>();
        var appr = new List<(string id, string json)>();
        var accept = new List<(string id, string json)>();
        var failures = new List<string>();
        var stress = new Dictionary<string, string>(StringComparer.Ordinal);
        var summary = new List<string[]>();
        var auditFlags = AuditFlags();
        var reviews = Reviews.Load(Path.Combine(outDir, "map_warning_reviews.json"));
        foreach (var file in files)
        {
            var map = MapDefinition.FromJson(File.ReadAllText(file));
            var world = Prepare(catalog, map);
            var g = world.GameplayTopology;
            var t0 = DateTime.UtcNow;
            topo.Add((map.Id, Topology(world, g)));
            conn.Add((map.Id, Connectivity(g)));
            pos.Add((map.Id, Positions(g)));
            if (map.Sea != null) naval.Add((map.Id, Naval(g)));
            fair.Add((map.Id, Fairness(g)));
            appr.Add((map.Id, Approaches(g)));
            var asym = Asymmetry(file);
            var firstWarning = warnings.Count;
            foreach (var w in g.Warnings) warnings.Add(reviews.Apply(w.WarningId, w.Severity.ToString().ToUpperInvariant(), w.Code, w.Metric, w.Value, w.Threshold, "GameplayTopology", asym));
            if (auditFlags.TryGetValue(map.Id, out var flags))
                foreach (var (code, metric, value, threshold, sev) in flags)
                    warnings.Add(reviews.Apply($"{map.Id}:{code}:map", sev, code, metric, value, threshold, "Docs/checks/map_audit.csv", asym));
            var gates = g.RunLoadGates(true);
            var rows = Acceptance(world, g, warnings.Skip(firstWarning).ToList(), gates);
            accept.Add((map.Id, AcceptanceJson(rows)));
            foreach (var (row, pass, detail) in rows)
                if (!pass) failures.Add($"{map.Id}: {row}: {detail}");
            foreach (var scene in MapStressScenes.All)
                if (scene.MapId == map.Id) stress[scene.Id] = SceneJson(scene, g, map);
            summary.Add(new[]
            {
                map.Id, g.Ground.Components.ToString(), g.Naval.Components.ToString(), g.Chokes.Count.ToString(), g.Lanes.Count.ToString(),
                g.Positions.Count.ToString(), g.StagingAreas.Count.ToString(), g.ShoreFireRegions.Count.ToString(),
                gates.Count(x => x.Pass) + "/" + gates.Count, g.Warnings.Count.ToString(),
                g.ObjectiveApproaches.Sum(a => a.Approaches.Count).ToString(), rows.Count(r => r.pass) + "/" + rows.Count,
            });
            Console.WriteLine($"{map.Id}: chokes {g.Chokes.Count}, lanes {g.Lanes.Count}, positions {g.Positions.Count}, gates {gates.Count(x => x.Pass)}/{gates.Count}, warnings {g.Warnings.Count} ({(DateTime.UtcNow - t0).TotalSeconds:0.0} s)");
        }
        foreach (var f in failures) Console.WriteLine("ACCEPTANCE FAIL " + f);
        if (args.Length > 0)
        {
            foreach (var w in warnings) Console.WriteLine($"  {w["warningId"]} [{w["severity"]}/{w["status"]}] {w["metric"]}={w["value"]} ({w["threshold"]})");
            Console.WriteLine("prefix run: nothing written (run without arguments to regenerate Docs/maps).");
            return check && failures.Count > 0 ? 1 : 0;
        }
        var head = $"\"generator\": \"Tools/maps/topogen (GameplayTopology, lanes W1-A / W2-A)\", \"source\": \"Assets/MachineBrigade/Resources/Data/maps (canonical)\", " +
                   $"\"note\": \"generated: never edit by hand\", \"global\": {Global(catalog)}";
        WriteMaps(Path.Combine(outDir, "GameplayTopology.json"), head, topo);
        WriteMaps(Path.Combine(outDir, "MapConnectivity.json"), head, conn);
        WriteMaps(Path.Combine(outDir, "TacticalPositions.json"), head, pos);
        WriteMaps(Path.Combine(outDir, "NavalRouteAudit.json"), head, naval);
        WriteMaps(Path.Combine(outDir, "SpawnFairnessAudit.json"), head, fair);
        WriteMaps(Path.Combine(outDir, "ObjectiveApproaches.json"), head, appr);
        WriteMaps(Path.Combine(outDir, "MapAcceptance.json"), head, accept);
        WriteStress(Path.Combine(outDir, "STRESS_SCENES.json"), head, stress);
        WriteRegistry(Path.Combine(outDir, "MapWarningRegistry.json"), warnings, reviews.Version);
        WriteSummary(Path.Combine(outDir, "GAMEPLAY_TOPOLOGY.md"), summary, warnings, failures);
        Console.WriteLine($"{files.Count} maps, {warnings.Count} warnings, {failures.Count} acceptance failures -> {outDir}");
        return check && failures.Count > 0 ? 1 : 0;
    }

    private static string FindRoot()
    {
        var d = new DirectoryInfo(AppContext.BaseDirectory);
        while (d != null && !Directory.Exists(Path.Combine(d.FullName, "Assets", "MachineBrigade"))) d = d.Parent;
        return d?.FullName ?? Directory.GetCurrentDirectory();
    }

    /// <summary>The world as a battle starts it, topology-wise: props (the world does), the map's fixed defences, wall lines standing (gates open).</summary>
    private static SimWorld Prepare(Catalog catalog, MapDefinition map)
    {
        var world = new SimWorld(catalog, map, 1);
        foreach (var u in map.Units)
            if (catalog.Vehicles.TryGetValue(u.DefId, out var def) && def.Static) world.SpawnVehicle(u.DefId, u.Team, u.Position, u.Heading);
        foreach (var line in map.Walls)
            foreach (var s in line.Segments) world.Grid.AddBlocker(s.Center, s.Width, s.Depth, SimWorld.ObstacleClearance);
        _ = world.Lanes;
        _ = world.Topology;
        return world;
    }

    private static string? Asymmetry(string file)
    {
        using var doc = JsonDocument.Parse(File.ReadAllText(file), new JsonDocumentOptions { CommentHandling = JsonCommentHandling.Skip, AllowTrailingCommas = true });
        if (doc.RootElement.TryGetProperty("asymmetry", out var a) && a.TryGetProperty("intended", out var i) && i.ValueKind == JsonValueKind.True &&
            a.TryGetProperty("reason", out var r)) return r.GetString();
        return null;
    }

    // ------------------------------------------------------------------------------------------------ JSON

    private sealed class J
    {
        private readonly StringBuilder _b = new();
        private bool _first = true;
        public override string ToString() => _b.ToString();

        private void Sep()
        {
            if (!_first) _b.Append(',');
            _first = false;
        }

        public J O(string? key = null)
        {
            Key(key);
            _b.Append('{');
            _first = true;
            return this;
        }

        public J A(string? key = null)
        {
            Key(key);
            _b.Append('[');
            _first = true;
            return this;
        }

        public J EndO()
        {
            _b.Append('}');
            _first = false;
            return this;
        }

        public J EndA()
        {
            _b.Append(']');
            _first = false;
            return this;
        }

        private void Key(string? key)
        {
            Sep();
            if (key != null) _b.Append(JsonSerializer.Serialize(key)).Append(':');
        }

        public J V(string? key, object? value)
        {
            Key(key);
            _b.Append(Value(value));
            return this;
        }

        public J Raw(string? key, string json)
        {
            Key(key);
            _b.Append(json);
            return this;
        }

        public static string Value(object? value) => value switch
        {
            null => "null",
            float f => float.IsFinite(f) ? Math.Round(f, 2).ToString("0.##", CultureInfo.InvariantCulture) : "null",
            double d => double.IsFinite(d) ? Math.Round(d, 2).ToString("0.##", CultureInfo.InvariantCulture) : "null",
            int i => i.ToString(CultureInfo.InvariantCulture),
            bool b => b ? "true" : "false",
            Vector2 v => $"[{Value(v.X)},{Value(v.Y)}]",
            string s => JsonSerializer.Serialize(s),
            Enum e => JsonSerializer.Serialize(e.ToString()),
            _ => JsonSerializer.Serialize(value.ToString()),
        };
    }

    private static string Points(IEnumerable<Vector2> points) => "[" + string.Join(",", points.Select(p => J.Value(p))) + "]";

    private static void WriteMaps(string path, string head, List<(string id, string json)> maps)
    {
        var sb = new StringBuilder();
        sb.Append("{").Append(head).Append(",\n\"maps\": {\n");
        for (var i = 0; i < maps.Count; i++)
            sb.Append(JsonSerializer.Serialize(maps[i].id)).Append(": ").Append(maps[i].json).Append(i + 1 < maps.Count ? ",\n" : "\n");
        sb.Append("}}\n");
        File.WriteAllText(path, sb.ToString(), new UTF8Encoding(false));
    }

    private static string Global(Catalog catalog)
    {
        var j = new J().O();
        j.A("terrainSemantics");
        foreach (TerrainTag tag in Enum.GetValues(typeof(TerrainTag)))
        {
            var s = GameplayTopology.SemanticsOf(tag);
            j.O().V("tag", tag).V("movementCost", s.MovementCost).V("traction", s.Traction).V("concealment", s.Concealment)
                .V("visualCover", s.VisualCover).V("directFireCover", s.DirectFireCover).V("artilleryExposure", s.ArtilleryExposure)
                .V("mineSuitability", s.MineSuitability).V("hullDownPotential", s.HullDownPotential).V("largeVehiclePenalty", s.LargeVehiclePenalty).EndO();
        }
        j.EndA();
        j.A("weatherPresentation");
        foreach (var k in WeatherPresentation.Kinds)
        {
            var w = WeatherPresentation.Of(k);
            j.O().V("weather", w.Weather).V("fogDensity", w.FogDensity).V("ambientLight", w.AmbientLight).V("cloudiness", w.Cloudiness)
                .V("rainIntensity", w.RainIntensity).V("snowIntensity", w.SnowIntensity).V("windStrength", w.WindStrength)
                .V("windDirectionDeg", w.WindDirectionDeg).V("lightningIntensity", w.LightningIntensity).V("dustIntensity", w.DustIntensity)
                .V("contrailVisibility", w.ContrailVisibility).V("muzzleFlashVisibility", w.MuzzleFlashVisibility)
                .V("lowpassEnvironmentAmount", w.LowpassEnvironmentAmount).V("telegraphBoost", w.TelegraphBoost)
                .V("ambientAudioProfile", w.AmbientAudioProfile).V("reverbProfile", w.ReverbProfile).EndO();
        }
        j.EndA();
        j.V("sizeBands", string.Join(";", SimTunables.Maps.Topology.SizeBands.Select(x => x.ToString(CultureInfo.InvariantCulture))));
        j.V("navalSafety", SimTunables.Maps.Topology.NavalSafety);
        j.EndO();
        return j.ToString();
    }

    private static void Classes(J j, GameplayTopology g)
    {
        j.A("sizeClasses");
        foreach (var c in g.Classes)
            j.O().V("class", c.Class).V("members", c.Members).V("referenceWidth", c.ReferenceWidth).V("medianWidth", c.MedianWidth)
                .V("referenceLength", c.ReferenceLength).V("medianSpeed", c.MedianSpeed).V("clearanceCells", c.ClearanceCells)
                .V("turnRadius", c.TurnRadius).V("components", g.ClassGraph(c.Class).Components).EndO();
        j.EndA();
    }

    private static string Topology(SimWorld world, GameplayTopology g)
    {
        var j = new J().O();
        j.V("ground", g.Ground.Components).V("naval", g.Naval.Components).V("amphibious", g.Amphibious.Components);
        Classes(j, g);
        j.A("chokes");
        foreach (var c in g.Chokes)
            j.O().V("id", c.Id).V("type", c.Type).V("shape", c.Shape).V("doorway", c.FromDoorway).V("centre", c.Centre).V("through", c.Through)
                .V("openWidth", c.OpenWidth).V("usableWidthM", c.UsableWidthM).V("length", c.Length)
                .V("maxLightSideBySide", c.MaxLightSideBySide).V("maxMediumSideBySide", c.MaxMediumSideBySide).V("maxHeavySideBySide", c.MaxHeavySideBySide)
                .V("estimatedThroughput", c.EstimatedThroughput).V("oppositeTrafficAllowed", c.OppositeTrafficAllowed)
                .V("queueAreaA", c.QueueAreaA.Centre).V("queueASafe", c.QueueAreaA.Safe).V("queueAIssue", c.QueueAreaA.Issue)
                .V("queueAreaB", c.QueueAreaB.Centre).V("queueBSafe", c.QueueAreaB.Safe).V("queueBIssue", c.QueueAreaB.Issue)
                .V("largestClass", c.LargestClass).V("critical", c.Critical).V("component", c.Component).EndO();
        j.EndA();
        j.A("lanes");
        foreach (var l in g.Lanes)
            j.O().V("id", l.Id).V("kind", l.Kind).V("from", l.From).V("to", l.To).V("lengthM", l.LengthM).V("laneWidth", l.LaneWidth).V("minWidth", l.MinWidth)
                .V("directionality", l.Directionality).V("vehicleClassSupport", l.VehicleClassSupport).V("expectedTravelSpeed", l.ExpectedTravelSpeed)
                .Raw("chokeDependency", "[" + string.Join(",", l.ChokeDependency) + "]").Raw("objectiveCoverage", "[" + string.Join(",", l.ObjectiveCoverage.Select(J.Value)) + "]")
                .V("trafficCapacity", l.TrafficCapacity).V("parkingForbidden", l.ParkingForbidden).Raw("points", Points(l.Points)).EndO();
        j.EndA();
        j.A("spawnClearZones");
        foreach (var z in g.SpawnClearZones)
            j.O().V("team", z.Team).V("centre", z.Centre).V("exitRadius", z.ExitRadius).V("clearRadius", z.ClearRadius).V("rallyRadius", z.RallyRadius).EndO();
        j.EndA();
        j.A("breaches");
        foreach (var b in g.Breaches)
            j.O().V("id", b.Id).V("owner", b.Owner).V("ring", b.Ring).V("centre", b.Centre).V("openingWidthM", b.OpeningWidthM)
                .Raw("blockedRouteIds", "[" + string.Join(",", b.BlockedRouteIds.Select(J.Value)) + "]").V("pathCostReductionOnDestroy", b.PathCostReductionOnDestroy)
                .Raw("heavyAccessGained", "[" + string.Join(",", b.HeavyAccessGained.Select(x => J.Value(x))) + "]")
                .V("objectiveAccessGained", b.ObjectiveAccessGained).V("alternateRouteExists", b.AlternateRouteExists).V("defensiveTowerCoverage", b.DefensiveTowerCoverage).EndO();
        j.EndA();
        j.O("terrainCells");
        foreach (var (tag, n) in g.TerrainCells.OrderBy(x => x.Key)) j.V(tag.ToString(), n);
        j.EndO();
        j.A("loadGates");
        foreach (var r in g.RunLoadGates(true)) j.O().V("gate", r.Gate).V("pass", r.Pass).V("detail", r.Detail).EndO();
        j.EndA();
        _ = world;
        return j.EndO().ToString();
    }

    private static string Connectivity(GameplayTopology g)
    {
        var j = new J().O();
        j.V("groundComponents", g.Ground.Components).V("navalComponents", g.Naval.Components).V("amphibiousComponents", g.Amphibious.Components);
        j.A("anchors");
        foreach (var a in g.Anchors)
            j.O().V("id", a.Id).V("kind", a.Kind).V("team", a.Team).V("position", a.Position).V("domain", a.Domain).V("resolved", a.Resolved)
                .V("ground", a.GroundComponent).V("naval", a.NavalComponent).V("amphibious", a.AmphibiousComponent)
                .Raw("classComponent", "[" + string.Join(",", a.ClassComponent) + "]").EndO();
        j.EndA();
        j.A("routes");
        foreach (var r in g.RouteAudits)
            j.O().V("from", r.From).V("to", r.To).V("class", r.Class).V("reachable", r.Reachable).V("lengthM", r.LengthM).V("minClearWidthM", r.MinClearWidthM)
                .V("minTurnSpaceM", r.MinTurnSpaceM).V("gateMinWidthM", r.GateMinWidthM).V("bridgeMinWidthM", r.BridgeMinWidthM).V("turnsFit", r.TurnsFit)
                .V("swingTurnSpaceM", r.SwingTurnSpaceM).V("turnsFitSwing", r.TurnsFitSwing).EndO();
        j.EndA();
        return j.EndO().ToString();
    }

    private static string Positions(GameplayTopology g)
    {
        var j = new J().O();
        j.A("positions");
        foreach (var p in g.Positions)
        {
            j.O().V("id", p.Id).V("kind", p.Kind).V("team", p.Team).V("position", p.Position).V("subject", p.Subject).V("score", p.Score);
            j.O("terms");
            foreach (var (k, v) in p.Terms) j.V(k, v);
            j.EndO().EndO();
        }
        j.EndA();
        j.A("staging");
        foreach (var s in g.StagingAreas)
            j.O().V("id", s.Id).V("team", s.Team).V("objective", s.Objective).V("centre", s.Centre).V("radius", s.Radius).V("capacityLight", s.CapacityLight)
                .V("capacityHeavy", s.CapacityHeavy).V("coverScore", s.CoverScore).V("threatExposure", s.ThreatExposure)
                .V("distanceToObjective", s.DistanceToObjective).V("lanesAvailable", s.LanesAvailable).EndO();
        j.EndA();
        return j.EndO().ToString();
    }

    private static string Naval(GameplayTopology g)
    {
        var j = new J().O();
        j.A("nodes");
        foreach (var n in g.NavalNodes)
            j.O().V("id", n.Id).V("kind", n.Kind).V("lane", n.Lane).V("position", n.Position).V("component", n.Component).V("width", n.Width)
                .V("curveRadiusM", n.CurveRadiusM).V("broadsideRoomLeft", n.BroadsideRoomLeft).V("broadsideRoomRight", n.BroadsideRoomRight)
                .V("maxRecommendedShipRadius", n.MaxRecommendedShipRadius).V("maxRecommendedShipLength", n.MaxRecommendedShipLength)
                .V("passingAllowed", n.PassingAllowed).V("passingBay", n.PassingBay).V("bossSafe", n.BossSafe).V("shoreThreatExposure", n.ShoreThreatExposure).EndO();
        j.EndA();
        j.A("segments");
        foreach (var s in g.NavalSegments)
            j.O().V("index", s.Index).V("a", s.A).V("b", s.B).V("kind", s.Kind).V("oneWay", s.OneWay).V("lane", s.Lane).V("length", s.Length)
                .V("entryHeading", s.EntryHeading).V("exitHeading", s.ExitHeading).V("curveRadiusM", s.CurveRadiusM)
                .V("passingAllowed", s.PassingAllowed).V("noOvertake", s.NoOvertake).EndO();
        j.EndA();
        j.A("turnAudit");
        foreach (var t in g.NavalTurnAudits)
            j.O().V("ship", t.Ship).V("boss", t.Boss).V("manoeuvre", t.Manoeuvre).V("where", t.Where).V("speed", t.Speed).V("turnRateDeg", t.TurnRateDeg)
                .V("rmin", t.Rmin).V("required", t.Required).V("available", t.Available).V("pass", t.Pass).V("mitigated", t.Mitigated).V("note", t.Note).EndO();
        j.EndA();
        j.A("shoreFireRegions");
        foreach (var r in g.ShoreFireRegions)
            j.O().V("id", r.Id).V("groundComponentId", r.GroundComponentId).V("fromU", r.FromU).V("toU", r.ToU).V("from", r.FromPoint).V("to", r.ToPoint)
                .V("centre", r.Centre).V("cells", r.Cells).V("nearestLane", r.NearestLane).V("minDistanceToNavalLane", r.MinDistanceToNavalLane)
                .V("maxDistanceToNavalLane", r.MaxDistanceToNavalLane).V("elevation", r.Elevation).V("losQuality", r.LosQuality)
                .V("coverScore", r.CoverScore).V("maxUsefulWeaponRange", r.MaxUsefulWeaponRange).EndO();
        j.EndA();
        return j.EndO().ToString();
    }

    private static string Fairness(GameplayTopology g)
    {
        var j = new J().O().A("spawns");
        foreach (var f in g.SpawnFairness)
            j.O().V("spawn", f.SpawnId).V("team", f.Team).V("position", f.Position).V("enemyDirectLOSAtSpawn", f.EnemyDirectLosAtSpawn)
                .V("enemyDirectLOSAtExit", f.EnemyDirectLosAtExit).V("enemyArtilleryCoverageAtSpawn", f.EnemyArtilleryCoverageAtSpawn)
                .V("spawnToFirstCoverM", f.SpawnToFirstCoverM).V("spawnExitWidthM", f.SpawnExitWidthM).V("narrowestExitM", f.NarrowestExitM)
                .V("alternateExitCount", f.AlternateExitCount).V("spawnQueueCapacity", f.SpawnQueueCapacity).V("enemyRushETA", f.EnemyRushEta)
                .V("friendlyObjectiveETA", f.FriendlyObjectiveEta).Raw("flags", "[" + string.Join(",", f.Flags.Select(J.Value)) + "]").EndO();
        return j.EndA().EndO().ToString();
    }

    // ------------------------------------------------------------------------------------------------ W2-A: approaches, acceptance, stress

    private static string Region(TacticalRegion? r)
    {
        if (r == null) return "null";
        var j = new J().O().V("centre", r.Centre).V("radius", r.Radius).V("cells", r.Cells).V("score", r.Score);
        j.O("terms");
        foreach (var (k, v) in r.Terms) j.V(k, v);
        return j.EndO().EndO().ToString();
    }

    private static string Approaches(GameplayTopology g)
    {
        var j = new J().O().A("sets");
        foreach (var a in g.ObjectiveApproaches)
        {
            j.O().V("id", a.Id).V("objective", a.Objective).V("team", a.Team).V("position", a.ObjectivePosition).V("distinct", a.Distinct)
                .Raw("artillerySupport", Region(a.ArtillerySupport)).Raw("defenderFallback", Region(a.DefenderFallback));
            j.A("routes");
            foreach (var r in a.Approaches)
                j.O().V("id", r.Id).Raw("roles", "[" + string.Join(",", r.Roles.Select(x => J.Value(x))) + "]").V("lengthM", r.LengthM)
                    .V("etaSeconds", r.EtaSeconds).V("exposure", r.Exposure).V("minWidthM", r.MinWidthM).V("vehicleClassSupport", r.VehicleClassSupport)
                    .Raw("chokeIds", "[" + string.Join(",", r.ChokeIds) + "]").V("laneId", r.LaneId).V("arrivalBearingDeg", r.ArrivalBearingDeg)
                    .Raw("points", Points(r.Points)).EndO();
            j.EndA().EndO();
        }
        return j.EndA().EndO().ToString();
    }

    /// <summary>
    /// Spec CI map rows (and the CJ validators' checks) for one map: what the acceptance tests assert, measured here so the
    /// export pack and the lead see them without a Unity run. The registry rows given are this map's, statuses applied.
    /// </summary>
    private static List<(string row, bool pass, string detail)> Acceptance(SimWorld world, GameplayTopology g, List<Dictionary<string, object?>> mapWarnings,
        List<LoadGateResult> gates)
    {
        var rows = new List<(string, bool, string)>();
        string Join(IEnumerable<string> items) => string.Join(", ", items.Take(8));
        string S(Dictionary<string, object?> w, string k) => w.TryGetValue(k, out var v) ? v as string ?? "" : "";
        // CI 1: objectives / spawns resolve (map_topology_audit).
        var unresolved = g.Anchors.Where(a => !a.Resolved && a.Kind is AnchorKind.Spawn or AnchorKind.MissionSpawn or AnchorKind.EntryGate or AnchorKind.Objective
            or AnchorKind.Base or AnchorKind.Fortress or AnchorKind.Battery or AnchorKind.NavalLane or AnchorKind.NavalNode or AnchorKind.BossRoute).Select(a => a.Id).ToList();
        rows.Add(("CI1 objectives/spawns resolve to components", unresolved.Count == 0, Join(unresolved)));
        // CI 2: every spawn -> objective pair audited for Heavy, SuperHeavy and Boss; an unreachable one carries a governed warning.
        var pairs = g.RouteAudits.Select(r => (r.From, r.To)).Distinct().ToList();
        var missing = new List<string>();
        var big = new[] { VehicleSizeClass.Heavy, VehicleSizeClass.SuperHeavy, VehicleSizeClass.Boss };
        foreach (var (from, to) in pairs)
            foreach (var cls in big)
                if (!g.RouteAudits.Any(r => r.From == from && r.To == to && r.Class == cls)) missing.Add($"{from}->{to}/{cls}");
        foreach (var cls in big)
            if (g.RouteAudits.Any(r => r.Class == cls && !r.Reachable) && !mapWarnings.Any(w => S(w, "code") == "ROUTE_SIZE" && S(w, "warningId").EndsWith(":" + cls, StringComparison.Ordinal)))
                missing.Add($"unreachable {cls} route without a ROUTE_SIZE warning");
        rows.Add(("CI2 heavy/boss routes validated by size", missing.Count == 0, Join(missing)));
        // CI 3: boss naval curvature (naval_route_audit).
        var bad = g.NavalTurnAudits.Where(t => t.Boss && !t.Pass && !t.Mitigated).Select(t => $"{t.Ship} {t.Manoeuvre} {t.Where}").ToList();
        rows.Add(("CI3 boss naval routes pass the curvature audit", bad.Count == 0, Join(bad)));
        // CI 4: critical chokes carry width and capacity.
        var chokes = g.Chokes.Where(c => c.Critical && !(c.UsableWidthM > 0f && c.EstimatedThroughput > 0f && c.MaxLightSideBySide >= 0)).Select(c => "choke" + c.Id).ToList();
        rows.Add(("CI4 critical chokes have width/capacity", chokes.Count == 0, Join(chokes)));
        // CI 5: no unexplained full-exit direct fire (spawn_fairness_audit).
        var exposed = mapWarnings.Where(w => S(w, "code") == "SPAWN_FULL_EXIT_DIRECT_FIRE" && S(w, "status") == "OPEN").Select(w => S(w, "warningId")).ToList();
        rows.Add(("CI5 no unexplained full-exit direct fire", exposed.Count == 0, Join(exposed)));
        // CI 6: shore-fire feasibility: a map with naval lanes and ground has shore fire regions.
        var lanes = world.Map.Sea?.Lanes.Count ?? 0;
        var shoreOk = lanes == 0 || g.ShoreFireRegions.Count > 0 || g.Ground.Components == 0;
        rows.Add(("CI6 shore-fire feasibility", shoreOk, lanes == 0 ? "no naval lanes" : $"{g.ShoreFireRegions.Count} regions"));
        // CI 7: every warning governed (state, owner, reason; none left "not reviewed").
        var ungoverned = mapWarnings.Where(w => S(w, "status").Length == 0 || S(w, "owner").Length == 0 || S(w, "acceptedReason").Length == 0 ||
            S(w, "acceptedReason").StartsWith("not reviewed", StringComparison.Ordinal)).Select(w => S(w, "warningId")).ToList();
        rows.Add(("CI7 warnings have state/owner/reason", ungoverned.Count == 0, Join(ungoverned)));
        // BW: the load gates (full).
        var failed = gates.Where(x => !x.Pass).Select(x => x.Gate + " " + x.Detail).ToList();
        rows.Add(("BW load gates pass", failed.Count == 0, Join(failed)));
        // H (tactical_position_audit): every objective a side reaches by ground has an approach set with its roles.
        var noRoles = new List<string>();
        foreach (var a in g.ObjectiveApproaches)
        {
            if (a.Approaches.Count == 0)
            {
                // Unreachable by ground for the side: the route audit (CI 2) and ROUTE_SIZE cover it; a light route that exists is a fault.
                if (g.RouteAudits.Any(r => r.To == a.Objective && r.From == "rally_" + a.Team && r.Class == VehicleSizeClass.Light && r.Reachable)) noRoles.Add(a.Id + " no route");
                continue;
            }
            foreach (var role in new[] { ApproachRole.Primary, ApproachRole.Shortest, ApproachRole.Safest })
                if (a.For(role) == null) noRoles.Add($"{a.Id} {role}");
        }
        rows.Add(("H objective approaches (primary / shortest / safest)", noRoles.Count == 0, Join(noRoles)));
        // I: staging areas off the major transit lanes (owner prompt 15).
        var staging = g.StagingAreas.Where(st => g.Lanes.Any(l => l.ParkingForbidden && l.DistanceTo(st.Centre) < 6f)).Select(st => st.Id).ToList();
        rows.Add(("I staging areas off major transit lanes", staging.Count == 0, Join(staging)));
        return rows;
    }

    private static string AcceptanceJson(List<(string row, bool pass, string detail)> rows)
    {
        var j = new J().O().V("pass", rows.All(r => r.pass)).A("rows");
        foreach (var (row, pass, detail) in rows) j.O().V("row", row).V("pass", pass).V("detail", detail).EndO();
        return j.EndA().EndO().ToString();
    }

    private static string SceneJson(MapStressScene scene, GameplayTopology g, MapDefinition map)
    {
        var (what, at) = MapStressScenes.FocusOf(scene, g, map.Centre);
        var j = new J().O().V("id", scene.Id).V("title", scene.Title).V("map", scene.MapId).V("mode", scene.Mode).V("perSide", scene.PerSide)
            .Raw("roster", "[" + string.Join(",", scene.Roster.Select(J.Value)) + "]");
        j.A("extra");
        foreach (var u in scene.Extra) j.O().V("unit", u.Unit).V("team", u.Team).V("at", u.At).V("count", u.Count).EndO();
        j.EndA();
        j.V("weather", scene.Weather).V("wreckSeed", scene.WreckSeed).V("focus", scene.Focus).V("focusResolved", what).V("focusAt", at)
            .V("warmupSeconds", scene.WarmupSeconds).V("seconds", scene.Seconds).V("seed", scene.Seed)
            .V("harness", scene.Mode == "conquest" ? "Tests/EditMode MapVaW2AStressHarness (Explicit, map metrics)" : "Unity play (ModeSessions siege session): final part")
            .Raw("mapMetrics", "[" + string.Join(",", MapStressScene.MapMetrics.Select(J.Value)) + "]")
            .Raw("renderMetrics", "[" + string.Join(",", MapStressScene.RenderMetrics.Select(J.Value)) + "]")
            .Raw("audioMetrics", "[" + string.Join(",", MapStressScene.AudioMetrics.Select(J.Value)) + "]");
        return j.EndO().ToString();
    }

    private static void WriteStress(string path, string head, Dictionary<string, string> scenes)
    {
        var sb = new StringBuilder();
        sb.Append("{").Append(head).Append(",\n\"scenes\": [\n");
        var ordered = MapStressScenes.All.Where(s => scenes.ContainsKey(s.Id)).ToList();
        for (var i = 0; i < ordered.Count; i++) sb.Append(scenes[ordered[i].Id]).Append(i + 1 < ordered.Count ? ",\n" : "\n");
        sb.Append("]}\n");
        File.WriteAllText(path, sb.ToString(), new UTF8Encoding(false));
    }

    // ------------------------------------------------------------------------------------------------ warnings

    /// <summary>The static audit's flags (Docs/checks/map_audit.csv), as registry rows: code, metric, value, threshold, severity.</summary>
    private static Dictionary<string, List<(string, string, string, string, string)>> AuditFlags()
    {
        var result = new Dictionary<string, List<(string, string, string, string, string)>>(StringComparer.Ordinal);
        var path = Path.Combine(Root, "Docs", "checks", "map_audit.csv");
        if (!File.Exists(path)) return result;
        var lines = File.ReadAllLines(path);
        var header = SplitCsv(lines[0]);
        int Col(string n) => Array.IndexOf(header, n);
        foreach (var line in lines.Skip(1))
        {
            var c = SplitCsv(line);
            if (c.Length < header.Length) continue;
            var list = new List<(string, string, string, string, string)>();
            foreach (var flag in c[Col("flags")].Split("; ", StringSplitOptions.RemoveEmptyEntries))
            {
                if (flag == "GREEN") continue;
                var sev = flag.StartsWith("RED", StringComparison.Ordinal) ? "RED" : "YELLOW";
                var name = flag.Substring(sev.Length + 1);
                var row = name switch
                {
                    "sightline" => ("AUDIT_SIGHTLINE", "sightlineP95", c[Col("sightlineP95")], "<= 32 (tank gun)", sev),
                    "exits" => ("AUDIT_EXITS", "exitCount", c[Col("exitCount")], ">= 2 per drop zone", sev),
                    "path delta" => ("AUDIT_PATH_DELTA", "medianPathDelta", c[Col("medianPathDelta")], "<= 10 %", sev),
                    "neutral delta" => ("AUDIT_NEUTRAL_DELTA", "neutralValueDelta", c[Col("neutralValueDelta")], "<= 10 %", sev),
                    "one lane" => ("AUDIT_ONE_LANE", "independentLaneCount", c[Col("independentLaneCount")], ">= 2", sev),
                    "connectivity" => ("AUDIT_CONNECTIVITY", "objectiveReachability", c[Col("objectiveReachability")], "ok", sev),
                    _ => ("AUDIT_" + name.ToUpperInvariant().Replace(' ', '_'), name, "", "", sev),
                };
                list.Add(row);
            }
            result[c[Col("map")]] = list;
        }
        return result;
    }

    private static string[] SplitCsv(string line)
    {
        var cells = new List<string>();
        var sb = new StringBuilder();
        var quoted = false;
        for (var i = 0; i < line.Length; i++)
        {
            var ch = line[i];
            if (quoted)
            {
                if (ch == '"' && i + 1 < line.Length && line[i + 1] == '"') { sb.Append('"'); i++; }
                else if (ch == '"') quoted = false;
                else sb.Append(ch);
            }
            else if (ch == '"') quoted = true;
            else if (ch == ',') { cells.Add(sb.ToString()); sb.Clear(); }
            else sb.Append(ch);
        }
        cells.Add(sb.ToString());
        return cells.ToArray();
    }

    /// <summary>Docs/maps/map_warning_reviews.json: the human review (rules by glob on the warning id, then per-id overrides).</summary>
    private sealed class Reviews
    {
        public string Version = "";
        private readonly List<(string match, bool? asymmetric, string status, string owner, string reason, string reviewed)> _rules = new();
        private readonly Dictionary<string, (string status, string owner, string reason, string reviewed)> _overrides = new(StringComparer.Ordinal);

        public static Reviews Load(string path)
        {
            var r = new Reviews();
            if (!File.Exists(path)) return r;
            using var doc = JsonDocument.Parse(File.ReadAllText(path), new JsonDocumentOptions { CommentHandling = JsonCommentHandling.Skip, AllowTrailingCommas = true });
            var root = doc.RootElement;
            r.Version = root.TryGetProperty("version", out var v) ? v.GetString() ?? "" : "";
            string S(JsonElement e, string k) => e.TryGetProperty(k, out var x) ? x.GetString() ?? "" : "";
            foreach (var rule in root.GetProperty("rules").EnumerateArray())
            {
                bool? asym = rule.TryGetProperty("asymmetric", out var a) ? a.GetBoolean() : null;
                r._rules.Add((S(rule, "match"), asym, S(rule, "status"), S(rule, "owner"), S(rule, "reason"), S(rule, "lastReviewedVersion")));
            }
            if (root.TryGetProperty("overrides", out var o))
                foreach (var p in o.EnumerateObject())
                    r._overrides[p.Name] = (S(p.Value, "status"), S(p.Value, "owner"), S(p.Value, "reason"), S(p.Value, "lastReviewedVersion"));
            return r;
        }

        private static bool Glob(string pattern, string text)
        {
            var rx = "^" + System.Text.RegularExpressions.Regex.Escape(pattern).Replace("\\*", ".*") + "$";
            return System.Text.RegularExpressions.Regex.IsMatch(text, rx);
        }

        public Dictionary<string, object?> Apply(string id, string severity, string code, string metric, string value, string threshold, string source, string? asymmetry)
        {
            string status = "OPEN", owner = "maps", reason = "not reviewed yet (generated)", reviewed = "";
            if (_overrides.TryGetValue(id, out var o)) (status, owner, reason, reviewed) = o;
            else
                foreach (var r in _rules)
                {
                    if (!Glob(r.match, id)) continue;
                    if (r.asymmetric is { } want && want != (asymmetry != null)) continue;
                    (status, owner, reason, reviewed) = (r.status, r.owner, r.reason, r.reviewed);
                    if (r.asymmetric == true && asymmetry != null) reason = reason.Replace("{asymmetry}", asymmetry);
                    break;
                }
            return new Dictionary<string, object?>
            {
                ["warningId"] = id, ["severity"] = severity, ["code"] = code, ["metric"] = metric, ["value"] = value, ["threshold"] = threshold,
                ["status"] = status, ["owner"] = owner, ["acceptedReason"] = reason, ["lastReviewedVersion"] = reviewed.Length > 0 ? reviewed : Version,
                ["source"] = source,
            };
        }
    }

    private static void WriteRegistry(string path, List<Dictionary<string, object?>> rows, string version)
    {
        var sb = new StringBuilder();
        sb.Append("{\"generator\": \"Tools/maps/topogen (lanes W1-A / W2-A)\", \"reviews\": \"Docs/maps/map_warning_reviews.json\", \"version\": ")
          .Append(JsonSerializer.Serialize(version)).Append(", \"statuses\": [\"OPEN\", \"FIXED\", \"ACCEPTED_INTENTIONAL\", \"PLAYTEST_REQUIRED\"],\n\"warnings\": [\n");
        for (var i = 0; i < rows.Count; i++)
        {
            sb.Append('{').Append(string.Join(", ", rows[i].Select(kv => JsonSerializer.Serialize(kv.Key) + ": " + J.Value(kv.Value)))).Append('}');
            sb.Append(i + 1 < rows.Count ? ",\n" : "\n");
        }
        sb.Append("]}\n");
        File.WriteAllText(path, sb.ToString(), new UTF8Encoding(false));
    }

    private static void WriteSummary(string path, List<string[]> rows, List<Dictionary<string, object?>> warnings, List<string> failures)
    {
        var sb = new StringBuilder();
        sb.AppendLine("# Gameplay topology (generated)");
        sb.AppendLine();
        sb.AppendLine("Generated by `Tools/maps/topogen` from the canonical map files through the game's `GameplayTopology` (lanes W1-A / W2-A,");
        sb.AppendLine("map spec Parts C-P, U, V, BT, BW, CI, CJ). Never edit by hand: regenerate. Data: `GameplayTopology.json`, `MapConnectivity.json`,");
        sb.AppendLine("`TacticalPositions.json`, `NavalRouteAudit.json`, `SpawnFairnessAudit.json`, `MapWarningRegistry.json` (statuses from");
        sb.AppendLine("`map_warning_reviews.json`), `ObjectiveApproaches.json` (spec H), `MapAcceptance.json` (spec CI map rows),");
        sb.AppendLine("`STRESS_SCENES.json` (spec BT). Worlds are built as a battle starts them (props, the map's fixed defences, wall lines");
        sb.AppendLine("standing with their gates open; base towers depend on the loadout and are not placed) and never stepped.");
        sb.AppendLine();
        var byStatus = warnings.GroupBy(w => (string)w["status"]!).OrderBy(x => x.Key, StringComparer.Ordinal).Select(x => $"{x.Key} {x.Count()}");
        var bySeverity = warnings.GroupBy(w => (string)w["severity"]!).OrderBy(x => x.Key, StringComparer.Ordinal).Select(x => $"{x.Key} {x.Count()}");
        sb.AppendLine($"{rows.Count} maps, {warnings.Count} warnings: {string.Join(", ", bySeverity)}; by status {string.Join(", ", byStatus)}.");
        sb.AppendLine();
        var codes = warnings.GroupBy(w => $"{w["code"]} ({w["severity"]}, {w["status"]})").OrderBy(x => x.Key, StringComparer.Ordinal);
        sb.AppendLine("| Warning code (severity, status) | Count |");
        sb.AppendLine("|---|---|");
        foreach (var c in codes) sb.AppendLine($"| {c.Key} | {c.Count()} |");
        sb.AppendLine();
        var passing = rows.Count(r => r[r.Length - 1].Split('/')[0] == r[r.Length - 1].Split('/')[1]);
        sb.AppendLine($"Acceptance (spec CI map rows + BW + H + I, `MapAcceptance.json`): {passing} of {rows.Count} maps pass every row; {failures.Count} failing rows.");
        foreach (var f in failures.Take(20)) sb.AppendLine($"- {f}");
        sb.AppendLine();
        sb.AppendLine("| Map | Ground comp. | Naval comp. | Chokes | Lanes | Positions | Staging | Shore regions | Load gates | Warnings | Approach routes | Acceptance |");
        sb.AppendLine("|---|---|---|---|---|---|---|---|---|---|---|---|");
        foreach (var r in rows) sb.AppendLine("| " + string.Join(" | ", r) + " |");
        File.WriteAllText(path, sb.ToString(), new UTF8Encoding(false));
    }
}
