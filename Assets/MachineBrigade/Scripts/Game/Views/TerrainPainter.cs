using System;
using System.Collections.Generic;
using MachineBrigade.Sim;
using UnityEngine;
using Random = System.Random;

namespace MachineBrigade.Game.Views
{
    /// <summary>Surface palette of one map theme (sRGB), after 3d_astra's visual-style.json.</summary>
    public readonly struct TerrainTheme
    {
        public TerrainTheme(string grass, string dirt, string sand, string road, string stone)
        {
            Grass = Hex(grass);
            Dirt = Hex(dirt);
            Sand = Hex(sand);
            Road = Hex(road);
            Stone = Hex(stone);
        }

        public Color Grass { get; }
        public Color Dirt { get; }
        public Color Sand { get; }
        public Color Road { get; }
        public Color Stone { get; }

        /// <summary>3d_astra's Riverlands palette.</summary>
        public static TerrainTheme Riverlands => new("#74846a", "#887e66", "#ada280", "#ab9775", "#6c7b77");

        private static Color Hex(string hex) => ColorUtility.TryParseHtmlString(hex, out var c) ? c : Color.magenta;
    }

    /// <summary>
    /// Paints the ground texture like the reference: noise-driven grass, dirt and sand regions
    /// with blurred borders, worn roads linking the camps through the town, trampled ground
    /// under buildings, then thousands of faint light and dark speckles for texture. Themes add
    /// their own ground: a city is paved (asphalt streets with lane markings and zebra
    /// crossings, lawns only under trees and hedges), an airfield (a map with runway lights)
    /// gets concrete runways and taxiways with their markings, lava pools a crust with an ember
    /// halo, rivers muddy banks, and volcanic ground dark fissures under its glowing cracks.
    /// </summary>
    public static class TerrainPainter
    {
        /// <summary>Roads at least this wide on an airfield are runways; narrower paved ones taxiways.</summary>
        private const float RunwayWidth = 18f;
        private const float TaxiwayWidth = 9f;

        public static Texture2D Paint(SimWorld world, MapTheme mapTheme, int size = 1024) => Paint(world, mapTheme, out _, size);

        /// <summary>
        /// The ground texture, and the minimap picture made from the same paint (see
        /// <see cref="MinimapFrom"/>).
        /// </summary>
        public static Texture2D Paint(SimWorld world, MapTheme mapTheme, out Texture2D minimap, int size = 1024)
        {
            var theme = mapTheme.Palette;
            var map = world.Map;
            var pixels = new Color[size * size];
            var worldPerPixel = map.Size / size;

            for (var y = 0; y < size; y++)
            for (var x = 0; x < size; x++)
            {
                var wx = (x + 0.5f) * worldPerPixel - map.HalfSize;
                var wz = (y + 0.5f) * worldPerPixel - map.HalfSize;
                pixels[y * size + x] = mapTheme.Paved ? Pavement(wx, wz, theme) : Surface(wx, wz, theme);
            }

            var roads = Roads(world);
            var airfield = IsAirfield(world);
            PaintRoads(pixels, size, map.HalfSize, worldPerPixel, roads, width => RoadColour(width, airfield, theme),
                airfield || mapTheme.Paved);
            PaintFootprints(pixels, size, map.HalfSize, worldPerPixel, world, mapTheme);
            if (mapTheme.Cracks > 0f) PaintCracks(pixels, size, map.HalfSize, worldPerPixel, Cracks(world, mapTheme));
            var field = BoundaryField.For(map);
            if (field.HasOutline) PaintWilds(pixels, size, map.HalfSize, worldPerPixel, field, theme);
            Blur(pixels, size, 2);
            if (mapTheme.Paved) PaintStreetMarkings(pixels, size, map.HalfSize, worldPerPixel, roads);
            if (airfield) PaintAirfieldMarkings(pixels, size, map.HalfSize, worldPerPixel, roads);
            Speckle(pixels, size, new Random(1482), mapTheme.SpeckleLight, mapTheme.SpeckleDark);
            minimap = MinimapFrom(pixels, size, world, mapTheme, field);

            var texture = new Texture2D(size, size, TextureFormat.RGBA32, true, false)
            {
                name = "Ground",
                wrapMode = TextureWrapMode.Clamp,
                filterMode = FilterMode.Trilinear,
                anisoLevel = 4,
            };
            texture.SetPixels(pixels);
            texture.Apply(true, true);
            return texture;
        }

        /// <summary>
        /// Beyond the battlefield's outline the ground is wild: stony earth under the rough terrain
        /// that fills the bays, with a dark rim of scree right along the edge. (Roads that ran on
        /// out there disappear under it.)
        /// </summary>
        private static void PaintWilds(Color[] pixels, int size, float half, float worldPerPixel, BoundaryField field, TerrainTheme theme)
        {
            var wild = Color.Lerp(theme.Stone, theme.Dirt, 0.45f) * 0.82f;
            var scree = Color.Lerp(theme.Stone, Color.black, 0.35f);
            for (var y = 0; y < size; y++)
            for (var x = 0; x < size; x++)
            {
                var wx = (x + 0.5f) * worldPerPixel - half;
                var wz = (y + 0.5f) * worldPerPixel - half;
                var d = field.Distance(new Vector2(wx, wz));
                if (d < -0.6f) continue;
                var i = y * size + x;
                var noise = Mathf.PerlinNoise(wx * 0.21f + 3.1f, wz * 0.21f + 8.7f);
                var ground = Color.Lerp(wild, theme.Dirt * 0.9f, noise * 0.5f);
                // A soft band of scree from just inside the edge to a metre or so out.
                var rim = 1f - Mathf.Clamp01(Mathf.Abs(d - 0.4f) / 1.1f);
                var outside = Mathf.Clamp01((d + 0.6f) / 1.2f);
                var c = Color.Lerp(pixels[i], ground, outside);
                c = Color.Lerp(c, scree, rim * 0.55f);
                c.a = 1f;
                pixels[i] = c;
            }
        }

        /// <summary>
        /// The minimap picture: the painted ground shrunk to <paramref name="size"/>/4 with the
        /// battlefield drawn on it (buildings as roofs, rock grey, trees as dark dots, water and
        /// lava in their colours); beyond the outline it is transparent, so the minimap shows the
        /// map's real shape. North is up (+z), east right (+x).
        /// </summary>
        private static Texture2D MinimapFrom(Color[] ground, int size, SimWorld world, MapTheme mapTheme, BoundaryField field)
        {
            const int factor = 4;
            var n = size / factor;
            var map = world.Map;
            var pixels = new Color[n * n];
            for (var y = 0; y < n; y++)
            for (var x = 0; x < n; x++)
            {
                var sum = Color.clear;
                for (var dy = 0; dy < factor; dy++)
                for (var dx = 0; dx < factor; dx++)
                    sum += ground[(y * factor + dy) * size + x * factor + dx];
                var c = sum / (factor * factor);
                // Brighten and saturate a little: the minimap is small and seen at a glance.
                c = Color.Lerp(c, c * 1.18f, 0.8f);
                c.a = 1f;
                pixels[y * n + x] = c;
            }

            var perPixel = map.Size / n;
            var roof = new Color(0.36f, 0.33f, 0.31f, 1f);
            var rock = new Color(0.52f, 0.5f, 0.47f, 1f);
            var tree = new Color(0.16f, 0.3f, 0.14f, 1f);
            var water = new Color(0.2f, 0.36f, 0.5f, 1f);
            var lava = new Color(1f, 0.42f, 0.08f, 1f);
            foreach (var prop in world.Props)
            {
                var id = prop.Def.Id;
                Color colour;
                if (id.Contains("lava")) colour = lava;
                else if (id == "river_water") colour = water;
                else if (id == "river_ford") colour = Color.Lerp(water, mapTheme.Palette.Sand, 0.5f);
                else if (id.Contains("tree") || id == "palm" || id == "bamboo_clump" || id == "hedge" || id == "fern_bush" || id == "bush" || id == "cactus")
                    colour = tree;
                else if (!prop.Def.BlocksMovement) continue;
                else if (prop.Def.Indestructible || id.Contains("rock") || id.Contains("cliff") || id.Contains("mesa") || id == "boulders" ||
                         id.Contains("spire"))
                    colour = rock;
                else colour = roof;
                var hw = Mathf.Max(prop.Width * 0.5f, perPixel * 0.6f);
                var hd = Mathf.Max(prop.Depth * 0.5f, perPixel * 0.6f);
                var x0 = Mathf.FloorToInt((prop.Position.X - hw + map.HalfSize) / perPixel);
                var x1 = Mathf.FloorToInt((prop.Position.X + hw + map.HalfSize) / perPixel);
                var y0 = Mathf.FloorToInt((prop.Position.Y - hd + map.HalfSize) / perPixel);
                var y1 = Mathf.FloorToInt((prop.Position.Y + hd + map.HalfSize) / perPixel);
                for (var y = Mathf.Max(0, y0); y <= Mathf.Min(n - 1, y1); y++)
                for (var x = Mathf.Max(0, x0); x <= Mathf.Min(n - 1, x1); x++)
                    pixels[y * n + x] = colour;
            }

            if (field.HasOutline)
            {
                var rimColour = new Color(0.93f, 0.9f, 0.8f, 1f);
                for (var y = 0; y < n; y++)
                for (var x = 0; x < n; x++)
                {
                    var d = field.Distance(new Vector2((x + 0.5f) * perPixel - map.HalfSize, (y + 0.5f) * perPixel - map.HalfSize));
                    var i = y * n + x;
                    if (d > perPixel * 1.2f) pixels[i] = Color.clear;
                    else if (d > -perPixel * 0.4f) pixels[i] = Color.Lerp(pixels[i], rimColour, 0.85f);
                }
            }

            var texture = new Texture2D(n, n, TextureFormat.RGBA32, false, false)
            {
                name = "Minimap",
                wrapMode = TextureWrapMode.Clamp,
                filterMode = FilterMode.Bilinear,
            };
            texture.SetPixels(pixels);
            texture.Apply(false, true);
            return texture;
        }

        /// <summary>A map with runway lights is an airfield: its wide roads are paved and marked.</summary>
        public static bool IsAirfield(SimWorld world)
        {
            foreach (var prop in world.Props)
                if (prop.Def.Id == "runway_light") return true;
            return false;
        }

        /// <summary>
        /// Glowing cracks for volcanic ground: short jagged polylines over open ground, clear of
        /// roads, camps and anything solid. Deterministic, so the painter (the dark fissure) and
        /// the map view (the glow) draw the same cracks.
        /// </summary>
        public static List<Vector2[]> Cracks(SimWorld world, MapTheme theme)
        {
            var cracks = new List<Vector2[]>();
            if (theme.Cracks <= 0f) return cracks;
            var rng = new Random(7331);
            var half = world.Map.HalfSize - 3f;
            var count = Mathf.RoundToInt(110 * theme.Cracks);
            var points = new List<Vector2>();
            for (var attempt = 0; attempt < count * 8 && cracks.Count < count; attempt++)
            {
                var p = new Vector2((float)(rng.NextDouble() * 2 - 1) * half, (float)(rng.NextDouble() * 2 - 1) * half);
                if (!CrackClear(world, p)) continue;
                points.Clear();
                points.Add(p);
                var heading = (float)(rng.NextDouble() * Math.PI * 2);
                var steps = rng.Next(4, 11);
                for (var k = 0; k < steps; k++)
                {
                    heading += (float)(rng.NextDouble() - 0.5) * 1.3f;
                    var step = 1.1f + (float)rng.NextDouble() * 1.9f;
                    var q = p + new Vector2(Mathf.Cos(heading), Mathf.Sin(heading)) * step;
                    if (Mathf.Abs(q.x) > half || Mathf.Abs(q.y) > half || !CrackClear(world, q)) break;
                    points.Add(q);
                    p = q;
                }
                if (points.Count >= 3) cracks.Add(points.ToArray());
            }
            return cracks;
        }

        private static bool CrackClear(SimWorld world, Vector2 p)
        {
            var at = new System.Numerics.Vector2(p.x, p.y);
            foreach (var team in world.Map.Teams)
                if (System.Numerics.Vector2.Distance(team.Rally, at) < 9f) return false;
            foreach (var prop in world.Props)
                if (prop.Def.BlocksMovement && prop.Def.Id != "lava_pool" && prop.Contains(at, 1.2f)) return false;
            foreach (var road in world.Map.Roads)
                for (var i = 0; i < road.Points.Count - 1; i++)
                {
                    var a = new Vector2(road.Points[i].X, road.Points[i].Y);
                    var b = new Vector2(road.Points[i + 1].X, road.Points[i + 1].Y);
                    if (DistanceToSegment(p, a, b) < road.Width * 0.5f + 0.6f) return false;
                }
            return true;
        }

        /// <summary>3d_astra's surface noise, plus a broad layer so large maps do not repeat.</summary>
        private static Color Surface(float x, float z, TerrainTheme t)
        {
            var n = Mathf.Sin(x * 0.13f) * Mathf.Cos(z * 0.17f) + Mathf.Sin((x + z) * 0.09f);
            n += (Mathf.PerlinNoise(x * 0.018f + 11f, z * 0.018f + 3f) - 0.5f) * 1.2f;
            if (n > 0.65f) return Color.Lerp(t.Grass, t.Sand, Mathf.Clamp01((n - 0.65f) * 3f));
            if (n < -0.4f) return Color.Lerp(t.Grass, t.Dirt, Mathf.Clamp01((-0.4f - n) * 3f));
            return t.Grass;
        }

        /// <summary>
        /// City ground: concrete slabs (a faint 3 m joint grid), weathered into lighter and darker
        /// patches by the same broad noise as the countryside.
        /// </summary>
        private static Color Pavement(float x, float z, TerrainTheme t)
        {
            var colour = Surface(x, z, t);
            var jx = Mathf.Abs(Mathf.Repeat(x, 3f) - 1.5f);
            var jz = Mathf.Abs(Mathf.Repeat(z, 3f) - 1.5f);
            var joint = Mathf.Max(jx, jz) > 1.42f ? 0.9f : 1f;
            var wear = 0.94f + 0.08f * Mathf.PerlinNoise(x * 0.4f + 5f, z * 0.4f + 2f);
            return colour * joint * wear;
        }

        /// <summary>Tracks are the theme's road colour; on an airfield the wide ones are concrete.</summary>
        private static Color RoadColour(float width, bool airfield, TerrainTheme theme)
        {
            if (!airfield || width < TaxiwayWidth) return theme.Road;
            var concrete = Color.Lerp(theme.Stone, new Color(0.78f, 0.77f, 0.73f), 0.55f);
            return width >= RunwayWidth ? concrete * 0.86f : concrete;
        }

        /// <summary>Main road from camp to camp through the town, plus spurs to the fuel depots.</summary>
        private static List<(Vector2[] points, float width)> Roads(SimWorld world)
        {
            var roads = new List<(Vector2[] points, float width)>();
            // Maps that lay out their own streets (towns) use those.
            if (world.Map.Roads.Count > 0)
            {
                foreach (var road in world.Map.Roads)
                {
                    var points = new List<Vector2>();
                    for (var i = 0; i < road.Points.Count - 1; i++)
                    {
                        var a = new Vector2(road.Points[i].X, road.Points[i].Y);
                        var b = new Vector2(road.Points[i + 1].X, road.Points[i + 1].Y);
                        var steps = Mathf.Max(1, Mathf.CeilToInt(Vector2.Distance(a, b) / 2f));
                        for (var k = 0; k < steps; k++) points.Add(Vector2.Lerp(a, b, k / (float)steps));
                    }
                    var last = road.Points[road.Points.Count - 1];
                    points.Add(new Vector2(last.X, last.Y));
                    roads.Add((points.ToArray(), road.Width));
                }
                return roads;
            }
            var rallies = new List<Vector2>();
            foreach (var team in world.Map.Teams) rallies.Add(new Vector2(team.Rally.X, team.Rally.Y));
            if (rallies.Count >= 2)
            {
                var a = rallies[0];
                var b = rallies[1];
                roads.Add((Bezier(a, a + new Vector2(30f, 10f), b - new Vector2(30f, 10f), b), 5.2f));
                roads.Add((Bezier(a, new Vector2(a.x + 10f, 20f), new Vector2(-10f, b.y - 5f), b), 5.2f));
            }
            foreach (var prop in world.Props)
                if (prop.Def.Id == "fuel_tank")
                {
                    var p = new Vector2(prop.Position.X, prop.Position.Y);
                    roads.Add((Bezier(Vector2.zero, p * 0.3f + new Vector2(p.y, -p.x) * 0.15f, p * 0.7f, p), 5.2f));
                }
            return roads;
        }

        private static Vector2[] Bezier(Vector2 a, Vector2 b, Vector2 c, Vector2 d)
        {
            var points = new Vector2[48];
            for (var i = 0; i < points.Length; i++)
            {
                var t = i / (points.Length - 1f);
                var u = 1f - t;
                points[i] = u * u * u * a + 3f * u * u * t * b + 3f * u * t * t * c + t * t * t * d;
            }
            return points;
        }

        /// <param name="crisp">
        /// Paved ground (airfields, cities): the narrow roads go down first so a runway or an
        /// avenue paints over the tracks that join it, and paved roads get a crisp kerb instead
        /// of a worn, wobbly edge.
        /// </param>
        private static void PaintRoads(Color[] pixels, int size, float half, float worldPerPixel, List<(Vector2[] points, float width)> roads,
            Func<float, Color> colourOf, bool crisp)
        {
            const float feather = 2.2f;
            var order = new List<(Vector2[] points, float width)>(roads);
            if (crisp) order.Sort((a, b) => a.width.CompareTo(b.width));
            foreach (var (points, roadWidth) in order)
            {
                var road = colourOf(roadWidth);
                var paved = crisp && (road != colourOf(0f) || roadWidth >= 12f);
                var edge = paved ? 0.5f : feather;
                for (var s = 0; s < points.Length - 1; s++)
                {
                    var width = roadWidth * 0.5f;
                    var reach = width + edge;
                    var a = points[s];
                    var b = points[s + 1];
                    var minX = ToPixel(Mathf.Min(a.x, b.x) - reach, half, worldPerPixel, size);
                    var maxX = ToPixel(Mathf.Max(a.x, b.x) + reach, half, worldPerPixel, size);
                    var minY = ToPixel(Mathf.Min(a.y, b.y) - reach, half, worldPerPixel, size);
                    var maxY = ToPixel(Mathf.Max(a.y, b.y) + reach, half, worldPerPixel, size);
                    for (var y = minY; y <= maxY; y++)
                    for (var x = minX; x <= maxX; x++)
                    {
                        var p = new Vector2((x + 0.5f) * worldPerPixel - half, (y + 0.5f) * worldPerPixel - half);
                        var d = DistanceToSegment(p, a, b);
                        if (d > reach) continue;
                        var wobble = paved ? 0f : Mathf.PerlinNoise(p.x * 0.3f, p.y * 0.3f) * 0.8f;
                        var k = 1f - Mathf.Clamp01((d - width + wobble) / edge);
                        var i = y * size + x;
                        pixels[i] = Color.Lerp(pixels[i], road, k * (paved ? 0.97f : 0.85f));
                    }
                }
            }
        }

        private static readonly HashSet<string> Unmarked = new()
        {
            "tree", "palm", "cactus", "barrel", "ammo_crate", "car", "truck", "fence", "hedge", "stone_wall", "sandbags",
            "tank_trap", "lamp_post", "jersey_barrier", "dock_bollards", "mesa", "snow_rock", "pipeline", "market_stall",
            "charred_tree", "jungle_tree_a", "jungle_tree_b", "jungle_tree_c", "bamboo_clump", "fern_bush", "basalt_rock_a",
            "basalt_rock_b", "basalt_rock_c", "obsidian_spire", "volcanic_cliff", "runway_light", "traffic_light", "billboard",
            "bus", "fuel_truck", "parked_jet", "razor_wire", "sandbag_wall", "floodlight_mast", "base_gate",
        };

        private static readonly HashSet<string> PavedUnder = new()
        {
            "fuel_tank", "storage_tank", "refinery_tower", "oil_pump", "container", "container_stack", "gantry_crane", "factory",
            "office_block", "rail_tanker", "rail_boxcar", "radar_station", "hangar", "control_tower", "radar_dome", "revetment",
            "highrise_a", "highrise_b", "skyscraper", "parking_garage", "command_hq", "base_wall", "fuel_depot", "ammo_dump",
            "vehicle_hangar", "helipad",
        };

        private static readonly HashSet<string> Greenery = new() { "tree", "hedge", "bush", "fern_bush" };

        /// <summary>
        /// Trampled dirt round buildings and walls, concrete pads under tanks and industry, lawns
        /// under city trees, a black crust with an ember halo round lava, mud round river water.
        /// </summary>
        private static void PaintFootprints(Color[] pixels, int size, float half, float worldPerPixel, SimWorld world,
            MapTheme mapTheme)
        {
            var theme = mapTheme.Palette;
            var crust = Color.Lerp(theme.Dirt, Color.black, 0.45f);
            var ember = new Color(0.55f, 0.2f, 0.07f);
            var mud = Color.Lerp(theme.Dirt, new Color(0.3f, 0.24f, 0.16f), 0.4f);
            foreach (var prop in world.Props)
            {
                var id = prop.Def.Id;
                Color colour, rim;
                float margin, strength;
                var round = false;
                if (id == "lava_pool")
                {
                    colour = crust;
                    rim = Color.Lerp(crust, ember, 0.7f);
                    margin = 2.6f;
                    strength = 0.9f;
                }
                else if (id is "river_water" or "river_ford")
                {
                    colour = mud * 0.8f;
                    rim = Color.Lerp(mud, theme.Sand, 0.3f);
                    margin = 2.2f;
                    strength = 0.85f;
                }
                else if (mapTheme.Paved && Greenery.Contains(id))
                {
                    // Lawns: a soft round patch under each tree, a strip under each hedge.
                    colour = rim = mapTheme.Lawn * (0.92f + 0.12f * Mathf.PerlinNoise(prop.Position.X * 0.3f, prop.Position.Y * 0.3f));
                    margin = id == "hedge" ? 1.6f : 2.2f;
                    strength = 0.95f;
                    round = id != "hedge";
                }
                else if (Unmarked.Contains(id))
                {
                    continue;
                }
                else
                {
                    // Concrete pads under tanks and industry; trampled earth round houses.
                    colour = rim = PavedUnder.Contains(id) || mapTheme.Paved ? theme.Stone : Color.Lerp(theme.Dirt, theme.Road, 0.4f);
                    margin = id is "wall" or "base_wall" ? 1.2f : 2.4f;
                    strength = 0.7f;
                }
                var hx = prop.Width * 0.5f + margin;
                var hz = prop.Depth * 0.5f + margin;
                var minX = ToPixel(prop.Position.X - hx, half, worldPerPixel, size);
                var maxX = ToPixel(prop.Position.X + hx, half, worldPerPixel, size);
                var minY = ToPixel(prop.Position.Y - hz, half, worldPerPixel, size);
                var maxY = ToPixel(prop.Position.Y + hz, half, worldPerPixel, size);
                for (var y = minY; y <= maxY; y++)
                for (var x = minX; x <= maxX; x++)
                {
                    var wx = (x + 0.5f) * worldPerPixel - half - prop.Position.X;
                    var wz = (y + 0.5f) * worldPerPixel - half - prop.Position.Y;
                    var edge = round
                        ? Mathf.Sqrt(wx * wx + wz * wz) - Mathf.Max(prop.Width, prop.Depth) * 0.5f
                        : Mathf.Max(Mathf.Abs(wx) - (hx - margin), Mathf.Abs(wz) - (hz - margin));
                    if (edge > margin) continue;
                    var k = 1f - Mathf.Clamp01(edge / margin);
                    var i = y * size + x;
                    // Inside the footprint the pad colour; outside it the rim fades out.
                    pixels[i] = Color.Lerp(pixels[i], edge <= 0f ? colour : rim, k * strength);
                }
            }
        }

        /// <summary>Dark fissures under the glowing cracks, with a faint warm scorch round them.</summary>
        private static void PaintCracks(Color[] pixels, int size, float half, float worldPerPixel, List<Vector2[]> cracks)
        {
            var fissure = new Color(0.06f, 0.04f, 0.035f);
            var scorch = new Color(0.32f, 0.14f, 0.07f);
            foreach (var crack in cracks)
                for (var i = 0; i < crack.Length - 1; i++)
                {
                    Stroke(pixels, size, half, worldPerPixel, crack[i], crack[i + 1], 2.0f, scorch, 0.35f);
                    Stroke(pixels, size, half, worldPerPixel, crack[i], crack[i + 1], 0.7f, fissure, 0.9f);
                }
        }

        /// <summary>
        /// City streets: a dashed white centre line and solid edge lines on every avenue (left out
        /// where another street crosses), and zebra crossings on every approach to a junction.
        /// </summary>
        private static void PaintStreetMarkings(Color[] pixels, int size, float half, float worldPerPixel,
            List<(Vector2[] points, float width)> roads)
        {
            var white = new Color(0.9f, 0.9f, 0.86f);
            for (var r = 0; r < roads.Count; r++)
            {
                var (points, width) = roads[r];
                if (width < 6f) continue;
                var along = 0f;
                for (var s = 0; s < points.Length - 1; s++)
                {
                    var a = points[s];
                    var b = points[s + 1];
                    var length = Vector2.Distance(a, b);
                    if (length < 1e-3f) continue;
                    var dir = (b - a) / length;
                    var side = new Vector2(-dir.y, dir.x);
                    for (var u = 0f; u < length; u += 0.5f)
                    {
                        var p = a + dir * u;
                        if (InsideOtherRoad(roads, r, p, 1.2f)) continue;
                        var q = p + dir * 0.5f;
                        // Centre line: 3 m dashes, 3 m gaps.
                        if (Mathf.Repeat(along + u, 6f) < 3f) Stroke(pixels, size, half, worldPerPixel, p, q, 0.24f, white, 0.9f);
                        foreach (var offset in new[] { -1f, 1f })
                        {
                            var o = side * offset * (width * 0.5f - 0.75f);
                            Stroke(pixels, size, half, worldPerPixel, p + o, q + o, 0.16f, white, 0.8f);
                        }
                    }
                    along += length;
                }
            }
            // Zebra crossings where two streets meet: stripes along the street, across its width,
            // just outside the junction on each of its four approaches.
            foreach (var (centre, dirA, widthA, dirB, widthB) in Junctions(roads))
                foreach (var (dir, width, other) in new[] { (dirA, widthA, widthB), (dirB, widthB, widthA) })
                {
                    if (width < 6f) continue;
                    var side = new Vector2(-dir.y, dir.x);
                    foreach (var sign in new[] { -1f, 1f })
                    {
                        var start = centre + dir * sign * (other * 0.5f + 1.4f);
                        var end = centre + dir * sign * (other * 0.5f + 4.2f);
                        for (var t = -width * 0.5f + 1.2f; t <= width * 0.5f - 1.2f; t += 1.2f)
                            Stroke(pixels, size, half, worldPerPixel, start + side * t, end + side * t, 0.55f, white, 0.9f);
                    }
                }
        }

        /// <summary>
        /// Runways: a dashed centre line, solid edge lines and piano-key threshold bars at both
        /// ends; taxiways and aprons: a solid yellow centre line.
        /// </summary>
        private static void PaintAirfieldMarkings(Color[] pixels, int size, float half, float worldPerPixel,
            List<(Vector2[] points, float width)> roads)
        {
            var white = new Color(0.93f, 0.93f, 0.9f);
            var yellow = new Color(0.92f, 0.74f, 0.2f);
            for (var r = 0; r < roads.Count; r++)
            {
                var (points, width) = roads[r];
                if (width < TaxiwayWidth) continue;
                var runway = width >= RunwayWidth;
                var total = 0f;
                for (var s = 0; s < points.Length - 1; s++) total += Vector2.Distance(points[s], points[s + 1]);
                var along = 0f;
                for (var s = 0; s < points.Length - 1; s++)
                {
                    var a = points[s];
                    var b = points[s + 1];
                    var length = Vector2.Distance(a, b);
                    if (length < 1e-3f) continue;
                    var dir = (b - a) / length;
                    var side = new Vector2(-dir.y, dir.x);
                    for (var u = 0f; u < length; u += 0.5f)
                    {
                        var p = a + dir * u;
                        var q = p + dir * 0.5f;
                        var at = along + u;
                        if (runway)
                        {
                            var threshold = at < 16f || at > total - 16f;
                            if (!threshold && Mathf.Repeat(at, 14f) < 8f)
                                Stroke(pixels, size, half, worldPerPixel, p, q, 0.9f, white, 0.92f);
                            foreach (var offset in new[] { -1f, 1f })
                            {
                                var o = side * offset * (width * 0.5f - 1.1f);
                                Stroke(pixels, size, half, worldPerPixel, p + o, q + o, 0.45f, white, 0.9f);
                            }
                            // Piano keys: bars along the runway from 3 m to 13 m in from each end.
                            if ((at > 3f && at < 13f) || (at > total - 13f && at < total - 3f))
                                for (var t = 1.6f; t < width * 0.5f - 2.2f; t += 1.9f)
                                    foreach (var offset in new[] { -1f, 1f })
                                    {
                                        var o = side * offset * t;
                                        Stroke(pixels, size, half, worldPerPixel, p + o, q + o, 0.95f, white, 0.92f);
                                    }
                        }
                        else if (!InsideOtherRoad(roads, r, p, -2f, RunwayWidth))
                        {
                            Stroke(pixels, size, half, worldPerPixel, p, q, 0.32f, yellow, 0.9f);
                        }
                    }
                    along += length;
                }
            }
        }

        /// <summary>Whether a point lies on another road at least <paramref name="minWidth"/> wide (a junction).</summary>
        private static bool InsideOtherRoad(List<(Vector2[] points, float width)> roads, int self, Vector2 p, float margin,
            float minWidth = 6f)
        {
            for (var r = 0; r < roads.Count; r++)
            {
                if (r == self || roads[r].width < minWidth) continue;
                var (points, width) = roads[r];
                for (var s = 0; s < points.Length - 1; s++)
                    if (DistanceToSegment(p, points[s], points[s + 1]) < width * 0.5f + margin) return true;
            }
            return false;
        }

        /// <summary>Crossing points of straight street segments (the grid's junctions).</summary>
        private static List<(Vector2 centre, Vector2 dirA, float widthA, Vector2 dirB, float widthB)> Junctions(
            List<(Vector2[] points, float width)> roads)
        {
            var found = new List<(Vector2, Vector2, float, Vector2, float)>();
            for (var i = 0; i < roads.Count; i++)
            for (var j = i + 1; j < roads.Count; j++)
            {
                var (pa, wa) = roads[i];
                var (pb, wb) = roads[j];
                for (var s = 0; s < pa.Length - 1; s++)
                for (var t = 0; t < pb.Length - 1; t++)
                {
                    if (!Intersect(pa[s], pa[s + 1], pb[t], pb[t + 1], out var hit)) continue;
                    var duplicate = false;
                    foreach (var f in found)
                        if (Vector2.Distance(f.Item1, hit) < 3f) duplicate = true;
                    if (duplicate) continue;
                    found.Add((hit, (pa[s + 1] - pa[s]).normalized, wa, (pb[t + 1] - pb[t]).normalized, wb));
                }
            }
            return found;
        }

        private static bool Intersect(Vector2 a, Vector2 b, Vector2 c, Vector2 d, out Vector2 hit)
        {
            hit = default;
            var r = b - a;
            var s = d - c;
            var denom = r.x * s.y - r.y * s.x;
            if (Mathf.Abs(denom) < 1e-5f) return false;
            var t = ((c.x - a.x) * s.y - (c.y - a.y) * s.x) / denom;
            var u = ((c.x - a.x) * r.y - (c.y - a.y) * r.x) / denom;
            if (t < 0f || t > 1f || u < 0f || u > 1f) return false;
            hit = a + r * t;
            return true;
        }

        /// <summary>A soft-edged line of paint from a to b.</summary>
        private static void Stroke(Color[] pixels, int size, float half, float worldPerPixel, Vector2 a, Vector2 b, float width,
            Color colour, float alpha)
        {
            var r = width * 0.5f;
            var feather = worldPerPixel * 0.75f;
            var minX = ToPixel(Mathf.Min(a.x, b.x) - r - feather, half, worldPerPixel, size);
            var maxX = ToPixel(Mathf.Max(a.x, b.x) + r + feather, half, worldPerPixel, size);
            var minY = ToPixel(Mathf.Min(a.y, b.y) - r - feather, half, worldPerPixel, size);
            var maxY = ToPixel(Mathf.Max(a.y, b.y) + r + feather, half, worldPerPixel, size);
            for (var y = minY; y <= maxY; y++)
            for (var x = minX; x <= maxX; x++)
            {
                var p = new Vector2((x + 0.5f) * worldPerPixel - half, (y + 0.5f) * worldPerPixel - half);
                var d = DistanceToSegment(p, a, b) - r;
                if (d > feather) continue;
                var k = d <= 0f ? 1f : 1f - d / feather;
                var i = y * size + x;
                pixels[i] = Color.Lerp(pixels[i], colour, k * alpha);
            }
        }

        /// <summary>Separable box blur: turns noise thresholds into soft natural borders.</summary>
        private static void Blur(Color[] pixels, int size, int radius)
        {
            var temp = new Color[pixels.Length];
            for (var pass = 0; pass < 2; pass++)
            {
                var horizontal = pass == 0;
                var src = horizontal ? pixels : temp;
                var dst = horizontal ? temp : pixels;
                for (var a = 0; a < size; a++)
                for (var b = 0; b < size; b++)
                {
                    var sum = Color.clear;
                    var count = 0;
                    for (var k = -radius; k <= radius; k++)
                    {
                        var c = Math.Clamp(b + k, 0, size - 1);
                        sum += horizontal ? src[a * size + c] : src[c * size + a];
                        count++;
                    }
                    var i = horizontal ? a * size + b : b * size + a;
                    dst[i] = sum / count;
                }
            }
        }

        /// <summary>Faint light and dark dots of varied size, as in the reference's 16,000 speckles.</summary>
        private static void Speckle(Color[] pixels, int size, Random rng, Color light, Color dark)
        {
            var scale = size / 1024f;
            for (var n = 0; n < 16000; n++)
            {
                var cx = rng.NextDouble() * size;
                var cy = rng.NextDouble() * size;
                var r = (1 + rng.NextDouble() * 10) * scale;
                var bright = rng.NextDouble() > 0.5;
                var alpha = (float)rng.NextDouble() * (bright ? 0.09f : 0.08f);
                var colour = bright ? light : dark;
                var ri = (int)Math.Ceiling(r);
                for (var dy = -ri; dy <= ri; dy++)
                for (var dx = -ri; dx <= ri; dx++)
                {
                    if (dx * dx + dy * dy > r * r) continue;
                    var x = (int)cx + dx;
                    var y = (int)cy + dy;
                    if (x < 0 || y < 0 || x >= size || y >= size) continue;
                    var i = y * size + x;
                    pixels[i] = Color.Lerp(pixels[i], colour, alpha);
                }
            }
        }

        private static int ToPixel(float world, float half, float worldPerPixel, int size) =>
            Math.Clamp((int)((world + half) / worldPerPixel), 0, size - 1);

        internal static float DistanceToSegment(Vector2 p, Vector2 a, Vector2 b)
        {
            var ab = b - a;
            var t = Mathf.Clamp01(Vector2.Dot(p - a, ab) / Mathf.Max(ab.sqrMagnitude, 1e-6f));
            return Vector2.Distance(p, a + ab * t);
        }
    }
}
