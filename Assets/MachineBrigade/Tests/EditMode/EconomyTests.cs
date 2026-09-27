using System.Linq;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Tests
{
    /// <summary>Command Points, deployments, fire support and Conquest scoring.</summary>
    public class EconomyTests
    {
        private static SimWorld WorldWithCp(float cp, int armyCap = 24)
        {
            var world = TestWorlds.World();
            world.EnableEconomy(new TeamEconomy(0, cp, income: 0f, armyCap: armyCap));
            world.EnableEconomy(new TeamEconomy(1, cp, income: 0f, armyCap: armyCap));
            return world;
        }

        [Test]
        public void DeploymentChargesOnceAndArrivesAtTheDropZone()
        {
            var world = WorldWithCp(10f);
            world.TryGetEconomy(0, out var economy);

            Assert.IsTrue(world.Submit(Command.Deploy(0, "tank")).Accepted);
            Assert.AreEqual(6f, economy.Cp, 0.001f, "charged when accepted (T03)");
            Assert.AreEqual(0, world.CountAlive(0), "still on its way");

            TestWorlds.Run(world, EconomySystem.DeliverySeconds + 0.2f);

            Assert.AreEqual(1, world.CountAlive(0));
            Assert.AreEqual(6f, economy.Cp, 0.001f, "never charged twice");
            world.TryGetRally(0, out var zone);
            Assert.Less(Vector2.Distance(world.Vehicles[0].Position, zone), 12f);
        }

        [Test]
        public void DeploymentWithoutCpIsRefusedWithoutCharge()
        {
            var poor = WorldWithCp(3f);
            Assert.AreEqual(CommandError.NotEnoughCp, poor.Submit(Command.Deploy(0, "tank")).Error);
            poor.TryGetEconomy(0, out var poorEconomy);
            Assert.AreEqual(3f, poorEconomy.Cp, 0.001f);
        }

        [Test]
        public void AnArmyAboveItsSupplyCostsUpkeepInsteadOfBeingCapped()
        {
            // Supply 6: the second tank takes the army over it, and is still delivered.
            var world = WorldWithCp(30f, armyCap: 6);
            Assert.IsTrue(world.Submit(Command.Deploy(0, "tank")).Accepted);
            Assert.IsTrue(world.Submit(Command.Deploy(0, "tank")).Accepted, "no hard cap: the purchase goes through");
            world.TryGetEconomy(0, out var economy);
            world.Step(0.05f);
            Assert.Less(economy.Upkeep, 1f, "an army above its supply earns less");
            Assert.AreEqual(1f, TeamEconomy.UpkeepFor(6, 6), 1e-4f, "up to the supply, full income");
            Assert.AreEqual(0.5f, TeamEconomy.UpkeepFor(12, 6), 1e-4f, "half at twice the supply");
            Assert.AreEqual(0.25f, TeamEconomy.UpkeepFor(60, 6), 1e-4f, "never below a quarter");
        }

        [Test]
        public void OnlyTheSafetyLimitOfVehiclesRefusesAPurchase()
        {
            var world = WorldWithCp(30f);
            for (var i = 0; i < TeamEconomy.MaxVehicles; i++)
                world.SpawnVehicle("tank", 0, new Vector2(-40f + i % 10 * 6f, -40f + i / 10 * 8f), 0f);
            world.Step(0.05f);
            Assert.AreEqual(CommandError.ArmyAtCapacity, world.Submit(Command.Deploy(0, "tank")).Error, "T08");
            world.TryGetEconomy(0, out var economy);
            Assert.AreEqual(30f, economy.Cp, 0.5f, "refused without charge");
        }

        [Test]
        public void AOneShotKillStillPaysTheKillReward()
        {
            var world = WorldWithCp(0f);
            world.SpawnVehicle("tank", 0, Vector2.Zero, 0f);
            var victim = world.SpawnVehicle("boomer", 1, new Vector2(12f, 0f), 0f); // 50 HP, one hit
            TestWorlds.Run(world, 1f);

            Assert.IsFalse(victim.IsAlive);
            world.TryGetEconomy(0, out var economy);
            Assert.AreEqual(1f, economy.Cp, 0.001f, "a quarter of the victim's 4 CP");
        }

        [Test]
        public void BarrageLandsAfterItsTelegraphAndSparesTheCaller()
        {
            var world = WorldWithCp(10f);
            var enemy = world.SpawnVehicle("decoy", 1, new Vector2(2f, 0f), 0f);
            var friend = world.SpawnVehicle("decoy", 0, new Vector2(-2f, 0f), 0f);

            Assert.IsTrue(world.Submit(Command.Strike(0, "barrage", Vector2.Zero)).Accepted);
            Assert.IsTrue(world.Events.Any(e => e.Kind == SimEventKind.StrikeWarning), "telegraphed (T04)");
            TestWorlds.Run(world, 1.3f);
            Assert.AreEqual(enemy.MaxHp, enemy.Hp, "nothing lands before the delay");

            TestWorlds.Run(world, 1.5f);
            Assert.Less(enemy.Hp, enemy.MaxHp);
            Assert.AreEqual(friend.MaxHp, friend.Hp);
            Assert.AreEqual(CommandError.OnCooldown, world.Submit(Command.Strike(0, "barrage", Vector2.Zero)).Error);
        }

        [Test]
        public void AirstrikeDropsEveryBombAlongItsLine()
        {
            var world = WorldWithCp(10f);
            world.Submit(Command.Strike(0, "airstrike", new Vector2(-20f, 0f), new Vector2(0f, 0f)));

            var impacts = new System.Collections.Generic.List<Vector2>();
            for (var i = 0; i < 80; i++)
            {
                world.Step(TestWorlds.Step);
                impacts.AddRange(world.Events.Where(e => e.Kind == SimEventKind.StrikeImpact).Select(e => e.Position));
                world.ClearEvents();
            }

            Assert.AreEqual(5, impacts.Count);
            foreach (var p in impacts)
            {
                Assert.Less(System.Math.Abs(p.Y), 2.1f, "within the line's half-width");
                Assert.That(p.X, Is.InRange(-20.1f, 20.1f));
            }
        }

        [Test]
        public void SmokeHidesVehiclesInsideIt()
        {
            var world = WorldWithCp(10f);
            var hidden = world.SpawnVehicle("decoy", 1, new Vector2(20f, 0f), 0f);
            world.SpawnVehicle("tank", 0, Vector2.Zero, 0f);
            TestWorlds.Run(world, TestWorlds.Step);
            Assert.IsTrue(hidden.IsVisibleTo(0));

            world.Submit(Command.Strike(1, "smoke", new Vector2(20f, 0f)));
            TestWorlds.Run(world, 1f);

            Assert.IsFalse(hidden.IsVisibleTo(0));
        }

        [Test]
        public void RepairRestoresHealth()
        {
            var world = WorldWithCp(10f);
            var tank = world.SpawnVehicle("tank", 0, Vector2.Zero, 0f);
            tank.Hp = 50f;

            world.Submit(Command.Strike(0, "repair", Vector2.Zero));
            TestWorlds.Run(world, 3f);

            Assert.AreEqual(200f, tank.Hp, 1f, "half of max HP restored");
        }

        [Test]
        public void ConquestCapturesContestsAndDrainsTickets()
        {
            var world = TestWorlds.ObjectiveWorld();
            var mode = new ConquestMode(new ConquestRules { Tickets = 100, CaptureSeconds = 4f, Bleed = 5f });
            mode.Setup(world);
            var point = mode.Points[0];
            var ours = world.SpawnVehicle("decoy", 0, Vector2.Zero, 0f);

            Run(world, mode, 4.2f);
            Assert.AreEqual(0, point.Owner, "captured alone in CaptureSeconds");

            var theirs = world.SpawnVehicle("decoy", 1, new Vector2(1f, 1f), 0f);
            Run(world, mode, 3f);
            Assert.IsTrue(point.Contested);
            Assert.AreEqual(0, point.Owner, "contested points do not change hands");

            Run(world, mode, 2f);
            Assert.Less(mode.Tickets(1), 100, "the side holding fewer points bleeds");
            Assert.AreEqual(100, mode.Tickets(0));

            ours.Hp = 0f; // dies at the next step
            Run(world, mode, 0.2f);
            Assert.AreEqual(99, mode.Tickets(0), "losing a vehicle costs its CP in tickets");
            Assert.IsNull(mode.Result);
            Assert.IsTrue(theirs.IsAlive);
        }

        [Test]
        public void ConquestEndsWhenTicketsRunOut()
        {
            var world = TestWorlds.ObjectiveWorld();
            var mode = new ConquestMode(new ConquestRules { Tickets = 10, CaptureSeconds = 1f, Bleed = 10f });
            mode.Setup(world);
            world.SpawnVehicle("decoy", 0, Vector2.Zero, 0f);

            Run(world, mode, 3f);

            Assert.IsNotNull(mode.Result);
            Assert.AreEqual(0, mode.Result.Value.WinningTeam);
            Assert.IsTrue(world.IsOver);
            Assert.AreEqual(CommandError.MatchOver, world.Submit(Command.Deploy(0, "tank")).Error, "R14");
        }

        private static void Run(SimWorld world, ConquestMode mode, float seconds)
        {
            for (var i = 0; i < (int)(seconds / TestWorlds.Step + 0.5f); i++)
            {
                mode.Tick(world, TestWorlds.Step);
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
        }
    }
}
