using NUnit.Framework;
using MachineBrigade.Game.Rendering;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>Checks the Blender models against the runtime contract in ModelLibrary.</summary>
    public class ModelTests
    {
        private static readonly string[] Vehicles = { "scout_jeep", "light_tank", "main_battle_tank", "artillery" };

        private static readonly string[] Props =
        {
            "house_small", "house_large", "wall", "fuel_tank", "barrel", "ammo_crate", "tree", "tree_broad", "bush",
            "rubble_small", "rubble_large", "debris_concrete", "debris_plaster", "debris_roof", "debris_wood",
            "debris_metal", "debris_leaves",
        };

        [Test]
        public void EveryModelLoadsWithMeshes()
        {
            foreach (var id in Vehicles)
                Assert.IsNotNull(Load(id).GetComponentInChildren<MeshFilter>(), id);
            foreach (var id in Props)
                Assert.IsNotNull(Load(id).GetComponentInChildren<MeshFilter>(), id);
        }

        /// <summary>Blender's -Y front must arrive as Unity +Z, or vehicles would drive backwards.</summary>
        [Test]
        public void VehiclesHaveATurretAndABarrelPointingForward()
        {
            foreach (var id in Vehicles)
            {
                var root = Load(id).transform;
                var turret = Find(root, "Turret");
                Assert.IsNotNull(turret, $"{id} needs a Turret pivot");
                var barrel = FindPrefix(turret, "Main_cannon");
                Assert.IsNotNull(barrel, $"{id} needs a Main_cannon under its Turret");
                // Measured from the turret pivot: the jeep's gun mount sits behind the hull centre.
                var mesh = barrel.GetComponentInChildren<MeshFilter>().sharedMesh;
                var tip = turret.InverseTransformPoint(barrel.TransformPoint(mesh.bounds.center));
                Assert.Greater(tip.z, 0.2f, $"{id}'s barrel points backwards (z = {tip.z})");
            }
        }

        [Test]
        public void GeneratedBoxFacesPointOutward()
        {
            var mesh = Primitives.Box();
            try
            {
                var vertices = mesh.vertices;
                var triangles = mesh.triangles;
                for (var t = 0; t < triangles.Length; t += 3)
                {
                    Vector3 a = vertices[triangles[t]], b = vertices[triangles[t + 1]], c = vertices[triangles[t + 2]];
                    Assert.Greater(Vector3.Dot(Vector3.Cross(b - a, c - a), (a + b + c) / 3f), 0f);
                }
            }
            finally
            {
                Object.DestroyImmediate(mesh);
            }
        }

        private static GameObject Load(string id)
        {
            var prefab = Resources.Load<GameObject>("Models/" + id);
            Assert.IsNotNull(prefab, $"Resources/Models/{id}.glb did not import as a model");
            return prefab;
        }

        private static Transform Find(Transform root, string name)
        {
            if (root.name == name) return root;
            foreach (Transform child in root)
            {
                var found = Find(child, name);
                if (found != null) return found;
            }
            return null;
        }

        private static Transform FindPrefix(Transform root, string prefix)
        {
            foreach (Transform child in root)
                if (child.name.StartsWith(prefix)) return child;
            return null;
        }
    }
}
