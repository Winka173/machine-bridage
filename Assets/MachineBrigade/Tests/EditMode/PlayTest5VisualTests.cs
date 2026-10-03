using System.Linq;
using NUnit.Framework;
using MachineBrigade.Editor;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Game.Views;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Play-test 5, the view and model half (DECISIONS 20V): the In action range's targets and fire-support framing,
    /// the reworked blasts and their Low budget, the new hull fire, the railgun's burn, the smaller FPV drone, the
    /// gunship's side battery and its transport twin, the gunship's card and the bunker's dug-in pose.
    /// </summary>
    public class PlayTest5VisualTests
    {
        private MaterialLibrary _materials;
        private GameObject _root;
        private GraphicsQuality _graphics;

        [SetUp]
        public void SetUp()
        {
            _materials = new MaterialLibrary();
            _root = new GameObject("Play-test 5 Test");
            _graphics = MatchSettings.Graphics;
            MatchSettings.Graphics = GraphicsQuality.High;
        }

        [TearDown]
        public void TearDown()
        {
            MatchSettings.Graphics = _graphics;
            Object.DestroyImmediate(_root);
            _materials.Dispose();
        }

        [Test]
        public void RangeTargetsCoverEveryArmourLevelAndNoneLaysSmoke()
        {
            var catalog = GameContent.LoadCatalog();
            var levels = FiringRange.GroundTargets.Select(t => catalog.Vehicles[t.id].Armour.Front).OrderBy(l => l).ToArray();
            CollectionAssert.AreEqual(new[] { 0, 1, 2, 3, 4 }, levels, "one target of each armour level");
            foreach (var (id, _) in FiringRange.GroundTargets)
                Assert.IsFalse(catalog.Vehicles[id].Skills.Any(s => s.Kind == SkillKind.Smoke), id + " lays no smoke");
        }

        [Test]
        public void FireSupportsAreFramedWithTheSkyTheyComeFrom()
        {
            var catalog = GameContent.LoadCatalog();
            foreach (var id in MatchSettings.AllSupports.Concat(Progression.Items))
                Assert.Greater(FiringRange.SupportSky(catalog.Supports[id]), 10f, id);
            Assert.GreaterOrEqual(FiringRange.SupportSky(catalog.Supports["airstrike"]), 24f, "the strike jet's height");
        }

        /// <summary>The airstrike's clip on its range: the targets and the strike jet's height over them both in the picture.</summary>
        [Test]
        public void TheAirstrikesClipShowsTheJetsHeightAsWellAsTheImpacts()
        {
            // The range's runtime clean-up calls Destroy, which edit mode only logs about: the framing is what is tested.
            UnityEngine.TestTools.LogAssert.ignoreFailingMessages = true;
            var catalog = GameContent.LoadCatalog();
            var meshes = new MeshLibrary();
            var models = new ModelLibrary(_materials);
            var camera = new GameObject("Range Camera").AddComponent<Camera>();
            camera.transform.SetParent(_root.transform, false);
            camera.aspect = 1.03f;
            var range = new FiringRange(catalog, _materials, meshes, models, camera, 30, "airstrike");
            try
            {
                for (var i = 0; i < 60; i++) range.Tick(0.05f);
                foreach (var point in new[] { new Vector3(0f, 0f, 6f), new Vector3(0f, 24f, 8f), new Vector3(-8.5f, 0f, 12f), new Vector3(8.5f, 0f, 15f), new Vector3(0f, 0f, 15f) })
                {
                    var v = camera.WorldToViewportPoint(point);
                    Assert.That(v.x, Is.InRange(0.03f, 0.97f), $"{point} across");
                    Assert.That(v.y, Is.InRange(0.03f, 0.97f), $"{point} up the picture");
                }
            }
            finally
            {
                var root = GameObject.Find("Firing Range");
                if (root != null) Object.DestroyImmediate(root);
                models.Dispose();
                meshes.Dispose();
            }
        }

        [Test]
        public void BlastsAreLayeredRicherAndLowKeepsTheShapesWithFewerParticles()
        {
            var layers = new BlastLayers(_materials, _root.transform);
            foreach (var tier in new[] { ExplosionTier.Medium, ExplosionTier.Large, ExplosionTier.Huge, ExplosionTier.Ultimate })
            {
                var blast = ExplosionEffect.Create(tier, layers);
                Assert.Greater(blast.ParticleCount, blast.CoreParticleCount, tier + ": the rework adds particles");
                var low = blast.ParticleCountAt(1f, 0.4f);
                Assert.Less(low, blast.ParticleCount, tier + ": Low emits fewer of them");
                Assert.GreaterOrEqual(low, blast.CoreParticleCount, tier + ": but never less than the old recipe");
            }
            // A big blast leaves a smoke column; the hot core and the fire bursts come with it.
            var large = ExplosionEffect.Create(ExplosionTier.Large, layers);
            large.Play(Vector3.zero, 0f);
            for (var t = 0.1f; t < 3f; t += 0.1f) large.Tick(t);
            layers.Column.Simulate(0.001f, false, false);
            Assert.Greater(layers.Column.particleCount, 3, "a column over the crater");
            layers.HotFireball.Simulate(0.001f, false, false);
            Assert.Greater(layers.HotFireball.particleCount, 0, "a white-hot core");
            Assert.AreEqual(1f, ExplosionEffect.RichShareAt(1f));
            Assert.AreEqual(0.5f, ExplosionEffect.RichShareAt(0.4f));
        }

        [Test]
        public void HullFireGrowsWithTheDamageAndLowBurnsOnFewerPoints()
        {
            Assert.AreEqual(0f, HullFire.Severity(HullFire.Burning), 1e-4f, "a small fire just under 30 %");
            Assert.AreEqual(1f, HullFire.Severity(0.02f), 1e-4f, "the biggest near death");
            Assert.Less(HullFire.Severity(0.25f), HullFire.Severity(0.1f));
            Assert.AreEqual(1, HullFire.PointsAt(0.1f, false));
            Assert.AreEqual(3, HullFire.PointsAt(0.9f, false));
            Assert.AreEqual(2, HullFire.PointsAt(0.9f, true), "Low: at most two fire points");
            Assert.Greater(HullFire.LowBeat, HullFire.Beat, "Low feeds it less often");
            var fire = new HullFire(_materials, _root.transform);
            Assert.AreEqual(0, fire.Alive);
        }

        [Test]
        public void ARailgunHitLeavesABurnThatCoolsAndGoes()
        {
            var emitters = new Emitters(_materials, _root.transform);
            var lasers = new LaserBeams(_materials, emitters, null, _root.transform);
            lasers.Sear(new Vector3(0f, 1f, 0f), Sim.Core.EntityId.None, null, 1.3f, 2.6f, 0f);
            Assert.AreEqual(1, lasers.Burns);
            for (var t = 0.05f; t < 1f; t += 0.05f) lasers.Tick(t, 0.05f, null);
            var sparks = _root.GetComponentsInChildren<ParticleSystem>().First(p => p.name == "Laser Sparks");
            sparks.Simulate(0.001f, false, false);
            Assert.Greater(sparks.particleCount, 0, "molten sparks off the burn");
            lasers.Tick(3f, 0.05f, null);
            Assert.AreEqual(0, lasers.Burns, "cooled and gone");
        }

        [Test]
        public void TheFpvDroneFliesAFifthSmaller()
        {
            Assert.AreEqual(1.3f * 0.8f, WeaponEffects.QuadScale, 1e-5f);
        }

        [Test]
        public void TheGunshipsBatteryFiresOutOfItsLeftSideAndTheTransportHasNone()
        {
            var gunship = Resources.Load<GameObject>("Models/sky_gunship");
            Assert.IsNotNull(gunship);
            float? side = null;
            foreach (var name in new[] { "Muzzle_mg", "Muzzle_gun", "Muzzle_main" })
            {
                var muzzle = gunship.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == name);
                Assert.IsNotNull(muzzle, name);
                var x = gunship.transform.InverseTransformPoint(muzzle.position).x;
                Assert.Greater(Mathf.Abs(x), 1.4f, name + " sticks well out of the fuselage");
                side ??= Mathf.Sign(x);
                Assert.AreEqual(side.Value, Mathf.Sign(x), name + " on the same (left) side as the others");
            }
            var transport = Resources.Load<GameObject>("Models/" + AirDrops.TransportModel);
            Assert.IsNotNull(transport, "the airlifter ships");
            Assert.IsFalse(transport.GetComponentsInChildren<Transform>(true).Any(t => t.name.StartsWith("Muzzle_")), "no guns on the transport");
        }

        [Test]
        public void TheBunkerDigsInHullDownBehindItsBank()
        {
            Assert.Greater(VehicleView.HullSink, 1f, "hull-down: sunk past its tracks");
            Assert.Less(VehicleView.MountLift, VehicleView.HullSink, "the turret lifted just clear of the parapet");
            Assert.That(VehicleView.PlateFold, Is.InRange(10f, 35f), "the side plates lean out as revetments");
        }
    }
}
