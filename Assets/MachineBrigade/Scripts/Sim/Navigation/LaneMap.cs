#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>What a navigation cell means for traffic (see <see cref="LaneMap"/>).</summary>
    [Flags]
    public enum LaneFlags : byte
    {
        None = 0,

        /// <summary>Under a road drawn on the map.</summary>
        Road = 1,

        /// <summary>On one of the main routes between the camps, the objectives and the fortress.</summary>
        Route = 2,

        /// <summary>A doorway: a gate, or a gap or alley too narrow for a hull to stand in without closing it.</summary>
        Narrow = 4,

        /// <summary>Nobody stops here: a short doorway and its mouths on either side.</summary>
        NoPark = 8,
    }

    /// <summary>
    /// Traffic knowledge about every navigation cell, worked out once from the walls and rebuilt
    /// when one falls: where the roads and the main routes run, where the doorways are (gates, gaps
    /// between buildings), and which cells nobody may stop on. Units that park on their way in a
    /// gate or on the road the others come along are what jams an army, so every rule that picks
    /// a place to stop (holding in range, firing spots, guard posts, formation slots, arriving)
    /// asks this map first. It also keeps the firing-spot reservations, so two guns do not pick
    /// the same spot.
    /// </summary>
    public sealed class LaneMap
    {
        /// <summary>A passage this wide or narrower (metres of hull-centre room across it) is a doorway.</summary>
        public static float NarrowWidth => global::MachineBrigade.Sim.Content.SimTunables.Maps.LaneMap.NarrowWidth;

        /// <summary>A doorway only counts where it leads somewhere: this many open cells on both sides of it, along the way through.</summary>
        private const int ThroughCells = 2;

        /// <summary>
        /// A doorway run of up to this many cells (a gate, a short alley: about 16 m of a 3-cell
        /// passage) is no-parking. A longer one (a canyon, a long street between houses) stays a
        /// doorway without the rule, or nobody could ever stop along it.
        /// </summary>
        private static int MaxNoParkCells => global::MachineBrigade.Sim.Content.SimTunables.Maps.LaneMap.MaxNoParkCells;

        /// <summary>How far round a doorway its mouths reach (cells): nobody parks there either.</summary>
        private const int NoParkMouth = 2;

        /// <summary>The main routes are stamped this wide either side of the path (metres).</summary>
        private static float RouteHalfWidth => global::MachineBrigade.Sim.Content.SimTunables.Maps.LaneMap.RouteHalfWidth;

        private static int MaxClearance => global::MachineBrigade.Sim.Content.SimTunables.Maps.LaneMap.MaxClearance;

        /// <summary>After a wall falls the map is rebuilt at most this often (seconds).</summary>
        private static double RebuildInterval => global::MachineBrigade.Sim.Content.SimTunables.Maps.LaneMap.RebuildInterval;

        private readonly NavGrid _grid;
        private readonly LaneFlags[] _flags;
        private readonly byte[] _clearance;
        private readonly byte[] _routeCount;
        private readonly int[] _stamp;
        private readonly int[] _reservedBy;
        private readonly byte[] _narrowAxis;
        private readonly short[] _doorway;
        private readonly List<Vector2> _doorwayThrough = new();
        private readonly PathFinder _finder;
        private readonly List<Vector2> _path = new();
        private readonly List<int> _queue = new();
        private int _version = -1;
        private int _stampId;
        private double _nextAllowed = double.NegativeInfinity;

        public LaneMap(NavGrid grid)
        {
            _grid = grid;
            var n = grid.Width * grid.Height;
            _flags = new LaneFlags[n];
            _clearance = new byte[n];
            _routeCount = new byte[n];
            _stamp = new int[n];
            _reservedBy = new int[n];
            _narrowAxis = new byte[n];
            _doorway = new short[n];
            _finder = new PathFinder(grid);
        }

        /// <summary>How many times the map has been built (tests).</summary>
        public int Builds { get; private set; }

        /// <summary>The short doorways (no-parking runs) found at the last build, numbered from 1.</summary>
        public int DoorwayCount => _doorwayThrough.Count;

        /// <summary>The short doorway (with its mouths) the cell under <paramref name="p"/> belongs to; 0 for none.</summary>
        public int DoorwayAt(Vector2 p)
        {
            var (x, y) = _grid.CellOf(p);
            return _grid.InBounds(x, y) ? _doorway[_grid.Index(x, y)] : 0;
        }

        /// <summary>The way through doorway <paramref name="id"/> (a unit vector; its sign is arbitrary).</summary>
        public Vector2 DoorwayThrough(int id) => id > 0 && id <= _doorwayThrough.Count ? _doorwayThrough[id - 1] : Vector2.UnitY;

        public LaneFlags At(Vector2 p)
        {
            var (x, y) = _grid.CellOf(p);
            return _grid.InBounds(x, y) ? _flags[_grid.Index(x, y)] : LaneFlags.None;
        }

        public bool NoParkAt(Vector2 p) => (At(p) & LaneFlags.NoPark) != 0;

        /// <summary>How many of the main routes use the cell under <paramref name="p"/>.</summary>
        public int RouteCountAt(Vector2 p)
        {
            var (x, y) = _grid.CellOf(p);
            return _grid.InBounds(x, y) ? _routeCount[_grid.Index(x, y)] : 0;
        }

        /// <summary>Cells from <paramref name="p"/> to the nearest blocked cell or the map's edge (capped at 15).</summary>
        public int ClearanceAt(Vector2 p)
        {
            var (x, y) = _grid.CellOf(p);
            return _grid.InBounds(x, y) ? _clearance[_grid.Index(x, y)] : 0;
        }

        /// <summary>Flags by cell index (tests and the debug view).</summary>
        public LaneFlags FlagsOf(int x, int y) => _grid.InBounds(x, y) ? _flags[_grid.Index(x, y)] : LaneFlags.None;

        /// <summary>
        /// Rebuilds the map when walkability changed since the last build (a wall or a defence
        /// fell), at most once every two seconds of battle; the first build is immediate.
        /// </summary>
        /// <summary>The next rebuild comes at once, whatever the last one (a fortress wall has just come down).</summary>
        internal void Hurry() => _nextAllowed = double.MinValue;

        internal void RebuildIfDirty(SimWorld world)
        {
            if (_grid.Version == _version) return;
            if (_version != -1 && world.Time < _nextAllowed) return;
            _version = _grid.Version;
            _nextAllowed = world.Time + RebuildInterval;
            Build(world);
        }

        private void Build(SimWorld world)
        {
            Builds++;
            Array.Clear(_flags, 0, _flags.Length);
            Array.Clear(_routeCount, 0, _routeCount.Length);
            Array.Clear(_doorway, 0, _doorway.Length);
            _doorwayThrough.Clear();
            BuildClearance();
            foreach (var road in world.Map.Roads)
                for (var i = 0; i + 1 < road.Points.Count; i++)
                    StampSegment(road.Points[i], road.Points[i + 1], road.Width * 0.5f, LaneFlags.Road, count: false);
            StampRoutes(world);
            FindDoorways();
            MarkNoPark();
            // A wall that fell made a breach where a gun had booked its firing spot: the spot is a
            // doorway now, so the booking goes and the gun picks another.
            foreach (var v in world.VehicleList)
                if (v.Traffic.HasReservation && NoParkAt(v.Traffic.ReservedAt)) Release(v);
        }

        /// <summary>Multi-source breadth-first search from every blocked cell and the map's edge (a brushfire).</summary>
        private void BuildClearance()
        {
            _queue.Clear();
            int w = _grid.Width, h = _grid.Height;
            for (var y = 0; y < h; y++)
            for (var x = 0; x < w; x++)
            {
                var i = _grid.Index(x, y);
                if (!_grid.IsWalkable(x, y))
                {
                    _clearance[i] = 0;
                    _queue.Add(i);
                }
                else if (x == 0 || y == 0 || x == w - 1 || y == h - 1)
                {
                    _clearance[i] = 1;
                    _queue.Add(i);
                }
                else
                {
                    _clearance[i] = (byte)MaxClearance;
                }
            }
            for (var head = 0; head < _queue.Count; head++)
            {
                var i = _queue[head];
                var next = _clearance[i] + 1;
                if (next >= MaxClearance) continue;
                int cx = i % w, cy = i / w;
                for (var dy = -1; dy <= 1; dy++)
                for (var dx = -1; dx <= 1; dx++)
                {
                    if (dx == 0 && dy == 0) continue;
                    int nx = cx + dx, ny = cy + dy;
                    if (!_grid.InBounds(nx, ny)) continue;
                    var j = _grid.Index(nx, ny);
                    if (_clearance[j] <= next) continue;
                    _clearance[j] = (byte)next;
                    _queue.Add(j);
                }
            }
        }

        /// <summary>
        /// The main routes: the path between every pair of places an army travels between (each
        /// side's camp and every objective), both ways through every gate on the way.
        /// </summary>
        private void StampRoutes(SimWorld world)
        {
            var places = new List<Vector2>();
            foreach (var team in world.Map.Teams) places.Add(team.Rally);
            foreach (var point in world.Map.Points) places.Add(point.Position);
            for (var i = 0; i < places.Count; i++)
            for (var j = i + 1; j < places.Count; j++)
            {
                if (!_finder.TryFindPath(places[i], places[j], _path)) continue;
                _stampId++;
                var from = places[i];
                foreach (var to in _path)
                {
                    StampSegment(from, to, RouteHalfWidth, LaneFlags.Route, count: true);
                    from = to;
                }
            }
        }

        /// <summary>Flags every cell whose centre lies within <paramref name="half"/> of the segment a-b.</summary>
        private void StampSegment(Vector2 a, Vector2 b, float half, LaneFlags flag, bool count)
        {
            var min = Vector2.Min(a, b) - new Vector2(half);
            var max = Vector2.Max(a, b) + new Vector2(half);
            var (x0, y0) = _grid.CellOf(min);
            var (x1, y1) = _grid.CellOf(max);
            var ab = b - a;
            var length = ab.LengthSquared();
            for (var y = Math.Max(0, y0); y <= Math.Min(_grid.Height - 1, y1); y++)
            for (var x = Math.Max(0, x0); x <= Math.Min(_grid.Width - 1, x1); x++)
            {
                var c = _grid.CellCenter(x, y);
                var t = length > 1e-6f ? Math.Clamp(Vector2.Dot(c - a, ab) / length, 0f, 1f) : 0f;
                if (Vector2.DistanceSquared(c, a + ab * t) > half * half) continue;
                var i = _grid.Index(x, y);
                _flags[i] |= flag;
                if (!count || _stamp[i] == _stampId) continue;
                _stamp[i] = _stampId;
                if (_routeCount[i] < global::MachineBrigade.Sim.Content.SimTunables.Maps.LaneMap.StampSegmentRouteCountMax) _routeCount[i]++;
            }
        }

        private static readonly int[] AxisX = { 1, 0, 1, 1 };
        private static readonly int[] AxisY = { 0, 1, 1, -1 };

        /// <summary>
        /// A walkable cell is in a doorway when, along one of the four axes, the free run through it
        /// is at most <see cref="NarrowWidth"/> across, and across that (the way through) there is
        /// open ground on both sides: a gate in a wall, a gap between two buildings. A pocket open
        /// on one side only is a good place to stand, not a doorway.
        /// </summary>
        private void FindDoorways()
        {
            int w = _grid.Width, h = _grid.Height;
            for (var y = 0; y < h; y++)
            for (var x = 0; x < w; x++)
            {
                if (!_grid.IsWalkable(x, y)) continue;
                for (var axis = 0; axis < 4; axis++)
                {
                    int ax = AxisX[axis], ay = AxisY[axis];
                    var step = (ax != 0 && ay != 0 ? 1.41421356f : 1f) * _grid.CellSize;
                    var cap = (int)(NarrowWidth / step) + 1;
                    var across = 1 + Run(x, y, ax, ay, cap) + Run(x, y, -ax, -ay, cap);
                    if (across * step > NarrowWidth + 0.01f) continue;
                    // The way through is square to the narrow axis.
                    int px = -ay, py = ax;
                    if (Run(x, y, px, py, ThroughCells) < ThroughCells || Run(x, y, -px, -py, ThroughCells) < ThroughCells) continue;
                    _flags[_grid.Index(x, y)] |= LaneFlags.Narrow;
                    _narrowAxis[_grid.Index(x, y)] = (byte)axis;
                    break;
                }
            }
        }

        /// <summary>Walkable cells from (x, y) along (dx, dy), not counting the cell itself, up to <paramref name="cap"/>.</summary>
        private int Run(int x, int y, int dx, int dy, int cap)
        {
            var k = 0;
            while (k < cap && _grid.IsWalkable(x + dx * (k + 1), y + dy * (k + 1))) k++;
            return k;
        }

        /// <summary>
        /// Short doorways and the cells round their mouths are no-parking. Doorway cells are joined
        /// into runs (neighbouring cells, diagonals included) and measured in breadth-first order.
        /// </summary>
        private void MarkNoPark()
        {
            var n = _flags.Length;
            _stampId++;
            var run = new List<int>();
            for (var start = 0; start < n; start++)
            {
                if ((_flags[start] & LaneFlags.Narrow) == 0 || _stamp[start] == _stampId) continue;
                run.Clear();
                run.Add(start);
                _stamp[start] = _stampId;
                for (var head = 0; head < run.Count; head++)
                {
                    int cx = run[head] % _grid.Width, cy = run[head] / _grid.Width;
                    for (var dy = -1; dy <= 1; dy++)
                    for (var dx = -1; dx <= 1; dx++)
                    {
                        int nx = cx + dx, ny = cy + dy;
                        if (!_grid.InBounds(nx, ny)) continue;
                        var j = _grid.Index(nx, ny);
                        if ((_flags[j] & LaneFlags.Narrow) == 0 || _stamp[j] == _stampId) continue;
                        _stamp[j] = _stampId;
                        run.Add(j);
                    }
                }
                if (run.Count > MaxNoParkCells || _doorwayThrough.Count >= short.MaxValue) continue;
                // A doorway of its own: numbered, with the way through it (square to the narrow axis
                // of its first cell), so traffic can take turns through it.
                var axis = _narrowAxis[start];
                _doorwayThrough.Add(Vector2.Normalize(new Vector2(-AxisY[axis], AxisX[axis])));
                var id = (short)_doorwayThrough.Count;
                foreach (var i in run)
                {
                    int cx = i % _grid.Width, cy = i / _grid.Width;
                    for (var dy = -NoParkMouth; dy <= NoParkMouth; dy++)
                    for (var dx = -NoParkMouth; dx <= NoParkMouth; dx++)
                    {
                        if (!_grid.IsWalkable(cx + dx, cy + dy)) continue;
                        var j = _grid.Index(cx + dx, cy + dy);
                        _flags[j] |= LaneFlags.NoPark;
                        if (_doorway[j] == 0) _doorway[j] = id;
                    }
                }
            }
        }

        /// <summary>
        /// The nearest point to <paramref name="p"/> (within <paramref name="reach"/> metres) where a
        /// vehicle may stop: walkable and not no-parking. Ties go to the first cell found (a fixed
        /// ring order), so the answer never depends on anything but the map.
        /// </summary>
        public bool TryParkable(Vector2 p, float reach, out Vector2 spot)
        {
            spot = p;
            if (_grid.IsWalkable(p) && !NoParkAt(p)) return true;
            var (cx, cy) = _grid.CellOf(p);
            var rings = (int)MathF.Ceiling(reach / _grid.CellSize);
            for (var ring = 1; ring <= rings; ring++)
            {
                var best = float.MaxValue;
                for (var y = cy - ring; y <= cy + ring; y++)
                for (var x = cx - ring; x <= cx + ring; x++)
                {
                    if (Math.Abs(x - cx) != ring && Math.Abs(y - cy) != ring) continue;
                    if (!_grid.IsWalkable(x, y) || (_flags[_grid.Index(x, y)] & LaneFlags.NoPark) != 0) continue;
                    var c = _grid.CellCenter(x, y);
                    var d = Vector2.DistanceSquared(c, p);
                    if (d >= best) continue;
                    best = d;
                    spot = c;
                }
                if (best < float.MaxValue) return true;
            }
            return false;
        }

        /// <summary>
        /// A place to stand near <paramref name="p"/> (within <paramref name="reach"/>) that keeps off
        /// the roads and main routes where it can, and never in a doorway: the point itself when it
        /// is already clear of them.
        /// </summary>
        public Vector2 OffLane(Vector2 p, float reach)
        {
            var here = At(p);
            if (_grid.IsWalkable(p) && (here & (LaneFlags.NoPark | LaneFlags.Route | LaneFlags.Road)) == 0) return p;
            var best = p;
            var bestScore = _grid.IsWalkable(p) ? StandCost(p) : float.MaxValue;
            for (var ring = 1; ring * global::MachineBrigade.Sim.Content.SimTunables.Maps.LaneMap.OffLaneRingScale <= reach; ring++)
            {
                var around = 8 * ring;
                for (var k = 0; k < around; k++)
                {
                    var c = p + SimMath.Forward(k * SimMath.Tau / around) * (ring * 2f);
                    if (!_grid.IsWalkable(c) || !_grid.LineOfSight(p, c)) continue;
                    var score = StandCost(c) + ring * 2f;
                    if (score >= bestScore) continue;
                    bestScore = score;
                    best = c;
                }
            }
            return best;
        }

        /// <summary>What standing at <paramref name="p"/> costs the traffic (0 in the open).</summary>
        internal float StandCost(Vector2 p)
        {
            var f = At(p);
            if ((f & LaneFlags.NoPark) != 0) return 1000f;
            return ((f & LaneFlags.Road) != 0 ? global::MachineBrigade.Sim.Content.SimTunables.Maps.LaneMap.StandCostFTrue : 0f) + ((f & LaneFlags.Route) != 0 ? global::MachineBrigade.Sim.Content.SimTunables.Maps.LaneMap.StandCostRouteCountAtScale * RouteCountAt(p) : 0f);
        }

        // ------------------------------------------------------------------ firing-spot reservations

        /// <summary>
        /// Books the 3 x 3 cells round <paramref name="p"/> for <paramref name="owner"/> (a gun's
        /// firing spot), releasing its previous booking first.
        /// </summary>
        internal void Reserve(Vector2 p, Vehicle owner)
        {
            Release(owner);
            var (cx, cy) = _grid.CellOf(p);
            for (var y = cy - 1; y <= cy + 1; y++)
            for (var x = cx - 1; x <= cx + 1; x++)
                if (_grid.InBounds(x, y)) _reservedBy[_grid.Index(x, y)] = owner.Id.Value;
            owner.Traffic.ReservedAt = p;
            owner.Traffic.HasReservation = true;
        }

        internal void Release(Vehicle owner)
        {
            if (!owner.Traffic.HasReservation) return;
            owner.Traffic.HasReservation = false;
            var (cx, cy) = _grid.CellOf(owner.Traffic.ReservedAt);
            for (var y = cy - 1; y <= cy + 1; y++)
            for (var x = cx - 1; x <= cx + 1; x++)
                if (_grid.InBounds(x, y) && _reservedBy[_grid.Index(x, y)] == owner.Id.Value) _reservedBy[_grid.Index(x, y)] = 0;
        }

        /// <summary>
        /// Whether a 3 x 3 booking round <paramref name="p"/> would overlap one another living vehicle
        /// holds and still uses (a booking left behind by a gun that moved on does not count).
        /// </summary>
        internal bool ReservedByOther(Vector2 p, EntityId self, SimWorld world)
        {
            var (cx, cy) = _grid.CellOf(p);
            for (var y = cy - 2; y <= cy + 2; y++)
            for (var x = cx - 2; x <= cx + 2; x++)
            {
                if (!_grid.InBounds(x, y)) continue;
                var owner = _reservedBy[_grid.Index(x, y)];
                if (owner == 0 || owner == self.Value) continue;
                if (world.TryGetVehicle(new EntityId(owner), out var o) && InUse(o)) return true;
            }
            return false;
        }

        /// <summary>A vehicle's booking still stands: it is at its booked spot or ordered there.</summary>
        internal static bool InUse(Vehicle o)
        {
            if (!o.IsAlive || !o.Traffic.HasReservation) return false;
            var at = o.Traffic.ReservedAt;
            // AI MASTER P1 (spec 41): the booking is an occupancy lease: it lapses once the gun is more than
            // ai.traffic.parkingLeaveM (5 m) from it and no longer ordered there.
            var leave = Content.SimTunables.Ai.Traffic.ParkingLeaveM;
            // (An idle order has no point: its default (0, 0) is not "ordered there".)
            return Vector2.DistanceSquared(o.Position, at) < leave * leave ||
                   (o.Order.Kind != OrderKind.Idle && Vector2.DistanceSquared(o.Order.Point, at) < leave * leave);
        }

        /// <summary>The owner of the booking on the cell under <paramref name="p"/> (0 for none; tests).</summary>
        internal int ReservationAt(Vector2 p)
        {
            var (x, y) = _grid.CellOf(p);
            return _grid.InBounds(x, y) ? _reservedBy[_grid.Index(x, y)] : 0;
        }
    }
}
