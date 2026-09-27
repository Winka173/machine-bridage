using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>Hulls knock down the trees, bushes, hedges and fences they drive into.</summary>
    public class CrushTests
    {
        [Test]
        public void ATankKnocksDownTheTreeInItsWay()
        {
            var props = new List<PropPlacement> { new("tree", new Vector2(0f, 10f), 0), new("house_small", new Vector2(30f, 30f), 0) };
            var world = new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 100f,
                new[] { new TeamStart(0, new Vector2(-40f, -40f)), new TeamStart(1, new Vector2(40f, 40f)) }, props, new List<UnitPlacement>()));
            var tree = world.Props.First(p => p.Def.Id == "tree");
            var house = world.Props.First(p => p.Def.Id == "house_small");
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            world.Submit(new Command(CommandType.Move, 0, new[] { tank.Id }, new Vector2(0f, 20f)));
            SimEvent? crushed = null;
            for (var t = 0f; t < 8f && tree.IsAlive; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.PropDestroyed && e.Entity == tree.Id) crushed = e;
                world.ClearEvents();
            }
            Assert.IsFalse(tree.IsAlive, "the tree goes down");
            Assert.IsNotNull(crushed);
            Assert.AreEqual(ExplosionTier.Small, crushed.Value.Tier, "knocked down, not blown up");
            Assert.Greater(crushed.Value.Target.Y, 0.5f, "it falls the way the tank was going (+Y)");
            Assert.IsTrue(house.IsAlive, "a house is not crushed");
        }
    }
}
