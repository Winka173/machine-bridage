using NUnit.Framework;
using MachineBrigade.Game.Rendering;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>Checks the Blender models against the runtime contract in ModelLibrary.</summary>
    public class ModelTests
    {
        private static readonly string[] Vehicles =
        {
            "scout_jeep", "light_tank", "main_battle_tank", "artillery", "apc", "mlrs", "aa_vehicle", "flame_tank",
        };

        private static readonly string[] Others =
        {
            "attack_helicopter", "strike_jet", "missile", "rocket", "bomb", "cruise_missile", "mountain_a", "mountain_b",
            "mountain_c", "cliff_a", "cliff_b", "boulders", "sandbags", "tank_trap", "dirt_mound",
        };

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
            foreach (var id in Others)
                Assert.IsNotNull(Load(id).GetComponentInChildren<MeshFilter>(), id);
        }

        /// <summary>Every weapon mount in the balance data has a muzzle on its model (V: ModelLibrary contract).</summary>
        [Test]
        public void EveryWeaponMountHasAMuzzleOnItsModel()
        {
            var catalog = MachineBrigade.Game.Match.GameContent.LoadCatalog();
            foreach (var def in catalog.Vehicles.Values)
            {
                var root = Load(def.Id).transform;
                foreach (var mount in def.Mounts)
                    Assert.IsNotNull(Find(root, "Muzzle_" + mount.Slot), $"{def.Id} has no Muzzle_{mount.Slot} for {mount.Weapon.Id}");
            }
        }

        [Test]
        public void HelicopterRotorsAreSeparatePivots()
        {
            var root = Load("attack_helicopter").transform;
            Assert.IsNotNull(Find(root, "Rotor"));
            Assert.IsNotNull(Find(root, "Tail_rotor"));
            Assert.IsNotNull(Find(root, "Mount_gun"));
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
                // Measured from the turret pivot: the jeep's gun mount sits behind the hull centre.
                var muzzle = Find(turret, "Muzzle_main");
                Assert.IsNotNull(muzzle, $"{id} needs a Muzzle_main under its Turret");
                var tip = turret.InverseTransformPoint(muzzle.position);
                Assert.Greater(tip.z, 0.2f, $"{id}'s weapon points backwards (z = {tip.z})");
                // Guns recoil; launchers (the rocket pod) have no barrel.
                if (id == "mlrs") continue;
                Assert.IsNotNull(FindPrefix(turret, "Main_cannon"), $"{id} needs a Main_cannon under its Turret");
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

        /// <summary>Spawned models keep every animated part but merge the rest into a few renderers.</summary>
        [Test]
        public void SpawnedModelsMergeRigidPartsButKeepMovingOnes()
        {
            var materials = new MaterialLibrary();
            var models = new ModelLibrary(materials);
            var parent = new GameObject("Spawn Test").transform;
            try
            {
                var tank = models.Spawn("main_battle_tank", 0, parent);
                var raw = Load("main_battle_tank").GetComponentsInChildren<MeshRenderer>(true).Length;
                Assert.Less(tank.Renderers.Length, raw / 2, "far fewer renderers than the imported model");
                Assert.IsNotNull(tank.Turret, "turret pivot kept");
                Assert.IsNotEmpty(tank.RecoilParts, "barrel still recoils");
                Assert.IsTrue(tank.Muzzles.ContainsKey("mg") && tank.Mounts.ContainsKey("mg"), "roof gun mount and muzzle kept");
                Assert.IsNotNull(tank.Turret.GetComponentInChildren<MeshRenderer>(), "the turret carries its own merged mesh");

                var heli = models.Spawn("attack_helicopter", 1, parent);
                Assert.AreEqual(2, heli.Spinners.Count, "both rotors still spin");
                foreach (var spinner in heli.Spinners)
                    Assert.IsNotNull(spinner.Transform.GetComponentInChildren<MeshRenderer>(), $"{spinner.Transform.name} has its blades");
            }
            finally
            {
                Object.DestroyImmediate(parent.gameObject);
                models.Dispose();
                materials.Dispose();
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
