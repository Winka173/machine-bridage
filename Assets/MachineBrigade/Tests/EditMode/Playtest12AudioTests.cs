using System.IO;
using NUnit.Framework;
using MachineBrigade.Game.Audio;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Play-test 12 audio (lane C; DECISIONS "Play-test 12 audio (lane C)", Docs/audio/pt12.md): machine guns and autocannons
    /// back on yesterday's voice with bursts for rapid fire, flak on its recorded burst, the 57 mm as an autocannon, and the
    /// launches by family (a rocket motor, not a gun). Written under the owner's rule of 30/09 and not run until the test phase.
    /// </summary>
    public class Playtest12AudioTests
    {
        private static string Sfx => Path.Combine(Application.dataPath, "MachineBrigade", "Resources", "Audio", "sfx");

        private static int Clips(string bank)
        {
            var dir = Path.Combine(Sfx, bank);
            return Directory.Exists(dir) ? Directory.GetFiles(dir, "*.ogg").Length : 0;
        }

        [Test]
        public void TheNewBanksAreBuilt()
        {
            foreach (var burst in SoundLibrary.Bursts) Assert.That(Clips(burst.Bank), Is.GreaterThanOrEqualTo(3), burst.Bank);
            foreach (var bank in new[] { "launch_atgm", "launch_sam", "launch_s2", "launch_s3", "launch_big", "launch_cruise", "shot_ac57" })
                Assert.That(Clips(bank), Is.GreaterThanOrEqualTo(3), bank);
            Assert.That(Clips("missile_hiss"), Is.GreaterThanOrEqualTo(2), "missile_hiss");
            Assert.That(Clips("shot_s0"), Is.GreaterThanOrEqualTo(4), "four machine-gun variants");
            Assert.That(Clips("shot_s1"), Is.GreaterThanOrEqualTo(4), "four autocannon variants");
        }

        [Test]
        public void RapidFireGunsPlayBurstsAtTheirOwnRate()
        {
            var c = GameContent.LoadCatalog();
            foreach (var w in c.Weapons.Values)
            {
                var bank = SoundLibrary.BurstBank(w, out var pitch, out var segment);
                var rapid = w.Projectile == ProjectileKind.Bullet && !w.Beam && w.Charge <= 0f && w.Cooldown > 0f &&
                            SoundLibrary.SizeOf(w) <= SizeClass.S1 && 1f / w.Cooldown >= SoundLibrary.BurstFrom;
                if (!rapid)
                {
                    Assert.IsNull(bank, w.Id + ": not rapid fire");
                    continue;
                }
                Assert.IsNotNull(bank, w.Id);
                Assert.That(Clips(bank), Is.GreaterThan(0), bank + " (" + w.Id + ")");
                Assert.That(pitch, Is.InRange(SoundLibrary.BurstPitchMin, SoundLibrary.BurstPitchMax), w.Id);
                Assert.That(segment, Is.InRange(0.2f, 0.45f), w.Id + ": a segment is about a third of a second");
            }
            Assert.AreEqual("burst_s0_55", SoundLibrary.BurstBank(c.Weapons["minigun"], out _, out _));
            Assert.AreEqual("burst_s1_55", SoundLibrary.BurstBank(c.Weapons["gau_gatling"], out _, out _));
            Assert.That(SoundLibrary.BurstBank(c.Weapons["mg_coax"], out _, out _), Does.StartWith("burst_s0_"));
            Assert.IsNull(SoundLibrary.BurstBank(c.Weapons["autocannon_30"], out _, out _), "a slow autocannon plays a clip a round");
            Assert.That(AudioDirector.BurstVoices, Is.InRange(2, 4));
        }

        [Test]
        public void FlakAndThe57mmKeepTheirOwnSounds()
        {
            var c = GameContent.LoadCatalog();
            Assert.IsNull(SoundLibrary.ShotBank(c.Weapons["flak_35"]), "flak plays the recorded flak burst (the old category)");
            Assert.IsNull(SoundLibrary.ShotBank(c.Weapons["bofors_l70"]), "flak plays the recorded flak burst (the old category)");
            Assert.AreEqual("shot_ac57", SoundLibrary.ShotBank(c.Weapons["gun_57_auto"]));
        }

        [Test]
        public void MissilesLaunchAsRocketMotorsByFamily()
        {
            var c = GameContent.LoadCatalog();
            Assert.AreEqual("launch_atgm", SoundLibrary.ShotBank(c.Weapons["atgm"]));
            Assert.AreEqual("launch_sam", SoundLibrary.ShotBank(c.Weapons["sam"]));
            Assert.AreEqual("launch_s2", SoundLibrary.ShotBank(c.Weapons["heli_rockets"]));
            Assert.AreEqual("launch_s3", SoundLibrary.ShotBank(c.Weapons["grad_rockets"]));
            Assert.AreEqual("launch_big", SoundLibrary.ShotBank(c.Weapons["mlrs_rockets"]));
            Assert.AreEqual("launch_cruise", SoundLibrary.ShotBank(c.Weapons["jassm"]));
            foreach (var w in c.Weapons.Values)
            {
                if (w.Projectile != ProjectileKind.Missile && w.Projectile != ProjectileKind.Rocket) continue;
                var shot = SoundLibrary.ShotBank(w);
                if (SoundLibrary.SizeOf(w) <= SizeClass.S1) Assert.IsNull(shot, w.Id);
                else Assert.That(shot, Does.StartWith("launch_"), w.Id + ": a launch, never a gun's shot");
            }
        }

        [Test]
        public void TheGunsTheOwnerLikesKeepTheirBanks()
        {
            var c = GameContent.LoadCatalog();
            foreach (var w in c.Weapons.Values)
            {
                if (w.Beam || w.Projectile is ProjectileKind.Bullet or ProjectileKind.Rocket or ProjectileKind.Missile or ProjectileKind.Flame
                        or ProjectileKind.Drone or ProjectileKind.Bomb) continue;
                Assert.That(SoundLibrary.ShotBank(w), Does.StartWith("shot_s"), w.Id + ": tank guns and artillery keep the L7 library");
            }
        }
    }
}
