using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 13 C: aircraft stores on the field and the holding pattern, the owner's key rules:
    /// nobody leaves the map (or goes home) to rearm and the holding pattern is a few seconds away;
    /// the full rate never runs in danger; a bomber goes in again only with two thirds of its bombs;
    /// an aircraft finishes its attack before it leaves.
    /// </summary>
    public class StoresTests
    {
        private static SimWorld Field(int seed = 3) =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("range", 300f,
                new[] { new TeamStart(0, new Vector2(0f, -130f)), new TeamStart(1, new Vector2(0f, 130f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed: seed);

        private static void Empty(Vehicle v)
        {
            for (var i = 0; i < v.Def.Mounts.Count; i++)
                if (v.Stores(i).full > 0) v.Weapons[i].Ammo = 0;
        }

        [Test]
        public void AnEmptyJetFliesAFewSecondsBehindItsLineToRearmAndNeverLeavesTheMap()
        {
            var world = Field();
            world.RevealAll = true;
            var jet = world.SpawnVehicle("attack_jet", 0, new Vector2(0f, -10f), 0f);
            world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, -20f), 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 40f), System.MathF.PI);
            world.MakeDummy(tank);
            world.Submit(new Command(CommandType.AttackMove, 0, new[] { jet.Id }, tank.Position));
            world.Step(TestWorlds.Step);
            Empty(jet);
            var half = world.Map.HalfSize;
            Vector2? leftFrom = null;
            double leftAt = 0, arrivedAt = -1;
            var full = false;
            for (var t = 0f; t < 60f && !full; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                Assert.LessOrEqual(System.MathF.Abs(jet.Position.X), half, "on the map");
                Assert.LessOrEqual(System.MathF.Abs(jet.Position.Y), half, "on the map");
                if (leftFrom == null && jet.Supply == SupplyState.Leaving)
                {
                    leftFrom = jet.Position;
                    leftAt = world.Time;
                }
                if (arrivedAt < 0 && jet.Supply == SupplyState.Holding) arrivedAt = world.Time;
                if (arrivedAt > 0 && jet.Supply == SupplyState.Fighting) full = true;
            }
            Assert.IsNotNull(leftFrom, "it went to rearm");
            Assert.AreEqual(RearmSite.Holding, jet.RearmAt, "no base here: the holding pattern");
            Assert.Greater(arrivedAt, 0.0, "and got there");
            Assert.LessOrEqual(arrivedAt - leftAt, 5.0, "the holding pattern is a few seconds' flight away");
            Assert.LessOrEqual(Vector2.Distance(leftFrom!.Value, jet.HoldPoint), jet.Def.Speed * 3.5f, "about 3 s at its speed");
            Assert.IsTrue(full, "it came back once rearmed");
            Assert.GreaterOrEqual(jet.StoresShare, 0.5f, "with half its stores or more");
        }

        [Test]
        public void TheFullRateNeverRunsInDanger()
        {
            var world = Field();
            world.RevealAll = true;
            var heli = world.SpawnVehicle("attack_helicopter", 0, new Vector2(0f, 0f), 0f);
            var aa = world.SpawnVehicle("aa_vehicle", 1, new Vector2(0f, 20f), System.MathF.PI);
            world.MakeSparring(aa);
            aa.HoldFire = true;
            Empty(heli);
            var inDanger = 0;
            var lastDanger = double.NegativeInfinity;
            for (var t = 0f; t < 30f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                if (heli.InDanger)
                {
                    inDanger++;
                    lastDanger = world.Time;
                }
                if (world.Time - lastDanger < 3.0 && heli.RearmRate > 0f)
                    Assert.LessOrEqual(heli.RearmRate, 0.5f + 1e-4f, $"at {world.Time:0.00} s: the slow rate in danger and for 3 s after");
            }
            Assert.Greater(inDanger, 0, "it was in the AA vehicle's reach");
        }

        [Test]
        public void ABomberGoesInOnlyWithTwoThirdsOfItsBombs()
        {
            var world = Field();
            world.RevealAll = true;
            var bomber = world.SpawnVehicle("heavy_bomber", 0, new Vector2(0f, -60f), 0f);
            var targets = new List<Vehicle>();
            for (var i = 0; i < 4; i++)
            {
                var t = world.SpawnVehicle("main_battle_tank", 1, new Vector2(-6f + i * 4f, 40f), System.MathF.PI);
                world.MakeDummy(t);
                targets.Add(t);
            }
            world.Submit(new Command(CommandType.AttackMove, 0, new[] { bomber.Id }, new Vector2(0f, 40f)));
            var load = bomber.Stores(0).full;
            var runs = new List<int>();
            var run = 0;
            var lastRelease = double.NegativeInfinity;
            for (var t = 0f; t < 150f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.WeaponFired && e.Entity == bomber.Id && e.Mount == 0)
                    {
                        if (world.Time - lastRelease > 2.0 && run > 0)
                        {
                            runs.Add(run);
                            run = 0;
                        }
                        run++;
                        lastRelease = world.Time;
                    }
                world.ClearEvents();
            }
            if (run > 0) runs.Add(run);
            Assert.GreaterOrEqual(runs.Count, 2, "it came back for another run");
            foreach (var r in runs)
                Assert.GreaterOrEqual(r, (int)System.MathF.Ceiling(load * 2f / 3f), $"each run drops two thirds of a load or more ({string.Join(", ", runs)})");
        }

        [Test]
        public void AJetOutOfStoresMidAttackFinishesItBeforeItLeaves()
        {
            var world = Field();
            world.RevealAll = true;
            var jet = world.SpawnVehicle("attack_jet", 0, new Vector2(0f, -40f), 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(0f, 40f), System.MathF.PI);
            world.MakeDummy(tank);
            world.Submit(new Command(CommandType.AttackMove, 0, new[] { jet.Id }, tank.Position));
            // One round of each store left: its holds spend them (the attack jet since prompt 17 D, the A-10 merged into it).
            for (var i = 0; i < jet.Def.Mounts.Count; i++)
                if (jet.Stores(i).full > 0) jet.Weapons[i].Ammo = 1;
            var wasHolding = false;
            var left = false;
            for (var t = 0f; t < 40f && !left; t += TestWorlds.Step)
            {
                var before = jet.Supply;
                var holding = jet.InAttackHold;
                // Out of danger stores refill as the jet flies (the attack jet's 16-round S-8 pods about a round a
                // second): held off here, so the spent stores stay spent (the refill has its own tests).
                foreach (var w in jet.Weapons) w.LoadProgress = 0f;
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                wasHolding |= holding;
                if (before == SupplyState.Fighting && jet.Supply == SupplyState.Leaving)
                {
                    left = true;
                    Assert.IsFalse(jet.InAttackHold, "not in the middle of its hold");
                    Assert.IsTrue(jet.Weapons.All(w => w.BurstLeft == 0), "no salvo still firing");
                    Assert.IsTrue(jet.Breaking || !holding, "it had pulled through (or was not on its run)");
                }
            }
            Assert.IsTrue(wasHolding, "it made its attack");
            Assert.IsTrue(left, "then went to rearm");
            Assert.IsTrue(jet.IsAlive);
        }
    }
}
