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
            Assert.LessOrEqual(_root.GetComponentsInChildren<ParticleSystem>(true).Length, 15, "one system per layer kind, not per blast");
        }

        [Test]
        public void FireballsSmokeAndFlamesAreFlipbooks()
        {
            new BlastLayers(_materials, _root.transform);
            new FireSpots(_materials, _root.transform);
            foreach (var name in new[] { "Fireball", "Hot Fireball", "Smoke", "Dust", "Dust Ring", "Flames" })
            {
                var layer = Layer(name);
                var sheet = layer.textureSheetAnimation;
                Assert.IsTrue(sheet.enabled, name + " animates a sheet");
                Assert.AreEqual(FxMaterials.Tiles, sheet.numTilesX, name);
                var material = layer.GetComponent<ParticleSystemRenderer>().sharedMaterial;
                Assert.AreEqual("MachineBrigade/Flipbook", material.shader.name, name);
                Assert.IsNotNull(material.GetTexture("_MainTex"), name + " has its sheet");
            }
        }

        [Test]
        public void BiggerBlastsThrowMoreSolidChunks()
        {
            var layers = new BlastLayers(_materials, _root.transform);
            var fires = new FireSpots(_materials, _root.transform);
            var previous = -1;
            foreach (var tier in new[] { ExplosionTier.Medium, ExplosionTier.Large, ExplosionTier.Huge, ExplosionTier.Ultimate })
            {
                var pool = new DebrisPool(600);
                layers.Chunks = new ChunkThrower(pool, _materials, null, fires, _root.transform);
                ExplosionEffect.Create(tier, layers).Play(Vector3.zero, 0f);
                Assert.Greater(pool.Active, previous, $"{tier} throws more chunks than the tier below");
                previous = pool.Active;
            }
            Assert.GreaterOrEqual(previous, 40, "the heaviest blasts throw dozens of chunks");
        }

        [Test]
        public void BurningChunksTrailFireAndSmokeThenBurnWhereTheyLand()
        {
            var layers = new BlastLayers(_materials, _root.transform);
            var fires = new FireSpots(_materials, _root.transform);
            var pool = new DebrisPool(300);
            layers.Chunks = new ChunkThrower(pool, _materials, null, fires, _root.transform);
            ExplosionEffect.Create(ExplosionTier.Huge, layers).Play(Vector3.zero, 0f);
            pool.Tick(0.3f, 0.3f);
            Assert.Greater(Layer("Chunk Flames").particleCount, 0, "burning chunks trail flames");
            Assert.Greater(Layer("Chunk Smoke").particleCount, 0, "and smoke");
            for (var t = 0.3f; t < 4f; t += 0.05f) pool.Tick(t, 0.05f);
            Assert.Greater(fires.Burning, 0, "the burning chunks keep burning on the ground");
        }

        [Test]
        public void ChunksBounceAndSettleLyingOnTheGround()
        {
            var pool = new DebrisPool(8);
            var mesh = ChunkMeshes.Shard(3);
            pool.Launch(new ChunkModel(mesh, new[] { _materials.Fallback }), new Vector3(0f, 1f, 0f), Random.rotation,
                new Vector3(4f, 9f, 0f), Vector3.one, 0f, 30f);
            for (var t = 0f; t < 6f; t += 0.02f) pool.Tick(t, 0.02f);
            Assert.AreEqual(1, pool.Active, "the chunk is still there");
            pool.Tick(31f, 0.02f);
            Assert.AreEqual(0, pool.Active, "and gone once its time is up");
        }

        [Test]
        public void BlastsStayWithinTheirParticleBudgets()
        {
            var layers = new BlastLayers(_materials, _root.transform);
            var caps = new System.Collections.Generic.Dictionary<ExplosionTier, int>
            {
                [ExplosionTier.Small] = 20, [ExplosionTier.Medium] = 90, [ExplosionTier.Large] = 240, [ExplosionTier.Huge] = 400,
                [ExplosionTier.Ultimate] = 480,
            };
            foreach (var pair in caps)
                Assert.LessOrEqual(ExplosionEffect.Create(pair.Key, layers).ParticleCount, pair.Value, pair.Key.ToString());
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
