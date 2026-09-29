using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Play-test 6, effects and models (DECISIONS 21H): the siege tank after StarCraft 2's (spawned in tank mode, its legs,
    /// rams and telescoping cannon apart), the launchers' erectors and the IFVs' ATGM boxes, the aircraft drawn smaller,
    /// the burning-vehicle fire, and the SEAD strike's missile.
    /// </summary>
    public class PlayTest6VisualTests
    {
        private MaterialLibrary _materials;
        private ModelLibrary _models;
        private GameObject _root;
        private GraphicsQuality _graphics;

        [SetUp]
        public void SetUp()
        {
            _materials = new MaterialLibrary();
            _models = new ModelLibrary(_materials);
            _root = new GameObject("Play-test 6 Test");
            _graphics = MatchSettings.Graphics;
            MatchSettings.Graphics = GraphicsQuality.High;
        }

        [TearDown]
        public void TearDown()
        {
            MatchSettings.Graphics = _graphics;
            Object.DestroyImmediate(_root);
            _models.Dispose();
            _materials.Dispose();
        }

        private static Transform Find(Transform root, string name) =>
            root.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == name);

        [Test]
        public void TheSiegeTankSpawnsInTankModeWithItsLegsRamsAndTelescopingCannonApart()
        {
            var tank = _models.Spawn("siege_tank", 0, _root.transform);
            var root = tank.Root.transform;
            Assert.AreEqual(180f, tank.Turret.localEulerAngles.y, 0.5f, "drawn sieged, spawned turned round: tank mode");
            // The twin 105 mm points forward (+Z) and the siege cannon back over the engine deck.
            Assert.Greater(Vector3.Dot(tank.Muzzles["gun"].position - tank.Turret.position, root.forward), 3f, "the twin guns forward");
            Assert.Less(Vector3.Dot(tank.Muzzles["main"].position - tank.Turret.position, root.forward), -3f, "the siege cannon back");
            foreach (var side in new[] { "_l", "_r" })
            foreach (var leg in new[] { "brace", "leg" })
            {
                Assert.IsNotNull(Find(root, $"Deploy_{leg}{side}"), leg + side);
                Assert.IsTrue(Find(root, $"Deploy_{leg}ram{side}").IsChildOf(Find(root, $"Deploy_{leg}knee{side}")), "the ram in its housing");
                Assert.IsTrue(Find(root, $"Deploy_{leg}knee{side}").IsChildOf(Find(root, $"Deploy_{leg}{side}")), "the housing on its leg");
            }
            Assert.IsNotNull(tank.Elevation, "the siege cannon elevates");
            Assert.IsTrue(tank.RecoilParts.Any(p => p.name.StartsWith("Main_cannon_tube")), "the inner tube runs out");
            Assert.IsTrue(tank.RecoilParts.Any(p => p.name.StartsWith("Muzzle_brake")), "with its brake");
            Assert.AreEqual(0f, tank.RestPitch, 3f, "the cannon is drawn level");
            // The pad reaches the ground: the tilted leg's tip, less the pad's depth and the ram's drive, is at the ground.
            Assert.AreEqual(0f, VehicleView.LegHinge - VehicleView.PadUnder -
                                VehicleView.LegLength * Mathf.Sin(VehicleView.LegTilt * Mathf.Deg2Rad) - VehicleView.PadDrop, 1e-4f);
        }

        [Test]
        public void EveryLauncherHasAnErectorAndTheIfvsTheirOwnAtgmBox()
        {
            var catalog = GameContent.LoadCatalog();
            foreach (var (id, erector) in VehicleView.Erectors)
            {
                Assert.IsTrue(catalog.Vehicles.TryGetValue(id, out var def), id);
                var model = _models.Spawn(def.Model, 0, _root.transform);
                Assert.IsNotNull(model.Elevation, $"{id}: its launcher is on an elevating pivot");
                Debug.Log($"[PlayTest6] {id} ({def.Model}): drawn at {model.RestPitch:0.0} degrees, {erector.Kind} {erector.Raise:0} / {erector.Stow:0}");
                Assert.That(model.RestPitch + erector.Raise, Is.InRange(-5f, 92f), $"{id}: raised no further than upright");
                Assert.That(erector.Seconds, Is.InRange(0.5f, 2.5f));
            }
            foreach (var (id, parts) in new[] { ("ballistic_launcher", "Missile_body"), ("shahed_truck", "Rack"), ("lancet_truck", "Cells") })
            {
                var model = _models.Spawn(id, 0, _root.transform);
                Assert.IsTrue(Find(model.Root.transform, parts).IsChildOf(model.Elevation), $"{id}: {parts} rides the erector");
            }
            foreach (var id in ModelLibrary.SideLaunchers)
            {
                var model = _models.Spawn(id, 0, _root.transform);
                var box = model.Turret.Find(ModelLibrary.SideErectorName);
                Assert.IsNotNull(box, id);
                Assert.IsTrue(model.Muzzles["missile"].IsChildOf(box), $"{id}: the missile leaves from the box");
                Assert.IsFalse(model.Muzzles["missile"].IsChildOf(model.Elevation), $"{id}: the box no longer rides the gun");
            }
        }

        [Test]
        public void AircraftAreDrawnSmallerAllAlikeAndBossesKeepTheirSize()
        {
            var catalog = GameContent.LoadCatalog();
            Assert.That(VehicleView.AirShrink, Is.InRange(0.8f, 0.9f), "the owner's 10-20 %");
            var jet = catalog.Vehicle("fighter_jet");
            var heli = catalog.Vehicle("attack_helicopter");
            var tank = catalog.Vehicle("main_battle_tank");
            Assert.AreEqual(jet.Scale * VehicleView.AirShrink, VehicleView.DrawScaleOf(jet), 1e-5f);
            Assert.AreEqual(VehicleView.DrawScaleOf(jet) / VehicleView.DrawScaleOf(heli), jet.Scale / heli.Scale, 1e-4f, "their sizes against each other stay");
            Assert.AreEqual(tank.Scale, VehicleView.DrawScaleOf(tank), 1e-5f, "ground vehicles keep theirs");
            foreach (var boss in catalog.Vehicles.Values.Where(v => v.Boss && v.Flying))
                Assert.AreEqual(boss.Scale, VehicleView.DrawScaleOf(boss), 1e-5f, boss.Id);
        }

        [Test]
        public void TheVehicleFireRidesTheHullAndLowBurnsLess()
        {
            var fire = new HullFire(_materials, _root.transform);
            var tank = new GameObject("Tank").transform;
            tank.SetParent(_root.transform, false);
            var drive = new Vector3(6f, 0f, 0f);
            fire.Feed(tank, 2.2f, 2.4f, false, 0, 0.05f, 0, drive);
            fire.Simulate(0.001f);
            var tongues = _root.GetComponentsInChildren<ParticleSystem>().First(p => p.name == "Hull Fire Tongues");
            var smoke = _root.GetComponentsInChildren<ParticleSystem>().First(p => p.name == "Hull Fire Smoke");
            var flames = new ParticleSystem.Particle[tongues.particleCount];
            tongues.GetParticles(flames);
            Assert.Greater(flames.Length, 0);
            Assert.IsTrue(flames.All(f => f.velocity.x > 5f), "the flames move with the hull");
            var puffs = new ParticleSystem.Particle[smoke.particleCount];
            smoke.GetParticles(puffs);
            Assert.IsTrue(puffs.All(p => p.velocity.x < drive.x * 0.5f), "the smoke is left behind: it trails");
            Assert.Less(HullFire.FlareChance(0.5f, true), HullFire.FlareChance(0.5f, false), "Low flares up less");
            Assert.Greater(HullFire.FlareChance(1f, false), HullFire.FlareChance(0f, false), "worse fires flare up more");
            var before = fire.Alive;
            fire.FeedPoint(Vector3.up * 5f, 2f, 0.8f, Vector3.zero, 1);
            fire.Simulate(0.001f);
            Assert.Greater(fire.Alive, before, "a boss's part fire burns the same way");
        }

        [Test]
        public void TheSeadMissileIsDrawnBig()
        {
            Assert.GreaterOrEqual(StrikeEffects.SeadScale, 1.5f);
        }
    }
}
