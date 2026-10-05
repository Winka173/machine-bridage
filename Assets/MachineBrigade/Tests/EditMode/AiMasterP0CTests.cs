using System;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using MachineBrigade.Game.Match;
using MachineBrigade.Sim;
using MachineBrigade.Sim.Bosses;
using MachineBrigade.Sim.Content;
using MachineBrigade.Sim.Core;
using MachineBrigade.Sim.Entities;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// AI MASTER P0-C (DECISIONS "AI MASTER P0-C (lane C)"): the boss brain's naval tests of spec section 110 (heading, target
    /// behind, turn radius, collision), Part R row R5 (a boss that loses a broadside recomputes it, Part F5), and the rules the
    /// controllers are built on (no reverse, cadence, escort rings, corridor). Written for the lead to run (the owner's rule:
    /// agents write tests, they do not run them).
    /// </summary>
    public class AiMasterP0CTests
    {
        private const float Dt = 0.05f;
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        private static SimWorld Bay(int seed = 1)
        {
            var world = new SimWorld(Catalog, GameContent.LoadMap("lighthousebay_sandbox"), seed);
            // No escorts unless a test wants them: the boss's own steering is under test.
            world.SeaRules.FleetShare = 0f;
            return world;
        }

        private static string Battery => Catalog.Vehicles.ContainsKey("coastal_battery") ? "coastal_battery" : "heavy_turret";

        private static void Run(SimWorld world, float seconds, Action<int> each = null)
        {
            var ticks = (int)(seconds / Dt);
            for (var t = 0; t < ticks; t++)
            {
                world.Step(Dt);
                world.ClearEvents();
                each?.Invoke(t);
            }
        }

        /// <summary>The flagship on <paramref name="lane"/> at <paramref name="u"/>, sailing +u (set after its first phase's lane).</summary>
        private static Vehicle Flagship(SimWorld world, float u, string lane = "mid", string id = "leviathan")
        {
            var sea = world.Map.Sea;
            var boss = world.SpawnVehicle(id, 1, sea.At(u, sea.Lane(lane).W), SimMath.HeadingOf(sea.Along));
            world.Step(Dt);
            world.ClearEvents();
            boss.NavalLane = lane;
            boss.NavalDir = 1;
            boss.Heading = SimMath.HeadingOf(sea.Along);
            Assert.IsNotNull(boss.BossBrain, id + " has a boss brain");
            Assert.AreEqual(BossCraft.Naval, boss.BossBrain.Craft);
            return boss;
        }

        // ================================================================== section 110: heading

        [Test]
        public void TargetSwitchingSidesTurnsTheTurretsNotTheHull()
        {
            var world = Bay(3);
            var sea = world.Map.Sea;
            var boss = Flagship(world, -60f);
            world.Step(Dt);
            // Port (on the shore, inshore of the mid lane) first, then starboard (out to sea past the far lane); both 50-130 m
            // off, outside the boss guns' ground dead zone (bossWeaponOverrides) and inside their reach.
            var port = world.SpawnVehicle(Battery, 0, sea.At(-20f, sea.ShoreAt(-20f) - 6f), 0f);
            var lane = SimMath.HeadingOf(sea.Along);
            var worst = 0f;
            Run(world, 10f, _ => worst = MathF.Max(worst, MathF.Abs(SimMath.WrapAngle(boss.Heading - lane))));
            port.Hp = 0f;
            var starboard = world.SpawnVehicle(Battery, 0, sea.At(0f, sea.Lane("mid").W + 60f), 0f);
            var turnedTo = false;
            var turnabouts = boss.BossBrain.ReverseRequestsTurned;
            Run(world, 12f, _ =>
            {
                worst = MathF.Max(worst, MathF.Abs(SimMath.WrapAngle(boss.Heading - lane)));
                turnedTo |= boss.BossBrain.TurretTargets.Contains(starboard.Id) || boss.BossBrain.TargetId == starboard.Id;
            });
            Assert.IsTrue(turnedTo, "a turret / mount took the new target on the other side");
            Assert.Less(worst, SimMath.DegToRad(SimTunables.Bosses.BossBrain.BroadsideMaxDeg + 10f),
                $"the hull stayed within its broadside offsets of the lane (worst {worst * 180f / MathF.PI:0} deg): no 180-degree flip");
            Assert.AreEqual(turnabouts, boss.BossBrain.ReverseRequestsTurned, "no turnabout for a target");
            Assert.AreEqual(0, world.Bosses.Brains.NavalReverseEvents, "never astern");
        }

        // ================================================================== section 110: target behind

        [Test]
        public void ATargetBehindNeverMakesTheShipReverseOrTurnAbout()
        {
            var world = Bay(5);
            var sea = world.Map.Sea;
            var boss = Flagship(world, -40f);
            world.Step(Dt);
            // Dead astern on its lane's line, past its guns' ground dead zone.
            world.SpawnVehicle(Battery, 0, sea.At(-95f, sea.Lane("mid").W), 0f);
            var start = sea.Frame(boss.Position).X;
            var last = start;
            var backwards = 0;
            var turnabouts = boss.BossBrain.ReverseRequestsTurned;
            Run(world, 12f, _ =>
            {
                Assert.GreaterOrEqual(boss.Speed, 0f, "speed never below 0");
                var u = sea.Frame(boss.Position).X;
                if (u < last - 0.02f) backwards++;
                last = u;
            });
            Assert.AreEqual(0, world.Bosses.Brains.NavalReverseEvents, "no reverse event");
            Assert.AreEqual(0, backwards, "it never went astern along its lane");
            Assert.Greater(sea.Frame(boss.Position).X - start, 10f, "it kept on its lane");
            Assert.AreEqual(turnabouts, boss.BossBrain.ReverseRequestsTurned, "no 180-degree turn for a target behind");
            Assert.AreNotEqual(HullReason.Turnabout, boss.BossBrain.HullReason);
        }

        // ================================================================== section 110: turn radius

        [Test]
        public void TurnRadiusFollowsTheDataAndThePlannerNeverCurvesTighter()
        {
            var def = Catalog.Vehicle("leviathan");
            var rmin = NavalBossMovementController.MinTurnRadius(def.Speed, def.TurnRate);
            // Spec 53's own example: 2.6 m/s at 8 deg/s is about 18.6 m.
            Assert.AreEqual(def.Speed / def.TurnRate, rmin, 1e-3f);
            if (MathF.Abs(def.Speed - 2.6f) < 1e-3f && MathF.Abs(def.TurnRate - SimMath.DegToRad(8f)) < 1e-4f) Assert.AreEqual(18.6f, rmin, 0.1f);
            var planning = NavalBossMovementController.PlanningRadius(def.HullRadius, rmin);
            Assert.GreaterOrEqual(planning, rmin * 1.1f - 1e-3f);
            Assert.GreaterOrEqual(planning, def.HullRadius);
            // Under way at any cruise speed the commanded turn is no tighter than the planning radius.
            foreach (var share in new[] { SimTunables.Bosses.BossBrain.CruiseThrottleMin, 0.8f, 1f })
            {
                var speed = def.Speed * share;
                var rate = NavalBossMovementController.CruiseTurnRate(def.TurnRate, speed, def.Speed, planning);
                Assert.GreaterOrEqual(speed / rate, planning - 1e-2f, $"radius at {share:0.00} of its speed");
            }
            // Spec 54: the look-ahead, and the curvature pure pursuit asks for to regain its lane from the corridor's edge.
            var look = NavalBossMovementController.LookAhead(def.Speed, def.Length);
            Assert.AreEqual(Math.Clamp(def.Speed * 6f, def.Length * 1.5f, def.Length * 4f), look, 1e-3f);
            var alpha = MathF.Atan2(10f, look);
            Assert.LessOrEqual(2f * MathF.Sin(alpha) / look, 1f / planning, "the lane point never asks for a curve tighter than Rmin");

            // In the battle: a phase's lane change (mid to near) under way, every step not coming about or avoiding.
            var world = Bay(7);
            var sea = world.Map.Sea;
            var boss = Flagship(world, -60f);
            Run(world, 4f);
            boss.NavalLane = "near";
            var offBefore = MathF.Abs(sea.Frame(boss.Position).Y - sea.Lane("near").W);
            var worst = float.PositiveInfinity;
            Run(world, 30f, _ =>
            {
                var b = boss.BossBrain;
                if (b.HullReason is HullReason.Turnabout or HullReason.Collision or HullReason.Hold) return;
                if (boss.Speed < def.Speed * SimTunables.Bosses.BossBrain.CruiseThrottleMin * 0.95f) return;
                worst = MathF.Min(worst, b.TurnRadius);
            });
            Assert.GreaterOrEqual(worst, boss.BossBrain.PlanningRadius * 0.98f, "the lane change turned no tighter than the planning radius");
            // Spec 54's long look-ahead (1.5-4 hull lengths) makes the change gradual: well on its way after 30 s.
            Assert.Less(MathF.Abs(sea.Frame(boss.Position).Y - sea.Lane("near").W), offBefore * 0.75f, "and it is closing on the new lane");
        }

        // ================================================================== section 110: collision

        private static bool Overlap(Vehicle a, Vehicle b)
        {
            var axes = new[]
            {
                SimMath.Forward(a.Heading), SimMath.Forward(a.Heading + MathF.PI * 0.5f),
                SimMath.Forward(b.Heading), SimMath.Forward(b.Heading + MathF.PI * 0.5f),
            };
            foreach (var axis in axes)
            {
                float Reach(Vehicle v)
                {
                    var f = SimMath.Forward(v.Heading);
                    var r = SimMath.Forward(v.Heading + MathF.PI * 0.5f);
                    return MathF.Abs(Vector2.Dot(f, axis)) * v.Def.Length * 0.5f + MathF.Abs(Vector2.Dot(r, axis)) * v.Def.Width * 0.5f;
                }
                if (MathF.Abs(Vector2.Dot(b.Position - a.Position, axis)) >= Reach(a) + Reach(b)) return false;
            }
            return true;
        }

        [Test]
        public void TwoConvergingShipsTurnAndSlowSecondsEarlyAndNeverOverlap()
        {
            var world = Bay(9);
            var sea = world.Map.Sea;
            var far = sea.Lane("far");
            // Two boss ships on one lane, under way and sailing at each other (each patrols towards its far end). They start
            // 140 m apart, bows ~45 m clear (at +-55 m two 96 m hulls began 14 m apart: the route traffic froze them at once and
            // there was no converging left to see).
            var a = world.SpawnVehicle("leviathan", 1, sea.At(-70f, far.W), SimMath.HeadingOf(sea.Along));
            var b = world.SpawnVehicle("leviathan", 1, sea.At(70f, far.W), SimMath.HeadingOf(-sea.Along));
            a.Speed = a.Def.Speed;
            b.Speed = b.Def.Speed;
            Assert.AreEqual(1, a.NavalDir);
            Assert.AreEqual(-1, b.NavalDir);
            var firstWarning = -1f;
            var overlaps = 0;
            var slowed = false;
            Run(world, 60f, t =>
            {
                foreach (var ship in new[] { a, b })
                {
                    var brain = ship.BossBrain;
                    if (brain.CpaThreat.IsValid && firstWarning < 0f) firstWarning = brain.CpaTime;
                    if (brain.CpaThreat.IsValid && ship.Speed < ship.Def.Speed * 0.95f) slowed = true;
                }
                if (t % 5 == 0 && a.IsAlive && b.IsAlive && Overlap(a, b)) overlaps++;
            });
            Assert.GreaterOrEqual(firstWarning, 3f, "the closest approach was seen seconds ahead (not at contact)");
            Assert.IsTrue(slowed, "a ship slowed for it");
            Assert.AreEqual(0, overlaps, "the hulls never overlapped");
            Assert.AreEqual(0, world.Bosses.Brains.NavalReverseEvents, "and neither went astern");
        }

        [Test]
        public void ClosestPointOfApproachIsPredicted()
        {
            // Head-on 100 m apart, closing at 5 m/s: the closest approach is 20 s away; inside a 10 s horizon it is clamped.
            Assert.IsTrue(NavalBossMovementController.Cpa(new Vector2(0f, 100f), new Vector2(0f, -5f), 30f, out var t));
            Assert.AreEqual(20f, t, 1e-3f);
            Assert.IsTrue(NavalBossMovementController.Cpa(new Vector2(0f, 100f), new Vector2(0f, -5f), 10f, out t));
            Assert.AreEqual(10f, t, 1e-3f);
            // Opening: no threat.
            Assert.IsFalse(NavalBossMovementController.Cpa(new Vector2(0f, 100f), new Vector2(0f, 5f), 10f, out _));
            // Spec 59: a boss's separation is the friendly one + the boss extra.
            var lev = Catalog.Vehicle("leviathan");
            var corvette = Catalog.Vehicle("sea_corvette");
            Assert.AreEqual(MathF.Max(lev.Width * 0.5f + corvette.Width * 0.5f + 4f, 0.5f * lev.Length) + SimTunables.Bosses.BossBrain.BossSeparationExtra,
                NavalBossMovementController.Separation(lev, corvette), 1e-3f);
            // Parallel lanes 14 m apart, sailing past each other: not a collision course.
            Assert.IsFalse(NavalBossMovementController.CollisionCourse(new Vector2(0f, 0f), 0f, 2.6f, lev, new Vector2(14f, 80f), MathF.PI, 3.4f, corvette, 9f,
                out _, out _, out _));
            // The same, on one line: a collision course.
            Assert.IsTrue(NavalBossMovementController.CollisionCourse(new Vector2(0f, 0f), 0f, 2.6f, lev, new Vector2(0f, 80f), MathF.PI, 3.4f, corvette, 9f,
                out _, out _, out _));
        }

        // ================================================================== no reverse, ever

        [Test]
        public void AGoalBehindBecomesAForwardTurn()
        {
            var heading = 0f;
            // Behind and to the right: square to the right; dead astern: the side given.
            Assert.AreEqual(MathF.PI * 0.5f, NavalBossMovementController.ForwardOnly(heading, SimMath.DegToRad(150f), 0), 1e-4f);
            Assert.AreEqual(-MathF.PI * 0.5f, NavalBossMovementController.ForwardOnly(heading, MathF.PI, -1), 1e-4f);
            // Ahead: unchanged.
            Assert.AreEqual(0.3f, NavalBossMovementController.ForwardOnly(heading, 0.3f, 1), 1e-5f);

            // Its patrol's end: it comes about forwards (no reverse), whichever way it turned.
            var world = Bay(11);
            var boss = Flagship(world, 60f);
            Run(world, 40f, _ => Assert.GreaterOrEqual(boss.Speed, 0f));
            Assert.Greater(boss.BossBrain.ReverseRequestsTurned, 0, "the patrol's end was a forward turn");
            Assert.AreEqual(0, world.Bosses.Brains.NavalReverseEvents);
            Assert.AreEqual(0, boss.BossBrain.Reverses, "a ship never backs up");
        }

        // ================================================================== Part R R5 / F5: broadside recompute

        private static List<MountSample> Batteries(bool port, bool starboard)
        {
            var list = new List<MountSample>();
            for (var k = 0; k < 2; k++)
            {
                if (port) list.Add(new MountSample(MountAim.Left, 0f, 0f, 10f, 0f, 80f, false, true));
                if (starboard) list.Add(new MountSample(MountAim.Right, 0f, 0f, 10f, 0f, 80f, false, true));
            }
            return list;
        }

        [Test]
        public void ABossThatLosesItsLeftBroadsideRecomputesItsBroadside()
        {
            var from = Vector2.Zero;
            var route = 0f;
            // A target 45 degrees to port of the route, 50 m off.
            var targets = new List<TargetSample> { new(SimMath.Forward(SimMath.DegToRad(-45f)) * 50f, 2f, false) };
            var open = RouteContext.Open;
            var both = NavalBossMovementController.ChooseOffset(Batteries(true, true), from, route, targets, open, 0f, out _, out var shareBoth);
            Assert.AreEqual(0f, both, 1e-4f, "both batteries: the port battery bears with the hull on its route");
            Assert.AreEqual(0.5f, shareBoth, 1e-4f, "one battery of two can bear on one side");
            // Port battery lost (its part broken: its mounts drop out of the samples).
            var right = NavalBossMovementController.ChooseOffset(Batteries(false, true), from, route, targets, open, both, out _, out var shareRight);
            Assert.Less(right, -SimMath.DegToRad(30f), "it turns to present its working starboard side");
            Assert.Greater(shareRight, 0.99f, "and the starboard battery bears");
            Assert.AreEqual(0f, NavalBossMovementController.BearingShare(Batteries(false, true), from, route, targets, out _), 1e-4f,
                "keeping the useless side would bear nothing");

            // Smoothing and hysteresis (spec 55, 57): the held offset jumps past the deadband, the steered one eases to it.
            var brain = new BossBrain(BossCraft.Naval) { RouteHeading = route };
            NavalBossMovementController.UpdateBroadside(brain, right, 0f);
            Assert.AreEqual(right, brain.BroadsideHeld, 1e-5f);
            Assert.AreEqual(right * SimTunables.Bosses.BossBrain.BroadsideSmoothing, brain.BroadsideOffset, 1e-4f, "lerp 0.15, no snap");
            // A candidate 3 degrees off the held one is ignored (deadband 5).
            NavalBossMovementController.UpdateBroadside(brain, right + SimMath.DegToRad(3f), 0f);
            Assert.AreEqual(right, brain.BroadsideHeld, 1e-5f);
        }

        [Test]
        public void ABrokenPartsMountsLeaveTheBroadsideSamples()
        {
            var world = Bay(13);
            var boss = Flagship(world, -40f);
            world.Step(Dt);
            var samples = new List<MountSample>();
            BossWeaponDirector.Samples(boss, samples);
            var before = samples.Count;
            var part = -1;
            for (var i = 0; i < boss.Def.Parts.Count && part < 0; i++)
                if (boss.Def.Parts[i].Mounts.Count > 0) part = i;
            Assume.That(part >= 0, "leviathan carries mounts on its parts");
            world.Bosses.Break(boss, part);
            BossWeaponDirector.Samples(boss, samples);
            Assert.Less(samples.Count, before, "the broken part's mounts no longer count for the broadside");
        }

        // ================================================================== the rest of the brain

        [Test]
        public void EscortStationsKeepTheirRings()
        {
            const float bound = 12f;
            foreach (EscortRole role in Enum.GetValues(typeof(EscortRole)))
            foreach (var rank in new[] { 0, 1, 2 })
            foreach (var close in new[] { false, true })
            {
                var ring = BossEscortCoordinator.Ring(role, rank, bound, close, 12f);
                Assert.Greater(ring, BossEscortCoordinator.Inner(bound), $"{role} r{rank}: never inside the boss's radius + 4 m");
                if (role == EscortRole.Repair) Assert.LessOrEqual(ring, bound + 12f, "a repairer stays in its repair reach");
                else if (BossEscortCoordinator.Support(role))
                {
                    Assert.GreaterOrEqual(ring, bound + 18f - 1e-3f, $"{role}: support ring");
                    Assert.LessOrEqual(ring, bound + 30f + 1e-3f, $"{role}: support ring");
                }
                else
                {
                    Assert.GreaterOrEqual(ring, bound + 10f - 1e-3f, $"{role}: screen ring");
                    Assert.LessOrEqual(ring, bound + 18f + 1e-3f, $"{role}: screen ring");
                }
            }
        }

        [Test]
        public void EveryMovingBossHasABrainOfItsLaw()
        {
            foreach (var def in Catalog.Vehicles.Values.Where(d => d.Boss && !d.Static))
            {
                var craft = BossMovementController.CraftOf(def);
                if (def.Naval != null) Assert.AreEqual(BossCraft.Naval, craft, def.Id);
                if (def.Frame?.Move == BossMove.Rail) Assert.AreEqual(BossCraft.Rail, craft, def.Id);
                if (def.FixedWing) Assert.AreEqual(BossCraft.FixedWing, craft, def.Id);
                if (def.Flying && def.HoldsToFire) Assert.AreEqual(BossCraft.Airship, craft, def.Id + ": a warship holds its heading (lane H)");
            }
        }

        [Test]
        public void TheSameBossBattleTwiceEndsTheSame()
        {
            ulong Play()
            {
                var world = Bay(17);
                world.SeaRules.FleetShare = 1f;
                var sea = world.Map.Sea;
                world.SpawnVehicle("leviathan", 1, sea.At(30f, sea.Lane("far").W), 0f);
                world.SpawnVehicle(Battery, 0, sea.At(10f, sea.Lane("near").W), 0f);
                Run(world, 60f);
                return world.StateHash();
            }
            Assert.AreEqual(Play(), Play(), "replay: the boss brain is deterministic");
        }
    }
}
