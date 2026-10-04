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
using EntityId = MachineBrigade.Sim.Core.EntityId;
using Vector2 = System.Numerics.Vector2;

namespace MachineBrigade.Tests
{
    /// <summary>
    /// AI MASTER P0-A (lane A, DECISIONS "AI MASTER P0-A"): the master spec's regression rows of the combat lane: Part R R1
    /// ("standing still but not attacking"), R2 (breacher), R3 (siege), section 113 (targeting) and the opportunity-fire row of
    /// section 224, plus Part H's escort row. Written by the lane, not run by it (the lead runs them).
    /// </summary>
    public class AiMasterP0ATests
    {
        private static Catalog _catalog;
        private static Catalog Catalog => _catalog ??= GameContent.LoadCatalog();

        [TearDown]
        public void TearDown() => GameContent.LoadTunables();

        private static SimWorld Field(List<PropPlacement> props = null, float size = 200f, int seed = 5) =>
            new SimWorld(Catalog, new MapDefinition("field", size,
                new[] { new TeamStart(0, new Vector2(-size * 0.4f, -size * 0.4f)), new TeamStart(1, new Vector2(size * 0.4f, size * 0.4f)) },
                props ?? new List<PropPlacement>(), new List<UnitPlacement>()), seed: seed);

        private static Vehicle Dummy(SimWorld world, string id, int team, Vector2 at, float heading = MathF.PI)
        {
            var v = world.SpawnVehicle(id, team, at, heading);
            world.MakeDummy(v);
            return v;
        }

        private static void Run(SimWorld world, float seconds, Action each = null)
        {
            for (var t = 0f; t < seconds; t += TestWorlds.Step)
            {
                world.Step(TestWorlds.Step);
                world.ClearEvents();
                each?.Invoke();
            }
        }

        private static bool Logged(SimWorld world, string code) => world.AiLog.Entries.Any(e => e.Text.StartsWith(code, StringComparison.Ordinal));

        private static void AiOrder(SimWorld world, CommandType type, Vehicle unit, Vector2 at, EntityId target = default) =>
            world.Submit(new Command(type, unit.Team, new[] { unit.Id }, at, target));

        // ------------------------------------------------------------------------------------------------ R1

        [Test]
        public void R1_AValidTargetWithAClearLineIsShot()
        {
            var world = Field();
            var tank = world.SpawnVehicle("main_battle_tank", 0, Vector2.Zero, 0f);
            Dummy(world, "light_tank", 1, new Vector2(0f, 20f));
            Run(world, 4f);
            Assert.Greater(tank.LastFiredAt, 0.0, "the tank fires at the target in reach and in sight");
            Assert.AreEqual(0, world.CombatWatch.Unexplained, "no unexplained idle");
            Assert.AreEqual(0, world.CombatWatch.Anomalies, "no combat anomaly");
        }

        [Test]
        public void R1_AFriendInTheLineGivesAReasonOrTheTankStillFights()
        {
            var world = Field();
            var rear = world.SpawnVehicle("main_battle_tank", 0, Vector2.Zero, 0f);
            var front = world.SpawnVehicle("main_battle_tank", 0, new Vector2(0f, 9f), 0f);
            front.HoldFire = true;
            Dummy(world, "light_tank", 1, new Vector2(0f, 24f));
            Run(world, 5f);
            var reason = world.CombatWatch.ReasonOf(rear.Id);
            Assert.That(rear.LastFiredAt > 0.0 || CombatReasons.Explains(reason),
                $"the rear tank fires or carries an explicit reason (got {CombatReasons.Code(reason)})");
            Assert.AreEqual(0, world.CombatWatch.Unexplained);
        }

        [Test]
        public void R1_ATargetInsideTheMinimumRangeIsWaitingMinRange()
        {
            var world = Field();
            var gun = world.SpawnVehicle("artillery", 0, Vector2.Zero, 0f);
            var near = Dummy(world, "light_tank", 1, new Vector2(0f, 10f));
            Assume.That(gun.Def.Weapon.MinRange, Is.GreaterThan(12f));
            Assert.AreEqual(TargetReject.MinRange, world.Combat.Feasibility(gun, gun.Def.Weapon, near), "spec 42: the min-range trap is infeasible");
            // The howitzer may back off (EscapeRoute); hold it in place so the watchdog's view is the one asked for.
            Run(world, 5f, () => gun.ClearPath());
            Assert.AreNotEqual(near.Id, gun.Target, "the main gun never takes a target inside its minimum reach");
            var reason = world.CombatWatch.ReasonOf(gun.Id);
            Assert.That(CombatReasons.Explains(reason), $"an explicit reason ({CombatReasons.Code(reason)})");
        }

        [Test]
        public void R1_ATargetOutsideAFixedMountsBearingIsFiltered()
        {
            var world = Field();
            var dozer = world.SpawnVehicle("armored_bulldozer", 0, Vector2.Zero, 0f);
            Assume.That(dozer.Def.Mounts[0].Aim, Is.EqualTo(MountAim.Hull));
            dozer.Deploy = DeployState.Deployed;
            var behind = Dummy(world, "scout_jeep", 1, new Vector2(0f, -3f));
            var ahead = Dummy(world, "scout_jeep", 1, new Vector2(0f, 3f));
            Assert.AreEqual(TargetReject.OutsideArc, world.Combat.Feasibility(dozer, dozer.Def.Weapon, behind), "a hull that cannot turn cannot bear behind it");
            Assert.AreEqual(TargetReject.None, world.Combat.Feasibility(dozer, dozer.Def.Weapon, ahead), "straight ahead it bears");
        }

        [Test]
        public void R1_AStaleTargetEntityIsDroppedAndTheTankFightsOn()
        {
            var world = Field();
            var tank = world.SpawnVehicle("main_battle_tank", 0, Vector2.Zero, 0f);
            var gone = world.SpawnVehicle("scout_jeep", 1, new Vector2(10f, 20f), MathF.PI);
            gone.HoldFire = true;
            Dummy(world, "light_tank", 1, new Vector2(0f, 22f));
            AiOrder(world, CommandType.Attack, tank, gone.Position, gone.Id);
            world.Step(TestWorlds.Step);
            // The ordered target is gone between two steps (killed elsewhere, removed with the dead).
            gone.Hp = 0f;
            Run(world, 5f);
            Assert.AreNotEqual(OrderKind.Attack, tank.Order.Kind, "the order on the vanished target is dropped");
            Assert.Greater(tank.LastFiredAt, 0.0, "and the tank fights the target that is there");
        }

        [Test]
        public void R1_AStuckAimIsACombatAnomalyWithAReasonAndARecovery()
        {
            var world = Field();
            var tank = world.SpawnVehicle("main_battle_tank", 0, Vector2.Zero, 0f);
            // The turret cannot traverse (a jammed ring): the target stays feasible (the hull could turn), the gun is ready, yet
            // no shot is ever fired: the "weapon reloaded but aim state stuck" row of R1.
            tank.TurretFactor = 0f;
            Dummy(world, "light_tank", 1, new Vector2(20f, 0f));
            Run(world, 8f);
            Assert.GreaterOrEqual(world.CombatWatch.Anomalies, 1, "Part C1: COMBAT_ANOMALY is detected");
            Assert.That(Logged(world, CombatReasons.WatchdogCombatAnomaly), "and logged with its cause");
            Assert.AreEqual(CombatIdleReason.StaleAim, world.CombatWatch.ReasonOf(tank.Id), "the unit carries the COMBAT_IDLE_STALE_AIM code, never silence");
        }

        [Test]
        public void R1_AnAiUnitStandingWithAReachableEnemyInSightIsRecovered()
        {
            var world = Field();
            // No guard leash: the idle vehicle would not close in on its own (the gap the watchdog has to catch).
            SimTunables.Vehicles.MovementSystem.GuardLeash = 0f;
            var tank = world.SpawnVehicle("light_tank", 0, Vector2.Zero, 0f);
            var reach = tank.Def.Weapon.Range;
            var vision = tank.Def.VisionRange;
            Assume.That(vision, Is.GreaterThan(reach * 0.9f + 6f));
            var enemy = Dummy(world, "main_battle_tank", 1, new Vector2(0f, MathF.Min(vision - 1f, reach + 5f)));
            world.CombatWatch.MarkAiTeam(0);
            Run(world, 6f);
            Assert.GreaterOrEqual(world.CombatWatch.Unexplained, 1, "Part C2: the unexplained idle is found");
            var requests = new List<WatchdogRequest>();
            world.CombatWatch.TakeRequests(0, requests);
            Assert.That(requests.Any(r => r.Unit == tank.Id && r.Kind == WatchdogRequestKind.Push), "and the side's AI is asked to push it at the enemy");
            Assert.That(Logged(world, CombatReasons.WatchdogIdleUnexplained));
            Assert.Less(Vector2.Distance(requests.First(r => r.Unit == tank.Id).Point, enemy.Position), 1f);
        }

        [Test]
        public void R1_AFormationWaitIsAnExplicitReasonAndExpires()
        {
            var world = Field();
            var tank = world.SpawnVehicle("main_battle_tank", 0, Vector2.Zero, 0f);
            Dummy(world, "light_tank", 1, new Vector2(0f, tank.Def.VisionRange + 30f));
            world.CombatWatch.MarkAiTeam(0);
            world.CombatWatch.Explain(tank.Id, CombatIdleReason.WaitingFormation, 2f);
            Run(world, 1f);
            Assert.AreEqual(CombatIdleReason.WaitingFormation, world.CombatWatch.ReasonOf(tank.Id));
            Run(world, 4f);
            var after = world.CombatWatch.ReasonOf(tank.Id);
            Assert.AreNotEqual(CombatIdleReason.WaitingFormation, after, "the reason lapses unless renewed");
            Assert.That(CombatReasons.Explains(after), $"and another explicit reason takes over ({CombatReasons.Code(after)})");
        }

        // ------------------------------------------------------------------------------------------------ R2 / R3

        [Test]
        public void R2_ABreacherKeepsOnTheBlockingWallBesideARandomJeep()
        {
            var world = Field();
            var dozer = world.SpawnVehicle("armored_bulldozer", 0, Vector2.Zero, 0f);
            Assume.That(dozer.Def.Breacher || dozer.Def.WallBreaker);
            var wall = world.SpawnVehicle("wall_hesco", 1, new Vector2(0f, 5f), 0f);
            Assume.That(wall.Def.Wall || wall.Def.Obstacle);
            var jeep = Dummy(world, "scout_jeep", 1, new Vector2(3f, 2f));
            AiOrder(world, CommandType.Attack, dozer, wall.Position, wall.Id);
            var tookJeep = false;
            Run(world, 4f, () => tookJeep |= dozer.Target == jeep.Id);
            Assert.False(tookJeep, "the wall stays the priority: the jeep is no immediate survival threat");
            Assert.False(world.Combat.ImmediateSurvivalThreat(dozer, jeep));
        }

        [Test]
        public void R2_AnImmediateSurvivalThreatMayTakeTheBreacherOffTheWall()
        {
            var world = Field();
            var dozer = world.SpawnVehicle("armored_bulldozer", 0, Vector2.Zero, 0f);
            var wall = world.SpawnVehicle("wall_hesco", 1, new Vector2(0f, 5f), 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 1, new Vector2(4f, 12f), MathF.PI);
            tank.Target = dozer.Id;
            Assert.True(world.Combat.ImmediateSurvivalThreat(dozer, tank));
            Assert.False(world.Combat.BreachHeld(dozer, dozer.Def.Weapon, wall, tank), "the breach lock gives way to a survival threat");
        }

        [Test]
        public void R3_ASiegePlatformShellsTheTowerBeforeTheScout()
        {
            var world = Field();
            var siege = world.SpawnVehicle("siege_tank", 0, Vector2.Zero, 0f);
            Assume.That(world.Combat.IsSiegePlatform(siege));
            siege.Deploy = DeployState.Deployed;
            var weapon = siege.Def.Weapon;
            var at = MathF.Max(weapon.MinRange + 12f, 30f);
            Assume.That(at + 6f, Is.LessThan(weapon.Range));
            var tower = Dummy(world, "guard_tower", 1, new Vector2(-6f, at + 4f));
            var scout = Dummy(world, "scout_jeep", 1, new Vector2(6f, at));
            Run(world, 2f);
            Assert.AreEqual(tower.Id, siege.Target, "Part B B3: the defensive structure before the light scout");
            Assert.AreNotEqual(scout.Id, siege.Target);
        }

        // ------------------------------------------------------------------------------------------------ section 113

        [Test]
        public void T113_AnUnreachableTargetIsFilteredAndTheAiOrderDropped()
        {
            var world = Field();
            // A sealed box round the far target: no open ground of the tank's region within its reach of it.
            var box = new Vector2(60f, 60f);
            world.Grid.AddBlocker(box, 90f, 90f, 0f);
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-40f, -40f), 0f);
            var target = Dummy(world, "light_tank", 1, box);
            Assert.False(world.TargetAccess.CanInfluence(tank, target.Position, false), "spec 47/83: no firing-access region");
            AiOrder(world, CommandType.Attack, tank, target.Position, target.Id);
            Run(world, 1f);
            Assert.AreNotEqual(OrderKind.Attack, tank.Order.Kind, "the AI's order is dropped, not chased round the map");
            Assert.GreaterOrEqual(world.CombatWatch.Dropped, 1);
            Assert.That(Logged(world, CombatReasons.TargetUnreachableDropped));
        }

        [Test]
        public void T113_TheAccessCacheIsDroppedWhenTheGroundChanges()
        {
            var world = Field();
            var tank = world.SpawnVehicle("main_battle_tank", 0, new Vector2(-40f, -40f), 0f);
            var at = new Vector2(40f, 40f);
            Assert.True(world.TargetAccess.CanInfluence(tank, at, false));
            world.Grid.AddBlocker(at, 90f, 90f, 0f);
            Assert.False(world.TargetAccess.CanInfluence(tank, at, false), "a new blocker (a gate shut, a wreck) invalidates the cache");
        }

        [Test]
        public void T113_ATargetBehindAWallIsFilteredForDirectFireButNotForIndirect()
        {
            var wall = new List<PropPlacement>();
            for (var x = -24f; x <= 24f; x += 8f) wall.Add(new PropPlacement("base_wall", new Vector2(x, 20f), 0));
            var world = Field(wall);
            var tank = world.SpawnVehicle("main_battle_tank", 0, Vector2.Zero, 0f);
            var gun = world.SpawnVehicle("artillery", 0, new Vector2(0f, -20f), 0f);
            var hidden = Dummy(world, "light_tank", 1, new Vector2(0f, 27f));
            Assert.AreEqual(TargetReject.NoLineOfFire, world.Combat.Feasibility(tank, tank.Def.Weapon, hidden), "direct fire needs a clear line");
            Assert.AreEqual(TargetReject.None, world.Combat.Feasibility(gun, gun.Def.Weapon, hidden), "a lobbed shell goes over the wall");
        }

        [Test]
        public void T113_AMountThatCannotBearIsFiltered() => R1_ATargetOutsideAFixedMountsBearingIsFiltered();

        [Test]
        public void T113_TheMinimumRangeIsRespected() => R1_ATargetInsideTheMinimumRangeIsWaitingMinRange();

        [Test]
        public void T113_OverkillSpreadsTheFire()
        {
            var world = Field();
            var tank = world.SpawnVehicle("main_battle_tank", 0, Vector2.Zero, 0f);
            var a = Dummy(world, "light_tank", 1, new Vector2(0f, 15f));
            var b = Dummy(world, "light_tank", 1, new Vector2(4f, 26f));
            // Everything about a is better (nearer, dead ahead); then more than 1.15 x its health is already on its way.
            world.Combat.NoteIncoming(a.Id, a.Hp * 2f);
            Assert.True(world.Combat.Overkilled(tank, a));
            Run(world, 0.5f);
            Assert.AreEqual(b.Id, tank.Target, "spec 44: a unit not yet firing takes another target");
        }

        [Test]
        public void T113_OverkillLeavesTheExceptionsAlone()
        {
            var world = Field();
            var tank = world.SpawnVehicle("main_battle_tank", 0, Vector2.Zero, 0f);
            var a = Dummy(world, "light_tank", 1, new Vector2(0f, 15f));
            world.Combat.NoteIncoming(a.Id, a.Hp * 2f);
            world.Submit(new Command(CommandType.Attack, 0, new[] { tank.Id }, a.Position, a.Id, manual: true));
            Assert.True(world.Combat.OverkillExempt(tank, a), "a forced (player) order");
            var boss = Dummy(world, "behemoth", 1, new Vector2(30f, 30f));
            world.Combat.NoteIncoming(boss.Id, boss.MaxHp * 3f);
            Assert.True(world.Combat.OverkillExempt(tank, boss), "a boss (extremely dangerous) is always worth the certainty");
            Assert.False(world.Combat.Overkilled(tank, boss));
        }

        [Test]
        public void T113_TheCurrentTargetIsStickyForASecondAndAHalf()
        {
            var world = Field();
            var tank = world.SpawnVehicle("main_battle_tank", 0, Vector2.Zero, 0f);
            var a = Dummy(world, "light_tank", 1, new Vector2(0f, 20f));
            Run(world, 0.2f);
            Assume.That(tank.Target, Is.EqualTo(a.Id));
            var held = world.Combat.P0AWorth(tank, a, tank.Def.Weapon);
            tank.Weapons[0].AcquiredAt -= SimTunables.Ai.Targeting.TargetStickSeconds + 0.1;
            var later = world.Combat.P0AWorth(tank, a, tank.Def.Weapon);
            Assert.AreEqual(1f + SimTunables.Ai.Targeting.TargetStickBonus, held / later, 1e-3f, "spec 45: +15 % inside the window, none after");
        }

        [Test]
        public void T113_AimTimeCostsATargetBehindTheTurret()
        {
            var world = Field();
            var tank = world.SpawnVehicle("main_battle_tank", 0, Vector2.Zero, 0f);
            var ahead = Dummy(world, "light_tank", 1, new Vector2(0f, 20f));
            var behind = Dummy(world, "light_tank", 1, new Vector2(0f, -20f));
            var front = world.Combat.P0AWorth(tank, ahead, tank.Def.Weapon);
            var back = world.Combat.P0AWorth(tank, behind, tank.Def.Weapon);
            var aim = Sim.Combat.CombatSystem.AimSeconds(tank, 0, behind.Position);
            Assert.Greater(aim, 0f);
            Assert.AreEqual(MathF.Exp(-aim / SimTunables.Ai.Targeting.AimTimeConstant), back / front, 1e-3f, "spec 89: exp(-AimSeconds / 4)");
        }

        [Test]
        public void T113_TheBossPartFocusStillOverridesOverkill()
        {
            var world = Field();
            var tank = world.SpawnVehicle("main_battle_tank", 0, Vector2.Zero, 0f);
            var boss = world.SpawnVehicle("behemoth", 1, new Vector2(0f, 30f), MathF.PI);
            world.Combat.NoteIncoming(boss.Id, boss.MaxHp * 3f);
            Assert.False(world.Combat.Overkilled(tank, boss), "a boss is never left for overkill, so a part focus order keeps its fire");
        }

        // ------------------------------------------------------------------------------------------------ section 224 / Part H

        [Test]
        public void A224_ATurretFiresOnTheMoveAndTheRouteDoesNotChange()
        {
            var world = Field();
            var tank = world.SpawnVehicle("light_tank", 0, Vector2.Zero, 0f);
            Assume.That(tank.Def.FiresWhileMoving);
            Dummy(world, "scout_jeep", 1, new Vector2(16f, 30f));
            var goal = new Vector2(0f, 70f);
            AiOrder(world, CommandType.Move, tank, goal);
            var firedMoving = false;
            var routeKept = true;
            Run(world, 6f, () =>
            {
                if (tank.LastFiredAt >= world.Time - TestWorlds.Step * 1.5 && tank.IsMoving) firedMoving = true;
                if (tank.Order.Kind == OrderKind.Move && Vector2.Distance(tank.Order.Point, goal) > 0.5f) routeKept = false;
            });
            Assert.True(firedMoving, "the turret fires at the target of opportunity while the hull drives");
            Assert.True(routeKept, "the hull's route is the order's, unchanged");
        }

        [Test]
        public void H_TheUnitShootingAtTheConvoyOutranksADistantHeavy()
        {
            var world = Field();
            var escort = world.SpawnVehicle("main_battle_tank", 0, Vector2.Zero, 0f);
            var truck = world.SpawnVehicle("supply_truck", 0, new Vector2(10f, 0f), 0f);
            world.ConvoySafeZone = () => new[] { truck.Position };
            var raider = Dummy(world, "scout_jeep", 1, new Vector2(10f, 20f));
            var heavy = Dummy(world, "main_battle_tank", 1, new Vector2(-20f, 40f));
            raider.Target = truck.Id;
            Assert.AreEqual(1f, world.Combat.ThreatToObjective(escort, raider), 1e-6f, "Part H Escort: damaging the convoy");
            Assert.AreEqual(0f, world.Combat.ThreatToObjective(escort, heavy), 1e-6f);
        }
    }
}
