using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>Blasts and fires share their particle systems, so nothing is cut short to make room.</summary>
    public class EffectsTests
    {
        private MaterialLibrary _materials;
        private GameObject _root;

        [SetUp]
        public void SetUp()
        {
            _materials = new MaterialLibrary();
            _root = new GameObject("Effects Test");
        }

        [TearDown]
        public void TearDown()
        {
            Object.DestroyImmediate(_root);
            _materials.Dispose();
        }

        [Test]
        public void ANewBlastDoesNotCutShortAnOlderOne()
        {
            var blast = ExplosionEffect.Create(ExplosionTier.Large, new BlastLayers(_materials, _root.transform));
            var fireball = Layer("Fireball");
            blast.Play(Vector3.zero, 0f);
            fireball.Simulate(0.2f, false, false);
            var first = fireball.particleCount;
            Assert.Greater(first, 0, "the first blast has a fireball");

            // Far more blasts than the old pool held: the first fireball must survive them all.
            for (var i = 0; i < 40; i++) blast.Play(new Vector3(i * 3f, 0f, 0f), 0.2f);
            fireball.Simulate(0.05f, false, false);
            Assert.GreaterOrEqual(fireball.particleCount, first * 20, "later blasts add fire instead of replacing it");
        }

        [Test]
        public void LaterBurstsArriveOnSchedule()
        {
            var blast = ExplosionEffect.Create(ExplosionTier.Large, new BlastLayers(_materials, _root.transform));
            var fireball = Layer("Fireball");
            blast.Play(Vector3.zero, 0f);
            fireball.Simulate(0.01f, false, false);
            var first = fireball.particleCount;
            blast.Tick(0.1f);
            fireball.Simulate(0.01f, false, false);
            Assert.AreEqual(first, fireball.particleCount, "secondary pops wait");
            blast.Tick(0.5f);
            fireball.Simulate(0.01f, false, false);
            Assert.Greater(fireball.particleCount, first, "and then pop");
        }

        [Test]
        public void EveryTierSharesTheSameFewSystems()
        {
            var layers = new BlastLayers(_materials, _root.transform);
            foreach (ExplosionTier tier in System.Enum.GetValues(typeof(ExplosionTier)))
                ExplosionEffect.Create(tier, layers).Play(Vector3.zero, 0f);
            Assert.LessOrEqual(_root.GetComponentsInChildren<ParticleSystem>(true).Length, 12, "one system per layer kind, not per blast");
        }

        [Test]
        public void BurningDebrisTrailsSmoke()
        {
            ExplosionEffect.Create(ExplosionTier.Huge, new BlastLayers(_materials, _root.transform)).Play(Vector3.zero, 0f);
            var debris = Layer("Burning Debris");
            var trail = Layer("Smoke Trail");
            debris.Simulate(0.3f, true, false);
            Assert.Greater(debris.particleCount, 0);
            Assert.Greater(trail.particleCount, 0, "each burning chunk leaves a smoke trail");
        }

        [Test]
        public void FiresBurnThenSmoulderThenGoOut()
        {
            var fires = new FireSpots(_materials, _root.transform);
            for (var i = 0; i < 200; i++) fires.Ignite(new Vector3(i, 0f, 0f), 1f, 10f, 0f);
            Assert.LessOrEqual(fires.Burning, 160, "a hard cap keeps a long battle bounded");
            fires.Tick(1f, 0.5f);
            Assert.Greater(Layer("Flames").particleCount, 0);
            fires.Tick(15f, 0.5f);
            Assert.Greater(fires.Burning, 0, "still smouldering after the flames die");
            fires.Tick(120f, 0.5f);
            Assert.AreEqual(0, fires.Burning);
        }

        [Test]
        public void MachineGunsFlickerOncePerRound()
        {
            var muzzle = new MuzzleFx(_materials, _root.transform);
            var core = Layer("Muzzle Core");
            muzzle.Fire(MuzzleFx.Kind.MachineGun, Vector3.up, Vector3.forward, 0f);
            core.Simulate(0.01f, false, false);
            Assert.AreEqual(1, core.particleCount, "the first round flashes at once");
            muzzle.Tick(MuzzleFx.RoundInterval * 2.5f);
            core.Simulate(0.001f, false, false);
            Assert.AreEqual(3, core.particleCount, "and each later round of the burst flashes again");
        }

        [Test]
        public void CannonsBlowSmokeAndGroundDustButAircraftDoNot()
        {
            var muzzle = new MuzzleFx(_materials, _root.transform);
            var smoke = Layer("Muzzle Puffs");
            var dust = Layer("Muzzle Dust");
            var flame = Layer("Muzzle Flame");
            muzzle.Fire(MuzzleFx.Kind.Cannon, new Vector3(0f, 2f, 0f), Vector3.forward, 0f, 1f, 0f);
            smoke.Simulate(0.01f, false, false);
            dust.Simulate(0.01f, false, false);
            flame.Simulate(0.01f, false, false);
            Assert.Greater(smoke.particleCount, 5, "a thick smoke puff");
            Assert.Greater(dust.particleCount, 0, "dust blown off the ground");
            Assert.Greater(flame.particleCount, 2, "a tongue of flame plus the muzzle-brake jets");

            var dustBefore = dust.particleCount;
            muzzle.Fire(MuzzleFx.Kind.Autocannon, new Vector3(0f, 30f, 0f), Vector3.down, 0f, 1f, null);
            dust.Simulate(0.001f, false, false);
            Assert.AreEqual(dustBefore, dust.particleCount, "an aircraft's gun raises no ground dust");
        }

        private ParticleSystem Layer(string name) =>
            _root.GetComponentsInChildren<ParticleSystem>(true).First(p => p.name == name);
    }
}
