#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;

namespace MachineBrigade.Sim.Content
{
    /// <summary>A sea lane ships run on (prompt 16): a line along the coast <see cref="W"/> metres out to sea.</summary>
    public sealed class SeaLaneDef
    {
        public string Id { get; internal set; } = "";

        /// <summary>How far out to sea it runs, in the coast's frame.</summary>
        public float W { get; internal set; }

        /// <summary>Half the stretch of it a ship patrols (u from -Patrol to +Patrol).</summary>
        public float Patrol { get; internal set; }

        /// <summary>Where the lane leaves the battlefield (|u|): a ship that gets there has sailed off.</summary>
        public float End { get; internal set; }
    }

    /// <summary>A beach a landing craft runs up on: where it grounds, and where its vehicles drive off to.</summary>
    public sealed class SeaLandingDef
    {
        public Vector2 At { get; internal set; }
        public Vector2 Inland { get; internal set; }
    }

    /// <summary>An abandoned coastal battery on the shore: neutral until a side takes it (prompt 16 A.3).</summary>
    public sealed class SeaBatteryDef
    {
        public string Id { get; internal set; } = "";
        public Vector2 At { get; internal set; }

        /// <summary>Degrees, the game's convention (0 north, clockwise): which way its guns face at first.</summary>
        public float Heading { get; internal set; }
    }

    /// <summary>
    /// A battlefield's sea (map data "sea", prompt 16): the coast's own frame (u along the coast, w out to
    /// sea, both in metres from the map's centre), the waterline, the lanes the ships run on, the beaches
    /// landing craft use, the pier heads, the coastal batteries, the lighthouse's objective and lamp, and
    /// where aircraft fly in from over the sea. Ships never leave the sea: the naval system moves them in
    /// this frame, off the ground's navigation grid.
    /// </summary>
    public sealed class SeaDef
    {
        private float[] _shoreU = Array.Empty<float>();
        private float[] _shoreW = Array.Empty<float>();

        /// <summary>The unit vector along the coast (+u).</summary>
        public Vector2 Along { get; private set; } = new(MathF.Sqrt(0.5f), MathF.Sqrt(0.5f));

        /// <summary>The unit vector out to sea (+w): <see cref="Along"/> turned a quarter to the right.</summary>
        public Vector2 Out => new(Along.Y, -Along.X);

        public IReadOnlyList<SeaLaneDef> Lanes { get; private set; } = Array.Empty<SeaLaneDef>();
        public IReadOnlyList<SeaLandingDef> Landings { get; private set; } = Array.Empty<SeaLandingDef>();

        /// <summary>The places on land nearest the lanes (the pier heads, the headland's tip).</summary>
        public IReadOnlyList<Vector2> Piers { get; private set; } = Array.Empty<Vector2>();

        public IReadOnlyList<SeaBatteryDef> Batteries { get; private set; } = Array.Empty<SeaBatteryDef>();

        /// <summary>The capture point whose holder watches the sea (the lighthouse), or null.</summary>
        public string? Lighthouse { get; private set; }

        /// <summary>The lighthouse's lamp: where its holder's watch is kept from.</summary>
        public Vector2 Lamp { get; private set; }

        /// <summary>Where aircraft from the fleet fly in from, out over the sea.</summary>
        public Vector2 AirEntry { get; private set; }

        /// <summary>A point's place in the coast's frame: (u along, w out).</summary>
        public Vector2 Frame(Vector2 p) => new(Vector2.Dot(p, Along), Vector2.Dot(p, Out));

        /// <summary>The point at (u, w) in the coast's frame.</summary>
        public Vector2 At(float u, float w) => Along * u + Out * w;

        /// <summary>The waterline's w at <paramref name="u"/> (linear between the data's samples).</summary>
        public float ShoreAt(float u)
        {
            if (_shoreU.Length == 0) return 0f;
            if (u <= _shoreU[0]) return _shoreW[0];
            var last = _shoreU.Length - 1;
            if (u >= _shoreU[last]) return _shoreW[last];
            var step = (_shoreU[last] - _shoreU[0]) / last;
            var i = Math.Clamp((int)((u - _shoreU[0]) / step), 0, last - 1);
            var t = (u - _shoreU[i]) / MathF.Max(1e-3f, _shoreU[i + 1] - _shoreU[i]);
            return _shoreW[i] + (_shoreW[i + 1] - _shoreW[i]) * t;
        }

        /// <summary>Whether a point is out on the water (beyond the waterline).</summary>
        public bool IsSea(Vector2 p, float margin = 0f)
        {
            var f = Frame(p);
            return f.Y > ShoreAt(f.X) + margin;
        }

        public SeaLaneDef? Lane(string? id)
        {
            foreach (var l in Lanes)
                if (l.Id == id) return l;
            return Lanes.Count > 0 ? Lanes[Lanes.Count - 1] : null;
        }

        /// <summary>The nearest place on land to shoot at a ship from: the pier head (or headland's tip) nearest it.</summary>
        public Vector2 Approach(Vector2 ship)
        {
            var best = ship;
            var bestDistance = float.MaxValue;
            foreach (var p in Piers)
            {
                var d = Vector2.DistanceSquared(p, ship);
                if (d >= bestDistance) continue;
                bestDistance = d;
                best = p;
            }
            return best;
        }

        internal static SeaDef Parse(JsonObject o)
        {
            var sea = new SeaDef();
            if (o.Has("along"))
            {
                var a = o.FloatArray("along");
                var v = new Vector2(a[0], a[1]);
                sea.Along = v.LengthSquared() > 1e-6f ? Vector2.Normalize(v) : sea.Along;
            }
            if (o.Has("shore"))
            {
                // u, w pairs, evenly spaced in u.
                var flat = o.FloatArray("shore");
                sea._shoreU = new float[flat.Count / 2];
                sea._shoreW = new float[flat.Count / 2];
                for (var i = 0; i + 1 < flat.Count; i += 2)
                {
                    sea._shoreU[i / 2] = flat[i];
                    sea._shoreW[i / 2] = flat[i + 1];
                }
            }
            var lanes = new List<SeaLaneDef>();
            if (o.Has("lanes"))
                foreach (var l in o.Array("lanes"))
                    lanes.Add(new SeaLaneDef { Id = l.String("id"), W = l.Float("w"), Patrol = l.Float("patrol", 80f), End = l.Float("end", 100f) });
            // Nearest the shore first.
            lanes.Sort((a, b) => a.W.CompareTo(b.W));
            sea.Lanes = lanes;
            var landings = new List<SeaLandingDef>();
            if (o.Has("landings"))
                foreach (var l in o.Array("landings"))
                {
                    var inland = l.FloatArray("inland");
                    landings.Add(new SeaLandingDef { At = new Vector2(l.Float("x"), l.Float("z")), Inland = new Vector2(inland[0], inland[1]) });
                }
            sea.Landings = landings;
            var piers = new List<Vector2>();
            if (o.Has("piers"))
            {
                var flat = o.FloatArray("piers");
                for (var i = 0; i + 1 < flat.Count; i += 2) piers.Add(new Vector2(flat[i], flat[i + 1]));
            }
            sea.Piers = piers;
            var batteries = new List<SeaBatteryDef>();
            if (o.Has("batteries"))
                foreach (var b in o.Array("batteries"))
                    batteries.Add(new SeaBatteryDef { Id = b.String("id"), At = new Vector2(b.Float("x"), b.Float("z")), Heading = b.Float("heading", 0f) });
            sea.Batteries = batteries;
            if (o.Has("lighthouse")) sea.Lighthouse = o.String("lighthouse");
            if (o.Has("lamp"))
            {
                var l = o.FloatArray("lamp");
                sea.Lamp = new Vector2(l[0], l[1]);
            }
            if (o.Has("airEntry"))
            {
                var e = o.FloatArray("airEntry");
                sea.AirEntry = new Vector2(e[0], e[1]);
            }
            return sea;
        }
    }
}
