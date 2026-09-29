using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The balance pass after prompt 18 (A.1): a tower's combat value in the vehicles' CP. A tower
    /// cannot go to the fight, so it is measured holding a point: alone, it fights a ladder of attacking
    /// groups of rising CP of one role (light vehicles, tanks, aircraft), each attacker ordered at it,
    /// to the end or 150 s, three seeds a rung. A fight scores the defender's health left (a win) or
    /// minus the attackers' (a loss), from +1 to -1; the tower's <b>worth</b> is the CP where the score
    /// crosses 0 (straight lines between rungs). Every buyable ground fighter (light, tank, heavy, tank
    /// hunter classes; anti-air against the air ladder) is measured the same way, one vehicle holding the
    /// point, and the median of their worth per CP turns a tower's worth into the CP of a vehicle doing
    /// the same: its <b>equivalent CP</b>. Run with MB_BALANCE=1 (MB_CV_OUT, MB_CV_TAG; MB_TV_ONLY=a,b
    /// limits the towers, MB_TV_SEEDS the seeds).
    /// </summary>
    public class TowerValueMeasure
    {
        private const float Limit = 150f;
        private static readonly Vector2 HoldAt = new(0f, -40f);

        /// <summary>The attacking ladders, rising in CP.</summary>
        internal static readonly Dictionary<string, string[][]> Ladders = new()
        {
            ["light"] = new[]
            {
                new[] { "scout_jeep" }, new[] { "armored_car" }, new[] { "armored_car", "scout_jeep" }, new[] { "armored_car", "armored_car" },
                new[] { "armored_car", "armored_car", "scout_jeep" }, new[] { "armored_car", "armored_car", "armored_car" },
                new[] { "armored_car", "armored_car", "armored_car", "scout_jeep" }, new[] { "armored_car", "armored_car", "armored_car", "armored_car" },
                new[] { "armored_car", "armored_car", "armored_car", "armored_car", "armored_car" },
                new[] { "armored_car", "armored_car", "armored_car", "armored_car", "armored_car", "armored_car" },
                new[] { "armored_car", "armored_car", "armored_car", "armored_car", "armored_car", "armored_car", "armored_car", "armored_car" },
            },
            ["tanks"] = new[]
            {
                new[] { "light_tank" }, new[] { "light_tank", "light_tank" }, new[] { "main_battle_tank" }, new[] { "main_battle_tank", "light_tank" },
                new[] { "main_battle_tank", "light_tank", "light_tank" }, new[] { "main_battle_tank", "main_battle_tank" },
                new[] { "main_battle_tank", "main_battle_tank", "light_tank" }, new[] { "main_battle_tank", "main_battle_tank", "main_battle_tank" },
                new[] { "main_battle_tank", "main_battle_tank", "main_battle_tank", "main_battle_tank" },
            },
            ["air"] = new[]
            {
                new[] { "scout_heli" }, new[] { "strike_drone" }, new[] { "scout_heli", "scout_heli" }, new[] { "attack_helicopter" },
                new[] { "attack_helicopter", "scout_heli" }, new[] { "attack_helicopter", "strike_drone" }, new[] { "attack_helicopter", "attack_helicopter" },
                new[] { "attack_helicopter", "attack_helicopter", "strike_drone" }, new[] { "attack_helicopter", "attack_helicopter", "attack_helicopter" },
            },
        };

        private static readonly HashSet<UnitClass> GroundFighters = new() { UnitClass.Light, UnitClass.Tank, UnitClass.Heavy, UnitClass.TankHunter };

        private static int[] Seeds
        {
            get
            {
                var list = Environment.GetEnvironmentVariable("MB_TV_SEEDS");
                return string.IsNullOrEmpty(list) ? new[] { 13, 14, 15 } : list.Split(',').Select(int.Parse).ToArray();
            }
        }

        /// <summary>Every weaponed tower and its branches, in data order.</summary>
        internal static List<string> Towers(Catalog catalog)
        {
            var only = Environment.GetEnvironmentVariable("MB_TV_ONLY");
            var filter = string.IsNullOrEmpty(only) ? null : new HashSet<string>(only.Split(','));
            var list = new List<string>();
            foreach (var t in TowerCards.All(catalog))
            {
                if (!catalog.Vehicles[t].Mounts.Any(m => m.Weapon.Damage > 0f)) continue;
                if (filter == null || filter.Contains(t)) list.Add(t);
                foreach (var b in TowerCards.Branches(catalog, t))
                    if (filter == null || filter.Contains(t) || filter.Contains(b)) list.Add(b);
            }
            return list;
        }

        [Test, Explicit("a measurement: run it by name with MB_BALANCE=1"), Category("Balance"), Timeout(7200000)]
        public void MeasureTheTowers()
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("tower value: set MB_BALANCE=1");
            var catalog = CombatValueMeasure.LoadCatalog();
            var started = DateTime.Now;
            var roles = Ladders.Keys.ToList();
            // The vehicles: one of each, holding the point; their worth per CP.
            var refText = new StringBuilder("id\tclass\tcp\trole\tworth\tworth_per_cp\n");
            var perCp = new Dictionary<string, float>();
            foreach (var role in roles)
            {
                var ratios = new List<float>();
                foreach (var id in CombatValueMeasure.Roster(catalog))
                {
                    var def = catalog.Vehicle(id);
                    var fits = role == "air" ? def.Class == UnitClass.AntiAir : GroundFighters.Contains(def.Class);
                    if (!fits) continue;
                    var worth = Worth(catalog, id, role);
                    ratios.Add(worth / def.CpCost);
                    refText.AppendLine(string.Join("\t", id, def.Class, def.CpCost, role, F(worth), F(worth / def.CpCost)));
                }
                perCp[role] = Median(ratios);
            }
            var sb = new StringBuilder("id\tsize\t" + string.Join("\t", roles.Select(r => r + "_cp")) + "\t" + string.Join("\t", roles.Select(r => r + "_worth")) + "\n");
            foreach (var t in Towers(catalog))
            {
                var worth = roles.ToDictionary(r => r, r => Worth(catalog, t, r));
                sb.AppendLine(string.Join("\t", new[] { t, catalog.Vehicles[t].Fort?.Size.ToString() ?? "" }
                    .Concat(roles.Select(r => F(worth[r] / Math.Max(0.01f, perCp[r]))))
                    .Concat(roles.Select(r => F(worth[r])))));
            }
            sb.AppendLine("vehicles' median worth per CP\t\t" + string.Join("\t", roles.Select(r => F(perCp[r]))));
            var outDir = Environment.GetEnvironmentVariable("MB_CV_OUT");
            if (string.IsNullOrEmpty(outDir)) outDir = Path.GetTempPath();
            Directory.CreateDirectory(outDir);
            var tag = Environment.GetEnvironmentVariable("MB_CV_TAG") ?? "now";
            File.WriteAllText(Path.Combine(outDir, $"tower_value_{tag}.tsv"), sb.ToString(), new UTF8Encoding(false));
            File.WriteAllText(Path.Combine(outDir, $"tower_value_{tag}_reference.tsv"), refText.ToString(), new UTF8Encoding(false));
            TestContext.Out.WriteLine(sb.ToString());
            UnityEngine.Debug.Log($"[TowerValueMeasure] {(DateTime.Now - started).TotalSeconds:0} s\n" + sb);
            Assert.Pass();
        }

        /// <summary>The CP of attackers of a role the unit holds against evenly (score 0), up the ladder.</summary>
        internal static float Worth(Catalog catalog, string id, string role)
        {
            var ladder = Ladders[role];
            var prevCp = 0f;
            var prevScore = 1f;
            foreach (var group in ladder)
            {
                var cp = group.Sum(g => catalog.Vehicle(g).CpCost);
                var score = Seeds.Average(s => Fight(catalog, id, group, s));
                if (score <= 0f)
                    return prevCp + (cp - prevCp) * prevScore / MathF.Max(0.01f, prevScore - score);
                prevCp = cp;
                prevScore = score;
            }
            return prevCp; // held the whole ladder: at least its top
        }

        /// <summary>
        /// One fight: the unit at the point (a tower anchored), the group coming at it, to the end or the
        /// limit. +its health share left when it wins, -the attackers' health share left when it loses.
        /// </summary>
        internal static float Fight(Catalog catalog, string id, string[] group, int seed)
        {
            var def = catalog.Vehicle(id);
            var world = Field(catalog, seed);
            world.RevealAll = true;
            var ours = world.SpawnVehicle(id, 0, HoldAt, 0f);
            if (def.Static) world.AnchorDefence(ours);
            var air = group.Any(g => catalog.Vehicle(g).Flying);
            var from = new Vector2(0f, air ? 100f : 60f);
            var theirs = new List<Vehicle>();
            for (var i = 0; i < group.Length; i++)
                theirs.Add(world.SpawnVehicle(group[i], 1, from + new Vector2((i - (group.Length - 1) * 0.5f) * 8f, (i % 2) * 5f), MathF.PI));
            var ids = theirs.Select(v => v.Id).ToArray();
            var next = 0.0;
            for (var t = 0f; t < Limit && ours.IsAlive && theirs.Any(v => v.IsAlive); t += TestWorlds.Step)
            {
                if (world.Time >= next)
                {
                    world.Submit(new Sim.Commands.Command(Sim.Commands.CommandType.Attack, 1, ids.Where(x => world.TryGetVehicle(x, out var a) && a.IsAlive).ToArray(), ours.Position, ours.Id));
                    next = world.Time + 2.0;
                }
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
            if (!ours.IsAlive) return -theirs.Sum(v => v.IsAlive ? v.Hp : 0f) / theirs.Sum(v => v.MaxHp);
            if (theirs.All(v => !v.IsAlive)) return ours.Hp / ours.MaxHp;
            // The clock: the share of health each side lost, the difference.
            var theirsLost = 1f - theirs.Sum(v => v.IsAlive ? v.Hp : 0f) / theirs.Sum(v => v.MaxHp);
            var oursLost = 1f - ours.Hp / ours.MaxHp;
            return (theirsLost - oursLost) * 0.5f;
        }

        /// <summary>
        /// A.2 C-RAM: the share of a salvo of medium rockets it stops. Two launchers fire on a target
        /// behind a C-RAM for 60 s from inside their reach; rockets fired against rounds intercepted,
        /// three seeds; the C-RAM and each branch.
        /// </summary>
        [Test, Explicit("a measurement: run it by name with MB_BALANCE=1"), Category("Balance")]
        public void PrintCRamInterception()
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("C-RAM: set MB_BALANCE=1");
            var catalog = CombatValueMeasure.LoadCatalog();
            var sb = new StringBuilder();
            var guards = new[] { "c_ram" }.Concat(TowerCards.Branches(catalog, "c_ram")).ToList();
            foreach (var launcher in new[] { "mlrs", "rocket_technical", "heavy_rocket_artillery" })
                foreach (var guard in guards)
                {
                    int fired = 0, stopped = 0;
                    var reach = MathF.Min(70f, catalog.Vehicle(launcher).Weapon.Range * 0.85f);
                    foreach (var seed in new[] { 13, 14, 15 })
                    {
                        var world = Field(catalog, seed);
                        world.RevealAll = true;
                        var target = world.SpawnVehicle("gun_turret", 0, new Vector2(0f, 0f), 0f);
                        world.AnchorDefence(target);
                        world.MakeSparring(target);
                        target.HoldFire = true;
                        var c = world.SpawnVehicle(guard, 0, new Vector2(8f, -6f), 0f);
                        world.AnchorDefence(c);
                        world.MakeSparring(c);
                        for (var i = 0; i < 2; i++)
                        {
                            var a = world.SpawnVehicle(launcher, 1, new Vector2(-10f + i * 20f, reach), MathF.PI);
                            world.MakeSparring(a);
                            world.Submit(new Sim.Commands.Command(Sim.Commands.CommandType.Attack, 1, new[] { a.Id }, target.Position, target.Id));
                        }
                        for (var t = 0f; t < 60f; t += TestWorlds.Step)
                        {
                            world.Step(TestWorlds.Step);
                            foreach (var e in world.Events)
                            {
                                if (e.Kind == SimEventKind.WeaponFired && e.Team == 1) fired++;
                                if (e.Kind == SimEventKind.Intercepted && e.Team == 0) stopped++;
                            }
                            world.ClearEvents();
                        }
                    }
                    sb.AppendLine($"{guard,-18} vs {launcher,-24} fired {fired / 3f,6:0.0} intercepted {stopped / 3f,6:0.0} ({(fired > 0 ? stopped / (float)fired : 0f):P0})");
                }
            TestContext.Out.WriteLine(sb.ToString());
            UnityEngine.Debug.Log("[TowerValueMeasure.CRam]\n" + sb);
            var dir = Environment.GetEnvironmentVariable("MB_CV_OUT");
            if (!string.IsNullOrEmpty(dir)) File.WriteAllText(Path.Combine(dir, "c_ram_" + (Environment.GetEnvironmentVariable("MB_CV_TAG") ?? "now") + ".txt"), sb.ToString());
            Assert.Pass();
        }

        private static SimWorld Field(Catalog catalog, int seed) =>
            new SimWorld(catalog, new MapDefinition("range", 300f,
                new[] { new TeamStart(0, new Vector2(0f, -130f)), new TeamStart(1, new Vector2(0f, 130f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed: seed);

        private static float Median(IEnumerable<float> values)
        {
            var list = values.OrderBy(v => v).ToList();
            if (list.Count == 0) return 0f;
            return list.Count % 2 == 1 ? list[list.Count / 2] : (list[list.Count / 2 - 1] + list[list.Count / 2]) * 0.5f;
        }

        private static string F(float v) => v.ToString("0.##", CultureInfo.InvariantCulture);
    }
}
