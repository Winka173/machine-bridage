#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>
    /// Extra step costs for one search: parked hulls stamped on the grid, the one hull in the way
    /// stamped dearer still, and a cap on how many cells the search may expand. Costs never make a
    /// cell unwalkable, so a route through a crowd is still found when it is the only one.
    /// </summary>
    public sealed class PathCosts
    {
        /// <summary>Per cell: a step into a cell costs its length times (1 + extra * <see cref="Scale"/>).</summary>
        public byte[]? Extra;

        public float Scale = 0.1f;

        /// <summary>Cells this close to the start cost nothing extra: they are under the requester's own hull.</summary>
        public Vector2 Start;
        public float StartSkip;

        /// <summary>The hull in the way, as a capsule: its cells cost <see cref="BlockerCost"/> at least, so the route really leaves it.</summary>
        public bool HasBlocker;
        public Vector2 BlockerA, BlockerB;
        public float BlockerRadius;
        public int BlockerCost = 120;

        /// <summary>The search gives up (fails) after expanding this many cells: a node budget, never a clock.</summary>
        public int MaxExpansions = int.MaxValue;

        /// <summary>
        /// Smoothing may draw a straight line across cells up to this dear (or as dear as the cells
        /// the raw path itself crossed), never straight back through a parked hull.
        /// </summary>
        public int SmoothLimit = 20;

        /// <summary>Cells the last search expanded.</summary>
        public int Expansions;
    }

    /// <summary>
    /// A* over <see cref="NavGrid"/> with 8-way moves (no corner cutting), followed by
    /// line-of-sight smoothing so vehicles drive straight lines instead of staircases.
    /// Buffers are reused between searches; stamps avoid clearing them each time.
    /// </summary>
    public sealed class PathFinder
    {
        private const float Diagonal = 1.41421356f;
        private static readonly int[] Dx = { 1, -1, 0, 0, 1, 1, -1, -1 };
        private static readonly int[] Dy = { 0, 0, 1, -1, 1, -1, 1, -1 };

        private readonly NavGrid _grid;
        private readonly float[] _cost;
        private readonly int[] _parent;
        private readonly int[] _seen;
        private readonly int[] _closed;
        private readonly MinHeap _open;
        private readonly List<Vector2> _raw = new();
        private readonly List<int> _rawExtra = new();
        private int _search;

        public PathFinder(NavGrid grid)
        {
            _grid = grid;
            var n = grid.Width * grid.Height;
            _cost = new float[n];
            _parent = new int[n];
            _seen = new int[n];
            _closed = new int[n];
            _open = new MinHeap(256);
        }

        /// <summary>
        /// Fills <paramref name="result"/> with waypoints from <paramref name="from"/> towards
        /// <paramref name="to"/>. An unwalkable goal resolves to the nearest walkable point.
        /// </summary>
        public bool TryFindPath(Vector2 from, Vector2 to, List<Vector2> result) => TryFindPath(from, to, result, null);

        /// <summary>
        /// The same, paying <paramref name="costs"/> on every step (null: plain distance). With
        /// costs the smoothing keeps to the cheap cells too: a straight line that shortcut back
        /// through a parked hull would undo the detour.
        /// </summary>
        public bool TryFindPath(Vector2 from, Vector2 to, List<Vector2> result, PathCosts? costs)
        {
            result.Clear();
            if (costs != null) costs.Expansions = 0;
            if (!_grid.TryNearestWalkable(to, 16, out var goal)) return false;

            if (_grid.LineOfSight(from, goal) && (costs == null || MaxExtraAlong(from, goal, costs) <= costs.SmoothLimit))
            {
                result.Add(goal);
                return true;
            }

            var (sx, sy) = _grid.CellOf(from);
            if (!_grid.IsWalkable(sx, sy))
            {
                if (!_grid.TryNearestWalkable(from, 4, out var start)) return false;
                (sx, sy) = _grid.CellOf(start);
            }
            var (gx, gy) = _grid.CellOf(goal);
            var startIndex = _grid.Index(sx, sy);
            var goalIndex = _grid.Index(gx, gy);

            _search++;
            _open.Clear();
            _cost[startIndex] = 0f;
            _parent[startIndex] = -1;
            _seen[startIndex] = _search;
            _open.Push(startIndex, Heuristic(sx, sy, gx, gy));

            var found = false;
            while (_open.Count > 0)
            {
                var current = _open.Pop();
                if (_closed[current] == _search) continue;
                _closed[current] = _search;
                if (costs != null && ++costs.Expansions > costs.MaxExpansions) return false;
                if (current == goalIndex)
                {
                    found = true;
                    break;
                }

                var cx = current % _grid.Width;
                var cy = current / _grid.Width;
                for (var k = 0; k < 8; k++)
                {
                    int nx = cx + Dx[k], ny = cy + Dy[k];
                    if (!_grid.IsWalkable(nx, ny)) continue;
                    var diagonal = k >= 4;
                    if (diagonal && (!_grid.IsWalkable(cx + Dx[k], cy) || !_grid.IsWalkable(cx, cy + Dy[k]))) continue;

                    var next = _grid.Index(nx, ny);
                    if (_closed[next] == _search) continue;
                    var step = diagonal ? Diagonal : 1f;
                    if (costs != null) step *= 1f + Extra(next, costs) * costs.Scale;
                    var cost = _cost[current] + step;
                    if (_seen[next] == _search && cost >= _cost[next]) continue;
                    _seen[next] = _search;
                    _cost[next] = cost;
                    _parent[next] = current;
                    _open.Push(next, cost + Heuristic(nx, ny, gx, gy));
                }
            }

            if (!found) return false;

            _raw.Clear();
            _rawExtra.Clear();
            for (var i = goalIndex; i != -1 && i != startIndex; i = _parent[i])
            {
                _raw.Add(_grid.CellCenter(i % _grid.Width, i / _grid.Width));
                _rawExtra.Add(costs != null ? Extra(i, costs) : 0);
            }
            _raw.Reverse();
            _rawExtra.Reverse();
            if (_raw.Count == 0)
            {
                _raw.Add(goal);
                _rawExtra.Add(0);
            }
            else _raw[_raw.Count - 1] = goal;

            Smooth(from, result, costs);
            return true;
        }

        private void Smooth(Vector2 from, List<Vector2> result, PathCosts? costs)
        {
            var anchor = from;
            var i = 0;
            while (i < _raw.Count)
            {
                var j = _raw.Count - 1;
                while (j > i && !Shortcut(anchor, i, j, costs)) j--;
                result.Add(_raw[j]);
                anchor = _raw[j];
                i = j + 1;
            }
        }

        /// <summary>
        /// Whether a straight line from <paramref name="anchor"/> can replace raw cells i to j: in
        /// plain sight and, with costs, crossing nothing dearer than those cells did.
        /// </summary>
        private bool Shortcut(Vector2 anchor, int i, int j, PathCosts? costs)
        {
            if (!_grid.LineOfSight(anchor, _raw[j])) return false;
            if (costs == null) return true;
            var allowed = costs.SmoothLimit;
            for (var k = i; k <= j; k++) allowed = Math.Max(allowed, _rawExtra[k]);
            return MaxExtraAlong(anchor, _raw[j], costs) <= allowed;
        }

        /// <summary>A cell's extra cost in this search: the stamped hulls, the blocker, and nothing under the requester.</summary>
        private int Extra(int index, PathCosts costs)
        {
            var c = _grid.CellCenter(index % _grid.Width, index / _grid.Width);
            if (Vector2.DistanceSquared(c, costs.Start) < costs.StartSkip * costs.StartSkip) return 0;
            var extra = costs.Extra != null ? costs.Extra[index] : 0;
            if (costs.HasBlocker && extra < costs.BlockerCost)
            {
                var ab = costs.BlockerB - costs.BlockerA;
                var length = ab.LengthSquared();
                var t = length > 1e-6f ? Math.Clamp(Vector2.Dot(c - costs.BlockerA, ab) / length, 0f, 1f) : 0f;
                if (Vector2.DistanceSquared(c, costs.BlockerA + ab * t) < costs.BlockerRadius * costs.BlockerRadius) extra = costs.BlockerCost;
            }
            return extra;
        }

        /// <summary>The dearest cell a straight line from a to b crosses (sampled every quarter cell).</summary>
        private int MaxExtraAlong(Vector2 a, Vector2 b, PathCosts costs)
        {
            var delta = b - a;
            var steps = Math.Max(1, (int)MathF.Ceiling(delta.Length() / (_grid.CellSize * 0.25f)));
            var worst = 0;
            var last = -1;
            for (var s = 0; s <= steps; s++)
            {
                var (x, y) = _grid.CellOf(a + delta * (s / (float)steps));
                if (!_grid.InBounds(x, y)) continue;
                var index = _grid.Index(x, y);
                if (index == last) continue;
                last = index;
                worst = Math.Max(worst, Extra(index, costs));
            }
            return worst;
        }

        private static float Heuristic(int x, int y, int gx, int gy)
        {
            int dx = Math.Abs(x - gx), dy = Math.Abs(y - gy);
            return dx + dy + (Diagonal - 2f) * Math.Min(dx, dy);
        }

        /// <summary>Binary min-heap of cell indices; stale duplicates are skipped by the closed set.</summary>
        private sealed class MinHeap
        {
            private int[] _items;
            private float[] _priorities;

            public MinHeap(int capacity)
            {
                _items = new int[capacity];
                _priorities = new float[capacity];
            }

            public int Count { get; private set; }

            public void Clear() => Count = 0;

            public void Push(int item, float priority)
            {
                if (Count == _items.Length)
                {
                    Array.Resize(ref _items, Count * 2);
                    Array.Resize(ref _priorities, Count * 2);
                }
                var i = Count++;
                while (i > 0)
                {
                    var parent = (i - 1) / 2;
                    if (_priorities[parent] <= priority) break;
                    _items[i] = _items[parent];
                    _priorities[i] = _priorities[parent];
                    i = parent;
                }
                _items[i] = item;
                _priorities[i] = priority;
            }

            public int Pop()
            {
                var top = _items[0];
                var lastItem = _items[--Count];
                var lastPriority = _priorities[Count];
                var i = 0;
                while (true)
                {
                    var child = 2 * i + 1;
                    if (child >= Count) break;
                    if (child + 1 < Count && _priorities[child + 1] < _priorities[child]) child++;
                    if (_priorities[child] >= lastPriority) break;
                    _items[i] = _items[child];
                    _priorities[i] = _priorities[child];
                    i = child;
                }
                _items[i] = lastItem;
                _priorities[i] = lastPriority;
                return top;
            }
        }
    }
}
