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
        // Fix pass L7 replaced the tiered p34 banks with the library by size (Resources/Audio/sfx): these follow it; the new
        // rules (surfaces, metal cap, falloff, compressor, size table) are in FixL7AudioTests.

        private static string SfxFolder(string bank) => System.IO.Path.Combine(Application.dataPath, "MachineBrigade", "Resources", "Audio", "sfx", bank);

        [Test]
        public void EveryTieredBankItsWeaponsPlayHasItsClips()
        {
            var c = GameContent.LoadCatalog();
            var missing = new System.Collections.Generic.SortedSet<string>();
            foreach (var w in c.Weapons.Values)
                foreach (var bank in new[] { AudioDirector.ShotBank(w), AudioDirector.ImpactBank(w), SoundLibrary.BlastBank(w, true) })
                    if (bank != null && (!System.IO.Directory.Exists(SfxFolder(bank)) || System.IO.Directory.GetFiles(SfxFolder(bank), "*.ogg").Length == 0))
                        missing.Add(bank + " (" + w.Id + ")");
            foreach (WreckClass k in System.Enum.GetValues(typeof(WreckClass)))
            {
                var bank = AudioDirector.WreckBank(k);
                if (bank != null && !System.IO.Directory.Exists(SfxFolder(bank))) missing.Add(bank);
            }
            foreach (var bank in new[] { "smallarms_cluster", "crash_fall", "crash_impact", "train_horn", "train_rails", "ship_horn", "ship_engine" })
                if (!System.IO.Directory.Exists(SfxFolder(bank))) missing.Add(bank);
            Assert.That(missing, Is.Empty, "missing sound banks (python Tools/sfx/build_sfx.py): " + string.Join(", ", missing));
        }

        [Test]
        public void ShotsAndLandingsPickTheirBankByTierAndRound()
        {
            var c = GameContent.LoadCatalog();
            foreach (var w in c.Weapons.Values)
            {
                var shot = AudioDirector.ShotBank(w);
                if (shot != null && shot.StartsWith("shot_s") && w.Tier >= 0 && w.Tier <= 4 && w.Projectile != ProjectileKind.Bomb)
                    Assert.AreEqual("shot_s" + w.Tier, shot, w.Id);
                var land = AudioDirector.ImpactBank(w);
                if (land == null) continue;
                if (w.DamageType == DamageType.ShapedCharge) Assert.That(land, Does.StartWith("blast_heat_"), w.Id);
                if (w.DamageType == DamageType.Kinetic && w.SplashRadius <= 0f) Assert.Fail(w.Id + ": a kinetic round without a blast plays a hit, not " + land);
            }
            var leviathan = c.Vehicles["leviathan"];
            Assert.AreEqual("blast_he_s406", AudioDirector.ImpactBank(c.Weapons[leviathan.Salvo.Weapon]), "the 406 mm lands as a 406 mm blast");
            Assert.IsNull(AudioDirector.ShotBank(null));
        }

        [Test]
        public void ThePrioritiesFollowThePromptsSevenSteps()
        {
            Assert.Greater(SoundPriority.Warning, SoundPriority.Boss, "warnings over boss / 406 mm");
            Assert.Greater(SoundPriority.Boss, SoundPriority.NearBlast, "boss / 406 mm over near blasts");
            Assert.Greater(SoundPriority.NearBlast, SoundPriority.NearShot, "near blasts over near shots");
            Assert.Greater(SoundPriority.NearShot, SoundPriority.FarBlast, "near shots over far blasts");
            Assert.Greater(SoundPriority.FarBlast, SoundPriority.FarShot, "far blasts over far shots");
            Assert.Greater(SoundPriority.FarShot, SoundPriority.SmallArms, "far shots over small arms");
            Assert.Greater(SoundPriority.SmallArms, SoundPriority.Ambient, "small arms over the environment");
            Assert.AreEqual(SoundPriority.Boss, SoundPriority.For(SizeClass.Super, false, false, false));
            Assert.AreEqual(SoundPriority.Boss, SoundPriority.For(SizeClass.S406, false, true, false));
            Assert.AreEqual(SoundPriority.Boss, SoundPriority.For(SizeClass.S2, true, false, false), "a boss's round");
            Assert.AreEqual(SoundPriority.NearBlast, SoundPriority.For(SizeClass.S3, false, true, true));
            Assert.AreEqual(SoundPriority.FarBlast, SoundPriority.For(SizeClass.S3, false, true, false));
            Assert.AreEqual(SoundPriority.NearShot, SoundPriority.For(SizeClass.S2, false, false, true));
            Assert.AreEqual(SoundPriority.SmallArms, SoundPriority.For(SizeClass.S0, false, false, true));
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
        // -------------------------------------------------------------------------------------------------- L7 wrecks

        [Test]
        public void TheClassTableSortsTheRoster()
        {
            var c = GameContent.LoadCatalog();
            Assert.AreEqual(WreckClass.Tank, WreckClasses.Of(c.Vehicles["main_battle_tank"]));
            Assert.AreEqual(WreckClass.Wheeled, WreckClasses.Of(c.Vehicles["scout_jeep"]));
            Assert.AreEqual(WreckClass.Truck, WreckClasses.Of(c.Vehicles["supply_truck"]));
            Assert.AreEqual(WreckClass.Artillery, WreckClasses.Of(c.Vehicles["wheeled_howitzer"]));
            Assert.AreEqual(WreckClass.Fighter, WreckClasses.Of(c.Vehicles["fighter_jet"]));
            Assert.AreEqual(WreckClass.Helicopter, WreckClasses.Of(c.Vehicles["attack_helicopter"]));
            Assert.AreEqual(WreckClass.BigAircraft, WreckClasses.Of(c.Vehicles["heavy_bomber"]));
            Assert.AreEqual(WreckClass.Ship, WreckClasses.Of(c.Vehicles["sea_corvette"]));
            Assert.AreEqual(WreckClass.Drone, WreckClasses.Of(c.Vehicles["recon_drone"]));
            Assert.IsTrue(WreckClasses.Falls(WreckClass.Helicopter));
            Assert.IsFalse(WreckClasses.Falls(WreckClass.Drone));
        }

        [Test]
        public void WrecksLiveHalfAMinuteBossesLongerAndAboutTwelveStayFull()
        {
            var c = GameContent.LoadCatalog();
            var tank = c.Vehicles["main_battle_tank"];
            Assert.AreEqual(30f, WreckClasses.Life(tank, 0f, GraphicsQuality.High), 1e-4f);
            Assert.AreEqual(45f, WreckClasses.Life(tank, 1f, GraphicsQuality.High), 1e-4f);
            var boss = c.Vehicles.Values.First(v => v.Boss && !v.Static);
            Assert.Greater(WreckClasses.Life(boss, 1f, GraphicsQuality.High), 45f, "bosses longer");
            Assert.Less(WreckClasses.Life(tank, 1f, GraphicsQuality.Low), 45f, "Low graphics shorter");
            Assert.AreEqual(12, WreckClasses.FullCap(GraphicsQuality.High));
            Assert.Less(WreckClasses.FullCap(GraphicsQuality.Low), WreckClasses.FullCap(GraphicsQuality.Medium));
        }

        [Test]
        public void TheModelsHaveTheirSeparableParts()
        {
            // Tools/blender/mb_p34_parts.py: two wheels on the wheeled vehicles, the left wing on the aeroplanes.
            var models = new ModelLibrary(_materials);
            try
            {
                foreach (var (model, part) in new[]
                         {
                             ("scout_jeep", "Part_wheel"), ("scout_jeep", "Part_wheelb"), ("armored_car", "Part_wheel"), ("zu23_technical", "Part_wheelb"),
                             ("fighter_jet", "Part_wing"), ("attack_jet", "Part_wing"), ("heavy_bomber", "Part_wing"), ("stealth_bomber", "Part_wing"),
                             ("attack_helicopter", "Tail_rotor"), ("attack_helicopter", "Rotor"),
                         })
                {
                    Assert.IsTrue(models.Has(model), model);
                    var instance = models.Spawn(model, 0, _root.transform);
                    var found = instance.Root.GetComponentsInChildren<Transform>(true).Any(t => t.name == part);
                    Assert.IsTrue(found, model + " has no " + part);
                }
            }
            finally
            {
                models.Dispose();
            }
        }

        [Test]
        public void ADownedAircraftsLossEventCarriesTheSimsCrashPlan()
        {
            var world = new MachineBrigade.Sim.SimWorld(GameContent.LoadCatalog(), new MachineBrigade.Sim.Content.MapDefinition("field", 160f,
                new[] { new MachineBrigade.Sim.Content.TeamStart(0, new System.Numerics.Vector2(-60f, -60f)),
                        new MachineBrigade.Sim.Content.TeamStart(1, new System.Numerics.Vector2(60f, 60f)) },
                new System.Collections.Generic.List<MachineBrigade.Sim.Content.PropPlacement>(),
                new System.Collections.Generic.List<MachineBrigade.Sim.Content.UnitPlacement>()));
            var heli = world.SpawnVehicle("attack_helicopter", 1, new System.Numerics.Vector2(5f, 0f), 0f);
            world.Step(TestWorlds.Step);
            world.ClearEvents();
            world.Damage.Apply(heli, 1e7f, DamageType.Fragmentation);
            var lost = world.Events.First(e => e.Kind == MachineBrigade.Sim.Events.SimEventKind.VehicleDestroyed && e.Entity == heli.Id);
            Assert.Greater(lost.Value, 0.2f, "the fall's seconds");
            var start = world.Time;
            for (var t = 0f; t < lost.Value + 1f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                {
                    if (e.Kind != MachineBrigade.Sim.Events.SimEventKind.Explosion || e.Entity != heli.Id) continue;
                    Assert.AreEqual(lost.Target.X, e.Position.X, 1e-3f, "the crash lands where the plan said");
                    Assert.AreEqual(lost.Target.Y, e.Position.Y, 1e-3f);
                    Assert.AreEqual(lost.Value, (float)(world.Time - start), TestWorlds.Step * 1.5f, "and when");
                    return;
                }
                world.ClearEvents();
            }
            Assert.Fail("no crash blast");
        }
    }
}
