using System.Collections.Generic;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>Every campaign mission loads and plays to an end with the player's commander AI in charge.</summary>
    public class CampaignTests
    {
        private List<string> _vehicles, _supports;
        private string _mission;

        private static IEnumerable<string> Missions()
        {
            foreach (var m in Campaign.All) yield return m.Id;
        }

        [SetUp]
        public void SetUp()
        {
            _vehicles = new List<string>(MatchSettings.DeckVehicles);
            _supports = new List<string>(MatchSettings.DeckSupports);
            _mission = MatchSettings.Mission;
        }

        [TearDown]
        public void TearDown()
        {
            MatchSettings.DeckVehicles.Clear();
            MatchSettings.DeckVehicles.AddRange(_vehicles);
            MatchSettings.DeckSupports.Clear();
            MatchSettings.DeckSupports.AddRange(_supports);
            MatchSettings.Mission = _mission;
        }

        [Test]
        public void TwelveMissionsOverFourBattlefieldsEachEndingInABoss()
        {
            Assert.AreEqual(12, Campaign.All.Count);
            var catalog = GameContent.LoadCatalog();
            foreach (var m in Campaign.All)
            {
                Assert.DoesNotThrow(() => GameContent.LoadMap(m.Map + "_" + m.Variant), m.Id);
                if (m.Boss != null) Assert.IsTrue(catalog.Vehicles[m.Boss.Def].Boss, $"{m.Id}: {m.Boss.Def} is a boss");
                foreach (var id in m.EnemyDeck) Assert.IsTrue(catalog.Vehicles.ContainsKey(id), $"{m.Id}: enemy card {id}");
            }
            for (var i = 2; i < 12; i += 3)
                Assert.IsTrue(Campaign.All[i].Goal is MissionGoal.Boss or MissionGoal.Intercept, $"mission {i + 1} is a boss fight");
        }

        [TestCaseSource(nameof(Missions))]
        public void MissionPlaysToAnEnd(string id)
        {
            var def = Campaign.Get(id);
            MatchSettings.Mission = id;
            // A strong but realistic deck: what a player has by the late campaign.
            MatchSettings.DeckVehicles.Clear();
            MatchSettings.DeckVehicles.AddRange(new[]
            {
                "light_tank", "main_battle_tank", "heavy_tank", "aa_vehicle", "tank_destroyer", "attack_helicopter", "mlrs", "apc",
            });
            MatchSettings.DeckSupports.Clear();
            MatchSettings.DeckSupports.AddRange(new[] { "artillery_barrage", "airstrike" });

            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(def.Map + "_" + def.Variant), seed: 5);
            var session = ModeSession.Create(GameModeKind.Campaign, false, world, 5);
            var mission = (MissionSession)session;
            const float step = 0.05f;
            var seconds = 0f;
            for (; seconds < 22 * 60 && session.Mode.Result == null; seconds += step)
            {
                session.Mode.Tick(world, step);
                session.TickAi(world, step);
                world.Step(step);
                world.ClearEvents();
            }
            var result = session.Mode.Result;
            Debug.Log($"Mission {id} ({def.Goal}): {(result?.WinningTeam == 0 ? "WON" : result == null ? "UNFINISHED" : "LOST")} " +
                      $"after {seconds / 60f:0.0} min, progress {mission.Mission.Progress(world):P0}, losses {mission.Mission.Losses}, " +
                      $"kills {mission.Mission.Kills}");
            Assert.IsNotNull(result, "a mission always ends (win, clock or defeat)");
        }
    }
}
