using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>What the commander's Attack and Defend stances mean, and the watchtowers on the points.</summary>
    public class StanceTests
    {
        private static void Run(SimWorld world, float seconds, System.Action<float> each = null)
        {
            for (var t = 0f; t < seconds; t += TestWorlds.Step)
            {
                each?.Invoke(TestWorlds.Step);
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
        }

        [Test]
        public void AHeldPointGetsItsOwnersTowerAndLosesItWhenItFalls()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_conquest"), seed: 5);
            var mode = new ConquestMode(new ConquestRules { BaseDefences = false, Outposts = false });
            mode.Setup(world);
            var town = mode.Points.First(p => p.Def.Id == "town");
            var outposts = new Outposts(world, mode.Points);
            PointCapture.Own(town, 0);
            Run(world, Outposts.BuildSeconds + 1f, _ => outposts.Tick(world));
            Assert.IsTrue(outposts.TryGetTower(world, town, out var ours), "the holder's tower goes up");
            Assert.AreEqual(0, ours.Team);
            Assert.Greater(Vector2.Distance(ours.Position, town.Def.Position), town.Def.Radius, "beside the circle, not in it");
            Assert.Less(Vector2.Distance(ours.Position, town.Def.Position), town.Def.Radius + 12f);

            PointCapture.Own(town, 1);
            outposts.Tick(world);
            Assert.IsFalse(ours.IsAlive, "the point fell: its tower is blown up");
            Run(world, Outposts.BuildSeconds + 1f, _ => outposts.Tick(world));
            Assert.IsTrue(outposts.TryGetTower(world, town, out var theirs), "and the new owner's goes up");
            Assert.AreEqual(1, theirs.Team);
        }

        [Test]
        public void AnEntrenchedVehicleTakesLessDamageUntilItMoves()
        {
            var world = TestWorlds.World();
            var a = world.SpawnVehicle("tank", 0, new Vector2(-20f, 0f), 0f);
            var b = world.SpawnVehicle("tank", 0, new Vector2(20f, 0f), 0f);
            world.Entrench(0, true);
            Run(world, SimWorld.EntrenchSeconds + 0.5f);
            Assert.IsTrue(world.IsEntrenched(a), "standing still, a dug-in side's vehicle goes hull-down");
            world.Entrench(0, false);
            Assert.IsFalse(world.IsEntrenched(b), "only while its side is dug in");
            world.Entrench(0, true);
            var before = a.Hp;
            world.Damage.Apply(a, 100f, DamageType.ShapedCharge);
            var entrenched = before - a.Hp;
            world.Entrench(0, false);
            before = b.Hp;
            world.Damage.Apply(b, 100f, DamageType.ShapedCharge);
            var open = before - b.Hp;
            Assert.AreEqual(open * (1f - SimWorld.EntrenchReduction), entrenched, 0.01f, "a fifth less damage");
        }

        [Test]
        public void ADefendingArmyHoldsItsFrontPoint()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_conquest"), seed: 6);
            var mode = new ConquestMode(new ConquestRules { BaseDefences = false, Outposts = false });
            mode.Setup(world);
            var town = mode.Points.First(p => p.Def.Id == "town");
            PointCapture.Own(town, 0);
            world.TryGetRally(0, out var home);
            for (var i = 0; i < 5; i++) world.SpawnVehicle("main_battle_tank", 0, home + new Vector2(i * 4f, 0f), 45f);
            var ai = new ConquestAi(mode, 0, 1, AiDifficulty.Normal, 3) { Stance = CommanderStance.Defend, AutoDeploy = false, AutoStrike = false };
            Run(world, 70f, dt => ai.Tick(world, dt));
            var army = world.VehicleList.Where(v => v.IsAlive && v.Team == 0 && !v.Def.Static && v.Def.Id == "main_battle_tank").ToList();
            var centre = army.Aggregate(Vector2.Zero, (s, v) => s + v.Position) / army.Count;
            Assert.Less(Vector2.Distance(centre, town.Def.Position), town.Def.Radius + 14f, "the army stands on the point it holds");
            Assert.IsTrue(army.Count(world.IsEntrenched) >= 3, "and digs in there");
        }
    }
}
