using System;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Commands;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Modes;
using Vector2 = System.Numerics.Vector2;
using EntityId = MachineBrigade.Sim.Core.EntityId;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Prompt 32 L4 (DECISIONS "Prompt 32 L4/L5/L6/L8"): the HQ types. The data's tables; a Fortress HQ stands as its
    /// branch's def with its gun scaled by HQ level; a Shield HQ's point defence by level; the Garrison stocks, turns out,
    /// stays outside supply, pays nothing and goes back in; the one skill and its shared cooldown; the emergency dome
    /// absorbs; the Fortress barrage's scale; the AI's choice by general; the HQ's damage marks; the point-defence
    /// stacking rule (the nearest system takes a round). Written, not run.
    /// </summary>
    public class HqTypeP32Tests
    {
        private static Catalog _catalog;
        private static Catalog C => _catalog ??= GameContent.LoadCatalog();
        private static HqTypeRules R => C.Base.HqTypes;

        private static void Run(SimWorld world, float seconds)
        {
            for (var t = 0f; t < seconds && !world.IsOver; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
        }

        private static (SimWorld world, TeamBase b) Base(HqType type, int level, HqBranch branch = HqBranch.Ground)
        {
            var world = new SimWorld(C, GameContent.LoadMap("ashfield_conquest"), seed: 7);
            world.EnableEconomy(new TeamEconomy(0, 30f, bank: 80f));
            world.EnableEconomy(new TeamEconomy(1, 30f, bank: 80f));
            var b = world.Bases.Establish(0, new BaseLoadout { HqLevel = level, HqType = type, HqBranch = branch }, BaseRole.Defend);
            return (world, b);
        }

        [Test]
        public void TheHqTypesComeFromTheData()
        {
            Assert.AreEqual(120f, R.SkillCooldown, 1e-3f);
            Assert.Greater(R.Radius, 10f);
            foreach (var id in new[] { R.FortressGround, R.FortressAir, R.ShieldHq })
                Assert.IsTrue(C.Vehicles.ContainsKey(id), id);
            Assert.IsTrue(C.TryGetSupport(R.Barrage, out var barrage) && barrage.EventOnly, "the barrage is an event support");
            Assert.AreEqual(3, barrage.Count, "three heavy rounds");
            for (var level = 1; level <= 5; level++)
            {
                Assert.Greater(R.FortressScale(level), 0f);
                Assert.Greater(R.FortressScale(level, HqBranch.Air), 0f);
                Assert.Greater(R.ShieldScale(level), 0f);
                Assert.Greater(R.GarrisonEvery(level), 0f);
                Assert.Greater(R.GarrisonCap(level), 0);
                Assert.IsNotEmpty(R.Squad(level));
                foreach (var unit in R.Squad(level)) Assert.IsTrue(C.Vehicles.ContainsKey(unit), unit);
                if (level > 1) Assert.GreaterOrEqual(R.GarrisonCap(level), R.GarrisonCap(level - 1), "the cap grows with the level");
            }
            Assert.AreEqual(new[] { "light_tank" }, R.Squad(1).ToArray());
            Assert.AreEqual(new[] { "main_battle_tank", "scout_jeep" }, R.Squad(5).ToArray());
        }

        [Test]
        public void AFortressHqStandsAsItsBranchWithItsGunScaledByLevel()
        {
            foreach (var branch in new[] { HqBranch.Ground, HqBranch.Air })
            {
                var (world, b) = Base(HqType.Fortress, 3, branch);
                Assert.IsTrue(world.TryGetVehicle(b.Hq, out var hq));
                Assert.AreEqual(branch == HqBranch.Air ? R.FortressAir : R.FortressGround, hq.Def.Id);
                var plain = C.Vehicles[C.Base.HqId].Mounts.Count;
                Assert.Greater(hq.Weapons.Length, plain, "the type's gun is a mount more");
                var k = MathF.Sqrt(R.FortressScale(3, branch));
                for (var i = 0; i < hq.Weapons.Length; i++)
                {
                    var want = i >= plain ? k : 1f;
                    Assert.AreEqual(want, hq.Weapons[i].DamageScale, 1e-4f, $"mount {i} damage");
                    Assert.AreEqual(want, hq.Weapons[i].RateScale, 1e-4f, $"mount {i} cadence");
                }
            }
        }

        [Test]
        public void AShieldHqsPointDefenceTakesItsLevelsShare()
        {
            for (var level = 1; level <= 5; level++)
            {
                var (world, b) = Base(HqType.Shield, level);
                Assert.IsTrue(world.TryGetVehicle(b.Hq, out var hq));
                Assert.AreEqual(R.ShieldHq, hq.Def.Id);
                Assert.IsNotNull(hq.Aps, "the Shield HQ carries a point defence");
                Assert.Greater(hq.Aps.Burst, 0f, "a gun point defence (POINT_DEFENSE), as the C-RAM's");
                var k = R.ShieldScale(level);
                Assert.AreEqual(Math.Clamp((int)MathF.Round(R.ShieldCharges * k), 1, hq.Aps.Charges), hq.ApsMax, $"HQ {level}");
                Assert.AreEqual(k, hq.ApsRate, 1e-4f);
            }
        }

        [Test]
        public void APlainOrGarrisonHqStandsAsThePlainHq()
        {
            var (world, b) = Base(HqType.Garrison, 2);
            Assert.IsTrue(world.TryGetVehicle(b.Hq, out var hq));
            Assert.AreEqual(C.Base.HqId, hq.Def.Id);
        }

        [Test]
        public void TheGarrisonStocksASquadAndTurnsItOutForAnIntruder()
        {
            var (world, b) = Base(HqType.Garrison, 1);
            world.TryGetEconomy(0, out var economy);
            Run(world, R.GarrisonEvery(1) + 1f);
            Assert.AreEqual(1, b.Hq32.Stock, "one squad stocked");
            var army = economy.ArmyCp;
            var intruder = world.SpawnVehicle("armored_car", 1, b.HqPosition + new Vector2(R.Radius * 0.5f, 0f), 0f);
            Run(world, 1f);
            var garrison = world.Vehicles.Where(v => v.IsAlive && v.Team == 0 && v.Garrison).ToList();
            Assert.IsNotEmpty(garrison, "the squad turned out");
            Assert.AreEqual(0, b.Hq32.Stock);
            foreach (var g in garrison)
            {
                Assert.LessOrEqual(Vector2.Distance(g.Position, b.HqPosition), R.Radius, "inside the base region");
                Assert.AreEqual(R.Radius, g.PostRadius, 1e-3f, "its post is the base region");
            }
            Run(world, 0.5f);
            Assert.AreEqual(army, economy.ArmyCp, "never in the army value supply reads");
            Assert.LessOrEqual(world.Bases.GarrisonCp(b.Hq32), R.GarrisonCap(1), "the alive cap holds");
            GC.KeepAlive(intruder);
        }

        [Test]
        public void AGarrisonSquadPaysNothingWhenDestroyed()
        {
            var (world, b) = Base(HqType.Garrison, 1);
            Run(world, R.GarrisonEvery(1) + 1f);
            world.SpawnVehicle("armored_car", 1, b.HqPosition + new Vector2(R.Radius * 0.5f, 0f), 0f);
            Run(world, 1f);
            var g = world.Vehicles.First(v => v.IsAlive && v.Garrison);
            world.TryGetEconomy(1, out var enemy);
            enemy.Cp = 5f;
            g.LastAttackerTeam = 1;
            world.Economy.OnVehicleDestroyed(g);
            Assert.AreEqual(5f, enemy.Cp, 1e-4f, "no CP for a garrison squad");
        }

        [Test]
        public void TheGarrisonGoesBackInOnceTheBaseIsClear()
        {
            var (world, b) = Base(HqType.Garrison, 1);
            Run(world, R.GarrisonEvery(1) + 1f);
            var intruder = world.SpawnVehicle("armored_car", 1, b.HqPosition + new Vector2(R.Radius * 0.5f, 0f), 0f);
            Run(world, 1f);
            Assert.IsTrue(world.Vehicles.Any(v => v.IsAlive && v.Garrison));
            intruder.Hp = 0f;
            Run(world, R.GarrisonClear + 2f);
            Assert.IsFalse(world.Vehicles.Any(v => v.IsAlive && v.Garrison), "gone after the base was clear");
        }

        [Test]
        public void TheSkillHasOneSharedCooldown()
        {
            var (world, b) = Base(HqType.Shield, 4);
            Assert.IsTrue(world.Submit(Command.HqSkill(0)).Accepted);
            var again = world.Submit(Command.HqSkill(0));
            Assert.IsFalse(again.Accepted);
            Assert.AreEqual(CommandError.OnCooldown, again.Error);
            Assert.AreEqual(R.SkillCooldown, b.Hq32.SkillLeft(world.Time), 0.01f);
            Run(world, R.SkillCooldown + 0.5f);
            Assert.AreEqual(0f, b.Hq32.SkillLeft(world.Time), 1e-3f, "ready again after its cooldown");
        }

        [Test]
        public void TheEmergencyDomeAbsorbsTheHqsShareAndLapses()
        {
            var (world, b) = Base(HqType.Shield, 5);
            Assert.IsTrue(world.TryGetVehicle(b.Hq, out var hq));
            Assert.IsTrue(world.Submit(Command.HqSkill(0)).Accepted);
            Assert.AreEqual(hq.MaxHp * R.Dome(5), b.Hq32.DomeHp, 0.5f);
            Assert.IsNotNull(world.Bases.SkillDomeOver(hq), "the HQ is under its dome");
            var through = world.Domes.Absorb(hq, 10f, DamageType.Kinetic, default);
            Assert.AreEqual(0f, through, 1e-3f, "a small hit is absorbed whole");
            Run(world, R.DomeSeconds + 0.5f);
            Assert.IsNull(world.Bases.SkillDomeOver(hq), "the dome lapses");
        }

        [Test]
        public void TheFortressBarrageIsAimedAndScaledByLevel()
        {
            var (world, b) = Base(HqType.Fortress, 2);
            Assert.AreEqual(R.FortressScale(2), world.Bases.SkillStrikeScale(0, R.Barrage), 1e-4f);
            Assert.AreEqual(1f, world.Bases.SkillStrikeScale(0, "artillery_barrage"), 1e-4f, "no other support");
            var at = b.HqPosition + new Vector2(20f, 0f);
            Assert.IsTrue(world.Submit(Command.HqSkill(0, at)).Accepted);
            Assert.IsFalse(world.Submit(Command.HqSkill(0, at)).Accepted, "on cooldown");
        }

        [Test]
        public void TheAiChoosesItsHqTypeByGeneralElseDifficulty()
        {
            Assert.AreEqual(HqType.Garrison, BaseLoadout.ForAi(C, "Normal", "varga").HqType);
            Assert.AreEqual(HqType.Shield, BaseLoadout.ForAi(C, "Normal", "orlov").HqType);
            Assert.AreEqual(HqType.Shield, BaseLoadout.ForAi(C, "Normal", "aurel").HqType);
            Assert.AreEqual(HqType.Fortress, BaseLoadout.ForAi(C, "Normal", "kessler").HqType);
            Assert.AreEqual(R.ForAi(null, "Easy"), BaseLoadout.ForAi(C, "Easy", "default").HqType);
            Assert.AreEqual(R.ForAi(null, "Hard"), BaseLoadout.ForAi(C, "Hard", "default").HqType);
            // A Fortress facing a deck of aircraft takes the anti-air guns.
            var air = BaseLoadout.ForAi(C, "Normal", "kessler", against: new[] { "attack_helicopter", "attack_jet", "scout_heli" });
            Assert.AreEqual(HqBranch.Air, air.HqBranch);
        }

        [Test]
        public void TheHqsDamageMarksAreGivenOnce()
        {
            var (world, b) = Base(HqType.Fortress, 1);
            Assert.IsTrue(world.TryGetVehicle(b.Hq, out var hq));
            hq.Hp = hq.MaxHp * 0.49f;
            Run(world, 0.2f);
            Assert.IsTrue(b.Hq32.Half, "the half mark");
            Assert.IsFalse(b.Hq32.Quarter);
            hq.Hp = hq.MaxHp * 0.2f;
            Run(world, 0.2f);
            Assert.IsTrue(b.Hq32.Quarter, "the quarter mark");
            Assert.IsTrue(hq.IsAlive, "the marks take nothing away");
        }

        [Test]
        public void ARoundIsOfferedOnlyToTheNearestPointDefence()
        {
            var world = new SimWorld(C, GameContent.LoadMap("ashfield_conquest"), seed: 3);
            var target = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 0f), 0f);
            var near = world.SpawnVehicle("laser_ad_station", 0, new Vector2(8f, 0f), 0f);
            var far = world.SpawnVehicle("laser_ad_station", 0, new Vector2(-20f, 0f), 0f);
            world.SpawnVehicle("nlos_atgm_vehicle", 1, new Vector2(0f, 60f), MathF.PI);
            int nearFull = near.ApsCharges, farFull = far.ApsCharges;
            for (var t = 0f; t < 30f; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                if (near.ApsCharges < nearFull || far.ApsCharges < farFull) break;
            }
            if (near.ApsCharges == nearFull && far.ApsCharges == farFull) Assert.Inconclusive("no round came in reach");
            Assert.Less(near.ApsCharges, nearFull, "the nearer system took it");
            Assert.AreEqual(farFull, far.ApsCharges, "the farther one was never offered it");
            GC.KeepAlive(target);
        }
    }
}
