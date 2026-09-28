using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 13 A: the combat value of every buyable vehicle, measured in the simulation rather
    /// than on paper. Each vehicle (rank 1, no equipment), in a group of about 14 CP of its kind led
    /// by the tactical AI, attacks a reference group on an open field for 90 s from arrival: a
    /// cluster of light vehicles, a pair of tanks, a gun turret with a bunker, or a helicopter and an
    /// attack jet; aircraft fight each ground group with and without an anti-aircraft vehicle in it.
    /// Aircraft, helicopters and launchers with limited ammunition also fight a mixed group for 4
    /// minutes, so their empty-and-reload cycles are counted. A destroyed reference group is sent in
    /// again (another wave) until the time is up. Everything that keeps a vehicle from firing
    /// counts: the drive or flight in, turning, loops, hovering and dodging, reloads, minimum range,
    /// flares, active protection, lines of fire. Seeds are fixed; one seed per scenario (the owner's
    /// rule: short measurements; the testing phase sweeps more).
    ///
    /// Per vehicle and scenario it records the damage it really did (never more than its victim had
    /// left) against each armour, the share of its time on the field with a target in reach, its
    /// average survival, the time to destroy the first reference group, and the combat value per CP:
    /// damage x survival factor / CP, the survival factor being (1 + share of the time alive) / 2.
    /// Run with MB_BALANCE=1 (and MB_CV_OUT for the output folder; default the temp folder); a
    /// filter MB_CV_ONLY=a,b limits it to some vehicles.
    /// </summary>
    public class CombatValueMeasure
    {
        private const float Budget = 14f;

        /// <summary>
        /// The fixed seed of every scenario (the owner's rule: one run); MB_CV_SEEDS (a comma list) averages
        /// several for a decision that needs a second look.
        /// </summary>
        private static int[] Seeds
        {
            get
            {
                var list = Environment.GetEnvironmentVariable("MB_CV_SEEDS");
                return string.IsNullOrEmpty(list) ? new[] { 13 } : list.Split(',').Select(int.Parse).ToArray();
            }
        }

        /// <summary>One scenario's results over several seeds, averaged (the first kill over the seeds that made one).</summary>
        private static Result Mean(List<Result> runs)
        {
            if (runs.Count == 1) return runs[0];
            var kills = runs.Where(r => r.FirstKill >= 0f).ToList();
            return new Result
            {
                Id = runs[0].Id, Scenario = runs[0].Scenario, Count = runs[0].Count, Cp = runs[0].Cp, Seconds = runs[0].Seconds,
                Light = runs.Average(r => r.Light), Heavy = runs.Average(r => r.Heavy), Air = runs.Average(r => r.Air), Structure = runs.Average(r => r.Structure),
                OnTarget = runs.Average(r => r.OnTarget), Survival = runs.Average(r => r.Survival), Value = runs.Average(r => r.Value),
                FirstKill = kills.Count > 0 ? kills.Average(r => r.FirstKill) : -1f, Ready = runs.Average(r => r.Ready),
            };
        }
        private const float Standard = 90f;
        private const float Long = 240f;

        internal sealed class Scenario
        {
            public string Name;
            public string[] Group;
            public float Seconds = Standard;
        }

        internal static readonly Scenario[] Standards =
        {
            new() { Name = "light", Group = new[] { "armored_car", "armored_car", "armored_car", "scout_jeep" } },
            new() { Name = "tanks", Group = new[] { "main_battle_tank", "main_battle_tank" } },
            new() { Name = "fort", Group = new[] { "gun_turret", "mg_bunker" } },
            new() { Name = "air", Group = new[] { "attack_helicopter", "attack_jet" } },
            new() { Name = "light+AA", Group = new[] { "armored_car", "armored_car", "armored_car", "aa_vehicle" } },
            new() { Name = "tanks+AA", Group = new[] { "main_battle_tank", "main_battle_tank", "aa_vehicle" } },
            new() { Name = "fort+AA", Group = new[] { "gun_turret", "mg_bunker", "aa_turret" } },
        };

        /// <summary>The long run for aircraft and launchers: a mixed group with anti-air, 4 minutes.</summary>
        internal static readonly Scenario LongRun = new()
        {
            Name = "long", Group = new[] { "main_battle_tank", "main_battle_tank", "armored_car", "armored_car", "aa_vehicle" }, Seconds = Long,
        };

        internal sealed class Result
        {
            public string Id, Scenario;
            public int Count, Cp;
            public float Light, Heavy, Air, Structure, OnTarget, Survival, FirstKill = -1f, Value, Seconds;

            /// <summary>Aircraft: the share of their time attacking or ready to (in reach or on the way in with ammunition), and the flight to the holding pattern.</summary>
            public float Ready = -1f;

            public float Total => Light + Heavy + Air + Structure;
        }

        internal static IEnumerable<string> Roster(Catalog catalog)
        {
            var only = Environment.GetEnvironmentVariable("MB_CV_ONLY");
            var filter = string.IsNullOrEmpty(only) ? null : new HashSet<string>(only.Split(','));
            return catalog.Vehicles.Values
                .Where(v => !v.Static && !v.Boss && !v.Elite && v.CpCost > 0 && MatchSettings.AllVehicles.Contains(v.Id) && (filter == null || filter.Contains(v.Id)))
                .OrderBy(v => v.Class).ThenBy(v => v.CpCost).ThenBy(v => v.Id).Select(v => v.Id);
        }

        /// <summary>A vehicle that runs dry and reloads (a launcher, a missile carrier, an aircraft's stores).</summary>
        internal static bool Limited(VehicleDef def) => def.Flying || def.Mounts.Any(m => m.Weapon.Ammo > 0);

        [Test, Explicit("a measurement: run it by name with MB_BALANCE=1"), Category("Balance")]
        public void MeasureTheRoster()
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("combat value: set MB_BALANCE=1");
            var catalog = LoadCatalog();
            var results = new List<Result>();
            var started = DateTime.Now;
            foreach (var id in Roster(catalog))
            {
                var def = catalog.Vehicle(id);
                foreach (var s in Standards)
                    results.Add(Mean(Seeds.Select(seed => Run(catalog, id, s, seed)).ToList()));
                if (Limited(def)) results.Add(Mean(Seeds.Select(seed => Run(catalog, id, LongRun, seed)).ToList()));
            }
            var outDir = Environment.GetEnvironmentVariable("MB_CV_OUT");
            if (string.IsNullOrEmpty(outDir)) outDir = Path.GetTempPath();
            Directory.CreateDirectory(outDir);
            var tag = Environment.GetEnvironmentVariable("MB_CV_TAG") ?? "now";
            File.WriteAllText(Path.Combine(outDir, $"combat_value_{tag}.tsv"), Tsv(results), new UTF8Encoding(false));
            var summary = Summary(catalog, results);
            File.WriteAllText(Path.Combine(outDir, $"combat_value_{tag}_summary.tsv"), summary, new UTF8Encoding(false));
            TestContext.Out.WriteLine(summary);
            UnityEngine.Debug.Log($"[CombatValueMeasure] {results.Count} runs in {(DateTime.Now - started).TotalSeconds:0} s\n" + summary);
            Assert.Pass();
        }

        /// <summary>
        /// Prompt 13 A.1 and A.7: the theoretical damage a second of every vehicle against each armour,
        /// all mounts added up, the old way (every weapon firing its salvo or magazine over and over
        /// with no reload) and the corrected one (<see cref="FirePower.Sustained"/>: a launcher's load
        /// and reload, an aircraft's stores and rearm), with the damage table and plain armour bonuses.
        /// </summary>
        [Test, Explicit("a measurement: run it by name with MB_BALANCE=1"), Category("Balance")]
        public void PrintTheoreticalDps()
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("theoretical DPS: set MB_BALANCE=1");
            var catalog = GameContent.LoadCatalog();
            var sb = new StringBuilder();
            sb.AppendLine("id\tclass\tcp\told_light\told_heavy\told_air\told_structure\tlight\theavy\tair\tstructure\theavy_per_cp");
            foreach (var def in catalog.Vehicles.Values.Where(v => !v.Boss && !v.Elite).OrderBy(v => v.Static).ThenBy(v => v.Class).ThenBy(v => v.CpCost).ThenBy(v => v.Id))
            {
                var old = new float[4];
                var now = new float[4];
                foreach (var m in def.Mounts)
                {
                    var w = m.Weapon;
                    if (w.Damage <= 0f) continue;
                    var before = FirePower.Volley(w) / MathF.Max(0.1f, w.CycleSeconds);
                    var after = FirePower.Sustained(w, def);
                    foreach (ArmorClass a in Enum.GetValues(typeof(ArmorClass)))
                    {
                        if (!w.CanTarget(a == ArmorClass.Air)) continue;
                        var bonus = 1f;
                        foreach (var b in w.Bonuses)
                            if (b.Armor == a && b.Class == null && b.StillFor <= 0f && !b.Flank) bonus *= b.Mult;
                        var k = catalog.Damage.Multiplier(w, a) * bonus;
                        old[(int)a] += before * k;
                        now[(int)a] += after * k;
                    }
                }
                sb.AppendLine(string.Join("\t", def.Id, def.Class, def.CpCost, F(old[0]), F(old[1]), F(old[2]), F(old[3]), F(now[0]), F(now[1]), F(now[2]), F(now[3]),
                    def.CpCost > 0 ? F(now[1] / def.CpCost) : ""));
            }
            var outDir = Environment.GetEnvironmentVariable("MB_CV_OUT");
            if (string.IsNullOrEmpty(outDir)) outDir = Path.GetTempPath();
            Directory.CreateDirectory(outDir);
            var tag = Environment.GetEnvironmentVariable("MB_CV_TAG") ?? "now";
            File.WriteAllText(Path.Combine(outDir, $"theoretical_dps_{tag}.tsv"), sb.ToString(), new UTF8Encoding(false));
            TestContext.Out.WriteLine(sb.ToString());
            Assert.Pass();
        }

        /// <summary>The shipped catalog, or another balance file (MB_CV_BALANCE: a path) to compare against.</summary>
        internal static Catalog LoadCatalog()
        {
            var path = Environment.GetEnvironmentVariable("MB_CV_BALANCE");
            return string.IsNullOrEmpty(path) ? GameContent.LoadCatalog() : Catalog.FromJson(File.ReadAllText(path));
        }

        private static SimWorld Field(Catalog catalog, int seed) =>
            new SimWorld(catalog, new MapDefinition("range", 300f,
                new[] { new TeamStart(0, new Vector2(0f, -130f)), new TeamStart(1, new Vector2(0f, 130f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed: seed);

        private static readonly Vector2 GroupAt = new(0f, 40f);

        internal static Result Run(Catalog catalog, string id, Scenario scenario, int seed)
        {
            var def = catalog.Vehicle(id);
            var world = Field(catalog, seed);
            // Everything in sight of everyone (artillery has no spotter of its own here), except for a
            // stealthy shooter, whose point is not being seen.
            world.RevealAll = !def.Stealth;
            var count = Math.Clamp((int)MathF.Round(Budget / def.CpCost), 1, 5);
            var ours = new List<Vehicle>();
            var startY = def.Flying ? -95f : -45f;
            for (var i = 0; i < count; i++)
                ours.Add(world.SpawnVehicle(id, 0, new Vector2((i - (count - 1) * 0.5f) * 8f, startY - (i % 2) * 4f), 0f));
            var theirs = new List<Vehicle>();
            void SendWave()
            {
                for (var i = 0; i < scenario.Group.Length; i++)
                {
                    var g = catalog.Vehicle(scenario.Group[i]);
                    var at = GroupAt + new Vector2((i - (scenario.Group.Length - 1) * 0.5f) * (g.Static ? 14f : 8f), g.Static ? 6f : (i % 2) * 5f);
                    theirs.Add(world.SpawnVehicle(scenario.Group[i], 1, at, MathF.PI));
                }
            }
            SendWave();
            var ai = new TacticalAi(0, 1) { Objective = _ => GroupAt };
            var result = new Result { Id = id, Scenario = scenario.Name, Count = count, Cp = def.CpCost * count, Seconds = scenario.Seconds };
            var left = new Dictionary<Vehicle, float>();
            DamageSystem.DamageLog = (by, victim, amount, kind, weapon) =>
            {
                if (victim.Team != 1) return;
                // Credited to the shooters: their own rounds, the blasts and fires they set off (a car
                // bomb's charge and the cook-offs it causes come with no shooter).
                if (by != null && by.Team != 0) return;
                if (!left.TryGetValue(victim, out var hp)) hp = victim.MaxHp;
                var real = MathF.Min(amount, hp);
                left[victim] = MathF.Max(0f, hp - amount);
                switch (victim.Armor)
                {
                    case ArmorClass.Light: result.Light += real; break;
                    case ArmorClass.Heavy: result.Heavy += real; break;
                    case ArmorClass.Air: result.Air += real; break;
                    default: result.Structure += real; break;
                }
            };
            var aliveSteps = 0;
            var onTargetSteps = 0;
            var readySteps = 0;
            var alive = new float[count];
            var waveDownAt = -1.0;
            try
            {
                for (var t = 0f; t < scenario.Seconds; t += TestWorlds.Step)
                {
                    ai.Tick(world, TestWorlds.Step);
                    world.Step(TestWorlds.Step);
                    world.ClearEvents();
                    for (var i = 0; i < count; i++)
                    {
                        var v = ours[i];
                        if (!v.IsAlive) continue;
                        alive[i] += TestWorlds.Step;
                        aliveSteps++;
                        var onTarget = false;
                        for (var m = 0; m < v.Def.Mounts.Count && !onTarget; m++)
                            if (v.Arm(m).Damage > 0f && v.MountTarget(m).IsValid) onTarget = true;
                        if (onTarget) onTargetSteps++;
                        if (v.Flying && Ready(v, onTarget)) readySteps++;
                    }
                    if (ours.All(v => !v.IsAlive)) break;
                    if (theirs.All(v => !v.IsAlive))
                    {
                        if (result.FirstKill < 0f) result.FirstKill = (float)world.Time;
                        if (waveDownAt < 0) waveDownAt = world.Time;
                        // The next wave a few seconds later, where the last one stood.
                        if (world.Time - waveDownAt > 3.0)
                        {
                            theirs.Clear();
                            SendWave();
                            waveDownAt = -1.0;
                        }
                    }
                }
            }
            finally
            {
                DamageSystem.DamageLog = null;
            }
            result.OnTarget = aliveSteps > 0 ? onTargetSteps / (float)aliveSteps : 0f;
            result.Survival = alive.Average();
            if (def.Flying) result.Ready = aliveSteps > 0 ? readySteps / (float)aliveSteps : 0f;
            var aliveShare = result.Survival / scenario.Seconds;
            result.Value = result.Total * (1f + aliveShare) * 0.5f / result.Cp;
            return result;
        }

        /// <summary>
        /// An aircraft attacking or ready to: a target in reach, in its attack hold or run, or with
        /// something left to fire and not on its way out to rearm.
        /// </summary>
        private static bool Ready(Vehicle v, bool onTarget)
        {
            if (onTarget || v.InAttackHold) return true;
            return ReadyHook?.Invoke(v) ?? true;
        }

        /// <summary>Set by the ammunition work (prompt 13 C): whether an aircraft not on target is ready to attack.</summary>
        internal static Func<Vehicle, bool> ReadyHook;

        private static string F(float v) => v.ToString("0.##", CultureInfo.InvariantCulture);

        internal static string Tsv(List<Result> results)
        {
            var sb = new StringBuilder();
            sb.AppendLine("id\tscenario\tcount\tcp\tlight\theavy\tair\tstructure\ttotal\tonTarget\tsurvival\tfirstKill\tready\tvalue");
            foreach (var r in results)
                sb.AppendLine(string.Join("\t", r.Id, r.Scenario, r.Count, r.Cp, F(r.Light), F(r.Heavy), F(r.Air), F(r.Structure), F(r.Total),
                    F(r.OnTarget), F(r.Survival), F(r.FirstKill), F(r.Ready), F(r.Value)));
            return sb.ToString();
        }

        /// <summary>One line per vehicle: class, CP, value per CP in each scenario, the mean over the standard ones, and on-target share.</summary>
        internal static string Summary(Catalog catalog, List<Result> results)
        {
            var sb = new StringBuilder();
            var names = Standards.Select(s => s.Name).Concat(new[] { LongRun.Name }).ToList();
            sb.AppendLine("id\tclass\tcp\t" + string.Join("\t", names) + "\tground\tnoAA\tonTarget\tsurvival\tready");
            foreach (var g in results.GroupBy(r => r.Id))
            {
                var def = catalog.Vehicle(g.Key);
                var cells = names.Select(n => g.FirstOrDefault(r => r.Scenario == n) is { } r ? F(r.Value) : "").ToList();
                var standard = g.Where(r => r.Scenario != LongRun.Name).ToList();
                // Ground value: the mean over the six ground groups, with and without anti-air (the
                // like-for-like comparison for anything that fights the ground); noAA: the three without.
                var ground = standard.Where(r => r.Scenario != "air").ToList();
                var noAa = ground.Where(r => !r.Scenario.EndsWith("+AA")).ToList();
                sb.AppendLine(string.Join("\t", g.Key, def.Class, def.CpCost) + "\t" + string.Join("\t", cells) + "\t" +
                    F(ground.Average(r => r.Value)) + "\t" + F(noAa.Average(r => r.Value)) + "\t" + F(standard.Average(r => r.OnTarget)) + "\t" +
                    F(standard.Average(r => r.Survival)) + "\t" +
                    (def.Flying ? F(g.Average(r => r.Ready)) : ""));
            }
            return sb.ToString();
        }
    }
}
