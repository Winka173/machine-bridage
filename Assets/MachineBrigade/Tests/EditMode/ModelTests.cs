using System.Linq;
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
            "armored_car", "tank_destroyer", "heavy_tank", "sam_launcher", "mortar_carrier", "rocket_technical",
            "ifv", "howitzer", "thermobaric_launcher", "heavy_aa", "titan_tank",
            "twin_tank", "siege_tank", "heavy_rocket_artillery", "ballistic_launcher", "siege_mortar",
        };

        private static readonly string[] Others =
        {
            "attack_helicopter", "strike_jet", "missile", "rocket", "bomb", "cruise_missile", "mountain_a", "mountain_b",
            "mountain_c", "cliff_a", "cliff_b", "boulders", "sandbags", "tank_trap", "dirt_mound",
            "scout_heli", "attack_jet", "strike_drone", "heavy_bomber", "stealth_bomber", "sky_gunship",
            "behemoth", "mobile_fortress", "armored_train", "mega_gunship",
            "elite_mbt", "elite_heavy_tank", "elite_tank_destroyer", "elite_attack_helicopter", "elite_mlrs", "elite_aa", "elite_apc",
            "ballistic_missile", "heavy_rocket", "mine", "fpv_drone", "supply_crate", "repair_crate",
            "engineer_vehicle", "ew_jammer", "fpv_carrier", "mine_layer",
            "fighter_jet", "tank_buster", "recon_drone", "heavy_attack_heli", "drone_mothership", "nuke_train", "icbm",
            "gun_turret", "aa_turret", "rocket_turret", "mg_bunker", "guard_tower",
            "command_hq", "base_wall", "base_gate", "floodlight_mast", "fuel_depot", "ammo_dump", "vehicle_hangar", "helipad",
            "razor_wire", "sandbag_wall",
            "basalt_rock_a", "basalt_rock_b", "basalt_rock_c", "obsidian_spire", "lava_vent", "charred_tree", "volcanic_cliff",
            "jungle_tree_a", "jungle_tree_b", "jungle_tree_c", "bamboo_clump", "fern_bush", "temple_ruin", "stilt_hut",
            "hangar", "control_tower", "parked_jet", "fuel_truck", "radar_dome", "revetment", "runway_light",
            "highrise_a", "highrise_b", "skyscraper", "parking_garage", "billboard", "bus", "traffic_light",
        };

        /// <summary>Vehicles added with the artillery pass (real-world equipment).</summary>
        private static readonly string[] Added = { "grad_truck", "atgm_carrier", "aps_tank", "heavy_turret", "flak_tower", "missile_battery" };

        private static readonly string[] Props =
        {
            "house_small", "house_large", "wall", "fuel_tank", "barrel", "ammo_crate", "tree", "tree_broad", "bush",
            "rubble_small", "rubble_large", "debris_concrete", "debris_plaster", "debris_roof", "debris_wood",
            "debris_metal", "debris_leaves",
            "cottage", "townhouse", "apartment", "shop", "church", "barn", "silo", "warehouse", "garage", "water_tower", "ruin",
            "fence", "stone_wall", "hedge", "car", "truck", "rubble_medium", "pine", "birch", "tree_dead", "tree_round",
            // Desert, snow and harbour maps.
            "adobe_house", "adobe_large", "market_stall", "palm", "cactus", "oil_pump", "refinery_tower", "storage_tank", "pipeline",
            "mesa", "snow_pine", "log_cabin", "snow_rock", "radar_station", "watchtower", "container", "container_stack",
            "gantry_crane", "factory", "rail_tanker", "rail_boxcar", "dock_bollards", "office_block", "lamp_post", "jersey_barrier",
            // Map kit.
            "wreck_tank", "wreck_truck", "wreck_car", "artillery_wreck", "trench_straight", "trench_corner", "foxhole", "crater_large",
            "tank_ditch", "command_tent", "camo_net", "supply_pile", "fuel_bladder", "checkpoint", "barricade", "power_pylon",
            "telegraph_pole", "radio_mast", "bridge_road", "ruin_house", "ruin_tower", "dead_tree",
            // Siege fortress.
            "shield_generator",
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
            foreach (var id in Added)
                Assert.IsNotNull(Load(id).GetComponentInChildren<MeshFilter>(), id);
        }

        /// <summary>Every weapon mount in the balance data has a muzzle on its model (V: ModelLibrary contract).</summary>
        [Test]
        public void EveryWeaponMountHasAMuzzleOnItsModel()
        {
            var catalog = MachineBrigade.Game.Match.GameContent.LoadCatalog();
            foreach (var def in catalog.Vehicles.Values)
            {
                // Units that borrow another model (the convoy truck), and bosses whose art is
                // still to come, are checked when their own model lands.
                if (def.Model != def.Id || Resources.Load<GameObject>("Models/" + def.Model) == null) continue;
                var root = Load(def.Id).transform;
                // A structure with nothing to fire (an obstacle, a module) needs no muzzle.
                // A melee weapon strikes with the hull's front instead: the bulldozer's Blade, the borer's drill.
                foreach (var mount in def.Mounts)
                    if (mount.Weapon.Melee)
                        Assert.IsNotNull(Find(root, "Blade") ?? Find(root, "Part_drill"), $"{def.Id} has no Blade or drill for {mount.Weapon.Id}");
                    else if (mount.Weapon.Damage > 0f)
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
            // The tandem boss gunship spins both of its rotors.
            var gunship = Load("mega_gunship").transform;
            Assert.IsNotNull(Find(gunship, "Rotor"));
            Assert.IsNotNull(Find(gunship, "Rotor_rear"));
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
                if (id is "mlrs" or "sam_launcher" or "mortar_carrier" or "rocket_technical" or "thermobaric_launcher" or "heavy_rocket_artillery"
                    or "ballistic_launcher" or "siege_mortar") continue;
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

        /// <summary>
        /// Every turreted vehicle's barrel sits on an elevating pivot at its trunnion, so shells
        /// that fly high leave from a raised barrel: raising the pivot lifts the muzzle and keeps
        /// it attached. Artillery, mortars, rocket boxes and anti-aircraft guns must have one.
        /// </summary>
        /// <summary>
        /// Rounds leave from the launchers on both sides (pods, rails, twin guns), found from the
        /// model's meshes, not from one muzzle on the centre line.
        /// </summary>
        [TestCase("attack_helicopter", "rocket", 2, 0.45f)]
        [TestCase("heavy_aa", "missile", 4, 1f)]
        [TestCase("titan_tank", "missile", 2, 1.5f)]
        [TestCase("attack_helicopter", "missile", 2, 0.8f)]
        [TestCase("scout_heli", "gun", 2, 0.8f)]
        [TestCase("heavy_attack_heli", "rocket", 2, 1.5f)]
        [TestCase("fighter_jet", "missile", 4, 1f)]
        [TestCase("attack_jet", "missile", 2, 1.5f)]
        [TestCase("tank_buster", "rocket", 2, 3f)]
        public void RoundsLeaveFromTheLaunchersOnBothSides(string id, string slot, int count, float offCentre)
        {
            var materials = new MaterialLibrary();
            var models = new ModelLibrary(materials);
            var parent = new GameObject("Launcher Test").transform;
            try
            {
                var model = models.Spawn(id, 0, parent);
                Assert.IsTrue(model.Launchers.TryGetValue(slot, out var launchers), $"{id} {slot}: launch points");
                Assert.AreEqual(count, launchers.Count, $"{id} {slot}: one per launcher");
                var root = model.Root.transform;
                var xs = launchers.Select(l => root.InverseTransformPoint(l.transform.position).x).OrderBy(x => x).ToList();
                Assert.Less(xs[0], -offCentre, $"{id} {slot}: a launcher on the left");
                Assert.Greater(xs[xs.Count - 1], offCentre, $"{id} {slot}: and on the right");
                Assert.AreEqual(-xs[0], xs[xs.Count - 1], 0.25f, $"{id} {slot}: mirrored");
                model.Muzzles.TryGetValue(slot, out var muzzle);
                foreach (var l in launchers)
                    Assert.Less(Mathf.Abs(root.InverseTransformPoint(l.transform.position).y - root.InverseTransformPoint(muzzle.position).y), 1.2f,
                        $"{id} {slot}: at the launcher's height");
            }
            finally
            {
                Object.DestroyImmediate(parent.gameObject);
                models.Dispose();
                materials.Dispose();
            }
        }

        /// <summary>A box of tubes fires each round from a different spot on its face.</summary>
        [TestCase("mlrs", "main")]
        [TestCase("grad_truck", "main")]
        [TestCase("elite_mlrs", "main")]
        [TestCase("sam_launcher", "main")]
        [TestCase("rocket_turret", "main")]
        [TestCase("thermobaric_launcher", "rocket")]
        public void ABoxOfTubesFiresFromAcrossItsFace(string id, string slot)
        {
            var materials = new MaterialLibrary();
            var models = new ModelLibrary(materials);
            var parent = new GameObject("Launcher Test").transform;
            try
            {
                var model = models.Spawn(id, 0, parent);
                Assert.IsTrue(model.Launchers.TryGetValue(slot, out var launchers), $"{id} {slot}: a launch face");
                Assert.AreEqual(1, launchers.Count, $"{id} {slot}: one face");
                Assert.Greater(launchers[0].Spread.x, 0.3f, $"{id} {slot}: rounds leave from across the face");
                Assert.Less(Mathf.Abs(model.Root.transform.InverseTransformPoint(launchers[0].transform.position).x), 0.3f, $"{id} {slot}: centred on the launcher");
            }
            finally
            {
                Object.DestroyImmediate(parent.gameObject);
                models.Dispose();
                materials.Dispose();
            }
        }

        [Test]
        public void BarrelsRiseOnTheirTrunnion()
        {
            var materials = new MaterialLibrary();
            var models = new ModelLibrary(materials);
            var parent = new GameObject("Elevation Test").transform;
            var report = new System.Text.StringBuilder();
            try
            {
                foreach (var id in Vehicles)
                {
                    var model = models.Spawn(id, 0, parent);
                    if (model.Elevation == null)
                    {
                        report.Append($"{id}: none; ");
                        continue;
                    }
                    Assert.IsTrue(model.Muzzles.TryGetValue("main", out var muzzle), $"{id}: Muzzle_main");
                    Assert.IsTrue(muzzle.IsChildOf(model.Elevation), $"{id}: the muzzle rides on the elevating pivot");
                    var before = muzzle.position;
                    model.Elevation.localRotation = Quaternion.Euler(-30f, 0f, 0f);
                    var lift = muzzle.position.y - before.y;
                    Assert.Greater(lift, 0.1f, $"{id}: raising the barrel lifts the muzzle");
                    Assert.Less(Vector3.Distance(model.Elevation.position, muzzle.position), 12f, $"{id}: the pivot is on the vehicle");
                    report.Append($"{id}: {model.Barrel} rest {model.RestPitch:0}deg lift {lift:0.00}; ");
                }
                Debug.Log("ELEVATION " + report);
                foreach (var id in new[] { "howitzer", "artillery", "siege_tank", "siege_mortar", "mortar_carrier", "mlrs", "sam_launcher",
                             "heavy_aa", "aa_vehicle", "thermobaric_launcher", "heavy_rocket_artillery", "main_battle_tank" })
                    Assert.IsNotNull(models.Spawn(id, 0, parent).Elevation, $"{id} raises its barrel");
            }
            finally
            {
                Object.DestroyImmediate(parent.gameObject);
                models.Dispose();
                materials.Dispose();
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

        /// <summary>Play-test 5 (DECISIONS 20W): the siege tank's sieging parts move on their own; the mortar elevates, the 105 mm slides.</summary>
        [Test]
        public void SiegeTankKeepsItsSiegePartsApart()
        {
            var materials = new MaterialLibrary();
            var models = new ModelLibrary(materials);
            var parent = new GameObject("Siege Test").transform;
            try
            {
                var tank = models.Spawn("siege_tank", 0, parent);
                var root = tank.Root.transform;
                foreach (var name in new[] { "Deploy_brace_l", "Deploy_brace_r", "Deploy_spade_l", "Deploy_spade_r", "Deploy_gun", "Deploy_riser" })
                {
                    var part = Find(root, name);
                    Assert.IsNotNull(part, name);
                    Assert.IsNotNull(part.GetComponentInChildren<MeshRenderer>(true), $"{name} keeps its own mesh");
                }
                Assert.IsTrue(tank.Turret.IsChildOf(Find(root, "Deploy_riser")), "the turret rides its column");
                Assert.IsNotNull(tank.Elevation, "the mortar elevates");
                Assert.IsTrue(tank.Muzzles["main"].IsChildOf(tank.Elevation), "the mortar's muzzle rides on it");
                Assert.IsTrue(tank.Muzzles["gun"].IsChildOf(Find(root, "Deploy_gun")), "the 105 mm's muzzle slides with it");
                Assert.IsFalse(tank.Muzzles["gun"].IsChildOf(tank.Elevation), "the 105 mm does not rise with the mortar");
            }
            finally
            {
                Object.DestroyImmediate(parent.gameObject);
                models.Dispose();
                materials.Dispose();
            }
        }

        /// <summary>The high-detail variants (High graphics) keep every pivot and muzzle of the normal model, in the same place.</summary>
        [TestCase("main_battle_tank"), TestCase("light_tank"), TestCase("heavy_tank"), TestCase("apc"), TestCase("scout_jeep"),
         TestCase("aa_vehicle"), TestCase("artillery"), TestCase("tank_destroyer"), TestCase("attack_helicopter"), TestCase("attack_jet"),
         TestCase("fighter_jet"), TestCase("sky_gunship")]
        public void HighDetailVariantsKeepThePivots(string id)
        {
            var normal = Load(id).transform;
            var detail = Load(id + "_hd").transform;
            var checkedAny = false;
            foreach (var t in normal.GetComponentsInChildren<Transform>(true))
            {
                if (!(t.name.StartsWith("Muzzle_") || t.name == "Turret" || t.name.StartsWith("Mount_") || t.name is "Rotor" or "Tail_rotor" or "Radar"))
                    continue;
                var twin = Find(detail, t.name);
                Assert.IsNotNull(twin, $"{id}_hd has {t.name}");
                Assert.Less(Vector3.Distance(normal.InverseTransformPoint(t.position), detail.InverseTransformPoint(twin.position)), 0.01f, $"{id}_hd {t.name} in place");
                checkedAny = true;
            }
            Assert.IsTrue(checkedAny, $"{id} has pivots to compare");
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
