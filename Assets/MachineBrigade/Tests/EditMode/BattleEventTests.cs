using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>Supply drops and bomber raids happen in a real battle, and crates get claimed.</summary>
    public class BattleEventTests
    {
        [Test]
        public void CratesAreDroppedAndClaimedAndBombersRaidTheFront()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap("ashfield_conquest"), seed: 9);
            var mode = new ConquestMode(new ConquestRules
            {
                PlayerVehicles = MatchSettings.AllVehicles, PlayerSupports = MatchSettings.AllSupports,
                EnemyVehicles = MatchSettings.AllVehicles, EnemySupports = MatchSettings.AllSupports,
            });
            mode.Setup(world);
            var a = new ConquestAi(mode, 0, 1, AiDifficulty.Normal, 5);
            var b = new ConquestAi(mode, 1, 0, AiDifficulty.Normal, 6);
            var events = new BattleEvents(9);
            int dropped = 0, claimed = 0, raids = 0;
            for (var t = 0f; t < 8 * 60 && mode.Result == null; t += TestWorlds.Step)
            {
                mode.Tick(world, TestWorlds.Step);
                a.Tick(world, TestWorlds.Step);
                b.Tick(world, TestWorlds.Step);
                events.Tick(world, TestWorlds.Step);
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                {
                    if (e.Kind == SimEventKind.CrateIncoming) dropped++;
                    else if (e.Kind == SimEventKind.CrateClaimed) claimed++;
                    else if (e.Kind == SimEventKind.StrikeWarning && e.Team == Teams.Environment) raids++;
                }
                world.ClearEvents();
            }
            Debug.Log($"Battle events: {dropped} crates dropped, {claimed} claimed, {raids} bomber raids in {world.Time / 60:0.0} min, result {mode.Result?.WinningTeam}");
            Assert.GreaterOrEqual(dropped, 2, "crates come down every minute or two");
            Assert.GreaterOrEqual(claimed, 1, "and somebody grabs one");
            Assert.GreaterOrEqual(raids, 1, "bombers raid the front at least once");
        }
    }
}
