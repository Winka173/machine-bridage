using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using System.Text.RegularExpressions;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Events;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 13 A.6: what slower missiles do to hit rates. A launcher fires at a target that
    /// cannot die (it flies or drives as usual, drops flares, and an Iron Beam's active protection
    /// covers the tanks) for 90 s; it prints the missiles fired, the hits, the ones shot down and the
    /// rest (flares, lost lock, missed), at the speeds now and at other speeds (the 11C speeds, the
    /// owner's 10 % slower ground SAMs). Run with MB_BALANCE=1.
    /// </summary>
    public class MissileHitMeasure
    {
        private static readonly (string shooter, string weapon, string target, bool aps)[] Cases =
        {
            ("aa_vehicle", "sam", "attack_jet", false), ("sam_launcher", "sam_long", "attack_jet", false),
            ("missile_battery", "sam_battery", "attack_jet", false), ("long_sam", "sam_48n6", "attack_jet", false),
            ("sam_launcher", "sam_long", "attack_helicopter", false), ("aa_vehicle", "sam", "attack_helicopter", false),
            ("fighter_jet", "air_to_air", "attack_jet", false), ("fighter_jet", "wvr_aam", "attack_helicopter", false),
            ("ifv", "atgm", "main_battle_tank", true), ("attack_helicopter", "hellfire_standoff", "main_battle_tank", true),
            ("ifv", "atgm", "main_battle_tank", false),
        };

        /// <summary>Variants: (name, edits of weapon fields: id, field, value); no edits is the data as it is.</summary>
        private static readonly (string name, (string id, string field, float value)[] edits)[] Variants =
        {
            ("now", Array.Empty<(string, string, float)>()),
            ("sam-10%", new[] { ("sam", "projectileSpeed", 36f), ("sam_long", "projectileSpeed", 41f), ("sam_battery", "projectileSpeed", 41f), ("sam_48n6", "projectileSpeed", 56f) }),
            ("sam-10%+resist", new[] { ("sam", "projectileSpeed", 36f), ("sam_long", "projectileSpeed", 41f), ("sam_battery", "projectileSpeed", 41f), ("sam_48n6", "projectileSpeed", 56f),
                ("sam", "flareResist", 0.5f), ("sam_long", "flareResist", 0.8f), ("sam_battery", "flareResist", 0.85f), ("sam_48n6", "flareResist", 0.85f) }),
            ("11C", new[] { ("air_to_air", "projectileSpeed", 48f), ("wvr_aam", "projectileSpeed", 48f), ("vikhr", "projectileSpeed", 34f), ("atgm_heavy", "projectileSpeed", 24f) }),
        };

        /// <summary>The catalog with some weapon fields changed (a field the weapon's line lacks is added to it).</summary>
        internal static Catalog WithFields(IEnumerable<(string id, string field, float value)> edits)
        {
            var lines = Resources.Load<TextAsset>("Data/balance").text.Replace("\r\n", "\n").Split('\n');
            foreach (var (id, field, value) in edits)
            {
                var index = Array.FindIndex(lines, l => l.Contains("{ \"id\": \"" + id + "\""));
                Assert.GreaterOrEqual(index, 0, "no weapon " + id);
                var line = lines[index];
                var number = value.ToString(CultureInfo.InvariantCulture);
                var pattern = "(\"" + Regex.Escape(field) + "\": )(-?[0-9.]+)";
                lines[index] = Regex.IsMatch(line, pattern) ? Regex.Replace(line, pattern, m => m.Groups[1].Value + number)
                    : line.Substring(0, line.LastIndexOf('}')) + ", \"" + field + "\": " + number + " " + line.Substring(line.LastIndexOf('}'));
            }
            return Catalog.FromJson(string.Join("\n", lines));
        }

        [Test, Explicit("a measurement: run it by name with MB_BALANCE=1"), Category("Balance")]
        public void PrintMissileHitRates()
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("missile hit rates: set MB_BALANCE=1");
            var report = new StringBuilder();
            report.AppendLine("variant\tshooter\tweapon\tspeed\ttarget\taps\tfired\thits\tshot down\tother\thit%");
            foreach (var (name, speeds) in Variants)
            {
                var catalog = speeds.Length == 0 ? GameContent.LoadCatalog() : WithFields(speeds);
                foreach (var c in Cases)
                {
                    if (name != "now" && Array.FindIndex(speeds, e => e.id == c.weapon) < 0) continue;
                    var (fired, hits, down) = Fire(catalog, c.shooter, c.weapon, c.target, c.aps, 7);
                    var other = fired - hits - down;
                    report.AppendLine(string.Join("\t", name, c.shooter, c.weapon, catalog.Weapons[c.weapon].ProjectileSpeed.ToString(CultureInfo.InvariantCulture),
                        c.target, c.aps ? "aps" : "-", fired, hits, down, other, fired > 0 ? (100f * hits / fired).ToString("0") : "-"));
                }
            }
            TestContext.Out.WriteLine(report.ToString());
            Debug.Log("[MissileHitMeasure]\n" + report);
            var dir = Environment.GetEnvironmentVariable("MB_CV_OUT");
            if (!string.IsNullOrEmpty(dir)) System.IO.File.WriteAllText(System.IO.Path.Combine(dir, "missile_hits_" + (Environment.GetEnvironmentVariable("MB_CV_TAG") ?? "now") + ".tsv"), report.ToString());
            Assert.Pass();
        }

        /// <summary>The counter test "SAM beats jets" (3 SAM launchers against 2 attack jets) over four seeds, for each variant.</summary>
        [Test, Explicit("a measurement: run it by name with MB_BALANCE=1"), Category("Balance")]
        public void PrintSamAgainstJets()
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("SAM against jets: set MB_BALANCE=1");
            var report = new StringBuilder();
            foreach (var (name, edits) in Variants)
            {
                if (name == "11C") continue;
                var catalog = edits.Length == 0 ? GameContent.LoadCatalog() : WithFields(edits);
                foreach (var (a, na, b, nb) in new[] { ("sam_launcher", 3, "attack_jet", 2), ("aa_vehicle", 3, "attack_helicopter", 2), ("sam_launcher", 2, "attack_jet", 1) })
                    for (var seed = 1; seed <= 4; seed++)
                    {
                        var winner = CounterTests.Skirmish(a, na, b, nb, out var summary, catalog: catalog, seed: seed);
                        report.AppendLine($"{name,-16} seed {seed}: winner {winner}  {summary}");
                    }
            }
            TestContext.Out.WriteLine(report.ToString());
            Debug.Log("[MissileHitMeasure.Sam]\n" + report);
            var dir = Environment.GetEnvironmentVariable("MB_CV_OUT");
            if (!string.IsNullOrEmpty(dir)) System.IO.File.WriteAllText(System.IO.Path.Combine(dir, "sam_vs_jets_" + (Environment.GetEnvironmentVariable("MB_CV_TAG") ?? "now") + ".txt"), report.ToString());
            Assert.Pass();
        }

        internal static (int fired, int hits, int down) Fire(Catalog catalog, string shooterId, string weaponId, string targetId, bool aps, int seed, float seconds = 90f)
        {
            var world = new SimWorld(catalog, new MapDefinition("range", 300f,
                new[] { new TeamStart(0, new Vector2(0f, -130f)), new TeamStart(1, new Vector2(0f, 130f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed: seed);
            world.RevealAll = true;
            var shooter = world.SpawnVehicle(shooterId, 0, new Vector2(0f, -20f), 0f);
            var target = world.SpawnVehicle(targetId, 1, new Vector2(0f, 20f), MathF.PI);
            world.MakeSparring(target);
            target.HoldFire = true;
            if (aps)
            {
                var guard = world.SpawnVehicle("iron_beam", 1, new Vector2(6f, 24f), MathF.PI);
                world.MakeSparring(guard);
                guard.HoldFire = true;
            }
            // Ground shooters hold their ground; aircraft attack-move at the target.
            if (shooter.Flying) world.Submit(new Sim.Commands.Command(Sim.Commands.CommandType.AttackMove, 0, new[] { shooter.Id }, target.Position));
            int fired = 0, hits = 0, down = 0;
            for (var t = 0f; t < seconds; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                foreach (var e in world.Events)
                {
                    if (e.DefId != weaponId) continue;
                    if (e.Kind == SimEventKind.WeaponFired && e.Entity == shooter.Id) fired++;
                    else if (e.Kind == SimEventKind.ProjectileImpact && e.Team == 0 && e.Entity.IsValid) hits++;
                    else if (e.Kind == SimEventKind.Intercepted) down++;
                }
                world.ClearEvents();
                shooter.Hp = shooter.MaxHp;
            }
            return (fired, hits, down);
        }
    }
}
