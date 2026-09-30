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
    /// held laser beams. The second play test's (12C): every blast a tenth bigger, drones by the
    /// drone, tank rounds lingering by the tank's class. Play-test 5's (20V) on top: tank rounds +20 % wide
    /// and long, artillery, mortars, missiles, rockets and drones +20 %, the gun turret +30 %.
    /// </summary>
    public class BlastSizeTests
    {
        private MaterialLibrary _materials;
        private GameObject _root;
        private GraphicsQuality _graphics;

        [SetUp]
        public void SetUp()
        {
            _materials = new MaterialLibrary();
            _root = new GameObject("Blast Size Test");
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
        public void TankRoundsAndBombsGrowByWhatFiredThem()
        {
            var catalog = GameContent.LoadCatalog();
            Assert.AreEqual(1.3f * 1.2f, BlastSizes.TankShell(catalog.Weapons["gun_57mm"]), 1e-4f, "light tank");
            Assert.AreEqual(1.4f * 1.2f, BlastSizes.TankShell(catalog.Weapons["gun_120mm"]), 1e-4f, "main battle tank");
            Assert.AreEqual(1.5f * 1.2f, BlastSizes.TankShell(catalog.Weapons["gun_152"]), 1e-4f, "heavy tank");
            Assert.AreEqual(1.5f * 1.2f, BlastSizes.TankShell(catalog.Weapons["gun_140_twin"]), 1e-4f, "super-heavy tank");
            Assert.AreEqual(1.4f * 1.3f * 1.2f, BlastSizes.TankShell(catalog.Weapons["turret_gun_120"]), 1e-4f, "the gun turret +30 %, then +20 % (play-test 6)");
            Assert.AreEqual(0.8f, BlastSizes.Round(catalog.Weapons["gun_155_twin_fort"]) / (catalog.Weapons["gun_155_twin_fort"].Indirect ? 1.2f : 1f), 1e-4f,
                "the heavy fortress's blasts 20 % smaller (play-test 6)");
            Assert.AreEqual(1.3f * 1.2f, BlastSizes.Round(catalog.Weapons["gun_57_auto"]), 1e-4f, "the gun turret's autocannon branch +30 %, then +20 % (play-test 6)");
            Assert.AreEqual(1.5f * 1.2f, BlastSizes.Ground(catalog.Weapons["gun_203_siege"]), 1e-4f, "siege tank");
            Assert.AreEqual(1f, BlastSizes.Ground(catalog.Weapons["howitzer"]), 1e-4f, "other artillery: not a bomb");
            Assert.AreEqual(1.2f, BlastSizes.Artillery(catalog.Weapons["howitzer"]), 1e-4f, "artillery +20 %");
            Assert.AreEqual(1.2f, BlastSizes.Round(catalog.Weapons["mortar_120"]), 1e-4f, "mortar +20 %");
            Assert.AreEqual(1.2f, BlastSizes.Round(catalog.Weapons["atgm"]), 1e-4f, "missile +20 %");
            Assert.AreEqual(1.2f, BlastSizes.Round(catalog.Weapons["grad_rockets"]), 1e-4f, "rocket +20 %");
            Assert.AreEqual(1f, BlastSizes.Round(catalog.Weapons["hmg_roof"]), 1e-4f, "bullets as they were");
            Assert.Less(BlastSizes.Bomb("guided_bomb"), BlastSizes.Bomb("jet_bombs"), "a small guided bomb grows less than a FAB");
            foreach (var id in new[] { "guided_bomb", "jet_bombs", "bomber_payload", "stealth_payload", "airstrike", "cluster_strike" })
                Assert.That(BlastSizes.Bomb(id), Is.InRange(1.3f, 1.5f), id);
            Assert.AreEqual(1.2f, BlastSizes.Strike(catalog.Supports["artillery_barrage"]), 1e-4f, "a barrage is shells, not bombs: +20 %");
        }

        [Test]
        public void TankRoundsLingerByTheTanksClassAndDronesGrowByTheDrone()
        {
            var w = GameContent.LoadCatalog().Weapons;
            foreach (var id in new[] { "gun_57mm", "gun_105_wheeled" })
                Assert.AreEqual(1.2f * 1.2f, BlastSizes.ShellLife(w[id]), 1e-4f, id + ": light tank and wheeled gun +20 %, +20 % again");
            foreach (var id in new[] { "gun_120mm", "gun_105_long", "gun_105_apfsds", "gun_105_twin", "gun_125_elite" })
                Assert.AreEqual(1.25f * 1.2f, BlastSizes.ShellLife(w[id]), 1e-4f, id + ": main battle tank, tank destroyers, twin +25 %, +20 % again");
            Assert.AreEqual(1.25f, BlastSizes.ShellLife(w["turret_gun_120"]), 1e-4f, "the 120 mm turret +25 % (not a tank)");
            foreach (var id in new[] { "gun_152", "gun_152_heat", "gun_140_twin", "gun_203_siege" })
                Assert.AreEqual(1.3f * 1.2f, BlastSizes.ShellLife(w[id]), 1e-4f, id + ": heavy, elite heavy, titan, siege +30 %, +20 % again");
            Assert.AreEqual(1.3f * 1.2f, BlastSizes.GroundLife(w["gun_203_siege"]), 1e-4f, "the siege tank's shell lands lingering");
            Assert.AreEqual(1f, BlastSizes.GroundLife(w["howitzer"]), 1e-4f, "other artillery as it was");

            Assert.AreEqual(1.2f * 1.2f, BlastSizes.Drone(w["fpv_swarm"]), 1e-4f, "FPV");
            Assert.AreEqual(1.2f * 1.2f, BlastSizes.Drone(w["fpv_hangar"]), 1e-4f, "the hangar's FPVs");
            Assert.AreEqual(1.25f * 1.2f, BlastSizes.Drone(w["lancet"]), 1e-4f, "Lancet");
            Assert.AreEqual(1.25f * 1.2f, BlastSizes.Drone(w["mothership_drones"]), 1e-4f, "the mothership's drones");
            Assert.AreEqual(1.3f * 1.2f, BlastSizes.Drone(w["shahed"]), 1e-4f, "Shahed");
            Assert.AreEqual(1.3f * 1.2f, BlastSizes.Drone(w["drone_missile"]), 1e-4f, "the strike drone's missiles");
            Assert.IsTrue(BlastSizes.Fpv(w["fpv_swarm"]) && !BlastSizes.Fpv(w["lancet"]) && !BlastSizes.Fpv(w["shahed"]), "FPVs told apart");

            Assert.AreEqual(1f, BlastSizes.Drone(w["atgm"]), 1e-4f, "a plain missile only gets the general tenth");
            Assert.AreEqual(1.1f, BlastSizes.Bigger, 1e-4f);
        }

        [Test]
        public void ALingeringShellHitKeepsItsFireAndSmokeLongerButItsFlashAndSparksQuick()
        {
            var layers = new BlastLayers(_materials, _root.transform);
            var hit = ExplosionEffect.CreateShellHit(layers);
            var lingering = new[] { "Hot Fireball", "Rolling Fireball", "Smoke", "Dust", "Embers" };
            var quick = new[] { "Flash", "Sparks", "Air Shock", "Ground Light" };
            var before = Lifetimes(hit, 1f, lingering, quick);

            var after = Lifetimes(hit, 1.3f, lingering, quick);
            foreach (var name in lingering) Assert.AreEqual(before[name] * 1.3f, after[name], 1e-3f, name + " lives 30 % longer on High");
            foreach (var name in quick) Assert.AreEqual(before[name], after[name], 1e-5f, name + " stays as quick");

            MatchSettings.Graphics = GraphicsQuality.Low;
            var low = Lifetimes(hit, 1.3f, lingering, quick);
            foreach (var name in lingering)
            {
                Assert.AreEqual(before[name] * (1f + 0.3f * 0.4f), low[name], 1e-3f, name + " lingers less on Low");
                Assert.Greater(low[name], before[name], name + " still longer on Low");
            }
            // Low's cost in particle-seconds: more than before, less than High.
            var (lingerLow, _) = hit.ParticleSecondsAt(1.65f, 1.3f, 0.4f);
            var (lingerHigh, _) = hit.ParticleSecondsAt(1.65f, 1.3f);
            var (lingerOld, _) = hit.ParticleSecondsAt(1.5f, 1f, 0.4f);
            Assert.Less(lingerLow, lingerHigh);
            Assert.Greater(lingerLow, lingerOld);
        }

        [Test]
        public void EveryBlastIsATenthBiggerButAMatchedRingStaysOnItsRadius()
        {
            var catalog = GameContent.LoadCatalog();
            var radius = catalog.Supports["moab"].BlastRadius;
            var layers = new BlastLayers(_materials, _root.transform);
            var blast = ExplosionEffect.Create(ExplosionTier.Ultimate, layers);
            var reach = BlastSizes.Reach(radius);
            blast.Play(Vector3.zero, 0f, 1f, reach);
            var flash = layers.Flash.main.startSize.constantMax;
            var ring = layers.Shockwave.main.startSize.constantMax;
            layers.Clear();
            blast.Play(Vector3.zero, 0f, 1f, reach * BlastSizes.Bigger, 1f, reach);
            Assert.AreEqual(flash * 1.1f, layers.Flash.main.startSize.constantMax, 1e-3f, "the flash a tenth bigger");
            Assert.AreEqual(ring, layers.Shockwave.main.startSize.constantMax, 1e-3f, "the ground ring still on the radius");
            foreach (ExplosionTier tier in System.Enum.GetValues(typeof(ExplosionTier)))
            {
                var e = ExplosionEffect.Create(tier, layers);
                Assert.GreaterOrEqual(e.ParticleCountAt(BlastSizes.Bigger, 0.4f), e.CoreParticleCount, tier + ": a tenth bigger never loses any of its old recipe");
            }
        }

        private System.Collections.Generic.Dictionary<string, float> Lifetimes(ExplosionEffect blast, float life, string[] lingering, string[] quick)
        {
            var layers = _root.GetComponentsInChildren<ParticleSystem>(true);
            foreach (var ps in layers) ps.Clear(true);
            blast.Play(Vector3.zero, 0f, 1f, 1.5f, life);
            blast.Tick(5f);
            var result = new System.Collections.Generic.Dictionary<string, float>();
            foreach (var name in lingering.Concat(quick)) result[name] = Layer(name).main.startLifetime.constantMax;
            return result;
        }

        [Test]
        public void AnEnlargedBlastKeepsEveryParticleOfItsRecipeOnEveryTier()
        {
            var layers = new BlastLayers(_materials, _root.transform);
            foreach (ExplosionTier tier in System.Enum.GetValues(typeof(ExplosionTier)))
            {
                var blast = ExplosionEffect.Create(tier, layers);
                Assert.AreEqual(blast.ParticleCount, blast.ParticleCountAt(1f), tier + ": grow 1 is the old blast");
                Assert.GreaterOrEqual(blast.ParticleCountAt(1.5f, 0.4f), blast.CoreParticleCount, tier + ": Low never loses any of the old recipe");
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
        public void EverySplashWeaponsBlastIsDrawnAsWideAsItsDamageReaches()
        {
            // Prompt 25 A5 (DECISIONS 25A): the blast on screen is the damage radius. EffectsDirector draws a round's blast
            // with its splash radius: the recipe's ring (the ground shockwave, or the air ring in the air and on a shell
            // striking armour) at BlastSizes.RingFor(radius, RingReach, scale), whatever the blast's grow; a blast with no
            // ring of its own (the Small tier: flak, grenades) a lone ring of BlastSizes.RingQuad(radius). Every one reaches
            // the radius, at the scales the director draws with (a tenth either way, 0.8 for a HEAT or drone strike).
            var catalog = GameContent.LoadCatalog();
            var layers = new BlastLayers(_materials, _root.transform);
            var recipes = new System.Collections.Generic.Dictionary<ExplosionTier, ExplosionEffect>();
            foreach (ExplosionTier tier in System.Enum.GetValues(typeof(ExplosionTier))) recipes[tier] = ExplosionEffect.Create(tier, layers);
            var airburst = ExplosionEffect.CreateAirburst(layers);
            var shellHit = ExplosionEffect.CreateShellHit(layers);
            var failures = new System.Collections.Generic.List<string>();
            var checkedCount = 0;
            foreach (var w in catalog.Weapons.Values.Where(w => w.SplashRadius > 0f))
            {
                var r = w.SplashRadius;
                var drawn = new System.Collections.Generic.List<(string name, ExplosionEffect fx)>
                    { ("its tier", recipes[w.ImpactTier]), ("a medium blast", recipes[ExplosionTier.Medium]) };
                if ((w.Targets & TargetLayers.Air) != 0) drawn.Add(("an air burst", airburst));
                if (w.Projectile == ProjectileKind.Shell && w.PiercingLook) drawn.Add(("a shell hit", shellHit));
                foreach (var (name, fx) in drawn)
                foreach (var scale in new[] { w.ImpactScale * 0.85f, w.ImpactScale * 1.2f, 0.8f * w.ImpactScale })
                {
                    checkedCount++;
                    float reach;
                    if (fx.RingLayer == null) reach = BlastSizes.RingQuad(r) * BlastSizes.RingShare;
                    else
                    {
                        layers.Clear();
                        fx.Play(Vector3.zero, 0f, scale, 1.5f, 1f, BlastSizes.RingFor(r, fx.RingReach, scale));
                        var size = fx.RingLayer.main.startSize;
                        reach = (size.constantMin + size.constantMax) * 0.5f * BlastSizes.RingShare;
                    }
                    if (Mathf.Abs(reach - r) > 0.01f * r) failures.Add($"{w.Id} as {name} at scale {scale:0.00}: its ring reaches {reach:0.00} m, its blast {r} m");
                }
            }
            Assert.IsEmpty(failures, string.Join("\n", failures));
            Assert.Greater(checkedCount, 200, "every splash weapon, on every recipe it is drawn with");
        }

        [Test]
        public void ACruiseMissilesShockwaveReachesItsBlastRadius()
        {
            var catalog = GameContent.LoadCatalog();
            var radius = catalog.Supports["cruise_missile"].BlastRadius;
            var layers = new BlastLayers(_materials, _root.transform);
            // As EffectsDirector draws it since 12C: the blast a tenth bigger, its ring kept on the radius.
            var grow = BlastSizes.Reach(radius);
            ExplosionEffect.Create(ExplosionTier.Ultimate, layers).Play(Vector3.zero, 0f, 1f, grow * BlastSizes.Bigger, 1f, grow);
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

        [Test]
        public void EachFireSupportCardBringsItsOwnRoundDown()
        {
            var catalog = GameContent.LoadCatalog();
            var meshes = new MeshLibrary();
            var models = new ModelLibrary(_materials);
            try
            {
                var emitters = new Emitters(_materials, _root.transform);
                var strikes = new StrikeEffects(catalog, _materials, meshes, models, emitters, new ProjectilePool(_root.transform, 16), new SmokeScreens(),
                    _root.transform);
                var land = Vector3.zero;
                var from = land + Vector3.left * 24f + Vector3.up * 58f;
                // Smoke shells, mine rockets and the SEAD missile are their own rounds, not the barrage's glowing HE shell.
                foreach (var id in new[] { "smoke_screen", "remote_mines", "sead_strike" })
                    Assert.IsTrue(strikes.Inbound(catalog.Supports[id], Vector3.left, from, land, 0.9f, 0f), id + " draws its own round");
                Assert.IsFalse(strikes.Inbound(catalog.Supports["artillery_barrage"], Vector3.left, from, land, 0.9f, 0f),
                    "a barrage keeps its glowing HE shell (with the shell inside)");
                var rounds = _root.transform.Find("Strikes");
                var before = rounds.childCount;
                // Napalm canisters, cluster dispensers and bomblets, the MOAB, the EMP warhead, the repair crate, the airlift.
                foreach (var id in new[] { "napalm_strike", "cluster_strike", "moab", "emp_blast", "repair_drop", "reinforcements" })
                {
                    var count = rounds.childCount;
                    strikes.Warned(catalog.Supports[id], 0, land, land + Vector3.right * 50f, 3f, 0f);
                    Assert.Greater(rounds.childCount, count, id + " comes down as something of its own");
                }
                // They fall and are cleared away once down.
                for (var t = 0f; t < 20f; t += 0.1f) strikes.Tick(t);
                Assert.LessOrEqual(rounds.childCount, before + 4, "rounds are cleared once they land (aircraft stay pooled)");
            }
            finally
            {
                // (MeshLibrary.Dispose destroys in play mode only; its few meshes are left to the editor.)
                models.Dispose();
            }
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
