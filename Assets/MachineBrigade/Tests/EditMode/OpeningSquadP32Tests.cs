using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 32 L6 (DECISIONS "Prompt 32 L4/L5/L6/L8"): the starting CP x 1.16 in the listed modes, rounded half up; the
    /// opening squads (each role the deck's cheapest card of it, by baseCP then id; a missing role left out; at most 60 %
    /// of the starting CP; 0-CP cards, structures, bosses and elites never; dropped as bought vehicles); the maps'
    /// generic start units left out where the squads come. Written, not run.
    /// </summary>
    public class OpeningSquadP32Tests
    {
        private static Catalog _catalog;
        private static Catalog C => _catalog ??= GameContent.LoadCatalog();
        private static OpeningRules O => C.Opening;

        [Test]
        public void TheStartingCpTakesTheNewPrices()
        {
            Assert.AreEqual(1.16f, O.StartCpScale, 1e-4f);
            Assert.AreEqual(16f, O.StartCp("Conquest", 14f), "Conquest 14 -> 16");
            Assert.AreEqual(21f, O.StartCp("Deathmatch", 18f), "18 -> 21");
            Assert.AreEqual(19f, O.StartCp("KingOfTheHill", 16f), "16 -> 19");
            Assert.AreEqual(19f, O.StartCp("Survival", 16f), "16 -> 19");
            Assert.AreEqual(35f, O.StartCp("Defend", 30f), "30 -> 35");
            Assert.AreEqual(44f, O.StartCp("Siege", 38f), "38 -> 44");
            Assert.AreEqual(46f, O.StartCp("BossRush", 40f), "40 -> 46 (the hunt's bank is 60)");
            Assert.AreEqual(29f, O.StartCp("Campaign", 25f), "a mission's own CP x 1.16, half up");
            Assert.AreEqual(18f, O.StartCp("Sandbox", 18f), "the Sandbox keeps its own");
            Assert.AreEqual(18f, O.StartCp(null, 18f), "tests (no mode) keep theirs");
        }

        [Test]
        public void EnablingAnEconomyScalesItsStartingCp()
        {
            var world = new SimWorld(C, GameContent.LoadMap("ashfield_conquest"), seed: 3) { ModeTag = "Deathmatch" };
            world.EnableEconomy(new TeamEconomy(0, 18f, bank: 45f));
            Assert.IsTrue(world.TryGetEconomy(0, out var e));
            Assert.AreEqual(21f, e.Cp, 1e-4f);
        }

        [Test]
        public void EveryCommanderHasARowAndEveryRoleExists()
        {
            foreach (var c in Commanders.All)
                Assert.IsTrue(O.Commanders.ContainsKey(c.Id), $"commander {c.Id} has an opening row");
            Assert.IsEmpty(O.CommanderRoles("brenn"), "Brenn: none");
            Assert.IsEmpty(O.CommanderRoles("okoye"), "Okoye: none");
            Assert.AreEqual(new[] { "mbt", "scout" }, O.CommanderRoles("kade").ToArray());
            Assert.AreEqual(3, O.CommanderRoles("varro").Count, "Varro: three vehicles of 4 CP at most");
            foreach (var role in O.Roles.Values)
                foreach (var id in role.Ids) Assert.IsTrue(C.Vehicles.ContainsKey(id), id);
            Assert.IsNotEmpty(O.GeneralRoles("unknown general"), "a general not in the table takes the default row");
        }

        [Test]
        public void EachRoleTakesTheDecksCheapestCard()
        {
            var deck = new[] { "heavy_tank", "main_battle_tank", "scout_jeep", "armored_car" };
            var squad = OpeningSquads.Pick(C, O.CommanderRoles("kade"), deck, 100f);
            var mbt = new[] { "main_battle_tank" };
            Assert.AreEqual(2, squad.Count);
            Assert.AreEqual("main_battle_tank", squad[0], "the cheapest main battle tank in the deck");
            var scouts = deck.Where(id => O.Roles["scout"].Ids.Contains(id)).OrderBy(id => C.Vehicles[id].BaseCp).ThenBy(id => id, System.StringComparer.Ordinal).First();
            Assert.AreEqual(scouts, squad[1], "the cheapest scout, ties by id");
            Assert.IsNotNull(mbt);
        }

        [Test]
        public void AMissingRoleIsLeftOutAndItsCpKept()
        {
            var squad = OpeningSquads.Pick(C, O.CommanderRoles("kade"), new[] { "scout_jeep" }, 100f);
            Assert.AreEqual(new[] { "scout_jeep" }, squad.ToArray(), "no main battle tank in the deck: only the scout");
        }

        [Test]
        public void TheSquadNeverPassesItsBudget()
        {
            var deck = new[] { "main_battle_tank", "scout_jeep" };
            var budget = C.Vehicles["main_battle_tank"].BaseCp - 1f;
            var squad = OpeningSquads.Pick(C, O.CommanderRoles("kade"), deck, budget);
            Assert.IsFalse(squad.Contains("main_battle_tank"), "the tank does not fit");
            Assert.LessOrEqual(squad.Sum(id => C.Vehicles[id].BaseCp), budget);
        }

        [Test]
        public void VarroTakesThreeCheapVehicles()
        {
            var deck = new[] { "main_battle_tank", "scout_jeep", "armored_car", "light_tank" };
            var squad = OpeningSquads.Pick(C, O.CommanderRoles("varro"), deck, 100f);
            Assert.AreEqual(3, squad.Count);
            foreach (var id in squad) Assert.LessOrEqual(C.Vehicles[id].BaseCp, 4, id);
        }

        [Test]
        public void ZeroCpCardsStructuresBossesAndElitesAreNeverPicked()
        {
            foreach (var def in C.Vehicles.Values)
                if (def.BaseCp <= 0 || def.Static || def.Boss || def.Elite || def.Fort != null)
                    Assert.IsFalse(OpeningSquads.Eligible(def), def.Id);
        }

        [Test]
        public void TheSquadDropsFromTheStartingCpAsBoughtVehicles()
        {
            var world = new SimWorld(C, GameContent.LoadMap("ashfield_conquest"), seed: 3) { ModeTag = "Conquest" };
            var deck = new[] { "main_battle_tank", "scout_jeep", "armored_car" };
            world.EnableEconomy(new TeamEconomy(0, 30f, bank: 60f, vehicles: deck));
            world.TryGetEconomy(0, out var e);
            var start = e.Cp;
            var dropped = OpeningSquads.Apply(world, 0, O.CommanderRoles("kade"));
            Assert.IsNotEmpty(dropped);
            var cost = dropped.Sum(id => C.Vehicles[id].BaseCp);
            Assert.AreEqual(start - cost, e.Cp, 1e-3f, "their baseCP comes off the starting CP");
            Assert.LessOrEqual(cost, start * O.Share + 1e-3f, "at most the share");
            for (var t = 0f; t < 12f; t += TestWorlds.Step) world.Step(TestWorlds.Step);
            Assert.AreEqual(dropped.Count, world.Vehicles.Count(v => v.IsAlive && v.Team == 0 && !v.Def.Static), "they landed");
            Assert.AreEqual(cost, e.ArmyCp, "regular vehicles: in the army supply reads");
        }

        [Test]
        public void TheMapsGenericStartUnitsAreMarkedAndLeftOutForTheSquads()
        {
            var world = new SimWorld(C, GameContent.LoadMap("ashfield_conquest"), seed: 3);
            Assert.IsTrue(world.Map.Units.Any(u => u.Start), "the generic start units are marked");
            var all = world.MapUnits.Count();
            world.SkipStartUnits = true;
            Assert.Less(world.MapUnits.Count(), all);
            Assert.IsFalse(world.MapUnits.Any(u => u.Start));
        }

        [Test]
        public void NoCampaignMissionTakesASquadUnlessItSaysSo()
        {
            foreach (var m in Campaign.All)
                Assert.IsFalse(m.OpeningSquad, $"{m.Id}: the default is off (no mission sets it yet)");
        }
    }
}
