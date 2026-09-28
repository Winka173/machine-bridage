using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Multi-stage missions (prompt 5): stages in order with their CP, branching choices,
    /// checkpoints that a replay of the player's commands brings back exactly, an allied commander
    /// with its own units, its betrayal, and the play area that opens as the mission goes.
    /// </summary>
    public class OperationTests
    {
        private const float Step = 0.05f;

        internal const string Json = @"{ ""missions"": [ {
            ""id"": ""op"", ""map"": ""ashfield"", ""goal"": ""Survive"", ""surviveSeconds"": 4,
            ""enemyAi"": ""none"", ""reinforcements"": 0, ""playerCp"": 5, ""playerIncome"": 0,
            ""units"": [ { ""def"": ""main_battle_tank"", ""team"": 0, ""x"": -60, ""z"": -60 } ],
            ""ally"": { ""x"": -50, ""z"": -70, ""hq"": ""guard_tower"", ""structures"": [ { ""def"": ""mg_bunker"", ""x"": -42, ""z"": -76 } ], ""units"": [ { ""def"": ""ifv"", ""x"": -50, ""z"": -70 }, { ""def"": ""main_battle_tank"", ""x"": -46, ""z"": -70 } ],
                        ""reinforcements"": [ { ""at"": 2, ""units"": [ ""armored_car"" ] } ] },
            ""playArea"": { ""minX"": -90, ""minZ"": -90, ""maxX"": 0, ""maxZ"": 0 },
            ""stages"": [
                { ""stage"": ""hold"", ""cp"": 10, ""events"": [ { ""at"": ""end"", ""kind"": ""Expand"", ""area"": { ""minX"": -90, ""minZ"": -90, ""maxX"": 90, ""maxZ"": 90 } },
                                                          { ""at"": ""1"", ""kind"": ""Radio"", ""key"": ""radio.test"" } ],
                  ""choices"": [ { ""key"": ""left"", ""next"": ""left"" }, { ""key"": ""right"", ""next"": ""right"" } ] },
                { ""stage"": ""left"", ""surviveSeconds"": 3, ""cp"": 5, ""next"": ""last"" },
                { ""stage"": ""right"", ""surviveSeconds"": 3, ""cp"": 7, ""events"": [ { ""at"": ""start"", ""kind"": ""Betrayal"" } ] },
                { ""stage"": ""last"", ""surviveSeconds"": 2 }
            ] } ] }";

        private static MissionDef Def() => MissionDef.ListFromJson(Json)[0];

        private static (SimWorld world, OperationMode op) Start(int seed = 3)
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_conquest"), seed: seed);
            // An empty field: only what the mission places.
            foreach (var v in world.VehicleList) v.Hp = 0f;
            world.Step(Step);
            world.ClearEvents();
            var op = new OperationMode(Def(), new SideSetup { StartCp = 5f, Income = 0f }, null);
            op.Setup(world);
            return (world, op);
        }

        private static void Run(SimWorld world, OperationMode op, float seconds, System.Action<SimWorld> each = null)
        {
            for (var t = 0f; t < seconds && op.Result == null; t += Step)
            {
                op.Tick(world, Step);
                each?.Invoke(world);
                world.Step(Step);
                world.ClearEvents();
            }
        }

        [Test]
        public void StagesParseWithTheirOwnFieldsOverTheMissions()
        {
            var def = Def();
            Assert.AreEqual(4, def.Stages.Count);
            Assert.AreEqual("hold", def.Stages[0].Id);
            Assert.AreEqual(4f, def.Stages[0].Mission.SurviveSeconds, "the mission's field");
            Assert.AreEqual(3f, def.Stages[1].Mission.SurviveSeconds, "the stage's own");
            Assert.AreEqual(0, def.Stages[1].Mission.Units.Count, "the mission's units are placed once, not by every stage");
            Assert.AreEqual(2, def.Stages[0].Choices.Count);
            Assert.AreEqual(StageMoment.End, def.Stages[0].Events[0].At);
            Assert.AreEqual(StageMoment.Time, def.Stages[0].Events[1].At);
            Assert.AreEqual(1.0, def.Stages[0].Events[1].Seconds, 1e-6);
            Assert.AreEqual(2, def.Ally.Units.Count);
            Assert.AreEqual(1, def.Ally.Structures.Count);
            Assert.IsTrue(def.PlayArea.HasValue);
        }

        [Test]
        public void AStagePaysItsCpAndTheBattleGoesOnToTheChoice()
        {
            var (world, op) = Start();
            Assert.AreEqual(0, op.StageIndex);
            world.TryGetEconomy(0, out var economy);
            var before = economy.Cp;
            Run(world, op, 4.5f);
            Assert.IsNull(op.Result, "one stage done is not the mission done");
            Assert.IsFalse(world.IsOver);
            Assert.IsNotNull(op.PendingChoice, "the first stage ends on a choice");
            Assert.AreEqual(before + 10f, economy.Cp, 0.01f, "its CP paid");
            Assert.IsTrue(world.PlayArea.HasValue && world.PlayArea.Value.Max.X >= 89f, "its end event opened the map");
        }

        [Test]
        public void TheChoiceBranchesAndTheMissionEndsAfterTheLastStage()
        {
            var (world, op) = Start();
            Run(world, op, 4.5f);
            Assert.IsTrue(op.Choose(world, "left"));
            Assert.AreEqual("left", op.Stage.Id);
            Run(world, op, 30f);
            Assert.AreEqual(0, op.Result?.WinningTeam, "left, then last: won");
            Assert.IsTrue(world.IsOver);
            CollectionAssert.AreEqual(new[] { 0, 1, 3 }, op.Path.ToArray(), "hold, left, last (right skipped)");
        }

        [Test]
        public void NobodyChoosingTakesTheFirstOption()
        {
            var (world, op) = Start();
            Run(world, op, 4.5f);
            Assert.IsNotNull(op.PendingChoice);
            Run(world, op, (float)OperationMode.ChoiceSeconds + 1f);
            Assert.AreEqual("left", op.Stage.Id);
        }

        [Test]
        public void TheAllyFightsOnThePlayersSideButIsNotThePlayersArmy()
        {
            var (world, op) = Start();
            var allies = world.VehicleList.Where(v => v.IsAlive && v.Ally && !v.Def.Static).ToList();
            Assert.AreEqual(2, allies.Count);
            Assert.IsTrue(allies.All(v => v.Team == 0));
            Assert.AreEqual(2, world.VehicleList.Count(v => v.IsAlive && v.Ally && v.Def.Static), "its HQ and tower");
            world.TryGetEconomy(0, out var economy);
            Run(world, op, 0.2f);
            int Own() => world.VehicleList.Where(v => v.IsAlive && v.Team == 0 && !v.Ally).Sum(v => v.Def.ArmyCost);
            Assert.AreEqual(Own(), economy.ArmyCp, "only the player's own vehicles count against the army");
            Run(world, op, 8f);
            Assert.AreEqual(3, world.VehicleList.Count(v => v.IsAlive && v.Ally && !v.Def.Static), "its reinforcement came in, as the ally's");
            Assert.AreEqual(Own(), economy.ArmyCp);
        }

        [Test]
        public void EachCommanderKeepsToItsOwnUnits()
        {
            // An open field: the player's two tanks and the ally's two, an enemy far off.
            var world = TestWorlds.World();
            var own = new[] { world.SpawnVehicle("tank", 0, new Vector2(-30f, -30f), 0f), world.SpawnVehicle("tank", 0, new Vector2(-26f, -30f), 0f) };
            var ours = new[] { world.SpawnVehicle("tank", 0, new Vector2(-30f, -20f), 0f), world.SpawnVehicle("tank", 0, new Vector2(-26f, -20f), 0f) };
            foreach (var v in ours) v.Ally = true;
            world.SpawnVehicle("decoy", 1, new Vector2(40f, 40f), 0f);
            var player = new TacticalAi(0, 1, 5) { Objective = _ => new Vector2(30f, 30f) };
            var ally = new TacticalAi(0, 1, 6) { Allies = true, Objective = _ => new Vector2(-35f, 30f) };
            for (var i = 0; i < 80; i++)
            {
                player.Tick(world, Step);
                world.Step(Step);
                world.ClearEvents();
            }
            Assert.IsTrue(ours.All(v => v.Order.Kind == OrderKind.Idle), "the player's commander does not send the ally's units");
            Assert.IsTrue(own.All(v => v.Order.Kind != OrderKind.Idle), "only its own");
            for (var i = 0; i < 80; i++)
            {
                ally.Tick(world, Step);
                world.Step(Step);
                world.ClearEvents();
            }
            Assert.IsTrue(ours.All(v => v.Order.Kind != OrderKind.Idle && v.Order.Point.Y > 0f), "the ally's commander sends them where it goes");
            Assert.IsTrue(own.All(v => Vector2.Distance(v.Order.Point, new Vector2(-35f, 30f)) > 20f), "and leaves the player's alone");
        }

        [Test]
        public void BetrayalTurnsOnlyTheAllysUnitsAndTheyFightThePlayer()
        {
            var (world, op) = Start();
            Run(world, op, 4.5f);
            var allies = world.VehicleList.Where(v => v.IsAlive && v.Ally).ToList();
            var own = world.VehicleList.Where(v => v.IsAlive && v.Team == 0 && !v.Ally).ToList();
            Assert.IsTrue(op.Choose(world, "right"));
            Assert.IsTrue(op.Betrayed, "the stage's start event");
            Assert.IsTrue(allies.All(v => v.Team == 1 && !v.Ally), "every ally unit now fights for the enemy");
            Assert.IsTrue(allies.Count(v => v.Def.Static) == 2, "its base with them");
            Assert.IsTrue(own.All(v => v.Team == 0), "nothing of the player's changed sides");
            // Side by side a moment ago: they fight now.
            var hp = own.Sum(v => v.Hp) + allies.Sum(v => v.Hp);
            var ai0 = new TacticalAi(0, 1, 5);
            var ai1 = new TacticalAi(1, 0, 6);
            for (var i = 0; i < 20 * 20 && op.Result == null; i++)
            {
                op.Tick(world, Step);
                ai0.Tick(world, Step);
                ai1.Tick(world, Step);
                world.Step(Step);
                world.ClearEvents();
            }
            Assert.Less(own.Sum(v => v.IsAlive ? v.Hp : 0f) + allies.Sum(v => v.IsAlive ? v.Hp : 0f), hp, "shots fired between the former allies");
        }

        [Test]
        public void ThePlayersMovesStopAtThePlayArea()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_conquest"), seed: 3);
            foreach (var v in world.VehicleList) v.Hp = 0f;
            world.Step(Step);
            world.Expand(new PlayArea(new Vector2(-90f, -90f), new Vector2(-30f, -30f)));
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-60f, -60f), 0f);
            var enemy = world.SpawnVehicle("armored_car", 1, new Vector2(-60f, -40f), 0f);
            world.Submit(new Command(CommandType.Move, 0, new[] { tank.Id }, new Vector2(60f, 60f)));
            world.Submit(new Command(CommandType.Move, 1, new[] { enemy.Id }, new Vector2(-60f, 10f)));
            for (var i = 0; i < 25 * 20; i++)
            {
                world.Step(Step);
                world.ClearEvents();
            }
            Assert.LessOrEqual(tank.Position.X, -28f, "the player's side stops at the edge");
            Assert.LessOrEqual(tank.Position.Y, -28f);
            if (enemy.IsAlive) Assert.Greater(enemy.Position.Y, -20f, "the enemy is not held by it");
            world.Expand(null);
            world.Submit(new Command(CommandType.Move, 0, new[] { tank.Id }, new Vector2(0f, 0f)));
            for (var i = 0; i < 25 * 20; i++) world.Step(Step);
            Assert.Greater(tank.Position.X, -20f, "the whole map open again");
        }

        [Test]
        public void ReplayingThePlayersCommandsFromTheSameSeedLandsOnTheCheckpoint()
        {
            // The original battle: both commanders, and the player's own orders now and then.
            var (world, op) = Start(seed: 9);
            var ai = new TacticalAi(1, 0, 4);
            var tank = world.VehicleList.First(v => v.IsAlive && v.Team == 0 && !v.Ally);
            var spots = new[] { new Vector2(-40f, -30f), new Vector2(-30f, -50f), new Vector2(-55f, -35f) };
            var n = 0;
            world.SpawnVehicle("armored_car", 1, new Vector2(-10f, -10f), 0f);
            // As the game runs it: the player's commands of a step, then the mission, the AI, the step.
            for (var i = 0; i < 5 * 20 && op.Result == null; i++)
            {
                if (world.Tick % 11 == 0) world.SubmitPlayer(new Command(CommandType.Move, 0, new[] { tank.Id }, spots[n++ % spots.Length]));
                op.Tick(world, Step);
                ai.Tick(world, Step);
                world.Step(Step);
                world.ClearEvents();
            }
            Assert.AreEqual(1, op.Checkpoints.Count, "the first stage's checkpoint");
            var checkpoint = op.Checkpoints[0];
            var journal = world.Journal.Where(j => j.tick <= checkpoint.Tick).ToList();
            Assert.Greater(journal.Count, 3);

            // The replay: a fresh battle of the same seed, the journal's commands at their steps.
            var (again, replay) = Start(seed: 9);
            var ai2 = new TacticalAi(1, 0, 4);
            again.SpawnVehicle("armored_car", 1, new Vector2(-10f, -10f), 0f);
            var next = 0;
            while (again.Tick < checkpoint.Tick)
            {
                while (next < journal.Count && journal[next].tick == again.Tick) again.SubmitPlayer(journal[next++].command);
                replay.Tick(again, Step);
                ai2.Tick(again, Step);
                again.Step(Step);
                again.ClearEvents();
            }
            while (next < journal.Count && journal[next].tick == again.Tick) again.SubmitPlayer(journal[next++].command);
            Assert.AreEqual(checkpoint.Hash, again.StateHash(), "the same battle, step for step");
            Assert.AreEqual(op.StageIndex, replay.StageIndex);

            // And from there on, the restored battle and the one that never stopped stay the same.
            void Continue(SimWorld w, OperationMode o, TacticalAi a)
            {
                for (var i = 0; i < 6 * 20; i++)
                {
                    if (i == 10) o.Choose(w, "right");
                    if (i % 17 == 0) w.SubmitPlayer(new Command(CommandType.Move, 0, new[] { tank.Id }, new Vector2(-45f, -45f + i * 0.1f)));
                    o.Tick(w, Step);
                    a.Tick(w, Step);
                    w.Step(Step);
                    w.ClearEvents();
                }
            }
            // The first battle is past the checkpoint already: bring the copy level with it, then both go on.
            while (again.Tick < world.Tick)
            {
                while (next < world.Journal.Count && world.Journal[next].tick == again.Tick) again.SubmitPlayer(world.Journal[next++].command);
                replay.Tick(again, Step);
                ai2.Tick(again, Step);
                again.Step(Step);
                again.ClearEvents();
            }
            Assert.AreEqual(world.StateHash(), again.StateHash(), "level again");
            Continue(world, op, ai);
            Continue(again, replay, ai2);
            Assert.AreEqual(world.StateHash(), again.StateHash(), "six seconds on, through a choice and a betrayal: still the same battle");
            Assert.AreEqual(op.Betrayed, replay.Betrayed);
        }
    }
}
