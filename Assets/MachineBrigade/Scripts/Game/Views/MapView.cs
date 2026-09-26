using System;
using System.Collections.Generic;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Voxel;
using UnityEngine;
using UnityEngine.Rendering;
using Object = UnityEngine.Object;
using Vector2 = System.Numerics.Vector2;
using Vector3 = UnityEngine.Vector3;

namespace MachineBrigade.Game.Views
{
    public sealed class PropView
    {
        public PropView(Prop prop, PropMeshes meshes, GameObject gameObject)
        {
            Prop = prop;
            Meshes = meshes;
            GameObject = gameObject;
        }

        public Prop Prop { get; }
        public PropMeshes Meshes { get; }
        public GameObject GameObject { get; }
        public Transform Transform => GameObject.transform;
    }

    /// <summary>Ground and props. Destroyed buildings turn into rubble; small props vanish into their blast.</summary>
    public sealed class MapView : IDisposable
    {
        private readonly Dictionary<EntityId, PropView> _props = new();
        private readonly GameObject _root;
        private readonly SimWorld _world;

        public MapView(SimWorld world, MeshLibrary meshes, MaterialLibrary materials, Transform parent)
        {
            _world = world;
            _root = new GameObject("Map");
            _root.transform.SetParent(parent, false);
            BuildGround(world.Map.Size, materials.Ground);

            foreach (var prop in world.Props)
            {
                var propMeshes = meshes.Prop(prop.Def.Id);
                var go = new GameObject($"{prop.Def.Id} {prop.Id}");
                go.transform.SetParent(_root.transform, false);
                go.transform.SetPositionAndRotation(new Vector3(prop.Position.X, 0f, prop.Position.Y),
                    Quaternion.Euler(0f, prop.Rotation, 0f));
                go.AddComponent<MeshFilter>().sharedMesh = propMeshes.Intact;
                var renderer = go.AddComponent<MeshRenderer>();
                renderer.sharedMaterial = materials.Voxel;
                renderer.shadowCastingMode = ShadowCastingMode.On;
                _props.Add(prop.Id, new PropView(prop, propMeshes, go));
            }
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

        /// <summary>Swaps a destroyed prop to rubble or hides it, returning its view for debris.</summary>
        public bool TryDestroy(EntityId id, out PropView view)
        {
            if (!_props.TryGetValue(id, out view)) return false;
            if (view.Meshes.Rubble != null) view.GameObject.GetComponent<MeshFilter>().sharedMesh = view.Meshes.Rubble;
            else view.GameObject.SetActive(false);
            return true;
        }

        public void Dispose()
        {
            if (_root != null) Object.Destroy(_root);
            _props.Clear();
        }

        private void BuildGround(float size, Material material)
        {
            var ground = new GameObject("Ground");
            ground.transform.SetParent(_root.transform, false);
            ground.AddComponent<MeshFilter>().sharedMesh = GroundMesh(size, 48);
            var renderer = ground.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = true;
            var collider = ground.AddComponent<BoxCollider>();
            collider.center = new Vector3(0f, -0.5f, 0f);
            collider.size = new Vector3(size * 3f, 1f, size * 3f);

            var apron = new GameObject("Apron");
            apron.transform.SetParent(_root.transform, false);
            apron.transform.position = new Vector3(0f, -0.05f, 0f);
            apron.AddComponent<MeshFilter>().sharedMesh = GroundMesh(size * 4f, 8, darken: 0.8f);
            var apronRenderer = apron.AddComponent<MeshRenderer>();
            apronRenderer.sharedMaterial = material;
            apronRenderer.shadowCastingMode = ShadowCastingMode.Off;
        }

        /// <summary>Flat grid tinted with two octaves of noise so the dirt does not look like a table top.</summary>
        private static Mesh GroundMesh(float size, int cells, float darken = 1f)
        {
            var count = cells + 1;
            var vertices = new Vector3[count * count];
            var colors = new Color[count * count];
            var normals = new Vector3[count * count];
            var soil = new Color(0.46f, 0.43f, 0.33f);
            var grass = new Color(0.37f, 0.43f, 0.26f);
            for (var z = 0; z < count; z++)
            for (var x = 0; x < count; x++)
            {
                var i = z * count + x;
                var px = (x / (float)cells - 0.5f) * size;
                var pz = (z / (float)cells - 0.5f) * size;
                vertices[i] = new Vector3(px, 0f, pz);
                normals[i] = Vector3.up;
                var n = Mathf.PerlinNoise(px * 0.025f + 17f, pz * 0.025f + 9f) * 0.7f
                        + Mathf.PerlinNoise(px * 0.11f, pz * 0.11f) * 0.3f;
                colors[i] = VoxelMesher.ToShader(Color.Lerp(soil, grass, Mathf.SmoothStep(0.3f, 0.7f, n)) * darken);
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
            mesh.SetVertices(vertices);
            mesh.SetColors(colors);
            mesh.SetNormals(normals);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateBounds();
            return mesh;
        }
    }
}
