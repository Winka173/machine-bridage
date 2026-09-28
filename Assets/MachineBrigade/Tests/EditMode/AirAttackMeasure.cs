using System.Collections.Generic;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Test feedback 2 (12F): measurements, not checks. The first prints what every aircraft's
    /// mounts deliver against a target that never fires back or dies, with the aircraft starting
    /// out of reach (so the approach, the attack hold and the loop are all in it); the second plays
    /// short real fights (fighters on helicopters and jets, attack aircraft on a tank column, with
    /// and without anti-air) and prints how long they took and what was left.
    /// </summary>
    public class AirAttackMeasure
    {
        private static readonly (string shooter, string target, float distance)[] Ranges =
        {
            ("attack_jet", "main_battle_tank", 70f), ("tank_buster", "main_battle_tank", 70f), ("fighter_jet", "attack_helicopter", 70f),
            ("fighter_jet", "attack_jet", 70f), ("fighter_jet", "fighter_jet", 70f), ("strike_drone", "main_battle_tank", 70f),
            ("recon_drone", "main_battle_tank", 70f), ("heavy_bomber", "main_battle_tank", 70f), ("stealth_bomber", "main_battle_tank", 70f),
            ("sky_gunship", "ifv", 60f), ("attack_helicopter", "ifv", 50f), ("elite_attack_helicopter", "ifv", 50f),
            ("gunship_heli", "ifv", 50f), ("heavy_attack_heli", "ifv", 70f), ("scout_heli", "armored_car", 45f),
        };

        private static SimWorld Field(int seed) =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("range", 260f,
                new[] { new TeamStart(0, new Vector2(0f, -110f)), new TeamStart(1, new Vector2(0f, 110f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed: seed);

        [Test, Explicit("a measurement: run it by name")]
        public void PrintWhatEachAircraftDelivers()
        {
            var report = new StringBuilder();
            foreach (var (shooterId, targetId, distance) in Ranges)
            {
                var world = Field(11);
                var shooter = world.SpawnVehicle(shooterId, 0, new Vector2(0f, -distance * 0.5f), 0f);
                var target = world.SpawnVehicle(targetId, 1, new Vector2(0f, distance * 0.5f), System.MathF.PI);
                // A jet flies on (it circles its post): it moves but cannot be destroyed; anything else stands still.
                if (target.Def.FixedWing) world.MakeSparring(target);
                else world.MakeDummy(target);
                target.HoldFire = true;
                // Sent at it, as a player's attack-move would: the approach, the attack and the loops are all measured.
                world.Submit(new Command(CommandType.AttackMove, 0, new[] { shooter.Id }, target.Position));
                var mounts = shooter.Def.Mounts.Count;
                var dealt = new float[mounts];
                var rounds = new int[mounts];
                var streamStart = new double[mounts];
                var lastAt = new double[mounts];
                var longest = new double[mounts];
                for (var i = 0; i < mounts; i++) lastAt[i] = streamStart[i] = double.NegativeInfinity;
                DamageSystem.DamageLog = (by, victim, amount, kind, weapon) =>
                {
                    if (by != shooter || weapon == null) return;
                    for (var i = 0; i < mounts; i++)
                        if (shooter.Arms[i] == weapon || shooter.Def.Mounts[i].Weapon == weapon)
                        {
                            dealt[i] += amount;
                            return;
                        }
                };
                var slow = 0;
                var steps = 0;
                try
                {
                    for (var t = 0f; t < 60f; t += TestWorlds.Step)
                    {
                        world.Step(TestWorlds.Step);
                        steps++;
                        if (shooter.Speed < shooter.Def.Speed * 0.5f) slow++;
                        foreach (var e in world.Events)
                        {
                            if (e.Kind != SimEventKind.WeaponFired || e.Entity != shooter.Id) continue;
                            var m = e.Mount;
                            rounds[m]++;
                            if (world.Time - lastAt[m] > 0.36) streamStart[m] = world.Time;
                            lastAt[m] = world.Time;
                            longest[m] = System.Math.Max(longest[m], lastAt[m] - streamStart[m]);
                        }
                        world.ClearEvents();
                        target.Hp = target.MaxHp;
                    }
                }
                finally
                {
                    DamageSystem.DamageLog = null;
                }
                for (var i = 0; i < mounts; i++)
                    report.AppendLine($"{shooterId,-24} vs {targetId,-18} m{i} {shooter.Def.Mounts[i].Weapon.Id,-20} dmg {dealt[i],8:0} dps {dealt[i] / 60f,6:0.0} rounds {rounds[i],5} longest {longest[i],4:0.00}s");
                report.AppendLine($"{shooterId,-24} vs {targetId,-18} ALL dps {dealt.Sum() / 60f,6:0.0}  slow {100f * slow / steps,3:0}% of the time");
            }
            Print("AirAttackMeasure.Dps", report.ToString());
            Assert.Pass();
        }

        private static readonly (string shooter, string target)[] Timelines =
        {
            ("attack_jet", "main_battle_tank"), ("tank_buster", "main_battle_tank"), ("fighter_jet", "attack_helicopter"), ("fighter_jet", "attack_jet"),
            ("strike_drone", "main_battle_tank"),
        };

        /// <summary>A quarter-second log of one aircraft's attack: speed, distance, hold, loop and the rounds each mount fired.</summary>
        [Test, Explicit("a measurement: run it by name")]
        public void PrintAttackTimelines()
        {
            var report = new StringBuilder();
            foreach (var (shooterId, targetId) in Timelines)
            {
                var world = Field(11);
                var shooter = world.SpawnVehicle(shooterId, 0, new Vector2(0f, -35f), 0f);
                var target = world.SpawnVehicle(targetId, 1, new Vector2(0f, 35f), System.MathF.PI);
                if (target.Def.FixedWing) world.MakeSparring(target);
                else world.MakeDummy(target);
                target.HoldFire = true;
                world.Submit(new Command(CommandType.AttackMove, 0, new[] { shooter.Id }, target.Position));
                report.AppendLine($"--- {shooterId} vs {targetId}");
                var fired = new int[shooter.Def.Mounts.Count];
                for (var t = 0f; t < 30f; t += TestWorlds.Step)
                {
                    world.Step(TestWorlds.Step);
                    foreach (var e in world.Events)
                        if (e.Kind == SimEventKind.WeaponFired && e.Entity == shooter.Id) fired[e.Mount]++;
                    world.ClearEvents();
                    target.Hp = target.MaxHp;
                    if (System.Math.Abs(world.Time * 4.0 - System.Math.Round(world.Time * 4.0)) > 0.01) continue;
                    var off = System.MathF.Abs(Sim.Core.SimMath.WrapAngle(Sim.Core.SimMath.HeadingOf(target.Position - shooter.Position) - shooter.Heading)) * 57.3f;
                    report.AppendLine($"t {world.Time,5:0.00} v {shooter.Speed,4:0.0} d {Vector2.Distance(shooter.Position, target.Position),5:0.0} off {off,3:0} {(shooter.InAttackHold ? "HOLD" : shooter.Breaking ? "brk " : "    ")} fired {string.Join(" ", fired)}");
                    System.Array.Clear(fired, 0, fired.Length);
                }
            }
            Print("AirAttackMeasure.Timelines", report.ToString());
            Assert.Pass();
        }

        private static readonly (string name, string[] attackers, string[] defenders)[] Fights =
        {
            ("fighters vs attack helicopters", new[] { "fighter_jet", "fighter_jet" }, new[] { "attack_helicopter", "attack_helicopter" }),
            ("fighters vs attack jets", new[] { "fighter_jet", "fighter_jet" }, new[] { "attack_jet", "attack_jet" }),
            ("fighters vs fighters", new[] { "fighter_jet", "fighter_jet" }, new[] { "fighter_jet", "fighter_jet" }),
            ("attack jets vs tank column", new[] { "attack_jet", "attack_jet" }, new[] { "main_battle_tank", "main_battle_tank", "main_battle_tank", "ifv" }),
            ("attack jets vs column + AA", new[] { "attack_jet", "attack_jet" }, new[] { "main_battle_tank", "main_battle_tank", "main_battle_tank", "aa_vehicle" }),
            ("A-10 vs tank column", new[] { "tank_buster" }, new[] { "main_battle_tank", "main_battle_tank", "main_battle_tank", "ifv" }),
            ("A-10 vs column + AA", new[] { "tank_buster" }, new[] { "main_battle_tank", "main_battle_tank", "main_battle_tank", "aa_vehicle" }),
            ("A-10 vs column + 2 AA", new[] { "tank_buster" }, new[] { "main_battle_tank", "main_battle_tank", "aa_vehicle", "aa_vehicle" }),
            ("attack helis vs IFV column", new[] { "attack_helicopter", "attack_helicopter" }, new[] { "ifv", "ifv", "ifv" }),
            ("attack helis vs IFVs + AA", new[] { "attack_helicopter", "attack_helicopter" }, new[] { "ifv", "ifv", "aa_vehicle" }),
            ("gunship helis vs tank column", new[] { "gunship_heli", "gunship_heli" }, new[] { "main_battle_tank", "main_battle_tank", "main_battle_tank" }),
            ("strike drones vs tank column", new[] { "strike_drone", "strike_drone" }, new[] { "main_battle_tank", "main_battle_tank", "main_battle_tank" }),
            ("AC-130 vs IFV column + AA", new[] { "sky_gunship" }, new[] { "ifv", "ifv", "ifv", "aa_vehicle" }),
        };

        [Test, Explicit("a measurement: run it by name")]
        public void PrintRealFights()
        {
            var report = new StringBuilder();
            foreach (var (name, attackers, defenders) in Fights)
                foreach (var seed in new[] { 1, 2 })
                    report.AppendLine(Fight(name, attackers, defenders, seed));
            Print("AirAttackMeasure.Fights", report.ToString());
            Assert.Pass();
        }

        private static string Fight(string name, string[] attackers, string[] defenders, int seed)
        {
            var world = Field(seed);
            var ours = new List<Vehicle>();
            var theirs = new List<Vehicle>();
            for (var i = 0; i < attackers.Length; i++)
                ours.Add(world.SpawnVehicle(attackers[i], 0, new Vector2(-8f + i * 16f, -90f), 0f));
            for (var i = 0; i < defenders.Length; i++)
                theirs.Add(world.SpawnVehicle(defenders[i], 1, new Vector2(-15f + i * 10f, 30f + (i % 2) * 6f), System.MathF.PI));
            var centre = new Vector2(0f, 33f);
            world.Submit(new Command(CommandType.AttackMove, 0, ours.Select(v => v.Id).ToArray(), centre));
            var dealt = 0f;
            var taken = 0f;
            DamageSystem.DamageLog = (by, victim, amount, kind, weapon) =>
            {
                if (by == null) return;
                if (by.Team == 0 && victim.Team == 1) dealt += amount;
                else if (by.Team == 1 && victim.Team == 0) taken += amount;
            };
            var end = 120.0;
            try
            {
                for (var t = 0f; t < 120f; t += TestWorlds.Step)
                {
                    world.Step(TestWorlds.Step);
                    world.ClearEvents();
                    if (theirs.All(v => !v.IsAlive) || ours.All(v => !v.IsAlive))
                    {
                        end = world.Time;
                        break;
                    }
                }
            }
            finally
            {
                DamageSystem.DamageLog = null;
            }
            string Left(List<Vehicle> side) => $"{side.Count(v => v.IsAlive)}/{side.Count} ({100f * side.Sum(v => v.IsAlive ? v.Hp : 0f) / side.Sum(v => v.MaxHp),3:0}% hp)";
            return $"{name,-32} seed {seed}: {(theirs.All(v => !v.IsAlive) ? "won" : ours.All(v => !v.IsAlive) ? "lost" : "open"),-4} at {end,5:0.0}s  air left {Left(ours)}  ground/enemy left {Left(theirs)}  dealt {dealt,6:0} taken {taken,6:0}";
        }

        private static void Print(string title, string text)
        {
            TestContext.Out.WriteLine(text);
            UnityEngine.Debug.Log($"[{title}]\n" + text);
        }
    }
}
