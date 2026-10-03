using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Navigation;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 33 L3 (DECISIONS "Prompt 33 L2 / L3"): the terrain tags and the landmarks. A road speeds a vehicle up, shallow
    /// water slows an ordinary one but not an amphibious one, a forest hides a vehicle from farther off; the tags are static
    /// (the same route twice); every map file's zones are valid (no overlap, none empty); every battlefield has 2-3 landmarks
    /// with both names; the role-asymmetric files say why. Written for the lead to run (the owner's rule: agents write tests,
    /// they do not run them).
    /// </summary>
    public class Prompt33TerrainTests
    {
        private const float Dt = 0.05f;
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static readonly string[] Battlefields =
        {
            "ashfield", "borderbridge", "capital", "coralisles", "dunebreak", "emberridge", "foundry", "frostpeak", "greenvale", "hydrodam",
            "ironport", "junglepass", "landingbeach", "launchsite", "lighthousebay", "metrocity", "openpit", "orbitalgate", "redrock", "rustyard",
            "saltflat", "skyhold", "swamp", "veyra_old_quarter", "whiteout",
        };

        /// <summary>A plain 300 m field; with a tag, a 40 m wide band of it along z = 0 right across.</summary>
        private static SimWorld Field(TerrainTag? tag)
        {
            var map = new MapDefinition("terrain_field", 300f,
                new[] { new TeamStart(0, new Vector2(-108.75f, -108.75f)), new TeamStart(1, new Vector2(108.75f, 108.75f)) },
                new List<PropPlacement>(), new List<UnitPlacement>());
            if (tag is { } t) map.TerrainZones = new[] { new TerrainZoneDef(t, new Vector2(-150f, -20f), new Vector2(150f, 20f)) };
            return new SimWorld(Catalog, map, 1);
        }

        private static void Run(SimWorld world, float seconds)
        {
            for (var t = 0; t < (int)(seconds / Dt); t++)
            {
                world.Step(Dt);
                world.ClearEvents();
            }
        }

        /// <summary>How far a vehicle of <paramref name="def"/> gets in 8 s along the band from x = -100.</summary>
        private static float Driven(TerrainTag? tag, string def)
        {
            var world = Field(tag);
            var v = world.SpawnVehicle(def, 0, new Vector2(-100f, 0f), MathF.PI * 0.5f);
            Assert.IsTrue(world.Submit(new Command(CommandType.Move, 0, new[] { v.Id }, new Vector2(120f, 0f))).Accepted, "the move is taken");
            Run(world, 8f);
            return v.Position.X + 100f;
        }

        [Test]
        public void ARoadSpeedsUpAndShallowWaterSlowsDownButNotTheAmphibious()
        {
            var plain = Driven(null, "main_battle_tank");
            Assert.Greater(plain, 10f, "the tank drives");
            Assert.Greater(Driven(TerrainTag.Road, "main_battle_tank") / plain, 1.1f, "a road: +20 %");
            Assert.Less(Driven(TerrainTag.Rough, "main_battle_tank") / plain, 0.92f, "rough ground: -15 %");
            Assert.Less(Driven(TerrainTag.Forest, "main_battle_tank") / plain, 0.82f, "a forest: -25 %");
            Assert.Less(Driven(TerrainTag.ShallowWater, "main_battle_tank") / plain, 0.6f, "shallow water: -50 %");
            var amphibious = Driven(null, "light_tank");
            Assert.Greater(Driven(TerrainTag.ShallowWater, "light_tank") / amphibious, 0.95f, "the amphibious light tank keeps its pace in the water");
            Assert.IsTrue(TerrainRules.Wades(Catalog.Vehicle("hover_gunboat")), "the air-cushion gunboat wades");
            Assert.IsFalse(TerrainRules.Wades(Catalog.Vehicle("main_battle_tank")), "a tank does not");
        }

        [Test]
        public void AForestHidesAVehicleFromFartherOff()
        {
            bool Seen(TerrainTag? tag)
            {
                var world = Field(tag);
                var reach = Catalog.Vehicle("main_battle_tank").VisionRange * 0.8f;
                world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, -reach), 0f);
                var target = world.SpawnVehicle("main_battle_tank", 1, Vector2.Zero, MathF.PI);
                Run(world, 0.5f);
                Assert.AreEqual(tag ?? TerrainTag.Normal, world.Grid.TerrainAt(target.Position), "the target's ground");
                return target.IsVisibleTo(0);
            }
            Assert.IsTrue(Seen(null), "on open ground the tank is seen at 0.8 of its spotter's sight");
            Assert.IsFalse(Seen(TerrainTag.Forest), "in a forest it is not (x 0.7)");
        }

        [Test]
        public void TheTagsAreStaticAndARouteIsTheSameTwice()
        {
            string Route()
            {
                var world = new SimWorld(Catalog, GameContent.LoadMap("junglepass_conquest"), 1);
                Assert.IsTrue(world.Grid.HasTerrain, "Jungle Pass has tags");
                var finder = new PathFinder(world.Grid);
                var path = new List<Vector2>();
                Assert.IsTrue(finder.TryFindPath(world.Map.Teams[0].Rally, world.Map.Teams[1].Rally, path), "a route across");
                return string.Join(";", path.Select(p => p.X.ToString("F2") + "," + p.Y.ToString("F2")));
            }
            Assert.AreEqual(Route(), Route(), "the same route both times");
        }

        [Test]
        public void EveryMapFilesZonesAreValid()
        {
            var problems = new List<string>();
            foreach (var b in Battlefields)
                foreach (var v in new[] { "_conquest", "_sandbox", "_siege", "_long" })
                {
                    if (UnityEngine.Resources.Load<UnityEngine.TextAsset>("Data/maps/" + b + v) == null) continue;
                    var map = GameContent.LoadMap(b + v);
                    if (map.TerrainZones.Count == 0)
                    {
                        problems.Add(b + v + ": no terrain zones");
                        continue;
                    }
                    var grid = new NavGrid(map.Min, map.Width, map.Length, 2f);
                    var seen = new HashSet<int>();
                    foreach (var z in map.TerrainZones)
                    {
                        if (!(z.Max.X > z.Min.X) || !(z.Max.Y > z.Min.Y)) problems.Add(b + v + ": an empty zone");
                        for (var x = z.Min.X + 1f; x < z.Max.X; x += 2f)
                            for (var y = z.Min.Y + 1f; y < z.Max.Y; y += 2f)
                            {
                                var (cx, cy) = grid.CellOf(new Vector2(x, y));
                                if (!seen.Add(grid.Index(cx, cy))) problems.Add(b + v + ": zones overlap at " + x + ", " + y);
                            }
                    }
                }
            Assert.IsEmpty(problems, string.Join("\n", problems.Take(40)));
        }

        [Test]
        public void EveryBattlefieldHasTwoOrThreeLandmarksWithBothNames()
        {
            foreach (var b in Battlefields)
            {
                var map = GameContent.LoadMap(b + "_conquest");
                Assert.That(map.Landmarks.Count, Is.InRange(2, 3), b + " has 2-3 landmarks");
                Assert.AreEqual(map.Landmarks.Count, map.Landmarks.Select(l => l.Id).Distinct().Count(), b + ": landmark ids are unique");
                foreach (var l in map.Landmarks)
                {
                    StringAssert.StartsWith(b + ".", l.Id, "a landmark id names its battlefield");
                    Assert.IsFalse(string.IsNullOrEmpty(l.NameEn) || string.IsNullOrEmpty(l.NameVi), l.Id + " has both names");
                    Assert.IsTrue(map.Contains(l.Position), l.Id + " stands on the map");
                }
            }
            Assert.AreEqual("The lighthouse", GameContent.LoadMap("lighthousebay_conquest").Landmark("lighthousebay.lighthouse")?.NameEn);
        }

        [Test]
        public void TheRoleAsymmetricFilesSayWhy()
        {
            Assert.IsNotNull(GameContent.LoadMap("ironport_siege").AsymmetryReason, "a Siege file is asymmetric on purpose");
            Assert.IsNotNull(GameContent.LoadMap("ashfield_long").AsymmetryReason, "a long file is too");
            Assert.IsNull(GameContent.LoadMap("ashfield_conquest").AsymmetryReason, "a versus file is not");
        }
    }
}
