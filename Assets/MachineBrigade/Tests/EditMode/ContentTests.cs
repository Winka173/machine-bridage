using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Tests
{
    public class ContentTests
    {
        /// <summary>Causeway battlefields whose Siege keeps the classic corner fortress (Tools/maps/build_maps.py CLASSIC_SIEGE).</summary>
        internal static readonly string[] ClassicSiege = { "swamp", "coralisles" };
        private static string DataPath(string file) =>
            Path.Combine(Application.dataPath, "MachineBrigade", "Resources", "Data", file);

        [Test]
        public void ParsesNestedJsonWithCommentsAndEscapes()
        {
            var value = MiniJson.Parse("// note\n{ \"a\": [1, -2.5e1, true, null], \"s\": \"x\\\"\\u0041\" }");

            var root = (Dictionary<string, object>)value;
            var list = (List<object>)root["a"];
            Assert.AreEqual(1d, list[0]);
            Assert.AreEqual(-25d, list[1]);
            Assert.AreEqual(true, list[2]);
            Assert.IsNull(list[3]);
            Assert.AreEqual("x\"A", root["s"]);
        }

        [Test]
        public void JsonErrorsReportLineAndColumn()
        {
            var e = Assert.Throws<FormatException>(() => MiniJson.Parse("{\n  \"a\": 1,\n  \"b\" 2\n}"));
            StringAssert.Contains("line 3", e.Message);
        }

        [Test]
        public void ShippedBalanceCatalogLoads()
        {
            var catalog = Catalog.FromJson(File.ReadAllText(DataPath("balance.json")));

            Assert.AreEqual("gun_120mm", catalog.Vehicle("main_battle_tank").Weapon.Id);
            Assert.IsNotNull(catalog.Prop("fuel_tank").Explosion);
            Assert.AreEqual(1.6f, catalog.Damage.Type(DamageType.HighExplosive, TargetKind.Structure), 1e-5f, "combat final 04/10");
        }

        [Test]
        public void ShippedSandboxMapLoadsAndUsesKnownDefinitions()
        {
            var catalog = Catalog.FromJson(File.ReadAllText(DataPath("balance.json")));
            var map = MapDefinition.FromJson(File.ReadAllText(DataPath("maps/ashfield_sandbox.json")));

            Assert.AreEqual(300f, map.Size);
            foreach (var p in map.Props) Assert.DoesNotThrow(() => catalog.Prop(p.DefId), p.DefId);
            foreach (var u in map.Units) Assert.DoesNotThrow(() => catalog.Vehicle(u.DefId), u.DefId);
        }

        /// <summary>Every battlefield on the menu ships both versions, in its theme, with objectives A, B and C.</summary>
        [Test]
        public void EveryMenuMapShipsBothVersionsWithKnownDefinitions()
        {
            var catalog = Catalog.FromJson(File.ReadAllText(DataPath("balance.json")));
            foreach (var info in MachineBrigade.Game.Match.MatchSettings.AllMaps)
            foreach (var suffix in new[] { "_conquest", "_sandbox" })
            {
                var map = MapDefinition.FromJson(File.ReadAllText(DataPath("maps/" + info.Id + suffix + ".json")));
                Assert.AreEqual(info.Id + suffix, map.Id);
                Assert.AreEqual(info.Theme, map.Theme, map.Id);
                Assert.AreEqual(2, map.Teams.Count, map.Id);
                foreach (var p in map.Props) Assert.DoesNotThrow(() => catalog.Prop(p.DefId), $"{map.Id}: {p.DefId}");
                foreach (var u in map.Units) Assert.DoesNotThrow(() => catalog.Vehicle(u.DefId), $"{map.Id}: {u.DefId}");
                if (suffix == "_conquest")
                    CollectionAssert.AreEqual(new[] { "west", "town", "east" }, map.Points.Select(p => p.Id).ToArray(), map.Id);
            }
        }

        /// <summary>
        /// Every battlefield on the menu also ships a Siege version: the enemy fortress with its
        /// command HQ and fixed team-1 defences, no objectives, and the HQ reachable by land from
        /// the player's rally (the gates are open) on the simulation's own navigation grid.
        /// </summary>
        [Test]
        public void EveryMenuMapShipsASiegeVersionWithAReachableHq()
        {
            var catalog = Catalog.FromJson(File.ReadAllText(DataPath("balance.json")));
            foreach (var info in MachineBrigade.Game.Match.MatchSettings.AllMaps)
            {
                var map = MapDefinition.FromJson(File.ReadAllText(DataPath("maps/" + info.Id + "_siege.json")));
                Assert.AreEqual(info.Id + "_siege", map.Id);
                Assert.AreEqual(info.Theme, map.Theme, map.Id);
                Assert.AreEqual(2, map.Teams.Count, map.Id);
                Assert.AreEqual(0, map.Points.Count, $"{map.Id}: Siege has no capture points");
                foreach (var p in map.Props) Assert.DoesNotThrow(() => catalog.Prop(p.DefId), $"{map.Id}: {p.DefId}");
                foreach (var u in map.Units) Assert.DoesNotThrow(() => catalog.Vehicle(u.DefId), $"{map.Id}: {u.DefId}");

                var hqs = map.Props.Where(p => p.DefId == "command_hq").ToList();
                Assert.AreEqual(1, hqs.Count, $"{map.Id}: one command HQ");
                // The fortress's towers stand in its sized hardpoints (the defender's loadout fills them), every ring holding some.
                // The causeway battlefields keep the classic corner fortress (its defences are map units).
                if (ClassicSiege.Contains(info.Id))
                {
                    Assert.IsNull(map.Fortress, $"{map.Id}: the classic fortress");
                    Assert.IsTrue(map.Units.Any(u => u.Team == 1), $"{map.Id}: its defences");
                    continue;
                }
                Assert.IsNotNull(map.Fortress, $"{map.Id}: has its fortress plan");
                Assert.GreaterOrEqual(map.Fortress.Slots.Count, 24, $"{map.Id}: the fortress is defended");
                for (var ring = 1; ring <= 3; ring++)
                    Assert.IsTrue(map.Fortress.Slots.Any(s => s.Ring == ring && s.Hardpoint.Kind == HardpointKind.Tower), $"{map.Id}: ring {ring} has towers");
                Assert.IsFalse(map.Units.Any(u => u.Team == 1 && catalog.Vehicle(u.DefId).Static), $"{map.Id}: no fixed defences as map units any more");

                var world = new MachineBrigade.Sim.SimWorld(catalog, map, seed: 1);
                var grid = world.Grid;
                var reached = new bool[grid.Width * grid.Height];
                var player = map.Teams.First(t => t.Team == 0).Rally;
                var (sx, sy) = grid.CellOf(player);
                Assert.IsTrue(grid.IsWalkable(sx, sy), $"{map.Id}: the player rally is open ground");
                var todo = new Stack<(int, int)>();
                todo.Push((sx, sy));
                reached[grid.Index(sx, sy)] = true;
                while (todo.Count > 0)
                {
                    var (x, y) = todo.Pop();
                    foreach (var (dx, dy) in new[] { (1, 0), (-1, 0), (0, 1), (0, -1) })
                    {
                        int nx = x + dx, ny = y + dy;
                        if (!grid.IsWalkable(nx, ny) || reached[grid.Index(nx, ny)]) continue;
                        reached[grid.Index(nx, ny)] = true;
                        todo.Push((nx, ny));
                    }
                }
                // Reached: an open cell within 3 m of the HQ's footprint (close enough to shoot it point blank).
                var hq = hqs[0];
                var def = catalog.Prop("command_hq");
                var half = new System.Numerics.Vector2(def.Width * 0.5f + 3f, def.Depth * 0.5f + 3f);
                var (x0, y0) = grid.CellOf(hq.Position - half);
                var (x1, y1) = grid.CellOf(hq.Position + half);
                var near = false;
                for (var y = y0; y <= y1 && !near; y++)
                for (var x = x0; x <= x1 && !near; x++)
                    near = grid.InBounds(x, y) && reached[grid.Index(x, y)];
                Assert.IsTrue(near, $"{map.Id}: the command HQ can be reached from the player rally");
                var (ex, ey) = grid.CellOf(map.Teams.First(t => t.Team == 1).Rally);
                Assert.IsTrue(reached[grid.Index(ex, ey)], $"{map.Id}: the enemy rally inside the base is reachable");
            }
        }

        /// <summary>
        /// Every battlefield has its own outline, not the plain square: the camps and objectives
        /// lie inside it, the ground beyond is blocked to ground units and stops direct fire,
        /// and all three versions of a map share it.
        /// </summary>
        [Test]
        public void EveryMapHasItsOwnOutlineAndNothingDrivesBeyondIt()
        {
            var catalog = Catalog.FromJson(File.ReadAllText(DataPath("balance.json")));
            foreach (var info in MachineBrigade.Game.Match.MatchSettings.AllMaps)
            {
                var conquest = MapDefinition.FromJson(File.ReadAllText(DataPath("maps/" + info.Id + "_conquest.json")));
                Assert.GreaterOrEqual(conquest.Boundary.Count, 12, $"{info.Id}: has an outline");
                foreach (var suffix in new[] { "_sandbox", "_siege" })
                {
                    var other = MapDefinition.FromJson(File.ReadAllText(DataPath("maps/" + info.Id + suffix + ".json")));
                    CollectionAssert.AreEqual(conquest.Boundary, other.Boundary, $"{info.Id}{suffix} shares the outline");
                }
                foreach (var team in conquest.Teams) Assert.IsTrue(conquest.InsideBoundary(team.Rally), $"{info.Id}: camp {team.Team} inside");
                foreach (var point in conquest.Points) Assert.IsTrue(conquest.InsideBoundary(point.Position), $"{info.Id}: {point.Id} inside");

                // A real shape: a good share of the square is terrain.
                var outside = 0;
                var half = conquest.HalfSize;
                for (var x = -half + 1f; x < half; x += 2f)
                for (var z = -half + 1f; z < half; z += 2f)
                    if (!conquest.InsideBoundary(new System.Numerics.Vector2(x, z))) outside++;
                Assert.Greater(outside, half * half / 20f, $"{info.Id}: at least a twentieth of the square is carved away");

                var world = new MachineBrigade.Sim.SimWorld(catalog, conquest, seed: 1);
                var top = half - 1f;
                var corner = new System.Numerics.Vector2(-top, top);
                for (var x = -top; x < half && conquest.InsideBoundary(corner); x += 1f) corner = new System.Numerics.Vector2(x, top);
                Assert.IsFalse(conquest.InsideBoundary(corner), $"{info.Id}: found ground beyond the outline");
                Assert.IsFalse(world.Grid.IsWalkable(corner), $"{info.Id}: no driving beyond the outline");
                Assert.IsTrue(world.Cover.IsBlocked(corner), $"{info.Id}: the terrain beyond stops direct fire");
            }
        }

        [Test]
        public void UnknownWeaponReferenceNamesThePath()
        {
            const string json = "{ \"weapons\": [], \"vehicles\": [ { \"id\": \"t\", \"armor\": \"Heavy\", \"hp\": 1, " +
                                "\"speed\": 1, \"turnRate\": 1, \"turretTurnRate\": 1, \"radius\": 1, \"vision\": 1, \"weapon\": \"nope\" } ] }";

            var e = Assert.Throws<FormatException>(() => Catalog.FromJson(json));
            StringAssert.Contains("vehicles[0].weapon", e.Message);
        }

        [Test]
        public void InvalidNumbersAreRejectedWithTheOwner()
        {
            const string json = "{ \"weapons\": [ { \"id\": \"w\", \"damageType\": \"Kinetic\", \"damage\": 1, \"cooldown\": 0, " +
                                "\"range\": 5, \"projectileSpeed\": 10, \"impactTier\": \"Small\" } ] }";

            var e = Assert.Throws<FormatException>(() => Catalog.FromJson(json));
            StringAssert.Contains("cooldown", e.Message);
        }
    }
}
