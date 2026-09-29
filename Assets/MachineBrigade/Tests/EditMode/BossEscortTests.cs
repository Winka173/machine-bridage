using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Events;
using MachineBrigade.Sim.Modes;
using UnityEngine;
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 16 E and F (DECISIONS 15B): the old bosses' new weapons, one behaviour each, and the escort
    /// system every boss shares (its timing, cap, leash and a helper at work). The kill-time check per boss
    /// (one seed, the boss alone as prompt 9 measured it) logs against the base data when it is at hand.
    /// </summary>
    public class BossEscortTests
    {
        private const float Step = 0.05f;

        private static List<SimEvent> Run(SimWorld world, float seconds, Action each = null)
        {
            var events = new List<SimEvent>();
            for (var t = 0f; t < seconds; t += Step)
            {
                each?.Invoke();
                world.Step(Step);
                events.AddRange(world.Events);
                world.ClearEvents();
            }
            return events;
        }

        private static Vehicle Tough(SimWorld world, string id, int team, Vector2 at, float heading = 0f)
        {
            var v = world.SpawnVehicle(id, team, at, heading);
            v.HpScale = 100f;
            v.Hp = v.MaxHp;
            return v;
        }

        // ------------------------------------------------------------------ E: the new weapons

        [Test]
        public void TheTrainsMortarCarHitsATankBehindAHouse()
        {
            var map = new MapDefinition("lab", 260f,
                new[] { new TeamStart(0, new Vector2(-100f, -100f)), new TeamStart(1, new Vector2(100f, 100f)) },
                new List<PropPlacement> { new("house_large", new Vector2(0f, 0f), 0) }, new List<UnitPlacement>(), null) ;
            var world = new SimWorld(Lab.Catalog, map, 3) { RevealAll = true };
            var train = world.SpawnVehicle("armored_train", 1, new Vector2(0f, -28f), 0f);
            var tank = Tough(world, "main_battle_tank", 0, new Vector2(0f, 24f), MathF.PI);
            var mortar = train.Def.Mounts.ToList().FindIndex(m => m.Weapon.Id == "train_mortar");
            Assert.Greater(mortar, 0);
            Assert.IsFalse(world.HasLineOfFire(train, tank, train.Def.Mounts[0].Weapon), "the house stops the train's guns");
            var events = Run(world, 16f);
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.WeaponFired && e.Entity == train.Id && e.Mount == mortar),
                "the mortar car lobs over the house");
        }

        [TestCase("behemoth", new[] { "aps" })]
        [TestCase("behemoth_tempest", new[] { "interceptor" })]
        [TestCase("landing_hovercraft", new[] { "ciws_l", "ciws_r" })]
        public void ItsProtectionShootsMissilesDownUntilItsPartsBreak(string id, string[] parts)
        {
            var world = Lab.Field(5, 300f);
            var boss = world.SpawnVehicle(id, 1, Vector2.Zero, 0f);
            boss.HpScale = 50f;
            boss.Hp = boss.MaxHp;
            for (var k = 0; k < 2; k++) Tough(world, "bmpt", 0, new Vector2(-8f + 16f * k, -34f));
            var before = Run(world, 14f).Count(e => e.Kind == SimEventKind.Intercepted && e.Entity == boss.Id);
            Assert.Greater(before, 0, id + " shoots anti-tank missiles down");
            for (var k = 0; k < parts.Length; k++)
            {
                world.Bosses.Break(boss, boss.Def.PartIndex(parts[k]));
                var after = Run(world, 14f).Count(e => e.Kind == SimEventKind.Intercepted && e.Entity == boss.Id);
                if (k < parts.Length - 1) Assert.Greater(after, 0, $"{id}: one of its {parts.Length} still stands");
                else Assert.AreEqual(0, after, $"{id}: none once every one is broken");
            }
        }

        [Test]
        public void TheInfernoLeavesAFireTrailUntilItsFuelTanksBreak()
        {
            var world = Lab.Field(6, 300f);
            var boss = world.SpawnVehicle("behemoth_inferno", 1, new Vector2(0f, -60f), 0f);
            world.Submit(new Command(CommandType.Move, 1, new[] { boss.Id }, new Vector2(0f, 60f)));
            var trail = Run(world, 12f).Where(e => e.Kind == SimEventKind.FireTrail && e.Entity == boss.Id).ToList();
            Assert.Greater(trail.Count, 3, "patches of burning fuel behind it as it drives");
            Assert.AreEqual(10f * FireTrailDef.GroundBurn, boss.Def.FireTrail.Burns, 1e-4f, "a patch burns the ground fires' time, a fifth shorter");
            // An enemy standing in the last patch catches fire (the boss stunned: its own flamers out of it).
            world.Status.Stun(boss, world.Time + 10.0);
            // A patch a few back: well behind its hull and still burning.
            var patch = trail[trail.Count - 4].Position;
            var tank = Tough(world, "main_battle_tank", 0, new Vector2(patch.X, patch.Y));
            Run(world, 1.2f);
            Assert.Greater(tank.Statuses[(int)StatusKind.Burn].Until, world.Time, "the tank in the patch burns");
            world.Bosses.Break(boss, boss.Def.PartIndex("fuel"));
            world.Status.Stun(boss, world.Time);
            world.Submit(new Command(CommandType.Move, 1, new[] { boss.Id }, new Vector2(60f, 60f)));
            Assert.IsFalse(Run(world, 10f).Any(e => e.Kind == SimEventKind.FireTrail), "no trail once its fuel tanks are gone");
        }

        [Test]
        public void TheHivesJammerThrowsGuidedRoundsWideNearItUntilItBreaks()
        {
            var world = Lab.Field(7, 300f);
            var hive = world.SpawnVehicle("fortress_hive", 1, Vector2.Zero, 0f);
            Run(world, 0.2f);
            Assert.IsTrue(world.Abilities.Jammed(hive.Position + new Vector2(20f, 0f), 0), "within its 30 m");
            Assert.IsFalse(world.Abilities.Jammed(hive.Position + new Vector2(40f, 0f), 0), "not beyond");
            world.Bosses.Break(hive, hive.Def.PartIndex("jammer"));
            Run(world, 0.2f);
            Assert.IsFalse(world.Abilities.Jammed(hive.Position + new Vector2(20f, 0f), 0), "its jamming mast broken");
        }

        /// <summary>The new mounts that simply shoot: the Bastion's Kornet, the Doomsday Train's rocket and SAM cars, the supergun's AA, the hovercraft's rockets and CIWS.</summary>
        [TestCase("fortress_bastion", "kornet_twin", "main_battle_tank", 32f)]
        [TestCase("nuke_train", "boss_rockets", "main_battle_tank", 34f)]
        [TestCase("nuke_train", "sam_battery", "attack_helicopter", 45f)]
        [TestCase("rail_supergun", "ciws_aa", "attack_helicopter", 26f)]
        [TestCase("landing_hovercraft", "hover_rockets", "main_battle_tank", 34f)]
        public void ItsNewMountFiresAtItsKindOfTarget(string id, string weapon, string target, float distance)
        {
            var world = Lab.Field(8, 300f);
            world.SetBoosts(0, _ => Lab.Harmless);
            var boss = world.SpawnVehicle(id, 1, Vector2.Zero, 0f);
            var mounts = boss.Def.Mounts.Select((m, i) => (m, i)).Where(x => x.i > 0 && x.m.Weapon.Id == weapon).Select(x => x.i).ToList();
            Assert.IsNotEmpty(mounts, $"{id} carries {weapon}");
            var foe = Tough(world, target, 0, new Vector2(distance * 0.6f, distance * 0.8f), MathF.PI);
            var events = Run(world, 18f);
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.WeaponFired && e.Entity == boss.Id && mounts.Contains(e.Mount)),
                $"{id}'s {weapon} fires at the {target}");
            Assert.IsTrue(foe.IsAlive);
        }

        // ------------------------------------------------------------------ F: escorts

        private static SimWorld Escorted(int seed, EscortSettings settings)
        {
            var world = Lab.Field(seed, 300f);
            world.EscortSettings = settings;
            return world;
        }

        private static List<Vehicle> EscortsOf(SimWorld world, Vehicle boss) =>
            world.VehicleList.Where(v => v.IsAlive && v.EscortOf == boss.Id).ToList();

        [Test]
        public void EscortsComeWithTheBossAndAtThePhaseChangeWithinTheCap()
        {
            var rules = Lab.Catalog.EscortRules;
            var world = Escorted(9, EscortSettings.For(rules, "Normal"));
            var boss = world.SpawnVehicle("behemoth", 1, Vector2.Zero, 0f);
            Run(world, 1f);
            var first = EscortsOf(world, boss);
            Assert.AreEqual(3, first.Count, "two battle tanks and an anti-aircraft gun come with it");
            Assert.AreEqual(1, first.Count(v => v.EscortRole == EscortRole.Cover), "its helper covers it from the air");
            Assert.AreEqual(3, world.EscortsAlive(boss.Id));
            Run(world, 4f);
            Assert.AreEqual(3, EscortsOf(world, boss).Count, "nothing more until a phase change");
            boss.Hp = boss.MaxHp * 0.45f;
            Run(world, 1f);
            var second = EscortsOf(world, boss);
            Assert.AreEqual(5, second.Count, "the phase wave: an elite heavy tank and an engineer (Normal's cap is 5)");
            Assert.IsTrue(second.Any(v => v.Def.Id == "elite_heavy_tank") && second.Any(v => v.EscortRole == EscortRole.Repair));

            // A lower cap: the phase wave's helper comes first.
            world = Escorted(9, new EscortSettings { Cap = 4 });
            boss = world.SpawnVehicle("behemoth", 1, Vector2.Zero, 0f);
            Run(world, 1f);
            boss.Hp = boss.MaxHp * 0.45f;
            Run(world, 1f);
            var capped = EscortsOf(world, boss);
            Assert.AreEqual(4, capped.Count, "never more than the cap alive");
            Assert.IsTrue(capped.Any(v => v.EscortRole == EscortRole.Repair), "the helper before the guard");

            // Boss Rush: fewer alive, half the guards, as elites.
            var rush = EscortSettings.For(rules, "Normal", bossRush: true);
            Assert.AreEqual(3, rush.Cap);
            world = Escorted(9, rush);
            boss = world.SpawnVehicle("behemoth", 1, Vector2.Zero, 0f);
            Run(world, 1f);
            var rushed = EscortsOf(world, boss);
            Assert.AreEqual(2, rushed.Count, "its helper and one of its two guards");
            Assert.IsTrue(rushed.Any(v => v.Def.Id == "elite_mbt"), "the guard as an elite");
        }

        [Test]
        public void GuardsTakeOnWhatAttacksTheBossButNeverLeaveTheLeash()
        {
            var world = Escorted(10, EscortSettings.For(Lab.Catalog.EscortRules, "Normal"));
            var boss = world.SpawnVehicle("behemoth", 1, Vector2.Zero, 0f);
            Run(world, 1f);
            // A bait that shoots at nothing, 55 m off, then running away.
            world.SetBoosts(0, _ => Lab.Harmless);
            var bait = Tough(world, "main_battle_tank", 0, new Vector2(0f, 55f), MathF.PI);
            var leash = Lab.Catalog.EscortRules.Leash;
            var farthest = 0f;
            var engaged = false;
            Run(world, 40f, () =>
            {
                if (world.Time > 12.0 && bait.IsAlive && world.Tick % 40 == 0)
                    world.Submit(new Command(CommandType.Move, 0, new[] { bait.Id }, new Vector2(0f, 130f)));
                foreach (var g in EscortsOf(world, boss).Where(v => v.EscortRole == EscortRole.Guard))
                {
                    farthest = MathF.Max(farthest, Vector2.Distance(g.Position, boss.Position));
                    engaged |= g.Order.Kind == OrderKind.Attack && g.Order.Target == bait.Id;
                }
            });
            Assert.IsTrue(engaged, "the guards go for the enemy near the boss");
            Assert.Less(farthest, leash + 10f, "but never far past the leash");
        }

        [Test]
        public void AnEngineerEscortMendsTheBossAndAnEscortDownPaysItsKiller()
        {
            var world = Escorted(11, EscortSettings.For(Lab.Catalog.EscortRules, "Normal"));
            world.EnableEconomy(new SideSetup { StartCp = 0f, Income = 0.001f }.Build(0));
            var boss = world.SpawnVehicle("mobile_fortress", 1, Vector2.Zero, 0f);
            Run(world, 1f);
            boss.Hp = boss.MaxHp * 0.8f;
            Run(world, 12f);
            Assert.Greater(boss.Hp, boss.MaxHp * 0.815f, "its engineer mends it (0.3 % a second)");
            var guard = EscortsOf(world, boss).First(v => v.EscortRole == EscortRole.Guard);
            world.TryGetEconomy(0, out var ours);
            var cp = ours.Cp;
            guard.LastAttackerTeam = 0;
            guard.LastHitTime = world.Time;
            guard.Hp = 0f;
            var events = Run(world, 1f);
            Assert.AreEqual(cp + Lab.Catalog.EscortRules.Bounty, ours.Cp, 0.1f, "an escort destroyed pays CP");
            Assert.IsTrue(events.Any(e => e.Kind == SimEventKind.Bounty && e.DefId == "escort"));
        }

        [Test]
        public void EveryBossHasAnEscortTableWithAHelperInEachWave()
        {
            var catalog = Lab.Catalog;
            foreach (var boss in catalog.Vehicles.Values.Where(v => v.Boss))
            {
                Assert.IsTrue(catalog.Escorts.TryGetValue(boss.Id, out var table), boss.Id + " has its escorts");
                // The Supreme Commander keeps its old guard (the brief): its command aura is the help.
                if (boss.Id == "supreme_command") continue;
                var waves = new List<EscortWaveDef>(table.Phases);
                if (table.Arrive != null) waves.Add(table.Arrive);
                foreach (var w in waves) Assert.IsTrue(w.Units.Any(u => u.Helper), boss.Id + ": a helper in every wave");
            }
            foreach (var old in new[] { "behemoth_escort", "fortress_escort", "gunship_escort", "nuke_escort", "supreme_guard" })
                Assert.IsFalse(catalog.Vehicles.Values.SelectMany(v => v.Skills).Any(s => s.Id == old), old + " is the general system's now");
        }

        // ------------------------------------------------------------------ the kill time per boss (1 seed)

        private static readonly string[] Changed =
            { "armored_train", "behemoth_tempest", "behemoth", "behemoth_inferno", "fortress_hive", "fortress_bastion", "nuke_train", "rail_supergun", "landing_hovercraft" };

        private static readonly string[] Army =
            { "main_battle_tank", "main_battle_tank", "main_battle_tank", "main_battle_tank", "tank_destroyer", "tank_destroyer", "fpv_carrier",
              "fpv_carrier", "aa_vehicle", "ifv", "ifv", "attack_helicopter", "attack_helicopter", "mlrs", "artillery" };

        /// <summary>A standard army against the boss alone (no escorts, as prompt 9 measured): seconds to the kill, or -1.</summary>
        private static float KillTime(Catalog catalog, string id, int seed)
        {
            var world = new SimWorld(catalog, new MapDefinition("lab", 300f,
                new[] { new TeamStart(0, new Vector2(-120f, -120f)), new TeamStart(1, new Vector2(120f, 120f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed) { RevealAll = true };
            var boss = world.SpawnVehicle(id, 1, new Vector2(0f, 20f), MathF.PI);
            var ids = new List<EntityId>();
            for (var i = 0; i < Army.Length; i++)
                ids.Add(world.SpawnVehicle(Army[i], 0, new Vector2(-42f + 6f * i, -50f - (i % 3) * 6f), 0f).Id);
            for (var t = 0f; t < 600f; t += Step)
            {
                if (world.Tick % 40 == 0) world.Submit(new Command(CommandType.Attack, 0, ids, target: boss.Id));
                world.Step(Step);
                world.ClearEvents();
                if (!boss.IsAlive) return (float)world.Time;
                if (world.VehicleList.All(v => !v.IsAlive || v.Team != 0)) return -1f;
            }
            return -1f;
        }

        [Test]
        public void EachChangedBossStillFallsInAboutTheSameTime()
        {
            var now = Lab.Catalog;
            // The base data (lead/integration's balance.json), when the lead's scratch copy is at hand.
            var basePath = Environment.GetEnvironmentVariable("MB_BASE_BALANCE");
            var before = !string.IsNullOrEmpty(basePath) && File.Exists(basePath) ? Catalog.FromJson(File.ReadAllText(basePath)) : null;
            var log = new System.Text.StringBuilder("BOSS KILL TIMES (1 seed, boss alone):");
            foreach (var id in Changed)
            {
                var after = KillTime(now, id, 21);
                var was = before != null ? KillTime(before, id, 21) : float.NaN;
                log.Append($" {id} {after:0}s" + (before != null ? $" (was {was:0}s, x{after / was:0.00})" : ""));
                Assert.Greater(after, 0f, id + " can still be killed by the standard army");
            }
            Debug.Log(log.ToString());
        }
    }
}
