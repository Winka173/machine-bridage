using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Modes;
using MachineBrigade.Sim.Navigation;
using UnityEngine;
using Debug = UnityEngine.Debug;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The stuck report's batch runs (prompt 12): whole battles in the base modes, both sides by
    /// their commanders, watched by <see cref="StuckWatch"/>. Run by name (they are Explicit):
    /// <c>StuckBatch.Siege</c> plays every battlefield's Siege, <c>StuckBatch.Modes</c> Defend,
    /// Endless and the weekly fortress on six battlefields, each on two seeds and a rotation of
    /// three base loadouts (few towers, every hardpoint filled, obstacles in the hardpoints).
    /// Environment: MB_STUCK_LABEL names the run (the output folder under Docs/stuck-report/data),
    /// MB_STUCK_RESCUE=0 turns the safety net off (to measure the causes alone), MB_STUCK_MAPS
    /// narrows the battlefields (comma-separated), MB_STUCK_SEEDS the seeds, MB_STUCK_MINUTES caps
    /// each battle. The full sweep for the testing phase: every mode on every battlefield, five
    /// seeds (MB_STUCK_SEEDS=1,2,3,4,5 MB_STUCK_MODES=Siege,Defend,Endless,Weekly).
    /// </summary>
    public class StuckBatch
    {
        private const float Step = 0.05f;

        /// <summary>Six battlefields for the other modes: a rail line and a runway, a city, a jungle, a desert, one of the new maps.</summary>
        private static readonly string[] ModeMaps = { "ashfield", "ironport", "metrocity", "redrock", "junglepass", "capital" };

        public static readonly string[] Configs = { "light", "full", "obstacles" };

        /// <summary>The player's decks, by seed: the heaviest hulls (bulldozer, siege gun, super-heavy tanks), and a mixed one.</summary>
        private static readonly string[][] Decks =
        {
            new[] { "main_battle_tank", "heavy_tank", "siege_tank", "armored_bulldozer", "titan_tank", "aa_vehicle", "artillery", "ifv" },
            new[] { "scout_jeep", "armored_car", "ifv", "light_tank", "main_battle_tank", "aa_vehicle", "mlrs", "siege_tank" },
        };

        [Test, Explicit("batch run for the stuck report"), Timeout(7200000)]
        public void Siege() => Run("Siege", MatchSettings.AllMaps.Select(m => m.Id).ToArray());

        [Test, Explicit("batch run for the stuck report"), Timeout(7200000)]
        public void Modes() => Run(Env("MB_STUCK_MODES", "Defend,Endless,Weekly"), ModeMaps);

        /// <summary>One case, MB_STUCK_CASE=mode:map:seed:config (a stuck record's replay; MB_STUCK_TRACE=vehicle id traces it).</summary>
        [Test, Explicit("batch run for the stuck report"), Timeout(7200000)]
        public void One()
        {
            var parts = Env("MB_STUCK_CASE", "Siege:ashfield:1:full").Split(':');
            var label = Env("MB_STUCK_LABEL", "one");
            var dir = Output(label);
            var csv = new StringBuilder(StuckWatch.CsvHeader + "\n");
            var trace = Env("MB_STUCK_TRACE", "").Split(',', StringSplitOptions.RemoveEmptyEntries).Select(int.Parse).ToArray();
            var line = Play((GameModeKind)Enum.Parse(typeof(GameModeKind), parts[0]), parts[1], int.Parse(parts[2]), parts[3], dir, csv, trace);
            File.WriteAllText(Path.Combine(dir, "stuck.csv"), csv.ToString());
            Debug.Log("STUCK ONE " + line);
        }

        private static string Env(string key, string fallback)
        {
            var v = Environment.GetEnvironmentVariable(key);
            return string.IsNullOrEmpty(v) ? fallback : v;
        }

        private static string Output(string label)
        {
            var root = Directory.GetParent(Application.dataPath)!.FullName;
            var dir = Path.Combine(root, "Docs", "stuck-report", "data", label);
            Directory.CreateDirectory(dir);
            return dir;
        }

        private static void Run(string modes, string[] maps)
        {
            var label = Env("MB_STUCK_LABEL", "run");
            var only = Env("MB_STUCK_MAPS", "");
            if (only.Length > 0) maps = only.Split(',');
            var seeds = Env("MB_STUCK_SEEDS", "1,2").Split(',').Select(int.Parse).ToArray();
            var dir = Output(label);
            var csv = new StringBuilder(StuckWatch.CsvHeader + "\n");
            var summary = new StringBuilder("mode,map,seed,config,minutes,result,stuck8,stuck10,worst_s,rescues,wall_s\n");
            var kinds = modes.Split(',').Select(m => (GameModeKind)Enum.Parse(typeof(GameModeKind), m)).ToArray();
            var name = string.Join("-", kinds.Select(k => k.ToString().ToLowerInvariant()));
            var total = 0;
            for (var mi = 0; mi < maps.Length; mi++)
            foreach (var kind in kinds)
            foreach (var seed in seeds)
            {
                // The loadouts go round the battlefields and seeds, so every map meets two of them.
                var config = Configs[(mi + seed + Array.IndexOf(kinds, kind)) % Configs.Length];
                summary.Append(Play(kind, maps[mi], seed, config, dir, csv, Array.Empty<int>())).Append('\n');
                total++;
                File.WriteAllText(Path.Combine(dir, $"stuck-{name}.csv"), csv.ToString());
                File.WriteAllText(Path.Combine(dir, $"summary-{name}.csv"), summary.ToString());
            }
            Debug.Log($"STUCK BATCH {label} {modes}: {total} battles\n{summary}");
        }

        /// <summary>The base loadout a configuration gives a side (null: the mode's own).</summary>
        internal static BaseLoadout Loadout(SimWorld world, string config, int team, int seed) => config switch
        {
            // Few towers: a bare HQ (the fortress's walls, gates and buildings stay).
            "light" => BaseLoadout.HqOnly(1),
            // Every hardpoint filled, any tower (the dragon's teeth and minefields among them).
            "full" => BaseLoadout.ForAi(world.Catalog, "Hard", "kessler", seed * 3 + team),
            // Obstacles in the hardpoints: dragon's teeth in the small ones, gun pits and big turrets.
            _ => new BaseLoadout
            {
                HqLevel = 5,
                Small = { "dragons_teeth", "dragons_teeth", "minefield", "dragons_teeth", "dragons_teeth", "aa_turret" },
                Medium = { "gun_pit", "c_ram", "gun_pit" },
                Large = { "heavy_turret", "drone_hangar" },
                Utilities = { "repair_bay", "ammo_depot", "radar_station" },
            },
        };

        private static string Play(GameModeKind kind, string map, int seed, string config, string dir, StringBuilder csv, int[] trace)
        {
            var clock = Stopwatch.StartNew();
            MatchSettings.Mode = kind;
            MatchSettings.Difficulty = AiDifficulty.Normal;
            MatchSettings.DeckVehicles.Clear();
            MatchSettings.DeckVehicles.AddRange(Decks[(seed - 1) % Decks.Length]);
            var file = kind == GameModeKind.Weekly ? map + "_siege" : ModeSession.MapFile(kind, map);
            var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(file), seed: seed);
            world.Movement.RescueEnabled = Env("MB_STUCK_RESCUE", "1") != "0";
            world.Bases.LoadoutFor = (team, _) => Loadout(world, config, team, seed);
            var session = ModeSession.Create(kind, false, world, seed);
            var watch = new StuckWatch(map, kind.ToString(), seed, config);
            var cap = float.Parse(Env("MB_STUCK_MINUTES", kind == GameModeKind.Siege ? "14" : "10"), CultureInfo.InvariantCulture) * 60f;
            var traced = new List<string>();
            // A replay's trace: every path and order change of the listed vehicles, and their state every half second, in the window.
            var window = Env("MB_STUCK_WINDOW", "0,99999").Split(',').Select(x => double.Parse(x, CultureInfo.InvariantCulture)).ToArray();
            if (trace.Length > 0)
                MachineBrigade.Sim.Entities.Vehicle.PathTrace = (v, what) =>
                {
                    if (Array.IndexOf(trace, v.Id.Value) >= 0 && world.Time >= window[0] && world.Time <= window[1])
                    {
                        var frames = new StackTrace(1, false).GetFrames() ?? Array.Empty<StackFrame>();
                        var stack = string.Join(" < ", frames.Take(4).Select(f => f.GetMethod()?.Name));
                        traced.Add($"t{world.Time:0.00} #{v.Id.Value} ({v.Position.X:0.0},{v.Position.Y:0.0}) {what} | {stack}");
                    }
                };
            try
            {
                for (var t = 0f; t < cap && session.Mode.Result == null; t += Step)
                {
                    session.Mode.Tick(world, Step);
                    session.TickAi(world, Step);
                    world.Step(Step);
                    world.ClearEvents();
                    watch.Observe(world);
                    if (trace.Length > 0 && world.Tick % 10 == 0 && world.Time >= window[0] && world.Time <= window[1])
                        foreach (var id in trace)
                            if (world.TryGetVehicle(new Sim.Core.EntityId(id), out var v) && v.IsAlive)
                                traced.Add(Snapshot(world, v));
                }
            }
            finally
            {
                MachineBrigade.Sim.Entities.Vehicle.PathTrace = null;
            }
            watch.Finish(world);
            var tag = $"{kind.ToString().ToLowerInvariant()}_{map}_s{seed}_{config}";
            File.WriteAllText(Path.Combine(dir, tag + ".json"), watch.ToJson(world, DataVersion(file)));
            if (trace.Length > 0) File.WriteAllText(Path.Combine(dir, tag + $"_trace{string.Join("-", trace)}.txt"), string.Join("\n", traced));
            foreach (var row in watch.CsvRows()) csv.Append(row).Append('\n');
            var result = session.Mode.Result is { } r ? r.WinningTeam == 0 ? "won" : r.WinningTeam == 1 ? "lost" : "draw" : "open";
            var worst = watch.Records.Count > 0 ? watch.Records.Max(x => x.Seconds) : 0.0;
            return string.Format(CultureInfo.InvariantCulture, "{0},{1},{2},{3},{4:0.0},{5},{6},{7},{8:0},{9},{10:0}",
                kind, map, seed, config, world.Time / 60.0, result, watch.CountOver(8), watch.CountOver(10), worst, watch.Rescues.Count,
                clock.Elapsed.TotalSeconds);
        }

        /// <summary>A traced vehicle's state: place, heading, speed, order, route, traffic waits.</summary>
        private static string Snapshot(SimWorld world, Sim.Entities.Vehicle v)
        {
            var t = v.Traffic;
            var next = v.HasPath ? v.Path[v.PathIndex] : v.Position;
            return string.Format(CultureInfo.InvariantCulture,
                "  t{0:0.0} #{1} {2} ({3:0.0},{4:0.0}) h{5:0} v{6:0.0} {7}->({8:0},{9:0}) path {10}/{11} next ({12:0.0},{13:0.0}) goal ({14:0},{15:0}) q{16} strikes {17} gate {18}/{19} yieldTo {20} waitYield {21} queue {22} hold {23:0.0} rev {24:0.0} lanes {25} target {26} engaged {27}",
                world.Time, v.Id.Value, v.Def.Id, v.Position.X, v.Position.Y, v.Heading * 57.3f, v.Speed, v.Order.Kind, v.Order.Point.X, v.Order.Point.Y,
                v.PathIndex, v.Path.Count, next.X, next.Y, v.PathGoal.X, v.PathGoal.Y, v.PathQueued ? 1 : 0, v.StuckStrikes,
                t.WaitingForGate ? 1 : 0, t.GateWaitId, t.YieldingTo.Value, t.WaitingOnYield ? 1 : 0, t.QueueBehind.Value,
                Math.Max(0, t.HoldUntil - world.Time), Math.Max(0, t.ReverseUntil - world.Time), world.Lanes.At(v.Position), v.Target.Value, v.Engaged.Value);
        }

        /// <summary>The data the battle was played with: the balance file's and the map's fingerprints.</summary>
        private static string DataVersion(string mapFile)
        {
            static string Hash(string resource)
            {
                var text = Resources.Load<TextAsset>(resource)?.text ?? "";
                unchecked
                {
                    var h = 2166136261u;
                    foreach (var ch in text)
                    {
                        h ^= ch;
                        h *= 16777619u;
                    }
                    return h.ToString("x8");
                }
            }
            return $"balance {Hash("Data/balance")} map {Hash("Data/maps/" + mapFile)} app {Application.version}";
        }
    }
}
