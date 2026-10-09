#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using Tun = MachineBrigade.Sim.Content.SimTunables.Maps.Topology;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>Map spec H: what an approach route is to its objective (one route may hold several roles).</summary>
    public enum ApproachRole
    {
        Primary,
        Secondary,
        Flank,
        Shortest,
        Safest,
        HeavyCompatible,
    }

    /// <summary>Map spec H: one way from a side's spawn into an objective (a polyline on open ground) and its measures.</summary>
    public sealed class ObjectiveApproach
    {
        public string Id { get; internal set; } = "";

        /// <summary>The roles this route holds (the first is its main one).</summary>
        public List<ApproachRole> Roles { get; } = new();

        public IReadOnlyList<Vector2> Points { get; internal set; } = Array.Empty<Vector2>();
        public float LengthM { get; internal set; }

        /// <summary>Seconds a medium hull needs along it (the class's median speed times the terrain's speed factors).</summary>
        public float EtaSeconds { get; internal set; }

        /// <summary>Share of its cells with no fire-blocking cover within 2 m (open ground: the "safest" route has the least).</summary>
        public float Exposure { get; internal set; }

        /// <summary>The narrowest physical width along it (m; the ends excluded).</summary>
        public float MinWidthM { get; internal set; }

        /// <summary>The largest size class whose clearance holds along the whole route.</summary>
        public VehicleSizeClass VehicleClassSupport { get; internal set; }

        /// <summary>The tactical chokes it runs through (ids).</summary>
        public IReadOnlyList<int> ChokeIds { get; internal set; } = Array.Empty<int>();

        /// <summary>The tactical lane it follows (at least 60 % of its cells within the lane's reach; "": none).</summary>
        public string LaneId { get; internal set; } = "";

        /// <summary>Its arrival bearing at the objective (degrees, 0 = +z, clockwise): flank routes arrive from another side.</summary>
        public float ArrivalBearingDeg { get; internal set; }

        public bool Has(ApproachRole role) => Roles.Contains(role);

        /// <summary>Distance (m) from a point to the route's polyline.</summary>
        public float DistanceTo(Vector2 p)
        {
            var best = float.MaxValue;
            for (var i = 0; i + 1 < Points.Count; i++)
            {
                var a = Points[i];
                var ab = Points[i + 1] - a;
                var len2 = ab.LengthSquared();
                var t = len2 > 1e-6f ? Math.Clamp(Vector2.Dot(p - a, ab) / len2, 0f, 1f) : 0f;
                best = MathF.Min(best, Vector2.Distance(p, a + ab * t));
            }
            return Points.Count == 1 ? Vector2.Distance(p, Points[0]) : best;
        }
    }

    /// <summary>Map spec H: a generated region (an artillery-support area, a defender's fallback area).</summary>
    public sealed class TacticalRegion
    {
        public Vector2 Centre { get; internal set; }
        public float Radius { get; internal set; }

        /// <summary>Open, parkable ground cells inside it.</summary>
        public int Cells { get; internal set; }

        public float Score { get; internal set; }

        /// <summary>Its score terms by name.</summary>
        public Dictionary<string, float> Terms { get; } = new();
    }

    /// <summary>Map spec H: one objective's approach topology for one attacking side.</summary>
    public sealed class ObjectiveApproachSet
    {
        /// <summary>"appr&lt;team&gt;_&lt;objective&gt;".</summary>
        public string Id { get; internal set; } = "";

        /// <summary>The objective (anchor id).</summary>
        public string Objective { get; internal set; } = "";

        public Vector2 ObjectivePosition { get; internal set; }

        /// <summary>The attacking side (its spawn is where the routes start).</summary>
        public int Team { get; internal set; }

        /// <summary>The distinct routes (each with its roles); empty when the side's ground cannot reach the objective.</summary>
        public List<ObjectiveApproach> Approaches { get; } = new();

        /// <summary>Where the attacking side's artillery covers the approaches from (null: no open ground in the band).</summary>
        public TacticalRegion? ArtillerySupport { get; internal set; }

        /// <summary>Where the defending side falls back to behind the objective, with a line back to it (null: none).</summary>
        public TacticalRegion? DefenderFallback { get; internal set; }

        /// <summary>The route holding <paramref name="role"/> (null: none does).</summary>
        public ObjectiveApproach? For(ApproachRole role)
        {
            foreach (var a in Approaches)
                if (a.Has(role)) return a;
            return null;
        }

        /// <summary>Distinct ways in (routes that are not a near copy of another).</summary>
        public int Distinct => Approaches.Count;
    }

    /// <summary>
    /// Map spec H (lane W2-A): the objective approach topology. For each objective and each side that attacks it, up to
    /// <c>maps.topology.approachAlternatives</c> + 1 distinct routes from the side's spawn (the terrain-weighted cheapest, then
    /// alternatives with a cost added round the routes found, as the lanes are searched), a cover-weighted route (the safest)
    /// and the heavy class graph's route (heavy-compatible); roles by measure: shortest (length), primary (the one on the side's
    /// tactical lane, else the shortest), secondary (the next), flank (far off the primary and arriving from another side),
    /// safest (least exposure), heavy-compatible (the shortest a heavy hull can drive). Plus an artillery-support region in the
    /// attacker's half (approach coverage, direct-fire protection, no transit) and the defender's fallback region behind the
    /// objective (cover, a line back to the objective, exits). Built on first use; deterministic (fixed sample orders).
    /// </summary>
    public sealed partial class GameplayTopology
    {
        private List<ObjectiveApproachSet>? _approaches;
        private bool[]? _exposedCells;

        /// <summary>Spec H: every objective's approach sets (one per attacking side).</summary>
        public IReadOnlyList<ObjectiveApproachSet> ObjectiveApproaches => _approaches ??= BuildApproaches();

        /// <summary>The approach set of <paramref name="objective"/> for <paramref name="team"/> (null: none).</summary>
        public ObjectiveApproachSet? ApproachesTo(string objective, int team)
        {
            foreach (var s in ObjectiveApproaches)
                if (s.Team == team && s.Objective == objective) return s;
            return null;
        }

        /// <summary>The objective anchor whose capture circle (plus <paramref name="margin"/>) holds <paramref name="p"/> (null: none).</summary>
        public TopologyAnchor? ObjectiveAt(Vector2 p, float margin)
        {
            TopologyAnchor? best = null;
            var bestD = float.MaxValue;
            foreach (var (o, radius) in Objectives())
            {
                var d = Vector2.Distance(o.Position, p);
                if (d > radius + margin || d >= bestD) continue;
                bestD = d;
                best = o;
            }
            return best;
        }

        /// <summary>Per ground cell: no fire-blocking cover within 2 m (open to fire).</summary>
        private bool[] ExposedCells()
        {
            if (_exposedCells != null) return _exposedCells;
            var n = CellsN;
            _exposedCells = new bool[n];
            for (var i = 0; i < n; i++)
                if (Map.Ground.Passable[i]) _exposedCells[i] = !BesideCover(Map.CellCentre(i));
            return _exposedCells;
        }

        private List<ObjectiveApproachSet> BuildApproaches()
        {
            var list = new List<ObjectiveApproachSet>();
            var objectives = Objectives();
            for (var team = 0; team <= 1; team++)
            {
                if (Rally(team) is not { } rally) continue;
                foreach (var (o, radius) in objectives)
                {
                    if (o.Kind == AnchorKind.Base && o.Team == team) continue;
                    var set = new ObjectiveApproachSet { Id = $"appr{team}_{o.Id}", Objective = o.Id, ObjectivePosition = o.Position, Team = team };
                    Approaches(set, rally, o, radius);
                    if (set.Approaches.Count > 0)
                    {
                        set.ArtillerySupport = ArtillerySupport(set, rally, o, radius);
                        set.DefenderFallback = DefenderFallback(set, o, radius);
                    }
                    list.Add(set);
                }
            }
            return list;
        }

        private void Approaches(ObjectiveApproachSet set, TopologyAnchor rally, TopologyAnchor o, float radius)
        {
            var ground = Map.Ground.Passable;
            var from = CellNear(Map.Ground, rally.Position);
            var to = CellNear(Map.Ground, o.Position, (int)MathF.Ceiling(radius / Map.Cell));
            if (from < 0 || to < 0 || Map.Ground.ComponentOfCell(from) != Map.Ground.ComponentOfCell(to)) return;
            var routes = new List<(List<int> cells, HashSet<int> near)>();
            var penalty = new float[CellsN];

            bool Distinct(List<int> cells)
            {
                foreach (var (_, near) in routes)
                {
                    var shared = 0;
                    foreach (var c in cells)
                        if (near.Contains(c)) shared++;
                    if (shared > cells.Count * Tun.ApproachDistinctShare) return false;
                }
                return true;
            }

            ObjectiveApproach Add(List<int> cells, string id)
            {
                var near = Near(cells);
                routes.Add((cells, near));
                foreach (var c in near) penalty[c] += Tun.LanePenalty;
                var a = MakeApproach(id, cells, o.Position);
                set.Approaches.Add(a);
                return a;
            }

            // 1. The cheapest (terrain-weighted) route, then distinct alternatives.
            var first = CheapestPath(ground, from, to, null);
            if (first.Count == 0) return;
            Add(first, set.Id + "/r0");
            for (var k = 1; k <= Math.Max(0, Tun.ApproachAlternatives); k++)
            {
                var cells = CheapestPath(ground, from, to, penalty);
                if (cells.Count == 0) break;
                if (!Distinct(cells))
                {
                    foreach (var c in Near(cells)) penalty[c] += Tun.LanePenalty;
                    continue;
                }
                Add(cells, $"{set.Id}/r{k}");
            }
            // 2. The cover-weighted route (an exposed cell costs maps.topology.approachExposurePenalty more).
            var exposed = ExposedCells();
            var cover = new float[CellsN];
            for (var i = 0; i < cover.Length; i++) cover[i] = exposed[i] ? Tun.ApproachExposurePenalty : 0f;
            var safe = CheapestPath(ground, from, to, cover);
            if (safe.Count > 0 && Distinct(safe)) Add(safe, set.Id + "/safe");
            // 3. The heavy class graph's route, unless a route found already carries heavy hulls.
            var heavyFound = false;
            foreach (var a in set.Approaches)
                if (a.VehicleClassSupport >= VehicleSizeClass.Heavy) heavyFound = true;
            if (!heavyFound)
            {
                var heavy = ClassGraph(VehicleSizeClass.Heavy);
                var need = Class(VehicleSizeClass.Heavy).ClearanceCells;
                var hf = CellNear(heavy, rally.Position, need);
                var ht = heavy.NearestPassableCell(o.Position, Math.Max(SimTunables.Ai.Topology.NearestRings, (int)MathF.Ceiling(radius / Map.Cell)) + need);
                if (hf >= 0 && ht >= 0 && heavy.ComponentOfCell(hf) == heavy.ComponentOfCell(ht))
                {
                    var cells = CheapestPath(heavy.Passable, hf, ht, null);
                    if (cells.Count > 0)
                    {
                        var a = Add(cells, set.Id + "/heavy");
                        // The class graph holds only cells with the class's clearance: the whole route carries it.
                        if (a.VehicleClassSupport < VehicleSizeClass.Heavy) a.VehicleClassSupport = VehicleSizeClass.Heavy;
                    }
                }
            }
            AssignRoles(set, rally);
        }

        private ObjectiveApproach MakeApproach(string id, List<int> cells, Vector2 objective)
        {
            var grid = _world.Grid;
            var exposed = ExposedCells();
            var minClear = int.MaxValue;
            var minWidth = float.PositiveInfinity;
            var length = 0f;
            var time = 0f;
            var open = 0;
            var medium = Class(VehicleSizeClass.Medium);
            var speed = MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.MakeApproachMedianSpeedFloor, medium.MedianSpeed);
            for (var i = 0; i < cells.Count; i++)
            {
                var c = cells[i];
                var clear = WindowClearance(c, 2);
                if (i >= global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.MakeApproachIMin && i < cells.Count - global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.MakeApproachCountSub)
                {
                    minClear = Math.Min(minClear, clear);
                    minWidth = MathF.Min(minWidth, WidthOfClearance(clear));
                }
                if (exposed[c]) open++;
                if (i > 0)
                {
                    var step = Vector2.Distance(Map.CellCentre(cells[i - 1]), Map.CellCentre(c));
                    length += step;
                    time += step * MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.MakeApproachStepCostFloor, grid.StepCost(c)) / speed;
                }
            }
            if (minClear == int.MaxValue)
            {
                foreach (var c in cells) minClear = Math.Min(minClear, WindowClearance(c, global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.MakeApproachR));
                minWidth = WidthOfClearance(minClear == int.MaxValue ? 0 : minClear);
            }
            var support = VehicleSizeClass.Light;
            for (var k = 0; k < 5; k++)
                if (_classes[k].ClearanceCells <= Math.Max(1, minClear)) support = (VehicleSizeClass)k;
            var chokes = new List<int>();
            foreach (var ch in _chokes)
                foreach (var c in cells)
                    if (ch.Contains(Map.CellCentre(c)))
                    {
                        chokes.Add(ch.Id);
                        break;
                    }
            // Arrival bearing: from the point ~20 m out along the route to its end.
            var end = Map.CellCentre(cells[cells.Count - 1]);
            var back = end;
            var walked = 0f;
            for (var i = cells.Count - global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.MakeApproachCountSub2; i >= 0; i--)
            {
                var p = Map.CellCentre(cells[i]);
                walked += Vector2.Distance(p, back);
                back = p;
                if (walked >= 20f) break;
            }
            var dir = objective - back;
            var bearing = dir.LengthSquared() > 1e-4f ? MathF.Atan2(dir.X, dir.Y) * 180f / MathF.PI : 0f;
            if (bearing < 0f) bearing += 360f;
            var approach = new ObjectiveApproach
            {
                Id = id,
                Points = Simplify(cells, 2f),
                LengthM = length,
                EtaSeconds = time,
                Exposure = cells.Count > 0 ? open / (float)cells.Count : 0f,
                MinWidthM = minWidth,
                VehicleClassSupport = support,
                ChokeIds = chokes,
                ArrivalBearingDeg = bearing,
            };
            // The tactical lane it follows.
            var bestShare = 0f;
            foreach (var l in Lanes)
            {
                if (l.Kind == LaneKind.BossCorridor) continue;
                var inside = 0;
                foreach (var c in cells)
                    if (l.DistanceTo(Map.CellCentre(c)) <= global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.MakeApproachDistanceToMax) inside++;
                var share = cells.Count > 0 ? inside / (float)cells.Count : 0f;
                if (share < global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.MakeApproachShareMax || share <= bestShare) continue;
                bestShare = share;
                approach.LaneId = l.Id;
            }
            return approach;
        }

        private void AssignRoles(ObjectiveApproachSet set, TopologyAnchor rally)
        {
            var routes = set.Approaches;
            if (routes.Count == 0) return;
            ObjectiveApproach Best(Func<ObjectiveApproach, float> key, Func<ObjectiveApproach, bool>? filter = null)
            {
                ObjectiveApproach? best = null;
                var bestKey = float.MaxValue;
                foreach (var a in routes)
                {
                    if (filter != null && !filter(a)) continue;
                    var k = key(a);
                    if (best != null && k >= bestKey) continue;
                    best = a;
                    bestKey = k;
                }
                return best!;
            }
            var shortest = Best(a => a.LengthM);
            // Primary: on the side's own lane to this objective, else on the main lane, else the shortest.
            ObjectiveApproach? primary = null;
            foreach (var a in routes)
                if (a.LaneId.Length > 0)
                    foreach (var l in Lanes)
                        if (l.Id == a.LaneId && l.From == rally.Id && l.To == set.Objective) primary ??= a;
            if (primary == null)
                foreach (var a in routes)
                    if (a.LaneId.Length > 0)
                        foreach (var l in Lanes)
                            if (l.Id == a.LaneId && l.Kind == LaneKind.Main && Has(l.ObjectiveCoverage, set.Objective)) primary ??= a;
            primary ??= shortest;
            primary.Roles.Add(ApproachRole.Primary);
            // Flank: far off the primary and arriving from another side.
            var span = MathF.Min(_world.Map.Width, _world.Map.Length);
            var primaryPts = new List<Vector2>(primary.Points);
            foreach (var a in routes)
            {
                if (a == primary) continue;
                var offset = 0f;
                foreach (var p in a.Points) offset = MathF.Max(offset, PolylineDistance(primaryPts, p));
                var turn = MathF.Abs(((a.ArrivalBearingDeg - primary.ArrivalBearingDeg) % 360f + 540f) % 360f - 180f);
                if (offset >= Tun.ApproachFlankOffset * span && turn >= Tun.ApproachFlankBearing) a.Roles.Add(ApproachRole.Flank);
            }
            // Secondary: the shortest route that is neither the primary nor a flank.
            var others = new List<ObjectiveApproach>();
            foreach (var a in routes)
                if (a != primary && !a.Has(ApproachRole.Flank)) others.Add(a);
            if (others.Count > 0)
            {
                var secondary = others[0];
                foreach (var a in others)
                    if (a.LengthM < secondary.LengthM) secondary = a;
                secondary.Roles.Add(ApproachRole.Secondary);
            }
            shortest.Roles.Add(ApproachRole.Shortest);
            Best(a => a.Exposure + a.LengthM * 1e-6f).Roles.Add(ApproachRole.Safest);
            var heavyKey = 0f;
            ObjectiveApproach? heavyRoute = null;
            foreach (var a in routes)
            {
                if (a.VehicleClassSupport < VehicleSizeClass.Heavy) continue;
                if (heavyRoute != null && a.LengthM >= heavyKey) continue;
                heavyRoute = a;
                heavyKey = a.LengthM;
            }
            heavyRoute?.Roles.Add(ApproachRole.HeavyCompatible);
            // Order each route's roles by the enum (the first is its main one) and the routes by their main role.
            foreach (var a in routes) a.Roles.Sort();
            routes.Sort((x, y) =>
            {
                var c = (x.Roles.Count > 0 ? (int)x.Roles[0] : global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.AssignRolesCountFalse).CompareTo(y.Roles.Count > 0 ? (int)y.Roles[0] : global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.AssignRolesCountFalse);
                return c != 0 ? c : string.CompareOrdinal(x.Id, y.Id);
            });
        }

        /// <summary>Spec H: where the attacker's artillery covers the approaches from (in its own half of the objective's ring).</summary>
        private TacticalRegion? ArtillerySupport(ObjectiveApproachSet set, TopologyAnchor rally, TopologyAnchor o, float radius)
        {
            var home = rally.Position - o.Position;
            home = home.LengthSquared() > 1e-4f ? Vector2.Normalize(home) : Vector2.UnitY;
            var points = new List<Vector2>();
            foreach (var a in set.Approaches) points.AddRange(a.Points);
            var component = Map.Ground.ComponentAt(rally.Position);
            TacticalRegion? best = null;
            var lo = MathF.Max(radius + Tun.ArtilleryMinRef + global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.ArtillerySupportRadiusAdd, global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.ArtillerySupportRadiusFloor);
            var hi = MathF.Max(lo + global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.ArtillerySupportLoAdd, Tun.ArtilleryRef * global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.ArtillerySupportArtilleryRefScale);
            foreach (var f in new[] { 0f, global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.ArtillerySupportF2, 1f })
                for (var k = 0; k < 16; k++)
                {
                    var dir = SimMath.Forward(k * MathF.PI / 8f);
                    if (Vector2.Dot(dir, home) < 0.2f) continue;
                    var p = o.Position + dir * (lo + (hi - lo) * f);
                    if (!PositionOk(p) || (component > 0 && Map.Ground.ComponentAt(p) != component)) continue;
                    var forbidden = false;
                    foreach (var l in Lanes)
                        if (l.ParkingForbidden && l.DistanceTo(p) < global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.ArtillerySupportDistanceToMax) forbidden = true;
                    if (forbidden) continue;
                    var inBand = 0;
                    foreach (var q in points)
                    {
                        var d = Vector2.Distance(p, q);
                        if (d >= Tun.ArtilleryMinRef && d <= Tun.ArtilleryRef) inBand++;
                    }
                    var r = new TacticalRegion { Centre = p, Radius = Tun.StagingRadius };
                    r.Terms["approachCoverage"] = points.Count > 0 ? inBand / (float)points.Count : 0f;
                    r.Terms["directFireProtection"] = 1f - OpenShare(p, global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.ArtillerySupportReach, global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.ArtillerySupportRays);
                    r.Terms["trafficConflict"] = LaneConflict(p);
                    r.Terms["exits"] = EscapeRoutes(p, 12f) / 8f;
                    r.Score = 0.45f * r.Terms["approachCoverage"] + 0.25f * r.Terms["directFireProtection"] + 0.2f * r.Terms["exits"] - 0.2f * r.Terms["trafficConflict"];
                    if (best != null && r.Score <= best.Score) continue;
                    best = r;
                }
            if (best != null) best.Cells = ParkableCells(best.Centre, best.Radius);
            return best;
        }

        /// <summary>Spec H: where the defender falls back to, behind the objective from the attacker's primary arrival.</summary>
        private TacticalRegion? DefenderFallback(ObjectiveApproachSet set, TopologyAnchor o, float radius)
        {
            var primary = set.For(ApproachRole.Primary);
            if (primary == null) return null;
            var rad = primary.ArrivalBearingDeg * MathF.PI / 180f;
            var away = new Vector2(MathF.Sin(rad), MathF.Cos(rad));
            var cell = Map.Ground.NearestPassableCell(o.Position, Math.Max(SimTunables.Ai.Topology.NearestRings, (int)MathF.Ceiling(radius / Map.Cell)));
            var component = cell >= 0 ? Map.Ground.ComponentOfCell(cell) : 0;
            TacticalRegion? best = null;
            foreach (var extra in new[] { global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.DefenderFallbackExtra1, global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.DefenderFallbackExtra2, global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.DefenderFallbackExtra3 })
                for (var k = -3; k <= 3; k++)
                {
                    var angle = k * MathF.PI / 9f;
                    var dir = new Vector2(away.X * MathF.Cos(angle) - away.Y * MathF.Sin(angle), away.X * MathF.Sin(angle) + away.Y * MathF.Cos(angle));
                    var p = o.Position + dir * (radius + extra);
                    if (!PositionOk(p) || (component > 0 && Map.Ground.ComponentAt(p) != component)) continue;
                    if (Vector2.Distance(p, o.Position) < radius + Tun.StagingRadius * global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.DefenderFallbackStagingRadiusScale) continue;
                    var r = new TacticalRegion { Centre = p, Radius = Tun.StagingRadius };
                    r.Terms["cover"] = BesideCover(p) ? 1f : 1f - OpenShare(p, global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.DefenderFallbackReach, global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.DefenderFallbackRays);
                    r.Terms["lineBack"] = LineClear(p, o.Position) ? 1f : 0f;
                    r.Terms["exits"] = EscapeRoutes(p, 12f) / 8f;
                    r.Terms["offApproach"] = MathF.Min(1f, primary.DistanceTo(p) / global::MachineBrigade.Sim.Content.SimTunables.Maps.GameplayTopology.DefenderFallbackDistanceToDivisor);
                    r.Score = 0.35f * r.Terms["cover"] + 0.3f * r.Terms["lineBack"] + 0.2f * r.Terms["exits"] + 0.15f * r.Terms["offApproach"] - 0.01f * Math.Abs(k);
                    if (best != null && r.Score <= best.Score) continue;
                    best = r;
                }
            if (best != null) best.Cells = ParkableCells(best.Centre, best.Radius);
            return best;
        }

        private int ParkableCells(Vector2 centre, float radius)
        {
            var n = 0;
            var rr = (int)MathF.Ceiling(radius / Map.Cell);
            var (cx, cy) = Map.CellXY(centre);
            for (var y = cy - rr; y <= cy + rr; y++)
            for (var x = cx - rr; x <= cx + rr; x++)
            {
                if (!Map.InGrid(x, y)) continue;
                var i = y * Map.Columns + x;
                var c = Map.CellCentre(i);
                if (Map.Ground.Passable[i] && Vector2.Distance(c, centre) <= radius && !_world.LanesNoRebuild.NoParkAt(c)) n++;
            }
            return n;
        }
    }
}
