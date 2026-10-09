#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Content;

namespace MachineBrigade.Sim.Navigation
{
    /// <summary>A level crossing: where a road crosses a rail inside the play area (prompt 33 L5).</summary>
    public sealed class RailCrossingDef
    {
        public RailCrossingDef(string id, float s, Vector2 position, float width, float depth, float length, bool closes = true)
        {
            Id = id;
            S = s;
            Position = position;
            Width = width;
            Depth = depth;
            Length = length;
            Closes = closes;
        }

        /// <summary>Whether its barriers close its ground (false: closing it would cut the ground, a camp's drop zone on it: it only warns).</summary>
        public bool Closes { get; }

        public string Id { get; }

        /// <summary>Where it lies along the rail (metres from the rail's first point).</summary>
        public float S { get; }

        public Vector2 Position { get; }

        /// <summary>The ground its barriers close (an axis-aligned box: x size, z size), the road's width by the rail's band.</summary>
        public float Width { get; }
        public float Depth { get; }

        /// <summary>How far a vehicle drives to get over it (metres): what its warning time is worked out from.</summary>
        public float Length { get; }

        /// <summary>Half the stretch of rail it covers, either side of <see cref="S"/>.</summary>
        public float Half => MathF.Max(Width, Depth) * global::MachineBrigade.Sim.Content.SimTunables.Vehicles.RailCrossingDef.HalfMaxScale;
    }

    /// <summary>
    /// Prompt 33 L5 (DECISIONS "Prompt 33 L5"): a railway line, separate from the ground's navigation: a polyline (its corners
    /// rounded by Tools/maps/transit.py) measured by arc length, that runs from a tunnel portal beyond the map, through the
    /// edge band and the entry gate, into the play area (to a buffer stop inside, or out through another gate). Map data
    /// "rails": [{"id", "kind", "points": [x, z, ...], "playFrom", "playTo", "crossings": [{"id", "s", "x", "z", "width",
    /// "depth", "length", "closes"}]}]. Trains run on it (the boss trains, the Siege support train); the ground beside it stays open
    /// ground (vehicles may cross it anywhere, but never park on it).
    /// </summary>
    public sealed class RailSpline
    {
        /// <summary>Half the rail's band (metres): a train is at most 3.5 m wide; nothing parks within this of the line.</summary>
        public const float BandHalf = 3.5f;

        private readonly Vector2[] _points;
        private readonly float[] _at;

        public RailSpline(string id, string kind, IReadOnlyList<Vector2> points, float playFrom = 0f, float playTo = float.PositiveInfinity,
            IReadOnlyList<RailCrossingDef>? crossings = null)
        {
            if (points.Count < 2) throw new FormatException($"rail {id}: needs two points at least.");
            Id = id;
            Kind = kind;
            _points = new Vector2[points.Count];
            _at = new float[points.Count];
            for (var i = 0; i < points.Count; i++)
            {
                _points[i] = points[i];
                _at[i] = i == 0 ? 0f : _at[i - 1] + Vector2.Distance(points[i - 1], points[i]);
            }
            Length = _at[_at.Length - 1];
            PlayFrom = Math.Clamp(playFrom, 0f, Length);
            PlayTo = Math.Clamp(playTo, PlayFrom, Length);
            Crossings = crossings ?? Array.Empty<RailCrossingDef>();
        }

        public string Id { get; }

        /// <summary>"line" (a map's own railway: the boss trains') or "siege" (the fortress's line in: the support train's).</summary>
        public string Kind { get; }

        public IReadOnlyList<Vector2> Points => _points;
        public float Length { get; }

        /// <summary>The stretch inside the play area: from the entry gate at <see cref="PlayFrom"/> to <see cref="PlayTo"/>.</summary>
        public float PlayFrom { get; }
        public float PlayTo { get; }

        /// <summary>Whether an end of the play stretch is an entry gate (the rail runs on out of the map there) rather than a buffer stop.</summary>
        public bool GateAtFrom => PlayFrom > 0.01f;
        public bool GateAtTo => PlayTo < Length - global::MachineBrigade.Sim.Content.SimTunables.Vehicles.RailSpline.GateAtToLengthSub;

        public IReadOnlyList<RailCrossingDef> Crossings { get; }

        private int SegmentAt(float s)
        {
            if (s <= 0f) return 0;
            if (s >= Length) return _points.Length - global::MachineBrigade.Sim.Content.SimTunables.Vehicles.RailSpline.SegmentAtLengthSub;
            int lo = 0, hi = _points.Length - 1;
            while (hi - lo > 1)
            {
                var mid = (lo + hi) >> 1;
                if (_at[mid] <= s) lo = mid;
                else hi = mid;
            }
            return lo;
        }

        /// <summary>The point <paramref name="s"/> metres along the line (clamped to its ends).</summary>
        public Vector2 At(float s)
        {
            var i = SegmentAt(s);
            var span = _at[i + 1] - _at[i];
            var t = span > 1e-5f ? Math.Clamp((s - _at[i]) / span, 0f, 1f) : 0f;
            return _points[i] + (_points[i + 1] - _points[i]) * t;
        }

        /// <summary>The unit direction of the line at <paramref name="s"/> (towards growing s).</summary>
        public Vector2 Tangent(float s)
        {
            var i = SegmentAt(s);
            var d = _points[i + 1] - _points[i];
            return d.LengthSquared() > 1e-8f ? Vector2.Normalize(d) : new Vector2(0f, 1f);
        }

        /// <summary>The left of the line at <paramref name="s"/> (the tangent turned a quarter anticlockwise, seen from above).</summary>
        public Vector2 Left(float s)
        {
            var t = Tangent(s);
            return new Vector2(-t.Y, t.X);
        }

        /// <summary>
        /// The nearest place on the line to <paramref name="p"/>: its arc length, and the signed distance off it (positive on
        /// the left). Deterministic: the first segment of equal distance wins.
        /// </summary>
        public float Project(Vector2 p, out float lateral)
        {
            var bestS = 0f;
            var bestD = float.MaxValue;
            lateral = 0f;
            for (var i = 0; i + 1 < _points.Length; i++)
            {
                var a = _points[i];
                var ab = _points[i + 1] - a;
                var len2 = ab.LengthSquared();
                if (len2 < 1e-8f) continue;
                var t = Math.Clamp(Vector2.Dot(p - a, ab) / len2, 0f, 1f);
                var q = a + ab * t;
                var d = Vector2.DistanceSquared(p, q);
                if (d >= bestD - 1e-6f) continue;
                bestD = d;
                bestS = _at[i] + MathF.Sqrt(len2) * t;
                var dir = ab / MathF.Sqrt(len2);
                lateral = dir.X * (p.Y - q.Y) - dir.Y * (p.X - q.X);
            }
            return bestS;
        }

        internal static IReadOnlyList<RailSpline> ParseAll(JsonObject root)
        {
            if (!root.Has("rails")) return Array.Empty<RailSpline>();
            var list = new List<RailSpline>();
            foreach (var r in root.Array("rails"))
            {
                var flat = r.FloatArray("points");
                if (flat.Count < 4 || flat.Count % 2 != 0) throw new FormatException($"{r.Path}.points: needs at least two x, z pairs.");
                var points = new List<Vector2>();
                for (var i = 0; i < flat.Count; i += 2) points.Add(new Vector2(flat[i], flat[i + 1]));
                var crossings = new List<RailCrossingDef>();
                if (r.Has("crossings"))
                    foreach (var c in r.Array("crossings"))
                        crossings.Add(new RailCrossingDef(c.String("id"), c.Float("s"), new Vector2(c.Float("x"), c.Float("z")), c.Float("width", 8f),
                            c.Float("depth", 8f), c.Float("length", 11f), c.Bool("closes", true)));
                list.Add(new RailSpline(r.String("id"), r.Has("kind") ? r.String("kind") : "line", points, r.Float("playFrom", 0f),
                    r.Float("playTo", float.PositiveInfinity), crossings));
            }
            return list;
        }
    }
}
