#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Content
{
    /// <summary>A fortress hardpoint: a base hardpoint and the ring (line) it belongs to (1 outer line, 2 walls, 3 keep).</summary>
    public readonly struct FortressSlotDef
    {
        public FortressSlotDef(HardpointDef hardpoint, int ring)
        {
            Hardpoint = hardpoint;
            Ring = ring;
        }

        public HardpointDef Hardpoint { get; }
        public int Ring { get; }
    }

    /// <summary>How the fortress's reinforcements come in: by train on a rail line or by aircraft onto a runway.</summary>
    public enum ArrivalKind
    {
        None,
        Rail,
        Runway,
    }

    /// <summary>
    /// The fortress's line in from beyond the map (a rail line or a runway): the way the train or
    /// the aircraft comes (from outside the outline to the stop), where it stops and the vehicles
    /// roll out, and which way they face.
    /// </summary>
    public sealed class ArrivalDef
    {
        public ArrivalDef(ArrivalKind kind, IReadOnlyList<Vector2> path, Vector2 stop, float heading)
        {
            Kind = kind;
            Path = path;
            Stop = stop;
            Heading = heading;
        }

        public ArrivalKind Kind { get; }

        /// <summary>The track (or the approach and runway), from where it starts beyond the edge to its far end.</summary>
        public IReadOnlyList<Vector2> Path { get; }

        /// <summary>Where the vehicles get off (the platform or the apron).</summary>
        public Vector2 Stop { get; }

        /// <summary>Radians: the way the vehicles face as they roll out.</summary>
        public float Heading { get; }
    }

    /// <summary>
    /// A siege map's fortress (map data "fortress"): the ground it holds (the area behind its outer
    /// line), its tower hardpoints by ring, its super-gun and its line in for reinforcements. The
    /// walls, gates, relays, shield generators and the command HQ are props.
    /// </summary>
    public sealed class FortressDef
    {
        public FortressDef(Vector2 hq, IReadOnlyList<Vector2> area, IReadOnlyList<FortressSlotDef> slots, Vector2? superGun, float superGunHeading,
            ArrivalDef? arrival, IReadOnlyList<IReadOnlyList<Vector2>>? rings = null, IReadOnlyList<Vector2>? forwardDrops = null,
            IReadOnlyList<Vector2>? firing = null)
        {
            Hq = hq;
            Area = area;
            Slots = slots;
            SuperGun = superGun;
            SuperGunHeading = superGunHeading;
            Arrival = arrival;
            Rings = rings ?? Array.Empty<IReadOnlyList<Vector2>>();
            ForwardDrops = forwardDrops ?? Array.Empty<Vector2>();
            Firing = firing ?? Array.Empty<Vector2>();
        }

        /// <summary>
        /// A long battlefield's layered base (prompt 17 B): the ground inside its outer wall and inside its keep as
        /// polygons (ring 2, ring 3); empty for the corner fortress, whose rings are distances from the HQ.
        /// </summary>
        public IReadOnlyList<IReadOnlyList<Vector2>> Rings { get; }

        /// <summary>Whether this is a layered base (its rings are polygons, its hardpoints labelled by place).</summary>
        public bool Layered => Rings.Count >= global::MachineBrigade.Sim.Content.SimTunables.Bases.FortressDef.LayeredCountMin;

        /// <summary>Where the attack's reinforcements land once a ring has fallen (B.2): after stage 1, after stage 2.</summary>
        public IReadOnlyList<Vector2> ForwardDrops { get; }

        /// <summary>The firing positions on the attacker's side of the buffer zone (B.3): earth-banked gun pits, the high ground.</summary>
        public IReadOnlyList<Vector2> Firing { get; }

        /// <summary>The ring a point lies in on a layered base (1 the forward works and beyond, 2 inside the outer wall, 3 the keep); 0 without ring polygons.</summary>
        public int RingOf(Vector2 p)
        {
            if (!Layered) return 0;
            if (Inside(Rings[1], p)) return 3;
            return Inside(Rings[0], p) ? 2 : 1;
        }

        /// <summary>
        /// The layered base as a camp for the Base screen and the player's plan: its HQ, facing the attack (south),
        /// and its hardpoints but the forward works', in the map's order (the most important of each size first).
        /// </summary>
        public BaseSiteDef? Site(int team)
        {
            if (!Layered) return null;
            var slots = new List<HardpointDef>();
            foreach (var s in Slots)
                if (!s.Hardpoint.Forward) slots.Add(s.Hardpoint);
            return new BaseSiteDef(team, Hq, MathF.PI, slots, layered: true);
        }

        /// <summary>The fortress's centre: its command HQ.</summary>
        public Vector2 Hq { get; }

        /// <summary>The ground behind the outer line, as a polygon (clipped by the map's outline where it matters).</summary>
        public IReadOnlyList<Vector2> Area { get; }

        public IReadOnlyList<FortressSlotDef> Slots { get; }

        /// <summary>Where the super-gun stands (null: none).</summary>
        public Vector2? SuperGun { get; }

        /// <summary>Radians.</summary>
        public float SuperGunHeading { get; }

        public ArrivalDef? Arrival { get; }

        /// <summary>Whether a point lies in the fortress's ground.</summary>
        public bool Contains(Vector2 p) => Inside(Area, p);

        private static bool Inside(IReadOnlyList<Vector2> poly, Vector2 p)
        {
            if (poly.Count < 3) return false;
            var inside = false;
            for (int i = 0, j = poly.Count - 1; i < poly.Count; j = i++)
            {
                var a = poly[i];
                var b = poly[j];
                if ((a.Y > p.Y) != (b.Y > p.Y) && p.X < (b.X - a.X) * (p.Y - a.Y) / (b.Y - a.Y) + a.X) inside = !inside;
            }
            return inside;
        }

        internal static FortressDef Parse(JsonObject f)
        {
            var hq = f.FloatArray("hq");
            if (hq.Count != 2) throw new FormatException($"{f.Path}.hq: needs x, z.");
            var area = Points(f, "area");
            var slots = new List<FortressSlotDef>();
            if (f.Has("slots"))
                foreach (var s in f.Array("slots"))
                    slots.Add(new FortressSlotDef(BaseSiteDef.ParseSlot(s), s.Int("ring", 1)));
            Vector2? gun = null;
            var gunHeading = 0f;
            if (f.Has("superGun"))
            {
                var g = f.Object("superGun");
                gun = new Vector2(g.Float("x"), g.Float("z"));
                gunHeading = SimMath.DegToRad(g.Float("heading", 225f));
            }
            ArrivalDef? arrival = null;
            if (f.Has("arrival"))
            {
                var a = f.Object("arrival");
                var kind = Enum.TryParse<ArrivalKind>(a.String("kind"), true, out var k) ? k : throw new FormatException($"{a.Path}.kind: rail or runway");
                var stop = a.FloatArray("stop");
                if (stop.Count != 2) throw new FormatException($"{a.Path}.stop: needs x, z.");
                arrival = new ArrivalDef(kind, Points(a, "path"), new Vector2(stop[0], stop[1]), SimMath.DegToRad(a.Float("heading", 0f)));
            }
            var rings = new List<IReadOnlyList<Vector2>>();
            if (f.Has("rings"))
                foreach (var flat in f.FloatArrays("rings"))
                {
                    if (flat.Count < 6 || flat.Count % 2 != 0) throw new FormatException($"{f.Path}.rings: each needs x, z pairs.");
                    var poly = new List<Vector2>();
                    for (var i = 0; i < flat.Count; i += 2) poly.Add(new Vector2(flat[i], flat[i + 1]));
                    rings.Add(poly);
                }
            List<Vector2> Pairs(string key)
            {
                var list = new List<Vector2>();
                if (!f.Has(key)) return list;
                foreach (var xz in f.FloatArrays(key))
                    if (xz.Count == 2) list.Add(new Vector2(xz[0], xz[1]));
                return list;
            }
            return new FortressDef(new Vector2(hq[0], hq[1]), area, slots, gun, gunHeading, arrival, rings, Pairs("forward"), Pairs("firing"));
        }

        private static List<Vector2> Points(JsonObject o, string key)
        {
            var list = new List<Vector2>();
            if (!o.Has(key)) return list;
            var flat = o.FloatArray(key);
            if (flat.Count % 2 != 0) throw new FormatException($"{o.Path}.{key}: needs x, z pairs.");
            for (var i = 0; i < flat.Count; i += 2) list.Add(new Vector2(flat[i], flat[i + 1]));
            return list;
        }
    }
}
