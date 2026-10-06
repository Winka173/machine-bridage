#nullable enable
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Numerics;
using Tun = MachineBrigade.Sim.Content.SimTunables.Maps.Topology;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>
    /// Spec BW (map topology load gates) and spec U (the generated map warnings). The runtime runs the quick gates once per battle
    /// (<see cref="SimWorld.GameplayTopology"/>'s first build: results in <see cref="LoadGates"/> and the map telemetry, never an
    /// exception); Tools/maps/topogen and the acceptance tests run the full set. Warnings carry the measured value and threshold;
    /// their status, owner and reason come from Docs/maps/map_warning_reviews.json (never auto-fixed: spec CH).
    /// </summary>
    public sealed partial class GameplayTopology
    {
        private List<LoadGateResult>? _gates;
        private List<MapWarning>? _warnings;

        /// <summary>The quick load gates (spec BW 1-5, 6 for chokes and zones, 7 as the runtime counter).</summary>
        public IReadOnlyList<LoadGateResult> LoadGates => _gates ??= RunLoadGates(false);

        private static string F(float v) => float.IsPositiveInfinity(v) ? "inf" : v.ToString("0.##", CultureInfo.InvariantCulture);

        /// <summary>Spec BW. <paramref name="full"/>: also the generated tactical points (positions, staging) and the artillery pockets.</summary>
        public List<LoadGateResult> RunLoadGates(bool full)
        {
            var results = new List<LoadGateResult>();
            var missing = new List<string>();
            foreach (var a in _anchors)
                if ((a.Kind is AnchorKind.Objective or AnchorKind.Base or AnchorKind.Fortress or AnchorKind.Battery) && !a.Resolved) missing.Add(a.Id);
            results.Add(new LoadGateResult("objectives-resolve", missing.Count == 0, string.Join(",", missing)));
            missing = new List<string>();
            foreach (var a in _anchors)
                if ((a.Kind is AnchorKind.Spawn or AnchorKind.MissionSpawn or AnchorKind.EntryGate) && !a.Resolved) missing.Add(a.Id);
            results.Add(new LoadGateResult("spawns-resolve", missing.Count == 0, string.Join(",", missing)));

            // Naval nodes: the graph's own checks, and every node on the map in one sea component.
            if (_world.Map.Sea is { } sea && RouteGraph() is { } graph)
            {
                var problems = new List<string>(graph.Validate(sea, _world.Map.HalfSize));
                var component = 0;
                foreach (var n in NavalNodes)
                {
                    if (n.Kind == SeaNodeKind.Exit || !_world.Map.Contains(n.Position)) continue;
                    if (n.Component <= 0) problems.Add($"{n.Id} off the sea");
                    else if (component == 0) component = n.Component;
                    else if (n.Component != component) problems.Add($"{n.Id} in sea component {n.Component}, not {component}");
                }
                results.Add(new LoadGateResult("naval-connected", problems.Count == 0, string.Join("; ", problems)));
                var bad = new List<string>();
                foreach (var t in NavalTurnAudits)
                    if (t.Boss && !t.Pass && !t.Mitigated) bad.Add($"{t.Ship} {t.Manoeuvre} {t.Where} {F(t.Available)}<{F(t.Required)}");
                results.Add(new LoadGateResult("boss-curvature", bad.Count == 0, string.Join("; ", bad)));
            }
            else
            {
                results.Add(new LoadGateResult("naval-connected", true, "no sea"));
                results.Add(new LoadGateResult("boss-curvature", true, "no sea"));
            }

            // Declared gates: every wall line's gate lets the largest normal class through.
            var super = Class(VehicleSizeClass.SuperHeavy);
            var need = super.ReferenceWidth + 2f * Tun.SideClearance;
            var narrow = new List<string>();
            foreach (var l in _world.Map.Walls)
                if (l.GateWidth < need) narrow.Add($"{l.Owner} ring {l.Ring} gate {F(l.GateWidth)} m < {F(need)} m");
            results.Add(new LoadGateResult("gate-clearance", narrow.Count == 0, string.Join("; ", narrow)));

            // Generated points inside the playable ground.
            var outside = new List<string>();
            void Inside(string id, Vector2 p)
            {
                if (!_world.Map.Contains(p) || !_world.Map.InsideBoundary(p)) outside.Add(id);
            }
            foreach (var c in _chokes) Inside("choke" + c.Id, c.Centre);
            foreach (var z in _spawnZones) Inside("spawnzone" + z.Team, z.Centre);
            if (full)
            {
                foreach (var p in Positions) Inside(p.Id, p.Position);
                foreach (var s in StagingAreas) Inside(s.Id, s.Centre);
                foreach (var r in ShoreFireRegions) Inside("shore" + r.Id, r.Centre);
            }
            results.Add(new LoadGateResult("points-in-bounds", outside.Count == 0, string.Join(",", outside)));

            // Fire-support anchors off the forbidden transit zones: the generated pockets (full), the runtime counter otherwise.
            if (full)
            {
                var onLane = new List<string>();
                foreach (var p in Positions)
                {
                    if (p.Kind != TacticalPositionKind.ArtilleryPocket) continue;
                    if (_world.LanesNoRebuild.NoParkAt(p.Position)) onLane.Add(p.Id);
                    foreach (var l in Lanes)
                        if (l.ParkingForbidden && l.DistanceTo(p.Position) < 6f) onLane.Add(p.Id + "@" + l.Id);
                }
                results.Add(new LoadGateResult("fire-support-transit", onLane.Count == 0, string.Join(",", onLane)));
            }
            else results.Add(new LoadGateResult("fire-support-transit", true, "runtime: MapTelemetry.FireSupportAnchorInTransit"));
            return results;
        }

        /// <summary>Spec U: the warnings this topology raises (full audit), ids "&lt;map&gt;:&lt;code&gt;:&lt;subject&gt;".</summary>
        public IReadOnlyList<MapWarning> Warnings => _warnings ??= BuildWarnings();

        private List<MapWarning> BuildWarnings()
        {
            var map = _world.Map.Id;
            var list = new List<MapWarning>();
            void Add(WarningSeverity severity, string code, string subject, string metric, string value, string threshold) =>
                list.Add(new MapWarning
                {
                    WarningId = $"{map}:{code}:{subject}",
                    Severity = severity,
                    Code = code,
                    Subject = subject,
                    Metric = metric,
                    Value = value,
                    Threshold = threshold,
                });

            foreach (var g in RunLoadGates(true))
                if (!g.Pass) Add(WarningSeverity.Red, "LOADGATE_" + g.Gate.ToUpperInvariant().Replace('-', '_'), g.Gate, "loadGate", g.Detail, "PASS");

            foreach (var f in SpawnFairness)
                foreach (var flag in f.Flags)
                {
                    var (metric, value, threshold) = flag switch
                    {
                        "FULL_EXIT_DIRECT_FIRE" => ("enemyDirectLOSAtExit", F(f.EnemyDirectLosAtExit), "< " + F(Tun.FullExposureShare)),
                        "ARTILLERY_FULL_COVER" => ("enemyArtilleryCoverageAtSpawn", F(f.EnemyArtilleryCoverageAtSpawn), "< 0.95 or an alternate exit"),
                        "EXIT_NARROWER_THAN_LARGEST" => ("narrowestExitM", F(f.NarrowestExitM), ">= " + F(Class(VehicleSizeClass.SuperHeavy).ReferenceWidth + 2f * Tun.SideClearance)),
                        "SINGLE_BLOCKER_SEALS" => ("narrowestExitM", F(f.NarrowestExitM), ">= " + F(2f * (Class(VehicleSizeClass.Heavy).ReferenceWidth + Tun.SeparationMargin)) + " or an alternate exit"),
                        _ => ("alternateExitCount", f.AlternateExitCount.ToString(CultureInfo.InvariantCulture), ">= 1"),
                    };
                    Add(flag == "NO_EXIT" ? WarningSeverity.Red : WarningSeverity.Yellow, "SPAWN_" + flag, f.SpawnId, metric, value, threshold);
                }

            for (var k = 0; k < 5; k++)
            {
                var cls = (VehicleSizeClass)k;
                var unreachable = new List<string>();
                int routes = 0, tight = 0;
                foreach (var r in RouteAudits)
                {
                    if (r.Class != cls) continue;
                    routes++;
                    if (!r.Reachable) unreachable.Add($"{r.From}->{r.To}");
                    else if (!r.TurnsFit) tight++;
                }
                if (unreachable.Count > 0)
                    Add(k <= (int)VehicleSizeClass.Medium ? WarningSeverity.Red : WarningSeverity.Yellow, "ROUTE_SIZE", cls.ToString(), "unreachable routes",
                        string.Join(",", unreachable), "0 (class clearance " + Class(cls).ClearanceCells + " cells)");
                if (tight > 0)
                    Add(WarningSeverity.Info, "ROUTE_TURN", cls.ToString(), "routes with a corner tighter than the pivot room",
                        $"{tight} of {routes}", "pivot radius " + F(Class(cls).TurnRadius) + " m");
            }

            var naval = new Dictionary<string, (WarningSeverity sev, string code, string value, string threshold)>();
            foreach (var t in NavalTurnAudits)
            {
                if (t.Pass) continue;
                var code = t.Boss ? t.Mitigated ? "NAVAL_TURN_MITIGATED" : "NAVAL_TURN" : "NAVAL_TURN_SHIP";
                var sev = t.Boss && !t.Mitigated ? WarningSeverity.Red : WarningSeverity.Yellow;
                var key = $"{code}|{t.Ship}:{t.Manoeuvre}";
                var value = $"{t.Where} {F(t.Available)} m";
                if (naval.TryGetValue(key, out var old)) value = old.value + "; " + value;
                naval[key] = (sev, code, value, $">= {F(t.Required)} m (Rmin {F(t.Rmin)} x {F(Tun.NavalSafety)})");
            }
            var keys = new List<string>(naval.Keys);
            keys.Sort(StringComparer.Ordinal);
            foreach (var key in keys)
            {
                var (sev, code, value, threshold) = naval[key];
                Add(sev, code, key.Substring(key.IndexOf('|') + 1), "turn radius available", value, threshold);
            }

            foreach (var c in _chokes)
            {
                if (!c.Critical) continue;
                foreach (var q in new[] { c.QueueAreaA, c.QueueAreaB })
                    if (!q.Safe) Add(WarningSeverity.Info, "CHOKE_QUEUE", $"choke{c.Id}{(q.Through == c.QueueAreaA.Through ? "A" : "B")}", "queue area", q.Issue, "safe");
            }

            var hullDown = 0;
            foreach (var p in Positions)
                if (p.Kind == TacticalPositionKind.HullDown) hullDown++;
            if (hullDown == 0) Add(WarningSeverity.Info, "HULLDOWN_NONE", "map", "hull-down positions", "0", "low cover (blocks hulls, not shots) on the map");

            // Spec S: orientation anchors (at least three macro landmarks in three compass quadrants).
            var landmarks = _world.Map.Landmarks;
            var quadrants = new HashSet<int>();
            var centre = _world.Map.Centre;
            foreach (var l in landmarks) quadrants.Add((l.Position.X >= centre.X ? 1 : 0) + (l.Position.Y >= centre.Y ? 2 : 0));
            if (landmarks.Count < 3) Add(WarningSeverity.Yellow, "LANDMARKS_FEW", "map", "landmarks", landmarks.Count.ToString(CultureInfo.InvariantCulture), ">= 3");
            else if (quadrants.Count < 3) Add(WarningSeverity.Yellow, "LANDMARKS_QUADRANTS", "map", "compass quadrants with a landmark", quadrants.Count.ToString(CultureInfo.InvariantCulture), ">= 3");
            return list;
        }
    }
}
