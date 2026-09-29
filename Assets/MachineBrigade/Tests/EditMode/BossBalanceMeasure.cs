using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Play-test 6 (DECISIONS 21G): every land boss against a geared player (card rank 7, about half the equipment
    /// caps: the campaign's curve entering act IV, DECISIONS 19A). Four tanks in a column, the standard army, one
    /// heavy bomber's load and one barrage and one airstrike on the boss standing still. Run with MB_BALANCE=1;
    /// MB_BOSSES=a,b limits the bosses, MB_SEEDS the seeds (21, 22), MB_CV_OUT a folder for the table.
    /// </summary>
    public class BossBalanceMeasure
    {
        private const float Step = 0.05f;

        /// <summary>Rank 7 (+30 % health and damage) and equipment at about half its caps: +12 % health and damage, +6 % fire rate, -8 % damage taken.</summary>
        internal static readonly VehicleBoost Geared = new(1.30f * 1.12f, 1.30f * 1.12f, 1.06f, 1f, 0.92f, 0f, SpecialModule.None, 0f);

        /// <summary>A rank 7 fire-support card's damage (CardRanks.Bonus).</summary>
        internal const float GearedStrike = 1.30f;

        private static readonly string[] Column = { "main_battle_tank", "main_battle_tank", "main_battle_tank", "main_battle_tank" };

        private static readonly string[] Army =
            { "main_battle_tank", "main_battle_tank", "main_battle_tank", "main_battle_tank", "tank_destroyer", "tank_destroyer", "fpv_carrier",
              "fpv_carrier", "aa_vehicle", "ifv", "ifv", "attack_helicopter", "attack_helicopter", "mlrs", "artillery" };

        internal static SimWorld Lab(Catalog catalog, int seed, bool geared = true)
        {
            var world = new SimWorld(catalog, new MapDefinition("lab", 300f,
                new[] { new TeamStart(0, new Vector2(-120f, -120f)), new TeamStart(1, new Vector2(120f, 120f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed) { RevealAll = true };
            if (geared) world.SetBoosts(0, _ => Geared, _ => GearedStrike, strikeRank: _ => 7);
            return world;
        }

        /// <summary>The land bosses (a ship needs the sea; the measure's field has none).</summary>
        internal static List<string> LandBosses(Catalog catalog)
        {
            var only = Environment.GetEnvironmentVariable("MB_BOSSES");
            var ids = catalog.Vehicles.Values.Where(v => v.Boss && !v.Static && v.Naval == null && v.Burrow is not { Sea: true }).Select(v => v.Id).OrderBy(id => id, StringComparer.Ordinal).ToList();
            return string.IsNullOrEmpty(only) ? ids : ids.Where(only.Split(',').Contains).ToList();
        }

        /// <summary>What the boss dealt a second in the last fight (a check that it fights at all).</summary>
        internal static float LastBossDps;

        /// <summary>A fight to the boss's death or the attackers': (seconds or -1, attackers lost, boss health share left).</summary>
        internal static (float time, int lost, float left) Fight(Catalog catalog, string boss, string[] attackers, int seed, bool column, float limit, bool escorts = false)
        {
            var world = Lab(catalog, seed);
            if (escorts) world.EscortSettings = EscortSettings.For(catalog.EscortRules, "Normal");
            var b = world.SpawnVehicle(boss, 1, new Vector2(0f, 20f), MathF.PI);
            var ids = new List<EntityId>();
            for (var i = 0; i < attackers.Length; i++)
            {
                var at = column ? new Vector2(0f, -55f - 9f * i) : new Vector2(-42f + 6f * i, -50f - (i % 3) * 6f);
                ids.Add(world.SpawnVehicle(attackers[i], 0, at, 0f).Id);
            }
            var dealt = 0f;
            Sim.Combat.DamageSystem.DamageLog = (by, victim, amount, kind, weapon) =>
            {
                if (by == b && victim.Team == 0) dealt += amount;
            };
            try
            {
                for (var t = 0f; t < limit; t += Step)
                {
                    if (world.Tick % 40 == 0) world.Submit(new Command(CommandType.Attack, 0, ids, target: b.Id));
                    world.Step(Step);
                    world.ClearEvents();
                    var lost = ids.Count(id => !world.TryGetVehicle(id, out var v) || !v.IsAlive);
                    if (!b.IsAlive) return ((float)world.Time, lost, 0f);
                    if (lost == ids.Count) return (-1f, lost, b.Hp / b.MaxHp);
                }
                return (-1f, ids.Count(id => !world.TryGetVehicle(id, out var v) || !v.IsAlive), b.Hp / b.MaxHp);
            }
            finally
            {
                LastBossDps = dealt / MathF.Max(1f, (float)world.Time);
                Sim.Combat.DamageSystem.DamageLog = null;
            }
        }

        /// <summary>The share of the boss's health one heavy bomber's load takes (the boss holding its fire).</summary>
        internal static float BomberShare(Catalog catalog, string boss, int seed)
        {
            var world = Lab(catalog, seed);
            var b = world.SpawnVehicle(boss, 1, new Vector2(0f, 20f), MathF.PI);
            b.HoldFire = true;
            var bomber = world.SpawnVehicle("heavy_bomber", 0, new Vector2(-60f, -40f), 0f);
            // One load: what the boss loses in the 6 s from the first bomb that reaches it.
            var first = -1.0;
            var lost = 0f;
            Sim.Combat.DamageSystem.DamageLog = (by, victim, amount, kind, weapon) =>
            {
                if (victim != b) return;
                if (first < 0.0 && weapon is { Projectile: ProjectileKind.Bomb }) first = world.Time;
                if (first >= 0.0 && world.Time - first <= 6.0) lost += amount;
            };
            try
            {
                for (var t = 0f; t < 40f; t += Step)
                {
                    if (world.Tick % 20 == 0) world.Submit(new Command(CommandType.Attack, 0, new[] { bomber.Id }, target: b.Id));
                    world.Step(Step);
                    world.ClearEvents();
                    if (!b.IsAlive || (first >= 0.0 && world.Time - first > 6.0)) break;
                }
            }
            finally
            {
                Sim.Combat.DamageSystem.DamageLog = null;
            }
            return lost / b.MaxHp;
        }

        /// <summary>The share of the boss's health one fire support at rank 7 takes, called on it standing still.</summary>
        internal static float StrikeShare(Catalog catalog, string boss, string support, int seed)
        {
            var world = Lab(catalog, seed);
            var b = world.SpawnVehicle(boss, 1, new Vector2(0f, 20f), MathF.PI);
            b.HoldFire = true;
            var s = catalog.Supports[support];
            var start = b.Hp;
            var from = s.IsLine ? new Vector2(-s.Length * 0.5f, 20f) : new Vector2(0f, 20f);
            world.Strikes.Launch(s, 0, from, s.IsLine ? new Vector2(s.Length * 0.5f, 20f) : new Vector2(1f, 20f));
            for (var t = 0f; t < s.Delay + s.Duration + 8f; t += Step)
            {
                world.Step(Step);
                world.ClearEvents();
                if (!b.IsAlive) break;
            }
            return (start - (b.IsAlive ? b.Hp : 0f)) / b.MaxHp;
        }

        [Test, Explicit("a measurement: run it by name with MB_BALANCE=1"), Category("Balance"), Timeout(7200000)]
        public void PrintBossBalance()
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("boss balance: set MB_BALANCE=1");
            var catalog = CombatValueMeasure.LoadCatalog();
            var seedList = Environment.GetEnvironmentVariable("MB_SEEDS");
            var seeds = string.IsNullOrEmpty(seedList) ? new[] { 21, 22 } : seedList.Split(',').Select(int.Parse).ToArray();
            var sb = new StringBuilder("boss\trank\thp\tboss_dps\tcolumn_kill_s\tcolumn_lost\tcolumn_left\tcolumn_esc_kill_s\tcolumn_esc_lost\tarmy_kill_s\tarmy_lost\tbomber\tbarrage\tairstrike\n");
            var started = DateTime.Now;
            foreach (var id in LandBosses(catalog))
            {
                var def = catalog.Vehicles[id];
                var col = seeds.Select(s => Fight(catalog, id, Column, s, true, 300f)).ToList();
                var dps = LastBossDps;
                var esc = seeds.Select(s => Fight(catalog, id, Column, s, true, 300f, escorts: true)).ToList();
                var army = seeds.Select(s => Fight(catalog, id, Army, s, false, 600f)).ToList();
                string Kill(List<(float time, int lost, float left)> r) => string.Join("/", r.Select(x => x.time < 0f ? "-" : x.time.ToString("0")));
                string Lost(List<(float time, int lost, float left)> r) => r.Average(x => x.lost).ToString("0.0");
                var bomber = seeds.Average(s => BomberShare(catalog, id, s));
                var barrage = seeds.Average(s => StrikeShare(catalog, id, "artillery_barrage", s));
                var air = seeds.Average(s => StrikeShare(catalog, id, "airstrike", s));
                sb.AppendLine($"{id}\t{def.Rank}\t{def.MaxHp:0}\t{dps:0}\t{Kill(col)}\t{Lost(col)}\t{col.Average(x => x.left):P0}\t{Kill(esc)}\t{Lost(esc)}\t{Kill(army)}\t{Lost(army)}\t{bomber:P0}\t{barrage:P0}\t{air:P0}");
            }
            sb.AppendLine($"({(DateTime.Now - started).TotalSeconds:0} s)");
            Debug.Log("[BossBalanceMeasure]\n" + sb);
            var dir = Environment.GetEnvironmentVariable("MB_CV_OUT");
            if (!string.IsNullOrEmpty(dir)) File.WriteAllText(Path.Combine(dir, "boss_balance_" + (Environment.GetEnvironmentVariable("MB_CV_TAG") ?? "now") + ".tsv"), sb.ToString());
            Assert.Pass();
        }
    }
}
