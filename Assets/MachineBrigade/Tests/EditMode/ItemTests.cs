using System.Collections.Generic;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Events;

namespace MachineBrigade.Tests
{
    /// <summary>Single-use items bought with coins: no CP, one use each, and what each one does.</summary>
    public class ItemTests
    {
        private static SimWorld Field(out TeamEconomy economy)
        {
            var world = new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 160f,
                new[] { new TeamStart(0, new Vector2(-60f, -60f)), new TeamStart(1, new Vector2(60f, 60f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));
            economy = new TeamEconomy(0, startCp: 0f);
            world.EnableEconomy(economy);
            world.EnableEconomy(new TeamEconomy(1));
            return world;
        }

        private static void Run(SimWorld world, float seconds)
        {
            for (var t = 0f; t < seconds; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
        }

        [Test]
        public void ItemsCostNoCpButOneUseEach()
        {
            var world = Field(out var economy);
            Assert.IsFalse(world.Submit(Command.Strike(0, "moab", Vector2.Zero, Vector2.Zero)).Accepted, "none owned: rejected");
            economy.Items["moab"] = 1;
            Assert.IsTrue(world.Submit(Command.Strike(0, "moab", Vector2.Zero, Vector2.Zero)).Accepted, "no CP needed");
            Assert.AreEqual(0, economy.ItemCount("moab"), "one item is spent");
            Run(world, 25f);
            Assert.IsFalse(world.Submit(Command.Strike(0, "moab", Vector2.Zero, Vector2.Zero)).Accepted, "and then there are none");
        }

        [Test]
        public void MoabFlattensEverythingAround()
        {
            var world = Field(out var economy);
            economy.Items["moab"] = 1;
            var tanks = new List<MachineBrigade.Sim.Entities.Vehicle>();
            for (var i = 0; i < 4; i++) tanks.Add(world.SpawnVehicle("main_battle_tank", 1, new Vector2(i * 5f - 7f, 0f), 0f));
            world.Submit(Command.Strike(0, "moab", Vector2.Zero, Vector2.Zero));
            Run(world, 6f);
            foreach (var t in tanks) Assert.IsFalse(t.IsAlive, "every tank near ground zero is gone");
        }

        [Test]
        public void ReinforcementsDropInAndStay()
        {
            // Play-test 14 deleted the gunship item whose escort flew home; the dropped armour stays.
            var world = Field(out var economy);
            economy.Items["reinforcements"] = 1;
            world.Submit(Command.Strike(0, "reinforcements", new Vector2(-20f, -20f), new Vector2(-20f, -20f)));
            Run(world, 5f);
            Assert.AreEqual(3, world.CountAlive(0), "two tanks and an IFV arrive");
            Run(world, 35f);
            Assert.AreEqual(3, world.CountAlive(0), "the dropped armour stays");
        }

        [Test]
        public void EmpAndShieldDome()
        {
            var world = Field(out var economy);
            economy.Items["emp_blast"] = 1;
            economy.Items["shield_dome"] = 1;
            var enemy = world.SpawnVehicle("heavy_tank", 1, new Vector2(30f, 30f), 0f);
            var friend = world.SpawnVehicle("heavy_tank", 0, new Vector2(-30f, -30f), 0f);
            world.Submit(Command.Strike(0, "emp_blast", new Vector2(30f, 30f), new Vector2(30f, 30f)));
            world.Submit(Command.Strike(0, "shield_dome", new Vector2(-30f, -30f), new Vector2(-30f, -30f)));
            Run(world, 2.5f);
            Assert.IsTrue(enemy.Stunned, "the EMP knocks out the enemy tank");
            Assert.IsTrue(friend.ShieldUp, "the dome shields our tank");
        }

        [Test]
        public void EveryItemIsSoldAndDefined()
        {
            var catalog = GameContent.LoadCatalog();
            foreach (var id in Progression.Items)
            {
                Assert.IsTrue(catalog.TryGetSupport(id, out var support), id);
                Assert.IsTrue(support.Consumable, id);
                Assert.Greater(Progression.ItemPrice(id), 0, id);
            }
        }
    }
}
