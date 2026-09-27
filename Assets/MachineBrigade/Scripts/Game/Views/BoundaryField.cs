using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Signed distance to the battlefield's outline (positive outside, negative inside), sampled on
    /// a 1 m grid round the map so the terrain, the scenery, the ground paint and the minimap can
    /// ask it millions of times at load. Beyond the grid (and on a map without an outline) it is
    /// the distance to the square's edge. Built once per map and shared.
    /// </summary>
    public sealed class BoundaryField
    {
        private const float Cell = 1f;
        private const float Margin = 24f;

        private static BoundaryField _cached;
        private static MapDefinition _cachedMap;

        private readonly float[] _distance;
        private readonly int _size;
        private readonly float _extent;
        private readonly float _half;

        private BoundaryField(MapDefinition map)
        {
            _half = map.HalfSize;
            HasOutline = map.Boundary.Count >= 3;
            _extent = _half + Margin;
            _size = Mathf.CeilToInt(_extent * 2f / Cell) + 1;
            _distance = new float[_size * _size];
            if (!HasOutline) return;

            var poly = new List<Vector2>(map.Boundary.Count);
            foreach (var p in map.Boundary) poly.Add(new Vector2(p.X, p.Y));
            Outline = poly;
            for (var gz = 0; gz < _size; gz++)
            for (var gx = 0; gx < _size; gx++)
            {
                var p = new Vector2(gx * Cell - _extent, gz * Cell - _extent);
                var nearest = float.MaxValue;
                for (int i = 0, j = poly.Count - 1; i < poly.Count; j = i++)
                    nearest = Mathf.Min(nearest, SegmentDistanceSq(p, poly[j], poly[i]));
                var d = Mathf.Sqrt(nearest);
                _distance[gz * _size + gx] = map.InsideBoundary(new System.Numerics.Vector2(p.x, p.y)) ? -d : d;
            }
        }

        public static BoundaryField For(MapDefinition map)
        {
            if (_cached == null || !ReferenceEquals(_cachedMap, map))
            {
                _cached = new BoundaryField(map);
                _cachedMap = map;
            }
            return _cached;
        }

        public bool HasOutline { get; }

        /// <summary>The outline's points (x, z), or null for a square map.</summary>
        public IReadOnlyList<Vector2> Outline { get; }

        /// <summary>Metres outside the outline (negative inside it).</summary>
        public float Distance(Vector2 p)
        {
            var square = Mathf.Max(Mathf.Abs(p.x), Mathf.Abs(p.y)) - _half;
            if (!HasOutline) return square;
            var fx = (p.x + _extent) / Cell;
            var fz = (p.y + _extent) / Cell;
            if (fx < 0f || fz < 0f || fx >= _size - 1 || fz >= _size - 1) return square;
            var x0 = (int)fx;
            var z0 = (int)fz;
            var tx = fx - x0;
            var tz = fz - z0;
            var a = Mathf.Lerp(_distance[z0 * _size + x0], _distance[z0 * _size + x0 + 1], tx);
            var b = Mathf.Lerp(_distance[(z0 + 1) * _size + x0], _distance[(z0 + 1) * _size + x0 + 1], tx);
            return Mathf.Lerp(a, b, tz);
        }

        public bool Inside(Vector2 p) => Distance(p) <= 0f;

        private static float SegmentDistanceSq(Vector2 p, Vector2 a, Vector2 b)
        {
            var ab = b - a;
            var t = Mathf.Clamp01(Vector2.Dot(p - a, ab) / Mathf.Max(1e-6f, ab.sqrMagnitude));
            return (a + ab * t - p).sqrMagnitude;
        }
    }
}
