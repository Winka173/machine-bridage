using System;
using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Entities;
using UnityEngine;
using UnityEngine.Rendering;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Object = UnityEngine.Object;
using Random = System.Random;
using Vector2 = System.Numerics.Vector2;
using Vector3 = UnityEngine.Vector3;

namespace MachineBrigade.Game.Views
{
    public sealed class PropView
    {
        public PropView(Prop prop, GameObject gameObject, string rubbleModel, IReadOnlyList<string> debris)
        {
            Prop = prop;
            GameObject = gameObject;
            RubbleModel = rubbleModel;
            Debris = debris;
        }

        public Prop Prop { get; }
        public GameObject GameObject { get; set; }
        public Transform Transform => GameObject.transform;

        /// <summary>Model left behind when destroyed, or null when the prop vanishes into its blast.</summary>
        public string RubbleModel { get; }

        /// <summary>Debris chunk models thrown when destroyed.</summary>
        public IReadOnlyList<string> Debris { get; }

        public bool IsBuilding => RubbleModel != null;
    }

    /// <summary>
    /// Ground, props and decoration. Destroyed buildings collapse into rubble; small props vanish
    /// into their blast. Decorative bushes are purely visual and never block movement.
    /// </summary>
    public sealed class MapView : IDisposable
    {
        private static readonly string[] BuildingDebris =
            { "debris_concrete", "debris_plaster", "debris_roof", "debris_concrete", "debris_plaster", "debris_roof", "debris_wood", "debris_concrete" };

        private readonly Dictionary<EntityId, PropView> _props = new();
        private readonly GameObject _root;
        private readonly SimWorld _world;
        private readonly ModelLibrary _models;

        public MapView(SimWorld world, ModelLibrary models, MaterialLibrary materials, Transform parent)
        {
            _world = world;
            _models = models;
            _root = new GameObject("Map");
            _root.transform.SetParent(parent, false);
            BuildGround(world.Map.Size, materials.Ground);

            var rng = new Random(17);
            foreach (var prop in world.Props)
            {
                var (model, rubble, debris) = Describe(prop.Def.Id, rng);
                var instance = models.Spawn(model, Teams.Neutral, _root.transform);
                var yaw = prop.Def.Id == "tree" ? (float)rng.NextDouble() * 360f : prop.Rotation;
                instance.Root.transform.SetPositionAndRotation(new Vector3(prop.Position.X, 0f, prop.Position.Y),
                    Quaternion.Euler(0f, yaw, 0f));
                if (prop.Def.Id == "tree") instance.Root.transform.localScale = Vector3.one * (0.85f + (float)rng.NextDouble() * 0.35f);
                _props.Add(prop.Id, new PropView(prop, instance.Root, rubble, debris));
            }
            ScatterBushes(world, rng);
        }

        /// <summary>Living prop under a ground point, preferring the smallest (a barrel beside a house).</summary>
        public Prop PropAt(Vector2 point)
        {
            Prop best = null;
            foreach (var prop in _world.Props)
            {
                if (!prop.IsAlive || !prop.Contains(point, 0.6f)) continue;
                if (best == null || prop.Width * prop.Depth < best.Width * best.Depth) best = prop;
            }
            return best;
        }

        /// <summary>Swaps a destroyed prop for its rubble (or hides it) and returns its view for debris.</summary>
        public bool TryDestroy(EntityId id, out PropView view)
        {
            if (!_props.TryGetValue(id, out view)) return false;
            var transform = view.Transform;
            if (view.RubbleModel != null)
            {
                var rubble = _models.Spawn(view.RubbleModel, Teams.Neutral, _root.transform);
                rubble.Root.transform.SetPositionAndRotation(transform.position, transform.rotation);
                view.GameObject.SetActive(false);
                view.GameObject = rubble.Root;
            }
            else
            {
                view.GameObject.SetActive(false);
            }
            return true;
        }

        public void Dispose()
        {
            if (_root != null) Object.Destroy(_root);
            _props.Clear();
        }

        private static (string model, string rubble, string[] debris) Describe(string defId, Random rng) => defId switch
        {
            "house_small" => ("house_small", "rubble_small", BuildingDebris),
            "house_large" => ("house_large", "rubble_large", BuildingDebris),
            "wall" => ("wall", null, new[] { "debris_concrete", "debris_concrete", "debris_concrete", "debris_concrete" }),
            "fuel_tank" => ("fuel_tank", null, new[] { "debris_metal", "debris_metal", "debris_metal", "debris_metal", "debris_metal" }),
            "barrel" => ("barrel", null, new[] { "debris_metal", "debris_metal" }),
            "ammo_crate" => ("ammo_crate", null, new[] { "debris_wood", "debris_wood", "debris_wood" }),
            "tree" => (rng.Next(3) == 0 ? "tree_broad" : "tree", null, new[] { "debris_leaves", "debris_leaves", "debris_leaves", "debris_wood" }),
            _ => (defId, null, Array.Empty<string>()),
        };

        /// <summary>Bushes in open ground, kept clear of props and both rally areas.</summary>
        private void ScatterBushes(SimWorld world, Random rng)
        {
            var half = world.Map.HalfSize - 4f;
            var placed = 0;
            for (var attempt = 0; attempt < 400 && placed < 70; attempt++)
            {
                var p = new Vector2((float)(rng.NextDouble() * 2 - 1) * half, (float)(rng.NextDouble() * 2 - 1) * half);
                var clear = true;
                foreach (var prop in world.Props)
                    if (prop.Contains(p, 3f)) { clear = false; break; }
                foreach (var team in world.Map.Teams)
                    if (Vector2.Distance(team.Rally, p) < 22f) clear = false;
                if (!clear) continue;
                var bush = _models.Spawn("bush", Teams.Neutral, _root.transform, castShadows: false);
                bush.Root.transform.SetPositionAndRotation(new Vector3(p.X, 0f, p.Y), Quaternion.Euler(0f, (float)rng.NextDouble() * 360f, 0f));
                bush.Root.transform.localScale = Vector3.one * (0.7f + (float)rng.NextDouble() * 0.6f);
                placed++;
            }
        }

        private void BuildGround(float size, Material material)
        {
            var ground = new GameObject("Ground");
            ground.transform.SetParent(_root.transform, false);
            ground.AddComponent<MeshFilter>().sharedMesh = GroundMesh(size, 64);
            var renderer = ground.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = true;
            var collider = ground.AddComponent<BoxCollider>();
            collider.center = new Vector3(0f, -0.5f, 0f);
            collider.size = new Vector3(size * 3f, 1f, size * 3f);

            var apron = new GameObject("Apron");
            apron.transform.SetParent(_root.transform, false);
            apron.transform.position = new Vector3(0f, -0.08f, 0f);
            apron.AddComponent<MeshFilter>().sharedMesh = GroundMesh(size * 5f, 10, darken: 0.55f);
            var apronRenderer = apron.AddComponent<MeshRenderer>();
            apronRenderer.sharedMaterial = material;
            apronRenderer.shadowCastingMode = ShadowCastingMode.Off;
        }

        /// <summary>
        /// Flat grid tinted like the reference's varied ground: dry grass, meadow and dirt patches
        /// from layered noise, with a subtle darkening towards the map edge.
        /// </summary>
        private static Mesh GroundMesh(float size, int cells, float darken = 1f)
        {
            var count = cells + 1;
            var vertices = new Vector3[count * count];
            var colors = new Color[count * count];
            var normals = new Vector3[count * count];
            var meadow = new Color(0.36f, 0.47f, 0.29f);
            var dryGrass = new Color(0.55f, 0.56f, 0.38f);
            var dirt = new Color(0.5f, 0.44f, 0.34f);
            for (var z = 0; z < count; z++)
            for (var x = 0; x < count; x++)
            {
                var i = z * count + x;
                var px = (x / (float)cells - 0.5f) * size;
                var pz = (z / (float)cells - 0.5f) * size;
                vertices[i] = new Vector3(px, 0f, pz);
                normals[i] = Vector3.up;
                var patches = Mathf.PerlinNoise(px * 0.022f + 17f, pz * 0.022f + 9f);
                var detail = Mathf.PerlinNoise(px * 0.13f + 3f, pz * 0.13f + 5f);
                var dirtMask = Mathf.SmoothStep(0.55f, 0.75f, Mathf.PerlinNoise(px * 0.035f + 41f, pz * 0.035f + 7f));
                var grass = Color.Lerp(dryGrass, meadow, Mathf.SmoothStep(0.35f, 0.65f, patches * 0.75f + detail * 0.25f));
                var colour = Color.Lerp(grass, dirt, dirtMask * 0.85f) * (0.93f + detail * 0.14f);
                var edge = Mathf.Max(Mathf.Abs(px), Mathf.Abs(pz)) / (size * 0.5f);
                colour *= Mathf.Lerp(1f, 0.82f, Mathf.SmoothStep(0.85f, 1f, edge));
                colors[i] = Primitives.Linear(colour * darken);
            }

            var triangles = new int[cells * cells * 6];
            var t = 0;
            for (var z = 0; z < cells; z++)
            for (var x = 0; x < cells; x++)
            {
                var i = z * count + x;
                // Wound so the face points up (+Y).
                triangles[t++] = i; triangles[t++] = i + count; triangles[t++] = i + 1;
                triangles[t++] = i + 1; triangles[t++] = i + count; triangles[t++] = i + count + 1;
            }

            var mesh = new Mesh { name = "Ground" };
            if (vertices.Length > 65535) mesh.indexFormat = IndexFormat.UInt32;
            mesh.SetVertices(vertices);
            mesh.SetColors(colors);
            mesh.SetNormals(normals);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateBounds();
            return mesh;
        }
    }
}
