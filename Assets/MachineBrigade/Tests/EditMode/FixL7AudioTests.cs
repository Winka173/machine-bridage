using System.IO;
using NUnit.Framework;
using MachineBrigade.Game.Audio;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Fix pass L7 (DECISIONS "Sửa lỗi tổng hợp L7 (lead pass, 2026-10-02)", Docs/audio): the sound library by size, hits by
    /// surface (metal only on armour not pierced, rate-capped), the camera-distance falloff, the Effects compressor, and the
    /// analyser's verdicts (no keng outside the armour group; the per-size table rises). Written under the owner's rule of
    /// 30/09 and not run until the test phase.
    /// </summary>
    public class FixL7AudioTests
    {
        private static string Sfx => Path.Combine(Application.dataPath, "MachineBrigade", "Resources", "Audio", "sfx");

        private static string Repo => Path.GetFullPath(Path.Combine(Application.dataPath, ".."));

        [Test]
        public void SizeClassesFollowTheTierAndTheKind()
        {
            var c = GameContent.LoadCatalog();
            foreach (var w in c.Weapons.Values)
            {
                var size = SoundLibrary.SizeOf(w);
                if (w.Projectile == ProjectileKind.Bomb) Assert.AreEqual(SizeClass.Bomb, size, w.Id);
                else if (w.WeaponFamilyId == "cal_406") Assert.AreEqual(SizeClass.S406, size, w.Id);
                else if (w.Tier >= 5) Assert.AreEqual(SizeClass.Super, size, w.Id);
                else if (w.Tier >= 4 && (w.Projectile == ProjectileKind.Rocket || w.Projectile == ProjectileKind.Missile))
                    Assert.AreEqual(SizeClass.S406, size, w.Id + ": a big rocket");
                else if (w.Tier >= 0) Assert.AreEqual((SizeClass)w.Tier, size, w.Id);
            }
            Assert.Less((int)SizeClass.S4, (int)SizeClass.Bomb);
            Assert.Less((int)SizeClass.Bomb, (int)SizeClass.S406);
            Assert.Less((int)SizeClass.S406, (int)SizeClass.Super);
            Assert.Greater(SoundLibrary.Carry(SizeClass.Super), SoundLibrary.Carry(SizeClass.S0), "bigger sounds carry farther");
        }

        [Test]
        public void EveryBankTheRoundsAndHitsPlayIsBuilt()
        {
            var c = GameContent.LoadCatalog();
            var missing = new System.Collections.Generic.SortedSet<string>();
            void Need(string bank, string why)
            {
                if (bank == null) return;
                var dir = Path.Combine(Sfx, bank);
                if (!Directory.Exists(dir) || Directory.GetFiles(dir, "*.ogg").Length == 0) missing.Add(bank + " (" + why + ")");
            }
            foreach (var w in c.Weapons.Values)
            {
                Need(SoundLibrary.ShotBank(w), w.Id);
                Need(SoundLibrary.BlastBank(w), w.Id);
                Need(SoundLibrary.BlastBank(w, true), w.Id + " in the air");
            }
            foreach (HitSurface s in System.Enum.GetValues(typeof(HitSurface)))
                foreach (SizeClass z in System.Enum.GetValues(typeof(SizeClass)))
                    Need(SoundLibrary.HitBank(s, z), s + " " + z);
            foreach (var bank in new[] { "engine_tracked", "engine_wheeled", "engine_heavy", "flare_pop", "warn_whistle", "warn_whistle_big", "blast_air_s1",
                         "blast_he_s1", "blast_he_s2", "blast_he_s3", "blast_he_s4", "blast_he_s406" })
                Need(bank, "the director");
            Assert.That(missing, Is.Empty, "missing sound banks (python Tools/sfx/build_sfx.py): " + string.Join(", ", missing));
        }

        [Test]
        public void MetalIsOnlyForArmourNotPierced()
        {
            foreach (SizeClass z in System.Enum.GetValues(typeof(SizeClass)))
            {
                Assert.That(SoundLibrary.HitBank(HitSurface.Metal, z), Does.StartWith("hit_metal_"));
                foreach (var s in new[] { HitSurface.Ground, HitSurface.Concrete, HitSurface.Pierced })
                    Assert.That(SoundLibrary.HitBank(s, z), Does.Not.Contain("metal"), s + " " + z);
            }
            Assert.AreEqual(HitSurface.Ground, SoundLibrary.SurfaceOf(false, false, false, false, true, 4f, 0f), "nothing struck: the ground");
            Assert.AreEqual(HitSurface.Concrete, SoundLibrary.SurfaceOf(true, false, false, false, true, 1f, 0f), "a prop: concrete");
            Assert.AreEqual(HitSurface.Concrete, SoundLibrary.SurfaceOf(true, true, true, false, true, 1f, 4f), "a fixed defence: concrete");
            Assert.AreEqual(HitSurface.Metal, SoundLibrary.SurfaceOf(true, true, false, false, true, 2f, 4f), "kinetic, not pierced: metal");
            Assert.AreEqual(HitSurface.Pierced, SoundLibrary.SurfaceOf(true, true, false, false, true, 4f, 4f), "kinetic, level with the armour: through");
            Assert.AreEqual(HitSurface.Pierced, SoundLibrary.SurfaceOf(true, true, false, false, true, 4f, 2f), "kinetic over the armour: through");
            Assert.AreEqual(HitSurface.Pierced, SoundLibrary.SurfaceOf(true, true, false, false, false, 1f, 4f), "not kinetic: never metal");
            Assert.AreEqual(HitSurface.Pierced, SoundLibrary.SurfaceOf(true, true, false, true, true, 0f, 4f), "an aircraft's skin: an impact");
            Assert.IsTrue(SoundLibrary.Penetrates(3f, 3f));
            Assert.IsFalse(SoundLibrary.Penetrates(2f, 3f));
        }

        [Test]
        public void KineticRoundsWithoutABlastPlayHitsNotBlasts()
        {
            var c = GameContent.LoadCatalog();
            foreach (var w in c.Weapons.Values)
            {
                if (w.Beam || w.DamageType != DamageType.Kinetic || w.SplashRadius > 0f) continue;
                Assert.IsNull(SoundLibrary.BlastBank(w), w.Id + ": a kinetic round without a blast lands by surface");
            }
        }

        [Test]
        public void TheMetalCapHoldsAMatchWideRate()
        {
            var cap = new MetalCap();
            var taken = 0;
            var last = -10f;
            for (var i = 0; i < 200; i++)
            {
                var now = i * 0.05f;
                if (!cap.TryTake(now)) continue;
                taken++;
                Assert.GreaterOrEqual(now - last, MetalCap.MinGap - 1e-4f, "never two metal hits within the gap");
                last = now;
            }
            Assert.LessOrEqual(taken, (int)(MetalCap.Burst + MetalCap.PerSecond * 10f) + 1, "20 hits a second for 10 s: capped");
            Assert.Greater(taken, 5, "some still play");
        }

        [Test]
        public void TheFalloffFallsWithDistanceAndHeight()
        {
            Assert.AreEqual(1f, SoundLibrary.Falloff(0f, 0f, 100f), 1e-4f);
            Assert.AreEqual(0f, SoundLibrary.Falloff(100f, 20f, 100f), 1e-4f, "nothing at the reach");
            var prev = 2f;
            for (var d = 0f; d <= 100f; d += 5f)
            {
                var g = SoundLibrary.Falloff(d, 30f, 100f);
                Assert.LessOrEqual(g, prev + 1e-5f, "falls with distance at " + d);
                prev = g;
            }
            Assert.Less(SoundLibrary.Falloff(10f, 120f, 150f), SoundLibrary.Falloff(10f, 20f, 150f), "a camera higher up hears less");
        }

        [Test]
        public void TheCompressorTurnsDownOnlyOverItsThreshold()
        {
            Assert.AreEqual(1f, SoundLibrary.CompressorGain(0f), 1e-6f);
            Assert.AreEqual(1f, SoundLibrary.CompressorGain(SoundLibrary.CompressorThreshold), 1e-5f);
            var prevGain = 1f;
            var prevOut = 0f;
            for (var level = 0.05f; level < 3f; level += 0.05f)
            {
                var gain = SoundLibrary.CompressorGain(level);
                Assert.LessOrEqual(gain, prevGain + 1e-6f, "more in, more reduction");
                Assert.Greater(level * gain, prevOut, "louder in is still louder out (a compressor, not a gate)");
                prevGain = gain;
                prevOut = level * gain;
            }
            Assert.Less(SoundLibrary.LimiterCeiling, 1f);
        }

        [Test]
        public void TheEnvelopesParseAndCoverTheLibrary()
        {
            var parsed = SoundLibrary.ParseEnvelopes("# head\nshot_s0_1 100 50 0\n\nblast_super_1 900\n");
            Assert.AreEqual(2, parsed.Count);
            Assert.AreEqual(0.1f, parsed["shot_s0_1"][0], 1e-6f);
            Assert.AreEqual(3, parsed["shot_s0_1"].Length);
            var file = Path.Combine(Sfx, "envelopes.txt");
            Assert.IsTrue(File.Exists(file), "python Tools/sfx/build_sfx.py writes envelopes.txt");
            var all = SoundLibrary.ParseEnvelopes(File.ReadAllText(file));
            foreach (var clip in Directory.GetFiles(Sfx, "*.ogg", SearchOption.AllDirectories))
                Assert.IsTrue(all.ContainsKey(Path.GetFileNameWithoutExtension(clip)), clip + " has an envelope");
        }

        [Test]
        public void TheAnalyserFindsNoKengOutsideArmourAndTheSizesRise()
        {
            var metrics = Path.Combine(Repo, "Docs", "audio", "metrics.json");
            Assert.IsTrue(File.Exists(metrics), "python Tools/sfx/analyze_sfx.py writes Docs/audio/metrics.json");
            var text = File.ReadAllText(metrics);
            Assert.That(text, Does.Contain("\"not_rising\": []"), "the per-size table rises (louder, deeper, longer)");
            Assert.That(text, Does.Contain("\"keng_outside_armour\": []"), "no keng outside the armour-metal group");
        }
    }
}
