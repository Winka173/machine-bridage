using System;
using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim;
using UnityEngine;
using UnityEngine.Rendering;
using Object = UnityEngine.Object;
using Random = System.Random;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Countryside around the battlefield, so zooming out never shows an empty void: ground all
    /// the way to the horizon (slightly darker than the playable area, which marks the boundary),
    /// a continuous mountain range that rises behind the map (highest along the top of the
    /// screen, low hills in front, a river valley cut through it), thick forests climbing its
    /// slopes, rock on the heights and snow on the peaks, plus farm fields with farmhouses. It is
    /// decoration only: the simulation and the camera clamp stay inside the map. Trees and rocks
    /// are drawn with GPU instancing in culled cells, so thousands of them cost a few draw calls.
    /// Themes change the picture: a volcanic map has a glowing lava river and fumaroles, a city
    /// continues its street grid out to the hills with a tower in every block and a canal.
    /// </summary>
    public sealed class Surroundings : IDisposable
    {
        private const float Extent = 230f; // half-size of the decorated area

        private readonly GameObject _root;
        private readonly List<Mesh> _meshes = new();
        /// <summary>Instances are grouped into square cells so the camera and shadow passes cull them.</summary>
        private const float CellSize = 80f;

        /// <summary>Scenery further than this outside the map edge casts no shadow (it sits in the haze).</summary>
        private const float ShadowReach = 45f;

        private readonly Dictionary<(int cell, Mesh mesh, int submesh, Material material), List<Matrix4x4>> _instances = new();
        private readonly Dictionary<int, Bounds> _cellBounds = new();
        private readonly List<(Mesh mesh, int submesh, Matrix4x4[] matrices, RenderParams parameters)> _draws = new();
        private readonly Texture2D _texture;
        private readonly float _half;
        private readonly Random _rng = new(97);

        public Surroundings(SimWorld world, ModelLibrary models, MaterialLibrary materials, MapTheme theme, Transform parent,
            Match.GraphicsOptions options = null)
        {
            _half = world.Map.HalfSize;
            _field = BoundaryField.For(world.Map);
            _theme = theme;
            options ??= Match.GraphicsOptions.For(Match.GraphicsQuality.High);
            _density = options.RichScenery ? 1f : 0.5f;
            // Scenery near the edge casts shadows into view; further out it sits in the haze.
            _shadowReach = options.Shadows switch
            {
                Match.ShadowLevel.Off => -999f,
                Match.ShadowLevel.Low => 20f,
                Match.ShadowLevel.Medium => ShadowReach,
                _ => ShadowReach + 20f,
            };
            _root = new GameObject("Surroundings");
            _root.transform.SetParent(parent, false);

            var fields = theme.Fields ? Fields() : new List<Rect>();
            _texture = PaintOuter(theme, fields);
            materials.OuterGround.SetTexture("_BaseMap", _texture);
            var ground = Place("Outer Ground", Own(Plane(Extent * 2f, 16)), materials.OuterGround);
            ground.transform.position = new Vector3(0f, -0.03f, 0f);
            // Ground beyond the decorated area, out to the fog, so no view ever ends in a void.
            var horizon = Place("Horizon Ground", Own(Plane(Extent * 6f, 4)), materials.Skirt);
            horizon.transform.position = new Vector3(0f, -0.3f, 0f);

            _palette = TerrainPalette(theme);
            materials.Skirt.SetColor("_BaseColor", theme.Skirt);
            _rangeMaterial = materials.Terrain;
            _rangeMaterial.SetTexture("_BaseMap", _palette);
            if (!Match.DebugFlags.Has("-mb-no-range")) Place("Mountain Range", Own(MountainRange()), _rangeMaterial);

            materials.Water.SetColor("_BaseColor", theme.WaterColour);
            materials.Water.SetFloat("_Roughness", theme.WaterRoughness);
            if (theme.Water is ThemeWater.River or ThemeWater.FrozenRiver or ThemeWater.Canal)
            {
                var river = Place("River", Own(Plane(1f, 1)), materials.Water);
                river.transform.position = new Vector3(0f, -0.01f, RiverZ);
                river.transform.localScale = new Vector3(Extent * 2f, 1f, RiverWidth);
            }
            else if (theme.Water == ThemeWater.Lava)
            {
                // Molten rock glows on the unlit shader, so it lights up the valley at night.
                _lavaMaterial = new Material(Shader.Find("MachineBrigade/Unlit")) { name = "Lava River" };
                _lavaMaterial.SetColor("_Color", theme.LavaHot);
                var lava = Place("Lava River", Own(LavaRiver()), _lavaMaterial);
                lava.transform.position = new Vector3(0f, -0.01f, RiverZ);
            }
            else if (theme.Water == ThemeWater.Sea)
            {
                // The sea fills everything beyond the north edge, out past the fog.
                var sea = Place("Sea", Own(Plane(1f, 1)), materials.Water);
                sea.transform.position = new Vector3(0f, -0.02f, SeaShore + Extent * 1.5f);
                sea.transform.localScale = new Vector3(Extent * 6f, 1f, Extent * 3f);
            }

            if (theme.Skyline != null) BuildSkyline(models);
            if (_field.HasOutline) ScatterBays(models);
            ScatterForests(models, fields);
            ScatterRocks(models);
            ScatterScenery(models, fields);
            PlaceFarmhouses(models, fields);
            var total = 0;
            foreach (var entry in _instances)
            {
                var (cell, mesh, submesh, material) = entry.Key;
                var bounds = _cellBounds[cell];
                // Room for tall trees and outcrops above the ground-level centres.
                bounds.Expand(new Vector3(14f, 0f, 14f));
                bounds.SetMinMax(new Vector3(bounds.min.x, bounds.min.y - 1f, bounds.min.z), new Vector3(bounds.max.x, bounds.max.y + 16f, bounds.max.z));
                var edge = Mathf.Max(Mathf.Abs(bounds.center.x), Mathf.Abs(bounds.center.z)) - CellSize * 0.5f - _half;
                var parameters = new RenderParams(material)
                {
                    shadowCastingMode = edge < _shadowReach ? ShadowCastingMode.On : ShadowCastingMode.Off,
                    receiveShadows = true,
                    worldBounds = bounds,
                };
                _draws.Add((mesh, submesh, entry.Value.ToArray(), parameters));
                total += entry.Value.Count;
                InstancedTriangles += mesh.GetIndexCount(submesh) / 3 * entry.Value.Count;
            }
            _instances.Clear();
            Debug.Log($"[Surroundings] {_draws.Count} instanced batches, {total} instances, instancing supported: {SystemInfo.supportsInstancing}");
        }

        /// <summary>Triangles submitted per frame by the instanced scenery (for the perf probe).</summary>
        public long InstancedTriangles { get; private set; }

        public int Batches => _draws.Count;

        private readonly Texture2D _palette;
        private readonly BoundaryField _field;
        private readonly Material _rangeMaterial;
        private readonly MapTheme _theme;
        private readonly float _density, _shadowReach;
        private Material _lavaMaterial;

        private float RiverZ => _half + 62f;

        /// <summary>A city canal is narrow; rivers of water or lava are wide.</summary>
        private float RiverWidth => _theme.Water == ThemeWater.Canal ? 9f : 16f;

        /// <summary>The city's street grid continues the map's: 16 m avenues every 36 m, from x and z = 18.</summary>
        private const float BlockPitch = 36f;
        private const float AvenueWidth = 16f;

        private bool OnAvenue(float v) => Mathf.Abs(Mathf.Repeat(v - 18f + BlockPitch * 0.5f, BlockPitch) - BlockPitch * 0.5f) < AvenueWidth * 0.5f;

        /// <summary>Inside the city that surrounds an urban map (it ends where the hills begin).</summary>
        private bool InCity(Vector2 p) =>
            _theme.Skyline != null && Mathf.Max(Mathf.Abs(p.x), Mathf.Abs(p.y)) - _half < _theme.RangeStart - 6f;

        /// <summary>The quay line of a harbour map: the sea starts just past the north edge.</summary>
        private float SeaShore => _half + 5f;

        private bool HasRiver => _theme.Water is ThemeWater.River or ThemeWater.FrozenRiver or ThemeWater.Lava or ThemeWater.Canal;

        private bool InSea(Vector2 p, float margin) => _theme.Water == ThemeWater.Sea && p.y > SeaShore - margin;

        /// <summary>Submits the instanced scenery; call once per frame.</summary>
        public void Draw()
        {
            // Each batch carries its cell's bounds, so off-screen cells are culled by the engine
            // (from the shadow pass too) instead of every tree being drawn every frame.
            foreach (var (mesh, submesh, matrices, parameters) in _draws)
                for (var start = 0; start < matrices.Length; start += 1023)
                    Graphics.RenderMeshInstanced(parameters, mesh, submesh, matrices, Mathf.Min(1023, matrices.Length - start), start);
        }

        public void Dispose()
        {
            if (_root != null) Object.Destroy(_root);
            foreach (var mesh in _meshes)
                if (mesh != null) Object.Destroy(mesh);
            if (_texture != null) Object.Destroy(_texture);
            if (_palette != null) Object.Destroy(_palette);
            if (_lavaMaterial != null) Object.Destroy(_lavaMaterial);
        }

        /// <summary>At least <paramref name="margin"/> metres beyond the battlefield's outline.</summary>
        private bool Outside(Vector2 p, float margin) => _field.Distance(p) > margin;

        private bool NearRiver(Vector2 p, float margin) =>
            (HasRiver && Mathf.Abs(p.y - RiverZ) < RiverWidth * 0.5f + margin) || InSea(p, margin);

        /// <summary>Rough terrain height at a ground point (0 on the flat around the map).</summary>
        private float Height(Vector2 p) => Mathf.Max(RangeHeight(p), BayHeight(p));

        /// <summary>
        /// The rough ground that fills the bays carved into the square by the battlefield's
        /// outline: it rises right at the edge into rocky knolls and ridges (kept low, so they
        /// frame the fight without hiding it) and runs out into the countryside past the square.
        /// </summary>
        private float BayHeight(Vector2 p)
        {
            if (!_field.HasOutline) return 0f;
            var square = Mathf.Max(Mathf.Abs(p.x), Mathf.Abs(p.y)) - _half;
            if (square > 14f) return 0f;
            var d = _field.Distance(p);
            if (d < 0.8f) return 0f;
            var n = Mathf.PerlinNoise(p.x * 0.06f + 31.7f, p.y * 0.06f + 12.9f);
            var detail = Mathf.PerlinNoise(p.x * 0.19f + 5.3f, p.y * 0.19f + 17.1f);
            var top = (3.5f + 6.5f * n) * Mathf.Max(0.7f, _theme.Peaks) + detail * 1.4f;
            var rise = Edge(0.8f, 6.5f, d);
            var fade = 1f - Edge(0f, 14f, square);
            return rise * top * fade;
        }

        /// <summary>The mountain range out in the countryside, rising some way past the square.</summary>
        private float RangeHeight(Vector2 p)
        {
            var outside = Mathf.Max(Mathf.Abs(p.x), Mathf.Abs(p.y)) - _half;
            var start = Mathf.Max(MountainStart, _theme.RangeStart);
            if (outside < start || InSea(p, 0f)) return 0f;
            var ramp = Mathf.SmoothStep(0f, 1f, (outside - start) / 70f);
            // Tall along the far (top of the screen) sides, rolling hills on the near ones, so
            // the range frames the battle without hiding it.
            var back = Mathf.Clamp01(0.5f + 0.65f * Vector2.Dot(p.normalized, new Vector2(-0.7071f, 0.7071f)));
            var n = Mathf.PerlinNoise(p.x * 0.011f + 13.7f, p.y * 0.011f + 4.1f);
            var ridge = 1f - Mathf.Abs(n * 2f - 1f);
            ridge *= ridge;
            var detail = Mathf.PerlinNoise(p.x * 0.045f + 2.3f, p.y * 0.045f + 7.9f);
            var peak = (5f + back * back * 52f) * _theme.Peaks;
            var height = ramp * (peak * (0.3f + 0.7f * ridge) + detail * 5f);
            // A valley for the river; hills fall away to the shore on a harbour map.
            var valley = HasRiver ? Mathf.SmoothStep(0f, 1f, (Mathf.Abs(p.y - RiverZ) - RiverWidth * 0.5f - 3f) / 26f) : 1f;
            if (_theme.Water == ThemeWater.Sea) valley *= Mathf.SmoothStep(0f, 1f, (SeaShore - p.y) / 30f);
            return height * valley;
        }

        private const float MountainStart = 16f;
        private const float RangeCell = 5f;
        private const float TreeLine = 30f;
        private const float SnowLine = 40f;

        private static float Slope(Vector3 normal) => 1f - Mathf.Clamp01(normal.y);

        /// <summary>
        /// Shader-style smoothstep: 0 below <paramref name="from"/>, 1 above <paramref name="to"/>.
        /// (Unity's Mathf.SmoothStep interpolates between its first two arguments instead.)
        /// </summary>
        private static float Edge(float from, float to, float x)
        {
            var t = Mathf.Clamp01((x - from) / (to - from));
            return t * t * (3f - 2f * t);
        }

        /// <summary>
        /// The range as one faceted mesh: each triangle is flat-shaded and coloured from a small
        /// palette by its height and steepness (meadow, forest floor, rock, snow), the low-poly
        /// look of the reference. Flat cells are left out; the ground plane shows there.
        /// </summary>
        private Mesh MountainRange()
        {
            var vertices = new List<Vector3>();
            var normals = new List<Vector3>();
            var uvs = new List<UnityEngine.Vector2>();
            var colors = new List<Color>();
            var triangles = new List<int>();
            var cells = Mathf.CeilToInt(Extent * 2f / RangeCell);
            var heights = new float[(cells + 1) * (cells + 1)];
            for (var z = 0; z <= cells; z++)
            for (var x = 0; x <= cells; x++)
                heights[z * (cells + 1) + x] = Height(new Vector2(x * RangeCell - Extent, z * RangeCell - Extent));

            void Triangle(Vector3 a, Vector3 b, Vector3 c)
            {
                var normal = Vector3.Cross(b - a, c - a).normalized;
                if (normal.y < 0f)
                {
                    (b, c) = (c, b);
                    normal = -normal;
                }
                var height = (a.y + b.y + c.y) / 3f;
                var uv = new UnityEngine.Vector2(Mathf.Clamp01(height / (SnowLine + 8f)), Mathf.Clamp01(Slope(normal) * 1.6f));
                var start = vertices.Count;
                vertices.Add(a);
                vertices.Add(b);
                vertices.Add(c);
                for (var k = 0; k < 3; k++)
                {
                    normals.Add(normal);
                    uvs.Add(uv);
                    colors.Add(Color.white);
                    triangles.Add(start + k);
                }
            }

            for (var z = 0; z < cells; z++)
            for (var x = 0; x < cells; x++)
            {
                var h00 = heights[z * (cells + 1) + x];
                var h10 = heights[z * (cells + 1) + x + 1];
                var h01 = heights[(z + 1) * (cells + 1) + x];
                var h11 = heights[(z + 1) * (cells + 1) + x + 1];
                if (h00 < 0.05f && h10 < 0.05f && h01 < 0.05f && h11 < 0.05f) continue;
                // Flat corners dip under the ground plane so the seam never flickers.
                float Y(float h) => h < 0.05f ? -0.25f : h;
                var x0 = x * RangeCell - Extent;
                var z0 = z * RangeCell - Extent;
                var p00 = new Vector3(x0, Y(h00), z0);
                var p10 = new Vector3(x0 + RangeCell, Y(h10), z0);
                var p01 = new Vector3(x0, Y(h01), z0 + RangeCell);
                var p11 = new Vector3(x0 + RangeCell, Y(h11), z0 + RangeCell);
                // Alternate the diagonal so the facets do not line up in stripes.
                if (((x + z) & 1) == 0)
                {
                    Triangle(p00, p01, p11);
                    Triangle(p00, p11, p10);
                }
                else
                {
                    Triangle(p00, p01, p10);
                    Triangle(p10, p01, p11);
                }
            }

            var mesh = new Mesh { name = "Mountain Range", indexFormat = IndexFormat.UInt32 };
            mesh.SetVertices(vertices);
            mesh.SetNormals(normals);
            mesh.SetUVs(0, uvs);
            mesh.SetColors(colors);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateBounds();
            return mesh;
        }

        /// <summary>Terrain colours by height (u) and steepness (v).</summary>
        private static Texture2D TerrainPalette(MapTheme theme)
        {
            const int width = 64, height = 16;
            var pixels = new Color[width * height];
            var meadow = theme.Meadow;
            var forest = theme.ForestFloor;
            var rock = theme.Rock;
            var cliff = theme.Cliff;
            var snow = theme.Peak;
            var line = theme.PeakLine;
            for (var y = 0; y < height; y++)
            for (var x = 0; x < width; x++)
            {
                var h = x / (width - 1f);
                var steep = y / (height - 1f);
                var colour = Color.Lerp(meadow, forest, Edge(0.05f, 0.3f, h));
                colour = Color.Lerp(colour, rock, Edge(0.5f, 0.72f, h));
                colour = Color.Lerp(colour, cliff, Edge(0.45f, 0.8f, steep));
                // Snow settles on the gentler slopes of the peaks.
                colour = Color.Lerp(colour, snow, Edge(line, line + 0.08f, h) * (1f - Edge(0.55f, 0.85f, steep)));
                pixels[y * width + x] = colour;
            }
            var texture = new Texture2D(width, height, TextureFormat.RGBA32, false, false)
            {
                name = "Terrain Palette",
                wrapMode = TextureWrapMode.Clamp,
                filterMode = FilterMode.Point,
            };
            texture.SetPixels(pixels);
            texture.Apply(false, true);
            return texture;
        }

        private bool OnMountain(Vector2 p) => Height(p) > 0.6f;

        /// <summary>
        /// A dense tree line hugging the battlefield edge (it frames the fight), then forest
        /// clusters further out with a minimum density so no side of the view is ever bare.
        /// Fields stay clear.
        /// </summary>
        private void ScatterForests(ModelLibrary models, List<Rect> fields)
        {
            var placed = 0;
            for (var attempt = 0; attempt < 90000 && placed < 5200 * _density; attempt++)
            {
                var p = RandomPoint();
                if (!Outside(p, 4f) || NearRiver(p, 3f) || InField(p, fields)) continue;
                // The city has its own street trees (see BuildSkyline).
                if (InCity(p)) continue;
                var height = Height(p);
                if (height > TreeLine) continue;
                var distance = _field.Distance(p);
                var noise = Mathf.PerlinNoise(p.x * 0.035f + 5f, p.y * 0.035f + 9f);
                // A thick tree line along the map edge, then whole forests on the lower slopes,
                // thinning out towards the tree line.
                var chance = distance < 26f
                    ? 0.3f + 0.7f * Edge(0.2f, 0.55f, noise)
                    : height > 1f
                        ? (0.55f + 0.45f * Edge(0.3f, 0.6f, noise)) * (1f - Edge(TreeLine * 0.6f, TreeLine, height))
                        : 0.12f + 0.8f * Edge(0.42f, 0.68f, noise);
                if (_rng.NextDouble() > chance * _theme.Forest) continue;
                // Conifers take over up the mountain; the theme's lowland mix below.
                var pool = height > 8f ? _theme.HighlandTrees : _theme.LowlandTrees;
                var model = pool[_rng.Next(pool.Length)];
                Add(models, model, p, (float)_rng.NextDouble() * 360f, 0.8f + (float)_rng.NextDouble() * 0.7f, height - 0.1f);
                placed++;
            }
            if (_theme.Bush == null) return;
            for (var i = 0; i < 700; i++)
            {
                var p = RandomPoint();
                if (!Outside(p, 3f) || NearRiver(p, 1f) || InField(p, fields) || OnMountain(p) || InCity(p)) continue;
                Add(models, _theme.Bush, p, (float)_rng.NextDouble() * 360f, 0.7f + (float)_rng.NextDouble() * 0.9f);
            }
        }

        /// <summary>
        /// Fills the bays carved into the square with the theme's wild ground: a thick tree line
        /// along the edge, rocks and crags on the knolls, trees in the hollows.
        /// </summary>
        private void ScatterBays(ModelLibrary models)
        {
            var reach = _half + 10f;
            for (var attempt = 0; attempt < 26000 * _density; attempt++)
            {
                var p = new Vector2((float)(_rng.NextDouble() * 2 - 1) * reach, (float)(_rng.NextDouble() * 2 - 1) * reach);
                var d = _field.Distance(p);
                if (d < 2.2f || Mathf.Max(Mathf.Abs(p.x), Mathf.Abs(p.y)) > _half + 8f || InCity(p) || NearRiver(p, 1f)) continue;
                var height = Height(p);
                var roll = _rng.NextDouble();
                if (roll < 0.1 && _theme.Crags.Length > 0 && height > 2f)
                {
                    Add(models, _theme.Crags[_rng.Next(_theme.Crags.Length)], p, (float)_rng.NextDouble() * 360f,
                        0.6f + (float)_rng.NextDouble() * 0.7f, height - 0.6f);
                }
                else if (roll < 0.26 && _theme.Rocks.Length > 0)
                {
                    Add(models, _theme.Rocks[_rng.Next(_theme.Rocks.Length)], p, (float)_rng.NextDouble() * 360f,
                        0.9f + (float)_rng.NextDouble() * 1.8f, height - 0.35f);
                }
                else if (_theme.Forest > 0.05f && roll < 0.26 + 0.6 * _theme.Forest && height < TreeLine)
                {
                    // Densest right along the edge, thinning over the knolls.
                    var chance = d < 7f ? 0.85f : 0.45f;
                    if (_rng.NextDouble() > chance) continue;
                    var pool = height > 6f ? _theme.HighlandTrees : _theme.LowlandTrees;
                    Add(models, pool[_rng.Next(pool.Length)], p, (float)_rng.NextDouble() * 360f,
                        0.8f + (float)_rng.NextDouble() * 0.6f, height - 0.1f);
                }
            }
        }

        private static bool InField(Vector2 p, List<Rect> fields)
        {
            foreach (var field in fields)
                if (field.Contains(p)) return true;
            return false;
        }

        private void ScatterRocks(ModelLibrary models)
        {
            for (var i = 0; i < 260; i++)
            {
                var p = RandomPoint();
                if (!Outside(p, 6f) || NearRiver(p, 2f) || InCity(p)) continue;
                var height = Height(p);
                var model = _theme.Rocks[_rng.Next(_theme.Rocks.Length)];
                Add(models, model, p, (float)_rng.NextDouble() * 360f, 1.2f + (float)_rng.NextDouble() * 2.4f + height * 0.05f, height - 0.4f);
            }
            // Crags on the heights, outcrops and boulder fields breaking up the forests below.
            for (var i = 0; i < 140; i++)
            {
                var p = RandomPoint();
                if (!Outside(p, 10f) || NearRiver(p, 6f) || InCity(p)) continue;
                var height = Height(p);
                if (height < 2f && _rng.Next(3) != 0) continue;
                var model = _theme.Crags[_rng.Next(_theme.Crags.Length)];
                Add(models, model, p, (float)_rng.NextDouble() * 360f, 0.8f + (float)_rng.NextDouble() * 0.9f, height - 0.6f);
            }
        }

        /// <summary>
        /// The city round an urban map: the map's street grid carried on out to the hills, with a
        /// tower in every block (two smaller ones in some), taller towards the far side so the
        /// skyline frames the battle without hiding it. Their windows use the kit's glowing glass
        /// and lamp materials, which is what lights the city up at night.
        /// </summary>
        private void BuildSkyline(ModelLibrary models)
        {
            var kinds = _theme.Skyline;
            var reach = _half + _theme.RangeStart - 6f;
            var first = -Mathf.Floor(Extent / BlockPitch) * BlockPitch;
            for (var cx = first; cx <= Extent; cx += BlockPitch)
            for (var cz = first; cz <= Extent; cz += BlockPitch)
            {
                // Block centres sit half a pitch off the avenues: 0, +-36, +-72, ...
                var centre = new Vector2(cx, cz);
                var outside = Mathf.Max(Mathf.Abs(cx), Mathf.Abs(cz)) - _half;
                if (outside < 18f || Mathf.Max(Mathf.Abs(cx), Mathf.Abs(cz)) > reach || NearRiver(centre, 11f)) continue;
                // Towers only in the ring the camera can see; a tower is thousands of triangles in a
                // dozen materials, and a city of them out to the horizon cost more than the battle.
                if (outside > 62f) continue;
                if (outside > 40f)
                {
                    Add(models, _rng.Next(2) == 0 ? "office_block" : "apartment", centre, _rng.Next(4) * 90f, 1f + (float)_rng.NextDouble() * 0.2f);
                    continue;
                }
                var back = Mathf.Clamp01(0.5f + 0.5f * Vector2.Dot(centre.normalized, new Vector2(-0.7071f, 0.7071f)));
                if (_rng.Next(4) == 0)
                {
                    // Two mid-size towers side by side.
                    for (var k = -1; k <= 1; k += 2)
                    {
                        var at = centre + new Vector2(k * 5f, -k * 1.5f);
                        Add(models, kinds[_rng.Next(kinds.Length)], at, _rng.Next(4) * 90f, 0.62f + (float)_rng.NextDouble() * 0.12f);
                    }
                    continue;
                }
                var scale = 0.95f + back * 0.3f + (float)_rng.NextDouble() * 0.12f;
                Add(models, kinds[_rng.Next(kinds.Length)], centre, _rng.Next(4) * 90f, Mathf.Min(scale, 1.3f));
            }
            // A few trees and lamps along the pavements.
            for (var i = 0; i < 260 * _density; i++)
            {
                var p = RandomPoint();
                if (!Outside(p, 3f) || !InCity(p) || NearRiver(p, 2f)) continue;
                var ax = OnAvenue(p.x);
                var az = OnAvenue(p.y);
                if (ax == az) continue;
                // Snap onto the pavement at the edge of the avenue.
                var v = ax ? p.x : p.y;
                var lane = Mathf.Round((v - 18f) / BlockPitch) * BlockPitch + 18f;
                var kerb = lane + Mathf.Sign(v - lane) * (AvenueWidth * 0.5f - 1f);
                var at = ax ? new Vector2(kerb, p.y) : new Vector2(p.x, kerb);
                Add(models, _rng.Next(3) == 0 ? "lamp_post" : _theme.Trees[_rng.Next(_theme.Trees.Length)], at,
                    (float)_rng.NextDouble() * 360f, 0.85f + (float)_rng.NextDouble() * 0.3f);
            }
        }

        /// <summary>Theme scenery on the flat round the map: fumaroles and obsidian, bamboo and huts.</summary>
        private void ScatterScenery(ModelLibrary models, List<Rect> fields)
        {
            if (_theme.Scenery == null) return;
            for (var i = 0; i < 180 * _density; i++)
            {
                var p = RandomPoint();
                if (!Outside(p, 5f) || NearRiver(p, 3f) || InField(p, fields) || OnMountain(p)) continue;
                var model = _theme.Scenery[_rng.Next(_theme.Scenery.Length)];
                Add(models, model, p, _rng.Next(4) * 90f + (float)_rng.NextDouble() * 20f, 0.8f + (float)_rng.NextDouble() * 0.5f);
            }
        }

        /// <summary>
        /// The lava river beyond the north edge: a strip of 2 m cells whose vertex colours hold
        /// floating plates of cooling crust on the glowing flow, darkest at the banks.
        /// </summary>
        private Mesh LavaRiver()
        {
            const float cell = 2f;
            var nx = Mathf.CeilToInt(Extent * 2f / cell);
            var nz = Mathf.CeilToInt(RiverWidth / cell);
            var vertices = new List<Vector3>();
            var colours = new List<Color>();
            var normals = new List<Vector3>();
            var triangles = new List<int>();
            var crust = _theme.LavaCrust;
            for (var j = 0; j <= nz; j++)
            for (var i = 0; i <= nx; i++)
            {
                var x = i * cell - Extent;
                var z = j * cell - RiverWidth * 0.5f;
                // A wavy bank.
                var bank = Mathf.Abs(z) / (RiverWidth * 0.5f);
                z += Mathf.Sin(x * 0.07f) * 1.2f * (1f - bank * 0.3f);
                vertices.Add(new Vector3(x, 0f, z));
                normals.Add(Vector3.up);
                var n = Mathf.PerlinNoise(x * 0.09f + 4.2f, (z + RiverZ) * 0.2f + 1.3f);
                var heat = (1f - Edge(0.55f, 1f, bank)) * (1f - 0.75f * Edge(0.5f, 0.68f, n));
                colours.Add(Primitives.Linear(Color.Lerp(crust, Color.white, Mathf.Clamp01(heat + 0.1f))));
            }
            var stride = nx + 1;
            for (var j = 0; j < nz; j++)
            for (var i = 0; i < nx; i++)
            {
                var k = j * stride + i;
                triangles.Add(k); triangles.Add(k + stride); triangles.Add(k + 1);
                triangles.Add(k + 1); triangles.Add(k + stride); triangles.Add(k + stride + 1);
            }
            var mesh = new Mesh { name = "Lava River" };
            mesh.SetVertices(vertices);
            mesh.SetNormals(normals);
            mesh.SetColors(colours);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateBounds();
            return mesh;
        }

        private void PlaceFarmhouses(ModelLibrary models, List<Rect> fields)
        {
            foreach (var field in fields)
            {
                if (_rng.Next(3) == 0) continue;
                var corner = new Vector2(field.xMax + 7f, field.center.y);
                if (!Outside(corner, 8f) || NearRiver(corner, 8f)) continue;
                if (OnMountain(corner)) continue;
                var kinds = _theme.Farmhouses;
                var house = models.Spawn(kinds[_rng.Next(kinds.Length)], -1, _root.transform);
                house.Root.transform.SetPositionAndRotation(new Vector3(corner.x, 0f, corner.y), Quaternion.Euler(0f, _rng.Next(4) * 90f, 0f));
            }
        }

        /// <summary>A few rectangular crop fields in the countryside, clear of the map and river.</summary>
        private List<Rect> Fields()
        {
            var fields = new List<Rect>();
            for (var attempt = 0; attempt < 200 && fields.Count < 14; attempt++)
            {
                var size = new Vector2(24f + (float)_rng.NextDouble() * 30f, 18f + (float)_rng.NextDouble() * 22f);
                var centre = RandomPoint();
                var rect = new Rect(centre - size * 0.5f, size);
                if (!Outside(centre, Mathf.Max(size.x, size.y) * 0.5f + 10f) || NearRiver(centre, size.y * 0.5f + 6f)) continue;
                if (Height(rect.min) > 0.05f || Height(rect.max) > 0.05f || Height(new Vector2(rect.xMin, rect.yMax)) > 0.05f ||
                    Height(new Vector2(rect.xMax, rect.yMin)) > 0.05f) continue;
                var overlaps = false;
                foreach (var other in fields)
                    if (other.Overlaps(new Rect(rect.position - Vector2.one * 6f, rect.size + Vector2.one * 12f))) overlaps = true;
                if (!overlaps) fields.Add(rect);
            }
            return fields;
        }

        private Texture2D PaintOuter(MapTheme mapTheme, List<Rect> fields)
        {
            const int size = 512;
            var theme = mapTheme.Palette;
            var pixels = new Color[size * size];
            var worldPerPixel = Extent * 2f / size;
            var crops = mapTheme.Crops;
            var bank = mapTheme.Water switch
            {
                ThemeWater.Lava => new Color(0.2f, 0.1f, 0.07f),
                ThemeWater.Canal => theme.Stone,
                _ => Color.Lerp(theme.Dirt, theme.Sand, 0.5f),
            };
            for (var y = 0; y < size; y++)
            for (var x = 0; x < size; x++)
            {
                var p = new Vector2((x + 0.5f) * worldPerPixel - Extent, (y + 0.5f) * worldPerPixel - Extent);
                var n = Mathf.PerlinNoise(p.x * 0.03f + 3f, p.y * 0.03f + 1f);
                var colour = Color.Lerp(theme.Grass, n > 0.62f ? theme.Dirt : theme.Grass * 0.92f, Mathf.Abs(n - 0.5f) * 1.6f);
                for (var f = 0; f < fields.Count; f++)
                {
                    if (!fields[f].Contains(p)) continue;
                    var rows = Mathf.Repeat(p.x * 0.9f, 1f) < 0.5f ? 0.92f : 1.04f;
                    colour = crops[f % crops.Length] * rows;
                }
                // The city: asphalt avenues between concrete blocks, and grass on the hills beyond.
                if (InCity(p) && (OnAvenue(p.x) || OnAvenue(p.y))) colour = theme.Road;
                else if (mapTheme.Paved && !InCity(p)) colour = Color.Lerp(mapTheme.Lawn, colour, 0.3f);
                var riverDistance = HasRiver ? Mathf.Abs(p.y - RiverZ) - RiverWidth * 0.5f
                    : mapTheme.Water == ThemeWater.Sea ? SeaShore - p.y : 99f;
                if (riverDistance < 4f) colour = Color.Lerp(colour, bank, Mathf.Clamp01(1f - riverDistance / 4f));
                // Out of bounds reads a little darker and duller, which marks the playable edge.
                var edge = Mathf.Max(Mathf.Abs(p.x), Mathf.Abs(p.y)) - _half;
                var shade = Mathf.Lerp(0.9f, 0.74f, Mathf.Clamp01(edge / 40f));
                var grey = colour.grayscale;
                pixels[y * size + x] = Color.Lerp(colour, new Color(grey, grey, grey), 0.15f) * shade;
            }

            var texture = new Texture2D(size, size, TextureFormat.RGBA32, true, false)
            {
                name = "Outer Ground",
                wrapMode = TextureWrapMode.Clamp,
                filterMode = FilterMode.Trilinear,
            };
            texture.SetPixels(pixels);
            texture.Apply(true, true);
            return texture;
        }

        private Vector2 RandomPoint() =>
            new((float)(_rng.NextDouble() * 2 - 1) * Extent * 0.96f, (float)(_rng.NextDouble() * 2 - 1) * Extent * 0.96f);

        private void Add(ModelLibrary models, string modelId, Vector2 position, float yaw, float scale, float height = 0f)
        {
            var placement = Matrix4x4.TRS(new Vector3(position.x, height, position.y), Quaternion.Euler(0f, yaw, 0f), Vector3.one * scale);
            var cell = Mathf.FloorToInt((position.x + Extent) / CellSize) * 64 + Mathf.FloorToInt((position.y + Extent) / CellSize);
            var at = new Vector3(position.x, height, position.y);
            if (_cellBounds.TryGetValue(cell, out var cellBounds))
            {
                cellBounds.Encapsulate(at);
                _cellBounds[cell] = cellBounds;
            }
            else
            {
                _cellBounds[cell] = new Bounds(at, Vector3.zero);
            }
            foreach (var (mesh, local, materials) in models.Parts(modelId))
            for (var sub = 0; sub < mesh.subMeshCount && sub < materials.Length; sub++)
            {
                var key = (cell, mesh, sub, materials[sub]);
                if (!_instances.TryGetValue(key, out var list)) _instances[key] = list = new List<Matrix4x4>();
                list.Add(placement * local);
            }
        }

        private GameObject Place(string name, Mesh mesh, Material material)
        {
            var go = new GameObject(name);
            go.transform.SetParent(_root.transform, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = go.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = true;
            return go;
        }

        private Mesh Own(Mesh mesh)
        {
            _meshes.Add(mesh);
            return mesh;
        }

        /// <summary>Square plane on the ground with 0..1 UVs.</summary>
        private static Mesh Plane(float size, int cells)
        {
            var count = cells + 1;
            var vertices = new Vector3[count * count];
            var uvs = new Vector2[count * count];
            var colors = new Color[count * count];
            var normals = new Vector3[count * count];
            for (var z = 0; z < count; z++)
            for (var x = 0; x < count; x++)
            {
                var i = z * count + x;
                vertices[i] = new Vector3((x / (float)cells - 0.5f) * size, 0f, (z / (float)cells - 0.5f) * size);
                uvs[i] = new Vector2(x / (float)cells, z / (float)cells);
                colors[i] = Color.white;
                normals[i] = Vector3.up;
            }
            var triangles = new int[cells * cells * 6];
            var t = 0;
            for (var z = 0; z < cells; z++)
            for (var x = 0; x < cells; x++)
            {
                var i = z * count + x;
                triangles[t++] = i; triangles[t++] = i + count; triangles[t++] = i + 1;
                triangles[t++] = i + 1; triangles[t++] = i + count; triangles[t++] = i + count + 1;
            }
            var mesh = new Mesh { name = "Plane" };
            mesh.SetVertices(vertices);
            mesh.SetUVs(0, uvs);
            mesh.SetColors(colors);
            mesh.SetNormals(normals);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateBounds();
            return mesh;
        }
    }
}
