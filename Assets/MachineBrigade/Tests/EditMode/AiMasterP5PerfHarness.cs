using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using Debug = UnityEngine.Debug;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// AI MASTER P5 Part P / section 114 / Part S: the 48v48 performance harness for the lead. A Conquest battle on Ashfield, both
    /// sides' layered AI, each side topped up to 48 ground units every 5 s; after a 10 s warm-up the AI timing counters run for
    /// <c>MB_P5_SECONDS</c> seconds (default 120). The report gives per-system milliseconds per step (steering, paths, tactical,
    /// squad, commander, procurement, targeting, watchdog, bosses, health monitor), the whole step's mean / p99, the
    /// SEVERE_UNSTUCK count and rate per 10 unit-minutes (Part S target: at most 1), NavalReverseEvents (must be 0) and the
    /// health monitor's Part K counters. Explicit: run it on purpose (Test Runner, category AIMasterP5Perf); it writes
    /// Temp/ai_p5_perf_48v48.txt and logs the same text.
    /// </summary>
    [Category("AIMasterP5Perf")]
    public class AiMasterP5PerfHarness
    {
        private const float Step = 0.05f;

        private static readonly string[] Army =
        {
            "main_battle_tank", "main_battle_tank", "ifv", "ifv", "heavy_tank", "tank_destroyer", "aa_vehicle", "mlrs", "artillery",
            "scout_jeep", "armored_car", "armored_car", "light_tank", "mortar_carrier",
        };

        [Test, Explicit("performance harness: the lead runs it"), Timeout(3600000)]
        public void Perf48v48_ReportsPerSystemMsSevereUnstuckAndNavalReverse()
        {
            var seconds = float.TryParse(Environment.GetEnvironmentVariable("MB_P5_SECONDS"), out var s) && s > 0f ? s : 120f;
            var report = Measure(48, 7, seconds);
            Debug.Log(report.text);
            TestContext.WriteLine(report.text);
            try
            {
                Directory.CreateDirectory("Temp");
                File.WriteAllText(Path.Combine("Temp", "ai_p5_perf_48v48.txt"), report.text);
            }
            catch (IOException)
            {
                // The report is in the log anyway.
            }
            Assert.AreEqual(0, report.navalReverse, "Part S: naval boss reverse events = 0");
            if (report.severePer10UnitMinutes > 1.0)
                Assert.Warn($"Part S target missed: {report.severePer10UnitMinutes:0.00} severe unstucks per 10 unit-minutes (target <= 1)");
        }

        internal static (string text, int severe, double severePer10UnitMinutes, int navalReverse) Measure(int perSide, int seed, float seconds)
        {
            SimTunables.Reset();
            GameContent.LoadTunables();
            var (world, mode, a, b) = AiMasterP5Tests.Conquest(seed, perSide, Army);
            var warmup = (int)(10f / Step);
            var total = warmup + (int)(seconds / Step);
            var watch = new Stopwatch();
            var steps = new double[total - warmup];
            var unitSeconds = 0.0;
            var severeAtStart = 0;
            for (var i = 0; i < total && mode.Result == null; i++)
            {
                if (i % 100 == 0)
                {
                    AiMasterP5Tests.Fill(world, 0, perSide, Army);
                    AiMasterP5Tests.Fill(world, 1, perSide, Army);
                }
                if (i == warmup)
                {
                    world.AiPerf.Reset();
                    world.AiPerf.Enabled = true;
                    severeAtStart = world.Traffic.Stats.SevereUnstuck;
                }
                watch.Restart();
                mode.Tick(world, Step);
                a.Tick(world, Step);
                b.Tick(world, Step);
                world.Step(Step);
                watch.Stop();
                world.ClearEvents();
                if (i < warmup) continue;
                steps[i - warmup] = watch.Elapsed.TotalMilliseconds;
                unitSeconds += world.VehicleList.Count(v => v.IsAlive && !v.Def.Static) * Step;
            }
            var measured = steps.Where(x => x > 0).OrderBy(x => x).ToArray();
            var severe = world.Traffic.Stats.SevereUnstuck - severeAtStart;
            var per10 = unitSeconds > 0 ? severe / (unitSeconds / 600.0) : 0.0;
            var naval = world.Bosses.Brains.NavalReverseEvents;
            var h = world.Health.Counters;
            var sb = new StringBuilder();
            sb.Append($"AI MASTER P5 48v48 harness: {perSide} v {perSide} ground units, seed {seed}, {seconds:0} s measured after 10 s warm-up\n");
            if (measured.Length > 0)
                sb.Append($"whole step (AI ticks + world step): mean {measured.Average():0.000} ms, p99 {measured[(int)(measured.Length * 0.99)]:0.000} ms, max {measured[^1]:0.000} ms\n");
            sb.Append(world.AiPerf.Report());
            sb.Append($"SevereUnstuckCount {severe} ({per10:0.00} per 10 unit-minutes; Part S target <= 1)\n");
            sb.Append($"NavalReverseEvents {naval} (Part S: 0)\n");
            sb.Append($"Part K: idleWithoutReason {h.ArmedIdleWithoutReason}, squadsNoDamage {h.SquadsNoDamage}, blocked {h.BlockedUnits} ({h.BlockedRatio:0.00}), " +
                      $"severe {h.SevereUnstuckEvents}, orders/unit/min {h.OrdersPerUnitPerMinute:0.0}, targetSwitches/min {h.TargetSwitchesPerMinute:0.0}, " +
                      $"actionSwitches/min {h.SquadActionSwitchesPerMinute:0.0}, noMapInfluence {h.NoMapInfluencePurchases}, lowUtilClasses {h.LowUtilizationUnitClasses}, " +
                      $"stalledObjectives {h.StalledObjectiveAssignments}, anomalies {h.CombatAnomalies}, deadlocks {h.DeadlockCycles}, navalReverse {h.NavalReverseAttempts}\n");
            sb.Append($"Part K recoveries: squads {h.SquadReevaluations}, idle audits {h.IdleAudits}, traffic {h.TrafficEscalations}, churn {h.ChurnDamps}; " +
                      $"Part L holds {h.ReloadHolds} / resumes {h.ReloadResumes} / kept targets {h.TargetsKeptReloading} / reload scoots {h.ScootsDuringReload}; " +
                      $"Part N overkill avoided {h.TowerOverkillAvoided}, critical overrides {h.TowerCriticalOverrides}\n");
            var byNs = ReasonCodes.CountByNamespace(world.AiLog);
            sb.Append("DecisionLog lines by namespace (last 4000): " + string.Join(", ", byNs.Select(kv => $"{kv.Key} {kv.Value}")) + "\n");
            var unregistered = ReasonCodes.Unregistered(world.AiLog);
            sb.Append($"Unregistered codes: {(unregistered.Count == 0 ? "none" : string.Join(", ", unregistered))}\n");
            return (sb.ToString(), severe, per10, naval);
        }
    }
}
