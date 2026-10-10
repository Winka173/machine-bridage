using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using NUnit.Framework;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Combat;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Entities;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// Scout Target Designation (10/10), prompt section 14 items 1-15. Written while testing is paused (not run when
    /// written). Targets are firing-range dummies (they never fire and are always seen), so a fight cannot kill a scout
    /// by accident; the damage factor is read through DesignationSystem.Multiplier and, once, through DamageSystem.Apply.
    /// </summary>
    public class ScoutDesignationTests
    {
        private const int Interval = 40, Duration = 100;

        private static SimWorld Field(int seed = 1) =>
            new SimWorld(GameContent.LoadCatalog(), new MapDefinition("field", 200f,
                new[] { new TeamStart(0, new Vector2(-80f, -80f)), new TeamStart(1, new Vector2(80f, 80f)) },
                new List<PropPlacement>(), new List<UnitPlacement>()), seed);

        private static void Ticks(SimWorld world, int n)
        {
            for (var i = 0; i < n; i++)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
            }
        }

        private static Vehicle Dummy(SimWorld world, string id, int team, Vector2 at)
        {
            var v = world.SpawnVehicle(id, team, at, 0f);
            world.MakeDummy(v);
            return v;
        }

        private static HitInfo Hit(Vehicle attacker, HitKind kind) =>
            new HitInfo(attacker, attacker.Team, attacker.Def.Weapon, attacker.Position, kind, false);

        /// <summary>Two ticks past one retarget interval: every scout has picked and marked at least once.</summary>
        private static void LetMark(SimWorld world) => Ticks(world, 2 * Interval + 2);

        [Test]
        public void OneScoutMarksOneTargetForTenPercentDirectDamage()
        {
            var world = Field();
            var scout = world.SpawnVehicle("scout_jeep", 0, new Vector2(0f, 0f), 0f);
            var tank = Dummy(world, "heavy_tank", 1, new Vector2(20f, 0f));
            var ally = world.SpawnVehicle("light_tank", 0, new Vector2(-10f, 0f), 0f);
            LetMark(world);
            Assert.IsTrue(world.Designation.IsMarkedFor(tank, 0), "the scout marked it");
            Assert.AreEqual(1.10f, world.Designation.Multiplier(tank, Hit(ally, HitKind.Direct)), 1e-5f);
            // Through the pipeline: the same direct hit on a fresh, unmarked twin in another world deals 10 % less.
            var twinWorld = Field();
            var twin = Dummy(twinWorld, "heavy_tank", 1, new Vector2(20f, 0f));
            var twinAlly = twinWorld.SpawnVehicle("light_tank", 0, new Vector2(-10f, 0f), 0f);
            var marked = world.Damage.Apply(tank, 40f, DamageType.Kinetic, Hit(ally, HitKind.Direct));
            var plain = twinWorld.Damage.Apply(twin, 40f, DamageType.Kinetic, Hit(twinAlly, HitKind.Direct));
            Assert.Greater(plain, 0f);
            Assert.AreEqual(plain * 1.10f, marked, plain * 1e-3f);
            Assert.IsNotNull(scout);
        }

        [Test]
        public void TwoScoutsOnTheSameTargetStillGiveTenPercent()
        {
            var world = Field();
            world.SpawnVehicle("scout_jeep", 0, new Vector2(0f, 0f), 0f);
            world.SpawnVehicle("scout_jeep", 0, new Vector2(0f, 4f), 0f);
            var tank = Dummy(world, "heavy_tank", 1, new Vector2(20f, 0f));
            var ally = world.SpawnVehicle("light_tank", 0, new Vector2(-10f, 0f), 0f);
            LetMark(world);
            Assert.AreEqual(1.10f, world.Designation.Multiplier(tank, Hit(ally, HitKind.Direct)), 1e-5f);
        }

        [Test]
        public void ScoutOfSideAGivesNothingToSideB()
        {
            var world = Field();
            world.SpawnVehicle("scout_jeep", 0, new Vector2(0f, 0f), 0f);
            var tank = Dummy(world, "heavy_tank", 1, new Vector2(20f, 0f));
            var enemyShooter = world.SpawnVehicle("light_tank", 1, new Vector2(40f, 0f), 0f);
            var friendlyFire = world.SpawnVehicle("light_tank", 1, new Vector2(40f, 4f), 0f);
            LetMark(world);
            Assert.IsTrue(world.Designation.IsMarkedFor(tank, 0));
            Assert.IsFalse(world.Designation.IsMarkedFor(tank, 1), "the mark belongs to side 0 only");
            Assert.AreEqual(1f, world.Designation.Multiplier(tank, Hit(enemyShooter, HitKind.Direct)), 1e-6f, "side 1 fires on its own unit: friendly fire, no bonus");
            Assert.AreEqual(1f, world.Designation.Multiplier(tank, Hit(friendlyFire, HitKind.Direct)), 1e-6f);
        }

        [Test]
        public void ScoutDoesNotBenefitFromItsOwnMark()
        {
            var world = Field();
            var scout = world.SpawnVehicle("scout_jeep", 0, new Vector2(0f, 0f), 0f);
            var tank = Dummy(world, "heavy_tank", 1, new Vector2(20f, 0f));
            LetMark(world);
            Assert.IsTrue(world.Designation.IsMarkedFor(tank, 0));
            Assert.AreEqual(1f, world.Designation.Multiplier(tank, Hit(scout, HitKind.Direct)), 1e-6f);
        }

        [Test]
        public void BossTakesFivePercent()
        {
            var world = Field();
            world.SpawnVehicle("recon_drone", 0, new Vector2(0f, 0f), 0f);
            var bossDef = world.Catalog.Vehicles.Values.First(d => d.Boss && !d.Static && d.Parts.Count == 0 && !d.Flying);
            var boss = world.SpawnVehicle(bossDef.Id, 1, new Vector2(30f, 0f), 0f);
            world.MakeDummy(boss);
            var ally = world.SpawnVehicle("light_tank", 0, new Vector2(-10f, 0f), 0f);
            LetMark(world);
            Assert.IsTrue(world.Designation.IsMarkedFor(boss, 0));
            Assert.AreEqual(1.05f, world.Designation.Multiplier(boss, Hit(ally, HitKind.Direct)), 1e-5f);
        }

        [Test]
        public void SplashAndDamageOverTimeGetNothing()
        {
            var world = Field();
            world.SpawnVehicle("scout_jeep", 0, new Vector2(0f, 0f), 0f);
            var tank = Dummy(world, "heavy_tank", 1, new Vector2(20f, 0f));
            var ally = world.SpawnVehicle("light_tank", 0, new Vector2(-10f, 0f), 0f);
            LetMark(world);
            Assert.AreEqual(1f, world.Designation.Multiplier(tank, Hit(ally, HitKind.Splash)), 1e-6f, "blast damage");
            Assert.AreEqual(1f, world.Designation.Multiplier(tank, Hit(ally, HitKind.Burn)), 1e-6f, "damage over time");
            Assert.AreEqual(1f, world.Designation.Multiplier(tank, Hit(ally, HitKind.Strike)), 1e-6f, "called fire");
            Assert.AreEqual(1f, world.Designation.Multiplier(tank, Hit(ally, HitKind.Mine)), 1e-6f, "a mine");
            Assert.AreEqual(1f, world.Designation.Multiplier(tank, new HitInfo(null, 0, null, Vector2.Zero, HitKind.Direct, false)), 1e-6f, "script, no attacker");
        }

        [Test]
        public void MarkIsRecalledWhenTheTargetDies()
        {
            var world = Field();
            world.SpawnVehicle("scout_jeep", 0, new Vector2(0f, 0f), 0f);
            var tank = Dummy(world, "heavy_tank", 1, new Vector2(20f, 0f));
            LetMark(world);
            Assert.IsTrue(world.Designation.IsMarkedFor(tank, 0));
            tank.Hp = 0f;
            Assert.IsFalse(world.Designation.IsMarkedFor(tank, 0), "a dead target carries no mark");
            Ticks(world, 1);
            Assert.AreEqual(0, world.MarkedTargets.Count, "and leaves the HUD list");
        }

        [Test]
        public void MarkLapsesExactlyAfterTheScoutDies()
        {
            var world = Field();
            var scout = world.SpawnVehicle("scout_jeep", 0, new Vector2(0f, 0f), 0f);
            var tank = Dummy(world, "heavy_tank", 1, new Vector2(20f, 0f));
            var ally = world.SpawnVehicle("light_tank", 0, new Vector2(-10f, 0f), 0f);
            LetMark(world);
            scout.Hp = 0f;
            Assert.AreEqual(1f, world.Designation.Multiplier(tank, Hit(ally, HitKind.Direct)), 1e-6f, "the dead scout's mark is gone at once");
            Ticks(world, Duration + Interval);
            Assert.IsFalse(world.Designation.IsMarkedFor(tank, 0));
        }

        [Test]
        public void ScoutSwitchingTargetLeavesNoMarkBehind()
        {
            var world = Field();
            var scout = world.SpawnVehicle("scout_jeep", 0, new Vector2(0f, 0f), 0f);
            var first = Dummy(world, "light_tank", 1, new Vector2(20f, 0f));
            LetMark(world);
            Assert.IsTrue(world.Designation.IsMarkedFor(first, 0));
            // A much more dangerous target (long-range fire) comes into range: the scout moves its one mark.
            var gun = Dummy(world, "artillery", 1, new Vector2(10f, 5f));
            Ticks(world, Interval + 2);
            Assert.AreEqual(gun.Id, scout.DesignationTarget);
            Assert.IsTrue(world.Designation.IsMarkedFor(gun, 0));
            Assert.IsFalse(world.Designation.IsMarkedFor(first, 0), "the old target's mark was handed back");
        }

        [Test]
        public void SecondScoutKeepsTheMarkWhenTheFirstDies()
        {
            var world = Field();
            var a = world.SpawnVehicle("scout_jeep", 0, new Vector2(0f, 0f), 0f);
            world.SpawnVehicle("scout_jeep", 0, new Vector2(0f, 4f), 0f);
            var tank = Dummy(world, "heavy_tank", 1, new Vector2(20f, 0f));
            var ally = world.SpawnVehicle("light_tank", 0, new Vector2(-10f, 0f), 0f);
            LetMark(world);
            a.Hp = 0f;
            Assert.IsTrue(world.Designation.IsMarkedFor(tank, 0), "the living scout's mark stands");
            Assert.AreEqual(1.10f, world.Designation.Multiplier(tank, Hit(ally, HitKind.Direct)), 1e-5f);
        }

        [Test]
        public void TargetOutOfRangeIsNotMarkedAndTheMarkIsNotRefreshed()
        {
            var world = Field();
            var scout = world.SpawnVehicle("scout_jeep", 0, new Vector2(0f, 0f), 0f);
            var far = Dummy(world, "heavy_tank", 1, new Vector2(60f, 0f));
            LetMark(world);
            Assert.IsFalse(world.Designation.IsMarkedFor(far, 0), "36 m and more is out of the jeep's 35 m");
            // In range first, then it leaves: the mark is not refreshed and runs out within one mark duration.
            far.Position = new Vector2(20f, 0f);
            LetMark(world);
            Assert.IsTrue(world.Designation.IsMarkedFor(far, 0));
            far.Position = new Vector2(80f, 0f);
            scout.Position = new Vector2(0f, 0f);
            Ticks(world, Duration + 1);
            Assert.IsFalse(world.Designation.IsMarkedFor(far, 0));
        }

        [Test]
        public void AiDoesNotFireOutOfReachJustBecauseTheTargetIsMarked()
        {
            var world = Field();
            world.SpawnVehicle("scout_jeep", 0, new Vector2(0f, 0f), 0f);
            var tank = Dummy(world, "heavy_tank", 1, new Vector2(20f, 0f));
            var shooter = world.SpawnVehicle("light_tank", 0, new Vector2(-150f, 0f), 0f);
            LetMark(world);
            Assert.IsTrue(world.Designation.IsMarkedFor(tank, 0));
            Assert.AreNotEqual(MachineBrigade.Sim.AI.TargetReject.None, world.Combat.Feasibility(shooter, shooter.Def.Weapon, tank),
                "the priority factor sits inside Score; Feasibility (reach, arc, visibility) still decides");
            Assert.AreEqual(SimTunables.Vehicles.ScoutDesignation.MarkedPriorityMultiplier, world.Designation.PriorityFor(shooter, tank), 1e-6f);
        }

        [Test]
        public void StealthKeepsItsCombatBehaviour()
        {
            var world = Field();
            var scout = world.SpawnVehicle("scout_jeep", 0, new Vector2(0f, 0f), 0f);
            var stealth = world.Catalog.Vehicles.Values.First(d => d.Stealth && !d.Static);
            var ghost = world.SpawnVehicle(stealth.Id, 1, new Vector2(34f, 0f), 0f);
            Ticks(world, 1);
            var seenBefore = ghost.IsVisibleTo(0);
            LetMark(world);
            Assert.AreEqual(seenBefore, ghost.IsVisibleTo(0), "a mark neither reveals nor hides anything");
            if (!seenBefore) Assert.IsFalse(world.Designation.IsMarkedFor(ghost, 0), "an unseen stealth unit cannot be designated");
            Assert.IsNotNull(scout);
        }

        [Test]
        public void SameSeedSameStateHash()
        {
            ulong Run()
            {
                var world = Field(7);
                world.SpawnVehicle("scout_jeep", 0, new Vector2(0f, 0f), 0f);
                world.SpawnVehicle("recon_drone", 0, new Vector2(-20f, 0f), 0f);
                world.SpawnVehicle("scout_heli", 0, new Vector2(-10f, 8f), 0f);
                for (var i = 0; i < 4; i++) world.SpawnVehicle("heavy_tank", 0, new Vector2(-30f, i * 6f), 0f);
                for (var i = 0; i < 4; i++) world.SpawnVehicle("light_tank", 1, new Vector2(25f, i * 6f - 10f), 3.14f);
                Ticks(world, 20 * 20);
                return world.StateHash();
            }
            Assert.AreEqual(Run(), Run());
        }

        [Test]
        public void RangesComeFromData()
        {
            var catalog = GameContent.LoadCatalog();
            Assert.AreEqual(35f, catalog.Vehicles["scout_jeep"].DesignationRange);
            Assert.AreEqual(55f, catalog.Vehicles["recon_drone"].DesignationRange);
            Assert.AreEqual(45f, catalog.Vehicles["scout_heli"].DesignationRange);
            Assert.AreEqual(0f, catalog.Vehicles["heavy_tank"].DesignationRange);
        }
    }
}
