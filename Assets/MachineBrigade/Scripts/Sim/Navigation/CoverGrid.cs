#nullable enable
using System;
using System.Numerics;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>
    /// Where a direct-fire round cannot pass: the footprints of props that stand tall enough to
    /// stop it (buildings, rock, fortress walls), on a one-metre grid. Low cover (sandbags, tank
    /// traps, barriers) and open structures are not in it. Footprints are drawn a little inside
    /// their edges, so a shot grazing a corner still gets through. Counts per cell, so knocking
    /// down one building never clears a neighbour overlapping the same cells.
    /// </summary>
    public sealed class CoverGrid
    {
        private const float CellSize = 1f;

        /// <summary>How far inside a footprint's edge the cover starts, in metres.</summary>
        private const float Inset = 0.35f;

        /// <summary>Spacing of the samples along a line of fire.</summary>
        private const float Step = 0.5f;

        private readonly int[] _count;
        private readonly int _size;
        private readonly float _half;

        public CoverGrid(float worldSize)
        {
            _size = (int)MathF.Ceiling(worldSize / CellSize);
            _half = _size * CellSize * 0.5f;
            _count = new int[_size * _size];
        }

        public void Add(Prop prop) => Change(prop, +1);

        /// <summary>Makes every cell whose centre fails <paramref name="open"/> stop fire for good (terrain beyond the outline).</summary>
        public void BlockWhere(Func<Vector2, bool> open)
        {
            for (var y = 0; y < _size; y++)
            for (var x = 0; x < _size; x++)
            {
                var centre = new Vector2((x + 0.5f) * CellSize - _half, (y + 0.5f) * CellSize - _half);
                if (!open(centre)) _count[y * _size + x]++;
            }
        }

        public void Remove(Prop prop) => Change(prop, -1);

        public bool IsBlocked(Vector2 p)
        {
            var x = (int)MathF.Floor((p.X + _half) / CellSize);
            var y = (int)MathF.Floor((p.Y + _half) / CellSize);
            return x >= 0 && y >= 0 && x < _size && y < _size && _count[y * _size + x] > 0;
        }

        /// <summary>
        /// The first point along <paramref name="from"/> to <paramref name="to"/> where cover
        /// stops a round, skipping the first <paramref name="skipStart"/> metres (the shooter's
        /// own hull) and the last <paramref name="skipEnd"/>, and ignoring the footprint of
        /// <paramref name="ignore"/> (a building being shot at is not in its own way).
        /// </summary>
        public bool TryFirstHit(Vector2 from, Vector2 to, float skipStart, float skipEnd, Prop? ignore, out Vector2 hit)
        {
            var delta = to - from;
            var length = delta.Length();
            hit = default;
            if (length < 1e-3f) return false;
            var direction = delta / length;
            for (var d = skipStart; d <= length - skipEnd; d += Step)
            {
                var p = from + direction * d;
                if (!IsBlocked(p)) continue;
                if (ignore != null && Inside(ignore, p)) continue;
                hit = p;
                return true;
            }
            return false;
        }

        /// <summary>Whether <paramref name="p"/> lies on the prop's footprint (grown by half a cell, so its edge cells count as its own).</summary>
        public static bool Inside(Prop prop, Vector2 p) =>
            MathF.Abs(p.X - prop.Position.X) <= prop.Width * 0.5f + CellSize * 0.5f &&
            MathF.Abs(p.Y - prop.Position.Y) <= prop.Depth * 0.5f + CellSize * 0.5f;

        private void Change(Prop prop, int delta)
        {
            var hw = MathF.Max(0.1f, prop.Width * 0.5f - Inset);
            var hd = MathF.Max(0.1f, prop.Depth * 0.5f - Inset);
            var minX = (int)MathF.Floor((prop.Position.X - hw + _half) / CellSize);
            var maxX = (int)MathF.Floor((prop.Position.X + hw + _half) / CellSize);
            var minY = (int)MathF.Floor((prop.Position.Y - hd + _half) / CellSize);
            var maxY = (int)MathF.Floor((prop.Position.Y + hd + _half) / CellSize);
            for (var y = Math.Max(0, minY); y <= Math.Min(_size - 1, maxY); y++)
            for (var x = Math.Max(0, minX); x <= Math.Min(_size - 1, maxX); x++)
            {
                var i = y * _size + x;
                _count[i] = Math.Max(0, _count[i] + delta);
            }
        }
    }
}
