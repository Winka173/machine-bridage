#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;

namespace MachineBrigade.Sim.Navigation
{
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
        public bool TryFindPath(Vector2 from, Vector2 to, List<Vector2> result)
        {
            result.Clear();
            if (!_grid.TryNearestWalkable(to, 16, out var goal)) return false;

            if (_grid.LineOfSight(from, goal))
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
                    var cost = _cost[current] + (diagonal ? Diagonal : 1f);
                    if (_seen[next] == _search && cost >= _cost[next]) continue;
                    _seen[next] = _search;
                    _cost[next] = cost;
                    _parent[next] = current;
                    _open.Push(next, cost + Heuristic(nx, ny, gx, gy));
                }
            }

            if (!found) return false;

            _raw.Clear();
            for (var i = goalIndex; i != -1 && i != startIndex; i = _parent[i])
                _raw.Add(_grid.CellCenter(i % _grid.Width, i / _grid.Width));
            _raw.Reverse();
            if (_raw.Count == 0) _raw.Add(goal);
            else _raw[_raw.Count - 1] = goal;

            Smooth(from, result);
            return true;
        }

        private void Smooth(Vector2 from, List<Vector2> result)
        {
            var anchor = from;
            var i = 0;
            while (i < _raw.Count)
            {
                var j = _raw.Count - 1;
                while (j > i && !_grid.LineOfSight(anchor, _raw[j])) j--;
                result.Add(_raw[j]);
                anchor = _raw[j];
                i = j + 1;
            }
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
