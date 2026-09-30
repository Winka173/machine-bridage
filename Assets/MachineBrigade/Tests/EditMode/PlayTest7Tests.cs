using System.Collections.Generic;
using System.Linq;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using NUnit.Framework;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Play-test 7 (DECISIONS 22P): the AC-130 as an aircraft card, several mounts firing together, slower missiles and
    /// drones, the siege tank's retracting 105 mm and its machine gun clear of the siege cannon, short self-defence machine
    /// guns, and towers without extra weapons (in the data and on their models).
    /// </summary>
    public class PlayTest7Tests
    {
        private static SimWorld Range(Catalog catalog) =>
            new SimWorld(catalog, new MapDefinition("range", 220f,
                new[] { new TeamStart(0, new Vector2(0f, -90f)), new TeamStart(1, new Vector2(0f, 90f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed: 7);

        [Test]
        public void TheAc130IsAnAircraftCardInTheAircraftList()
        {
            var catalog = GameContent.LoadCatalog();
            CollectionAssert.Contains(MatchSettings.AllVehicles, "sky_gunship", "a vehicle card in the deck and collection");
            Assert.IsFalse(catalog.TryGetSupport("gunship_strike", out _), "the Gunship support card is gone");
            CollectionAssert.DoesNotContain(MatchSettings.AllSupports, "gunship_strike");
            var def = catalog.Vehicles["sky_gunship"];
            Assert.IsTrue(def.Card && def.CpCost > 0 && def.Flying && def.FixedWing && def.Orbit, "a card-carrying aeroplane in a pylon turn");
            Assert.AreEqual(UnitClass.Plane, def.Class);
            Assert.AreEqual(GearBranch.Air, Gear.BranchOf(def), "listed with the aircraft");
            Assert.IsTrue(Progression.IsPremium("sky_gunship"));
            Assert.AreEqual(4500, Progression.Price("sky_gunship", catalog));
            Assert.AreEqual("vehicle", CardArt.EntryFor("sky_gunship")?.kind);
            Assert.AreEqual("sky_gunship", CardArt.EntryFor("sky_gunship")?.model);
            var sides = def.Mounts.Where(m => m.Aim == MountAim.Left).Select(m => m.Weapon.Id).ToList();
            CollectionAssert.AreEquivalent(new[] { "gunship_105", "gunship_40mm", "gunship_25mm" }, sides, "105, 40 and 25 mm out of the left side");
            var was = Strings.Vietnamese;
            try
            {
                Strings.Vietnamese = false;
                // Prompt 25 D1 (DECISIONS 25D1): the spreadsheet's name; the AC-130 is on its reference line.
                Assert.AreEqual("Airborne gunship", Strings.Card("sky_gunship"));
                Assert.AreNotEqual(Strings.Card("sky_gunship"), Strings.Card("gunship_heli"), "not the Mi-24");
                Strings.Vietnamese = true;
                Assert.AreEqual("Pháo hạm bay", Strings.Card("sky_gunship"));
            }
            finally
            {
                Strings.Vietnamese = was;
            }
        }

        /// <summary>
        /// A tank, a helicopter, the AC-130, a tower and a boss against a group of dummies: each mount fires on its own
        /// timing (two different mounts fire within a tenth of a second of each other), and twin mounts (the same weapon)
        /// never open fire less than <see cref="CombatSystem.TwinOffset"/> apart.
        /// </summary>
        [TestCase("main_battle_tank"), TestCase("gunship_heli"), TestCase("sky_gunship"), TestCase("heavy_turret.bastion"), TestCase("mega_gunship")]
        public void SeveralMountsFireTogether(string id)
        {
            var catalog = GameContent.LoadCatalog();
            var def = catalog.Vehicles[id];
            var world = Range(catalog);
            var shooter = world.SpawnVehicle(id, 0, new Vector2(0f, -12f), 0f);
            foreach (var (other, at) in new[] { ("main_battle_tank", new Vector2(-4f, 12f)), ("ifv", new Vector2(5f, 15f)), ("armored_car", new Vector2(-8f, 6f)),
                         ("attack_helicopter", new Vector2(8f, 6f)) })
            {
                var dummy = world.SpawnVehicle(other, 1, at, System.MathF.PI);
                world.MakeDummy(dummy);
                dummy.HpScale = 1000f;
                dummy.Hp = dummy.MaxHp;
            }
            var last = new Dictionary<int, double>();
            var opened = new List<(int mount, double at)>();
            var fired = new HashSet<int>();
            var together = 0;
            for (var t = 0f; t < 30f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                {
                    if (e.Kind != SimEventKind.WeaponFired || e.Entity != shooter.Id) continue;
                    var now = world.Time;
                    if (last.Any(p => p.Key != e.Mount && now - p.Value < 0.1)) together++;
                    var weapon = def.Mounts[e.Mount].Weapon;
                    if (!last.TryGetValue(e.Mount, out var before) || now - before > weapon.Cooldown * 1.1f + 0.06f) opened.Add((e.Mount, now));
                    last[e.Mount] = now;
                    fired.Add(e.Mount);
                }
                world.ClearEvents();
            }
            Assert.GreaterOrEqual(fired.Count, 2, $"{id}: several mounts fired ({string.Join(", ", fired.Select(m => def.Mounts[m].Weapon.Id))})");
            Assert.Greater(together, 0, $"{id}: two mounts fired together");
            var lockstep = new List<string>();
            foreach (var (mount, at) in opened)
                foreach (var (other, when) in opened)
                    if (other > mount && def.Mounts[other].Weapon.Id == def.Mounts[mount].Weapon.Id && System.Math.Abs(when - at) < CombatSystem.TwinOffset - 1e-3)
                        lockstep.Add($"{def.Mounts[mount].Weapon.Id} mounts {mount} and {other} at {at:0.00} s");
            Assert.IsEmpty(lockstep, id + ": twin barrels opened fire together\n" + string.Join("\n", lockstep));
        }

        [Test]
        public void TheHeavyGunshipsAndAttackJetsMissilesAndTheMothershipsDronesAreSlower()
        {
            var w = GameContent.LoadCatalog().Weapons;
            // 30 % slower than play-test 6's.
            Assert.AreEqual(26.9f, w["gunship_rockets"].ProjectileSpeed, 1e-3f);
            Assert.AreEqual(11.8f, w["heli_atgm"].ProjectileSpeed, 1e-3f);
            Assert.AreEqual(20.2f, w["s8_pods"].ProjectileSpeed, 1e-3f);
            Assert.AreEqual(9.7f, w["kh29"].ProjectileSpeed, 1e-3f);
            Assert.AreEqual(10.1f, w["r60"].ProjectileSpeed, 1e-3f);
            Assert.AreEqual(18.2f, w["swarm_drones"].ProjectileSpeed, 1e-3f);
        }

        [Test]
        public void LongRangeAndSupportVehiclesCarryAShortSelfDefenceMachineGun()
        {
            var catalog = GameContent.LoadCatalog();
            var full = catalog.Weapons["hmg_roof"].Range;
            foreach (var id in new[] { "artillery", "mlrs", "heavy_rocket_artillery", "ballistic_launcher", "lancet_truck", "shahed_truck", "elite_mlrs",
                         "elite_grad", "sam_launcher", "mortar_carrier", "thermobaric_launcher", "fpv_carrier", "siege_tank", "rocket_technical",
                         "counter_battery_radar", "command_vehicle", "ammo_carrier", "ew_jammer", "mine_layer", "smoke_carrier", "shield_carrier",
                         "engineer_vehicle" })
            {
                var guns = catalog.Vehicles[id].Mounts.Where(m => m.Weapon.Family == "mg").ToList();
                Assert.IsNotEmpty(guns, id);
                foreach (var gun in guns)
                    Assert.LessOrEqual(gun.Weapon.Range, full * 0.7f + 1e-3f, $"{id}: {gun.Weapon.Id} reaches {gun.Weapon.Range} m");
            }
            Assert.AreEqual(full, catalog.Vehicles["main_battle_tank"].Mounts.First(m => m.Weapon.Id == "hmg_roof").Weapon.Range, "a tank's roof gun keeps its reach");
        }

        [Test]
        public void TowersCarryNoExtraWeaponsInTheDataOrOnTheirModels()
        {
            var catalog = GameContent.LoadCatalog();
            var v = catalog.Vehicles;
            Assert.AreEqual(1, v["gun_turret"].Mounts.Count, "the gun turret: its gun only");
            Assert.AreEqual(1, v["heavy_turret"].Mounts.Count, "the heavy fortress: its twin 155 mm only");
            Assert.AreEqual(1, v["mg_bunker"].Mounts.Count, "the MG bunker: its machine gun");
            Assert.AreEqual(1, v["guard_tower"].Mounts.Count, "the guard tower: its own gun");
            var bastion = v["heavy_turret.bastion"].Mounts;
            Assert.AreEqual(2, bastion.Count(m => m.Slot == "gun" && m.Weapon.Family == "mg"), "the steel fortress keeps its two machine-gun turrets");
            Assert.IsFalse(bastion.Any(m => m.Slot == "coax"));
            var materials = new MaterialLibrary();
            var models = new ModelLibrary(materials);
            var root = new GameObject("Towers").transform;
            try
            {
                string[] Parts(string model) => models.Spawn(model, 0, root).Root.GetComponentsInChildren<Transform>(true).Select(t => t.name).ToArray();
                foreach (var model in new[] { "heavy_turret", "heavy_turret_a", "gun_turret", "gun_turret_a", "gun_turret_b", "missile_battery", "rocket_turret",
                             "artillery_emplacement", "mg_bunker", "guard_tower" })
                {
                    if (!models.Has(model)) continue;
                    var parts = Parts(model);
                    Assert.IsFalse(parts.Any(n => n.StartsWith("Coax")), model + ": no coaxial gun drawn");
                    Assert.IsFalse(parts.Any(n => n.StartsWith("Mount_")), model + ": no second weapon drawn (" + string.Join(", ", parts.Where(n => n.StartsWith("Mount_"))) + ")");
                }
                var steel = Parts("heavy_turret_b");
                Assert.AreEqual(2, steel.Count(n => n.StartsWith("Mount_gun")), "the steel fortress's two machine-gun turrets are drawn");
                Assert.IsFalse(steel.Any(n => n.StartsWith("Mount_mg") || n.StartsWith("Coax")), "without the base's roof gun and coaxial gun");
                Assert.IsTrue(Parts("headquarters").Any(n => n.StartsWith("Mount_mg")), "the HQ keeps its roof guns");
            }
            finally
            {
                Object.DestroyImmediate(root.gameObject);
                models.Dispose();
                materials.Dispose();
            }
        }

        [Test]
        public void TheSiegeTanksTwinGunRetractsAndItsMachineGunStaysClearOfTheSiegeCannon()
        {
            var catalog = GameContent.LoadCatalog();
            var materials = new MaterialLibrary();
            var meshes = new MeshLibrary();
            var models = new ModelLibrary(materials);
            var root = new GameObject("Siege").transform;
            try
            {
                var world = Range(catalog);
                var views = new ViewRegistry(models, meshes, materials, root, 0);
                var tank = world.SpawnVehicle("siege_tank", 0, Vector2.Zero, 0f);
                var view = views.Add(tank);
                var parts = view.Model.Root.GetComponentsInChildren<Transform>(true);
                Transform Part(string name) => parts.First(t => t.name == name);
                var turret = view.Model.Turret;
                var hull = view.Model.Root.transform;
                void Render()
                {
                    for (var i = 0; i < 3; i++)
                    {
                        views.SnapshotAll();
                        views.Render(1f, Quaternion.identity);
                    }
                }
                Render();
                var reach = Vector3.Dot(Part("Muzzle_gun").position - turret.position, hull.forward);
                Assert.Greater(reach, 3f, "tank mode: the twin 105 mm out in front");
                tank.Deploy = DeployState.Deployed;
                Render();
                // Sieged: the 105 mm run right into the turret (its muzzle inside the turret's 3.35 m length, drawn at 0.85).
                var inside = turret.InverseTransformPoint(Part("Muzzle_gun").position);
                Assert.Less(Mathf.Abs(inside.z), 1.9f, $"sieged: the twin 105 mm retracted ({inside.z:0.00} m from the turret's middle)");
                // The roof machine gun rides the turret and stands clear of the siege cannon's cradle.
                var mg = Part("Mount_mg");
                Assert.AreEqual(turret, mg.parent);
                var cradle = Part("Elevation");
                var apart = Vector3.Distance(Vector3.ProjectOnPlane(mg.position - cradle.position, Vector3.up), Vector3.zero);
                Assert.Greater(apart, 1.2f, $"the machine gun {apart:0.00} m from the siege cannon's trunnion");
                tank.Deploy = DeployState.Mobile;
                Render();
                Assert.Greater(Vector3.Dot(Part("Muzzle_gun").position - turret.position, hull.forward), 3f, "packed up: the 105 mm back out");
            }
            finally
            {
                Object.DestroyImmediate(root.gameObject);
                models.Dispose();
                materials.Dispose();
            }
        }
    }
}
