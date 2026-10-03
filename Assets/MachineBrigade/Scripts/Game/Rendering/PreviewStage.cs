using System;
using System.Collections.Generic;
using MachineBrigade.Game.Views;
using UnityEngine;

namespace MachineBrigade.Game.Rendering
{
    /// <summary>
    /// Prompt 34 L8 (DECISIONS "Prompt 34 L8 / L9"): the ground a preview stands its unit on, built for its setting
    /// (<see cref="PreviewSettings"/>): the biome's ground, a wavy sea with a shore, a stretch of track, a base slot's pad,
    /// the ground far below an aircraft. Prompt 33's biome, sea and rail pieces are not merged yet, so these are the
    /// temporary scenes of the right kind (flat water with waves, a short track, a pad), made from procedural meshes with
    /// their colours in the vertices. Two plain materials of its own (the shared ground material carries the lobby map's
    /// painted texture) and no MaterialPropertyBlock. View only; the range's Sim knows nothing of it.
    /// </summary>
    public sealed class PreviewStage : IDisposable
    {
        public const string GroundName = "Stage Ground", WaterName = "Stage Water", RailName = "Stage Rails",
            SleeperName = "Stage Sleepers", PadName = "Stage Pad", ShoreName = "Stage Shore";

        /// <summary>The water's level and the waves' height in metres (the map's rivers lie at 0.04 m; ships ride at 0).</summary>
        public const float SeaLevel = 0.04f, WaveHeight = 0.14f;

        private readonly Transform _root;
        private readonly List<Mesh> _meshes = new();
        private readonly List<Material> _materials = new();
        private readonly List<(Mesh mesh, Vector3[] rest, Vector3[] moved, Vector3[] normals)> _waves = new();
        private readonly MapTheme _theme;

        public PreviewSetting Setting { get; }

        /// <summary>How far the stage reaches from its centre (for the camera's far plane).</summary>
        public float Radius { get; private set; }

        public Transform Root => _root;

        private PreviewStage(Transform parent, PreviewSetting setting, string biome)
        {
            Setting = setting;
            _theme = MapTheme.For(biome);
            _root = new GameObject("Preview Stage").transform;
            _root.SetParent(parent, false);
        }

        // ----------------------------------------------------------------------------------------------- the range

        /// <summary>
        /// "In action": a 260 m square round the range. The shooter stands at z = <paramref name="startZ"/> facing +z, its
        /// targets round z = <paramref name="farZ"/>. <paramref name="length"/> and <paramref name="width"/> are the shooter's.
        /// </summary>
        public static PreviewStage ForRange(MaterialLibrary materials, Transform parent, PreviewSetting setting, string biome,
            float startZ, float farZ, float length, float width)
        {
            var s = new PreviewStage(parent, setting, biome);
            const float half = 130f;
            s.Radius = half * 1.42f;
            var ground = s.PlainMaterial(materials);
            switch (setting)
            {
                case PreviewSetting.Sea:
                {
                    var shore = ShoreForSea(startZ, farZ, length);
                    s.Land(ground, -half, half, shore, half, 5f);
                    s.Water(materials, -half, half, -half, shore + 3f, 4f);
                    s.Shore(ground, -half, half, shore);
                    break;
                }
                case PreviewSetting.WaterEdge:
                    s.Land(ground, -half, half, startZ, half, 5f);
                    s.Water(materials, -half, half, -half, startZ + 3f, 4f);
                    s.Shore(ground, -half, half, startZ);
                    break;
                case PreviewSetting.Coast:
                {
                    var shore = startZ + (farZ - startZ) * 0.4f;
                    s.Land(ground, -half, half, -half, shore, 5f);
                    s.Water(materials, -half, half, shore - 3f, half, 4f);
                    s.Shore(ground, -half, half, shore);
                    s.Pad(ground, new Vector3(0f, 0f, startZ), Mathf.Max(length, width) * 1.3f + 2f);
                    break;
                }
                default:
                    s.Land(ground, -half, half, -half, half, 5f);
                    break;
            }
            if (setting == PreviewSetting.Rail)
                s.Track(materials, ground, -half, Mathf.Min(startZ + length * 0.5f + 10f, farZ - 8f), RailGauge(width));
            if (setting == PreviewSetting.BasePad)
                s.Pad(ground, new Vector3(0f, 0f, startZ), Mathf.Max(length, width) * 1.3f + 2f);
            return s;
        }

        /// <summary>Where the sea's shore runs on the range: <see cref="PreviewSettings.ShoreGap"/> before the targets, else just past the bow.</summary>
        public static float ShoreForSea(float startZ, float farZ, float length) =>
            Mathf.Max(farZ - PreviewSettings.ShoreGap, Mathf.Min(startZ + length * 0.5f + 2f, farZ - 4f));

        /// <summary>The track's gauge for a train of this width (prompt 33's real track will set its own).</summary>
        public static float RailGauge(float width) => Mathf.Clamp(width * 0.62f, 1.4f, 5f);

        // ----------------------------------------------------------------------------------------------- the turntable

        /// <summary>
        /// The detail page's turntable: a disc of the setting under the model, turning with it. <paramref name="extents"/> are
        /// the model's half sizes (its foot at y = 0), <paramref name="waterline"/> how high over its foot the model's own
        /// origin sits (a ship's waterline), <paramref name="lift"/> how far below an aircraft the ground lies.
        /// </summary>
        public static PreviewStage ForTurntable(MaterialLibrary materials, Transform parent, PreviewSetting setting, string biome,
            Vector3 extents, float waterline, float lift)
        {
            var s = new PreviewStage(parent, setting, biome);
            var size = Mathf.Max(extents.x, extents.z);
            var radius = size * 1.45f + 3f;
            var ground = s.PlainMaterial(materials);
            switch (setting)
            {
                case PreviewSetting.Air:
                    radius = size * 2.2f + lift * 1.4f + 4f;
                    s.Disc(ground, radius, -lift, float.NegativeInfinity, false);
                    break;
                case PreviewSetting.Sea:
                    s.Disc(s.WaterMaterial(materials), radius, Mathf.Max(0.02f, waterline), float.NegativeInfinity, true);
                    break;
                case PreviewSetting.WaterEdge:
                case PreviewSetting.Coast:
                    // The rear half over the water, the front on the shore.
                    s.Disc(s.WaterMaterial(materials), radius, -0.12f, float.NegativeInfinity, true);
                    s.Disc(ground, radius, -0.02f, setting == PreviewSetting.Coast ? -size * 0.6f : 0f, false);
                    if (setting == PreviewSetting.Coast) s.Pad(ground, Vector3.zero, size * 2.5f + 1f);
                    break;
                default:
                    s.Disc(ground, radius, -0.02f, float.NegativeInfinity, false);
                    break;
            }
            if (setting == PreviewSetting.Rail)
            {
                // The track runs along the model's long side.
                s.Track(materials, ground, -radius * 0.98f, radius * 0.98f, RailGauge(Mathf.Min(extents.x, extents.z) * 2f));
                if (extents.x > extents.z) s._root.localRotation = Quaternion.Euler(0f, 90f, 0f);
            }
            if (setting == PreviewSetting.BasePad) s.Pad(ground, Vector3.zero, size * 2.5f + 1f);
            s.Radius = radius;
            return s;
        }

        // ----------------------------------------------------------------------------------------------- per frame

        /// <summary>Moves the waves (a few crossing swells; the normals follow them).</summary>
        public void Tick(float time)
        {
            foreach (var (mesh, rest, moved, normals) in _waves)
            {
                if (mesh == null) continue;
                for (var i = 0; i < rest.Length; i++)
                {
                    var p = rest[i];
                    var (h, dx, dz) = Wave(p.x, p.z, time);
                    moved[i] = new Vector3(p.x, p.y + h, p.z);
                    normals[i] = new Vector3(-dx, 1f, -dz).normalized;
                }
                mesh.vertices = moved;
                mesh.normals = normals;
            }
        }

        /// <summary>The swell at a point: its height and slopes (three sines crossing, about 9-30 m long).</summary>
        public static (float h, float dx, float dz) Wave(float x, float z, float t)
        {
            float a1 = 0.21f * x + 0.05f * z + 1.1f * t, a2 = 0.07f * x - 0.17f * z + 0.8f * t + 1.7f, a3 = 0.45f * (x + z) + 1.9f * t;
            var h = WaveHeight * (Mathf.Sin(a1) + 0.7f * Mathf.Sin(a2) + 0.25f * Mathf.Sin(a3)) / 1.95f;
            var dx = WaveHeight * (0.21f * Mathf.Cos(a1) + 0.7f * 0.07f * Mathf.Cos(a2) + 0.25f * 0.45f * Mathf.Cos(a3)) / 1.95f;
            var dz = WaveHeight * (0.05f * Mathf.Cos(a1) - 0.7f * 0.17f * Mathf.Cos(a2) + 0.25f * 0.45f * Mathf.Cos(a3)) / 1.95f;
            return (h, dx, dz);
        }

        public void Dispose()
        {
            if (_root != null) Gone(_root.gameObject);
            foreach (var m in _meshes)
                if (m != null) Gone(m);
            foreach (var m in _materials)
                if (m != null) Gone(m);
            _meshes.Clear();
            _materials.Clear();
            _waves.Clear();
        }

        /// <summary>Destroyed at the frame's end in play, at once in the editor (the edit-mode tests).</summary>
        private static void Gone(UnityEngine.Object o)
        {
            if (Application.isPlaying) UnityEngine.Object.Destroy(o);
            else UnityEngine.Object.DestroyImmediate(o);
        }

        // ----------------------------------------------------------------------------------------------- pieces

        /// <summary>A plain white matte copy of the fallback surface: the vertices carry the colours.</summary>
        private Material PlainMaterial(MaterialLibrary materials)
        {
            var m = new Material(materials.Fallback) { name = "Preview Ground" };
            m.SetColor("_BaseColor", Color.white);
            m.SetFloat("_Metallic", 0f);
            m.SetFloat("_Roughness", 0.95f);
            m.SetColor("_EmissionColor", Color.black);
            _materials.Add(m);
            return m;
        }

        /// <summary>
        /// The biome's water (play-test 13: the water shader): the deep colour offshore, the shallow one at the shore; the
        /// vertices carry the depth (r), the open water (g) and a fade into the backdrop (b), as MapView's water.
        /// </summary>
        private Material WaterMaterial(MaterialLibrary materials)
        {
            var m = new Material(materials.Water) { name = "Preview Water" };
            m.SetColor("_BaseColor", _theme.WaterColour);
            m.SetColor("_ShallowColor", MaterialLibrary.ShallowOf(_theme.WaterColour, _theme.Palette.Sand));
            m.SetFloat("_Roughness", Mathf.Min(_theme.WaterRoughness, 0.2f));
            _materials.Add(m);
            return m;
        }

        /// <summary>The biome's ground colour at a point: grass with patches of dirt and sand, speckled.</summary>
        private Color GroundColour(float x, float z)
        {
            var p = _theme.Palette;
            var n = Mathf.PerlinNoise(x * 0.045f + 11.3f, z * 0.045f + 4.1f);
            var m = Mathf.PerlinNoise(x * 0.11f + 2.7f, z * 0.11f + 9.6f);
            var c = Color.Lerp(p.Grass, p.Dirt, Edge(0.45f, 0.75f, n));
            c = Color.Lerp(c, p.Sand, Edge(0.62f, 0.85f, m) * 0.6f);
            var speck = Mathf.PerlinNoise(x * 0.9f + 0.5f, z * 0.9f + 0.5f);
            return c * (0.92f + speck * 0.14f);
        }

        private void Land(Material material, float x0, float x1, float z0, float z1, float cell)
        {
            if (z1 - z0 < 0.5f) return;
            var mesh = GridMesh(GroundName, x0, x1, z0, z1, cell, -0.02f, (x, z) => GroundColour(x, z));
            Place(GroundName, mesh, material);
        }

        private void Water(MaterialLibrary materials, float x0, float x1, float z0, float z1, float cell)
        {
            // Play-test 13: r = depth (deep 30 m from the shore), g = open water (foam in the first 4 m), b = 1.
            var mesh = GridMesh(WaterName, x0, x1, z0, z1, cell, SeaLevel, (x, z) =>
            {
                var metres = Mathf.Min(Mathf.Abs(z - z1), Mathf.Abs(z - z0));
                // GridMesh linearises its colours; these are data, so they go in pre-gamma'd to arrive as written.
                var data = new Color(Mathf.Clamp01(metres / 30f), Mathf.Clamp01(metres / 4f), 1f, 1f);
                return QualitySettings.activeColorSpace == ColorSpace.Linear ? data.gamma : data;
            });
            mesh.MarkDynamic();
            Place(WaterName, mesh, WaterMaterial(materials));
            AddWaves(mesh);
        }

        /// <summary>A strip of wet sand along the waterline (z = <paramref name="z"/>).</summary>
        private void Shore(Material material, float x0, float x1, float z)
        {
            var sand = Color.Lerp(_theme.Palette.Sand, _theme.Palette.Dirt, 0.35f) * 0.85f;
            var mesh = GridMesh(ShoreName, x0, x1, z - 1.2f, z + 1.6f, 4f, 0f, (_, __) => sand);
            Place(ShoreName, mesh, material);
        }

        /// <summary>A disc of ground or water, its rim darkened into the menu's backdrop; cut straight at z = <paramref name="cutBelow"/>.</summary>
        private void Disc(Material material, float radius, float y, float cutBelow, bool waves)
        {
            const int rings = 10, segments = 48;
            var verts = new List<Vector3> { new(0f, y, Mathf.Max(0f, cutBelow)) };
            for (var r = 1; r <= rings; r++)
                for (var k = 0; k < segments; k++)
                {
                    var a = k * Mathf.PI * 2f / segments;
                    var rr = radius * r / rings;
                    verts.Add(new Vector3(Mathf.Cos(a) * rr, y, Mathf.Max(cutBelow, Mathf.Sin(a) * rr)));
                }
            var tris = new List<int>();
            for (var k = 0; k < segments; k++)
            {
                var k1 = (k + 1) % segments;
                tris.AddRange(new[] { 0, 1 + k1, 1 + k });
                for (var r = 1; r < rings; r++)
                {
                    int a = 1 + (r - 1) * segments + k, b = 1 + (r - 1) * segments + k1, c = 1 + r * segments + k, d = 1 + r * segments + k1;
                    tris.AddRange(new[] { a, b, d, a, d, c });
                }
            }
            var colours = new Color[verts.Count];
            for (var i = 0; i < verts.Count; i++)
            {
                var v = verts[i];
                var rim = Mathf.Pow(Mathf.Clamp01(new Vector2(v.x, v.z).magnitude / radius), 3f);
                // Play-test 13: water vertices carry deep open water and the rim's fade in b (the water shader's inputs).
                colours[i] = waves ? new Color(1f, 1f, Mathf.Lerp(1f, 0.5f, rim), 1f) : Primitives.Linear(GroundColour(v.x, v.z) * Mathf.Lerp(1f, 0.5f, rim));
            }
            var name = waves ? WaterName : GroundName;
            var mesh = new Mesh { name = name };
            mesh.SetVertices(verts);
            mesh.SetColors(colours);
            mesh.SetNormals(Fill(verts.Count, Vector3.up));
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateBounds();
            _meshes.Add(mesh);
            if (waves) mesh.MarkDynamic();
            Place(name, mesh, material);
            if (waves) AddWaves(mesh);
        }

        /// <summary>A base slot: a concrete pad over a dark rim, a hazard mark at each corner.</summary>
        private void Pad(Material material, Vector3 at, float size)
        {
            var b = new BoxBuilder();
            var concrete = Primitives.Linear(new Color(0.58f, 0.57f, 0.53f));
            var rim = Primitives.Linear(new Color(0.24f, 0.24f, 0.23f));
            var hazard = Primitives.Linear(new Color(0.89f, 0.71f, 0.29f));
            b.Add(at + new Vector3(0f, -0.2f, 0f), new Vector3(size + 0.8f, 0.36f, size + 0.8f), rim);
            b.Add(at + new Vector3(0f, -0.12f, 0f), new Vector3(size, 0.26f, size), concrete);
            var c = size * 0.5f - 0.5f;
            for (var i = 0; i < 4; i++)
            {
                var sx = i % 2 == 0 ? -1f : 1f;
                var sz = i < 2 ? -1f : 1f;
                b.Add(at + new Vector3(sx * c, 0.015f, sz * (c - 0.3f)), new Vector3(0.35f, 0.02f, 1.0f), hazard);
                b.Add(at + new Vector3(sx * (c - 0.3f), 0.015f, sz * c), new Vector3(1.0f, 0.02f, 0.35f), hazard);
            }
            Place(PadName, Own(b.Build(PadName)), material);
        }

        /// <summary>A stretch of track along z: ballast, sleepers, two rails and a buffer stop at the far end.</summary>
        private void Track(MaterialLibrary materials, Material ground, float z0, float z1, float gauge)
        {
            if (z1 - z0 < 2f) return;
            var bed = new BoxBuilder();
            var stone = Primitives.Linear(Color.Lerp(_theme.Palette.Stone, new Color(0.45f, 0.44f, 0.42f), 0.5f));
            var wood = Primitives.Linear(new Color(0.33f, 0.24f, 0.17f));
            var hazard = Primitives.Linear(new Color(0.89f, 0.71f, 0.29f));
            var length = z1 - z0;
            var mid = (z0 + z1) * 0.5f;
            bed.Add(new Vector3(0f, -0.06f, mid), new Vector3(gauge * 2.1f, 0.16f, length), stone);
            var step = Mathf.Clamp(gauge * 0.45f, 0.6f, 1.6f);
            for (var z = z0 + step * 0.5f; z < z1; z += step)
                bed.Add(new Vector3(0f, 0.06f, z), new Vector3(gauge * 1.55f, 0.09f, step * 0.38f), wood);
            bed.Add(new Vector3(0f, 0.4f, z1 - 0.3f), new Vector3(gauge * 1.3f, 0.7f, 0.5f), hazard);
            Place(SleeperName, Own(bed.Build(SleeperName)), ground);
            var rails = new BoxBuilder();
            var steel = Primitives.Linear(Color.white);
            var rail = Mathf.Clamp(gauge * 0.06f, 0.08f, 0.22f);
            for (var side = -1; side <= 1; side += 2)
                rails.Add(new Vector3(side * gauge * 0.5f, 0.1f + rail * 0.5f, mid), new Vector3(rail, rail, length), steel);
            Place(RailName, Own(rails.Build(RailName)), materials.ForModel("Steel", 0));
        }

        private Mesh GridMesh(string name, float x0, float x1, float z0, float z1, float cell, float y, Func<float, float, Color> colour)
        {
            var nx = Mathf.Max(1, Mathf.CeilToInt((x1 - x0) / cell));
            var nz = Mathf.Max(1, Mathf.CeilToInt((z1 - z0) / cell));
            var verts = new Vector3[(nx + 1) * (nz + 1)];
            var colours = new Color[verts.Length];
            for (var j = 0; j <= nz; j++)
                for (var i = 0; i <= nx; i++)
                {
                    var x = Mathf.Lerp(x0, x1, (float)i / nx);
                    var z = Mathf.Lerp(z0, z1, (float)j / nz);
                    verts[j * (nx + 1) + i] = new Vector3(x, y, z);
                    colours[j * (nx + 1) + i] = Primitives.Linear(colour(x, z));
                }
            var tris = new int[nx * nz * 6];
            var t = 0;
            for (var j = 0; j < nz; j++)
                for (var i = 0; i < nx; i++)
                {
                    int a = j * (nx + 1) + i, b = a + 1, c = a + nx + 1, d = c + 1;
                    tris[t++] = a; tris[t++] = c; tris[t++] = b;
                    tris[t++] = b; tris[t++] = c; tris[t++] = d;
                }
            var mesh = new Mesh { name = name, indexFormat = verts.Length > 65000 ? UnityEngine.Rendering.IndexFormat.UInt32 : UnityEngine.Rendering.IndexFormat.UInt16 };
            mesh.vertices = verts;
            mesh.colors = colours;
            mesh.normals = Fill(verts.Length, Vector3.up).ToArray();
            mesh.triangles = tris;
            mesh.RecalculateBounds();
            _meshes.Add(mesh);
            return mesh;
        }

        private void AddWaves(Mesh mesh)
        {
            var rest = mesh.vertices;
            // The bounds take in the highest swell, so the water is never culled on a crest.
            var b = mesh.bounds;
            b.Expand(new Vector3(0f, WaveHeight * 2.5f, 0f));
            mesh.bounds = b;
            _waves.Add((mesh, rest, (Vector3[])rest.Clone(), mesh.normals));
            Tick(0f);
        }

        private Mesh Own(Mesh mesh)
        {
            _meshes.Add(mesh);
            return mesh;
        }

        private void Place(string name, Mesh mesh, Material material) => VehicleView.CreateMesh(name, _root, mesh, material, false);

        /// <summary>0 below <paramref name="a"/>, 1 above <paramref name="b"/>, smooth between (GLSL's smoothstep).</summary>
        private static float Edge(float a, float b, float x)
        {
            var t = Mathf.Clamp01((x - a) / (b - a));
            return t * t * (3f - 2f * t);
        }

        private static List<Vector3> Fill(int n, Vector3 v)
        {
            var list = new List<Vector3>(n);
            for (var i = 0; i < n; i++) list.Add(v);
            return list;
        }

        /// <summary>Axis-aligned boxes in one mesh, each with its colour in its vertices.</summary>
        private sealed class BoxBuilder
        {
            private readonly List<Vector3> _v = new(), _n = new();
            private readonly List<Color> _c = new();
            private readonly List<int> _t = new();

            private static readonly Vector3[] Normals = { Vector3.up, Vector3.down, Vector3.right, Vector3.left, Vector3.forward, Vector3.back };

            public void Add(Vector3 centre, Vector3 size, Color colour)
            {
                var h = size * 0.5f;
                foreach (var n in Normals)
                {
                    // Two axes across the face (w = n x u, the same handedness on every face); the triangles below
                    // run the corners clockwise seen from outside (Unity's front face).
                    var u = Mathf.Abs(n.y) > 0.5f ? Vector3.right : Vector3.up;
                    var w = Vector3.Cross(n, u);
                    var start = _v.Count;
                    var f = Vector3.Scale(n, h);
                    var du = Vector3.Scale(u, h);
                    var dw = Vector3.Scale(w, h);
                    _v.Add(centre + f - du - dw);
                    _v.Add(centre + f - du + dw);
                    _v.Add(centre + f + du + dw);
                    _v.Add(centre + f + du - dw);
                    for (var i = 0; i < 4; i++)
                    {
                        _n.Add(n);
                        _c.Add(colour);
                    }
                    _t.AddRange(new[] { start, start + 2, start + 1, start, start + 3, start + 2 });
                }
            }

            public Mesh Build(string name)
            {
                var mesh = new Mesh { name = name, indexFormat = _v.Count > 65000 ? UnityEngine.Rendering.IndexFormat.UInt32 : UnityEngine.Rendering.IndexFormat.UInt16 };
                mesh.SetVertices(_v);
                mesh.SetNormals(_n);
                mesh.SetColors(_c);
                mesh.SetTriangles(_t, 0);
                mesh.RecalculateBounds();
                return mesh;
            }
        }
    }
}
