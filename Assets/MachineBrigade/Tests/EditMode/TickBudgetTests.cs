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
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;
using Debug = UnityEngine.Debug;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The simulation's tick budget with many enemies (prompt 5, item 8). A battle on Ashfield
    /// with both level-5 bases, the player's army of 28 and N enemy vehicles in cheap swarms,
    /// both commanders running, the fallen replaced every few seconds so the count holds. Each
    /// step (both AIs and the world step) is timed: the mean and the 99th percentile. The enemy
    /// ceiling is the largest N whose cost, scaled to a low-end phone, fits the budget.
    /// </summary>
    public class TickBudgetTests
    {
        /// <summary>
        /// A low-end phone (a Cortex-A55 / A73 class CPU, e.g. Helio G85 or Snapdragon 680) against
        /// this desktop (Ryzen 7 9700X) in the editor's Mono: about 7-8 times slower in single-thread
        /// scores, less the IL2CPP build's gain over Mono; taken as 6 times, on the careful side.
        /// </summary>
        public const double PhoneFactor = 6.0;

        /// <summary>The phone's budget for one 20 Hz step: 8 ms on average, 16 ms (half a 30 fps frame) at the 99th percentile.</summary>
        public const double PhoneMeanMs = 8.0, PhoneP99Ms = 16.0;

        private const float Step = 0.05f;

        private static readonly string[] Army =
        {
            "main_battle_tank", "main_battle_tank", "main_battle_tank", "ifv", "ifv", "heavy_tank", "tank_destroyer", "aa_vehicle",
            "mlrs", "artillery", "attack_helicopter", "scout_jeep", "armored_car", "armored_car",
        };

        private static readonly string[] Swarm = { "armored_car", "rocket_technical", "zu23_technical", "scout_jeep", "light_tank", "mortar_carrier", "vbied", "armored_car" };

        internal static (double mean, double p99, int alive) Measure(int enemies, int seed, float seconds = 60f) => Measure(enemies, seed, seconds, null);

        /// <param name="parts">When given: the p99 of the commanders' share and of the world step, and the worst step.</param>
        internal static (double mean, double p99, int alive) Measure(int enemies, int seed, float seconds, StringBuilder parts)
        {
            var catalog = GameContent.LoadCatalog();
            var world = new SimWorld(catalog, GameContent.LoadMap("ashfield_conquest"), seed: seed);
            var ours = world.Bases.Establish(0, BaseBalanceTests.Mixed(), BaseRole.Anchor);
            var theirs = world.Bases.Establish(1, BaseBalanceTests.Mixed(), BaseRole.Anchor);
            world.TryGetRally(0, out var home);
            world.TryGetRally(1, out var camp);
            var ai0 = new TacticalAi(0, 1, seed) { Objective = _ => theirs.HqPosition };
            var ai1 = new TacticalAi(1, 0, seed + 1) { Objective = _ => ours.HqPosition };
            var n = 0;
            void Fill(int team, IReadOnlyList<string> roster, int count, Vector2 at)
            {
                var alive = world.VehicleList.Count(v => v.IsAlive && v.Team == team && !v.Def.Static);
                for (var i = alive; i < count; i++, n++)
                {
                    var angle = n * 2.39996f;
                    world.SpawnVehicle(roster[n % roster.Count], team, world.ClampToMap(at + new Vector2(MathF.Cos(angle), MathF.Sin(angle)) * (4f + n % 7 * 2f)), 0f);
                }
            }
            var times = new List<double>();
            var aiTimes = new List<double>();
            var stepTimes = new List<double>();
            var watch = new Stopwatch();
            var split = new Stopwatch();
            var warmup = (int)(10f / Step);
            var total = warmup + (int)(seconds / Step);
            var aliveSum = 0L;
            var queued = 0;
            if (parts != null) world.Profile = new List<double[]>();
            for (var i = 0; i < total; i++)
            {
                if (i % 100 == 0)
                {
                    Fill(0, Army.Concat(Army).ToArray(), 28, home);
                    Fill(1, Swarm, enemies, camp);
                }
                watch.Restart();
                ai0.Tick(world, Step);
                ai1.Tick(world, Step);
                var ai = watch.Elapsed.TotalMilliseconds;
                world.Step(Step);
                watch.Stop();
                world.ClearEvents();
                if (i < warmup) continue;
                times.Add(watch.Elapsed.TotalMilliseconds);
                aiTimes.Add(ai);
                stepTimes.Add(watch.Elapsed.TotalMilliseconds - ai);
                aliveSum += world.VehicleList.Count(v => v.IsAlive);
                queued = Math.Max(queued, world.QueuedPaths);
            }
            times.Sort();
            if (parts != null)
            {
                // Each system's mean and p99 over the measured steps (the warm-up left out).
                var rows = world.Profile.Skip(warmup).ToList();
                parts.Append($"  {enemies} enemies, systems (mean/p99 ms):");
                for (var s = 0; s < SimWorld.ProfileSections.Length; s++)
                {
                    var column = rows.Select(r => r[s]).OrderBy(x => x).ToList();
                    parts.Append($" {SimWorld.ProfileSections[s]} {column.Average():0.00}/{column[(int)(column.Count * 0.99)]:0.00}");
                }
                parts.Append('\n');
                aiTimes.Sort();
                stepTimes.Sort();
                parts.Append($"  {enemies} enemies: commanders mean {aiTimes.Average():0.00} p99 {aiTimes[(int)(aiTimes.Count * 0.99)]:0.00} max {aiTimes[^1]:0.00}; " +
                             $"world step mean {stepTimes.Average():0.00} p99 {stepTimes[(int)(stepTimes.Count * 0.99)]:0.00} max {stepTimes[^1]:0.00}; " +
                             $"total p95 {times[(int)(times.Count * 0.95)]:0.00} p99 {times[(int)(times.Count * 0.99)]:0.00} max {times[^1]:0.00}; most routes waiting {queued}\n");
            }
            return (times.Average(), times[(int)(times.Count * 0.99)], (int)(aliveSum / Math.Max(1, times.Count)));
        }

        [Test, Category("Balance"), Timeout(7200000)]
        public void TheEnemyCeilingFitsTheTickBudget()
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("performance measurement: set MB_BALANCE=1 to run it");
            // Once to warm the JIT and the content caches.
            Measure(24, 1, 5f);
            var report = new StringBuilder($"TICK budget: phone = desktop x {PhoneFactor}, phone budget mean {PhoneMeanMs} ms, p99 {PhoneP99Ms} ms\n");
            report.Append("enemies  alive  mean ms  p99 ms  phone mean  phone p99  fits\n");
            var best = 0;
            var parts = new StringBuilder();
            foreach (var enemies in new[] { 24, 32, 40, 48, 56, 64, 80 })
            {
                var runs = new[] { Measure(enemies, 3, 60f, parts), Measure(enemies, 4, 60f, parts), Measure(enemies, 5, 60f, parts) };
                var mean = runs.Average(r => r.mean);
                var p99 = runs.Select(r => r.p99).OrderBy(x => x).ElementAt(1);
                var fits = mean * PhoneFactor <= PhoneMeanMs && p99 * PhoneFactor <= PhoneP99Ms;
                if (fits) best = enemies;
                report.Append($"{enemies,7}  {runs.Average(r => r.alive),5:0}  {mean,7:0.00}  {p99,6:0.00}  {mean * PhoneFactor,10:0.0}  {p99 * PhoneFactor,9:0.0}  {(fits ? "yes" : "no")}\n");
            }
            report.Append($"largest fitting: {best}\n").Append(parts);
            Debug.Log(report.ToString());
            Assert.GreaterOrEqual(best, 48, "the big battles' ceiling of 48 enemies fits the budget");
        }
    }
}
