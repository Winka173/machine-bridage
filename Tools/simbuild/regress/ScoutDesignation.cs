// Scout Target Designation (10/10): the gameplay measurement harness entry (prompt section 14, "Gameplay tests").
// Mode `scout` (MB_SET = all | light | heavy | artillery | air | siege | boss). NOT RUN: testing is paused by the owner until the
// AI rework lands. Same seeds, same map, same opponent; the variants differ only in the scouts the player side adds, and the
// scouts' CP is counted in the damage-per-CP column. Output: one tab-separated row per set x variant x seed.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Sandbox;
using Vector2 = System.Numerics.Vector2;

static class ScoutSuite
{
    static readonly CultureInfo Inv = CultureInfo.InvariantCulture;
    const float CapSeconds = 90f;

    static readonly string[] Core = { "main_battle_tank", "main_battle_tank", "light_tank", "light_tank", "ifv" };

    static readonly (string Name, string[] Ids)[] Variants =
    {
        ("none", new string[0]),
        ("jeep", new[] { "scout_jeep" }),
        ("drone", new[] { "recon_drone" }),
        ("heli", new[] { "scout_heli" }),
        ("2x jeep", new[] { "scout_jeep", "scout_jeep" }),
        ("mixed", new[] { "scout_jeep", "recon_drone", "scout_heli" }),
    };

    static readonly (string Name, string[] Ids)[] Sets =
    {
        ("light", new[] { "light_tank", "light_tank", "light_tank", "scout_jeep", "light_tank", "ifv" }),
        ("heavy", new[] { "heavy_tank", "heavy_tank", "heavy_tank", "heavy_tank" }),
        ("artillery", new[] { "artillery", "artillery", "artillery", "artillery", "light_tank", "light_tank" }),
        ("air", new[] { "aa_vehicle", "aa_vehicle", "aa_vehicle", "attack_helicopter", "attack_helicopter" }),
        ("siege", new[] { "guard_tower", "guard_tower", "guard_tower", "light_tank" }),
        ("boss", new[] { "behemoth" }),
    };

    public static void Run(Catalog cat, StringBuilder sb, string only, int[] seeds)
    {
        sb.AppendLine("set\tvariant\tseed\tscout_cp\tteam_cp\tteam0_damage\tdamage_per_cp\tkill_time_s\tmarked_ticks\tscout_survival\twinner");
        foreach (var (setName, enemyIds) in Sets)
        {
            if (only != "all" && only != setName) continue;
            foreach (var (variant, scouts) in Variants)
            foreach (var seed in seeds)
            {
                try { sb.AppendLine(One(cat, setName, enemyIds, variant, scouts, seed)); }
                catch (Exception e) { sb.AppendLine($"{setName}\t{variant}\t{seed}\tERROR {e.GetType().Name}: {e.Message.Split('\n')[0]}"); }
            }
        }
    }

    static string One(Catalog cat, string setName, string[] enemyIds, string variant, string[] scoutIds, int seed)
    {
        var world = new SimWorld(cat, SandboxMaps.Flat(), seed);
        var mine = new List<Vehicle>();
        var scouts = new List<Vehicle>();
        for (var i = 0; i < Core.Length; i++) mine.Add(world.SpawnVehicle(Core[i], 0, new Vector2(-30f + i * 9f, -22f), 0f));
        for (var i = 0; i < scoutIds.Length; i++)
        {
            var s = world.SpawnVehicle(scoutIds[i], 0, new Vector2(-18f + i * 12f, -14f), 0f);
            scouts.Add(s);
            mine.Add(s);
        }
        var enemies = new List<Vehicle>();
        for (var i = 0; i < enemyIds.Length; i++) enemies.Add(world.SpawnVehicle(enemyIds[i], 1, new Vector2(-30f + i * 11f, 22f), MathF.PI));
        var damage = 0f;
        var markedTicks = 0;
        var killAt = -1f;
        DamageSystem.DamageLog = (by, victim, amount, kind, weapon) => { if (by != null && by.Team == 0 && victim.Team == 1) damage += amount; };
        try
        {
            for (var t = 0f; t < CapSeconds; t += 0.05f)
            {
                world.Step(0.05f);
                world.ClearEvents();
                if (world.MarkedTargets.Count > 0) markedTicks++;
                if (killAt < 0f && enemies.All(e => !e.IsAlive)) { killAt = t; break; }
                if (mine.All(m => !m.IsAlive)) break;
            }
        }
        finally { DamageSystem.DamageLog = null; }
        var scoutCp = scouts.Sum(s => s.Def.CpCost);
        var teamCp = mine.Sum(m => m.Def.CpCost);
        var alive = scouts.Count == 0 ? "n/a" : (scouts.Count(s => s.IsAlive) / (float)scouts.Count).ToString("0.00", Inv);
        var winner = enemies.All(e => !e.IsAlive) ? "player" : mine.All(m => !m.IsAlive) ? "enemy" : "none";
        return string.Join("\t", setName, variant, seed.ToString(Inv), scoutCp.ToString(Inv), teamCp.ToString(Inv), damage.ToString("0", Inv),
            (damage / Math.Max(1, teamCp)).ToString("0.0", Inv), killAt < 0f ? "cap" : killAt.ToString("0.0", Inv), markedTicks.ToString(Inv), alive, winner);
    }
}
