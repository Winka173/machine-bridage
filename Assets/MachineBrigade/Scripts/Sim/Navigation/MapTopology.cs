#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>AI MASTER section 4: how a unit moves over the battlefield (which cells it may stand on).</summary>
    public enum MobilityDomain
    {
        /// <summary>Wheels and tracks: open ground of the navigation grid, never the sea.</summary>
        Ground,

        /// <summary>Ships: the sea (the map's <see cref="SeaDef"/>), off the ground's grid.</summary>
        Naval,

        /// <summary>Waders and hovercraft: open ground, shallow water, and the sea where the grid lets them drive.</summary>
        Amphibious,

        /// <summary>Aircraft: anywhere over the map.</summary>
        Air,

        /// <summary>Fixed defences: where they stand.</summary>
        Static,
    }

    /// <summary>AI MASTER section 4: a narrow passage of open ground (a gate, a bridge, a lane between cliffs).</summary>
    public readonly struct ChokePoint
    {
        public ChokePoint(Vector2 centre, float width, int cells, int component)
        {
            Centre = centre;
            Width = width;
            Cells = cells;
            Component = component;
        }

        public Vector2 Centre { get; }

        /// <summary>The passage's narrowest width (metres).</summary>
        public float Width { get; }
        public int Cells { get; }

        /// <summary>The ground component it lies in.</summary>
        public int Component { get; }
    }

    /// <summary>AI MASTER sections 4-5: one connected component of a domain (a region a unit of it can drive all over).</summary>
    public readonly struct TopologyRegion
    {
        public TopologyRegion(MobilityDomain domain, int component, int cells, Vector2 centre, Vector2 min, Vector2 max)
        {
            Domain = domain;
            Component = component;
            Cells = cells;
            Centre = centre;
            Min = min;
            Max = max;
        }

        public MobilityDomain Domain { get; }
        public int Component { get; }
        public int Cells { get; }
        public Vector2 Centre { get; }
        public Vector2 Min { get; }
        public Vector2 Max { get; }

        public override string ToString() => $"{Domain}Component {Component} ({Cells} cells)";
    }

    /// <summary>AI MASTER section 5: a map objective (a capture point, a team's rally, a coastal battery) and its component per domain.</summary>
    public readonly struct ObjectiveRegion
    {
        public ObjectiveRegion(string id, Vector2 centre, float radius, int ground, int naval, int amphibious)
        {
            Id = id;
            Centre = centre;
            Radius = radius;
            GroundComponent = ground;
            NavalComponent = naval;
            AmphibiousComponent = amphibious;
        }

        public string Id { get; }
        public Vector2 Centre { get; }
        public float Radius { get; }

        /// <summary>0: no ground cell of it (or near it) is open.</summary>
        public int GroundComponent { get; }
        public int NavalComponent { get; }
        public int AmphibiousComponent { get; }

        public int ComponentOf(MobilityDomain domain) => domain switch
        {
            MobilityDomain.Ground => GroundComponent,
            MobilityDomain.Naval => NavalComponent,
            MobilityDomain.Amphibious => AmphibiousComponent,
            MobilityDomain.Air => 1,
            _ => 0,
        };
    }

    /// <summary>
    /// AI MASTER section 5: the cells of one mobility domain on the navigation grid's cells, split into connected components
    /// (four-neighbour flood fill, as the route search moves), with travel distances from a source cell on demand (cached
    /// per source until the topology is rebuilt).
    /// </summary>
    public sealed class DomainGraph
    {
        private readonly MapTopology _map;
        private readonly int[] _component;
        private readonly List<TopologyRegion> _regions = new();
        private readonly Dictionary<int, int[]> _distances = new();
        private readonly List<int> _distanceOrder = new();
        private static int DistanceCacheSize => global::MachineBrigade.Sim.Content.SimTunables.Maps.DomainGraph.DistanceCacheSize;

        internal DomainGraph(MapTopology map, MobilityDomain domain, bool[] passable)
        {
            _map = map;
            Domain = domain;
            Passable = passable;
            _component = new int[passable.Length];
            Label();
        }

        public MobilityDomain Domain { get; }

        /// <summary>Per cell: whether a unit of this domain may stand there.</summary>
        internal bool[] Passable { get; }

        /// <summary>How many components (numbered from 1).</summary>
        public int Components => _regions.Count;

        /// <summary>The components, largest first is not promised: in label order (component i at index i - 1).</summary>
        public IReadOnlyList<TopologyRegion> Regions => _regions;

        /// <summary>The component of a cell (0: not passable, or off the grid).</summary>
        public int ComponentOfCell(int cell) => cell >= 0 && cell < _component.Length ? _component[cell] : 0;

        public int ComponentAt(Vector2 p) => ComponentOfCell(_map.CellIndex(p));

        public bool IsPassable(Vector2 p)
        {
            var c = _map.CellIndex(p);
            return c >= 0 && Passable[c];
        }

        /// <summary>The cell under <paramref name="p"/>, or the nearest passable one within <paramref name="rings"/> rings (-1: none).</summary>
        public int NearestPassableCell(Vector2 p, int rings)
        {
            var (cx, cy) = _map.CellXY(p);
            if (_map.InGrid(cx, cy) && Passable[cy * _map.Columns + cx]) return cy * _map.Columns + cx;
            for (var ring = 1; ring <= rings; ring++)
            {
                var best = -1;
                var bestD = float.MaxValue;
                for (var y = cy - ring; y <= cy + ring; y++)
                for (var x = cx - ring; x <= cx + ring; x++)
                {
                    if (Math.Abs(x - cx) != ring && Math.Abs(y - cy) != ring) continue;
                    if (!_map.InGrid(x, y)) continue;
                    var i = y * _map.Columns + x;
                    if (!Passable[i]) continue;
                    var d = Vector2.DistanceSquared(_map.CellCentre(i), p);
                    if (d >= bestD) continue;
                    bestD = d;
                    best = i;
                }
                if (best >= 0) return best;
            }
            return -1;
        }

        /// <summary>
        /// Four-neighbour steps over this domain from <paramref name="source"/> to every cell (-1: unreachable). Cached per
        /// source (the last <see cref="DistanceCacheSize"/> sources), so a side's drop zone is walked once per topology.
        /// </summary>
        public int[] DistancesFrom(int source)
        {
            if (_distances.TryGetValue(source, out var cached)) return cached;
            var n = Passable.Length;
            var dist = new int[n];
            for (var i = 0; i < n; i++) dist[i] = -1;
            if (source >= 0 && source < n && Passable[source])
            {
                var queue = new int[n];
                int head = 0, tail = 0;
                dist[source] = 0;
                queue[tail++] = source;
                var w = _map.Columns;
                while (head < tail)
                {
                    var i = queue[head++];
                    int x = i % w, y = i / w;
                    var d = dist[i] + 1;
                    if (x + 1 < w) Visit(i + 1);
                    if (x > 0) Visit(i - 1);
                    if (y + 1 < _map.Rows) Visit(i + w);
                    if (y > 0) Visit(i - w);

                    void Visit(int j)
                    {
                        if (dist[j] >= 0 || !Passable[j]) return;
                        dist[j] = d;
                        queue[tail++] = j;
                    }
                }
            }
            if (_distanceOrder.Count >= DistanceCacheSize)
            {
                _distances.Remove(_distanceOrder[0]);
                _distanceOrder.RemoveAt(0);
            }
            _distances[source] = dist;
            _distanceOrder.Add(source);
            return dist;
        }

        private void Label()
        {
            var n = Passable.Length;
            var w = _map.Columns;
            var queue = new int[n];
            var next = 0;
            for (var start = 0; start < n; start++)
            {
                if (_component[start] != 0 || !Passable[start]) continue;
                next++;
                _component[start] = next;
                int head = 0, tail = 0;
                queue[tail++] = start;
                var sum = Vector2.Zero;
                var min = new Vector2(float.MaxValue);
                var max = new Vector2(float.MinValue);
                while (head < tail)
                {
                    var i = queue[head++];
                    var c = _map.CellCentre(i);
                    sum += c;
                    min = Vector2.Min(min, c);
                    max = Vector2.Max(max, c);
                    int x = i % w, y = i / w;
                    if (x + 1 < w) Fill(i + 1);
                    if (x > 0) Fill(i - 1);
                    if (y + 1 < _map.Rows) Fill(i + w);
                    if (y > 0) Fill(i - w);
                }
                _regions.Add(new TopologyRegion(Domain, next, tail, sum / tail, min, max));

                void Fill(int j)
                {
                    if (_component[j] != 0 || !Passable[j]) return;
                    _component[j] = next;
                    queue[tail++] = j;
                }
            }
        }
    }

    /// <summary>
    /// AI MASTER sections 4-5 (lane P0-B): the battlefield's shape for the AI, built once per map from the navigation grid and
    /// the sea (and again, at most every <c>ai.topology.rebuildSeconds</c>, after walls fall or wrecks close ground): per
    /// mobility domain the passable cells and their connected components, the narrow passages (chokes), the components as
    /// regions, and the map's objectives with their component per domain. Reads the world only; never changes a battle.
    /// Other AI lanes read it through <see cref="SimWorld.Topology"/>.
    /// </summary>
    public sealed class MapTopology
    {
        private readonly List<ChokePoint> _chokes = new();
        private readonly List<TopologyRegion> _regions = new();
        private readonly List<ObjectiveRegion> _objectives = new();

        private MapTopology(Vector2 origin, float cell, int columns, int rows)
        {
            Origin = origin;
            Cell = cell;
            Columns = columns;
            Rows = rows;
            Sea = new bool[columns * rows];
            Clearance = new byte[columns * rows];
        }

        public Vector2 Origin { get; }

        /// <summary>The cell size (metres): the navigation grid's.</summary>
        public float Cell { get; }
        public int Columns { get; }
        public int Rows { get; }

        /// <summary>The navigation grid's version this was built from.</summary>
        public int GridVersion { get; private set; }

        /// <summary>The battle time it was built at.</summary>
        public double BuiltAt { get; private set; }

        /// <summary>How many times the battle's topology has been built (1: the load-time build).</summary>
        public int Generation { get; private set; }

        public DomainGraph Ground { get; private set; } = null!;
        public DomainGraph Naval { get; private set; } = null!;
        public DomainGraph Amphibious { get; private set; } = null!;

        /// <summary>Per cell: out on the water (beyond the waterline of the map's sea).</summary>
        internal bool[] Sea { get; }

        /// <summary>Per cell: steps of open ground to the nearest blocked cell (capped at 15): a passage's half width.</summary>
        internal byte[] Clearance { get; }

        public bool HasSea { get; private set; }

        public IReadOnlyList<ChokePoint> Chokes => _chokes;
        public IReadOnlyList<TopologyRegion> Regions => _regions;
        public IReadOnlyList<ObjectiveRegion> Objectives => _objectives;

        /// <summary>The domain graph of a mobility domain (null for Air and Static: nothing to partition).</summary>
        public DomainGraph? For(MobilityDomain domain) => domain switch
        {
            MobilityDomain.Ground => Ground,
            MobilityDomain.Naval => Naval,
            MobilityDomain.Amphibious => Amphibious,
            _ => null,
        };

        /// <summary>How a vehicle moves: aircraft fly, fixed defences stand, ships sail, waders wade, the rest drive.</summary>
        public static MobilityDomain DomainOf(VehicleDef def) =>
            def.Flying ? MobilityDomain.Air
            : def.Static || def.Speed <= 0f ? MobilityDomain.Static
            : def.Naval != null ? MobilityDomain.Naval
            : TerrainRules.Wades(def) ? MobilityDomain.Amphibious
            : MobilityDomain.Ground;

        internal bool InGrid(int x, int y) => x >= 0 && y >= 0 && x < Columns && y < Rows;

        internal (int x, int y) CellXY(Vector2 p) =>
            ((int)MathF.Floor((p.X - Origin.X) / Cell), (int)MathF.Floor((p.Y - Origin.Y) / Cell));

        /// <summary>The cell under a point (-1: off the grid).</summary>
        public int CellIndex(Vector2 p)
        {
            var (x, y) = CellXY(p);
            return InGrid(x, y) ? y * Columns + x : -1;
        }

        public Vector2 CellCentre(int index) =>
            new(Origin.X + (index % Columns + 0.5f) * Cell, Origin.Y + (index / Columns + 0.5f) * Cell);

        /// <summary>Whether a point is out on the water.</summary>
        public bool IsSea(Vector2 p)
        {
            var c = CellIndex(p);
            return c >= 0 && Sea[c];
        }

        /// <summary>The narrowest passage (metres, capped) on a shortest ground route between two points; +inf when no choke lies on it.</summary>
        public float Bottleneck(int sourceCell, int targetCell)
        {
            if (sourceCell < 0 || targetCell < 0) return float.PositiveInfinity;
            var dist = Ground.DistancesFrom(sourceCell);
            if (dist[targetCell] < 0) return float.PositiveInfinity;
            // Walk back from the target down the distance field (a shortest route), taking the narrowest clearance.
            var narrowest = int.MaxValue;
            var at = targetCell;
            for (var guard = 0; guard < dist.Length && dist[at] > 0; guard++)
            {
                narrowest = Math.Min(narrowest, Clearance[at]);
                int x = at % Columns, y = at / Columns;
                var next = -1;
                if (x + 1 < Columns && dist[at + 1] == dist[at] - 1) next = at + 1;
                else if (x > 0 && dist[at - 1] == dist[at] - 1) next = at - 1;
                else if (y + 1 < Rows && dist[at + Columns] == dist[at] - 1) next = at + Columns;
                else if (y > 0 && dist[at - Columns] == dist[at] - 1) next = at - Columns;
                if (next < 0) break;
                at = next;
            }
            return narrowest == int.MaxValue || narrowest >= 15 ? float.PositiveInfinity : (narrowest * 2f - 1f) * Cell;
        }

        /// <summary>
        /// Builds the topology of a battlefield: ground = open grid cells off the sea; naval = the sea; amphibious = open grid
        /// cells and the sea where open; then components, clearance, chokes and objectives.
        /// </summary>
        public static MapTopology Build(SimWorld world)
        {
            var grid = world.Grid;
            var topo = new MapTopology(grid.Origin, grid.CellSize, grid.Width, grid.Height)
            {
                GridVersion = grid.Version,
                BuiltAt = world.Time,
            };
            var n = topo.Columns * topo.Rows;
            var ground = new bool[n];
            var naval = new bool[n];
            var amphibious = new bool[n];
            var sea = world.Map.Sea;
            topo.HasSea = sea != null;
            for (var y = 0; y < topo.Rows; y++)
            for (var x = 0; x < topo.Columns; x++)
            {
                var i = y * topo.Columns + x;
                var centre = topo.CellCentre(i);
                var water = sea != null && sea.IsSea(centre);
                var open = grid.IsWalkable(x, y);
                topo.Sea[i] = water;
                ground[i] = open && !water;
                naval[i] = water;
                amphibious[i] = open;
            }
            topo.Ground = new DomainGraph(topo, MobilityDomain.Ground, ground);
            topo.Naval = new DomainGraph(topo, MobilityDomain.Naval, naval);
            topo.Amphibious = new DomainGraph(topo, MobilityDomain.Amphibious, amphibious);
            topo._regions.AddRange(topo.Ground.Regions);
            topo._regions.AddRange(topo.Naval.Regions);
            topo._regions.AddRange(topo.Amphibious.Regions);
            topo.MeasureClearance(ground);
            topo.FindChokes(ground, SimTunables.Ai.Topology.ChokeWidth);
            topo.AddObjectives(world);
            return topo;
        }

        internal MapTopology Rebuilt(SimWorld world)
        {
            var next = Build(world);
            next.Generation = Generation + 1;
            return next;
        }

        internal void FirstBuild() => Generation = 1;

        private void MeasureClearance(bool[] open)
        {
            // Multi-source walk from every closed cell (and the grid's edge) over the open ground, four-neighbour.
            var n = open.Length;
            var queue = new int[n];
            int head = 0, tail = 0;
            for (var i = 0; i < n; i++)
            {
                int x = i % Columns, y = i / Columns;
                var edge = x == 0 || y == 0 || x == Columns - 1 || y == Rows - 1;
                if (!open[i])
                {
                    Clearance[i] = 0;
                    queue[tail++] = i;
                }
                else Clearance[i] = edge ? (byte)1 : byte.MaxValue;
            }
            // Edge seeds go in after every closed cell so the queue stays in distance order and no cell is queued twice
            // (mixing 0 and 1 seeds let cells be lowered and re-queued, overflowing the n-sized queue).
            for (var i = 0; i < n; i++)
                if (open[i] && Clearance[i] == 1) queue[tail++] = i;
            while (head < tail)
            {
                var i = queue[head++];
                int x = i % Columns, y = i / Columns;
                var d = (byte)Math.Min(global::MachineBrigade.Sim.Content.SimTunables.Maps.MapTopology.MeasureClearanceClearanceCap, Clearance[i] + 1);
                if (x + 1 < Columns) Step(i + 1);
                if (x > 0) Step(i - 1);
                if (y + 1 < Rows) Step(i + Columns);
                if (y > 0) Step(i - Columns);

                void Step(int j)
                {
                    if (!open[j] || Clearance[j] <= d) return;
                    Clearance[j] = d;
                    queue[tail++] = j;
                }
            }
            for (var i = 0; i < n; i++)
                if (Clearance[i] > 15) Clearance[i] = 15;
        }

        private void FindChokes(bool[] open, float chokeWidth)
        {
            // A choke cell: open ground no wider than chokeWidth with closed ground on two opposite sides (a passage, not a
            // wall's foot by an open field). Adjacent choke cells make one choke point.
            var half = Math.Max(1, (int)MathF.Ceiling(chokeWidth * 0.5f / Cell));
            var n = open.Length;
            var choke = new bool[n];
            for (var i = 0; i < n; i++)
            {
                if (!open[i] || Clearance[i] > half) continue;
                int x = i % Columns, y = i / Columns;
                choke[i] = (Closed(-1, 0) && Closed(1, 0)) || (Closed(0, -1) && Closed(0, 1));

                // A closed cell (or the grid's edge) within half + 1 steps that way.
                bool Closed(int dx, int dy)
                {
                    for (var k = 1; k <= half + 1; k++)
                    {
                        int qx = x + dx * k, qy = y + dy * k;
                        if (!InGrid(qx, qy) || !open[qy * Columns + qx]) return true;
                    }
                    return false;
                }
            }
            var seen = new bool[n];
            var queue = new int[n];
            for (var start = 0; start < n; start++)
            {
                if (!choke[start] || seen[start]) continue;
                int head = 0, tail = 0;
                queue[tail++] = start;
                seen[start] = true;
                var sum = Vector2.Zero;
                var narrowest = int.MaxValue;
                while (head < tail)
                {
                    var i = queue[head++];
                    sum += CellCentre(i);
                    narrowest = Math.Min(narrowest, Clearance[i]);
                    int x = i % Columns, y = i / Columns;
                    for (var dy = -1; dy <= 1; dy++)
                    for (var dx = -1; dx <= 1; dx++)
                    {
                        int nx = x + dx, ny = y + dy;
                        if (!InGrid(nx, ny)) continue;
                        var j = ny * Columns + nx;
                        if (!choke[j] || seen[j]) continue;
                        seen[j] = true;
                        queue[tail++] = j;
                    }
                }
                if (tail < 2) continue;
                _chokes.Add(new ChokePoint(sum / tail, (narrowest * 2f - 1f) * Cell, tail, Ground.ComponentOfCell(start)));
            }
        }

        private void AddObjectives(SimWorld world)
        {
            var rings = SimTunables.Ai.Topology.NearestRings;
            foreach (var p in world.Map.Points) Add(p.Id, p.Position, MathF.Max(global::MachineBrigade.Sim.Content.SimTunables.Maps.MapTopology.AddObjectivesRadiusFloor, p.Radius));
            foreach (var t in world.Map.Teams) Add("rally_" + t.Team, t.Rally, global::MachineBrigade.Sim.Content.SimTunables.Maps.MapTopology.AddObjectivesRadius);
            if (world.Map.Sea is { } sea)
                foreach (var b in sea.Batteries) Add("battery_" + b.Id, b.At, global::MachineBrigade.Sim.Content.SimTunables.Maps.MapTopology.AddObjectivesRadius);

            void Add(string id, Vector2 at, float radius)
            {
                var reach = Math.Max(rings, (int)MathF.Ceiling(radius / Cell));
                _objectives.Add(new ObjectiveRegion(id, at, radius,
                    Ground.ComponentOfCell(Ground.NearestPassableCell(at, reach)),
                    Naval.ComponentOfCell(Naval.NearestPassableCell(at, reach)),
                    Amphibious.ComponentOfCell(Amphibious.NearestPassableCell(at, reach))));
            }
        }
    }
}
