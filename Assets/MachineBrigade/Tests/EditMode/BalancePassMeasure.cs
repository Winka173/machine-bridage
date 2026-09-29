using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// The balance pass after prompt 18: the smaller measurements behind its decisions (DECISIONS 19B). Run by
    /// name with MB_BALANCE=1; MB_CV_OUT and MB_CV_TAG name the output (as for the combat value).
    /// </summary>
    public class BalancePassMeasure
    {
        private static void Gate()
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("balance measurement: set MB_BALANCE=1");
        }

        private static void Write(string name, string text)
        {
            TestContext.Out.WriteLine(text);
            UnityEngine.Debug.Log($"[BalancePassMeasure.{name}]\n{text}");
            var dir = Environment.GetEnvironmentVariable("MB_CV_OUT");
            if (!string.IsNullOrEmpty(dir)) File.WriteAllText(Path.Combine(dir, $"{name}_{Environment.GetEnvironmentVariable("MB_CV_TAG") ?? "now"}.txt"), text);
        }

        /// <summary>B.1: how often the wheeled gun's rounds land on a side or the rear (its flank bonus), in the combat-value fights.</summary>
        [Test, Explicit("a measurement: run it by name with MB_BALANCE=1"), Category("Balance")]
        public void PrintWheeledGunFlankShare()
        {
            Gate();
            var catalog = CombatValueMeasure.LoadCatalog();
            var sb = new StringBuilder();
            foreach (var s in CombatValueMeasure.Standards.Where(x => x.Name is "light" or "tanks" or "light+AA" or "tanks+AA"))
            {
                int hits = 0, flank = 0;
                CombatValueMeasure.OnHit = (by, victim, amount, weapon) =>
                {
                    if (by == null || weapon == null || weapon.Id != "gun_105_wheeled") return;
                    hits++;
                    if (DamageSystem.Flanked(victim, by.Position)) flank++;
                };
                try
                {
                    foreach (var seed in new[] { 13, 14, 15 }) CombatValueMeasure.Run(catalog, "wheeled_gun", s, seed);
                }
                finally
                {
                    CombatValueMeasure.OnHit = null;
                }
                sb.AppendLine($"{s.Name,-10} main-gun hits {hits,4}, on a side or the rear {flank,4} ({(hits > 0 ? flank / (float)hits : 0f):P0})");
            }
            Write("flank_share", sb.ToString());
        }

        /// <summary>A.3: the HQ alone (level 5 and 3, no towers) against the base-balance air army, five seeds.</summary>
        [Test, Explicit("a measurement: run it by name with MB_BALANCE=1"), Category("Balance"), Timeout(3600000)]
        public void PrintHqAgainstAircraft()
        {
            Gate();
            var catalog = CombatValueMeasure.LoadCatalog();
            var sb = new StringBuilder();
            foreach (var level in new[] { 5, 3 })
                foreach (var (name, army) in new[] { ("air", BaseBalanceTests.Enemies["air"]), ("air x2", BaseBalanceTests.Enemies["air"].Concat(BaseBalanceTests.Enemies["air"]).ToArray()) })
                {
                    var hq = new List<float>();
                    var killed = new List<float>();
                    for (var seed = 1; seed <= 5; seed++)
                    {
                        BaseBalanceTests.Battle(catalog, new BaseLoadout { HqLevel = level }, army, seed, 5f, out _);
                        hq.Add(BaseBalanceTests.LastHq);
                        killed.Add(BaseBalanceTests.LastKilled);
                    }
                    sb.AppendLine($"HQ level {level} alone vs {name,-7} ({army.Length} aircraft, {army.Sum(a => catalog.Vehicle(a).CpCost)} CP), 5 min: HQ left {hq.Average():P0} " +
                                  $"(held {hq.Count(x => x > 0f)}/5), aircraft destroyed {killed.Average():P0}");
                }
            Write("hq_air", sb.ToString());
        }

        internal sealed class Target
        {
            public string Name;
            public string[] Group;
            public float Spacing = 8f;
        }

        private static readonly Target[] Targets =
        {
            new() { Name = "light", Group = new[] { "armored_car", "armored_car", "armored_car", "scout_jeep" } },
            new() { Name = "column", Group = new[] { "armored_car", "armored_car", "armored_car", "armored_car", "armored_car", "armored_car" }, Spacing = 9f },
            new() { Name = "tanks", Group = new[] { "main_battle_tank", "main_battle_tank", "main_battle_tank" } },
            new() { Name = "fort", Group = new[] { "gun_turret", "mg_bunker", "guard_tower" }, Spacing = 12f },
        };

        /// <summary>
        /// C.1: a fire support's value per CP: called on a group standing in a row (a line strike dragged along
        /// it, a circle on its middle), the real damage it does (never more than a victim had left), three seeds.
        /// </summary>
        [Test, Explicit("a measurement: run it by name with MB_BALANCE=1"), Category("Balance")]
        public void PrintSupportValue()
        {
            Gate();
            var catalog = CombatValueMeasure.LoadCatalog();
            var ids = new[] { "artillery_barrage", "airstrike", "napalm_strike", "cruise_missile", "remote_mines", "cluster_strike", "moab" };
            var sb = new StringBuilder("support\tcp\t" + string.Join("\t", Targets.Select(t => t.Name)) + "\tmean\tmean_per_cp\n");
            foreach (var id in ids)
            {
                var s = catalog.Supports[id];
                var values = new List<float>();
                foreach (var t in Targets)
                    values.Add(new[] { 13, 14, 15 }.Average(seed => Strike(catalog, s, t, seed)));
                var mean = values.Average();
                sb.AppendLine($"{id}\t{s.CpCost}\t{string.Join("\t", values.Select(v => v.ToString("0")))}\t{mean:0}\t{(s.CpCost > 0 ? (mean / s.CpCost).ToString("0") : "-")}");
            }
            Write("support_value", sb.ToString());
        }

        private static float Strike(Catalog catalog, SupportDef s, Target t, int seed)
        {
            var world = new SimWorld(catalog, new MapDefinition("range", 300f,
                new[] { new TeamStart(0, new Vector2(0f, -130f)), new TeamStart(1, new Vector2(0f, 130f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed: seed);
            var victims = new List<Vehicle>();
            var n = t.Group.Length;
            for (var i = 0; i < n; i++)
            {
                var v = world.SpawnVehicle(t.Group[i], 1, new Vector2((i - (n - 1) * 0.5f) * t.Spacing, 40f), MathF.PI);
                if (v.Def.Static) world.AnchorDefence(v);
                v.HoldFire = true;
                victims.Add(v);
            }
            var half = (n - 1) * 0.5f * t.Spacing;
            var start = s.IsLine ? new Vector2(-half - 4f, 40f) : new Vector2(0f, 40f);
            var towards = s.IsLine ? new Vector2(half + 4f, 40f) : new Vector2(1f, 40f);
            if (s.IsLine && s.Length > 0f)
            {
                // Centre the line on the row when it is longer than the row.
                var extra = MathF.Max(0f, s.Length - (2f * half + 8f)) * 0.5f;
                start.X -= extra;
            }
            var damage = 0f;
            var left = new Dictionary<Vehicle, float>();
            DamageSystem.DamageLog = (by, victim, amount, kind, weapon) =>
            {
                if (victim.Team != 1) return;
                if (!left.TryGetValue(victim, out var hp)) hp = victim.MaxHp;
                damage += MathF.Min(amount, hp);
                left[victim] = MathF.Max(0f, hp - amount);
            };
            try
            {
                if (s.Kind == SupportKind.Minefield)
                {
                    // Mines are laid where the group will drive: the group goes through the field.
                    world.Strikes.Launch(s, 0, new Vector2(0f, 20f), new Vector2(1f, 20f));
                    for (var k = 0f; k < s.Delay + 1f; k += TestWorlds.Step) { world.Step(TestWorlds.Step); world.ClearEvents(); }
                    foreach (var v in victims.Where(v => !v.Def.Static))
                        world.Submit(new Sim.Commands.Command(Sim.Commands.CommandType.Move, 1, new[] { v.Id }, new Vector2(v.Position.X, -20f)));
                }
                else world.Strikes.Launch(s, 0, start, towards);
                for (var k = 0f; k < s.Delay + s.Duration + 15f; k += TestWorlds.Step)
                {
                    world.Step(TestWorlds.Step);
                    world.ClearEvents();
                }
            }
            finally
            {
                DamageSystem.DamageLog = null;
            }
            return damage;
        }
    }
}
