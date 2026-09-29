using System.Collections.Generic;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Signed distance to the battlefield's outline (positive outside, negative inside), sampled on
    /// a 1 m grid round the map so the terrain, the scenery, the ground paint and the minimap can
    /// ask it millions of times at load. Beyond the grid (and on a map without an outline) it is
    /// the distance to the map's edge (a square, or a long battlefield's rectangle). Built once per
    /// map and shared.
    /// </summary>
    public sealed class BoundaryField
    {
        private const float Cell = 1f;
        private const float Margin = 24f;

        private static BoundaryField _cached;
        private static MapDefinition _cachedMap;

        private readonly float[] _distance;
        private readonly int _sizeX, _sizeZ;
        private readonly Vector2 _origin, _centre;
        private readonly float _halfX, _halfZ;

        private BoundaryField(MapDefinition map)
        {
            _halfX = map.Width * 0.5f;
            _halfZ = map.Length * 0.5f;
            _centre = new Vector2(map.Centre.X, map.Centre.Y);
            HasOutline = map.Boundary.Count >= 3;
            _origin = new Vector2(map.Min.X - Margin, map.Min.Y - Margin);
            _sizeX = Mathf.CeilToInt((map.Width + Margin * 2f) / Cell) + 1;
            _sizeZ = Mathf.CeilToInt((map.Length + Margin * 2f) / Cell) + 1;
            _distance = new float[_sizeX * _sizeZ];
            if (!HasOutline) return;

            var poly = new List<Vector2>(map.Boundary.Count);
            foreach (var p in map.Boundary) poly.Add(new Vector2(p.X, p.Y));
            Outline = poly;
            for (var gz = 0; gz < _sizeZ; gz++)
            for (var gx = 0; gx < _sizeX; gx++)
            {
                var p = new Vector2(gx * Cell + _origin.x, gz * Cell + _origin.y);
                var nearest = float.MaxValue;
                for (int i = 0, j = poly.Count - 1; i < poly.Count; j = i++)
                    nearest = Mathf.Min(nearest, SegmentDistanceSq(p, poly[j], poly[i]));
                var d = Mathf.Sqrt(nearest);
                _distance[gz * _sizeX + gx] = map.InsideBoundary(new System.Numerics.Vector2(p.x, p.y)) ? -d : d;
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
            var square = Mathf.Max(Mathf.Abs(p.x - _centre.x) - _halfX, Mathf.Abs(p.y - _centre.y) - _halfZ);
            if (!HasOutline) return square;
            var fx = (p.x - _origin.x) / Cell;
            var fz = (p.y - _origin.y) / Cell;
            if (fx < 0f || fz < 0f || fx >= _sizeX - 1 || fz >= _sizeZ - 1) return square;
            var x0 = (int)fx;
            var z0 = (int)fz;
            var tx = fx - x0;
            var tz = fz - z0;
            var a = Mathf.Lerp(_distance[z0 * _sizeX + x0], _distance[z0 * _sizeX + x0 + 1], tx);
            var b = Mathf.Lerp(_distance[(z0 + 1) * _sizeX + x0], _distance[(z0 + 1) * _sizeX + x0 + 1], tx);
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
