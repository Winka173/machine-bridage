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
    /// under buildings, then thousands of faint light and dark speckles for texture.
    /// </summary>
    public static class TerrainPainter
    {
        public static Texture2D Paint(SimWorld world, TerrainTheme theme, int size = 1024)
        {
            var map = world.Map;
            var pixels = new Color[size * size];
            var worldPerPixel = map.Size / size;

            for (var y = 0; y < size; y++)
            for (var x = 0; x < size; x++)
            {
                var wx = (x + 0.5f) * worldPerPixel - map.HalfSize;
                var wz = (y + 0.5f) * worldPerPixel - map.HalfSize;
                pixels[y * size + x] = Surface(wx, wz, theme);
            }

            var roads = Roads(world);
            PaintRoads(pixels, size, map.HalfSize, worldPerPixel, roads, theme.Road);
            PaintFootprints(pixels, size, map.HalfSize, worldPerPixel, world, theme);
            Blur(pixels, size, 2);
            Speckle(pixels, size, new Random(1482));

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

        /// <summary>3d_astra's surface noise, plus a broad layer so large maps do not repeat.</summary>
        private static Color Surface(float x, float z, TerrainTheme t)
        {
            var n = Mathf.Sin(x * 0.13f) * Mathf.Cos(z * 0.17f) + Mathf.Sin((x + z) * 0.09f);
            n += (Mathf.PerlinNoise(x * 0.018f + 11f, z * 0.018f + 3f) - 0.5f) * 1.2f;
            if (n > 0.65f) return Color.Lerp(t.Grass, t.Sand, Mathf.Clamp01((n - 0.65f) * 3f));
            if (n < -0.4f) return Color.Lerp(t.Grass, t.Dirt, Mathf.Clamp01((-0.4f - n) * 3f));
            return t.Grass;
        }

        /// <summary>Main road from camp to camp through the town, plus spurs to the fuel depots.</summary>
        private static List<Vector2[]> Roads(SimWorld world)
        {
            var roads = new List<Vector2[]>();
            var rallies = new List<Vector2>();
            foreach (var team in world.Map.Teams) rallies.Add(new Vector2(team.Rally.X, team.Rally.Y));
            if (rallies.Count >= 2)
            {
                var a = rallies[0];
                var b = rallies[1];
                roads.Add(Bezier(a, a + new Vector2(30f, 10f), b - new Vector2(30f, 10f), b));
                roads.Add(Bezier(a, new Vector2(a.x + 10f, 20f), new Vector2(-10f, b.y - 5f), b));
            }
            foreach (var prop in world.Props)
                if (prop.Def.Id == "fuel_tank")
                {
                    var p = new Vector2(prop.Position.X, prop.Position.Y);
                    roads.Add(Bezier(Vector2.zero, p * 0.3f + new Vector2(p.y, -p.x) * 0.15f, p * 0.7f, p));
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

        private static void PaintRoads(Color[] pixels, int size, float half, float worldPerPixel, List<Vector2[]> roads,
            Color road)
        {
            const float width = 2.6f;
            const float feather = 2.2f;
            var reach = width + feather;
            foreach (var points in roads)
            for (var s = 0; s < points.Length - 1; s++)
            {
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
                    var wobble = Mathf.PerlinNoise(p.x * 0.3f, p.y * 0.3f) * 0.8f;
                    var k = 1f - Mathf.Clamp01((d - width + wobble) / feather);
                    var i = y * size + x;
                    pixels[i] = Color.Lerp(pixels[i], road, k * 0.85f);
                }
            }
        }

        /// <summary>Trampled dirt around buildings and walls, stone pads under fuel tanks.</summary>
        private static void PaintFootprints(Color[] pixels, int size, float half, float worldPerPixel, SimWorld world,
            TerrainTheme theme)
        {
            foreach (var prop in world.Props)
            {
                var id = prop.Def.Id;
                if (id == "tree" || id == "barrel" || id == "ammo_crate") continue;
                var colour = id == "fuel_tank" ? theme.Stone : Color.Lerp(theme.Dirt, theme.Road, 0.4f);
                var margin = id == "wall" ? 1.2f : 2.4f;
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
                    var edge = Mathf.Max(Mathf.Abs(wx) - (hx - margin), Mathf.Abs(wz) - (hz - margin));
                    var k = 1f - Mathf.Clamp01(edge / margin);
                    var i = y * size + x;
                    pixels[i] = Color.Lerp(pixels[i], colour, k * 0.7f);
                }
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
        private static void Speckle(Color[] pixels, int size, Random rng)
        {
            var light = new Color(209 / 255f, 188 / 255f, 128 / 255f);
            var dark = new Color(31 / 255f, 58 / 255f, 40 / 255f);
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

        private static float DistanceToSegment(Vector2 p, Vector2 a, Vector2 b)
        {
            var ab = b - a;
            var t = Mathf.Clamp01(Vector2.Dot(p - a, ab) / Mathf.Max(ab.sqrMagnitude, 1e-6f));
            return Vector2.Distance(p, a + ab * t);
        }
    }
}
