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
        public UnitPlacement(string defId, int team, Vector2 position, float heading, bool start = false)
        {
            DefId = defId;
            Team = team;
            Position = position;
            Heading = heading;
            Start = start;
        }

        /// <summary>
        /// Prompt 32 L6: one of a generated map's generic start units (the map file's "start": true): replaced by the
        /// opening squad in the modes that have one (<see cref="SimWorld.MapUnits"/>); a mission keeps them.
        /// </summary>
        public bool Start { get; }

        public string DefId { get; }
        public int Team { get; }
        public Vector2 Position { get; }

        /// <summary>Radians.</summary>
        public float Heading { get; }
    }

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

    /// <summary>
    /// A battlefield as data. A map is a square of <see cref="Size"/> metres centred on the origin
    /// (coordinates from -HalfSize to +HalfSize on both axes), or (prompt 17's long battlefields) a
    /// rectangle given by its <see cref="Min"/> and <see cref="Max"/> corners: 300 m across and 480 m
    /// along the attack, the square's own ground where it always was and the rest to the north.
    /// Everything that keeps to the map uses the corners (<see cref="Contains"/>, <see cref="Clamp"/>).
    /// </summary>
    /// <summary>Prompt 23 B: a spawn point a map sets by hand: whose (0 the player's side's allies, 1 the enemy), how they come, where.</summary>
    public sealed class SpawnPointDef
    {
        public SpawnPointDef(int side, Navigation.SpawnKind kind, Vector2 position, Vector2? from)
        {
            Side = side;
            Kind = kind;
            Position = position;
            From = from;
        }

        public int Side { get; }
        public Navigation.SpawnKind Kind { get; }
        public Vector2 Position { get; }

        /// <summary>An air path's entry over the edge, or null.</summary>
        public Vector2? From { get; }

        internal static IReadOnlyList<SpawnPointDef> ParseAll(JsonObject root)
        {
            var list = new List<SpawnPointDef>();
            foreach (var s in root.Array("spawns"))
                list.Add(new SpawnPointDef(s.Int("team", 1), s.Enum<Navigation.SpawnKind>("kind", Navigation.SpawnKind.Edge),
                    new Vector2(s.Float("x"), s.Float("z")), s.Has("fromX") ? new Vector2(s.Float("fromX"), s.Float("fromZ")) : null));
            return list;
        }
    }

    public sealed partial class MapDefinition
    {
        public MapDefinition(string id, float size, IReadOnlyList<TeamStart> teams,
            IReadOnlyList<PropPlacement> props, IReadOnlyList<UnitPlacement> units,
            IReadOnlyList<CapturePointDef>? points = null, IReadOnlyList<RoadDef>? roads = null, string theme = "temperate",
            IReadOnlyList<Vector2>? boundary = null, IReadOnlyList<float>? siegeRings = null, IReadOnlyList<PropPlacement>? decor = null,
            IReadOnlyList<BaseSiteDef>? bases = null, FortressDef? fortress = null, (Vector2 min, Vector2 max)? bounds = null)
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
            if (bounds is { } b)
            {
                if (!(b.max.X > b.min.X) || !(b.max.Y > b.min.Y)) throw new ArgumentException($"Map '{id}': bounds must have a positive area.");
                Min = b.min;
                Max = b.max;
                Size = MathF.Max(b.max.X - b.min.X, b.max.Y - b.min.Y);
            }
            else
            {
                Min = new Vector2(-Size * 0.5f);
                Max = new Vector2(Size * 0.5f);
            }
            Teams = teams;
            Props = props;
            Units = units;
        }

        public string Id { get; }

        /// <summary>The longer side in metres (the square's side on a square map).</summary>
        public float Size { get; }

        /// <summary>Half the longer side. A square map runs from -HalfSize to +HalfSize; keep to the map with <see cref="Min"/> and <see cref="Max"/>.</summary>
        public float HalfSize => Size * 0.5f;

        /// <summary>The south-west corner (lowest x and z).</summary>
        public Vector2 Min { get; }

        /// <summary>The north-east corner (highest x and z).</summary>
        public Vector2 Max { get; }

        /// <summary>Metres across (along x).</summary>
        public float Width => Max.X - Min.X;

        /// <summary>Metres along (z).</summary>
        public float Length => Max.Y - Min.Y;

        /// <summary>The map's middle (the origin on a square map).</summary>
        public Vector2 Centre => (Min + Max) * 0.5f;

        /// <summary>A long battlefield (prompt 17): noticeably longer than wide.</summary>
        public bool IsLong => Length > Width * 1.2f;

        /// <summary>The point kept at least <paramref name="margin"/> inside the map's edges.</summary>
        public Vector2 Clamp(Vector2 p, float margin = 0f) =>
            new(Math.Clamp(p.X, MathF.Min(Min.X + margin, Centre.X), MathF.Max(Max.X - margin, Centre.X)),
                Math.Clamp(p.Y, MathF.Min(Min.Y + margin, Centre.Y), MathF.Max(Max.Y - margin, Centre.Y)));

        /// <summary>How far inside the nearest edge a point is (negative outside).</summary>
        public float EdgeDistance(Vector2 p) => MathF.Min(MathF.Min(p.X - Min.X, Max.X - p.X), MathF.Min(p.Y - Min.Y, Max.Y - p.Y));
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
            point.X >= Min.X && point.X <= Max.X && point.Y >= Min.Y && point.Y <= Max.Y;

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
            foreach (var u in Units) units.Add(new UnitPlacement(u.DefId, Swap(u.Team), u.Position, u.Heading, u.Start));
            var bases = new List<BaseSiteDef>();
            foreach (var b in Bases) bases.Add(new BaseSiteDef(Swap(b.Team), b.Hq, b.Heading, b.Slots));
            // A fixed route runs toward the other camp now: the same road, walked the other way.
            var routes = new Dictionary<string, IReadOnlyList<Vector2>>();
            foreach (var (key, line) in Routes)
            {
                var back = new List<Vector2>(line);
                back.Reverse();
                routes[key] = back;
            }
            var spawns = new List<SpawnPointDef>();
            foreach (var sp in Spawns) spawns.Add(new SpawnPointDef(Swap(sp.Side), sp.Kind, sp.Position, sp.From));
            return new MapDefinition(Id, Size, teams, Props, units, Points, Roads, Theme, Boundary, SiegeRings, Decor, bases,
                bounds: IsSquare ? null : (Min, Max)) { Routes = routes, Spawns = spawns, Rails = Rails };
        }

        /// <summary>
        /// Prompt 20 M: fixed routes by name (map data "routes": {"kronos": [x, z, ...]}), for a slow boss that
        /// drives the same road every time toward the player's camp (the open-pit mine's excavator). Empty on most maps.
        /// </summary>
        public IReadOnlyDictionary<string, IReadOnlyList<Vector2>> Routes { get; internal set; } = new Dictionary<string, IReadOnlyList<Vector2>>();

        /// <summary>A named fixed route, or null when the map has none by that name.</summary>
        public IReadOnlyList<Vector2>? Route(string name) => Routes.TryGetValue(name, out var line) ? line : null;

        /// <summary>Prompt 16: the sea beside the battlefield (its lanes, beaches, piers, batteries), or null.</summary>
        public SeaDef? Sea { get; internal set; }

        /// <summary>Prompt 30 L6: the neutral sites (radar, workshop, abandoned AA, ammo depot), placed by Tools/maps/place_neutrals.py.</summary>
        public IReadOnlyList<NeutralSiteDef> Neutrals { get; internal set; } = Array.Empty<NeutralSiteDef>();

        /// <summary>
        /// Prompt 23 B: spawn points the map sets by hand (map data "spawns": [{"team", "kind", "x", "z", "fromX", "fromZ"}]),
        /// on top of the ones worked out from the map (<see cref="Navigation.SpawnPoints"/>). Empty on most maps.
        /// </summary>
        public IReadOnlyList<SpawnPointDef> Spawns { get; internal set; } = Array.Empty<SpawnPointDef>();
        /// <summary>Whether the map is the plain square centred on the origin.</summary>
        private bool IsSquare => Min == new Vector2(-Size * 0.5f) && Max == new Vector2(Size * 0.5f);

        public static MapDefinition FromJson(string json)
        {
            var root = new JsonObject(MiniJson.Parse(json), "map");
            var id = root.String("id");
            var size = root.Float("size");
            (Vector2, Vector2)? bounds = null;
            if (root.Has("bounds"))
            {
                var b = root.FloatArray("bounds");
                if (b.Count != 4) throw new FormatException("map.bounds: needs min x, min z, max x, max z.");
                bounds = (new Vector2(b[0], b[1]), new Vector2(b[2], b[3]));
            }

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
                    SimMath.DegToRad(u.Float("heading", 0f)), u.Bool("start", false)));
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
            var routes = new Dictionary<string, IReadOnlyList<Vector2>>();
            if (root.Has("routes"))
            {
                var r = root.Object("routes");
                foreach (var key in r.Keys)
                {
                    var flat = r.FloatArray(key);
                    if (flat.Count < 4 || flat.Count % 2 != 0) throw new FormatException($"map.routes.{key}: needs at least two x, z pairs.");
                    var line = new List<Vector2>();
                    for (var i = 0; i < flat.Count; i += 2) line.Add(new Vector2(flat[i], flat[i + 1]));
                    routes[key] = line;
                }
            }
            return new MapDefinition(id, size, teams, props, units, points, roads, root.Has("theme") ? root.String("theme") : "temperate",
                boundary, rings, decor, bases, fortress, bounds)
            {
                // Prompt 16: a battlefield on the sea (Lighthouse Bay): its lanes, beaches and batteries.
                Sea = root.Has("sea") ? SeaDef.Parse(root.Object("sea")) : null,
                Routes = routes,
                Spawns = SpawnPointDef.ParseAll(root),
                Neutrals = NeutralSiteDef.ParseAll(root),
                // Prompt 33 L4-L5: the big ships' sea routes and the railway lines.
                SeaRoutes = root.Has("seaRoutes") ? Navigation.SeaRouteGraph.Parse(root.Object("seaRoutes")) : null,
                Rails = RailsOf(root),
            };
        }
    }
}
