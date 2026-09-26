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

        public Surroundings(SimWorld world, ModelLibrary models, MaterialLibrary materials, TerrainTheme theme, Transform parent)
        {
            _half = world.Map.HalfSize;
            _root = new GameObject("Surroundings");
            _root.transform.SetParent(parent, false);

            var fields = Fields();
            _texture = PaintOuter(theme, fields);
            materials.OuterGround.SetTexture("_BaseMap", _texture);
            var ground = Place("Outer Ground", Own(Plane(Extent * 2f, 16)), materials.OuterGround);
            ground.transform.position = new Vector3(0f, -0.03f, 0f);
            // Ground beyond the decorated area, out to the fog, so no view ever ends in a void.
            var horizon = Place("Horizon Ground", Own(Plane(Extent * 6f, 4)), materials.Skirt);
            horizon.transform.position = new Vector3(0f, -0.3f, 0f);

            _palette = TerrainPalette(theme);
            _rangeMaterial = materials.Terrain;
            _rangeMaterial.SetTexture("_BaseMap", _palette);
            Place("Mountain Range", Own(MountainRange()), _rangeMaterial);

            var river = Place("River", Own(Plane(1f, 1)), materials.Water);
            river.transform.position = new Vector3(0f, -0.12f, RiverZ);
            river.transform.localScale = new Vector3(Extent * 2f, 1f, RiverWidth);

            ScatterForests(models, fields);
            ScatterRocks(models);
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
                    shadowCastingMode = edge < ShadowReach ? ShadowCastingMode.On : ShadowCastingMode.Off,
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
        private readonly Material _rangeMaterial;

        private float RiverZ => _half + 62f;
        private const float RiverWidth = 16f;

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
        }

        private bool Outside(Vector2 p, float margin) => Mathf.Abs(p.x) > _half + margin || Mathf.Abs(p.y) > _half + margin;

        private bool NearRiver(Vector2 p, float margin) => Mathf.Abs(p.y - RiverZ) < RiverWidth * 0.5f + margin;

        /// <summary>Rough terrain height at a ground point (0 on the flat around the map).</summary>
        private float Height(Vector2 p)
        {
            var outside = Mathf.Max(Mathf.Abs(p.x), Mathf.Abs(p.y)) - _half;
            if (outside < MountainStart) return 0f;
            var ramp = Mathf.SmoothStep(0f, 1f, (outside - MountainStart) / 70f);
            // Tall along the far (top of the screen) sides, rolling hills on the near ones, so
            // the range frames the battle without hiding it.
            var back = Mathf.Clamp01(0.5f + 0.65f * Vector2.Dot(p.normalized, new Vector2(-0.7071f, 0.7071f)));
            var n = Mathf.PerlinNoise(p.x * 0.011f + 13.7f, p.y * 0.011f + 4.1f);
            var ridge = 1f - Mathf.Abs(n * 2f - 1f);
            ridge *= ridge;
            var detail = Mathf.PerlinNoise(p.x * 0.045f + 2.3f, p.y * 0.045f + 7.9f);
            var peak = 5f + back * back * 52f;
            var height = ramp * (peak * (0.3f + 0.7f * ridge) + detail * 5f);
            // A valley for the river.
            var valley = Mathf.SmoothStep(0f, 1f, (Mathf.Abs(p.y - RiverZ) - RiverWidth * 0.5f - 3f) / 26f);
            return height * valley;
        }

        private const float MountainStart = 16f;
        private const float RangeCell = 5f;
        private const float TreeLine = 30f;
        private const float SnowLine = 40f;

        private static float Slope(Vector3 normal) => 1f - Mathf.Clamp01(normal.y);

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
        private static Texture2D TerrainPalette(TerrainTheme theme)
        {
            const int width = 64, height = 16;
            var pixels = new Color[width * height];
            var meadow = theme.Grass * 0.92f;
            var forest = Color.Lerp(theme.Grass, new Color(0.24f, 0.33f, 0.2f), 0.6f);
            var rock = Color.Lerp(theme.Stone, theme.Dirt, 0.35f);
            var cliff = theme.Stone * 0.8f;
            var snow = new Color(0.9f, 0.93f, 0.95f);
            for (var y = 0; y < height; y++)
            for (var x = 0; x < width; x++)
            {
                var h = x / (width - 1f);
                var steep = y / (height - 1f);
                var colour = Color.Lerp(meadow, forest, Mathf.SmoothStep(0.05f, 0.3f, h));
                colour = Color.Lerp(colour, rock, Mathf.SmoothStep(0.5f, 0.72f, h));
                colour = Color.Lerp(colour, cliff, Mathf.SmoothStep(0.45f, 0.8f, steep));
                // Snow settles on the gentler slopes of the peaks.
                colour = Color.Lerp(colour, snow, Mathf.SmoothStep(0.8f, 0.88f, h) * (1f - Mathf.SmoothStep(0.55f, 0.85f, steep)));
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
            for (var attempt = 0; attempt < 90000 && placed < 5200; attempt++)
            {
                var p = RandomPoint();
                if (!Outside(p, 4f) || NearRiver(p, 3f) || InField(p, fields)) continue;
                var height = Height(p);
                if (height > TreeLine) continue;
                var distance = Mathf.Max(Mathf.Abs(p.x), Mathf.Abs(p.y)) - _half;
                var noise = Mathf.PerlinNoise(p.x * 0.035f + 5f, p.y * 0.035f + 9f);
                // A thick tree line along the map edge, then whole forests on the lower slopes,
                // thinning out towards the tree line.
                var chance = distance < 26f
                    ? 0.3f + 0.7f * Mathf.SmoothStep(0.2f, 0.55f, noise)
                    : height > 1f
                        ? (0.55f + 0.45f * Mathf.SmoothStep(0.3f, 0.6f, noise)) * (1f - Mathf.SmoothStep(TreeLine * 0.6f, TreeLine, height))
                        : 0.12f + 0.8f * Mathf.SmoothStep(0.42f, 0.68f, noise);
                if (_rng.NextDouble() > chance) continue;
                // Conifers take over up the mountain; broadleaves and birches in the lowlands.
                var roll = _rng.NextDouble();
                var model = height > 8f
                    ? (roll < 0.75 ? "pine" : roll < 0.9 ? "tree" : "tree_dead")
                    : (roll < 0.35 ? "tree" : roll < 0.55 ? "pine" : roll < 0.75 ? "tree_round" : roll < 0.9 ? "tree_broad" : "birch");
                Add(models, model, p, (float)_rng.NextDouble() * 360f, 0.8f + (float)_rng.NextDouble() * 0.7f, height - 0.1f);
                placed++;
            }
            for (var i = 0; i < 700; i++)
            {
                var p = RandomPoint();
                if (!Outside(p, 3f) || NearRiver(p, 1f) || InField(p, fields) || OnMountain(p)) continue;
                Add(models, "bush", p, (float)_rng.NextDouble() * 360f, 0.7f + (float)_rng.NextDouble() * 0.9f);
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
                if (!Outside(p, 6f) || NearRiver(p, 2f)) continue;
                var height = Height(p);
                var model = "rock_" + (char)('a' + _rng.Next(3));
                Add(models, model, p, (float)_rng.NextDouble() * 360f, 1.2f + (float)_rng.NextDouble() * 2.4f + height * 0.05f, height - 0.4f);
            }
            // Crags on the heights, outcrops and boulder fields breaking up the forests below.
            for (var i = 0; i < 140; i++)
            {
                var p = RandomPoint();
                if (!Outside(p, 10f) || NearRiver(p, 6f)) continue;
                var height = Height(p);
                if (height < 2f && _rng.Next(3) != 0) continue;
                var model = _rng.Next(3) switch { 0 => "cliff_a", 1 => "cliff_b", _ => "boulders" };
                Add(models, model, p, (float)_rng.NextDouble() * 360f, 0.8f + (float)_rng.NextDouble() * 0.9f, height - 0.6f);
            }
        }

        private void PlaceFarmhouses(ModelLibrary models, List<Rect> fields)
        {
            foreach (var field in fields)
            {
                if (_rng.Next(3) == 0) continue;
                var corner = new Vector2(field.xMax + 7f, field.center.y);
                if (!Outside(corner, 8f) || NearRiver(corner, 8f)) continue;
                if (OnMountain(corner)) continue;
                var kinds = new[] { "house_large", "house_small", "cottage", "barn", "cottage" };
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

        private Texture2D PaintOuter(TerrainTheme theme, List<Rect> fields)
        {
            const int size = 512;
            var pixels = new Color[size * size];
            var worldPerPixel = Extent * 2f / size;
            var crops = new[] { new Color(0.62f, 0.6f, 0.36f), new Color(0.46f, 0.55f, 0.32f), new Color(0.66f, 0.55f, 0.36f) };
            var bank = Color.Lerp(theme.Dirt, theme.Sand, 0.5f);
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
                var riverDistance = Mathf.Abs(p.y - RiverZ) - RiverWidth * 0.5f;
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
