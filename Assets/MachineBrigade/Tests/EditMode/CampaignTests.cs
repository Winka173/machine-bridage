using System.Linq;
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
            // A deck a player would build: the dearest aircraft (one at most: air slots are scarce),
            // an anti-air card, an artillery card (the answer to a dug-in enemy), then the dearest
            // ground vehicles. Ties keep the order the cards were won in.
            var byCost = owned.Select((id, i) => (id, i)).OrderByDescending(c => catalog.Vehicle(c.id).CpCost).ThenBy(c => c.i)
                .Select(c => c.id).ToList();
            var deck = new List<string>();
            void Take(System.Func<VehicleDef, bool> fits)
            {
                var id = byCost.Find(v => !deck.Contains(v) && fits(catalog.Vehicle(v)));
                if (id != null && deck.Count < 6) deck.Add(id);
            }
            Take(d => d.Flying);
            Take(d => d.Class == UnitClass.AntiAir);
            Take(d => d.Class == UnitClass.Artillery || d.Weapon.MinRange > 0f);
            foreach (var id in byCost)
                if (deck.Count < 6 && !deck.Contains(id) && !catalog.Vehicle(id).Flying) deck.Add(id);
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

        /// <summary>
        /// Balance check, run by hand (it takes a while): each mission over five seeds with the
        /// deck a player really has, logging wins, time, progress and the peak army size.
        /// Runs only with the environment variable MB_BALANCE=1 (and -testFilter WinRateOverFiveSeeds).
        /// </summary>
        [Category("Balance")]
        [TestCaseSource(nameof(Missions))]
        public void WinRateOverFiveSeeds(string id)
        {
            if (System.Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("balance check: set MB_BALANCE=1 to run it");
            var wins = 0;
            var text = "";
            for (var seed = 1; seed <= 5; seed++)
            {
                var def = Campaign.Get(id);
                MatchSettings.Mission = id;
                var (vehicles, supports) = RealisticDeck(id);
                MatchSettings.DeckVehicles.Clear();
                MatchSettings.DeckVehicles.AddRange(vehicles);
                MatchSettings.DeckSupports.Clear();
                MatchSettings.DeckSupports.AddRange(supports);
                var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(def.Map + "_" + def.Variant), seed: seed);
                var session = ModeSession.Create(GameModeKind.Campaign, false, world, seed);
                var mission = (MissionSession)session;
                var t = 0f;
                var peak = 0;
                for (; t < 22 * 60 && session.Mode.Result == null; t += 0.05f)
                {
                    session.Mode.Tick(world, 0.05f);
                    session.TickAi(world, 0.05f);
                    world.Step(0.05f);
                    world.ClearEvents();
                    if (world.TryGetEconomy(0, out var economy) && economy.VehicleCount > peak) peak = economy.VehicleCount;
                }
                var won = session.Mode.Result?.WinningTeam == 0;
                if (won) wins++;
                text += $" s{seed}:{(won ? "W" : "L")}{t / 60f:0.0}m/{mission.Mission.Progress(world):P0}/peak {peak}";
            }
            Debug.Log($"SEEDS {id}: {wins}/5{text}");
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
