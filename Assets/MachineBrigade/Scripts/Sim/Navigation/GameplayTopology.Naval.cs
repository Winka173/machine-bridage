#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using Tun = MachineBrigade.Sim.Content.SimTunables.Maps.Topology;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>
    /// GameplayTopology's sea layers (spec K-N), built on first use on a map with a sea: shore fire regions, the sea route graph's
    /// kinematic node / segment fields, and the turn-radius audit of every ship of the catalog against the routes' lane changes,
    /// bays and patrol turnabouts (Rmin = speed / angular speed, required = Rmin x maps.topology.navalSafety).
    /// </summary>
    public sealed partial class GameplayTopology
    {
        private List<ShoreFireRegion>? _shore;
        private List<NavalNodeInfo>? _navalNodes;
        private List<NavalSegmentInfo>? _navalSegments;
        private List<NavalTurnAudit>? _turns;

        public IReadOnlyList<ShoreFireRegion> ShoreFireRegions => _shore ??= BuildShore();
        public IReadOnlyList<NavalNodeInfo> NavalNodes => _navalNodes ?? BuildNaval().nodes;
        public IReadOnlyList<NavalSegmentInfo> NavalSegments => _navalSegments ?? BuildNaval().segments;
        public IReadOnlyList<NavalTurnAudit> NavalTurnAudits => _turns ??= BuildTurns();

        /// <summary>The catalog's ships (sea units with a speed), by id.</summary>
        private List<VehicleDef> Ships()
        {
            var ids = new List<string>(_world.Catalog.Vehicles.Keys);
            ids.Sort(StringComparer.Ordinal);
            var list = new List<VehicleDef>();
            foreach (var id in ids)
            {
                var d = _world.Catalog.Vehicles[id];
                if (d.Naval != null && d.Speed > 0f && !d.Flying) list.Add(d);
            }
            return list;
        }

        // ================================================================================================ shore fire regions (spec K)

        /// <summary>The distance (m) from a point to a lane's line (its stretch u in [-End, End] at w = W) in the coast frame.</summary>
        private static float LaneDistance(SeaDef sea, SeaLaneDef lane, Vector2 p)
        {
            var f = sea.Frame(p);
            var u = Math.Clamp(f.X, -lane.End, lane.End);
            return Vector2.Distance(f, new Vector2(u, lane.W));
        }

        private List<ShoreFireRegion> BuildShore()
        {
            var list = new List<ShoreFireRegion>();
            if (_world.Map.Sea is not { } sea || sea.Lanes.Count == 0) return list;
            var corridor = (RouteGraph()?.Corridor ?? SeaRouteGraph.DefaultCorridor);
            // The ground cells within the band of the waterline, by stretch of u.
            var buckets = new SortedDictionary<int, List<int>>();
            for (var i = 0; i < CellsN; i++)
            {
                if (!Map.Ground.Passable[i]) continue;
                var p = Map.CellCentre(i);
                var f = sea.Frame(p);
                var shore = sea.ShoreAt(f.X);
                if (f.Y > shore || f.Y < shore - Tun.ShoreBand) continue;
                var key = (int)MathF.Floor(f.X / Tun.ShoreStep);
                if (!buckets.TryGetValue(key, out var cells)) buckets[key] = cells = new List<int>();
                cells.Add(i);
            }
            var id = 0;
            foreach (var (key, cells) in buckets)
            {
                // The stretch's largest ground component (a pier head apart from the beach is its own stretch next time).
                var counts = new SortedDictionary<int, int>();
                foreach (var c in cells)
                {
                    var comp = Map.Ground.ComponentOfCell(c);
                    counts[comp] = counts.TryGetValue(comp, out var n) ? n + 1 : 1;
                }
                var best = 0;
                var bestN = -1;
                foreach (var (comp, n) in counts)
                    if (n > bestN)
                    {
                        best = comp;
                        bestN = n;
                    }
                var mine = cells.FindAll(c => Map.Ground.ComponentOfCell(c) == best);
                if (mine.Count < global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.BuildShoreCountMax) continue;
                SeaLaneDef? nearest = null;
                var nearestD = float.MaxValue;
                var sum = Vector2.Zero;
                foreach (var c in mine) sum += Map.CellCentre(c);
                var centre = sum / mine.Count;
                foreach (var l in sea.Lanes)
                {
                    var d = LaneDistance(sea, l, centre);
                    if (d < nearestD)
                    {
                        nearestD = d;
                        nearest = l;
                    }
                }
                if (nearest == null) continue;
                float min = float.MaxValue, max = 0f, useful = 0f;
                int clear = 0, covered = 0, sampled = 0;
                for (var k = 0; k < mine.Count; k++)
                {
                    var p = Map.CellCentre(mine[k]);
                    var d = LaneDistance(sea, nearest, p);
                    min = MathF.Min(min, d);
                    max = MathF.Max(max, d);
                    foreach (var l in sea.Lanes) useful = MathF.Max(useful, LaneDistance(sea, l, p) + corridor * global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.BuildShoreCorridorScale);
                    if (BesideCover(p)) covered++;
                    if (k % 2 != 0) continue;
                    sampled++;
                    var f = sea.Frame(p);
                    var target = sea.At(Math.Clamp(f.X, -nearest.End, nearest.End), nearest.W);
                    if (LineClear(p, target)) clear++;
                }
                var u0 = key * Tun.ShoreStep;
                var u1 = u0 + Tun.ShoreStep;
                list.Add(new ShoreFireRegion
                {
                    Id = ++id,
                    GroundComponentId = best,
                    FromU = u0,
                    ToU = u1,
                    FromPoint = sea.At(u0, sea.ShoreAt(u0)),
                    ToPoint = sea.At(u1, sea.ShoreAt(u1)),
                    Centre = centre,
                    Cells = mine.Count,
                    NearestLane = nearest.Id,
                    MinDistanceToNavalLane = min,
                    MaxDistanceToNavalLane = max,
                    Elevation = 0f,
                    LosQuality = sampled > 0 ? clear / (float)sampled : 0f,
                    CoverScore = covered / (float)mine.Count,
                    MaxUsefulWeaponRange = useful,
                });
            }
            return list;
        }

        /// <summary>
        /// Spec K: the nearest a unit of ground component <paramref name="component"/> can stand to naval lane
        /// <paramref name="lane"/> (m; +inf: no shore of that component). "Cannot enter water" is not "cannot influence water":
        /// a weapon with at least this reach affects ships on the lane from reachable shore.
        /// </summary>
        public float ShoreReach(int component, string lane)
        {
            var best = float.PositiveInfinity;
            foreach (var r in ShoreFireRegions)
                if (r.GroundComponentId == component && r.NearestLane == lane) best = MathF.Min(best, r.MinDistanceToNavalLane);
            if (!float.IsPositiveInfinity(best) || _world.Map.Sea is not { } sea || sea.Lane(lane) is not { } l) return best;
            // The region's nearest lane may be another one: measure this lane from the component's regions.
            foreach (var r in ShoreFireRegions)
                if (r.GroundComponentId == component) best = MathF.Min(best, LaneDistance(sea, l, r.Centre) - (r.MaxDistanceToNavalLane - r.MinDistanceToNavalLane));
            return best;
        }

        // ================================================================================================ naval routes (spec L, N)

        /// <summary>Water (m) from a point out along <paramref name="dir"/> to the map's edge.</summary>
        private float EdgeRoom(Vector2 p, Vector2 dir)
        {
            var min = _world.Map.Min;
            var max = _world.Map.Max;
            var t = float.PositiveInfinity;
            if (dir.X > 1e-4f) t = MathF.Min(t, (max.X - p.X) / dir.X);
            if (dir.X < -1e-4f) t = MathF.Min(t, (min.X - p.X) / dir.X);
            if (dir.Y > 1e-4f) t = MathF.Min(t, (max.Y - p.Y) / dir.Y);
            if (dir.Y < -1e-4f) t = MathF.Min(t, (min.Y - p.Y) / dir.Y);
            return MathF.Max(0f, t);
        }

        /// <summary>The S-curve radius (m) of a lateral move <paramref name="offset"/> over a run <paramref name="run"/>: (L^2 + d^2) / 4d.</summary>
        public static float SCurveRadius(float run, float offset) =>
            offset < global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.SCurveRadiusOffsetMax ? float.PositiveInfinity : (run * run + offset * offset) / (global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.SCurveRadiusOffsetScale * offset);

        private (List<NavalNodeInfo> nodes, List<NavalSegmentInfo> segments) BuildNaval()
        {
            var nodes = new List<NavalNodeInfo>();
            var segments = new List<NavalSegmentInfo>();
            _navalNodes = nodes;
            _navalSegments = segments;
            if (_world.Map.Sea is not { } sea || RouteGraph() is not { } graph) return (nodes, segments);
            var ships = Ships();
            var maxWidth = 0f;
            foreach (var s in ships) maxWidth = MathF.Max(maxWidth, s.Width);
            foreach (var s in graph.Segments)
            {
                var a = graph.Nodes[s.A];
                var b = graph.Nodes[s.B];
                var heading = SimMath.HeadingOf(b.Position - a.Position) * 180f / MathF.PI;
                var info = new NavalSegmentInfo
                {
                    Index = s.Index,
                    A = a.Id,
                    B = b.Id,
                    Kind = s.Kind,
                    OneWay = s.OneWay,
                    Lane = s.Lane,
                    Length = s.Length,
                    EntryHeading = (heading + 360f) % 360f,
                    ExitHeading = (heading + 360f) % 360f,
                };
                if (s.Kind != SeaSegmentKind.Track)
                    info.CurveRadiusM = SCurveRadius(SeaRouteGraph.NodeStep, MathF.Abs(b.Frame.Y - a.Frame.Y));
                info.PassingAllowed = s.Kind == SeaSegmentKind.Track && !s.OneWay && graph.Corridor * global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.BuildNavalCorridorScale >= global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.BuildNavalMaxWidthScale * maxWidth + global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.BuildNavalNavalMarginScale * Tun.NavalMargin;
                info.NoOvertake = s.OneWay || !info.PassingAllowed;
                segments.Add(info);
            }
            var batteries = sea.Batteries;
            foreach (var n in graph.Nodes)
            {
                var info = new NavalNodeInfo
                {
                    Index = n.Index,
                    Id = n.Id,
                    Kind = n.Kind,
                    Lane = n.Lane,
                    Position = n.Position,
                    Component = Map.Naval.ComponentOfCell(Map.Naval.NearestPassableCell(n.Position, 4)),
                    Width = graph.Corridor * global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.BuildNavalCorridorScale,
                };
                var shoreRoom = n.Frame.Y - sea.ShoreAt(n.Frame.X);
                var seaRoom = EdgeRoom(n.Position, sea.Out);
                info.BroadsideRoomLeft = shoreRoom;
                info.BroadsideRoomRight = seaRoom;
                info.MaxRecommendedShipRadius = MathF.Max(0f, MathF.Min(shoreRoom, seaRoom) - Tun.NavalMargin);
                info.MaxRecommendedShipLength = info.MaxRecommendedShipRadius * 2f;
                foreach (var s in segments)
                    if ((s.A == n.Id || s.B == n.Id) && s.Kind != SeaSegmentKind.Track) info.CurveRadiusM = MathF.Min(info.CurveRadiusM, s.CurveRadiusM);
                // Passing: a holding node within the bay reach along the coast, or a cross link here.
                var bestBay = float.MaxValue;
                foreach (var h in graph.Nodes)
                {
                    if (h.Kind != SeaNodeKind.Holding) continue;
                    var d = MathF.Abs(h.Frame.X - n.Frame.X);
                    if (d <= SeaRouteGraph.BayReach && d < bestBay)
                    {
                        bestBay = d;
                        info.PassingBay = h.Id;
                    }
                }
                foreach (var s in graph.Segments)
                    if (s.Kind == SeaSegmentKind.Cross && (s.A == n.Index || s.B == n.Index)) info.PassingAllowed = true;
                info.PassingAllowed |= info.PassingBay != null;
                var exposure = 0;
                foreach (var b in batteries)
                    if (Vector2.Distance(b.At, n.Position) <= Tun.ArtilleryRef) exposure++;
                foreach (var r in ShoreFireRegions)
                    if (Vector2.Distance(r.Centre, n.Position) - (r.MaxDistanceToNavalLane - r.MinDistanceToNavalLane) * global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.BuildNavalMaxDistanceToNavalLaneScale <= Tun.DirectFireRef) exposure++;
                info.ShoreThreatExposure = exposure;
                nodes.Add(info);
            }
            // Boss safety: every boss ship fits the node's water and its turns pass (or the controller's mitigation holds).
            var turns = NavalTurnAudits;
            foreach (var info in nodes)
            {
                if (info.Kind == SeaNodeKind.Exit) continue;
                foreach (var s in ships)
                {
                    if (!s.Boss) continue;
                    if (s.HullBound > info.MaxRecommendedShipRadius) info.BossSafe = false;
                    foreach (var t in turns)
                        if (t.Ship == s.Id && t.Where == info.Id && !t.Pass && !t.Mitigated) info.BossSafe = false;
                }
            }
            return (nodes, segments);
        }

        // ================================================================================================ turn audit (spec M)

        private List<NavalTurnAudit> BuildTurns()
        {
            var list = new List<NavalTurnAudit>();
            if (_world.Map.Sea is not { } sea || RouteGraph() is not { } graph) return list;
            var throttle = SimTunables.Bosses.BossBrain.TurnaboutThrottle;
            foreach (var ship in Ships())
            {
                var rate = ship.TurnRate;
                var rmin = ship.Speed / MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.BuildTurnsRateFloor, rate);
                var required = rmin * Tun.NavalSafety;
                var slow = rmin * throttle;
                var look = Bosses.NavalBossMovementController.LookAhead(ship.Speed, ship.Length);
                // The S-curve radius over the look-ahead for the lateral offset the one-step radius implies.
                float lookRadius(float stepRadius)
                {
                    if (float.IsPositiveInfinity(stepRadius)) return stepRadius;
                    var step = SeaRouteGraph.NodeStep;
                    // Solve (L^2 + d^2) / 4d = stepRadius for d (the smaller root), then the radius over the look-ahead.
                    var disc = global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.BuildTurnsStepRadiusScale * stepRadius * stepRadius - step * step;
                    if (disc < 0f) return stepRadius;
                    var d = 2f * stepRadius - MathF.Sqrt(disc);
                    return SCurveRadius(MathF.Max(step, look), d);
                }
                NavalTurnAudit Add(string manoeuvre, string where, float available, bool mitigable, string note)
                {
                    var a = new NavalTurnAudit
                    {
                        Ship = ship.Id,
                        Boss = ship.Boss,
                        Manoeuvre = manoeuvre,
                        Where = where,
                        Speed = ship.Speed,
                        TurnRateDeg = rate * 180f / MathF.PI,
                        Rmin = rmin,
                        Required = required,
                        Available = available,
                        Pass = available >= required,
                    };
                    a.Mitigated = !a.Pass && mitigable && available >= slow;
                    // A boss ship changes lane over its controller's look-ahead (AI MASTER spec 54), not over one node step.
                    if (!a.Pass && manoeuvre == "lane-change" && ship.Boss && lookRadius(available) >= required)
                    {
                        a.Mitigated = true;
                        note += $"; the boss controller's look-ahead ({look:0} m) spreads it (radius {lookRadius(available):0.0} m)";
                    }
                    a.Note = a.Pass || manoeuvre == "lane-change" ? note : a.Mitigated ? $"{note}; comes about at {throttle:0.00} speed (Rmin there {slow:0.0} m)" : note;
                    list.Add(a);
                    return a;
                }
                // Lane changes and bays: the S-curve each cross / bay link allows (once per pair of lines, the tightest).
                var seen = new Dictionary<string, (float r, string where)>();
                foreach (var s in graph.Segments)
                {
                    if (s.Kind == SeaSegmentKind.Track) continue;
                    var a = graph.Nodes[s.A];
                    var b = graph.Nodes[s.B];
                    var r = SCurveRadius(SeaRouteGraph.NodeStep, MathF.Abs(b.Frame.Y - a.Frame.Y));
                    var key = (s.Kind == SeaSegmentKind.Bay ? "bay:" : "lane-change:") + (a.Lane ?? "") + "|" + (b.Lane ?? "") + "|" + (b.Kind == SeaNodeKind.Holding || a.Kind == SeaNodeKind.Holding ? "h" : "");
                    if (!seen.TryGetValue(key, out var old) || r < old.r) seen[key] = (r, a.Kind == SeaNodeKind.Holding ? b.Id : a.Id);
                }
                var keys = new List<string>(seen.Keys);
                keys.Sort(StringComparer.Ordinal);
                foreach (var k in keys)
                {
                    var bay = k.StartsWith("bay:", StringComparison.Ordinal);
                    // A ship goes into a bay to hold (slowing down): the coming-about mitigation applies; a lane change is under way.
                    Add(bay ? "bay" : "lane-change", seen[k].where, seen[k].r, bay, bay ? "holding-bay S-curve over one node step" : "lane-change S-curve over one node step");
                }
                // Patrol turnabouts: a U-turn at each end of every lane's patrol needs 2R of water to one side plus half the hull.
                foreach (var lane in sea.Lanes)
                {
                    if (lane.Patrol <= 0f) continue;
                    foreach (var end in new[] { -lane.Patrol, lane.Patrol })
                    {
                        var p = sea.At(end, lane.W);
                        var shoreRoom = lane.W - sea.ShoreAt(end);
                        var seaRoom = EdgeRoom(p, sea.Out);
                        var room = MathF.Max(shoreRoom, seaRoom) - Tun.NavalMargin - ship.Width * 0.5f;
                        var available = MathF.Max(0f, room * global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.BuildTurnsRoomScale);
                        Add("turnabout", $"{lane.Id}@{(end < 0 ? "-" : "+")}{lane.Patrol:0}", available, true, "U-turn at the patrol's end");
                    }
                }
                // Hairpins (spec M1): a node whose two route links turn back more than 120 degrees.
                foreach (var n in graph.Nodes)
                {
                    if (n.Kind != SeaNodeKind.Track) continue;
                    var links = new List<Vector2>();
                    foreach (var s in graph.Segments)
                    {
                        if (s.A != n.Index && s.B != n.Index) continue;
                        var other = graph.Nodes[s.A == n.Index ? s.B : s.A];
                        if (other.Kind != SeaNodeKind.Holding) links.Add(other.Position);
                    }
                    var worst = 0f;
                    for (var i = 0; i < links.Count; i++)
                    for (var k = i + 1; k < links.Count; k++)
                    {
                        var inDir = n.Position - links[i];
                        var outDir = links[k] - n.Position;
                        var cos = Vector2.Dot(inDir, outDir) / MathF.Max(1e-3f, inDir.Length() * outDir.Length());
                        worst = MathF.Max(worst, MathF.Acos(Math.Clamp(cos, -1f, 1f)) * 180f / MathF.PI);
                    }
                    if (worst > 120f) Add("hairpin", n.Id, 0f, true, $"links turn back {worst:0} degrees");
                }
            }
            return list;
        }
    }
}
