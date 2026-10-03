using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Measurements behind the roster's prices (prompt 2 E): how many vehicles a railgun slug goes
    /// through in real battles, what the Iron Beam saves a group, and a stream of car bombs at a
    /// base. The battle ones are long: run by hand with MB_BALANCE=1.
    /// </summary>
    public class RosterBalanceTests
    {
        private static void Gate()
        {
            if (Environment.GetEnvironmentVariable("MB_BALANCE") != "1") Assert.Ignore("balance measurement: set MB_BALANCE=1 to run it");
        }

        [Test, Category("Balance")]
        public void RailgunPierce()
        {
            Gate();
            var shots = 0;
            var direct = 0;
            var pierced = 0;
            foreach (var map in new[] { "ashfield_conquest", "greenvale_conquest", "dunebreak_conquest" })
                for (var seed = 1; seed <= 5; seed++)
                {
                    var world = new SimWorld(GameContent.LoadCatalog(), GameContent.LoadMap(map), seed: seed);
                    var deck = new[] { "main_battle_tank", "heavy_tank", "ifv", "armored_car", "railgun_truck", "mlrs", "aa_vehicle", "tank_destroyer" };
                    var mode = new ConquestMode(new ConquestRules
                    {
                        PlayerVehicles = deck, EnemyVehicles = deck, PlayerSupports = Array.Empty<string>(), EnemySupports = Array.Empty<string>(),
                    });
                    mode.Setup(world);
                    var ais = new[] { new ConquestAi(mode, 0, 1, AiDifficulty.Hard, seed), new ConquestAi(mode, 1, 0, AiDifficulty.Hard, seed + 3) };
                    for (var i = 0; i < 8 * 60 * 20 && !world.IsOver; i++)
                    {
                        mode.Tick(world, TestWorlds.Step);
                        foreach (var ai in ais) ai.Tick(world, TestWorlds.Step);
                        world.Step(TestWorlds.Step);
                        foreach (var e in world.Events)
                        {
                            if (e.DefId != "railgun") continue;
                            if (e.Kind == SimEventKind.WeaponFired) shots++;
                            if (e.Kind == SimEventKind.ProjectileImpact && e.Entity.IsValid) direct++;
                        }
                        world.ClearEvents();
                    }
                    pierced += world.Damage.PierceVictims;
                }
            var average = shots > 0 ? (direct + pierced) / (float)shots : 0f;
            Debug.Log($"RAILGUN shots {shots}, direct hits {direct}, pierced {pierced}: {average:0.00} vehicles a shot");
            Assert.Greater(shots, 10, "railguns fired");
        }

        /// <summary>A tank group under missiles, drones and rockets, with and without an Iron Beam among it (5 seeds).</summary>
        [Test, Category("Balance")]
        public void IronBeamValue()
        {
            Gate();
            float Lost(bool beam, int seed, out int intercepts)
            {
                var world = new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 240f,
                    new[] { new TeamStart(0, new Vector2(-100f, -100f)), new TeamStart(1, new Vector2(100f, 100f)) },
                    new List<PropPlacement>(), new List<UnitPlacement>()), seed: seed);
                var group = new List<Vehicle>();
                for (var i = 0; i < 4; i++) group.Add(world.SpawnVehicle("main_battle_tank", 1, new Vector2(-9f + i * 6f, 0f), 3.14f));
                var guard = world.SpawnVehicle(beam ? "iron_beam" : "aa_vehicle", 1, new Vector2(0f, 6f), 3.14f);
                if (!beam) world.SpawnVehicle("aa_vehicle", 1, new Vector2(6f, 6f), 3.14f);
                var attackers = new List<Vehicle>
                {
                    world.SpawnVehicle("ifv", 0, new Vector2(-10f, -36f), 0f),
                    world.SpawnVehicle("ifv", 0, new Vector2(10f, -36f), 0f),
                    world.SpawnVehicle("fpv_carrier", 0, new Vector2(0f, -70f), 0f),
                    world.SpawnVehicle("mlrs", 0, new Vector2(-20f, -90f), 0f),
                    world.SpawnVehicle("attack_helicopter", 0, new Vector2(20f, -60f), 0f),
                };
                var spotter = world.SpawnVehicle("recon_drone", 0, new Vector2(0f, -20f), 0f);
                foreach (var v in group.Append(guard)) world.Submit(new Command(CommandType.Stop, 1, new[] { v.Id }));
                foreach (var a in attackers) world.Submit(new Command(CommandType.Attack, 0, new[] { a.Id }, target: group[0].Id));
                var count = 0;
                var start = group.Sum(v => v.Hp);
                for (var t = 0f; t < 30f; t += TestWorlds.Step)
                {
                    spotter.Hp = spotter.MaxHp;
                    foreach (var a in attackers) a.Hp = a.MaxHp;
                    world.Step(TestWorlds.Step);
                    foreach (var e in world.Events)
                        if (e.Kind == SimEventKind.Intercepted && e.Entity == guard.Id) count++;
                    world.ClearEvents();
                    foreach (var a in attackers)
                        if (a.Order.Kind == OrderKind.Idle)
                        {
                            var next = group.FirstOrDefault(v => v.IsAlive);
                            if (next != null) world.Submit(new Command(CommandType.Attack, 0, new[] { a.Id }, target: next.Id));
                        }
                }
                intercepts = count;
                return start - group.Sum(v => Mathf.Max(0f, v.Hp));
            }
            var withBeam = 0f;
            var withAa = 0f;
            var intercepted = 0;
            for (var seed = 1; seed <= 5; seed++)
            {
                withBeam += Lost(true, seed, out var n);
                intercepted += n;
                withAa += Lost(false, seed, out _);
            }
            Debug.Log($"IRONBEAM tank health lost over 30 s: {withBeam / 5f:0} with the beam (9 CP), {withAa / 5f:0} with two AA vehicles (8 CP); " +
                      $"{intercepted / 5f * 2f:0.0} intercepts a minute");
            Assert.Greater(intercepted, 0);
        }

        /// <summary>A stream of car bombs at a base's HQ does not bring it down: half damage on structures, and towers stop most of them.</summary>
        [Test]
        public void ACarBombStreamDoesNotBreakABase()
        {
            var world = new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 200f,
                new[] { new TeamStart(0, new Vector2(-80f, -80f)), new TeamStart(1, new Vector2(80f, 80f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed: 4);
            var hq = world.SpawnVehicle("headquarters", 1, new Vector2(40f, 40f), 3.93f);
            world.SpawnVehicle("mg_bunker", 1, new Vector2(28f, 32f), 3.93f);
            world.SpawnVehicle("gun_turret", 1, new Vector2(34f, 24f), 3.93f);
            world.SpawnVehicle("guard_tower", 1, new Vector2(22f, 40f), 3.93f);
            var bombs = new List<Vehicle>();
            // Twelve car bombs (36 CP) in waves of four, every 8 s, straight at the HQ.
            for (var t = 0f; t < 60f; t += TestWorlds.Step)
            {
                if (bombs.Count < 12 && Mathf.Abs(t % 8f) < TestWorlds.Step)
                    for (var k = 0; k < 4; k++)
                    {
                        var b = world.SpawnVehicle("vbied", 0, new Vector2(-30f + k * 5f, -30f), 0.78f);
                        world.Submit(new Command(CommandType.Attack, 0, new[] { b.Id }, target: hq.Id));
                        bombs.Add(b);
                    }
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
            Debug.Log($"VBIED stream: HQ at {hq.Hp / hq.MaxHp:P0} after {bombs.Count} car bombs");
            Assert.IsTrue(hq.IsAlive, "the HQ stands");
            Assert.Greater(hq.Hp / hq.MaxHp, 0.5f, "with more than half its health");
        }
    }
}
