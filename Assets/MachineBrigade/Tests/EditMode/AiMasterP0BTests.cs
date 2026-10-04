using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.AI;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Economy;
using MachineBrigade.Sim.Entities;
using MachineBrigade.Sim.Modes;
using MachineBrigade.Sim.Navigation;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// AI MASTER lane P0-B, section 109 (and 15, 67, 196): the buying AI's map filter. Written by the lane, not run by it
    /// (the lead runs them). The maps are built here: a straight coast at x = 0 (sea to the east), land to the west.
    /// </summary>
    [Category("AIMasterP0B")]
    public class AiMasterP0BTests
    {
        private const float Half = 200f;

        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static readonly Vector2 Home = new(-150f, 0f);

        /// <summary>A 400 m square with the waterline at x = 0 and one lane <paramref name="laneW"/> m out.</summary>
        private static MapDefinition Coast(float laneW, IReadOnlyList<CapturePointDef> points = null)
        {
            var teams = new[] { new TeamStart(0, Home), new TeamStart(1, new Vector2(laneW, 0f)) };
            var lanes = new List<SeaLaneDef> { new() { Id = "far", W = laneW, Patrol = 120f, End = Half - 4f } };
            var sea = SeaDef.Straight(new Vector2(0f, 1f), 0f, -Half, Half, lanes, new List<SeaLandingDef>(), Array.Empty<Vector2>(),
                new Vector2(Half - 6f, 0f));
            return new MapDefinition("p0b_coast", Half * 2f, teams, Array.Empty<PropPlacement>(), Array.Empty<UnitPlacement>(), points) { Sea = sea };
        }

        private static float GroundReach(string id) =>
            WeaponEnvelope.Of(Catalog.Vehicle(id), TargetLayer.Naval).MaxRange;

        private static (SimWorld world, Vehicle boss) NavalBoss(float laneGapPastRadius, IReadOnlyList<CapturePointDef> points = null)
        {
            // The boss's own radius is only known once it is placed: place it on a probe map first.
            var radius = Catalog.Vehicle("leviathan").Radius;
            var laneW = laneGapPastRadius + radius;
            Assert.Less(laneW, Half - 10f, "the lane fits the map");
            var world = new SimWorld(Catalog, Coast(laneW, points), 7);
            var boss = world.SpawnVehicle("leviathan", 1, new Vector2(laneW, 0f), 0f);
            return (world, boss);
        }

        private static ProcurementDirector Director(SimWorld world, Vehicle boss, IObjectiveMode mode = null)
        {
            var director = new ProcurementDirector(0);
            director.Observe(world, new[] { boss }, Home, mode, boss.Position, null, null, null);
            return director;
        }

        private sealed class Points : IObjectiveMode
        {
            public Points(params CapturePointDef[] defs) => this.points = defs.Select(d => new ObjectiveState(d)).ToList();

            private readonly List<ObjectiveState> points;
            IReadOnlyList<ObjectiveState> IObjectiveMode.Points => points;
        }

        // ------------------------------------------------------------------ section 109 Test A

        [Test]
        public void A_NavalBossOutOfReachOfTheShoreRejectsBattleTanks()
        {
            // The lane lies 30 m past the longest of the battle tanks' guns (and the firing check's snap slack) from the waterline.
            var reach = Math.Max(GroundReach("main_battle_tank"), GroundReach("heavy_tank"));
            var (world, boss) = NavalBoss(reach + 30f);
            var director = Director(world, boss);

            foreach (var id in new[] { "main_battle_tank", "heavy_tank" })
            {
                Assert.IsFalse(director.Gate(world, Catalog.Vehicle(id), out var influence), $"{id}: {influence}");
                Assert.AreEqual("no-map-influence", director.LastReject(id));
                Assert.IsFalse(influence.CanReachEnemy, "a tank cannot drive to sea");
                Assert.IsFalse(influence.CanFireFromReachableRegion, "nor fire on the lane from the shore");
            }
            Assert.IsTrue(world.AiLog.Entries.Any(e => e.Kind == DecisionKind.Purchase && e.Text.StartsWith("REJECT main_battle_tank reason=no-map-influence")),
                "the rejection is in the decision log");

            // Aircraft that can hurt a ship stay eligible.
            var air = Catalog.Vehicles.Values
                .Where(d => d.Card && d.CpCost > 0 && !d.Boss && d.Flying && EngagementFeasibility.CanHit(d, TargetLayer.Naval))
                .OrderBy(d => d.Id, StringComparer.Ordinal).FirstOrDefault();
            Assert.IsNotNull(air, "the roster has an aircraft that strikes ships");
            Assert.IsTrue(director.Gate(world, air, out var airInfluence), airInfluence.ToString());
            Assert.IsTrue(airInfluence.CanFireFromReachableRegion);
        }

        // ------------------------------------------------------------------ section 109 Test B

        [Test]
        public void B_ACoastalGunThatReachesTheLaneFromTheShoreIsEligible()
        {
            var gun = LongestGroundGun();
            var reach = GroundReach(gun.Id);
            var (world, boss) = NavalBoss(reach * 0.6f);
            var director = Director(world, boss);

            Assert.IsTrue(director.Gate(world, gun, out var influence), $"{gun.Id}: {influence}");
            Assert.IsFalse(influence.CanReachEnemy, "it cannot drive to the ship");
            Assert.IsTrue(influence.CanFireFromReachableRegion, "but it fires on the lane from the shore");
            Assert.Greater(influence.Coverage, 0f);
            Assert.Less(influence.TravelSeconds, float.PositiveInfinity, "the firing ground has a travel time");
        }

        [Test]
        public void B_TheFiringGroundMustBeReachable()
        {
            // The same gun, but a wall cuts the shore strip off from the drop zone: the strip is its own ground component,
            // and from behind the wall the lane is out of reach.
            var gun = LongestGroundGun();
            var reach = GroundReach(gun.Id);
            var (world, boss) = NavalBoss(reach * 0.6f);
            var wallX = -reach * 0.6f;
            world.Grid.AddBlocker(new Vector2(wallX - 1f, 0f), 2f, Half * 2f + 8f, 0f);
            var director = Director(world, boss);

            var topo = world.Topology;
            Assert.AreNotEqual(topo.Ground.ComponentAt(Home), topo.Ground.ComponentAt(new Vector2(-2f, 0f)),
                "the shore strip is a separate ground component");
            Assert.AreEqual(0, topo.Ground.ComponentAt(new Vector2(10f, 0f)), "the sea is no ground");
            Assert.Greater(topo.Naval.ComponentAt(boss.Position), 0, "the boss is on a naval component");

            Assert.IsFalse(director.Gate(world, gun, out var influence), $"{gun.Id}: {influence}");
            Assert.AreEqual("no-map-influence", director.LastReject(gun.Id));
        }

        // ------------------------------------------------------------------ section 109 Test C

        [Test]
        public void C_ALandObjectiveKeepsGroundUnitsEligibleAgainstANavalBoss()
        {
            var reach = Math.Max(GroundReach("main_battle_tank"), GroundReach("heavy_tank"));
            var point = new CapturePointDef("hill", "Hill", new Vector2(-60f, 30f), 10f);
            var (world, boss) = NavalBoss(reach + 30f, new[] { point });
            var director = Director(world, boss, new Points(point));

            Assert.IsTrue(director.Gate(world, Catalog.Vehicle("main_battle_tank"), out var influence), influence.ToString());
            Assert.IsTrue(influence.CanReachObjective, "the tank serves the land objective");
            Assert.IsFalse(influence.CanFireFromReachableRegion, "even though it cannot touch the ship");
            Assert.IsNull(director.LastReject("main_battle_tank"));
            var objective = world.Topology.Objectives.First(o => o.Id == "hill");
            Assert.AreEqual(world.Topology.Ground.ComponentAt(Home), objective.GroundComponent, "the point is on the drop zone's ground");
        }

        // ------------------------------------------------------------------ section 196 (109's procurement feedback row)

        [Test]
        public void LowSameMatchUtilizationLowersTheScore()
        {
            var world = new SimWorld(Catalog, Sim.Sandbox.SandboxMaps.Flat(), 3);
            var director = new ProcurementDirector(0);
            world.TryGetRally(0, out var home);
            director.Observe(world, Array.Empty<Vehicle>(), home, null, null, null, null, null);
            var economy = new TeamEconomy(0, 40f);
            var tank = Catalog.Vehicle("main_battle_tank");
            Assert.IsTrue(director.Gate(world, tank, out var influence));

            var before = director.Score(world, economy, tank, influence, 0, null, null);
            var adjustBefore = director.LegacyAdjust(before, tank, AiDifficulty.Normal);
            Assert.Greater(before, 0f);

            // 30 s in a fight, firing 1.5 s of it (5 %): under the 15 % line.
            director.RecordUse(tank.Id, 30f, 1.5f);
            var modifier = director.FeedbackModifier(tank.Id);
            Assert.Less(modifier, 1f);
            Assert.GreaterOrEqual(modifier, SimTunables.Ai.Procurement.FeedbackMinModifier - 1e-4f);
            var factors = new List<Factor>();
            var after = director.Score(world, economy, tank, influence, 0, null, factors);
            Assert.Less(after, before, "the master score falls");
            Assert.Less(director.LegacyAdjust(after, tank, AiDifficulty.Normal), adjustBefore, "and so does the buying score");
            Assert.IsTrue(factors.Any(f => f.Key == "low-realized-utilization"), "the reason is named");

            // Used well, or not fought long enough to judge: no change.
            director.RecordUse("heavy_tank", 30f, 12f);
            Assert.AreEqual(1f, director.FeedbackModifier("heavy_tank"));
            director.RecordUse("ifv", 10f, 0f);
            Assert.AreEqual(1f, director.FeedbackModifier("ifv"));
        }

        // ------------------------------------------------------------------ sections 15 and 67

        [Test]
        public void OneAircraftDoesNotConfirmACounterNeedAtOnce()
        {
            var world = new SimWorld(Catalog, Sim.Sandbox.SandboxMaps.Flat(), 5);
            var heli = Catalog.Vehicles.Values.Where(d => d.Card && d.CpCost > 0 && d.Flying && !d.Boss)
                .OrderBy(d => d.Id, StringComparer.Ordinal).First();
            var enemy = world.SpawnVehicle(heli.Id, 1, new Vector2(40f, 40f), 0f);
            var director = new ProcurementDirector(0);
            world.TryGetRally(0, out var home);
            director.Observe(world, new[] { enemy }, home, null, null, null, null, null);
            Assert.IsFalse(director.Confirmed(ProcurementDirector.Threat.Air, world.Time), "one sighting is not a confirmed need");
            Assert.Less(director.Share(ProcurementDirector.Threat.Air), 0.21f, "the EMA moves a fifth of the way");
        }

        [Test]
        public void FactorySpawnsUseTheSameFeasibility()
        {
            var reach = GroundReach("main_battle_tank");
            var (world, _) = NavalBoss(reach + 30f);
            var tank = Catalog.Vehicle("main_battle_tank");
            Assert.IsFalse(world.Feasibility.SpawnUseful(tank, 1, new Vector2(150f, 0f), out var atSea), "no tank comes out on the open sea: " + atSea);
            Assert.IsTrue(world.Feasibility.SpawnUseful(tank, 1, new Vector2(-40f, 0f), out var onLand), "one on the shore reaches the other camp: " + onLand);
        }

        /// <summary>The ground card with the longest reach on ships up to 140 m (the test map's room), longer than a battle tank's.</summary>
        private static VehicleDef LongestGroundGun()
        {
            var tank = GroundReach("main_battle_tank");
            var gun = Catalog.Vehicles.Values
                .Where(d => d.Card && d.CpCost > 0 && !d.Boss && !d.Flying && !d.Static && d.Naval == null)
                .Where(d => WeaponEnvelope.Of(d, TargetLayer.Naval).MaxRange <= 140f)
                .OrderByDescending(d => WeaponEnvelope.Of(d, TargetLayer.Naval).MaxRange).ThenBy(d => d.Id, StringComparer.Ordinal).First();
            Assert.Greater(WeaponEnvelope.Of(gun, TargetLayer.Naval).MaxRange, tank * 1.3f, "a gun that outranges the tanks: " + gun.Id);
            return gun;
        }
    }
}
