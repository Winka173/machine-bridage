using System.Collections.Generic;
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
    /// Prompt 34 L8 (DECISIONS "Prompt 34 L8 / L9 (lead pass, 2026-10-02)"): every preview stands its unit in its own setting
    /// (ground, sea, water's edge, track, air, base pad, coast), the range's ships keep their hull on the water, the preview's
    /// rings. Written under the owner's rule of 30/09 and not run until the test phase.
    /// </summary>
    public class Prompt34PreviewTests
    {
        private static Catalog C => GameContent.LoadCatalog();

        /// <summary>The domain the unit's data says, read independently of <see cref="PreviewSettings"/>'s order.</summary>
        private static PreviewDomain Expected(VehicleDef v)
        {
            if (v.Flying) return PreviewDomain.Air;
            if (v.Frame?.Move == BossMove.Rail || v.RouteName == "rail") return PreviewDomain.Rail;
            if (v.Naval != null || v.Frame?.Move is BossMove.Ship or BossMove.Submarine) return PreviewDomain.Water;
            if (PreviewSettings.Amphibious.Contains(v.Id) || v.Id.Contains("boat") || v.Id.Contains("hover")) return PreviewDomain.Water;
            return PreviewDomain.Ground;
        }

        [Test]
        public void EveryRosterUnitHasAPreviewOfItsDomain()
        {
            var wrong = new List<string>();
            var seen = new HashSet<PreviewDomain>();
            foreach (var v in C.Vehicles.Values)
            {
                var got = PreviewSettings.Domain(v);
                seen.Add(got);
                if (got != Expected(v)) wrong.Add(v.Id + ": " + got + ", expected " + Expected(v));
            }
            Assert.That(wrong, Is.Empty, string.Join("\n", wrong));
            Assert.That(seen.Count, Is.EqualTo(4), "ground, water, rail and air units all exist");
        }

        [Test]
        public void TheNamedUnitsStandInThePromptsSettings()
        {
            var c = C;
            void Check(string id, PreviewSetting setting)
            {
                if (!c.Vehicles.TryGetValue(id, out var v)) Assert.Fail(id + " is not in the roster");
                Assert.AreEqual(setting, PreviewSettings.Of(v), id);
            }
            foreach (var rail in new[] { "armored_train", "nuke_train", "rail_supergun" }) Check(rail, PreviewSetting.Rail);
            foreach (var sea in new[] { "leviathan", "typhon", "caspian", "scylla", "sea_corvette", "sea_cruiser", "missile_boat", "river_patrol_boat", "river_gunboat" })
                Check(sea, PreviewSetting.Sea);
            foreach (var edge in new[] { "amphib_light_vehicle", "hover_gunboat", "landing_hovercraft" }) Check(edge, PreviewSetting.WaterEdge);
            foreach (var air in new[] { "mega_gunship", "drone_mothership", "command_airship", "sky_fortress", "silver_bug", "attack_helicopter" })
                Check(air, PreviewSetting.Air);
            Check("main_battle_tank", PreviewSetting.Ground);
            Check("behemoth", PreviewSetting.Ground);
            Check("kronos", PreviewSetting.Ground);
            Check("coastal_battery", PreviewSetting.Coast);
            Check("heavy_turret", PreviewSetting.BasePad);
        }

        [Test]
        public void EveryTowerStandsOnABasePad()
        {
            foreach (var v in C.Vehicles.Values.Where(v => v.Static && !v.Boss && !v.NavalOnly && !v.Flying))
                Assert.AreEqual(PreviewSetting.BasePad, PreviewSettings.Of(v), v.Id);
        }

        [Test]
        public void ARangeShipKeepsItsHullOnTheWater()
        {
            foreach (var v in C.Vehicles.Values.Where(v => PreviewSettings.Of(v) == PreviewSetting.Sea && v.Mounts.Any(m => m.Weapon.Damage > 0f)))
            {
                var d = PreviewSettings.SeaDistance(v, FiringRange.TargetDistance(v));
                float start = -d * 0.5f, far = d * 0.5f;
                var shore = PreviewStage.ShoreForSea(start, far, v.Length);
                var reach = v.Mounts.Where(m => m.Weapon.Damage > 0f).Max(m => m.Weapon.Range);
                // Either the bow is on the water, or the targets already stand at most of the ship's longest reach.
                Assert.That(start + v.Length * 0.5f <= shore + 0.01f || d >= reach * 0.9f - 0.01f, Is.True, v.Id);
                Assert.That(d, Is.GreaterThanOrEqualTo(FiringRange.TargetDistance(v)), v.Id + ": never nearer than the plain range");
            }
        }

        [Test]
        public void ACoastalGunGetsAShipForItsTarget()
        {
            var c = C;
            Assert.That(c.Vehicles.TryGetValue(FiringRange.ShipTarget, out var ship), Is.True);
            Assert.That(ship.Naval, Is.Not.Null, "the coastal gun fires on ships only");
        }

        [Test]
        public void PreviewRingsAreTheBlastsAndLeaveTheBossWarningsAlone()
        {
            var c = C;
            var shell = c.Weapons.Values.First(w => w.SplashRadius > 0f && !w.Guided && !w.Laid && w.WarnSeconds <= 0f && w.SplashRadius < 5f);
            Assert.That(EffectsDirector.PreviewRingFor(shell, false), Is.True, shell.Id);
            Assert.That(EffectsDirector.PreviewRingFor(shell, true), Is.True, shell.Id + ": a small boss round has no warning of its own");
            var guided = c.Weapons.Values.First(w => w.Guided && w.SplashRadius > 0f);
            Assert.That(EffectsDirector.PreviewRingFor(guided, false), Is.False, guided.Id + ": no fixed fall point");
            var big = c.Weapons.Values.FirstOrDefault(w => w.WarnSeconds > 0f && !w.Guided && !w.Laid && w.SplashRadius > 0f);
            if (big != null)
            {
                Assert.That(EffectsDirector.PreviewRingFor(big, true), Is.False, big.Id + ": the boss's escape warning draws it");
                Assert.That(EffectsDirector.PreviewRingFor(big, false), Is.True, big.Id);
            }
            var plain = c.Weapons.Values.First(w => w.SplashRadius <= 0f && w.Cluster == null);
            Assert.That(EffectsDirector.PreviewRingFor(plain, false), Is.False, plain.Id + ": no blast, no ring");
        }

        // ------------------------------------------------------------------------------------------------ the stages

        private MaterialLibrary _materials;
        private GameObject _root;

        [SetUp]
        public void SetUp()
        {
            _materials = new MaterialLibrary();
            _root = new GameObject("Prompt 34 Preview Test");
        }

        [TearDown]
        public void TearDown()
        {
            Object.DestroyImmediate(_root);
            _materials.Dispose();
        }

        private static HashSet<string> Pieces(PreviewStage stage)
        {
            var names = new HashSet<string>();
            foreach (Transform t in stage.Root) names.Add(t.name);
            return names;
        }

        [Test]
        public void EachRangeSettingBuildsItsPieces()
        {
            var expected = new Dictionary<PreviewSetting, string[]>
            {
                [PreviewSetting.Ground] = new[] { PreviewStage.GroundName },
                [PreviewSetting.Air] = new[] { PreviewStage.GroundName },
                [PreviewSetting.Sea] = new[] { PreviewStage.WaterName, PreviewStage.GroundName, PreviewStage.ShoreName },
                [PreviewSetting.WaterEdge] = new[] { PreviewStage.WaterName, PreviewStage.GroundName, PreviewStage.ShoreName },
                [PreviewSetting.Rail] = new[] { PreviewStage.GroundName, PreviewStage.RailName, PreviewStage.SleeperName },
                [PreviewSetting.BasePad] = new[] { PreviewStage.GroundName, PreviewStage.PadName },
                [PreviewSetting.Coast] = new[] { PreviewStage.GroundName, PreviewStage.WaterName, PreviewStage.PadName },
            };
            foreach (var kv in expected)
            {
                var setting = kv.Key;
                var pieces = kv.Value;
                var stage = PreviewStage.ForRange(_materials, _root.transform, setting, "temperate", -20f, 20f, 10f, 4f);
                try
                {
                    var names = Pieces(stage);
                    foreach (var p in pieces) Assert.That(names.Contains(p), Is.True, setting + " has " + p);
                    Assert.That(names.Contains(PreviewStage.WaterName), Is.EqualTo(pieces.Contains(PreviewStage.WaterName)), setting + ": water only where it belongs");
                    Assert.That(names.Contains(PreviewStage.RailName), Is.EqualTo(setting == PreviewSetting.Rail), setting + ": a track only for a train");
                }
                finally
                {
                    stage.Dispose();
                }
            }
        }

        [Test]
        public void EachTurntableSettingBuildsItsPieces()
        {
            foreach (PreviewSetting setting in System.Enum.GetValues(typeof(PreviewSetting)))
            {
                var stage = PreviewStage.ForTurntable(_materials, _root.transform, setting, "desert", new Vector3(2f, 1.2f, 4f), 0.4f,
                    setting == PreviewSetting.Air ? 6f : 0f);
                try
                {
                    var names = Pieces(stage);
                    var water = setting is PreviewSetting.Sea or PreviewSetting.WaterEdge or PreviewSetting.Coast;
                    Assert.That(names.Contains(PreviewStage.WaterName), Is.EqualTo(water), setting + " water");
                    Assert.That(names.Contains(PreviewStage.RailName), Is.EqualTo(setting == PreviewSetting.Rail), setting + " track");
                    Assert.That(names.Contains(PreviewStage.PadName), Is.EqualTo(setting is PreviewSetting.BasePad or PreviewSetting.Coast), setting + " pad");
                    Assert.That(stage.Radius, Is.GreaterThan(4f), setting + " reaches past the model");
                }
                finally
                {
                    stage.Dispose();
                }
            }
        }

        [Test]
        public void AnAircraftsGroundLiesBelowIt()
        {
            var stage = PreviewStage.ForTurntable(_materials, _root.transform, PreviewSetting.Air, "temperate", new Vector3(3f, 1f, 4f), 0f, 7f);
            try
            {
                var ground = stage.Root.Find(PreviewStage.GroundName).GetComponent<MeshFilter>().sharedMesh;
                Assert.That(ground.bounds.max.y, Is.LessThan(-6f), "the ground is the lift below the model's foot");
            }
            finally
            {
                stage.Dispose();
            }
        }

        [Test]
        public void TheSeaHasWavesThatMove()
        {
            var stage = PreviewStage.ForRange(_materials, _root.transform, PreviewSetting.Sea, "harbor", -25f, 25f, 30f, 8f);
            try
            {
                var water = stage.Root.Find(PreviewStage.WaterName).GetComponent<MeshFilter>().sharedMesh;
                stage.Tick(0f);
                var before = water.vertices.Select(v => v.y).ToArray();
                stage.Tick(1.7f);
                var after = water.vertices.Select(v => v.y).ToArray();
                Assert.That(before.Zip(after, (a, b) => Mathf.Abs(a - b)).Max(), Is.GreaterThan(0.01f), "the swell moves");
                Assert.That(after.Max(), Is.LessThanOrEqualTo(PreviewStage.SeaLevel + PreviewStage.WaveHeight + 0.001f));
                Assert.That(after.Min(), Is.GreaterThanOrEqualTo(PreviewStage.SeaLevel - PreviewStage.WaveHeight - 0.001f));
            }
            finally
            {
                stage.Dispose();
            }
        }

        [Test]
        public void TheBiomeIsTheChosenMapsOrTheDefault()
        {
            var map = MatchSettings.Map;
            try
            {
                MatchSettings.Map = "no_such_map";
                Assert.AreEqual(MatchSettings.AllMaps[0].Theme, PreviewSettings.Biome());
                MatchSettings.Map = MatchSettings.AllMaps[0].Id;
                Assert.AreEqual(MatchSettings.AllMaps[0].Theme, PreviewSettings.Biome());
            }
            finally
            {
                MatchSettings.Map = map;
            }
        }
    }
}
