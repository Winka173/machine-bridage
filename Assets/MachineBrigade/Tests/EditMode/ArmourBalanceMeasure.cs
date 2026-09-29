using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Sandbox;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The armour and damage balance pass (DECISIONS 20X): time to kill in representative matchups on the Sandbox's
    /// flat range, how often hits land at each penetration step, and the share of damage armour takes off. Each
    /// matchup is a shooter group (side 0) against a target group (side 1) that holds its fire, so the time is the
    /// shooters' alone: from the first hit on the targets to the last target's end (called after the limit and
    /// then estimated from the damage rate, marked "~"). Direct-fire shooters stand where they are put, in reach,
    /// so the face they strike is the one set (front, side, rear); artillery and aircraft use the fighting AI.
    /// A mixed battle (both sides fighting, the same army each) gives the hit spread of a whole fight and its
    /// length. Run with MB_BALANCE=1 (MB_CV_OUT for the folder, MB_CV_TAG for the name, MB_CV_BALANCE for another
    /// balance file, MB_CV_SEEDS for the seeds; 3 by default).
    /// </summary>
    public class ArmourBalanceMeasure
    {
        internal sealed class Matchup
        {
            public string Name;
            public string[] Shooters, Targets;
            public float Distance;
            public DuelFacing Facing = DuelFacing.Front;
            public SandboxAi ShooterAi = SandboxAi.Idle, TargetAi = SandboxAi.Idle;
            public float Limit = 120f;
        }

        private static string[] N(string id, int n) => Enumerable.Repeat(id, n).ToArray();

        internal static readonly Matchup[] Matchups =
        {
            new() { Name = "light: 2 armoured cars vs 2 armoured cars", Shooters = N("armored_car", 2), Targets = N("armored_car", 2), Distance = 18f },
            new() { Name = "light: IFV vs 2 armoured cars", Shooters = N("ifv", 1), Targets = N("armored_car", 2), Distance = 18f },
            new() { Name = "light: 2 IFVs vs 2 IFVs", Shooters = N("ifv", 2), Targets = N("ifv", 2), Distance = 18f },
            new() { Name = "light: 2 jeeps vs 2 armoured cars", Shooters = N("scout_jeep", 2), Targets = N("armored_car", 2), Distance = 16f },
            new() { Name = "tank: MBT vs MBT, front", Shooters = N("main_battle_tank", 1), Targets = N("main_battle_tank", 1), Distance = 24f },
            new() { Name = "tank: MBT vs MBT, flank", Shooters = N("main_battle_tank", 1), Targets = N("main_battle_tank", 1), Distance = 24f, Facing = DuelFacing.Side },
            new() { Name = "tank: MBT vs heavy tank, front", Shooters = N("main_battle_tank", 1), Targets = N("heavy_tank", 1), Distance = 24f },
            new() { Name = "tank: MBT vs heavy tank, flank", Shooters = N("main_battle_tank", 1), Targets = N("heavy_tank", 1), Distance = 24f, Facing = DuelFacing.Side },
            new() { Name = "tank: light tank vs IFV, front", Shooters = N("light_tank", 1), Targets = N("ifv", 1), Distance = 22f },
            new() { Name = "tank: light tank vs MBT, flank", Shooters = N("light_tank", 1), Targets = N("main_battle_tank", 1), Distance = 22f, Facing = DuelFacing.Side },
            new() { Name = "tank: IFV vs MBT, front", Shooters = N("ifv", 1), Targets = N("main_battle_tank", 1), Distance = 22f },
            new() { Name = "tank: IFV vs MBT, flank", Shooters = N("ifv", 1), Targets = N("main_battle_tank", 1), Distance = 22f, Facing = DuelFacing.Side },
            new() { Name = "AT: tank destroyer vs MBT, front", Shooters = N("tank_destroyer", 1), Targets = N("main_battle_tank", 1), Distance = 30f },
            new() { Name = "AT: FPV carrier vs MBT", Shooters = N("fpv_carrier", 1), Targets = N("main_battle_tank", 1), Distance = 50f },
            new() { Name = "AT: Lancet truck vs heavy tank", Shooters = N("lancet_truck", 1), Targets = N("heavy_tank", 1), Distance = 60f },
            new() { Name = "AT: armoured car vs MBT, front (wrong tool)", Shooters = N("armored_car", 2), Targets = N("main_battle_tank", 1), Distance = 20f },
            new() { Name = "AA: AA vehicle vs attack helicopter", Shooters = N("aa_vehicle", 1), Targets = N("attack_helicopter", 1), Distance = 30f },
            new() { Name = "AA: SAM launcher vs attack jet", Shooters = N("sam_launcher", 1), Targets = N("attack_jet", 1), Distance = 60f, TargetAi = SandboxAi.Combat },
            new() { Name = "AA: heavy AA vs attack jet", Shooters = N("heavy_aa", 1), Targets = N("attack_jet", 1), Distance = 60f, TargetAi = SandboxAi.Combat },
            new() { Name = "arty: 2 SP howitzers vs 4 armoured cars", Shooters = N("artillery", 2), Targets = N("armored_car", 4), Distance = 60f },
            new() { Name = "arty: 2 MLRS vs 2 MBTs", Shooters = N("mlrs", 2), Targets = N("main_battle_tank", 2), Distance = 70f },
            new() { Name = "arty: 2 SP howitzers vs 2 MBTs", Shooters = N("artillery", 2), Targets = N("main_battle_tank", 2), Distance = 60f },
            new() { Name = "tower: gun turret vs 2 MBTs", Shooters = N("gun_turret", 1), Targets = N("main_battle_tank", 2), Distance = 24f },
            new() { Name = "tower: MG bunker vs 3 armoured cars", Shooters = N("mg_bunker", 1), Targets = N("armored_car", 3), Distance = 22f },
            new() { Name = "tower: ATGM tower vs MBT", Shooters = N("atgm_tower", 1), Targets = N("main_battle_tank", 1), Distance = 30f },
            new() { Name = "tower: AA turret vs attack helicopter", Shooters = N("aa_turret", 1), Targets = N("attack_helicopter", 1), Distance = 30f },
            new() { Name = "vs tower: 2 MBTs vs gun turret", Shooters = N("main_battle_tank", 2), Targets = N("gun_turret", 1), Distance = 24f },
            new() { Name = "vs tower: 3 armoured cars vs MG bunker", Shooters = N("armored_car", 3), Targets = N("mg_bunker", 1), Distance = 22f },
        };

        /// <summary>The mixed battle: the same army each side, both fighting.</summary>
        internal static readonly string[] Army =
        {
            "main_battle_tank", "main_battle_tank", "ifv", "ifv", "armored_car", "armored_car", "tank_destroyer", "aa_vehicle", "artillery",
            "attack_helicopter",
        };

        private static int[] Seeds
        {
            get
            {
                var list = Environment.GetEnvironmentVariable("MB_CV_SEEDS");
                return string.IsNullOrEmpty(list) ? new[] { 1, 2, 3 } : list.Split(',').Select(int.Parse).ToArray();
            }
        }

        internal sealed class Tally
        {
            public int Hits;
            /// <summary>Hits by penetration step (<see cref="DamageTable.PenetrationStep"/>: two above, one above, level, one, two, three under), then part levels.</summary>
            public readonly int[] ByStep = new int[DamageTable.PenetrationSteps + 1];
            public readonly int[] ByFace = new int[4];
            public double Dealt, Raw;

            public void Add(HitReport h, float[] table)
            {
                Hits++;
                // The step whose multiplier it is (the thinnest armour first: a five-value row's two above is its one above).
                var best = table.Length;
                for (var i = table.Length - 1; i >= 0; i--)
                    if (MathF.Abs(h.Pen - table[i]) < 0.005f) best = i;
                ByStep[best]++;
                ByFace[(int)h.Face]++;
                if (h.Dealt > 0f && h.Pen > 0f)
                {
                    Dealt += h.Dealt;
                    Raw += h.Dealt / h.Pen;
                }
            }

            public void Add(Tally t)
            {
                Hits += t.Hits;
                for (var i = 0; i < ByStep.Length; i++) ByStep[i] += t.ByStep[i];
                for (var i = 0; i < ByFace.Length; i++) ByFace[i] += t.ByFace[i];
                Dealt += t.Dealt;
                Raw += t.Raw;
            }

            public float Lost => Raw > 0 ? (float)(1 - Dealt / Raw) : 0f;
            public float Share(int step) => Hits > 0 ? ByStep[step] / (float)Hits : 0f;
            public float FaceShare(int face) => Hits > 0 ? ByFace[face] / (float)Hits : 0f;
        }

        private sealed class RunResult
        {
            public double Ttk;

            /// <summary>The mixed battle: when a side first had half its starting health left (-1: never).</summary>
            public double Half = -1;
            public bool Killed;
            public double Seconds;
            public int Winner;
            public readonly Tally Tally = new();
        }

        private static float[] TableSteps(Catalog catalog)
        {
            var t = new float[DamageTable.PenetrationSteps];
            for (var i = 0; i < t.Length; i++) t[i] = catalog.Damage.PenetrationStep(i);
            return t;
        }

        private static RunResult Run(Catalog catalog, SandboxScenario s, float seconds, bool holdTargets, bool bothSides)
        {
            var world = new SimWorld(catalog, SandboxMaps.Flat(), s.Seed);
            var battle = new SandboxBattle(s, null);
            battle.Setup(world);
            var result = new RunResult();
            var steps = TableSteps(catalog);
            var targetHp = 0f;
            var start = new float[2];
            foreach (var v in world.Vehicles)
            {
                if (v.Team is 0 or 1) start[v.Team] += v.MaxHp;
                if (v.Team != 1) continue;
                targetHp += v.MaxHp;
                if (holdTargets) world.HoldFire(v, true);
            }
            double firstHit = -1;
            var dealt = 0f;
            var inner = world.HitLog;
            world.HitLog = h =>
            {
                inner?.Invoke(h);
                if (!bothSides && h.VictimTeam != 1) return;
                if (h.VictimTeam == 1)
                {
                    if (firstHit < 0) firstHit = world.Time;
                    dealt += h.Dealt;
                }
                result.Tally.Add(h, steps);
            };
            var n = (int)MathF.Ceiling(seconds / SandboxLab.Step);
            for (var i = 0; i < n && battle.Result == null; i++)
            {
                battle.Tick(world, SandboxLab.Step);
                world.Step(SandboxLab.Step);
                world.ClearEvents();
                if (result.Half < 0 && bothSides && i % 20 == 0)
                    for (var team = 0; team < 2; team++)
                    {
                        var left = 0f;
                        foreach (var v in world.Vehicles)
                            if (v.Team == team && v.IsAlive) left += v.Hp;
                        if (left <= start[team] * 0.5f) result.Half = world.Time;
                    }
            }
            var end = battle.Result != null ? battle.EndedAt : world.Time;
            result.Seconds = end;
            result.Winner = battle.Result is { } won ? won.WinningTeam : -2;
            result.Killed = result.Winner == 0;
            if (firstHit < 0) result.Ttk = double.PositiveInfinity;
            else if (result.Killed) result.Ttk = end - firstHit;
            else result.Ttk = dealt > 0f ? (end - firstHit) * targetHp / dealt : double.PositiveInfinity;
            return result;
        }

        private static SandboxScenario Scenario(Catalog catalog, Matchup m, int seed)
        {
            var s = SandboxLab.DuelScenario(catalog, m.Shooters, m.Targets, m.Distance, m.Facing, seed, m.Limit);
            s.Sides[0].Ai = m.ShooterAi;
            s.Sides[1].Ai = m.TargetAi;
            // Artillery and drones need the fighting AI to pick their mark; aircraft targets fly under it.
            if (m.Shooters.Any(id => catalog.Vehicles.TryGetValue(id, out var d) && (d.Flying || d.Mounts.Any(x => x.Weapon.MinRange > 0f))))
                s.Sides[0].Ai = SandboxAi.Combat;
            return s;
        }

        [Test, Explicit("a measurement: run it by name with MB_BALANCE=1"), Category("Balance")]
        public void MeasureTimeToKill()
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("armour balance: set MB_BALANCE=1");
            var catalog = CombatValueMeasure.LoadCatalog();
            var inv = CultureInfo.InvariantCulture;
            var sb = new StringBuilder();
            sb.AppendLine("matchup\tttk_s\tkilled\thits\tover2\tover1\tlevel\tunder1\tunder2\tunder3\tpart\tlostToArmour\tfront\tside\trear\ttop");
            var all = new Tally();
            var started = DateTime.Now;
            foreach (var m in Matchups)
            {
                var runs = Seeds.Select(seed => Run(catalog, Scenario(catalog, m, seed), m.Limit + 1f, true, false)).ToList();
                var t = new Tally();
                foreach (var r in runs) t.Add(r.Tally);
                all.Add(t);
                var finite = runs.Where(r => !double.IsInfinity(r.Ttk)).Select(r => r.Ttk).ToList();
                var ttk = finite.Count > 0 ? finite.Average() : double.PositiveInfinity;
                var killed = runs.Count(r => r.Killed);
                var mark = killed < runs.Count ? "~" : "";
                sb.AppendLine(string.Join("\t", m.Name, double.IsInfinity(ttk) ? "none" : mark + ttk.ToString("0.0", inv), $"{killed}/{runs.Count}",
                    (t.Hits / runs.Count).ToString(inv), Shares(t), P(t.Lost),
                    P(t.FaceShare(0)), P(t.FaceShare(1)), P(t.FaceShare(2)), P(t.FaceShare(3))));
            }
            sb.AppendLine(string.Join("\t", "ALL MATCHUPS", "", "", all.Hits.ToString(inv), Shares(all), P(all.Lost), P(all.FaceShare(0)), P(all.FaceShare(1)), P(all.FaceShare(2)), P(all.FaceShare(3))));

            // The mixed battle: the whole fight's hits, its length and who won.
            var mixed = new Tally();
            var lengths = new List<string>();
            foreach (var seed in Seeds)
            {
                var s = SandboxLab.DuelScenario(catalog, Army, Army, 60f, DuelFacing.Front, seed, 240f);
                var r = Run(catalog, s, 241f, false, true);
                mixed.Add(r.Tally);
                lengths.Add($"{r.Seconds.ToString("0", inv)} s, half at {r.Half.ToString("0", inv)} s (winner {r.Winner})");
            }
            sb.AppendLine(string.Join("\t", "MIXED BATTLE " + string.Join(", ", lengths), "", "", (mixed.Hits / Seeds.Length).ToString(inv), Shares(mixed), P(mixed.Lost), P(mixed.FaceShare(0)),
                P(mixed.FaceShare(1)), P(mixed.FaceShare(2)), P(mixed.FaceShare(3))));

            var outDir = Environment.GetEnvironmentVariable("MB_CV_OUT");
            if (string.IsNullOrEmpty(outDir)) outDir = Path.GetTempPath();
            Directory.CreateDirectory(outDir);
            var tag = Environment.GetEnvironmentVariable("MB_CV_TAG") ?? "now";
            File.WriteAllText(Path.Combine(outDir, $"armour_ttk_{tag}.tsv"), sb.ToString(), new UTF8Encoding(false));
            UnityEngine.Debug.Log($"[ArmourBalanceMeasure] {(DateTime.Now - started).TotalSeconds:0} s\n" + sb);
            Assert.Pass();
        }

        private static string Shares(Tally t) => string.Join("\t", Enumerable.Range(0, DamageTable.PenetrationSteps + 1).Select(i => P(t.Share(i))));

        private static string P(float share) => (share * 100f).ToString("0", CultureInfo.InvariantCulture) + "%";
    }
}
