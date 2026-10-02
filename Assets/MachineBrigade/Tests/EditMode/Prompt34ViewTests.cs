using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Audio;
using MachineBrigade.Game.Effects;
using MachineBrigade.Game.Match;
using MachineBrigade.Game.Rendering;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 34 L5-L7 (DECISIONS "Prompt 34 L5/L6/L7 (lead pass, 2026-10-02)"): firing and blasts by tier, the concurrency
    /// budget and distance detail, the T4+ camera shake, tiered sounds and their priority, wreck breakup by class and the
    /// crash plan. Written under the owner's rule of 30/09 and not run until the test phase.
    /// </summary>
    public class Prompt34ViewTests
    {
        private MaterialLibrary _materials;
        private GameObject _root;
        private GraphicsQuality _graphics;

        [SetUp]
        public void SetUp()
        {
            _materials = new MaterialLibrary();
            _root = new GameObject("Prompt 34 View Test");
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

        // ------------------------------------------------------------------------------------------------- L5 effects

        [Test]
        public void FullDetailCapsAreThePrompts()
        {
            Assert.AreEqual(1, TierFx.FullCap(5), "T5");
            Assert.That(TierFx.FullCap(4), Is.InRange(2, 3), "T4");
            Assert.That(TierFx.FullCap(3), Is.InRange(4, 6), "T3");
            Assert.AreEqual(int.MaxValue, TierFx.FullCap(2), "T2 and below are not capped");
        }

        [Test]
        public void ABlastOverItsCapStepsDownAndComesBackWhenTheOthersAreDone()
        {
            var budget = new TierBudget();
            Assert.AreEqual(TierFx.Detail.Full, budget.Admit(5, TierFx.Detail.Full, 0f));
            Assert.AreEqual(TierFx.Detail.Reduced, budget.Admit(5, TierFx.Detail.Full, 0.5f), "a second T5 at once");
            // With the T5 going, two T4 fit in full and the third steps down (the weight cap).
            Assert.AreEqual(TierFx.Detail.Full, budget.Admit(4, TierFx.Detail.Full, 0.6f));
            Assert.AreEqual(TierFx.Detail.Full, budget.Admit(4, TierFx.Detail.Full, 0.7f));
            Assert.AreEqual(TierFx.Detail.Reduced, budget.Admit(4, TierFx.Detail.Full, 0.8f));
            // A far blast stays far and a reduced one is not counted.
            Assert.AreEqual(TierFx.Detail.Far, budget.Admit(4, TierFx.Detail.Far, 0.9f));
            Assert.AreEqual(TierFx.Detail.Reduced, budget.Admit(3, TierFx.Detail.Reduced, 0.9f));
            Assert.AreEqual(1, budget.Active(5, 1f));
            // Once they are done, a T5 is full again.
            Assert.AreEqual(TierFx.Detail.Full, budget.Admit(5, TierFx.Detail.Full, 20f));
        }

        [Test]
        public void SixT3BlastsAtOnceAreFullTheSeventhIsNot()
        {
            var budget = new TierBudget();
            for (var i = 0; i < TierFx.FullCap(3); i++) Assert.AreEqual(TierFx.Detail.Full, budget.Admit(3, TierFx.Detail.Full, 0.1f * i), "T3 " + i);
            Assert.AreEqual(TierFx.Detail.Reduced, budget.Admit(3, TierFx.Detail.Full, 0.7f));
        }

        [Test]
        public void DetailFallsWithDistanceAndZoom()
        {
            Assert.AreEqual(TierFx.Detail.Full, TierFx.DetailAt(10f, 20f));
            Assert.AreEqual(TierFx.Detail.Reduced, TierFx.DetailAt(80f, 20f));
            Assert.AreEqual(TierFx.Detail.Far, TierFx.DetailAt(150f, 20f));
            Assert.AreEqual(TierFx.Detail.Reduced, TierFx.DetailAt(40f, 42f), "zoomed right out counts as farther");
            Assert.AreEqual(1f, TierFx.ShareOf(TierFx.Detail.Full));
            Assert.Less(TierFx.ShareOf(TierFx.Detail.Reduced), 1f);
            Assert.AreEqual(0f, TierFx.ShareOf(TierFx.Detail.Far));
        }

        [Test]
        public void OnlyT4AndT5ShakeTheCameraNearAndOnScreen()
        {
            for (var tier = 0; tier <= 3; tier++) Assert.AreEqual(0f, TierFx.Shake(tier, 0f, true), "T" + tier);
            Assert.Greater(TierFx.Shake(4, 0f, true), 0f);
            Assert.Greater(TierFx.Shake(5, 0f, true), TierFx.Shake(4, 0f, true), "T5 strong, T4 light");
            Assert.Greater(TierFx.Shake(5, 5f, true), TierFx.Shake(5, 40f, true), "falls off with distance");
            Assert.AreEqual(0f, TierFx.Shake(5, 10f, false), "not when off screen");
            Assert.AreEqual(0f, TierFx.Shake(5, TierFx.ShakeReach + 1f, true), "not when far");
            Assert.Less(TierFx.Shake(5, 0f, true, shot: true), TierFx.Shake(5, 0f, true), "a shot shakes less than its landing");
            Assert.LessOrEqual(TierFx.ShakeCap, 1f);
        }

        [Test]
        public void EachTierIsRedrawnBiggerThanTheOneBelow()
        {
            var layers = new BlastLayers(_materials, _root.transform);
            var counts = Enumerable.Range(2, 4).Select(t => ExplosionEffect.CreateTier(t, layers).ParticleCount).ToArray();
            for (var i = 1; i < counts.Length; i++) Assert.Greater(counts[i], counts[i - 1], "T" + (i + 2) + " over T" + (i + 1));
            // T5 has its mushroom cap: smoke column billows at the top of the column, round its centre.
            var t5 = ExplosionEffect.CreateTier(5, layers);
            var t4 = ExplosionEffect.CreateTier(4, layers);
            Assert.Greater(t5.ParticleCount, t4.ParticleCount * 1.4f);
            Assert.Greater(t5.ChunkCount, t4.ChunkCount, "T5 throws debris farther and more");
        }

        [Test]
        public void TheOverlayIsSizedToTheRoundsCoreButNeverShrinksBelowItsDesign()
        {
            Assert.AreEqual(1f, TierFx.OverlayScale(5, 14f), 1e-4f, "the 406 mm's 14 m core is the T5 design");
            Assert.AreEqual(0.8f, TierFx.OverlayScale(4, 1f), 1e-4f);
            Assert.AreEqual(1.6f, TierFx.OverlayScale(3, 40f), 1e-4f);
            Assert.AreEqual(1f, TierFx.Extra(2), 1e-4f);
            Assert.Greater(TierFx.Extra(5), TierFx.Extra(4), "the round's own extras grow by tier");
        }

        [Test]
        public void FiringLooksGrowByTier()
        {
            for (var tier = 1; tier <= TierFx.Top; tier++)
            {
                var a = TierFx.FireOf(tier - 1);
                var b = TierFx.FireOf(tier);
                Assert.GreaterOrEqual(b.Puffs, a.Puffs, "puffs T" + tier);
                Assert.GreaterOrEqual(b.PuffLife.y, a.PuffLife.y, "smoke clears slower T" + tier);
                Assert.GreaterOrEqual(b.Flash, a.Flash, "flash T" + tier);
            }
            Assert.Greater(TierFx.FireOf(3).DustRing, 0f, "T3 a dust ring");
            Assert.Greater(TierFx.FireOf(4).Pressure, 0f, "T4 a pressure wave");
            Assert.Greater(TierFx.FireOf(4).Water, 0f, "T4 ships flatten the water");
            Assert.AreEqual(0f, TierFx.FireOf(2).Squat, "T2 only recoils");
            Assert.Greater(TierFx.FireOf(3).Squat, 0f, "T3 the hull squats");
        }

        [Test]
        public void TheBigBossRoundsHaveTheirTiers()
        {
            var c = GameContent.LoadCatalog();
            var leviathan = c.Vehicles["leviathan"];
            Assert.That(leviathan.Salvo?.Weapon, Is.Not.Null, "Leviathan's salvo names its gun");
            Assert.AreEqual(5, TierFx.Of(c.Weapons[leviathan.Salvo.Weapon]), "the 406 mm is T5");
            Assert.AreEqual(-1, TierFx.Of(null));
        }
        // -------------------------------------------------------------------------------------------------- L6 sounds

        private static string P34Folder(string bank) => System.IO.Path.Combine(Application.dataPath, "MachineBrigade", "Resources", "Audio", "p34", bank);

        [Test]
        public void EveryTieredBankItsWeaponsPlayHasItsClips()
        {
            var c = GameContent.LoadCatalog();
            var missing = new System.Collections.Generic.SortedSet<string>();
            foreach (var w in c.Weapons.Values)
                foreach (var bank in new[] { AudioDirector.ShotBank(w), AudioDirector.ImpactBank(w) })
                    if (bank != null && (!System.IO.Directory.Exists(P34Folder(bank)) || System.IO.Directory.GetFiles(P34Folder(bank), "*.ogg").Length == 0))
                        missing.Add(bank + " (" + w.Id + ")");
            foreach (WreckClass k in System.Enum.GetValues(typeof(WreckClass)))
            {
                var bank = AudioDirector.WreckBank(k);
                if (bank != null && !System.IO.Directory.Exists(P34Folder(bank))) missing.Add(bank);
            }
            foreach (var bank in new[] { "smallarms_cluster", "crash_fall", "crash_impact", "train_horn", "train_rails", "ship_horn", "ship_engine" })
                if (!System.IO.Directory.Exists(P34Folder(bank))) missing.Add(bank);
            Assert.That(missing, Is.Empty, "missing sound banks (python Tools/sfx/build_sfx.py): " + string.Join(", ", missing));
        }

        [Test]
        public void ShotsAndLandingsPickTheirBankByTierAndRound()
        {
            var c = GameContent.LoadCatalog();
            foreach (var w in c.Weapons.Values)
            {
                var shot = AudioDirector.ShotBank(w);
                if (shot != null && shot.StartsWith("shot_t")) Assert.AreEqual("shot_t" + System.Math.Min(5, w.Tier), shot, w.Id);
                var land = AudioDirector.ImpactBank(w);
                if (land == null) continue;
                if (w.DamageType == DamageType.ShapedCharge) Assert.AreEqual("blast_heat", land, w.Id);
                if (land.StartsWith("blast_he_")) Assert.AreEqual("blast_he_t" + System.Math.Max(1, System.Math.Min(5, w.Tier)), land, w.Id);
            }
            var leviathan = c.Vehicles["leviathan"];
            Assert.AreEqual("blast_he_t5", AudioDirector.ImpactBank(c.Weapons[leviathan.Salvo.Weapon]), "the 406 mm lands as a T5 blast");
            Assert.IsNull(AudioDirector.ShotBank(null));
        }

        [Test]
        public void ThePrioritiesFollowThePromptsSevenSteps()
        {
            Assert.Greater(SoundPriority.Warning, SoundPriority.Boss, "1 warnings over 2 T5 / boss");
            Assert.Greater(SoundPriority.Boss, SoundPriority.T4Near, "2 over 3 T4 near");
            Assert.Greater(SoundPriority.T4Near, SoundPriority.T3Near, "3 over 4 T3 near");
            Assert.Greater(SoundPriority.T3Near, SoundPriority.Ally, "4 over 5 our important weapons");
            Assert.Greater(SoundPriority.Ally, SoundPriority.SmallArms, "5 over 6 small arms");
            Assert.Greater(SoundPriority.SmallArms, SoundPriority.Ambient, "6 over 7 the environment");
            Assert.AreEqual(SoundPriority.Boss, SoundPriority.For(5, false, false, false, true));
            Assert.AreEqual(SoundPriority.Boss, SoundPriority.For(2, true, false, false, true), "a boss's round");
            Assert.AreEqual(SoundPriority.T4Near, SoundPriority.For(4, false, false, true, true));
            Assert.Less(SoundPriority.For(4, false, false, false, true), SoundPriority.T4Near, "a T4 far off counts less");
            Assert.AreEqual(SoundPriority.Ally, SoundPriority.For(2, false, true, false, true));
            Assert.AreEqual(SoundPriority.SmallArms, SoundPriority.For(0, false, true, true, false));
            Assert.AreEqual(SoundPriority.Warning, SoundPriority.Steps(7));
            Assert.AreEqual(24, AudioDirector.EffectVoices, "about 24 effect voices before cutting by priority");
        }

        [Test]
        public void SmallArmsAreTheStreamingBulletsOnly()
        {
            var c = GameContent.LoadCatalog();
            foreach (var w in c.Weapons.Values)
            {
                if (!AudioDirector.SmallArms(w)) continue;
                Assert.That(w.Tier, Is.LessThanOrEqualTo(1), w.Id);
                Assert.AreEqual(ProjectileKind.Bullet, w.Projectile, w.Id);
                Assert.AreNotEqual(DamageType.Fragmentation, w.DamageType, w.Id + ": flak keeps its own burst");
            }
            Assert.That(AudioDirector.ClusterFrom, Is.GreaterThanOrEqualTo(2));
        }
    }
}
