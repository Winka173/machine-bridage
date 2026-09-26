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
            Assert.AreEqual(1.5f, catalog.Damage.Multiplier(DamageType.HighExplosive, ArmorClass.Structure));
        }

        [Test]
        public void ShippedSandboxMapLoadsAndUsesKnownDefinitions()
        {
            var catalog = Catalog.FromJson(File.ReadAllText(DataPath("balance.json")));
            var map = MapDefinition.FromJson(File.ReadAllText(DataPath("maps/ashfield_sandbox.json")));

            Assert.AreEqual(160f, map.Size);
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
