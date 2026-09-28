using System.Collections.Generic;
using System.Linq;
using System.Text;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Test feedback 11C: a measurement, not a check. Each shooter fights a dummy (it never fires
    /// back and never dies) for 60 s; per mount it prints the damage dealt, the damage a second,
    /// the rounds fired and the longest unbroken stream of fire. Run before and after a change to
    /// the weapon data to compare what the weapons really deliver (strafing runs included).
    /// </summary>
    public class FireRhythmMeasure
    {
        private static readonly (string shooter, string target, float distance)[] Cases =
        {
            ("attack_jet", "main_battle_tank", 45f), ("tank_buster", "main_battle_tank", 45f), ("fighter_jet", "attack_helicopter", 45f),
            ("fighter_jet", "ifv", 45f), ("gunship_heli", "ifv", 22f), ("attack_helicopter", "ifv", 22f), ("heavy_attack_heli", "ifv", 22f),
            ("scout_heli", "armored_car", 18f), ("sky_gunship", "ifv", 40f), ("armored_car", "armored_car", 18f), ("armored_car", "attack_helicopter", 14f),
            ("ifv", "ifv", 18f), ("ifv", "attack_helicopter", 14f), ("bmpt", "ifv", 18f), ("main_battle_tank", "ifv", 18f), ("scout_jeep", "armored_car", 16f),
            ("heavy_aa", "attack_helicopter", 25f), ("aa_vehicle", "attack_helicopter", 25f), ("zu23_technical", "attack_helicopter", 20f),
            // Test feedback 2 (12D): the anti-aircraft guns, towers, bunkers and boss guns on streams.
            ("elite_aa", "attack_helicopter", 25f), ("aa_turret", "attack_helicopter", 25f), ("aa_turret.flak", "attack_helicopter", 25f),
            ("c_ram", "attack_helicopter", 20f), ("c_ram.hunter", "attack_helicopter", 30f), ("headquarters", "attack_helicopter", 22f),
            ("landing_hovercraft", "attack_helicopter", 20f), ("landing_hovercraft", "ifv", 20f), ("mega_gunship", "ifv", 22f),
            ("mg_bunker", "armored_car", 18f), ("mg_bunker.twin", "armored_car", 18f), ("bulwark_post", "armored_car", 18f),
            ("gun_turret", "armored_car", 16f), ("guard_tower", "armored_car", 18f), ("guard_tower.nest", "armored_car", 18f),
            ("fortress_bastion", "attack_helicopter", 20f), ("behemoth", "attack_helicopter", 25f), ("heavy_bomber", "attack_helicopter", 20f),
            ("main_battle_tank", "attack_helicopter", 14f), ("scout_jeep", "attack_helicopter", 14f), ("heavy_attack_heli", "armored_car", 12f), ("command_airship", "attack_helicopter", 30f), ("supreme_command", "armored_car", 18f), ("armored_train", "attack_helicopter", 25f),
        };

        [Test, Explicit("a measurement: run it by name")]
        public void PrintWhatEachMountDelivers()
        {
            var catalog = GameContent.LoadCatalog();
            var report = new StringBuilder();
            foreach (var (shooterId, targetId, distance) in Cases)
            {
                var world = new SimWorld(catalog, new MapDefinition("range", 260f,
                    new[] { new TeamStart(0, new Vector2(0f, -110f)), new TeamStart(1, new Vector2(0f, 110f)) },
                    new List<PropPlacement>(), new List<UnitPlacement>()), seed: 11);
                var shooter = world.SpawnVehicle(shooterId, 0, new Vector2(0f, -distance * 0.5f), 0f);
                var target = world.SpawnVehicle(targetId, 1, new Vector2(0f, distance * 0.5f), System.MathF.PI);
                world.MakeDummy(target);
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
                try
                {
                    for (var t = 0f; t < 60f; t += TestWorlds.Step)
                    {
                        world.Step(TestWorlds.Step);
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
                report.AppendLine($"{shooterId,-18} vs {targetId,-18} ALL dps {dealt.Sum() / 60f,6:0.0}");
                for (var i = 0; i < mounts; i++)
                    report.AppendLine($"{shooterId,-18} vs {targetId,-18} m{i} {shooter.Def.Mounts[i].Weapon.Id,-20} dmg {dealt[i],8:0} dps {dealt[i] / 60f,6:0.0} rounds {rounds[i],5} longest {longest[i],4:0.00}s");
            }
            TestContext.Out.WriteLine(report.ToString());
            UnityEngine.Debug.Log("[FireRhythmMeasure]\n" + report);
            System.IO.File.WriteAllText(System.IO.Path.Combine(System.IO.Path.GetTempPath(), "mb_fire_rhythm.txt"), report.ToString());
            Assert.Pass();
        }
    }
}
