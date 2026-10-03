using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using UnityEngine;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Balance pack (lane B, §4 / §7.5): fixed deterministic battles (a few modes and maps, fixed seeds, both sides
    /// played by their commanders) are stepped for a fixed number of ticks and the battle's fingerprint
    /// (<see cref="SimWorld.StateHash"/>) is taken every <see cref="Every"/> ticks. Moving code constants into data must
    /// leave every fingerprint identical.
    ///
    /// The baseline lives in Docs/export/replay_hashes.txt (committed). The first run with no file records it (and
    /// passes); MB_REPLAY_RECORD=1 records it again on purpose (after a value change that Docs/export/CHANGES.md lists).
    /// A scenario named in <see cref="ChangedByRules"/> may differ (a rule C / D value change, listed in CHANGES.md):
    /// the test logs it and does not fail.
    /// </summary>
    public class ReplayHashTests
    {
        private const float Step = 0.05f;
        private const int Ticks = 2400;
        private const int Every = 400;

        private static readonly (string name, GameModeKind kind, string map, int seed)[] Scenarios =
        {
            ("conquest_ashfield_s3", GameModeKind.Conquest, "ashfield", 3),
            ("deathmatch_greenvale_s5", GameModeKind.Deathmatch, "greenvale", 5),
            ("hill_dunebreak_s4", GameModeKind.KingOfTheHill, "dunebreak", 4),
            ("siege_ashfield_s7", GameModeKind.Siege, "ashfield", 7),
            ("endless_ironport_s11", GameModeKind.Endless, "ironport", 11),
            ("survival_frostpeak_s6", GameModeKind.Survival, "frostpeak", 6),
            ("bossrush_ashfield_s2", GameModeKind.BossRush, "ashfield", 2),
            ("campaign_framework_s9", GameModeKind.Campaign, "ashfield_conquest", 9),
        };

        /// <summary>
        /// The pack's rule C / D value changes so far (Docs/export/CHANGES.md). A baseline recorded under an older number
        /// lets the scenarios of <see cref="ChangedByRules"/> differ; a baseline of this number must match exactly.
        /// </summary>
        internal const int RulesVersion = 1;

        /// <summary>
        /// Scenarios a rule C / D value change of this pack may move (scenario, the CHANGES.md items). The constant moves
        /// (rule B) must keep every fingerprint. D1: no pull-back of damaged vehicles by the wave AIs (BossRush, Survival,
        /// mission waves); D2: no jet break-off on health; C1: the supply threshold x 1.16 (every mode with an economy).
        /// </summary>
        internal static readonly Dictionary<string, string> ChangedByRules = new()
        {
            ["conquest_ashfield_s3"] = "C1 supply x1.16, D2 jets",
            ["deathmatch_greenvale_s5"] = "C1 supply x1.16, D2 jets",
            ["hill_dunebreak_s4"] = "C1 supply x1.16, D2 jets",
            ["siege_ashfield_s7"] = "C1 supply x1.16, D2 jets",
            ["endless_ironport_s11"] = "C1 supply x1.16, D2 jets",
            ["survival_frostpeak_s6"] = "D1 wave AI pull-back, C1 supply x1.16, D2 jets",
            ["bossrush_ashfield_s2"] = "D1 wave AI pull-back, C1 supply x1.16, D2 jets",
            ["campaign_framework_s9"] = "D1 mission wave AI, C1 supply x1.16 (campaign cap 24), D2 jets",
        };

        private static string BaselinePath =>
            Path.GetFullPath(Path.Combine(Application.dataPath, "..", "Docs", "export", "replay_hashes.txt"));

        [SetUp]
        public void SetUp() => PlayerProfile.ResetForTests();

        /// <summary>One scenario played: its fingerprints every <see cref="Every"/> ticks, the last one at the end.</summary>
        internal static List<ulong> Play(GameModeKind kind, string map, int seed)
        {
            MatchSettings.Mode = kind;
            MatchSettings.Difficulty = Sim.AI.AiDifficulty.Normal;
            MatchSettings.Weather = WeatherKind.Random;
            MatchSettings.MissionTier = 0;
            MatchSettings.Run = null;
            MatchSettings.DeckVehicles.Clear();
            MatchSettings.DeckVehicles.AddRange(new[] { "main_battle_tank", "ifv", "armored_car", "aa_vehicle", "mlrs" });
            MatchSettings.DeckSupports.Clear();
            BossRushSession.Pending = null;
            SimWorld world;
            ModeSession session;
            if (kind == GameModeKind.Campaign)
            {
                var def = MissionDef.ListFromJson(OperationTests.Json)[0];
                def.EnemyAi = "commander";
                def.EnemyDeck = new[] { "armored_car", "main_battle_tank", "ifv" };
                world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(map), seed: seed);
                session = ModeSession.Create(GameModeKind.Campaign, false, world, seed, def);
            }
            else
            {
                world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(ModeSession.MapFile(kind, map)), seed: seed);
                session = ModeSession.Create(kind, false, world, seed);
            }
            var hashes = new List<ulong>();
            for (var i = 1; i <= Ticks; i++)
            {
                if (session.Mode.Result == null && !world.IsOver)
                {
                    if (session is MissionSession mission && mission.Operation?.PendingChoice != null) mission.Choose(world, "left");
                    session.Mode.Tick(world, Step);
                    session.TickAi(world, Step);
                    world.Step(Step);
                    world.ClearEvents();
                }
                if (i % Every == 0) hashes.Add(world.StateHash());
            }
            return hashes;
        }

        private static Dictionary<string, string> ReadBaseline(string path, out int rules)
        {
            var result = new Dictionary<string, string>();
            rules = 0;
            foreach (var raw in File.ReadAllLines(path))
            {
                var line = raw.Trim();
                if (line.StartsWith("# rules:") && int.TryParse(line.Substring(8).Trim(), out var version)) rules = version;
                if (line.Length == 0 || line.StartsWith("#")) continue;
                var space = line.IndexOf(' ');
                if (space <= 0) continue;
                result[line.Substring(0, space)] = line.Substring(space + 1).Trim();
            }
            return result;
        }

        [Test]
        public void TheFixedBattlesKeepTheirFingerprints()
        {
            var now = new Dictionary<string, string>();
            foreach (var (name, kind, map, seed) in Scenarios)
                now[name] = string.Join(" ", Play(kind, map, seed).Select(h => h.ToString("X16")));

            var path = BaselinePath;
            var record = Environment.GetEnvironmentVariable("MB_REPLAY_RECORD") == "1" || !File.Exists(path);
            if (record)
            {
                var text = new StringBuilder();
                text.Append("# Replay-hash baseline (Tests/EditMode/ReplayHashTests.cs): scenario, then SimWorld.StateHash every ");
                text.Append(Every).Append(" ticks over ").Append(Ticks).Append(" ticks (20 Hz).\n");
                text.Append("# Recorded ").Append(DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm")).Append(" UTC. Record again only with MB_REPLAY_RECORD=1.\n");
                text.Append("# rules: ").Append(RulesVersion).Append('\n');
                foreach (var (name, _, _, _) in Scenarios) text.Append(name).Append(' ').Append(now[name]).Append('\n');
                Directory.CreateDirectory(Path.GetDirectoryName(path));
                File.WriteAllText(path, text.ToString());
                Debug.Log($"[ReplayHash] baseline recorded: {path}");
                return;
            }

            var kept = ReadBaseline(path, out var baselineRules);
            var failures = new StringBuilder();
            foreach (var (name, _, _, _) in Scenarios)
            {
                if (!kept.TryGetValue(name, out var before))
                {
                    failures.Append(name).Append(": not in the baseline (record with MB_REPLAY_RECORD=1)\n");
                    continue;
                }
                if (before == now[name])
                {
                    Debug.Log($"[ReplayHash] {name}: identical");
                    continue;
                }
                var a = before.Split(' ');
                var b = now[name].Split(' ');
                var first = 0;
                while (first < a.Length && first < b.Length && a[first] == b[first]) first++;
                var where = $"first difference at tick {(first + 1) * Every}";
                if (baselineRules < RulesVersion && ChangedByRules.TryGetValue(name, out var why))
                    Debug.Log($"[ReplayHash] {name}: changed by a listed rule value change ({why}), {where}");
                else
                    failures.Append(name).Append(": ").Append(where).Append('\n');
            }
            Assert.AreEqual("", failures.ToString(), "replay fingerprints moved:\n" + failures);
        }

        [Test]
        public void TheSameBattleTwiceGivesTheSameFingerprints()
        {
            var first = Play(GameModeKind.Conquest, "greenvale", 8);
            var second = Play(GameModeKind.Conquest, "greenvale", 8);
            Assert.AreEqual(string.Join(",", first), string.Join(",", second), "the fixed battle is deterministic in one run");
        }
    }
}
