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
    /// Countryside around the battlefield, so zooming out never shows an empty void: extended
    /// ground (slightly darker than the playable area, which marks the boundary), forest belts,
    /// boulders, farm fields with farmhouses and a river. It is decoration only: the simulation
    /// and the camera clamp stay inside the map. Trees, bushes and rocks are drawn with GPU
    /// instancing (one call per mesh part), so the whole ring costs a handful of draw calls and
    /// the imported meshes never need CPU read access.
    /// </summary>
    public sealed class Surroundings : IDisposable
    {
        private const float Extent = 230f; // half-size of the decorated area

        private readonly GameObject _root;
        private readonly List<Mesh> _meshes = new();
        private readonly Dictionary<(Mesh, int, Material), List<Matrix4x4>> _instances = new();
        private readonly List<(Mesh mesh, int submesh, Material material, Matrix4x4[] matrices)> _draws = new();
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

            var river = Place("River", Own(Plane(1f, 1)), materials.Water);
            river.transform.position = new Vector3(0f, -0.12f, RiverZ);
            river.transform.localScale = new Vector3(Extent * 2f, 1f, RiverWidth);

            ScatterForests(models, fields);
            ScatterRocks(models);
            PlaceFarmhouses(models, fields);
            var total = 0;
            foreach (var entry in _instances)
            {
                _draws.Add((entry.Key.Item1, entry.Key.Item2, entry.Key.Item3, entry.Value.ToArray()));
                total += entry.Value.Count;
            }
            _instances.Clear();
            Debug.Log($"[Surroundings] {_draws.Count} instanced batches, {total} instances, instancing supported: {SystemInfo.supportsInstancing}");
        }

        private float RiverZ => _half + 62f;
        private const float RiverWidth = 16f;

        /// <summary>Submits the instanced scenery; call once per frame.</summary>
        public void Draw()
        {
            foreach (var (mesh, submesh, material, matrices) in _draws)
            {
                // Explicit bounds: the default is tiny, so the whole batch was culled whenever the
                // map centre left the view.
                var parameters = new RenderParams(material)
                {
                    shadowCastingMode = ShadowCastingMode.On,
                    receiveShadows = true,
                    worldBounds = new Bounds(Vector3.zero, new Vector3(Extent * 2f, 60f, Extent * 2f)),
                };
                for (var start = 0; start < matrices.Length; start += 1023)
                    Graphics.RenderMeshInstanced(parameters, mesh, submesh, matrices, Mathf.Min(1023, matrices.Length - start), start);
            }
        }

        public void Dispose()
        {
            if (_root != null) Object.Destroy(_root);
            foreach (var mesh in _meshes)
                if (mesh != null) Object.Destroy(mesh);
            if (_texture != null) Object.Destroy(_texture);
        }

        private bool Outside(Vector2 p, float margin) => Mathf.Abs(p.x) > _half + margin || Mathf.Abs(p.y) > _half + margin;

        private bool NearRiver(Vector2 p, float margin) => Mathf.Abs(p.y - RiverZ) < RiverWidth * 0.5f + margin;

        /// <summary>
        /// A dense tree line hugging the battlefield edge (it frames the fight), then forest
        /// clusters further out with a minimum density so no side of the view is ever bare.
        /// Fields stay clear.
        /// </summary>
        private void ScatterForests(ModelLibrary models, List<Rect> fields)
        {
            var placed = 0;
            for (var attempt = 0; attempt < 40000 && placed < 2400; attempt++)
            {
                var p = RandomPoint();
                if (!Outside(p, 4f) || NearRiver(p, 3f) || InField(p, fields)) continue;
                var distance = Mathf.Max(Mathf.Abs(p.x), Mathf.Abs(p.y)) - _half;
                var noise = Mathf.PerlinNoise(p.x * 0.035f + 5f, p.y * 0.035f + 9f);
                var chance = distance < 26f
                    ? 0.2f + 0.75f * Mathf.SmoothStep(0.2f, 0.6f, noise)
                    : 0.12f + 0.8f * Mathf.SmoothStep(0.42f, 0.68f, noise);
                if (_rng.NextDouble() > chance) continue;
                var model = _rng.Next(4) == 0 ? "tree_broad" : "tree";
                Add(models, model, p, (float)_rng.NextDouble() * 360f, 0.8f + (float)_rng.NextDouble() * 0.7f);
                placed++;
            }
            for (var i = 0; i < 700; i++)
            {
                var p = RandomPoint();
                if (!Outside(p, 3f) || NearRiver(p, 1f) || InField(p, fields)) continue;
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
            for (var i = 0; i < 120; i++)
            {
                var p = RandomPoint();
                if (!Outside(p, 6f) || NearRiver(p, 2f)) continue;
                var model = "rock_" + (char)('a' + _rng.Next(3));
                Add(models, model, p, (float)_rng.NextDouble() * 360f, 1.2f + (float)_rng.NextDouble() * 2.4f);
            }
        }

        private void PlaceFarmhouses(ModelLibrary models, List<Rect> fields)
        {
            foreach (var field in fields)
            {
                if (_rng.Next(3) == 0) continue;
                var corner = new Vector2(field.xMax + 7f, field.center.y);
                if (!Outside(corner, 8f) || NearRiver(corner, 8f)) continue;
                var house = models.Spawn(_rng.Next(3) == 0 ? "house_large" : "house_small", -1, _root.transform);
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

        private void Add(ModelLibrary models, string modelId, Vector2 position, float yaw, float scale)
        {
            var placement = Matrix4x4.TRS(new Vector3(position.x, 0f, position.y), Quaternion.Euler(0f, yaw, 0f), Vector3.one * scale);
            foreach (var (mesh, local, materials) in models.Parts(modelId))
            for (var sub = 0; sub < mesh.subMeshCount && sub < materials.Length; sub++)
            {
                var key = (mesh, sub, materials[sub]);
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
