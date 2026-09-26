using System.Collections.Generic;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>Whole Conquest matches between two AIs with the shipped content, headless.</summary>
    public class ConquestBattleTests
    {
        [TestCase("ashfield")]
        [TestCase("dunebreak")]
        [TestCase("frostpeak")]
        [TestCase("ironport")]
        public void AiVersusAiConquestUsesTheWholeRosterAndFinishes(string mapId)
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(mapId + "_conquest"), seed: 77);
            var mode = new ConquestMode(new ConquestRules
            {
                PlayerVehicles = MatchSettings.AllVehicles,
                PlayerSupports = MatchSettings.AllSupports,
                EnemyVehicles = MatchSettings.AllVehicles,
                EnemySupports = MatchSettings.AllSupports,
            });
            mode.Setup(world);
            var a = new ConquestAi(mode, 0, 1, AiDifficulty.Hard, 5);
            var b = new ConquestAi(mode, 1, 0, AiDifficulty.Normal, 6);

            var deployed = new HashSet<string>();
            var strikes = new HashSet<string>();
            var captures = 0;
            var destroyed = 0;
            const float step = 0.05f;
            var seconds = 0f;
            for (; seconds < 20 * 60 && mode.Result == null; seconds += step)
            {
                mode.Tick(world, step);
                a.Tick(world, step);
                b.Tick(world, step);
                world.Step(step);
                foreach (var e in world.Events)
                {
                    if (e.Kind == SimEventKind.DeploymentQueued) deployed.Add(e.DefId);
                    else if (e.Kind == SimEventKind.StrikeWarning) strikes.Add(e.DefId);
                    else if (e.Kind == SimEventKind.PointCaptured && e.Team >= 0) captures++;
                    else if (e.Kind == SimEventKind.VehicleDestroyed) destroyed++;
                }
                world.ClearEvents();
            }

            Debug.Log($"Conquest AI match on {mapId}: {seconds / 60f:0.0} min, result {(mode.Result.HasValue ? mode.Result.Value.WinningTeam.ToString() : "none")}, " +
                      $"tickets {mode.Tickets(0)}:{mode.Tickets(1)}, captures {captures}, destroyed {destroyed}, " +
                      $"deployed [{string.Join(",", deployed)}], strikes [{string.Join(",", strikes)}]");
            Assert.Greater(captures, 2, "objectives change hands");
            Assert.Greater(destroyed, 10, "there is real fighting");
            Assert.GreaterOrEqual(deployed.Count, 5, "the AI buys a varied army");
            Assert.GreaterOrEqual(strikes.Count, 2, "the AI calls fire support");
            Assert.IsNotNull(mode.Result, "a match ends within 20 minutes");
        }
    }
}
