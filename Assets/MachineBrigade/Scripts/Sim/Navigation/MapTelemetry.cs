#nullable enable
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Numerics;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using Tun = MachineBrigade.Sim.Content.SimTunables.Maps.Topology;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>
    /// Map spec CA / owner prompt 64 (lane W1-A): counters that check the topology's assumptions in play: lane usage share, choke
    /// queue seconds, spawn-exit block events, first contact, objective arrival, heavy-unit routes their size class cannot
    /// drive, where fire support anchors (and any anchor in a forbidden transit zone), naval close-approach events, boss route
    /// replans, load-gate failures, the average engagement distance and (W2-A, behind a flag) approach-route usage. Sampled every maps.topology.telemetrySeconds (off with maps.topology.telemetry). Pure reads:
    /// no reading here ever feeds a decision, no random draw, so a battle plays the same with it on or off.
    /// </summary>
    public sealed class MapTelemetry
    {
        private readonly Dictionary<string, int> _laneSamples = new(StringComparer.Ordinal);
        private readonly Dictionary<string, double> _objectiveEta = new(StringComparer.Ordinal);
        private readonly Dictionary<string, int> _anchorUse = new(StringComparer.Ordinal);
        private readonly Dictionary<int, Vector2> _orderSeen = new();
        private readonly Dictionary<int, Vector2> _bossGoal = new();
        private readonly Dictionary<int, int> _cpaSeen = new();
        private readonly Dictionary<string, int> _approachSamples = new(StringComparer.Ordinal);
        private double _next;
        private double _engageSum;

        public int Samples { get; private set; }
        public int GroundSamples { get; private set; }

        /// <summary>Vehicle-seconds waiting at a passage (a doorway turn or a choke queue).</summary>
        public float ChokeQueueSeconds { get; private set; }

        /// <summary>The first shot of the battle (s; -1: none yet).</summary>
        public double FirstContactTime { get; private set; } = -1;

        public int HeavyRouteFailures { get; private set; }
        public int NavalCloseApproachEvents { get; private set; }
        public int BossRouteReplans { get; private set; }
        public int FireSupportAnchorSets { get; private set; }
        public int FireSupportAnchorInTransit { get; private set; }
        public List<string> LoadGateFailures { get; } = new();

        /// <summary>Lane W2-A (spec CA "average LOS engagement distance"): shots sampled (a vehicle that fired since the last sample, at its target).</summary>
        public int EngagementSamples { get; private set; }

        /// <summary>The mean shooter-to-target distance of the sampled shots (m; 0: none yet).</summary>
        public double AverageEngagementDistance => EngagementSamples > 0 ? _engageSum / EngagementSamples : 0;

        /// <summary>Lane W2-A (spec H): per approach route id, ground vehicle samples within 6 m of it (maps.topology.telemetryApproaches).</summary>
        public IReadOnlyDictionary<string, int> ApproachSamples => _approachSamples;

        /// <summary>Per tactical lane id: share of ground vehicle samples within 6 m of it.</summary>
        public IReadOnlyDictionary<string, int> LaneSamples => _laneSamples;

        /// <summary>"&lt;objective&gt;@&lt;team&gt;": the first time a vehicle of the side stood in it (s).</summary>
        public IReadOnlyDictionary<string, double> ObjectiveEta => _objectiveEta;

        /// <summary>Fire-support anchor sets by 10 m cell ("x,z"): the artillery firing-position distribution.</summary>
        public IReadOnlyDictionary<string, int> ArtilleryPositionUsage => _anchorUse;

        internal void Step(SimWorld world)
        {
            if (!Tun.Telemetry || world.Time < _next) return;
            _next = world.Time + Math.Max(0.1f, Tun.TelemetrySeconds);
            Samples++;
            var topology = world.GameplayTopology;
            var lanes = topology.Lanes;
            var approaches = Tun.TelemetryApproaches ? topology.ObjectiveApproaches : null;
            var since = world.Time - Math.Max(0.1f, Tun.TelemetrySeconds);
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive) continue;
                if (v.LastFiredAt > double.NegativeInfinity && (FirstContactTime < 0 || v.LastFiredAt < FirstContactTime)) FirstContactTime = v.LastFiredAt;
                if (v.LastFiredAt > since && v.Target.IsValid && Locate(world, v.Target) is { } at)
                {
                    EngagementSamples++;
                    _engageSum += Vector2.Distance(v.Position, at);
                }
                if (v.Flying || v.Def.Static) continue;
                if (v.Def.Naval == null)
                {
                    GroundSamples++;
                    string? best = null;
                    var bestD = 6f;
                    foreach (var l in lanes)
                    {
                        var d = l.DistanceTo(v.Position);
                        if (d >= bestD) continue;
                        bestD = d;
                        best = l.Id;
                    }
                    if (best != null) _laneSamples[best] = _laneSamples.TryGetValue(best, out var n) ? n + 1 : 1;
                    if (approaches != null)
                        foreach (var set in approaches)
                        {
                            if (set.Team != v.Team) continue;
                            foreach (var a in set.Approaches)
                                if (a.DistanceTo(v.Position) < 6f) _approachSamples[a.Id] = _approachSamples.TryGetValue(a.Id, out var m) ? m + 1 : 1;
                        }
                    if (v.Traffic.WaitingForGate) ChokeQueueSeconds += Tun.TelemetrySeconds;
                    foreach (var p in world.Map.Points)
                    {
                        var key = "point_" + p.Id + "@" + v.Team;
                        if (!_objectiveEta.ContainsKey(key) && Vector2.Distance(p.Position, v.Position) <= p.Radius) _objectiveEta[key] = world.Time;
                    }
                    // A heavy hull sent where its size class cannot drive (each new order once).
                    if (v.Order.Kind != OrderKind.Idle && GameplayTopology.ClassOf(v.Def) >= VehicleSizeClass.Heavy &&
                        (!_orderSeen.TryGetValue(v.Id.Value, out var seen) || Vector2.DistanceSquared(seen, v.Order.Point) > 4f))
                    {
                        _orderSeen[v.Id.Value] = v.Order.Point;
                        if (!topology.SizeClassReaches(v.Def, v.Position, v.Order.Point, 4f)) HeavyRouteFailures++;
                    }
                }
                if (v.Def.Boss)
                {
                    if (v.HasPath)
                    {
                        var goal = v.Path[v.Path.Count - 1];
                        if (_bossGoal.TryGetValue(v.Id.Value, out var old) && Vector2.DistanceSquared(old, goal) > 4f) BossRouteReplans++;
                        _bossGoal[v.Id.Value] = goal;
                    }
                    if (v.Brain is { } brain)
                    {
                        var threat = brain.CpaThreat.Value;
                        if (threat != 0 && (!_cpaSeen.TryGetValue(v.Id.Value, out var last) || last != threat)) NavalCloseApproachEvents++;
                        _cpaSeen[v.Id.Value] = threat;
                    }
                }
            }
        }

        /// <summary>Where an entity (vehicle or prop) stands (null: gone).</summary>
        private static Vector2? Locate(SimWorld world, EntityId id)
        {
            if (world.TryGetVehicle(id, out var v)) return v.Position;
            if (world.TryGetProp(id, out var p)) return p.Position;
            return null;
        }

        /// <summary>A fire-support anchor was set at <paramref name="point"/> (the director's call; counted only).</summary>
        internal void AnchorSet(Vector2 point, bool inTransit)
        {
            if (!Tun.Telemetry) return;
            FireSupportAnchorSets++;
            if (inTransit) FireSupportAnchorInTransit++;
            var key = string.Format(CultureInfo.InvariantCulture, "{0:0},{1:0}", MathF.Floor(point.X / 10f) * 10f, MathF.Floor(point.Y / 10f) * 10f);
            _anchorUse[key] = _anchorUse.TryGetValue(key, out var n) ? n + 1 : 1;
        }

        /// <summary>Every counter as (key, value) for a report or the debug view.</summary>
        public List<(string key, string value)> Snapshot(SimWorld world)
        {
            string N(double v) => v.ToString("0.##", CultureInfo.InvariantCulture);
            var list = new List<(string, string)>
            {
                ("samples", N(Samples)),
                ("firstContactTime", N(FirstContactTime)),
                ("chokeQueueSeconds", N(ChokeQueueSeconds)),
                ("spawnBlockEvents", N(world.Traffic.Stats.SpawnExitClears)),
                ("heavyRouteFailure", N(HeavyRouteFailures)),
                ("navalCollisionEvents", N(NavalCloseApproachEvents)),
                ("bossRouteReplanCount", N(BossRouteReplans)),
                ("fireSupportAnchorSets", N(FireSupportAnchorSets)),
                ("fireSupportAnchorInTransit", N(FireSupportAnchorInTransit)),
                ("loadGateFailures", string.Join(";", LoadGateFailures)),
                ("averageLosEngagementDistance", N(AverageEngagementDistance)),
                ("engagementSamples", N(EngagementSamples)),
            };
            var routes = new List<string>(_approachSamples.Keys);
            routes.Sort(StringComparer.Ordinal);
            foreach (var r in routes) list.Add(("approachUsage." + r, N(_approachSamples[r])));
            var lanes = new List<string>(_laneSamples.Keys);
            lanes.Sort(StringComparer.Ordinal);
            foreach (var l in lanes) list.Add(("laneUsageShare." + l, N(GroundSamples > 0 ? _laneSamples[l] / (double)GroundSamples : 0)));
            var etas = new List<string>(_objectiveEta.Keys);
            etas.Sort(StringComparer.Ordinal);
            foreach (var e in etas) list.Add(("objectiveETA." + e, N(_objectiveEta[e])));
            var cells = new List<string>(_anchorUse.Keys);
            cells.Sort(StringComparer.Ordinal);
            foreach (var c in cells) list.Add(("artilleryPositionUsage." + c, N(_anchorUse[c])));
            return list;
        }
    }
}
