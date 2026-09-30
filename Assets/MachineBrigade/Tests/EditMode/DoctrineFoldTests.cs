using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text.RegularExpressions;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// DECISIONS 23D: the doctrines are folded into the commanders. Nothing reads a doctrine any more (no type, no
    /// setting, no shop entry, no old id); each doctrine's edge is in the commander that suits it; an old save gets its
    /// coins back once and loses its doctrine entries.
    /// </summary>
    public class DoctrineFoldTests
    {
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static SimWorld World() =>
            new(Catalog, new MapDefinition("test", 200f,
                new[] { new TeamStart(0, new Vector2(0f, -80f)), new TeamStart(1, new Vector2(0f, 80f)) },
                new List<PropPlacement>(), new List<UnitPlacement>(),
                new[] { new CapturePointDef("mid", "mid", new Vector2(0f, 0f), 8f) }));

        private const BindingFlags Every = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance;

        [Test]
        public void NothingReadsADoctrineAnyMore()
        {
            Assert.IsNull(typeof(CommanderDef).Assembly.GetType("MachineBrigade.Sim.Content.Doctrine"), "no doctrine type");
            Assert.IsEmpty(typeof(Progression).GetMembers(Every).Where(m => m.Name.Contains("Doctrine")), "no doctrine price or ownership");
            Assert.IsNull(typeof(MatchSettings).GetProperty("Doctrine", Every), "no doctrine in the match settings");
            Assert.IsNull(typeof(TeamEconomy).GetProperty("Doctrine", Every), "no doctrine in a side's economy");
            Assert.IsNull(typeof(SimWorld).GetMethod("SetDoctrine", Every), "the sim applies none");
            Assert.IsNull(typeof(Vehicle).GetField("DoctrineSpeed", Every));
            foreach (var id in new[] { "title", "locked", "armor", "air", "artillery", "blitz", "logistics", "air.info" })
                Assert.IsFalse(Strings.Has("doctrine." + id), "no doctrine text: " + id);

            // The source: no doctrine identifier and no old id ("doctrine.air", the "mb.doctrine" setting) outside the
            // one-off migration (the profile's refund, the setting dropped on load); no doctrine style in the UI sheets.
            var root = Path.Combine(Application.dataPath, "MachineBrigade");
            var ids = new Regex(@"\w*Doctrine\w*|doctrine\.\w|mb\.doctrine", RegexOptions.CultureInvariant);
            var migration = new[] { "PlayerProfile.cs", "MatchSettings.cs" };
            var found = new List<string>();
            foreach (var file in Directory.GetFiles(Path.Combine(root, "Scripts"), "*.cs", SearchOption.AllDirectories))
            {
                if (migration.Contains(Path.GetFileName(file))) continue;
                var lines = File.ReadAllLines(file);
                for (var i = 0; i < lines.Length; i++)
                    if (ids.IsMatch(lines[i])) found.Add($"{Path.GetFileName(file)}:{i + 1}: {lines[i].Trim()}");
            }
            foreach (var file in Directory.GetFiles(Path.Combine(root, "Resources", "UI"), "*.uss", SearchOption.AllDirectories))
                if (File.ReadAllText(file).ToLowerInvariant().Contains("doctrine")) found.Add(Path.GetFileName(file));
            Assert.IsEmpty(found, string.Join("\n", found));

            // The saved choice is dropped, never read.
            PlayerPrefs.SetString(MatchSettings.OldDoctrineKey, "air");
            MatchSettings.DropOldDoctrineChoice();
            Assert.IsFalse(PlayerPrefs.HasKey(MatchSettings.OldDoctrineKey));
        }

        [Test]
        public void AnOldSavesDoctrinesAreRefundedOnce()
        {
            var all = Progression.TestUnlockAll;
            Progression.TestUnlockAll = true;
            try
            {
                PlayerProfile.TakeRefundNews();
                PlayerProfile.LoadForTests("{\"coins\":100,\"owned\":[\"doctrine.armor\",\"doctrine.air\",\"titan_tank\",\"doctrine.logistics\",\"doctrine.air\"]}");
                Assert.AreEqual(100 + 2 * 1500, PlayerProfile.Coins, "1,500 back for each bought doctrine (the free armoured one pays nothing, a doubled entry once)");
                Assert.AreEqual(3000, PlayerProfile.TakeRefundNews(), "the menu is told once");
                Assert.AreEqual(0, PlayerProfile.TakeRefundNews());
                Assert.IsFalse(PlayerProfile.Owns("doctrine.air"), "the old ids are gone, even in a test build");
                Assert.IsFalse(PlayerProfile.Owns("doctrine.armor"));
                Assert.IsTrue(PlayerProfile.Owns("titan_tank"), "other purchases stay");

                // Saved and loaded again: nothing more to pay.
                PlayerProfile.LoadForTests(PlayerProfile.JsonForTests());
                Assert.AreEqual(3100, PlayerProfile.Coins, "refunded once only");
                Assert.AreEqual(0, PlayerProfile.TakeRefundNews());

                // A save that never bought one: untouched.
                PlayerProfile.LoadForTests("{\"coins\":250,\"owned\":[\"titan_tank\"]}");
                Assert.AreEqual(250, PlayerProfile.Coins);
                Assert.AreEqual(0, PlayerProfile.TakeRefundNews());
            }
            finally
            {
                Progression.TestUnlockAll = all;
                PlayerProfile.Load();
            }
        }

        [Test]
        public void EachDoctrinesEdgeIsInItsCommander()
        {
            Vehicle Spawn(string commander, string id)
            {
                var w = World();
                w.SetCommander(0, Commanders.Get(commander));
                return w.SpawnVehicle(id, 0, new Vector2(0f, -40f), 0f);
            }
            float Hp(string id) => World().SpawnVehicle(id, 0, new Vector2(0f, -40f), 0f).MaxHp;

            // Crown: tanks, heavies and dear vehicles +20 % health, one number (a dear tank no longer stacks two).
            Assert.AreEqual(Hp("main_battle_tank") * 1.2f, Spawn("reyn", "main_battle_tank").MaxHp, 0.05f, "Crown: a 7 CP tank");
            Assert.AreEqual(Hp("heavy_tank") * 1.2f, Spawn("reyn", "heavy_tank").MaxHp, 0.05f, "Crown: a dear heavy, +20 % not +35 %");
            Assert.AreEqual(Hp("armored_car"), Spawn("reyn", "armored_car").MaxHp, 0.05f, "Crown: a cheap light vehicle, nothing");
            // Hawk and Longshot: their arm's health.
            Assert.AreEqual(Hp("attack_helicopter") * 1.2f, Spawn("reyes", "attack_helicopter").MaxHp, 0.05f, "Hawk: aircraft +20 % health");
            Assert.AreEqual(Hp("artillery") * 1.25f, Spawn("dahl", "artillery").MaxHp, 0.05f, "Longshot: artillery +25 % health");
            // Rush: one speed number, and the light vehicles' health less the army's -5 %.
            var light = Spawn("mendez", "armored_car");
            Assert.AreEqual(1.15f, light.SpeedFactor, 1e-4f, "Rush: +15 % speed, not +10 % and +15 %");
            Assert.AreEqual(Hp("armored_car") * 1.10f, light.MaxHp, 0.05f, "Rush: light +15 %, army -5 %");

            // Fire support recharges faster under Hawk and Longshot.
            float Cooldown(string commander)
            {
                var w = World();
                w.SetCommander(0, Commanders.Get(commander));
                var economy = new TeamEconomy(0, 30f);
                w.EnableEconomy(economy);
                Assert.IsTrue(w.Submit(MachineBrigade.Sim.Commands.Command.Strike(0, "artillery_barrage", new Vector2(0f, 20f))).Accepted, commander);
                return economy.CooldownLeft("artillery_barrage", w.Time);
            }
            var plain = Cooldown("kade");
            Assert.Greater(plain, 0f);
            Assert.AreEqual(plain * 0.85f, Cooldown("reyes"), 1e-3f, "Hawk: 15 % faster");
            Assert.AreEqual(plain * 0.75f, Cooldown("dahl"), 1e-3f, "Longshot: 25 % faster");

            // Ledger: all income +15 % (one number) and supply +10 %.
            var ledgerWorld = World();
            ledgerWorld.SetCommander(0, Commanders.Get("brenn"));
            var ledger = new TeamEconomy(0, 10f, income: 1f, bank: 30f);
            ledgerWorld.EnableEconomy(ledger);
            ledgerWorld.Step(0.05f);
            var plainWorld = World();
            var none = new TeamEconomy(0, 10f, income: 1f, bank: 30f);
            plainWorld.EnableEconomy(none);
            plainWorld.Step(0.05f);
            Assert.AreEqual(none.Earning * 1.15f, ledger.Earning, 1e-4f, "Ledger: +15 % income");
            Assert.AreEqual(Mathf.RoundToInt(none.ArmyCap * 1.1f), ledger.ArmyCap, 1, "Ledger: supply +10 %");
        }
    }
}
