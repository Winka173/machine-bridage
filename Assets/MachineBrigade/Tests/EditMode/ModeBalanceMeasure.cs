using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 13 H: every mode played whole, both sides by their commanders (the player's by its auto
    /// commander, with the deck and base it has), on two or three battlefields and two seeds (the owner's
    /// rule: short measurements; the testing phase sweeps more). Prints for each match the result, its
    /// length and what the mode keeps count of. Run with MB_BALANCE=1; MB_MODES=Conquest,Defend limits the
    /// modes, MB_SEEDS=1,2 the seeds, MB_DIFF the difficulty (Normal).
    /// </summary>
    public class ModeBalanceMeasure
    {
        private static readonly Dictionary<GameModeKind, string[]> Maps = new()
        {
            [GameModeKind.Conquest] = new[] { "ashfield", "dunebreak", "ironport" },
            [GameModeKind.Deathmatch] = new[] { "ashfield", "dunebreak", "ironport" },
            [GameModeKind.KingOfTheHill] = new[] { "ashfield", "dunebreak", "redrock" },
            [GameModeKind.Assault] = new[] { "ironport", "redrock", "ashfield" },
            [GameModeKind.Siege] = new[] { "ashfield", "dunebreak", "ironport" },
            [GameModeKind.Defend] = new[] { "ashfield", "dunebreak", "ironport" },
            [GameModeKind.Endless] = new[] { "ashfield", "dunebreak" },
            [GameModeKind.Survival] = new[] { "ashfield", "greenvale" },
            [GameModeKind.BossRush] = new[] { "ashfield", "dunebreak" },
            // The weekly fortress from each stage a week's earlier attacks may have reached (H.6).
            [GameModeKind.Weekly] = new[] { "weekly@1", "weekly@2", "weekly@3" },
        };

        /// <summary>The sample player deck (prompt 13 H and the difficulty ladder of J): one of each role.</summary>
        internal static readonly string[] SampleDeck =
            { "main_battle_tank", "ifv", "tank_destroyer", "light_tank", "mlrs", "aa_vehicle", "attack_helicopter", "engineer_vehicle" };

        [Test, Explicit("a measurement: run it by name with MB_BALANCE=1"), Category("Balance"), Timeout(7200000)]
        public void PrintEveryMode()
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("mode balance: set MB_BALANCE=1");
            var only = Environment.GetEnvironmentVariable("MB_MODES");
            var kinds = string.IsNullOrEmpty(only) ? Maps.Keys.ToList() : only.Split(',').Select(s => (GameModeKind)Enum.Parse(typeof(GameModeKind), s)).ToList();
            var seedList = Environment.GetEnvironmentVariable("MB_SEEDS");
            var seeds = string.IsNullOrEmpty(seedList) ? new[] { 1, 2 } : seedList.Split(',').Select(int.Parse).ToArray();
            var diff = Environment.GetEnvironmentVariable("MB_DIFF");
            var difficulty = string.IsNullOrEmpty(diff) ? AiDifficulty.Normal : (AiDifficulty)Enum.Parse(typeof(AiDifficulty), diff);
            // The player's deck: a sample mid-game deck of eight over the roles (the test build unlocks every card,
            // so the enemy draws from all of them); MB_DECK=starter for the seven starter cards, or a list.
            var deck = Environment.GetEnvironmentVariable("MB_DECK");
            var vehicles = string.IsNullOrEmpty(deck) ? SampleDeck : deck == "starter" ? Progression.StarterVehicles : deck.Split(',');
            var saved = MatchSettings.DeckVehicles.ToList();
            MatchSettings.DeckVehicles.Clear();
            MatchSettings.DeckVehicles.AddRange(vehicles);
            var report = new StringBuilder();
            report.AppendLine($"player deck: {string.Join(", ", vehicles)}");
            var started = DateTime.Now;
            foreach (var kind in kinds)
            {
                var results = new List<(bool won, bool lost, float minutes, string text)>();
                foreach (var map in Maps[kind])
                    foreach (var seed in seeds)
                    {
                        var r = Play(kind, map, seed, difficulty);
                        results.Add(r);
                        report.AppendLine($"{kind,-14} {map,-10} s{seed}: {(r.won ? "WON " : r.lost ? "LOST" : "open")} {r.minutes,5:0.0} min  {r.text}");
                    }
                var mins = results.Select(r => r.minutes).OrderBy(m => m).ToList();
                var median = mins.Count % 2 == 1 ? mins[mins.Count / 2] : (mins[mins.Count / 2 - 1] + mins[mins.Count / 2]) * 0.5f;
                report.AppendLine($"{kind,-14} SUMMARY ({difficulty}): won {results.Count(r => r.won)}/{results.Count}, median {median:0.0} min, range {mins.First():0.0}-{mins.Last():0.0}");
            }
            report.AppendLine($"({(DateTime.Now - started).TotalSeconds:0} s)");
            MatchSettings.DeckVehicles.Clear();
            MatchSettings.DeckVehicles.AddRange(saved);
            TestContext.Out.WriteLine(report.ToString());
            Debug.Log("[ModeBalanceMeasure]\n" + report);
            var dir = Environment.GetEnvironmentVariable("MB_CV_OUT");
            if (!string.IsNullOrEmpty(dir))
                System.IO.File.WriteAllText(System.IO.Path.Combine(dir, "modes_" + (Environment.GetEnvironmentVariable("MB_CV_TAG") ?? "now") + ".txt"), report.ToString());
            Assert.Pass();
        }

        internal static (bool won, bool lost, float minutes, string text) Play(GameModeKind kind, string map, int seed, AiDifficulty difficulty, float limit = 30f)
        {
            MatchSettings.Mode = kind;
            MatchSettings.Difficulty = difficulty;
            var at = map.IndexOf('@');
            WeeklySession.TestStage = at > 0 ? int.Parse(map.Substring(at + 1)) : null;
            if (at > 0) map = map.Substring(0, at);
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(ModeSession.MapFile(kind, map)), seed: seed);
            var session = ModeSession.Create(kind, false, world, seed);
            WeeklySession.TestStage = null;
            var mode = session.Mode;
            var t = 0f;
            var kills = 0;
            var losses = 0;
            MatchOutcome outcome = null;
            var stages = "";
            var stage = mode is SiegeMode sm ? sm.Stage : mode is AssaultMode am ? am.Sector : 0;
            var outerLost = -1f;
            var bossTimes = "";
            var bossAt = 0f;
            var defeated = 0;
            int peak0 = 0, peak1 = 0;
            for (; t < limit * 60f; t += 0.05f)
            {
                mode.Tick(world, 0.05f);
                session.TickAi(world, 0.05f);
                world.Step(0.05f);
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.VehicleDestroyed)
                    {
                        if (e.Team == 1) kills++;
                        else if (e.Team == 0) losses++;
                    }
                world.ClearEvents();
                if (world.TryGetEconomy(0, out var e0)) peak0 = Math.Max(peak0, e0.ArmyCp);
                if (world.TryGetEconomy(1, out var e1)) peak1 = Math.Max(peak1, e1.ArmyCp);
                var now = mode is SiegeMode s2 ? s2.Stage : mode is AssaultMode a2 ? a2.Sector : 0;
                if (now != stage)
                {
                    stage = now;
                    stages += $" {stage}@{t / 60f:0.0}";
                    if (mode is SiegeMode defended && defended.Rules.PlayerDefends && outerLost < 0f && stage >= 2) outerLost = t / 60f;
                }
                if (mode is BossRushMode rush && rush.Defeated != defeated)
                {
                    defeated = rush.Defeated;
                    bossTimes += $" {(t - bossAt) / 60f:0.0}";
                    bossAt = t;
                }
                if (mode.Result != null) break;
                if (((int)(t * 20f)) % 20 == 0 && (outcome = session.Outcome(world, kills, losses)) != null) break;
            }
            var result = mode.Result;
            var won = result != null ? result.Value.WinningTeam == 0 : outcome != null && outcome.Result > 0;
            var lost = result != null ? result.Value.WinningTeam == 1 : outcome != null && outcome.Result < 0;
            var text = $"kills {kills} losses {losses}";
            switch (mode)
            {
                case SiegeMode s:
                    text += $" stages{stages} waves {s.Wave} progress {s.Progress(world):P0}" + (s.Rules.PlayerDefends ? $" outer line {(outerLost >= 0f ? $"lost at {outerLost:0.0}" : "held")}" : "");
                    break;
                case DeathmatchMode d:
                    text += $" score {d.Score(0)}:{d.Score(1)} of {d.ScoreTarget} (kills {d.Kills(0)}:{d.Kills(1)})";
                    break;
                case KingOfTheHillMode h:
                    text += $" score {h.Score(0)}:{h.Score(1)} of {h.ScoreTarget}";
                    break;
                case AssaultMode a:
                    text += $" sectors{stages} taken {a.Taken}";
                    break;
                case BossRushMode b:
                    text += $" bosses {b.Defeated}/{b.Total}, minutes each{bossTimes}";
                    break;
                case ConquestMode c:
                    text += $" tickets {c.Tickets(0)}:{c.Tickets(1)}";
                    break;
            }
            if (session is SurvivalSession survival) text += $" wave {survival.Survival.Wave}";
            if (Environment.GetEnvironmentVariable("MB_SHOW_DECK") == "1" && world.TryGetEconomy(1, out var enemy))
                text += $" | army peak {peak0}:{peak1} | enemy deck {string.Join(" ", enemy.Vehicles)}";
            return (won, lost, t / 60f, text);
        }
    }
}
