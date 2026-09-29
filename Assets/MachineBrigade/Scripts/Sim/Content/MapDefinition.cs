#nullable enable
using System;
using System.Collections.Generic;
using System.Numerics;
using MachineBrigade.Sim.Core;

namespace MachineBrigade.Sim.Content
{
    /// <summary>Where a team gathers: its drop zone and retreat destination.</summary>
    public readonly struct TeamStart
    {
        public TeamStart(int team, Vector2 rally)
        {
            Team = team;
            Rally = rally;
        }

        public int Team { get; }
        public Vector2 Rally { get; }
    }

    public readonly struct PropPlacement
    {
        public PropPlacement(string defId, Vector2 position, int rotation)
        {
            DefId = defId;
            Position = position;
            Rotation = rotation;
        }

        public string DefId { get; }
        public Vector2 Position { get; }

        /// <summary>Degrees; one of 0, 90, 180, 270 so footprints stay grid-aligned.</summary>
        public int Rotation { get; }
    }

    public readonly struct UnitPlacement
    {
        public UnitPlacement(string defId, int team, Vector2 position, float heading)
        {
            DefId = defId;
            Team = team;
            Position = position;
            Heading = heading;
        }

        public string DefId { get; }
        public int Team { get; }
        public Vector2 Position { get; }

        /// <summary>Radians.</summary>
        public float Heading { get; }
    }

    /// <summary>
    /// A battlefield as data. The map is a square of <see cref="Size"/> metres centred on the
    /// origin, so coordinates run from -HalfSize to +HalfSize on both axes.
    /// </summary>
    /// <summary>A road drawn on the ground (presentation only; the simulation ignores it).</summary>
    public sealed class RoadDef
    {
        public RoadDef(float width, IReadOnlyList<Vector2> points)
        {
            Width = width;
            Points = points;
        }

        public float Width { get; }
        public IReadOnlyList<Vector2> Points { get; }
    }

    public sealed class MapDefinition
    {
        public MapDefinition(string id, float size, IReadOnlyList<TeamStart> teams,
            IReadOnlyList<PropPlacement> props, IReadOnlyList<UnitPlacement> units,
            IReadOnlyList<CapturePointDef>? points = null, IReadOnlyList<RoadDef>? roads = null, string theme = "temperate",
            IReadOnlyList<Vector2>? boundary = null, IReadOnlyList<float>? siegeRings = null, IReadOnlyList<PropPlacement>? decor = null,
            IReadOnlyList<BaseSiteDef>? bases = null, FortressDef? fortress = null)
        {
            Fortress = fortress;
            Bases = bases ?? Array.Empty<BaseSiteDef>();
            Decor = decor ?? Array.Empty<PropPlacement>();
            SiegeRings = siegeRings ?? Array.Empty<float>();
            Boundary = boundary ?? Array.Empty<Vector2>();
            Theme = string.IsNullOrWhiteSpace(theme) ? "temperate" : theme;
            Points = points ?? Array.Empty<CapturePointDef>();
            Roads = roads ?? Array.Empty<RoadDef>();
            Id = string.IsNullOrWhiteSpace(id) ? throw new ArgumentException("Map id must not be empty.") : id;
            Size = float.IsFinite(size) && size > 0 ? size : throw new ArgumentException($"Map '{id}': size must be positive.");
            Teams = teams;
            Props = props;
            Units = units;
        }

        public string Id { get; }
        public float Size { get; }
        public float HalfSize => Size * 0.5f;
        public IReadOnlyList<TeamStart> Teams { get; }
        public IReadOnlyList<PropPlacement> Props { get; }
        public IReadOnlyList<UnitPlacement> Units { get; }

        /// <summary>
        /// Scenery beyond the boundary: buildings, woods and rocks drawn like the map's own but never
        /// simulated (nothing reaches them), so the country goes on past the edge.
        /// </summary>
        public IReadOnlyList<PropPlacement> Decor { get; }

        /// <summary>Each side's camp: its headquarters and hardpoints (empty on maps without bases).</summary>
        public IReadOnlyList<BaseSiteDef> Bases { get; }

        /// <summary>A siege map's fortress: its ground, tower hardpoints by ring, super-gun and line in (null elsewhere).</summary>
        public FortressDef? Fortress { get; }

        /// <summary>A side's camp in the map data, or null.</summary>
        public BaseSiteDef? BaseOf(int team)
        {
            foreach (var b in Bases)
                if (b.Team == team) return b;
            return null;
        }

        /// <summary>Objectives for Conquest (may be empty for other modes).</summary>
        public IReadOnlyList<CapturePointDef> Points { get; }

        /// <summary>Look of the battlefield (temperate, desert, snow, harbor); presentation only.</summary>
        public string Theme { get; }

        /// <summary>Roads for the ground painter; empty means the painter lays its own.</summary>
        public IReadOnlyList<RoadDef> Roads { get; }

        public bool Contains(Vector2 point) =>
            MathF.Abs(point.X) <= HalfSize && MathF.Abs(point.Y) <= HalfSize;

        /// <summary>
        /// The battlefield's outline inside the square (counter-clockwise), or empty for a plain
        /// square. Outside it is terrain: ground vehicles cannot drive there and it stops direct
        /// fire; aircraft fly over it.
        /// </summary>
        public IReadOnlyList<Vector2> Boundary { get; }

        /// <summary>
        /// Siege maps: the fortress rings, as distances (the larger of the x and z offsets) from the
        /// command HQ: beyond the first is the outer line (stage 1), between them the wall ring
        /// (stage 2), inside the second the keep (stage 3). Empty elsewhere.
        /// </summary>
        public IReadOnlyList<float> SiegeRings { get; }

        /// <summary>Whether a point lies inside the outline (always, for a map without one).</summary>
        public bool InsideBoundary(Vector2 p)
        {
            var poly = Boundary;
            if (poly.Count < 3) return Contains(p);
            var inside = false;
            for (int i = 0, j = poly.Count - 1; i < poly.Count; j = i++)
            {
                var a = poly[i];
                var b = poly[j];
                if ((a.Y > p.Y) != (b.Y > p.Y) && p.X < (b.X - a.X) * (p.Y - a.Y) / (b.Y - a.Y) + a.X) inside = !inside;
            }
            return inside;
        }

        /// <summary>
        /// The same battlefield with the two sides' camps swapped: side 0 starts where side 1 did,
        /// with its camp, hardpoints and the units placed there (a fortress's towers too). A campaign
        /// mission that comes back to a map from the other side plays on this.
        /// </summary>
        public MapDefinition Reversed()
        {
            static int Swap(int team) => team == 0 ? 1 : team == 1 ? 0 : team;
            var teams = new List<TeamStart>();
            foreach (var t in Teams) teams.Add(new TeamStart(Swap(t.Team), t.Rally));
            var units = new List<UnitPlacement>();
            foreach (var u in Units) units.Add(new UnitPlacement(u.DefId, Swap(u.Team), u.Position, u.Heading));
            var bases = new List<BaseSiteDef>();
            foreach (var b in Bases) bases.Add(new BaseSiteDef(Swap(b.Team), b.Hq, b.Heading, b.Slots));
            return new MapDefinition(Id, Size, teams, Props, units, Points, Roads, Theme, Boundary, SiegeRings, Decor, bases);
        }

        /// <summary>Prompt 16: the sea beside the battlefield (its lanes, beaches, piers, batteries), or null.</summary>
        public SeaDef? Sea { get; internal set; }

        public static MapDefinition FromJson(string json)
        {
            var root = new JsonObject(MiniJson.Parse(json), "map");
            var id = root.String("id");
            var size = root.Float("size");

            var teams = new List<TeamStart>();
            foreach (var t in root.Array("teams"))
                teams.Add(new TeamStart(t.Int("team", 0), new Vector2(t.Float("x"), t.Float("z"))));

            var props = new List<PropPlacement>();
            foreach (var p in root.Array("props"))
            {
                var rotation = p.Int("rot", 0);
                if (rotation % 45 != 0) throw new FormatException($"{p.Path}.rot: must be a multiple of 45.");
                props.Add(new PropPlacement(p.String("def"), new Vector2(p.Float("x"), p.Float("z")), ((rotation % 360) + 360) % 360));
            }

            var units = new List<UnitPlacement>();
            foreach (var u in root.Array("units"))
            {
                units.Add(new UnitPlacement(u.String("def"), u.Int("team", 0), new Vector2(u.Float("x"), u.Float("z")),
                    SimMath.DegToRad(u.Float("heading", 0f))));
            }

            var points = new List<CapturePointDef>();
            if (root.Has("points"))
            {
                foreach (var c in root.Array("points"))
                {
                    var outpost = new List<HardpointDef>();
                    if (c.Has("outpost"))
                        foreach (var s in c.Array("outpost"))
                            outpost.Add(BaseSiteDef.ParseSlot(s));
                    points.Add(new CapturePointDef(c.String("id"), c.Has("name") ? c.String("name") : c.String("id"),
                        new Vector2(c.Float("x"), c.Float("z")), c.Float("radius", 10f), outpost));
                }
            }

            var roads = new List<RoadDef>();
            if (root.Has("roads"))
            {
                foreach (var r in root.Array("roads"))
                {
                    var flat = r.FloatArray("points");
                    if (flat.Count < 4 || flat.Count % 2 != 0) throw new FormatException($"{r.Path}.points: needs x, z pairs.");
                    var line = new List<Vector2>();
                    for (var i = 0; i < flat.Count; i += 2) line.Add(new Vector2(flat[i], flat[i + 1]));
                    roads.Add(new RoadDef(r.Float("width", 5f), line));
                }
            }

            var boundary = new List<Vector2>();
            if (root.Has("boundary"))
            {
                var flat = root.FloatArray("boundary");
                if (flat.Count < 6 || flat.Count % 2 != 0) throw new FormatException("map.boundary: needs at least three x, z pairs.");
                for (var i = 0; i < flat.Count; i += 2) boundary.Add(new Vector2(flat[i], flat[i + 1]));
            }

            var rings = root.Has("siegeRings") ? new List<float>(root.FloatArray("siegeRings")) : null;
            var decor = new List<PropPlacement>();
            if (root.Has("decor"))
                foreach (var p in root.Array("decor"))
                {
                    var rotation = ((p.Int("rot", 0) % 360) + 360) % 360;
                    decor.Add(new PropPlacement(p.String("def"), new Vector2(p.Float("x"), p.Float("z")), rotation - rotation % 45));
                }
            var bases = new List<BaseSiteDef>();
            if (root.Has("bases"))
                foreach (var b in root.Array("bases"))
                    bases.Add(BaseSiteDef.Parse(b));
            var fortress = root.Has("fortress") ? FortressDef.Parse(root.Object("fortress")) : null;
            return new MapDefinition(id, size, teams, props, units, points, roads, root.Has("theme") ? root.String("theme") : "temperate",
                boundary, rings, decor, bases, fortress)
            {
                // Prompt 16: a battlefield on the sea (Lighthouse Bay): its lanes, beaches and batteries.
                Sea = root.Has("sea") ? SeaDef.Parse(root.Object("sea")) : null,
            };
        }
    }
}
