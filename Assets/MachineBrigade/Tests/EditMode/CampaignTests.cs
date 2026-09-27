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

        /// <summary>Starter cards plus the unlocks of every earlier mission: six strongest vehicles, two best supports.</summary>
        internal static (List<string> vehicles, List<string> supports) RealisticDeck(string missionId)
        {
            var catalog = GameContent.LoadCatalog();
            var owned = new List<string>(Progression.StarterVehicles);
            var supports = new List<string>(Progression.StarterSupports);
            foreach (var m in Campaign.All)
            {
                if (m.Id == missionId) break;
                foreach (var id in m.Unlocks)
                {
                    if (catalog.Vehicles.ContainsKey(id) && !owned.Contains(id)) owned.Add(id);
                    else if (catalog.TryGetSupport(id, out _) && !supports.Contains(id)) supports.Add(id);
                }
            }
            owned.Sort((a, b) => catalog.Vehicle(b).CpCost.CompareTo(catalog.Vehicle(a).CpCost));
            var deck = owned.GetRange(0, System.Math.Min(6, owned.Count));
            // Keep an anti-air card if there is one: skies are busy by the midgame.
            if (!deck.Exists(v => catalog.Vehicle(v).Class == UnitClass.AntiAir))
            {
                var aa = owned.Find(v => catalog.Vehicle(v).Class == UnitClass.AntiAir);
                if (aa != null) deck[deck.Count - 1] = aa;
            }
            supports.Sort((a, b) => catalog.Supports[b].CpCost.CompareTo(catalog.Supports[a].CpCost));
            return (deck, supports.GetRange(0, System.Math.Min(2, supports.Count)));
        }

        [Test]
        public void ABootCampThenSixteenMissionsWithABossEveryThird()
        {
            Assert.AreEqual(17, Campaign.All.Count);
            Assert.IsTrue(Campaign.All[0].Optional, "the boot camp is optional");
            var catalog = GameContent.LoadCatalog();
            foreach (var m in Campaign.All)
            {
                Assert.DoesNotThrow(() => GameContent.LoadMap(m.Map + "_" + m.Variant), m.Id);
                if (m.Boss != null) Assert.IsTrue(catalog.Vehicles[m.Boss.Def].Boss, $"{m.Id}: {m.Boss.Def} is a boss");
                foreach (var id in m.EnemyDeck) Assert.IsTrue(catalog.Vehicles.ContainsKey(id), $"{m.Id}: enemy card {id}");
            }
            for (var i = 3; i < 17; i += 3)
                Assert.IsTrue(Campaign.All[i].Goal is MissionGoal.Boss or MissionGoal.Intercept, $"mission {i} is a boss fight");
        }

        [TestCaseSource(nameof(Missions))]
        public void MissionPlaysToAnEnd(string id)
        {
            var def = Campaign.Get(id);
            MatchSettings.Mission = id;
            // The deck a player really has at this point: the starter cards plus everything the
            // missions before this one unlocked, the six strongest vehicles of them.
            var (vehicles, supports) = RealisticDeck(id);
            MatchSettings.DeckVehicles.Clear();
            MatchSettings.DeckVehicles.AddRange(vehicles);
            MatchSettings.DeckSupports.Clear();
            MatchSettings.DeckSupports.AddRange(supports);

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
