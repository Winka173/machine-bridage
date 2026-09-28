using System.Collections.Generic;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The campaign enemy keeps pace with the player: it matches most of the edge the arsenal
    /// gives (its boss too), and calls for reinforcements, flown in, when it is losing.
    /// </summary>
    public class ReinforcementTests
    {
        private static SimWorld Field() =>
            new(GameContent.LoadCatalog(), new MapDefinition("field", 200f,
                new[] { new TeamStart(0, new Vector2(-80f, -80f)), new TeamStart(1, new Vector2(80f, 80f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()));

        [Test]
        public void TheEnemyMatchesMostOfThePlayersEdge()
        {
            var none = EnemyScaling.Match(new[] { VehicleBoost.None });
            Assert.AreEqual(1f, none.Hp, 1e-4f);
            Assert.AreEqual(1f, none.Damage, 1e-4f);

            // Health 1.5 taking 90% of the damage: 1.67 times as tough; damage 1.2 at 1.25 the rate: 1.5 the firepower.
            var boosted = new VehicleBoost(1.5f, 1.2f, 1.25f, 1.1f, 0.9f, 0.01f, SpecialModule.None, 0f);
            var edge = EnemyScaling.Match(new[] { boosted, boosted });
            Assert.AreEqual(1f + (1.5f / 0.9f - 1f) * EnemyScaling.Share, edge.Hp, 1e-3f);
            Assert.AreEqual(1f + (1.5f - 1f) * EnemyScaling.Share, edge.Damage, 1e-3f);
            Assert.AreEqual(1f, edge.FireRate, 1e-4f, "the edge goes on damage, not on the rate of fire");
            Assert.Less(edge.Hp, 1.5f / 0.9f, "the player keeps part of the edge");
        }

        [Test]
        public void ACampaignEnemysBossAndTowersAreScaledToo()
        {
            var world = Field();
            var edge = new VehicleBoost(1.5f, 1.4f, 1f, 1f, 1f, 0f, SpecialModule.None, 0f);
            world.SetBoosts(1, _ => edge, _ => edge.Damage, everything: true);
            world.SetBoosts(0, _ => edge);
            var boss = world.SpawnVehicle("behemoth", 1, new Vector2(60f, 60f), 0f);
            var enemyTank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(50f, 60f), 0f);
            var playerBoss = world.SpawnVehicle("behemoth", 0, new Vector2(-60f, -60f), 0f);
            Assert.AreEqual(boss.Def.MaxHp * 1.5f, boss.MaxHp, 1f, "the enemy's boss keeps pace");
            Assert.AreEqual(enemyTank.Def.MaxHp * 1.5f, enemyTank.MaxHp, 1f);
            Assert.AreEqual(playerBoss.Def.MaxHp, playerBoss.MaxHp, 1f, "a normal side's boss is left as it is");
        }

        [Test]
        public void ALosingEnemyIsReinforcedByAir()
        {
            var world = Field();
            var def = new MissionDef
            {
                Id = "test", Goal = MissionGoal.Survive, SurviveSeconds = 600f, EnemyAi = "none",
                Reinforcements = 2, ReinforceSize = 3,
            };
            var enemy = new SideSetup { Vehicles = new[] { "main_battle_tank", "ifv", "aa_vehicle" } };
            var mode = new MissionMode(def, new SideSetup(), enemy);
            mode.Setup(world);
            world.SpawnVehicle("main_battle_tank", 0, new Vector2(-80f, -80f), 0f);
            var army = new List<Sim.Entities.Vehicle>();
            for (var i = 0; i < 5; i++) army.Add(world.SpawnVehicle("main_battle_tank", 1, new Vector2(70f + i * 5f, 80f), 0f));

            var alerted = 0;
            var queued = 0;
            void Run(float seconds)
            {
                for (var t = 0f; t < seconds; t += 0.05f)
                {
                    mode.Tick(world, 0.05f);
                    world.Step(0.05f);
                    foreach (var e in world.Events)
                    {
                        if (e.Kind == SimEventKind.FortressAlert && e.DefId == "toast.enemyReinforce") alerted++;
                        if (e.Kind == SimEventKind.DeploymentQueued && e.Team == 1) queued++;
                    }
                    world.ClearEvents();
                }
            }

            Run(10f);
            Assert.AreEqual(0, alerted, "a full-strength enemy does not call for help");
            for (var i = 0; i < 3; i++) army[i].Hp = 0f;
            Run(10f);
            Assert.AreEqual(0, alerted, "not in the opening minute, however it goes");
            Run(35f);
            Assert.AreEqual(1, alerted, "down to two of five: reinforcements");
            Assert.AreEqual(3, queued, "the first group is the mission's size");
            Assert.AreEqual(1, mode.Reinforced);
            Run(6f);
            Assert.GreaterOrEqual(world.CountAlive(1), 5, "they land");

            // Not again straight away, and never more often than the mission allows.
            Run(30f);
            Assert.AreEqual(1, alerted);
            foreach (var v in world.VehicleList)
                if (v.Team == 1) v.Hp = 0f;
            Run(200f);
            Assert.AreEqual(2, alerted, "the second call, a gap later");
            Assert.AreEqual(3 + 4, queued, "one more each time");
            foreach (var v in world.VehicleList)
                if (v.Team == 1) v.Hp = 0f;
            Run(200f);
            Assert.AreEqual(2, mode.Reinforced, "no more than the mission's reinforcements");
        }
    }
}
