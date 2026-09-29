using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using Debug = UnityEngine.Debug;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 22 F.6: every commander against every deck style, the player's side led by its auto commander with the
    /// style's deck and the commander, against the mode's enemy (the same for a seed whoever leads), on Conquest (and
    /// Deathmatch for the style without points). The score of a battle is the ticket (or kill-score) margin at the end,
    /// -1 to 1; a commander is a style's best when its mean is the highest, or within <see cref="Tie"/> of it. Also:
    /// the economy commanders with catch-up, upkeep and the 45 % refund cap as the modes have them (there is no
    /// escalating income), Tide's simulation cost with many cheap units on the field, and Vault in a short and a long
    /// battle. Three seeds (the owner's rule; the testing phase runs five). Run with MB_BALANCE=1; MB_CMD_SEEDS,
    /// MB_CMD_STYLES, MB_CMD_ONLY (commander ids) and MB_CMD_MINUTES narrow it; MB_CV_OUT names the output folder.
    /// </summary>
    public class CommanderMeasure
    {
        /// <summary>Two means this close are the same result at three seeds.</summary>
        private const float Tie = 0.03f;

        internal sealed class Style
        {
            public string Name;
            public string[] Deck;
            public string[] Supports;
            public GameModeKind Mode = GameModeKind.Conquest;
            public float Minutes = 6f;
        }

        private static readonly string[] Supports = { "artillery_barrage", "airstrike", "smoke_screen", "repair_drop" };

        internal static readonly Style[] Styles =
        {
            new() { Name = "Balanced", Deck = ModeBalanceMeasure.SampleDeck },
            new() { Name = "Sustain", Deck = new[] { "engineer_vehicle", "main_battle_tank", "ifv", "bunker_vehicle", "tank_destroyer", "aa_vehicle", "ammo_carrier", "heavy_tank" } },
            new() { Name = "Air", Deck = new[] { "attack_helicopter", "gunship_heli", "fighter_jet", "attack_jet", "scout_heli", "aa_vehicle", "ifv", "main_battle_tank" } },
            new() { Name = "Recon", Deck = new[] { "scout_jeep", "armored_car", "tank_destroyer", "wheeled_gun", "recon_drone", "counter_battery_radar", "mlrs", "ifv" } },
            new() { Name = "Drones", Deck = new[] { "strike_drone", "fpv_carrier", "lancet_truck", "recon_drone", "swarm_carrier", "ew_jammer", "ifv", "aa_vehicle" } },
            new() { Name = "Blitz", Deck = new[] { "scout_jeep", "armored_car", "light_tank", "rocket_technical", "wheeled_gun", "ifv", "zu23_technical", "vbied" } },
            // Towers are fought over in Defend (the base's) more than in Conquest.
            new() { Name = "Fortress", Deck = new[] { "bunker_vehicle", "engineer_vehicle", "main_battle_tank", "tank_destroyer", "mlrs", "aa_vehicle", "ifv", "heavy_tank" },
                Supports = new[] { "field_tower", "artillery_barrage", "repair_drop", "smoke_screen" }, Mode = GameModeKind.Defend },
            new() { Name = "Artillery", Deck = new[] { "artillery", "mlrs", "mortar_carrier", "heavy_rocket_artillery", "siege_tank", "counter_battery_radar", "ifv", "main_battle_tank" } },
            new() { Name = "LongGame", Deck = ModeBalanceMeasure.SampleDeck, Minutes = 12f },
            new() { Name = "Points", Deck = new[] { "ifv", "armored_car", "light_tank", "main_battle_tank", "scout_jeep", "tank_destroyer", "aa_vehicle", "mlrs" } },
            new() { Name = "NoPoints", Deck = ModeBalanceMeasure.SampleDeck, Mode = GameModeKind.Deathmatch },
            new() { Name = "Swarm", Deck = new[] { "scout_jeep", "armored_car", "light_tank", "rocket_technical", "zu23_technical", "mortar_carrier", "aa_vehicle", "flame_tank" } },
            new() { Name = "Heavy", Deck = new[] { "twin_tank", "railgun_truck", "bmpt", "laser_tank", "heavy_tank", "attack_helicopter", "titan_tank", "long_sam" } },
            new() { Name = "Attrition", Deck = new[] { "tank_destroyer", "wheeled_gun", "railgun_truck", "ifv", "main_battle_tank", "aa_vehicle", "lancet_truck", "light_tank" } },
            new() { Name = "Hoard", Deck = new[] { "heavy_tank", "twin_tank", "attack_helicopter", "main_battle_tank", "railgun_truck", "ifv", "aa_vehicle", "heavy_rocket_artillery" }, Minutes = 12f },
            new() { Name = "Short", Deck = ModeBalanceMeasure.SampleDeck, Minutes = 3f },
        };

        private static int[] Seeds => Env("MB_CMD_SEEDS") is { } s ? s.Split(',').Select(int.Parse).ToArray() : new[] { 1, 2, 3 };

        private static string Env(string name) => Environment.GetEnvironmentVariable(name) is { Length: > 0 } v ? v : null;

        internal readonly struct Battle
        {
            public Battle(float score, bool won, float minutes, double msPerStep, int peakUnits)
            {
                Score = score;
                Won = won;
                Minutes = minutes;
                MsPerStep = msPerStep;
                PeakUnits = peakUnits;
            }

            public float Score { get; }
            public bool Won { get; }
            public float Minutes { get; }
            public double MsPerStep { get; }
            public int PeakUnits { get; }
        }

        /// <summary>One battle: the style's deck under the commander (null: none) against the mode's enemy for the seed.</summary>
        internal static Battle Play(Style style, CommanderDef commander, int seed, float? minutes = null)
        {
            MatchSettings.Mode = style.Mode;
            MatchSettings.Difficulty = AiDifficulty.Normal;
            MatchSettings.DeckVehicles.Clear();
            MatchSettings.DeckVehicles.AddRange(style.Deck);
            MatchSettings.DeckSupports.Clear();
            MatchSettings.DeckSupports.AddRange(style.Supports ?? Supports);
            var catalog = GameContent.LoadCatalog();
            var world = new SimWorld(catalog, GameContent.LoadMap(ModeSession.MapFile(style.Mode, "ashfield")), seed: seed);
            world.SetStatCaps(GearCatalog.StatCap, GearCatalog.TowerStatCap);
            world.SetCommander(0, commander);
            var session = ModeSession.Create(style.Mode, false, world, seed);
            var mode = session.Mode;
            var limit = (minutes ?? style.Minutes) * 60f;
            var watch = Stopwatch.StartNew();
            var steps = 0;
            var peak = 0;
            float t;
            for (t = 0f; t < limit; t += 0.05f)
            {
                mode.Tick(world, 0.05f);
                session.TickAi(world, 0.05f);
                world.Step(0.05f);
                world.ClearEvents();
                steps++;
                if (steps % 40 == 0) peak = Math.Max(peak, world.CountAlive(0) + world.CountAlive(1));
                if (mode.Result != null) break;
            }
            watch.Stop();
            float score;
            switch (mode)
            {
                case ConquestMode c:
                    score = (c.Tickets(0) - c.Tickets(1)) / (float)Math.Max(1, c.MaxTickets);
                    break;
                case DeathmatchMode d:
                    score = (d.Score(0) - d.Score(1)) / (float)Math.Max(1, d.ScoreTarget);
                    break;
                case SiegeMode s when s.Rules.PlayerDefends:
                    // How much of the base the attackers took: none +1, all of it -1.
                    score = 1f - 2f * s.Progress(world);
                    break;
                default:
                    score = 0f;
                    break;
            }
            if (mode.Result is { } r) score = r.WinningTeam == 0 ? Math.Max(score, 0.5f) : r.WinningTeam == 1 ? Math.Min(score, -0.5f) : score;
            return new Battle(Math.Clamp(score, -1f, 1f), score > 0f, t / 60f, watch.Elapsed.TotalMilliseconds / Math.Max(1, steps), peak);
        }

        [Test, Explicit("a measurement: run it by name with MB_BALANCE=1"), Category("Balance"), Timeout(14400000)]
        public void EveryCommanderAgainstEveryDeckStyle()
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("commander balance: set MB_BALANCE=1");
            var savedDeck = MatchSettings.DeckVehicles.ToList();
            var savedSupports = MatchSettings.DeckSupports.ToList();
            var savedMode = MatchSettings.Mode;
            var styles = Env("MB_CMD_STYLES") is { } sn ? Styles.Where(s => sn.Split(',').Contains(s.Name)).ToArray() : Styles.Where(s => s.Name != "Short").ToArray();
            var commanders = Env("MB_CMD_ONLY") is { } only ? Commanders.All.Where(c => only.Split(',').Contains(c.Id)).ToList() : Commanders.All.ToList();
            if (Env("MB_CMD_MINUTES") is { } m)
                foreach (var s in styles) s.Minutes = float.Parse(m, System.Globalization.CultureInfo.InvariantCulture);
            var report = new StringBuilder();
            var started = DateTime.Now;
            var mean = new Dictionary<(string style, string cmd), float>();
            var wins = new Dictionary<(string style, string cmd), int>();
            var minutesOf = new Dictionary<string, float>();
            var stepMs = new Dictionary<string, double>();
            try
            {
                foreach (var style in styles)
                {
                    foreach (var c in commanders)
                    {
                        var runs = Seeds.Select(seed => Play(style, c, seed)).ToList();
                        mean[(style.Name, c.Id)] = runs.Average(b => b.Score);
                        minutesOf[style.Name] = minutesOf.TryGetValue(style.Name, out var had) ? had + runs.Sum(b => b.Minutes) : runs.Sum(b => b.Minutes);
                        stepMs[style.Name] = stepMs.TryGetValue(style.Name, out var ms) ? ms + runs.Sum(b => b.MsPerStep) : runs.Sum(b => b.MsPerStep);
                        wins[(style.Name, c.Id)] = runs.Count(b => b.Won);
                        if (c.Id == "varro" && style.Name == "Swarm")
                            report.AppendLine($"Tide on Swarm: {runs.Average(b => b.MsPerStep):0.00} ms a step, peak {runs.Max(b => b.PeakUnits)} units");
                        if (c.Id == "kade" && style.Name == "Swarm")
                            report.AppendLine($"Iron on Swarm: {runs.Average(b => b.MsPerStep):0.00} ms a step, peak {runs.Max(b => b.PeakUnits)} units");
                    }
                    Debug.Log($"[CommanderMeasure] {style.Name} done ({(DateTime.Now - started).TotalMinutes:0.0} min)");
                }
                // Vault in a short and a long battle, against Iron.
                if (Env("MB_CMD_STYLES") == null || Env("MB_CMD_VAULT") != null)
                {
                    var shortStyle = Styles.First(s => s.Name == "Short");
                    var longStyle = Styles.First(s => s.Name == "Hoard");
                    foreach (var id in new[] { "okoye", "kade" })
                    {
                        var sh = Seeds.Select(seed => Play(shortStyle, Commanders.Get(id), seed)).Average(b => b.Score);
                        var lo = Seeds.Select(seed => Play(longStyle, Commanders.Get(id), seed)).Average(b => b.Score);
                        report.AppendLine($"{id} short (3 min) {sh:+0.00;-0.00} · long (12 min) {lo:+0.00;-0.00}");
                    }
                }
            }
            finally
            {
                MatchSettings.DeckVehicles.Clear();
                MatchSettings.DeckVehicles.AddRange(savedDeck);
                MatchSettings.DeckSupports.Clear();
                MatchSettings.DeckSupports.AddRange(savedSupports);
                MatchSettings.Mode = savedMode;
            }

            // The table: mean score by commander (rows) and style (columns), the best of each style marked.
            report.AppendLine();
            report.Append("| commander |");
            foreach (var s in styles) report.Append(' ').Append(s.Name).Append(" |");
            report.AppendLine();
            report.Append("|---|");
            foreach (var _ in styles) report.Append("---|");
            report.AppendLine();
            var bestOf = new Dictionary<string, List<string>>();
            foreach (var s in styles)
            {
                var top = commanders.Max(c => mean[(s.Name, c.Id)]);
                bestOf[s.Name] = commanders.Where(c => mean[(s.Name, c.Id)] >= top - Tie).Select(c => c.Id).ToList();
            }
            foreach (var c in commanders)
            {
                report.Append("| ").Append(c.Id).Append(" |");
                foreach (var s in styles)
                    report.Append(' ').Append(mean[(s.Name, c.Id)].ToString("+0.00;-0.00")).Append(bestOf[s.Name].Contains(c.Id) ? "*" : "")
                        .Append(" (").Append(wins[(s.Name, c.Id)]).Append(") |");
                report.AppendLine();
            }
            report.AppendLine();
            var never = commanders.Where(c => !styles.Any(s => bestOf[s.Name].Contains(c.Id))).Select(c => c.Id).ToList();
            var always = commanders.Where(c => styles.All(s => bestOf[s.Name].Contains(c.Id))).Select(c => c.Id).ToList();
            var n = commanders.Count * Seeds.Length;
            foreach (var s in styles) report.AppendLine($"{s.Name}: {s.Mode}, battles last {minutesOf[s.Name] / n:0.0} min on average, {stepMs[s.Name] / n:0.00} ms a step");
            report.AppendLine($"best of no style: {(never.Count == 0 ? "none" : string.Join(", ", never))}");
            report.AppendLine($"best of every style: {(always.Count == 0 ? "none" : string.Join(", ", always))}");
            report.AppendLine($"({(DateTime.Now - started).TotalMinutes:0.0} min, seeds {string.Join(",", Seeds)})");
            TestContext.Out.WriteLine(report.ToString());
            Debug.Log("[CommanderMeasure]\n" + report);
            var dir = Env("MB_CV_OUT") ?? System.IO.Path.GetTempPath();
            System.IO.File.WriteAllText(System.IO.Path.Combine(dir, "commanders_" + (Env("MB_CV_TAG") ?? "now") + ".md"), report.ToString());
            Assert.Pass();
        }
    }
}
