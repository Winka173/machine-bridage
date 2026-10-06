using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Play-test 8 B, effects and models (DECISIONS 22R): the burning-vehicle fire in three stages with its light on the
    /// hull and ground, blast smoke that clears sooner, the AC-130 without its Griffins and with shorter barrels, and
    /// Icarus redrawn as an orbital platform with every part node and muzzle kept.
    /// </summary>
    public class PlayTest8VisualTests
    {
        private MaterialLibrary _materials;
        private GameObject _root;
        private GraphicsQuality _graphics;

        [SetUp]
        public void SetUp()
        {
            _materials = new MaterialLibrary();
            _root = new GameObject("Play-test 8 Test");
            _graphics = MatchSettings.Graphics;
            MatchSettings.Graphics = GraphicsQuality.High;
        }

        [TearDown]
        public void TearDown()
        {
            MatchSettings.Graphics = _graphics;
            HeatLights.Clear();
            Object.DestroyImmediate(_root);
            _materials.Dispose();
        }

        [Test]
        public void TheVehicleFireBurnsInThreeStagesAndIsNeverSmallerThanBefore()
        {
            Assert.AreEqual(1, HullFire.Stage(HullFire.Severity(0.25f)), "catching");
            Assert.AreEqual(2, HullFire.Stage(HullFire.Severity(0.15f)), "burning");
            Assert.AreEqual(3, HullFire.Stage(HullFire.Severity(0.05f)), "ablaze");
            for (var s = 0f; s <= 1f; s += 0.05f)
            {
                // Play-test 6's flames were radius x share x Lerp(0.8, 1.45, s): the new ones are at least as big.
                Assert.GreaterOrEqual(HullFire.FlameSize(s) + 0.04f, Mathf.Lerp(0.8f, 1.45f, s), $"flames at severity {s:0.00}");
                if (s < 0.05f) continue;
                Assert.GreaterOrEqual(HullFire.FlameSize(s), HullFire.FlameSize(s - 0.05f), "grows with the damage");
                Assert.GreaterOrEqual(HullFire.LightReach(s), HullFire.LightReach(s - 0.05f), "its light reaches farther");
                Assert.GreaterOrEqual(HullFire.TonguesAt(s, false), HullFire.TonguesAt(s - 0.05f, false));
                Assert.GreaterOrEqual(HullFire.BodiesAt(s), HullFire.BodiesAt(s - 0.05f));
            }
            var fire = new HullFire(_materials, _root.transform);
            var tank = new GameObject("Tank").transform;
            tank.SetParent(_root.transform, false);
            fire.Feed(tank, 2.2f, 2.4f, false, 0, 0.05f, 0);
            fire.Simulate(0.001f);
            var flames = _root.GetComponentsInChildren<ParticleSystem>().First(p => p.name == "Hull Fire Tongues");
            Assert.GreaterOrEqual(flames.particleCount, 3 * (HullFire.BodiesAt(1f) + HullFire.TonguesAt(1f, false)) - 3,
                "an ablaze tank's three sources each put out bodies and tongues on a beat");
        }

        [Test]
        public void BurningVehiclesLightTheirHullAndTheGroundAtMostFourAtOnce()
        {
            HeatLights.Begin();
            for (var i = 0; i < 6; i++) HeatLights.Add(new Vector3(i * 10f, 1.8f, 0f), 6f, 1f + i, i, 1f);
            Assert.AreEqual(HeatLights.Max, HeatLights.Count, "capped");
            HeatLights.Commit();
            Assert.AreEqual(HeatLights.Max, Shader.GetGlobalFloat("_MbHeatCount"), 1e-4f, "handed to the Lit shader");
            MatchSettings.Graphics = GraphicsQuality.Low;
            HeatLights.Begin();
            for (var i = 0; i < 6; i++) HeatLights.Add(Vector3.zero, 6f, 1f, i, 1f);
            Assert.AreEqual(HeatLights.LowMax, HeatLights.Count, "fewer on Low");
            for (var t = 0f; t < 3f; t += 0.07f)
                Assert.That(HeatLights.Flicker(7, t), Is.InRange(0.6f, 1.12f), "it flickers, never out");
            HeatLights.Clear();
            Assert.AreEqual(0f, Shader.GetGlobalFloat("_MbHeatCount"), 1e-4f, "nothing lit once cleared");
        }

        [Test]
        public void BlastSmokeClearsSoonerButTheFireballsAreUntouched()
        {
            Assert.That(BlastLayers.SmokeLife, Is.InRange(0.5f, 0.7f), "30-50 % shorter");
            var layers = new BlastLayers(_materials, _root.transform);
            var blast = ExplosionEffect.Create(ExplosionTier.Medium, layers);
            blast.Play(Vector3.zero, 0f);
            blast.Tick(1f);
            layers.Smoke.Simulate(0.001f, false, false);
            layers.Fireball.Simulate(0.001f, false, false);
            var smoke = new ParticleSystem.Particle[layers.Smoke.particleCount];
            layers.Smoke.GetParticles(smoke);
            Assert.Greater(smoke.Length, 0);
            // The Medium recipe's smoke lives 2.6 to 4.6 s: now at most 0.65 of that.
            Assert.IsTrue(smoke.All(p => p.startLifetime <= 4.6f * BlastLayers.SmokeLife + 1e-3f), "the smoke lives shorter");
            var fire = new ParticleSystem.Particle[layers.Fireball.particleCount];
            layers.Fireball.GetParticles(fire);
            // The recipe's fireballs live 0.95 to 1.25 s, its fire bursts round them 0.7 to 0.95 s: as before.
            Assert.IsTrue(fire.Length > 0 && fire.All(p => p.startLifetime >= 0.7f - 1e-3f), "the fireballs as long as before");
        }

        [Test]
        public void TheGunshipFliesWithoutMissilesAndWithShorterBarrels()
        {
            var gunship = GameContent.LoadCatalog().Vehicle("sky_gunship");
            Assert.IsFalse(gunship.Mounts.Any(m => m.Weapon.Id == "griffin"), "no Griffins");
            foreach (var id in new[] { "sky_gunship", "sky_gunship_hd" })
            {
                var model = Resources.Load<GameObject>("Models/" + id);
                Assert.IsNotNull(model, id);
                var nodes = model.GetComponentsInChildren<Transform>(true);
                Assert.IsFalse(nodes.Any(t => t.name == "Muzzle_ramp"), id + ": no ramp launcher");
                foreach (var name in new[] { "Muzzle_mg", "Muzzle_gun", "Muzzle_main" })
                {
                    var x = Mathf.Abs(model.transform.InverseTransformPoint(nodes.First(t => t.name == name).position).x);
                    Assert.That(x, Is.InRange(1.4f, 2.3f), $"{id} {name}: out of the side, but not far");
                }
            }
        }

        [Test]
        public void IcarusKeepsEveryPartNodeAndMuzzle()
        {
            var icarus = GameContent.LoadCatalog().Vehicle("silver_bug");
            var model = Resources.Load<GameObject>("Models/silver_bug");
            Assert.IsNotNull(model);
            var nodes = model.GetComponentsInChildren<Transform>(true);
            foreach (var part in icarus.Parts.Where(p => p.Node != null))
            {
                var node = nodes.FirstOrDefault(t => t.name == part.Node);
                Assert.IsNotNull(node, part.Node);
                var at = model.transform.InverseTransformPoint(node.position);
                Assert.Less(Vector3.Distance(at, new Vector3(part.At.X, part.Height, part.At.Y)), 0.05f, part.Node + " in its place");
            }
            var wreck = Resources.Load<GameObject>("Models/silver_bug_wreck").GetComponentsInChildren<Transform>(true);
            foreach (var name in new[] { "Muzzle_main", "Muzzle_gun", "Muzzle_gun_02", "Muzzle_missile" })
            {
                Assert.IsTrue(nodes.Any(t => t.name == name), "silver_bug " + name);
                Assert.IsTrue(wreck.Any(t => t.name == name), "silver_bug_wreck " + name);
            }
        }
    }
}
