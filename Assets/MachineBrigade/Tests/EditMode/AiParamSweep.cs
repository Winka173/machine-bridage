using System;
using System.Collections.Generic;
using System.IO;
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
    /// Prompt 28 L.3: sweeps AI parameters across their min-max range through AI-versus-AI Conquest matches and writes a
    /// table per parameter with its own metric next to the common ones. Environment: MB_SWEEP_KEYS (comma list of keys,
    /// prefix match, default "params."), MB_SWEEP_POINTS (values per range, default 3: min, start, max; more spreads
    /// them evenly), MB_SWEEP_SEEDS (default 3), MB_SWEEP_MAPS (default ashfield), MB_SWEEP_MINUTES (default 12),
    /// MB_SWEEP_OUT (default Docs/ai/sweep.csv).
    /// </summary>
    public class AiParamSweep
    {
        private static string Env(string key, string fallback) => Environment.GetEnvironmentVariable(key) is { Length: > 0 } v ? v : fallback;

        [Test, Explicit("a measurement: run it by name with MB_BALANCE=1"), Category("Balance"), Timeout(int.MaxValue)]
        public void SweepAiParameters()
        {
            var baseline = GameContent.LoadCatalog().Ai;
            var prefixes = Env("MB_SWEEP_KEYS", "params.").Split(',');
            var keys = baseline.Keys.Where(k => prefixes.Any(p => k.StartsWith(p.Trim(), StringComparison.Ordinal))).ToList();
            var points = Math.Max(2, int.Parse(Env("MB_SWEEP_POINTS", "3")));
            var seeds = int.Parse(Env("MB_SWEEP_SEEDS", "3"));
            var maps = Env("MB_SWEEP_MAPS", "ashfield").Split(',');
            var minutes = float.Parse(Env("MB_SWEEP_MINUTES", "12"), System.Globalization.CultureInfo.InvariantCulture);
            var output = Env("MB_SWEEP_OUT", Path.Combine(Application.dataPath, "..", "Docs", "ai", "sweep.csv"));

            var csv = new StringBuilder("key,value,metric,runs,minutes,fightShare,destroyedPerMin,captures,aliveA,aliveB,winsA,winsB\n");
            foreach (var key in keys)
            {
                var p = baseline.Param(key);
                var values = new SortedSet<float>();
                if (points == 3) values.UnionWith(new[] { p.Min, p.Value, p.Max });
                else for (var i = 0; i < points; i++) values.Add(p.Min + (p.Max - p.Min) * i / (points - 1));
                foreach (var value in values)
                {
                    var sum = new Result();
                    var runs = 0;
                    foreach (var map in maps)
                    for (var s = 0; s < seeds; s++, runs++)
                        sum.Add(Play(map.Trim(), 100 + s, minutes, key, value));
                    csv.Append($"{key},{value:0.###},\"{p.Metric.Replace("\"", "'")}\",{runs},{sum.Minutes / runs:0.0},{sum.FightShare / runs:0.000}," +
                               $"{sum.DestroyedPerMin / runs:0.00},{sum.Captures / (float)runs:0.0},{sum.AliveA / runs:0.0},{sum.AliveB / runs:0.0},{sum.WinsA},{sum.WinsB}\n");
                    Debug.Log($"AI sweep {key}={value}: {csv.ToString().Split('\n').Reverse().Skip(1).First()}");
                }
            }
            Directory.CreateDirectory(Path.GetDirectoryName(output)!);
            File.WriteAllText(output, csv.ToString());
            Debug.Log($"AI sweep written to {output}");
        }

        private sealed class Result
        {
            public float Minutes, FightShare, DestroyedPerMin, AliveA, AliveB;
            public int Captures, WinsA, WinsB;

            public void Add(Result r)
            {
                Minutes += r.Minutes;
                FightShare += r.FightShare;
                DestroyedPerMin += r.DestroyedPerMin;
                AliveA += r.AliveA;
                AliveB += r.AliveB;
                Captures += r.Captures;
                WinsA += r.WinsA;
                WinsB += r.WinsB;
            }
        }

        private static Result Play(string map, int seed, float minutes, string key, float value)
        {
            var catalog = GameContent.LoadCatalog();
            catalog.Ai = catalog.Ai.With(key, value);
            var world = new SimWorld(catalog, GameContent.LoadMap(map + "_conquest"), seed: seed);
            var mode = new ConquestMode(new ConquestRules
            {
                PlayerVehicles = MatchSettings.AllVehicles,
                PlayerSupports = MatchSettings.AllSupports,
                EnemyVehicles = MatchSettings.AllVehicles,
                EnemySupports = MatchSettings.AllSupports,
            });
            mode.Setup(world);
            world.Intel.Objectives = mode;
            var a = new ConquestAi(mode, 0, 1, AiDifficulty.Normal, seed + 1);
            var b = new ConquestAi(mode, 1, 0, AiDifficulty.Normal, seed + 2);

            const float step = 0.05f;
            var r = new Result();
            int samples = 0, fighting = 0, destroyed = 0;
            var seconds = 0f;
            for (; seconds < minutes * 60f && mode.Result == null; seconds += step)
            {
                mode.Tick(world, step);
                a.Tick(world, step);
                b.Tick(world, step);
                world.Step(step);
                foreach (var e in world.Events)
                {
                    if (e.Kind == SimEventKind.PointCaptured && e.Team >= 0) r.Captures++;
                    else if (e.Kind == SimEventKind.VehicleDestroyed) destroyed++;
                }
                world.ClearEvents();
                if (world.Tick % 20 != 0) continue;
                samples++;
                // Fighting: either side's World Model sees a contested cell.
                if (world.Intel.For(0).Contested.Count > 0 || world.Intel.For(1).Contested.Count > 0) fighting++;
                r.AliveA += world.Vehicles.Count(v => v.IsAlive && v.Team == 0);
                r.AliveB += world.Vehicles.Count(v => v.IsAlive && v.Team == 1);
            }
            r.Minutes = seconds / 60f;
            r.FightShare = samples > 0 ? fighting / (float)samples : 0f;
            r.DestroyedPerMin = destroyed / Math.Max(0.1f, r.Minutes);
            r.AliveA /= Math.Max(1, samples);
            r.AliveB /= Math.Max(1, samples);
            if (mode.Result is { } result)
            {
                if (result.WinningTeam == 0) r.WinsA = 1;
                else if (result.WinningTeam == 1) r.WinsB = 1;
            }
            return r;
        }
    }
}
