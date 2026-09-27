using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using UnityEngine;
using PB = MachineBrigade.Game.Effects.ParticleBuilder;

namespace MachineBrigade.Game.Effects
{
    /// <summary>
    /// Throws solid chunks into the <see cref="DebrisPool"/>: clods and rocks out of a crater,
    /// charred and glowing shards of wreckage, and, when a vehicle dies, pieces of its armour in
    /// its own colours plus road wheels. A share of every big blast's chunks burns, trailing
    /// fire and smoke and leaving small fires where they land. The chunk meshes are built here
    /// (jagged shards, lumpy clods, bent bars, wheels) next to the Blender debris models.
    /// </summary>
    internal sealed class ChunkThrower
    {
        /// <summary>What one blast throws: earth, wreckage, and burning pieces, at what speed and size.</summary>
        public readonly struct Recipe
        {
            public Recipe(int earth, int wreckage, int burning, Vector2 speed, float size, bool fuel = false)
            {
                Earth = earth;
                Wreckage = wreckage;
                Burning = burning;
                Speed = speed;
                Size = size;
                Fuel = fuel;
            }

            public int Earth { get; }
            public int Wreckage { get; }
            public int Burning { get; }
            public Vector2 Speed { get; }
            public float Size { get; }

            /// <summary>The burning pieces are gobs of fuel (napalm): bigger flames, bigger fires where they land.</summary>
            public bool Fuel { get; }
        }

        private readonly DebrisPool _pool;
        private readonly MaterialLibrary _materials;
        private readonly ChunkModel[] _earth;
        private readonly ChunkModel[] _wreckage;
        private readonly ChunkModel[] _burning;
        private readonly ChunkModel[] _hot;
        private readonly ChunkModel _gob;
        private readonly ChunkModel _wheel;
        private readonly Mesh[] _shards;
        private readonly Dictionary<int, ChunkModel[]> _armour = new();

        public ChunkThrower(DebrisPool pool, MaterialLibrary materials, ModelLibrary models, FireSpots fires, Transform parent)
        {
            _pool = pool;
            _materials = materials;
            Trails = new ChunkTrails(fires, parent);
            pool.Trails = Trails;

            _shards = new[] { ChunkMeshes.Shard(11), ChunkMeshes.Shard(23), ChunkMeshes.Shard(37) };
            var clods = new[] { ChunkMeshes.Clod(5), ChunkMeshes.Clod(17), ChunkMeshes.Clod(29) };
            var bar = ChunkMeshes.Bar(41);
            // Every distinct mesh and material pair is one instanced draw call, so the set is kept
            // small and pieces are varied by scale and tumble instead.
            _earth = new[] { Model(clods[0], "Dirt"), Model(clods[1], "Dirt"), Model(clods[2], "Rock"), Model(clods[1], "Charred") };
            var wreckage = new List<ChunkModel>
            {
                Model(_shards[0], "Charred"), Model(_shards[1], "Armor"), Model(_shards[2], "Charred"), Model(bar, "Steel"),
            };
            if (models != null && models.Has("debris_metal")) wreckage.Add(models.Chunk("debris_metal"));
            _wreckage = wreckage.ToArray();
            _burning = new[] { Model(_shards[0], "Charred"), Model(_shards[2], "Charred"), Model(clods[1], "Charred") };
            // Emissive: fragments still glowing from the heat of the blast.
            _hot = new[] { Model(_shards[2], "Alloy") };
            _gob = Model(clods[1], "Charred");
            _wheel = Model(ChunkMeshes.Wheel(), "Rubber");
        }

        public ChunkTrails Trails { get; }

        /// <summary>Throws a blast's chunks out of <paramref name="at"/>.</summary>
        public void Throw(in Recipe r, Vector3 at, float scale, float now)
        {
            var size = r.Size * Mathf.Sqrt(scale);
            var speed = r.Speed * Mathf.Sqrt(scale);
            var start = new Vector3(at.x, Mathf.Max(at.y, 0.25f), at.z);
            for (var i = 0; i < r.Earth; i++)
                Fly(_earth[Random.Range(0, _earth.Length)], start, size * 0.75f, speed, 0.25f, 0.9f, 0.9f, 1.5f, now, Random.Range(6f, 9f));
            for (var i = 0; i < r.Wreckage; i++)
            {
                var hot = Random.value < 0.25f;
                var model = hot ? _hot[Random.Range(0, _hot.Length)] : _wreckage[Random.Range(0, _wreckage.Length)];
                Fly(model, start, size * 0.6f, speed, 0.5f, 1.1f, 0.6f, 1.3f, now, hot ? Random.Range(3f, 5f) : Random.Range(9f, 14f));
            }
            for (var i = 0; i < r.Burning; i++)
            {
                var model = r.Fuel ? _gob : _burning[Random.Range(0, _burning.Length)];
                Fly(model, start, size * (r.Fuel ? 0.7f : 0.55f), speed * 1.1f, 0.3f, 0.8f, 1.2f, 1.8f, now, Random.Range(10f, 14f),
                    Random.Range(5f, 9f), r.Fuel);
            }
        }

        /// <summary>
        /// A vehicle torn apart by its death explosion: pieces of armour in its own colours,
        /// charred and glowing shards, bars and (for ground vehicles) road wheels, several burning.
        /// </summary>
        public void Wreck(Vector3 at, float radius, int team, bool wheels, float now)
        {
            var armour = Armour(team);
            var count = Mathf.Clamp(Mathf.RoundToInt(10f + radius * 6f), 12, 40);
            var burning = Mathf.RoundToInt(4f + radius * 1.5f);
            var speed = new Vector2(6f, 15f) * (0.8f + radius * 0.1f);
            var size = Mathf.Clamp(radius * 0.22f, 0.35f, 0.8f);
            var spread = radius * 0.5f;
            for (var i = 0; i < count; i++)
            {
                var from = at + new Vector3(Random.Range(-spread, spread), Random.Range(0.6f, 1.6f), Random.Range(-spread, spread));
                var roll = Random.value;
                var model = roll < 0.35f ? armour[Random.Range(0, armour.Length)]
                    : roll < 0.5f ? _hot[Random.Range(0, _hot.Length)]
                    : _wreckage[Random.Range(0, _wreckage.Length)];
                var life = roll is >= 0.35f and < 0.5f ? Random.Range(3f, 5f) : Random.Range(10f, 15f);
                Fly(model, from, size, speed, 0.5f, 1.1f, 0.7f, 1.5f, now, life, i < burning ? Random.Range(4f, 9f) : 0f);
            }
            if (!wheels) return;
            for (var i = 0; i < 2; i++)
            {
                var from = at + new Vector3(Random.Range(-spread, spread), 0.6f, Random.Range(-spread, spread));
                Fly(_wheel, from, Mathf.Clamp(radius * 0.4f, 0.8f, 1.3f), speed * 0.8f, 0.6f, 1f, 0.8f, 1.3f, now, Random.Range(12f, 16f));
            }
        }

        private void Fly(ChunkModel model, Vector3 from, float size, Vector2 speed, float outMin, float outMax, float upMin, float upMax,
            float now, float life, float burn = 0f, bool fuel = false)
        {
            var angle = Random.Range(0f, Mathf.PI * 2f);
            var outward = Random.Range(outMin, outMax);
            var direction = new Vector3(Mathf.Cos(angle) * outward, Random.Range(upMin, upMax), Mathf.Sin(angle) * outward).normalized;
            var s = size * Random.Range(0.6f, 1.4f);
            var scale = new Vector3(s * Random.Range(0.8f, 1.2f), s * Random.Range(0.8f, 1.2f), s * Random.Range(0.8f, 1.2f));
            _pool.Launch(model, from, Random.rotation, direction * Random.Range(speed.x, speed.y), scale, now, life, burn, fuel);
        }

        private ChunkModel[] Armour(int team)
        {
            if (_armour.TryGetValue(team, out var set)) return set;
            var paint = _materials.ForModel("Team", team);
            set = new[] { Model(_shards[0], paint), Model(_shards[1], paint) };
            _armour[team] = set;
            return set;
        }

        private ChunkModel Model(Mesh mesh, string surface) => Model(mesh, _materials.ForModel(surface, -1));

        private static ChunkModel Model(Mesh mesh, Material material) => new(mesh, new[] { material });
    }

    /// <summary>
    /// Fire and smoke streaming off burning chunks as they fly, a flare where they bounce, and a
    /// small fire where they come to rest. Two shared flipbook systems draw every trail.
    /// </summary>
    internal sealed class ChunkTrails
    {
        private const float FlameInterval = 1f / 16f;
        private const float SmokeInterval = 1f / 7f;

        private readonly ParticleSystem _flames;
        private readonly ParticleSystem _smoke;
        private readonly FireSpots _fires;

        public ChunkTrails(FireSpots fires, Transform parent)
        {
            _fires = fires;
            var fx = FxMaterials.Shared;
            var root = new GameObject("Chunk Trails").transform;
            root.SetParent(parent, false);

            _flames = Shared(root, "Chunk Flames", fx.Flames, 2500);
            PB.Flipbook(_flames, loop: true, tilt: 25f);
            PB.Colors(_flames, PB.Hold(new Color(0.3f, 0.26f, 0.22f), new Color(0.3f, 0.26f, 0.22f), 0.1f, 0.5f));
            PB.Grow(_flames, 1f, 0.45f);

            _smoke = Shared(root, "Chunk Smoke", fx.Smoke, 3000);
            PB.Flipbook(_smoke, loop: false, tilt: 30f, from: 0.1f);
            PB.Colors(_smoke, PB.Hold(new Color(0.14f, 0.13f, 0.12f), new Color(0.42f, 0.41f, 0.4f), 0.08f, 0.45f, 0.85f));
            PB.Grow(_smoke, 0.45f, 2.4f);
            PB.Rise(_smoke, 0.4f, 1.1f);
        }

        /// <summary>Only chunks that could be seen trail particles; the rest fly on unseen.</summary>
        public System.Func<Vector3, bool> Visible { get; set; }

        /// <summary>A burning chunk in flight: flames licking off it and a ribbon of smoke behind.</summary>
        public void Fly(ref float flameDebt, ref float smokeDebt, Vector3 at, bool fuel, float dt)
        {
            if (Visible != null && !Visible(at))
            {
                flameDebt = smokeDebt = 0f;
                return;
            }
            var size = fuel ? 1.5f : 1f;
            for (flameDebt += dt; flameDebt >= FlameInterval; flameDebt -= FlameInterval)
                Emit(_flames, at + Random.insideUnitSphere * 0.15f, Random.insideUnitSphere * 0.4f, Random.Range(1.1f, 1.6f) * size,
                    Random.Range(0.25f, 0.4f));
            for (smokeDebt += dt; smokeDebt >= SmokeInterval; smokeDebt -= SmokeInterval)
                Emit(_smoke, at, Random.insideUnitSphere * 0.3f, Random.Range(1.3f, 1.8f) * size, Random.Range(1.2f, 1.8f));
        }

        /// <summary>A burning chunk lying on the ground before its fire takes over: a slow wisp of smoke.</summary>
        public void Smoulder(ref float smokeDebt, Vector3 at, float dt)
        {
            if (Visible != null && !Visible(at)) return;
            for (smokeDebt += dt * 0.25f; smokeDebt >= SmokeInterval; smokeDebt -= SmokeInterval)
                Emit(_smoke, at, Vector3.up * 0.5f, Random.Range(0.6f, 0.9f), Random.Range(1.5f, 2.2f));
        }

        /// <summary>A burning chunk hitting the ground and bouncing on: a flare of flame.</summary>
        public void Impact(Vector3 at)
        {
            if (Visible != null && !Visible(at)) return;
            for (var i = 0; i < 3; i++)
                Emit(_flames, at + Random.insideUnitSphere * 0.3f, Random.insideUnitSphere + Vector3.up, Random.Range(1f, 1.6f),
                    Random.Range(0.3f, 0.5f));
        }

        /// <summary>A burning chunk at rest keeps burning where it lies.</summary>
        public void Land(Vector3 at, float seconds, bool fuel, float now)
        {
            Impact(at);
            if (seconds > 0.8f && _fires != null) _fires.Ignite(new Vector3(at.x, 0.05f, at.z), fuel ? 0.55f : 0.28f, seconds, now);
        }

        private static void Emit(ParticleSystem system, Vector3 position, Vector3 velocity, float size, float lifetime)
        {
            system.Emit(new ParticleSystem.EmitParams
            {
                position = position,
                velocity = velocity,
                startSize = size,
                startLifetime = lifetime,
                applyShapeToPosition = false,
            }, 1);
        }

        private static ParticleSystem Shared(Transform parent, string name, Material material, int max)
        {
            var ps = PB.Create(parent, name, material);
            var main = ps.main;
            main.loop = true;
            main.maxParticles = max;
            var emission = ps.emission;
            emission.enabled = false;
            ps.Play();
            return ps;
        }
    }

    /// <summary>
    /// Low-poly chunk meshes, flat shaded, with a little random shading per face in the vertex
    /// colours (the Lit shader reads them as ambient occlusion). All are centred on their origin
    /// so they tumble about it; sizes are about a third of a metre across before scaling.
    /// </summary>
    internal static class ChunkMeshes
    {
        /// <summary>A jagged plate of armour or sheet metal.</summary>
        public static Mesh Shard(int seed)
        {
            var soup = new Soup(seed);
            var r = new System.Random(seed);
            var n = 5 + r.Next(3);
            var angles = new float[n];
            for (var i = 0; i < n; i++) angles[i] = (i + (float)r.NextDouble() * 0.7f) / n * Mathf.PI * 2f;
            var top = new Vector3[n];
            var bottom = new Vector3[n];
            const float half = 0.028f;
            for (var i = 0; i < n; i++)
            {
                var radius = 0.35f * (0.5f + (float)r.NextDouble() * 0.5f);
                var x = Mathf.Cos(angles[i]) * radius;
                var z = Mathf.Sin(angles[i]) * radius * 0.75f;
                // A slight buckle, as if torn off.
                var bend = x * x * 0.8f;
                top[i] = new Vector3(x, half + bend, z);
                bottom[i] = new Vector3(x, -half + bend, z);
            }
            var centreTop = new Vector3(0f, half, 0f);
            var centreBottom = new Vector3(0f, -half, 0f);
            for (var i = 0; i < n; i++)
            {
                var j = (i + 1) % n;
                soup.Tri(centreTop, top[i], top[j], Vector3.up);
                soup.Tri(centreBottom, bottom[j], bottom[i], Vector3.down);
                var side = (top[i] + top[j]) * 0.5f;
                side.y = 0f;
                soup.Quad(top[i], bottom[i], bottom[j], top[j], side);
            }
            return soup.Build("Chunk Shard " + seed);
        }

        /// <summary>A lumpy clod of earth or a rock.</summary>
        public static Mesh Clod(int seed)
        {
            var soup = new Soup(seed);
            var r = new System.Random(seed);
            const float t = 1.618034f;
            var v = new[]
            {
                new Vector3(-1, t, 0), new Vector3(1, t, 0), new Vector3(-1, -t, 0), new Vector3(1, -t, 0),
                new Vector3(0, -1, t), new Vector3(0, 1, t), new Vector3(0, -1, -t), new Vector3(0, 1, -t),
                new Vector3(t, 0, -1), new Vector3(t, 0, 1), new Vector3(-t, 0, -1), new Vector3(-t, 0, 1),
            };
            for (var i = 0; i < v.Length; i++)
            {
                var jitter = 0.75f + (float)r.NextDouble() * 0.5f;
                v[i] = Vector3.Scale(v[i].normalized * (0.17f * jitter), new Vector3(1f, 0.72f, 0.9f));
            }
            int[] f =
            {
                0, 11, 5, 0, 5, 1, 0, 1, 7, 0, 7, 10, 0, 10, 11, 1, 5, 9, 5, 11, 4, 11, 10, 2, 10, 7, 6, 7, 1, 8,
                3, 9, 4, 3, 4, 2, 3, 2, 6, 3, 6, 8, 3, 8, 9, 4, 9, 5, 2, 4, 11, 6, 2, 10, 8, 6, 7, 9, 8, 1,
            };
            for (var i = 0; i < f.Length; i += 3)
            {
                var a = v[f[i]];
                var b = v[f[i + 1]];
                var c = v[f[i + 2]];
                soup.Tri(a, b, c, (a + b + c) / 3f);
            }
            return soup.Build("Chunk Clod " + seed);
        }

        /// <summary>A bent bar: a track pin, a gun barrel fragment, a strut.</summary>
        public static Mesh Bar(int seed)
        {
            var soup = new Soup(seed);
            Box(soup, new Vector3(-0.22f, 0f, 0f), new Vector3(0.24f, 0.035f, 0.035f), Quaternion.Euler(0f, 0f, 12f));
            Box(soup, new Vector3(0.2f, 0.04f, 0f), new Vector3(0.2f, 0.035f, 0.035f), Quaternion.Euler(0f, 0f, -18f));
            return soup.Build("Chunk Bar");
        }

        /// <summary>A road wheel blown off a running gear.</summary>
        public static Mesh Wheel()
        {
            var soup = new Soup(7);
            const int sides = 12;
            const float radius = 0.33f;
            const float half = 0.09f;
            for (var i = 0; i < sides; i++)
            {
                var a0 = i * Mathf.PI * 2f / sides;
                var a1 = (i + 1) * Mathf.PI * 2f / sides;
                var p0 = new Vector3(0f, Mathf.Cos(a0) * radius, Mathf.Sin(a0) * radius);
                var p1 = new Vector3(0f, Mathf.Cos(a1) * radius, Mathf.Sin(a1) * radius);
                var l = Vector3.left * half;
                var rgt = Vector3.right * half;
                soup.Quad(p0 + l, p1 + l, p1 + rgt, p0 + rgt, (p0 + p1) * 0.5f);
                soup.Tri(l * 1.4f, p0 + l, p1 + l, Vector3.left);
                soup.Tri(rgt * 1.4f, p1 + rgt, p0 + rgt, Vector3.right);
            }
            return soup.Build("Chunk Wheel");
        }

        private static void Box(Soup soup, Vector3 centre, Vector3 half, Quaternion rotation)
        {
            Vector3 P(float x, float y, float z) => centre + rotation * Vector3.Scale(half, new Vector3(x, y, z));
            var c = new[] { P(-1, -1, -1), P(1, -1, -1), P(1, 1, -1), P(-1, 1, -1), P(-1, -1, 1), P(1, -1, 1), P(1, 1, 1), P(-1, 1, 1) };
            int[][] faces = { new[] { 0, 1, 2, 3 }, new[] { 5, 4, 7, 6 }, new[] { 4, 0, 3, 7 }, new[] { 1, 5, 6, 2 }, new[] { 3, 2, 6, 7 }, new[] { 4, 5, 1, 0 } };
            foreach (var q in faces)
            {
                var mid = (c[q[0]] + c[q[1]] + c[q[2]] + c[q[3]]) * 0.25f;
                soup.Quad(c[q[0]], c[q[1]], c[q[2]], c[q[3]], mid - centre);
            }
        }

        /// <summary>Triangle soup: every triangle gets its own vertices, so faces shade flat.</summary>
        private sealed class Soup
        {
            private readonly List<Vector3> _vertices = new();
            private readonly List<Vector3> _normals = new();
            private readonly List<Color> _colours = new();
            private readonly System.Random _random;

            public Soup(int seed) => _random = new System.Random(seed * 7919 + 1);

            /// <summary>Adds a triangle whose front face points along <paramref name="outward"/> (a direction).</summary>
            public void Tri(Vector3 a, Vector3 b, Vector3 c, Vector3 outward)
            {
                var n = Vector3.Cross(b - a, c - a);
                if (Vector3.Dot(n, outward) < 0f)
                {
                    (b, c) = (c, b);
                    n = -n;
                }
                n.Normalize();
                var s = 0.78f + (float)_random.NextDouble() * 0.22f;
                var shade = Primitives.Linear(new Color(s, s, s, 1f));
                _vertices.Add(a);
                _vertices.Add(b);
                _vertices.Add(c);
                for (var i = 0; i < 3; i++)
                {
                    _normals.Add(n);
                    _colours.Add(shade);
                }
            }

            public void Quad(Vector3 a, Vector3 b, Vector3 c, Vector3 d, Vector3 outward)
            {
                Tri(a, b, c, outward);
                Tri(a, c, d, outward);
            }

            public Mesh Build(string name)
            {
                var mesh = new Mesh { name = name };
                mesh.SetVertices(_vertices);
                mesh.SetNormals(_normals);
                mesh.SetColors(_colours);
                var uvs = new List<Vector2>(_vertices.Count);
                for (var i = 0; i < _vertices.Count; i++) uvs.Add(Vector2.zero);
                mesh.SetUVs(0, uvs);
                var triangles = new int[_vertices.Count];
                for (var i = 0; i < triangles.Length; i++) triangles[i] = i;
                mesh.SetTriangles(triangles, 0);
                mesh.RecalculateBounds();
                return mesh;
            }
        }
    }
}
