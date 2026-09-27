#nullable enable
using System;
using System.Numerics;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>
    /// Walkability of the battlefield on a square grid centred on the origin. Blockers are
    /// reference-counted per cell, so removing one building never unblocks a neighbour that
    /// overlaps the same cells.
    /// </summary>
    public sealed class NavGrid
    {
        private readonly int[] _blockers;

        public NavGrid(float worldSize, float cellSize)
        {
            if (!(worldSize > 0f) || !(cellSize > 0f)) throw new ArgumentException("Grid sizes must be positive.");
            CellSize = cellSize;
            Width = Height = (int)MathF.Ceiling(worldSize / cellSize);
            HalfExtent = Width * cellSize * 0.5f;
            _blockers = new int[Width * Height];
        }

        public int Width { get; }
        public int Height { get; }
        public float CellSize { get; }
        public float HalfExtent { get; }

        /// <summary>Increments whenever walkability changes, so cached paths can be revalidated.</summary>
        public int Version { get; private set; }

        public bool InBounds(int x, int y) => x >= 0 && y >= 0 && x < Width && y < Height;

        public int Index(int x, int y) => y * Width + x;

        public (int x, int y) CellOf(Vector2 p) =>
            ((int)MathF.Floor((p.X + HalfExtent) / CellSize), (int)MathF.Floor((p.Y + HalfExtent) / CellSize));

        public Vector2 CellCenter(int x, int y) =>
            new Vector2((x + 0.5f) * CellSize - HalfExtent, (y + 0.5f) * CellSize - HalfExtent);

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
        public void AddBlocker(Vector2 center, float width, float depth, float clearance) =>
            ChangeRect(center, width + 2f * clearance, depth + 2f * clearance, +1);

        public void RemoveBlocker(Vector2 center, float width, float depth, float clearance) =>
            ChangeRect(center, width + 2f * clearance, depth + 2f * clearance, -1);

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
