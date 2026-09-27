using System.Collections.Generic;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Tests
{
    /// <summary>The tactical AI weighs the odds: it falls back when badly outmatched and attacks when stronger.</summary>
    public class OddsTests
    {
        private static SimWorld Field() =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 140f,
                new[] { new TeamStart(0, new Vector2(-60f, -60f)), new TeamStart(1, new Vector2(60f, 60f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));

        private static List<Vehicle> Spawn(SimWorld world, int team, int count, Vector2 at)
        {
            var list = new List<Vehicle>();
            for (var i = 0; i < count; i++)
                list.Add(world.SpawnVehicle("main_battle_tank", team, at + new Vector2((i % 4) * 5f, (i / 4) * 8f), team == 0 ? 0f : 3.14f));
            return list;
        }

        private static int Alive(List<Vehicle> list)
        {
            var n = 0;
            foreach (var v in list) if (v.IsAlive) n++;
            return n;
        }

        [Test]
        public void OutmatchedArmyFallsBackInsteadOfCharging()
        {
            var world = Field();
            var ours = Spawn(world, 0, 2, new Vector2(-10f, -40f));
            var theirs = Spawn(world, 1, 7, new Vector2(-10f, 10f));
            var ai = new TacticalAi(0, 1) { Objective = _ => new Vector2(0f, 20f) };
            var heldBack = false;
            for (var t = 0f; t < 40f; t += TestWorlds.Step)
            {
                ai.Tick(world, TestWorlds.Step);
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                heldBack |= ai.HoldingBack;
            }
            Assert.IsTrue(heldBack, "two tanks facing seven judge the odds and fall back");
            Assert.AreEqual(2, Alive(ours), "and survive instead of driving into the guns");
        }

        [Test]
        public void StrongerArmyStillAttacks()
        {
            var world = Field();
            var ours = Spawn(world, 0, 7, new Vector2(-10f, -40f));
            var theirs = Spawn(world, 1, 2, new Vector2(-10f, 10f));
            var ai = new TacticalAi(0, 1) { Objective = _ => new Vector2(0f, 20f) };
            for (var t = 0f; t < 60f && Alive(theirs) > 0; t += TestWorlds.Step)
            {
                ai.Tick(world, TestWorlds.Step);
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                Assert.IsFalse(ai.HoldingBack, "seven tanks do not fall back from two");
            }
            Assert.AreEqual(0, Alive(theirs), "the stronger army wins the fight");
        }
    }
}
