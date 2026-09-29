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
            // MB_DIFF may list several (Easy,Normal,Hard,VeryHard); MB_LIMIT the minutes a battle may run (30).
            var difficulties = string.IsNullOrEmpty(diff) ? new[] { AiDifficulty.Normal } : diff.Split(',').Select(d => (AiDifficulty)Enum.Parse(typeof(AiDifficulty), d)).ToArray();
            var limit = float.TryParse(Environment.GetEnvironmentVariable("MB_LIMIT"), out var minutes) ? minutes : 30f;
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
            foreach (var difficulty in difficulties)
            foreach (var kind in kinds)
            {
                var results = new List<(bool won, bool lost, float minutes, string text)>();
                foreach (var map in Maps[kind])
                    foreach (var seed in seeds)
                    {
                        var r = Play(kind, map, seed, difficulty, limit);
                        results.Add(r);
                        report.AppendLine($"{difficulty,-8} {kind,-14} {map,-10} s{seed}: {(r.won ? "WON " : r.lost ? "LOST" : "open")} {r.minutes,5:0.0} min  {r.text}");
                        Flush(report);
                    }
                var mins = results.Select(r => r.minutes).OrderBy(m => m).ToList();
                var median = mins.Count % 2 == 1 ? mins[mins.Count / 2] : (mins[mins.Count / 2 - 1] + mins[mins.Count / 2]) * 0.5f;
                report.AppendLine($"{difficulty,-8} {kind,-14} SUMMARY ({difficulty}): won {results.Count(r => r.won)}/{results.Count}, median {median:0.0} min, range {mins.First():0.0}-{mins.Last():0.0}");
            }
            report.AppendLine("idle over 20 s: " + string.Join(", ", IdleWho.OrderByDescending(p => p.Value).Take(14).Select(p => $"{p.Key} {p.Value}")));
            IdleWho.Clear();
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

        /// <summary>A long sweep's table so far (MB_CV_OUT), after every battle.</summary>
        private static void Flush(StringBuilder report)
        {
            var dir = Environment.GetEnvironmentVariable("MB_CV_OUT");
            if (!string.IsNullOrEmpty(dir))
                System.IO.File.WriteAllText(System.IO.Path.Combine(dir, "modes_" + (Environment.GetEnvironmentVariable("MB_CV_TAG") ?? "now") + ".txt"), report.ToString());
        }

        internal static (bool won, bool lost, float minutes, string text) Play(GameModeKind kind, string map, int seed, AiDifficulty difficulty, float limit = 30f)
        {
            MatchSettings.Mode = kind;
            MatchSettings.Difficulty = difficulty;
            var at = map.IndexOf('@');
            WeeklySession.TestStage = at > 0 ? int.Parse(map.Substring(at + 1)) : null;
            if (at > 0) map = map.Substring(0, at);
            // Boss Rush goes home to the battlefield chosen (MatchSettings.Map) after a sea boss or an arena.
            var savedMap = MatchSettings.Map;
            if (at < 0) MatchSettings.Map = map;
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(ModeSession.MapFile(kind, map)), seed: seed);
            // DECISIONS 21G: MB_GEAR=1 plays the player's side as a geared rank 7 arsenal (the campaign's curve entering act IV).
            var gear = Environment.GetEnvironmentVariable("MB_GEAR") == "1";
            if (gear) world.SetBoosts(0, _ => BossBalanceMeasure.Geared, _ => BossBalanceMeasure.GearedStrike, strikeRank: _ => 7);
            // As MatchRunner: the enemy keeps pace with the deck's edge by the difficulty's share.
            var deckEdge = MatchSettings.DeckVehicles.Select(_ => gear ? BossBalanceMeasure.Geared : MachineBrigade.Sim.Content.VehicleBoost.None).ToList();
            ModeSession.KeepPace(world, deckEdge, difficulty, kind);
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
            var roster = "";
            var lastBoss = MachineBrigade.Sim.Core.EntityId.None;
            var bossAt = 0f;
            var defeated = 0;
            int peak0 = 0, peak1 = 0;
            // DECISIONS 21G: the player's vehicles standing idle (no order, no target) while enemies are on the field.
            var idleSince = new Dictionary<MachineBrigade.Sim.Core.EntityId, float>();
            var idleSeconds = 0f;
            var busySeconds = 0f;
            var idleSpells = 0;
            var longestIdle = 0f;
            for (; t < limit * 60f; t += 0.05f)
            {
                mode.Tick(world, 0.05f);
                session.TickAi(world, 0.05f);
                world.Step(0.05f);
                // DECISIONS 21G: Boss Rush switches battlefield for a sea boss, an arena or a train's line, as the game does.
                if (session is BossRushSession rushing && rushing.SwitchTo is { } carry)
                {
                    BossRushSession.Pending = carry;
                    world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(ModeSession.MapFile(kind, map)), seed: seed);
                    if (gear) world.SetBoosts(0, _ => BossBalanceMeasure.Geared, _ => BossBalanceMeasure.GearedStrike, strikeRank: _ => 7);
                    ModeSession.KeepPace(world, deckEdge, difficulty, kind);
                    session = ModeSession.Create(kind, false, world, seed);
                    mode = session.Mode;
                    idleSince.Clear();
                    continue;
                }
                foreach (var e in world.Events)
                    if (e.Kind == SimEventKind.VehicleDestroyed)
                    {
                        if (e.Team == 1) kills++;
                        else if (e.Team == 0) losses++;
                    }
                world.ClearEvents();
                if (world.Tick % 20 == 0) TrackIdle(world, t, idleSince, ref idleSeconds, ref busySeconds, ref idleSpells, ref longestIdle);
                if (world.TryGetEconomy(0, out var e0)) peak0 = Math.Max(peak0, e0.ArmyCp);
                if (world.TryGetEconomy(1, out var e1)) peak1 = Math.Max(peak1, e1.ArmyCp);
                var now = mode is SiegeMode s2 ? s2.Stage : mode is AssaultMode a2 ? a2.Sector : 0;
                if (now != stage)
                {
                    stage = now;
                    stages += $" {stage}@{t / 60f:0.0}";
                    if (mode is SiegeMode defended && defended.Rules.PlayerDefends && outerLost < 0f && stage >= 2) outerLost = t / 60f;
                }
                if (mode is BossRushMode seen && seen.Boss.IsValid && seen.Boss != lastBoss && world.TryGetVehicle(seen.Boss, out var came))
                {
                    lastBoss = seen.Boss;
                    roster += " " + came.Def.Id;
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
            MatchSettings.Map = savedMap;
            BossRushSession.Pending = null;
            var result = mode.Result;
            var won = result != null ? result.Value.WinningTeam == 0 : outcome != null && outcome.Result > 0;
            var lost = result != null ? result.Value.WinningTeam == 1 : outcome != null && outcome.Result < 0;
            var text = $"kills {kills} losses {losses} idle {(busySeconds > 0f ? idleSeconds / busySeconds : 0f):P0} spells>20s {idleSpells} longest {longestIdle:0}s";
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
                    text += $" bosses {b.Defeated}/{b.Total}, minutes each{bossTimes}, roster{roster}";
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

        /// <summary>DECISIONS 21G: who stood idle over 20 s (def id, and "/ammo" when it was reloading), over the sweep.</summary>
        internal static readonly Dictionary<string, int> IdleWho = new();

        /// <summary>Once a second: each of the player's ground vehicles with no order and no target while an enemy vehicle is on the field.</summary>
        private static void TrackIdle(SimWorld world, float t, Dictionary<MachineBrigade.Sim.Core.EntityId, float> since, ref float idle, ref float busy,
            ref int spells, ref float longest)
        {
            var enemies = false;
            foreach (var v in world.VehicleList)
                if (v.IsAlive && v.Team == 1 && !v.Def.Static) { enemies = true; break; }
            foreach (var v in world.VehicleList)
            {
                if (!v.IsAlive || v.Team != 0 || v.Def.Static || v.Flying || v.Scripted || v.Def.CpCost <= 0) continue;
                if (!enemies) { since.Remove(v.Id); continue; }
                busy += 1f;
                var standing = v.Order.Kind == MachineBrigade.Sim.Entities.OrderKind.Idle && !v.Target.IsValid;
                if (!standing)
                {
                    if (since.TryGetValue(v.Id, out var from) && t - from > 20f)
                    {
                        spells++;
                        var nearest = float.MaxValue;
                        var seen = false;
                        foreach (var e in world.VehicleList)
                            if (e.IsAlive && e.Team == 1 && !e.Flying)
                            {
                                var d = System.Numerics.Vector2.Distance(e.Position, v.Position);
                                if (d < nearest) { nearest = d; seen = e.IsVisibleTo(0); }
                            }
                        var band = nearest < 45f ? "near" : nearest < 110f ? "mid" : "far";
                        var why = v.Def.Id + (v.OutOfAmmo ? "/ammo" : v.UnderPlayerControl(world.Time) ? "/manual" : v.IsEscort ? "/escort" : "") + "/" + band + (seen ? "+seen" : "");
                        IdleWho[why] = (IdleWho.TryGetValue(why, out var n) ? n : 0) + 1;
                    }
                    since.Remove(v.Id);
                    continue;
                }
                idle += 1f;
                if (!since.ContainsKey(v.Id)) since[v.Id] = t;
                longest = Math.Max(longest, t - since[v.Id]);
            }
        }
    }
}
