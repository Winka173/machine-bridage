using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The game's way back to a checkpoint (prompt 5): a real mission session (the player's
    /// commander and the enemy's, the player's own orders and switches) is played to a
    /// checkpoint; a fresh battle of the same seed replayed from the journal lands on it exactly.
    /// </summary>
    public class CheckpointReplayTests
    {
        private const float Step = 0.05f;

        private static MissionDef Mission()
        {
            var def = MissionDef.ListFromJson(OperationTests.Json)[0];
            // Both commanders at work (the framework test's mission has no enemy commander).
            def.EnemyAi = "commander";
            def.EnemyDeck = new[] { "armored_car", "main_battle_tank", "ifv" };
            return def;
        }

        private static (SimWorld world, MissionSession session) Start(MissionDef def, int seed)
        {
            MatchSettings.DeckVehicles.Clear();
            MatchSettings.DeckVehicles.AddRange(new[] { "main_battle_tank", "ifv", "armored_car", "aa_vehicle", "mlrs" });
            MatchSettings.DeckSupports.Clear();
            MatchSettings.Run = null;
            MatchSettings.MissionTier = 0;
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_conquest"), seed: seed);
            var session = (MissionSession)ModeSession.Create(GameModeKind.Campaign, false, world, seed, def);
            MatchJournal.Inputs.Clear();
            MatchJournal.Record(world, "autoDeploy", session.PlayerAi.AutoDeploy ? "1" : "0");
            MatchJournal.Record(world, "autoStrike", session.PlayerAi.AutoStrike ? "1" : "0");
            return (world, session);
        }

        [Test]
        public void AReplayOfTheJournalLandsOnTheCheckpoint()
        {
            var def = Mission();
            var (world, session) = Start(def, 9);
            // The original battle: the player's orders now and then, a stance switch, a branch chosen.
            for (var i = 0; i < 20 * 20 && session.Mode.Result == null; i++)
            {
                if (i % 37 == 5)
                {
                    var own = world.VehicleList.FirstOrDefault(v => v.IsAlive && v.Team == 0 && !v.Ally && !v.Def.Static);
                    if (own != null) world.SubmitPlayer(new Command(CommandType.Move, 0, new[] { own.Id }, new Vector2(-40f + i % 13, -40f)));
                }
                if (i == 60)
                {
                    session.PlayerAi.Stance = CommanderStance.Defend;
                    MatchJournal.Record(world, "stance", "defend");
                }
                if (session.Operation.PendingChoice != null) session.Choose(world, "left");
                session.Mode.Tick(world, Step);
                session.TickAi(world, Step);
                world.Step(Step);
                world.ClearEvents();
            }
            Assert.Greater(session.Operation.Checkpoints.Count, 0, "a checkpoint was kept");
            var resume = MatchJournal.Checkpoint(world, def.Id, 0, session.Operation);
            Assert.IsNotNull(resume);
            Assert.Greater(resume.Commands.Count, 2);
            Assert.IsTrue(resume.Inputs.Any(x => x.input == "stance"));

            // The same mission and seed, rebuilt and replayed.
            var (again, replayed) = Start(def, 9);
            var replay = new CheckpointReplay(resume, replayed, again);
            while (replay.Advance(Step, 200)) { }
            Assert.AreEqual(resume.Tick, again.Tick);
            Assert.IsTrue(replay.Matches, "the replay lands on the checkpoint's state");
            Assert.AreEqual(CommanderStance.Defend, replayed.PlayerAi.Stance, "the switches came back too");
            Assert.IsTrue(MatchJournal.Inputs.Any(x => x.input == "stance"), "and are in the new journal for the next restore");
        }
    }
}
