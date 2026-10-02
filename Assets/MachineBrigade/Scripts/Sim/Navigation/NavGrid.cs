#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>
    /// Walkability of the battlefield on a grid over the map's rectangle (a square centred on the
    /// origin, or a long battlefield's own corners). Blockers are reference-counted per cell, so
    /// removing one building never unblocks a neighbour that overlaps the same cells.
    /// </summary>
    public sealed class NavGrid
    {
        private readonly int[] _blockers;

        public NavGrid(float worldSize, float cellSize) : this(new Vector2(-(int)MathF.Ceiling(worldSize / cellSize) * cellSize * 0.5f), worldSize, worldSize, cellSize)
        {
        }

        /// <summary>A grid from the south-west corner <paramref name="origin"/>, <paramref name="width"/> along x and <paramref name="length"/> along z.</summary>
        public NavGrid(Vector2 origin, float width, float length, float cellSize)
        {
            if (!(width > 0f) || !(length > 0f) || !(cellSize > 0f)) throw new ArgumentException("Grid sizes must be positive.");
            CellSize = cellSize;
            Width = (int)MathF.Ceiling(width / cellSize);
            Height = (int)MathF.Ceiling(length / cellSize);
            Origin = origin;
            _blockers = new int[Width * Height];
        }

        public int Width { get; }
        public int Height { get; }
        public float CellSize { get; }

        /// <summary>The south-west corner of cell (0, 0).</summary>
        public Vector2 Origin { get; }

        /// <summary>Bytes the grid's own arrays hold (blockers and regions), for the path-memory budget (prompt 17 A.5).</summary>
        public long MemoryBytes => (_blockers.Length + _region.Length + _queue.Length) * 4L;

        /// <summary>Increments whenever walkability changes, so cached paths can be revalidated.</summary>
        public int Version { get; private set; }

        public bool InBounds(int x, int y) => x >= 0 && y >= 0 && x < Width && y < Height;

        // ------------------------------------------------------------------ prompt 33 L3: terrain tags

        private byte[]? _terrain;

        /// <summary>Whether any cell has a tag other than NORMAL (else the path costs are plain distance, as before).</summary>
        public bool HasTerrain => _terrain != null;

        /// <summary>
        /// Prompt 33 L3: the static terrain tags (map data "terrain"): every cell whose centre lies in a zone takes its tag (a
        /// later zone over an earlier one wins; the tool writes none that overlap). Set once as the world is built; no tick
        /// changes them, so the path costs never swing.
        /// </summary>
        public void SetTerrain(IReadOnlyList<TerrainZoneDef> zones)
        {
            if (zones.Count == 0)
            {
                _terrain = null;
                return;
            }
            var tags = new byte[Width * Height];
            var any = false;
            foreach (var z in zones)
            {
                if (z.Tag == TerrainTag.Normal) continue;
                // The cells whose centres lie inside [Min, Max).
                var x0 = Math.Max(0, (int)MathF.Ceiling((z.Min.X - Origin.X) / CellSize - 0.5f));
                var y0 = Math.Max(0, (int)MathF.Ceiling((z.Min.Y - Origin.Y) / CellSize - 0.5f));
                var x1 = Math.Min(Width - 1, (int)MathF.Ceiling((z.Max.X - Origin.X) / CellSize - 0.5f) - 1);
                var y1 = Math.Min(Height - 1, (int)MathF.Ceiling((z.Max.Y - Origin.Y) / CellSize - 0.5f) - 1);
                for (var y = y0; y <= y1; y++)
                    for (var x = x0; x <= x1; x++)
                    {
                        tags[Index(x, y)] = (byte)z.Tag;
                        any = true;
                    }
            }
            _terrain = any ? tags : null;
        }

        public TerrainTag TerrainAt(int x, int y) => _terrain != null && InBounds(x, y) ? (TerrainTag)_terrain[Index(x, y)] : TerrainTag.Normal;

        public TerrainTag TerrainAt(Vector2 p)
        {
            var (x, y) = CellOf(p);
            return TerrainAt(x, y);
        }

        /// <summary>The static path cost of a cell (its tag's, <see cref="TerrainRules.PathCost"/>; 1 on a grid without tags).</summary>
        public float StepCost(int index) => _terrain == null ? 1f : TerrainRules.PathCost((TerrainTag)_terrain[index]);

        /// <summary>The cheapest cell's cost (the heuristic's scale): a road's on a grid with tags, else 1.</summary>
        public float MinStepCost => _terrain == null ? 1f : TerrainRules.MinPathCost;

        public int Index(int x, int y) => y * Width + x;

        public (int x, int y) CellOf(Vector2 p) =>
            ((int)MathF.Floor((p.X - Origin.X) / CellSize), (int)MathF.Floor((p.Y - Origin.Y) / CellSize));

        public Vector2 CellCenter(int x, int y) =>
            new Vector2(Origin.X + (x + 0.5f) * CellSize, Origin.Y + (y + 0.5f) * CellSize);

        public bool IsWalkable(int x, int y) => InBounds(x, y) && _blockers[Index(x, y)] == 0;

        public bool IsWalkable(Vector2 p)
        {
            var (x, y) = CellOf(p);
            return IsWalkable(x, y);
        }

        /// <summary>
        /// Marks a footprint as blocked, grown by <paramref name="clearance"/> on every side so
        /// vehicles keep their hulls out of walls without per-vehicle grids.
        /// </summary>
        public void AddBlocker(Vector2 center, float width, float depth, float clearance)
        {
            ChangeRect(center, width + 2f * clearance, depth + 2f * clearance, +1);
            // (Routes planned across this ground are stale now: the movement system looks at these.)
            var half = new Vector2(width * 0.5f + clearance, depth * 0.5f + clearance);
            _closed.Add((center - half, center + half));
        }

        public void RemoveBlocker(Vector2 center, float width, float depth, float clearance) =>
            ChangeRect(center, width + 2f * clearance, depth + 2f * clearance, -1);

        /// <summary>
        /// Prompt 31 L3: a prebuilt state's rectangle in (+1) or out (-1) without telling the routes (the load-time build and
        /// check of <see cref="NavStates"/>; a switch during the battle closes ground through <see cref="AddBlocker"/>).
        /// </summary>
        internal void Mark(NavBlock block, int delta) =>
            ChangeRect(block.Center, block.Width + 2f * block.Clearance, block.Depth + 2f * block.Clearance, delta);

        /// <summary>Blocks every cell whose centre fails <paramref name="open"/> for good (terrain outside the map's outline).</summary>
        public void BlockWhere(Func<Vector2, bool> open)
        {
            for (var y = 0; y < Height; y++)
            for (var x = 0; x < Width; x++)
                if (!open(CellCenter(x, y))) _blockers[Index(x, y)]++;
            Version++;
        }

        private void ChangeRect(Vector2 center, float width, float depth, int delta)
        {
            var half = new Vector2(width * 0.5f, depth * 0.5f);
            var (minX, minY) = CellOf(center - half);
            var (maxX, maxY) = CellOf(center + half - new Vector2(1e-4f));
            for (var y = Math.Max(0, minY); y <= Math.Min(Height - 1, maxY); y++)
            for (var x = Math.Max(0, minX); x <= Math.Min(Width - 1, maxX); x++)
            {
                var i = Index(x, y);
                _blockers[i] = Math.Max(0, _blockers[i] + delta);
            }
            Version++;
        }

        // ------------------------------------------------------------------ closed ground (prompt 12)

        private readonly List<(Vector2 min, Vector2 max)> _closed = new();

        /// <summary>
        /// Every rectangle closed by <see cref="AddBlocker"/> so far, in order (a tower raised, a
        /// wreck anchored): routes planned before one of them may run into it now. Readers keep
        /// their own count of the ones they have seen.
        /// </summary>
        public IReadOnlyList<(Vector2 min, Vector2 max)> Closed => _closed;

        // ------------------------------------------------------------------ regions (prompt 12)

        private int[] _region = Array.Empty<int>();
        private int[] _queue = Array.Empty<int>();
        private readonly List<int> _regionSizes = new();
        private int _regionVersion = -1;
        private int _mainRegion;

        /// <summary>
        /// The connected open ground the cell belongs to (numbered from 1; 0 for a blocked cell or
        /// one off the grid). Two cells of one region are joined by a route; cells of two regions are
        /// not (a pocket sealed by walls, a yard behind a shut gate). Worked out again after
        /// walkability changes, when first asked. Four-neighbour, as the route search's corner rule
        /// makes it.
        /// </summary>
        public int RegionOf(int x, int y)
        {
            if (!InBounds(x, y)) return 0;
            Label();
            return _region[Index(x, y)];
        }

        public int RegionOf(Vector2 p)
        {
            var (x, y) = CellOf(p);
            return RegionOf(x, y);
        }

        /// <summary>Open cells in a region (a pocket's size in the stuck report).</summary>
        public int RegionSize(int region)
        {
            Label();
            return region > 0 && region < _regionSizes.Count ? _regionSizes[region] : 0;
        }

        /// <summary>The largest region: the battlefield's open ground (the rest are pockets sealed off from it).</summary>
        public int MainRegion
        {
            get
            {
                Label();
                return _mainRegion;
            }
        }

        private void Label()
        {
            if (_regionVersion == Version && _region.Length > 0) return;
            _regionVersion = Version;
            var n = Width * Height;
            if (_region.Length != n)
            {
                _region = new int[n];
                _queue = new int[n];
            }
            Array.Clear(_region, 0, n);
            _regionSizes.Clear();
            _regionSizes.Add(0);
            _mainRegion = 0;
            var next = 0;
            for (var start = 0; start < n; start++)
            {
                if (_region[start] != 0 || _blockers[start] != 0) continue;
                next++;
                _region[start] = next;
                int head = 0, tail = 0;
                _queue[tail++] = start;
                while (head < tail)
                {
                    var i = _queue[head++];
                    int x = i % Width, y = i / Width;
                    if (x + 1 < Width && Fill(i + 1)) _queue[tail++] = i + 1;
                    if (x > 0 && Fill(i - 1)) _queue[tail++] = i - 1;
                    if (y + 1 < Height && Fill(i + Width)) _queue[tail++] = i + Width;
                    if (y > 0 && Fill(i - Width)) _queue[tail++] = i - Width;
                }
                _regionSizes.Add(tail);
                if (tail > _regionSizes[_mainRegion]) _mainRegion = next;

                bool Fill(int j)
                {
                    if (_region[j] != 0 || _blockers[j] != 0) return false;
                    _region[j] = next;
                    return true;
                }
            }
        }

        /// <summary>
        /// Like <see cref="TryNearestWalkable(Vector2, int, out Vector2)"/>, but only open ground of
        /// <paramref name="region"/> counts (0: any): where a vehicle standing in that region can
        /// actually get to near the point. The point itself when it is in the region.
        /// </summary>
        public bool TryNearestInRegion(Vector2 point, int region, int maxRings, out Vector2 result)
        {
            if (region <= 0) return TryNearestWalkable(point, maxRings, out result);
            var (cx, cy) = CellOf(point);
            if (RegionOf(cx, cy) == region)
            {
                result = point;
                return true;
            }
            // Rings are squares: once one holds a cell, the rings out to 1.42 times as far may still
            // hold a nearer one (a wall's side beats the pocket's corner).
            var found = float.MaxValue;
            var last = maxRings;
            result = default;
            for (var ring = 1; ring <= last; ring++)
            {
                for (var y = cy - ring; y <= cy + ring; y++)
                for (var x = cx - ring; x <= cx + ring; x++)
                {
                    if (Math.Abs(x - cx) != ring && Math.Abs(y - cy) != ring) continue;
                    if (RegionOf(x, y) != region) continue;
                    var center = CellCenter(x, y);
                    var d = Vector2.DistanceSquared(center, point);
                    if (d >= found) continue;
                    if (found == float.MaxValue) last = Math.Min(maxRings, (int)MathF.Ceiling(ring * 1.42f));
                    found = d;
                    result = center;
                }
            }
            return found < float.MaxValue;
        }

        // ------------------------------------------------------------------ distances over the ground (prompt 12)

        private int[] _steps = Array.Empty<int>();
        private int[] _stepStamp = Array.Empty<int>();
        private int _stepSearch;

        /// <summary>
        /// Walks the open ground out from <paramref name="origin"/> (four-neighbour, at most
        /// <paramref name="radius"/> metres out as the crow flies); <see cref="StepsTo"/> then tells
        /// how many cells away over the ground each cell is. A group's slots stay on the near side
        /// of a wall with it (see <see cref="Formation"/>).
        /// </summary>
        public void WalkFrom(Vector2 origin, float radius)
        {
            var n = Width * Height;
            if (_steps.Length != n)
            {
                _steps = new int[n];
                _stepStamp = new int[n];
                if (_queue.Length != n) _queue = new int[n];
                Label();
            }
            _stepSearch++;
            var (ox, oy) = CellOf(origin);
            if (!IsWalkable(ox, oy)) return;
            var reach = (int)MathF.Ceiling(radius / CellSize);
            int head = 0, tail = 0;
            var start = Index(ox, oy);
            _steps[start] = 0;
            _stepStamp[start] = _stepSearch;
            _queue[tail++] = start;
            while (head < tail)
            {
                var i = _queue[head++];
                int x = i % Width, y = i / Width;
                var d = _steps[i] + 1;
                for (var k = 0; k < 4; k++)
                {
                    int nx = x + (k == 0 ? 1 : k == 1 ? -1 : 0), ny = y + (k == 2 ? 1 : k == 3 ? -1 : 0);
                    if (!InBounds(nx, ny) || Math.Abs(nx - ox) > reach || Math.Abs(ny - oy) > reach) continue;
                    var j = Index(nx, ny);
                    if (_stepStamp[j] == _stepSearch || _blockers[j] != 0) continue;
                    _stepStamp[j] = _stepSearch;
                    _steps[j] = d;
                    _queue[tail++] = j;
                }
            }
        }

        /// <summary>Cells over the ground from the last <see cref="WalkFrom"/> origin to the cell under <paramref name="p"/> (-1: not reached).</summary>
        public int StepsTo(Vector2 p)
        {
            var (x, y) = CellOf(p);
            if (!InBounds(x, y) || _stepStamp.Length == 0) return -1;
            var i = Index(x, y);
            return _stepStamp[i] == _stepSearch ? _steps[i] : -1;
        }

        /// <summary>
        /// True when a strip a quarter-cell either side of the segment only crosses walkable
        /// cells. The width stops paths squeezing diagonally between two blocked corners.
        /// </summary>
        public bool LineOfSight(Vector2 from, Vector2 to)
        {
            var delta = to - from;
            var length = delta.Length();
            var side = length > 1e-5f ? new Vector2(-delta.Y, delta.X) * (CellSize * 0.25f / length) : Vector2.Zero;
            var steps = Math.Max(1, (int)MathF.Ceiling(length / (CellSize * 0.25f)));
            for (var i = 0; i <= steps; i++)
            {
                var p = from + delta * (i / (float)steps);
                if (!IsWalkable(p) || !IsWalkable(p + side) || !IsWalkable(p - side)) return false;
            }
            return true;
        }

        /// <summary>
        /// The point itself when walkable, otherwise the centre of the nearest walkable cell
        /// within <paramref name="maxRings"/> rings. Unreachable orders resolve here instead of
        /// looping forever.
        /// </summary>
        public bool TryNearestWalkable(Vector2 point, int maxRings, out Vector2 result)
        {
            var (cx, cy) = CellOf(point);
            if (IsWalkable(cx, cy))
            {
                result = point;
                return true;
            }

            for (var ring = 1; ring <= maxRings; ring++)
            {
                var best = float.MaxValue;
                result = default;
                for (var y = cy - ring; y <= cy + ring; y++)
                for (var x = cx - ring; x <= cx + ring; x++)
                {
                    if (Math.Abs(x - cx) != ring && Math.Abs(y - cy) != ring) continue; // ring edge only
                    if (!IsWalkable(x, y)) continue;
                    var center = CellCenter(x, y);
                    var d = Vector2.DistanceSquared(center, point);
                    if (d < best)
                    {
                        best = d;
                        result = center;
                    }
                }
                if (best < float.MaxValue) return true;
            }

            result = default;
            return false;
        }
    }
}
