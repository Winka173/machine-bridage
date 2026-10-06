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
    /// GameplayTopology's ground layers, each built on first use (the AI's hot paths never ask for them; the map tools, tests and
    /// telemetry do): tactical lanes (spec F), size-class route audits (D1), spawn fairness (G), staging areas (I), tactical
    /// positions (J), breach metadata (O) and terrain semantics (P). All deterministic: fixed sample orders, ties by order.
    /// </summary>
    public sealed partial class GameplayTopology
    {
        private List<TacticalLane>? _lanes;
        private List<RouteAudit>? _routes;
        private List<SpawnFairness>? _fairness;
        private List<StagingArea>? _staging;
        private List<TacticalPosition>? _positions;
        private List<BreachInfo>? _breaches;
        private Dictionary<TerrainTag, int>? _terrainCells;

        public IReadOnlyList<TacticalLane> Lanes => _lanes ??= BuildLanes();
        public IReadOnlyList<RouteAudit> RouteAudits => _routes ??= BuildRouteAudits();
        public IReadOnlyList<SpawnFairness> SpawnFairness => _fairness ??= BuildFairness();
        public IReadOnlyList<StagingArea> StagingAreas => _staging ??= BuildStaging();
        public IReadOnlyList<TacticalPosition> Positions => _positions ??= BuildPositions();
        public IReadOnlyList<BreachInfo> Breaches => _breaches ??= BuildBreaches();

        /// <summary>Spec P: open ground cells per terrain tag.</summary>
        public IReadOnlyDictionary<TerrainTag, int> TerrainCells => _terrainCells ??= CountTerrain();

        // ================================================================================================ helpers

        private int CellsN => Map.Columns * Map.Rows;

        /// <summary>The largest clearance within <paramref name="r"/> cells of a cell (a shortest path hugs walls: the corridor's).</summary>
        private int WindowClearance(int cell, int r)
        {
            int cx = cell % Map.Columns, cy = cell / Map.Columns;
            var best = 0;
            for (var y = Math.Max(0, cy - r); y <= Math.Min(Map.Rows - 1, cy + r); y++)
            for (var x = Math.Max(0, cx - r); x <= Math.Min(Map.Columns - 1, cx + r); x++)
                best = Math.Max(best, Map.Clearance[y * Map.Columns + x]);
            return best;
        }

        private bool CoverAt(Vector2 p) => _world.Cover.IsBlocked(p);

        /// <summary>No fire-blocking cover on the straight line (1 m samples, ends excluded).</summary>
        private bool LineClear(Vector2 a, Vector2 b)
        {
            var d = Vector2.Distance(a, b);
            if (d < 1f) return true;
            var dir = (b - a) / d;
            for (var t = 1f; t < d - 0.5f; t += 1f)
                if (CoverAt(a + dir * t)) return false;
            return true;
        }

        /// <summary>Fire-blocking cover within 2 m (one of four bearings).</summary>
        private bool BesideCover(Vector2 p) =>
            CoverAt(p + new Vector2(2f, 0f)) || CoverAt(p - new Vector2(2f, 0f)) || CoverAt(p + new Vector2(0f, 2f)) || CoverAt(p - new Vector2(0f, 2f));

        /// <summary>Share of <paramref name="rays"/> bearings with no fire-blocking cover within <paramref name="reach"/> m (open exposure).</summary>
        private float OpenShare(Vector2 p, float reach, int rays)
        {
            var open = 0;
            for (var k = 0; k < rays; k++)
            {
                var dir = SimMath.Forward(k * MathF.PI * 2f / rays);
                var clear = true;
                for (var t = 2f; t <= reach; t += 2f)
                {
                    var q = p + dir * t;
                    if (!_world.Map.Contains(q)) break;
                    if (CoverAt(q))
                    {
                        clear = false;
                        break;
                    }
                }
                if (clear) open++;
            }
            return open / (float)Math.Max(1, rays);
        }

        /// <summary>The mean ray length (share of <paramref name="reach"/>) before cover or the map's edge (how much ground a point sees).</summary>
        private float SightArea(Vector2 p, float reach, int rays)
        {
            var sum = 0f;
            for (var k = 0; k < rays; k++)
            {
                var dir = SimMath.Forward(k * MathF.PI * 2f / rays);
                var t = 2f;
                for (; t <= reach; t += 2f)
                {
                    var q = p + dir * t;
                    if (!_world.Map.Contains(q) || CoverAt(q)) break;
                }
                sum += MathF.Min(t, reach) / reach;
            }
            return sum / Math.Max(1, rays);
        }

        private int CellNear(DomainGraph graph, Vector2 p, int extra = 0) =>
            graph.NearestPassableCell(p, SimTunables.Ai.Topology.NearestRings + extra);

        /// <summary>Four-neighbour steps over <paramref name="passable"/> from <paramref name="source"/> (-1: unreachable).</summary>
        private int[] Bfs(bool[] passable, int source)
        {
            var n = passable.Length;
            var dist = new int[n];
            for (var i = 0; i < n; i++) dist[i] = -1;
            if (source < 0 || source >= n || !passable[source]) return dist;
            var queue = new int[n];
            int head = 0, tail = 0;
            dist[source] = 0;
            queue[tail++] = source;
            var w = Map.Columns;
            while (head < tail)
            {
                var i = queue[head++];
                int x = i % w, y = i / w;
                var d = dist[i] + 1;
                if (x + 1 < w) Visit(i + 1);
                if (x > 0) Visit(i - 1);
                if (y + 1 < Map.Rows) Visit(i + w);
                if (y > 0) Visit(i - w);

                void Visit(int j)
                {
                    if (dist[j] >= 0 || !passable[j]) return;
                    dist[j] = d;
                    queue[tail++] = j;
                }
            }
            return dist;
        }

        /// <summary>A shortest four-neighbour route (cells, source first) down a distance field to <paramref name="target"/>.</summary>
        private List<int> WalkBack(int[] dist, int target)
        {
            var path = new List<int>();
            if (target < 0 || dist[target] < 0) return path;
            var at = target;
            path.Add(at);
            for (var guard = 0; guard < dist.Length && dist[at] > 0; guard++)
            {
                int x = at % Map.Columns, y = at / Map.Columns;
                var next = -1;
                if (x + 1 < Map.Columns && dist[at + 1] == dist[at] - 1) next = at + 1;
                else if (x > 0 && dist[at - 1] == dist[at] - 1) next = at - 1;
                else if (y + 1 < Map.Rows && dist[at + Map.Columns] == dist[at] - 1) next = at + Map.Columns;
                else if (y > 0 && dist[at - Map.Columns] == dist[at] - 1) next = at - Map.Columns;
                if (next < 0) break;
                at = next;
                path.Add(at);
            }
            path.Reverse();
            return path;
        }

        /// <summary>
        /// The cheapest eight-neighbour route (no corner cutting) over <paramref name="passable"/>: a cell costs its length times
        /// its terrain's path cost (TerrainRules, as the path finder), plus <paramref name="penalty"/>. Empty when unreachable.
        /// </summary>
        private List<int> CheapestPath(bool[] passable, int source, int target, float[]? penalty)
        {
            var path = new List<int>();
            var n = passable.Length;
            if (source < 0 || target < 0 || !passable[source] || !passable[target]) return path;
            var cost = new float[n];
            var parent = new int[n];
            for (var i = 0; i < n; i++)
            {
                cost[i] = float.PositiveInfinity;
                parent[i] = -1;
            }
            var heap = new MinHeap();
            cost[source] = 0f;
            heap.Push(0f, source);
            var w = Map.Columns;
            var grid = _world.Grid;
            const float Diagonal = 1.41421356f;
            while (heap.Count > 0)
            {
                var (c, i) = heap.Pop();
                if (c > cost[i]) continue;
                if (i == target) break;
                int x = i % w, y = i / w;
                for (var dy = -1; dy <= 1; dy++)
                for (var dx = -1; dx <= 1; dx++)
                {
                    if (dx == 0 && dy == 0) continue;
                    int nx = x + dx, ny = y + dy;
                    if (nx < 0 || ny < 0 || nx >= w || ny >= Map.Rows) continue;
                    var j = ny * w + nx;
                    if (!passable[j]) continue;
                    if (dx != 0 && dy != 0 && (!passable[y * w + nx] || !passable[ny * w + x])) continue;
                    var step = (dx != 0 && dy != 0 ? Diagonal : 1f) * Map.Cell * grid.StepCost(j) + (penalty != null ? penalty[j] : 0f);
                    var nc = c + step;
                    if (nc >= cost[j]) continue;
                    cost[j] = nc;
                    parent[j] = i;
                    heap.Push(nc, j);
                }
            }
            if (float.IsPositiveInfinity(cost[target])) return path;
            for (var at = target; at >= 0; at = parent[at]) path.Add(at);
            path.Reverse();
            return path;
        }

        /// <summary>A binary min-heap of (cost, cell); equal costs pop in push order's heap order (deterministic).</summary>
        private sealed class MinHeap
        {
            private readonly List<(float key, int value)> _items = new();
            public int Count => _items.Count;

            public void Push(float key, int value)
            {
                _items.Add((key, value));
                var i = _items.Count - 1;
                while (i > 0)
                {
                    var p = (i - 1) / 2;
                    if (_items[p].key <= key) break;
                    _items[i] = _items[p];
                    i = p;
                }
                _items[i] = (key, value);
            }

            public (float key, int value) Pop()
            {
                var top = _items[0];
                var last = _items[_items.Count - 1];
                _items.RemoveAt(_items.Count - 1);
                if (_items.Count == 0) return top;
                var i = 0;
                var n = _items.Count;
                while (true)
                {
                    var l = i * 2 + 1;
                    if (l >= n) break;
                    var r = l + 1;
                    var m = r < n && _items[r].key < _items[l].key ? r : l;
                    if (_items[m].key >= last.key) break;
                    _items[i] = _items[m];
                    i = m;
                }
                _items[i] = last;
                return top;
            }
        }

        /// <summary>Douglas-Peucker simplification of a cell route's centres (tolerance <paramref name="tolerance"/> m).</summary>
        private List<Vector2> Simplify(List<int> cells, float tolerance)
        {
            var pts = new List<Vector2>(cells.Count);
            foreach (var c in cells) pts.Add(Map.CellCentre(c));
            if (pts.Count <= 2) return pts;
            var keep = new bool[pts.Count];
            keep[0] = keep[pts.Count - 1] = true;
            var stack = new Stack<(int, int)>();
            stack.Push((0, pts.Count - 1));
            while (stack.Count > 0)
            {
                var (a, b) = stack.Pop();
                var best = -1;
                var bestD = tolerance;
                var ab = pts[b] - pts[a];
                var len = ab.Length();
                for (var i = a + 1; i < b; i++)
                {
                    var d = len < 1e-4f ? Vector2.Distance(pts[i], pts[a]) : MathF.Abs(Cross(ab, pts[i] - pts[a])) / len;
                    if (d <= bestD) continue;
                    bestD = d;
                    best = i;
                }
                if (best < 0) continue;
                keep[best] = true;
                stack.Push((a, best));
                stack.Push((best, b));
            }
            var output = new List<Vector2>();
            for (var i = 0; i < pts.Count; i++)
                if (keep[i]) output.Add(pts[i]);
            return output;
        }

        private static float Cross(Vector2 a, Vector2 b) => a.X * b.Y - a.Y * b.X;

        private static float Percentile(List<float> values, float p)
        {
            if (values.Count == 0) return 0f;
            var s = new List<float>(values);
            s.Sort();
            return s[Math.Min(s.Count - 1, (int)(p * s.Count))];
        }

        /// <summary>The objectives a route serves: capture points, camps' HQs and the fortress HQ, with their radii.</summary>
        private List<(TopologyAnchor anchor, float radius)> Objectives()
        {
            var list = new List<(TopologyAnchor, float)>();
            foreach (var a in _anchors)
            {
                if (a.Kind == AnchorKind.Objective)
                {
                    var radius = 6f;
                    foreach (var p in _world.Map.Points)
                        if ("point_" + p.Id == a.Id) radius = MathF.Max(2f, p.Radius);
                    list.Add((a, radius));
                }
                else if (a.Kind == AnchorKind.Base || a.Id == "fortress_hq") list.Add((a, 10f));
            }
            return list;
        }

        private TopologyAnchor? Rally(int team) => AnchorOf("rally_" + team);

        // ================================================================================================ lanes (spec F)

        private List<TacticalLane> BuildLanes()
        {
            var lanes = new List<TacticalLane>();
            var near = new List<HashSet<int>>();
            var ground = Map.Ground.Passable;
            var r0 = Rally(0);
            var r1 = Rally(1);
            var c0 = r0 != null ? CellNear(Map.Ground, r0.Position) : -1;
            var c1 = r1 != null ? CellNear(Map.Ground, r1.Position) : -1;
            var objectives = Objectives();
            var penalty = new float[CellsN];
            List<Vector2>? mainPoints = null;
            var mainLength = 0f;
            var span = MathF.Min(_world.Map.Width, _world.Map.Length);
            if (c0 >= 0 && c1 >= 0 && Map.Ground.ComponentOfCell(c0) == Map.Ground.ComponentOfCell(c1))
            {
                for (var k = 0; k <= Math.Max(0, Tun.LaneAlternatives); k++)
                {
                    var cells = CheapestPath(ground, c0, c1, k == 0 ? null : penalty);
                    if (cells.Count == 0) break;
                    var set = Near(cells);
                    var shared = 0;
                    foreach (var c in cells)
                        foreach (var s in near)
                            if (s.Contains(c))
                            {
                                shared++;
                                break;
                            }
                    foreach (var c in set) penalty[c] += Tun.LanePenalty;
                    if (k > 0 && shared > cells.Count / 2) continue;
                    var kind = LaneKind.Main;
                    if (k > 0)
                    {
                        var offset = 0f;
                        foreach (var c in cells) offset = MathF.Max(offset, PolylineDistance(mainPoints!, Map.CellCentre(c)));
                        kind = offset >= 0.2f * span ? LaneKind.Flank : LaneKind.Secondary;
                    }
                    var lane = MakeLane(k == 0 ? "main" : $"alt{k}", kind, "rally_0", "rally_1", cells, objectives);
                    if (k == 0)
                    {
                        mainPoints = new List<Vector2>(lane.Points);
                        mainLength = lane.LengthM;
                    }
                    else if (lane.MinWidth < Class(VehicleSizeClass.Light).ReferenceWidth) continue;
                    lanes.Add(lane);
                    near.Add(set);
                }
            }
            // Each side's way to each objective, unless a lane found already runs it (70 % shared).
            for (var team = 0; team <= 1; team++)
            {
                var rally = Rally(team);
                var from = rally != null ? CellNear(Map.Ground, rally.Position) : -1;
                if (from < 0) continue;
                foreach (var (o, radius) in objectives)
                {
                    if (o.Kind == AnchorKind.Base && o.Team == team) continue;
                    var to = CellNear(Map.Ground, o.Position, (int)MathF.Ceiling(radius / Map.Cell));
                    if (to < 0 || Map.Ground.ComponentOfCell(to) != Map.Ground.ComponentOfCell(from)) continue;
                    var cells = CheapestPath(ground, from, to, null);
                    if (cells.Count == 0) continue;
                    var shared = 0;
                    foreach (var c in cells)
                        foreach (var s in near)
                            if (s.Contains(c))
                            {
                                shared++;
                                break;
                            }
                    if (lanes.Count > 0 && shared >= cells.Count * 7 / 10) continue;
                    var lane = MakeLane($"obj{team}_{o.Id}", lanes.Count == 0 ? LaneKind.Main : LaneKind.Secondary, "rally_" + team, o.Id, cells, objectives);
                    lanes.Add(lane);
                    near.Add(Near(cells));
                }
                // Service: the spawn to its own camp's HQ.
                if (AnchorOf("hq_" + team) is { } hq && Vector2.Distance(hq.Position, rally!.Position) > 20f)
                {
                    var to = CellNear(Map.Ground, hq.Position, 4);
                    var cells = to >= 0 ? CheapestPath(ground, from, to, null) : new List<int>();
                    if (cells.Count > 0) lanes.Add(MakeLane($"service{team}", LaneKind.Service, "rally_" + team, hq.Id, cells, objectives));
                }
            }
            // Boss corridors: the map's fixed boss routes (not the rails), and the boss-size way between the camps.
            foreach (var (name, line) in SortedRoutes(_world.Map))
            {
                if (name == "rail" || line.Count < 2) continue;
                var cells = new List<int>();
                for (var i = 0; i + 1 < line.Count; i++)
                {
                    var d = Vector2.Distance(line[i], line[i + 1]);
                    for (var t = 0f; t <= d; t += Map.Cell * 0.5f)
                    {
                        var c = Map.CellIndex(Vector2.Lerp(line[i], line[i + 1], d > 0f ? t / d : 0f));
                        if (c >= 0 && (cells.Count == 0 || cells[cells.Count - 1] != c)) cells.Add(c);
                    }
                }
                if (cells.Count > 1) lanes.Add(MakeLane("route_" + name, LaneKind.BossCorridor, $"route_{name}_start", $"route_{name}_end", cells, objectives));
            }
            var boss = ClassGraph(VehicleSizeClass.Boss);
            if (r0 != null && r1 != null)
            {
                var need = Class(VehicleSizeClass.Boss).ClearanceCells;
                var b0 = CellNear(boss, r0.Position, need);
                var b1 = CellNear(boss, r1.Position, need);
                if (b0 >= 0 && b1 >= 0 && boss.ComponentOfCell(b0) == boss.ComponentOfCell(b1))
                {
                    var cells = CheapestPath(boss.Passable, b0, b1, null);
                    if (cells.Count > 0) lanes.Add(MakeLane("boss", LaneKind.BossCorridor, "rally_0", "rally_1", cells, objectives));
                }
            }
            _ = mainLength;
            return lanes;
        }

        private HashSet<int> Near(List<int> cells)
        {
            var set = new HashSet<int>();
            foreach (var c in cells)
            {
                int x = c % Map.Columns, y = c / Map.Columns;
                for (var dy = -2; dy <= 2; dy++)
                for (var dx = -2; dx <= 2; dx++)
                {
                    int nx = x + dx, ny = y + dy;
                    if (nx >= 0 && ny >= 0 && nx < Map.Columns && ny < Map.Rows) set.Add(ny * Map.Columns + nx);
                }
            }
            return set;
        }

        private static float PolylineDistance(List<Vector2> points, Vector2 p)
        {
            var best = float.MaxValue;
            for (var i = 0; i + 1 < points.Count; i++)
            {
                var a = points[i];
                var ab = points[i + 1] - a;
                var len2 = ab.LengthSquared();
                var t = len2 > 1e-6f ? Math.Clamp(Vector2.Dot(p - a, ab) / len2, 0f, 1f) : 0f;
                best = MathF.Min(best, Vector2.Distance(p, a + ab * t));
            }
            return points.Count == 1 ? Vector2.Distance(points[0], p) : best;
        }

        private TacticalLane MakeLane(string id, LaneKind kind, string from, string to, List<int> cells, List<(TopologyAnchor anchor, float radius)> objectives)
        {
            var widths = new List<float>(cells.Count);
            var minClear = int.MaxValue;
            var speed = 0f;
            var grid = _world.Grid;
            var length = 0f;
            for (var i = 0; i < cells.Count; i++)
            {
                var c = cells[i];
                var clear = WindowClearance(c, 2);
                widths.Add(WidthOfClearance(clear));
                minClear = Math.Min(minClear, clear);
                speed += 1f / MathF.Max(0.1f, grid.StepCost(c));
                if (i > 0) length += Vector2.Distance(Map.CellCentre(cells[i - 1]), Map.CellCentre(c));
            }
            var lane = new TacticalLane
            {
                Id = id,
                Kind = kind,
                From = from,
                To = to,
                Points = Simplify(cells, 2f),
                LengthM = length,
                LaneWidth = Percentile(widths, 0.1f),
                MinWidth = widths.Count > 0 ? Min(widths) : 0f,
                ParkingForbidden = kind is LaneKind.Main or LaneKind.BossCorridor,
            };
            var support = VehicleSizeClass.Light;
            for (var k = 0; k < 5; k++)
                if (_classes[k].ClearanceCells <= Math.Max(1, minClear)) support = (VehicleSizeClass)k;
            lane.VehicleClassSupport = support;
            var medium = Class(VehicleSizeClass.Medium);
            lane.ExpectedTravelSpeed = medium.MedianSpeed * (cells.Count > 0 ? speed / cells.Count : 1f);
            lane.Directionality = lane.MinWidth >= 2f * (medium.MedianWidth + Tun.SeparationMargin) ? LaneDirectionality.TwoWay : LaneDirectionality.Alternating;
            var chokes = new List<int>();
            var capacity = float.PositiveInfinity;
            foreach (var ch in _chokes)
                foreach (var c in cells)
                    if (ch.Contains(Map.CellCentre(c)))
                    {
                        chokes.Add(ch.Id);
                        capacity = MathF.Min(capacity, ch.EstimatedThroughput);
                        break;
                    }
            lane.ChokeDependency = chokes;
            if (float.IsPositiveInfinity(capacity))
            {
                var through = Math.Max(1, (int)MathF.Floor((lane.LaneWidth - 2f * SimWorld.ObstacleClearance) / MathF.Max(1f, medium.MedianWidth + 1f)));
                capacity = through * MathF.Max(0.5f, medium.MedianSpeed) / MathF.Max(2f, medium.ReferenceLength + 4f);
            }
            lane.TrafficCapacity = capacity;
            var covered = new List<string>();
            foreach (var (o, radius) in objectives)
                if (lane.DistanceTo(o.Position) <= radius + 20f) covered.Add(o.Id);
            lane.ObjectiveCoverage = covered;
            return lane;
        }

        private static bool Has(IReadOnlyList<string> list, string id)
        {
            foreach (var s in list)
                if (s == id) return true;
            return false;
        }

        private static float Min(List<float> list)
        {
            var m = float.MaxValue;
            foreach (var v in list) m = MathF.Min(m, v);
            return m;
        }

        // ================================================================================================ route audits (spec D1)

        private List<RouteAudit> BuildRouteAudits()
        {
            var list = new List<RouteAudit>();
            var objectives = Objectives();
            for (var team = 0; team <= 1; team++)
            {
                if (Rally(team) is not { } rally || rally.Domain != MobilityDomain.Ground) continue;
                foreach (var (o, radius) in objectives)
                {
                    if (o.Kind == AnchorKind.Base && o.Team == team) continue;
                    for (var k = 0; k < 5; k++)
                        list.Add(Audit(rally, o, radius, (VehicleSizeClass)k));
                }
            }
            return list;
        }

        private RouteAudit Audit(TopologyAnchor from, TopologyAnchor to, float radius, VehicleSizeClass cls)
        {
            var info = Class(cls);
            var graph = ClassGraph(cls);
            var audit = new RouteAudit { From = from.Id, To = to.Id, Class = cls };
            var source = CellNear(graph, from.Position, info.ClearanceCells);
            var target = graph.NearestPassableCell(to.Position, Math.Max(SimTunables.Ai.Topology.NearestRings, (int)MathF.Ceiling(radius / Map.Cell)) + info.ClearanceCells);
            if (source < 0 || target < 0) return audit;
            var dist = graph.DistancesFrom(source);
            if (dist[target] < 0) return audit;
            audit.Reachable = true;
            var path = WalkBack(dist, target);
            audit.LengthM = (path.Count - 1) * Map.Cell;
            var minWidth = float.PositiveInfinity;
            var growth = SimWorld.ObstacleClearance;
            var swingCells = Math.Max(2, (int)MathF.Ceiling(info.TurnRadius / Map.Cell));
            for (var i = 0; i < path.Count; i++)
            {
                var c = path[i];
                var clear = WindowClearance(c, 2);
                if (i >= 3 && i < path.Count - 3) minWidth = MathF.Min(minWidth, WidthOfClearance(clear));
                if (i >= 4 && i + 4 < path.Count)
                {
                    var din = Map.CellCentre(c) - Map.CellCentre(path[i - 4]);
                    var dout = Map.CellCentre(path[i + 4]) - Map.CellCentre(c);
                    var cos = Vector2.Dot(din, dout) / MathF.Max(1e-3f, din.Length() * dout.Length());
                    if (cos < MathF.Cos(50f * MathF.PI / 180f))
                    {
                        audit.MinTurnSpaceM = MathF.Min(audit.MinTurnSpaceM, (clear - 0.5f) * Map.Cell + growth);
                        // Lane W2-A: a hull swings wide through the corner's open ground (the best clearance within its pivot
                        // radius of the corner cell), where a shortest path hugs the inside of the turn.
                        var swing = WindowClearance(c, swingCells);
                        audit.SwingTurnSpaceM = MathF.Min(audit.SwingTurnSpaceM, (swing - 0.5f) * Map.Cell + growth);
                    }
                }
                var p = Map.CellCentre(c);
                foreach (var line in _world.Map.Walls)
                    if (Vector2.Distance(line.Gate, p) <= line.GateWidth * 0.5f + 1f) audit.GateMinWidthM = MathF.Min(audit.GateMinWidthM, line.GateWidth);
                foreach (var ch in _chokes)
                {
                    if (!ch.Contains(p)) continue;
                    if (ch.Type == ChokeType.Gate) audit.GateMinWidthM = MathF.Min(audit.GateMinWidthM, ch.UsableWidthM);
                    if (ch.Type is ChokeType.Bridge or ChokeType.RiverCrossing) audit.BridgeMinWidthM = MathF.Min(audit.BridgeMinWidthM, ch.UsableWidthM);
                }
            }
            audit.MinClearWidthM = float.IsPositiveInfinity(minWidth) ? WidthOfClearance(info.ClearanceCells) : minWidth;
            audit.TurnsFit = audit.MinTurnSpaceM >= info.TurnRadius;
            audit.TurnsFitSwing = audit.SwingTurnSpaceM >= info.TurnRadius;
            return audit;
        }

        // ================================================================================================ spawn fairness (spec G)

        private List<SpawnFairness> BuildFairness()
        {
            var list = new List<SpawnFairness>();
            var symmetric = _world.Map.AsymmetryReason == null;
            for (var team = 0; team <= 1; team++)
            {
                if (Rally(team) is not { } own || Rally(1 - team) is not { } enemy) continue;
                if (own.Domain != MobilityDomain.Ground) continue;
                list.Add(Fairness(own, enemy, team));
            }
            _ = symmetric;
            return list;
        }

        private SpawnFairness Fairness(TopologyAnchor own, TopologyAnchor enemy, int team)
        {
            var f = new SpawnFairness { SpawnId = own.Id, Team = team, Position = own.Position };
            var zone = _spawnZones.Find(z => z.Team == team);
            var clearRadius = zone.Team == team ? zone.ClearRadius : SimTunables.Ai.Traffic.SpawnClearRadius;
            var ownCell = CellNear(Map.Ground, own.Position);
            var enemyCell = CellNear(Map.Ground, enemy.Position);
            var enemyDist = enemyCell >= 0 ? Map.Ground.DistancesFrom(enemyCell) : new int[CellsN];
            if (enemyCell < 0)
                for (var i = 0; i < enemyDist.Length; i++) enemyDist[i] = -1;
            var ownDist = ownCell >= 0 ? Map.Ground.DistancesFrom(ownCell) : enemyDist;
            var keepOut = clearRadius * 1.5f;

            bool Visible(Vector2 s)
            {
                for (var k = 0; k < 32; k++)
                {
                    var dir = SimMath.Forward(k * MathF.PI / 16f);
                    for (var t = Map.Cell; t <= Tun.DirectFireRef; t += Map.Cell)
                    {
                        var q = s + dir * t;
                        if (CoverAt(q)) break;
                        var c = Map.CellIndex(q);
                        if (c < 0) break;
                        // Ground the enemy holds at the start: it gets there before this side does (path distance), off the clear zone.
                        if (enemyDist[c] >= 0 && (ownDist[c] < 0 || enemyDist[c] < ownDist[c]) && Vector2.Distance(q, own.Position) > keepOut) return true;
                    }
                }
                return false;
            }

            // The clear zone's open ground.
            int zoneCells = 0, zoneSeen = 0, zoneShelled = 0;
            var r = (int)MathF.Ceiling(clearRadius / Map.Cell);
            var (cx, cy) = Map.CellXY(own.Position);
            for (var y = cy - r; y <= cy + r; y++)
            for (var x = cx - r; x <= cx + r; x++)
            {
                if (!Map.InGrid(x, y)) continue;
                var i = y * Map.Columns + x;
                if (!Map.Ground.Passable[i]) continue;
                var p = Map.CellCentre(i);
                if (Vector2.Distance(p, own.Position) > clearRadius) continue;
                zoneCells++;
                if (Visible(p)) zoneSeen++;
                if (Vector2.Distance(p, enemy.Position) <= Tun.ArtilleryRef) zoneShelled++;
            }
            f.EnemyDirectLosAtSpawn = zoneCells > 0 ? zoneSeen / (float)zoneCells : 0f;
            f.EnemyArtilleryCoverageAtSpawn = zoneCells > 0 ? zoneShelled / (float)zoneCells : 0f;
            var medium = Class(VehicleSizeClass.Medium);
            var footprint = (medium.MedianWidth + Tun.SeparationMargin) * (medium.ReferenceLength + Tun.SeparationMargin);
            f.SpawnQueueCapacity = (int)(zoneCells * Map.Cell * Map.Cell / MathF.Max(1f, footprint));

            // The exit ring: runs of open samples are the exits.
            const int Samples = 72;
            var ring = new bool[Samples];
            var seen = 0;
            var open = 0;
            for (var k = 0; k < Samples; k++)
            {
                var p = own.Position + SimMath.Forward(k * MathF.PI * 2f / Samples) * Tun.SpawnRing;
                ring[k] = Map.Ground.IsPassable(p);
                if (!ring[k]) continue;
                open++;
                if (Visible(p)) seen++;
            }
            f.EnemyDirectLosAtExit = open > 0 ? seen / (float)open : 0f;
            var arc = MathF.PI * 2f * Tun.SpawnRing / Samples;
            if (open == Samples)
            {
                f.SpawnExitWidthM = float.PositiveInfinity;
                f.NarrowestExitM = float.PositiveInfinity;
                f.AlternateExitCount = 3;
            }
            else
            {
                var runs = new List<int>();
                var start = Array.IndexOf(ring, false);
                var run = 0;
                for (var j = 1; j <= Samples; j++)
                {
                    var k = (start + j) % Samples;
                    if (ring[k]) run++;
                    else if (run > 0)
                    {
                        runs.Add(run);
                        run = 0;
                    }
                }
                if (run > 0) runs.Add(run);
                var total = 0f;
                var narrowest = float.PositiveInfinity;
                foreach (var n in runs)
                {
                    var w = n * arc + 2f * SimWorld.ObstacleClearance;
                    total += w;
                    narrowest = MathF.Min(narrowest, w);
                }
                f.SpawnExitWidthM = total;
                f.NarrowestExitM = runs.Count > 0 ? narrowest : 0f;
                f.AlternateExitCount = Math.Max(0, runs.Count - 1);
            }

            // First cover and the two ETAs.
            if (ownCell >= 0)
            {
                var dist = Map.Ground.DistancesFrom(ownCell);
                var best = int.MaxValue;
                var reach = (int)MathF.Ceiling(100f / Map.Cell);
                var (ox, oy) = Map.CellXY(own.Position);
                for (var y = oy - reach; y <= oy + reach; y++)
                for (var x = ox - reach; x <= ox + reach; x++)
                {
                    if (!Map.InGrid(x, y)) continue;
                    var i = y * Map.Columns + x;
                    if (dist[i] < 0 || dist[i] >= best) continue;
                    if (BesideCover(Map.CellCentre(i))) best = dist[i];
                }
                f.SpawnToFirstCoverM = best == int.MaxValue ? float.PositiveInfinity : best * Map.Cell;
                var speed = MathF.Max(0.5f, medium.MedianSpeed);
                var detour = SimTunables.Ai.Feasibility.TravelDetour;
                f.EnemyRushEta = enemyCell >= 0 && dist[enemyCell] >= 0 ? dist[enemyCell] * Map.Cell * detour / speed : float.PositiveInfinity;
                var objective = float.PositiveInfinity;
                foreach (var (o, radius) in Objectives())
                {
                    if (o.Kind == AnchorKind.Base && o.Team == team) continue;
                    var c = Map.Ground.NearestPassableCell(o.Position, Math.Max(SimTunables.Ai.Topology.NearestRings, (int)MathF.Ceiling(radius / Map.Cell)));
                    if (c >= 0 && dist[c] >= 0) objective = MathF.Min(objective, dist[c] * Map.Cell * detour / speed);
                }
                f.FriendlyObjectiveEta = objective;
            }
            else
            {
                f.SpawnToFirstCoverM = f.EnemyRushEta = f.FriendlyObjectiveEta = float.PositiveInfinity;
            }

            // Spec G1.
            var heavy = Class(VehicleSizeClass.Heavy);
            var super = Class(VehicleSizeClass.SuperHeavy);
            if (open > 0 && f.EnemyDirectLosAtExit >= Tun.FullExposureShare) f.Flags.Add("FULL_EXIT_DIRECT_FIRE");
            // One way out that is also narrow (a wide single arc by the map's corner is no choke point).
            if (open > 0 && open < Samples && f.AlternateExitCount == 0 && f.NarrowestExitM < 3f * (heavy.ReferenceWidth + Tun.SeparationMargin)) f.Flags.Add("SINGLE_EXIT");
            if (open > 0 && f.AlternateExitCount == 0 && f.NarrowestExitM < 2f * (heavy.ReferenceWidth + Tun.SeparationMargin)) f.Flags.Add("SINGLE_BLOCKER_SEALS");
            if (open > 0 && f.NarrowestExitM < super.ReferenceWidth + 2f * Tun.SideClearance) f.Flags.Add("EXIT_NARROWER_THAN_LARGEST");
            if (open == 0) f.Flags.Add("NO_EXIT");
            if (f.EnemyArtilleryCoverageAtSpawn >= 0.95f && f.AlternateExitCount == 0) f.Flags.Add("ARTILLERY_FULL_COVER");
            return f;
        }

        // ================================================================================================ staging (spec I)

        private List<StagingArea> BuildStaging()
        {
            var list = new List<StagingArea>();
            var objectives = Objectives();
            var light = Class(VehicleSizeClass.Light);
            var heavy = Class(VehicleSizeClass.Heavy);
            for (var team = 0; team <= 1; team++)
            {
                if (Rally(team) is not { } rally) continue;
                foreach (var (o, radius) in objectives)
                {
                    if (o.Kind == AnchorKind.Base && o.Team == team) continue;
                    // The lane this side takes there (its own objective lane, else the main), walked back from the objective.
                    TacticalLane? lane = null;
                    foreach (var l in Lanes)
                        if (l.To == o.Id && l.From == rally.Id) lane = l;
                    if (lane == null)
                        foreach (var l in Lanes)
                            if (l.Kind == LaneKind.Main && Has(l.ObjectiveCoverage, o.Id)) lane = l;
                    if (lane == null || lane.Points.Count < 2) continue;
                    var standoff = radius + Tun.StagingDistance;
                    var seed = PointBefore(lane, o.Position, standoff, lane.From == rally.Id ? rally.Position : (Vector2?)null);
                    if (seed is not { } s) continue;
                    if (!FindStaging(s, o, radius, out var centre)) continue;
                    var area = 0;
                    var covered = 0;
                    var rr = (int)MathF.Ceiling(Tun.StagingRadius / Map.Cell);
                    var (cx, cy) = Map.CellXY(centre);
                    for (var y = cy - rr; y <= cy + rr; y++)
                    for (var x = cx - rr; x <= cx + rr; x++)
                    {
                        if (!Map.InGrid(x, y)) continue;
                        var i = y * Map.Columns + x;
                        if (!Map.Ground.Passable[i] || Vector2.Distance(Map.CellCentre(i), centre) > Tun.StagingRadius) continue;
                        area++;
                        if (BesideCover(Map.CellCentre(i))) covered++;
                    }
                    var m2 = area * Map.Cell * Map.Cell;
                    var lanesNear = 0;
                    foreach (var l in Lanes)
                        if (l.DistanceTo(centre) <= 25f) lanesNear++;
                    var objectiveVisible = Vector2.Distance(centre, o.Position) <= Tun.DirectFireRef && LineClear(centre, o.Position);
                    list.Add(new StagingArea
                    {
                        Id = $"stage{team}_{o.Id}",
                        Centre = centre,
                        Radius = Tun.StagingRadius,
                        Team = team,
                        Objective = o.Id,
                        CapacityLight = (int)(m2 / MathF.Max(1f, (light.MedianWidth + Tun.SeparationMargin) * (light.ReferenceLength + Tun.SeparationMargin))),
                        CapacityHeavy = (int)(m2 / MathF.Max(1f, (heavy.MedianWidth + Tun.SeparationMargin) * (heavy.ReferenceLength + Tun.SeparationMargin))),
                        CoverScore = area > 0 ? covered / (float)area : 0f,
                        ThreatExposure = objectiveVisible ? 1f : OpenShare(centre, Tun.DirectFireRef, 16) * 0.5f,
                        DistanceToObjective = Vector2.Distance(centre, o.Position),
                        LanesAvailable = lanesNear,
                    });
                }
            }
            return list;
        }

        /// <summary>The point on a lane <paramref name="standoff"/> m before the target (walking from the lane's far end at it).</summary>
        private static Vector2? PointBefore(TacticalLane lane, Vector2 target, float standoff, Vector2? from)
        {
            var pts = new List<Vector2>(lane.Points);
            // Walk from the target end back towards the other end.
            if (Vector2.Distance(pts[0], target) < Vector2.Distance(pts[pts.Count - 1], target)) pts.Reverse();
            _ = from;
            for (var i = pts.Count - 1; i > 0; i--)
            {
                var a = pts[i - 1];
                var b = pts[i];
                if (Vector2.Distance(a, target) < standoff) continue;
                // a is beyond the standoff, b inside: the crossing on this segment.
                var lo = 0f;
                var hi = 1f;
                for (var k = 0; k < 20; k++)
                {
                    var mid = (lo + hi) * 0.5f;
                    if (Vector2.Distance(Vector2.Lerp(a, b, mid), target) >= standoff) lo = mid;
                    else hi = mid;
                }
                return Vector2.Lerp(a, b, lo);
            }
            return null;
        }

        /// <summary>Spec I's rules round a seed: open, no-parking free, off chokes, spawn zones, capture circles and no-parking lanes.</summary>
        private bool FindStaging(Vector2 seed, TopologyAnchor objective, float radius, out Vector2 centre)
        {
            // Lane W2-A (spec I "not inside immediate direct-fire threat if avoidable"): first out of a direct line of fire from
            // the objective (within the direct-fire reference), then anywhere the rules allow.
            for (var pass = 0; pass < 2; pass++)
                for (var ring = 0; ring <= 10; ring++)
                {
                    var samples = ring == 0 ? 1 : 8 * ring;
                    for (var k = 0; k < samples; k++)
                    {
                        var p = ring == 0 ? seed : seed + SimMath.Forward(k * MathF.PI * 2f / samples) * (ring * 2f);
                        if (!StagingOk(p, objective, radius)) continue;
                        if (pass == 0 && Vector2.Distance(p, objective.Position) <= Tun.DirectFireRef && LineClear(p, objective.Position)) continue;
                        centre = p;
                        return true;
                    }
                }
            centre = seed;
            return false;
        }

        private bool StagingOk(Vector2 p, TopologyAnchor objective, float radius)
        {
            if (!_world.Map.InsideBoundary(p) || !Map.Ground.IsPassable(p) || _world.LanesNoRebuild.NoParkAt(p)) return false;
            if (InSpawnClearZone(p) || Vector2.Distance(p, objective.Position) < radius + Tun.StagingRadius) return false;
            foreach (var c in _chokes)
                if (c.Contains(p) || Vector2.Distance(c.Centre, p) < c.Reach) return false;
            foreach (var l in Lanes)
                if (l.ParkingForbidden && l.DistanceTo(p) < 6f) return false;
            var cell = Map.Ground.NearestPassableCell(objective.Position, Math.Max(SimTunables.Ai.Topology.NearestRings, (int)MathF.Ceiling(radius / Map.Cell)));
            return cell >= 0 && Map.Ground.ComponentAt(p) == Map.Ground.ComponentOfCell(cell);
        }

        // ================================================================================================ positions (spec J)

        private List<TacticalPosition> BuildPositions()
        {
            var list = new List<TacticalPosition>();
            DirectFirePositions(list);
            ArtilleryPockets(list);
            ReconPositions(list);
            HullDownPositions(list);
            return list;
        }

        /// <summary>A position may be generated here: inside the outline, open, parkable, off spawn zones (shared rule of every kind).</summary>
        private bool PositionOk(Vector2 p) =>
            _world.Map.InsideBoundary(p) && Map.Ground.IsPassable(p) && !_world.LanesNoRebuild.NoParkAt(p) && !InSpawnClearZone(p);

        private float LaneConflict(Vector2 p)
        {
            var flags = _world.LanesNoRebuild.At(p);
            return (flags & LaneFlags.Route) != 0 ? 1f : (flags & LaneFlags.Road) != 0 ? 0.5f : 0f;
        }

        private float DirectRange()
        {
            if (_world.Catalog.Vehicles.TryGetValue("main_battle_tank", out var mbt) && mbt.Weapon.Range > 0f) return mbt.Weapon.Range;
            return 32f;
        }

        private static void Keep(List<TacticalPosition> into, List<TacticalPosition> candidates, int count)
        {
            candidates.Sort((a, b) =>
            {
                var c = b.Score.CompareTo(a.Score);
                return c != 0 ? c : string.CompareOrdinal(a.Id, b.Id);
            });
            var kept = new List<TacticalPosition>();
            foreach (var c in candidates)
            {
                var far = true;
                foreach (var k in kept)
                    if (Vector2.Distance(k.Position, c.Position) < Tun.PositionSpacing) far = false;
                if (!far) continue;
                kept.Add(c);
                if (kept.Count >= count) break;
            }
            for (var i = 0; i < kept.Count; i++) kept[i].Id = $"{kept[i].Id.Split('#')[0]}#{i}";
            into.AddRange(kept);
        }

        private void DirectFirePositions(List<TacticalPosition> list)
        {
            var range = DirectRange();
            foreach (var (o, radius) in Objectives())
            {
                var candidates = new List<TacticalPosition>();
                foreach (var f in new[] { 0.6f, 0.8f, 0.95f })
                {
                    var d = MathF.Max(radius + 4f, range * f);
                    for (var k = 0; k < 24; k++)
                    {
                        var p = o.Position + SimMath.Forward(k * MathF.PI / 12f) * d;
                        if (!PositionOk(p) || !LineClear(p, o.Position)) continue;
                        var t = new TacticalPosition { Id = $"df_{o.Id}#", Kind = TacticalPositionKind.DirectFire, Position = p, Subject = o.Id };
                        t.Terms["los"] = 1f;
                        t.Terms["range"] = MathF.Max(0f, 1f - MathF.Abs(d - range * 0.8f) / (range * 0.35f));
                        t.Terms["cover"] = BesideCover(p) ? 1f : 0f;
                        t.Terms["hullDown"] = LowCoverBetween(p, o.Position) ? 1f : 0f;
                        t.Terms["escape"] = EscapeRoutes(p, 12f) / 8f;
                        t.Terms["friendlyObstruction"] = LaneConflict(p);
                        t.Terms["threat"] = OpenShare(p, 40f, 16);
                        t.Score = 0.3f * t.Terms["los"] + 0.2f * t.Terms["range"] + 0.15f * t.Terms["cover"] + 0.1f * t.Terms["hullDown"] +
                                  0.15f * t.Terms["escape"] - 0.1f * t.Terms["friendlyObstruction"] - 0.1f * t.Terms["threat"];
                        candidates.Add(t);
                    }
                }
                Keep(list, candidates, Math.Max(1, Tun.PositionsPerObjective));
            }
        }

        private void ArtilleryPockets(List<TacticalPosition> list)
        {
            var objectives = Objectives();
            for (var team = 0; team <= 1; team++)
            {
                if (Rally(team) is not { } rally || Rally(1 - team) is not { } enemy) continue;
                var enemyLanes = new List<Vector2>();
                foreach (var l in Lanes)
                    if (l.From == enemy.Id || l.To == enemy.Id) enemyLanes.AddRange(l.Points);
                var candidates = new List<TacticalPosition>();
                foreach (var d in new[] { 40f, 60f, 80f })
                    for (var k = 0; k < 16; k++)
                    {
                        var p = rally.Position + SimMath.Forward(k * MathF.PI / 8f) * d;
                        if (!PositionOk(p)) continue;
                        var forbidden = false;
                        foreach (var l in Lanes)
                            if (l.ParkingForbidden && l.DistanceTo(p) < 6f) forbidden = true;
                        if (forbidden) continue;
                        int inBand = 0, n = 0;
                        var nearest = float.PositiveInfinity;
                        foreach (var (o, _) in objectives)
                        {
                            if (o.Kind == AnchorKind.Base && o.Team == team) continue;
                            n++;
                            var dd = Vector2.Distance(p, o.Position);
                            nearest = MathF.Min(nearest, dd);
                            if (dd >= Tun.ArtilleryMinRef + 5f && dd <= Tun.ArtilleryRef) inBand++;
                        }
                        var approach = 0;
                        foreach (var q in enemyLanes)
                        {
                            var dd = Vector2.Distance(p, q);
                            if (dd >= Tun.ArtilleryMinRef && dd <= Tun.ArtilleryRef) approach++;
                        }
                        var t = new TacticalPosition { Id = $"art{team}#", Kind = TacticalPositionKind.ArtilleryPocket, Position = p, Team = team, Subject = rally.Id };
                        t.Terms["objectiveCoverage"] = n > 0 ? inBand / (float)n : 0f;
                        t.Terms["approachCoverage"] = enemyLanes.Count > 0 ? approach / (float)enemyLanes.Count : 0f;
                        t.Terms["minRangeSafety"] = float.IsPositiveInfinity(nearest) ? 1f : MathF.Min(1f, nearest / (Tun.ArtilleryMinRef + 10f));
                        t.Terms["directFireProtection"] = 1f - OpenShare(p, 40f, 16);
                        t.Terms["counterbattery"] = MathF.Min(1f, Vector2.Distance(p, enemy.Position) / Tun.ArtilleryRef);
                        t.Terms["aaPotential"] = OpenGround(p, 15f);
                        t.Terms["exits"] = EscapeRoutes(p, 12f) / 8f;
                        t.Terms["trafficConflict"] = LaneConflict(p);
                        t.Score = 0.25f * t.Terms["objectiveCoverage"] + 0.15f * t.Terms["approachCoverage"] + 0.1f * t.Terms["minRangeSafety"] +
                                  0.15f * t.Terms["directFireProtection"] + 0.1f * t.Terms["counterbattery"] + 0.05f * t.Terms["aaPotential"] +
                                  0.1f * t.Terms["exits"] - 0.1f * t.Terms["trafficConflict"];
                        candidates.Add(t);
                    }
                Keep(list, candidates, 3);
            }
        }

        private float OpenGround(Vector2 p, float radius)
        {
            int open = 0, all = 0;
            var r = (int)MathF.Ceiling(radius / Map.Cell);
            var (cx, cy) = Map.CellXY(p);
            for (var y = cy - r; y <= cy + r; y++)
            for (var x = cx - r; x <= cx + r; x++)
            {
                if (!Map.InGrid(x, y)) continue;
                var i = y * Map.Columns + x;
                if (Vector2.Distance(Map.CellCentre(i), p) > radius) continue;
                all++;
                if (Map.Ground.Passable[i]) open++;
            }
            return all > 0 ? open / (float)all : 0f;
        }

        private void ReconPositions(List<TacticalPosition> list)
        {
            var objectives = Objectives();
            var mainPoints = new List<Vector2>();
            foreach (var l in Lanes)
                if (l.Kind == LaneKind.Main) mainPoints.AddRange(l.Points);
            var diag = MathF.Sqrt(_world.Map.Width * _world.Map.Width + _world.Map.Length * _world.Map.Length);
            for (var team = 0; team <= 1; team++)
            {
                if (Rally(team) is not { } rally || Rally(1 - team) is not { } enemy) continue;
                var candidates = new List<TacticalPosition>();
                for (var y = _world.Map.Min.Y + 8f; y < _world.Map.Max.Y; y += 16f)
                for (var x = _world.Map.Min.X + 8f; x < _world.Map.Max.X; x += 16f)
                {
                    var p = new Vector2(x, y);
                    if (Vector2.Distance(p, rally.Position) < 40f || Vector2.Distance(p, enemy.Position) < 40f || !PositionOk(p)) continue;
                    // Its own half (nearer its own spawn than the enemy's): recon watches forward from friendly ground.
                    if (Vector2.Distance(p, rally.Position) > Vector2.Distance(p, enemy.Position)) continue;
                    int seenObjectives = 0, objectivesN = 0;
                    foreach (var (o, _) in objectives)
                    {
                        objectivesN++;
                        if (Vector2.Distance(p, o.Position) <= Tun.ReconRef && LineClear(p, o.Position)) seenObjectives++;
                    }
                    int seenApproach = 0;
                    foreach (var q in mainPoints)
                        if (Vector2.Distance(p, q) <= Tun.ReconRef && LineClear(p, q)) seenApproach++;
                    var t = new TacticalPosition { Id = $"recon{team}#", Kind = TacticalPositionKind.ReconObservation, Position = p, Team = team, Subject = "map" };
                    t.Terms["losArea"] = SightArea(p, Tun.ReconRef, 16);
                    t.Terms["objectiveVisibility"] = objectivesN > 0 ? seenObjectives / (float)objectivesN : 0f;
                    t.Terms["approachVisibility"] = mainPoints.Count > 0 ? seenApproach / (float)mainPoints.Count : 0f;
                    t.Terms["risk"] = MathF.Max(0f, 1f - Vector2.Distance(p, enemy.Position) / (diag * 0.5f));
                    t.Terms["escape"] = EscapeRoutes(p, 12f) / 8f;
                    t.Score = 0.35f * t.Terms["losArea"] + 0.25f * t.Terms["objectiveVisibility"] + 0.2f * t.Terms["approachVisibility"] -
                              0.1f * t.Terms["risk"] + 0.1f * t.Terms["escape"];
                    candidates.Add(t);
                }
                Keep(list, candidates, 3);
            }
        }

        /// <summary>A low-cover prop (blocks hulls, not shots) within 4 m of <paramref name="p"/> on the line towards <paramref name="target"/>.</summary>
        private bool LowCoverBetween(Vector2 p, Vector2 target)
        {
            var dir = target - p;
            var d = dir.Length();
            if (d < 1f) return false;
            dir /= d;
            foreach (var (centre, half) in LowCover())
            {
                var along = Vector2.Dot(centre - p, dir);
                if (along <= 0f || along > 4f + half.Y) continue;
                var across = MathF.Abs(Cross(dir, centre - p));
                if (across <= MathF.Max(half.X, half.Y)) return true;
            }
            return false;
        }

        private List<(Vector2 centre, Vector2 half)>? _lowCover;

        /// <summary>
        /// Spec J4: the map's low cover: props that stop a hull but not a shot (sandbags, low walls, barriers) at least 3 m long,
        /// as (centre, half extents x / z). The only geometry in this flat Sim that masks a hull while keeping weapon LOS.
        /// </summary>
        private List<(Vector2 centre, Vector2 half)> LowCover()
        {
            if (_lowCover != null) return _lowCover;
            _lowCover = new List<(Vector2, Vector2)>();
            foreach (var p in _world.Map.Props)
            {
                if (!_world.Catalog.Props.TryGetValue(p.DefId, out var def) || !def.BlocksMovement || def.BlocksFire) continue;
                float w = def.Width, d = def.Depth;
                if (MathF.Max(w, d) < 3f) continue;
                var rot = ((p.Rotation % 180) + 180) % 180;
                if (rot == 90) (w, d) = (d, w);
                else if (rot % 90 != 0) w = d = MathF.Max(w, d);
                _lowCover.Add((p.Position, new Vector2(w * 0.5f, d * 0.5f)));
            }
            return _lowCover;
        }

        private void HullDownPositions(List<TacticalPosition> list)
        {
            var objectives = Objectives();
            var candidates = new List<TacticalPosition>();
            var range = DirectRange();
            var index = 0;
            foreach (var (centre, half) in LowCover())
            {
                index++;
                // The thin axis is the cover's normal; stand just behind it on the side away from the nearest objective.
                var normal = half.X < half.Y ? Vector2.UnitX : Vector2.UnitY;
                var thin = MathF.Min(half.X, half.Y);
                TopologyAnchor? nearest = null;
                var best = float.MaxValue;
                foreach (var (o, _) in objectives)
                {
                    var d = Vector2.Distance(o.Position, centre);
                    if (d < best)
                    {
                        best = d;
                        nearest = o;
                    }
                }
                if (nearest == null || best > range * 2f) continue;
                var side = Vector2.Dot(nearest.Position - centre, normal) >= 0f ? -1f : 1f;
                var p = centre + normal * side * (thin + SimWorld.ObstacleClearance + 1f);
                if (!PositionOk(p) || !LineClear(p, nearest.Position)) continue;
                var t = new TacticalPosition { Id = $"hd_{index}#", Kind = TacticalPositionKind.HullDown, Position = p, Subject = nearest.Id };
                t.Terms["masked"] = 1f;
                t.Terms["los"] = 1f;
                t.Terms["range"] = MathF.Max(0f, 1f - MathF.Abs(best - range * 0.8f) / range);
                t.Terms["escape"] = EscapeRoutes(p, 12f) / 8f;
                t.Score = 0.4f + 0.3f * t.Terms["range"] + 0.3f * t.Terms["escape"];
                candidates.Add(t);
            }
            Keep(list, candidates, 64);
        }

        // ================================================================================================ breaches (spec O)

        private List<BreachInfo> BuildBreaches()
        {
            var list = new List<BreachInfo>();
            var map = _world.Map;
            if (map.Walls.Count == 0) return list;
            var owners = new List<string>();
            foreach (var l in map.Walls)
                if (!owners.Contains(l.Owner)) owners.Add(l.Owner);
            owners.Sort(StringComparer.Ordinal);
            var growth = SimWorld.ObstacleClearance;
            foreach (var owner in owners)
            {
                var lines = map.WallsOf(owner);
                // The owner's HQ and the side that attacks it.
                Vector2 hq;
                int attacker;
                var camp = lines[0].CampTeam;
                if (camp >= 0)
                {
                    if (map.BaseOf(camp) is not { } site) continue;
                    hq = site.Hq;
                    attacker = 1 - camp;
                }
                else if (map.Fortress is { } fort)
                {
                    hq = fort.Hq;
                    var d0 = _world.TryGetRally(0, out var a0) ? Vector2.Distance(a0, hq) : 0f;
                    var d1 = _world.TryGetRally(1, out var a1) ? Vector2.Distance(a1, hq) : 0f;
                    attacker = d0 >= d1 ? 0 : 1;
                }
                else continue;
                if (!_world.TryGetRally(attacker, out var from)) continue;
                var targets = new List<(string id, Vector2 at)> { (camp >= 0 ? "hq" + camp : "fortress_hq", hq) };
                var reach = 0f;
                foreach (var l in lines) reach = MathF.Max(reach, l.Radius);
                foreach (var p in map.Points)
                    if (Vector2.Distance(p.Position, hq) <= reach + 10f) targets.Add(("point_" + p.Id, p.Position));
                // The ground with every segment of the owner's lines standing (gates open), and each segment's footprint.
                var closed = (bool[])Map.Ground.Passable.Clone();
                var footprints = new List<List<int>>();
                foreach (var l in lines)
                    foreach (var s in l.Segments)
                    {
                        var cells = Footprint(s.Center, s.Width + 2f * growth, s.Depth + 2f * growth);
                        foreach (var c in cells) closed[c] = false;
                        footprints.Add(cells);
                    }
                var source = NearestIn(closed, from);
                var closedDist = Bfs(closed, source);
                var targetCells = new List<int>();
                foreach (var (_, at) in targets) targetCells.Add(NearestIn(closed, at));
                var index = 0;
                foreach (var l in lines)
                    for (var si = 0; si < l.Segments.Count; si++)
                    {
                        var s = l.Segments[si];
                        var open = (bool[])closed.Clone();
                        foreach (var c in footprints[index])
                            if (_world.Map.InsideBoundary(Map.CellCentre(c)) && !Map.IsSea(Map.CellCentre(c))) open[c] = true;
                        index++;
                        var openDist = Bfs(open, source);
                        var b = new BreachInfo
                        {
                            Id = $"{owner}_r{l.Ring}_s{si}",
                            Owner = owner,
                            Ring = l.Ring,
                            Centre = s.Center,
                            OpeningWidthM = s.Length,
                            AlternateRouteExists = true,
                        };
                        for (var t = 0; t < targets.Count; t++)
                        {
                            var tc = targetCells[t];
                            var before = tc >= 0 ? closedDist[tc] : -1;
                            var after = tc >= 0 ? openDist[tc] : -1;
                            if (before < 0) b.AlternateRouteExists = false;
                            if (after < 0) continue;
                            if (before < 0 || after < before)
                            {
                                b.BlockedRouteIds.Add($"rally{attacker}->{targets[t].id}");
                                var saving = before < 0 ? float.PositiveInfinity : (before - after) * Map.Cell;
                                b.PathCostReductionOnDestroy = MathF.Max(b.PathCostReductionOnDestroy, saving);
                                if (before < 0 || after <= before * 0.75f) b.ObjectiveAccessGained = true;
                            }
                        }
                        foreach (var cls in new[] { VehicleSizeClass.Heavy, VehicleSizeClass.SuperHeavy, VehicleSizeClass.Boss })
                        {
                            var need = Class(cls).ReferenceWidth + 2f * Tun.SideClearance;
                            if (l.GateWidth < need && s.Length >= need) b.HeavyAccessGained.Add(cls);
                        }
                        var towers = 0;
                        foreach (var ll in lines)
                            foreach (var ss in ll.Segments)
                                if (ss.Gun && Vector2.Distance(ss.Center, s.Center) <= Tun.TowerRangeRef) towers++;
                        if (camp >= 0 && map.BaseOf(camp) is { } site2)
                        {
                            foreach (var slot in site2.Slots)
                                if (Vector2.Distance(slot.Position, s.Center) <= Tun.TowerRangeRef) towers++;
                        }
                        else if (map.Fortress is { } fort2)
                            foreach (var slot in fort2.Slots)
                                if (Vector2.Distance(slot.Hardpoint.Position, s.Center) <= Tun.TowerRangeRef) towers++;
                        b.DefensiveTowerCoverage = towers;
                        list.Add(b);
                    }
            }
            return list;
        }

        private List<int> Footprint(Vector2 centre, float width, float depth)
        {
            var cells = new List<int>();
            var (x0, y0) = Map.CellXY(centre - new Vector2(width, depth) * 0.5f);
            var (x1, y1) = Map.CellXY(centre + new Vector2(width, depth) * 0.5f - new Vector2(1e-3f));
            for (var y = Math.Max(0, y0); y <= Math.Min(Map.Rows - 1, y1); y++)
            for (var x = Math.Max(0, x0); x <= Math.Min(Map.Columns - 1, x1); x++)
                cells.Add(y * Map.Columns + x);
            return cells;
        }

        private int NearestIn(bool[] passable, Vector2 p)
        {
            var (cx, cy) = Map.CellXY(p);
            for (var ring = 0; ring <= SimTunables.Ai.Topology.NearestRings + 4; ring++)
            {
                var best = -1;
                var bestD = float.MaxValue;
                for (var y = cy - ring; y <= cy + ring; y++)
                for (var x = cx - ring; x <= cx + ring; x++)
                {
                    if (Math.Max(Math.Abs(x - cx), Math.Abs(y - cy)) != ring || !Map.InGrid(x, y)) continue;
                    var i = y * Map.Columns + x;
                    if (!passable[i]) continue;
                    var d = Vector2.DistanceSquared(Map.CellCentre(i), p);
                    if (d < bestD)
                    {
                        bestD = d;
                        best = i;
                    }
                }
                if (best >= 0) return best;
            }
            return -1;
        }

        // ================================================================================================ terrain (spec P)

        /// <summary>
        /// Spec P: a terrain tag's semantics. Movement cost is TerrainRules' path cost and a forest's concealment its sight
        /// factor (the values the Sim already uses, not copies); the rest is maps.terrainSemantics metadata. Direct-fire cover
        /// and hull-down potential are 0: the Sim gives no terrain cover and the ground is flat.
        /// </summary>
        public static TerrainSemantics SemanticsOf(TerrainTag tag)
        {
            var row = tag switch
            {
                TerrainTag.Road => SimTunables.Maps.TerrainSemantics.Road,
                TerrainTag.Rough => SimTunables.Maps.TerrainSemantics.Rough,
                TerrainTag.Forest => SimTunables.Maps.TerrainSemantics.Forest,
                TerrainTag.ShallowWater => SimTunables.Maps.TerrainSemantics.ShallowWater,
                _ => SimTunables.Maps.TerrainSemantics.Normal,
            };
            float V(int i) => i < row.Length ? row[i] : 0f;
            var concealment = tag == TerrainTag.Forest ? 1f - TerrainRules.ForestSight : 0f;
            return new TerrainSemantics(tag, TerrainRules.PathCost(tag), V(0), concealment, V(1), 0f, V(2), V(3), 0f, V(4));
        }

        private Dictionary<TerrainTag, int> CountTerrain()
        {
            var counts = new Dictionary<TerrainTag, int>();
            foreach (TerrainTag t in Enum.GetValues(typeof(TerrainTag))) counts[t] = 0;
            var grid = _world.Grid;
            for (var y = 0; y < Map.Rows; y++)
            for (var x = 0; x < Map.Columns; x++)
                if (Map.Ground.Passable[y * Map.Columns + x]) counts[grid.TerrainAt(x, y)]++;
            return counts;
        }
    }
}
