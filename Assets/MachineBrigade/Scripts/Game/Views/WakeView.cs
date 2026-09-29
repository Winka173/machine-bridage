using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Game.Views
{
    /// <summary>
    /// Ships' wakes (prompt 16 G): foam laid on the water behind every ship under way, spreading and fading
    /// out, and a bow wave either side at speed. Low graphics draws the short wake only (six patches, no bow
    /// waves); the rest draw twenty-two. One mesh per ship, rebuilt each frame from its sampled track. A ship
    /// that got away over the edge is hidden here too.
    /// </summary>
    public sealed class WakeView
    {
        private const float SampleEvery = 0.3f;

        private sealed class Trail
        {
            public readonly List<(Vector3 at, Vector3 across, float born, float width)> Patches = new();
            public float NextSample;
            public Mesh Mesh;
            public GameObject Object;
        }

        private readonly Dictionary<EntityId, Trail> _trails = new();
        private readonly List<EntityId> _gone = new();
        private readonly Transform _root;
        private readonly Material _material;
        private readonly int _patches;
        private readonly bool _bowWaves;
        private readonly List<Vector3> _vertices = new();
        private readonly List<Color32> _colours = new();
        private readonly List<Vector2> _uvs = new();
        private readonly List<int> _triangles = new();

        public WakeView(MaterialLibrary materials, Transform parent, bool low)
        {
            _root = new GameObject("Wakes").transform;
            _root.SetParent(parent, false);
            _material = materials.Foam;
            _patches = low ? 6 : 22;
            _bowWaves = !low;
        }

        public void Update(SimWorld world, ViewRegistry views)
        {
            var now = Time.time;
            foreach (var v in world.Vehicles)
            {
                if (!v.IsAlive || v.Def.Naval == null) continue;
                if (views.TryGet(v.Id, out var view) && view.Root.gameObject.activeSelf == v.Escaped) view.Root.gameObject.SetActive(!v.Escaped);
                if (v.Escaped) continue;
                if (!_trails.TryGetValue(v.Id, out var trail))
                {
                    trail = new Trail { Mesh = new Mesh { name = "Wake" } };
                    trail.Mesh.MarkDynamic();
                    trail.Object = new GameObject("Wake " + v.Def.Id, typeof(MeshFilter), typeof(MeshRenderer));
                    trail.Object.transform.SetParent(_root, false);
                    trail.Object.GetComponent<MeshFilter>().sharedMesh = trail.Mesh;
                    var renderer = trail.Object.GetComponent<MeshRenderer>();
                    renderer.sharedMaterial = _material;
                    renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                    renderer.receiveShadows = false;
                    _trails[v.Id] = trail;
                }
                var forward = new Vector3(Mathf.Sin(v.Heading), 0f, Mathf.Cos(v.Heading));
                var across = new Vector3(forward.z, 0f, -forward.x);
                var half = v.Def.Length > 0f ? v.Def.Length * 0.5f : v.Def.Radius;
                var beam = v.Def.Width > 0f ? v.Def.Width : v.Def.Radius;
                if (now >= trail.NextSample && v.Speed > 0.25f)
                {
                    trail.NextSample = now + SampleEvery;
                    var stern = new Vector3(v.Position.X, 0.07f, v.Position.Y) - forward * half * 0.9f;
                    trail.Patches.Add((stern, across, now, beam * Mathf.Clamp01(v.Speed / Mathf.Max(0.5f, v.Def.Speed))));
                    if (trail.Patches.Count > _patches) trail.Patches.RemoveAt(0);
                }
                Build(trail, v, forward, across, half, beam, now);
            }
            // Ships sunk or gone: their wakes go with them.
            _gone.Clear();
            foreach (var pair in _trails)
                if (!world.TryGetVehicle(pair.Key, out var ship) || !ship.IsAlive || ship.Escaped) _gone.Add(pair.Key);
            foreach (var id in _gone)
            {
                Object.Destroy(_trails[id].Object);
                Object.Destroy(_trails[id].Mesh);
                _trails.Remove(id);
            }
        }

        private void Build(Trail trail, Sim.Entities.Vehicle v, Vector3 forward, Vector3 across, float half, float beam, float now)
        {
            _vertices.Clear();
            _colours.Clear();
            _uvs.Clear();
            _triangles.Clear();
            var life = SampleEvery * _patches;
            foreach (var (at, side, born, width) in trail.Patches)
            {
                var age = Mathf.Clamp01((now - born) / life);
                // Spreads out behind the ship and fades.
                var w = width * (0.7f + 1.6f * age);
                var length = Mathf.Max(1.5f, width * 0.9f);
                var along = new Vector3(-side.z, 0f, side.x);
                Quad(at, side * w, along * length, (1f - age) * 0.75f);
            }
            if (_bowWaves && v.Speed > v.Def.Speed * 0.35f)
            {
                var strength = Mathf.Clamp01(v.Speed / Mathf.Max(0.5f, v.Def.Speed)) * 0.6f;
                var bow = new Vector3(v.Position.X, 0.07f, v.Position.Y) + forward * half * 0.8f;
                foreach (var s in new[] { -1f, 1f })
                {
                    var at = bow + across * (s * beam * 0.55f) - forward * half * 0.2f;
                    Quad(at, (across * s * 0.6f - forward * 0.8f).normalized * beam * 0.35f, forward * half * 0.45f, strength);
                }
            }
            var mesh = trail.Mesh;
            mesh.Clear();
            mesh.SetVertices(_vertices);
            mesh.SetColors(_colours);
            mesh.SetUVs(0, _uvs);
            mesh.SetTriangles(_triangles, 0);
            mesh.RecalculateBounds();
        }

        private void Quad(Vector3 centre, Vector3 halfAcross, Vector3 halfAlong, float alpha)
        {
            var i = _vertices.Count;
            _vertices.Add(centre - halfAcross - halfAlong);
            _vertices.Add(centre + halfAcross - halfAlong);
            _vertices.Add(centre + halfAcross + halfAlong);
            _vertices.Add(centre - halfAcross + halfAlong);
            var c = Primitives.Linear(new Color(0.92f, 0.96f, 1f, Mathf.Clamp01(alpha)));
            for (var k = 0; k < 4; k++) _colours.Add(c);
            _uvs.Add(new Vector2(0f, 0f));
            _uvs.Add(new Vector2(1f, 0f));
            _uvs.Add(new Vector2(1f, 1f));
            _uvs.Add(new Vector2(0f, 1f));
            _triangles.Add(i);
            _triangles.Add(i + 2);
            _triangles.Add(i + 1);
            _triangles.Add(i);
            _triangles.Add(i + 3);
            _triangles.Add(i + 2);
        }
    }
}
