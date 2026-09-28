using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Hud;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Modes;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The Operations mode (prompt 6): tiers, the score, the records, the weekly rotation of
    /// mutators (deterministic by week), the one weekly reward ledger, and what the mutators do.
    /// </summary>
    public class OperationsModeTests
    {
        private static OperationsData Data => Operations.Data;

        [Test]
        public void FourTiersAndAtLeastFifteenMutatorsAreData()
        {
            CollectionAssert.AreEqual(new[] { "normal", "heroic", "iron", "legend" }, Data.Tiers.Select(t => t.Id).ToArray());
            Assert.GreaterOrEqual(Data.Mutators.Count, 15);
            Assert.AreEqual(Data.Mutators.Count, Data.Mutators.Select(m => m.Id).Distinct().Count(), "ids unique");
            foreach (var m in Data.Mutators)
            {
                Assert.AreNotEqual("mutator." + m.Id, Strings.Get("mutator." + m.Id), $"{m.Id} has a name");
                Assert.AreNotEqual("mutator." + m.Id + ".info", Strings.Get("mutator." + m.Id + ".info"), $"{m.Id} has a line");
                foreach (var x in m.Excludes) Assert.IsNotNull(Data.Mutator(x), $"{m.Id} excludes a mutator that exists ({x})");
            }
        }

        [Test]
        public void TheRotationIsTheSameEveryTimeCoversEveryMutatorAndNeverPairsExcludedOnes()
        {
            var a = Data.Rotation(9);
            var b = Data.Rotation(9);
            Assert.AreEqual(OperationsData.RotationWeeks, a.Count);
            CollectionAssert.AreEqual(a.Select(e => (e.operation, e.a.Id, e.b.Id)).ToArray(), b.Select(e => (e.operation, e.a.Id, e.b.Id)).ToArray(), "deterministic");
            foreach (var (_, x, y) in a) Assert.IsFalse(x.Clashes(y), $"{x.Id} and {y.Id} are never drawn together");
            var seen = new HashSet<string>(a.SelectMany(e => new[] { e.a.Id, e.b.Id }));
            Assert.AreEqual(Data.Mutators.Count, seen.Count, "every mutator comes up in half a year");
            Assert.AreEqual(a.Count, a.Select(e => e.a.Id + "+" + e.b.Id).Distinct().Count(), "no pair twice");
            // A week always gives the same entry; the next week another.
            Assert.AreEqual(Data.Weekly(202640, 9)?.a.Id, Data.Weekly(202640, 9)?.a.Id);
            Assert.AreNotEqual(Data.Weekly(202640, 9)?.a.Id + Data.Weekly(202640, 9)?.b.Id, Data.Weekly(202641, 9)?.a.Id + Data.Weekly(202641, 9)?.b.Id);
            Assert.IsNull(Data.Weekly(202640, 0), "no operations: no weekly entry");
        }

        [Test]
        public void TheScoreRewardsSpeedFewLossesAndTheHqAndScalesByTierAndMutators()
        {
            var s = Data.Scoring;
            var normal = Operations.Tier(0);
            var none = new List<MutatorDef>();
            Assert.AreEqual(0, s.Score(false, 300, 0, 1f, normal, none), "a loss scores nothing");
            var fast = s.Score(true, 600, 5, 1f, normal, none);
            var slow = s.Score(true, 1200, 5, 1f, normal, none);
            Assert.Greater(fast, slow);
            Assert.Greater(s.Score(true, 600, 0, 1f, normal, none), fast, "fewer losses");
            Assert.Greater(fast, s.Score(true, 600, 5, 0.3f, normal, none), "the HQ's health counts");
            // Exactly: 5000 + 3000 x (1 - 600/1500) + 2000 x (1 - 5/20) + 2000 x 1.
            Assert.AreEqual(5000 + 1800 + 1500 + 2000, fast);
            Assert.AreEqual((int)Math.Round(fast * 2.0), s.Score(true, 600, 5, 1f, Operations.Tier(3), none), "Legend doubles it");
            var two = new List<MutatorDef> { Data.Mutator("no_support"), Data.Mutator("veterans") };
            Assert.AreEqual((int)Math.Round(fast * 1.4), s.Score(true, 600, 5, 1f, normal, two), "each mutator adds its share");
        }

        [Test]
        public void RecordsKeepTheBestScoreAndTimePerTier()
        {
            PlayerProfile.ResetForTests();
            Assert.IsTrue(PlayerProfile.RecordOperation("op_test", 1, 9000, 800f));
            Assert.IsFalse(PlayerProfile.RecordOperation("op_test", 1, 7000, 700f), "not a better score");
            Assert.AreEqual(9000, PlayerProfile.BestScore("op_test", 1));
            Assert.AreEqual(700f, PlayerProfile.BestTime("op_test", 1), 1e-3f, "the faster time is kept anyway");
            Assert.AreEqual(0, PlayerProfile.BestScore("op_test", 2), "each tier has its own record");
            Assert.IsTrue(PlayerProfile.RecordOperation("op_test", 1, 9500, 900f));
            Assert.AreEqual(9500, PlayerProfile.BestScore("op_test", 1));
        }

        [Test]
        public void OneWeeklyLedgerPaysTheFortressAndTheOperationOnceAWeekEach()
        {
            PlayerProfile.ResetForTests();
            Assert.IsTrue(PlayerProfile.ClaimWeekly(202640, "operation"));
            Assert.IsFalse(PlayerProfile.ClaimWeekly(202640, "operation"), "once a week");
            Assert.IsTrue(PlayerProfile.RecordWeekly(202640, 3, true), "the fortress's own reward, same ledger");
            Assert.IsFalse(PlayerProfile.RecordWeekly(202640, 3, true));
            Assert.IsTrue(PlayerProfile.WeeklyClaimed(202640));
            Assert.IsTrue(PlayerProfile.ClaimWeekly(202641, "operation"), "a new week pays again");
            Assert.IsFalse(PlayerProfile.WeeklyClaimed(202641), "and the fortress's is open again");
        }

        [Test]
        public void MutatorsChangeTheCardsTheMissionAndTheStrength()
        {
            var catalog = GameContent.LoadCatalog();
            var player = new SideSetup { Income = 1f, Vehicles = new[] { "heavy_tank", "armored_car", "main_battle_tank", "attack_helicopter", "light_tank" }, Supports = new[] { "artillery_barrage", "repair_drop" } };
            var enemy = new SideSetup { StartCp = 10f, Income = 1f, Vehicles = new[] { "main_battle_tank", "attack_helicopter" } };
            var owned = new[] { "scout_jeep", "armored_car", "light_tank", "aa_vehicle", "mortar_carrier", "ifv" };
            Mutators.Apply(player, enemy, new[] { Data.Mutator("light_deck"), Data.Mutator("no_repair"), Data.Mutator("general_boost") }, catalog, owned);
            Assert.IsTrue(player.Vehicles.All(id => catalog.Vehicles[id].CpCost < 8), "under 8 CP only");
            Assert.GreaterOrEqual(player.Vehicles.Count, 4, "filled up from the vehicles the player owns");
            CollectionAssert.DoesNotContain(player.Supports, "repair_drop");
            Assert.AreEqual(15f, enemy.StartCp, 1e-3f);
            Assert.AreEqual(1.3f, enemy.Income, 1e-3f);

            var air = new SideSetup { StartCp = 10f, Vehicles = new[] { "main_battle_tank" } };
            Mutators.Apply(new SideSetup(), air, new[] { Data.Mutator("enemy_air") }, catalog, owned);
            Assert.IsTrue(air.Vehicles.Count > 0 && air.Vehicles.All(id => catalog.Vehicles[id].Flying), "aircraft only");

            var mission = Campaign.All.First(m => m.Waves != null);
            var timed = Mutators.Apply(mission, new[] { Data.Mutator("time_attack"), Data.Mutator("swarm") }, catalog);
            Assert.AreNotSame(mission, timed, "the campaign's own mission is untouched");
            if (mission.Goal is not (MissionGoal.Survive or MissionGoal.Protect))
                Assert.AreEqual((mission.TimeLimit > 0f ? mission.TimeLimit : 1500f) * 0.7f, timed.TimeLimit, 1e-2f);
            Assert.AreEqual(mission.ReinforceSize * 2, timed.ReinforceSize);
            CollectionAssert.AreEqual(Mutators.SwarmUnits, timed.Waves.Roster.ToArray());

            var strength = Mutators.Strength(new[] { Data.Mutator("towers_x2"), Data.Mutator("veterans") }, 1);
            Assert.AreEqual((2.5f, 1.5f), strength(catalog.Vehicles["gun_turret"]), "a tower: x2 health x1.25 veterans, x1.5 fire");
            Assert.AreEqual((1.25f, 1f), strength(catalog.Vehicles["main_battle_tank"]));
            Assert.IsNull(Mutators.Strength(new[] { Data.Mutator("towers_x2") }, 0), "the player's own side is untouched");
        }

        [Test]
        public void HarderTiersKeepTheWaves()
        {
            var mission = Campaign.All.First(m => m.Waves != null && m.Waves.Roster.Count > 0);
            var heroic = mission.Harder(1.3f);
            CollectionAssert.AreEqual(mission.Waves.Roster.ToArray(), heroic.Waves.Roster.ToArray(), "a harder tier's waves still come");
            CollectionAssert.AreEqual(mission.Waves.Spawns.ToArray(), heroic.Waves.Spawns.ToArray());
        }

        /// <summary>
        /// Every week of the rotation (its operation with its two mutators, on Normal) is won in
        /// most of five seeds with the deck a player has by then. Run with MB_BALANCE=1.
        /// </summary>
        [Test, Category("Balance"), Timeout(14400000)]
        public void EveryWeekOfTheRotationIsWinnableOverFiveSeeds()
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("balance check: set MB_BALANCE=1 to run it");
            var big = Operations.Big;
            if (big.Count == 0) Assert.Ignore("no big operations in the campaign data yet");
            var failures = new List<string>();
            var report = new System.Text.StringBuilder("ROTATION five seeds, Normal\n");
            foreach (var (index, a, b) in Data.Rotation(big.Count))
            {
                var mission = big[index];
                var wins = 0;
                var times = new List<float>();
                for (var seed = 1; seed <= 5; seed++)
                {
                    var (vehicles, supports) = CampaignTests.RealisticDeck(mission.Id);
                    MatchSettings.DeckVehicles.Clear();
                    MatchSettings.DeckVehicles.AddRange(vehicles);
                    MatchSettings.DeckSupports.Clear();
                    MatchSettings.DeckSupports.AddRange(supports);
                    MatchSettings.Mission = mission.Id;
                    MatchSettings.MissionTier = 0;
                    var run = new OperationRun { Mission = mission.Id, Tier = 0, Weekly = true };
                    run.Mutators.Add(a);
                    run.Mutators.Add(b);
                    MatchSettings.Run = run;
                    var world = new Sim.SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(mission.Map + "_" + mission.Variant), seed: seed);
                    var session = ModeSession.Create(GameModeKind.Campaign, false, world, seed);
                    var t = 0f;
                    for (; t < 32 * 60 && session.Mode.Result == null; t += 0.05f)
                    {
                        session.Mode.Tick(world, 0.05f);
                        session.TickAi(world, 0.05f);
                        world.Step(0.05f);
                        world.ClearEvents();
                    }
                    if (session.Mode.Result?.WinningTeam != 0) continue;
                    wins++;
                    times.Add(t / 60f);
                }
                MatchSettings.Run = null;
                report.Append($"{mission.Id} + {a.Id} + {b.Id}: {wins}/5, {(times.Count > 0 ? times.Average() : 0f):0.0} min\n");
                if (wins < 3) failures.Add($"{mission.Id} with {a.Id} and {b.Id}: {wins}/5");
            }
            UnityEngine.Debug.Log(report.ToString());
            Assert.IsEmpty(failures, "every week of the rotation is winnable");
        }

        [Test]
        public void TheMenuStillReachesEveryMode()
        {
            var reachable = new HashSet<GameModeKind>(MenuScreen.BattleModes.Concat(MenuScreen.OperationsModes));
            foreach (GameModeKind kind in Enum.GetValues(typeof(GameModeKind)))
                Assert.IsTrue(reachable.Contains(kind), $"{kind} is reachable from the menu");
        }
    }
}
