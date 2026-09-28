using System.Linq;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The story campaign's mission types (prompt 4): setting up an outpost, breaking the siege of an
    /// allied base, an evacuation, a duel with a general's base, a boss that flees, a boss in a
    /// weaker or stronger form, a base that must not fall, free fire support and income from stage
    /// events, the traitor's base to strike back at, and a map played from the other side.
    /// </summary>
    public class CampaignGoalTests
    {
        private const float Step = 0.05f;

        private static SimWorld EmptyWorld(string map = "ashfield_conquest", int seed = 3)
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(map), seed: seed);
            foreach (var v in world.VehicleList) v.Hp = 0f;
            world.Step(Step);
            world.ClearEvents();
            return world;
        }

        private static MissionMode Start(SimWorld world, MissionDef def, float cp = 20f)
        {
            def.Reinforcements = 0;
            def.EnemyAi = "none";
            var mode = new MissionMode(def, new SideSetup { StartCp = cp, Income = 0f }, null);
            mode.Setup(world);
            return mode;
        }

        private static void Run(SimWorld world, IGameMode mode, float seconds)
        {
            for (var t = 0f; t < seconds && mode.Result == null; t += Step)
            {
                mode.Tick(world, Step);
                world.Step(Step);
                world.ClearEvents();
            }
        }

        [Test]
        public void AnOutpostIsWonOnceItHasStoodOnItsPointLongEnough()
        {
            var world = EmptyWorld();
            var mode = Start(world, new MissionDef { Id = "outpost", Goal = MissionGoal.Outpost, Points = new[] { "town" }, HoldSeconds = 6f });
            world.Bases.Ensure(0, new BaseLoadout());
            world.Bases.OutpostPoints.Add("town");
            world.Bases.PointOwner = id => mode.Points.First(p => p.Def.Id == id).Owner;
            Assert.AreEqual(1, mode.Points.Count, "one site");
            Assert.AreEqual(-1, mode.Points[0].Owner, "it has to be taken first");
            world.SpawnVehicle("main_battle_tank", 0, Vector2.Zero, 0f);
            Run(world, mode, 14f);
            Assert.AreEqual(0, mode.Points[0].Owner, "taken");
            Run(world, mode, 10f);
            Assert.IsNull(mode.Result, "taking the point is not enough: the outpost must be set up");
            Assert.AreEqual(0f, mode.Progress(world), 1e-3f);
            Assert.IsTrue(world.Submit(new Command(CommandType.Outpost, 0, System.Array.Empty<EntityId>(), defId: "town")).Accepted);
            Run(world, mode, 3f);
            Assert.IsNull(mode.Result);
            Assert.Greater(mode.Progress(world), 0.3f, "its clock runs once it stands");
            Run(world, mode, 5f);
            Assert.AreEqual(0, mode.Result?.WinningTeam, "set up and kept: won");
        }

        private const string ReliefJson = @"{ ""missions"": [ {
            ""id"": ""relief"", ""map"": ""ashfield"", ""goal"": ""Relieve"", ""enemyAi"": ""none"", ""reinforcements"": 0,
            ""hunt"": [ { ""def"": ""light_tank"", ""x"": -30, ""z"": -60 }, { ""def"": ""light_tank"", ""x"": -40, ""z"": -30 } ],
            ""ally"": { ""x"": -60, ""z"": -60, ""hq"": ""headquarters"",
                        ""structures"": [ { ""def"": ""guard_tower"", ""x"": -52, ""z"": -52 } ] } } ] }";

        private static (SimWorld world, OperationMode op) Relief()
        {
            var world = EmptyWorld();
            var op = new OperationMode(MissionDef.ListFromJson(ReliefJson)[0], new SideSetup { StartCp = 5f, Income = 0f }, null);
            op.Setup(world);
            return (world, op);
        }

        [Test]
        public void TheSiegeIsBrokenWhenEveryBesiegerIsDown()
        {
            var (world, op) = Relief();
            Assert.IsTrue(op.AllyHq.IsValid, "the ally's HQ stands at its site");
            Assert.IsTrue(world.TryGetVehicle(op.AllyHq, out var hq) && hq.Ally && hq.Team == 0);
            Assert.AreEqual(2, world.VehicleList.Count(v => v.IsAlive && v.Ally), "its HQ and its tower");
            var besiegers = world.VehicleList.Where(v => v.IsAlive && v.Marked).ToList();
            Assert.AreEqual(2, besiegers.Count);
            Assert.AreEqual(hq.Position.X, op.Current.EnemyGoal(world).Value.X, 0.01f, "the besiegers go for the allied HQ");
            Run(world, op, 1f);
            Assert.IsNull(op.Result);
            foreach (var b in besiegers) b.Hp = 0f;
            Run(world, op, 1f);
            Assert.AreEqual(0, op.Result?.WinningTeam, "the ring broken: won");
        }

        [Test]
        public void TheReliefFailsWhenTheAlliedHqFalls()
        {
            var (world, op) = Relief();
            world.TryGetVehicle(op.AllyHq, out var hq);
            hq.Hp = 0f;
            Run(world, op, 1f);
            Assert.AreEqual(1, op.Result?.WinningTeam, "the base the army came to save is gone");
        }

        [Test]
        public void EvacueesLeaveOneAfterAnotherWithoutWaitingForAnEscort()
        {
            var world = EmptyWorld();
            var def = new MissionDef
            {
                Id = "evac", Goal = MissionGoal.Evacuate, ConvoyCount = 3, ConvoyNeeded = 2, ConvoyInterval = 6f,
                Convoy = new ScriptedUnitDef { Def = "supply_truck", Position = new Vector2(0f, 0f), Route = new[] { new Vector2(-40f, -40f) } },
            };
            var mode = Start(world, def);
            // A guard at the site, none along the road: the evacuees still run for it.
            world.SpawnVehicle("main_battle_tank", 0, new Vector2(6f, 6f), 0f);
            Assert.AreEqual(0f, mode.PlayerGoal(world).Value.Length(), 0.01f, "the army holds the site while evacuees are left there");
            Run(world, mode, 1f);
            Assert.AreEqual(1, world.VehicleList.Count(v => v.IsAlive && v.Def.Id == "supply_truck"), "the first leaves");
            Run(world, mode, 6f);
            Assert.AreEqual(2, world.VehicleList.Count(v => v.IsAlive && v.Def.Id == "supply_truck"), "the next one a few seconds later");
            Run(world, mode, 60f);
            Assert.AreEqual(0, mode.Result?.WinningTeam, "enough got out");
        }

        [Test]
        public void TheEvacuationIsLostWhenTooFewCanStillGetOut()
        {
            var world = EmptyWorld();
            var def = new MissionDef
            {
                Id = "evac", Goal = MissionGoal.Evacuate, ConvoyCount = 2, ConvoyNeeded = 2, ConvoyInterval = 2f,
                Convoy = new ScriptedUnitDef { Def = "supply_truck", Position = new Vector2(0f, 0f), Route = new[] { new Vector2(-80f, -80f) } },
            };
            var mode = Start(world, def);
            world.SpawnVehicle("main_battle_tank", 0, new Vector2(6f, 6f), 0f);
            Run(world, mode, 3f);
            foreach (var truck in world.VehicleList.Where(v => v.Def.Id == "supply_truck").ToList()) truck.Hp = 0f;
            Run(world, mode, 2f);
            Assert.AreEqual(1, mode.Result?.WinningTeam);
        }

        [Test]
        public void ADuelIsWonWhenTheGeneralsHqFalls()
        {
            var world = EmptyWorld();
            var mode = Start(world, new MissionDef { Id = "duel", Goal = MissionGoal.Duel, EnemyBase = BaseRole.Target });
            BaseDefences.Build(world, new BaseSetup().Set(1, BaseLoadout.ForAi(world.Catalog, "Hard", "varga", 3, level: 5), BaseRole.Target), 1);
            var camp = world.Bases.Of(1);
            Assert.IsNotNull(camp);
            Assert.AreEqual(camp.HqPosition, mode.PlayerGoal(world), "the army goes for the general's HQ");
            Assert.Greater(camp.Slots.Count(s => s.Structure.IsValid), 8, "a full base at level 5");
            world.SpawnVehicle("main_battle_tank", 0, new Vector2(-80f, -80f), 0f);
            Run(world, mode, 1f);
            Assert.IsNull(mode.Result);
            world.TryGetVehicle(camp.Hq, out var hq);
            hq.Hp = hq.MaxHp * 0.25f;
            Run(world, mode, 0.5f);
            Assert.AreEqual(0.75f, mode.Progress(world), 0.02f);
            hq.Hp = 0f;
            Run(world, mode, 1f);
            Assert.AreEqual(0, mode.Result?.WinningTeam);
        }

        [Test]
        public void ABaseToDefendLosesTheMissionWhenItsHqFalls()
        {
            var world = EmptyWorld();
            var mode = Start(world, new MissionDef { Id = "defend", Goal = MissionGoal.Survive, SurviveSeconds = 600f, PlayerBase = BaseRole.Defend });
            BaseDefences.Build(world, new BaseSetup().Set(0, new BaseLoadout { HqLevel = 1 }, BaseRole.Defend), 0);
            world.SpawnVehicle("main_battle_tank", 0, new Vector2(-80f, -80f), 0f);
            Run(world, mode, 1f);
            Assert.IsNull(mode.Result);
            world.TryGetVehicle(world.Bases.Of(0).Hq, out var hq);
            hq.Hp = 0f;
            Run(world, mode, 1f);
            Assert.AreEqual(1, mode.Result?.WinningTeam, "the HQ was the thing to hold");
        }

        [Test]
        public void ABossCanComeWeakerOrStrongerThanItsDef()
        {
            var world = EmptyWorld();
            var weak = Start(world, new MissionDef
            {
                Id = "weak", Goal = MissionGoal.Boss, Boss = new ScriptedUnitDef { Def = "fortress_bastion", Position = new Vector2(80f, 80f), Health = 0.6f },
            });
            world.TryGetVehicle(weak.Boss, out var bastion);
            Assert.AreEqual(world.Catalog.Vehicles["fortress_bastion"].MaxHp * 0.6f, bastion.MaxHp, 1f);
            Assert.AreEqual(bastion.MaxHp, bastion.Hp, 1f, "at its full (lower) health");
        }

        [Test]
        public void ABossThatFleesAtHalfHealthWinsTheFightAndLeaves()
        {
            var world = EmptyWorld();
            var mode = Start(world, new MissionDef
            {
                Id = "flee", Goal = MissionGoal.Boss,
                Boss = new ScriptedUnitDef { Def = "silver_bug", Position = new Vector2(60f, 60f), FleeAt = 0.5f },
            });
            world.SpawnVehicle("main_battle_tank", 0, new Vector2(-80f, -80f), 0f);
            world.TryGetVehicle(mode.Boss, out var bug);
            bug.Hp = bug.MaxHp * 0.55f;
            Run(world, mode, 1f);
            Assert.IsNull(mode.Result, "still over half");
            bug.Hp = bug.MaxHp * 0.45f;
            Run(world, mode, 0.2f);
            Assert.IsTrue(mode.BossFled);
            Assert.AreEqual(0, mode.Result?.WinningTeam, "driven off: the fight is won");
            Assert.AreEqual(1f, mode.Progress(world), 1e-3f);
            Assert.IsTrue(bug.Invulnerable, "it cannot be finished off as it goes");
            for (var i = 0; i < 12 * 20; i++)
            {
                world.Step(Step);
                world.ClearEvents();
            }
            Assert.IsFalse(bug.IsAlive, "it has left the battle");
        }

        private const string StrikeJson = @"{ ""missions"": [ {
            ""id"": ""op"", ""map"": ""ashfield"", ""goal"": ""Survive"", ""surviveSeconds"": 3,
            ""enemyAi"": ""none"", ""reinforcements"": 0, ""playerCp"": 5, ""playerIncome"": 0,
            ""stages"": [
                { ""stage"": ""radio"", ""events"": [ { ""at"": ""end"", ""kind"": ""Strike"", ""team"": 0, ""support"": ""artillery_barrage"", ""every"": 10 },
                                                   { ""at"": ""end"", ""kind"": ""Income"", ""team"": 1, ""amount"": 0.5 } ] },
                { ""stage"": ""hold"", ""surviveSeconds"": 35 },
                { ""stage"": ""back"", ""goal"": ""Hunt"", ""surviveSeconds"": 5 }
            ] } ] }";

        [Test]
        public void AStageCanOpenRepeatingFireSupportAndCutTheEnemysIncome()
        {
            var world = EmptyWorld();
            world.EnableEconomy(new SideSetup { StartCp = 5f, Income = 1f }.Build(1));
            var op = new OperationMode(MissionDef.ListFromJson(StrikeJson)[0], new SideSetup { StartCp = 5f, Income = 0f }, null);
            op.Setup(world);
            world.TryGetEconomy(1, out var enemy);
            var income = enemy.Income;
            world.SpawnVehicle("main_battle_tank", 0, new Vector2(-100f, -100f), 0f);
            for (var i = 0; i < 4; i++) world.SpawnVehicle("light_tank", 1, new Vector2(40f + i * 3f, 40f), 0f);
            Run(world, op, 4f);
            Assert.AreEqual("hold", op.Stage.Id);
            Assert.AreEqual(1, op.FreeStrikes, "the first strike as the stage ended");
            Assert.AreEqual(income * 0.5f, enemy.Income, 1e-4f, "the enemy earns half from now on");
            Run(world, op, 21f);
            Assert.AreEqual(3, op.FreeStrikes, "and again every ten seconds");
        }

        [Test]
        public void TheTraitorsBaseIsMarkedForTheStrikeBack()
        {
            var world = EmptyWorld();
            var op = new OperationMode(MissionDef.ListFromJson(ReliefJson.Replace("\"Relieve\"", "\"Survive\"").Replace("\"hunt\"", "\"units\""))[0],
                new SideSetup { StartCp = 5f, Income = 0f }, null);
            op.Setup(world);
            op.Betray(world);
            Assert.IsTrue(world.TryGetVehicle(op.AllyHq, out var hq));
            Assert.AreEqual(1, hq.Team, "the ally's HQ is the enemy's now");
            Assert.IsTrue(hq.Marked, "and marked to strike back at");
            var hunt = new MissionMode(new MissionDef { Id = "back", Goal = MissionGoal.Hunt }, new SideSetup(), null);
            hunt.SetupStage(world, false, null);
            var marks = new System.Collections.Generic.List<MissionMark>();
            hunt.Marks(world, marks);
            Assert.AreEqual(2, marks.Count, "a hunt with no targets of its own goes after the traitor's HQ and tower");
        }

        [Test]
        public void AReversedMapSwapsTheCamps()
        {
            var map = GameContent.LoadMap("ashfield_siege");
            var reversed = map.Reversed();
            Assert.AreEqual(map.Teams.First(t => t.Team == 1).Rally, reversed.Teams.First(t => t.Team == 0).Rally, "side 0 starts in the enemy's corner");
            Assert.AreEqual(map.BaseOf(1)?.Hq, reversed.BaseOf(0)?.Hq);
            Assert.AreEqual(map.Units.Count(u => u.Team == 1), reversed.Units.Count(u => u.Team == 0), "the fortress's towers are side 0's");
            Assert.AreEqual(map.Props.Count, reversed.Props.Count);
            var world = new SimWorld(GameContent.LoadCatalog(), reversed, seed: 1);
            Assert.IsTrue(world.TryGetRally(0, out var rally) && rally.X > 0f && rally.Y > 0f);
        }
    }
}
