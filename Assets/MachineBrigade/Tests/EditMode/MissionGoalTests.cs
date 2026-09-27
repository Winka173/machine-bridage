using System.Collections.Generic;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Tests
{
    /// <summary>The round 5 mission goals: hunt the marked vehicles, scout the objectives, keep the buildings standing, shoot aircraft down.</summary>
    public class MissionGoalTests
    {
        private const float Step = 0.05f;

        private static (SimWorld world, MissionMode mode) Mission(string map, MissionDef def)
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(map), seed: 3);
            def.Reinforcements = 0;
            def.EnemyAi = "none";
            var mode = new MissionMode(def, new SideSetup(), null);
            mode.Setup(world);
            return (world, mode);
        }

        private static void Run(SimWorld world, MissionMode mode, float seconds)
        {
            for (var t = 0f; t < seconds && mode.Result == null; t += Step)
            {
                mode.Tick(world, Step);
                world.Step(Step);
                world.ClearEvents();
            }
        }

        private static void Clear(SimWorld world)
        {
            // An empty field: only what each test places.
            foreach (var v in world.VehicleList) v.Hp = 0f;
            world.Step(Step);
            world.ClearEvents();
        }

        [Test]
        public void HuntingEndsWhenEveryMarkedVehicleIsDown()
        {
            var def = new MissionDef
            {
                Id = "hunt", Goal = MissionGoal.Hunt,
                Hunt = new[]
                {
                    new ScriptedUnitDef { Def = "mlrs", Position = new Vector2(40f, 40f), Route = new[] { new Vector2(60f, 40f), new Vector2(40f, 40f) } },
                    new ScriptedUnitDef { Def = "sam_launcher", Position = new Vector2(50f, 10f) },
                },
            };
            var (world, mode) = Mission("ashfield_conquest", def);
            world.SpawnVehicle("main_battle_tank", 0, new Vector2(-72f, -72f), 0f);
            var marks = new List<MissionMark>();
            mode.Marks(world, marks);
            Assert.AreEqual(2, marks.Count);
            Assert.IsTrue(marks.TrueForAll(m => m.Kind == MissionMarkKind.Attack && !m.Prop), "both marked for attack");
            var hunted = new List<Sim.Entities.Vehicle>();
            foreach (var v in world.VehicleList)
                if (v.Marked) hunted.Add(v);
            Assert.AreEqual(2, hunted.Count);
            Assert.IsTrue(hunted.Exists(v => v.Scripted), "the one with a route patrols it");

            Run(world, mode, 1f);
            Assert.AreEqual(0f, mode.Progress(world), 1e-3f);
            hunted[0].Hp = 0f;
            Run(world, mode, 1f);
            Assert.AreEqual(0.5f, mode.Progress(world), 1e-3f);
            Assert.IsNull(mode.Result);
            hunted[1].Hp = 0f;
            Run(world, mode, 1f);
            Assert.AreEqual(0, mode.Result?.WinningTeam, "every marked vehicle down: won");
        }

        [Test]
        public void ScoutingTakesAFewSecondsOnEachObjective()
        {
            var def = new MissionDef { Id = "recon", Goal = MissionGoal.Recon, Points = new[] { "west", "town", "east" } };
            var (world, mode) = Mission("ashfield_conquest", def);
            Clear(world);
            Assert.AreEqual(3, mode.Points.Count);
            Assert.IsTrue(new List<ObjectiveState>(mode.Points).TrueForAll(p => p.Owner == -1), "objectives start unscouted");
            world.SpawnVehicle("main_battle_tank", 0, new Vector2(-72f, -72f), 0f);
            world.SpawnVehicle("scout_jeep", 0, new Vector2(0f, 0f), 0f);
            Run(world, mode, 1.5f);
            Assert.AreEqual(0, mode.Count(world).done, "a look takes a few seconds");
            var marks = new List<MissionMark>();
            mode.Marks(world, marks);
            Assert.AreEqual(3, marks.Count);
            Assert.IsTrue(marks.Exists(m => m.Kind == MissionMarkKind.Scout && m.Progress > 0.3f), "the spot being scouted fills");
            Run(world, mode, 2f);
            Assert.AreEqual(1, mode.Count(world).done, "the town is scouted");
            var next = mode.PlayerGoal(world);
            Assert.IsTrue(next == new Vector2(-37.5f, 57.5f) || next == new Vector2(37.5f, -57.5f), "the commander is sent to a spot not yet scouted");
            foreach (var p in mode.Points)
                if (p.Owner != 0) world.SpawnVehicle("scout_jeep", 0, p.Def.Position, 0f);
            Run(world, mode, 3.5f);
            Assert.AreEqual(0, mode.Result?.WinningTeam, "every objective scouted: won");
        }

        [Test]
        public void ProtectIsLostWhenTooFewBuildingsStandAndWonOnTheClock()
        {
            MissionDef Def() => new()
            {
                Id = "protect", Goal = MissionGoal.Protect, Targets = new[] { "silo", "water_tower" }, ProtectNeeded = 2, SurviveSeconds = 20f,
            };
            var (world, mode) = Mission("greenvale_conquest", Def());
            var marks = new List<MissionMark>();
            mode.Marks(world, marks);
            Assert.AreEqual(3, marks.Count, "only the player's side's two silos and water tower");
            Assert.IsTrue(marks.TrueForAll(m => m.Kind == MissionMarkKind.Defend && m.Prop));
            foreach (var m in marks) Assert.Less(m.Position.Y, 0f, "all on the south, the player's side");
            Assert.IsTrue(world.TryGetProp(mode.EnemyDemolish(world), out _), "the enemy has a building to go for");
            world.SpawnVehicle("main_battle_tank", 0, new Vector2(-72f, -72f), 0f);
            Run(world, mode, 22f);
            Assert.AreEqual(0, mode.Result?.WinningTeam, "standing when the clock runs out: won");

            (world, mode) = Mission("greenvale_conquest", Def());
            world.SpawnVehicle("main_battle_tank", 0, new Vector2(-72f, -72f), 0f);
            mode.Marks(world, marks);
            world.TryGetProp(marks[0].Entity, out var first);
            world.TryGetProp(marks[1].Entity, out var second);
            first.Hp = 0f;
            Run(world, mode, 2f);
            Assert.IsNull(mode.Result, "two of three still standing");
            second.Hp = 0f;
            Run(world, mode, 2f);
            Assert.AreEqual(1, mode.Result?.WinningTeam, "fewer than two standing: lost");
        }

        [Test]
        public void ShootDownCountsOnlyAircraft()
        {
            var def = new MissionDef { Id = "air", Goal = MissionGoal.ShootDown, KillsNeeded = 2 };
            var (world, mode) = Mission("ashfield_conquest", def);
            Clear(world);
            world.SpawnVehicle("main_battle_tank", 0, new Vector2(-72f, -72f), 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(72f, 72f), 0f);
            var heli = world.SpawnVehicle("attack_helicopter", 1, new Vector2(60f, 72f), 0f);
            var jet = world.SpawnVehicle("attack_jet", 1, new Vector2(72f, 60f), 0f);
            Run(world, mode, 0.5f);
            tank.Hp = 0f;
            Run(world, mode, 0.5f);
            Assert.AreEqual(0, mode.Count(world).done, "a tank is not an aircraft");
            heli.Hp = 0f;
            Run(world, mode, 0.5f);
            Assert.AreEqual(1, mode.Count(world).done);
            jet.Hp = 0f;
            Run(world, mode, 0.5f);
            Assert.AreEqual(0, mode.Result?.WinningTeam, "two aircraft down: won");
        }
    }
}
