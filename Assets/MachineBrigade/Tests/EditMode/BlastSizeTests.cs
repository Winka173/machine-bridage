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
    /// The play-test fix of 2026-09-28 (DECISIONS 11A): bigger tank-round, bomb and cruise-missile
    /// blasts that never lose particles of their own, a flame stream with rolling fireballs, and
    /// held laser beams.
    /// </summary>
    public class BlastSizeTests
    {
        private MaterialLibrary _materials;
        private GameObject _root;

        [SetUp]
        public void SetUp()
        {
            _materials = new MaterialLibrary();
            _root = new GameObject("Blast Size Test");
        }

        [TearDown]
        public void TearDown()
        {
            Object.DestroyImmediate(_root);
            _materials.Dispose();
        }

        [Test]
        public void TankRoundsAndBombsGrowByWhatFiredThem()
        {
            var catalog = GameContent.LoadCatalog();
            Assert.AreEqual(1.3f, BlastSizes.TankShell(catalog.Weapons["gun_57mm"]), 1e-4f, "light tank");
            Assert.AreEqual(1.4f, BlastSizes.TankShell(catalog.Weapons["gun_120mm"]), 1e-4f, "main battle tank");
            Assert.AreEqual(1.5f, BlastSizes.TankShell(catalog.Weapons["gun_152"]), 1e-4f, "heavy tank");
            Assert.AreEqual(1.5f, BlastSizes.TankShell(catalog.Weapons["gun_140_twin"]), 1e-4f, "super-heavy tank");
            Assert.AreEqual(1.5f, BlastSizes.Ground(catalog.Weapons["gun_203_siege"]), 1e-4f, "siege tank");
            Assert.AreEqual(1f, BlastSizes.Ground(catalog.Weapons["howitzer"]), 1e-4f, "other artillery as it was");
            Assert.Less(BlastSizes.Bomb("guided_bomb"), BlastSizes.Bomb("jet_bombs"), "a small guided bomb grows less than a FAB");
            foreach (var id in new[] { "guided_bomb", "jet_bombs", "bomber_payload", "stealth_payload", "airstrike", "cluster_strike" })
                Assert.That(BlastSizes.Bomb(id), Is.InRange(1.3f, 1.5f), id);
            Assert.AreEqual(1f, BlastSizes.Strike(catalog.Supports["artillery_barrage"]), 1e-4f, "a barrage is shells, not bombs");
        }

        [Test]
        public void AnEnlargedBlastKeepsEveryParticleOfItsRecipeOnEveryTier()
        {
            var layers = new BlastLayers(_materials, _root.transform);
            foreach (ExplosionTier tier in System.Enum.GetValues(typeof(ExplosionTier)))
            {
                var blast = ExplosionEffect.Create(tier, layers);
                Assert.AreEqual(blast.ParticleCount, blast.ParticleCountAt(1f), tier + ": grow 1 is the old blast");
                Assert.GreaterOrEqual(blast.ParticleCountAt(1.5f, 0.4f), blast.ParticleCount, tier + ": Low never loses any");
                Assert.Greater(blast.ParticleCountAt(1.5f), blast.ParticleCountAt(1.5f, 0.4f), tier + ": High adds the most");
            }
        }

        [Test]
        public void EnlargedFireballsComeInMoreQuadsRatherThanOnlyBiggerOnes()
        {
            var layers = new BlastLayers(_materials, _root.transform);
            var blast = ExplosionEffect.Create(ExplosionTier.Huge, layers);
            var (count, size) = Fireballs(() => blast.Play(Vector3.zero, 0f));
            layers.Clear();
            var (bigCount, bigSize) = Fireballs(() => blast.Play(Vector3.zero, 0f, 1f, 1.5f));
            Assert.Greater(bigCount, count, "more fireball quads");
            Assert.Greater(bigSize, size * 1.1f, "a little bigger each");
            Assert.Less(bigSize, size * 1.4f, "but not blown up half as big again");
        }

        [Test]
        public void ACruiseMissilesShockwaveReachesItsBlastRadius()
        {
            var catalog = GameContent.LoadCatalog();
            var radius = catalog.Supports["cruise_missile"].BlastRadius;
            var layers = new BlastLayers(_materials, _root.transform);
            ExplosionEffect.Create(ExplosionTier.Ultimate, layers).Play(Vector3.zero, 0f, 1f, BlastSizes.Reach(radius));
            layers.Shockwave.Simulate(0.001f, false, false);
            var particles = new ParticleSystem.Particle[8];
            var n = layers.Shockwave.GetParticles(particles);
            Assert.AreEqual(1, n);
            // The ring is drawn at 0.82 of the quad's half size.
            var reach = particles[0].startSize * 0.82f * 0.5f;
            Assert.That(reach, Is.InRange(radius * 0.95f, radius * 1.1f), $"ring reach {reach:F1} m for a {radius} m blast");
        }

        [Test]
        public void AFlameStreamRollsFireballsOntoItsTargetAndSetsItAlight()
        {
            var emitters = new Emitters(_materials, _root.transform);
            emitters.FlameJet(new Vector3(0f, 1.5f, 0f), new Vector3(12f, 0.4f, 0f), 0.35f, 0.25f, 0f);
            for (var t = 0.02f; t < 0.3f; t += 0.02f) emitters.Tick(t, 0.02f);
            foreach (var name in new[] { "Flame Balls", "Flame Rod", "Flame Licks", "Flame Heat", "Damage Smoke" })
            {
                var ps = Layer(name);
                ps.Simulate(0.001f, false, false);
                Assert.Greater(ps.particleCount, 0, name);
            }
            // Flames stand upright on the target (never spun into petals).
            var licks = Layer("Flame Licks");
            var buffer = new ParticleSystem.Particle[64];
            var count = licks.GetParticles(buffer);
            for (var i = 0; i < count; i++)
            {
                var degrees = Mathf.DeltaAngle(0f, buffer[i].rotation);
                Assert.LessOrEqual(Mathf.Abs(degrees), 10f, "a lick of flame is upright");
            }
        }

        [Test]
        public void ALaserHoldsOneBeamWhileItFiresThenFadesOut()
        {
            var emitters = new Emitters(_materials, _root.transform);
            var lasers = new LaserBeams(_materials, emitters, null, _root.transform);
            var from = new Vector3(0f, 3f, 0f);
            for (var shot = 0; shot < 5; shot++)
            {
                var now = shot * 0.1f;
                lasers.Fire(null, 0, from, new Vector3(10f, 12f, 5f), MachineBrigade.Sim.Core.EntityId.None, true, null, now, 0.16f);
                lasers.Tick(now + 0.05f, 0.05f, null);
                Assert.AreEqual(1, lasers.ActiveBeams, "one beam, however many shots");
            }
            Assert.Greater(CountAfterSimulate("Laser Sparks"), 0, "sparks fly off the hit");
            lasers.Tick(0.4f + 0.16f + 0.1f, 0.05f, null);
            Assert.AreEqual(1, lasers.ActiveBeams, "an afterglow once it stops");
            lasers.Tick(1.2f, 0.05f, null);
            Assert.AreEqual(0, lasers.ActiveBeams, "then gone");
        }

        private int CountAfterSimulate(string name)
        {
            var ps = Layer(name);
            ps.Simulate(0.001f, false, false);
            return ps.particleCount;
        }

        private (int count, float size) Fireballs(System.Action play)
        {
            play();
            var ps = Layer("Fireball");
            ps.Simulate(0.001f, false, false);
            // The size range the burst was emitted with (the particles themselves are random within it).
            return (ps.particleCount, ps.main.startSize.constantMax);
        }

        private ParticleSystem Layer(string name) =>
            _root.GetComponentsInChildren<ParticleSystem>(true).First(p => p.name == name);
    }
}
